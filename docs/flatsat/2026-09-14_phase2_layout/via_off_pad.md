> **Superseded 2026-10-21 (owner ruling F17):** "We're not tied to this layout, go ahead and attempt to reroute and
> free all of these via in pad items." The 7 POFV vias below were freed by the emulator re-place/reroute pass
> (`emulator_replace.md`). Via-in-pad is now **0 in-pad / 0 edge**; nothing is ordered filled-and-capped.

# F16 via-off-pad (dogbone) workstream, 2026-10-21

Input: `routed_r3/`. Output: installed as `FlatSat_V1/FlatSat_V1.kicad_pcb` and refilled.
Tool: `FlatSat_V1/tools/pcb/closure/dogbone.py` (repo). 

## Counts

| | in-pad | edge | distinct new vias |
|---|---|---|---|
| before (routed_r3) | 45 | 19 | 62 |
| after | 7 | 0 | 7 (all POFV) |

55 vias moved off-pad. 7 are ordered POFV (filled and capped).

## Method

`dogbone.py` per via: grid search of sites around the via, cheapest added copper first. A site is accepted only if
the via annulus is clear of every pad of any net by the pad gap. The via, the dogbone and every rewired track must
pass `fan2.py`'s exact KiCad-polygon clearance (per-pair rule, EMU_FANOUT relaxation only when both items are in the
area), hole, hole-to-hole and edge checks. `clusters.py` must show the net in no more pieces than before; pour nets
are judged on an in-memory refill, and the stored fills are restored before saving. A save guard refuses the board
if any existing item changed outside an accepted move.

| batch | settings | moved | gates after |
|---|---|---|---|
| 1 | r 2.5 mm, step 0.025, pad gap 0.10 | 47 | pass |
| 2 | r 3, step 0.05, `--area-via` | 1 (C220.1) | pass |
| 3 | dogbone narrowed to pad width | 1 (U511.15/16) | pass |
| (7) | push/shove, pad gap 0.05 | rejected | errors 190, unconnected 19: undo kept live `GetStart()` refs, so failed shoves were never reverted. Fixed (copies) and save guard added. Rolled back to checkpoint 3. |
| 4 | push/shove 60, pad gap 0.05, r 2 | 6 | pass |
| 5 | push/shove 250, r 2.5, 6000 sites | 0 | (no change) |

Pad gap. Vias are tented both sides and pad-to-mask clearance is 0. Batches 1 to 3 kept the via ring 0.10 mm off
every pad. The last 6 moves (batch 4) use 0.05 mm, which still leaves a tented mask web between the pad opening and
the via.

Via sizes. All moved vias keep their size, with 2 exceptions. C216.1 (1V1_EMU) and R205.1 (3V3_EMU) went from
0.46/0.20 to 0.40/0.20. Both new sites lie wholly inside EMU_FANOUT (x 266.5 to 280.0, y 88.0 to 101.5), where the
`emu_fanout_via` rule allows that size. No 0.40 via left the area. BenchPower/FCPower 0.80 vias were not on the list.

Foreign copper moved by `--push` in batch 4 (all new copper, none heritage). Each move was checked by the same exact
clearance and connectivity tests.

| for via | shoved |
|---|---|
| C206.1 | EMU_SWCLK B.Cu (2 segments) |
| C310.2 | F1_PWR F.Cu, EMU_BATT_SDA In2.Cu |
| R201.2 | 1V1_EMU In2.Cu, 3V3_EMU B.Cu |
| R205.1 | EMU_STATUS_LED F.Cu |
| U313.4 | F4_PWR F.Cu |

Total added copper over all nets is +36.0 mm. GND accounts for +7.1 mm and 3V3_EMU for +3.9 mm. Shoved signal nets
changed by EMU_SWCLK +0.50, F1_PWR +1.01, F4_PWR +0.26 and EMU_BATT_SDA +0.30 mm.

## QSPI length deltas (routed_r3 to final, track length per net)

