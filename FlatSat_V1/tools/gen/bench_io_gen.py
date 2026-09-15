#!/usr/bin/env python3
"""Generator for bench_io.kicad_sch (PROVES FlatSat V1, Phase 1, brief section 6.6).

Emulator USB-C + SWD, FC bench control (open-drain FC_RESET/USBBOOT/WDT_DISABLE
drivers), WDT_DISABLE toggle, EMU_RUN / EMU_BOOTSEL_SW buttons, bench header.

Run: python3 tools/gen/bench_io_gen.py
Writes FlatSat_V1/bench_io.kicad_sch.tmp then renames atomically over the target.
"""
import math
import os
import random
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.dirname(os.path.dirname(HERE))
# Checked-in symbol pantry (tools/pantry); $FLATSAT_PANTRY overrides it.  Never a
# session scratch path: the generator must run from a clean checkout (review fix 13).
# Transistor_FET:BSS138 used to come from a scratch work dir; it now lives in the pantry too.
PANTRY = os.environ.get("FLATSAT_PANTRY", os.path.join(HERE, "..", "pantry"))

ROOT_UUID = "c64c0d72-a9f6-4f3a-891e-1f647558f538"
SHEET_UUID = "54b8f29e-9dcb-4e24-99b9-415a110b338a"
INST_PATH = f"/{ROOT_UUID}/{SHEET_UUID}"
PROJECT = "FlatSat_V1"

# Review fix 14: deterministic uuid4 stream.  Emission order is fixed, so seeding the
# RNG makes a regeneration byte-identical to the committed sheet instead of churning
# every uuid (which would orphan any layout that had already been placed from it).
# Set FLATSAT_FRESH_UUIDS=1 to get real random uuids (only when re-keying a sheet).
_rng = random.Random("flatsat-bench_io-2026-09-14")
_FRESH = os.environ.get("FLATSAT_FRESH_UUIDS") == "1"

def u():
    if _FRESH:
        return str(uuid.uuid4())
    return str(uuid.UUID(int=_rng.getrandbits(128), version=4))

def rd(v):
    return round(v, 2)

def transform(px, py, x0, y0, rot, mirror=None):
    """Same transform sch_lint.py uses: lib pin (px,py) -> sheet coords."""
    x, y = px, -py
    if mirror == 'x':
        y = -y
    elif mirror == 'y':
        x = -x
    r = math.radians(rot)
    xr = x * math.cos(r) + y * math.sin(r)
    yr = -x * math.sin(r) + y * math.cos(r)
    return rd(x0 + xr), rd(y0 + yr)

# ---------- pin tables (number -> (px, py)) taken from pantry lib_symbols ----------
PINS = {
    'mainboard:RESISTOR0603': {'1': (-5.08, 0), '2': (5.08, 0)},
    'Device:C': {'1': (0, 3.81), '2': (0, -3.81)},
    'power:GND': {'1': (0, 0)},
    'power:PWR_FLAG': {'1': (0, 0)},
    'flatsat:VBUS_EMU': {'1': (0, 0)},
    'flatsat:3V3_EMU': {'1': (0, 0)},
    'Connector:TestPoint': {'1': (0, 0)},
    'Connector:USB_C_Receptacle_USB2.0_16P': {
        'A1': (0, -22.86), 'A4': (15.24, 15.24), 'A5': (15.24, 10.16),
        'A6': (15.24, -2.54), 'A7': (15.24, 2.54), 'A8': (15.24, -12.7),
        'A9': (15.24, 15.24), 'A12': (0, -22.86),
        'B1': (0, -22.86), 'B4': (15.24, 15.24), 'B5': (15.24, 7.62),
        'B6': (15.24, -5.08), 'B7': (15.24, 0), 'B8': (15.24, -15.24),
        'B9': (15.24, 15.24), 'B12': (0, -22.86),
        'S1': (-7.62, -22.86),
    },
    'Connector_Generic:Conn_01x03': {'1': (-5.08, 2.54), '2': (-5.08, 0), '3': (-5.08, -2.54)},
    'Connector_Generic:Conn_02x05_Odd_Even': {
        '1': (-5.08, 5.08), '2': (7.62, 5.08),
        '3': (-5.08, 2.54), '4': (7.62, 2.54),
        '5': (-5.08, 0), '6': (7.62, 0),
        '7': (-5.08, -2.54), '8': (7.62, -2.54),
        '9': (-5.08, -5.08), '10': (7.62, -5.08),
    },
    'Switch:SW_SPST': {'1': (-5.08, 0), '2': (5.08, 0)},
    # SW_SPDT: pin 2 ('B') is the common wiper (connects to the circle at local
    # x=-2.032,y=0); pins 1 ('A') and 3 ('C') are the two throws.
    'Switch:SW_SPDT': {'1': (5.08, 2.54), '2': (-5.08, 0), '3': (5.08, -2.54)},
    'Adafruit ItsyBitsy RP2040-eagle-import:SWITCH_TACT_SMT4.6X2.8': {
        'A': (-5.08, 0), "A'": (-5.08, -2.54), 'B': (5.08, 0), "B'": (5.08, -2.54),
    },
    # BSS138: same G/S/D = pin 1/2/3 geometry as 2N7002 (both SOT-23, pin_names hidden).
    'Transistor_FET:BSS138': {'1': (-5.08, 0), '2': (2.54, -5.08), '3': (2.54, 5.08)},
}

