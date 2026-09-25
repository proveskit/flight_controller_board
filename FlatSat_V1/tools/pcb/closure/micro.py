#!/usr/bin/env python3
"""Area-aware fine router for short hops out of a fine-pitch fan-out ring (e.g. U200/EMU_FANOUT).

Promoted from .flatsat_work/phase2/micro.py (closure round 2, route_report.md D5/D7) -- the only
router on the project that can leave a rule-area fan-out ring, because it is the only one that
knows the relaxed clearance only applies where BOTH items intersect the rule area. The routing
algorithm (dual raster obstacle sets, Dijkstra on the raster, exact-polygon re-check of every
emitted segment/via via fan2's collides()/hole_ok()/edge_ok()) is unchanged from the scratch
version; this promotion removes the two hard-coded session-scratch paths (`PRO`, `SNAP`) and
wraps every path, the rule area and the net list in argparse.

WHAT IT DOES
    For each net in --only that has more than one connectivity cluster (via clusters.build()),
    finds the two nearest clusters, opens a padded bounding box around them, rasterises it at a
    chosen grid step into TWO obstacle sets per copper layer -- 0.20 mm (Default netclass) and
    0.127 mm (the rule area) -- and uses the relaxed set only in cells at least `--inset` mm
    inside the rule area (default 0.60 mm), which guarantees any obstacle close enough to matter
    there also intersects the area itself, matching KiCad's own `A.intersectsArea() &&
    B.intersectsArea()` rule semantics. Runs a multi-layer Dijkstra (mlroute.dijkstra_ml) over
    that raster from decreasing track widths (default 0.25, 0.20, 0.152, 0.127 mm, widest first)
    until one succeeds. The winning raster path is simplified to line segments and vias, then
    EVERY segment and via is re-checked against fan2's exact-polygon test (the real DRC-shaped
    rule, not the raster approximation) before being kept -- a raster win that fails the exact
    check is rejected and the net falls through to the next narrower width.

INPUTS
    BOARD     .kicad_pcb path (read).
    OUT       .kicad_pcb path to write (skipped with --dry-run).
    --only    comma list of net names (bare or full hierarchical) to attempt; required.
    --snap    heritage snapshot JSON (footprints/tracks/Rev2 outline) used only to keep new vias
              outside the Rev2 outline. Default: `<script dir>/../../baseline/heritage_rev2.json`,
              i.e. `tools/baseline/heritage_rev2.json` when this tool lives at
              `tools/pcb/closure/micro.py` -- pass --snap explicitly if that default does not
              resolve for your layout.
    --project/--pro   the board's .kicad_pro path, for netclass clearances. Default: BOARD with
                       its extension swapped to `.kicad_pro`.
    --pad     mm of padding around the nearest-cluster pair's bbox for the search window
              (default 6.0).
    --step    raster grid step in mm (default 0.02); auto-coarsened if the window would exceed
              9,000,000 cells.
    --area    x0,y0,x1,y1 in mm for the relaxed-clearance rule area (default the EMU_FANOUT area,
              266.5,88.0,280.0,101.5) -- also passed through to fan2's exact-polygon checks so
              the raster and the exact check agree on what "inside" means.
    --inset   mm inside --area before the relaxed 0.127 mm obstacle set is trusted (default 0.60).
    --widths  comma list of candidate track widths in mm, tried widest first (default
              0.25,0.20,0.152,0.127).
    --wmin    skip candidate widths below this value in mm (default 0.0; replaces the old
              MICRO_WMIN env var).
    --dry-run  do everything except SaveBoard(OUT).

OUTPUT
    OUT (a .kicad_pcb, unless --dry-run) with any closed nets' new tracks/vias added; stdout logs
    one line per net attempted ("ok gap X -> Y mm, w=..., N via(s), M seg" or "FAIL gap X mm
    (...)->(...)" or "already one cluster") and a final "micro: closed K of N" count.

EXACTNESS GUARANTEE
    The raster search is a heuristic accelerator only -- every track and via it proposes is
    re-verified by fan2's exact-polygon collides()/hole_ok()/edge_ok() (KiCad's own
    TransformShapeToPolygon + boolean intersection, the same shapes DRC itself tests) before
    being added to the board, and a raster win that fails that check is discarded, never emitted.
    So a net this tool reports "ok" has already passed the real clearance/hole/edge rule for
    every item it added; the raster only decides what to try, never what to accept.

PROMOTION FIX
    The scratch version had two hard-coded absolute paths at module scope (`PRO`, `SNAP`)
    pointing at one old session's scratchpad. Both are now `--project`/`--snap` arguments (with
    non-scratch, repo-relative defaults); nothing in this file points at a session-specific path.

USAGE
    micro.py BOARD OUT --only NET1,NET2[,...] [--snap heritage_rev2.json] [--project PRO]
             [--pad 6] [--step 0.02] [--area 266.5,88.0,280.0,101.5] [--inset 0.60]
             [--widths 0.25,0.20,0.152,0.127] [--wmin 0.0] [--dry-run]
    micro.py --help
"""
import argparse
import math
import os
import json

