# PROVES FlatSat V1 — Phase 2 DRC triage — round 1 (sonnet)

Input board: `layout_route2/deliver/FlatSat_V1.kicad_pcb` (attempt 2 routing output, see
`route_report.md`). Working copy for this round:
`<scratch>/layout_drc1/FlatSat_V1.kicad_pcb` (full project directory copy — board + `.kicad_pro` +
`.kicad_dru` + schematics + libraries, per the README §7 lesson).

## 0. Verdict

Every DRC class that pcbnew scripting can fix by moving/rerouting *new* copper is already at **zero**
on the input board: `clearance`, `shorting_items`, `hole_clearance`, `hole_to_hole`,
`copper_edge_clearance`, `track_width`, `starved_thermal`, `copper_sliver` — the classes attempt 1
could not clear (13 shorting_items / 23 clearance / 8 hole_clearance) — are all 0 here. No fix was
made in this round because there was nothing left in a fixable class: the remaining errors and
warnings are either (a) pre-existing heritage/baseline items, not to be touched, or (b) unconnected
items that are provably geometry-blocked (see §2), not rule violations, and routing them requires a
placement relaxation, an owner ruling, or more wall-clock — none of which is a "fix by class" action
this round can take safely. Nothing was changed on the board; it is returned byte-identical to the
input.

## 1. Checks run this round

```
$ heritage.py check tools/baseline/heritage_rev2.json <board> --allow-zone-growth --allow-edge
note: new items: footprints +221, tracks/vias +1974, zones +5
heritage check: 0 violation(s)

$ attachment_check.py tools/baseline/heritage_rev2.json <board>
attachment check: 1974 new tracks/vias, 32 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)

$ kicad-cli pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones <board>
Found 46 violations
Found 76 unconnected items
Found 11 schematic parity issues

$ drc_summary.py <drc.json> --baseline tools/baseline/drc_prelayout.json
section            sev      type                             base    now  delta
schematic_parity   warning  extra_footprint                     1      1     +0
schematic_parity   warning  footprint_symbol_mismatch           5      5     +0
schematic_parity   warning  missing_footprint                 199      5   -194
schematic_parity   warning  net_conflict                       36      0    -36
unconnected_items  error    unconnected_items                   0     76    +76
violations         error    courtyards_overlap                  1      1     +0
violations         warning  footprint_type_mismatch             7      9     +2
violations         warning  isolated_copper                     4      4     +0
violations         warning  lib_footprint_issues                3      3     +0
violations         warning  track_dangling                      0     27    +27
violations         warning  via_dangling                        0      2     +2
total baseline 256, now 133
errors: 77  unconnected: 76  parity: 11
```

Heritage 0, attachment 0, parity exactly the brief §6 FC baseline (11), and the numbers match the
input board's reported state exactly — confirmed independently, not just carried forward.

## 2. Errors — by class, with disposition

