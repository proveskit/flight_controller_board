# FlatSat V1 production files (2026-10-22)

Owner request 2026-10-22 16:14 PT: sync `jlcpcb/project.db` and generate the production files. Board on branch `claude/project-thread-ywww1h` from `200985f`. KiCad 10.0.6. No order was placed, carted, uploaded or quoted.

## Verdict

| Question | Answer |
|---|---|
| Files generated | Yes, by the JLCPCB Tools plugin's own `Store` and `Fabrication` code, run headless. Release **2026.04.03**, the current PCM release. |
| `project.db` synced | Yes. 258 rows became 481. 223 rows added, 0 changed, 0 removed. |
| Wrong parts found and fixed first | 8 refs. Board-only `LCSC` fields shadowed the schematic's `LCSC Part`, so the plugin would have ordered the wrong parts. See "Defect fixed before generation". |
| Gates | Same as the 10-21 closeout. heritage_refill 0, attachment 0/7/37, DRC errors 14, unconnected 1, parity 11, via-in-pad 0/0, track_width 95, ERC errors 12. |
| Stock blockers (live, 23:27 UTC) | **U6 TPS4H160 C485918: stock 1** (need 2 for qty 2, 5 for qty 5). **IC3 RV-3028 C3304278: stock 0** (owner consigns). Everything else covers qty 5. |
| BOM | 115 unique LCSC codes, 436 placements with a code, 36 lines with no code (472 BOM refs). |
| CPL | 474 rows: 335 top, 139 bottom. All 256 heritage refs match the Rev2 as-ordered CPL rotation, package and side. |

## Which plugin code ran

| Item | Value |
|---|---|
| Plugin | Bouni `kicad-jlcpcb-tools` release `2026.04.03` (tag tarball, 2026-04-23). This is what PCM installs today. |
| Not used | `main` at `14bf352` (2026-10-14, unreleased). It no longer reads `project.db` `part_info`. It reads assignments from board fields and migrates `project.db` into the board inside the GUI. Its output for this board would differ, so it can't stand in for the GUI's Generate. |
| Call sequence | `Library(parent)` (corrections), `Store(parent, project_path, board)` (runs `update_from_board`), `Fabrication.get_part_consistency_warnings`, `fill_zones`, `generate_geber(None)` ("Auto" layers), `generate_excellon`, `zip_gerber_excellon`, `generate_cpl`, `generate_bom`, `Store.increment_generation_count`. This is `MainWindow.generate_fabrication_data` minus its dialogs. |
| Stubs | One plain `parent` object carrying `settings`, `project_path`, `library`, `store`. Settings are the release's shipped `settings.json` (`lcsc_priority` false, `lcsc_bom_cpl` true, `fill_zones` true). Only `library.data_path` points at a scratch dir. The package was imported without its `__init__` so nothing registers with pcbnew. |
| Skipped GUI steps | Forced DRC dialog (the gates ran the same DRC). The order-number placeholder dialog: the board has no `JLCJLCJLCJLC` text, so the GUI would ask "Continue?". The stock column refresh, which needs the parts catalog and does not affect output. |
| Corrections | Fresh `corrections.db`: the plugin's 59-row seed (Matthew Lai `cpl_rotations_db.csv`) plus 5 user rows entered the way the Corrections dialog saves them. See "Rotations". |
| Side effects | `project.db` `metadata.generation_count` 8 to 9, as the GUI does. The board file was not written by the plugin (`fill_zones` refills in memory). |

## Defect fixed before generation

35 Phase-1/2 footprints carried two LCSC fields: a board-only `LCSC` (cloned from a heritage footprint) and the schematic's `LCSC Part`. The plugin's `get_lcsc_value` takes the first `lcsc|jlc` field, which was the stale one. 27 agreed. 8 did not:

| Ref | Value | Stale board `LCSC` (would have been ordered) | Schematic `LCSC Part` (now ordered) |
|---|---|---|---|
| C221, C222 | 15pF | C1525 (100 nF 0402) | C1548 |
| C301 | 10nF | C1525 | C15195 |
| C304 | 1uF | C1525 | C52923 |
| D201, D202, D510, LED600 | LED | C12624 (KT-0603G) | C2290 (KT-0603W) |

Fix: the board-only `LCSC` field was removed from those 35 footprints. No schematic sheet has an `LCSC` field on these refs, so Update PCB from Schematic will not bring it back. After the fix, every one of the 218 Phase-1/2 refs resolves to its schematic `LCSC Part` (scripted check, 0 mismatches). The 10-21 BOM report read `LCSC Part` directly, so it did not see this.

## Schematic and board field edits

| Change | Refs | Files |
|---|---|---|
| PLM-08: `LCSC Part` to C492401, `Datasheet` to the PZ254V-11-02P PDF | JP500, JP510 (were C358684); JP600 to JP607 (were C124375). J300, JP400, JP401 already C492401. | `battery_protection_replica.kicad_sch`, `pyro_inhibit.kicad_sch`, `FlatSat_V1.kicad_pcb` |
| U1: `LCSC` C181596 (TLV1704AIPWR TSSOP-14) | U1, all 5 units. Board `LCSC` was C33503485 (TLV1824DR **SOIC-14**). | `watchdog.kicad_sch` (field added), `FlatSat_V1.kicad_pcb` |
| Stale board-only `LCSC` removed | 35 Phase-1/2 refs above | `FlatSat_V1.kicad_pcb` |

Fields only. No geometry changed. Zone refill afterwards was byte-identical.

