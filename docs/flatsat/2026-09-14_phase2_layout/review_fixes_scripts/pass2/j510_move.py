"""Review-2 item 1: J510 to (262.0,168.93), shell face 0.46 mm proud of Edge.Cuts y=172.12 (HRO C165948
RECOMMEND P.C.B LAYOUT). The pad-row strap moves with the part; each escape keeps its segment and width and
only its pad end is stretched by DY, so no new track_width item appears."""
import sys, pcbnew, ed
DY = 2.87
E = ed.Editor(sys.argv[1])
T = pcbnew.ToMM
f = E.fp('J510')
x0, y0 = T(f.GetPosition().x), T(f.GetPosition().y)
assert (round(x0, 3), round(y0, 3)) == (262.0, 166.06), (x0, y0)
uu = lambda t: t.m_Uuid.AsString()[:8]
strap = {'af7fb969', '6f33174a', 'bc9e5c1e', 'e9589dbf', '56c0a8a7', 'b06cf6f6'}
stretch = {'467132b9': (259.55, 161.32), '3d51ac80': (260.75, 162.015), '7bffc762': (263.75, 162.015)}
E.move_fp('J510', (262.0, 168.93))
moved = []
for t in list(E.b.GetTracks()):
    u = uu(t)
    if u in strap:
        assert t.m_Uuid.AsString() not in ed.HER_T
        before = E.desc(t)
        t.Move(pcbnew.VECTOR2I_MM(0, DY))
        E.log.append(('mov', before, f'+{DY} y'))
        moved.append(t)
    elif u in stretch:
        px, py = stretch[u]
        s, e = t.GetStart(), t.GetEnd()
        which = 'start' if abs(T(s.x) - px) < 1e-3 and abs(T(s.y) - py) < 1e-3 else 'end'
        q = s if which == 'start' else e
        assert abs(T(q.x) - px) < 1e-3 and abs(T(q.y) - py) < 1e-3, (u, E.desc(t))
        ed.set_end(E, t, which, (px, py + DY))
        moved.append(t)
assert len(moved) == 9, len(moved)
E.rebuild()
bad = 0
for t in moved:
    why = E.check_track(t)
    if why:
        print('  FAIL', E.desc(t), why); bad += 1
fab = [g for g in f.GraphicalItems() if E.b.GetLayerName(g.GetLayer()) == 'F.Fab']
front = max(T(g.GetBoundingBox().GetBottom()) for g in fab) - 0.05
print(f'J510 F.Fab front y={front:.3f}, Edge.Cuts y=172.12 -> proud {front - 172.12:+.3f} mm')
print('courtyard overlaps with J510:', ed.court_overlaps(E, {'J510'}))
if bad:
    sys.exit('clearance failures; not saved')
E.save()
