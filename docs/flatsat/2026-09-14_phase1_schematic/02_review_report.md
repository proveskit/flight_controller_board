# FlatSat V1 Phase 1 — Review-board report (chair sign-off)

Date: 2026-09-14. Scope: the six new Phase-1 sheets (`emulator_mcu`, `solar_emulation`,
`solar_power_injection`, `battery_protection_replica`, `pyro_inhibit`, `bench_io`) plus the
integrated root `FlatSat_V1.kicad_sch`. Baseline for comparison: Rev2 FC (`tools/baseline/erc.json`,
`tools/baseline/netlist.kicadxml`) and the post-promotion baseline (`tools/baseline/erc_promoted.json`).
All numbers in this report were re-run by the chair from the delivered files on 2026-09-14
(`kicad-cli` 10.0.1); artifacts in
`/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/review_chair/`.

---

## 1. Scope of the five review lenses

| Lens | What it covered |
|---|---|
| **Electrical** | Net-contract conformance (brief §4.1/4.2) across all defined nets and refdes 200–799; full pin maps of U200-U202, U300-U303, U500, U510/U511, Q510, Q701-703, J510, J701, SW703; comparison against reference netlists (battery_pack_v2, XY_Face_V4, antenna_top_cap_v2c, debug_board_v1) and datasheets (R5460, BQ25886, TCA4311A, TPS4H160, DZDH0401DW, AP22652/53, RP2350-E9); hard rules 6/8/9; every emulator↔FC current path; ERC on the six new sheets. |
| **Datasheet** | Refdes/value/footprint/pin↔net parity against RP2350 hardware design guide, W25Q128JVS, AP2112K-3.3, TCA4311A (SCPS226), TMP112, VEML6031X00, DRV2605L (SLOS854), R5460N208AA, BQ25886 (SLUSD88A), DZDH0401DW+DMP4047, CDBA240LL-HF/PTC fuse, BAT54W, BSS138, USB-C/JST-SH SWD pinouts. Confirmed R5/R6/R7 were **not yet applied** at review time. |
| **Bench-safety** | Bench-usability and safety across the six sheets and their FC interfaces: PSU-through-replica, USB→BQ25886, VSOLAR injection, inhibit engaged/released, emulator-on/FC-off and reverse, JP602-607 combinations, real hardware on J6/J14/J16. Verified no bench circuit can raise a flight net, default jumper states match the brief, and confirmed R5/R6/R7 not yet applied. |
| **Integrity** | Project hygiene: ERC (`--severity-all`), `erc_summary.py --baseline …--ignore-noise`, `netlist_diff.py`, `sch_lint.py` on all six sheets, refdes/uuid/footprint/lib_id resolution, LCSC coverage, root sheet-symbol placement, generator reproducibility, `connector_trace.md` cross-check (147/147 rows), `integration_report.md` triage of W1-W10. |
| **Firmware** | Phase-3/4 usability: FC baseline netlist traced (TCA9548, MCP23017, AP22653, TPS4H160, TPS2HB50, WDT_DISABLE, USBBOOT, FC_RESET paths) against proves-core-reference (dtsi, `ReferenceDeploymentTopology.cpp`, `topology.fpp`, `Drv2605Manager`/`Tmp112Manager`/`Veml6031Manager`, Zephyr `drv2605.c`/`tmp112.c`/`veml6031.c`, HWIL tests). Confirmed TCA4311A orientation, EN/READY straps, GPIO↔I2C pin-mux, E9 exposure math, and R5/R6/R7 not yet applied. |

Out of scope for all five lenses (per PM instruction): unchanged FC flight-heritage circuitry beyond
the already-logged findings F1-F4 (`integration_report.md` §7a); library-metadata ERC noise
(`lib_symbol_issues`, `lib_symbol_mismatch`, `footprint_link_issues`, `endpoint_off_grid`, `pin_to_pin`
on an Unspecified-typed pin); outstanding LCSC numbers (deferred to the layout-phase supply-chain pass,
PM ruling R12); the PM's own §11 rulings R1-R15 (dispositioned already — verifying R5/R6/R7 were *carried
out* was in scope, re-litigating them was not).

