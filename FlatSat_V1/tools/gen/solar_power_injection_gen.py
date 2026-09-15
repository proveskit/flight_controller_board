#!/usr/bin/env python3
"""Generator for solar_power_injection.kicad_sch (PROVES FlatSat V1, Phase 1, sheet 9).

Two independent bench VSOLAR injection channels (PM brief §6.3, decision D2):
  screw terminal -> fuse -> series Schottky -> open jumper header -> VSOLAR (global)
CH-A: JP400 shunt fitted by default (active). CH-B: JP401 shunt open by default
(footprint present, inactive until a shunt is installed).

Writes atomically: <out>.tmp then os.replace() over the target.

Usage: python3 tools/gen/solar_power_injection_gen.py [--out PATH]
"""
import argparse
import math
import os
import random
import textwrap
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
PROJ = os.path.dirname(TOOLS)
# Checked-in symbol pantry (tools/pantry); $FLATSAT_PANTRY overrides it.  Never a
# session scratch path: the generator must run from a clean checkout (review fix 13).
PANTRY = os.environ.get('FLATSAT_PANTRY', os.path.join(TOOLS, 'pantry'))

ROOT_UUID = 'c64c0d72-a9f6-4f3a-891e-1f647558f538'
SHEET_UUID = '88d5f13b-6a4a-4f50-805f-872821082e52'
PROJECT = 'FlatSat_V1'
PATH = '/%s/%s' % (ROOT_UUID, SHEET_UUID)

T1 = '\t'
T2 = '\t\t'


# Review fix 14: deterministic uuid4 stream.  Emission order is fixed, so seeding the
# RNG makes a regeneration byte-identical to the committed sheet instead of churning
# every uuid (which would orphan any layout that had already been placed from it).
# Set FLATSAT_FRESH_UUIDS=1 to get real random uuids (only when re-keying a sheet).
_rng = random.Random('flatsat-solar_power_injection-2026-09-14')
_FRESH = os.environ.get('FLATSAT_FRESH_UUIDS') == '1'


def u():
    if _FRESH:
        return str(uuid.uuid4())
    return str(uuid.UUID(int=_rng.getrandbits(128), version=4))


# ---------- pin transform (matches tools/sch_lint.py exactly) ----------
def tf(x0, y0, rot, mirror, px, py):
    x, y = px, -py
    if mirror == 'x':
        y = -y
    elif mirror == 'y':
        x = -x
    r = math.radians(rot)
    xr = x * math.cos(r) + y * math.sin(r)
    yr = -x * math.sin(r) + y * math.cos(r)
    return round(x0 + xr, 2), round(y0 + yr, 2)


# local pin coordinates (from the pantry lib_symbols blocks, verified by hand)
PINS = {
    'power:GND': {'1': (0, 0)},
    'flatsat:VSOLAR_BENCH': {'1': (0, 0)},
    'power:PWR_FLAG': {'1': (0, 0)},
    'Connector:TestPoint': {'1': (0, 0)},
    'Connector:Screw_Terminal_01x02': {'1': (-5.08, 0), '2': (-5.08, -2.54)},
    'Device:Polyfuse': {'1': (0, 3.81), '2': (0, -3.81)},
    'Device:D_Schottky': {'1': (-3.81, 0), '2': (3.81, 0)},  # 1=K cathode, 2=A anode
    'Jumper:Jumper_2_Open': {'1': (-5.08, 0), '2': (5.08, 0)},
}


