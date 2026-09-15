# FlatSat V1 — connector trace (Phase 1 integration)

Generated from the integrated netlist `FlatSat_V1.kicad_sch` → kicadxml, 2026-09-14, by the integrator.
Baseline for comparison: `FlatSat_V1/tools/baseline/netlist.kicadxml` (FC_V5e_Production_Rev2).
Brief §9 deliverable: every FC connector pin → net → FlatSat destination.

**How to read the Destination column**

- `<refdes>.<pin> (<sheet>)` — a new Phase-1 sheet lands on this net at that pin.
- *unchanged: external connector kept* — the pin keeps its FC net and no new sheet touches it; the connector stays populated and is still wired to the outside world exactly as on the FC.
- *unpopulated* — the reference designator exists on the FC board but has no pins in the netlist (no symbol placed).

Nets printed in `code` are the **integrated** net names. Where the §4.3 promotion renamed a net, the old
Rev2 name is shown after an arrow, e.g. `` `B-` `` ← `/Power Systems/B-`.

## 1. Connector pin → net → FlatSat destination

### J1 — Conn_01x06 — `Connector_Molex:Molex_Pico-Lock_504050-0691_1x06-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 2 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `F4_PWR` | solar_emulation: 8 pins on C313, R340, R341, R342, R343, R344 …(8 refs) |
| 5 | `F4_SCL` | U313.3 (solar_emulation) |
| 6 | `F4_SDA` | U313.6 (solar_emulation) |

### J2 — Conn_01x06 — `Connector_Molex:Molex_Pico-Lock_504050-0691_1x06-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 2 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `F5_PWR` | solar_emulation: 8 pins on C314, R350, R351, R352, R353, R354 …(8 refs) |
| 5 | `F5_SCL` | U314.3 (solar_emulation) |
| 6 | `F5_SDA` | U314.6 (solar_emulation) |

### J3 — Life Makes Lemonade — `Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical` — FC sheet /

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 2 | `SCL1` | *unchanged: external connector kept* |
| 3 | `SDA1` | *unchanged: external connector kept* |
| 4 | `RX0` | *unchanged: external connector kept* |
| 5 | `TX0` | *unchanged: external connector kept* |
| 6 | `+3V3` | shared rail — solar_emulation (+13 pins); see §2 |

### J4 — Conn_01x02 — `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` — FC sheet /Watchdog Circuit/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `WDT_DISABLE` | J703.9 (bench_io)<br>Q703.3 (bench_io)<br>SW703.1 (bench_io) |
| 2 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J5 — BM04B-SRSS-TB(LF)(SN) — `FC_DEV_BOARD:JST_BM04B-SRSS-TB(LF)(SN)` — FC sheet /

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 2 | `PAYLOAD_PWR` | *unchanged: external connector kept* |
| 3 | `SDA1` | *unchanged: external connector kept* |
| 4 | `SCL1` | *unchanged: external connector kept* |
| S1 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| S2 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J6 — Conn_01x06 — `Connector_Molex:Molex_Pico-Lock_504050-0691_1x06-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 2 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `F0_PWR` | solar_emulation: 14 pins on C300, C301, C302, C303, R300, R301 …(13 refs) |
| 5 | `F0_SCL` | U300.3 (solar_emulation) |
| 6 | `F0_SDA` | U300.6 (solar_emulation) |

### J7 — INHIBIT_P1 — `Connector_Hirose:Hirose_DF11-4DP-2DSA_2x02_P2.00mm_Vertical` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `VBATT_SENSE` ← `/Power Systems/VBATT_SENSE` | JP602.1 (pyro_inhibit)<br>JP604.1 (pyro_inhibit) |
| 2 | `INHIB_2` ← `/Power Systems/INHIB_2` | JP604.2 (pyro_inhibit)<br>JP605.1 (pyro_inhibit) |
| 3 | `VBATT_SENSE` ← `/Power Systems/VBATT_SENSE` | JP602.1 (pyro_inhibit)<br>JP604.1 (pyro_inhibit) |
| 4 | `INHIB_2` ← `/Power Systems/INHIB_2` | JP604.2 (pyro_inhibit)<br>JP605.1 (pyro_inhibit) |

### J8 — INHIBIT_S1_Picolock — `Connector_Molex:Molex_Pico-Lock_504050-0291_1x02-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `INHIB_1` ← `/Power Systems/INHIB_1` | JP602.2 (pyro_inhibit)<br>JP603.1 (pyro_inhibit) |
| 2 | `VBATT_SENSE` ← `/Power Systems/VBATT_SENSE` | JP602.1 (pyro_inhibit)<br>JP604.1 (pyro_inhibit) |

