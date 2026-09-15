#!/usr/bin/env python3
"""Generator for FlatSat_V1/emulator_mcu.kicad_sch  ("Emulator MCU", page 7).

PROVES FlatSat V1 - Phase 1 schematic capture, brief section 6.1.

Builds the whole sheet from validated pantry lib_symbols blocks:
  * lib symbol pin/property geometry is parsed out of the pantry .sexp files and
    transformed exactly the way tools/sch_lint.py does, so wires always land on pins;
  * wires are emitted as explicit segments between consecutive attachment points, so
    every attachment is a wire endpoint (no pin sitting mid-segment);
  * junctions are placed automatically wherever >= 3 connected items meet;
  * uuids come from a seeded uuid4 stream, so re-running reproduces the committed sheet
    byte for byte (FLATSAT_FRESH_UUIDS=1 forces real random uuids);
  * the file is written atomically (tmp + os.replace).

Run:  python3 tools/gen/emulator_mcu_gen.py [-o emulator_mcu.kicad_sch]
"""
import argparse
import math
import os
import random
import re
import uuid
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
# Checked-in symbol pantry (tools/pantry); $FLATSAT_PANTRY overrides it.  Never a
# session scratch path: the generator must run from a clean checkout (review fix 13).
PANTRY = os.environ.get('FLATSAT_PANTRY', os.path.join(HERE, '..', 'pantry'))
PROJECT = 'FlatSat_V1'
ROOT_UUID = 'c64c0d72-a9f6-4f3a-891e-1f647558f538'
SHEET_UUID = '8394a2ec-8c1e-41a1-b086-be3289cedfbc'
INST_PATH = '/%s/%s' % (ROOT_UUID, SHEET_UUID)
GRID = 1.27

DS_RP2350 = 'https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf'
DS_FLASH = 'https://www.winbond.com/hq/product/code-storage-flash-memory/serial-nor-flash/?__locale=en&partNo=W25Q128JV'
DS_LDO = 'https://www.diodes.com/assets/Datasheets/AP2112.pdf'
DS_XTAL = 'https://abracon.com/Resonators/abm8.pdf'
DS_NSR = 'https://www.onsemi.com/download/data-sheet/pdf/nsr0320-d.pdf'
DS_LED = 'https://www.lcsc.com/datasheet/lcsc_datasheet_2305091500_Hubei-KENTO-Elec-KT-0603W_C2290.pdf'
DS_L200 = 'https://www.lcsc.com/datasheet/lcsc_datasheet_2412101620_Abracon-LLC-AOTA-B201610S3R3-101-T_C42411119.pdf'


# ----------------------------------------------------------------- s-expr parse
def parse(text):
    tokens = re.findall(r'\(|\)|"(?:[^"\\]|\\.)*"|[^\s()]+', text)
    stack = [[]]
    for t in tokens:
        if t == '(':
            stack.append([])
        elif t == ')':
            node = stack.pop()
            stack[-1].append(node)
        else:
            if t.startswith('"') and t.endswith('"') and len(t) >= 2:
                t = t[1:-1]
            stack[-1].append(t)
    return stack[0]


def head(n):
    return n[0] if isinstance(n, list) and n and isinstance(n[0], str) else None


def child(n, name):
    for c in n:
        if isinstance(c, list) and head(c) == name:
            return c
    return None


def children(n, name):
    return [c for c in n if isinstance(c, list) and head(c) == name]


def pantry_file(lib_id):
    return os.path.join(PANTRY, re.sub(r'[:/ ()]', '_', lib_id) + '.sexp')


class LibSym:
    """One pantry (symbol "Lib:Name" ...) block: raw text + pin/property geometry."""

    def __init__(self, lib_id):
        self.lib_id = lib_id
        self.text = open(pantry_file(lib_id), encoding='utf-8').read().rstrip('\n')
        node = parse(self.text)[0]
        self.pins = {}          # number -> (px, py)
        self.pin_order = []
        for sub in children(node, 'symbol'):
            for p in children(sub, 'pin'):
                at = child(p, 'at')
                num = child(p, 'number')
                if at and num:
                    self.pins[num[1]] = (float(at[1]), float(at[2]))
                    self.pin_order.append(num[1])
        self.props = {}         # name -> (px, py, angle, value)
        for p in children(node, 'property'):
            at = child(p, 'at')
            self.props[p[1]] = (float(at[1]), float(at[2]),
                                float(at[3]) if len(at) > 3 else 0.0, p[2])


_LIBS = {}


def lib(lib_id):
    if lib_id not in _LIBS:
        _LIBS[lib_id] = LibSym(lib_id)
    return _LIBS[lib_id]


def xform(px, py, x0, y0, rot):
    """lib (px,py) -> schematic (x,y), same transform as tools/sch_lint.py."""
    x, y = px, -py
    r = math.radians(rot)
    xr = x * math.cos(r) + y * math.sin(r)
    yr = -x * math.sin(r) + y * math.cos(r)
    return round(x0 + xr, 4), round(y0 + yr, 4)


# Review fix 14: deterministic uuid4 stream.  Emission order is fixed, so seeding the
# RNG makes a regeneration byte-identical to the committed sheet instead of churning
# every uuid (which would orphan any layout that had already been placed from it).
# Set FLATSAT_FRESH_UUIDS=1 to get real random uuids (only when re-keying a sheet).
_rng = random.Random('flatsat-emulator_mcu-2026-09-14')
_FRESH = os.environ.get('FLATSAT_FRESH_UUIDS') == '1'


def uid():
    if _FRESH:
        return str(uuid.uuid4())
    return str(uuid.UUID(int=_rng.getrandbits(128), version=4))


def q(x):
    s = ('%.4f' % x).rstrip('0').rstrip('.')
    return '0' if s in ('', '-0') else s


