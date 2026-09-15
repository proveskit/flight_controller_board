# Sheet report: `solar_power_injection`

**File:** `FlatSat_V1/solar_power_injection.kicad_sch` · **Sheetname:** "Solar Power Injection" · **Page:** 9
**Generator:** `FlatSat_V1/tools/gen/solar_power_injection_gen.py` · **Refdes block:** 400–449
**Sheet-symbol uuid:** `88d5f13b-6a4a-4f50-805f-872821082e52` · **Instances path:** `/c64c0d72-a9f6-4f3a-891e-1f647558f538/88d5f13b-6a4a-4f50-805f-872821082e52`

## 1. Purpose

Bench VSOLAR injection per PM brief §6.3 and decision D2: two independent screw-terminal input channels, each a fuse → series Schottky → open jumper header, feeding the FC's existing `VSOLAR` net (the same net all six face connectors J1/J2/J6/J9/J11/J13 already share pins 1–2 on). CH-A is fitted and shunted by default (active); CH-B is a second, identical, populated channel whose jumper is left open by default (inactive until a shunt is installed) — two channels are enough to demonstrate diode-OR'd/one-face-shadowed behaviour with two bench supplies, since per D2 all six face taps are electrically one net anyway.

## 2. Block description

Each channel (CH-A: J400/F400/D400/JP400; CH-B: J401/F401/D401/JP401) is identical:

`screw terminal (+/−, 5.08 mm pitch class) → polyfuse → Schottky (anode toward source) → open 2-pin jumper header → global label VSOLAR`

- Terminal pin 2 (−) goes to `GND`.
- The node between the terminal and the fuse is named `VSOLAR_BENCH_A` / `VSOLAR_BENCH_B` (a `flatsat:VSOLAR_BENCH` power symbol with its `Value` overridden per instance, per the pantry convention — same lib symbol, two different net names), carries this sheet's `PWR_FLAG`, and has a test point.
- A shared test point (TP401) taps `VSOLAR` itself, downstream of CH-A's jumper (the net is common to both channels via the two `VSOLAR` global-label instances, so one test point is enough).
- No per-face/per-channel current limiting beyond the fuse — this matches D2's rationale that six face taps are already one net.
- Reverse-polarity handling is the series Schottky only (anode facing the bench source); no TVS is fitted (brief explicitly allows omitting one, PSU OVP is primary protection).

## 3. Parts table

| Ref | Value | Footprint | LCSC | Source |
|---|---|---|---|---|
| J400, J401 | `Terminal_2P_5.08mm` | `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` | **needs LCSC** | Brief §6.3 ("5.08 mm pitch class"); Phoenix MKDS-1,5-2-5.08 is a true 5.08 mm-pitch 1x02 screw-terminal footprint (fix round: replaces the 5.00 mm MaiXu MX126 substitution — see §10) |
| F400, F401 | `1.85A_PTC_33V` (Littelfuse 2920L185DR: 1.85 A Ihold / 3.70 A Itrip / 33 V Vmax / 40 A Imax, Rmin 0.050 Ω, R1max 0.150 Ω) | `Fuse:Fuse_2920_7451Metric` | **`C207086`** | Brief §6.3's own "1.85 A polyfuse" option, taken literally (integrator fix round 3, §12). LCSC C207086 confirmed in the JLCPCB catalogue (`parts-fts5.db`): Littelfuse 2920L185DR, 2920, Extended, 14 433 in stock. Ratings from the Littelfuse 2920L Series PolySwitch datasheet, Electrical Characteristics table. Chosen over the "2 A slow-blow" alternative for bench convenience (auto-resets, no fuse replacement after a trip) |
| D400, D401 | `CDBA240LL-HF` | `Diode_SMD:D_SMA` | `C2886093` | Brief §6.3, as ordered on XY_Face_V4 (40 V, 2 A SMA Schottky). Manufacturer is Comchip Technology, per 01_brief_critique.md §13 and live-verified via LCSC listing `C2886093` during this task |
| JP400, JP401 | `Jumper_2_Open` | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | **needs LCSC** | Brief §6.3 + rule 9 (open-header symbol, never `_Bridged`); JP400 shunt fitted by default (CH-A), JP401 shunt open by default (CH-B, D2) |
| TP400, TP402 | `VSOLAR_BENCH_A` / `VSOLAR_BENCH_B` | `TestPoint:TestPoint_Pad_D1.5mm` | — (no BOM line, test point) | Brief §6.3 "test points on each VSOLAR_BENCH_x" |
| TP401 | `VSOLAR` | `TestPoint:TestPoint_Pad_D1.5mm` | — | Brief §6.3 "and on VSOLAR" (shared, one is enough — common net) |
| #PWR400, #PWR402 | `GND` | — | — | Terminal return |
| #PWR401, #PWR403 | `VSOLAR_BENCH_A` / `VSOLAR_BENCH_B` | — | — | `flatsat:VSOLAR_BENCH` pantry power symbol, `Value` overridden per instance |
| #FLG400, #FLG401 | `PWR_FLAG` | — | — | One PWR_FLAG per new rail (brief §4.2 ownership: this sheet owns `VSOLAR_BENCH_A`, `VSOLAR_BENCH_B`) |

