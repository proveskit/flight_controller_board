# FlatSat V1 Phase-2 floorplan — Proposal 1

**Agent:** Floorplan proposer #1 (Sonnet) · **Date:** 2026-09-14 · **Emphasis (owner's instruction):**
shortest-connections-first — minimise the length of every new-to-existing net, accepting a less regular
block layout to do it.

## 1. Outline

Uses `tools/pcb/outline_L1.json` **unmodified** (no ±15 mm adjustment to the wing/strip): right wing
65 mm to x=296.39 (full height y47.51–142.12), bottom strip 30 mm to y=172.12 (full new width 153 mm,
x143.34–296.39). New board bbox after `outline.py`: **x 143.29–296.44, y 47.51–172.17** (153.05 × 124.56 mm
board footprint per `kicad-cli pcb stats`, 184.1 cm² total board area). New area added ≈ wing (65×94.61 mm
= 61.5 cm²) + strip (153×30 mm = 45.9 cm²) = **107.4 cm²**, matching the brief's own L1 estimate.

Reasons the default was kept rather than adjusted: the default already gives ~107 cm² for ~50 cm² of
component footprint (see §5), and every block in this proposal fit inside it with room to spare once the
face-front-end column was moved onto the west (near) edge (§3) — there was no block that needed the wing
or strip enlarged to reach a reasonable placement.

## 2. Board facts used (measured on the live board, §2 of the brief cross-checked directly)

Right-edge/bottom-edge connector positions used to anchor every block (pcbnew query, not just the brief
table): J1 (223.66,91.34,F), J2 (223.69,91.55,B), J6 (223.60,106.50,F), J9 (223.60,106.56,B),
J11 (223.70,121.55,F), J13 (223.60,121.55,B), J14 (207.00,131.20, THT), J16 (222.50,71.00, THT),
J8 (206.75,137.53), J29 (197.72,137.60), J30 (188.75,137.53), J15 (215.75,137.53), J19 (213.10,130.10),
J20 (190.90,125.10), J7 (203.00,121.53), J10 (197.00,121.48), U6 (177.70,129.40,B; pad1 GND, pads 3-6
Deploy1_EN/Deploy1_EN/Heater_EN/Deploy2_EN), R104 pad1 (216.76,85.14, Deploy1_EN), R100 pad1
(172.50,129.91, Heater_EN).

## 3. Block placement and the attachment table (net → pad → block)

