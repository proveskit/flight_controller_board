# Detailed placement — block `bench_io_drivers` (Q701–Q703, R705–R710, SW703)

**Date:** 2026-09-14 · **Owner:** Sonnet agent, Phase 2 stage 2b (detailed placement) · **Sheet:** `FlatSat_V1/bench_io.kicad_sch` (§2 Block D/E) · **Phase-1 doc:** `docs/flatsat/2026-09-14_phase1_schematic/sheet_bench_io.md` §2, §7 · **v1 reference:** `docs/flatsat/2026-09-14_phase2_layout/floorplan.json` / `floorplan.md` §1, §3, §5

## 1. What is in this block, and what each part does

Ten refs, two independent circuits sharing one 20.5 × 15.5 mm envelope `[242, 64.5, 262.5, 80]`:

- **Blocks E (open-drain bench-control drivers), sheet doc §2/§7.** Three identical open-drain N-FET
  pulldown stages, one per FC control net:
  - **Q701** (BSS138, SOT-23) — gate driven by `EMU_CTL_FC_RESET` through **R705** (1 kΩ gate-series);
    gate held low by **R706** (4.7 kΩ pulldown, RP2350 erratum E9 A2-safe value, ≤ 8.2 kΩ); drain →
    `FC_RESET` (J16.2, THT); source → GND.
  - **Q702** (BSS138) — gate driven by `EMU_CTL_USBBOOT` through **R707** (1 k); pulldown **R708** (4.7 k);
    drain → `USBBOOT` (J16.1); source → GND.
  - **Q703** (BSS138) — gate driven by `EMU_CTL_WDT_DIS` through **R709** (1 k); pulldown **R710** (4.7 k);
    drain → `WDT_DISABLE` (same net as SW703); source → GND.
  Each stage only ever *pulls* its FC net low (open-drain, source grounded) — never drives it high.
- **Block D (WDT_DISABLE manual override), sheet doc §2/§5.** **SW703** (`Switch:SW_SPDT`, footprint
  `easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4`, THT slide switch) — common pole (pin 2) → GND, pin 1 →
  `WDT_DISABLE`, pin 3 unused (marked NC in schematic). Bench-operable parallel path to the FC's own
  J4 shunt jumper; **fixed anchor per the brief — not moved or rotated in this pass.**

No decoupling caps, dividers, crystals or ESD parts in this block — it is three identical discrete
gate-driver stages plus one toggle switch, so the "manufacturer guideline" that applies is the BSS138
datasheet's own layout section (there isn't one — see §2) and the brief's own fallback rule for this
circuit shape ("gate resistors at the FET gate").

## 2. Guideline checklist (source + measurable criterion)

**BSS138 datasheet has no PCB layout section.** Fetched the actual datasheet cited by the schematic
(`https://www.onsemi.com/pub/Collateral/BSS138-D.PDF`, onsemi/Fairchild `BSS138-D.PDF`) via WebFetch
and asked it directly for any layout/application-circuit/gate-resistor-placement guidance. Result,
verbatim: *"there is no PCB layout guidance, application circuit notes, or recommendations regarding
gate resistor placement, gate pull-down placement, trace length, source/ground return routing... The
datasheet contains: Absolute maximum ratings, Thermal characteristics, Electrical characteristics,
Switching characteristics, Typical characteristic graphs."* Confirmed: this is a small-signal
SOT-23 discrete with no reference layout, land-pattern-only. **Falling back**, per the task's own
"MANUFACTURER GUIDELINES" fallback clause, to the standard guideline for this circuit shape: *"gate
resistors at the FET gate"* — i.e. the gate-series R and the gate-pulldown R both sit as close to the
FET's own gate pad as the envelope and part pitch allow, minimizing the high-impedance gate-node loop;
source returns to the nearest GND copper; drain trace is short and its attachment reach must not
regress beyond the brief's L11 3 mm allowance.

