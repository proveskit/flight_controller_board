#!/usr/bin/env python3
"""Generator for FlatSat_V1/pyro_inhibit.kicad_sch ("Pyro Inhibit and Jumpers", page 11).

Writes atomically (tmp + mv). See docs/flatsat/2026-09-14_phase1_schematic/00_pm_brief.md
section 6.5 for the spec and sheet_pyro_inhibit.md for the design writeup.
"""
import math
import random
import uuid
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Checked-in symbol pantry (tools/pantry); $FLATSAT_PANTRY overrides it.  Never a
# session scratch path: the generator must run from a clean checkout (review fix 13).
PANTRY = os.environ.get("FLATSAT_PANTRY", os.path.join(HERE, "..", "pantry"))
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "pyro_inhibit.kicad_sch")
PROJECT = "FlatSat_V1"
ROOT_UUID = "c64c0d72-a9f6-4f3a-891e-1f647558f538"
SHEET_SYM_UUID = "ba398093-e7fc-4f25-8f04-4265c3e55b54"
INST_PATH = "/%s/%s" % (ROOT_UUID, SHEET_SYM_UUID)
GRID = 1.27

def g(n):
    return round(n * GRID, 2)

# Review fix 14: deterministic uuid4 stream.  Emission order is fixed, so seeding the
# RNG makes a regeneration byte-identical to the committed sheet instead of churning
# every uuid (which would orphan any layout that had already been placed from it).
# Set FLATSAT_FRESH_UUIDS=1 to get real random uuids (only when re-keying a sheet).
_rng = random.Random("flatsat-pyro_inhibit-2026-09-14")
_FRESH = os.environ.get("FLATSAT_FRESH_UUIDS") == "1"

def U():
    if _FRESH:
        return str(uuid.uuid4())
    return str(uuid.UUID(int=_rng.getrandbits(128), version=4))

def fmt(v):
    v = round(v, 4)
    if abs(v - round(v)) < 1e-9:
        return str(int(round(v)))
    s = ("%.4f" % v).rstrip('0').rstrip('.')
    return s

def pt(x, y):
    return "(xy %s %s)" % (fmt(x), fmt(y))

# ---------------------------------------------------------------- transforms
def transform(px, py, rot, mirror=None):
    """Same algorithm as tools/sch_lint.py: lib pin (px,py) -> offset from symbol origin."""
    x, y = px, -py
    if mirror == 'x':
        y = -y
    elif mirror == 'y':
        x = -x
    r = math.radians(rot)
    xr = x * math.cos(r) + y * math.sin(r)
    yr = -x * math.sin(r) + y * math.cos(r)
    return xr, yr

# ------------------------------------------------------------ lib pin tables
PINS = {
    'Diode:BAT54W': {'1': (3.81, 0), '2': (0, 0), '3': (-3.81, 0)},
    'Jumper:Jumper_2_Open': {'1': (-5.08, 0), '2': (5.08, 0)},
    'Switch:SW_SPST': {'1': (-5.08, 0), '2': (5.08, 0)},
    # SW_SPDT: pin 2 ('B') is the common wiper; pins 1 ('A') and 3 ('C') are the two throws
    # (same geometry/convention as bench_io_gen.py's SW703).
    'Switch:SW_SPDT': {'1': (5.08, 2.54), '2': (-5.08, 0), '3': (5.08, -2.54)},
    'mainboard:RESISTOR0603': {'1': (-5.08, 0), '2': (5.08, 0)},
    'Device:LED': {'1': (-3.81, 0), '2': (3.81, 0)},
    'Connector:TestPoint': {'1': (0, 0)},
    'power:GND': {'1': (0, 0)},
    'power:+3V3': {'1': (0, 0)},
}

out = []          # body s-expr lines (everything between lib_symbols and sheet_instances)
lib_used = set()

def emit(s):
    out.append(s)