### J9 — Conn_01x06 — `Connector_Molex:Molex_Pico-Lock_504050-0691_1x06-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 2 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `F1_PWR` | solar_emulation: 8 pins on C310, R310, R311, R312, R313, R314 …(8 refs) |
| 5 | `F1_SCL` | U310.3 (solar_emulation) |
| 6 | `F1_SDA` | U310.6 (solar_emulation) |

### J10 — INHIBIT_P2 — `Connector_Hirose:Hirose_DF11-4DP-2DSA_2x02_P2.00mm_Vertical` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `INHIB_2` ← `/Power Systems/INHIB_2` | JP604.2 (pyro_inhibit)<br>JP605.1 (pyro_inhibit) |
| 2 | `IN_RBF` ← `/Power Systems/IN_RBF` | JP603.2 (pyro_inhibit)<br>JP605.2 (pyro_inhibit)<br>JP606.1 (pyro_inhibit) |
| 3 | `INHIB_2` ← `/Power Systems/INHIB_2` | JP604.2 (pyro_inhibit)<br>JP605.1 (pyro_inhibit) |
| 4 | `IN_RBF` ← `/Power Systems/IN_RBF` | JP603.2 (pyro_inhibit)<br>JP605.2 (pyro_inhibit)<br>JP606.1 (pyro_inhibit) |

### J11 — Conn_01x06 — `Connector_Molex:Molex_Pico-Lock_504050-0691_1x06-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 2 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `F2_PWR` | solar_emulation: 8 pins on C311, R320, R321, R322, R323, R324 …(8 refs) |
| 5 | `F2_SCL` | U311.3 (solar_emulation) |
| 6 | `F2_SDA` | U311.6 (solar_emulation) |

### J12 — USB_C_Receptacle_USB2.0_16P — `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12` — FC sheet /