0402/0603 passives were not needed on this sheet (no resistors/caps in the injection path).

## 4. Interface nets

**Existing FC nets touched** (global labels / power symbols, exact names): `VSOLAR`, `GND`.

**New nets defined by this sheet** (local rails, per brief §4.2 rail list and §4.2 PWR_FLAG ownership table): `VSOLAR_BENCH_A`, `VSOLAR_BENCH_B`.

**New nets consumed from another sheet:** none.

No `EMU_*`, `F0..F5_*`, `Dir_Chrg_In`, `B-`, `VBUSP`, or inhibit-chain nets are touched by this sheet — out of scope per the brief's per-sheet net table.

## 5. Jumper table

| Jumper | Channel | Default state | Effect |
|---|---|---|---|
| JP400 | CH-A | **SHUNT FITTED** (closed) | `VSOLAR_BENCH_A` → `VSOLAR` active |
| JP401 | CH-B | **Shunt OPEN** (not fitted) | CH-B fully populated (terminal/fuse/diode/header) but inactive until a 2.54 mm shunt is installed (PM brief D2) |

Both are drawn as `Jumper:Jumper_2_Open` (rule 9) — never a `_Bridged` symbol, so the netlist keeps `VSOLAR_BENCH_A`/`VSOLAR_BENCH_B` separate from `VSOLAR` until a physical shunt is fitted; the "shunt fitted" state for JP400 is an assembly note only.

### 5.1 Bench-procedure note — flight-software tests that depend on this sheet

> **`power_monitor_test` and any INA219-sol check require CH-A live (JP400 shunt fitted, PSU ≥ 11.7 V for LT3652 startup).**

Detail (see §13, review fix id 12): `proves-core-reference` `test/int/power_monitor_test.py` is tagged
`pytestmark = [pytest.mark.requires_battery]` only — there is no solar/CH-A marker — yet
`test_01_power_manager_readings` asserts
`sol_voltage != 0, "Solar voltage reading should be non-zero"` on `ReferenceDeployment.ina219SolManager`.
`ina219SolManager` is INA219 U8 (0x41), whose IN+ sits directly on `VSOLAR` (§6), so that assertion
is only satisfiable when this sheet is actually injecting: JP400's shunt fitted **and** a bench PSU
on J400. Run it with CH-A off and the test fails for a bench-configuration reason, not a FlatSat or
flight-software defect. Two qualifiers on the ≥ 11.7 V figure:

- 11.7 V is the LT3652 start-up threshold measured **at `VSOLAR`**. Because this sheet inserts
  F400 (R1max 0.150 Ω) and D400 (≈0.25–0.31 V at ≤1.2 A) in series, the **bench terminal** (J400)
  must be set to ≥ ~12.3 V, **12.5 V recommended** — see §11 item 3 and §12.2. A terminal reading of
  exactly 11.7 V or 12.0 V will not reliably start the charger.
- Bench window stays 12–18 V nominal, **hard maximum 24 V** (brief §6.3, restored in §12.2).

No schematic change: JP400 already defaults shunt-fitted/closed per brief D2, so the sheet is
correct as built; only the bench procedure and the Phase-4 test matrix need to say so.

## 6. Datasheet / brief facts relied on

- **CDBA240LL-HF**: 40 V, 2 A SMD Schottky, SMA (DO-214AC) package; manufacturer Comchip Technology, per 01_brief_critique.md §13 ("C2886093 is the Comchip CDBA240LL-HF (40 V, 2 A, 310 mV @ 2 A)") and live-verified via LCSC listing `C2886093` during this task.
- **F400/F401 fuse selection** *(superseded by integrator fix round 3, §12 — kept for traceability)*: rounds 1–2 searched only the Littelfuse **1812L** and Bourns **MF-MSMF** series and concluded that no 1.85 A polyfuse was procurable, which is true only inside those two 1812-body families. Fix round 3 re-specified F400/F401 to the **Littelfuse 2920L185DR** (LCSC `C207086`), the brief's own "1.85 A polyfuse" in a 2920 body. Numbers now quoted on the sheet come from the **Littelfuse 2920L Series PolySwitch Resettable PPTC datasheet** (© 2024, Farnell mirror `farnell.com/datasheets/4435859.pdf`, extracted with `pdftotext -layout`):
  - Electrical Characteristics table, row `2920L185 / LF185`: **Ihold 1.85 A, Itrip 3.70 A, Vmax 33 Vdc, Imax 40 A, Pd 1.50 W, max time to trip 2.50 s at 8.00 A, Rmin 0.050 Ω, R1max 0.150 Ω**.
  - Temperature Rerating table ("Ambient Operation Temperature", columns −40/−20/0/20/40/50/60/70/85 °C), row `2920L185`: **2.80 / 2.47 / 2.17 / 1.85 / 1.54 / 1.39 / 1.22 / 1.07 / 0.85 A**. So Ihold is a **20 °C** rating and the part still holds **1.54 A at 40 °C**, i.e. 28 % margin over the ≤1.2 A expected bench draw.
  - 33 V Vmax leaves **9 V of margin** over the brief's mandated 24 V bench hard maximum, so the round-2 narrowing of that limit to 20 V is no longer needed and has been reverted.