# ------------------------------------------------------------------- symbol
def place_symbol(lib_id, ref, value, footprint, datasheet, description, x, y, rot=0,
                  mirror=None, extra_props=None, dnp_pin1_nc=False,
                  ref_dx=2.54, ref_dy=-2.54, val_dx=2.54, val_dy=2.54,
                  hide_ref=False, hide_val=False, pwr_val_dy=3.556):
    """Emit a symbol instance, return {pin_num: (gx,gy)}."""
    lib_used.add(lib_id)
    uid = U()
    is_power = lib_id.startswith('power:') or lib_id.startswith('flatsat:')
    lines = []
    lines.append('\t(symbol')
    lines.append('\t\t(lib_id "%s")' % lib_id)
    # KiCad always writes the explicit angle, even 0 (e.g. primer's GND sample
    # "(at 389.89 238.76 0)"); omitting it for rot==0 desyncs kicad-cli's parser
    # for everything that follows in the file.
    at = '\t\t(at %s %s %s)' % (fmt(x), fmt(y), fmt(rot))
    lines.append(at)
    lines.append('\t\t(unit 1)')
    lines.append('\t\t(body_style 1)') if False else None
    lines.append('\t\t(exclude_from_sim no)')
    lines.append('\t\t(in_bom yes)')
    lines.append('\t\t(on_board yes)')
    lines.append('\t\t(in_pos_files yes)')
    lines.append('\t\t(dnp no)')
    if mirror:
        lines.append('\t\t(mirror %s)' % mirror)
    lines.append('\t\t(uuid "%s")' % uid)

    def prop(name, val, dx, dy, hide=True, extra_size=1.27):
        lines.append('\t\t(property "%s" "%s"' % (name, val))
        lines.append('\t\t\t(at %s %s 0)' % (fmt(x + dx), fmt(y + dy)))
        if hide:
            lines.append('\t\t\t(hide yes)')
        lines.append('\t\t\t(show_name no)')
        lines.append('\t\t\t(do_not_autoplace no)')
        lines.append('\t\t\t(effects')
        lines.append('\t\t\t\t(font')
        lines.append('\t\t\t\t\t(size %s %s)' % (extra_size, extra_size))
        lines.append('\t\t\t\t)')
        lines.append('\t\t\t)')
        lines.append('\t\t)')

    if is_power:
        # pwr_val_dy: power:GND's graphic (and so its visible Value) hangs BELOW the
        # pin (+y), power:+3V3's sits ABOVE it (-y).  The library symbols say so
        # directly -- GND's Value is at lib (0,-3.81), +3V3's at lib (0,+3.556), and
        # KiCad's lib y axis points up, so the schematic-space sign flips.  Pass
        # pwr_val_dy=-3.556 for a rail symbol or its "+3V3" text lands on the wire.
        lines.append('\t\t(property "Reference" "#%s"' % ref)
        lines.append('\t\t\t(at %s %s 0)' % (fmt(x), fmt(y - pwr_val_dy)))
        lines.append('\t\t\t(hide yes)(show_name no)(do_not_autoplace no)')
        lines.append('\t\t\t(effects (font (size 1.27 1.27)))')
        lines.append('\t\t)')
        lines.append('\t\t(property "Value" "%s"' % value)
        lines.append('\t\t\t(at %s %s 0)' % (fmt(x), fmt(y + pwr_val_dy)))
        lines.append('\t\t\t(show_name no)(do_not_autoplace no)')
        lines.append('\t\t\t(effects (font (size 1.27 1.27)))')
        lines.append('\t\t)')
        prop("Footprint", footprint, 0, 0)
        prop("Datasheet", datasheet, 0, 0)
        prop("Description", description, 0, 0)
    else:
        lines.append('\t\t(property "Reference" "%s"' % ref)
        lines.append('\t\t\t(at %s %s 0)' % (fmt(x + ref_dx), fmt(y + ref_dy)))
        if hide_ref:
            lines.append('\t\t\t(hide yes)')
        lines.append('\t\t\t(show_name no)(do_not_autoplace no)')
        lines.append('\t\t\t(effects (font (size 1.27 1.27)))')
        lines.append('\t\t)')
        lines.append('\t\t(property "Value" "%s"' % value)
        lines.append('\t\t\t(at %s %s 0)' % (fmt(x + val_dx), fmt(y + val_dy)))
        if hide_val:
            lines.append('\t\t\t(hide yes)')
        lines.append('\t\t\t(show_name no)(do_not_autoplace no)')
        lines.append('\t\t\t(effects (font (size 1.27 1.27)))')
        lines.append('\t\t)')
        prop("Footprint", footprint, 0, 5.08)
        prop("Datasheet", datasheet, 0, 0)
        prop("Description", description, 0, 0)
    if extra_props:
        for pname, pval in extra_props:
            prop(pname, pval, 0, 0)

    pins_local = PINS[lib_id]
    gpins = {}
    for num, (px, py) in pins_local.items():
        ox, oy = transform(px, py, rot, mirror)
        gx, gy = x + ox, y + oy
        gpins[num] = (round(gx, 4), round(gy, 4))
        lines.append('\t\t(pin "%s"' % num)
        lines.append('\t\t\t(uuid "%s")' % U())
        lines.append('\t\t)')

    lines.append('\t\t(instances')
    lines.append('\t\t\t(project "%s"' % PROJECT)
    lines.append('\t\t\t\t(path "%s"' % INST_PATH)
    lines.append('\t\t\t\t\t(reference "%s")' % (('#' + ref) if is_power else ref))
    lines.append('\t\t\t\t\t(unit 1)')
    lines.append('\t\t\t\t)')
    lines.append('\t\t\t)')
    lines.append('\t\t)')
    lines.append('\t)')
    emit('\n'.join(lines))
    return gpins

def wire(p1, p2):
    emit('\t(wire\n\t\t(pts\n\t\t\t%s %s\n\t\t)\n\t\t(stroke\n\t\t\t(width 0)\n\t\t\t(type default)\n\t\t)\n\t\t(uuid "%s")\n\t)' %
         (pt(*p1), pt(*p2), U()))

def junction(p):
    emit('\t(junction\n\t\t(at %s %s)\n\t\t(diameter 0)\n\t\t(color 0 0 0 0)\n\t\t(uuid "%s")\n\t)' %
         (fmt(p[0]), fmt(p[1]), U()))

def no_connect(p):
    emit('\t(no_connect\n\t\t(at %s %s)\n\t\t(uuid "%s")\n\t)' % (fmt(p[0]), fmt(p[1]), U()))

def global_label(text, shape, x, y, rot=0, justify=None):
    j = ('\n\t\t\t(justify %s)' % justify) if justify else ''
    emit('\t(global_label "%s"\n\t\t(shape %s)\n\t\t(at %s %s %s)\n\t\t(fields_autoplaced yes)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)%s\n\t\t)\n\t\t(uuid "%s")\n\t\t(property "Intersheetrefs" "${INTERSHEET_REFS}"\n\t\t\t(at %s %s 0)\n\t\t\t(hide yes)\n\t\t\t(show_name no)\n\t\t\t(do_not_autoplace no)\n\t\t\t(effects\n\t\t\t\t(font\n\t\t\t\t\t(size 1.27 1.27)\n\t\t\t\t)\n\t\t\t)\n\t\t)\n\t)' %
         (text, shape, fmt(x), fmt(y), fmt(rot), j, U(), fmt(x), fmt(y)))
    return (x, y)

def local_label(text, x, y, rot=0, justify="left bottom"):
    emit('\t(label "%s"\n\t\t(at %s %s %s)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size 1.27 1.27)\n\t\t\t)\n\t\t\t(justify %s)\n\t\t)\n\t\t(uuid "%s")\n\t)' %
         (text, fmt(x), fmt(y), fmt(rot), justify, U()))

def text_note(s, x, y, size=1.27):
    # KiCad encodes an embedded newline in a quoted string as the literal two
    # characters backslash+n (see eps_side.kicad_sch "Schottky Diode\n...");
    # a *raw* newline byte inside the string corrupts the S-expression stream
    # for every item that follows it, even though kicad-cli fails silently.
    # Explicit "left top": with no justify, KiCad centers text on (at), which
    # runs multi-line left-anchored notes off the left edge of the page (see
    # bench_io_gen.py add_text for the same fix).
    esc = s.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')
    emit('\t(text "%s"\n\t\t(exclude_from_sim no)\n\t\t(at %s %s 0)\n\t\t(effects\n\t\t\t(font\n\t\t\t\t(size %s %s)\n\t\t\t)\n\t\t\t(justify left top)\n\t\t)\n\t\t(uuid "%s")\n\t)' %
         (esc, fmt(x), fmt(y), size, size, U()))

