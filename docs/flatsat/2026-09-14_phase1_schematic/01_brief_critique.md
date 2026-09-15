# Critique of `00_pm_brief.md` (Phase 1 schematic capture) — review-board pass, 2026-09-14

Scope: every claim in the brief was checked against the Rev2/FlatSat_V1 schematics and `tools/baseline/netlist.kicadxml`, the five reference designs (KiCad 10 copies + as-ordered BOM CSVs in the scratchpad), the plan of record (rev 4), the handoff, `CLAUDE.md`, `tools/harness_erc.sh`, `tools/sch_lint.py`, and the primary datasheets named below. Findings are ordered most severe first. "Fix" = exact replacement text or edit for the brief.

Datasheets used (local text extracted with `pdftotext` from the fetched PDFs):
TCA4311A (TI, https://www.ti.com/lit/ds/symlink/tca4311a.pdf) · R5460 series (Nisshinbo EA-165-250616, https://www.nisshinbo-microdevices.co.jp/en/pdf/datasheet/r5460-ea.pdf) · TPS4H160-Q1 (TI, https://www.ti.com/lit/ds/symlink/tps4h160-q1.pdf) · BAT54W series (Nexperia, https://assets.nexperia.com/documents/data-sheet/BAT54W_SER.pdf) · LT3652 (ADI 3652fe, https://www.analog.com/media/en/technical-documentation/data-sheets/3652fe.pdf) · BQ25886 (TI SLUSD88A, https://www.ti.com/lit/ds/symlink/bq25886.pdf) · INA219 (TI, https://www.ti.com/lit/ds/symlink/ina219.pdf) · RP2350 datasheet Appendix E, erratum RP2350-E9 (https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf; summary https://hackaday.com/2024/09/20/raspberry-pi-rp2350-e9-erratum-redefined-as-input-mode-leakage-current/) · LCSC C8678 (https://www.lcsc.com/product-detail/C8678.html) · LCSC C2886093 (https://www.lcsc.com/product-detail/C2886093.html).

---

## 1. BLOCKER — The "synthetic cell midpoint" (2 × 100 k) violates the R5460 datasheet and will trip or mis-detect

**What is wrong.** §2 D4 (line 31) and §6.4 (line 173) specify "two equal high-value resistors (e.g. 2 × 100 k) B+→MID→B−, connected to the IC's VC". The R5460's VC input draws conduction current; the datasheet limits the series resistance at VC to < 1 kΩ. A 100 k/100 k divider presents 50 kΩ Thevenin at VC — 50× the limit — so the cell-1/cell-2 split shifts by tens to hundreds of mV. R5460N208AA trips over-charge at 4.250 V per cell; the FC's LT3652 float is 8.38 V (R71 634 k / R74 412 k → 3.3 V × 1046/412), i.e. 4.19 V per synthetic cell, only 60 mV below the trip. Any midpoint error of that order opens COUT (charge FET) during every charge test, and an error the other way pulls the low "cell" toward the 2.40 V under-voltage trip. The brief's own instruction "Document … the IC's VC input impedance" shows it suspected this; the datasheet answers it and the answer forbids the proposed values.

**Evidence.** R5460 datasheet p.17 "TYPICAL APPLICATION AND TECHNICAL NOTES": "R1, R2, C1 and C2 stabilize a supply voltage to the R5460xxxxxx. A recommended R1, R2 value is less than 1kΩ. A larger value of R1 and R2 makes the detection voltage shift higher because of some conduction current in the R5460x2xxxx." Product Code Table: `R5460x208AA VDET1U 4.250 VREL1U 4.050 VDET1L 4.250 VREL1L 4.050 VDET2U 2.400 VREL2U 3.000 VDET2L 2.400 VREL2L 3.000 VDET3 0.200 VDET4 −0.200; tVDET1 1 s, tVDET2 128 ms, tVDET3 12 ms, tVDET4 8 ms`. battery_pack_v2 uses R4 330 Ω into VC and C8 0.1 µF (refs/battery_pack_v2.netlist.xml, U1 pin 4 → Net-(U1-VC) → R4 → BM). LT3652 float: `tools/baseline/netlist.kicadxml` R71 634 k (VBATT_SENSE→VFB), R74 412 k (VFB→GND).

**Fix (replace the "Synthetic midpoint" sentence in §6.4 and the D4 wording).**
> Synthetic midpoint: two equal **1.0 kΩ 0805 1 %** resistors B+→MID→B− (the R5460 datasheet, p.17 Technical Notes, requires < 1 kΩ effective series resistance at VC because VC conduction current shifts the detection voltage; 2 × 1 k gives 500 Ω Thevenin, 4.2 mA and 18 mW per resistor at 8.4 V). Keep the pack's R4 330 Ω + C8 0.1 µF between MID and VC exactly as on pack_v2. The MID screw terminal lets a real dual supply override the divider (remove the divider jumper). Do NOT use high-value resistors. Record in the report: R5460N208AA trips at 4.250 V/cell (8.50 V pack) and 2.400 V/cell (4.80 V), releases at 4.050/3.000 V; LT3652 float on this FC is 8.38 V, 120 mV below the OV trip, so the PSU setpoint must be ≤ 8.4 V.

---

## 2. MAJOR — `B-` means two different nodes: the pack's cell negative vs. the FC's pack-terminal negative. The brief's wording invites shorting out the protection FETs

**What is wrong.** §6.4 line 174: "Output: B+ (through nothing) → `Dir_Chrg_In`; B− → protection FETs → `B-`." and §4.3 promotes the FC local label `B-` to global "for battery_protection_replica (pack negative)". In battery_pack_v2 the net literally named `B-` is the **cell** negative (R5460 VSS, Q1 source, test point TP2 "B-"); the node that reaches the FC's J14 pins 2/4/6/8 is the pack's `PACK-` (Q2 source, after both FETs). The FC's global `B-` therefore corresponds to the pack's `PACK-`, not the pack's `B-`. An implementer told to "copy the pack's R/C network exactly" and to "use the global name `B-`" will either carry a local label `B-` on the cell side next to a global `B-` on the pack side (KiCad `same_local_global_label` warning, and one "fix" away from a short) or, if the generator promotes the pack's labels, will wire VSS straight to the FC `B-` and bypass both FETs silently — the sheet then exercises nothing.

**Evidence.** refs/battery_pack_v2.netlist.xml: U1 pin 6 VSS → `B-`; Q1 S(1,2,3) → `B-`, Q1 D → common drain; Q2 S(1,2,3) → `PACK-`; J1 pins 2/4/6/8 → `PACK-`; C5 0.1 µF between `B-` and `PACK-`; U3 TCA4311A GND → `PACK-`. FC: `tools/baseline/connector_nets.md` J14 pins 2/4/6/8 → `/Power Systems/B-`.

**Fix (add to §6.4 after "Exactly the pack's topology…").**
> Net-name rule for this sheet: the pack's cell-negative net (R5460 VSS, Q1 source, pack_v2 label `B-`) must be named **`VBAT_BENCH_N`** (local) on this sheet — never `B-`. The FC global `B-` is the pack's `PACK-` (Q2 source, after both FETs). The synthetic-midpoint divider and the R5460's R1/C1, R2/C2, C3 all reference `VBAT_BENCH_N`, not `B-` and not `GND`. State this mapping in a text note next to the FETs.

---

## 3. MAJOR — The BQ25886 sub-block description is factually wrong on three points and the reference it copies has never been built

**What is wrong.** §6.4 line 175: "BQ25886RGE with its inductor (SPM6530T-4R7M-HZ) and the debug board's diode/FET output arrangement (DZDH0401DW-7, DMP4047LFDE-7)".
(a) On debug_board_v1 the DZDH0401DW-7 (ideal-diode controller) + DMP4047LFDE-7 (P-FET) sit on the **USB VBUS input** to the charger's VBUS pin (reverse-current blocking), not on the output. The BAT pins go straight to `Dir_Chrg_In` with C1 10 µF.
(b) The debug board's inductor is **SPM6530T-1R0M120, 1.0 µH, LCSC C87572**. SPM6530T-4R7M-HZ (C360729) is the FC's L5 (U12 buck). The BQ25886 datasheet characterises and designs with L = 1 µH at 1.5 MHz.
(c) The debug board leaves **SYS floating with no capacitor** (datasheet §9.2.2.3: "Minimum 44-μF capacitor is suggested for up to 2.2-A boost converter output current"), TS open (pin table: "Charge suspends when TS pin is out of range"), and routes real USB data to D+/D− (BC1.2 detection sets IINDPM per Table 3). Its `jlcpcb/production_files/BOM-*.csv` and `CPL-*.csv` are header-only (44/51 bytes) — the board was never assembled through JLC, so "the project's established 'USB in and go' pattern" (D3) is an untested schematic, not a precedent. Copying it "as on debug_board_v1" propagates an output-cap-less boost with charging possibly suspended by TS.

**Evidence.** refs/debug_board_v1.netlist.xml: Q1 DMP4047LFDE-7 D→`VBUS`, S→`Net-(U1-VBUS)`; U2 DZDH0401DW-7 SOURCE→`Net-(U1-VBUS)`, DRAIN→`VBUS`, BIAS→Q1 gate; U1 BAT(13,14)→`Dir_Chrg_In`; SYS(15,16)→`Net-(U1-SYS-Pad15)` (no other member); TS/CE/STAT/PG/OTG unconnected; L5 `SPM6530T-1R0M120` LCSC C87572; R4 VSET 150 k; R3 ICHGSET 5.7 k; R5 ILIM 383 k. BQ25886 SLUSD88A: §7.7 conditions "L = 1µH (DFE252012F-1R0)", §9.2.3 "L = DFE252012F-1R0 (1 µH)"; §9.2.2.3 SYS capacitor ≥ 44 µF; pin table VSET "RVSET > 150kΩ (floating) = 8.4 V" (150 k is at the bin edge), CE "internally pulled low with 900k-Ω resistor" (charge enabled when floating), TS "Charge suspends when TS pin is out of range"; features "Instant-on works with no battery or deeply discharged battery"; §8.3.7.1 "If no battery is connected, the STAT pin blinks as capacitance connected at BAT charges, discharges, then recharges." FC BOM: L5 SPM6530T-4R7M-HZ C360729. antenna-board/debug_board_v1/jlcpcb/production_files/: BOM and CPL header-only.

**Fix (replace the BQ25886 bullet in §6.4).**
> BQ25886 USB path per D3, based on `antenna-board/debug_board_v1` (schematic only — that board was never assembled; treat it as a starting point, not a validated precedent): power-only USB-C (`Connector:USB_C_Receptacle_USB2.0_16P` / `USB_C_Receptacle_HRO_TYPE-C-31-M-12`, C165948; 5.1 k CC pull-downs), the debug board's **input** reverse-blocking stage between USB VBUS and the charger VBUS pin (DZDH0401DW-7 C3235552 + DMP4047LFDE-7 C442635, R 1 M as drawn), BQ25886RGE (needs LCSC) with **L = 1.0 µH SPM6530T-1R0M120 (C87572)**, CVBUS 1 µF, CPMID 10 µF, **CSYS ≥ 44 µF on SYS (16 V X7R; the debug board omits this — add it)**, CBAT 10 µF, REGN 4.7 µF, BTST 47 nF, ILIM 383 k, ICHGSET 5.7 k, VSET left open (= 8.4 V; 150 k is at the bin edge), TS: fit the datasheet's REGN–TS–GND divider so TS sits mid-window (charging is suspended if TS is out of range; the debug board leaves it open), CE open (internal 900 k pull-down enables charging), D+/D− shorted together (presents a DCP to the BC1.2 detector — quote the resulting IINDPM from Table 3) because this port carries no data. BAT → 2-pin jumper (shunt removed by default) → `Dir_Chrg_In`. Quote in the report: input-current and charge-current formulas (KILIM = 1110, ICHG from ICHGSET), and the no-battery behaviour (§8.3.7.1). Where LCSC numbers are unknown list them under "needs LCSC".

---

## 4. MAJOR — RP2350 erratum E9 defeats the "unpowered/unprogrammed emulator leaves the FC alone" guarantee on the three open-drain drivers

**What is wrong.** §6.6 line 192: 2N7002 gate "through 1 k with a 100 k gate pull-down (so an unpowered emulator leaves the FC alone)". On A2-stepping RP2350 silicon (what LCSC C42411118 stock may be), a GPIO left as an input with the input buffer enabled (the post-reset default and the state in BOOTSEL/unprogrammed) leaks up to 120 µA and settles around 2 V unless the external pull-down is ≤ 8.2 kΩ. With 100 k the `EMU_CTL_*` pads float to ~2 V; a 2N7002 (VGS(th) 1–2.5 V) conducts enough at 2 V to sink the FC's 10 k RUN pull-up (0.33 mA), the D4+R10 BOOTSEL path and the watchdog integrator — i.e. **whenever the emulator is unprogrammed or in USB-boot, the FC may be held in reset, forced into USB boot, or have its watchdog disabled**. That is exactly the bench-blocking failure D8 is trying to avoid.

**Evidence.** RP2350 datasheet Appendix E, RP2350-E9 (leakage up to 120 µA at IOVDD 3.3 V when a GPIO is an input with input buffer enabled and the pad is between logic levels; workaround: external pull-down ≤ 8.2 kΩ or disable the input buffer; fixed in A4 stepping per the July 2025 PCN). FC pull-ups: `tools/baseline/netlist.kicadxml` R1 10 k (+3V3→FC_RESET); USBBOOT reaches BOOTSEL via D4 NSR0320 + R10 1 k.

**Fix (replace in §6.6).**
> gate ← `EMU_CTL_*` through 1 k with a **4.7 k gate pull-down (≤ 8.2 k is required by RP2350 erratum E9 so that an unprogrammed / BOOTSEL-mode / unpowered emulator cannot float the gate to ~2 V; 100 k is not enough on A2 silicon)**. Note E9 and the A4 stepping in the sheet text.

Add to §6.1 GPIO-map requirements: "Every emulator GPIO that is an input or is read before firmware configures it must have an external pull ≤ 8.2 k or be documented as input-buffer-disabled (RP2350-E9)."

---

## 5. MAJOR — E9 also makes the 10 k series sense inputs (`EMU_Fn_SENSE`, `EMU_FC3V3_SENSE`, `PYRO_INHIBIT_STATE`) indeterminate when the source is low

**What is wrong.** §4.2 lines 96–98 and §6.2/§6.5 specify 10 k series resistors into emulator GPIO inputs. When `Fn_PWR` is 0 V (face off) or `PYRO_INH_COM` is at GND (inhibit engaged — the safe state the console must recognise), the pad's only pull-down is the 10 k series resistor, which is above the 8.2 k E9 limit: 120 µA × 10 k = 1.2 V at the pad, in the undefined region for a 3.3 V input. The core function of the emulator (respond only while the face's switch is on) and the console's "refuse burn-wire tests unless inhibited" interlock (D9) both depend on these reads.