---

## 2. Prioritized findings — disposition and fix verification

Three PM fix-now rulings (R5 CSYS≥44 µF, R6 R600 100 k→4.7 k, R7 4.7 k device-side pull-ups on the
7 emulated channels) were confirmed **not yet applied** by all five lenses at review time and are
ranked 1-3. Ranks 4-12 are minor fix-now items (documentation/note corrections and two cheap
datasheet-conformance fixes). Ranks 13-14 are generator-infrastructure housekeeping. Ranks 15-16 are
accept-with-rationale. Ranks 17-21 are info/no-action, already covered by other PM decisions or
correctly deferred to R12/layout. Two findings (ids 34, 38 in the raw packet) were refuted — see §4.

All 14 fix-now items were dispatched to their owning sheet. **The chair independently re-verified every
one of the 14 against the delivered files** (not just the fixers' or the checker's self-reports) —
methodology and evidence below the table.

| Rank | Title | Sev | Disposition | Owner | Fixer-reported | Checker-verified | **Chair-reverified** |
|---|---|---|---|---|---|---|---|
| 1 | BQ25886 CSYS ≥44 µF effective at 8.4 V (R5) | major | fix-now | battery_protection_replica | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 2 | R6 not applied as literally worded creates a new armed-state hazard; source R600 from FC +3V3 instead | major | fix-now | pyro_inhibit | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 3 | R7: 14 device-side I2C pull-ups 10 k→4.7 k (E9) | major | fix-now | solar_emulation | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 4 | emulator_mcu notes stale after R7; phantom-power mechanism factually wrong | minor | fix-now | emulator_mcu | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 5 | Bench-mode jumper table omits "JP500 open" for Modes 2/3 | minor | fix-now | battery_protection_replica | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 6 | JP600 removal silently uninhibits heater channel | minor | fix-now | pyro_inhibit | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 7 | No power-up recipe; RBF bridge energises VBUSP; SW600 mislabeled in report | minor | fix-now | pyro_inhibit | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 8 | BQ25886 OTG left floating; datasheet says pull low | minor | fix-now | battery_protection_replica | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 9 | CBAT/CPMID single 10 µF below derated minimum | minor | fix-now | battery_protection_replica | ✅ fixed (1210 not 0805, documented deviation) | ✅ verified | ✅ **confirmed** |
| 10 | No FC-face↔firmware-face↔TCA9548↔MCP23017 crosswalk doc | minor | fix-now | emulator_mcu | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 11 | No warning at J701 about leaving FC powered with emulator unplugged | minor | fix-now | bench_io | ✅ fixed | ✅ verified | ✅ **confirmed** |
| 12 | `power_monitor_test` needs CH-A live, undocumented | minor | fix-now | solar_power_injection | ✅ fixed (doc-only) | ✅ verified | ✅ **confirmed** |
| 13 | Generators depend on session-scoped scratchpad pantry | minor | fix-now | root/integrator | ⚠️ partially done by the first fixer (data half only); **completed by the integrator** (path wiring) | ✅ verified | ✅ **confirmed** — see below |
| 14 | 5/6 generators re-roll every uuid; would orphan PCB footprints once layout starts | minor | fix-now | root/integrator | ❌ deferred by the first fixer (concurrency); **completed by the integrator** | ✅ verified | ✅ **confirmed** — see below |
| 15 | DRV2605L C303 100 nF vs datasheet Table 32's 1 µF | minor | accept-with-rationale | solar_emulation | — | — | reviewed, rationale sound |
| 16 | Face-0 dummy load 43 Ω vs firmware's 13 Ω default | minor | accept-with-rationale | solar_emulation | — | — | reviewed, rationale sound |
| 17 | R505 100 k bleed resistor — battery_pack_v2 fidelity deviation | info | no-action | battery_protection_replica | — | — | reviewed, awaiting PM ruling on strict fidelity |
| 18 | No per-channel EN-to-GND header for mixed real/emulated boards | info | no-action | solar_emulation | — | — | reviewed, correctly deferred (D11 mitigation in place) |
| 19 | AP22653 ILIM margin vs Face-0 DRV2605L burst (R11 check) | info | no-action | solar_emulation | — | — | reviewed, ~5× margin confirmed, no action |
| 20 | Datasheet URL empty on 24 non-passive parts | info | fix-in-layout | root | — | — | correctly deferred with R12 |
| 21 | `.kicad_pro` cached sheets list stale | info | no-action | root | — | — | confirmed advisory-only, tools don't read it |

