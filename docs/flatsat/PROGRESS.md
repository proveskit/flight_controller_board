# FlatSat V1 Phase 2 closeout: progress log

Branch `claude/project-thread-ywww1h` from `origin/flatsat-v1` @ `487dfe0`. KiCad 10.0.6 (`kicad-cli`, bundled pcbnew).
Owner rulings F15/F16: `2026-09-14_phase2_layout/OWNER_RULINGS_2026-10-21.md`.
Every row is `FlatSat_V1/tools/pcb/gates.sh <board> <out>` run inside a project directory.

## Machine baseline (KiCad 10.0.6 on the Mac mini)

The round-3 numbers came from KiCad 10.0.1 on another machine. Two differences on this machine, both proven on flown Rev2:

- `annular_width` x12 on U6 PTH pad 29 (GND thermal pad, 0.10 mm ring vs the 0.13 mm board minimum). KiCad 10.0.6 reports
  the same 12 on `FC_V5e_Production_Rev2.kicad_pcb` itself. Heritage footprint, not touched. DRC errors baseline = 2 + 12 = 14.
- `lib_footprint_issues` 28 vs 3: this machine has KiCad's stock global library tables only; the old machine also had
  `easyeda2kicad` and `mainboard` configured. Warning only, no copper meaning.

## Gate table

| Step | Board | heritage (stored) | heritage --refill core 12 | attachment viol/warn/stubs | DRC errors | unconnected | parity | via in-pad / edge |
|---|---|---|---|---|---|---|---|---|
| 0 | `routed_r3` as committed (stored fills) | 0 | 0 | 0 / 0 / 37 | 14 (2 + 12 U6.29 annular) | 1 (U6.1/U6.29) | 11 | 45 / 19 (62 vias) |
| 0f | `routed_r3` refilled | 7 (expected: stored fills changed) | 0 (3 band notes, as round 3) | 0 / 7 / 37 (F15 warnings) | 14 | 1 | 11 | 45 / 19 |
| 1 | via-off-pad (`dogbone.py`, scratch, stored fills) | 0 | 0 | 0 / 0 / 37 | 14 | 1 | 11 | **7 / 0** (55 moved, 7 POFV) |
| 2 | installed in `FlatSat_V1/` + refilled (board, `.kicad_pro` netclasses, `.kicad_dru`) | 7 (expected after refill) | **0** (same 3 band notes as round 3) | **0** / 7 F15 / 37 | **14** | **1** | **11** | **7 / 0** |

Step 1: DRC item set identical to routed_r3 (0 added, 0 removed, compared by type + items). Per-via table and POFV
reasons in `2026-09-14_phase2_layout/via_off_pad.md`. QSPI growth: SD0 +2.9 mm, SS +1.9, SD1 +0.9, SD3 +0.3, SCLK/SD2 0.
| 3 | review fix-this-rev items 1,2,3,4,6,7 installed (refilled) | 7 (expected) | **0** | **0** / 7 F15 / 37 (J16.8 stub replaced by J14.1 In1 stub) | **14** | **1** | **11** | 7 / 0; track_width (new rule) 95 deferred residuals |

Step 3: DRC item set vs step 2: 0 removed, 1 added (footprint_type_mismatch U511, from the 9 EP thermal PTH pads; flown
U18 carries the same). ERC errors 12, unchanged. Details and before/after numbers: `2026-09-14_phase2_layout/review_fixes.md`.
Item 4 sub-asks not met (PM accepts (a) this rev): no 0402 across SYS/PGND (SW pins sit between them); CSYS return goes
via In1. Item 2 trunk layer changes stay single 0.8/0.4 vias.
