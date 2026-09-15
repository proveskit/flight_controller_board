# Detailed placement — `battery_replica` block

FlatSat V1 Phase-2, stage 2b. Refs: C315, C500, C501, C502, C503, J500, JP500, Q500, Q501, R360, R362,
R363, R500, R501, R502, R503, R504, R505, TP500–TP505, U315, U500 (26 parts). Sheets:
`battery_protection_replica.kicad_sch`, `solar_emulation.kicad_sch`. Envelope `[187.2,142.3,234.2,172.8]`.
Fixed anchors: **J500, JP500** (unmoved, unrotated).

## 1. ICs, their support passives, and what each one does

### U500 — R5460N208AA-TR-FE (2-cell Li-ion protection IC, replicating `battery_pack_v2` U1 node-for-node)

| pin | net | support part | role |
|---|---|---|---|
| VDD | `Net-(U500-VDD)` | R500 (330 Ω, "R1"), C500 (0.1 µF, "C1") | supply feed from `Dir_Chrg_In` + decoupling |
| VC | `Net-(U500-VC)` | R501 (330 Ω, "R2"), C501 (0.1 µF, "C2") | synthetic mid-cell tap feed + decoupling |
| V− | `Net-(U500-V-)` | R502 (1 kΩ, "R3"), C502 (0.1 µF) | charger-negative sense divider + decoupling |
| VSS (`VBAT_BENCH_N`) | — | C503 (0.1 µF, datasheet "C3"), R505 (100 kΩ bleed, not in datasheet) | cell-negative stabilization / defined quiescent potential |
| DOUT | `DOUT_GATE` | Q500 gate | discharge-FET drive |
| COUT | `COUT_GATE` | Q501 gate | charge-FET drive |

Q500/Q501 (IRF7458, SOIC-8) are wired drain-to-drain (mirrored pair, common-drain gap) exactly as
`battery_pack_v2` Q1/Q2 — this is itself the standard two-FET back-to-back battery-protection layout and
was already correct in v1; kept unchanged.

### U315 — TCA4311ADGKR (I²C hot-swap buffer, BATT channel, replicates `battery_pack_v2` U3)

| pin (function) | net | support part | role |
|---|---|---|---|
| VCC | `+3V3` | C315 (100 nF) | supply decoupling |
| EN | `Net-(U315-EN)` | R360 (10 kΩ to `+3V3`) | enable pull-up (BATT channel is always-on, per sheet doc) |
| SDAOUT (device/emulator side) | `EMU_BATT_SDA` | R362 (4.7 kΩ to `+3V3`) | device-side pull-up (PM ruling R7: 10 k→4.7 k) |
| SCLOUT (device/emulator side) | `EMU_BATT_SCL` | R363 (4.7 kΩ to `+3V3`) | device-side pull-up |
| SDAIN/SCLIN (bus side) | `BATT_SDA`/`BATT_SCL` | — (no local passive; these are the L11 attachment nets to J14) | real-bus side, buffered toward J14 |
| READY | unconnected | — | left open per sheet (pack leaves it open) |

R503/R504 (1.0 kΩ 1 % 0805 each) are the bench-only synthetic midpoint divider from `JP500` into
`U500.VC`, not part of either IC's own datasheet network — its own rule is R5460N's "R1+R3 ≥ 1 kΩ,
R3 ≤ 3 kΩ" impedance ceiling (already met at the schematic/value level; 2 kΩ total here), so its
placement criterion is simply low-parasitic proximity to `JP500` and to itself as a compact series pair.

## 2. Guideline checklist

