"""Shared board-edit helpers for the fix pass. Every new track/via goes through fan2's exact-polygon
clearance, hole and edge checks against the live board (pads, tracks, vias, footprint copper); zones are
refilled afterwards by refill.py and judged by DRC. Heritage items are refused by uuid.

Use from item scripts:  E = ed.Editor(board_path); ...; E.save()
"""
import json, math, sys
sys.path.insert(0, '/Users/ossf-1/GitHut/flight_controller_board/FlatSat_V1/tools/pcb/closure')
import pcbnew
import fan2

MM, T = pcbnew.FromMM, pcbnew.ToMM
SNAP = '/Users/ossf-1/GitHut/flight_controller_board/FlatSat_V1/tools/baseline/heritage_rev2.json'
HER = json.load(open(SNAP))
HER_T = set(HER['tracks'])
HER_FP = set(HER['footprints'])
L = {'F.Cu': pcbnew.F_Cu, 'B.Cu': pcbnew.B_Cu, 'In1.Cu': None, 'In2.Cu': None}


class Editor:
    def __init__(self, path):
        self.bpath = path
        self.b = pcbnew.LoadBoard(path)
        for n in ('In1.Cu', 'In2.Cu'):
            L[n] = self.b.GetLayerID(n)
        self.cls = fan2.load_cls(path.replace('.kicad_pcb', '.kicad_pro'), self.b)
        self.keep = []
        self.log = []
        self.fails = 0
        self.rebuild()

    def rebuild(self):
        self.obs = fan2.Obs(self.b, self.cls)

    # ---------- queries
    def net(self, name):
        for n, ni in self.b.GetNetsByName().items():
            if str(n) == name or str(n).split('/')[-1] == name:
                return ni
        raise KeyError(name)

    def fp(self, ref):
        return self.b.FindFootprintByReference(ref)

    def pad(self, ref, num):
        return next(p for p in self.fp(ref).Pads() if p.GetNumber() == str(num))

    def padxy(self, ref, num):
        q = self.pad(ref, num).GetPosition()
        return (T(q.x), T(q.y))

    def items(self, net=None, layer=None, kind=None, near=None, r=0.01):
        """tracks/vias filtered; near=(x,y) matches an endpoint (track) or position (via) within r"""
        out = []
        for t in self.b.GetTracks():
            isv = t.GetClass() == 'PCB_VIA'
            if kind == 'via' and not isv or kind == 'track' and isv:
                continue
            if net and t.GetNetname().split('/')[-1] != net and t.GetNetname() != net:
                continue
            if layer and not isv and t.GetLayer() != L[layer]:
                continue
            if near:
                pts = [t.GetPosition()] if isv else [t.GetStart(), t.GetEnd()]
                if not any(math.hypot(T(p.x) - near[0], T(p.y) - near[1]) <= r for p in pts):
                    continue
            out.append(t)
        return out

    # ---------- edits
    def remove(self, items, why=''):
        for t in items:
            assert t.m_Uuid.AsString() not in HER_T, 'refusing to touch heritage item'
            self.b.Remove(t)
            self.keep.append(t)
            self.log.append(('del', self.desc(t), why))
        self.rebuild()

    def desc(self, t):
        if t.GetClass() == 'PCB_VIA':
            q = t.GetPosition()
            return f'via {t.GetNetname().split("/")[-1]} ({T(q.x):.3f},{T(q.y):.3f}) {T(t.GetWidth(pcbnew.F_Cu)):.2f}/{T(t.GetDrill()):.2f}'
        s, e = t.GetStart(), t.GetEnd()
        return f'trk {t.GetNetname().split("/")[-1]} {self.b.GetLayerName(t.GetLayer())} w{T(t.GetWidth()):.3f} ({T(s.x):.3f},{T(s.y):.3f})->({T(e.x):.3f},{T(e.y):.3f})'

    def check_track(self, t, skip=()):
        layer = t.GetLayer()
        net = t.GetNetname()
        bb = fan2.bb_of(t)
        hit = fan2.collides(self.obs, t, layer, net, bb, fan2.in_area(bb), skip=skip)
        if hit:
            return 'clearance vs ' + self.what(hit[1], hit[0])
        if not fan2.edge_ok(self.obs, t, layer):
            return 'edge'
        if not fan2.hole_ok(self.obs, t, [layer], net):
            return 'hole clearance'
        return None

    def what(self, o, net):
        n = (net or '').split('/')[-1]
        if isinstance(o, pcbnew.PAD):
            return f'pad {o.GetParentFootprint().GetReference()}.{o.GetNumber()} {n}'
        try:
            return self.desc(o)
        except Exception:
            return f'{o.GetClass()} {n}'

    def track(self, a, b, w, layer, net, force=False, skip=()):
        t = fan2.mk_track(self.b, a, b, w, L[layer], self.net(net))
        why = self.check_track(t, skip)
        if why and not force:
            self.fails += 1
            print(f'  FAIL track {net} {layer} w{w} {a}->{b}: {why}')
            return None
        self.b.Add(t)
        self.obs.add(t)
        self.log.append(('add', self.desc(t), why or ''))
        return t

    def path(self, pts, w, layer, net, **kw):
        return [self.track(pts[i], pts[i + 1], w, layer, net, **kw) for i in range(len(pts) - 1)]

    def via(self, p, net, dia=0.8, drill=0.4, force=False, skip=()):
        v = fan2.mk_via(self.b, p, self.net(net), dia, drill)
        bb = fan2.bb_of(v)
        why = None
        for l in fan2.cu_layers(self.b):
            hit = fan2.collides(self.obs, v, l, v.GetNetname(), bb, fan2.in_area(bb), skip=skip)
            if hit:
                why = f'{self.b.GetLayerName(l)} clearance vs ' + self.what(hit[1], hit[0])
                break
        if not why and not fan2.hole_ok(self.obs, v, fan2.cu_layers(self.b), v.GetNetname(), pos=p, drill=drill):
            why = 'hole/hole-to-hole'
        if not why and not fan2.edge_ok(self.obs, v, pcbnew.F_Cu):
            why = 'edge'
        if not why:
            c, r = v.GetPosition(), v.GetWidth(pcbnew.F_Cu) // 2
            for f in self.b.GetFootprints():
                for pd in f.Pads():
                    if pd.GetAttribute() != pcbnew.PAD_ATTRIB_SMD:
                        continue
                    lay = pcbnew.F_Cu if pd.IsOnLayer(pcbnew.F_Cu) else pcbnew.B_Cu
                    if pd.GetEffectivePolygon(lay, pcbnew.ERROR_INSIDE).Collide(c, r):
                        why = f'via on SMD pad {f.GetReference()}.{pd.GetNumber()} (F16)'
                        break
                if why:
                    break
        if why and not force:
            self.fails += 1
            print(f'  FAIL via {net} {p}: {why}')
            return None
        self.b.Add(v)
        self.obs.add(v)
        self.log.append(('add', self.desc(v), why or ''))
        return v

    def set_pad_net(self, ref, num, net):
        p = self.pad(ref, num)
        assert p.GetParentFootprint().m_Uuid.AsString() not in HER_FP
        old = p.GetNetname()
        p.SetNet(self.net(net))
        self.log.append(('net', f'{ref}.{num} {old} -> {net}', ''))
        self.rebuild()

    def move_fp(self, ref, xy=None, rot=None):
        f = self.fp(ref)
        assert f.m_Uuid.AsString() not in HER_FP
        old = (T(f.GetPosition().x), T(f.GetPosition().y), f.GetOrientationDegrees())
        if xy:
            f.SetPosition(pcbnew.VECTOR2I_MM(*xy))
        if rot is not None:
            f.SetOrientationDegrees(rot)
        self.log.append(('move', f'{ref} {old} -> ({xy}, {rot})', ''))
        self.rebuild()

    def text(self, s, xy, h=1.0, stroke=0.15, layer=pcbnew.F_SilkS):
        t = pcbnew.PCB_TEXT(self.b)
        t.SetText(s)
        t.SetPosition(pcbnew.VECTOR2I_MM(*xy))
        t.SetLayer(layer)
        t.SetTextSize(pcbnew.VECTOR2I_MM(h, h))
        t.SetTextThickness(MM(stroke))
        self.b.Add(t)
        self.log.append(('add', f'text {s!r} at {xy} h{h} s{stroke}', ''))
        return t

    def save(self, path=None, allow_fail=False):
        if self.fails and not allow_fail:
            sys.exit(f'{self.fails} failed placements; not saved')
        pcbnew.SaveBoard(path or self.bpath, self.b)
        for k, d, w in self.log:
            print(f'{k:4} {d} {w}')
        print("saved", path or self.bpath)


