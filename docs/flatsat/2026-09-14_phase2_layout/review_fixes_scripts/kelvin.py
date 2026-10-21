"""kelvin.py BOARD : remove the Kelvin stub at Q500 S pad 2 in memory and report VBAT_BENCH_N clusters (expect 2: heavy + sense)"""
import sys, pcbnew, ed
E = ed.Editor(sys.argv[1])
stub = E.items('VBAT_BENCH_N', 'F.Cu', 'track', near=(188.35, 154.8))
print('stub', [E.desc(t) for t in stub])
for t in stub: E.b.Remove(t)
pcbnew.ZONE_FILLER(E.b).Fill(E.b.Zones())
E.b.BuildConnectivity()
c = E.b.GetConnectivity()
net = E.net('VBAT_BENCH_N').GetNetCode()
pads = [p for f in E.b.GetFootprints() for p in f.Pads() if p.GetNetCode() == net]
groups = {}
for p in pads:
    items = c.GetConnectedItems(p)
    key = min([p.m_Uuid.AsString()] + [i.m_Uuid.AsString() for i in items])
    groups.setdefault(key, []).append(f'{p.GetParentFootprint().GetReference()}.{p.GetNumber()}')
for g in groups.values(): print('cluster', sorted(set(g)))