### 2.1 Items 13/14 — reconciling the two conflicting fixer reports

The first fixer assigned to `root` reported item 13 **partially** done (pantry files copied into
`tools/pantry/`, but the six generators' `PANTRY`/`SCRATCH_PANTRY` env-var names left unwired because
five of those files were being edited concurrently by the per-sheet fixers) and item 14 **not** done
(same concurrency reason, plus the seeding scheme needs the *final* delivered uuids, which were still
moving). A second, later "integrator" fix pass reported both items **completed**: all six
`tools/gen/*.py` now resolve the pantry via `FLATSAT_PANTRY` (default `<script-dir>/../pantry`) with no
scratch/tmp path anywhere, and the five non-`battery_protection_replica` generators now draw uuids from
a `random.Random('flatsat-<sheet>-2026-09-14')` seeded stream instead of `uuid.uuid4()`.

The chair did not take either report on faith. Independent verification, from a clean environment with
no `PANTRY`/`FLATSAT_PANTRY`/`SCRATCH_PANTRY` set and no session scratch directories present:

```
$ grep -rn "private/tmp\|scratchpad" tools/gen/*.py   →  (no matches)

$ python3 tools/gen/battery_protection_replica_gen.py --out regen/battery_protection_replica.kicad_sch
$ python3 tools/gen/solar_emulation_gen.py            --out regen/solar_emulation.kicad_sch
$ python3 tools/gen/emulator_mcu_gen.py             -o regen/emulator_mcu.kicad_sch
$ python3 tools/gen/solar_power_injection_gen.py      --out regen/solar_power_injection.kicad_sch
$ python3 tools/gen/pyro_inhibit_gen.py                          # writes pyro_inhibit.kicad_sch directly
$ python3 tools/gen/bench_io_gen.py                              # writes bench_io.kicad_sch directly
   → all six exit 0, no PANTRY/scratch env vars set

diff <uuid-stripped delivered sheet> <uuid-stripped regenerated sheet>, all six:  0 diff lines
```
(the last two were run against an isolated full copy of the project tree, not the live files, since
they write in place). Ran the whole six-generator batch **twice in a row**; `pyro_inhibit.kicad_sch`
came out byte-identical across both runs (0-line diff, including uuids) — confirming the uuid stream is
seeded, not random. Finally confirmed the re-key was safe to have done: `FlatSat_V1.kicad_pcb` carries
262 footprints and **zero** reference any refdes in the 200-799 blocks, so no PCB layout existed to
orphan.

**Chair verdict: items 13 and 14 are done, verified independently, evidence solid.** The two fixer
reports are not a discrepancy once sequenced — the first agent correctly deferred the generator edits
to avoid clobbering five files mid-edit by other agents, and a second pass finished the job after the
per-sheet fixes landed. Recorded in `integration_report.md` §10.

### 2.2 Direct netlist/schematic proof for the three PM-fix-now rulings (chair's own read of the files)

