# Detailed placement — block `emulator_core` (fix round 5, Opus)

**Block**: emulator_core (47 refs, sheet `emulator_mcu`) · **Envelope** [266.9, 89.6, 296.1, 116.9] mm ·
**Fixed anchors**: none declared; PM ruling still in force: **U200 does not move**, every other part may move
anywhere inside the envelope (anchor ICs U201/U202/Y200 kept inside the 3 mm budget anyway).

**Deliverables**

| what | path |
|---|---|
| placement (this block's refs only) | `docs/flatsat/2026-09-14_phase2_layout/detail/placement_emulator_core.json` |
| this report | `docs/flatsat/2026-09-14_phase2_layout/detail/placement_emulator_core.md` |
| rebuilt, placed scratch board | `/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_emulator_core/r5/drc/placed_r7_final.kicad_pcb` |
| merged floorplan used to rebuild it | `…/scratchpad/detail_emulator_core/r5/merged.json` |
| DRC evidence (`--refill-zones`) | `…/scratchpad/detail_emulator_core/r5/drc/drc_refill.json` (board + `.kicad_pro`/`.kicad_dru` siblings in `…/r5/drc/`) |

**Gates (canonical rebuild from `FlatSat_V1.kicad_pcb` → `outline.py` → `apply_placement.py`)**

```
apply_placement.py : applied 218; refused (heritage) []; missing refs []
                     footprints not fully inside the outline: 0
                     courtyard overlaps (same-side, >=1 new part; real polygons): 0     -> exit 0
heritage.py check --allow-zone-growth --allow-edge : 0 violation(s)                      -> exit 0
attachment_check.py: 65 new tracks/vias, 0 stub chain(s) into the flight section,
                     0 violation(s), 0 warning(s)                                        -> exit 0
envelope (real courtyard bbox, all 47 refs)        : 0 outside
position identity (delivered board vs this .json)  : 0 mismatches of 47
kicad-cli pcb drc --refill-zones (with .kicad_pro/.kicad_dru siblings):
                     49 total = clearance 7 + courtyards_overlap 1 + via_dangling 1
                              + isolated_copper 4 + footprint_type_mismatch 9
                              + lib_footprint_issues 27
                     real-DRC items (clearance / courtyard / hole / mask-bridge)
                     touching any emulator_core ref: 0
```

Identical DRC counts to round 4 — this round moved four small parts inside an already-clear pocket and
introduced nothing.

---

## 0. Fix round 5 — each audit finding → what changed → new measurement

The round-5 audit returned **FAIL** with **1 should-fix and 2 notes**. It independently reproduced every
gate and ~25 of the report's numeric claims exactly; the one substantive defect was in the crystal
network. That finding is fixed, and while fixing it I re-derived the crystal rows **net-matched** and
found two further self-inflicted measurement problems in the round-4 report that the auditor had not yet
reached (§0.2). All of them are corrected below with numbers.

### SF-1 (should-fix) — the crystal load-capacitor network was not symmetric; row 15's C222 figure was the wrong pad

> *"This load capacitance is achieved by placing two capacitors of equal value, one on each side of the
> crystal to ground (C3 and C4)… the parasitic capacitance of the PCB traces are a factor, and we
> therefore need to keep them small so we don't upset the crystal and stop it oscillating as intended.
> **Try and keep the layout as short as possible.**"* — HW-RP2350 (RP-008280-DS-2) §4 p.13, re-read
> verbatim this round from the cached PDF text (`…/r4/hwrp2350.txt` lines 550–559).

**The auditor was right.** On the round-4 board `C222` was mounted with its signal and GND pads mirrored
relative to `C221`: its `Net-(C222-Pad1)` pad was **2.444 mm** from `Y200` pin 3 while the 2.083 mm the
report quoted was C222's **GND** pad. Two "symmetric" legs of 2.083 and 2.444 mm — a 17 % mismatch.

**What changed.** Rather than take the auditor's free one-line fix (rotate C222 90° → 270°, which would
have equalised the legs at 2.083 mm and left everything else untouched), the whole four-part crystal
cluster was re-solved, because re-measuring net-matched exposed that the *XOUT side of the resonant loop
was being measured through a part that is not on that net* (§0.2, C-2). Only `Y200`, `C221`, `C222`,
`R201` moved. **U200 and the other 43 refs are byte-identical to round 4.**

| ref | round 4 | round 5 | note |
|---|---|---|---|
| Y200 | 273.000, 102.350, rot 0 | **273.650, 102.750, rot 270** | XIN pad moved from the crystal's far (south-west) corner to its near (north-west) corner, directly under U200 pin 21 |
| C221 | 269.850, 102.350, rot 90 | **270.420, 101.650, rot 180** | signal pad faces the XIN pin; leg is a straight horizontal 1.900 mm |
| C222 | 276.150, 102.350, rot 90 | **276.400, 104.330, rot 270** | signal pad faces the XOUT pin; leg is a straight horizontal 1.900 mm (was a mirrored, 2.444 mm GND-first placement) |
| R201 | 277.900, 102.350, rot 90 | **276.450, 101.700, rot 90** | 1 kΩ damping resistor pulled into the crystal-side node and toward U200 |

