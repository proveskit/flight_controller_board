import sys, ed
E = ed.Editor(sys.argv[1])
D = 'Net-(Q500-D-Pad5)'
E.remove(E.items(D, None, None, near=(202.9, 158.0)), 'via annulus touched Q501.5 pad edge (F16)')
E.via((202.9, 158.1), D)
E.track((202.9, 158.1), (203.3, 157.45), 0.6, 'F.Cu', D)
E.track((202.4, 157.0), (202.9, 158.1), 1.0, 'In1.Cu', D)
E.save()
