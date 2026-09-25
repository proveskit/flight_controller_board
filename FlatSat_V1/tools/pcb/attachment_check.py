#!/usr/bin/env python3
"""L11 attachment-rule gate (Phase-2 brief §3 L11): new copper may enter the Rev2 flight section only as
short stubs from allowed pads. Run with KiCad's bundled python3.

  attachment_check.py SNAP.json BOARD.kicad_pcb [--band 12] [--max-stub 12] [--json OUT.json]

SNAP.json must be a heritage.py snapshot that carries "rev2_outline" (heritage.py snapshot stores it).
Checks every track/via whose uuid is not in the snapshot:
  * a via inside the Rev2 outline                                    -> violation
  * a track inside/crossing the outline that is not part of a stub   -> violation
  * a stub = connected chain of new tracks whose inside part: touches exactly one allowed pad
    (any pad of a heritage connector J*, or R104/R100/R103 pad 1 for the EN taps), stays within
    --band mm of the outline boundary, is <= --max-stub mm long, lies on the pad's layer(s), and
    touches no heritage track/via endpoint                           -> allowed
  * more than one stub per net into the flight section              -> warning (one per net is the rule; two are tolerated with a reason)
  * heritage zone filled areas that changed by > 0.5 %              -> warning (fills inside the flight section must not change)
Exit 0 = compliant (warnings allowed), 1 = violations.
"""
import argparse
import json
import math
import re
import sys
from collections import defaultdict

try:
    import pcbnew
except ImportError:
    sys.exit('run with KiCad\'s bundled python3')

# (reference regex, allowed pad numbers or None = all, max stub length inside the flight section in mm)
# Brief L11 attachment map. Face connectors and the Pico-Lock inhibit connectors sit within 5 mm of the old edge;
# J14 / J16 / J19 within 12 mm; INHIB_2 exists only on J7 / J10 (~20 mm deep) so those get a longer allowance;
# the three EN nets have no connector and are picked up at U6's IN pads (8-10 mm from the bottom edge, bottom side)
# or at R104.1 / R100.1 (11-12 mm). R103 (Deploy2_EN, 35 mm deep) is not an allowed tap.
# Owner amendment 2026-09-20 (panel PLR-01): the bottom-side face connectors J2/J9/J13 are walled off on B.Cu by the
# heritage PAYLOAD_BATT/DEPLOY1 traces, so each of their stubs may make exactly ONE B.Cu->F.Cu layer change with a
# via inside the attachment band (within VIA_BAND_MM of the Rev2 edge, not on a heritage endpoint). Every other via
# inside the Rev2 outline is still a violation.
# Extended 2026-09-20 (PM, routing attempt 2 / brief §12 F11): the same DEPLOY1/PAYLOAD_BATT wall runs north to y 65.3 and
# also boxes in J16 pin 1 (USBBOOT) and J14 pins 10/12 (BATT_SDA/BATT_SCL); those stubs get the same single layer change.
VIA_ALLOWED = [
    (re.compile(r'^J(2|9|13)$'), None),
    (re.compile(r'^J16$'), {'1'}),
    (re.compile(r'^J14$'), {'10', '12'}),
    # Owner ruling 2026-09-22 (brief §12 F14): Deploy2_EN at U6.6 is fenced on F.Cu (0.202 mm hole) and B.Cu (0.182 mm)
    # by heritage copper (route report §D6); its stub gets the same single B.Cu->F.Cu layer change inside the band.
    (re.compile(r'^U6$'), {'6'}),
]
VIA_BAND_MM = 24.0   # the via must lie inside the stub's own allowance band (checked as depth from the Rev2 edge)


def via_allowed(ref, num):
    return any(rx.match(ref) and (nums is None or num in nums) for rx, nums in VIA_ALLOWED)


# Owner ruling 2026-09-20 (brief §12 F12): these three nets cannot be reached at their pad without touching heritage
# copper (J6.5/J1.6 sit exactly over the bottom-side connector pads and are wrapped by their own face-power traces;
# U6.6 is boxed on both layers). Their stub may instead END ON the same net's heritage track or via (a T-junction that
# changes no heritage geometry) within TAP_RADIUS_MM of the named pad. Exactly one tap point per net.
NET_TAP_EXCEPTIONS = {'F0_SCL': ('J6', '5'), 'F4_SDA': ('J1', '6'), 'Deploy2_EN': ('U6', '6')}
TAP_RADIUS_MM = 2.5