# ============================================================ SHEET CONTENT

text_note("Pyro Inhibit and Jumpers", 25.4, 12.7, 2.54)
text_note("PROVES FlatSat V1 -- Phase 1", 25.4, 17.78, 1.27)
text_note("Bench inhibit for the FC's live pyro/heater driver U6 (TPS4H160): one switch force-lows\n"
          "all three EN nets (Deploy1_EN, Heater_EN, Deploy2_EN) through Schottky diodes so an\n"
          "inhibited bench is always safe by default. Also carries six parallel bench-shunt headers\n"
          "across the existing RBF/inhibit-chain break points (D6) so the bench can be operated\n"
          "without Pico-Lock crimp pigtails.", 25.4, 24.13, 1.0)

# ---------------------------------------------------------- Section 1: diodes
# Fix round 2 (D1 note vs TP600): anchored at y=39.4, not 36.83 -- the previous
# anchor put the note's top line exactly where TP600's circle/lead sit (both at
# x=35.56, y=36.83), so the note's own two lines struck through the symbol.
# y=39.4 clears TP600 (which stays at y=36.83) while still finishing well above
# the Deploy1_EN row at y=44.45.
text_note("EN-Line Force-Low Diodes (D1) -- flight_controller_board#53 (ch3/ch4 crossed) is unresolved,\n"
          "so the heater channel cannot be assumed non-pyro; one inhibit covers all three EN nets.", 25.4, 36.83, 1.0)
# Fix round 2: TP600-603's Reference/Value stay hidden (see the collision analysis
# in sheet_pyro_inhibit.md Sec 10.1 item 2 -- un-rotating them or showing rotated
# text both reintroduce real collisions at this row pitch). Instead, a visible
# legend maps each hidden refdes to its net, placed in open canvas clear of every
# other note/label/wire on the sheet (well below and right of the D1 note's text
# extent, which runs out past x=103 on its own).
text_note("Test points (Ref/Value hidden on-canvas; net name shown here):\n"
          "  TP600 = Deploy1_EN   TP601 = Heater_EN   TP602 = Deploy2_EN   TP603 = PYRO_INH_COM",
          110.0, 50.0, 1.0)

# Supply-chain pass 2026-09-14 (rev 2, verifier fix): all eight JP600-607 headers use
# the same JLC part (C124375, B-2100S02P-A110, 1x02 2.54mm THT). Rev 1 of this pass
# picked C5383111 using an uncast "ORDER BY Stock DESC" on the FTS5 catalogue, where
# every column (Stock included) is compared as TEXT -- that sorts lexicographically,
# not numerically, and hid far-better-stocked identical-footprint/pitch rows. Rerun
# with "ORDER BY CAST(Stock AS INTEGER) DESC": within the same filter (Second
# Category='Pin Headers', Description LIKE '%1x2P%'/'%1*2P%', Package LIKE 'Plugin%')
# restricted to the report's own "both pitch dims 2.54mm 2.54mm" tie-break, C124375
# (159,910 in stock) tops the list -- 16x the stock of the rev-1 pick C5383111
# (9,828), same package/pitch/Extended-lib class. See supply_pyro_inhibit.md.
JP_DATASHEET = 'https://www.lcsc.com/datasheet/lcsc_datasheet_2411220201_Ckmtw-Shenzhen-Cankemeng-B-2100S02P-A110_C124375.pdf'

BUS_X = 76.2
rows = [
    ("Deploy1_EN", 44.45, False, "D600"),
    ("Heater_EN", 57.15, True, "D601"),
    ("Deploy2_EN", 69.85, False, "D602"),
]
diode_cathodes = {}
for net, y, has_jumper, dref in rows:
    lx = 25.4
    # Fix round 2: this label sits at the LEFT end of a rightward wire (lx -> tp_x);
    # rot0/justify-left ran the text on top of that same wire. rot180/justify-right
    # flows the text away from the wire, matching the convention already used on
    # eps_side/load_switches/solar_emulation for left-side labels.
    global_label(net, "passive", lx, y, 180, justify="right")
    # test point tap partway along the row
    # Fix round 2: TP600 taps at x=48 (close to D600's anode) instead of the usual
    # 35.56 -- see the tp_y note just below for why.
    if net == "Deploy1_EN":
        tp_x = 48.26  # 38 * GRID -- stay on the 1.27 mm grid
    else:
        tp_x = 35.56 if not has_jumper else 31.75
    # Rotated TestPoint Reference/Value fields render as vertical text at this
    # symbol scale (KiCad composes the field's own angle with the symbol's 90 deg
    # rotation) and this row spacing leaves no clear band for a ~6 mm-tall vertical
    # string next to the row above/below's global label and, on the jumper rows,
    # JP600's Value -- both fields are hidden; the net is still named by the wired
    # global label on this row, the Description property, and the sheet's own
    # "Test points on the three EN nets and PYRO_INH_COM" note.
    # Fix round 2: TP600 alone drops BELOW its row (y+3.81) at tp_x=48 instead of
    # the usual "above" placement (y-7.62) at tp_x=35.56. Above the Deploy1_EN row
    # is exactly where the D1 text note sits (25.4,36.83) -- routing TP600's lead
    # wire up through that band struck through the note's own text (confirmed in a
    # 300 dpi re-render). Below the row at the *usual* x=35.56 instead put TP600
    # within a few mm of TP601 (which sits at (31.75,49.53), just below the same
    # row, on its own Heater_EN tap) -- their rotated pin-stub-plus-circle graphics
    # visually interleaved (also confirmed by re-render). Moving 12.4 mm right to
    # x=48 (near D600's own anode) keeps TP600 (48,48.26) >=16 mm from TP601's
    # centre while staying a short, uncrowded drop from the Deploy1_EN row.
    tp_y = y + 3.81 if net == "Deploy1_EN" else y - 7.62
    tp = place_symbol('Connector:TestPoint', 'TP60%d' % (0 if net == "Deploy1_EN" else (1 if net == "Heater_EN" else 2)),
                       net, 'TestPoint:TestPoint_Pad_D1.5mm', '', 'Test point on %s' % net,
                       tp_x, tp_y, 90, hide_val=True, hide_ref=True)
    wire((lx, y), (tp_x, y))
    wire((tp_x, y), tp['1'])
    junction((tp_x, y))
    if has_jumper:
        jp = place_symbol('Jumper:Jumper_2_Open', 'JP600', 'Conn_01x02', 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
                           JP_DATASHEET, 'Heater_EN leg jumper -- shunt fitted by default (D1); remove to exclude heater from inhibit',
                           40.64, y, 0,
                           extra_props=[("LCSC Part", "C124375")])  # B-2100S02P-A110 1x02 2.54mm THT pin header,
                                                                     # Extended, stock 159910 -- supply-chain pass rev 2
        wire((tp_x, y), jp['1'])
        anode_start = jp['2']
    else:
        anode_start = (tp_x, y)
    d = place_symbol('Diode:BAT54W', dref, 'BAT54W', 'Package_TO_SOT_SMD:SOT-323_SC-70',
                      'https://assets.nexperia.com/documents/data-sheet/BAT54W_SER.pdf',
                      'Schottky, anode on %s, cathode -> PYRO_INH_COM' % net,
                      57.15, y, 180,
                      extra_props=[("LCSC Part", "C77328")])  # Nexperia BAT54W SOT-323, Extended,
                                                                # stock 7403 -- supply-chain pass 2026-09-14
    wire(anode_start, d['1'])
    no_connect(d['2'])
    diode_cathodes[net] = d['3']
    wire(d['3'], (BUS_X, y))

