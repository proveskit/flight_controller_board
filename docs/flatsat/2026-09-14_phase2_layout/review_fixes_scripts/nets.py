"""Dump tracks/vias/pads of nets (substring match on the short name, or exact with =NAME).
  nets.py BOARD NET [NET...]
"""
import sys, json
import pcbnew

T = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
her = set(json.load(open('/Users/ossf-1/GitHut/flight_controller_board/FlatSat_V1/tools/baseline/heritage_rev2.json'))['tracks'])


def match(n):
    s = n.split('/')[-1]
    for q in sys.argv[2:]:
        if (q.startswith('=') and s == q[1:]) or (not q.startswith('=') and q in n):
            return True
    return False


for fp in b.GetFootprints():
    for p in fp.Pads():
        if match(p.GetNetname()):
            q = p.GetPosition(); s = p.GetSize(pcbnew.F_Cu)
            print(f'PAD {fp.GetReference()}.{p.GetNumber()} {p.GetNetname()} ({T(q.x):.3f},{T(q.y):.3f}) {T(s.x):.2f}x{T(s.y):.2f} {"THT" if p.GetDrillSizeX() else "SMD"} {fp.GetSide() and "bot" or "top"}')
for t in b.GetTracks():
    if not match(t.GetNetname()):
        continue
    h = 'H' if t.m_Uuid.AsString() in her else 'n'
    if t.GetClass() == 'PCB_VIA':
        q = t.GetPosition()
        print(f'VIA {h} {t.GetNetname()} ({T(q.x):.3f},{T(q.y):.3f}) {T(t.GetWidth(pcbnew.F_Cu)):.2f}/{T(t.GetDrill()):.2f}')
    else:
        s, e = t.GetStart(), t.GetEnd()
        print(f'TRK {h} {t.GetNetname()} {b.GetLayerName(t.GetLayer())} w{T(t.GetWidth()):.3f} ({T(s.x):.3f},{T(s.y):.3f})->({T(e.x):.3f},{T(e.y):.3f}) L{T(t.GetLength()):.2f}')
for z in b.Zones():
    if match(z.GetNetname()):
        bb = z.GetBoundingBox()
        print(f'ZONE {z.GetNetname()} {[b.GetLayerName(l) for l in z.GetLayerSet().Seq()]} bbox ({T(bb.GetLeft()):.1f},{T(bb.GetTop()):.1f})-({T(bb.GetRight()):.1f},{T(bb.GetBottom()):.1f}) prio {z.GetAssignedPriority()}')
