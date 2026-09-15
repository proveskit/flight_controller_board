# Sheet report — `solar_emulation` ("Solar and Sensor Emulation", page 8)

**Agent:** implementer of one sheet · **Date:** 2026-09-14 · **Spec:** `00_pm_brief.md` rev 2 §6.2 (interface §4, format §7, deliverables §8)

| item | value |
|---|---|
| sheet file | `/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/solar_emulation.kicad_sch` |
| generator | `/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/tools/gen/solar_emulation_gen.py` |
| sheet-symbol uuid | `0ec7a68a-65de-4eda-8407-9dcf20e51c0b` (root `c64c0d72-a9f6-4f3a-891e-1f647558f538`) |
| instances path | `/c64c0d72-a9f6-4f3a-891e-1f647558f538/0ec7a68a-65de-4eda-8407-9dcf20e51c0b` |
| refdes block | 300–399 (used: U300–U303, U310–U316, R300–R374, C300–C316, J300, TP300–TP306, #PWR301–#PWR332) |
| paper | A3 |

---

## 1. Purpose

Presents to the flight controller (FC) the electrical behaviour of six solar faces, the battery pack's four
TMP112s and the antenna top-cap sensor pair:

* **Face 0** is **real reference silicon** — the sensor section of `solar_boards/XY_Face_V4` reproduced
  part-for-part (TCA4311A hot-swap buffer, TMP112, VEML6031X00, DRV2605L) and powered from the FC's own
  face switch output `F0_PWR`. It is the calibration truth for everything the emulator fakes.
* **Faces 1–5** are **emulated**: one TCA4311A per face with VCC on that face's `Fn_PWR`, bus side on the FC
  nets `Fn_SDA`/`Fn_SCL`, device side handed to the Emulator MCU as `EMU_Fn_SDA`/`EMU_Fn_SCL`, plus a 4.7 k
  face-power sense tap `EMU_Fn_SENSE`.
* **Battery channel** (TCA9548 ch4) and **top-cap channel** (ch7) are emulated the same way with the buffer
  VCC on the FC `+3V3`, replicating `battery_pack_v2` U3 and `antenna_top_cap_v2c` U6 respectively; the
  top-cap block also carries the `EMU_FC3V3_SENSE` tap.
* Seven bench probe pads on `F0_PWR`…`F5_PWR` and `+3V3`.

Decision **D7** is what this sheet implements: the emulator answers *behind the same TCA4311A front-ends the
real boards use, only while the FC has that face's power switch on*. Nothing on this sheet is in series with
any power path — every connection to an FC net is a buffer bus pin, a pull-up (10 k on Face 0, **4.7 k** on
the emulated channels per PM ruling R7 — see §13.1), a 4.7 k sense tap, a decoupling cap or a probe pad.

## 2. Block description

### 2.1 Face 0 — golden reference (top band)

Copied from `refs/upgraded/XY_Face_V4/XY_Face_V4.kicad_sch` (verified against `refs/XY_Face_V4.netlist.xml`).
The face's local `+3V3` rail is the connector pin that the FC drives as `F0_PWR` (J6.4 ← U19 AP22653), so every
"+3V3" on the face becomes `F0_PWR` here.

| face part | here | connection |
|---|---|---|
| U4 TCA4311A | **U300** | VCC = `F0_PWR` + C300 100 nF; EN 10 k (R300) to VCC; READY 10 k (R301) to VCC; SDAIN/SCLIN = `F0_SDA`/`F0_SCL`; SDAOUT/SCLOUT = local `F0_DEV_SDA`/`F0_DEV_SCL` with R302/R303 10 k to `F0_PWR` |
| U2 TMP112 | **U301** | on `F0_DEV_*`; ADD0 = GND → **0x48**; V+ = `F0_PWR`; C301 10 nF; **ALERT left open** (see §7 deviations) |
| U7 VEML6031X00 | **U302** | on `F0_DEV_*`; **0x29**; VDD = `F0_PWR`; C302 100 nF; INT no-connect (as on the face) |
| U3 DRV2605L | **U303** | on `F0_DEV_*`; **0x5A**; VDD and EN both on `F0_PWR`; IN/TRIG = GND; VDD/NC no-connect; REG → C304 1 µF; OUT+/OUT− → `F0_COIL_P`/`F0_COIL_N` |
| PCB trace coil | **J300 + R304** | 2-pin 2.54 mm header for an external magnetorquer coil / lab inductor, with a **fitted 43 R 2010** across it that stands in for the XY_Face_V4 PCB coil (§5) |

### 2.2 Faces 1–5, battery, top-cap — emulated front-ends

One identical block per channel (U310…U316). Per block:

```
Fn_SDA  ──► SDAIN   SDAOUT ──► EMU_Fn_SDA      4.7k to Fn_PWR on the device side (Rx2)
Fn_SCL  ──► SCLIN   SCLOUT ──► EMU_Fn_SCL      4.7k to Fn_PWR on the device side (Rx3)
Fn_PWR  ──► VCC  (+100 nF Cx)   EN ──10k──► VCC (Rx0)    READY ──10k──► VCC (Rx1)
Fn_PWR  ──4.7k(Rx4)──► EMU_Fn_SENSE            GND on pin 4
```

* Faces 1–5: `Fn_PWR` is the AP22653 face-switch output, so the whole block is dead until the FC asserts
  `FACEn_ENABLE`. This is the behaviour the brief asks for and the reason the pull-ups go to `Fn_PWR`, never
  to `3V3_EMU`.
* **BATT (U315)** replicates `battery_pack_v2` U3: VCC = `+3V3`, EN 10 k to `+3V3`, device-side **4.7 k**
  pull-ups to `+3V3` (the pack uses 10 k; lowered to 4.7 k by PM ruling R7, §13.1 — the only departure from
  the pack), **READY left unconnected** (the pack leaves it open — marked with a no-connect so ERC is
  quiet). No sense tap (there is no switched rail to sense).
* **TOP (U316)** replicates `antenna_top_cap_v2c` U6: VCC = `+3V3`, EN **and** READY each 10 k to `+3V3`,
  device-side **4.7 k** pull-ups to `+3V3` (top-cap uses 10 k; lowered by PM ruling R7, §13.1), and the
  `EMU_FC3V3_SENSE` = `+3V3` via 4.7 k tap lives here.

### 2.3 Bench test points

TP300…TP305 on `F0_PWR`…`F5_PWR`, TP306 on `+3V3`. Probe pads only, `TestPoint:TestPoint_Pad_D1.5mm`.

## 3. Parts table

| ref | value | footprint | LCSC | source of the number |
|---|---|---|---|---|
| U300, U310–U316 (8×) | TCA4311ADGKR | `easyeda2kicad:MSOP-8_L3.0-W3.0-P0.65-LS5.0-BL` | **C130025** | as-ordered `BOM-XY_Face_V4.csv`, `BOM-Z_Face_V3.csv`, `BOM-antenna_top_cap_v2c.csv` |
| U301 | TMP112xxDRL | `Package_TO_SOT_SMD:SOT-563` | **C28927** | as-ordered `BOM-XY_Face_V4.csv` (also Z_Face, top-cap) |
| U302 | VEML6031X00 | `easyeda2kicad:SENSOR-SMD_VEML6031X00` | **C3678616** | as-ordered `BOM-Z_Face_V3.csv` + `BOM-antenna_top_cap_v2c.csv` (the XY_Face_V4 CSV is the V3 order and lists VEML7700 — brief §6.2 says to use C3678616) |
| U303 | DRV2605LDGS | `Package_SO:TSSOP-10_3x3mm_P0.5mm` | **C527464** | as-ordered `BOM-XY_Face_V4.csv`, `BOM-Z_Face_V3.csv`. Footprint corrected in integrator fix round 3 (§12): the `VSSOP-10_3x3mm_P0.5mm` name inherited from XY_Face_V4 no longer exists in KiCad 10 |
| R300–R303, R310, R311, R320, R321, R330, R331, R340, R341, R350, R351, R360, R370, R371 (**17×**) | 10k | `Resistor_SMD:R_0402_1005Metric` | **C25744** | FC as-ordered `FlatSat_V1/jlcpcb/project.db` (10k / R_0402) and `BOM-antenna_top_cap_v2c.csv`. Face-0 device-side pull-ups (R302/R303) + every EN/READY strap; these keep 10 k under PM ruling R7 |
| R312, R313, R314, R322–R324, R332–R334, R342–R344, R352–R354, R362, R363, R372–R374 (**20×**) | 4.7k | `Resistor_SMD:R_0402_1005Metric` | **C25900** | FC as-ordered `project.db` (R44/R45/R88/R89/R100/R103/R104/R105/R106 …). The 6 sense taps (Rx4) **plus the 14 emulated-channel device-side pull-ups (Rx2/Rx3), lowered 10 k → 4.7 k by PM ruling R7 — see §13.1** |
| R304 | 43R (0.253 W worst case) | `Resistor_SMD:R_2010_5025Metric` | *needs LCSC* | computed value, §5 — no repo BOM has a 43 Ω. Package raised 0805 → **2010** in integrator fix round 3 (§12): 0.253 W is 200 % of a stock 0805 thick-film rating and 101 % of a 1206; a 2010 is 0.75 W = 34 % of rating |
| C300, C302, C303, C310–C316 (10×) | 100nF | `Capacitor_SMD:C_0402_1005Metric` | **C1525** | FC as-ordered `project.db` (100nF / C_0402); `BOM-Z_Face_V3.csv` agrees |
| C301 | 10nF | `Capacitor_SMD:C_0402_1005Metric` | **C15195** | FC as-ordered `project.db`; `BOM-Z_Face_V3.csv` agrees |
| C304 | 1uF | `Capacitor_SMD:C_0402_1005Metric` | **C52923** | as-ordered `BOM-Z_Face_V3.csv` (the XY face used a 0805 1 µF, C28323; 0402 chosen per brief §6 "0402 for signal passives") |
| J300 | Coil Out (1×02, 2.54 mm) | `Connector_PinHeader_2.54mm:PinHeader_1x02_P2.54mm_Vertical` | *needs LCSC* | FC's own J4 header has no LCSC in `project.db` either |
| TP300–TP306 (7×) | TestPoint | `TestPoint:TestPoint_Pad_D1.5mm` | n/a (bare pad) | — |

**Counts, parsed from the sheet file (not from the generator), as delivered after fix round 2:**
101 symbol instances = 69 real refdes + 32 power symbols (`#PWR301`–`#PWR332`: **25 × GND, 7 × +3V3**),
191 wires, 46 junctions, 4 no-connects, 62 global labels, 12 local labels. Real parts: 11 ICs
(8 × TCA4311A, TMP112, VEML6031X00, DRV2605L), **38 resistors** (17 × 10 k + 20 × 4.7 k + R304 43 R),
12 capacitors (10 × 100 nF, 10 nF, 1 µF), 1 header, 7 test points — **69** components in the BOM roll-up,
unchanged by fix round 2. (Round 1 had 99 instances / 30 power symbols / 177 wires; round 2 added two
`+3V3` symbols — the extra BATT and TOP supply taps — and 14 wires. Power symbols carry no BOM line and
kicad-cli keeps them out of the netlist `<components>` list entirely, so the netlist is unchanged.)

**Needs LCSC:** `R304 / 43R 2010 0.75 W`, `J300 / 2-pin 2.54 mm vertical header`.

Every symbol carries Reference, Value, Footprint, Datasheet and Description; `LCSC Part` is set only where the
number came from an as-ordered BOM in the repos or from `FlatSat_V1/jlcpcb/project.db` (read-only — the file
was **not** written).

## 4. Interface nets

### 4.1 Existing FC nets this sheet connects to (global labels / power symbols)

| net | how this sheet touches it |
|---|---|
| `F0_SDA` `F0_SCL` | U300 SDAIN/SCLIN (bus side of the Face-0 buffer) |
| `F1_SDA` `F1_SCL` … `F5_SDA` `F5_SCL` | U310…U314 SDAIN/SCLIN |
| `BATT_SDA` `BATT_SCL` | U315 SDAIN/SCLIN (TCA9548 ch4) |
| `SDA_Top` `SCL_Top` | U316 SDAIN/SCLIN (TCA9548 ch7) |
| `F0_PWR` | U300 VCC + C300, R300/R301/R302/R303, and the Face-0 devices U301 V+, U302 VDD, U303 VDD+EN, C301/C302/C303, TP300 |
| `F1_PWR` … `F5_PWR` | buffer VCC + 100 nF (Cx), the EN 10 k and READY 10 k straps (Rx0/Rx1), the two **4.7 k** device-side pull-ups (Rx2/Rx3, PM ruling R7 — §13.1), the 4.7 k sense tap (Rx4) and probe pad TP30x — nothing else (brief §6.2, read as in §7.2) |
| `+3V3` | U315/U316 VCC + C315/C316, their EN/READY and device-side pull-ups, R374 sense tap, TP306 |
| `GND` | every buffer GND pin, all decoupling returns, TMP112 GND/ADD0, VEML GND, DRV2605L GND/IN-TRIG, C304 |

No FC net is renamed, no pin is removed from any existing net, and nothing is inserted in series.

### 4.2 New global nets **defined** here (consumed by `emulator_mcu`)

`EMU_F1_SDA` `EMU_F1_SCL` `EMU_F2_SDA` `EMU_F2_SCL` `EMU_F3_SDA` `EMU_F3_SCL` `EMU_F4_SDA` `EMU_F4_SCL`
`EMU_F5_SDA` `EMU_F5_SCL` `EMU_BATT_SDA` `EMU_BATT_SCL` `EMU_TOP_SDA` `EMU_TOP_SCL`
`EMU_F1_SENSE` `EMU_F2_SENSE` `EMU_F3_SENSE` `EMU_F4_SENSE` `EMU_F5_SENSE` `EMU_FC3V3_SENSE` — 20 nets.

### 4.3 New global nets **consumed** here

None. This sheet drives/sources everything it names and takes nothing from another new sheet — in particular
**no `3V3_EMU`, no `VBUS_EMU`** (brief §4.2: face-side pull-ups go to `Fn_PWR`/`+3V3`).

### 4.4 Sheet-local nets

`F0_DEV_SDA`, `F0_DEV_SCL` (the Face-0 device-side I²C bus, behind U300) and `F0_COIL_P`, `F0_COIL_N`
(DRV2605L outputs to J300). Local labels, so they appear in the netlist as
`/Solar and Sensor Emulation/F0_DEV_SDA` etc.

### 4.5 PWR_FLAG

**None placed** — this sheet defines no new rail. Per brief §4.2 a PWR_FLAG is forbidden on `GND`, `+3V3` and
`Fn_PWR`. See §8 open question 1 for the consequence.

## 5. Face-0 magnetorquer load (R304) — derivation

`solar_boards/XY_Face_V4` ties DRV2605L OUT+ and OUT− to one schematic net because the "actuator" is a PCB
spiral. From `XY_Face_V4.kicad_pcb` (read-only), net `Net-(U3-OUT+)`:

| layer | track width | length |
|---|---|---|
| In1.Cu | 0.25 mm | 5 226.4 mm |
| In2.Cu | 0.25 mm | 5 200.7 mm |
| B.Cu | 0.25 mm | 90.2 mm |
| F.Cu | 0.25 mm | 3.5 mm |
| **total** | | **10 520.7 mm** (5 vias) |

The project has no explicit stackup, so the JLCPCB 4-layer default is assumed: 1 oz finished outer, 0.5 oz
(17.5 µm) inner. With ρ_Cu = 1.72 × 10⁻⁸ Ω·m:

* 1 oz outer / 0.5 oz inner → **41.2 Ω** ← value used
* 1 oz on all four layers → 20.7 Ω (stated for sensitivity)

Nearest E24 value: **43 Ω**, fitted as a 2010 (R304) — see the dissipation paragraph below.

**Dissipation.** DRV2605L (TI SLOS854D) §6.3 Recommended Operating Conditions gives VDD 2 – 5.2 V and a
minimum load impedance Z_L = 8 Ω; §8.5.2.1 Eq. 6 sets the open-loop ERM full-scale output from
OD_CLAMP[7:0] (21.59 mV × code, i.e. up to 5.5 V), but the H-bridge cannot exceed its own supply, which here is
`F0_PWR` = 3.3 V. Worst case therefore **3.3 V across 43 Ω = 76.7 mA, 0.253 W**. Recorded on the sheet
(package raised in integrator fix round 3, §12): R304 is a **2010, 0.75 W**, so 0.253 W is **34 % of rating**
and the part does not need a duty-cycle limit to survive — the sheet nevertheless asks for **≤ 50 % duty** at
full amplitude, as a thermal-comfort limit on a dummy load sitting next to the driver. The earlier "fit a
0.25 W-rated 0805 and drive in bursts" wording was unsafe in practice: a stock 0805 thick-film part is 0.125 W,
i.e. 200 % of rating, and even a 1206 is exactly 0.25 W = 101 %. 43 Ω is comfortably above the 8 Ω minimum, so
the §8.3.12 overcurrent/OC_DETECT shutdown will not trip. R304 is removed whenever a real coil or lab inductor is plugged into J300 (assembly note on the
sheet).

## 6. Datasheet facts relied on

**TCA4311A — TI SCPS226C (Jan 2011, rev. Aug 2018), <https://www.ti.com/lit/ds/symlink/tca4311a.pdf>**
(confirmed against the fetched text; the same facts are printed in the sheet's DESIGN NOTES block):

| § | fact | why it matters here |
|---|---|---|
| §1 Features | "Powered-Off High-Impedance I²C Pins"; open-drain I²C pins; open-drain READY | with `Fn_PWR` off, the FC bus sees a high-Z buffer — an unpowered emulated face cannot hold `Fn_SDA`/`Fn_SCL` down or back-feed them |
| §6.3 | VCC 2.7 – 5.5 V; EN V_IH(min) 2 V; SDA/SCL V_IL(max) 0.4 V | 3.3 V rails are in range; EN strapped to VCC is a valid logic high |
| §8.3.1 | rise-time accelerators switch in 2 mA (typ) once a line passes 0.6 V and slews > 1.25 V/µs | with FC-side 4.7 k and device-side 4.7 k (10 k on Face 0) the bus rises fine at 100/400 kHz |
| §8.3.2 | READY is a digital flag, low while EN is low **or** start-up is incomplete; open-drain, sinks 3 mA at 0.4 V; TI specifies a 10 kΩ pull-up to VCC | R301/R311/R321/R331/R341/R351/R371 are exactly that; BATT leaves READY open as `battery_pack_v2` does |
| §8.3.3 | grounding EN disconnects backplane from card, disables the accelerators and the precharge, drives READY low, near-zero current | EN is tied high through 10 k on every channel, so the buffer is enabled whenever its VCC is up |
| §8.4.1 Start-Up | UVLO until VCC rises above **2.5 V**; during UVLO a **1 V precharge through 100 kΩ nominal** is forced on all four SDA/SCL pins; out of UVLO the part waits for a STOP bit **or** bus idle on the IN side **and** for both SDAOUT and SCLOUT to be high before connecting IN to OUT | this is the power-up timing firmware must reproduce: an emulated face becomes visible to the FC only some time after `FACEn_ENABLE` rises, exactly as a real face does. The 1 V/100 k precharge is the only thing the FC bus sees while the face is in UVLO (≈ 23 µA out of the FC's 4.7 k pull-up — negligible) |
| §8.4.2 | a low forced on either side pulls both sides low; both sides go high only when everything releases — clock stretching, arbitration and ACK all work through the buffer | the emulator can clock-stretch and NACK exactly like the real slaves |
| §8.4.3 | "Missing ACK Event": a slave ACK issued while the rise-time accelerators are engaged can fail to transfer | inherited by the emulated channels as well as the real face; worth reproducing in the Phase-3 firmware test matrix |

**DRV2605L — TI SLOS854D:** §6.3 (VDD 2–5.2 V, Z_L min 8 Ω), §8.3.4 + §8.5.2.1 Eq. 6 (open-loop ERM
full-scale set by OD_CLAMP), §8.3.12.3/§8.6 OC_DETECT (shutdown below the load-impedance threshold). Used in §5.

**TMP112 — TI SBOS473:** ADD0 = GND selects slave address **0x48**; ALERT is an open-drain output.
**VEML6031X00:** fixed I²C address **0x29** (brief §6.2 / `antenna_top_cap_v2c`).

## 7. Assumptions, deviations and things the reviewer should check

1. **`U301` TMP112 ALERT is left open (no-connect) instead of tied to GND.** `XY_Face_V4` (and
   `battery_pack_v2`, and `antenna_top_cap_v2c`) ground ALERT. Here that produces a hard ERC error —
   `pin_to_pin: Pins of type Open collector and Power output are connected` — because the FC's `GND` net
   carries `power_out` pins (U7 LSM6DSO pins 6 and 7 are typed `power_out` in `Package_LGA` metadata).
   ALERT is unused on the golden face and is an open-drain output, so leaving it open is electrically
   identical for this bench. **Reversible**: if the reviewer prefers exact heritage, re-ground it and accept
   one ERC error (or exclude it in `FlatSat_V1.kicad_pro`).
2. **Brief §6.2's last bullet ("do not add anything to `Fn_PWR` other than the buffer VCC, its decoupling, the
   two 10 k device-side pull-ups and the 4.7 k sense tap" — *the brief's 10 k was later superseded by PM
   ruling R7; the delivered sheet has 4.7 k there, §13.1*) is read as applying to the *emulated* faces 1–5,
   and even there the literal list is short by three items.** What `F1_PWR`…`F5_PWR` actually carry is: the
   buffer VCC + 100 nF, **the EN 10 k strap and the READY 10 k strap** (required by §6.2's own "EN/READY
   strapped as on the face"), the two **4.7 k** device-side pull-ups (PM ruling R7), the 4.7 k sense tap **and one probe pad**
   (required by §6's "test points on every bench-relevant rail"). Netlist, per face:
   `F1_PWR +[C310.1, R310.1(EN), R311.2(READY), R312.1, R313.1, R314.1(sense), TP301.1, U310.8]`.
   Nothing else — no load, nothing in series. The sheet's "Loading (brief 6.2)" text block was reworded in the
   fix round (§10) to list all six items, because a note that understates its own sheet misleads the next
   reviewer (hard rule §3.4 makes sheet notes requirements).
   `F0_PWR` additionally carries the real Face-0 devices (TMP112 V+, VEML VDD, DRV2605L VDD + EN and their
   decoupling), because Face 0 *is* a real face and must load its rail the way one does. If that reading is
   wrong, Face 0 cannot be built as specified.
3. **Face-0 load on the AP22653 (U19).** TCA4311A ≈ 0.25 mA + TMP112 ≈ 10 µA + VEML6031X00 ≈ 0.3 mA +
   DRV2605L quiescent ≈ 1.6 mA, plus up to 77 mA in bursts through R304/J300 when the magnetorquer is driven.
   The AP22653's programmed limit is set by R on U19 ILIM on the FC (unchanged by this sheet) — worth a check
   by whoever owns the load-switch budget that a 77 mA magnetorquer burst plus inrush is inside it.
4. **BATT channel READY left open** is a faithful copy of `battery_pack_v2` U3, not an oversight. The
   top-cap channel *does* get the READY pull-up because `antenna_top_cap_v2c` U6 has one (R11).
5. **Refdes gap `R361`.** The channel generator reserves offset `+1` for the READY pull-up; the BATT channel
   has none, so R361 is unused. Harmless, but flagged so the integrator does not think a part went missing.
6. **`R304` = 43 Ω is an estimate**, not a measurement — it depends on the JLC inner-layer copper weight
   (§5 gives the 1 oz sensitivity, 20.7 Ω). If someone can 4-wire a built XY_Face_V4 coil, replace the value.
7. **Sense taps** are 4.7 k (≤ 8.2 k, RP2350 erratum E9, brief rule 10) and also limit back-feed into an
   unpowered emulator's ESD diode to ≈ (3.3 − 0.7)/4.7 k ≈ 0.55 mA per line, as the brief states.
   **7b — RESOLVED by fix id 3 (§13.1); the paragraph below describes the pre-fix state and is kept for the
   record.** The 14 `EMU_*_SDA/SCL` pull-ups are now **4.7 k**, so 4.7 k + the AP22653 600 Ω discharge = 5.3 k
   ≤ 8.2 k and 120 µA × 5.3 k = 0.64 V < 0.99 V: rule 10 is met **in hardware**, and the firmware
   input-buffer-disable rule below is retained only as belt-and-braces. *Superseded text:*
   the 14 `EMU_*_SDA/SCL` nets do NOT meet rule 10 — their only external
   pull is **10 k** (R312/R313, R322/R323, R332/R333, R342/R343, R352/R353, R362/R363, R372/R373) because
   brief §4.2 and §6.2 mandate 10 k for parity with `XY_Face_V4` R5/R6. Hard rule §3.10 wants ≤ 8.2 k on every
   emulator input: on A2 silicon an enabled input buffer leaks up to 120 µA, and 120 µA × 10 k = **1.2 V**,
   above the RP2350 V_IL(max) of 0.3 × IOVDD ≈ **0.99 V**. So with `Fn_PWR` off (pull-up returning to a dead
   rail) the emulator's PIO can read a bus line that is neither a real high nor a real low. The sheet keeps
   10 k — reference-board parity is the explicit instruction and the value is right whenever the face is
   powered — and the conflict is **handed to `emulator_mcu`** as a GPIO-map requirement: every `EMU_*_SDA` and
   `EMU_*_SCL` GPIO must be declared **input-buffer-disabled while that face is off** (`EMU_Fn_SENSE` low), or
   the PM must accept the E9 floor. A DESIGN NOTES block stating exactly this was added to the sheet in the fix
   round (§10). The 4.7 k sense taps are unaffected and do meet rule 10.
8. Only the `easyeda2kicad:TCA4311ADGKR` and `easyeda2kicad:VEML6031X00` pantry symbols were used for those
   parts; both type every signal pin `unspecified`, which is where all 51 `pin_to_pin` warnings come from
   (§8). Swapping to better-typed symbols is a library job, not a sheet job.

## 8. Validation results

> **These are the first-round numbers.** The sheet was regenerated in the fix round; §10 carries the re-run
> lint / ERC / netlist-diff output. The netlist is byte-for-byte equivalent (same nets, same pins); only the
> two text notes and the item UUIDs changed, so §8.3's net tables still stand.

### 8.1 `sch_lint.py`

```
$ python3 tools/sch_lint.py solar_emulation.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/0ec7a68a-65de-4eda-8407-9dcf20e51c0b \
    --refdes-block 300-399
solar_emulation.kicad_sch: 99 symbol instances, 10 lib symbols, 177 wires, 0 errors, 0 warnings
```

**0 errors, 0 warnings.** Every item is on the 1.27 mm grid, every wire ends on a pin/label/junction, every
instance carries the right project + path, every refdes is inside 300–399.

### 8.2 `harness_erc.sh "Solar and Sensor Emulation"`

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

=== violations on sheets matching 'Solar and Sensor Emulation' ===
error    power_pin_not_driven              6
warning  pin_to_pin                       51
total 57
errors: 6
- [error] power_pin_not_driven: Input Power pin not driven by any Output Power pins | U300 Pin 8 [VCC]
- [error] power_pin_not_driven: Input Power pin not driven by any Output Power pins | U310 Pin 8 [VCC]
- [error] power_pin_not_driven: Input Power pin not driven by any Output Power pins | U311 Pin 8 [VCC]
- [error] power_pin_not_driven: Input Power pin not driven by any Output Power pins | U312 Pin 8 [VCC]
- [error] power_pin_not_driven: Input Power pin not driven by any Output Power pins | U313 Pin 8 [VCC]
- [error] power_pin_not_driven: Input Power pin not driven by any Output Power pins | U314 Pin 8 [VCC]
```

(The whole-project delta above also contains the other five agents' sheets, which were on disk during this run;
`+6` power_pin_not_driven and `51` pin_to_pin are this sheet's share, the remainder is theirs.)

**Errors on this sheet: 6**, all of one kind — see open question 1. **No new errors anywhere else** are caused
by this sheet, and `single_global_label` went 9 → 0 because the partner sheets now exist.

**Warning triage — 51 `pin_to_pin` warnings, all "Unspecified and X":**

| count | pair | cause |
|---|---|---|
| 31 | Unspecified ↔ Passive | TCA4311A / VEML6031X00 signal pins meeting my pull-up and decoupling passives |
| 9 | Unspecified ↔ Bidirectional | TCA4311A SDAIN meeting TCA9548 U3 SDn (and VEML SDA meeting TMP112 SDA) |
| 8 | Unspecified ↔ Output | TCA4311A SCLIN meeting TCA9548 U3 SCn |
| 2 | Unspecified ↔ Power input | VEML6031X00 GND (pins 1 and 4, typed `unspecified`) meeting the GND power symbol |
| 1 | Unspecified ↔ Input | VEML SCL meeting TMP112 SCL |

Every one of them is the `easyeda2kicad` symbols' habit of typing pins `unspecified`; the project's ERC pin
matrix scores `Unspecified` against everything as a warning. The FC baseline already carries 96 of exactly this
class. **No electrical content** — nothing to fix on the sheet; the fix, if wanted, is better symbol metadata.

### 8.3 `netlist_diff.py` vs the post-promotion baseline

Existing FC nets that gained pins **from this sheet** (nothing lost a pin anywhere, 0 nets removed):

```
~ F0_SDA   +[U300.6]                      ~ F0_SCL   +[U300.3]
~ F1_SDA   +[U310.6]                      ~ F1_SCL   +[U310.3]
~ F2_SDA   +[U311.6]                      ~ F2_SCL   +[U311.3]
~ F3_SDA   +[U312.6]                      ~ F3_SCL   +[U312.3]
~ F4_SDA   +[U313.6]                      ~ F4_SCL   +[U313.3]
~ F5_SDA   +[U314.6]                      ~ F5_SCL   +[U314.3]
~ BATT_SDA +[U315.6]                      ~ BATT_SCL +[U315.3]
~ SDA_Top  +[U316.6]                      ~ SCL_Top  +[U316.3]
~ F0_PWR   +[C300.1, C301.1, C302.1, C303.1, R300.1, R301.2, R302.1, R303.1, TP300.1,
             U300.8, U301.5, U302.6, U303.10, U303.5]
~ F1_PWR   +[C310.1, R310.1, R311.2, R312.1, R313.1, R314.1, TP301.1, U310.8]
~ F2_PWR   +[C311.1, R320.1, R321.2, R322.1, R323.1, R324.1, TP302.1, U311.8]
~ F3_PWR   +[C312.1, R330.1, R331.2, R332.1, R333.1, R334.1, TP303.1, U312.8]
~ F4_PWR   +[C313.1, R340.1, R341.2, R342.1, R343.1, R344.1, TP304.1, U313.8]
~ F5_PWR   +[C314.1, R350.1, R351.2, R352.1, R353.1, R354.1, TP305.1, U314.8]
~ +3V3     +[C315.1, C316.1, R360.1, R362.1, R363.1, R370.1, R371.2, R372.1, R373.1,
             R374.1, TP306.1, U315.8, U316.8]
~ GND      +[C300.2, C301.2, C302.2, C303.2, C304.2, C310.2 … C316.2, U300.4, U301.2,
             U301.4, U302.1, U302.4, U303.4, U303.8, U310.4 … U316.4]
```

That is exactly the set brief §4.1 assigns to `solar_emulation` (`Fn_SDA`/`Fn_SCL`/`Fn_PWR`, `BATT_SDA`/`BATT_SCL`,
`SDA_Top`/`SCL_Top`, `+3V3`, `GND`) and nothing else.

New nets created by this sheet:

```
+ EMU_F1_SDA:  R312.2, U310.7, U200.2      + EMU_F1_SENSE:   R314.2, U200.40
+ EMU_F1_SCL:  R313.2, U310.2, U200.3      + EMU_F2_SENSE:   R324.2, U200.41
+ EMU_F2_SDA:  R322.2, U311.7, U200.4      + EMU_F3_SENSE:   R334.2, U200.42
+ EMU_F2_SCL:  R323.2, U311.2, U200.5      + EMU_F4_SENSE:   R344.2, U200.43
+ EMU_F3_SDA:  R332.2, U312.7, U200.7      + EMU_F5_SENSE:   R354.2, U200.36
+ EMU_F3_SCL:  R333.2, U312.2, U200.8      + EMU_FC3V3_SENSE: R374.2, U200.34
+ EMU_F4_SDA:  R342.2, U313.7, U200.9
+ EMU_F4_SCL:  R343.2, U313.2, U200.10     + /Solar and Sensor Emulation/F0_DEV_SDA:
+ EMU_F5_SDA:  R352.2, U314.7, U200.12         R302.2, U300.7, U301.6, U302.2, U303.3
+ EMU_F5_SCL:  R353.2, U314.2, U200.13     + /Solar and Sensor Emulation/F0_DEV_SCL:
+ EMU_BATT_SDA: R362.2, U315.7, U200.14        R303.2, U300.2, U301.1, U302.5, U303.2
+ EMU_BATT_SCL: R363.2, U315.2, U200.15    + /Solar and Sensor Emulation/F0_COIL_P:
+ EMU_TOP_SDA:  R372.2, U316.7, U200.16        J300.1, R304.1, U303.7
+ EMU_TOP_SCL:  R373.2, U316.2, U200.17    + /Solar and Sensor Emulation/F0_COIL_N:
                                               J300.2, R304.2, U303.9
```

All 20 contract nets land on the Emulator MCU (U200) as brief §4.2 requires — the hand-off is verified end to
end in this netlist, not just by name.

Components added by this sheet: **69** = 8 × TCA4311A + TMP112 + VEML6031X00 + DRV2605L (11 ICs)
+ **38 resistors** (17 × 10 k, 20 × 4.7 k, 1 × 43 R) + 12 capacitors + 1 header + 7 test points.
Plus 30 power symbols (`#PWR301`–`#PWR330`: 25 GND, 5 +3V3), which carry no BOM line.

### 8.4 PDF read-back

> **SUPERSEDED — this paragraph was wrong.** "No overlapping text" was asserted from a 300 dpi eyeball of the
> whole A3 page and was false: 19 wire segments ran straight through global-label hexagons and 20 more ran
> through symbol reference/value text. Verifier finding 2 caught it; §11 has the sweep, the fix and the tool
> that now proves it. Read §11, not this paragraph.

`kicad-cli sch export pdf` on the harness root, page for this sheet read and inspected at 300 dpi: no
overlapping text, all labels sit on wire ends, junction dots appear wherever three or more wires meet, all
eight functional areas are boxed and titled, and the design-note column clears both the Face-0 area and the
A3 title block. Two rendering bugs found and fixed during review (fields on 90°-rotated symbols were coming
out vertical — `SCH_FIELD::GetDrawRotation()` swaps horizontal/vertical on a rotated symbol, so those fields
now carry angle 90; and the multi-line note blocks are now anchored at their vertical centre, which is where
KiCad puts a multi-line text's origin).

## 9. Open questions for the reviewer / PM

1. **The 6 `power_pin_not_driven` errors on `F0_PWR`…`F5_PWR` cannot be cleared from this sheet.** Root cause:
   the face rails are driven by the AP22653 load switches (U19/U21/U22/U23/U24/U27), whose symbol Output pin is
   typed **`output`**, not `power_out`. KiCad only accepts `power_out` or `PWR_FLAG` as a driver for a
   `power_in` pin, and the TCA4311A VCC pin is `power_in`. Brief §4.2's premise — "the FC already has
   power-output pins on those" — does not hold for `Fn_PWR`.
   I **tested the PWR_FLAG alternative** (6 flags, one per face rail) rather than guessing: it clears all six
   errors on this sheet but produces **six new errors on the flight-heritage `/Power Systems/Load Switches/`
   sheet** — `Pins of type Output and Power output are connected` on U19/U21/U22/U23/U24/U27 pin 6 — because the
   project's ERC pin matrix (`FlatSat_V1.kicad_pro`) scores Output × Power-out as an error. So the PWR_FLAG
   trades six errors on a new sheet for six on an untouchable one, and the brief forbids it anyway. **Left as
   is.** Recommended resolutions, in order:
   a. add six `erc_exclusions` entries in `FlatSat_V1.kicad_pro` (integrator's file, one-line-per-error, no
      schematic change); or
   b. give the project-local AP22652/AP22653 symbol a `power_out` Output pin — the real fix, but it changes FC
      symbol metadata and would then also want the PWR_FLAG question revisited; or
   c. downgrade `power_pin_not_driven` to warning project-wide — note the Rev2 baseline already ships **6** of
      these errors (`+3V3`, `VBUS`, `VBUSP`, `+1V1`, `VREG_AVDD`, one on `/Power Systems/`), so the FC is not
      clean on this rule today either.
   Whichever is chosen, it is an integrator/PM decision, not a sheet-agent one.
2. **Is the Face-0 reading in §7.2 the intended one?** (real Face-0 devices allowed on `F0_PWR`).
3. **AP22653 current-limit headroom** for the 77 mA R304/magnetorquer burst on `F0_PWR` (§7.3) — outside this
   sheet, but nobody else is looking at it.
4. **`R304` / `J300` still need LCSC numbers** (§3).
5. **Should the emulated channels get a READY-visible path?** Right now READY is only pulled up locally and not
   routed to the emulator, matching the real boards. If the Phase-3 firmware wants to know when its own buffer
   has connected, that would be 7 more GPIOs — out of budget on the RP2350A, so probably not, but recording it.
6. **Face-0 DRV2605L OUT+/OUT− are 2 pins on a 2.54 mm header.** If the bench magnetorquer draws the full
   77 mA continuously the header is fine, but the 2010 R304 must be de-populated first — this is an assembly
   note on the sheet and should become an ATP line.

---

## 10. Fix round (2026-09-14, after independent verification)

Four defects were raised against the first version. Three are fixed in this file; the fourth is a blocker whose
only fixes live in files this agent is forbidden to write (hard rule §3.2), so it is escalated with a
**measured, ready-to-apply patch** below.

| # | verifier finding | severity | disposition |
|---|---|---|---|
| 1 | ERC errors (`power_pin_not_driven`) remain on the sheet | blocker | **Not fixable from this sheet.** Verified integrator patch + measurements in §10.1. Residual on the sheet: **5 errors** (see §10.1 on why the count moved from 6 to 5). |
| 2 | "Loading (brief 6.2)" text note contradicts the sheet (omits the EN/READY straps and the probe pad) | minor | **Fixed** — note reworded on the sheet; report §7.2 corrected to describe faces 1–5 as well as Face 0. |
| 3 | Report parts table / component counts wrong (29× vs 31× 10 k, 35 vs 38 resistors, 32 vs 30 power symbols) | minor | **Fixed** — all three corrected from a parse of the sheet file; a "Counts, parsed from the sheet file" block was added under §3 so the integrator's BOM roll-up has one authoritative source. |
| 4 | Rule §3.10 (≤ 8.2 k on emulator inputs) vs the 10 k on `EMU_*_SDA/SCL` never flagged | minor | **Fixed** — new report item §7.7b and a new DESIGN NOTES block on the sheet; handed to `emulator_mcu` as a GPIO-map requirement. |

Changes to the sheet, all via the generator (`tools/gen/solar_emulation_gen.py`, atomic tmp + `os.replace`):

1. `NOTE_BLOCKS` "Loading (brief 6.2)" reworded to
   *"on faces 1-5 Fn_PWR carries only the buffer VCC + 100 nF, the EN and READY 10 k straps, the two 10 k
   device-side pull-ups, the 4.7 k sense tap and a probe pad - no other load."*
2. New note block **"RP2350 ERRATUM E9 vs THE 10 k I2C PULL-UPS (brief rule 10 vs brief 4.2 / 6.2)"**, placed
   in the free band at (20.32, 254.0) below the FACE 5 box — the right-hand note column already runs down to
   the FACE 3 box and had no room. It states the 120 µA × 10 k = 1.2 V vs V_IL(max) 0.99 V arithmetic and the
   firmware requirement (input buffer disabled while `EMU_Fn_SENSE` is low, or the PM accepts the E9 floor).

**No electrical change.** The netlist diff is identical to §8.3 — same nets, same pins, same 69 components;
only text and item UUIDs moved.

### 10.1 The blocker: `power_pin_not_driven` on `F0_PWR`…`F5_PWR`

**Root cause (verified, unchanged from §9.1):** `Power_Management:AP22652` — the symbol behind the six face
load switches U19/U21/U22/U23/U24/U27 — declares pin 6 as `(pin output line … (name "Output"))`, not
`power_out`. KiCad accepts only `power_out` (or a PWR_FLAG) as a driver for a `power_in` pin, and the
TCA4311A VCC pin is correctly typed `power_in`. Nothing placed on this sheet can create a driver:

* a PWR_FLAG on `Fn_PWR` is forbidden by brief §4.2 **and** moves the six errors onto the flight-heritage
  `/Power Systems/Load Switches/` sheet (`Output` × `Power output` = error in this project's pin map) — tested,
  §9.1;
* retyping the TCA4311A VCC pin in this sheet's `lib_symbols` would be false metadata **and** would not clear
  `F0_PWR`, which also carries `Sensor_Temperature:TMP112xxDRL` pin 5 and `Driver_Haptic:DRV2605LDGS` pins 6/10,
  all correctly `power_in` KiCad-stock symbols.

**Verified integrator patch (recommended — option (a)).** In `FlatSat_V1/load_switches.kicad_sch`, in the
`(lib_symbols …)` block for `Power_Management:AP22652`, one token:

```
-				(pin output line
+				(pin power_out line
 					(at 11.43 5.08 180)
 					(length 2.54)
 					(name "Output"                     <- pin 6; the only `output line` pin at that position
```

Measured by this agent in a throwaway copy of the harness project
(`<scratch>/work_solar_emulation/trial_a`, ERC report `trial_a_erc.json`):

```
                                       before fix      after fix
error    pin_not_connected                 5              5        (= baseline)
error    power_pin_not_driven             11              6        (= baseline)
warning  pin_to_pin                      164            164
project errors                            16             11        (= post-promotion baseline)
errors on 'Solar and Sensor Emulation'     5              0
```

Zero new violations anywhere; net membership is untouched (a pin-type token is not netlist content), so the
integrator's "eight pure renames, additions only" netlist check is unaffected. This also fixes the same class
of error for anything else that ever hangs a `power_in` pin on a face rail.

**Option (b), `erc_exclusions` in `FlatSat_V1.kicad_pro`, is fragile** and is not recommended: KiCad keys an
ERC exclusion to the identity of the violating items, so every regeneration of this sheet invalidates the
entries. That fragility is not theoretical — see the count change below.

**Why the count is 5 here and 6 in the verifier's run.** Both runs have byte-identical `Fn_PWR` membership
(`F1_PWR` = C310.1, R310.1, R311.2, R312.1, R313.1, R314.1, TP301.1, U310.8, plus the FC's C48, J9, U21.6 —
structurally identical to F2…F5). The only difference is that the generator re-rolls every item UUID. Proof:
dropping the *new* `solar_emulation.kicad_sch` into the verifier's own harness project
(`<scratch>/work_solar_emulation/trial_b`) drops the `U310` violation and leaves 5; the verifier's project with
the old file reports 6. KiCad emits one `power_pin_not_driven` per undriven power net, but which pin it is
attributed to — and, apparently, whether one of them is emitted at all — depends on UUID ordering. So:
**5 errors is this run's honest number, 6 is the same defect, and neither is stable under regeneration.**
One more reason to fix the symbol rather than exclude the violations.

**Scope note.** `load_switches.kicad_sch` and `FlatSat_V1.kicad_pro` are integrator files (brief §3 rule 2:
"one agent, one writable file"; PM context: "the FC portion is flight heritage and must not change beyond
those promotions"). This agent did not write either. The patch above is applied and measured only inside the
scratch harness copy.

### 10.2 Re-run validation (post-fix, this sheet as delivered)

```
$ python3 tools/sch_lint.py solar_emulation.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/0ec7a68a-65de-4eda-8407-9dcf20e51c0b \
    --refdes-block 300-399
solar_emulation.kicad_sch: 99 symbol instances, 10 lib symbols, 177 wires, 0 errors, 0 warnings

$ SCRATCH=<scratch>/work_solar_emulation/fix1 tools/harness_erc.sh "Solar and Sensor Emulation"
harness: sheets in hierarchy: Emulator MCU | Solar and Sensor Emulation | Solar Power Injection |
                              Battery Replica and Bench Power | Pyro Inhibit and Jumpers | Bench IO

=== ERC delta vs baseline (Rev2 + 8 promotions; noise types excluded) ===
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

=== violations on sheets matching 'Solar and Sensor Emulation' ===
error    power_pin_not_driven              5     <- U300, U311, U312, U313, U314 pin 8 [VCC]; see 10.1
warning  pin_to_pin                       52     <- all "Unspecified and X", easyeda2kicad pin metadata
total 57
```

`+68` project `pin_to_pin` and `+5` `power_pin_not_driven` include the other five sheets; **52** and **5** are
this sheet's share. `single_global_label` is 0 — all 20 contract nets have their partner on disk. The
`pin_to_pin` triage table in §8.2 still applies (52 rather than 51: the same UUID-ordering effect surfaces one
extra `VEML6031X00 GND hidden pin 4 ↔ #PWR311` duplicate). **No new ERC error anywhere is caused by this
sheet.**

Netlist diff vs the post-promotion baseline — unchanged from §8.3, re-confirmed:

```
~ F0_PWR +[C300.1, C301.1, C302.1, C303.1, R300.1, R301.2, R302.1, R303.1, TP300.1,
           U300.8, U301.5, U302.6, U303.10, U303.5]
~ F1_PWR +[C310.1, R310.1, R311.2, R312.1, R313.1, R314.1, TP301.1, U310.8]        (F2..F5 identical)
~ F0..F5_SDA/SCL +[U300.6/U300.3 … U314.6/U314.3]
~ BATT_SDA +[U315.6]  ~ BATT_SCL +[U315.3]  ~ SDA_Top +[U316.6]  ~ SCL_Top +[U316.3]
~ +3V3 +[C315.1, C316.1, R360.1, R362.1, R363.1, R370.1, R371.2, R372.1, R373.1, R374.1,
         TP306.1, U315.8, U316.8]
~ GND  +[C300.2 … C316.2, C304.2, U300.4, U301.2, U301.4, U302.1, U302.4, U303.4, U303.8,
         U310.4 … U316.4]
0 nets removed, 0 pins lost anywhere.
```

All 20 new global nets land on the Emulator MCU U200:
`EMU_F1_SDA: R312.2, U200.2, U310.7` … `EMU_TOP_SCL: R373.2, U200.17, U316.2`,
`EMU_F1..F5_SENSE: Rx4.2, U200.{40,41,42,43,36}`, `EMU_FC3V3_SENSE: R374.2, U200.34`.

PDF re-read (`kicad-cli sch export pdf`, page 7 of the harness export, cropped at 200 dpi): the reworded
"Loading" block and the new E9 block both render clean — no overlapping text, the right-hand note column still
clears the FACE 3 / FACE 4 boxes, and the new bottom block sits between the FACE 5 box (ends y ≈ 249) and the
A3 frame, well clear of the title block.

> **SUPERSEDED — "no overlapping text" was wrong here too.** The two *new note blocks* did render clean, but
> the sentence was written as if it certified the whole page, and the page was not clean: see §11.

### 10.3 Still open after this round

1. **The 5 `power_pin_not_driven` errors** — needs the §10.1 one-token patch by the integrator (or a PM
   decision to exclude/downgrade). This is the only thing between this sheet and brief §10's "ERC clean".
2. **Brief §4.2 contains a false premise** the PM should correct: "the FC already has power-output pins on
   those" is not true for `Fn_PWR` (AP22652 pin 6 is `output`) and not true for `+3V3` (U10 pin 1 is also
   `output`) — which is why the Rev2 baseline already ships a `power_pin_not_driven` error on `+3V3`.
3. **Rule §3.10 vs §4.2/§6.2 on the 14 `EMU_*_SDA/SCL` nets** (§7.7b) — needs the `emulator_mcu` GPIO map to
   record "input buffer disabled while the face is off", or a PM acceptance of the E9 floor.
4. Unchanged from §9: `R304` and `J300` need LCSC numbers; AP22653 current-limit headroom for the 77 mA
   magnetorquer burst on `F0_PWR`; the Face-0 reading of §6.2's last bullet (§7.2).

---

## 11. Fix round 2 (2026-09-14, after the second independent verification)

Two findings were raised. Both are addressed below; one is fixed in this agent's own files, the other is
still the integrator's one-token patch and is re-measured here against the files as they stand today.

| # | verifier finding | severity | disposition |
|---|---|---|---|
| 1 | ERC errors (`power_pin_not_driven`) still on the sheet | blocker | **Still not fixable from this sheet** (brief §3 rule 2). Patch re-measured on today's files in §11.1: applying it takes this sheet 6 → **0** errors and the project 17 → **11** (= post-promotion baseline). |
| 2 | Fn_PWR riser and the SCL pull-up lead drawn through the `EMU_*_SDA`/`EMU_*_SCL` label hexagons — 19 crossings; the report claimed the opposite | major | **Fixed**, and the claim retracted (§8.4, §10.2 now carry SUPERSEDED banners). The sweep found **39** crossings, not 19; all 39 are gone. §11.2. |

### 11.1 Blocker: `power_pin_not_driven` on `F0_PWR`…`F5_PWR` — integrator patch, re-measured

Root cause is unchanged and is not on this sheet (§9.1, §10.1): `Power_Management:AP22652`, the symbol behind
the six face load switches U19/U21/U22/U23/U24/U27, declares pin 6 as `output`, not `power_out`, so KiCad sees
no driver for the correctly typed `power_in` VCC pins hanging on `F0_PWR`…`F5_PWR`. A PWR_FLAG here is
forbidden by brief §4.2 and would move six errors onto the flight-heritage Load Switches sheet
(`pin_map[output][power_out] = 2 = error` in `FlatSat_V1.kicad_pro`); `erc_exclusions` are keyed to item
identity, which this sheet's generator re-rolls every run. So the patch belongs to the integrator.

**The patch** — `FlatSat_V1/load_switches.kicad_sch`, inside the `(lib_symbols …)` block for
`Power_Management:AP22652`, one token, exactly one occurrence in the file:

```
-				(pin output line
+				(pin power_out line
 					(at 11.43 5.08 180)
 					(length 2.54)
 					(name "Output"            <- pin 6; the only `output line` pin at that position
```

**Measured today** in a throwaway copy of the harness project
(`<scratch>/work_solar_emulation/r2/trial`, ERC report `erc_after.json`), with the fix-round-2 sheet and all
five sibling sheets on disk:

```
                                          before patch   after patch
error    pin_not_connected                     5             5       (= baseline)
error    power_pin_not_driven                 12             6       (= baseline)
warning  pin_to_pin                          163           164
project errors                                17            11       (= post-promotion baseline)
errors on 'Solar and Sensor Emulation'         6             0
errors on 'Load Switches'                      0             0
```

A per-violation diff of the two ERC reports (not just the counts) shows the patch removes exactly six items —
`power_pin_not_driven` on U300/U310/U311/U312/U313/U314 pin 8 — and adds exactly one:
`pin_to_pin: Unspecified and Passive | R312.2 ; U310.7`, another instance of the `easyeda2kicad`
pin-metadata class this sheet already contributes 51 of. **No new error anywhere, on any sheet.** Net
membership is untouched (a pin-type token is not netlist content), so the integrator's "eight pure renames,
additions only" netlist check is unaffected.

**On the error count being 5 in the verifier's run and 6 here.** The verifier was right that the number is not
stable: this round's runs report 6 (all six face rails), the previous round reported 5 (F1/U310 missing). The
sheet file is byte-identical between the two runs of this round that differ only by the load-switch token, and
one `pin_to_pin` item still moved between them, so the instability is KiCad's, not the sheet's. **Treat the
target as zero, not as a number.**

### 11.2 Major: wires drawn through label and field text

**What was actually there.** A geometric sweep of the round-1 file — every wire segment against every drawn
text body, using KiCad's own label geometry (`GetLabelBoxExpansion` margin = 0.375 × size; global-label body =
text + 2 × margin + body height) and a deliberately generous 0.95 em stroke-font advance — found **39** wire
crossings, not 19:

| count | what | cause |
|---|---|---|
| 19 | wires through `EMU_*_SDA` / `EMU_*_SCL` global-label hexagons | exactly the set the verifier listed: the Fn_PWR riser at `X+30.48` feeding the READY pull-up (2 labels × 6 blocks) and the SCL pull-up's lower lead at `X+25.4` (1 label × 7 blocks) |
| 12 | the same READY riser through the SCL pull-up's own `R3n3` / `10k` field text | same riser, never noticed |
| 1 | R303's lower lead through the Face-0 `F0_DEV_SDA` local label | the Face-0 copy of the same topology |
| 7 | wires through `U301` / `U302` / `DRV2605LDGS` / `R304` / `43R` symbol field text | fields left at the default offset, sitting on a supply riser |

The verifier's connectivity reading was right and is re-confirmed: none of it was an electrical defect. The
netlist below is pin-for-pin identical to §8.3.

**The fix — a routing rule, applied to all eight blocks.** A global label's hexagon is drawn to the *right* of
its anchor, so nothing vertical may live inside that band. Every `EMU_*` / `F0_DEV_*` label now terminates its
exit wire at the right-hand end of the block, and every riser stays to its left:

```
        Fn_PWR ------.                    top rail, feeds the SDA pull-up ONLY
                     R{n}2
        SDAOUT ------+--------> EMU_Fn_SDA        (hexagon runs right into clear space)
        SCLOUT --+------------> EMU_Fn_SCL
                 R{n}3                    SCL pull-up hangs BELOW the exits
        READY -R{n}1-.
                     `--------> Fn_PWR    second tap on the same net
```

The SCL pull-up and the READY pull-up are now fed from a second `Fn_PWR` (or `+3V3`) tap below the exits
instead of from the top rail, which is what removes the long riser. Each block therefore shows its supply
label at three points — buffer VCC, SDA pull-up rail, SCL+READY tap. They are one net; a new sheet note
**"READING THE CHANNEL BLOCKS"** says so and says why, so the split is not read as three different rails.
Face 0 got the same treatment (R303 and R301 moved below the exits, the pin-4 GND dropped straight down),
and the five stray symbol fields were moved off their risers (`U301`, `U302`, `U303` value, `R304` to
`side='left'`).

**Pin numbering was preserved on purpose.** The two pull-ups that moved below their exits (`R{n}3`, Face-0
`R303`) are placed `rot 180` so pin 1 still sits on `Fn_PWR` and pin 2 on the signal — otherwise the netlist
would have shown `F1_PWR +[… R313.2 …]` instead of `R313.1` and the integrator's diff would have had a
spurious change to explain. Their reference/value fields are **centred** rather than left/right justified,
because KiCad applies the symbol transform to a field's justification and left/right would flip on a
180° symbol.

**Proof, not eyeball.** The sweep is now a tool, `FlatSat_V1/tools/gen/geomcheck.py`:

```
$ python3 tools/gen/geomcheck.py solar_emulation.kicad_sch --overlaps
solar_emulation.kicad_sch: 191 wires, 269 text bodies
--- wire-through-text: 0 ---
--- text-over-text: 0 ---
```

It was calibrated against the round-1 file first (it reproduced the verifier's 19 label crossings exactly,
including the same anchor and body coordinates, before finding the other 20). The `--overlaps` pass also
caught two text-on-text collisions introduced while fixing the wires — the new note block running into the
FACE 3 / FACE 4 titles — which is why that note now sits in the free band at (160.02, 254.0) next to the E9
note instead of at the bottom of the right-hand note column. Three block titles and the five per-face
"VCC = Fn_PWR …" notes were shortened so each stays inside its own box (the boxes were widened from
±43.18 mm to ±45.72 mm, which keeps a 5.08 mm gap between columns and leaves the FACE 4 / test-point column
inside the A3 frame).

The render was then read back (`pdftoppm -r 600`, page 7 of the harness export, crops of FACE 1, the Face-0
buffer and the BATT channel plus the full page): every exit label is clear of every wire, the junction dots
are where three wires meet, and the two bottom note blocks clear the A3 title block.

### 11.3 Re-run validation (fix round 2, as delivered)

```
$ python3 tools/sch_lint.py solar_emulation.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/0ec7a68a-65de-4eda-8407-9dcf20e51c0b \
    --refdes-block 300-399
solar_emulation.kicad_sch: 101 symbol instances, 10 lib symbols, 191 wires, 0 errors, 0 warnings

$ SCRATCH=<scratch>/work_solar_emulation/r2/harness2 tools/harness_erc.sh "Solar and Sensor Emulation"
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

=== violations on sheets matching 'Solar and Sensor Emulation' ===
error    power_pin_not_driven              6     <- U300, U310, U311, U312, U313, U314 pin 8 [VCC]; §11.1
warning  pin_to_pin                       51     <- all "Unspecified and X", easyeda2kicad pin metadata
total 57
```

`+6` and `+67` in the project delta include the other five sheets; **6** and **51** are this sheet's share.
With the §11.1 patch applied the sheet line becomes `errors: 0` and the project line `errors: 11`.
`single_global_label` is 0 — all 20 contract nets have their partner sheet on disk. The `pin_to_pin` triage
table in §8.2 still applies unchanged; every one of the 51 is an `easyeda2kicad` `unspecified` pin meeting a
correctly typed pin, and the FC baseline already ships 96 of the same class.

**Netlist diff vs the post-promotion baseline — unchanged from §8.3 / §10.2, re-confirmed pin for pin:**

```
~ F0_PWR   +[C300.1, C301.1, C302.1, C303.1, R300.1, R301.2, R302.1, R303.1, TP300.1,
             U300.8, U301.5, U302.6, U303.10, U303.5]
~ F1_PWR   +[C310.1, R310.1, R311.2, R312.1, R313.1, R314.1, TP301.1, U310.8]   (F2..F5 identical)
~ F0..F5_SDA/SCL +[U300.6/U300.3 … U314.6/U314.3]
~ BATT_SDA +[U315.6]   ~ BATT_SCL +[U315.3]   ~ SDA_Top +[U316.6]   ~ SCL_Top +[U316.3]
~ +3V3     +[C315.1, C316.1, R360.1, R362.1, R363.1, R370.1, R371.2, R372.1, R373.1,
             R374.1, TP306.1, U315.8, U316.8]
~ GND      +[C300.2 … C316.2, C304.2, U300.4, U301.2, U301.4, U302.1, U302.4, U303.4,
             U303.8, U310.4 … U316.4]
0 nets removed, 0 pins lost anywhere; 69 components added by this sheet.

+ EMU_F1_SDA: R312.2, U200.2, U310.7        + EMU_F1_SENSE:    R314.2, U200.40
+ EMU_F1_SCL: R313.2, U200.3, U310.2        + EMU_F2_SENSE:    R324.2, U200.41
+ EMU_F2_SDA: R322.2, U200.4, U311.7        + EMU_F3_SENSE:    R334.2, U200.42
+ EMU_F2_SCL: R323.2, U200.5, U311.2        + EMU_F4_SENSE:    R344.2, U200.43
+ EMU_F3_SDA: R332.2, U200.7, U312.7        + EMU_F5_SENSE:    R354.2, U200.36
+ EMU_F3_SCL: R333.2, U200.8, U312.2        + EMU_FC3V3_SENSE: R374.2, U200.34
+ EMU_F4_SDA: R342.2, U200.9, U313.7
+ EMU_F4_SCL: R343.2, U200.10, U313.2       + /Solar and Sensor Emulation/F0_DEV_SDA:
+ EMU_F5_SDA: R352.2, U200.12, U314.7           R302.2, U300.7, U301.6, U302.2, U303.3
+ EMU_F5_SCL: R353.2, U200.13, U314.2       + /Solar and Sensor Emulation/F0_DEV_SCL:
+ EMU_BATT_SDA: R362.2, U200.14, U315.7         R303.2, U300.2, U301.1, U302.5, U303.2
+ EMU_BATT_SCL: R363.2, U200.15, U315.2     + /Solar and Sensor Emulation/F0_COIL_P:
+ EMU_TOP_SDA:  R372.2, U200.16, U316.7         J300.1, R304.1, U303.7
+ EMU_TOP_SCL:  R373.2, U200.17, U316.2     + /Solar and Sensor Emulation/F0_COIL_N:
                                                J300.2, R304.2, U303.9
```

### 11.4 Still open after this round

1. **The 6 `power_pin_not_driven` errors** — needs the §11.1 one-token patch by the integrator (or a PM
   decision to downgrade the rule project-wide). Still the only thing between this sheet and brief §10's
   "ERC clean". Measured, zero side effects, ready to apply.
2. Unchanged from §10.3: brief §4.2's "the FC already has power-output pins on those" is false for `Fn_PWR`
   (AP22652 pin 6 is `output`) and for `+3V3` (U10 pin 1 is `output`) — the PM should correct the brief;
   rule §3.10 vs the mandated 10 k on the 14 `EMU_*_SDA/SCL` nets needs an `emulator_mcu` GPIO-map line or a
   PM acceptance (§7.7b) — **closed: PM ruling R7, applied as fix id 3 (§13.1), 10 k → 4.7 k**;
   `R304` and `J300` need LCSC numbers; the AP22653 current-limit headroom for the
   77 mA magnetorquer burst on `F0_PWR` is nobody's sheet.
3. **New, for the other five sheet agents and the reviewer:** `tools/gen/geomcheck.py` is generic — it takes
   any `.kicad_sch` and reports wire-through-text and text-over-text. This sheet had 39 crossings that
   several rounds of human and agent PDF-reading missed. Run read-only against the five sibling sheets as
   they stand on disk right now, it reports the same class on every one of them:

   | sheet | wire-through-text | text-over-text |
   |---|---|---|
   | `emulator_mcu` | 6 | 0 |
   | `solar_power_injection` | 4 | 0 |
   | `battery_protection_replica` | 3 | 2 |
   | `pyro_inhibit` | 4 | 1 |
   | `bench_io` | 7 | 3 |

   Examples: on `emulator_mcu` the 1V1/VREG_AVDD risers at x = 133.35/135.89 run through the `3V3_EMU`
   hexagon and the `1V1_EMU` / `VREG_AVDD_EMU` local labels; on `bench_io` the SWD block wires run through
   the "Block B — Emulator SWD" title and the J4 note runs into the `FC_RESET` / `WDT_DISABLE` hexagons.
   These are **not this agent's files** and nothing was changed in them — they are reported so the review
   round can triage them (the tool's stroke-font advance is deliberately generous at 0.95 em, so a hit
   within a few tenths of a millimetre of the box edge may be marginal in the real render; every hit on
   this sheet was confirmed against a 600 dpi render before and after).

---

## 12. Integrator fix round 3 (2026-09-14)

**Ownership note.** Applied by the **integrator**, not the sheet agent, after an independent check of the first
integration pass. Brief §3 rule 2 puts `solar_emulation.kicad_sch` and `tools/gen/solar_emulation_gen.py` in
the sheet agent's writable set; that agent's run had finished. Recorded as an explicit rule deviation in
`integration_report.md` §1.2. Both the sheet and its generator were changed; the delivered sheet is the
generator's own output, with the sheet's header uuid `b052df5b-7243-43fa-8269-29ece06d5de9` restored afterwards
(the generator re-rolls item uuids on every run).

### 12.1 [major] `U303` footprint `Package_SO:VSSOP-10_3x3mm_P0.5mm` does not exist in KiCad 10

Inherited verbatim from the XY_Face_V4 reference board. `Package_SO.pretty` in KiCad 10 carries
`TSSOP-10_3x3mm_P0.5mm` and `HVSSOP-10-1EP_3x3mm_P0.5mm…` but **no** `VSSOP-10_3x3mm_P0.5mm`, so the project
ERC raised one `footprint_link_issues` warning (`23 → 24` against the Rev2 baseline, reported under sheet path
`/`, which is why a per-sheet filter missed it) and **layout could not place U303**.

Fixed to **`Package_SO:TSSOP-10_3x3mm_P0.5mm`** — the same 3 × 3 mm body, 0.5 mm pitch, 10 pins, no thermal
pad, which is the DRV2605L **DGS** land. Changed in **both** places the string occurred: the U303 instance and
the cached `lib_symbols` default for `Driver_Haptic:DRV2605LDGS`. The generator now applies that correction
through a new `LIB_FIXUPS` table in `lib_block()`, so a GUI *Update Symbols from Library* cannot put the
dangling name back and a regeneration cannot reintroduce it.

Measured: project `footprint_link_issues` **24 → 23 = the Rev2 baseline**, and a sweep of all **39** distinct
footprints used by the six new sheets against `fp-lib-table` + the KiCad standard libraries + the user's
`easyeda2kicad.pretty` now returns **0 unresolved**.

### 12.2 [minor] `R304` was a 0805 dissipating 0.253 W

`3.3 V² / 43 Ω = 0.253 W`, which is 200 % of a stock 0805 thick-film part's 0.125 W rating and 101 % of a 1206.
The old mitigation was the qualitative instruction "drive in bursts". Package raised to
**`Resistor_SMD:R_2010_5025Metric` (0.75 W)** — 34 % of rating, so continuous full-amplitude drive is within
spec — and the sheet note now carries a numeric limit (**≤ 50 % duty** at full amplitude) instead of "in
bursts". `Description` updated to "XY_Face_V4 PCB coil DC-resistance equivalent, 2010 0.75 W (0.253 W worst
case)". The value stays 43 Ω; R304 still has no LCSC (rule 5) and remains on the needs-LCSC list.

R304 is the coil-emulation dummy load, removed when a real magnetorquer is plugged into J300, and is on no
flight path.

### 12.3 [minor] No warning against mixing real and emulated boards

Every emulated channel reproduces its real board's address map on the same TCA9548 channel, and the FC
connectors stay populated (D11 keeps J14 populated on purpose). Plugging a real board in therefore puts two
devices at one address on one channel — an address clash, not merely a duplicate load. The equivalent warning
existed only on `battery_protection_replica` (the D11 note about J14).

Two lines appended to the sheet's I2C-map note in the DESIGN NOTES column:

```
DO NOT plug a real face board into J1/J2/J6/J9/J11/J13, a real pack into J14 or a real top-cap
into J16 while this emulation is fitted: both answer at one address on that channel (D11).
```

The note column is vertically packed by `notes()`, so adding two lines pushes the three blocks below it down by
2 × 2.0574 mm; the last of them (the D7 note) now ends at y = 121.4 mm, still clear of the row-2 channel-block
rectangles that start at y = 123.19 mm. Confirmed in the render, not just the arithmetic.

### 12.4 Re-run validation (fix round 3, as delivered)

```
python3 tools/sch_lint.py solar_emulation.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/0ec7a68a-65de-4eda-8407-9dcf20e51c0b --refdes-block 300-399
  -> 101 symbol instances, 10 lib symbols, 191 wires, 0 errors, 0 warnings

python3 tools/gen/geomcheck.py solar_emulation.kicad_sch --overlaps
  -> 191 wires, 269 text bodies; wire-through-text: 0; text-over-text: 0

kicad-cli sch erc --severity-all (full integrated project)
  -> erc_summary.py --sheet "Solar and Sensor Emulation" --ignore-noise : total 52, errors: 0
     (the 52 are the same Unspecified-pin `pin_to_pin` library-metadata class triaged in §11;
      the 6 `power_pin_not_driven` errors of round 2 stay cleared by the integrator's AP22652
      pin-type fix in load_switches.kicad_sch)
  -> project footprint_link_issues 23 = Rev2 baseline (was 24)
```

Netlist contribution unchanged pin-for-pin — a footprint string and a text note are not netlist topology. The
regenerated file differs from the round-2 file in exactly 20 lines (and the item uuids): the three note
strings, the four note anchors they shift, the U303 footprint ×2, and R304's footprint and Description.

### 12.5 Still open after this round

1. `R304` (43 Ω 2010 ≥ 0.5 W) and `J300` still need LCSC numbers.
2. ~~The E9-vs-10 k pull-up conflict (§11.4) is unchanged — still a firmware requirement, printed on the
   sheet.~~ **Resolved in the Fable review round by fix id 3 (§13.1): PM ruling R7, 10 k → 4.7 k on the 14
   emulated-channel device-side pull-ups; rule 10 is now met in hardware.**
3. AP22653 current-limit headroom on `F0_PWR` for the 77 mA magnetorquer burst — still outside this sheet.

## 13. Review fixes (2026-09-14, Fable review-and-fix round)

**Ids applied on this sheet: 3.** (`fix-now`, owner file `solar_emulation`.)

### 13.1 [id 3, major] R7 not applied — 14 emulated-channel device-side I2C pull-ups were still 10 k

**Change.** `R312 R313 R322 R323 R332 R333 R342 R343 R352 R353 R362 R363 R372 R373`
(the device-side SDA/SCL pull-ups on EMU_F1…F5 / BATT / TOP): `10k` / `C25744` → **`4.7k` / `C25900`**.
`R302 R303` (Face 0, golden reference) stay **10 k** per PM ruling R7. The EN and READY straps
(`R310 R311 R320 R321 R330 R331 R340 R341 R350 R351 R360 R370 R371`) stay 10 k — TI SCPS226C §8.3.2
specifies 10 k for READY, and they are not emulator inputs. The 4.7 k sense taps
(`R314 R324 R334 R344 R354 R374`) were already correct.

**Why.** PM brief §11 R7 allows and prefers this fix-now. Brief rule 10 requires every emulator input to be
pulled through ≤ 8.2 kΩ so RP2350 A2 erratum E9 (an enabled input buffer leaks up to 120 µA) cannot hold the
pad above `VIL(max) = 0.3 × IOVDD = 0.99 V`. With the face switched off the pull-up rail `Fn_PWR` is not an
ideal ground: the AP22653 discharges it through an internal NMOS of **600 Ω typ** (Diodes DS41186, AP22652/
AP22653 Electrical Characteristics, `VIN = 5 V`, disabled, `IOUT = 1 mA`; "the discharge function is active
when the device is disabled"). So the E9 path is pull-up + R_DIS:

| device-side pull-up | path to GND with the face off | 120 µA × R | vs VIL(max) 0.99 V | rule 10 (≤ 8.2 k) |
|---|---|---|---|---|
| 10 k (as captured) | 10 k + 0.6 k = **10.6 k** | 1.27 V | **fails** | fails |
| 4.7 k (this fix)   | 4.7 k + 0.6 k = **5.3 k**  | 0.64 V | passes | passes |

Rule 10 is now met in hardware. The firmware rule printed on the sheet (EMU_\*_SDA/SCL input-buffer-disabled
while `EMU_Fn_SENSE` is low) is retained as belt-and-braces, but is no longer the only guard.
`BATT`/`TOP` pull up to the FC `+3V3`, which is off only when the whole FC is off; they take 4.7 k for
consistency and because the same emulator GPIOs read them.

**Loading check at 4.7 k** (the id-3 verification item). Rail 3.3 V, so each pull-up sources
`3.3 V / 4.7 kΩ = 0.70 mA` into whatever holds the line low. The TCA4311A `SDAOUT`/`SCLOUT` and `READY`
outputs are specified to sink **3 mA at VOL = 0.4 V** (TI SCPS226C §6.5 / §8.3.2), so one 4.7 k pull-up is
23 % of the sink budget — the same margin the already-fitted 4.7 k FC-side pull-ups (R44 R45 R61 R62 R88 R89
R105 R106 …) impose on the bus side. The RP2350 open-drain pads sink ≥ 4 mA at the default drive strength.
Nothing else on `Fn_PWR` changes: 4.7 k adds 0.70 mA − 0.33 mA = 0.37 mA per line over the 10 k version only
while a line is low, which is inside the AP22653 headroom quantified in §7.3. Rise time improves (RC halves).

**Sheet notes rewritten with the value change.**

* Heading `RP2350 ERRATUM E9 vs THE 10 k I2C PULL-UPS   (brief rule 10 vs brief 4.2 / 6.2)`
  → `RP2350 ERRATUM E9 AND THE 4.7 k DEVICE-SIDE PULL-UPS   (brief rule 10; PM R7)`.
* Body: now states the hardware guarantee (4.7 k + AP22653 R_DIS 600 Ω typ = 5.3 k ≤ 8.2 k,
  120 µA × 5.3 k = 0.64 V < 0.99 V), that the firmware input-buffer-disable rule is belt-and-braces,
  that BATT/TOP sit on FC `+3V3`, that Face 0 keeps 10 k per R7, and the 0.70 mA / 3 mA VOL loading number.
  Grew 9 → 13 lines, so `block_note()` re-centred its anchor `(at 20.32 266.0396)` → `(at 20.32 270.1544)`.
* `Loading (brief 6.2)` note: "the two 10 k device-side pull-ups" → "the two 4.7 k device-side pull-ups
  (PM ruling R7; Face 0 keeps its 10 k)", and "back-powered through its 10 k pull-ups" → "its 4.7 k pull-ups".
  Deliberately kept at 8 lines so the right-hand note column does not grow into the FACE 3 box.

**Generator.** `tools/gen/solar_emulation_gen.py` updated in the same commit so a regeneration reproduces the
sheet: `channel()` now emits `r_base+'2'` and `r_base+'3'` as `'4.7k'` / `'C25900'` (with the E9 rationale as
a code comment), the module docstring says 4.7 k, and `E9_NOTE`, the `block_note` heading and the Loading
`NOTE_BLOCKS` entry carry the new text. `face0()` is untouched, which is what keeps R302/R303 at 10 k.

### 13.2 Re-run validation (review fixes, as delivered)

```
python3 tools/sch_lint.py solar_emulation.kicad_sch --project FlatSat_V1 \
    --path /c64c0d72-a9f6-4f3a-891e-1f647558f538/0ec7a68a-65de-4eda-8407-9dcf20e51c0b --refdes-block 300-399
  -> solar_emulation.kicad_sch: 101 symbol instances, 10 lib symbols, 191 wires, 0 errors, 0 warnings

python3 tools/gen/geomcheck.py solar_emulation.kicad_sch --overlaps
  -> 191 wires, 269 text bodies; wire-through-text: 0; text-over-text: 0
     (the first heading wording overlapped "READING THE CHANNEL BLOCKS" and was shortened)

python3 tools/gen/solar_emulation_gen.py --out <scratch>/regen2.kicad_sch
  -> generator reproduces the on-disk sheet (uuid-stripped): True

SCRATCH=<scratch>/harness tools/harness_erc.sh "Solar and Sensor Emulation"
  === ERC delta vs baseline (Rev2 + 8 promotions; noise types excluded) ===
  error    pin_not_connected                 5      5     +0
  error    power_pin_not_driven              6      6     +0
  warning  multiple_net_names               12     12     +0
  warning  pin_to_pin                       96    164    +68
  warning  same_local_global_label           4      4     +0
  warning  single_global_label               9      0     -9
  warning  unconnected_wire_endpoint         1      1     +0
  total baseline 133, now 192, delta +59 ; errors: 11 (all on FC sheets, byte-identical to Rev2)

  === violations on sheets matching 'Solar and Sensor Emulation' ===
  warning  pin_to_pin                       52 ; total 52 ; errors: 0
     (the same Unspecified-pin library-metadata class triaged in section 11 — known noise)

  netlist: components base 261, new 477, added 216, removed 0 ; nets base 215, new 355,
           added 117, removed 0, changed 38 (all gained pins, none lost) — unchanged by this fix
```

**Value-only proof.** Diff of the pre-fix and post-fix sheet with `(uuid …)` lines stripped:

```
 14 >     (property "Value" "4.7k"          14 <     (property "Value" "10k"
 14 >     (property "LCSC Part" "C25900"    14 <     (property "LCSC Part" "C25744"
  1 >     (at 20.32 270.1544 0)              1 <     (at 20.32 266.0396 0)   [E9 note anchor]
    plus the three note strings
```

No wire, junction, label, pin, power symbol or symbol placement changed — connectivity is bit-identical.
Confirmed independently in the exported netlist: R312 R313 R322 R323 R332 R333 R342 R343 R352 R353 R362 R363
R372 R373 = `4.7k` / `C25900`; R300–R303, R310 R311, R320 R321, R330 R331, R340 R341, R350 R351, R360,
R370 R371 = `10k` / `C25744`; R314 R324 R334 R344 R354 R374 = `4.7k` / `C25900` (unchanged).

**PDF read-back** (`kicad-cli sch export pdf --pages 8`): every emulated channel now prints `4.7k` on both
device-side pull-ups; Face 0 still prints `10k` on R302/R303; the EN/READY straps still print `10k`; the
rewritten E9 note sits inside the frame with no overlap into "READING THE CHANNEL BLOCKS" or the title block.

### 13.3 [id 0, minor] Documentation sweep after fix id 3 (integrator round 2, 2026-09-14)

The checker found that this report had not been fully swept for the 10 k → 4.7 k value change: the
current-state text still described the emulated-channel device-side pull-ups as 10 k in places, with no
`superseded` annotation (the precedent being `sheet_pyro_inhibit.md` §12.5 items 1 and 3). **Documentation
only — `solar_emulation.kicad_sch` and `tools/gen/solar_emulation_gen.py` are correct and were not touched
by this fix** (verified: the sheet's 20 `4.7k` / 17 `10k` resistors are unchanged, and the generator still
regenerates the sheet to a 0-line uuid-stripped diff).

Lines corrected to the delivered 4.7 k (current-state prose):

| § | was | now |
|---|---|---|
| §1 (line 34) | "every connection to an FC net is a … 10 k pull-up" | "a pull-up (10 k on Face 0, 4.7 k on the emulated channels per R7)" |
| §2.2 ASCII block (lines 58–59) | `10k to Fn_PWR on the device side (Rx2/Rx3)` | `4.7k …` |
| §2.2 BATT bullet | "device-side 10 k pull-ups to `+3V3`" | "device-side **4.7 k**", with the departure-from-`battery_pack_v2` noted |
| §2.2 TOP bullet | "device-side pull-ups to `+3V3`" (no value) | "device-side **4.7 k** pull-ups", departure from `antenna_top_cap_v2c` noted |
| §3 parts table | one row "R300–R303, R310–R313 … (31×) 10k" + "(6×) 4.7k" | **17× 10 k** (Face-0 device side + every EN/READY strap) and **20× 4.7 k** (6 sense taps + 14 device-side), refdes lists rebuilt from a parse of the sheet |
| §3 counts block | "38 resistors (31 × 10 k + 6 × 4.7 k + R304)" | "38 resistors (17 × 10 k + 20 × 4.7 k + R304)" |
| §6 existing-nets table (line 120) | "the two 10 k device-side pull-ups (Rx2/Rx3)" | "the two **4.7 k** device-side pull-ups (Rx2/Rx3, PM ruling R7)" |
| §8.2 TCA4311A §8.3.1 row | "FC-side 4.7 k and device-side 10 k" | "device-side 4.7 k (10 k on Face 0)" |
| §8.3 roll-up (line 374) | "38 resistors (31 × 10 k, 6 × 4.7 k, 1 × 43 R)" | "(17 × 10 k, 20 × 4.7 k, 1 × 43 R)" |

The resistor split was re-derived from `solar_emulation.kicad_sch` itself, not from either report:
`10k` = R300 R301 R302 R303 R310 R311 R320 R321 R330 R331 R340 R341 R350 R351 R360 R370 R371 (17);
`4.7k` = R312 R313 R314 R322 R323 R324 R332 R333 R334 R342 R343 R344 R352 R353 R354 R362 R363 R372 R373 R374
(20); `43R` = R304. Total 38, unchanged, so the BOM roll-up count does not move.

Annotated rather than rewritten (they quote a superseded source or record an earlier round's state):

* §7.2 item 2 (line 213) quotes brief §6.2's literal "the two 10 k device-side pull-ups" — kept verbatim as a
  quotation, with an inline note that R7 superseded the brief's 10 k. Line 216, which enumerates what
  `F1_PWR` *actually* carries, is corrected to 4.7 k (it is current state, not a quote).
* §7.7b — the whole "the 14 `EMU_*_SDA/SCL` nets do NOT meet rule 10" paragraph now opens with **RESOLVED by
  fix id 3 (§13.1)** and the 5.3 k / 0.64 V arithmetic, with the old text kept below as *superseded*.
* §11 "still open" (line 788) and §12.5 item 2 — both annotated closed by R7 / fix id 3.
* §10 and §11 fix-round narratives (the "10 k" strings at lines 442–446) and the §12 geometry census
  (line 656, a wire-through-`10k`-field-text count) are **left as written**: they are dated records of what
  those rounds did, and rewriting them would falsify the history. §13.1 is the authority on the value.

### 13.4 Still open after this round

1. `R304` (43 Ω 2010 ≥ 0.5 W) and `J300` still need LCSC numbers — deferred to the layout-phase supply-chain
   pass (PM ruling R12), not a finding.
2. AP22653 current-limit headroom on `F0_PWR` for the 77 mA magnetorquer burst — outside this sheet (R11).
3. Item 2 of §12.5 (the E9-vs-10 k conflict) is **closed** by fix id 3.