# vertical PYRO_INH_COM riser segments (top to bottom), junctions at every interior tap
riser_ys = [44.45, 57.15, 69.85, 76.2, 82.55, 88.9, 95.25]
for i in range(len(riser_ys) - 1):
    wire((BUS_X, riser_ys[i]), (BUS_X, riser_ys[i + 1]))
for y in riser_ys[1:-1]:
    junction((BUS_X, y))

# ------------------------------------------------ Section 2: sense/LED/pull-up
text_note("Inhibit State Sense, SAFE LED, Pull-up", 25.4, 111.76, 1.4)

# R601 sense resistor: PYRO_INH_COM (bus tap y=76.2) -> PYRO_INHIBIT_STATE
r601 = place_symbol('mainboard:RESISTOR0603', 'R601', '4.7k', 'Resistor_SMD:R_0402_1005Metric', '',
                     'Series sense R, PYRO_INH_COM to PYRO_INHIBIT_STATE (RP2350 erratum E9: <=8.2k)',
                     81.28, 76.2, 0, val_dy=-5.08,  # Value stacked above the Reference (both above
                                                     # the body) -- LED600 sits 6.35 mm below and its
                                                     # Reference would collide with a Value placed below.
                     extra_props=[("LCSC Part", "C25900")])  # 4.7k 0402, BOM-proves_radio_stick_V2.csv R14/R15
assert r601['1'] == (BUS_X, 76.2)
# Name the commoned diode-cathode/switch/pull-up/LED/sense net so the netlist and
# the sheet's own text notes (which refer to "PYRO_INH_COM" by name) agree.
# justify "right bottom": text sits above-left of the tap, in the clear space between
# the D602 row and R601 -- "left bottom" (the default) collides with R601's Reference/
# Value stack, which sits immediately up-right of this same point.
local_label("PYRO_INH_COM", BUS_X, 76.2, justify="right bottom")
global_label("PYRO_INHIBIT_STATE", "output", 101.6, 76.2, 0, justify="left")
wire(r601['2'], (101.6, 76.2))
tp603 = place_symbol('Connector:TestPoint', 'TP603', 'PYRO_INH_COM', 'TestPoint:TestPoint_Pad_D1.5mm', '',
                      'Test point on PYRO_INH_COM', BUS_X, 34.29, 90, hide_val=True, hide_ref=True)
# TP603's Reference/Value are hidden for the same reason as TP600-602 above --
# rotated vertical text with no clear band between the two text notes at this x.
wire((BUS_X, 34.29), (BUS_X, 44.45))
junction((BUS_X, 44.45))

# LED600 + R602: 3V3_EMU -> R602 -> LED600(A->K) -> PYRO_INH_COM (bus tap y=82.55)
global_label("3V3_EMU", "input", 101.6, 60.96, 0, justify="left")
# Fix round 2 (unmarked 4-way meeting point): R602 was at x=91.44, so its pin1
# (x=86.36) put the vertical R602->LED600 wire on the exact same x column as
# R601's pin2 (86.36,76.2) -- the wire passed straight through that pin with no
# junction, and through the PYRO_INHIBIT_STATE wire's own start point at the same
# coordinate. Moved to x=93.98 so pin1 lands at x=88.9 instead: the vertical run
# (88.9,60.96)-(88.9,82.55) crosses the R601->PYRO_INHIBIT_STATE wire
# (86.36,76.2)-(101.6,76.2) only at (88.9,76.2), which is the *interior* of both
# segments (not a pin, not either wire's endpoint) -- an ordinary unconnected
# crossing, ambiguous to no tool or reviewer, needing no junction.
# Integrator fix round 2: LED600's assigned LCSC C2290 is a WHITE 0603 (Vf 2.6-3.1 V), not the
# ~2.0 V green the 1 k was sized for -- 1 k gave 0.2-0.8 mA and a nearly dark SAFE indicator at
# worst-case Vf.  470 R (C25117, UNI-ROYAL 0402WGF4700TCE, 0402 1 % Basic, 62.5 mW) gives
# 0.43-1.49 mA over the Vf spread, ~0.96 mA typ, 1.0 mW worst case.
r602 = place_symbol('mainboard:RESISTOR0603', 'R602', '470R', 'Resistor_SMD:R_0402_1005Metric', '',
                     'SAFE LED series R: (3.3 V - Vf 2.6..3.1 V) / 470 R = 0.43..1.49 mA (~0.96 mA typ)',
                     93.98, 60.96, 0,
                     extra_props=[("LCSC Part", "C25117")])  # 470R 0402 1% Basic, JLC catalogue
