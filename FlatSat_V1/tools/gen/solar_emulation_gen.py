#!/usr/bin/env python3
"""Generate FlatSat_V1/solar_emulation.kicad_sch  (sheet 8, "Solar and Sensor Emulation").

PROVES FlatSat V1 - Phase 1 schematic capture, brief section 6.2.

  * Face 0  : real reference silicon copied from solar_boards/XY_Face_V4
              (TCA4311A + TMP112 + VEML6031X00 + DRV2605L), powered from F0_PWR.
  * Faces1-5: one TCA4311A hot-swap buffer per face, VCC = Fn_PWR, bus side on the
              FC nets Fn_SDA/Fn_SCL, device side EMU_Fn_SDA/EMU_Fn_SCL with 4.7 k
              pull-ups to Fn_PWR (PM ruling R7; <= 8.2 k for RP2350 erratum E9),
              plus a 4.7 k Fn_PWR sense tap (EMU_Fn_SENSE).
  * BATT    : TCA4311A on BATT_SDA/BATT_SCL (mux ch4), VCC = +3V3   (battery_pack_v2 U3)
  * TOP     : TCA4311A on SDA_Top/SCL_Top   (mux ch7), VCC = +3V3   (antenna_top_cap_v2c U6)
              plus the 4.7 k +3V3 sense tap (EMU_FC3V3_SENSE).

Everything is placed on the 1.27 mm grid; pin coordinates are computed from the
lib_symbols pin positions with the same transform tools/sch_lint.py uses.
Writes atomically (tmp + os.replace).

Usage:  python3 tools/gen/solar_emulation_gen.py [--out <path>]
"""
import argparse
import os
import random
import re
import sys
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, '..', '..'))
# Checked-in symbol pantry (tools/pantry); $FLATSAT_PANTRY overrides it.  Never a
# session scratch path: the generator must run from a clean checkout (review fix 13).
PANTRY = os.environ.get('FLATSAT_PANTRY', os.path.join(HERE, '..', 'pantry'))

ROOT_UUID = 'c64c0d72-a9f6-4f3a-891e-1f647558f538'
SHEET_UUID = '0ec7a68a-65de-4eda-8407-9dcf20e51c0b'
INST_PATH = '/%s/%s' % (ROOT_UUID, SHEET_UUID)
PROJECT = 'FlatSat_V1'

G = 1.27


# Review fix 14: deterministic uuid4 stream.  Emission order is fixed, so seeding the
# RNG makes a regeneration byte-identical to the committed sheet instead of churning
# every uuid (which would orphan any layout that had already been placed from it).
# Set FLATSAT_FRESH_UUIDS=1 to get real random uuids (only when re-keying a sheet).
_rng = random.Random('flatsat-solar_emulation-2026-09-14')
_FRESH = os.environ.get('FLATSAT_FRESH_UUIDS') == '1'


def u():
    if _FRESH:
        return str(uuid.uuid4())
    return str(uuid.UUID(int=_rng.getrandbits(128), version=4))


# ----------------------------------------------------------------------------- pantry
def pantry_file(lib_id):
    return os.path.join(PANTRY, re.sub(r'[:/ ()]', '_', lib_id) + '.sexp')


_LIB_CACHE = {}

# Corrections applied to a pantry block's cached default properties.  Integrator fix round 2:
# the KiCad 10 Driver_Haptic:DRV2605LDGS symbol still defaults to Package_SO:VSSOP-10_3x3mm_P0.5mm,
# which was removed from Package_SO.pretty; TSSOP-10_3x3mm_P0.5mm is the same land (3x3 mm body,
# 0.5 mm pitch, 10 pins, no thermal pad = the DGS package).  Fixing it in lib_symbols as well as
# on the instance means a GUI "Update Symbols from Library" cannot put the dangling name back.
LIB_FIXUPS = {
    'Driver_Haptic:DRV2605LDGS': [
        ('Package_SO:VSSOP-10_3x3mm_P0.5mm', 'Package_SO:TSSOP-10_3x3mm_P0.5mm'),
    ],
}


def lib_block(lib_id):
    if lib_id not in _LIB_CACHE:
        p = pantry_file(lib_id)
        if not os.path.exists(p):
            raise SystemExit('pantry block missing for %s (%s)' % (lib_id, p))
        blk = open(p, encoding='utf-8').read().rstrip('\n')
        for old, new in LIB_FIXUPS.get(lib_id, ()):
            # Idempotent (review fix 13): a pantry block rebuilt from a delivered sheet
            # already carries `new`, and that must not abort the generator.  Only a block
            # that has neither the old nor the new string is a real error.
            if old not in blk and new not in blk:
                raise SystemExit('lib fixup for %s: neither %r nor %r present'
                                 % (lib_id, old, new))
            blk = blk.replace(old, new)
        _LIB_CACHE[lib_id] = blk
    return _LIB_CACHE[lib_id]


def _parse(text):
    toks = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for t in toks:
        if t == '(':
            stack.append([])
        elif t == ')':
            n = stack.pop()
            stack[-1].append(n)
        else:
            if t.startswith('"'):
                t = t[1:-1]
            stack[-1].append(t)
    return stack[0]


def _ch(node, name):
    for c in node:
        if isinstance(c, list) and c and c[0] == name:
            return c
    return None


def _chs(node, name):
    return [c for c in node if isinstance(c, list) and c and c[0] == name]


_PINS_CACHE = {}


def lib_pins(lib_id):
    """{pin number: (x, y)} in library coordinates (y up)."""
    if lib_id not in _PINS_CACHE:
        sym = _parse(lib_block(lib_id))[0]
        pins = {}
        for sub in _chs(sym, 'symbol'):
            for p in _chs(sub, 'pin'):
                at = _ch(p, 'at')
                num = _ch(p, 'number')
                if at and num:
                    pins[num[1]] = (float(at[1]), float(at[2]))
        _PINS_CACHE[lib_id] = pins
    return _PINS_CACHE[lib_id]


def pin_xy(lib_id, number, at, rot=0, mirror=None):
    """Schematic coordinate of one pin of a placed symbol."""
    import math
    px, py = lib_pins(lib_id)[str(number)]
    x, y = px, -py
    if mirror == 'x':
        y = -y
    elif mirror == 'y':
        x = -x
    r = math.radians(rot)
    xr = x * math.cos(r) + y * math.sin(r)
    yr = -x * math.sin(r) + y * math.cos(r)
    return (round(at[0] + xr, 4), round(at[1] + yr, 4))