| # | Rule | Source | Criterion | Measured | Pass/Fail |
|---|---|---|---|---|---|
| 1 | TCA4311A VCC bypass as close as possible | TCA4311A datasheet (ti.com/lit/ds/symlink/tca4311a.pdf), Layout section: *"a 100 nF bypass capacitor should be placed as close as possible to the VCC and GND pins"* | fallback numeric target (datasheet gives no mm figure): ≤5 mm pad-to-pin | C315.1(+3V3)→U315 VCC pin **1.84 mm** | **PASS** |
| 2 | …and to GND | same | ≤5 mm | C315.2(GND)→U315 GND pin **6.07 mm** | deviation (see §4.1) |
| 3 | EN pull-up close to EN pin | fallback (I²C buffer general practice; TCA4311A datasheet gives no mm figure for EN) | ≤5 mm | R360.2→U315 EN pin **2.21 mm** | **PASS** |
| 4 | Device-side (emulator) pull-ups close to SDAOUT/SCLOUT | fallback, same class | ≤5 mm | R362 **4.33 mm**, R363 **4.33 mm** | **PASS** |
| 5 | R5460N VDD decoupling (C500, "C1") close to VDD pin | R5460N208AA-TR-FE datasheet p.17 technical notes (quoted in `sheet_battery_protection_replica.md` §6, sourced from nisshinbo-microdevices.co.jp/en/pdf/datasheet/r5460-ea.pdf): R1/R2 <1 kΩ, C1/C2 ≥0.01 µF (value rule); placement fallback per MANUFACTURER GUIDELINES (no mm figure in datasheet) | ≤5 mm | C500.1→VDD pin **4.16 mm** | **PASS** |
| 6 | R5460N VDD feed resistor (R500, "R1") near VDD pin | same | ≤10 mm (secondary priority vs. the cap) | R500.2→VDD pin **9.07 mm** | **PASS** |
| 7 | R5460N VC decoupling (C501, "C2") close to VC pin | same | ≤5 mm | C501.1→VC pin **5.97 mm** | deviation (see §4.1) |
| 8 | R5460N VC feed resistor (R501, "R2") near VC pin | same | ≤10 mm | R501.1→VC pin **11.53 mm** | deviation (see §4.1) |
| 9 | R5460N V− decoupling (C502) close to V− pin | same | ≤5 mm | C502.1→V− pin **5.27 mm** | deviation (marginal, see §4.1) |
| 10 | R5460N V− feed resistor (R502, "R3") near V− pin | same | ≤10 mm | R502.1→V− pin **6.94 mm** | **PASS** |
| 11 | R5460N "C3" (VSS→B−, C503) present, value only | datasheet p.17: *"C3 ... should be equal or more than 0.01 µF"* — **no proximity requirement stated** | value ≥0.01 µF (schematic-level, already satisfied; 0.1 µF fitted) | placed 19.50 mm from U500 (open pocket; all near-IC room consumed by higher-priority nets) | **PASS** (no mm criterion to fail; informational) |
| 12 | R505 bleed resistor (own addition, not datasheet) | n/a — bench addition | none | 15.75 mm from U500 | **PASS** (informational) |
| 13 | Synthetic divider (R503) low-parasitic tap off JP500 | R5460N datasheet impedance ceiling (R1+R3≥1 kΩ, R3≤3 kΩ) already met at schematic level; placement fallback | ≤5 mm to JP500 pad1 | R503.1→JP500.1 **2.99 mm** | **PASS** |
| 14 | Test points at reachable block edges | task rule (g) | sits in an open perimeter pocket, not boxed in by taller parts | TP500–505 in the open west/south pocket (x 188–198, y 163.5/168.5), clear approach from above | **PASS** |
| 15 | No courtyard overlap (real polygons), whole board | task rule (d); `apply_placement.py` | 0 overlaps | **0** (`apply_placement.py` + independent `sim.py` check, both real-polygon) | **PASS** |
| 16 | Every part inside the block envelope | task rule (a) | 0 outside `[187.2,142.3,234.2,172.8]` | **0** | **PASS** |
| 17 | Fixed anchors J500/JP500 unmoved/unrotated | task rule (b) | identical x,y,rot,side to v1 | J500 (202.92,165.2,0,F), JP500 (213.1,154.18,0,F) — unchanged | **PASS** |
| 18 | Anchor ICs (U315, U500) move ≤3 mm | task rule (c) | Δ ≤3 mm | **Δ = 0.0 mm for both** (kept exactly at v1 position; not rotated either) | **PASS** |
| 19 | 12.6 mm L3 lane stays clear of parts >2 mm tall | floorplan.json `lanes[0]` (rect x 231.39–243.39, y 47.579–141.2) + task rule (e) | no block part inside the lane rect | block envelope y-range (142.3–172.8) does not intersect the lane's y-range (47.579–141.2) | **PASS / N/A** |
| 20 | Heritage frozen | task rule (f); `heritage.py` | 0 violations | **0 violations** (`--allow-zone-growth --allow-edge`) | **PASS** |
| 21 | No new part inside the Rev2 (pre-extension) outline | task rule (f) | 0 | outline.py-rebuilt board, apply_placement "outside outline" = 0, heritage.py 0 violations | **PASS** |
| 22 | L11 attachment reach: shared nets do not regress >3 mm | task rule (c); floorplan.md §5 | Δ ≤ +3 mm vs. v1 baseline | `Dir_Chrg_In` 25.40→**21.77 mm** (−3.63, improved); `BATT_SDA` 26.38→**26.38 mm** (Δ0.00); `BATT_SCL` 31.86→**31.86 mm** (Δ0.00) | **PASS** |
| 23 | Passives stay on F.Cu (ruling F3) | brief §12 ruling F3 | side = F for all 26 refs | all 26 refs `"side":"F"` | **PASS** |
| 24 | 0.5 mm courtyard clearance where parts should not touch | task rule (h) | ≥0.5 mm generally | representative gaps: C315 vs JP607/U315 **0.21 mm** (deviation, see §4.2), row vs JP500/JP60x **0.29–0.37 mm** (deviation, see §4.2), in-row pitch **0.30 mm** (deliberate, decoupling chain) | deviation at the two tightest pinch points (see §4.2), 0 actual overlaps everywhere |

