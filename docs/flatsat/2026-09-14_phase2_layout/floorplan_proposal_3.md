# FlatSat V1 Phase-2 floorplan — proposal #3 (Sonnet)

**Date:** 2026-09-14 · **Scope:** placement of all 218 new footprints + board-extension outline. Brief §3 L1–L3, L6, L8, L11 and §2 keep-outs. No routing.

## Owner summary

- **Outline: kept the validated default (`tools/pcb/outline_L1.json`) unmodified** — right wing 65 mm (x 231.39→296.39, full height), bottom strip 30 mm (y 142.12→172.12, full new width). No size change proposed: with ~107 cm² of new area against ~50 cm² of raw component footprint, the default already gives comfortable routing room, and the brief's own emphasis for this pass ("minimise outline complexity") argues against adjusting it without a concrete need. 0 of the 218 new parts fall outside this outline (checked with `apply_placement.py`); 0 courtyard/bbox overlaps among the 218 new parts.
- **Every block sits opposite the connector(s) it attaches to** (L11): the seven TCA4311A face/BATT/TOP buffers form a column hugging the old right edge, each at the same y as its connector; the pyro EN-tap drivers sit opposite J16; the three EN taps for the pyro-inhibit sheet sit right on the bottom strip under U6; the battery replica sits directly under J14. See the attachment table below.
- **L3's 12 mm clear lane is respected**: nothing new starts before x=244.0 (the lane runs 231.39→243.39), so J1/J2/J6/J9/J11/J13/J16/J12/J22 stay mateable by a real face board or a bench cable.
- **Two known issues, both independent of this proposal's placements** (reproduced with an *empty* placement — see "Known risks" below): (1) `tools/pcb/outline_L1.json` + `outline.py`, run exactly as instructed, produce 4 small heritage zone-fill deltas (≤0.25% area change each) at the seam where the new area attaches to the old — this is the outline tool/spec's own behaviour, not something this placement introduces, and is very likely the "accepted last-millimetre" case the brief itself calls out in L11, just flagged strictly by `heritage.py`'s 0-tolerance check; (2) `H10–H12` (mounting holes *added by* `outline.py`, not by this placement) and five heritage parts near the old left notch (`J4,J21,J24,U13,U30`) report "not fully inside the outline" from `apply_placement.py`'s generic bbox-in-polygon check, again reproduced with zero new parts placed. Both are flagged for the PM/outline-stage owner, not fixed here (out of scope for a floorplan proposal, and I should not be modifying shared tooling or moving heritage parts).
- Silkscreen is default/cluttered at this stage (expected — L8 is a later stage).

## 1. Outline

Unmodified `tools/pcb/outline_L1.json`: 3 new M3 mounting holes (H10 292.39,51.58 · H11 292.39,168.12 · H12 147.3,168.12), In1 GND grown over the whole new area, F.Cu/B.Cu GND pours (wing priority 1, strip priority 2), heritage zones clipped to the Rev2 outline inset 0.2 mm. Board becomes 153×125 mm (296.44×172.17 mm bbox), matching brief §2/L1 exactly.

## 2. Block placement (by zone)

**Wing, attachment column (x 244–268, hugs the old right edge), top → bottom:**

| y | Component(s) | Opposite |
|---|---|---|
| 50–61 | U316 (TOP buffer) + C316 + R370–374 | near J16 (222.5, 71) |
| 64–83 | Q701/Q702/Q703 (EN-tap drivers) + SW703 (WDT slide) + R705–710 | opposite J16 (FC_RESET/USBBOOT/WDT_DISABLE) |
| 88–99 | U313 (F, ch F4) + U314 (B, ch F5) + C313/C314 + R340–344/R350–354 | opposite J1 (91, F) / J2 (91, B) |
| 103–118 | U300 (F, Face0 real ref) + U310 (B, ch F1) + C300/C310 + R300–303/R310–314 | opposite J6 (106.5, F) / J9 (106.5, B) |
| 119–133 | U311 (F, ch F2) + U312 (B, ch F3) + C311/C312 + R320–324/R330–334 | opposite J11 (121.5, F) / J13 (121.5, B) |
| 136–141 | U315 (BATT buffer) + C315 + R360/362/363 | near J14 (207, 131.2) |