wire((101.6, 60.96), r602['2'])
# LED600 rotation 0: pin1=K at center-3.81 (left), pin2=A at center+3.81 (right).
# Center it so K lands exactly on the PYRO_INH_COM bus (x=76.2) at the y=82.55 tap.
# Value is plain "LED" to match the LCSC part actually assigned (C2290 = Hubei KENTO KT-0603W,
# a WHITE 0603) and the three other C2290 instances on this project (emulator_mcu D201/D202,
# battery_protection_replica D510) plus proves_radio_stick_V2 D1/D3, so a grouped BOM emits one
# line for one part number.  "LED_GREEN" was wrong on both counts.  Integrator fix round 2.
led = place_symbol('Device:LED', 'LED600', 'LED', 'LED_SMD:LED_0603_1608Metric',
                    'https://www.lcsc.com/datasheet/lcsc_datasheet_2305091500_'
                    'Hubei-KENTO-Elec-KT-0603W_C2290.pdf',
                    'SAFE indicator, white 0603 (KT-0603W, Vf 2.6-3.1 V, 360 mcd at 5 mA): lit = inhibit '
                    'engaged AND emulator powered (does not gate the inhibit itself). '
                    'A dark LED does NOT mean the inhibit is released -- verify at TP603 / PYRO_INH_COM.',
                    BUS_X + 3.81, 82.55, 0,
                    extra_props=[("LCSC Part", "C2290")])  # LED_0603_1608Metric, same part as D201/D202/D510 on this project
assert led['1'] == (BUS_X, 82.55)
# R602 pin1 (left, now x=88.9) drops straight down then over to LED's anode (pin2)
wire(r602['1'], (88.9, 82.55))
wire((88.9, 82.55), led['2'])

# R600 pull-up: FC +3V3 -> PYRO_INH_COM (bus tap y=88.9)
#
# Review fix #2 (2026-09-14).  Two changes to one part, and they belong together:
#
#  (a) PM ruling R6: R600 100 k -> 4.7 k, so PYRO_INHIBIT_STATE's pull-up class is
#      inside the RP2350 erratum-E9 8.2 k limit instead of 104.7 k (R600+R601).
#
#  (b) R600's HIGH side moves from 3V3_EMU to the FC +3V3 rail.  R6 as worded kept
#      the pull-up on 3V3_EMU; at 4.7 k that turns a harmless weak pull-up into an
#      armed-state hazard whenever the emulator is unpowered.  With 3V3_EMU at 0 V,
#      R600 is a 4.7 k pull-DOWN on PYRO_INH_COM.  The FC drives each EN net from
#      3.3 V through its own 4.7 k series resistor (R104 Deploy1_EN / R100 Heater_EN
#      / R103 Deploy2_EN, brief 4.1), and the BAT54W then conducts:
#          EN = (3.3 + VF) / 2 ~= 1.8 V   (4.7 k : 4.7 k divider, VF ~ 0.3 V)
#      vs TPS4H160-Q1 VIH(min) 2.0 V -- an FC-only bench run (D11) could silently
#      NOT fire, and the failure depends on a phantom rail level, so it would be
#      intermittent.  On the FC +3V3 the armed node sits at the full +3V3 with both
#      diode ends at the same potential (zero bias, no divider) regardless of the
#      emulator, and +3V3 tracks FC power exactly (U10 runs off VBUSP; USB J12
#      reaches VBUSP through D15).  Inhibited-state behaviour is unchanged: SW600
#      shorts PYRO_INH_COM to GND, 0.70 mA through R600, EN nodes at VF ~ 0.28 V.
#
#      +3V3 is placed as the power:+3V3 power symbol, per brief 4.1 ("power symbols
#      for GND / +3V3") and matching solar_emulation's 8 placements.  Unlike the
#      3V3_EMU case in sheet_pyro_inhibit.md deviation 2, this cannot produce a
#      power_pin_not_driven ERC error in a partial harness: +3V3's power_out driver
#      is the FC's own U10, which is always on disk.
#
#      Consequence, carried into the notes and the report: PYRO_INHIBIT_STATE low
#      now means "inhibit engaged" OR "FC unpowered".  The console must AND it with
#      EMU_FC3V3_SENSE (solar_emulation's 4.7 k FC-+3V3 presence tap) before
#      reporting the inhibit as positively engaged.  The SAFE LED (R602/LED600) is
#      deliberately left on 3V3_EMU -- it is an emulator-side indicator, not an
#      interlock, and moving it would load the FC rail for no gain.
pwr3v3 = place_symbol('power:+3V3', 'PWR602', '+3V3', '', '', 'FC 3.3 V rail (U10) -- source for the '
                      'PYRO_INH_COM pull-up; deliberately NOT 3V3_EMU, see the note on the sheet',
                      101.6, 88.9, 0, pwr_val_dy=-3.556)
assert pwr3v3['1'] == (101.6, 88.9)
r600 = place_symbol('mainboard:RESISTOR0603', 'R600', '4.7k', 'Resistor_SMD:R_0402_1005Metric', '',
                     'PYRO_INH_COM pull-up to the FC +3V3 (R6: 4.7k, <=8.2k for RP2350 erratum E9; '
                     '0.70 mA with SW600 closed). Sourced from +3V3, not 3V3_EMU, so the armed-state '
                     'EN level does not depend on the emulator being powered.',
                     91.44, 88.9, 0,
                     extra_props=[("LCSC Part", "C25900")])  # 4.7k 0402, same part as R601
wire((101.6, 88.9), r600['2'])
wire(r600['1'], (BUS_X, 88.9))