class Part:
    def __init__(self, lib_id, ref, value, footprint='', datasheet='', description='',
                 lcsc=None, x=0, y=0, rot=0, mirror=None, is_power=False, label_side=False,
                 value_dy=2.794):
        self.lib_id = lib_id
        self.ref = ref
        self.value = value
        self.footprint = footprint
        self.datasheet = datasheet
        self.description = description
        self.lcsc = lcsc
        self.x, self.y, self.rot, self.mirror = x, y, rot, mirror
        self.is_power = is_power
        self.label_side = label_side  # place Ref/Value to the right, clear of a small vertical symbol body
        self.value_dy = value_dy  # vertical offset of the Value field below the reference (non-label_side only)
        self.uuid = u()

    def pin(self, num):
        px, py = PINS[self.lib_id][num]
        return tf(self.x, self.y, self.rot, self.mirror, px, py)

    def sexp(self):
        out = []
        out.append('%s(symbol' % T1)
        out.append('%s\t(lib_id "%s")' % (T1, self.lib_id))
        at = '%s\t(at %s %s%s)' % (T1, fmt(self.x), fmt(self.y), (' %s' % fmt(self.rot)) if self.rot else (' 0' if True else ''))
        out.append(at)
        if self.mirror:
            out.append('%s\t(mirror %s)' % (T1, self.mirror))
        out.append('%s\t(unit 1)' % T1)
        out.append('%s\t(body_style 1)' % T1)
        out.append('%s\t(exclude_from_sim no)' % T1)
        out.append('%s\t(in_bom yes)' % T1)
        out.append('%s\t(on_board yes)' % T1)
        out.append('%s\t(in_pos_files yes)' % T1)
        out.append('%s\t(dnp no)' % T1)
        if self.is_power:
            out.append('%s\t(fields_autoplaced yes)' % T1)
        out.append('%s\t(uuid "%s")' % (T1, self.uuid))
        # KiCad composes a field's rendered angle from (parent symbol rotation + field's own
        # stored rotation), mod 180, to pick the text axis (horizontal vs vertical) -- so a
        # field stored at "0" on a symbol rotated 90 degrees renders vertically. Store the
        # inverse of the symbol rotation on every field so text always ends up horizontal.
        # Empirically (verified by rendering and reading the exported SVG's <text> transforms):
        # KiCad only rotates a field to follow its parent symbol's rotation when that rotation
        # is 90 or 270 (it renders a field stored at "0" unrotated for a parent at 0 OR 180,
        # mirrored or not). So only the 90/270 case needs a field-rotation to compensate back
        # to horizontal, readable text.
        frot = (360 - self.rot) % 360 if self.rot in (90, 270) else 0
        if self.label_side:
            out.append(prop(2, 'Reference', self.ref, self.x + 3.81, self.y - 1.27, hide=self.is_power, rot=frot, justify='left'))
            out.append(prop(2, 'Value', self.value, self.x + 3.81, self.y + 1.27, hide=False, rot=frot, justify='left'))
        else:
            out.append(prop(2, 'Reference', self.ref, self.x, self.y - 2.794, hide=self.is_power, rot=frot))
            out.append(prop(2, 'Value', self.value, self.x, self.y + self.value_dy, hide=False, rot=frot))
        out.append(prop(2, 'Footprint', self.footprint, self.x, self.y, hide=True))
        out.append(prop(2, 'Datasheet', self.datasheet, self.x, self.y, hide=True))
        out.append(prop(2, 'Description', self.description, self.x, self.y, hide=True))
        if self.lcsc:
            out.append(prop(2, 'LCSC Part', self.lcsc, self.x, self.y, hide=True))
        for num in PINS[self.lib_id]:
            out.append('%s\t(pin "%s"' % (T1, num))
            out.append('%s\t\t(uuid "%s")' % (T1, u()))
            out.append('%s\t)' % T1)
        out.append('%s\t(instances' % T1)
        out.append('%s\t\t(project "%s"' % (T1, PROJECT))
        out.append('%s\t\t\t(path "%s"' % (T1, PATH))
        out.append('%s\t\t\t\t(reference "%s")' % (T1, self.ref))
        out.append('%s\t\t\t\t(unit 1)' % T1)
        out.append('%s\t\t\t)' % T1)
        out.append('%s\t\t)' % T1)
        out.append('%s\t)' % T1)
        out.append('%s)' % T1)
        return '\n'.join(out)


def fmt(v):
    s = ('%.4f' % v).rstrip('0').rstrip('.')
    return s if s else '0'


