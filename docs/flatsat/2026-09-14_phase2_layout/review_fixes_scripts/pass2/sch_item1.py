import re, uuid, sys
p = sys.argv[1]
s = open(p).read()
old = re.search(r'\t\(wire\n\t\t\(pts\n\t\t\t\(xy 342\.9 101\.6\) \(xy 350\.52 101\.6\)\n\t\t\)', s)
assert old, 'wire not found'
s = s[:old.start()] + old.group(0).replace('(xy 350.52 101.6)', '(xy 347.98 101.6)') + s[old.end():]
j = re.search(r'\t\(junction\n\t\t\(at 347\.98 101\.6\)\n.*?\n\t\)\n', s, re.S)
assert j and j.group(0).count('(junction') == 1
s = s[:j.start()] + s[j.end():]
add = (f'\t(wire\n\t\t(pts\n\t\t\t(xy 350.52 101.6) (xy 350.52 97.79)\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n'
       f'\t(label "CHG_SYS"\n\t\t(at 350.52 97.79 90)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
i = s.index('\t(wire\n')
s = s[:i] + add + s[i:]
rep = [('"Test point, BQ25886 BAT (charger output, before JP510)"', '"Test point, BQ25886 BAT (CBAT C515 only; JP510 is fed from SYS)"'),
       ('"2-pin header, shunt REMOVED by default (D3): charger BAT -> Dir_Chrg_In"', '"2-pin header, shunt REMOVED by default (D3): charger SYS -> Dir_Chrg_In"')]
for a, b in rep:
    assert s.count(a) == 1, a
    s = s.replace(a, b)
open(p, 'w').write(s)
print('ok')
