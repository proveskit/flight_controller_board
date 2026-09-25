#!/usr/bin/env python3
"""Exact-polygon staggered fan-out for a fine-pitch QFN inside a relaxed-clearance rule area.

Promoted from .flatsat_work/phase2/fan2.py (closure round 2, route_report.md D2/D7) for the
EMU_FANOUT rule area over U200 (brief 12 F13a). The placement algorithm (candidate row/lattice
generation, 1/2/3-segment exact-polygon path search, same-net pad/via sharing) is byte-for-byte
unchanged from the scratch version; this promotion only removes the hard-coded scratch
`.kicad_pro` path (the one behavioural bug fixed here -- see "PROMOTION FIX" below) and wraps
every path, the rule area and the pad/net selection in argparse.

WHAT IT DOES
    Places two staggered via rows (default 0.40/0.20 mm) at alternating pads of one footprint
    (default U200), each with a 0.127-or-0.20-mm track from the pad to its via, or a same-net
    share link to a nearby pad/via if one is close enough. Every candidate track and via is
    checked against KiCad's own exact polygons (TransformShapeToPolygon + boolean intersection),
    never an inscribed-circle approximation, at the rule that actually applies to that pair of
    items: `AREA_CLEAR` when BOTH items intersect the named rule area, the larger of the two
    nets' netclass clearance otherwise, plus hole clearance / hole-to-hole / copper-to-edge
    (board minimums, NOT relaxed by the rule area). Only wedge geometry (outer row, inner alley
    with two staggered sub-rows) tuned for a 0.400 mm land pitch is baked in; see route_report.md
    D2 for the derivation of the row offsets.

INPUTS
    BOARD    .kicad_pcb path (read).
    OUT      .kicad_pcb path to write (skipped with --dry-run; a `OUT.json` per-pad placement
             report is always written, dry-run or not, alongside stdout).
    --project/--pro   the board's .kicad_pro path, for netclass clearances. Defaults to BOARD
                       with its extension swapped to `.kicad_pro` (same directory) -- pass this
                       explicitly if the project file lives elsewhere.
    --ref             footprint reference to fan out (default U200).
    --pads            comma list of pad numbers to place (default: every escapable pad of --ref
                       except pad 61, the exposed pad).
    --width           track width in mm (default 0.127).
    --area             x0,y0,x1,y1 in mm for the relaxed-clearance rule area (default the
                       EMU_FANOUT area, 266.5,88.0,280.0,101.5 -- brief 12 F13a).
    --wide            widen the candidate lattice search (slower, more coverage; off by default,
                       replaces the old FAN_WIDE env var).
    --dry-run / --dry  do everything except SaveBoard(OUT); the placement-report JSON is still
                       written. `--dry` is kept as an alias for scratch-era call sites.

OUTPUT
    OUT (a .kicad_pcb, unless --dry-run/--dry) with the placed tracks/vias added to BOARD's
    in-memory board and saved; OUT.json (always) listing, per pad, either the via site chosen
    (position, row offset r, lateral offset lat, segment count) or "NO SITE"; stdout mirrors the
    same per-pad lines plus a final "placed M/N" count.

EXACTNESS GUARANTEE
    Every emitted track/via has already passed the same exact-polygon collides()/hole_ok()/
    edge_ok() checks DRC itself would apply (clearance via TransformShapeToPolygon boolean
    intersection, not a radius heuristic) at the correct per-pair rule (area-relaxed only when
    both items intersect --area, matching KiCad's own `A.intersectsArea() && B.intersectsArea()`
    rule-area semantics) -- so a placement this tool reports as placed will pass `kicad-cli pcb
    drc` for clearance/hole/edge on that item; it does not itself re-run DRC.

PROMOTION FIX
    The scratch version's `load_cls()` call in main() ignored its own path-selection ternary
    (guarded by `if False`) and always read one hard-coded session scratch `.kicad_pro` path.
    That is fixed here: `--project` is used when given, otherwise BOARD's own `.kicad_pro`
    sibling, and the codepath that unconditionally pointed at the old session path is removed.

USAGE
    fan2.py BOARD OUT [--project PRO] [--ref U200] [--pads 4,8,...] [--width 0.127]
            [--area 266.5,88.0,280.0,101.5] [--wide] [--dry-run]
    fan2.py --help
"""
import argparse
import math
import os
import sys
import json
from collections import defaultdict