| net | before mm | after mm | delta mm |
|---|---|---|---|
| EMU_QSPI_SCLK | 29.877 | 29.877 | +0.000 |
| EMU_QSPI_SD0 | 45.631 | 48.524 | +2.894 |
| EMU_QSPI_SD1 | 43.564 | 44.428 | +0.864 |
| EMU_QSPI_SD2 | 45.699 | 45.699 | +0.000 |
| EMU_QSPI_SD3 | 30.810 | 31.111 | +0.301 |
| EMU_QSPI_SS | 23.879 | 25.817 | +1.938 |

SD0 grows most because U201.5's via had to move 1.45 mm before it found a clear site (+2.89 mm). SS grows by the two
moves at U200.60 (+1.02) and R203.1 (+0.92). The SD0 to SCLK mismatch was 15.8 mm and is now 18.6 mm.

## POFV list (7)

Order these filled and capped (POFV) at JLC. For each via, the search tried every grid site at 0.05 mm pitch within
2.5 mm, with up to 250 nudges or shoves of a blocking new via or track. No site passed. The counts give how many
candidate sites each obstacle rejected in that last pass.

| ref.pad | net | via | position | what blocks every off-pad site |
|---|---|---|---|---|
| C209.1 | 3V3_EMU | 0.40/0.20 | (268.42, 99.405) | This is a U200 decoupling cap inside EMU_FANOUT, and all four layers are full around the pad. EMU_BATT_SCL runs diagonally on F.Cu along the pad's west edge (1125), and EMU_F2_SCL on F.Cu wraps its north side (680). GND tracks block 961 sites. EMU_TOP_SDA and EMU_F5_SENSE run under the pad on B.Cu (606), with EMU_F3_SDA/EMU_BATT_SDA nearby and the EMU_F5_SDA diagonal on In2. |
| C218.1 | 1V1_EMU | 0.46/0.20 | (278.32, 95.4) | This is the U200 core-supply decoupling cap. The EMU_GPIO_RSVD via and F.Cu track are 0.75 mm west (306). The EMU_GPIO_SPARE0 via is 0.6 mm north-east, with its F.Cu tracks to the south (494). VREG_AVDD_EMU (507) and GND (487) tracks close the remaining sides, EMU_F3_SENSE runs under the pad on B.Cu, and EMU_F2_SENSE is nearby (294). Nudging the SPARE0 via found no clear pair of sites. |
| C500.1 | Net-(U500-VDD) | 0.46/0.20 | (208.832, 151.672) | VBAT_BENCH_N BenchPower tracks (0.8 to 1.0 mm wide, 0.25 mm clearance) and pads C500.2 and C502.2 wrap the pad on F.Cu to the west, south and east (3076 + 432 + 310). A +3V3 In2 track runs 0.3 mm north of the pad centre. A site north of that track would leave the VDD In2 feed unable to reach it without crossing. INHIB_1 (FCPower, 711) and U500-VC (311) close the rest. |
| L200.1 | EMU_VREG_LX | 0.40/0.20 | (278.403, 90.408) | This is the RP2350 regulator switch node, a 0.7 x 1.7 mm pad. 3V3_EMU tracks block most sites (1877). EMU_GPIO_RSVD runs along the pad's west side and EMU_GPIO_SPARE0 along its east side, both on B.Cu. VREG_AVDD_EMU (453) and GND tracks and vias (442 + 289) are next to it, the EMU_GPIO_SPARE1 diagonal is on In2, and the L200.2 pad (1V1_EMU) blocks 226 sites. |
| R204.1 | EMU_QSPI_SS | 0.46/0.20 | (286.49, 90.75) | EMU_BOOTSEL_SW on F.Cu and EMU_RUN on B.Cu run parallel 0.7 mm west (1298). The EMU_QSPI_SD3 via sits just north (463). D200-A tracks and the R204.2 pad are east (709), and EMU_SWDIO (687) and 3V3_EMU (608) are south. |
| U201.3 | EMU_QSPI_SD2 | 0.46/0.20 | (283.074, 96.009) | This is the QSPI flash data pin. The EMU_GPIO_SPARE0 tracks and via block 1108 sites. The PYRO_INHIBIT_STATE B.Cu diagonal and its via block 763 + 454. The EMU_F2_SENSE In2 diagonal is 0.4 mm east (441), the U201.4 GND pad blocks 331, and EMU_UART_RX runs on B.Cu. |
| Y200.4 | GND | 0.40/0.20 | (274.994, 101.57) | This is a crystal ground pad. The 1V1_EMU In2 track runs diagonally across the pad's footprint (595), and EMU_UART_RX (443) and EMU_SWCLK run on B.Cu just south. The R201.1 and Y200.3 pads (C222 net) and their track close the west and north sides (213 + 206 + 193). |

