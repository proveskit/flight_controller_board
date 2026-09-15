#!/usr/bin/env python3
"""Generate FlatSat_V1/battery_protection_replica.kicad_sch ("Battery Replica and Bench Power").

PROVES FlatSat V1, Phase 1 schematic capture (docs/flatsat/2026-09-14_phase1_schematic/00_pm_brief.md
section 6.4).  Two blocks on one A3 sheet:

  A  bench PSU 3-way screw terminal (B+/MID/B-) -> exact replica of the battery_pack_v2 protection
     stage (R5460N208AA + 2x IRF7458 + the pack's R/C network) with a synthetic 2 x 1.0k cell
     midpoint; output B+ -> Dir_Chrg_In, cell-negative -> Q500 -> Q501 -> B-.
  B  power-only USB-C -> debug_board_v1 reverse-blocking stage (DZDH0401DW-7 + DMP4047LFDE-7) ->
     BQ25886RGE 2-cell charger -> 2-pin jumper (shunt removed by default) -> Dir_Chrg_In.

Everything is emitted from the pantry lib_symbols blocks; every wire endpoint is computed from the
library pin coordinates with the same transform tools/sch_lint.py uses.  Written atomically.

Usage:  python3 tools/gen/battery_protection_replica_gen.py [--out PATH]
"""
import argparse
import math
import os
import random
import re
import sys
import uuid as uuidlib

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
# Checked-in symbol pantry (tools/pantry); $FLATSAT_PANTRY overrides it.  Never a
# session scratch path: the generator must run from a clean checkout (review fix 13).
PANTRY = os.environ.get('FLATSAT_PANTRY', os.path.join(HERE, '..', 'pantry'))

ROOT_UUID = 'c64c0d72-a9f6-4f3a-891e-1f647558f538'
SHEET_SYM_UUID = 'bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0'
SHEET_FILE_UUID = '3f1c9d64-17ab-4c2e-9b55-0d7a4e6c81b2'   # this file's own uuid (fresh uuid4)
INST_PATH = '/%s/%s' % (ROOT_UUID, SHEET_SYM_UUID)
PROJECT = 'FlatSat_V1'

# deterministic uuid4 stream so re-running the generator does not churn the file
_rng = random.Random('flatsat-battery_protection_replica-2026-09-14')


def U():
    return str(uuidlib.UUID(int=_rng.getrandbits(128), version=4))


# --------------------------------------------------------------------------- pantry / lib symbols
def pantry_file(lib_id):
    return os.path.join(PANTRY, re.sub(r'[:/ ()]', '_', lib_id) + '.sexp')


_LIB_TEXT = {}
_LIB_PINS = {}


def _parse(text):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for t in toks:
        if t == '(':
            stack.append([])
        elif t == ')':
            node = stack.pop()
            stack[-1].append(node)
        else:
            if t.startswith('"') and t.endswith('"'):
                t = t[1:-1]
            stack[-1].append(t)
    return stack[0]


def _children(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]


def _child(node, name):
    c = _children(node, name)
    return c[0] if c else None


def load_lib(lib_id):
    """Read one pantry block; cache its text and its pin table."""
    if lib_id in _LIB_TEXT:
        return
    path = pantry_file(lib_id)
    with open(path, encoding='utf-8') as fh:
        text = fh.read().rstrip('\n')
    _LIB_TEXT[lib_id] = text
    sym = _parse(text)[0]
    assert sym[1] == lib_id, '%s defines %s' % (path, sym[1])
    pins = []          # (number, name, x, y)
    for sub in _children(sym, 'symbol'):
        for p in _children(sub, 'pin'):
            at = _child(p, 'at')
            num = _child(p, 'number')[1]
            nam = _child(p, 'name')[1]
            pins.append((num, nam, float(at[1]), float(at[2])))
    _LIB_PINS[lib_id] = pins


def pin_xy(lib_id, key, at, rot, mirror):
    """Schematic coordinate of a library pin, by pin number or pin name."""
    for (num, nam, px, py) in _LIB_PINS[lib_id]:
        if num == key or nam == key:
            x, y = px, -py
            if mirror == 'x':
                y = -y
            elif mirror == 'y':
                x = -x
            r = math.radians(rot)
            xr = x * math.cos(r) + y * math.sin(r)
            yr = -x * math.sin(r) + y * math.cos(r)
            return (round(at[0] + xr, 2), round(at[1] + yr, 2))
    raise KeyError('%s has no pin %r' % (lib_id, key))


# --------------------------------------------------------------------------- emitters
ITEMS = []
USED_LIBS = []
REFS = []


def n(v):
    s = ('%.4f' % float(v)).rstrip('0').rstrip('.')
    return s if s not in ('-0', '') else '0'


def eff(size=1.27, justify=None, extra=''):
    j = '\n\t\t\t(justify %s)' % justify if justify else ''
    return ('(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)\n\t\t\t)%s%s\n\t\t)' %
            (n(size), n(size), j, extra))


def wire(x1, y1, x2, y2):
    if (round(x1, 2), round(y1, 2)) == (round(x2, 2), round(y2, 2)):
        raise ValueError('zero-length wire at (%s, %s)' % (n(x1), n(y1)))
    ITEMS.append('\t(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n'
                 '\t\t\t(type default)\n\t\t)\n\t\t(uuid "%s")\n\t)' % (n(x1), n(y1), n(x2), n(y2), U()))


def poly(points):
    for i in range(len(points) - 1):
        wire(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])


def junction(x, y):
    ITEMS.append('\t(junction\n\t\t(at %s %s)\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "%s")\n\t)'
                 % (n(x), n(y), U()))


def no_connect(x, y):
    ITEMS.append('\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid "%s")\n\t)' % (n(x), n(y), U()))


def label(name, x, y, rot=0, justify='left bottom'):
    ITEMS.append('\t(label "%s"\n\t\t(at %s %s %s)\n\t\t%s\n\t\t(uuid "%s")\n\t)'
                 % (name, n(x), n(y), n(rot), eff(1.27, justify), U()))


def glabel(name, x, y, rot=0, shape='bidirectional', justify='left'):
    dx = -9.8 if 'right' in justify else 9.8
    ITEMS.append(
        '\t(global_label "%s"\n\t\t(shape %s)\n\t\t(at %s %s %s)\n\t\t(fields_autoplaced yes)\n\t\t%s\n'
        '\t\t(uuid "%s")\n\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"\n\t\t\t(at %s %s 0)\n'
        '\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t%s\n\t\t)\n\t)'
        % (name, shape, n(x), n(y), n(rot), eff(1.27, justify), U(), n(x + dx), n(y),
           eff(1.27, justify).replace('\n\t\t', '\n\t\t\t\t')))


def text(s, x, y, size=1.27):
    ITEMS.append('\t(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n\t\t%s\n\t\t(uuid "%s")\n\t)'
                 % (s.replace('"', '\\"'), n(x), n(y), eff(size, 'left'), U()))


def notes(lines, x, y, step=3.81, size=1.27):
    for i, ln in enumerate(lines):
        if ln:
            text(ln, x, y + i * step, size)


def prop(name, value, x, y, hide, size=1.27, justify=None, angle=0):
    h = '\n\t\t\t(hide yes)' if hide else ''
    return ('\t\t(property "%s" "%s"\n\t\t\t(at %s %s %s)%s\n\t\t\t(show_name no)\n'
            '\t\t\t(do_not_autoplace no)\n\t\t\t%s\n\t\t)'
            % (name, value.replace('"', '\\"'), n(x), n(y), n(angle), h,
               eff(size, justify).replace('\n\t\t', '\n\t\t\t')))