- **INA219 U8** (0x41), IN+ directly on `VSOLAR`: 26 V absolute maximum (brief §4.1/§6.3, from the Rev2 netlist/schematic).
- **LT3652 IC6**: 32 V operating maximum input; float voltage on this FC is 8.38 V, set by R71 (634 k) / R74 (412 k); startup requires VIN ≥ VFLOAT + 3.3 V = 11.7 V (brief §6.3).
- **eps_side.kicad_sch text note "VSOLAR 9V to 40V"** (at (95.25, 57.15) near IC6): brief §6.3 states this is wrong (40 V exceeds both the INA219 26 V and LT3652 32 V limits) and must be flagged, not repeated — done via a sheet note here; the note itself is left untouched on `eps_side.kicad_sch` (only the integrator may edit that file, hard rule 2).
- Fuse sizing: eps_side IC6 R75 = 0.1 Ω sets the LT3652 charge-current limit to ≈1.0 A, so expected bench input is ≤ ~1.2 A at 12 V (brief §6.3) — the 1.85 A Ihold 2920L185DR polyfuse (1.54 A held at 40 °C) and the "2 A slow-blow ≥32 V" alternative both clear this with margin. Its 3.70 A Itrip exceeds D400/D401's 2 A IF(AV) rating, so in an overcurrent event the bench PSU's own current limit protects the diode, not the PTC (which only opens above 3.7 A).

## 7. Assumptions / open questions for the reviewer

1. **D2 "CH-B footprint-only" reading**: I populated J401/F401/D401/JP401 identically to CH-A and left only JP401's shunt open, rather than marking the whole CH-B chain DNP. This follows §6.3's literal wording ("Each: ... jumper header (CH-A shunt fitted, CH-B open)"), which implies uniform population of the terminal/fuse/diode on both channels and only the jumper differs, and rule 9's framing of "shunt fitted by default" as an assembly-note distinction on an otherwise-always-populated header. If the intended reading was "CH-B parts fully DNP, footprints only," that would need `(dnp yes)` added to J401/F401/D401/JP401 — please confirm.
2. **F400/F401 part number — CLOSED in fix round 3 (§12).** F400/F401 are Littelfuse **2920L185DR**, LCSC **`C207086`** (1.85 A Ihold / 3.70 A Itrip / 33 V Vmax / 40 A Imax, SMD 2920/7451 metric), which is brief §6.3's own "1.85 A polyfuse" and no longer needs an LCSC lookup. Bench hard maximum restored to the brief's **24 V**, with 9 V of PTC voltage margin. Datasheet property points at the Littelfuse 2920L series datasheet.
3. **J400/J401 footprint**: now `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal`, a true 5.08 mm-pitch 1x02 screw-terminal footprint (see §10, fix round) — matches the brief's "5.08 mm pitch class" exactly; Datasheet property now set to the Phoenix Contact MKDS 1,5/2-5,08 product page (fix round 2, §11). Still flag for BOM/LCSC confirmation at layout.
4. **JP400/JP401 LCSC**: generic 2.54 mm 2-pin pin header; likely already has a known LCSC number elsewhere in the FC BOM, but none was found in the materials handed to this agent — needs a live lookup or BOM cross-reference.
5. No TVS is fitted on `VSOLAR_BENCH_A`/`VSOLAR_BENCH_B` (brief explicitly makes this optional, with bench-PSU OVP as the primary protection) — confirm this default is acceptable for Phase 1.

## 8. Validation results

_Superseded by the fix-round re-run in §10 — kept here for the pre-fix record; current authoritative numbers are in §10._

### `sch_lint.py`
```
solar_power_injection.kicad_sch: 17 symbol instances, 8 lib symbols, 24 wires, 0 errors, 0 warnings
```

### `harness_erc.sh "Solar Power Injection"` (final run, with emulator_mcu, solar_emulation, pyro_inhibit and bench_io also present from parallel agents)
```
=== ERC delta vs baseline (default: Rev2 + 8 promotions; noise types excluded) ===
sev      type                           base    now  delta
error    pin_not_connected                 5      5     +0
error    pin_to_pin                        0      1     +1
error    power_pin_not_driven              6     12     +6
warning  multiple_net_names               12     12     +0
warning  pin_to_pin                       96    147    +51
warning  same_local_global_label           4      4     +0
warning  single_global_label               9      0     -9
warning  unconnected_wire_endpoint         1      1     +0
total baseline 133, now 182, delta +49
errors: 18

=== violations on sheets matching 'Solar Power Injection' ===
total 0
errors: 0
```
Every non-zero delta line above is attributable to the four other in-progress sheets sharing the harness run (confirmed by `erc_summary.py --sheet "Solar Power Injection" --list --ignore-noise` printing `total 0 / errors: 0` on every run of this validation loop, including the very first run before the other sheets existed). This sheet contributes zero ERC errors and zero ERC warnings.

