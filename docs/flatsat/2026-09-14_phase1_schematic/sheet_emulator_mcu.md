# Sheet report — `emulator_mcu` ("Emulator MCU", page 7)

**PROVES FlatSat V1 · Phase 1 schematic capture · 2026-09-14**
Spec: `00_pm_brief.md` (rev 2) §6.1, interface contract §4, format/validation §7, deliverables §8.
Critique `01_brief_critique.md` items 4, 5, 7, 9, 11, 14, 21 all land on this sheet and are implemented as the brief states.

| | |
|---|---|
| Sheet file | `/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/emulator_mcu.kicad_sch` |
| Generator | `/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/tools/gen/emulator_mcu_gen.py` |
| Sheet symbol uuid | `8394a2ec-8c1e-41a1-b086-be3289cedfbc` (page 7, root placement 33.02, 154.94) |
| Instances path | `/c64c0d72-a9f6-4f3a-891e-1f647558f538/8394a2ec-8c1e-41a1-b086-be3289cedfbc`, project `FlatSat_V1` |
| Refdes block | 200–299 (used: C200–C222, D200–D202, L200, R200–R211, TP200–TP203, U200–U202, Y200 = 47 parts; plus #PWR200–#PWR243 and #FLG200–#FLG201 = 46 power symbols. 93 instances, all inside the block.) |
| Paper | A3, no `(sheet_instances …)`, no trailing `(embedded_fonts no)` — matches `load_switches.kicad_sch` |

---

## 1. Purpose

A second RP2350A ("the emulator") on its **own** USB-C supply, sharing only GND with the flight
controller. It answers as the I2C slave for solar faces 1–5, the battery pack's four TMP112s and the
antenna top-cap sensor pair, behind the same TCA4311A hot-swap buffers the real boards use
(sheet *Solar and Sensor Emulation*), and it gives the bench scripted control of the FC's
reset / boot / watchdog lines through the open-drain FETs on sheet *Bench IO*.

This sheet carries **only the MCU core**: the RP2350A, its boot flash, crystal, core-regulator
passives, its 3.3 V LDO, the RUN/BOOTSEL arrangement, two LEDs, the RP2350-E9 default-state pulls
that belong on this sheet, and four bench test points. Every connection to the FC leaves through a
global label to another new sheet — nothing on this sheet touches an FC net except `GND`.

## 2. Blocks

| Block | Contents |
|---|---|
| Emulator power (top left) | `VBUS_EMU` → U202 AP2112K-3.3 (EN tied to VIN) → `3V3_EMU`; C200/C201 in, C202/C203 out; TP200, TP201; D201 power LED with R211. U202 pin 4 (NC) carries a `no_connect`. **C200 is 1 µF, not 10 µF** — changed by the integrator, see §12. |
| 3V3_EMU decoupling (top middle) | Nine 100 nF (C204–C212), one 4.7 µF (C213) and one 10 µF (C214) on a two-row rail that feeds the RP2350A's six IOVDD pins, QSPI_IOVDD, USB_OTP_VDD and ADC_AVDD. Mirrors the FC's C71–C78 + C65 + C75. |
| VREG_AVDD filter (left) | R200 33 Ω from `3V3_EMU` + C215 4.7 µF to GND — the FC R94/C68 arrangement. PWR_FLAG here (§4.2). |
| Core buck (left) | VREG_LX → L200 3.3 µH → `1V1_EMU`; C216/C217 4.7 µF + C218/C219 100 nF; VREG_FB tied back to `1V1_EMU`; TP202; PWR_FLAG. FC L3/C66/C67/C69/C70 parity. |
| QSPI flash (left) | U201 W25Q128JVS on QSPI_SD0–3/SCLK, `~CS` = `EMU_FLASH_SS`; C220 decoupling on its own `3V3_EMU`/GND island. |
| Crystal (bottom left) | Y200 ABM8-272-T3 12 MHz, C221/C222 15 pF, R201 1 k in the XOUT leg (FC Y1/C63/C64/R93 parity). |
| RUN / BOOTSEL (bottom left) | R205 10 k pull-up → `EMU_RUN`; `EMU_QSPI_SS` — R203 0 Ω — `EMU_FLASH_SS` (R202 10 k pull-up); `EMU_QSPI_SS` — R204 1 k — D200 NSR0320 (anode at R204, cathode at the button) → `EMU_BOOTSEL_SW`. Exactly the FC's R91/R2/R10/D4/SW1 topology, renamed. |
| Status LED and E9 pulls (right) | D202 + R206 on GPIO19; R207 4.7 k pull-up on `EMU_UART_RX`; R208/R209 4.7 k pull-downs on `EMU_GPIO_SPARE0/1`; R210 4.7 k pull-down and TP203 on `EMU_GPIO_RSVD`. |

## 3. Parts

Every LCSC number below except U202's comes from an **as-ordered** JLC BOM in the repos
(`FC_V5e_Production_Rev2/jlcpcb/production_files/BOM-FC_V5e_Production_Rev2.csv` = "FC", and
`<scratch>/refs/bom/BOM-proves_radio_stick_V2.csv` = "stick"), per brief rule 5.

| Ref | Value | Footprint | LCSC | Source of the number |
|---|---|---|---|---|
| U200 | RP2350A | `RP2350_60QFN_minimal:RP2350-QFN-60-1EP_7x7_P0.4mm_EP3.4x3.4mm_ThermalVias` | C42411118 | FC (U18), stick |
| U201 | W25Q128JVS | `Package_SO:SOIC-8_5.3x5.3mm_P1.27mm` | C97521 | stick (U11) |
| U202 | AP2112K-3.3 | `Package_TO_SOT_SMD:SOT-23-5` | C51118 | **verified live** at `lcsc.com/product-detail/C51118.html` (Diodes AP2112K-3.3TRG1, SOT-23-5, 600 mA) — not in any repo BOM |
| Y200 | ABM8-272-T3 | `Crystal:Crystal_SMD_3225-4Pin_3.2x2.5mm` | C20625731 | FC (Y1), stick |
| L200 | 3.3u | `RP2350_60QFN_minimal:L_pol_2016` | C42411119 | FC (L3), stick |
| D200 | NSR0320 | `Diode_SMD:D_SOD-323F` | C48192 | FC (D4), stick |
| D201, D202 | LED | `LED_SMD:LED_0603_1608Metric` | C2290 | FC (D1/D2/D3), stick |
| R200 | 33 | `Resistor_SMD:R_0402_1005Metric` | C25105 | FC (R94) |
| R201, R204, R206, R211 | 1k | `Resistor_SMD:R_0402_1005Metric` | C11702 | FC (R93) |
| R202, R205 | 10k | `Resistor_SMD:R_0402_1005Metric` | C25744 | FC (R2/R37) |
| R203 | 0 | `Resistor_SMD:R_0402_1005Metric` | C17168 | FC (R91) |
| R207–R210 | 4.7k | `Resistor_SMD:R_0402_1005Metric` | C25900 | FC (R100/R103/R104/…) |
| C200 | 1uF | `Capacitor_SMD:C_0603_1608Metric` | C15849 | as-ordered `BOM-FC_V5e_Production_Rev2.csv` (`1uF,"C37,C4,C41",C_0603_1608Metric,C15849,3`). Was `10uF`/`C19702`; retuned by the integrator for the cross-sheet `VBUS_EMU` bulk-capacitance limit — see §12 |
| C202 | 10uF | `Capacitor_SMD:C_0603_1608Metric` | C19702 | FC (C1/C14/…) |
| C214 | 10uF | `Capacitor_SMD:C_0805_2012Metric` | C15850 | FC (C75) |
| C201, C203, C204–C212, C218–C220 | 100nF | `Capacitor_SMD:C_0402_1005Metric` | C1525 | FC (C71–C78) |
| C213, C215, C216, C217 | 4.7uF | `RP2350_60QFN_minimal:C_0402_1005Metric_small_pads` | C23733 | FC (C65/C66/C68/C69) |
| C221, C222 | 15pF | `Capacitor_SMD:C_0402_1005Metric` | C1548 | FC (C63/C64) |
| TP200–TP203 | TestPoint | `TestPoint:TestPoint_Pad_D1.5mm` | — | pad only, no part |

**Needs LCSC:** none outstanding. U202 AP2112K-3.3 (C51118) is the only line not backed by a repo
BOM; it was verified live, so it is carried on the symbol per rule 5. If the integrator prefers a
strictly repo-sourced regulator, the alternative is noted in §6.

## 4. Interface nets

### 4.1 Existing FC nets used

`GND` only — 34 pins added (all decoupling/return pins plus U200 pins 47 and 61 and U201 pin 4).
**No `+3V3` power symbol and no `+3V3` label appears anywhere on this sheet** (brief §6.1), and no
FC global label survived from the `RP2350.kicad_sch` template (hard rule 8, verified by a name scan —
see §7.4).

### 4.2 New cross-sheet nets **defined** by this sheet

| Net | Kind | Where it goes |
|---|---|---|
| `3V3_EMU` | power symbol `flatsat:3V3_EMU` + one global label on U200 VREG_VIN | consumed by `bench_io` (J703.1) and `pyro_inhibit` (R600, R602) |
| `EMU_CTL_FC_RESET` / `EMU_CTL_USBBOOT` / `EMU_CTL_WDT_DIS` | global, output | `bench_io` R705 / R707 / R709 (1 k into the 2N7002 gates) |
| `EMU_RUN` | global, output (R205 10 k pull-up to `3V3_EMU`) | `bench_io` SW701 to GND |
| `EMU_BOOTSEL_SW` | global, output (D200 cathode) | `bench_io` SW702 to GND |
| `EMU_UART_TX` | global, output | `bench_io` J703.3 |
| `EMU_UART_RX` | global, input (R207 4.7 k pull-up here) | `bench_io` J703.4 |
| `EMU_GPIO_SPARE0` / `EMU_GPIO_SPARE1` | global (R208/R209 4.7 k pull-downs here) | `bench_io` J703.5 / J703.6 |

### 4.3 New cross-sheet nets **consumed** by this sheet

`VBUS_EMU` (from `bench_io` USB-C J701; PWR_FLAG lives there, not here) ·
`EMU_F1_SDA/SCL` … `EMU_F5_SDA/SCL`, `EMU_BATT_SDA/SCL`, `EMU_TOP_SDA/SCL` (14 lines, TCA4311A
device sides U310–U316 on `solar_emulation`) · `EMU_F1_SENSE` … `EMU_F5_SENSE`, `EMU_FC3V3_SENSE`
(4.7 k series taps R314/R324/R334/R344/R354/R374 on `solar_emulation`) · `PYRO_INHIBIT_STATE`
(4.7 k tap R601 on `pyro_inhibit`) · `EMU_USB_DP` / `EMU_USB_DM` (22 Ω R703/R704 on `bench_io`) ·
`EMU_SWCLK` / `EMU_SWDIO` (JST-SH J702 on `bench_io`).

### 4.4 Sheet-local nets

`1V1_EMU`, `VREG_AVDD_EMU`, `EMU_VREG_LX`, `EMU_QSPI_SS`, `EMU_FLASH_SS`, `EMU_QSPI_SD0…SD3`,
`EMU_QSPI_SCLK`, `EMU_XIN`, `EMU_XOUT`, `EMU_STATUS_LED`, `EMU_GPIO_RSVD`
(+ auto-named `Net-(C222-Pad1)` for the crystal XOUT node and `Net-(D200-A)` / `Net-(D201-A)` /
`Net-(D202-A)`).

### 4.5 PWR_FLAG ownership (brief §4.2)

* `1V1_EMU` → #FLG on this sheet (otherwise the FC baseline's `power_pin_not_driven` on U18 DVDD recurs on U200).
* `VREG_AVDD_EMU` → #FLG on this sheet (same reason, U18 VREG_AVDD).
* `3V3_EMU` → **no** PWR_FLAG: U202 pin 5 VOUT is already `power_out`, so a flag would be a second power output on the net (an ERC error).
* `VBUS_EMU` → **no** PWR_FLAG here; it belongs to `bench_io`.
* Nothing on `GND`.

Confirmed by ERC: the baseline's two RP2350 `power_pin_not_driven` errors do **not** reappear for U200.

## 5. GPIO map — firmware contract

RP2350A (QFN-60) has 30 GPIO. Budget: 14 I2C + 7 read lines + 3 control outputs + 2 UART +
2 spare + 1 status LED = 29; GPIO25 is the reserved 30th.

| GPIO | Pin | Net | Direction / drive | Note |
|---|---|---|---|---|
| GPIO0 / GPIO1 | 2 / 3 | `EMU_F1_SDA` / `EMU_F1_SCL` | open-drain only | face 1, TCA9548 ch1, PIO0 SM0 |
| GPIO2 / GPIO3 | 4 / 5 | `EMU_F2_SDA` / `EMU_F2_SCL` | open-drain only | face 2, ch2, PIO0 SM1 |
| GPIO4 / GPIO5 | 7 / 8 | `EMU_F3_SDA` / `EMU_F3_SCL` | open-drain only | face 3, ch3, PIO0 SM2 |
| GPIO6 / GPIO7 | 9 / 10 | `EMU_F4_SDA` / `EMU_F4_SCL` | open-drain only | face 4, ch5, PIO0 SM3 |
| GPIO8 / GPIO9 | 12 / 13 | `EMU_F5_SDA` / `EMU_F5_SCL` | open-drain only | face 5, ch6, PIO1 SM0 |
| GPIO10 / GPIO11 | 14 / 15 | `EMU_BATT_SDA` / `EMU_BATT_SCL` | open-drain only | pack TMP112 ×4, ch4, PIO1 SM1 |
| GPIO12 / GPIO13 | 16 / 17 | `EMU_TOP_SDA` / `EMU_TOP_SCL` | open-drain only | top cap VEML6031 + TMP112, ch7, PIO1 SM2 |
| GPIO14 | 18 | `EMU_CTL_FC_RESET` | output, default low | 4.7 k gate pull-down on `bench_io` |
| GPIO15 | 19 | `EMU_CTL_USBBOOT` | output, default low | 4.7 k gate pull-down on `bench_io` |
| GPIO16 | 27 | `EMU_UART_TX` | output | UART0 TX function |
| GPIO17 | 28 | `EMU_UART_RX` | input | UART0 RX function; R207 4.7 k pull-up here |
| GPIO18 | 29 | `EMU_CTL_WDT_DIS` | output, default low | 4.7 k gate pull-down on `bench_io` |
| GPIO19 | 31 | `EMU_STATUS_LED` | output | R206 1 k → D202, ~1.3 mA |
| GPIO20 | 32 | `EMU_GPIO_SPARE0` | either | R208 4.7 k pull-down here; bench header |
| GPIO21 | 33 | `EMU_GPIO_SPARE1` | either | R209 4.7 k pull-down here; bench header |
| GPIO22 | 34 | `EMU_FC3V3_SENSE` | input | 4.7 k from FC `+3V3` on `solar_emulation` |
| GPIO23 | 35 | `PYRO_INHIBIT_STATE` | input | 4.7 k from `PYRO_INH_COM` on `pyro_inhibit`; low = inhibited |
| GPIO24 | 36 | `EMU_F5_SENSE` | input | 4.7 k from `F5_PWR` |
| GPIO25 | 37 | `EMU_GPIO_RSVD` | reserved | TP203 only; R210 4.7 k pull-down |
| GPIO26 (ADC0) | 40 | `EMU_F1_SENSE` | input | 4.7 k from `F1_PWR` |
| GPIO27 (ADC1) | 41 | `EMU_F2_SENSE` | input | 4.7 k from `F2_PWR` |
| GPIO28 (ADC2) | 42 | `EMU_F3_SENSE` | input | 4.7 k from `F3_PWR` |
| GPIO29 (ADC3) | 43 | `EMU_F4_SENSE` | input | 4.7 k from `F4_PWR` |

Non-GPIO: pin 21/22 XIN/XOUT (Y200), 24/25 SWCLK/SWD (`EMU_SWCLK`/`EMU_SWDIO`), 26 RUN (`EMU_RUN`),
51/52 USB_DM/USB_DP (`EMU_USB_DM`/`EMU_USB_DP`, direct — the 22 Ω lives on `bench_io`),
55–60 QSPI (U201), 46–50 core regulator, 61 + EP GND.

**PIO budget.** Seven I2C-slave channels, one state machine each → 7 of the 12 state machines
(3 PIO blocks × 4). Each channel's SDA/SCL are on **adjacent** GPIOs so one `in`/`set` pin group
covers both, and the four face channels sit in GPIO0–7 so a single PIO block can serve them without
a GPIO-base change. GPIO26–29 (ADC-capable) carry four of the six face/rail sense taps, leaving the
door open for analogue rail monitoring in Phase 2.

**Firmware rules (also printed as text notes on the sheet):**

1. Every `EMU_*_SDA` / `EMU_*_SCL` GPIO is **open-drain only** — never driven high. A push-pull high
   while `Fn_PWR` is off would source ~0.70 mA per line into the dead face rail through the two 4.7 k
   device-side pull-ups, back-powering the AP22653 output and the TCA4311A VCC.
   (3.3 V / 4.7 kΩ = 0.70 mA; was 0.33 mA at the pre-R7 10 k.)
2. With a face off, those two pads see 4.7 k to 0 V, which **already meets** the 8.2 k RP2350-E9
   limit in hardware — that is what PM ruling **R7** bought. Keeping that channel's input buffers
   disabled while `EMU_Fn_SENSE` reads low is now belt-and-braces, not a requirement. (See §8 open
   question 1, closed by R7.)
3. `EMU_CTL_*` are outputs held low by default; the 4.7 k gate pull-downs on `bench_io` keep the FETs
   off while the emulator is unprogrammed, in BOOTSEL, or unpowered.

### 5.1 FC face ↔ TCA9548 channel ↔ flight-software name crosswalk

The FlatSat schematic names every channel after the **FC** net (brief §4), but the flight software names
the same channels `faceN` with an index that is *not* the FC face number for F4/F5, because TCA9548
channel 4 is the battery. Nothing in the FlatSat documentation recorded that until this table, so a
Phase-3 engineer building emulation profiles by name could load the wrong device set onto a channel.

Validated against **`proves-core-reference` commit `8e4d487a2a0056dd7d374c86ae47e8443a1c0fd1`**
(2026-08-30), files `boards/bronco_space/proves_flight_control_board_v5/proves_flight_control_board_v5.dtsi`
and `PROVESFlightControllerReference/ReferenceDeployment/Top/ReferenceDeploymentTopology.cpp`.

| FlatSat net (this sheet) | FC face / net | TCA9548 U3 ch | Zephyr dts node | Devices on the channel | Evidence |
|---|---|---|---|---|---|
| — (not emulated) | `F0_*` | ch0 | `mux_channel_0` / `face0_*` | TMP112 `0x48`, VEML6031 `0x29`, DRV2605L `0x5a` | dtsi 210–243 |
| `EMU_F1_SDA/SCL` | `F1_*` | ch1 | `mux_channel_1` / `face1_*` | TMP112 `0x48`, VEML6031 `0x29`, DRV2605L `0x5a` | dtsi 245–278 |
| `EMU_F2_SDA/SCL` | `F2_*` | ch2 | `mux_channel_2` / `face2_*` | same three | dtsi 280–313 |
| `EMU_F3_SDA/SCL` | `F3_*` | ch3 | `mux_channel_3` / `face3_*` | same three | dtsi 315–348 |
| `EMU_BATT_SDA/SCL` | `BATT_SDA/SCL` | ch4 | `mux_channel_4` / `batt_cell1..4_temp_sens` | TMP112 ×4 at `0x48` `0x49` `0x4a` `0x4b` | dtsi 351–383 |
| `EMU_F4_SDA/SCL` | `F4_*` | **ch5** | `mux_channel_5` / **`face5_*`** | TMP112 `0x48`, VEML6031 `0x29`, DRV2605L `0x5a`; dtsi comment `// Z- Face x1` | dtsi 386–419 |
| `EMU_F5_SDA/SCL` | `F5_*` | **ch6** | `mux_channel_6` / **`face6_*`** | dts declares all three; **only the VEML6031 `0x29` is instantiated** in the current topology | dtsi 422–455; Topology.cpp 158–182 |
| `EMU_TOP_SDA/SCL` | `SDA_Top` / `SCL_Top` | ch7 | `mux_channel_7` / `face7_light_sens` | VEML6031 `0x29` only in the dts; the **real top cap also carries a TMP112 at `0x48`** | dtsi 458–470; `antenna_top_cap_v2c` U4 |

**Rule of thumb.** Firmware `faceN` = FC face N for F0–F3; **+1** for F4 and F5 (ch4 is the battery).
Brief §4 states the same channel mapping from the FC side ("ch0..3 = F0..F3, ch5 = F4, ch6 = F5").

Three facts a Phase-3 profile author needs and cannot get from the net names:

* **`EMU_F4` (ch5 / `face5`) is the detumble Z− face.** `DetumbleManager.fpp` line 110 sets
  `param Z_MINUS_RESISTANCE: F64 default 150.7 id 30` with `Z_MINUS_SHAPE = CIRCULAR`,
  `Z_MINUS_DIAMETER = 0.05755` — the coil model the emulated DRV2605L on that channel sits behind.
  (The `sdd.md` line 465 rendering of that number as "150.7 mΩ" is a units typo: 3.3 V / 150.7 Ω =
  21.9 mA is the plausible magnetorquer current, 3.3 V / 150.7 mΩ = 21.9 A is not.)
* **ch6 / `face6` answers for the VEML6031 only** in the current topology — there is no
  `tmp112Face6Manager` and no `drv2605Face6Manager` in `ReferenceDeploymentTopology.cpp`. An emulation
  profile that answers at `0x48`/`0x5a` on `EMU_F5` will simply never be polled today, but it must not
  *fail* to answer if firmware adds those managers.
* **The ch7 dts TODO is stale.** `mux_channel_7` carries the comment `// TODO add top cap temp sensor
  (it's not a TMP112)`, but `antenna_top_cap_v2c` fits **U4 = TMP112xxDRL** with `ADD0` (pin 4) tied to
  `GND` → address **`0x48`** (netlist export of `antenna_top_cap_v2c.kicad_sch`; U3 on that board is the
  VEML6031X00 and U6 the TCA4311ADGKR). `EMU_TOP` must therefore emulate **both** devices, which is what
  the GPIO map in §5 and the sheet note already say.

**Observation for the firmware team (not a FlatSat finding).** In `ReferenceDeploymentTopology.cpp`
lines 178–182 every `drv2605FaceNManager.configure(...)` passes `state.muxChannel0Device`, including
`drv2605Face5Manager`. If that is not intentional, the DRV2605L traffic firmware believes it is sending
to face 1/2/3/5 actually lands on channel 0, and the FlatSat emulator on `EMU_F1..F4` would never see
it. Worth confirming before Phase 3 writes the DRV2605L emulation profile; no FlatSat hardware change
either way.

## 6. Design decisions, with the numbers

### 6.1 Regulator: AP2112K-3.3 LDO, not the radio-stick buck (D7, critique item 11)

Worst case on `3V3_EMU`:

| Load | Current |
|---|---|
| RP2350A core + I/O, full PIO and USB activity | ~100 mA |
| U201 W25Q128JVS read burst | ~25 mA |
| D201 power LED + D202 status LED (1 k each, ~1.3 mA) | ~2.6 mA |
| R207–R210 E9 pulls + bench-header spare-GPIO loads | ~5 mA |
| **total** | **~135 mA** |

The seven TCA4311A buffers are powered from FC rails (`F1_PWR`…`F5_PWR` and FC `+3V3`) per D7 and
§6.2, so they are **not** in this budget — the critique's item 11 correction. At 135 mA the
AP2112K-3.3 (600 mA, dropout 320 mV @ 600 mA) has 4.4× headroom and dissipates
(5.0 − 3.3) × 0.135 = **0.23 W** in SOT-23-5. The radio stick's TPS62085 + XFL4015 buck would give
heritage with `proves_radio_stick_V2` but costs four more parts and puts a 1.5 MHz switcher next to
the emulated I2C lines on a bench board whose whole point is clean I2C timing; the LDO is the
better trade here. If the hardware lead prefers repo-sourced parts only, swapping to
TPS62085RLTT (C2070694) + XFL4015-471MEC (C18221164) is a drop-in change to this block.

### 6.2 RP2350-E9 (critique items 4, 5, 21)

RP2350 datasheet Appendix E, erratum RP2350-E9 (A2 silicon): a GPIO configured as an input with the
input buffer enabled leaks up to 120 µA and floats to ≈2 V unless the external pull is ≤ 8.2 kΩ;
fixed in the A4 stepping. Every emulator GPIO that is an input, is read before firmware configures
it, or whose default state matters to the FC therefore has a 4.7 kΩ external pull:

* `EMU_F1..F5_SENSE`, `EMU_FC3V3_SENSE` — 4.7 k series resistors on `solar_emulation`;
* `PYRO_INHIBIT_STATE` — 4.7 k series resistor on `pyro_inhibit`;
* `EMU_CTL_FC_RESET` / `_USBBOOT` / `_WDT_DIS` — 4.7 k gate pull-downs on `bench_io`;
* `EMU_UART_RX` (R207, pull-up), `EMU_GPIO_SPARE0/1` (R208/R209, pull-down),
  `EMU_GPIO_RSVD` (R210, pull-down) — **on this sheet**.

R207–R210 are the four pulls the brief left to this sheet: `EMU_UART_RX` is a genuine input with
nothing on it until a bench cable is plugged in, and the two spares plus the reserved GPIO would
otherwise be the only floating pads on the emulator. SWCLK/SWD are not GPIO-bank pads and use the
RP2350's internal debug-port pulls, exactly as the FC does (no external pulls on U18 pins 24/25).

### 6.3 Phantom power into `3V3_EMU` (critique item 14; corrected after review)

**The current.** With the FC powered and the emulator unpowered, the 14 device-side pull-ups on
`solar_emulation` — **4.7 k after PM ruling R7**, not the 10 k this section originally assumed — feed
up to (3.3 − 0.7)/4.7 k ≈ **0.55 mA per line, ~7.7 mA across the 14 lines**, into `3V3_EMU` through
the RP2350's I/O ESD diodes. The `pyro_inhibit` STATE tap adds a negligible amount. Nothing is added
in series to block this (brief hard rule 6 and the "no series parts" intent). 0.55 mA/line and
7.7 mA are **upper bounds**, taken with the rail held at 0 V; the settled current is lower because
the rail floats up (below).

**The mechanism — this section was wrong.** The original text said "U202's output stage … sink[s] it".
It does not. U202 is an **AP2112K-3.3**, and its only output sink is the *auto-discharge* FET, which
the datasheet Electrical Characteristics table specifies as `VOUT Discharge Resistor R_DCHG = 60 Ω`
**under the condition "Set EN pin at Low"** (Diodes AP2112, the `DS_LDO` link on the sheet symbol;
the same row appears in the table for every voltage option). On this sheet **EN is tied to VIN**
(`emulator_mcu_gen.py` `build_power()`: `s.wire((66.04, yr), (66.04, u['3'][1]))`, "EN tied to VIN",
and the netlist shows `VBUS_EMU: … U202.1, U202.3`). With the emulator unplugged `VBUS_EMU` is absent,
so EN is not "low with the part alive" — the discharge FET is not held on, and the LDO's pass element
back-feeds its own input instead of pulling `VOUT` down. **The bulk capacitance does not sink it
either**: C202/C214 etc. are a one-shot charge, not a DC load.

**What actually happens.** `3V3_EMU` floats up until the injection equals the only real DC load on it,
the power-LED leg (R211 1 k + D201). The ceiling is one ESD-diode drop below the face rails,
**≈ 2.6 V**; solving 14 × (2.6 − V)/4.7 k = (V − V_f)/1 k with a 1.8–2.0 V red-LED V_f puts the settled
rail at **≈ 2.4 V**. Either way the RP2350A sits **partially powered with its I/O state undefined** —
its supplies are out of spec (VREG_VIN and IOVDD both sit on this rail, and the 1V1 core rail
follows it down), so the old text's "nothing is powered" does not hold.

**Consequence — bench rule, now printed on the sheet.**
**Connect the emulator's USB before or together with FC power, and never leave the FC powered with the
emulator unplugged.** This is an operating rule, not a hardware guarantee: brief hard rule 6 (no series
parts on the emulated I2C lines) is why no blocking element was added, and R7 raised the current
rather than lowering it.

### 6.4 FC parity items kept deliberately

* QSPI_SS ↔ FLASH_SS through a **0 Ω** (R203) with a 10 k pull-up (R202) on FLASH_SS, and
  QSPI_SS → 1 k (R204) → Schottky (D200, cathode at the button) → `EMU_BOOTSEL_SW`. That is the FC's
  R91 / R2 / R10 / D4 / SW1 arrangement pin for pin, so the emulator enters USB boot the same way
  the FC does and the button can never pull QSPI_SS high.
* 33 Ω + 4.7 µF on VREG_AVDD (FC R94/C68), 3.3 µH + 2×4.7 µF + 2×100 nF on the core rail
  (FC L3/C66/C67/C69/C70), 12 MHz ABM8-272-T3 with 2×15 pF and a 1 k in the XOUT leg
  (FC Y1/C63/C64/R93), eight 100 nF + 4.7 µF + 10 µF of IOVDD decoupling (FC C71–C78/C65/C75).
* USB_DP/USB_DM go **straight** to `EMU_USB_DP`/`EMU_USB_DM` with no series resistors and no
  pull-ups (critique item 9); the 22 Ω pair (C25092) lives on `bench_io` only.

### 6.5 Template handling (hard rule 8)

The sheet was generated from validated pantry `lib_symbols` blocks rather than by copying
`RP2350.kicad_sch`, so no FC global label (`TX0`, `SDA1`, `FC_RESET`, `SWCLK`, `USB_DP`, `BOOTSEL`,
`+3V3`, `+1V1`, …) could survive; the APS1604M PSRAM, the I2C pull-ups R6/R25/R39/R41 and the
RF1 pull-downs R110/R111 are not present. A name scan over every label and power symbol on the
finished sheet confirms zero FC names (§7.4).

## 7. Validation (tool output pasted)

### 7.1 `sch_lint.py`

```
$ python3 tools/sch_lint.py emulator_mcu.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/8394a2ec-8c1e-41a1-b086-be3289cedfbc \
    --refdes-block 200-299
emulator_mcu.kicad_sch: 93 symbol instances, 14 lib symbols, 185 wires, 0 errors, 0 warnings
```

**0 errors, 0 warnings** — no off-grid items, no duplicate or malformed uuids, no dangling wire
endpoints, no untouched pins, every instance on the right project/path, every refdes inside 200–299.

### 7.2 `harness_erc.sh "Emulator MCU"` (all six new sheets on disk)

```
harness: sheets in hierarchy: Emulator MCU | Solar and Sensor Emulation | Solar Power Injection |
         Battery Replica and Bench Power | Pyro Inhibit and Jumpers | Bench IO

=== ERC delta vs baseline (Rev2 + 8 promotions; noise types excluded) ===
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

=== violations on sheets matching 'Emulator MCU' ===
total 0
errors: 0
```

* **ERC errors on this sheet: 0. ERC warnings on this sheet: 0** — including the library-metadata
  noise types, which are also zero here.
* **No violation anywhere in the project names a 200–299 refdes.** Checked explicitly:
  `erc_summary.py … --list --ignore-noise | grep -cE 'Symbol (U20[012]|Y200|L200|TP20[0-3]|[RCD]2[0-2][0-9]) '` → **0**.
* The `+6 power_pin_not_driven` and `+67 pin_to_pin` deltas are all on
  `/Solar and Sensor Emulation/` and the other new sheets (TCA4311A VCC pins fed from FC face rails,
  and open-collector/passive pin pairings), not on this one. The two baseline RP2350
  `power_pin_not_driven` errors (U18 DVDD, U18 VREG_AVDD) did **not** reappear for U200 — the two
  PWR_FLAGs on `1V1_EMU` and `VREG_AVDD_EMU` do their job.
* `single_global_label` went **9 → 0**: every contract net on this sheet found its partner, which is
  the cleanest possible confirmation of §4. (Had a partner sheet been missing, the expected residue
  would have been one `single_global_label` warning per orphaned contract net plus a
  `power_pin_not_driven` error on `VBUS_EMU`, whose PWR_FLAG lives on `bench_io`.)

### 7.3 `netlist_diff.py` restricted to this sheet's refdes

```
components: base 261, new 476, added 215, removed 0      (47 of the additions are C200-C222, D200-D202,
                                                          L200, R200-R211, TP200-TP203, U200-U202, Y200)
nets: base 215, new 354
added nets (54) touching emulator_mcu parts
removed nets (0)
changed nets touching emulator_mcu parts (1):
  ~ GND: +[C200.2 … C222.2, D201.1, D202.1, R208.2, R209.2, R210.2, U200.47, U200.61, U201.4, U202.2, Y200.2, Y200.4]  -[]
```

* **Exactly one existing net gains pins from this sheet: `GND` (34 pins).** That is what §4.1 allows.
* **No existing net loses a pin**; nothing is renamed or merged.
* Of the 54 added nets: 14 are sheet-local `/Emulator MCU/…`, 4 are auto-named `Net-(…)`, 10 are the
  new globals this sheet defines and 26 are the new globals it consumes — all listed in §4.2/§4.3,
  and each resolves to the partner refdes the brief predicted (U310–U316 and R31x–R37x on
  `solar_emulation`, R60x on `pyro_inhibit`, J701–J703 / R70x / SW701 / SW702 on `bench_io`).

### 7.4 Name scan and PDF read

```
global labels (35): 3V3_EMU, EMU_BATT_SCL, EMU_BATT_SDA, EMU_BOOTSEL_SW, EMU_CTL_FC_RESET,
  EMU_CTL_USBBOOT, EMU_CTL_WDT_DIS, EMU_F1_SCL … EMU_F5_SENSE, EMU_FC3V3_SENSE, EMU_GPIO_SPARE0,
  EMU_GPIO_SPARE1, EMU_RUN, EMU_SWCLK, EMU_SWDIO, EMU_TOP_SCL, EMU_TOP_SDA, EMU_UART_RX,
  EMU_UART_TX, EMU_USB_DM, EMU_USB_DP, PYRO_INHIBIT_STATE
local labels (14): 1V1_EMU, EMU_FLASH_SS, EMU_GPIO_RSVD, EMU_QSPI_SCLK, EMU_QSPI_SD0..SD3,
  EMU_QSPI_SS, EMU_STATUS_LED, EMU_VREG_LX, EMU_XIN, EMU_XOUT, VREG_AVDD_EMU
power symbols: 3V3_EMU, GND, PWR_FLAG, VBUS_EMU
FC names present: NONE
paper: A3 | sheet_instances: False | trailing (embedded_fonts no): False
```

The harness root was exported to PDF and page 7 read at full page and at 250–400 dpi on the dense
regions (left VREG group, the 32-row GPIO label column, the core-regulator island, the crystal and
BOOTSEL islands). Four readability defects found and fixed in the generator: global-label text was
being centred on its anchor instead of left/right justified; the five VREG pins were fanned out to
four staggered label rows so no two label boxes touch; the two sheet-local right-edge labels
(`EMU_STATUS_LED`, `EMU_GPIO_RSVD`) were given longer stubs so their plain text clears the
neighbouring global-label boxes; and Reference/Value fields on the horizontal resistors, the LEDs,
L200, Y200, U201, U202 and the test points were placed explicitly because the pantry symbols carry
their Value field on the body. The final render has no overlapping text, every label sits on a wire
end, and nothing crosses the A3 frame or the title block.

## 8. Assumptions and open questions for the reviewer

1. ~~**I2C pads on an off face sit above the E9 limit.**~~ **CLOSED by PM ruling R7 (review round,
   2026-09-14).** The original question was: `EMU_Fn_SDA/SCL` are pulled up through 10 k to `Fn_PWR`
   (brief §6.2), so with that face off the pad's only path to 0 V was 10 k — larger than the 8.2 k E9
   workaround — which made the mitigation a *firmware* requirement (disable that channel's input
   buffers while `EMU_Fn_SENSE` reads low) rather than a hardware guarantee. The PM took exactly the
   option this section offered: **R7 drops the device-side pull-ups on the seven emulated channels to
   4.7 k** (Face 0 keeps 10 k for `XY_Face_V4` parity), applied on `solar_emulation` — see
   `solar_emulation_gen.py` `channel()`, `res(sh, r_base+'2'|'3', '4.7k', …)`. 4.7 kΩ ≤ 8.2 kΩ, so the
   off-face pad now meets E9 **in hardware**, the firmware IE-disable is belt-and-braces, and the
   price is the doubled bus current this section predicted (0.33 → 0.70 mA per line when a channel is
   driven, §5 rule 1) plus the larger phantom-power injection recomputed in §6.3.
2. **U202 AP2112K-3.3 has no repo BOM precedent.** C51118 was verified live and the part is a JLC
   Basic-class staple, but no PROVES board has ordered it. The heritage alternative
   (TPS62085RLTT C2070694 + XFL4015-471MEC C18221164, as on `proves_radio_stick_V2`) is a
   contained swap in the power block if the reviewer prefers it — see §6.1 for why I did not.
3. **ADC_AVDD is tied straight to `3V3_EMU`,** exactly as the FC ties U18 pin 44 to `+3V3`. The
   RP2350 hardware design guide suggests a ferrite/RC into ADC_AVDD when the ADC is used for
   precision work. The emulator does not use its ADC in Phase 1 (GPIO26–29 carry digital sense taps),
   so FC parity was kept. Flag it if Phase 2 wants analogue rail monitoring on those pins.
4. **GPIO16/17 were chosen for the UART** because they carry the UART0 TX/RX pin-mux function, so the
   bench console needs no PIO. If firmware would rather put the console on UART1, GPIO20/21
   (`EMU_GPIO_SPARE0/1`) are the UART1 TX/RX alternates and the map can be swapped without a respin.
5. **The PIO assumption is 1 state machine per I2C channel** (7 of 12), per critique item 21. If the
   Phase 3 spike finds an I2C slave needs 2 SMs per channel, 7 channels need 14 and the design breaks;
   the schematic mitigation available without a respin is to group the four face channels in GPIO0–7
   so one PIO block can multiplex them, which is what the map does.
6. **Two global labels carry a duplicate name on this sheet** (`EMU_UART_RX`, `EMU_GPIO_SPARE0`,
   `EMU_GPIO_SPARE1` appear once at the MCU pin and once at their pull resistor). That is ordinary
   KiCad practice and the netlist is unaffected, but it means a future harness run with `bench_io`
   absent would *not* raise `single_global_label` for those three nets. Noted so the integrator does
   not read their absence as proof of a connection.
7. **No FC finding from this sheet.** The eps_side "VSOLAR 9V to 40V" error belongs to
   `solar_power_injection`; nothing on the RP2350 sheet contradicted the FC.

## 9. Deviations from the brief

| # | Deviation | Why |
|---|---|---|
| 1 | Brief §6.1 lists the E9 pulls for `EMU_UART_RX` / `EMU_GPIO_SPARE0/1` / `EMU_GPIO_RSVD` only implicitly (hard rule 10 + critique item 4/5 assign the other sheets' pulls explicitly). I fitted **four 4.7 k resistors (R207–R210)** on this sheet to cover them. | Hard rule 10 requires every input or default-state-sensitive GPIO to have a ≤ 8.2 k pull or be documented as input-buffer-disabled. `EMU_UART_RX` is a real input; the spares and the reserved GPIO would otherwise be the only floating pads on the emulator. Four 0402s, no firmware caveat. |
| 2 | The flash decoupling cap (C220) and the RUN/BOOTSEL network are drawn as **separate islands joined by `3V3_EMU` power symbols and local labels**, not by long wires. | Keeps the A3 sheet free of crossings; electrically identical, and the netlist diff confirms one `3V3_EMU` net and one `EMU_FLASH_SS` net. |
| 3 | The sheet was **generated from pantry symbols** rather than copied from `RP2350.kicad_sch`. | Brief §6.1 suggests the template; §7 recommends a generator. Generating removes any chance of a stray FC global label (hard rule 8) while keeping every component value, footprint and LCSC number at FC parity — the parity is itemised in §6.4. |
| 4 | Test points: TP200 `VBUS_EMU`, TP201 `3V3_EMU`, TP202 `1V1_EMU`, TP203 `EMU_GPIO_RSVD`. **No test point on `VREG_AVDD_EMU`.** | §6 asks for test points "on every bench-relevant rail". `VREG_AVDD_EMU` is an internal RC filter node on an MCU analogue supply pin, not a bench rail, and a probe pad on it would only load the filter. Say so and I will add TP204. |

---

## 12. Integrator change (2026-09-14): C200 10 µF → 1 µF

**Ownership note.** This edit was made by the **integrator**, not by this sheet's agent. Brief §3 rule 2 puts
`emulator_mcu.kicad_sch` in the sheet agent's writable set, so it is an explicit rule deviation, recorded in
`integration_report.md` §1.2 alongside the other three.

**Why it could not be fixed on one sheet.** `bench_io` fits C701 = 10 µF at the USB-C connector (brief §6.6,
"with bulk cap"); this sheet independently fitted C200 = 10 µF + C201 = 100 nF as the AP2112K input caps on the
same net. Combined that is **20.1 µF on `VBUS_EMU`**, against the USB 2.0 §7.2.4.1 limit of 10 µF of bypass
capacitance a downstream device may present. Neither sheet could see the total; `bench_io`'s report escalated
it to the integrator ("drop one of the two 10 µF caps or explicitly accept the derated total").

**The edit.** C200 `Value` `10uF` → `1uF`, `LCSC Part` `C19702` → **`C15849`** (1 µF, `C_0603_1608Metric`,
from the as-ordered `FC_V5e_Production_Rev2/jlcpcb/production_files/BOM-*.csv` line
`1uF,"C37,C4,C41",C_0603_1608Metric,C15849,3` — rule 5 satisfied), footprint unchanged, `Description` updated
to name it the AP2112K input capacitor. 1 µF is the AP2112 datasheet's own recommendation (BCD/Diodes AP2112
Rev 2.0 p.1, "stable with 1.0 µF"), and `proves_radio_stick_V2` — the closest PROVES topology, RP2350 + USB-C +
regulator — carries exactly one 10 µF (C15) on VBUS.

**Result.** `VBUS_EMU` now carries C701 10 µF (bench_io, at the connector) + C200 1 µF + C201 100 nF =
**11.1 µF nominal**, ≈ 8 µF effective after the 20–30 % DC-bias derating normal for X5R/X7R ceramics on a 5 V
rail. Still 11 % over the literal §7.2.4.1 number nominally; carried as integration-report open item **O6**
rather than pushed lower, because taking it lower would under-bulk the LDO input. No netlist change (property
edit only); C200 remains one of the 216 *added* components, so the netlist diff shows it as an addition, not
as a change to anything that existed in Rev2.

---

## 13. Review fixes (Fable review-and-fix round, 2026-09-14)

Applied by the `emulator_mcu` fixer. Writable set: `emulator_mcu.kicad_sch`,
`tools/gen/emulator_mcu_gen.py`, this report. **Both** the sheet and the generator were changed, so a
regeneration reproduces the sheet (integrator convention).

| id | Title | Severity | Status |
|---|---|---|---|
| 4 | Stale R7 figures (10 k / 0.33 mA / 0.26 mA) in the sheet notes, and a phantom-power note asserting a sink mechanism the AP2112K datasheet does not support | minor | **applied** |
| 10 | No FlatSat document recorded the FC-face ↔ TCA9548-channel ↔ firmware-face crosswalk | minor | **applied** |

### 13.1 What changed on the sheet

**Item 4 — `FIRMWARE RULES THAT THE HARDWARE ASSUMES`.** Rule 1 `10 k … (~0.33 mA per line)` →
`4.7 k … (~0.70 mA per line)`. Rule 2 rewritten: the off-face pad now reads
"see 4.7 k to 0 V, which already meets the 8.2 k E9 limit in hardware (R7)", and the firmware
input-buffer-disable is demoted to "belt-and-braces, not a requirement". Depends on item 3 (R7), which
had already landed on `solar_emulation` when this was applied — verified directly, not assumed:
`solar_emulation_gen.py` `channel()` now emits `res(sh, r_base+'2', '4.7k', …)` and
`res(sh, r_base+'3', '4.7k', …)` for the device-side SDA/SCL pull-ups, Face 0's `R302`/`R303` still
read `10k` (line 494 comment "Face 0 … keeps 10 k for XY_Face_V4 parity"), and
`solar_emulation.kicad_sch` on disk holds 20 × `4.7k` (14 device-side + 6 sense taps) and 17 × `10k`.

**Item 4 — `PHANTOM POWER PATH`.** Rewritten end to end. Old text (removed):
"*…the 14 device-side 10 k pull-ups … feed about 0.26 mA per line … U202 sinks it and the rail sits
well below its 3.3 V setpoint.*" New text:

```
PHANTOM POWER PATH (accepted - obey the BENCH RULE)
FC powered, emulator unpowered: the 14 device-side 4.7 k pull-
ups on solar_emulation push up to (3.3-0.7)/4.7k = 0.55 mA per
line, ~7.7 mA over 14 lines, into 3V3_EMU via the RP2350 pad
ESD diodes. Nothing is in series to block it.
U202 does NOT sink it: the AP2112K 60 ohm output discharge
(datasheet Electrical Characteristics, RDCHG) needs EN LOW, and
EN is tied to VIN here, so with VBUS_EMU absent the LDO back-
feeds its own input instead. 3V3_EMU therefore floats to about
2.6 V (one ESD-diode drop below Fn_PWR; R211/D201 hold it near
2.4 V), leaving the RP2350 PARTIALLY POWERED, I/O UNDEFINED.
BENCH RULE: plug the emulator USB in before or with FC power;
never leave the FC powered with the emulator unplugged.
```

Datasheet evidence for the mechanism correction: Diodes **AP2112** (the `DS_LDO` URL on U202), Electrical
Characteristics, row `VOUT Discharge Resistor  R_DCHG  Set EN pin at Low  60  Ω` — the 60 Ω discharge is
conditioned on **EN low**, and this sheet ties EN to VIN (`build_power()`: `s.wire((66.04, yr), (66.04,
u['3'][1]))  # EN tied to VIN`; netlist `VBUS_EMU: … U202.1, U202.3`). Full reasoning and the ≈2.4 V
settling calculation are in §6.3.

**Item 10 — new `FC FACE <-> TCA9548 <-> FIRMWARE CROSSWALK` block** in the footer of the sheet, six
lines, under the GPIO map:

```
FC FACE <-> TCA9548 <-> FIRMWARE CROSSWALK (proves-core-reference 8e4d487)
EMU_F1/F2/F3 = FC F1/F2/F3 = ch1/ch2/ch3 = zephyr face1/face2/face3:  TMP112 0x48 + VEML6031 0x29 + DRV2605L 0x5A
EMU_F4 = FC F4 = ch5 = zephyr face5:  same three devices; Z- detumble face (Z_MINUS_RESISTANCE 150.7 ohm coil model)
EMU_F5 = FC F5 = ch6 = zephyr face6:  only the VEML6031 0x29 is instantiated in the current FSW topology
EMU_BATT = ch4:  TMP112 x4 at 0x48/0x49/0x4A/0x4B.  EMU_TOP = ch7 = zephyr face7:  VEML6031 0x29 (the real top cap
   also carries TMP112 0x48; the dts top-cap-temp TODO is stale).  Firmware face = FC face for F0-F3, +1 for F4/F5.
```

The full table, with the per-row evidence and the three facts a Phase-3 profile author cannot get from
the net names, is the new **§5.1**. Validated against `proves-core-reference`
`8e4d487a2a0056dd7d374c86ae47e8443a1c0fd1` (2026-08-30); the top-cap TMP112 address came from a
`kicad-cli` netlist export of `antenna_top_cap_v2c.kicad_sch` (U4 `ADD0` pin 4 on `GND` → `0x48`).

### 13.2 Layout consequence (cosmetic, unavoidable)

The R7 / phantom-power rewrite lengthened the right-hand note column past `y = 204`, where the
`INTERFACE NOTES` footer column starts and overlaps the same x band — the first PDF re-export showed the
two blocks printing on top of each other. The fix is in `build_notes()`: the side column's row pitch
goes **4.0 mm → 3.5 mm** (with a comment saying why), which lands the last side-note row at `y = 191.5`,
12.5 mm clear. Foot-note pitch is unchanged at 3.8 mm; the crosswalk block ends at `y = 280.0` and
`x ≤ 288.9`, clear of both the frame and the title block. Confirmed by reading the re-exported page 7.

### 13.3 Sections of this report updated

§5 firmware rules 1 and 2 · **new §5.1** crosswalk table · §6.3 rewritten (current, mechanism, settling
voltage, bench rule) · §8 open question 1 marked **CLOSED by R7**.

### 13.4 Validation after the fixes

Both fixes are text-only. Proof that nothing electrical moved: regenerate the sheet from the *pre-fix*
generator, strip every `(text …)` item and normalise uuids in both files — the remainder is
**byte-identical**, 220 236 bytes each. All 72 symbol instances keep their original uuids (the new sheet
is a clean regeneration with the uuids of unchanged items copied back from the previous file), and no
item uuid is duplicated.

```
$ python3 tools/sch_lint.py emulator_mcu.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/8394a2ec-8c1e-41a1-b086-be3289cedfbc \
    --refdes-block 200-299
emulator_mcu.kicad_sch: 93 symbol instances, 14 lib symbols, 185 wires, 0 errors, 0 warnings

$ SCRATCH=<scratch>/review_fix_emulator_mcu tools/harness_erc.sh "Emulator MCU"
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

=== violations on sheets matching 'Emulator MCU' ===
total 0
errors: 0

=== netlist diff vs baseline ===
components: base 261, new 477, added 216, removed 0
removed nets (0):

$ BASE_ERC=tools/baseline/erc.json BASE_NET=tools/baseline/netlist.kicadxml \
  SCRATCH=<scratch>/review_fix_emulator_mcu_rev2 tools/harness_erc.sh "Emulator MCU"
error    pin_not_connected                 5      5     +0
error    power_pin_not_driven              6      6     +0
total baseline 125, now 192, delta +67
errors: 11
=== violations on sheets matching 'Emulator MCU' ===  total 0, errors: 0
```

The 11 errors and every error class are `+0` against **both** the post-promotion baseline and the raw
Rev2 baseline; zero violations of any severity land on this sheet; no net lost a pin and none was
removed. Page 7 was re-exported with `kicad-cli sch export pdf --pages 7` and read at 150 dpi to confirm
both note blocks render inside the frame with no overlap.
