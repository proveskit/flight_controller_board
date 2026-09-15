# Detailed placement — `strip_left_pyro_shunts` (2026-09-14, stage 2b)

**Refs (20):** D600, D601, D602, JP600, JP601, JP602, JP603, JP604, JP605, JP606, JP607, LED600,
R600, R601, R602, SW600, TP600, TP601, TP602, TP603
**Sheet:** `pyro_inhibit` (`FlatSat_V1/pyro_inhibit.kicad_sch`) · **Envelope:** x 150.5–220.7, y 142.8–161.9 mm
**Fixed anchors (0 mm / 0° move):** JP600–JP607, SW600
**v1 reference:** `floorplan.json` (positions), `floorplan.md` §1 block map row "pyro EN diodes / SAFE
switch" + "shunt headers JP602–607", §3, §5 (attachment map)

## 0. What's actually in this block

This block has **no supported IC** — it is the bench pyro-inhibit ladder plus RBF/shunt jumpers.
Every part is a discrete: 3 small-signal Schottky diodes, 8 fixed 2-pin jumper headers, 1 SPDT slide
switch (used as SPST), 1 LED, 3 resistors, 4 test points. There is consequently no decoupling, no
bootstrap, no feedback divider, no crystal, no QSPI — the "IC-guideline" categories in the brief do
not apply here. What *does* apply is generic good-practice placement for signal-clamp diodes,
indicator LEDs and bench test points, which is what the checklist below documents, with an explicit
fallback note per part per the brief's own fallback instruction.

| Ref | Function | What it does |
|---|---|---|
| D600 | BAT54W Schottky (1 of 3 diodes in the pack) | Anode on `Deploy1_EN`, cathode commoned on `PYRO_INH_COM` — force-lows the channel when the switch/JP601 grounds the common rail |
| D601 | BAT54W Schottky | Anode on `Net-(D601-A)`, fed from `Heater_EN` through the JP600 shunt; cathode on `PYRO_INH_COM` |
| D602 | BAT54W Schottky | Anode on `Deploy2_EN`, cathode on `PYRO_INH_COM` |
| JP600 | 2-pin header (fixed) | In series in the `Heater_EN` leg, ahead of D601 — pull to exclude the heater channel from the inhibit without a respin |
| JP601 | 2-pin header (fixed) | `PYRO_INH_COM` ↔ `GND`, parallel to SW600, for an external panel switch |
| JP602–607 | 2-pin headers (fixed) | RBF/inhibit-chain shunts, each in parallel with an existing FC connector break point (J8/J29/J7/J10/J20-J30/J15-J19) |
| LED600 | White 0603 LED | SAFE indicator — lights from `3V3_EMU` through R602 when `PYRO_INH_COM` is grounded (switch closed) |
| R600 | 4.7 k pull-up | `PYRO_INH_COM` → FC `+3V3` (review fix #2) — armed-state level independent of emulator power |
| R601 | 4.7 k sense | `PYRO_INH_COM` → `PYRO_INHIBIT_STATE` (RP2350 GPIO read, ≤8.2 kΩ per erratum E9) |
| R602 | 470 Ω LED series R | `3V3_EMU` → R602 → LED600 anode → `PYRO_INH_COM` |
| SW600 | MSK12C02 slide switch (fixed) | `PYRO_INH_COM` ↔ `GND`, closed = INHIBIT/SAFE |
| TP600–603 | Bench test points | `Deploy1_EN`, `Heater_EN`, `Deploy2_EN`, `PYRO_INH_COM` respectively |

## 1. Guideline checklist

Sources checked and fetched this pass: Nexperia `BAT54W_SER.pdf` (Rev 3, 20-Nov-2012, full 11
pages read) and the SHOU-HAN `MSK12C02` mechanical/spec PDF (`2304140030_..._C431540.pdf`, 5 pages,
via the LCSC CDN mirror — the `www.lcsc.com/datasheet/...` front-end URL bot-checks and does not
serve the PDF, confirmed same issue the sheet doc already recorded). **Neither datasheet has a PCB
layout / application-circuit section** — BAT54W_SER is a 3-page electrical+package spec with no
"Layout considerations" heading; MSK12C02's only placement-relevant line is §8.1 "follow the
recommended P.W.B. piercing plan in outside drawing" (i.e. just its own footprint, already the
KiCad-standard `SW_SPDT_Shouhan_MSK12C02` used on the sheet). **Fallback applied** for every row
below to the generic guideline named in the brief's MANUFACTURER GUIDELINES section (short loop /
shortest return, edge-reachable test points, adjacent series-R/LED) — noted per row.

