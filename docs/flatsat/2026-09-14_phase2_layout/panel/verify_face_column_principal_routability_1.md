# Verification — face_column — routability reviewer — run 1

## PLR-01: heritage B.Cu wall (PAYLOAD_BATT + DEPLOY1) blocks J2/J9/J13 stubs

**Verdict: CONFIRMED, blocker, confidence 0.92**

### Re-measurement (pcbnew, live scratch board)
- PAYLOAD_BATT vertical run on B.Cu: bbox x 223.500–223.900 (w=0.400), y 84.800–129.900
  (segment endpoints (223.70,85.00)-(223.70,129.70) confirmed by direct track read).
- DEPLOY1 vertical run on B.Cu: bbox x 224.183–224.818 (w=0.635), y 84.282–132.626
  (segment endpoints (224.50,84.60)-(224.50,132.31) confirmed).
- Gap between the two: 224.183 − 223.900 = **0.283 mm** (finding claimed 0.28 mm — matches).
  Minimum needed for any track at the board's absolute floor rule (0.127 track /
  0.127 clearance each side) = 0.127 + 2×0.127 = **0.381 mm > 0.283 mm available**. No
  track of any legal width fits in that gap. This reproduces the finding's r8.py result
  independently (0 bands at x 223.5/224.0/224.5/225.0 for y 85–128).
- The wall is continuous across y 84.8–129.9, which fully contains J2 (87.80–95.30),
  J9 (102.81–110.31) and J13 (117.80–125.30) — all three connectors' pin rows sit inside
  the blocked span, not just brushing an edge of it.
- Checked for a cheap "go around": north end of the wall (y<85) is not open ground — it's
  packed with heritage Deploy1_EN/FIRE_DEPLOY1_A/SWDIO/SWCLK vias and PAYLOAD_BATT's own
  diagonal fan-out (x 222.3–223.9, y 81.9–85.2), so a short northward jog for J2 does not
  have clear passage either. South end frees up only past y≈130–134, which is 5–12 mm
  below J13's pins — well over L11's 12–14 mm stub cap once added to the pad→edge run.
  This corroborates the finding's "20+ mm to go around" claim rather than refuting it.

### Rule check
- 00_pm_brief.md §L11 (verbatim): J2/J9/J13 are bottom-side → "stub on B.Cu"; "no new via
  inside the old outline"; fc_keepout.json rule (3): "the whole band ring blocked on
  In1/In2 (no stubs on the plane layers)". So neither an inner-layer detour nor a via
  hop is currently legal — the constraint is exactly as the finding states, not a
  misreading.
- L4 (heritage frozen) forbids moving PAYLOAD_BATT/DEPLOY1 to open the gap — no
  placement-side fix exists within current rules. This is not one of the PM's
  standing pre-decisions (support-parts-in-loops, sub-0.5mm capacitor courtyards,
  fixed-anchor envelope breaches, 0402 poking into the 12.6mm band) — none of those
  cover an L11 attachment path being physically closed, so it is not something already
  litigated and dismissed.

### Recommendation feasibility check (added value beyond the original finding)
Scanned F.Cu in the proposed via band (x 221.5–223.2, y 85–128): it is **not empty** —
heritage VSOLAR/GND/F0_PWR/F3_SDA breakout vias and pads already occupy parts of it
(e.g. VSOLAR vias at x 221.52–222.18 sit right at J9's SCL/SDA pin y-levels
108.42–108.98 and 109.92–110.48). There is still a usable pocket: gap from the VSOLAR
via edge (222.18) to the PAYLOAD_BATT wall (223.5) is 1.32 mm, enough for a ~0.4/0.2mm
via with clearance to spare. For J13 (y 122.8–125.3) F.Cu is more congested
(F3_SDA copper out to x≈223.0), matching the original finding's own caveat that J13
needs its via shifted to x 221.5–222.0. Net: the recommended fix is workable but each
of the 9 net vias needs its own per-y clearance check against existing F.Cu heritage
copper, not just against the B.Cu wall — add this as an explicit sub-step for whoever
implements the L11 amendment.

### Final recommendation (refines the original)
Confirm as blocker. Owner must decide on an L11 amendment before routing: permit one
B.Cu→F.Cu via per net (9 total) inside the attachment band, west of the PAYLOAD_BATT/
DEPLOY1 wall, each individually cleared against existing F.Cu heritage copper (not
just placed at a uniform x) — J9's SCL/SDA fit near x 222.2–223.3; J13 needs x
221.5–222.0 per the original note; J2 should be checked the same way before committing
(not yet measured here, flag as follow-up). Alternative unchanged: drop F1/F3/F5 from
FlatSat V1 and populate only the top-side faces (J1/J6/J11) if the owner will not amend
L11.
