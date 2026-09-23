# PROVES FlatSat V1 — Phase 2 build stage (outline + ground + netclasses) report

**Date:** 2026-09-20 · **Stage:** 3 (Outline + ground) · **Owner:** Sonnet build agent · **Input:** owner-approved `floorplan_v2_3.json` (panel-fixed v2.3) · **Live board `FlatSat_V1/FlatSat_V1.kicad_pcb`: not written.** Result delivered as a copy only.

## 0. Tool fix made in this stage

`tools/pcb/build_floorplan.sh`'s project-siblings copy step did not copy `Backup_Footprints/` (the project's `fp-lib-table` resolves `RTC`, `SOT26`, `RP2350_60QFN_minimal`, `Molex …`, `SuperCap`, `SN74HC595DR` there). On the first build this produced 18 spurious `lib_footprint_issues` warnings (vs. 3 in the pre-layout baseline) because those libraries could not be found inside `OUT_DIR/proj/`. Fixed the copy line (added `Backup_Footprints` alongside `symbols`/`footprints.pretty`) and rebuilt; `lib_footprint_issues` returned to exactly the baseline 3 (`REF**`, `U10`, `IC6`). This is a tool fix in the repo (`tools/pcb/build_floorplan.sh`), not a board edit — no board file, heritage snapshot or live board touched.

## 1. Command run

