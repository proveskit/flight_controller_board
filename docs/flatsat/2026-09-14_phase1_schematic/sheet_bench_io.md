# `bench_io` — Bench IO (page 12, refdes 700–799)

Sheet file: `FlatSat_V1/bench_io.kicad_sch` · Generator: `FlatSat_V1/tools/gen/bench_io_gen.py` · Sheet-symbol uuid `54b8f29e-9dcb-4e24-99b9-415a110b338a` · Instances path `/c64c0d72-a9f6-4f3a-891e-1f647558f538/54b8f29e-9dcb-4e24-99b9-415a110b338a`

## 1. Purpose

Gives the emulator MCU its own USB-C (power + data) and SWD debug port, and gives the bench scripted control of the FC's `FC_RESET`, `USBBOOT` and `WDT_DISABLE` lines through open-drain N-FETs, plus a passive bench header exposing the emulator's UART/spare GPIO and those same three FC control nets. Per brief §6.6 / D8.

## 2. Block description

- **Block A — Emulator USB-C (J701).** `Connector:USB_C_Receptacle_USB2.0_16P`, footprint `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` (C165948), power+data only. VBUS pins (A4/A9/B4/B9, physically ganged in the symbol) → `VBUS_EMU` power rail with a 10 µF bulk cap (C701), a test point (TP701) and the sheet's one `PWR_FLAG` (#FLG701) — `VBUS_EMU` is **defined** on this sheet per the §4.2 ownership table. CC1/CC2 each get a 5.1 kΩ pulldown to GND (R701/R702, C25905) — this presents the port as a UFP (Rd on both CC lines), so an *upstream* DFP (the bench PC / USB-C charger) sources `VBUS_EMU`; J701 itself never sources VBUS. D+ (A6/B6 tied) → 22 Ω (R703, C25092) → `EMU_USB_DP`; D− (A7/B7 tied) → 22 Ω (R704, C25092) → `EMU_USB_DM` — mirrors the FC's own J12/R7/R8 arrangement exactly (same value, same topology, confirmed by reading the FC root sheet's R7/R8/J12 wiring before laying this out). SBU1/SBU2 are `no_connect`. Shield and the GND-pin group tie to `GND`. No USB ESD array: none of the common 2-line array footprints in the standard libraries matched this connector's exact D+/D− pin geometry without a bespoke footprint, so it is omitted per brief's "otherwise omit and note" — text note on the sheet records this; exposure is the same as any bench USB cable.
- **Block B — Emulator SWD (J702).** 3-pin JST-SH, drawn as `Connector_Generic:Conn_01x03` with `Footprint` overridden to `Connector_JST:JST_SH_BM03B-SRSS-TB_1x03-1MP_P1.00mm_Vertical` (C160389) — the same pattern the FC root sheet itself uses for J22 (its own SWD port), since no dedicated JST_SH-3 symbol exists in the installed KiCad 10 standard libraries. Pin 1 → `EMU_SWCLK`, pin 2 → `GND`, pin 3 → `EMU_SWDIO`, mirroring J22's pin order (SWCLK/GND/SWDIO).
- **Block C — EMU_RUN / EMU_BOOTSEL_SW buttons (SW701/SW702).** `Adafruit ItsyBitsy RP2040-eagle-import:SWITCH_TACT_SMT4.6X2.8` (Value `KMR2`, footprint `FC_DEV_BOARD:BTN_KMR2_4.6X2.8`, C72443) — the exact symbol/footprint/LCSC the FC uses for its own SW1 (USBBOOT) and SW2 (RESET) buttons, confirmed by reading the FC root sheet before reuse. Each button ties one side (A+A′, shorted) to its global label and the other side (B+B′, shorted) to GND, exactly as SW1/SW2 are wired on the FC root. `EMU_RUN` and `EMU_BOOTSEL_SW` are **consumed** here — both are defined on `emulator_mcu` (RUN pull-up node; BOOTSEL node mirroring the FC's SW1→D4→R10→QSPI_SS arrangement).
- **Block D — WDT_DISABLE toggle (SW703).** `Switch:SW_SPDT` (system library, all 3 terminals used and wired — see Fix round 2 §2 for why this replaced the 2-pin `SW_SPST` symbol), footprint `easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4` (LCSC C2887259, live-verified — see Fix round 2 §7) — the project-standard bench slide switch: `debug_board_v1` (the board brief §6.6 cites for this circuit) uses this exact MPN/footprint for its own equivalent toggle (SW3, `Switch:SW_Push_SPDT`; `refs/upgraded/debug_board_v1/debug_board_v1.kicad_sch`). Common pole (pin 2) → GND; pin 1 → the `WDT_DISABLE` global label; pin 3 (the other throw) is a marked `no_connect` — slider toward pin 1 grounds `WDT_DISABLE` through the common pole, slider toward pin 3 leaves it open. A bench-operable, always-available parallel path to the FC's own J4 shunt jumper (same net, same watchdog-integrator node; closing this switch has the identical electrical effect as fitting J4, without needing to find the jumper). Independent of the EMU_CTL_WDT_DIS open-drain driver in Block E — this is a manual override, the driver is the scripted one.
- **Block E — Open-drain FC bench-control drivers (Q701/Q702/Q703).** Per D8 / brief rule 10 (RP2350 erratum E9), 1 kΩ gate series R + 4.7 kΩ gate pulldown exactly as brief §6.6 specifies. Each: `EMU_CTL_FC_RESET` / `EMU_CTL_USBBOOT` / `EMU_CTL_WDT_DIS` (inputs, driven by `emulator_mcu`, default low) → 1 kΩ gate series R (R705/R707/R709, C11702) → **BSS138** gate, with a 4.7 kΩ gate pulldown to GND (R706/R708/R710, C25900, ≤ 8.2 kΩ per erratum E9 so an unprogrammed/BOOTSEL-mode/unpowered emulator can never float the gate high and assert the FC net) → drain to `FC_RESET`/`USBBOOT`/`WDT_DISABLE` (global labels, existing FC nets) → source to GND. Each driver only ever *pulls* its FC net low; it can never drive it high (open-drain, N-channel, source grounded). **BSS138, not 2N7002** (see Fix round §1): with the brief's own 1 k/4.7 k gate divider, a worst-case IOVDD (3.3 V −5 %) GPIO drive gives V_GS ≈ 2.59 V at the gate — above BSS138's V_GS(th) max (1.5 V, giving ≥ 1.08 V of guaranteed overdrive at worst case) but *not* comfortably above 2N7002's V_GS(th) max (2.5 V, only 0.09–0.22 V of overdrive, no on-state parameter specified that close to threshold). BSS138 is pin-compatible (SOT-23, G/S/D = pins 1/2/3, same as 2N7002) so no layout/footprint change was needed, only the part.
- **Block F — Bench header (J703).** `Connector_Generic:Conn_02x05_Odd_Even`, footprint `Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical` (needs LCSC), pin 1 called out in a text note (silkscreen / connector-key marking, no physical pin-1 indicator drawn on the schematic itself since that's a layout/silkscreen concern). Pinout exactly as brief §6.6 lists it: `3V3_EMU`, `GND`, `EMU_UART_TX`, `EMU_UART_RX`, `EMU_GPIO_SPARE0`, `EMU_GPIO_SPARE1`, `FC_RESET`, `USBBOOT`, `WDT_DISABLE`, `GND`. `3V3_EMU` and `GND` are power ties (`GND` via `power:GND`, `3V3_EMU` via a plain `global_label` — see §5 below for why not a power symbol); everything else is a passive tap, this sheet never drives `FC_RESET`/`USBBOOT`/`WDT_DISABLE` from the header side, only from the Block E drivers.

## 3. Parts table

| Ref | Value | Footprint | LCSC | Source of LCSC # |
|---|---|---|---|---|
| J701 | USB_C_Receptacle_USB2.0_16P | `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` | C165948 | brief §6.6 (same part as the FC's own J12) |
| R701 | 5.1k | `Resistor_SMD:R_0402_1005Metric` | C25905 | brief §6.6 (named) + as-ordered `refs/bom/BOM-proves_radio_stick_V2.csv` (same 5.1k 0402 USB-C CC pulldown, R26/R27) |
| R702 | 5.1k | `Resistor_SMD:R_0402_1005Metric` | C25905 | as above |
| R703 | 22 | `Resistor_SMD:R_0402_1005Metric` | C25092 | brief §6.6 / §4.2 (same part as FC R7/R8) |
| R704 | 22 | `Resistor_SMD:R_0402_1005Metric` | C25092 | brief §6.6 / §4.2 |
| C701 | 10uF | `Capacitor_SMD:C_0805_2012Metric` | needs LCSC | — |
| TP701 | VBUS_EMU | `TestPoint:TestPoint_Pad_D1.5mm` | needs LCSC | — |
| J702 | SWD | `Connector_JST:JST_SH_BM03B-SRSS-TB_1x03-1MP_P1.00mm_Vertical` | C160389 | brief §6.6 (same part as FC J22) |
| SW701 | KMR2 | `FC_DEV_BOARD:BTN_KMR2_4.6X2.8` | C72443 | brief §6.6 (same part as FC SW1/SW2) |
| SW702 | KMR2 | `FC_DEV_BOARD:BTN_KMR2_4.6X2.8` | C72443 | brief §6.6 |
| SW703 | SS12D10G4 | `easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4` | C2887259 | Live-verified on lcsc.com / jlcpcb.com (Fix round 2 §7); MPN from `debug_board_v1` SW3, brief-cited reference |
| Q701 | BSS138 | `Package_TO_SOT_SMD:SOT-23` | needs LCSC | — (datasheet: onsemi/Fairchild BSS138, `BSS138-D.PDF` — see Fix round §1) |
| Q702 | BSS138 | `Package_TO_SOT_SMD:SOT-23` | needs LCSC | — |
| Q703 | BSS138 | `Package_TO_SOT_SMD:SOT-23` | needs LCSC | — |
| R705 | 1k | `Resistor_SMD:R_0402_1005Metric` | C11702 | as-ordered `refs/bom/BOM-proves_radio_stick_V2.csv` (1k 0402, R10/R13/R80/R93) |
| R706 | 4.7k | `Resistor_SMD:R_0402_1005Metric` | C25900 | as-ordered `refs/bom/BOM-proves_radio_stick_V2.csv` (4.7k 0402, R14/R15) |
| R707 | 1k | `Resistor_SMD:R_0402_1005Metric` | C11702 | as above |
| R708 | 4.7k | `Resistor_SMD:R_0402_1005Metric` | C25900 | as above |
| R709 | 1k | `Resistor_SMD:R_0402_1005Metric` | C11702 | as above |
| R710 | 4.7k | `Resistor_SMD:R_0402_1005Metric` | C25900 | as above |
| J703 | Bench Header | `Connector_PinHeader_2.54mm:PinHeader_2x05_P2.54mm_Vertical` | needs LCSC | — |

Power symbols (not in BOM): #PWR701–#PWR709, #PWR711–#PWR718 (17 total; GND / VBUS_EMU ties — there is no #PWR710 or #PWR719), #FLG701 (PWR_FLAG on VBUS_EMU).

**Needs LCSC** (rule 5 — no as-ordered BOM or live-verified number found for these): C701, TP701, Q701/Q702/Q703 (BSS138), J703.

## 4. Interface nets

**Existing FC nets used** (global labels, exact names per brief §4.1): `FC_RESET`, `USBBOOT`, `WDT_DISABLE`, `GND`.

**New cross-sheet nets defined here** (per §4.2 ownership table): `VBUS_EMU` (power symbol `flatsat:VBUS_EMU`, `PWR_FLAG` #FLG701 on this sheet — this is the one and only source flag for this rail).

**New cross-sheet nets consumed here** (defined on `emulator_mcu`): `EMU_USB_DP`, `EMU_USB_DM`, `EMU_SWCLK`, `EMU_SWDIO`, `EMU_RUN`, `EMU_BOOTSEL_SW`, `EMU_CTL_FC_RESET`, `EMU_CTL_USBBOOT`, `EMU_CTL_WDT_DIS`, `EMU_UART_TX`, `EMU_UART_RX`, `EMU_GPIO_SPARE0`, `EMU_GPIO_SPARE1`, `3V3_EMU`.

**Local-only:** none (every net on this sheet is either an existing FC global, a brief §4.2 cross-sheet global, or `GND`/`VBUS_EMU`).

### `3V3_EMU` — power symbol vs global label

Brief §4.2 calls `3V3_EMU` a "power symbol" on its defining sheet (`emulator_mcu`, the regulator output). On this *consuming* sheet I initially used the pantry's `flatsat:3V3_EMU` power-input symbol, but that symbol's single pin is typed `power_in` with no matching `power_out` anywhere until `emulator_mcu` exists — before that sheet was on disk this produced an ERC **error** (`power_pin_not_driven`, not just a warning). I checked how `pyro_inhibit` (already on disk, also consumes `3V3_EMU` for its pull-up/LED per §6.5) handles the same net: it uses a plain `global_label "3V3_EMU"`, not the power symbol. I matched that convention on the bench header. With `emulator_mcu` now integrated this is moot either way (both approaches net-tie correctly), but the global-label form degrades gracefully to a `single_global_label` *warning* rather than a `power_pin_not_driven` *error* if a consuming sheet is ever checked in isolation again — consistent with the one other sheet that had already made this choice.

## 5. Jumper / switch table

| Ref | Function | Default state | Note |
|---|---|---|---|
| SW701 | `EMU_RUN` → GND (momentary) | open | Tact switch, mirrors FC SW2 |
| SW702 | `EMU_BOOTSEL_SW` → GND (momentary) | open | Tact switch, mirrors FC SW1 |
| SW703 | `WDT_DISABLE` → GND via common pole (toggle/slide, pin 1 vs. pin 3/NC) | open (watchdog enabled) | Bench-operable parallel path to the FC's own J4 shunt; closing (slider toward pin 1) has the same electrical effect as fitting J4 |
| Q701/Q702/Q703 | Scripted open-drain pulldown of `FC_RESET`/`USBBOOT`/`WDT_DISABLE` | off (net not pulled) | Gate held low by its 4.7 kΩ pulldown whenever `EMU_CTL_*` is not actively driven high. BSS138 (see Fix round §1) |

No brief-mandated shunt headers live on this sheet (rule 9 doesn't apply here — nothing on `bench_io` is "shunt fitted by default").

## 6. GPIO / net map for firmware (bench-side view)

This sheet has no MCU of its own; the table below is the bench_io-side contract that `emulator_mcu` firmware must honor (full GPIO assignment lives in the `emulator_mcu` report):

| Net | Direction at `emulator_mcu` | What it does here |
|---|---|---|
| `EMU_CTL_FC_RESET` | GPIO output, default low | Drives Q701 gate through 1k; high = pulls FC `RUN`/`FC_RESET` low |
| `EMU_CTL_USBBOOT` | GPIO output, default low | Drives Q702 gate; high = pulls FC `USBBOOT`/`BOOTSEL` chain low |
| `EMU_CTL_WDT_DIS` | GPIO output, default low | Drives Q703 gate; high = pulls FC `WDT_DISABLE` (watchdog integrator node) low |
| `EMU_RUN` | GPIO in (10k pull-up on `emulator_mcu`) | SW701 pulls low momentarily to reset the emulator |
| `EMU_BOOTSEL_SW` | GPIO / BOOTSEL node on `emulator_mcu` | SW702 pulls low momentarily to force emulator USB-boot |
| `EMU_SWCLK`/`EMU_SWDIO` | SWD pins | External debug probe via J702 |
| `EMU_USB_DP`/`EMU_USB_DM` | USB_DP/USB_DM pins (no series R on that sheet) | 22R series lives here (Block A); emulator sheet wires its pins directly |
| `EMU_UART_TX`/`EMU_UART_RX`/`EMU_GPIO_SPARE0`/`EMU_GPIO_SPARE1` | GPIO | Passively exposed on J703 pins 3/4/5/6 |

## 7. Datasheet facts relied on

- **BSS138** (onsemi/Fairchild `BSS138-D.PDF`, ON CHARACTERISTICS table, fetched and confirmed live this round): V_GS(th) min/typ/max = 0.8 / 1.3 / 1.5 V at V_DS=V_GS, I_D=1 mA; R_DS(on) ≤ 6.0 Ω at V_GS=4.5 V, V_DS=5 V, I_D=0.22 A; I_D(on) ≥ 0.2 A at V_GS=10 V. Chosen (Fix round §1) because with the brief's 1 k/4.7 k gate divider off a 3.3 V-class GPIO, worst-case V_GS at the gate is ≈2.59 V (IOVDD −5 %) — ≥ 1.08 V above BSS138's V_GS(th) max, comfortably in saturation, versus only 0.09–0.22 V of overdrive on a 2N7002 (V_GS(th) max 2.5 V). Required sink current on either driven net is a few hundred µA (FC_RESET ≈330 µA through R1 10k to +3V3; USBBOOT ≈245 µA through R10 1k + R2 10k to +3V3, both from `tools/baseline/netlist.kicadxml`), trivial for either FET once actually enhanced — the margin problem was V_GS headroom against V_GS(th), not current capacity. Never in the flight power path (satisfies hard rule 6 — nothing added in series with a flight power path; these are parallel taps on control nets).
- **2N7002** (Diodes Inc. `DS11303 Rev 33-2`, July 2013, ON CHARACTERISTICS): V_GS(th) max 2.5 V, no on-state parameter (R_DS(on), I_D(on)) specified anywhere near a 2.6–2.7 V gate drive — the lowest R_DS(on) test point is V_GS=5.0 V. Recorded here as the reason 2N7002 was rejected for Q701–Q703 (Fix round §1), not as the part used.
- **RP2350 erratum E9** (brief rule 10, quoted from the brief's own citation): A2 silicon leaks up to 120 µA on an input-buffer-enabled floating GPIO, settling near 2V, unless the external pull is ≤ 8.2 kΩ. All three gate pulldowns here are 4.7 kΩ, matching the value used throughout the rest of the brief's E9-affected nets. The A4 stepping corrects this erratum; the 4.7 k pulldown is the A2-safe value and could be relaxed if A4-stepping emulator silicon is fitted (noted on the sheet, Block E, per brief §6.6).
- **FC J12/R7/R8 USB arrangement** (read directly from `FlatSat_V1/FlatSat_V1.kicad_sch`): J12 is `Connector:USB_C_Receptacle_USB2.0_16P` at (157.48, 38.1); D+ (A6/B6) and D− (A7/B7) are each tied together locally and routed through a 22 Ω 0402 resistor (R8 for D+, R7 for D−) before reaching the RP2350's `USB_DP`/`USB_DM` (via intermediate `USB_D+`/`USB_D-` labels). `bench_io` reproduces this exact topology for the emulator's own port.
- **FC J22 / SW1 / SW2** (same file): J22 (SWD) and SW1/SW2 (tact buttons) are both drawn with generic `Connector_Generic`/`Adafruit...SWITCH_TACT_SMT4.6X2.8` symbols and a `Footprint` property override to the real part — `bench_io` copies this pattern rather than searching for symbols that may not exist in the installed libraries (confirmed: no `JST_SH_BM03B` symbol exists in any installed `.kicad_sym` on this machine).
- **FC USBBOOT → BOOTSEL path** (same file, per brief §6.6's note requirement): `USBBOOT` ties to D4 (NSR0320) **cathode**; D4 **anode** → R10 (1k) → `BOOTSEL` (also reachable from `R91` 0R → `FLASH_SS` → `R2` 10k → +3V3), same node SW1 pulls low. Confirmed against `tools/baseline/netlist.kicadxml`: `USBBOOT = D4.1 (pinfunction K_1, cathode), J16.1, SW1.A/A'`, `Net-(D4-A) = D4.2 (pinfunction A_2, anode), R10.2`, `BOOTSEL = R10.1, R91.1, U18.60`. Q702 pulling `USBBOOT` low therefore reproduces an SW1 press exactly, through the same diode/resistor path — noted on the sheet, Block E. (Polarity corrected in Fix round 2 §6 — the sheet's own Block E note never stated polarity and was unaffected; only this sentence was wrong.)

## 8. Validation results

*Updated across two fix rounds — see §10 and §11. Numbers below are from the post-fix-round-2 run; sch_lint's wire count moved from 62 (original) to 66 (round 1, D+/D- reroute) and stayed at 66 through round 2 (SW703's rewiring and the SWD-area GND move changed wire endpoints, not the count; the new no_connect on SW703 pin 3 is a separate element type, not a wire).*

### `sch_lint.py`
```
$ python3 tools/sch_lint.py bench_io.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/54b8f29e-9dcb-4e24-99b9-415a110b338a --refdes-block 700-799
bench_io.kicad_sch: 39 symbol instances, 12 lib symbols, 66 wires, 0 errors, 0 warnings
```

### `harness_erc.sh "Bench IO"` (full six-sheet hierarchy — all six new sheets are on disk)
```
harness: sheets in hierarchy: Emulator MCU Solar and Sensor Emulation Solar Power Injection
  Battery Replica and Bench Power Pyro Inhibit and Jumpers Bench IO

=== ERC delta vs baseline (Rev2 + 8 promotions; noise excluded) ===
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

=== violations on sheets matching 'Bench IO' ===
total 0
errors: 0
```
All project-wide delta (+5 power_pin_not_driven, +68 pin_to_pin, vs. the other sheets' own baselines) comes from `emulator_mcu` / `solar_emulation` / `battery_protection_replica` (the other sheets landing/changing in parallel) — **zero** of it is attributed to `/Bench IO/`. The fix round's D+/D- reroute briefly introduced a `no_connect_connected` warning on this sheet (R704 pin 1 routed through J701's SBU2 no-connect marker at the same coordinates) — found by this same harness run, fixed by moving the reroute's jog point off that x-coordinate, and confirmed gone (0 violations of any kind on `/Bench IO/`, re-run in §10).

### Netlist diff (this sheet's contribution)
```
added nets defined/sourced here: VBUS_EMU (C701.1, J701.A4/A9/B4/B9, TP200.1[emulator_mcu], TP701.1, U202.1/3[emulator_mcu])
added nets consumed here, now matched on emulator_mcu:
  EMU_BOOTSEL_SW: D200.1[emulator_mcu], SW702.A/A'
  EMU_CTL_FC_RESET: R705.1, U200.18[emulator_mcu]
  EMU_CTL_USBBOOT:  R707.1, U200.19[emulator_mcu]
  EMU_CTL_WDT_DIS:  R709.1, U200.29[emulator_mcu]
  EMU_RUN:          R205.2[emulator_mcu], SW701.A/A', U200.26[emulator_mcu]
  EMU_SWCLK:        J702.1, U200.24[emulator_mcu]
  EMU_SWDIO:        J702.3, U200.25[emulator_mcu]
  EMU_USB_DM:       R704.2, U200.51[emulator_mcu]
  EMU_USB_DP:       R703.2, U200.52[emulator_mcu]
changed (existing FC) nets -- gained pins, none lost:
  FC_RESET:    +[J703.7, Q701.3]
  USBBOOT:     +[J703.8, Q702.3]
  WDT_DISABLE: +[J703.9, Q703.3, SW703.1]
  GND:         +[all this sheet's GND ties, plus every other new sheet's]
removed nets: 0
```
Exactly the existing nets brief §4.1 says this sheet touches (`FC_RESET`, `USBBOOT`, `WDT_DISABLE`, `GND`) gained pins and nothing else; the eight label-promotion renames are untouched by this sheet (verified separately by the integrator per brief §4.3). Re-run after the fix round (§10) — same result.

### Visual check
Exported to PDF/SVG and reviewed at zoom (`kicad-cli sch export pdf|svg`, then `pdftocairo` crops of every block, 300–600 dpi). Found and fixed three real layout defects in the original pass:
1. Symbol `(at x y)` with an omitted rotation (`rot=0` → 2-token `(at x y)` instead of 3-token `(at x y 0)`) — valid to my own lint's regex parser but **not** to KiCad's real parser (`kicad-cli` reported "Failed to load schematic" when the sheet was checked standalone, and the harness silently skipped the sheet entirely rather than erroring). Fixed by always emitting the rotation token.
2. `(text ...)` notes have no default `justify`, so KiCad *centers* them on the given `(at)` point rather than left-anchoring — every multi-line note was drifting left/up of where the generator "placed" it, crossing wires and the sheet's own title block. Fixed by adding explicit `(justify left top)`.
3. For a symbol rotated 90°/270°, a property's *stored* text angle (always 0 in this generator, for Reference/Value alike) is **not** what gets rendered — kicad-cli's plotter combines it with the parent symbol's own rotation. This pass's independent verifier found the original fix for this (§10 below has the corrected, confirmed-by-render account: rot=90 parts render a stored-angle-0 property horizontally when given a `dx` split, which is why R701/R702/R706/R708/R710 were already fine; rot=270 parts render a stored-angle-0 property **vertically** regardless of `dx` or `dy` — confirmed against the FC's own SW1/SW2 root-sheet render, where Value "KMR2" is genuinely vertical by design and Reference "SW1"/"SW2" is stored at angle 90 to render horizontal). The original claim that a plain default `dy` split "becomes the correct horizontal split" after a 270° rotation was wrong and is what the verifier caught on SW701/SW702/TP701.

A second independent verifier pass (§11) found four more real defects that survived rounds 1–2 of visual review (a GND symbol drawn inside a global label's text box, Q701/Q702/Q703's Reference/Value struck through by their own drain/source wires, VBUS_EMU's rail name hidden, and SW703's 2-pin symbol on a 3-pad footprint) plus two documentation-only errors; all fixed and re-verified, see §11.

## 9. Assumptions and open questions for the reviewer

1. **BSS138 LCSC number** — left blank per rule 5 (no as-ordered BOM hit, not verified live against LCSC; see Fix round §1 for why BSS138 replaced 2N7002). Any SOT-23 BSS138 works electrically; the integrator or supply-chain pass should pick and verify a specific LCSC part.
2. **USB ESD array omitted** — I looked for a 2-line USB ESD diode array footprint matching this connector's D+/D− pin pitch in the standard libraries and didn't find one that was an unambiguous drop-in; brief explicitly allows "omit and note" for this case. If the reviewer has a specific part in mind (e.g. one already used elsewhere in this repo), it's a small addition.
3. **Bench header pin-1 marking** is a text note only (no drawn pin-1 triangle on the schematic symbol itself, since `Connector_Generic:Conn_02x05_Odd_Even` doesn't carry one) — the footprint's own silkscreen is what actually marks pin 1 on the board; flagged in case the reviewer wants a schematic-level marker too.
4. ~~**SW703 LCSC number**~~ — resolved in Fix round 2 §7: C2887259, live-verified on lcsc.com / jlcpcb.com (the number is embedded in SW703's own Datasheet URL, inherited from `debug_board_v1`).
5. Per brief rule 5, `LCSC Part` is populated where a number came from the brief's own citations (USB-C receptacle, 22R-class resistors, JST-SH connector, KMR2 buttons), an as-ordered BOM (5.1k CC pulldowns, 1k/4.7k gate network — all four traced to `refs/bom/BOM-proves_radio_stick_V2.csv`, Fix round §2), or a live-verified lookup (SW703, Fix round 2 §7); everything else is listed under "needs LCSC" above rather than guessed.
6. **VBUS_EMU bulk capacitance — cross-sheet integration item, not a bench_io defect** (Fix round 2 §5): this sheet's own C701 (10 µF) is within the USB 2.0 §7.2.4.1 downstream-device VBUS bypass limit (10 µF max) on its own, but `emulator_mcu` also fits 10 µF (C200) on the same `VBUS_EMU` net, plus a 100 nF (C201) — 20.1 µF combined. Recommend the integrator drop one of the two 10 µF caps (either C701 here or `emulator_mcu`'s C200) or explicitly accept the MLCC DC-bias-derated total in `integration_report.md`. No FC counter-precedent either way — the FC's own `VBUS` net carries no bulk cap at all.

No deviations from the brief's §6.6 spec beyond the `3V3_EMU` power-symbol-vs-global-label choice explained in §4 above (which is a format choice, not a functional one — same net, same pins, same ERC-clean result either way) and the BSS138-for-2N7002 substitution (Fix round §1 — brief §6.6 says "N-FET such as 2N7002", exemplary rather than mandatory; BSS138 keeps the brief's exact 1k/4.7k gate network unchanged and is pin-compatible).

## 10. Fix round (independent verifier, 7 findings)

All seven findings from the independent verifier were fixed in `tools/gen/bench_io_gen.py` and the sheet regenerated; the full validation loop (sch_lint, harness_erc against the six-sheet hierarchy, netlist diff, and a re-render/crop visual pass) was re-run after each structural change. Sections 2–9 above were updated in place to reflect the fixed design; this section records what changed and why.

### 1. [major] 2N7002 gate drive below datasheet threshold → swapped to BSS138

Confirmed the finding by fetching both datasheets. Diodes 2N7002 `DS11303 Rev 33-2`: V_GS(th) max 2.5 V, no on-state parameter specified near a 2.6–2.7 V drive. With the brief's own 1k/4.7k gate divider off a 3.3 V-class GPIO, V_GS at the gate is ≈2.72 V typical, ≈2.59 V at IOVDD −5% — leaving only 0.09–0.22 V of guaranteed overdrive on a worst-case 2N7002, i.e. not reliably above its own threshold-definition current (250 µA at V_GS=V_GS(th)).

Fixed by swapping Q701/Q702/Q703 from `Transistor_FET:2N7002` to `Transistor_FET:BSS138` (fetched from the KiCad 10 standard library via `tools/get_symbol.py`; pin geometry G/S/D = 1/2/3 is identical, so no footprint or wiring change was needed) instead of shrinking the gate series resistor — this keeps the brief's exact "1k series / 4.7k pulldown" text (§6.6) unchanged and, as a side benefit, keeps R705/R707/R709 at the same 1k value the as-ordered BOM prices (finding 2, below), rather than moving them off that BOM line. Fetched the onsemi/Fairchild BSS138 datasheet (`BSS138-D.PDF`) live and confirmed V_GS(th) = 0.8/1.3/1.5 V (min/typ/max) at V_DS=V_GS, I_D=1 mA: worst case (2.59 V delivered vs. 1.5 V max threshold) leaves ≥1.08 V of guaranteed overdrive, comfortably enhancing the FET well past its threshold region for the few-hundred-µA sink current these nets actually need (≈330 µA on FC_RESET, ≈245 µA on USBBOOT, both computed from the FC's own pull-ups in `tools/baseline/netlist.kicadxml`).

Corrected the Block E sheet note (previously: "2N7002 Vgs(th) well below the FC's own logic levels" — false, and it didn't account for the divider) to state the actual numbers, and added the two brief-required notes that were missing (finding 4, below) in the same pass. Updated Q701–Q703's Datasheet property from the stock onsemi NDS7002A URL (a different MPN, inherited from the KiCad symbol default, not something previously verified against) to the BSS138 datasheet actually fetched and cited. Corrected §7's datasheet-facts entry and this report's parts table/§5 accordingly.

### 2. [major] Missing LCSC numbers with an as-ordered BOM source

`refs/bom/BOM-proves_radio_stick_V2.csv` was re-checked and confirmed to carry all four values used in Block A/E at the same 0402 footprint: `5.1k,"R26,R27",R_0402_1005Metric,C25905,2`, `1k,"R10,R13,R80,R93",R_0402_1005Metric,C11702`, `4.7k,"R14,R15",R_0402_1005Metric,C25900`. Set `LCSC Part` = C25905 on R701/R702, C11702 on R705/R707/R709, C25900 on R706/R708/R710. Removed all six from the report's "Needs LCSC" list and cited the BOM file in the parts table's source column; deleted the contradictory §9 sentence that claimed no BOM source existed for "22R/5.1k-class resistors" while also listing R701/R702 as unsourced two lines above it.

### 3. [major] Wires drawn through symbol bodies (D+/D- through R701/R702; C701's GND through the CC1 wire)

Confirmed both instances by computing exact pin/wire coordinates from the generator's own transform and cross-checking against the verifier's evidence, then confirmed visually on 600 dpi crops before and after.

- **D+/D- reroute**: the two USB differential-pair wires used to run straight from J701's D+/D- tie points across to R703/R704, passing directly through R701's and R702's bodies and GND leads (both pulldowns sit in that x-range, at y up to 96.52/99.06). Rerouted each wire with a short jog off J701's pin column, a drop to a row below both pulldowns' lowest point (y=104.14 for D-, y=109.22 for D+, both on the 1.27mm grid, ≥5mm clear of R701/R702), then across to R703/R704 (which moved down to sit on those same rows). Re-verified with `sch_lint.py` (catches off-grid points and dangling pins — this reroute needed two iterations: the first grid-snap was fine, but the first drop point for the D- wire coincided with J701's SBU2 `no_connect` marker at the same coordinates, which `harness_erc.sh` caught as a `no_connect_connected` warning attributed to `/Bench IO/`; moved the jog off that x-coordinate and re-ran clean) and by re-rendering — no wire now crosses any symbol body.
- **C701 GND clearance**: C701's GND symbol was anchored close enough to the CC1 wire (y=78.74) that its triangle graphic reached the wire. Shortened the GND stub from y=76.2 to y=71.12 (≥7.6 mm clear of the CC1 wire, well past the ≥2.54 mm the finding asked for).

### 4. [minor] Missing brief-required sheet notes (A4 stepping; USBBOOT → D4 → R10 → BOOTSEL)

Added both to the Block E note, folded into the same edit as finding 1's correction: the A4 stepping corrects erratum E9 and the 4.7k pulldown is the A2-safe value (may be relaxed on A4 silicon); and USBBOOT reaches the FC's U18 BOOTSEL pin through D4 + R10 1k, the same path SW1 uses, so Q702 pulling USBBOOT low reproduces an SW1 press. Traced the path in `tools/baseline/netlist.kicadxml` (`USBBOOT = D4.1, J16.1, SW1.A/A'`; `Net-(D4-A) = D4.2, R10.2`; `BOOTSEL = R10.1, R91.1, U18.60`) before writing the note. §7 updated with the same citation.

### 5. [minor] SW703 generic DIP switch → project-standard SS12D10G4

Confirmed `refs/upgraded/debug_board_v1/debug_board_v1.kicad_sch` (SW3, line 6197) uses `easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4` for its own WDT-equivalent toggle, and that the footprint file exists on disk (`~/Documents/KiCad/easyeda2kicad/easyeda2kicad.pretty/SW-TH_SHOU-HAN_SS12D10G4.kicad_mod`). Switched SW703's footprint to that part and its Value to `SS12D10G4`, keeping `Switch:SW_SPST` (2 of the SPDT's 3 terminals are used, same as `debug_board_v1`'s own `SW_Push_SPDT` instance) rather than changing the symbol. Set the Datasheet property to the same LCSC-hosted PDF `debug_board_v1` cites. No LCSC number was available there either — `debug_board_v1`'s BOM is header-only (D3: never assembled) — so SW703 stays on the "needs LCSC" list, now with the MPN named. Updated §2 Block D and §9 item 4 accordingly.

### 6. [minor] Overlapping reference/value text at five places; ambiguous 22R labels

Re-rendered at 600 dpi after each change and visually confirmed each fix (crops saved under the session scratchpad, not committed). Root-caused why the *previous* attempt at this (the original §8 "Visual check" item 3) was wrong: for a symbol rotated 90°/270°, kicad-cli's plotter does not render a property's *stored* text angle literally — it combines it with the parent symbol's own rotation. Confirmed directly against the FC root sheet's own rendered SW1/SW2 (same footprint, same rot=270): Value "KMR2" (stored angle 0) renders **vertically** by design, Reference "SW1"/"SW2" (stored angle 90) renders horizontally. The original generator left EMU_RUN/EMU_BOOTSEL_SW's buttons and TP701 on stored-angle-0 defaults believing that would render horizontal after rotation; it does not, which is exactly what the verifier caught.

Fixed by adding an explicit per-property text-angle parameter to the generator's `add_symbol()`/`prop()` and using it:
- **J702, J703**: increased the default `ref_dy`/`val_dy` (±3.556 mm, smaller than either connector's own pin span) to ±7.62 mm, clearing the pin-number text and connector body.
- **SW701, SW702**: copied the FC's own SW1/SW2 Reference/Value offsets and angles verbatim (read from `FlatSat_V1.kicad_sch`) — Reference `dx=0, dy=6.35, angle=90`; Value `dx=-6.35, dy=-1.905, angle=0` (vertical, matching FC's accepted convention).
- **TP701**: gave both Reference and Value `angle=90` (both render horizontal) with `dx=-9.0` and a `dy=∓2.54` split, clearing C701 (whose own Reference/Value were also nudged `dx=+2.54`, away from TP701) by several mm in both axes.
- **R703, R704**: kept the existing `dx`-split pattern (unchanged from the original, already correct for rot=0 parts) but increased the vertical offsets so R703 (the lower of the pair, after the D+/D- reroute above) pushes south past the Block C/D header text row (y=111.76–113.3) and R704 pushes north — eliminating both the R703/R704 "which 22 is which" ambiguity and a new collision the reroute created between R703's label and the header text.
- **Block A's descriptive note**: relocated from directly under the D+/D- reroute (now contested by R703/R704's own labels and the Block C/D header row) to the open pocket above the CC network, right of TP701/C701 — confirmed clear on render.

### 7. [minor] Report inaccuracies

Fixed all four: corrected the #PWR range (line 44) to `#PWR701–#PWR709, #PWR711–#PWR718` (17 symbols; there is no #PWR710 or #PWR719) — recounted directly from the file. Reworded the Block A / §2 UFP sentence: the 5.1k CC pulldowns present the port as a UFP, so an *upstream* DFP sources `VBUS_EMU`, not the reverse. Deleted the §9 sentence contradicting the parts-table LCSC status (finding 2). Q701–Q703's Datasheet property now points at the BSS138 datasheet actually used and fetched (finding 1), not the stock NDS7002A URL inherited from the KiCad symbol default.

### Re-run validation (post-fix)

```
$ python3 tools/sch_lint.py bench_io.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/54b8f29e-9dcb-4e24-99b9-415a110b338a --refdes-block 700-799
bench_io.kicad_sch: 39 symbol instances, 12 lib symbols, 66 wires, 0 errors, 0 warnings
```
```
$ SCRATCH=<scratch>/work_bench_io/harness_run2 bash tools/harness_erc.sh "Bench IO"
=== violations on sheets matching 'Bench IO' ===
total 0
errors: 0
```
Project-wide delta (excluded from this sheet's own count): +5 power_pin_not_driven, +68 pin_to_pin, all attributed to `emulator_mcu`/`solar_emulation`/`battery_protection_replica` (the sheets other agents are concurrently building), -9 single_global_label (all `EMU_*` nets now matched now that `emulator_mcu` exists). Netlist diff re-checked — identical to §4/§6 above (component *values* changed, refdes and net connectivity did not). Full-page render re-reviewed at 200 dpi and each block re-cropped at 600 dpi; no remaining text/wire overlaps found.

## 11. Fix round 2 (independent verifier, 7 findings)

A second independent verifier reviewed the round-1 output and found 7 more findings (2 major, 5 minor) — two real geometry/part defects that survived round 1's own visual pass, one hidden-property inconsistency, one text/wire overlap round 1 missed on a part it had already touched, one cross-sheet integration item, and two report-only inaccuracies. All were fixed in `tools/gen/bench_io_gen.py` (`FlatSat_V1/tools/gen/bench_io_gen.py`) and the sheet regenerated; the full validation loop (sch_lint, harness_erc against the six-sheet hierarchy, netlist diff, and a fresh 300 dpi render with targeted crops) was re-run after all structural changes. Sections 2–9 above were updated in place; this section records what changed and why.

### 1. [major] GND (#PWR706) drawn on top of the EMU_SWDIO global label

Confirmed by computing J702 pin 2's global coordinate (58.42, 149.86) and the EMU_SWDIO label's anchor (48.26, 152.4) from the generator's own transform, then re-rendering at 300 dpi (`<scratch>/work_verify_bench_io_r2fix/swd.png`) — the original GND symbol at (45.72, 149.86) sat inside the label's text box, its stub wire terminating over the glyphs.

Considered the verifier's first suggested fix (jog the wire vertically to a GND at (48.26, 144.78)) but rejected it: that x (48.26) is exactly where the EMU_SWCLK label's own wire terminates (at (48.26, 147.32)), so a vertical run through that point would electrically tie GND to EMU_SWCLK — a real short, not just a visual one. Used the horizontal-only alternative instead: kept the wire at pin 2's row (y=149.86, between the SWCLK and SWDIO label rows) and moved #PWR706 out to x=30.48, well clear of both labels' text boxes (which run roughly x 37.6–48.3) in x alone, so the fix can't cross either label's wire regardless of the GND symbol's vertical extent. Re-rendered and confirmed clear (`swd.png`): GND now sits well left of both labels with visible daylight on both sides.

### 2. [major] SW703: 2-pin `Switch:SW_SPST` on a 3-pad SPDT footprint

Confirmed the footprint (`easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4.kicad_mod`) defines three thru-hole pads (1/2/3) and that `Switch:SW_SPST` has only two pins, leaving pad 3 with no schematic counterpart. Also confirmed `debug_board_v1`'s own SW3 (the reference this sheet's Block D note cited) uses the 3-pin `Switch:SW_Push_SPDT`, not a 2-pin symbol — round 1's claim of parity with that reference was wrong.

Fixed per the verifier's option (a): switched to the system library's `Switch:SW_SPDT` (fetched via a direct extract from `/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Switch.kicad_sym`, added to the pantry as `Switch_SW_SPDT.sexp`). Read the symbol geometry to confirm pin 2 ("B") is the wiper/common (the polyline that indicates the switch's moving contact runs from the circle at pin 2's node to pin 1's), matching the SS12D10G4 datasheet's own claim (center pad = common pole) — so the two map onto each other correctly with no pin renumbering needed. Wired pin 2 (common) → GND, pin 1 → `WDT_DISABLE`, and added an explicit `no_connect` on pin 3 (the unused throw) so nothing is left dangling. Added a sentence to the Block D sheet note stating which slider position grounds `WDT_DISABLE`. Also increased the symbol's default Reference/Value `dy` from ±3.556 to ±5.08: `SW_SPDT`'s body is a drawn rectangle (±3.81 mm) that `SW_SPST` didn't have, so the smaller default would have landed the text just inside the box. Re-rendered (`<scratch>/work_verify_bench_io_r2fix/sw703.png`) and confirmed all three pins present, pin 3 marked NC, text clear of the box.

### 3. [minor] VBUS_EMU power symbol's rail name hidden

Confirmed by grep: this was the only sheet in the project hiding a non-GND/non-PWR_FLAG power symbol's Value text (`FlatSat_V1.kicad_sch` 11/11 shown, `emulator_mcu.kicad_sch` 10/10, `battery_protection_replica.kicad_sch` 3/3). Traced to `hide_val=True` on the `#PWR702` (`flatsat:VBUS_EMU`) call. Flipped to `hide_val=False`; no coordinate change needed since the default `val_dy` offset already clears the sheet's title-block text (which the surrounding comment establishes stays at y≤43, well above this symbol's y=45.72+3.556). Re-rendered (`<scratch>/work_verify_bench_io_r2fix/vbus.png`) and confirmed "VBUS_EMU" now prints under the rail arrow, matching every other sheet's convention.

### 4. [minor] Q701/Q702/Q703 Reference/Value text struck through by their own drain/source wires

Confirmed: at `rot=0` with no `dx` offset, the default Reference/Value placement sits directly above/below the symbol origin — the same x-column the drain (up, to the FC net label) and source (down, to GND) leads run through vertically. Fixed by adding `ref_dx=-5.08, val_dx=5.08` to the shared `add_driver()` symbol call (the same style of fix `rpd`/R706-R708-R710 already used for their own 90°-rotated text, per the verifier's pointer), which moves both strings off the vertical-wire column entirely regardless of the existing `dy` split. Re-rendered (`<scratch>/work_verify_bench_io_r2fix/q70x.png`) and confirmed "Q701"/"BSS138" (and Q702/Q703's) now sit beside the wires, not through them.

### 5. [minor] VBUS_EMU carries 20.1 µF combined — cross-sheet integration item

Confirmed via the harness netlist: `VBUS_EMU` = C200.1 (10 µF, `emulator_mcu`), C201.1 (100 nF, `emulator_mcu`), C701.1 (10 µF, this sheet), plus the connector/test-point/IC pins. This sheet's own C701 alone is within the USB 2.0 §7.2.4.1 10 µF downstream-device bypass limit; the excess only exists because `emulator_mcu` also fits 10 µF on the same rail. As the verifier noted, this isn't a bench_io-only defect — no schematic change made here. Recorded as an explicit integration item in §9 (new item 6) for the integrator to resolve (drop one of the two 10 µF caps, or accept the derated total in writing).

### 6. [minor] Report stated the FC's D4 polarity backwards

`tools/baseline/netlist.kicadxml` shows `USBBOOT` on D4 pin 1 (`pinfunction "K_1"`, i.e. cathode) and `Net-(D4-A)` (D4's anode, pin 2, `pinfunction "A_2"`) feeding R10 — the opposite of what §7 said. Corrected the sentence in §7 (this sheet's own Block E note never stated a polarity and needed no change). Confirmed no other report section repeated the error.

### 7. [minor] SW703's LCSC number was available and unclaimed

SW703's own Datasheet property (`https://.../2108201830_SHOU-HAN-SS12D10G4-071_C2887259.pdf`, carried over from `debug_board_v1`) already embeds LCSC part C2887259 in its filename. Checked it live: the part (SHOU HAN SS12D10G4-071, SPDT slide switch) is in stock on both lcsc.com and jlcpcb.com as of this check. Set SW703's `LCSC Part` = C2887259 (rule 5 permits a live-verified number) and updated the parts table / §9 item 4 accordingly.

### Re-run validation (post-fix-round-2)

```
$ python3 tools/gen/bench_io_gen.py
wrote FlatSat_V1/bench_io.kicad_sch (4714 lines)
```
```
$ python3 tools/sch_lint.py bench_io.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/54b8f29e-9dcb-4e24-99b9-415a110b338a --refdes-block 700-799
bench_io.kicad_sch: 39 symbol instances, 12 lib symbols, 66 wires, 0 errors, 0 warnings
```
```
$ SCRATCH=<scratch>/work_verify_bench_io_r2fix bash tools/harness_erc.sh "Bench IO"
=== ERC delta vs baseline (Rev2 + 8 promotions; noise excluded) ===
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

=== violations on sheets matching 'Bench IO' ===
total 0
errors: 0
```
```
$ python3 tools/erc_summary.py <scratch>/work_verify_bench_io_r2fix/erc.json --sheet "Bench IO"
total 0
errors: 0
```
Identical project-wide delta to round 1 (all of it attributed to the concurrently-built `emulator_mcu`/`solar_emulation`/`battery_protection_replica` sheets, none to `/Bench IO/`) — none of round 2's fixes changed this sheet's ERC footprint, only its geometry, one part's symbol/pin count, and a hidden-property flag. Netlist diff re-checked: `WDT_DISABLE` now gains `SW703.1` specifically (pin 2/common moved to the `GND`-net pin list, pin 3 dropped from any net as an explicit NC) instead of the old `SW703.1`/`SW703.2` pairing off a 2-pin symbol — connectivity intent unchanged (`WDT_DISABLE`↔`GND` through the switch), only the pin-level bookkeeping is now footprint-accurate. Full-page render re-reviewed at 300 dpi (`<scratch>/work_verify_bench_io_r2fix/full_thumb.png`) and all four fixed areas re-cropped individually (`swd.png`, `sw703.png`, `q70x.png`, `vbus.png`) — no remaining overlaps found, all match the descriptions above.
## 12. Review fixes (Fable review-and-fix round, 2026-09-14)

Ids applied: **11**.

### 11. [minor] No bench-operator warning at the emulator USB connector (fix-now)

The reviewer's companion item to the phantom-power note on `emulator_mcu`: the note explaining
the hazard lived on the emulator sheet, but the physical connector an operator plugs and unplugs
is `J701` on this sheet, so the rule was not where it would be read.

Added one bench-rule note on the sheet, at `(112, 74)`, size 1.27 mm (deliberately larger than the
1.0 mm explanatory notes so it reads as an operating rule, not commentary), in the empty pocket
directly right of the `J701` pin column and below the existing Block A note:

```
BENCH RULE: Connect emulator USB (J701) before or together with FC power;
do not leave FC powered with the emulator unplugged (3V3_EMU can float
to an undefined partial-power state).
```

Placement clearances: the Block A note above ends near y=70.5; the CC pulldown network
(`R701`/`R702` bodies, their GND leads and value text) stops at x<=110; the D-/D+ reroute is at
y=104.14/109.22; the `VBUS_EMU` rail and `TP701`/`C701`/`#FLG701` sit at x=78.74-93.98. Nothing
else occupies x 112-185, y 74-80.

Applied to both `bench_io.kicad_sch` (single `(text ...)` element inserted after the Block A note,
new uuid `d20af317-d57d-4588-bca7-dd612b77e0ca`, written tmp+rename) and
`tools/gen/bench_io_gen.py` (matching `add_text(...)` call after the Block A note, with the
placement reasoning as a comment). Re-running the generator into a scratch target and diffing
against the on-disk sheet with uuids normalised gives a zero-line diff, so a regeneration
reproduces the sheet exactly.

Text-only change: no symbol, pin, wire, label or junction was touched, so the netlist and ERC
footprint are unchanged (verified below).

### Re-run validation (post-review-fix)

```
$ python3 tools/sch_lint.py bench_io.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/54b8f29e-9dcb-4e24-99b9-415a110b338a \
    --refdes-block 700-799
bench_io.kicad_sch: 39 symbol instances, 12 lib symbols, 66 wires, 0 errors, 0 warnings
```
```
$ SCRATCH=<scratch>/review_fix_bench_io tools/harness_erc.sh
=== ERC delta vs baseline (default: Rev2 + 8 promotions; noise types excluded) ===
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

=== violations on 'Bench IO' ===
total 0
errors: 0

=== netlist diff vs baseline ===
components: base 261, new 477, added 216, removed 0
nets: base 215, new 355
```

Eleven project-wide errors, all on FC sheets and byte-identical to the Rev2 baseline; zero
violations on `/Bench IO/`; component and net counts unchanged from the pre-fix capture (216
added, 0 removed), as expected for a text-only edit. Page re-exported
(`kicad-cli sch export pdf bench_io.kicad_sch`) and read at full page plus a 400 dpi crop of the
note area: the bench rule renders clear of `C701`, `R701`/`R702`, their value text and the
`EMU_USB_DM` row, and is legible at page scale.