def prop(depth, name, value, x, y, hide, rot=0, justify=None):
    tabs = T1 * depth
    lines = []
    val = value.replace('\\', '\\\\').replace('"', '\\"')
    lines.append('%s(property "%s" "%s"' % (tabs, name, val))
    lines.append('%s\t(at %s %s %s)' % (tabs, fmt(x), fmt(y), rot))
    lines.append('%s\t(show_name no)' % tabs)
    lines.append('%s\t(do_not_autoplace yes)' % tabs)
    if hide:
        lines.append('%s\t(hide yes)' % tabs)
    lines.append('%s\t(effects' % tabs)
    lines.append('%s\t\t(font' % tabs)
    lines.append('%s\t\t\t(size 1.27 1.27)' % tabs)
    lines.append('%s\t\t)' % tabs)
    if justify:
        lines.append('%s\t\t(justify %s)' % (tabs, justify))
    lines.append('%s\t)' % tabs)
    lines.append('%s)' % tabs)
    return '\n'.join(lines)


def wire(p1, p2):
    L = []
    L.append('%s(wire' % T1)
    L.append('%s\t(pts' % T1)
    L.append('%s\t\t(xy %s %s) (xy %s %s)' % (T1, fmt(p1[0]), fmt(p1[1]), fmt(p2[0]), fmt(p2[1])))
    L.append('%s\t)' % T1)
    L.append('%s\t(stroke' % T1)
    L.append('%s\t\t(width 0)' % T1)
    L.append('%s\t\t(type default)' % T1)
    L.append('%s\t)' % T1)
    L.append('%s\t(uuid "%s")' % (T1, u()))
    L.append('%s)' % T1)
    return '\n'.join(L)


def junction(p):
    L = []
    L.append('%s(junction' % T1)
    L.append('%s\t(at %s %s)' % (T1, fmt(p[0]), fmt(p[1])))
    L.append('%s\t(diameter 0)' % T1)
    L.append('%s\t(color 0 0 0 0)' % T1)
    L.append('%s\t(uuid "%s")' % (T1, u()))
    L.append('%s)' % T1)
    return '\n'.join(L)


def global_label(name, at, shape='bidirectional', rot=0, justify='left'):
    x, y = at
    L = []
    L.append('%s(global_label "%s"' % (T1, name))
    L.append('%s\t(shape %s)' % (T1, shape))
    L.append('%s\t(at %s %s %s)' % (T1, fmt(x), fmt(y), rot))
    L.append('%s\t(fields_autoplaced yes)' % T1)
    L.append('%s\t(effects' % T1)
    L.append('%s\t\t(font' % T1)
    L.append('%s\t\t\t(size 1.27 1.27)' % T1)
    L.append('%s\t\t)' % T1)
    L.append('%s\t\t(justify %s)' % (T1, justify))
    L.append('%s\t)' % T1)
    L.append('%s\t(uuid "%s")' % (T1, u()))
    L.append('%s\t(property "Intersheetrefs" "${INTERSHEET_REFS}"' % T1)
    L.append('%s\t\t(at %s %s 0)' % (T1, fmt(x - 5.5 if justify == 'left' else x + 5.5), fmt(y)))
    L.append('%s\t\t(hide yes)' % T1)
    L.append('%s\t\t(show_name no)' % T1)
    L.append('%s\t\t(do_not_autoplace no)' % T1)
    L.append('%s\t\t(effects' % T1)
    L.append('%s\t\t\t(font' % T1)
    L.append('%s\t\t\t\t(size 1.27 1.27)' % T1)
    L.append('%s\t\t\t)' % T1)
    L.append('%s\t\t\t(justify %s)' % (T1, justify))
    L.append('%s\t\t)' % T1)
    L.append('%s\t)' % T1)
    L.append('%s)' % T1)
    return '\n'.join(L)


def text(s, x, y, size=1.778):
    L = []
    L.append('%s(text "%s"' % (T1, s.replace('"', '\\"')))
    L.append('%s\t(exclude_from_sim no)' % T1)
    L.append('%s\t(at %s %s 0)' % (T1, fmt(x), fmt(y)))
    L.append('%s\t(effects' % T1)
    L.append('%s\t\t(font' % T1)
    L.append('%s\t\t\t(size %s %s)' % (T1, size, size))
    L.append('%s\t\t)' % T1)
    L.append('%s\t\t(justify left bottom)' % T1)
    L.append('%s\t)' % T1)
    L.append('%s\t(uuid "%s")' % (T1, u()))
    L.append('%s)' % T1)
    return '\n'.join(L)