# ----------------------------------------------------------------- sheet model
class Sheet:
    def __init__(self):
        self.items = []                 # rendered s-expression chunks
        self.used_libs = []
        self.wire_ends = Counter()      # (x,y) -> number of wire endpoints
        self.segments = []              # ((x1,y1),(x2,y2))
        self.pin_pts = Counter()        # (x,y) -> number of symbol pins
        self.label_pts = set()
        self.refs = {}                  # prefix -> next number
        self.parts = []                 # bookkeeping for the report

    # ---- refdes
    def ref(self, prefix, start=200):
        n = self.refs.get(prefix, start)
        self.refs[prefix] = n + 1
        return '%s%d' % (prefix, n)

    # ---- primitives
    def wire(self, p1, p2):
        p1 = (round(p1[0], 4), round(p1[1], 4))
        p2 = (round(p2[0], 4), round(p2[1], 4))
        if p1 == p2:
            return
        self.wire_ends[p1] += 1
        self.wire_ends[p2] += 1
        self.segments.append((p1, p2))
        self.items.append(
            '\t(wire\n\t\t(pts\n\t\t\t(xy %s %s) (xy %s %s)\n\t\t)\n'
            '\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n'
            '\t\t(uuid "%s")\n\t)' % (q(p1[0]), q(p1[1]), q(p2[0]), q(p2[1]), uid()))

    def bus(self, y, xs, vertical=False):
        """Explicit segments between consecutive attachment coordinates."""
        for a, b in zip(xs, xs[1:]):
            if vertical:
                self.wire((y, a), (y, b))
            else:
                self.wire((a, y), (b, y))

    def label(self, name, x, y, rot=0, glob=False, shape='bidirectional'):
        self.label_pts.add((round(x, 4), round(y, 4)))
        just = '\n\t\t\t(justify right)' if rot == 180 else '\n\t\t\t(justify left)'
        if glob:
            self.items.append(
                '\t(global_label "%s"\n\t\t(shape %s)\n\t\t(at %s %s %d)\n'
                '\t\t(fields_autoplaced yes)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)%s\n\t\t)\n'
                '\t\t(uuid "%s")\n'
                '\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"\n\t\t\t(at %s %s 0)\n\t\t\t(hide yes)\n'
                '\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)%s\n\t\t\t)\n\t\t)\n\t)'
                % (name, shape, q(x), q(y), rot, just, uid(), q(x), q(y),
                   '\n\t\t\t\t(justify right)' if rot == 180 else '\n\t\t\t\t(justify left)'))
        else:
            j = 'right bottom' if rot == 180 else 'left bottom'
            self.items.append(
                '\t(label "%s"\n\t\t(at %s %s %d)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n'
                '\t\t\t(justify %s)\n\t\t)\n\t\t(uuid "%s")\n\t)'
                % (name, q(x), q(y), rot, j, uid()))

    def no_connect(self, x, y):
        self.label_pts.add((round(x, 4), round(y, 4)))
        self.items.append('\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid "%s")\n\t)'
                          % (q(x), q(y), uid()))

    def text(self, s, x, y, size=1.27, bold=False):
        b = '\n\t\t\t\t(bold yes)' if bold else ''
        self.items.append(
            '\t(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n'
            '\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)%s\n\t\t\t)\n\t\t\t(justify left)\n\t\t)\n'
            '\t\t(uuid "%s")\n\t)' % (s.replace('"', '\\"'), q(x), q(y), q(size), q(size), b, uid()))

    # ---- symbol placement
    def sym(self, lib_id, ref, x, y, rot=0, value=None, fp='', ds='', desc='',
            lcsc='', ref_at=None, val_at=None, hide_ref=False, hide_val=False,
            note=None):
        L = lib(lib_id)
        if lib_id not in self.used_libs:
            self.used_libs.append(lib_id)
        if value is None:
            value = L.props.get('Value', (0, 0, 0, ref))[3]

        def prop(name, val, px, py, pr, hide, show=False):
            hx, hy = (px, py)
            h = '\n\t\t\t(hide yes)' if hide else ''
            return ('\t\t(property "%s" "%s"\n\t\t\t(at %s %s %d)%s\n\t\t\t(show_name no)\n'
                    '\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)'
                    % (name, val.replace('"', '\\"'), q(hx), q(hy), pr, h))

        def libpos(name, fallback_dx=0.0, fallback_dy=0.0):
            if name in L.props:
                px, py, pa, _ = L.props[name]
                gx, gy = xform(px, py, x, y, rot)
                return gx, gy, int((pa + rot) % 180)
            gx, gy = x + fallback_dx, y + fallback_dy
            return gx, gy, 0

        if ref_at is None:
            rx, ry, ra = libpos('Reference', 2.54, -1.27)
        else:
            rx, ry, ra = ref_at[0], ref_at[1], (ref_at[2] if len(ref_at) > 2 else 0)
        if val_at is None:
            vx, vy, va = libpos('Value', 2.54, 1.905)
        else:
            vx, vy, va = val_at[0], val_at[1], (val_at[2] if len(val_at) > 2 else 0)

        props = [prop('Reference', ref, rx, ry, ra, hide_ref),
                 prop('Value', value, vx, vy, va, hide_val),
                 prop('Footprint', fp, x, y, 0, True),
                 prop('Datasheet', ds, x, y, 0, True),
                 prop('Description', desc, x, y, 0, True)]
        if lcsc:
            props.append(prop('LCSC Part', lcsc, x, y, 0, True))
        pins = ''.join('\n\t\t(pin "%s"\n\t\t\t(uuid "%s")\n\t\t)' % (n, uid())
                       for n in L.pin_order)
        self.items.append(
            '\t(symbol\n\t\t(lib_id "%s")\n\t\t(at %s %s %d)\n\t\t(unit 1)\n\t\t(body_style 1)\n'
            '\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(in_pos_files yes)\n'
            '\t\t(dnp no)\n\t\t(uuid "%s")\n%s%s\n'
            '\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "%s"\n\t\t\t\t\t(reference "%s")\n'
            '\t\t\t\t\t(unit 1)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)'
            % (lib_id, q(x), q(y), rot, uid(), '\n'.join(props), pins,
               PROJECT, INST_PATH, ref))

        pts = {}
        for num, (px, py) in L.pins.items():
            gx, gy = xform(px, py, x, y, rot)
            self.pin_pts[(gx, gy)] += 1
            pts[num] = (gx, gy)
        if not ref.startswith('#'):
            self.parts.append((ref, value, fp, lcsc, note or desc))
        return pts

    # ---- convenience blocks
    def gnd(self, x, y, rot=0, val_at=None):
        return self.sym('power:GND', self.ref('#PWR'), x, y, rot,
                        hide_ref=True, val_at=val_at)['1']

    def pwr(self, lib_id, x, y, rot=0):
        return self.sym(lib_id, self.ref('#PWR'), x, y, rot, hide_ref=True)['1']

    def pwr_flag(self, x, y, rot=0):
        return self.sym('power:PWR_FLAG', self.ref('#FLG'), x, y, rot,
                        hide_ref=True)['1']

    # ---- finish
    def auto_junctions(self):
        pts = set(self.wire_ends) | set(self.pin_pts)
        out = []
        for p in sorted(pts):
            n = self.wire_ends.get(p, 0) + self.pin_pts.get(p, 0)
            interior = False
            for (a, b) in self.segments:
                if p == a or p == b:
                    continue
                cross = (b[0] - a[0]) * (p[1] - a[1]) - (b[1] - a[1]) * (p[0] - a[0])
                if abs(cross) > 1e-6:
                    continue
                if (min(a[0], b[0]) - 1e-6 <= p[0] <= max(a[0], b[0]) + 1e-6 and
                        min(a[1], b[1]) - 1e-6 <= p[1] <= max(a[1], b[1]) + 1e-6):
                    interior = True
                    break
            if n >= 3 or (interior and n >= 1):
                out.append(p)
        for (x, y) in out:
            self.items.append('\t(junction\n\t\t(at %s %s)\n\t\t(diameter 0)\n'
                              '\t\t(color 0 0 0 0)\n\t\t(uuid "%s")\n\t)' % (q(x), q(y), uid()))
        return out

    def render(self):
        libs = '\n'.join(lib(l).text for l in sorted(self.used_libs))
        return ('(kicad_sch\n\t(version 20260306)\n\t(generator "eeschema")\n'
                '\t(generator_version "10.0")\n\t(uuid "%s")\n\t(paper "A3")\n'
                '\t(lib_symbols\n%s\n\t)\n%s\n)\n'
                % (uid(), libs, '\n'.join(self.items)))


