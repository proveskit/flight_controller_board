# FlatSat V1 pre-order review, 2026-10-21

`pcb-flight-review` (CLAUDE.md pre-order step 2) on `FlatSat_V1/` as installed at commit `5ee7219`
(routed board + F16 via-off-pad, zones refilled). Run `wf_faedff08-e88`: 6 reviewers with FlatSat-specific
dimensions (`docs/flatsat/2026-09-14_phase2_layout/review_args_flatsat.json`), Opus verifiers per subsystem,
two Fable principals (PCB, QA), Fable chair. 16 agents, about 58 minutes.

| Rank | Severity | Disposition | Item |
|---|---|---|---|
| 1 | major | fix-this-rev | Mode 2 feeds the FC from BQ25886 BAT, not SYS; termination and timers cut FC power |
| 2 | major | fix-this-rev | Bench battery current enters the FC copy via J16.8 and a 0.4 mm heritage inner trace, not J14 |
| 3 | major | fix-this-rev | Replica drain link inside the R5460 sense loop trips excess-discharge at ~2-2.5 A |
| 4 | major | fix-this-rev | BQ25886 SYS hot loop through 2 vias and In2, no EP vias, no GND vias at the caps |
| 5 | major | monitor-in-test | U200 core-regulator cell differs from the RP2350 reference / flown U18 cell |
| 6 | minor | fix-this-rev | Bench power width not DRC-enforced; auto-named power nets have no netclass |
| 7 | minor | fix-this-rev | VSOLAR bench hard maximum 24 V -> 18 V (heritage C40 is 10 V X5R) |
| 8 | minor | next-rev | F1-F4 face-power sense taps on non-5V-tolerant RP2350 ADC pins |
| 9 | minor | next-rev | No reverse-polarity element on J500 bench PSU input |
| 10 | minor | next-rev | R503/R504 synthetic midpoint margin to R5460 over-charge threshold at 8.4 V |
| 11 | minor | next-rev | New-area silkscreen below JLC minimum; 12 refdes over pad openings |
| 12 | info | no-action | EMU QSPI 30-49 mm is fine at the 75 MHz default flash clock |

Files: `final_list.md` (chair's list with locations, rationale, actions, verification, dropped items),
`final.json` (same, structured), `agents.json` (every agent's raw return: reviewers, verifiers, principals).
Fix outcomes for the fix-this-rev items are in `docs/flatsat/PROGRESS.md`.