# lib_symbols source files (verbatim pantry / fetched blocks)
LIB_FILES = {
    'mainboard:RESISTOR0603': f'{PANTRY}/mainboard_RESISTOR0603.sexp',
    'Device:C': f'{PANTRY}/Device_C.sexp',
    'power:GND': f'{PANTRY}/power_GND.sexp',
    'power:PWR_FLAG': f'{PANTRY}/power_PWR_FLAG.sexp',
    'flatsat:VBUS_EMU': f'{PANTRY}/flatsat_VBUS_EMU.sexp',
    'flatsat:3V3_EMU': f'{PANTRY}/flatsat_3V3_EMU.sexp',
    'Connector:TestPoint': f'{PANTRY}/Connector_TestPoint.sexp',
    'Connector:USB_C_Receptacle_USB2.0_16P': f'{PANTRY}/Connector_USB_C_Receptacle_USB2.0_16P.sexp',
    'Connector_Generic:Conn_01x03': f'{PANTRY}/Connector_Generic_Conn_01x03.sexp',
    'Connector_Generic:Conn_02x05_Odd_Even': f'{PANTRY}/Connector_Generic_Conn_02x05_Odd_Even.sexp',
    'Switch:SW_SPST': f'{PANTRY}/Switch_SW_SPST.sexp',
    'Switch:SW_SPDT': f'{PANTRY}/Switch_SW_SPDT.sexp',
    'Adafruit ItsyBitsy RP2040-eagle-import:SWITCH_TACT_SMT4.6X2.8': f'{PANTRY}/Adafruit_ItsyBitsy_RP2040-eagle-import_SWITCH_TACT_SMT4.6X2.8.sexp',
    'Transistor_FET:BSS138': f'{PANTRY}/Transistor_FET_BSS138.sexp',
}

# ---------- output buffers ----------
lib_symbols_used = []          # ordered unique list of lib_ids
body = []                      # lines after lib_symbols, before sheet_instances
parts_report = []              # for the report: (ref, value, footprint, lcsc, note)

def use_lib(lib_id):
    if lib_id not in lib_symbols_used:
        lib_symbols_used.append(lib_id)

def emit(line_or_lines, indent=1):
    if isinstance(line_or_lines, str):
        line_or_lines = [line_or_lines]
    for l in line_or_lines:
        body.append('\t' * indent + l if l else '')

# ---------- primitive emitters ----------
def add_wire(pts):
    emit('(wire')
    emit('\t(pts', 0)
    pts_line = '\t\t' + ' '.join('(xy %s %s)' % (fmt(x), fmt(y)) for x, y in pts)
    body.append(pts_line)
    emit('\t)', 0)
    emit('\t(stroke', 0)
    emit('\t\t(width 0)', 0)
    emit('\t\t(type default)', 0)
    emit('\t)', 0)
    emit('\t(uuid "%s")' % u(), 0)
    emit(')', 0)

def fmt(v):
    v = rd(v)
    s = ('%.2f' % v).rstrip('0').rstrip('.')
    return s if s not in ('', '-0') else '0'

def add_junction(at):
    emit('(junction')
    emit('\t(at %s %s)' % (fmt(at[0]), fmt(at[1])), 0)
    emit('\t(diameter 0)', 0)
    emit('\t(color 0 0 0 0)', 0)
    emit('\t(uuid "%s")' % u(), 0)
    emit(')', 0)

def add_no_connect(at):
    emit('(no_connect')
    emit('\t(at %s %s)' % (fmt(at[0]), fmt(at[1])), 0)
    emit('\t(uuid "%s")' % u(), 0)
    emit(')', 0)

def add_label(text, at, rot=0, shape=None, local=False, size=1.27):
    kind = 'label' if local else 'global_label'
    emit('(%s "%s"' % (kind, text))
    if not local:
        emit('\t(shape %s)' % shape, 0)
    emit('\t(at %s %s %s)' % (fmt(at[0]), fmt(at[1]), rot), 0)
    emit('\t(fields_autoplaced yes)', 0)
    emit('\t(effects', 0)
    emit('\t\t(font', 0)
    emit('\t\t\t(size %s %s)' % (size, size), 0)
    emit('\t\t)', 0)
    just = 'left' if rot in (0, 90) else 'right'
    emit('\t\t(justify %s)' % just, 0)
    emit('\t)', 0)
    emit('\t(uuid "%s")' % u(), 0)
    if not local:
        emit('\t(property "Intersheetrefs" "${INTERSHEET_REFS}"', 0)
        emit('\t\t(at %s %s 0)' % (fmt(at[0]), fmt(at[1])), 0)
        emit('\t\t(hide yes)', 0)
        emit('\t\t(show_name no)', 0)
        emit('\t\t(do_not_autoplace no)', 0)
        emit('\t\t(effects', 0)
        emit('\t\t\t(font', 0)
        emit('\t\t\t\t(size 1.27 1.27)', 0)
        emit('\t\t\t)', 0)
        emit('\t\t)', 0)
        emit('\t)', 0)
    emit(')', 0)

def add_text(text, at, rot=0, size=1.524):
    # explicit "left top": KiCad centers text on (at) with no justify, which makes a
    # left-anchored placement impossible to reason about -- pin it top-left instead so
    # multi-line notes flow down-and-right from the given point, like the project's own.
    emit('(text "%s"' % text.replace('"', '\\"'))
    emit('\t(exclude_from_sim no)', 0)
    emit('\t(at %s %s %s)' % (fmt(at[0]), fmt(at[1]), rot), 0)
    emit('\t(effects', 0)
    emit('\t\t(font', 0)
    emit('\t\t\t(size %s %s)' % (size, size), 0)
    emit('\t\t)', 0)
    emit('\t\t(justify left top)', 0)
    emit('\t)', 0)
    emit('\t(uuid "%s")' % u(), 0)
    emit(')', 0)