# ---------------------------------------------- Section 3: switch + panel header + GND
# PM ruling S2 (2026-09-14, 00_pm_brief.md Sec 3.1): SW_DIP_SPSTx01_Slide had no JLC part
# (parts-fts5.db has no match for that exact 7.62mm-row DIP-slide footprint -- every
# "SPST"+"Slide"+"7.62mm" search came back empty, and the one MFR.Part hit for the reference
# part number itself, 1MS1T1B1M2QES/C22422208, is 0 stock / not-ROHS -- see
# supply_pyro_inhibit.md). Replaced with a JLC-stocked SMD SPDT slide switch used as SPST:
# MSK12C02 (SHOU-HAN), LCSC C431540, stock 146,433 (Extended -- JLC stocks zero Basic slide
# switches of any kind). Footprint Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02 is a KiCad-
# standard footprint built specifically for this LCSC part (its own descr field cites
# C431540's datasheet URL verbatim); pad geometry verified against the SHOU-HAN MSK12C02
# mechanical drawing (wmsc.lcsc.com PDF for C431540): 8mm-wide body, pins 1/2/3 at 1.5mm/
# 3.0mm spacing, matching the footprint's -2.25/0.75/2.25mm pad x-coordinates. THT
# alternatives (SS-12D00-G3 family) were rejected: 10x less stock (13,170) and no
# project/KiCad-standard footprint tied to that exact MFR.Part, vs. this part's purpose-built
# footprint and the ~20x higher stock. Symbol Switch:SW_SPDT (pantry block, same symbol
# bench_io's SW703 uses): pin 2 is the common wiper, pins 1 and 3 are the two throws (pin 1
# sits above the common at y=92.71, pin 3 below it at y=97.79, per the symbol's own local pin
# coordinates transformed at rot=0). Wired exactly as SW_SPST was: common (pin 2) to
# PYRO_INH_COM at BUS_X (same node SW_SPST's pin 1 used), one throw (pin 3, the lower one --
# it lines up with the existing GND-column run down to JP601) to GND in place of SW_SPST's old
# pin 2 -- so the switch is still electrically SPST and "closed" (slider toward pin 3) still
# means common-to-GND = INHIBIT / SAFE, exactly as before. The other throw (pin 1) is not
# used: marked no_connect instead of left off the symbol.
sw = place_symbol('Switch:SW_SPDT', 'SW600', 'MSK12C02',
                   'Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02',
                   'https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_SHOU-HAN-MSK12C02_C431540.pdf',
                   'Pyro inhibit switch (SPDT used as SPST) -- common (pin 2) to PYRO_INH_COM, '
                   'pin 3 to GND, pin 1 (unused throw) no_connect. Slider toward pin 3 = closed '
                   '= inhibited = safe default.',
                   81.28, 95.25, 0,
                   extra_props=[("LCSC Part", "C431540")],
                   # SW_SPDT's own rectangle body spans +-3.81mm vertically from centre (bigger
                   # than SW_SPST's, which had no box) -- default +-2.54 would land the text
                   # inside that box (same fix bench_io_gen.py's SW703 uses), so pushed to +-5.08.
                   ref_dy=-5.08, val_dy=5.08)
assert sw['2'] == (BUS_X, 95.25)
junction((BUS_X, 95.25))

jp601 = place_symbol('Jumper:Jumper_2_Open', 'JP601', 'Conn_01x02', 'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical',
                      JP_DATASHEET, 'Parallel header for an external panel-mount inhibit switch (no shunt; wire a 2-pin switch cable here)',
                      81.28, 107.95, 0,
                      extra_props=[("LCSC Part", "C124375")])  # same 1x02 2.54mm THT header as JP600/JP602-607
assert jp601['1'] == (BUS_X, 107.95)
wire((BUS_X, 95.25), (BUS_X, 107.95))
gnd1 = place_symbol('power:GND', 'PWR600', 'GND', '', '', 'GND', 86.36, 113.03, 0)
assert sw['1'] == (86.36, 92.71) and sw['3'] == (86.36, 97.79) and jp601['2'] == (86.36, 107.95)
wire(sw['3'], (86.36, 107.95))
no_connect(sw['1'])
junction((86.36, 107.95))
wire((86.36, 107.95), gnd1['1'])

text_note("SW600 closed and/or JP601 bridged pulls PYRO_INH_COM low (inhibited). R600 (4.7k) and the SAFE LED\n"
          "path can never raise an EN node: each is separated from Deploy1_EN/Heater_EN/Deploy2_EN by its own\n"
          "reverse-biased BAT54W (anode toward the EN net) -- current can only flow EN-net -> PYRO_INH_COM.\n"
          "R600 pulls PYRO_INH_COM up to the FC +3V3, NOT to 3V3_EMU -- see the boxed note at right.\n"
          "SAFE LED (R602 + LED600) stays on 3V3_EMU: lit = inhibit engaged AND emulator powered. A dark LED does\n"
          "NOT mean the inhibit is released -- SW600/JP601 depend on neither rail. Verify at TP603 / PYRO_INH_COM.\n"
          "JP600 REMOVED: SAFE LED and PYRO_INHIBIT_STATE then cover Deploy1/Deploy2 only; Heater_EN is live --\n"
          "treat ch3/ch4 as ARMED (D1 / flight_controller_board#53).\n"
          "LED600 = C2290, a WHITE 0603 (Vf 2.6-3.1 V); R602 = 470 R gives 0.43-1.49 mA, ~0.96 mA typical.",
          # Anchor stays at 118.11.  text_note() emits "justify left top", so this block runs
          # DOWNWARD from the anchor: review fix #2/#6 grew it from 6 to 9 lines, so
          # 9 x 1.62 mm = 118.11..132.69, still clear of #PWR600's "GND" value text above
          # (ends 117.35); the next note below was pushed 132.08 -> 134.62 to match.
          # NB tools/gen/geomcheck.py models every (text) block as vertically CENTRED on its anchor,
          # which is right for solar_emulation but not for this sheet's top-justified notes, so its
          # one "text-over-text" hit here (GND vs this block) is a false positive.  Verified in the
          # rendered PDF instead.  Integrator fix round 2.
          25.4, 118.11, 1.0)