The 13 headers are one mechanical part. All 13 use `PinHeader_1x02_P2.54mm_Vertical`. Live JLC data for all three SKUs: 1x2P, 2.54 mm pitch, 3 mm tail, 6 to 6.1 mm mating pin, 3 A, brass. Insulator height is 2.5 mm vs 2.54 mm. J4 (heritage, no LCSC, hand-solder) is the same footprint and was left alone.

U1 sheet notes (rule 3). "Do Not Consolidate the BOM on this Circuit" holds: U1 keeps its own line. "Use TLV1704AQPWRQ1 for non-flight C3 boards" is not met. The symbol MPN says TLV1704AQPWRQ1, but `project.db` already ordered C181596 TLV1704AIPWR before this change, and Rev2 did too. Ordering is unchanged. Owner call: keep AIPWR for the bench board, or find a JLC code for AQPWRQ1.

## project.db sync

| Measure | Count |
|---|--:|
| Rows before / after | 258 / 481 |
| Added | 223 |
| Added with an LCSC from the board field | 190 |
| Added with no LCSC (28 test pads TP2xx to TP7xx, FID1, FID2, H10 to H12) | 33 |
| Added and excluded from BOM and POS by board attribute | 5 (FID1, FID2, H10, H11, H12) |
| Changed | 0 |
| Removed | 0 |
| Heritage rows whose `lcsc` differs from the board field, `project.db` kept (`lcsc_priority` false) | R42 C227953 (board C185323), U1 C181596 (board now matches) |
| Value or footprint mismatches (rule 2) | 0 |

Every board ref has a row. 485 footprints are 481 unique refs, because the 5 `G***` logos share one row. Exclusion flags are the board attributes, as the plugin derives them. No test pad, DNF resistor or hand-solder part is flagged excluded on the board.

Rows added (from `Store.update_from_board`):

| LCSC | Footprint | Rows | Refs | Flags |
|---|---|--:|---|---|
| C1525 | C_0402_1005Metric | 24 | C201 C203 C204 C205 C206 C207 C208 C209 C210 C211 C212 C218 C219 C220 C300 C302 C303 C310 C311 C312 C313 C314 C315 C316 |  |
| C1548 | C_0402_1005Metric | 2 | C221 C222 |  |
| C1622 | C_0603_1608Metric | 1 | C512 |  |
| C2290 | LED_0603_1608Metric | 4 | D201 D202 D510 LED600 |  |
| C8409 | TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal | 2 | J400 J401 |  |
| C10879 | SOIC-8_3.9x4.9mm_P1.27mm | 2 | Q500 Q501 |  |
| C11702 | R_0402_1005Metric | 7 | R201 R204 R206 R211 R705 R707 R709 |  |
| C14663 | C_0603_1608Metric | 4 | C500 C501 C502 C503 |  |
| C15195 | C_0402_1005Metric | 1 | C301 |  |
| C15849 | C_0603_1608Metric | 1 | C200 |  |
| C15850 | C_0805_2012Metric | 1 | C214 |  |
| C17168 | R_0402_1005Metric | 1 | R203 |  |
| C17513 | R_0805_2012Metric | 2 | R503 R504 |  |
| C19666 | C_0603_1608Metric | 1 | C516 |  |
| C19702 | C_0603_1608Metric | 1 | C202 |  |
| C21190 | R_0603_1608Metric | 2 | R502 R519 |  |
| C22935 | R_0603_1608Metric | 2 | R512 R513 |  |
| C23000 | R_0603_1608Metric | 1 | R517 |  |
| C23068 | R_0603_1608Metric | 1 | R516 |  |
| C23138 | R_0603_1608Metric | 2 | R500 R501 |  |
| C23188 | R_0603_1608Metric | 1 | R515 |  |
| C23241 | R_0603_1608Metric | 1 | R514 |  |
| C23733 | C_0402_1005Metric_small_pads | 4 | C213 C215 C216 C217 |  |
| C25092 | R_0402_1005Metric | 2 | R703 R704 |  |
| C25105 | R_0402_1005Metric | 1 | R200 |  |
| C25117 | R_0402_1005Metric | 1 | R602 |  |
| C25744 | R_0402_1005Metric | 19 | R202 R205 R300 R301 R302 R303 R310 R311 R320 R321 R330 R331 R340 R341 R350 R351 R360 R370 R371 |  |
| C25803 | R_0603_1608Metric | 1 | R505 |  |
| C25804 | R_0603_1608Metric | 1 | R518 |  |
| C25900 | R_0402_1005Metric | 29 | R207 R208 R209 R210 R312 R313 R314 R322 R323 R324 R332 R333 R334 R342 R343 R344 R352 R353 R354 R362 R363 R372 R373 R374 R600 R601 R706 R708 R710 |  |
| C25905 | R_0402_1005Metric | 4 | R510 R511 R701 R702 |  |
| C28323 | C_0805_2012Metric | 1 | C510 |  |
| C28927 | SOT-563 | 1 | U301 |  |
| C48192 | D_SOD-323F | 1 | D200 |  |
| C51118 | SOT-23-5 | 1 | U202 |  |
| C52306 | C_1210_3225Metric | 6 | C511 C513 C514 C515 C517 C518 |  |
| C52923 | C_0402_1005Metric | 1 | C304 |  |
| C72334 | TerminalBlock_Phoenix_MKDS-1,5-3-5.08_1x03_P5.08mm_Horizontal | 1 | J500 |  |
| C72443 | BTN_KMR2_4.6X2.8 | 2 | SW701 SW702 |  |
| C77328 | SOT-323_SC-70 | 3 | D600 D601 D602 |  |
| C78284 | SOT-23 | 3 | Q701 Q702 Q703 |  |
| C87572 | IND-SMD_L7.1-W6.5-P5.60 | 1 | L510 |  |
| C97521 | SOIC-8_5.3x5.3mm_P1.27mm | 1 | U201 |  |
| C130025 | MSOP-8_L3.0-W3.0-P0.65-LS5.0-BL | 8 | U300 U310 U311 U312 U313 U314 U315 U316 |  |
| C160389 | JST_SH_BM03B-SRSS-TB_1x03-1MP_P1.00mm_Vertical | 1 | J702 |  |
| C165948 | USB_C_Receptacle_HRO_TYPE-C-31-M-12 | 2 | J510 J701 |  |
| C207086 | Fuse_2920_7451Metric | 2 | F400 F401 |  |
| C259714 | SOT-23-6 | 1 | U500 |  |
| C431540 | SW_SPDT_Shouhan_MSK12C02 | 1 | SW600 |  |
| C442635 | U-DFN2020-6E_L2.0-W2.0-P0.65-BL | 1 | Q510 |  |
| C492401 | PinHeader_1x02_P2.54mm_Vertical | 13 | J300 JP400 JP401 JP500 JP510 JP600 JP601 JP602 JP603 JP604 JP605 JP606 JP607 |  |
| C492422 | PinHeader_2x05_P2.54mm_Vertical | 1 | J703 |  |
| C527464 | TSSOP-10_3x3mm_P0.5mm | 1 | U303 |  |
| C2182156 | C_0805_2012Metric | 1 | C701 |  |
| C2765094 | Texas_RGE0024H_VQFN-24-1EP_4x4mm_P0.5mm_EP2.7x2.7mm | 1 | U511 |  |
| C2886093 | D_SMA | 2 | D400 D401 |  |
| C2887259 | SW-TH_SHOU-HAN_SS12D10G4 | 1 | SW703 |  |
| C3235552 | SOT-363_L2.0-W1.3-P0.65-LS2.1-BR | 1 | U510 |  |
| C3678616 | SENSOR-SMD_VEML6031X00 | 1 | U302 |  |
| C7467404 | R_2010_5025Metric | 1 | R304 |  |
| C20625731 | Crystal_SMD_3225-4Pin_3.2x2.5mm | 1 | Y200 |  |
| C42411118 | RP2350-QFN-60-1EP_7x7_P0.4mm_EP3.4x3.4mm_ThermalVias | 1 | U200 |  |
| C42411119 | L_pol_2016 | 1 | L200 |  |
| (none) | Fiducial_1mm_Mask2mm | 2 | FID1 FID2 | BOM+POS excluded (board attribute) |
| (none) | MountingHole_3.2mm_M3_DIN965_Pad | 3 | H10 H11 H12 | BOM+POS excluded (board attribute) |
| (none) | TestPoint_Pad_D1.5mm | 28 | TP200 TP201 TP202 TP203 TP300 TP301 TP302 TP303 TP304 TP305 TP306 TP400 TP401 TP402 TP500 TP501 TP502 TP503 TP504 TP505 TP510 TP511 TP512 TP600 TP601 TP602 TP603 TP701 |  |

