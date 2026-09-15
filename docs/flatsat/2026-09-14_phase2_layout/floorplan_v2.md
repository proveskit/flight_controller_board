# PROVES FlatSat V1 — Phase 2 floorplan **v2** (detailed passive placement) — integration **v2.2**

Stage 2b integrator output, 2026-09-14. **This package overwrites the previous (v2.1) package in place**
(`floorplan_v2.json`, `floorplan_v2.md`, `floorplan_v2_preview.*`, `img/floorplan_v2_*`), so the build
stage keeps pointing at the same names.

- Floorplan of record for v2: `/Users/ncc-michael/GitHut/flight_controller_board/docs/flatsat/2026-09-14_phase2_layout/floorplan_v2.json`
  (`based_on_v2.floorplan` = the v2.1 file of the same name; provenance chain recorded in the key)
- Preview board (with its `.kicad_pro` / `.kicad_dru` / `.kicad_prl` siblings, page A3):
  `/Users/ncc-michael/GitHut/flight_controller_board/docs/flatsat/2026-09-14_phase2_layout/floorplan_v2_preview.kicad_pcb`
- The live board `FlatSat_V1/FlatSat_V1.kicad_pcb` was **read only** (mtime unchanged, 2026-09-14 11:31:05).
  Nothing routed, nothing committed, the KiCad GUI was never opened, `FC_V5e_Production_Rev2/` was read
  once, as `heritage.py`'s `--ref-board`, and never written.

---

## 1. Owner summary — one page

### 1.1 Changes since the previous integration (v2.1 → v2.2)

The v2.1 package passed every hard gate, and seven of its nine blocks passed their datasheet audits. A
second PM-directed fix round re-placed the two that had not: `emulator_core` (with an escalated Opus
fixer) and `charger_bq25886`. Both now hold an independent auditor's **PASS with 0 must-fix and
0 should-fix**. **52 of the 218 placements changed since v2.1**; the other seven blocks are
byte-identical to v2.1.

| Block | Refs changed vs v2.1 | Max move | What moved / which audit items closed |
|---|---|---|---|
| `emulator_core` | 46 of 47 (`C200–C222`, `D200–D202`, `L200`, `R200–R211`, `TP200–TP203`, `U201`, `U202`, `Y200`; only `U200` is bit-identical) | 22.463 mm (`R204`) | Whole block re-solved around the RP2350 regulator loop. **v2.1's single open owner question is closed by geometry:** the `VREG_PGND` return is now **C213 GND → U200 pin 47 = 2.033 mm** (v2.1: nearest 1V1 cap GND terminal 8.340 mm), with C217 GND → pin 47 = **2.911 mm**. Also closed: v2.1's must-fix #1 (same item), the crystal load-cap asymmetry (`C221`/`C222` signal legs now **1.900 / 1.900 mm, mismatch 0.000 mm`)`, and the 4.7 µF/100 nF banks re-seated onto their own supply pins (10 of 13 power pins now ≤ 2 mm). `Y200` rotated 270° and moved 2.725 mm; `U201` +1.500 mm; `U202` rotation only. |
| `charger_bq25886` | 6 (`R510 R511 R516 R517 R518 L510`) | 7.793 mm (`R510`) | v2.1 listed two open should-fix pairs. Both are closed: `J510↔R510` / `J510↔R511` at **0.550 mm** and `R517↔U511` at **0.560 mm** (round-4 fixes that v2.1 predated and therefore did not carry), and the round-5 `L510↔U511` inductor pair is fixed outright — `L510` +0.130 mm in x only, gap **0.430 → 0.560 mm**, SW-pad cost +0.075 mm (3.946 → 4.021 mm). |
| `face_column`, `bench_io_drivers`, `battery_replica`, `bench_io_cable`, `face0_reference`, `strip_left_pyro_shunts`, `vsolar_injection` | 0 | — | Unchanged since v2.1; all seven **PASS**. `face_column`'s v2.1 must-fix (R372 vs the stitching via) stays closed — that via has not moved again. |

**Three further stitching points had to move** (§5.1) because `emulator_core`'s re-place walked parts
under the east ring and the emulator south row. One of the three was a hard defect: the via at
(284.00, 115.50) was being silently re-netted **GND → `EMU_GPIO_RSVD`** by `apply_placement.py`'s
connectivity rebuild, because `TP203` landed 0.254 mm from it. All 65 vias are on GND again.

**Nothing else changed.** No block-boundary conflict arose this round (§5.2): the full-board
real-polygon courtyard scan finds **0 cross-block pairs below 0.5 mm**, so no integrator nudge was
needed and §5.2's v2.1 fix (`battery_replica`'s seven parts) is carried through untouched.

**Trades the PM accepted this round** (decisions, not open questions — §5.3):

1. **29 intra-block courtyard pairs below 0.5 mm**, minimum **0.110 mm** (`C315↔U315`), all of them a
   decoupling / input / output / bootstrap capacitor — or, for `C217↔L200` (0.150 mm), the output cap
   against the inductor the RP2350 datasheet explicitly wants it beside — sitting against the pin it
   serves. `emulator_core` contributes 11, `charger_bq25886` 8, `battery_replica` 10. Four blocks have none.
2. **Three more fixed GND stitching points moved** (§5.1), under the PM's step-6b authority. `stitching`
   is otherwise frozen; nine of the 65 points have now been relocated across v2.1+v2.2, none added or removed.
3. **`emulator_core`'s seven named deviations D-1…D-7** stay as deviations, not defects. Each is a miss
   against the *report's own* self-imposed mm target (the RP2350 datasheet's own wording for these is
   qualitative), each has a demonstrated geometric floor, and the independent auditor spot-checked the two
   largest and declined to escalate either.
4. **`charger_bq25886`'s two disclosed BAT/SYS-cap trades** (C515 at 7.143 mm; three *redundant* SYS caps
   at 5.29–7.62 mm courtyard gap) stay as disclosed priority trade-offs — the only alternative demotes a
   numbered §11.1 priority-1 row to satisfy an unnumbered pin-table line.
5. **Six 0402/SOT-23 parts poke ≤ 0.505 mm into the wider 12.6 mm band.** The **12.00 mm lane rect
   written into `floorplan_v2.json` is the lane of record and is completely empty**; measured clear depth
   in front of every named connector is **≥ 15.93 mm**. Per the PM's standing ruling this is closed.
6. **Fixed anchors whose courtyards poke past their block envelope** (`J400`, `J401`, `J701`) are not
   findings.

### 1.2 Per block: rules checked / passed / accepted trades / open items

163 → **176 manufacturer-guideline rules** have now been checked across the nine blocks, **0 failed**.
(v2.1 recorded 2 failed, both in `emulator_core`; both are gone.)

| Block | Refs | Rules checked | Rules failed | Accepted trades (PM) | Open items | Auditor verdict |
|---|---|---|---|---|---|---|
| `face_column` | 48 | 19 (carried, v2.1) | 0 | 0 sub-0.5 mm pairs | none | **pass** (v2.1 must-fix closed by §5.1) |
| `bench_io_drivers` | 10 | 12 (carried) | 0 | none | none | **pass** (1 note) |
| `battery_replica` | 26 | 24 (carried) | 0 | 10 sub-0.5 mm pairs, min 0.110 mm | none | **pass** |
| `bench_io_cable` | 11 (6 movable) | 16 (carried) | 0 | none | none | **pass** (2 notes) |
| `emulator_core` | 47 | **33** (this round) | **0** | 11 sub-0.5 mm pairs, min 0.135 mm; 7 named deviations D-1…D-7 | 2 routing/pour carve-outs (N-1 VREG_PGND via topology, N-2 copper cutout under L200) — not decidable on an unrouted board | **pass** (0 must-fix, 0 should-fix, 4 notes) |
| `face0_reference` | 16 | 21 (carried) | 0 | none | none | **pass** (2 notes) |
| `strip_left_pyro_shunts` | 20 (3 movable) | 11 (carried) | 0 | none | none | **pass** (2 notes) |
| `vsolar_injection` | 11 (3 movable) | 11 (carried) | 0 | none | none | **pass** |
| `charger_bq25886` | 29 (27 movable) | **29** (this round; the auditor independently audited 27) | **0** | 8 sub-0.5 mm pairs, min 0.280 mm; 2 disclosed BAT/SYS trades | 1 note for stage 3/5: `Q510`'s DFN2020-6 land pattern has 0.19 mm adjacent-pad spacing vs the project's 0.2 mm blanket default — invariant under placement | **pass** (0 must-fix, 0 should-fix, 4 notes) |