Every new-to-FC net is picked up at exactly one of the L11-allowed pads; the table gives the connector, the
block it feeds, and the straight-line centroid-to-pad distance (the L11 stub itself is still ≤14 mm inside
the flight section — this column is the *routed* distance across the extension, the thing "shortest
connections first" is actually about).

| Net(s) | Pad | Block (this JSON's zone) | Placement | Centroid→pad dist |
|---|---|---|---|---|
| `F1_SDA/SCL`, `F1_PWR`, `VSOLAR` | J1 pins 1-6 (F.Cu) | face_U313 (U313 + R340-344 + C313 + TP304) | wing west col, x244-261 y80-95 | 27.0 mm |
| `F2_SDA/SCL`, `F2_PWR`, `VSOLAR` | J2 pins 1-6 (B.Cu) | face_U314 (U314 + R350-354 + C314 + TP305) | wing west col, x244-261 y80-95 (paired row with U313) | 28.3 mm |
| `F0_SDA/SCL`, `F0_PWR`, `VSOLAR` (real Face-0 reference) | J6 pins 1-6 (F.Cu) | face0_real (U300-303, J300, R300-304, C300-304, TP300) | wing west col, x244-280 y97-125 | 26.0 mm |
| `F3(EMU_F5)_SDA/SCL`(*), `F5_PWR`, `VSOLAR` | J9 pins 1-6 (B.Cu) | face_U310 (U310 + R310-314 + C310 + TP301) | wing, x263-280 y97-110 (east of face0_real, same y-band) | 46.4 mm |
| `Fn_SDA/SCL`, `Fn_PWR`, `VSOLAR` | J11 pins 1-6 (F.Cu) | face_U311 (U311 + R320-324 + C311 + TP302) | wing west col, x244-261 y127-142 | 29.3 mm |
| `Fn_SDA/SCL`, `Fn_PWR`, `VSOLAR` | J13 pins 1-6 (B.Cu) | face_U312 (U312 + R330-334 + C312 + TP303) | wing west col, x244-261 y127-142 (paired row with U311) | 31.4 mm |
| `Dir_Chrg_In`, `B-`, `BATT_SDA/SCL`, `+3V3` | J14 (THT, any layer) | batt_core (U315+R360/362/363+C315, in the batt_replica zone) + batt_term (J500) | strip, x213-254 y144-172 | U315 cluster 31.6 mm (from §ext measurement in proposal-1 v1); J500 34.7 mm |
| `SDA_Top/SCL_Top`, `FC_RESET`, `USBBOOT`, `WDT_DISABLE`, `+3V3` | J16 (THT) | face_top (U316+R370-374+C316+TP306) + bench_drv (Q701-703+R705-710) | wing west col, x244-261 y64-78 / y50-63 | 28.4 mm / 34.5 mm |
| `VBATT_SENSE`,`INHIB_1` | J8 (∥ JP602) | pyro_diodes_sw block + JP602 header | strip, x156-205 y144-156 (block); JP602 at (206.75,~161) | 22.3 mm (JP602↔J8) |
| `INHIB_1`,`IN_RBF` | J29 (∥ JP603) | JP603 header | strip | 22.2 mm |
| `VBATT_SENSE`,`INHIB_2` | J7 (∥ JP604) | JP604 header | strip | 38.3 mm (J7 is 20.5 mm deep per L11; ≤24 mm stub band applies) |
| `INHIB_2`,`IN_RBF` | J10 (∥ JP605) | JP605 header | strip | 38.3 mm (same 24 mm-band pad) |
| `IN_RBF`,`VBUSP` | J20/J30 (∥ JP606) | JP606 header | strip | 34.7 mm |
| `B-`,`GND` | J15/J19 (∥ JP607) | JP607 header | strip | 29.7 mm |
| `Deploy1_EN` | R104 pad1 (F.Cu, 11 mm from the right edge) | pyro D600 (diode block) | strip, x156-205 y144-156 | — (EN taps land on the shared pyro rail; block itself sits west in the strip, directly under U6/J8/J29/J30 per L2) |
| `Heater_EN` | R100 pad1 (B.Cu, 12 mm from the bottom edge) *and* U6 pad5 | pyro block | strip | — |
| `Deploy2_EN` | U6 pad6 (B.Cu, 8-10 mm from the bottom edge — R103 itself is 35 mm deep and is *not* a tap per L11) | pyro block | strip | — |
| `VSOLAR` (bench injection) | J1/J2/J6/J9/J11/J13 pins 1-2, shared net | vsolar_AB (J400/F400/D400/JP400/TP400, J401/F401/D401/JP401/TP402, TP401) | wing, x263-296 y112-144 ("low on the wing" per L2) | 50.0 mm (centroid of J400/J401 to J6) |

(*) the exact FC-side face identity behind each of J1/J2/J6/J9/J11/J13's 6 pins is a routing-stage
question (the connectors are 6-pin and the board facts table does not resolve which of F1-F5 rides which
physical connector beyond the brief's own "U310-U314 opposite J9/J11/J13/J1/J2" mapping, which this
proposal follows literally); floorplan correctness here means "this front-end sits opposite this
connector", not a claim about which net name is on which pin.

**Layer note.** Every new footprint in this proposal is placed on **F.Cu** (matching how `board_sync`
staged all 218 parts). J1/J6/J11 face pads are F.Cu-side and J2/J9/J13 are B.Cu-side (top/bottom mounted
pairs at the same location); rather than flip the three B-side front-ends (U310/U312/U314) and risk
mirrored-offset placement errors at this stage (see §6), the stub's required layer-change via is left for
the routing stage — L11 permits a new via anywhere inside the new area (only vias *inside the old Rev2
outline* are forbidden), so this costs one extra via per B-side face net, not a rule violation.

## 4. Lanes and keepouts (brief §2, L3)

`floorplan_proposal_1.json`'s `lanes` array reserves the 12 mm-wide strip directly in front of
J1/J2, J6/J9, J11/J13, J16 and J12/J22 (x231.39–243.39 at each connector's y-band); every west-column block
starts at x=244, 0.6 mm clear of that boundary. `keepouts` documents the RF (U13→RF1) and U30 antenna
keep-outs and why neither is reachable from the new area (U13/RF1 sit at old x155–194, the wing starts at
x231.39; U30's outline bottom edge is at y105.1, the nearest new copper — the strip — starts at y142.12,
>37 mm clear).

## 5. Ground, stitching, mounting holes

Unmodified from `outline_L1.json`: In1 GND plane grown to the new bbox; F.Cu/B.Cu GND pours on the wing
(priority 1) and strip (priority 2); heritage zones clipped to the Rev2 outline inset 0.2 mm; 3 new M3
holes (H10 at 292.39,51.58; H11 at 292.39,168.12; H12 at 147.3,168.12). `floorplan_proposal_1.json` adds a
**stitching-via suggestion** (not authoritative — stage 3 "Outline + ground" owns the final stitching
pass): 37 points at ≤9 mm pitch, 3 mm inset from the new perimeter (skipping anything within 6.5 mm of a
mounting hole), plus a 5-point ring around the emulator core block. This is offered as a starting point for
stage 3, not a claim that it is complete or DRC-verified for via-to-pad clearance against the final
placement.

## 6. Validation run (board copy, this proposal's placement applied)

Pipeline: `outline.py --spec outline_L1.json` → `apply_placement.py --placement floorplan_proposal_1.json`
→ `heritage.py check --allow-zone-growth --allow-edge` → `attachment_check.py` → a custom courtyard/hole
geometry pass (§6.1, written because the canonical `kicad-cli` DRC command proved too slow to iterate on —
see §6.2) → `kicad-cli pcb drc --severity-all --all-track-errors --schematic-parity --refill-zones` →
`drc_summary.py` → `render.sh` → read top.pdf/bottom.pdf. Final board: `board4_placed.kicad_pcb` (three
placement iterations; §6.1 explains what the second and third caught).

* **apply_placement.py**: `applied 218; refused (heritage) []; missing refs []`. **Footprints not fully
  inside the outline: 8** — `H10, H11, H12, J21, J24, J4, U13, U30`. **All 8 are pre-existing, not
  introduced by this proposal**: re-running the identical check against `board1_outline.kicad_pcb`
  (`outline.py`'s own output, *before any of this proposal's 218 placements are applied*) reports the exact
  same 8 refs. H10-H12 are the new corner mounting holes whose round pad legitimately sits close to the
  new outline's filleted corners; J21/J24/J4/U13/U30 are heritage footprints this proposal never touches
  (`apply_placement.py` refuses non-`--allow-heritage` moves) — their bounding-box corners fall outside the
  new outline polygon only because the check tests all 4 AABB corners against a non-convex (notched)
  outline, a known limitation of that check, not a placement defect. **0 of the 218 new parts are outside
  the outline.**
* **heritage.py check --allow-zone-growth --allow-edge**: **4 violations**, all zone-fill-area deltas
  inside the Rev2 outline: two unnamed F.Cu zones (33.5→28.0 mm², 32.5→26.3 mm²), `GND` on In1.Cu
  (6409.2→6397.2 mm², 0.19%), `+3V3` on In2.Cu (5434.3→5422.3 mm², 0.22%). **Root-caused as a pre-existing
  defect in `outline.py`'s zone-clip step (the `clip_heritage_zones_to`/`clip_inset_mm` mechanism), not
  attributable to this proposal**: the identical 4 violations, with the identical mm² numbers, reproduce on
  `board1_outline.kicad_pcb` — i.e. running only `outline.py` on the synced board with the default
  `outline_L1.json`, before any of this proposal's placements are applied. Confirmed on three independently
  regenerated placement attempts (board2/board3/board4), byte-identical numbers every time. This should be
  reported to the PM/outline-tool owner; it is not something a floorplan JSON can fix.
* **attachment_check.py**: `0 new tracks/vias, 0 stub chain(s) into the flight section, 0 warning(s)` — as
  expected at the floorplan stage (no routing yet). **4 violations**, byte-identical to the heritage.py
  ones above (same zone-fill-area mechanism) — same root cause, same conclusion.
* **kicad-cli DRC / drc_summary.py**: see §6.2 for `check_results`.
* **render.sh + top.pdf/bottom.pdf read**: whole board fits legibly inside the plotted page (296.44 mm
  board width vs. 297 mm A4-landscape frame — a coincidence, not by design; the "set page to A3" step
  mentioned in `outline.py`'s docstring belongs to the build stage, and this KiCad 10 Python build does not
  expose `pcbnew.PAGE_INFO` to script a page-size change here). Visual read of top.pdf: the six-face column
  (U313/U314, face0_real, U310, U311/U312) reads as a clean run down the west edge, mirroring the run of
  J1/J2→J6/J9→J11/J13 down the old edge; bench I/O (J701/J702/SW701-703/J703) sits top-right for cable
  access; the emulator core sits in its own pocket top-right; VSOLAR injection (J400/J401) sits mid-wing,
  east; the bottom strip shows pyro/jumpers (west) → battery replica + BATT face channel (centre, under
  J14) → BQ25886 charger + J510 (east), matching L2's left-to-right instruction. No part visibly overlaps
  another on the render.

### 6.1 Courtyard/hole geometry pass — two real defects caught and fixed

The canonical `kicad-cli pcb drc --schematic-parity --refill-zones ...` command took over 10 minutes per
run on this board even in isolation, and this task ran with two other floorplan-proposer agents doing the
same thing concurrently on the same machine, making iteration on it impractical. Wrote a standalone
pcbnew-script check (`courtyard_check.py`) that computes each new footprint's `F.CrtYd` polygon directly
(`FOOTPRINT.GraphicalItems()` filtered to the courtyard layer, `TransformShapeToPolygon` +
`SHAPE_POLY_SET.BooleanIntersection`) and pairwise-tests all 218 new footprints plus every heritage
footprint whose bounding box lies near the seam (x>240mm) — the same geometry kicad-cli's own
courtyard-overlap check uses, without the full connectivity/zone-fill DRC pass. Ran in a few seconds.
**First run (on the placement described in §3 before this fix) found 3 real defects**, none visible at
render resolution:

1. `JP607`↔`J500` courtyard overlap (~4×4 mm) — the ISS shunt header (JP607, paralleling J15/J19) and the
   battery-replica screw terminal J500 both wanted the same x213-222 pocket at the strip's bottom edge.
2. `JP605`↔`JP603` courtyard overlap (~4×4 mm) — their target x-positions (the connectors they parallel,
   J10 at x=197.0 and J29 at x=197.72) are 0.72 mm apart, closer than the 3.59 mm header body.
3. `U200`↔`H10` bounding-box overlap — the emulator-core zone's top-left corner sat directly on mounting
   hole H10 (292.39, 51.58).

Fixed by: (1) enforcing a 5.5 mm minimum pitch across the six JP602-607 targets (sorted by x, each pushed
right of the previous by at least 5.5 mm) rather than placing each independently at its own connector's raw
x — `JP603`/`JP604`/`JP602`/`JP607` moved 2.5-4.8 mm off their ideal x as a result, still each within a few
mm of the connector they parallel; (2) moving `batt_term` (J500) east, out from under the header row, to
x230-255 (still "under J14" in spirit — J14 is at x=207, the strip's screw-terminal edge is only 30 mm deep
so *something* east-west compromise was always going to be needed once six headers and a 16×11 mm terminal
both wanted the same 75 mm-wide pocket); (3) raising `emu_core`'s zone to start at y=58 (H10's pad + its
courtyard clearance ends before that). **Re-ran the checker after the fix: 0 courtyard-overlap pairs among
the 218 new footprints, 0 new-vs-heritage bounding-box overlaps.** Also wrote and ran a targeted
mounting-hole proximity check (`hole_check.py`) against H10/H11/H12: 0 new footprints within 4 mm of any of
the three. `floorplan_proposal_1.json` and this report reflect the fixed placement (`board4_placed.kicad_pcb`).

### 6.2 `kicad-cli` DRC — canonical command, attempted, did not finish inside this session

```
kicad-cli pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones \
    --output drc4.json board4_placed.kicad_pcb
```

Run four times across this task (against board2/board3/board4 as the placement was iterated) and never
completed inside this session's time budget: this board (3271+ heritage tracks/vias, 45 zones including the
full-board In1 GND plane, now 218 more footprints) takes the full-featured DRC command
(`--schematic-parity --refill-zones --all-track-errors`) past 10 minutes even alone, and this task ran with
**two other floorplan-proposer agents running the identical command concurrently on the same machine** —
confirmed via `ps`, 3-6 simultaneous `kicad-cli pcb drc` processes at 99-100% CPU each for the whole
session. A control run with `--schematic-parity`/`--refill-zones`/`--all-track-errors` all dropped (just
`--severity-all`) also exceeded 3 minutes, showing the slowness is the board's size under contention, not
any one flag. `--schematic-parity` additionally logs `Failed to fetch schematic netlist for parity tests`
against every scratch-copy board in this task (the copies live outside the project's normal
`FlatSat_V1.kicad_pro`/`.kicad_sch` pair, which `kicad-cli` looks for by sibling naming) — harmless (parity
is simply skipped, per the empty `schematic_parity` section in every DRC JSON this task's other checks
produced) but worth the integrator knowing about if they see the same message.

**What stands in for it in this hand-back**: §6.1's from-scratch courtyard/hole geometry pass (the specific
thing this stage's DRC requirement cares about — "courtyard overlaps must be 0 among new parts; parts
outside outline 0" — computed directly from the same `SHAPE_POLY_SET`/`F.CrtYd` machinery kicad-cli's own
courtyard check uses, in seconds instead of minutes) plus `heritage.py`/`attachment_check.py` (which already
run a full zone-fill-area diff over the whole board and would catch a clearance-relevant zone regression).
**Recommend the Opus judge or the stage-3 owner re-run the canonical `kicad-cli` command once on an
uncontended machine** as the authoritative full DRC pass (clearances, hole-to-hole, silkscreen-over-courtyard
etc. beyond what §6.1's targeted script checks) before this proposal — or whatever the judge synthesizes
from it — is handed to stage 3.

## 7. Known risks / open items for the judge

1. **The 4 heritage/attachment zone-fill violations are a shared-tool defect** (outline.py's Rev2-zone
   clipping), reproduced identically with zero placements applied. Every proposal using the default
   `outline_L1.json` will show the same 4 violations. Recommend the PM/stage-3 owner investigate
   `outline.py`'s `clip_heritage_zones_to` step (possibly a zone-fill refill ordering issue, or the
   validated baseline was measured against a different KiCad point version) rather than treat it as a
   floorplan defect to fix per-proposal.