## BOM and CPL checks

| Check | 10-21 BOM report | Generated | Delta and why |
|---|--:|--:|---|
| Unique LCSC codes | 117 | 115 | -2: C358684 and C124375 collapsed into C492401 (PLM-08) |
| Placements with an LCSC | 436 | 436 | 0. The 8 corrected refs swap codes, they don't add placements. |
| BOM refs (lines with and without a code) | 472 | 472 | 0 |
| BOM lines | 182 (Value+Footprint+LCSC) | 167 (131 with a code, 36 without) | The plugin groups by Value+LCSC, not footprint |
| BOM lines with no LCSC | 36 refs | 36 | 28 test pads, TP2/TP5/TP6/TP8, J3, J4, JP6, R9 (DNF). JLC lists them as unmatched. Leave them unselected. |
| CPL rows | | 474 | 472 + H1, H2. Heritage `project.db` excludes them from the BOM but not from POS, the same as Rev2. JLC ignores CPL rows with no BOM line. |
| CPL sides | top 333 / bottom 139 | top 335 / bottom 139 | +2 top: H1, H2 |
| CPL refs == BOM refs | | 472 shared, CPL-only H1, H2, BOM-only none | |
| Duplicate refs | | 0 in BOM, 0 in CPL | |
| Heritage CPL vs Rev2 as-ordered CPL | | 256 of 256 identical (package, side, rotation) | The corrections set reproduces Rev2's |
| Plugin consistency warnings | | 7 codes with >1 value text | All benign: same part, different net labels (DF11 headers, Pico-Lock, USB-C, SWD, RP2350A, C492401 headers, C177235). C1525 no longer appears. |

## Files

| File | Bytes | Notes |
|---|--:|---|
| `FlatSat_V1/jlcpcb/production_files/GERBER-FlatSat_V1.zip` | 3,262,382 | 15 entries, 12,555,295 bytes unzipped |
| `FlatSat_V1/jlcpcb/production_files/BOM-FlatSat_V1.csv` | 9,774 | git-ignored (`*.csv`). Force-add (rule 4). |
| `FlatSat_V1/jlcpcb/production_files/CPL-FlatSat_V1.csv` | 27,786 | git-ignored (`*.csv`). Force-add (rule 4). |
| `FlatSat_V1/jlcpcb/gerber/` (15 files) | 12,555,295 | The plugin's plot dir. Same content as the zip. Rev2 committed its equivalent. |

