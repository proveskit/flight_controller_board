# Supply chain — "Pyro Inhibit and Jumpers" (refdes 600–649)

**Date:** 2026-09-14 (rev 2, verifier fix) · **Sheet:** `FlatSat_V1/pyro_inhibit.kicad_sch` · **Generator:** `tools/gen/pyro_inhibit_gen.py`
**Source of truth for the part list:** `/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/final/netlist.xml`, components whose `sheetpath` is `/Pyro Inhibit and Jumpers/`.
**Catalogue:** `~/Documents/KiCad/10.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/parts-fts5.db` (refreshed 2026-09-13), table `parts` (fts5, trigram).

## Rev 2 changelog (verifier fix, major severity)

A verifier found that `parts` is an FTS5 virtual table where **every column, including `Stock`, is untyped/compared as TEXT**. Rev 1's JP600–607 query used a bare `ORDER BY Stock DESC`, which sorts lexicographically ("9828" > "159910" as strings, because `'9' > '1'` as a leading character), not numerically. Reran every `ORDER BY Stock DESC` query in this report with `ORDER BY CAST(Stock AS INTEGER) DESC`:

- **JP600–607 changed: C5383111 → C124375.** The true numeric-max row in the report's own filter (`Second Category`='Pin Headers', `Description` LIKE '%1x2P%'/'%1*2P%', `Package` LIKE 'Plugin%'), restricted to the report's own tie-break of both pitch dimensions reading exactly "2.54mm 2.54mm", is **C124375** (B-2100S02P-A110, Ckmtw, stock 159,910) — 16x the stock of the rev-1 pick C5383111 (2541WV-02P, HanElectricity, stock 9,828), same package class (`Plugin,P=2.54mm`, Extended library), same 1×2 2.54 mm THT footprint (`Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical`). Full ranked list captured in "Newly filled LCSC numbers" below. C5383111 was not a build-blocker (9,828 pcs comfortably covers 8 needed) but rev 1's "highest-stock" framing was factually wrong and left a materially safer option undiscovered; fixed by re-picking the part rather than just correcting the narrative.
- **D600–602 (BAT54W) unchanged (C77328), but the documented query text was wrong.** Rev 1's printed SQL (`SELECT ... WHERE "MFR.Part" LIKE 'BAT54W%' AND Package='SOT-323'` with no CAST) does not reproduce the report's own stated top-3 when actually run — an uncast run returns C28750440 (stock '90', text-sorts above '7403') at the top, not C77328/C41374260/C5240621. Reran with `ORDER BY CAST(Stock AS INTEGER) DESC`: this **does** reproduce the documented ordering exactly (C77328 7,403 · C41374260 7,108 · C5240621 3,000 · ... · BAT54WFILMY variant at 374, still correctly excluded). So the BAT54W pick itself needed no change — only the query text below, which now has the CAST and is verified to actually produce the displayed rows.

Every other `ORDER BY Stock DESC` query in this report (there are none besides the two above) is unaffected. Flagging for the other five per-sheet agents in this batch: any of them using an uncast `ORDER BY Stock DESC` against this FTS5 catalogue has the identical bug — `Stock` must be `CAST(... AS INTEGER)` (or `AS REAL`) before sorting.