```
CHG_SYS   → C513.1, C514.1, C517.1, C518.1, TP511.1, U511.15, U511.16      (was 2 caps, now 4×22 µF/25 V/1210)
C511/C513/C514/C515/C517/C518  =  22uF 25V | Capacitor_SMD:C_1210_3225Metric | LCSC C52306   (all six)

+3V3      gains R600.2   (R600 = 4.7k, C25900)   — not 3V3_EMU
PYRO_INH_COM → D600.3, D601.3, D602.3, JP601.1, LED600.1, R600.1, R601.1, SW600.1, TP603.1  (R601 stays 4.7 k, on 3V3_EMU via LED600)

R302/R303 (Face 0)                                    = 10k   (unchanged, correct)
R312/313, R322/323, R332/333, R342/343, R352/353,
R362/363, R372/373 (14 device-side pull-ups, R7)      = 4.7k  (were 10k)
R310/311/320/321/330/331/340/341/350/351/360/370/371
  (EN/READY straps — not R7's target)                 = 10k   (unchanged, correct per TCA4311A §8.3.2)
```

Recomputed the armed-state hazard the R6 fix addresses (fix id 2): with the emulator **unpowered** and
the FC driving a channel through its 4.7 k series resistor, R600 sourced from a *dead* 3V3_EMU (the
literal R6 wording) divides down to EN≈1.8 V — below TPS4H160-Q1 VIH(min) 2.0 V, an indeterminate logic
level during an FC-only D11 test. As built (R600 from FC +3V3, which is always live whenever the FC is
powered), PYRO_INH_COM sits at +3V3 with zero bias across every BAT54W when armed, so EN≈3.3 V,
comfortably above VIH(min). Confirmed against the BQ25886/BAT54W/TPS4H160 pin data already cited by the
electrical and bench-safety lenses.

### 2.3 ERC/lint proof at the current file state (re-run by chair)

`sch_lint.py` on all six sheets with correct `--path`/`--refdes-block`: **0 errors, 0 warnings** on
every sheet (93/185, 101/191, 17/24, 77/137, 23/41, 39/66 symbol-instances/wires — matches every sheet
report and `integration_report.md` §6). Full ERC delta and netlist-diff tables are in §5 below.

---

## 3. Accept-with-rationale and ask-hardware-lead items

### 3.1 Accept-with-rationale (no action this round)

- **DRV2605L C303 = 100 nF vs datasheet Table 32's 1 µF (finding 15).** SLOS854 is internally
  inconsistent (pin table says 1 µF, §9.2.2.2 design procedure says 0.1 µF); the brief instructs
  copying XY_Face_V4's decoupling for golden-reference parity, and XY_Face_V4 uses 100 nF. **Recommended
  default: keep as-is.** Cheap to bump to 1 µF (C304 already carries that value elsewhere on the sheet)
  if the hardware lead prefers datasheet-strict over parity — flag if so.
- **Face-0 dummy load R304 = 43 Ω vs firmware `DetumbleManager` default 13 Ω (finding 16).** R304 was
  independently confirmed to match the *actual* XY_Face_V4 PCB coil trace-resistance geometry (≈41 Ω
  computed at 0.5 oz copper) better than firmware's 13 Ω default, which is unreachable with any standard
  copper weight at that trace geometry. This points to a `proves-core-reference` parameter/documentation
  gap, not a FlatSat hardware defect. **Recommended default: keep R304 at 43 Ω**, file the discrepancy
  upstream against `DetumbleManager.fpp`'s `Z_MINUS_RESISTANCE` default and the `drv2605_test` power-rise
  threshold.

### 3.2 Ask hardware lead — items needing an explicit call

