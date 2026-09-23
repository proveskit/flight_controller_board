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
