#!/usr/bin/env python3
"""Re-place new (non-heritage) parts and rip up / reroute their nets from a JSON batch spec, with exact checks.
Run with KiCad's bundled python3 with numpy on PYTHONPATH (micro.py needs it too, e.g.
`python3 -m pip install --target DIR 'numpy<2.1'`); the board must sit next to its .kicad_pro/.kicad_dru.

  reroute.py BOARD OUT SPEC.json [--snap heritage_rev2.json] [--project PRO] [--area X0,Y0,X1,Y1]
             [--pad-gap 0.10] [--save-failed PATH] [--reorder 6]

SPEC is {"ops": [...]}; ops run in order on one in-memory board:
  {"op": "move", "ref": "C209", "x": 269.0, "y": 99.6, "rot": 0}      heritage footprints are refused
  {"op": "ripup", "nets": [...], "window": [x0,y0,x1,y1], "layers": ["F.Cu", ...]}
        removes the nets' new copper inside the window; a segment crossing the window edge is clipped and its
        outside part kept (heritage copper is never touched)
  {"op": "ripup_at", "net": N, "at": [x,y], "r": 0.3}                 removes new items of N within r of a point
  {"op": "track", "net": N, "layer": "F.Cu", "w": 0.3, "pts": [[x,y], ...]}   exact-checked or the batch fails
  {"op": "via", "net": N, "at": [x,y], "dia": 0.46, "drill": 0.2}       exact-checked, never on/near an SMD pad
  {"op": "route", "nets": [...], "widths": [...], "pad": 4, "layers": ["F.Cu","In2.Cu","B.Cu"],
        "step": 0.025, "via_cost": 1.2, "rounds": 12}
        multi-layer raster Dijkstra between the nearest two clusters (closure/micro.py's search and emit, so
        every item passes fan2's exact KiCad-polygon clearance), repeated until the net is one piece; vias
        are kept --pad-gap off every SMD pad by construction and by an exact re-check
  {"op": "stitch", "pad": "Y200.4", "max_r": 2.0}   drops a via into the pad, then dogbones it off (dogbone.py)
  {"op": "dogbone", "pad": "C209.1", "max_r": 2.5, "push": 0}         moves the via sitting in that pad off it
  {"op": "prune", "nets": [...]}    removes copper KiCad's own TestTrackEndpointDangling calls dangling: a
        one-layer via goes (tracks ending on its ring are first bridged to its centre), a track with one free
        end is cut back to its nearest interior connection or removed
A route failure re-executes the whole batch with the failing net first in that op (--reorder times). After
the ops every zone is refilled, all touched nets are pruned and any net that split is routed again. Then: every net the batch touched must be in no more pieces than before (pour nets judged on a
refill), no new via may sit on or within --pad-gap of an SMD pad, moved parts' pads must clear all foreign
copper and their courtyards must not overlap any other courtyard on their side, and no heritage item may
change. Any failure prints the reasons and exits 1 without writing OUT (--save-failed writes it elsewhere
for inspection). Gates (tools/pcb/gates.sh) stay the acceptance test.
"""
import argparse
import json
import math
import os
import sys

import numpy as np
import pcbnew

sys.path.insert(0, os.environ.get('CLOSURE_DIR', os.path.dirname(os.path.abspath(__file__))))
import clusters  # noqa: E402
import dogbone  # noqa: E402
import fan2  # noqa: E402
import micro  # noqa: E402
import mlroute  # noqa: E402
import rgeo  # noqa: E402

MM, TOMM = pcbnew.FromMM, pcbnew.ToMM


def uid(it):
    return it.m_Uuid.AsString()


def P(v):
    return (TOMM(v.x), TOMM(v.y))


def bbox(it):
    b = it.GetBoundingBox()
    return (TOMM(b.GetLeft()), TOMM(b.GetTop()), TOMM(b.GetRight()), TOMM(b.GetBottom()))


def meets(bb, w):
    return not (bb[2] < w[0] or bb[0] > w[2] or bb[3] < w[1] or bb[1] > w[3])