ALLOWED_PADS = [
    # J14 pins 10/12 (BATT_SDA/BATT_SCL) sit 18.5 mm from the nearest Rev2 edge: PM exception 2026-09-20 (panel PLR-02),
    # 22 mm → 24 mm (routing attempt 2, precedent J7/J10/J20), conditional on a hand-traced path. Listed first so it wins.
    (re.compile(r'^J14$'), {'10', '12'}, 24.0),
    # PM 2026-09-20 (closure attempt 1, brief §12 F13): J1 pin 6 (F4_SDA) — the direct exit is closed by the heritage
    # FIRE_DEPLOY1_A diagonal, the measured minimum path is 17.9 mm → 20 mm; U6 pin 6 (Deploy2_EN) — the F12 tap opens
    # only a pocket bounded by the bottom-edge F.Cu wall, the way out is the x 178.7–182 corridor → 24 mm.
    (re.compile(r'^J1$'), {'6'}, 20.0),
    (re.compile(r'^U6$'), {'6'}, 24.0),
    (re.compile(r'^J(1|2|6|9|11|13|8|29|30|15|14|16|19)$'), None, 14.0),
    (re.compile(r'^J(7|10|20)$'), None, 24.0),
    (re.compile(r'^U6$'), {'3', '4', '5', '6'}, 14.0),
    (re.compile(r'^R104$'), {'1'}, 14.0),
    (re.compile(r'^R100$'), {'1'}, 14.0),
]


def mm(v):
    return pcbnew.ToMM(v)


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


def dist_point_seg(p, a, b):
    ax, ay = a
    bx, by = b
    px, py = p
    dx, dy = bx - ax, by - ay
    if dx == dy == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def dist_to_boundary(p, poly):
    return min(dist_point_seg(p, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))


def fill_area_inside(zone, poly):
    """mm² of the zone's filled copper (all its layers) that lies inside the polygon (list of (x, y) mm)."""
    clip = pcbnew.SHAPE_POLY_SET()
    clip.NewOutline()
    for x, y in poly:
        clip.Append(pcbnew.VECTOR2I_MM(x, y))
    clip.Inflate(-pcbnew.FromMM(1.0), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))  # same 1 mm band as heritage.py
    total = 0.0
    for layer in zone.GetLayerSet().Seq():
        fp = pcbnew.SHAPE_POLY_SET(zone.GetFilledPolysList(layer))
        fp.BooleanIntersection(clip)
        total += fp.Area() / 1e12
    return total