### Netlist diff (this sheet's contribution, extracted from the full diff)
```
+ VSOLAR_BENCH_A: F400.1, J400.1, TP400.1
+ VSOLAR_BENCH_B: F401.1, J401.1, TP402.1
+ Net-(D400-A): D400.2, F400.2
+ Net-(D400-K): D400.1, JP400.1
+ Net-(D401-A): D401.2, F401.2
+ Net-(D401-K): D401.1, JP401.1
~ GND:    +[J400.2, J401.2] -[]
~ VSOLAR: +[JP400.2, JP401.2, TP401.1] -[]
```
Exactly the existing nets brief §4 says this sheet touches (`VSOLAR`, `GND`), plus the two new local rails it owns (`VSOLAR_BENCH_A/B`) and their internal diode nodes. No existing net lost pins; no unrelated net was touched.

## 9. Deviations from the brief

1. Chose the PTC resettable-fuse option over the "2 A slow-blow" alternative the brief also permits (see open question 2). As of integrator fix round 3 (§12) this is **no longer a deviation**: F400/F401 are Littelfuse 2920L185DR, exactly the brief's "1.85 A polyfuse", and the bench hard maximum is back at the brief's 24 V. (Rounds 1–2 had wrongly concluded no 1.85 A polyfuse existed; that was true only of the two 1812-body series searched.)
2. Interpreted D2's "CH-B footprint-only" as "fully populated, jumper open" rather than "DNP" — see open question 1; reversible (add `(dnp yes)` to the four CH-B refs) if the reviewer disagrees.

No other deviations. All eleven decisions relevant to this sheet (D2 directly; D1, D3–D11 not applicable) are reflected as specified.

## 10. Fix round (independent-verifier findings, addressed)

An independent verifier found four defects in the first version of this sheet. All four are fixed on `solar_power_injection.kicad_sch`; the generator `tools/gen/solar_power_injection_gen.py` was updated to match so a future regeneration reproduces the fix.

1. **[major] F400/F401 rating not a procurable part.** "1.85 A Ihold PTC, 30 V, 1812/4532" does not exist: Littelfuse 1812L Series (datasheet rev 01/10/23) and Bourns MF-MSMF Series both step through fixed Ihold/Vmax combinations with no 1.85 A entry, and every real 1.85 A-class 1812 PPTC in those series tops out at 16 V — below this sheet's own 24 V hard-maximum bench PSU setting, meaning the fuse would be over its voltage rating exactly while tripped and protecting the rail. Re-specified to **Bourns MF-MSMF160/24X**: 1.60 A Ihold, 3.20 A Itrip, 24 V Vmax, 20 A Imax — clears the ≤1.2 A expected bench draw (brief §6.3, from eps_side IC6 R75 = 0.1 Ω) with margin, and 24 V Vmax matches this sheet's bench PSU hard maximum. Changed on the schematic: `Value` "1.85A_PTC" → "1.60A_PTC_24V" on F400 and F401; `Description` on both now names the exact part and its four datasheet ratings; the sheet text note at `(20 186.67)` (uuid `4f91708a`) rewritten to the same facts, plus an added sentence that Itrip (3.2 A) exceeds D400/D401's IF(AV) = 2 A rating, so the bench PSU current limit — not the PTC — is what protects the diode in an overcurrent event. Footprint (`Fuse:Fuse_1812_4532Metric`) is unchanged; both candidate parts are 1812 body size.
2. **[minor] J400/J401 Value/Footprint pitch mismatch, and the report's "no 5.08 mm footprint exists" claim was wrong.** `TerminalBlock_Phoenix.pretty`, `TerminalBlock_CUI.pretty` and `TerminalBlock_RND.pretty` (all present in this KiCad 10 install, distinct from `TerminalBlock.pretty`) each carry a true 1x02 P5.08mm footprint. Changed J400/J401 `Footprint` to `TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal` (verified present on disk); `Value` "Terminal_2P_5.08mm" is now accurate rather than aspirational. Updated both `Description` properties and the sheet text note at `(20 195.56)` (uuid `ecf5f61a`) to match. Open questions 2/3 (§7) and deviation 1 (former §9) updated/removed to stop asserting the false "no 5.08 mm footprint exists" claim — see item 4 below.
3. **[minor] Trailing `(embedded_fonts no)`.** Deleted the stray top-level `(embedded_fonts no)` that was line 3072 of the sheet (a sub-sheet file must end in a plain `)` per brief §7, matching `load_switches.kicad_sch`/`RP2350.kicad_sch`). Also removed the matching `lines.append('%s(embedded_fonts no)' % T1)` from `tools/gen/solar_power_injection_gen.py` so a regeneration stays compliant.
4. **[minor] Report mis-attributed a "Central Semiconductor" claim to the brief.** Neither `00_pm_brief.md` nor `01_brief_critique.md` names a manufacturer other than Comchip for CDBA240LL-HF (01_brief_critique.md §13 already states "C2886093 is the Comchip CDBA240LL-HF"); the "brief's prose implies Central Semiconductor" framing in the original report (§3, §6, former deviation 3) was a fabricated correction with no source. Removed former deviation 3 and the "not Central Semiconductor" clauses from §3 and §6 above; §6 now cites 01_brief_critique.md §13 as the source of the Comchip attribution. No schematic change — D400/D401 (`CDBA240LL-HF`, `Diode_SMD:D_SMA`, LCSC `C2886093`) are unchanged.