**New measurements — every one net-matched (each pad measured to the pin on *its own* net):**

| quantity | net | round 4 | round 5 |
|---|---|---|---|
| C221 pad 1 (signal) → Y200 pin 1 | `EMU_XIN` | 2.083 mm | **1.900 mm** |
| C222 pad 1 (signal) → Y200 pin 3 | `Net-(C222-Pad1)` | **2.444 mm** (report claimed 2.083) | **1.900 mm** |
| **load-cap leg mismatch** | — | **0.361 mm (17 %)** | **0.000 mm** |
| U200 pin 21 XIN → Y200 pin 1 | `EMU_XIN` | 4.928 mm | **3.388 mm** |
| R201 pad 1 (crystal side) → Y200 pin 3 | `Net-(C222-Pad1)` | 4.036 mm | **2.548 mm** |
| R201 pad 2 (chip side) → U200 pin 22 | `EMU_XOUT` | 6.258 mm | **4.703 mm** |
| **resonant-loop copper** (XIN node MST + XOUT-crystal node MST) | — | **11.205 mm** | **8.829 mm** |

Both load capacitors are 15 pF (schematic `emulator_mcu.kicad_sch`), they sit one on each side of the
crystal (C221 west of pin 1, C222 east of pin 3 — the two signal corners of the 3225 package), and their
legs are now **identical straight 1.900 mm runs**, not merely "equal-ish". For the record, the GND-pad
distances — the numbers round 4 accidentally reported — are now 2.860 mm (C221) and 2.129 mm (C222) and
are *not* what any row claims. **Resolved.**

*Why the cluster was re-solved rather than nudged.* The search space was enumerated on a 0.05 mm grid
(`…/r5/search9.py`): four rotations × all positions for Y200 within its 3 mm anchor budget, and all
courtyard-legal positions for C221/C222/R201, scored on
`MST(XIN node) + MST(XOUT-crystal node) + 0.5·(chip-side XOUT leg) + 2·|C221 leg − C222 leg|`,
subject to ≥ 0.50 mm courtyard gaps against all 468 footprints on the board, envelope containment,
Y200 ≤ 3 mm from its floorplan_v2 position, and Y200 ≥ 5 mm from L200. The chosen solution is the
optimum of that search; the runner-up (Y200 rot 180 at 271.65, 102.35 — a much smaller 1.007 mm anchor
move) scores 12.169 against 11.056 and gives 2.020/2.012 mm cap legs, i.e. worse on both the loop length
and symmetry. The audit's minimal one-line fix scores 13.13 mm of loop copper against 8.829 mm here.

*Why the chip-side leg is weighted lower.* `R201` (1 kΩ, the damping resistor HW-RP2350 §4 requires) sits
**between** U200's XOUT driver and the crystal node. The parasitic capacitance that adds to the crystal's
10 pF load is the capacitance of the two *resonant* nodes — `EMU_XIN` (U200 pin 21 + Y200 pin 1 + C221)
and `Net-(C222-Pad1)` (Y200 pin 3 + C222 + R201 pad 1). The `EMU_XOUT` segment on the far side of the
1 kΩ is driven by the chip and is not part of the load network. Both were nevertheless shortened this
round (4.703 mm vs 6.258 mm).

### N-1 (note) — VREG_PGND "single point / 2 adjacent vias", C_FILT not sharing a GND via

Carried forward verbatim as a **routing-stage requirement**, not scored here. HW-RP2350 §6.3.8.1:
*"The GND via placement is critical… a short-as-possible, low impedance GND path back to the QFN GND pad
from the high-current GND at one single point (using 2 adjacent vias to reduce the impedance)"* and
*"[C_FILT] must also have a low impedance and short-as-possible path back to the QFN GND pad (don't share
any GND vias with the C_IN/C_OUT high current GND)."*
Placement has done what placement can: C213 (C_IN) GND pad **2.033 mm** and C217 (C_OUT) GND pad
**2.911 mm** from pin 47, with C215's (C_FILT) GND terminal on the opposite (east) side of the corridor.
**Routing must**: (a) tie C213's and C217's GND pads to **one shared pair of adjacent vias** near pin 47;
(b) give C215's GND pad **its own** via, sharing nothing with (a); (c) not use either as a general pour
stitching point. Nothing on an unrouted board demonstrates or violates this.

### N-2 (note) — copper cutout under L200 / the VREG_LX node

Carried forward verbatim as a **pour-stage requirement**. HW-RP2350 §6.3.8.1 / Fig. 24: *"On the top
layer make sure to cut away any extra copper underneath the inductor… For a multi-layer board (4 or more
layers) please cut away any copper immediately underneath L_X/VREG_LX node."* L200's courtyard on the
delivered board is **[278.105, 89.655] – [280.695, 91.845]**; when zones are refilled, that rectangle
(plus the C217 side of the LX net) needs a keepout on F.Cu and on the layer(s) immediately beneath.
Not a placement defect.

### 0.2 Corrections to round-4 numbers found while re-measuring (self-reported)

