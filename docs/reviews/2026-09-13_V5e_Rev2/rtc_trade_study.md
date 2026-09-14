# RTC Trade Study — IC3, FC_V5e_Production_Rev2 (2026-09-13)

READ-ONLY study. No project file was modified.

## Headline

**RV-3032-C7 is NOT a drop-in.** Same SON-8 3.2×1.5×0.8 land pattern, but a completely
different pin-1..8 function map and a different I2C address (0x51 vs 0x52). Swapping it in
means rerouting IC3 and writing a new CircuitPython driver. **Recommendation: stay on
RV-3028-C7 for the Rev2 build; the QA grade (C3304278) is electrically identical to the QC
grade — QA/QC is a qualification grade (automotive AEC-Q200 vs commercial), not an accuracy
grade. Buy QA and don't wait.**

---

## As-built wiring (from FC_V5e_Production_Rev2.kicad_pcb, IC3 = `RTC:RV3028C7`, on B.Cu)

| Pad | Func | Net | Notes |
|---|---|---|---|
| 1 | CLKOUT | *unconnected* | free |
| 2 | /INT | `RTC_INT` | to RP2350 (U18); pulled up via **R5 10k → +3V3** |
| 3 | SCL | `SCL1` | |
| 4 | SDA | `SDA1` | |
| 5 | VSS | GND | metal lid also VSS |
| 6 | VBACKUP | `Net-(IC3-VBACKUP)` | via **R64 1k** to `BT1+` (BT1 = MY-1220-03 coin cell holder), **C26 100nF** to GND |
| 7 | VDD | +3V3 | |
| 8 | EVI | `Net-(IC3-EVI)` | **R14 10k → +3V3**, **TP6** test point |

Footprint pads: 8 × 0.5 × 0.8 mm, 0.9 mm pitch, rows 1.2 mm apart — standard Micro Crystal C7 land.
Series 1k on VBACKUP from a primary coin cell ⇒ trickle charger must stay disabled; backup
switchover is the level/direct-switching mode. Both RV-3028 and RV-3032 support this.

BOM state today: `jlcpcb/project.db` assigns IC3 → **C3304278** (QA), while the schematic symbol
value/MPN says the **QC** part. That mismatch is currently benign (see grade section) but should be
made deliberate.

---

## Grades: QA vs QC (settled)

From the Micro Crystal ordering diagrams:

- Suffix pattern is `RV-30xx-C7 <freq tolerance> <temp code> <grade>`.
- **QC = Commercial grade. QA = Automotive grade, AEC-Q200 qualified.**
- **TA = −40 to +85 °C** — the only temperature code offered on these parts.
- Accuracy is *not* in the QA/QC field. It is the fixed `1ppm` (RV-3028-C7) / `2.5ppm`
  (RV-3032-C7) token, identical between the QA and QC orderable parts.

RV-3028-C7 timing: ±1 ppm initial at 25 °C, uncompensated tuning-fork curve
`ΔF/F = −0.035 × (T−T0)² ppm ±10 %` ⇒ ≈ −150 to −220 ppm at the −40/+85 °C ends
(≈ 13–19 s/day worst case). Aging ±3 ppm/yr max. RV-3032-C7 is a TCXO: **±2.5 ppm over
−40..+85 °C**, ±20 ppm over +85..+105 °C.

**Is QA acceptable for this mission? Yes — it is the strictly stronger part.** Same die, same
±1 ppm, plus AEC-Q200 qualification (vibration/thermal-shock/mechanical screening that is a
plus, not a minus, for a CubeSat). The only cost is ~15–25 % unit price. There is no
mission-relevant spec on which QC beats QA.

---

## Option A — keep RV-3028-C7

Every RV-3028 SKU in the 2026-09-13 JLC parts DB:

| LCSC | MPN | Package | Stock | @10 | @100 |
|---|---|---|---|---|---|
| **C3304278** | RV-3028-C7-32.768KHZ-1PPM-TA-**QA** | SMD3215-8P | **13** | $2.565 | $2.000 |
| C3019759 | RV-3028-C7-32.768kHz-1ppm-TA-**QC** | SMD3215-8P | **0** | $1.930 | $1.548 |
| C2829066 | RV-3028-C7 (generic listing) | DFN-8(1.5x3.2) | 0 | — | — |
| C17356995 | RV-3028-C7 eval board | — | 0 | — | — |

Trend given: QC went 30,219 (Feb) → 0; QA went 179 → 2,195 → 13. JLC is draining this line and
not restocking. Treat JLC stock on RV-3028 as unreliable from here on.

Elsewhere (verify live before ordering — DigiKey blocks automated fetch):
- LCSC direct: same two SKUs as JLC, both showed out of stock / 13 pcs at check time.
- DigiKey carries RV-3028-C7-32.768KHZ-1PPM-TA-QC (P/N 10431070); Mouser 428-203591-MG01 (the
  MPN already embedded in the KiCad symbol properties). Arrow / Farnell / Newark also list the
  family. Micro Crystal sells direct through these franchised distributors; factory lead time on
  a non-stock C7 order is typically 8–12 weeks — that is the schedule killer if JLC and the
  catalogue distributors are both dry.

