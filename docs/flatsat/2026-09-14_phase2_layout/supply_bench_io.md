# Supply chain — Bench IO (refdes 700–799)

**Date:** 2026-09-14 · **Owner:** Sonnet agent, Phase 2 stage 1 (supply chain) · **Sheet:** `FlatSat_V1/bench_io.kicad_sch` · **Generator:** `FlatSat_V1/tools/gen/bench_io_gen.py` · **Brief:** `00_pm_brief.md` §3 L9, §4 rule 5

Database: `~/Documents/KiCad/10.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/parts-fts5.db`, table `parts` (fts5, trigram tokenizer — plain `LIKE`/`=` on columns works; `MATCH` phrase queries were unreliable for short numeric/symbol tokens, so `LIKE`/`=` was used throughout below). 21 symbols total on this sheet (all in sheetpath `/Bench IO/`); 5 had a blank `LCSC Part`, 9 already had one (all re-verified), 1 (TP701) is a test point with no LCSC by convention, 6 are `#PWR`/`#FLG` power symbols (no LCSC/BOM part).

## 1. Full part table

| Ref | Value | Footprint | LCSC | MPN | Lib Type | Stock | Price (¥, 1pc break) | Source |
|---|---|---|---|---|---|---|---|---|
| J701 | USB_C_Receptacle_USB2.0_16P | Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12 | C165948 | TYPE-C-31-M-12 | Extended | 243,870 | — | **Pre-existing, re-verified** (query 2 below): MFR.Part/package match |
| J702 | SWD | Connector_JST:JST_SH_BM03B-SRSS-TB_1x03-1MP_P1.00mm_Vertical | C160389 | BM03B-SRSS-TB(LF)(SN) | Extended | 37,157 | — | **Pre-existing, re-verified**: MFR.Part/package match |
| J703 | Bench Header | Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical | **C492422** | PZ254V-12-10P | Extended | 108,087 | 1-9999:0.13 (typ.) | **New** (query 4 below): 2×5P, 2.54 mm, through-hole pin header, highest-stock exact match |
| C701 | 10uF | Capacitor_SMD:C_0805_2012Metric | **C2182156** | EMK212BB7106KG-T (Taiyo Yuden) | Extended | 82,290 | 1-9999:0.06 (typ.) | **New** (query 5 below): 10 µF, 16 V, X7R, 0805 — matches the symbol's "X7R 16V" description exactly; no Basic part exists at this value/voltage/dielectric/package |
| Q701 | BSS138 | Package_TO_SOT_SMD:SOT-23 | **C78284** | BSS138 | Extended | 212,211 | 1-199:0.023 | **New** (query 3 below): exact MPN match, SOT-23, highest stock of all BSS138 SOT-23 rows |
| Q702 | BSS138 | Package_TO_SOT_SMD:SOT-23 | **C78284** | BSS138 | Extended | 212,211 | 1-199:0.023 | same as Q701 |
| Q703 | BSS138 | Package_TO_SOT_SMD:SOT-23 | **C78284** | BSS138 | Extended | 212,211 | 1-199:0.023 | same as Q701 |
| R701 | 5.1k | Resistor_SMD:R_0402_1005Metric | C25905 | 0402WGF5101TCE | Basic | 7,547,316 | — | **Pre-existing, re-verified**: 5.1kΩ 0402 ±1%, match |
| R702 | 5.1k | Resistor_SMD:R_0402_1005Metric | C25905 | 0402WGF5101TCE | Basic | 7,547,316 | — | same as R701 |
| R703 | 22 | Resistor_SMD:R_0402_1005Metric | C25092 | 0402WGF220JTCE | Basic | 6,703,051 | — | **Pre-existing, re-verified**: 22Ω 0402 ±1%, match |
| R704 | 22 | Resistor_SMD:R_0402_1005Metric | C25092 | 0402WGF220JTCE | Basic | 6,703,051 | — | same as R703 |
| R705 | 1k | Resistor_SMD:R_0402_1005Metric | C11702 | 0402WGF1001TCE | Basic | 12,881,369 | — | **Pre-existing, re-verified**: 1kΩ 0402 ±1%, match |
| R706 | 4.7k | Resistor_SMD:R_0402_1005Metric | C25900 | 0402WGF4701TCE | Basic | 18,365,039 | — | **Pre-existing, re-verified**: 4.7kΩ 0402 ±1%, match |
| R707 | 1k | Resistor_SMD:R_0402_1005Metric | C11702 | 0402WGF1001TCE | Basic | 12,881,369 | — | same as R705 |
| R708 | 4.7k | Resistor_SMD:R_0402_1005Metric | C25900 | 0402WGF4701TCE | Basic | 18,365,039 | — | same as R706 |
| R709 | 1k | Resistor_SMD:R_0402_1005Metric | C11702 | 0402WGF1001TCE | Basic | 12,881,369 | — | same as R705 |
| R710 | 4.7k | Resistor_SMD:R_0402_1005Metric | C25900 | 0402WGF4701TCE | Basic | 18,365,039 | — | same as R706 |
| SW701 | KMR2 | FC_DEV_BOARD:BTN_KMR2_4.6X2.8 | C72443 | KMR221GLFS | Extended | 9,073 | — | **Pre-existing, re-verified**: SMD 4.6×2.8mm tact, match |
| SW702 | KMR2 | FC_DEV_BOARD:BTN_KMR2_4.6X2.8 | C72443 | KMR221GLFS | Extended | 9,073 | — | same as SW701 |
| SW703 | SS12D10G4 | easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4 | C2887259 | SS12D10G4 071 | Extended | 28,409 | — | **Pre-existing, re-verified**: SPDT slide switch, THT, match |
| TP701 | VBUS_EMU | TestPoint:TestPoint_Pad_D1.5mm | *(none)* | — | — | — | — | Test point — see §3 |

