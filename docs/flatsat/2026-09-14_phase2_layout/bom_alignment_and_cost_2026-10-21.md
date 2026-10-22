# FlatSat V1 BOM alignment and JLCPCB cost estimate (2026-10-21)

Board `FlatSat_V1` at `a544052`. Live JLC data pulled 2026-10-21. Read-only pass: no `project.db`, schematic, or board writes.

## Verdict

| Question | Answer |
|---|---|
| Aligned? | **No.** 2 parts cannot be assembled at JLC today, and `project.db` was never re-synced after the review fixes. |
| Schematic vs board vs `project.db` value/footprint mismatches | 0 |
| Placed refs with an orderable LCSC | 436 of 472 |
| Unique LCSC codes | 117 (81 Extended, 36 Basic, 0 confirmed preferred-extended) |
| qty 2 assembled (of 5 fabricated) | **~$590 to $615 per order, ~$295 to $310 per board** |
| qty 5 assembled | **~$940 to $965 per order, ~$190 per board** |

### Blocking mismatches

| # | Refs | LCSC | Part | Problem (live 2026-10-21) | Fix options |
|---|---|---|---|---|---|
| B1 | IC3 | C3304278 | RV-3028-C7 RTC (heritage) | JLC stock **0** | JLC pre-order / global sourcing (pre-order min 5), or consign. Buy first (CLAUDE.md step 7). |
| B2 | L3, L200 | C42411119 | AOTA-B201610S3R3-101-T 3.3 µH 2016 | JLC stock **1**; need 2/board + 1 attrition (5 for qty 2, 11 for qty 5) | Pre-order (min 32) or swap L200 and L3 to a stocked 3.3 µH 2016 part. L3 is heritage, so a swap needs a datasheet check. |
| B3 | 218 refs | n/a | All Phase-1/2 refs, including every review-fix ref | Missing from `jlcpcb/project.db` (258 rows, last commit `d56c9df` 2026-09-14) | GUI step (CLAUDE.md procedure step 6). Opening JLCPCB Tools adds the rows from the board `LCSC Part` fields, which match the schematic for all 218. Afterwards, confirm the LCSC column. |

### Non-blocking findings

| Refs | Finding | Effect on the order |
|---|---|---|
| U1 | Schematic field `C33503485` = TLV1824DR **SOIC-14** (wrong package for the TSSOP-14 footprint, stock 127). `project.db` has `C181596` TLV1704AIPWR TSSOP-14 (stock 568). | `project.db` wins for this heritage ref, so the order is correct. If the row is ever cleared, the schematic field would reintroduce a wrong part. Fix the schematic field. |
| R42 | Schematic field `C185323` RC0603FR-0752K3L (stock **9**). `project.db` has `C227953` AC0603FR-0752K3L (stock 39,588). | `project.db` wins, so the order is correct. Fix the schematic field. |
| R26, R27 | `in_bom no` in the schematic, but the board footprint is not BOM-excluded and `project.db` has C23186. | Ordered. Rev2 BOM orders them the same way (heritage convention). |
| R108, R109 | C92124 PMR18EZPFV2L00 is a **1206** part on `LED_1210_3225Metric` | Heritage (flown) footprint. Info only. |
| U22, U27, U29 | `SOT26` footprints carry the through-hole attribute (U19 and the others are SMD) | Plugin CPL ignores the attribute. A `kicad-cli --smd-only` export would drop them. |
| SW1, SW2, SW701, SW702 | KMR2 footprints have no SMD/THT attribute | Same as above. |
| J300, JP400/401, JP500/510, JP600–607 | PLM-08 **not done**: 13 identical 1×02 2.54 mm headers are still split across C492401 (3), C358684 (2), C124375 (8) | Collapsing to C492401 removes 2 feeder fees (about $3). |
| C701 | C2182156 (Ext 10 µF 0805) while C214/C75 use C15850 (Basic 10 µF 0805) | One avoidable feeder fee, unless C701 needs the different rating. |
| Tooling | `parts-fts5.db` absent: the Bouni plugin is not installed under `~/Documents/KiCad/10.0/3rdparty/plugins/` | All 117 codes were checked live instead (see Sources). |

### Refs with no LCSC anywhere (36, none ordered)

