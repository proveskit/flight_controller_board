# FC_V5e_Production_Rev2 — JLCPCB Supply-Chain Review

## 1. Data provenance

| Source | Detail |
|---|---|
| **Primary parts DB** | `parts-fts5.db`, **generated 2026-09-13T10:47:30Z** (today), 7,142,068 parts, 5.32 GB |
| How obtained | Read `library.py` → chunked download from `https://bouni.github.io/kicad-jlcpcb-tools/`. Fetched `chunk_num_fts5.txt` (= 11), downloaded `parts-fts5.db.zip.001…011` (3-digit index), concatenated, unzipped — exactly the plugin's own mechanism. **Installed into the KiCad 10 plugin dir** `/Users/ncc-michael/Documents/KiCad/10.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/parts-fts5.db`. The plugin is now refreshed; no fallback was needed. |
| Trend comparison DBs | `current-parts-fts5.db` **2026-04-26** (709 MB, was already in the KiCad 10 dir) and KiCad 9's `parts-fts5.db` **2026-02-11** (5.2 GB) |
| Live cross-check | `https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode=…` (the endpoint in the plugin's `lcsc_api.py`), 12 critical parts queried 2026-09-13. **Live stock agreed exactly with the 2026-09-13 DB** on every part checked (C2692098=0, C2875854=0, C1857514=27, C404816=22, C42411118=9546, C18214056=1372…), so the DB is trustworthy as "today". |
| Refdes → LCSC authority | `jlcpcb/project.db` (254 rows) plus the `LCSC Part` schematic property for **U5**, which is *not* in project.db. |
| Failures | The live endpoint returns no price array (`componentPrices: null`) for these codes — **all prices below come from the 2026-09-13 DB**. No other lookup failed. |

Build quantities assumed: **10 boards** and **50 boards**; qty/board = refdes count per LCSC.

## 2. BOM table (LCSC assignments, 78 distinct parts)

Unit price @10 = the DB price tier covering 10 units. Status key at the bottom.

### Blockers / risky lines

| LCSC | MPN (DB) | Refs | Qty/bd | Stock (2026-09-13) | B/E | $ @10 | Status |
|---|---|---|---|---|---|---|---|
| C2692098 | DF11-4DP-2DSA(24) | J7,J10,J19,J20 | 4 | **0** | Ext | 0.220 | **OUT** — needs 40 / 200 |
| C2875854 | ZDSD04GLGEAG (Zetta SD NAND) | U2 | 1 | **0** | Ext | 16.565 | **OUT** |
| C1857514 | TPS2HB50AQPWPRQ1 | U25 | 1 | **27** | Ext | 1.818 | **LOW** — ok@10, fails@50 |
| C404816 | SPM6530T-3R3M-HZ | L4 | 1 | **22** | Ext | 0.283 | **LOW** — ok@10, fails@50 |
| C3304278 | RV-3028-C7-32.768KHZ-1PPM-TA-**QA** | IC3 | 1 | **13** | Ext | 2.565 | **LOW + MISMATCH** (schematic says **QC**) |
| C185323 | RC0603FR-0752K3L (52.3k) | R42 | 1 | **11** | Ext | 0.003 | **LOW** — ok@10, fails@50 |
| C33503485 | **TLV1824DR, SOIC-14** | U1 | 1 | 136 | Ext | 1.507 | **MISMATCH** — symbol is `TLV1704AIPWR`, footprint TSSOP-14 |
| C555460 | **TPS54225PWPR** | U10 | 1 | 607 | Ext | 0.552 | **MISMATCH** — schematic value says TPS54226 |
| C597838 | DF11CZ-4DP-2V(27) | J23 | 1 | 134 | Ext | 0.863 | LOW-ish (ok@10 & @50, thin) |
| C411292 | E22-400M30S | U13 | 1 | 210 | Ext | 6.551 | WATCH |
| C411312 | E28-2G4M27S | U30 | 1 | 490 | Ext | 6.785 | WATCH |
| C485918 | TPS4H160AQPWPRQ1 | U6 | 1 | 630 | Ext | 1.968 | WATCH |
| C580306 | LT8610ABEMSE#TRPBF | U12 | 1 | 984 | Ext | 5.268 | WATCH (sole viable SKU) |
| C2128 | **1N4148WS** | D7 | 1 | 1,770,049 | Basic | 0.016 | MISMATCH-minor (schematic: 1N4151WS) |
| C92124 | PMR18EZPFV2L00, **1206** | R108,R109 | 2 | 4,571 | Ext | 0.232 | Footprint is 1210 land — check |
| C18214056 | APS1604M-3SQR-SN | **U5** | 1 | 1,372 | Ext | 2.825 | **MISSING from project.db** |

### Remaining lines (all OK)

| LCSC | MPN | Qty/bd | Stock | B/E | $ @10 |
|---|---|---|---|---|---|
| C1525 | CL05B104KO5NNNC 100nF 0402 | 35 | 33,327,481 | Basic | 0.004 |
| C25900 | 0402WGF4701TCE 4.7k | 25 | 18,365,039 | Basic | 0.003 |
| C25804 | 0603WAF1002T5E 10k | 20 | 26,967,989 | Basic | 0.003 |
| C25803 | 0603WAF1003T5E 100k | 20 | 23,829,690 | Basic | 0.004 |
| C19702 | CL10A106KP8NNNC 10µF 0603 | 11 | 13,909,324 | Basic | 0.032 |
| C21190 | 0603WAF1001T5E 1k | 8 | 26,034,969 | Basic | 0.003 |
| C25819 | 0603WAF4702T5E 47k | 7 | 2,543,020 | Basic | 0.004 |
| C1511768 | AP22653AW6-7 | 7 | 9,131 | Ext | 0.207 |
| C563981 | MOLEX 5040500691 Pico-Lock 1x06 | 6 | 2,222 | Ext | 0.425 |
| C16772 | CL05B224KO5NNNC 220nF | 5 | 3,083,972 | Basic | 0.006 |
| C23733 | CL05A475MP5NRNC 4.7µF 0402 | 4 | 3,271,433 | Basic | 0.019 |
| C5119943 | MOLEX 5040500291 Pico-Lock 1x02 | 4 | 17,500 | Ext | 0.211 |
| C22809 | 0603WAF1502T5E 15k | 4 | 5,202,966 | Basic | 0.003 |
| C90143 | EMK325ABJ107MM-P 100µF 1210 | 3 | 54,053 | Ext | 0.771 |
| C15849 | CL10A105KB8NNNC 1µF | 3 | 8,129,560 | Basic | 0.021 |
| C2290 | KT-0603W LED | 3 | 1,158,040 | Basic | 0.012 |
| C110493 | DFLS130L-7 | 3 | 4,517 | Ext | 0.431 |
| C506658 | DF11-12DP-2DSA(08) | 3 | 9,396 | Ext | 0.229 |
| C4211 | 0603WAF3001T5E 3.0k | 3 | 8,967,010 | Basic | 0.003 |
| C59461 | CL10A226MQ8NRNC 22µF | 2 | 9,999,859 | Basic | 0.031 |
| C1548 | 0402CG150J500NT 15pF | 2 | 1,676,236 | Basic | 0.004 |
| C177235 | MOLEX 5040500491 Pico-Lock 1x04 | 2 | 14,327 | Ext | 0.325 |
| C23186 | 0603WAF5101T5E 5.1k | 2 | 23,480,095 | Basic | 0.002 |
| C25092 | 0402WGF220JTCE 22R | 2 | 6,703,051 | Basic | 0.003 |
| C72443 | C&K KMR221GLFS | 2 | 9,073 | Ext | 0.535 |
| C87469 | INA219AIDCNR | 2 | 4,670 | Ext | 0.929 |
| C964818 | MY-1220-03 coin holder | 1 | 9,848 | Ext | 0.099 |
| C32949 | CL05C100JB5NNNC 10pF | 1 | 1,332,271 | Basic | 0.006 |
| C1613 | CL10B332KB8NNNC 3.3nF | 1 | 320,697 | Basic | 0.008 |
| C15195 | CL05B103KB5NNNC 10nF | 1 | 5,949,302 | Basic | 0.005 |
| C15850 | CL21A106KAYNNNE 10µF 0805 | 1 | 7,037,778 | Basic | 0.084 |
| C84494 | GRM32ER71A476KE15L 47µF | 1 | 34,773 | Ext | 0.555 |
| C48192 | NSR0320MW2T1G | 1 | 24,605 | Ext | 0.125 |
| C12624 | KT-0603G green LED | 1 | 112,726 | Ext | 0.012 |
| C671115 | LT3652IMSE#TRPBF | 1 | 2,980 | Ext | 7.527 |
| C165948 | TYPE-C-31-M-12 | 1 | 243,870 | Ext | 0.186 |
| C160389 | JST BM03B-SRSS-TB | 1 | 37,157 | Ext | 0.275 |
| C160390 | JST BM04B-SRSS-TB | 1 | 71,154 | Ext | 0.253 |
| C112288 | SPM6530T-100M | 1 | 5,923 | Ext | 0.226 |
| C42411119 | AOTA-B201610S3R3-101-T 3.3µH | 1 | 13,543 | Ext | 0.283 |
| C360729 | SPM6530T-4R7M-HZ | 1 | 1,852 | Ext | 0.326 |
| C25744 | 0402WGF1002TCE 10k | 1 | 29,737,515 | Basic | 0.003 |
| C861248 | RT0603BRD07243KL 243k 0.1% | 1 | 1,746 | Ext | 0.035 |
| C18335 | 0603WAJ0475T5E 4.7M | 1 | 13,177 | Ext | 0.002 |
| C14890 | 0603WAF7322T5E 73.2k | 1 | 32,272 | Ext | 0.003 |
| C137768 | RC0603FR-0722K1L 22.1k | 1 | 93,299 | Ext | 0.005 |
| C22935 | 0603WAF1004T5E 1M | 1 | 7,762,450 | Basic | 0.002 |
| C861602 | RT0603BRD0794K2L 94k 0.1% | 1 | 10,000 | Ext | 0.036 |
| C2999499 | FRC0603F6343TS 634k | 1 | 10,983 | Ext | 0.002 |
| C23050 | 0603WAF4123T5E 412k | 1 | 8,081 | Ext | 0.002 |
| C81248 | 25121WF120LT4E 0.12R 2512 | 1 | 4,753 | Ext | 0.044 |
| C17168 | 0402WGF0000TCE 0R | 1 | 12,093,991 | Basic | 0.003 |
| C11702 | 0402WGF1001TCE 1k | 1 | 12,881,369 | Basic | 0.002 |
| C25105 | 0402WGF330JTCE 33R | 1 | 2,162,502 | Basic | 0.004 |
| C530664 | KH-MMCX-Z | 1 | 1,921 | Ext | 0.588 |
| C97521 | W25Q128JVSIQ | 1 | 82,786 | **Basic** | 2.261 |
| C919695 | LIS2MDLTR | 1 | 9,916 | Ext | 4.671 |
| C42411118 | **RP2350A** QFN-60 | 1 | 9,546 | Ext | 1.201 |
| C130026 | TCA9548APWR | 1 | 46,746 | Ext | 0.700 |
| C2655100 | LSM6DSOTR | 1 | 1,770 | Ext | 3.677 |
| C558584 | MCP23017T-E/SS | 1 | 6,171 | Ext | 1.380 |
| C20625731 | ABM8-272-T3 | 1 | 23,494 | Ext | 0.509 |

Status key: OK = stock ≥ 10× the 50-board need; WATCH = covers 50 boards but <10× margin; LOW = covers 10 but not 50; OUT = 0 stock; MISMATCH = DB part ≠ schematic intent; MISSING = no LCSC in the authoritative mapping.

**Note on "Preferred":** the published `parts-fts5.db` only carries `Library Type` ∈ {Basic, Extended}; the preferred flag is only populated in the `basic-preferred`/`current-parts` variants. Only **2 lines in the whole BOM are Basic and non-passive**: C97521 (W25Q128JVSIQ) and C2128. Everything else active is Extended.

## 3. Lines with no LCSC assignment

| Ref | Value | Judgement |
|---|---|---|
| **C10** | 100nF 0402 | **GAP — Rev2 regression.** This is U5's decoupling cap, placed on the PCB, present in the netlist, and has **no LCSC**. It will be omitted from the JLC BOM. Assign **C1525** (the same 100nF 0402 used by the other 35 caps). |
| **U5** | APS1604M-3SQR-SN | **GAP — Rev2 regression.** The symbol carries `LCSC Part = C18214056`, but `project.db` (what the plugin actually exports) has **no U5 row at all**. The plugin BOM/CPL is driven by project.db, so the PSRAM will be **unassembled** unless you open the plugin and assign C18214056 to U5. Stock 1,372 today, $2.825@10 — the part itself is fine. |
| R9 | "DNF" | Intentional (Do Not Fit). Confirm `exclude_from_bom` is set — it currently is **0**, so it will appear in the BOM with an empty LCSC. Harmless but noisy; better to mark it DNP. |
| J3 (1x06 THT header "Life Makes Lemonade"), J4 (1x02 THT) | Intentional — THT headers, excluded from BOM and POS. |
| JP6 solder jumper, H1/H2 mounting holes, TP2/TP5/TP6/TP8 test points, G***/REF** graphics | Intentional, all `exclude_from_bom=1`. |

Everything else that is *not* JLC-assemblable (radio modules, MMCX, coin cell holder, DF11/Picolock/SRSS connectors) **is** LCSC-assigned and will be placed by JLC — that is intentional and consistent with Rev1's as-ordered BOM.

## 4. Risk register (prioritized)

### P0 — hard blockers, will stop the order

**1. J7 / J10 / J19 / J20 — Hirose DF11-4DP-2DSA(24), C2692098 — STOCK 0.**
Evidence: 2026-02-11 DB: **2**. 2026-04-26 DB: **2**. 2026-09-13 DB and live JLCPCB API: **0**. Stuck at 2 for seven months, then zeroed — classic end-of-life tail. 4 per board = 40 / 200 needed. This part alone blocks the build.
*Mitigation (same 2 mm DF11 4-pos family, same footprint):*
- **C7427056** DF11-4DP-2DS(52) — **5,022** in stock. Best choice.
- **C506665** DF11-4DP-2DSA(08) — **1,328**. `(08)` vs `(24)` is the plating/packaging suffix only, mechanically identical.
- **C202087** DF11-4DP-2DS(24) — **1,065**.
Verify the suffix's plating and tray/tube packaging against your DF11 mating half before committing.

**2. U2 — Zetta ZDSD04GLGEAG SD NAND, C2875854 — STOCK 0.**
Evidence: 2026-02-11: **497**. 2026-04-26: **192**. 2026-09-13 + live: **0**. Sibling `ZDSD04GLGIAG` (C5349318) went 754 → **0** as well. The whole Zetta SD-NAND line is dead at JLC; Zetta's remaining stocked parts are only EEPROM/NOR. Treat as **discontinued**.
*Mitigation (LGA-8 6×8 SD NAND, same de-facto SDIO pinout — **verify pin 1–8 against the datasheet before ordering**):*
- **C2838632** CSNP1GCR01-AOW (Creat Storage World, 1 Gb) — **2,160**.
- **C2691593** CSNP1GCR01-BOW — **672**.
- **C2841139** CSNP32GCR01-AOW (32 Gb, LGA-8 6.2×8 — slightly larger body, check courtyard) — **973**.
Capacity changes from 4 Gb to 1 Gb on the direct-footprint options; if 512 MB of storage is a requirement, the 32 Gb part with a footprint check is the better path.

### P1 — wrong part assigned (would ship a board that doesn't work)

**3. U1 — schematic symbol `oresat-ics:TLV1704AIPWR`, footprint `TSSOP-14`, but LCSC C33503485 = TI **TLV1824DR**, package **SOIC-14**.**
Two independent errors: wrong device (TLV1824 is a different comparator family) and wrong package (SOIC-14 body will not sit on a TSSOP-14 land pattern). This is a **build-stopper disguised as an in-stock line**.
*Fix:* **C181596 TLV1704AIPWR, TSSOP-14, stock 155, $1.634@10** — exactly the symbol's part. (Automotive grade **C702103 TLV1704AQPWRQ1**, TSSOP-14, stock **31**, $5.814@10, if Q1 is wanted — but 31 pcs will not cover 50 boards.) Note 155 pcs covers 10 and 50 boards but is thin: **lifetime-buy candidate**.

**4. IC3 — schematic value `RV-3028-C7_32.768kHz_1ppm_TA_QC` but LCSC C3304278 = `…TA-QA`.**
Wrong accuracy grade **and** collapsing stock: 2026-02-11: **179** → 2026-04-26: **2,195** → 2026-09-13: **13**. The QC part you actually specified, **C3019759**, is **0 stock today** (it was 30,219 in February — a catastrophic drop across the whole Micro Crystal RV-3028 line at JLC).
*Mitigation:* neither grade covers a 50-board build; QA covers 10 boards only, at the wrong spec. Decide the grade deliberately, then either buy the 13 remaining QA units now, or plan to **consign** RV-3028-C7 from a distributor (Digi-Key/Mouser stock Micro Crystal normally) rather than relying on JLC. **Flag as the single highest long-lead risk after the two P0s.**

**5. U10 — value string says `TPS54226PWP…`, LCSC C555460 = **TPS54225PWPR**.**
Not necessarily an error — **TPS54226PWPR (C72066) has been 0 stock since at least February** and TPS54226PWP (C1356054) is 0 too, so someone substituted. But TPS54225 and TPS54226 differ in switching frequency (TPS54225 ≈ 500 kHz vs TPS54226 ≈ 1.2 MHz), which changes the required inductor and compensation. **Confirm L/C around U10 were re-sized for the '25**, and update the schematic value so the BOM is self-consistent. Stock 607, adequate for both builds. No stocked TPS54226 exists in HTSSOP-14 at JLC.

**6. D7 — value `1N4151WS`, MPN field `1N4151WS-E3-08`, but C2128 = **1N4148WS** (Jiangsu Changjing).**
Electrically near-identical small-signal diode, same SOD-323, Basic part, 1.77 M in stock. Almost certainly a deliberate jellybean substitution — but the BOM should say so. Low risk; fix the value string.

**7. R108/R109 — PMR18EZPFV2L00 is a **1206** part on a **1210** land pattern (`LED_1210_3225Metric`).**
It will place and solder (same 3.2 mm length, narrower 1.6 mm body vs 2.5 mm pads), but the paste/pad ratio is off and the footprint name suggests it was copied from an LED. Verify before a 50-board run. Stock 4,571 — supply is fine.

### P2 — quantity-limited (10 boards fine, 50 boards not)

| Part | Stock | Need @10 / @50 | Notes / alternate |
|---|---|---|---|
| **U25 TPS2HB50AQPWPRQ1** (C1857514) | **27** | 10 / 50 | Was 523 in Feb, 238 in Apr, **27** now — steep decline on an automotive Q1 high-side switch. Only sibling **C1857515 TPS2HB50BQPWPRQ1** has **15** (B = different current-limit/diag variant, *not* a drop-in without checking CL/SNS). **Lifetime-buy candidate — buy the 27 now if you intend 50 boards.** |
| **L4 SPM6530T-3R3M-HZ** (C404816) | **22** | 10 / 50 | Feb 897 → Apr 502 → **22**. The -HZ (high-current) suffix is the scarce one. **C76856 SPM6530T-3R3M — 2,775 in stock**, identical 7.1×6.5 mm footprint, same 3.3 µH; lower saturation current than -HZ, so check your peak inductor current before swapping. |
| **IC3 RV-3028** | 13 | 10 / 50 | See P1 #4. |
| **R42 52.3k** (C185323, RC0603FR-0752K3L) | **11** | 10 / 50 | Was 27,929 in April. Trivial to replace: **C23198 0603WAF5232T5E — 87,042 in stock**, 1% 0603, $0.003. |
| **U1 TLV1704AIPWR** (C181596, after the P1 fix) | 155 | 10 / 50 | Covers both, no margin. Lifetime-buy candidate. |
| **J23 DF11CZ-4DP-2V(27)** (C597838) | **134** | 10 / 50 | Feb 95 → Apr 165 → 134. Sole SKU — **no alternate exists** at JLC for the SMD DF11CZ 4-pos. Covers 50 boards with ~2.7× margin; a single competing order could wipe it. |

### P3 — watch list (covers 50 boards, thin margin or single-source)

- **U13 E22-400M30S** (C411292, **210**) and **U30 E28-2G4M27S** (C411312, **490**) — Ebyte modules, single-source, 6–7 USD each, historically volatile (E28 was **97** in April, **94** in February). 50 boards = 50 each; fine today. E28 alternates exist in the family (E28-2G4M20SX etc.) but all differ in RF power **and body size**, so none is a footprint drop-in. Order the modules first; they gate everything else.
- **U6 TPS4H160AQPWPRQ1** (C485918, **630**, down from 3,071 in Feb). Drop-in: **C471053 TPS4H160BQPWPRQ1, 3,912 in stock** — the B variant differs only in current-limit/diagnostic behaviour; check `TPS4H160A` vs `B` datasheet table before swapping.
- **U12 LT8610ABEMSE#TRPBF** (C580306, **984**, down from 1,806 in Feb). Of the ~70 LT8610 SKUs in the catalog, **this is the only one with meaningful stock** — every other grade is 0–23 pcs. Single point of failure on an ADI/Linear part with long factory lead times. **Lifetime-buy candidate.**
- **IC6 LT3652IMSE#TRPBF** (C671115, **2,980**) — healthy now, but the same "one SKU alive, all siblings at 0" pattern (LT3652IMSE#PBF C194712 = 0). Watch.
- **U7 LSM6DSOTR** (C2655100, **1,770**) — ST is steering new designs to LSM6DSO**32**/DSV; LSM6DSO itself is still in production. Fine for both builds.
- **U18 RP2350A** (C42411118, **9,546**) — **correct variant confirmed**: QFN-60, `RP2350A`, Raspberry Pi. Healthy.
- **U11 W25Q128JVSIQ** (C97521, **82,786**, **Basic**) — the safest IC on the board.
- **RF1 KH-MMCX-Z** (C530664, **1,921**, down from 3,660 in Feb) — Kinghelm, plentiful family (KH-MMCX-PBS C910124 etc. if needed).
- **BT1 MY-1220-03** (C964818, **9,848**) — fine; MY-1220-03-R / -01 available as backups.
- **J1/J2/J6/J9/J11/J13 Molex 5040500691** (C563981, **2,222**, was 9,361 in project.db snapshot) — 6/board → 300 for 50 boards. Margin ~7×; watch, no action.
- **D12/D13/D15 DFLS130L-7** (C110493, **4,517**, was 13,268 in April) — declining but ample.
- **U8/U16 INA219AIDCNR** (C87469, **4,670**, was 19,798) — declining but ample. TI has **not** marked INA219 NRND; it remains active.

### P4 — no action
All 30 Basic passives (0402/0603 resistors and MLCCs, LEDs, 1N4148WS) have 10⁵–10⁷ stock, multi-sourced, and cost <$0.04. Zero risk. No setup-fee exposure on these.

**Extended-part setup fees:** ~48 distinct Extended lines. At JLC's per-unique-Extended-part fee this is a fixed cost that hits a 10-board run much harder per board than a 50-board run — worth knowing but not a supply risk.

## 5. Summary

**Can Rev2 be assembled today at JLC?**

- **10 boards: NO — not as the BOM stands.** Two lines are at literally zero stock (C2692098 ×4/board, C2875854), one line (U1) points at the wrong device in the wrong package, and two Rev2 additions (U5, C10) have no LCSC in the plugin database and would be left off the board — meaning you'd receive 10 boards with no PSRAM, no SD NAND, no inhibit connectors, and a comparator that doesn't fit. Every one of these is fixable in an afternoon; **after the fixes below, 10 boards is comfortably buildable.**
- **50 boards: NO, and harder.** On top of the above, six lines cannot cover 50 pcs today: TPS2HB50AQPWPRQ1 (27), SPM6530T-3R3M-HZ (22), RV-3028 QA (13) / QC (0), RC0603FR-0752K3L (11). Three have easy drop-ins; **the RTC is the one with no good JLC answer and should be consigned or bought outside JLC.**

**Designer checklist before ordering:**

1. **Assign U5 → C18214056 and C10 → C1525 in the JLCPCB Tools plugin** (project.db), not just in the schematic. Re-export BOM/CPL and confirm U5 and C10 appear.
2. **Re-assign J7/J10/J19/J20** from C2692098 to **C7427056** (5,022 in stock), after checking the `(52)` suffix against your mating connector.
3. **Re-assign U2** from C2875854 to **C2838632** (or C2841139 for 32 Gb), after verifying the LGA-8 pinout and body size.
4. **Re-assign U1** from C33503485 to **C181596 (TLV1704AIPWR, TSSOP-14)** — this is a wrong-part bug, not a stock issue.
5. **Decide the RV-3028 grade (QA vs QC)** and source it outside JLC, or accept the 13 QA units for a 10-board run only.
6. **Re-assign R42** to **C23198** (87k stock) — free win.
7. **If building 50:** swap L4 to **C76856** (verify saturation current), swap U6 to **C471053** if the B variant is acceptable, and **place a lifetime buy on TPS2HB50AQPWPRQ1 (27), TLV1704AIPWR (155) and LT8610ABEMSE#TRPBF (984)** — all three are single-SKU-alive ICs with declining curves.
8. **Confirm the U10 TPS54225-vs-TPS54226 substitution** was intentional and that the switching-frequency-dependent passives were re-sized; then fix the schematic value string.
9. Fix the cosmetic value mismatches (D7 → 1N4148WS) and mark **R9 DNF** as excluded from BOM.
10. Check the **R108/R109 1206-part-on-1210-land** footprint before a 50-board run.
11. Order the **Ebyte modules first** (210 / 490 in stock, single-source, long lead) — they are the schedule driver.
