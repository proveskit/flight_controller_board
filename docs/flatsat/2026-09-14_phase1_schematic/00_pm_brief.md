# PROVES FlatSat V1 — Phase 1 schematic capture: product-manager brief (rev 2)

**Date:** 2026-09-14 · **Rev 2:** all 21 items of the Fable critique `01_brief_critique.md` folded in (values, net-name rule, BQ25886 facts, RP2350-E9 pull values, VSOLAR limits, PWR_FLAG ownership, promotion sequencing, USB series R, root placement, notes). · **Project:** `flight_controller_board/FlatSat_V1/` on branch `flatsat-v1` (forked from `v5e-rev2`, `FC_V5e_Production_Rev2`) · **Plan of record:** the PROVES FlatSat plan artifact rev 4 (§4 subsystem table, §7 roadmap, §8 risks) · **Handoff:** `/tmp/proves-flatsat-phase1-handoff.md`

This brief is the specification for the six new schematic sheets. Implementer agents work from it; reviewer agents review against it. Where this brief and the plan artifact disagree, this brief wins for Phase 1 and the disagreement is recorded in §2 below.

---

## 1. What is being built

The FlatSat is one PCB, forked from the flight controller (FC) `FC_V5e_Production_Rev2`, that keeps the real flight MCU (RP2350, U18) and real radios (U13 UHF, U30 S-band) and folds the *electrical behaviour* of the other kit boards onto the same board so flight software can be tested end to end on a bench:

- five solar faces, the battery pack's four temperature sensors and the antenna top-cap sensor pair are **emulated** by a second RP2350 (the Emulator MCU) that answers as I2C slaves behind the same TCA4311A hot-swap buffers the real boards use, only while the FC has that face's power switch on;
- one solar face (Face 0) is **real reference silicon** (TMP112 + VEML6031 + DRV2605L + TCA4311A) for calibration;
- the LT3652 solar charge path is exercised by **bench VSOLAR injection**;
- the battery pack's **protection stage is replicated** (R5460N208AA + IRF7458 FETs) in front of a bench PSU input, plus a USB→BQ25886 charger path derived from `antenna-board/debug_board_v1`;
- the FC's live pyro/heater driver U6 (TPS4H160) gets a **bench inhibit switch** on its enable lines;
- a **bench I/O** block gives the emulator its own USB-C + SWD and gives the bench control of the FC's reset/boot/watchdog lines.

Everything already on the FC stays as it is (heritage: V5d flew, V5e Rev1 passed environmental test). New sheets connect to existing nets through the global labels the FC sheets already use. No existing net is renamed except the eight local labels promoted to global in §4.3 (already done), and nothing is added **in series** with any power path that exists in flight wiring.

## 2. Decisions taken for Phase 1 (PM, 2026-09-14)

These close the items the plan left open for Phase 1. Each is reversible in Phase 2 if the hardware lead objects; say so in your sheet report if you find a reason to.

| # | Question (plan ref) | Decision | Why |
|---|---|---|---|
| D1 | Heater channel scope (§1, §4 pyro row) | One inhibit switch covers all three EN nets (Deploy1_EN, Heater_EN, Deploy2_EN). The Heater_EN diode leg gets a 2-pin jumper header, **shunt fitted by default** (assembly note, not a schematic short), so the heater can be excluded from the inhibit later without a respin. No on-board heater dummy load; J21 stays a connector. | flight_controller_board#53 (ch3/ch4 crossed) is unresolved, so "heater-only" cannot be assumed non-pyro. The jumper costs nothing and keeps the future option. |
| D2 | Per-face VSOLAR injection (§4 solar rows, §8) | **Two** injection channels, not six: CH-A fitted by default, CH-B footprint-only (shunt open). Each: screw terminal → fuse → Schottky (CDBA240LL-HF class, as the faces) → jumper header → `VSOLAR`. No per-face current limiting. | On this FC all six face connectors' VSOLAR pins are one net (J1/J2/J6/J9/J11/J13 pins 1-2 → `VSOLAR`), so six taps from one bench rail are electrically identical to one tap. Two independent channels are enough to demonstrate diode OR-ing / one-face-shadowed with two bench supplies. |
| D3 | Bench power: PSU-behind-replica vs USB→BQ25886 (§3, §8) | **Carry both**, on the `battery_protection_replica` sheet. The BQ25886 stage gets its own power-only USB-C and a 2-pin output jumper header, **shunt removed by default**, in its `Dir_Chrg_In` feed. Note: `debug_board_v1` was never assembled (its JLC BOM/CPL are header-only), so it is a starting point, not a validated precedent; its known gaps are corrected in §6.4. | Both feed the same node (`Dir_Chrg_In`); the jumper prevents the charger pushing into a bench PSU. The replica path is what exercises pack-side protection; the USB path is the "plug in and go" convenience. |
| D4 | Protection-replica fidelity (§8) | Copy `battery_pack_v2`'s stage **exactly** (R5460N208AA-TR-FE, C259714; 2× IRF7458, C10879; same R/C values), with a **synthetic cell midpoint of 2 × 1.0 kΩ** (jumper-selectable) because a single bench PSU has no 2-cell mid-tap, plus a 3-way input terminal (B+, MID, B−) for a real dual supply. | R5460N is a 2-cell protector; without a midpoint it would see one "cell" at full pack voltage and trip. The R5460 datasheet (p.17) requires < 1 kΩ effective series resistance at VC, so high-value dividers are forbidden. |
| D5 | S-band RF (§4, §8) | **Radiated-only** on the bench for Phase 1. No schematic change. | U30's footprint has no antenna net; a module variant or pigtail is a mechanical/procurement decision, not a schematic one. Recorded as open in the plan's risk list. |
| D6 | RBF / inhibit break points (§4 RBF row) | The existing connectors (J7/J8/J10/J15/J19/J20/J29/J30) remain the break points. Add one 2.54 mm 2-pin shunt header **in parallel** with each break on the `pyro_inhibit` sheet (six headers). No relay/FET arm stage in Phase 1. | Parallel headers add nothing in series with a flight path; they make the bench usable without Pico-Lock crimp pigtails. The optional scripted-arm stage is deferred to a later revision. |
| D7 | Emulator architecture | One RP2350A (60-QFN, same part/footprint as U18 and proves_radio_stick_V2), W25Q128JVS flash, its **own** 3.3 V rail `3V3_EMU` from its **own** USB-C `VBUS_EMU`, common GND with the FC. Seven I2C channel front-ends, each a TCA4311A powered exactly like the real board it replaces (five from `F1_PWR`..`F5_PWR`, two from the FC `+3V3`). Fn_PWR presence sensed on dedicated GPIO through 4.7 k. | Independent power means the emulator survives FC power cycles and watchdog resets and can present "just powered" register state on every Fn_PWR rising edge. Matching TCA4311A topology gives the same hot-swap/isolation behaviour firmware sees on real hardware (TCA4311A: powered-off high-impedance I2C pins; EN low or VCC < UVLO 2.5 V isolates IN from OUT). |
| D8 | Bench control of FC lines | The FC's own SW1 (USBBOOT) and SW2 (FC_RESET) are on the board already and are not duplicated. `bench_io` adds a WDT_DISABLE toggle, three open-drain N-FET drivers (4.7 k gate pull-downs, RP2350-E9) so the emulator can pull `FC_RESET`, `USBBOOT`, `WDT_DISABLE` low under console command, and a bench header exposing those nets plus emulator UART/spare GPIO. | Scripted reset/boot/watchdog control is what makes an automated bench possible; buttons alone do not. |
| D9 | Pyro inhibit state visibility | The inhibit switch's common node is read by an emulator GPIO (`PYRO_INHIBIT_STATE`, through 4.7 k) and drives a "SAFE" LED. LED lit = inhibit engaged AND emulator powered; the inhibit itself never depends on `3V3_EMU`. | Lets the console refuse burn-wire tests unless the inhibit is engaged. Sense only; the emulator never drives the EN nets. |
| D10 | Phase numbering | Workflow phase labels are neutral ("Capture", "Review", "Layout"). The plan's §7 numbering (schematic = 1, layout = 2) is not changed by this work. | The user's "Phase 3 = layout" phrasing is unresolved; the PM asks before renumbering. |
| D11 | J14 with bench sources live | J14 (battery pack connector) stays populated for connector-trace completeness and for FC-only tests with a real pack. Text note on `battery_protection_replica`: never connect a pack to J14 while the bench PSU or the charger USB is connected. Whether to mark J14 DNP on the FlatSat BOM is deferred to the layout/BOM phase. | Two sources in parallel on a lithium pack is the one failure this bench must make impossible; a note plus the default-open charger jumper is the Phase 1 answer. |