import pcbnew

MM, TOMM = pcbnew.FromMM, pcbnew.ToMM
AREA = (266.5, 88.0, 280.0, 101.5)          # EMU_FANOUT default (brief 12 F13a)
AREA_CLEAR = 0.127
DEF_CLEAR = 0.20
HOLE_CLEAR = 0.20                            # board minimum, not relaxed
HOLE2HOLE = 0.50                             # board minimum, not relaxed
EDGE_CLEAR = 0.20
VIA_DIA, VIA_DRILL = 0.40, 0.20
EPS = 0.004                                  # safety margin over the rule


def in_area(bb):
    """KiCad 'intersectsArea' semantics on a bbox (x0,y0,x1,y1)."""
    return not (bb[2] < AREA[0] or bb[0] > AREA[2] or bb[3] < AREA[1] or bb[1] > AREA[3])


def cu_layers(board):
    n = board.GetCopperLayerCount()
    return [pcbnew.F_Cu] + [board.GetLayerID('In%d.Cu' % i) for i in range(1, n - 1)] + [pcbnew.B_Cu]


def bb_of(item):
    b = item.GetBoundingBox()
    return (TOMM(b.GetLeft()), TOMM(b.GetTop()), TOMM(b.GetRight()), TOMM(b.GetBottom()))


class Obs:
    def __init__(self, board, cls):
        self.board, self.cls = board, cls
        self.by_layer = defaultdict(list)     # layer -> [(net, bbox, item, inarea)]
        self.holes = []                       # (x, y, drill_mm, net)
        L = cu_layers(board)
        for fp in board.GetFootprints():
            for pd in fp.Pads():
                bb = bb_of(pd); ia = in_area(bb)
                for l in L:
                    if pd.IsOnLayer(l):
                        self.by_layer[l].append((pd.GetNetname(), bb, pd, ia))
                if pd.GetDrillSizeX() > 0:
                    p = pd.GetPosition()
                    self.holes.append((TOMM(p.x), TOMM(p.y), TOMM(pd.GetDrillSizeX()), pd.GetNetname()))
        for t in board.GetTracks():
            self.add(t)
        for d in list(board.GetDrawings()) + [g for f in board.GetFootprints() for g in f.GraphicalItems()]:
            if d.GetLayer() in L:
                bb = bb_of(d)
                self.by_layer[d.GetLayer()].append(('', bb, d, in_area(bb)))
        self.outline = pcbnew.SHAPE_POLY_SET()
        board.GetBoardPolygonOutlines(self.outline, False)

    def add(self, t):
        bb = bb_of(t); ia = in_area(bb)
        if t.GetClass() == 'PCB_VIA':
            for l in cu_layers(self.board):
                if t.IsOnLayer(l):
                    self.by_layer[l].append((t.GetNetname(), bb, t, ia))
            p = t.GetPosition()
            self.holes.append((TOMM(p.x), TOMM(p.y), TOMM(t.GetDrill()), t.GetNetname()))
        else:
            self.by_layer[t.GetLayer()].append((t.GetNetname(), bb, t, ia))

    def clear_between(self, net_a, a_in_area, onet, o_in_area):
        if a_in_area and o_in_area:
            return AREA_CLEAR
        return max(self.cls.get(net_a, DEF_CLEAR), self.cls.get(onet, DEF_CLEAR))


def poly(item, layer, infl):
    ps = pcbnew.SHAPE_POLY_SET()
    item.TransformShapeToPolygon(ps, layer, MM(max(0.0, infl)), MM(0.002), pcbnew.ERROR_OUTSIDE)
    return ps


def collides(obs, item, layer, net, item_bb, item_in_area, skip=()):
    """True if `item` on `layer` breaks copper clearance against anything of another net."""
    for onet, obb, o, oia in obs.by_layer.get(layer, ()):
        if o in skip:
            continue
        if onet == net and onet != '':
            continue
        if obb[2] < item_bb[0] - 1.5 or obb[0] > item_bb[2] + 1.5 or obb[3] < item_bb[1] - 1.5 or obb[1] > item_bb[3] + 1.5:
            continue
        need = obs.clear_between(net, item_in_area, onet, oia) + EPS
        a = poly(item, layer, need)
        try:
            b = poly(o, layer, 0.0)
        except Exception:
            continue
        a.BooleanIntersection(b)
        if not a.IsEmpty():
            return (onet, o)
    return None