PROP_OFFSETS = {
    # small default offsets (mm) for Reference (above) / Value (below) text, generic parts
}

def add_symbol(lib_id, ref, value, at, rot=0, mirror=None, footprint='', datasheet='',
               description='', lcsc=None, ref_dy=-3.556, val_dy=3.556, ref_dx=0.0, val_dx=0.0,
               ref_angle=0, val_angle=0,
               hide_ref=False, hide_val=False, extra_props=None):
    """Emit a symbol instance. Returns dict pin_name -> (gx, gy).

    ref_dy/val_dy place the Reference/Value text above/below the symbol origin;
    for symbols rotated 90/270 (tall/narrow after rotation) pass ref_dx/val_dx
    (and dy=0) instead so the text sits beside the symbol, not on top of its
    now-vertical pins.

    ref_angle/val_angle: the property's OWN stored text angle is not rendered
    literally for a rotated (rot=90/270) symbol -- kicad-cli's plotter combines
    it with the parent symbol's rotation. Confirmed against the FC's own SW1/
    SW2 (same footprint, rot=270): Value stored at angle 0 renders VERTICAL
    ("KMR2", read bottom-to-top -- a deliberate, accepted FC convention, not a
    defect), Reference stored at angle 90 renders HORIZONTAL ("SW1"/"SW2").
    Default 0 is correct for unrotated (rot=0) parts.
    """
    use_lib(lib_id)
    x0, y0 = at
    iu = u()
    emit('(symbol')
    emit('\t(lib_id "%s")' % lib_id, 0)
    at_str = '(at %s %s %s)' % (fmt(x0), fmt(y0), rot)
    emit('\t%s' % at_str, 0)
    emit('\t(unit 1)', 0)
    emit('\t(body_style 1)', 0)
    emit('\t(exclude_from_sim no)', 0)
    emit('\t(in_bom yes)', 0)
    emit('\t(on_board yes)', 0)
    emit('\t(in_pos_files yes)', 0)
    emit('\t(dnp no)', 0)
    if mirror:
        emit('\t(mirror %s)' % mirror, 0)
    emit('\t(uuid "%s")' % iu, 0)
    is_power = lib_id.startswith('power:') or lib_id.startswith('flatsat:') and ref.startswith('#')

    def prop(name, val, dx, dy, hide, justify=None, size=1.27, angle=0):
        emit('\t(property "%s" "%s"' % (name, val.replace('"', '\\"')), 0)
        px, py = x0 + dx, y0 + dy
        emit('\t\t(at %s %s %s)' % (fmt(px), fmt(py), angle), 0)
        if hide:
            emit('\t\t(hide yes)', 0)
        emit('\t\t(show_name no)', 0)
        emit('\t\t(do_not_autoplace no)', 0)
        emit('\t\t(effects', 0)
        emit('\t\t\t(font', 0)
        emit('\t\t\t\t(size %s %s)' % (size, size), 0)
        emit('\t\t\t)', 0)
        if justify:
            emit('\t\t\t(justify %s)' % justify, 0)
        emit('\t\t)', 0)
        emit('\t)', 0)

    prop('Reference', ref, ref_dx, ref_dy, hide_ref or ref.startswith('#'), angle=ref_angle)
    prop('Value', value, val_dx, val_dy, hide_val, angle=val_angle)
    emit('\t(property "Footprint" "%s"' % footprint, 0)
    emit('\t\t(at %s %s 0)' % (fmt(x0), fmt(y0)), 0)
    emit('\t\t(hide yes)', 0)
    emit('\t\t(show_name no)', 0)
    emit('\t\t(do_not_autoplace no)', 0)
    emit('\t\t(effects', 0)
    emit('\t\t\t(font', 0)
    emit('\t\t\t\t(size 1.27 1.27)', 0)
    emit('\t\t\t)', 0)
    emit('\t\t)', 0)
    emit('\t)', 0)
    emit('\t(property "Datasheet" "%s"' % datasheet, 0)
    emit('\t\t(at %s %s 0)' % (fmt(x0), fmt(y0)), 0)
    emit('\t\t(hide yes)', 0)
    emit('\t\t(show_name no)', 0)
    emit('\t\t(do_not_autoplace no)', 0)
    emit('\t\t(effects', 0)
    emit('\t\t\t(font', 0)
    emit('\t\t\t\t(size 1.27 1.27)', 0)
    emit('\t\t\t)', 0)
    emit('\t\t)', 0)
    emit('\t)', 0)
    emit('\t(property "Description" "%s"' % description, 0)
    emit('\t\t(at %s %s 0)' % (fmt(x0), fmt(y0)), 0)
    emit('\t\t(hide yes)', 0)
    emit('\t\t(show_name no)', 0)
    emit('\t\t(do_not_autoplace no)', 0)
    emit('\t\t(effects', 0)
    emit('\t\t\t(font', 0)
    emit('\t\t\t\t(size 1.27 1.27)', 0)
    emit('\t\t\t)', 0)
    emit('\t\t)', 0)
    emit('\t)', 0)
    if lcsc:
        emit('\t(property "LCSC Part" "%s"' % lcsc, 0)
        emit('\t\t(at %s %s 0)' % (fmt(x0), fmt(y0)), 0)
        emit('\t\t(hide yes)', 0)
        emit('\t\t(show_name no)', 0)
        emit('\t\t(do_not_autoplace no)', 0)
        emit('\t\t(effects', 0)
        emit('\t\t\t(font', 0)
        emit('\t\t\t\t(size 1.27 1.27)', 0)
        emit('\t\t\t)', 0)
        emit('\t\t)', 0)
        emit('\t)', 0)
    pins = PINS[lib_id]
    for num in pins:
        emit('\t(pin "%s"' % num, 0)
        emit('\t\t(uuid "%s")' % u(), 0)
        emit('\t)', 0)
    emit('\t(instances', 0)
    emit('\t\t(project "%s"' % PROJECT, 0)
    emit('\t\t\t(path "%s"' % INST_PATH, 0)
    emit('\t\t\t\t(reference "%s")' % ref, 0)
    emit('\t\t\t\t(unit 1)', 0)
    emit('\t\t\t)', 0)
    emit('\t\t)', 0)
    emit('\t)', 0)
    emit(')', 0)
    gpins = {name: transform(px, py, x0, y0, rot, mirror) for name, (px, py) in pins.items()}
    if not ref.startswith('#'):
        parts_report.append((ref, value, footprint, lcsc, datasheet))
    return gpins

