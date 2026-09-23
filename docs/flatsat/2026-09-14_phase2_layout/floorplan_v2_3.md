# PROVES FlatSat V1 — floorplan v2.3 (panel fixes applied)

**Date:** 2026-09-20 · **Built by:** PM, `tools/pcb/build_floorplan.sh` · **Status: awaiting the owner's go for routing — nothing routed, nothing committed since checkpoint `d56c9df`, live board untouched.**

v2.3 = floorplan v2.2 (`floorplan_v2.md`) plus the placement-level outcomes of the stage 2c review panel (`panel/floorplan_v2_panel_review.md`, verdict fix-then-route) and the owner's two decisions of 2026-09-20 (brief §12 F5–F10). Only the `placements` entry of J701, a new `cutouts` key and the `stitching` points changed; outline, pours, holes, lane and the other 217 placements are byte-identical to v2.2.

| File | What |
|---|---|
| `floorplan_v2_3.json` | Floorplan of record for the build stage (`based_on_v2_3` records the provenance) |
| `floorplan_v2_3_preview.kicad_pcb` (+ `.kicad_pro`, `.kicad_dru`, `.kicad_prl`) | v2.3 applied to a fresh copy of the live board, page A3, unrouted |
| `img/floorplan_v2_3_top.png`, `_bottom.png` | Whole-board renders |
| `img/floorplan_v2_3_j701.png`, `img/floorplan_v2_3_j12_slot_top.png` | Close-ups of the two changes |
| `panel/v2_3_drc.json` | kicad-cli DRC (parity, refilled) on the preview |

## What changed since v2.2

| # | Change | Source | Detail |
|---|---|---|---|
| 1 | **J701 (emulator USB-C) rotated 180°** and moved to (275.000, 51.874) | panel blocker PLM-01, PM | At rot 0 the pad row faced the north edge and the mating slot faced the board interior — no plug could be inserted. Now the mating face is 0.100 mm off the north edge (the flown FC J12 has 0.165 mm), pad row at y 55.92, 1.84 mm courtyard gap to R701/R702, 3.48 mm to J702, pad copper 2.45 mm from the edge. |
| 2 | **Relief slot through the wing in front of the FC's USB-C J12** | panel blocker PLM-02, **owner decision** | J12 is surface-mounted on the bottom side at the old edge and opens east; a plug's overmold needs open air where the wing now is. Slot x 228.0–243.0 (0.5 mm past the receptacle face, up to the lane edge), y 71.5–85.7 (J12 centre 78.6 ± 7.1 mm for the 12.35 mm max overmold), corner r 1.5; `outline.py` gained the `cutouts` key. No part on either side within 0.5 mm of it. The In1 GND plane and the wing pours tie around it through the north and south bars. |
| 3 | Stitching: 2 points inside the slot removed, 5-point GND ring added on its north/south/east sides (none on the west: that is the FC edge) | with 2 | 68 stitching vias, all on GND |

Rulings that changed rules rather than the floorplan (brief §12): one B.Cu→F.Cu via per bottom-side-connector stub (F6, gate amended and unit-tested), J14 pins 10/12 stub allowance 22 mm (F7), 3V3_EMU / PYRO_INHIBIT_STATE routed on In2 (F9). The remaining panel items are routing-stage instructions in `panel/panel_fix_plan.json` and minors deferred there.

## Gates (rebuilt from the pristine live board with the project files beside the board)

| Gate | Result |
|---|---|
| `apply_placement.py` | applied 218 · refused 0 · outside outline 0 · courtyard overlaps 0 (real polygons) |
| `heritage.py check --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2` | **0 violations, 0 band-fill notes** — the slot's edge clearance stays outside the Rev2 outline |
| `attachment_check.py` | 68 new tracks/vias, 0 stub chains, **0 violations**, 0 warnings |
| Board outline | 1 outline, 3 holes (two heritage slots + the J12 relief), 184.1 cm² |
| kicad-cli DRC (parity, refill) | parity 11 = the FC baseline · courtyards_overlap 1 (heritage SW2/TP2) · clearance 7 (intra-footprint U301/Q510, `.kicad_dru` exemption at stage 3) · unconnected 383 (nothing routed) — identical to v2.2 |

## Lesson recorded

The first v2.3 build measured 6 mm² of heritage copper "missing" around the FC's top-right mounting slot and −0.4 % on the In1/In2 planes. Cause: the intermediate board copies had no `.kicad_pro` beside them, so pcbnew's zone filler used factory-default rules (0.5 mm copper-to-edge instead of the project's 0.2 mm). `build_floorplan.sh` now does every step inside a project directory; the brief's tools table carries the warning.
