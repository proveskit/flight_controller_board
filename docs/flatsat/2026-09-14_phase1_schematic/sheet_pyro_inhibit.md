# Sheet report: `pyro_inhibit` — "Pyro Inhibit and Jumpers"

**File:** `FlatSat_V1/pyro_inhibit.kicad_sch` · **Generator:** `FlatSat_V1/tools/gen/pyro_inhibit_gen.py` · **Page:** 11 · **Refdes block:** 600–649 · **Sheet symbol uuid:** `ba398093-e7fc-4f25-8f04-4265c3e55b54` · **Instances path:** `/c64c0d72-a9f6-4f3a-891e-1f647558f538/ba398093-e7fc-4f25-8f04-4265c3e55b54`

## 1. Purpose

Bench inhibit for the FC's live pyro/heater driver U6 (TPS4H160): a single switch force-lows all three EN nets (`Deploy1_EN`, `Heater_EN`, `Deploy2_EN`) through Schottky diodes so the bench defaults to safe, plus six parallel 2‑pin headers across the existing RBF/inhibit-chain break points so the bench can be operated without Pico-Lock crimp pigtails (brief §6.5, decisions D1 and D6).

## 2. Block description

- **EN-line force-low diodes.** Three `Diode:BAT54W` (D600/D601/D602), anode on `Deploy1_EN`/`Heater_EN`/`Deploy2_EN` respectively, cathodes commoned on local net `PYRO_INH_COM`. The `Heater_EN` leg runs through JP600 (`Connector_Generic:Conn_01x02`, shunt fitted by default) before its diode, so the heater channel can be excluded from the inhibit later by pulling that one header, without a respin (D1).
- **Inhibit switch / state sense / SAFE LED.** `PYRO_INH_COM` runs to SW600 (SPST, closed = inhibited = safe default) to `GND`, with a parallel 2-pin header JP601 for an external panel-mount switch. R600 (**4.7k, pulled up to the FC `+3V3`** — review fix #2, §13) pulls `PYRO_INH_COM` up; R601 (4.7k) senses `PYRO_INH_COM` out to global label `PYRO_INHIBIT_STATE`; R602 (470 R) + LED600 (C2290, a **white** 0603) light from `3V3_EMU` through `PYRO_INH_COM` when the switch is closed and the emulator is powered. The pull-up and the SAFE LED are now on **different** rails on purpose: the armed-state EN level must not depend on the emulator being powered, while the LED is an emulator-side indicator and is deliberately left off the FC rail.
- **Bench RBF / inhibit shunt headers.** Six `Connector_Generic:Conn_01x02` (JP602–JP607, open by default, never a `_Bridged` symbol), each in parallel with an existing FC connector break point per D6: `VBATT_SENSE`↔`INHIB_1` (∥ J8), `INHIB_1`↔`IN_RBF` (∥ J29), `VBATT_SENSE`↔`INHIB_2` (∥ J7), `INHIB_2`↔`IN_RBF` (∥ J10), `IN_RBF`↔`VBUSP` (∥ J20/J30), `B-`↔`GND` (∥ J15/J19).
- **Test points.** TP600/601/602 on the three EN nets; TP603 on `PYRO_INH_COM`.

## 3. Parts table

| Ref | Value | Footprint | LCSC | Source |
|---|---|---|---|---|
| D600, D601, D602 | BAT54W | `Package_TO_SOT_SMD:SOT-323_SC-70` | needs LCSC | Nexperia BAT54W_SER datasheet (https://assets.nexperia.com/documents/data-sheet/BAT54W_SER.pdf) — actual package is SOT-323/SC-70, not the SOD-123 named in brief §6.5 text; see §7 deviations |
| JP600 | Conn_01x02 (shunt fitted by default) | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | needs LCSC | brief §6.5 / D1, rule 9 |
| JP601 | Conn_01x02 (no shunt; external panel switch) | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | needs LCSC | brief §6.5 |
| JP602–JP607 | Conn_01x02 (open by default) | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | needs LCSC | brief §6.5 / D6 |
| SW600 | SW_SPST | `Button_Switch_THT:SW_DIP_SPSTx01_Slide_9.78x4.72mm_W7.62mm_P2.54mm` | needs LCSC (deferred to the layout-phase supply-chain pass, R12) | brief §6.5. **Not** the same part as `bench_io`'s WDT_DISABLE toggle — corrected in review fix #7 (§13). SW703 there is `Switch:SW_SPDT`, value `SS12D10G4`, footprint `easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4`, LCSC **C2887259** (a 3-pin SPDT slide, from `debug_board_v1`). SW600 is a 2-pin SPST DIP slide with no MPN, no footprint and no LCSC in common with it. The footprint silkscreens only the word `on` with no safe/armed sense, so the mapping (`on` = closed = INHIBIT/SAFE) is carried as schematic text next to SW600 and in the jumper table |
| R600 | **4.7k** | `Resistor_SMD:R_0402_1005Metric` | **C25900** | PM ruling R6 (100k → 4.7k, ≤ 8.2k for RP2350 erratum E9) as applied in review fix #2 (§13). High side is the FC `+3V3` power symbol, **not** `3V3_EMU` — see §13. Same 4.7k 0402 part as R601 |
| R601 | 4.7k | `Resistor_SMD:R_0402_1005Metric` | **C25900** | brief §6.5 (PYRO_INHIBIT_STATE sense, ≤8.2k per RP2350-E9); LCSC C25900, exact value+footprint match in `refs/bom/BOM-proves_radio_stick_V2.csv` line 19 (R14/R15, 4.7k 0402) — fix round (§10) |
| R602 | 470R | `Resistor_SMD:R_0402_1005Metric` | **C25117** | LED series R. Value not specified by the brief. Re-sized in integrator fix round 3 (§12) for the LED that is actually fitted: C2290 is a **white** 0603, Vf 2.6–3.1 V, so (3.3 − Vf)/470 = **0.43–1.49 mA, ~0.96 mA typical** (1.0 mW worst case, against the part's 62.5 mW). LCSC C25117 = UNI-ROYAL 0402WGF4700TCE, 470 Ω 0402 1 % **Basic**, verified in the JLCPCB catalogue. The previous 1 k (C11702) was sized for a ~2.0 V green LED and gave only 0.2–0.8 mA into the white part |
| LED600 | LED | `LED_SMD:LED_0603_1608Metric` | **C2290** | SAFE indicator. `Value` corrected `LED_GREEN` → `LED` in integrator fix round 3 (§12): C2290 is Hubei KENTO **KT-0603W, a white 0603** (Vf 2.6–3.1 V, 360 mcd at 5 mA, Basic), and every other C2290 on this project (D201/D202 on `emulator_mcu`, D510 on `battery_protection_replica`, D1/D3 on proves_radio_stick_V2) carries `Value` = `LED`, so a grouped BOM now emits one line for one part number. `Datasheet` populated with the KT-0603W datasheet URL |
| TP600–TP603 | (net name) | `TestPoint:TestPoint_Pad_D1.5mm` | n/a | brief §6 (test points on bench-relevant rails) |
| #PWR600, #PWR601 | GND | (power symbol) | n/a | ground taps for the switch ladder and the ISS shunt header |
| #PWR602 | +3V3 | (power symbol) | n/a | FC 3.3 V rail (U10) feeding R600. Added in review fix #2 (§13); `power:+3V3` per brief §4.1 ("power symbols for `GND` / `+3V3`"), matching `solar_emulation`'s 8 placements |

BAT54W, the 2-pin headers, and SW600 remain "needs LCSC" — no as-ordered BOM or live-verified source was found for those (unchanged from §7; corrected in the fix round to no longer include R601/R602/LED600, and in review fix #2 to no longer include R600, which all have sources — see §10, §13). Those remaining LCSC numbers are deferred to the layout-phase supply-chain pass (PM ruling R12).

## 4. Interface nets

**Existing FC nets used (global labels, exact names, shape `passive` to match the promoted-label convention already on `eps_side`/`load_switches`; `VBUSP` shape `bidirectional` to match its existing global label):**
`Deploy1_EN`, `Heater_EN`, `Deploy2_EN`, `VBATT_SENSE`, `INHIB_1`, `INHIB_2`, `IN_RBF`, `B-`, `VBUSP`, `GND` (power symbol).

**New cross-sheet nets (brief §4.2):**
- `PYRO_INHIBIT_STATE` — **defined here** (global label, shape `output`), driven from `PYRO_INH_COM` through R601 (4.7k). Consumed by `emulator_mcu` (confirmed in the integration harness once that sheet existed: net gained pin `U200.35`).
- `3V3_EMU` — **consumed here** (one `global_label` placement, shape `input`, at R602's LED-resistor top) for the SAFE LED only. The second placement, at R600's pull-up top, was removed in review fix #2 (§13); R600 now runs to the FC `+3V3`. See §7 for why this is a plain global label rather than the `flatsat:3V3_EMU` power symbol.
- `+3V3` — **consumed here** (`power:+3V3` power symbol `#PWR602`, added in review fix #2), the high side of R600. This is an existing FC net (brief §4.1) driven by the FC's own U10, so unlike `3V3_EMU` it cannot raise `power_pin_not_driven` in a partial harness.

**Console rule this sheet now imposes on flight software** (review fix #2): `PYRO_INHIBIT_STATE` low means *"inhibit engaged" **or** "FC unpowered"*. The console must AND it with `EMU_FC3V3_SENSE` (`solar_emulation`'s 4.7k FC-`+3V3` presence tap) before reporting the inhibit as positively engaged. `PYRO_INHIBIT_STATE` high unambiguously means armed **and** FC powered.

**Local net (sheet-internal, not part of the §4 contract):** `PYRO_INH_COM` — the commoned diode-cathode / switch / pull-up / LED / sense-resistor node. Named with a `(label "PYRO_INH_COM")` on the vertical common rail at (76.2, 76.2) (fix round, see §10); confirmed in the netlist as `/Pyro Inhibit and Jumpers/PYRO_INH_COM` grouping `D600.3, D601.3, D602.3, JP601.1, LED600.1, R600.1, R601.1, SW600.1, TP603.1` (previously rendered as the synthetic name `Net-(D600-K)` before the label was added).

## 5. Jumper / header table

| Ref | Bridges | Default | Effect when changed |
|---|---|---|---|
| SW600 | `PYRO_INH_COM` ↔ `GND` | **Closed (`on`) = INHIBIT / SAFE** | Silkscreen `on` = contacts closed = inhibited. Open = ARMED. The DIP-slide footprint prints no safe/armed sense of its own, so this mapping is carried as schematic text next to SW600 and in the on-sheet jumper table (review fix #7, §13) |
| JP600 | `Heater_EN` ↔ D601 anode | **Shunt fitted** | Remove to exclude the heater channel from the inhibit without a respin (D1; flight_controller_board#53 ch3/ch4 crossing is unresolved so "heater-only" cannot be assumed non-pyro). **Caveat (review fix #6, §13):** with JP600 removed the SAFE LED and `PYRO_INHIBIT_STATE` still report on `PYRO_INH_COM`, which then covers **Deploy1/Deploy2 only** — `Heater_EN` is live and uninhibited while the indicator and the console interlock read "safe". Treat ch3/ch4 as **ARMED** whenever JP600 is out |
| JP601 | `PYRO_INH_COM` ↔ `GND` | No shunt (header only) | Wire an external 2-pin panel-mount switch here, in parallel with on-board SW600. Closed = SAFE |
| JP602 (INH_S1) | `VBATT_SENSE` ↔ `INHIB_1` | Open | Bridges ∥ J8 (INHIBIT_S1_Picolock) |
| JP603 (INH_S2) | `INHIB_1` ↔ `IN_RBF` | Open | Bridges ∥ J29 (INHIBIT_S2_Picolock) |
| JP604 (INH_P1) | `VBATT_SENSE` ↔ `INHIB_2` | Open | Bridges ∥ J7 (INHIBIT_P1) |
| JP605 (INH_P2) | `INHIB_2` ↔ `IN_RBF` | Open | Bridges ∥ J10 (INHIBIT_P2) |
| JP606 (RBF) | `IN_RBF` ↔ `VBUSP` | Open | Bridges ∥ J20/J30 (RBF_Inhibit / RBF_Picolock) |
| JP607 (ISS) | `B-` ↔ `GND` | Open | Bridges ∥ J15/J19 (ISS_INHIBIT / ISS_INHIBIT_Picolock) |

JP602–JP607 are current-rated for a ~3 A shunt assumption (matching the crimp connectors they parallel) and are **never fitted on flight units** — noted on the sheet.

**Power-up recipe (review fix #7, §13; now on the sheet under the jumper table).** To power the FC with no crimp plugs fitted, bridge:

1. **JP607** — `B-` ↔ `GND`, the pack-return path (∥ J15/J19 ISS inhibit);
2. **JP606** — `IN_RBF` ↔ `VBUSP`. **Closing this energises `VBUSP`.** This is the opposite of the naive "remove before flight = safety pin" reading: a shunt *across* JP606 closes the RBF break and turns the FC on; pulling it opens the bus;
3. **one** inhibit path — **JP602 + JP603** (`VBATT_SENSE`→`INHIB_1`→`IN_RBF`, ∥ J8 + J29) **or** **JP604 + JP605** (`VBATT_SENSE`→`INHIB_2`→`IN_RBF`, ∥ J7 + J10).

Leave the others open. Verified against the Rev2 baseline netlist: `IN_RBF` = {J10.2/4, J20.1/3, J29.1, J30.2}, `VBUSP` = {…, D15.1/K, J20.2/4, J30.1, U10.13/14 VIN/VCC, …}, `INHIB_1` = {J29.2, J8.1}, `INHIB_2` = {J10.1/3, J7.2/4}, `VBATT_SENSE` = {…, J7.1/3, J8.2, …}.

**"All jumpers open" is not a guarantee that `VBUSP` is dead.** The FC's own USB-C J12 feeds `VBUS` → D15 (DFLS130L Schottky, anode `VBUS`, cathode `VBUSP`, confirmed in the baseline netlist) → `VBUSP` regardless of every jumper on this sheet. Unplug FC USB as well.

## 6. Datasheet facts relied on

- **Nexperia BAT54W_SER** (https://assets.nexperia.com/documents/data-sheet/BAT54W_SER.pdf): VF ≈ 0.28 V at 0.64 mA (≤240 mV @ 0.1 mA, ≤320 mV @ 1 mA), quoted verbatim in a sheet text note and used to confirm the inhibited EN-node voltage stays well under the TPS4H160-Q1's VIL(max).
- **TPS4H160-Q1** §6.5 Logic Input: VIL(max) 0.8 V, VIH(min) 2 V; IN pins have 100–250 kΩ internal pull-downs — cited from the brief (already sourced there from the TI datasheet) to size the inhibited-node margin: with the switch closed each EN node sits at ~0.28 V, comfortably below the 0.8 V VIL(max).
- **RP2350 erratum E9** (brief rule 10): every emulator-read GPIO needs an external pull ≤ 8.2 kΩ. R601 (4.7 kΩ) on `PYRO_INHIBIT_STATE` satisfies this.
- **flight_controller_board#53** (ch3/ch4 crossed, unresolved) — cited in a sheet note next to the diode block as the reason all three EN nets, not just Deploy1/Deploy2, are covered by one inhibit (D1).

## 7. Validation results

### 7.1 `sch_lint.py`

```
$ python3 tools/sch_lint.py pyro_inhibit.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/ba398093-e7fc-4f25-8f04-4265c3e55b54 --refdes-block 600-649
pyro_inhibit.kicad_sch: 22 symbol instances, 7 lib symbols, 41 wires, 0 errors, 0 warnings
```

### 7.2 `harness_erc.sh` (final run, with `solar_power_injection`, `emulator_mcu`, `solar_emulation` and `bench_io` also present on disk)

```
=== violations on sheets matching 'Pyro Inhibit and Jumpers' ===
total 0
errors: 0
```

Full-project ERC delta vs the promoted baseline at that point (library noise excluded): `pin_not_connected` +0, `pin_to_pin` (error) +1 and (warning) +51, `power_pin_not_driven` +6, `single_global_label` **-9** (all eight promotions plus `USBBOOT` resolved once the consuming sheets appeared), `multiple_net_names`/`same_local_global_label`/`unconnected_wire_endpoint` +0. All non-zero deltas were independently confirmed **not** attributable to this sheet: re-running the harness with `pyro_inhibit.kicad_sch` temporarily removed reproduced the same `pin_to_pin` error (root sheet, `U7` GND pins 6/7, a pre-existing FC/easyeda2kicad symbol quirk unrelated to any new sheet) and the same `power_pin_not_driven` baseline, confirming this sheet adds zero errors of any kind, on itself or elsewhere.

Earlier in the same working session, with only `solar_power_injection` and `bench_io` present (before `emulator_mcu` existed), this sheet's harness run showed exactly one residual warning — `single_global_label` on `PYRO_INHIBIT_STATE` (its only consumer, `emulator_mcu`, not yet on disk) — matching brief §7's anticipated exception exactly. That warning is now gone (confirmed above) now that `emulator_mcu` consumes the net (`U200.35`).

### 7.3 Netlist diff (this sheet's contribution)

```
+ D600, D601, D602, JP600–JP607, SW600, R600, R601, R602, LED600, TP600–TP603, #PWR600, #PWR601   [/Pyro Inhibit and Jumpers/]
~ Deploy1_EN: +[D600.1, TP600.1]
~ Heater_EN:  +[JP600.1, TP601.1]
~ Deploy2_EN: +[D602.1, TP602.1]
~ VBATT_SENSE:+[JP602.1, JP604.1]
~ INHIB_1:    +[JP602.2, JP603.1]
~ INHIB_2:    +[JP604.2, JP605.1]
~ IN_RBF:     +[JP603.2, JP605.2, JP606.1]
~ VBUSP:      +[JP606.2]
~ B-:         +[JP607.1]
~ GND:        +[..., JP601.2, JP607.2, SW600.2, ...]
+ PYRO_INHIBIT_STATE: R601.2 (later also U200.35 once emulator_mcu existed)
+ 3V3_EMU (merged into emulator_mcu's/bench_io's rail): R600.2, R602.2
```

Exactly the nine existing nets brief §4 lists for this sheet (`Deploy1_EN`, `Heater_EN`, `Deploy2_EN`, `VBATT_SENSE`, `INHIB_1`, `INHIB_2`, `IN_RBF`, `B-`, `VBUSP`, plus `GND`) gained pins, plus the two new contract nets (`PYRO_INHIBIT_STATE` defined, `3V3_EMU` consumed). No existing net lost a pin; no unrelated net touched.

### 7.4 Visual check

Exported `pyro_inhibit` (page 11) to PDF from the full harness project and read it back: title block, functional-area group notes, all three diode rows, the switch/LED/pull-up ladder, and the six shunt-header rows all render with labels on wire ends and junction dots at the T-connections; no overlapping text observed.

## 8. Deviations from the brief

1. **BAT54W footprint.** Brief §6.5 text says "SOD-123"; the part's actual package (Nexperia datasheet, and the only `Diode:BAT54W` KiCad symbol/footprint pairing available) is SOT-323/SC-70 (a 3-pin package — pin 2 is a hidden no-connect, consistent with BAT54W's real pinout). Used `Package_TO_SOT_SMD:SOT-323_SC-70`; flagging per brief §7's instruction to report deviations rather than force a mismatched footprint.
2. **`3V3_EMU` implemented as a global label, not the `flatsat:3V3_EMU` power symbol**, on this (consuming) sheet. Brief §4.2 frames the whole new-net table as "global labels," and only calls out the `flatsat:3V3_EMU` power symbol explicitly for the *defining* sheet (`emulator_mcu`, at the regulator output). A power-symbol pin is electrically type `power_in`; placing it here with no local `power_out` driver produced a genuine `power_pin_not_driven` **ERC error** whenever `emulator_mcu` wasn't yet on disk (confirmed by an isolated repro). An ordinary `global_label` merges onto the exact same project-wide net (confirmed in §7.3 once `emulator_mcu` existed: `3V3_EMU` correctly grouped `R600.2, R602.2` with `emulator_mcu`'s and `bench_io`'s pins) without that failure mode, and degrades gracefully to the single `single_global_label` warning brief §7 explicitly anticipates when the partner sheet is absent.
3. **LED series-resistor value (R602)** and **LED choice** are not specified by the brief ("3V3_EMU → R → LED → PYRO_INH_COM"). As delivered after integrator fix round 3 (§12): LED600 = C2290, the project's standard white 0603 (Vf 2.6–3.1 V), with R602 = 470 R giving 0.43–1.49 mA, ~0.96 mA typical. The round-1/2 text claiming "≈1.3 mA into a ~2.0 V green LED" was wrong on both the colour and the current.

## 9. Assumptions / open questions for the reviewer

- ~~LCSC part numbers are not filled in anywhere on this sheet~~ — resolved in the fix round 2 (§10.4): R601 (C25900), R602 (C11702 — **superseded by C25117 in fix round 3, §12**), and LED600 (C2290) have as-ordered/already-used sources and now carry `LCSC Part`. BAT54W, the 2-pin headers, SW600, and R600 (100k) genuinely have no repo BOM source and stay "needs LCSC" in §3.
- JP601's mating hardware (a specific panel-mount switch/cable) is left to the integrator/BOM phase; the header itself is generic `Conn_01x02`.
- The six shunt headers assume ~3 A shunts (matching the crimp connectors they parallel); no current-limiting element is added since they are direct 1:1 parallel taps, per D6.
- ~~`PYRO_INH_COM` is deliberately left as an unlabelled local net (no `local_label`) since it never leaves this sheet~~ — resolved in the fix round (§10): it now carries an explicit `(label "PYRO_INH_COM")`.

## 10. Fix round

An independent verifier found four defects in the version above (2 major, 2 minor). All four are fixed in `tools/gen/pyro_inhibit_gen.py`; the sheet was regenerated and the full validation loop re-run. Nothing electrical changed — no component, pin, or wire endpoint moved — so the netlist and ERC results are identical to §7 except that `PYRO_INH_COM` is now a named net instead of the synthetic `Net-(D600-K)`.

### 10.1 Defects and fixes

1. **Major — all 11 text notes centre-justified, running up to ~17 mm off the left edge of the A3 page.** `text_note()` had no `(justify ...)`, so KiCad centred every multi-line note on its anchor instead of flowing it down-and-right, truncating the leading 14–20 characters of every note block in the plotted PDF. Fixed by adding `(justify left top)` to `text_note()`'s `(effects ...)` block, copying the convention already used by `bench_io_gen.py`'s `add_text()`. Confirmed on the regenerated SVG: 0 `<text>`/`<tspan>` elements with negative x (previously the minimum was −16.96 mm); the leftmost text anchor is now at x = 11.0 mm, inside the A3 frame.
2. **Major — none of the 17 global labels carried a justify, so label text centred on its anchor and overlapped its own flag outline / the wire; TestPoint and R601/LED600 Reference/Value fields collided.** Two sub-fixes:
   - `global_label()` already supported an optional `justify` parameter but no caller passed one. All 7 call sites (the 3-row EN-net loop, `PYRO_INHIBIT_STATE`, the two `3V3_EMU` consumers, the 5-row shunt-header loop's left/right labels, and `B-`) are rot=0, so all now pass `justify="left"`, matching the rot-0→left / rot-180→right convention already established by `bench_io_gen.py`/`solar_power_injection_gen.py` (verified against `bench_io.kicad_sch`'s own 21 labels). Re-rendered PDF crops (300–500 dpi) confirm every label now sits cleanly inside its flag shape with no overlap on the wire.
   - `place_symbol()` gained `ref_dx/ref_dy/val_dx/val_dy/hide_ref/hide_val` parameters. R601's Value was moved from below the body (colliding with LED600's Reference 1.27 mm away) to stacked above the body (`val_dy=-5.08`), clearing LED600 by more than 6 mm. TP600–TP603 (`Connector:TestPoint`, rotated 90°) turned out to have a second, worse problem on inspection: KiCad composes a property's own `(at x y 0)` angle with the parent symbol's rotation, so their Reference/Value text renders **vertically**, not horizontally as the unrotated offset math assumed. At this row pitch there is no clear vertical band for ~6–9 mm of rotated text next to the row-above/row-below global label, and — on the two jumper rows — next to JP600's `Conn_01x02` Value, which sits at the same y by coincidence of the row spacing. Iterative re-rendering (300–500 dpi PDF crops) turned up three real collisions beyond the ones named in the original finding (TP600 vs. the D1 text note, TP601 vs. the `Deploy1_EN` label, TP602 vs. JP600's `Conn_01x02` Value) that no amount of re-offsetting cleared for all four points simultaneously without risking new collisions elsewhere. Per the finding's own suggested fix ("or drop the redundant net-name Value on the rotated test points"), both Reference and Value are now hidden (`hide_ref=True, hide_val=True`) for all four TestPoints; the net each one taps is still identified by the row's own wired global label, the symbol's `Description` property, and the sheet's `Test points on the three EN nets and PYRO_INH_COM` note. Refdes and net name remain intact in the BOM/instances data (`hide` only affects on-canvas visibility). Verified clean at 300–500 dpi across the whole sheet (see §10.2).
3. **Minor — trailing top-level `(embedded_fonts no)` on a sub-sheet file.** Removed the line from the generator's footer (`footer.append('\t(embedded_fonts no)')` deleted). The file now ends `)` / `)` with no trailing top-level `embedded_fonts`, matching `load_switches.kicad_sch`; the per-symbol `(embedded_fonts no)` lines inside `lib_symbols` (inherited from the pantry `.sexp` blocks) are untouched and expected.
4. **Minor — `PYRO_INH_COM` has no netlist name.** Added `local_label("PYRO_INH_COM", BUS_X, 76.2, justify="right bottom")` on the vertical common rail, at the R601 tap point. `justify="right bottom"` was chosen (over the helper's `"left bottom"` default) after the first attempt placed the label directly on top of R601's Reference/Value text; the final placement sits in the clear space between the D602 row and R601, confirmed collision-free by re-render. The net now appears in the netlist as `/Pyro Inhibit and Jumpers/PYRO_INH_COM` instead of the synthetic `Net-(D600-K)`.

### 10.2 Re-validation

**`sch_lint.py`** (unchanged from §7.1):
```
pyro_inhibit.kicad_sch: 22 symbol instances, 7 lib symbols, 41 wires, 0 errors, 0 warnings
```

**`harness_erc.sh` "Pyro Inhibit and Jumpers"** (full project, all 6 sheets present):
```
=== violations on sheets matching 'Pyro Inhibit and Jumpers' ===
total 0
errors: 0
```
Full-project delta vs. the promoted baseline is unchanged from §7.2 (`pin_not_connected` +0, `power_pin_not_driven` +6, `pin_to_pin` warning +67, `single_global_label` −9, others +0) — none of it attributable to this sheet, as previously confirmed. This sheet still contributes exactly 0 errors and 0 warnings of any kind.

**Netlist diff (this sheet's contribution):** identical to §7.3, with one change — the local net is now named:
```
+ /Pyro Inhibit and Jumpers/PYRO_INH_COM: D600.3, D601.3, D602.3, JP601.1, LED600.1, R600.1, R601.1, SW600.1, TP603.1
```
(previously `Net-(D600-K)`). All other net deltas (`Deploy1_EN`, `Heater_EN`, `Deploy2_EN`, `VBATT_SENSE`, `INHIB_1`, `INHIB_2`, `IN_RBF`, `VBUSP`, `B-`, `GND`, `PYRO_INHIBIT_STATE`, `3V3_EMU`) are byte-for-byte the same pins as §7.3. Component count unchanged: 22 new parts under `/Pyro Inhibit and Jumpers/`.

**Visual check (superseding §7.4):** §7.4's "no overlapping text observed" was not reproducible, as the verifier correctly found. This round's check was done properly: the regenerated sheet was rendered to PDF (`kicad-cli sch export pdf`) and to SVG, at 260–500 dpi, in the full 6-sheet harness project (not in isolation). The full page was inspected at 300 dpi in three vertical tiles (top notes/diode rows/sense-LED block; jumper-header rows 1–4; jumper-header rows 5–6 and the jumper population table), then every symbol cluster flagged by the original finding (all three EN rows' TestPoints/JP600, R601/LED600/PYRO_INH_COM, TP603, the jumper table) was additionally re-cropped at 400–500 dpi and inspected individually, iterating twice more (see defect 2 above) until no residual overlap remained. SVG text-anchor extents were also checked programmatically: 0 negative-x text elements (previously the leftmost ran to −16.96 mm); minimum x = 11.0 mm, inside the A3 border.

### 10.3 Outcome

All four defects fixed; no new errors or warnings introduced (still 0/0 on this sheet, both in isolation via `sch_lint.py` and in the full 6-sheet harness); the netlist contribution is unchanged except for the newly-named `PYRO_INH_COM` net. §4 and §9 above are corrected in place to match (net is now named; the open question is resolved, struck through rather than deleted for traceability). Net removed from the open-questions list: `PYRO_INH_COM` naming (§9). One design choice is newly recorded: TP600–TP603 show only their symbol graphic on-canvas (Reference/Value hidden) rather than colliding text — a `hide`-only change with no netlist or BOM effect, disclosed here rather than silently reverted from the original report's "readable" claim.

## 11. Fix round 2

A second independent verifier found six further defects in the fix-round-1 sheet (2 major, 4 minor). All six are fixed in `tools/gen/pyro_inhibit_gen.py`; the sheet was regenerated and the full validation loop re-run, including a new automated geometry audit (below) built specifically to catch the class of defect in finding 1. No pin, wire electrical endpoint, or net membership changed from §10 except the three new `LCSC Part` properties (finding 3) — the netlist contribution and ERC results are otherwise identical to §10.2.

### 11.1 Defects and fixes

1. **Major — unmarked 4-way meeting point at (86.36, 76.2).** R602's series-resistor-to-LED wire ran vertically at x=86.36 (R602's pin1 x, since R602 was placed at x=91.44), which is the exact x of R601's pin2 — and R601's row is at y=76.2. The vertical wire therefore passed straight through R601 pin2 *and* through the start point of the R601→`PYRO_INHIBIT_STATE` wire, with no junction there — a genuine ambiguous 4-way meeting point (confirmed reproducible by the verifier: adding a junction there merges `PYRO_INHIBIT_STATE` onto `LED600`/`R602`'s net and makes the interlock read "not inhibited" permanently). Fixed by moving R602 from x=91.44 to x=93.98, so its pin1 (and the vertical wire) sit at x=88.9 instead of 86.36. The vertical run (88.9,60.96)–(88.9,82.55) now crosses the R601→`PYRO_INHIBIT_STATE` wire at (88.9,76.2), which is the *interior* of both segments — not a pin, not either wire's endpoint — an ordinary unconnected crossing that needs no junction (standard schematic convention: no dot = no connection). LED600's `LCSC Part` (see item 3) also gained the SAFE-LED-vs-inhibit-state sentence from finding 5 in its Description, and the anode-side wire was correspondingly re-routed through (88.9,82.55) instead of (86.36,82.55).
2. **Major — 9 of 17 global labels struck through by their own wire.** All labels that sit at the LEFT end of a rightward wire (`Deploy1_EN`, `Heater_EN`, `Deploy2_EN`, and the left label of each of the six shunt-header rows: `VBATT_SENSE` ×2, `INHIB_1`, `INHIB_2`, `IN_RBF`, `B-`) were `rot=0, justify="left"`, so their text flowed in the same +x direction as the wire and sat on top of it (`B-` plotted with its wire covering the hyphen, reading as `B`). Fixed by changing all 9 to `rot=180, justify="right"`, matching the convention already used on `eps_side`/`load_switches`/`solar_emulation` for left-side labels — text now flows away from the wire. The 8 right-hand labels (`INHIB_1`/`IN_RBF`/`INHIB_2`/`VBUSP` at x=91.44 and `PYRO_INHIBIT_STATE`/both `3V3_EMU` at x=101.6) were left at `rot=0, justify="left"`, which was already clean.
3. **Major — LCSC Part omitted on three parts with an as-ordered/already-used source.** R601 (4.7k 0402), R602 (1k 0402), and LED600 (LED_0603_1608Metric) all have exact value+footprint matches: R601/R602 in `refs/bom/BOM-proves_radio_stick_V2.csv` (R14/R15 → C25900 for 4.7k; R10/R13/R80/R93 → C11702 for 1k), LED600 already used on this project for D201/D202 (`emulator_mcu.kicad_sch`) and D510 (`battery_protection_replica.kicad_sch`) → C2290. Added `LCSC Part` extra-properties to all three in the generator (`extra_props=[("LCSC Part", "C25900")]` etc.); §3 and §9 corrected to match. R600 (100k), D600–D602, JP600–JP607, and SW600 remain "needs LCSC" — no repo BOM source exists for those. `jlcpcb/project.db` was not touched.
4. **Minor — TP600's circle/lead drawn over the D1 requirement note.** In fix round 1, TP600 sat at (35.56,36.83), directly inside the D1 note's text band (25.4,36.83, two lines). Root-caused and fixed properly this round (see §11.2 for the two rejected intermediate attempts): TP600 now taps the Deploy1_EN row at x=48.26 (near D600's own anode) instead of x=35.56, and drops *below* the row (y=48.26, i.e. row_y+3.81) instead of above it — clear of the D1 note (which stays at its original y=36.83, unmoved) and >=16 mm from TP601's centre (31.75,49.53), so their rotated pin-stub-plus-circle graphics no longer interleave either (see §11.2).
5. **Minor — brief §6.5's "dark LED does not mean released" note not on the sheet.** Added a fourth/fifth line to the "Inhibit State Sense, SAFE LED, Pull-up" note block: *"SAFE LED lit = inhibit engaged AND emulator powered. A dark LED does NOT mean the inhibit is released -- the inhibit (SW600/JP601) does not depend on 3V3_EMU. Verify at TP603 / PYRO_INH_COM."* The same sentence was already present in LED600's (non-plotting) Description property; it's now also on-canvas. The block below it (the VF-margin note) was pushed from y=127.0 to y=132.08 (+5.08) to keep the sheet's established 2.54 mm/line note pitch from running the two blocks together; the section-4 header note two blocks later still clears with a comfortable 5.08 mm gap.
6. **Minor — TP600–TP603 show as unlabelled circles (Ref/Value hidden).** Kept hidden (re-showing rotated Ref/Value was already tried and rejected in fix round 1 for real collisions at this row pitch — §10.1 item 2). Added a visible legend instead, per the finding's own suggested fix: `"Test points (Ref/Value hidden on-canvas; net name shown here): TP600 = Deploy1_EN   TP601 = Heater_EN   TP602 = Deploy2_EN   TP603 = PYRO_INH_COM"`, placed at (110.0, 50.0) — clear of the D1 note (whose longest line ends around x=104, per a character-count estimate) and of every other note/label/wire on the sheet, confirmed by re-render.

### 11.2 Two rejected intermediate fixes for TP600 (kept here for traceability)

Getting TP600 off the D1 note took three attempts; the first two are recorded because they introduced their own regressions that a less careful re-render would have missed:

- **Attempt 1: move the D1 note down to y=39.4 instead of moving TP600.** This cleared TP600 (which stayed at y=36.83) but moved the note's second line to y=41.94 — landing almost exactly on D600's default Reference position (57.15, 44.45−2.54=41.91), a *new* collision not present in fix round 1 or flagged by the second verifier. Caught by re-rendering and visually inspecting the diode block after the change (not just the specific coordinate the finding named).
- **Attempt 2: drop TP600 below its row at the standard 7.62 mm offset, same x=35.56.** This cleared the note cleanly (confirmed by re-render) but put TP600 at (35.56,48.26), only ~4 mm (diagonal) from TP601 at (31.75,49.53) — both TestPoint symbols' pin-stub+circle graphics (a ~4 mm-long rotated flag shape, per the `Connector:TestPoint` library pin length 2.54 mm + circle offset 3.302 mm) visually interleaved into what looked like one connected shape, even though they are on different nets with no shared coordinate. Caught by re-rendering and cropping the specific area at 4x zoom.
- **Final fix (in §11.1 item 4):** reverted the note to its original y=36.83, and moved TP600 to (48.26, 48.26) — a distinct tap point near D600's anode, far from both the note and TP601. Verified clean by re-render (§11.3).

### 11.3 Re-validation

**Geometry audit (new tool, built for this fix round).** A standalone script (`geom_audit.py`, parses the `.kicad_sch` text directly — independent of `sch_lint.py`) checks two conditions across all 41 wires and 41 symbol pins: (a) any pin lying in the *interior* of a wire it doesn't own, (b) any wire endpoint lying in the interior of a different wire. Both must be zero for the sheet to be free of finding 1's defect class (an unmarked ambiguous meeting point). Result on the fixed sheet:
```
wires: 41
junctions: 11
pins: 41
pin-in-wire-interior: 0 (must be 0)
wire-endpoint-in-wire-interior: 0 (must be 0)
```
The former (86.36,76.2) meeting point is confirmed gone; the new crossing at (88.9,76.2) is a plain interior-interior crossing (not a pin, not an endpoint of either wire) and was independently visually confirmed clean at 3x zoom (no junction dot, two lines simply cross).

**`sch_lint.py`** (unchanged from §7.1/§10.2):
```
$ python3 tools/sch_lint.py pyro_inhibit.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/ba398093-e7fc-4f25-8f04-4265c3e55b54 --refdes-block 600-649
pyro_inhibit.kicad_sch: 22 symbol instances, 7 lib symbols, 41 wires, 0 errors, 0 warnings
```

**`harness_erc.sh` "Pyro Inhibit and Jumpers"** (full project, all 6 sheets present):
```
=== violations on 'Pyro Inhibit and Jumpers' ===
total 0
errors: 0
```
Full-project ERC delta vs. the promoted baseline (library noise excluded): `pin_not_connected` +0, `power_pin_not_driven` +5, `pin_to_pin` (warning) +68, `single_global_label` −9, `multiple_net_names`/`same_local_global_label`/`unconnected_wire_endpoint` +0 — all pre-existing and attributable to `Solar and Sensor Emulation` (5 `power_pin_not_driven` errors, all `U30x` pin 8 VCC) and other sheets, not to this one, matching §7.2/§10.2's already-confirmed attribution (re-verified this round by inspecting the per-sheet breakdown directly in the harness output: `Pyro Inhibit and Jumpers` contributes 0 of every violation type). This sheet still contributes exactly 0 errors and 0 warnings of any kind.

**Netlist diff (this sheet's contribution):** byte-for-byte identical to §10.2 except the three new `LCSC Part` properties (not netlist-visible) — same 22 components under `/Pyro Inhibit and Jumpers/`, same net deltas:
```
~ Deploy1_EN: +[D600.1, TP600.1]
~ Heater_EN:  +[JP600.1, TP601.1]
~ Deploy2_EN: +[D602.1, TP602.1]
~ VBATT_SENSE:+[JP602.1, JP604.1]
~ INHIB_1:    +[JP602.2, JP603.1]
~ INHIB_2:    +[JP604.2, JP605.1]
~ IN_RBF:     +[JP603.2, JP605.2, JP606.1]
~ VBUSP:      +[JP606.2]
~ B-:         +[JP607.1]
+ PYRO_INHIBIT_STATE: R601.2, U200.35
+ /Pyro Inhibit and Jumpers/PYRO_INH_COM: D600.3, D601.3, D602.3, JP601.1, LED600.1, R600.1, R601.1, SW600.1, TP603.1
```
No existing net lost a pin; no unrelated net touched; no component added or removed.

**Visual check.** Full-page and per-region re-renders (`kicad-cli sch export pdf/svg`, 300 dpi PNG crops and SVG text-anchor extents) confirmed, in the fixed sheet, in the full 6-sheet harness project:
- The former unmarked meeting point at (86.36,76.2): now a clean unmarked *crossing* (no dot, standard convention), verified both geometrically (§11.3 above) and visually at 3x zoom.
- All 9 relabelled global labels (`Deploy1_EN`, `Heater_EN`, `Deploy2_EN`, `VBATT_SENSE` ×2, `INHIB_1`, `INHIB_2`, `IN_RBF`, `B-`) sit cleanly inside their flag shapes with text flowing away from the wire; `B-`'s hyphen is fully visible.
- D600/D601/D602 reference/value text, the D1 note, and TP600 (now at (48.26,48.26)) are all mutually clear — zero overlap.
- TP600 and TP601 are visually distinct and well-separated (>=16 mm centre-to-centre).
- The new TP legend note at (110.0,50.0) is clear of the D1 note and everything else.
- The extended SAFE-LED note (5 lines) and the VF-margin note below it (moved to y=132.08) are both fully readable with a clear gap between them and before the section-4 header.
- SVG text-anchor extents: 0 negative-x text elements; minimum x = 11.0 mm (unchanged from §10.2, inside the A3 border).
- All 6 shunt-header rows (`JP602`–`JP607`) and their left/right labels, notes, and jumper-population table render exactly as in §10.2, now with clean left labels per item 2 above.

### 11.4 Outcome

All six fix-round-2 defects fixed; two intermediate attempts for finding 4 were tried, found to introduce their own regressions on re-render, and replaced (§11.2) rather than shipped. `sch_lint.py` and the full-project harness both remain 0 errors / 0 warnings for this sheet; the geometry audit built for this round confirms zero pin-in-wire-interior and zero wire-endpoint-in-wire-interior cases (the specific defect class of finding 1) across all 41 wires and 41 pins. The netlist contribution is unchanged from §10.2 except for the three new `LCSC Part` properties, which are not netlist-visible. §3 and §9 above are corrected in place. No component, pin, or wire electrical endpoint moved from §10's version except the R602/LED600 re-route (finding 1) and the TP600 re-route (finding 4), both of which preserve the exact same net memberships as before (confirmed in the netlist diff, §11.3).

---

## 12. Integrator fix round 3 (2026-09-14)

**Ownership note.** Applied by the **integrator**, not the sheet agent, after an independent check of the first
integration pass. Brief §3 rule 2 puts `pyro_inhibit.kicad_sch` and `tools/gen/pyro_inhibit_gen.py` in the
sheet agent's writable set; that agent's run had finished. Recorded as an explicit rule deviation in
`integration_report.md` §1.2. Both the sheet and its generator were changed; the delivered sheet is the
generator's own output with the header uuid `f09ab68d-4b6e-4de6-a0d0-0f22e160b47a` restored afterwards.

### 12.1 The finding

> **[minor]** LED600: `Value` `LED_GREEN` contradicts its assigned LCSC `C2290` (white 0603), and its
> `Datasheet` field is empty.

Two separate problems in one part:

1. **BOM.** A grouped BOM keyed on (value, footprint, LCSC) would emit **two lines for one part number** —
   `LED_GREEN / C2290` here and `LED / C2290` for `emulator_mcu` D201/D202 and `battery_protection_replica`
   D510.
2. **Electrical.** C2290 is Hubei KENTO **KT-0603W**, a *white* 0603: Vf 2.6–3.1 V, 360 mcd at 5 mA, 100 mW,
   Basic (verified in the JLCPCB catalogue mirror `parts-fts5.db`). R602 = 1 k off a 3.3 V rail therefore gave
   **(3.3 − 2.6…3.1)/1 k = 0.2–0.8 mA**, not the "≈1.3 mA" §3/§9 claimed for a ~2.0 V green part. At
   worst-case Vf the SAFE indicator was close to dark — poor for a *safety* indicator.

### 12.2 What changed

| item | before | after |
|---|---|---|
| LED600 `Value` | `LED_GREEN` | `LED` (matches D201/D202/D510 and proves_radio_stick_V2 D1/D3) |
| LED600 `Datasheet` | *(empty)* | `https://www.lcsc.com/datasheet/lcsc_datasheet_2305091500_Hubei-KENTO-Elec-KT-0603W_C2290.pdf` |
| LED600 `Description` | generic | now names the part and its Vf/intensity |
| R602 `Value` | `1k` | `470R` |
| R602 `LCSC Part` | `C11702` | **`C25117`** (UNI-ROYAL 0402WGF4700TCE, 470 Ω 0402 1 % Basic, 1.36 M in stock) |
| R602 `Description` | "SAFE LED series R" | now carries the current arithmetic |
| SAFE-LED note | 5 lines | 6 lines: *"LED600 = C2290, a WHITE 0603 (Vf 2.6-3.1 V); R602 = 470 R gives 0.43-1.49 mA, ~0.96 mA typical."* |

R602 dissipates 1.0 mW worst case against the part's 62.5 mW. Nothing else on the sheet moved: the LED/R602
net topology, the R601 → `PYRO_INHIBIT_STATE` crossing at (88.9, 76.2) and the diode/inhibit chain are
byte-identical in the netlist.

**Why not keep 1 k for heritage parity?** proves_radio_stick_V2 drives its C2290s through 1 k (R13/R80), and
so do `emulator_mcu` R206/R211 and `battery_protection_replica` R519. But those are *activity/status* LEDs;
this one reports whether the pyro inhibit is engaged, so brightness at worst-case Vf matters. 470 R is a JLC
**Basic** part, so it adds no setup cost, and it is the value the independent check asked for.

### 12.3 One self-inflicted regression, caught and reverted

An intermediate attempt also moved the SAFE-LED note block from y = 118.11 to y = 124.0, on the strength of
`tools/gen/geomcheck.py` reporting a `text-over-text` hit between that block and `#PWR601`'s "GND" value text.
That was a **geomcheck false positive**: geomcheck models every `(text)` block as vertically *centred* on its
anchor (correct for `solar_emulation`), while this sheet's `text_note()` emits `justify left top`, so blocks
run **downward** from the anchor. The move pushed the now-6-line block to y 124.0–133.7 and straight into the
VF-margin note at y = 132.08 — visible as overstruck text in the 400 dpi render. Reverted to y = 118.11
(block occupies 118.11–127.83, clear of the GND text ending at 117.35 above and the next note at 132.08
below) and confirmed in the render rather than in the tool. A comment in the generator records the geomcheck
modelling mismatch so the next reader does not repeat it.

### 12.4 Re-run validation (fix round 3, as delivered)

```
python3 tools/sch_lint.py pyro_inhibit.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/ba398093-e7fc-4f25-8f04-4265c3e55b54 --refdes-block 600-649
  -> 22 symbol instances, 7 lib symbols, 41 wires, 0 errors, 0 warnings

kicad-cli sch erc --severity-all (full integrated project)
  -> erc_summary.py --sheet "Pyro Inhibit and Jumpers" --ignore-noise : total 0, errors: 0
```

PDF page 10 of the integrated export, re-read at 150 dpi full page and 400 dpi over the sense/LED block: the
six-line note reads cleanly, the new LED600/R602 line is legible, and the next note block is well clear.

`tools/gen/geomcheck.py --overlaps` reports 4 `wire-through-text` and 0 `text-over-text`. The 4 are
byte-identical to the pre-edit file (JP601/SW600/`Conn_01x02` field text on the GND drop, and the D1 note
crossed by the TP603 stub) — pre-existing, and listed as open items in §11.4.

### 12.5 Still open after this round

1. D600–D602 (BAT54W), JP600–JP607, SW600 and R600 (100 k) still need LCSC numbers. R601, R602 and LED600 no
   longer do. — *Partly resolved in §13: R600 is now 4.7 k and carries C25900. The rest are deferred to the
   layout-phase supply-chain pass (PM ruling R12).*
2. The four pre-existing `wire-through-text` hits above (cosmetic; both notes and fields stay legible at
   300 dpi).
3. `PYRO_INHIBIT_STATE` in the *armed* state sits at ≈ 104.7 kΩ to `3V3_EMU` (R601 4.7 k + R600 100 k), far
   above the RP2350 erratum-E9 8.2 kΩ limit — the brief's own §6.5 topology, carried to the Fable round as
   integration-report item O13. — **Resolved in §13** (PM ruling R6 + review fix #2): R600 is 4.7 k to the
   FC `+3V3`, so the armed-state pull-up class is 4.7 k, inside the 8.2 kΩ limit.

## 13. Review fixes (Fable review-and-fix round, 2026-09-14)

Chair-dispositioned fix-now items applied to this sheet. Every change was made in **both**
`tools/gen/pyro_inhibit_gen.py` and (by regenerating) `FlatSat_V1/pyro_inhibit.kicad_sch`, per the
integrator's convention — re-running the generator reproduces the delivered sheet (identical geometry, nets
and properties; UUIDs are freshly minted on every run, as they always have been on this sheet).

**Ids applied: #2, #6, #7.** None declined.

### 13.1 Fix #2 (major) — PM ruling R6 applied, with the pull-up moved off `3V3_EMU`

R6 had not been carried out: R600 was still 100 k in both the sheet and the generator. Applying R6 *exactly
as worded* (4.7 k to `3V3_EMU`) was independently shown to create a new armed-state hazard, so the fix applies
R6's substance on a different supply.

| | Before | After |
|---|---|---|
| R600 value | `100k` | **`4.7k`** (PM ruling R6, ≤ 8.2 kΩ for RP2350 erratum E9) |
| R600 LCSC | none | **C25900** (same 4.7 k 0402 as R601) |
| R600 high side | `3V3_EMU` global label at (101.6, 88.9) | **`power:+3V3`** symbol `#PWR602` at (101.6, 88.9) |
| `3V3_EMU` placements on this sheet | 2 (pull-up + LED) | 1 (**LED only** — R602/LED600 stay on `3V3_EMU`) |

**Why the supply moved.** With `3V3_EMU` at 0 V (emulator unpowered) a 4.7 k R600 is a 4.7 k pull-*down* on
`PYRO_INH_COM`. The FC drives each EN net from 3.3 V through its own 4.7 k series resistor (R104 `Deploy1_EN`
/ R100 `Heater_EN` / R103 `Deploy2_EN`, brief §4.1); the BAT54W then forward-conducts and the EN node divides
to

> V(EN) = (3.3 V + V<sub>F</sub>) / 2 ≈ **1.8 V**  (4.7 k : 4.7 k, V<sub>F</sub> ≈ 0.3 V at ~0.3 mA)

against TPS4H160-Q1 **V<sub>IH(min)</sub> = 2.0 V** (§6.5 Logic Input). An FC-only bench run (brief decision
D11) could therefore silently **not fire**, and because the level depends on a phantom rail it would be
intermittent. At the original 100 k the same divider gives 3.15 V, which is why the hazard is *created by*
R6 rather than pre-existing.

**Why the FC `+3V3` fixes it.** Armed (SW600 open), `PYRO_INH_COM` sits at `+3V3` and both ends of every
BAT54W are at the same potential — zero bias, no divider — so each EN node stays at the full **+3V3
(≈ 3.3 V, ≫ the 2.6 V target and the 2.0 V V<sub>IH</sub>)** whether or not the emulator is powered. `+3V3`
tracks FC power exactly (U10 runs off `VBUSP`; USB J12 reaches `VBUSP` through D15), so the sense reports the
state of the thing it is sensing. Inhibited state is unchanged: SW600 shorts `PYRO_INH_COM` to `GND`,
0.70 mA flows through R600, EN nodes sit at V<sub>F</sub> ≈ 0.28 V at 0.64 mA — well under
V<sub>IL(max)</sub> 0.8 V.

**Back-feed check.** With the FC powered and the emulator off, `PYRO_INH_COM` at 3.3 V drives R601 (4.7 k)
into U200 pin 35's ESD clamp: (3.3 − 0.7)/4.7 k ≈ **0.55 mA**, far below the RP2350 per-pin limit. This is the
identical sense-tap rule `solar_emulation` already documents for its own 4.7 k taps ("limit back-feed into an
unpowered emulator ESD diode to about 0.55 mA per line").

**Deviation recorded.** Brief §6.5 literally says "100 k pull-up from `3V3_EMU` to `PYRO_INH_COM`". Both
halves of that sentence are now superseded: the value by PM ruling R6, the supply by this fix. This is a
**chair-accepted deviation**, not a capture error, and the reasoning is carried on the sheet itself as a boxed
text note at (139.7, 88.9) so a future respin cannot "tidy" R600 back onto `3V3_EMU` (CLAUDE.md hard rule 3 —
schematic text notes are requirements).

**Consequence for flight software** (also on the sheet and in §4): `PYRO_INHIBIT_STATE` low now means
*"inhibit engaged" **or** "FC unpowered"*; the console must AND it with `EMU_FC3V3_SENSE` before reporting the
inhibit as positively engaged. The SAFE LED is deliberately left on `3V3_EMU` — it is an emulator-side
indicator, not an interlock, and moving it would load the FC rail for no gain.

**Power-symbol choice.** `power:+3V3` per brief §4.1 ("power symbols for `GND` / `+3V3`"), matching
`solar_emulation`'s 8 placements. Unlike the `3V3_EMU` case in §8 deviation 2, this cannot raise
`power_pin_not_driven` in a partial harness: `+3V3`'s `power_out` driver is the FC's own U10, always on disk.
The generator's `place_symbol()` gained a `pwr_val_dy` argument for this — `power:GND`'s visible Value hangs
below its pin, a rail symbol's sits above it, and the library y-axis sign flips into schematic space.

### 13.2 Fix #6 (minor) — JP600-removed caveat

With JP600 pulled, `Heater_EN` (U6 IN3) is uninhibited while `PYRO_INH_COM`, the SAFE LED and the console
interlock all still read "inhibited" — misleading, and brief decision D1 states the heater channel cannot be
assumed non-pyro (flight_controller_board#53, ch3/ch4 crossed). Caveat text added in both places named by the
finding:

- the SAFE-LED / pull-up note at (25.4, 118.11): *"JP600 REMOVED: SAFE LED and PYRO_INHIBIT_STATE then cover
  Deploy1/Deploy2 only; Heater_EN is live — treat ch3/ch4 as ARMED (D1 / flight_controller_board#53)."*
- the JP600 row of the on-sheet jumper table at (25.4, 243.84), as a `CAVEAT:` block.

Mirrored as a console rule in §5 (JP600 row) above. The emulator GPIO map lives on `emulator_mcu`, which this
fixer does not own — flagged for that sheet's owner rather than edited here.

### 13.3 Fix #7 (minor) — power-up recipe, RBF direction, SW600 identity

1. **Power-up recipe** added under the on-sheet jumper table, including the explicit warning that a shunt
   *across* JP606 **closes** `IN_RBF` to `VBUSP` and energises the bus — the opposite of the naive "remove
   before flight = safety pin" reading — and that FC USB J12 powers `VBUSP` through D15 regardless of every
   jumper on this sheet. Chain verified against the Rev2 baseline netlist (see §5).
2. **SW600 safe/armed mapping** added to the sheet: a short note beside the switch at (95.25, 99.06)
   (*"SW600 silkscreen 'on' = CLOSED = INHIBIT / SAFE (default). Open / slider off = ARMED. JP601 panel switch
   is in parallel: closed = SAFE too."*) plus an `SW600` row at the head of the on-sheet jumper table. The
   `SW_DIP_SPSTx01_Slide` footprint silkscreens only the word `on`, with no safe/armed sense of its own.
3. **§3 part-identity error corrected.** §3 claimed SW600 was "the same part as bench_io's WDT_DISABLE
   toggle". It is not: `bench_io` SW703 is `Switch:SW_SPDT`, value `SS12D10G4`, footprint
   `easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4`, LCSC **C2887259** — a 3-pin SPDT slide from `debug_board_v1`.
   SW600 is a 2-pin `Switch:SW_SPST` on `Button_Switch_THT:SW_DIP_SPSTx01_Slide_9.78x4.72mm_W7.62mm_P2.54mm`
   with no MPN. Nothing is shared. SW600's LCSC stays deferred to the supply-chain pass (R12), per the
   finding's own scope note.

### 13.4 Re-validation

`tools/sch_lint.py` — clean:

```
pyro_inhibit.kicad_sch: 23 symbol instances, 8 lib symbols, 41 wires, 0 errors, 0 warnings
```

`tools/harness_erc.sh pyro` — **0 violations on this sheet**, 11 project errors (unchanged from the Rev2 + 8
promotions baseline: `pin_not_connected` 5 + `power_pin_not_driven` 6, all on FC sheets, delta +0 on every
error class).

Netlist, this sheet's delta from the fix:

| Net | Change |
|---|---|
| `+3V3` | **+`R600.2`** (existing FC net gains one pin; nothing removed) |
| `3V3_EMU` | now `…, R602.2, …` from this sheet only — `R600.2` moved off it |
| `/Pyro Inhibit and Jumpers/PYRO_INH_COM` | unchanged: `D600.3, D601.3, D602.3, JP601.1, LED600.1, R600.1, R601.1, SW600.1, TP603.1` |
| `PYRO_INHIBIT_STATE` | unchanged: `R601.2, U200.35` |

No net lost a pin; no component was removed; R600's refdes, footprint and pin count are unchanged, so the
change is a value + one-terminal-net edit plus one added power symbol (`#PWR602`).

PDF page 11 re-exported from the harness project at 300 dpi and read back: the R600/`+3V3` branch, the
boxed pull-up rationale at (139.7, 88.9), the SW600 legend at (95.25, 99.06), the 9-line SAFE-LED note and
the 19-line jumper table all render inside the A3 frame with no overlaps. One collision was found and fixed
during this round: the first cut of the SW600 legend ran 59 characters wide and struck through the boxed
note, so the legend was rewrapped to ≤ 34 characters and the box moved 125.0 → 139.7 mm.

### 13.5 Still open after this round

1. D600–D602 (BAT54W), JP600–JP607 and SW600 still need LCSC numbers — deferred to the layout-phase
   supply-chain pass (PM ruling R12), not a finding.
2. The four pre-existing `wire-through-text` hits from §12.5 item 2 (cosmetic).
3. The JP600-removed caveat should also appear in the emulator GPIO map on `emulator_mcu` — that sheet's
   owner's call, not this file's.