| # | Rule | Source | Criterion | Measured (placed board) | Pass/Fail |
|---|---|---|---|---|---|
| 1 | BAT54W clamp diode: anode faces the EN-net side it clamps, cathode faces the common-rail direction it commons into (short loop, no guideline section — fallback: standard signal-diode placement practice) | `BAT54W_SER.pdf` §1.3 Applications ("voltage clamping"); no layout section — fallback | Anode pad y < cathode pad y is wrong test; real test: anode pad on the north side of the footprint (toward the flight-section boundary at y=142.1, the direction every EN net enters from) | D600/601/602 anode (pin1) at y=151.685, 0.65 mm **north** of body centre (152.335); cathode (pin3) at body-centre y, offset **east** (+0.887 mm), continuing the common rail into the next diode in the chain (D600→D601→D602, monotonic +x) | **PASS** (rot=0, unchanged from v1 — already correct, confirmed by pad-geometry inspection, not just carried over) |
| 2 | BAT54W-to-BAT54W and diode-to-test-point courtyard spacing ≥ 0.5 mm (constraint h) | Brief placement constraint (h) | courtyard gap ≥ 0.5 mm | TP600→TP601→TP602→TP603→D600→D601→D602: **0.957–0.960 mm** every gap | **PASS** |
| 3 | LED indicator: series resistor immediately adjacent to the LED, short loop (no manufacturer layout section for KT-0603W beyond its footprint — fallback: generic indicator-LED placement practice) | KT-0603W datasheet (LCSC C2290, cited in the sheet doc) has no layout section — fallback | R602–LED600 pad-to-pad loop as short as the row allows | **v1: 7.99 mm** (R600, R601 physically sat between LED600 and R602) → **placed: 2.18 mm** (R602 moved to the slot adjacent to LED600; R600/R601 shifted one slot east, still adjacent to each other and to the common rail/SW600/JP601 cluster) | **PASS** (v1 would have **FAILED** this row — see §3 below) |
| 4 | Pull-up (R600) / sense (R601) resistor: short stub to the `PYRO_INH_COM` node they tap (fallback: generic pull-up/sense placement, no formal criterion in either resistor's datasheet — these are generic 0402s) | Fallback (generic) | Pad-to-node distance stays short (single-digit mm) inside this small envelope | R600.1→SW600.2 6.92 mm; R601.1→SW600.2 8.31 mm; JP601.1→SW600.2 6.38 mm (all within the 70×19 mm envelope, no long detour) | **PASS** |
| 5 | Test points at a reachable block location, unobstructed by any taller part directly overhead (a probe approaches from above) | Brief §(g): "test points go where a probe can reach"; sheet doc §2 (TP600–603 on the three EN nets + `PYRO_INH_COM`) | No footprint's bounding box overlaps a TP's bounding box in x when projected — i.e. nothing sits directly over/under a TP | JP600/601 courtyard bottom 150.16 mm, TP600–603 courtyard top 151.119 mm → 0.959 mm clear; D600–602 sit immediately east of the TP row at the same y, 0.960 mm gap, no x-overlap with any JP | **PASS** (unchanged from v1 — already correct) |
| 6 | SW600 / LED600 reachable by a hand/finger, not boxed in (brief §(g)) | Brief placement constraint (g) | Sits at/near a block edge with ≥1 mm clearance to neighbours, not enclosed on more than 2 sides by taller parts | LED600 west edge at x=152.00, 1.5 mm from the envelope's west boundary (150.5); SW600 (fixed) at the block's south-west quadrant, 0.96 mm clear of the LED/R row to its south, clear on its west (152.00 vs envelope 150.5) | **PASS** |
| 7 | 12.6 mm F.Cu lane (x 231.4–244) stays clear of parts > 2 mm tall | Brief / floorplan.md ruling F-lane | This block's envelope (x ≤ 220.7) does not reach the lane | N/A — 10.7 mm clear margin, no part of this block is anywhere near x 231.4 | **N/A / PASS** |
| 8 | Heritage frozen; no new part inside the Rev2 outline | Brief (f); `heritage.py` | 0 violations | `heritage.py check … --allow-zone-growth --allow-edge` → **0 violations** (all 9 fixed anchors bit-for-bit unchanged, verified directly — see §4) | **PASS** |
| 9 | No courtyard overlap with any part of any block; nothing outside the outline | Brief (d); `apply_placement.py` | 0/0 | `apply_placement.py` → **outside: 0, courtyard overlaps: 0** | **PASS** |
| 10 | Attachment reach for this block's 3 shared nets must not worsen by > 3 mm | Brief (c) / L11 / floorplan.md §5 | Δreach ≤ 3 mm | Deploy1_EN 19.45→19.45 mm (Δ0.00); Heater_EN 22.85→22.85 mm (Δ0.00); Deploy2_EN 22.49→22.49 mm (Δ0.00) — the 3 attachment pads (D600.1, TP601.1, TP602.1) were not moved | **PASS** |
| 11 | Rotations chosen so pins face the pins they connect to (brief g) | Brief (g) | Qualitative + pad-geometry check | Diodes: see row 1. R600/R601/R602/LED600: all rot=0, all three resistors + LED body axis in line with the row (pad-1/pad-2 east-west), matching the rail's own east-west run | **PASS** |

**Rules checked: 11. Rules failed: 0.**

## 2. Placement rationale, part by part

- **D600, D601, D602 — unchanged from v1 (177.625/181.575/185.525, 152.335, rot 0, F.Cu).**
  Inspecting the actual SOT-323 pad geometry (not just the symbol) showed the v1 rotation is already
  correct: pin 1 (anode) sits 0.65 mm north of the body centre — the side facing the flight-section
  boundary every EN net arrives from — and pin 3 (cathode) sits 0.887 mm east, continuing the
  commoned `PYRO_INH_COM` rail into the next diode in the D600→D601→D602 chain. Re-deriving this
  from pad coordinates (rather than trusting the inherited rotation) was the actual check; no change
  was warranted.
- **R602 moved from (162.825,158.635) to (157.005,158.635)** — the v1 slot adjacent to LED600. This
  is the one real defect this pass found: R602 (the LED's own series resistor) sat at the *far* end
  of the R600/R601/R602 row, 7.99 mm from LED600 across two unrelated resistors, when it belongs
  immediately next to the part it drives. Since R600/R601/R602 are identical 0402 footprints on the
  same three-slot row, they were simply re-assigned among their own three slots — no new spacing,
  no envelope change, no new overlap risk.
- **R600 moved from (157.005,158.635) to (159.915,158.635)** (the old R601 slot) and **R601 moved
  from (159.915,158.635) to (162.825,158.635)** (the old R602 slot) — the other two legs of the same
  three-way permutation. Both stay in the tight cluster next to SW600/JP601 (6.4–8.3 mm), where the
  `PYRO_INH_COM` node they tap already sits; neither is a nailed-down attachment pad (§5's reach
  table uses D600.1/TP601.1/TP602.1 for this block, not R600/R601), so this move has zero attachment
  consequence.
- **LED600 — unchanged (153.545,158.935).** Already at the block's west edge (1.5 mm inboard of the
  envelope boundary), the correct place for a hand/eye-reachable SAFE indicator; only its series
  resistor needed to move to it, not the other way around.
- **TP600–603 — unchanged (163.225/166.775/170.325/173.875, 152.415).** Already sit in the open gap
  between the JP600/601 row and the D600–602 row with no footprint of any height directly over or
  under them (0.96 mm clear top and bottom, no x-overlap with any header) — already correct for
  "probe reaches from above."
- **JP600–JP607, SW600 — fixed anchors, 0 mm / 0° move, confirmed bit-for-bit unchanged** (verified
  by direct position/rotation/flip comparison against the v1 preview board, §4).

## 3. Deviation found and fixed (not a rule failure — the thing this pass exists to catch)

v1 had R600 and R601 sitting physically between LED600 and R602 on the same row, so the
LED-series-resistor loop (`Net-(LED600-A)`, LED600 pin 2 to R602 pin 1) ran 7.99 mm across two
unrelated nets' resistors instead of directly to its neighbour. That is exactly the class of defect
the owner's ruling was aimed at (a support passive not placed by what it's actually wired to). Fixed
by permuting R600/R601/R602 among their own three interchangeable slots — R602 next to LED600, loop
down to 2.18 mm — with no other geometry disturbed. No rule in the table above was left failing;
this row (row 3) is recorded here because it's the one substantive change this pass made, not a
forced deviation.

