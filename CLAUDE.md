# PROVES Kit Flight Controller Board

KiCad 10 hardware repo. One directory per board revision (`FC_V5e_Production_Rev2` is current). Fab and assembly at JLCPCB via the Bouni `kicad-jlcpcb-tools` plugin. Heritage: `FC_V5d_Production` flew; `FC_V5e_Production_Rev1` passed bench and environmental test. Treat heritage as evidence, do not churn validated layout.

## Tooling

- `kicad-cli`: `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`. Use it for ERC, DRC, netlist, BOM, position, gerbers, renders. Pre-generate these into the scratchpad before handing work to subagents.
- Bundled Python with `pcbnew`: `/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3` (zone refill, board queries).
- JLCPCB Tools plugin data: `~/Documents/KiCad/10.0/3rdparty/plugins/com_github_bouni_kicad-jlcpcb-tools/jlcpcb/`. `parts-fts5.db` is the full catalog (refresh via the plugin's chunked download), `corrections.db` is the rotation table. Plugin setting `selected_library` picks `current-parts` vs `parts`. Not installed on the Mac mini as of 2026-11-08; release 2026.04.03 has been run headless from a clone with the bundled Python (its `Store` and `Fabrication` classes).
- Per-project `jlcpcb/project.db` (sqlite, table `part_info`) is the authoritative refdes → LCSC mapping the plugin exports from. Schematic `LCSC Part` fields are not what gets ordered.
- Custom DRC rules live in `<project>.kicad_dru`. Fine-pitch pad-to-pad exemptions use `memberOfFootprint('REF')`; `A.Footprint` is not a valid expression property and silently matches nothing.

## Hard rules learned the hard way

1. **Close Eeschema and Pcbnew before scripted edits** to `.kicad_sch` or `.kicad_pcb`. Lock files (`~*.lck`) in the project dir mean the GUI is open. Update PCB from Schematic uses the in-memory schematic, and a GUI save overwrites disk edits.
2. **Never write `value` into `jlcpcb/project.db`.** The plugin's `update_from_board` clears `lcsc` on any row whose value or footprint differs from the board. Only edit the `lcsc` column, and only after the board matches. If rows get cleared, restore `lcsc` from git and set values to match the board. A footprint field named LCSC or JLC also overrides `project.db` on open (setting `lcsc_priority`, default on), so keep every board LCSC field equal to the `project.db` row.
3. **Schematic text notes are requirements.** Grep `(text "` on the sheet before changing any part. Example: `watchdog.kicad_sch` says D7 must be 1N4151WS.
4. **Force-add BOM and CPL.** `*.csv` is ignored repo-wide. The as-ordered `jlcpcb/production_files/BOM-*.csv` and `CPL-*.csv` must be committed with the gerber zip.
5. **Check rotations in the JLC placement viewer on the first order of any footprint**, then record the fix in the project's own corrections table, not by hand in the CPL. Rev2's `jlcpcb/project.db` has a `correction` table: the global set (matthewlai `cpl_rotations_db.csv` plus the rows below) and one `^REF$` row per part fixed on an order. JLCPCB Tools release 2026.04.03 uses that table instead of the global `corrections.db` whenever it exists, and matches the reference before value and footprint. Leave "Use global corrections" unticked in the plugin's corrections dialog, because ticking it drops the table. Known footprint rows: `^Hirose_DF11-` +180, `^CONN-SMD_4P-P2.00_DF11CZ` +180, `^L_pol_2016` +180, `^USB_C_Receptacle_HRO_TYPE-C-31-M-12*` 0 (plugin default of +180 is wrong for bottom-side placement). Per-part rows for the November 2026 reorder: `docs/reviews/2026-11-02_V5e_Rev2_reorder/placement_rotations.md`.
6. **Order settings for this board:** stackup JLC04161H-7628 (RF traces tuned to 0.2104 mm prepreg), 4-wire Kelvin test, no cleaning (not solvent), no JLC conformal coat. Product description: Development Board, HS code 847330. Confirm Parts Placement on, auto-confirm off. BT1 (C964818) middle pad gets paste: JLC asks, answer yes. Decide per order whether to buy the stencil option "add openings for unpopulated pads" ($4.97 in November 2026). As-ordered facts per order: `docs/reviews/<date>_*/as_ordered.md`.
7. **JP6 must be bridged and J4 shunt removed on flight units.** Open JP6 disables the watchdog's power-cycle path to the 3V3 regulator. Needs an assembly note and an ATP line.

## Pre-order review procedure

Run before generating production files for any revision.

1. Export artifacts with `kicad-cli`: netlist (kicadxml), ERC json (`--severity-all`), DRC json (`--severity-all --all-track-errors`), grouped BOM csv, position csv.
2. Run the review workflow: `Workflow({name: "pcb-flight-review", args: {...}})`. Script in `.claude/workflows/pcb-flight-review.js`. Args: project paths, scratch dir with the artifacts, heritage directories, and a context paragraph stating what changed since the validated baseline and that zero findings is acceptable. Pipeline: 6 reviewers (schematic correctness, power datasheet parity, digital/RF datasheet parity, layout correctness, layout datasheet parity, spaceflight practice) → verifiers batched by subsystem, max 6 findings each, prompted to refute → two Fable personas (principal PCB engineer, principal QA) → chair merge. Expect ~2M tokens and ~50 min.
3. Fix only `fix-this-rev` items. Everything else goes to the next revision unless the user says otherwise.
4. Supply-chain pass: one agent refreshes `parts-fts5.db`, checks every LCSC in `project.db` for stock, Basic/Extended, MPN-vs-schematic mismatch, and lines with no assignment. Verify live against `cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail` for critical ICs.
5. Fan out P0/P1 fixes with one agent per writable file (`project.db`, schematics) and read-only research agents for trade studies. Report trade-study recommendations back before applying.
6. In the KiCad GUI: F8 Update PCB from Schematic, save, open JLCPCB Tools, confirm the LCSC column is intact, Generate. Commit gerbers, BOM, CPL. Rev2 caution: the Rev2 schematic and PCB are out of sync (TP9-TP13 exist only in the schematic, U10's footprint and the R26/R27 BOM flags differ). F8 on Rev2 adds copper. Run `kicad-cli pcb drc --schematic-parity` and edit both files instead.
7. Buy scarce Extended parts first (RTC, high-side switches, radio modules). Extended stock at JLC can reach zero between review and order.

Review history and retros: `docs/reviews/`.
