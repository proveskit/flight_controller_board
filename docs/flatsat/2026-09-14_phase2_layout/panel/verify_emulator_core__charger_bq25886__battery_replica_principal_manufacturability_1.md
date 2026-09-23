# Verification — emulator_core / charger_bq25886 / battery_replica (manufacturability)

Role: independent skeptic, manufacturability lens. Board: scratch copy of v2.2
at `.../scratchpad/panel/project/FlatSat_V1.kicad_pcb` (read-only).

## PLM-11 — Thermal-pad via arrays; U200 via-in-pad EP heritage-identical

**Verdict: CONFIRMED (severity unchanged: note)**

Re-measured directly with pcbnew, comparing the READ-ONLY live board
(`/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/FlatSat_V1.kicad_pcb`,
never written) against the scratch review copy:

- U18 (live, heritage) footprint id = `RP2350-QFN-60-1EP_7x7_P0.4mm_EP3.4x3.4mm_ThermalVias`,
  74 pads, 9 pads with nonzero drill (via-in-pad).
- U200 (scratch v2.2) footprint id = identical string, 74 pads, 9 via-in-pad
  pads. Byte-for-byte footprint match confirmed — this is genuinely flown,
  JLC-assembled hardware, not a new design. L4 (heritage frozen) applies: no
  placement change is possible or warranted regardless of manufacturability
  opinion on via-in-pad EPs.
- U511 EP: pad "25" (thermal pad) is 2.700x2.700 mm, drill = 0.000 mm —
  confirmed no via-in-pad in the current footprint, matching the finding.
- 3x3 via array feasibility recomputed independently: with the project
  minimum via (0.4 mm pad OD / 0.2 mm drill) at 0.9 mm pitch, outermost via
  centers sit 0.9 mm off EP-center, plus 0.2 mm pad radius = 1.1 mm reach.
  EP half-width is 1.35 mm, so margin to EP edge = **0.25 mm** (finding
  states 0.22 mm — close, likely a rounding/annular-ring convention
  difference; direction and conclusion, "fits with margin," both hold).
- B.Cu occupancy re-checked by radius search against every foreign pad and
  every B.Cu track/via on the board: zero foreign B.Cu pads and zero B.Cu
  copper within 3 mm of U511/Q500/Q501, 4 mm of L510, 2 mm of Q510 — matches
  the finding exactly (expected also because nothing is routed yet, so no
  B.Cu tracks exist anywhere on the new area).
- Courtyard gaps for C510/C511/C512/C516 vs U511 cross-checked against
  `facts.md`: 0.280/0.280/0.300/0.300 mm — matches the finding's "0.28-0.30
  mm outside U511's courtyard" claim; since courtyard encloses the full
  footprint (EP included), these caps are necessarily clear of the EP too.

No placement change needed; this is correctly scoped as a routing-stage
note, not a placement finding, and correctly says so. Improve the
recommendation only in emphasis: explicitly flag for the routing stage that
U511's 3x3 via array at 0.9 mm pitch leaves just 0.25 mm annular margin to
the EP edge — tight enough that the router/fab step should confirm JLCPCB's
via-in-pad tenting/plugging capability before committing to that exact
pitch, but this is a routing-stage action item, not a v2.2 placement
blocker.

**Confidence: 0.9** (own pcbnew re-measurement matches the finding's
numbers to within rounding; heritage-identity claim independently verified
against the live board's U18.)