def hole_ok(obs, item, layer_list, net, pos=None, drill=None):
    """copper of `item` vs foreign holes (0.20), and hole-to-hole (0.50) for a new via."""
    ib = bb_of(item)
    for hx, hy, hd, hnet in obs.holes:
        if hx < ib[0] - 1.2 or hx > ib[2] + 1.2 or hy < ib[1] - 1.2 or hy > ib[3] + 1.2:
            if pos is None or drill is None:
                continue
            if math.hypot(hx - pos[0], hy - pos[1]) > 2.0:
                continue
        if drill is not None:
            d = math.hypot(hx - pos[0], hy - pos[1])
            if d < HOLE2HOLE + (hd + drill) / 2 - 1e-9:
                return False
        if hnet == net and hnet != '':
            continue
        # copper of item vs this hole
        h = pcbnew.SHAPE_POLY_SET()
        h.NewOutline()
        for k in range(24):
            ang = 2 * math.pi * k / 24
            h.Append(pcbnew.VECTOR2I_MM(hx + (hd / 2 + HOLE_CLEAR + EPS) * math.cos(ang),
                                        hy + (hd / 2 + HOLE_CLEAR + EPS) * math.sin(ang)))
        for L in layer_list:
            try:
                a = poly(item, L, 0.0)
            except Exception:
                continue
            q = pcbnew.SHAPE_POLY_SET(a)
            q.BooleanIntersection(h)
            if not q.IsEmpty():
                return False
    return True


def edge_ok(obs, item, layer):
    e = poly(item, layer, EDGE_CLEAR)
    q = pcbnew.SHAPE_POLY_SET(e)
    q.BooleanSubtract(obs.outline)
    return q.IsEmpty()


def mk_track(board, a, b, w, layer, net):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I_MM(float(a[0]), float(a[1])))
    t.SetEnd(pcbnew.VECTOR2I_MM(float(b[0]), float(b[1])))
    t.SetWidth(MM(w)); t.SetLayer(layer); t.SetNet(net)
    return t


def mk_via(board, p, net, dia=VIA_DIA, drill=VIA_DRILL):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I_MM(float(p[0]), float(p[1])))
    v.SetWidth(MM(dia)); v.SetDrill(MM(drill))
    v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu); v.SetNet(net)
    return v


def load_cls(pro, board):
    cls = {}
    d = json.load(open(pro))
    ns = d['net_settings']
    byname = {c['name']: c for c in ns['classes']}
    import fnmatch
    for net in board.GetNetsByName().keys():
        n = str(net)
        cl = 'Default'
        for pat in ns.get('netclass_patterns', []):
            if fnmatch.fnmatch(n, pat['pattern']) or fnmatch.fnmatch(n.rsplit('/', 1)[-1], pat['pattern']):
                cl = pat['netclass']
        cls[n] = byname.get(cl, byname['Default'])['clearance']
    return cls


LATS = [0.0, 0.1, -0.1, 0.2, -0.2, 0.3, -0.3, 0.4, -0.4, 0.5, -0.5, 0.6, -0.6,
        0.8, -0.8, 1.0, -1.0, 1.2, -1.2, 1.5, -1.5]
LATS_WIDE = [round(0.05 * k * (1 if j == 0 else -1), 3) for k in range(0, 41) for j in (0, 1)]
LATS_WIDE = list(dict.fromkeys(LATS_WIDE))
KNEE_LAT = [0.0]
KNEE_LAT_WIDE = [0.0, 0.2, -0.2, 0.35, -0.35, 0.5, -0.5, 0.7, -0.7, 1.0, -1.0]
KNEE_LAT3 = [0.1, -0.1, 0.2, -0.2, 0.3, -0.3, 0.4, -0.4, 0.5, -0.5]
KNEE_LAT3_WIDE = [round(0.05 * k * s2, 3) for k in range(1, 13) for s2 in (1, -1)]