This sheet has 23 symbol instances / 17 distinct refs-groups: 3 diodes (D600–602), 8 jumper headers
(JP600–607), 1 LED (LED600), 3 resistors (R600–602), 1 slide switch (SW600), 4 test points
(TP600–603), plus 3 power symbols (#PWR600–602, no LCSC by convention).

## Newly filled LCSC numbers

| Ref | Value | Footprint | LCSC | MPN | Lib Type | Stock | Price (qty1) | Source |
|---|---|---|---|---|---|---|---|---|
| D600, D601, D602 | BAT54W | `Package_TO_SOT_SMD:SOT-323_SC-70` | **C77328** | BAT54W (Jiangsu Changjing) | Extended | 7,403 | $0.024 | `SELECT ... FROM parts WHERE "MFR.Part" LIKE 'BAT54W%' AND Package='SOT-323' ORDER BY CAST(Stock AS INTEGER) DESC` — verified-numeric-highest-stock exact-MFR.Part hit (C77328 7,403 · C41374260 7,108 · C5240621 3,000 · C41382599 3,000 · ... · a "BAT54WFILMY" variant at 374, excluded as a different part). No Basic-library BAT54W exists in the catalogue. (Rev 2: added the `CAST` — rev 1's printed query lacked it and, run literally, does not reproduce this ordering; see the rev-2 changelog above. The pick itself, C77328, is unchanged.) |
| JP600–JP607 (8 headers) | Conn_01x02 | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | **C124375** | B-2100S02P-A110 (Ckmtw/Shenzhen Cankemeng) | Extended | 159,910 | $0.030 | `SELECT ... FROM parts WHERE "Second Category"='Pin Headers' AND (Description LIKE '%1x2P%' OR Description LIKE '%1*2P%') AND Package LIKE 'Plugin%' AND Description LIKE '%2.54mm 2.54mm%' ORDER BY CAST(Stock AS INTEGER) DESC` — the pitch-exact filter is the report's own original tie-break (reject rows whose second pitch dimension reads "2.5mm" instead of "2.54mm", e.g. C492401/C358684 which otherwise have far higher raw stock); within it, C124375 (159,910) is the verified numeric-max, ahead of C225477 (55,248), C706874 (28,775), and rev 1's pick C5383111 (9,828, 7th place in this list). No Basic-library 2.54 mm 1×2 THT pin header exists in the catalogue (`SELECT ... WHERE "Second Category"='Pin Headers' AND "Library Type"='Basic'` returns 0 rows) — Extended is the only option, consistent with the PM brief's own framing ("2.54 mm headers" listed among the blanks with no Basic-vs-Extended promise). (Rev 2: re-picked from C5383111 — see the rev-2 changelog above.) |

Datasheet URLs added (both are non-passive per L9):
- D600–602: unchanged — see "Notes" below (kept the Nexperia `BAT54W_SER.pdf` already on the sheet from Phase‑1; the JLC row's own Nexperia-doc-agnostic sheet is `https://www.lcsc.com/datasheet/lcsc_datasheet_1809212129_Jiangsu-Changjing-Electronics-Technology-Co---Ltd--BAT54W_C77328.pdf`, not added since a JEDEC-generic-part datasheet swap would drop the specific VF/VIL/VIH margin numbers the sheet's own text notes and the Phase-1 review cite).
- JP600–607 (8 refs): **added** `https://www.lcsc.com/datasheet/lcsc_datasheet_2411220201_Ckmtw-Shenzhen-Cankemeng-B-2100S02P-A110_C124375.pdf` (was blank; rev 2 URL, for C124375 — supersedes rev 1's C5383111 URL).

**Datasheet URLs added this pass: 8** (JP600, JP601, JP602, JP603, JP604, JP605, JP606, JP607).

## Existing LCSC — re-verified against the catalogue

| Ref | Value | Footprint | LCSC | DB row (package / value / type) | Result |
|---|---|---|---|---|---|
| LED600 | LED (white 0603) | `LED_SMD:LED_0603_1608Metric` | C2290 | KT-0603W (Hubei KENTO Elec), Package `0603`, Basic, stock 1,158,040, "2.6V~3.1V 360mcd 5mA ... White" | **Match** — package and description (white 0603 LED) agree with the symbol's Value/Description. No defect. |
| R600, R601 | 4.7k | `Resistor_SMD:R_0402_1005Metric` | C25900 | 0402WGF4701TCE (UNI-ROYAL), Package `0402`, Basic, stock 18,365,039, "4.7kΩ ±1%" | **Match**. No defect. |
| R602 | 470R | `Resistor_SMD:R_0402_1005Metric` | C25117 | 0402WGF4700TCE (UNI-ROYAL), Package `0402`, Basic, stock 1,362,254, "470Ω ±1%" | **Match**. No defect. |

Query used for all three: `SELECT * FROM parts WHERE "LCSC Part" IN ('C2290','C25900','C25117')`. All three package/value pairs agree with the symbol; **no mismatches found, no defects to fix** on this sheet. (These may or may not be among the Phase-1 review's globally-flagged "8 LCSC numbers to re-verify" — the review report does not name which refs; every existing LCSC on this sheet was re-verified regardless, per instructions.)

## Unresolved — left blank

| Ref | Value | Footprint | Why unresolved |
|---|---|---|---|
| SW600 | ~~SW_SPST~~ **MSK12C02** | ~~`Button_Switch_THT:SW_DIP_SPSTx01_Slide_9.78x4.72mm_W7.62mm_P2.54mm`~~ **`Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02`** | **Resolved by PM ruling S2 (2026-09-14) — see §7.** Originally: this was a specific CTS 206/208-series-style 1-pole DIP slide switch (row spacing 7.62 mm/300 mil, body 9.78×4.72 mm — per the KiCad footprint's own `descr`). Exhaustive search of the catalogue (`Second Category` = 'Slide Switches' and 'DIP Switches'; `Description` LIKE combinations of 'SPST'/'Slide'/'7.62'/'9.7'/'4.7'; `MFR.Part` MATCH the reference 1MS1T1B1M2QE family) found **no in-stock part with a matching footprint**. The one catalogue hit for the reference family itself, C22422208 (`1MS1T1B1M2QES`), is 0 stock and marked not-ROHS. PM ruling S2 authorized replacing the part and symbol (the one permitted netlist change of stage 1): now `Switch:SW_SPDT` used as SPST, MPN MSK12C02, LCSC **C431540**, stock 146,433. Full detail in §7. |
| TP600, TP601, TP602, TP603 | Deploy1_EN / Heater_EN / Deploy2_EN / PYRO_INH_COM | `TestPoint:TestPoint_Pad_D1.5mm` | **Intentional, matches the FC convention** — see below. |

## Test-point handling

Checked the FC's own root-sheet test points (`FlatSat_V1.kicad_sch`, TP2/TP6/TP8 — the only root TPs actually present as symbols; TP1/TP3–5/TP7 are referenced only via the Phase-1 brief, not found as root symbols). TP2's symbol block: `(in_bom yes)`, `(on_board yes)`, `(in_pos_files yes)`, no `LCSC Part` field, `Datasheet`/`Description` both empty. No exclude-from-BOM or exclude-from-position flag is set differently from any other part on the FC.

TP600–603 on this sheet already match that convention exactly: no `LCSC Part` field, `in_bom yes`, `in_pos_files yes` (the generator's `place_symbol()` defaults, never overridden for these four). **No change made** — left as-is, per the instruction to only mark exclude-from-BOM/position if the FC's own TPs do, which they don't.

## Proof (rev 2, re-run after the fix)

- `python3 tools/sch_lint.py pyro_inhibit.kicad_sch --project FlatSat_V1 --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/ba398093-e7fc-4f25-8f04-4265c3e55b54 --refdes-block 600-649` → `23 symbol instances, 8 lib symbols, 41 wires, 0 errors, 0 warnings`.
- `tools/harness_erc.sh "Pyro Inhibit"` → `violations on sheets matching 'Pyro Inhibit': total 0, errors: 0` (unchanged from rev 1; the whole-project totals shown by the harness — errors 11, total delta +59 vs baseline — are pre-existing from all Phase-1 sheets being present, not from this pass).
- `kicad-cli sch export netlist --format kicadxml` on the live `FlatSat_V1.kicad_sch` (with the regenerated `pyro_inhibit.kicad_sch`) → `tools/netlist_diff.py` against the Phase-1 final netlist (`/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/final/netlist.xml`): `components: base 479, new 479, added 0, removed 0`; `nets: base 354, new 354`; `added nets (0)`, `removed nets (0)`, `changed nets (0)`; **zero `~` component value/footprint-change lines printed** — confirms the rev-2 edit (C5383111 → C124375 on JP600–607, plus the corrected BAT54W query text) stayed field-only (LCSC Part / Datasheet changes only).
- Generator reproducibility: regenerated the sheet twice in a row from the rev-2 generator and diffed byte-for-byte — **identical** (uuid-stable, per the seeded RNG).
- Stock-query fix itself: reran the JP600–607 query and the BAT54W query both with and without `CAST(Stock AS INTEGER)` and confirmed the uncast forms text-sort wrong (as the verifier reported) while the cast forms reproduce the rankings now documented above — see the rev-2 changelog.

## Summary of file changes

- `FlatSat_V1/tools/gen/pyro_inhibit_gen.py` (rev 1): added `extra_props=[("LCSC Part", "C77328")]` to D600–602's `place_symbol()` call; added `extra_props=[("LCSC Part", "C5383111")]` to all 8 JP600–607 `place_symbol()` calls; changed those same 8 calls' `datasheet` argument from `''` to the new `JP_DATASHEET` constant; added a documentation comment above SW600 explaining why it has no LCSC.
- `FlatSat_V1/tools/gen/pyro_inhibit_gen.py` (rev 2, this fix): changed `JP_DATASHEET` to C124375's datasheet URL and its comment to explain the CAST-fix re-pick; changed all 8 JP600–607 `extra_props` LCSC values from `"C5383111"` to `"C124375"` (JP600, JP601, JP602–606, JP607) with updated inline comments.
- `FlatSat_V1/pyro_inhibit.kicad_sch`: regenerated from the rev-2 generator (atomic `.tmp` + `os.replace`).
- `docs/flatsat/2026-09-14_phase2_layout/supply_pyro_inhibit.md`: this file — added the rev-2 changelog, updated the JP600–607 and BAT54W table rows/source SQL, updated the datasheet-URL list, re-ran and re-pasted the proof section.

No other file was touched. The board (`.kicad_pcb`) and `jlcpcb/project.db` were not opened or modified.

## 7. PM ruling S2 applied (2026-09-14) — SW600 replaced

`00_pm_brief.md` §3.1 ruling S2: SW600's `SW_DIP_SPSTx01_Slide` footprint has no JLC part (§3/§6 above). PM ruling: **replace with a JLC-stocked slide switch**, symbol `Switch:SW_SPDT` used as SPST (unused throw marked no-connect), footprint matching the chosen part, "SAFE ↔ ARMED" legend retained. Declared the one permitted netlist change of stage 1 (SW600's pins only).

### 7.1 Part chosen and why

Queried `parts-fts5.db` for both candidate families named in the ruling:

```sql
-- THT candidate
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock,Manufacturer FROM parts
WHERE "MFR.Part" LIKE 'SS-12D00%' OR "MFR.Part" LIKE 'SS12D00%' ORDER BY CAST(Stock AS INTEGER) DESC LIMIT 20;

-- SMD candidate
SELECT "LCSC Part","MFR.Part",Package,"Library Type",Description,Stock,Manufacturer FROM parts
WHERE "MFR.Part" LIKE 'MSK-12C02%' OR "MFR.Part" LIKE 'MSK12C02%' ORDER BY CAST(Stock AS INTEGER) DESC LIMIT 20;
```

THT top hit: `C22355741` (SS-12D00-G3, SOFNG, `Plugin-3P,8.8x3.9mm`, Extended, stock **13,170**). SMD top hit: `C431540` (**MSK12C02**, SHOU HAN, `SMD,8x2.8mm`, Extended, stock **146,433**, Datasheet `https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_SHOU-HAN-MSK12C02_C431540.pdf`). No Basic-library slide switch of any kind exists in the catalogue (`Second Category`='Slide Switches'/'DIP Switches', `Library Type`='Basic' returns 0 rows) — Extended is the only option either way.

**Footprint check decided it.** KiCad's standard `Button_Switch_SMD.pretty` carries `SW_SPDT_Shouhan_MSK12C02.kicad_mod` — a footprint built specifically for this exact LCSC part: its own `descr` field cites `https://www.lcsc.com/datasheet/lcsc_datasheet_2304140030_SHOU-HAN-MSK12C02_C431540.pdf` verbatim (the same URL the DB row carries independently), and its `tags` list `MSK-12C02 MSK12C02 MSK12C02-HB`. Pad layout: 3 SMD electrical pads ("1","2","3") plus 4 "SH" shield/mounting pads and 2 NPTH alignment holes — matches the `Switch:SW_SPDT` symbol's 3-pin SPDT electrical model directly, no adaptation needed. `~/Documents/KiCad/easyeda2kicad/easyeda2kicad.pretty` was also checked (`Switch_SW_SPDT.sexp` note in the task): it holds only two switch footprints, `SW-TH_D2F-L` and `SW-TH_SHOU-HAN_SS12D10G4` (the part `bench_io`'s SW703 already uses, LCSC C2887259) — no MSK12C02 SMD footprint there, so the KiCad-standard one is the only ready-made, part-verified option.

**Datasheet verification (pad count/pitch vs. the KiCad footprint):** fetched the SHOU-HAN MSK12C02 mechanical drawing (`https://wmsc.lcsc.com/wmsc/upload/file/pdf/v2/lcsc/2304140030_SHOU-HAN-MSK12C02_C431540.pdf` — the `www.lcsc.com/datasheet/...` URL that both the DB and the footprint cite front-ends a bot-check page and does not itself serve the PDF; the `wmsc.lcsc.com` CDN mirror does). Page 1's mechanical drawing shows an 8±0.2 mm-wide body and a 4-point contact/mounting pattern with 1.5 mm and 3 mm pin-spacing dimensions, matching the footprint's pad-1/2/3 x-coordinates (-2.25, 0.75, 2.25 mm — i.e. 3.0 mm and 1.5 mm gaps) exactly. (The datasheet's own boilerplate spec text in §2.4 says "Contact arrangement: 1 pole, 1 throw" — this is a template artifact reused across SHOU-HAN's switch/button product lines, contradicted by the drawing's own 3-contact circuit diagram, the JLC catalogue's "SPDT" description, and the KiCad footprint's own SPDT-specific pad set and name; the mechanical drawing and the catalogue/footprint metadata, not the reused boilerplate sentence, are treated as authoritative here.)

**THT alternative rejected:** `C22355741` (SS-12D00-G3) has ~10x less stock (13,170 vs. 146,433) and no footprint in this project tying it to that exact MFR.Part — verifying its pad geometry against the datasheet would have been extra unverified work for a worse-stocked part with no existing footprint precedent, against a part (MSK12C02) that already has a purpose-built, LCSC-linked, pad-verified KiCad footprint and ~10x the stock. `MSK12C02` / `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02` was selected.

### 7.2 Symbol, wiring, no-connect

`Switch:SW_SPDT` (pantry block `tools/pantry/Switch_SW_SPDT.sexp` — already present; confirmed via `python3 tools/get_symbol.py "Switch:SW_SPDT"`, which re-fetches the block from `bench_io.kicad_sch` (the sheet that already uses it for SW703) and reproduces the checked-in pantry file's content exactly — the only diff is cosmetic (the source sheet wraps one `polyline`'s two `(xy ...)` points across two lines, the pantry file has them on one; both parse to the identical symbol). Same symbol `bench_io`'s SW703 uses. Pin map (same convention as `bench_io_gen.py`): pin 2 = common wiper, pins 1 and 3 = the two throws.

Wired exactly as `SW_SPST` was: common (pin 2) → `PYRO_INH_COM` at the same bus node SW_SPST's pin 1 used; one throw (pin 3, the one whose local geometry lines up with the existing GND-column wire down to JP601) → `GND`, in place of `SW_SPST`'s old pin 2. The switch is therefore still electrically SPST: slider toward pin 3 = closed = common-to-GND = INHIBIT/SAFE, identical behaviour to the part it replaces. The unused throw (pin 1) carries a `no_connect` marker rather than being left off the symbol, per the ruling.

On-sheet text updated to match: the SW600 legend ("SW600 (MSK12C02): pin 3 = CLOSED = INHIBIT / SAFE (default). Pin 1 (NC) = ARMED. JP601 panel switch is in parallel: closed = SAFE too.") and the jumper-population-table SW600 row both name pin 3 as the closed/inhibit throw and pin 1 as the no-connect/armed throw — the "SAFE ↔ ARMED" sense is retained, now tied to the correct physical pin.

### 7.3 Proof (re-run after this pass)

```
$ python3 tools/sch_lint.py pyro_inhibit.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/ba398093-e7fc-4f25-8f04-4265c3e55b54 --refdes-block 600-649
pyro_inhibit.kicad_sch: 23 symbol instances, 8 lib symbols, 41 wires, 0 errors, 0 warnings
```

```
$ tools/harness_erc.sh "Pyro Inhibit and Jumpers"
=== violations on sheets matching 'Pyro Inhibit and Jumpers' ===
total 0
errors: 0
```
Sheet-local: 0 violations of any kind (unchanged from every prior round). Project-wide: 11 errors (unchanged FC baseline, all pre-existing on other sheets), +0 new errors.

```
$ kicad-cli sch export netlist --format kicadxml -o netlist_fresh.kicadxml FlatSat_V1.kicad_sch
$ python3 tools/netlist_diff.py tools/baseline/netlist_phase1.kicadxml netlist_fresh.kicadxml
components: base 479, new 479, added 0, removed 0
  ~ R515: ('5.7k', ...) -> ('5.62k', ...)                    [PM ruling S1, same pass -- see supply_battery_protection_replica.md §7]
  ~ SW600: ('SW_SPST', 'Button_Switch_THT:SW_DIP_SPSTx01_Slide_9.78x4.72mm_W7.62mm_P2.54mm')
           -> ('MSK12C02', 'Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02')
nets: base 354, new 355
added nets (1):
  + unconnected-(SW600-A-Pad1): SW600.1
removed nets (0):
changed nets (2):
  ~ /Pyro Inhibit and Jumpers/PYRO_INH_COM: +[SW600.2] -[SW600.1]
  ~ GND: +[SW600.3] -[SW600.2]
```
Exactly the expected result: **one new `unconnected-(SW600-...)` net** (the no-connect throw, pin 1) and **two changed nets that are both SW600-pin-membership swaps** (`PYRO_INH_COM` gains SW600's new common pin 2 in place of the old SPST pin 1; `GND` gains SW600's new GND-throw pin 3 in place of the old SPST pin 2) — i.e. the SW600-pin-renumbering consequence of moving from a 2-pin SPST symbol to a 3-pin SPDT-used-as-SPST symbol on the same two electrical roles. **Nothing else in the project changed**: 0 components added/removed, 0 nets added beyond the one no-connect stub, 0 nets removed, and the only other component-level change anywhere (`R515`) belongs to the separate, concurrently-applied PM ruling S1 on the sibling sheet. No net any other sheet defines, consumes, or touches is affected.

**Generator reproducibility:** ran `tools/gen/pyro_inhibit_gen.py` twice after this edit — byte-identical output (including uuids), and byte-identical to the live `pyro_inhibit.kicad_sch`.

**PDF visual check:** exported the full harness project to PDF (`kicad-cli sch export pdf`) and read page 11 (`Pyro Inhibit and Jumpers`) back at full-page and cropped resolution around the switch/JP601/legend cluster — the SW_SPDT body outline, the relocated Reference/Value text (pushed to ±5.08 mm per the box-clearance fix bench_io's SW703 already established for this symbol), the no-connect X at pin 1, and the updated legend text all render cleanly with no overlaps.

### 7.4 Files changed (this pass)

- `FlatSat_V1/tools/gen/pyro_inhibit_gen.py`:
  - Added a `Switch:SW_SPDT` entry to the `PINS` pin-coordinate map and the `lib_block_files` map (pantry block already present at `tools/pantry/Switch_SW_SPDT.sexp`, confirmed via `get_symbol.py`, so no pantry file was added).
  - SW600's `place_symbol(...)` call: `lib_id` `Switch:SW_SPST`→`Switch:SW_SPDT`, `Value` `SW_SPST`→`MSK12C02`, `Footprint` → `Button_Switch_SMD:SW_SPDT_Shouhan_MSK12C02`, `Datasheet` added, `Description` rewritten, `extra_props=[("LCSC Part","C431540")]` added, `ref_dy=-5.08, val_dy=5.08` added (SW_SPDT's body box is bigger than SW_SPST's, same fix `bench_io`'s SW703 uses).
  - Wiring: common (pin 2) → `PYRO_INH_COM` (unchanged node); pin 3 → `GND` (wire endpoint moved from the old pin 2's location to pin 3's); pin 1 → `no_connect(...)` (new).
  - Updated the SW600 legend `text_note` and the jumper-population-table SW600 row to name pin 3/pin 1 instead of the old footprint's silkscreen convention.
- `FlatSat_V1/pyro_inhibit.kicad_sch` — regenerated from the updated generator (atomic `.tmp` + `os.replace`).
- This report — updated the SW600 row (§3/§6 table), added this §7.

`jlcpcb/project.db` was not touched. The board (`.kicad_pcb`) was not touched.

**PM ruling S2 applied.**
