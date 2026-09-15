# Supply chain — Battery Replica and Bench Power (refdes 500–599)

**Date:** 2026-09-14 · **Owner:** Sonnet agent, Phase 2 stage 1 (supply chain) · **Sheet:** `FlatSat_V1/battery_protection_replica.kicad_sch` · **Generator:** `FlatSat_V1/tools/gen/battery_protection_replica_gen.py` · **Brief:** `00_pm_brief.md` §3 L9, §4 rule 5 (Phase-1 brief §3 rule 5 referenced there is the "nothing but fields may change" schematic rule)

**Review-fix pass (2026-09-14, same day):** a verifier found 3 defects in the original pass — (1, major) the J500/JP500/JP510 "highest-stock" queries sorted `Stock` as TEXT (it is stored as SQLite TEXT) instead of numerically, so the true top-stock parts in each footprint class were silently missed; re-run with `ORDER BY CAST(Stock AS INTEGER) DESC` and the selections corrected (J500: `C474953`→`C72334`, ~19x more stock; JP500/JP510: `C7430358`→`C358684`, ~3.6x more stock) — (2, minor) the §4/owner-summary "4 datasheets added" count double-counted U511, whose datasheet was untouched (pre-existing from Phase-1) — corrected to 3 — (3, minor) §3's test-point citation named a non-existent "TP1" — dropped. All three are fixed below; proofs re-run clean. Sections below reflect the corrected state; changes from the original pass are marked "corrected in review-fix pass" inline.

Database: `~/Documents/KiCad/10.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/parts-fts5.db`, table `parts` (fts5, trigram tokenizer). Plain `=`/`LIKE` were used throughout (a bare `MATCH` on short numeric/Ω tokens was unreliable and is not used below); `LIKE` needed a leading/trailing space around the value token to avoid matching sub-decades (e.g. `%5.7kΩ%` also matches `35.7kΩ`).

50 symbols on this sheet (sheetpath `/Battery Replica and Bench Power/`). Of those: 12 had a blank `LCSC Part` (11 filled below, 1 — R515 — stays unresolved, see §3); 16 already carried an `LCSC Part` and were re-verified (§2, query 1) with no mismatches; 9 test points (TP500–TP505, TP510–TP512) carry no LCSC by the FC's own convention (§3); the rest are `#PWR`/`#FLG` power symbols, out of scope.

## 1. Full part table