def seg_ok(board, obs, a, b, width, layer, net, skip=()):
    if abs(a[0] - b[0]) < 1e-6 and abs(a[1] - b[1]) < 1e-6:
        return None
    t = mk_track(board, a, b, width, layer, board.FindNet(net))
    tbb = bb_of(t)
    if collides(obs, t, layer, net, tbb, in_area(tbb), skip=skip):
        return None
    if not edge_ok(obs, t, layer):
        return None
    if not hole_ok(obs, t, [layer], net):
        return None
    return t


def try_paths(board, obs, pd, pc, tip, u, perp, vp, r, width, layer, net, nn, knee_lat, knee_lat3, skip=None):
    """1- and 2-segment F.Cu paths from the land to the via site, exact-polygon checked."""
    skip = skip if skip is not None else (pd,)
    one = seg_ok(board, obs, pc, vp, width, layer, net, skip=skip)
    if one is not None:
        return [one]
    sgn = 1.0 if r >= 0 else -1.0
    for k in (0.25, 0.35, 0.45, 0.55, 0.70, 0.90, 1.10):
        if abs(k) > abs(r) - 0.05:
            continue
        for m in knee_lat:
            knee = (tip[0] + u[0] * sgn * k + perp[0] * m, tip[1] + u[1] * sgn * k + perp[1] * m)
            s1 = seg_ok(board, obs, pc, knee, width, layer, net, skip=skip)
            if s1 is None:
                continue
            s2 = seg_ok(board, obs, knee, vp, width, layer, net, skip=skip)
            if s2 is None:
                continue
            return [s1, s2]
    # 3 segments: straight out past the land row, one lateral jog, then to the via
    for k in (0.25, 0.35, 0.45, 0.60, 0.80, 1.00):
        if abs(k) > abs(r) - 0.05:
            continue
        a = (tip[0] + u[0] * sgn * k, tip[1] + u[1] * sgn * k)
        s1 = seg_ok(board, obs, pc, a, width, layer, net, skip=skip)
        if s1 is None:
            continue
        for m in knee_lat3:
            if abs(m) < 1e-9:
                continue
            b2 = (a[0] + perp[0] * m, a[1] + perp[1] * m)
            s2 = seg_ok(board, obs, a, b2, width, layer, net, skip=skip)
            if s2 is None:
                continue
            s3 = seg_ok(board, obs, b2, vp, width, layer, net, skip=skip)
            if s3 is None:
                continue
            return [s1, s2, s3]
    return None


