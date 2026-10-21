"""Review-2 sheet notes (items 2, 3, 6). Each op is idempotent: an appended pointer or a note line already
present is skipped, so a rerun converges to the same files.
  sch_review2.py PROJECT_DIR"""
import re, sys, uuid
D = sys.argv[1]
esc = lambda t: t.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def note(x, y, text, size=1.27, just='left bottom'):
    return (f'\t(text "{esc(text)}"\n\t\t(exclude_from_sim no)\n\t\t(at {x} {y} 0)\n\t\t(effects\n\t\t\t(font\n'
            f'\t\t\t\t(size {size} {size})\n\t\t\t)\n\t\t\t(justify {just})\n\t\t)\n\t\t(uuid "{uuid.uuid4()}")\n\t)\n')


def append_to(s, prefix, tail):
    hits = [m for m in re.finditer(r'\(text "((?:[^"\\]|\\.)*)"', s) if m.group(1).startswith(esc(prefix))]
    assert len(hits) == 1, (prefix, len(hits))
    m = hits[0]
    if m.group(1).endswith(esc(tail)):
        return s
    return s[:m.end(1)] + esc(tail) + s[m.end(1):]


def add_block(s, x, y0, lines, **kw):
    out = ''
    for i, t in enumerate(lines):
        if t and f'(text "{esc(t)}"' not in s:
            out += note(x, round(y0 + 3.81 * i, 2), t, **kw)
    i = s.index('\t(wire\n')
    return s[:i] + out + s[i:]


OVP = ['J500 OVER-VOLTAGE (no OV element on J500 this rev; legend 8.4V MAX on the board):',
       '  PSU OVP <= 9 V; verify the trip with J500 disconnected before each session;',
       '  never use the 12-18 V VSOLAR supply on J500 (heritage C42/C1/C3 are 10 V',
       '  rated, U500 VDD abs max 12 V).']
MODE2 = ['MODE 2 returns through board GND: the ISS inhibit (J15/J19/JP607) and the R5460',
         '  replica are NOT in circuit; JP607 is needed in Mode 1 only; safe the bus with',
         '  JP606/RBF; run ISS-inhibit, deployment-switch and protection-trip tests in',
         '  Mode 1 only.']
GATES = ['GATE-DRIVE PROBING (TP501-TP504):',
         '  TP501/TP503 are referenced to VBAT_BENCH_N and TP502/TP504 to B-, not GND.',
         '  Measure gate drive with a floating DMM, a differential probe or an isolated',
         '  scope; or clip the scope ground to board GND (JP607.2) with JP607 closed and',
         '  read gates relative to TP501/TP502 by subtraction.  Never earth TP501 or J500.3',
         '  while J701 or FC USB is on an earthed host.']

p = f'{D}/battery_protection_replica.kicad_sch'
s = open(p).read()
s = append_to(s, 'BENCH PSU WINDOW:', '  PSU OVP <= 9 V: see J500 OVER-VOLTAGE, right.')
s = append_to(s, '  Mode 2  USB charger', '  See MODE 2 note, right.')
s = add_block(s, 205, 248.25, OVP + [''] + MODE2)
s = add_block(s, 142.24, 102.87, GATES)
open(p, 'w').write(s)

p = f'{D}/pyro_inhibit.kicad_sch'
s = open(p).read()
old = 'JP607 (B- return) + JP606'
new = 'JP607 (B- return; Mode 1 only, see right) + JP606'
if new not in s:
    assert s.count(old) == 1
    s = s.replace(old, new)
PY = ['MODE 2 (battery sheet: USB charger via JP510) returns through board GND: the ISS inhibit',
      '(J15/J19/JP607) and the R5460 replica are NOT in circuit; JP607 is needed in Mode 1 only;',
      'safe the bus with JP606/RBF; run ISS-inhibit, deployment-switch and protection-trip tests',
      'in Mode 1 only.']
if f'(text "{esc(PY[0])}' not in s:
    i = s.index('\t(wire\n')
    s = s[:i] + note(107.95, 265.43, '\n'.join(PY), size=1.0, just='left top') + s[i:]
open(p, 'w').write(s)
print('ok')
