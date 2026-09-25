#!/usr/bin/env python3
"""Multi-layer (F.Cu / In2.Cu / B.Cu) raster router for the board extension.
Used to close connections Freerouting could not reach, at a chosen width, with vias only outside the
Rev2 outline (L11).  Same exact-shape clearance model as rgeo.
"""
import heapq
import math

import numpy as np
import pcbnew

import rgeo
from rgeo import Grid, TOMM, MM

CLEAR = 0.24
SAME = None         # same-net copper is not an obstacle: joining it is the point
EDGE = 0.25
MARGIN = 0.04       # grid-quantisation head-room on top of the rule clearance

# netclass clearance per net, loaded from the project file: DRC uses the LARGER of the two nets'
# class clearances, so BenchPower's 0.25 mm applies to any track running next to a BenchPower net.
_CLS = {}


def load_netclasses(pro_path, board):
    import json, fnmatch
    global _CLS
    d = json.load(open(pro_path))
    ns = d['net_settings']
    byname = {c['name']: c.get('clearance', 0.2) for c in ns['classes']}
    dflt = byname.get('Default', 0.2)
    nets = [str(n) for n in board.GetNetsByName().keys()]
    _CLS = {n: dflt for n in nets}
    for pat in ns.get('netclass_patterns', []):
        c = byname.get(pat['netclass'], dflt)
        for n in nets:
            if fnmatch.fnmatch(n, pat['pattern']):
                _CLS[n] = max(_CLS[n], c)
    return _CLS


def net_clear(net):
    return _CLS.get(net, 0.2) + MARGIN


def layer_ids(board):
    return [pcbnew.F_Cu, board.GetLayerID('In2.Cu'), pcbnew.B_Cu]


def dijkstra_ml(frees, via_mask, starts, goal_masks, step, via_cost=1.0, cost_mult=None):
    L = len(frees)
    H, W = frees[0].shape
    N = H * W
    dist = np.full(L * N, 1e18)
    prev = np.full(L * N, -1, dtype=np.int64)
    fr = [f.ravel() for f in frees]
    vm = via_mask.ravel() if via_mask is not None else None
    gm = [m.ravel() for m in goal_masks]
    cm = [c.ravel() if c is not None else None for c in (cost_mult or [None] * L)]
    pq = []
    for (lay, j, i) in starts:
        if 0 <= j < H and 0 <= i < W and frees[lay][j, i]:
            idx = lay * N + j * W + i
            if dist[idx] > 0:
                dist[idx] = 0.0
                heapq.heappush(pq, (0.0, idx))
    best = None
    while pq:
        d, idx = heapq.heappop(pq)
        if d > dist[idx] + 1e-12:
            continue
        lay, rest = divmod(idx, N)
        if gm[lay][rest]:
            best = idx
            break
        j, i = divmod(rest, W)
        for dj, di, w in rgeo.NB:
            nj, ni = j + dj, i + di
            if nj < 0 or nj >= H or ni < 0 or ni >= W:
                continue
            nrest = nj * W + ni
            if not fr[lay][nrest]:
                continue
            nd = d + w * step * (cm[lay][nrest] if cm[lay] is not None else 1.0)
            nidx = lay * N + nrest
            if nd < dist[nidx] - 1e-12:
                dist[nidx] = nd
                prev[nidx] = idx
                heapq.heappush(pq, (nd, nidx))
        if vm is not None and vm[rest]:
            for nl in range(L):
                if nl == lay or not fr[nl][rest]:
                    continue
                nidx = nl * N + rest
                nd = d + via_cost * abs(nl - lay)
                if nd < dist[nidx] - 1e-12:
                    dist[nidx] = nd
                    prev[nidx] = idx
                    heapq.heappush(pq, (nd, nidx))
    if best is None:
        return None
    chain = []
    idx = best
    while idx != -1:
        lay, rest = divmod(idx, N)
        j, i = divmod(rest, W)
        chain.append((lay, j, i))
        idx = prev[idx]
    chain.reverse()
    return chain