# ----------------------------------------------------------------------------- sheet
class Sheet:
    def __init__(self):
        self.libs = []          # ordered lib_ids
        self.rects = []
        self.texts = []
        self.junctions = []
        self.no_connects = []
        self.wires = []
        self.labels = []        # (kind, name, x, y, rot, shape)
        self.symbols = []
        self.pwr_n = 300

    # -- primitives ---------------------------------------------------------
    def need(self, lib_id):
        if lib_id not in self.libs:
            self.libs.append(lib_id)

    def rect(self, a, b):
        self.rects.append((a, b))

    def text(self, s, at, size=1.27):
        self.texts.append((s, at, size))

    def junction(self, at):
        self.junctions.append(at)

    def nc(self, at):
        self.no_connects.append(at)

    def wire(self, a, b):
        if a == b:
            raise ValueError('zero length wire at %r' % (a,))
        self.wires.append((a, b))

    def poly(self, *pts):
        for i in range(len(pts) - 1):
            self.wire(pts[i], pts[i + 1])

    def glabel(self, name, at, rot=0, shape='bidirectional'):
        self.labels.append(('global_label', name, at, rot, shape))

    def label(self, name, at, rot=0):
        self.labels.append(('label', name, at, rot, None))

    # -- symbols ------------------------------------------------------------
    def sym(self, lib_id, ref, value, at, rot=0, props=None, ref_at=None,
            val_at=None, hide_value=False, mirror=None, just=None):
        self.need(lib_id)
        self.symbols.append(dict(lib_id=lib_id, ref=ref, value=value, at=at, rot=rot,
                                 props=props or {}, ref_at=ref_at, val_at=val_at,
                                 hide_value=hide_value, mirror=mirror, just=just))
        return at

    def gnd(self, at):
        self.pwr_n += 1
        self.sym('power:GND', '#PWR%d' % self.pwr_n, 'GND', at,
                 val_at=(at[0], at[1] + 4.445))

    def v3v3(self, at):
        self.pwr_n += 1
        self.sym('power:+3V3', '#PWR%d' % self.pwr_n, '+3V3', at,
                 val_at=(at[0], at[1] - 4.445))

    # -- emit ---------------------------------------------------------------
    def render(self):
        o = []
        w = o.append
        w('(kicad_sch')
        w('\t(version 20260306)')
        w('\t(generator "eeschema")')
        w('\t(generator_version "10.0")')
        w('\t(uuid "%s")' % u())
        w('\t(paper "A3")')
        w('\t(lib_symbols')
        for lid in self.libs:
            w(lib_block(lid))
        w('\t)')

        for a, b in self.rects:
            w('\t(rectangle')
            w('\t\t(start %s %s)' % (fm(a[0]), fm(a[1])))
            w('\t\t(end %s %s)' % (fm(b[0]), fm(b[1])))
            w('\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)')
            w('\t\t(fill\n\t\t\t(type none)\n\t\t)')
            w('\t\t(uuid "%s")' % u())
            w('\t)')

        for s, at, size in self.texts:
            w('\t(text "%s"' % esc(s))
            w('\t\t(exclude_from_sim no)')
            w('\t\t(at %s %s 0)' % (fm(at[0]), fm(at[1])))
            w('\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)\n\t\t\t)\n\t\t\t(justify left)\n\t\t)'
              % (fm(size), fm(size)))
            w('\t\t(uuid "%s")' % u())
            w('\t)')

        for at in self.junctions:
            w('\t(junction')
            w('\t\t(at %s %s)' % (fm(at[0]), fm(at[1])))
            w('\t\t(diameter 0)')
            w('\t\t(color 0 0 0 0)')
            w('\t\t(uuid "%s")' % u())
            w('\t)')

        for at in self.no_connects:
            w('\t(no_connect')
            w('\t\t(at %s %s)' % (fm(at[0]), fm(at[1])))
            w('\t\t(uuid "%s")' % u())
            w('\t)')

        for a, b in self.wires:
            w('\t(wire')
            w('\t\t(pts')
            w('\t\t\t(xy %s %s) (xy %s %s)' % (fm(a[0]), fm(a[1]), fm(b[0]), fm(b[1])))
            w('\t\t)')
            w('\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)')
            w('\t\t(uuid "%s")' % u())
            w('\t)')

        for kind, name, at, rot, shape in self.labels:
            just = 'right' if rot in (180, 270) else 'left'
            if kind == 'global_label':
                w('\t(global_label "%s"' % esc(name))
                w('\t\t(shape %s)' % shape)
                w('\t\t(at %s %s %d)' % (fm(at[0]), fm(at[1]), rot))
                w('\t\t(fields_autoplaced yes)')
                w('\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s)\n\t\t)' % just)
                w('\t\t(uuid "%s")' % u())
                w('\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"')
                w('\t\t\t(at %s %s 0)' % (fm(at[0]), fm(at[1])))
                w('\t\t\t(hide yes)')
                w('\t\t\t(show_name no)')
                w('\t\t\t(do_not_autoplace no)')
                w('\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t\t(justify %s)\n\t\t\t)' % just)
                w('\t\t)')
                w('\t)')
            else:
                w('\t(label "%s"' % esc(name))
                w('\t\t(at %s %s %d)' % (fm(at[0]), fm(at[1]), rot))
                w('\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s bottom)\n\t\t)' % just)
                w('\t\t(uuid "%s")' % u())
                w('\t)')

        for s in self.symbols:
            w(self._sym_sexp(s))

        w(')')
        return '\n'.join(o) + '\n'

    def _sym_sexp(self, s):
        lid, at, rot = s['lib_id'], s['at'], s['rot']
        x, y = at
        is_pwr = lid.startswith('power:')
        o = []
        w = o.append
        w('\t(symbol')
        w('\t\t(lib_id "%s")' % lid)
        w('\t\t(at %s %s %d)' % (fm(x), fm(y), rot))
        if s['mirror']:
            w('\t\t(mirror %s)' % s['mirror'])
        w('\t\t(unit 1)')
        w('\t\t(body_style 1)')
        w('\t\t(exclude_from_sim no)')
        w('\t\t(in_bom yes)')
        w('\t\t(on_board yes)')
        w('\t\t(in_pos_files yes)')
        w('\t\t(dnp no)')
        w('\t\t(uuid "%s")' % u())

        ref_at = s['ref_at'] or (x, y - 5.08)
        val_at = s['val_at'] or (x, y + 5.08)
        # SCH_FIELD::GetDrawRotation() swaps horizontal/vertical for a symbol whose
        # transform is rotated 90/270, so a field on such a symbol needs angle 90 to
        # come out horizontal on the sheet.
        pang = 90 if rot in (90, 270) else 0
        w(prop('Reference', s['ref'], ref_at, hide=is_pwr, justify=s.get('just'), angle=pang))
        w(prop('Value', s['value'], val_at, hide=s['hide_value'], justify=s.get('just'), angle=pang))
        for k in ('Footprint', 'Datasheet', 'Description', 'LCSC Part'):
            v = s['props'].get(k)
            if v is None:
                if k in ('Footprint', 'Datasheet', 'Description'):
                    v = ''
                else:
                    continue
            w(prop(k, v, (x, y), hide=True))
        for num in sorted(lib_pins(lid), key=lambda n: (len(n), n)):
            w('\t\t(pin "%s"' % num)
            w('\t\t\t(uuid "%s")' % u())
            w('\t\t)')
        w('\t\t(instances')
        w('\t\t\t(project "%s"' % PROJECT)
        w('\t\t\t\t(path "%s"' % INST_PATH)
        w('\t\t\t\t\t(reference "%s")' % s['ref'])
        w('\t\t\t\t\t(unit 1)')
        w('\t\t\t\t)')
        w('\t\t\t)')
        w('\t\t)')
        w('\t)')
        return '\n'.join(o)


