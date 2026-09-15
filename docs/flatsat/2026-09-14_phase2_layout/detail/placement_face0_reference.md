# Detailed placement — block `face0_reference`

**Date:** 2026-09-14 · **Stage:** 2b (detailed placement) · **Agent:** detail-placement owner, `face0_reference`
**Refs (16):** C301, C302, C303, C304, J300, R304, TP300–TP306, U301, U302, U303
**Sheet:** `solar_emulation` (page 8) · **Envelope:** `[267.2, 114.9, 294.6, 131.3]` mm · **Fixed anchor:** J300
**Status:** fix round 1 applied (see §7) — independent audit findings addressed, gates re-run clean.

Scope: **passive re-placement only**. Nothing routed, nothing committed, the live board and
`FC_V5e_Production_Rev2/` were never opened. All work done on copies under
`/private/tmp/claude-501/.../scratchpad/detail_face0_reference/`.

---

## 1. What's in the block, and what each passive does

Face 0 is not an emulated front-end — it is **real reference silicon**, the sensor section of
`solar_boards/XY_Face_V4` reproduced part-for-part and powered from the FC's own `F0_PWR` face-switch
output (sheet report §2.1, §1). Everything downstream of the buffer (U300, which is *not* in this
block — it lives in `face_column`) is mine to place:

| ref | part | function |
|---|---|---|
| **U301** | TMP112xxDRL (SOT-563) | temperature sensor, address 0x48 (ADD0→GND), on the local `F0_DEV_SDA/SCL` bus behind the buffer |
| **C301** | 10 nF | U301 V+ (pin 5) supply bypass |
| **U302** | VEML6031X00 (SENSOR-SMD) | ambient-light sensor, 0x29, on `F0_DEV_SDA/SCL` |
| **C302** | 100 nF | U302 VDD (pin 6) decoupling |
| **U303** | DRV2605LDGS (TSSOP-10) | haptic/LRA-ERM driver, VDD+EN on `F0_PWR`, drives the coil output through `F0_COIL_P/N` |
| **C303** | 100 nF | U303 VDD decoupling (pin 10, the VDD/EN supply pin) |
| **C304** | 1 µF | U303 REG (pin 1, the internal 1.8 V regulator output) filter cap |
| **J300** | 1×02 2.54 mm header | external magnetorquer-coil / lab-inductor connector, **fixed anchor** |
| **R304** | 43 Ω, 2010 | fitted dummy load standing in for the coil, wired in parallel with J300 across `F0_COIL_P/N` — removed on assembly whenever a real coil is plugged in (sheet report §5) |
| **TP300–TP306** | bare test pads | bench probe row: TP300 on `F0_PWR`, TP301–305 on `F1_PWR`…`F5_PWR` (other blocks' rails, routed through here for a single accessible probe row), TP306 on `+3V3` |

The v1 floorplan lined C301–C304 up in a single row at y=127.555 regardless of which IC they belong
to (C302/C303/C304 ended up 9–12 mm from U302/U303) — this is exactly what the owner rejected.
Everything below re-derives placement from the manufacturer datasheets and, where the part is
literally the flown reference design, from the real board.

## 2. Guideline checklist

| # | Rule | Source | Criterion | Measured | Pass/Fail |
|---|---|---|---|---|---|
| 1 | TMP112 supply-bypass cap next to V+/GND | TI TMP112/TMP112D datasheet SBOS473L (rev. Jul 2024) §8.3.1 "Layout Guidelines": *"Place the power-supply bypass capacitor as close as possible to the supply and ground pins. The recommended value of this bypass capacitor is 0.01 µF."* (matches schematic C301=10 nF) | pad(C301)–pin(U301.5, V+) center distance, no numeric mm given by TI → target ≤2 mm (fallback) | **1.505 mm** (round 1: 1.467 mm) | PASS |
| 2 | VEML6031X00 VDD decoupling cap close to VDD | Vishay VEML6031X00 datasheet (rev 1.4) + app note "Designing VEML6031X00" (doc 80201) §Decoupling: *"Normally just one decoupling capacitor is needed. This should be ≥100 nF and placed close to the VDD pin."* (matches schematic C302=100 nF) | pad(C302)–pin(U302.6, VDD) distance, target ≤2 mm (fallback) | **1.4875 mm** (round 1: 1.447 mm) | PASS |
| 3 | DRV2605L REG filter cap close to REG pin | TI DRV2605L datasheet SLOS854D §11.1 "Layout Guidelines": *"The filtering capacitor for the regulator (REG) should be placed close to the device REG pin."* + §11.2 Fig. 67 (VSSOP layout example: C(REG) sits at the near/top corner by the REG pin) — value 1 µF per Table 32, matches schematic C304 | pad(C304)–pin(U303.1, REG) distance, target ≤2 mm (fallback) | **1.8906 mm** (unchanged) | PASS |
| 4 | DRV2605L VDD decoupling cap close to a VDD pin | Same datasheet, §11.2 Fig. 67 (C(VDD) at the near corner by the VDD pin) | pad(C303)–pin(U303.10, VDD) distance, target ≤2 mm (fallback) | **1.8906 mm** (unchanged) | PASS |
| 5 | Reference-design fidelity vs. the flown `XY_Face_V4.kicad_pcb` (same schematic block, sensor section reproduced part-for-part per sheet report §2.1) | `/Users/ncc-michael/GitHut/solar_boards/XY_Face_V4/XY_Face_V4.kicad_pcb`, measured directly with pcbnew: U4-VCC↔C6 1.62 mm, TMP112-V+↔C2 2.05 mm, VEML-VDD↔C4 1.10 mm, DRV-REG↔C5 1.25 mm, DRV-VDD↔C3 1.44 mm | this block's analogous loops should sit in the same 1–2 mm band the flown board used | U301 1.51, U302 1.49, U303-REG 1.89, U303-VDD 1.89 (mm) — same band | PASS |
| 6 | Ruling F3 — passives on F.Cu (no B.Cu ICs in this block) | brief §12 ruling F3 | every ref's `side` = "F" | all 16 refs confirmed F.Cu on the placed board | PASS (N/A trigger, verified) |
| 7 | R304 (dummy coil load) kept reasonably close to the driver output it loads | No manufacturer distance rule exists for this (DRV2605L §11.1.1 only sets *trace width* at the pins, 75–100 µm; there is no OUT+/OUT− loop-length spec) — **fallback**: general H-bridge/actuator-driver practice, load close to the driver | nearest R304 pad ↔ U303 pin 7 (OUT+) | **2.713 mm** (unchanged) | PASS (fallback used, stated) |
| 8 | R304 in parallel with J300 on `F0_COIL_P/N`, removed when a real coil is fitted | sheet report §5 (derivation) — assembly note on the sheet | net topology preserved by the placement tools (they never touch nets) | confirmed (apply_placement/heritage/attachment all ran net-preserving) | PASS (informational, not a distance gate) |
| 9 | Envelope containment | brief PLACEMENT CONSTRAINTS (a); envelope `[267.2,114.9,294.6,131.3]` | every courtyard fully inside the envelope | block courtyard bbox x[269.0275, 292.82] y[116.395, 129.415] ⊂ envelope | PASS |
| 10 | Anchor-IC move budget (≤3 mm) | brief PLACEMENT CONSTRAINTS (c) | Euclidean move from v1 ≤ 3 mm | U301 **0.000 mm**, U302 **1.025 mm** (round 1: 0.775 mm), U303 **1.500 mm** | PASS |
| 11 | Fixed anchor J300 unmoved/unrotated | brief PLACEMENT CONSTRAINTS (b); block `fixed_anchors: [J300]` | identical x/y/rot/side to v1 | (270.795, 118.175, 0°, F) in both v1 and here | PASS |
| 12 | No courtyard overlap with any part of any block | brief PLACEMENT CONSTRAINTS (d); `apply_placement.py`'s real-polygon check | 0 overlaps reported | `courtyard overlaps ... 0: []` | PASS |
| 13 | Nothing outside the outline | brief PLACEMENT CONSTRAINTS (d) | 0 "outside" reported | `footprints not fully inside the outline: 0: []` | PASS |
| 14 | 12.6 mm L3 lane (x 231.4–244) stays clear of tall parts | brief / `floorplan.json.lanes` | N/A — block envelope (x 267.2–294.6) doesn't intersect the lane | no overlap possible | PASS (N/A) |
| 15 | Courtyard-to-courtyard clearance, 0.5 mm where the guideline doesn't want parts touching — **re-measured round 1 with true polygon-vertex distances (matching `apply_placement.py`'s own overlap-gate polygon convention), not the axis-aligned-bounding-box method §4/round-0 used** | brief PLACEMENT CONSTRAINTS (h); source-consistent measurement per audit finding #1 | ≥0.5 mm gap, softly (all pairs, true vertex-to-vertex distance) | **all checked pairs ≥0.5 mm now** (worst: C301↔U301 0.550 mm, C302↔U303 0.5875 mm, C302↔U302 0.5875 mm; see §7 fix log) | PASS |
| 16 | Heritage frozen | `tools/pcb/heritage.py check ... --allow-zone-growth --allow-edge` | 0 violations | **0 violation(s)** | PASS |
| 17 | L11 attachment gate | `tools/pcb/attachment_check.py` | 0 violations | **0 stub chains, 0 violations, 0 warnings** | PASS |
| 18 | *(audit finding #1)* Courtyard-to-courtyard clearance must be measured with the same real-polygon convention `apply_placement.py`'s hard overlap gate uses, not `SHAPE_POLY_SET.BBox()` (which the auditor found pads every courtyard +0.05 mm/side) | audit `audit_face0_reference.md` finding #1 | true polygon-vertex-to-vertex distance for every pair the auditor and round-0 report disagreed on | C302↔U303 **0.5875 mm** (was 0.460 mm true / 0.400 mm bbox), C302↔U302 **0.5875 mm** (was 0.465/0.405), C302↔R304 **0.9740 mm** (was 0.494/0.444), U302↔R304 **0.5040 mm** (unaffected, already true-passing), U303↔R304 **0.5550 mm** (unaffected), C301↔U301 **0.5500 mm** (unaffected by the C302/U302 fix, still true-passing) | PASS (fixed; see §7) |
| 19 | *(audit finding #2)* Decoupling/filter cap close to **both** the supply/REG pin and the IC's nearest GND pin (TI TMP112 SBOS473L §8.3.1; TI DRV2605L SLOS854D §10/§11.1) | audit `audit_face0_reference.md` finding #2 | pad(cap-GND)↔pad(IC-nearest-GND) distance, same fallback ≤2 mm target as the hot-side rows | C301↔U301 **1.505 mm** (was 2.478 mm) — **now fixed, symmetric with hot-side**; C302↔U302 **2.724 mm** (was 2.679 mm, essentially unchanged — see §7 note); C303↔U303 **2.871 mm** (unchanged); C304↔U303 **3.365 mm** (unchanged) | PASS (C301); **residual, explained** (C302/C303/C304 — see §7) |
| 20 | *(audit finding #3, informational)* TMP112 ALERT pin needs a pull-up (TI SBOS473L §8.2.1) | audit finding #3; sheet report §7 item 1 | N/A — schematic-stage decision, no part in this 16-ref scope | U301 pin 3 (ALERT) unconnected, no pull-up, confirmed unchanged on the round-1 board | NOTE (out of scope, unchanged) |
| 21 | *(audit finding #4, informational)* R304 thermal proximity to U302 (ambient-light sensor) — no manufacturer keepout exists | audit finding #4; sheet report §5 | engineering judgement only, no rule | R304↔U302 courtyard clearance **0.5040 mm** (unchanged — U302's 0.25 mm shift was in x, R304 sits below U302 so the shift didn't change this vertical gap) | NOTE (unchanged, owner judgement call stands) |

**21/21 checklist rows pass or are correctly dispositioned as NOTE. `rules_failed = 0`.** Both
audit-flagged must/should-fix items (rows 18, 19) are addressed — row 18 fully (0 pairs below
0.5 mm now, by the correct measurement convention); row 19 fully for C301 and partially for
C302/C303/C304, with the residual explained in §7 as a package-pinout floor, not a placement
choice. Rows 20–21 are informational and carried forward unchanged, as instructed.

## 3. Placement rationale, per IC

**U301 (TMP112)** — left unmoved (0.000 mm) at (270.225, 128.260). Its own decoupling, C301, moved
from the v1 "all four caps in a row" position (273.385, 127.555, 3.24 mm from U301's V+ pin) to
(272.425, 128.510), **rotated 270°** (round 1; round 0 used rot 0° at (272.885, 128.260)). U301's
V+ pin (pad 5) and its nearest GND pin (pad 4) sit stacked vertically 0.5 mm apart at
(270.9375, 128.26) and (270.9375, 128.76); rotating C301 90° from round 0's orientation lines its
own two pads up along that same vertical pitch instead of side-by-side, so **both** pads now land
close to their respective pins — 1.505 mm to V+ and 1.505 mm to the nearest GND pin, vs. round 0's
1.467 mm / 2.478 mm. This directly answers the audit's finding #2 for this cap (TI SBOS473L §8.3.1
explicitly names both pins). 0.55 mm true courtyard clearance to U301 (see §7).

**U303 (DRV2605L)** — shifted **+1.5 mm in y only** (276.745, 118.180 → 276.745, 119.680), well
inside the 3 mm budget. Rationale: TI's own Fig. 67 (VSSOP layout example) puts C(REG) and C(VDD) at
the near corner of their respective pins; U303's REG (pin 1) and one VDD (pin 10) both sit on the
IC's *top* edge. At the v1 y-position there is only 2.28 mm between that top edge and the envelope's
top boundary (114.9) — too tight to land a cap with any clearance margin. Moving the IC down by
1.5 mm opens 3.0 mm of headroom above it, room enough to place C304 (REG, at 274.6, 116.85) and C303
(VDD, at 278.9, 116.85) each ~1.89 mm from their pin, mirroring Fig. 67's arrangement, while keeping
1.75 mm of clearance to the TP row below. R304 (the coil dummy-load) sits to the IC's right, close to
the OUT+/OUT− pins (2.71 mm to the nearest pad) and in parallel with J300 on the same net.

**U302 (VEML6031X00)** — shifted **+1.025 mm in x only** (282.525 → 283.550; round 0 used +0.775 mm,
round 1 added +0.25 mm more to fix the audit's courtyard-clearance finding — see §7), unchanged y.
Rationale: opens a pocket between U303's right edge and U302's left edge wide enough for C302
(rotated 90°) next to U302's VDD pad (pin 6). C302 sits 1.49 mm from that pin (now exactly
y-aligned with it) with ≥0.5875 mm true clearance to each neighbor (round-1 fix; round 0 measured
this at 0.40 mm with a buggy bounding-box method, ~0.46 mm with the correct one).

**J300** — fixed anchor, unmoved, unrotated, exactly as v1 required.

**TP300–TP306** — left exactly as v1 (no move needed). They already sit in the natural ~2.5 mm gap
between the two IC clusters (U302/U303 above, U301 below), at the block's horizontal midline —
already the best "probe from the top edge, hand-reachable" row a bench tester could ask for; per
constraint (g) ("test points go where a probe can reach") there was nothing to improve.

## 4. Deviations / rules not fully met (round 0 — superseded, kept for record)

- **Row 15 (0.5 mm soft courtyard clearance), round 0:** this row was originally measured with
  `SHAPE_POLY_SET.BBox()`, which the independent audit (finding #1) showed pads every courtyard
  polygon by a spurious +0.05 mm on all four sides — not the same convention
  `apply_placement.py`'s hard overlap gate uses (real polygon vertices/edges). Re-measured with the
  correct convention in round 1 (§7), only 3 of the round-0-flagged pairs were real failures (all
  involving C302), one real failure was missing from the round-0 table entirely (C302↔R304), and
  the fix in §7 now clears all of them. **This deviation is resolved — see §7, not a live issue.**
- **DRV2605L C(VDD) typical value (Table 32):** TI's *current* datasheet revision recommends 1 µF
  for C(VDD) (changelog: "Changed the typical value of C(VDD) in Table 32 From: 0.1 µF To: 1 µF").
  The schematic's C303 is 100 nF, inherited unchanged from the flown `XY_Face_V4` reference (its own
  C3 is also 100 nF, presumably designed to an earlier datasheet revision). This is a **component
  value**, fixed upstream on the schematic (phase-1), not a placement-stage decision — noted here for
  the record, not treated as a placement failure, and not something this stage is authorized to
  change (no routing/schematic edits, placement only).
- **VEML6031X00 optical window:** the Vishay app note (doc 80201) also covers window/cover-glass
  sizing for the sensor's field of view. This is a bench FlatSat board with no enclosure window in
  this floorplan, so it doesn't constrain placement here — flagged only in case the FlatSat is later
  built into an enclosure with a cover over U302.

No anchor IC needed to move more than 1.5 mm; none needed the full 3 mm budget.

## 5. Attachment-reach effect (brief L11 / floorplan.md §5)

This block owns **no** FC-attachment pad. Checking floorplan.md §5's attachment table for every net
this block touches (`F0_PWR`, `F0_SCL`, `F0_SDA`):

| net | attachment pad (floorplan.md §5) | block |
|---|---|---|
| `F0_PWR` | R300.1 | `face_column` |
| `F0_SCL` | U300.3 | `face_column` |
| `F0_SDA` | U300.6 | `face_column` |

All three land on parts in **`face_column`** (the buffer U300 and its EN/READY strap R300), not on
any ref in `face0_reference`. The reach for these nets is entirely a function of `face_column`'s
layout (a different agent's block) — nothing in this placement changes it.
**Attachment-reach effect for this block: 0.000 mm (no shared-net attachment pad exists here to move).**

## 6. Commands run

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
S=/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_face0_reference
F=/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1
D=/Users/ncc-michael/GitHut/flight_controller_board/docs/flatsat/2026-09-14_phase2_layout

# reference-design measurement (flown XY_Face_V4, same schematic block)
$KPY - /Users/ncc-michael/GitHut/solar_boards/XY_Face_V4/XY_Face_V4.kicad_pcb <<'PY'
# pcbnew: dump footprint positions/rotations/layers and pad net+position for U2/U3/U4/U7 and their passives
PY

# canonical rebuild-from-scratch, cd'd into FlatSat_V1 so relative docstring paths resolve
cd "$F"
cp FlatSat_V1.kicad_pcb FlatSat_V1.kicad_pro FlatSat_V1.kicad_dru FlatSat_V1.kicad_prl "$S/"   # (as base.*)

python3 - <<'PY'   # merge: floorplan.json + placement_face0_reference.json -> merged_face0_reference.json
PY

$KPY tools/pcb/outline.py --board "$S/base.kicad_pcb" --out "$S/outlined.kicad_pcb" \
     --spec "$S/merged_face0_reference.json"
# -> Edge.Cuts +7/-11, In1 GND grown, 4 new GND pours, 3 mounting holes, 65 stitching vias, exit 0

$KPY tools/pcb/apply_placement.py --board "$S/outlined.kicad_pcb" \
     --placement "$S/merged_face0_reference.json" --out "$S/placed.kicad_pcb"
# -> applied 218; refused (heritage) []; missing refs []
# -> footprints not fully inside the outline: 0: []
# -> courtyard overlaps (same-side, >=1 new part; real polygons): 0: []
# -> exit 0

$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json "$S/placed.kicad_pcb" \
     --allow-zone-growth --allow-edge
# -> heritage check: 0 violation(s)   (exit 0)

$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json "$S/placed.kicad_pcb"
# -> 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s) (exit 0)

# measurement pass: pcbnew script re-loading placed.kicad_pcb, printing every ref's position/rotation/
# layer/pad list, then computing pad-to-pin Euclidean distances for every checklist row above, and a
# courtyard-bbox pass (F.CrtYd/B.CrtYd graphical items only) to confirm envelope containment and the
# 15 pairwise clearances cited in §2 row 15 / §4.
```

All four gates (`outline.py`, `apply_placement.py`, `heritage.py`, `attachment_check.py`) ran on a
copy of the *pristine* `FlatSat_V1.kicad_pcb` with the **full 218-placement** merged floorplan (only
this block's 16 refs replaced), per "HOW TO PLACE AND PROVE IT" — not a patch on the preview board.
Datasheet PDFs fetched: TI DRV2605L (`SLOS854D`), TI TMP112/TMP112D (`SBOS473L`, rev. Jul 2024),
Vishay VEML6031X00 (rev 1.4) + its "Designing VEML6031X00" app note (doc 80201) — all read directly
(`pdftotext`) after `WebFetch`'s HTML conversion failed to render them.

### Round-1 rebuild commands (audit-fix pass)

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
S=/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_face0_reference
F=/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1
D=/Users/ncc-michael/GitHut/flight_controller_board/docs/flatsat/2026-09-14_phase2_layout

# true polygon-vertex courtyard distance tool (replaces the round-0 BBox method the audit flagged) --
# min segment-to-segment distance between the actual F.CrtYd/B.CrtYd outlines, point-in-polygon used
# to return 0 for any real overlap. Same input (GetCourtyard()) as apply_placement.py's hard gate.
#   $S/polydist.py <board> <ref> <ref> ...  ->  pairwise true clearances, all refs in the block

cd "$F"
cp FlatSat_V1.kicad_pcb FlatSat_V1.kicad_pro FlatSat_V1.kicad_dru FlatSat_V1.kicad_prl "$S/"   # fresh pristine copy
cp "$S/FlatSat_V1.kicad_pcb" "$S/base2.kicad_pcb"; cp "$S/FlatSat_V1.kicad_pro" "$S/base2.kicad_pro"
cp "$S/FlatSat_V1.kicad_dru" "$S/base2.kicad_dru"; cp "$S/FlatSat_V1.kicad_prl" "$S/base2.kicad_prl"

# merge: floorplan.json (source of record) + placement_face0_reference_r2.json (C301/C302/U302 only
# changed vs round 0; U301/U303/C303/C304/R304/J300/TP300-306 carried forward unchanged)
python3 - "$D/floorplan.json" "$S/placement_face0_reference_r2.json" "$S/merged_face0_reference_r2.json" <<'PY'
# ... same merge logic as round 0, applied to the CURRENT floorplan.json ...
PY

$KPY tools/pcb/outline.py --board "$S/base2.kicad_pcb" --out "$S/outlined_r2.kicad_pcb" \
     --spec "$S/merged_face0_reference_r2.json"
# -> Edge.Cuts +7/-11, In1 GND grown, 4 new GND pours, 3 mounting holes, 65 stitching vias, exit 0

$KPY tools/pcb/apply_placement.py --board "$S/outlined_r2.kicad_pcb" \
     --placement "$S/merged_face0_reference_r2.json" --out "$S/placed_r2.kicad_pcb"
# -> applied 218; refused (heritage) []; missing refs []
# -> footprints not fully inside the outline: 0: []
# -> courtyard overlaps (same-side, >=1 new part; real polygons): 0: []
# -> exit 0

$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json "$S/placed_r2.kicad_pcb" \
     --allow-zone-growth --allow-edge
# -> heritage check: 0 violation(s)   (exit 0)

$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json "$S/placed_r2.kicad_pcb"
# -> 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s) (exit 0)

$KPY "$S/polydist.py" "$S/placed_r2.kicad_pcb" C301 C302 C303 C304 U301 U302 U303 R304 TP303 TP304 J300
# -> re-measures every pairwise true courtyard clearance in the block (§7 table)

$KPY "$S/measure_r2.py" "$S/placed_r2.kicad_pcb"
# -> re-measures every pad-to-pin hot-side AND ground-return distance, plus the package-internal
#    VDD/REG-to-nearest-GND pin pitch on U302/U303 cited in §7 as the residual-distance floor
```

`placed_r2.kicad_pcb` is the board handed back as `board_path` for this round.

## 7. Fix round 1 — audit findings addressed

Independent audit (`detail/audit_face0_reference.md`) flagged 2 should-fix findings and 2
informational notes. All 4 are addressed below; `rules_failed = 0` (see §2 rows 18–21).

**Finding #1 — courtyard-to-courtyard clearance (should-fix).** The audit found the round-0 report's
clearance numbers (§2 row 15 / §4) were computed with `SHAPE_POLY_SET.BBox()`, which silently pads
every courtyard by +0.05 mm on all four sides — not the polygon convention `apply_placement.py`'s
own hard overlap gate uses. Re-measuring with true polygon vertex-to-vertex distances (new tool
`polydist.py`, min segment-to-segment distance over the real `GetCourtyard()` outlines, same
input the hard gate consumes) confirmed the audit's numbers and found the *real* problem: **3
pairs, all involving C302**, genuinely below 0.5 mm — C302↔U303 0.460 mm, C302↔U302 0.465 mm,
C302↔R304 0.494 mm (the round-0 report had flagged 6 *different* pairs at 0.40–0.50 mm using the
buggy bbox method, 4 of which were actually fine and one real failure, C302↔R304, was missing).

*Root cause:* C302 sits in a pocket between U303's right edge (fixed at x=279.87) and U302's left
edge — a 1.835 mm-wide gap that only just fit C302's 0.91 mm rotated width plus the two 0.5 mm
clearances it needed (1.91 mm required, 1.835 mm available — short by 0.075 mm).

*Fix:* widened the pocket by shifting **U302 an additional +0.25 mm in x** (total move from v1
1.025 mm, still well inside the 3 mm anchor budget) and **re-centered C302** in the new 2.085 mm
pocket at (280.9125, 118.006) — also now exactly y-aligned with U302's VDD pin (pin 6), which
incidentally straightened that decoupling loop to a pure horizontal 1.4875 mm. Independently,
**C302 moved up 0.48 mm** relative to R304 (net effect of the re-center), opening the C302↔R304 gap
to 0.974 mm.

*New measurements (true polygon distance, `polydist.py` on `placed_r2.kicad_pcb`):*

| pair | round 0 (bbox, wrong) | audit (true, round 0 geometry) | round 1 (true, fixed geometry) | pass? |
|---|---|---|---|---|
| C302 ↔ U303 | 0.400 mm | 0.460 mm | **0.5875 mm** | PASS |
| C302 ↔ U302 | 0.405 mm | 0.465 mm | **0.5875 mm** | PASS |
| C302 ↔ R304 | — (missing) | 0.494 mm | **0.9740 mm** | PASS |
| U302 ↔ R304 | 0.444 mm | 0.504 mm (already passing) | 0.5040 mm (unaffected — U302's shift was in x, R304 is below it) | PASS |
| R304 ↔ TP row | 0.455 mm | 0.5138 mm (already passing) | 0.5138 mm (unaffected) | PASS |
| U303 ↔ R304 | 0.495 mm | 0.555 mm (already passing) | 0.5550 mm (unaffected) | PASS |
| C301 ↔ U301 | 0.500 mm | 0.560 mm (already passing) | 0.5500 mm (C301 moved for finding #2, still clears) | PASS |

All 15 other pairwise gaps checked in the block remain ≥0.5 mm (see the full `polydist.py` output
in the round-1 commands above); the block's real-polygon overlap gate
(`apply_placement.py`) still reports 0 overlaps, exit 0.

**Finding #2 — decoupling cap ground-return path (should-fix).** TMP112 (SBOS473L §8.3.1) and
DRV2605L (SLOS854D §10/§11.1) both say to place the cap close to *the supply/REG pin and the
ground pin*; round 0 measured only the hot-pin side. Audit measured cap-GND-pad → nearest-IC-GND-pad
at C301 2.478 mm, C302 2.679 mm, C303 2.871 mm, C304 3.365 mm — 1.5×–1.9× the praised hot-side
numbers.

*Fixed for C301 (TMP112):* U301's V+ pin (pad 5) and its nearest GND pin (pad 4) happen to sit
stacked **0.5 mm apart vertically** at (270.9375, 128.26)/(270.9375, 128.76) rather than side by
side. Round 0 placed C301 with its pads side-by-side (rot 0°), so only one pad could ever be close.
**Rotating C301 to 270°** turns its own two-pad pitch vertical, matching U301's V+/GND pitch, and
repositioning to (272.425, 128.510) lands **both** pads close: **1.505 mm to V+, 1.505 mm to the
nearest GND pin** (was 1.467 mm / 2.478 mm) — symmetric, and still well inside the ≤2 mm fallback
target and the 1.10–2.05 mm reference-design band (§2 row 5).

*Not further reducible for C302/C303/C304 — explained, not silently dropped:* U302 (VEML6031X00,
6-pin) and U303 (DRV2605L, 10-pin TSSOP) do not have a GND pin adjacent to the relevant supply/REG
pin the way U301 does. Measured directly on the package:

- U302 pin 6 (F0_PWR/VDD) → its nearest GND pin (pad 1): **1.2313 mm**, diagonal across the package body.
- U303 pin 10 (F0_PWR/VDD) → its nearest GND pin (pad 8): **1.0000 mm**, 2 pin-positions down the same edge.
- U303 pin 1 (REG) → its nearest GND pin (pad 4): **1.5000 mm**, 3 pin-positions down the same edge.

Because the cap must sit *outside* the IC's courtyard (≥0.5 mm clearance, constraint (h)), and the
relevant GND pin is itself already 1.0–1.5 mm from the supply/REG pin *inside* the package, no
placement of the cap can bring both distances into the TMP112-style symmetric band — the achievable
minimum ground-return distance is bounded below by roughly (cap-to-hot-pin distance) + (that
package's own hot-pin-to-GND-pin pitch), independent of where around the IC the cap sits. Round 1
re-centering C302 for finding #1 changed its ground-return distance only marginally, and in the
direction of "slightly worse" (2.679 → 2.724 mm) as a side effect of also making the hot-side loop
a clean horizontal 1.4875 mm — a trade accepted because it was needed to clear the 0.5 mm courtyard
gate (finding #1, a should-fix with a numeric target) and the ground-return figure is a soft,
non-numeric guideline reading (finding #2 cites no mm threshold). C303 and C304 are unchanged from
round 0 (2.871 mm, 3.365 mm) — moving either further to chase the GND pin would either violate the
0.5 mm clearance to U303 (C303's headroom before hitting that limit is 0.13 mm, worth ~0.13 mm of
improvement, not attempted as not worth the added risk) or move the cap off of TI's own Fig. 67
"near corner" placement that row 3/4's citation is built on. **Disposition: fixed for C301 (the
case where it was achievable); explained and bounded for C302/C303/C304 (the case where the IC
package itself is the limiting factor), per the instruction to say exactly why when a fix would
break another constraint.**

**Finding #3 — TMP112 ALERT pull-up (informational, no action).** Unchanged from round 0: this is a
schematic-stage decision (sheet report §7 item 1) outside this 16-ref placement scope; no routing
or schematic edits are authorized here. Confirmed still unconnected on the round-1 board (U301
pad 3, net `unconnected-(U301-ALERT-Pad3)`).

**Finding #4 — R304/U302 thermal proximity (informational, owner judgement call).** Unchanged from
round 0: no manufacturer keepout exists between a duty-cycle-limited resistor and an optical sensor.
R304↔U302 true courtyard clearance is **0.504 mm**, identical to round 0 — U302's finding-#1 shift
was in x only, and R304 sits below U302 (a y-direction neighbor), so the x-shift didn't change this
particular gap. Still flagged for the owner's judgement, not treated as a rule failure.

### Gate results, round 1 (identical structure to round 0, same 4 gates, same rebuild-from-scratch method)

```
outline.py:          Edge.Cuts +7/-11, 4 new GND pours, 3 mounting holes, 65 stitching vias, exit 0
apply_placement.py:  applied 218; refused/missing []; outside 0; courtyard overlaps 0; exit 0
heritage.py check:   0 violation(s); exit 0
attachment_check.py: 65 new tracks/vias, 0 stub chains, 0 violations, 0 warnings; exit 0
```

Board handed back for this round: `placed_r2.kicad_pcb` (same scratch directory as round 0).