Zip contents. Each file is non-empty and carries its X2 file function:

| File | Bytes | X2 function | Draw/flash ops |
|---|--:|---|--:|
| FlatSat_V1-CuTop.gbr | 1,380,844 | Copper,L1,Top | 50,234 |
| FlatSat_V1-CuIn1.gbr | 1,323,001 | Copper,L2,Inr | 51,282 |
| FlatSat_V1-CuIn2.gbr | 1,062,639 | Copper,L3,Inr | 40,923 |
| FlatSat_V1-CuBottom.gbr | 1,588,013 | Copper,L4,Bot | 59,991 |
| FlatSat_V1-SilkTop.gbr | 1,412,630 | Legend,Top | 53,749 |
| FlatSat_V1-SilkBottom.gbr | 5,204,743 | Legend,Bot | 204,921 |
| FlatSat_V1-MaskTop.gbr | 376,339 | Soldermask,Top | 13,811 |
| FlatSat_V1-MaskBottom.gbr | 26,535 | Soldermask,Bot | 629 |
| FlatSat_V1-PasteTop.gbr | 46,963 | Paste,Top | 1,012 |
| FlatSat_V1-PasteBottom.gbr | 21,033 | Paste,Bot | 486 |
| FlatSat_V1-EdgeCuts.gbr | 2,781 | Profile,NP | 78 |
| FlatSat_V1-PTH.drl | 21,786 | Plated,1,4,PTH | 1,240 holes, 13 tools |
| FlatSat_V1-NPTH.drl | 521 | NonPlated,1,4,NPTH | 8 holes, 2 tools |
| FlatSat_V1-PTH-drl_map.pdf | 72,357 | drill map | |
| FlatSat_V1-NPTH-drl_map.pdf | 15,110 | drill map | |

The plugin writes no `.gbrjob` (`SetCreateGerberJobFile(False)`), so there is no job file to read. The four copper layers are L1 to L4 in the X2 headers above, and both drill files span layers 1 to 4. The release writes Excellon in inches (`SetFormat(False)`). JLC accepts it. Plugin `main` has since switched to metric.

## Rotations

| Ref | Package | Side | Board angle | Correction matched | CPL rotation |
|---|---|---|--:|---|--:|
| C513 | C_1210_3225Metric | top | -90 | none | -90 |
| L510 | IND-SMD_L7.1-W6.5-P5.60 | top | 90 | none | 90 |
| C512 | C_0603_1608Metric | top | 90 | none | 90 |
| TP512 | TestPoint_Pad_D1.5mm | top | 0 | none | 0 (no part) |
| C215 | C_0402_1005Metric_small_pads | top | 180 | none | 180 |
| C218 | C_0402_1005Metric | top | 0 | none | 0 |
| J510 | USB_C_Receptacle_HRO_TYPE-C-31-M-12 | top | 0 | `^USB_C_Receptacle_HRO_TYPE-C-31-M-12*` = 0 | 0 |
| U511 | Texas_RGE0024H_VQFN-24-1EP_4x4mm | top | 0 | none | 0 |
| U510 | SOT-363_L2.0-W1.3-P0.65-LS2.1-BR | top | 0 | `^SOT-363_L2.0-W1.3-P0.65-LS2.1-BR` = 0 (PLM-04) | 0 |
| L3 | L_pol_2016 | top | -45 | `^L_pol_2016` = 180 | 135 |
| L200 | L_pol_2016 | top | 0 | `^L_pol_2016` = 180 | 180 |
| J12 | USB_C_Receptacle_HRO_TYPE-C-31-M-12 | bottom | -90 | `^USB_C_...-M-12*` = 0 | 270 (= Rev2) |
| J701 | USB_C_Receptacle_HRO_TYPE-C-31-M-12 | top | 180 | `^USB_C_...-M-12*` = 0 | 180 |
| D400, D401 | D_SMA | top | 180, 0 | none | 180, 0 |
| D600 to D602 | SOT-323_SC-70 | top | 0 | none | 0 |

User correction rows (CLAUDE.md rule 5 and PLM-04), in the plugin's global `corrections.db`:

| Regex | Rotation | Seed had |
|---|--:|---|
| `^Hirose_DF11-` | 180 | absent |
| `^CONN-SMD_4P-P2.00_DF11CZ` | 180 | absent |
| `^L_pol_2016` | 180 | absent |
| `^USB_C_Receptacle_HRO_TYPE-C-31-M-12*` | 0 | 180 (updated) |
| `^SOT-363_L2.0-W1.3-P0.65-LS2.1-BR` | 0 | `^SOT-363` = 180 would have matched |

The plugin tries anchored patterns first, so the full SOT-363 name beats `^SOT-363`. 33 refs got a correction. The PLM-05 first-use parts U511, D400/D401 and D600 to D602 got none. Check them in JLC's viewer first. The easyeda heritage packages (U5 SOIC-8_L4.9, U6 HTSSOP-28_L9.7, U25 HTSSOP-16_L5.0) take the generic +270 and match Rev2 exactly.

## Stock (live JLC API, 2026-10-22 23:27 UTC)

Need = max(qty per board x boards + attrition, MOQ). 115 codes, 2 short. Full table in the appendix.


Shortfalls:

| LCSC | Part | Need (2 / 5) | Stock | Options |
|---|---|--:|--:|---|
| C485918 | U6 TPS4H160AQPWPRQ1 (heritage pyro/heater driver) | 2 / 5 | **1** (16 on 10-21) | Consign from a distributor, or JLC global sourcing / pre-order. Buy before ordering (procedure step 7). |
| C3304278 | IC3 RV-3028-C7 | 2 / 5 | **0** | Owner pre-ordered. Consign to JLC. The plugin has no consign flag, so IC3 stays in the BOM with its code. Mark it consigned in the JLC BOM page. |

