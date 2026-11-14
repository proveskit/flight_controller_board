# Schematic ERC

Schematic ERC runs KiCad's electrical rules check over the root sheet and every child sheet (on `FC_V5e_Production_Rev1`, four instantiated sheets: `RP2350AHHHHHHHHH` from `RP2350.kicad_sch`, `Power Systems` from `eps_side.kicad_sch`, `Load Switches` under it from `load_switches.kicad_sch`, and `Watchdog Circuit` from `watchdog.kicad_sch`; `rtc_backup.kicad_sch` and `untitled.kicad_sch` sit in the folder but are not placed, so ERC never sees them) and reports findings by severity and type, either absolute or as a delta against a baseline revision.

## Sub-features

- `erc-absolute` counts errors and warnings on one revision.
- `erc-delta` compares one revision with a baseline and counts only new errors.
- `erc-list` lists each finding with its sheet, description, and position.

## How to get to it (user POV)

- In the KiCad GUI, Schematic Editor, Inspect, Electrical Rules Checker.
- Headless: `kicad-cli sch erc <board>.kicad_sch`.

## Driving it with kv.py

Preconditions:

- `$K doctor FC_V5e_Production_Rev1` ends in `READY`.
- `HEAD=$($K stage FC_V5e_Production_Rev1)` and `BASE=$($K stage FC_V5e_Production_Rev1 --rev main)` both printed a run path.

- **Absolute check.** Run `$K erc "$HEAD"`. The last line reads `VERDICT erc FC_V5e_Production_Rev1@worktree: N errors, M warnings (library noise filtered)`, and `$HEAD/erc.json` exists.
- **Delta check.** Run `$K erc "$HEAD" --baseline "$BASE"`. Run `$K erc "$BASE"` first so the baseline has `erc.json`. The table shows `base`, `now`, and `delta` per type, and the verdict reads `0 new errors, 0 new warnings` for a change that adds no ERC findings.
- **Inspect findings.** Run `$K erc "$HEAD" --list`. Each `- [error] <type> <sheet path> <description> | <item> @(x,y)` line locates one finding in schematic millimetres.
- **Proof.** Quote the verdict line and attach `$HEAD/erc.txt`.

## Gotchas

- `kicad-cli sch erc` exits 0 with errors present. `FC_V5e_Production_Rev1` at `2a7c1ec` exits 0 with 12 errors and 118 warnings. Only the verdict and `erc.json` say anything.
- `--baseline` reads the baseline's own `erc.json` and does not run ERC on it. Without it, `kv.py` fails with `baseline <run> has no erc.json`.
- Heritage findings are on `main`. `FC_V5e_Production_Rev1` carries 5 `pin_not_connected`, 6 `power_pin_not_driven` and 1 `pin_to_pin` error at both `8a00c6a` and `2a7c1ec`. Judge the delta.
- The four library metadata types are most of the raw report: 331 of 461 findings on `FC_V5e_Production_Rev1`. They are filtered as noise. Read `erc.json` directly if a change is about library links.