## 3. Project layout, tools, hard rules

```
flight_controller_board/                      (git, branch flatsat-v1)
├── FC_V5e_Production_Rev2/                   baseline — READ ONLY, KiCad GUI has it open
├── FlatSat_V1/                               the new project (copy of Rev2, renamed, verified identical, then the §4.3 promotions)
│   ├── FlatSat_V1.kicad_sch                  root sheet (uuid c64c0d72-a9f6-4f3a-891e-1f647558f538)
│   ├── eps_side.kicad_sch                    "Power Systems"  (sheet uuid 7cbc73fc-c188-4597-842f-d15f69db7471, page 4)
│   ├── load_switches.kicad_sch               "Load Switches"  (inside eps_side; uuid 1ac8f3d4-e8b4-451e-be76-8bf59103b6c5, page 5)
│   ├── RP2350.kicad_sch                      flight MCU sheet (uuid 0828f938-6835-4ac8-b7be-ff90971df31f, page 6)
│   ├── watchdog.kicad_sch                    (uuid d3e26510-981a-4dd5-9b7d-a587e6324dc6, page 3)
│   ├── <six new sheets>.kicad_sch            YOU WRITE THESE (one per agent)
│   ├── symbols/flatsat.kicad_sym             project-local symbol lib (integrator maintains; sheet agents do not touch)
│   ├── sym-lib-table, fp-lib-table           project libs (RP2350_60QFN_minimal footprint lib is here)
│   ├── jlcpcb/project.db                     LCSC mapping for the plugin — DO NOT WRITE
│   └── tools/                                helpers (see §7)
├── docs/flatsat/2026-09-14_phase1_schematic/ this brief, the critique, your sheet reports
└── .claude/workflows/                        pcb-flight-review.js, flatsat-schematic-capture.js, flatsat-schematic-review.js
```

Tools: `kicad-cli` = `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` (10.0.1). Symbol libraries: KiCad standard at `/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/`, the user's global `easyeda2kicad` at `~/Documents/KiCad/easyeda2kicad/easyeda2kicad.kicad_sym` (+ `.pretty`), project libs per `sym-lib-table`. KiCad standard footprints at `/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/`.

