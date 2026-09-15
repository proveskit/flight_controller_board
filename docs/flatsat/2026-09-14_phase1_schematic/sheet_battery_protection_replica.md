# Sheet report — `battery_protection_replica` ("Battery Replica and Bench Power")

**Date:** 2026-09-14 · **Spec:** `00_pm_brief.md` rev 2 §6.4 (interface §4, format/validation §7, deliverables §8) · **Decisions:** D3, D4, D11
**Files**

| item | path |
|---|---|
| sheet | `FlatSat_V1/battery_protection_replica.kicad_sch` |
| generator | `FlatSat_V1/tools/gen/battery_protection_replica_gen.py` |
| readability checker | `FlatSat_V1/tools/gen/battery_protection_replica_textcheck.py` (text-vs-text, text-vs-wire, text-vs-symbol-body, page bounds) |
| this report | `docs/flatsat/2026-09-14_phase1_schematic/sheet_battery_protection_replica.md` |
| harness run | `<scratch>/work_battery_protection_replica/harness` (erc.json, netlist.xml), PDF page 10 of `<scratch>/work_battery_protection_replica/battery_protection_replica.pdf` |

Sheet uuid `3f1c9d64-17ab-4c2e-9b55-0d7a4e6c81b2`, sheet-symbol uuid `bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0`, instances path
`/c64c0d72-a9f6-4f3a-891e-1f647558f538/bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0`, page 10, A3, refdes block 500–599 (used 500–519 plus
C517/C518 from the review round, #PWR500–519 and #PWR590–592, #FLG500–503).

**Revision:** fix round 1 (seven findings), fix round 2 (five findings) and the **Fable review round (§12, items 1/5/8/9)** applied
2026-09-14. See §10, §11 and §12 for the finding-by-finding resolution. The review round raised CSYS to four 22 µF 25 V X5R **1210**
parts (51 µF effective at 8.4 V against the datasheet's 44 µF minimum, derating taken from a manufacturer DC-bias curve), moved CPMID and
CBAT to the same part, tied the BQ25886 OTG pin low, and put `JP500 OPEN` into the on-sheet bench-mode table for modes 2 and 3.

---

## 1. Purpose

Two independent bench sources for the FC's battery node `Dir_Chrg_In`, on one sheet:

* **A — bench PSU behind a replica of the `battery_pack_v2` protection stage (D4).** A 3-way screw terminal (B+ / MID / B−) feeds an exact copy
  of the pack's R5460N208AA + 2 × IRF7458 low-side protection, so flight software and the bench see real pack-protection behaviour
  (over-charge / over-discharge / over-current cut-off) without a lithium pack on the bench. A jumper-selectable synthetic cell midpoint
  (2 × 1.0 kΩ) stands in for the cell tap a single bench supply does not have.
* **B — power-only USB-C → BQ25886 charger (D3),** derived from `antenna-board/debug_board_v1` with that board's gaps corrected. Its BAT output
  reaches `Dir_Chrg_In` only through a 2-pin header whose shunt is **removed by default**, so the charger can never push into a bench PSU.

Nothing on the sheet is in series with the FC's `Dir_Chrg_In ↔ VBATT_SENSE ↔` inhibit chain (brief hard rule 6): both bench sources are new
branches onto `Dir_Chrg_In` / `B-`, and the only series elements are inside the replica's own low-side return.

## 2. Block description

### A. Bench PSU input + protection replica

```
J500.1 (B+)  ──┬────────────────────────────────► Dir_Chrg_In      (no series element; PACK+ is unswitched on the real pack)
               ├─ JP500 (fitted while a PSU is on J500) ─ R503 1.0k ─┬─► MID_BENCH ─┬─ J500.2 (MID)
               │                                                     │              └─ R501 330 ─┬─ U500.VC ─ C501 0.1u ─┐
               │                                                     └─ R504 1.0k ──────────────┼───────────────────────┤
               └─ R500 330 ─────────────────────────────────────── U500.VDD ─ C500 0.1u ────────┤                       │
                                                                                                 └─ VBAT_BENCH_N ◄──────┘
J500.3 (B−) ──────────────────────────── VBAT_BENCH_N ─┬─ U500.VSS
                                                       ├─ Q500.S           (DOUT / discharge FET)
                                                       ├─ C502 0.1u ─ U500.V− ─ R502 1k ─► B-
                                                       ├─ C503 0.1u ──────────────────────► B-
                                                       └─ R505 100k (bleed) ───────────────► B-
U500.DOUT ─► Q500.G      Q500.D ── common drain ── Q501.D      Q501.S ─► B-   (COUT / charge FET)
```

`U500`/`R500`–`R502`/`C500`–`C503`/`Q500`/`Q501` reproduce `battery_pack_v2` `U1` / `R5,R4,R3` / `C9,C8,C7,C5` / `Q1,Q2` node-for-node
(verified against `refs/battery_pack_v2.netlist.xml`). The only additions are the terminal, the synthetic-midpoint divider + JP500, the R505 bleed,
and six test points.

### B. USB-C → BQ25886 charger

```
J510 VBUS ─► VBUS_CHG ─┬─ Q510.D (DMP4047 P-FET) ─ Q510.S ─┬─ CHG_DVIN ─ C510 1u ─ GND
                       └─ U510.DRAIN (DZDH0401DW-7)  ──────┘            └─ U511.VBUS
   U510.BIAS ─ CHG_GATE ─ Q510.G, R512 1M→GND      U510.REF ─ CHG_REF ─ R513 1M→GND
U511 BQ25886RGE: PMID ─ C511 10u 25V ─ L510 1.0uH ─ SW ─ C512 47n ─ BTST
                 SYS  ─ CHG_SYS ─ C513+C514 = 2 x 22uF 25V X5R ─ TP511
                 BAT  ─ CHG_BAT ─ C515 10u 25V ─ TP512 ─ JP510 (OPEN by default) ─► Dir_Chrg_In
                 ILIM ─ R514 750R ;  ICHGSET ─ R515 5.7k ;  VSET / CE / PG / OTG open (no_connect)
                 REGN ─ C516 4.7u, R516 5.23k ─ TS ─ R517 30.1k ∥ R518 10k ─ GND
                 D+ tied to D−  (DCP signature to the internal BC1.2 detector; port carries no data)
                 STAT ─ D510 ─ R519 1k ─ VBUS_CHG   (charge-status LED)
```

## 3. Parts

| ref | value | footprint | LCSC | source of the LCSC number |
|---|---|---|---|---|
| J500 | BENCH PSU B+/MID/B- | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal` | **needs LCSC** | 3-pos 5.08 mm screw terminal; no as-ordered precedent in the repos |
| U500 | R5460N208AA-TR-FE | `Package_TO_SOT_SMD:SOT-23-6` | C259714 | `refs/bom/BOM-battery_pack_v2.csv` (as ordered) |
| Q500, Q501 | IRF7458 | `Package_SO:SOIC-8_3.9x4.9mm_P1.27mm` | C10879 | `BOM-battery_pack_v2.csv` (the pack schematic's `IRF7404` symbol is stale metadata) |
| R500, R501 | 330 | `Resistor_SMD:R_0603_1608Metric` | C23138 | `BOM-battery_pack_v2.csv` (pack R5/R4) |
| R502 | 1k | R_0603 | C21190 | `BOM-battery_pack_v2.csv` (pack R3) |
| R503, R504 | 1.0k 1% | `Resistor_SMD:R_0805_2012Metric` | **needs LCSC** | brief §6.4 requires 0805 1 %; no 0805 1 k in any repo BOM |
| R505 | 100k (bleed, `VBAT_BENCH_N`→`B-`) | R_0603 | C25803 | JLC catalogue, verified live 2026-09-14 (0603WAF1003T5E, Basic, 100 kΩ ±1 %, stock 23.66 M) |
| C500–C503 | 0.1uF | `Capacitor_SMD:C_0603_1608Metric` | C14663 | `BOM-battery_pack_v2.csv` (pack C9/C8/C7/C5) |
| JP500 | MID DIV – FIT (2-pin header, shunt fitted) | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | **needs LCSC** | generic 1×2 2.54 mm header |
| TP500–TP505 | Dir_Chrg_In / VBAT_BENCH_N / B- / DOUT_GATE / COUT_GATE / MID_BENCH | `TestPoint:TestPoint_Pad_D1.5mm` | n/a (pad only) | — |
| J510 | USB-C CHARGER IN (power only) | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | C165948 | brief §6.4/§6.6; `BOM-antenna_top_cap_v2c.csv`, `BOM-proves_radio_stick_V2.csv` (as ordered) |
| R510, R511 | 5.1k (CC pull-downs) | `Resistor_SMD:R_0402_1005Metric` | C25905 | brief §6.6; `BOM-proves_radio_stick_V2.csv` (as ordered) |
| Q510 | DMP4047LFDE-7 | `easyeda2kicad:U-DFN2020-6E_L2.0-W2.0-P0.65-BL` | C442635 | **verified live** 2026-09-14 (see §3.1) |
| U510 | DZDH0401DW-7 | `easyeda2kicad:SOT-363_L2.0-W1.3-P0.65-LS2.1-BR` | C3235552 | **verified live** 2026-09-14 (see §3.1) |
| R512, R513 | 1M | R_0603 | C22935 | `BOM-antenna_top_cap_v2c.csv` (as ordered) |
| U511 | BQ25886RGE | `Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm` | **needs LCSC** | `debug_board_v1` was never assembled; no verified number (brief says so too) |
| C510 | 1uF (CVBUS) | `Capacitor_SMD:C_0805_2012Metric` | C28323 | `BOM-XY_Face_V4.csv` (1 µF 0805, as ordered) |
| C511 | `22uF 25V` (CPMID, X5R) | `Capacitor_SMD:C_1210_3225Metric` | C52306 | JLC catalogue, **verified live 2026-09-14** (CL32A226KAJNNNE, 1210, Extended, **22 µF 25 V X5R ±10 %**, stock 334 k). Raised from 10 µF 0805 in the review round (§12 item 9): the 0805 held 6.7 µF at the 5 V PMID bias, the 1210 holds 19.0 µF |
| C512 | 47nF (CBTST) | C_0603 | **needs LCSC** | no 47 nF in any repo BOM |
| C513, C514, **C517, C518** | `22uF 25V` (CSYS, X5R) | `Capacitor_SMD:C_1210_3225Metric` | C52306 | same part as C511. Four parts, 1210 not 0805: §12 item 1 / PM ruling R5 — 51 µF effective at 8.4 V against the 44 µF minimum of §9.2.2.3 |
| C515 | `22uF 25V` (CBAT, X5R) | `Capacitor_SMD:C_1210_3225Metric` | C52306 | same part as C511/C513; BAT sits at 8.4 V where a 10 µF 0805 holds only 4.0 µF (§12 item 9) |
| C516 | 4.7uF 16 V (CREGN) | C_0603 | **needs LCSC** | repo 4.7 µF parts are 0402 6.3 V class |
| L510 | SPM6530T-1R0M120 (1.0 µH) | `easyeda2kicad:IND-SMD_L7.1-W6.5-P5.60` | C87572 | brief §6.4 names this part; **verified live** 2026-09-14 (see §3.1) |
| R514 | 750 (ILIM) | R_0603 | **needs LCSC** | value changed from the brief — see §7 deviation 2 |
| R515 | 5.7k (ICHGSET) | R_0603 | **needs LCSC** | brief value; not in a repo BOM |
| R516 | 5.23k (TS RT1) | R_0603 | **needs LCSC** | datasheet value 5.24 k → E96 5.23 k |
| R517 | 30.1k (TS RT2) | R_0603 | **needs LCSC** | datasheet value 30.31 k → E96 30.1 k |
| R518 | 10k (103AT stand-in) | R_0603 | C25804 | `BOM-battery_pack_v2.csv` (as ordered) |
| R519 | 1k (STAT LED) | R_0603 | C21190 | `BOM-battery_pack_v2.csv` (as ordered) |
| D510 | LED (charge status) | `LED_SMD:LED_0603_1608Metric` | C2290 | `BOM-proves_radio_stick_V2.csv` (as ordered) |
| JP510 | CHG OUT – OPEN (2-pin header, shunt removed) | `PinHeader_1x02_P2.54mm_Vertical` | **needs LCSC** | generic 1×2 2.54 mm header |
| TP510–TP512 | VBUS_CHG / CHG_SYS / CHG_BAT | `TestPoint:TestPoint_Pad_D1.5mm` | n/a | — |

**needs LCSC (summary):** J500, R503/R504 (1.0 k 1 % 0805), JP500, JP510, U511 (BQ25886RGE), C512 (47 nF 0603),
C516 (4.7 µF 0603 ≥16 V), R514 (750 R), R515 (5.7 k), R516 (5.23 k), R517 (30.1 k). `jlcpcb/project.db` was not touched.

### 3.1 LCSC numbers verified live (hard rule 5, "verified live")

Checked on 2026-09-14 against the JLCPCB catalogue — the plugin's `parts-fts5.db` (refreshed 2026-09-13) **and** the live
endpoint `https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode=<LCSC>`; both agree:

| LCSC | MFR.Part | manufacturer | package | description | library | stock |
|---|---|---|---|---|---|---|
| C442635 | DMP4047LFDE-7 | Diodes Inc. | U-DFN2020-6E | P-channel, 40 V, 6 A, 50 mΩ@4.5 V | Extended | 12 860 |
| C3235552 | DZDH0401DW-7 | Diodes Inc. | SOT-363 | 0–40 V, 300 mA ideal-diode / reverse-blocking controller | Extended | 10 938 |
| C87572 | SPM6530T-1R0M120 | TDK | SMD 7.1 × 6.5 mm | 1 µH, 13 A, 7.81 mΩ ±20 % | Extended | 11 577 |
| C15850 | CL21A106KAYNNNE | Samsung | 0805 | 10 µF 25 V X5R ±10 % | Basic | 6 938 849 |
| C45783 | CL21A226MAQNNNE | Samsung | 0805 | 22 µF 25 V X5R ±20 % | Basic | 4 842 649 (no longer used — see §12 item 1) |
| C52306 | CL32A226KAJNNNE | Samsung | 1210 | 22 µF 25 V X5R ±10 % | Extended | 333 998 (checked live in the review round, 2026-09-14) |
| C25803 | 0603WAF1003T5E | Uniroyal | 0603 | 100 kΩ ±1 %, 100 mW | Basic | 23 663 052 |

`debug_board_v1`'s BOM CSV is header-only (never assembled), so the first three numbers do **not** come from an as-ordered
BOM; the live check above is what satisfies rule 5. **C19702 was removed from C511**: the catalogue shows it as
Samsung CL10A106KP8NNNC, 0603, 10 µF **10 V** X5R — below BQ25886 §9.2.2.2's "25-V rating or higher … preferred".

*Integrator note:* the pantry block for `easyeda2kicad:SPM6530T-4R7M-HZ` carries `LCSC Part = C360729` inside its `(lib_symbols …)` definition — that
is the 4.7 µH variant's number and it is inherited from the user's global library, not set by this sheet. The **L510 instance** carries C87572, which
is what the netlist and the BOM see. Same for `DZDH0401DW-7` (C3235552) and `DMP4047LFDE-7` (C442635), where the library default happens to agree.

Symbols used (all from the validated pantry): `flatsat:R5460N208AA`, `flatsat:IRF7458`, `flatsat:VBUS_CHG`, `Battery_Management:BQ25886RGE`,
`easyeda2kicad:DZDH0401DW-7`, `easyeda2kicad:DMP4047LFDE-7`, `easyeda2kicad:SPM6530T-4R7M-HZ` (used for the 1.0 µH SPM6530T-1R0M120, exactly as
`debug_board_v1` does), `Connector:USB_C_Receptacle_USB2.0_16P`, `Connector:Screw_Terminal_01x03`, `Connector:TestPoint`, `Jumper:Jumper_2_Open`,
`Device:R/C/LED`, `power:GND`, `power:PWR_FLAG`. The integrator needs `flatsat:R5460N208AA`, `flatsat:IRF7458` and `flatsat:VBUS_CHG`
in `symbols/flatsat.kicad_sym` for the GUI to resolve them.

## 4. Interface nets

**Existing FC globals used (3):**

| net | what this sheet adds | why |
|---|---|---|
| `Dir_Chrg_In` | `J500.1` (bench PSU B+), `JP510.2` (charger output jumper), `R500.1` (R5460 VDD feed), `JP500.2` (top of the midpoint divider), `TP500.1` | the FC battery node both bench sources drive |
| `B-` | `Q501.1/2/3` (COUT FET source = pack negative), `C503.2`, `R502.2` (R5460 V− through 1 k), `R505.2` (100 k bleed), `TP502.1` | the pack-terminal negative, i.e. the return of the replica |
| `GND` | `J510` shell/GND, `U511` GND/EP, `C510/C511/C513/C514/C515/C516`, `R510–R515`, `R517`, `R518` | charger block reference only — the replica block has **no** GND connection by design |

No existing FC net loses a pin; no existing FC net is renamed. `VBAT_BENCH` does not exist as a separate net — see deviation 1.

**New nets defined here:** `VBUS_CHG` (global, via the `flatsat:VBUS_CHG` power symbol; PWR_FLAG on this sheet).
**New nets consumed from other sheets:** none.

**Sheet-local nets:** `VBAT_BENCH_N` (cell negative — brief §6.4 net-name rule), `MID_BENCH`, `DOUT_GATE`, `COUT_GATE`, `CHG_DVIN`, `CHG_GATE`,
`CHG_REF`, `CHG_SYS` (BQ25886 SYS) and `CHG_BAT` (BQ25886 BAT, isolated from `Dir_Chrg_In` by the open JP510) — the last two added in fix round 1 so
the names printed next to TP511/TP512 exist in the netlist — plus KiCad-auto names for the R5460 VDD/VC/V− nodes, the common FET drain, the divider
midpoint and the charger's PMID / SW / BTST / REGN / TS / ILIM / ICHGSET / D+D− nodes.

**PWR_FLAG ownership (brief §4.2):** `VBAT_BENCH_N` (#FLG500, at 43.18/90.17), `VBUS_CHG` (#FLG501, at 243.84/45.72 on the U510 DRAIN node),
`CHG_DVIN` (#FLG502, at 269.24/52.07 on the U510 SOURCE node), plus one on the charger's switching node (#FLG503, at 340.36/74.93) — see
deviation 4. None on `GND`, `Dir_Chrg_In` or `B-`. (Fix round 2: #FLG501 and #FLG502 were transposed in this line; the schematic was always
right — the ERC violation list shows `U510 Pin 6 [DRAIN] … #FLG501` and `U510 Pin 4 [SOURCE] … #FLG502`.)

## 5. Jumper / bench-mode table (also a text note on the sheet)

| jumper | net A ↔ net B | default | meaning |
|---|---|---|---|
| JP500 | `Dir_Chrg_In` ↔ top of the divider (`Net-(JP500-A)` = R503.1) | **shunt FITTED while a bench PSU is connected to J500** | the 2 × 1.0 k divider sets the R5460 VC node. Pulling the shunt disconnects the *whole* divider — no 4.2 mA path from `Dir_Chrg_In` to the cell-negative node — and lets a real 2-cell dual supply on J500 pin 2 (MID) set VC on its own. Moved from the divider midpoint to the divider top in fix round 1. |
| JP510 | charger BAT (`Net-(JP510-A)`) ↔ `Dir_Chrg_In` | **shunt REMOVED** (D3) | the charger reaches the board only when this is fitted, so it can never push into a bench PSU. |

| mode | JP500 | JP510 | bench |
|---|---|---|---|
| 1 — PSU through the replica | fitted | open | bench PSU on J500, charger USB unplugged |
| 2 — USB charger | **open** | fitted | bench PSU disconnected at J500 — pull JP500 so the divider draws nothing from `Dir_Chrg_In` |
| 3 — both off | **open** | open | PSU off/disconnected |

**The on-sheet note now says the same thing** (§12 item 5). Until the review round the sheet's three `Mode …` lines named only JP510, so a
technician working from the sheet alone would have left JP500 fitted in modes 2 and 3 — the state the sheet's own PSU-window warning
("PULL JP500 WHENEVER NO BENCH PSU IS CONNECTED") forbids. The lines now read:

```
Mode 1  PSU through the replica : JP500 fitted, JP510 open, charger USB unplugged.
Mode 2  USB charger             : JP500 OPEN, JP510 fitted, bench PSU disconnected at J500.
Mode 3  both off                : JP500 OPEN, JP510 open, bench PSU disconnected.
```

Both are open 2-pin headers (`Jumper:Jumper_2_Open`, `PinHeader_1x02_P2.54mm_Vertical`), never `_Bridged`, so the netlist keeps the two nets
separate (brief rule 9). Confirmed in the netlist: `Net-(JP500-A)` (JP500.1 + R503.1) and `Dir_Chrg_In` are distinct, and `CHG_BAT` and
`Dir_Chrg_In` are distinct.

## 6. Datasheet facts relied on

**R5460N208AA-TR-FE** — <https://www.nisshinbo-microdevices.co.jp/en/pdf/datasheet/r5460-ea.pdf>

* Pin description (p.4): 1 DOUT, 2 COUT, 3 V− (charger negative input), 4 VC (centre voltage between the two cells), 5 VDD, 6 VSS. Matches the
  brief and the symbol. Absolute maximum VDD 12 V, VC within VSS−0.3 … VDD+0.3.
* Product-code table (Selection Guide, `R5460x208AA` row): VDET1U/VDET1L = **4.250 V/cell** (pack 8.50 V), VREL1 = 4.050 V,
  VDET2U/VDET2L = **2.400 V/cell** (pack 4.80 V), VREL2 = **3.000 V/cell** (pack 6.00 V), VDET3 = **0.200 V** (excess discharge current),
  VDET4 = **−0.200 V** (excess charge current); tVDET1 = 1 s, tVDET2 = 128 ms, tVDET3 = 12 ms, tVDET4 = 8 ms.
* Typical application and **technical notes, p.17**: "R1, R2, C1 and C2 stabilize a supply voltage … A recommended R1, R2 value is **less than
  1 kΩ**. A larger value of R1 and R2 makes the detection voltage shift higher because of some conduction current in the R5460." → the synthetic
  midpoint must be low impedance: 2 × 1.0 k gives 500 Ω Thevenin, +330 Ω (R501) = **830 Ω** at VC, inside the limit. Same page: "C1 and C2 should be
  equal or more than 0.01 µF", "the total value of R1+R3 should be equal or more than 1 kΩ" (here 330 Ω + 1 k = 1.33 kΩ ✓) and "recommendation value
  of R3 is equal or less than 3 kΩ" (here 1 k ✓), and C3 (the cell-negative-to-pack-negative cap, C503 here) ≥ 0.01 µF (0.1 µF fitted ✓).
* Discharge over-current: VDET3 0.200 V across the two IRF7458 in series ≈ 11 A at 2 × ~9 mΩ (consistent with the brief's figure).

**BQ25886 (SLUSD88A)** — <https://www.ti.com/lit/ds/symlink/bq25886.pdf>

* Pin table (§7 / p.5): "VSET … RVSET > 150 kΩ (floating) = **8.4 V**" → VSET left open gives the 8.4 V 2-cell float required here.
* §8.3.9 / §9.2.2.4 "Input Current Limit on ILIM Pin": IINMAX = KILIM / RILIM, **KILIM = 1110 A·Ω** (electrical table). "Input current limit less
  than 500 mA is not supported on ILIM pin. **Do not float this pin**" and "If ILIM pin is open, the input current is limited to zero since ILIM
  voltage floats above 0.8 V." → 750 Ω gives **1.48 A**; the debug board's 383 kΩ gives 2.9 mA, i.e. no charging at all (deviation 2).
* **Figure 20, "BQ25886 Stand-Alone Typical Application Diagram" (p.25)** — the datasheet's own strapping: **ILIM 383 Ω** (= 1110/383 = 2.9 A),
  VSET 150 k, ICHGSET 5.7 k, TS 5.23 k / 30.1 k / 10 k. So `debug_board_v1`'s 383 **k** (and brief §6.4's "ILIM 383 k", which copies it) is a
  **units error of the datasheet's 383 Ω**, not an invented value. This sheet fits 750 Ω rather than the datasheet's 383 Ω so the port suits a
  5 V / 2 A bench supply (2.9 A would demand a 3 A source); see deviation 2. The other three figure-20 values are used as drawn.
* §9.2.2.5: ICHG = RICHGSET / KICHGSET with **KICHGSET = 3810 Ω/A** → 5.7 kΩ = **1.50 A**; pre-charge and termination are ICHG/10.
* Table 3 "Input Current Limit Setting from D+/D− Detection": **USB DCP = 3.0 A** (SDP 500 mA, CDP 1.5 A). D+ shorted to D− at the IC presents a DCP
  to the internal BC1.2 detector; §8.3.9 says the active limit is the lower of the D+/D− result and the ILIM setting → **1.48 A** here.
* **§9.2.2.2 Input (VBUS / PMID) Capacitor** (quoted verbatim from SLUSD88A p.26): "A low ESR ceramic capacitor such as X7R or X5R is preferred
  for input decoupling capacitor and should be placed close to the PMID and GND pins of the IC. Voltage rating of the capacitor must be higher than
  normal input voltage level. **25-V rating or higher capacitor is preferred for up to 5-V input voltage. A minimum 10-μF capacitor is suggested for
  up to 3.3-A input current.** … **For optimal performance, 44-uF cap on PMID is recommended.** In addition, a minimum 1-μF capacitor is suggested at
  VBUS pin." → C510 = 1 µF on VBUS, and **C511 = 22 µF 25 V X5R 1210 (C52306) since the review round** = **19.0 µF at the 5 V PMID bias**
  (§12 item 9; the 10 µF 25 V X5R 0805 it replaced held 6.7 µF there, under the 10 µF the datasheet asks for *after* derating). PMID sits at USB
  VBUS (~5 V) behind Q510 and the input limit is 1.48 A, well under the 3.3 A the 10 µF minimum is quoted for; the 44 µF "optimal performance"
  figure is still not met, but 19 µF is nearly 3 × what the sheet had. This section was **missing from the first revision of this report**, which
  is how a 10 V part (C19702) got onto C511.
* §9.2.2.3 (SYS): "A low ESR ceramic capacitor such as **X7R or X5R** is preferred for SYS decoupling … 16-V rating or higher capacitor is preferred.
  **Minimum 44-μF capacitor is suggested** for up to 2.2-A boost converter output current." → **C513 + C514 + C517 + C518 = 4 × 22 µF 25 V X5R
  1210 (C52306)** since the review round (§12 item 1 / PM ruling R5). The 44 µF is a figure *after* DC-bias derating, so the derating is taken from
  a manufacturer curve rather than a rule of thumb: **KEMET/YAGEO K-SIM**, part `C1210C226K3PAC` (22 µF, 25 V, X5R, 1210 — the same
  capacitance / voltage / dielectric / case as the fitted Samsung CL32A226KAJNNNE), `Capacitance vs. Vbias (DC)` plot, 25 °C:
  **−41.89 % at 8.4 V → 12.78 µF per part**, so **CSYS = 51.1 µF effective ≥ 44 µF** (interpolated between the tool's 8.25 V / −40.85 % and
  8.50 V / −42.59 % points). Ripple from equation (9), ΔVSYS = IOUT·D/(fSW·CSYS) with IOUT = 1.5 A, D = 1 − VBUS/VSYS = 1 − 5/8.4 = 0.405,
  fSW = 1.5 MHz: **7.9 mV** at 51.1 µF. The same tool, same C/V/dielectric, gives the case-size trend that decides the package: 10 µF 25 V X5R at
  8.4 V keeps **−60.0 % in 0805** (C0805C106K3PAC), **−39.0 % in 1206** (C1206C106K3PAC), **−19.1 % in 1210** (C1210C106K3PAC). That is why the
  0805 pair this sheet carried before the review held **under 18 µF**, not the ≈ 24 µF the old note claimed, and why the ruling's first suggestion
  ("add a third 22 µF") in 0805 or 1206 would still have missed 44 µF — three 1206 parts reach at best 3 × 12.8 ≈ 38 µF.
* §8.3.7.4.1 + Figure 18 (TS resistor network, REGN–RT1–TS–RT2/NTC–GND) for 0 … 60 °C with a 103AT: **RT1 = 5.24 kΩ, RT2 = 30.31 kΩ**.
  Thresholds (§7 electrical table, percentage of REGN): VT1 73.25 % (0 °C), VT2 68.25 % (10 °C), VT3 44.75 % (45 °C), VT5 34.375 % (60 °C).
  With R516 5.23 k, R517 30.1 k and R518 10 k (fixed stand-in for the pack's 103AT at 25 °C): V(TS)/V(REGN) = (30.1‖10)/(5.23+30.1‖10) = **58.9 %**,
  between VT3 and VT2 → full ICHG and full VREG. An open TS pin (as on `debug_board_v1`) suspends charging.
* §8.3.7.1: "The STAT output indicates … charging (LOW), charging complete or charge disable (HIGH) or charging fault (Blinking). **If no battery is
  connected, the STAT pin blinks as capacitance connected at BAT charges, discharges, then recharges.**" — expected behaviour on this bench when
  JP510 is open or nothing holds `Dir_Chrg_In`.
* **BAT pin capacitor:** the pin table asks for 10 µF "after derating" on BAT as well. BAT sits at the 8.4 V float, where the same K-SIM curves give
  **4.0 µF for a 10 µF 25 V X5R 0805** (C0805C106K3PAC, −60.0 %). C515 is therefore the same 22 µF 25 V X5R 1210 part as CSYS/CPMID = **12.8 µF at
  8.4 V** (§12 item 9). One BOM line covers C511, C513, C514, C515, C517 and C518 (6 × C52306).
* **CE / OTG:** CE has an internal 900 kΩ pull-down and enables charging when left open (brief §6.4); left open with a `no_connect` here. **OTG has
  no internal pull documented** — the pin table's entry is "Pull low to disable OTG function" — so since the review round **U511 pin 5 is wired to
  `GND`** rather than left floating (§12 item 8). That is also what TI's own EVM jumper selects in charge mode. Exposure was small but real: §8.3.5
  lists five conditions for buck (OTG) operation — BAT above VOTG_BAT, **VBUS *below* VVBUS_PRESENT**, OTG pulled high, TS in range, and a 30 ms
  delay — so a floating OTG that read high could start the boost with the USB cable *unplugged* and a charged pack on `Dir_Chrg_In` through a fitted
  JP510. Even then the 5 V output lands on `CHG_DVIN` and the Q510/U510 ideal-diode stage blocks it from reaching J510, so nothing outside the board
  would have been driven; tying the pin low removes the question. (Verbatim, SLUSD88A pin table, pin 5: *"OTG – USB On-The-Go Enable input. Pull high
  to enable OTG function. Pull low to disable OTG function."* — with no internal pull mentioned, against pin 3's *"internally pulled low with
  900k-Ω resistor"*.)

**LT3652 / FC interaction** (from `tools/baseline/connector_nets.md` and the brief): float 8.38 V set by R71/R74, 120 mV below the R5460 over-charge
trip of 8.50 V; `Dir_Chrg_In` also carries INA219 U16 IN+ and R109 (2 mΩ) to `VBATT_SENSE`.

## 7. Deviations from the brief, and why

1. **No `VBAT_BENCH` net and no PWR_FLAG on it.** §6.4 says "B+ (through nothing) → `Dir_Chrg_In`" *and* "`VBAT_BENCH` power symbol on B+ … PWR_FLAG
   on both". Those cannot both hold: with no series element the B+ terminal *is* `Dir_Chrg_In`, so a `VBAT_BENCH` power symbol there would merge two
   names onto one net — KiCad would rename the FC net, and §4.2 forbids a PWR_FLAG on `Dir_Chrg_In`. I kept the topology (rule 6: nothing in series
   with the flight power path, and the pack's PACK+ really is unswitched) and dropped the name: the B+ node carries only the `Dir_Chrg_In` global
   label, with TP500 on it. `VBAT_BENCH_N` exists as specified, with its PWR_FLAG. The independent verifier confirmed in round 2 that the
   contradiction is real and that **no implementer-side fix exists that does not add a part**, so this is now an explicit
   **PM decision, still open after two fix rounds** — either
   **(a)** strike `VBAT_BENCH` from brief §4.2 and §6.4 and delete `<scratch>/pantry/flatsat_VBAT_BENCH.sexp` (pre-staged and unused) so the
   integrator does not look for it, or
   **(b)** authorise a third `Jumper:Jumper_2_Open` between J500 pin 1 and `Dir_Chrg_In`, after which `VBAT_BENCH` becomes a real, separately
   flagged net with its own PWR_FLAG and "both off" becomes a pure jumper state. (b) does not breach hard rule 6 — the header would be in the new
   bench branch, not in the existing `Dir_Chrg_In ↔ VBATT_SENSE ↔` inhibit chain — but it is a part on a branch of a flight power net and therefore
   a PM / hardware-lead call, not mine. The sheet as delivered implements neither; it keeps the topology and drops the name.
2. **ILIM resistor 750 Ω instead of the brief's 383 kΩ.** 383 kΩ → IINMAX = 1110/383 k = **2.9 mA**, and the datasheet explicitly says limits below
   500 mA are not supported and the pin must not float. **The datasheet's own typical application (SLUSD88A figure 20, p.25) specifies ILIM = 383 Ω
   (2.9 A); `debug_board_v1`'s 383 kΩ — and brief §6.4, which repeats it — is a units error of that value** (added fix round 2; the first two
   revisions of this report attributed the value to the never-assembled debug board without naming the datasheet figure it came from).
   **750 Ω (1.48 A) is fitted instead of the datasheet's 383 Ω (2.9 A) so the port suits a 5 V / 2 A bench supply**; 1.48 A still lets the 1.5 A
   ICHG setting run (the charger works in IINDPM at low battery voltage). If the PM prefers datasheet parity over bench-supply parity, 383 Ω is the
   drop-in alternative and needs a 3 A source. Flagged as a `debug_board_v1` and a brief finding.
3. **TS network uses a third resistor.** The brief says "fit the datasheet's REGN–TS–GND divider so TS sits mid-window". I fitted the datasheet's
   actual network (RT1 5.23 k / RT2 30.1 k) plus R518 = 10 k in the NTC position, which is exactly Figure 18 with the pack's 103AT replaced by its
   25 °C resistance. One extra 0603 buys a network a reviewer can check against the datasheet figure directly.
4. **Two PWR_FLAGs beyond §4.2's list.** `CHG_DVIN` (post-blocking-FET node, feeds U511 VBUS, a `power_in` pin) and the charger switching node
   (U511 SW is also `power_in`, and its neighbours L510/C512 are `unspecified`/`passive`) both need one, or ERC raises `power_pin_not_driven`.
   Neither is a new board rail; both are internal charger nodes.
5. **Charge-status LED (D510 + R519) added.** Not in §6.4's parts list. The brief requires the report to explain the §8.3.7.1 "STAT blinks with no
   battery" behaviour; without an indicator that behaviour is invisible on the bench. Two 0603 parts; remove if the reviewer considers it scope creep.
6. **`Value` of TP500–TP505 and TP510 is hidden** (the net label sits directly under each one) — cosmetic only, the field is still in the netlist.
7. ~~`C511` keeps `debug_board_v1`'s 10 µF 0603 with LCSC C19702.~~ **Withdrawn in fix round 1** — C19702 is a 10 V part; C511 is now
   10 µF 25 V X5R 0805, C15850 (§6, §9.2.2.2).
8. **JP500 sits at the top of the divider (`Dir_Chrg_In` → JP500 → R503), not between the divider midpoint and VC** (fix round 1). Brief §6.4 words it
   as "…connected to the pack's R4 330 Ω + C8 0.1 µF into VC through a jumper header"; with the jumper there, pulling the shunt still leaves
   R503 + R504 (2 kΩ) across B+ and the cell-negative node, so the divider keeps loading `Dir_Chrg_In` and keeps pulling `VBAT_BENCH_N` up when no PSU
   is plugged in. At the divider top the shunt does what the brief wants it to do — remove it and the divider is gone, and the MID screw terminal
   drives VC on its own. The jumper is still on a *branch*, never in series with `Dir_Chrg_In` (hard rule 6).
9. **R505 = 100 k bleed from `VBAT_BENCH_N` to `B-`** (fix round 1, not in §6.4). Without it the cell-negative node has no DC return at all when J500 is
   open; 100 k / 84 µA at 8.4 V gives it a defined potential and changes none of the R5460 thresholds. See §8 open question 3 for what it does and does
   not fix.
10. **CSYS is four 22 µF 25 V X5R 1210 parts, not the brief's "2 × 22 µF 16 V X7R 0805"** (fix round 1 changed the class, the review round the count
    and the case — §12 item 1 / PM ruling R5). 22 µF 16 V X7R does not exist in an 0805 at all; §9.2.2.3 accepts X5R and states its 44 µF *after*
    derating, which needs ~76 µF of nominal 25 V X5R at the 8.4 V SYS bias. Dielectric, case and the measured derating are in each part's
    Description, in the sheet note and in §6.
11. **Reference/Value fields of the rotated symbols (JP500, C503, R505, R519, L510) carry a stored field angle of 90°** so KiCad draws them
    horizontally (`SCH_FIELD::GetDrawRotation()` swaps H/V for a symbol whose transform is rotated 90/270). Without this they render as vertical text
    through their neighbours, which is what the first revision did.

## 8. Assumptions / open questions for the reviewer

1. **Floating bench PSU.** `VBAT_BENCH_N` reaches `GND` only through Q500 → Q501 → `B-` → the ISS-inhibit break (J15/J19 or the pyro_inhibit shunt).
   If the PSU's negative is earthed while the FC ground is earthed (laptop USB, scope), both FETs are bypassed and the replica proves nothing. Noted
   on the sheet; worth an ATP line.
2. **PSU sink capability.** With VSOLAR injected, the LT3652 sources into `Dir_Chrg_In` and will pull a non-sinking supply to its 8.38 V float, 120 mV
   under the R5460 over-charge trip. The sheet note says use a sinking PSU or add a bleed load; no bleed load is fitted (it would be a permanent load
   on `Dir_Chrg_In`).
3. **`VBAT_BENCH_N` state with J500 open, and the divider's quiescent current** (rewritten in fix round 1 — the first version of this entry was
   wrong: it said the 4.2 mA flows "whenever the PSU is on", which is not the governing condition). The governing condition is *the FETs conducting*,
   and with `Dir_Chrg_In` live from a real pack on J14 (D11) or from the LT3652 there are two self-consistent DC states with the PSU unplugged and
   JP500 still shunted: (i) both FETs off, `VBAT_BENCH_N` sits at 8.4 V × 100 k/(100 k + 2 k) ≈ **8.2 V**, so J500 pin 3 — silkscreened "B−" — is near
   pack potential w.r.t. board ground and U500 sees VDD − VSS ≈ 0.16 V, too little to turn the FETs on; (ii) if the FETs are already on (PSU just
   unplugged, or a fast `Dir_Chrg_In` rise held the node down through C503) then `VBAT_BENCH_N` ≈ `B-`, U500 is fully powered, the state latches and
   R503 + R504 draw a permanent **4.2 mA** from `Dir_Chrg_In` to `B-`. **R505 removes the "floating/indeterminate" part** (the node now always has a
   defined potential) but it does **not** remove the bistability — a 100 k bleed cannot overpower a 2 kΩ divider. The operational answer, now on the
   sheet and in the jumper table, is: **pull the JP500 shunt whenever no bench PSU is connected to J500.** With JP500 open there is exactly one state —
   `VBAT_BENCH_N` = `B-` through R505, nothing drawn from `Dir_Chrg_In`, and the R5460 reads cell 1 as over-voltage and holds COUT open, which is
   harmless. Both behaviours are stated in the BENCH PSU WINDOW note. **For the PM/hardware lead:** if an always-safe board is wanted instead of a
   procedure, the alternatives are (a) make JP500 a normally-open header and accept that VC is undefined unless a real MID supply is present, or
   (b) put a 3rd 2-pin header between J500 pin 1 (B+) and `Dir_Chrg_In` — which is a header on a branch of a flight power net and therefore a PM call.
4. **BQ25886 boost topology check.** `debug_board_v1` wires L510 between PMID and SW (5 V in, 8.4 V out = boost), and I copied that. Worth one
   reviewer pass against §9.2 since that board was never built.
5. **J500 pin order** is pin 1 = B+, pin 2 = MID, pin 3 = B−, top to bottom on the sheet. Needs a silkscreen callout at layout.
6. **No on-board fuse on the bench PSU input** — the PSU's own current limit is the protection, matching the brief (which only calls for a fuse on the
   VSOLAR injection sheet). The R5460 over-current trip is at ~11 A, far above a sane bench limit of 2 A.
7. **FC finding (not mine to fix):** `eps_side`'s text note "VSOLAR 9V to 40V" is wrong per brief §6.3 — reported here for completeness because this
   sheet's PSU-window note interacts with the LT3652 float.
8. **PM decision, still open after two fix rounds: `VBAT_BENCH`.** Brief §4.2/§6.4 ask for a `VBAT_BENCH` net with a PWR_FLAG on the B+ terminal
   while also requiring B+ to reach `Dir_Chrg_In` through nothing, and §4.2 bans a PWR_FLAG on `Dir_Chrg_In`; the three cannot hold at once. Either
   strike `VBAT_BENCH` from the brief and delete the pre-staged, unused `<scratch>/pantry/flatsat_VBAT_BENCH.sexp`, or authorise a third
   `Jumper:Jumper_2_Open` between J500 pin 1 and `Dir_Chrg_In` (a part on a branch of a flight power net — not an implementer call, though it does
   not breach hard rule 6). See deviation 1.
9. **Brief §6.4 ILIM value.** "ILIM 383 k" in the brief is a units error inherited from `debug_board_v1`; the datasheet's figure 20 says 383 Ω.
   The sheet fits 750 Ω (1.48 A) for a 5 V / 2 A bench supply — the PM may prefer 383 Ω (2.9 A) for datasheet parity. See deviation 2.

## 9. Validation results (pasted) — re-run after fix round 2

### 9.1 `sch_lint.py`

```
$ python3 tools/sch_lint.py battery_protection_replica.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0 --refdes-block 500-599
battery_protection_replica.kicad_sch: 72 symbol instances, 16 lib symbols, 131 wires, 0 errors, 0 warnings
```

### 9.2 `harness_erc.sh "Battery Replica and Bench Power"` (all six new sheets present on disk)

```
=== ERC delta vs baseline (default: Rev2 + 8 promotions; noise types excluded) ===
sev      type                           base    now  delta
error    pin_not_connected                 5      5     +0
error    power_pin_not_driven              6     12     +6
warning  multiple_net_names               12     12     +0
warning  pin_to_pin                       96    163    +67
warning  same_local_global_label           4      4     +0
warning  single_global_label               9      0     -9
warning  unconnected_wire_endpoint         1      1     +0
total baseline 133, now 197, delta +64
errors: 17

=== violations on sheets matching 'Battery Replica and Bench Power' ===
warning  pin_to_pin                       16
total 16
errors: 0
```

**Errors on this sheet: 0.** Per-sheet breakdown of the 17 project errors from the same `erc.json`
(`pin_not_connected`: 2 on `/`, 3 on `/Power Systems/`; `power_pin_not_driven`: 2 on `/`, 1 on `/Power Systems/`,
2 on `/RP2350AHHHHHHHHH/`, 1 on `/Watchdog Circuit/`, **6 on `/Solar and Sensor Emulation/`**) — 11 are the untouched FC
baseline and the 6 new ones are all on another agent's sheet. The project-wide delta moved between fix round 1
(+5 `power_pin_not_driven`, +68 `pin_to_pin`) and this run (+6 / +67) because the other five sheets changed on disk
between harness runs; nothing attributable to this sheet changed. `single_global_label` is zero because all six new
sheets are on disk.

**Warning triage — all 16 warnings on this sheet are `pin_to_pin`**, the same library-metadata class as the 96 in the FC baseline: every pin of
`flatsat:R5460N208AA`, `easyeda2kicad:DZDH0401DW-7`, `easyeda2kicad:DMP4047LFDE-7` and `easyeda2kicad:SPM6530T-4R7M-HZ` is typed `Unspecified` in the
source libraries, so each one meeting a Passive / Input / Power pin raises a warning. Representative lines:

```
- [warning] pin_to_pin: Pins of type Unspecified and Input are connected      | U500 Pin 1 [DOUT] ; Q500 Pin 4 [G]
- [warning] pin_to_pin: Pins of type Unspecified and Passive are connected    | U500 Pin 4 [VC]   ; R501 Pin 1
- [warning] pin_to_pin: Pins of type Unspecified and Power input are connected| Q510 Pin 1 [D]    ; #PWR505 [VBUS_CHG]
- [warning] pin_to_pin: Pins of type Unspecified and Power output are connected | U510 Pin 4 [SOURCE] ; #FLG502 [pwr]
- [warning] pin_to_pin: Pins of type Unspecified and Unspecified are connected | Q510 Pin 3 [S] ; Q510 Pin 4 [S]
```

Fixing them would mean retyping pins in shared symbols (`flatsat:*` is the integrator's file, `easyeda2kicad:*` is the user's global library).
No `single_global_label`, `multiple_net_names` or `unconnected_wire_endpoint` warning is attributable to this sheet.

### 9.3 Netlist diff vs the post-promotion baseline

Existing FC nets that gained pins (nothing lost, nothing renamed):

```
~ Dir_Chrg_In: +[J500.1, JP500.2, JP510.2, R500.1, TP500.1] -[]
~ B-:          +[C503.2, Q501.1, Q501.2, Q501.3, R502.2, R505.2, TP502.1] -[]   (JP607.1 in the same line is pyro_inhibit's ISS shunt)
~ GND:         +[C510.2, C511.2, C513.2, C514.2, C515.2, C516.2, J510.A1, J510.A12, J510.B1, J510.B12, J510.S1,
                 R510.2, R511.2, R512.2, R513.2, R514.2, R515.2, R517.2, R518.2, U511.19, U511.20, U511.25, U511.4] -[]
```

New nets added by this sheet (sheet-local names shown without the `/Battery Replica and Bench Power/` prefix):

```
VBUS_CHG            J510.A4, J510.A9, J510.B4, J510.B9, Q510.1, R519.2, TP510.1, U510.6
VBAT_BENCH_N        C500.2, C501.2, C502.2, C503.1, J500.3, Q500.1, Q500.2, Q500.3, R504.2, R505.1, TP501.1, U500.6
MID_BENCH           J500.2, R501.2, R503.2, R504.1, TP505.1
DOUT_GATE           Q500.4, TP503.1, U500.1
COUT_GATE           Q501.4, TP504.1, U500.2
CHG_DVIN            C510.1, Q510.3, Q510.4, U510.4, U511.23
CHG_GATE            Q510.2, R512.1, U510.3
CHG_REF             R513.1, U510.2
CHG_SYS             C513.1, C514.1, TP511.1, U511.15, U511.16          (new in fix round 1)
CHG_BAT             C515.1, JP510.1, TP512.1, U511.13, U511.14         (new in fix round 1; open JP510 keeps it off Dir_Chrg_In)
Net-(JP500-A)       JP500.1, R503.1                                     (divider top, isolated by the open jumper symbol)
Net-(U500-VDD)      C500.1, R500.2, U500.5        Net-(U500-VC)  C501.1, R501.1, U500.4
Net-(U500-V-)       C502.1, R502.1, U500.3        Net-(Q500-D-Pad5) Q500.5-8, Q501.5-8   (common drain)
Net-(C511-Pad1)     C511.1, L510.2, U511.21, U511.22                    (PMID)
Net-(C512-Pad1)     C512.1, L510.1, U511.17, U511.18                    (SW)
Net-(U511-BTST) / -ILIM / -ICHGSET / -REGN / -TS / -D+ , Net-(D510-A), Net-(D510-K), Net-(J510-CC1), Net-(J510-CC2)
```

Note that `MID_BENCH` now carries `R503.2` and `R504.1` directly (the divider midpoint *is* the MID node, because JP500 moved to the divider top),
and the isolated stub `Net-(JP500-A)` is what the shunt bridges to `Dir_Chrg_In`.

Components added: 48 (C500–C503, C510–C516, D510, J500, J510, JP500, JP510, L510, Q500, Q501, Q510, R500–R505, R510–R519, TP500–TP505,
TP510–TP512, U500, U510, U511) plus 21 power symbols (#PWR500–#PWR520) and 4 PWR_FLAGs (#FLG500–#FLG503).

Fix round 2 changed placement only: R504 moved 2.54 mm left, the VDD/VC column (R500, C500, C501) 5.08 mm right, and four field/note anchors moved.
The netlist above is unchanged — every net on this sheet has exactly the same pin membership as after round 1 (re-checked pin-by-pin against the
new `harness/netlist.xml`).

Cross-check against `battery_pack_v2`'s netlist: `Net-(U500-VDD)` ≡ pack `/VDD`, `Net-(U500-VC)` ≡ pack `Net-(U1-VC)`, `Net-(U500-V-)` ≡ pack
`Net-(U1-V-)`, `VBAT_BENCH_N` ≡ pack `B-` (cell negative), `B-` ≡ pack `PACK-`, `Dir_Chrg_In` ≡ pack `PACK+` — identical membership, part for part,
with R505 the only addition to the pack's own network.

### 9.4 Readability — checker rewritten in fix round 2

Round 1's checker tested text-vs-text and text-vs-wire only. It had **no page-bounds test and no text-vs-symbol-body test**, which is exactly why
round 1 certified "0 collisions" while the D11 note was drawn outside the A3 frame (its last line off the page entirely) and three strings were drawn
through neighbouring symbol bodies. Both tests were added, and the font metric was corrected:

* `tools/gen/battery_protection_replica_textcheck.py <sheet>.kicad_sch --wires --bodies` builds a bounding box for every visible string (symbol
  Reference/Value, labels, global labels, `(text)` notes) using the KiCad stroke-font metrics, models `SCH_FIELD::GetDrawRotation()` (fields on a
  90/270-rotated symbol render with H and V swapped) and the horizontal-justification flip KiCad applies for symbols rotated 90/180/270 or mirrored
  in y. It now reports, in addition to overlapping pairs and strings drawn across wires:
  * **text vs symbol body** — every graphic primitive (rectangle, circle, polyline, arc) of every `lib_symbols` definition is transformed by each
    instance's rotation/mirror and tested against every string. A field drawn over *another* symbol's outline is a collision; over its own parent's
    outline it is reported as INFO.
  * **page bounds** — every string, wire endpoint, junction, no-connect and symbol-body corner must lie inside the A3 frame
    (`x 13…407`, `y 13…284` with the default 3 mm keep-out for the ruler band inside the 10 mm frame). The bottom ruler band on this page measures
    `y 284.5…287.8` in the export, so anything below `y ≈ 284` is struck by the border.
  * the per-character advance is **0.87 × text size**, measured against the KiCad 10 PDF plot (an 87-character 2.54 mm heading spans 189.3 mm →
    0.834); round 1 used 0.95, which over-reported width by ~14 % and produced two phantom hits.
  * `--region X0 Y0 X1 Y1` lists every item touching a rectangle, which is how the free canvas for the relocated D11 note was found.

  Result on the delivered file:

  ```
  text-on-own-body (INFO)  TP512.Reference  'TP512'   body=(347.22, 107.95, 348.74, 109.47)
  (1 text-over-own-symbol-body items, informational)
  0 collisions, 213 text items, 172 symbol bodies
  ```

* **Ground truth from the rendered PDF.** `kicad-cli sch export pdf` emits a real text layer, so `pdftotext -bbox -f 9 -l 9` gives the exact box of
  every string as plotted, including pin numbers and pin names, which the analytic checker does not model. On page 9 of 11 (`Id: 10/11` = this sheet),
  1525 words: **nothing outside the frame** and **2 overlapping word pairs**, both inside the `easyeda2kicad:DMP4047LFDE-7` symbol itself — pins 3
  and 4 are both named `S` and sit 2.54 mm apart, so KiCad draws `3`/`4` and `S`/`S` on top of each other. That is a library-symbol artefact (the
  same one the ERC reports as `Q510 Pin 3 [S] ; Q510 Pin 4 [S]`), not a placement error, and it is unchanged from round 1.
* The page was also re-read as a 300 dpi render: the whole page plus crops of the five areas touched this round (relocated D11 note, foot of the left
  note column, the R5460 VDD/VC network, the USB-C CC pair, the divider). Every Reference, Value, label and note is legible and inside the border.
* Remaining cosmetic-only item, deliberately left: `TP512`'s Reference is drawn over its own test-point circle (a 1.5 mm outline; the text is fully
  readable). Round 1 also listed `C501`/`0.1uF` as "over its own plates" — that was wrong, it was over **R501's** body, and it is fixed this round.

---

## 10. Fix round 1 (2026-09-14) — verifier findings and what changed

| # | verifier finding | severity | resolution |
|---|---|---|---|
| 1 | ≥6 overlapping-text places; several values illegible; report certified the opposite | major | **Fixed.** Rotated symbols (JP500, C503, R505, R519, L510) now carry a 90° stored field angle so KiCad draws their Reference/Value horizontally; L510's fields moved above the PMID wire and the STAT-LED `VBUS_CHG` PWR_FLAG moved to the USB end of the net; TP511/TP512 Values hidden (as TP500–TP505 already were) and their References moved clear; C500/C501/R501, C513/C514, C515/C516/R516, R515, Q510, J510 and the two block headings re-anchored; the SW-node and `VBAT_BENCH_N` PWR_FLAGs given rot-180 / side-placed Value text so "PWR_FLAG" no longer lands on its own stub. Verified by `text_overlap.py` (0 collisions) **and** by reading the re-exported PDF. §9.4 rewritten. |
| 2 | `VBAT_BENCH_N` has no DC return with the PSU unplugged; indeterminate/bistable; possible permanent 4.2 mA on `Dir_Chrg_In` and ~8.4 V on the J500 "B−" terminal | major | **Fixed as prescribed, with the residual stated.** JP500 moved from the divider midpoint to the divider top (`Dir_Chrg_In` → JP500 → R503), so pulling the shunt genuinely disconnects the divider; R505 = 100 k added from `VBAT_BENCH_N` to `B-` so the node always has a defined potential. Four lines added to the BENCH PSU WINDOW note: J500 pin 3 can sit near pack potential with no PSU fitted, the 4.2 mA flows whenever the FETs conduct (not "when the PSU is on"), and JP500 must be pulled whenever no PSU is connected. Open question 3 rewritten — a 100 k bleed cannot break the bistability against a 2 kΩ divider, so the operating procedure, not the bleed, is what removes state (ii); the two board-level alternatives are put to the PM. |
| 3 | C511 assigned C19702 = 10 V X5R 0603, contrary to §9.2.2.2 | major | **Fixed.** C511 is now 10 µF **25 V** X5R 0805, LCSC **C15850** (Samsung CL21A106KAYNNNE, Basic, stock 6.94 M), footprint `C_0805_2012Metric`. §9.2.2.2 quoted verbatim in §6, including the 25 V preference, the 10 µF minimum for up to 3.3 A and the 44 µF "optimal performance" figure. C515 (CBAT, 8.4 V) got the same part. |
| 4 | Q510/U510 (and L510) carry LCSC numbers from a never-assembled board | minor | **Fixed by the "verified live" route.** New §3.1 records all three checked on 2026-09-14 against the JLC catalogue snapshot *and* the live `getComponentDetail` endpoint, with MFR.Part, package, library type and stock; the parts table now cites that instead of `debug_board_v1`. |
| 5 | C513/C514 specified as "22 µF 16 V X7R", a part class that does not exist in 0805; SYS capacitance short after derating | minor | **Fixed.** Value is now `22uF 25V`, LCSC **C45783** (22 µF 25 V X5R 0805, Basic, stock 4.84 M); §6 quotes §9.2.2.3's "X7R or X5R" and states the derating (≈24 µF effective at 8.4 V) with the resulting ripple, 17 mV from datasheet equation (9) — the justification for not fitting a third capacitor. |
| 6 | TP511/TP512 Values read like net names but the nets were KiCad-auto named | minor | **Fixed.** Local labels `CHG_SYS` (SYS) and `CHG_BAT` (BAT) added; the netlist now shows `/Battery Replica and Bench Power/CHG_SYS` = {C513.1, C514.1, TP511.1, U511.15, U511.16} and `…/CHG_BAT` = {C515.1, JP510.1, TP512.1, U511.13, U511.14}. `CHG_BAT` stays separate from `Dir_Chrg_In` (open JP510), so rule 9 is unaffected. |
| 7 | `VBAT_BENCH` net + PWR_FLAG dropped although the PM pre-staged `flatsat:VBAT_BENCH` — needs a PM ruling | minor | **No sheet change, as the verifier directed.** Deviation 1 stands. The PM must either strike `VBAT_BENCH` from brief §4.2/§6.4 and the pantry, or accept a third 2-pin header between J500 pin 1 and `Dir_Chrg_In`; that header is on a branch of a flight power net, so it is not an implementer call. Listed again under open questions. |

Files touched in this round: `FlatSat_V1/battery_protection_replica.kicad_sch`, `FlatSat_V1/tools/gen/battery_protection_replica_gen.py`,
this report. Nothing else; `jlcpcb/project.db`, `FC_V5e_Production_Rev2/` and the other agents' files were not opened for writing.

---

## 11. Fix round 2 (2026-09-14) — verifier findings and what changed

| # | verifier finding | severity | resolution |
|---|---|---|---|
| 1 | The required D11 text note is drawn outside the A3 frame; its last line is off the page entirely | major | **Fixed.** The three D11 lines were the tail of the left note column at `y 292.16 / 295.97 / 299.78` (A3 is 297 mm tall; the frame border is at `y ≈ 287` and the bottom ruler band measures `284.5…287.8` in the export). They are now their own note block at **`x 205.0, y 224.0 / 227.81 / 231.62`**, in the empty canvas right of the note column and below the BQ25886 block — a `--region 200 212 400 250` scan returns zero items there. The rest of the left column moved up one line pitch (start `y 155.0 → 151.19`) so the SYNTHETIC CELL MIDPOINT block now ends at `y 280.73` instead of `284.54`, clear of the border and the ruler band. Verified in the 300 dpi render of page 9: all three D11 lines print inside the frame, and the `8.4 V, no effect on the protection thresholds…` line no longer touches the border. The checker gained the page-bounds test that would have caught this (§9.4). |
| 2 | ILIM deviation rationale incomplete: the datasheet's own typical application specifies 383 Ω, not 383 k | minor | **Fixed, no schematic change.** SLUSD88A **figure 20 (p.25)** is now quoted in §6 with its full strapping (ILIM 383 Ω = 2.9 A, VSET 150 k, ICHGSET 5.7 k, TS 5.23 k/30.1 k/10 k), and both the sheet note and deviation 2 now say that `debug_board_v1`'s (and the brief's) 383 k is a **units error of that 383 Ω**, and that 750 Ω (1.48 A) is chosen over 383 Ω so the port suits a 5 V / 2 A bench supply. The BQ25886 sheet note grew from 18 to 20 lines (`y 145.0 … 217.39`), which is why the D11 block sits at `y 224` rather than the `216` the verifier suggested. |
| 3 | R511's Reference/Value are drawn through R510's body (third text-over-symbol case, not disclosed) | minor | **Fixed, and two more of the same class found and fixed.** The checker now tests text against transformed symbol-body primitives (§9.4), which found three cross-symbol cases, not one: **R511** Reference/Value at `x 231.14`, in the 3 mm gap between R511 and R510 → moved above the pair to `(225.42, 47.0)` / `(225.42, 49.5)`, centred over R511's column between the VBUS wire (`y 45.72`) and the CC1 wire (`y 50.8`); **C501** Reference/Value (right-justified at `x 139.7`) were drawn through **R501's** body, not their own plates as round 1 claimed → the VDD/VC column (R500, C500, C501) moved 5.08 mm right so C501's fields sit in clear canvas at `x 144.78`; the **`VBAT_BENCH_N`** label on C502's stub reaches back to `x 81.02` and clipped **R504's** body → R504 moved 2.54 mm left to `x 78.74`. Also fixed while there: `#FLG501`'s `PWR_FLAG` value text ran through the second `VBUS_CHG` rail symbol at `(254.0, 44.45)` → moved below-left of the flag, right-justified at `(243.84, 47.0)`; `Q510`'s Value clipped the top-right corner of U510's body → both its fields moved up 1.23 mm. Checker result on the delivered file: **0 collisions**, one informational own-body item (TP512 over its own circle). Netlist unchanged. |
| 4 | `VBAT_BENCH` net and its PWR_FLAG absent; the brief requirement is self-contradictory and needs a PM ruling | minor | **No sheet change — confirmed PM decision.** The verifier independently confirmed the contradiction (§6.4 says "B+ (through nothing) → `Dir_Chrg_In`" *and* "`VBAT_BENCH` power symbol on B+ … PWR_FLAG on both", while §4.2 bans a PWR_FLAG on `Dir_Chrg_In`) and that no implementer-side fix exists without adding a part. Deviation 1 is rewritten with the two options (strike `VBAT_BENCH` from the brief + pantry, or authorise a third `Jumper:Jumper_2_Open` between J500 pin 1 and `Dir_Chrg_In`) and is carried as open question 8. `multiple_net_names` stays at 12, unchanged from baseline. |
| 5 | Report §4 swaps the #FLG501 and #FLG502 assignments | minor | **Fixed, report only.** §4 now reads `VBAT_BENCH_N` (#FLG500, 43.18/90.17), `VBUS_CHG` (#FLG501, 243.84/45.72, U510 DRAIN node), `CHG_DVIN` (#FLG502, 269.24/52.07, U510 SOURCE node), SW node (#FLG503, 340.36/74.93) — matching the PWR_FLAG symbol coordinates in the sheet file and the ERC violation list. |

Files touched in this round: `FlatSat_V1/battery_protection_replica.kicad_sch`, `FlatSat_V1/tools/gen/battery_protection_replica_gen.py`,
`FlatSat_V1/tools/gen/battery_protection_replica_textcheck.py` (new — the extended readability checker), and this report. Nothing else;
`jlcpcb/project.db`, `FC_V5e_Production_Rev2/` and the other agents' files were not opened for writing. Both the sheet and the generator are
written atomically (`.tmp` + `os.replace`).

---

## 12. Review fixes (2026-09-14, Fable review round) — items applied

Chair-dispositioned **fix-now** items assigned to this sheet: **1, 5, 8, 9**. All four applied, to the `.kicad_sch` **and** to
`tools/gen/battery_protection_replica_gen.py`, and the sheet was then regenerated from the generator so the two cannot drift
(the generator reproduced the pre-fix sheet byte-for-byte before the edits, and produced the delivered sheet after them).

| id | item | what changed |
|---|---|---|
| **1** | BQ25886 CSYS ≈ 24 µF effective at 8.4 V vs the 44 µF datasheet minimum (PM ruling **R5** not yet applied) | **Fixed.** CSYS is now **4 × 22 µF 25 V X5R 1210** (C513, C514 re-cased plus new **C517, C518**), LCSC **C52306** / Samsung CL32A226KAJNNNE, footprint `Capacitor_SMD:C_1210_3225Metric`. **51.1 µF effective at 8.4 V**, ΔVSYS = 7.9 mV. Derating from a manufacturer curve, not an estimate — see below. |
| **5** | On-sheet bench-mode table omits "JP500 open" for modes 2 and 3, contradicting the sheet's own PSU-window warning | **Fixed.** The two `Mode` lines now read `JP500 OPEN, JP510 fitted, bench PSU disconnected at J500` and `JP500 OPEN, JP510 open, bench PSU disconnected`; Mode 1 is unchanged (`JP500 fitted`). Sheet text and §5 of this report now read identically. |
| **8** | BQ25886 OTG input left floating on a `no_connect` | **Fixed.** `OTG` removed from the `no_connect` tuple; **U511 pin 5 wired straight to `GND`** (wire `(299.72, 69.85) → (293.37, 69.85) → (293.37, 73.66)`, `#PWR590`). Direct tie rather than the optional 10 k: GND is the one net on this sheet that is unambiguously driven, and TI's EVM selects the same state with JP8 in charge mode. Sheet note now reads "OTG tied low (buck/OTG mode disabled per the SLUSD88A pin table); PG unused". |
| **9** | CBAT (C515) and CPMID (C511) single 10 µF 0805 fall below the "after derating" minimums | **Fixed, with one deviation from the wording of the item.** The item offered "22 µF 25 V X5R **0805** (C45783)"; the vendor curves show that does **not** reach 10 µF at 8.4 V (an 0805 25 V X5R loses 60 % there, so 22 µF → ≈ 8.8 µF). Both capacitors are therefore the **same 22 µF 25 V X5R 1210 (C52306)** as the CSYS bank: **C515 (BAT, 8.4 V) = 12.8 µF**, **C511 (PMID, 5 V) = 19.0 µF**, both over the 10 µF the pin table asks for after derating, and one BOM line now covers all six capacitors. |

### 12.1 The DC-bias source (what the ruling asked for)

R5 and review item 1 both require the derated value to come from a **real manufacturer DC-bias curve**, not the 50–60 % rule of thumb the
old sheet note used. Murata SimSurfing, Samsung's Component Library and TDK's characteristic viewer are all JavaScript front ends and
their per-part curves could not be retrieved here; the curves used are **KEMET/YAGEO K-SIM** (`https://ksim3.kemet.com`, the
manufacturer's own simulator), `Capacitance vs. Vbias (DC)` at 25 °C, exported as CSV from the tool's plot endpoint:

| K-SIM part | C / V / dielectric / case | −% at 5.0 V | −% at 8.4 V | effective at 8.4 V |
|---|---|---|---|---|
| `C1210C226K3PAC` | 22 µF 25 V X5R **1210** | −13.44 % | **−41.89 %** | **12.78 µF** |
| `C1206C106K3PAC` | 10 µF 25 V X5R 1206 | −12.21 % | −39.03 % | 6.10 µF |
| `C0805C106K3PAC` | 10 µF 25 V X5R **0805** | −32.80 % | −59.99 % | 4.00 µF |
| `C1210C106K3PAC` | 10 µF 25 V X5R 1210 | −6.76 % | −19.08 % | 8.09 µF |
| `C1206C226K4PAC` | 22 µF **16 V** X5R 1206 | −50.39 % | −70.47 % | 6.50 µF |

Consequences, in order:

* **The fitted part.** `C1210C226K3PAC` is the same capacitance / voltage / dielectric / case as the Samsung **CL32A226KAJNNNE (C52306)**
  actually fitted (KEMET's own 1210 parts are effectively out of stock at JLCPCB: C1882823 = 0, C696378 = 6). 4 × 12.78 µF = **51.1 µF**,
  a 16 % margin on the 44 µF minimum, which is what covers the part-for-part difference between the two vendors' ceramics.
* **Why not "add a third 22 µF" in the existing 0805** (the ruling's first suggestion): an 0805 at this bias is the worst case in the table
  (−60 % on the 10 µF part), so three 0805 22 µF parts hold ≈ 26 µF — still short. The old note's "roughly 50–60 % … ≈ 24 µF" was optimistic;
  the real figure for the delivered 2 × 22 µF 0805 was **under 18 µF**.
* **Why not 3 × 22 µF 1206** (review item 1's first option): the 10 µF row shows 1206 losing 39 % where 1210 loses 19 %, so a 22 µF 1206 cannot
  beat the 12.78 µF of a 22 µF 1210. Three of them reach at best ≈ 38 µF — under 44 µF.
* **Why not 2 × 47 µF 25 V 1210** (review item 1's second option): no vendor curve is published for a 47 µF 25 V 1210 in any tool reachable
  from here, and a 47 µF part in the same case at the same rating has thinner dielectric layers than the 22 µF one, so it must derate at least
  as hard. Fitting it would have meant guessing exactly the number the ruling asked us to stop guessing.
* **Why not a 16 V part**: the last row. At 8.4 V a 16 V X5R is past half its rating and loses 70 %.

Board area was the trade: four 1210 parts (4 × 8.0 mm²) against two 0805 (2 × 2.0 mm²). This is a bench sheet on a large board, and the SYS
rail already had free canvas to the right of C514, so the four parts sit in a row at `x = 345.44 / 355.60 / 368.30 / 381.00, y = 83.82`.

### 12.2 Other sheet changes forced by the above

* `C511`'s ground stub shortened one grid step (`76.2 → 74.93`) so its `GND` field clears the `CHG_SYS` rail, which now runs on to
  `x = 381.0`. No net change.
* The BQ25886 note block grew by three lines (derating, ripple, the case-size table summary) and therefore starts one line pitch higher
  (`y 145.0 → 141.19`); the **D11 note block moved from `y 224.0` to `y 233.0`** so the two blocks do not touch. Both still sit well inside
  the A3 frame and clear of the title block — `battery_protection_replica_textcheck.py --wires --bodies --page A3` reports **0 collisions**.
* `gnd()` in the generator gained an optional `ref=` argument. The three grounds added this round are pinned to **`#PWR590`–`#PWR592`** so
  that every pre-review ground keeps its `#PWR500`–`#PWR520` number and the netlist diff shows only the parts that really changed.

### 12.3 Validation after the fixes

```
$ python3 tools/sch_lint.py battery_protection_replica.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0 --refdes-block 500-599
battery_protection_replica.kicad_sch: 77 symbol instances, 16 lib symbols, 137 wires, 0 errors, 0 warnings

$ SCRATCH=<scratch>/review_fix_battery_protection_replica tools/harness_erc.sh "Battery Replica and Bench Power"
=== ERC delta vs baseline (default: Rev2 + 8 promotions; noise types excluded) ===
sev      type                           base    now  delta
error    pin_not_connected                 5      5     +0
error    power_pin_not_driven              6      6     +0
warning  multiple_net_names               12     12     +0
warning  pin_to_pin                       96    164    +68
warning  same_local_global_label           4      4     +0
warning  single_global_label               9      0     -9
warning  unconnected_wire_endpoint         1      1     +0
total baseline 133, now 192, delta +59
errors: 11

=== violations on sheets matching 'Battery Replica and Bench Power' ===
warning  pin_to_pin                       16
total 16
errors: 0
```

**Errors on this sheet: 0**, and the project's 11 errors are the untouched Rev2 FC baseline (5 `pin_not_connected` + 6
`power_pin_not_driven`). The 16 warnings on this sheet are the same `Unspecified`-pin `pin_to_pin` noise as before the fixes —
**the same 16 lines, none of them on U511 pin 5**: tying OTG to `GND` added no warning, because `GND` is a driven net.
(The project total moved from 17 errors / 163 `pin_to_pin` in §9.2 to 11 / 164 because other agents fixed `solar_emulation`'s
six `power_pin_not_driven` and touched their own sheets between harness runs; nothing on this sheet contributed.)

Netlist, from the same harness run (`harness/netlist.xml`) — only the intended pins moved:

```
CHG_SYS  -> C513.1, C514.1, C517.1, C518.1, TP511.1, U511.15, U511.16     (was C513.1, C514.1, TP511.1, U511.15, U511.16)
CHG_BAT  -> C515.1, JP510.1, TP512.1, U511.13, U511.14                    (unchanged)
GND      -> … + C517.2, C518.2, U511.5 …                                  (U511.5 = OTG, new)
unconnected-(U511-VSET-Pad6), unconnected-(U511-~{CE}-Pad3), unconnected-(U511-~{PG}-Pad9)
                                                                          (U511 OTG no longer among them)
```

No existing FC net lost a pin, no net was renamed, and `Dir_Chrg_In`, `B-`, `VBAT_BENCH_N`, `MID_BENCH`, `DOUT_GATE`, `COUT_GATE`,
`CHG_DVIN`, `CHG_GATE`, `CHG_REF` and `Net-(JP500-A)` have exactly the membership §9.3 records. Components on this sheet: 50
(was 48; C517 and C518 added), plus 23 power symbols (#PWR500–519 and #PWR590–592) and 4 PWR_FLAGs (#FLG500–503).

Readability, on the delivered file:

```
$ python3 tools/gen/battery_protection_replica_textcheck.py battery_protection_replica.kicad_sch --wires --bodies --page A3
text-on-own-body (INFO)  TP512.Reference  'TP512'     body=(347.22, 107.95, 348.74, 109.47)
0 collisions, 224 text items, 179 symbol bodies

$ python3 tools/gen/geomcheck.py battery_protection_replica.kicad_sch
battery_protection_replica.kicad_sch: 137 wires, 224 text bodies
--- wire-through-text: 3 ---   (the same three as before the fixes: JP500's value, the CHG_DVIN label, the MID_BENCH label)
```

Page 9 of the re-exported project PDF was read at 300 dpi: the four CSYS capacitors sit in a legible row on the `CHG_SYS` rail with
their values readable, the OTG stub and its ground symbol are clear of C510's ground field and of the ILIM wire, C511/C515 read
`22uF 25V`, the bench-mode lines show `JP500 OPEN` for modes 2 and 3, and both note blocks print inside the frame.

**Not applied / out of scope for this sheet:** nothing. **Files touched this round:** `FlatSat_V1/battery_protection_replica.kicad_sch`,
`FlatSat_V1/tools/gen/battery_protection_replica_gen.py`, and this report. `jlcpcb/project.db` was not touched — C52306 still has to be
entered there in the layout-phase supply-chain pass (R12), along with the parts already listed as "needs LCSC".
