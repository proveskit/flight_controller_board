# Fab outputs against the ordered zip

Fab outputs regenerates the gerbers and drill files with the settings the JLCPCB tools plugin uses (copper, paste, silkscreen, mask and Edge.Cuts layers, silkscreen clipped by mask, inch Excellon with routed slots) and compares every layer with the gerber zip that was ordered (`jlcpcb/production_files/GERBER-<board>.zip`). Layers are matched by Gerber file function (`Copper,L1,Top`, `Paste,Bot`) or drill type (`PTH`, `NPTH`), not file name, and compared with volatile header lines (dates, generator, `G04` comments) removed. It proves that a board folder still produces what was ordered, or shows which layers a change moved.

## Sub-features

- `fab-generate` writes gerbers and Excellon drills with PDF drill maps into `fab/`.
- `fab-compare` reports each layer as `identical`, `DIFFERS`, `missing from regenerated`, or `not in ordered zip`.
- `fab-layerset` catches a package that lacks layers, such as missing paste layers.

## How to get to it (user POV)

- In the KiCad GUI, PCB Editor, File, Fabrication Outputs, Gerbers and Drill Files; or the JLCPCB tools plugin's Generate fabrication files.
- Headless: `kicad-cli pcb export gerbers` and `kicad-cli pcb export drill`, with the flags in the `fab-gerbers.log` and `fab-drill.log` of a run.

## Driving it with kv.py

Preconditions:

- A staged run `RUN` of a board folder with `jlcpcb/production_files/GERBER-*.zip`, or a zip path for `--against`.

- **Regenerate and compare.** Run `$K fab "$RUN"`. Lines list each layer key with its state, and the verdict reads `VERDICT fab <board>@<rev> vs GERBER-<board>.zip: N layers identical, D differ or missing`.
- **As-ordered check.** On an "As Ordered" board at its order commit, copper, paste and drill layers read `identical`. `FC_V5e_Production_Rev1` reads `10 layers identical, 3 differ` (see Gotchas for the three). A `DIFFERS` line on copper, paste or drill means the committed board is not what was ordered.
- **Change check.** Compare the two revisions, not each against the zip. For a silkscreen-only change, only `Legend,*` layers differ. For a BOM-only change, nothing differs.
- **Compare with another zip.** Run `$K fab "$RUN" --against /path/to/GERBER.zip`.
- **Compare two revisions.** Run `$K fab "$BASE"`, then `$K fab "$HEAD" --against "$BASE"`. The table goes to `$HEAD/fab-vs-<base rev>.txt`. This separates a design change from a tool difference, because both sides come from the same `kicad-cli`.
- **Proof.** Attach `$RUN/fab.txt` or `$HEAD/fab-vs-<base rev>.txt` and quote the verdict.

## Gotchas

- Regenerated output is not byte-identical to the ordered zip, even at the order commit. `FC_V5e_Production_Rev1` at `2a7c1ec` gives 10 of 13 layers identical: all four copper layers, both drill files, both paste layers, bottom mask and the outline. The ordered zip was plotted by KiCad 10.0.1 and the Mac mini runs 10.0.6. Both silkscreens differ by small clipping differences (164 of 218,000 lines on the bottom). Top mask gains two 0.65 mm openings over the J12 NPTH holes. These are likely plotter changes between the two versions (inferred, not tested against 10.0.1). Treat `DIFFERS` on `Legend,*` and `Soldermask,Top` as expected for this board, and anything on copper, paste or drill as real.
- Do not use `--board-plot-params`. This board's saved plot settings have drill marks on (`drillshape 1`), which add a flash at every hole on each copper layer, so all four copper layers report `DIFFERS`. Its drill export defaulted to millimetres while the plugin writes inches.
- The comparison detects layout changes. The pre-cleanup revision `8a00c6a` against the same zip gives 4 identical and 9 different layers, copper and PTH drill included.
- Only a zip named `GERBER-<board>.zip` is the default reference. Older commits can carry another board's zip: `8a00c6a` of `FC_V5e_Production_Rev1` holds `GERBER-FC_V5d_Production_Rev3.zip`, copied from the V5d folder. Such a run reports `no GERBER-<board>.zip to compare`.
- The JLCPCB plugin is not installed on the Mac mini. BOM and CPL files are not regenerated here.
- Committed `jlcpcb/gerber/` folders hold the unzipped plugin output. They match the zip and are not a second reference.