2. **face_U310's 46.4 mm and vsolar_AB's 50.0 mm are the two longest routed distances** in this proposal.
   Both are geometrically constrained: J9 (U310's connector) shares its y-band with J6 (Face-0's
   connector, already the anchor for the larger 16-part face0_real cluster), so U310 was pushed one column
   east rather than displacing face0_real; VSOLAR's two screw terminals (11.22×11.12 mm each, plus
   fuse/diode/jumper/TP) do not fit in the 12 mm lane-respecting west column alongside five other blocks,
   so they sit further out on the east side, still "low on the wing" per L2. A different proposal that
   gives the west column more width (at the cost of the 12 mm L3 lane margin, or by widening the wing
   under the brief's ±15 mm allowance) could likely shave 15-20 mm off both.
3. **All new ICs are on F.Cu** (see §3 layer note) — the three connectors with B-side pads (J2, J9, J13)
   therefore need one layer-change via each in the extension for their stub to reach a B.Cu pad on the
   matching connector's side, OR the routing stage flips U310/U312/U314 (and their support passives) to
   B.Cu directly. Either is compliant with L11 (via inside the new area only); flagged so stage 3/4 doesn't
   have to rediscover it.
4. **Stitching-via points are a starting suggestion, not a final pass** (§5) — stage 3 "Outline + ground"
   should treat `floorplan_proposal_1.json`'s `stitching.points` as a proposal, re-verify clearance to the
   final GND pour and to every footprint pad, and add points around the emulator/charger switching nodes
   that a real ground-bounce analysis would want.
5. Per-part rotation was kept at each part's own **staged rotation** (0° or 180°, whatever `board_sync`
   assigned) rather than re-oriented for pin-1/cable-entry conventions (e.g. screw terminals facing the
   board edge). This is a layout-polish item for stage 6 (silkscreen) or an early pass in stage 3, not a
   floorplan-blocking issue.
