#!/usr/bin/env python3
"""Build the Freerouting keep-out fixture that enforces the L11 attachment rule at routing time.

  make_keepout.py SNAP.json PRE.kicad_pcb OUT.json [--band 12] [--clearance 0.3] [--outer-layers F.Cu,B.Cu]

Run with KiCad's bundled python3. Writes a JSON spec that tools/pcb/route.sh applies as rule-area zones on
the DSN-export copy (never on the delivered board):

  FC_CORE            tracks+vias forbidden, all copper layers, Rev2 outline deflated by --band mm
  FC_VIA_KEEPOUT     vias forbidden, all copper layers, the whole Rev2 outline (no new vias in the flight section)
  FC_BAND_<inner>    tracks+vias forbidden, each inner layer, the whole band ring (no stubs on plane layers)
  FC_HERITAGE_<L>_n  tracks+vias forbidden, outer layer L: every heritage track / via / non-allowed pad in
                     the band, inflated by --clearance, minus the allowed attachment pads (attachment_check
                     .ALLOWED_PADS) inflated by --clearance, so Freerouting can only reach an allowed pad
                     and can never tap a heritage trace.

KiCad exports these as Specctra (keepout ...) / (via_keepout ...) records per layer, which Freerouting
2.4.1 honours (its parser knows keepout / via_keepout / place_keepout; it does NOT know wire_keepout,
so never build a tracks-only rule area). Heritage zone fills are deliberately NOT part of the fixture:
a stub from an edge connector pad has to cross the F/B pours to leave the flight section, and the
pour refill carving around it inside the band is the accepted cost of any stub (heritage.py checks
that fills inside the core stay identical). Taps into a pour edge are still caught by
attachment_check.py and pruned.

Spec entries: {"name", "forbid": "both"|"vias", "layers": "all"|[...], "poly": [[x, y], ...]} (mm).
"""
import argparse
import json
import os
import sys

try:
    import pcbnew
except ImportError:
    sys.exit("run with KiCad's bundled python3")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from attachment_check import ALLOWED_PADS  # noqa: E402

mm = pcbnew.ToMM
MM = pcbnew.VECTOR2I_MM


def poly_from_points(points):
    p = pcbnew.SHAPE_POLY_SET()
    p.NewOutline()
    for x, y in points:
        p.Append(MM(x, y))
    return p


def deflated(points, inset_mm):
    p = poly_from_points(points)
    if inset_mm > 0:
        p.Inflate(-pcbnew.FromMM(inset_mm), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))
    return p


def outlines_of(p):
    out = []
    for i in range(p.OutlineCount()):
        o = p.Outline(i)
        pts = [[round(mm(o.CPoint(k).x), 3), round(mm(o.CPoint(k).y), 3)] for k in range(o.PointCount())]
        if len(pts) >= 3:
            out.append(pts)
    return out