| Refs | Why it's acceptable |
|---|---|
| TP200–203, TP300–306, TP400–402, TP500–505, TP510–512, TP600–603, TP701 (28) | Bare 1.5 mm test pads, no part by design |
| TP2, TP5, TP6, TP8 | Heritage THT loop test points, not ordered on Rev2 either. Hand-solder if wanted. |
| J3 (1×06), J4 (1×02) | Heritage headers, `project.db` lcsc null. Hand-solder. J4 shunt is removed on flight units. |
| JP6 | Solder jumper. Bridge by hand (CLAUDE.md rule 7). |
| R9 | Value `DNF`, `project.db` lcsc null |

### Since the 2026-09-14 pass

| Item | 2026-09-14 | 2026-10-21 (live) |
|---|---|---|
| SW600 | No LCSC | C431540 MSK12C02, stock 195,614 |
| Q500, Q501 IRF7458 (C10879) | Stock 57 | **Stock 24** (12 boards' worth). Buy at order time. |
| U6 TPS4H160AQPWPRQ1 (C485918) | n/a | Stock **16** (16 boards) |
| IC3 RV-3028 (C3304278) | n/a | **Stock 0** (B1) |
| L3/L200 (C42411119) | n/a | **Stock 1** (B2) |
| Review-fix refs C513, L510, C512, C215, C218, J510, U511 | n/a | All on the board with LCSC fields: C52306, C87572, C1622, C23733, C1525, C165948, C2765094 |
| TP512, FID1, FID2 | n/a | No part (pad, board-only fiducials) |

### Unique Extended parts (81)

C10879 IRF7458TRPBF, C110493 DFLS130L-7, C112288 SPM6530T-100M, C124375 B-2100S02P-A110, C12624 KT-0603G, C130025 TCA4311ADGKR, C130026 TCA9548APWR, C137768 RC0603FR-0722K1L, C14890 0603WAF7322T5E, C1511768 AP22653AW6-7, C160389 BM03B-SRSS-TB(LF)(SN), C160390 BM04B-SRSS-TB(LF)(SN), C165948 TYPE-C-31-M-12, C17429783 1N4151WS-E3-18, C177235 5040500491, C181596 TLV1704AIPWR, C18214056 APS1604M-3SQR-SN, C18335 0603WAJ0475T5E, C1857514 TPS2HB50AQPWPRQ1, C20625731 ABM8-272-T3, C207086 2920L185DR, C2182156 EMK212BB7106KG-T, C227953 AC0603FR-0752K3L, C23000 0603WAF3012T5E, C23050 0603WAF4123T5E, C23068 0603WAF5231T5E, C23188 0603WAF5621T5E, C23241 0603WAF7500T5E, C259714 R5460N208AA-TR-FE, C2655100 LSM6DSOTR, C2765094 BQ25886RGER, C2875853 ZDSD02GLGEAG, C2886093 CDBA240LL-HF, C2887259 SS12D10G4 071, C28927 TMP112AIDRLR, C2999499 FRC0603F6343TS, C3235552 DZDH0401DW-7, C3304278 RV-3028-C7-32.768KHZ-1PPM-TA-QA, C358684 MTP125-1102S1, C360729 SPM6530T-4R7M-HZ, C3678616 VEML6031X00, C404816 SPM6530T-3R3M-HZ, C411292 E22-400M30S, C411312 E28-2G4M27S, C42411118 RP2350A, C42411119 AOTA-B201610S3R3-101-T, C431540 MSK12C02, C442635 DMP4047LFDE-7, C48192 NSR0320MW2T1G, C485918 TPS4H160AQPWPRQ1, C492401 PZ254V-11-02P, C492422 PZ254V-12-10P, C506658 DF11-12DP-2DSA(08), C506665 DF11-4DP-2DSA(08), C51118 AP2112K-3.3TRG1, C5119943 5040500291, C52306 CL32A226KAJNNNE, C527464 DRV2605LDGSR, C530664 KH-MMCX-Z, C555460 TPS54225PWPR, C558584 MCP23017T-E/SS, C563981 5040500691, C580306 LT8610ABEMSE#TRPBF, C597838 DF11CZ-4DP-2V(27), C671115 LT3652IMSE#TRPBF, C72334 WJ500V-5.08-03P-14-00A, C72443 KMR221GLFS, C7467404 FRC2010F43R0TS, C77328 BAT54W, C78284 BSS138, C81248 25121WF120LT4E, C8409 WJ2EDGKA-5.08-02P-14-00A, C84494 GRM32ER71A476KE15L, C861248 RT0603BRD07243KL, C861602 RT0603BRD0794K2L, C87469 INA219AIDCNR, C87572 SPM6530T-1R0M120, C90143 EMK325ABJ107MM-P, C919695 LIS2MDLTR, C92124 PMR18EZPFV2L00, C964818 MY-1220-03

## Board and BOM counts (measured)

| Measure | Value |
|---|---|
| Edge.Cuts bbox | 153.15 × 124.66 mm (190.9 cm²) |
| Copper layers, thickness | 4, 1.6 mm (JLC04161H-7628) |
| Footprints on board | 485 (9 excluded: H1/H2/H10–H12, FID1/FID2, logo, REF**) |
| BOM-scope placements | 472. Grouped BOM: 182 lines (Value+Footprint+LCSC). |
| Side | top 333, bottom 139. **Double-sided, so Standard PCBA only.** |
| KiCad attribute | SMD 401, THT 38, unspecified 33 |
| JLC process (ordered parts) | SMT 410 (top 273, bottom 137), THT 26 (all top, JLC hand-solders) |
| Joints per board | SMT 1,549, THT 103 |
| Vias | 0.40/0.20 ×78, 0.46/0.20 ×481, 0.56/0.30 ×218, 0.60/0.30 ×66, 0.80/0.40 ×222 |
| Min track / clearance | 0.127 / 0.127 mm (418 segments at 0.127) |
| Via-in-pad (`tools/pcb/via_in_pad.py`) | 0 in-pad, 45 edge, so no POFV |
| Castellation | none |
| Surface finish in board file | `None` (not recorded for FlatSat or Rev2) |

Fab capability tier: 0.127 mm track/space is well above JLC's 0.09 mm multilayer minimum. The **78 EMU_FANOUT vias at 0.40 dia / 0.20 hole fall in JLC's paid via option** ("0.2 or 0.25 mm holes with via diameter under 0.45 mm cost more"). Growing them to 0.45 mm would remove that surcharge, if EMU_FANOUT clearance allows.

## Cost estimate

### Per-order totals (USD, before shipping and duties)

| Line | qty 2 assembled (5 fabbed) | qty 5 assembled | Basis |
|---|--:|--:|---|
| PCB fab, 5 pcs, HASL-LF to ENIG | 60 to 85 | 60 to 85 | **assumed** (quote page not scriptable) |
| Parts (MOQ + attrition, tier price) | 259.73 | 578.63 | **measured** live prices × computed quantities |
| Setup, Standard double-side | 51.12 | 51.12 | published |
| Stencil, Standard double-side | 16.42 | 16.42 | published |
| Feeder loading, 117 types × $1.53 | 179.01 | 179.01 | published rate, per-type basis **assumed** |
| SMT joints × $0.0016 | 4.96 | 12.39 | published × measured joints |
| THT joints × $0.0164 + $3.58 labor | 6.96 | 12.03 | published × measured joints |
| X-ray (U2, U7, U15, U18, U200, U511, Q510 per board) | 11.48 | 28.70 | published; which parts trigger it is **assumed** |
| Packing + placement confirm | 0.96 | 0.98 | published |
| **Total per order** | **~591 to 616** | **~940 to 965** | |
| **Per assembled board** | **~296 to 308** | **~188 to 193** | |
| If feeder fee applies to Extended only (81 types) | −55.08 | −55.08 | alternative reading |
| Shipping, DHL/FedEx to LA | +30 to 45 | +35 to 50 | **assumed**. US import duties on PCBA are excluded. |

Qty 2 means 5 bare boards fabricated and 2 assembled. JLC's PCBA quantity selector allows 2 (published Standard range "2 - 80000 pcs"). The 3 spare bare boards ship with the order.

### Top 10 cost drivers (qty 5 order)

| # | Driver | $ (qty 5) | Lever |
|---|---|--:|---|
| 1 | Feeder loading (117 unique codes) | 179.01 | Collapse PLM-08 headers and C701 (−3 types). Fixed per order, so it dominates at small qty. |
| 2 | PCB fab | 60 to 85 | HASL vs ENIG; 0.40/0.20 via surcharge |
| 3 | Setup, double-side | 51.12 | Fixed |
| 4 | U2 ZDSD02GLGEAG (C2875853) | 42.72 | |
| 5 | IC6 LT3652IMSE (C671115) | 42.63 | |
| 6 | U12 LT8610ABEMSE (C580306) | 36.93 | |
| 7 | U13 E22-400M30S (C411292) | 33.77 | |
| 8 | U30 E28-2G4M27S (C411312) | 32.10 | |
| 9 | X-ray | 28.70 | |
| 10 | U300, U310–U316 TCA4311A ×8 (C130025) | 28.26 | |

The next items are IRF7458 ×2 ($25.34), LIS2MDL ($25.21) and W25Q128 ×2 ($23.99). The full per-part table is in the Appendix.

## Assumptions

| Assumption | Why |
|---|---|
| Fab $60 to $85 for 5 pcs | Assumed. The JLC quote page is JS-only and was not scriptable. The range covers HASL-LF vs ENIG, the JLC04161H-7628 stackup, and the small-via surcharge. Get a real quote before ordering. |
| ENIG recommended | Inferred. RP2350 QFN-60 at 0.4 mm pitch and three LGA sensors favor a flat finish. No prior order recorded a finish. |
| Feeder fee is per unique code | The published table says "$1.53 Basic/Extend" for Standard and gives no unit basis. |
| No preferred-extended waivers | jlcsearch found 37 of 81 Extended codes, and none were flagged preferred. The other 44 are unknown. |
| 4-wire Kelvin test, solvent cleaning | Assumed $0. Not priced on the pages fetched. |
| Parts prices | Measured unit price at the tier reached by max(qty × N + attrition, MOQ). Blocked parts B1/B2 are included at list price. |
| JLC hand-solders the 26 THT parts | Measured: `assemblyProcess=THT`, `assemblyMode=manualWeld` on 10 codes |

## Sources

| Source | Used for |
|---|---|
| `https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode=…` (GET, 119 codes) | Stock, Basic/Extended, MOQ, attrition, price tiers, package, SMT/THT |
| `https://jlcsearch.tscircuit.com/components/list.json?search=…` | Preferred-extended flag (37/81 found) |
| https://jlcpcb.com/help/article/pcb-assembly-price | Setup, stencil, feeder, joint, X-ray, packing fees |
| https://jlcpcb.com/capabilities/pcb-assembly-capabilities | Economic vs Standard eligibility (Economic is single-sided only) |
| https://jlcpcb.com/capabilities/pcb-capabilities | Via size tiers, track/space minimum, finishes |
| `https://bouni.github.io/kicad-jlcpcb-tools/chunk_num_fts5.txt` | Reachable (12 chunks). Full DB not downloaded because the live API covered every code. |

Exports and scripts (not committed, CSV is ignored): `/private/tmp/claude-501/-Users-ossf-1-GitHut/0ffadabf-7bf0-51b2-8fd8-5873ed53463c/scratchpad/bom/` (`bom_grouped.csv`, `bom_flat.csv`, `pos.csv`, `board.json`, `align_rows.json`, `parts_table.json`, `live/*.json`), scripts in `../tools/` (`dump_board.py`, `align.py`, `fetch_live.py`, `parts_table.py`, `cost.py`, `geom.py`).

## Appendix: per-part order (live 2026-10-21)

| LCSC | MPN | Refs | Qty/bd | Lib | JLC proc | Stock | MOQ | Attrition | Order $ (2) | Order $ (5) |
|---|---|---|--:|---|---|--:|--:|--:|--:|--:|
| C2875853 | ZDSD02GLGEAG | U2 | 1 | Ext | SMT | 2,538 | 1 | 0 | 17.09 | 42.72 |
| C671115 | LT3652IMSE#TRPBF | IC6 | 1 | Ext | SMT | 2,811 | 1 | 0 | 17.05 | 42.63 |
| C580306 | LT8610ABEMSE#TRPBF | U12 | 1 | Ext | SMT | 1,718 | 1 | 0 | 14.77 | 36.93 |
| C411292 | E22-400M30S | U13 | 1 | Ext | SMT | 229 | 1 | 0 | 13.51 | 33.77 |
| C411312 | E28-2G4M27S | U30 | 1 | Ext | SMT | 467 | 1 | 0 | 12.84 | 32.10 |
| C130025 | TCA4311ADGKR | U300 U310 U311 U312 U313 U314 U315 U316 | 8 | Ext | SMT | 2,255 | 1 | 0 | 12.72 | 28.26 |
| C10879 | IRF7458TRPBF | Q500 Q501 | 2 | Ext | SMT | 24 | 1 | 0 | 11.98 | 25.34 |
| C919695 | LIS2MDLTR | U15 | 1 | Ext | SMT | 4,218 | 1 | 0 | 10.09 | 25.21 |
| C97521 | W25Q128JVSIQ | U11 U201 | 2 | Basic | SMT | 55,904 | 1 | 0 | 11.41 | 23.99 |
| C2655100 | LSM6DSOTR | U7 | 1 | Ext | SMT | 1,456 | 1 | 0 | 7.81 | 19.52 |
| C485918 | TPS4H160AQPWPRQ1 | U6 | 1 | Ext | SMT | 16 | 1 | 0 | 6.26 | 15.64 |
| C18214056 | APS1604M-3SQR-SN | U5 | 1 | Ext | SMT | 721 | 1 | 0 | 5.15 | 12.88 |
| C90143 | EMK325ABJ107MM-P | C11 C19 C25 | 3 | Ext | SMT | 39,508 | 5 | 0 | 6.13 | 12.36 |
| C42411118 | RP2350A | U18 U200 | 2 | Ext | SMT | 6,019 | 1 | 0 | 5.17 | 12.07 |
| C563981 | 5040500691 | J1 J11 J13 J2 J6 J9 | 6 | Ext | SMT | 3,364 | 1 | 0 | 5.10 | 11.33 |
| C87469 | INA219AIDCNR | U16 U8 | 2 | Ext | SMT | 3,459 | 2 | 0 | 5.09 | 11.15 |
| C72443 | KMR221GLFS | SW1 SW2 SW701 SW702 | 4 | Ext | SMT | 4,373 | 5 | 0 | 5.23 | 10.76 |
| C1857514 | TPS2HB50AQPWPRQ1 | U25 | 1 | Ext | SMT | 125 | 1 | 0 | 3.95 | 9.88 |
| C3304278 | RV-3028-C7-32.768KHZ-1PPM-TA-QA | IC3 | 1 | Ext | SMT | 0 | 1 | 0 | 3.85 | 9.61 |
| C1511768 | AP22653AW6-7 | U19 U21 U22 U23 U24 U27 U29 | 7 | Ext | SMT | 6,906 | 5 | 0 | 3.64 | 9.11 |
| C3235552 | DZDH0401DW-7 | U510 | 1 | Ext | SMT | 9,228 | 1 | 0 | 3.47 | 8.67 |
| C558584 | MCP23017T-E/SS | U9 | 1 | Ext | SMT | 4,548 | 1 | 0 | 3.26 | 8.14 |
| C181596 | TLV1704AIPWR | U1 | 1 | Ext | SMT | 568 | 1 | 0 | 3.18 | 7.95 |
| C110493 | DFLS130L-7 | D12 D13 D15 | 3 | Ext | SMT | 1,571 | 5 | 2 | 4.02 | 6.90 |
| C2765094 | BQ25886RGER | U511 | 1 | Ext | SMT | 5,372 | 1 | 0 | 2.67 | 6.68 |
| C527464 | DRV2605LDGSR | U303 | 1 | Ext | SMT | 10,046 | 1 | 0 | 2.46 | 6.16 |
| C52306 | CL32A226KAJNNNE | C511 C513 C514 C515 C517 C518 | 6 | Ext | SMT | 238,127 | 5 | 2 | 3.26 | 5.86 |
| C5119943 | 5040500291 | J15 J29 J30 J8 | 4 | Ext | SMT | 16,010 | 1 | 0 | 2.15 | 5.37 |
| C597838 | DF11CZ-4DP-2V(27) | J23 | 1 | Ext | SMT | 87 | 1 | 0 | 2.14 | 5.36 |
| C20625731 | ABM8-272-T3 | Y1 Y200 | 2 | Ext | SMT | 4,699 | 5 | 0 | 3.23 | 5.33 |
| C3678616 | VEML6031X00 | U302 | 1 | Ext | SMT | 221 | 1 | 0 | 1.99 | 4.96 |
| C506658 | DF11-12DP-2DSA(08) | J14 J16 J18 | 3 | Ext | THT | 8,174 | 2 | 0 | 1.73 | 4.33 |
| C130026 | TCA9548APWR | U3 | 1 | Ext | SMT | 28,011 | 1 | 0 | 1.65 | 4.11 |
| C177235 | 5040500491 | J21 J24 | 2 | Ext | SMT | 2,285 | 5 | 0 | 2.48 | 4.07 |
| C530664 | KH-MMCX-Z | RF1 | 1 | Ext | THT | 2,986 | 2 | 0 | 1.48 | 3.69 |
| C42411119 | AOTA-B201610S3R3-101-T | L200 L3 | 2 | Ext | SMT | 1 | 5 | 1 | 1.42 | 3.13 |
| C555460 | TPS54225PWPR | U10 | 1 | Ext | SMT | 590 | 1 | 0 | 1.25 | 3.12 |
| C506665 | DF11-4DP-2DSA(08) | J10 J19 J20 J7 | 4 | Ext | THT | 914 | 2 | 1 | 1.29 | 3.01 |
| C92124 | PMR18EZPFV2L00 | R108 R109 | 2 | Ext | SMT | 8,325 | 5 | 0 | 1.50 | 3.00 |
| C2886093 | CDBA240LL-HF | D400 D401 | 2 | Ext | SMT | 619 | 5 | 0 | 1.48 | 2.95 |
| C8409 | WJ2EDGKA-5.08-02P-14-00A | J400 J401 | 2 | Ext | THT | 1,013 | 2 | 0 | 1.16 | 2.91 |
| C165948 | TYPE-C-31-M-12 | J12 J510 J701 | 3 | Ext | SMT | 331,728 | 2 | 0 | 1.12 | 2.80 |
| C160389 | BM03B-SRSS-TB(LF)(SN) | J22 J702 | 2 | Ext | SMT | 27,741 | 5 | 0 | 1.38 | 2.76 |
| C84494 | GRM32ER71A476KE15L | C8 | 1 | Ext | SMT | 8,227 | 5 | 0 | 2.43 | 2.43 |
| C442635 | DMP4047LFDE-7 | Q510 | 1 | Ext | SMT | 4,303 | 5 | 0 | 2.12 | 2.12 |
| C207086 | 2920L185DR | F400 F401 | 2 | Ext | SMT | 15,360 | 2 | 0 | 0.79 | 1.98 |
| C404816 | SPM6530T-3R3M-HZ | L4 | 1 | Ext | SMT | 982 | 2 | 0 | 0.76 | 1.91 |
| C19702 | CL10A106KP8NNNC | C1 C14 C20 C202 C21 C22 C23 C24 C3 C4... | 12 | Basic | SMT | 9,656,367 | 20 | 10 | 0.92 | 1.90 |
| C48192 | NSR0320MW2T1G | D200 D4 | 2 | Ext | SMT | 21,750 | 5 | 5 | 1.05 | 1.75 |
| C259714 | R5460N208AA-TR-FE | U500 | 1 | Ext | SMT | 2,830 | 5 | 0 | 1.70 | 1.70 |
| C360729 | SPM6530T-4R7M-HZ | L5 | 1 | Ext | SMT | 1,414 | 5 | 0 | 1.64 | 1.64 |
| C160390 | BM04B-SRSS-TB(LF)(SN) | J5 | 1 | Ext | SMT | 29,462 | 5 | 1 | 1.27 | 1.53 |
| C28927 | TMP112AIDRLR | U301 | 1 | Ext | SMT | 3,185 | 5 | 0 | 1.52 | 1.52 |
| C112288 | SPM6530T-100M | L1 | 1 | Ext | SMT | 3,655 | 5 | 1 | 1.14 | 1.36 |
| C124375 | B-2100S02P-A110 | JP600 JP601 JP602 JP603 JP604 JP605 J... | 8 | Ext | THT | 177,875 | 2 | 5 | 0.63 | 1.35 |
| C2182156 | EMK212BB7106KG-T | C701 | 1 | Ext | SMT | 35,686 | 5 | 4 | 0.82 | 1.24 |
| C1525 | CL05B104KO5NNNC | C10 C18 C2 C201 C203 C204 C205 C206 C... | 60 | Basic | SMT | 37,556,250 | 20 | 10 | 0.48 | 1.15 |
| C17429783 | 1N4151WS-E3-18 | D7 | 1 | Ext | SMT | 5,430 | 5 | 0 | 1.11 | 1.11 |
| C72334 | WJ500V-5.08-03P-14-00A | J500 | 1 | Ext | THT | 177,075 | 2 | 0 | 0.43 | 1.08 |
| C2887259 | SS12D10G4 071 | SW703 | 1 | Ext | THT | 27,494 | 2 | 0 | 0.41 | 1.03 |
| C87572 | SPM6530T-1R0M120 | L510 | 1 | Ext | SMT | 702 | 5 | 0 | 1.01 | 1.01 |
| C51118 | AP2112K-3.3TRG1 | U202 | 1 | Ext | SMT | 16,774 | 5 | 0 | 0.89 | 0.89 |
| C15850 | CL21A106KAYNNNE | C214 C75 | 2 | Basic | SMT | 9,536,527 | 20 | 10 | 0.85 | 0.85 |
| C861248 | RT0603BRD07243KL | R23 | 1 | Ext | SMT | 61,052 | 20 | 8 | 0.79 | 0.79 |
| C23733 | CL05A475MP5NRNC | C213 C215 C216 C217 C65 C66 C68 C69 | 8 | Basic | SMT | 2,782,035 | 20 | 10 | 0.40 | 0.77 |
| C861602 | RT0603BRD0794K2L | R69 | 1 | Ext | SMT | 8,892 | 20 | 8 | 0.73 | 0.73 |
| C28323 | CL21B105KBFNNNE | C510 | 1 | Basic | SMT | 2,151,898 | 20 | 10 | 0.68 | 0.68 |
| C964818 | MY-1220-03 | BT1 | 1 | Ext | SMT | 2,295 | 2 | 1 | 0.32 | 0.63 |
| C59461 | CL10A226MQ8NRNC | C15 C16 | 2 | Basic | SMT | 6,773,101 | 20 | 10 | 0.63 | 0.63 |
| C431540 | MSK12C02 | SW600 | 1 | Ext | SMT | 195,614 | 2 | 6 | 0.43 | 0.60 |
| C25900 | 0402WGF4701TCE | R100 R103 R104 R105 R106 R110 R111 R2... | 54 | Basic | SMT | 15,004,800 | 20 | 10 | 0.25 | 0.59 |
| C2290 | KT-0603W | D1 D2 D201 D202 D3 D510 LED600 | 7 | Basic | SMT | 1,687,020 | 20 | 10 | 0.30 | 0.55 |
| C15849 | CL10A105KB8NNNC | C200 C37 C4 C41 | 4 | Basic | SMT | 14,569,909 | 20 | 10 | 0.31 | 0.46 |
| C77328 | BAT54W | D600 D601 D602 | 3 | Ext | SMT | 3,740 | 5 | 4 | 0.24 | 0.45 |
| C81248 | 25121WF120LT4E | R75 | 1 | Ext | SMT | 3,839 | 5 | 4 | 0.27 | 0.40 |
| C19666 | CL10A475KO8NNNC | C516 | 1 | Basic | SMT | 3,200,317 | 20 | 10 | 0.39 | 0.39 |
| C78284 | BSS138 | Q701 Q702 Q703 | 3 | Ext | SMT | 106,030 | 10 | 5 | 0.22 | 0.39 |
| C25803 | 0603WAF1003T5E | R101 R30 R32 R33 R34 R36 R43 R505 R65... | 21 | Basic | SMT | 18,689,131 | 20 | 10 | 0.16 | 0.36 |
| C492422 | PZ254V-12-10P | J703 | 1 | Ext | THT | 110,038 | 2 | 0 | 0.13 | 0.33 |
| C492401 | PZ254V-11-02P | J300 JP400 JP401 | 3 | Ext | THT | 1,033,311 | 2 | 0 | 0.11 | 0.28 |
| C1613 | CL10B332KB8NNNC | C36 | 1 | Basic | SMT | 369,716 | 20 | 10 | 0.26 | 0.26 |
| C14663 | CC0603KRX7R9BB104 | C500 C501 C502 C503 | 4 | Basic | SMT | 46,782,401 | 20 | 10 | 0.16 | 0.25 |
| C12624 | KT-0603G | D6 | 1 | Ext | SMT | 471,520 | 20 | 16 | 0.23 | 0.25 |
| C16772 | CL05B224KO5NNNC | C31 C54 C56 C57 C58 | 5 | Basic | SMT | 1,387,157 | 20 | 18 | 0.14 | 0.21 |
| C25804 | 0603WAF1002T5E | R1 R107 R11 R124 R13 R14 R15 R16 R17 ... | 21 | Basic | SMT | 37,287,115 | 20 | 10 | 0.09 | 0.21 |
| C25819 | 0603WAF4702T5E | R46 R47 R48 R49 R50 R51 R86 | 7 | Basic | SMT | 2,504,238 | 20 | 10 | 0.08 | 0.16 |
| C1622 | CL10B473KB8NNNC | C512 | 1 | Basic | SMT | 1,024,508 | 20 | 10 | 0.15 | 0.15 |
| C52923 | CL05A105KA5NQNC | C304 | 1 | Basic | SMT | 7,864,050 | 20 | 10 | 0.15 | 0.15 |
| C358684 | MTP125-1102S1 | JP500 JP510 | 2 | Ext | THT | 141,496 | 2 | 5 | 0.08 | 0.14 |
| C25744 | 0402WGF1002TCE | R2 R202 R205 R300 R301 R302 R303 R310... | 21 | Basic | SMT | 18,623,622 | 20 | 10 | 0.06 | 0.14 |
| C7467404 | FRC2010F43R0TS | R304 | 1 | Ext | SMT | 4,516 | 5 | 2 | 0.10 | 0.13 |
| C32949 | CL05C100JB5NNNC | C12 | 1 | Basic | SMT | 1,735,563 | 20 | 10 | 0.12 | 0.12 |
| C1548 | 0402CG150J500NT | C221 C222 C63 C64 | 4 | Basic | SMT | 1,058,914 | 20 | 10 | 0.08 | 0.11 |
| C21190 | 0603WAF1001T5E | R10 R102 R29 R3 R31 R4 R502 R519 R64 R81 | 10 | Basic | SMT | 37,104,226 | 20 | 10 | 0.05 | 0.11 |
| C227953 | AC0603FR-0752K3L | R42 | 1 | Ext | SMT | 39,588 | 20 | 10 | 0.10 | 0.10 |
| C22809 | 0603WAF1502T5E | R54 R55 R82 R85 | 4 | Basic | SMT | 3,940,711 | 20 | 10 | 0.06 | 0.09 |
| C15195 | CL05B103KB5NNNC | C301 C6 | 2 | Basic | SMT | 5,705,057 | 20 | 10 | 0.08 | 0.08 |
| C17513 | 0805W8F1001T5E | R503 R504 | 2 | Basic | SMT | 43,607,773 | 20 | 10 | 0.07 | 0.07 |
| C23241 | 0603WAF7500T5E | R514 | 1 | Ext | SMT | 371,299 | 20 | 10 | 0.07 | 0.07 |
| C25905 | 0402WGF5101TCE | R510 R511 R701 R702 | 4 | Basic | SMT | 4,810,129 | 20 | 10 | 0.05 | 0.07 |
| C11702 | 0402WGF1001TCE | R201 R204 R206 R211 R705 R707 R709 R93 | 8 | Basic | SMT | 20,182,599 | 20 | 10 | 0.03 | 0.07 |
| C4211 | 0603WAF3001T5E | R19 R20 R21 | 3 | Basic | SMT | 7,386,344 | 20 | 10 | 0.05 | 0.06 |
| C137768 | RC0603FR-0722K1L | R40 | 1 | Ext | SMT | 258,990 | 20 | 10 | 0.06 | 0.06 |
| C22935 | 0603WAF1004T5E | R512 R513 R63 | 3 | Basic | SMT | 5,980,977 | 20 | 10 | 0.04 | 0.05 |
| C23050 | 0603WAF4123T5E | R74 | 1 | Ext | SMT | 254 | 20 | 10 | 0.05 | 0.05 |
| C23188 | 0603WAF5621T5E | R515 | 1 | Ext | SMT | 23,217 | 20 | 10 | 0.05 | 0.05 |
| C25092 | 0402WGF220JTCE | R7 R703 R704 R8 | 4 | Basic | SMT | 3,518,796 | 20 | 10 | 0.03 | 0.04 |
| C23138 | 0603WAF3300T5E | R500 R501 | 2 | Basic | SMT | 3,972,527 | 20 | 10 | 0.04 | 0.04 |
| C23068 | 0603WAF5231T5E | R516 | 1 | Ext | SMT | 72,045 | 20 | 10 | 0.04 | 0.04 |
| C2999499 | FRC0603F6343TS | R71 | 1 | Ext | SMT | 21,093 | 20 | 10 | 0.04 | 0.04 |
| C18335 | 0603WAJ0475T5E | R35 | 1 | Ext | SMT | 17,158 | 20 | 10 | 0.04 | 0.04 |
| C14890 | 0603WAF7322T5E | R38 | 1 | Ext | SMT | 109,655 | 20 | 10 | 0.04 | 0.04 |
| C23000 | 0603WAF3012T5E | R517 | 1 | Ext | SMT | 81,950 | 20 | 10 | 0.03 | 0.03 |
| C23186 | 0603WAF5101T5E | R26 R27 | 2 | Basic | SMT | 22,652,120 | 20 | 10 | 0.03 | 0.03 |
| C25117 | 0402WGF4700TCE | R602 | 1 | Basic | SMT | 1,190,109 | 20 | 10 | 0.02 | 0.02 |
| C25105 | 0402WGF330JTCE | R200 R94 | 2 | Basic | SMT | 2,309,992 | 20 | 10 | 0.02 | 0.02 |
| C17168 | 0402WGF0000TCE | R203 R91 | 2 | Basic | SMT | 9,882,471 | 20 | 10 | 0.02 | 0.02 |
| **Total** | | | **436** | | | | | | **259.73** | **578.63** |
