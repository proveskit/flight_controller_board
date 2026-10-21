"""Plot a board region to PNG for inspection.
  plot.py BOARD x0 y0 x1 y1 OUT.png [--layers F.Cu,In1.Cu,In2.Cu,B.Cu] [--zones] [--scale 40] [--nets]
"""
import argparse, math, subprocess, html
import pcbnew

T = pcbnew.ToMM
COL = {'F.Cu': '#d22', 'In1.Cu': '#c80', 'In2.Cu': '#a0a', 'B.Cu': '#22d'}

ap = argparse.ArgumentParser()
ap.add_argument('board'); ap.add_argument('x0', type=float); ap.add_argument('y0', type=float)
ap.add_argument('x1', type=float); ap.add_argument('y1', type=float); ap.add_argument('out')
ap.add_argument('--layers', default='F.Cu,In1.Cu,In2.Cu,B.Cu')
ap.add_argument('--zones', action='store_true')
ap.add_argument('--scale', type=float, default=40)
ap.add_argument('--labels', action='store_true')
ap.add_argument('--grid', type=float, default=1.0)
ap.add_argument('--court', action='store_true')
a = ap.parse_args()
b = pcbnew.LoadBoard(a.board)
layers = a.layers.split(',')
S = a.scale
W, H = (a.x1 - a.x0) * S, (a.y1 - a.y0) * S
X = lambda x: (x - a.x0) * S
Y = lambda y: (y - a.y0) * S
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}"><rect width="100%" height="100%" fill="white"/>']


def inbox(x0, y0, x1, y1, m=1):
    return not (x1 < a.x0 - m or x0 > a.x1 + m or y1 < a.y0 - m or y0 > a.y1 + m)


def polypath(ps):
    d = ''
    for i in range(ps.OutlineCount()):
        o = ps.Outline(i)
        pts = [o.CPoint(k) for k in range(o.PointCount())]
        d += 'M' + ' L'.join(f'{X(T(p.x)):.1f},{Y(T(p.y)):.1f}' for p in pts) + ' Z '
        for h in range(ps.HoleCount(i)):
            ho = ps.Hole(i, h)
            pts = [ho.CPoint(k) for k in range(ho.PointCount())]
            d += 'M' + ' L'.join(f'{X(T(p.x)):.1f},{Y(T(p.y)):.1f}' for p in pts) + ' Z '
    return d


g = a.grid
k = math.ceil(a.x0 / g)
while k * g <= a.x1:
    x = k * g
    out.append(f'<line x1="{X(x)}" y1="0" x2="{X(x)}" y2="{H}" stroke="#ddd" stroke-width="1"/>')
    out.append(f'<text x="{X(x)+2}" y="10" font-size="9" fill="#888">{x:g}</text>')
    k += 1
k = math.ceil(a.y0 / g)
while k * g <= a.y1:
    y = k * g
    out.append(f'<line x1="0" y1="{Y(y)}" x2="{W}" y2="{Y(y)}" stroke="#ddd" stroke-width="1"/>')
    out.append(f'<text x="2" y="{Y(y)-2}" font-size="9" fill="#888">{y:g}</text>')
    k += 1
if a.zones:
    for z in b.Zones():
        for L in z.GetLayerSet().Seq():
            ln = b.GetLayerName(L)
            if ln in layers and z.HasFilledPolysForLayer(L):
                out.append(f'<path d="{polypath(z.GetFilledPolysList(L))}" fill="{COL[ln]}" fill-opacity="0.08" fill-rule="evenodd"/>')
labels = []
for ln in reversed(layers):
    L = b.GetLayerID(ln)
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_VIA' or t.GetLayer() != L:
            continue
        s, e = t.GetStart(), t.GetEnd()
        if not inbox(min(T(s.x), T(e.x)), min(T(s.y), T(e.y)), max(T(s.x), T(e.x)), max(T(s.y), T(e.y))):
            continue
        out.append(f'<line x1="{X(T(s.x)):.1f}" y1="{Y(T(s.y)):.1f}" x2="{X(T(e.x)):.1f}" y2="{Y(T(e.y)):.1f}" stroke="{COL[ln]}" stroke-opacity="0.55" stroke-width="{T(t.GetWidth())*S:.1f}" stroke-linecap="round"/>')
        if a.labels:
            labels.append(((T(s.x) + T(e.x)) / 2, (T(s.y) + T(e.y)) / 2, t.GetNetname().split('/')[-1][:14], COL[ln]))
for fp in b.GetFootprints():
    for p in fp.Pads():
        bb = p.GetBoundingBox()
        if not inbox(T(bb.GetLeft()), T(bb.GetTop()), T(bb.GetRight()), T(bb.GetBottom())):
            continue
        for ln in layers:
            L = b.GetLayerID(ln)
            if p.IsOnLayer(L):
                ps = p.GetEffectivePolygon(L, pcbnew.ERROR_INSIDE)
                out.append(f'<path d="{polypath(ps)}" fill="none" stroke="#080" stroke-width="1.2"/>')
                break
        q = p.GetPosition()
        labels.append((T(q.x), T(q.y), f'{fp.GetReference()}.{p.GetNumber()} {p.GetNetname().split("/")[-1][:12]}', '#060'))
for t in b.GetTracks():
    if t.GetClass() != 'PCB_VIA':
        continue
    q = t.GetPosition()
    x, y = T(q.x), T(q.y)
    if not inbox(x, y, x, y):
        continue
    r = T(t.GetWidth(pcbnew.F_Cu)) / 2
    out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{r*S:.1f}" fill="#999" fill-opacity="0.6" stroke="black" stroke-width="0.8"/>')
    out.append(f'<circle cx="{X(x):.1f}" cy="{Y(y):.1f}" r="{T(t.GetDrill())/2*S:.1f}" fill="white"/>')
    if a.labels:
        labels.append((x, y + r, t.GetNetname().split('/')[-1][:12], '#333'))
if a.court:
    for fp in b.GetFootprints():
        try:
            cy = fp.GetCourtyard(pcbnew.F_CrtYd if not fp.IsFlipped() else pcbnew.B_CrtYd)
        except Exception:
            continue
        if cy.OutlineCount():
            bb = fp.GetBoundingBox(False)
            if inbox(T(bb.GetLeft()), T(bb.GetTop()), T(bb.GetRight()), T(bb.GetBottom())):
                out.append(f'<path d="{polypath(cy)}" fill="none" stroke="#0aa" stroke-width="1" stroke-dasharray="4,2"/>')
                q = fp.GetPosition()
                labels.append((T(q.x), T(q.y) - 0.3, fp.GetReference(), '#077'))
for x, y, s, c in labels:
    if a.x0 <= x <= a.x1 and a.y0 <= y <= a.y1:
        out.append(f'<text x="{X(x):.1f}" y="{Y(y):.1f}" font-size="8" fill="{c}">{html.escape(s)}</text>')
out.append('</svg>')
svg = a.out.rsplit('.', 1)[0] + '.svg'
open(svg, 'w').write('\n'.join(out))
subprocess.run(['rsvg-convert', '-o', a.out, svg], check=True)
print(a.out, f'{W:.0f}x{H:.0f}')