```
tools/pcb/build_floorplan.sh docs/flatsat/2026-09-14_phase2_layout/floorplan_v2_3.json <OUT_DIR> \
    FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb
```
from the live `FlatSat_V1/FlatSat_V1.kicad_pcb`, into `OUT_DIR/proj/` (board + `.kicad_pro`/`.kicad_dru`/schematics/libraries copied alongside, per the tool's own warning about factory-default rules on a bare board copy).

## 2. Outline

Single outline, 3 holes (2 pre-existing heritage rounded slots near the top corners + the new J12 USB-C plug relief slot). Board bounding box **x 143.292–296.440 mm, y 47.514–172.170 mm** (153.05 × 124.66 mm envelope), outline area **184.10 cm²** (18410.45 mm² from `kicad-cli pcb stats`). L-extension applied per `outline_L1.json`: right wing to x = 296.44, bottom strip to y = 172.17, 4 mm corner radii matching the FC's existing arcs.

J12 relief slot (`cutouts` key, floorplan v2.3 change #2): x 228.00–243.00, y 71.50–85.70, corner r 1.5 mm — visible as the square notch through the wing in both the top and bottom renders, directly opposite the FC's own USB-C J12.

**New mounting holes (H10–H12, board-only, exempt from parity):**

| Ref | x (mm) | y (mm) |
|---|---|---|
| H10 | 292.39 | 51.58 |
| H11 | 292.39 | 168.12 |
| H12 | 147.30 | 168.12 |

(H1/H2, heritage, unmoved: H1 147.3/138.0, H2 227.3/138.0.)

## 3. Zones

45 zones total (41 heritage + 4 new): new GND pours added on F.Cu/B.Cu over the wing and strip (`GND_F_Cu_wing` priority 1, `GND_F_Cu_strip` priority 2, `GND_B_Cu_wing` priority 1, `GND_B_Cu_strip` priority 2 — distinct priorities per overlapping-pour requirement). In1 GND plane grown over the whole new outline (heritage GND zone, `grown` noted by `heritage.py`, old outline fully contained). No new In2 pours (per L6, In2 nets stay FC-only at this stage; In2's 3V3_EMU/PYRO_INHIBIT_STATE pours are a routing-stage (F9) item). All heritage zone outlines inside the flight core are byte-identical after refill (0 band-fill notes — v2.3's J12 slot sits outside the Rev2 outline so no flight-section fill was disturbed); heritage zone polygons are clipped to the Rev2 outline by `outline.py` so no FC-net pour extends into the extension. 68 GND stitching vias added along the new perimeter and around the emulator core / J12 relief slot (≤ 10 mm spacing, all on GND, all outside the Rev2 outline — 0 non-GND new vias).

## 4. Netclasses (`tools/pcb/netclasses.py` on `OUT_DIR/proj/FlatSat_V1.kicad_pro`)

Classes written (`classes added: ['BenchPower', 'USB_EMU'] | patterns now: 12`):

| Class | Clearance | Track | Via dia/drill | Diff-pair width/gap | Patterns |
|---|---|---|---|---|---|
| Default (unchanged) | 0.20 | 0.25 | 0.8 / 0.4 | 0.20 / 0.25 | — |
| **BenchPower** | 0.25 | 1.00 | 0.8 / 0.4 | — | `VBAT_BENCH_N`, `VSOLAR_BENCH_A`, `VSOLAR_BENCH_B`, `VBUS_CHG`, `CHG_SYS`, `CHG_BAT`, `CHG_PMID`, `VBUS_EMU`, `3V3_EMU`, `MID_BENCH` (10 nets) |
| **USB_EMU** | 0.20 | 0.25 | 0.6 / 0.3 | 0.25 / 0.15 | `EMU_USB_DP`, `EMU_USB_DM` (2 nets) — scoped exactly to the emulator's own USB pair, **not** J701's connector-pad nets (which stay Default, per panel note PLM-09/NETCLASS item (a)) |

12 `netclass_patterns` entries total, confirmed by re-reading the written `.kicad_pro`. `1.5 mm` routing widths for `Dir_Chrg_In`/`B-`/`VBUSP`/`VBATT_SENSE`/`INHIB_x`/`IN_RBF`/`VSOLAR` and the U200/U511 0.45/0.20 escape-via override remain routing-stage instructions (L5, panel NETCLASS items (b)/(c)) — no netclass exists for them because they are FC nets/local overrides, not new classes; flagged for the routing stage.

## 5. Floorplan-level panel items (F10/PLM-09, PLM-07)

- **PLM-07 SW703 courtyard** — added an `F.CrtYd` rectangle (x 243.75–257.20, y 63.75–71.20, the panel's measured real bbox + 0.25 mm) directly to the SW703 footprint instance on the board (the `easyeda2kicad` library copy is not present on disk locally as a `.kicad_mod`, so the courtyard graphic was added to the board-embedded footprint definition itself — same effect, same footprint, no heritage part touched). Confirmed picked up by `fp.GetCourtyard(F_CrtYd)` (1 outline) and produces no new courtyard-overlap violation (nearest real gaps to Q701/Q702/Q703 unchanged, ~1 mm).
- **PLM-09 fiducials** — **not placed as copper this stage; recorded for stage 5**, per the panel's own finding ("the copper lands at stage 5") and the task's stated option. Attempted adding two `Fiducial_1mm_Mask2mm`-equivalent footprints (1 mm F.Cu pad, 2 mm mask opening, no net) at the two primary sites; FID1 at (232.5, 50.5) sits only ~0.60 mm (copper) / ~0.80 mm (hole) from one of the new GND stitching vias placed by `outline.py`'s ≤10 mm perimeter rule, which the reserved-site clearance check (parts only, 3.35 mm) did not cover — a 2 mm mask opening at that site bridges the GND pour underneath a differently-netted pad (`solder_mask_bridge` at 0 mm pad clearance) and cannot reach the 1 mm effective clearance the mask opening needs without violating via-to-pad clearance against that same stitching via. Removed both trial footprints rather than force a marginal fit or reduce the spec'd 1 mm/2 mm dimensions. **Reserved sites for stage 5 to re-verify against the final stitched perimeter and place fiducial copper (or relocate the one stitching via at (232.5, 50.5) by ≤2 mm first):** (232.5, 50.5) primary — conflicts with a stitching via, needs a ≥1 mm-clear site check first; (252.0, 140.0) primary — not rechecked after removal, should be clear (fallbacks (262.0, 50.0) / (262.0, 140.0) also on file per PLM-09 if needed).

## 6. Pad-to-pad clearance exemptions (`.kicad_dru`, project-local copy in `OUT_DIR/proj/`)

Once the L5 netclasses were applied (BenchPower's 0.25 mm clearance is stricter than Default's 0.20 mm), `kicad-cli pcb drc` reported 40 pad-to-pad clearance errors, all intra-footprint on 5 new, datasheet-audited refs (all gaps clear JLCPCB's 4-layer fab minimum of 0.127 mm):

| Ref | Part | Gaps seen | Class in force |
|---|---|---|---|
| U200 | RP2350 QFN-60, 0.4 mm-pitch escape pattern | 0.2000 / 0.2121 mm | BenchPower (adjacent 3V3_EMU pads) |
| J701 | Emulator USB-C receptacle (24-pin) | 0.2000 mm (A/B row) | BenchPower (VBUS_EMU pads) |
| J510 | Charger USB-C receptacle (24-pin) | 0.2000 mm (A/B row) | BenchPower (VBUS_CHG pads) |
| Q510 | Dual-MOSFET SOT23-6 | 0.1900 / 0.2400 mm | BenchPower / Default |
| U301 | Face-0 reference IC, SOT/DFN | 0.1500 mm | Default |

Added a second `memberOfFootprint('REF')` rule (`phase2-fine-pitch-pad-pitch`) to `OUT_DIR/proj/FlatSat_V1.kicad_dru`, alongside the FC's existing `fine-pitch-pad-pitch` rule for U7/U15/U8/U16, relaxing intra-footprint clearance to 0.127 mm for **U200, J701, J510, Q510, U301** only — never a netclass-wide clearance reduction. Tracks/vias/zones near these pads keep the full BenchPower/Default clearance. Re-ran DRC after: clearance errors 40 → 0.

## 7. Hand-back gates (final, after all steps above)

```
$ heritage.py check heritage_rev2.json <board> --allow-zone-growth --allow-edge --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2.kicad_pcb
note: new items: footprints +221, tracks/vias +68, zones +4
heritage check: 0 violation(s)

$ attachment_check.py heritage_rev2.json <board>
attachment check: 68 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)

$ kicad-cli pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones --output drc4.json <board>
$ drc_summary.py drc4.json --baseline drc_prelayout.json
section            sev      type                             base    now  delta
schematic_parity   warning  extra_footprint                     1      1     +0
schematic_parity   warning  footprint_symbol_mismatch           5      5     +0
schematic_parity   warning  missing_footprint                 199      5   -194
schematic_parity   warning  net_conflict                       36      0    -36
unconnected_items  error    unconnected_items                   0    383   +383
violations         error    courtyards_overlap                  1      1     +0
violations         warning  footprint_type_mismatch             7      9     +2
violations         warning  isolated_copper                     4      4     +0
violations         warning  lib_footprint_issues                3      3     +0
total baseline 256, now 411
errors: 384  unconnected: 383  parity: 11
```

- **Heritage: 0 violations.**
- **Attachment (L11): 0 violations**, 68 new tracks/vias (all GND stitching, all in the extension).
- **Parity: 11** = exactly the §6 baseline (1 extra_footprint `REF**` + 5 footprint_symbol_mismatch + 5 missing_footprint = H1/H2/TP9–13 group). No new parity drift.
- **DRC errors beyond baseline:** `courtyards_overlap` 1 — the known, accepted Rev2 item (`SW2`/`TP2`, confirmed by inspecting the violation, unrelated to SW703's new courtyard); `unconnected_items` 383 — expected, nothing is routed yet (this is the routing stage's job). **0 clearance errors** after the `.kicad_dru` exemptions above.
- **New warnings, both attributable to Phase-2 parts:** `footprint_type_mismatch` +2 (`U200`, `U302` — SMD/THT pad-vs-symbol-type mismatches on the new emulator MCU and Face-0 reference IC footprints, same class of warning as the 7 pre-existing heritage items, not a defect). `isolated_copper`/`lib_footprint_issues` unchanged at baseline (0 new).
- **Outside-outline: 0** (`apply_placement.py`: `applied 218; refused (heritage) []; missing refs []`, no outside-outline report).
- **Courtyard overlaps among new parts: 0** (`apply_placement.py`: `courtyard overlaps (same-side, >=1 new part; real polygons): 0: []`; SW703's new courtyard does not introduce one).
- **Render:** `top.pdf`/`bottom.pdf` (A3) show the full L-shaped board — Rev2 flight section intact on the left, bench-I/O column + emulator core + face-front-end column + VSOLAR injection on the wing, pyro-inhibit/battery-replica/charger on the strip, J12 relief slot visible as the cutout square opposite the FC's own USB-C, all 218 new parts inside the outline.

## 8. Open items for later stages

- Fiducial copper (PLM-09): deferred to stage 5 per §5 above; re-check (232.5, 50.5) against the final stitching-via layout first.
- U200/U511 0.45 mm pad / 0.20 mm drill escape-via override and the 3V3_EMU west-branch width exception (panel NETCLASS items (b)/(c)): routing-stage instructions, not applicable until vias exist.
- 3V3_EMU / PYRO_INHIBIT_STATE In2 pours (F9): routing stage.
- Everything else in `panel/panel_fix_plan.json`'s `routing_instructions` and `deferred` sections is unchanged and still applies to stage 4.

## 9. Deliverable

Board copy: `OUT_DIR/proj/FlatSat_V1.kicad_pcb` (with its `.kicad_pro`/`.kicad_dru`/schematics/`symbols`/`footprints.pretty`/`Backup_Footprints` siblings in the same directory). Live board `FlatSat_V1/FlatSat_V1.kicad_pcb` untouched; nothing committed.