def trim_dangling(board, snap, keep):
    """After a prune, remove NEW tracks/vias that were left dangling: a track with an end that touches no
    other track end (same layer), no via and no pad; a via that tracks reach on fewer than two layers and
    that sits on no pad. Repeats until stable. Removed wrappers are appended to `keep` (must stay alive)."""
    her = set(snap['tracks'])
    pads = [(pad, pad.GetBoundingBox()) for fp in board.GetFootprints() for pad in fp.Pads()]

    def key(p):
        return (round(mm(p.x), 3), round(mm(p.y), 3))

    def on_pad(p, layer):
        for pad, bb in pads:
            if bb.Contains(p) and (layer is None or pad.IsOnLayer(layer)) and pad.HitTest(p):
                return True
        return False

    removed = 0
    while True:
        tracks = [t for t in board.GetTracks() if t.GetClass() != 'PCB_VIA']
        vias = [t for t in board.GetTracks() if t.GetClass() == 'PCB_VIA']
        ends = defaultdict(int)          # (pt, layer) -> number of track ends there
        via_at = {key(v.GetPosition()) for v in vias}
        via_layers = defaultdict(set)    # via pos -> layers on which a track ends there
        for t in tracks:
            for p in (t.GetStart(), t.GetEnd()):
                k = key(p)
                ends[(k, t.GetLayer())] += 1
                if k in via_at:
                    via_layers[k].add(t.GetLayer())
        drop = []
        for t in tracks:
            if t.m_Uuid.AsString() in her:
                continue
            for p in (t.GetStart(), t.GetEnd()):
                k = key(p)
                if ends[(k, t.GetLayer())] >= 2 or k in via_at or on_pad(p, t.GetLayer()):
                    continue
                drop.append(t)
                break
        for v in vias:
            if v.m_Uuid.AsString() in her:
                continue
            k = key(v.GetPosition())
            if len(via_layers[k]) >= 2 or on_pad(v.GetPosition(), None):
                continue
            drop.append(v)
        if not drop:
            return removed
        for t in drop:
            board.Remove(t)
            keep.append(t)
        removed += len(drop)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('snap')
    ap.add_argument('board')
    ap.add_argument('--band', type=float, default=14.0, help='default depth allowance from the Rev2 edge (per-pad limits in ALLOWED_PADS override)')
    ap.add_argument('--max-stub', type=float, default=14.0)
    ap.add_argument('--json')
    ap.add_argument('--prune', metavar='OUT.kicad_pcb', help='remove every NEW track/via that violates the rule (never heritage items) and save the board here; the affected connections must then be routed again from the stub ends')
    a = ap.parse_args()
    snap = json.load(open(a.snap))
    poly = snap.get('rev2_outline')
    if not poly:
        print('snapshot has no rev2_outline; re-run heritage.py snapshot on the Rev2-shaped board')
        return 2
    poly = [tuple(p) for p in poly]
    board = pcbnew.LoadBoard(a.board)
    old_tracks = set(snap['tracks'].keys())
    old_endpoints = set()
    for t in snap['tracks'].values():
        old_endpoints.add((round(t['start'][0], 2), round(t['start'][1], 2)))
        old_endpoints.add((round(t['end'][0], 2), round(t['end'][1], 2)))

    # allowed pads (heritage footprints only)
    pads = []
    limit_of = {}
    for f in board.GetFootprints():
        ref = f.GetReference()
        for rx, nums, lim in ALLOWED_PADS:
            if rx.match(ref) and f.m_Uuid.AsString() in snap['footprints']:
                for pd in f.Pads():
                    if nums is None or pd.GetNumber() in nums:
                        if (ref, pd.GetNumber()) not in limit_of:
                            pads.append((ref, pd))
                        limit_of.setdefault((ref, pd.GetNumber()), lim)   # first matching row wins (the J14 pins 10/12 exception precedes the J14 row)
    violations, warnings = [], []
    to_prune = []
    new = [t for t in board.GetTracks() if t.m_Uuid.AsString() not in old_tracks]
    inside_items = []
    inside_vias = []   # vias inside the Rev2 outline: allowed only as the single layer change of a bottom-side-connector stub (see VIA_ALLOWED_PADS)
    for t in new:
        s, e = t.GetStart(), t.GetEnd()
        ps, pe = (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))
        if t.GetClass() == 'PCB_VIA':
            if point_in_poly(ps, poly):
                inside_vias.append((t, ps))
            continue
        ins = point_in_poly(ps, poly) or point_in_poly(pe, poly)
        if not ins:
            # a segment can also cross the section with both ends outside; sample midpoints
            for k in (0.25, 0.5, 0.75):
                q = (ps[0] + (pe[0] - ps[0]) * k, ps[1] + (pe[1] - ps[1]) * k)
                if point_in_poly(q, poly):
                    ins = True
                    break
        if ins:
            inside_items.append((t, ps, pe))
    # group inside tracks into chains by shared endpoints
    key = lambda p: (round(p[0], 2), round(p[1], 2))
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x

    def union(x, y):
        parent[find(x)] = find(y)

    for i, (t, ps, pe) in enumerate(inside_items):
        parent.setdefault(i, i)
    pt_owner = {}
    for i, (t, ps, pe) in enumerate(inside_items):
        for p in (key(ps), key(pe)):
            if p in pt_owner:
                union(i, pt_owner[p])
            else:
                pt_owner[p] = i
    chains = defaultdict(list)
    for i in range(len(inside_items)):
        chains[find(i)].append(inside_items[i])
    def inside_length(ps, pe, n=64):
        """length of the part of segment ps-pe that lies inside the Rev2 outline (sampled)"""
        total = math.hypot(pe[0] - ps[0], pe[1] - ps[1])
        if total == 0:
            return 0.0
        k = sum(1 for i in range(n) if point_in_poly((ps[0] + (pe[0] - ps[0]) * (i + 0.5) / n, ps[1] + (pe[1] - ps[1]) * (i + 0.5) / n), poly))
        return total * k / n

    per_net = defaultdict(int)
    stubs = []
    chain_pts = {cid: {key(p) for t, ps, pe in items for p in (ps, pe)} for cid, items in chains.items()}
    via_owner = {}   # via index -> chain id (a via belongs to the chain whose endpoint it sits on)
    for vi, (v, pv) in enumerate(inside_vias):
        for cid, pts in chain_pts.items():
            if key(pv) in pts:
                via_owner[vi] = cid
                break
    for vi, (v, pv) in enumerate(inside_vias):
        if vi not in via_owner:
            violations.append(f'via {v.GetNetname()} at ({pv[0]:.2f},{pv[1]:.2f}) inside the flight section (not part of any stub)')
            to_prune.append(v)
    for cid, items in chains.items():
        net = items[0][0].GetNetname()
        length = sum(inside_length(ps, pe) for t, ps, pe in items)
        endpoints = [p for t, ps, pe in items for p in (ps, pe)]
        touched = set()
        pad_points = set()
        for t, ps, pe in items:
            for ref, pd in pads:
                if not pd.IsOnLayer(t.GetLayer()):
                    continue  # a pad on the other side is not touched by this segment
                for p in (ps, pe):
                    if point_in_poly(p, poly) and pd.HitTest(pcbnew.VECTOR2I_MM(p[0], p[1]), 0):
                        touched.add((ref, pd.GetNumber(), pd.GetNetname()))
                        pad_points.add(key(p))
        # F12 trace-tap exception: a stub of one of the three walled nets may end on its own net's heritage track/via (detected before the via rules so a tap stub can also use an F14 via allowance, e.g. Deploy2_EN at U6.6)
        tap = None
        if net in NET_TAP_EXCEPTIONS and not touched:
            tref, tnum = NET_TAP_EXCEPTIONS[net]
            tfp = board.FindFootprintByReference(tref)
            tpad = next((pd for pd in tfp.Pads() if pd.GetNumber() == tnum), None) if tfp else None
            if tpad is not None:
                pc = (mm(tpad.GetPosition().x), mm(tpad.GetPosition().y))
                for p in endpoints:
                    if math.hypot(p[0] - pc[0], p[1] - pc[1]) > TAP_RADIUS_MM:
                        continue
                    for u, ht in snap['tracks'].items():
                        if ht['net'].split('/')[-1] != net:
                            continue
                        if ht['type'] == 'PCB_VIA':
                            if math.hypot(p[0] - ht['start'][0], p[1] - ht['start'][1]) <= ht['width'] / 2 + 0.01:
                                tap = (p, 'via', u)
                        elif dist_point_seg(p, tuple(ht['start']), tuple(ht['end'])) <= ht['width'] / 2 + 0.01:
                            tap = (p, ht['layer'], u)
                        if tap:
                            break
                    if tap:
                        break
            if tap:
                touched.add((tref, tnum, net))          # counts as the attachment for limits/reporting
                pad_points.add(key(tap[0]))             # and its endpoint may coincide with heritage geometry
        bad = []
        chain_vias = [(v, pv) for vi, (v, pv) in enumerate(inside_vias) if via_owner.get(vi) == cid]
        via_ok = False
        if chain_vias:
            via_pads = [tp for tp in touched if via_allowed(tp[0], tp[1])]
            if not via_pads:
                bad.append(f'{len(chain_vias)} via(s) inside the flight section on a stub that does not start at a via-allowed pad (J2/J9/J13 any pin, J16.1, J14.10/12, U6.6)')
            elif len(chain_vias) > 1:
                bad.append(f'{len(chain_vias)} vias inside the flight section (rule: at most one layer change per bottom-side stub)')
            else:
                v, pv = chain_vias[0]
                via_lim = max(limit_of.get((ref, num), a.max_stub) for ref, num, pnet in via_pads)
                if dist_to_boundary(pv, poly) > min(VIA_BAND_MM, via_lim) + 1e-6:
                    bad.append(f'stub via at ({pv[0]:.2f},{pv[1]:.2f}) is {dist_to_boundary(pv, poly):.1f} mm deep (> {min(VIA_BAND_MM, via_lim):.0f} mm allowed for these pads)')
                elif key(pv) in old_endpoints:
                    bad.append(f'stub via at ({pv[0]:.2f},{pv[1]:.2f}) sits on a heritage track/via endpoint')
                else:
                    via_ok = True
            if bad:
                to_prune.extend(v for v, pv in chain_vias)
        if not touched:
            bad.append('touches no allowed pad')
        wrong_net = [tp for tp in touched if tp[2] != net]
        if wrong_net:
            bad.append(f'touches pads of another net {wrong_net}')
        lim = max([limit_of.get((ref, num), a.max_stub) for ref, num, pnet in touched] or [a.max_stub])
        band = max(a.band, lim)
        far = [p for p in endpoints if point_in_poly(p, poly) and dist_to_boundary(p, poly) > band + 1e-6]
        if far:
            bad.append(f'{len(far)} endpoint(s) deeper than the {band:.0f} mm band')
        if length > lim + 1e-6:
            bad.append(f'inside length {length:.1f} mm > {lim:.0f} mm allowed for these pads')
        # a stub may share the pad point with the heritage track that ends on the same pad; any other coincidence is a tap
        touching_old = [p for p in endpoints if key(p) in old_endpoints and key(p) not in pad_points]
        if touching_old:
            bad.append(f'touches heritage track/via endpoint(s) off-pad at {touching_old[:3]}')
        layers = {board.GetLayerName(t.GetLayer()) for t, ps, pe in items}
        if tap is not None and not via_ok:
            # without a layer change the stub must stay on the tapped item's layer (a tapped via accepts either outer layer); with an allowed via the else-branch rule applies
            ok_layers = {'F.Cu', 'B.Cu'} if tap[1] == 'via' else {tap[1]}
            off = sorted({board.GetLayerName(t.GetLayer()) for t, ps, pe in items} - ok_layers)
            if off:
                bad.append(f'tap stub segment(s) on {off} but the tapped heritage item is on {tap[1]}')
        elif not via_ok:
            for ref, num, pnet in touched:
                pd = next((pd for r, pd in pads if r == ref and pd.GetNumber() == num), None)
                if pd is None:
                    continue
                off = [board.GetLayerName(t.GetLayer()) for t, ps, pe in items if not pd.IsOnLayer(t.GetLayer())]
                if off:
                    bad.append(f'stub segment(s) on {sorted(set(off))} but pad {ref}.{num} has no copper there')
        else:
            # one layer change allowed: only F.Cu / B.Cu segments (no inner-layer stubs)
            inner = [l for l in layers if l not in ('F.Cu', 'B.Cu')]
            if inner:
                bad.append(f'stub segment(s) on inner layer(s) {sorted(inner)}')
        desc = f"stub net {net}: {len(items)} seg, {length:.1f} mm inside, pads {sorted(touched)}, layers {sorted(layers)}" + (f", via at ({chain_vias[0][1][0]:.2f},{chain_vias[0][1][1]:.2f})" if chain_vias else '') + (f", TAP on heritage {tap[1]} at ({tap[0][0]:.2f},{tap[0][1]:.2f}) (F12)" if tap else '')
        stubs.append(desc)
        if bad:
            violations.append(desc + ' -> ' + '; '.join(bad))
            to_prune.extend(t for t, ps, pe in items)
        else:
            per_net[net] += 1
    for net, n in per_net.items():
        if n > 1:
            warnings.append(f'net {net} has {n} stubs into the flight section (rule: one)')
    # heritage zone fills inside the flight section must be unchanged (heritage.py check reports the same)
    for u, z in snap['zones'].items():
        if z.get('fill_in_rev2') is None:
            continue
        zz = next((x for x in board.Zones() if x.m_Uuid.AsString() == u), None)
        if zz is None:
            continue
        now = fill_area_inside(zz, poly)
        if z['fill_in_rev2'] and abs(now - z['fill_in_rev2']) / z['fill_in_rev2'] > 0.001:
            violations.append(f"zone {z['net']} on {z['layer']}: copper inside the flight section changed {z['fill_in_rev2']:.1f} -> {now:.1f} mm²")
    for s in stubs:
        print('STUB:', s)
    for w in warnings:
        print('WARNING:', w)
    for v in violations:
        print('VIOLATION:', v)
    print(f'attachment check: {len(new)} new tracks/vias, {len(chains)} stub chain(s) into the flight section, {len(violations)} violation(s), {len(warnings)} warning(s)')
    if a.prune and to_prune:
        keep = []
        nets = set()
        for t in to_prune:
            nets.add(t.GetNetname())
            board.Remove(t)
            keep.append(t)  # keep the wrappers alive (see heritage.py / outline.py notes)
        trimmed = trim_dangling(board, snap, keep)
        pcbnew.SaveBoard(a.prune, board)
        print(f'pruned {len(to_prune)} new track(s)/via(s) on nets {sorted(nets)} + {trimmed} dangling new track(s)/via(s) left behind -> saved {a.prune}; route those connections again from the stub ends')
    elif a.prune:
        pcbnew.SaveBoard(a.prune, board)
        print('nothing to prune; saved', a.prune)
    if a.json:
        json.dump({'violations': violations, 'warnings': warnings, 'stubs': len(chains), 'new_items': len(new)}, open(a.json, 'w'), indent=1)
    return 1 if violations else 0


if __name__ == '__main__':
    sys.exit(main())
