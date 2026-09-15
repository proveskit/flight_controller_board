# FlatSat V1 Phase 2 — Supply-Chain Report (stage 1, 2026-09-14)

Aggregates the six per-sheet supply-chain passes (`supply_<key>.md`, one Sonnet owner + one verifier per sheet) that filled `LCSC Part` / `Datasheet` on the 218 new FlatSat components (refdes 200–799). Field-only pass per PM brief §4 rule 5 / §3 L9: **only** `LCSC Part`, `Datasheet`, `Description` may change; no value, footprint or net may change. Six owners' individual reports are the primary source; this document cross-checks their numbers against a fresh netlist export and independent DB queries and rolls them up.

## 1. Data provenance

| Source | Detail |
|---|---|
| Parts DB | `parts-fts5.db`, refreshed 2026-09-13 (per task brief), FTS5 trigram virtual table, columns include LCSC Part, Package, MFR.Part, Library Type, Stock, Price, Datasheet |
| Query method | Each sheet owner ran targeted `sqlite3`/python3 queries (recorded per-part in their own report's `source` field); this report re-ran a batched `WHERE "LCSC Part" IN (...)` query over all 63 distinct newly-assigned codes plus the 7 named critical ICs to confirm Library Type/Package/Stock, and spot-queried Basic-equivalent searches for every Extended pick (§4) |
| Netlist baseline | `/private/tmp/.../scratchpad/final/netlist.xml` (Phase-1 final, frozen) |
| Netlist under test | Fresh `kicad-cli sch export netlist --format kicadxml` of the live `FlatSat_V1.kicad_sch` (exported by this pass) |
| Refdes → LCSC authority for this stage | Symbol `LCSC Part` properties in each `.kicad_sch` (the board is re-synced from these afterward by the PM; `jlcpcb/project.db` was not written by any sheet agent, confirmed by file mtime checks in each verifier's report) |

## 2. Project-wide netlist proof (aggregate, this report)

`tools/netlist_diff.py` (Phase-1 final `netlist.xml` vs. the fresh export above):

```
components: base 479, new 479, added 0, removed 0
nets: base 354, new 354
added nets (0):
removed nets (0):
changed nets (0):
```

Matches every individual sheet owner's and verifier's own netlist_diff run. Zero net or component/value/footprint changes project-wide — the six sheets' edits are field-only, as required.

## 3. Refdes 200–799: LCSC Part field coverage (fresh netlist, this report)

Counted directly from the fresh kicadxml export, grouped by sheet:

| Sheet | Refs (200–799) | With LCSC | Without LCSC |
|---|---|---|---|
| Emulator MCU | 47 | 43 | 4 (TP200–203) |
| Solar and Sensor Emulation | 69 | 62 | 7 (TP300–306) |
| Solar Power Injection | 11 | 8 | 3 (TP400–402) |
| Battery Replica and Bench Power | 50 | 40 | 10 (TP500–505, TP510–512, R515) |
| Pyro Inhibit and Jumpers | 20 | 15 | 5 (SW600, TP600–603) |
| Bench IO | 21 | 20 | 1 (TP701) |
| **Total** | **218** | **188** | **30** |

**188 / 218 (86.2%) of the new refdes now carry an LCSC Part field.** Of the 30 without: 28 are test points (policy, §6), and 2 are genuinely unresolved parts (R515, SW600 — §5).

Of the 188 with LCSC, 63 distinct LCSC codes are used; batched DB lookup on all 63 codes: **67 component instances resolve to an Extended-library part, 121 to a Basic-library part** (0 unresolved/not-found in the DB).

## 4. Summary counts (of the 63 originally-blank parts named in the task brief)

| | Count | |
|---|---|---|
| **Filled this pass** | **33** | new `LCSC Part` assigned (11 distinct LCSC codes, since many refs share a part) |
| **Re-verified (already had LCSC)** | **155** | pre-existing LCSC re-checked against the DB by the sheet's verifier — 0 mismatches beyond 2 documented naming aliases (§7) |
| **Left blank — test points (policy)** | **28** | TP200–203, TP300–306, TP400–402, TP500–505/510–512, TP600–603, TP701 — matches FC convention, not part of this count's "still needs a number" total |
| **Still blank — unresolved** | **2** | R515 (battery_protection_replica), SW600 (pyro_inhibit) — see §5 |

33 + 2 + 28 = 63. ✓

### 4.1 Newly filled parts (33 refs / 11 distinct LCSC codes)

| Ref(s) | Value | LCSC | MPN | Lib | Stock | Sheet |
|---|---|---|---|---|---|---|
| R304 | 43R 2010 | C7467404 | FRC2010F43R0TS | Ext | 9,737 | Solar Emulation |
| J300 | Coil Out header | C492401 | PZ254V-11-02P | Ext | 1,222,203 | Solar Emulation |
| J400, J401 | Terminal_2P_5.08mm | C8409 | WJ2EDGKA-5.08-02P-14-00A | Ext | 9,409 | Solar Power Injection |
| JP400, JP401 | Jumper_2_Open 2.54mm | C492401 | PZ254V-11-02P | Ext | 1,222,203 | Solar Power Injection |
| C512 | 47nF 0603 | C1622 | CL10B473KB8NNNC | Basic | 1,010,662 | Battery Replica |
| C516 | 4.7uF 0603 | C19666 | CL10A475KO8NNNC | Basic | 3,663,291 | Battery Replica |
| J500 | 5.08mm 3P terminal (BENCH PSU) | C72334 | WJ500V-5.08-03P-14-00A | Ext | 226,856 | Battery Replica |
| JP500, JP510 | Jumper_2_Open 2.54mm | C358684 | MTP125-1102S1 | Ext | 237,277 | Battery Replica |
| R503, R504 | 1.0k 1% 0805 | C17513 | 0805W8F1001T5E | Basic | 30,684,161 | Battery Replica |
| R514 | 750 0603 | C23241 | 0603WAF7500T5E | Ext | 603,086 | Battery Replica |
| R516 | 5.23k 0603 | C23068 | 0603WAF5231T5E | Ext | 51,539 | Battery Replica *(see §8 open item — not the true top-stock candidate)* |
| R517 | 30.1k 0603 | C23000 | 0603WAF3012T5E | Ext | 74,544 | Battery Replica *(see §8 open item — not the true top-stock candidate)* |
| U511 | BQ25886RGE | C2765094 | BQ25886RGER | Ext | 6,948 | Battery Replica |
| D600, D601, D602 | BAT54W | C77328 | BAT54W (Jiangsu Changjing) | Ext | 7,403 | Pyro Inhibit |
| JP600–607 (×8) | Conn_01x02 2.54mm | C124375 | B-2100S02P-A110 | Ext | 159,910 | Pyro Inhibit |
| C701 | 10uF 0805 | C2182156 | EMK212BB7106KG-T | Ext | 82,290 | Bench IO |
| J703 | Bench Header 2x5 2.54mm | C492422 | PZ254V-12-10P | Ext | 108,087 | Bench IO |
| Q701, Q702, Q703 | BSS138 | C78284 | BSS138 | Ext | 212,211 | Bench IO |

## 5. Parts still without a number, and why

| Ref | Value | Sheet | Reason |
|---|---|---|---|
| **R515** | 5.7k (ICHGSET, BQ25886 charge-current setpoint) | Battery Replica | Non-standard resistance — not on the E24 or E96 grid. Zero SMD catalogue rows exist for 5.7k at any package/tolerance. Substituting the nearest E96 value (5.62k or 5.76k) would silently change the replica's charge-current setpoint, which this field-only supply-chain pass is not authorized to do (that's a value change, forbidden by hard rule 5). **Flagged for PM/hardware-lead decision** — either accept a nearby E96 value (schematic edit, next stage) or source 5.7k off-catalogue. |
| **SW600** | SW_SPST (slide switch) | Pyro Inhibit | No catalogue part matches the schematic's footprint for this slide switch. Checked the switch's own reference MFR.Part family (`1MS1T1B1M2QES` / C22422208) — 0 stock. Left blank, unchanged from Phase 1. |

## 6. Test-point policy applied

Per hard rules: test points get no LCSC, and are only marked exclude-from-BOM/position if the FC's own TP symbols are. The FC root sheet (`FlatSat_V1.kicad_sch`) carries TP2, TP6, TP8, and `eps_side.kicad_sch` carries TP5 — all four checked directly: **`in_bom` yes, `on_board` yes, `in_pos_files` yes, `dnp` no, no `LCSC Part` property at all.** They are *not* excluded from BOM or position files.

All 28 new test points (TP200–203, TP300–306, TP400–402, TP500–505/510–512, TP600–603, TP701) were verified by their sheet owner and independently re-checked by that sheet's verifier to match this exactly — same four flags, no LCSC property, unchanged from the Phase-1 baseline. No test point was touched in this pass.

## 7. Reverified pre-existing LCSC numbers (155 refs)

Every sheet re-ran its own pre-existing `LCSC Part` values against the current DB (Package vs. footprint, MFR.Part vs. Value, Library Type, Stock). Zero real mismatches found. Two DB *naming* aliases were investigated and confirmed benign (not defects):

- **D200 (emulator_mcu)** — DB `Package` reads `SOD-323` for LCSC C48192, schematic footprint is `D_SOD-323F`. The `F` suffix is a flat-variant footprint naming convention already used elsewhere on the FC (D4 parity), not a real package mismatch.
- **U202 (emulator_mcu)** — DB `Package` reads `SOT-25-5` for LCSC C51118 (AP2112K-3.3). Cross-checked against C22365427, an equivalent AP2112K-3.3 part from a different manufacturer explicitly listed as `SOT-23-5` in the same DB — confirms `SOT-25-5` is a DB-side naming alias for the same physical SOT-23-5 footprint.
- **U303 (solar_emulation)** — DB `Package` reads `VSSOP-10-0.5mm` for DRV2605LDGSR (C527464), schematic footprint is `TSSOP-10_3x3mm_P0.5mm`. Documented as a pre-existing Phase-1 footprint substitution in the generator (library-availability workaround), not a new defect; left untouched per the field-only mandate this stage.

Datasheet URLs were added across the six sheets: emulator_mcu 3, solar_emulation 1, solar_power_injection 4, battery_protection_replica 3, pyro_inhibit 8, bench_io 5 — **24 total**, matching brief L9's "Datasheet URLs filled on the 24 non-passive parts."

## 8. Open item carried forward (not resolved by this pass)

**battery_protection_replica verdict = FAIL (unresolved).** The sheet's own verifier found that R516 and R517's stated selection rationale ("top-stock Extended part") does not match what their printed SQL actually produces: the query as documented sorts `Stock` as TEXT (the same bug the owner had already caught and fixed for J500/JP500/JP510 earlier in the same pass), so R516/R517 were not, in fact, the highest-stock footprint/spec match.

| Ref | Picked | Stock | True top-stock candidate (same package/value/tolerance/tempco) | Stock | Gap |
|---|---|---|---|---|---|
| R517 | C23000 (0603WAF3012T5E) | 74,544 | **C137745** (RC0603FR-0730K1L) | 425,894 | ~5.7× |
| R516 | C23068 (0603WAF5231T5E) | 51,539 | **C2930111** (FRC0603F5231TS) | 54,790 | ~6% |

Neither pick is wrong electrically (right value/package/tolerance), so no netlist or footprint risk — the LCSC is real, in stock, and correctly specified. This is a documentation/selection-rationale defect, not a build-stopper. **Recommendation:** the integrator/PM should either (a) re-point R517 (and optionally R516) to the true top-stock rows and regenerate, with a fresh `netlist_diff` proof, or (b) accept the current picks and correct the report's stated rationale (both are in-stock, in-spec parts). Not blocking for board re-sync since both current LCSC values are valid, in-stock, footprint-correct picks — just not the *maximum*-stock ones as claimed.

## 9. Risk register

### 9.1 Named critical/single-source ICs (task-specified)

| IC | Ref(s) | LCSC | Lib | Stock | Note |
|---|---|---|---|---|---|
| **RP2350A** | U200 (emulator_mcu) | C42411118 | Extended | 9,546 | Identical LCSC line to the FC's own U18 RP2350A (per the Rev2 board's own supply-chain review, same stock figure 9,546 on the same refresh date) — **the emulator now draws against the same scarce Extended SKU the flight board itself needs.** Buy early / together, per brief note "scarce, buy early." |
| **BQ25886** | U511 (battery_protection_replica) | C2765094 | Extended | 6,948 | BQ25886RGER, VQFN-24. Single SKU at JLC for this exact charger variant; no Basic alternative exists for any BQ2588x part. |
| **R5460N** | U500 (battery_protection_replica, "= battery_pack_v2 U1" per schematic text note) | C259714 | Extended | 2,860 | Pre-existing (not touched this pass); 2-cell Li-ion protection IC, SOT-23-6. |
| **TCA4311A** | U300, U310–U316 (×8 per board, solar_emulation) | C130025 | Extended | 2,691 | 8 instances per board — at this consumption rate, 2,691 units covers ~336 boards, ample for FlatSat bench-unit quantities, but it is an Extended, single-SKU part with no sibling in the DB checked. |
| **VEML6031** | U302 (solar_emulation) | C3678616 | Extended | **519** | Lowest stock of the seven named critical ICs. Single instance per board — fine at FlatSat quantities, but this is the thinnest margin on the sheet; watch before any multi-unit order. |
| **DRV2605L** | U303 (solar_emulation) | C527464 | Extended | 2,442 | DRV2605LDGSR. Footprint substitution note carried from Phase 1 (§7) — not a stock issue. |
| **IRF7458** | Q500, Q501 (×2 per board, battery_protection_replica) | C10879 | Extended | **57** | **Scarcest part found in this entire pass.** 2 instances per board → only ~28 boards' worth at current stock. Already flagged by the sheet owner as a supply risk in Phase 1; unchanged by this stage (pre-existing LCSC, only re-verified). **Highest-priority lifetime-buy candidate** if more than a couple of FlatSat units are ever built. |

