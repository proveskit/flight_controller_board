"""metrics4.py BOARD : item-4 design checks (GND via distance per charger cap GND pad, EP via count, hot-loop geometry)"""
import sys, math, pcbnew
T = pcbnew.ToMM
b = pcbnew.LoadBoard(sys.argv[1])
gv = [t for t in b.GetTracks() if t.GetClass() == 'PCB_VIA' and t.GetNetname() == 'GND']
for ref in ('C510', 'C511', 'C513', 'C514', 'C515', 'C517', 'C518'):
    f = b.FindFootprintByReference(ref)
    p = next(p for p in f.Pads() if p.GetNetname() == 'GND')
    poly = p.GetEffectivePolygon(pcbnew.F_Cu, pcbnew.ERROR_INSIDE)
    best = min(((T(math.sqrt(poly.SquaredDistance(v.GetPosition()))) - T(v.GetWidth(pcbnew.F_Cu)) / 2), v) for v in gv)
    q = best[1].GetPosition()
    print(f'{ref}.{p.GetNumber()} GND pad -> nearest GND via ({T(q.x):.2f},{T(q.y):.2f}) edge gap {max(best[0], 0):.2f} mm')
u = b.FindFootprintByReference('U511')
print('U511 EP PTH pads:', sum(1 for p in u.Pads() if p.GetNumber() == '25' and p.GetDrillSizeX() > 0))
c = b.FindFootprintByReference('C513')
p1 = next(p for p in c.Pads() if p.GetNumber() == '1'); p2 = next(p for p in c.Pads() if p.GetNumber() == '2')
pin = next(p for p in u.Pads() if p.GetNumber() == '15')
bb1 = p1.GetBoundingBox(); bbp = pin.GetBoundingBox()
print(f'SYS pins 15/16 outer end -> C513.1 pad edge: {T(bb1.GetLeft() - bbp.GetRight()):.2f} mm (F.Cu, 0.7 mm neck)')
q1, q2 = p1.GetPosition(), p2.GetPosition()
print(f'C513 pad1 ({T(q1.x):.2f},{T(q1.y):.2f}) pad2 ({T(q2.x):.2f},{T(q2.y):.2f})')