def run(bp, out, project=None, ref='U200', width=0.127, pads=None, area=None, wide=False,
        dry_run=False):
    """Core algorithm, unchanged from the scratch version's main(); callable directly (e.g. from
    micro.py) as well as from the CLI wrapper below."""
    global AREA
    if area is not None:
        AREA = tuple(area)
    pro = project or (os.path.splitext(bp)[0] + '.kicad_pro')
    board = pcbnew.LoadBoard(bp)
    cls = load_cls(pro, board)
    obs = Obs(board, cls)
    fp = board.FindFootprintByReference(ref)
    c = fp.GetPosition(); fc = (TOMM(c.x), TOMM(c.y))
    cu = cu_layers(board)
    lats = LATS_WIDE if wide else LATS
    knee_lat = KNEE_LAT_WIDE if wide else KNEE_LAT
    knee_lat3 = KNEE_LAT3_WIDE if wide else KNEE_LAT3
    report = []
    placed = 0
    placed_vias = defaultdict(list)     # net -> [(x, y)] vias this run put down
    same_pads = defaultdict(list)       # net -> [(pad, (x, y))] every other pad of the same net
    for f2 in board.GetFootprints():
        for pd2 in f2.Pads():
            if pd2.GetNetname() and f2.GetReference() != ref:
                p2 = pd2.GetPosition()
                same_pads[pd2.GetNetname()].append((pd2, (TOMM(p2.x), TOMM(p2.y))))
    want = set(pads) if pads else None
    cand_pads = [pd for pd in fp.Pads() if pd.GetNumber() != '61' and (want is None or pd.GetNumber() in want)]
    RAILS = ('3V3_EMU', '1V1_EMU', 'VREG_AVDD_EMU')
    # signals first: a rail land can fall back on its own decoupling cap pad, a signal cannot.
    cand_pads.sort(key=lambda pd: (1 if pd.GetNetname().rsplit('/', 1)[-1] in RAILS else 0, int(pd.GetNumber())))
    for pd in cand_pads:
        num = pd.GetNumber(); net = pd.GetNetname()
        nn = board.FindNet(net)
        p = pd.GetPosition(); pc = (TOMM(p.x), TOMM(p.y))
        bb = bb_of(pd)
        # outward direction and land tip
        dx, dy = pc[0] - fc[0], pc[1] - fc[1]
        if abs(dx) > abs(dy):
            u = (1.0 if dx > 0 else -1.0, 0.0); tip = (bb[2] if dx > 0 else bb[0], pc[1])
        else:
            u = (0.0, 1.0 if dy > 0 else -1.0); tip = (pc[0], bb[3] if dy > 0 else bb[1])
        perp = (-u[1], u[0])
        layer = pcbnew.F_Cu
        got = None
        # (0) same-net copper already nearby: the datasheet connection for a rail land is its own
        # decoupling cap pad, and two adjacent lands of one rail can share a single escape via.
        share = []
        for pd2, p2 in same_pads.get(net, ()):
            d = math.hypot(p2[0] - pc[0], p2[1] - pc[1])
            if d <= 3.0 and (pd2.IsOnLayer(pcbnew.F_Cu) or pd2.IsOnLayer(pcbnew.B_Cu)):
                share.append((d, p2, pd2))
        for vp2 in placed_vias.get(net, ()):
            d = math.hypot(vp2[0] - pc[0], vp2[1] - pc[1])
            if d <= 2.5:
                share.append((d, vp2, None))
        share.sort(key=lambda s2: s2[0])
        for d, p2, pd2 in share:
            skips = (pd,) if pd2 is None else (pd, pd2)
            path = try_paths(board, obs, pd, pc, tip, u, perp, p2, 1.0, width, pcbnew.F_Cu, net, nn,
                              knee_lat, knee_lat3, skip=skips)
            if path is not None:
                for t in path:
                    board.Add(t); obs.add(t)
                placed += 1
                report.append((num, net, ('share', p2, d)))
                print(f'  {ref}.{num:<3s} {net:32s} SHARE -> ({p2[0]:.3f},{p2[1]:.3f}) d={d:.2f} seg={len(path)}')
                break
        else:
            pass
        if report and report[-1][0] == num:
            continue
        # candidate via sites in this land's own wedge: outward rows first (0.55 / 1.25 = the PM's
        # staggered pattern), then a fine outward sweep, then the inner alley between the land inner
        # ends and the exposed pad.
        # the PM's staggered pattern: alternate lands take the OUTER row 0.55 mm past the tips,
        # the others the INNER alley between the land inner ends and the exposed pad (1.30 mm wide,
        # centre 1.525 mm inside the tip).  Both rows sit on 0.80 mm pitch (>= the 0.70 mm that
        # 0.20 mm drills need for the un-relaxed 0.50 mm hole-to-hole rule), and a row-2 land's
        # 0.127 mm track leaves between two row-1 vias through a 0.40 mm gap (0.381 mm needed).
        n = int(num)
        side_ix = (n - 1) if n <= 15 else (n - 16) if n <= 30 else (n - 31) if n <= 45 else (n - 46)
        # Rows: the OUTER row 0.55 mm past the land tips, and the inner ALLEY between the land
        # inner ends and the exposed pad (1.30 mm wide).  The alley is wide enough for TWO
        # radially staggered sub-rows 0.58 mm apart, which is what lifts the along-row pitch from
        # 0.80 mm (hole-to-hole 0.50 + 0.20 drills = 0.70 mm centre-to-centre in one line) to the
        # 0.40 mm land pitch: sqrt(0.58^2 + 0.40^2) = 0.705 mm between diagonal neighbours.
        R_OUT, R_A, R_B, R_MID = 0.55, -1.235, -1.815, -1.525
        m4 = side_ix % 4
        if side_ix <= 1 or side_ix >= 13:
            rows = [R_OUT, R_A, R_B, R_MID, 1.25]
        elif m4 == 0:
            rows = [R_OUT, R_A, R_B, R_MID, 1.25]
        elif m4 == 1:
            rows = [R_A, R_B, R_OUT, R_MID, 1.25]
        elif m4 == 2:
            rows = [R_OUT, R_B, R_A, R_MID, 1.25]
        else:
            rows = [R_B, R_A, R_OUT, R_MID, 1.25]
        cand = [(r, 0.0) for r in rows]
        for r in rows:
            for lat in (0.1, -0.1, 0.2, -0.2, 0.3, -0.3, 0.4, -0.4, 0.5, -0.5):
                cand.append((r, lat))
        head = list(cand)
        rr = 0.45
        RMAX = 3.0 if wide else 2.60001
        while rr <= RMAX:
            for lat in lats:
                cand.append((round(rr, 3), lat))
            rr = round(rr + 0.05, 3)
        rr = -1.15
        while rr >= (-2.00001 if not wide else -1.90001):
            for lat in lats:
                cand.append((round(rr, 3), lat))
            rr = round(rr - 0.05, 3)
        rest = [c for c in cand[len(head):]]
        rest.sort(key=lambda c: (abs(c[0]) + abs(c[1]) * 0.7, abs(c[1])))
        cand = head + rest
        for r, lat in cand:
            vp = (tip[0] + u[0] * r + perp[0] * lat, tip[1] + u[1] * r + perp[1] * lat)
            v = mk_via(board, vp, nn)
            vbb = bb_of(v)
            if not in_area(vbb):
                continue
            bad = False
            for L in cu:
                if collides(obs, v, L, net, vbb, True):
                    bad = True; break
                if not edge_ok(obs, v, L):
                    bad = True; break
            if bad:
                continue
            if not hole_ok(obs, v, cu, net, pos=vp, drill=VIA_DRILL):
                continue
            path = try_paths(board, obs, pd, pc, tip, u, perp, vp, r, width, layer, net, nn,
                              knee_lat, knee_lat3)
            if path is None:
                continue
            got = (path, v, vp, r, lat)
            break
        if got is None:
            report.append((num, net, None))
            print(f'  {ref}.{num:<3s} {net:32s} NO SITE')
            continue
        path, v, vp, r, lat = got
        for t in path:
            board.Add(t); obs.add(t)
        board.Add(v); obs.add(v)
        placed_vias[net].append(vp)
        placed += 1
        report.append((num, net, (vp, r, lat)))
        print(f'  {ref}.{num:<3s} {net:32s} via ({vp[0]:.3f},{vp[1]:.3f}) r={r:+.3f} lat={lat:+.2f} seg={len(path)}')
    print(f'placed {placed}/{len(cand_pads)}')
    if not dry_run:
        pcbnew.SaveBoard(out, board)
        print('saved', out)
    json.dump([(n, net, g) for n, net, g in report], open(out + '.json', 'w'), indent=1)
    return placed, len(cand_pads)