def pad_allowed(fp_ref, pad_number):
    for rx, nums, _limit in ALLOWED_PADS:
        if rx.match(fp_ref) and (nums is None or pad_number in nums):
            return True
    return False


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('snap')
    ap.add_argument('board')
    ap.add_argument('out')
    ap.add_argument('--band', type=float, default=12.0, help='depth of the attachment band (core = outline deflated by this)')
    ap.add_argument('--clearance', type=float, default=0.3, help='inflation around heritage copper / carve-out around allowed pads')
    ap.add_argument('--outer-layers', default='F.Cu,B.Cu', help='layers on which stubs may run; every other copper layer is fully blocked in the band')
    a = ap.parse_args()

    snap = json.load(open(a.snap))
    outline_pts = snap['rev2_outline']
    her_tracks = set(snap['tracks'])
    her_fps = set(snap['footprints'])
    board = pcbnew.LoadBoard(a.board)
    n_cu = board.GetCopperLayerCount()
    cu_layers = ['F.Cu'] + ['In%d.Cu' % i for i in range(1, n_cu - 1)] + ['B.Cu']
    outer = [l for l in a.outer_layers.split(',') if l]
    inner = [l for l in cu_layers if l not in outer]
    clr = pcbnew.FromMM(a.clearance)
    maxerr = pcbnew.FromMM(0.01)

    outline = poly_from_points(outline_pts)
    core = deflated(outline_pts, a.band)
    ring = poly_from_points(outline_pts)
    ring.BooleanSubtract(core)
    ring_bb = ring.BBox()

    spec = {'source': os.path.basename(a.board), 'band_mm': a.band, 'clearance_mm': a.clearance, 'keepouts': []}
    for pts in outlines_of(core):
        spec['keepouts'].append({'name': 'FC_CORE', 'forbid': 'both', 'layers': 'all', 'poly': pts})
    for pts in outlines_of(outline):
        spec['keepouts'].append({'name': 'FC_VIA_KEEPOUT', 'forbid': 'vias', 'layers': 'all', 'poly': pts})
    ring_f = pcbnew.SHAPE_POLY_SET(ring)
    ring_f.Fracture()
    for l in inner:
        for pts in outlines_of(ring_f):
            spec['keepouts'].append({'name': 'FC_BAND_%s' % l, 'forbid': 'both', 'layers': [l], 'poly': pts})

    stats = {}
    for lname in outer:
        layer = board.GetLayerID(lname)
        cop = pcbnew.SHAPE_POLY_SET()
        n_tr = n_via = n_pad = n_allowed = 0
        for t in board.GetTracks():
            if t.m_Uuid.AsString() not in her_tracks:
                continue
            if not t.GetBoundingBox().Intersects(ring_bb):
                continue
            if t.GetClass() == 'PCB_VIA':
                if not t.IsOnLayer(layer):
                    continue
                n_via += 1
            else:
                if t.GetLayer() != layer:
                    continue
                n_tr += 1
            t.TransformShapeToPolygon(cop, layer, clr, maxerr, pcbnew.ERROR_OUTSIDE)
        allowed = pcbnew.SHAPE_POLY_SET()
        for fp in board.GetFootprints():
            if fp.m_Uuid.AsString() not in her_fps:
                continue
            if not fp.GetBoundingBox().Intersects(ring_bb):
                continue
            for pad in fp.Pads():
                if not pad.IsOnLayer(layer):
                    continue
                if pad_allowed(fp.GetReference(), pad.GetNumber()):
                    pad.TransformShapeToPolygon(allowed, layer, clr, maxerr, pcbnew.ERROR_OUTSIDE)
                    n_allowed += 1
                else:
                    pad.TransformShapeToPolygon(cop, layer, clr, maxerr, pcbnew.ERROR_OUTSIDE)
                    n_pad += 1
        cop.Simplify()
        cop.BooleanIntersection(ring)
        allowed.Simplify()
        cop.BooleanSubtract(allowed)
        cop.Fracture()
        polys = outlines_of(cop)
        for i, pts in enumerate(polys):
            spec['keepouts'].append({'name': 'FC_HERITAGE_%s_%d' % (lname, i), 'forbid': 'both', 'layers': [lname], 'poly': pts})
        stats[lname] = dict(tracks=n_tr, vias=n_via, pads=n_pad, allowed_pads=n_allowed, polygons=len(polys),
                            area_mm2=round(cop.Area() / 1e12, 1))

    json.dump(spec, open(a.out, 'w'))
    print('keep-out spec written to %s: %d record(s)' % (a.out, len(spec['keepouts'])))
    print('  core (both, all layers): outline deflated %.1f mm; via_keepout: whole Rev2 outline; band ring blocked on %s' % (a.band, inner))
    for l, s in stats.items():
        print('  %s: heritage %d tracks, %d vias, %d non-allowed pads in the band -> %d polygon(s), %.1f mm2; %d allowed pad(s) carved out'
              % (l, s['tracks'], s['vias'], s['pads'], s['polygons'], s['area_mm2'], s['allowed_pads']))
    print('  ring area %.1f mm2' % (ring.Area() / 1e12))


if __name__ == '__main__':
    sys.exit(main())
