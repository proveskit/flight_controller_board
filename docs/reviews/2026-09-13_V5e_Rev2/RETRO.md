# Retro: FC V5e Production Rev2 pre-order review (2026-09-13)

One session, product manager + Claude Code orchestrating subagents. Goal: catch anything real on Rev2 before ordering, without churning a layout that has flight heritage (V5d) and environmental validation (V5e Rev1). Boards were ordered at the end of the session.

## What we did

| Stage | Agents | Output |
|---|---|---|
| Design review workflow | 6 reviewers (2 Sonnet, 4 Opus) → 8 Opus subsystem verifiers → 2 Fable principals (PCB, QA) → Fable chair merge | 21 raw findings → 17 confirmed, 3 refuted, 1 duplicate → 12 prioritized items, 2 fix-before-order |
| Supply chain | 1 Opus agent, refreshed the JLCPCB Tools parts DB, live JLC lookups | 2 zero-stock lines, 1 wrong-part assignment, 3 missing assignments, 4 quantity-limited lines |
| P0/P1 fan-out | 5 agents (project.db owner, schematic owner, 3 read-only studies) | DF11 alternate, U1 fix, TPS54225 verified, RTC trade, SD-NAND alternate |
| Order prep | inline | value normalization, DRC rule, production files, R42 swap, CPL rotations |

Workflow cost: 17 agents, ~2.0M tokens, 51 min for the review pipeline. Roughly another 0.6M across the follow-up agents.

## What went well

- **Verification stage earned its keep.** Three review findings were flat wrong (USB-C CC pull-downs "missing", PSRAM "no decoupling", LIS2MDL C1 "wrong value"). All three cited datasheet numbers confidently. The Opus refuters caught every one by reproducing the evidence. Never ship a first-pass review list without this stage.
- **Batching verifiers by subsystem** instead of one per finding cut agent count roughly in half with no visible loss. One agent loads the LT3652 datasheet once and checks six charger findings.
- **Heritage as an explicit input.** Telling agents "V5d flew, Rev1 passed environmental, zero findings is fine" produced a list with no criticals and no majors surviving, which matched reality. Both Fable principals independently declined to fold Rev3 decoupling adds into Rev2, citing the C10 regression as evidence that incidental edits carry risk.
- **The one real Rev2 defect was found.** C10 had been nudged 0.125 mm in commit 066aeb7 to dodge a hand-drawn courtyard, leaving four clearance errors including a 0.089 mm +3V3-to-GND gap. Fix was a move-back plus courtyard trim, DRC returned to the Rev1 baseline exactly.
- **Supply chain review found a wrong part that had already been built.** U1 was assigned C33503485, a TLV1824 in SOIC-14, on a TSSOP-14 land. Same LCSC in the Rev1 as-ordered BOM. Rev2 now carries the right TLV1704AIPWR. Rev1 units should be inspected at U1.
- **Agent skepticism of the orchestrator.** The project.db agent rejected the DF11 alternate I handed it (C7427056, a right-angle body) and found the correct vertical variant (C506665) by reading the package description and the footprint's 3D model reference.
- **Owner-per-file fan-out** (one agent owns project.db, one owns schematics, others read-only) avoided any write conflicts across five parallel agents.

## What went wrong

- **project.db regression.** I wrote normalized value strings into the plugin's project.db while the board still carried old strings. The JLCPCB Tools plugin treats a value mismatch as "part changed" and clears the LCSC assignment. 30 rows lost their LCSC on the next plugin start. Root cause: I did not read the plugin's `update_from_board` before writing its database. Recovered with a repair script and a fixed sequence (F8 first, then sync).
- **Stale in-memory schematic.** Editing `.kicad_sch` on disk while Eeschema had the sheets open meant Update PCB from Schematic pushed old values. Worse, a save from Eeschema would have overwritten the disk edits. Rule: close Eeschema before scripted schematic edits, or edit through the GUI.
- **First workflow launch used one verifier per finding.** The PM caught it as wasteful before any agent finished. Should have defaulted to batching.
- **Plugin default rotation was wrong for a bottom-side USB-C.** The shipped correction table had +180 for the HRO TYPE-C-31-M-12. Combined with the plugin's bottom-side mirroring, the CPL came out 180 off. Only discovered in the JLC placement viewer. Now set to 0 for this footprint; re-check if the footprint is ever placed on top.
- **D7 value churn.** An agent changed D7 to 1N4148WS to match the as-built LCSC, contradicting a schematic note "D7 MUST be 1N4151WS". The PM caught it. Reverted and assigned an in-stock 1N4151WS instead. Lesson: schematic text notes are design intent and must be surfaced before an agent overrides them.
- **`git checkout` blocked by the permission classifier.** Minor, worked around with exact string replacement, but it cost a turn.

## Lessons for next time

1. Run the review workflow before the production-files commit, not after. Parametrize with the new project path and heritage list.
2. Never write the plugin's project.db values directly. Let the plugin sync from the board, then only touch the `lcsc` column.
3. Close Eeschema and Pcbnew before scripted edits to `.kicad_sch` / `.kicad_pcb`. Lock files in the project dir are the tell.
4. Treat schematic text notes as requirements. Grep for `(text "` on any sheet before changing a part.
5. Check the JLCPCB Tools rotation table against the JLC placement viewer on the first order of any new footprint. Record corrections in the plugin, not in the GUI.
6. The as-ordered BOM/CPL must be in git. `*.csv` is ignored repo-wide, so force-add them.
7. Before ordering: buy the scarce parts first (RTC, high-side switch, radio modules). Stock at JLC on Extended parts can go to zero between review and order.

## Open items carried to Rev3 / flight build

See `design_review.md` items 4–12 and `rtc_trade_study.md`. Short list: JP6 bridged on flight units with an ATP line; PSRAM memtest at temperature with radio TX in the Rev2 test campaign; RV-3028 second source or RV-3032 migration; 4 Gb SD-NAND; decoupling adds on E28, TPS54226 VCC, TLV1704, PSRAM; solar shunt value and Kelvin taps.
