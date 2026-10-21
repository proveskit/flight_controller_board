import sys, ed
E = ed.Editor(sys.argv[1])
for x in (233.0, 245.5):
    E.text('18V MAX', (x, 171.2), h=1.0, stroke=0.15)
E.save()
