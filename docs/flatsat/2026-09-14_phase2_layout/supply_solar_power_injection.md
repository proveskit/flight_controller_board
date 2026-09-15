# Supply chain — Solar Power Injection (refdes 400–449)

**Sheet:** `FlatSat_V1/solar_power_injection.kicad_sch` · **Generator:** `FlatSat_V1/tools/gen/solar_power_injection_gen.py`
**Stage:** Phase 2 stage 1, supply chain · **Date:** 2026-09-14 · **Owner:** Sonnet (one-agent-one-sheet)

11 symbols total (two identical CH-A/CH-B injection chains + one shared VSOLAR test point). All 11 are in the netlist's `/Solar Power Injection/` sheetpath; no other symbols (power symbols `#PWR`/`#FLG` are schematic-only, not netlist components).

## Parts table

| Ref | Value | Footprint | LCSC | MPN | Lib Type | Stock | Price (1pc) | Source |
|---|---|---|---|---|---|---|---|---|
| F400 | 1.85A_PTC_33V | Fuse:Fuse_2920_7451Metric | **C207086** (pre-existing, re-verified) | Littelfuse 2920L185DR | Extended | 14,433 | $0.231 | `SELECT * FROM parts WHERE "LCSC Part"='C207086'` → row matches: package `2920` = footprint `Fuse_2920_7451Metric`, MFR.Part `2920L185DR` = symbol value; **confirmed, no mismatch** |
| F401 | 1.85A_PTC_33V | Fuse:Fuse_2920_7451Metric | **C207086** (pre-existing, re-verified) | Littelfuse 2920L185DR | Extended | 14,433 | $0.231 | same query/row as F400 |
| D400 | CDBA240LL-HF | Diode_SMD:D_SMA | **C2886093** (pre-existing, re-verified) | Comchip CDBA240LL-HF | Extended | 42,394 | $0.307 | `SELECT * FROM parts WHERE "LCSC Part"='C2886093'` → row matches: package `SMA(DO-214AC)` = footprint `D_SMA`, MFR.Part `CDBA240LL-HF` = symbol value; **confirmed, no mismatch** |
| D401 | CDBA240LL-HF | Diode_SMD:D_SMA | **C2886093** (pre-existing, re-verified) | Comchip CDBA240LL-HF | Extended | 42,394 | $0.307 | same query/row as D400 |
| J400 | Terminal_2P_5.08mm | TerminalBlock_Phoenix:…_1x02_P5.08mm_Horizontal | **C8409** (filled) | Ningbo Kangnex WJ2EDGKA-5.08-02P-14-00A | Extended | 9,409 | $0.289 | `SELECT ... FROM parts WHERE Description LIKE '%5.08mm%' AND '%1x2P%' AND '%Horizontal Termination%'` (excludes right-angle/socket variants) ORDER BY Stock DESC → top row `C8409`, highest-stock straight/through-hole 5.08 mm 2‑pin screw terminal, plug (male) side matching the footprint's board-mount orientation |
| J401 | Terminal_2P_5.08mm | TerminalBlock_Phoenix:…_1x02_P5.08mm_Horizontal | **C8409** (filled) | Ningbo Kangnex WJ2EDGKA-5.08-02P-14-00A | Extended | 9,409 | $0.289 | same query/row as J400 |
| JP400 | Jumper_2_Open | Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical | **C492401** (filled) | XFCN PZ254V-11-02P | Extended | 1,222,203 | $0.018 | `SELECT ... FROM parts WHERE "Second Category"='Pin Headers' AND Description LIKE '%1x2P%' AND '%2.54mm%'` excluding Right Angle/SMD, ORDER BY Stock DESC → top row `C492401`, straight THT 2.54 mm 2‑pin header, by far the highest-stock match |
| JP401 | Jumper_2_Open | Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical | **C492401** (filled) | XFCN PZ254V-11-02P | Extended | 1,222,203 | $0.018 | same query/row as JP400 |
| TP400 | VSOLAR_BENCH_A | TestPoint:TestPoint_Pad_D1.5mm | — (no LCSC, by convention) | — | — | — | — | test point, see below |
| TP401 | VSOLAR | TestPoint:TestPoint_Pad_D1.5mm | — (no LCSC, by convention) | — | — | — | — | test point, see below |
| TP402 | VSOLAR_BENCH_B | TestPoint:TestPoint_Pad_D1.5mm | — (no LCSC, by convention) | — | — | — | — | test point, see below |

No Basic-library part exists in the catalogue for either the 5.08 mm screw-terminal package or the 2.54 mm 1x02 THT pin-header package (`SELECT DISTINCT "Library Type" FROM parts WHERE "Second Category"='Pin Headers'` returns only `Extended`; the 5.08 mm terminal-block search returned zero `Library Type='Basic'` rows either). Both chosen parts are the highest-stock Extended rows that match the footprint's pin count, pitch, and mounting orientation (straight/through-hole, not right-angle or SMD), per the brief's fallback rule.

## Unresolved parts

None on this sheet. All 11 symbols have a resolved LCSC/no-LCSC status.

