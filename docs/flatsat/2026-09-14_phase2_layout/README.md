# PROVES FlatSat V1 — Phase 2 layout (started 2026-09-14)

Layout, DRC and the full review pipeline for the 218 new components captured in Phase 1, on a copy of the Rev2 flight-controller board whose own layout stays frozen. Plan numbering unchanged: schematic = Phase 1, layout = Phase 2, fab + firmware = Phase 3. Owner's model policy: Sonnet first; Opus for the floorplan judgement and stubborn DRC classes; Fable only in the repo's pre-order review board.

## Status 2026-10-21: routed board installed, both review passes closed, ready for the owner's order steps

`FlatSat_V1/FlatSat_V1.kicad_pcb` is the routed, reviewed board (branch `claude/project-thread-ywww1h`). Per-step gate
numbers are in [`../PROGRESS.md`](../PROGRESS.md); the closeout narrative is `layout_report.md` §11.

| Gate (KiCad 10.0.6, zones refilled) | Final |
|---|---|
| `heritage.py check --refill --core-inset 12 --ref-board` | 0 (3 band notes, same as round 3) |
| `attachment_check.py` | 0 violations, 7 F15 fill warnings, 37 stubs |
| DRC errors / unconnected / parity | 14 / 1 / 11 (2 Rev2 items + 12 U6.29 `annular_width` that 10.0.6 also reports on flown Rev2) |
| Via-in-pad (`via_in_pad.py`) | 0 in-pad, 0 edge (was 45 / 19); no filled-and-capped vias |
| `bench_power_width` (`track_width`) | 95 deferred residual runs (`residual_widths.txt`) |
| ERC errors | 12 (11 Phase-1 baseline + U7 `pin_to_pin`, also on Rev2 under 10.0.6) |


| File | What |
|---|---|
| [00_pm_brief.md](00_pm_brief.md) | The specification: board facts, decisions L1–L10 (L-shaped extension, block placement, lanes, heritage freeze, net classes, ground, routing method, silkscreen, supply chain, review), hard rules, tools, exit criteria |
| `supply_<key>.md`, `supply_chain_report.md` | Stage 1: LCSC / datasheet sourcing per sheet + the verifier-checked summary and risk register |
| `floorplan_proposal_N.json/.md`, `floorplan.json`, `floorplan.md`, `floorplan_preview.kicad_pcb`, `img/floorplan_*` | Stage 2: three Sonnet proposals, the Opus judge's scores and the synthesized floorplan (v1). Owner review 2026-09-14 → brief §12: block plan accepted, passive placement rejected |
| `blocks.json`, `detail/placement_<block>.json/.md`, `detail/audit_<block>.md`, `floorplan_v2.json`, `floorplan_v2.md`, `floorplan_v2_preview.kicad_pcb`, `img/floorplan_v2_*`, `detailed_placement_args.json` | Stage 2b: per-block detailed placement to the manufacturers' layout guidelines (Sonnet placer + independent Sonnet datasheet auditor per block, Opus integrator); second owner review gate before routing |
| `panel/` (`principal_routability.md`, `principal_manufacturability.md`, `junior_developer.md`, `verify_*.md`, `floorplan_v2_panel_review.md`, `panel_fix_plan.json`, `prior_state.json`), `panel_args.json` | Stage 2c (owner-requested, 2026-09-19): review panel of floorplan v2.2 — principal layout engineer (routability + manufacturability, Opus) and junior developer / bench user (Sonnet), every finding re-measured by a Sonnet skeptic, Opus chair report + fix plan whose `blockNotes` feed the detailed-placement workflow. Facts pre-measured by `tools/pcb/placement_facts.py` |
| `floorplan_v2_3.json`, `floorplan_v2_3.md`, `floorplan_v2_3_preview.kicad_pcb` (+ siblings), `img/floorplan_v2_3_*` | Floorplan v2.3 = v2.2 + the panel's placement fixes: J701 rotated 180° (mouth off the edge), J12 plug relief slot through the wing (owner decision F8) with a GND stitching ring, built by `tools/pcb/build_floorplan.sh` (outline → placement → A3 → heritage refilled vs Rev2 → attachment gate → DRC with parity, all with project siblings in place). The floorplan the build stage starts from. |
| `build_report.md` | Stage 3: outline, holes, ground zones, net classes, placement applied; heritage / DRC / parity outputs |
| `route_report.md` | Stage 4: Freerouting round trip with the heritage lock, width audit of the bench-power nets, USB pair |
| `drc_triage.md` | Stage 5: every DRC item fixed / pre-existing / accepted with reason |
| `layout_report.md`, `img/` | Stage 6: what was built, routing stats, silkscreen, renders, production preview list |
| `OWNER_RULINGS_2026-10-21.md` | F15 (attachment fill test -> warning), F16 (via-in-pad off-pad), F17 (free every via-in-pad, re-place allowed) |
| `via_off_pad.md`, `emulator_replace.md`, `img/emu_*`, `img/vreg_*`, `img/c500_*` | F16 dogbone pass (55 of 62 moved) and the F17 emulator rip-up/re-place that freed the last 7 |
| `review_fixes.md`, `review2_fixes.md`, `residual_widths.txt`, `review_fixes_scripts/` | Stage 7 fixes for review passes 1 and 2, with the edit scripts |
| [`../../reviews/2026-10-21_FlatSat_V1/`](../../reviews/2026-10-21_FlatSat_V1/) | Stage 7: `pcb-flight-review` passes 1 and 2 (final lists, raw agent returns) |
| `review_args_flatsat.json` | FlatSat-specific reviewer dimensions passed to `pcb-flight-review.js` |
| `layout_args.json` | Exact arguments used for `.claude/workflows/flatsat-layout.js` |

Tooling (`FlatSat_V1/tools/pcb/`, all validated by the PM on scratch copies before dispatch): `board_sync.py` (scripted Update-PCB-from-Schematic; parity proven), `heritage.py` (Rev2 snapshot/check; `--refill --core-inset 12 --ref-board` for the refilled core-fill check), `outline.py` + `outline_L1.json` (extension, planes, holes), `apply_placement.py` (real courtyard polygons for overlaps, pad copper for outline containment), `netclasses.py`, `make_keepout.py` → `fc_keepout.json` (Freerouting-side L11 fixture), `attachment_check.py` (L11 gate, `--prune` + dangling trim), `route.sh` + `route_merge.py` + `README.md` (Freerouting recipe with heritage lock, echo filter, auto-prune; §7 = the 2026-09-14 smoke-run findings), `drc_summary.py`, `render.sh`, and since 2026-10-21 `gates.sh` (every gate in one call), `via_in_pad.py`, `refill.py`, `add_fiducials.py`, `preview.sh`, `closure/dogbone.py`, `closure/reroute.py`. Baselines in `FlatSat_V1/tools/baseline/` (`heritage_rev2.json`, `drc_prelayout.json`, `drc_postsync.json`, `netlist_phase2.kicadxml`).

Workflows: `.claude/workflows/flatsat-supply-chain.js` (stage 1), `flatsat-layout.js` (stage 2 with `stage:"floorplan"`, stages 3–6 with `stage:"build"` + the owner-approved floorplan JSON), `flatsat-detailed-placement.js` (stage 2b), `pcb-flight-review.js` (stage 7, repo's existing review board).

The JLCPCB-plugin steps (project.db, F8, Generate) and the order itself remain the owner's GUI steps (Phase 3).