import numpy as np
import pcbnew
import rgeo
import mlroute
import clusters as CL
from rgeo import Board, Grid, TOMM, MM
import fan2
from fan2 import Obs, mk_track, mk_via, bb_of, collides, hole_ok, edge_ok, in_area, cu_layers, load_cls

DEFAULT_AREA = (266.5, 88.0, 280.0, 101.5)          # EMU_FANOUT default (brief 12 F13a)
DEFAULT_INSET = 0.60
DEFAULT_WIDTHS = (0.25, 0.2, 0.152, 0.127)
VIA_D, VIA_DR = 0.40, 0.20


def default_snap_path():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.normpath(os.path.join(here, '..', '..', 'baseline', 'heritage_rev2.json'))


def item_pts(it):
    if it.GetClass() == 'ZONE':
        return []
    p = it.GetPosition()
    if it.GetClass() in ('PAD', 'PCB_VIA'):
        return [(TOMM(p.x), TOMM(p.y))]
    s, e = it.GetStart(), it.GetEnd()
    return [(TOMM(s.x), TOMM(s.y)), (TOMM(e.x), TOMM(e.y))]


def mask_of(g, cluster, layer, hw, free):
    m = np.zeros((g.H, g.W), dtype=bool)
    for it in cluster:
        if it.GetClass() == 'ZONE':
            continue
        if it.GetClass() == 'PAD':
            if not it.IsOnLayer(layer):
                continue
            m |= mlroute.pad_inner(g, it, layer, hw)
        elif it.GetClass() == 'PCB_VIA':
            if not it.IsOnLayer(layer):
                continue
        elif it.GetLayer() != layer:
            continue
        ps = pcbnew.SHAPE_POLY_SET()
        try:
            it.TransformShapeToPolygon(ps, layer, 0, MM(0.005), pcbnew.ERROR_INSIDE)
        except Exception:
            continue
        for pts in rgeo.polyset_pts(ps):
            rgeo.fill_poly(m, pts, g.x0, g.y0, g.step)
    return m & free