def place(lib_id, ref, value, at, rot=0, mirror=None, footprint='', datasheet='', description='',
          lcsc='', ref_at=None, val_at=None, justify='left', hide_value=False,
          val_justify=None, field_angle=None):
    """field_angle: stored angle of the Reference/Value fields.  KiCad's
    SCH_FIELD::GetDrawRotation() swaps horizontal<->vertical for a symbol whose transform is
    rotated 90/270, so a field on such a symbol needs the stored angle 90 to *render*
    horizontally.  Left at None it defaults to 90 for rot 90/270 and 0 otherwise, i.e.
    every Reference / Value on this sheet is drawn horizontally."""
    """Emit one symbol instance; return a callable giving pin coordinates."""
    load_lib(lib_id)
    if lib_id not in USED_LIBS:
        USED_LIBS.append(lib_id)
    if not ref.startswith('#'):
        REFS.append(ref)
    x, y = at
    ref_at = ref_at or (x + 2.54, y - 1.905)
    val_at = val_at or (x + 2.54, y + 1.905)
    if field_angle is None:
        field_angle = 90 if round(rot) % 180 == 90 else 0
    val_justify = val_justify or justify
    props = [prop('Reference', ref, ref_at[0], ref_at[1], ref.startswith('#'), 1.27, justify,
                  field_angle),
             prop('Value', value, val_at[0], val_at[1], hide_value, 1.27, val_justify,
                  field_angle),
             prop('Footprint', footprint, x, y, True),
             prop('Datasheet', datasheet, x, y, True),
             prop('Description', description, x, y, True)]
    if lcsc:
        props.append(prop('LCSC Part', lcsc, x, y, True))
    pinlines = ['\t\t(pin "%s"\n\t\t\t(uuid "%s")\n\t\t)' % (p[0], U()) for p in _LIB_PINS[lib_id]]
    mir = '\n\t\t(mirror %s)' % mirror if mirror else ''
    ITEMS.append(
        '\t(symbol\n\t\t(lib_id "%s")\n\t\t(at %s %s %s)%s\n\t\t(unit 1)\n\t\t(body_style 1)\n'
        '\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n'
        '\t\t(dnp no)\n\t\t(uuid "%s")\n%s\n%s\n\t\t(instances\n\t\t\t(project "%s"\n'
        '\t\t\t\t(path "%s"\n\t\t\t\t\t(reference "%s")\n\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n'
        '\t\t)\n\t)'
        % (lib_id, n(x), n(y), n(rot), mir, U(), '\n'.join(props), '\n'.join(pinlines),
           PROJECT, INST_PATH, ref))
    return lambda key: pin_xy(lib_id, key, (x, y), rot, mirror)


_PWR = [500]
_FLG = [500]


def gnd(x, y, ref=None):
    """ref: pin a specific #PWRnnn.  The review-round additions (2026-09-14) pass an explicit
    ref in the 590 block so that the #PWR500.. numbering of every pre-review ground stays
    put and the netlist diff shows only the parts that really changed."""
    if ref is None:
        ref = '#PWR%d' % _PWR[0]
        _PWR[0] += 1
    place('power:GND', ref, 'GND', (x, y), ref_at=(x, y + 6.35), val_at=(x, y + 3.81),
          hide_value=False)


def rail(lib_id, x, y, ref_hidden_value=None):
    r = '#PWR%d' % _PWR[0]
    _PWR[0] += 1
    place(lib_id, r, lib_id.split(':')[1], (x, y), ref_at=(x, y - 6.35), val_at=(x, y - 3.556))


def pwr_flag(x, y, rot=0, val_at=None, justify='left'):
    """PWR_FLAG.  The flag graphic sits *above* the pin at rot 0, so the wire must arrive
    from below; use rot=180 where the stub comes down from above.  val_at keeps the
    'PWR_FLAG' string off that stub."""
    r = '#FLG%d' % _FLG[0]
    _FLG[0] += 1
    place('power:PWR_FLAG', r, 'PWR_FLAG', (x, y), rot=rot, ref_at=(x, y + 1.905),
          val_at=val_at or (x, y - 3.81), justify=justify, field_angle=0)


# =============================================================================== sheet content
FP_R0603 = 'Resistor_SMD:R_0603_1608Metric'
FP_R0805 = 'Resistor_SMD:R_0805_2012Metric'
FP_R0402 = 'Resistor_SMD:R_0402_1005Metric'
FP_C0603 = 'Capacitor_SMD:C_0603_1608Metric'
FP_C0805 = 'Capacitor_SMD:C_0805_2012Metric'
FP_C1210 = 'Capacitor_SMD:C_1210_3225Metric'
FP_HDR2 = 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical'
FP_TP = 'TestPoint:TestPoint_Pad_D1.5mm'
DS_R5460 = 'https://www.nisshinbo-microdevices.co.jp/en/pdf/datasheet/r5460-ea.pdf'
DS_BQ = 'https://www.ti.com/lit/ds/symlink/bq25886.pdf'


