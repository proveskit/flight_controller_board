# Verification — bench_io_drivers — principal/manufacturability review 1

Reviewer: independent skeptic (manufacturability). Board checked: scratch copy
`/private/.../scratchpad/panel/project/FlatSat_V1.kicad_pcb` (v2.2, read-only,
loaded via pcbnew, not the live board).

## PLM-07 — SW703 empty courtyard blinds the courtyard-overlap gate

**Verdict: CONFIRMED, severity as-reported (minor).**

Re-measured independently with pcbnew:

- `SW703.GetCourtyard(F.CrtYd).OutlineCount() == 0` and `B.CrtYd` is also 0.
  Confirmed empty on both sides — matches the finding exactly.
- Full-board audit of all 483 footprints: 11 have an empty courtyard on both
  sides, not just SW703: `RF1, U30, U12, BT1`, four `LOGO` graphics, and one
  `REF**` (XYZ_cubesat-top marker). All of these sit at x = 167–211 mm — the
  original Rev2/FC heritage footprint area, frozen under L4 — so they are
  heritage parts, not among the 218 new parts. **SW703 is confirmed to be the
  only one of the 218 new footprints with an empty courtyard**, exactly as
  claimed.
- Real geometry (pads + non-text graphics only, excluding ref/value text):
  SW703 bbox x 244.000–256.950 mm, y 64.000–70.950 mm — matches the finding's
  quoted bbox exactly (12.95 × 6.95 mm body).
- Gap to nearest neighbours by this real bbox: Q701 0.995 mm, Q702 0.995 mm,
  Q703 1.000 mm. (Finding quoted 0.97–0.98 mm from a slightly different bbox
  method; same conclusion — **no overlap**, ≥ 0.95 mm clear on all three.)
- `GetFootprint().GetFPID()` confirms footprint id
  `SW-TH_SHOU-HAN_SS12D10G4` (easyeda2kicad import), the only new footprint
  with this problem — consistent with it being an easyeda2kicad conversion
  artifact rather than a hand-authored KiCad footprint.

Conclusion: the measurement is accurate and reproducible. This is correctly
scoped as minor — there is no actual overlap today (confirmed ≥0.95 mm real
clearance to all three neighbours), so it does not block routing or
assembly. But it is a genuine, currently-invisible gap in the "courtyard
overlaps = 0" hard gate: any future nudge of SW703 or its neighbours that the
team checks only via that gate would not be caught even if it created a real
collision, because the courtyard polygon this part reports is empty. This is
a legitimate forward-looking audit-integrity issue, not a routing/silkscreen
matter, and not something the PM decisions already cover.

**Recommendation (unchanged, confirmed feasible):** add an `F.CrtYd`
rectangle to the project's local copy of
`footprints.pretty/SW-TH_SHOU-HAN_SS12D10G4.kicad_mod` at
x 243.75–257.20 mm, y 63.75–71.20 mm (real body bbox + 0.25 mm), matching the
part's placement at (250.475, 67.475). This is a footprint-file edit, not a
board edit — it does not touch heritage parts/tracks/zones (L4) and does not
require the KiCad GUI (a plain S-expression text edit of the `.kicad_mod`
adding one `(fp_rect ... (layer "F.CrtYd") ...)` line is sufficient). As a
fallback, the gate script itself could treat an empty courtyard as "fall back
to real bbox" rather than "0 = clean," which would also catch the other 7
heritage empty-courtyard parts if any of them are ever perturbed — but since
those are frozen (L4) that fallback is optional, not required.

**Confidence: 0.92** (own pcbnew measurement matches the reported bbox and
courtyard state exactly; only the exact neighbour-gap figure differs by
~0.02–0.03 mm depending on bbox method, which does not change the verdict).