def prop(name, value, at, hide=False, justify=None, angle=0):
    o = []
    w = o.append
    w('\t\t(property "%s" "%s"' % (name, esc(value)))
    w('\t\t\t(at %s %s %d)' % (fm(at[0]), fm(at[1]), angle))
    if hide:
        w('\t\t\t(hide yes)')
    w('\t\t\t(show_name no)')
    w('\t\t\t(do_not_autoplace no)')
    w('\t\t\t(effects')
    w('\t\t\t\t(font')
    w('\t\t\t\t\t(size 1.27 1.27)')
    w('\t\t\t\t)')
    if justify:
        w('\t\t\t\t(justify %s)' % justify)
    w('\t\t\t)')
    w('\t\t)')
    return '\n'.join(o)


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')


def fm(v):
    s = '%.4f' % float(v)
    s = s.rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'


# ----------------------------------------------------------------------------- parts
FP_R0402 = 'Resistor_SMD:R_0402_1005Metric'
FP_R0805 = 'Resistor_SMD:R_0805_2012Metric'
# R304 dissipates 0.253 W at the DRV2605L supply-limited maximum.  A stock 0805 thick-film part
# is 0.125 W and a 1206 is 0.25 W (100 % of rating), so the coil-emulation dummy load is a 2010
# (0.75 W = 34 % of rating).  Integrator fix round 2.
FP_R2010 = 'Resistor_SMD:R_2010_5025Metric'
FP_C0402 = 'Capacitor_SMD:C_0402_1005Metric'
FP_TP = 'TestPoint:TestPoint_Pad_D1.5mm'

R_LIB = 'Device:R'
C_LIB = 'Device:C'
BUF = 'easyeda2kicad:TCA4311ADGKR'

BUF_PROPS = {
    'Footprint': 'easyeda2kicad:MSOP-8_L3.0-W3.0-P0.65-LS5.0-BL',
    'Datasheet': 'https://www.ti.com/lit/ds/symlink/tca4311a.pdf',
    'Description': 'Hot-swappable I2C bus buffer, 1V precharge, READY flag (SCPS226C)',
    'LCSC Part': 'C130025',
}


def res(sh, ref, value, at, rot, desc, lcsc, fp=FP_R0402, side='right'):
    just = None
    if rot == 90:      # horizontal
        ref_at = (at[0], at[1] - 2.54)
        val_at = (at[0], at[1] + 2.54)
    elif side == 'center':
        # Used on the rot-180 pull-ups: KiCad applies the symbol transform to a
        # field's justification, so left/right would flip on a 180-degree symbol.
        # Centred text is transform-invariant.
        ref_at = (at[0] + 5.08, at[1] - 1.27)
        val_at = (at[0] + 5.08, at[1] + 1.27)
    elif side == 'left':
        ref_at = (at[0] - 2.286, at[1] - 1.27)
        val_at = (at[0] - 2.286, at[1] + 1.27)
        just = 'right'
    else:              # vertical, text to the right
        ref_at = (at[0] + 2.286, at[1] - 1.27)
        val_at = (at[0] + 2.286, at[1] + 1.27)
        just = 'left'
    props = {'Footprint': fp, 'Datasheet': '', 'Description': desc}
    if lcsc:
        props['LCSC Part'] = lcsc
    sh.sym(R_LIB, ref, value, at, rot, props, ref_at=ref_at, val_at=val_at, just=just)
    return (pin_xy(R_LIB, 1, at, rot), pin_xy(R_LIB, 2, at, rot))


def cap(sh, ref, value, at, desc, lcsc, fp=FP_C0402):
    props = {'Footprint': fp, 'Datasheet': '', 'Description': desc}
    if lcsc:
        props['LCSC Part'] = lcsc
    sh.sym(C_LIB, ref, value, at, 0, props,
           ref_at=(at[0] + 2.54, at[1] - 1.27), val_at=(at[0] + 2.54, at[1] + 1.27),
           just='left')
    return (pin_xy(C_LIB, 1, at, 0), pin_xy(C_LIB, 2, at, 0))