def emit(board, cls, full, netname, got, d, simp=True):
    chain, w, g, frees, layers = got
    segs, cur = [], [chain[0]]
    for c in chain[1:]:
        if c[0] != cur[-1][0]:
            segs.append(cur); cur = [c]
        else:
            cur.append(c)
    segs.append(cur)
    parts, vias, prev = [], [], None
    for s2 in segs:
        li = s2[0][0]
        cells = [(jj, ii) for (l, jj, ii) in s2]
        if simp:
            pts = rgeo.simplify(cells, g, frees[li])
        else:
            keep = [cells[0]] + [cells[k] for k in range(1, len(cells) - 1)
                                 if (cells[k][0] - cells[k-1][0], cells[k][1] - cells[k-1][1])
                                 != (cells[k+1][0] - cells[k][0], cells[k+1][1] - cells[k][1])] + [cells[-1]]
            pts = [g.pos(jj, ii) for jj, ii in keep]
        if prev is not None:
            pts[0] = prev
        prev = pts[-1]
        parts.append((layers[li], pts))
    for k in range(1, len(segs)):
        vp = g.pos(segs[k][0][1], segs[k][0][2])
        vias.append(vp)
        parts[k - 1][1][-1] = (vp[0], vp[1])
        parts[k][1][0] = (vp[0], vp[1])
    obs = Obs(board, cls)
    nn = board.FindNet(full)
    new, ok = [], True
    for L, pts in parts:
        for a, b in zip(pts, pts[1:]):
            if math.hypot(a[0] - b[0], a[1] - b[1]) < 1e-9:
                continue
            t = mk_track(board, a, b, w, L, nn)
            if collides(obs, t, L, full, bb_of(t), in_area(bb_of(t))) or not edge_ok(obs, t, L) \
                    or not hole_ok(obs, t, [L], full):
                ok = False; break
            new.append(t); obs.add(t)
        if not ok:
            break
    if ok:
        for vp in vias:
            v = mk_via(board, vp, nn, VIA_D if in_area(bb_of(mk_via(board, vp, nn, VIA_D, VIA_DR))) else 0.46, VIA_DR)
            bad = False
            for L in cu_layers(board):
                if collides(obs, v, L, full, bb_of(v), in_area(bb_of(v))) or not edge_ok(obs, v, L):
                    bad = True; break
            if bad or not hole_ok(obs, v, cu_layers(board), full, pos=vp, drill=VIA_DR):
                ok = False; break
            new.append(v); obs.add(v)
    if not ok:
        return False
    for t in new:
        board.Add(t)
    ln = sum(math.dist(a, b) for L, pts in parts for a, b in zip(pts, pts[1:]))
    print('  %-28s ok  gap %.2f -> %.2f mm, w=%.3f, %d via(s), %d seg'
          % (netname, d, ln, w, len(vias), len(new) - len(vias)))
    return True