**Evidence.** As item 4. `EMU_Fn_SENSE` = `Fn_PWR` via 10 k (§6.2 line 158); `PYRO_INHIBIT_STATE` = `PYRO_INH_COM` via 10 k (§6.5 line 182).

**Fix.** In §4.2 rows `EMU_F1_SENSE…`, `EMU_FC3V3_SENSE`, `PYRO_INHIBIT_STATE` and in §6.1/§6.2/§6.5: change "through 10 k" to "**through 4.7 k** (≤ 8.2 k per RP2350-E9; 4.7 k also limits the back-feed into an unpowered emulator's ESD diode to 0.55 mA per line)". Same for §6.1 "The sense inputs have 10 k series resistors on the other sheets" → "4.7 k".

---

## 6. MAJOR — "the eps_side note allows 9–40 V" on VSOLAR is unsafe: the FC's own INA219 U8 has a 26 V absolute maximum on that net and the LT3652's operating maximum is 32 V

**What is wrong.** §6.3 line 167 tells the injection agent the allowed range is 9–40 V and to size a TVS on that basis. VSOLAR connects directly to U8 (INA219, 0x41) IN+; U8 IN− is V_SOLAR_SENSE on the other side of the 2 mΩ shunt R108. The INA219 absolute maximum on IN+/IN− is 26 V ("In no event should more than 26 V be applied to this device"). The LT3652 operating range is 4.95–32 V (40 V is the absolute maximum only). A bench operator or a 40 V-standoff TVS choice following the brief can destroy U8. The pre-existing FC note is itself wrong and should be reported, not propagated.