Consignment at JLC if bought outside (jlcpcb.com/help/article/how-to-consign-parts-to-jlcpcb):
- Handling fee **declared value × 2 %, min US$10 per shipment**.
- Import duty + 13 % import VAT collected as refundable deposit.
- Retrieval fee if you pull stock back out: 30 % of value, **min US$30**, 7 days notice.
- Free storage up to 3 years. Intake review ~2 business days after the parts land in HK.
- No published hard minimum qty, but JLC expects an attrition buffer above exact BOM need —
  send **BOM qty + ~20 % / at least +5 pcs**.
- Practical effect: consignment adds ~1–2 weeks and ≥$10–40 of fees, plus the shipping leg.

## Option B — swap to RV-3032-C7

| Aspect | Finding |
|---|---|
| Package | Identical SON-8 ceramic, 3.2 × 1.5 × 0.8 mm, same recommended land pattern. Lid = VSS = pin 5 on both. **Existing copper pads fit.** |
| Pinout | **Different.** RV-3028: 1 CLKOUT, 2 /INT, 3 SCL, 4 SDA, 5 VSS, 6 VBACKUP, 7 VDD, 8 EVI. RV-3032: 1 VBACKUP, 2 SDA, 3 /INT, 4 EVI, 5 VSS, 6 VDD, 7 CLKOUT, 8 SCL. Only VSS coincides. ⇒ **new symbol + full reroute of 6 nets on a dense inner region of a flight board.** |
| I2C address | 0x52 → **0x51**. Check for a collision with anything else at 0x51 on I2C1 before assuming free. |
| Supply current | RV-3028 **45 nA typ / 60 nA max @3 V**; RV-3032 **160 nA typ / 210 nA max** (TCXO overhead). ~3.5× the backup-mode drain on the CR1220 — still negligible vs cell self-discharge, but not nothing. VDD 1.3–5.5 V (vs 1.1–5.5 V). |
| Backup / trickle | Same feature set: automatic backup switchover + integrated (charge-pump) trickle charger, no external diode. The R64 1k + 100nF + primary cell wiring works unchanged, trickle charger left disabled. |
| Timing | ±2.5 ppm over −40..+85 °C (temperature compensated) vs RV-3028's ~±200 ppm at the extremes. **This is the one real technical win** — ~0.2 s/day worst case vs ~15 s/day. |
| Registers / driver | **No CircuitPython or MicroPython RV-3032 driver exists.** Only a C driver (gfcwfzkm/RTC-RV3032) and an Arduino port (KineticLabs25/RV-3032-C7). PROVES uses its own `proveskit/PROVES_CircuitPython_RV3028` (addr 0x52; regs 0x00-0x28 + EEPROM 0x35/0x36/0x37, EECMD sequence, BSM/trickle bits). Time/date/alarm regs 0x00–0x09 carry over; **EEPROM/PMU/backup-switchover block, control/status bit positions, CLKOUT/interrupt-mask split, EE command codes, EEPROM password feature, and a new 12-bit temperature register all differ** and must be rewritten against the RV-3032 App Manual. Est. **1–3 days of driver work + bench validation**, plus a new flight-software release and regression. |
| JLC stock (2026-09-13) | C5366550 RV-3032-C7-2.5PPM-TA-**QA** SMD3215-8P **550 pcs**, $2.980@10 / $2.404@100. C5127802 (QC) **1 pc**. C5158624 0. C9900204995 0. |

### Other JLC RTCs considered — none are drop-in
Verified against the datasheet pin tables: **no** other Micro Crystal C7 part shares the
RV-3028 pinout.

| Part | JLC stock | Pinout vs 3028 | Addr | Why not |
|---|---|---|---|---|
| RV-4162-C7 QC (C3304279) | 9,812 | different | 0x68 | **no VBACKUP, no EVI** — loses the backup battery entirely |
| RV-8263-C7 QA (C5137460) | 455 | different | 0x51 | no VBACKUP/EVI; 20 ppm |
| RV-8803-C7 QA (C5341296) | 39 | different | 0x32 | no VBACKUP (has CLKOE) |
| RV-8263-C8 QA (C24955829) | 813 | different pkg (2012) | 0x51 | different footprint too |

---

## Comparison

| | **A: RV-3028-C7 (QA, C3304278)** | **B: RV-3032-C7 (QA, C5366550)** |
|---|---|---|
| Footprint compatible | Yes — as built | Pads yes, **pinout no → reroute required** |
| Schematic/layout change | none | new symbol, 6 nets rerouted, ECO + DRC + refab risk |
| Stock @ JLC today | **13** | **550** |
| Stock elsewhere | LCSC 0–13; DigiKey/Mouser/Arrow/Farnell list it, verify live; factory ~8–12 wk | DigiKey ≈$3.04 (QC) / $3.17 (QA) listed; LCSC ~40 |
| Price @10 / @100 | $2.57 / $2.00 | $2.98 / $2.40 |
| Firmware effort | **zero** — PROVES_CircuitPython_RV3028 is flight-proven | **1–3 days new driver + bench + flight-SW release**; no existing CP driver |
| Timing spec | ±1 ppm @25 °C, ~±200 ppm over TA | **±2.5 ppm over full TA (TCXO)** |
| Backup current | 45 nA | 160 nA |
| Schedule risk | **supply risk** (13 pcs, trending to zero) | **engineering risk** (layout spin + unwritten driver) |