# =============================================================== sheet contents
MCU_X, MCU_Y = 177.8, 140.97
LEFT_STUB = 140.97                      # x where left-pin stubs end (labels)
RIGHT_STUB = 217.17                     # x where right-pin stubs end (labels)

# GPIO map: (pin number, net name, global?, shape, comment for the report)
RIGHT_PINS = [
    ('52', 'EMU_USB_DP', True, 'bidirectional'),
    ('51', 'EMU_USB_DM', True, 'bidirectional'),
    ('2', 'EMU_F1_SDA', True, 'bidirectional'),
    ('3', 'EMU_F1_SCL', True, 'bidirectional'),
    ('4', 'EMU_F2_SDA', True, 'bidirectional'),
    ('5', 'EMU_F2_SCL', True, 'bidirectional'),
    ('7', 'EMU_F3_SDA', True, 'bidirectional'),
    ('8', 'EMU_F3_SCL', True, 'bidirectional'),
    ('9', 'EMU_F4_SDA', True, 'bidirectional'),
    ('10', 'EMU_F4_SCL', True, 'bidirectional'),
    ('12', 'EMU_F5_SDA', True, 'bidirectional'),
    ('13', 'EMU_F5_SCL', True, 'bidirectional'),
    ('14', 'EMU_BATT_SDA', True, 'bidirectional'),
    ('15', 'EMU_BATT_SCL', True, 'bidirectional'),
    ('16', 'EMU_TOP_SDA', True, 'bidirectional'),
    ('17', 'EMU_TOP_SCL', True, 'bidirectional'),
    ('18', 'EMU_CTL_FC_RESET', True, 'output'),
    ('19', 'EMU_CTL_USBBOOT', True, 'output'),
    ('27', 'EMU_UART_TX', True, 'output'),
    ('28', 'EMU_UART_RX', True, 'input'),
    ('29', 'EMU_CTL_WDT_DIS', True, 'output'),
    ('31', 'EMU_STATUS_LED', False, ''),
    ('32', 'EMU_GPIO_SPARE0', True, 'bidirectional'),
    ('33', 'EMU_GPIO_SPARE1', True, 'bidirectional'),
    ('34', 'EMU_FC3V3_SENSE', True, 'input'),
    ('35', 'PYRO_INHIBIT_STATE', True, 'input'),
    ('36', 'EMU_F5_SENSE', True, 'input'),
    ('37', 'EMU_GPIO_RSVD', False, ''),
    ('40', 'EMU_F1_SENSE', True, 'input'),
    ('41', 'EMU_F2_SENSE', True, 'input'),
    ('42', 'EMU_F3_SENSE', True, 'input'),
    ('43', 'EMU_F4_SENSE', True, 'input'),
]

# VREG group: (pin, net, global?, shape, turn-x, label-y).  Lower pins turn
# further left and rise higher, so no two wires cross and no two labels touch.
VREG_PINS = [
    ('46', 'VREG_AVDD_EMU', False, '', 140.97, 97.79),
    ('49', '3V3_EMU', True, 'input', 138.43, 93.98),
    ('50', '1V1_EMU', False, '', 135.89, 90.17),
    ('48', 'EMU_VREG_LX', False, '', 133.35, 86.36),
]

LEFT_PINS = [
    ('60', 'EMU_QSPI_SS', False, ''),
    ('57', 'EMU_QSPI_SD0', False, ''),
    ('59', 'EMU_QSPI_SD1', False, ''),
    ('58', 'EMU_QSPI_SD2', False, ''),
    ('55', 'EMU_QSPI_SD3', False, ''),
    ('56', 'EMU_QSPI_SCLK', False, ''),
    ('21', 'EMU_XIN', False, ''),
    ('22', 'EMU_XOUT', False, ''),
    ('26', 'EMU_RUN', True, 'output'),
    ('24', 'EMU_SWCLK', True, 'input'),
    ('25', 'EMU_SWDIO', True, 'bidirectional'),
]

IOVDD_PINS = ['45', '38', '30', '20', '11', '1']      # left to right on the top edge
DVDD_PINS = ['39', '23', '6']