Four figures in the round-4 report were measured with the wrong convention. None changes a pass/fail, all
are corrected in the tables below and listed here so the reader does not have to find them:

* **C-1 — C216 → L200 courtyard gap: 7.230 mm → 7.931 mm.** Round 4 reported only the *vertical*
  component (`dy`); the two courtyards are also 3.260 mm apart in `x`, so the real 2-D courtyard gap is
  `hypot(3.260, 7.230) = 7.931 mm`. The rule ("don't place the second 4.7 µF near LX/C_OUT") passes by
  more than reported, not less.
* **C-2 — "R201 → Y200 pin 3 = 3.815 mm" was the geometric-nearest pad, which is R201's `EMU_XOUT`
  (chip-side) pad — the pad that is *not* on Y200 pin 3's net.** The net-matched figure on the round-4
  board was **4.036 mm** (R201 pad 1). It is **2.548 mm** now. The crystal rows in §2 are all net-matched
  this round, and the table states the net for each.
* **C-3 — "Y200 pin 3 (XOUT) → U200 pin 22 = 3.482 mm" (round-4 row 14) measured two pads that are on
  different nets.** `Y200` pin 3 is `Net-(C222-Pad1)`; `U200` pin 22 is `EMU_XOUT`; `R201` is in series
  between them. There is no direct XOUT trace, so that number never described anything on the board. Row
  14 is restated this round as the three real net-matched segments.
* **C-4 — TP202/TP203 "nearest courtyard neighbour" was scanned intra-block only.** Their true nearest
  neighbours are in other blocks: **TP202 – C303 0.549 mm** and **TP203 – U302 0.565 mm** (both ≥ 0.5 mm,
  so the conclusion stands, but the quoted 1.407 mm was the nearest *emulator_core* part, not the nearest
  part).

---

## 1. Round-4 fixes — reconfirmed on this round's board

The round-5 audit independently reconfirmed all of these as resolved; they are unchanged by this round
(none of the parts involved moved) and were re-measured on the delivered file:

| round-4 item | status on `placed_r7_final.kicad_pcb` |
|---|---|
| MF-1 VREG_PGND switching return | C213 (C_IN) GND → pin 47 **2.033 mm**; C217 (C_OUT) GND → pin 47 **2.911 mm**; C217 1V1 → L200 1V1 **1.827 mm**; C213 3V3 → pin 49 **1.859 mm**; 2nd 4.7 µF C216 → DVDD pin 23 **1.308 mm** |
| MF-2 undisclosed sub-0.5 mm pairs | complete scan in §3 — **11 pairs, all PM-accepted capacitor trades; 0 cross-block** |
| SF-1 R202/R204/D200 far from the flash | R202 **2.552**, R203 **3.083**, R204 **3.190**, D200 **3.263** mm to the nearest U201 pad |
| SF-2 DRC without `--refill-zones` | every DRC run this round uses `--refill-zones` with the `.kicad_pro`/`.kicad_dru` siblings |
| SF-3 TP202 boxed in mid-block | TP202/TP203 on the south envelope edge (1.104 mm), TP200/TP201 on the east edge (0.205 mm); min gap to any neighbour **0.549 mm** |
| N-1 R205–Y200 / L200–U201 near-zero gaps | gone; no sub-0.5 mm pair on the board involves two non-capacitor parts |

---

## 2. Guideline checklist — every row re-measured on `placed_r7_final.kicad_pcb`

Sources, all fetched and read (round 4) and re-read from the cached text this round:

* **HW-RP2350** = *Hardware design with RP2350*, Raspberry Pi **RP-008280-DS-2**
  (`https://pip-assets.raspberrypi.com/categories/1214-rp2350/documents/RP-008280-DS-2-hardware-design-with-rp2350.pdf`)
* **DS** = *RP2350 Datasheet* (`https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf`), §1.2.1.1
  Fig. 2 (QFN-60 pinout), §6.3.8 / 6.3.8.1 / 6.3.8.2
* **AUDIT-R5** = the independent audit `detail/audit_emulator_core.md` (its rules are rows 31–33)
* **AP2112K** LDO and **W25Q128JVS** flash: standard-practice rows, marked `[FALLBACK]`, with the reason