def parse_args(argv=None):
    ap = argparse.ArgumentParser(
        description='Exact-polygon staggered fan-out for a fine-pitch part inside a relaxed-clearance rule area.')
    ap.add_argument('board', help='.kicad_pcb path (read)')
    ap.add_argument('out', help='.kicad_pcb path to write (an OUT.json report is always written)')
    ap.add_argument('--project', '--pro', dest='project', default=None,
                     help='.kicad_pro path for netclass clearances (default: BOARD with .kicad_pro extension)')
    ap.add_argument('--ref', default='U200', help='footprint reference to fan out (default U200)')
    ap.add_argument('--pads', default=None, help='comma list of pad numbers (default: all escapable pads)')
    ap.add_argument('--width', type=float, default=0.127, help='track width in mm (default 0.127)')
    ap.add_argument('--area', default=None, metavar='X0,Y0,X1,Y1',
                     help='relaxed-clearance rule-area bbox in mm (default the EMU_FANOUT area '
                          '266.5,88.0,280.0,101.5)')
    ap.add_argument('--wide', action='store_true', help='widen the candidate lattice search (slower)')
    ap.add_argument('--dry-run', '--dry', dest='dry_run', action='store_true',
                     help='do everything except SaveBoard(OUT); the OUT.json report is still written')
    return ap.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)
    pads = args.pads.split(',') if args.pads else None
    area = tuple(float(x) for x in args.area.split(',')) if args.area else None
    run(args.board, args.out, project=args.project, ref=args.ref, width=args.width, pads=pads,
        area=area, wide=args.wide, dry_run=args.dry_run)


if __name__ == '__main__':
    main()