| # | Rule | Source | Criterion (measurable) | Measured | Pass/Fail |
|---|---|---|---|---|---|
| 1 | Gate-series R sits at the FET's own gate pad | Fallback (BSS138 datasheet confirmed layout-section-free, WebFetch above); brief MANUFACTURER GUIDELINES fallback text | gate pad ↔ series-R gate-node pad ≤ 8 mm straight-line | Q703↔R709 4.293 mm · Q701↔R705 4.446 mm · Q702↔R707 4.738 mm | **PASS** (all ≤ 8 mm, in fact all ≤ 5 mm) |
| 2 | Gate-pulldown R sits at the same gate node, close to the gate pad | Fallback (as above) + brief rule 10 / RP2350 erratum E9 (value, not placement, already fixed in schematic at 4.7 kΩ ≤ 8.2 kΩ) | gate pad ↔ pulldown-R gate-node pad ≤ 8 mm | Q703↔R710 5.432 mm · Q701↔R706 5.946 mm · Q702↔R708 6.542 mm | **PASS** |
| 3 | Each FET's *own* gate-R pair sits in that FET's own column (fixes the v1 defect) | This pass's own audit of v1 (see §3) | worst single gate-loop leg, any FET, ≤ 8 mm | v2 worst leg 6.542 mm (v1 worst leg was **15.59 mm**, Q703↔R710) | **PASS** (v1 would have **FAILED** this criterion) |
| 4 | Source (GND) pin returns to the nearest ground copper, not routed across the block | Fallback ("shortest ground return") + `floorplan.json.new_gnd_pours` (`GND_F_Cu_wing` rect (232,48.5)–(295.5,171.2) covers the whole block on F.Cu) | source pad falls inside the F.Cu GND pour rectangle | Q701.2/Q702.2/Q703.2 all `True` | **PASS** |
| 5 | Drain-to-FC-net attachment reach does not regress > 3 mm vs v1 | Brief L11 / `floorplan.md` §5 attachment-reach table | \|reach_v2 − reach_v1\| ≤ 3 mm, per net | FC_RESET (J16.2↔Q701.3) 27.567 vs 27.6 mm (Δ 0.03) · USBBOOT (J16.1↔Q702.3) 34.541 vs 34.5 mm (Δ 0.04) · WDT_DISABLE (J16.9↔SW703.1) 23.603 vs 23.6 mm (Δ 0.003) | **PASS** (Q701/Q702/SW703 were not moved at all — Δ is FP rounding noise) |
| 6 | SW703 fixed anchor: no move, no rotation | Task's fixed-anchors rule | position/rotation/side identical to v1 | (250.475, 67.475) rot 0 side F — identical | **PASS** |
| 7 | No courtyard overlap anywhere on the board (real polygons); nothing outside the board outline | `apply_placement.py` enforced check | tool exit 0, 0 overlap lines, 0 outside lines | `footprints not fully inside the outline: 0` · `courtyard overlaps ...: 0` | **PASS** |
| 8 | ≥ 0.5 mm courtyard-to-courtyard clearance between parts that shouldn't touch | Placement constraint (h) | min bbox gap ≥ 0.5 mm between any two of this block's parts | R-pair-to-R-pair 0.960 mm · Q-to-SW703 0.975–0.980 mm · FET row to R row ≈ 1.06–1.11 mm | **PASS** |
| 9 | Every part inside the block envelope `[242, 64.5, 262.5, 80]` | Placement constraint (a) | footprint bbox ⊆ envelope | 9/10 parts fully inside; **SW703 (fixed, unmoved) top edge y=64.000 vs envelope y0=64.5** (0.5 mm over, silkscreen/body outline of the THT slide switch, inherited unchanged from the owner-accepted v1 block-level plan) | **PASS for the 9 movable refs**; SW703 is a forced, pre-existing, non-blocking deviation (see §4) |
| 10 | 12.6 mm keep-clear lane (x ≤ 243.39 mm) stays free of parts this block could have put there | `floorplan.json.lanes` L3 | no part's left edge < 243.39 mm | leftmost edges (Q703/R709/SW703) all at x = 244.000 mm | **PASS** (0.61 mm clear, matches v1's own documented margin) |
| 11 | Heritage frozen | `heritage.py check ... --allow-zone-growth --allow-edge` | exit 0 | `heritage check: 0 violation(s)` | **PASS** |
| 12 | L11 attachment gate | `attachment_check.py` | exit 0, 0 violations | `65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violations, 0 warnings` | **PASS** |