# ----------------------------------------------------------------------------- blocks
def channel(sh, X, Y, title, u_ref, r_base, c_ref,
            bus_sda, bus_scl, dev_sda, dev_scl,
            pwr_label, sense_label, ready_pullup, tp_note=''):
    """One TCA4311A front-end.  pwr_label = ('glabel', 'F1_PWR') or ('+3V3', None).

    Device-side routing rule (fix round 2, verifier finding 2): a global label's
    hexagon is drawn to the RIGHT of its anchor, so nothing vertical may sit inside
    that band.  The EMU_* labels therefore end the two exit wires and every riser
    stays to their left:

        Fn_PWR --------.                      (top rail, feeds the SDA pull-up only)
                       R{n}2
        SDAOUT --------+-----> EMU_Fn_SDA
        SCLOUT ----+---------> EMU_Fn_SCL
                   R{n}3                      (SCL pull-up hangs BELOW the exits)
        READY --R{n}1--.                      (READY pull-up hangs below too)
                       `------> Fn_PWR        (second tap on the same net)

    Resistor pin 1 still sits on Fn_PWR and pin 2 on the signal for every pull-up
    (R{n}1 and R{n}3 are placed rot 180 for that), so the netlist is pin-identical
    to the pre-fix version.
    """
    P = lambda n: pin_xy(BUF, n, (X, Y))
    sh.rect((X - 45.72, Y - 29.21), (X + 45.72, Y + 33.02))
    sh.text(title, (X - 41.91, Y - 26.67), 1.778)
    if tp_note:
        sh.text(tp_note, (X - 41.91, Y + 31.75), 1.27)

    sh.sym(BUF, u_ref, 'TCA4311ADGKR', (X, Y), 0, BUF_PROPS,
           ref_at=(X, Y - 12.7), val_at=(X, Y + 12.7))

    def power_point(at, rot=180):
        if pwr_label[0] == 'glabel':
            sh.glabel(pwr_label[1], at, rot, 'input')
        else:
            sh.v3v3(at)

    # ---- bus (FC) side
    sh.wire(P(6), (X - 25.4, Y - 6.35))
    sh.glabel(bus_sda, (X - 25.4, Y - 6.35), 180, 'bidirectional')
    sh.wire(P(3), (X - 25.4, Y - 3.81))
    sh.glabel(bus_scl, (X - 25.4, Y - 3.81), 180, 'bidirectional')

    # ---- VCC + EN pull-up + decoupling (+ optional sense tap) on one riser
    sh.wire(P(8), (X - 33.02, Y + 6.35))
    power_point((X - 33.02, Y + 6.35))
    sh.wire(P(1), (X - 20.32, Y + 1.27))
    res(sh, r_base + '0', '10k', (X - 24.13, Y + 1.27), 90,
        'TCA4311A EN pull-up to the buffer VCC rail', 'C25744')
    riser_bot = Y + 26.67 if sense_label else Y + 6.35
    sh.wire((X - 27.94, Y + 1.27), (X - 27.94, riser_bot))
    sh.junction((X - 27.94, Y + 6.35))
    sh.wire((X - 22.86, Y + 6.35), (X - 22.86, Y + 8.89))
    sh.junction((X - 22.86, Y + 6.35))
    cap(sh, c_ref, '100nF', (X - 22.86, Y + 12.7), 'TCA4311A VCC decoupling', 'C1525')
    sh.gnd((X - 22.86, Y + 16.51))

    # ---- device (emulator) side: top rail feeds the SDA pull-up only
    sh.wire((X + 15.24, Y - 17.78), (X + 20.32, Y - 17.78))
    power_point((X + 15.24, Y - 17.78))
    # PM ruling R7 / review fix id 3: 4.7 k, not 10 k.  With the face off the pad
    # sees 4.7 k + the AP22653 output-discharge NMOS (600 Ohm typ) = 5.3 k <= the
    # 8.2 k RP2350 erratum E9 threshold, so brief rule 10 holds in hardware.
    # Face 0 (face0(), R302/R303) keeps 10 k for XY_Face_V4 parity.
    res(sh, r_base + '2', '4.7k', (X + 20.32, Y - 13.97), 0,
        'device-side SDA pull-up to the buffer VCC rail', 'C25900')
    sh.wire((X + 20.32, Y - 10.16), (X + 20.32, Y - 6.35))

    sh.wire(P(7), (X + 22.86, Y - 6.35))
    sh.junction((X + 20.32, Y - 6.35))
    sh.glabel(dev_sda, (X + 22.86, Y - 6.35), 0, 'bidirectional')

    sh.wire(P(2), (X + 25.4, Y - 3.81))
    sh.glabel(dev_scl, (X + 25.4, Y - 3.81), 0, 'bidirectional')

    # ---- SCL pull-up hangs below the exits (rot 180 keeps pin 1 on Fn_PWR)
    res(sh, r_base + '3', '4.7k', (X + 22.86, Y + 5.08), 180,
        'device-side SCL pull-up to the buffer VCC rail', 'C25900', side='center')
    sh.wire((X + 22.86, Y + 1.27), (X + 22.86, Y - 3.81))
    sh.junction((X + 22.86, Y - 3.81))
    sh.wire((X + 22.86, Y + 8.89), (X + 22.86, Y + 13.97))
    sh.wire((X + 22.86, Y + 13.97), (X + 33.02, Y + 13.97))
    power_point((X + 33.02, Y + 13.97), 0)

    # ---- READY pull-up, on the same second Fn_PWR tap
    if ready_pullup:
        sh.wire(P(5), (X + 20.32, Y + 1.27))
        res(sh, r_base + '1', '10k', (X + 20.32, Y + 16.51), 0,
            'TCA4311A READY open-drain pull-up (datasheet 8.3.2)', 'C25744', side='left')
        sh.wire((X + 20.32, Y + 1.27), (X + 20.32, Y + 12.7))
        sh.wire((X + 20.32, Y + 20.32), (X + 20.32, Y + 22.86))
        sh.wire((X + 20.32, Y + 22.86), (X + 30.48, Y + 22.86))
        sh.wire((X + 30.48, Y + 22.86), (X + 30.48, Y + 13.97))
        sh.junction((X + 30.48, Y + 13.97))
    else:
        sh.nc(P(5))

    # ---- GND
    sh.wire(P(4), (X + 16.51, Y + 6.35))
    sh.gnd((X + 16.51, Y + 6.35))

    # ---- sense tap
    if sense_label:
        res(sh, r_base + '4', '4.7k', (X - 24.13, Y + 26.67), 90,
            'power-present sense tap, 4.7k <= 8.2k per RP2350 erratum E9', 'C25900')
        sh.wire((X - 20.32, Y + 26.67), (X - 12.7, Y + 26.67))
        sh.glabel(sense_label, (X - 12.7, Y + 26.67), 0, 'output')


