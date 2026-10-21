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

## Pass 2 (final board, commit `1ccbd07`)

Rerun `wf_8830004d-04b` after the six fixes and the F17 via-in-pad rework. 15 agents, about 47 minutes.
All six pass-1 fixes confirmed correct, with no new failure or damage path. Files in `pass2/`.

| Rank | Severity | Disposition | Item |
|---|---|---|---|
| 1 | major | fix-this-rev | J510 USB-C face 2.41 mm behind the edge (HRO drawing: 0.46 mm proud); plugs may not seat |
| 2 | minor | fix-this-rev | J500 bench PSU: no OVP procedure or voltage legend; FC-copy 10 V caps behind it |
| 3 | info | fix-this-rev | ATP text: TP503/TP504 are referenced to floating nets, not GND |
| 4 | minor | next-rev | BQ25886 REGN/BTST caps not at their pins |
| 5 | minor | next-rev | C216.2/Y200.4 GND island returns through ~6 mm of 0.25 mm trace |
| 6 | info | accept-with-rationale | Mode 2 bypasses the ISS inhibit chain; sheet note added |
| 7 | info | accept-with-rationale | Mode-1 current through three 0.5 oz inner-layer 1.0 mm runs |