def build_mcu(s):
    """U200 RP2350A + its top-edge power rails + left/right pin stubs."""
    u = s.sym('MCU_RaspberryPi_RP2350:RP2350_60QFN', 'U200', MCU_X, MCU_Y, 0,
              value='RP2350A', fp='RP2350_60QFN_minimal:RP2350-QFN-60-1EP_7x7_P0.4mm_EP3.4x3.4mm_ThermalVias',
              ds=DS_RP2350, desc='RP2350A dual Cortex-M33/Hazard3 MCU, QFN-60 (emulator)',
              lcsc='C42411118',
              ref_at=(150.495, 195.58), val_at=(150.495, 198.12),
              note='emulator MCU, same part/footprint as FC U18')

    # ---- right edge: one 7.62 mm stub + label per pin
    for num, net, glob, shape in RIGHT_PINS:
        x, y = u[num]
        end = RIGHT_STUB if glob else 241.3
        s.wire((x, y), (end, y))
        s.label(net, end, y, 0, glob, shape or 'bidirectional')

    # ---- left edge: stubs + labels (VREG_PGND goes straight to GND)
    for num, net, glob, shape in LEFT_PINS:
        x, y = u[num]
        s.wire((x, y), (LEFT_STUB, y))
        s.label(net, LEFT_STUB, y, 180, glob, shape or 'bidirectional')
    for num, net, glob, shape, tx, ty in VREG_PINS:
        x, y = u[num]
        s.wire((x, y), (tx, y))
        s.wire((tx, y), (tx, ty))
        s.label(net, tx, ty, 180, glob, shape or 'bidirectional')
    x, y = u['47']                                        # VREG_PGND
    s.wire((x, y), (130.81, y))
    s.gnd(130.81, y, 270, val_at=(124.46, y))

    # ---- bottom: exposed pad / GND
    x, y = u['61']
    s.wire((x, y), (x, y + 2.54))
    s.gnd(x, y + 2.54)

    # ---- top edge: 1V1_EMU rail (3 DVDD pins) and 3V3_EMU rail (9 pins)
    ytop = u['1'][1]
    yrail = 82.55
    dv = sorted(u[p][0] for p in DVDD_PINS)
    s.bus(yrail, [152.4] + dv)
    for x in dv:
        s.wire((x, yrail), (x, ytop))
    s.label('1V1_EMU', 152.4, yrail, 180)

    v3 = sorted([u['54'][0]] + [u[p][0] for p in IOVDD_PINS] + [u['53'][0], u['44'][0]])
    s.bus(yrail, v3 + [201.93])
    for x in v3:
        s.wire((x, yrail), (x, ytop))
    s.wire((201.93, yrail), (201.93, 63.5))               # up to the decoupling rail
    return u


C0402 = 'Capacitor_SMD:C_0402_1005Metric'
C0603 = 'Capacitor_SMD:C_0603_1608Metric'
C0805 = 'Capacitor_SMD:C_0805_2012Metric'
C0402S = 'RP2350_60QFN_minimal:C_0402_1005Metric_small_pads'
R0402 = 'Resistor_SMD:R_0402_1005Metric'
TPFP = 'TestPoint:TestPoint_Pad_D1.5mm'


def cap(s, ref, x, y_top, value, fp, lcsc, desc, gnd_rot=0, drop=2.54):
    """Vertical Device:C from a rail at y_top down to its own GND symbol."""
    p = s.sym('Device:C', ref, x, y_top + 3.81, 0, value=value, fp=fp,
              desc=desc, lcsc=lcsc)
    s.wire(p['2'], (x, p['2'][1] + drop))
    s.gnd(x, p['2'][1] + drop, gnd_rot)
    return p


def res_v(s, ref, x, y_centre, value, lcsc, desc, fp=R0402):
    # the pantry Device:R carries its Value field on the body; place both explicitly
    return s.sym('Device:R', ref, x, y_centre, 0, value=value, fp=fp,
                 ref_at=(x + 2.54, y_centre, 90), val_at=(x - 2.54, y_centre, 90),
                 desc=desc, lcsc=lcsc)


def res_h(s, ref, x_centre, y, value, lcsc, desc, fp=R0402):
    return s.sym('Device:R', ref, x_centre, y, 90, value=value, fp=fp,
                 ref_at=(x_centre, y - 2.54, 0), val_at=(x_centre, y + 2.54, 0),
                 desc=desc, lcsc=lcsc)


def testpoint(s, ref, x, y, net):
    return s.sym('Connector:TestPoint', ref, x, y, 0, value=net, fp=TPFP,
                 ref_at=(x + 2.54, y - 3.81), val_at=(x + 2.54, y - 1.27),
                 desc='Bench test point on %s' % net)