# Fix round 2: pushed from y=127.0 to y=132.08 (+5.08) -- the block above grew
# from 3 to 5 lines (added the SAFE-LED-vs-inhibit-state note) and would otherwise
# run into this note's first line at the 2.54 mm/line pitch used throughout this
# sheet.  Review fix #2/#6 grew that block again (6 -> 9 lines, now ending at
# 132.69), so this anchor moves 132.08 -> 134.62 (+2.54, still on the 1.27 grid):
# 3 lines -> 134.62..139.48, clear of the shunt-header heading at 142.24.
text_note("With the switch closed each EN node sits at VF(BAT54W) ~= 0.28 V at 0.64 mA (<=240 mV @ 0.1 mA,\n"
          "<=320 mV @ 1 mA, Nexperia BAT54W_SER) vs TPS4H160-Q1 VIL(max) 0.8 V, VIH(min) 2 V (Sec 6.5 Logic\n"
          "Input; IN pins have 100-250 kOhm internal pull-downs) -- comfortably inhibited.",
          25.4, 134.62, 1.0)

# Review fix #7, updated for PM ruling S2 (2026-09-14): the old SW_DIP_SPSTx01_Slide
# footprint silkscreened only the word "on" with no safe/armed sense; the new MSK12C02 SMD
# slide switch carries no on-board safe/armed silkscreen at all, so the mapping has to live
# on the schematic either way.  Placed at x=95.25 (right of the switch ladder, which ends at
# x=86.36) rather than at the sheet's usual x=25.4: a left-anchored note here would run right
# into the SW600 -> JP601 riser at x=76.2, y=95.25..107.95.  Lines are kept under ~34
# characters (~0.78 mm/char at size 1.0, so the block ends near x=122) to stay clear
# of the boxed R600 note that starts at x=139.7 -- the first cut of this note ran
# 59 characters wide and struck through that box in the rendered PDF.
text_note("SW600 (MSK12C02): pin 3 =\n"
          "CLOSED = INHIBIT / SAFE\n"
          "(default). Pin 1 (NC) = ARMED.\n"
          "JP601 panel switch is in\n"
          "parallel: closed = SAFE too.",
          95.25, 99.06, 1.0)

# Review fix #2: the "why" for R600's supply, boxed off in the sheet's empty right-hand
# canvas (x >= 125, nothing else on this sheet reaches past x ~ 115) so the dense
# left-hand ladder notes stay readable.  Per CLAUDE.md hard rule 3 a schematic text
# note is a requirement: this one exists so a future respin does not "tidy" R600 back
# onto 3V3_EMU to match brief 6.5's literal wording.
text_note("WHY R600 PULLS UP TO THE FC +3V3 AND NOT TO 3V3_EMU (review fix, chair-accepted\n"
          "deviation from brief Sec 6.5's literal '100 k pull-up from 3V3_EMU')\n"
          "PM ruling R6 sets R600 = 4.7 k so PYRO_INHIBIT_STATE's pull-up class is inside the\n"
          "RP2350 erratum-E9 8.2 k limit. Taken literally -- 4.7 k to 3V3_EMU -- the pull-up\n"
          "becomes a 4.7 k pull-DOWN whenever the emulator is unpowered: an FC-commanded EN\n"
          "(3.3 V behind its own 4.7 k, R104/R100/R103) divides through the forward BAT54W to\n"
          "(3.3 + VF)/2 ~= 1.8 V, under TPS4H160-Q1 VIH(min) 2.0 V, so an FC-only bench run\n"
          "(D11) could silently not fire -- and the level depends on a phantom rail, so it\n"
          "would be intermittent. On the FC +3V3 both ends of each diode sit at the same\n"
          "potential when armed (zero bias, no divider): EN stays at +3V3 whether or not the\n"
          "emulator is powered, and +3V3 tracks FC power exactly (U10 off VBUSP; USB J12\n"
          "reaches VBUSP through D15). Inhibited state is unchanged (0.70 mA through R600).\n"
          "R601 4.7 k limits back-feed into an unpowered emulator's ESD diode to ~0.55 mA,\n"
          "the same sense-tap rule solar_emulation uses for EMU_FC3V3_SENSE.\n"
          "CONSOLE RULE: PYRO_INHIBIT_STATE low now means 'inhibit engaged' OR 'FC unpowered'.\n"
          "AND it with EMU_FC3V3_SENSE before reporting the inhibit as positively engaged.",
          # x=139.7 (110 x 1.27, on grid).  Nothing else on this sheet reaches past
          # x ~ 122, and the block's widest line (~84 chars) ends near x=205, well
          # left of the A3 title block (x >= 290, y >= 255).
          139.7, 88.9, 1.0)

# ==================================================== Section 4: bench inhibit shunt headers
text_note("Bench RBF / Inhibit Shunt Headers (D6) -- parallel taps only, nothing in series with a flight power\n"
          "path. 2-pin 2.54 mm headers, open by default (~3 A shunt when bridged). Flight units never fit these;\n"
          "the crimp-pigtail connectors listed remain the primary break points.", 25.4, 142.24, 1.0)

HDR_Y0 = 154.94
HDR_DY = 15.24
LEFT_X = 33.02
JP_PIN_GAP = 5.08  # Jumper_2_Open pin to pin is 10.16; center offset 5.08
RIGHT_LABEL_X = 91.44

shunt_rows = [
    ("JP602", "INH_S1", "VBATT_SENSE", "INHIB_1", "passive", "passive", "|| J8 (INHIBIT_S1_Picolock)"),
    ("JP603", "INH_S2", "INHIB_1", "IN_RBF", "passive", "passive", "|| J29 (INHIBIT_S2_Picolock)"),
    ("JP604", "INH_P1", "VBATT_SENSE", "INHIB_2", "passive", "passive", "|| J7 (INHIBIT_P1)"),
    ("JP605", "INH_P2", "INHIB_2", "IN_RBF", "passive", "passive", "|| J10 (INHIBIT_P2)"),
    ("JP606", "RBF", "IN_RBF", "VBUSP", "passive", "bidirectional", "|| J20/J30 (RBF_Inhibit / RBF_Picolock)"),
]