`#PWR701–#PWR718`, `#FLG701` (power symbols) have no LCSC/BOM footprint and are out of scope.

## 2. Queries run (verbatim, against `parts-fts5.db`)

**Query 1 — re-verify the 9 pre-existing LCSC numbers:**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Stock,Description FROM parts
WHERE "LCSC Part" IN ('C165948','C160389','C25905','C25092','C11702','C25900','C72443','C2887259');
```
Result rows: all 8 distinct LCSC values returned exactly one row each; `MFR.Part`/`Package` in every row is consistent with the symbol's Value/Footprint (checked by hand, see table above — resistor values/packages match, connector/switch part numbers match the description text in the netlist). **No mismatches found; none of the 8 flagged-for-re-verification numbers project-wide turned out to be on this sheet, but all 9 LCSC numbers present on Bench IO were re-checked anyway per the task instructions and confirmed correct.**

**Query 2 — BSS138 (Q701/Q702/Q703), exact MPN match, SOT-23 package, ranked by stock:**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Stock,Manufacturer,Datasheet,Description FROM parts
WHERE "MFR.Part"='BSS138' ORDER BY Stock DESC;
```
No `Library Type='Basic'` row exists for BSS138 in any package (checked separately: `SELECT ... WHERE parts MATCH '"BSS138"' AND "Library Type"='Basic'` returns 0 rows) — this is an Extended-only part in the catalogue. Top row: `C78284`, MFR.Part `BSS138`, Package `SOT-23`, Manufacturer Jiangsu Changjing Electronics Technology Co., Ltd., stock 212,211 — selected.

**Query 3 — 2×5P 2.54 mm through-hole pin header (J703):**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Stock,Description FROM parts
WHERE "Second Category"='Pin Headers' AND Description LIKE '%2x5P%' AND Description LIKE '%2.54mm%'
  AND Description LIKE '%Through Hole%' ORDER BY CAST(Stock AS INTEGER) DESC;