def build_power(s):
    """Block A: VBUS_EMU -> AP2112K-3.3 -> 3V3_EMU, bulk caps, TPs, power LED."""
    u = s.sym('Regulator_Linear:AP2112K-3.3', 'U202', 76.2, 53.34, 0,
              ref_at=(68.58, 44.45), val_at=(68.58, 41.91),
              value='AP2112K-3.3', fp='Package_TO_SOT_SMD:SOT-23-5', ds=DS_LDO,
              desc='600 mA LDO, 5 V VBUS_EMU -> 3.3 V 3V3_EMU', lcsc='C51118',
              note='LCSC verified live at lcsc.com/product-detail/C51118.html')
    yr = 50.8
    s.bus(yr, [33.02, 40.64, 48.26, 55.88, 66.04, u['1'][0]])
    s.pwr('flatsat:VBUS_EMU', 33.02, yr)
    testpoint(s, 'TP200', 40.64, yr, 'VBUS_EMU')
    # Integrator, cross-sheet fix: bench_io already fits C701 = 10 uF at the USB-C connector
    # (brief 6.6 "with bulk cap"), so a second 10 uF here put 20.1 uF on VBUS_EMU against the
    # USB 2.0 s7.2.4.1 10 uF downstream-device bypass limit.  1 uF is the AP2112 datasheet's own
    # input recommendation (Rev 2.0 p.1, "stable with 1.0 uF"); C15849 is the as-ordered Rev2
    # BOM part (1uF,"C37,C4,C41",C_0603_1608Metric,C15849,3).  See integration_report.md 2.2.
    cap(s, 'C200', 48.26, yr, '1uF', C0603, 'C15849',
        'U202 AP2112K input cap (CIN 1uF per AP2112 DS p.1); VBUS_EMU bulk lives on bench_io C701 '
        '(integration fix, see integration_report.md)')
    cap(s, 'C201', 55.88, yr, '100nF', C0402, 'C1525', 'VBUS_EMU HF bypass')
    s.wire((66.04, yr), (66.04, u['3'][1]))                 # EN tied to VIN
    s.wire((66.04, u['3'][1]), u['3'])
    s.no_connect(*u['4'])
    s.wire(u['2'], (u['2'][0], u['2'][1] + 2.54))
    s.gnd(u['2'][0], u['2'][1] + 2.54)

    s.bus(yr, [u['5'][0], 91.44, 99.06, 106.68, 114.3])
    testpoint(s, 'TP201', 91.44, yr, '3V3_EMU')
    cap(s, 'C202', 99.06, yr, '10uF', C0603, 'C19702', '3V3_EMU bulk')
    cap(s, 'C203', 106.68, yr, '100nF', C0402, 'C1525', '3V3_EMU HF bypass')
    s.pwr('flatsat:3V3_EMU', 114.3, yr)

    # power LED
    s.pwr('flatsat:3V3_EMU', 35.56, 66.04)
    s.wire((35.56, 66.04), (35.56, 69.85))
    r = res_v(s, 'R211', 35.56, 73.66, '1k', 'C11702', '3V3_EMU power LED series R')
    s.wire(r['2'], (35.56, 80.01))
    d = s.sym('Device:LED', 'D201', 35.56, 83.82, 90, value='LED', fp='LED_SMD:LED_0603_1608Metric',
              ref_at=(30.48, 83.82, 90), val_at=(40.64, 83.82, 90), ds=DS_LED,
              desc='Power LED, lit whenever 3V3_EMU is up', lcsc='C2290')
    s.wire((35.56, 80.01), d['2'])
    s.wire(d['1'], (35.56, 90.17))
    s.gnd(35.56, 90.17)


def build_decoupling(s):
    """Block B: 3V3_EMU decoupling farm feeding the MCU top-edge rail."""
    rowb = [152.4, 160.02, 167.64, 175.26, 182.88]
    rowa = [152.4, 160.02, 167.64, 175.26, 182.88, 190.5]
    s.bus(45.72, [146.05] + rowb)
    s.pwr('flatsat:3V3_EMU', 146.05, 45.72)
    s.wire((146.05, 45.72), (146.05, 63.5))
    s.bus(63.5, [146.05] + rowa + [201.93])
    names = ['C204', 'C205', 'C206', 'C207', 'C208']
    for ref, x in zip(names, rowb):
        cap(s, ref, x, 45.72, '100nF', C0402, 'C1525', 'RP2350 IOVDD decoupling')
    cap(s, 'C209', rowa[0], 63.5, '100nF', C0402, 'C1525', 'RP2350 IOVDD decoupling')
    cap(s, 'C210', rowa[1], 63.5, '100nF', C0402, 'C1525', 'RP2350 IOVDD decoupling')
    cap(s, 'C211', rowa[2], 63.5, '100nF', C0402, 'C1525', 'RP2350 QSPI_IOVDD decoupling')
    cap(s, 'C212', rowa[3], 63.5, '100nF', C0402, 'C1525', 'RP2350 USB_OTP_VDD decoupling')
    cap(s, 'C213', rowa[4], 63.5, '4.7uF', C0402S, 'C23733', '3V3_EMU local bulk at the MCU')
    cap(s, 'C214', rowa[5], 63.5, '10uF', C0805, 'C15850', '3V3_EMU bulk at the MCU')


def build_core_reg(s):
    """Islands C1/C2: VREG_AVDD_EMU filter and the 1V1_EMU core rail."""
    s.pwr('flatsat:3V3_EMU', 30.48, 100.33)
    s.wire((30.48, 100.33), (30.48, 104.14))
    r = res_v(s, 'R200', 30.48, 107.95, '33', 'C25105',
              'RP2350 VREG_AVDD RC filter (FC R94 parity)')
    s.wire(r['2'], (30.48, 114.3))
    s.bus(114.3, [30.48, 40.64, 50.8, 60.96])
    cap(s, 'C215', 40.64, 114.3, '4.7uF', C0402S, 'C23733', 'RP2350 VREG_AVDD bypass')
    s.wire((50.8, 114.3), (50.8, 110.49))
    s.pwr_flag(50.8, 110.49)
    s.label('VREG_AVDD_EMU', 60.96, 114.3, 0)

    s.label('EMU_VREG_LX', 33.02, 135.89, 180)
    s.wire((33.02, 135.89), (38.1, 135.89))
    l = s.sym('Device:L', 'L200', 41.91, 135.89, 90, value='3.3u',
              ref_at=(41.91, 131.44, 0), val_at=(41.91, 140.34, 0),
              fp='RP2350_60QFN_minimal:L_pol_2016', lcsc='C42411119', ds=DS_L200,
              desc='RP2350 internal core buck inductor (FC L3 parity)')
    s.wire((45.72, 135.89), (48.26, 135.89))
    s.bus(135.89, [48.26, 55.88, 63.5, 71.12, 78.74, 86.36, 101.6, 109.22])
    cap(s, 'C216', 55.88, 135.89, '4.7uF', C0402S, 'C23733', '1V1_EMU core bulk')
    cap(s, 'C217', 63.5, 135.89, '4.7uF', C0402S, 'C23733', '1V1_EMU core bulk')
    cap(s, 'C218', 71.12, 135.89, '100nF', C0402, 'C1525', '1V1_EMU HF bypass')
    cap(s, 'C219', 78.74, 135.89, '100nF', C0402, 'C1525', '1V1_EMU HF bypass')
    s.wire((86.36, 135.89), (86.36, 132.08))
    testpoint(s, 'TP202', 86.36, 132.08, '1V1_EMU')
    s.wire((101.6, 135.89), (101.6, 132.08))
    s.pwr_flag(101.6, 132.08)
    s.label('1V1_EMU', 109.22, 135.89, 0)
    return l