Distances are **pad centre to pad centre**, and every crystal/regulator row names the **net** it is
measured on. Gaps are **real KiCad courtyard polygons, bbox convention** (the auditor's method), with
`BuildCourtyardCaches()` called before any courtyard is read.

| # | rule | source | criterion | measured | pass |
|---|---|---|---|---|---|
| 1 | C_IN close to VREG_VIN | HW-RP2350 §2.1 p.5 *"As large currents are switched from VREG_VIN to VREG_LX, a large capacitor (C6) close to the input is required"*; DS §6.3.8.2 *"C_IN should be at least 4.7 μF"* | 4.7 µF, ≤ 3 mm to pin 49 | C213 4.7 µF, `3V3_EMU` pad → pin 49 = **1.859 mm** | **pass** |
| 2 | C_IN's own short GND path to PGND | DS §6.3.8.1 | C_IN GND pad ≤ 3 mm from pin 47 | C213 GND pad → pin 47 = **2.033 mm** | **pass** |
| 3 | Inductor adjacent to VREG_LX | DS §6.3.8.1 *"Reduce parasitics on the VREG_LX node"*; Fig. 23 | L pad to pin 48 as small as geometry allows (ref. layout ≈ 1–3 mm) | L200 `VREG_LX` pad → pin 48 = **3.617 mm** | **deviation, floor demonstrated (§4 D-1)** |
| 4 | C_OUT between the regulator pins, as close as practical | DS §6.3.8.1 *"It must be placed between VREG_VIN and VREG_PGND as close to the pins as practically possible"* | C_OUT GND ≤ 3 mm from pin 47, adjacent to L | C217 GND pad → pin 47 = **2.911 mm**; C217 `1V1_EMU` pad → L200 `1V1_EMU` pad = **1.827 mm**; courtyard gap C217–L200 = **0.050 mm** | **pass** |
| 5 | Second 4.7 µF on V_OUT at DVDD pin 23, away from LX/C_OUT | DS §6.3.8.1 *"…located on the bottom edge of the package (DVDD pin 23 on the QFN-60). Don't place this near LX/COUT"* | 4.7 µF at pin 23, far from L200/C217 | C216 `1V1_EMU` pad → pin 23 = **1.308 mm**; C216 → L200 courtyard = **7.931 mm** (2-D; round 4 quoted the 7.230 mm vertical component — correction C-1) | **pass** |
| 6 | VREG_FB fed from the C_OUT node, not routed under LX | DS §6.3.8.1 | FB pin's nearest C_OUT terminal, routable clear of L200 | pin 50 VREG_FB → C217 `1V1_EMU` pad = **5.066 mm**; L200 occupies y 89.655–91.845 at x 278.105–280.695, the FB pin is at (274.345, 91.418), so a route along y ≈ 92.4 reaches C217 without passing under L200 | **pass (placement permits it; routing is a later stage)** |
| 7 | VREG_AVDD RC-filtered, cap at the pin, its own GND return | HW-RP2350 §2.1 p.7 *"an RC filter of 33 Ω and 4.7 μF is adequate"*; DS §6.3.8.1 | C_FILT at pin 46; C_FILT GND not shared with C_IN/C_OUT | C215 `VREG_AVDD` pad → pin 46 = **3.419 mm**; R200 33 Ω `VREG_AVDD` pad → C215 = **4.560 mm**; C215's GND terminal is on the corridor's east side, **1.828 mm** from the nearest C_IN/C_OUT GND terminal (C217), so it can take its own via | **deviation, named (§4 D-2)**; via topology carried to routing (§0 N-1) |
| 8 | C_IN / L / C_OUT not on the opposite side of the PCB | DS §6.3.8.1 | all on F.Cu with U200 | C213, L200, C217, U200 all `side: F` | **pass** |
| 9 | 100 nF per power pin, close to the pin | HW-RP2350 §2.2.1 p.8 *"it is important to place decoupling close to the power pins… a 100 nF capacitor per power pin"* | every IOVDD/DVDD/USB_OTP_VDD/QSPI_IOVDD/ADC_AVDD pin ≤ 2 mm pad-to-pad from a same-rail capacitor pad | pin 1 **1.845** · 6 **1.798** · 11 **1.843** · 20 **1.597** · 23 **1.308** · 30 **1.294** · 38 **2.714** · 39 **1.987** · 44 **2.354** · 45 **1.964** · 49 **1.859** · 53 **2.197** · 54 **1.885** | **10 of 13 pass; 3 named deviations (§4 D-3, D-4, D-5)** |
| 10 | Pins 53/54 may share one capacitor when the regulator needs the space | HW-RP2350 §2.2.1 p.8 verbatim: *"In this design, pins 53 and 54 of RP2350A … share a single capacitor (C12 …), as there is not a lot of room on that side of the device, and the components and layout of the regulator take precedence."* | one 100 nF serving both | C212 serves pin 54 at **1.885 mm**, pin 53 at **2.197 mm** | **pass (the reference design's own documented compromise)** |
| 11 | QSPI wired directly to the flash, short connections | HW-RP2350 §3.1 p.10 | shortest practical U200 pin 60 → U201 pin 1 | **12.168 mm** | **deviation, named (§4 D-6)** |
| 12 | R1 / R6 (and R9/R10) close to the flash chip | HW-RP2350 §3.1 p.11 verbatim | ≤ 5 mm to a U201 pad | R202 (R1) **2.552** · R203 **3.083** · R204 (R6) **3.190** · D200 **3.263** | **pass** |
| 13 | Flash VCC decoupling at the flash | `[FALLBACK]` — the W25Q128JV datasheet has no layout section; standard practice 100 nF within 1–2 mm of VCC | C220 ≤ 2 mm from U201 pin 8 | C220 `3V3_EMU` pad → U201 pin 8 = **1.677 mm** (nearest U201 pad 1.664 mm) | **pass** |
| 14 | Crystal close to XIN/XOUT; keep the layout short | HW-RP2350 §4 p.13 *"…the parasitic capacitance of the PCB traces are a factor… Try and keep the layout as short as possible"*; working criterion ≤ 5 mm per resonant segment | each **net-matched** segment of the crystal loop ≤ 5 mm | `EMU_XIN`: U200 pin 21 → Y200 pin 1 = **3.388 mm**. `Net-(C222-Pad1)`: Y200 pin 3 → R201 pad 1 = **2.548 mm**. `EMU_XOUT` (driver side of the 1 kΩ, not in the resonant loop): U200 pin 22 → R201 pad 2 = **4.703 mm**. There is **no** direct XOUT pad-to-pad trace — R201 is in series (correction C-3) | **pass (all three ≤ 5 mm)** |
| 15 | Two equal load caps, one each side of the crystal, short matched traces | HW-RP2350 §4 p.13 verbatim: *"This load capacitance is achieved by placing two capacitors of equal value, one on each side of the crystal to ground (C3 and C4)"* | equal value; **signal** pad of each ≤ 2 mm from the crystal pin **on that same net**; the two legs matched | C221 = C222 = **15 pF** (schematic). C221 pad 1 (`EMU_XIN`) → Y200 pin 1 = **1.900 mm**; C222 pad 1 (`Net-(C222-Pad1)`) → Y200 pin 3 = **1.900 mm**; **mismatch 0.000 mm**. Both legs are straight horizontal runs with no pad of any other footprint within 0.30 mm of the centreline. (GND-pad distances, for contrast: 2.860 / 2.129 mm — not what this row claims) | **pass** |
| 16 | 1 kΩ series damping resistor in the XOUT leg | HW-RP2350 §4 p.13 *"a 1 kΩ series resistor (R2) … to prevent the crystal being over-driven"* | R201 = 1 kΩ, in series in the XOUT leg, close to the crystal node | R201 **1 kΩ**; pad 1 on `Net-(C222-Pad1)` **2.548 mm** from Y200 pin 3; pad 2 on `EMU_XOUT` **4.703 mm** from U200 pin 22 (round 4 quoted 3.815 mm, which was the chip-side pad measured to the crystal pin — correction C-2) | **pass** |
| 17 | Keep the switching node away from the crystal | `[FALLBACK]` — neither document gives a number; PM rule (4) sets ≥ 5 mm | L200 / VREG_LX ≥ 5 mm from Y200 | L200 courtyard → Y200 courtyard = **9.170 mm**; centre-to-centre **13.306 mm** | **pass** |
| 18 | USB series resistors close to the chip | HW-RP2350 §5.1 p.15 | R703/R704 (bench_io_cable) adjacent to pins 51/52 | not this block's refs; their floorplan_v2 positions (272.845 / 274.645, 89.1) are honoured and worked around | **n/a (respected)** |
| 19 | LDO input capacitor at VIN | `[FALLBACK]` — AP2112K's layout note is a generic "place C_IN/C_OUT as close as possible to the IC"; applied as ≤ 2 mm | C200/C201 ≤ 2 mm to a U202 VIN pad | C201 100 nF **1.869 mm**; C200 1 µF **1.788 mm** | **pass** |
| 20 | LDO output capacitor at VOUT | same `[FALLBACK]` | C202/C203 ≤ 2 mm to U202 pin 5 | C203 100 nF **1.578 mm**; C202 10 µF **3.393 mm** | **partial — HF cap passes, bulk named in §4 D-7** |
| 21 | Test points reachable at a block edge with probe clearance | placement constraint (g) | on a block edge, ≥ 0.5 mm courtyard gap all round | TP200 (VBUS_EMU) nearest C202 **0.860**, TP201 (3V3_EMU) nearest R211 **0.839**, TP202 (1V1_EMU) nearest **C303 0.549**, TP203 (EMU_GPIO_RSVD) nearest **U302 0.565**; TP200/201 0.205 mm from the east envelope edge, TP202/203 1.104 mm from the south edge (correction C-4: the scan is now all-board, not intra-block) | **pass** |
| 22 | RP2350-E9 external GPIO pull-downs present | DS erratum **RP2350-E9** — requires an external pull-down on affected inputs; states no placement distance | R208/R209/R210 4.7 kΩ on the spare GPIOs | R208 → pin 32 **8.960**, R209 → pin 33 **11.368**, R210 → pin 37 **14.315** | **pass (DC pull-downs, no distance requirement)** |
| 23 | RUN pull-up near the RUN pin | `[FALLBACK]` — HW-RP2350 §5.4 shows the network but gives no distance; applied as ≤ 8 mm on the same side | R205 near pin 26 | **6.060 mm** | **pass** |
| 24 | All block parts inside the envelope | constraint (a) | real courtyard bbox inside [266.9, 89.6, 296.1, 116.9] | **0 of 47 outside** | **pass** |
| 25 | No courtyard overlap with anything on the board | constraint (d), `apply_placement.py` real polygons | 0 overlaps | **0** | **pass** |
| 26 | ≥ 0.50 mm courtyard-to-courtyard except PM-accepted trades | constraint (h) + PM ruling | complete sub-0.5 mm table disclosed | **11 intra-block pairs, all accepted trades; 0 cross-block — §3** | **pass** |
| 27 | Heritage frozen, nothing new inside the Rev2 outline | constraint (f) | `heritage.py check … --allow-zone-growth --allow-edge` = 0 | **0 violations** | **pass** |
| 28 | Attachment reach to the FC pads not worse by > 3 mm | constraint (c) / brief L11 | `attachment_check.py` = 0 violations, 0 warnings | **0 / 0** | **pass** |
| 29 | Anchor ICs move ≤ 3 mm | constraint (c) as amended | U200 / U201 / U202 / Y200 | U200 **0.000**, U201 **1.500**, U202 **0.000** (rot 0 → 180), Y200 **2.725** | **pass** |
| 30 | 12.6 mm L3 lane free of parts > 2 mm tall | constraint (e) | lane x 231.4–244 | no emulator_core part is west of x 266.9 | **pass (n/a)** |
| **31** | **AUDIT-R5 §1 — load-cap network genuinely symmetric, measured net-to-net** | AUDIT-R5 §1 (source: HW-RP2350 §4 p.13) | the two capacitors' **signal-net** pads equidistant from their crystal pins | **1.900 mm / 1.900 mm, mismatch 0.000 mm** (§0 SF-1) | **pass** |
| **32** | **AUDIT-R5 §2 — VREG_PGND single-point GND return, 2 adjacent vias, C_FILT on its own via** | AUDIT-R5 §2 (source: HW-RP2350 §6.3.8.1) | not decidable at placement; distances done, topology specified for routing | C213 GND **2.033 mm**, C217 GND **2.911 mm** from pin 47; C215's GND terminal isolated on the corridor's east side. Routing instruction recorded in §0 N-1 | **carried forward (not a placement defect)** |
| **33** | **AUDIT-R5 §3 — copper cut away under L200 / VREG_LX** | AUDIT-R5 §3 (source: HW-RP2350 §6.3.8.1, Fig. 24) | pour/keepout instruction for the refill stage | L200 courtyard [278.105, 89.655]–[280.695, 91.845] recorded as the keepout rectangle in §0 N-2 | **carried forward (not a placement defect)** |

**Rules checked 33 · rules failed 0 · named deviations 7 (§4) · routing/pour items carried forward 2.**

### 2.1 Routability of the crystal legs (measured, not asserted)

Straight pad-to-pad distance is the convention above and in the audit. Because row 15 claims *matched
straight legs*, they were also checked as real tracks (0.20 mm track + 0.20 mm clearance ⇒ the centreline
must clear any foreign pad edge by 0.30 mm), script `…/r5/route_check.py`:

| segment | straight length | min centreline → foreign pad edge | verdict |
|---|---|---|---|
| C221 pad 1 → Y200 pin 1 | 1.900 mm | no foreign pad within 0.30 mm of the run | straight run is DRC-clean |
| C222 pad 1 → Y200 pin 3 | 1.900 mm | no foreign pad within 0.30 mm of the run | straight run is DRC-clean |
| R201 pad 1 → Y200 pin 3 | 2.548 mm | no foreign pad within 0.30 mm of the run | straight run is DRC-clean |
| U200 pin 21 → Y200 pin 1 (`EMU_XIN`) | 3.388 mm | **0.417 mm** (C216 pad 1) / 0.457 mm (C206 pad 2) on a two-segment route of **3.430 mm** | clean, +0.042 mm over the straight line |
| U200 pin 22 → R201 pad 2 (`EMU_XOUT`) | 4.703 mm | no F.Cu straight run: the direct line crosses C216's pads. A measured DRC-clean F.Cu detour east of C207 is **8.943 mm** (min clearance 0.340 mm); a via to an inner layer is shorter | **routing choice, disclosed** |

The XIN escape threads the decoupling row south of U200 through the **0.900 mm** pad-to-pad channel
between C206 and C216 (a 0.20 mm track with 0.20 mm clearance needs 0.60 mm, so there is 0.30 mm to
spare); the neighbouring channels are 0.890 mm (C209–C206) and 0.900 mm (C216–C207). The `EMU_XOUT`
driver segment is the one leg that cannot leave U200's south edge on F.Cu without a detour (8.943 mm
measured, DRC-clean, or a via to an inner layer) — it is outboard of the 1 kΩ and therefore not part of
the load network, and it is 1.555 mm shorter than it was in round 4 in any case. Round 4's own
`EMU_XOUT` and `EMU_XIN` legs were equally non-straight (blocked by C216/C207 and by C206 respectively),
so this is not a regression introduced by the re-layout.

---

## 3. Complete courtyard-gap scan below 0.50 mm — the delivered board

Method: `fp.BuildCourtyardCaches()` then `GetCourtyard(F_CrtYd).BBox()` for **all 218 footprints** on
`placed_r7_final.kicad_pcb`, read straight off the file with no in-memory edits; all 47×46/2 intra-block
pairs plus all 47 × 171 cross-block pairs. Nothing is omitted — this is the whole table.

| pair | gap | classification |
|---|---|---|
| C210 – U200 | 0.035 mm | accepted trade (PM) — 100 nF against IOVDD pin 1 |
| C212 – U200 | 0.035 mm | accepted trade (PM) — 100 nF against QSPI_IOVDD pin 54 / USB_OTP_VDD pin 53 |
| C213 – U200 | 0.035 mm | accepted trade (PM) — regulator **C_IN** against VREG_VIN pin 49 / VREG_PGND pin 47 |
| C217 – L200 | 0.050 mm | accepted trade (PM) — regulator **C_OUT** against the inductor it serves (DS §6.3.8.1) |
| C206 – U200 | 0.055 mm | accepted trade (PM) — 100 nF against IOVDD pin 20 |
| C207 – U200 | 0.055 mm | accepted trade (PM) — 100 nF against IOVDD pin 30 |
| C209 – U200 | 0.055 mm | accepted trade (PM) — 100 nF, 3V3 rail cap at the south-west pin corner |
| C216 – U200 | 0.055 mm | accepted trade (PM) — second 4.7 µF against DVDD pin 23 (DS §6.3.8.1) |
| C220 – U201 | 0.055 mm | accepted trade (PM) — flash VCC decoupling against U201 pin 8 |
| C200 – U202 | 0.220 mm | accepted trade (PM) — LDO input capacitor against U202's VIN pins |
| C203 – U202 | 0.240 mm | accepted trade (PM) — LDO output capacitor against U202's VOUT pin |

**Total 11, overlaps 0** — the same eleven as round 4 (none of the four parts that moved this round is in
the list, before or after). Every one is a capacitor sitting against the pin (or, for C217, the inductor)
it serves. **No pair between two non-capacitor parts is below 0.5 mm.**

**Cross-block scan (47 block refs × 171 other footprints): 0 pairs below 0.50 mm.** The five closest
pairs on the whole board involving this block are C212–R703 **0.505**, C213–R704 **0.505**, TP202–C303
**0.549**, TP203–U302 **0.565**, U200–R703 **0.615** mm.

Nearest neighbour of each of the four parts that moved, scanned against **all 217 other footprints**
(not just the ones that did not move): Y200 **0.500** (C222), C221 **0.530** (Y200), C222 **0.500**
(Y200), R201 **0.540** (Y200); next-nearest are Y200–C206 0.520, C221–C206 1.060, C222–R201 0.700,
R201–C207 0.640. Every one is at or above the 0.50 mm rule, and none of the four is a capacitor-against-
its-pin trade, so none of them may use the PM exemption — and none needs it.

---

## 4. Named deviations (each with the pin, the number and why)

**D-1 — L200 3.617 mm from pin 48 VREG_LX (reference layout ≈ 1–3 mm).** A demonstrated geometric floor.
L200's courtyard is 2.59 × 2.19 mm; the strip north of U200 is 1.09 mm tall (envelope edge y 89.6,
U200 courtyard top y 90.69), so L200 cannot go there in any rotation. East of U200 its left courtyard
edge cannot pass 277.31 + 0.50 = 277.81; with C213 (C_IN) occupying the right-hand north segment
(courtyard right edge 277.575) the inductor's left edge is pinned at 278.105, putting its LX pad at
x 278.70 against pin 48 at x 275.145 — 3.555 mm in x alone. Rotating L200 90° moves the LX pad *further*
(3.78 mm). Giving L200 the 277.81 slot costs C213 its position and pushes C_IN to ≥ 3.6 mm from
VREG_VIN; the datasheet ranks the input loop above LX trace length, so the inductor takes the 0.28 mm.
Accepted by the round-5 audit as "a demonstrated geometric floor, not an omission".

