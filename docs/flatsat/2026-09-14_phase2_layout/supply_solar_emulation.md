# Supply chain — Sheet 8 "Solar and Sensor Emulation" (refdes 300–399)

**Date:** 2026-09-14 · **Owner:** Sonnet supply-chain agent (Phase 2, stage 1) · **Sheet file:** `FlatSat_V1/solar_emulation.kicad_sch` · **Generator:** `FlatSat_V1/tools/gen/solar_emulation_gen.py` · **Source:** `~/Documents/KiCad/10.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/parts-fts5.db` (refreshed 2026-09-13, `fts5` trigram table `parts`)

## Summary

69 symbols on this sheet (69 refdes: BATT/TOP + 5 emulated-face TCA4311A channels + Face-0 real reference silicon + 7 test points). Two were blank on entry (**J300**, **R304**); both are now filled with an LCSC number from the parts database. The seven TP300–306 test points stay LCSC-blank, matching the FC's own TP1/TP2/TP6/TP8 convention on the root sheet (checked directly — see §3). All nine distinct non-blank LCSC numbers already on the sheet (C1525, C15195, C52923, C25744, C25900, C130025, C28927, C3678616, C527464) were re-queried against the database and their package/value agree with the schematic; none is a defect. One Datasheet URL was added (J300); the ICs already carried Datasheet URLs from Phase 1 capture.

Proof: `sch_lint.py` 0 errors / 0 warnings; `tools/harness_erc.sh "Solar and Sensor Emulation"` shows 0 errors on this sheet (52 pre-existing `pin_to_pin` warnings, unchanged by this pass — the harness baseline predates all six Phase-1 sheets, so its delta is not zero project-wide, but nothing on this sheet is new); `netlist_diff.py` against the Phase-1 final netlist shows **0 added/removed/changed nets, 0 component value/footprint changes** — every edit was field-only (LCSC Part + Datasheet on 2 refs).

## 1. Newly filled (were blank)

| Ref | Value | Footprint | LCSC | MPN | Lib type | Stock | Price (1pc) | Source |
|---|---|---|---|---|---|---|---|---|
| **R304** | 43R | `Resistor_SMD:R_2010_5025Metric` | **C7467404** | FRC2010F43R0TS | Extended | 9,737 | $0.019 | DB query: `MATCH 'Package:2010 "MFR.Part":43R0'`, highest-stock ±1% 750 mW row (no Basic 43 Ω/2010 part exists in the catalogue — every 43 Ω 2010 row is Extended). 750 mW rating matches the generator's own derating note (0.253 W worst case = 34 % of rating). |
| **J300** | Coil Out | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | **C492401** | PZ254V-11-02P | Extended | 1,222,203 | $0.018 | DB query: `MATCH '"Second Category":"Pin Header"'`, filtered in Python for `1*2P`, `2.54`, `Through Hole`; highest-stock straight (vertical) 1×2P 2.54 mm male header (no Basic 2.54 mm headers exist in the catalogue at all — 0 rows with `Library Type='Basic'` under Pin Headers). Datasheet URL added: `https://www.lcsc.com/datasheet/lcsc_datasheet_2409302300_XFCN-PZ254V-11-02P_C492401.pdf`. |

## 2. Re-verified (already had an LCSC number)

Every distinct LCSC value used on the sheet was re-queried (`SELECT ... FROM parts WHERE parts MATCH ? AND "LCSC Part"=?`) and checked against the schematic's Value/Footprint. All agree — no defects found on this sheet.

| LCSC | MPN | Package | Lib type | Description (DB) | Stock | Used on (refs) |
|---|---|---|---|---|---|---|
| C1525 | CL05B104KO5NNNC | 0402 | Basic | 100nF 16V X7R ±10% | 33,327,481 | C300, C302, C303, C310, C311, C312, C313, C314, C315, C316 |
| C15195 | CL05B103KB5NNNC | 0402 | Basic | 10nF 50V X7R ±10% | 5,949,302 | C301 |
| C52923 | CL05A105KA5NQNC | 0402 | Basic | 1uF 25V X5R ±10% | 9,480,732 | C304 |
| C25744 | 0402WGF1002TCE | 0402 | Basic | 10kΩ ±1% ±100ppm/°C | 29,737,515 | R300, R301, R302, R303, R310, R311, R320, R321, R330, R331, R340, R341, R350, R351, R360, R370, R371 |
| C25900 | 0402WGF4701TCE | 0402 | Basic | 4.7kΩ ±1% ±100ppm/°C | 18,365,039 | R312, R313, R314, R322, R323, R324, R332, R333, R334, R342, R343, R344, R352, R353, R354, R362, R363, R372, R373, R374 |
| C130025 | TCA4311ADGKR | MSOP-8 | Extended | TCA4311A hot-swap I2C buffer | 2,691 | U300, U310, U311, U312, U313, U314, U315, U316 |
| C28927 | TMP112AIDRLR | SOT-563 | Extended | TMP112 temperature sensor, I2C | 47,727 | U301 |
| C3678616 | VEML6031X00 | SMD-6P | Extended | VEML6031X00 ambient light sensor, I2C | 519 | U302 |
| C527464 | DRV2605LDGSR | VSSOP-10-0.5mm | Extended | DRV2605L haptic driver, I2C | 2,442 | U303 |

