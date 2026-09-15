# Supply chain — Emulator MCU (refdes 200–299)

**Date:** 2026-09-14 · **Owner:** Sonnet agent, sheet "Emulator MCU" (`FlatSat_V1/emulator_mcu.kicad_sch`, generator `tools/gen/emulator_mcu_gen.py`) · **Stage:** Phase 2 §7 stage 1 (supply chain)

## Summary

All 47 symbols on this sheet were parsed from the Phase-1 final netlist
(`sheetpath` / `Sheetfile` = `emulator_mcu.kicad_sch`). **43 of 47 already carried an
LCSC number** at Phase-1 hand-off (documented in
`docs/flatsat/2026-09-14_phase1_schematic/sheet_emulator_mcu.md` §6.4 as FC-parity
sticks, one as-ordered BOM retune, and one live-verified part). This agent's job was
therefore mostly **re-verification**, not sourcing: every existing LCSC number was
re-queried against `parts-fts5.db` (refreshed 2026-09-13) and its package/value
checked against the symbol. **0 mismatches found; 0 LCSC numbers changed.**

The only outstanding item from the Phase-1 review deferred to this stage (finding 20,
"Datasheet URL empty on 24 non-passive parts") had **3 instances on this sheet**:
D201, D202 (LED, C2290) and L200 (inductor, C42411119). Datasheet URLs were added for
all three, from the same DB rows used to verify their LCSC numbers. That is the only
field change made — the netlist proof below shows 0 net/value/footprint changes.

The 4 test points (TP200–TP203) have no LCSC, per FC convention (verified below), and
needed no change.

## Part table (47 symbols)

| Ref | Value | Footprint | LCSC | MPN | Basic/Extended | Stock | Price (1pc) | Source |
|---|---|---|---|---|---|---|---|---|
| C200 | 1uF | C_0603_1608Metric | C15849 | CL10A105KB8NNNC | Basic | 8,129,560 | $0.021 | re-verified; Phase-1 as-ordered BOM `BOM-FC_V5e_Production_Rev2.csv`: `1uF,"C37,C4,C41",C_0603_1608Metric,C15849,3` |
| C201 | 100nF | C_0402_1005Metric | C1525 | CL05B104KO5NNNC | Basic | 33,327,481 | $0.004 | re-verified; FC (C71–C78) stick |
| C202 | 10uF | C_0603_1608Metric | C19702 | CL10A106KP8NNNC | Basic | 13,909,324 | $0.032 | re-verified; FC (C1/C14/…) stick |
| C203, C204–C212, C218–C220 | 100nF | C_0402_1005Metric | C1525 | CL05B104KO5NNNC | Basic | 33,327,481 | $0.004 | re-verified; FC (C71–C78) stick |
| C213, C215, C216, C217 | 4.7uF | C_0402_1005Metric_small_pads | C23733 | CL05A475MP5NRNC | Basic | 3,271,433 | $0.019 | re-verified; FC (C65/C66/C68/C69) stick |
| C214 | 10uF | C_0805_2012Metric | C15850 | CL21A106KAYNNNE | Basic | 7,037,778 | $0.084 | re-verified; FC (C75) stick |
| C221, C222 | 15pF | C_0402_1005Metric | C1548 | 0402CG150J500NT | Basic | 1,676,236 | $0.004 | re-verified; FC (C63/C64) stick |
| D200 | NSR0320 | D_SOD-323F | C48192 | NSR0320MW2T1G | Extended | 24,605 | $0.125 | re-verified; FC (D4) stick |
| D201, D202 | LED | LED_0603_1608Metric | C2290 | KT-0603W | Basic | 1,158,040 | $0.012 | re-verified; FC (D1/D2/D3) stick. **Datasheet URL added** (was blank) |
| L200 | 3.3u | L_pol_2016 | C42411119 | AOTA-B201610S3R3-101-T | Extended | 13,543 | $0.283 | re-verified; FC (L3) stick. **Datasheet URL added** (was blank) |
| R200 | 33 | R_0402_1005Metric | C25105 | 0402WGF330JTCE ±1% | Basic | 2,162,502 | $0.004 | re-verified; FC (R94) stick |
| R201, R204, R206, R211 | 1k | R_0402_1005Metric | C11702 | 0402WGF1001TCE ±1% | Basic | 12,881,369 | $0.002 | re-verified; FC (R93) stick |
| R202, R205 | 10k | R_0402_1005Metric | C25744 | 0402WGF1002TCE ±1% | Basic | 29,737,515 | $0.003 | re-verified; FC (R2/R37) stick |
| R203 | 0 | R_0402_1005Metric | C17168 | 0402WGF0000TCE | Basic | 12,093,991 | $0.003 | re-verified; FC (R91) stick |
| R207–R210 | 4.7k | R_0402_1005Metric | C25900 | 0402WGF4701TCE ±1% | Basic | 18,365,039 | $0.003 | re-verified; FC (R100/R103/R104/…) stick |
| TP200–TP203 | (net name) | TestPoint_Pad_D1.5mm | — | — | — | — | — | test point, no LCSC by FC convention (see below) |
| U200 | RP2350A | RP2350-QFN-60-1EP_7x7… | C42411118 | RP2350A | Extended | 9,546 | $1.287 | re-verified; FC (U18) stick. Low stock (Extended) — flag to buy early per brief §7 note |
| U201 | W25Q128JVS | SOIC-8_5.3x5.3mm_P1.27mm | C97521 | W25Q128JVSIQ | Basic | 82,786 | $2.599 | re-verified; FC (U11) stick |
| U202 | AP2112K-3.3 | SOT-23-5 | C51118 | AP2112K-3.3TRG1 | Extended | 67,872 | $0.171 | re-verified; live-verified at Phase-1 (`lcsc.com/product-detail/C51118.html`), no repo BOM precedent. DB `Package` field reads "SOT-25-5" — confirmed this is the JLC catalogue's own alias for the same physical SOT-23-5 outline used by this exact Diodes part family (cross-checked against C22365427, an equivalent AP2112K-3.3 pin-compatible part from another manufacturer explicitly listed as "SOT-23-5" in the same DB) — **not a footprint mismatch** |
| Y200 | ABM8-272-T3 | Crystal_SMD_3225-4Pin_3.2x2.5mm | C20625731 | ABM8-272-T3 | Extended | 23,494 | $0.620 | re-verified; FC (Y1) stick |

