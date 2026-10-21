# Emulator re-place / reroute: last 7 POFV vias off-pad (2026-10-21)

Input: repo `FlatSat_V1/` at `935e32b`, refilled (`work/ckpt0.kicad_pcb`). Output: `FlatSat_V1.kicad_pcb` in this
directory, refilled. `.kicad_pro` and `.kicad_dru` are unchanged (byte-identical to HEAD). The EMU_FANOUT rule area
did not move, because U200 did not move.

## Result

| | baseline (HEAD, refilled) | final |
|---|---|---|
| via-in-pad (in-pad / edge) | 7 / 0 | **0 / 0** |
| POFV vias to order | 7 | **0** |
| DRC errors / unconnected / parity | 14 / 1 / 11 | 14 / 1 / 11 |
| track_width | 95 | 95 |
| DRC items not in the baseline set (type + descriptions, track_width ignored) | - | **0** (`scripts/drcdiff.py work/g0/drc.json work/gfinal/drc.json`) |
| courtyard overlaps | SW2/TP2 | SW2/TP2 only |
| heritage (stored) / heritage_refill | 7 / 0 | 7 / 0 |
| attachment viol / warn / stubs | 0 / 7 / 37 | 0 / 7 / 37 |

Final GATES line (repo `gates.sh` on `emu/FlatSat_V1.kicad_pcb`):

```
GATES heritage=7 heritage_refill=0 attachment(viol,warn,stubs)=0 7 37 | errors: 14  unconnected: 1  parity: 11 | via-in-pad: 0 in-pad, 0 edge, 0 distinct vias | track_width: 95
```

The final board is a clean replay of batches b1 to b6 from the baseline with the final tool (`scripts/replay.sh`),
and each batch was gated on its own (`PROGRESS.md`).

## Per-via outcome

| # | via | net | outcome | new site (mm) | how | what was ripped and rerouted |
|---|---|---|---|---|---|---|
| b1 | Y200.4 | GND | via removed | Y200.2 via at (271.850, 104.375) 0.46 | 0.25 mm F.Cu GND link Y200.4 to Y200.2 under the crystal body (between XIN and XOUT, a guard); Y200.2 stitched off-pad | none |
| b2 | C209.1 | 3V3_EMU | MOVED | (268.020, 99.330) 0.40 | dogbone | EMU_F2_SCL, EMU_F5_SENSE in [267.2,98.6,269.0,100.4] |
| b3 | R204.1 | EMU_QSPI_SS | via removed | none | SS In2 jumper and both of its vias deleted; SS rerouted R203.1 to R204.1 on F.Cu (0 vias) | EMU_BOOTSEL_SW, EMU_RUN, EMU_GPIO_RSVD, EMU_UART_RX in [284.5,89.0,288.5,92.5] |
| b4 | U201.3 | EMU_QSPI_SD2 | MOVED | (283.374, 96.284) 0.46 | dogbone, 0.38 mm shift | PYRO_INHIBIT_STATE, EMU_UART_RX, EMU_F2_SENSE, EMU_GPIO_SPARE0 in [282.3,94.6,284.4,97.3] |
| b5 | L200.1 | EMU_VREG_LX | MOVED | (278.028, 90.408) 0.40 | dogbone (0 added mm, In2 LX end re-pointed) | EMU_GPIO_RSVD/SPARE0/SPARE1, EMU_F2/F3_SENSE in [277.4,89.0,279.6,92.0] |
| b5 | C218.1 | 1V1_EMU | via removed | none | C218 re-placed; 1V1 now COUT to C218 to pin 39 on F.Cu | VREG cell window, see below |
| b6 | C500.1 | Net-(U500-VDD) | via removed and replaced | (212.412, 150.188) 0.46 | C500.1 runs 0.25 mm F.Cu north-east above C500.2 to the new via, which joins the existing VDD In2 run | only the VDD in-pad via and its 1.5 mm In2 stub |

Every new via is 0.10 mm or more off every SMD pad (tented mask dam). The 0.40/0.20 vias all intersect EMU_FANOUT.
24 vias were added and 24 removed in total (list: `work/` replay logs).

## What moved

Only two parts moved, both in the emulator block and on F.Cu: C218 (1V1 100 nF) from (278.8, 95.42) r0 to
(278.8, 93.91) r0, and C215 (VREG_AVDD 4.7 uF CFILT) from (278.8, 93.91) r0 to (278.8, 95.42) r180. They swapped
slots, so the 1V1 network runs L200 to C217 (COUT) to C218 to pin 39 on F.Cu with no via. U200, U201, Y200, L200
and all other parts kept their positions. No heritage footprint, track, via or zone changed (heritage_refill 0,
heritage geometry guard in the tool).

Rerouted nets (track length / vias, baseline to final):