def face0(sh):
    sh.rect((20.32, 24.13), (259.08, 118.11))
    sh.text('FACE 0 - GOLDEN REFERENCE (real silicon, copied from solar_boards/XY_Face_V4)',
            (22.86, 28.19), 1.778)
    sh.text('Powered from the FC face switch F0_PWR (U19 AP22653).  Bus side = F0_SDA / F0_SCL (TCA9548 U3 ch0).',
            (22.86, 32.0), 1.27)

    # ---------- U300 TCA4311A -------------------------------------------------
    X, Y = 63.5, 63.5
    P = lambda n: pin_xy(BUF, n, (X, Y))
    sh.sym(BUF, 'U300', 'TCA4311ADGKR', (X, Y), 0, BUF_PROPS,
           ref_at=(X, Y - 12.7), val_at=(X, Y + 12.7))

    sh.wire(P(6), (38.1, 57.15))
    sh.glabel('F0_SDA', (38.1, 57.15), 180, 'bidirectional')
    sh.wire(P(3), (38.1, 59.69))
    sh.glabel('F0_SCL', (38.1, 59.69), 180, 'bidirectional')

    sh.wire(P(8), (33.02, 69.85))
    sh.glabel('F0_PWR', (33.02, 69.85), 180, 'input')
    sh.wire(P(1), (43.18, 64.77))
    res(sh, 'R300', '10k', (39.37, 64.77), 90,
        'TCA4311A EN pull-up to F0_PWR (as XY_Face_V4 R2)', 'C25744')
    sh.wire((35.56, 64.77), (35.56, 69.85))
    sh.junction((35.56, 69.85))
    sh.wire((40.64, 69.85), (40.64, 72.39))
    sh.junction((40.64, 69.85))
    cap(sh, 'C300', '100nF', (40.64, 76.2), 'TCA4311A VCC decoupling (XY_Face_V4 C6)', 'C1525')
    sh.gnd((40.64, 80.01))

    # device side.  Same rule as the emulated channels (fix round 2): the two
    # F0_DEV_* labels end their exit wires and every riser stays to their left,
    # so the SCL and READY pull-ups hang BELOW the exits on a second F0_PWR tap.
    sh.wire((78.74, 43.18), (83.82, 43.18))
    sh.glabel('F0_PWR', (78.74, 43.18), 180, 'input')
    res(sh, 'R302', '10k', (83.82, 49.53), 0,
        'Face 0 device-side SDA pull-up (XY_Face_V4 R6)', 'C25744')
    sh.wire((83.82, 45.72), (83.82, 43.18))
    sh.wire((83.82, 53.34), (83.82, 57.15))

    sh.wire(P(7), (86.36, 57.15))
    sh.junction((83.82, 57.15))
    sh.label('F0_DEV_SDA', (86.36, 57.15), 0)

    sh.wire(P(2), (99.06, 59.69))
    sh.label('F0_DEV_SCL', (99.06, 59.69), 0)
    res(sh, 'R303', '10k', (93.98, 67.31), 180,
        'Face 0 device-side SCL pull-up (XY_Face_V4 R5)', 'C25744', side='center')
    sh.wire((93.98, 63.5), (93.98, 59.69))
    sh.junction((93.98, 59.69))
    sh.wire((93.98, 71.12), (93.98, 77.47))

    sh.wire(P(5), (83.82, 64.77))
    res(sh, 'R301', '10k', (83.82, 68.58), 0,
        'TCA4311A READY pull-up (datasheet 8.3.2; XY_Face_V4 R4)', 'C25744')
    sh.wire((83.82, 72.39), (83.82, 77.47))
    sh.wire((83.82, 77.47), (93.98, 77.47))
    sh.junction((93.98, 77.47))
    sh.wire((93.98, 77.47), (101.6, 77.47))
    sh.glabel('F0_PWR', (101.6, 77.47), 0, 'input')

    sh.wire(P(4), (78.74, 76.2))
    sh.gnd((78.74, 76.2))

    # ---------- device power rail --------------------------------------------
    sh.wire((137.16, 38.1), (238.76, 38.1))
    sh.glabel('F0_PWR', (137.16, 38.1), 180, 'input')

    # ---------- U301 TMP112 ---------------------------------------------------
    T = 'Sensor_Temperature:TMP112xxDRL'
    tx, ty = 146.05, 60.96
    Q = lambda n: pin_xy(T, n, (tx, ty))
    sh.sym(T, 'U301', 'TMP112xxDRL', (tx, ty), 0,
           {'Footprint': 'Package_TO_SOT_SMD:SOT-563',
            'Datasheet': 'https://www.ti.com/lit/ds/symlink/tmp112.pdf',
            'Description': 'Face 0 board temperature sensor, I2C 0x48 (ADD0 = GND, ALERT unused)',
            'LCSC Part': 'C28927'},
           ref_at=(tx - 5.08, ty - 13.97), val_at=(tx + 12.7, ty + 13.97))
    sh.wire(Q(6), (127.0, 55.88))
    sh.label('F0_DEV_SDA', (127.0, 55.88), 180)
    sh.wire(Q(1), (127.0, 58.42))
    sh.label('F0_DEV_SCL', (127.0, 58.42), 180)
    sh.poly(Q(4), (130.81, 63.5), (130.81, 68.58))
    sh.gnd((130.81, 68.58))
    # ALERT: XY_Face_V4 grounds it; grounding an open-collector pin trips the KiCad
    # "Open collector / Power output" pin conflict because the FC GND net carries
    # power_out pins (U7 LSM6DSO pins 6/7).  ALERT is unused on the face, so it is
    # left open with a no-connect marker instead.  See the sheet report.
    sh.nc(Q(3))
    sh.wire(Q(2), (146.05, 74.93))
    sh.gnd((146.05, 74.93))
    sh.wire(Q(5), (146.05, 38.1))
    sh.junction((146.05, 38.1))
    cap(sh, 'C301', '10nF', (167.64, 44.45), 'TMP112 supply decoupling (XY_Face_V4 C2)', 'C15195')
    sh.wire((167.64, 40.64), (167.64, 38.1))
    sh.junction((167.64, 38.1))
    sh.gnd((167.64, 48.26))

    # ---------- U303 DRV2605L -------------------------------------------------
    D = 'Driver_Haptic:DRV2605LDGS'
    dx, dy = 213.36, 60.96
    R = lambda n: pin_xy(D, n, (dx, dy))
    sh.sym(D, 'U303', 'DRV2605LDGS', (dx, dy), 0,
           # Integrator fix round 2: Package_SO:VSSOP-10_3x3mm_P0.5mm (inherited verbatim from
           # XY_Face_V4) does not exist in KiCad 10 -> footprint_link_issues, U303 unplaceable.
           # TSSOP-10_3x3mm_P0.5mm is the same 3x3 mm, 0.5 mm pitch, 10-pin, no-thermal-pad land.
           {'Footprint': 'Package_SO:TSSOP-10_3x3mm_P0.5mm',
            'Datasheet': 'https://www.ti.com/lit/ds/symlink/drv2605l.pdf',
            'Description': 'Face 0 magnetorquer driver, I2C 0x5A (EN = VDD, IN/TRIG = GND)',
            'LCSC Part': 'C527464'},
           ref_at=(dx - 16.51, dy - 13.97), val_at=(dx + 15.24, dy - 13.97))
    sh.wire(R(10), (213.36, 38.1))
    sh.junction((213.36, 38.1))
    sh.poly(R(5), (215.9, 41.91), (213.36, 41.91))
    sh.junction((213.36, 41.91))
    sh.nc(R(6))
    sh.wire(R(3), (191.77, 55.88))
    sh.label('F0_DEV_SDA', (191.77, 55.88), 180)
    sh.wire(R(2), (191.77, 58.42))
    sh.label('F0_DEV_SCL', (191.77, 58.42), 180)
    sh.poly(R(4), (195.58, 63.5), (195.58, 68.58))
    sh.gnd((195.58, 68.58))
    sh.wire(R(8), (213.36, 74.93))
    sh.gnd((213.36, 74.93))
    sh.poly(R(1), (231.14, 66.04), (231.14, 69.85))
    cap(sh, 'C304', '1uF', (231.14, 73.66), 'DRV2605L REG reservoir (XY_Face_V4 C5)', 'C52923')
    sh.gnd((231.14, 77.47))
    cap(sh, 'C303', '100nF', (238.76, 44.45), 'DRV2605L VDD decoupling (XY_Face_V4 C3)', 'C1525')
    sh.wire((238.76, 40.64), (238.76, 38.1))
    sh.gnd((238.76, 48.26))
    sh.wire(R(7), (233.68, 55.88))
    sh.label('F0_COIL_P', (233.68, 55.88), 0)
    sh.wire(R(9), (233.68, 58.42))
    sh.label('F0_COIL_N', (233.68, 58.42), 0)

    # ---------- U302 VEML6031X00 ---------------------------------------------
    V = 'easyeda2kicad:VEML6031X00'
    vx, vy = 146.05, 99.06
    W = lambda n: pin_xy(V, n, (vx, vy))
    sh.sym(V, 'U302', 'VEML6031X00', (vx, vy), 0,
           {'Footprint': 'easyeda2kicad:SENSOR-SMD_VEML6031X00',
            'Datasheet': 'https://www.vishay.com/docs/80007/veml6031x00.pdf',
            'Description': 'Face 0 ambient light / sun sensor, I2C 0x29',
            'LCSC Part': 'C3678616'},
           ref_at=(vx - 6.35, vy - 10.16), val_at=(vx + 13.97, vy + 11.43))
    sh.wire(W(6), (146.05, 85.09))
    sh.wire((138.43, 85.09), (157.48, 85.09))
    sh.junction((146.05, 85.09))
    sh.glabel('F0_PWR', (138.43, 85.09), 180, 'input')
    cap(sh, 'C302', '100nF', (157.48, 88.9), 'VEML6031X00 supply decoupling (XY_Face_V4 C4)', 'C1525')
    sh.gnd((157.48, 92.71))
    sh.wire(W(2), (128.27, 97.79))
    sh.label('F0_DEV_SDA', (128.27, 97.79), 180)
    sh.wire(W(5), (128.27, 100.33))
    sh.label('F0_DEV_SCL', (128.27, 100.33), 180)
    sh.nc(W(3))
    sh.wire(W(1), (146.05, 110.49))
    sh.gnd((146.05, 110.49))

    # ---------- coil header + dummy load -------------------------------------
    sh.text('External magnetorquer coil header J300.\n'
            'R304 = XY_Face_V4 PCB-coil equivalent (43 R 2010);\n'
            'remove it when a real coil is plugged in.',
            (186.69, 107.95), 1.27)
    sh.label('F0_COIL_P', (222.25, 87.63), 180)
    sh.poly((222.25, 87.63), (231.14, 87.63), (237.49, 87.63))
    sh.label('F0_COIL_N', (222.25, 95.25), 180)
    sh.poly((222.25, 95.25), (231.14, 95.25), (233.68, 95.25), (233.68, 90.17), (237.49, 90.17))
    res(sh, 'R304', '43R', (231.14, 91.44), 0,
        'XY_Face_V4 PCB coil DC-resistance equivalent, 2010 0.75 W (0.253 W worst case)',
        'C7467404', fp=FP_R2010, side='left')
    sh.junction((231.14, 87.63))
    sh.junction((231.14, 95.25))
    J = 'Connector_Generic:Conn_01x02'
    sh.sym(J, 'J300', 'Coil Out', (242.57, 87.63), 0,
           {'Footprint': 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
            'Datasheet': 'https://www.lcsc.com/datasheet/lcsc_datasheet_2409302300_XFCN-PZ254V-11-02P_C492401.pdf',
            'Description': 'DRV2605L OUT+/OUT- to an external magnetorquer coil or lab inductor',
            'LCSC Part': 'C492401'},
           ref_at=(244.0, 82.55), val_at=(244.0, 93.98))