def build():
    # ---------------------------------------------------------------- titles
    text('PROVES FlatSat V1 - Phase 1   |   Battery Replica and Bench Power', 15.24, 20.32, 3.175)
    notes(['Sheet 10 of FlatSat_V1.  Replica of battery_pack_v2 protection (brief 6.4 / D4) + the '
           'USB->BQ25886 bench charger (D3).  Refdes block 500-599.',
           'Both paths feed the FC net Dir_Chrg_In.  Nothing is added in series with the FC '
           'Dir_Chrg_In <-> VBATT_SENSE <-> inhibit chain.'], 15.24, 26.67)

    text('A.  BENCH PSU INPUT  +  battery_pack_v2 PROTECTION REPLICA  (D4)', 48.26, 44.45, 2.54)
    text('Bench PSU input + synthetic cell midpoint', 48.26, 50.8)
    text('R5460N208AA protection IC (= battery_pack_v2 U1)', 100.33, 50.8)
    text('Series protection FETs (battery_pack_v2 Q1/Q2), low side only', 76.2, 99.06)
    text('TEST POINTS', 53.34, 136.53)

    # ---------------------------------------------------------------- A1: terminal + divider
    j500 = place('Connector:Screw_Terminal_01x03', 'J500', 'BENCH PSU B+/MID/B-', (48.26, 60.96),
                 mirror='y',
                 footprint='TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_'
                           'P5.08mm_Horizontal',
                 datasheet='https://www.lcsc.com/product-detail/C72334.html', lcsc='C72334',
                 description='3-way 5.08mm screw terminal: bench battery PSU B+ / cell midpoint / B-',
                 ref_at=(41.91, 52.07), val_at=(41.91, 54.61), justify='right')
    bplus = j500('1')          # (53.34, 58.42)
    mid_t = j500('2')          # (53.34, 60.96)
    bminus = j500('3')         # (53.34, 63.50)

    # B+ node == Dir_Chrg_In (no series element: the pack's PACK+ is unswitched, protection is low side)
    wire(bplus[0], bplus[1], 63.5, 58.42)
    wire(63.5, 58.42, 76.2, 58.42)
    glabel('Dir_Chrg_In', 76.2, 58.42, 0, 'output')
    junction(63.5, 58.42)

    # JP500 sits at the TOP of the divider (Dir_Chrg_In -> R503), not at its midpoint, so
    # pulling the shunt genuinely disconnects the divider instead of leaving R503+R504
    # across B+/cell-negative (fix round 1, verifier finding 2).
    jp500 = place('Jumper:Jumper_2_Open', 'JP500', 'MID DIV - FIT', (63.5, 63.5), rot=90,
                  footprint=FP_HDR2,
                  datasheet='https://www.lcsc.com/product-detail/C358684.html', lcsc='C358684',
                  description='2-pin header, shunt FITTED by default: Dir_Chrg_In -> synthetic '
                              'midpoint divider.  Pull it when no bench PSU is fitted.',
                  ref_at=(71.12, 62.23), val_at=(71.12, 64.77), justify='right')
    assert jp500('B') == (63.5, 58.42)          # top pin lands on the B+ node
    wire(*(jp500('A') + (63.5, 71.12)))

    r503 = place('Device:R', 'R503', '1.0k 1%', (63.5, 74.93), footprint=FP_R0805,
                 lcsc='C17513',
                 description='Synthetic cell midpoint, upper half (B+ to MID)')
    assert r503('1') == (63.5, 71.12)
    junction(63.5, 78.74)

    # R504 sits at x=78.74 (2.54 left of the divider return) so that the VBAT_BENCH_N label
    # on C502's stub, which reaches back to x=81.02, clears its body (fix round 2, finding 3).
    r504 = place('Device:R', 'R504', '1.0k 1%', (78.74, 82.55), footprint=FP_R0805,
                 lcsc='C17513',
                 description='Synthetic cell midpoint, lower half (MID to cell negative)',
                 ref_at=(76.2, 80.645), val_at=(76.2, 83.185), justify='right')
    wire(63.5, 78.74, 78.74, 78.74)
    assert r504('1') == (78.74, 78.74)
    wire(*(r504('2') + (78.74, 92.71)))
    wire(78.74, 92.71, 86.36, 92.71)
    label('VBAT_BENCH_N', 86.36, 92.71)

    # MID_BENCH: terminal pin 2 + divider midpoint + hop to R501
    wire(63.5, 78.74, 63.5, 88.9)
    wire(mid_t[0], mid_t[1], 57.15, 60.96)
    wire(57.15, 60.96, 57.15, 88.9)
    wire(57.15, 88.9, 71.12, 88.9)
    junction(63.5, 88.9)
    label('MID_BENCH', 71.12, 88.9)

    # cell-negative from the terminal, with this sheet's PWR_FLAG
    wire(bminus[0], bminus[1], 53.34, 96.52)
    wire(53.34, 96.52, 68.58, 96.52)
    wire(43.18, 96.52, 53.34, 96.52)
    junction(53.34, 96.52)
    wire(43.18, 96.52, 43.18, 90.17)
    pwr_flag(43.18, 90.17, val_at=(50.8, 86.36), justify='right')
    label('VBAT_BENCH_N', 68.58, 96.52)

    # ---------------------------------------------------------------- A2: R5460 network
    u500 = place('flatsat:R5460N208AA', 'U500', 'R5460N208AA-TR-FE', (105.41, 66.04),
                 footprint='Package_TO_SOT_SMD:SOT-23-6', datasheet=DS_R5460, lcsc='C259714',
                 description='2-cell Li-ion protection IC, 4.250V/2.400V, SOT-23-6 '
                             '(battery_pack_v2 U1)',
                 ref_at=(110.49, 58.42), val_at=(110.49, 60.96))
    dout, cout, vminus = u500('DOUT'), u500('COUT'), u500('V-')
    vc, vdd, vss = u500('VC'), u500('VDD'), u500('VSS')

    wire(dout[0], dout[1], 99.06, 66.04)
    label('DOUT_GATE', 99.06, 66.04, 180, 'right bottom')
    wire(cout[0], cout[1], 99.06, 68.58)
    label('COUT_GATE', 99.06, 68.58, 180, 'right bottom')

    wire(vminus[0], vminus[1], 95.25, 71.12)
    junction(100.33, 71.12)
    c502 = place('Device:C', 'C502', '0.1uF', (95.25, 76.2), footprint=FP_C0603, lcsc='C14663',
                 description='R5460 V- filter (battery_pack_v2 C7), V- to cell negative',
                 ref_at=(92.71, 75.57), val_at=(92.71, 78.11), justify='right')
    wire(95.25, 71.12, *c502('1'))
    wire(*(c502('2') + (95.25, 83.82)))
    label('VBAT_BENCH_N', 95.25, 83.82, 180, 'right bottom')
    r502 = place('Device:R', 'R502', '1k', (100.33, 76.2), footprint=FP_R0603, lcsc='C21190',
                 description='R5460 V- series resistor to pack negative (battery_pack_v2 R3)')
    wire(100.33, 71.12, *r502('1'))
    wire(*(r502('2') + (100.33, 83.82)))
    glabel('B-', 100.33, 83.82, 0, 'passive')

    wire(vss[0], vss[1], 137.16, 66.04)
    label('VBAT_BENCH_N', 137.16, 66.04)

    # The VDD / VC columns sit 5.08 further right than battery_pack_v2 draws them, so that
    # C501's Reference/Value clear R501's body (fix round 2, finding 3).
    wire(vdd[0], vdd[1], 157.48, 68.58)
    junction(152.4, 68.58)
    r500 = place('Device:R', 'R500', '330', (157.48, 60.96), footprint=FP_R0603, lcsc='C23138',
                 description='R5460 VDD series resistor from pack + (battery_pack_v2 R5)')
    wire(157.48, 68.58, *r500('2'))
    wire(*(r500('1') + (157.48, 53.34)))
    glabel('Dir_Chrg_In', 157.48, 53.34, 0, 'input')
    c500 = place('Device:C', 'C500', '0.1uF', (152.4, 74.93), footprint=FP_C0603, lcsc='C14663',
                 description='R5460 VDD decoupling (battery_pack_v2 C9), VDD to cell negative')
    wire(152.4, 68.58, *c500('1'))
    wire(*(c500('2') + (152.4, 83.82)))
    label('VBAT_BENCH_N', 152.4, 83.82)

    wire(vc[0], vc[1], 147.32, 71.12)
    junction(137.16, 71.12)
    r501 = place('Device:R', 'R501', '330', (137.16, 76.2), footprint=FP_R0603, lcsc='C23138',
                 description='R5460 VC series resistor from cell midpoint (battery_pack_v2 R4)',
                 ref_at=(132.08, 74.93), val_at=(132.08, 77.47), justify='right')
    wire(137.16, 71.12, *r501('1'))
    wire(*(r501('2') + (137.16, 83.82)))
    label('MID_BENCH', 137.16, 83.82, 180, 'right bottom')
    c501 = place('Device:C', 'C501', '0.1uF', (147.32, 76.2), footprint=FP_C0603, lcsc='C14663',
                 description='R5460 VC decoupling (battery_pack_v2 C8), VC to cell negative',
                 ref_at=(144.78, 74.93), val_at=(144.78, 77.47), justify='right')
    wire(147.32, 71.12, *c501('1'))
    wire(*(c501('2') + (147.32, 88.9)))
    label('VBAT_BENCH_N', 147.32, 88.9)

    # ---------------------------------------------------------------- A3: protection FETs
    q500 = place('flatsat:IRF7458', 'Q500', 'IRF7458', (88.9, 106.68),
                 footprint='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
                 datasheet='https://www.lcsc.com/product-detail/C10879.html', lcsc='C10879',
                 description='N-ch 30V 9.7A SO-8, discharge FET driven by R5460 DOUT '
                             '(battery_pack_v2 Q1)',
                 ref_at=(83.82, 110.49), val_at=(83.82, 113.03), justify='right')
    q501 = place('flatsat:IRF7458', 'Q501', 'IRF7458', (127.0, 106.68),
                 footprint='Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
                 datasheet='https://www.lcsc.com/product-detail/C10879.html', lcsc='C10879',
                 description='N-ch 30V 9.7A SO-8, charge FET driven by R5460 COUT '
                             '(battery_pack_v2 Q2)',
                 ref_at=(121.92, 110.49), val_at=(121.92, 113.03), justify='right')
    wire(*(q500('D') + q501('D')))                       # common drain
    wire(q500('G')[0], q500('G')[1], 76.2, 106.68)
    label('DOUT_GATE', 76.2, 106.68, 180, 'right bottom')
    wire(q501('G')[0], q501('G')[1], 114.3, 106.68)
    label('COUT_GATE', 114.3, 106.68, 180, 'right bottom')

    c503 = place('Device:C', 'C503', '0.1uF', (110.49, 111.76), rot=90, footprint=FP_C0603,
                 lcsc='C14663',
                 description='Cell negative to pack negative (battery_pack_v2 C5; R5460 datasheet '
                             'C3, >= 0.01uF)',
                 ref_at=(104.14, 118.11), val_at=(112.39, 118.11))
    wire(q500('S')[0], q500('S')[1], *c503('1'))
    wire(*(c503('2') + q501('S')))
    junction(*q500('S'))
    junction(*q501('S'))
    wire(q500('S')[0], q500('S')[1], 91.44, 115.57)
    label('VBAT_BENCH_N', 91.44, 115.57)
    wire(q501('S')[0], q501('S')[1], 129.54, 115.57)
    glabel('B-', 129.54, 115.57, 0, 'output')

    # Bleed: gives VBAT_BENCH_N a defined potential when no PSU is plugged into J500 and both
    # protection FETs are off (fix round 1, verifier finding 2).  100k = 84 uA at 8.4 V.
    r505 = place('Device:R', 'R505', '100k', (110.49, 125.73), rot=90, footprint=FP_R0603,
                 lcsc='C25803',
                 description='Bleed, cell negative to pack negative: defines VBAT_BENCH_N when '
                             'J500 is open',
                 ref_at=(104.14, 121.92), val_at=(112.39, 121.92))
    wire(r505('1')[0], r505('1')[1], 100.33, 125.73)
    label('VBAT_BENCH_N', 100.33, 125.73, 180, 'right bottom')
    wire(r505('2')[0], r505('2')[1], 121.92, 125.73)
    glabel('B-', 121.92, 125.73, 0, 'passive')

    # ---------------------------------------------------------------- A4: test point cluster
    for i, (ref, net, kind) in enumerate([
            ('TP500', 'Dir_Chrg_In', 'g'), ('TP501', 'VBAT_BENCH_N', 'l'), ('TP502', 'B-', 'g'),
            ('TP503', 'DOUT_GATE', 'l'), ('TP504', 'COUT_GATE', 'l'), ('TP505', 'MID_BENCH', 'l')]):
        x = 53.34 + i * 19.05
        tp = place('Connector:TestPoint', ref, net, (x, 144.78), footprint=FP_TP,
                   description='Test point, %s' % net, hide_value=True,
                   ref_at=(x + 2.54, 142.24), val_at=(x + 2.54, 139.7))
        wire(tp('1')[0], tp('1')[1], x, 148.59)
        if kind == 'g':
            glabel(net, x, 148.59, 0, 'passive')
        else:
            label(net, x, 148.59)

    # ---------------------------------------------------------------- B: charger heading
    text('B.  USB-C -> BQ25886 BENCH CHARGER  (D3; from antenna-board/debug_board_v1, corrected)',
         200.66, 34.29, 2.54)
    text('USB-C, power only', 200.66, 40.64)
    text('Reverse blocking (debug_board_v1)', 251.46, 38.1)
    text('BQ25886RGE 2-cell charger', 292.1, 44.45)

    # B1: USB-C receptacle
    j510 = place('Connector:USB_C_Receptacle_USB2.0_16P', 'J510', 'USB-C CHARGER IN (power only)',
                 (210.82, 60.96),
                 footprint='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
                 datasheet='https://www.lcsc.com/product-detail/C165948.html', lcsc='C165948',
                 description='USB 2.0 Type-C receptacle, power only (no data), charger input',
                 ref_at=(198.12, 53.34), val_at=(198.12, 55.88), justify='right')
    vbus = j510('A4')
    wire(vbus[0], vbus[1], 236.22, 45.72)
    junction(231.14, 45.72)
    wire(231.14, 45.72, 231.14, 41.91)
    place('Connector:TestPoint', 'TP510', 'VBUS_CHG', (231.14, 41.91), footprint=FP_TP,
          description='Test point, charger USB VBUS', hide_value=True,
          ref_at=(228.6, 40.64), val_at=(228.6, 38.1), justify='right')
    wire(236.22, 45.72, 236.22, 41.91)
    rail('flatsat:VBUS_CHG', 236.22, 41.91)
    # VBUS_CHG PWR_FLAG (brief 4.2 ownership) - at the USB end, where there is room
    junction(236.22, 45.72)
    wire(236.22, 45.72, 243.84, 45.72)
    # value text below-left of the flag: to its right it would be drawn across the second
    # VBUS_CHG rail symbol at (254.0, 44.45)  (fix round 2, finding 3)
    pwr_flag(243.84, 45.72, val_at=(243.84, 47.0), justify='right')
    # CC pull-downs
    cc2 = j510('B5')
    wire(cc2[0], cc2[1], 228.6, 53.34)
    # R511's fields go above the pair: R510 sits 5.08 to the right, so fields beside R511
    # are drawn through R510's body (verifier fix round 2, finding 3).
    r511 = place('Device:R', 'R511', '5.1k', (228.6, 58.42), footprint=FP_R0402, lcsc='C25905',
                 description='USB-C CC2 pull-down (5.1k, UFP)',
                 ref_at=(225.42, 47.0), val_at=(225.42, 49.5))
    wire(228.6, 53.34, *r511('1'))
    wire(*(r511('2') + (228.6, 66.04)))
    gnd(228.6, 66.04)
    cc1 = j510('A5')
    wire(cc1[0], cc1[1], 233.68, 50.8)
    r510 = place('Device:R', 'R510', '5.1k', (233.68, 58.42), footprint=FP_R0402, lcsc='C25905',
                 description='USB-C CC1 pull-down (5.1k, UFP)',
                 ref_at=(238.76, 56.52), val_at=(238.76, 60.33))
    wire(233.68, 50.8, *r510('1'))
    wire(*(r510('2') + (233.68, 66.04)))
    gnd(233.68, 66.04)
    for pin in ('A6', 'A7', 'B6', 'B7', 'A8', 'B8'):
        no_connect(*j510(pin))
    wire(j510('A1')[0], j510('A1')[1], 210.82, 87.63)
    gnd(210.82, 87.63)
    wire(j510('S1')[0], j510('S1')[1], 203.2, 87.63)
    gnd(203.2, 87.63)

    # B2: reverse-blocking ideal diode
    q510 = place('easyeda2kicad:DMP4047LFDE-7', 'Q510', 'DMP4047LFDE-7', (254.0, 53.34),
                 footprint='easyeda2kicad:U-DFN2020-6E_L2.0-W2.0-P0.65-BL',
                 datasheet='https://www.lcsc.com/product-detail/C442635.html', lcsc='C442635',
                 description='P-ch MOSFET, input reverse-blocking pass FET (debug_board_v1 Q1)',
                 ref_at=(262.89, 61.0), val_at=(262.89, 63.54))
    wire(q510('D')[0], q510('D')[1], 254.0, 44.45)
    rail('flatsat:VBUS_CHG', 254.0, 44.45)
    junction(254.0, 48.26)
    wire(q510('G')[0], q510('G')[1], 243.84, 53.34)
    label('CHG_GATE', 243.84, 53.34, 180, 'right bottom')

    u510 = place('easyeda2kicad:DZDH0401DW-7', 'U510', 'DZDH0401DW-7', (254.0, 74.93),
                 footprint='easyeda2kicad:SOT-363_L2.0-W1.3-P0.65-LS2.1-BR',
                 datasheet='https://www.lcsc.com/product-detail/C3235552.html', lcsc='C3235552',
                 description='Ideal-diode / reverse-blocking controller for Q510 '
                             '(debug_board_v1 U2)',
                 ref_at=(241.3, 76.2), val_at=(241.3, 78.74), justify='right')
    wire(u510('DRAIN')[0], u510('DRAIN')[1], 248.92, 48.26)
    wire(248.92, 48.26, 254.0, 48.26)
    # source / Q510 source / DVIN node
    wire(*(q510('S') + (256.54, 58.42)))
    junction(256.54, 58.42)
    wire(256.54, 58.42, 259.08, 58.42)
    wire(259.08, 58.42, u510('SOURCE')[0], u510('SOURCE')[1])
    junction(259.08, 58.42)
    wire(259.08, 58.42, 274.32, 58.42)
    label('CHG_DVIN', 274.32, 58.42, 0, 'left top')
    junction(269.24, 58.42)
    wire(269.24, 58.42, 269.24, 52.07)
    pwr_flag(269.24, 52.07, val_at=(271.78, 50.8))
    wire(u510('REF')[0], u510('REF')[1], 248.92, 86.36)
    label('CHG_REF', 248.92, 86.36)
    wire(u510('BIAS')[0], u510('BIAS')[1], 259.08, 88.9)
    label('CHG_GATE', 259.08, 88.9)
    no_connect(*u510('1'))
    no_connect(*u510('5'))
    r512 = place('Device:R', 'R512', '1M', (243.84, 95.25), footprint=FP_R0603, lcsc='C22935',
                 description='Q510 gate pull-down (debug_board_v1 R1)')
    wire(243.84, 88.9, *r512('1'))
    label('CHG_GATE', 243.84, 88.9)
    wire(*(r512('2') + (243.84, 101.6)))
    gnd(243.84, 101.6)
    r513 = place('Device:R', 'R513', '1M', (269.24, 95.25), footprint=FP_R0603, lcsc='C22935',
                 description='DZDH0401DW REF resistor to GND (debug_board_v1 R2)')
    wire(269.24, 88.9, *r513('1'))
    label('CHG_REF', 269.24, 88.9)
    wire(*(r513('2') + (269.24, 101.6)))
    gnd(269.24, 101.6)

    # B3: BQ25886
    u511 = place('Battery_Management:BQ25886RGE', 'U511', 'BQ25886RGE', (309.88, 74.93),
                 footprint='Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm',
                 datasheet=DS_BQ, lcsc='C2765094',
                 description='2-cell 5V-input boost battery charger, 8.4V float (VSET open)',
                 ref_at=(302.26, 50.8), val_at=(302.26, 53.34))
    # VBUS + CVBUS
    wire(u511('VBUS')[0], u511('VBUS')[1], 287.02, 57.15)
    wire(287.02, 57.15, 281.94, 57.15)
    label('CHG_DVIN', 281.94, 57.15, 180, 'right bottom')
    junction(287.02, 57.15)
    c510 = place('Device:C', 'C510', '1uF', (287.02, 60.96), footprint=FP_C0805, lcsc='C28323',
                 description='CVBUS, charger input decoupling (datasheet 9.2.2)')
    wire(*(c510('2') + (287.02, 68.58)))
    gnd(287.02, 68.58)
    # D+/D- shorted at the IC = DCP signature to the BC1.2 detector
    poly([u511('D+'), (294.64, 62.23), (294.64, 64.77), u511('D-')])
    for pin in ('~{CE}', 'VSET', '~{PG}'):
        no_connect(*u511(pin))
    # Review fix 8 (2026-09-14): OTG tied low instead of left floating.  SLUSD88A pin table,
    # pin 5: "Pull low to disable OTG function" - and, unlike /CE (internal 900k pull-down),
    # no internal pull is documented for OTG.  Tied straight to GND, which is what TI's own
    # EVM jumper JP8 selects in charge mode.
    wire(u511('OTG')[0], u511('OTG')[1], 293.37, 69.85)
    wire(293.37, 69.85, 293.37, 73.66)
    gnd(293.37, 73.66, ref='#PWR590')
    # ILIM / ICHGSET
    wire(u511('ILIM')[0], u511('ILIM')[1], 289.56, 80.01)
    r514 = place('Device:R', 'R514', '750', (289.56, 85.09), footprint=FP_R0603,
                 lcsc='C23241',
                 description='ILIM: IINMAX = KILIM/RILIM = 1110/750 = 1.48A (datasheet 8.3.9)',
                 ref_at=(287.02, 83.82), val_at=(287.02, 86.36), justify='right')
    wire(289.56, 80.01, *r514('1'))
    wire(*(r514('2') + (289.56, 92.71)))
    gnd(289.56, 92.71)
    wire(u511('ICHGSET')[0], u511('ICHGSET')[1], 294.64, 85.09)
    r515 = place('Device:R', 'R515', '5.62k', (294.64, 90.17), footprint=FP_R0603,
                 lcsc='C23188',
                 datasheet='https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF5621T5E_C23188.pdf',
                 description='ICHGSET: ICHG = RICHGSET/KICHGSET = 5620/3810 = 1.475A '
                             '(datasheet 9.2.2.5). PM ruling S1: 5.62k 1% 0603 E96 '
                             '(was 5.7k, not an E24/E96 value).',
                 # val_at nudged 297.18 -> 296.2 (from 297.18): "5.62k" is one character wider than
                 # the old "5.7k" value, and at the default left-justify + size 1.27 that pushed the
                 # Value text's right edge into U511's body (x=302.26) -- textcheck.py flagged
                 # TEXT-ON-BODY.  The gap between R515's own body (ends x=295.66) and U511's body
                 # (starts x=302.26) is only 6.6 mm, tight for a 5-character value at this size, so
                 # this is centred in it rather than reusing the old left edge.
                 ref_at=(297.18, 87.63), val_at=(296.2, 90.17))
    wire(294.64, 85.09, *r515('1'))
    wire(*(r515('2') + (294.64, 97.79)))
    gnd(294.64, 97.79)
    # GND
    wire(u511('GND')[0], u511('GND')[1], 309.88, 101.6)
    gnd(309.88, 101.6)
    # STAT LED
    wire(u511('STAT')[0], u511('STAT')[1], 326.39, 57.15)
    d510 = place('Device:LED', 'D510', 'LED', (330.2, 57.15), footprint='LED_SMD:LED_0603_1608Metric',
                 lcsc='C2290', description='Charge status LED, lit while charging (STAT low)',
                 ref_at=(330.2, 52.07), val_at=(330.2, 54.61))
    r519 = place('Device:R', 'R519', '1k', (341.63, 57.15), rot=90, footprint=FP_R0603, lcsc='C21190',
                 description='STAT LED series resistor (~3mA from VBUS_CHG)',
                 ref_at=(337.82, 48.26), val_at=(345.44, 48.26))
    wire(*(d510('A') + r519('1')))
    wire(r519('2')[0], r519('2')[1], 353.06, 57.15)
    wire(353.06, 57.15, 353.06, 53.34)
    rail('flatsat:VBUS_CHG', 353.06, 53.34)
    # PMID -> L -> SW
    wire(u511('PMID')[0], u511('PMID')[1], 355.6, 64.77)
    l510 = place('easyeda2kicad:SPM6530T-4R7M-HZ', 'L510', 'SPM6530T-1R0M120', (355.6, 68.58), rot=90,
                 footprint='easyeda2kicad:IND-SMD_L7.1-W6.5-P5.60',
                 datasheet='https://www.lcsc.com/product-detail/C87572.html', lcsc='C87572',
                 description='1.0uH 6.5x6.5mm power inductor, BQ25886 boost (datasheet 9.2.2.2)',
                 ref_at=(351.79, 59.69), val_at=(351.79, 62.23), justify='right')
    wire(355.6, 64.77, *l510('2'))
    junction(355.6, 64.77)
    wire(355.6, 64.77, 360.68, 64.77)
    # Review fix 9 (2026-09-14): 10uF 0805 keeps only 6.7uF at the 5V PMID bias, under the
    # datasheet's "minimum 10uF" (which 9.2.2.2 states after derating).  22uF 25V X5R 1210
    # keeps 19.0uF at 5V on the KEMET/YAGEO K-SIM curve for C1210C226K3PAC.
    c511 = place('Device:C', 'C511', '22uF 25V', (360.68, 68.58), footprint=FP_C1210,
                 lcsc='C52306',
                 description='CPMID, 22uF 25V X5R 1210 = 19.0uF at the 5V PMID bias '
                             '(K-SIM C1210C226K3PAC DC-bias curve); datasheet 9.2.2.2 asks for '
                             '10uF after derating, 44uF optimal')
    # ground stub one grid step shorter than before so the "GND" field clears the CHG_SYS
    # rail, which now runs on to C517/C518 at x=368.3/381.0
    wire(*(c511('2') + (360.68, 74.93)))
    gnd(360.68, 74.93)
    wire(u511('SW')[0], u511('SW')[1], 330.2, 69.85)
    wire(330.2, 69.85, 350.52, 69.85)
    junction(330.2, 69.85)
    poly([(350.52, 69.85), (350.52, 73.66), l510('1')])
    junction(340.36, 69.85)
    wire(340.36, 69.85, 340.36, 74.93)
    pwr_flag(340.36, 74.93, rot=180, val_at=(342.9, 76.2), justify='right')
    c512 = place('Device:C', 'C512', '47nF', (330.2, 73.66), footprint=FP_C0603,
                 lcsc='C1622',
                 description='CBTST bootstrap capacitor (datasheet 9.2.2)',
                 ref_at=(332.74, 72.39), val_at=(332.74, 74.93))
    poly([u511('BTST'), (325.12, 74.93), (325.12, 77.47), c512('2')])
    # SYS  (local label CHG_SYS so the net has the name the sheet and the report print)
    wire(u511('SYS')[0], u511('SYS')[1], 323.85, 80.01)
    wire(323.85, 80.01, 337.82, 80.01)
    wire(337.82, 80.01, 345.44, 80.01)
    wire(345.44, 80.01, 355.6, 80.01)
    label('CHG_SYS', 323.85, 80.01)
    junction(337.82, 80.01)
    junction(345.44, 80.01)
    wire(337.82, 80.01, 337.82, 83.82)
    place('Connector:TestPoint', 'TP511', 'CHG_SYS', (337.82, 83.82), rot=180, footprint=FP_TP,
          description='Test point, BQ25886 SYS', hide_value=True,
          ref_at=(344.17, 78.74), val_at=(344.17, 76.2))
    # Review fix 1 / PM ruling R5 (2026-09-14).  CSYS must be >= 44uF *after* DC-bias derating
    # at the 8.4V SYS bias (SLUSD88A 9.2.2.3).  Derating is read off the manufacturer curve
    # KEMET/YAGEO K-SIM gives for C1210C226K3PAC (22uF 25V X5R 1210, the same C/V/dielectric/
    # case as the fitted Samsung CL32A226KAJNNNE): -41.9% at 8.4V, i.e. 12.8uF per part.
    #   4 x 12.8uF = 51.1uF effective  >= 44uF.
    # The same tool on 10uF 25V X5R shows the case-size trend that rules the smaller options
    # out: -60.0% in 0805, -39.0% in 1206, -19.1% in 1210 at 8.4V.  So the 2 x 22uF 0805 this
    # sheet carried before the review held under 18uF, and 3 x 22uF 1206 would not reach 44uF
    # either - hence four 1210 parts rather than the brief's "add a third 22uF".
    csys = []
    for ref, x, ref_at, val_at, just in [
            ('C513', 345.44, (344.17, 86.36), (344.17, 88.9), 'right'),
            ('C514', 355.6, (358.14, 86.36), (358.14, 88.9), 'left'),
            ('C517', 368.3, (370.84, 86.36), (370.84, 88.9), 'left'),
            ('C518', 381.0, (383.54, 86.36), (383.54, 88.9), 'left')]:
        c = place('Device:C', ref, '22uF 25V', (x, 83.82), footprint=FP_C1210, lcsc='C52306',
                  description='CSYS %s of 4, 22uF 25V X5R 1210 = 12.8uF at the 8.4V SYS bias '
                              '(K-SIM C1210C226K3PAC DC-bias curve); 4 x 12.8 = 51uF vs the '
                              '44uF minimum of datasheet 9.2.2.3'
                              % (['C513', 'C514', 'C517', 'C518'].index(ref) + 1),
                  ref_at=ref_at, val_at=val_at, justify=just)
        csys.append(c)
    # SYS rail carried on to the two added capacitors
    junction(355.6, 80.01)
    wire(355.6, 80.01, 368.3, 80.01)
    junction(368.3, 80.01)
    wire(368.3, 80.01, 381.0, 80.01)
    for c, x, ref in zip(csys, (345.44, 355.6, 368.3, 381.0),
                         (None, None, '#PWR591', '#PWR592')):
        wire(*(c('2') + (x, 91.44)))
        gnd(x, 91.44, ref=ref)
    # BAT -> jumper -> Dir_Chrg_In   (local label CHG_BAT, isolated from Dir_Chrg_In by JP510)
    poly([u511('BAT'), (332.74, 82.55), (332.74, 99.06), (332.74, 101.6), (342.9, 101.6),
          (350.52, 101.6)])
    label('CHG_BAT', 332.74, 99.06)
    junction(342.9, 101.6)
    junction(347.98, 101.6)
    # Review fix 9 (2026-09-14): a 10uF 25V X5R 0805 keeps only 4.0uF at the 8.4V BAT bias
    # (K-SIM C0805C106K3PAC), far under the pin table's "10uF after derating".  22uF 25V X5R
    # 1210 keeps 12.8uF at 8.4V - same part as the CSYS bank, so one BOM line.
    c515 = place('Device:C', 'C515', '22uF 25V', (342.9, 105.41), footprint=FP_C1210,
                 lcsc='C52306',
                 description='CBAT, 22uF 25V X5R 1210 = 12.8uF at the 8.4V BAT bias '
                             '(K-SIM C1210C226K3PAC DC-bias curve), over the 10uF '
                             'after-derating minimum of the SLUSD88A pin table',
                 ref_at=(340.36, 103.505), val_at=(340.36, 105.41), justify='right')
    wire(*(c515('2') + (342.9, 113.03)))
    gnd(342.9, 113.03)
    wire(347.98, 101.6, 347.98, 105.41)
    place('Connector:TestPoint', 'TP512', 'CHG_BAT', (347.98, 105.41), rot=180, footprint=FP_TP,
          description='Test point, BQ25886 BAT (charger output, before JP510)', hide_value=True,
          ref_at=(350.52, 107.95), val_at=(350.52, 110.49))
    jp510 = place('Jumper:Jumper_2_Open', 'JP510', 'CHG OUT - OPEN', (355.6, 101.6),
                  footprint=FP_HDR2,
                  datasheet='https://www.lcsc.com/product-detail/C358684.html', lcsc='C358684',
                  description='2-pin header, shunt REMOVED by default (D3): charger BAT -> '
                              'Dir_Chrg_In',
                  ref_at=(360.68, 96.52), val_at=(360.68, 99.06))
    wire(jp510('B')[0], jp510('B')[1], 365.76, 101.6)
    glabel('Dir_Chrg_In', 365.76, 101.6, 0, 'output')
    # REGN
    poly([u511('REGN'), (327.66, 87.63), (327.66, 106.68)])
    junction(327.66, 106.68)
    wire(327.66, 106.68, 337.82, 106.68)
    c516 = place('Device:C', 'C516', '4.7uF', (337.82, 110.49), footprint=FP_C0603,
                 lcsc='C19666',
                 description='CREGN LDO decoupling (datasheet 9.2.2)',
                 ref_at=(335.28, 108.585), val_at=(335.28, 111.125), justify='right')
    wire(*(c516('2') + (337.82, 118.11)))
    gnd(337.82, 118.11)
    r516 = place('Device:R', 'R516', '5.23k', (327.66, 114.3), footprint=FP_R0603,
                 lcsc='C23068',
                 description='TS RT1, REGN to TS (datasheet 8.3.7.4.1, RT1 = 5.24k)',
                 ref_at=(330.2, 119.38), val_at=(330.2, 121.92))
    wire(327.66, 106.68, *r516('1'))
    wire(*(r516('2') + (322.58, 118.11)))
    # TS
    poly([u511('TS'), (322.58, 92.71), (322.58, 118.11)])
    junction(322.58, 118.11)
    r517 = place('Device:R', 'R517', '30.1k', (322.58, 125.73), footprint=FP_R0603,
                 lcsc='C23000',
                 description='TS RT2, TS to GND (datasheet 8.3.7.4.1, RT2 = 30.31k)')
    wire(322.58, 118.11, *r517('1'))
    wire(*(r517('2') + (322.58, 133.35)))
    gnd(322.58, 133.35)
    wire(322.58, 118.11, 314.96, 118.11)
    r518 = place('Device:R', 'R518', '10k', (314.96, 125.73), footprint=FP_R0603, lcsc='C25804',
                 description='Stands in for the pack 103AT NTC at 25C, TS to GND',
                 ref_at=(312.42, 124.46), val_at=(312.42, 127.0), justify='right')
    wire(314.96, 118.11, *r518('1'))
    wire(*(r518('2') + (314.96, 133.35)))
    gnd(314.96, 133.35)

    # ---------------------------------------------------------------- notes
    notes([
        'NET NAMES ON THIS SHEET (brief 6.4 net-name rule)',
        '  VBAT_BENCH_N (local) = the pack cell-negative node: R5460 VSS, Q500 source, C500/C501/'
        'C502/C503 return, R504 bottom.',
        '  It is NOT the FC global B-.  B- = pack negative = Q501 source = J14 pins 2/4/6/8, and '
        'reaches GND only through the ISS inhibit J15/J19.',
        '  B+ has no series element: the positive path of the pack is unswitched, so the bench PSU '
        'B+ terminal IS the FC net Dir_Chrg_In.',
        '  Nothing on this sheet is in series with the FC Dir_Chrg_In <-> VBATT_SENSE <-> inhibit '
        'chain (brief hard rule 6).',
        '',
        'JUMPERS AND BENCH MODES',
        '  JP500  Dir_Chrg_In -> top of the R503/R504 divider : shunt FITTED by default, and '
        'fitted ONLY while a bench PSU is connected to J500.',
        '         Pulling it disconnects the whole divider (no 4.2 mA path from Dir_Chrg_In to the '
        'cell-negative node) and lets a real 2-cell dual',
        '         supply on J500 pin 2 (MID) set VC on its own.  Open-header symbol: the two nets '
        'stay separate in the netlist (brief rule 9).',
        '  JP510  BQ25886 BAT -> Dir_Chrg_In    : shunt REMOVED by default (D3), so the charger can '
        'never push into a bench PSU.',
        # Review fix 5 (2026-09-14): modes 2 and 3 now state JP500 explicitly.  The PSU-window
        # warning below ("PULL JP500 WHENEVER NO BENCH PSU IS CONNECTED") and the sheet report
        # both require it open in those modes; leaving it out of the table let a technician
        # follow the table alone and keep JP500 fitted with no PSU on J500.
        '  Mode 1  PSU through the replica : JP500 fitted, JP510 open, charger USB unplugged.',
        '  Mode 2  USB charger             : JP500 OPEN, JP510 fitted, bench PSU disconnected '
        'at J500.',
        '  Mode 3  both off                : JP500 OPEN, JP510 open, bench PSU disconnected.',
        '',
        'BENCH PSU WINDOW:  4.9 V <= V(B+ - B-) <= 8.4 V,  current limit <= 2 A,  FLOATING output.',
        '  R5460N208AA-TR-FE (datasheet product-code table): over-charge VDET1 4.250 V/cell = 8.50 V '
        'pack, tVDET1 1 s -> COUT opens (charge blocked);',
        '  over-discharge VDET2 2.400 V/cell = 4.80 V pack, tVDET2 128 ms -> DOUT opens, and only '
        'releases above VREL2 3.000 V/cell = 6.00 V pack;',
        '  excess-discharge VDET3 = 0.200 V across Q500+Q501 (about 11 A at 2 x 9 mOhm), '
        'excess-charge VDET4 = -0.200 V, tVDET3 12 ms / tVDET4 8 ms.',
        '  Set the PSU to 8.4 V or less: the LT3652 float on this FC is 8.38 V, 120 mV below the '
        'over-charge trip.',
        '  With VSOLAR injected the LT3652 sources into Dir_Chrg_In and will pull a non-sinking PSU '
        'up to its 8.38 V float; use a PSU that sinks,',
        '  or add a bleed load.  If the replica opens COUT that is the expected pack behaviour, not '
        'a fault.',
        '  The PSU must FLOAT.  If its negative is earthed while the FC ground is earthed (laptop, '
        'scope), VBAT_BENCH_N is shorted to GND and',
        '  both protection FETs are bypassed - the replica then proves nothing.',
        '  WITH NO PSU FITTED AND JP500 STILL SHUNTED, the divider holds VBAT_BENCH_N near B+ '
        'through R503+R504, so J500 pin 3 (silkscreened',
        '  "B-") can sit at close to pack potential (about 8.2 V above board ground) with the FETs '
        'off; and whenever the FETs do conduct, R503+R504',
        '  draw a permanent 4.2 mA from Dir_Chrg_In to B- - not only "when the PSU is on".  PULL '
        'JP500 WHENEVER NO BENCH PSU IS CONNECTED; R505',
        '  (100k) then defines VBAT_BENCH_N at B- and nothing is drawn from Dir_Chrg_In.',
        '',
        'SYNTHETIC CELL MIDPOINT (D4):  R503/R504 = 2 x 1.0k 1% 0805 across B+/B- (4.2 mA, 18 mW '
        'each at 8.4 V), fed through JP500.',
        '  Thevenin 500 Ohm + R501 330 Ohm = 830 Ohm at VC, under the 1 kOhm limit of the R5460 '
        'datasheet p.17 technical note (a larger series',
        '  resistance at VC/VDD shifts the detection voltage up).  Do not substitute a high-value '
        'divider.  A single bench PSU has no cell tap,',
        '  so without this divider the R5460 would see one cell at the full pack voltage and trip '
        'immediately.',
        '  R505 = 100k from VBAT_BENCH_N to B- is a bleed only: it gives the cell-negative node a '
        'defined potential when J500 is open (84 uA at',
        '  8.4 V, no effect on the protection thresholds).  It is not a substitute for pulling '
        'JP500 when no PSU is fitted.',
    ], 15.24, 151.19)

    # D11 (brief 2 / 6.4 text note 3).  It lives in the free canvas right of the note column,
    # below the BQ25886 block: at the foot of the left column it fell outside the A3 frame
    # (fix round 2, finding 1 - the last line was off the page entirely).
    notes([
        'D11:  NEVER connect a battery pack to J14 while the bench PSU (J500) or the charger USB '
        '(J510) is connected.  Two sources in parallel',
        '  on a lithium pack is the one failure this bench must make impossible.  J14 stays '
        'populated for connector-trace completeness and',
        '  for FC-only tests with a real pack.',
    ], 205.0, 233.0)

    notes([
        'BQ25886 (U511) - values quoted from SLUSD88A (https://www.ti.com/lit/ds/symlink/bq25886.pdf)',
        '  VSET open  = 8.4 V battery regulation (pin table: RVSET > 150k / floating = 8.4 V).  CE '
        'open = charging enabled by the internal 900k',
        '  pull-down.  OTG tied low (buck/OTG mode disabled per the SLUSD88A pin table); PG '
        'unused.  STAT drives D510/R519 from VBUS_CHG.',
        '  D+ and D- of U511 are shorted to each other, so its BC1.2 detector sees a DCP and applies '
        'the 3.0 A input limit of Table 3; the',
        '  active limit is the lower of that and the ILIM pin.  J510 is power only: its D+/D- and '
        'SBU pins are not connected.',
        '  R514 = 750 Ohm -> IINMAX = KILIM/RILIM = 1110/750 = 1.48 A (8.3.9 / 9.2.2.4).  The '
        'datasheet typical application (figure 20, p.25)',
        '  specifies ILIM = 383 Ohm (2.9 A); debug_board_v1 used 383k - a units error of that '
        'value - giving 2.9 mA, which would never charge',
        '  ("input current limit less than 500 mA is not supported on ILIM").  750 Ohm is fitted '
        'instead of 383 Ohm so the port suits a',
        '  5 V / 2 A bench supply.',
        '  R515 = 5.62k -> ICHG = RICHGSET/KICHGSET = 5620/3810 = 1.475 A (9.2.2.5), pre-charge/term '
        'ICHG/10.  PM ruling S1: 5.7k not E24/E96; 5.62k 1% E96 fitted (1.48 A ILIM dominates).',
        '  C513/C514/C517/C518 = 4 x 22 uF 25 V X5R 1210 on SYS (9.2.2.3: X7R or X5R, 16 V or '
        'higher, minimum 44 uF) - absent on debug_board_v1.',
        '  DC-bias derating read off the KEMET/YAGEO K-SIM curve for C1210C226K3PAC (22 uF 25 V '
        'X5R 1210, same C/V/dielectric/case as the fitted',
        '  Samsung CL32A226KAJNNNE): -41.9% at 8.4 V = 12.8 uF each, so CSYS = 51 uF effective '
        'at the 8.4 V SYS bias, above the 44 uF minimum,',
        '  and dVSYS = IOUT*D/(fSW*CSYS) = 1.5 A * 0.405 / (1.5 MHz * 51.1 uF) = 8 mV ripple.  '
        'Same tool on 10 uF 25 V X5R: -60.0% in 0805,',
        '  -39.0% in 1206, -19.1% in 1210 - so the 2 x 22 uF 0805 fitted before this review held '
        'under 18 uF, and 3 x 22 uF 1206 would also miss 44 uF.',
        '  C511 = 22 uF 25 V X5R 1210 on PMID (9.2.2.2: 25 V or higher preferred for a 5 V input, '
        'minimum 10 uF for up to 3.3 A; 44 uF optimal)',
        '  = 19.0 uF at the 5 V PMID bias.  CBAT C515 = 22 uF 25 V X5R 1210 = 12.8 uF at 8.4 V, '
        'over the 10 uF after-derating figure of the pin table.',
        '  L510 = 1.0 uH SPM6530T-1R0M120 (C87572), CVBUS 1 uF, CREGN 4.7 uF, CBTST 47 nF.',
        '  TS network per figure 18 / 8.3.7.4.1 (RT1 5.24k, RT2 30.31k): R516 5.23k from REGN, R517 '
        '30.1k to GND, and R518 10k standing in for',
        '  the pack 103AT NTC at 25 C.  V(TS)/V(REGN) = 58.9%, inside the T2..T3 band (VT2 68.25%, '
        'VT3 44.75%), so full ICHG and full 8.4 V.',
        '  An open TS pin suspends charging, which is why debug_board_v1 (TS floating) could not '
        'have charged.',
        '  With no battery on Dir_Chrg_In the STAT LED blinks as the BAT capacitance charges and '
        'discharges (8.3.7.1) - expected, not a fault.',
        '  Q510/U510 are the debug_board_v1 input reverse-blocking stage: the DZDH0401DW-7 drives '
        'the DMP4047LFDE-7 as an ideal diode so a',
        '  charged pack on Dir_Chrg_In cannot back-feed the USB port.',
    # review round: the block grew by three lines (CSYS / PMID / BAT derating), so it starts
    # one line higher and the D11 block below it moved down to 233.0
    ], 200.66, 141.19)


# --------------------------------------------------------------------------- assemble + write
def render():
    build()
    libs = '\n'.join(_LIB_TEXT[k] for k in sorted(USED_LIBS))
    body = '\n'.join(ITEMS)
    return ('(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n\t(generator_version "10.0")\n'
            '\t(uuid "%s")\n\t(paper "A3")\n\t(lib_symbols\n%s\n\t)\n%s\n)\n'
            % (SHEET_FILE_UUID, libs, body))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(PROJ, 'battery_protection_replica.kicad_sch'))
    a = ap.parse_args()
    txt = render()
    dup = [r for r in set(REFS) if REFS.count(r) > 1]
    if dup:
        print('duplicate refdes: %s' % sorted(dup), file=sys.stderr)
        return 1
    tmp = a.out + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as fh:
        fh.write(txt)
    os.replace(tmp, a.out)
    print('%s: %d items, %d symbols, %d lib_symbols' % (a.out, len(ITEMS), len(REFS), len(USED_LIBS)))
    print('refdes: %s' % ' '.join(sorted(REFS)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
