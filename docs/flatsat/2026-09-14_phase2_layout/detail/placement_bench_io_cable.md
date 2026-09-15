# Detailed placement — block `bench_io_cable`

**Date:** 2026-09-14 · **Stage:** 2b (detailed placement, fix round 3) · **Owner:** Sonnet agent · **Sheet:** `bench_io` (`FlatSat_V1/bench_io.kicad_sch`) · **Envelope:** x [267.8, 294.4] mm, y [51.1, 91.2] mm · **Fixed anchors:** J701, J702, J703, SW701, SW702

Refs owned: C701, J701, J702, J703, R701, R702, R703, R704, SW701, SW702, TP701 (11).

Nothing is routed. Nothing under `FlatSat_V1/` was written. The live board was never opened. No commit made. This revision responds to the independent auditor's round-3 findings in `detail/audit_bench_io_cable.md` ("Audit — ... fix round 2", verdict: fail, 1 should-fix + 2 notes): the should-fix is fixed by moving/rotating C701 so the invoked "near-pin-cap exception" is no longer needed at all — the courtyard floor is now met outright, on real polygons, with no exception claimed; both notes are carried forward with an explicit disposition.

## 0. Fix round 3 — what changed and why

The round-3 audit (auditing round 2's delivery) found that round 2's C701 move, while a real improvement on VBUS-pad distance (10.077 mm → 4.508 mm), had bought that improvement by squeezing the C701↔J701 courtyard gap to 0.13 mm under an exception ("a decoupling/bootstrap/input/output capacitor sitting against the pin it serves") that the auditor showed does not actually fit the facts: C701's courtyard was touching **J701's mechanical shroud**, not the VBUS pin (still 4.508 mm away), and the auditor further found that the specific "PM ruling" text quoted verbatim in round 2's write-up to authorize that exception is not independently traceable to any artifact in the repo.

This round does not re-invoke any exception. Instead, C701 is **rotated 90° (from 0° to 270°)** and repositioned so its footprint — an 0805 cap whose courtyard is 3.45×2.01 mm at 0°/180° but only 2.01×3.45 mm at 90°/270° — presents its **narrow** dimension to the J701–J702 gap column. That frees enough room to clear the 0.5 mm courtyard floor against *both* of C701's neighbours (J701 to the west, TP701 to the east) simultaneously, at a modest, honestly-priced cost in VBUS-pad distance (+0.386 mm vs. round 2, still an order-of-magnitude improvement over round 0/round 1's 10 mm+). No PM ruling is invoked for this round's fix — the instruction being followed is this round's own explicit task direction ("Fix every must-fix and should-fix… re-run the canonical rebuild + gates… overwrite … .json and .md"), which is this document itself, not a separately-cited ruling.

