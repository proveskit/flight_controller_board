#!/usr/bin/env python3
"""Measurable placement facts for a floorplan review — run with KiCad's bundled python3.

  placement_facts.py BOARD.kicad_pcb SNAP.json OUT_DIR [--blocks blocks.json] [--gap-mm 1.0] [--hole-mm 3.5] [--edge-mm 1.5]

Writes OUT_DIR/facts.json and OUT_DIR/facts.md with, for the NEW footprints (ref 200-799):
  placements      ref, value, footprint, x, y, rot, side, block, courtyard bbox
  gaps            courtyard-bbox gaps below --gap-mm between any two footprints where at least one is new (same side)
  holes           new footprints whose courtyard bbox comes within --hole-mm of a mounting-hole centre (H*)
  edges           new footprints whose courtyard bbox comes within --edge-mm of the board outline
  ratsnest        per net: pad count, Euclidean MST length, longest edge, edges; crossings between MST edges of
                  different nets in the new area (a routing-congestion proxy); per block: internal MST length,
                  edges leaving the block, crossings touching the block
  stubs           for every net shared with the flight section: nearest ALLOWED FC pad (attachment_check.ALLOWED_PADS)
                  → nearest new pad distance vs nearest ANY FC pad → nearest new pad (if the any-pad distance is
                  shorter, the router will want a non-allowed attachment and the keep-out forces a detour)
  sides           counts of new parts per side, distinct footprints/values (feeder count)
GND is excluded from the ratsnest (plane net). Nothing is written to the board.
"""
import argparse
import json
import math
import os
import re
import sys
from collections import defaultdict

try:
    import pcbnew
except ImportError:
    sys.exit("run with KiCad's bundled python3")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attachment_check import ALLOWED_PADS  # noqa: E402

mm = pcbnew.ToMM
NEW_REF = re.compile(r'^[A-Z]{1,3}(2\d\d|3\d\d|4[0-4]\d|5\d\d|6[0-4]\d|7\d\d)$')


def _field(fp, name):
    try:
        fld = fp.GetFieldByName(name)
        return fld.GetText() if fld is not None else ''
    except Exception:
        try:
            return fp.GetFieldText(name)
        except Exception:
            return ''


def rect_gap(a, b):
    """Gap between two BOX2I (mm); negative = overlap."""
    dx = max(mm(b.GetLeft()) - mm(a.GetRight()), mm(a.GetLeft()) - mm(b.GetRight()), 0)
    dy = max(mm(b.GetTop()) - mm(a.GetBottom()), mm(a.GetTop()) - mm(b.GetBottom()), 0)
    if dx == 0 and dy == 0:
        ox = min(mm(a.GetRight()), mm(b.GetRight())) - max(mm(a.GetLeft()), mm(b.GetLeft()))
        oy = min(mm(a.GetBottom()), mm(b.GetBottom())) - max(mm(a.GetTop()), mm(b.GetTop()))
        return -min(ox, oy)
    return math.hypot(dx, dy)


def crt_bbox(fp):
    layer = pcbnew.B_CrtYd if fp.GetLayer() == pcbnew.B_Cu else pcbnew.F_CrtYd
    try:
        poly = fp.GetCourtyard(layer)
        if poly.OutlineCount():
            return poly.BBox(), 'courtyard'
    except Exception:
        pass
    return fp.GetBoundingBox(False, False), 'bbox'


def point_in_poly(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xin = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if x < xin:
                inside = not inside
    return inside


def seg_intersect(p1, p2, p3, p4):
    def ccw(a, b, c):
        return (c[1] - a[1]) * (b[0] - a[0]) > (b[1] - a[1]) * (c[0] - a[0])
    if p1 in (p3, p4) or p2 in (p3, p4):
        return False
    return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)


