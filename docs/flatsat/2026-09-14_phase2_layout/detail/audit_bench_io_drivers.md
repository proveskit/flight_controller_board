# Independent audit — block `bench_io_drivers` (Q701–Q703, R705–R710, SW703)

**Auditor:** Sonnet agent, Phase 2 stage 2b independent audit · **Date:** 2026-09-14
**Role:** refute, not confirm. Own checklist built from primary sources; placer's checklist
(`detail/placement_bench_io_drivers.md`) read only after forming the checklist, then used solely to
identify claims to re-verify independently.
**Board audited:** `<scratch>/detail_bench_io_drivers/placed.kicad_pcb` (re-derived independently —
see §3 — byte-identical to the placer's file).
**Verdict: PASS — 0 must-fix, 0 should-fix, 1 note (pre-existing, non-blocking).**

## 1. What is actually in this block (verified against the schematic and the board, not the placer's memo)

Read `FlatSat_V1/bench_io.kicad_sch` directly (not the placer's md) and confirmed by symbol
property text:

| Ref | `lib_id` | Value | Footprint | Datasheet field |
|---|---|---|---|---|
| Q701/Q702/Q703 | `Transistor_FET:BSS138` | BSS138 | `Package_TO_SOT_SMD:SOT-23` | `https://www.onsemi.com/pub/Collateral/BSS138-D.PDF` |
| R705/R707/R709 | `mainboard:RESISTOR0603` | 1k | `Resistor_SMD:R_0402_1005Metric` | (none) |
| R706/R708/R710 | `mainboard:RESISTOR0603` | 4.7k | `Resistor_SMD:R_0402_1005Metric` | (none) |
| SW703 | `Switch:SW_SPDT` | SS12D10G4 | `easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4` | LCSC PDF |

Netlist read directly from the placed board with `pcbnew` (not from the schematic text, so this
also validates the footprint's pin-to-function mapping is what the placer assumed):

- Q70x pad 1 = gate (net `Net-(Q70x-G)`), pad 2 = **GND** (source), pad 3 = FC net (drain):
  Q701.3→`FC_RESET`, Q702.3→`USBBOOT`, Q703.3→`WDT_DISABLE`.
- R705/R707/R709 (1k): one pad on `EMU_CTL_*`, one pad on the shared gate net — these are the
  **gate-series** resistors.
- R706/R708/R710 (4.7k): one pad on `GND`, one pad on the shared gate net — these are the
  **gate-pulldown** resistors.
- SW703 pad 1 = `WDT_DISABLE`, pad 2 = `GND`, pad 3 = `unconnected` (schematic-documented NC).

This matches the placer's description; independently confirmed the BSS138 SOT-23 pinout itself
(pin1=Gate, pin2=Source, pin3=Drain — onsemi/Fairchild/Diodes/Digi-Key datasheets all agree) so the
footprint-to-function mapping in the schematic is not just self-consistent, it is also correct
against the real part.

## 2. My own checklist (built before reading the placer's), with sources

No manufacturer layout section exists for this block's only active part (BSS138 — confirmed
independently, see row 1). No decoupling caps, dividers, crystal, ESD parts, inductor, or sense
resistor in this block, so the omission-classes the task asks auditors to specifically hunt for
(ground-return path, switching-loop area, crystal isolation, ESD-first ordering, Kelvin sense
access, inductor keep-out) are either covered by row 1's fallback or **not applicable** — there is
no crystal, no ESD part, no inductor, no sense resistor, no connector inside this block's own ref
list. I checked for all of them anyway (rows 8–9) rather than take the placer's "N/A" at face value.

| # | Rule | Source | Criterion | My independent measurement | Verdict |
|---|---|---|---|---|---|
| 1 | BSS138 has no PCB layout/application-circuit section | Fetched `https://www.onsemi.com/pub/Collateral/BSS138-D.PDF` myself via WebFetch, asked for every section heading | Layout guidance present y/n | Section list returned: Absolute Max Ratings, Thermal, Electrical, Off/On/Dynamic/Switching Characteristics, Drain-Source Diode Characteristics, Typical Characteristics. **No layout/application-circuit section.** Independently confirms the placer's fallback is the correct posture, not an excuse. | Confirmed — fallback justified |
| 2 | BSS138 SOT-23 pinout is G-S-D (1-2-3) | WebSearch across onsemi/Fairchild/Diodes/Digi-Key datasheets | Pin1/2/3 = Gate/Source/Drain | Confirmed by 4 independent datasheet sources; matches the board netlist exactly (§1) | PASS |
| 3 | Gate-series R (1k) sits closer to the gate pad than the gate-pulldown R (4.7k), for every FET | Fallback rule ("gate resistors at the FET gate") — series R suppresses transients from the long EMU_CTL trace before they reach the gate; this is the harder-to-satisfy sub-case the placer's own aggregate metric could mask | Per-FET: series-R distance < pulldown-R distance | Recomputed from raw pad coordinates (not trusted from the md): Q701 R705=4.446mm < R706=5.946mm; Q702 R707=4.738mm < R708=6.542mm; Q703 R709=4.293mm < R710=5.432mm. Consistent ordering on all 3 stages. | PASS |
| 4 | Worst single gate-node leg, any FET, stays short (≤ 8mm fallback threshold) | Fallback rule + task's own criterion | max(all 6 leg distances) ≤ 8mm | Recomputed independently from pad coordinates (not copied from placer's numbers): 4.293 / 4.446 / 4.738 / 5.432 / 5.946 / 6.542 mm. Max = 6.542mm. | PASS |
| 5 | v1 defect claim is real (R709/R710 sat under the wrong FET) | My own re-derivation, not taken on faith | Recompute v1 leg distances from `floorplan.json`'s own v1 coordinates + this board's local pad offsets | Q703↔R709(v1 slot) = 12.82mm, Q703↔R710(v1 slot) = 15.59mm — reproduced independently to the reported precision. v1 would fail row 4's own 8mm threshold; v2 does not. | Confirmed — genuine fix, not a cosmetic reshuffle |
| 6 | Source (GND) pad has a short return path available | Fallback ("shortest ground return") + `floorplan.json.new_gnd_pours` `GND_F_Cu_wing` (232,48.5)-(295.5,171.2) | Pad falls inside the **actual filled zone outline** on F.Cu, not just the nominal rectangle | Loaded the real `ZONE` objects from the board (not the JSON rect) and ran `SHAPE_POLY_SET.Contains()` against Q701.2/Q702.2/Q703.2/R706.1/R708.1/R710.1/SW703.2 — all `True`. Zone confirmed `IsFilled()=True`. 0 tracks/vias found inside the block envelope (board is genuinely unrouted, as stated). | PASS |
| 7 | Drain/common-pad attachment reach to the FC connector does not regress > 3mm vs v1 (brief L11) | `floorplan.md` §5 / brief L11 | \|Δreach\| ≤ 3mm per net, computed pad-to-pad, not trusted from the memo | Located J16 independently on the board (pos 222.5,71.0, rot 90°) and recomputed all three distances from raw pad coordinates: FC_RESET 27.567mm, USBBOOT 34.541mm, WDT_DISABLE 23.603mm — reproduced the placer's numbers to 3 decimal places from scratch, and independently confirmed Q701/Q702/SW703 pad positions are pixel-identical to v1 (0.000mm move) by loading `floorplan_preview.kicad_pcb` (the actual v1 applied board) directly, not just `floorplan.json`'s placement table. | PASS |
| 8 | No ESD/crystal/inductor/sense-resistor omissions | My own check of the ref list and schematic text, independent of the placer's "N/A" | Any such part physically in this block? | None — the block's only active silicon is 3× BSS138 in an open-drain sink configuration (never drives high) plus one mechanical switch; confirmed against the schematic text block at `bench_io.kicad_sch` line ~5580. | N/A confirmed, not just asserted |
| 9 | SW703 datasheet reviewed for any actuator/hand-clearance callout | LCSC PDF cited in the schematic (`SHOU-HAN-SS12D10G4-071`) | Any placement-relevant guidance | Not fetched in full — moot regardless of content: SW703 is this block's one fixed anchor and is **not moved or rotated** in this pass, so no placement decision in this pass is gated on it. Recorded for completeness per the task's instruction to look for omitted rule-classes, not counted as a checklist failure either way. | N/A (fixed anchor) |
| 10 | Fixed anchor SW703: position, rotation, side, footprint identical to v1 | Task's fixed-anchor rule | Compare against `floorplan.json` **and** the actual v1 board `floorplan_preview.kicad_pcb` (not just the JSON, in case outline.py/apply_placement.py altered it) | Loaded `floorplan_preview.kicad_pcb` directly: pos (250.475,67.475), rot 0°, side F, bbox (244.000,64.000)-(256.950,70.950) — **identical, to the mm, in the v2 placed board.** | PASS |
| 11 | Every one of the 9 movable refs stays inside the envelope `[242,64.5,262.5,80]` | Placement constraint (a) | Footprint bbox (incl. silkscreen/body) ⊆ envelope | Recomputed bboxes directly from `pcbnew.GetBoundingBox()` for all 9: Q701/Q702/Q703 and all 6 resistors are fully inside. | PASS |
| 12 | SW703 (fixed) envelope containment | Placement constraint (a), in tension with the fixed-anchor rule | Same bbox test | SW703 bbox top edge y=64.000 vs envelope y0=64.5 → 0.5mm over. **Verified this is not new**: identical bbox exists in `floorplan_preview.kicad_pcb`, the v1 board the owner already reviewed and accepted at the block level. Not something this pass could fix without violating "do not move or rotate the fixed anchor." | **NOTE** (pre-existing, disclosed, non-blocking — see §4) |
| 13 | 12.6mm keep-clear lane (`floorplan.json.lanes`, rect x 231.39–243.39) stays clear | `floorplan.json.lanes[0]` (read directly, not trusted from the memo — the actual rect right edge is x=243.39, and the lane's own `"rule"` field already documents "first new component left edge in this proposal is x=244.0") | No part's left edge < 243.39mm | Leftmost edges among this block's parts (Q703/R709/SW703) all at x=244.000 — 0.61mm clear, matching the lane definition's own note verbatim | PASS |
| 14 | No courtyard overlap anywhere on the board; nothing outside the outline | `apply_placement.py`'s real-polygon check | exit clean, 0/0 | **Re-ran the tool myself** (not just read the placer's transcript) against `outlined.kicad_pcb` + `merged_floorplan.json` already in the scratch dir: `footprints not fully inside the outline: 0`, `courtyard overlaps: 0`. Output file diffed **byte-identical** to the placer's `placed.kicad_pcb` (`diff` exit 0), so the board I measured everything above on is provably the same one the placer measured — no possibility the placer showed me a different board than they built. | PASS |
| 15 | ≥0.5mm courtyard-to-courtyard clearance | Placement constraint (h) | min gap ≥ 0.5mm between any two of this block's parts (and vs SW703) | Recomputed from raw `F.CrtYd` graphical-item bounding boxes (not the placer's numbers): R-pair-to-R-pair gaps 1.000mm ×4; Q-to-SW703 vertical gap 0.995mm; FET row to R row 1.105mm. All ≥0.5mm. | PASS |
| 16 | Heritage frozen | `heritage.py check ... --allow-zone-growth --allow-edge` | exit 0 | Re-ran myself: `heritage check: 0 violation(s)`. Also ran the identical command against the **untouched v1 board** `floorplan_preview.kicad_pcb` to confirm the `+221 footprints / +65 tracks-vias` "new items" note is a pre-existing whole-floorplan artifact, not something this block's rework introduced (identical note on both boards). | PASS |
| 17 | L11 attachment gate | `attachment_check.py` | exit 0, 0 violations | Re-ran myself: `65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)` | PASS |
| 18 | Merged floorplan touches only this block's 10 refs; no other `floorplan.json` key (outline/pours/holes/stitching/lanes/keepouts) was altered | Task's "merge... same keys, only your refs' entries replaced" requirement | Diff `merged_floorplan.json` against `floorplan.json` | Diff shows exactly 6 changed placement entries (R705–R710); Q701/Q702/Q703/SW703 entries and every non-`placements` key are byte-identical to `floorplan.json`. | PASS |

