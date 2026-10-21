import sys, ed
E = ed.Editor(sys.argv[1])
t, = E.items('CHG_SYS', 'In2.Cu', 'track', near=(271.151, 145.031))
ed.set_end(E, t, 'end' if abs(ed.T(t.GetEnd().x) - 271.151) < 0.01 else 'start', (267.5, 145.031))
E.save()