- **CSYS derating source is a same-class proxy, not the fitted part's own curve.** Item 1's 44 µF
  requirement was met using the KEMET `C1210C226K3PAC` DC-bias curve (22 µF/25 V/X5R/1210) as a stand-in
  for the actually-fitted Samsung `CL32A226KAJNNNE` (same case/voltage/dielectric), because Samsung
  publishes no part-specific bias curve through any reachable tool. Result: 4×12.78 µF = 51.1 µF at
  8.4 V, 16% over the 44 µF minimum — comfortable margin even if the Samsung part derates somewhat worse
  than the KEMET proxy. **Recommended default: accept** (margin absorbs reasonable proxy error); ask the
  hardware lead to add a bench measurement of CSYS ripple/derating to the Phase-2 bring-up checklist as
  a belt-and-braces confirmation, rather than blocking Phase 1 on it.
- **C511 (CPMID) / C515 (CBAT) upsized to 22 µF/1210 instead of the fix item's suggested 22 µF/0805.**
  The fixer deviated deliberately (0805/25 V/X5R would derate to ~8.8 µF at 8.4 V bias, still short of
  the BQ25886 pin table's 10 µF "after derating"; 1210 gives 12.8/19.0 µF). This reuses the same BOM line
  as the CSYS fix (C52306), so no new part number. **Recommended default: accept** — ask the hardware
  lead only if 1210 footprint area near U511 is a board-space concern for Phase-2 layout (not evaluated
  here; PCB layout is out of this round's scope).
- **R505 100 k bleed resistor (finding 17) — still open per the sheet's own report**, an addition beyond
  a strict battery_pack_v2 copy (brief D4). Electrically inert (84 µA at 8.4 V, doesn't touch detection
  thresholds). **Recommended default: keep it** (bleeds VBAT_BENCH_N to a defined potential when JP500 is
  open, which is the safer failure mode); the hardware lead can strike it in a later ruling if strict
  pack-replica fidelity is preferred over the extra safety margin.
- **Per-channel EN-to-GND header for mixing real and emulated face boards (finding 18) — Phase-2
  candidate, not built this round.** Current mitigation is a documented "don't plug a real board while
  emulation is fitted" rule (D11). **Recommended default: leave for Phase 2** unless the hardware lead
  expects to mix real/emulated boards on the bench before a layout respin is otherwise due.
- **Firmware note surfaced during the emulator_mcu fix (not a hardware finding, flagged for relay):**
  `ReferenceDeploymentTopology.cpp` lines 178-182 pass `state.muxChannel0Device` to *every*
  `drv2605FaceNManager.configure()` call, including `drv2605Face5Manager`. If unintentional, DRV2605L
  traffic firmware believes it is sending to faces 1/2/3/5 would land on TCA9548 channel 0 instead, and
  the FlatSat emulator on EMU_F1..F4 would never see it. No FlatSat schematic implication either way —
  **ask the hardware lead to relay to the firmware/proves-core-reference owner** for Phase 3 triage.

---

## 4. Refuted findings

| id | Finding | Why refuted |
|---|---|---|
| 34 | With the inhibit engaged, HWIL cannot observe a burn/heater command (EN moves only 0→0.28 V); repurpose the free emulator SPARE0/1 lines to tap the FC pyro command nets | The plan of record explicitly excludes pyro/deploy testing from the FlatSat HWIL suite ("a separate fixture owns deploy ATP"; runs "minus burnwire"); D9's `PYRO_INHIBIT_STATE` read is a safety interlock, not an observability requirement; no heater test exists in the suite. Repurposing SPARE0/1 is a brief-contract change (§4.2/6.1/6.6) needing a PM amendment, not a fix-stage schematic defect. The proposed tap topology is also electrically wrong: a 4.7 k series tap into the existing 4.7 k E9 pull-downs yields 1.65 V, below RP2350 VIH(min) 2.0 V — an undefined-region reading, not a working observability path. Kept as an info/idea for the PM and Phase-4 test planning, not a Phase-1 defect. |
| 38 | Two emulated channels (BATT, TOP) could fall back to the RP2350's hardware I2C slave engines to mitigate PIO-engine risk, since their SDA/SCL pairs sit on hardware I2C function pins | A `DW_apb_i2c` hardware slave ACKs exactly one programmed `IC_SAR` address in hardware before software ever sees the transaction. BATT (4× TMP112, four distinct addresses) and TOP (VEML6031 + TMP112, two addresses) — the two channels the finding proposes moving — must each answer for multiple slave addresses, so no hardware-engine fallback exists for either. Recording this as a mitigation in the GPIO map would mislead Phase-3 firmware. No schematic change either way; the underlying pin-mux fact (hardware I2C function on every channel pair) is true and already correctly documented, just not as a multi-address fallback. |

---

## 5. Final ERC delta and netlist diff (chair re-run, 2026-09-14)

### 5.1 ERC — vs the **post-promotion baseline** (`tools/harness_erc.sh` default / `tools/baseline/erc_promoted.json`)

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
```

### 5.2 ERC — vs the raw **Rev2 baseline** (`--baseline tools/baseline/erc.json`, proves the Rev2 relationship)

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

Both baselines agree: **every error class is +0**. The 11 project errors (4 on `/`, 4 on
`/Power Systems/`, 2 on `/RP2350AHHHHHHHHH/`, 1 on `/Watchdog Circuit/`) are byte-for-byte the Rev2 FC
list — none on a new sheet. `pin_to_pin` +68 is entirely the declared Unspecified-pin noise class
(chair confirmed: 0 `pin_to_pin` violations project-wide lack an Unspecified-typed pin).
`single_global_label` improved (9→0 / 1→0) because `USBBOOT` is now paired by `bench_io`.

**Per-sheet, non-noise totals (chair re-run):**

| Sheet | Errors | Non-noise warnings | Warning class |
|---|---|---|---|
| Emulator MCU | 0 | 0 | — |
| Solar and Sensor Emulation | 0 | 52 | `pin_to_pin` (all Unspecified-pin, known noise) |
| Solar Power Injection | 0 | 0 | — |
| Battery Replica and Bench Power | 0 | 16 | `pin_to_pin` (all Unspecified-pin, known noise) |
| Pyro Inhibit and Jumpers | 0 | 0 | — |
| Bench IO | 0 | 0 | — |

**Zero ERC errors on any of the six new sheets. Confirmed.**

### 5.3 Netlist diff vs `tools/baseline/netlist.kicadxml` (`netlist_diff.py --ignore-unconnected`)

```
components: base 261, new 479, added 218, removed 0
nets:       base 215, new 354
added nets (125)
removed nets (8):
  - /Power Systems/B-                          - /Power Systems/INHIB_1
  - /Power Systems/INHIB_2                     - /Power Systems/IN_RBF
  - /Power Systems/Load Switches/Deploy1_EN    - /Power Systems/Load Switches/Deploy2_EN
  - /Power Systems/Load Switches/Heater_EN     - /Power Systems/VBATT_SENSE
changed nets (30) — every one is "+[...] -[]" (pins gained only)
```

The removed-net list is exactly the 8 brief §4.3 label promotions (local→global renames, membership
preserved: e.g. `B-` 7→15 pins, `INHIB_1` 2→4, `VBATT_SENSE` 10→12 — all gains, zero losses). Filtering
the 30 changed nets for any non-empty "lost" list returns nothing: **no existing FC net lost a pin.**
The +218 components over the capture-stage +216 are the two extra CSYS caps (C517/C518) added by fix 1;
power symbols are not netlist components. Spot-checked: `CHG_SYS`, `+3V3`, `PYRO_INH_COM` membership
exactly as expected (§2.2 above).

**Netlist baseline preserved. Confirmed.**

---

## 6. Phase-1 exit-criteria verdict (brief §10)

> "ERC clean on all six new sheets (no errors; warnings triaged); every connector-facing net on the FC
> board traced to its new destination; heater-channel and per-face VSOLAR scope decided (D1, D2) and
> reflected in the sheets; S-band approach recorded (D5). Then the Fable review-and-fix round, then
> layout."

| Criterion | Status |
|---|---|
| ERC clean on all six new sheets | ✅ 0 errors on all six (re-confirmed §5.2); remaining warnings triaged as known-noise or resolved by the fix round |
| Every connector-facing net traced | ✅ `connector_trace.md` — 147/147 rows checked against the reproduced netlist (integrity lens); not independently re-run this round, no regression risk since no connector was touched by the fix round |
| Heater-channel / per-face VSOLAR scope decided (D1, D2) and reflected | ✅ D1 (heater channel is not assumed non-pyro; ch3/ch4 crossed, #53) now carries an explicit on-sheet caveat (fix 6); D2 (JP400 fitted/JP401 open defaults) confirmed unchanged and correct |
| S-band approach recorded (D5) | ✅ recorded in the brief/integration report; no FlatSat schematic touches S-band (out of Phase-1 scope) |
| Fable review-and-fix round | ✅ **this round** — 14 fix-now items dispositioned, applied, and independently chair-reverified against the delivered files (§2); 2 refuted, 2 accept-with-rationale, 5 info/no-action |

**Verdict: Phase-1 exit criteria are MET.** Zero ERC errors attributable to any new sheet, netlist
baseline fully preserved, all three PM fix-now rulings (R5/R6/R7) carried out and independently verified
by the chair (not just by the fixers' or checker's self-reports), and all 14 chair-ranked fix-now items
applied to both the `.kicad_sch` and its generator with regeneration proven byte-identical (uuid-stripped)
for every one of the six sheets.

### What layout (Phase 2) must pick up

1. **Bring-up measurement**: confirm CSYS (C511/C513-C515/C517/C518, 22 µF/25 V/1210, LCSC C52306)
   actually derates in line with the KEMET proxy curve used to justify the R5 fix — the fitted Samsung
   part has no published DC-bias curve, so this is a same-class estimate, not a datasheet-verified number
   for the *exact* part (§3.2).
2. **LCSC/supply-chain pass (PM ruling R12, deferred, not a Phase-1 blocker)**: 8 LCSC numbers on the
   216+ new parts need catalogue re-verification and the remaining blanks (test points, jumpers, headers)
   need sourcing; Datasheet-URL fields on 24 non-passive parts (headers, jumpers, switches, LEDs, L200)
   are empty (finding 20).
3. **Generator uuid stability is now real but untested under a layout regeneration**: all six generators
   are confirmed uuid-stable and pantry-independent as of this review (§2.1), but this was only exercised
   pre-layout (zero footprints in `FlatSat_V1.kicad_pcb` reference any 200-799 refdes today). The first
   regeneration performed *after* footprints exist on these sheets should be diffed against the PCB's
   footprint-to-symbol-uuid links before trusting "Update PCB from Schematic."
4. **`FlatSat_V1.kicad_pro` cached `sheets` list is stale** (Rev2-era, omits the six new sheets) — cosmetic,
   regenerates on the next GUI save, but don't use it as a substitute for the actual hierarchy when
   scripting anything for layout (finding 21).
5. **Open PM-deferred item**: R505 (battery_protection_replica, 100 k bleed resistor, finding 17) is a
   documented deviation from strict battery_pack_v2 fidelity awaiting a PM/hardware-lead ruling — resolve
   before treating this sheet as final-for-layout, though it has no electrical or layout impact either way.
6. **Two firmware-side items to relay, not FlatSat hardware changes**: the `DetumbleManager` 13 Ω vs the
   FlatSat's (and the real board's) ~41-43 Ω coil-resistance default mismatch (finding 16), and the
   `drv2605Face5Manager` mux-channel wiring question in `ReferenceDeploymentTopology.cpp` (§3.2) — both
   should go to the firmware/proves-core-reference owner ahead of Phase-3/4 HWIL bring-up.