def build_flash(s):
    """Island D: W25Q128JVS QSPI flash + its decoupling."""
    u = s.sym('Memory_Flash:W25Q128JVS', 'U201', 66.04, 184.15, 0,
              ref_at=(55.88, 195.58), val_at=(55.88, 198.12), value='W25Q128JVS', fp='Package_SO:SOIC-8_5.3x5.3mm_P1.27mm',
              ds=DS_FLASH, desc='128 Mbit QSPI NOR flash (emulator boot flash)',
              lcsc='C97521')
    s.wire(u['8'], (66.04, 170.18))
    s.pwr('flatsat:3V3_EMU', 66.04, 170.18)
    s.wire(u['4'], (66.04, 196.85))
    s.gnd(66.04, 196.85)
    for pin, net in (('1', 'EMU_FLASH_SS'), ('6', 'EMU_QSPI_SCLK')):
        s.wire(u[pin], (48.26, u[pin][1]))
        s.label(net, 48.26, u[pin][1], 180)
    for pin, net in (('5', 'EMU_QSPI_SD0'), ('2', 'EMU_QSPI_SD1'),
                     ('3', 'EMU_QSPI_SD2'), ('7', 'EMU_QSPI_SD3')):
        s.wire(u[pin], (83.82, u[pin][1]))
        s.label(net, 83.82, u[pin][1], 0)
    # flash VCC decoupling (own island on the same 3V3_EMU net)
    s.pwr('flatsat:3V3_EMU', 30.48, 170.18)
    s.wire((30.48, 170.18), (30.48, 172.72))
    cap(s, 'C220', 30.48, 172.72, '100nF', C0402, 'C1525', 'U201 VCC decoupling')


def build_crystal(s):
    """Island E: 12 MHz ABM8-272-T3 with 15 pF loads and the XOUT series R."""
    y = 215.9
    Y = s.sym('Device:Crystal_GND24', 'Y200', 66.04, y, 0, value='ABM8-272-T3',
              ref_at=(50.8, 208.28), val_at=(50.8, 210.82),
              fp='Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm', ds=DS_XTAL,
              desc='12 MHz crystal, 2 x 15 pF load (FC Y1 parity)', lcsc='C20625731')
    s.wire(Y['2'], (66.04, 208.28))
    s.gnd(66.04, 208.28, 180)
    s.wire(Y['4'], (66.04, 223.52))
    s.gnd(66.04, 223.52)
    s.bus(y, [48.26, 57.15, Y['1'][0]])
    s.label('EMU_XIN', 48.26, y, 180)
    cap(s, 'C221', 57.15, y, '15pF', C0402, 'C1548', 'XIN load capacitor')
    s.bus(y, [Y['3'][0], 76.2, 81.28])
    cap(s, 'C222', 76.2, y, '15pF', C0402, 'C1548', 'XOUT load capacitor')
    res_h(s, 'R201', 85.09, y, '1k', 'C11702', 'XOUT drive-level series R (FC R93 parity)')
    s.wire((88.9, y), (93.98, y))
    s.label('EMU_XOUT', 93.98, y, 0)


def build_boot(s):
    """Island F: EMU_RUN pull-up and the QSPI_SS / BOOTSEL arrangement."""
    s.pwr('flatsat:3V3_EMU', 25.4, 243.84)
    s.wire((25.4, 243.84), (25.4, 247.65))
    r = res_v(s, 'R205', 25.4, 251.46, '10k', 'C25744', 'EMU_RUN pull-up to 3V3_EMU')
    s.wire(r['2'], (33.02, 255.27))
    s.label('EMU_RUN', 33.02, 255.27, 0, True, 'output')

    y = 265.43
    s.label('EMU_QSPI_SS', 60.96, y, 180)
    s.bus(y, [60.96, 63.5, 66.04])
    res_h(s, 'R203', 69.85, y, '0', 'C17168', 'QSPI_SS to FLASH_SS link (FC R91 parity)')
    s.bus(y, [73.66, 76.2, 83.82])
    s.label('EMU_FLASH_SS', 83.82, y, 0)
    s.wire((76.2, y), (76.2, 260.35))
    r2 = res_v(s, 'R202', 76.2, 256.54, '10k', 'C25744', 'FLASH_SS pull-up (FC R2 parity)')
    s.wire(r2['1'], (76.2, 250.19))
    s.pwr('flatsat:3V3_EMU', 76.2, 250.19)

    s.wire((63.5, y), (63.5, 271.78))
    res_h(s, 'R204', 67.31, 271.78, '1k', 'C11702',
          'BOOTSEL series R to the boot button (FC R10 parity)')
    s.wire((71.12, 271.78), (76.2, 271.78))
    d = s.sym('Diode:1SS355VM', 'D200', 80.01, 271.78, 180, value='NSR0320',
              ref_at=(76.2, 276.86), val_at=(76.2, 279.4),
              fp='Diode_SMD:D_SOD-323F', ds=DS_NSR, lcsc='C48192',
              desc='Boot-button isolation Schottky (FC D4 parity)')
    ka = {n: p for n, p in d.items()}
    s.wire((83.82, 271.78), (88.9, 271.78))
    s.label('EMU_BOOTSEL_SW', 88.9, 271.78, 0, True, 'output')
    return ka


