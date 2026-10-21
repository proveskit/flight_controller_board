#!/usr/bin/env python3
"""Render a board region to SVG (then PNG via rsvg-convert): pads, tracks, vias, zones outline, courtyards, refs.
  regsvg.py BOARD x0 y0 x1 y1 OUT.png [--layers F,B,1,2] [--scale 40] [--nets] [--zones] [--hl NET,NET]
Run with KiCad's bundled python3; needs rsvg-convert (Homebrew librsvg) on PATH. Read-only."""
import sys, argparse, subprocess, pcbnew, html
ap = argparse.ArgumentParser(); ap.add_argument('board'); ap.add_argument('x0',type=float); ap.add_argument('y0',type=float)
ap.add_argument('x1',type=float); ap.add_argument('y1',type=float); ap.add_argument('out')
ap.add_argument('--layers', default='F,B,1,2'); ap.add_argument('--scale', type=float, default=40)
ap.add_argument('--nets', action='store_true'); ap.add_argument('--hl', default='')
ap.add_argument('--zones', action='store_true')
a = ap.parse_args()
b = pcbnew.LoadBoard(a.board)
LID = {'F': pcbnew.F_Cu, 'B': pcbnew.B_Cu, '1': pcbnew.In1_Cu, '2': pcbnew.In2_Cu}
COL = {'F': '#d03030', 'B': '#3060e0', '1': '#c0a000', '2': '#20a040'}
order = [l for l in ['2','1','B','F'] if l in a.layers.split(',')]
hl = set(x for x in a.hl.split(',') if x)
S = a.scale; mm = pcbnew.ToMM
def X(v): return (mm(v) - a.x0) * S
def Y(v): return (mm(v) - a.y0) * S
W = (a.x1-a.x0)*S; H = (a.y1-a.y0)*S
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" style="background:#111">', '<rect width="100%" height="100%" fill="#111"/>']
def inbox(bb):
    return not (mm(bb.GetRight()) < a.x0 or mm(bb.GetLeft()) > a.x1 or mm(bb.GetBottom()) < a.y0 or mm(bb.GetTop()) > a.y1)
def polypath(ps):
    d=''
    for i in range(ps.OutlineCount()):
        ol = ps.Outline(i)
        pts = [ol.CPoint(j) for j in range(ol.PointCount())]
        d += 'M' + ' L'.join(f'{X(p.x):.1f},{Y(p.y):.1f}' for p in pts) + ' Z '
    return d
labels=[]
for L in order:
    lid = LID[L]; c = COL[L]
    if a.zones:
        for z in b.Zones():
            if z.IsOnLayer(lid) and not z.GetIsRuleArea() and inbox(z.GetBoundingBox()):
                fp = z.GetFilledPolysList(lid)
                if fp.OutlineCount(): o.append(f'<path d="{polypath(fp)}" fill="{c}" fill-opacity="0.10" stroke="none"/>')
    for t in b.GetTracks():
        if t.GetClass() == 'PCB_TRACK' and t.GetLayer() == lid and inbox(t.GetBoundingBox()):
            n=t.GetNetname(); col = '#ffffff' if n in hl else c
            o.append(f'<line x1="{X(t.GetStart().x):.1f}" y1="{Y(t.GetStart().y):.1f}" x2="{X(t.GetEnd().x):.1f}" y2="{Y(t.GetEnd().y):.1f}" stroke="{col}" stroke-opacity="0.75" stroke-width="{mm(t.GetWidth())*S:.1f}" stroke-linecap="round"/>')
            if a.nets and t.GetLength() > 1.2e6:
                labels.append(((X(t.GetStart().x)+X(t.GetEnd().x))/2, (Y(t.GetStart().y)+Y(t.GetEnd().y))/2, n.split('/')[-1], c))
for fp in b.GetFootprints():
    if not inbox(fp.GetBoundingBox()): continue
    for p in fp.Pads():
        on = [L for L in order if p.IsOnLayer(LID[L])]
        if not on: continue
        ps = p.GetEffectivePolygon(pcbnew.F_Cu if 'F' in on else LID[on[0]], pcbnew.ERROR_INSIDE)
        col = '#ffffff' if p.GetNetname() in hl else ('#ff8080' if 'F' in on else COL[on[0]])
        o.append(f'<path d="{polypath(ps)}" fill="{col}" fill-opacity="0.55" stroke="#fff" stroke-width="0.5"/>')
    cy = fp.GetCourtyard(pcbnew.F_CrtYd)
    if cy.OutlineCount(): o.append(f'<path d="{polypath(cy)}" fill="none" stroke="#ff0" stroke-opacity="0.35" stroke-width="0.7"/>')
    pp = fp.GetPosition(); labels.append((X(pp.x), Y(pp.y), fp.GetReference(), '#ffff60'))
for v in b.GetTracks():
    if v.GetClass() == 'PCB_VIA' and inbox(v.GetBoundingBox()):
        r = mm(v.GetWidth(pcbnew.F_Cu))/2*S
        col = '#ffffff' if v.GetNetname() in hl else '#c0c0c0'
        o.append(f'<circle cx="{X(v.GetPosition().x):.1f}" cy="{Y(v.GetPosition().y):.1f}" r="{r:.1f}" fill="{col}" fill-opacity="0.8"/><circle cx="{X(v.GetPosition().x):.1f}" cy="{Y(v.GetPosition().y):.1f}" r="{mm(v.GetDrillValue())/2*S:.1f}" fill="#111"/>')
for x,y,t,c in labels:
    o.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{c}" font-size="{max(8,S*0.35):.0f}" font-family="Helvetica" text-anchor="middle">{html.escape(t)}</text>')
# grid
import math
for gx in range(math.ceil(a.x0), math.floor(a.x1)+1):
    o.append(f'<line x1="{(gx-a.x0)*S:.0f}" y1="0" x2="{(gx-a.x0)*S:.0f}" y2="{H:.0f}" stroke="#444" stroke-width="{2 if gx%5==0 else 0.4}"/>')
    if gx%5==0: o.append(f'<text x="{(gx-a.x0)*S+2:.0f}" y="12" fill="#888" font-size="11">{gx}</text>')
for gy in range(math.ceil(a.y0), math.floor(a.y1)+1):
    o.append(f'<line x1="0" y1="{(gy-a.y0)*S:.0f}" x2="{W:.0f}" y2="{(gy-a.y0)*S:.0f}" stroke="#444" stroke-width="{2 if gy%5==0 else 0.4}"/>')
    if gy%5==0: o.append(f'<text x="2" y="{(gy-a.y0)*S-2:.0f}" fill="#888" font-size="11">{gy}</text>')
o.append('</svg>')
svg = a.out.rsplit('.',1)[0]+'.svg'
open(svg,'w').write('\n'.join(o))
subprocess.run(['rsvg-convert', svg, '-o', a.out], check=True)
print(a.out)