**D-2 — C215 (C_FILT) 3.419 mm from pin 46 VREG_AVDD; R200 4.560 mm from C215.** Pin 46 is on U200's
north edge (275.945, 91.417). The north strip above it is 1.09 mm tall and its only right-hand slot is
held by C_IN (rules 1/2, which the datasheet calls critical); the next-nearest legal position is the east
column's second slot, which is where C215 is. Putting C215 in the north slot gives 1.277 mm on AVDD but
pushes C_IN to ≥ 3.6 mm and breaks the input loop. R200 is a series element in a DC filter; its distance
to C215 constrains nothing in either document.

**D-3 — pin 38 IOVDD decoupled at 2.714 mm (target 2 mm).** The corridor between U200 (right edge
277.31) and U201 (left edge 281.27) is 3.96 mm wide: exactly one column of 0402s at x 278.80, nearest pad
column x 278.32, already 1.74 mm from U200's east pins. The column's five usable slots (y 92.40 → 98.47)
go, in datasheet-priority order, to C217 (C_OUT), C215 (VREG_AVDD filter), C218 (**DVDD pin 39 at
1.987 mm** — core supply outranks I/O supply), C208 (pin 38) and R200. Swapping C208 and C218 gives
pin 38 = 1.827 mm but pin 39 = 3.032 mm.