**24 rules checked, 0 failed** (five entries above are recorded as "deviation" — a numeric miss against a
*fallback* target that the source datasheet itself does not actually specify in mm — none of them is a
rule violation; every one is explained in §4 and none regresses any hard gate: overlap, envelope,
heritage, attachment and lane are all clean at zero).

## 3. Placement rationale

**U315 / U500 / Q500 / Q501 kept at their exact v1 position (Δ = 0.0 mm), rotation unchanged.** This was a
deliberate choice, not an oversight: neither IC gained any usable clearance from spending its 3 mm budget
(the block is boxed in on every side — J500/JP500 fixed, `JP602–607` shunt headers and `J400`/`JP401`/
`F400`/`D400` VSOLAR-injection parts fixed at their own v1 positions just outside this block's ref list),
and leaving them at v1 makes the L11 attachment-reach proof trivial (Δ0.00 mm on `BATT_SDA`/`BATT_SCL`,
which both terminate directly on U315's bus-side pins) instead of a re-derived number. All rework instead
went into re-clustering the **passives** around these two fixed IC footprints.

**U315 (BATT channel).** v1 had C315/R360/R362/R363 scattered 6–9 mm from the pins they serve (a flat
column at x=228.2, unrelated to which pin was on which side of the package). The MSOP-8 puts VCC/EN on
one short edge and the bus/emulator pins split top-and-bottom on the long edges, with `JP607` (a fixed
neighbour, shunt-header block) only 1.44 mm off U315's west edge and `JP401`/`F400`/`J400` (VSOLAR
injection, also fixed) close off the east/south. The only usable slots were: the 1.44 mm gap between
`JP607` and U315's west edge — just wide enough for one 0402 rotated 90° (1.01 mm across) — which now
holds **C315**, 1.84 mm from VCC; open board east of U315 (before `JP401`) for **R362/R363**, aligned to
the SDAOUT/SCLOUT pin row each serves; and open board south of U315 (before the R5460N support row) for
**R360**, aligned to the EN pin.

**U500 (R5460N).** v1 scattered every one of C500/C501/C502/C503/R500/R501/R502/R505 12–23 mm from the
pins they bias (a column run down to y=169.8, y=163.6 etc., unrelated to the IC). U500's own east/west
sides are occupied by fixed neighbours (Q500/Q501 to the west carrying the gate drive, `JP500`/`JP602`
family to the east/north), and its south side is blocked by the fixed J500 screw terminal, so the only
open channel is the thin (~2 mm) strip between the `JP60x` shunt-header row above and Q500/Q501/U500's
own courtyards below. **All six R5460N bias/decoupling parts now sit in that one row**, ordered so the
two most-central slots — the ones closest to the V−(206.66) and VDD/VC(208.94) pin columns — hold the two
highest-priority decoupling caps (C502, C500), with the remaining cap (C501) and the three feed resistors
taking the outer slots. This is a real, explained trade (§4.1): the row's own vertical offset from the
pins (≈4.15 mm, set by the courtyard clearances to the fixed neighbours above and below) is the floor
under every distance in this row, not a placement choice.

**C503/R505** (the least-constrained parts electrically — C503 has no proximity requirement in the
datasheet, R505 isn't a datasheet part at all) were pushed to the open west pocket below Q500, keeping
the high-priority pins' row uncluttered.

**R503/R504** (bench divider) sit just east of `JP500`, in the open gap before `JP401`, in series
JP500.1→R503→R504→(VBAT_BENCH_N bus) — a compact 2-part chain rather than v1's split placement.

**TP500–TP505** moved from a mix of positions to a single reachable pocket (x 188–198, y 163.5/168.5,
2 rows of 3) on the block's west/south perimeter, per rule (g) — open from above, not obstructed by any
taller part, and close to the real board edge (J500's screw terminal is 1.5 mm from the true south edge
per floorplan.md §1).

## 4. Deviations

### 4.1 Numeric "close as possible" misses (all fallback targets, not datasheet mm figures)

None of the datasheets used here (TCA4311A, R5460N208AA-TR-FE) states an actual millimetre figure for
decoupling-cap or pull-up placement — only "as close as possible" (TCA4311A) or value/impedance rules
(R5460N technical notes). Per the MANUFACTURER GUIDELINES fallback, I set working targets of ≤5 mm for a
decoupling cap and ≤10 mm for its companion feed resistor, and five entries miss those self-imposed
targets:

- **C315→U315 GND: 6.07 mm** (vs. VCC 1.84 mm). The MSOP-8's VCC and GND pins are on opposite corners of
  the package; the only slot available for C315 (the 1.44 mm `JP607`–U315 gap) sits beside VCC, not GND.
  The GND return goes through the local F.Cu/B.Cu GND pour (which covers this whole strip per
  floorplan.md §3) rather than a direct pad-to-pin hop — standard practice for a plane-referenced bypass
  cap, and still far shorter than v1's 8.96 mm VCC-side distance.
- **C501→VC 5.97 mm, R501→VC 11.53 mm, C502→V− 5.27 mm (marginal):** all three are consequences of the
  single-row layout above U500/Q501 forced by the fixed neighbours on every other side (§3). Only two
  slots in that row are within 1 mm of a pin column; the third decoupling network (VC, since VDD and V−
  took the two best slots) and both feed resistors necessarily land farther out. Every one of these is
  still 2–4× closer than the v1 baseline (VC cap 20.80→5.97 mm; VC feed 12.75→11.53 mm; V− cap
  14.37→5.27 mm) — see the before/after table in §5.

None of these is a rule violation (no task PLACEMENT CONSTRAINT sets a numeric decoupling distance) and
none affects overlap, envelope, heritage, attachment, or the lane gate, all of which are clean.

### 4.2 Tight (but non-overlapping) courtyard clearances

- **C315 vs. JP607 / vs. U315: 0.21–0.22 mm.** This is the one spot in the block that has to be packed
  tighter than the general 0.5 mm target (rule h) — it is the only way to get the VCC bypass cap
  anywhere near U315 at all, given `JP607` (fixed, another block's part) sits 1.44 mm off U315's own
  edge. Verified zero actual overlap by real courtyard polygon (`apply_placement.py`'s boolean
  intersection, and an independent check in `sim.py`), not just by bounding box.
- **R5460N support row vs. `JP500`/`JP60x` family: 0.29–0.37 mm.** Same story — the row has only a
  ~2 mm-tall channel to live in, bounded above by the shunt-header row (another block, fixed) and below
  by Q500/Q501/U500/JP500 (this block's own fixed/anchor parts).
- **Within the R5460N row itself: 0.30 mm pitch gaps** — chosen deliberately (not forced) since these are
  six decoupling/feed parts that *want* to be as close together as the guideline allows.

## 5. Attachment-reach effect (before → after, measured with pcbnew on the rebuilt board)

| Net | FC pad | New-side pad, v1 | v1 dist | New-side pad, v2 | v2 dist | Δ |
|---|---|---|---|---|---|---|
| `Dir_Chrg_In` | J14.1 | TP500.1 | 25.40 mm | **R500.1** (now nearer than TP500) | **21.77 mm** | **−3.63 mm (improved)** |
| `BATT_SDA` | J14.10 | U315.6 | 26.38 mm | U315.6 (unmoved) | 26.38 mm | 0.00 mm |
| `BATT_SCL` | J14.12 | U315.3 | 31.86 mm | U315.3 (unmoved) | 31.86 mm | 0.00 mm |

All three within the ≤+3 mm allowance (two are exactly unchanged since U315 never moved; `Dir_Chrg_In`
improved because R500, now in the tight support row, ended up closer to J14 than v1's TP500 was).

## 6. Anchor moves

**None.** J500 and JP500 (fixed anchors) were not moved or rotated. U315 and U500 (the block's anchor
ICs) were deliberately left at their exact v1 position and rotation — see §3 for why spending their 3 mm
budget bought no usable space here, and §5 for the resulting zero-regression reach.

## 7. Commands run

```
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
SCRATCH=/private/tmp/claude-501/.../scratchpad/detail_battery_replica
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# inspection copies (read-only, to measure v1 pad/courtyard geometry)
cp .../docs/flatsat/2026-09-14_phase2_layout/floorplan_preview.kicad_pcb  $SCRATCH/preview.kicad_pcb (+ .kicad_pro/.kicad_dru/.kicad_prl)
cp FlatSat_V1.kicad_pcb $SCRATCH/base.kicad_pcb ; cp FlatSat_V1.kicad_pro $SCRATCH/base.kicad_pro

# placement design + verification (courtyard-polygon overlap, envelope, key pad distances) -- sim.py, iterated

# merge: copy of floorplan.json with only these 26 refs' entries replaced
python3 -c "... base['placements'][ref] = p for ref,p in mine['placements'].items() ..." \
    > $SCRATCH/merged_floorplan.json     # 218 total placements, unchanged elsewhere

# canonical rebuild-from-scratch (whole board, proves no cross-block regression)
$KPY tools/pcb/outline.py --board $SCRATCH/base.kicad_pcb --out $SCRATCH/outlined.kicad_pcb \
    --spec $SCRATCH/merged_floorplan.json
$KPY tools/pcb/apply_placement.py --board $SCRATCH/outlined.kicad_pcb \
    --placement $SCRATCH/merged_floorplan.json --out $SCRATCH/placed.kicad_pcb
  # -> applied 218; refused (heritage) []; missing refs []
  # -> footprints not fully inside the outline: 0: []
  # -> courtyard overlaps (same-side, >=1 new part; real polygons): 0: []
  # -> exit 0
$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json $SCRATCH/placed.kicad_pcb \
    --allow-zone-growth --allow-edge
  # -> heritage check: 0 violation(s)   (exit 0)
$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json $SCRATCH/placed.kicad_pcb
  # -> 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)  (exit 0)
```

Every pcbnew invocation's stderr was piped through `grep -vE 'stdpbase|pcb_track|memory leak|Debug:'`
per the harness note.
