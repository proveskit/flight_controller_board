"""widthlist.py BOARD : every BenchPower/BenchPower5V/FCPower track < 1.0 mm outside the FC_COPY area, with geometry"""
import sys, json, fnmatch, pcbnew, ed
E = ed.Editor(sys.argv[1])
d = json.load(open(sys.argv[1].replace('.kicad_pcb', '.kicad_pro')))
pats = d['net_settings']['netclass_patterns']
def cls(n):
    c = 'Default'
    for p in pats:
        if fnmatch.fnmatch(n, p['pattern']) or fnmatch.fnmatch(n.split('/')[-1], p['pattern']): c = p['netclass']
    return c
poly = [tuple(p) for p in ed.HER['rev2_outline']]
import math
def inside(p):
    x, y = p; c = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1): c = not c
    return c
rows = []
for t in E.b.GetTracks():
    if t.GetClass() == 'PCB_VIA' or cls(t.GetNetname()) not in ('BenchPower', 'BenchPower5V', 'FCPower'): continue
    if ed.T(t.GetWidth()) >= 1.0 - 1e-6: continue
    s, e = t.GetStart(), t.GetEnd()
    ps, pe = (ed.T(s.x), ed.T(s.y)), (ed.T(e.x), ed.T(e.y))
    if any(inside((ps[0] + (pe[0] - ps[0]) * k / 8, ps[1] + (pe[1] - ps[1]) * k / 8)) for k in range(9)): continue
    rows.append((t.GetNetname().split('/')[-1], E.b.GetLayerName(t.GetLayer()), ed.T(t.GetWidth()), ed.T(t.GetLength()), ps, pe, 'H' if t.m_Uuid.AsString() in ed.HER_T else 'n'))
for r in sorted(rows):
    print(f'{r[0]:14} {r[1]:7} w{r[2]:.3f} L{r[3]:6.2f} ({r[4][0]:.2f},{r[4][1]:.2f})->({r[5][0]:.2f},{r[5][1]:.2f}) {r[6]}')
print(len(rows))