# =====================================================================
# Layout
# =====================================================================

# ---------------- Block A: Emulator USB-C, CC pulldowns, D+/D- series, VBUS_EMU rail ----------------
emit(''); body.append('')
add_text("PROVES FlatSat V1 -- Phase 1", (20.32, 19.05), size=2.159)
add_text("Bench IO", (20.32, 24.13), size=2.159)
add_text("Emulator USB-C + SWD, FC bench control (RESET/USBBOOT/WDT_DISABLE open-drain drivers),\\n"
         "WDT_DISABLE toggle, EMU_RUN / EMU_BOOTSEL_SW buttons, bench header.\\n"
         "See docs/flatsat/2026-09-14_phase1_schematic/sheet_bench_io.md.", (20.32, 30.48))

add_text("Block A -- Emulator USB-C", (33.02, 60.96))
J701 = add_symbol('Connector:USB_C_Receptacle_USB2.0_16P', 'J701', 'USB_C_Receptacle_USB2.0_16P',
                   (63.5, 88.9), rot=0,
                   footprint='Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12',
                   datasheet='https://www.lcsc.com/datasheet/lcsc_datasheet_2205251630_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf',
                   lcsc='C165948',
                   description='USB-C receptacle, power+data only (emulator USB)',
                   ref_dy=-25.4, val_dy=-22.86)

# GND stack (A1/A12/B1/B12) + shield
gA1 = J701['A1']
gS1 = J701['S1']
gnd_junc = (gA1[0], 130.81)
add_wire([gA1, gnd_junc])
shield_bend = (gS1[0], 118.11)
add_wire([gS1, shield_bend])
add_wire([shield_bend, (gA1[0], 118.11)])
add_junction((gA1[0], 118.11))
add_junction(gnd_junc)
gndp = add_symbol('power:GND', '#PWR701', 'GND', gnd_junc, rot=0, hide_ref=True, hide_val=True)

# VBUS_EMU rail: connector VBUS-stack -> up through junctions -> PWR_FLAG / TestPoint / bulk cap -> #PWR (VBUS_EMU)
gVBUS = J701['A4']
vbus_x = gVBUS[0]
# kept below y=45 (the title block's text occupies y<=43 at this x) so the rail
# never runs up through the sheet title/description.
p_flg = (vbus_x, 50.8)
p_tp = (vbus_x, 55.88)
p_cap = (vbus_x, 60.96)
p_top = (vbus_x, 45.72)
add_wire([gVBUS, p_cap])
add_wire([p_cap, p_tp])
add_wire([p_tp, p_flg])
add_wire([p_flg, p_top])
add_junction(p_cap)
add_junction(p_tp)
add_junction(p_flg)
pwr_vbus = add_symbol('flatsat:VBUS_EMU', '#PWR702', 'VBUS_EMU', p_top, rot=0, hide_ref=True, hide_val=False)
flg = add_symbol('power:PWR_FLAG', '#FLG701', 'PWR_FLAG', (vbus_x + 12.7, 50.8), rot=0, hide_ref=True, hide_val=True)
add_wire([p_flg, (vbus_x + 12.7, 50.8)])
tp_vbus = add_symbol('Connector:TestPoint', 'TP701', 'VBUS_EMU', (vbus_x + 12.7, 55.88), rot=270,
                      footprint='TestPoint:TestPoint_Pad_D1.5mm', description='Test point, VBUS_EMU (emulator USB-C 5V)',
                      # angle=90 on both (see add_symbol docstring: a rot=270 parent
                      # renders a stored angle-0 property VERTICAL) keeps both lines
                      # horizontal; pushed left + split top/bottom, clear of C701's
                      # Reference/Value (now offset right, dx=2.54) two rows below --
                      # the two used to land within ~3mm of each other, and vertical.
                      ref_dx=-9.0, ref_dy=-2.54, ref_angle=90,
                      val_dx=-9.0, val_dy=2.54, val_angle=90)
add_wire([p_tp, (vbus_x + 12.7, 55.88)])
c701 = add_symbol('Device:C', 'C701', '10uF', (vbus_x + 15.24, 64.77), rot=0,
                   footprint='Capacitor_SMD:C_0805_2012Metric', description='VBUS_EMU bulk capacitor, X7R 16V',
                   lcsc='C2182156',
                   ref_dx=2.54, val_dx=2.54)