def testpoints(sh, X, Y):
    sh.rect((X - 45.72, Y - 29.21), (X + 45.72, Y + 33.02))
    sh.text('BENCH TEST POINTS', (X - 41.91, Y - 26.67), 1.778)
    sh.text('Probe pads only - nothing in series with an FC rail.',
            (X - 41.91, Y - 22.86), 1.27)
    rails = [('F0_PWR', 'TP300'), ('F1_PWR', 'TP301'), ('F2_PWR', 'TP302'),
             ('F3_PWR', 'TP303'), ('F4_PWR', 'TP304'), ('F5_PWR', 'TP305'),
             ('+3V3', 'TP306')]
    y = Y - 16.51
    for name, ref in rails:
        if name == '+3V3':
            sh.v3v3((X - 7.62, y))
            desc = 'bench probe pad on the FC +3V3 rail (BATT / TOP buffer supply)'
        else:
            sh.glabel(name, (X - 7.62, y), 180, 'input')
            desc = 'bench probe pad on the FC face-switch output %s' % name
        sh.wire((X - 7.62, y), (X + 5.08, y))
        sh.sym('Connector:TestPoint', ref, 'TestPoint', (X + 5.08, y), 0,
               {'Footprint': FP_TP, 'Datasheet': '', 'Description': desc},
               ref_at=(X + 7.62, y - 1.27), hide_value=True)
        y += 7.62