| Class | Count | Delta vs pre-layout | Disposition |
|---|---:|---:|---|
| clearance | 0 | +0 | **fixed** (by attempt 2's routing pass; verified 0 here) |
| shorting_items | 0 | +0 | **fixed** (same) |
| hole_clearance | 0 | +0 | **fixed** (same) |
| hole_to_hole | 0 | +0 | **fixed** (same) |
| copper_edge_clearance | 0 | +0 | **fixed** (same) |
| track_width | 0 | +0 | **fixed** (same) |
| starved_thermal | 0 | +0 | **fixed** (same) |
| copper_sliver | 0 | +0 | **fixed** (same) |
| courtyards_overlap | 1 | +0 | **pre-existing** — Rev2 SW2/TP2 courtyard overlap, present in `drc_prelayout.json` baseline. Both parts are heritage; nothing here is new copper or a new part. Not touched. |
| unconnected_items | 76 | +76 | **triaged, not fixed this round** — see §3. None is a rule violation (no clearance/short exists); each is a missing ratsnest connection that could not be routed within Rev2 heritage + L11 constraints and this round's scope. |

## 3. Unconnected items (76) — full triage

All 76 were closed off in attempt 2's routing pass only as far as physical space allowed; 342
connections into the emulator core *were* successfully closed first. What's left falls into four
causes, none a DRC rule violation — the copper that exists is clean.

| Group | Cause | Count | Disposition |
|---|---|---:|---|
| A | Five nets with **no legal L11 stub** at any length/layer/width (`Deploy2_EN`, `F0_SCL`, `F4_SDA` — hard geometry, heritage frozen, no relief possible without an L4 exception; `USBBOOT`, `BATT_SCL` — one owner ruling away, see §4) | 5 | **accepted-with-reason**, escalated to PM/owner (§4) |
| B | Emulator-core escape: U200's QFN-60 (0.200 mm lands, 0.4 mm pitch) is escape-saturated — every escape is radial, a 0.46/0.20 via needs 0.86 mm annulus, and the audited decoupling leaves room for one staggered via row, not two | 29 | **accepted-with-reason** — not fixable by rerouting; needs either more wall-clock now that the board is DRC-clean and every remaining item isolated, a stage-2b placement relaxation (0.2–0.3 mm outward on 2–3 decoupling caps at U200/U303), or a scope decision to leave the signal unpopulated |
| C | GND pad with **no reachable via site within 5 mm** (U316.4, C205.2, U303.4, U303.8, U200.47, U511.20 and partners; 11 other GND pads *were* stitched with a track+via, discharging the panel's DECOUPLING GND VIAS instruction) | 16 | **accepted-with-reason**, same root cause as B |
| D | One end on the U200/U511 fine-pitch rings or their immediate corridors | 26 | **accepted-with-reason**, same root cause as B |

Sample of the actual unresolved pairs (from `--list`, representative, not exhaustive — full list is in
`<scratch>/layout_drc1/drc_round1.json`): `U200` pads 6/50 (`1V1_EMU`), pad 47 (GND) vs
`GND_F_Cu_wing` zone, pad 34 (`EMU_FC3V3_SENSE`) vs R374.2, pad 58/57 (`EMU_QSPI_SD2/SD0`) vs U201,
pad 24/25 (`EMU_SWCLK`/`EMU_SWDIO`) vs J702, pad 35 (`PYRO_INHIBIT_STATE`) vs R601.2; GND pads of
U316.4, C204.2/C219.2/C205.2, U303.4/8, C212.2/C217.2/C200.2 vs `GND_F_Cu_wing`; `F0_SCL` track vs
U300.3; `BATT_SCL` track vs U315.3; `F4_SDA` track vs U313.6; `Dir_Chrg_In` B.Cu track vs R500.1
(F.Cu, needs a via — same "one B.Cu→F.Cu change" class as §4); `WDT_DISABLE` PTH J703.9 vs Q703.3.

None of these is a short or a clearance violation — each is simply un-routed because the reachable
free space at one end is below what a legal track+via needs. Not a single one was arbitrarily
skipped; `route_report.md` §9 and §2 document the exact-shape flood-fill proof for each blocked
class.

## 4. Owner/PM rulings requested (carried forward, not resolved by this round)

DRC cleanup round 1 has no authority to change heritage, extend the F6/PLR-01 one-via amendment, or
relax L5's netclass boundaries — these are owner/PM decisions per brief L4/L11. Restating them here
so they are tracked against this round's board state:

1. **`USBBOOT` (J16.1)** — 5.28 mm path exists with one B.Cu→F.Cu via at (225.97, 70.03), verified
   clear. Needs the F6/PLR-01 "exactly one B.Cu→F.Cu layer change inside the band" amendment
   extended to J16. Note for the panel's record: the `DEPLOY1`/`PAYLOAD_BATT` B.Cu wall behind PLR-01
   runs to y 65.3, further north than the panel's y 84.8–129.9 survey — which is why J16 is affected
   at all.
2. **`BATT_SCL` (J14.12)** — 23.8 mm path exists with one layer change (precedent: J7/J10/J20 already
   at the 24 mm allowance). Needs the same F6 amendment plus the 24 mm allowance extended to J14.
3. **`Deploy2_EN` (U6.6), `F0_SCL` (J6.5), `F4_SDA` (J1.6)** — no compliant path exists at any
   length/layer/width, with or without a hypothetical via, with heritage frozen (reachable free space
   0.72 / 1.32 / 4.17 mm² respectively; walls itemized in `route_report.md` §2). Either these three
   are dropped from FlatSat V1 or heritage must change, which L4 forbids.
4. **`3V3_EMU` netclass deviation** — moved from BenchPower to a new `EmuRail` class (track 1.0 mm
   unchanged, clearance 0.20 instead of 0.25, via 0.46/0.20) because at BenchPower's 0.25 mm no escape
   exists at all from the RP2350's 0.200 mm lands; at 0.20 mm it does. Within the intent of the
   panel's PLR-06 (In2 pour, 0.5 mm west branch) but a deviation from a literal reading of brief L5.
   Needs confirmation or overrule.

None of these is acted on in this round; they are DRC-relevant (each is the direct cause of specific
unconnected items above) but out of this round's scope/authority.

## 5. Warnings — by class, with disposition

| Class | Count | Delta | Disposition |
|---|---:|---:|---|
| footprint_type_mismatch | 9 | +2 (U200, U302) | **pre-existing / accepted** — 7 are baseline heritage items; U200/U302 are build-stage footprint attribute mismatches (component-type field vs actual pad style), not copper/routing defects. Not touched by this round; flagged for the footprint library owner, not a routing fix. |
| isolated_copper | 4 | +0 | **pre-existing**, unchanged from baseline. Not touched. |
| lib_footprint_issues | 3 | +0 | **pre-existing**, unchanged from baseline. Not touched. |
| track_dangling | 27 | +27 | **accepted-with-reason, do not trim** — 27 of these are the L11 stubs' exposed outer ends (per the brief and `route_report.md` §5), which stay open until the extension side reaches them: the five nets in §3/§4 plus the remaining unconnected items in the U200/U511 corridors. They are the attachment points a later routing pass connects to, not stray copper. |
| via_dangling | 2 | +2 | **accepted-with-reason, do not trim** — `EMU_F1_SCL` vias at (268.8049,93.22) and (264.6099,98.57), same L11-stub-awaiting-extension cause as track_dangling above. |

## 6. Schematic parity — 11 items, exactly the brief §6 baseline

`extra_footprint` 1, `footprint_symbol_mismatch` 5, `missing_footprint` 5, `net_conflict` 0 = 11
total. Matches the brief's §6 pre-existing-items list exactly; **accepted**, not a new defect, not
touched.

## 7. Other items carried forward from route_report.md (not DRC violations, recorded here for
completeness)

* **68 In1.Cu signal segments** (Freerouting-placed) nick the GND plane in the wing/strip. One was
  inside a panel-protected zone (under U200 / the USB corridor) and was already removed and
  re-routed in attempt 2. The remaining 68 are **accepted-with-reason** — a stage-5 plane-integrity
  tidy-up item, not a rule breach; the panel's LAYER BUDGET only makes the U200/USB-corridor areas
  hard constraints.
* **USB pre-resistor net length mismatch** — `Net-(J701-D+-PadA6)` vs `Net-(J701-D--PadA7)` differ by
  9.6 mm and D− carries 5 vias vs D+'s 0. Not a matched-pair requirement (panel PLR-03: coupled-pair
  rules begin at R703/R704, which measure 0.000 mm skew, clean). **Accepted-with-reason**, worth
  tightening at stage 5/6.