def run(bp, out, only, snap_path=None, project=None, pad=6.0, step=0.02, area=None, inset=None,
        widths=None, wmin=0.0, dry_run=False):
    """Core algorithm, unchanged from the scratch version's main(); callable directly."""
    global DEFAULT_AREA
    area = tuple(area) if area else DEFAULT_AREA
    inset = DEFAULT_INSET if inset is None else inset
    widths = tuple(widths) if widths else DEFAULT_WIDTHS
    fan2.AREA = area          # keep fan2's exact-polygon checks in agreement with the raster
    snap_path = snap_path or default_snap_path()
    pro = project or (os.path.splitext(bp)[0] + '.kicad_pro')
    snap = json.load(open(snap_path))
    bd = Board(bp, snap)
    board = bd.b
    mlroute.load_netclasses(pro, board)
    cls = load_cls(pro, board)
    layers = [pcbnew.F_Cu, board.GetLayerID('In2.Cu'), pcbnew.B_Cu]
    done = 0
    for netname in only:
        full = None
        for n in board.GetNetsByName().keys():
            if str(n) == netname or str(n).rsplit('/', 1)[-1] == netname:
                full = str(n); break
        if full is None:
            print('  %s: no such net' % netname); continue
        cl = CL.build(board).get(board.FindNet(full).GetNetCode(), [])
        if len(cl) < 2:
            print('  %-28s already one cluster' % netname); continue
        # nearest pair of clusters
        best = None
        for i in range(len(cl)):
            for j in range(i + 1, len(cl)):
                for a in [p for it in cl[i] for p in item_pts(it)]:
                    for b in [p for it in cl[j] for p in item_pts(it)]:
                        dd = math.hypot(a[0] - b[0], a[1] - b[1])
                        if best is None or dd < best[0]:
                            best = (dd, i, j, a, b)
        d, i, j, pa, pb = best
        x0 = min(pa[0], pb[0]) - pad; x1 = max(pa[0], pb[0]) + pad
        y0 = min(pa[1], pb[1]) - pad; y1 = max(pa[1], pb[1]) + pad
        st = step
        while ((x1 - x0) / st) * ((y1 - y0) / st) > 9000000:
            st *= 1.25
        g = Grid(bd, x0, y0, x1, y1, st)
        xs = g.x0 + (np.arange(g.W) + 0.5) * g.step
        ys = g.y0 + (np.arange(g.H) + 0.5) * g.step
        inner = ((xs >= area[0] + inset) & (xs <= area[2] - inset))[None, :] & \
                ((ys >= area[1] + inset) & (ys <= area[3] - inset))[:, None]
        got = None
        for w in [x for x in widths if x >= wmin]:
            hw = w / 2.0
            frees = []
            for L in layers:
                b20 = g.obstacles(L, full, hw, 0.205, None, 0.2)
                b12 = g.obstacles(L, full, hw, 0.131, None, 0.2)
                frees.append((~b20) | (inner & (~b12)))
            vb20 = np.zeros((g.H, g.W), dtype=bool)
            vb12 = np.zeros((g.H, g.W), dtype=bool)
            for L in rgeo.copper_layers(board):
                vb20 |= g.obstacles(L, full, VIA_D / 2.0, 0.205, None, 0.2)
                vb12 |= g.obstacles(L, full, VIA_D / 2.0, 0.131, None, 0.2)
            vm = ((~vb20) | (inner & (~vb12))) & (~g.hole_mask(full, VIA_DR / 2.0, extra=0.0)) & (~g.inside_rev2)
            starts = []
            for li, L in enumerate(layers):
                m = mask_of(g, cl[i], L, hw, frees[li])
                for jj, ii in zip(*np.where(m)):
                    starts.append((li, int(jj), int(ii)))
            goals = [mask_of(g, cl[j], L, hw, frees[li]) for li, L in enumerate(layers)]
            if not starts or not any(m.any() for m in goals):
                empty = 'start' if not starts else 'goal'
                if w == 0.127:
                    print('    (%s mask empty at w=%.3f)' % (empty, w))
                continue
            chain = mlroute.dijkstra_ml(frees, vm, starts, goals, st, via_cost=1.2)
            if chain is None:
                continue
            got = (chain, w, g, frees, layers)
            if emit(board, cls, full, netname, got, d) or \
                    emit(board, cls, full, netname, got, d, simp=False):
                got = 'done'
                break
            got = None
            print('    w=%.3f rejected by the exact check, trying narrower' % w)
        if got is None:
            print('  %-28s FAIL gap %.2f mm  (%.1f,%.1f)->(%.1f,%.1f)' % (netname, d, pa[0], pa[1], pb[0], pb[1]))
            continue
        done += 1
        bd.refresh_tracks()
        continue
    print('micro: closed %d of %d' % (done, len(only)))
    if not dry_run:
        pcbnew.SaveBoard(out, board)
        print('saved', out)
    return done, len(only)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description='Area-aware fine router for short hops out of a fine-pitch fan-out ring.')
    ap.add_argument('board', help='.kicad_pcb path (read)')
    ap.add_argument('out', help='.kicad_pcb path to write')
    ap.add_argument('--only', required=True, help='comma list of net names to attempt')
    ap.add_argument('--snap', dest='snap_path', default=None,
                     help='heritage snapshot JSON (default: <script dir>/../../baseline/heritage_rev2.json)')
    ap.add_argument('--project', '--pro', dest='project', default=None,
                     help='.kicad_pro path for netclass clearances (default: BOARD with .kicad_pro extension)')
    ap.add_argument('--pad', type=float, default=6.0, help='mm padding around the search window (default 6.0)')
    ap.add_argument('--step', type=float, default=0.02, help='raster grid step in mm (default 0.02)')
    ap.add_argument('--area', default=None, metavar='X0,Y0,X1,Y1',
                     help='relaxed-clearance rule-area bbox in mm (default the EMU_FANOUT area '
                          '266.5,88.0,280.0,101.5)')
    ap.add_argument('--inset', type=float, default=None,
                     help='mm inside --area before the relaxed obstacle set is trusted (default 0.60)')
    ap.add_argument('--widths', default=None,
                     help='comma list of candidate track widths in mm, widest first '
                          '(default 0.25,0.20,0.152,0.127)')
    ap.add_argument('--wmin', type=float, default=0.0, help='skip candidate widths below this mm value')
    ap.add_argument('--dry-run', action='store_true', help='do everything except SaveBoard(OUT)')
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    only = args.only.split(',')
    area = tuple(float(x) for x in args.area.split(',')) if args.area else None
    widths = tuple(float(x) for x in args.widths.split(',')) if args.widths else None
    run(args.board, args.out, only, snap_path=args.snap_path, project=args.project, pad=args.pad,
        step=args.step, area=area, inset=args.inset, widths=widths, wmin=args.wmin,
        dry_run=args.dry_run)


if __name__ == '__main__':
    main()