def add_note(all_texts, s, x, y, width=150, line_pitch=2.0, size=1.27):
    """Word-wrap a long note into several stacked (text ...) items so no line runs off the
    sheet's right edge (fix round 2: a 532-char unwrapped line was measured at x=20..420.2mm
    on the A3 page, past the ~397mm inner border). width=150 chars keeps every line under
    ~133mm wide (20 + 150*0.7526mm/char), far inside the ~390mm safe edge. Returns the y just
    past the last emitted line (add the inter-note gap on top of that)."""
    for ln in textwrap.wrap(s, width=width, break_long_words=False, break_on_hyphens=False):
        all_texts.append(text(ln, x, y, size=size))
        y += line_pitch
    return y


def pwr_flag(x, y, ref):
    p = Part('power:PWR_FLAG', ref, 'PWR_FLAG', is_power=True, x=x, y=y)
    return p


def build_channel(letter, row_y, tp_vsolar_shared):
    """Returns (parts, wires, junctions, global_label_str, texts) for one channel."""
    n = '400' if letter == 'A' else '401'
    x_term, x_fuse, x_diode, x_jump = 50.8, 127.0, 165.1, 193.04
    parts = []
    wires_ = []
    junctions_ = []
    texts_ = []

    # Supply chain (Phase 2 stage 1): footprint-compatible with the Phoenix MKDS-1,5-2-5.08
    # this footprint is named for, but sourced from JLC stock as the Kangnex WJ2EDGKA
    # 5.08 mm horizontal-termination screw terminal (query: parts MATCH 'terminal' AND
    # Description LIKE '%5.08mm%' AND '%1x2P%' AND '%Horizontal Termination%', straight/
    # through-hole orientation only -- ORDER BY Stock DESC -> C8409, stock 9409, Extended).
    term = Part('Connector:Screw_Terminal_01x02', 'J%s' % n,
                'Terminal_2P_5.08mm',
                'TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal',
                'https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/1912251633_Ningbo-Kangnex-Elec-WJ2EDGKA-5-08-2P_C8409.pdf',
                'Bench VSOLAR CH-%s input, 5.08 mm pitch, footprint-compatible with Phoenix '
                'MKDS-1,5-2-5.08; sourced as Ningbo Kangnex WJ2EDGKA-5.08-02P-14-00A (LCSC C8409)'
                % letter,
                lcsc='C8409', x=x_term, y=row_y, rot=180, mirror='x',
                value_dy=6.35)  # fix round 2: default 2.794 offset drew the Value string through the
                                 # rotated/mirrored screw-terminal body; 6.35 clears it below the symbol
    # Integrator fix round 2: the 1.60 A / 24 V Bourns part forced this sheet to narrow the
    # brief's 24 V bench hard maximum to 20 V.  Littelfuse 2920L185DR is the brief's own
    # "1.85 A polyfuse" and is 33 V, so both deviations go away together.
    fuse = Part('Device:Polyfuse', 'F%s' % n, '1.85A_PTC_33V',
                'Fuse:Fuse_2920_7451Metric',
                'https://www.littelfuse.com/assetdocs/resettable-ptcs-2920l-datasheet'
                '?assetguid=f237e8c2-1ed9-4c13-a738-dbe0738b3d2c',
                'PTC resettable fuse, Littelfuse 2920L185DR: 1.85 A Ihold / 3.70 A Itrip / 33 V Vmax / '
                '40 A Imax, Rmin 0.050 ohm / R1max 0.150 ohm '
                "(brief 6.3 '1.85 A polyfuse'; 2 A slow-blow >=32 V equally acceptable)",
                lcsc='C207086', x=x_fuse, y=row_y, rot=90)
    diode = Part('Device:D_Schottky', 'D%s' % n, 'CDBA240LL-HF',
                 'Diode_SMD:D_SMA',
                 'https://www.lcsc.com/product-detail/Schottky-Barrier-Diodes-SBD_Comchip-CDBA240LL-HF_C2886093.html',
                 '40V 2A Schottky, series reverse-polarity/injection diode (as XY_Face_V4)',
                 lcsc='C2886093', x=x_diode, y=row_y, rot=180)
    # Supply chain (Phase 2 stage 1): 2.54 mm straight THT pin header (query: Second
    # Category = 'Pin Headers' AND Description LIKE '%1x2P%' AND '%2.54mm%', excluding
    # Right Angle/SMD -> C492401 XFCN PZ254V-11-02P, stock 1,222,203, Extended).
    jump = Part('Jumper:Jumper_2_Open', 'JP%s' % n, 'Jumper_2_Open',
                'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
                'https://www.lcsc.com/datasheet/lcsc_datasheet_2409302300_XFCN-PZ254V-11-02P_C492401.pdf',
                'CH-%s VSOLAR injection shunt (%s by default, rule 9); sourced as XFCN '
                'PZ254V-11-02P 2.54 mm THT pin header (LCSC C492401)' %
                (letter, 'fitted' if letter == 'A' else 'OPEN, not fitted'),
                lcsc='C492401', x=x_jump, y=row_y)
    parts += [term, fuse, diode, jump]

    t1 = term.pin('1')
    t2 = term.pin('2')
    f1 = fuse.pin('1')
    f2 = fuse.pin('2')
    da = diode.pin('2')  # anode
    dk = diode.pin('1')  # cathode
    ja = jump.pin('1')
    jb = jump.pin('2')

    tap1 = (68.58, row_y)
    tap2 = (88.9, row_y)
    tap3 = (109.22, row_y)

    wires_.append(wire(t1, tap1))
    wires_.append(wire(tap1, tap2))
    wires_.append(wire(tap2, tap3))
    wires_.append(wire(tap3, f1))
    wires_.append(wire(f2, da))
    wires_.append(wire(dk, ja))
    # No junction on t1: only the terminal pin and one wire end meet there, so a dot would
    # paint a branch that does not exist (integrator fix round 2, checker finding).
    junctions_ += [junction(tap1), junction(tap2), junction(tap3)]

    # GND stub off terminal pin 2
    gnd = Part('power:GND', '#PWR%s' % ('400' if letter == 'A' else '402'), 'GND', is_power=True,
               x=t2[0], y=t2[1] + 7.62, label_side=True)
    parts.append(gnd)
    wires_.append(wire(t2, gnd.pin('1')))

    # VSOLAR_BENCH_x rail: power symbol + PWR_FLAG + test point, tapped above the row,
    # each on its own tap so the (wide) Value text of one never overlaps its neighbour.
    cy = row_y - 15.24
    vb = Part('flatsat:VSOLAR_BENCH', '#PWR%s' % ('401' if letter == 'A' else '403'),
              'VSOLAR_BENCH_%s' % letter, is_power=True, x=tap1[0], y=cy, label_side=True)
    fl = Part('power:PWR_FLAG', '#FLG%s' % ('400' if letter == 'A' else '401'), 'PWR_FLAG',
              is_power=True, x=tap2[0], y=cy, label_side=True)
    tpb = Part('Connector:TestPoint', 'TP%s' % ('400' if letter == 'A' else '402'),
               'VSOLAR_BENCH_%s' % letter, 'TestPoint:TestPoint_Pad_D1.5mm', '',
               'Bench test point, VSOLAR_BENCH_%s (pre-diode)' % letter, x=tap3[0], y=cy, label_side=True)
    parts += [vb, fl, tpb]
    wires_.append(wire(tap1, vb.pin('1')))
    wires_.append(wire(tap2, fl.pin('1')))
    wires_.append(wire(tap3, tpb.pin('1')))

    # final leg: jumper -> (optional shared VSOLAR test point tap) -> global label
    lbl_at = (x_jump + 17.78, row_y)
    if tp_vsolar_shared:
        tap4 = (jb[0] + 8.89, row_y)
        wires_.append(wire(jb, tap4))
        wires_.append(wire(tap4, lbl_at))
        junctions_.append(junction(tap4))
        tpv = Part('Connector:TestPoint', 'TP401', 'VSOLAR',
                   'TestPoint:TestPoint_Pad_D1.5mm', '', 'Bench test point, VSOLAR (shared, post-injection)',
                   x=tap4[0], y=cy, label_side=True)
        parts.append(tpv)
        wires_.append(wire(tap4, tpv.pin('1')))
    else:
        wires_.append(wire(jb, lbl_at))

    gl = global_label('VSOLAR', lbl_at, shape='bidirectional', rot=0, justify='left')

    texts_.append(text(
        'Channel %s -- bench VSOLAR injection (%s)' %
        (letter, 'fitted, JP%s shunt CLOSED by default' % n if letter == 'A'
         else 'footprint fitted, JP%s shunt OPEN by default -- D2' % n),
        x_term, cy - 12.7, size=1.778))

    return parts, wires_, junctions_, gl, texts_