def build_side(s):
    """Island H: status LED and the RP2350-E9 default-state pulls."""
    y = 104.14
    s.label('EMU_STATUS_LED', 271.78, y, 180)
    s.wire((271.78, y), (276.86, y))
    res_h(s, 'R206', 280.67, y, '1k', 'C11702', 'Status LED series R (GPIO19 sources ~1.3 mA)')
    s.wire((284.48, y), (289.56, y))
    d = s.sym('Device:LED', 'D202', 293.37, y, 180, value='LED',
              ref_at=(290.83, 99.06), val_at=(290.83, 110.49),
              fp='LED_SMD:LED_0603_1608Metric', lcsc='C2290', ds=DS_LED,
              desc='Emulator status LED on GPIO19')
    s.wire((297.18, y), (302.26, y))
    s.gnd(302.26, y, 90)

    y = 127.0
    s.label('EMU_UART_RX', 271.78, y, 180, True, 'input')
    s.wire((271.78, y), (276.86, y))
    r = res_v(s, 'R207', 276.86, 123.19, '4.7k', 'C25900',
              'EMU_UART_RX idle-high pull-up, <= 8.2k per RP2350-E9')
    s.wire(r['1'], (276.86, 116.84))
    s.pwr('flatsat:3V3_EMU', 276.86, 116.84)

    for ref, net, y, glob in (('R208', 'EMU_GPIO_SPARE0', 147.32, True),
                              ('R209', 'EMU_GPIO_SPARE1', 167.64, True),
                              ('R210', 'EMU_GPIO_RSVD', 187.96, False)):
        s.label(net, 271.78, y, 180, glob, 'bidirectional')
        s.wire((271.78, y), (276.86, y))
        r = res_v(s, ref, 276.86, y + 3.81, '4.7k', 'C25900',
                  '%s default-low pull-down, <= 8.2k per RP2350-E9' % net)
        s.wire(r['2'], (276.86, y + 10.16))
        s.gnd(276.86, y + 10.16)
    s.wire((276.86, 187.96), (284.48, 187.96))
    testpoint(s, 'TP203', 284.48, 187.96, 'EMU_GPIO_RSVD')


HEAD_NOTES = [
    (15.24, 17.78, 2.54, True, 'EMULATOR MCU'),
    (15.24, 23.0, 1.778, False, 'PROVES FlatSat V1 - Phase 1 (sheet 7 of the FlatSat additions)'),
    (15.24, 28.0, 1.27, False,
     'Second RP2350A on its own USB-C supply (VBUS_EMU / 3V3_EMU), common GND with the FC.'),
    (15.24, 32.0, 1.27, False,
     'It answers as the I2C slave for solar faces 1-5, the battery-pack TMP112s and the'),
    (15.24, 36.0, 1.27, False,
     'antenna top-cap sensors, behind the TCA4311A front-ends on sheet Solar and Sensor Emulation.'),
]

SIDE_NOTES = [
    (True, 'POWER BUDGET AND REGULATOR CHOICE (brief 6.1, D7)'),
    (False, 'U202 AP2112K-3.3 LDO, 600 mA. Worst case on 3V3_EMU:'),
    (False, '   RP2350A core + IO, full PIO / USB activity     ~100 mA'),
    (False, '   U201 W25Q128JVS read burst                       ~25 mA'),
    (False, '   D201 power LED + D202 status LED                ~2.6 mA'),
    (False, '   R207..R210 E9 pulls + bench-header loads          ~5 mA'),
    (False, '   total                                           ~135 mA'),
    (False, 'Dissipation (5.0 - 3.3) x 0.135 = 0.23 W in SOT-23-5.'),
    (False, 'The seven TCA4311A buffers run from FC rails (F1..F5_PWR, +3V3),'),
    (False, 'not from 3V3_EMU, so they are not in this budget. The radio-stick'),
    (False, 'TPS62085 buck is not needed; the LDO is quieter beside the'),
    (False, 'emulated I2C and costs four fewer parts.'),
    (False, ''),
    (True, 'RP2350-E9 (A2 silicon, RP2350 datasheet Appendix E)'),
    (False, 'A GPIO left as an input with its input buffer enabled leaks up to'),
    (False, '120 uA and floats to about 2 V unless the external pull is 8.2 k'),
    (False, 'or less. Every input / default-state-sensitive emulator GPIO has'),
    (False, 'a 4.7 k pull:'),
    (False, '   EMU_F1..F5_SENSE, EMU_FC3V3_SENSE: 4.7 k series R on'),
    (False, '      sheet Solar and Sensor Emulation;'),
    (False, '   PYRO_INHIBIT_STATE: 4.7 k series R on sheet Pyro Inhibit;'),
    (False, '   EMU_CTL_FC_RESET / _USBBOOT / _WDT_DIS: 4.7 k gate'),
    (False, '      pull-downs on sheet Bench IO;'),
    (False, '   EMU_UART_RX (R207), EMU_GPIO_SPARE0/1 (R208/R209),'),
    (False, '      EMU_GPIO_RSVD (R210): on this sheet.'),
    (False, 'A4 stepping fixes E9; the 4.7 k values are kept regardless.'),
    (False, ''),
    (True, 'FIRMWARE RULES THAT THE HARDWARE ASSUMES'),
    (False, '1. Every EMU_*_SDA / EMU_*_SCL GPIO is OPEN-DRAIN ONLY. Never'),
    (False, '   drive one high: an off face would be back-powered through its'),
    (False, '   4.7 k device-side pull-ups (~0.70 mA per line into Fn_PWR).'),
    (False, '2. With a face off, its two pads see 4.7 k to 0 V, which already'),
    (False, '   meets the 8.2 k E9 limit in hardware (R7). Keeping that'),
    (False, '   channel input-buffer-disabled while EMU_Fn_SENSE reads low'),
    (False, '   is now belt-and-braces, not a requirement.'),
    (False, '3. EMU_CTL_* are outputs, default low (FET off, FC untouched).'),
    (False, ''),
    (True, 'PHANTOM POWER PATH (accepted - obey the BENCH RULE)'),
    (False, 'FC powered, emulator unpowered: the 14 device-side 4.7 k pull-'),
    (False, 'ups on solar_emulation push up to (3.3-0.7)/4.7k = 0.55 mA per'),
    (False, 'line, ~7.7 mA over 14 lines, into 3V3_EMU via the RP2350 pad'),
    (False, 'ESD diodes. Nothing is in series to block it.'),
    (False, 'U202 does NOT sink it: the AP2112K 60 ohm output discharge'),
    (False, '(datasheet Electrical Characteristics, RDCHG) needs EN LOW, and'),
    (False, 'EN is tied to VIN here, so with VBUS_EMU absent the LDO back-'),
    (False, 'feeds its own input instead. 3V3_EMU therefore floats to about'),
    (False, '2.6 V (one ESD-diode drop below Fn_PWR; R211/D201 hold it near'),
    (False, '2.4 V), leaving the RP2350 PARTIALLY POWERED, I/O UNDEFINED.'),
    (False, 'BENCH RULE: plug the emulator USB in before or with FC power;'),
    (False, 'never leave the FC powered with the emulator unplugged.'),
]

