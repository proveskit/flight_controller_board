"""region.py BOARD x0 y0 x1 y1 [layers] : every pad/track/via touching the box, grouped by net"""
import sys, collections, pcbnew
T = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1]); x0, y0, x1, y1 = map(float, sys.argv[2:6])
lay = sys.argv[6].split(',') if len(sys.argv) > 6 else None
inb = lambda x, y: x0 <= x <= x1 and y0 <= y <= y1
g = collections.defaultdict(list)
for f in b.GetFootprints():
    for p in f.Pads():
        q = p.GetPosition(); bb = p.GetBoundingBox()
        if inb(T(q.x), T(q.y)):
            g[p.GetNetname().split('/')[-1]].append(f'PAD {f.GetReference()}.{p.GetNumber()} ({T(q.x):.3f},{T(q.y):.3f}) bb x{T(bb.GetLeft()):.2f}-{T(bb.GetRight()):.2f} y{T(bb.GetTop()):.2f}-{T(bb.GetBottom()):.2f}')
for t in b.GetTracks():
    n = t.GetNetname().split('/')[-1]
    if t.GetClass() == 'PCB_VIA':
        q = t.GetPosition()
        if inb(T(q.x), T(q.y)): g[n].append(f'VIA ({T(q.x):.3f},{T(q.y):.3f}) {T(t.GetWidth(pcbnew.F_Cu)):.2f}')
    else:
        ln = b.GetLayerName(t.GetLayer())
        if lay and ln not in lay: continue
        s, e = t.GetStart(), t.GetEnd()
        if inb(T(s.x), T(s.y)) or inb(T(e.x), T(e.y)):
            g[n].append(f'{ln} ({T(s.x):.3f},{T(s.y):.3f})->({T(e.x):.3f},{T(e.y):.3f}) w{T(t.GetWidth()):.3f}')
for n in sorted(g):
    print(n)
    for s in g[n]: print('   ', s)
