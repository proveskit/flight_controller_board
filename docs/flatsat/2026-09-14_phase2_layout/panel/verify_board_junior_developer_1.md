# Independent skeptic verification — junior developer / bench-user panel, block "board"

Panel: FlatSat V1 floorplan v2.2 pre-routing review, 2026-09-19. Verifying 2 findings from
`junior_developer.md` against a fresh `pcbnew` load of the same read-only scratch board
(`.../scratchpad/panel/project/FlatSat_V1.kicad_pcb`, copied to my own scratch dir before
running any query) and the source docs (`floorplan_v2.md`, `00_pm_brief.md`).

## JD-01 — "No test point exists anywhere on any I2C bus net" (reported major)

**Re-measured independently.** Full `pcbnew` pad-net dump of every `TP*` footprint (32 found:
4 heritage TP2/TP5/TP6/TP8 + 28 new TP200–706-series) confirms the reporter's numbers exactly:
TP300–306 = `F0_PWR..F5_PWR`/`+3V3` (power, not I2C, despite the generic "TestPoint" value),
and no TP pad net contains `SCL` or `SDA` anywhere on the board. The measurement is correct
and reproduces cleanly.

**Verdict: refuted (out of scope for this review, not a placement defect).**

The 28 new test points and the specific net each one is dropped on were fixed in **Phase 1
schematic capture**, not in Phase 2 floorplan/placement. `00_pm_brief.md` §3.1 ruling **S5**
already covers test points explicitly ("Test points (28) have no LCSC — correct per FC
convention; unchanged") and `floorplan_v2.md` row 5/R4 already audited every existing TP's
*placement* (reachability, no part overhead, ≥0.5 mm courtyard clearance) against the nets the
schematic gave it — all **PASS**. Nobody at floorplan stage chose which nets get a test point;
that roster is Phase 1 content, already reviewed and closed out.

The finding's own recommendation concedes this: "This needs a schematic-level part addition...
should go to the owner now." Adding new `TestPoint_Pad_D1.5mm` symbols on the buffered SCL/SDA
pins is not achievable by moving any of the 218 already-placed parts — there is no placement
fix available, so it cannot be a placement finding under this review's charter ("Do not report
things ... that belong to routing/silkscreen stages unless the placement makes them
impossible" — this is the same exclusion one stage earlier: it belongs to schematic capture,
already complete, and the missing TPs make nothing about the current placement impossible).
I could not find the cited "Task brief workflow step 4... 'the shared I2C buses'" text anywhere
in `floorplan_v2.md`, `00_pm_brief.md`, or `blocks.json` — the reference does not resolve, which
is a second, independent reason to discount it as this review's finding rather than a stray
citation from a different task.

If the owner wants I2C bring-up probe points, that is a schematic-revision request for a future
pass (e.g., one shared TP per face on the buffered SCL/SDA output, or 2 TPs on the raw
`EMU_SCL`/`EMU_SDA` bus as the reporter suggests) — worth carrying forward as a **note** for the
next schematic revision, not a Phase-2 placement blocker/major.

- Confirmed facts: TP net dump matches reporter's table exactly; 0 TP nets contain SCL/SDA.
- Refuted as a **placement** finding: no placement action resolves it; the gap is a Phase-1
  schematic-capture omission, already reviewed and signed off (S5), and out of this review's
  remit per the same "belongs to a different stage" exclusion the brief names for
  routing/silkscreen.
- Recommendation if carried forward at all: log as a **note** for the *next schematic
  revision* (new TestPoint symbols on U300/U310–U316 pins 3/6, or on `EMU_SCL`/`EMU_SDA`),
  addressed to the owner as a schematic change request, not to this floorplan.
- Confidence: 0.9 (the net-name measurement is unambiguous; the scope call follows directly
  from S5 and the brief's stage boundaries).

## JD-05 — "J12 (FC's own laptop USB-C) is bottom-side while every other bench connector is top-side" (reported note)

**Re-measured independently.** `pcbnew`: `J12` side = **B**, rotation **-90°**, position
**(223.160, 78.600) mm** — matches the reporter exactly. All eight comparison connectors
(`J701, J510, J500, J400, J401, J22, J702, J703`) confirmed side = **F**. J12's B.Courtyard east
edge measured at **x = 227.335 mm** (reporter: 227.355 mm, 0.02 mm apart — a courtyard-segment
selection rounding difference, not a disagreement); using the face-column west edge at
x = 243.495 mm (per `floorplan_v2.md`'s block envelope table) that gives **16.16 mm** clear
(reporter: 16.14 mm) — same result within measurement noise, and either way well clear of any
plausible USB-C plug/cable body.

**Verdict: confirmed, severity correct (note).**

J12 is a Rev2 heritage part (L4, `00_pm_brief.md` §3 — no existing footprint moves/flips/
rotations), so nothing here is fixable by this floorplan even if it wanted to be; the finding
already says so and does not ask for a placement change. It is accurately measured,
correctly scoped as informational (a bring-up-fixture note, not a routing/manufacturability
issue), and does not conflict with any PM decision or L-rule. No change to severity or
recommendation.

- Confirmed facts: side/position/rotation for J12 and all eight comparison connectors; clear
  distance ~16.1 mm either way (both numbers reproduce to within a rounding difference on which
  courtyard segment is used as the reference edge).
- Recommendation stands as written: document the required underside access / standoff height in
  the bring-up guide; not a placement action.
- Confidence: 0.92.

## Summary

| ID | Verdict | Severity after | Notes |
|---|---|---|---|
| JD-01 | refuted (as a placement finding) | note (if carried forward at all) | Measurement correct; belongs to Phase-1 schematic capture (already closed, S5), not Phase-2 placement; no placement fix exists; cited brief text not found. |
| JD-05 | confirmed | note (unchanged) | Measurement reproduces within 0.02–0.02 mm; correctly scoped as a bring-up-documentation note only; J12 is heritage-frozen (L4). |