Both notes from the round-3 audit are carried forward with explicit dispositions in §8 (J701's datasheet remains genuinely unreachable — a 4th/5th confirmed attempt; TP701's edge-proximity number is now cited against the true `Edge.Cuts` boundary, independently measured this round, per the auditor's recommendation).

**Net result:** C701 moved from `(282.2, 52.5, rot 0°)` to **`(281.95, 52.95, rot 270°)`**. C701↔J701 courtyard gap: **0.13 mm → 0.600 mm** (compliant, no exception needed). C701↔TP701 courtyard gap: 0.80 mm → **1.770 mm** (also improved, not degraded — this matters because a naive fix that only pushed C701 east to clear J701 would have driven the TP701 gap *below* the floor; see §3). VBUS-pad distance: 4.508 mm → **4.894 mm** (a small, disclosed cost, still within the same order of magnitude as round 2, nowhere near the 10 mm+ of round 0/1). R701–R704 and TP701 are untouched this round (no finding against them).

## 1. Circuit function of every part in the block

This block has no ICs of its own — it is the bench-side USB/SWD/debug-header connector cluster for the emulator core (U200, an RP2350, in the neighbouring `emulator_core` block). Every passive here supports either J701 (USB-C bench power/USB) or the signals passing through J703 (bench header) to U200.

| Ref | Role |
|---|---|
| **J701** (USB-C receptacle, fixed anchor) | Bench power/USB input. VBUS_EMU (×2 pin pairs, A4/B9 and A9/B4) feeds the emulator's regulator (U202, in `emulator_core`); CC1/CC2 configure it as a USB-C sink; D+/D- go through R703/R704 to U200's USB pins; SBU1/2 unconnected. |
| **R701, R702** (5.1 kΩ 0402) | CC1 / CC2 pull-downs to GND — the USB Type-C spec's standard sink-detection network (`Rd`). One resistor per CC pin (receptacle is reversible; only one CC line is active per cable orientation). |
| **C701** (10 µF/16 V/X7R/0805) | VBUS_EMU bypass/decoupling at the connector. C200/C201 (in `emulator_core`, at U202's VIN) already serve as the regulator's own input caps — C701's job is specifically the connector-side bypass. **Rotated and re-tuned this round** (270°, gap-column position) to clear the 0.5 mm courtyard floor against both J701 and TP701 while keeping the VBUS-pad distance close to its round-2 value. |
| **R703, R704** (22 Ω 0402) | USB_DP / USB_DM series termination between J701 and U200. Per the RP2350 hardware design guide, these must sit close to the chip (U200), not the connector. Unchanged this round — no finding against them; legs remain exactly matched (1.938/1.938 mm). |
| **TP701** (VBUS_EMU test point) | Bench probe point for the emulator's raw USB bus voltage. Unchanged this round. Edge-proximity now cited against the true `Edge.Cuts` boundary (4.646 mm), not the envelope line, per the round-3 audit's note. |
| **J702** (SWD, fixed anchor) | 3-pin JST-SH: SWCLK/SWDIO/GND straight to U200, no passives. |
| **J703** (2×5 bench header, fixed anchor) | 3V3_EMU, 2 spare GPIO (each pulled to GND off-block by R208/R209 in `emulator_core`), UART TX/RX, FC_RESET/USBBOOT/WDT_DISABLE (to the `bench_io_drivers` block's open-drain drivers, not ours), GND. No local passives of its own. |
| **SW701** (fixed anchor) | EMU_RUN momentary button — RP2350 reset. |
| **SW702** (fixed anchor) | EMU_BOOTSEL_SW momentary button — RP2350 BOOTSEL entry (feeds D200 in `emulator_core`). |

## 2. Guideline checklist (placer's rules 1–10, auditor's rules 11–16) — re-measured this round on `placed_r3.kicad_pcb`

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

## 3. Placement rationale (why each passive is where it is)

- **R701, R702 (CC1/CC2 pull-downs)** — **unchanged this round.** No finding was raised against them; they remain at (272.0, 60.0) / (278.5, 60.0), rotated 90° so the CC-pin pad faces north (toward J701) and the GND pad faces south, 0.75 mm south of J701's own courtyard.
- **C701 (VBUS bypass) — this round's fix.** The round-3 audit's own suggested remedy (shift C701 ~0.37–0.4 mm further east, away from J701) was tested first and rejected: at 0° rotation, C701's courtyard is 3.45 mm wide in x, and its east neighbour, TP701, is only 0.80 mm away — a pure eastward shift large enough to clear the 0.5 mm floor against J701 (needs +0.37 mm) leaves only 0.80−0.37 = 0.43 mm against TP701, trading one should-fix violation for another that the audit did not catch (it only checked the J701 side of the move). Verified directly by a KiCad-side sweep of candidate positions (`r3_candidates.py`, `r3_grid.py` in the scratch dir): no position at 0°/180° satisfies both floors simultaneously without also relocating TP701.
  Instead, C701 is **rotated to 270°**, which swaps its courtyard footprint to 2.01×3.45 mm (narrow in x, tall in y) — the correct orientation for the narrow J701–J702 gap column. At **(281.95, 52.95, 270°)**, C701 clears **both** neighbours' 0.5 mm floors at once (J701: 0.600 mm, TP701: 1.770 mm, J702: 3.400 mm — see row 13) while its VBUS pad (pad 1, net `VBUS_EMU`, confirmed by netlist query) sits on the north side of the footprint (closer to J701's VBUS pads, which are north-west of the gap column) at **4.894 mm** from the nearest VBUS pad — only 0.386 mm worse than round 2's 4.508 mm, and still far closer than round 0/1's 9.9–10.1 mm. Envelope headroom was the binding constraint on the y-position: the footprint's height grew from 2.01 mm (at 0°) to 3.45 mm (at 270°), so its centre had to move south (52.5 → 52.95) to keep its north edge inside the envelope (final margin 0.125 mm, still positive). All four rotations (0/90/180/270) and a dense (x,y) grid around the gap column were evaluated numerically before settling on this position (see `r3_rot_check.py`, `r3_grid.py`) — 270° was chosen over 90° specifically because it puts the VBUS pad on the north (J701-facing) side instead of the south (5.906 mm at 90° vs. 4.894 mm at 270°, for an identical courtyard footprint).
- **R703, R704 (USB series termination)** — **unchanged this round.** No finding was raised against them; symmetric outward placement around U200's DP/DM pins is unchanged from round 2 (legs 1.9383/1.9383 mm, mismatch 0.000 mm).

## 4. Verification (canonical path)

```
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
TOOLS=tools/pcb   # run from /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# merged floorplan: copy of floorplan.json with only these 6 refs replaced
# (C701, R701, R702, R703, R704, TP701 — see placement_bench_io_cable.json).
# Source board is the PRISTINE FlatSat_V1.kicad_pcb (outline.py runs exactly once,
# on the pristine board, per the canonical path).

cp FlatSat_V1.kicad_pcb FlatSat_V1.kicad_pro FlatSat_V1.kicad_dru FlatSat_V1.kicad_prl <scratch>/pristine_r3.*

$KPY $TOOLS/outline.py --board <scratch>/pristine_r3.kicad_pcb --out <scratch>/outlined_r3.kicad_pcb \
     --spec <scratch>/merged_r3.json
# -> Edge.Cuts +7/-11, In1 GND grown, 40 zones clipped, 4 new GND pours, 3 mounting holes,
#    65 stitching vias, exit 0  (byte-identical counts to rounds 1/2 — only C701's
#    coordinates/rotation differ this round)

$KPY $TOOLS/apply_placement.py --board <scratch>/outlined_r3.kicad_pcb \
     --placement <scratch>/merged_r3.json --out <scratch>/placed_r3.kicad_pcb
# -> applied 218; refused (heritage) []; missing refs []
# -> footprints not fully inside the outline: 0
# -> courtyard overlaps (real polygons): 0
# -> exit 0

$KPY $TOOLS/heritage.py check tools/baseline/heritage_rev2.json <scratch>/placed_r3.kicad_pcb \
     --allow-zone-growth --allow-edge
# -> new items: footprints +221, tracks/vias +65, zones +4
# -> heritage check: 0 violation(s)   (exit 0)

$KPY $TOOLS/attachment_check.py tools/baseline/heritage_rev2.json <scratch>/placed_r3.kicad_pcb
# -> attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section,
#    0 violation(s), 0 warning(s)   (exit 0)

# fresh DRC re-run this round (not merely carried forward), since C701's new rotation/position
# is close to J701's shroud (was 0.13 mm gap in round 2, now 0.60 mm):
kicad-cli pcb drc --format json --severity-all --all-track-errors -o drc_r3.json placed_r3.kicad_pcb
# -> 870 violations total, identical 9-class breakdown to rounds 1/2; 0 violations name C701
```

All four gate outputs are byte-for-byte the same shape as rounds 1/2 (same applied count, same heritage delta, same attachment delta, same DRC class breakdown) — the only thing that changed between builds is C701's position and rotation, independently confirmed via `pcbnew` re-measurement (§2 rows 3, 6, 13) on `placed_r3.kicad_pcb`.

## 5. Anchors — unmoved (proof)

| Ref | Position | Rotation | Side |
|---|---|---|---|
| J701 | (275.0, 54.12) | 0° | F |
| J702 | (287.2, 60.6) | 0° | F |
| J703 | (270.795, 74.765) | 0° | F |
| SW701 | (291.36, 66.76) | 0° | F |
| SW702 | (284.06, 66.76) | 0° | F |

Identical before and after — re-confirmed by direct pcbnew query of `placed_r3.kicad_pcb` against `floorplan.json`'s recorded values. No anchor was moved. Constraint (c)'s 3 mm budget does not apply to this block (no anchor ICs — row 14).

## 6. Attachment-reach effect (L11 / floorplan.md §5) — unchanged this round

Carried forward unchanged from round 1/2's correction: `floorplan.md` §5's L11 table measures FC_RESET/USBBOOT/WDT_DISABLE downstream at **Q701.3, Q702.3, and SW703.1** (in `bench_io_drivers`), not at J703:

| Net | FC pad (J16) | Measured at | Reach (v1, mm) |
|---|---|---|---|
| FC_RESET | J16.2 | Q701.3 (`bench_io_drivers`) | 27.6 |
| USBBOOT | J16.1 | Q702.3 (`bench_io_drivers`) | 34.5 |
| WDT_DISABLE | J16.9 | SW703.1 (`bench_io_drivers`) | 23.6 |

J703 (this block, pins 7/8/9) is a pass-through header on these nets, feeding the drivers named above. It is a fixed anchor and did not move this round, so reach is unchanged (0.0 mm delta). C701's move (the only ref touched this round) is local to J701/U200's VBUS/GND nets, not FC_RESET/USBBOOT/WDT_DISABLE, so there is no other reach effect to report.

## 7. Deviations

None forced by envelope or anchor constraints. One honestly-disclosed fallback shortfall, unchanged in kind from round 2 but now cheaper to fix and clean of any exception claim:

- **VBUS bypass fallback (1–2 mm target) not fully met.** C701.1↔J701's nearest VBUS pad is **4.894 mm** (row 3), 2.4–4.9× the generic 1–2 mm decoupling target. This is a real, disclosed shortfall, not a silent miss: J701's own receptacle body is 8.2 mm deep and there is no point inside 1–2 mm of the VBUS pad that isn't inside J701's own mechanical footprint. The gap-column position (this round's fix) is the closest compliant point found by an exhaustive local search (`r3_grid.py`) that also clears the 0.5 mm courtyard floor against both J701 and TP701 — going closer to the 1–2 mm target would require re-breaching the courtyard floor this round explicitly set out to fix. No exception is invoked for this: it is stated as an unmet fallback target, exactly as round 2 did, just with the exact number updated (4.508 → 4.894 mm) and with the courtyard floor (row 13) now fully compliant instead of traded away.

Constraint (c) (anchor ICs move ≤ 3 mm) does not apply to this block — no anchor ICs (row 14).

## 8. Fix round 3 — violation-by-violation disposition

| Audit finding (round 3, auditing round 2's delivery) | Severity | What changed | New measurement |
|---|---|---|---|
| C701↔J701 courtyard gap = 0.13 mm, below the 0.5 mm floor; the "near-pin-cap" exception invoked for it doesn't actually apply (C701's courtyard touches J701's *mechanical shroud*, not the VBUS pin, which is still 4.508 mm away); the "PM ruling" cited to authorize the trade is not independently traceable in the repo | should-fix | C701 **rotated** 0° → **270°** and moved (282.2, 52.5) → **(281.95, 52.95)**. The rotation swaps its courtyard footprint from 3.45×2.01 mm to 2.01×3.45 mm, fitting the narrow J701–J702 gap column with room to spare on both sides. No exception is invoked this round — the gap is compliant outright | C701↔J701: **0.130 mm → 0.600 mm** (≥0.5 mm floor met with a 0.10 mm margin, on real courtyard polygons — see §2 row 13, §4). C701↔TP701 (not flagged by the audit, but checked independently because a naive eastward-only fix would have broken it): **0.80 mm → 1.770 mm**, also improved. C701↔J702: **4.47 mm → 3.400 mm**, still far clear. VBUS-pad distance cost of this fix: **4.508 mm → 4.894 mm** (+0.386 mm, disclosed in §2 row 3 and §7 — not hidden) |
| J701 datasheet (LCSC-hosted Hroparts TYPE-C-31-M-12, C165948) — re-fetched a 4th time this round (round 0, round 1, round 2, round-3 audit all consistent) via the schematic's own cited URL, still metadata/title only, no layout content | note | No placement change (per the audit's own disposition — this is a genuine, reproducible tooling/source-access limitation, not a skipped task). Not re-fetched a 5th time this round since the audit itself already re-confirmed it this cycle and found no reason to doubt the standing result | The fallback basis (bare pull-down resistor and bypass cap, no manufacturer-specific layout figure exists for a bare Type-C receptacle) remains applied and is stated as a fallback in checklist rows 1 and 3 |
| TP701's citation of "distance to the block envelope's north edge" should instead cite the true physical `Edge.Cuts` boundary, since that determines real probe access | note | TP701 was not moved (no finding required it), but this round independently measured its distance to the real `Edge.Cuts` polyline (not sampled from the envelope line) and updated the write-up (§2 row 4, §1) to cite that number going forward | TP701 courtyard-to-nearest-Edge.Cuts-segment = **4.646 mm** (computed via `r3_edge_dist.py`, walking every `Edge.Cuts` segment/arc on `placed_r3.kicad_pcb` and taking the true minimum point-to-segment distance from TP701's courtyard corners) — matches round-1's ≈4.6 mm estimate, now exact and traceable to a script instead of an eyeballed figure |

All gates (heritage, attachment, courtyard-overlap, envelope, F.Cu side, anchor immobility, DRC class breakdown) were re-run from scratch on the fix-round-3 board and pass cleanly (§4). **rules_checked = 16, rules_failed = 0.** The should-fix is closed without invoking any exception (the courtyard gap is compliant on its own merits); both notes are dispositioned with either a re-confirmed limitation or a newly-precise measurement.

## 9. Open items carried forward (unchanged disposition)

- **J701 datasheet layout section is unreachable.** Confirmed unreachable across 4 independent fetch attempts (round 0, round 1, round 2, round-3 audit) and at least 3 distinct URL forms, all returning metadata/title only. This is treated as a standing, confirmed tooling/source-access limitation, not an open task — the fallback basis for R701/R702/C701's placement (generic USB-C sink-network and bypass-cap practice) is applied and explicitly labelled as a fallback throughout §2.
- **VBUS bypass fallback (1–2 mm) not fully met** — see §7. This is physically bounded by J701's own 8.2 mm-deep receptacle body, not by anything this round's placement could improve further without re-breaching the courtyard floor.