add_wire([p_cap, c701['1']])
# GND stub kept short (anchor at y=71.12) so the GND symbol's triangle graphic (~2.5mm
# below its anchor) stays well clear of the CC1 wire at y=78.74 -- was landing on it.
gndc_at = (c701['2'][0], 71.12)
gndc = add_symbol('power:GND', '#PWR703', 'GND', gndc_at, rot=0, hide_ref=True, hide_val=True)
add_wire([c701['2'], gndc_at])

# CC1 / CC2 5.1k pulldowns to GND
gCC1 = J701['A5']
gCC2 = J701['B5']
r701_top = (104.14, gCC1[1])
r701 = add_symbol('mainboard:RESISTOR0603', 'R701', '5.1k', (104.14, gCC1[1] + 5.08), rot=90,
                   ref_dy=0, val_dy=0, ref_dx=-3.81, val_dx=3.81,
                   footprint='Resistor_SMD:R_0402_1005Metric', lcsc='C25905',
                   description='USB-C CC1 pulldown, 5.1k 0402')
add_wire([gCC1, r701_top])
gnd_r701 = add_symbol('power:GND', '#PWR704', 'GND', (104.14, r701_top[1] + 17.78), rot=0, hide_ref=True, hide_val=True)
add_wire([r701['1'], (104.14, r701_top[1] + 17.78)])

r702 = add_symbol('mainboard:RESISTOR0603', 'R702', '5.1k', (91.44, gCC2[1] + 5.08), rot=90,
                   ref_dy=0, val_dy=0, ref_dx=-3.81, val_dx=3.81,
                   footprint='Resistor_SMD:R_0402_1005Metric', lcsc='C25905',
                   description='USB-C CC2 pulldown, 5.1k 0402')
add_wire([gCC2, (91.44, gCC2[1])])
gnd_r702 = add_symbol('power:GND', '#PWR705', 'GND', (91.44, gCC2[1] + 5.08 + 12.7), rot=0, hide_ref=True, hide_val=True)
add_wire([r702['1'], (91.44, gCC2[1] + 5.08 + 12.7)])

# D+ (A6/B6) tie -> R703 (22R) -> EMU_USB_DP ; D- (A7/B7) tie -> R704 (22R) -> EMU_USB_DM
gA6, gB6 = J701['A6'], J701['B6']
gA7, gB7 = J701['A7'], J701['B7']
mid_dp = (gA6[0], (gA6[1] + gB6[1]) / 2)
mid_dm = (gA7[0], (gA7[1] + gB7[1]) / 2)
add_wire([gA6, mid_dp])
add_wire([mid_dp, gB6])
add_junction(mid_dp)
add_wire([gA7, mid_dm])
add_wire([mid_dm, gB7])
add_junction(mid_dm)

# Route D+/D- well below the CC1/CC2 pulldown network (R701/R702 bodies + GND leads
# span y=78.74..99.06 at x=91.44/104.14) instead of straight across at pin height --
# the straight run used to draw the green wire directly through both resistor bodies.
r703_x0 = 152.4
r704_x0 = 152.4
dp_row_y = 109.22   # D+ row (1.27mm grid), below R701/R702's lowest GND lead (99.06)
dm_row_y = 104.14   # D- row (1.27mm grid), likewise
# Both jogged off x=78.74 (the J701 pin column) -- that column also carries the SBU1/
# SBU2 no_connect flags at (78.74, 101.6) and (78.74, 104.14); a straight drop at
# x=78.74 down to dm_row_y ran the D- wire right through the SBU2 no-connect marker.
dp_drop_x = 81.28
dm_drop_x = 80.01
add_wire([mid_dp, (dp_drop_x, mid_dp[1])])
add_wire([(dp_drop_x, mid_dp[1]), (dp_drop_x, dp_row_y)])
add_wire([mid_dm, (dm_drop_x, mid_dm[1])])
add_wire([(dm_drop_x, mid_dm[1]), (dm_drop_x, dm_row_y)])

# R703 sits below R704 (dp_row_y > dm_row_y) -- push R703's ref/value both further
# south (past y=113.3, where the Block C/D header text row ends) and R704's both
# further north so neither pair drifts into the gap between the two resistors (the
# original default +-3.556 split put both "22" values in that gap, indistinguishable
# from one another) or into the header text immediately below R703.
r703 = add_symbol('mainboard:RESISTOR0603', 'R703', '22', (r703_x0, dp_row_y), rot=0,
                   footprint='Resistor_SMD:R_0402_1005Metric', lcsc='C25092',
                   ref_dy=6.35, val_dy=9.0,
                   description='USB D+ series termination, 22R 0402')
add_wire([(dp_drop_x, dp_row_y), r703['1']])
add_label('EMU_USB_DP', r703['2'], rot=0, shape='bidirectional')

r704 = add_symbol('mainboard:RESISTOR0603', 'R704', '22', (r704_x0, dm_row_y), rot=0,
                   footprint='Resistor_SMD:R_0402_1005Metric', lcsc='C25092',
                   ref_dy=-6.35, val_dy=-3.556,
                   description='USB D- series termination, 22R 0402')
add_wire([(dm_drop_x, dm_row_y), r704['1']])
add_label('EMU_USB_DM', r704['2'], rot=0, shape='bidirectional')

# SBU (unused)
add_no_connect(J701['A8'])
add_no_connect(J701['B8'])

# Placed in the open pocket right of C701/TP701 and above the CC network (x>=110
# clears both; y<78.74 clears R701/R702) -- the lower-right area (below the D+/D-
# reroute) is contested by the Block C/D header text row and R703/R704's own labels.
add_text("USB-C is power+data only; no CC logic beyond 5.1k Rd -- this presents the port\\n"
         "as a UFP, so an upstream DFP (the bench PC) sources VBUS_EMU; J701 does not.\\n"
         "22R series on D+/D- mirrors the FC's J12/R7/R8 arrangement (C25092).\\n"
         "No USB ESD array fitted (none found that matches this footprint); ESD exposure\\n"
         "is bench-only, same as any lab USB cable.", (110.0, 63.0), size=1.0)