NOTE_BLOCKS = [
    (1.778, 'DESIGN NOTES'),
    (1.27,
     'TCA4311A (TI SCPS226C) facts this sheet relies on:\n'
     ' - Features: powered-off high-impedance I2C pins, open-drain I2C pins, open-drain READY.\n'
     ' - 8.4.1 Start-Up: UVLO until VCC > 2.5 V; during UVLO a 1 V precharge is forced onto all\n'
     '   four SDA/SCL pins through 100 kOhm nominal.  Out of UVLO the part waits for a STOP bit\n'
     '   or bus idle on the IN side AND for both SDAOUT/SCLOUT high before it connects.\n'
     ' - 8.3.2 READY: open-drain, low while EN is low or start-up is incomplete, sinks 3 mA at\n'
     '   0.4 V; TI specifies a 10 kOhm pull-up to VCC.\n'
     ' - 8.3.3 EN low: isolates IN from OUT, disables the accelerators and the precharge, drives\n'
     '   READY low, near-zero supply current.  6.3: VCC 2.7-5.5 V, EN VIH 2 V min.\n'
     ' - 8.3.1: 2 mA rise-time accelerators above 0.6 V.  8.4.3 missing-ACK behaviour applies to\n'
     '   the emulated channels exactly as it does to the real faces.\n'
     '=> an emulated face answers only after the FC turns FACEn_ENABLE on and the buffer finishes\n'
     '   start-up: firmware sees the real face power-up timing.'),
    (1.27,
     'Loading (brief 6.2): on faces 1-5 Fn_PWR carries only the buffer VCC + 100 nF, the EN and\n'
     'READY 10 k straps, the two 4.7 k device-side pull-ups (PM ruling R7; Face 0 keeps its 10 k),\n'
     'the 4.7 k sense tap and a probe pad - no other load.  Face 0 also carries the real face\n'
     'devices, exactly as XY_Face_V4 does.  Sense taps are 4.7 k (<= 8.2 k, RP2350 erratum E9) and\n'
     'limit back-feed into an unpowered emulator ESD diode to about 0.55 mA per line.\n'
     'The emulator drives every EMU_*_SDA/SCL open-drain only (brief 6.1), so an off face is never\n'
     'back-powered through its 4.7 k pull-ups.  FC-side 4.7 k pull-ups already exist on\n'
     'Fn_SDA/Fn_SCL/BATT_SDA/BATT_SCL/SDA_Top/SCL_Top (R44 R45 R61 R62 R88 R89 R105 R106 ...).'),
    (1.27,
     'I2C map presented to the FC TCA9548 U3:\n'
     '  ch0 = F0 real : TMP112 0x48 (ADD0 = GND), VEML6031X00 0x29, DRV2605L 0x5A\n'
     '  ch1-ch3 = F1-F3, ch5 = F4, ch6 = F5 : emulated, same address map\n'
     '  ch4 = BATT : four emulated TMP112 (battery_pack_v2 U2 U4 U5 U6)\n'
     '  ch7 = TOP  : emulated VEML6031X00 + TMP112 (antenna_top_cap_v2c U3 U4)\n'
     'DO NOT plug a real face board into J1/J2/J6/J9/J11/J13, a real pack into J14 or a real top-cap\n'
     'into J16 while this emulation is fitted: both answer at one address on that channel (D11).'),
    (1.27,
     'Face 0 magnetorquer load R304: XY_Face_V4.kicad_pcb routes the coil as 10 520.7 mm of 0.25 mm\n'
     'track, 10 427 mm of it on In1.Cu/In2.Cu.  With the JLC 4-layer default (1 oz outer, 0.5 oz\n'
     'inner) that is 41.2 Ohm, so R304 = 43 R.  At maximum DRV2605L output the H-bridge puts\n'
     'VDD = 3.3 V across it: 77 mA and 0.253 W, so R304 is a 2010 (0.75 W = 34 % of rating);\n'
     'keep full-amplitude drive to <= 50 % duty.  Remove R304 when a real coil is fitted to J300.'),
    (1.27,
     'Provenance: faces 0-5 copy XY_Face_V4 U4 (EN and READY each 10 k to VCC); BATT copies\n'
     'battery_pack_v2 U3 (EN 10 k to +3V3, READY left open - marked no-connect here); TOP copies\n'
     'antenna_top_cap_v2c U6 (EN and READY each 10 k to +3V3).  The BATT and TOP buffers run from\n'
     'the FC +3V3, which is what J14.11 and J16.6 feed on the real pack and top-cap boards.'),
    (1.27,
     'D7: the emulator answers behind the same TCA4311A front-ends the real boards use, only while\n'
     'the FC has that face switch on.  Nothing on this sheet is in series with a flight power path;\n'
     'every connection to an FC net is a tap or a probe pad.  No PWR_FLAG is placed here - GND,\n'
     '+3V3 and F0..F5_PWR are existing FC nets owned by the FC sheets (brief 4.2).'),
]


READ_NOTE = (
    'Each channel shows its supply label (Fn_PWR, or +3V3 on the BATT and TOP channels) at THREE\n'
    'points: the buffer VCC on the left, the device-side SDA pull-up rail above, and the SCL +\n'
    'READY pull-up tap below the two exits.  They are one net.  The split exists so that no riser\n'
    'runs through the EMU_* global-label text on its way to the rail - a wire drawn across a label\n'
    'reads like a connection that is not there.  Fix round 2, verifier finding 2; the whole sheet\n'
    'is swept for wire-through-text by tools/gen/geomcheck.py (0 hits as delivered).')