FOOT_NOTES = [
    (True, 'GPIO MAP - firmware contract (full table in sheet_emulator_mcu.md)'),
    (False, 'GP0/1    EMU_F1_SDA/SCL      PIO0 SM0   face 1  (TCA9548 ch1)'),
    (False, 'GP2/3    EMU_F2_SDA/SCL      PIO0 SM1   face 2  (ch2)'),
    (False, 'GP4/5    EMU_F3_SDA/SCL      PIO0 SM2   face 3  (ch3)'),
    (False, 'GP6/7    EMU_F4_SDA/SCL      PIO0 SM3   face 4  (ch5)'),
    (False, 'GP8/9    EMU_F5_SDA/SCL      PIO1 SM0   face 5  (ch6)'),
    (False, 'GP10/11  EMU_BATT_SDA/SCL    PIO1 SM1   pack TMP112 x4 (ch4)'),
    (False, 'GP12/13  EMU_TOP_SDA/SCL     PIO1 SM2   top cap VEML6031 + TMP112 (ch7)'),
    (False, 'GP14 EMU_CTL_FC_RESET   GP15 EMU_CTL_USBBOOT   GP18 EMU_CTL_WDT_DIS'),
    (False, 'GP16/17 EMU_UART_TX/RX (UART0)   GP19 status LED   GP20/21 spare'),
    (False, 'GP22 EMU_FC3V3_SENSE   GP23 PYRO_INHIBIT_STATE   GP24 EMU_F5_SENSE'),
    (False, 'GP25 EMU_GPIO_RSVD (TP203 only)  GP26-29 EMU_F1..F4_SENSE (ADC0-3)'),
    (False, 'Seven I2C-slave channels, one PIO state machine each: 7 of 12.'),
    (False, 'Each channel keeps SDA/SCL on adjacent GPIOs (PIO pin-group rule).'),
    (False, ''),
    (True, 'FC FACE <-> TCA9548 <-> FIRMWARE CROSSWALK (proves-core-reference 8e4d487)'),
    (False, 'EMU_F1/F2/F3 = FC F1/F2/F3 = ch1/ch2/ch3 = zephyr face1/face2/face3:  TMP112 0x48 + VEML6031 0x29 + DRV2605L 0x5A'),
    (False, 'EMU_F4 = FC F4 = ch5 = zephyr face5:  same three devices; Z- detumble face (Z_MINUS_RESISTANCE 150.7 ohm coil model)'),
    (False, 'EMU_F5 = FC F5 = ch6 = zephyr face6:  only the VEML6031 0x29 is instantiated in the current FSW topology'),
    (False, 'EMU_BATT = ch4:  TMP112 x4 at 0x48/0x49/0x4A/0x4B.  EMU_TOP = ch7 = zephyr face7:  VEML6031 0x29 (the real top cap'),
    (False, '   also carries TMP112 0x48; the dts top-cap-temp TODO is stale).  Firmware face = FC face for F0-F3, +1 for F4/F5.'),
    (False, ''),
    (True, 'INTERFACE NOTES'),
    (False, 'No +3V3 and no FC global label appears anywhere on this sheet'),
    (False, '(brief 6.1 and hard rule 8). Only 3V3_EMU / VBUS_EMU / 1V1_EMU.'),
    (False, 'USB_DP/USB_DM go straight to EMU_USB_DP / EMU_USB_DM: the 22 ohm'),
    (False, 'series resistors (C25092) and the USB-C live on sheet Bench IO.'),
    (False, 'The RP2350 needs no external USB pull-ups.'),
    (False, 'PWR_FLAGs on this sheet: 1V1_EMU and VREG_AVDD_EMU only. U202'),
    (False, 'VOUT already drives 3V3_EMU as a power output; the VBUS_EMU'),
    (False, 'PWR_FLAG belongs to sheet Bench IO (brief 4.2).'),
]


def build_notes(s):
    for x, y, size, bold, t in HEAD_NOTES:
        s.text(t, x, y, size, bold)
    # 3.5 mm pitch (was 4.0): the R7 / phantom-power rewrite lengthened this column and it
    # has to finish above y = 204, where the FOOT_NOTES "INTERFACE NOTES" column starts and
    # overlaps this column's x band (259.08 .. ~331 vs 313.69).
    y = 20.0
    for bold, t in SIDE_NOTES:
        if t:
            s.text(t, 313.69, y, 1.27, bold)
        y += 3.5
    x, y = 149.86, 204.0
    for bold, t in FOOT_NOTES:
        if t == 'INTERFACE NOTES':                 # second column
            x, y = 259.08, 204.0
        if t:
            s.text(t, x, y, 1.27, bold)
        y += 3.8


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-o', '--output', default=os.path.join(
        os.path.dirname(os.path.abspath(__file__)), '..', '..', 'emulator_mcu.kicad_sch'))
    a = ap.parse_args()
    s = Sheet()
    build_mcu(s)
    build_power(s)
    build_decoupling(s)
    build_core_reg(s)
    build_flash(s)
    build_crystal(s)
    build_boot(s)
    build_side(s)
    build_notes(s)
    s.auto_junctions()
    out = os.path.abspath(a.output)
    tmp = out + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(s.render())
    os.replace(tmp, out)
    offgrid = [p for p in list(s.wire_ends) + list(s.pin_pts)
               if abs(p[0] / GRID - round(p[0] / GRID)) > 1e-3
               or abs(p[1] / GRID - round(p[1] / GRID)) > 1e-3]
    print('wrote %s: %d items, %d parts, %d off-grid points'
          % (out, len(s.items), len(s.parts), len(offgrid)))
    for p in offgrid[:20]:
        print('  off-grid', p)
    for row in sorted(s.parts, key=lambda r: (r[0][0], int(re.sub(r'\D', '', r[0]) or 0))):
        print('  %-6s %-14s %-52s %s' % row[:4])


if __name__ == '__main__':
    main()
