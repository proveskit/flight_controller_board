# PROVES FlatSat V1 — Phase 1 schematic capture (2026-09-14)

Six new KiCad 10 sheets folded onto a copy of `FC_V5e_Production_Rev2` (`FlatSat_V1/`, branch `flatsat-v1`), captured by a product-manager-orchestrated multi-agent workflow and closed with a Fable review-and-fix round. Plan of record: the PROVES FlatSat plan artifact (rev 4 → rev 5 after this phase).

| File | What |
|---|---|
| [00_pm_brief.md](00_pm_brief.md) | The specification (rev 2): decisions D1–D11, net contract, sheet table, per-sheet requirements, validation procedure |
| [01_brief_critique.md](01_brief_critique.md) | Fable adversarial critique of the brief before capture (21 items, all folded into rev 2) |
| [capture_args.json](capture_args.json) | Exact arguments used to run `.claude/workflows/flatsat-schematic-capture.js` |
| `sheet_<key>.md` | One report per new sheet from its implementer (parts, nets, GPIO/jumper tables, datasheet facts, tool output, deviations) |
| `integration_report.md` | Integrator: root sheet symbols, promotions, project symbol lib, full ERC triage, netlist diff vs Rev2 |
| `connector_trace.md` | Every FC connector pin → net → FlatSat destination (Phase 1 exit criterion) |
| `02_review_report.md` | Fable review-and-fix round: prioritized findings, dispositions, refuted items, final ERC/netlist state, exit-criteria verdict |

## How it was run

1. PM (interactive session) copied Rev2 to `FlatSat_V1/`, renamed the project, verified ERC/netlist identical, built the helper tools in `FlatSat_V1/tools/` (lint, scratch-copy ERC harness, netlist diff, symbol fetcher, validated symbol pantry), wrote the brief, had Fable critique it, folded the critique in, and applied the eight label promotions (brief §4.3) — verified as pure renames.
2. `Workflow({scriptPath: ".claude/workflows/flatsat-schematic-capture.js", args: capture_args.json})`: per sheet, implementer (Opus for emulator_mcu / solar_emulation / battery_protection_replica, Sonnet for the rest) → Opus skeptic verifier → fix loop (≤ 2 rounds); then one Opus integrator; then an independent Opus exit-criteria checker (≤ 2 rounds). Concurrency ≤ 6.
3. `Workflow({scriptPath: ".claude/workflows/flatsat-schematic-review.js", args: {...same paths, captureResult}})`: five Fable review lenses → dedup → refuters per sheet → chair fix list → owner-per-file Opus fixers → Opus re-check → sign-off (`02_review_report.md`). Mid-run the owner asked for the remaining stages to use Sonnet: the run was stopped after the five Fable lenses and 10 of 11 Fable verify batches, the script was made model-configurable (`args.models`, `args.verifyModelByIndex`), and it was resumed from cache with the last verify batch, the chair and the sign-off on Sonnet (`review_args.json`).

## Outcome (2026-09-14)

Capture: 36 agents, six sheets, 218 new components, ERC 0 errors on new sheets (the 11 remaining errors are byte-identical to the Rev2 FC baseline), Rev2 netlist preserved (no existing net lost a pin; the eight promotions are pure renames), connector trace complete, exit criteria met by an independent checker. Review: 28 agents, 21 items dispositioned — 14 fixed and re-verified (incl. PM rulings R5/R6/R7), 2 accepted with rationale, 2 refuted, 1 deferred to layout, zero regressions; chair sign-off: Phase-1 exit criteria met. Five items await hardware-lead sign-off (see `02_review_report.md` §3). `capture_result.json` / `review_result.json` hold the raw workflow return values. Nothing on the `flatsat-v1` branch has been committed yet.

## Reusing the workflows

Both scripts are parameterized by the args object (project paths, sheet table with uuids/pages/refdes blocks/models, brief path, scratch dir). To capture a different set of sheets, edit the brief and the `sheets` array; keep `FlatSat_V1/tools/harness_erc.sh`'s sheet table in sync with the brief's §5.

## Hard rules that applied

See brief §3. In short: Rev2 is read-only (GUI open), one agent per writable file, atomic writes, nothing in series with a flight power path, no `project.db` writes, no GUI, no commits.