**D-4 — pin 44 ADC_AVDD decoupled at 2.354 mm (target 2 mm).** Pin 44 is at (276.582, 92.455), in the
corner shadow of the C_IN/inductor cluster. Its capacitor is C213 (the 4.7 µF C_IN, same `3V3_EMU` net),
whose nearest pad is 2.354 mm away; the same capacitor reaches pin 45 at 1.964 mm. The only position
that beats it is the east column's top slot (1.74 mm), which C_OUT must occupy.

**D-5 — pin 53 USB_OTP_VDD decoupled at 2.197 mm (target 2 mm).** This is the reference design's own
documented compromise, quoted verbatim in row 10. C212 is placed so the closer of the two pins — 54,
QSPI_IOVDD, which carries the flash bus switching current — gets 1.885 mm.

**D-6 — QSPI_SS run U200 pin 60 → U201 pin 1 is 12.168 mm.** Set by the block-level plan the owner
already accepted, not by this round: U200's QSPI pins 55–60 are on its **north** edge (x 270.3–272.3)
while the only space big enough for a SOIC-8 flash is **east** of U200. Moving U201 west is blocked by
U200's courtyard, north by the 1.09 mm envelope strip. U201 was moved 1.500 mm south in round 4, the
direction that opened the resistor strip fixing SF-1.