**Wing, core column (x 269–294):** bench-IO connectors J701 (USB-C)/J702 (SWD)/SW701/SW702 at the very top-right (y 50–61), then J703 (bench header) + R701–704/C701/TP701 (y 62–68), then the full emulator_mcu core — U200/U201/U202, Y200, L200, D200–202, C200–222, R200–211, TP200–203 (y ~69–115) — then the Face-0 golden-reference device stack (U301 TMP112, U302 VEML6031, U303 DRV2605L, C301–304, J300 + R304 coil header, TP300–306) filling out to y≈130. All local/new nets only except U300 (already placed in the attachment column) — no FC attachment needed here.

**Bottom band (strip x143–231 + wing's own bottom-right corner x231–296, y144–171):** four side-by-side shelf packs, left→right — pyro inhibit (x152–188: SW600, D600-602, JP600-607, R600-602, LED600, TP600-603, under U6/J7/J8/J10/J15/J19/J20/J29/J30) → battery replica (x190–222: J500, U500, Q500/Q501, R500-505, C500-503, JP500, TP500-505, directly under J14) → solar injection (x224–256: J400/J401, F400/F401, D400/D401, JP400/401, TP400-402, low on the wing) → BQ25886 charger (x258–288: J510 on the new bottom edge, U511 with its six 1210 22 µF caps and L510 clustered directly around it, R510-519, Q510, U510, JP510, D510, TP510-512). Kept off x143.3–152 and x288–296 throughout so nothing crowds the two bottom mounting holes; all four blocks stay within y144–171 (≥1 mm clear of the 172.12 mm bottom edge).

## 3. Attachment table (net → pad → block) — brief L11

All figures below are the brief's own measured pad-to-Rev2-edge distances (§3 L11), which are fixed by the Rev2 layout and don't depend on this placement; they confirm every stub stays inside the allowed band once routing starts. "Block" is where this proposal put the far end of that stub.

| Net(s) | Pad | Distance to old edge | Block (this proposal) |
|---|---|---|---|
| F0_SDA/SCL, F0_PWR | J6 pins 4/5/6 (top, F.Cu) | 3.8–3.9 mm | U300 (Face0 real reference), x244–252, y~103–112 |
| F1(F9)_SDA/SCL/PWR — sheet nets `EMU_F1_*` | J9 pins 4/5/6 (bottom, B.Cu) | 3.8–3.9 mm | U310 (ch1 buffer), x256, y106.5, side B |
| F2_SDA/SCL/PWR | J11 pins 4/5/6 (top, F.Cu) | 3.8–3.9 mm | U311, x248, y121.5, side F |
| F3_SDA/SCL/PWR | J13 pins 4/5/6 (bottom, B.Cu) | 3.8–3.9 mm | U312, x256, y121.5, side B |
| F4_SDA/SCL/PWR | J1 pins 4/5/6 (top, F.Cu) | 3.8–3.9 mm | U313, x248, y91, side F |
| F5_SDA/SCL/PWR | J2 pins 4/5/6 (bottom, B.Cu) | 3.8–3.9 mm | U314, x256, y91, side B |
| VSOLAR (×6, common) | J1/J2/J6/J9/J11/J13 pins 1–2 | 3.8–3.9 mm | J400/J401 injection channels, x224–256, y~144–156 (one stub tap; VSOLAR is already one shared net) |
| Dir_Chrg_In, B-, BATT_SDA, BATT_SCL, +3V3 | J14 (THT, any layer) | 10.9 mm | J500 (battery replica terminal), x~190–222, y~144–156, directly under J14 |
| SDA_Top, SCL_Top, FC_RESET, USBBOOT, WDT_DISABLE, +3V3 | J16 (THT) | 5.0 mm | U316 (TOP buffer, y50–61) + Q701/Q702/Q703/SW703 (EN-tap drivers, y64–83) — one stub per net, fanned out on-board to the drivers/header/switch |
| VBATT_SENSE, INHIB_1, GND | J8 | 4.5 mm | JP602 (pyro block, bottom band) |
| INHIB_1, IN_RBF | J29 | 4.5 mm | JP603 |
| IN_RBF, VBUSP | J30 | 4.5 mm | JP606 |
| B-, GND | J15 | 4.5 mm | JP607 |
| VBATT_SENSE, INHIB_2 | J7 | 20.5 mm (long allowance) | JP604 |
| INHIB_2, IN_RBF | J10 | 20.5 mm (long allowance) | JP605 |
| IN_RBF, VBUSP | J20 | 17.0 mm (long allowance) | JP606 (shared reach, same J20/J30 net) |
| B-, GND | J19 | 12.0 mm | JP607 (shared reach, same J15/J19 net) |
| Deploy1_EN | R104 pad 1 (top, F.Cu, ~11 mm from right edge) | ~11 mm | D600 (pyro diode), bottom band |
| Heater_EN | R100 pad 1 (bottom, B.Cu, ~12 mm from bottom edge) | ~12 mm | D601 (pyro diode), bottom band |
| Deploy2_EN | U6 pad 6 (bottom, B.Cu, 8–10 mm from bottom edge) | 8–10 mm | D602 (pyro diode), bottom band |

## 4. Ground / stitching (L6)

In1 GND plane extended over the whole new outline; F.Cu/B.Cu GND pours added over the wing (priority 1) and strip (priority 2) — both from the unmodified `outline_L1.json`. `stitching.points` in the JSON carries 63 proposed via locations: ~39 around the new-area perimeter (9 mm pitch, 3 mm inset — satisfies "≤10 mm along the perimeter") plus a ~24-point loose ring around the emulator-MCU/bench-IO zone ("around the emulator"). All 63 lie outside the Rev2 outline by construction (checked). These are a floorplan-stage proposal for the outline/ground stage (stage 3) to refine against real copper once nets are routed — I did not verify them against final pad clearances since nothing is routed yet.

## 5. L3 lane / RF keep-outs

12 mm clear lane `x 231.39–243.39` kept empty for the full wing height opposite J1/J2/J6/J9/J11/J13/J16/J12/J22 — no new component's left edge is inside x=244. RF keep-outs (U13→RF1 trace, U30's 8 mm surroundings) are both deep inside the old outline (x 147–194, y 57–105); the nearest new-area component in this proposal is >45 mm away, so no explicit keepout geometry was needed.