Hard rules (from the repo's CLAUDE.md and this phase):

1. **Never modify anything under `FC_V5e_Production_Rev2/`.** The KiCad GUI has it open (lock files present).
2. **One agent, one writable file.** A sheet agent writes only `FlatSat_V1/<its sheet>.kicad_sch`, its report `docs/flatsat/2026-09-14_phase1_schematic/sheet_<key>.md`, and its generator under `FlatSat_V1/tools/gen/`. Only the integrator edits the root, `eps_side`, `load_switches`, `symbols/flatsat.kicad_sym`, `sym-lib-table`.
3. **Write atomically**: write to `<file>.tmp` then `mv` over the target. Other agents' harness runs read your file while you work.
4. Schematic text notes on existing sheets are requirements (`grep '(text "'`) — except the eps_side note "VSOLAR 9V to 40V", which is wrong (see §6.3) and must be reported, not repeated.
5. Do not write `jlcpcb/project.db`. Put `LCSC Part` on symbols only when the number comes from an as-ordered BOM in the repos or was verified live; otherwise leave it blank and list the part in your report under "needs LCSC".
6. Nothing in series with a flight power path (`VBUSP`, "High Power Interstage", `Dir_Chrg_In`↔`VBATT_SENSE`↔inhibit chain, `VSOLAR`, face `Fn_PWR`). Taps, parallel headers and diode clamps on control nets are fine.
7. Do not run the KiCad GUI. Do not `git commit`. Do not touch the `proves-wiring-harness` stash.
8. The RP2350 template sheets contain **global labels that belong to the FC** (`TX0`, `SDA1`, `FC_RESET`, `SWCLK`, `USB_DP`, …). Any global label you copy from a template must be renamed to a name from §4 or deleted; a stray FC net name on the emulator sheet shorts the emulator into the flight MCU.
9. Jumpers that are "shunt fitted by default" are drawn as open 2-pin headers (`Connector_Generic:Conn_01x02` or `Jumper:Jumper_2_Open`, never a `_Bridged` symbol) with an assembly/text note; a bridged symbol merges nets in the netlist and breaks the baseline check.
10. RP2350 erratum E9 (A2 silicon: a GPIO configured as input with the input buffer enabled leaks up to 120 µA and floats to ~2 V unless the external pull is ≤ 8.2 kΩ): every emulator GPIO that is an input, or is read before firmware configures it, or whose default state matters to the FC, gets an external pull ≤ 8.2 k (4.7 k used throughout this brief) or is documented as input-buffer-disabled.

## 4. Interface net contract

### 4.1 Existing FC global nets that new sheets connect to (use these exact names as `global_label`s; power symbols for `GND` / `+3V3`)

| Net | What it is on the FC (from the Rev2 netlist) | Used by |
|---|---|---|
| `F0_SDA` `F0_SCL` `F0_PWR` … `F5_SDA` `F5_SCL` `F5_PWR` | Per-face I2C behind TCA9548 U3 (ch0..3 = F0..F3, ch5 = F4, ch6 = F5; FC-side 4.7 k pull-ups already on every line) and per-face 3V3 from AP22653 U19/U21/U22/U24/U23/U27 gated by `FACEn_ENABLE` (MCP23017 U9). Also on J6/J9/J11/J13/J1/J2 pins 4-6 | solar_emulation |
| `VSOLAR` | Charger input: J1/J2/J6/J9/J11/J13 pins 1-2 → R108 2 mΩ → `V_SOLAR_SENSE` → IC6 LT3652 VIN/SHDN; INA219 U8 (0x41) IN+ is directly on `VSOLAR` (26 V absolute maximum) | solar_power_injection |
| `BATT_SDA` `BATT_SCL` | TCA9548 U3 ch4 → J14 pins 10/12 (battery pack TMP112s behind the pack's TCA4311A) | solar_emulation |
| `SDA_Top` `SCL_Top` | TCA9548 U3 ch7 → J16 pins 5/7 (antenna top-cap VEML6031 + TMP112) | solar_emulation |
| `+3V3` | FC 3.3 V rail from U10; also J14 pin 11 and J16 pin 6 (feeds the pack's and top-cap's TCA4311A) | solar_emulation (VCC of the BATT/TOP buffers, sense) |
| `Dir_Chrg_In` | Battery + into the FC: J14 pins 1,3,5,7,9; J16 pin 8 (debug-board charger); INA219 U16 (0x40) IN+; R109 2 mΩ shunt to `VBATT_SENSE` (LT3652 BAT) | battery_protection_replica |
| `B-` | Pack-terminal negative (the pack's `PACK-`, after both protection FETs): J14 pins 2/4/6/8; joined to `GND` only through J15/J19 (ISS inhibit). Promoted global (§4.3) | battery_protection_replica, pyro_inhibit |
| `VBUSP` | Main switched bus after the inhibit chain (U10 VIN, U25 VBB, U1 V+) | pyro_inhibit (RBF header only) |
| `VBATT_SENSE` `INHIB_1` `INHIB_2` `IN_RBF` | Inhibit-chain nodes, promoted global (§4.3) | pyro_inhibit (shunt headers) |
| `Deploy1_EN` `Heater_EN` `Deploy2_EN` | U6 IN1+IN2 / IN3 / IN4 nodes downstream of R104 / R100 / R103 (4.7 k from GPIO29 `FIRE_DEPLOY1_B` / U9 GPA0 `ENABLE_Heater` / U9 GPA2 `FIRE_DEPLOY2_B`); promoted global (§4.3) | pyro_inhibit |
| `FC_RESET` `USBBOOT` `WDT_DISABLE` | J16 pins 2/1/9; `FC_RESET` = U18 RUN with R1 10 k to +3V3 and SW2; `USBBOOT` = SW1 node, D4 (NSR0320) cathode, anode → R10 1 k → `BOOTSEL`; `WDT_DISABLE` = watchdog integrator node (C22+C23, R31/R33/R35, U1 pin 8) with J4 jumper | bench_io |
| `DEPLOY1` `DEPLOY1_AUX` `DEPLOY2` `Heater Output` | U6 outputs to J16.10 / J23 / J24 / J21 | none (connectors stay; listed for the trace table) |
| `GND` | common ground | all |

### 4.2 New cross-sheet nets (global labels; the sheet in the "defined by" column drives or sources it)

| Net | Defined by | Consumed by | Meaning |
|---|---|---|---|
| `EMU_F1_SDA` `EMU_F1_SCL` … `EMU_F5_SDA` `EMU_F5_SCL` | solar_emulation (TCA4311A device side, 10 k pull-ups to that face's `Fn_PWR`) | emulator_mcu (GPIO, PIO I2C slave, open-drain only) | emulated face n bus |
| `EMU_BATT_SDA` `EMU_BATT_SCL` | solar_emulation (buffer VCC = `+3V3`, 10 k pull-ups to `+3V3`) | emulator_mcu | emulated battery TMP112 ×4 (mux ch4) |
| `EMU_TOP_SDA` `EMU_TOP_SCL` | solar_emulation (buffer VCC = `+3V3`, 10 k pull-ups to `+3V3`) | emulator_mcu | emulated top-cap VEML6031 + TMP112 (mux ch7) |
| `EMU_F1_SENSE` … `EMU_F5_SENSE` | solar_emulation (`Fn_PWR` through **4.7 k** series R; ≤ 8.2 k per RP2350-E9, also limits back-feed into an unpowered emulator's ESD diode to ~0.55 mA) | emulator_mcu | face power present |
| `EMU_FC3V3_SENSE` | solar_emulation (`+3V3` through 4.7 k) | emulator_mcu | FC 3.3 V present (BATT/TOP channels alive) |
| `PYRO_INHIBIT_STATE` | pyro_inhibit (switch common node through 4.7 k) | emulator_mcu | low = inhibited/safe |
| `EMU_CTL_FC_RESET` `EMU_CTL_USBBOOT` `EMU_CTL_WDT_DIS` | emulator_mcu (GPIO, default low; input-buffer note per rule 10) | bench_io (gate of open-drain N-FET pulling the FC net low; 4.7 k gate pull-down lives on bench_io) | scripted reset / boot / watchdog-disable |
| `EMU_USB_DP` `EMU_USB_DM` | bench_io (USB-C, after **22 Ω** series R, C25092, as R7/R8 on the FC) | emulator_mcu (USB_DP/USB_DM pins wired directly; no series R, no pull-ups on the emulator sheet) | emulator USB |
| `EMU_SWCLK` `EMU_SWDIO` | bench_io (JST-SH SWD) | emulator_mcu | emulator debug |
| `EMU_RUN` | emulator_mcu (RUN pin with 10 k pull-up to `3V3_EMU`) | bench_io (button to GND) | emulator reset |
| `EMU_BOOTSEL_SW` | emulator_mcu (node that a button pulls low to enter USB boot; mirror the FC's SW1 → D4 → R10 → QSPI_SS arrangement) | bench_io (button to GND) | emulator USB boot |
| `EMU_UART_TX` `EMU_UART_RX` `EMU_GPIO_SPARE0` `EMU_GPIO_SPARE1` | emulator_mcu | bench_io (header) | bench header |
| `VBUS_EMU` | bench_io (USB-C VBUS; power symbol `flatsat:VBUS_EMU`) | emulator_mcu (regulator in) | emulator 5 V |
| `3V3_EMU` | emulator_mcu (regulator out; power symbol `flatsat:3V3_EMU`) | bench_io, pyro_inhibit (LED/pull-up). Nothing on solar_emulation (face-side pull-ups go to `Fn_PWR`/`+3V3`) | emulator 3.3 V |

Rails internal to one sheet (power symbols exist in the pantry, or use local labels): `VBUS_CHG` (charger USB-C), `VSOLAR_BENCH_A/B` (solar bench inputs), `VBAT_BENCH` / `VBAT_BENCH_N` (battery PSU + / cell-negative), `1V1_EMU` (emulator core).

**PWR_FLAG ownership** — exactly one per new rail, on the defining sheet, and never on `GND`, `+3V3`, `VSOLAR`, `Dir_Chrg_In`, `VBUSP`, `B-`, `VBATT_SENSE`, `Fn_PWR` or any other existing FC net (the FC already has power-output pins on those and no PWR_FLAG anywhere; a second power output on a net is an ERC error): `VBUS_EMU` → bench_io; `3V3_EMU`, `1V1_EMU`, `VREG_AVDD_EMU` → emulator_mcu (omit where the regulator symbol's output pin is already `power_out`); `VBUS_CHG`, `VBAT_BENCH`, `VBAT_BENCH_N` → battery_protection_replica; `VSOLAR_BENCH_A`, `VSOLAR_BENCH_B` → solar_power_injection. The FC baseline's `power_pin_not_driven` errors on U18 DVDD (+1V1) / VREG_AVDD will recur on the emulator copy unless flagged there — flag them.

### 4.3 Local labels promoted to global — DONE by the PM on 2026-09-14, before any sheet agent ran

| Sheet | Was local label (all occurrences, each unique) | Now global | Needed by |
|---|---|---|---|
| load_switches | `Deploy1_EN` at (223.52, 81.28) | `Deploy1_EN` | pyro_inhibit |
| load_switches | `Heater_EN` at (223.52, 86.36) | `Heater_EN` | pyro_inhibit |
| load_switches | `Deploy2_EN` at (223.52, 88.9) | `Deploy2_EN` | pyro_inhibit |
| eps_side | `B-` at (134.62, 187.96) | `B-` | battery_protection_replica, pyro_inhibit |
| eps_side | `VBATT_SENSE` at (165.1, 110.49, rot 270) | `VBATT_SENSE` | pyro_inhibit |
| eps_side | `INHIB_1` at (199.39, 57.15) | `INHIB_1` | pyro_inhibit |
| eps_side | `INHIB_2` at (199.39, 68.58) | `INHIB_2` | pyro_inhibit |
| eps_side | `IN_RBF` at (223.52, 57.15) | `IN_RBF` | pyro_inhibit |

Verified after promotion: netlist diff vs Rev2 = eight pure renames (`/Power Systems/X` or `/Power Systems/Load Switches/X` → `X`, identical membership), zero new ERC errors; the only new warnings are eight `single_global_label` until the consuming sheets exist. Sheet agents use the global names directly. The integrator re-checks the eight renames in the final netlist diff.

Inhibit chain for reference (Rev2 netlist): `VBATT_SENSE` —J8(INHIBIT_S1)— `INHIB_1` —J29(INHIBIT_S2)— `IN_RBF` —J30/J20(RBF)— `VBUSP`; parallel path `VBATT_SENSE` —J7(INHIBIT_P1)— `INHIB_2` —J10(INHIBIT_P2)— `IN_RBF`; return `B-` —J15/J19(ISS_INHIBIT)— `GND`.

## 5. Sheet table

Root uuid `c64c0d72-a9f6-4f3a-891e-1f647558f538`. Instances path for a symbol on sheet k = `/c64c0d72-a9f6-4f3a-891e-1f647558f538/<sheet symbol uuid>`. Project name in every `(instances (project "FlatSat_V1" …))` block is `FlatSat_V1`.

| key | file | Sheetname (root) | sheet symbol uuid | page | root placement (at) | refdes block (every prefix incl. #PWR/#FLG) | model |
|---|---|---|---|---|---|---|---|
| emulator_mcu | `emulator_mcu.kicad_sch` | Emulator MCU | `8394a2ec-8c1e-41a1-b086-be3289cedfbc` | 7 | (33.02, 154.94) | 200–299 | opus |
| solar_emulation | `solar_emulation.kicad_sch` | Solar and Sensor Emulation | `0ec7a68a-65de-4eda-8407-9dcf20e51c0b` | 8 | (71.12, 154.94) | 300–399 | opus |
| solar_power_injection | `solar_power_injection.kicad_sch` | Solar Power Injection | `88d5f13b-6a4a-4f50-805f-872821082e52` | 9 | (109.22, 154.94) | 400–449 | sonnet |
| battery_protection_replica | `battery_protection_replica.kicad_sch` | Battery Replica and Bench Power | `bb4d499a-05c5-44dd-bd1a-4ed07bbd6ca0` | 10 | (33.02, 176.53) | 500–599 | opus |
| pyro_inhibit | `pyro_inhibit.kicad_sch` | Pyro Inhibit and Jumpers | `ba398093-e7fc-4f25-8f04-4265c3e55b54` | 11 | (71.12, 176.53) | 600–649 | sonnet |
| bench_io | `bench_io.kicad_sch` | Bench IO | `54b8f29e-9dcb-4e24-99b9-415a110b338a` | 12 | (109.22, 176.53) | 700–799 | sonnet |

Sheet symbol size 35.56 × 12.7 mm (the block sits in the free area below the RP2350 sheet symbol, x 33–145, y 152–192, verified clear against every root item's bounding box including label text; the root's R3/D1/D2/RX0/TX0 group starts at x ≈ 146). Each sheet file gets its own fresh uuid4 in its header (not the sheet-symbol uuid). Existing refdes maxima on the FC: R124, C80, D15, J30, U30, SW2, TP13, L5, Y1, JP6, IC6, BT1, H2, #PWR172, no #FLG — the blocks above avoid them.

## 6. Per-sheet requirements

Every sheet: A3, titled with a `(text …)` block naming the sheet and "PROVES FlatSat V1 — Phase 1", grouped into labelled functional areas, readable in the GUI (no overlapping text, labels on wire ends, junctions where three or more wires meet). Every part carries Reference, Value, Footprint, Datasheet (URL if known), Description, and `LCSC Part` where rule 5 allows. Unused IC pins get `no_connect` markers. Add test points (`Connector:TestPoint`, `TestPoint:TestPoint_Pad_D1.5mm`) on every bench-relevant rail. Use 0402 for signal passives and ≥0603/0805 for power passives, matching the FC.

### 6.1 `emulator_mcu` (opus) — RP2350 core

- RP2350A 60-QFN (`MCU_RaspberryPi_RP2350:RP2350_60QFN`, footprint `RP2350_60QFN_minimal:RP2350-QFN-60-1EP_7x7_P0.4mm_EP3.4x3.4mm_ThermalVias`, LCSC C42411118), W25Q128JVS (C97521) on QSPI, 12 MHz crystal ABM8-272-T3 (C20625731) with load caps and series R as on the FC/radio stick, 1V1 core-regulator inductor + caps (local rail `1V1_EMU`, not the FC's `+1V1`), per-rail decoupling, RUN pull-up, BOOTSEL/QSPI_SS arrangement mirroring the FC (R10/R91/D4/SW1 pattern) but exposed as `EMU_RUN` and `EMU_BOOTSEL_SW`. USB_DP/USB_DM pins wire directly to `EMU_USB_DP`/`EMU_USB_DM` — the 22 Ω series resistors live on bench_io only; no pull-ups (the RP2350 needs none).
- Template: start from a copy of `FlatSat_V1/RP2350.kicad_sch` (same project conventions; drop the APS1604M PSRAM and every FC global label per rule 8) and use `proves_radio_stick_V2` (scratch `refs/upgraded/proves_radio_stick_V2/`) for the standalone-MCU peripherals (regulator, buttons).
- Regulator: `VBUS_EMU` → 3.3 V → `3V3_EMU`. Worst-case current: RP2350 core+I/O at full PIO/USB activity (~100 mA), status/power LEDs, bench-header spare GPIO loads — the TCA4311As are on FC rails and do not count. An AP2112K-3.3 LDO (600 mA, `Regulator_Linear:AP2112K-3.3`) is sufficient; choose the radio stick's TPS62085RLTT + XFL4015-471MEC buck (C2070694 / C18221164) only if you want heritage with the radio stick. State the choice and the budget in the report. PWR_FLAGs per §4.2 ownership. Power LED on `3V3_EMU`, one status LED on a GPIO.
- GPIO map (document as a table in the report; firmware in Phase 3 depends on it). Budget: 14 I2C lines (`EMU_F1..F5_SDA/SCL`, `EMU_BATT_*`, `EMU_TOP_*`) + 6 sense (`EMU_F1..F5_SENSE`, `EMU_FC3V3_SENSE`) + `PYRO_INHIBIT_STATE` + 3 control outputs (`EMU_CTL_*`) + `EMU_UART_TX/RX` + `EMU_GPIO_SPARE0/1` + status LED = 29 of the RP2350A's 30 GPIO; reserve the 30th as `EMU_GPIO_RSVD` (test point only). PIO: 12 state machines for 7 I2C-slave channels — one per channel is the design assumption (plan §8 spike); group each channel's SDA/SCL on adjacent GPIOs. Keep GPIO26-29 (ADC-capable) for sense lines if it helps future analog monitoring.
- Firmware rules to record in the GPIO map: all `EMU_*_SDA/SCL` GPIOs are open-drain only (never driven high) so an off face is never back-powered through its pull-ups; every input or default-state-sensitive GPIO has its external pull ≤ 8.2 k on the other sheet (rule 10). Note in the report the phantom-power path into `3V3_EMU` through the RP2350 ESD diodes when the emulator is unpowered and the FC is on (~0.26 mA per pulled-up line from the 10 k pull-ups; acceptable, documented).
- The emulator must never source current into an unpowered FC: all connections to FC-side nets go through the TCA4311A front-ends on `solar_emulation` or through the open-drain FETs on `bench_io`; the sense inputs have 4.7 k series resistors on the other sheets.
- No `+3V3` power symbol or `+3V3` label anywhere on this sheet. Only `3V3_EMU`, `VBUS_EMU`, `1V1_EMU`.

### 6.2 `solar_emulation` (opus) — Face 0 real, Faces 1-5 / battery / top-cap emulated front-ends

- **Face 0 golden reference**: copy the sensor section of `solar_boards/XY_Face_V4` (scratch `refs/upgraded/XY_Face_V4/`, PDF `refs/XY_Face_V4.pdf`; the CSV `refs/bom/BOM-XY_Face_V4.csv` is actually the XY_Faces_V3 order — V4 has no BOM yet — and confirms TMP112 C28927, TCA4311ADGKR C130025, DRV2605LDGS C527464; for the VEML6031X00 use C3678616 from the Z_Face_V3 / top-cap BOMs): TCA4311ADGKR (VCC = `F0_PWR`; EN and READY each 10 k to VCC as on the face), TMP112 (ADD0 = GND → 0x48), VEML6031X00 (0x29), DRV2605LDGS (0x5A; EN to VCC, IN/TRIG to GND as on the face), the face's pull-ups/decoupling values. Face-side of the buffer = `F0_SDA`/`F0_SCL` (the FC bus). DRV2605L OUT+/OUT− → 2-pin 2.54 mm header for an external coil (real magnetorquer or lab inductor) with a **fitted** 0805 resistor across it equal to the XY_Face_V4 coil's DC resistance (on the face OUT+ and OUT− are one schematic net — the coil is copper — so estimate the value from the trace geometry in `solar_boards/XY_Face_V4/XY_Face_V4.kicad_pcb`; state the value and its dissipation at the DRV2605L's maximum RTP output; the resistor is removed when a real coil is plugged in). Do not attempt a PCB trace coil in Phase 1.
- **Faces 1-5 emulated**: five TCA4311ADGKR, each VCC = `Fn_PWR` (with the face's decoupling), EN/READY strapped as on the face, bus side = `Fn_SDA`/`Fn_SCL`, device side = `EMU_Fn_SDA`/`EMU_Fn_SCL` with 10 k pull-ups to that face's `Fn_PWR` (not to `3V3_EMU`). `EMU_Fn_SENSE` = `Fn_PWR` via 4.7 k.
- **Battery channel (mux ch4)**: one TCA4311A, VCC = `+3V3`, bus side `BATT_SDA`/`BATT_SCL`, device side `EMU_BATT_SDA`/`EMU_BATT_SCL` pulled to `+3V3`, replicating `battery_pack_v2` U3 (see `refs/battery_pack_v2.pdf`).
- **Top-cap channel (mux ch7)**: one TCA4311A, VCC = `+3V3`, bus side `SDA_Top`/`SCL_Top`, device side `EMU_TOP_SDA`/`EMU_TOP_SCL` pulled to `+3V3`, replicating `antenna_top_cap_v2c` U6 (`refs/antenna_top_cap_v2c.pdf`). `EMU_FC3V3_SENSE` = `+3V3` via 4.7 k.
- Confirm from the TCA4311A datasheet (https://www.ti.com/lit/ds/symlink/tca4311a.pdf) and record in the report: powered-off high-impedance I2C pins; EN low or VCC < UVLO (2.5 V) isolates IN from OUT; 1 V precharge through 100 k during UVLO; READY behaviour, so firmware can reproduce the real face's power-up timing.
- Do not add anything to `Fn_PWR` other than the buffer VCC, its decoupling, the two 10 k device-side pull-ups and the 4.7 k sense tap.

### 6.3 `solar_power_injection` (sonnet) — bench VSOLAR

- Two channels per D2. Each: 2-pin screw terminal (bench supply +/−, 5.08 mm pitch class) → fuse (IC6: R75 0.1 Ω → 1.0 A charge current; R71 634 k / R74 412 k → 8.38 V float; expect ≤ 1.2 A bench input at 12 V — fuse 2 A slow or 1.85 A polyfuse) → Schottky CDBA240LL-HF, LCSC C2886093 (SMA, 40 V 2 A, as ordered on XY_Face_V4; Z_Face_V3 ordered C8678 = MDD SS34, a 3 A substitute — either is acceptable, state which) → 2-pin jumper header (CH-A shunt fitted, CH-B open; open-header symbol per rule 9) → `VSOLAR`. Terminal − to `GND`. Local rails `VSOLAR_BENCH_A` / `VSOLAR_BENCH_B` (PWR_FLAG each, this sheet).
- Test points on each `VSOLAR_BENCH_x` and on `VSOLAR`. Text note giving the bench setting: supply **12–18 V, hard maximum 24 V** (INA219 U8 IN+ absolute maximum is 26 V on this net; LT3652 operating maximum 32 V; the eps_side note "9V to 40V" is wrong and must not be repeated — flag it in your report as an FC finding). Start-up needs VIN ≥ VFLOAT + 3.3 V = 11.7 V for the 8.38 V float programmed by R71/R74. Current limit per the fuse.
- Reverse-polarity is handled by the series Schottky; say so. If a TVS is fitted on `VSOLAR_BENCH_x`, choose a ≤ 22 V standoff SMA part and state the clamp voltage; PSU OVP is the primary protection. Otherwise omit and note.

### 6.4 `battery_protection_replica` (opus) — pack_v2 protection replica, bench PSU input, BQ25886 USB path

- Replica per D4: copy `battery_pack_v2` (scratch `refs/upgraded/battery_pack_v2/`, PDF, BOM `refs/bom/BOM-battery_pack_v2.csv`): R5460N208AA (pantry `flatsat:R5460N208AA`, C259714), 2× IRF7458 (pantry `flatsat:IRF7458`, C10879; the pack schematic's `IRF7404` symbol is stale metadata, the JLC BOM orders IRF7458), the pack's network exactly: VDD via R5 330 Ω + C9 0.1 µF, VC via R4 330 Ω + C8 0.1 µF, V− via R3 1 k + C7 0.1 µF, C5 0.1 µF between cell-negative and pack-negative, Q1 (DOUT) source at cell negative, Q2 (COUT) source at pack negative, common drain. Fetch the R5460 datasheet (https://www.nisshinbo-microdevices.co.jp/en/pdf/datasheet/r5460-ea.pdf); confirm pin functions (1 DOUT, 2 COUT, 3 V−, 4 VC, 5 VDD, 6 VSS) and the 2-cell application.
- **Net-name rule for this sheet:** the pack's cell-negative net (R5460 VSS, Q1 source, pack_v2 label `B-`) must be named **`VBAT_BENCH_N`** (local) on this sheet — never `B-`. The FC global `B-` is the pack's `PACK-` (Q2 source, after both FETs). The synthetic-midpoint divider and the R5460's R/C network all reference `VBAT_BENCH_N`, not `B-` and not `GND`. State this mapping in a text note next to the FETs.
- Bench input: 3-way screw terminal `B+ / MID / B−` (`VBAT_BENCH` power symbol on B+, `VBAT_BENCH_N` on B−; PWR_FLAG on both, this sheet). Synthetic midpoint: two equal **1.0 kΩ 0805 1 %** resistors B+→MID→B− (the R5460 datasheet p.17 Technical Notes requires < 1 kΩ effective series resistance at VC because VC conduction current shifts the detection voltage; 2 × 1 k gives 500 Ω Thevenin, 4.2 mA and 18 mW per resistor at 8.4 V), connected to the pack's R4 330 Ω + C8 0.1 µF into VC through a jumper header (shunt fitted by default; rule 9). The MID screw terminal lets a real dual supply override the divider (remove the divider shunt). Do NOT use high-value resistors. Record: R5460N208AA trips at 4.250 V/cell (8.50 V pack) and 2.400 V/cell (4.80 V), releases at 4.050/3.000 V; LT3652 float on this FC is 8.38 V, 120 mV below the OV trip, so the PSU setpoint must be ≤ 8.4 V.
- Output: B+ (through nothing) → `Dir_Chrg_In`; `VBAT_BENCH_N` → Q1 → Q2 → `B-`. Test points on `VBAT_BENCH`, `VBAT_BENCH_N`, `Dir_Chrg_In`, `B-`, both FET gates.
- BQ25886 USB path per D3, based on `antenna-board/debug_board_v1` (schematic only — never assembled; starting point, not precedent): power-only USB-C (`Connector:USB_C_Receptacle_USB2.0_16P` / `USB_C_Receptacle_HRO_TYPE-C-31-M-12`, C165948; 5.1 k CC pull-downs), the debug board's **input** reverse-blocking stage between USB VBUS and the charger VBUS pin (DZDH0401DW-7 + DMP4047LFDE-7 with the 1 M as drawn; both need LCSC), BQ25886RGE (needs LCSC; datasheet https://www.ti.com/lit/ds/symlink/bq25886.pdf) with **L = 1.0 µH SPM6530T-1R0M120 (C87572)** — not the 4.7 µH part, which is the FC's L5 — CVBUS 1 µF, CPMID 10 µF, **CSYS ≥ 44 µF on SYS (16 V X7R; the debug board omits this — add it, datasheet §9.2.2.3)**, CBAT 10 µF, REGN 4.7 µF, BTST 47 nF, ILIM 383 k, ICHGSET 5.7 k, VSET open (= 8.4 V), TS: fit the datasheet's REGN–TS–GND divider so TS sits mid-window (charging suspends if TS is out of range; the debug board leaves it open), CE open (internal 900 k pull-down enables charging), D+/D− shorted together (presents a DCP to the BC1.2 detector — quote the resulting IINDPM from Table 3) because this port carries no data. BAT → 2-pin jumper header (shunt removed by default) → `Dir_Chrg_In`. `VBUS_CHG` power symbol for its 5 V (PWR_FLAG, this sheet). Quote in the report: input-current and charge-current formulas (KILIM = 1110, ICHG from ICHGSET) and the no-battery behaviour (§8.3.7.1 STAT blinking as the BAT capacitance charges/discharges).
- Text notes: (1) jumper table for the three bench modes (PSU through replica; USB charger; both off); (2) PSU window **4.9 V ≤ V ≤ 8.4 V** (OV 4.250 V/cell trips COUT after 1 s; UV 2.400 V/cell trips DOUT after 128 ms and releases only above 3.000 V/cell = 6.0 V pack; discharge over-current at 0.200 V across the two IRF7458 ≈ 11 A). With VSOLAR injected, the LT3652 will source into the node and raise a non-sinking PSU to its 8.38 V float — 120 mV under the OV trip — so use a PSU that sinks or add a bleed load; if the replica opens COUT that is the expected pack behaviour, not a fault; (3) D11: never connect a battery pack to J14 while the bench PSU or the charger USB is connected.

### 6.5 `pyro_inhibit` (sonnet) — EN-line force-low switch + bench inhibit shunt headers

- Three small-signal Schottky diodes (`Diode:BAT54W`; KiCad's symbol is the 3-pin SC-70 / SOT-323 part with a no-connect centre pin, footprint `Package_TO_SOT_SMD:SOT-323_SC-70`, not SOD-123): anode on `Deploy1_EN`, `Heater_EN`, `Deploy2_EN` respectively (global labels, already promoted), cathodes commoned on a local net `PYRO_INH_COM`. Heater leg through a 2-pin jumper header, shunt fitted (D1; rule 9). Quote in a text note and the report: with the switch closed each EN node sits at VF(BAT54W) ≈ 0.28 V at 0.64 mA (≤ 240 mV @ 0.1 mA, ≤ 320 mV @ 1 mA, Nexperia BAT54W_SER) vs TPS4H160-Q1 VIL(max) 0.8 V, VIH(min) 2 V (§6.5 Logic Input; IN pins have 100–250 kΩ internal pull-downs).
- `PYRO_INH_COM` → SPST switch to `GND` (an on-board slide/toggle switch symbol `Switch:SW_SPST` with a PCB-mount toggle footprint you name, plus a parallel 2-pin header for a panel switch). Closed = inhibited = safe default.
- 100 k pull-up from `3V3_EMU` to `PYRO_INH_COM`; `PYRO_INHIBIT_STATE` = `PYRO_INH_COM` via 4.7 k (global label, to the emulator). "SAFE" LED: `3V3_EMU` → R → LED → `PYRO_INH_COM` (lit when the switch is closed). Note: LED lit = inhibit engaged AND emulator powered; the inhibit itself does not depend on `3V3_EMU`. Show in a note that the pull-up/LED can never raise an EN node (diodes reverse-biased).
- Six bench inhibit shunt headers (2-pin 2.54 mm, `Connector_Generic:Conn_01x02` or `Jumper:Jumper_2_Open` — never a `_Bridged` symbol, so the six existing nets stay separate in the netlist; footprint `PinHeader_1x02_P2.54mm_Vertical`), each in parallel with an existing break: `VBATT_SENSE`↔`INHIB_1` (JP INH_S1 ∥ J8), `INHIB_1`↔`IN_RBF` (INH_S2 ∥ J29), `VBATT_SENSE`↔`INHIB_2` (INH_P1 ∥ J7), `INHIB_2`↔`IN_RBF` (INH_P2 ∥ J10), `IN_RBF`↔`VBUSP` (RBF ∥ J20/J30), `B-`↔`GND` (ISS ∥ J15/J19). Label each with the connector it parallels. Note the current rating assumption (~3 A shunt) and that flight units never fit these.
- Test points on the three EN nets and `PYRO_INH_COM`. Text note referencing flight_controller_board#53 and D1.

### 6.6 `bench_io` (sonnet) — emulator USB-C + SWD, FC bench control, bench header

- Emulator USB-C: `Connector:USB_C_Receptacle_USB2.0_16P` / `USB_C_Receptacle_HRO_TYPE-C-31-M-12` (C165948), 5.1 k CC pull-downs (C25905), VBUS → `VBUS_EMU` (power symbol; PWR_FLAG, this sheet) with bulk cap, D+/D− → **22 Ω** series (C25092) → `EMU_USB_DP`/`EMU_USB_DM` (mirror the FC's J12/R7/R8 arrangement on the root sheet), shield to GND. Optional USB ESD array if a common part fits; otherwise omit and note.
- Emulator SWD: JST-SH 3-pin `BM03B-SRSS-TB` as the FC's J22 (footprint `Connector_JST:JST_SH_BM03B-SRSS-TB_1x03-1MP_P1.00mm_Vertical`, C160389): `EMU_SWCLK`, GND, `EMU_SWDIO`.
- Buttons: `EMU_RUN` → tact switch (KMR2, `BTN_KMR2_4.6X2.8` in the project's `FC_DEV_BOARD` footprint lib, C72443) → GND; `EMU_BOOTSEL_SW` → tact switch → GND.
- WDT_DISABLE toggle: SPST switch `WDT_DISABLE` → GND (mirrors the FC's J4 jumper; debug_board_v1 uses a switch — see `refs/debug_board_v1.pdf`).
- Three open-drain drivers (D8): N-FET such as 2N7002 (SOT-23; needs LCSC unless found in a repo BOM) per line, gate ← `EMU_CTL_FC_RESET` / `EMU_CTL_USBBOOT` / `EMU_CTL_WDT_DIS` through 1 k with a **4.7 k gate pull-down (≤ 8.2 k is required by RP2350 erratum E9 so that an unprogrammed / BOOTSEL-mode / unpowered emulator cannot float the gate to ~2 V; 100 k is not enough on A2 silicon)**, drain → `FC_RESET` / `USBBOOT` / `WDT_DISABLE`, source → GND. Note E9 and the A4 stepping in the sheet text. Note that `USBBOOT` on the FC reaches BOOTSEL through D4 + R10, exactly like SW1, and that `WDT_DISABLE` is the watchdog integrator node that J4 grounds.
- Bench header: 2×5 2.54 mm (`Connector_Generic:Conn_02x05_Odd_Even`): `3V3_EMU`, GND, `EMU_UART_TX`, `EMU_UART_RX`, `EMU_GPIO_SPARE0`, `EMU_GPIO_SPARE1`, `FC_RESET`, `USBBOOT`, `WDT_DISABLE`, GND. Pin-1 marking note.

## 7. Format, tools, validation procedure

Read first: `FlatSat_V1/tools/kicad10_sch_primer.md` (verbatim format samples from this project), `tools/baseline/connector_nets.md` (every connector pin → net on the FC, key IC pin maps), the pantry index at `<scratch>/pantry/INDEX.md`, and `01_brief_critique.md` (the datasheet facts and URLs it cites are the ones to reuse).

File format essentials (KiCad 10, `(version 20260306)`): tabs; every placed item has a uuid; a symbol instance embeds nothing but references a `(symbol "Lib:Name" …)` definition that **must** exist in the sheet's `(lib_symbols …)`; pin positions are the lib pin `(at x y)` transformed by the instance's rotation/mirror with y flipped (see `tools/sch_lint.py` for the exact transform); wires must end exactly on pins/labels/junctions; sub-sheet files have **no** `(sheet_instances …)` and no trailing `(embedded_fonts no)` (match `load_switches.kicad_sch`); every instance carries `(instances (project "FlatSat_V1" (path "/<root uuid>/<your sheet uuid>" (reference "R2xx") (unit 1))))`.

Recommended way to write the sheet: a small Python generator (save it as `FlatSat_V1/tools/gen/<key>_gen.py`) with helpers that place a symbol from a pantry block, compute its pin coordinates, and emit wires/labels at those coordinates. Hand-typing 10 000 lines of S-expressions is how errors happen. Get symbol blocks with `python3 FlatSat_V1/tools/get_symbol.py "Lib:Name" --sch-dirs <scratch>/refs/upgraded` (or copy from the pantry). Use `uuid.uuid4()` for every uuid.

Validation loop (run from `FlatSat_V1/`):

```
python3 tools/sch_lint.py <sheet>.kicad_sch --project FlatSat_V1 --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/<sheet uuid> --refdes-block <lo>-<hi>
SCRATCH=<your scratch dir>/harness_<key> tools/harness_erc.sh "<Sheetname>"
```

`harness_erc.sh` copies the project to scratch, adds every new sheet that exists and parses, runs ERC + netlist, prints the ERC delta vs the Rev2 baseline (library-metadata noise excluded), your sheet's violations, and the netlist diff (which existing nets your sheet reached, which components were added). Done means: lint 0 errors; no ERC **errors** on your sheet; no new ERC errors elsewhere caused by your sheet; the only warnings left are `single_global_label` for contract nets whose partner sheet is not on disk yet; the netlist diff shows exactly the existing nets §4 says you touch (plus the eight promotions, which are already in the baseline comparison as renames) and nothing else.

Also export your sheet to PDF and look at it: `kicad-cli sch export pdf --output <scratch>/<key>.pdf <harness>/proj/FlatSat_V1.kicad_sch` then Read the PDF page for your sheet — overlapping labels and off-pin wires are obvious there.

## 8. Deliverables per sheet agent

1. `FlatSat_V1/<key>.kicad_sch` — the sheet, passing §7.
2. `FlatSat_V1/tools/gen/<key>_gen.py` — the generator (if you used one).
3. `docs/flatsat/2026-09-14_phase1_schematic/sheet_<key>.md` — the report: purpose; block description; parts table (ref, value, footprint, LCSC or "needs LCSC", source of the number); interface nets used (existing and new, exact names); GPIO map (emulator) / jumper table (others); datasheet facts you relied on (with section numbers and URLs); assumptions and open questions for the reviewer; lint/ERC/netlist-diff results pasted; deviations from this brief and why.

Return value to the orchestrator (structured): sheet file path, report path, refdes used, global labels used (existing / new), ERC error count on the sheet, remaining warnings, open questions.

## 9. Integrator deliverables

`FlatSat_V1/FlatSat_V1.kicad_sch` with the six sheet symbols (table §5, plus a text block "PROVES FlatSat V1 additions — see docs/flatsat/"), confirmation that the §4.3 promotions still read as eight pure renames, `symbols/flatsat.kicad_sym` populated with every `flatsat:*` symbol used (so the GUI resolves them), full-project ERC with zero errors attributable to new sheets and every remaining warning triaged in `docs/flatsat/2026-09-14_phase1_schematic/integration_report.md`, and `connector_trace.md`: every FC connector (J1–J30, RF1, J12, J16, J18, J22) pin → net → FlatSat destination (new sheet + refdes, "unchanged: external connector kept", or "unpopulated"). Netlist diff vs Rev2 must show: no existing net lost pins; the eight promotions as pure renames; additions only.

## 10. Phase exit criteria (from the plan §7)

ERC clean on all six new sheets (no errors; warnings triaged); every connector-facing net on the FC board traced to its new destination; heater-channel and per-face VSOLAR scope decided (D1, D2) and reflected in the sheets; S-band approach recorded (D5). Then the Fable review-and-fix round, then layout.

## 11. Post-capture PM rulings (rev 2.1, 2026-09-14, after the capture workflow and its two checker rounds)

These answer the open items the implementers, integrator and checker raised (`capture_result.json`, `integration_report.md` O1–O16). They supersede the earlier text where they conflict. The review round treats them as decisions, not findings.

| # | Item | Ruling |
|---|---|---|
| R1 | O1 `VBAT_BENCH` power symbol + PWR_FLAG (§4.2, §6.4) | **Struck.** J500 pin 1 *is* `Dir_Chrg_In` (no series element, by design); the bench B+ carries no separate name or flag. No third jumper. The pantry block `flatsat_VBAT_BENCH.sexp` is unused; `symbols/flatsat.kicad_sym` correctly omits it. |
| R2 | `load_switches.kicad_sch` AP22652 pin 6 retyped `output` → `power_out` (one token, flight-heritage sheet) | **Accepted for FlatSat_V1.** Metadata only; netlist/PCB/BOM unchanged; it is what a correct library symbol would carry and it is why the TCA4311A `power_in` VCC pins on `Fn_PWR` now pass ERC. Forwarded to the upstream FC project as finding F2/F3 (`integration_report.md` §7a). §4.2's premise that the FC already had power-output pins on `Fn_PWR`/`+3V3` was wrong (critique item 7 and this ruling correct it): the Rev2 `power_pin_not_driven` on `+3V3` (#PWR029) is the same defect on U10 pin 1 and stays as a baseline error. |
| R3 | Integrator edits to `emulator_mcu`, `solar_emulation`, `solar_power_injection`, `pyro_inhibit` (+ generators) outside its declared writable set (O15) | **Acknowledged, no rework.** Every edit went into the generator too; `integration_report.md` §1.2 is the record. |
| R4 | BQ25886 ILIM "383 k" in §6.4 (units error; datasheet 383 Ω = 2.9 A) | **750 Ω (1.48 A) accepted** for a 5 V / 2 A bench USB source. Note it on the sheet (done). |
| R5 | BQ25886 CSYS 2 × 22 µF 25 V X5R 0805 = ~24 µF effective at 8.4 V vs the datasheet's 44 µF minimum | **Fix in the review round:** add a third 22 µF or move to a lower-derating case/rating so ≥ 44 µF effective at 8.4 V; record the derated value on the sheet. |
| R6 | O13 `PYRO_INHIBIT_STATE` in the armed state sees 104.7 k to `3V3_EMU` (R600 100 k + R601 4.7 k), above the RP2350-E9 8.2 k limit | **Fix in the review round:** R600 100 k → 4.7 k (0.7 mA through the closed switch; diodes stay reverse-biased when the node is at 3.3 V). Re-check the SAFE-LED note and the pull-up wording on the sheet. |
| R7 | O14 emulated-channel device-side pull-ups 10 k (parity with XY_Face_V4) vs E9 | **4.7 k allowed on the emulated channels** (faces 1–5 device side, BATT, TOP): with the face off the pad is then pulled to 0 V through ≤ 8.2 k, satisfying rule 10 in hardware instead of by firmware. Face 0 (golden reference) keeps the face's 10 k. Fixer's choice whether to apply now (preferred) or leave the firmware rule; record either way. |
| R8 | D2 wording "CH-B footprint-only": the sheet populates J401/F401/D401/JP401 with only the JP401 shunt open | **Accepted as built** (parts are cheap; only the shunt differs). D2 now reads "CH-B populated, shunt open". |
| R9 | No TVS on `VSOLAR_BENCH_A/B`; PTC re-spec to Littelfuse 2920L185DR (C207086) with the 24 V hard-maximum note restored | **Accepted.** Bench PSU OVP is the primary protection. |
| R10 | AP2112K-3.3 (C51118, live-verified, no PROVES precedent) vs the radio stick's TPS62085 buck | **Accepted.** LDO stays; the buck is the recorded alternative. |
| R11 | Face-0 coil dummy load R304 43 Ω 2010 (computed from the XY_Face_V4 PCB coil) and the AP22653 U19 current-limit headroom for the 77 mA burst | **Accepted with the ≤ 50 % duty note.** Reviewer: check U19's current limit against the burst; if marginal, raise R304 and record. |
| R12 | Outstanding LCSC numbers (O9) | **Deferred to the layout-phase supply-chain pass** (the repo's existing procedure). No guessing now. |
| R13 | O6 `VBUS_EMU` bulk ≈ 11 µF nominal vs USB 2.0 §7.2.4.1 10 µF | **Accepted** (radio-stick precedent). |
| R14 | O7/O8 library-metadata warnings (`pin_to_pin` with Unspecified pins, `mainboard` lib not in table) | **Accepted as pre-existing FC convention**; not Phase 1 scope. |
| R15 | O10 eps_side note "VSOLAR 9V to 40V" | **FC finding, reported not repeated.** Stays untouched on the flight sheet. |

Corrected part fact for reviewers: `Diode:BAT54W` is a 3-pin SC-70 (SOT-323) symbol/footprint (§6.5 updated). The `flatsat:VSOLAR_BENCH` Description string inherited from the pantry block ("…name \"+3V3\"") is a cosmetic artefact (O12); fix it in the pantry and the project lib together if a fixer touches that file anyway.