Query used for every re-verification (sqlite3, `python3` `sqlite3` module):

```sql
SELECT * FROM parts WHERE "LCSC Part" = ?
```
against `~/Documents/KiCad/10.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/parts-fts5.db`,
run once per the 18 distinct LCSC numbers on this sheet. All 18 rows found, all
`Package` fields consistent with the symbol's KiCad footprint (see table; the one
apparent SOT-25-5/SOT-23-5 naming difference on U202 is a cross-checked DB alias, not
a real mismatch). No row's `Value`/description contradicted the symbol's value. **0
defects found on any existing LCSC.**

## Datasheet URLs added (3, all previously blank)

| Ref | Datasheet URL | Source |
|---|---|---|
| D201, D202 | `https://www.lcsc.com/datasheet/lcsc_datasheet_2305091500_Hubei-KENTO-Elec-KT-0603W_C2290.pdf` | DB row for C2290 (`Datasheet` column) |
| L200 | `https://www.lcsc.com/datasheet/lcsc_datasheet_2412101620_Abracon-LLC-AOTA-B201610S3R3-101-T_C42411119.pdf` | DB row for C42411119 (`Datasheet` column) |

The other 5 non-passive-with-datasheet parts on this sheet (D200, U200, U201, U202,
Y200) already had their Datasheet URLs filled from Phase-1 (manufacturer pages, not
LCSC mirrors) and were left as is.

## Unresolved parts

None. Every part on this sheet either already had an LCSC number (re-verified, 0
changes) or is a test point (no LCSC by convention, see below).

## Test-point handling

Checked the FC convention directly: grepped `FlatSat_V1.kicad_sch` and
`eps_side.kicad_sch` for `Connector:TestPoint` symbols with `Reference` TP1–TP8
(TP2, TP5, TP6, TP8 found; TP1/TP3/TP4/TP7 don't exist as discrete symbols on this
board). All four found instances carry `(in_bom yes) (on_board yes) (in_pos_files
yes) (dnp no)` and **no `LCSC Part` property at all** (not even blank) — i.e. the FC's
own test points are normal, orderable-BOM-row entries that simply have no LCSC
assignment; they are **not** excluded from BOM or position files.

TP200–TP203 on this sheet already match that convention exactly: the generator's
`sym()` helper hardcodes `in_bom yes / on_board yes / in_pos_files yes / dnp no` for
every symbol, and the `testpoint()` helper never sets an `LCSC Part` property. Checked
the live sheet directly — all four confirm `in_bom yes`, `in_pos_files yes`, `dnp no`.
**No change was needed or made.**

## Netlist proof (field-only change)

- `tools/sch_lint.py emulator_mcu.kicad_sch --project FlatSat_V1 --path
  /c64c0d72-a9f6-4f3a-891e-1f647558f538/8394a2ec-8c1e-41a1-b086-be3289cedfbc
  --refdes-block 200-299` → `93 symbol instances, 14 lib symbols, 185 wires, 0
  errors, 0 warnings`.
- `tools/harness_erc.sh "Emulator MCU"` → `violations on sheets matching 'Emulator
  MCU': total 0, errors: 0`; sheet-independent ERC delta vs the harness's Rev2+
  promotions baseline is `+0` on both error classes (`pin_not_connected`,
  `power_pin_not_driven`); the harness's warning/added-component deltas reflect all
  six Phase-1 sheets being present against a baseline that predates all of them (the
  harness always folds in every integrated sheet), not anything from this stage.
- `tools/netlist_diff.py <final Phase-1 netlist.xml> <fresh kicad-cli kicadxml
  export of the current project>` →
  `components: base 479, new 479, added 0, removed 0`;
  `nets: base 354, new 354`; `added nets (0)`, `removed nets (0)`, `changed nets
  (0)` — and no `~ ref: (value,fp) -> (value,fp)` lines at all, i.e. **0 component
  value/footprint changes** anywhere in the project, confirming this sheet's edits
  (3 `Datasheet` field additions) did not touch any net, value or footprint.
- Regeneration reproducibility: ran `tools/gen/emulator_mcu_gen.py` a second time
  into scratch after the field edits were applied to the generator and the live
  sheet; `diff emulator_mcu.kicad_sch <scratch regen>` is **byte-identical** —
  uuid-stable regeneration confirmed with the new fields baked in.

## Files changed

- `FlatSat_V1/emulator_mcu.kicad_sch` — regenerated (3 `Datasheet` property values
  filled: D201, D202, L200; nothing else changed, confirmed byte-diff above).
- `FlatSat_V1/tools/gen/emulator_mcu_gen.py` — added `DS_LED` and `DS_L200`
  constants and passed `ds=DS_LED` / `ds=DS_L200` to the D201, D202 and L200 `sym()`
  calls, so a regeneration reproduces the sheet with the new fields.
- `docs/flatsat/2026-09-14_phase2_layout/supply_emulator_mcu.md` — this report.

`jlcpcb/project.db` was not opened or written. The board (`FlatSat_V1.kicad_pcb`) was
not touched.
