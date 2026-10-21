import sys, ed
E = ed.Editor(sys.argv[1])
E.set_pad_net('JP510', '1', 'CHG_SYS')
run = [t for t in E.items('CHG_BAT', 'In2.Cu', 'track') if t.GetWidth() == ed.MM(1.5)]
assert len(run) == 3, len(run)
ed.set_net(E, run, 'CHG_SYS')
E.remove(E.items('CHG_BAT', 'In2.Cu', 'track', near=(271.151, 145.031)), 'BAT In2 link to via 272.254 (JP510 now on SYS)')
for x, y in ((266.6, 145.75), (267.5, 146.159)):
    E.via((x, y), 'CHG_SYS', 0.8, 0.4)
    E.track((x, 145.031), (x, y), 1.0, 'In2.Cu', 'CHG_SYS')
E.save()
