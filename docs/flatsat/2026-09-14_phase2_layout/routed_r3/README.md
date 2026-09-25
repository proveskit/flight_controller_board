# Routed board after closure round 3 (2026-09-23)

Copy of `.flatsat_work/phase2/round3/layout_finish/deliver/` (git-ignored working dir), committed so the work is
portable. NOT yet installed into `FlatSat_V1/` — the live board stays unrouted until the owner rules on via-in-pad.

- Unconnected 1 (U6.1/U6.29, Rev2 baseline), heritage 0, attachment 0, DRC errors 2 (both Rev2 baseline), parity 11.
- The `.kicad_dru` here carries the EMU_FANOUT rules (F13) and must travel with the board.
- Heritage zones hold Rev2's STORED fills (restorefills convention) — refill before any production export.
- To check it: copy this directory's files next to the FlatSat_V1 schematics/libs (e.g. copy `FlatSat_V1/` to a
  scratch dir and drop these four files in), then run the gates in route_report.md / layout_args_close3.json closureNotes.