**D-7 — LDO bulk output capacitor C202 3.393 mm from U202 pin 5.** With U202 rotated 180° its VOUT pin
faces west into the 0.82 mm gap between U201 and U202, so the output caps come from the south. C203
(100 nF, the capacitor that matters for transient response) is at 1.578 mm; C202 is the 10 µF bulk behind
it. The rotation is the only one that gets *both* input caps (1.788 / 1.869 mm) *and* the HF output cap
under 2 mm — at rot 0 the output caps could get no closer than 3.47 mm.

*(The round-4 report's D-6, "crystal XIN leg 4.928 mm with 0.072 mm of margin", is gone: the XIN leg is
now 3.388 mm.)*

---

## 5. PM-accepted trades, listed as such

Per the PM ruling, courtyard gaps below 0.5 mm are accepted where the near part is a decoupling /
bootstrap / input / output capacitor sitting against the pin it serves. All eleven pairs in §3 are of
that kind and are recorded as accepted trades, not deviations:

* 0.035 mm × 3 — C210, C212, C213 against U200's north edge (pins 1, 53/54, 47/49).
* 0.050 mm × 1 — C217 (C_OUT) against L200, which DS §6.3.8.1 explicitly wants.
* 0.055 mm × 5 — C206, C207, C209, C216 against U200's south edge (pins 20, 30, corner, 23); C220
  against U201's north edge (pin 8).