## Every via (62)

| # | ref.pad | net | kind | old (mm) | disposition | new (mm) | via | added track mm |
|---|---|---|---|---|---|---|---|---|
| 1 | C200.1 | VBUS_EMU | IN-PAD | (294.762, 97.31) | MOVED | (294.188, 97.510) | 0.46/0.20 | +1.218 |
| 2 | C201.1 | VBUS_EMU | IN-PAD | (293.952, 90.364) | MOVED | (293.627, 90.239) | 0.46/0.20 | +0.696 |
| 3 | C202.1 | 3V3_EMU | IN-PAD | (291.57, 98.85) | MOVED | (291.270, 98.675) | 0.46/0.20 | +0.189 |
| 4 | C203.1 | 3V3_EMU | IN-PAD | (291.57, 96.05) | MOVED | (291.270, 96.200) | 0.46/0.20 | +0.168 |
| 5 | C204.1 | 3V3_EMU | EDGE | (268.16, 91.2) | MOVED | (268.410, 91.150) | 0.46/0.20 | +0.597 |
| 6 | C205.1 | 3V3_EMU | EDGE | (267.64, 96.055) | MOVED | (267.590, 95.905) | 0.40/0.20 | +0.210 |
| 7 | C206.1 | 3V3_EMU | EDGE | (270.57, 100.14) | MOVED | (270.520, 100.290) | 0.40/0.20 | +0.789 |
| 8 | C209.1 | 3V3_EMU | IN-PAD | (268.42, 99.405) | POFV | - | 0.40/0.20 | - |
| 9 | C213.2 | GND | EDGE | (276.712, 89.883) | MOVED | (277.087, 90.883) | 0.40/0.20 | +1.116 |
| 10 | C216.1 | 1V1_EMU | EDGE | (273.689, 99.699) | MOVED | (273.839, 99.199) | 0.40/0.20 | +1.225 |
| 11 | C218.1 | 1V1_EMU | IN-PAD | (278.32, 95.4) | POFV | - | 0.46/0.20 | - |
| 12 | C220.1 | 3V3_EMU | IN-PAD | (288.79, 91.48) | MOVED | (289.990, 90.230) | 0.46/0.20 | +1.733 |
| 13 | C221.2 | GND | IN-PAD | (270.127, 101.838) | MOVED | (270.303, 102.237) | 0.46/0.20 | +0.437 |
| 14 | C310.2 | GND | IN-PAD | (256.418, 106.438) | MOVED | (257.067, 106.537) | 0.46/0.20 | +0.658 |
| 15 | C500.1 | Net-(U500-VDD) | IN-PAD | (208.832, 151.672) | POFV | - | 0.46/0.20 | - |
| 16 | C513.1 | CHG_SYS | EDGE | (281.112, 155.1) | MOVED | (281.462, 154.950) | 0.46/0.20 | +0.255 |
| 17 | D200.2 | Net-(D200-A) | IN-PAD | (286.745, 99.405) | MOVED | (286.820, 99.030) | 0.46/0.20 | +0.765 |
| 18 | D201.2 | Net-(D201-A) | EDGE | (291.238, 107.0) | MOVED | (291.288, 106.875) | 0.46/0.20 | +0.405 |
| 19 | J702.1 | EMU_SWCLK | IN-PAD | (286.395, 62.605) | MOVED | (286.570, 62.980) | 0.46/0.20 | +0.225 |
| 20 | L200.1 | EMU_VREG_LX | IN-PAD | (278.403, 90.408) | POFV | - | 0.40/0.20 | - |
| 21 | Q500.3 | VBAT_BENCH_N | IN-PAD | (190.986, 155.846) | MOVED | (191.436, 155.846) | 0.46/0.20 | +0.900 |
| 22 | Q510.1 | VBUS_CHG | IN-PAD | (269.54, 155.675) | MOVED | (268.590, 155.675) | 0.46/0.20 | +0.664 |
| 23 | Q702.2 | GND | IN-PAD | (255.062, 74.62) | MOVED | (255.062, 73.970) | 0.46/0.20 | +0.650 |
| 24 | Q703.3 | WDT_DISABLE | IN-PAD | (247.042, 73.925) | MOVED | (247.042, 74.325) | 0.46/0.20 | +0.800 |
| 25 | R201.2 | EMU_XOUT | IN-PAD | (276.17, 100.968) | MOVED | (275.920, 100.868) | 0.40/0.20 | +0.539 |
| 26 | R203.1 | EMU_QSPI_SS | IN-PAD | (284.39, 90.75) | MOVED | (284.290, 90.050) | 0.46/0.20 | +0.916 |
| 27 | R204.1 | EMU_QSPI_SS | IN-PAD | (286.49, 90.75) | POFV | - | 0.46/0.20 | - |
| 28 | R205.1 | 3V3_EMU | IN-PAD | (279.19, 101.39) | MOVED | (278.940, 101.240) | 0.40/0.20 | +0.171 |
| 29 | R205.2 | EMU_RUN | IN-PAD | (280.2, 101.447) | MOVED | (280.550, 100.998) | 0.46/0.20 | -0.133 |
| 30 | R206.1 | EMU_STATUS_LED | IN-PAD | (284.795, 104.655) | MOVED | (284.520, 105.380) | 0.46/0.20 | +1.551 |
| 31 | R208.1 | EMU_GPIO_SPARE0 | IN-PAD | (284.545, 101.405) | MOVED | (284.470, 100.980) | 0.46/0.20 | +0.017 |
| 32 | R209.1 | EMU_GPIO_SPARE1 | IN-PAD | (286.637, 101.42) | MOVED | (286.538, 101.045) | 0.46/0.20 | +0.393 |
| 33 | R211.2 | Net-(D201-A) | EDGE | (292.938, 105.3) | MOVED | (293.062, 105.500) | 0.46/0.20 | +0.532 |
| 34 | R304.1 | F0_COIL_P | IN-PAD | (280.745, 121.355) | MOVED | (279.945, 122.155) | 0.46/0.20 | +2.263 |
| 35 | R314.2 | EMU_F1_SENSE | IN-PAD | (245.145, 107.005) | MOVED | (245.320, 106.705) | 0.46/0.20 | +0.026 |
| 36 | R322.2 | EMU_F2_SDA | IN-PAD | (248.695, 117.305) | MOVED | (249.120, 117.305) | 0.46/0.20 | +0.299 |
| 37 | R334.2 | EMU_F3_SENSE | IN-PAD | (257.945, 117.355) | MOVED | (258.370, 117.355) | 0.46/0.20 | +0.129 |
| 38 | R362.2 | EMU_BATT_SDA | IN-PAD | (227.195, 145.205) | MOVED | (227.545, 144.930) | 0.46/0.20 | +0.003 |
| 39 | R363.2 | EMU_BATT_SCL | IN-PAD | (226.876, 149.395) | MOVED | (226.726, 149.020) | 0.46/0.20 | +0.272 |
| 40 | R373.2 | EMU_TOP_SCL | IN-PAD | (248.695, 57.805) | MOVED | (249.120, 57.755) | 0.46/0.20 | +0.291 |
| 41 | R374.2 | EMU_FC3V3_SENSE | IN-PAD | (251.145, 57.955) | MOVED | (251.145, 58.355) | 0.46/0.20 | +0.076 |
| 42 | R515.1 | Net-(U511-ICHGSET) | IN-PAD | (277.5, 160.713) | MOVED | (277.500, 160.338) | 0.46/0.20 | +0.000 |
| 43 | R515.2 | GND | EDGE | (278.1, 159.425) | MOVED | (278.425, 159.450) | 0.46/0.20 | +0.726 |
| 44 | R517.2 | GND | EDGE | (275.614, 156.587) | MOVED | (275.489, 156.887) | 0.46/0.20 | +0.656 |
| 45 | R601.2 | PYRO_INHIBIT_STATE | IN-PAD | (163.545, 158.855) | MOVED | (163.870, 159.055) | 0.46/0.20 | +0.045 |
| 46 | R707.1 | EMU_CTL_USBBOOT | IN-PAD | (255.86, 77.27) | MOVED | (255.585, 77.470) | 0.46/0.20 | +0.034 |
| 47 | U200.60 | EMU_QSPI_SS | EDGE | (270.159, 91.252) | MOVED | (269.909, 91.202) | 0.46/0.20 | +1.022 |
| 48 | U201.2 | EMU_QSPI_SD1 | IN-PAD | (281.58, 94.272) | MOVED | (281.430, 93.948) | 0.46/0.20 | +0.864 |
| 49 | U201.3 | EMU_QSPI_SD2 | IN-PAD | (283.074, 96.009) | POFV | - | 0.46/0.20 | - |
| 50 | U201.5 | EMU_QSPI_SD0 | IN-PAD | (290.045, 96.715) | MOVED | (288.620, 96.465) | 0.46/0.20 | +2.894 |
| 51 | U201.7 | EMU_QSPI_SD3 | IN-PAD | (288.76, 94.272) | MOVED | (288.485, 94.073) | 0.46/0.20 | +0.301 |
| 52 | U202.1 | VBUS_EMU | EDGE | (294.762, 94.71) | MOVED | (294.762, 94.910) | 0.46/0.20 | +0.181 |
| 53 | U202.1 | VBUS_EMU | IN-PAD | (294.062, 94.41) | MOVED | (293.712, 94.385) | 0.46/0.20 | +0.354 |
| 54 | U202.2 | GND | IN-PAD | (295.373, 93.31) | MOVED | (295.723, 93.310) | 0.46/0.20 | +0.350 |
| 55 | U202.3 | VBUS_EMU | IN-PAD | (294.062, 92.21) | MOVED | (293.712, 92.210) | 0.46/0.20 | +0.322 |
| 56 | U300.6 | F0_SDA | EDGE | (248.38, 103.425) | MOVED | (248.505, 103.200) | 0.46/0.20 | +0.704 |
| 57 | U310.4 | GND | EDGE | (257.342, 104.362) | MOVED | (257.493, 104.362) | 0.46/0.20 | +0.518 |
| 58 | U313.4 | GND | IN-PAD | (248.98, 93.15) | MOVED | (249.480, 93.150) | 0.46/0.20 | +0.500 |
| 59 | U511.12 | Net-(U511-BTST) | EDGE | (278.4, 154.055) | MOVED | (278.725, 154.330) | 0.46/0.20 | +0.661 |
| 60 | U511.15, U511.16 | CHG_SYS | EDGE | (279.212, 152.15) | MOVED | (279.663, 152.200) | 0.46/0.20 | +1.009 |
| 61 | U511.19, U511.20 | GND | EDGE | (278.05, 149.898) | MOVED | (278.000, 149.523) | 0.46/0.20 | +1.464 |
| 62 | Y200.4 | GND | IN-PAD | (274.994, 101.57) | POFV | - | 0.40/0.20 | - |

Added track mm is the dogbone length plus the length change of re-pointed or bridged tracks. A negative value means
re-pointing shortened a track.

## Final gates (verbatim)

```
GATES heritage=0 heritage_refill=0 attachment(viol,warn,stubs)=0 0 37 | errors: 14  unconnected: 1  parity: 11 | via-in-pad: 7 in-pad, 0 edge, 7 distinct vias
```

Compared with routed_r3 on this machine, the DRC report shows no new item of any severity: errors, warnings and
unconnected match item for item (`drcdiff` of `g0/drc.json` vs `gfinal/drc.json` is empty).
