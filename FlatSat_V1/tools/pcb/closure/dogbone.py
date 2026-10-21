#!/usr/bin/env python3
"""Move vias off SMD pads (owner ruling F16): dogbone each via to the cheapest clear off-pad site.

Run with KiCad's bundled python3.

  dogbone.py BOARD OUT [--via UUID ...] [--vip via_in_pad.json] [--snap heritage_rev2.json]
             [--max-r 2.5] [--step 0.025] [--pad-gap 0.10] [--area-via] [--push N]
             [--max-tries 2000] [--json REPORT.json] [--dry-run]

For each via (by uuid, or every via in a via_in_pad.py --json report):
  1. Candidate sites p on a grid within --max-r of the old centre c, cheapest first. Cost is the added
     copper: the pad-layer dogbone length plus, per attached track end on another layer, the growth from
     re-pointing that end from c to p (a shortening counts as zero), ties broken by distance from c.
  2. A site is kept only if the via annulus stays --pad-gap off every pad of any net (vias are tented,
     so this is the mask dam to the pad opening), and the via, the dogbone and every rewired track pass
     fan2.py's exact KiCad-polygon clearance (per-pair rule; EMU_FANOUT relaxation only when both items
     intersect the area), copper-to-hole, hole-to-hole and board-edge checks, and KiCad's connectivity
     engine (clusters.py) shows the net in no more pieces than before. A pour net is judged on an
     in-memory refill of its zones; the stored fills are put back before saving.
  3. Rewire: on the pad layer a dogbone, never wider than the pad, runs from inside each same-net pad the
     via touched to p, straight or with one orthogonal or 45-degree knee. Tracks there that end inside the
     pad stay. On every other layer each track end at c is re-pointed to p, or bridged with a c-to-p
     segment if the re-pointed track would collide. Heritage tracks are only ever bridged, never edited.
--area-via gives the 0.40/0.20 EMU_FANOUT via to any site wholly inside that area; elsewhere a via is
at least 0.46/0.20. --push N allows up to N attempts per via to clear a blocked site: a blocking new
via is nudged up to 0.6 mm by this same search, a blocking new track segment is shoved up to 0.6 mm
sideways (free joints drag their neighbours, fixed joints get a jog), up to three per site, each with
the moving via and dogbone as phantom obstacles and its own connectivity check.
Every existing item an accepted move did not edit must come out unchanged, or the board is not saved.
The report lists, per via, MOVED with the new site, via size, added track length and anything cleared,
or NOSITE with the obstacles that rejected the most candidates, which is the POFV reason.
"""
import argparse
import json
import math
import os
import sys
from collections import Counter

import pcbnew

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import clusters  # noqa: E402
import fan2  # noqa: E402

MM, TOMM = pcbnew.FromMM, pcbnew.ToMM
AREA = fan2.AREA
DEF_VIA = (0.46, 0.20)
AREA_VIA = (0.40, 0.20)   # EMU_FANOUT only (emu_fanout_via rule)


def pt(v):
    return (TOMM(v.x), TOMM(v.y))


def vec(p):
    return pcbnew.VECTOR2I_MM(float(p[0]), float(p[1]))