# Bench rule for the operator, placed at the physical connector (review fix id 11):
# the band x>=112, y=74..80 is the empty pocket directly right of the J701 pin column
# and below the Block A note (which ends near y=70.5); the CC pulldown network
# (R701/R702 bodies + value text) stops at x<=110, and nothing else occupies this row
# until the D-/D+ reroute at y=104. Size 1.27 (larger than the 1.0 explanatory notes)
# so it reads as an operating rule, not commentary.
add_text("BENCH RULE: Connect emulator USB (J701) before or together with FC power;\\n"
         "do not leave FC powered with the emulator unplugged (3V3_EMU can float\\n"
         "to an undefined partial-power state).", (112.0, 74.0), size=1.27)

# ---------------- Block B: Emulator SWD (JST-SH 3-pin) ----------------
add_text("Block B -- Emulator SWD", (33.02, 111.76))
J702 = add_symbol('Connector_Generic:Conn_01x03', 'J702', 'SWD', (63.5, 149.86), rot=0,
                   footprint='Connector_JST:JST_SH_BM03B-SRSS-TB_1x03-1MP_P1.00mm_Vertical',
                   lcsc='C160389',
                   datasheet='https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_JST-BM03B-SRSS-TB-LF-SN_C160389.pdf',
                   description='JST-SH 1x03, emulator SWD (mirrors FC J22)',
                   # Default +-3.556 dy landed inside the pin column (pins span
                   # y0-2.54..y0+2.54) and over pin 1's number; pushed further out.
                   ref_dy=-7.62, val_dy=7.62)
add_wire([J702['1'], (48.26, J702['1'][1])])
add_label('EMU_SWCLK', (48.26, J702['1'][1]), rot=180, shape='bidirectional')
# x pulled well clear of both the EMU_SWCLK (y=147.32) and EMU_SWDIO (y=152.4) global
# label boxes (each spans roughly x 37.6-48.3) -- kept horizontal at pin 2's own row
# (y=149.86, between the two label rows) so it can't cross either label's own wire/
# anchor point the way a vertical jog at x=48.26 would (that x is where both labels
# terminate their wires).
add_wire([J702['2'], (30.48, J702['2'][1])])
gnd_swd = add_symbol('power:GND', '#PWR706', 'GND', (30.48, J702['2'][1]), rot=0, hide_ref=True, hide_val=True)
add_wire([J702['3'], (48.26, J702['3'][1])])
add_label('EMU_SWDIO', (48.26, J702['3'][1]), rot=180, shape='bidirectional')

# ---------------- Block C: EMU_RUN / EMU_BOOTSEL_SW buttons ----------------
add_text("Block C -- Emulator reset / boot buttons", (100.33, 111.76))
TACT = 'Adafruit ItsyBitsy RP2040-eagle-import:SWITCH_TACT_SMT4.6X2.8'

def add_button(ref, gnd_ref, at, net_label, shape='input'):
    # Exactly the FC's own SW1/SW2 Reference/Value offsets and text angles (same
    # lib_id, same rot=270; read directly from FlatSat_V1.kicad_sch) -- their
    # default dy-only placement (this generator's old default) rendered "SW701"/
    # "KMR2" stacked on top of the switch graphic; angle=90 on the Reference is
    # what makes it render horizontal (see add_symbol docstring), and dx=-6.35 is
    # what clears the Value ("KMR2", left as vertical -- FC's own convention) of
    # the now-vertical footprint's +-2.54mm-wide body.
    sw = add_symbol(TACT, ref, 'KMR2', at, rot=270,
                     footprint='FC_DEV_BOARD:BTN_KMR2_4.6X2.8', lcsc='C72443',
                     datasheet='https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_C-K-KMR221GLFS_C72443.pdf',
                     description='Tact switch, momentary, to GND (mirrors FC SW1/SW2)',
                     ref_dx=0, ref_dy=6.35, ref_angle=90,
                     val_dx=-6.35, val_dy=-1.905, val_angle=0)
    a, ap, b, bp = sw['A'], sw["A'"], sw['B'], sw["B'"]
    add_wire([a, ap])
    add_junction(a)
    add_wire([b, bp])
    add_junction(b)
    top = (a[0], a[1] - 5.08)
    add_wire([a, top])
    add_label(net_label, top, rot=90, shape=shape)
    bot = (b[0], b[1] + 5.08)
    add_wire([b, bot])
    add_symbol('power:GND', gnd_ref, 'GND', bot, rot=0, hide_ref=True, hide_val=True)
    return sw

add_button('SW701', '#PWR707', (114.3, 149.86), 'EMU_RUN')
add_button('SW702', '#PWR708', (139.7, 149.86), 'EMU_BOOTSEL_SW')