### Re-run validation (post-fix)

`sch_lint.py`:
```
solar_power_injection.kicad_sch: 17 symbol instances, 8 lib symbols, 24 wires, 0 errors, 0 warnings
```

`harness_erc.sh "Solar Power Injection"` (with emulator_mcu, solar_emulation, battery_protection_replica, pyro_inhibit and bench_io also present from parallel agents):
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

=== violations on sheets matching 'Solar Power Injection' ===
total 0
errors: 0
```
`erc_summary.py <harness erc.json> --sheet "Solar Power Injection" --list --ignore-noise` independently confirms `total 0 / errors: 0`. Every non-zero delta above belongs to the other five in-progress sheets sharing the harness run (their part counts grew since this sheet's first validation pass, which is why totals moved but this sheet's own contribution did not). This sheet's ERC contribution is unchanged at zero errors, zero warnings before and after the fix — the fixes were part-attribute/footprint/text corrections, not net-topology changes, so no ERC or netlist-diff line changes as a result.

Netlist diff for this sheet's nets is unchanged from §8 (`VSOLAR_BENCH_A`, `VSOLAR_BENCH_B`, the two diode-internal nets per channel, plus pins added to existing `GND`/`VSOLAR`) — confirmed by re-running the harness netlist diff after the fix and finding the same net membership, since none of the four fixes touch a wire, label, or pin connection, only `Value`/`Footprint`/`Description`/text-note strings.

`kicad-cli sch export pdf` on the full fixed hierarchy plots cleanly with no errors, confirming the file parses and the trailing-paren fix did not break the sheet.

## 11. Fix round 2 (independent-verifier findings, addressed)

A second independent verifier found six defects in the fix-round-1 version of this sheet (one major, five minor). All six are fixed on `solar_power_injection.kicad_sch`; `tools/gen/solar_power_injection_gen.py` was updated to match so a future regeneration reproduces the fix.

1. **[major] F400/F401 note (and the jumper-table note) ran off the right edge of the A3 sheet.** The unwrapped F400/F401 note was 532 characters on one line, measured at x = 20 → 420.2 mm on the exported PDF (page width 420 mm, inner border ≈ 397 mm) — `pdftotext` recovered only 359 of 532 characters, losing the entire safety-relevant tail ("...the injection diode is protected by the bench PSU current limit, not by the PTC"). The jumper-table note similarly reached x = 400.1 mm. **Fix:** added a generic `add_note()` helper to the generator that word-wraps every note to ≤150 characters/line (textwrap, no mid-word breaks) and stacks the wrapped lines 2.0 mm apart, with the original 8.89 mm gap preserved between notes. Re-measured on the regenerated PDF (`pdftotext -bbox` on page 8 of the harness-root export, the same method the verifier used): the widest note-block line is now 304.9 mm (the top title paragraph, unchanged/not wrapped since it was already safely inside the frame), and the widest *wrapped* note line is 186.9 mm — both far inside the ~390 mm safe bound. The bottom-most note line now ends at y = 247.9 mm, well clear of the ≈287 mm bottom frame border (confirmed against the row-marker "F" glyph at y = 286.7 mm on the same page). Verified visually too: a 300 dpi crop of the note block (`notes.png` in this task's scratch dir) shows every line fully inside the sheet with no clipping.
2. **[minor] J400/J401 Value text drawn inside the screw-terminal symbol body.** The default `Part` layout placed `Value` at `y + 2.794`, which for the rotated/mirrored `Connector:Screw_Terminal_01x02` body (occupying y 74.93–80.01 for J400, 138.43–143.51 for J401) put the "Terminal_2P_5.08mm" string through the connector graphic and under the pin-number glyphs. **Fix:** added a `value_dy` override to `Part` (default unchanged at 2.794 for every other part on the sheet) and set it to 6.35 for the two screw terminals only, matching the verifier's suggested clear positions exactly: J400 Value now at (50.8, 82.55), J401 at (50.8, 146.05) — both below the body, visually confirmed clear in a 300 dpi crop (`j400.png`/`j401.png`).
3. **[minor] Bench-window note quoted 11.7 V without allowing for the fuse + diode drop this sheet adds.** Added a sentence to the bench-PSU note: the 11.7 V LT3652 start-up threshold is at VSOLAR, downstream of F400/F401 (≤0.3 Ω) and D400/D401 (≈0.25–0.31 V at ≤1.2 A) — a ≈0.4–0.6 V series drop — so the bench terminal must be set to ≥12.3 V (12.5 V recommended), and a terminal reading of exactly 12.0 V will not reliably start the charger. No schematic topology change.
4. **[minor] PTC Vmax margin and Ihold derating basis.** The sheet previously set the bench PSU hard-maximum to 24 V, exactly equal to F400/F401's own Vmax rating — zero margin at the PTC's own trip condition. **Fix (took the first of the verifier's two offered options):** lowered the bench-PSU hard-maximum text from 24 V to **20 V** (still well above the 18 V nominal top, and unaffected by the INA219 26 V / LT3652 32 V limits), giving the 24 V-Vmax PTC 4 V of margin while tripped. Also added the 23 °C Ihold basis (standard PPTC convention, confirmed on the DigiKey MF-MSMF160/24X-2 part page) and a typical-derated figure (~0.85× at 40 °C ambient ≈ 1.36 A) to the F400/F401 note, confirming it still clears the ≤1.2 A expected bench draw with margin at that temperature. No schematic wiring change; only the two text notes and the report's restated facts (§6, open question 2) changed.
5. **[minor] No current rating stated for JP400/JP401.** Added a sentence to the jumper-table note: JP400/JP401 are the only series element in each channel and can see the PTC's 3.2 A Itrip fault current; a 2.54 mm gold-plated shunt is assumed, rated ≥3 A (typical for this pitch), against the ≤1.2 A steady-state channel current, and — since the PTC does not protect the shunt either — the bench PSU current limit must also be set ≤ the shunt rating. No schematic change.
6. **[minor] Datasheet property empty on every part except D400/D401.** Set `Datasheet` on F400/F401 to the Bourns MF-MSMF series datasheet (`https://www.bourns.com/docs/product-datasheets/mf-msmf.pdf`, confirmed as the correct/current URL via three independent search results and cross-checked against the DigiKey MF-MSMF160/24X-2 product page) and on J400/J401 to the Phoenix Contact MKDS 1,5/2-5,08 product page (`https://www.phoenixcontact.com/en-pc/products/pcb-terminal-block-mkds-15-2-508-1715721`, live-verified). Test points, PWR_FLAG/power symbols and the generic jumper header remain blank per the fix's own guidance.