def build():
    all_parts = []
    all_wires = []
    all_junctions = []
    all_globals = []
    all_texts = []

    pA, wA, jA, glA, tA = build_channel('A', 76.2, tp_vsolar_shared=True)
    pB, wB, jB, glB, tB = build_channel('B', 139.7, tp_vsolar_shared=False)
    all_parts += pA + pB
    all_wires += wA + wB
    all_junctions += jA + jB
    all_globals += [glA, glB]
    all_texts += tA + tB

    # title block
    all_texts.append(text('PROVES FlatSat V1 -- Phase 1', 20, 15.24, size=2.54))
    all_texts.append(text('Solar Power Injection', 20, 22.86, size=1.778))
    all_texts.append(text(
        'Two bench VSOLAR injection channels (PM brief section 6.3, decision D2). No per-face current '
        'limiting: all six FC face VSOLAR pins (J1/J2/J6/J9/J11/J13) are one net, so two independent '
        'bench channels are sufficient to demonstrate diode-OR / one-face-shadowed behaviour.',
        20, 27.94, size=1.27))

    notes_y = 160
    notes = [
        'Bench PSU setting: 12 V to 18 V nominal, HARD MAXIMUM 24 V (brief section 6.3; F400/F401 are '
        '33 V Vmax, so 9 V of margin). INA219 U8 (0x41) IN+ absolute maximum on VSOLAR is 26 V '
        '(eps_side.kicad_sch); LT3652 IC6 operating maximum input is 32 V. Startup needs VIN >= VFLOAT + '
        '3.3 V = 11.7 V for the 8.38 V float set by R71/R74 on eps_side. This 11.7 V threshold is at '
        'VSOLAR, downstream of F400/F401 (R1max 0.150 ohm) and D400/D401 (~0.25-0.31 V at <=1.2 A): the '
        'series drop is ~0.4-0.5 V at the expected bench current, so set the bench terminal to >=12.3 V '
        '(12.5 V recommended) to actually clear 11.7 V at VSOLAR -- a terminal reading of exactly 12.0 V '
        'will not reliably start the charger.',
        'FC finding (not repeated on this sheet, per brief section 6.3): eps_side.kicad_sch text note '
        '"VSOLAR 9V to 40V" near IC6 is INCORRECT -- 40 V exceeds both the INA219 U8 26 V absolute maximum '
        'and the LT3652 32 V maximum. See sheet_solar_power_injection.md.',
        'Reverse-polarity protection: series Schottky D400/D401 (anode toward the bench source) blocks '
        'reverse current into VSOLAR if the bench supply leads are swapped. No TVS fitted on '
        'VSOLAR_BENCH_A/B -- bench PSU overvoltage protection (OVP) is the primary defense (brief section 6.3).',
        'F400/F401: Littelfuse 2920L185DR PPTC resettable fuse (LCSC C207086, JLC Extended, SMD 2920/7451 '
        'metric): 1.85 A Ihold / 3.70 A Itrip / 33 V Vmax / 40 A Imax, Rmin 0.050 ohm, R1max 0.150 ohm, '
        'max time to trip 2.50 s at 8.00 A (Littelfuse 2920L Series datasheet, Electrical Characteristics '
        "table). This is the '1.85 A polyfuse' option of brief section 6.3; the '2 A slow-blow rated "
        ">=32 V' alternative is equally acceptable. Ihold is a 20 C ambient rating and derates with "
        'temperature. The datasheet Temperature Rerating table gives 2920L185 hold current = '
        '2.80 / 2.47 / 2.17 / 1.85 / 1.54 / 1.39 / 1.22 / 1.07 / 0.85 A at '
        '-40 / -20 / 0 / 20 / 40 / 50 / 60 / 70 / 85 C ambient, i.e. 1.54 A at 40 C against the <=1.2 A '
        'expected bench draw (eps_side IC6 R75 = 0.1 ohm sets the LT3652 1.0 A charge current) -- 28 % '
        "margin. 33 V Vmax leaves 9 V over the brief's 24 V hard maximum. Itrip (3.70 A) exceeds "
        'D400/D401 IF(AV) = 2 A, so in an overcurrent event the injection diode is protected by the bench '
        'PSU current limit, not by the PTC.',
        'J400/J401: 2-pin screw terminal, 5.08 mm pitch (footprint: TerminalBlock_Phoenix '
        'MKDS-1,5-2-5.08, true 5.08 mm pitch). Pin 1 = bench supply +; Pin 2 = bench supply - '
        '(wired to GND, NOT B-).',
        'Jumper table: JP400 (CH-A) SHUNT FITTED by default -> VSOLAR_BENCH_A active. JP401 (CH-B) shunt '
        'OPEN by default (not fitted) -> CH-B footprint present, inactive until a shunt is installed '
        '(PM brief D2). Both drawn as open 2-pin headers per rule 9 (Jumper:Jumper_2_Open); never a bridged '
        'symbol -- shunt state is an assembly note only, not a schematic short. JP400/JP401 are the only '
        'series element in each channel and can see the PTC Itrip fault current: a 2.54 mm gold-plated '
        'shunt is assumed, rated >= 3 A (typical for this pitch), against a <=1.2 A steady-state channel '
        'current. The PTC does not protect the shunt either (see F400/F401 note above) -- the bench PSU '
        'current limit must also be set <= the shunt rating.',
        'PWR_FLAG #FLG400/#FLG401 declare VSOLAR_BENCH_A/B as sourced nets for ERC (brief section 4.2 '
        'PWR_FLAG ownership table); this sheet owns both. No PWR_FLAG is placed on GND or VSOLAR (existing '
        'FC nets, rule: never a second power source on those).',
    ]
    ny = notes_y
    for n in notes:
        ny = add_note(all_texts, n, 20, ny)
        ny += 8.89 - 2.0  # inter-note gap on top of the last line already advanced by line_pitch

    return all_parts, all_wires, all_junctions, all_globals, all_texts