# ---------------- Block D: WDT_DISABLE toggle switch ----------------
add_text("Block D -- WDT_DISABLE toggle (mirrors FC J4 jumper)", (165.1, 111.76))
sw703 = add_symbol('Switch:SW_SPDT', 'SW703', 'SS12D10G4', (185.42, 149.86), rot=0,
                    footprint='easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4',
                    datasheet='https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2108201830_SHOU-HAN-SS12D10G4-071_C2887259.pdf',
                    lcsc='C2887259',
                    # Project-standard bench slide switch: debug_board_v1 (brief-cited
                    # for this circuit) uses this exact MPN/footprint for its own
                    # WDT-equivalent toggle (refs/upgraded/debug_board_v1, SW3, lib_id
                    # Switch:SW_Push_SPDT -- 3 pins). Symbol here is the 3-pin
                    # Switch:SW_SPDT (system library) so every footprint pad (1/2/3,
                    # SHOU-HAN SS12D10G4, centre pad 2 = common pole per datasheet) has
                    # a matching schematic pin; pin 3 (the unused throw) is a marked
                    # no_connect rather than left off the symbol.
                    description='On-board SPDT slide switch, common pole (pin 2) to GND, pin 1 to '
                                 'WDT_DISABLE, pin 3 (other throw) not connected -- bench equivalent of '
                                 'FC J4 shunt. MPN SHOU-HAN SS12D10G4-071',
                    # SW_SPDT's own rectangle body spans +-3.81mm vertically from centre
                    # (bigger than SW_SPST's, which had no box) -- default +-3.556 would
                    # land the text just inside that box, so pushed out to +-5.08.
                    ref_dy=-5.08, val_dy=5.08)
# Common pole (pin 2) -> GND
gnd_sw703_pt = (sw703['2'][0] - 7.62, sw703['2'][1])
add_wire([sw703['2'], gnd_sw703_pt])
gnd_sw703 = add_symbol('power:GND', '#PWR709', 'GND', gnd_sw703_pt, rot=270,
                        hide_ref=True, hide_val=True)
# Pin 1 (one throw) -> WDT_DISABLE
wdt_pt = (sw703['1'][0] + 7.62, sw703['1'][1])
add_wire([sw703['1'], wdt_pt])
add_label('WDT_DISABLE', wdt_pt, rot=0, shape='bidirectional')
# Pin 3 (other throw) -- not used
add_no_connect(sw703['3'])
add_text("Parallel manual path to the FC's own J4 jumper (RC watchdog integrator node).\\n"
         "Closed = watchdog disabled. Independent of the EMU_CTL_WDT_DIS open-drain driver below.\\n"
         "Slider toward pin 1 grounds WDT_DISABLE through the common pole (pin 2); slider toward\\n"
         "pin 3 (NC) leaves WDT_DISABLE open.",
         (165.1, 158.75), size=1.0)

# ---------------- Block E: open-drain FC_RESET / USBBOOT / WDT_DISABLE drivers ----------------
add_text("Block E -- Open-drain FC bench-control drivers (D8), erratum E9 (A2 silicon): an\\n"
         "unprogrammed / BOOTSEL-mode / unpowered emulator GPIO can float to ~2V and leak up to\\n"
         "120uA, so the gate pull-down is <= 8.2k (4.7k used) to hold the gate low regardless.\\n"
         "The A4 stepping corrects erratum E9; the 4.7k pull-down is the A2-safe value and may be\\n"
         "relaxed if A4-stepping emulator silicon is fitted. BSS138 (Vgs(th) 0.8-1.5V max) is used\\n"
         "instead of a plain 2N7002 (Vgs(th) up to 2.5V max) so the 1k/4.7k gate divider (3.3V x\\n"
         "4.7/5.7 = 2.72V typ, 2.59V at IOVDD -5%) stays well above threshold at worst case --\\n"
         "each driver only pulls its FC net low, never drives it high. USBBOOT reaches the FC's\\n"
         "U18 BOOTSEL pin through D4 + R10 1k, exactly the path FC SW1 uses, so Q702 pulling\\n"
         "USBBOOT low reproduces an SW1 press.", (33.02, 172.72), size=1.0)


def add_driver(qref, rs_ref, rpd_ref, gnd1_ref, gnd2_ref, x0, y0, ctl_label, out_label):
    q = add_symbol('Transistor_FET:BSS138', qref, 'BSS138', (x0, y0), rot=0,
                    footprint='Package_TO_SOT_SMD:SOT-23',
                    datasheet='https://www.onsemi.com/pub/Collateral/BSS138-D.PDF',
                    lcsc='C78284',
                    description='N-ch logic-level MOSFET (Vgs(th) 0.8-1.5V max), open-drain bench driver',
                    # Default dx=0 put Reference/Value directly above/below the symbol
                    # origin -- the same x column the drain (up) and source (down)
                    # leads run vertically through, so the wires struck through both
                    # strings. dx offset moves the text off that column entirely.
                    ref_dx=-5.08, val_dx=5.08)
    gate, source, drain = q['1'], q['2'], q['3']
    rs_center = (gate[0] - 10.16, gate[1])
    rs = add_symbol('mainboard:RESISTOR0603', rs_ref, '1k', rs_center, rot=0,
                     footprint='Resistor_SMD:R_0402_1005Metric', lcsc='C11702',
                     description='Gate series R, 1k 0402')
    add_wire([rs['2'], gate])
    add_junction(rs['2'])
    label_pos = (rs['1'][0] - 10.16, gate[1])
    add_wire([rs['1'], label_pos])
    add_label(ctl_label, label_pos, rot=180, shape='input')
    pd_top = (rs['2'][0], rs['2'][1] + 7.62)
    add_wire([rs['2'], pd_top])
    rpd = add_symbol('mainboard:RESISTOR0603', rpd_ref, '4.7k', (pd_top[0], pd_top[1] + 5.08), rot=90,
                      ref_dy=0, val_dy=0, ref_dx=-3.81, val_dx=3.81,
                      footprint='Resistor_SMD:R_0402_1005Metric', lcsc='C25900',
                      description='RP2350 erratum E9 gate pull-down, <=8.2k, 4.7k 0402')
    gnd1_pt = (rpd['1'][0], rpd['1'][1] + 7.62)
    add_wire([rpd['1'], gnd1_pt])
    add_symbol('power:GND', gnd1_ref, 'GND', gnd1_pt, rot=0, hide_ref=True, hide_val=True)
    drain_label_pt = (drain[0] + 7.62, drain[1])
    add_wire([drain, drain_label_pt])
    add_label(out_label, drain_label_pt, rot=0, shape='bidirectional')
    source_gnd_pt = (source[0], source[1] + 7.62)
    add_wire([source, source_gnd_pt])
    add_symbol('power:GND', gnd2_ref, 'GND', source_gnd_pt, rot=0, hide_ref=True, hide_val=True)


