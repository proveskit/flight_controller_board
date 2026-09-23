# PROVES FlatSat V1 — Phase 2 layout (started 2026-09-14)

Layout, DRC and the full review pipeline for the 218 new components captured in Phase 1, on a copy of the Rev2 flight-controller board whose own layout stays frozen. Plan numbering unchanged: schematic = Phase 1, layout = Phase 2, fab + firmware = Phase 3. Owner's model policy: Sonnet first; Opus for the floorplan judgement and stubborn DRC classes; Fable only in the repo's pre-order review board.

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
| `design_review.md` | Stage 7: `pcb-flight-review` result, fixes applied, deferred items |
| `layout_args.json` | Exact arguments used for `.claude/workflows/flatsat-layout.js` |

Tooling (`FlatSat_V1/tools/pcb/`, all validated by the PM on scratch copies before dispatch): `board_sync.py` (scripted Update-PCB-from-Schematic; parity proven), `heritage.py` (Rev2 snapshot/check; `--refill --core-inset 12 --ref-board` for the refilled core-fill check), `outline.py` + `outline_L1.json` (extension, planes, holes), `apply_placement.py` (real courtyard polygons for overlaps, pad copper for outline containment), `netclasses.py`, `make_keepout.py` → `fc_keepout.json` (Freerouting-side L11 fixture), `attachment_check.py` (L11 gate, `--prune` + dangling trim), `route.sh` + `route_merge.py` + `README.md` (Freerouting recipe with heritage lock, echo filter, auto-prune; §7 = the 2026-09-14 smoke-run findings), `drc_summary.py`, `render.sh`. Baselines in `FlatSat_V1/tools/baseline/` (`heritage_rev2.json`, `drc_prelayout.json`, `drc_postsync.json`, `netlist_phase2.kicadxml`).

Workflows: `.claude/workflows/flatsat-supply-chain.js` (stage 1), `flatsat-layout.js` (stage 2 with `stage:"floorplan"`, stages 3–6 with `stage:"build"` + the owner-approved floorplan JSON), `flatsat-detailed-placement.js` (stage 2b), `pcb-flight-review.js` (stage 7, repo's existing review board).

The JLCPCB-plugin steps (project.db, F8, Generate) and the order itself remain the owner's GUI steps (Phase 3).
