import sys, ed
E = ed.Editor(sys.argv[1])
E.remove(E.items('GND', 'F.Cu', 'track', near=(278.0, 150.45)), 'PGND bridge: endpoint between pins was dangling')
E.remove(E.items('GND', 'F.Cu', 'track', near=(277.75, 150.238)), 'redundant dogbone leg 0.225 mm from PMID pin 21 (BenchPower 0.25)')
E.track((278.25, 150.45), (278.0, 151.0), 0.25, 'F.Cu', 'GND')
E.track((277.85, 150.45), (277.95, 151.0), 0.25, 'F.Cu', 'GND')
E.save()