| net | before mm | after mm | vias |
|---|---|---|---|
| 1V1_EMU | 48.38 | 43.93 | 7 to 5 |
| VREG_AVDD_EMU | 14.46 | 9.47 | 4 to 2 |
| EMU_QSPI_SS | 25.82 | 25.72 | 6 to 4 |
| EMU_QSPI_SD2 | 45.70 | 45.85 | 8 to 8 |
| Net-(U500-VDD) | 12.99 | 14.91 | 3 to 3 |
| GND (new copper) | 315.25 | 313.90 | 277 to 280 |
| EMU_UART_RX | 41.04 | 46.24 | 2 to 4 |
| EMU_GPIO_RSVD | 56.00 | 60.69 | 12 to 13 |
| EMU_GPIO_SPARE0 | 40.20 | 36.50 | 6 to 7 |
| PYRO_INHIBIT_STATE | 178.39 | 177.08 | 9 to 6 |
| EMU_BOOTSEL_SW / EMU_RUN | 39.14 / 53.66 | 39.30 / 53.73 | 2 to 4 / 4 to 4 |
| sense and face-bus lines (F2/F3/F5_SENSE, F2_SCL, GPIO_SPARE1) | | within 0.3 mm | within 1 |

## U18 template mapping (rotation-normalised U200/U18 local frame, mm; local north = the pin 46-60 side)

| role | flown Rev2 part, local (x, y) rot | FlatSat before | FlatSat after |
|---|---|---|---|
| L (VREG) | L3 (+2.19, -7.45) 0, pad 1 = +1V1 | L200 (+6.26, -4.11) 0, pad 1 = LX | unchanged |
| CIN 4.7 uF | C65 (+2.05, -4.91) 0, straddles pins 49/47, LX between its pads | C213 (+3.48, -4.71) 0 | unchanged |
| COUT 4.7 uF | C66 (+2.05, -5.90) 0, LX between its pads | C217 (+5.66, -2.46) 180 | unchanged; own GND via at (277.735, 92.400) |
| CFILT (AVDD) 4.7 uF | C68 (+4.24, -5.20) 270 | C215 (+5.66, -0.95) 0 | C215 (+5.66, +0.57) 180; own GND via at (278.285, 94.845) |
| AVDD 33 R | R94 (+4.24, -7.04) 270 | R200 (+5.66, +3.62) 180 | unchanged |
| DVDD 100 nF at pin 39 | C67 (+6.58, -0.81) 0 | C218 (+5.66, +0.57) 0 | C218 (+5.66, -0.95) 0; own GND via at (279.280, 93.285) |
| crystal | Y1 (-0.64, +8.39) 315 | Y200 (+0.51, +7.90) 270 | unchanged |
| flash | U11 (-3.89, -11.84) 45 | U201 (+12.82, +0.28) 0 | unchanged |

Why the flown cell could not be copied verbatim. Mapped onto U200 (r0), the template puts CIN at y 89.95, COUT at
y 88.96 and L at y 87.40, north of the pins. The emulator block ends at y 89.6, and bench_io_cable's R703/R704
(courtyards y 88.13 to 90.08, x 272.33 to 275.16) sit exactly there. CIN must straddle pins 49/47 at x 275.145 for LX
to pass between its pads. Its courtyard then overlaps R704's, and below y 90.08 there is only 0.61 mm before U200's
courtyard (y 90.69), against the 1.01 mm the 0402 courtyard needs. With CIN anywhere east of R704, VIN (pin 49) and
LX (pin 48) cannot both stay on F.Cu, because pin 48 lies between pin 49 and CIN. Rotating or moving U200 would
re-route all of its ~45 signal nets. The flash cannot reach the template's 8-13 mm either: the QSPI pins (55-60)
face north, out of the block. These are inferences from the geometry; no layout attempted them.

## VREG cell vs review item 5

| item 5 point | before | after |
|---|---|---|
| LX via in L200 pad (POFV) | via centred at the pad edge (278.403, 90.408) | via 0.10 mm off the pad at (278.028, 90.408); 0.25 mm F.Cu stub |
| LX on the surface | F.Cu 0.87 mm + In2 3.1 mm | unchanged (In2 2.7 mm). Needs R703/R704 moved, see above |
| COUT return under L200 | 0.127 mm x 3.4 mm under the L body to via (279.66, 89.575) | removed; COUT GND has its own via 0.55 mm from the pad |
| CFILT shares COUT's via | C215.2 tracked to C217.2 | C215.2 has its own via 0.58 mm from the pad |
| 1V1 path L to COUT to DVDD | COUT to pin 39 through 2 vias and In2 (C218.1 in-pad via) | all F.Cu, no via, 1V1 copper -4.5 mm |
| VREG_AVDD near LX | In2 ~1.25 mm from LX | In2 1.27 mm from LX at closest; AVDD 2 vias (was 4) |
| L200 orientation | dot = LX, unchanged | unchanged, so the bench A/B rotation in item 5 still applies |