def lib_symbols_block():
    names = [
        'power_GND', 'flatsat_VSOLAR_BENCH', 'power_PWR_FLAG', 'Connector_TestPoint',
        'Connector_Screw_Terminal_01x02', 'Device_Polyfuse', 'Device_D_Schottky', 'Jumper_Jumper_2_Open',
    ]
    blocks = []
    for n in names:
        with open(os.path.join(PANTRY, n + '.sexp'), encoding='utf-8') as f:
            blocks.append(f.read().rstrip('\n'))
    return '\n'.join(blocks)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default=os.path.join(PROJ, 'solar_power_injection.kicad_sch'))
    a = ap.parse_args()

    parts, wires_, junctions_, globals_, texts_ = build()

    lines = []
    lines.append('(kicad_sch')
    lines.append('%s(version 20260306)' % T1)
    lines.append('%s(generator "eeschema")' % T1)
    lines.append('%s(generator_version "10.0")' % T1)
    lines.append('%s(uuid "%s")' % (T1, u()))
    lines.append('%s(paper "A3")' % T1)
    lines.append('%s(lib_symbols' % T1)
    lines.append(lib_symbols_block())
    lines.append('%s)' % T1)

    for t in texts_:
        lines.append(t)
    for w in wires_:
        lines.append(w)
    for j in junctions_:
        lines.append(j)
    for g in globals_:
        lines.append(g)
    for p in parts:
        lines.append(p.sexp())

    lines.append(')')
    content = '\n'.join(lines) + '\n'

    tmp = a.out + '.tmp'
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(content)
    os.replace(tmp, a.out)
    print('wrote %s (%d parts, %d wires, %d junctions, %d global labels, %d texts)' %
          (a.out, len(parts), len(wires_), len(junctions_), len(globals_), len(texts_)))


if __name__ == '__main__':
    main()