---

## Recommendation

**10-board Rev2 order — Option A, QA grade.** Buy C3304278 now. 13 pcs in stock covers 10 boards
only if you order today and accept zero attrition margin, so treat it as urgent. Do **not** chase
the QC SKU; it is zero and QA is the same or better part. Do not spin the layout for RV-3032 at
this stage — a pin-remap on a flight board plus an unwritten CircuitPython driver is far more
schedule and defect risk than the timing benefit is worth for a 10-board run.

**50-board build — plan the RV-3032 migration for the *next* board revision, and bridge with
RV-3028 bought outside JLC.** JLC will not have 50 pcs of RV-3028; source 55–60 pcs from
DigiKey/Mouser/Arrow and consign them (≈$10–40 in fees, ~1–2 weeks). In parallel, if the
±200 ppm cold-end drift of the uncompensated RV-3028 is actually a problem for the mission
(beacon scheduling, timestamp accuracy between GPS/ground syncs), start the RV-3032 work now so it
lands on a planned revision rather than as a panic substitution: 550 pcs in stock, TCXO accuracy,
and Micro Crystal is clearly steering the family that way. Whichever way, **write down a second
source**; the RV-3028 stock curve says this part is being deprecated at JLC.

---

## Next actions

**Immediate (Option A, this order)**
1. Order/lock **C3304278** (RV-3028-C7-32.768KHZ-1PPM-TA-QA) at JLC today — 13 pcs is the whole
   pool. Add it to the cart/quote before the BOM review.
2. Reconcile the grade mismatch so the BOM is intentional: schematic symbol value and
   `Manufacturer_Part_Number` say `RV-3028-C7 32.768kHz 1ppm TA QC`, `jlcpcb/project.db` says
   C3304278 (QA). Update the symbol's MPN/value/Mouser fields to the QA part, or add a
   "QA or QC acceptable, same die" BOM note. *(Not done — this study is read-only.)*
3. Quote 60 pcs of RV-3028-C7 (QA or QC) at DigiKey / Mouser (428-203591-MG01) / Arrow / Farnell
   and capture the lead times — this is the 50-board bridge and the fallback if the 13 pcs
   disappear before the order lands.
4. If sourcing outside: read jlcpcb.com/help/article/consignment-part-terms-conditions for the
   current attrition rule, then consign BOM qty +20 %.
5. Contact: Micro Crystal AG sales (sales@microcrystal.com) for an RV-3028-C7 lifecycle /
   last-time-buy statement and factory lead time — worth asking directly given the stock collapse.
   JLC parts team via the "request a part" / consignment ticket for the consignment quote.

**If Option B is chosen later (next revision, not Rev2)**
- New schematic symbol `RV-3032-C7` with pins 1 VBACKUP / 2 SDA / 3 /INT / 4 EVI / 5 VSS /
  6 VDD / 7 CLKOUT / 8 SCL. Reuse the existing `RTC:RV3028C7` footprint (land pattern matches);
  rename it to something neutral like `RTC:MicroCrystal_C7_SON8`.
- Rewire in the schematic: VBACKUP →pad 1 (keep R64 1k + C26 100nF from BT1+), SDA1 →pad 2,
  RTC_INT →pad 3 (keep R5 10k pull-up), EVI →pad 4 (keep R14 10k + TP6), GND →pad 5,
  +3V3 →pad 6, leave pad 7 CLKOUT unconnected, SCL1 →pad 8.
- Layout: IC3 is on **B.Cu at (194.85, 73.25, −90°)** — expect to redo all six escapes; re-run
  DRC and re-check the coin-cell and I2C1 routing.
- Firmware: fork `proveskit/PROVES_CircuitPython_RV3028` → `..._RV3032`; change address 0x52→0x51;
  rewrite `registers.py` against the RV-3032-C7 App Manual (EEPROM/PMU/backup-switchover block,
  EE command codes, control/status bits, CLKOUT + interrupt-mask split, EEPROM password); add the
  temperature register read. Keep `_read_register`/`_set_flag`/BCD/`set_time`/`get_time` as-is.
- Verify 0x51 is free on I2C1 before committing.

**LCSC numbers referenced:** C3304278 (RV-3028 QA, buy this), C3019759 (RV-3028 QC, stock 0),
C5366550 (RV-3032 QA, 550), C5127802 (RV-3032 QC, 1), C3304279 (RV-4162, not drop-in),
C5137460 (RV-8263-C7, not drop-in), C5341296 (RV-8803-C7, not drop-in).