* 0.220 / 0.240 mm — C200, C203 against U202's VIN / VOUT.

At a 0.035 mm courtyard gap the real copper separation here is ≈ 0.70 mm (the QFN-60's courtyard carries
0.665 mm of margin beyond its pads, the 0402's ≈ 0.25 mm), so none is a paste-print or reflow risk.
**This round added no new sub-0.5 mm pair.**

## 6. Anchor moves and reach

| ref | v1 (floorplan_v2) | now | move | note |
|---|---|---|---|---|
| U200 | 273.145, 94.855, rot 0 | 273.145, 94.855, rot 0 | **0.000 mm** | PM ruling: does not move |
| U201 | 285.965, 93.635, rot 0 | 285.965, 95.135, rot 0 | **1.500 mm** | round 4; opens the strip that fixed SF-1 |
| U202 | 293.575, 93.310, rot 0 | 293.575, 93.310, rot 180 | **0.000 mm** (rotation only) | round 4; VIN/GND north, VOUT south — D-7 |
| Y200 | 271.125, 101.725, rot 0 | **273.650, 102.750, rot 270** | **2.725 mm** | this round; puts the XIN pad under U200 pin 21 (§0 SF-1). Inside the 3 mm anchor budget |
| L200 | 279.290, 96.840, rot 0 | 279.400, 90.750, rot 0 | 6.091 mm | round 4; support part per the PM ruling, moved to VREG_LX |
| C221 | 269.000, 104.500, rot 0 | **270.420, 101.650, rot 180** | 3.184 mm | this round; support part (PM ruling) |
| C222 | 273.400, 104.500, rot 0 | **276.400, 104.330, rot 270** | 3.005 mm | this round; support part |
| R201 | 271.200, 104.500, rot 0 | **276.450, 101.700, rot 90** | 5.950 mm | this round; support part |

`attachment_check.py` reports **0 violations and 0 warnings** against `heritage_rev2.json`: no shared
net's reach to an FC pad got worse. Every net this round touched (`EMU_XIN`, `EMU_XOUT`,
`Net-(C222-Pad1)`, `GND`) is internal to the block.

## 7. Provenance / compliance

Live board `FlatSat_V1/FlatSat_V1.kicad_pcb` and everything under `FC_V5e_Production_Rev2/` were never
written — only read, and copied into the scratch directory. No KiCad GUI was opened. No git commits. All
intermediates live under
`/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_emulator_core/r5/`
(`search9.py` the placement search, `measure.py` + `checklist.py` the measurements, `route_check.py` the
routability check, `drc/` the DRC evidence with its `.kicad_pro`/`.kicad_dru` siblings).
