# FlatSat V1 Phase 1 — integration report

**Date:** 2026-09-14 · **Role:** integrator · **Spec:** `00_pm_brief.md` rev 2, §4.3 / §5 / §7 / §9
**Project root:** `/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/FlatSat_V1.kicad_sch`
(root uuid `c64c0d72-a9f6-4f3a-891e-1f647558f538`)
**Companion:** `connector_trace.md` (brief §9 connector table) in this directory.
**Artifacts:** `<scratch>/work_integrate2/{erc.json, netlist.kicadxml, netlist_diff.txt, FlatSat_V1.pdf}`
(pass 1 artifacts remain in `<scratch>/work_integrate/`)
where `<scratch>` = `/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad`.

---

## 0. Verdict

| exit criterion (brief §10) | result |
|---|---|
| ERC clean on all six new sheets — **no errors** | **met.** 0 errors on every new sheet. All 11 project errors are byte-identical to the Rev2 baseline. |
| warnings triaged | **met.** §5 below: 17 non-noise non-`pin_to_pin` warnings, all baseline; 68 new `pin_to_pin`, all library-metadata; 146 new library-metadata noise warnings (`lib_symbol_mismatch` +129, `lib_symbol_issues` +17). **`footprint_link_issues` is back at the baseline 23 (+0)** — the one new warning with real content (U303's dangling footprint) was fixed in pass 2, §2.5.1. |
| every connector-facing net traced | **met.** `connector_trace.md`, 26 populated connectors pin by pin + 6 unpopulated, plus a global-net carrier table. |
| §4.3 promotions still read as eight pure renames | **met.** §3: all eight retain 100 % of their Rev2 membership, nothing renamed or merged elsewhere. |
| no existing net lost pins; additions only | **met.** §4: 0 nets removed (beyond the eight renames), 0 pins lost on any of the 215 Rev2 nets, 125 nets added, 216 components added, 0 removed. |
| D1–D11 reflected | **met** in the sheets; D11 carries an open PM question, §7. D2 is settled as built (§7 O-list). |
| S-band approach recorded (D5) | **met, documentary only.** Radiated-only on the bench for Phase 1, **no schematic change**: U30 has no antenna net on this board, and a module variant or pigtail is a mechanical/procurement decision carried in the plan's risk list. The two `pin_not_connected` errors on U30 pins 14/15 (DIO2/DIO3) in §5.3 are the Rev2 baseline's, unchanged. |

---

## 1. What the integrator changed

Files written (all atomically, `<file>.tmp` + `os.replace`):

| file | pass | change |
|---|---|---|
| `FlatSat_V1.kicad_sch` | 1 | six hierarchical sheet symbols per brief §5 + the required title text block. |
| `symbols/flatsat.kicad_sym` | 1 | populated with the six `flatsat:*` symbols the new sheets embed (was an empty 5-line stub). |
| `load_switches.kicad_sch` | 1 | one pin-type token, `Power_Management:AP22652` pin 6 `output` → `power_out` (cross-sheet ERC fix, §2.1). |
| `emulator_mcu.kicad_sch` + `tools/gen/emulator_mcu_gen.py` | 1 / 2 | C200 `10uF`/`C19702` → `1uF`/`C15849` + Description (cross-sheet `VBUS_EMU` bulk-capacitance fix, §2.2); the generator was brought into line in pass 2. |
| *(deleted)* `out.log`, `final_out.log` | 1 | two 50 kB stray harness logs left in the project directory by a sheet agent; `harness_erc.sh` rsyncs the project, so they were being copied into every harness run. |
| `solar_emulation.kicad_sch` + `tools/gen/solar_emulation_gen.py` | 2 | U303 footprint `VSSOP-10` → `TSSOP-10` (instance **and** `lib_symbols` default); R304 0805 → 2010; address-collision warning note (§2.5.1–2.5.3). |
| `solar_power_injection.kicad_sch` + `tools/gen/solar_power_injection_gen.py` | 2 | F400/F401 re-spec'd to Littelfuse 2920L185DR (`C207086`, 33 V); bench hard maximum restored to the brief's 24 V; derating and PTC-resistance figures corrected; two redundant junction dots deleted (§2.5.4). |
| `pyro_inhibit.kicad_sch` + `tools/gen/pyro_inhibit_gen.py` | 2 | LED600 `Value` `LED_GREEN` → `LED` + Datasheet; R602 `1k`/`C11702` → `470R`/`C25117`; note line added (§2.5.5). |

`eps_side.kicad_sch` and `sym-lib-table` needed no change (see §2.3, §2.4).
`FC_V5e_Production_Rev2/` untouched (`find … -newermt "2026-09-14 01:00"` → empty).
`jlcpcb/project.db` untouched (mtime 00:20, before any agent ran). No GUI, no commit, no stray `.tmp` or
`.log` left in the project.

### 1.2 Ownership exceptions — explicit brief §3 rule 2 deviations

Brief §3 rule 2 limits the integrator to `FlatSat_V1.kicad_sch`, `eps_side.kicad_sch`,
`load_switches.kicad_sch`, `symbols/flatsat.kicad_sym` and `sym-lib-table`. **Four sheet files outside that
set were written**, each because the defect was invisible from inside the sheet or because the owning agent's
run had already ended and the fix was required to close a checker finding:

| file written | rule-2 owner | why the integrator took it | needs PM acknowledgement? |
|---|---|---|---|
| `emulator_mcu.kicad_sch` (+ `tools/gen/emulator_mcu_gen.py`, + report §12) | emulator_mcu agent | genuinely cross-sheet: 20.1 µF on `VBUS_EMU` is only visible once `bench_io`'s 10 µF and this sheet's 10 µF are in the same netlist, and `bench_io`'s report escalated it to the integrator by name. C15849 comes from the as-ordered Rev2 BOM (rule 5). | yes — and confirm **O6** (11.1 µF nominal / ≈ 8 µF derated) is accepted |
| `solar_emulation.kicad_sch` + its generator | solar_emulation agent | pass-2 checker findings (unplaceable U303 footprint, R304 over its rating, missing address-collision note); the sheet agent had finished. | yes |
| `solar_power_injection.kicad_sch` + its generator | solar_power_injection agent | pass-2 checker finding: the sheet shipped a text note (= a requirement, hard rule 4) contradicting brief §6.3 on two points. | yes |
| `pyro_inhibit.kicad_sch` + its generator | pyro_inhibit agent | pass-2 checker finding: LED600 `Value`/LCSC contradiction and a 2–6× current error. | yes |

In every case the **generator** under `tools/gen/` was changed as well as the sheet, so a regeneration cannot
reintroduce the defect. For the three pass-2 sheets the delivered file **is** that generator's own output;
since the generators re-roll every item uuid on each run, each sheet's **header uuid was restored** afterwards
to keep the file's identity stable (`b052df5b-…` solar_emulation, `a4833db2-…` solar_power_injection,
`f09ab68d-…` pyro_inhibit). `emulator_mcu.kicad_sch` was edited in place (a three-property change, pass 1) and
`tools/gen/emulator_mcu_gen.py` line 469 was brought into line with it, so a regeneration there now reproduces
the delivered values too. No other agent's file was touched.

A fifth, narrower exception is `load_switches.kicad_sch` (§2.1): that file **is** in the integrator's writable
set, but the PM context says the FC portion "must not change beyond those promotions", so the one-token
pin-type edit needs a PM acknowledgement too. See §2.1 and the FC-findings list in §7a.

### 1.1 Sheet symbols added to the root (brief §5, verbatim)

| Sheetname | Sheetfile | sheet symbol uuid | page | at (mm) | size (mm) |
|---|---|---|---|---|---|
| Emulator MCU | `emulator_mcu.kicad_sch` | `8394a2ec-8c1e-41a1-b086-be3289cedfbc` | 7 | 33.02, 154.94 | 35.56 × 12.7 |
| Solar and Sensor Emulation | `solar_emulation.kicad_sch` | `0ec7a68a-65de-4eda-8407-9dcf20e51c0b` | 8 | 71.12, 154.94 | 35.56 × 12.7 |
| Solar Power Injection | `solar_power_injection.kicad_sch` | `88d5f13b-6a4a-4f50-805f-872821082e52` | 9 | 109.22, 154.94 | 35.56 × 12.7 |
| Battery Replica and Bench Power | `battery_protection_replica.kicad_sch` | `bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0` | 10 | 33.02, 176.53 | 35.56 × 12.7 |
| Pyro Inhibit and Jumpers | `pyro_inhibit.kicad_sch` | `ba398093-e7fc-4f25-8f04-4265c3e55b54` | 11 | 71.12, 176.53 | 35.56 × 12.7 |
| Bench IO | `bench_io.kicad_sch` | `54b8f29e-9dcb-4e24-99b9-415a110b338a` | 12 | 109.22, 176.53 | 35.56 × 12.7 |

Plus `(text "PROVES FlatSat V1 additions — see docs/flatsat/2026-09-14_phase1_schematic/")` at (40.64, 196.85),
size 1.27, justify left top.

**Placement verified visually** on page 1 of `<scratch>/work_integrate/FlatSat_V1.pdf`, rendered at 300 dpi and
read. The 2 × 3 block sits in the free area below the RP2350 sheet symbol (that sheet spans y 86.36–149.86,
its `Sheetfile` annotation ends at y ≈ 152.1) and left of the root's `RX0`/`TX0`/`D1`/`D2`/`D3`/`R3`/`R4`/`R80`
group (x ≥ 148.59). Nothing overlaps.

Two placement adjustments were needed after the first render, both cosmetic and both on the root only:

1. The title text as first placed (size 1.778 at x 33.02, y 193.04) ran 93 mm wide, reaching the `R3`/`RX0`
   column, and its left end grazed the `H1 MountingHole` annotation. Moved to (40.64, 196.85) at size 1.27
   (the size the root's other notes use), width ≈ 66 mm, clear of both.
2. `File: battery_protection_replica.kicad_sch` is 42 characters ≈ 40 mm at 1.27 mm, and the row-2 column
   pitch is 38.1 mm, so it ran into `File: pyro_inhibit.kicad_sch`. That one sheet's `Sheetfile` property was
   dropped 2.54 mm (y 189.8146 → 192.3546) and its block set to `(fields_autoplaced no)` so Eeschema keeps
   the position. The sheet symbol itself is exactly where brief §5 puts it.

### 1.2 `symbols/flatsat.kicad_sym`

Populated from the `lib_symbols` blocks the new sheets already embed (so the library and the sheet caches are
byte-identical apart from the stripped `flatsat:` prefix — no new `lib_symbol_mismatch` is introduced):

| symbol | used by |
|---|---|
| `3V3_EMU` | emulator_mcu (9 instances) |
| `VBUS_EMU` | emulator_mcu (1), bench_io (1) |
| `VSOLAR_BENCH` | solar_power_injection (2: `VSOLAR_BENCH_A`, `VSOLAR_BENCH_B` via the Value field) |
| `VBUS_CHG` | battery_protection_replica (3) |
| `IRF7458` | battery_protection_replica (2: Q500, Q501) |
| `R5460N208AA` | battery_protection_replica (1: U500) |

`flatsat:VBAT_BENCH` is **not** included: `battery_protection_replica` deliberately dropped that net
(brief §6.4 contradiction, §7 item O1), so nothing references it. The pantry file
`<scratch>/pantry/flatsat_VBAT_BENCH.sexp` remains unused.

Validated: `kicad-cli sym export svg` plots all six; `kicad-cli sym upgrade` reports "Symbol library was not
updated" (already current format, `(version 20251024)`). The `sym-lib-table` entry
`(lib (name "flatsat") … "${KIPRJMOD}/symbols/flatsat.kicad_sym")` already existed and was left as is.

**Result:** the ERC report previously carried `lib_symbol_issues` "Symbol 'X' not found in symbol library
'flatsat'" for `3V3_EMU` ×9, `VBUS_EMU` ×2, `VSOLAR_BENCH`, `VBUS_CHG`, `IRF7458`, `R5460N208AA`.
A grep of the final `erc.json` for the string `flatsat` returns **0 hits**.

---

## 2. Cross-sheet defects found and fixed

### 2.1 `load_switches.kicad_sch` — AP22652 pin 6 retyped `output` → `power_out`

**Symptom.** Six ERC **errors**, `power_pin_not_driven`, on `/Solar and Sensor Emulation/`:
U300, U310, U311, U312, U313, U314 pin 8 `[VCC, Power input]`, i.e. every TCA4311A whose VCC sits on a face
rail `F0_PWR`…`F5_PWR`. This is the blocker that made `solar_emulation` fail its verification round.

**Root cause.** `F0_PWR`…`F5_PWR` are driven by the AP22653 load switches U19/U21/U22/U23/U24/U27, whose
cached symbol `Power_Management:AP22652` (defined only in `load_switches.kicad_sch`, line 603) types pin 6
"Output" as `output`, not `power_out`. Nothing on those rails therefore counts as a power source. Brief §4.2's
premise "the FC already has power-output pins on those" is **false** for `Fn_PWR` — this should be corrected in
the brief (§7 item O2).

**Why it had to be fixed here.** `solar_emulation` cannot fix it: retyping the TCA4311A VCC pin in its own
`lib_symbols` still leaves one error (the stock TMP112 V+ and DRV2605L VDD pins on `F0_PWR` are `power_in`),
and brief §4.2 forbids a `PWR_FLAG` on `Fn_PWR`. `erc_exclusions` were ruled out: the project has none today
and KiCad keys them to item identity, which the sheet generators re-roll on every run.
`load_switches.kicad_sch` is an integrator-owned file (brief §3 rule 2).

**The edit.** Exactly one token, exactly one occurrence:

```
                (pin output line            ->      (pin power_out line
                    (at 11.43 5.08 180)                  (at 11.43 5.08 180)
                    (length 2.54)                        (length 2.54)
                    (name "Output"                       (name "Output"
                    …  (number "6")                      …  (number "6")
```

**Netlist impact: none.** Pin *type* is ERC metadata; it carries no net membership and no footprint. The
netlist diff in §4 shows every `Fn_PWR` net gaining only `solar_emulation` pins and losing nothing, and no
`load_switches`-internal net changed at all.

**ERC impact, measured:** `power_pin_not_driven` 12 → 6 (= the Rev2 baseline count), project errors 17 → 11,
`/Solar and Sensor Emulation/` 6 errors → 0. One extra `pin_to_pin` warning appears on that sheet
(`U310 pin 7 SDAOUT [Unspecified]` vs `R312 pin 2 [Passive]`) — the same Unspecified-pin class as the other
51 there; KiCad re-emits it once the error that suppressed it is gone.

**Note for the record — needs PM acknowledgement.** This is the only change to an FC heritage file beyond the
eight §4.3 promotions, and the PM context says the FC portion "must not change beyond those promotions", so it
is flagged rather than assumed. It is metadata-only: it does not alter the netlist, the PCB, the BOM or any
footprint, and it is arguably a correction — an AP22653 load-switch output really is a power output.

Diffed byte-for-byte against the read-only baseline `FC_V5e_Production_Rev2/load_switches.kicad_sch`, the
removed lines group to exactly: 91 × `(project "FC_V5e_Production_Rev2")` (the project rename), 3 ×
`(justify left bottom)`, 3 × `(label "Deploy1_EN"/"Deploy2_EN"/"Heater_EN")` (the §4.3 promotions), one `)`,
and **one** `(pin output line`. Nothing else on the sheet moved. `eps_side.kicad_sch` shows only its five
promotions plus the project rename. `netlist_diff.py` reports 0 removed components, an empty
`~ ref: old -> new` section, and 0 baseline nets losing pins.

There is no installed `Power_Management:AP22652` library symbol at all (the project already carries 7
pre-existing `lib_symbol_issues` "Symbol AP22652 not found in symbol library Power_Management"), so there is
no library for a GUI *Update Symbols from Library* to silently revert the fix from. Carried to the FC-findings
list (§7a item **F3**) so the upstream FC project gets the same symbol-quality fix if it ever adopts a real
AP22652 symbol.

### 2.2 `emulator_mcu.kicad_sch` — C200 10 µF → 1 µF (`VBUS_EMU` bulk capacitance)

**Symptom.** Neither sheet could see this alone. `bench_io` fits C701 = 10 µF at the USB-C connector
(brief §6.6 "with bulk cap"); `emulator_mcu` independently fitted C200 = 10 µF + C201 = 100 nF as the LDO
input caps on the same net. Combined: **20.1 µF** on `VBUS_EMU`, against the USB 2.0 §7.2.4.1 limit of 10 µF
of bypass capacitance a downstream device may present. `bench_io`'s report escalated exactly this to the
integrator ("drop one of the two 10 µF caps or explicitly accept the derated total").

**Reference check.** The FC's own J12 `VBUS` carries **no** bypass cap (it goes straight through D15 to
`VBUSP`). `proves_radio_stick_V2` — the PROVES board closest to this topology, RP2350 + USB-C + regulator —
carries exactly **one 10 µF** (C15) on VBUS. One 10 µF is the house pattern.

**The edit.** C200 on `emulator_mcu`: Value `10uF` → `1uF`, `LCSC Part` `C19702` → **`C15849`**
(1 µF, `C_0603_1608Metric`, taken from the as-ordered `FC_V5e_Production_Rev2/jlcpcb/production_files/BOM-*.csv`
line `1uF,"C37,C4,C41",C_0603_1608Metric,C15849,3` — rule 5 satisfied), footprint unchanged, Description
updated to name it the AP2112K input capacitor. 1 µF is the AP2112 datasheet's own recommendation
(BCD/Diodes AP2112 Rev 2.0 p.1, "stable with 1.0 µF").

**Result.** `VBUS_EMU` now carries C701 10 µF (bench_io, at the connector) + C200 1 µF + C201 100 nF =
**11.1 µF nominal**. Both large parts are X5R/X7R multilayer ceramics on a 5 V rail, where DC-bias derating of
20–30 % is normal, so the *effective* bypass capacitance is ≈ 8 µF — at or under the USB limit, and in line
with the radio stick's single nominal 10 µF. **Residual:** 11.1 µF nominal is still 11 % over the literal
§7.2.4.1 number; recorded as open item O6 rather than pushed further, because taking it lower would mean
under-bulking the LDO input. No netlist change (value/property edit only).

### 2.3 The eight §4.3 promotions — verified, not re-applied

The brief records the promotions as already done by the PM before any sheet agent ran, and the files confirm
it: `eps_side.kicad_sch` and `load_switches.kicad_sch` contain **zero** `(label "…")` items with any of the
eight names and exactly one `(global_label "…")` each, at the anchor and rotation brief §4.3 tabulates, every
one with `(shape passive)`, `(fields_autoplaced yes)` and the hidden
`(property "Intersheetrefs" "${INTERSHEET_REFS}" … (hide yes))`:

| sheet | name | anchor | rotation | shape |
|---|---|---|---|---|
| load_switches | `Deploy1_EN` | 223.52, 81.28 | 0 | passive |
| load_switches | `Heater_EN` | 223.52, 86.36 | 0 | passive |
| load_switches | `Deploy2_EN` | 223.52, 88.9 | 0 | passive |
| eps_side | `B-` | 134.62, 187.96 | 0 | passive |
| eps_side | `VBATT_SENSE` | 165.1, 110.49 | 270 | passive |
| eps_side | `INHIB_1` | 199.39, 57.15 | 0 | passive |
| eps_side | `INHIB_2` | 199.39, 68.58 | 0 | passive |
| eps_side | `IN_RBF` | 223.52, 57.15 | 0 | passive |

No other sheet carries a global label or power symbol with any of those eight names, so nothing was merged by
accident. **No edit was made to `eps_side.kicad_sch`.** §3 proves the electrical result.

### 2.4 Cross-sheet checks that came back clean

