# Board DRC and schematic parity

Board DRC runs KiCad's design rules check on the layout with the board's own constraints from `<board>.kicad_pro`, lists every unrouted connection, and checks that the board's footprints and nets agree with the schematic.

## Sub-features

- `drc-rules` reports clearance, width, annular ring, silk and courtyard violations.
- `drc-unrouted` reports unconnected items as `unconnected_items:<type>`.
- `drc-parity` reports board-to-schematic mismatches as `schematic_parity:<type>`.
- `drc-delta` compares with a baseline revision and counts only new errors.

## How to get to it (user POV)

- In the KiCad GUI, PCB Editor, Inspect, Design Rules Checker, with "Test for parity between PCB and schematic" ticked.
- Headless: `kicad-cli pcb drc --schematic-parity <board>.kicad_pcb`.

## Driving it with kv.py

Preconditions:

- `$K doctor FC_V5e_Production_Rev1` ends in `READY`.
- `HEAD` and `BASE` runs are staged as in the ERC recipe.

- **Absolute check.** Run `$K drc "$HEAD"`. The verdict reads `VERDICT drc FC_V5e_Production_Rev1@<rev>: N errors, M warnings`, and `$HEAD/drc.json` exists.
- **Delta check.** Run `$K drc "$BASE"`, then `$K drc "$HEAD" --baseline "$BASE"`. A layout change that introduces no violations reads `0 new errors, 0 new warnings`.
- **Parity and routing.** In `drc.txt`, rows starting `schematic_parity:` and `unconnected_items:` are the parity and unrouted counts. A board ready to order has zero `unconnected_items` rows.
- **Proof.** Quote the verdict and attach `$HEAD/drc.txt`. Add `--list` to locate each finding in board millimetres.

## Gotchas

- `kicad-cli pcb drc` does not refill zones unless you pass `--refill-zones`, which `kv.py` does not. DRC checks the zone fills that were committed. To test whether fills are stale, run `kicad-cli pcb drc --refill-zones --format json --severity-all --schematic-parity -o /tmp/refill.json <board>.kicad_pcb` in `RUN/src` and compare counts. Without `--save-board` the board file is not changed (same MD5 before and after on `FC_V5e_Production_Rev1`, where both runs gave 93 findings).
- `0 new errors` can hide new warnings. `FC_V5e_Production_Rev1` from `8a00c6a` to `2a7c1ec` fixed 39 errors and added 8 `schematic_parity:footprint_symbol_mismatch` and 2 `isolated_copper` warnings. The verdict prints both counts.
- The ordered `FC_V5e_Production_Rev1` is not DRC-clean: 35 `clearance`, 12 `annular_width` and 1 `courtyards_overlap` error, plus 18 schematic parity warnings. Judge the delta.
- The board's own rules, not JLC's, drive DRC. A pass does not mean JLC capability limits are met.
