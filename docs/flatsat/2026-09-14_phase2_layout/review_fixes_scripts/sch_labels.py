"""sch_labels.py SHEET NAME:x,y [NAME:x,y ...] : add local labels (idempotent per name)"""
import sys, uuid
p = sys.argv[1]
s = open(p).read()
add = ''
for spec in sys.argv[2:]:
    name, xy = spec.split(':')
    x, y = xy.split(',')
    if f'(label "{name}"' in s:
        print('exists', name); continue
    add += (f'\t(label "{name}"\n\t\t(at {x} {y} 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
            f'\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
i = s.index('\t(wire\n')
open(p, 'w').write(s[:i] + add + s[i:])
print('ok')