E9_NOTE = (
    'The 14 EMU_*_SDA/SCL nets defined here are pulled up through 4.7 k (R312/R313, R322/R323,\n'
    'R332/R333, R342/R343, R352/R353, R362/R363, R372/R373) - PM ruling R7, review fix id 3.\n'
    'Brief rule 10 wants <= 8.2 k on every emulator input: on RP2350 A2 silicon an enabled input\n'
    'buffer leaks up to 120 uA, and 120 uA x 10 k = 1.2 V would sit above VIL(max) =\n'
    '0.3 x IOVDD = 0.99 V, so an off face could read as neither a real high nor a real low.\n'
    'Faces 1-5: with Fn_PWR off the pad now sees 4.7 k in series with the AP22653 output-discharge\n'
    'NMOS (600 Ohm typ, DS41186 electrical characteristics; active whenever the switch is disabled)\n'
    '= 5.3 k <= 8.2 k, so 120 uA x 5.3 k = 0.64 V < 0.99 V.  Rule 10 is met in HARDWARE; keeping\n'
    'these GPIOs input-buffer-disabled while EMU_Fn_SENSE is low is now belt-and-braces, not the\n'
    'only guard.  BATT/TOP pull up to the FC +3V3 (off only with the whole FC); the 4.7 k sense\n'
    'taps R314 R324 R334 R344 R354 R374 meet rule 10 the same way.  Face 0 keeps 10 k (R302/R303)\n'
    'per R7 - real face silicon read by the FC, not an emulator input.  Bus loading at 4.7 k is\n'
    '0.70 mA per line at 3.3 V, inside the TCA4311A 3 mA at VOL = 0.4 V sink spec (SCPS226C 6.5).')


def block_note(sh, x, y0, heading, body):
    """A headed note in the free band below the face row (the right-hand note column
    already runs down to the FACE 3 box).  KiCad centres a multi-line text block on
    its anchor, so the body anchor sits at the centre of the space it needs."""
    sh.text(heading, (x, y0), 1.778)
    lines = body.count('\n') + 1
    h = lines * 1.27 * 1.62
    sh.text(body, (x, y0 + 3.81 + h / 2.0 - 1.27 * 0.81), 1.27)


def notes(sh, x, y0, gap=1.8):
    """KiCad centres a multi-line text block vertically on its anchor, so place each
    block's anchor at the centre of the vertical space it needs."""
    y = y0
    for size, body in NOTE_BLOCKS:
        lines = body.count('\n') + 1
        h = lines * size * 1.62
        sh.text(body, (x, y + h / 2.0 - size * 0.81), size)
        y += h + gap
    return y


def build():
    sh = Sheet()
    sh.text('PROVES FlatSat V1 - Phase 1     SOLAR AND SENSOR EMULATION     (sheet 8)',
            (20.32, 17.78), 2.54)
    sh.text('Face 0 is real reference silicon; faces 1-5, the battery pack TMP112s and the antenna top-cap pair are emulated behind their own TCA4311A hot-swap buffers.',
            (20.32, 21.59), 1.27)

    face0(sh)

    cols = [63.5, 160.02, 256.54, 353.06]
    rowA, rowB = 152.4, 215.9

    faces = [
        (1, cols[0], rowA, 'R31', 'C310', 'U310'),
        (2, cols[1], rowA, 'R32', 'C311', 'U311'),
        (3, cols[2], rowA, 'R33', 'C312', 'U312'),
        (4, cols[3], rowA, 'R34', 'C313', 'U313'),
        (5, cols[0], rowB, 'R35', 'C314', 'U314'),
    ]
    mux = {1: 'ch1', 2: 'ch2', 3: 'ch3', 4: 'ch5', 5: 'ch6'}
    conn = {1: 'J9', 2: 'J11', 3: 'J13', 4: 'J1', 5: 'J2'}
    for n, X, Y, rb, cref, uref in faces:
        channel(sh, X, Y,
                'FACE %d - EMULATED  (%s, TCA9548 %s)' % (n, conn[n], mux[n]),
                uref, rb, cref,
                'F%d_SDA' % n, 'F%d_SCL' % n,
                'EMU_F%d_SDA' % n, 'EMU_F%d_SCL' % n,
                ('glabel', 'F%d_PWR' % n), 'EMU_F%d_SENSE' % n, True,
                tp_note='VCC = F%d_PWR (AP22653 face switch); dead until the FC turns face %d on.' % (n, n))

    channel(sh, cols[1], rowB,
            'BATTERY PACK CHANNEL - EMULATED  (J14.10/12, ch4)',
            'U315', 'R36', 'C315',
            'BATT_SDA', 'BATT_SCL', 'EMU_BATT_SDA', 'EMU_BATT_SCL',
            ('+3V3', None), None, False,
            tp_note='Copies battery_pack_v2 U3 exactly: READY left open, EN 10 k to +3V3.')

    channel(sh, cols[2], rowB,
            'ANTENNA TOP-CAP CHANNEL - EMULATED  (J16.5/7, ch7)',
            'U316', 'R37', 'C316',
            'SDA_Top', 'SCL_Top', 'EMU_TOP_SDA', 'EMU_TOP_SCL',
            ('+3V3', None), 'EMU_FC3V3_SENSE', True,
            tp_note='Copies antenna_top_cap_v2c U6.  The sense tap reports FC +3V3 presence.')

    testpoints(sh, cols[3], rowB)

    notes(sh, 264.16, 25.4)
    block_note(sh, 20.32, 254.0,
               'RP2350 ERRATUM E9 AND THE 4.7 k DEVICE-SIDE PULL-UPS   (brief rule 10; PM R7)',
               E9_NOTE)
    block_note(sh, 160.02, 254.0, 'READING THE CHANNEL BLOCKS', READ_NOTE)

    return sh


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(PROJ, 'solar_emulation.kicad_sch'))
    a = ap.parse_args()
    sh = build()
    text = sh.render()
    tmp = a.out + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(text)
    os.replace(tmp, a.out)
    refs = sorted({s['ref'] for s in sh.symbols if not s['ref'].startswith('#')})
    print('wrote %s: %d symbols (%d refdes), %d wires, %d junctions, %d labels'
          % (a.out, len(sh.symbols), len(refs), len(sh.wires), len(sh.junctions),
             len(sh.labels)))
    print('refdes:', ' '.join(refs))


if __name__ == '__main__':
    sys.exit(main())