| check | method | result |
|---|---|---|
| duplicate refdes across sheets | parsed all 477 components of the integrated netlist | **0 duplicates** |
| refdes outside its §5 block | ditto, per sheetpath | **0 out of block**; no collision with the FC maxima (R124, C80, D15, J30, U30, SW2, TP13, L5, Y1, JP6, IC6, BT1, H2, `#PWR172`, no `#FLG`) |
| `#PWR`/`#FLG` collisions | grep across the six sheets | `#PWR200-243`/`#FLG200-201`, `#PWR301-332`, `#PWR400-403`/`#FLG400-401`, `#PWR500-519`/`#FLG500-503`, `#PWR600-601`, `#PWR701-718`/`#FLG701` — disjoint, all ≥ 200 |
| a contract net spelled differently on two sheets | `single_global_label` count | **0** project-wide (Rev2 baseline had 1, `USBBOOT`, now resolved by bench_io). A global label appearing only once is exactly the misspelling signature; zero means every one of the 39 new globals found its partner. |
| all 39 §4.2 new globals present | looked each name up in the netlist by hand | **39/39 present**, each with the members brief §4.2 predicts — see `connector_trace.md` §2b |
| a rail with no driver | `power_pin_not_driven` delta | **+0** after the §2.1 fix |
| `PWR_FLAG` on a forbidden net | inspected every `#FLG` | 10 flags: `1V1_EMU`, `VREG_AVDD_EMU` (emulator_mcu), `VSOLAR_BENCH_A/B` (solar_power_injection), `VBAT_BENCH_N`, `VBUS_CHG`, `CHG_DVIN`, charger `SW` (battery_protection_replica), `VBUS_EMU` (bench_io). None on `GND`, `+3V3`, `VSOLAR`, `Dir_Chrg_In`, `VBUSP`, `B-`, `VBATT_SENSE` or any `Fn_PWR`. |
| `_Bridged` jumper symbols | grep | **none**; every jumper is `Jumper:Jumper_2_Open` or `Connector_Generic:Conn_01x02` |
| stray FC global label on a new sheet | the netlist itself: a stray name would merge an FC net | no new-sheet pin lands on `TX0`, `SDA1`, `SWCLK`, `SWDIO`, `USB_DP`, `USB_DM`, `BOOTSEL`, `+1V1` or any other FC signal — see §4's changed-net list, which is exactly the brief §4.1 set |
| lint, all six sheets | `tools/sch_lint.py` with each sheet's project path and refdes block | 0 errors, 0 warnings on all six (§6) |

---

### 2.5 Pass 2 — sheet-owner defects fixed by the integrator

An independent check of pass 1 returned nine discrepancies. Five were documentary (§0, §1.2, §2.1, §7) and
four needed schematic edits on sheets the integrator does not own; those four are below, with the ownership
exception recorded in §1.2 and the full detail in each sheet's own report (`sheet_<key>.md` §12).

#### 2.5.1 `solar_emulation` U303 — `Package_SO:VSSOP-10_3x3mm_P0.5mm` does not exist (was §5.4 W9 / O3)

