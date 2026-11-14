---
name: verify
description: Prove a change to a PROVES flight controller KiCad board (schematic, layout, or fab outputs) by driving kicad-cli headlessly on a staged copy. Runs ERC, DRC with schematic parity, schematic and 3D renders for PR screenshots, netlist diffs between revisions, and gerber regeneration against the ordered zip. Use before opening or approving any PR that touches a board folder, and to check a board is order-ready.
---

# Verify a KiCad board change

This repo has no app to launch. The user surface is a KiCad project: one board folder such as `FC_V5e_Production_Rev1/` holding `<name>.kicad_pro`, `.kicad_sch` (plus child sheets), `.kicad_pcb`, project-local libraries (`footprints.pretty`, `symbols`, `Backup_Footprints`, referenced through `${KIPRJMOD}`), and `jlcpcb/` order outputs. "Driving" a board means running `kicad-cli`, the headless half of KiCad, against it and reading the reports and images it produces. The KiCad GUI is not driven.

Every command goes through one helper, `scripts/kv.py` (Python 3 stdlib only). Run it from the repo root:

```sh
K=.claude/skills/verify/scripts/kv.py
```

## Where it runs

`kicad-cli` must be at least the major version that wrote the files, which `doctor` reads from each file's `generator_version`. Current boards (`FC_V5e*`) are KiCad 10, V5d boards are KiCad 9. KiCad 10 reads both. The Mac mini (`mac.lan`, `/Users/ossf-1/GitHut`) has KiCad 10.0.6 at `/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli` (also on `PATH` as `/opt/homebrew/bin/kicad-cli`), and `rsvg-convert` for schematic PNGs. Cloud containers have no KiCad 10 package, so a cloud agent runs this skill through a Remote Control session on the Mac mini. Set `KICAD_CLI=/path/to/kicad-cli` to use another install.

## Launch

A run is a directory that holds a staged copy of one board folder (`src/`) and the evidence produced from it. `kicad-cli` only ever reads and writes inside the run, never in the checkout.

```sh
RUN=$($K stage FC_V5e_Production_Rev1)             # working tree, uncommitted edits included
BASE=$($K stage FC_V5e_Production_Rev1 --rev main) # a committed revision, via git archive
```

`--rev` must name a commit that has the board folder. A new board folder does not exist on `main~N` before the PR that added it, and `stage` fails with the `git log` command that lists usable revisions. `stage` prints the run path, `~/kicad-verify-evidence/<board>@<rev>-<timestamp>/` (override the root with `KV_EVIDENCE_ROOT`). The run is ready when the path prints and `src/<board>.kicad_pro` exists. It skips lock files, `*.kicad_prl`, backups and caches when copying a working tree. There is no server, so there is nothing to keep alive and nothing to tear down except the staged copy.

## Doctor

Run this first, and again whenever a command fails in a way you did not expect. It is read-only.

```sh
$K doctor FC_V5e_Production_Rev1
```

It prints one line per check and ends in `READY` or `NOT READY` (exit 1): `kicad-cli` found, its version against the version the board files need, the git head and the count of uncommitted paths in the board folder, and any `~*.lck` lock file. A lock file is either committed junk (several board folders carry them) or a sign that someone has the project open in the KiCad GUI. Neither blocks a run, because runs use a staged copy. Do not edit files in a board folder someone has open in the GUI. The GUI will overwrite your edit on its next save.

## Drive

Each command takes a run, writes its raw report and a `.txt` summary into the run, keeps the exact `kicad-cli` invocation, exit code, stdout and stderr in `<step>.log`, and ends with one `VERDICT` line. Read the verdict, then the summary.

| Command | `kicad-cli` call | Evidence written to the run |
|---|---|---|
| `$K erc RUN [--baseline BASE] [--list]` | `sch erc --severity-all --format json` | `erc.json`, `erc.txt` |
| `$K drc RUN [--baseline BASE] [--list]` | `pcb drc --severity-all --all-track-errors --schematic-parity --format json` | `drc.json`, `drc.txt` |
| `$K render RUN` | `sch export pdf`, `sch export svg`, `pcb render --side top/bottom` | `render/schematic.pdf`, `render/sch/*.svg` (and `.png` through `rsvg-convert`), `render/pcb-top.png`, `render/pcb-bottom.png`, `render/missing-3d-models.txt` |
| `$K netlist RUN` | `sch export netlist --format kicadxml` | `netlist.xml` |
| `$K netdiff BASE HEAD` | none (reads both `netlist.xml`) | `HEAD/netdiff-vs-<base rev>.txt` |
| `$K fab RUN [--against ZIP or RUN]` | `pcb export gerbers --subtract-soldermask -l <copper, paste, silk, mask, Edge.Cuts>`, `pcb export drill --excellon-units in --excellon-oval-format route` | `fab/*`, `fab.txt` (against the ordered zip) or `fab-vs-<rev>.txt` (against another run) |

ERC and DRC summaries drop four library-metadata types that every board carries (`lib_symbol_issues`, `lib_symbol_mismatch`, `footprint_link_issues`, `endpoint_off_grid`). They are noise, not findings. `--baseline BASE` turns the summary into a per-type delta table, and its verdict counts new errors and new warnings separately, so a change is judged against the board it changed rather than against zero. Read the new-warning count too: schematic parity findings are warnings. Existing heritage boards are not ERC- or DRC-clean.

The feature map in [`features/README.md`](features/README.md) is the recipe for each check. Use it to pick what to run.

## Evidence

Proof for a board change is the pair of runs (base and head) plus the summaries that compare them. Report the `VERDICT` lines with the run paths.

- Exercise the real files. Stage the exact revision under test (`--rev <sha>` for a pushed commit, the working tree for local edits). Never hand-edit a staged copy to make a check pass.
- Capture before and after. A change claim ("no copper changes", "fixes the U6 footprint", "adds pull-ups on SDA") is proven by a base run and a head run with `--baseline`, `netdiff`, or `fab` output that shows exactly that delta and nothing else.
- Check side effects, not only reports. A BOM-only or silkscreen-only PR must show `0 connectivity changes` in `netdiff` and identical copper layers in `$K fab HEAD --against BASE` (run `$K fab BASE` first).
- Images for the PR come from `render/`. Project rule: every PR with a visual change carries verification screenshots. Attach `pcb-top.png`, `pcb-bottom.png`, and the changed schematic sheet.
- A `kicad-cli` exit code is not a verdict. `sch erc` and `pcb drc` exit 0 with violations present. Read the summary, and open every PNG you cite.

## Cleanup

```sh
$K cleanup "$RUN"
```

This removes the run's staged `src/` copy only. Reports, renders, gerbers and logs stay in the run directory for the PR or the thread to cite. Nothing runs in the background, so there are no processes to kill. Delete a whole run directory by hand only once its evidence is no longer cited anywhere.

## Helpers

`scripts/kv.py` is the only helper. `$K --help` and `$K <command> --help` print usage. It exits 1 with a `FAIL` line when a check cannot run (missing `kicad-cli`, board folder absent at `--rev`, no report produced, baseline not yet checked, run already cleaned up).