| pin | net | FlatSat destination |
|---|---|---|
| A1 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| A4 | `VBUS` | *unchanged: external connector kept* |
| A5 | `Net-(J12-CC1)` | *unchanged: external connector kept* |
| A6 | `USB_D+` | *unchanged: external connector kept* |
| A7 | `USB_D-` | *unchanged: external connector kept* |
| A8 | *(no net — pin unconnected)* | *unchanged: external connector kept* |
| A9 | `VBUS` | *unchanged: external connector kept* |
| A12 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| B1 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| B4 | `VBUS` | *unchanged: external connector kept* |
| B5 | `Net-(J12-CC2)` | *unchanged: external connector kept* |
| B6 | `USB_D+` | *unchanged: external connector kept* |
| B7 | `USB_D-` | *unchanged: external connector kept* |
| B8 | *(no net — pin unconnected)* | *unchanged: external connector kept* |
| B9 | `VBUS` | *unchanged: external connector kept* |
| B12 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| S1 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J13 — Conn_01x06 — `Connector_Molex:Molex_Pico-Lock_504050-0691_1x06-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 2 | `VSOLAR` | JP400.2 (solar_power_injection)<br>JP401.2 (solar_power_injection)<br>TP401.1 (solar_power_injection) |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `F3_PWR` | solar_emulation: 8 pins on C312, R330, R331, R332, R333, R334 …(8 refs) |
| 5 | `F3_SCL` | U312.3 (solar_emulation) |
| 6 | `F3_SDA` | U312.6 (solar_emulation) |

### J14 — Battery Input — `Connector_Hirose:Hirose_DF11-12DP-2DSA_2x06_P2.00mm_Vertical` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `Dir_Chrg_In` | J500.1 (battery_protection_replica)<br>JP500.2 (battery_protection_replica)<br>JP510.2 (battery_protection_replica)<br>R500.1 (battery_protection_replica)<br>TP500.1 (battery_protection_replica) |
| 2 | `B-` ← `/Power Systems/B-` | battery_protection_replica: 7 pins on C503, Q501, R502, R505, TP502<br>pyro_inhibit: 1 pins on JP607 |
| 3 | `Dir_Chrg_In` | J500.1 (battery_protection_replica)<br>JP500.2 (battery_protection_replica)<br>JP510.2 (battery_protection_replica)<br>R500.1 (battery_protection_replica)<br>TP500.1 (battery_protection_replica) |
| 4 | `B-` ← `/Power Systems/B-` | battery_protection_replica: 7 pins on C503, Q501, R502, R505, TP502<br>pyro_inhibit: 1 pins on JP607 |
| 5 | `Dir_Chrg_In` | J500.1 (battery_protection_replica)<br>JP500.2 (battery_protection_replica)<br>JP510.2 (battery_protection_replica)<br>R500.1 (battery_protection_replica)<br>TP500.1 (battery_protection_replica) |
| 6 | `B-` ← `/Power Systems/B-` | battery_protection_replica: 7 pins on C503, Q501, R502, R505, TP502<br>pyro_inhibit: 1 pins on JP607 |
| 7 | `Dir_Chrg_In` | J500.1 (battery_protection_replica)<br>JP500.2 (battery_protection_replica)<br>JP510.2 (battery_protection_replica)<br>R500.1 (battery_protection_replica)<br>TP500.1 (battery_protection_replica) |
| 8 | `B-` ← `/Power Systems/B-` | battery_protection_replica: 7 pins on C503, Q501, R502, R505, TP502<br>pyro_inhibit: 1 pins on JP607 |
| 9 | `Dir_Chrg_In` | J500.1 (battery_protection_replica)<br>JP500.2 (battery_protection_replica)<br>JP510.2 (battery_protection_replica)<br>R500.1 (battery_protection_replica)<br>TP500.1 (battery_protection_replica) |
| 10 | `BATT_SDA` | U315.6 (solar_emulation) |
| 11 | `+3V3` | shared rail — solar_emulation (+13 pins); see §2 |
| 12 | `BATT_SCL` | U315.3 (solar_emulation) |

### J15 — ISS_INHIBIT_Picolock — `Connector_Molex:Molex_Pico-Lock_504050-0291_1x02-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `B-` ← `/Power Systems/B-` | battery_protection_replica: 7 pins on C503, Q501, R502, R505, TP502<br>pyro_inhibit: 1 pins on JP607 |
| 2 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J16 — DEBUG — `Connector_Hirose:Hirose_DF11-12DP-2DSA_2x06_P2.00mm_Vertical` — FC sheet /

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `USBBOOT` | J703.8 (bench_io)<br>Q702.3 (bench_io) |
| 2 | `FC_RESET` | J703.7 (bench_io)<br>Q701.3 (bench_io) |
| 3 | `USB_D+` | *unchanged: external connector kept* |
| 4 | `USB_D-` | *unchanged: external connector kept* |
| 5 | `SDA_Top` | U316.6 (solar_emulation) |
| 6 | `+3V3` | shared rail — solar_emulation (+13 pins); see §2 |
| 7 | `SCL_Top` | U316.3 (solar_emulation) |
| 8 | `Dir_Chrg_In` | J500.1 (battery_protection_replica)<br>JP500.2 (battery_protection_replica)<br>JP510.2 (battery_protection_replica)<br>R500.1 (battery_protection_replica)<br>TP500.1 (battery_protection_replica) |
| 9 | `WDT_DISABLE` | J703.9 (bench_io)<br>Q703.3 (bench_io)<br>SW703.1 (bench_io) |
| 10 | `DEPLOY1` | *unchanged: external connector kept* |
| 11 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 12 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J17 — unpopulated