```
No Basic-library pin headers exist at all in the catalogue (`SELECT ... WHERE "Second Category"='Pin Headers' AND "Library Type"='Basic'` returns 0 rows) — connectors of this kind are Extended-only at JLC. Top row: `C492422`, MFR.Part `PZ254V-12-10P`, Package `Plugin,P=2.54mm`, stock 108,087 — selected (matches `PinHeader_2x05_P2.54mm_Vertical`: 10-pin, 2×5, 2.54 mm pitch, through-hole).

**Query 4 — 10 µF 0805 X7R 16 V (C701):**
```sql
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Stock,Description FROM parts
WHERE parts MATCH '"10uF" "X7R"' AND Package LIKE '0805%' ORDER BY "Library Type" ASC, Stock DESC;
```
(Checked separately that no Basic 10 µF/0805 part meets the X7R+16V spec: the only two Basic 0805 10µF rows found, `C15850` and `C440198`, are X5R 25V/50V, not X7R 16V as the symbol's Description explicitly calls for.) Selected `C2182156`, MFR.Part `EMK212BB7106KG-T` (Taiyo Yuden), 10µF 16V X7R ±10%, stock 82,290 — best-stock exact match to the required dielectric/voltage.

## 3. Test points

TP701 (VBUS_EMU) follows the FC's own convention, confirmed by inspecting the three `Connector:TestPoint` instances on the root sheet `FlatSat_V1.kicad_sch` (TP2 and two others): all have `(in_bom yes) (on_board yes) (in_pos_files yes) (dnp no)` and no `LCSC Part` field. TP701 in `bench_io.kicad_sch` already matched this exactly before this pass (`in_bom yes / on_board yes / in_pos_files yes / dnp no`, no LCSC). **No change made** — left as-is per the instruction to only add exclude flags if the FC's own TP symbols do, which they do not.

## 4. Datasheet URLs added

Per L9, Datasheet URLs were added to the non-passive parts on this sheet that had a blank `Datasheet` field (5 of them; the already-populated ones — Q701–Q703's onsemi BSS138 datasheet and SW703's LCSC-hosted datasheet — were left untouched as authoritative/already-correct):

| Ref | Datasheet URL added |
|---|---|
| J701 | `https://www.lcsc.com/datasheet/lcsc_datasheet_2205251630_Korean-Hroparts-Elec-TYPE-C-31-M-12_C165948.pdf` |
| J702 | `https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_JST-BM03B-SRSS-TB-LF-SN_C160389.pdf` |
| J703 | `https://www.lcsc.com/datasheet/lcsc_datasheet_2003191006_XFCN-PZ254V-12-10P_C492422.pdf` |
| SW701 | `https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_C-K-KMR221GLFS_C72443.pdf` |
| SW702 | `https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_C-K-KMR221GLFS_C72443.pdf` |

C701 (a passive) was left without a Datasheet field, consistent with every other passive on this sheet (resistors carry none either) — datasheet URLs are for the 24 non-passive parts project-wide per L9, not passives.

Also, while adding Q701–Q703's LCSC number, the trailing "(needs LCSC)" was dropped from their `Description` field (now reads "…open-drain bench driver" — the parenthetical was a TODO note, not part of the actual description) in both the generator and the regenerated sheet.

## 5. Unresolved parts

None on this sheet. All 21 symbols are resolved: 15 already had a confirmed-correct LCSC, 5 blanks were filled, 1 (TP701) is correctly LCSC-less by the FC test-point convention.

## 6. Changes applied

Edited `tools/gen/bench_io_gen.py` (table/`add_symbol` call arguments only — no geometry, wiring, or pin changes):
- `C701`: added `lcsc='C2182156'`
- `J703`: added `lcsc='C492422'` and `datasheet=...`
- `Q701`/`Q702`/`Q703` (via `add_driver()`): added `lcsc='C78284'`, trimmed the description's "(needs LCSC)" note
- `J701`: added `datasheet=...` (was `datasheet=''`)
- `J702`: added `datasheet=...`
- `SW701`/`SW702` (via `add_button()`): added `datasheet=...`

Then ran `python3 tools/gen/bench_io_gen.py` to regenerate `bench_io.kicad_sch` atomically (`.tmp` + `os.replace`). Regenerated a second time into a scratch copy and diffed byte-for-byte against the live file — identical (the seeded uuid4 stream is unaffected by field-only changes, confirming the generator stays uuid-stable).

## 7. Verification

- **`sch_lint.py`**: `python3 tools/sch_lint.py bench_io.kicad_sch --project FlatSat_V1 --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/54b8f29e-9dcb-4e24-99b9-415a110b338a --refdes-block 700-799` → `39 symbol instances, 12 lib symbols, 66 wires, 0 errors, 0 warnings`.
- **`harness_erc.sh bench_io`**: ERC delta vs the promoted baseline is **+0** (`pin_not_connected 5/5 +0`, `power_pin_not_driven 6/6 +0`, total 11 unchanged pre-existing baseline items, none attributable to Bench IO); **0 violations** on sheets matching `bench_io`.
- **`netlist_diff.py`** (Phase-1 final netlist vs a fresh `kicad-cli sch export netlist --format kicadxml` of the live, regenerated project): `components: base 479, new 479, added 0, removed 0`; `nets: base 354, new 354`; **added nets (0), removed nets (0), changed nets (0)**; no `~ ref: (value,footprint) -> (value,footprint)` lines printed, i.e. **0 component value/footprint changes**. Field-only diff confirmed.

## 8. Risks / notes

- BSS138 and the 2×5P 2.54mm pin header have no Basic-library option at JLC at all (verified above) — both will place as Extended parts; stock is very high on the selected LCSC numbers (212k and 108k respectively) so this is a cost/placement-fee consideration for the owner, not a stock risk.
- C701's 10µF/16V/X7R/0805 combination also has no Basic option; the selected Extended part (C2182156, Taiyo Yuden EMK212BB7106KG-T) has 82,290 in stock.