**rules_audited = 18** (12 numbered rows above the fixed-anchor tension, plus 2 fixed-anchor rows,
plus 4 gate/process-integrity rows). 0 must-fix, 0 should-fix, 1 note.

## 3. Reproducibility check (board identity)

Before trusting any measurement, I rebuilt the board myself from the artifacts already in
`<scratch>/detail_bench_io_drivers/` (not from the placer's prose):

```
apply_placement.py --board outlined.kicad_pcb --placement merged_floorplan.json --out audit_placed.kicad_pcb
# -> applied 218; refused (heritage) []; missing refs []
# -> footprints not fully inside the outline: 0: []
# -> courtyard overlaps (same-side, >=1 new part; real polygons): 0: []
diff placed.kicad_pcb audit_placed.kicad_pcb   # exit 0 -- byte-identical
```
All measurements in §2 were then taken with my own `pcbnew` scripts against this board (pad
positions, footprint/zone bounding boxes, zone-outline containment via `SHAPE_POLY_SET.Contains()`,
track/via enumeration), independent of the numbers printed in `placement_bench_io_drivers.md`. Every
number I recomputed matched the placer's reported figure to the last digit shown; none were taken on
faith.

## 4. The one note (not counted against the pass)

**SW703 top edge overhangs the block envelope by 0.5mm** (bbox y0=64.000 vs envelope y0=64.5). This
is a **pre-existing condition inherited unchanged from the v1 floorplan the owner already accepted
at the block level** — confirmed by loading `floorplan_preview.kicad_pcb` (the actual v1 board)
directly and finding the identical bbox, not merely by trusting the placer's assertion. SW703 is
this block's sole fixed anchor ("do not move or rotate"); no placement decision available to this
pass could change it. `apply_placement.py`'s real containment check (pad-copper vs outline, not
bbox-vs-envelope) does not flag it, and it is disclosed rather than hidden. Recorded for the owner's
visibility; not a defect of this rework and does not change the verdict.