**Anchor-IC moves.** `U200` 0.000, `U201` 1.500, `U202` 0.000 (rot 0→180), `Y200` 2.725, `U511` 0.000,
`U315`/`U500` 0.000, `U300`/`U310`–`U314` 0.000, `U316` 0.100, `U301` 0.000, `U302` 1.025, `U303` 1.500 mm —
all inside the 3 mm budget measured the way each block's audit measured it. Measured instead against the
**original v1 `floorplan.json`**, four parts exceed 3 mm: `L200` 11.419, `L510` 14.609 (both inductors —
support parts, not their blocks' constraint-(c) anchor IC), `U510` 8.448 (the charger's load switch, ruled
a support part in round 3) and `U201` 3.354 (the flash; 1.500 mm of that is this round's). None of the four
carries a shared FC net — `emulator_core` and `charger_bq25886` have **no entry at all** in the L11
attachment map — so constraint (c)'s operative clause ("attachment reach must not get worse by more than
3 mm") is untouched by every one of them. §1.4 is the binding evidence.

### 1.3 Gate table (all run by me, on a board rebuilt from scratch from the pristine live board)

| Gate | Criterion | Result |
|---|---|---|
| `apply_placement.py` | applied 218, refused 0, outside outline 0, courtyard overlaps 0, exit 0 | **applied 218 · refused [] · missing [] · outside 0 · overlaps 0 · EXIT 0** |
| `heritage.py check --allow-zone-growth --allow-edge --refill --core-inset 12 --ref-board …Rev2` | 0 violations | **heritage check: 0 violation(s) · EXIT 0** (55 expected zone-reshape / Edge.Cuts notes) |
| `attachment_check.py` | 0 violations, 0 warnings | **65 new tracks/vias, 0 stub chains into the flight section, 0 violations, 0 warnings · EXIT 0** |
| L3 lane | no part > 2 mm tall inside x 231.4–244 in front of J1/J2/J6/J9/J11/J13/J16/J12/J22 | **pass** — the 12.00 mm lane rect of record (`[231.39, 47.579, 243.39, 141.2]`) holds **0 courtyards**; measured clear depth in front of every named connector **≥ 15.93 mm** (J11); the only courtyards in the wider 12.6 mm band are six 0402/SOT-23 parts (≤ 1.1 mm tall), max penetration **0.505 mm** |
| RF keep-outs (brief §2) | U13→RF1 region, U30 8 mm surround | **pass** — nearest new part: **49.47 mm** from U13, **38.92 mm** from U30, **54.88 mm** from RF1 |
| New parts inside the Rev2 outline | 0 | **0** (heritage check clean; every new ref is east of x = 143.3/above y = 142.1 in the new area) |
| Block envelopes | every part inside, fixed anchors excepted | **0 non-anchor breaches**; only `J701` (bench_io_cable) and `J400`/`J401` (vsolar_injection) poke out — the named exception |
| Cross-block courtyard gaps | ≥ 0.5 mm, real polygons | **0 pairs < 0.50 mm** across every block boundary (full board, all 218 new refs × 483 footprints) |
| Stitching vias | every new via on GND, ≥ 1.2 mm from any non-GND pad | **65/65 on GND · 0 points within 1.2 mm of a non-GND pad**; tightest 1.2044 mm (to `H12`'s netless mounting-hole pad), tightest to a *signal* pad 1.2739 mm (`TP400.1`) |
| `kicad-cli pcb drc` (with `.kicad_pro`/`.kicad_dru`/`.kicad_prl` siblings + the schematic set, `--refill-zones`) | parity = the 11 §6 baseline items, `courtyards_overlap` ≤ 1, everything else unconnected-only | **parity 11 (+0 in every class) · courtyards_overlap 1 (+0, the heritage `SW2`/`TP2` item) · unconnected 383 (nothing routed) · clearance 7, every one intra-footprint inside `U301` and `Q510`** — full disposition in §4 |

### 1.4 Attachment reach (brief L11) — v2.2 vs v1

**37 nets · max 35.8 mm (v1 35.8) · median 26.4 mm (v1 26.4) · sum 947 mm (v1 959, −12 mm).**

**Nets worse by more than 3 mm: none.** Worst regression `+3V3` J16.6→R370.1 **+0.6 mm**; best
improvement `Dir_Chrg_In` J14.1→R500.1 **−3.6 mm**, then `F1_PWR`/`F3_PWR` −2.5 mm and `F5_PWR` −2.2 mm.
**Identical to v2.1 to the tenth of a millimetre in every row** — neither block fixed this round consumes
any shared FC net. Full table in §2.

### 1.5 Renders

All in `/Users/ncc-michael/GitHut/flight_controller_board/docs/flatsat/2026-09-14_phase2_layout/img/`, all regenerated from the shipped board:

- `floorplan_v2_top.png`, `floorplan_v2_bottom.png` — 3D, whole board
- `floorplan_v2_top.pdf`, `floorplan_v2_bottom.pdf`, `floorplan_v2_in1_gnd.pdf`, `floorplan_v2_in2.pdf`,
  `floorplan_v2_all_copper.pdf` — fab-style, via `tools/pcb/render.sh`
- Per-block close-ups (`--zoom` + `--pivot` do work): `floorplan_v2_block_<block>.png` for all nine
  blocks, plus `floorplan_v2_block_face_column_{n,m,s}.png` (three zoom-5 tiles down the column) and
  `floorplan_v2_block_face_column_bcu.png` (B.Cu view of U310/U312/U314). Framing table in §6.9.
  `--pivot X,Y,0` is in centimetres from the board centre (219.866, 109.842) and **+Y moves the view
  toward *smaller* board y** — v2.1's calibration, re-used unchanged.

### 1.6 Questions the owner must answer

**One.**

1. **Is stage 2b done?** Every hard gate is clean, every block holds an independent PASS with zero
   must-fix and zero should-fix, and v2.1's only open owner question (the `emulator_core` VREG_PGND
   return path) is closed by measurement at **2.033 mm**. Nothing in the package is waiting on a
   decision. **Say go and the build stage can take `floorplan_v2.*` as-is; otherwise name what you want
   re-opened.**

Everything else that could have been a question is a PM decision recorded in §5.3 — including the
12.6 mm-band 0402s, the sub-0.5 mm capacitor pairs, the seven `emulator_core` deviations, and the three
stitching moves. Override any of them and I will re-run the affected block.

---

## 2. Attachment map (brief L11) — v2.2 vs v1, every shared net

Method identical to `floorplan.md` §5: pad centre of the named FC allowed pad to the pad centre of the
nearest **new** pad carrying that net, measured with `pcbnew` on the shipped board.

| Net | FC attachment pad | v1 (mm) | v2.2 (mm) | Δ | Consumed at |
|---|---|---|---|---|---|
| `+3V3` | J16.6 | 21.9 | 22.5 | +0.6 | R370.1 |
| `F0_PWR` | J6.4 | 25.6 | 25.4 | -0.2 | C300.1 |
| `F0_SCL` | J6.5 | 27.9 | 27.9 | -0.0 | U300.3 |
| `F0_SDA` | J6.6 | 27.6 | 27.6 | -0.0 | U300.6 |
| `F1_PWR` | J9.4 | 25.7 | 23.2 | -2.5 | R314.1 |
| `F1_SCL` | J9.5 | 35.8 | 35.8 | +0.0 | U310.3 |
| `F1_SDA` | J9.6 | 35.6 | 35.6 | -0.0 | U310.6 |
| `F2_PWR` | J11.4 | 25.5 | 24.6 | -0.9 | R320.1 |
| `F2_SCL` | J11.5 | 27.8 | 27.8 | -0.0 | U311.3 |
| `F2_SDA` | J11.6 | 27.5 | 27.5 | -0.0 | U311.6 |
| `F3_PWR` | J13.4 | 25.7 | 23.2 | -2.5 | R333.1 |
| `F3_SCL` | J13.5 | 35.8 | 35.8 | +0.0 | U312.3 |
| `F3_SDA` | J13.6 | 35.6 | 35.6 | -0.0 | U312.6 |
| `F4_PWR` | J1.4 | 25.2 | 24.5 | -0.7 | R340.1 |
| `F4_SCL` | J1.5 | 27.8 | 27.8 | -0.0 | U313.3 |
| `F4_SDA` | J1.6 | 27.5 | 27.5 | -0.0 | U313.6 |
| `F5_PWR` | J2.4 | 25.3 | 23.1 | -2.2 | R353.1 |
| `F5_SCL` | J2.5 | 35.8 | 35.8 | -0.0 | U314.3 |
| `F5_SDA` | J2.6 | 35.5 | 35.5 | -0.0 | U314.6 |
| `SCL_Top` | J16.7 | 27.5 | 27.4 | -0.1 | U316.3 |
| `SDA_Top` | J16.5 | 30.2 | 30.1 | -0.1 | U316.6 |
| `BATT_SCL` | J14.12 | 31.9 | 31.9 | -0.0 | U315.3 |
| `BATT_SDA` | J14.10 | 26.4 | 26.4 | -0.0 | U315.6 |
| `FC_RESET` | J16.2 | 27.6 | 27.6 | -0.0 | Q701.3 |
| `USBBOOT` | J16.1 | 34.5 | 34.5 | +0.0 | Q702.3 |
| `WDT_DISABLE` | J16.9 | 23.6 | 23.6 | +0.0 | SW703.1 |
| `B-` | J15.1 | 11.4 | 11.4 | -0.0 | JP607.1 |
| `INHIB_1` | J29.2 | 11.1 | 11.1 | +0.0 | JP603.1 |
| `INHIB_2` | J10.3 | 22.5 | 22.5 | -0.0 | JP605.1 |
| `IN_RBF` | J30.2 | 11.1 | 11.1 | -0.0 | JP606.1 |
| `VBATT_SENSE` | J8.2 | 11.1 | 11.1 | +0.0 | JP604.1 |
| `VBUSP` | J30.1 | 13.6 | 13.6 | +0.0 | JP606.2 |
| `Deploy1_EN` | U6.3 | 19.4 | 19.4 | +0.0 | D600.1 |
| `Deploy2_EN` | U6.6 | 22.5 | 22.5 | -0.0 | TP602.1 |
| `Heater_EN` | U6.5 | 22.9 | 22.9 | -0.0 | TP601.1 |
| `Dir_Chrg_In` | J14.1 | 25.4 | 21.8 | -3.6 | R500.1 |
| `VSOLAR` | J11.1 | 31.1 | 31.6 | +0.5 | JP401.2 |

**v2.2: 37 nets · max 35.8 · median 26.4 · sum 947 mm — v1: max 35.8 · median 26.4 · sum 959 mm.
Nets worse by > 3 mm: none.** Every row is identical to v2.1: neither block re-placed this round consumes
a shared FC net. `GND` is not in the table (it reaches the extension through the grown In1 plane and the
new pours, with no new via inside the flight section).

---

## 3. Per-block detail

Each section quotes the block's own guideline checklist verbatim from `detail/placement_<block>.md`, then
the independent auditor's verdict from `detail/audit_<block>.md`, then this integration's disposition. The
two blocks re-placed this round (§3.5, §3.9) carry their new round-6 checklists and audits; the other seven
are carried forward from the v2.1 report unchanged, because their placements are byte-identical.

### 3.1 `face_column` — 48 refs · auditor verdict **fail** (its 1 must-fix is closed — see the note below; 0 should-fix, 3 notes)

> **Unchanged since v2.1 — 0 refs moved this round.** Its v2.1 must-fix (R372 pad copper 0.130 mm from the stitching via at (250.97, 50.60)) was closed by the v2.1 integration's own stitching move, and that point has not moved again: `R372.2` is still **1.5099 mm** from point #2 on this round's board. The block is **pass** with no open item. Section carried forward from the v2.1 report, verbatim.


All numbers below are freshly measured with `pcbnew` on `placement_face_column_placed.kicad_pcb`
(fix round 3), using `fp.GetCourtyard(layer)` real polygon bounding boxes for every courtyard
measurement — the same method used since round 2. This round's numbers are cross-checked against
`apply_placement.py`'s own real-polygon overlap test (0 overlaps reported, §15.4), and 45 of 48
refs (everything except C316/R371/R372) were independently confirmed byte-identical to round 2
before re-measuring (§15.0), so rows below with no round-2→3 change are re-verified, not carried
over on faith.

| # | Rule | Source | Criterion | Measured (round 3) | Pass/Fail |
|---|---|---|---|---|---|
| 1 | VCC decoupling (100 nF), hot (VCC-net) pad nearest VCC pin, shortest GND return | TCA4311A SCPS226C §11.1 Layout Guidelines / §11.2 Fig. 16 ("placed ... as close ... as possible"); §5 Pin Functions VCC row ("bypass capacitor ... close to this pin") | as close as possible, subject to constraint (h) | F-side (C300/C311/C313): **2.210 mm each**, unchanged. B-side via-pair (C310/C312/C314): **2.207 mm**, unchanged. TOP (C316): **2.090 mm** — was 8.712 mm, fixed this round (§15.1) | **Pass (7/7 at 2.09–2.21 mm)** — was 6/7 + 1 deviation |
| 2 | EN strapped high to VCC through 10 k, at the EN pin | TCA4311A §8.3.3 + sheet §2.2 | ≤ ~2 mm to EN pin (fallback figure, §2) | R300 1.965, R310 1.915, R320 2.196, R330 1.915, R340 2.196, R350 1.915, R370 2.196 mm (unchanged, none of these refs moved) | **Pass** (7/7, 1.9–2.2 mm) |
| 3 | READY pulled to VCC through 10 k at the READY pin | TCA4311A §8.3.2 | ≤ ~2 mm to READY pin | R301 2.196, R311 1.915, R321 2.196, R331 1.915, R341 2.196, R351 1.915 mm (unchanged); R371(TOP) **4.580 mm** — was 8.709 mm (§15.1; still the block's farthest pull-up, disclosed, §9B) | **Pass** (7/7 have a real, measured value); 1 disclosed residual gap, halved not eliminated |
| 4 | Device-side SDAOUT/SCLOUT pull-ups (10 k Face 0 / 4.7 k elsewhere, PM ruling R7) at their own pin | Sheet §2.1/§2.2, PM ruling R7 | ≤ ~2 mm to the SDAOUT/SCLOUT pin | R302 2.119, R303 2.851, R312 1.946, R322 2.119, R323 2.119, R332 1.946, R342 2.119, R343 2.119, R352 1.946 mm (unchanged, 9/14); R313(F1) 2.817 mm (unchanged); **R333(F3) 11.099 mm, R353(F5) 11.242 mm** (unchanged — genuine L11-governed trade, §9B / row 19); R372(TOP) **3.380 mm** — was 8.690 mm (§15.1); R373(TOP) 2.119 mm (unchanged) | **Pass** (12/14 at ≤2.85 mm, up from 11/14); 2 documented deviations (R333/R353 only) |
| 5 | Sense tap (4.7 k, Fn_PWR→EMU_Fn_SENSE) near the buffer's GND column, output free to run east to U200 | **Our own fallback placement-distance proxy, corrected citation this round (§15.2)** — same status as rules 1–4's "~2 mm" figure, not a datasheet/brief number | ≤ ~2 mm from IC GND pin | R324 2.196, R334 1.915, R344 2.196, R354 1.915, R374 2.196 mm (GND-pin anchor, unchanged); R314(F1) still has no local IC pad on its own net — governed by row 19 (L11) instead, unchanged reasoning from round 0/1/2 | **Pass** (5/6 have a clean IC-local anchor) |
| 6 | Passives on F.Cu; B.Cu-IC decoupling cap directly opposite, via pair (ruling F3) | Owner ruling F3 | side = F for all 41 passives; C310/C312/C314 centre-offset 0 mm | Confirmed: 41/41 `side:"F"`; C310/C312/C314 offset 0.000 mm | **Pass** (41/41) |
| 7 | No same-side courtyard overlap, block-internal and vs. every other block | Constraint (d); `apply_placement.py` | exit 0, 0 overlaps | `apply_placement.py`: **courtyard overlaps: 0** (whole board, 218 placements) | **Pass** |
| 8 | Every part inside the block envelope and the Rev2 outline | Constraint (a)(f) | x∈[242,268.3], y∈[50.5,135.5]; 0 new-part intrusion | All 48 courtyards fully inside. U316 F.CrtYd north edge **50.555 mm, 0.055 mm inside** y0=50.5 (unchanged, U316 didn't move). C316/R371/R372's new courtyards' north edges are **50.945 / 50.935 / 50.935 mm — 0.445/0.435/0.435 mm inside** y0=50.5, comfortably clearer than U316's own margin. `apply_placement.py`: **outside outline: 0** | **Pass** (48/48) |
| 9 | Heritage frozen | Constraint (f); `heritage.py` | 0 violations (`--allow-zone-growth --allow-edge`) | **heritage check: 0 violation(s)** | **Pass** |
| 10 | L3 lane (x 231.4–244) stays clear of parts > 2 mm tall | Constraint (e) | nothing of this block in the lane band is > 2 mm | Block's west-most courtyard edge is now x=243.495, shared by R314/R333/R353 **and** C316 (C316's new west edge lands at the same x by coincidence of the chosen 0.55 mm IC clearance) — all four are 0402/MSOP-8 (≤1.1 mm tall), well under 2 mm regardless of x | **Pass** |
| 11 | Attachment reach to the FC pad does not regress > 3 mm per shared net (L11) | Constraint (c); floorplan.md §5 table | Δreach ≤ 3.0 mm per net vs. the table | **All 21 nets identical to round 2** (max Δ = +0.602 mm, `+3V3`) — none of the 21 L11 nets touch C316/R371/R372, so nothing could move (§15.5 full table, independently re-measured, not assumed) | **Pass (21/21)** |
| 12 | Rotation chosen so loops are short / pins face the pins they connect to | Constraint (g) | qualitative | C316 rot 180°→**180°** (unchanged number, but the meaning flips: hot VCC pad now faces **east**, toward U316, since C316 moved to the IC's *west* flank — the opposite-facing choice from round 2, re-derived for the new position, §15.1); R372 rot 0°→**180°** (hot SDAOUT pad now faces west, toward U316, from its new *east*-flank slot); R371 rot unchanged at **0°** (hot READY pad already faced west, still correct from its new east-flank slot). All three re-verified against the flipped alternative (§15.1) — every choice here is the shorter of the two | Design choice, not gated |
| 13 | *(round-0 audit, must-fix)* Constraint (c): the 3-net regression, independently re-measured | Round-0 audit §3.1 | Δ ≤ 3.0 mm on F1_PWR/F3_PWR/F5_PWR specifically | **23.152 / 23.155 / 23.060 mm** (Δ −2.548/−2.545/−2.240 vs v1) — unchanged from round 1, see row 11 | **Pass (3/3)** |
| 14 | *(round-0 audit, should-fix)* Rule 1 measured from the cap's actual VCC-net pad, not just "the cap" | Round-0 audit §3.2 | VCC-net-pad→VCC-pin, hot pad nearest the IC | C300/C311/C313 **2.210 mm** each (unchanged); C316 **2.090 mm** — was 8.712 mm (§15.1) | **Pass (7/7 rotated)** — was 4/4 + 1 deviation |
| 15 | *(round-1/2 audit, should-fix, cleared round 2)* Constraint (h): ≥0.5 mm courtyard-to-courtyard clearance, real `GetCourtyard()` polygons | Round-1/2 audit | ≥ 0.500 mm same-layer courtyard gap | **Minimum gap in the block: 0.510 mm** (R314–U300, R333–U311, R353–U313, unchanged). The 3 new pairs this round's fix creates — U316↔C316, U316↔R372, R371↔R372 — all measure **0.550 mm** (§15.6, by design: the same 0.55 mm target used throughout the round-2 row fixes). **0 of the block's same-side pairs are below 0.5 mm.** | **Pass** |
| 16 | *(round-0 audit, note, cleared round 2)* Constraint (a): U316 envelope excursion, pre-existing in v1 | Round-0/2 audit | Courtyard fully within `[242,50.5,268.3,135.5]` | U316 unchanged this round (y=53.6). **F.Courtyard north edge = 50.555 mm, 0.055 mm inside** y0=50.5 (unchanged) | **Pass** |
| 17 | *(round-2 audit, should-fix 1)* TCA4311A SCPS226C §11.1 "placed ... as close ... as possible" — U316's decoupling cap and 2 pull-ups | Round-2 audit §4 should-fix 1 | as close as possible, no numeric target; auditor's own suggested fix (extend the south row east) claimed to reach ~2.1–2.3 mm | **Fixed with a different, better-measured layout** (§15.1): C316 **2.090 mm**, R372 **3.380 mm**, R371 **4.580 mm** — all far below the pre-fix 8.69–8.71 mm, and C316 (the datasheet's explicitly-named part) now *beats* every other channel's decoupling cap. The auditor's literal same-row suggestion was independently re-derived and found **not** able to reach 2.1–2.3 mm for all three parts (real geometry gives ≈4–9 mm depending on slot assignment, §15.1 proof) — a corrected, better alternative (flanking the IC west+east instead of extending one row) is used instead, with the shortfall on R371 explained by real pitch-vs-target-spread arithmetic, not by an unexplored option | **Pass** (materially fixed; residual gap on R371 is proven-minimal, not unaddressed) — was **should-fix** |
| 18 | *(round-2 audit, should-fix 2)* Row 5's citation must not misattribute an unrelated electrical-value rule as a placement-distance source | Round-2 audit §4 should-fix 2 | citation accuracy | Row 5 above no longer cites "brief rule 10 (E9, §7.7b)" — replaced with an explicit "our own fallback proxy" label, matching how rows 1–4 already disclose their "~2 mm" figure (§15.2) | **Pass** — was **should-fix** |
| 19 | *(round-2 audit, note)* R314/R333/R353's long reach to their nominal B-Cu IC — genuine L11-driven trade, re-confirmed | Round-2 audit §4 note | no numeric target; verify the trade is real and bounded | Independently re-confirmed this round (§15.3): geometry unchanged (these 3 refs did not move), L11 reach for F1/F3/F5_PWR still 23.06–23.16 mm, **−2.24 to −2.55 mm vs. v1** (an improvement, well inside the 3 mm budget) — no fix needed, not reopened | **Pass** (no action needed, confirmed not just repeated) |

**Rules checked: 19. Rules failed: 0.**

**Auditor:** FAIL — 1 must-fix: *"R372's new position violates real copper clearance against a fixed
stitching via"* — `kicad-cli` reported `Clearance violation (netclass 'Default' clearance 0.2000 mm;
actual 0.1300 mm) · Via [GND] on F.Cu-B.Cu, pos (250.97, 50.6) · Pad 2 [EMU_TOP_SDA] of R372 on F.Cu`.
The auditor could not fix it because `stitching` was frozen for the block role. Three notes, all
re-confirmed as non-blocking.

**Integration disposition: CLOSED.** The PM authorised editing `stitching` for exactly this class of
problem (brief step 6b). Stitching point #2 moved (250.97, 50.60) → (250.42, 53.20), 2.66 mm, keeping
the perimeter x-ladder; R372 did not move, so none of this block's 19 measured rows changed.
`kicad-cli pcb drc` on the shipped board reports **7 clearance errors, all intra-footprint pad-to-pad
inside U301 and Q510 — none names R372, any other `face_column` ref, or any via** (§4).


---

### 3.2 `bench_io_drivers` — 10 refs · auditor verdict **pass** (0 must-fix, 0 should-fix, 1 note)

> **Unchanged since v2.1 — 0 refs moved this round.** Section carried forward verbatim.


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

**Auditor:** PASS — 0 must-fix, 0 should-fix, 1 note (pre-existing, non-blocking: SW703 is a fixed
anchor whose footprint has no courtyard layer, so its silhouette falls back to the pad union).
Unchanged since the previous integration.


---

### 3.3 `battery_replica` — 26 refs · auditor verdict **pass** (0 must-fix, 0 should-fix)

> **Unchanged since v2.1 — 0 refs moved this round**, including the seven parts the v2.1 integration nudged to clear the `strip_left_pyro_shunts` headers (still 0.520 mm). Section carried forward verbatim.


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

**Auditor:** PASS. Notably the auditor **refuted** the placer's own self-reported deviation on row 2:
TCA4311A §11.2 Figure 16 shows the bypass cap's GND pad dropping straight into the plane through a via,
not a trace back to the IC's GND pin, so the 6.07 mm cap-GND-to-IC-GND-pin distance is the correct
topology, not a miss.

**Integration disposition:** this block's 7 re-pitched parts were the only cross-block conflict of the
integration; all 7 moved a further ≤0.20 mm in the v2.1 integration's §5.2. The row's guideline distances change by ≤0.05 mm
(C500→VDD 4.16 → 4.18 mm class), well inside every criterion above.


---

### 3.4 `bench_io_cable` — 11 refs (6 movable) · auditor verdict **pass** (0 must-fix, 0 should-fix, 2 notes)

> **Unchanged since v2.1 — 0 refs moved this round.** Section carried forward verbatim.


| # | Rule | Source | Criterion | Measured (fix round 3) | Pass/Fail |
|---|---|---|---|---|---|
| 1 | CC1/CC2 pull-down resistors as close as practical to the receptacle's CC pins | USB Type-C spec sink-detection network (generic practice) — **fallback**, no manufacturer layout guide exists for a bare pull-down resistor; J701's datasheet has no layout section (see §9) | Pad-centre distance R701.2↔J701.A5 and R702.2↔J701.B5 | R701.2↔A5 = **9.5763 mm**; R702.2↔B5 = **9.5763 mm** (unchanged — not touched this round) | **Pass** |
| 2 | USB_DP/USB_DM series termination resistors placed close to the chip (U200), not the connector | Raspberry Pi, *Hardware design with RP2350*, §5.1 "USB": *"these I/Os do require 27 Ω series termination resistors (R7 and R8 in Figure 11), placed close to the chip, in order to meet the USB impedance specification."* | Pad-centre distance from R703/R704's U200-side pad to U200 pin 52 (DP) / 51 (DM) | R703.2↔U200.52 = **1.9383 mm**; R704.2↔U200.51 = **1.9383 mm** (unchanged) | **Pass** |
| 2b | D+/D- pair symmetry (pad-to-pad leg-length match) | Same source, §5.1 | \|R703.2↔U200.52 − R704.2↔U200.51\| | **0.000 mm** (unchanged) | **Pass** |
| 3 | VBUS bulk/bypass cap adjacent to the VBUS pins, short GND return | **Fallback** (generic decoupling practice; neither J701's nor C701's datasheet has an application-specific layout section, see §9) | Pad-centre distance C701.1(VBUS, net `VBUS_EMU`)↔ nearest J701 VBUS pad | C701.1 (281.95, 52.0) ↔ J701.A9=B4 (277.45, 50.075) = **4.8944 mm** — up from round 2's 4.508 mm (**+0.386 mm**, the disclosed cost of this round's courtyard fix), still an order-of-magnitude improvement over round 0/1 (9.9–10.1 mm). Fallback target (1–2 mm) still not met — see §3, §7 | **Pass (fallback honestly not fully met — disclosed)** |
| 4 | Test points at block edges, probe-reachable | Brief PLACEMENT CONSTRAINTS (g) | TP701 distance to the true `Edge.Cuts` boundary (not the internal envelope line — corrected this round per the round-3 audit note §3.3/§9.3) | TP701 unchanged at (286.0, 53.5). Independently re-measured against the real Edge.Cuts polyline (not the envelope line): **4.646 mm** clear to the nearest board-edge segment (matches round-1's estimate of ≈4.6 mm, now exact) | **Pass** |
| 5 | No courtyard overlap with any part of any block (real polygons) | Brief PLACEMENT CONSTRAINTS (d) | `apply_placement.py` courtyard-overlap count | **0** (see §4) | **Pass** |
| 6 | Every part inside the block envelope | Brief PLACEMENT CONSTRAINTS (a) | Courtyard bbox of every moved ref within x[267.8,294.4] / y[51.1,91.2] | All 6 owned refs' courtyard bboxes inside the envelope. Tightest margin this round: **C701 north edge, 0.125 mm clear of y0=51.1** (was 0.395 mm in round 2 — tighter but still positive; the rotation trades some north margin for courtyard clearance on both sides, see §3). R703/R704 south edge unchanged at 1.145 mm clear | **Pass** |
| 7 | Fixed anchors do not move or rotate | Brief PLACEMENT CONSTRAINTS (b) | J701/J702/J703/SW701/SW702 position, rotation, side identical pre/post | Identical (see §5) | **Pass** |
| 8 | 12.6 mm L3 lane (x 231.4–244) kept free of parts > 2 mm tall | Brief PLACEMENT CONSTRAINTS (e) | Block x-range vs lane x-range | Block occupies x 267.8–294.4, entirely east of the lane — **N/A** | **Pass (N/A)** |
| 9 | Heritage frozen | Brief PLACEMENT CONSTRAINTS (f) | `heritage.py check --allow-zone-growth --allow-edge` | **0 violations** (see §4) | **Pass** |
| 10 | L11 attachment gate | Brief PLACEMENT CONSTRAINTS (c) / `attachment_check.py` | New tracks/vias into the Rev2 flight section | 65 new items (outline.py's stitching vias, none ours), **0 violations, 0 warnings** | **Pass** |
| 11 *(auditor)* | Test points at block edges — literal reading of constraint (g)'s parenthetical | Round-1 audit, carried forward | TP701 sits at a true envelope/board edge | Unchanged, re-confirmed — see row 4 | **Pass** |
| 12 *(auditor)* | §6 attachment-reach documentation must attribute the correct measured pad | Round-1 audit, carried forward | floorplan.md §5's L11 table measures FC_RESET/USBBOOT/WDT_DISABLE at Q701.3/Q702.3/SW703.1 (`bench_io_drivers`), not at J703 | Correction stands unchanged — see §6 | **Pass** |
| 13 *(auditor)* | 0.5 mm courtyard-to-courtyard minimum ("don't pack just because you can", constraint h) | Round-3 audit §3.1, **should-fix** — fixed this round | C701↔J701, C701↔TP701, C701↔J702, R703↔R704, R703/R704↔U200, R701/R702↔J701 courtyard gaps | **C701↔J701: 0.130 mm → 0.600 mm** (now compliant outright, no exception invoked). C701↔TP701: 0.80 → **1.770 mm** (also improved). C701↔J702: 4.47 → **3.400 mm** (still far clear). R703↔R704: 0.81 mm (unchanged, > floor). R703/R704↔U200: 0.655 mm each (unchanged, > floor — termination resistors, general rule, no exception ever invoked). R701/R702↔J701: 0.75 mm (unchanged, > floor). **No sub-0.5 mm gap remains anywhere in this block** | **Pass (fixed this round — no exception needed)** |
| 14 *(auditor)* | Constraint (c) — anchor ICs move ≤ 3 mm — needs an explicit disposition even when N/A | Round-1 audit, carried forward | Whether this block has any anchor ICs | **N/A**: fixed anchors here (J701/J702/J703/SW701/SW702) are connectors/switches, not ICs | **Pass (N/A)** |
| 15 *(auditor)* | DRC dismissal must name every affected rule class | Round-1 audit, carried forward | Full class breakdown of `kicad-cli pcb drc --severity-all` on the placed board | **Re-run this round** (not merely carried forward, since C701 moved and rotated near J701's shroud): 870 violations total, identical 9-class breakdown to rounds 1/2 (`clearance` 500, `solder_mask_bridge` 199, `hole_clearance` 128, `lib_footprint_issues` 27, `footprint_type_mismatch` 9, `isolated_copper` 4, `courtyards_overlap` 1 pre-existing, `copper_edge_clearance` 1 pre-existing, `via_dangling` 1 pre-existing). Filtered for any violation naming C701: **0 hits** — the wider 0.6 mm gap produces no new clearance/solder-mask defect (round 2's tighter 0.13 mm gap already produced 0 hits; this round's compliant gap is strictly safer) | **Pass (re-verified, not just carried forward)** |
| 16 *(new, round 2, carried forward)* | Fixed anchor whose courtyard pokes past the block envelope is not a violation | PM ruling on this named exception (J400/J401/J701/SW703) — pre-existing, floorplan_v2.md line 68, independently corroborated by the round-3 audit's own bbox measurement (2.275 mm) | J701's courtyard (y down to 48.825) vs envelope y0=51.1 | J701 breaches by 2.275 mm — pre-existing, one of the four named exceptions, **not this block's doing, not movable** | **Pass (N/A, documented)** |

**rules_checked = 16, rules_failed = 0.** The one should-fix from the round-3 audit (row 13) is fixed with a compliant ≥0.5 mm gap everywhere in the block — no exception is invoked anywhere this round, closing the traceability concern the auditor raised about round 2's cited "PM ruling" (that citation is not reused; this round's courtyard gaps are compliant on their own merits). Both notes (rows re: J701 datasheet, TP701 edge citation) are dispositioned in §8/§9.

**Auditor:** PASS — no must-fix or should-fix. Two documentation-completeness notes (J701's datasheet
has no layout section — re-fetched a 5th time and still metadata-only; TP701's edge citation now exact
at 4.646 mm to the real `Edge.Cuts` polyline).


---

### 3.5 `emulator_core` — 47 refs · auditor verdict **pass** (0 must-fix, 0 should-fix, 4 notes) — **re-placed this round**

Envelope `[266.9, 89.6, 296.1, 116.9]`, no fixed anchors. 46 of 47 refs changed since v2.1 (`U200` alone is
bit-identical); the block was re-solved end to end around the RP2350 on-chip regulator loop by an escalated
Opus fixer, then independently re-audited (round 6).

**Sources** (all fetched/re-read by the placer, and independently re-fetched or re-read by the auditor):
*Hardware design with RP2350* RP-008280-DS-2 (§2.1, §2.2.1, §3.1, §4, §5.1, §5.4), the *RP2350 Datasheet*
(§1.2.1.1 Fig. 2, §6.3.8 / 6.3.8.1 / 6.3.8.2, erratum RP2350-E9), and — confirmed by the auditor to contain
**no** layout section, so `[FALLBACK]` correctly applies — Winbond W25Q128JV, Diodes AP2112K, Abracon
ABM8-272-T3.

**Checklist, quoted verbatim from `detail/placement_emulator_core.md` §2** (pad centre to pad centre;
courtyard gaps are real KiCad polygons, bbox convention, `BuildCourtyardCaches()` called first):

| # | rule | source | criterion | measured | pass |
|---|---|---|---|---|---|
| 1 | C_IN close to VREG_VIN | HW-RP2350 §2.1 p.5 *"As large currents are switched from VREG_VIN to VREG_LX, a large capacitor (C6) close to the input is required"*; DS §6.3.8.2 *"C_IN should be at least 4.7 μF"* | 4.7 µF, ≤ 3 mm to pin 49 | C213 4.7 µF, `3V3_EMU` pad → pin 49 = **1.859 mm** | **pass** |
| 2 | C_IN's own short GND path to PGND | DS §6.3.8.1 | C_IN GND pad ≤ 3 mm from pin 47 | C213 GND pad → pin 47 = **2.033 mm** | **pass** |
| 3 | Inductor adjacent to VREG_LX | DS §6.3.8.1 *"Reduce parasitics on the VREG_LX node"*; Fig. 23 | L pad to pin 48 as small as geometry allows (ref. layout ≈ 1–3 mm) | L200 `VREG_LX` pad → pin 48 = **3.617 mm** | **deviation, floor demonstrated (§4 D-1)** |
| 4 | C_OUT between the regulator pins, as close as practical | DS §6.3.8.1 *"It must be placed between VREG_VIN and VREG_PGND as close to the pins as practically possible"* | C_OUT GND ≤ 3 mm from pin 47, adjacent to L | C217 GND pad → pin 47 = **2.911 mm**; C217 `1V1_EMU` pad → L200 `1V1_EMU` pad = **1.827 mm**; courtyard gap C217–L200 = **0.050 mm** | **pass** |
| 5 | Second 4.7 µF on V_OUT at DVDD pin 23, away from LX/C_OUT | DS §6.3.8.1 *"…located on the bottom edge of the package (DVDD pin 23 on the QFN-60). Don't place this near LX/COUT"* | 4.7 µF at pin 23, far from L200/C217 | C216 `1V1_EMU` pad → pin 23 = **1.308 mm**; C216 → L200 courtyard = **7.931 mm** (2-D; round 4 quoted the 7.230 mm vertical component — correction C-1) | **pass** |
| 6 | VREG_FB fed from the C_OUT node, not routed under LX | DS §6.3.8.1 | FB pin's nearest C_OUT terminal, routable clear of L200 | pin 50 VREG_FB → C217 `1V1_EMU` pad = **5.066 mm**; L200 occupies y 89.655–91.845 at x 278.105–280.695, the FB pin is at (274.345, 91.418), so a route along y ≈ 92.4 reaches C217 without passing under L200 | **pass (placement permits it; routing is a later stage)** |
| 7 | VREG_AVDD RC-filtered, cap at the pin, its own GND return | HW-RP2350 §2.1 p.7 *"an RC filter of 33 Ω and 4.7 μF is adequate"*; DS §6.3.8.1 | C_FILT at pin 46; C_FILT GND not shared with C_IN/C_OUT | C215 `VREG_AVDD` pad → pin 46 = **3.419 mm**; R200 33 Ω `VREG_AVDD` pad → C215 = **4.560 mm**; C215's GND terminal is on the corridor's east side, **1.828 mm** from the nearest C_IN/C_OUT GND terminal (C217), so it can take its own via | **deviation, named (§4 D-2)**; via topology carried to routing (§0 N-1) |
| 8 | C_IN / L / C_OUT not on the opposite side of the PCB | DS §6.3.8.1 | all on F.Cu with U200 | C213, L200, C217, U200 all `side: F` | **pass** |
| 9 | 100 nF per power pin, close to the pin | HW-RP2350 §2.2.1 p.8 *"it is important to place decoupling close to the power pins… a 100 nF capacitor per power pin"* | every IOVDD/DVDD/USB_OTP_VDD/QSPI_IOVDD/ADC_AVDD pin ≤ 2 mm pad-to-pad from a same-rail capacitor pad | pin 1 **1.845** · 6 **1.798** · 11 **1.843** · 20 **1.597** · 23 **1.308** · 30 **1.294** · 38 **2.714** · 39 **1.987** · 44 **2.354** · 45 **1.964** · 49 **1.859** · 53 **2.197** · 54 **1.885** | **10 of 13 pass; 3 named deviations (§4 D-3, D-4, D-5)** |
| 10 | Pins 53/54 may share one capacitor when the regulator needs the space | HW-RP2350 §2.2.1 p.8 verbatim: *"In this design, pins 53 and 54 of RP2350A … share a single capacitor (C12 …), as there is not a lot of room on that side of the device, and the components and layout of the regulator take precedence."* | one 100 nF serving both | C212 serves pin 54 at **1.885 mm**, pin 53 at **2.197 mm** | **pass (the reference design's own documented compromise)** |
| 11 | QSPI wired directly to the flash, short connections | HW-RP2350 §3.1 p.10 | shortest practical U200 pin 60 → U201 pin 1 | **12.168 mm** | **deviation, named (§4 D-6)** |
| 12 | R1 / R6 (and R9/R10) close to the flash chip | HW-RP2350 §3.1 p.11 verbatim | ≤ 5 mm to a U201 pad | R202 (R1) **2.552** · R203 **3.083** · R204 (R6) **3.190** · D200 **3.263** | **pass** |
| 13 | Flash VCC decoupling at the flash | `[FALLBACK]` — the W25Q128JV datasheet has no layout section; standard practice 100 nF within 1–2 mm of VCC | C220 ≤ 2 mm from U201 pin 8 | C220 `3V3_EMU` pad → U201 pin 8 = **1.677 mm** (nearest U201 pad 1.664 mm) | **pass** |
| 14 | Crystal close to XIN/XOUT; keep the layout short | HW-RP2350 §4 p.13 *"…the parasitic capacitance of the PCB traces are a factor… Try and keep the layout as short as possible"*; working criterion ≤ 5 mm per resonant segment | each **net-matched** segment of the crystal loop ≤ 5 mm | `EMU_XIN`: U200 pin 21 → Y200 pin 1 = **3.388 mm**. `Net-(C222-Pad1)`: Y200 pin 3 → R201 pad 1 = **2.548 mm**. `EMU_XOUT` (driver side of the 1 kΩ, not in the resonant loop): U200 pin 22 → R201 pad 2 = **4.703 mm**. There is **no** direct XOUT pad-to-pad trace — R201 is in series (correction C-3) | **pass (all three ≤ 5 mm)** |
| 15 | Two equal load caps, one each side of the crystal, short matched traces | HW-RP2350 §4 p.13 verbatim: *"This load capacitance is achieved by placing two capacitors of equal value, one on each side of the crystal to ground (C3 and C4)"* | equal value; **signal** pad of each ≤ 2 mm from the crystal pin **on that same net**; the two legs matched | C221 = C222 = **15 pF** (schematic). C221 pad 1 (`EMU_XIN`) → Y200 pin 1 = **1.900 mm**; C222 pad 1 (`Net-(C222-Pad1)`) → Y200 pin 3 = **1.900 mm**; **mismatch 0.000 mm**. Both legs are straight horizontal runs with no pad of any other footprint within 0.30 mm of the centreline. (GND-pad distances, for contrast: 2.860 / 2.129 mm — not what this row claims) | **pass** |
| 16 | 1 kΩ series damping resistor in the XOUT leg | HW-RP2350 §4 p.13 *"a 1 kΩ series resistor (R2) … to prevent the crystal being over-driven"* | R201 = 1 kΩ, in series in the XOUT leg, close to the crystal node | R201 **1 kΩ**; pad 1 on `Net-(C222-Pad1)` **2.548 mm** from Y200 pin 3; pad 2 on `EMU_XOUT` **4.703 mm** from U200 pin 22 (round 4 quoted 3.815 mm, which was the chip-side pad measured to the crystal pin — correction C-2) | **pass** |
| 17 | Keep the switching node away from the crystal | `[FALLBACK]` — neither document gives a number; PM rule (4) sets ≥ 5 mm | L200 / VREG_LX ≥ 5 mm from Y200 | L200 courtyard → Y200 courtyard = **9.170 mm**; centre-to-centre **13.306 mm** | **pass** |
| 18 | USB series resistors close to the chip | HW-RP2350 §5.1 p.15 | R703/R704 (bench_io_cable) adjacent to pins 51/52 | not this block's refs; their floorplan_v2 positions (272.845 / 274.645, 89.1) are honoured and worked around | **n/a (respected)** |
| 19 | LDO input capacitor at VIN | `[FALLBACK]` — AP2112K's layout note is a generic "place C_IN/C_OUT as close as possible to the IC"; applied as ≤ 2 mm | C200/C201 ≤ 2 mm to a U202 VIN pad | C201 100 nF **1.869 mm**; C200 1 µF **1.788 mm** | **pass** |
| 20 | LDO output capacitor at VOUT | same `[FALLBACK]` | C202/C203 ≤ 2 mm to U202 pin 5 | C203 100 nF **1.578 mm**; C202 10 µF **3.393 mm** | **partial — HF cap passes, bulk named in §4 D-7** |
| 21 | Test points reachable at a block edge with probe clearance | placement constraint (g) | on a block edge, ≥ 0.5 mm courtyard gap all round | TP200 (VBUS_EMU) nearest C202 **0.860**, TP201 (3V3_EMU) nearest R211 **0.839**, TP202 (1V1_EMU) nearest **C303 0.549**, TP203 (EMU_GPIO_RSVD) nearest **U302 0.565**; TP200/201 0.205 mm from the east envelope edge, TP202/203 1.104 mm from the south edge (correction C-4: the scan is now all-board, not intra-block) | **pass** |
| 22 | RP2350-E9 external GPIO pull-downs present | DS erratum **RP2350-E9** — requires an external pull-down on affected inputs; states no placement distance | R208/R209/R210 4.7 kΩ on the spare GPIOs | R208 → pin 32 **8.960**, R209 → pin 33 **11.368**, R210 → pin 37 **14.315** | **pass (DC pull-downs, no distance requirement)** |
| 23 | RUN pull-up near the RUN pin | `[FALLBACK]` — HW-RP2350 §5.4 shows the network but gives no distance; applied as ≤ 8 mm on the same side | R205 near pin 26 | **6.060 mm** | **pass** |
| 24 | All block parts inside the envelope | constraint (a) | real courtyard bbox inside [266.9, 89.6, 296.1, 116.9] | **0 of 47 outside** | **pass** |
| 25 | No courtyard overlap with anything on the board | constraint (d), `apply_placement.py` real polygons | 0 overlaps | **0** | **pass** |
| 26 | ≥ 0.50 mm courtyard-to-courtyard except PM-accepted trades | constraint (h) + PM ruling | complete sub-0.5 mm table disclosed | **11 intra-block pairs, all accepted trades; 0 cross-block — §3** | **pass** |
| 27 | Heritage frozen, nothing new inside the Rev2 outline | constraint (f) | `heritage.py check … --allow-zone-growth --allow-edge` = 0 | **0 violations** | **pass** |
| 28 | Attachment reach to the FC pads not worse by > 3 mm | constraint (c) / brief L11 | `attachment_check.py` = 0 violations, 0 warnings | **0 / 0** | **pass** |
| 29 | Anchor ICs move ≤ 3 mm | constraint (c) as amended | U200 / U201 / U202 / Y200 | U200 **0.000**, U201 **1.500**, U202 **0.000** (rot 0 → 180), Y200 **2.725** | **pass** |
| 30 | 12.6 mm L3 lane free of parts > 2 mm tall | constraint (e) | lane x 231.4–244 | no emulator_core part is west of x 266.9 | **pass (n/a)** |
| **31** | **AUDIT-R5 §1 — load-cap network genuinely symmetric, measured net-to-net** | AUDIT-R5 §1 (source: HW-RP2350 §4 p.13) | the two capacitors' **signal-net** pads equidistant from their crystal pins | **1.900 mm / 1.900 mm, mismatch 0.000 mm** (§0 SF-1) | **pass** |
| **32** | **AUDIT-R5 §2 — VREG_PGND single-point GND return, 2 adjacent vias, C_FILT on its own via** | AUDIT-R5 §2 (source: HW-RP2350 §6.3.8.1) | not decidable at placement; distances done, topology specified for routing | C213 GND **2.033 mm**, C217 GND **2.911 mm** from pin 47; C215's GND terminal isolated on the corridor's east side. Routing instruction recorded in §0 N-1 | **carried forward (not a placement defect)** |
| **33** | **AUDIT-R5 §3 — copper cut away under L200 / VREG_LX** | AUDIT-R5 §3 (source: HW-RP2350 §6.3.8.1, Fig. 24) | pour/keepout instruction for the refill stage | L200 courtyard [278.105, 89.655]–[280.695, 91.845] recorded as the keepout rectangle in §0 N-2 | **carried forward (not a placement defect)** |

**Rules checked 33 · rules failed 0 · named deviations 7 (§4) · routing/pour items carried forward 2.**

**Named deviations kept (D-1…D-7), each a demonstrated floor, none a datasheet-number miss** — the RP2350
documents' own wording for these is qualitative ("reduce parasitics", "as close as practically possible"),
so every one of the seven is a miss against the *report's own* working target:

- **D-1** `L200` 3.617 mm from pin 48 `VREG_LX` (self-set target ≈1–3 mm). The only strip closer to pin 48
  is 1.09 mm tall and L200's courtyard is 2.19 mm in its shortest dimension — physically impossible. Taking
  the closer east slot would displace `C213` (C_IN), which DS §6.3.8.1 calls critical. A trade between two
  datasheet priorities, resolved the way the document ranks them.
- **D-2** `C215` (C_FILT) 3.419 mm from pin 46 `VREG_AVDD`; the north slot it wants is held by C_IN.
- **D-3/D-4/D-5** pins 38 / 44 / 53 decoupled at 2.714 / 2.354 / 2.197 mm against a 2 mm working target;
  the corridor between U200 and U201 is 3.96 mm and fits exactly one 0402 column, allocated in
  datasheet-priority order. D-5 is the reference design's **own documented** pin-53/54 shared-cap compromise.
- **D-6** QSPI_SS run U200 pin 60 → U201 pin 1 = 12.168 mm. Follows from the owner-accepted block plan
  (U200's QSPI pins are on its north edge; the SOIC-8 flash only fits east) plus the 1.5 mm of anchor budget
  already spent opening the strip that fixed the crystal.
- **D-7** LDO bulk cap `C202` 3.393 mm from `U202` pin 5. The 180° rotation that puts the 100 nF output cap
  at 1.578 mm and both input caps under 1.9 mm is the only one that gets all three; at rot 0 the output caps
  reach no closer than 3.47 mm.

**PM-accepted trades:** 11 intra-block courtyard pairs below 0.5 mm — 0.135 mm × 3 (`C210`, `C212`, `C213`
against U200's north edge, pins 1 / 53-54 / 47-49), 0.150 mm (`C217` C_OUT against `L200`, which DS §6.3.8.1
explicitly wants), 0.155 mm × 5 (`C206`, `C207`, `C209`, `C216` against U200's south edge; `C220` against
U201 pin 8), 0.320 / 0.340 mm (`C200` / `C203` against U202's VIN / VOUT). At a 0.135 mm courtyard gap the
real copper separation is ≈ 0.70 mm (the QFN-60's courtyard carries 0.665 mm of margin beyond its pads).
**0 cross-block pairs.** (My full-board real-*polygon* scan reports these 0.100 mm higher than the block's
own bbox-convention numbers; both methods are disclosed and neither changes a verdict.)

**Auditor's verdict** (`detail/audit_emulator_core.md`, round 6, independent Sonnet, role = refute):
**PASS — 0 must-fix, 0 should-fix, 4 notes.** The auditor rebuilt the board from scratch (0 position
mismatches across all 47 refs against the delivered file), re-scanned all 218 footprints for courtyard gaps
(same 11 pairs, same values to the ten-thousandth, 0 undisclosed, 0 cross-block), re-derived the crystal
fix from raw pad coordinates (1.9000 / 1.9000 mm, mismatch 0.0000 mm), re-exported the netlist to confirm
`R202 ≡ R1` and `R204 ≡ R6` rather than trusting the report's labelling, and re-read the RP2350-E9 errata
text to confirm the 4.7 kΩ pull-downs clear its actual 8.2 kΩ threshold. The four notes are: N-1 the
`VREG_PGND` single-point-return / two-adjacent-via / C_FILT-isolation **routing** instruction, N-2 the
copper cutout under `L200` / `VREG_LX` for the **pour** stage (neither decidable on an unrouted board),
the D-1…D-7 spot-check (declined to escalate), and a new informational one for fab prep: the scratch
project's `fp-lib-table` does not list the custom `RP2350_60QFN_minimal` library, and `U200`'s footprint
carries a stale "Through hole" component-type attribute — both are project-config facts, not placement
defects, and both are visible in this integration's own DRC as `lib_footprint_issues` /
`footprint_type_mismatch` (§4).

**Integration disposition:** accepted as delivered. The block's re-place forced three stitching points to
move (§5.1) and nothing else; no cross-block gap, no envelope breach, no reach change.


---

### 3.6 `face0_reference` — 16 refs · auditor verdict **pass** (0 must-fix, 0 should-fix, 2 notes)

> **Unchanged since v2.1 — 0 refs moved this round.** Section carried forward verbatim.


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

**Auditor:** PASS — both round-0 should-fix findings resolved; two informational notes (a razor-thin
0.504 mm clearance pair, and a U303 footprint-family naming mismatch that predates this stage).
Unchanged since the previous integration.


---

### 3.7 `strip_left_pyro_shunts` — 20 refs (3 movable) · auditor verdict **pass** (0 must-fix, 0 should-fix, 2 notes)

> **Unchanged since v2.1 — 0 refs moved this round.** Section carried forward verbatim.


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

**Auditor:** PASS. Unchanged since the previous integration.


---

### 3.8 `vsolar_injection` — 11 refs (3 movable) · auditor verdict **pass** (0 must-fix, 0 should-fix)

> **Unchanged since v2.1 — 0 refs moved this round.** Section carried forward verbatim.


| # | Rule | Source | Criterion | Measured (on rebuilt board) | Pass/Fail |
|---|---|---|---|---|---|
| R1 | PTC fuse: shall be provided with adequate space around the device body and protected against mechanical stress (thermal expansion under fault conditions) | Littelfuse 2920L Series PolySwitch® Resettable PPTC Datasheet, **Warnings** section (p.6): *"These devices undergo thermal expansion under fault conditions, and thus shall be provided with adequate space and be protected against mechanical stresses."* **Fix round 1:** re-sourced from the real document — independently re-fetched (`farnell_2920l.pdf`, 448 KB valid PDF, `pdftotext`), the quote confirmed present verbatim at line 465 of the extracted text (`farnell_2920l.txt`), corroborated by an independent web search returning the same sentence. The round-1 citation ("no via/trace/nomenclature under the device") is **withdrawn** — it does not occur anywhere in this datasheet (confirmed by the independent auditor and by my own grep of the same extracted text) | No frozen stitching via (or other fixed via/trace) falls inside F400's/F401's courtyard, **and** F400/F401 hold ≥0.5 mm courtyard-to-courtyard clearance to every neighboring footprint (this board's own standard for "adequate space", brief constraint (h), since the datasheet gives no numeric threshold) | Nearest frozen stitching point to F400 is 7.395 mm away, to F401 is 9.383 mm away (0 of 65 stitching points inside either courtyard — re-measured on the fix-round-1 rebuild). F400/F401 nearest-neighbor courtyard gaps: D400↔F400 0.820 mm, D401↔F401 0.820 mm, D400↔F401 0.857 mm, F400↔F401 1.350 mm, F400↔JP401 1.180 mm — all ≥0.5 mm | **PASS** |
| R2 | Series diode oriented so its cathode/anode pads face the parts they connect to (short loop, no reversed pin forcing a trace over the part body); specifically, **Schottky anode toward the source** | `sheet_solar_power_injection.md` §2, this sheet's own explicit rule: *"Schottky (anode toward source)"* — a project-specific rule, cited in preference to the round-1 general fallback ("general Schottky-rectifier / series-protection-chain layout practice"), which is kept as secondary corroboration only (Comchip's CDBA240LL-HF datasheet has no PCB-layout section reachable via WebFetch — 403/HTML-block on every mirror tried, re-confirmed by the independent auditor) | D400/D401's anode pad (net `Net-(D40x-A)`) sits on the side facing its own fuse (F400/F401, the source), not the jumper side; pad-to-pad chain length J400.1→F400.1→(F400.2/D400.2)→D400.1→JP400.1 (and the CH-B equivalent) does not exceed the v1 baseline | D400 anode pad (pin2, `Net-(D400-A)`) sits at x=234.0, 0.8 mm from F400's pad2 at x=237.188 (source-side, correct — cathode pin1 is now at x=238.0, facing JP400); D401's anode pad (pin2) already sat at x=246.5, 1.29 mm from F401's pad2 at x=247.787 (already correct, no rotation needed). CH-A chain: v1 = 35.045 mm (10.204 + 5.659 + 19.182); after 180° D400 rotation = 31.930 mm (10.204 + 6.444 + 15.283), **-3.115 mm (-8.9%)**. CH-B: unchanged at 32.721 mm both before and after | **PASS** |
| R3 | Placement change does not regress any chain's terminal→jumper path (electrical order preserved, no new hop longer than v1) | Derived from R2 / general series-chain practice, checked against this specific board's frozen anchor geometry | No hop in either chain is longer after this pass than in v1 | CH-A: all three hops shorter or equal (10.204=10.204, 6.444<5.659 -- see note below, 15.283<19.182). CH-B: identical (10.110, 5.746, 16.865 in both v1 and this pass; F401/D401 unmoved). **Note:** the F400.2→D400.2 hop grew slightly (5.659→6.444 mm, +0.79 mm) because the 180° rotation that shortens the far more important D400.1→JP400.1 hop (-3.9 mm) also swaps which pad is nearest F400; net chain length is still shorter overall (R2) | **PASS** |
| R4 | Test points sit where a probe can reach (brief constraint g: block edges) with ≥0.5 mm courtyard clearance from every neighbor | Brief §"PLACEMENT CONSTRAINTS" (g)/(h) | Courtyard-to-courtyard gap ≥ 0.5 mm to every neighboring footprint; no footprint sits above the test point on the same face | TP400↔D400 gap 2.009 mm; TP402↔D401 gap 2.320 mm; TP402↔D400 gap 2.009 mm; TP401↔JP400 gap 0.890 mm; TP400↔J400 gap 13.749 mm. All three sit in a clear row at y=144.5, 2.5 mm inside the envelope's north edge (envelope y0=142), open above them (F.Cu, nothing on top) | **PASS** |
| R5 | The passive move must not worsen the L11 attachment reach (FC pad → nearest new pad on the shared net) by more than 3 mm | Brief §L11 / `floorplan.md` §5 attachment table (this block's only listed row: `VSOLAR` J11.1 → TP401.1, 31.1 mm) | \|reach_after − reach_before\| ≤ 3 mm, measured pad-centre to pad-centre with pcbnew | v1: min(JP400.2=39.340, JP401.2=31.617, TP401.1=31.123) = **31.123 mm** via TP401. After: TP401 moved to (248.8,144.5) → TP401.1 is now 33.864 mm from J11.1, so the *nearest* pad on the shared `VSOLAR` net becomes the frozen JP401.2 at **31.617 mm** (JP401 did not move). Net reach change: **+0.494 mm** | **PASS** (0.494 mm ≪ 3 mm budget) |
| R6 | Screw-terminal / jumper mechanical accessibility (board-edge access for wire insertion, top access for a 2.54 mm shunt) unchanged | Brief §6.3 + standard connector layout practice; these four are fixed anchors, not touched by this pass | J400/J401/JP400/JP401 position and rotation identical to v1 (already gated 0 overlaps in the accepted v1 floorplan) | Verified on the rebuilt board: J400 (228.96,165.3,0°,F), J401 (241.46,165.3,0°,F), JP400 (252.8,145.79,0°,F), JP401 (226.2,153.93,0°,F) — bit-for-bit the v1 values | **PASS** |

**Auditor's rules (added, fix round 1)** — `audit_vsolar_injection.md` §3's lettered PLACEMENT CONSTRAINTS + ruling F3, re-measured independently on the fix-round-1 rebuild (`placed2.kicad_pcb`), not copied from the audit:

| # | Rule | Source | Criterion | Measured (on fix-round-1 rebuild) | Pass/Fail |
|---|---|---|---|---|---|
| R7 | (a) every part of the block stays inside the block envelope | Brief PLACEMENT CONSTRAINTS (a); envelope_mm [223.2,142,255.8,168.3]. **Fix round 2:** PM ruling ("A fixed anchor whose courtyard pokes past the block envelope (J400/J401/J701/SW703 — the envelope was computed from part centres) is NOT a violation. Do not move it; say so in the .md.") supersedes the round-1 FAIL disposition for this exact pair of refs | 9/11 F_CrtYd courtyard bboxes fully inside the envelope; J400/J401 accepted as a named PM exception rather than measured against strict containment | 9/11 inside (D400, D401, F400, F401, JP400, JP401, TP400, TP401, TP402), re-confirmed on `placed3.kicad_pcb`. J400/J401 courtyard y-max = 170.425 mm, 2.125 mm south of the envelope's y1=168.3 — bit-identical to v1/frozen-anchor position (constraint (b) forbids moving them; the PM ruling forbids it too). Board's own Edge.Cuts extends to y=172.17 mm here, so both stay physically on-board at the true south edge, not overlapping anything (0 overlaps, gate above) | **PASS (PM-accepted anchor/envelope exception — not moved, not a deviation)** |
| R8 | (d) no courtyard overlap with any part of any block; nothing outside the outline (gate) | Brief PLACEMENT CONSTRAINTS (d); `apply_placement.py` real-polygon check | `courtyard overlaps: 0`, `footprints not fully inside the outline: 0` | Re-run on `placed2.kicad_pcb`: `applied 218; refused (heritage) []; missing refs []`; `footprints not fully inside the outline: 0: []`; `courtyard overlaps (same-side, ≥1 new part; real polygons): 0: []`; exit 0 | **PASS** |
| R9 | (e) 12.6 mm L3 lane (rect [231.39, 47.579, 243.39, 141.2] per `floorplan.json` `lanes[0]`) stays free of parts >2 mm tall | Brief PLACEMENT CONSTRAINTS (e); block-level lane definition, unmodified by this pass | No part of this block's envelope (y≥142) overlaps the lane's y-range (≤141.2) | This block's northernmost parts (TP400/TP401/TP402) sit at y 143.225–145.775, 2.025 mm south of the lane's y1=141.2 — no overlap | **PASS / N/A** (block does not reach the lane) |
| R10 | (f) heritage frozen; no new part inside the Rev2 outline | Brief PLACEMENT CONSTRAINTS (f); `heritage.py check ... --allow-zone-growth --allow-edge` | `heritage check: 0 violation(s)` | Re-run on `placed2.kicad_pcb`: 0 violation(s) (only expected zone-reshape/edge notes and new-item notes for the 221 new footprints/65 tracks/4 zones staged east of the Rev2 outline); exit 0 | **PASS** |
| R11 | F3 ruling: support passives (this block has no ICs, but the ruling's F.Cu requirement applies to all passives) stay on F.Cu | Brief §12 ruling F3 | All 11 refs `side: F` in the merged placement spec | Confirmed on `placed2.kicad_pcb`: all 11 footprints report `F.Cu` as their layer | **PASS** |

**rules_checked = 11, rules_failed = 0** (fix round 2: R7/(a) — the J400/J401 vs. envelope mismatch — is now a PM-accepted named exception, not a violation, per the round-2 ruling quoted above; see §4 Deviations and §6 Fix round 2 for the disposition. All 11 rows now pass clean.)

**Auditor:** PASS — the round-1 must-fix (J400/J401 courtyards past the envelope) is closed as the
PM-named fixed-anchor exception, not a geometry change. Unchanged since the previous integration.


---

### 3.9 `charger_bq25886` — 29 refs (27 movable) · auditor verdict **pass** (0 must-fix, 0 should-fix, 4 notes) — **fixed this round**

Envelope `[254.3, 141.8, 294.5, 171.9]`, fixed anchors `J510`/`JP510` (both bit-identical, Δ 0.0000 mm),
anchor IC `U511` Δ **0.000 mm**. Six refs changed since v2.1: `R510`/`R511` (the CC pull-downs, relocated in
round 4 — v2.1 predated that fix and carried the round-3 positions), `R516`/`R517`/`R518` (the REGN-RT1-TS-RT2
divider column, +0.26 mm as a group, also round 4) and `L510` (+0.130 mm in x, round 5).

**Sources:** BQ25886 — **TI SLUSD88A**, §11.1 "Layout Guidelines" (the 7-item numbered priority list,
transcribed verbatim and independently re-transcribed by the auditor from the rendered page image) and
§11.2 Fig. 35 "Layout Example", plus the p.4-5 pin table (independently cross-checked pin for pin).
DZDH0401DW — Diodes **DS42784 Rev.3-2**, read page by page and confirmed to contain **no** PCB-layout
section anywhere, so the fallback stands. USB Type-C CC pull-down ≤ 5 mm — the round-4 PM numeric criterion.

**Checklist, quoted verbatim from `detail/placement_charger_bq25886.md` §2** (courtyard gap = real
`GetCourtyard()` rectangle-to-rectangle Euclidean distance; pad distance = pad centre to the nearest
candidate same-net pin):

| # | Rule | Source | Criterion | Measured (this round) | Pass/Fail |
|---|---|---|---|---|---|
| 1 | "Put SYS output capacitor as close to SYS and GND pins as possible" | §11.1 priority 1 | Nearest SYS cap, pad‑to‑nearest‑pin | **C513 → nearest(pin15/16) = 4.512 mm**, courtyard gap 0.301 mm | **PASS** |
| 2 | "Place PMID input capacitor as close as possible to PMID and PGND pins" | §11.1 priority 2 | C511 pad‑to‑PMID‑pin | **1.879 mm**, courtyard gap 0.280 mm (unchanged) | **PASS** |
| 3 | "Place inductor input terminal to SW pins as close as possible… minimize copper area" | §11.1 priority 3 | L510 SW‑side pad to nearest SW pin | **4.021 mm** (was 3.946 mm — +0.075 mm from this round's +0.13 mm x‑move, still tight/reasonable for a boost/buck inductor), courtyard gap to U511 **0.560 mm** (was 0.430 mm — fixed, §8.12) | **PASS (guideline intent preserved, courtyard gap now also passes)** |
| 4 | "Decoupling capacitors should be placed on the same side of and next to the IC, trace as short as possible" | §11.1 priority 4 | Courtyard gap to U511, all 9 caps, each individually | C510 0.280, C511 0.280, C512 0.300, C513 0.301, C516 0.300 — **5 of 9 at 0.28–0.30 mm**; C515 3.832, C514 5.290, C518 6.729, C517 7.616 mm (unchanged) | **PASS (4 caps disclosed farther, §4)** |
| 5 | "Route analog ground separately… tie at the thermal pad" | §11.1 priority 5 | Not a placement action | N/A — pins 4/19/20/25(EP) are the only U511 GND pins | **N/A (placement stage)** |
| 6 | "Exposed thermal pad soldered to PCB ground, sufficient thermal vias" | §11.1 priority 6 | Routing‑stage | Footprint's EP pad unchanged | **N/A (placement stage)** |
| 7 | "Via size/number sufficient for current path" | §11.1 priority 7 | Routing‑stage | N/A | **N/A (placement stage)** |
| 8 | Ideal‑diode controller: DRAIN/SOURCE sense the pass FET's D/S (Kelvin), BIAS drives the gate | DZDH0401DW p.5 | U510→Q510 cluster intact | Unchanged | **PASS** |
| 9 | Rbias/Rref close to BIAS/REF pins | DZDH0401DW p.5 | R512→BIAS, R513→REF | R512→pin3 **4.416 mm**; R513→pin2 **5.149 mm** (unchanged) | **PASS** |
| 10 | USB‑C CC1/CC2 pull‑downs close to J510's CC pins | USB Type‑C spec + round‑4 PM ruling (≤5 mm) | R510→CC1, R511→CC2, pad‑to‑pin | **R510: 2.390 mm; R511: 2.390 mm** (unchanged since round 4) | **PASS (unchanged)** |
| 11 | Ruling F3: passives stay on F.Cu | Brief §12 ruling F3 | All 27 placed refs `side: F` | Confirmed | **PASS** |
| 12 | BTST cap inherits the SW‑node "minimize copper area" rule | §11.1 priority 3 + pin table BTST row | C512's SW‑leg / BTST‑leg pad‑to‑pin, both stated | **SW‑leg 2.997 mm; BTST‑leg 3.115 mm** (unchanged) | **PASS** |
| 13 | BAT cap "closely to the BAT pin and GND" | BQ25886 pin table, BAT row | C515 pad‑to‑nearest(pin13/14) | **7.143 mm**, courtyard gap 3.832 mm (unchanged) | **DISCLOSED, §4** |
| 14 | ICHGSET/REGN not the farthest south‑row items without reason | General practice + REGN pin‑table bypass instruction | R515→ICHGSET, C516→REGN vs. R514/R516 | **R515→pin10 6.921 mm; C516→pin11 3.316 mm** (courtyard gap 0.300 mm, unchanged); R514 (ILIM) 10.549 mm, R516 (REGN pad) 10.977 mm, R516 (TS pad) 9.079 mm | **PASS** |
| 15 | R512/R513 courtyard‑to‑courtyard routing room | Brief constraint (h), ≥0.5 mm | Real rect‑to‑rect gap | **0.650 mm** (unchanged) | **PASS** |
| 16–21 | *(round‑1/2 audit items, all previously fixed — history preserved)* | — | — | — | **RESOLVED — see round‑2/3 deliveries, unchanged since** |
| 22 | D510↔U511 courtyard gap (round‑3 should‑fix, fixed round 3) | Round‑3 audit §3.1 | Real rect‑to‑rect gap, ≥0.5 mm | **0.570 mm** (unchanged this round) | **PASS (unchanged)** |
| 23 | C515↔C518 courtyard gap (round‑3 should‑fix, fixed round 3) | Round‑3 audit §3.2 | Real rect‑to‑rect gap, ≥0.5 mm | **0.550 mm** (unchanged this round) | **PASS (unchanged)** |
| 24 | R517↔U511 courtyard gap (round‑4 should‑fix, fixed round 4) | Round‑4 audit | Real rect‑to‑rect gap, ≥0.5 mm | **0.560 mm** (unchanged this round — the block‑specific PM note repeated in this round's task packet was already satisfied by round 4; re‑confirmed here) | **PASS (unchanged)** |
| 25 | J510↔R510 / J510↔R511 courtyard gaps (round‑4 should‑fix, fixed round 4) | Round‑4 audit | Real rect‑to‑rect gap, ≥0.5 mm, and ≤5 mm to CC pin | **J510↔R510 0.550 mm, J510↔R511 0.550 mm; R510→CC1 2.390 mm, R511→CC2 2.390 mm** (all unchanged this round — re‑confirmed) | **PASS (unchanged)** |
| 26 | *(round‑5 audit, should‑fix)* L510↔U511 courtyard gap 0.430 mm, inductor, no cap exemption applies per carve‑out wording | This round's audit finding (quoted above); consistent with prior self‑disclosure in §4 rounds 1‑4 | Real rect‑to‑rect gap, ≥0.5 mm | **L510 moved +0.13 mm in x (284.00→284.13, y/rot/side unchanged). New gap: 0.560 mm** (was 0.430 mm) — see §8.12 | **FIXED** |
| 27 | *(round‑5 audit, note)* R515 documentation‑table label said "5.7 kΩ", schematic/footprint value is 5.62 kΩ | This round's audit finding (quoted above) | Doc‑table value matches schematic note + placed `Value` field | **Table corrected to 5.62 kΩ in §1/§1a — not a placement defect; no pad‑distance number changes** | **FIXED (documentation)** |
| 28 | *(round‑5 audit, note)* GND‑side pads of C514/C515/C517/C518/R516/R517/R518 all sit inside the filled F.Cu ground pour — favorable disclosure, not a defect | This round's audit finding (quoted above) | `zone.HitTestFilledArea()` against `GND_F_Cu_wing` | Re‑confirmed this round on `placed7.kicad_pcb`: every one of those refs' GND pads sits inside the filled pour footprint (0 mm hot‑to‑plane trace‑length cost for ground return; only the hot‑side distances in row 4/§4 are real costs) | **N/A — favorable note, no action** |
| 29 | *(round‑5 audit, note)* J510 has no ESD/TVS part — schematic‑author decision, outside placement scope | This round's audit finding (quoted above); consistent with rounds 3/4's identical note | Whether an ESD/TVS device exists among the 29 refs | Reconfirmed a **fifth** consecutive round: none of the 29 refs is an ESD/TVS part; `battery_protection_replica.kicad_sch` labels J510 "USB‑C, power only" | **N/A — no part to place, unchanged** |

**Rows not independently measurable / not applicable at the placement stage:** #5–#7 (analog/power‑ground separation, thermal‑via count, via sizing) are routing/fab actions.

**Deviations kept (2, both disclosed since round 1):**

1. **Not all 9 decoupling caps can sit at ≈0.3 mm.** Four 3.2 × 2.5 mm 1210 SYS caps plus a fifth 1210 (BAT)
   cannot all be adjacent to a 6-pin band 2.5 mm tall. Every net with **no redundant partner** (PMID, VBUS,
   both BTST legs, REGN) is at a true 0.28–0.30 mm courtyard gap; only the three *redundant* SYS caps
   (`C514`, `C517`, `C518`) sit farther out at 5.290 / 6.729 / 7.616 mm gap.
2. **BAT cap `C515` is 7.143 mm from its nearest BAT pin.** Giving BAT the closest slot would demote `C513`,
   the numbered §11.1 priority-1 SYS representative, to satisfy an unnumbered pin-table line. Disclosed
   rather than silently taken.

**Items closed this round:** `L510↔U511` 0.430 → **0.560 mm** (the round-5 should-fix, fixed by geometry, not
by stretching the capacitor carve-out over an inductor: L510 moved +0.13 mm in x only, SW-pad cost
+0.075 mm, `L510↔C512` unchanged at 0.340 mm because that pair is y-governed); `R517↔U511` **0.560 mm** and
`J510↔R510`/`J510↔R511` **0.550 mm** (the two pairs v2.1 listed as open should-fix — they were already fixed
in round 4, and v2.1 simply predated that delivery); `R515`'s documentation label corrected to 5.62 kΩ
(E96; no pad number changes — every distance was always computed from the correctly-valued placed part).

**PM-accepted trades:** 8 intra-block courtyard pairs below 0.5 mm by my real-polygon scan (the block's own
bbox-convention scan reports 10, 0.100 mm tighter): `C511↔U511` 0.380, `C512↔C513` / `C512↔U511` /
`C513↔C514` / `C516↔U511` 0.400, `C510↔C511` / `C510↔D510` 0.430, `C512↔L510` 0.440 mm. Every one is a
capacitor against the specific pin(s) it decouples or bypasses. **0 cross-block pairs.**

**Auditor's verdict** (`detail/audit_charger_bq25886.md`, round 6, independent Sonnet): **PASS.** The
auditor fetched the BQ25886 PDF live and read pages 4-5 and 31-32 as page images rather than trusting any
summary, read all 10 pages of the DZDH0401DW datasheet from the cached copy, re-derived every pad position
and courtyard gap with a script written fresh this round (every spot-checked number matched the report's own
figure to the same precision — "no fabricated or rounded-away measurement found"), re-ran the whole canonical
pipeline from a fresh copy of the live board, and extended the gap scan to all 483 board-wide footprints
(zero real or sub-0.5 mm overlaps beyond the already-known, non-block-caused `JP400↔JP510` at 0.870 mm).
Four notes: (a) **new** — `Q510`'s `U-DFN2020-6E` land pattern has 0.19 mm adjacent different-net pad
spacing, 0.01 mm under the project's blanket 0.2 mm `Default` netclass clearance, producing 3 real DRC
clearance errors that **no placement choice can fix** (Q510 has not moved in any round); the fix is to list
`Q510` in `FlatSat_V1.kicad_dru`'s existing `fine-pitch-pad-pitch` rule, whose 0.127 mm floor is JLCPCB's
real minimum — stage 3 or 5. (b) `R515` label, fixed. (c) favourable: `C514`/`C515`/`C517`/`C518`/`R517`/
`R518`'s GND pads all sit **inside** the filled `GND_F_Cu_wing` pour (0 mm ground-return cost), verified with
`zone.HitTestFilledArea()`. (d) carried forward for a 6th round: `J510` has no ESD/TVS part — a Phase-1
schematic decision for a power-only bench USB-C input, outside a placement pass's scope.

**Integration disposition:** accepted as delivered. No cross-block effect; the six moved refs changed no
stitching point and no attachment reach (this block has no L11 entry — its only path to a flight net is the
normally-open `JP510` jumper).


---

## 4. DRC — every class, with a disposition

```
section            sev      type                             base    now  delta
schematic_parity   warning  extra_footprint                     1      1     +0
schematic_parity   warning  footprint_symbol_mismatch           5      5     +0
schematic_parity   warning  missing_footprint                 199      5   -194
schematic_parity   warning  net_conflict                       36      0    -36
unconnected_items  error    unconnected_items                   0    383   +383
violations         error    clearance                           0      7     +7
violations         error    courtyards_overlap                  1      1     +0
violations         warning  footprint_type_mismatch             7      9     +2
violations         warning  isolated_copper                     4      4     +0
violations         warning  lib_footprint_issues                3     21    +18
total baseline 256, now 436
errors: 391  unconnected: 383  parity: 11
```

Byte-for-byte the same profile as v2.1 — the two re-placed blocks introduced no new DRC class and cleared none.

| Class | Now | Δ vs baseline | Disposition |
|---|---|---|---|
| `schematic_parity` (all four types) | **11** | **+0 in every class** | Exactly the brief §6 FC baseline: H1/H2 no footprint field, R26/R27 BOM-exclude, U10 HTSSOP footprint-vs-symbol, TP9–TP13 no footprint, one extra footprint. **Zero parity items come from the 218 placements.** The 199→5 and 36→0 deltas are the Phase-1 sync landing. |
| `unconnected_items` | 383 | +383 | Expected floorplan-stage state — nothing is routed. Goes to 0 in stage 4. |
| `clearance` (error) | 7 | +7 | **All intra-footprint pad-to-pad**, confirmed by pulling each item's two sub-item positions out of the DRC json: 4 inside `U301` (TMP112 DFN, 0.15 mm, at 269.51/270.94 × 127.76–128.76) and 3 inside `Q510` (U-DFN2020-6E, 0.19 mm, at 269.51–270.49 × 155.1–156.9). A property of the packages, not of where the parts sit — a rigid translation or rotation cannot change a footprint's own pad spacing — and exactly the class `FlatSat_V1.kicad_dru` already exempts for U7/U15/U8/U16 via `memberOfFootprint`, down to JLCPCB's real 0.127 mm floor. **Fix: add `U301` and `Q510` to that rule — two lines, stage 3 or 5.** No placement change can clear them. |
| `courtyards_overlap` (error) | 1 | +0 | The accepted Rev2 heritage item only (`SW2`/`TP2` at (194.2, 85.2–86.0)), confirmed from the item's own sub-items. Independently: **0 overlaps among the 218 new parts and 0 new-vs-heritage** (`apply_placement.py`, real polygons). |
| `footprint_type_mismatch` (warning) | 9 | +2 | `U200` marked through-hole with SMD pads, `U302` the reverse — a schematic symbol attribute, not layout. Stage 6/7. |
| `isolated_copper` (warning) | 4 | +0 | Heritage zones, unchanged (all four at heritage coordinates). |
| `lib_footprint_issues` (warning) | 21 | +18 | New footprints differing from, or whose library is absent from, the scratch project's `fp-lib-table` — includes the `RP2350_60QFN_minimal` gap the `emulator_core` auditor flagged for fab prep (§3.5). Triage, not a defect. |
| `copper_edge_clearance`, `hole_to_hole`, `via_dangling`, `solder_mask_bridge` | 0 | 0 | Clean. |

No error class outside the ones above appears in the run.

---

## 5. Integration actions

### 5.1 Stitching (brief step 6b — PM-authorised edit of the `stitching` key)

After the first rebuild I read the net of every one of the 65 new stitching vias off the placed board and
measured each point's distance to the nearest non-GND pad, using **real pad polygons** (point-to-polygon
edge distance, `GetEffectivePolygon()`), not bounding boxes.

```
via nets before:  {'GND': 64, '/Emulator MCU/EMU_GPIO_RSVD': 1}

idx      x       y   net                          nearest-non-GND-pad                 dist_mm
 63  284.000  115.500  /Emulator MCU/EMU_GPIO_RSVD  TP203.1[EMU_GPIO_RSVD]              0.2536
 12  293.400   98.880  GND                          C202.1[3V3_EMU]                     0.9276
 13  291.500  109.160  GND                          D201.2[Net-(D201-A)]                1.1755
```

One via (#63) was being silently **re-netted GND → `EMU_GPIO_RSVD`** by `apply_placement.py`'s connectivity
rebuild because `TP203` landed on top of it — a ground stitch shorted to a GPIO. Three points moved; each new
location is ≥ 1.5 mm from every non-GND pad, ≥ 3 mm from the board edge and ≥ 2 mm from any other stitching
point.

| # | From | To | Moved | Why it had to move | Clearance now | Edge |
|---|---|---|---|---|---|---|
| 12 | (293.40, 98.88) | (291.90, 101.63) | 3.132 mm | 0.928 mm from `C202.1` (`3V3_EMU`). The whole x = 293.4 ring segment from y 94 to 106 is blocked — best clearance anywhere on it is 1.30 mm — by the `C200`/`C202`/`C203`/`TP200`/`R211` column `emulator_core` moved east. Stepped 1.5 mm inward off the ring line and 2.75 mm south. | **1.964 mm** (`TP200.1`) | 4.49 mm |
| 13 | (291.50, 109.16) | (291.50, 110.66) | 1.500 mm | 1.176 mm from `D201.2` after `D201` moved to (290.00, 107.60). Moved along the ring line, x unchanged. | **2.632 mm** (`D201.2`) | 4.89 mm |
| 63 | (284.00, 115.50) | (288.00, 115.50) | 4.000 mm | **Via was re-netted GND → `EMU_GPIO_RSVD`**: `TP203` sits 0.254 mm from it. Moved east along the emulator south row, y unchanged, so the row's 8 mm pitch survives at 268 / 276 / 288 / 292. | **3.208 mm** (`U302.3`) | 8.39 mm |

After the second rebuild: **65/65 vias on GND, 0 points within 1.2 mm of a non-GND pad.** Tightest remaining
point 1.2044 mm (#35 to `H12`'s mounting-hole pad, which carries **no net** — the same 1.204 mm item v2.1
recorded); tightest to an actual signal pad 1.2739 mm (#48 to `TP400.1`, `VSOLAR_BENCH_A`). The six v2.1
moves are unchanged and still hold — `R372.2` vs point #2 is still 1.5099 mm, so `face_column`'s v2.1
must-fix stays closed. `floorplan_v2.json` records this round's three moves in `stitching._moved_in_v2_2`
and v2.1's six in `stitching._moved_in_v2`. Stage 3 still owns the authoritative ≤ 10 mm stitching pass
(brief L6).

### 5.2 Block-boundary conflicts (brief step 5) — none this round

`emulator_core` moved 46 parts and `charger_bq25886` six, so I re-scanned **every** pair of courtyards
involving a new ref across the whole 483-footprint board with real polygons (F.CrtYd and B.CrtYd, same-side
only). Result: **29 pairs below 0.5 mm, 0 of them cross-block.** No integrator nudge was needed and no
anchor was touched. v2.1's §5.2 fix (the seven `battery_replica` parts nudged off the `strip_left_pyro_shunts`
shunt headers) is carried through in the merged `placements` verbatim, and `battery_replica` still sits
0.520 mm off every `JP60x` courtyard.

### 5.3 Decisions taken (PM — the owner can override any of these)

1. **The three stitching points in §5.1 were moved**, under the step-6b authority. `stitching` is otherwise
   frozen; no point was added or removed and the count stays at 65.
2. **The 29 intra-block sub-0.5 mm courtyard pairs are accepted** as decoupling-chain trades (min 0.110 mm,
   `C315↔U315`; copper-to-copper there is 1.12 mm). Every one is a capacitor — or, once, an output cap
   against its inductor — against the pin it serves.
3. **`emulator_core`'s D-1…D-7 stay deviations, not defects**, and its N-1 / N-2 go to the routing and pour
   stages as written.
4. **`charger_bq25886`'s BAT/SYS-cap priority trade stands**, and the new `Q510` DRU finding is routed to
   stage 3/5 as a `.kicad_dru` edit, not a placement change.
5. **Fixed anchors past their block envelope** (`J400`, `J401`, `J701`) are not findings, per the standing ruling.
6. **The 12.00 mm lane rect is the lane of record**; the six 0402/SOT-23 parts ≤ 0.505 mm inside the wider
   12.6 mm band are fine, per the PM's standing ruling.
7. **`U201` at 3.354 mm from its *original v1* position is accepted** (1.500 mm of it this round). It carries
   no shared FC net; the binding constraint-(c) test, attachment reach, is unchanged in every row (§1.4).

---

## 6. Evidence — every command and its output

All run from `/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1` with
`KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3`,
`KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`,
`S=/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_integrate_v22`,
`D=…/docs/flatsat/2026-09-14_phase2_layout`, on copies in the scratch directory. The live board was never written.

### 6.1 Merge — the two fixed blocks' JSONs into a copy of the v2.1 `floorplan_v2.json`

```
emulator_core      json=47 refs  changed=46  max move 22.463 mm (R204)
charger_bq25886    json=27 refs  changed= 6  max move  7.793 mm (R510)
wrote $S/floorplan_v2_new.json  218 placements
```

Every other key carried over verbatim (`remove_edge_regions`, `add_edges`, `grow_in1_gnd_rect`,
`new_gnd_pours`, `mounting_holes`, `clip_heritage_zones_to`, `clip_inset_mm`, `lanes`, `keepouts`,
`_boundary_fixes_v2`), including v2.1's six relocated stitching points. `based_on_v2` records the provenance
chain, the two blocks re-merged and the seven carried through, and the exact ref lists.

### 6.2 Canonical rebuild from the pristine live board (`outline.py` runs exactly once per build)

```
$ stat -f '%N %Sm' FlatSat_V1.kicad_pcb
FlatSat_V1.kicad_pcb 2026-09-14 11:31:05        # unchanged before and after this stage

$ cp FlatSat_V1.kicad_pcb $S/live.kicad_pcb ; cp FlatSat_V1.kicad_pro $S/live.kicad_pro
$ $KPY tools/pcb/outline.py --board $S/live.kicad_pcb --out $S/outlined.kicad_pcb --spec $S/floorplan_v2_new.json
Edge.Cuts items removed: 11
Edge.Cuts items added: 7
In1 GND zones grown (rect): 1
heritage zones clipped to the Rev2 outline: 40
new GND pours: 4
mounting holes added: 3 (H10..)
stitching vias added: 65
saved …/outlined.kicad_pcb new bbox x 143.29..296.44 y 47.51..172.17          EXIT 0

$ $KPY tools/pcb/apply_placement.py --board $S/outlined.kicad_pcb --placement $S/floorplan_v2_new.json --out $S/placed.kicad_pcb
applied 218; refused (heritage) []; missing refs []
footprints not fully inside the outline: 0: []
courtyard overlaps (same-side, >=1 new part; real polygons): 0: []
footprints missing their preferred silhouette (…), using a fallback: 7: ['BT1', 'G***', 'REF**', 'RF1', 'SW703', 'U12', 'U30']
saved …/placed.kicad_pcb                                                       EXIT 0
```

The 7-footprint fallback line is informational and heritage-only (no new ref is in it); it does not affect the
0 / 0 / 0 counts. The whole build was run **twice** — once before the stitching fix, once after — and the
outline/apply numbers are identical both times.

Copying `FlatSat_V1.kicad_pro` next to the board copy before `outline.py` is mandatory (v2.1 §5.3): without it
`ZONE_FILLER.Fill()` falls back to factory clearances and `attachment_check.py` reports four spurious
zone-fill violations.

### 6.3 Heritage

```
$ $KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json $S/placed.kicad_pcb \
      --allow-zone-growth --allow-edge --refill --core-inset 12 \
      --ref-board …/FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb
note: zones refilled in memory before measuring (reference board too)
… 55 notes: 41 zone-outline reshape/clip notes, 11 Edge.Cuts removals, bbox, new items …
note: bbox before [143.2916, 47.5137, 231.3932, 142.1248] after [143.2916, 47.5137, 296.44, 172.17]
note: new items: footprints +221, tracks/vias +65, zones +4
heritage check: 0 violation(s)                                                 EXIT 0
```

### 6.4 Attachment (brief L11)

```
$ $KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json $S/placed.kicad_pcb
attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
                                                                               EXIT 0
```

### 6.5 Envelopes, anchor moves, cross-block courtyard gaps (my own measurements, `$S/measure.py`)

```
=== (a) ENVELOPES (real courtyard bbox vs block envelope) ===
 face_column              refs=48  outside=0
 bench_io_drivers         refs=10  outside=0
 battery_replica          refs=26  outside=0
 bench_io_cable           refs=11  outside=1  (fixed anchors: ['J701'])   (non-anchor: [])
 emulator_core            refs=47  outside=0
 face0_reference          refs=16  outside=0
 strip_left_pyro_shunts   refs=20  outside=0
 vsolar_injection         refs=11  outside=2  (fixed anchors: ['J400', 'J401'])  (non-anchor: [])
 charger_bq25886          refs=29  outside=0
 non-anchor envelope breaches total: 0

=== (c) IC / INDUCTOR MOVES vs v1 (floorplan.json) and vs v2.1 ===
  L510   vs v1 14.609 mm   vs v2.1  0.130 mm     (support part, not the block's anchor IC)
  L200   vs v1 11.419 mm   vs v2.1  6.091 mm     (support part)
  U510   vs v1  8.448 mm   vs v2.1  0.000 mm     (support part, ruled in round 3)
  U201   vs v1  3.354 mm   vs v2.1  1.500 mm
  U202   vs v1  2.944 mm   vs v2.1  0.000 mm
  Y200   vs v1  2.725 mm   vs v2.1  2.725 mm
  U303   vs v1  1.500 mm   vs v2.1  0.000 mm
  U302   vs v1  1.025 mm   vs v2.1  0.000 mm
  U316   vs v1  0.100 mm   vs v2.1  0.000 mm
  (U200, U300, U310-U314, U315, U500, U511 all 0.000 mm vs v1)

=== (d) COURTYARD GAPS — full board, all pairs involving a new ref, real polygons ===
  pairs < 0.5 mm involving a new ref: 29  (cross-block: 0)
   0.1100  C315   (battery_replica) <-> U315   (battery_replica) F
   0.1350  C210 / C212 / C213 (emulator_core) <-> U200
   0.1500  C217   (emulator_core) <-> L200
   0.1550  C206 / C207 / C209 / C216 <-> U200 ; C220 <-> U201
   0.3200  C200 <-> U202       0.3400  C203 <-> U202
   0.3400  C501 <-> JP500      0.3400  JP500 <-> R500     0.4600  JP500 <-> R503
   0.3800  C511 <-> U511
   0.4000  C500<->C501, C500<->C502, C501<->R500, C502<->R502, R501<->R502, R503<->R504
   0.4000  C512<->C513, C512<->U511, C513<->C514, C516<->U511
   0.4300  C510<->C511, C510<->D510      0.4400  C512<->L510
```

Per-block move counts vs v1: `face_column` 42/48, `bench_io_drivers` 6/10, `battery_replica` 20/26,
`bench_io_cable` 6/11, `emulator_core` 46/47, `face0_reference` 7/16, `strip_left_pyro_shunts` 3/20,
`vsolar_injection` 3/11, `charger_bq25886` 23/29 — **156 of 218 moved, 41 changed rotation, 0 changed side**
(ruling F3 holds; U310/U312/U314 remain the only B.Cu parts).

### 6.6 Lane, RF keep-outs (`$S/misc.py`, `$S/rf.py`)

```
=== (e) LANE ===
 lane of record (floorplan_v2.json, [231.39,47.579,243.39,141.2], 12.00 mm): 0 courtyards intersect
 brief's 12.6 mm band (x 231.4-244.0): 6 courtyards intersect
   C316   penetration 0.505 mm  x[243.495..245.405]  C_0402_1005Metric
   R314   penetration 0.505 mm  x[243.495..245.445]  R_0402_1005Metric
   R333   penetration 0.505 mm  x[243.495..245.445]  R_0402_1005Metric
   R353   penetration 0.505 mm  x[243.495..245.445]  R_0402_1005Metric
   Q703   penetration 0.020 mm  x[243.980..247.930]  SOT-23
   R709   penetration 0.020 mm  x[243.980..245.930]  R_0402_1005Metric
 connector clear depth (east face -> nearest new courtyard west edge, in that connector's y band):
   J1  15.971   J2  15.935   J6  16.030   J9  16.027   J11 15.930
   J13 16.030   J16 17.435   J12 16.625   J22 17.935   (mm)

=== RF KEEP-OUTS (brief S2) ===
U13  bbox [155.47,58.74,194.49,83.21] nearest NEW part C316  at 49.47 mm -> OK (>=8 mm)
U30  bbox [162.07,87.90,171.86,105.10] nearest NEW part JP601 at 38.92 mm -> OK (>=8 mm)
RF1  bbox [184.10,84.90,188.30,89.10] nearest NEW part JP606 at 54.88 mm -> OK (>=8 mm)
```

Tallest part in the 12.6 mm band is the SOT-23 `Q703` at ≈1.1 mm; the four 0402s are ≈0.35 mm. The rule
("no parts taller than 2 mm, no headers") is met with margin either way you draw the lane.

### 6.7 `emulator_core` VREG_PGND return — this round's number

```
  U200 pin47 net = GND at (275.545, 91.418)
   C213.2 (GND) -> U200.47 : 2.033 mm        <- C_IN, DS S6.3.8.1's "critical" ground return
   C217.2 (GND) -> U200.47 : 2.911 mm        <- C_OUT
   C215.2 (GND) -> U200.47 : 4.519 mm
   C212.2 (GND) -> U200.47 : 5.309 mm
   C218.2 (GND) -> U200.47 : 5.475 mm
   nearest GND stitching via -> U200.47 : 6.434 mm
```

**2.033 mm**, measured on the shipped board. v2.1's open owner question asked whether 8.340 mm was a floor
or an oversight; it was an oversight, and the fix round closed it to 2.033 mm without costing any other row.

### 6.8 Stitching vias (brief step 6b) — after the fix

```
via net histogram: {'GND': 65}

idx      x       y   net    nearest-non-GND-pad                                  dist_mm
 35  151.300  168.000  GND   H12.1[]  (netless mounting-hole pad)                 1.2044
 34  147.000  164.100  GND   H12.1[]                                              1.2327
 48  234.000  144.800  GND   TP400.1[VSOLAR_BENCH_A]                              1.2739
 20  288.400  169.100  GND   H11.1[]                                              1.3124
  6  293.400   55.600  GND   H10.1[]                                              1.3484
 21  293.400  164.100  GND   H11.1[]                                              1.3484
 29  192.000  167.450  GND   TP503.1[DOUT_GATE]                                   1.5089
  2  250.420   53.200  GND   R372.2[EMU_TOP_SDA]                                  1.5099
 12  291.900  101.630  GND   TP200.1[VBUS_EMU]                                    1.9635
 13  291.500  110.660  GND   D201.2[Net-(D201-A)]                                 2.6317
 63  288.000  115.500  GND   U302.3[unconnected-(U302-INT-Pad3)]                  3.2080
```

### 6.9 Attachment reach, v2.2 vs v1 (raw) — see §2 for the full table

```
n=37  max=35.8  median=26.4  sum=947      (v1: max 35.8, median 26.4, sum 959)
worse by >3 mm vs v1: none
worst regression: +3V3 J16.6 -> R370.1  +0.6 mm
best improvement: Dir_Chrg_In J14.1 -> R500.1  -3.6 mm
```

### 6.10 DRC

```
$ mkdir -p $S/drcdir && cp *.kicad_sch fp-lib-table sym-lib-table $S/drcdir/
$ cp -R footprints.pretty symbols $S/drcdir/
$ cp $D/floorplan_v2_preview.{kicad_pro,kicad_dru,kicad_prl} -> $S/drcdir/FlatSat_V1.*
$ perl -0pi -e 's/\(paper "A4"\)/(paper "A3")/' $S/ship.kicad_pcb   # page A3, as the v1/v2.1 previews
$ cp $S/ship.kicad_pcb $S/drcdir/FlatSat_V1.kicad_pcb
$ (cd $S/drcdir && $KCLI pcb drc --format json --severity-all --all-track-errors \
       --schematic-parity --refill-zones -o $S/drc_v22.json FlatSat_V1.kicad_pcb)
Found 42 violations
Found 383 unconnected items
Found 11 schematic parity issues

$ $KPY tools/pcb/drc_summary.py $S/drc_v22.json --baseline tools/baseline/drc_prelayout.json
  (table reproduced in §4)

$ python3 - (pull each clearance/courtyard item's sub-item positions out of the json)
clearance        -> U301 x4 (0.15 mm), Q510 x3 (0.19 mm)
courtyards_overlap -> SW2 / TP2 at (194.2, 85.2)-(194.2, 86.0)   [heritage]
```

The board must sit beside its `.kicad_pro` / `.kicad_dru` / `.kicad_prl` **and** the full schematic set,
named to match, or parity cannot run and `kicad-cli` silently uses factory rules (`floorplan.md` §2).
`--refill-zones` is mandatory: without it the run reports ~870 violations, almost all stale-zone-fill noise.

### 6.11 Renders

```
$ (cd $S/drcdir && $KCLI pcb render --side top    -o $D/img/floorplan_v2_top.png    FlatSat_V1.kicad_pcb)
$ (cd $S/drcdir && $KCLI pcb render --side bottom -o $D/img/floorplan_v2_bottom.png FlatSat_V1.kicad_pcb)
$ bash tools/pcb/render.sh $S/drcdir/FlatSat_V1.kicad_pcb $S/pdfs
      -> top/bottom/in1/in2/all_copper.pdf, copied to img/floorplan_v2_{top,bottom,in1_gnd,in2,all_copper}.pdf
$ per block: --side top --width 1400 --height 1000 --zoom Z --pivot (cx-219.866)/10,(109.842-cy)/10,0
```

Per-block framing, recomputed from each block's real footprint bbox on this round's shipped board, with
`zoom = min(220/(W+4), 157/(H+4))`:

```
block                   centre (mm)          size WxH     zoom
face_column             (250.86,  88.34)    14.7x75.6     1.97
bench_io_drivers        (252.23,  70.07)    16.5x14.9     8.31
battery_replica         (208.09, 157.37)    38.8x26.0     5.14
bench_io_cable          (281.48,  69.44)    25.0x41.3     3.47
emulator_core           (281.65, 102.72)    28.5x26.2     5.21
face0_reference         (280.92, 122.91)    23.9x13.1     7.89
strip_left_pyro_shunts  (185.75, 151.84)    67.5x15.7     3.08
vsolar_injection        (239.50, 156.82)    30.2x27.2     5.03
charger_bq25886         (272.70, 156.88)    34.4x26.8     5.11
```

`face_column` is 15 × 76 mm, so a single frame containing it can only be at zoom 1.97 — too coarse to review
passives. It additionally gets three zoom-5.0 tiles (`_n` centre y 61, `_m` y 90, `_s` y 120) and one B.Cu
view (`_bcu`, zoom 3.0) showing U310/U312/U314 on the back of the wing.

---

## 7. Reproducing this

```bash
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
KCLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
D=/Users/ncc-michael/GitHut/flight_controller_board/docs/flatsat/2026-09-14_phase2_layout
S=<your scratch dir>

# 1. merge detail/placement_{emulator_core,charger_bq25886}.json into a copy of the v2.1 $D/floorplan_v2.json
#    (only those refs' "placements" entries replaced; every other key verbatim, including the six
#     v2.1 stitching moves; then this round's three further points, recorded in stitching._moved_in_v2_2)

# 2. canonical rebuild from the PRISTINE live board — the .kicad_pro sibling is REQUIRED (v2.1 §5.3)
cp FlatSat_V1.kicad_pcb $S/live.kicad_pcb ; cp FlatSat_V1.kicad_pro $S/live.kicad_pro
$KPY tools/pcb/outline.py        --board $S/live.kicad_pcb     --out $S/outlined.kicad_pcb --spec $S/merged.json
$KPY tools/pcb/apply_placement.py --board $S/outlined.kicad_pcb --out $S/placed.kicad_pcb   --placement $S/merged.json

# 3. gates
$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json $S/placed.kicad_pcb \
     --allow-zone-growth --allow-edge --refill --core-inset 12 \
     --ref-board ../FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb
$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json $S/placed.kicad_pcb

# 4. stitching-net check FIRST, then re-run 2-3 if any point had to move (step 6b)
#    (a via that physically touches a pad is re-netted by apply_placement's connectivity rebuild)

# 5. DRC — the board must sit beside its .kicad_pro/.kicad_dru/.kicad_prl AND the full schematic set,
#    named to match, or parity cannot run and kicad-cli uses factory rules (floorplan.md §2).
#    --refill-zones is mandatory (without it: ~870 violations, almost all stale-fill noise).

# 6. renders (see §6.11; +Y in --pivot is toward SMALLER board y)
```

---

## 8. What v2.2 does not change

`outline_L1` spec, the wing/strip block order, the attachment column, every edge connector, the 12.6 mm L3
lane definition, the three mounting holes H10–H12, the four new GND pours, the grown In1 plane, the 65-via
stitching *count* and *class* (nine points relocated across v2.1+v2.2, none added or removed), the F.Cu
ruling, and the placements of the seven blocks that were not re-placed. Rulings F2, F3 and F4 are honoured
unchanged: the lane definition stands, U310/U312/U314 stay on B.Cu with their decoupling directly opposite
on F.Cu at 0.000 mm centre offset, and H10–H12 keep the 4 mm corner inset.