def pad_inner(g, pad, layer, hw):
    """cells where a track centre of half-width `hw` still sits entirely inside the pad's own copper.
    A track that leaves its pad along the pad's axis adds no copper outside the pad, so it cannot
    reduce the clearance a neighbouring pad already has -- without this, the clearance halo of a
    0.4 mm-pitch neighbour covers the pad itself and the escape has nowhere to start."""
    ps = pcbnew.SHAPE_POLY_SET()
    pad.TransformShapeToPolygon(ps, layer, 0, MM(0.005), pcbnew.ERROR_INSIDE)
    if hw > 0:
        ps.Inflate(-MM(hw), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, MM(0.005))
    m = np.zeros((g.H, g.W), dtype=bool)
    for pts in rgeo.polyset_pts(ps):
        rgeo.fill_poly(m, pts, g.x0, g.y0, g.step)
    return m


def pad_cells(g, pad, layer, free):
    ps = pcbnew.SHAPE_POLY_SET()
    pad.TransformShapeToPolygon(ps, layer, 0, MM(0.005), pcbnew.ERROR_INSIDE)
    m = np.zeros((g.H, g.W), dtype=bool)
    for pts in rgeo.polyset_pts(ps):
        rgeo.fill_poly(m, pts, g.x0, g.y0, g.step)
    return m & free


def net_copper_mask(g, bd, net, layer, free):
    """cells covered by existing copper of `net` on `layer` (pads, tracks, vias)."""
    m = np.zeros((g.H, g.W), dtype=bool)
    for pd, ref, pnet, lay, bb, ish in bd.pads:
        if pnet != net or layer not in lay:
            continue
        ps = pcbnew.SHAPE_POLY_SET()
        pd.TransformShapeToPolygon(ps, layer, 0, MM(0.005), pcbnew.ERROR_INSIDE)
        for pts in rgeo.polyset_pts(ps):
            rgeo.fill_poly(m, pts, g.x0, g.y0, g.step)
    for t, tnet, tl, bb, ish, isv in bd.tracks:
        if tnet != net:
            continue
        if not isv and tl != layer:
            continue
        if isv and not t.IsOnLayer(layer):
            continue
        ps = pcbnew.SHAPE_POLY_SET()
        try:
            t.TransformShapeToPolygon(ps, layer, 0, MM(0.005), pcbnew.ERROR_INSIDE)
        except Exception:
            continue
        for pts in rgeo.polyset_pts(ps):
            rgeo.fill_poly(m, pts, g.x0, g.y0, g.step)
    return m & free


def island(g, bd, net, layers, seed_masks, copper):
    """flood the connected copper island of `net` that contains the seed, across layers at same-net vias."""
    from collections import deque
    L = len(layers)
    seen = [np.zeros((g.H, g.W), dtype=bool) for _ in layers]
    via_at = np.zeros((g.H, g.W), dtype=bool)
    for t, tnet, tl, bb, ish, isv in bd.tracks:
        if isv and tnet == net:
            pp = t.GetPosition()
            rgeo.fill_circle(via_at, TOMM(pp.x), TOMM(pp.y), TOMM(t.GetDrill()) / 2.0 + 0.05, g.x0, g.y0, g.step)
    for pd, ref, pnet, lay, bb, ish in bd.pads:
        if pnet == net and len(lay) > 2:
            pp = pd.GetPosition()
            rgeo.fill_circle(via_at, TOMM(pp.x), TOMM(pp.y), 0.15, g.x0, g.y0, g.step)
    dq = deque()
    for li, m in seed_masks:
        mm = m & copper[li]
        for j, i in zip(*np.where(mm)):
            if not seen[li][j, i]:
                seen[li][j, i] = True
                dq.append((li, int(j), int(i)))
    while dq:
        li, j, i = dq.popleft()
        for dj, di, _ in rgeo.NB:
            nj, ni = j + dj, i + di
            if 0 <= nj < g.H and 0 <= ni < g.W and copper[li][nj, ni] and not seen[li][nj, ni]:
                seen[li][nj, ni] = True
                dq.append((li, nj, ni))
        if via_at[j, i]:
            for nl in range(L):
                if nl != li and copper[nl][j, i] and not seen[nl][j, i]:
                    seen[nl][j, i] = True
                    dq.append((nl, j, i))
    return seen