add_driver('Q701', 'R705', 'R706', '#PWR711', '#PWR712', 63.5, 200.66, 'EMU_CTL_FC_RESET', 'FC_RESET')
add_driver('Q702', 'R707', 'R708', '#PWR713', '#PWR714', 139.7, 200.66, 'EMU_CTL_USBBOOT', 'USBBOOT')
add_driver('Q703', 'R709', 'R710', '#PWR715', '#PWR716', 215.9, 200.66, 'EMU_CTL_WDT_DIS', 'WDT_DISABLE')

# ---------------- Block F: bench header (2x5) ----------------
add_text("Block F -- Bench header (2x5, 2.54mm). Pin 1 marked on silkscreen / connector key.",
         (254.0, 111.76))
J703 = add_symbol('Connector_Generic:Conn_02x05_Odd_Even', 'J703', 'Bench Header', (279.4, 152.4), rot=0,
                   footprint='Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical',
                   lcsc='C492422',
                   datasheet='https://www.lcsc.com/datasheet/lcsc_datasheet_2003191006_XFCN-PZ254V-12-10P_C492422.pdf',
                   description='Bench header: 3V3_EMU, GND, EMU UART/GPIO spares, FC_RESET/USBBOOT/WDT_DISABLE',
                   # Default +-3.556 dy landed inside the pin block (pins span y0+-5.08)
                   # and over pin-number text; pushed clear of it, same as J702 above.
                   ref_dy=-7.62, val_dy=7.62)

left_x = 254.0
right_x = 304.8
header_map = [
    ('1', '3V3_EMU', 'pwr3v3'),
    ('2', 'GND', 'gnd'),
    ('3', 'EMU_UART_TX', 'label'),
    ('4', 'EMU_UART_RX', 'label'),
    ('5', 'EMU_GPIO_SPARE0', 'label'),
    ('6', 'EMU_GPIO_SPARE1', 'label'),
    ('7', 'FC_RESET', 'label_bidir'),
    ('8', 'USBBOOT', 'label_bidir'),
    ('9', 'WDT_DISABLE', 'label_bidir'),
    ('10', 'GND', 'gnd'),
]
gnd_hdr_ref = ['#PWR717', '#PWR718']
gi = 0
for num, net, kind in header_map:
    pin = J703[num]
    is_left = int(num) % 2 == 1
    stub_x = left_x if is_left else right_x
    stub = (stub_x, pin[1])
    add_wire([pin, stub])
    if kind == 'pwr3v3':
        # plain global_label (not the flatsat:3V3_EMU power-input symbol): emulator_mcu
        # (not yet on disk in isolated harness runs) owns the power_out source for this
        # rail, matching the convention pyro_inhibit already uses for the same net.
        add_label('3V3_EMU', stub, rot=(180 if is_left else 0), shape='input')
    elif kind == 'gnd':
        add_symbol('power:GND', gnd_hdr_ref[gi], 'GND', stub, rot=270, hide_ref=True, hide_val=True)
        gi += 1
    elif kind == 'label':
        add_label(net, stub, rot=(180 if is_left else 0), shape='input')
    elif kind == 'label_bidir':
        add_label(net, stub, rot=(180 if is_left else 0), shape='bidirectional')

add_text("3V3_EMU / GND on this header are the emulator's own rail (power symbols tie into the\\n"
         "nets defined on emulator_mcu). FC_RESET / USBBOOT / WDT_DISABLE here are the same FC\\n"
         "global nets the drivers above pull low -- this header only taps them, never sources them.",
         (254.0, 168.91), size=1.0)

# =====================================================================
# Assemble the file
# =====================================================================
SHEET_UUID_FILE = u()

out = []
out.append('(kicad_sch')
out.append('\t(version 20260306)')
out.append('\t(generator "eeschema")')
out.append('\t(generator_version "10.0")')
out.append('\t(uuid "%s")' % SHEET_UUID_FILE)
out.append('\t(paper "A3")')
out.append('\t(lib_symbols')
for lib in lib_symbols_used:
    with open(LIB_FILES[lib], encoding='utf-8') as f:
        text = f.read()
    out.append(text.rstrip('\n'))
out.append('\t)')
out.extend(body)
out.append(')')

final_text = '\n'.join(out) + '\n'

target = os.path.join(PROJ, 'bench_io.kicad_sch')
tmp = target + '.tmp'
with open(tmp, 'w', encoding='utf-8') as f:
    f.write(final_text)
os.replace(tmp, target)
print('wrote', target, '(%d lines)' % len(out))

print('\n-- parts_report --')
for ref, value, footprint, lcsc, datasheet in parts_report:
    print(ref, value, footprint, lcsc or 'NEEDS LCSC', datasheet)
print('\n-- lib_symbols used --')
for lib in lib_symbols_used:
    print(lib)



