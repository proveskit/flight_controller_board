# FlatSat V1 pre-order review: fix pass for items 1, 2, 3, 4, 6, 7

Workspace: `fix/FlatSat_V1/` (copy of the repo `FlatSat_V1/` without `jlcpcb/`). Repo writes: only `FlatSat_V1/tools/pcb/gates.sh` (track_width count).
Every edit was made by a script in `fix/` through `ed.py` (fan2 exact-polygon clearance, hole, edge and SMD-pad checks per new track/via; heritage uuids refused). Each item ends in `refill.py` + repo `gates.sh` + ERC + a checkpoint in `fix/ckpt/<item>/` (see `PROGRESS.md`).

## Result

| | baseline (installed) | final |
|---|---|---|
| GATES | heritage=7 heritage_refill=0 attachment 0/7/37, errors 14, unconnected 1, parity 11, via-in-pad 7/0 | identical, plus `track_width: 95` |
| ERC errors | 12 (6 power_pin_not_driven, 5 pin_not_connected, 1 pin_to_pin) | 12, same set; ERC warnings 693 -> 693 |
| DRC items new vs baseline (non track_width) | - | 1 warning: `footprint_type_mismatch U511` (SMD footprint with PTH EP pads; flown U18 and U10 carry the same warning) |
| courtyard overlaps | SW2/TP2 | SW2/TP2 only |

Final GATES line (repo `gates.sh`):

```
GATES heritage=7 heritage_refill=0 attachment(viol,warn,stubs)=0 7 37 | errors: 14  unconnected: 1  parity: 11 | via-in-pad: 7 in-pad, 0 edge, 7 distinct vias | track_width: 95
```

Resistances below come from `res.py`: nodal solve over the net's tracks, vias and pads (zones ignored), 1 oz outer / 0.5 oz inner (JLC04161H-7628), 20 um via plating, FET/connector pads lumped as one terminal.

## Item 7: VSOLAR hard maximum 18 V

| what | before | after |
|---|---|---|
| `solar_power_injection.kicad_sch` note | HARD MAXIMUM 24 V, "9 V of margin" | HARD MAXIMUM 18 V, reason "heritage C40 (LT3652 VIN bypass on V_SOLAR_SENSE) is a 10 V X5R"; 33 V Vmax line reads "15 V over the 18 V hard maximum"; two new lines: OVP <= 18 V verified with J400/J401 disconnected before each session, no soak at 18 V; INA219 26 V / PTC 33 V kept as secondary limits |
| F.SilkS | none | `18V MAX` 1.0 mm / 0.15 mm under J400 (233.0,171.2) and J401 (245.5,171.2); clear of pads, the terminal outline and the pin-1 marks |

GATES: `heritage=7 heritage_refill=0 attachment 0 7 37 | errors: 14 unconnected: 1 parity: 11 | via-in-pad 7/0`. ERC 12.
Not done here (outside the board): filing C40's 10 V rating as an FC_V5e finding, bench-procedure text.

## Item 1: Mode 2 feeds the FC from SYS

| what | before | after |
|---|---|---|
| schematic JP510.1 | CHG_BAT (wire from the C515/TP512 node) | CHG_SYS (wire cut at the TP512 node, stub + local label `CHG_SYS`); CHG_BAT = U511.13/14, C515, TP512 only |
| sheet notes / fields | "JP510 BQ25886 BAT -> Dir_Chrg_In"; STAT-blink note | "JP510 BQ25886 SYS -> Dir_Chrg_In ... Never fit JP510 with a PSU on J500."; Mode 2 line adds "The FC runs from U511 SYS (instant-on, >= 6.2 V), not BAT."; STAT note says BAT carries no load. JP510/TP512 Description fields updated on sheet and board (parity stays 11) |
| board | JP510.1 on CHG_BAT through In2 1.5 mm + 0.5 mm neck to a 0.46/0.20 via, then the 0.25 mm In1 run | pad net reassigned by script; the In2 1.5 mm run now CHG_SYS, fed from SYS by two 0.8/0.4 vias at TP511 and (item 4) an In2 1.5 mm run from paired 0.8/0.4 vias at C513 |
| R(charger pins -> JP510.1) | 78.4 mOhm (BAT pins) | 24.4 mOhm (SYS pins) |

