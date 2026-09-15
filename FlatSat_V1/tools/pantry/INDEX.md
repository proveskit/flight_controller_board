# Symbol pantry — validated KiCad 10 lib_symbols blocks

Each `.sexp` file is one `(symbol "Lib:Name" ...)` block, flattened, indented two tabs, ready to paste inside a sheet's `(lib_symbols ...)`. Every block has been loaded by kicad-cli 10.0.1 in isolation. File name = symbol name with `: / space ( )` replaced by `_`. Regenerate any of them (or fetch others) with `tools/get_symbol.py "Lib:Name" --sch-dirs <upgraded refs dir>`.

| symbol | source |
|---|---|
| `power:GND` | $PROJ/FlatSat_V1.kicad_sch |
| `power:+3V3` | $PROJ/FlatSat_V1.kicad_sch |
| `power:+1V1` | $PROJ/RP2350.kicad_sch |
| `power:PWR_FLAG` | $SCRATCH/refs/upgraded/XY_Face_V4/XY_Face_V4.kicad_sch |
| `power:VBUS` | $SCRATCH/refs/upgraded/proves_radio_stick_V2/proves_radio_stick_V2.kicad_sch |
| `Device:R` | $PROJ/RP2350.kicad_sch |
| `Device:C` | $PROJ/RP2350.kicad_sch |
| `Device:R_US` | $PROJ/FlatSat_V1.kicad_sch |
| `Device:R_Small` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym |
| `Device:C_Small` | $PROJ/FlatSat_V1.kicad_sch |
| `Device:C_Polarized` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym |
| `Device:L` | $PROJ/RP2350.kicad_sch |
| `Device:LED` | $PROJ/FlatSat_V1.kicad_sch |
| `Device:D` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym |
| `Device:D_Schottky` | $PROJ/eps_side.kicad_sch |
| `Device:D_Zener` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym |
| `Device:Polyfuse` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym |
| `Device:Fuse` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Device.kicad_sym |
| `Device:Crystal_GND24` | $PROJ/RP2350.kicad_sch |
| `Device:FerriteBead` | $SCRATCH/refs/upgraded/proves_radio_stick_V2/proves_radio_stick_V2.kicad_sch |
| `Device:Q_NMOS_GDS` | NOT FOUND |
| `Device:Q_PMOS_GDS` | NOT FOUND |
| `Diode:1N4148W` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Diode.kicad_sym |
| `Diode:1N4148WS` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Diode.kicad_sym |
| `Diode:BAT54W` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Diode.kicad_sym |
| `Diode:BAT54S` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Diode.kicad_sym |
| `Diode:1SS355VM` | $PROJ/FlatSat_V1.kicad_sch |
| `Diode:SS34` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Diode.kicad_sym |
| `Connector:TestPoint` | $PROJ/FlatSat_V1.kicad_sch |
| `Connector:USB_C_Receptacle_USB2.0_16P` | $PROJ/FlatSat_V1.kicad_sch |
| `Connector:Screw_Terminal_01x02` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector.kicad_sym |
| `Connector:Screw_Terminal_01x03` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector.kicad_sym |
| `Connector:Barrel_Jack_Switch` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector.kicad_sym |
| `Connector:Conn_01x02_Pin` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector.kicad_sym |
| `Connector:Conn_01x03_Pin` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector.kicad_sym |
| `Connector:Conn_01x04_Pin` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector.kicad_sym |
| `Connector:Conn_01x06_Pin` | $SCRATCH/refs/upgraded/proves_radio_stick_V2/proves_radio_stick_V2.kicad_sch |
| `Connector:Conn_Coaxial` | $SCRATCH/refs/upgraded/proves_radio_stick_V2/proves_radio_stick_V2.kicad_sch |
| `Connector_Generic:Conn_01x02` | $PROJ/eps_side.kicad_sch |
| `Connector_Generic:Conn_01x03` | $PROJ/FlatSat_V1.kicad_sch |
| `Connector_Generic:Conn_01x04` | $PROJ/eps_side.kicad_sch |
| `Connector_Generic:Conn_01x06` | $PROJ/FlatSat_V1.kicad_sch |
| `Connector_Generic:Conn_01x08` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector_Generic.kicad_sym |
| `Connector_Generic:Conn_02x02_Odd_Even` | $PROJ/eps_side.kicad_sch |
| `Connector_Generic:Conn_02x03_Odd_Even` | $SCRATCH/refs/upgraded/XY_Face_V4/XY_Face_V4.kicad_sch |
| `Connector_Generic:Conn_02x05_Odd_Even` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Connector_Generic.kicad_sym |
| `Connector_Generic:Conn_02x06_Odd_Even` | $PROJ/FlatSat_V1.kicad_sch |
| `Jumper:Jumper_2_Open` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Jumper.kicad_sym |
| `Jumper:Jumper_2_Bridged` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Jumper.kicad_sym |
| `Jumper:SolderJumper_2_Open` | $PROJ/watchdog.kicad_sch |
| `Jumper:SolderJumper_2_Bridged` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Jumper.kicad_sym |
| `Jumper:Jumper_3_Open` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Jumper.kicad_sym |
| `Switch:SW_Push` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Switch.kicad_sym |
| `Switch:SW_Push_SPDT` | $SCRATCH/refs/upgraded/debug_board_v1/debug_board_v1.kicad_sch |
| `Switch:SW_SPST` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Switch.kicad_sym |
| `Switch:SW_SPDT` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Switch.kicad_sym |
| `Switch:SW_Slide_SPDT` | NOT FOUND |
| `Memory_Flash:W25Q128JVS` | $PROJ/RP2350.kicad_sch |
| `MCU_RaspberryPi_RP2350:RP2350_60QFN` | $PROJ/RP2350.kicad_sch |
| `Interface_Expansion:TCA9548APWR` | $PROJ/FlatSat_V1.kicad_sch |
| `Power_Management:AP22652` | $PROJ/load_switches.kicad_sch |
| `Regulator_Linear:AP2112K-3.3` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Regulator_Linear.kicad_sym |
| `Regulator_Linear:NCP1117-3.3_SOT223` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Regulator_Linear.kicad_sym |
| `Battery_Management:BQ25886RGE` | $SCRATCH/refs/upgraded/debug_board_v1/debug_board_v1.kicad_sch |
| `Sensor_Temperature:TMP112xxDRL` | $SCRATCH/refs/upgraded/XY_Face_V4/XY_Face_V4.kicad_sch |
| `Driver:DRV2605LDGS` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Driver.kicad_sym |
| `Driver_Haptic:DRV2605LDGS` | $SCRATCH/refs/upgraded/XY_Face_V4/XY_Face_V4.kicad_sch |
| `Transistor_FET:IRF7404` | $SCRATCH/refs/upgraded/battery_pack_v2/battery_pack_v2.kicad_sch |
| `Transistor_FET:IRF7403` | /Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols/Transistor_FET.kicad_sym |
| `Transistor_FET:CSD17576Q5B` | $SCRATCH/refs/upgraded/XY_Face_V4/XY_Face_V4.kicad_sch |
| `easyeda2kicad:TCA4311ADGKR` | $SCRATCH/refs/upgraded/XY_Face_V4/XY_Face_V4.kicad_sch |
| `easyeda2kicad:VEML6031X00` | $SCRATCH/refs/upgraded/XY_Face_V4/XY_Face_V4.kicad_sch |
| `easyeda2kicad:5040500691` | $SCRATCH/refs/upgraded/XY_Face_V4/XY_Face_V4.kicad_sch |
| `easyeda2kicad:SPM6530T-4R7M-HZ` | $PROJ/eps_side.kicad_sch |
| `easyeda2kicad:DZDH0401DW-7` | $SCRATCH/refs/upgraded/debug_board_v1/debug_board_v1.kicad_sch |
| `easyeda2kicad:DMP4047LFDE-7` | $SCRATCH/refs/upgraded/debug_board_v1/debug_board_v1.kicad_sch |
| `easyeda2kicad:TPS62085RLTT` | $SCRATCH/refs/upgraded/proves_radio_stick_V2/proves_radio_stick_V2.kicad_sch |
| `easyeda2kicad:XFL4015-471MEC` | $SCRATCH/refs/upgraded/proves_radio_stick_V2/proves_radio_stick_V2.kicad_sch |
| `easyeda2kicad:TPS22918DBV` | $SCRATCH/refs/upgraded/proves_radio_stick_V2/proves_radio_stick_V2.kicad_sch |
| `easyeda2kicad:KH-MMCX-Z` | $PROJ/FlatSat_V1.kicad_sch |
| `easyeda2kicad:AP22652W6-7` | /Users/ncc-michael/Documents/KiCad/easyeda2kicad/easyeda2kicad.kicad_sym |
| `easyeda2kicad:DF11-4DP-2DSA(08)` | /Users/ncc-michael/Documents/KiCad/easyeda2kicad/easyeda2kicad.kicad_sym |
| `easyeda2kicad:DF11-12DP-2DSA(24)` | /Users/ncc-michael/Documents/KiCad/easyeda2kicad/easyeda2kicad.kicad_sym |
| `mainboard:RESISTOR0603` | $PROJ/FlatSat_V1.kicad_sch |
| `mainboard:R-US_R0603` | $PROJ/FlatSat_V1.kicad_sch |
| `Adafruit ItsyBitsy RP2040-eagle-import:CAP_CERAMIC_0402NO` | $PROJ/FlatSat_V1.kicad_sch |
| `Adafruit ItsyBitsy RP2040-eagle-import:SWITCH_TACT_SMT4.6X2.8` | $PROJ/FlatSat_V1.kicad_sch |
| `Adafruit ItsyBitsy RP2040-eagle-import:VBUS` | $PROJ/FlatSat_V1.kicad_sch |
| `BM04B-SRSS-TB_LF__SN_:BM04B-SRSS-TB(LF)(SN)` | $PROJ/FlatSat_V1.kicad_sch |
| `flatsat:R5460N208AA` | derived from batteryboard-rescue:R5460N233AF-symbols (battery_pack_v2); Value/MPN corrected to R5460N208AA-TR-FE, LCSC C259714 |
| `flatsat:IRF7458` | derived from Transistor_FET:IRF7403 (N-ch SO-8: S=1,2,3 G=4 D=5,6,7,8); Value IRF7458, LCSC C10879 = battery_pack_v2 as-ordered FET |
| `flatsat:3V3_EMU` | power symbol, emulator 3.3 V rail |
| `flatsat:VBUS_EMU` | power symbol, emulator USB-C 5 V |
| `flatsat:VBUS_CHG` | power symbol, charger USB-C 5 V |
| `flatsat:VSOLAR_BENCH` | power symbol, bench solar input rail (before injection diode) |
| `flatsat:VBAT_BENCH` | power symbol, bench battery PSU + input (before protection replica) |