class MemBoard(rgeo.Board):
    """rgeo.Board over an in-memory pcbnew board (rgeo.Board itself loads from a path)."""

    def __init__(self, board, snap):
        self.b = board
        self.snap = snap
        self.cu = rgeo.copper_layers(board)
        self.fcu, self.bcu = pcbnew.F_Cu, pcbnew.B_Cu
        self.her_fp = set(snap['footprints'].keys())
        self.her_tr = set(snap['tracks'].keys())
        self.rev2 = [tuple(p) for p in snap['rev2_outline']]
        self._index()


class Fail(Exception):
    pass


class RouteFail(Fail):
    def __init__(self, msg, op, net):
        super().__init__(msg)
        self.op, self.net = op, net


class Session:
    def __init__(self, path, project, snap_path, area, pad_gap):
        self.board = pcbnew.LoadBoard(path)
        self.snap = json.load(open(snap_path))
        self.her_fp = set(self.snap['footprints'])
        self.her_tr = set(self.snap['tracks'])
        self.cls = fan2.load_cls(project, self.board)
        mlroute.load_netclasses(project, self.board)
        fan2.AREA = dogbone.AREA = micro.DEFAULT_AREA = tuple(area)
        self.area = tuple(area)
        self.gap = pad_gap
        self.base = {}
        self.moved = []
        self.her_geom = self.heritage_geometry()
        self.grave = []
        self.vip0 = self.vias_on_pads()
        self.via0 = {uid(v) for v in self.vias()}

    # ---------------------------------------------------------------- facts
    def vias(self):
        return [t for t in self.board.GetTracks() if t.Type() == pcbnew.PCB_VIA_T]

    def net(self, name):
        for n in self.board.GetNetsByName().keys():
            if str(n) == name or str(n).rsplit('/', 1)[-1] == name:
                return str(n)
        raise Fail(f'no net {name}')

    def pad(self, spec):
        ref, num = spec.split('.')
        fp = self.board.FindFootprintByReference(ref)
        if fp is None:
            raise Fail(f'no footprint {ref}')
        pads = [p for p in fp.Pads() if p.GetNumber() == num]
        if not pads:
            raise Fail(f'no pad {spec}')
        return pads[0]

    def heritage_geometry(self):
        g = {}
        for t in self.board.GetTracks():
            if uid(t) in self.her_tr:
                g[uid(t)] = (t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y)
        for fp in self.board.GetFootprints():
            if uid(fp) in self.her_fp:
                g[uid(fp)] = (fp.GetPosition().x, fp.GetPosition().y, fp.GetOrientationDegrees())
        return g

    def pieces(self, net):
        return dogbone.pieces(self.board, net)

    def touch(self, net):
        if net and net not in self.base:
            self.base[net] = self.pieces(net)

    def vias_on_pads(self):
        smd = self.smd_polys()
        out = {}
        for v in self.vias():
            if uid(v) in self.her_tr:
                continue
            hit = self.via_clear_of_pads(P(v.GetPosition()), TOMM(v.GetWidth(pcbnew.F_Cu)) / 2 - self.gap, smd)
            if hit:
                out[uid(v)] = f'{hit.GetParentFootprint().GetReference()}.{hit.GetNumber()}'
        return out

    def smd_polys(self):
        out = []
        for fp in self.board.GetFootprints():
            for p in fp.Pads():
                if p.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                    continue
                l = pcbnew.F_Cu if p.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
                out.append((p, p.GetEffectivePolygon(l, pcbnew.ERROR_INSIDE)))
        return out

    # ---------------------------------------------------------------- ops
    def op_move(self, o):
        fp = self.board.FindFootprintByReference(o['ref'])
        if fp is None or uid(fp) in self.her_fp:
            raise Fail(f"move {o['ref']}: missing or heritage")
        for p in fp.Pads():
            self.touch(p.GetNetname())
        fp.SetPosition(pcbnew.VECTOR2I_MM(float(o['x']), float(o['y'])))
        fp.SetOrientationDegrees(float(o.get('rot', fp.GetOrientationDegrees())))
        self.moved.append(fp)
        print(f"move {o['ref']} -> ({o['x']},{o['y']}) r{fp.GetOrientationDegrees():.0f}")

    def remove(self, t):
        # pcbnew hands ownership of a removed item back to Python; if it is collected, SWIG's type table
        # is corrupted (later board.Zones() yields bare SwigPyObjects). Keep every removed item alive.
        self.board.Remove(t)
        self.grave.append(t)

    def removable(self, t):
        return uid(t) not in self.her_tr

    def op_ripup(self, o):
        nets = [self.net(n) for n in o['nets']]
        lays = {self.board.GetLayerID(l) for l in o.get('layers', [])}
        n = 0
        for net in nets:
            self.touch(net)
            for t in list(self.board.GetTracks()):
                if t.GetNetname() != net or not self.removable(t) or not meets(bbox(t), o['window']):
                    continue
                if lays and t.Type() != pcbnew.PCB_VIA_T and t.GetLayer() not in lays:
                    continue
                if t.Type() != pcbnew.PCB_VIA_T:
                    for a, b in self.outside_parts(P(t.GetStart()), P(t.GetEnd()), o['window']):
                        self.board.Add(fan2.mk_track(self.board, a, b, TOMM(t.GetWidth()), t.GetLayer(),
                                                     t.GetNet()))
                self.remove(t)
                n += 1
        print(f"ripup {','.join(x.rsplit('/', 1)[-1] for x in nets)} in {o['window']}: {n} items")

    @staticmethod
    def outside_parts(a, b, w):
        """The pieces of segment a-b outside the window (Liang-Barsky clip), as point pairs."""
        dx, dy = b[0] - a[0], b[1] - a[1]
        t0, t1 = 0.0, 1.0
        for p_, q_ in ((-dx, a[0] - w[0]), (dx, w[2] - a[0]), (-dy, a[1] - w[1]), (dy, w[3] - a[1])):
            if abs(p_) < 1e-12:
                if q_ < 0:
                    return [(a, b)]
                continue
            r = q_ / p_
            if p_ < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
        if t0 > t1:
            return [(a, b)]
        out = []
        pa = (a[0] + dx * t0, a[1] + dy * t0)
        pb = (a[0] + dx * t1, a[1] + dy * t1)
        if t0 > 1e-6 and math.dist(a, pa) > 0.01:
            out.append((a, pa))
        if t1 < 1 - 1e-6 and math.dist(pb, b) > 0.01:
            out.append((pb, b))
        return out

    def op_ripup_at(self, o):
        net = self.net(o['net'])
        self.touch(net)
        c, r = o['at'], o.get('r', 0.3)
        n = 0
        for t in list(self.board.GetTracks()):
            if t.GetNetname() != net or not self.removable(t):
                continue
            if t.Type() == pcbnew.PCB_VIA_T:
                hit = math.dist(P(t.GetPosition()), c) <= r
            else:
                hit = any(math.dist(P(e), c) <= r for e in (t.GetStart(), t.GetEnd()))
            if hit:
                self.remove(t)
                n += 1
        print(f"ripup_at {net.rsplit('/', 1)[-1]} {c}: {n} items")

    def obs(self):
        return fan2.Obs(self.board, self.cls)

    def op_track(self, o):
        net = self.net(o['net'])
        self.touch(net)
        lay = self.board.GetLayerID(o['layer'])
        obs = self.obs()
        for a, b in zip(o['pts'], o['pts'][1:]):
            t = fan2.seg_ok(self.board, obs, tuple(a), tuple(b), o['w'], lay, net)
            if t is None:
                raise Fail(f"track {net} {a}->{b} on {o['layer']}: " + str(dogbone.seg_reason(
                    self.board, obs, tuple(a), tuple(b), o['w'], lay, net)))
            self.board.Add(t)
            obs.add(t)
        print(f"track {net.rsplit('/', 1)[-1]} {o['layer']} {len(o['pts']) - 1} seg")

    def via_clear_of_pads(self, p, r, smd=None):
        for pd, poly in (smd or self.smd_polys()):
            if poly.Collide(pcbnew.VECTOR2I_MM(p[0], p[1]), MM(r + self.gap)):
                return pd
        return None

    def op_via(self, o):
        net = self.net(o['net'])
        self.touch(net)
        dia, drill = o.get('dia', 0.46), o.get('drill', 0.2)
        p = tuple(o['at'])
        hit = self.via_clear_of_pads(p, dia / 2)
        if hit:
            raise Fail(f"via {net} {p}: on/near pad {hit.GetParentFootprint().GetReference()}.{hit.GetNumber()}")
        v = fan2.mk_via(self.board, p, self.board.FindNet(net), dia, drill)
        obs = self.obs()
        bb = fan2.bb_of(v)
        for l in fan2.cu_layers(self.board):
            hit = fan2.collides(obs, v, l, net, bb, fan2.in_area(bb))
            if hit or not fan2.edge_ok(obs, v, l):
                raise Fail(f"via {net} {p}: clearance {hit[0] if hit else 'edge'}")
        if not fan2.hole_ok(obs, v, fan2.cu_layers(self.board), net, pos=p, drill=drill):
            raise Fail(f'via {net} {p}: hole clearance')
        self.board.Add(v)
        print(f"via {net.rsplit('/', 1)[-1]} {p} {dia}/{drill}")

    def nearest_pair(self, cl):
        best = None
        for i in range(len(cl)):
            for j in range(i + 1, len(cl)):
                for a in [p for it in cl[i] for p in micro.item_pts(it)]:
                    for b in [p for it in cl[j] for p in micro.item_pts(it)]:
                        d = math.hypot(a[0] - b[0], a[1] - b[1])
                        if best is None or d < best[0]:
                            best = (d, i, j, a, b)
        return best

    def clusters_of(self, net):
        dogbone.refill_net(self.board, net)
        return clusters.build(self.board).get(self.board.FindNet(net).GetNetCode(), [])

    def route_once(self, net, cl, o):
        d, i, j, pa, pb = self.nearest_pair(cl)
        pad = o.get('pad', 4.0)
        x0, x1 = min(pa[0], pb[0]) - pad, max(pa[0], pb[0]) + pad
        y0, y1 = min(pa[1], pb[1]) - pad, max(pa[1], pb[1]) + pad
        st = o.get('step', 0.025)
        while ((x1 - x0) / st) * ((y1 - y0) / st) > 6000000:
            st *= 1.25
        bd = MemBoard(self.board, self.snap)
        g = rgeo.Grid(bd, x0, y0, x1, y1, st)
        area, inset = self.area, o.get('inset', 0.6)
        inner = ((g.xx >= area[0] + inset) & (g.xx <= area[2] - inset))[None, :] & \
                ((g.yy >= area[1] + inset) & (g.yy <= area[3] - inset))[:, None]
        layers = [self.board.GetLayerID(l) for l in o.get('layers', ['F.Cu', 'In2.Cu', 'B.Cu'])]
        # vias: never within pad-gap of an SMD pad (any net); 0.46 outside the relaxed area
        nopad = np.zeros((g.H, g.W), dtype=bool)
        for pd, poly in self.smd_polys():
            bb = bbox(pd)
            if not meets(bb, (x0 - 1, y0 - 1, x1 + 1, y1 + 1)):
                continue
            ps = pcbnew.SHAPE_POLY_SET(poly)
            ps.Inflate(MM(0.23 + self.gap + 0.03), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.005))
            for pts in rgeo.polyset_pts(ps):
                rgeo.fill_poly(nopad, pts, g.x0, g.y0, g.step)
        cm = None
        if o.get('prefer'):
            pref = {self.board.GetLayerID(l): f for l, f in o['prefer'].items()}
            cm = [np.full((g.H, g.W), pref.get(L, 1.0)) for L in layers]
        for w in o.get('widths', [0.25, 0.2, 0.152, 0.127]):
            hw = w / 2.0
            frees = []
            for L in layers:
                b20 = g.obstacles(L, net, hw, 0.205, None, 0.2, net_clear=lambda n: mlroute.net_clear(n) - 0.035)
                b12 = g.obstacles(L, net, hw, 0.131, None, 0.2)
                frees.append((~b20) | (inner & (~b12)))
            vb20 = np.zeros((g.H, g.W), dtype=bool)
            vb12 = np.zeros((g.H, g.W), dtype=bool)
            for L in rgeo.copper_layers(self.board):
                vb20 |= g.obstacles(L, net, 0.23, 0.205, None, 0.2, net_clear=lambda n: mlroute.net_clear(n) - 0.035)
                vb12 |= g.obstacles(L, net, 0.20, 0.131, None, 0.2)
            vm = (((~vb20) | (inner & (~vb12))) & ~g.hole_mask(net, 0.1, extra=0.0) & ~g.inside_rev2 & ~nopad)
            starts = []
            for li, L in enumerate(layers):
                m = micro.mask_of(g, cl[i], L, hw, frees[li])
                for jj, ii in zip(*np.where(m)):
                    starts.append((li, int(jj), int(ii)))
            goals = [micro.mask_of(g, cl[j], L, hw, frees[li]) for li, L in enumerate(layers)]
            if not starts or not any(m.any() for m in goals):
                continue
            chain = mlroute.dijkstra_ml(frees, vm, starts, goals, st, via_cost=o.get('via_cost', 1.2), cost_mult=cm)
            if chain is None:
                continue
            got = (chain, w, g, frees, layers)
            for simp in (True, False):
                before = {uid(t) for t in self.board.GetTracks()}
                if not micro.emit(self.board, self.cls, net, net.rsplit('/', 1)[-1], got, d, simp=simp):
                    continue
                new = [t for t in self.board.GetTracks() if uid(t) not in before]
                smd = self.smd_polys()
                bad = [v for v in new if v.Type() == pcbnew.PCB_VIA_T
                       and self.via_clear_of_pads(P(v.GetPosition()), TOMM(v.GetWidth(pcbnew.F_Cu)) / 2, smd)]
                if bad:
                    for t in new:
                        self.remove(t)
                    print('    via near a pad, rejected')
                    continue
                return True
        return False

    def op_route(self, o):
        for name in o['nets']:
            net = self.net(name)
            self.touch(net)
            pruned = o.get('noprune', False)
            for _ in range(o.get('rounds', 12)):
                cl = self.clusters_of(net)
                print(f'    {name}: {len(cl)} pieces', flush=True)
                if len(cl) < 2:
                    if pruned:
                        break
                    self.prune([net])
                    pruned = True
                    continue
                if not self.route_once(net, cl, o):
                    d, i, j, pa, pb = self.nearest_pair(cl)
                    msg = f'route {name}: no path ({pa[0]:.2f},{pa[1]:.2f})->({pb[0]:.2f},{pb[1]:.2f}) gap {d:.2f}'
                    if o.get('optional'):
                        print('  ' + msg + ' (optional, left open)')
                        break
                    raise RouteFail(msg, o, name)
                pruned = o.get('noprune', False)

    def via_in(self, pad):
        poly = pad.GetEffectivePolygon(pcbnew.F_Cu if pad.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu,
                                       pcbnew.ERROR_INSIDE)
        for v in self.vias():
            if poly.Collide(v.GetPosition(), v.GetWidth(pcbnew.F_Cu) // 2) and v.GetNetname() == pad.GetNetname():
                return v
        return None

    def op_dogbone(self, o):
        pad = self.pad(o['pad'])
        v = self.via_in(pad)
        if v is None:
            print(f"dogbone {o['pad']}: no via in pad")
            return
        self.touch(v.GetNetname())
        her = self.her_tr
        rec, undo = dogbone.move_one(self.board, self.cls, dogbone.outer_pads(self.board), her, v,
                                     o.get('max_r', 2.5), o.get('step', 0.025), o.get('max_tries', 3000),
                                     self.gap, o.get('small', True), o.get('push', 0))
        rec.pop('_plan', None)
        if rec['status'] != 'MOVED':
            raise Fail(f"dogbone {o['pad']}: {rec.get('reasons')}")
        print(f"dogbone {o['pad']} -> {rec['new']} {rec['new_via']} +{rec['added_mm']} mm")

    def op_stitch(self, o):
        pad = self.pad(o['pad'])
        net = pad.GetNetname()
        self.touch(net)
        c = P(pad.GetPosition())
        v = fan2.mk_via(self.board, c, self.board.FindNet(net), o.get('dia', 0.46), 0.2)
        self.board.Add(v)
        rec, undo = dogbone.move_one(self.board, self.cls, dogbone.outer_pads(self.board), self.her_tr, v,
                                     o.get('max_r', 2.0), o.get('step', 0.025), o.get('max_tries', 3000),
                                     self.gap, o.get('small', True), o.get('push', 0))
        rec.pop('_plan', None)
        if rec['status'] != 'MOVED':
            self.remove(v)
            raise Fail(f"stitch {o['pad']}: {rec.get('reasons')}")
        print(f"stitch {o['pad']} -> via {rec['new']} {rec['new_via']}")

    def prune(self, nets):
        """Remove new-copper dangling ends of `nets` as KiCad's DRC sees them (its own
        TestTrackEndpointDangling): a dangling via goes, a track with one dangling end is cut back to the
        connection on its interior nearest that end, or removed. Repeats until nothing changes."""
        nets = set(nets)
        removed = 0
        if len(nets) < 20:
            for net in nets:
                dogbone.refill_net(self.board, net)
        seen = set()
        for _ in range(2000):
            self.board.BuildConnectivity()
            conn = self.board.GetConnectivity()
            items = [t for t in self.board.GetTracks() if t.GetNetname() in nets]
            changed = False
            for t in items:
                if not self.removable(t):
                    continue
                pos = pcbnew.VECTOR2I(0, 0)
                if not conn.TestTrackEndpointDangling(t, False, pos):
                    continue
                if t.Type() == pcbnew.PCB_VIA_T:
                    # a via on one layer can still join tracks that end on its ring: bridge them to its
                    # centre (inside the old via copper, so no clearance changes) before removing it
                    c = t.GetPosition()
                    r = t.GetWidth(pcbnew.F_Cu) // 2
                    for o in items:
                        if o.Type() == pcbnew.PCB_VIA_T:
                            continue
                        for e in (o.GetStart(), o.GetEnd()):
                            d = math.dist((e.x, e.y), (c.x, c.y))
                            if 1000 < d <= r + o.GetWidth() // 2:
                                self.board.Add(fan2.mk_track(self.board, P(e), P(c), TOMM(o.GetWidth()),
                                                             o.GetLayer(), o.GetNet()))
                    self.remove(t)
                else:
                    e = t.GetStart() if (t.GetStart().x, t.GetStart().y) == (pos.x, pos.y) else t.GetEnd()
                    cut = self.inner_tap(t, e, items)
                    key = (uid(t), cut)
                    if cut is not None and (key in seen or math.dist(cut, (e.x, e.y)) < 1000):
                        cut = None
                    seen.add(key)
                    if cut is None:
                        self.remove(t)
                    else:
                        (t.SetStart if e is t.GetStart() or (t.GetStart().x, t.GetStart().y) == (e.x, e.y)
                         else t.SetEnd)(pcbnew.VECTOR2I(int(cut[0]), int(cut[1])))
                removed += 1
                changed = True
                break
            if not changed:
                break
        if removed:
            print(f'prune: {removed} dangling items removed or cut back')

    def inner_tap(self, t, e, items):
        """Where the dangling end e of t should be cut back to: the connection on t's interior (another
        track's end, a via) nearest e, or None."""
        lay = t.GetLayer()
        f = t.GetEnd() if (t.GetStart().x, t.GetStart().y) == (e.x, e.y) else t.GetStart()
        best = None
        for o in items:
            if o is t:
                continue
            if o.Type() == pcbnew.PCB_VIA_T:
                cands = [o.GetPosition()]
            elif o.GetLayer() == lay:
                cands = [o.GetStart(), o.GetEnd()]
            else:
                continue
            for q in cands:
                if not t.HitTest(q, 0):
                    continue
                if math.dist((q.x, q.y), (f.x, f.y)) < 2:
                    continue
                d = math.dist((q.x, q.y), (e.x, e.y))
                if best is None or d < best[0]:
                    best = (d, (q.x, q.y))
        return None if best is None else best[1]

    def op_prune(self, o):
        nets = [self.net(n) for n in o['nets']]
        for n in nets:
            self.touch(n)
        self.prune(nets)

    # ---------------------------------------------------------------- checks
    def check(self):
        errs = []
        for net, b in self.base.items():
            now = self.pieces(net)
            if now > b:
                errs.append(f'net {net} split: {b} -> {now} pieces')
        vip = self.vias_on_pads()
        for u, where in vip.items():
            if u not in self.vip0:
                errs.append(f'via on pad {where}')
        smd = self.smd_polys()
        for v in self.vias():
            if uid(v) not in self.via0:
                hit = self.via_clear_of_pads(P(v.GetPosition()), TOMM(v.GetWidth(pcbnew.F_Cu)) / 2, smd)
                if hit:
                    errs.append(f'new via {P(v.GetPosition())} within pad gap of '
                                f'{hit.GetParentFootprint().GetReference()}.{hit.GetNumber()}')
        print('vias on pads: %d (was %d): %s' % (len(vip), len(self.vip0), ' '.join(sorted(vip.values()))))
        obs = self.obs()
        for fp in self.moved:
            mine = list(fp.Pads())
            for p in fp.Pads():
                bb = fan2.bb_of(p)
                for l in (pcbnew.F_Cu, pcbnew.B_Cu):
                    if not p.IsOnLayer(l):
                        continue
                    hit = fan2.collides(obs, p, l, p.GetNetname(), bb, fan2.in_area(bb), skip=mine)
                    if hit:
                        errs.append(f'pad {fp.GetReference()}.{p.GetNumber()} hits {dogbone.describe(hit[1], hit[0])}')
            errs += self.courtyard(fp)
        if self.heritage_geometry() != self.her_geom:
            errs.append('heritage geometry changed')
        return errs

    def courtyard(self, fp):
        out = []
        fp.BuildCourtyardCaches()
        for side in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
            a = fp.GetCourtyard(side)
            if a.OutlineCount() == 0:
                continue
            for o in self.board.GetFootprints():
                if uid(o) == uid(fp):
                    continue
                o.BuildCourtyardCaches()
                b = o.GetCourtyard(side)
                if b.OutlineCount() == 0:
                    continue
                q = pcbnew.SHAPE_POLY_SET(a)
                q.BooleanIntersection(b)
                if not q.IsEmpty() and q.Area() > 1e3:
                    out.append(f'courtyard {fp.GetReference()} overlaps {o.GetReference()}')
        return out

    def run(self, ops):
        import time
        for o in ops:
            t0 = time.time()
            getattr(self, 'op_' + o['op'])(o)
            print(f"  [{o['op']} {time.time() - t0:.1f}s]")
        # final sweep: dangling copper as DRC sees it on a fully refilled board
        for _ in range(3):
            pcbnew.ZONE_FILLER(self.board).Fill(self.board.Zones())
            self.prune(list(self.base))
            split = [n for n, b in self.base.items() if n != 'GND' and self.pieces(n) > b]
            if not split:
                break
            print('final sweep: rerouting', split)
            self.op_route({'nets': split, 'widths': [0.2, 0.152, 0.127], 'pad': 3, 'noprune': True})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('board')
    ap.add_argument('out')
    ap.add_argument('spec')
    here = os.path.dirname(os.path.abspath(__file__))
    ap.add_argument('--snap', default=os.path.join(here, '..', '..', 'baseline', 'heritage_rev2.json'))
    ap.add_argument('--project')
    ap.add_argument('--area', default='266.5,88.0,280.0,101.5')
    ap.add_argument('--pad-gap', type=float, default=0.10)
    ap.add_argument('--save-failed')
    ap.add_argument('--reorder', type=int, default=6,
                    help='on a route failure, rerun the batch with the failing net first, up to N times')
    a = ap.parse_args()
    spec = json.load(open(a.spec))
    s = Session(a.board, a.project or os.path.splitext(a.board)[0] + '.kicad_pro', a.snap,
                [float(x) for x in a.area.split(',')], a.pad_gap)
    try:
        s.run(spec['ops'])
        errs = s.check()
    except RouteFail as e:
        errs = [str(e)]
        nets = e.op['nets']
        if a.reorder > 0 and nets[0] != e.net:
            nets.remove(e.net)
            nets.insert(0, e.net)
            retry = os.path.splitext(a.spec)[0] + '.retry.json'
            json.dump(spec, open(retry, 'w'), indent=1)
            print(f'--- retry ({a.reorder} left): route order {nets}', flush=True)
            argv = [a for a in sys.argv]
            argv[3] = retry
            if '--reorder' in argv:
                argv[argv.index('--reorder') + 1] = str(a.reorder - 1)
            else:
                argv += ['--reorder', str(a.reorder - 1)]
            os.execv(sys.executable, [sys.executable] + argv)
    except Fail as e:
        errs = [str(e)]
    if errs:
        print('BATCH FAILED:')
        for e in errs:
            print('  ' + e)
        if a.save_failed:
            pcbnew.SaveBoard(a.save_failed, s.board)
        sys.stdout.flush()
        os._exit(1)
    pcbnew.SaveBoard(a.out, s.board)
    print('saved', a.out)
    sys.stdout.flush()
    os._exit(0)


if __name__ == '__main__':
    main()