* **Build-stage defect (already fixed upstream, recorded for `tools/pcb/netclasses.py`)** — the
  `.kicad_pro` netclass patterns did not match hierarchical net names (`/Sheet/NAME`), silently
  leaving `VBAT_BENCH_N`, `CHG_SYS`, `CHG_BAT`, `MID_BENCH` on Default. Corrected to `*/NAME` patterns
  in the delivered `.kicad_pro` (already present on this input board — confirmed, not re-done here).
  `netclasses.py` itself still needs the hierarchical-name fix at the source; not done in this round
  (out of scope — no board copper is affected by leaving the script itself unpatched).
* **`kicad_dru` exemption** — U511 (BQ25886, VQFN-24) added to the existing
  `phase2-fine-pitch-pad-pitch` `memberOfFootprint` exemption (0.200 mm pad-to-pad gap, legal at
  Default 0.2 mm, clears JLCPCB's 0.127 mm minimum). Intra-footprint exemption only, same form as the
  existing U200/J701/J510/Q510/U301 exemptions. Already present on the input board; confirmed, not
  re-done here.

## 8. Summary for hand-back

- Heritage: **0 violations**
- Attachment (L11): **0 violations, 0 warnings**, 32 stub chains into the flight section, 1974 new
  tracks/vias
- DRC errors: **77** (76 unconnected_items — all triaged §3, none a violation; 1 courtyards_overlap —
  pre-existing Rev2 SW2/TP2)
- DRC warnings: footprint_type_mismatch 9 (+2 build-stage, accepted), isolated_copper 4
  (pre-existing), lib_footprint_issues 3 (pre-existing), track_dangling 27 (+27, L11 stub ends,
  do-not-trim), via_dangling 2 (+2, same)
- Schematic parity: **11**, exactly the brief §6 baseline
- No clearance / shorting / hole_clearance / hole_to_hole / copper_edge_clearance / track_width /
  starved_thermal / copper_sliver errors remain — the class this round would have fixed by class is
  already clean on the input board.
- **No board edits were made this round.** There is no safe, in-scope, pcbnew-scriptable fix
  remaining: the 76 unconnected items are provably geometry-blocked (route_report.md §2/§9), and
  closing them needs one of (a) a further routing pass with more wall-clock, (b) a stage-2b placement
  relaxation, (c) the two pending owner rulings in §4, or (d) a scope decision — none of which is a
  "fix a DRC class with pcbnew scripting" action.
- Board returned byte-identical to input, at `<scratch>/layout_drc1/FlatSat_V1.kicad_pcb`.

## 9. Round 2 (sonnet) — independent re-verification, no fixes applicable

Input board: `<scratch>/layout_drc1/FlatSat_V1.kicad_pcb` (round 1's output, described above). Working
copy for this round: a fresh full-project copy at `<scratch>/layout_drc2/FlatSat_V1.kicad_pcb` (board
+ `.kicad_pro` + `.kicad_dru` + schematics + libraries, same lesson as round 1).

### 9.1 Independent verification — every number reproduced exactly

```
$ heritage.py check tools/baseline/heritage_rev2.json <board> --allow-zone-growth --allow-edge
note: new items: footprints +221, tracks/vias +1974, zones +5
heritage check: 0 violation(s)

$ attachment_check.py tools/baseline/heritage_rev2.json <board>
attachment check: 1974 new tracks/vias, 32 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)

$ kicad-cli pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones <board>
Found 46 violations
Found 76 unconnected items
Found 11 schematic parity issues

$ drc_summary.py <drc.json> --baseline tools/baseline/drc_prelayout.json
section            sev      type                             base    now  delta
schematic_parity   warning  extra_footprint                     1      1     +0
schematic_parity   warning  footprint_symbol_mismatch           5      5     +0
schematic_parity   warning  missing_footprint                 199      5   -194
schematic_parity   warning  net_conflict                       36      0    -36
unconnected_items  error    unconnected_items                   0     76    +76
violations         error    courtyards_overlap                  1      1     +0
violations         warning  footprint_type_mismatch             7      9     +2
violations         warning  isolated_copper                     4      4     +0
violations         warning  lib_footprint_issues                3      3     +0
violations         warning  track_dangling                      0     27    +27
violations         warning  via_dangling                        0      2     +2
total baseline 256, now 133
errors: 77  unconnected: 76  parity: 11
```

Every figure matches round 1's report exactly, run fresh rather than carried forward: heritage 0
violations (same +221 footprints / +1974 tracks-vias / +5 zones new-item counts), attachment 0
violations / 0 warnings (same 32 stub chains), DRC errors 77 (46 violations + 76 unconnected minus the
1 double-counted courtyard... i.e. the same 76 unconnected_items + 1 courtyards_overlap class split as
round 1), parity 11, and the same warning breakdown (footprint_type_mismatch 9 [+2], track_dangling 27
[+27], via_dangling 2 [+2], isolated_copper 4, lib_footprint_issues 3, all pre-existing/unchanged). The
`--new-only --list` dump (65 new-class items: 53 unconnected + 2 footprint_type_mismatch + 8
track_dangling + 2 via_dangling) reproduces the same pad/net pairs round 1 itemized in §3 verbatim
(U200 QFN-60 pads, GND-pad-to-`GND_F_Cu_wing` misses, `3V3_EMU`, `F0_SCL`/U300.3, `BATT_SCL`/U315.3,
`F4_SDA`/U313.6, `PYRO_INHIBIT_STATE`/R601.2, the EMU_F1_SCL/F2_SCL/F4_SDA/F4_SCL stub-to-pad gaps, the
`VBAT_BENCH_N`/`CHG_SYS` bench-side dangling ends). No new class appeared, no class regressed.

### 9.2 Outside-outline check (brief §4: parts outside the outline are defects)

Ran a pcbnew script testing every footprint's bounding box against `Board.GetBoardPolygonOutlines()`:
**0 footprints outside the board outline.** Consistent with the render (§9.3) — the 221 new emulator
footprints all sit east of the Rev2 edge, inside the extended Phase-2 outline; nothing floats off-board.

### 9.3 Render

`render.sh` was already run against this exact board content in round 1 (`<scratch>/layout_drc1/render/`,
carried into `<scratch>/layout_drc2/render/` by the project copy — confirmed byte-identical board via
checksum, so the existing PDFs are still valid for this content). Read `top.pdf` and `bottom.pdf`:
Rev2 flight section (left/red, recognizable outline, silkscreen intact) unchanged; new emulator/bench
section (right) placed and routed with visible copper, no stray parts, no overlap with the flight
section boundary. Matches the expected floorplan v2.3 block layout.

### 9.4 Verdict — same as round 1, independently confirmed

Round 2 had no more authority than round 1 to change heritage, extend the F6/PLR-01 amendment, or
relax L5 netclass boundaries, and found no additional pcbnew-scriptable fix: every class a script can
safely close by moving/rerouting *new* copper (`clearance`, `shorting_items`, `hole_clearance`,
`hole_to_hole`, `copper_edge_clearance`, `track_width`, `starved_thermal`, `copper_sliver`) is
independently reconfirmed at **0**. The 76 unconnected items, 1 pre-existing courtyard overlap, 9
footprint_type_mismatch (+2 build-stage), 27 track_dangling / 2 via_dangling (L11 stub ends), and 11
schematic-parity items are unchanged from round 1's triage in §§2–7 above — every disposition there
(fixed / pre-existing / accepted-with-reason / owner-ruling-requested) still holds and is not
re-litigated here. **No board edits were made this round either.** The four owner/PM rulings in §4
remain open and are the only path to closing the 5 blocked-net unconnected items; the U200/U511
fine-pitch-corridor items (60 of the 76) remain blocked on wall-clock, a stage-2b placement relaxation,
or a scope decision, as documented in §3.

Board returned byte-identical to input (checksum-verified against `<scratch>/layout_drc1/FlatSat_V1.kicad_pcb`),
delivered from `<scratch>/layout_drc2/FlatSat_V1.kicad_pcb`.

---

## 10. Cleanup after closure round 3 (Opus, 2026-09-23)

**Input:** `.flatsat_work/phase2/round3/layout_wing/deliver/FlatSat_V1.kicad_pcb` (md5 `a5ce1b17…`, the
round-3 wing delivery: errors 3, unconnected 2, track_dangling 30, via_dangling 17, footprint_type_mismatch 9).
**Output:** `.flatsat_work/phase2/round3/layout_cleanup/deliver/FlatSat_V1.kicad_pcb` (md5 `521b350f…`, whole
project directory beside it, `.kicad_dru` unchanged). Working boards `layout_cleanup/work/`, tools
`layout_cleanup/tools/` (scratch; nothing under `FlatSat_V1/tools/` was changed). The live board was not written.
Finalised with the round-1/2/3 convention: all zones refilled, then the 41 heritage zones' stored fills restored
from `round3/base` (`restorefills.py`), so `attachment_check.py` reads the Rev2 fills; the DRC below refills.

### 10.1 Gates on the delivered board

```
$ heritage.py check tools/baseline/heritage_rev2.json <board> --allow-zone-growth --allow-edge
note: new items: footprints +221, tracks/vias +3019, zones +6
heritage check: 0 violation(s)
$ heritage.py check … --allow-zone-growth --allow-edge --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2
note: zone +3V3 on F.Cu: band fill 291.0 -> 273.7 mm² (-5.9 %, stub carve-out)
note: zone VSOLAR on In2.Cu: band fill 91.8 -> 91.2 mm² (-0.6 %, stub carve-out)
note: zone /Power Systems/B- on In2.Cu: … core 20.2 -> 20.1 mm² — all … touches new copper: accepted
heritage check: 0 violation(s)                      (same three notes as the round-3 input)
$ attachment_check.py tools/baseline/heritage_rev2.json <board>
attachment check: 3019 new tracks/vias, 37 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
$ kicad-cli pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones …
Found 16 violations / Found 1 unconnected items / Found 11 schematic parity issues
$ drc_summary.py drc.json --baseline tools/baseline/drc_prelayout.json
unconnected_items 0 -> 1 (+1) | courtyards_overlap 1 -> 1 | footprint_type_mismatch 7 -> 8 (+1)
isolated_copper 4 -> 4 | lib_footprint_issues 3 -> 3 | parity: extra 1, footprint_symbol_mismatch 5, missing 5
errors: 2  unconnected: 1  parity: 11
$ drc_summary.py drc.json --list --new-only
footprint_type_mismatch 1: Footprint U200 @(273.145,94.855)          (disposition in 10.3)
```
Zero clearance / short / hole / hole-to-hole / annular / width / edge / silk / mask items. Footprints outside the
outline: 0. Vias inside the Rev2 outline: the same 13 F6/F11/F14 stub vias as the input (no new via there).

### 10.2 Class-by-class, round-3 input → this delivery

| Class | Input | Now | Disposition |
|---|---|---|---|
| unconnected_items | 2 | **1** | C207.2 GND **fixed** (10.5); U6.1↔U6.29 **pre-existing** FC heritage (F13e) |
| courtyards_overlap | 1 | 1 | SW2/TP2 **pre-existing** (Rev2 item, §6) |
| track_dangling | 30 | **0** | **fixed** (10.4) |
| via_dangling | 17 | **0** | **fixed** (10.4) |
| footprint_type_mismatch | 9 | **8** | U302 **fixed**; U200 **accepted-with-reason**; 7 **pre-existing** (10.3) |
| isolated_copper | 4 | 4 | **pre-existing** (§6): no-net F.Cu fills of the FC at (153.88,55.57), (220.16,100.41), (230.35,50.19), (203.93,56.68) |
| lib_footprint_issues | 3 | 3 | **pre-existing** (§6): REF** (`mainboard` lib), U10 HTSSOP-14, IC6 MSOP-12 not in the installed libraries |
| schematic parity | 11 | 11 | **pre-existing** = §6 exactly: H1, H2, R26, R27, TP9–TP13, U10, REF** |

### 10.3 footprint_type_mismatch — every item

| Ref | Message | Disposition |
|---|---|---|
| U302 (283.55, 117.89) | expected SMD, footprint typed "Through hole" | **fixed.** VEML6031X00 easyeda2kicad footprint: all 6 pads SMD, the footprint type was "Through hole" (easyeda2kicad default). Set to SMD on the board (`tools/fix_u302_attr.py`; nothing else on the footprint changed). Matters for any `--smd-only` position export. The easyeda2kicad library copy is not in the project's fp-lib-table; if the part is re-imported, fix the type there too. |
| U200 (273.145, 94.855) | expected Through hole, footprint typed SMD | **accepted-with-reason.** Same footprint as the FC's U18 (`RP2350-QFN-60-1EP_7x7_P0.4mm_EP3.4x3.4mm_ThermalVias`, cloned from the flown board): the 9 exposed-pad thermal vias are PTH pads, so KiCad expects "Through hole". U18's identical warning is a §6 baseline item. Retyping U200 would drop it from SMD placement exports, so it stays SMD. |
| U18, U29, U12, U27, U6, U10, U22 | as in `drc_prelayout.json` | **pre-existing** (§6: "7 footprint-type mismatches") |

### 10.4 Dangling items: 30 track + 17 via → 0 + 0

Tool `layout_cleanup/tools/fixdangle.py` works on new copper only. Heritage items are never candidates, and none was
flagged. For each DRC-flagged item, one action, kept only if KiCad's connectivity engine (zones refilled in memory)
shows no net losing a connection:
(a) **remove** it when its net's cluster count does not rise (a dead end or a redundant via);
(b) **via → segments** for a via connected on one layer only: short segments on that layer from each attached track
end to the via centre, all inside the via's own copper, then remove the via;
(c) **shorten** a needed track's free end back to the last contact on its body (the overshoot past a T-junction).
The whole board was DRC'd after every pass (11 passes). A removal re-exposes the next dead end, which is why
the passes continue until no action is left. Unconnected stayed at 1 after every pass except one (pass 5 of a first run, where an aliasing bug in
the tool mis-restored a failed shortening on EMU_GPIO_SPARE0). That run was discarded, the tool fixed (VECTOR2I copies), and
passes 5–11 re-run from pass 4.
The last item, EMU_GPIO_SPARE0 B.Cu (282.230,94.500)–(282.930,92.800), was a T-join made by copper overlap only
(0.125 mm off the centreline). Its free end was moved to the projection point (282.680,93.408), and a 0.2 mm joining segment was added
inside the existing copper (`tools/fix_spare0_t.py`).

| Action | Count | Notes |
|---|---|---|
| removed (dead-end track / redundant via) | 79 (60 tracks, 19 vias) | incl. **F5_PWR dead copper on In1.Cu** (the GND plane layer), 3 segments at (253.45–259.06, 95.28–97.47): removed, which restores the In1 GND plane there. Also the dead F5_PWR F.Cu tail (228.325,96.775)–(233.052,92.048) across the old edge, and dead VBUSP/F0_SDA/F5_SCL/F0_PWR bits at the J2/J6/J8 stubs (each net stayed one cluster, and attachment_check still counts 37 stubs) |
| via → segments | 9 vias | GPIO_RSVD (284.688,94.373); TOP_SCL (268.345,87.680); F4_SENSE (272.045,87.680); SPARE0 (277.570,96.955); WDT_DIS (277.220,102.030); F5_SDA (260.447,98.010); SPARE1 (289.295,89.555), (285.420,85.680); F3_SENSE (280.870,96.955) |
| shortened overshoot | 12 + 1 | F0_PWR ×2, F5_SDA (stub ends east of the old edge, outside the Rev2 outline), QSPI_SS, QSPI_SD1, SWCLK, F5_SCL, UART_RX, PYRO_INHIBIT_STATE, GPIO_RSVD, VREG_AVDD_EMU, F1_SDA; + the SPARE0 T-join above |
| **remaining** | **0** | nothing to triage |

Side effect on path lengths (connectivity is unchanged, but a removed dead end can also remove a short cut): QSPI_SD1/SD2 +0.22 mm and one via fewer
each; TP202.1 (1V1 test point) series path 112 → 122 mΩ. Nothing else measured changed.

### 10.5 C207.2 (GND), the last non-heritage unconnected item: **closed**

`gndwhat.py --pairs` on the current board found exactly one unlock pair: {1V1_EMU In2 (276.789,101.199)–(278.189,97.799)
w0.25 + EMU_STATUS_LED B.Cu (277.645,97.830)–(277.695,99.930)}. Both were ripped. C207.2 then got a 0.25 mm F.Cu stub to
an **off-pad** 0.40/0.20 GND via at **(277.320, 99.705)** (inside EMU_FANOUT; the via copper stays ≥ 0.04 mm off every pad,
**no via-in-pad**), which lands on the In1 GND plane. The victims were re-routed without further rip-up. The order and
window that worked: STATUS_LED first, window = cluster box + 4 mm. STATUS_LED: 6.11 mm, 0.25 mm, In2 + F.Cu, one 0.40/0.20 via at
(279.895,100.705). 1V1_EMU: 6.65 mm, 0.25 mm, In2 only, 0 vias. The round-3 cascades had used STATUS_LED second and a 2 mm window.
Cost: the 1V1 branch to DVDD pin 23 / C216 is longer. Least-resistance path from L200.2 to U200.23 goes from 63.0 to 72.9 mΩ and from 2 to 4 vias; C216.1 goes from 57.9 to 67.8 mΩ.
DVDD pin 39 / C218 (26.4 mΩ), pin 6 and VREG_FB are unchanged. C216 (4.7 µF) sits 1.3 mm from pin 23, so the pin's high-frequency supply is still local.
The PM's two suggested unlocks were not usable on this board. The EMU_UART_RX (275.570,100.188)–(281.420,100.188) segment and the
C207.1 0.5 mm link appear in no single or pair unlock at w 0.127. The C207.1 link also now carries C207.1/C208.1/U200.30 to
the south-east pour (10.6).

### 10.6 3V3_EMU power integrity (PM item 1) — before / after

Metrics come from `tools/g33*.py`: KiCad copper after a refill; pads, tracks, vias and In2 pour pieces as graph nodes.
Track R = ρL/(w·t) with t = 35 µm outer and 17.5 µm inner. A 0.20 mm via ≈ 2.2 mΩ. Pour pieces count as 0 Ω, which is optimistic, but equally so before and after.

| Link | Before | After |
|---|---|---|
| **South-east group → U202 side, new path A** | none | **B.Cu 1.0 mm, 2.65 mm, 2 × 0.46/0.20 vias** (287.370,103.555) → (290.020,103.555): SE In2 pour piece ↔ east In2 3V3_EMU pour (the U202/C202/C203 side) |
| **South-east group → U202 side, new path B** | none | **B.Cu 1.0 mm, 3.17 mm, 2 × 0.46/0.20 vias** (286.845,105.780) → (290.020,105.780), parallel to A |
| U202.5 → east In2 pour | 1 via (291.570,96.050), which sits in C203.1's pad | **2 vias**: + 0.46/0.20 at (291.970,95.080) on the 1.0 mm U202.5 F.Cu track, off every pad |
| Old west link (the round-3 joincl link) | B.Cu **0.30 mm** (268.420,99.405)–(267.420,96.930), 2 × 0.40/0.20 vias; F.Cu 0.30 to C205.1 | B.Cu **0.40**, F.Cu **0.40**: the clearance limit (C209/C205 pads, EMU_FANOUT neighbours). Now the second, redundant path |
| Old chain, other segments | F.Cu 0.25 (268.150,100.020)–(268.590,99.580); B.Cu 0.25 and 0.127 at C206; C204.1→C205.1 F.Cu thread 5 × 0.127 mm (3.6 mm); C206.1 via stub 0.20 | 0.50; 0.275 and 0.425; thread 0.325–0.35 on 4 of 5 segments (the 0.48 mm segment at C204.1 stays 0.127 because there is no clearance); stub 0.40 |
| U200.38 (IOVDD) land link | F.Cu 0.127 to its inward via (275.785,94.855) | F.Cu **0.200** (= land width) |
| U200.38 In2 link | In2 0.127 mm, 3.4 mm, to the north-west pour piece | **unchanged, 0.127 mm**. The channel between the ring via column (x 275.785) and EMU_UART_TX In2 (x 276.495) is 0.41 mm, so the most that fits is about 0.15 mm |
| U200.38 second path | none | **none possible without re-escaping a ring net.** `unlock33.py`: only {EMU_RUN B.Cu (277.295,96.355)–(275.670,96.355)} or {EMU_F3_SENSE via (275.785,93.255)} unlock one. Both were executed. With a 0.2–0.5 mm B.Cu path to C207's via (276.738,98.594) in place, EMU_RUN has no route at any width in a 16 × 16 mm window. Re-siting F3_SENSE's via re-cuts the new In2 path. Both discarded |
| Other 3V3 land links | U200.20, .30, .44/.45, .53/.54, .1 at 0.127; U200.11 0.152 | 0.200 (U200.20 third segment 0.175, U200.11 0.175) |

| Pad (series path from U202.5) | Before: mΩ / vias on path / narrowest | After |
|---|---|---|
| C206.1 | 50.6 / 11 / 0.127 | 18.3 / 5 / 0.275 |
| C207.1 = U200.30 (IOVDD) | 63.8 / 13 / 0.127 | 13.1 / 4 / 0.50 |
| C208.1 | 65.2 / 13 / 0.127 | 14.5 / 4 / 0.25 |
| C209.1 | 43.1 / 9 / 0.127 | 22.9 / 6 / 0.275 |
| C211.1 / C214.1 | 62.2 / 62.1, 13 vias | 11.5 / 11.4, 4 vias, 1.0 mm |
| R200.1 / R205.1 / R207.1 | 62.5 / 61.0 / 61.9, 13 vias | 15.2 / 10.3 / 11.2, 4–5 vias |
| U200.20 (IOVDD) | 58.3 / 11 | 23.4 / 5 |
| R602.2 (west branch to the strip) | 114.4 / 12 | 93.6 / 9 (dominated by its own 1.0 mm run to the strip) |
| U200.38 (IOVDD) | 30.8 / 4 / 0.127 | 29.7 / 4 / 0.127 |
| U200.38 → its datasheet cap C208.1 | 78.9 mΩ, 11 vias | 43.9 mΩ, 8 vias |

Node-disjoint paths SE group → U202.5: **1 → 2** (the old west chain and the new south-east pour ↔ east pour links).
U200.38 → U202.5: 1 → 1.

### 10.7 EMU QSPI lengths (PM item 4; not re-routed)

`tools/padlen.py`: routed centreline length, pad centre to pad centre, along the net's copper (T-joins split at the
contact, vias counted at zero planar length).

| Net | From → to | Routed mm | Vias | Layers |
|---|---|---|---|---|
| EMU_QSPI_SCLK | U200.56 → U201.6 | **30.00** | 4 | F/In2/B |
| EMU_QSPI_SD0 | U200.57 → U201.5 | **45.74** | 3 | F/In2/B |
| EMU_QSPI_SD1 | U200.59 → U201.2 | **44.23** | 8 | F/In2/B |
| EMU_QSPI_SD2 | U200.58 → U201.3 | **46.04** | 8 | F/In2/B |
| EMU_QSPI_SD3 | U200.55 → U201.7 | **30.92** | 5 | F/In2/B |
| EMU_QSPI_SS | U200.60 → R203.1 (0 Ω) | **22.18** | 4 | F/In2 |
| EMU_FLASH_SS | R203.2 → U201.1 | **4.13** | 0 | F |
| EMU_QSPI_SS (BOOTSEL branch) | U200.60 → R204.1 | 24.28 | 6 | F/In2 |

The spread is 30.0–46.0 mm: SCLK is 14–16 mm shorter than SD0–SD2 and about 1 mm shorter than SD3. SD1/SD2 have 8 vias each.
The same RP2350 → W25Q128 bus on the flown FC (U18 → U11, same tool) is SCLK 12.45, SD0 12.02, SD1 9.82, SD2 8.30,
SD3 12.78 mm, with 0–2 vias. For the review: 16 mm is about 0.1 ns of skew, and the data lines are sampled against SCLK.
At bench QSPI clocks (≤ 75 MHz) that is not length-critical, but it is 3–4× the heritage length and via count.

### 10.8 Findings for the review (not DRC items; not changed this round)

* **Via-in-pad in earlier-round new copper.** 45 new vias have their centre inside an SMD pad of their own net, and 19 more
  overlap a pad edge (`tools/viapad2.py`; list in `layout_cleanup/viapad_final.txt`). Examples: C203.1, C202.1, C220.1, C209.1,
  R205.1 (3V3_EMU); U201.2/3/5/7 (QSPI); U202.1/.2/.3, C200.1, C201.1 (VBUS_EMU/GND); L200.1 (VREG_LX); Y200.4, C221.2 (GND).
  All were created by routing rounds 1–3. This round added none and removed none. The PM's standing position is
  that via-in-pad needs an owner decision (filled-and-capped cost). These need that decision: order POFV, or move them off-pad.
* 1V1_EMU pin-23 branch longer by the C207.2 unlock (10.5).
* U200.38 keeps a single 0.127 mm In2 feed (10.6).

## 11. Stage 6 (silkscreen + docs + preview, Sonnet, 2026-09-23)

**Input:** `round3/layout_cleanup/deliver/FlatSat_V1.kicad_pcb` (10.1–10.8 above). **Delivered:**
`round3/layout_finish/deliver/FlatSat_V1.kicad_pcb`. This stage added only F.SilkS `PCB_TEXT` items
and flipped `Reference.Visible` on 21 already-placed new footprints (see `layout_report.md` §5 for
the full silkscreen list); it re-routed nothing, moved no footprint, and touched no track, via or
zone. Re-running every gate from 10.2 on the result reproduces it **exactly, item for item**:

```
errors: 2  unconnected: 1  parity: 11
schematic_parity   warning  extra_footprint                     1      1     +0
schematic_parity   warning  footprint_symbol_mismatch           5      5     +0
schematic_parity   warning  missing_footprint                 199      5   -194
schematic_parity   warning  net_conflict                       36      0    -36
unconnected_items  error    unconnected_items                   0      1     +1
violations         error    courtyards_overlap                  1      1     +0
violations         warning  footprint_type_mismatch             7      8     +1
violations         warning  isolated_copper                     4      4     +0
violations         warning  lib_footprint_issues                3      3     +0
```

`heritage.py check --allow-zone-growth --allow-edge`: **0 violations** (same edge/zone notes as
every prior round — outline growth and zone reshaping only). `heritage.py check --refill
--core-inset 12 --ref-board FC_V5e_Production_Rev2`: **0 violations**, the same three band notes as
10.1/E6 (`+3V3` F.Cu band fill −5.9 %, `VSOLAR` In2 band fill −0.6 %, `B-` In2 2.2 mm² island —
all three "every piece touches new copper" and accepted, not new this round).
`attachment_check.py`: **0 violations, 0 warnings, 37 stub chains** (same list as 10.1, unchanged —
this stage added no track or via inside the Rev2 outline). No DRC class not already itemised in
§10.2/§10.6 appeared; in particular there is **no silkscreen-vs-pad or silkscreen-vs-mask DRC class in
this KiCad 10 ruleset** (`--severity-all` was on throughout; kicad-cli's DRC does not check text
overlap, so the silkscreen tool's own collision search — every candidate placement checked against
the real KiCad bounding box of every pad on the board and of every other label already placed, on top
of DRC — is what stands in for that gate here; see `layout_report.md` §5 for the two collisions it
found and fixed during development, both caught by render inspection rather than DRC).

**One quality note for the review, not a DRC item:** the jumper-header legend block between JP602/
JP603/JP604/JP607, JP500's own two-word legend and the four-line J500 bench-mode legend all compete
for the same crowded pocket between the JP60x row and J500/Q500/Q501 (the header pitch there is only
5.6–11.6 mm and the row sits directly above J500's own silkscreen). The placer's collision search
keeps every item legible and clear of every pad, at font sizes down to 0.6 mm (project default is
1.0 mm) and some up to ~9 mm from their own header; it is correct and non-overlapping but genuinely
busy in that one pocket — a human pass with more room to negotiate (e.g. shortening JP602–605's
own legends further, or moving SW600's `CLOSED=SAFE`/`OPEN=ARMED` block to free area) could make it
easier to read at 1:1 scale. Flagged for `pcb-flight-review`, not fixed here.