Not in the netlist: no symbol is placed on any sheet. Nothing added in Phase 1.

### J18 — Payload — `Connector_Hirose:Hirose_DF11-12DP-2DSA_2x06_P2.00mm_Vertical` — FC sheet /

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `PAYLOAD_PWR` | *unchanged: external connector kept* |
| 2 | `PAYLOAD_PWR` | *unchanged: external connector kept* |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 5 | `TX0` | *unchanged: external connector kept* |
| 6 | `RX0` | *unchanged: external connector kept* |
| 7 | `PAYLOAD_BATT` | *unchanged: external connector kept* |
| 8 | `PAYLOAD_BATT` | *unchanged: external connector kept* |
| 9 | `TX1` | *unchanged: external connector kept* |
| 10 | `RX1` | *unchanged: external connector kept* |
| 11 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 12 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J19 — ISS_INHIBIT — `Connector_Hirose:Hirose_DF11-4DP-2DSA_2x02_P2.00mm_Vertical` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `B-` ← `/Power Systems/B-` | battery_protection_replica: 7 pins on C503, Q501, R502, R505, TP502<br>pyro_inhibit: 1 pins on JP607 |
| 2 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 3 | `B-` ← `/Power Systems/B-` | battery_protection_replica: 7 pins on C503, Q501, R502, R505, TP502<br>pyro_inhibit: 1 pins on JP607 |
| 4 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J20 — RBF_Inhibit — `Connector_Hirose:Hirose_DF11-4DP-2DSA_2x02_P2.00mm_Vertical` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `IN_RBF` ← `/Power Systems/IN_RBF` | JP603.2 (pyro_inhibit)<br>JP605.2 (pyro_inhibit)<br>JP606.1 (pyro_inhibit) |
| 2 | `VBUSP` | JP606.2 (pyro_inhibit) |
| 3 | `IN_RBF` ← `/Power Systems/IN_RBF` | JP603.2 (pyro_inhibit)<br>JP605.2 (pyro_inhibit)<br>JP606.1 (pyro_inhibit) |
| 4 | `VBUSP` | JP606.2 (pyro_inhibit) |

### J21 — Heater Output — `Connector_Molex:Molex_Pico-Lock_504050-0491_1x04-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `Heater Output` | *unchanged: external connector kept* |
| 2 | `Heater Output` | *unchanged: external connector kept* |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J22 — SWD Port — `Connector_JST:JST_SH_BM03B-SRSS-TB_1x03-1MP_P1.00mm_Vertical` — FC sheet /

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `SWCLK` | *unchanged: external connector kept* |
| 2 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 3 | `SWDIO` | *unchanged: external connector kept* |

### J23 — Aux Deploy 1 — `easyeda2kicad:CONN-SMD_4P-P2.00_DF11CZ-4DP-2V-27` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `DEPLOY1_AUX` | *unchanged: external connector kept* |
| 2 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 3 | `DEPLOY1_AUX` | *unchanged: external connector kept* |
| 4 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J24 — Deploy 2 — `Connector_Molex:Molex_Pico-Lock_504050-0491_1x04-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `DEPLOY2` | *unchanged: external connector kept* |
| 2 | `DEPLOY2` | *unchanged: external connector kept* |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |

### J25 — unpopulated

Not in the netlist: no symbol is placed on any sheet. Nothing added in Phase 1.

### J26 — unpopulated

Not in the netlist: no symbol is placed on any sheet. Nothing added in Phase 1.

### J27 — unpopulated

Not in the netlist: no symbol is placed on any sheet. Nothing added in Phase 1.

### J28 — unpopulated

Not in the netlist: no symbol is placed on any sheet. Nothing added in Phase 1.

### J29 — INHIBIT_S2_Picolock — `Connector_Molex:Molex_Pico-Lock_504050-0291_1x02-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `IN_RBF` ← `/Power Systems/IN_RBF` | JP603.2 (pyro_inhibit)<br>JP605.2 (pyro_inhibit)<br>JP606.1 (pyro_inhibit) |
| 2 | `INHIB_1` ← `/Power Systems/INHIB_1` | JP602.2 (pyro_inhibit)<br>JP603.1 (pyro_inhibit) |

