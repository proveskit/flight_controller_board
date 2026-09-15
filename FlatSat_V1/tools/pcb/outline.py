#!/usr/bin/env python3
"""Grow the board outline, extend the In1 GND plane, add GND pours / mounting holes / stitching vias
for the new area. Run with KiCad's bundled python3. Works on a copy; verify with heritage.py afterwards
(`check --allow-zone-growth --allow-edge`).

  outline.py --board IN --out OUT --spec spec.json

spec.json:
{
  "remove_edge_regions": [[xmin, ymin, xmax, ymax], ...],   # Edge.Cuts items whose bounding box lies entirely inside are deleted
  "add_edges": {"points": [[x, y], ...],                    # OPEN polyline of NEW edge segments; its two ends must land exactly on
                "fillet_vertices": [1, 2],                  # the endpoints of surviving Edge.Cuts items; interior vertices listed
                "fillet_radius": 4.0},                      # here get a rounded corner (arc)
  "grow_in1_gnd_rect": [x1, y1, x2, y2],                    # replace the In1 GND plane outline with this rectangle (KiCad clips the
                                                            # fill to the board outline, so make it a little larger than the board)
  "outline": [[x, y], ...], "fillet_vertices": [...],       # legacy: closed polygon drawn in full (only for a board with no edges yet)
  "grow_in1_gnd": true, "inset_mm": 0.5,                    # legacy: In1 outline = closed polygon inset
  "new_gnd_pours": [{"layer": "F.Cu", "rect": [x1, y1, x2, y2]}, {"layer": "B.Cu", "rect": [...]}],
  "mounting_holes": [[x, y], ...],                          # cloned from H1 (same footprint, net)
  "stitching": {"points": [[x, y], ...], "via": [0.8, 0.4]} # GND through vias
}
"""
import argparse
import json
import math
import sys

try:
    import pcbnew
except ImportError:
    sys.exit('run with KiCad\'s bundled python3')

MM = pcbnew.VECTOR2I_MM
_KEEP = []  # wrappers of items removed from the board: if Python garbage-collects them the board's item list is
            # corrupted (KiCad 10 SWIG binding), so they are kept alive until the process exits