### 9.2 Other Extended, low/thin-stock parts surfaced by this pass

- **J500** (C72334, WJ500V-5.08-03P-14-00A, 226,856 in stock) and **JP500/JP510** (C358684, MTP125-1102S1, 237,277) — both were re-picked mid-pass after the sheet's verifier caught a TEXT-vs-numeric stock-sort bug in the original query; both current picks are confirmed genuine top-stock matches.
- **R514** (C23241, 750R 0603, 603,086) — ample.
- **U202** AP2112K-3.3 (C51118, emulator_mcu) — Extended; stock not separately re-quoted here, no flag raised by the sheet owner.
- Every 2.54 mm pin header used across all six sheets (J300, JP400/401, JP500/510, J703, JP600–607) resolves to the **same LCSC, C492401/C492401 or its close sibling C358684/C492422** — i.e. FlatSat's header consumption is concentrated on 2–3 SKUs. All have stock in the hundreds of thousands; no near-term risk, but a large enough single order across many boards should still be checked against these specific SKUs rather than assumed infinite.

## 10. Alternates checked — no Basic equivalent exists

For every Extended pick in §4.1, this report independently re-queried the DB for a Basic-library part in the same package/spec class. **None exists** for any of the following (0 rows returned each time):

- 2010-package 43R resistors (any tolerance/power) — R304
- 2.54 mm pin headers, THT, any pin count — J300, JP400/401, JP500/510, J703, JP600–607 (0 Basic rows exist in the "Pin Headers" second-category at all)
- 5.08 mm pluggable screw terminals, 2- or 3-position — J400/401, J500
- BSS138 in any package — Q701–703
- 0603 750R / 5.23k / 30.1k 1% precision resistors — R514/R516/R517
- BAT54W in any package — D600–602

**One partial alternate exists**: C701 (10uF/0805/X7R, Extended C2182156) — the DB's only Basic 0805 10uF parts are **X5R dielectric**, not X7R (C15850 @25V, 7.04M stock; C440198 @50V, 1.53M stock). If X5R's greater temperature/voltage coefficient sensitivity is acceptable for this bench-only decoupling location, either Basic part is a drop-in-stock alternate; the sheet owner kept X7R to match the schematic's original intent and left this as Extended.

## 11. Files

Report written to: `docs/flatsat/2026-09-14_phase2_layout/supply_chain_report.md`

Per-sheet reports (primary source for all figures above):
- `docs/flatsat/2026-09-14_phase2_layout/supply_emulator_mcu.md`
- `docs/flatsat/2026-09-14_phase2_layout/supply_solar_emulation.md`
- `docs/flatsat/2026-09-14_phase2_layout/supply_solar_power_injection.md`
- `docs/flatsat/2026-09-14_phase2_layout/supply_battery_protection_replica.md`
- `docs/flatsat/2026-09-14_phase2_layout/supply_pyro_inhibit.md`
- `docs/flatsat/2026-09-14_phase2_layout/supply_bench_io.md`
