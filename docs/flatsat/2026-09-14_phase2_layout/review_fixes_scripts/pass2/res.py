"""DC resistance of one net's track/via/pad copper by nodal analysis (zones ignored).

  res.py BOARD NET --src REF.PAD[,REF.PAD..] --snk REF.PAD[,..] [--probe REF.PAD ...] [--cut x,y,r ...]

Source pads are tied to one node through 1 uOhm each (a lumped terminal, e.g. all FET source pads), same for
sink pads. Prints R(src->snk) and, for each --probe pad, (V(probe) - V(snk)) / I, i.e. the copper a sense pin
on that pad sees in series with the sink terminal. --cut drops tracks/vias whose centre is within r of x,y.
Copper: JLC04161H-7628, outer 1 oz (35 um), inner 0.5 oz (17.5 um), via plating 20 um, board 1.6 mm with
layer stack F 0 / In1 0.21 / In2 1.39 / B 1.6 mm. rho = 1.72e-8 Ohm m.
"""
import argparse, math, collections
import pcbnew

T = pcbnew.ToMM
RHO = 1.72e-8
THK = {'F.Cu': 35e-6, 'In1.Cu': 17.5e-6, 'In2.Cu': 17.5e-6, 'B.Cu': 35e-6}
Z = {'F.Cu': 0.0, 'In1.Cu': 0.2104, 'In2.Cu': 1.3896, 'B.Cu': 1.6}
PLATE = 20e-6
LAYERS = ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu']

ap = argparse.ArgumentParser()
ap.add_argument('board'); ap.add_argument('net')
ap.add_argument('--src', required=True); ap.add_argument('--snk', required=True)
ap.add_argument('--probe', nargs='*', default=[])
ap.add_argument('--cut', nargs='*', default=[])
a = ap.parse_args()
b = pcbnew.LoadBoard(a.board)
LN = {b.GetLayerID(n): n for n in LAYERS}
cuts = [tuple(map(float, c.split(','))) for c in a.cut]


def netok(n):
    return n == a.net or n.split('/')[-1] == a.net


edges = []            # (n1, n2, R)
nid = {}


def node(key):
    if key not in nid:
        nid[key] = len(nid)
    return nid[key]


def barrel(x, y, drill, layers, tag):
    """chain of per-layer nodes joined by plated-barrel resistance"""
    ls = sorted(layers, key=lambda l: Z[l])
    ns = [node((tag, l)) for l in ls]
    for i in range(len(ls) - 1):
        dz = (Z[ls[i + 1]] - Z[ls[i]]) * 1e-3
        r = RHO * dz / (math.pi * drill * 1e-3 * PLATE)
        edges.append((ns[i], ns[i + 1], r))
    return dict(zip(ls, ns))


# ---- collect copper
tracks, vias, pads = [], [], []
for t in b.GetTracks():
    if not netok(t.GetNetname()):
        continue
    if t.GetClass() == 'PCB_VIA':
        q = t.GetPosition()
        if any(math.hypot(T(q.x) - x, T(q.y) - y) < r for x, y, r in cuts):
            continue
        vias.append((T(q.x), T(q.y), T(t.GetWidth(pcbnew.F_Cu)) / 2, T(t.GetDrill())))
    else:
        s, e = t.GetStart(), t.GetEnd()
        m = ((T(s.x) + T(e.x)) / 2, (T(s.y) + T(e.y)) / 2)
        if any(math.hypot(m[0] - x, m[1] - y) < r for x, y, r in cuts):
            continue
        if t.GetLayer() not in LN:
            continue
        tracks.append([LN[t.GetLayer()], (T(s.x), T(s.y)), (T(e.x), T(e.y)), T(t.GetWidth())])
for f in b.GetFootprints():
    for p in f.Pads():
        if not netok(p.GetNetname()):
            continue
        ls = [LN[l] for l in p.GetLayerSet().Seq() if l in LN]
        polys = {l: p.GetEffectivePolygon(b.GetLayerID(l), pcbnew.ERROR_INSIDE) for l in ls}
        pads.append((f'{f.GetReference()}.{p.GetNumber()}', p, ls, polys, T(p.GetDrillSizeX())))

# ---- attachment points per track endpoint: pad, via, or another track's body (T-junction)
anchors = collections.defaultdict(list)   # track index -> list of (param t, node)


def seg_param(p, a_, b_):
    dx, dy = b_[0] - a_[0], b_[1] - a_[1]
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return 0.0, math.hypot(p[0] - a_[0], p[1] - a_[1])
    t = max(0.0, min(1.0, ((p[0] - a_[0]) * dx + (p[1] - a_[1]) * dy) / L2))
    return t, math.hypot(p[0] - (a_[0] + t * dx), p[1] - (a_[1] + t * dy))


pad_nodes = {}
for name, p, ls, polys, drill in pads:
    q = p.GetPosition()
    if drill > 0:
        pad_nodes[name] = barrel(T(q.x), T(q.y), drill, ls, ('pad', name))
    else:
        pad_nodes[name] = {l: node(('pad', name, l)) for l in ls}
via_nodes = [barrel(x, y, d, LAYERS, ('via', i)) for i, (x, y, r, d) in enumerate(vias)]

for i, (l, s, e, w) in enumerate(tracks):
    for end, t in ((s, 0.0), (e, 1.0)):
        hit = False
        for name, p, ls, polys, drill in pads:
            if l in polys and polys[l].Contains(pcbnew.VECTOR2I_MM(*end)):
                anchors[i].append((t, pad_nodes[name][l])); hit = True
        for k, (x, y, r, d) in enumerate(vias):
            if math.hypot(end[0] - x, end[1] - y) <= r:
                anchors[i].append((t, via_nodes[k][l])); hit = True
        anchors[i].append((t, node(('end', l, round(end[0], 3), round(end[1], 3)))))
