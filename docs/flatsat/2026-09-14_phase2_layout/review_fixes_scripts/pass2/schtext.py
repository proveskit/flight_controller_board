"""Edit schematic text notes in place.
  schtext.py SHEET replace OLD_SUBSTRING NEW_FULL_TEXT     (exactly one (text "...") must contain OLD_SUBSTRING)
  schtext.py SHEET append X Y TEXT                          (new note, 1.27 mm, left bottom, before the first wire)
"""
import re, sys, uuid

path, op = sys.argv[1], sys.argv[2]
s = open(path).read()
esc = lambda t: t.replace('\\', '\\\\').replace('"', '\\"')
if op == 'replace':
    old, new = sys.argv[3], sys.argv[4]
    hits = [m for m in re.finditer(r'\(text "((?:[^"\\]|\\.)*)"', s) if old in m.group(1)]
    assert len(hits) == 1, f'{len(hits)} notes contain {old!r}'
    m = hits[0]
    s = s[:m.start(1)] + esc(new) + s[m.end(1):]
elif op == 'append':
    x, y, text = sys.argv[3], sys.argv[4], sys.argv[5]
    assert esc(text) not in s, 'note already present'
    block = (f'\t(text "{esc(text)}"\n\t\t(exclude_from_sim no)\n\t\t(at {x} {y} 0)\n\t\t(effects\n\t\t\t(font\n'
             f'\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify left bottom)\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')
    i = s.index('\t(wire\n')
    s = s[:i] + block + s[i:]
else:
    sys.exit('op?')
open(path, 'w').write(s)
print('ok', op)