def set_net(E, items, net):
    n = E.net(net)
    for t in items:
        assert t.m_Uuid.AsString() not in HER_T
        E.log.append(('net', E.desc(t), f'-> {net}'))
        t.SetNet(n)
    E.rebuild()


def set_end(E, t, which, xy):
    """move one endpoint of a new track ('start'/'end')"""
    assert t.m_Uuid.AsString() not in HER_T
    before = E.desc(t)
    (t.SetStart if which == 'start' else t.SetEnd)(pcbnew.VECTOR2I_MM(*xy))
    E.log.append(('mod', before, f'{which} -> {xy}'))
    E.rebuild()


def set_field(E, ref, name, value):
    f = E.fp(ref)
    old = f.GetFieldText(name) if f.HasField(name) else None
    f.SetField(name, value)
    E.log.append(('fld', f'{ref}.{name} {old!r}', f'-> {value!r}'))


def court_overlaps(E, refs=None):
    """courtyard overlaps between footprints (front and back), optionally only those involving refs"""
    fps = list(E.b.GetFootprints())
    out = []
    for side in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
        cs = []
        for f in fps:
            c = f.GetCourtyard(side)
            if c.OutlineCount():
                cs.append((f.GetReference(), c, c.BBox()))
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                a, b = cs[i], cs[j]
                if refs and a[0] not in refs and b[0] not in refs:
                    continue
                if not a[2].Intersects(b[2]):
                    continue
                q = pcbnew.SHAPE_POLY_SET(a[1])
                q.BooleanIntersection(b[1])
                if not q.IsEmpty() and q.Area() > 1e3:
                    out.append((a[0], b[0], round(q.Area() / 1e12, 4)))
    return out