# T-junctions: an endpoint of track j lying on the body of track i (same layer)
for j, (lj, sj, ej, wj) in enumerate(tracks):
    for end in (sj, ej):
        for i, (l, s, e, w) in enumerate(tracks):
            if i == j or l != lj:
                continue
            t, d = seg_param(end, s, e)
            if d <= w / 2 and 1e-6 < t < 1 - 1e-6:
                anchors[i].append((t, node(('end', l, round(end[0], 3), round(end[1], 3)))))
# overlapping track ends (end-to-end overlaps without a shared point)
ends = [(l, end, w) for (l, s_, e_, w) in tracks for end in (s_, e_)]
for x in range(len(ends)):
    for y in range(x + 1, len(ends)):
        (l1, p1, w1), (l2, p2, w2) = ends[x], ends[y]
        if l1 == l2 and 1e-6 < math.hypot(p1[0] - p2[0], p1[1] - p2[1]) <= max(w1, w2) / 2:
            edges.append((node(('end', l1, round(p1[0], 3), round(p1[1], 3))), node(('end', l2, round(p2[0], 3), round(p2[1], 3))), 1e-7))
# vias/pads sitting on a track body
for i, (l, s, e, w) in enumerate(tracks):
    for k, (x, y, r, d) in enumerate(vias):
        t, dist = seg_param((x, y), s, e)
        if dist <= w / 2:
            anchors[i].append((t, via_nodes[k][l]))
# resistors along each track between its sorted anchors
for i, (l, s, e, w) in enumerate(tracks):
    L = math.hypot(e[0] - s[0], e[1] - s[1])
    pts = sorted(anchors[i])
    for (t0, n0), (t1, n1) in zip(pts, pts[1:]):
        if n0 == n1:
            continue
        r = RHO * max((t1 - t0) * L, 1e-4) * 1e-3 / (w * 1e-3 * THK[l])
        edges.append((n0, n1, r))
# coincident track ends on one layer are the same node already (keyed by rounded xy)


def solve(src_nodes, snk_nodes):
    """direct nodal solve; ties (<= 1 uOhm) merge nodes. Returns potential function and R(src->snk)."""
    n = len(nid)
    S, K = n, n + 1
    E = list(edges) + [(S, x, 1e-9) for x in src_nodes] + [(K, x, 1e-9) for x in snk_nodes]
    par = list(range(n + 2))
    def fd(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for u, v, r in E:
        if r <= 1e-6:
            par[fd(u)] = fd(v)
    reps = sorted({fd(x) for x in range(n + 2)})
    assert fd(S) != fd(K), 'source and sink shorted'
    idx = {r: i for i, r in enumerate(reps)}
    m = len(reps)
    G = [[0.0] * m for _ in range(m)]
    for u, v, r in E:
        if r <= 1e-6:
            continue
        i, j = idx[fd(u)], idx[fd(v)]
        if i == j:
            continue
        g = 1.0 / r
        G[i][i] += g; G[j][j] += g; G[i][j] -= g; G[j][i] -= g
    k = idx[fd(K)]
    keep = [i for i in range(m) if i != k]
    A = [[G[i][j] for j in keep] + [1.0 if i == idx[fd(S)] else 0.0] for i in keep]
    N = len(keep)
    for c in range(N):
        p = max(range(c, N), key=lambda r_: abs(A[r_][c]))
        if abs(A[p][c]) < 1e-30:
            continue
        A[c], A[p] = A[p], A[c]
        for r_ in range(c + 1, N):
            f = A[r_][c] / A[c][c]
            if f:
                row, pc = A[r_], A[c]
                for j in range(c, N + 1):
                    row[j] -= f * pc[j]
    x = [0.0] * N
    for c in range(N - 1, -1, -1):
        if abs(A[c][c]) < 1e-30:
            continue
        x[c] = (A[c][N] - sum(A[c][j] * x[j] for j in range(c + 1, N))) / A[c][c]
    Vr = {keep[i]: x[i] for i in range(N)}
    Vr[k] = 0.0
    V = [Vr[idx[fd(u)]] for u in range(n + 2)]
    return V, S


def pad_layer_nodes(spec):
    out = []
    for nm in spec.split(','):
        out += list(pad_nodes[nm].values())
    return out


src, snk = pad_layer_nodes(a.src), pad_layer_nodes(a.snk)
V, S = solve(src, snk)
print(f'{a.net}: R({a.src} -> {a.snk}) = {V[S] * 1e3:.2f} mOhm  ({len(tracks)} tracks, {len(vias)} vias, {len(nid)} nodes)')
for pr in a.probe:
    vv = [V[x] for x in pad_layer_nodes(pr)]
    print(f'  probe {pr}: (V - V_snk)/I = {sum(vv) / len(vv) * 1e3:.2f} mOhm')

if __name__ == '__main__' and 'DEBUG' in __import__('os').environ:
    par = list(range(len(nid)))
    def fd(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for u, v, r in edges:
        par[fd(u)] = fd(v)
    inv = {v: k for k, v in nid.items()}
    comp = collections.defaultdict(list)
    for k, v in nid.items():
        comp[fd(v)].append(k)
    for c, ks in comp.items():
        pn = sorted({str(k[1]) if k[0] == 'pad' else str(k[0][1]) for k in ks if k[0] == 'pad' or (isinstance(k[0], tuple) and k[0][0] == 'pad')})
        print('COMP', len(ks), pn[:12], [k for k in ks if k[0] == 'end'][:3])