### Re-run validation (post fix-round-2)

`sch_lint.py`:
```
solar_power_injection.kicad_sch: 17 symbol instances, 8 lib symbols, 24 wires, 0 errors, 0 warnings
```

`harness_erc.sh "Solar Power Injection"` (with emulator_mcu, solar_emulation, battery_protection_replica, pyro_inhibit and bench_io also present from parallel agents):
```
=== ERC delta vs baseline (default: Rev2 + 8 promotions; noise types excluded) ===
sev      type                           base    now  delta
error    pin_not_connected                 5      5     +0
error    power_pin_not_driven              6     11     +5
warning  multiple_net_names               12     12     +0
warning  pin_to_pin                       96    164    +68
warning  same_local_global_label           4      4     +0
warning  single_global_label               9      0     -9
warning  unconnected_wire_endpoint         1      1     +0
total baseline 133, now 197, delta +64
errors: 16

=== violations on sheets matching 'Solar Power Injection' ===
total 0
errors: 0
```
`erc_summary.py <harness erc.json> --sheet "Solar Power Injection" --list --ignore-noise` independently confirms `total 0 / errors: 0`. Every non-zero delta above belongs to the other five in-progress sheets sharing the harness run — none of this fix round's changes (text wrapping, Value-field offsets, note wording, Datasheet URLs) touch a wire, label, or pin connection. This sheet's ERC contribution remains zero errors, zero warnings.

Netlist diff for this sheet's nets is unchanged from §8/§10 (`VSOLAR_BENCH_A`, `VSOLAR_BENCH_B`, the two diode-internal nets per channel, plus pins added to existing `GND`/`VSOLAR`) — none of the six fixes touch topology.

**PDF page-geometry re-check** (the method the verifier used, reproduced against the regenerated file): exported the harness-root hierarchy (`$SCRATCH/proj/FlatSat_V1.kicad_sch`, built by `harness_erc.sh`) to PDF, located this sheet at page 8, and ran `pdftotext -bbox` on that page. Result: every note-block line's `xMax` ≤ 304.9 mm (title paragraph, unwrapped, unchanged) / ≤ 186.9 mm (wrapped notes) — both well inside the ~390 mm safe bound the verifier specified — and the bottom-most note line's `yMax` = 247.9 mm, well clear of the ≈287 mm bottom frame border. A 300 dpi render of the note block and of J400/J401 individually confirms no clipping and no text-over-symbol overlap.