**Evidence.** `eps_side.kicad_sch:6252` text "VSOLAR 9V to 40V". `tools/baseline/netlist.kicadxml`: U8 pin 1 IN+ → `VSOLAR`, U8 pin 2 IN− → `V_SOLAR_SENSE`, R108 2 mΩ. INA219 datasheet §7.1 Absolute Maximum Ratings: IN+, IN− common-mode −0.3 to 26 V; note (2) "the voltage at these pins must not exceed the range –0.3 to 26 V"; §7.5 note (2) "In no event should more than 26 V be applied to this device." LT3652 datasheet: VIN operating 4.95–32 V, 40 V absolute maximum; VIN must be ≥ VBAT(FLT) + 3.3 V for start-up, ≥ 0.75 V above once switching.

**Fix (replace the bench-setting sentence in §6.3).**
> A text note giving the bench setting: supply **12–18 V, hard maximum 24 V** (INA219 U8 IN+ absolute maximum is 26 V on this net; LT3652 operating maximum is 32 V; the eps_side note "9V to 40V" is wrong and must not be repeated — flag it in your report as an FC finding). Start-up needs VIN ≥ VFLOAT + 3.3 V = 11.7 V for the 8.38 V float programmed by R71/R74. If a TVS is fitted, choose a ≤ 22 V standoff SMA part and state the clamp voltage; PSU OVP is the primary protection.