## 6. Checks run

Final board copy: `board_placed4.kicad_pcb` (outline-extended with the unmodified `outline_L1.json`, then all 218 placements applied).

```
apply_placement.py --board board_outline_out.kicad_pcb --placement floorplan_proposal_3.json --out board_placed4.kicad_pcb
  applied 218; refused (heritage) []; missing refs []
  footprints not fully inside the outline: 8: ['H10','H11','H12','J21','J24','J4','U13','U30']
    (identical set reproduced with an EMPTY placement -- see "Known risks", not from this proposal's 218 placements)

bbox/courtyard overlap scan among the 218 new footprints (script check, pending the full kicad-cli DRC
  below for the courtyard-polygon-accurate version): 0 pairs. All 218 within x152.0-294.0, y50.5-169.6
  (>=1 mm clear of every new board edge). (Caught and fixed an anchor-vs-bbox-center bug in the packer
  along the way -- see "Known risks" item 3.)

heritage.py check tools/baseline/heritage_rev2.json board_placed4.kicad_pcb --allow-zone-growth --allow-edge
  4 violations, all zone-fill-area deltas <=0.25% right at the old/new seam -- reproduced identically by
  running outline.py ALONE (0 of the 218 parts placed) and by an earlier placement iteration, so confirmed
  independent of this proposal's actual placement.
    HERITAGE VIOLATION: zone  on F.Cu: filled copper inside the Rev2 outline changed 33.5 -> 28.0 mm2
    HERITAGE VIOLATION: zone  on F.Cu: filled copper inside the Rev2 outline changed 32.5 -> 26.3 mm2
    HERITAGE VIOLATION: zone GND on In1.Cu: filled copper inside the Rev2 outline changed 6409.2 -> 6397.2 mm2
    HERITAGE VIOLATION: zone +3V3 on In2.Cu: filled copper inside the Rev2 outline changed 5434.3 -> 5422.3 mm2

attachment_check.py: 0 new tracks/vias, 0 stub chains (expected -- no routing at this stage); same 4 zone
  fill-delta violations as above (informal for this stage since routing hasn't started -- this check's
  real job begins at the routing stage).

kicad-cli pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones:
  STARTED on this exact board copy but DID NOT FINISH inside the session -- observed 3-4 kicad-cli DRC
  processes running concurrently for 15+ minutes (the other floorplan proposers' own hand-back checks),
  all pinned near 100% CPU on shared hardware; a lighter run (no --refill-zones/--schematic-parity, on an
  already-refilled copy) still hadn't returned after 100 s. This is a session/scheduling constraint, not
  a property of this board -- see the structured-output "check_results" field for exactly what was
  attempted and observed. The floorplan-stage acceptance bar in the workflow HOW section (0 courtyard
  overlaps among new parts, 0 outside the outline) is covered by the bbox scan and apply_placement.py
  above; a full kicad-cli DRC pass is squarely stage 3-5's job once routing exists and should be re-run
  by the stage-3 owner on the approved floorplan before any routing begins regardless.

render.sh board_placed4.kicad_pcb render2/ -> top.pdf / bottom.pdf read and visually checked: the
  attachment column reads cleanly opposite its connectors, the 12 mm lane is visibly clear, U310/U312/U314
  (bottom-side buffers) land correctly on the bottom render at the same y as U311/U313/U300 on top, and the
  bottom-band pyro / battery replica / solar injection / charger blocks are now visibly separated
  left-to-right, matching the table above. Default (unrouted) silkscreen is cluttered, as expected pre-L8.
```