def route_conn(bd, net, a_pt, b_pt, width, via_dia=0.46, via_drill=0.2, step=0.1,
               margin=12.0, layers=None, a_pad=None, b_pad=None, allow_via=True,
               start_any_copper=True, clear=None, avoid_rev2=True):
    """Route a connection on `net` between two points.  Returns (parts, vias) in mm, or None."""
    board = bd.b
    layers = layers if layers is not None else layer_ids(board)
    hw = width / 2.0
    CL = CLEAR if clear is None else clear
    # the grid-quantisation head-room shrinks with the grid step, so a fine retry may legitimately
    # use a smaller margin -- apply the SAME margin to the per-netclass clearances
    mg = CL - 0.2
    nc = (lambda n: _CLS.get(n, 0.2) + mg)
    x0 = min(a_pt[0], b_pt[0]) - margin
    x1 = max(a_pt[0], b_pt[0]) + margin
    y0 = min(a_pt[1], b_pt[1]) - margin
    y1 = max(a_pt[1], b_pt[1]) + margin
    bb = board.GetBoardEdgesBoundingBox()
    x0 = max(x0, TOMM(bb.GetLeft()) - 1); y0 = max(y0, TOMM(bb.GetTop()) - 1)
    x1 = min(x1, TOMM(bb.GetRight()) + 1); y1 = min(y1, TOMM(bb.GetBottom()) + 1)
    while ((x1 - x0) / step) * ((y1 - y0) / step) > 1600000:
        step *= 1.25
    g = Grid(bd, x0, y0, x1, y1, step)
    base = max(CL, nc(net))
    frees, pens = [], []
    for L in layers:
        blk = g.obstacles(L, net, hw, base, SAME, EDGE, net_clear=nc)
        fr = ~blk
        for pad in (a_pad, b_pad):
            if pad is not None and pad.IsOnLayer(L):
                fr |= pad_inner(g, pad, L, hw)
        fr &= g._deflated_board(EDGE + hw)
        if avoid_rev2:
            fr &= ~g.inside_rev2          # L11: nothing new inside the flight section but the stubs
        frees.append(fr)
        pens.append(None)
    vm = None
    if allow_via:
        vb = np.zeros((g.H, g.W), dtype=bool)
        for L in rgeo.copper_layers(board):
            vb |= g.obstacles(L, net, via_dia / 2.0, base, SAME, EDGE, net_clear=nc)
        vb |= g.hole_mask(net, via_drill / 2.0, extra=0.05)
        vm = (~vb) & (~g.inside_rev2)
    # start / goal masks
    def endpoint_mask(pt, pad):
        ms = []
        for li, L in enumerate(layers):
            if pad is not None:
                if L in [l for l in rgeo.copper_layers(board) if pad.IsOnLayer(l)]:
                    ms.append((li, pad_cells(g, pad, L, frees[li])))
            else:
                # no pad: the endpoint is a point on existing copper of this net (a stub end).  The
                # anchor must land INSIDE that copper or KiCad's connectivity will not join them, so
                # use the net's actual copper cells near the point, not a blob around it.
                cop = net_copper_mask(g, bd, net, L, np.ones((g.H, g.W), dtype=bool))
                near = np.zeros((g.H, g.W), dtype=bool)
                rgeo.fill_circle(near, pt[0], pt[1], 1.0, g.x0, g.y0, g.step)
                m = cop & near
                if not m.any():
                    j, i = g.cell(pt[0], pt[1])
                    if 0 <= j < g.H and 0 <= i < g.W:
                        m[max(0, j - 2):j + 3, max(0, i - 2):i + 3] = True
                ms.append((li, m & frees[li]))
        return ms
    smask = endpoint_mask(a_pt, a_pad)
    if start_any_copper:
        copper = [net_copper_mask(g, bd, net, L, np.ones((g.H, g.W), dtype=bool)) for L in layers]
        isl = island(g, bd, net, layers, smask, copper)
        smask = smask + [(li, isl[li] & frees[li]) for li in range(len(layers))]
    starts = []
    for li, m in smask:
        for j, i in zip(*np.where(m)):
            starts.append((li, int(j), int(i)))
    goals = [np.zeros((g.H, g.W), dtype=bool) for _ in layers]
    for li, m in endpoint_mask(b_pt, b_pad):
        goals[li] |= m
    if b_pad is not None:
        for li, L in enumerate(layers):
            if b_pad.IsOnLayer(L):
                goals[li] |= pad_inner(g, b_pad, L, hw)
    if not starts or not any(m.any() for m in goals):
        return None
    chain = dijkstra_ml(frees, vm, starts, goals, step, via_cost=1.0, cost_mult=pens)
    if chain is None:
        return None
    segs = []
    cur = [chain[0]]
    for c in chain[1:]:
        if c[0] != cur[-1][0]:
            segs.append(cur)
            cur = [c]
        else:
            cur.append(c)
    segs.append(cur)
    parts, vias = [], []
    prev_end = None
    for si, s in enumerate(segs):
        li = s[0][0]
        pts = rgeo.simplify([(j, i) for (l, j, i) in s], g, frees[li])
        if si == 0 and a_pad is not None and a_pad.IsOnLayer(layers[li]) and start_any_copper is not None:
            j0, i0 = g.cell(TOMM(a_pad.GetPosition().x), TOMM(a_pad.GetPosition().y))
            if abs(j0 - s[0][1]) <= 3 and abs(i0 - s[0][2]) <= 3:
                pts[0] = (TOMM(a_pad.GetPosition().x), TOMM(a_pad.GetPosition().y))
        if si == len(segs) - 1 and b_pad is not None and b_pad.IsOnLayer(layers[li]):
            pts[-1] = (TOMM(b_pad.GetPosition().x), TOMM(b_pad.GetPosition().y))
        if prev_end is not None:
            pts[0] = prev_end
        parts.append({'layer': board.GetLayerName(layers[li]), 'pts': pts})
        prev_end = pts[-1]
    for k in range(1, len(segs)):
        vp = g.pos(segs[k][0][1], segs[k][0][2])
        vias.append({'pos': [vp[0], vp[1]], 'dia': via_dia, 'drill': via_drill})
        parts[k - 1]['pts'][-1] = (vp[0], vp[1])
        parts[k]['pts'][0] = (vp[0], vp[1])
    return parts, vias


def draw(board, net_name, parts, vias, width):
    net = board.FindNet(net_name)
    added = []
    for part in parts:
        lay = board.GetLayerID(part['layer'])
        for a, b in zip(part['pts'], part['pts'][1:]):
            if math.hypot(a[0] - b[0], a[1] - b[1]) < 1e-6:
                continue
            t = pcbnew.PCB_TRACK(board)
            t.SetStart(pcbnew.VECTOR2I_MM(float(a[0]), float(a[1])))
            t.SetEnd(pcbnew.VECTOR2I_MM(float(b[0]), float(b[1])))
            t.SetWidth(MM(width))
            t.SetLayer(lay)
            t.SetNet(net)
            board.Add(t)
            added.append(t)
    for v in vias:
        pv = pcbnew.PCB_VIA(board)
        pv.SetPosition(pcbnew.VECTOR2I_MM(float(v['pos'][0]), float(v['pos'][1])))
        pv.SetWidth(MM(v['dia']))
        pv.SetDrill(MM(v['drill']))
        pv.SetNet(net)
        pv.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        board.Add(pv)
        added.append(pv)
    return added