## Test-point handling

Checked the FC's own `Connector:TestPoint` instances (TP2 on `FC_V5e_Production_Rev2.kicad_sch`, TP5/TP6/TP8 on `FC_V5e_Production_Rev2/eps_side.kicad_sch` and root): none carry an `LCSC Part` property, and all have `(in_bom yes) (in_pos_files yes) (dnp no)` — i.e. the FC does **not** exclude test points from BOM/position files. TP400/TP401/TP402 on this sheet already match that convention exactly (no LCSC field, `in_bom yes`, `in_pos_files yes`, `dnp no` — unchanged by this pass). No sheet or generator edit was needed for the test points; left as-is per the FC convention.

## Datasheet URLs added

2 non-passive parts got a new/updated Datasheet URL as part of filling their LCSC (both were previously blank or pointed at a generic manufacturer page rather than the part actually being sourced):

- **J400/J401** (same part, 2 refs): Datasheet changed from the generic Phoenix Contact MKDS-1,5-2-5.08 product page to the JLC-hosted datasheet for the part actually sourced: `https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/1912251633_Ningbo-Kangnex-Elec-WJ2EDGKA-5-08-2P_C8409.pdf`. Description updated to note the footprint is Phoenix-MKDS-compatible but the sourced part is Kangnex WJ2EDGKA (LCSC C8409).
- **JP400/JP401** (same part, 2 refs): Datasheet filled (was empty) with `https://www.lcsc.com/datasheet/lcsc_datasheet_2409302300_XFCN-PZ254V-11-02P_C492401.pdf`. Description updated to note the sourced part, XFCN PZ254V-11-02P (LCSC C492401).

F400/F401 and D400/D401 already carried correct manufacturer datasheet URLs from Phase 1 (Littelfuse and LCSC product-page links respectively); re-verified against the database row, unchanged.

Total: **4 symbol instances** (2 distinct parts, J400/J401 and JP400/JP401) got a Datasheet field change; **0** parts required an MPN field (this generator has no separate MPN property — MPN is folded into the `Description` field, matching every other part on this sheet, e.g. F400/F401's existing "Littelfuse 2920L185DR" wording).

## Re-verified (pre-existing LCSC)

| Ref | LCSC | Package match | Value match | Result |
|---|---|---|---|---|
| F400/F401 | C207086 | `2920` = `Fuse:Fuse_2920_7451Metric` | `2920L185DR` = `1.85A_PTC_33V` | OK, no defect |
| D400/D401 | C2886093 | `SMA(DO-214AC)` = `Diode_SMD:D_SMA` | `CDBA240LL-HF` = `CDBA240LL-HF` | OK, no defect |

Neither part shows a package/value mismatch; both remain unchanged in the sheet and generator.

## Changes applied

The generator's `build_channel()` function (`tools/gen/solar_power_injection_gen.py`) now sets:
- `term = Part(..., lcsc='C8409', datasheet=<JLC pdf>, description=<updated>)` for J400/J401
- `jump = Part(..., lcsc='C492401', datasheet=<JLC pdf>, description=<updated>)` for JP400/JP401

Regeneration reproduces the live sheet byte-for-byte (verified: `python3 tools/gen/solar_power_injection_gen.py --out <scratch>` diffed against the committed `solar_power_injection.kicad_sch` with zero differences), and the deterministic uuid seed (`flatsat-solar_power_injection-2026-09-14`) was left untouched, so the emitted uuids are identical to the pre-existing sheet — nothing to orphan for a later layout stage.

## Verification

- `tools/sch_lint.py solar_power_injection.kicad_sch --project FlatSat_V1 --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/88d5f13b-6a4a-4f50-805f-872821082e52 --refdes-block 400-449 --strict` → `17 symbol instances, 8 lib symbols, 24 wires, 0 errors, 0 warnings`
- `tools/harness_erc.sh "Solar Power Injection"` → `violations on sheets matching 'Solar Power Injection': total 0, errors: 0` (project-wide ERC delta vs the pre-Phase-1 baseline is unchanged by this pass — the harness's default baseline predates all six Phase-1 sheets, so it necessarily shows all Phase-1 content as "new"; the sheet-scoped violation count, which is what this stage can affect, is 0)
- `tools/netlist_diff.py <Phase-1 final netlist.xml> <fresh kicad-cli netlist export of the live project>` → `components: base 479, new 479, added 0, removed 0` / `nets: base 354, new 354` / `added nets (0): removed nets (0): changed nets (0):`
- Per-ref Value/Footprint comparison (base netlist vs. fresh netlist) for all 11 refs on this sheet: identical in every case — only `LCSC Part`, `Datasheet`, `Description` fields changed, exactly as the hard rule requires.

## Files changed

- `FlatSat_V1/solar_power_injection.kicad_sch` (field-only edit, applied atomically via `.tmp` + `mv`)
- `FlatSat_V1/tools/gen/solar_power_injection_gen.py` (mirrors the same field edits in the generator's part table so a regeneration reproduces the sheet)
