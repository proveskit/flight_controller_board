"""Review-2 item 2: F.SilkS '8.4V MAX' under J500, same size/stroke/row as the J400/J401 '18V MAX' legends.
Refuses to save if the text box touches any pad (with 0.2 mm margin) or another F.SilkS text."""
import sys, pcbnew, ed
T = pcbnew.ToMM
E = ed.Editor(sys.argv[1])
ref = [d for d in E.b.GetDrawings() if d.GetClass() == 'PCB_TEXT' and d.GetText() == '18V MAX']
assert len(ref) == 2
if any(d.GetClass() == 'PCB_TEXT' and d.GetText() == '8.4V MAX' for d in E.b.GetDrawings()):
    sys.exit('already present')
t = E.text('8.4V MAX', (208.0, 171.2), h=1.0, stroke=0.15)
t.SetHorizJustify(ref[0].GetHorizJustify()); t.SetVertJustify(ref[0].GetVertJustify())
bb = t.GetBoundingBox(); bb.Inflate(pcbnew.FromMM(0.2))
print('8.4V MAX box', [round(T(v), 3) for v in (bb.GetLeft(), bb.GetTop(), bb.GetRight(), bb.GetBottom())])
hits = [f'{f.GetReference()}.{p.GetNumber()}' for f in E.b.GetFootprints() for p in f.Pads() if bb.Intersects(p.GetBoundingBox())]
hits += [d.GetText() for d in E.b.GetDrawings() if d.GetClass() == 'PCB_TEXT' and d.GetText() != '8.4V MAX' and bb.Intersects(d.GetBoundingBox())]
f = E.fp('J500'); cy = f.GetCourtyard(pcbnew.F_CrtYd).BBox()
print('J500 courtyard', [round(T(v), 3) for v in (cy.GetLeft(), cy.GetTop(), cy.GetRight(), cy.GetBottom())])
assert not hits, hits
E.save()