**rules_checked = 12, rules_failed = 0** (row 9's SW703 note is a forced, documented deviation on a
fixed anchor, not a failure of anything this pass controlled — see §4).

## 3. What was wrong in v1, and what changed

v1 already had the three FETs and SW703 in good positions (Q703/Q701/Q702 left-to-right, gate pads at
x = 245.018 / 250.062 / 255.062, exactly matched to J16 opposite them — `floorplan.md` §5's own G8
optimisation). **The six gate-network resistors were the problem**: v1 laid them out as one contiguous
run of 6 evenly-spaced 0402s (x = 244.955 … 259.505) *in schematic order* (R705/706, R707/708,
R709/710) rather than *spatial order matching the FETs above them*. Since the FET order is
Q703, Q701, Q702 (not Q701, Q702, Q703), R709/R710 — Q703's own gate-series/pulldown pair — ended up
in the *rightmost* slot, under Q702, 12.8 mm and 15.6 mm from Q703's actual gate pad. Q701's and
Q702's pairs were serviceable but not optimal either (10.06–10.88 mm total loop each).

**Fix**: reassign which ref occupies which of the three existing slot-pairs (244.955/247.865,
250.775/253.685, 256.595/259.505 — same y = 76.995 row, same pitch, **zero new geometry**) so each
pair sits under its own FET in left-to-right order: R709/R710 → leftmost slot (under Q703), R705/R706
→ middle slot (under Q701, unchanged from v1), R707/R708 → rightmost slot (under Q702). Q701, Q702,
Q703 and SW703 are **not moved at all** (0.000 mm, 0°) — the defect was purely a resistor-to-slot
assignment problem, not a macro-layout problem, so the fix carries zero risk to the courtyard/outline
checks that v1 had already passed, and zero effect on L11 attachment reach (the drain/common pads that
attachment_check.py and the L11 table care about never moved).

Net effect: total gate-loop length (both resistors' gate-node pad to the FET's gate pad, summed per
FET) went from Q703 28.42 mm / Q701 10.88 mm / Q702 10.06 mm (v1, wildly unbalanced, one FET at
nearly 3× the others) to Q703 9.72 mm / Q701 10.39 mm / Q702 11.28 mm (v2, balanced, no single leg
over 6.542 mm, whole-block max-leg criterion in row 3 now met — v1 would have failed it at 15.59 mm).

## 4. Deviations

**SW703 envelope, row 9.** SW703's footprint (THT slide switch body + silkscreen, no defined courtyard
layer so `apply_placement.py` falls back to the pad-shape/bbox silhouette) has a physical bounding box
of (244.000, 64.000)–(256.950, 70.950) mm — 0.5 mm above the envelope's nominal y0 = 64.5 mm at its top
edge. This is **not a placement choice available to this pass**: SW703 is listed as this block's one
fixed anchor ("do not move or rotate"), its position (250.475, 67.475) is exactly its v1 value, and v1
was the floorplan the owner already reviewed and accepted at the block level (only the passive layout
was rejected). No gate flags it: `apply_placement.py`'s own containment/overlap checks (which use real
pad/courtyard polygons, not my invented bbox-vs-envelope-box test) reported 0 outside-outline and 0
courtyard overlaps, and heritage/attachment are both 0. Recorded here for the owner's visibility, not
counted against rules_failed.