def mst(points):
    """Prim's MST on (x, y, tag) points; returns list of (i, j, length)."""
    n = len(points)
    if n < 2:
        return []
    in_tree = [False] * n
    best = [float('inf')] * n
    parent = [-1] * n
    best[0] = 0
    edges = []
    for _ in range(n):
        u = min((i for i in range(n) if not in_tree[i]), key=lambda i: best[i])
        in_tree[u] = True
        if parent[u] >= 0:
            edges.append((parent[u], u, best[u]))
        ux, uy = points[u][0], points[u][1]
        for v in range(n):
            if not in_tree[v]:
                d = math.hypot(points[v][0] - ux, points[v][1] - uy)
                if d < best[v]:
                    best[v] = d
                    parent[v] = u
    return edges


def pad_allowed(ref, num):
    for rx, nums, _ in ALLOWED_PADS:
        if rx.match(ref) and (nums is None or num in nums):
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('board'); ap.add_argument('snap'); ap.add_argument('out_dir')
    ap.add_argument('--blocks'); ap.add_argument('--gap-mm', type=float, default=1.0)
    ap.add_argument('--hole-mm', type=float, default=3.5); ap.add_argument('--edge-mm', type=float, default=1.5)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    board = pcbnew.LoadBoard(a.board)
    snap = json.load(open(a.snap))
    rev2 = [tuple(p) for p in snap['rev2_outline']]
    block_of = {}
    if a.blocks:
        for name, b in json.load(open(a.blocks)).items():
            for r in b['refs']:
                block_of[r] = name

    fps = list(board.GetFootprints())
    new = [f for f in fps if NEW_REF.match(f.GetReference())]
    heritage = [f for f in fps if not NEW_REF.match(f.GetReference())]
    side = lambda f: 'B' if f.GetLayer() == pcbnew.B_Cu else 'F'

    # --- placements
    bb = {}
    placements = []
    for f in fps:
        box, src = crt_bbox(f)
        bb[f.GetReference()] = (box, src)
    for f in sorted(new, key=lambda f: (re.sub(r'\d', '', f.GetReference()), int(re.search(r'\d+', f.GetReference()).group()))):
        box, src = bb[f.GetReference()]
        p = f.GetPosition()
        placements.append({'ref': f.GetReference(), 'value': f.GetValue(), 'footprint': str(f.GetFPID().GetLibItemName()),
                           'x': round(mm(p.x), 3), 'y': round(mm(p.y), 3), 'rot': round(f.GetOrientationDegrees(), 1), 'side': side(f),
                           'block': block_of.get(f.GetReference(), '?'), 'lcsc': _field(f, 'LCSC Part'),
                           'crt_bbox': [round(mm(box.GetLeft()), 2), round(mm(box.GetTop()), 2), round(mm(box.GetRight()), 2), round(mm(box.GetBottom()), 2)],
                           'crt_source': src, 'pads': f.Pads().__len__()})

    # --- gaps (same side, at least one new)
    gaps = []
    for i, f in enumerate(new):
        for g in fps:
            if g is f or (g in new and new.index(g) < i):
                continue
            if side(f) != side(g):
                continue
            d = rect_gap(bb[f.GetReference()][0], bb[g.GetReference()][0])
            if d < a.gap_mm:
                gaps.append({'a': f.GetReference(), 'b': g.GetReference(), 'gap_mm': round(d, 3), 'side': side(f),
                             'heritage_neighbour': g not in new})
    gaps.sort(key=lambda x: x['gap_mm'])

    # --- holes / edges
    holes = [(f.GetReference(), mm(f.GetPosition().x), mm(f.GetPosition().y)) for f in fps if re.match(r'^H\d+$', f.GetReference())]
    near_holes = []
    for f in new:
        box = bb[f.GetReference()][0]
        for h, hx, hy in holes:
            dx = max(mm(box.GetLeft()) - hx, hx - mm(box.GetRight()), 0)
            dy = max(mm(box.GetTop()) - hy, hy - mm(box.GetBottom()), 0)
            d = math.hypot(dx, dy)
            if d < a.hole_mm:
                near_holes.append({'ref': f.GetReference(), 'hole': h, 'dist_mm': round(d, 2)})
    outline = pcbnew.SHAPE_POLY_SET()
    board.GetBoardPolygonOutlines(outline, False)
    chain = outline.Outline(0)
    near_edge = []
    for f in new:
        box = bb[f.GetReference()][0]
        cx, cy = (box.GetLeft() + box.GetRight()) // 2, (box.GetTop() + box.GetBottom()) // 2
        pts = [(box.GetLeft(), box.GetTop()), (box.GetRight(), box.GetTop()), (box.GetLeft(), box.GetBottom()), (box.GetRight(), box.GetBottom()),
               (cx, box.GetTop()), (cx, box.GetBottom()), (box.GetLeft(), cy), (box.GetRight(), cy)]
        d = min(mm(chain.Distance(pcbnew.VECTOR2I(int(x), int(y)), True)) for x, y in pts)  # outline only (a closed chain returns 0 for interior points otherwise)
        if d < a.edge_mm:
            near_edge.append({'ref': f.GetReference(), 'edge_dist_mm': round(d, 2), 'footprint': str(f.GetFPID().GetLibItemName())})

    # --- ratsnest
    pads_by_net = defaultdict(list)
    for f in fps:
        for pd in f.Pads():
            n = pd.GetNetname()
            if not n or n == 'GND' or n.startswith('unconnected-'):
                continue
            p = pd.GetPosition()
            pads_by_net[n].append((mm(p.x), mm(p.y), f.GetReference(), pd.GetNumber(), f in new))
    nets = {}
    all_edges = []
    for n, pads in pads_by_net.items():
        if not any(p[4] for p in pads):
            continue  # heritage-only net
        # dedupe coincident pads (e.g. THT pads listed twice)
        uniq = {}
        for p in pads:
            uniq.setdefault((round(p[0], 3), round(p[1], 3)), p)
        pts = list(uniq.values())
        if len(pts) > 400:
            nets[n] = {'pads': len(pts), 'skipped': 'too many pads (plane net)'}
            continue
        edges = mst(pts)
        elist = []
        for i, j, L in edges:
            pi, pj = pts[i], pts[j]
            e = {'a': '%s.%s' % (pi[2], pi[3]), 'b': '%s.%s' % (pj[2], pj[3]), 'len_mm': round(L, 2),
                 'a_new': pi[4], 'b_new': pj[4], 'ax': pi[0], 'ay': pi[1], 'bx': pj[0], 'by': pj[1]}
            elist.append(e)
            all_edges.append((n, (pi[0], pi[1]), (pj[0], pj[1]), e))
        elist.sort(key=lambda e: -e['len_mm'])
        nets[n] = {'pads': len(pts), 'new_pads': sum(1 for p in pts if p[4]), 'mst_mm': round(sum(L for _, _, L in edges), 1),
                   'longest_mm': elist[0]['len_mm'] if elist else 0, 'edges': elist}
    # crossings in the new area (either endpoint outside the Rev2 outline)
    new_area = [(n, p, q, e) for n, p, q, e in all_edges if not (point_in_poly(p, rev2) and point_in_poly(q, rev2))]
    crossings = []
    for i in range(len(new_area)):
        n1, p1, q1, e1 = new_area[i]
        for j in range(i + 1, len(new_area)):
            n2, p2, q2, e2 = new_area[j]
            if n1 == n2:
                continue
            if seg_intersect(p1, q1, p2, q2):
                crossings.append({'net_a': n1, 'edge_a': '%s-%s' % (e1['a'], e1['b']), 'net_b': n2, 'edge_b': '%s-%s' % (e2['a'], e2['b'])})
    cross_by_net = defaultdict(int)
    for c in crossings:
        cross_by_net[c['net_a']] += 1
        cross_by_net[c['net_b']] += 1
    for n, v in nets.items():
        v['crossings'] = cross_by_net.get(n, 0)
    # per block
    blocks = defaultdict(lambda: {'internal_mst_mm': 0.0, 'edges_leaving': 0, 'edges_leaving_len_mm': 0.0, 'crossings': 0})
    for n, p, q, e in all_edges:
        ra, rb = e['a'].split('.')[0], e['b'].split('.')[0]
        ba, bb_ = block_of.get(ra, 'FC' if not e['a_new'] else '?'), block_of.get(rb, 'FC' if not e['b_new'] else '?')
        if ba == bb_:
            blocks[ba]['internal_mst_mm'] += e['len_mm']
        else:
            for b in (ba, bb_):
                blocks[b]['edges_leaving'] += 1
                blocks[b]['edges_leaving_len_mm'] += e['len_mm']
    for c in crossings:
        for key in ('edge_a', 'edge_b'):
            for r in [s.split('.')[0] for s in c[key].split('-')]:
                b = block_of.get(r)
                if b:
                    blocks[b]['crossings'] += 1
    for b in blocks.values():
        for k in ('internal_mst_mm', 'edges_leaving_len_mm'):
            b[k] = round(b[k], 1)

    # --- stubs (shared nets)
    stubs = []
    for n, pads in pads_by_net.items():
        newp = [p for p in pads if p[4]]
        fcp = [p for p in pads if not p[4] and point_in_poly((p[0], p[1]), rev2)]
        if not newp or not fcp:
            continue
        def nearest(cands):
            best = None
            for c in cands:
                for q in newp:
                    d = math.hypot(c[0] - q[0], c[1] - q[1])
                    if best is None or d < best[0]:
                        best = (d, '%s.%s' % (c[2], c[3]), '%s.%s' % (q[2], q[3]))
            return best
        allowed = [p for p in fcp if pad_allowed(p[2], p[3])]
        na = nearest(allowed) if allowed else None
        nany = nearest(fcp)
        stubs.append({'net': n, 'allowed_pad_to_new_mm': round(na[0], 2) if na else None, 'allowed_pad': na[1] if na else None, 'new_pad': na[2] if na else None,
                      'any_fc_pad_to_new_mm': round(nany[0], 2), 'any_fc_pad': nany[1],
                      'detour_risk': (na is None) or (nany[0] < na[0] - 3.0)})
    stubs.sort(key=lambda s: -(s['allowed_pad_to_new_mm'] or 999))

    sides = {'F': sum(1 for f in new if side(f) == 'F'), 'B': sum(1 for f in new if side(f) == 'B'),
             'distinct_footprints': len({str(f.GetFPID().GetLibItemName()) for f in new}),
             'distinct_values': len({(str(f.GetFPID().GetLibItemName()), f.GetValue()) for f in new}),
             'heritage_F': sum(1 for f in heritage if side(f) == 'F'), 'heritage_B': sum(1 for f in heritage if side(f) == 'B')}

    facts = {'board': os.path.basename(a.board), 'new_parts': len(new), 'sides': sides, 'placements': placements, 'gaps': gaps,
             'near_holes': near_holes, 'near_edge': near_edge, 'nets': nets, 'crossings': crossings, 'blocks': dict(blocks), 'stubs': stubs,
             'holes': [{'ref': h, 'x': round(x, 2), 'y': round(y, 2)} for h, x, y in holes]}
    json.dump(facts, open(os.path.join(a.out_dir, 'facts.json'), 'w'), indent=1)

    L = []
    L.append('# Placement facts — %s\n' % os.path.basename(a.board))
    L.append('New parts: %d (F %d / B %d); distinct footprints %d, distinct footprint+value %d; heritage F %d / B %d\n' %
             (len(new), sides['F'], sides['B'], sides['distinct_footprints'], sides['distinct_values'], sides['heritage_F'], sides['heritage_B']))
    L.append('## Courtyard gaps < %.1f mm (bbox-to-bbox, same side, at least one new part)\n' % a.gap_mm)
    L.append('| a | b | gap mm | side | heritage neighbour |\n|---|---|---|---|---|')
    for g in gaps:
        L.append('| %s | %s | %.3f | %s | %s |' % (g['a'], g['b'], g['gap_mm'], g['side'], 'yes' if g['heritage_neighbour'] else ''))
    L.append('\n## New parts within %.1f mm of a mounting-hole centre\n' % a.hole_mm)
    L.append('| ref | hole | dist mm |\n|---|---|---|')
    for h in sorted(near_holes, key=lambda h: h['dist_mm']):
        L.append('| %s | %s | %.2f |' % (h['ref'], h['hole'], h['dist_mm']))
    L.append('\n## New parts within %.1f mm of the board edge\n' % a.edge_mm)
    L.append('| ref | footprint | edge dist mm |\n|---|---|---|')
    for e in sorted(near_edge, key=lambda e: e['edge_dist_mm']):
        L.append('| %s | %s | %.2f |' % (e['ref'], e['footprint'], e['edge_dist_mm']))
    L.append('\n## Ratsnest — nets with new pads (GND excluded), sorted by MST length\n')
    L.append('| net | pads | new pads | MST mm | longest edge mm | crossings |\n|---|---|---|---|---|---|')
    for n, v in sorted(nets.items(), key=lambda kv: -kv[1].get('mst_mm', 0)):
        if 'skipped' in v:
            L.append('| %s | %d | – | skipped (%s) | | |' % (n, v['pads'], v['skipped']))
        else:
            L.append('| %s | %d | %d | %.1f | %.1f | %d |' % (n, v['pads'], v['new_pads'], v['mst_mm'], v['longest_mm'], v['crossings']))
    L.append('\nTotal MST edge crossings in the new area (different nets): %d\n' % len(crossings))
    L.append('## Per block\n')
    L.append('| block | internal MST mm | edges leaving | their length mm | crossings touching |\n|---|---|---|---|---|')
    for b, v in sorted(blocks.items()):
        L.append('| %s | %.1f | %d | %.1f | %d |' % (b, v['internal_mst_mm'], v['edges_leaving'], v['edges_leaving_len_mm'], v['crossings']))
    L.append('\n## Shared nets — attachment stubs (nearest allowed FC pad vs nearest any FC pad)\n')
    L.append('| net | allowed pad → new pad mm | allowed pad | new pad | any FC pad → new pad mm | any FC pad | detour risk |\n|---|---|---|---|---|---|---|')
    for s in stubs:
        L.append('| %s | %s | %s | %s | %.2f | %s | %s |' % (s['net'], s['allowed_pad_to_new_mm'], s['allowed_pad'], s['new_pad'], s['any_fc_pad_to_new_mm'], s['any_fc_pad'], 'YES' if s['detour_risk'] else ''))
    L.append('\n## Longest airwires (top 40)\n')
    L.append('| net | a | b | mm |\n|---|---|---|---|')
    longest = sorted(((n, e) for n, v in nets.items() if 'edges' in v for e in v['edges']), key=lambda t: -t[1]['len_mm'])[:40]
    for n, e in longest:
        L.append('| %s | %s | %s | %.1f |' % (n, e['a'], e['b'], e['len_mm']))
    L.append('\n## Placements\n')
    L.append('| ref | value | footprint | x | y | rot | side | block | LCSC |\n|---|---|---|---|---|---|---|---|---|')
    for p in placements:
        L.append('| %s | %s | %s | %.2f | %.2f | %g | %s | %s | %s |' % (p['ref'], p['value'], p['footprint'], p['x'], p['y'], p['rot'], p['side'], p['block'], p['lcsc']))
    open(os.path.join(a.out_dir, 'facts.md'), 'w').write('\n'.join(L) + '\n')
    print('facts: %d new parts, %d gaps < %.1f mm, %d near holes, %d near edge, %d nets, %d crossings, %d shared nets (%d detour risks) -> %s' %
          (len(new), len(gaps), a.gap_mm, len(near_holes), len(near_edge), len(nets), len(crossings), len(stubs), sum(1 for s in stubs if s['detour_risk']), a.out_dir))


if __name__ == '__main__':
    sys.exit(main())