`kicad-cli sch export pdf` on both the standalone sheet and the full harness-root hierarchy plots cleanly with no errors.

---

## 12. Integrator fix round 3 (2026-09-14) — brief §6.3 conformance

**Ownership note.** This round was applied by the **integrator**, not by the sheet agent, after an independent
check of the first integration pass. Brief §3 rule 2 puts `solar_power_injection.kicad_sch` and
`tools/gen/solar_power_injection_gen.py` in the *sheet agent's* writable set; the sheet agent's run had already
finished, so the integrator took the file. Recorded as an explicit rule deviation in
`integration_report.md` §1.2.

### 12.1 The finding

> **[major]** solar_power_injection contradicts two explicit brief §6.3 requirements: a 20 V hard maximum
> written into a schematic text note instead of the briefed 24 V, and a 1.60 A PTC instead of the briefed
> "2 A slow / 1.85 A polyfuse".

Both deviations had one root cause: fix rounds 1–2 searched only the Littelfuse **1812L** and Bourns
**MF-MSMF** series, found no 1.85 A part in either, picked the Bourns MF-MSMF160/24X (1.60 A, **24 V** Vmax),
and then had to narrow the brief's 24 V bench maximum to 20 V to keep the PTC inside its voltage rating while
tripped. Hard rule 4 makes a schematic text note a requirement, so the sheet was shipping a requirement that
contradicted the spec.

The premise was wrong: the constraint belongs to the 1812 body size, not to the market. **Littelfuse
2920L185DR** is a stocked 1.85 A polyfuse with 33 V Vmax.

### 12.2 What changed