### J30 — RBF_Picolock — `Connector_Molex:Molex_Pico-Lock_504050-0291_1x02-1MP_P1.50mm_Horizontal` — FC sheet /Power Systems/

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `VBUSP` | JP606.2 (pyro_inhibit) |
| 2 | `IN_RBF` ← `/Power Systems/IN_RBF` | JP603.2 (pyro_inhibit)<br>JP605.2 (pyro_inhibit)<br>JP606.1 (pyro_inhibit) |

### RF1 — KH-MMCX-Z — `easyeda2kicad:MMCX-TH_KH-MMCX-Z` — FC sheet /

| pin | net | FlatSat destination |
|---|---|---|
| 1 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 2 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 3 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 4 | `GND` | shared rail — emulator_mcu, solar_emulation, solar_power_injection, battery_protection_replica, pyro_inhibit, bench_io (+110 pins); see §2 |
| 5 | `/RF1_ANT` | *unchanged: external connector kept* |

### RF2 — unpopulated

Not in the netlist: no symbol is placed on any sheet. Nothing added in Phase 1.

## 2. Global-net carrier table

Every net promoted in brief §4.3, every new cross-sheet global from brief §4.2, and every existing FC
global a new sheet reaches. "Sheets" lists each sheet that carries a pin on the net and its pin count.

### 2a. The eight §4.3 promotions (local → global). Membership check vs Rev2 in §3 of integration_report.md.

| net | kind | pins now | sheets (pin count) | was, in Rev2 |
|---|---|---|---|---|
| `Deploy1_EN` | promoted global | 5 | load_switches (3), pyro_inhibit (2) | `/Power Systems/Load Switches/Deploy1_EN` — 3 pins, all retained |
| `Heater_EN` | promoted global | 4 | load_switches (2), pyro_inhibit (2) | `/Power Systems/Load Switches/Heater_EN` — 2 pins, all retained |
| `Deploy2_EN` | promoted global | 4 | load_switches (2), pyro_inhibit (2) | `/Power Systems/Load Switches/Deploy2_EN` — 2 pins, all retained |
| `B-` | promoted global | 15 | eps_side (7), battery_protection_replica (7), pyro_inhibit (1) | `/Power Systems/B-` — 7 pins, all retained |
| `VBATT_SENSE` | promoted global | 12 | eps_side (10), pyro_inhibit (2) | `/Power Systems/VBATT_SENSE` — 10 pins, all retained |
| `INHIB_1` | promoted global | 4 | eps_side (2), pyro_inhibit (2) | `/Power Systems/INHIB_1` — 2 pins, all retained |
| `INHIB_2` | promoted global | 6 | eps_side (4), pyro_inhibit (2) | `/Power Systems/INHIB_2` — 4 pins, all retained |
| `IN_RBF` | promoted global | 9 | eps_side (6), pyro_inhibit (3) | `/Power Systems/IN_RBF` — 6 pins, all retained |

### 2b. New cross-sheet globals (brief §4.2)