def dist(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


def end_of(track, which):
    """A copy of a track end. GetStart()/GetEnd() return live references, so a saved one would follow
    every later SetStart()/SetEnd() and an undo would restore nothing."""
    v = track.GetStart() if which == 'start' else track.GetEnd()
    return pcbnew.VECTOR2I(int(v.x), int(v.y))


def uid(item):
    return item.m_Uuid.AsString()


class Why(str):
    """A rejection reason that also carries the copper item that caused it (None for edge/hole/pad rules)."""

    def __new__(cls, text, item=None):
        w = super().__new__(cls, text)
        w.item = item
        return w


def tag(prefix, why):
    return Why(prefix + why, getattr(why, 'item', None))


def obstacles(board, cls, without=None, extra=()):
    """fan2.Obs plus phantom `extra` items, with the moving via removed (its hole would otherwise fail
    hole-to-hole at every site)."""
    obs = fan2.Obs(board, cls)
    for it in extra:
        obs.add(it)
    if without is None:
        return obs
    c = pt(without.GetPosition())
    for l in obs.by_layer:
        obs.by_layer[l] = [e for e in obs.by_layer[l] if uid(e[2]) != uid(without)]
    obs.holes = [h for h in obs.holes if not (abs(h[0] - c[0]) < 1e-4 and abs(h[1] - c[1]) < 1e-4)]
    return obs


def outer_pads(board):
    out = []
    for fp in board.GetFootprints():
        for p in fp.Pads():
            for l in (pcbnew.F_Cu, pcbnew.B_Cu):
                if p.IsOnLayer(l):
                    out.append((p, l, p.GetEffectivePolygon(l, pcbnew.ERROR_INSIDE)))
    return out


def inside_point(poly, c, centre):
    """A point inside the pad on the way from c to the pad centre, just past the pad edge."""
    if poly.Contains(vec(c)):
        return c
    for k in range(1, 21):
        t = k / 20
        q = (c[0] + (centre[0] - c[0]) * t, c[1] + (centre[1] - c[1]) * t)
        if poly.Contains(vec(q)):
            t = min(1.0, t + 0.05)
            return (c[0] + (centre[0] - c[0]) * t, c[1] + (centre[1] - c[1]) * t)
    return centre


def wholly_in_area(p, r):
    return AREA[0] <= p[0] - r and p[0] + r <= AREA[2] and AREA[1] <= p[1] - r and p[1] + r <= AREA[3]


class Plan:
    """Everything one via move touches, captured before any candidate is tried."""

    def __init__(self, board, via, pads, heritage):
        self.via = via
        self.net = via.GetNetname()
        self.c = pt(via.GetPosition())
        self.dia = TOMM(via.GetWidth(pcbnew.F_Cu))
        self.drill = TOMM(via.GetDrill())
        r = self.dia / 2
        self.pads = [(p, l, poly) for p, l, poly in pads
                     if p.GetNetname() == self.net and poly.Collide(vec(self.c), MM(r))]
        self.pad_layers = {l for _, l, _ in self.pads}
        self.ends = []      # (track, 'start'|'end', layer, end point, far point)
        self.heritage_hit = []
        widths = [0.25]
        for t in board.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T or t.GetNetname() != self.net:
                continue
            for which, e, f in (('start', t.GetStart(), t.GetEnd()), ('end', t.GetEnd(), t.GetStart())):
                e = pt(e)
                if dist(e, self.c) > r + 1e-4:
                    continue
                widths.append(TOMM(t.GetWidth()))
                if t.GetLayer() in self.pad_layers and any(poly.Contains(vec(e)) for _, l, poly in self.pads
                                                           if l == t.GetLayer()):
                    continue  # still lands in the pad after the move
                if uid(t) in heritage:
                    self.heritage_hit.append(uid(t))
                self.ends.append((t, which, t.GetLayer(), e, pt(f)))
        self.width = min(max(widths), self.dia)
        # a dogbone is never wider than the pad it leaves
        self.dog = [(inside_point(poly, self.c, pt(p.GetPosition())), l,
                     min(self.width, TOMM(min(p.GetSize(l).x, p.GetSize(l).y)))) for p, l, poly in self.pads]

    def cost(self, p):
        return (sum(dist(q, p) for q, _, _ in self.dog)
                + sum(max(0.0, dist(f, p) - dist(f, e)) for _, _, _, e, f in self.ends))


def via_ok(board, obs, plan, p, dia, pads, gap):
    """None if a via fits at p, else the Why."""
    r = dia / 2 + gap
    for pd, l, poly in pads:
        if poly.Collide(vec(p), MM(r)):
            return Why(f'on pad {pd.GetParentFootprint().GetReference()}.{pd.GetNumber()}')
    v = fan2.mk_via(board, p, board.FindNet(plan.net), dia, plan.drill)
    bb = fan2.bb_of(v)
    for l in fan2.cu_layers(board):
        hit = fan2.collides(obs, v, l, plan.net, bb, fan2.in_area(bb))
        if hit:
            return Why('via clearance ' + describe(hit[1], hit[0]), hit[1])
        if not fan2.edge_ok(obs, v, l):
            return Why('via board edge')
    if not fan2.hole_ok(obs, v, fan2.cu_layers(board), plan.net, pos=p, drill=plan.drill):
        return Why('via hole clearance')
    return None


def describe(item, net):
    if item.GetClass() == 'PAD':
        return f'pad {item.GetParentFootprint().GetReference()}.{item.GetNumber()} ({net})'
    kind = {'PCB_VIA': 'via', 'PCB_TRACK': 'track', 'PCB_ARC': 'arc'}.get(item.GetClass(), 'copper item')
    return f'{kind} {net}'


def seg_reason(board, obs, a, b, w, layer, net):
    t = fan2.mk_track(board, a, b, w, layer, board.FindNet(net))
    bb = fan2.bb_of(t)
    hit = fan2.collides(obs, t, layer, net, bb, fan2.in_area(bb))
    if hit:
        return Why('track clearance ' + describe(hit[1], hit[0]), hit[1])
    if not fan2.edge_ok(obs, t, layer):
        return Why('track board edge')
    if not fan2.hole_ok(obs, t, [layer], net):
        return Why('track hole clearance')
    return None


def dog_path(board, obs, q, p, w, layer, net):
    """Straight dogbone, else an orthogonal or 45-degree two-segment one. Returns (points, None) or (None, why)."""
    dx, dy = p[0] - q[0], p[1] - q[1]
    m = min(abs(dx), abs(dy))
    sx, sy = math.copysign(1, dx), math.copysign(1, dy)
    knees = [(q[0], p[1]), (p[0], q[1]), (q[0] + sx * m, q[1] + sy * m), (p[0] - sx * m, p[1] - sy * m)]
    first = None
    for path in [[q, p]] + [[q, k, p] for k in knees if dist(k, q) > 1e-4 and dist(k, p) > 1e-4]:
        why = next((r for r in (seg_reason(board, obs, a, b, w, layer, net) for a, b in zip(path, path[1:])) if r),
                   None)
        if not why:
            return path, None
        first = first or why
    return None, first


def rewire(board, obs, plan, p):
    """Return (edits, None) or (None, reason). Edits: ('point', track, which) | ('seg', a, b, w, layer)."""
    edits = []
    for q, l, w in plan.dog:
        if dist(q, p) < 1e-4:
            continue
        path, why = dog_path(board, obs, q, p, w, l, plan.net)
        if why:
            return None, tag('dogbone ', why)
        edits += [('seg', a, b, w, l) for a, b in zip(path, path[1:])]
    for t, which, l, e, f in plan.ends:
        w = TOMM(t.GetWidth())
        if uid(t) not in plan.heritage_hit and not seg_reason(board, obs, f, p, w, l, plan.net):
            edits.append(('point', t, which))
            continue
        why = seg_reason(board, obs, e, p, w, l, plan.net)
        if why:
            return None, tag('rewire ', why)
        edits.append(('seg', e, p, w, l))
    return edits, None


def refill_net(board, net):
    zs = [z for z in board.Zones() if not z.GetIsRuleArea() and z.GetNetname() == net]
    if zs:
        pcbnew.ZONE_FILLER(board).Fill(zs)


def pieces(board, net):
    """Connected pieces of one net per KiCad's connectivity engine. A pour net is judged on a fresh fill
    of its own zones, since a stored fill has no copper at a new site yet. (The board connectivity's
    GetUnconnectedCount() reads 0 in a headless pcbnew, so it cannot serve here.)"""
    refill_net(board, net)
    return len(clusters.build(board).get(board.FindNet(net).GetNetCode(), [None]))


def apply(board, plan, p, dia, edits):
    o = plan.via.GetPosition()
    undo = [('via', pcbnew.VECTOR2I(int(o.x), int(o.y)), plan.via.GetWidth(pcbnew.F_Cu))]
    plan.via.SetPosition(vec(p))
    plan.via.SetWidth(MM(dia))
    added = 0.0
    for e in edits:
        if e[0] == 'point':
            t, which = e[1], e[2]
            old = end_of(t, which)
            before = TOMM(t.GetLength())
            (t.SetStart if which == 'start' else t.SetEnd)(vec(p))
            added += TOMM(t.GetLength()) - before
            undo.append(('point', t, which, old))
        else:
            _, a, b, w, l = e
            t = fan2.mk_track(board, a, b, w, l, board.FindNet(plan.net))
            board.Add(t)
            added += dist(a, b)
            undo.append(('seg', t))
    return added, undo


def revert(board, plan, undo):
    for u in reversed(undo):
        if u[0] == 'nested':
            revert(board, u[1], u[2])
        elif u[0] == 'via':
            plan.via.SetPosition(u[1])
            plan.via.SetWidth(u[2])
        elif u[0] == 'point':
            (u[1].SetStart if u[2] == 'start' else u[1].SetEnd)(u[3])
        else:
            board.Remove(u[1])


def shove(board, cls, heritage, track, extra, pads):
    """Translate one foreign track segment sideways, its free joints dragging their neighbours along and
    each fixed joint (a via, a pad, a heritage neighbour) bridged by a short jog. Returns undo or None."""
    if track.GetClass() != 'PCB_TRACK' or uid(track) in heritage:
        return None
    net, layer, w = track.GetNetname(), track.GetLayer(), TOMM(track.GetWidth())
    A, B = pt(track.GetStart()), pt(track.GetEnd())
    L = dist(A, B)
    if L < 1e-3:
        return None
    nx, ny = -(B[1] - A[1]) / L, (B[0] - A[0]) / L
    joints = []
    for which, E in (('start', A), ('end', B)):
        near = [t for t in board.GetTracks() if t.GetNetname() == net and uid(t) != uid(track)
                and (dist(pt(t.GetStart()), E) < 1e-3 or dist(pt(t.GetEnd()), E) < 1e-3)]
        fixed = any(t.GetClass() == 'PCB_VIA' or uid(t) in heritage for t in near if t.IsOnLayer(layer)
                    ) or any(pd.GetNetname() == net and l == layer and poly.Contains(vec(E)) for pd, l, poly in pads)
        nbrs = [(t, 'start' if dist(pt(t.GetStart()), E) < 1e-3 else 'end') for t in near
                if t.GetClass() == 'PCB_TRACK' and t.GetLayer() == layer]
        joints.append((which, E, fixed, nbrs))
    obs = obstacles(board, cls, extra=extra)
    base = pieces(board, net)
    for s in (0.05, -0.05, 0.1, -0.1, 0.15, -0.15, 0.2, -0.2, 0.3, -0.3, 0.4, -0.4, 0.5, -0.5, 0.6, -0.6):
        d = (nx * s, ny * s)
        undo, check = [], [track]
        for which, E, fixed, nbrs in joints:
            E2 = (E[0] + d[0], E[1] + d[1])
            undo.append(('point', track, which, end_of(track, which)))
            (track.SetStart if which == 'start' else track.SetEnd)(vec(E2))
            if fixed:
                j = fan2.mk_track(board, E, E2, w, layer, track.GetNet())
                board.Add(j)
                undo.append(('seg', j))
                check.append(j)
            else:
                for t, tw in nbrs:
                    undo.append(('point', t, tw, end_of(t, tw)))
                    (t.SetStart if tw == 'start' else t.SetEnd)(vec(E2))
                    check.append(t)
        bad = any(seg_reason(board, obs, pt(t.GetStart()), pt(t.GetEnd()), TOMM(t.GetWidth()), layer, net)
                  for t in check if t.GetLength() > 0)
        if not bad and pieces(board, net) <= base:
            return undo
        revert(board, None, undo)
    return None


def sites(c, max_r, step):
    n = int(max_r / step)
    return [(round(c[0] + i * step, 4), round(c[1] + j * step, 4))
            for i in range(-n, n + 1) for j in range(-n, n + 1) if 0 < math.hypot(i, j) * step <= max_r]


def site_dia(plan, p, small):
    if wholly_in_area(p, DEF_VIA[0] / 2):
        return min(plan.dia, AREA_VIA[0]) if small else plan.dia
    return max(plan.dia, DEF_VIA[0])


def move_one(board, cls, pads, heritage, via, max_r, step, max_tries, gap, small=False, push=0, extra=()):
    """Relocate one via. Returns (record, undo list or None). `extra` are phantom obstacles; `push` is the
    number of blocker nudges/shoves allowed (see the module docstring)."""
    plan = Plan(board, via, pads, heritage)
    rec = {'uuid': uid(via), 'net': plan.net, 'old': [round(x, 4) for x in plan.c],
           'pads': [f'{p.GetParentFootprint().GetReference()}.{p.GetNumber()}' for p, _, _ in plan.pads],
           'old_via': f'{plan.dia:.2f}/{plan.drill:.2f}'}
    if plan.heritage_hit:
        rec['note'] = 'attached heritage track kept; bridged with new segment'
    obs = obstacles(board, cls, via, extra)
    cands = sorted((round(plan.cost(p), 2), dist(p, plan.c), p) for p in sites(plan.c, max_r, step))
    base = pieces(board, plan.net)
    reasons = Counter()
    tried = pushes = 0
    for _, _, p in cands:
        dia = site_dia(plan, p, small)
        if any(poly.Collide(vec(p), MM(dia / 2 + gap)) for _, _, poly in pads):
            continue
        tried += 1
        if tried > max_tries:
            break
        chain, cleared = [], []
        while True:
            why = via_ok(board, obs, plan, p, dia, pads, gap)
            edits = None
            if not why:
                edits, why = rewire(board, obs, plan, p)
            blocker = getattr(why, 'item', None)
            if (not why or not push or pushes >= push or len(chain) >= 3 or blocker is None
                    or uid(blocker) in heritage):
                break
            pushes += 1
            phantom = [fan2.mk_via(board, p, board.FindNet(plan.net), dia, plan.drill)]
            phantom += [fan2.mk_track(board, q, p, w, l, board.FindNet(plan.net)) for q, l, w in plan.dog]
            if blocker.GetClass() == 'PCB_VIA':
                sub, sub_undo = move_one(board, cls, pads, heritage, blocker, 0.6, step / 2, 400, gap, small,
                                         extra=list(extra) + phantom)
                if sub_undo is None:
                    break
                chain.append(('nested', sub.pop('_plan'), sub_undo))
                cleared.append({'via': sub['net'], 'from': sub['old'], 'to': sub['new']})
            else:
                sh = shove(board, cls, heritage, blocker, list(extra) + phantom, pads)
                if sh is None:
                    break
                chain.append(('nested', None, sh))
                cleared.append({'track': blocker.GetNetname(), 'layer': board.GetLayerName(blocker.GetLayer())})
            obs = obstacles(board, cls, via, extra)
        if not why:
            added, undo = apply(board, plan, p, dia, edits)
            if pieces(board, plan.net) <= base:
                rec.update(status='MOVED', new=[round(x, 4) for x in p], new_via=f'{dia:.2f}/{plan.drill:.2f}',
                           added_mm=round(added, 3), shift_mm=round(dist(p, plan.c), 3), tried=tried, _plan=plan)
                if cleared:
                    rec['cleared'] = cleared
                return rec, chain + undo
            revert(board, plan, undo)
            why = Why('connectivity')
        if chain:
            revert(board, None, chain)
            obs = obstacles(board, cls, via, extra)
        reasons[str(why)] += 1
    rec.update(status='NOSITE', tried=tried, reasons=reasons.most_common(6))
    return rec, None


def net_lengths(board, prefix):
    out = Counter()
    for t in board.GetTracks():
        if t.Type() != pcbnew.PCB_VIA_T and prefix in t.GetNetname():
            out[t.GetNetname().rsplit('/', 1)[-1]] += TOMM(t.GetLength())
    return out


def geometry(board):
    out = {}
    for t in board.GetTracks():
        a, b = t.GetStart(), t.GetEnd()
        out[uid(t)] = (a.x, a.y, b.x, b.y, t.GetWidth(pcbnew.F_Cu) if t.GetClass() == 'PCB_VIA' else t.GetWidth())
    return out


def touched(undo, plan=None, acc=None):
    """uuids of the existing items an applied move edited, from its undo list."""
    acc = set() if acc is None else acc
    for u in undo:
        if u[0] == 'nested':
            touched(u[2], u[1], acc)
        elif u[0] == 'via':
            acc.add(uid(plan.via))
        elif u[0] == 'point':
            acc.add(uid(u[1]))
    return acc


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('board')
    ap.add_argument('out')
    ap.add_argument('--via', action='append', default=[])
    ap.add_argument('--vip', help='via_in_pad.py --json report; every listed via is processed')
    ap.add_argument('--snap', default=os.path.join(os.path.dirname(__file__), '..', '..', 'baseline',
                                                   'heritage_rev2.json'))
    ap.add_argument('--project')
    ap.add_argument('--max-r', type=float, default=2.5)
    ap.add_argument('--step', type=float, default=0.025)
    ap.add_argument('--pad-gap', type=float, default=0.10,
                    help='min distance from the via annulus to any pad edge, a solder-mask dam against wicking')
    ap.add_argument('--area-via', action='store_true',
                    help='use the 0.40/0.20 EMU_FANOUT via at any site wholly inside that area')
    ap.add_argument('--push', type=int, default=0, metavar='N',
                    help='up to N attempts per via to nudge a blocking new via or shove a blocking new track '
                         '(up to 0.6 mm) to free a site (try 60)')
    ap.add_argument('--max-tries', type=int, default=2000)
    ap.add_argument('--json')
    ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    board = pcbnew.LoadBoard(a.board)
    cls = fan2.load_cls(a.project or os.path.splitext(a.board)[0] + '.kicad_pro', board)
    heritage = set(json.load(open(a.snap))['tracks'])
    uuids = list(a.via)
    if a.vip:
        uuids += [h['uuid'] for h in json.load(open(a.vip))]
    uuids = list(dict.fromkeys(uuids))
    vias = {uid(t): t for t in board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T}
    pads = outer_pads(board)
    stored = [(z, l, pcbnew.SHAPE_POLY_SET(z.GetFilledPolysList(l))) for z in board.Zones()
              if not z.GetIsRuleArea() for l in z.GetLayerSet().Seq() if z.HasFilledPolysForLayer(l)]
    qspi0 = net_lengths(board, 'EMU_QSPI')
    before = geometry(board)
    edited = set()
    report = []
    for u in uuids:
        if u in heritage:
            report.append({'uuid': u, 'status': 'SKIP', 'note': 'heritage via'})
            continue
        if u not in vias:
            report.append({'uuid': u, 'status': 'SKIP', 'note': 'not on board'})
            continue
        rec, undo = move_one(board, cls, pads, heritage, vias[u], a.max_r, a.step, a.max_tries, a.pad_gap,
                             a.area_via, a.push)
        if undo:
            touched(undo, rec['_plan'], edited)
        rec.pop('_plan', None)
        report.append(rec)
        tail = (f"-> {rec['new']} {rec['new_via']} +{rec['added_mm']} mm"
                + (f" cleared {rec['cleared']}" if 'cleared' in rec else '')
                if rec['status'] == 'MOVED'
                else str(rec['reasons']))
        print(f"{rec['status']:6} {','.join(rec['pads']):18} {rec['net'][-24:]:24} {tail}", flush=True)
    qspi1 = net_lengths(board, 'EMU_QSPI')
    qspi = {n: round(qspi1[n] - qspi0[n], 3) for n in sorted(qspi0)}
    print('QSPI length delta mm:', qspi)
    moved = sum(r['status'] == 'MOVED' for r in report)
    print(f'moved {moved}/{len(report)}')
    if a.json:
        json.dump({'vias': report, 'qspi_delta_mm': qspi}, open(a.json, 'w'), indent=1)
    after = geometry(board)
    stray = sorted(k for k, g in before.items() if after.get(k) != g and k not in edited)
    if stray:
        sys.exit(f'refusing to save: {len(stray)} existing items changed outside any accepted move '
                 f'(an undo failed): {stray[:5]}')
    if not a.dry_run:
        for z, l, ps in stored:     # in-memory refills only judged connectivity; keep the stored fills
            z.SetFilledPolysList(l, ps)
        pcbnew.SaveBoard(a.out, board)


if __name__ == '__main__':
    main()