Watched parts:

| LCSC | Part | Need (2 / 5) | Stock |
|---|---|--:|--:|
| C42411119 | L3, L200 AOTA-B201610S3R3-101-T | 5 / 11 | 229 (407 earlier on 10-22) |
| C10879 | Q500, Q501 IRF7458 | 4 / 10 | 24 |
| C485918 | U6 TPS4H160 | 2 / 5 | **1** |
| C42411118 | U18, U200 RP2350A | 4 / 10 | 5,926 |
| C2765094 | U511 BQ25886 | 2 / 5 | 5,372 |
| C3678616 | U302 VEML6031 | 2 / 5 | 221 |

## What the owner still does

| # | Step |
|---|---|
| 1 | Review and commit: the 4 design files, `project.db`, the zip, and force-add the BOM and CPL csv (rule 4). |
| 2 | Secure U6 (C485918, stock 1) and consign IC3 before ordering. |
| 3 | Upload `GERBER-FlatSat_V1.zip`. Stackup JLC04161H-7628, 4 layers, 1.6 mm, 4-wire Kelvin test, no conformal coat (rule 6). |
| 4 | Choose the finish. HASL-LF or ENIG. ENIG suits the 0.4 mm RP2350 QFN and the LGA sensors. |
| 5 | Order number: the board has no `JLCJLCJLCJLC` placeholder. Pick "remove order number" or a location on the JLC page. |
| 6 | PCBA Standard, double-sided. Upload the BOM and CPL. Leave the 36 no-LCSC lines unselected. Mark IC3 consigned. Solvent cleaning (rule 6). |
| 7 | In JLC's placement viewer, confirm U510, J510, J701, L3, L200, U511, D400/D401, D600 to D602 and the DF11 connectors. Record any fix in the plugin `corrections.db` (rule 5). |
| 8 | If you regenerate in the GUI: install release 2026.04.03 (not `main`) and add the 5 correction rows above. A fresh install seeds `^USB_C_Receptacle_HRO_TYPE-C-31-M-12*` = 180 and `^SOT-363` = 180, which are wrong for this board. |
| 9 | Assembly notes: JP6 bridged and J4 shunt removed on flight units (rule 7); bench shunt states per the jumper tables on the sheets. |

## Reproduce

Scripts are in the session scratch dir (`prod/`), not committed: `edit_fields.py` (field edits, idempotent), `run_plugin.py` (drives the release plugin), `analyze.py` (sync diff, BOM/CPL checks). The plugin source was the `2026.04.03` tag tarball from GitHub.

## Appendix: stock per code (live 2026-10-22 23:27 UTC)

Watched parts in bold.