**No anchor IC was moved.** Q701/Q702/Q703 are not literally "anchor ICs" in the block-level sense
(this block has no regulator/MCU/bridge IC), but they are the L11 attachment targets; none were moved
even the small amount the 3 mm allowance would have permitted, because the v1 defect was entirely in
the resistor network, not the FET macro-placement.

## 5. Attachment-reach effect (brief L11 / `floorplan.md` §5)

| Net | FC pad | This block's pad | v1 reach | v2 reach | Δ |
|---|---|---|---|---|---|
| `FC_RESET` | J16.2 (THT) | Q701.3 (drain) | 27.6 mm | 27.567 mm | −0.03 mm |
| `USBBOOT` | J16.1 (THT) | Q702.3 (drain) | 34.5 mm | 34.541 mm | +0.04 mm |
| `WDT_DISABLE` | J16.9 (THT) | SW703.1 (pin 1) | 23.6 mm | 23.603 mm | +0.003 mm |

All three deltas are floating-point noise from the outline/pours rebuild, not real movement — Q701,
Q702 and SW703 were placed at their exact v1 coordinates. L11 attachment is unaffected by this pass.

## 6. Commands run (canonical path)

```
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
SCRATCH=<scratchpad>/detail_bench_io_drivers
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# scratch copies only (hard rule: never write FlatSat_V1.kicad_pcb or FC_V5e_Production_Rev2/)
cp FlatSat_V1.kicad_pcb FlatSat_V1.kicad_pcb.kicad_pro "$SCRATCH/"
mv "$SCRATCH/FlatSat_V1.kicad_pcb.kicad_pro" "$SCRATCH/base.kicad_pro"
mv "$SCRATCH/FlatSat_V1.kicad_pcb" "$SCRATCH/base.kicad_pcb"   # (copied then renamed)

# merge this block's 10 refs into a copy of floorplan.json (all other 208 refs unchanged)
# -> $SCRATCH/merged_floorplan.json  (python, not shown: dict update on "placements")

$KPY tools/pcb/outline.py --board "$SCRATCH/base.kicad_pcb" \
    --out "$SCRATCH/outlined.kicad_pcb" --spec "$SCRATCH/merged_floorplan.json"
# -> saved ... new bbox x 143.29..296.44 y 47.51..172.17

$KPY tools/pcb/apply_placement.py --board "$SCRATCH/outlined.kicad_pcb" \
    --placement "$SCRATCH/merged_floorplan.json" --out "$SCRATCH/placed.kicad_pcb"
# -> applied 218; refused (heritage) []; missing refs []
# -> footprints not fully inside the outline: 0: []
# -> courtyard overlaps (same-side, >=1 new part; real polygons): 0: []

$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json "$SCRATCH/placed.kicad_pcb" \
    --allow-zone-growth --allow-edge
# -> heritage check: 0 violation(s)

$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json "$SCRATCH/placed.kicad_pcb"
# -> attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
```

Measurement of every checklist row (pad-to-pad distances, GND-pour containment, envelope/lane bbox
checks, courtyard-gap estimates) was done with a `pcbnew` script against `$SCRATCH/placed.kicad_pcb`
(reads `GetPosition()`/pad positions/`GetBoundingBox()`/`GetCourtyard()` directly — see §2/§5 above for
the numbers). No routing was performed; the 65 new tracks/vias are `outline.py`'s GND stitching vias
for the grown board area, not routing of this block's nets.

## 7. Files

- `detail/placement_bench_io_drivers.json` — this block's 10 refs only, `{ref:{x,y,rot,side}}`.
- `$SCRATCH/merged_floorplan.json` — full floorplan.json with only these 10 refs replaced.
- `$SCRATCH/base.kicad_pcb` / `base.kicad_pro` — untouched copies of the live heritage board (never written).
- `$SCRATCH/outlined.kicad_pcb` — after `outline.py` (outline/pours/holes/stitching rebuilt from the merged spec).
- `$SCRATCH/placed.kicad_pcb` — after `apply_placement.py`; the board all gates above were run against.