---

## 7. MAJOR — PWR_FLAG ownership is unassigned; two sheets are told to "add PWR_FLAGs" on shared rails, and none is told not to on `GND`/`+3V3`

**What is wrong.** §6.1 line 150: "Add PWR_FLAGs so ERC sees the rails driven" (emulator_mcu, whose input rail `VBUS_EMU` is defined on bench_io); §4.2 line 106: `3V3_EMU` "needs a PWR_FLAG or a power-output pin"; nothing for `VBUS_CHG`, `VBAT_BENCH`, `VSOLAR_BENCH`. A PWR_FLAG is a power-output pin; two on one net, or one on a net that already has a power-output pin, is an ERC **error** (power-output to power-output). The FC baseline already has power-output pins on `GND` and `+3V3` (no `power_pin_not_driven` on them in `tools/baseline/erc.json`) and has **no** PWR_FLAG anywhere (`grep -c '#FLG' *.kicad_sch` = 0). Two implementers will resolve this differently and the error will only appear when both sheets are on disk, with the blame unclear.

**Evidence.** `tools/baseline/erc.json` summary: 6 `power_pin_not_driven` errors, on `VBUS` (#U$05), U3 A0, U1 V+ (VBUSP), #PWR029, U18 VREG_AVDD, U18 DVDD (+1V1) — none on GND/+3V3. Pantry `flatsat_3V3_EMU.sexp`, `flatsat_VBUS_EMU.sexp`, `flatsat_VBAT_BENCH.sexp`: pin type `power_in`.

**Fix (add a paragraph to §4.2 after the table).**
> PWR_FLAG ownership (exactly one per net, on the defining sheet; never on `GND`, `+3V3`, `VSOLAR`, `Dir_Chrg_In`, `VBUSP`, `B-`, `VBATT_SENSE`, `Fn_PWR` or any other existing FC net): `VBUS_EMU` → bench_io; `3V3_EMU`, `1V1_EMU`, `VREG_AVDD_EMU` → emulator_mcu (omit where the regulator symbol's output pin is already `power_out`); `VBUS_CHG`, `VBAT_BENCH`, `VBAT_BENCH_N` → battery_protection_replica; `VSOLAR_BENCH_A/B` → solar_power_injection. Note that the FC's U18 DVDD/VREG_AVDD baseline errors will recur on the emulator copy unless flagged there.

---

## 8. MAJOR — The §4.3 label promotions must be done before the sheet agents run, or their harness results are meaningless

**What is wrong.** pyro_inhibit (8 promoted nets) and battery_protection_replica (`B-`) use global labels that, until the integrator edits `eps_side`/`load_switches`, connect to nothing: the harness copies the real project as-is, so those sheets will show eight `single_global_label` warnings the brief says to expect only for "contract nets whose partner sheet is not on disk yet", and the netlist diff will not show them reaching `/Power Systems/Load Switches/Deploy1_EN` etc. — so "Done means … the netlist diff shows exactly the existing nets §4 says you touch" cannot be evaluated. The brief gives no ordering.

**Evidence.** §4.3 lines 110–123; §7 line 210; `tools/harness_erc.sh` lines 33–60 (rsync of the real project, sheet symbols added, nothing else edited). Labels verified: exactly one `(label "Deploy1_EN")` at (223.52, 81.28), `Heater_EN` (223.52, 86.36), `Deploy2_EN` (223.52, 88.9) in `load_switches.kicad_sch:4581/4631/4591`; `INHIB_1` (199.39, 57.15), `INHIB_2` (199.39, 68.58), `B-` (134.62, 187.96), `IN_RBF` (223.52, 57.15), `VBATT_SENSE` (165.1, 110.49, 270) in `eps_side.kicad_sch:10868–10938`; no global label or power symbol of any of these names on any sheet.

**Fix (add to §4.3 and §9).**
> Sequencing: the integrator performs the eight promotions and re-runs `tools/harness_erc.sh` (expect: netlist diff = eight pure renames, zero new ERC errors) **before** any sheet agent is dispatched. Sheet agents may assume the global names exist. If the promotions have not landed, pyro_inhibit / battery_protection_replica must list the eight `single_global_label` warnings as expected in their report.

---

## 9. MAJOR — USB series resistors are specified on two sheets, with a value that matches no PROVES board

**What is wrong.** §6.1 line 148 puts a "USB series/pull arrangement" on emulator_mcu; §6.6 line 188 and §4.2 line 100 put "27 Ω series" on bench_io "mirror[ing] the FC's J12/R7/R8 arrangement". Two implementers will each add series resistors (44–54 Ω total in each data line), and the FC, the radio stick and the debug board all use **22 Ω** (R7/R8, LCSC C25092). The RP2350 needs no external USB pull-ups.

**Evidence.** `tools/baseline/netlist.kicadxml` R7/R8 = 22 Ω (`USB_D±` ↔ `USB_DM/DP`); FC BOM line "22,R7,R8,R_0402_1005Metric,C25092"; refs/proves_radio_stick_V2.netlist.xml R7/R8 22 Ω; refs/debug_board_v1.netlist.xml R7/R8 22 Ω.

**Fix.** §6.1: delete "USB series/pull arrangement"; add "USB_DP/USB_DM pins wire directly to global labels `EMU_USB_DP`/`EMU_USB_DM`; the 22 Ω series resistors live on bench_io only; no pull-ups." §6.6 and §4.2: "27 Ω" → "22 Ω (C25092, as R7/R8 on the FC and on the radio stick)".

---

## 10. MINOR — Two of the §5 root placements overlap existing root-sheet graphics

**What is wrong.** `solar_power_injection` at (284.48, 140.97), size 43.18 × 12.7, covers U3 TCA9548APWR's lower pins (U3 at (318.77, 118.11); pins extend to y = 143.51) and the `#PWR088` GND symbol at (318.77, 146.05–152.4) plus the SDA0 wire at y = 135.89…; the (x, 161.29) row crosses a graphic polyline. No electrical effect (sheet symbols have no pins), but the brief demands a readable root and the harness table must stay in sync.

**Evidence.** `FlatSat_V1.kicad_sch` U3 instance `(at 318.77 118.11 0)`, lib rectangle y −22.86…+20.32, pins to −25.4; scan of top-level items inside each proposed box: solar_power_injection → wire, #PWR088, U3; battery_protection_replica and bench_io → polyline.

**Fix.** Move the block: column x = 182.88 / 233.68 / 284.48 → rows y = **190.5** and **210.82** (both clear), or keep the rows and move column 3 to x = 340.36. Update `tools/harness_erc.sh` lines 25–30 in the same edit.

---

## 11. MINOR — §6.1's regulator current budget counts loads that are not on `3V3_EMU`

**What is wrong.** §6.1 line 150: "worst-case current: RP2350 + 7 TCA4311A + LEDs". Per D7 and §6.2 the seven TCA4311As are powered from `F1_PWR…F5_PWR` and the FC `+3V3`, not from `3V3_EMU`. The budget as written pushes an implementer toward the buck for no reason.

**Fix.** "…worst-case current: RP2350 core+I/O at full PIO/USB activity (~100 mA), status/power LEDs, bench-header spare GPIO loads; the TCA4311As are on FC rails and do not count. An AP2112K-3.3 (600 mA) is sufficient; choose the buck only if you want heritage with the radio stick."

---

## 12. MINOR — "as-ordered BOM refs/bom/BOM-XY_Face_V4.csv" is the XY_Faces_V3 order, not V4, and lists a VEML7700

**What is wrong.** §6.2 line 157 points to that CSV as the face's as-ordered BOM. `solar_boards/XY_Face_V4/jlcpcb/production_files/` contains only `BOM-XY_Faces_V3.csv`/`CPL-XY_Faces_V3.csv` (Feb 2026) next to a V4 gerber (Aug 2026); the CSV orders `VEML7700 U1 C1850416`, while the V4 schematic has `U7 VEML6031X00` (C3678616). The VEML6031X00 LCSC number is verified elsewhere (Z_Face_V3 and antenna_top_cap_v2c BOMs both order C3678616), and the XY_Face_V4 note "Temperature Sensor I2C Address 0x72" is stale.

**Fix.** §6.2: "as-ordered BOM `refs/bom/BOM-XY_Face_V4.csv` (this is the XY_Faces_V3 order; V4 has no BOM/CPL yet — for the VEML6031X00 use C3678616 from the Z_Face_V3 / top-cap BOMs; TMP112 C28927, TCA4311ADGKR C130025 and DRV2605LDGS C527464 are confirmed in that file)".

---

## 13. MINOR — LCSC C8678 is an MDD SS34, not a CDBA240LL-HF

**What is wrong.** §6.3 line 166: "CDBA240LL-HF (C8678 on Z_Face_V3 / C2886093 on XY_Face_V4; SMA, 40 V 2 A)". C8678 is MDD SS34 (SMA, 40 V, 3 A, 550 mV @ 3 A) — the Z_Face_V3 order substituted it under the CDBA240LL-HF comment. C2886093 is the Comchip CDBA240LL-HF (40 V, 2 A, 310 mV @ 2 A).

**Fix.** "CDBA240LL-HF, LCSC C2886093 (as ordered on XY_Face_V4; Z_Face_V3 ordered C8678 = MDD SS34, a 3 A substitute — either is acceptable, state which)".

---

## 14. MINOR — §6.2 contradicts itself on what may hang on `Fn_PWR`, and the back-powering constraints are not stated

**What is wrong.** Line 158 puts "10 k pull-ups to that face's `Fn_PWR`" on the device side; line 162 says "Do not add anything to `Fn_PWR` other than the buffer VCC, its decoupling and the 10 k sense tap." Also, two real current paths are not documented: (a) if emulator firmware ever drives an `EMU_Fn_SDA/SCL` GPIO push-pull high while `Fn_PWR` is off, it sources ~0.33 mA/line into the dead `Fn_PWR` rail through the pull-ups (back-powering U19–U27 outputs and the buffer VCC); (b) with the FC on and the emulator unpowered, the 14 pull-ups feed ~0.26 mA/line into `3V3_EMU` through the RP2350 ESD diodes (phantom-powering the emulator to ~2.6 V) — same on the pyro sheet via the 100 k pull-up and the STATE tap. TCA4311A isolation is confirmed ("Powered-Off High-Impedance I2C Pins"; EN low or VCC < UVLO 2.5 V isolates IN from OUT), so these are the only paths.

**Evidence.** TCA4311A datasheet features list; §5 pin functions (EN: "isolates SDAIN from SDAOUT… EN should be high (at VCC)"); §8.4.1 (UVLO 2.5 V, 1 V precharge through 100 k during UVLO). XY_Face_V4 / top-cap / pack_v2 netlists: EN and READY each pulled to VCC through 10 k (READY NC on the pack), device-side 10 k pull-ups, FC-side 4.7 k pull-ups on every Fn/BATT/Top line (R44/R62/R56/R61/R73/R88/R89/R105/R106).

**Fix.** Line 162 → "Do not add anything to `Fn_PWR` other than the buffer VCC, its decoupling, the two 10 k device-side pull-ups and the 4.7 k sense tap." Add to §6.1: "Firmware rule (record in the GPIO map): all `EMU_*_SDA/SCL` GPIOs are open-drain only — never driven high — so an off face is never back-powered through its pull-ups. Note in the report the phantom-power path into `3V3_EMU` through the RP2350 ESD diodes when the emulator is unpowered (~0.26 mA per pulled-up line); acceptable, documented."

---

## 15. MINOR — Jumper symbol choice is left open where it changes the netlist

**What is wrong.** §6.5 line 183 offers `Connector_Generic:Conn_01x02` or `Jumper:Jumper_2_Open` for the six parallel inhibit headers; the pantry also carries `Jumper:Jumper_2_Bridged`. A bridged jumper symbol merges its two nets in the netlist, which would collapse `VBATT_SENSE`/`INHIB_1`/`INHIB_2`/`IN_RBF`/`VBUSP` (and `B-`/`GND`) into single nets and fail the "netlist diff shows exactly the existing nets" test. The "shunt fitted by default" jumpers in D1/D2/D4 have the same ambiguity (harmless there, but say so).

**Fix.** §6.5: "use `Connector_Generic:Conn_01x02` (or `Jumper:Jumper_2_Open`) — never a `_Bridged` symbol — so the six existing nets stay separate in the netlist; 'shunt fitted' is a BOM/assembly note, not a schematic short." Same sentence in §6.3 (CH-A), §6.4 (midpoint, BQ output) and §6.5 (heater leg).

---

## 16. MINOR — §6.4 bench notes lack the numbers the replica imposes on the PSU

**What is wrong.** "Text notes: which jumper to fit for each of the three bench modes" is the only bench guidance; the R5460N208AA limits and the LT3652 float interact with a bench PSU that cannot sink current.

**Fix (add to §6.4).**
> Text note: PSU window **4.9 V ≤ V ≤ 8.4 V** (R5460N208AA: OV 4.250 V/cell trips COUT after 1 s; UV 2.400 V/cell trips DOUT after 128 ms and releases only above 3.000 V/cell = 6.0 V pack; discharge over-current at 0.200 V across the two IRF7458 ≈ 11 A). With VSOLAR injected, the LT3652 will source into the node and raise a non-sinking PSU to its 8.38 V float — 120 mV under the OV trip — so either use a PSU that sinks or add a bleed load; if the replica opens COUT, that is the expected pack behaviour, not a fault.

---

## 17. MINOR — §6.3 delegates facts that are already known and that size the fuse

**What is wrong.** "check IC6's programmed charge current on eps_side: sense resistor and R-divider values" — these are fixed: R75 = 0.1 Ω → 1.0 A charge current (LT3652: 0.1 V / RSENSE); R71/R74 → 8.38 V float; input current at 12 V ≈ 1 A × 8.4 V / (0.9 × 12 V) ≈ 0.8 A, ≈ 1.1 A at 9 V.

**Fix.** Replace the parenthetical with "(IC6: R75 0.1 Ω → 1.0 A charge current; R71 634 k / R74 412 k → 8.38 V float; expect ≤ 1.2 A bench input at 12 V — fuse 2 A slow / 1.85 A polyfuse)".

---

## 18. MINOR — The DRV2605L dummy load is DNP by default, which defeats the plan's reason for keeping a real driver

**What is wrong.** Plan §4 "Golden-reference solar face": the DRV2605L drives "a dummy inductive load so its power-draw assertions in the existing HWIL tests remain meaningful". §6.2 line 157 makes the 0805 resistor DNP and asks the implementer to "state the intended dummy value" — but on XY_Face_V4 OUT+ and OUT− are the same schematic net (the coil is copper on the PCB), so the value is only derivable from `XY_Face_V4.kicad_pcb`.

**Evidence.** refs/XY_Face_V4.netlist.xml: U3 DRV2605LDGS pin 7 OUT+ and pin 9 OUT− both on `Net-(U3-OUT+)`.

**Fix.** "…with a **fitted** 0805 resistor across it equal to the XY_Face_V4 coil's DC resistance (measure/estimate from the trace geometry in `solar_boards/XY_Face_V4/XY_Face_V4.kicad_pcb`; state the value and its dissipation at the DRV2605L's max RTP output); remove it when a real coil is plugged in."

---

## 19. MINOR — "SAFE" LED semantics with the emulator unpowered

**What is wrong.** §6.5: LED and 100 k pull-up are on `3V3_EMU`. With the emulator's USB unplugged and the inhibit switch closed the LED is dark; an operator reading "no SAFE light" as "not inhibited" is the wrong-way failure. Electrically the clamp is fine: with the switch closed each EN node sits at VF(BAT54W) ≈ 0.28 V at 0.64 mA (≤ 240 mV @ 0.1 mA, ≤ 320 mV @ 1 mA, Tj 25 °C) against TPS4H160-Q1 VIL(max) 0.8 V (VIH(min) 2 V; IN pins have 100–250 kΩ internal pull-downs).

**Fix.** Add to the §6.5 note: "LED lit = inhibit engaged AND emulator powered; the inhibit itself does not depend on `3V3_EMU`. Quote: EN node ≈ 0.3 V vs VIL(max) 0.8 V (TPS4H160-Q1 §6.5 Logic Input; BAT54W VF table)."

---

## 20. MINOR — Nothing forbids a real pack on J14 while the bench source is live

**What is wrong.** J14 stays populated (§1 "Everything already on the FC stays"), and `Dir_Chrg_In`/`B-` are now also fed by the replica and the BQ25886. Two sources in parallel on a lithium pack is the one failure this bench should make impossible.

**Fix.** §6.4 text note: "Never connect a battery pack to J14 while the bench PSU or the charger USB is connected; J14 is retained for connector-trace completeness only." Consider `dnp yes` on J14 for the FlatSat variant (integrator decision).

---

## 21. MINOR — GPIO and PIO budget should be stated, not left to the implementer

**What is wrong.** RP2350A (QFN-60) has 30 GPIO (GPIO0–29; see U18's pin list). The §6.1 budget is 14 + 6 + 1 + 3 + 2 + 2 + 1 = 29, leaving one spare — fine, but say so, and note that the seven PIO I2C-slave channels must fit in 12 state machines (3 PIO × 4), which is the plan §8 spike; the schematic's "adjacent SDA/SCL per channel" is the right constraint.

**Fix.** Add to §6.1: "Budget: 29 of 30 GPIO; reserve the 30th (document it as `EMU_GPIO_RSVD`, no connector). PIO: 12 state machines for 7 channels — one per channel is the design assumption; record it."

---

## Checked and found correct (no change needed)

- Inhibit chain §4.3 line 125 matches the netlist: `VBATT_SENSE`—J8—`INHIB_1`—J29—`IN_RBF`—J20/J30—`VBUSP`; `VBATT_SENSE`—J7—`INHIB_2`—J10—`IN_RBF`; `B-`—J15/J19—`GND`. Six parallel headers cover all eight connectors.
- EN-net drivers: R104 ← `FIRE_DEPLOY1_B` (U18 GPIO29), R100 ← `ENABLE_Heater` (U9 GPA0), R103 ← `FIRE_DEPLOY2_B` (U9 GPA2); all 3.3 V sources through 4.7 k; nothing else on the three EN nets except U6 IN1–IN4.
- USBBOOT/BOOTSEL: `USBBOOT` = D4 (NSR0320) cathode, J16.1, SW1; D4 anode → R10 1 k → `BOOTSEL` (QSPI_SS, R91 0 Ω → FLASH_SS). "SW1+D4→BOOTSEL" and "USBBOOT reaches BOOTSEL through D4, exactly like SW1" are correct. FC_RESET: R1 10 k to +3V3, SW2, J16.2, TP2, U18 RUN. WDT_DISABLE: watchdog integrator node (C22+C23 20 µF, R31/R33/R35), J4, J16.9, U1 pin 8 — pulling it low is what J4 does; a 2N7002 is adequate.
- `Dir_Chrg_In` ↔ R109 2 mΩ ↔ `VBATT_SENSE` (U16 IN+/IN−, 0x40); `VSOLAR` ↔ R108 2 mΩ ↔ `V_SOLAR_SENSE` (U8, 0x41; IC6 VIN/SHDN). TCA9548 channel map, AP22653 per-face map, J14/J16 pinouts, U6 output map — all as stated.
- §4.3 coordinates and rotations exact; each label occurs once; no global label / power symbol of those names exists. Sheet uuids/pages (watchdog 3, eps_side 4, load_switches 5, RP2350 6), root uuid, `(version 20260306)`, sub-sheets without `(sheet_instances)` and without trailing `(embedded_fonts no)` — all verified. #PWR max on the FC is 172, no #FLG — the 200–799 blocks are clear.
- LCSC numbers verified in as-ordered BOMs: C165948 (USB-C), C160389 (JST-SH), C72443 (KMR2), C42411118 (RP2350A), C97521 (W25Q128JVS), C20625731 (ABM8-272-T3), C2070694 (TPS62085RLTT), C18221164 (XFL4015-471MEC), C130025 (TCA4311ADGKR), C28927 (TMP112), C527464 (DRV2605LDGS), C3678616 (VEML6031X00, via Z_Face_V3/top-cap), C259714 (R5460N208AA), C10879 (IRF7458), C2886093 (CDBA240LL-HF).
- pack_v2 topology: FETs on the negative side, common-drain, Q1 (DOUT) source at cell negative, Q2 (COUT) source at pack negative; VDD via R5 330 Ω + C9 0.1 µF, VC via R4 330 Ω + C8 0.1 µF, V− via R3 1 k + C7 0.1 µF; pantry `flatsat:R5460N208AA` pin order (1 DOUT, 2 COUT, 3 V−, 4 VC, 5 VDD, 6 VSS) matches the datasheet SOT-23-6 column; `flatsat:IRF7458` S=1-3, G=4, D=5-8 matches Q1/Q2 usage.
- Face-side TCA4311A strapping (EN and READY 10 k to VCC, device-side 10 k pull-ups, TMP112 ADD0 = GND → 0x48, DRV2605L EN tied to VCC, IN/TRIG to GND) and top-cap U6 / pack U3 equivalents — as the brief describes.
- Harness table (`tools/harness_erc.sh` lines 25–30) is identical to §5 (uuids, names, pages, coordinates). Brief §10 matches the plan §7 Phase-1 exit criteria; D1/D2/D5/D6/D8 record every deviation from the plan §4 table.
- User non-negotiables respected: baseline v5e-rev2; R5460N208AA-TR-FE C259714; the inhibit is a diode + switch EN-line pulldown with nothing in series in VBUSP / High Power Interstage. Item 1 changes resistor values in the replica, not the inhibit approach.
