# KiCad board verification map

This directory is the maintained source for verifying changes to the flight controller boards in this repo. Read the index, then use the matching feature file as the recipe. The harness is `kv.py` from [`../SKILL.md`](../SKILL.md).

## Baseline preconditions

- Work from the repo root with `K=.claude/skills/verify/scripts/kv.py`.
- Run on a machine with KiCad 10 `kicad-cli` (the Mac mini). `$K doctor <board>` must end in `READY`.
- Stage every revision you compare into its own run: `RUN=$($K stage <board>)` and `BASE=$($K stage <board> --rev <base sha or branch>)`.
- Default board for examples is `FC_V5e_Production_Rev1`, the current ordered board. Its `jlcpcb/production_files/GERBER-FC_V5e_Production_Rev1.zip` is the as-ordered fab package.
- Never run `kicad-cli` against a board folder in the checkout. The staged copy is the only target.

## Driving conventions

- One board folder per run. A board folder holds exactly one `.kicad_pro`.
- Compare against a baseline whenever the change has a parent revision. Heritage boards carry ERC and DRC findings, so an absolute count proves nothing about the change.
- Treat every command as literal. Keep flags unchanged.
- "No copper change" claims need both `netdiff` and `fab`. Connectivity can be identical while copper geometry moves.

## Proof and skip reporting

- Quote each `VERDICT` line with its run path.
- Image proof is a PNG from `render/` that you opened and checked shows the board and the changed area.
- Report a check you could not run with the `FAIL` line and the `<step>.log` path. Do not substitute a different check and call the original verified.
- Run `$K cleanup <run>` after reading results. Evidence stays in the run directory.

## Feature entry contract

Each feature file starts with an H1 title and one paragraph describing what it proves. It then uses exactly four H2 sections in this order: `Sub-features`, `How to get to it (user POV)`, `Driving it with kv.py`, and `Gotchas`.

## Features

- [Schematic ERC](./erc.md) checks electrical rules on the whole sheet hierarchy, absolute or against a baseline.
- [Board DRC and schematic parity](./drc.md) checks layout rules, unrouted nets, and board-to-schematic agreement.
- [Renders for review](./renders.md) produces schematic PDF and SVG sheets and top and bottom 3D board images for PRs.
- [Netlist diff between revisions](./netlist-diff.md) lists every part and connectivity change between two revisions.
- [Fab outputs against the ordered zip](./fab-outputs.md) regenerates gerbers and drills and compares each layer with what was ordered.