def ep_pads(E, ref, num, pts, dia, drill, net='GND'):
    f = E.fp(ref)
    for x, y in pts:
        p = pcbnew.PAD(f)
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        p.SetShape(pcbnew.PAD_SHAPE_CIRCLE)
        p.SetSize(pcbnew.VECTOR2I_MM(dia, dia))
        p.SetDrillSize(pcbnew.VECTOR2I_MM(drill, drill))
        p.SetLayerSet(pcbnew.PAD.PTHMask())
        p.SetNumber(str(num))
        f.Add(p)
        p.SetPosition(pcbnew.VECTOR2I_MM(x, y))
        p.SetNet(E.net(net))
        p.SetLocalZoneConnection(pcbnew.ZONE_CONNECTION_FULL)
        E.log.append(('pad', f'{ref}.{num} PTH {dia}/{drill} at ({x},{y}) {net}', ''))
    E.rebuild()


def rename_net(E, old, new):
    """move every pad/track/zone of net `old` onto a new net named `new`, then drop `old`"""
    b = E.b
    o = E.net(old)
    n = pcbnew.NETINFO_ITEM(b, new)
    b.Add(n)
    k = 0
    for f in b.GetFootprints():
        for p in f.Pads():
            if p.GetNetCode() == o.GetNetCode():
                p.SetNet(n); k += 1
    for t in b.GetTracks():
        if t.GetNetCode() == o.GetNetCode():
            t.SetNet(n); k += 1
    for z in b.Zones():
        if z.GetNetCode() == o.GetNetCode():
            z.SetNet(n); k += 1
    b.Remove(o)
    E.log.append(('ren', f'{old} -> {new}', f'{k} items'))
    E.rebuild()


def widen(E, t, w):
    """try to set a new track's width to w (exact clearance re-check); returns True on success"""
    assert t.m_Uuid.AsString() not in HER_T
    old = t.GetWidth()
    before = E.desc(t)
    t.SetWidth(MM(w))
    why = E.check_track(t)
    if why:
        t.SetWidth(old)
        print(f'  keep {before}: {why}')
        return False
    E.log.append(('wid', before, f'-> w{w}'))
    E.rebuild()
    return True