GATES after item 1: `errors: 24` (the 10 extra are item 6's BenchPower 0.25 mm clearance on newly classed nets, cleared in item 6), parity 11, rest baseline. ERC 12.

## Item 4: BQ25886 power stage (same pass as item 1)

| check | before | after |
|---|---|---|
| CSYS (C513) | (282.32,156.55) rot 0; SYS reached through 0.25 mm F.Cu, a 0.46/0.20 via, ~5.7 mm In2 and a second via | (281.75,153.675) rot 270; pad 1 1.0 mm from the SYS pins over a 0.7 mm F.Cu neck, no via |
| GND via at each charger cap GND pad (edge gap) | C510 3.98, C511 3.29, C513 4.88, C514 3.25, C515 4.56, C517 3.77, C518 3.39 mm | 0.62, 0.42, 0.40, 0.32, 0.32, 0.32, 0.31 mm (0.46/0.20 vias with stubs; C513 has two) |
| EP thermal vias | 0 | 9 PTH pads in U511, number 25, 0.6/0.3 mm, 1.0 mm pitch 3x3, solid zone connection (U18 convention); PGND pins 19/20 bridged to the EP on F.Cu |
| SW | 0.25 mm, ~2.1 mm + 3.6 mm to L510 | 0.8 mm F.Cu 4.4 mm to L510.1; C512 on the run |
| PMID | 0.25 mm F.Cu + 7.15 mm In2 + 2 vias | 1.0 mm F.Cu to L510.2, no vias; pin riser 0.6 mm |
| CHG_BAT In1 run under U511 | 0.25 mm, 14.4 mm | deleted; BAT goes 0.4 mm F.Cu pins -> C515.1 -> TP512 (no load after item 1) |
| part moves | - | L510 (284.13,147.7) rot 0 -> (284.85,147.3) rot 90 (pad 2 PMID toward C511); C512 -> (280.5,149.3) rot 90; TP512 -> (279.9,167.6); 0 new courtyard overlaps |
| SYS bus to C514/C517/C518 | partly 0.25/0.6 mm | 1.0 mm F.Cu spine |

Not met as written, with reason:
- "0.1-1 uF 25 V 0402 directly across SYS 15/16 and PGND 19/20": skipped. The SW pins 17/18 sit between the SYS and PGND pins, so no F.Cu placement spans them; a new part also needs a BOM line in `jlcpcb/project.db`, which this pass may not write. Options: (a) accept C513 at the pins with the via-stitched return (recommended for this rev); (b) add an 0402 across C513's pads next rev with a supply-chain pick.
- "CSYS loop pins-to-cap-to-pins under 5 mm on F.Cu": the cap side is 1.0 mm on F.Cu; the GND side returns C513.2 -> two vias -> In1 (0.21 mm below F.Cu) -> 9 EP pads / the PGND via. No F.Cu path from C513.2 to PGND exists without crossing SW.

GATES after item 4: `errors: 21`, parity 11, via-in-pad 7/0, rest baseline. New warning `footprint_type_mismatch U511`. ERC 12.

## Item 3: R5460 sense loop

The fix keeps Q501 in place. Rotating it puts its gate pin behind the V-/DOUT fence at U500, and every layer between Q501 and U500 carries a crossing run (In2 VC/PYRO, B.Cu 3V3_EMU). Instead:

| sense-loop copper | before | after | how |
|---|---|---|---|
| PROT_DRAIN Q500 D -> Q501 D | 33.9 mOhm | 2.7 mOhm | 0.25 mm In1 neck + two 0.46/0.20 vias replaced by 1.2 mm F.Cu bars on both drain rows, two 0.8/0.4 vias per side, In1 1.5 + 2.0 mm |
| VBAT_BENCH_N J500.3 -> Q500 S, as seen by VSS (U500.6) | 28.6 mOhm | 0.0 mOhm | VSS Kelvin: the U500/C500-C502/R504 cluster no longer taps J500.3; a 1.0 mm B.Cu sense run joins it at Q500 source pad 2 (`kelvin.py`: cutting that stub splits the net into heavy and sense clusters) |
| B- R502 tap -> Q501 S | 5.2 mOhm | 5.2 mOhm | unchanged: R502.2 is boxed by V- copper and the VC In2 run blocks a second B- via |
| total | 67.6 mOhm | 7.8 mOhm | |
| implied excess-discharge trip, VDET3 0.200 V, FETs 2 x 9 mOhm | 2.3 A (2.0-2.5) | 7.7 A (6.6-9.0 A over VDET3 0.185-0.215 V, FETs 16-20 mOhm) | |

Also: COUT_GATE re-run (via moved to (201.4,158.476), F.Cu run off Q501 pad 5, clearing the 0.21 mm pad-5 gap); heavy J500.3 -> Q500 path 28.6 -> 24.8 mOhm with partner 0.8/0.4 vias at 2 of its 3 layer changes. Its 0.3 mm F.Cu neck (191.5-194.2, 158.7-160) stays: the C503.2/B- via leaves no room, and the run is now outside the sense loop. Sheet note now reads "... + 8 mOhm sense-loop copper (about 7.7 A at 2 x 9 mOhm)" and VBAT_BENCH_N note names the Kelvin tap.

GATES after item 3: `errors: 20`, parity 11, via-in-pad 7/0 (a first placement left one EDGE via on Q501.5, moved 0.1 mm; `ed.via` now refuses any via touching an SMD pad). ERC 12.

## Item 2: bench current enters at J14

| | before | after |
|---|---|---|
| attachment | J16.8 F.Cu stub + 140 mm run with five 0.46/0.20 vias, then heritage 0.4 mm In2 x=226.6 | L11 stub on In1, 1.5 mm, J14.1 -> Rev2 edge, 10.9 mm inside, no via in the band; J16.8 run removed (23 items), J16.8 keeps its heritage copper and nothing disconnects |
| R(J500.1 -> J14.1), Mode 1 | 307 mOhm | 34.7 mOhm |
| R(JP510.2 -> J14.1), Mode 2 | 271 mOhm | 62.3 mOhm |
| attachment_check | 0 / 7 / 37 | 0 / 7 / 37 (`stub net Dir_Chrg_In: 1 seg, 10.9 mm inside, pads J14.1, In1.Cu`) |

Why In1 and only J14.1: F.Cu (heritage VBATT_SENSE diagonal), In2 (heritage VBUSP) and B.Cu (heritage Dir_Chrg_In, PAYLOAD_BATT, DEPLOY1) wall J14.1 off to the south; J14 pins 1-9 are not via-allowed. In1 holds only the heritage GND pour there (in-band fill change 6401.6 -> 6384.2 mm^2 is an F15 warning; the 12 mm core is identical, heritage_refill 0). J14.3 sits 12.9 mm deep, so a stub there would carve the frozen core; the odd pins are already joined by the heritage Dir_Chrg_In B.Cu/In2 pours. Bench side: In1 1.8/1.1 mm to the trunk via (217.581,152.526) and 0.8 mm (JP500.1 clearance limit) to JP500.2. The sense-only VSS In1 diagonal that blocked the corridor moved to B.Cu.
Not met: the trunk layer changes this stub joins, (217.581,152.526) and (203.856,159.744), remain single 0.8/0.4 vias (existing copper): partner sites are blocked by R500/R503 pads, the VBAT In2 cluster and the COUT_GATE run. The stub itself adds no via.

GATES after item 2: `errors: 20`, attachment 0/7/37, heritage_refill 0, parity 11, via-in-pad 7/0. ERC 12.

## Item 6: width rule, net names, netclasses

- `.kicad_dru`: rule `bench_power_width`, `(severity warning)`, `track_width min 1.0mm` for BenchPower, BenchPower5V and FCPower outside rule area `FC_COPY` (new zone, no keepouts, polygon = Rev2 outline from the heritage snapshot). Warning keeps the error baseline; `gates.sh` prints the count.
- Proof on the as-built board (`widths_asbuilt.txt`, 136 items): flags Net-(Q500-D-Pad5) incl. the In1 0.25 mm neck, CHG_BAT In1 10.4 mm, VBAT_BENCH_N 0.3 mm.
- Schematic local labels: PROT_DRAIN (Q500/Q501 drains), CHG_PMID, CHG_SW (battery sheet); INJ_A_PTC, INJ_A_OR, INJ_B_PTC, INJ_B_OR (D400/D401 anode/cathode). Board nets renamed by script to the same hierarchical names (parity 11).
- `.kicad_pro`: those seven in BenchPower; CHG_DVIN in a new class BenchPower5V (0.2 mm clearance, 1.0 mm track, 0.8/0.4 via). Reason: putting the 5 V USB node in BenchPower (0.25 mm) raised five clearance errors in the U510/Q510 ideal-diode cluster; 0.2 mm is the board default and enough for 5 V.
- One geometric fix the class change needed: VSOLAR run past JP400.1 (INJ_A_OR) re-routed.
- 30 residual segments widened in place where the exact check allowed (INJ_A/B runs incl. In2, B-, PROT_DRAIN stubs, VBAT, VBUS_CHG, part of CHG_DVIN).
- `gates.sh` (repo): GATES line ends `| track_width: N`.

Remaining 95 track_width items (`residual_widths.txt`), all outside FC_COPY:

| group | items | why it stays |
|---|---|---|
| deferred by item 6: CHG_DVIN (incl. 0.187 mm neck), VBUS_CHG (0.25-0.5 mm from J510), INJ_A_OR In2 0.25 mm 3.7 mm, INHIB_2 J10.3 stub tail 0.5 mm, IN_RBF 0.5 mm x 5.5 mm, B- 0.9 mm links at Q501/R505 | 31 (15 + 8 + 1 + 1 + 2 + 4) | next rev per the item; bench procedure: injection PSU limit <= 1.5 A |
| U511 pin necks (0.25 mm joiners, SYS 0.7 mm neck, SW 0.8 mm, PMID 0.6 mm riser) | 9 (CHG_SYS 2, CHG_SW 3, CHG_PMID 3, CHG_BAT 1) | 0.5 mm pin pitch |
| CHG_BAT 0.4 mm to C515/TP512 | 6 | no load after item 1 |
| VBAT_BENCH_N sense cluster and Kelvin stub (0.4-0.8 mm), heavy-path 0.3 mm neck (2) | 13 | sense lines carry uA/mA; the neck is outside the sense loop now |
| PROT_DRAIN 0.8 mm via stub | 1 | Q501.5 / COUT clearance |
| Dir_Chrg_In 0.9 mm R500 link, 0.8 mm In1 to JP500.2 | 2 | R500 pad / JP500.1 clearance; parallel to the 1.1-1.8 mm trunk |
| MID_BENCH (4.2 mA divider), VBUS_EMU (emulator USB) | 10 + 23 | signal-current nets in BenchPower by pattern; next rev: move to a sense class or widen |

Doc corrections for the parent (repo files I may not write):
- `layout_report.md` line 116: replace "visible in DRC — no width below class was flagged" with "KiCad 10 uses the netclass track width only as a routing default, so DRC never checked it; since the 2026-10-21 review the `bench_power_width` rule in `FlatSat_V1.kicad_dru` does (warning, counted as track_width by gates.sh)".
- `route_report.md` §7: the sentence "Every FCPower and BenchPower net carries 1.0–1.5 mm on its new copper. The sub-1.0 mm entries are all L11 stub segments inside the attachment band" is false for VBAT_BENCH_N, CHG_BAT, CHG_SYS, VBUS_CHG, Q500 drain; point it at review item 6 and `track_width` in gates.

GATES after item 6: `errors: 14`, parity 11, attachment 0/7/37, heritage_refill 0, via-in-pad 7/0, track_width 95. ERC 12.

## For the order

- Moved/rotated footprints C513 (rot 270), L510 (rot 90), C512, TP512: check them in the JLC placement viewer (CLAUDE.md rule 5).
- U511 now has 9 PTH pads: drill file gains 9 x 0.3 mm holes; footprint type stays SMD so the CPL keeps U511.

## Tools (fix/)

`ed.py` (edit API with exact checks), `item{1,1b,1c,2,3,3b,4,4b,6,6b,7}.py` (the edits, in order), `rulearea.py`, `netclass_add.py`, `schtext.py`, `sch_item1.py`, `sch_labels.py`, `schpins.py`, `res.py` (nodal resistance), `kelvin.py`, `metrics4.py`, `widths.py`, `widthlist.py`, `plot.py`, `region.py`, `nets.py`, `gate.sh`, `erc.sh`.
