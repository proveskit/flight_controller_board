# Netlist diff between revisions

Netlist diff exports the schematic netlist of two revisions of the same board and lists every part added, removed or changed (value or footprint), every net that gained or lost pins, and every net that only changed its name. It is the proof for "no connectivity change" and for "this change touches only these nets".

## Sub-features

- `netlist-export` writes `netlist.xml` for one run.
- `netdiff-parts` lists `+ part`, `- part` and `~ part` lines.
- `netdiff-nets` lists `+ net`, `- net`, `~ net` lines with the pins gained and lost.
- `netdiff-renames` lists `= net renamed` lines for nets with identical pins under a new name.

## How to get to it (user POV)

- In the KiCad GUI, Schematic Editor, File, Export, Netlist, for each revision, then a manual compare.
- Headless: `kicad-cli sch export netlist --format kicadxml` twice.

## Driving it with kv.py

Preconditions:

- `BASE=$($K stage <board> --rev <base>)` and `HEAD=$($K stage <board>)` (or `--rev <head sha>`).

- **Export both.** Run `$K netlist "$BASE"` and `$K netlist "$HEAD"`. Each prints `VERDICT netlist <board>@<rev>: N components, M nets`.
- **Diff.** Run `$K netdiff "$BASE" "$HEAD"`. The last line reads `VERDICT netdiff <board>@<base> -> <board>@<head>: P part changes, C connectivity changes, R pure renames`.
- **BOM-only claim.** A change that only swaps LCSC numbers or fields shows `0 part changes, 0 connectivity changes`. A value change shows as `~ part`.
- **Proof.** Attach `$HEAD/netdiff-vs-<base rev>.txt` and quote the verdict.

## Gotchas

- Comparing two different board folders (V5e Rev1 against Rev2) works, but reference designators and auto-named nets (`Net-(U3-Pad4)`) can change between folders. Auto-named nets then appear as renames or as `-`/`+` pairs.
- The schematic netlist does not see the layout. `8a00c6a` to `2a7c1ec` on `FC_V5e_Production_Rev1` reads `0 part changes, 0 connectivity changes` while DRC and fab show the copper moved. Use DRC and fab for that.
- Only value and footprint are compared. Fields such as `LCSC Part` (on 21 of the board's symbols) and the part mappings in `jlcpcb/project.db` are not. `netdiff` does not see LCSC changes.
- A real schematic change reads as expected. `05d8f59` to `8a00c6a` ("Added Picolocks for Inhibits") gives `+ part J15`, `+ part J30`, `~ part J8` and `J29` (DF11 to Pico-Lock), and six `~ net` lines.