One regression to note. The CFILT pad is now 5.6 mm (straight line) from pin 46, up from 3.7 mm. Its path is pin 46,
then F.Cu to the via at (277.783, 91.680), then In2 to the via at (279.082, 94.580), then F.Cu to C215.1. Before, it
was a 3.6 mm F.Cu run. I took this trade so that the 1V1 core-supply path, which carries the load transient item 5
asks the bench to check, is all on F.Cu.

## QSPI (track length per net, mm, same metric as via_off_pad.md)

| net | before | after | delta | vias |
|---|---|---|---|---|
| EMU_QSPI_SCLK | 29.877 | 29.877 | 0 | 4 to 4 |
| EMU_QSPI_SD0 | 48.524 | 48.524 | 0 | 3 to 3 |
| EMU_QSPI_SD1 | 44.428 | 44.428 | 0 | 8 to 8 |
| EMU_QSPI_SD2 | 45.699 | 45.846 | +0.147 | 8 to 8 |
| EMU_QSPI_SD3 | 31.111 | 31.111 | 0 | 5 to 5 |
| EMU_QSPI_SS | 25.817 | 25.723 | -0.094 | 6 to 4 |

The bonus of shortening QSPI toward the flown 8-13 mm was not reached, for the block-geometry reason above. Review
item 12 already closed QSPI as acceptable at 75 MHz.

## C500 (battery-protection replica)

Only the VDD net changed. VBAT_BENCH_N, PROT_DRAIN, B-, +3V3 and INHIB_1 were not touched, and C500/C502 did not
move. Review item 3's sense loop was re-measured with `review_fixes_scripts/res.py` on the baseline and the final
board, and the results are identical: PROT_DRAIN 2.67 mOhm, VBAT_BENCH_N J500.3 to Q500 S 24.83 mOhm with the U500.6
probe at 0.00 mOhm, and B- R502.2 to Q501 S 6.63 mOhm. Review fixes 1, 2, 3, 4, 6 and 7 were not touched: the
battery, charger, J14 and injection copper is outside every rip-up window.

## Datasheet placement checks (stage-2b guidelines)

Decoupling stays at the pins. C218 moved closer to pin 39 (1.38 mm to the pin tip, was 1.6 mm), and C215 moved away
from pin 46 (see the regression above). The crystal and its load caps did not move. One side effect: C216's GND (the
DVDD 4.7 uF at pin 23) now reaches a via through Y200.4, the under-crystal link and Y200.2, about 4 mm instead of
1.6 mm. The flash pull-ups R202 to R204 did not move (within 5 mm of U201).

## Tools

These are in the repo, with a README section 10 row each:

- `FlatSat_V1/tools/pcb/closure/reroute.py` is the JSON-spec re-place and rip-up/reroute driver. Its ops are move,
  windowed rip-up with clipping, route, stitch, dogbone and prune. It uses exact fan2 checks, keeps vias off pads, and
  prunes dangling copper with KiCad's own test. It needs numpy on PYTHONPATH: `pip install --target DIR 'numpy<2.1'`
  with KiCad's python.
- `FlatSat_V1/tools/pcb/closure/regsvg.py` renders a board region to PNG.

These are in scratch only (`scripts/`): `batch.sh` (one batch with refill, gates and drcdiff), `replay.sh`,
`drcdiff.py`, `netlen.py`, `template.py` (the U18 local-frame mapping), `probe.py`, `netdump.py` and `dumpfp.py`.
The batch specs are in `specs/b1_y200.json` to `specs/b6_c500.json`.

## Renders (`renders/`)

`emu_before_all.png` and `emu_after_all.png` show the whole emulator block, all layers. `vreg_before.png` and
`vreg_after.png` show the VREG cell with LX, 1V1 and AVDD in white. `c500_before.png` and `c500_after.png` show the
C500 area with the VDD net in white. Colours: F.Cu red, In1 yellow, In2 green, B.Cu blue.

## For the parent

- Install `FlatSat_V1.kicad_pcb` only. The `.kicad_pro` and `.kicad_dru` are unchanged.
- Docs to update: via_off_pad.md (POFV list is now empty), HANDOFF/PROGRESS, and review item 5 status.
- New footprint positions for the JLC placement check: C218 and C215, same footprints, C215 now at r180.
- Open option for the owner: a verbatim flown VREG cell (LX on F.Cu between the CIN/COUT pads) needs R703/R704
  (bench_io_cable) moved about 2 mm west, as review item 5's next-rev action says. This brief did not allow moving
  those parts.