Note on U303: the JLC catalogue lists C527464's land as `VSSOP-10-0.5mm`; the schematic/generator footprint is `Package_SO:TSSOP-10_3x3mm_P0.5mm` — a deliberate Phase-1 integrator substitution (documented in `solar_emulation_gen.py` `LIB_FIXUPS`/comments: KiCad 10's `Package_SO:VSSOP-10_3x3mm_P0.5mm` footprint was removed from the library, so the schematic was pointed at the TSSOP-10 land as "the same 3×3 mm, 0.5 mm-pitch, 10-pin, no-thermal-pad footprint"). That substitution predates this stage, is not an LCSC/Datasheet field, and footprint changes are outside this stage's mandate (netlist diff must show 0 footprint changes) — flagged here for the owner's awareness, not altered.

## 3. Test points (TP300–TP306)

Brief L9 and the hard rules: test points get no LCSC, and are excluded from BOM/position only if the FC's own TP symbols are. I checked the FC's own TP2, TP6, TP8 instances on the root sheet (`FlatSat_V1.kicad_sch`) directly:

```
(symbol (lib_id "Connector:TestPoint") ...
  (in_bom yes) (on_board yes) (in_pos_files yes) (dnp no)
  ... no "LCSC Part" property at all ...
```

All three (TP2, TP6, TP8) are `in_bom yes`, `on_board yes`, `in_pos_files yes`, and carry no LCSC Part field. TP300–306 on this sheet already match exactly that pattern (verified with `grep` around each `Reference "TP30x"` block: `in_bom yes` / `in_pos_files yes` on every one, no LCSC Part property). **No change made** — they were already correct per the FC convention, so nothing needed touching.

| Ref | Net probed | Footprint | LCSC | Notes |
|---|---|---|---|---|
| TP300 | F0_PWR | `TestPoint:TestPoint_Pad_D1.5mm` | — | in_bom/in_pos_files yes (FC convention) |
| TP301 | F1_PWR | same | — | same |
| TP302 | F2_PWR | same | — | same |
| TP303 | F3_PWR | same | — | same |
| TP304 | F4_PWR | same | — | same |
| TP305 | F5_PWR | same | — | same |
| TP306 | +3V3 | same | — | same |

## 4. Unresolved

None. Every non-test-point part on this sheet (62 of 69 refs) now carries an LCSC number; the remaining 7 are the test points, correctly left LCSC-blank per §3.

## 5. Datasheet URLs added

| Ref | URL |
|---|---|
| J300 | `https://www.lcsc.com/datasheet/lcsc_datasheet_2409302300_XFCN-PZ254V-11-02P_C492401.pdf` |

(U300/U310–U316, U301, U302, U303 already carried Datasheet URLs from Phase-1 capture — ti.com and vishay.com links, unchanged. R304 is a passive; no Datasheet URL added, consistent with every other resistor on the sheet.)

## 6. How the fields were applied

Both changed fields were added inside `tools/gen/solar_emulation_gen.py` (the `R304` call to `res(...)` in `face0()`, and the `J300` `props` dict passed to `sh.sym(...)`), then the sheet was regenerated with `python3 tools/gen/solar_emulation_gen.py` (writes atomically, tmp + `os.replace`, inside the generator itself). A `--out` dry run to the scratch directory, diffed against the previously-live sheet with `uuid` lines stripped, showed only the two intended `LCSC Part`/`Datasheet` property blocks changing — confirming the generator's uuid stream is still deterministic and the regeneration is otherwise byte-identical.

## 7. Verification

- `python3 tools/sch_lint.py solar_emulation.kicad_sch --project FlatSat_V1 --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/0ec7a68a-65de-4eda-8407-9dcf20e51c0b --refdes-block 300-399 --strict` → `101 symbol instances, 10 lib symbols, 191 wires, 0 errors, 0 warnings`
- `tools/harness_erc.sh "Solar and Sensor Emulation"` → sheet-scoped section: `52 pin_to_pin warnings, 0 errors` (all 52 are pre-existing Phase-1 Unspecified/Bidirectional-pin-type warnings inherent to the TCA4311A/mux symbols, unrelated to this stage's field-only edits; the harness's own baseline predates all six Phase-1 sheets so its whole-project delta is not zero, but nothing new appears on this sheet)
- `tools/netlist_diff.py <phase1 final netlist.xml> <fresh kicad-cli netlist>` → `components: base 479, new 479, added 0, removed 0`; `nets: base 354, new 354`; `added nets (0)`; `removed nets (0)`; `changed nets (0)` — field-only change proven project-wide (the fresh netlist was exported from the whole `FlatSat_V1.kicad_sch` root, so this also confirms no other sheet was touched).