| net | kind | pins | sheets (pin count) | note |
|---|---|---|---|---|
| `3V3_EMU` | new global | 35 | emulator_mcu (32), pyro_inhibit (2), bench_io (1) |  |
| `VBUS_EMU` | new global | 11 | emulator_mcu (5), bench_io (6) |  |
| `PYRO_INHIBIT_STATE` | new global | 2 | emulator_mcu (1), pyro_inhibit (1) |  |
| `EMU_F1_SDA` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F1_SCL` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F2_SDA` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F2_SCL` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F3_SDA` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F3_SCL` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F4_SDA` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F4_SCL` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F5_SDA` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F5_SCL` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_BATT_SDA` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_BATT_SCL` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_TOP_SDA` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_TOP_SCL` | new global | 3 | emulator_mcu (1), solar_emulation (2) |  |
| `EMU_F1_SENSE` | new global | 2 | emulator_mcu (1), solar_emulation (1) |  |
| `EMU_F2_SENSE` | new global | 2 | emulator_mcu (1), solar_emulation (1) |  |
| `EMU_F3_SENSE` | new global | 2 | emulator_mcu (1), solar_emulation (1) |  |
| `EMU_F4_SENSE` | new global | 2 | emulator_mcu (1), solar_emulation (1) |  |
| `EMU_F5_SENSE` | new global | 2 | emulator_mcu (1), solar_emulation (1) |  |
| `EMU_FC3V3_SENSE` | new global | 2 | emulator_mcu (1), solar_emulation (1) |  |
| `EMU_CTL_FC_RESET` | new global | 2 | emulator_mcu (1), bench_io (1) |  |
| `EMU_CTL_USBBOOT` | new global | 2 | emulator_mcu (1), bench_io (1) |  |
| `EMU_CTL_WDT_DIS` | new global | 2 | emulator_mcu (1), bench_io (1) |  |
| `EMU_USB_DP` | new global | 2 | emulator_mcu (1), bench_io (1) |  |
| `EMU_USB_DM` | new global | 2 | emulator_mcu (1), bench_io (1) |  |
| `EMU_SWCLK` | new global | 2 | emulator_mcu (1), bench_io (1) |  |
| `EMU_SWDIO` | new global | 2 | emulator_mcu (1), bench_io (1) |  |
| `EMU_RUN` | new global | 4 | emulator_mcu (2), bench_io (2) |  |
| `EMU_BOOTSEL_SW` | new global | 3 | emulator_mcu (1), bench_io (2) |  |
| `EMU_UART_TX` | new global | 2 | emulator_mcu (1), bench_io (1) |  |
| `EMU_UART_RX` | new global | 3 | emulator_mcu (2), bench_io (1) |  |
| `EMU_GPIO_SPARE0` | new global | 3 | emulator_mcu (2), bench_io (1) |  |
| `EMU_GPIO_SPARE1` | new global | 3 | emulator_mcu (2), bench_io (1) |  |
| `VSOLAR_BENCH_A` | new global | 3 | solar_power_injection (3) |  |
| `VSOLAR_BENCH_B` | new global | 3 | solar_power_injection (3) |  |
| `VBUS_CHG` | new global | 8 | battery_protection_replica (8) |  |

### 2c. Existing FC globals reached by a new sheet (brief §4.1)

| net | kind | pins | sheets (pin count) | note |
|---|---|---|---|---|
| `GND` | existing FC global | 311 | root (FlatSat_V1.kicad_sch) (62), eps_side (53), load_switches (51), RP2350 (26), watchdog (9), emulator_mcu (34), solar_emulation (26), solar_power_injection (2), battery_protection_replica (23), pyro_inhibit (3), bench_io (22) | Rev2 201 pins → 311; +110, none lost |
| `+3V3` | existing FC global | 119 | root (FlatSat_V1.kicad_sch) (47), eps_side (14), load_switches (14), RP2350 (31), solar_emulation (13) | Rev2 106 pins → 119; +13, none lost |
| `VSOLAR` | existing FC global | 17 | eps_side (14), solar_power_injection (3) | Rev2 14 pins → 17; +3, none lost |
| `Dir_Chrg_In` | existing FC global | 13 | root (FlatSat_V1.kicad_sch) (1), eps_side (7), battery_protection_replica (5) | Rev2 8 pins → 13; +5, none lost |
| `VBUSP` | existing FC global | 23 | eps_side (14), load_switches (3), watchdog (5), pyro_inhibit (1) | Rev2 22 pins → 23; +1, none lost |
| `FC_RESET` | existing FC global | 8 | root (FlatSat_V1.kicad_sch) (4), RP2350 (2), bench_io (2) | Rev2 6 pins → 8; +2, none lost |
| `USBBOOT` | existing FC global | 6 | root (FlatSat_V1.kicad_sch) (4), bench_io (2) | Rev2 4 pins → 6; +2, none lost |
| `WDT_DISABLE` | existing FC global | 12 | root (FlatSat_V1.kicad_sch) (1), watchdog (8), bench_io (3) | Rev2 9 pins → 12; +3, none lost |
| `F0_PWR` | existing FC global | 17 | eps_side (1), load_switches (2), solar_emulation (14) | Rev2 3 pins → 17; +14, none lost |
| `F0_SDA` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F0_SCL` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F1_PWR` | existing FC global | 11 | eps_side (1), load_switches (2), solar_emulation (8) | Rev2 3 pins → 11; +8, none lost |
| `F1_SDA` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F1_SCL` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F2_PWR` | existing FC global | 11 | eps_side (1), load_switches (2), solar_emulation (8) | Rev2 3 pins → 11; +8, none lost |
| `F2_SDA` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F2_SCL` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F3_PWR` | existing FC global | 11 | eps_side (1), load_switches (2), solar_emulation (8) | Rev2 3 pins → 11; +8, none lost |
| `F3_SDA` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F3_SCL` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F4_PWR` | existing FC global | 11 | eps_side (1), load_switches (2), solar_emulation (8) | Rev2 3 pins → 11; +8, none lost |
| `F4_SDA` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F4_SCL` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F5_PWR` | existing FC global | 11 | eps_side (1), load_switches (2), solar_emulation (8) | Rev2 3 pins → 11; +8, none lost |
| `F5_SDA` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `F5_SCL` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `BATT_SDA` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `BATT_SCL` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (2), eps_side (1), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `SDA_Top` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (3), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |
| `SCL_Top` | existing FC global | 4 | root (FlatSat_V1.kicad_sch) (3), solar_emulation (1) | Rev2 3 pins → 4; +1, none lost |

## 3. Coverage statement

- Connectors enumerated: **J1–J30, RF1, RF2** (32 designators). Of those, **J17, J25, J26, J27, J28 and RF2**
  have no symbol in the schematic and are listed as *unpopulated*; the other 26 are traced pin by pin above.
- Every pin of every populated connector appears in exactly one row. The FlatSat destination is either a
  new-sheet refdes/pin, a shared-rail summary, or *unchanged: external connector kept*.
- Connectors whose nets a new sheet reaches: **J1, J2, J3, J4, J5, J6, J7, J8, J9, J10, J11, J12, J13, J14,
  J15, J16, J18, J19, J20, J21, J22, J23, J24, J29, J30, RF1** — via GND alone for several of them
  (J12, J18, J21, J22, J23, J24, RF1), which is why the shared-rail rows appear there.
- Connectors that keep a genuinely FC-only function on every non-ground pin (no new sheet on any signal):
  **J3** (except `+3V3`), **J5**, **J12** (FC USB — the emulator has its own USB-C, `bench_io` J701),
  **J18** (payload), **J21/J23/J24** (pyro/heater outputs — D1 keeps them as connectors, no dummy loads),
  **J22** (FC SWD — the emulator has its own, `bench_io` J702), **RF1**.
- `DEPLOY1`, `DEPLOY1_AUX`, `DEPLOY2` and `Heater Output` (brief §4.1, "Used by: none") are confirmed
  untouched: no new-sheet pin appears on any of them. The pyro inhibit acts on the U6 **enable** nets
  (`Deploy1_EN`, `Heater_EN`, `Deploy2_EN`), never on the outputs.
- D11 note: **J14 stays populated.** `battery_protection_replica` lands on `Dir_Chrg_In` (J14 pins 1/3/5/7/9),
  `B-` (pins 2/4/6/8) and `+3V3` (pin 11); `solar_emulation` answers the pack's TMP112s on `BATT_SDA`/`BATT_SCL`
  (pins 10/12). Never connect a real pack to J14 while the bench PSU or the charger USB is live.