def fillet_polygon(pts, fillet_idx, r):
    """Return a list of segments: ('line', p1, p2) and ('arc', start, mid, end) with rounded corners at fillet_idx."""
    n = len(pts)
    segs = []
    corner_pts = {}  # vertex -> (a, b) tangent points
    for i in fillet_idx:
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % n]
        v1 = (p0[0] - p1[0], p0[1] - p1[1])
        v2 = (p2[0] - p1[0], p2[1] - p1[1])
        l1 = math.hypot(*v1)
        l2 = math.hypot(*v2)
        u1 = (v1[0] / l1, v1[1] / l1)
        u2 = (v2[0] / l2, v2[1] / l2)
        ang = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
        t = r / math.tan(ang / 2)
        a = (p1[0] + u1[0] * t, p1[1] + u1[1] * t)
        b = (p1[0] + u2[0] * t, p1[1] + u2[1] * t)
        bis = (u1[0] + u2[0], u1[1] + u2[1])
        lb = math.hypot(*bis)
        bis = (bis[0] / lb, bis[1] / lb)
        d = r / math.sin(ang / 2)
        c = (p1[0] + bis[0] * d, p1[1] + bis[1] * d)
        # arc midpoint: from centre toward the vertex, at radius r
        m = (c[0] + (p1[0] - c[0]) / math.hypot(p1[0] - c[0], p1[1] - c[1]) * r, c[1] + (p1[1] - c[1]) / math.hypot(p1[0] - c[0], p1[1] - c[1]) * r)
        corner_pts[i] = (a, m, b)
    for i in range(n):
        start = corner_pts[i][2] if i in corner_pts else pts[i]
        j = (i + 1) % n
        end = corner_pts[j][0] if j in corner_pts else pts[j]
        segs.append(('line', start, end))
        if j in corner_pts:
            a, m, b = corner_pts[j]
            segs.append(('arc', a, m, b))
    return segs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--board', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--spec', required=True)
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    board = pcbnew.LoadBoard(a.board)
    edge = board.GetLayerID('Edge.Cuts')
    mm = lambda v: pcbnew.ToMM(v)

    removed = 0
    drawings = list(board.GetDrawings())
    _KEEP.append(drawings)
    for d in drawings:
        if d.GetLayer() != edge:
            continue
        bb = d.GetBoundingBox()
        x1, y1, x2, y2 = mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())
        for rx1, ry1, rx2, ry2 in spec.get('remove_edge_regions', []):
            if x1 >= rx1 - 1e-3 and y1 >= ry1 - 1e-3 and x2 <= rx2 + 1e-3 and y2 <= ry2 + 1e-3:
                g = d.GetParentGroup()
                if g is not None:
                    g.RemoveItem(d)     # detach from its PCB group first; a dangling group member crashes later board traversals
                board.Remove(d)
                _KEEP.append(d)
                removed += 1
                break
    print('Edge.Cuts items removed:', removed)

    added = 0
    segs = []
    if spec.get('add_edges'):
        ae = spec['add_edges']
        pts = [tuple(p) for p in ae['points']]
        r = float(ae.get('fillet_radius', 4.0))
        fil = set(ae.get('fillet_vertices', []))
        # open polyline: corners only at interior vertices
        corner = {}
        for i in fil:
            if i <= 0 or i >= len(pts) - 1:
                continue
            p0, p1, p2 = pts[i - 1], pts[i], pts[i + 1]
            v1 = (p0[0] - p1[0], p0[1] - p1[1]); v2 = (p2[0] - p1[0], p2[1] - p1[1])
            l1 = math.hypot(*v1); l2 = math.hypot(*v2)
            u1 = (v1[0] / l1, v1[1] / l1); u2 = (v2[0] / l2, v2[1] / l2)
            ang = math.acos(max(-1, min(1, u1[0] * u2[0] + u1[1] * u2[1])))
            t = r / math.tan(ang / 2)
            pa = (p1[0] + u1[0] * t, p1[1] + u1[1] * t); pb = (p1[0] + u2[0] * t, p1[1] + u2[1] * t)
            bis = (u1[0] + u2[0], u1[1] + u2[1]); lb = math.hypot(*bis); bis = (bis[0] / lb, bis[1] / lb)
            dd = r / math.sin(ang / 2)
            c = (p1[0] + bis[0] * dd, p1[1] + bis[1] * dd)
            dc = math.hypot(p1[0] - c[0], p1[1] - c[1])
            pm = (c[0] + (p1[0] - c[0]) / dc * r, c[1] + (p1[1] - c[1]) / dc * r)
            corner[i] = (pa, pm, pb)
        for i in range(len(pts) - 1):
            start = corner[i][2] if i in corner else pts[i]
            end = corner[i + 1][0] if (i + 1) in corner else pts[i + 1]
            segs.append(('line', start, end))
            if (i + 1) in corner:
                pa, pm, pb = corner[i + 1]
                segs.append(('arc', pa, pm, pb))
    elif spec.get('outline'):
        segs = fillet_polygon([tuple(p) for p in spec['outline']], spec.get('fillet_vertices', []), float(spec.get('fillet_radius', 4.0)))
    if segs:
        for s in segs:
            sh = pcbnew.PCB_SHAPE(board)
            sh.SetLayer(edge)
            sh.SetWidth(pcbnew.FromMM(0.1))
            if s[0] == 'line':
                if math.hypot(s[1][0] - s[2][0], s[1][1] - s[2][1]) < 1e-3:
                    continue
                sh.SetShape(pcbnew.SHAPE_T_SEGMENT)
                sh.SetStart(MM(*s[1]))
                sh.SetEnd(MM(*s[2]))
            else:
                sh.SetShape(pcbnew.SHAPE_T_ARC)
                sh.SetArcGeometry(MM(*s[1]), MM(*s[2]), MM(*s[3]))
            board.Add(sh)
            added += 1
    print('Edge.Cuts items added:', added)

    if spec.get('grow_in1_gnd_rect'):
        x1, y1, x2, y2 = spec['grow_in1_gnd_rect']
        grown = 0
        for z in board.Zones():
            if z.GetNetname() == 'GND' and board.GetLayerName(z.GetFirstLayer()) == 'In1.Cu':
                ol = z.Outline()            # edit the zone's own polygon in place (SetOutline with a Python-owned
                ol.RemoveAllContours()      # SHAPE_POLY_SET transfers ownership and segfaults on GC)
                ol.NewOutline()
                for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
                    ol.Append(MM(x, y))
                z.SetNeedRefill(True)
                grown += 1
        print('In1 GND zones grown (rect):', grown)
    if spec.get('grow_in1_gnd') and spec.get('outline'):
        inset = float(spec.get('inset_mm', 0.5))
        poly = pcbnew.SHAPE_POLY_SET()
        poly.NewOutline()
        for x, y in spec['outline']:
            poly.Append(MM(x, y))
        poly.Inflate(-pcbnew.FromMM(inset), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))
        grown = 0
        for z in board.Zones():
            if z.GetNetname() == 'GND' and board.GetLayerName(z.GetFirstLayer()) == 'In1.Cu':
                ol = z.Outline()
                ol.RemoveAllContours()
                ol.NewOutline()
                for i in range(poly.Outline(0).PointCount()):
                    ol.Append(poly.Outline(0).CPoint(i))
                z.SetNeedRefill(True)
                grown += 1
        print('In1 GND zones grown:', grown)

    # Heritage zones other than the grown In1 GND plane must not spill into the new area (their polygons often
    # extend past the old edge, clipped only by the old outline): intersect them with the Rev2 outline polygon.
    if spec.get('clip_heritage_zones_to'):
        snapz = json.load(open(spec['clip_heritage_zones_to']))
        rev2 = snapz.get('rev2_outline') or []
        if rev2:
            clip = pcbnew.SHAPE_POLY_SET()
            clip.NewOutline()
            for x, y in rev2:
                clip.Append(MM(x, y))
            # inset by the edge clearance the original fill obeyed, so the fill boundary is reproduced exactly and no
            # ribbon of new copper along the former edge can bridge (and thereby keep) an island KiCad used to remove
            inset = float(spec.get('clip_inset_mm', 0.2))
            if inset > 0:
                clip.Inflate(-pcbnew.FromMM(inset), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))
            clipped = 0
            for z in board.Zones():
                if z.m_Uuid.AsString() not in snapz.get('zones', {}):
                    continue
                if z.GetNetname() == 'GND' and board.GetLayerName(z.GetFirstLayer()) == 'In1.Cu':
                    continue
                before = z.Outline().Outline(0).PointCount() if z.Outline().OutlineCount() else 0
                z.Outline().BooleanIntersection(clip)
                z.SetNeedRefill(True)
                clipped += 1
            print('heritage zones clipped to the Rev2 outline:', clipped)

    for pour in spec.get('new_gnd_pours', []):
        x1, y1, x2, y2 = pour['rect']
        z = pcbnew.ZONE(board)
        z.SetLayer(board.GetLayerID(pour['layer']))
        z.SetNet(board.FindNet('GND'))
        ol = z.Outline()
        ol.NewOutline()
        for x, y in ((x1, y1), (x2, y1), (x2, y2), (x1, y2)):
            ol.Append(MM(x, y))
        z.SetIsFilled(False)
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetMinThickness(pcbnew.FromMM(0.25))
        z.SetLocalClearance(pcbnew.FromMM(0.25))
        z.SetAssignedPriority(int(pour.get('priority', 0)))
        z.SetZoneName(pour.get('name', 'GND_' + pour['layer'].replace('.', '_') + '_flatsat'))
        board.Add(z)
    print('new GND pours:', len(spec.get('new_gnd_pours', [])))

    holes = spec.get('mounting_holes', [])
    if holes:
        donor = next((f for f in board.GetFootprints() if f.GetReference() == 'H1'), None)
        if donor is None:
            print('no H1 to clone for mounting holes')
        else:
            for i, (x, y) in enumerate(holes):
                h = donor.Duplicate(False).Cast()
                h.SetReference(f'H{10 + i}')
                h.SetPosition(MM(x, y))
                h.SetPath(pcbnew.KIID_PATH(''))
                h.SetBoardOnly(True)        # no schematic symbol: exempt from the schematic-parity check
                h.SetExcludedFromBOM(True)
                h.SetExcludedFromPosFiles(True)
                board.Add(h)
            print('mounting holes added:', len(holes), '(H10..)')

    st = spec.get('stitching')
    if st:
        gnd = board.FindNet('GND')
        dia, drill = st.get('via', [0.8, 0.4])
        for x, y in st['points']:
            v = pcbnew.PCB_VIA(board)
            v.SetPosition(MM(x, y))
            v.SetViaType(pcbnew.VIATYPE_THROUGH)
            v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
            v.SetWidth(pcbnew.FromMM(dia))
            v.SetDrill(pcbnew.FromMM(drill))
            v.SetNet(gnd)
            board.Add(v)
        print('stitching vias added:', len(st['points']))

    filler = pcbnew.ZONE_FILLER(board)
    filler.Fill(board.Zones())
    pcbnew.SaveBoard(a.out, board)
    bb = board.GetBoardEdgesBoundingBox()
    print('saved', a.out, 'new bbox x %.2f..%.2f y %.2f..%.2f' % (mm(bb.GetLeft()), mm(bb.GetRight()), mm(bb.GetTop()), mm(bb.GetBottom())))
    return 0


if __name__ == '__main__':
    sys.exit(main())