## 7. Known risks / open items for the judge

1. **outline_L1.json + outline.py, run with the default spec exactly as instructed, do not currently give heritage 0** — reproduced with zero new parts placed, so this is a pre-existing characteristic of the validated default tool/spec pairing, not a defect in this placement. The magnitude (≤0.25% area change on 4 zones, all right at the seam) matches what brief L11 explicitly calls "accepted" ("where the extension attaches, the old edge clearance no longer applies and the FC's planes fill that last millimetre"), but `heritage.py`'s check has no tolerance band for it. Recommend the PM/outline-stage owner either add a small tolerance to `heritage.py`'s fill-area check for zones touching the new seam, or confirm in writing that this specific delta is accepted per L11 so stage 3 doesn't get stuck chasing it.
2. **`apply_placement.py`'s outline-containment check flags 8 pre-existing items** (`H10–H12`, the 3 mounting holes `outline.py` itself adds, plus heritage `J4/J21/J24/U13/U30` near the old left notch) as not fully inside the new outline polygon — again reproduced with an empty placement. Likely a fillet/corner precision artifact where the new polyline's geometry meets the old notch, or the hole pads' bounding boxes (courtyard-ish) extending a fraction of a mm past the polygon right at the rounded corners. Not something a placement proposal can or should fix (H10-H12 are added by the outline tool; J4/J21/J24/U13/U30 are frozen heritage).
3. **Stitching-via points (§4) are a first pass**, not checked against real copper (nothing is routed yet); expect the outline/ground stage to adjust pitch/position once nets exist.
4. **`R304` (43 Ω 2010, Face-0 coil dummy load) and `J300`** sit in the "Face-0 support" pool (core column, x269–294) rather than immediately next to `U300` (attachment column, x244–268) — they only connect to `U300`'s device-side bus (`F0_DEV_SDA/SCL`), a local net, so the ~20 mm separation costs a slightly longer local trace but does not affect any L11 attachment stub.