for i, (ref, name, left_net, right_net, lshape, rshape, note) in enumerate(shunt_rows):
    y = HDR_Y0 + i * HDR_DY
    # Fix round 2: left-hand label at the start of a rightward wire -- rot180/
    # justify-right flows text away from the wire (see the EN-row fix above).
    global_label(left_net, lshape, LEFT_X, y, 180, justify="right")
    jp = place_symbol('Jumper:Jumper_2_Open', ref, 'Conn_01x02',
                       'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical', JP_DATASHEET,
                       '%s bench inhibit shunt header, %s' % (name, note),
                       58.42, y, 0,
                       extra_props=[("LCSC Part", "C124375")])  # same 1x02 2.54mm THT header as JP600/601
    wire((LEFT_X, y), jp['1'])
    global_label(right_net, rshape, RIGHT_LABEL_X, y, 0, justify="left")
    wire(jp['2'], (RIGHT_LABEL_X, y))
    text_note(note, LEFT_X, y - 5.08, 1.0)

# ISS row (B- <-> GND) -- separate because the right side is a power symbol, not a label
iss_y = HDR_Y0 + len(shunt_rows) * HDR_DY
# Fix round 2: same left-label-on-rightward-wire fix as the shunt rows above --
# rot180/justify-right so the "-" of "B-" is not struck through by the wire.
global_label("B-", "passive", LEFT_X, iss_y, 180, justify="right")
jp607 = place_symbol('Jumper:Jumper_2_Open', 'JP607', 'Conn_01x02',
                      'Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical', JP_DATASHEET,
                      'ISS bench inhibit shunt header, || J15/J19 (ISS_INHIBIT / ISS_INHIBIT_Picolock)',
                      58.42, iss_y, 0,
                      extra_props=[("LCSC Part", "C124375")])  # same 1x02 2.54mm THT header as JP600-606
wire((LEFT_X, iss_y), jp607['1'])
gnd2 = place_symbol('power:GND', 'PWR601', 'GND', '', '', 'GND', RIGHT_LABEL_X, iss_y, 0)
wire(jp607['2'], (RIGHT_LABEL_X, iss_y))
text_note("|| J15/J19 (ISS_INHIBIT / ISS_INHIBIT_Picolock)", LEFT_X, iss_y - 5.08, 1.0)

text_note("Jumper population table:\n"
          "  SW600 (on-board inhibit)    -- MSK12C02 SPDT-as-SPST: pin 3 = CLOSED = INHIBIT / SAFE\n"
          "                                 (default); pin 1 (NC, unused throw) = ARMED.\n"
          "  JP600 (Heater_EN leg)       -- SHUNT FITTED by default. Remove to exclude the heater channel\n"
          "                                 from the inhibit without a respin (D1).\n"
          "                                 CAVEAT: with JP600 removed the SAFE LED and PYRO_INHIBIT_STATE\n"
          "                                 cover Deploy1/Deploy2 only; Heater_EN is live -- treat ch3/ch4\n"
          "                                 as ARMED (D1 / flight_controller_board#53).\n"
          "  JP601 (panel switch header) -- no shunt; wire an external 2-pin panel-mount switch here, in\n"
          "                                 parallel with the on-board SW600. Closed = SAFE.\n"
          "  JP602-JP607 (bench RBF/inhibit shunts) -- OPEN by default. Bridge with a shunt only when the\n"
          "                                 matching crimp connector (J7/J8/J10/J15/J19/J20/J29/J30) is not\n"
          "                                 fitted. Never fitted on flight units.\n"
          "\n"
          "POWER-UP RECIPE -- to power the FC with no crimp plugs fitted, bridge:\n"
          "  JP607 (B- return) + JP606 (RBF -- CLOSING THIS ENERGISES VBUSP)\n"
          "  + ONE inhibit path: JP602 + JP603, or JP604 + JP605. Leave the others open.\n"
          "JP606 is the opposite of the naive 'remove before flight = safety pin' reading: a shunt ACROSS\n"
          "JP606 CLOSES IN_RBF to VBUSP and turns the FC on; pulling it opens the bus. The FC's own USB J12\n"
          "powers VBUSP through D15 (DFLS130L) regardless of every jumper on this sheet, so 'all jumpers\n"
          "open' is NOT a guarantee that VBUSP is dead -- unplug USB as well.",
          25.4, iss_y + 12.7, 1.0)

# =============================================================== file assembly
lib_block_files = {
    'power:GND': 'power_GND.sexp',
    'power:+3V3': 'power_+3V3.sexp',
    'Diode:BAT54W': 'Diode_BAT54W.sexp',
    'Jumper:Jumper_2_Open': 'Jumper_Jumper_2_Open.sexp',
    'Switch:SW_SPST': 'Switch_SW_SPST.sexp',
    'Switch:SW_SPDT': 'Switch_SW_SPDT.sexp',
    'mainboard:RESISTOR0603': 'mainboard_RESISTOR0603.sexp',
    'Device:LED': 'Device_LED.sexp',
    'Connector:TestPoint': 'Connector_TestPoint.sexp',
}
lib_symbols_text = []
for lid in sorted(lib_used):
    fn = os.path.join(PANTRY, lib_block_files[lid])
    with open(fn) as f:
        lib_symbols_text.append(f.read().rstrip('\n'))

header = []
header.append('(kicad_sch')
header.append('\t(version 20260306)')
header.append('\t(generator "eeschema")')
header.append('\t(generator_version "10.0")')
header.append('\t(uuid "%s")' % U())
header.append('\t(paper "A3")')
header.append('\t(lib_symbols')
header.append('\n'.join(lib_symbols_text))
header.append('\t)')

footer = []
footer.append(')')

full = '\n'.join(header) + '\n' + '\n'.join(out) + '\n' + '\n'.join(footer) + '\n'

tmp = OUT + '.tmp'
with open(tmp, 'w') as f:
    f.write(full)
os.replace(tmp, OUT)
print('wrote', os.path.abspath(OUT), len(full), 'bytes')