The name is inherited verbatim from the `XY_Face_V4` reference board, but KiCad 10's `Package_SO.pretty`
carries only `TSSOP-10_3x3mm_P0.5mm` and `HVSSOP-10-1EP_3x3mm_P0.5mm…`. Effect: one `footprint_link_issues`
warning (project 23 → 24, reported under sheet path `/`, which is why a per-sheet filter missed it) and
**layout could not place U303**. A dangling library reference is not a footprint, so brief §6 ("Every part
carries Reference, Value, Footprint…") was not met.

Changed to `Package_SO:TSSOP-10_3x3mm_P0.5mm` — same 3 × 3 mm body, 0.5 mm pitch, 10 pins, no thermal pad,
which is the DRV2605L **DGS** land — in **both** places the string appeared: the U303 instance and the cached
`lib_symbols` default for `Driver_Haptic:DRV2605LDGS`. The generator now applies the correction through a
`LIB_FIXUPS` table in `lib_block()`, so neither a regeneration nor a GUI *Update Symbols from Library* can put
the dangling name back.

**Measured:** project `footprint_link_issues` **24 → 23 = the Rev2 baseline (+0)**. A fresh sweep of all **39**
distinct footprints used by the six new sheets against `fp-lib-table` + the KiCad standard libraries + the
user's `easyeda2kicad.pretty` returns **0 unresolved**.

#### 2.5.2 `solar_emulation` R304 — 0.253 W in an 0805 (was O-list, raised by the pass-1 verifier)

`3.3 V² / 43 Ω = 0.253 W` at the DRV2605L's supply-limited maximum — 200 % of a stock 0805 thick-film part's
0.125 W and 101 % of a 1206 — mitigated only by the qualitative instruction "drive in bursts". Package raised
to `Resistor_SMD:R_2010_5025Metric` (0.75 W = **34 % of rating**, so continuous full-amplitude drive is within
spec), `Description` updated, and the sheet note now carries a numeric **≤ 50 % duty** limit instead of "in
bursts". Value stays 43 Ω; R304 still has no LCSC and stays on the needs-LCSC list (O9). R304 is the
coil-emulation dummy load, removed when a real magnetorquer is plugged into J300, and is on no flight path.

#### 2.5.3 `solar_emulation` — no "do not mix real and emulated boards" note

Every emulated channel reproduces its real board's address map on the same TCA9548 channel, and the FC
connectors stay populated (D11 keeps J14 populated on purpose — `connector_trace.md` shows `F1_SDA` still on
J9.6, `BATT_SDA` on J14.10, `SDA_Top` on J16.5). Plugging a real board in is therefore an **address clash**,
not merely a duplicate load. The equivalent warning existed only on `battery_protection_replica` (the D11 note
about J14). Two lines appended to the sheet's I2C-map note:

```
DO NOT plug a real face board into J1/J2/J6/J9/J11/J13, a real pack into J14 or a real top-cap
into J16 while this emulation is fitted: both answer at one address on that channel (D11).
```

The note column is vertically packed, so the three blocks below shift down 2 × 2.0574 mm; the last (the D7
note) ends at y = 121.4 mm, clear of the row-2 channel rectangles at y = 123.19 mm. Confirmed in the render.

#### 2.5.4 `solar_power_injection` — two brief §6.3 contradictions, one root cause (was O5)

The sheet carried `(text "Bench PSU setting: … HARD MAXIMUM 20 V …")` where brief §6.3 mandates **24 V**, and
`1.60A_PTC_24V` (Bourns MF-MSMF160/24X) where brief §6.3 asks for "2 A slow or **1.85 A polyfuse**". Hard rule
4 makes a schematic text note a requirement, so the sheet was shipping a requirement that contradicted the
spec. Both came from one wrong premise: rounds 1–2 searched only the Littelfuse **1812L** and Bourns
**MF-MSMF** series, found no 1.85 A part, and then had to narrow the bench maximum to keep the 24 V-Vmax part
inside its rating while tripped. The constraint belongs to the 1812 body size, not to the market.

Re-spec'd to **Littelfuse 2920L185DR**, LCSC **`C207086`** — the brief's own "1.85 A polyfuse", in a 2920
body:

| | before | after |
|---|---|---|
| `Value` | `1.60A_PTC_24V` | `1.85A_PTC_33V` |
| `Footprint` | `Fuse:Fuse_1812_4532Metric` | `Fuse:Fuse_2920_7451Metric` |
| `LCSC Part` | *(absent, "needs LCSC")* | **`C207086`** |
| `Datasheet` | Bourns MF-MSMF | Littelfuse 2920L series |
| bench note | "HARD MAXIMUM **20 V**" | "HARD MAXIMUM **24 V** … F400/F401 are 33 V Vmax, so 9 V of margin" |
| derating figure | "~0.85× … ~1.36 A held" (the *wrong variant's* row) | the verbatim nine-column Temperature Rerating row; **1.54 A at 40 °C**, 28 % margin over the ≤ 1.2 A bench draw |
| PTC resistance | "≤ 0.3 ohm" (not from any datasheet) | "**R1max 0.150 ohm**" (Rmin 0.050 Ω) |
| junction dots | redundant dots at (55.88, 76.2) and (55.88, 139.7) on J400/J401 pin 1, where only the pin and one wire end meet | **deleted** — 7 junctions, was 9 |

Datasheet provenance: Littelfuse *PolySwitch® Resettable PPTC — 2920L Series* (© 2024), Electrical
Characteristics row `2920L185 / LF185` → Ihold 1.85 A, Itrip 3.70 A, Vmax 33 Vdc, Imax 40 A, Pd 1.50 W, max
time to trip 2.50 s at 8.00 A, Rmin 0.050 Ω, R1max 0.150 Ω; Temperature Rerating row `2920L185` →
2.80 / 2.47 / 2.17 / 1.85 / 1.54 / 1.39 / 1.22 / 1.07 / 0.85 A at −40 / −20 / 0 / 20 / 40 / 50 / 60 / 70 / 85 °C.
LCSC `C207086` verified in the JLCPCB catalogue mirror `parts-fts5.db` (opened read-only): *Littelfuse
2920L185DR, 2920, Extended, 14 433 in stock* — rule 5 satisfied without writing `jlcpcb/project.db`.

`Fuse:Fuse_2920_7451Metric` exists in the KiCad 10 standard library, pads 1.925 × 5.45 mm at ±3.3875 mm, an
IPC land for the datasheet's 7.98 × 5.44 mm maximum body.

#### 2.5.5 `pyro_inhibit` LED600 — `Value` contradicts its LCSC, and the current was wrong (was O4)

`LED_GREEN` with LCSC `C2290`, which is Hubei KENTO **KT-0603W, a white 0603** (Vf 2.6–3.1 V, 360 mcd at
5 mA, 100 mW, Basic — verified in `parts-fts5.db`). Two consequences: a grouped BOM keyed on
(value, footprint, LCSC) would emit **two lines for one part number** (`LED / C2290` is what `emulator_mcu`
D201/D202 and `battery_protection_replica` D510 carry), and R602 = 1 k off 3.3 V actually gave
**0.2–0.8 mA**, not the "≈ 1.3 mA" the sheet report claimed for a ~2.0 V green part — nearly dark at
worst-case Vf, for a *safety* indicator.

Fixed: `Value` → `LED`; `Datasheet` → the KT-0603W datasheet URL; `Description` now names the part and its Vf.
R602 `1k`/`C11702` → **`470R`/`C25117`** (UNI-ROYAL 0402WGF4700TCE, 470 Ω 0402 1 % **Basic**, 1.36 M in stock),
giving **0.43–1.49 mA, ~0.96 mA typical**, 1.0 mW worst case against a 62.5 mW part. A sixth line was added to
the SAFE-LED note recording the part and the current. Net topology unchanged.

*(Heritage note: proves_radio_stick_V2 R13/R80, `emulator_mcu` R206/R211 and `battery_protection_replica` R519
all drive C2290 through 1 k. Those are activity/status LEDs; this one reports whether the pyro inhibit is
engaged, so brightness at worst-case Vf matters. 470 Ω is a JLC Basic part, so it adds no setup cost.)*

#### 2.5.6 One self-inflicted regression in pass 2, caught and reverted

An intermediate `pyro_inhibit` edit also moved the SAFE-LED note from y = 118.11 to y = 124.0, on the strength
of `tools/gen/geomcheck.py` reporting a `text-over-text` hit against `#PWR601`'s "GND" value text. That was a
**geomcheck false positive**: geomcheck models every `(text)` block as vertically *centred* on its anchor
(right for `solar_emulation`), while `pyro_inhibit`'s notes are emitted `justify left top` and run *downward*.
The move pushed the now-6-line block into the VF-margin note at y = 132.08 — visible as overstruck text in the
400 dpi render. Reverted; a comment in the generator records the modelling mismatch. Recorded here because it
is the one case in this round where a tool result had to be overruled by the rendered PDF.

---

## 3. The eight §4.3 promotions are eight pure renames

Membership compared pin-for-pin against `tools/baseline/netlist.kicadxml` (Rev2, pre-promotion):

```
old name                                       new name       base  now   verdict
/Power Systems/Load Switches/Deploy1_EN        Deploy1_EN     3     5     PURE RENAME  lost=[] gained=[('D600','1'),('TP600','1')]
/Power Systems/Load Switches/Heater_EN         Heater_EN      2     4     PURE RENAME  lost=[] gained=[('JP600','1'),('TP601','1')]
/Power Systems/Load Switches/Deploy2_EN        Deploy2_EN     2     4     PURE RENAME  lost=[] gained=[('D602','1'),('TP602','1')]
/Power Systems/B-                              B-             7     15    PURE RENAME  lost=[] gained=[('C503','2'),('JP607','1'),('Q501','1'),('Q501','2'),('Q501','3'),('R502','2'),('R505','2'),('TP502','1')]
/Power Systems/VBATT_SENSE                     VBATT_SENSE    10    12    PURE RENAME  lost=[] gained=[('JP602','1'),('JP604','1')]
/Power Systems/INHIB_1                         INHIB_1        2     4     PURE RENAME  lost=[] gained=[('JP602','2'),('JP603','1')]
/Power Systems/INHIB_2                         INHIB_2        4     6     PURE RENAME  lost=[] gained=[('JP604','2'),('JP605','1')]
/Power Systems/IN_RBF                          IN_RBF         6     9     PURE RENAME  lost=[] gained=[('JP603','2'),('JP605','2'),('JP606','1')]

all eight pure renames: True
baseline nets that lost pins or vanished (excluding the 8 renames): []
```

Every gained pin is a Phase-1 part (`pyro_inhibit` shunt headers and test points, `battery_protection_replica`
replica FETs). The inhibit chain reads exactly as brief §4.3 describes it:
`VBATT_SENSE` —J8/JP602— `INHIB_1` —J29/JP603— `IN_RBF` —J30,J20/JP606— `VBUSP`, parallel
`VBATT_SENSE` —J7/JP604— `INHIB_2` —J10/JP605— `IN_RBF`, return `B-` —J15,J19/JP607— `GND`.
Every JP6xx **parallels** its connector; nothing is in series with a flight power path.

---

## 4. Netlist diff vs the Rev2 baseline

`python3 tools/netlist_diff.py tools/baseline/netlist.kicadxml <scratch>/work_integrate/netlist.kicadxml --ignore-unconnected`

```
components: base 261, new 477, added 216, removed 0
nets: base 215, new 355
added nets (125)          = 8 promotion renames + 39 new global labels
                            + 28 sheet-local nets (/<sheet>/NAME)
                            + 50 auto-named Net-(...) nets
removed nets (8)          = the 8 pre-promotion local names, nothing else:
  - /Power Systems/B-, /Power Systems/INHIB_1, /Power Systems/INHIB_2, /Power Systems/IN_RBF,
    /Power Systems/VBATT_SENSE, /Power Systems/Load Switches/Deploy1_EN,
    /Power Systems/Load Switches/Deploy2_EN, /Power Systems/Load Switches/Heater_EN
changed nets (30)         = additions only, every one shows -[]
```

Changed nets, in full (`+[…] -[…]`; the `-[]` on every line is the "no existing net lost pins" proof):

```
  ~ +3V3: +[C315.1, C316.1, R360.1, R362.1, R363.1, R370.1, R371.2, R372.1, R373.1, R374.1, TP306.1, U315.8, U316.8] -[]
  ~ BATT_SCL: +[U315.3] -[]
  ~ BATT_SDA: +[U315.6] -[]
  ~ Dir_Chrg_In: +[J500.1, JP500.2, JP510.2, R500.1, TP500.1] -[]
  ~ F0_PWR: +[C300.1, C301.1, C302.1, C303.1, R300.1, R301.2, R302.1, R303.1, TP300.1, U300.8, U301.5, U302.6, U303.10, U303.5] -[]
  ~ F0_SCL: +[U300.3] -[]
  ~ F0_SDA: +[U300.6] -[]
  ~ F1_PWR: +[C310.1, R310.1, R311.2, R312.1, R313.1, R314.1, TP301.1, U310.8] -[]
  ~ F1_SCL: +[U310.3] -[]
  ~ F1_SDA: +[U310.6] -[]
  ~ F2_PWR: +[C311.1, R320.1, R321.2, R322.1, R323.1, R324.1, TP302.1, U311.8] -[]
  ~ F2_SCL: +[U311.3] -[]
  ~ F2_SDA: +[U311.6] -[]
  ~ F3_PWR: +[C312.1, R330.1, R331.2, R332.1, R333.1, R334.1, TP303.1, U312.8] -[]
  ~ F3_SCL: +[U312.3] -[]
  ~ F3_SDA: +[U312.6] -[]
  ~ F4_PWR: +[C313.1, R340.1, R341.2, R342.1, R343.1, R344.1, TP304.1, U313.8] -[]
  ~ F4_SCL: +[U313.3] -[]
  ~ F4_SDA: +[U313.6] -[]
  ~ F5_PWR: +[C314.1, R350.1, R351.2, R352.1, R353.1, R354.1, TP305.1, U314.8] -[]
  ~ F5_SCL: +[U314.3] -[]
  ~ F5_SDA: +[U314.6] -[]
  ~ FC_RESET: +[J703.7, Q701.3] -[]
  ~ GND: +[110 pins: C200.2 … Y200.4 — every new sheet's returns] -[]
  ~ SCL_Top: +[U316.3] -[]
  ~ SDA_Top: +[U316.6] -[]
  ~ USBBOOT: +[J703.8, Q702.3] -[]
  ~ VBUSP: +[JP606.2] -[]
  ~ VSOLAR: +[JP400.2, JP401.2, TP401.1] -[]
  ~ WDT_DISABLE: +[J703.9, Q703.3, SW703.1] -[]
```

(The full untruncated GND line is in `<scratch>/work_integrate/netlist_diff.txt`.)

**Read against brief §4.1:** these 30 nets plus the 8 promoted ones are *exactly* the "Used by" column of the
§4.1 table and nothing else. No new sheet reaches `DEPLOY1`, `DEPLOY1_AUX`, `DEPLOY2`, `Heater Output`,
`PAYLOAD_*`, `SDA0/1`, `SCL0/1`, `TX0/1`, `RX0/1`, `SPI0_*`, `SPI1_*`, `RF*`, `SWCLK`, `SWDIO`, `USB_DP`,
`USB_DM`, `BOOTSEL`, `+1V1`, `~{MUX_RESET}` or any other FC net. Hard rule 8 holds.

**Components:** 216 added, 0 removed, and **no baseline component changed value or footprint** — the
`netlist_diff` "~ ref: old -> new" section is empty. (The §2.2 edit retunes C200, which is itself one of the
216 *added* parts, so it shows up as `+ C200 1uF Capacitor_SMD:C_0603_1608Metric [/Emulator MCU/]`, not as a
change to anything that existed in Rev2.)

---

## 5. ERC triage

Full-project run on the real root:
`kicad-cli sch erc --format json --severity-all --output erc.json FlatSat_V1.kicad_sch` → **641 violations**
(642 before the pass-2 U303 footprint fix, §2.5.1).

### 5.1 Delta vs the Rev2 baseline, non-noise types

`python3 tools/erc_summary.py erc.json --baseline tools/baseline/erc.json --ignore-noise`

```
sev      type                           base    now  delta
error    pin_not_connected                 5      5     +0
error    power_pin_not_driven              6      6     +0
warning  multiple_net_names               12     12     +0
warning  pin_to_pin                       96    164    +68
warning  same_local_global_label           4      4     +0
warning  single_global_label               1      0     -1
warning  unconnected_wire_endpoint         1      1     +0
total baseline 125, now 192, delta +67
errors: 11
```

### 5.2 Delta including the library-metadata noise classes

```
sev      type                           base    now  delta
error    pin_not_connected                 5      5     +0
error    power_pin_not_driven              6      6     +0
warning  endpoint_off_grid                36     36     +0
warning  footprint_link_issues            23     23     +0
warning  lib_symbol_issues               161    178    +17
warning  lib_symbol_mismatch              83    212   +129
warning  multiple_net_names               12     12     +0
warning  pin_to_pin                       96    164    +68
warning  same_local_global_label           4      4     +0
warning  single_global_label               1      0     -1
warning  unconnected_wire_endpoint         1      1     +0
total baseline 428, now 641, delta +213
errors: 11
```

### 5.3 Errors — 11, all baseline, **zero attributable to the new sheets**

The 11-item list from the integrated project is **identical, item for item and position for position**, to the
11 items in `tools/baseline/erc.json`:

| sheet | error | note |
|---|---|---|
| `/` | `power_pin_not_driven` `#U$05` pin 1 [VBUS] | FC baseline |
| `/` | `power_pin_not_driven` U3 pin 1 [A0] | FC baseline |
| `/` | `pin_not_connected` U30 pin 15 [DIO3] | FC baseline (S-band module) |
| `/` | `pin_not_connected` U30 pin 14 [DIO2] | FC baseline |
| `/Watchdog Circuit/` | `power_pin_not_driven` U1 pin 3 [V+] | FC baseline |
| `/Power Systems/` | `pin_not_connected` U12 pins 15, 1, 7 (×3) | FC baseline |
| `/Power Systems/` | `power_pin_not_driven` `#PWR029` pin 1 | FC baseline (`+3V3`; U10 pin 1 is typed `output`, same class as §2.1) |
| `/RP2350AHHHHHHHHH/` | `power_pin_not_driven` U18 pin 46 [VREG_AVDD] | FC baseline |
| `/RP2350AHHHHHHHHH/` | `power_pin_not_driven` U18 pin 6 [DVDD] | FC baseline |

Per new sheet (`erc_summary.py --sheet … --ignore-noise`):

| sheet | errors | non-noise warnings |
|---|---|---|
| Emulator MCU | **0** | 0 |
| Solar and Sensor Emulation | **0** | 52 (`pin_to_pin`) |
| Solar Power Injection | **0** | 0 |
| Battery Replica and Bench Power | **0** | 16 (`pin_to_pin`) |
| Pyro Inhibit and Jumpers | **0** | 0 |
| Bench IO | **0** | 0 |

The FC baseline's two RP2350 `power_pin_not_driven` errors (U18 DVDD, U18 VREG_AVDD) do **not** recur on the
emulator copy U200, because `emulator_mcu` carries `PWR_FLAG`s on `1V1_EMU` and `VREG_AVDD_EMU` per brief §4.2.

### 5.4 Warnings — every one triaged

| # | type | count | new? | triage |
|---|---|---|---|---|
| W1 | `multiple_net_names` | 12 | 0 new | **Baseline, no action.** All 12 are FC sheets naming one node twice (`BOOTSEL`/`QSPI_CS`, `USB_DM`/`D-`, `USB_DP`/`D+`, `Dir_Chrg_In`/`VBATT`, `RF_VCC`/`+5V`, `TX0`/`GPIO0`, `FC_RESET`/`RUN`, `SWDIO`/`SWD`, `VBUSP`/`WDT_BIAS`, …). Flight heritage; renaming them would change FC net names, which brief §9 forbids. |
| W2 | `same_local_global_label` | 4 | 0 new | **Baseline, no action.** `~{RESET}`, `SWCLK`, `USBBOOT` on the root, `VBUSP` on watchdog. Same reason as W1. |
| W3 | `unconnected_wire_endpoint` | 1 | 0 new | **Baseline, no action.** A 0.0127 mm stub on the root at (3.4544, 1.3843). Cosmetic FC artefact. |
| W4 | `single_global_label` | 0 | **−1** | **Improved.** The Rev2 baseline had one (`USBBOOT`, lonely on the root); `bench_io` J703.8 / Q702.3 now gives it a partner. Zero remaining is also the strongest evidence there is no misspelled contract net (§2.4). |
| W5 | `pin_to_pin` on new sheets | 68 new (52 solar_emulation + 16 battery_protection_replica) | **new** | **Library metadata, not electrical. No action in Phase 1.** Every one of the 68 has `Unspecified` on at least one side: 39 Unspecified↔Passive, 9 ↔Bidirectional, 8 ↔Output, 3 ↔Input, 3 ↔Power input, 3 ↔Unspecified, 3 ↔Power output. The sources are the easyeda2kicad `TCA4311ADGKR`, `VEML6031X00`, `DZDH0401DW-7`, `DMP4047LFDE-7`, `SPM6530T-4R7M-HZ` symbols and the project-local `flatsat:R5460N208AA`, all of which type every signal pin `unspecified`. The Rev2 baseline already ships **96** of this identical class, and the reference boards `XY_Face_V4` / `battery_pack_v2` / `debug_board_v1` use the same symbols. Fixing it means retyping pins in the user's shared global library (`~/Documents/KiCad/easyeda2kicad/easyeda2kicad.kicad_sym`), which would diverge the project from the global library for zero electrical benefit. Recorded as open item O7. |
| W6 | `pin_to_pin` on FC sheets | 96, 0 new | 0 new | **Baseline, no action.** Verified explicitly: no new `pin_to_pin` appears on `/`, `/Power Systems/`, `/Power Systems/Load Switches/`, `/Watchdog Circuit/` or `/RP2350AHHHHHHHHH/`. The §2.1 pin-type change added none. |
| W7 | `lib_symbol_mismatch` | +129 | **new** | **Noise, no action.** 112 of the 129 name library `power` — every `power:GND` and `power:PWR_FLAG` instance on the six new sheets, because the pantry blocks the sheet generators used differ cosmetically from the installed `power` library (`PWR_FLAG` went 0 → 9 simply because the FC baseline has no PWR_FLAG at all). The remaining 17 are `easyeda2kicad` ×8, `Device` ×5 (LED, Crystal_GND24), `Connector` ×2, `Memory_Flash` ×1 (W25Q128JVS), `Battery_Management` ×1 (BQ25886RGE) — the same class the FC baseline already raises for D1/D2/D3, U11, Y1. Zero electrical effect; the flags demonstrably work (§5.3). |
| W8 | `lib_symbol_issues` | +17 | **new** | **Noise, no action.** "The current configuration does not include the symbol library 'X'": `mainboard` ×13 (used by pyro_inhibit R600/R601/R602 and bench_io, matching the FC's own convention — the baseline already has 90 of these from eps_side/load_switches/RP2350/root), `Adafruit ItsyBitsy RP2040-eagle-import` ×2, `MCU_RaspberryPi_RP2350` ×1 (U200), `Driver_Haptic` ×1 (U303). The definitions are embedded in each sheet's `lib_symbols`, so ERC, netlist and PDF are unaffected; only the GUI's "edit symbol" path would complain. **`flatsat` no longer appears at all** (§1.2). A future cleanup could add `mainboard` to `sym-lib-table`; out of scope for Phase 1. |
| W9 | `footprint_link_issues` | **+0** | — | **FIXED in pass 2 (§2.5.1).** Pass 1 carried one new warning here: `Footprint 'VSSOP-10_3x3mm_P0.5mm' not found in library 'Package_SO'` — `solar_emulation` U303 `DRV2605LDGS`, inherited verbatim from `XY_Face_V4`, a name KiCad 10's `Package_SO.pretty` no longer carries. Layout could not have placed U303. Re-spec'd to `Package_SO:TSSOP-10_3x3mm_P0.5mm` (same 3 × 3 mm body, 0.5 mm pitch, 10 pins, no thermal pad = the DGS land) on the U303 instance *and* in the sheet's cached `lib_symbols`, plus a `LIB_FIXUPS` entry in the generator so it cannot come back. Count is now **23 = the Rev2 baseline**, and a sweep of all 39 distinct footprints used by the six new sheets against `fp-lib-table` + the KiCad standard libraries + the user's `easyeda2kicad.pretty` returns **0 unresolved**. |
| W10 | `endpoint_off_grid` | 36, 0 new | 0 new | **Baseline, no action.** FC artefacts. |

**Summary: 0 errors and 0 non-library warnings are attributable to the six new sheets.** After the pass-2
fixes, **every** warning class with real content is back at its Rev2 baseline count; the entire remaining
delta (`pin_to_pin` +68, `lib_symbol_mismatch` +129, `lib_symbol_issues` +17) is symbol-library metadata,
triaged in W5/W7/W8 and carried as open items O7 and O8.

---

## 6. Lint, all six sheets

```
emulator_mcu.kicad_sch:               93 symbol instances, 14 lib symbols, 185 wires, 0 errors, 0 warnings
solar_emulation.kicad_sch:           101 symbol instances, 10 lib symbols, 191 wires, 0 errors, 0 warnings
solar_power_injection.kicad_sch:      17 symbol instances,  8 lib symbols,  24 wires, 0 errors, 0 warnings
battery_protection_replica.kicad_sch: 72 symbol instances, 16 lib symbols, 131 wires, 0 errors, 0 warnings
pyro_inhibit.kicad_sch:               22 symbol instances,  7 lib symbols,  41 wires, 0 errors, 0 warnings
bench_io.kicad_sch:                   39 symbol instances, 12 lib symbols,  66 wires, 0 errors, 0 warnings
```

PDF: `<scratch>/work_integrate/FlatSat_V1.pdf`, 11 A3 pages —
1 `/`, 2 watchdog, 3 eps_side, 4 load_switches, 5 RP2350, 6 Emulator MCU, 7 Solar and Sensor Emulation,
8 Solar Power Injection, 9 Battery Replica and Bench Power, 10 Pyro Inhibit and Jumpers, 11 Bench IO.

---

## 7. Open items handed on (nothing here blocks Phase 1 exit)

These are recorded for the PM and the Fable review-and-fix round. Items struck through were **closed in pass 2**
(§2.5); the pass-1 policy of leaving single-sheet defects with their owner was overtaken by the fact that the
sheet agents' runs had ended — see the ownership exceptions in §1.2.

**Needs a PM decision before the Fable round:** O1 (`VBAT_BENCH`), O2 (brief §4.2 wording), O6 (`VBUS_EMU`
bulk capacitance), and the four ownership exceptions plus the `load_switches` pin-type edit in §1.2 / §7a.

| # | item | owner |
|---|---|---|
| O1 | **`VBAT_BENCH` is unresolvable as written — PM RULING REQUIRED before the Fable round.** Brief §6.4 wants a `VBAT_BENCH` power symbol + `PWR_FLAG` on the bench B+ *and* "B+ (through nothing) → `Dir_Chrg_In`", while §4.2 bans a `PWR_FLAG` on `Dir_Chrg_In`. `battery_protection_replica` kept the topology and dropped the name. Re-verified in pass 2: the netlist shows `J500.1` sitting directly on `Dir_Chrg_In` with no series element, so a `VBAT_BENCH` power symbol there would merge two names onto one net and could rename an existing FC net — which brief §9 forbids. All **10** `PWR_FLAG`s were traced geometrically (`#FLG200` `VREG_AVDD_EMU`, `#FLG201` `1V1_EMU`, `#FLG400/401` `VSOLAR_BENCH_A/B`, `#FLG500` `VBAT_BENCH_N`, `#FLG501` `VBUS_CHG`, `#FLG502` `CHG_DVIN`, `#FLG503` the BQ25886 SW node, `#FLG701` `VBUS_EMU`): none sits on `GND`, `+3V3`, `VSOLAR`, `Dir_Chrg_In`, `VBUSP`, `B-`, `VBATT_SENSE` or any `Fn_PWR`, so §4.2's prohibition holds. `flatsat:VBAT_BENCH` is **absent** from `symbols/flatsat.kicad_sym` (which holds exactly `3V3_EMU`, `IRF7458`, `R5460N208AA`, `VBUS_CHG`, `VBUS_EMU`, `VSOLAR_BENCH`) and the pantry block is unused. **Ruling needed:** either (a) strike `VBAT_BENCH` from brief §4.2/§6.4, recording that B+ *is* `Dir_Chrg_In` and therefore cannot carry its own name or flag, and delete `<scratch>/pantry/flatsat_VBAT_BENCH.sexp`; or (b) authorise a third `Jumper:Jumper_2_Open` between J500 pin 1 and `Dir_Chrg_In` so B+ becomes a separable named rail. Not an implementer call; it will be re-raised in the Fable round if left open. | **PM** |
| O2 | **Brief §4.2 is factually wrong** where it says "the FC already has power-output pins on those" — `Fn_PWR` (AP22652 pin 6) and `+3V3` (U10 pin 1) are both typed `output`, which is why the Rev2 baseline already carries a `power_pin_not_driven` on `+3V3` and why §2.1 was needed. Correct the brief. | **PM** |
| ~~O3~~ | **CLOSED in pass 2 (§2.5.1).** U303 is now `Package_SO:TSSOP-10_3x3mm_P0.5mm`, fixed on the instance, in the sheet's `lib_symbols` and in the generator. `footprint_link_issues` 24 → 23 = baseline; 39/39 footprints on the new sheets resolve. | — |
| ~~O4~~ | **CLOSED in pass 2 (§2.5.5).** Took the BOM-consistent option: LED600 `Value` → `LED` with the KT-0603W datasheet URL, and R602 `1k`/`C11702` → `470R`/`C25117` (Basic) so the white LED gets 0.43–1.49 mA (~0.96 mA typ) instead of 0.2–0.8 mA. Sheet note and `sheet_pyro_inhibit.md` §3/§9/§12 corrected. | — |
| ~~O5~~ | **CLOSED in pass 2 (§2.5.4).** Took option (a): F400/F401 re-spec'd to Littelfuse 2920L185DR (LCSC `C207086`, 1.85 A / 3.70 A / 33 V, `Fuse:Fuse_2920_7451Metric`) and the brief's **24 V** hard-maximum text restored, with 9 V of PTC voltage margin. The wrong-variant derating figure (1.36 A) and the unsourced 0.3 Ω PTC resistance were corrected to the datasheet's 1.54 A at 40 °C and R1max 0.150 Ω, and the two redundant junction dots on J400/J401 pin 1 were deleted. No PM decision needed — the sheet now matches §6.3 as written. | — |
| O6 | **`VBUS_EMU` is at 11.1 µF nominal — PM ACCEPTANCE REQUESTED.** After the §2.2 fix the net carries C701 10 µF (bench_io, at the connector) + C200 1 µF + C201 100 nF; the netlist confirms membership `C200.1, C201.1, C701.1, J701.A4/A9/B4/B9, TP200.1, TP701.1, U202.1, U202.3`. ≈ 8 µF effective after the 20–30 % DC-bias derating normal for X5R/X7R on a 5 V rail, against the USB 2.0 §7.2.4.1 10 µF bypass limit; 11.1 µF nominal is 11 % over the literal number. In line with `proves_radio_stick_V2`'s single nominal 10 µF. Going lower would under-bulk the AP2112K input. Confirm accepted, or say which cap to drop. | **PM** |
| O7 | **68 new `pin_to_pin` warnings are pure symbol metadata** (W5). Clearing them means retyping `unspecified` pins in the user's global `easyeda2kicad` library and in `flatsat:R5460N208AA`. Library job, deferred. | **library / later revision** |
| O8 | **`mainboard` symbol library is not in `sym-lib-table`** (W8) and produces 103 `lib_symbol_issues` (90 baseline + 13 new). Pre-existing FC convention; adding the library or migrating those instances to `Device:R` is a separate cleanup. | **later revision** |
| O9 | **LCSC numbers still outstanding** across the six sheets, collected from the sheet reports: `solar_emulation` R304 (43 R **2010** ≥ 0.5 W), J300; `solar_power_injection` J400/J401, JP400/JP401 (**F400/F401 now carry `C207086`**); `battery_protection_replica` J500, R503/R504, JP500/JP510, U511 BQ25886RGE, C512, C516, R514–R517; `pyro_inhibit` D600–D602, JP600–JP607, SW600, R600 (**R602 now carries `C25117`**); `bench_io` C701, TP701, Q701–Q703, J703. Rule 5 was respected — these are blank, not guessed. | **supply-chain pass** |
| O10 | **FC finding, reported not repeated** (hard rule 4): the `eps_side` text note "VSOLAR 9V to 40V" is wrong. `VSOLAR` is limited by INA219 U8 IN+ absolute maximum 26 V and by the LT3652's 32 V; brief §6.3 sets the bench window at 12–18 V with a 24 V hard maximum (which pass 2 restored on `solar_power_injection`, §2.5.4). The note needs correcting on `eps_side` in a later revision — the integrator did not edit it, as this phase's mandate is additions plus the eight promotions. Tabulated as **F1** in §7a. | **later revision** |
| O11 | **`solar_emulation` wrote a second file** under `tools/gen/` (`geomcheck.py`, a generic wire-through-text sweeper) where brief §3 rule 2 allows one generator. Harmless and useful; it belongs in `tools/` rather than `tools/gen/`. Left in place. **Caveat found in pass 2:** it models every `(text)` block as vertically *centred* on its anchor, which is right for `solar_emulation` but wrong for `pyro_inhibit` and `bench_io`, whose notes are emitted `justify left top`. Its `text-over-text` hits on those sheets can be false positives — check the rendered PDF before acting on one (§2.5.6). | **housekeeping** |
| O12 | **`flatsat:VSOLAR_BENCH`'s Description reads** `Power symbol creates a global label with name "+3V3"` — a copy-paste artefact that came with the sanctioned pantry block (`pantry/flatsat_VSOLAR_BENCH.sexp` line 54). `symbols/flatsat.kicad_sym` reproduces the sheet cache byte-for-byte on purpose (so no new `lib_symbol_mismatch` appears), so it is preserved here too. Fix in the pantry and in both places together. | **later revision** |
| O13 | **E9 residue on `PYRO_INHIBIT_STATE` in the armed state.** With the inhibit switch open, U200 pin 35 sees ≈ 104.7 k to `3V3_EMU` (R601 4.7 k + R600 100 k), far above the 8.2 k that RP2350 erratum E9 requires, so an A2-silicon pad leaking 120 µA sits near its float voltage in exactly the state where a misread matters. The brief's own §6.5 topology; noted by the emulator_mcu verifier. | **Fable round** |
| O14 | **I2C pads on an OFF face** (`EMU_Fn_SDA/SCL`) are pulled up through 10 k to `Fn_PWR` per brief §4.2/§6.2, which does not meet rule 10's ≤ 8.2 k; with the face off the pad floats to ≈ 1.4 V. Mitigation is a firmware guarantee (input buffer disabled while `EMU_Fn_SENSE` reads low), printed on both sheets. | **Fable round / firmware** |
| O15 | **Four sheet files outside the integrator's rule-2 writable set were written** (`emulator_mcu`, `solar_emulation`, `solar_power_injection`, `pyro_inhibit`, each with its generator), plus the one-token `load_switches` pin-type edit. Rationale and evidence per file in §1.2. Needs PM acknowledgement; no rework implied. | **PM** |
| O16 | **Four pre-existing `wire-through-text` hits on `pyro_inhibit`** (JP601 / SW600 / `Conn_01x02` field text crossed by the GND drop at x = 86.36, and the D1 requirement note crossed by the TP603 stub at x = 76.2), plus 4 on `solar_power_injection` (terminal-block and `VSOLAR_BENCH_x` field text). Cosmetic; every string stays legible at 300 dpi and none was introduced by pass 2 (identical counts before and after). `solar_emulation`, whose generator sweeps for this, has 0. | **Fable round / cosmetic** |

---

### 7a. FC findings — reported, not repeated (hard rule 4)

Facts about the flight-heritage FC portion that this phase discovered and deliberately did **not** fix on the
FC sheets. They belong upstream, in the FC project, not in a FlatSat additions phase.

| # | FC finding | where | disposition |
|---|---|---|---|
| F1 | Text note **"VSOLAR 9V to 40V"** near IC6 is wrong: `VSOLAR` is limited by INA219 U8 IN+ absolute maximum **26 V** and by the LT3652's **32 V** operating maximum. Brief §6.3 sets the bench window at 12–18 V with a 24 V hard maximum. | `eps_side.kicad_sch` | Flagged on `solar_power_injection` and in its report as required; the FC note itself left untouched. Same as O10. |
| F2 | **`Power_Management:AP22652` pin 6 "Output" is typed `output`, not `power_out`,** so nothing on `F0_PWR`…`F5_PWR` counts as a power source and any `power_in` pin added to a face rail raises `power_pin_not_driven`. The same defect exists on `+3V3` (U10 pin 1, also `output`), which is why the **Rev2 baseline already ships** a `power_pin_not_driven` error on `+3V3`. Brief §4.2's premise "the FC already has power-output pins on those" is therefore false. | `load_switches.kicad_sch` (cached symbol), `eps_side.kicad_sch` | **Fixed for FlatSat only**, one token, §2.1 — the only change to an FC heritage file beyond the eight §4.3 promotions, and it needs PM acknowledgement (§1.2). Metadata-only: netlist, PCB, BOM and footprints unchanged. |
| F3 | The upstream FC project should take the same AP22652 pin-type correction **if it ever adopts a real `Power_Management:AP22652` library symbol**. Today there is none installed at all (7 pre-existing `lib_symbol_issues` "Symbol AP22652 not found in symbol library Power_Management"), so the cached definition in `load_switches.kicad_sch` is the only copy and nothing can silently revert it. | upstream FC | Carry to the FC project's next revision. |
| F4 | 36 `endpoint_off_grid` and 1 `unconnected_wire_endpoint` warnings, 12 `multiple_net_names`, 4 `same_local_global_label`, 96 `pin_to_pin` and 161 `lib_symbol_issues` are all pre-existing FC artefacts (§5.4 W1/W2/W3/W6/W8/W10). | FC sheets | Baseline; no action in Phase 1. |

---

## 8. How to reproduce

```bash
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1
K=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
W=<scratch>/work_integrate2

$K sch erc --format json --severity-all --output $W/erc.json FlatSat_V1.kicad_sch
$K sch export netlist --format kicadxml --output $W/netlist.kicadxml FlatSat_V1.kicad_sch
$K sch export pdf --output $W/FlatSat_V1.pdf FlatSat_V1.kicad_sch

python3 tools/erc_summary.py $W/erc.json --baseline tools/baseline/erc.json --ignore-noise
python3 tools/erc_summary.py $W/erc.json --baseline tools/baseline/erc.json          # incl. noise classes
python3 tools/netlist_diff.py tools/baseline/netlist.kicadxml $W/netlist.kicadxml --ignore-unconnected
python3 tools/sch_lint.py <sheet>.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/<sheet uuid> --refdes-block <lo>-<hi>

# per-sheet ERC (all six return "total <n>, errors: 0")
for S in "Emulator MCU" "Solar and Sensor Emulation" "Solar Power Injection" \
         "Battery Replica and Bench Power" "Pyro Inhibit and Jumpers" "Bench IO"; do
    python3 tools/erc_summary.py $W/erc.json --sheet "$S" --ignore-noise
done

# regenerate any sheet from its generator.  Since review round 2 (§10) all six are
# uuid-stable and pantry-independent: no env var, no scratch path, and the output is
# byte-identical to the committed sheet.  FLATSAT_PANTRY=<dir> overrides the pantry;
# FLATSAT_FRESH_UUIDS=1 forces real random uuids (only to deliberately re-key a sheet).
python3 tools/gen/emulator_mcu_gen.py [-o <path>]
python3 tools/gen/solar_emulation_gen.py [--out <path>]
python3 tools/gen/solar_power_injection_gen.py [--out <path>]
python3 tools/gen/battery_protection_replica_gen.py [--out <path>]
python3 tools/gen/pyro_inhibit_gen.py          # writes FlatSat_V1/pyro_inhibit.kicad_sch directly
python3 tools/gen/bench_io_gen.py              # writes FlatSat_V1/bench_io.kicad_sch directly

# readability sweep (see O11 for its centred-anchor caveat)
python3 tools/gen/geomcheck.py <sheet>.kicad_sch --overlaps
```

`tools/harness_erc.sh` still works unchanged: it now detects that the real root already references all six
sheets ("already referenced by the real root (integrated), left as is") and runs ERC on the integrated
hierarchy directly.

---

## 9. Review fixes (round 1, 2026-09-14)

Owner: root. Writable targets this round were `FlatSat_V1.kicad_sch` and this report.
Two review items were dispositioned fix-now against the root owner.

| id | title | status |
|---|---|---|
| 13 | Generators depend on the session-scoped scratchpad pantry | **partially applied** — data half landed, generator half deferred |
| 14 | Five of six generators re-roll every uuid on each run | **not applied** — deferred, see below |

`FlatSat_V1.kicad_sch` itself needed no edit for either item: both are `tools/` housekeeping.
The root schematic is byte-unchanged this round (mtime 05:48:46, from the integration pass).

### 9.1 Finding 13 — `tools/pantry/` is now checked in

**Applied.** The 42 `lib_symbols` blocks the six Phase-1 sheets actually reference are now in
`FlatSat_V1/tools/pantry/`, copied verbatim out of the capture session's scratchpad
(`Transistor_FET_BSS138.sexp` came from `scratchpad/work_bench_io/`, the only used block that
was never in the pantry proper; `work_bench_io/Switch_SW_SPDT.sexp` was byte-identical to the
pantry copy, so there is one of those). `INDEX.md` (per-symbol provenance) and a new `README.md`
(contents, the intended env-var contract, and the exact one-line change each generator still
needs) are alongside.

This was the load-bearing half: the blocks existed **only** under a session-scoped `/private/tmp`
path that is garbage-collected, and nothing under the repo held them. They are now recoverable.

Verified — the checked-in pantry reproduces the delivered sheets:

* all 42 blocks are **byte-identical** to the block the corresponding delivered sheet embeds,
  after the one documented `LIB_FIXUPS` substitution
  (`Driver_Haptic:DRV2605LDGS` `Package_SO:VSSOP-10_3x3mm_P0.5mm` -> `TSSOP-10_3x3mm_P0.5mm`);
* `PANTRY=$PWD/tools/pantry python3 tools/gen/battery_protection_replica_gen.py --out <scratch>`
  produced a file **byte-identical** to the delivered `battery_protection_replica.kicad_sch`
  (that generator is the seeded, uuid-stable one);
* `PANTRY=$PWD/tools/pantry python3 tools/gen/solar_emulation_gen.py --out <scratch>` produced a
  **uuid-stripped-identical** `solar_emulation.kicad_sch`;
* `FLATSAT_PANTRY=$PWD/tools/pantry python3 tools/gen/emulator_mcu_gen.py -o <scratch>` produced a
  **byte-identical `lib_symbols` section** (53 006 bytes both sides). Its remaining body diff is the
  R7 pull-up rework (generator says "4.7 k device-side pull-ups (~0.70 mA per line into Fn_PWR)",
  the delivered sheet still said 10 k at the time of sampling) — that is the emulator_mcu owner's
  in-flight fix, not a pantry effect.

**Deferred:** repointing the six `PANTRY` constants in `tools/gen/*.py`, and making
`solar_emulation_gen.py`'s `LIB_FIXUPS` idempotent. Reason: five of the six generators were being
rewritten by the per-sheet fixers while this ran — `bench_io_gen.py` at 07:55:35,
`pyro_inhibit_gen.py` at 08:00:08, `solar_emulation_gen.py` at 08:00:41, `emulator_mcu_gen.py` at
08:00:59, against a start time of 07:56. A second writer doing a non-atomic read-modify-write on
those files risks silently dropping a sheet fix, which is exactly the failure the
"generator must reproduce the sheet" convention exists to prevent. The remaining work is one line
per file and is tabulated in `tools/pantry/README.md`; it should be applied by the sheet owners or
by the integrator once the fixers have quiesced.

Until then the three already-env-aware generators run against the repo copy today:

```sh
PANTRY=$PWD/tools/pantry FLATSAT_PANTRY=$PWD/tools/pantry python3 tools/gen/solar_emulation_gen.py --out <path>
```

`solar_power_injection_gen.py` (hardcoded `PANTRY`), `pyro_inhibit_gen.py` (hardcoded
`SCRATCH_PANTRY`) and `bench_io_gen.py` (hardcoded `PANTRY` + `WORK`) still need the edit before
they will run outside this session. Note also that `pyro_inhibit_gen.py` and `bench_io_gen.py` have
no `--out` flag — they write the project sheet directly, so they cannot be dry-run.

### 9.2 Finding 14 — uuid-stable generators

**Not applied**, deliberately. Three reasons, in order of weight:

1. It requires rewriting five generators (22–38 KB each) that other agents were actively editing
   during this round (timestamps above). Same clobber risk as 9.1, over five times the surface.
2. The fix specifies seeding "from/reading the currently-delivered sheet's uuids", because a fresh
   seed cannot reproduce already-issued `uuid4` values. Those sheets were changing under the fix
   round — `pyro_inhibit.kicad_sch` 08:00:14, `solar_emulation.kicad_sch` 08:00:41 — so any uuid
   set pinned now would be stale within minutes, and its own verification ("before/after diff shows
   only the intended item changed") cannot be run against a moving target.
3. It is not urgent this round on its own terms: the finding records that no PCB layout references
   any of the six new sheet uuids yet, and its verification says "do this before Phase-2 layout
   begins". Doing it after the fix round settles is strictly better and strictly safer.

Carry to the Phase-2 kickoff, before any layout work: port
`battery_protection_replica_gen.py`'s pattern (lines 34–43, seeded `random.Random` +
pinned header uuid) into the other five, seeding from the then-final delivered sheets.

### 9.3 Verification after the fixes

`tools/sch_lint.py FlatSat_V1.kicad_sch --project FlatSat_V1 --path /c64c0d72-…`:

```
FlatSat_V1.kicad_sch: 115 symbol instances, 33 lib symbols, 308 wires, 0 errors, 33 warnings
```

33 warnings, all pre-existing FC-sheet off-grid items and unconnected pins on unchanged flight
heritage (U30.14/15, U15.2/11/12) — the file was not edited this round.

`SCRATCH=… tools/harness_erc.sh` (whole integrated hierarchy):

```
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
=== violations on 'Emulator MCU' ===  total 0, errors: 0
```

Errors still 11, every error class +0 — unchanged from the Rev2 relationship in §5.3. The +68
`pin_to_pin` are all "Unspecified" pins (declared noise). `single_global_label` is **-9**, an
improvement from the other owners' in-flight fixes. Netlist diff vs baseline: 0 removed nets, and
every one of the 38 changed nets is `+[…] -[]`, i.e. pins added only, no existing net lost a pin.

PDF re-exported and read (page 1, root): all six sheet symbols present with the correct filenames
and the "PROVES FlatSat V1 additions — see docs/flatsat/2026-09-14_phase1_schematic/" note; the FC
blocks render unchanged.

Because ERC and the netlist were sampled while five other owners were mid-edit, these numbers
describe the tree at 08:02 and should be re-run by whoever closes the round.

---

## 10. Review fixes (round 2, 2026-09-14) — integrator/fixer

The checker's re-run confirmed 12 of 14 round-1 items applied and left three open against this
owner: **id 0** (a documentation sweep miss on `sheet_solar_emulation.md`), **id 13** (the pantry
data was checked in but the generator *paths* were not repointed) and **id 14** (uuid-stable
generators, deferred in round 1). All three are now applied. No `.kicad_sch` **content** changed:
every sheet is byte-identical to its round-1 delivery except for re-keyed item uuids on five sheets
(§10.2), and the netlist and ERC results below are unchanged from the checker's numbers.

### 10.1 [id 13] Pantry path wiring — all six generators repointed at `tools/pantry`

Round 1 checked in `FlatSat_V1/tools/pantry/` (42 `.sexp` blocks + `INDEX.md` + `README.md`) but left
the generators pointing at the session scratchpad. Three hardcoded it outright; three defaulted to it
behind an env var. Either way, all six break once the session scratch is collected. Every one now uses
the contract already documented in `tools/pantry/README.md`:

```python
HERE = os.path.dirname(os.path.abspath(__file__))
PANTRY = os.environ.get('FLATSAT_PANTRY', os.path.join(HERE, '..', 'pantry'))
```

| generator | was | now |
|---|---|---|
| `tools/gen/emulator_mcu_gen.py:23` | `os.environ.get('FLATSAT_PANTRY', <abs scratch>)` | contract above (`HERE` added) |
| `tools/gen/solar_emulation_gen.py:30` | `os.environ.get('PANTRY', <abs scratch>)` | contract above (env var renamed) |
| `tools/gen/battery_protection_replica_gen.py:28` | `os.environ.get('PANTRY', <abs scratch>)` | contract above (env var renamed) |
| `tools/gen/solar_power_injection_gen.py:22` | hardcoded `PANTRY = <abs scratch>`, no override | contract above, via the existing `TOOLS` constant |
| `tools/gen/pyro_inhibit_gen.py:12` | hardcoded `SCRATCH_PANTRY = <abs scratch>`, no override | renamed `PANTRY`, contract above; the single use site (`os.path.join(SCRATCH_PANTRY, …)`) follows |
| `tools/gen/bench_io_gen.py:16-17` | hardcoded `PANTRY` **and** `WORK` | contract above; `WORK` **deleted** — its only use, `Transistor_FET:BSS138`, now comes from `tools/pantry` |

`grep -rn 'private/tmp\|scratchpad' tools/gen/*.py` now returns nothing.

**Proven by removing the crutch, not by reading the code.** The session scratchpad's `pantry/` and
`work_bench_io/` directories were renamed away and all six generators re-run with no environment
variables set:

```
=== regenerate with session scratch pantry ABSENT ===
  emulator_mcu: OK          solar_power_injection: OK       pyro_inhibit: OK
  solar_emulation: OK       battery_protection_replica: OK  bench_io: OK
=== still byte-identical to the committed sheet? ===
  all six: BYTE-IDENTICAL
```

(The scratch directories were restored afterwards.)

**One related robustness item, also closed.** `solar_emulation_gen.py`'s `LIB_FIXUPS`
(`Driver_Haptic:DRV2605LDGS` `VSSOP-10` → `TSSOP-10`) did `raise SystemExit` whenever the *old*
string was absent, so it aborted against any pantry rebuilt **from** a delivered sheet. It now
aborts only when a block carries neither the old nor the new string. Verified by building a
post-fixup copy of `tools/pantry` and regenerating `solar_emulation.kicad_sch` from it: byte-identical
output, no abort. Output against the committed pantry is unchanged.

`tools/pantry/README.md` "Status" section rewritten from a to-do list into the delivered state.

### 10.2 [id 14] uuid-stable generators — all six

`battery_protection_replica_gen.py` was the only uuid-stable generator (seeded `random.Random` +
pinned `SHEET_FILE_UUID`). The other five drew a fresh `uuid4` per item and a fresh header uuid, so a
regeneration re-keyed every element in the file. The same pattern is now in all five:

```python
_rng = random.Random('flatsat-<key>-2026-09-14')
_FRESH = os.environ.get('FLATSAT_FRESH_UUIDS') == '1'

def u():
    if _FRESH:
        return str(uuid.uuid4())          # escape hatch: deliberately re-key a sheet
    return str(uuid.UUID(int=_rng.getrandbits(128), version=4))
```

Each generator gets its own seed string, so no two sheets can draw the same uuid. The header/file uuid
comes from the same seeded stream (`bench_io`'s `SHEET_UUID_FILE`, `pyro_inhibit`'s and
`solar_power_injection`'s header `U()`/`u()` call, `emulator_mcu`'s `render()`), so it is pinned too.
Seeding is sufficient because emission order was already deterministic — that is exactly what the
checker's two "uuid-stripped identical, 0-line diff" passes proved.

Round 1 deferred this partly because "a fresh seed cannot reproduce already-issued `uuid4` values", so
the sheets had to be re-keyed to the new streams. That is safe here and was checked before doing it:

* `FlatSat_V1.kicad_pcb` contains **262 footprints, all Rev2 FC**, and
  `grep -cE '"(U2[0-9][0-9]|R3[0-9][0-9]|C5[0-9][0-9]|JP6[0-9][0-9]|J7[0-9][0-9])"'` returns **0** —
  no layout references anything on the six new sheets, so nothing is orphaned.
* `FlatSat_V1.kicad_pro` holds only 5 uuids, all root/FC sheet uuids; `FlatSat_V1.kicad_prl` holds none.
* The root schematic references each new sheet only by its **sheet-symbol** uuid, which is a pinned
  constant in every generator and did not move.
* `tools/netlist_diff.py` keys on refdes/pin/net name, not uuids.

**Result — two consecutive regeneration passes of all six:**

```
=== PASS1 vs PASS2 (byte) ===
  emulator_mcu: BYTE-IDENTICAL            battery_protection_replica: BYTE-IDENTICAL
  solar_emulation: BYTE-IDENTICAL         pyro_inhibit: BYTE-IDENTICAL
  solar_power_injection: BYTE-IDENTICAL   bench_io: BYTE-IDENTICAL

=== round-1 delivered vs regenerated (uuid-stripped) ===
  emulator_mcu:               content IDENTICAL (uuids changed)
  solar_emulation:            content IDENTICAL (uuids changed)
  solar_power_injection:      content IDENTICAL (uuids changed)
  battery_protection_replica: content IDENTICAL (byte-identical — was already stable)
  pyro_inhibit:               content IDENTICAL (uuids changed)
  bench_io:                   content IDENTICAL (uuids changed)
```

So the schematic content delivered in round 1 is preserved exactly; only the five sheets' internal
item uuids were re-keyed once, and from now on `python3 tools/gen/<key>_gen.py` reproduces the
committed file byte for byte. §8's "each re-rolls item uuids" note is corrected.

### 10.3 [id 0] Documentation sweep — `sheet_solar_emulation.md`

Documentation only; `solar_emulation.kicad_sch` and its generator were already correct at 4.7 k and
were **not** touched for this item. The checker named lines 120, 213 and 216; the full sweep found
six more current-state statements with the same stale value, and the resistor split itself was wrong
in two places. Corrected from a parse of the sheet file (`10k` = 17 parts, `4.7k` = 20, `43R` = 1):
§1 line 34, the §2.2 channel diagram, the §2.2 BATT and TOP bullets, the §3 parts table (was one
"31× 10k" row + a "6× 4.7k" row; now 17× / 20× with rebuilt refdes lists), the §3 counts block, the
§6 existing-nets table (line 120), the §8.2 TCA4311A `§8.3.1` row and the §8.3 roll-up (line 374).
Annotated rather than rewritten, following the `sheet_pyro_inhibit.md` §12.5 precedent: line 213
(a verbatim quote of brief §6.2 — kept, with an inline "superseded by R7" note), §7.7b (now opens
**RESOLVED by fix id 3** with the 5.3 k / 0.64 V arithmetic, old text kept below as superseded), the
§11 "still open" line and §12.5 item 2. The §10/§11 fix-round narratives and the §12 geometry census
are left verbatim — they are dated records, and rewriting them would falsify the history. Full table
in the new `sheet_solar_emulation.md` §13.3.

### 10.4 Verification after round 2

`kicad-cli 10.0.1 sch erc --format json --severity-all` on the real root: **645 violations**.
`tools/erc_summary.py --baseline tools/baseline/erc.json --ignore-noise` (Rev2):

```
sev      type                           base    now  delta
error    pin_not_connected                 5      5     +0
error    power_pin_not_driven              6      6     +0
warning  multiple_net_names               12     12     +0
warning  pin_to_pin                       96    164    +68
warning  same_local_global_label           4      4     +0
warning  single_global_label               1      0     -1
warning  unconnected_wire_endpoint         1      1     +0
total baseline 125, now 192, delta +67
errors: 11
```

Errors by sheet path — `/` 4, `/Power Systems/` 4, `/RP2350AHHHHHHHHH/` 2, `/Watchdog Circuit/` 1;
**zero on any of the six new sheets**, and both error classes +0, so the byte-identical-to-Rev2
relationship in §5.3 still holds. Per new sheet, non-noise: Emulator MCU 0, Solar Power Injection 0,
Pyro Inhibit and Jumpers 0, Bench IO 0, Solar and Sensor Emulation 52 `pin_to_pin`, Battery Replica
and Bench Power 16 `pin_to_pin`. A scan for a `pin_to_pin` with no `Unspecified` token found **0**.

`tools/harness_erc.sh` (default post-promotion baseline): `total baseline 133, now 192, delta +59`,
`errors: 11`, `single_global_label` −9.

Netlist, `tools/netlist_diff.py … --ignore-unconnected` vs `tools/baseline/netlist.kicadxml`:

```
components: base 261, new 479, added 218, removed 0
nets:       base 215, new 354      added 125, removed 8, changed 30
```

All 30 changed nets are `-[]` (a filter for any non-empty lost list returned nothing); the 8 removed
nets are the 8 §4.3 label promotions. Identical to the checker's re-run.

`tools/sch_lint.py`, six sheets, correct `--path` and `--refdes-block`: **0 errors, 0 warnings** each —
`emulator_mcu` 93/14/185, `solar_emulation` 101/10/191, `solar_power_injection` 17/8/24,
`battery_protection_replica` 77/16/137, `pyro_inhibit` 23/8/41, `bench_io` 39/12/66. Unchanged.

PDF re-exported from the real root: 11 pages (page numbers 1, 3–12; the page-2 gap is pre-existing
Rev2 numbering), no plot errors.

### 10.5 Still open after round 2

Nothing from ids 0, 13 or 14. The residual the checker flagged for the chair is unchanged and is not
this owner's to close: the CSYS derating curve behind fix id 1 is KEMET `C1210C226K3PAC`, not the
fitted Samsung `CL32A226KAJNNNE`; margin is 51.1 µF vs the 44 µF minimum (16 %), which holds unless
the Samsung part derates worse than ~50 % at 8.4 V. Outstanding LCSC numbers remain deferred to the
layout-phase supply-chain pass (PM ruling R12).