| Ref | Value | Footprint | LCSC | MPN | Lib Type | Stock | Price (¥, 1pc break) | Source |
|---|---|---|---|---|---|---|---|---|
| BT1 | MY-1220-03 | easyeda2kicad:BAT-SMD_MY-1220-03 | C964818 | MY-1220-03 | — | — | — | Root sheet, outside this sheet's refdes block — listed by the netlist under sheetpath `/`, not `/Battery Replica and Bench Power/`; not this agent's part, out of scope |
| C500 | 0.1uF | Capacitor_SMD:C_0603_1608Metric | C14663 | CC0603KRX7R9BB104 | Basic | 53,757,674 | — | **Pre-existing, re-verified** (query 1): 100nF 50V X7R 0603, matches |
| C501 | 0.1uF | Capacitor_SMD:C_0603_1608Metric | C14663 | CC0603KRX7R9BB104 | Basic | 53,757,674 | — | same as C500 |
| C502 | 0.1uF | Capacitor_SMD:C_0603_1608Metric | C14663 | CC0603KRX7R9BB104 | Basic | 53,757,674 | — | same as C500 |
| C503 | 0.1uF | Capacitor_SMD:C_0603_1608Metric | C14663 | CC0603KRX7R9BB104 | Basic | 53,757,674 | — | same as C500 |
| C510 | 1uF | Capacitor_SMD:C_0805_2012Metric | C28323 | CL21B105KBFNNNE | Basic | 3,479,565 | — | **Pre-existing, re-verified**: 1uF 50V X7R 0805, matches |
| C511 | 22uF 25V | Capacitor_SMD:C_1210_3225Metric | C52306 | CL32A226KAJNNNE | Extended | 336,176 | — | **Pre-existing, re-verified**: 22uF 25V X5R 1210, matches (Phase-1 review's own "22uF 25V \| C_1210_3225Metric \| C52306 (all six)" line) |
| C512 | 47nF | Capacitor_SMD:C_0603_1608Metric | **C1622** | CL10B473KB8NNNC | Basic | 1,010,662 | 1-:0.008 | **New** (query 2): 47nF 50V X7R 0603, only Basic 0603 47nF in the catalogue |
| C513 | 22uF 25V | Capacitor_SMD:C_1210_3225Metric | C52306 | CL32A226KAJNNNE | Extended | 336,176 | — | same as C511 |
| C514 | 22uF 25V | Capacitor_SMD:C_1210_3225Metric | C52306 | CL32A226KAJNNNE | Extended | 336,176 | — | same as C511 |
| C515 | 22uF 25V | Capacitor_SMD:C_1210_3225Metric | C52306 | CL32A226KAJNNNE | Extended | 336,176 | — | same as C511 |
| C516 | 4.7uF | Capacitor_SMD:C_0603_1608Metric | **C19666** | CL10A475KO8NNNC | Basic | 3,663,291 | 1-99:0.033 | **New** (query 3): 16V 4.7uF X5R 0603 — matches the CREGN LDO-decoupling requirement (description says 16 V) |
| C517 | 22uF 25V | Capacitor_SMD:C_1210_3225Metric | C52306 | CL32A226KAJNNNE | Extended | 336,176 | — | same as C511 |
| C518 | 22uF 25V | Capacitor_SMD:C_1210_3225Metric | C52306 | CL32A226KAJNNNE | Extended | 336,176 | — | same as C511 |
| D510 | LED | LED_SMD:LED_0603_1608Metric | C2290 | KT-0603W | Basic | 1,158,040 | — | **Pre-existing, re-verified**: 0603 LED, matches |
| J500 | BENCH PSU B+/MID/B- | TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal | **C72334** | WJ500V-5.08-03P-14-00A | Extended | 226,856 | 1-49:0.215 | **New, corrected in review-fix pass** (query 4, numeric-sorted): 3-position 5.08mm-pitch single-piece pluggable screw terminal, true highest-stock part in this footprint class |
| J510 | USB-C CHARGER IN (power only) | Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12 | C165948 | TYPE-C-31-M-12 | Extended | 243,870 | — | **Pre-existing, re-verified**: USB-C receptacle, matches |
| JP500 | MID DIV - FIT | Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical | **C358684** | MTP125-1102S1 | Extended | 237,277 | 1-:0.009 | **New, corrected in review-fix pass** (query 5, numeric-sorted): 1x2P 2.54mm through-hole pin header, true highest-stock part in this footprint class |
| JP510 | CHG OUT - OPEN | Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical | **C358684** | MTP125-1102S1 | Extended | 237,277 | 1-:0.009 | same as JP500 |
| L510 | SPM6530T-1R0M120 | easyeda2kicad:IND-SMD_L7.1-W6.5-P5.60 | C87572 | SPM6530T-1R0M120 | Extended | 11,577 | — | **Pre-existing, re-verified**: matches; verified live in the Phase-1 review (§3.1 of `02_review_report.md`) |
| Q500 | IRF7458 | Package_SO:SOIC-8_3.9x4.9mm_P1.27mm | C10879 | IRF7458TRPBF | Extended | 57 | — | **Pre-existing, re-verified**: N-ch 30V SO-8, matches. Stock is thin (57 units) — flagged as a supply risk, see §3 |
| Q501 | IRF7458 | Package_SO:SOIC-8_3.9x4.9mm_P1.27mm | C10879 | IRF7458TRPBF | Extended | 57 | — | same as Q500; same stock risk |
| Q510 | DMP4047LFDE-7 | easyeda2kicad:U-DFN2020-6E_L2.0-W2.0-P0.65-BL | C442635 | DMP4047LFDE-7 | Extended | 12,860 | — | **Pre-existing, re-verified**: matches; verified live in the Phase-1 review |
| R500 | 330 | Resistor_SMD:R_0603_1608Metric | C23138 | 0603WAF3300T5E | Basic | 4,008,776 | — | **Pre-existing, re-verified**: 330Ω 0603, matches |
| R501 | 330 | Resistor_SMD:R_0603_1608Metric | C23138 | 0603WAF3300T5E | Basic | 4,008,776 | — | same as R500 |
| R502 | 1k | Resistor_SMD:R_0603_1608Metric | C21190 | 0603WAF1001T5E | Basic | 26,034,969 | — | **Pre-existing, re-verified**: 1kΩ 0603, matches |
| R503 | 1.0k 1% | Resistor_SMD:R_0805_2012Metric | **C17513** | 0805W8F1001T5E | Basic | 30,684,161 | 1-:0.004 | **New** (query 6): 1kΩ ±1% 0805, exact match to the brief's "0805 1%" requirement |
| R504 | 1.0k 1% | Resistor_SMD:R_0805_2012Metric | **C17513** | 0805W8F1001T5E | Basic | 30,684,161 | 1-:0.004 | same as R503 |
| R505 | 100k | Resistor_SMD:R_0603_1608Metric | C25803 | 0603WAF1003T5E | Basic | 23,829,690 | — | **Pre-existing, re-verified**: 100kΩ 0603, matches |
| R510 | 5.1k | Resistor_SMD:R_0402_1005Metric | C25905 | 0402WGF5101TCE | Basic | 7,547,316 | — | **Pre-existing, re-verified**: 5.1kΩ 0402, matches |
| R511 | 5.1k | Resistor_SMD:R_0402_1005Metric | C25905 | 0402WGF5101TCE | Basic | 7,547,316 | — | same as R510 |
| R512 | 1M | Resistor_SMD:R_0603_1608Metric | C22935 | 0603WAF1004T5E | Basic | 7,762,450 | — | **Pre-existing, re-verified**: 1MΩ 0603, matches |
| R513 | 1M | Resistor_SMD:R_0603_1608Metric | C22935 | 0603WAF1004T5E | Basic | 7,762,450 | — | same as R512 |
| R514 | 750 | Resistor_SMD:R_0603_1608Metric | **C23241** | 0603WAF7500T5E | Extended | 603,086 | 1-:0.004 | **New** (query 7): 750Ω ±1% 0603 — no Basic part exists at 750Ω 0603 (the whole Basic 0603 E24 ladder skips this one mid-decade value; confirmed by enumerating all 80 Basic 0603 resistors, §2) |
| R515 | 5.62k | Resistor_SMD:R_0603_1608Metric | **C23188** | 0603WAF5621T5E | Extended | 29,745 | 1-:0.003 | **PM ruling S1 applied** (2026-09-14, §7): value changed 5.7k→5.62k 1% 0603 (E96) — 5.7k was neither E24 nor E96 and had no catalogue part. Same Uniroyal 0603WAF family as every other 0603 R on this sheet (R500-R502/R505/R512-R514/R516-R519), per the family-consistency precedent PM ruling S3 already accepted for R516/R517 (query 11, §2) |
| R516 | 5.23k | Resistor_SMD:R_0603_1608Metric | **C23068** | 0603WAF5231T5E | Extended | 51,539 | 1-:0.002 | **New** (query 8): 5.23kΩ ±1% 0603, E96 precision value — Extended only, no Basic 0603 exists above the E24 ladder |
| R517 | 30.1k | Resistor_SMD:R_0603_1608Metric | **C23000** | 0603WAF3012T5E | Extended | 74,544 | 1-:0.002 | **New** (query 9): 30.1kΩ ±1% 0603, same reasoning as R516 |
| R518 | 10k | Resistor_SMD:R_0603_1608Metric | C25804 | 0603WAF1002T5E | Basic | 26,967,989 | — | **Pre-existing, re-verified**: 10kΩ 0603, matches |
| R519 | 1k | Resistor_SMD:R_0603_1608Metric | C21190 | 0603WAF1001T5E | Basic | 26,034,969 | — | **Pre-existing, re-verified**: 1kΩ 0603, matches |
| TP500 | Dir_Chrg_In | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |
| TP501 | VBAT_BENCH_N | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |
| TP502 | B- | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |
| TP503 | DOUT_GATE | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |
| TP504 | COUT_GATE | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |
| TP505 | MID_BENCH | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |
| TP510 | VBUS_CHG | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |
| TP511 | CHG_SYS | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |
| TP512 | CHG_BAT | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |
| U500 | R5460N208AA-TR-FE | Package_TO_SOT_SMD:SOT-23-6 | C259714 | R5460N208AA-TR-FE | Extended | 2,860 | — | **Pre-existing, re-verified**: matches |
| U510 | DZDH0401DW-7 | easyeda2kicad:SOT-363_L2.0-W1.3-P0.65-LS2.1-BR | C3235552 | DZDH0401DW-7 | Extended | 10,939 | — | **Pre-existing, re-verified**: matches; verified live in the Phase-1 review |
| U511 | BQ25886RGE | Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm | **C2765094** | BQ25886RGER | Extended | 6,948 | 1-9:1.746 | **New** (query 10): exact MFR.Part family match (BQ25886RGE**R** = tape-and-reel suffix of the schematic's BQ25886RGE), package VQFN-24-EP(4x4) matches the symbol's footprint |

`#PWR500–#PWR5xx`, `#FLG501–#FLG503` (power symbols) have no LCSC/BOM footprint and are out of scope.

## 2. Queries run (verbatim, against `parts-fts5.db`)

**Query 1 — re-verify all 16 pre-existing LCSC numbers on this sheet:**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock
FROM parts WHERE "LCSC Part"=?;
-- run once per: C14663 C23138 C21190 C25803 C25905 C22935 C25804 C2290
--               C10879 C87572 C442635 C3235552 C259714 C28323 C165948 C52306
```
All 16 returned exactly one row each; `MFR.Part`/`Package`/`Description` agree with the symbol's Value/Footprint in every case (details in the table above). **No mismatches found.** The Phase-1 review report flags "8 LCSC numbers project-wide need re-verification" without naming them; none of the anomalies it hints at (the C511/C513-518 22uF/25V/1210 re-cased parts, all C52306) turned out to be wrong — that group was re-verified explicitly and matches the review's own confirmed value.

**Query 2 — 47nF 0603 (C512):**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock,Price FROM parts
WHERE Package='0603' AND Description LIKE '%47nF%' AND "Library Type"='Basic'
ORDER BY Stock DESC LIMIT 10;
```
Single Basic result: `C1622` (CL10B473KB8NNNC, Samsung), 47nF 50V X7R, stock 1,010,662 — selected.

**Query 3 — 4.7uF 0603 (C516):**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock,Price FROM parts
WHERE Package='0603' AND Description LIKE '%4.7uF%' AND "Library Type"='Basic'
ORDER BY Stock DESC LIMIT 15;
```
Single Basic result: `C19666` (CL10A475KO8NNNC, Samsung), **16V** 4.7uF X5R — matches the sheet's own "CREGN LDO decoupling" note (the sheet doc §6.4 wants a 16V-class part for this rail) — selected.

**Query 4 — 3-position 5.08mm screw terminal (J500) — corrected in review-fix pass:**

The original pass's query 4 (`... LIKE 'KF128%...' ORDER BY Stock DESC LIMIT 20`) both over-narrowed to one MFR-Part family and, more importantly, sorted on `Stock`, which is stored as SQLite `TEXT` (`SELECT typeof(Stock) FROM parts` → `text`) — `ORDER BY Stock DESC` is a lexicographic string sort, not a numeric one (e.g. `'226856'` sorts *below* `'11903'` because the first character `'2'` < `'9'`, even though 226,856 is numerically larger), so it silently dropped every true top row and the LIMIT clause never saw them. The original pick, `C474953` (KF128-5.08-3P-AA, stock 11,903), is a real, in-stock, footprint-correct part, but the report's "highest-stock" claim was false. Re-run with a numeric cast, scoped to the exact `Package` value of this footprint class (`'Plugin,P=5.08mm'`, single-piece pluggable screw terminals — excludes `Board Side/Socket` two-part header+plug systems, which are not footprint-compatible with `TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm`):
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock FROM parts
WHERE Package='Plugin,P=5.08mm' AND Description LIKE '%3P%'
ORDER BY CAST(Stock AS INTEGER) DESC LIMIT 20;
```
True top result (excluding Board Side/Socket rows, which are a different mechanical system): `C72334` (WJ500V-5.08-03P-14-00A, Ningbo Wanjia), 5.08mm, 3-position, 18A/250V, single-piece pluggable, stock **226,856** — ~19x the originally-picked part's stock. Second: `C430602` (DB128L-5.08-3P-BK-S, stock 45,561). **Selection corrected to `C72334`.** No Basic screw terminal exists in the catalogue at any pitch (`SELECT count(*) FROM parts WHERE "Library Type"='Basic' AND "First Category" LIKE '%Connector%'` returns 0 — JLC stocks zero Basic-library connectors of any kind), so `C72334` is Extended, same as the part it replaces.

**Query 5 — 1x2P 2.54mm through-hole pin header (JP500/JP510) — corrected in review-fix pass:**

Same `ORDER BY Stock DESC` TEXT-sort bug as query 4. The original pick, `C7430358` (DS1021-1x2SF11-B, stock 66,713), is real and footprint-correct but not the true top result. Re-run with a numeric cast, scoped to the exact `Package` value of this footprint (`'Plugin,P=2.54mm'`, 1x2-position straight pin headers):
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock FROM parts
WHERE Package='Plugin,P=2.54mm' AND Description LIKE '%1x2P%'
ORDER BY CAST(Stock AS INTEGER) DESC LIMIT 20;
```
The single highest-stock row (`C492401`, PZ254V-11-02P, stock 1,222,203) is a square-pin/brass-socket wire-to-board part, not a straight 0.64mm round-pin header of the kind the schematic's `PinHeader_1x02_P2.54mm_Vertical` footprint expects, so it was excluded as not footprint-equivalent. The true top result in the pin-header sub-family: `C358684` (MTP125-1102S1, Zhejiang Ganjia), 1x2P, 2.54mm, straight through-hole pin header, stock **237,277** — ~3.6x the originally-picked part's stock. Second: `C124375` (B-2100S02P-A110, stock 159,910). **Selection corrected to `C358684`** for both JP500 and JP510 (identical footprint, both plain 1x2 shunt headers). No Basic pin headers exist in the catalogue (same zero-Basic-connectors finding as query 4).

**Query 6 — 1.0k 1% 0805 (R503/R504):**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock FROM parts
WHERE Package='0805' AND Description LIKE '%1k%' AND Description LIKE '%±1%%' AND "Library Type"='Basic'
ORDER BY Stock DESC LIMIT 20;
```
`C17513` (0805W8F1001T5E, Uniroyal), 1kΩ ±1%, Basic, stock 30,684,161 — exact value/tolerance/package match to the brief's requirement — selected.

**Query 7 — 750Ω 0603 (R514):**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock FROM parts
WHERE Package='0603' AND Description LIKE '% 750Ω %' ORDER BY "Library Type", Stock DESC;
```
Zero `Library Type='Basic'` rows. Confirmed exhaustively: enumerating every Basic 0603 "Thick Film Resistor" in the catalogue (80 rows, one per E24 decade value 0Ω/1Ω–9.1MΩ) shows the Basic 0603 ladder has 75Ω, 7.5kΩ and 75kΩ but **no 750Ω** — a gap in this specific decade, not a missing search term. Top Extended result: `C23241` (0603WAF7500T5E, Uniroyal — same MFR family as every other Uniroyal 0603 resistor already on this sheet), 750Ω ±1%, stock 603,086 — selected.

**Query 8 — 5.23kΩ 0603 (R516):**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock FROM parts
WHERE Package='0603' AND Description LIKE '% 5.23kΩ %' ORDER BY "Library Type", Stock DESC;
```
Zero Basic rows (5.23k is an E96 precision value, not on the Basic E24 ladder). Top Extended, same Uniroyal 0603WAF family: `C23068` (0603WAF5231T5E), stock 51,539 — selected.

**Query 9 — 30.1kΩ 0603 (R517):**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock FROM parts
WHERE Package='0603' AND Description LIKE '% 30.1kΩ %' ORDER BY "Library Type", Stock DESC;
```
Same pattern as query 8 (E96 value, Extended only): `C23000` (0603WAF3012T5E), stock 74,544 — selected.

**Query 10 — BQ25886RGE (U511):**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock,Manufacturer FROM parts
WHERE "MFR.Part" LIKE '%BQ25886%' ORDER BY Stock DESC;
```
Two rows: `C2765094` (BQ25886RGER, stock 6,948) and `C2864444` (BQ25886RGET, stock 0). The schematic symbol's MPN is `BQ25886RGE`; TI's actual orderable part numbers append a packaging suffix (`R` = tape-and-reel, `T` = small reel) — `BQ25886RGE` alone is not an orderable MPN. `C2765094`/RGER is the in-stock tape-and-reel variant, package `VQFN-24-EP(4x4)` matching the symbol's `Texas_RGE0024H_VQFN-24-1EP_4x4mm` footprint — selected. Datasheet field already carried `https://www.ti.com/lit/ds/symlink/bq25886.pdf` (TI's own page) from Phase-1 capture; left unchanged.

**Basic-0603-resistor ladder enumeration (used by queries 7–9):**
```sql
SELECT "LCSC Part","MFR.Part",Description,Stock FROM parts
WHERE Package='0603' AND "Library Type"='Basic' AND Description LIKE '%Thick Film Resistor%';
```
80 rows returned — the full Basic 0603 E24 decade ladder (0Ω, 1Ω–9.1Ω, 10Ω–91Ω, 100Ω–910Ω [except 750Ω], 1k–9.1k, 10k–91k [except 5.23k], 100k–910k [except 30.1k, 51k exists], 1M, 2M, 10MΩ). Confirms R514/R516/R517 have no Basic option and rules out a typo in the search terms.

**Query 11 — 5.62kΩ 1% 0603, E96 (R515) — PM ruling S1 pass, 2026-09-14:**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock FROM parts
WHERE Package='0603' AND Description LIKE '% 5.62kΩ %' ORDER BY "Library Type", CAST(Stock AS INTEGER) DESC LIMIT 20;
```
Zero `Library Type='Basic'` rows (5.62k is an E96 precision value, same gap pattern as R516/R517 — confirmed by the same Basic-0603-ladder enumeration above, which has no 5.62k entry). 20 Extended rows returned; true numeric-max stock is `C2930113` (FRC0603F5621TS, FOJAN, stock 66,282), but the pick was **`C23188`** (0603WAF5621T5E, Uniroyal, stock 29,745) — the same `0603WAF` Uniroyal family as every other 0603 resistor already on this sheet (R500–R502, R505, R512–R514, R516–R519), consistent with the reasoning already used for R514/R516/R517 above and with the family-consistency precedent the PM accepted for R516/R517 in ruling S3 (`00_pm_brief.md` §3.1: "correct parts, not top-stock rows" — accepted as picked). Second-place by stock within the Uniroyal-adjacent field is irrelevant here since family match, not raw stock, is the deciding criterion once a part is confirmed in stock at the needed quantity (1 per board). `Datasheet` field: `https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF5621T5E_C23188.pdf` (present in the DB row, added per the ruling's explicit instruction — see §7).

## 3. Unresolved / defects / notes

- **R515 (ICHGSET) — resolved by PM ruling S1 (2026-09-14).** Originally left blank: 5.7k is neither an E24 nor an E96 standard value (E24 has 5.6k; E96 has 5.62k and 5.76k, neither of which is "5.7k"), and a catalogue-wide search (no package/library filter) for `% 5.7kΩ %` returned zero SMD rows at any package. The PM authorized the value change (`00_pm_brief.md` §3.1 ruling S1): **R515 5.7k → 5.62k 1% 0603 (E96)**. New ICHG = 5620/3810 = **1.475 A** (was 1.50 A) — the 1.48 A input-current limit set by R514/ILIM dominates either way, so the charger's effective behaviour is unchanged. See §7 for the full re-run (this is the one intentional value/field change the S1 pass makes; `netlist_diff.py` confirms it is the only component-value change project-wide).
- **Q500/Q501 (IRF7458, C10879) stock is thin: 57 units on an Extended MPN-exact match**, needed 2× for this board. Re-verified against the current catalogue snapshot (matches the Phase-1 "verified live" figure of the same order of magnitude); flagged as a scarce-Extended-part supply risk per brief §7 pre-order-procedure item 7 ("buy scarce Extended parts first... stock can reach zero between review and order") — not something this pass can fix, just recorded.
- **Test points (TP500–TP505, TP510–TP512): left exactly as they are, per instructions.** Checked the FC's own TP2/TP6/TP8 symbols on the root sheet (`FlatSat_V1.kicad_sch`, lines 15162–15239, 22661–22735, 20745–20819) — corrected in review-fix pass: TP1 does not exist anywhere in the project (grepped `"Reference" "TP1"` across every `.kicad_sch`, no match; only TP2, TP5 (on `eps_side.kicad_sch`), TP6, TP8 exist project-wide). All three (TP2/TP6/TP8) carry `(in_bom yes) (on_board yes) (in_pos_files yes) (dnp no)` — i.e. the FC convention does **not** exclude test points from BOM/position files, and none carry an LCSC field. This sheet's nine TP500-series symbols already match that (checked `in_bom`/`on_board`/`in_pos_files` on every `Connector:TestPoint` instance in `battery_protection_replica.kicad_sch` — all `yes`, no `dnp yes` anywhere). No change made.
- No package/value mismatches found among the 16 re-verified pre-existing LCSC numbers.

## 4. Datasheet URLs added

**3** parts on this sheet gained a `Datasheet` field (were empty in the Phase-1 final netlist; corrected in review-fix pass — the original report said 4, double-counting U511, whose datasheet field was already present and unchanged, see query 10 above): **J500** (`https://www.lcsc.com/product-detail/C72334.html`, corrected in review-fix pass from the C474953 URL), **JP500** and **JP510** (`https://www.lcsc.com/product-detail/C358684.html`, corrected in review-fix pass from the C7430358 URL, same part both places). U511's datasheet (`https://www.ti.com/lit/ds/symlink/bq25886.pdf`) was already present from Phase-1 capture and is unchanged — it is **not** counted here. Field-diff proof (§5): exactly 3 `Datasheet` additions on this sheet (J500, JP500, JP510), confirmed by comparing the Phase-1 final baseline netlist against the fresh live-project netlist field-by-field. Passive parts (R/C) follow the sheet's existing convention of no `Datasheet` field even when an LCSC is present (matches C500–C503, R500–R502, etc., none of which carry a Datasheet field either before or after this pass) — **R515 is the one deliberate exception**, added in the PM ruling S1 pass (§7) because that ruling's own instruction explicitly calls for a `Datasheet` field "if the DB has one," overriding the sheet's general passive-parts convention for this one part.

## 5. Verification

Re-run in full after the review-fix pass (J500/JP500/JP510 LCSC/Datasheet corrections):

- `python3 tools/sch_lint.py battery_protection_replica.kicad_sch --project FlatSat_V1 --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0 --refdes-block 500-599 --strict` → **0 errors, 0 warnings** (77 symbol instances, 16 lib symbols, 137 wires).
- `tools/harness_erc.sh "Battery Replica and Bench Power"` → sheet-scoped violations: **0 errors**, 16 pre-existing `pin_to_pin` warnings (Unspecified-pin-type connections inherent to the R5460/DZDH0401DW/BQ25886 symbol pin electrical types, unrelated to this pass — same 16 before and after this pass, and unchanged by the review-fix). Project-wide ERC delta vs. the pre-Phase-1 promoted baseline: errors +0 (11/11, unchanged), matching the pattern already documented in the Phase-1 review for this harness (the warning deltas are dominated by the other five sheets referenced in the same harness run, concurrently owned by other agents).
- `tools/netlist_diff.py <Phase-1 final netlist.xml> <fresh netlist from the live, regenerated project>` → **components: base 479, new 479, added 0, removed 0; nets: base 354, new 354, added 0, removed 0, changed 0**. A separate field-by-field diff of `value`/`footprint` across all 479 components confirms **0 value/footprint changes** anywhere in the project. The only field differences are `LCSC Part`/`Datasheet` additions — 11 on this sheet (exactly the refs edited above; `LCSC Part` on all 11, `Datasheet` on 3: J500, JP500, JP510) plus field-only edits made concurrently by the other five sheets' owners in the same parallel workflow (50 field changes on other refs, none touched by this agent).
- Generator reproducibility: ran `tools/gen/battery_protection_replica_gen.py` twice into scratch files after the review-fix edit — byte-identical output (including uuids), and byte-identical to the live `battery_protection_replica.kicad_sch` after regeneration, confirming the uuid stream stayed seeded/deterministic through this edit.

## 6. Files changed

- `FlatSat_V1/tools/gen/battery_protection_replica_gen.py` — added `lcsc=` (11 refs) and `datasheet=` (3 refs: J500, JP500, JP510) keyword arguments to the corresponding `place(...)` calls; review-fix pass corrected J500's LCSC from `C474953`→`C72334` and JP500/JP510's from `C7430358`→`C358684` (and their `Datasheet` URLs to match) after the numeric-sort bug in queries 4/5 was found.
- `FlatSat_V1/battery_protection_replica.kicad_sch` — regenerated from the updated generator (atomic write via the generator's own temp-file+rename), twice (initial pass, then review-fix pass).
- This report — corrected §1/§2 (J500/JP500/JP510 selection + rationale), §3 (dropped the erroneous "TP1" citation), §4 (datasheet-added count 4→3) per verifier findings.

`jlcpcb/project.db` was not touched (out of scope, read-only per hard rule 8). The board (`FlatSat_V1.kicad_pcb`) was not touched (out of scope for this stage; re-synced by the PM afterward per L9).

## 7. PM ruling S1 applied (2026-09-14)

`00_pm_brief.md` §3.1 ruling S1: R515 (BQ25886 ICHGSET) is not an E24/E96 value at 5.7 kΩ and has no catalogue part (see §3's original unresolved note). PM ruling: **change to 5.62 kΩ 1 % 0603 (E96)**.

**What changed:**

| field | before | after |
|---|---|---|
| `Value` | `5.7k` | `5.62k` |
| `LCSC Part` | *(none)* | `C23188` (0603WAF5621T5E, Uniroyal, Extended, stock 29,745 — query 11, §2) |
| `Datasheet` | *(none)* | `https://www.lcsc.com/datasheet/lcsc_datasheet_2206010116_UNI-ROYAL-Uniroyal-Elec-0603WAF5621T5E_C23188.pdf` |
| `Description` | `ICHGSET: ICHG = RICHGSET/KICHGSET = 5700/3810 = 1.50A (datasheet 9.2.2.5)` | `ICHGSET: ICHG = RICHGSET/KICHGSET = 5620/3810 = 1.475A (datasheet 9.2.2.5). PM ruling S1: 5.62k 1% 0603 E96 (was 5.7k, not an E24/E96 value).` |

ICHG = 5620/3810 = **1.475 A** (was 1.50 A). The BQ25886's active input-current limit is still the lower of the D+/D− DCP result and the ILIM pin (R514 = 750 Ω → 1.48 A, §6/§9.2.2.4), so the 0.025 A drop in the charge-current setpoint has no effect on the charger's actual behaviour on this bench — the sheet's own text note (BQ25886 block) now says so explicitly.

**On-sheet text note updated** (the note quoting `ICHG = RICHGSET/KICHGSET`, in the BQ25886 block): now reads `R515 = 5.62k -> ICHG = RICHGSET/KICHGSET = 5620/3810 = 1.475 A (9.2.2.5), pre-charge/term ICHG/10.  PM ruling S1: 5.7k was not E24/E96; 5.62k 1% E96 fitted (1.48 A ILIM still dominates).`

**Proof (re-run after this pass):**

```
$ python3 tools/sch_lint.py battery_protection_replica.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0 --refdes-block 500-599
battery_protection_replica.kicad_sch: 77 symbol instances, 16 lib symbols, 137 wires, 0 errors, 0 warnings
```

```
$ SCRATCH=.../scratchpad/fix_s1 tools/harness_erc.sh "Battery Replica and Bench Power"
=== violations on sheets matching 'Battery Replica and Bench Power' ===
warning  pin_to_pin                       16
total 16
errors: 0
```
Sheet-local violations: 16 `pin_to_pin` warnings, 0 errors — identical set and count to §5's pre-ruling baseline (all pre-existing library-metadata warnings on `flatsat:R5460N208AA`/`easyeda2kicad:*` pins, unrelated to R515). Project-wide: 11 errors (unchanged FC baseline, all on other sheets), +0 new errors anywhere.

`tools/netlist_diff.py tools/baseline/netlist_phase1.kicadxml <fresh netlist>`: only two components changed project-wide, `R515` (this ruling) and `SW600` (PM ruling S2, applied in the same pass on `pyro_inhibit.kicad_sch` — see `supply_pyro_inhibit.md` §7); 0 components added/removed; the only net-membership changes are SW600's (this sheet's own nets — `Dir_Chrg_In`, `B-`, `GND`, `CHG_SYS`, `CHG_BAT`, etc. — are all byte-identical in membership before/after, confirming R515 is a field/value change with **zero netlist impact**, as expected for a same-footprint same-net passive value swap).

**Generator reproducibility:** ran `tools/gen/battery_protection_replica_gen.py` twice after this edit — byte-identical output (including uuids), and byte-identical to the live `battery_protection_replica.kicad_sch`.

**Readability check:** `tools/gen/battery_protection_replica_textcheck.py battery_protection_replica.kicad_sch --wires --bodies` first flagged two collisions this ruling introduced: R515's `Value` text ("5.62k", one character wider than "5.7k") ran onto U511's body outline (the gap between R515's own body and U511's is only 6.6 mm, tight even for the old value), and the rewritten on-sheet ICHG note line ran 1.6 mm past the A3 frame's right keep-in edge (188 characters at size 1.27 — the note text convention on this sheet is a single un-wrapped line per list entry, no auto-wrap). Fixed by nudging R515's `val_at` from `(297.18, 90.17)` to `(296.2, 90.17)` (re-centring the value in the available gap) and trimming the note line to 178 characters (dropped "was"/"still", kept every fact). Re-run: `0 collisions, 224 text items, 179 symbol bodies` (one pre-existing, unrelated `TP512.Reference` on-own-body info note, unchanged by this pass). Confirmed visually in a `kicad-cli sch export pdf` render of the full 6-sheet harness project at 400 dpi.

**Files changed (this pass):**

- `FlatSat_V1/tools/gen/battery_protection_replica_gen.py` — R515's `place(...)` call: `Value` `5.7k`→`5.62k`, added `lcsc='C23188'` and `datasheet=...`, updated `description=...`; updated the on-sheet BQ25886 text note's R515/ICHG line.
- `FlatSat_V1/battery_protection_replica.kicad_sch` — regenerated from the updated generator (atomic `.tmp` + rename).
- This report — updated the R515 row (§1), added query 11 (§2), resolved the §3 "unresolved" note, updated §4's datasheet-exception note, added this §7.

**PM ruling S1 applied.**