No other deviation was needed and no anchor IC exists in this block to report a move for.

## 4. Attachment-reach effect (brief L11 / floorplan.md §5)

| Net | FC pad | This block's reach pad | v1 distance | Placed distance | Δ |
|---|---|---|---|---|---|
| `Deploy1_EN` | U6.3 | D600.1 | 19.45 mm | 19.45 mm | 0.00 mm |
| `Heater_EN` | U6.5 | TP601.1 | 22.85 mm | 22.85 mm | 0.00 mm |
| `Deploy2_EN` | U6.6 | TP602.1 | 22.49 mm | 22.49 mm | 0.00 mm |

All three reach pads (D600, TP601, TP602) were left at their v1 positions — zero change, well inside
the ≤3 mm allowance. (`R104.1`/`R100.1` remain available alternates per floorplan.md §5, unaffected
either way.)

## 5. Commands run

```
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
SCRATCH=/private/tmp/claude-501/.../scratchpad/detail_strip_left_pyro_shunts
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# scratch copies (never touch the live board or FC_V5e_Production_Rev2/)
cp docs/../2026-09-14_phase2_layout/floorplan_preview.kicad_pcb{,.kicad_pro,.kicad_dru,.kicad_prl} $SCRATCH/
cp FlatSat_V1.kicad_pcb FlatSat_V1.kicad_pro FlatSat_V1.kicad_dru FlatSat_V1.kicad_prl $SCRATCH/

# merge this block's placement into a copy of the floorplan of record
python3 - <<'PY'   # merges placement_strip_left_pyro_shunts.json into a copy of floorplan.json
PY

# rebuild from scratch and gate
$KPY tools/pcb/outline.py --board $SCRATCH/FlatSat_V1.kicad_pcb --out $SCRATCH/outlined.kicad_pcb \
    --spec $SCRATCH/merged_floorplan.json
$KPY tools/pcb/apply_placement.py --board $SCRATCH/outlined.kicad_pcb \
    --placement $SCRATCH/merged_floorplan.json --out $SCRATCH/placed.kicad_pcb
$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json $SCRATCH/placed.kicad_pcb \
    --allow-zone-growth --allow-edge
$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json $SCRATCH/placed.kicad_pcb
```

Results: `outline.py` → outline/pours/holes/stitching rebuilt (bbox 143.29..296.44 / 47.51..172.17,
matching v1 exactly). `apply_placement.py` → `applied 218; refused (heritage) []; missing refs []`,
**outside: 0, courtyard overlaps: 0**, exit 0. `heritage.py check` → **0 violations** (all zone/edge
notes are the expected outline-growth deltas already accepted in v1; the 9 fixed anchors verified
bit-for-bit unchanged by direct position/rotation/flip comparison). `attachment_check.py` → **65 new
tracks/vias (the stitching set), 0 stub chains into the flight section, 0 violations, 0 warnings.**

## 6. Files

- `docs/flatsat/2026-09-14_phase2_layout/detail/placement_strip_left_pyro_shunts.json` — this
  block's 20 refs, `{ref:{x,y,rot,side}}`.
- Scratch (never committed, never the live board): merged floorplan, outlined/placed board copies,
  under `/private/tmp/claude-501/.../scratchpad/detail_strip_left_pyro_shunts/`.