| item | before | after |
|---|---|---|
| F400/F401 `Value` | `1.60A_PTC_24V` | `1.85A_PTC_33V` |
| F400/F401 `Footprint` | `Fuse:Fuse_1812_4532Metric` | `Fuse:Fuse_2920_7451Metric` |
| F400/F401 `LCSC Part` | *(absent — "needs LCSC")* | **`C207086`** |
| F400/F401 `Datasheet` | Bourns MF-MSMF | Littelfuse 2920L series datasheet |
| F400/F401 `Description` | Bourns ratings | Littelfuse 2920L185DR ratings incl. Rmin / R1max |
| bench-PSU note | "HARD MAXIMUM **20 V** (kept below F400/F401 24 V Vmax…)" | "HARD MAXIMUM **24 V** (brief section 6.3; F400/F401 are 33 V Vmax, so 9 V of margin)" |
| start-up note | "downstream of F400/F401 (**≤0.3 ohm**) … series drop ~0.4–0.6 V" | "downstream of F400/F401 (**R1max 0.150 ohm**) … series drop ~0.4–0.5 V" |
| F400/F401 note | Bourns ratings + "~0.85× … ~1.36 A held" (the wrong variant's derating row) | full 2920L185 Electrical Characteristics row + the verbatim nine-column Temperature Rerating row, "1.54 A at 40 C … 28 % margin" |
| junction dots | redundant dots at (55.88, 76.2) and (55.88, 139.7), on J400/J401 pin 1 where only the pin and one wire end meet | **deleted** (7 junctions, was 9) |

Both the sheet and `tools/gen/solar_power_injection_gen.py` were changed; the sheet on disk is the generator's
own output (the generator re-rolls item uuids each run, so the sheet's header uuid
`a4833db2-7816-47df-981b-8e3870abec60` was restored afterwards to keep the file's identity stable).

`R1max 0.150 Ω` is the *post-trip, one-hour* maximum resistance, the conservative figure for the start-up-drop
calculation; `Rmin` is 0.050 Ω. At 1.2 A that is 0.18 V, plus 0.25–0.31 V of Schottky, so the ≥12.3 V
(12.5 V recommended) bench setpoint conclusion is unchanged.

### 12.3 Provenance for the new part

- **LCSC `C207086`** verified in the JLCPCB catalogue mirror
  `~/Documents/KiCad/10.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/parts-fts5.db`
  (opened read-only): `C207086 | 2920L185DR | 2920 | Littelfuse | Extended | -40℃~+85℃ 1.25mm 1.5W 1.85A
  150mΩ 2.5s 3.7A 33V 40A 5.44mm 50mΩ 7.98mm | … | stock 14433`. Rule 5 satisfied (catalogue-verified, not
  guessed). `jlcpcb/project.db` was **not** written.
- **Datasheet**: Littelfuse *PolySwitch® Resettable PPTC — 2920L Series, Surface Mount* (© 2024). Electrical
  Characteristics and Temperature Rerating rows quoted in §6 above were extracted from the PDF, not from a
  search summary.
- **Footprint** `Fuse:Fuse_2920_7451Metric` exists in the KiCad 10 standard library
  (`/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/Fuse.pretty/`), pads 1.925 × 5.45 mm at
  ±3.3875 mm — an IPC land for the datasheet's 7.98 × 5.44 mm max body.

### 12.4 Re-run validation (fix round 3, as delivered)

```
python3 tools/sch_lint.py solar_power_injection.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/88d5f13b-6a4a-4f50-805f-872821082e52 --refdes-block 400-449
  -> 17 symbol instances, 8 lib symbols, 24 wires, 0 errors, 0 warnings

python3 tools/gen/geomcheck.py solar_power_injection.kicad_sch --overlaps
  -> 24 wires, 60 text bodies; wire-through-text: 4 (all pre-existing, identical to the pre-edit file);
     text-over-text: 0

kicad-cli sch erc --severity-all (full integrated project)
  -> erc_summary.py --sheet "Solar Power Injection" --ignore-noise : total 0, errors: 0
```

Netlist contribution unchanged pin-for-pin (`VSOLAR_BENCH_A` = F400.1/J400.1/TP400.1,
`VSOLAR_BENCH_B` = F401.1/J401.1/TP402.1, `GND` +[J400.2, J401.2], `VSOLAR` +[JP400.2, JP401.2, TP401.1]);
a junction dot and a footprint/value/property are not netlist objects.

PDF page 8 of the integrated export re-read at 150 dpi: both channels and all eight note blocks render inside
the frame, no clipping, and the two redundant dots on J400/J401 pin 1 are gone.

### 12.5 Still open after this round

1. J400/J401 (Phoenix MKDS-1,5-2-5.08) and JP400/JP401 (generic 2.54 mm 1×02 header) still need LCSC numbers.
   F400/F401 no longer do.
2. No TVS on `VSOLAR_BENCH_A/B` — brief-permitted default, confirm for Phase 1.
3. D2 "CH-B footprint-only" reading (populated, shunt open) — the skeptic round judged this settled by §6.3's
   own restatement; left as built.

---

## 13. Review fixes (Fable review-and-fix round, 2026-09-14)

Ids applied to this sheet's owner set: **12**.

| id | severity | title | disposition | what changed |
|---|---|---|---|---|
| 12 | minor | `power_monitor_test` (proves-core-reference) requires CH-A solar injection live but is tagged `requires_battery` only — undocumented on the FlatSat bench procedure | fix-now, documentation-only | Added §5.1 "Bench-procedure note — flight-software tests that depend on this sheet", carrying the required note verbatim plus the terminal-setpoint and bench-window qualifiers already established in §11.3 / §12.2. |

### 13.1 Evidence for id 12

`/Users/ncc-michael/GitHut/proves-core-reference/PROVESFlightControllerReference/test/int/power_monitor_test.py`:

```python
pytestmark = [pytest.mark.requires_battery]
...
ina219SolManager = "ReferenceDeployment.ina219SolManager"
...
    sol_voltage = get_voltage(fprime_test_api, ina219SolManager)
...
    assert sol_voltage != 0, "Solar voltage reading should be non-zero"
```

One marker (`requires_battery`), no solar/CH-A marker, but a hard non-zero assertion on the solar
INA219's bus voltage. `ina219SolManager` = U8 (0x41), IN+ on `VSOLAR` (§6), which on the FlatSat is
driven only through this sheet's CH-A path `J400 → F400 → D400 → JP400 → VSOLAR`. Sibling copies of
the same file under `~/GitHut/proves-cd/.../FprimeZephyrReference/test/int/` and
`~/.warp/worktrees/proves-core-reference/*/` carry the identical `pytestmark` line, so this is the
upstream state, not a local edit.

`test_02_total_power_consumption` (`total_power != 0`) does not depend on CH-A; only
`test_01_power_manager_readings` does.

### 13.2 Scope of the change

- **No `.kicad_sch` edit.** JP400 already defaults shunt-fitted/closed per brief D2 and §5, so the
  hardware is already in the state the test needs; the gap is in the bench procedure, not the sheet.
- **No `tools/gen/solar_power_injection_gen.py` edit,** for the same reason — the generator emits the
  schematic, and the schematic is unchanged, so a regeneration still reproduces the sheet byte-for-byte
  in netlist and note content. The generator/sheet parity convention is therefore preserved trivially.
- Netlist contribution, ERC contribution, parts table, jumper defaults and footprints are all untouched
  by this round.

### 13.3 Re-run validation (post review-fix)

`python3 tools/sch_lint.py solar_power_injection.kicad_sch --project FlatSat_V1 --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/88d5f13b-6a4a-4f50-805f-872821082e52 --refdes-block 400-449`

```
solar_power_injection.kicad_sch: 17 symbol instances, 8 lib symbols, 24 wires, 0 errors, 0 warnings
```

`SCRATCH=.../review_fix_solar_power_injection tools/harness_erc.sh "Solar Power Injection"`

```
=== violations on sheets matching 'Solar Power Injection' ===
total 0
errors: 0
```

Full harness output and the re-exported PDF page 9 read-back are recorded in the fixer's structured
`verification` field. Unchanged from §12.4, as expected for a documentation-only round.