| LCSC | MPN | Refs | Qty/bd | Lib | Stock | MOQ | Attrition | Need (2) | Need (5) | Short (2) | Short (5) |
|---|---|---|--:|---|--:|--:|--:|--:|--:|--:|--:|
| **C3304278** | RV-3028-C7-32.768KHZ-1PPM-TA-QA | IC3 | 1 | Ext | 0 | 1 | 0 | 2 | 5 | **2** | **5** |
| **C485918** | TPS4H160AQPWPRQ1 | U6 | 1 | Ext | 1 | 1 | 0 | 2 | 5 | **1** | **4** |
| **C10879** | IRF7458TRPBF | Q500 Q501 | 2 | Ext | 24 | 1 | 0 | 4 | 10 | 0 | 0 |
| C597838 | DF11CZ-4DP-2V(27) | J23 | 1 | Ext | 87 | 1 | 0 | 2 | 5 | 0 | 0 |
| C580306 | LT8610ABEMSE#TRPBF | U12 | 1 | Ext | 118 | 1 | 0 | 2 | 5 | 0 | 0 |
| C1857514 | TPS2HB50AQPWPRQ1 | U25 | 1 | Ext | 125 | 1 | 0 | 2 | 5 | 0 | 0 |
| **C3678616** | VEML6031X00 | U302 | 1 | Ext | 221 | 1 | 0 | 2 | 5 | 0 | 0 |
| **C42411119** | AOTA-B201610S3R3-101-T | L200 L3 | 2 | Ext | 229 | 5 | 1 | 5 | 11 | 0 | 0 |
| C411292 | E22-400M30S | U13 | 1 | Ext | 229 | 1 | 0 | 2 | 5 | 0 | 0 |
| C23050 | 0603WAF4123T5E | R74 | 1 | Ext | 254 | 20 | 10 | 20 | 20 | 0 | 0 |
| C87572 | SPM6530T-1R0M120 | L510 | 1 | Ext | 292 | 5 | 0 | 5 | 5 | 0 | 0 |
| C411312 | E28-2G4M27S | U30 | 1 | Ext | 467 | 1 | 0 | 2 | 5 | 0 | 0 |
| C7467404 | FRC2010F43R0TS | R304 | 1 | Ext | 516 | 5 | 2 | 5 | 7 | 0 | 0 |
| C181596 | TLV1704AIPWR | U1 | 1 | Ext | 568 | 1 | 0 | 2 | 5 | 0 | 0 |
| C2886093 | CDBA240LL-HF | D400 D401 | 2 | Ext | 578 | 5 | 0 | 5 | 10 | 0 | 0 |
| C555460 | TPS54225PWPR | U10 | 1 | Ext | 590 | 1 | 0 | 2 | 5 | 0 | 0 |
| C18214056 | APS1604M-3SQR-SN | U5 | 1 | Ext | 701 | 1 | 0 | 2 | 5 | 0 | 0 |
| C506665 | DF11-4DP-2DSA(08) | J10 J19 J20 J7 | 4 | Ext | 914 | 2 | 1 | 9 | 21 | 0 | 0 |
| C404816 | SPM6530T-3R3M-HZ | L4 | 1 | Ext | 982 | 2 | 0 | 2 | 5 | 0 | 0 |
| C8409 | WJ2EDGKA-5.08-02P-14-00A | J400 J401 | 2 | Ext | 1,013 | 2 | 0 | 4 | 10 | 0 | 0 |
| C2655100 | LSM6DSOTR | U7 | 1 | Ext | 1,408 | 1 | 0 | 2 | 5 | 0 | 0 |
| C360729 | SPM6530T-4R7M-HZ | L5 | 1 | Ext | 1,414 | 5 | 0 | 5 | 5 | 0 | 0 |
| C110493 | DFLS130L-7 | D12 D13 D15 | 3 | Ext | 1,561 | 5 | 2 | 8 | 17 | 0 | 0 |
| C130025 | TCA4311ADGKR | U300 U310 U311 U312 U313 U314 U315 U316 | 8 | Ext | 2,251 | 1 | 0 | 16 | 40 | 0 | 0 |
| C177235 | 5040500491 | J21 J24 | 2 | Ext | 2,285 | 5 | 0 | 5 | 10 | 0 | 0 |
| C964818 | MY-1220-03 | BT1 | 1 | Ext | 2,289 | 2 | 1 | 3 | 6 | 0 | 0 |
| C2875853 | ZDSD02GLGEAG | U2 | 1 | Ext | 2,538 | 1 | 0 | 2 | 5 | 0 | 0 |
| C530664 | KH-MMCX-Z | RF1 | 1 | Ext | 2,576 | 2 | 0 | 2 | 5 | 0 | 0 |
| C671115 | LT3652IMSE#TRPBF | IC6 | 1 | Ext | 2,811 | 1 | 0 | 2 | 5 | 0 | 0 |
| C259714 | R5460N208AA-TR-FE | U500 | 1 | Ext | 2,830 | 5 | 0 | 5 | 5 | 0 | 0 |
| C28927 | TMP112AIDRLR | U301 | 1 | Ext | 3,109 | 5 | 0 | 5 | 5 | 0 | 0 |
| C563981 | 5040500691 | J1 J11 J13 J2 J6 J9 | 6 | Ext | 3,364 | 1 | 0 | 12 | 30 | 0 | 0 |
| C87469 | INA219AIDCNR | U16 U8 | 2 | Ext | 3,479 | 2 | 0 | 4 | 10 | 0 | 0 |
| C112288 | SPM6530T-100M | L1 | 1 | Ext | 3,655 | 5 | 1 | 5 | 6 | 0 | 0 |
| C77328 | BAT54W | D600 D601 D602 | 3 | Ext | 3,731 | 5 | 4 | 10 | 19 | 0 | 0 |
| C81248 | 25121WF120LT4E | R75 | 1 | Ext | 3,839 | 5 | 4 | 6 | 9 | 0 | 0 |
| C558584 | MCP23017T-E/SS | U9 | 1 | Ext | 4,130 | 1 | 0 | 2 | 5 | 0 | 0 |
| C919695 | LIS2MDLTR | U15 | 1 | Ext | 4,186 | 1 | 0 | 2 | 5 | 0 | 0 |
| C20625731 | ABM8-272-T3 | Y1 Y200 | 2 | Ext | 4,218 | 5 | 0 | 5 | 10 | 0 | 0 |
| C72443 | KMR221GLFS | SW1 SW2 SW701 SW702 | 4 | Ext | 4,278 | 5 | 0 | 8 | 20 | 0 | 0 |
| C442635 | DMP4047LFDE-7 | Q510 | 1 | Ext | 4,288 | 5 | 0 | 5 | 5 | 0 | 0 |
| **C2765094** | BQ25886RGER | U511 | 1 | Ext | 5,372 | 1 | 0 | 2 | 5 | 0 | 0 |
| C17429783 | 1N4151WS-E3-18 | D7 | 1 | Ext | 5,430 | 5 | 0 | 5 | 5 | 0 | 0 |
| C3235552 | DZDH0401DW-7 | U510 | 1 | Ext | 5,728 | 1 | 0 | 2 | 5 | 0 | 0 |
| **C42411118** | RP2350A | U18 U200 | 2 | Ext | 5,926 | 1 | 0 | 4 | 10 | 0 | 0 |
| C1511768 | AP22653AW6-7 | U19 U21 U22 U23 U24 U27 U29 | 7 | Ext | 6,901 | 5 | 0 | 14 | 35 | 0 | 0 |
| C506658 | DF11-12DP-2DSA(08) | J14 J16 J18 | 3 | Ext | 7,919 | 2 | 0 | 6 | 15 | 0 | 0 |
| C84494 | GRM32ER71A476KE15L | C8 | 1 | Ext | 7,964 | 5 | 0 | 5 | 5 | 0 | 0 |
| C92124 | PMR18EZPFV2L00 | R108 R109 | 2 | Ext | 8,322 | 5 | 0 | 5 | 10 | 0 | 0 |
| C861602 | RT0603BRD0794K2L | R69 | 1 | Ext | 8,892 | 20 | 8 | 20 | 20 | 0 | 0 |
| C527464 | DRV2605LDGSR | U303 | 1 | Ext | 10,031 | 1 | 0 | 2 | 5 | 0 | 0 |
| C18335 | 0603WAJ0475T5E | R35 | 1 | Ext | 10,184 | 20 | 10 | 20 | 20 | 0 | 0 |
| C51118 | AP2112K-3.3TRG1 | U202 | 1 | Ext | 14,630 | 5 | 0 | 5 | 5 | 0 | 0 |
| C207086 | 2920L185DR | F400 F401 | 2 | Ext | 15,350 | 2 | 0 | 4 | 10 | 0 | 0 |
| C5119943 | 5040500291 | J15 J29 J30 J8 | 4 | Ext | 15,980 | 1 | 0 | 8 | 20 | 0 | 0 |
| C48192 | NSR0320MW2T1G | D200 D4 | 2 | Ext | 20,194 | 5 | 5 | 9 | 15 | 0 | 0 |
| C2999499 | FRC0603F6343TS | R71 | 1 | Ext | 21,073 | 20 | 10 | 20 | 20 | 0 | 0 |
| C23188 | 0603WAF5621T5E | R515 | 1 | Ext | 23,057 | 20 | 10 | 20 | 20 | 0 | 0 |
| C130026 | TCA9548APWR | U3 | 1 | Ext | 26,282 | 1 | 0 | 2 | 5 | 0 | 0 |
| C2887259 | SS12D10G4 071 | SW703 | 1 | Ext | 27,289 | 2 | 0 | 2 | 5 | 0 | 0 |
| C160389 | BM03B-SRSS-TB(LF)(SN) | J22 J702 | 2 | Ext | 27,711 | 5 | 0 | 5 | 10 | 0 | 0 |
| C160390 | BM04B-SRSS-TB(LF)(SN) | J5 | 1 | Ext | 28,476 | 5 | 1 | 5 | 6 | 0 | 0 |
| C227953 | AC0603FR-0752K3L | R42 | 1 | Ext | 33,488 | 20 | 10 | 20 | 20 | 0 | 0 |
| C2182156 | EMK212BB7106KG-T | C701 | 1 | Ext | 35,686 | 5 | 4 | 6 | 9 | 0 | 0 |
| C90143 | EMK325ABJ107MM-P | C11 C19 C25 | 3 | Ext | 37,958 | 5 | 0 | 6 | 15 | 0 | 0 |
| C97521 | W25Q128JVSIQ | U11 U201 | 2 | Basic | 55,412 | 1 | 0 | 4 | 10 | 0 | 0 |
| C861248 | RT0603BRD07243KL | R23 | 1 | Ext | 61,032 | 20 | 8 | 20 | 20 | 0 | 0 |
| C23068 | 0603WAF5231T5E | R516 | 1 | Ext | 71,480 | 20 | 10 | 20 | 20 | 0 | 0 |
| C23000 | 0603WAF3012T5E | R517 | 1 | Ext | 80,990 | 20 | 10 | 20 | 20 | 0 | 0 |
| C78284 | BSS138 | Q701 Q702 Q703 | 3 | Ext | 92,267 | 10 | 5 | 11 | 20 | 0 | 0 |
| C492422 | PZ254V-12-10P | J703 | 1 | Ext | 108,723 | 2 | 0 | 2 | 5 | 0 | 0 |
| C14890 | 0603WAF7322T5E | R38 | 1 | Ext | 109,035 | 20 | 10 | 20 | 20 | 0 | 0 |
| C72334 | WJ500V-5.08-03P-14-00A | J500 | 1 | Ext | 175,826 | 2 | 0 | 2 | 5 | 0 | 0 |
| C431540 | MSK12C02 | SW600 | 1 | Ext | 195,228 | 2 | 6 | 8 | 11 | 0 | 0 |
| C52306 | CL32A226KAJNNNE | C511 C513 C514 C515 C517 C518 | 6 | Ext | 227,991 | 5 | 2 | 14 | 32 | 0 | 0 |
| C137768 | RC0603FR-0722K1L | R40 | 1 | Ext | 258,200 | 20 | 10 | 20 | 20 | 0 | 0 |
| C165948 | TYPE-C-31-M-12 | J12 J510 J701 | 3 | Ext | 332,581 | 2 | 0 | 6 | 15 | 0 | 0 |
| C23241 | 0603WAF7500T5E | R514 | 1 | Ext | 369,971 | 20 | 10 | 20 | 20 | 0 | 0 |
| C1613 | CL10B332KB8NNNC | C36 | 1 | Basic | 370,489 | 20 | 10 | 20 | 20 | 0 | 0 |
| C12624 | KT-0603G | D6 | 1 | Ext | 464,448 | 20 | 16 | 20 | 21 | 0 | 0 |
| C492401 | PZ254V-11-02P | J300 JP400 JP401 JP500 JP510 JP600 JP... | 13 | Ext | 1,006,446 | 2 | 0 | 26 | 65 | 0 | 0 |
| C1622 | CL10B473KB8NNNC | C512 | 1 | Basic | 1,012,126 | 20 | 10 | 20 | 20 | 0 | 0 |
| C1548 | 0402CG150J500NT | C221 C222 C63 C64 | 4 | Basic | 1,048,843 | 20 | 10 | 20 | 30 | 0 | 0 |
| C25117 | 0402WGF4700TCE | R602 | 1 | Basic | 1,146,300 | 20 | 10 | 20 | 20 | 0 | 0 |
| C16772 | CL05B224KO5NNNC | C31 C54 C56 C57 C58 | 5 | Basic | 1,379,652 | 20 | 18 | 28 | 43 | 0 | 0 |
| C2290 | KT-0603W | D1 D2 D201 D202 D3 D510 LED600 | 7 | Basic | 1,684,687 | 20 | 10 | 24 | 45 | 0 | 0 |
| C32949 | CL05C100JB5NNNC | C12 | 1 | Basic | 1,725,813 | 20 | 10 | 20 | 20 | 0 | 0 |
| C28323 | CL21B105KBFNNNE | C510 | 1 | Basic | 2,077,929 | 20 | 10 | 20 | 20 | 0 | 0 |
| C25105 | 0402WGF330JTCE | R200 R94 | 2 | Basic | 2,287,417 | 20 | 10 | 20 | 20 | 0 | 0 |
| C25819 | 0603WAF4702T5E | R46 R47 R48 R49 R50 R51 R86 | 7 | Basic | 2,450,598 | 20 | 10 | 24 | 45 | 0 | 0 |
| C23733 | CL05A475MP5NRNC | C213 C215 C216 C217 C65 C66 C68 C69 | 8 | Basic | 2,758,325 | 20 | 10 | 26 | 50 | 0 | 0 |
| C19666 | CL10A475KO8NNNC | C516 | 1 | Basic | 3,152,303 | 20 | 10 | 20 | 20 | 0 | 0 |
| C25092 | 0402WGF220JTCE | R7 R703 R704 R8 | 4 | Basic | 3,458,618 | 20 | 10 | 20 | 30 | 0 | 0 |
| C23138 | 0603WAF3300T5E | R500 R501 | 2 | Basic | 3,877,982 | 20 | 10 | 20 | 20 | 0 | 0 |
| C22809 | 0603WAF1502T5E | R54 R55 R82 R85 | 4 | Basic | 3,893,054 | 20 | 10 | 20 | 30 | 0 | 0 |
| C25905 | 0402WGF5101TCE | R510 R511 R701 R702 | 4 | Basic | 4,410,526 | 20 | 10 | 20 | 30 | 0 | 0 |
| C22935 | 0603WAF1004T5E | R512 R513 R63 | 3 | Basic | 5,875,528 | 20 | 10 | 20 | 25 | 0 | 0 |
| C59461 | CL10A226MQ8NRNC | C15 C16 | 2 | Basic | 6,745,048 | 20 | 10 | 20 | 20 | 0 | 0 |
| C15195 | CL05B103KB5NNNC | C301 C6 | 2 | Basic | 6,955,741 | 20 | 10 | 20 | 20 | 0 | 0 |
| C4211 | 0603WAF3001T5E | R19 R20 R21 | 3 | Basic | 7,363,315 | 20 | 10 | 20 | 25 | 0 | 0 |
| C52923 | CL05A105KA5NQNC | C304 | 1 | Basic | 7,709,874 | 20 | 10 | 20 | 20 | 0 | 0 |
| C15850 | CL21A106KAYNNNE | C214 C75 | 2 | Basic | 9,379,085 | 20 | 10 | 20 | 20 | 0 | 0 |
| C17168 | 0402WGF0000TCE | R203 R91 | 2 | Basic | 9,500,593 | 20 | 10 | 20 | 20 | 0 | 0 |
| C19702 | CL10A106KP8NNNC | C1 C14 C20 C202 C21 C22 C23 C24 C3 C4... | 12 | Basic | 13,348,110 | 20 | 10 | 34 | 70 | 0 | 0 |
| C15849 | CL10A105KB8NNNC | C200 C37 C4 C41 | 4 | Basic | 14,343,292 | 20 | 10 | 20 | 30 | 0 | 0 |
| C25900 | 0402WGF4701TCE | R100 R103 R104 R105 R106 R110 R111 R2... | 54 | Basic | 14,942,247 | 20 | 10 | 118 | 280 | 0 | 0 |
| C25744 | 0402WGF1002TCE | R2 R202 R205 R300 R301 R302 R303 R310... | 21 | Basic | 18,463,783 | 20 | 10 | 52 | 115 | 0 | 0 |
| C25803 | 0603WAF1003T5E | R101 R30 R32 R33 R34 R36 R43 R505 R65... | 21 | Basic | 18,622,333 | 20 | 10 | 52 | 115 | 0 | 0 |
| C11702 | 0402WGF1001TCE | R201 R204 R206 R211 R705 R707 R709 R93 | 8 | Basic | 20,017,409 | 20 | 10 | 26 | 50 | 0 | 0 |
| C23186 | 0603WAF5101T5E | R26 R27 | 2 | Basic | 22,443,315 | 20 | 10 | 20 | 20 | 0 | 0 |
| C21190 | 0603WAF1001T5E | R10 R102 R29 R3 R31 R4 R502 R519 R64 R81 | 10 | Basic | 36,176,416 | 20 | 10 | 30 | 60 | 0 | 0 |
| C25804 | 0603WAF1002T5E | R1 R107 R11 R124 R13 R14 R15 R16 R17 ... | 21 | Basic | 36,870,978 | 20 | 10 | 52 | 115 | 0 | 0 |
| C1525 | CL05B104KO5NNNC | C10 C18 C2 C201 C203 C204 C205 C206 C... | 60 | Basic | 36,888,077 | 20 | 10 | 130 | 310 | 0 | 0 |
| C17513 | 0805W8F1001T5E | R503 R504 | 2 | Basic | 43,374,455 | 20 | 10 | 20 | 20 | 0 | 0 |
| C14663 | CC0603KRX7R9BB104 | C500 C501 C502 C503 | 4 | Basic | 45,709,679 | 20 | 10 | 20 | 30 | 0 | 0 |