## 5. What I looked for and did not find

- No evidence the resistor reassignment broke anything else on the board (heritage/attachment both
  0, courtyard check re-run independently, board-identity confirmed by diff).
- No orientation error: rotating any FET 180° would shorten its drain-to-J16 trace by ~1.9mm out of
  a 27–35mm total (≤7%) but would move the gate pad to the far side from the resistor pair,
  undoing the very fix this pass made to the higher-priority gate-loop criterion — current rot=0 is
  the correct trade-off, not an oversight.
- No BOM/value mismatch: all 6 resistor values (1k series / 4.7k pulldown per stage) match the
  schematic's own description of the RP2350 erratum-E9 gate-divider requirement.
- No routing artifacts: block envelope contains 0 track/via endpoints, consistent with "nothing is
  routed" for this stage.
- No hidden footprint substitution: `lib_id`/footprint/datasheet fields read directly from the
  schematic match the board.

## 6. Conclusion

The placer's re-assignment of R705–R710 to the three existing slot-pairs (unchanged geometry, only
the ref-to-slot mapping changed) is a genuine, independently-reproduced fix to a real v1 defect
(worst gate-loop leg 15.59mm → 6.542mm), achieved with zero macro-layout risk (Q701/Q702/Q703/SW703
provably unmoved, both against `floorplan.json` and against the actual v1 board). All gates
(heritage, attachment, courtyard/outline) were re-run independently and reproduced exactly, on a
board file confirmed byte-identical to the one the placer measured. One pre-existing, disclosed,
non-actionable envelope note on the fixed anchor SW703 does not change the verdict.

**verdict: PASS**
