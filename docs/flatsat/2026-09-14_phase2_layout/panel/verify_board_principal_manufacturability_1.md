# Skeptic verification — board/manufacturability panel (relaunch, 2026-09-19 evening)

Board: scratch copy `.../scratchpad/panel/project/FlatSat_V1.kicad_pcb` (read-only, per HARD RULES). No live board touched, no commits.

## PLM-02 — J12 USB-C plug envelope blocked by new wing — CONFIRMED, UPGRADED major -> blocker
Re-measured J12 directly: `pos=(223.160,78.600) rot=-90 side=B, fpbbox x 217.865..227.335, crtyd x 217.845..227.355 y 73.235..83.965`. Pads sit at x=219.115, so the mating/shell face is at the high-x end (227.355), i.e. it opens toward +X — straight into the new wing, matching the finding.
Edge.Cuts scan of the FlatSat board, x 224..246 / y 54..136 (the disputed corridor), found exactly two Edge.Cuts shapes, both confined to y 50.6..54.1 (the unrelated north slot at x 223.6-229.2) — **zero** cutout anywhere in y 55..135. This reproduces the finding's central claim: no relief exists, the wing is solid board from the old FC edge (227.50) out to 296.44 across J12's full height. There is nothing a placement move can do about this — it's PCB material, not a part.
Per the panel's own severity rubric ("blocker = ... cannot be assembled, cannot be mated/used, or breaks an owner rule"), a receptacle whose cable cannot be inserted is a mate/use failure, not a "should fix" — so this is a **blocker**, not major. Recommendation as written (relief slot vs. document J12 as not-matable and route the FC over J703/J702/J701 instead) stands; add "escalate to owner before block-level acceptance is finalized for routing" since it's a topology decision, not something routing can absorb.
Confidence: 0.85.

## PLM-05 — first-use footprint rotations lack a corrections.db rule — CONFIRMED fact, DOWNGRADED major -> minor
CLAUDE.md rule 5 exists exactly as quoted: "Check rotations in the JLC placement viewer on the first order of any footprint... Known: ... `^USB_C_Receptacle_HRO_TYPE-C-31-M-12*` 0 (plugin default of +180 is wrong for bottom-side placement)." So the finding's facts (rule text, the J12/bottom-side note) check out.
But rotation correctness only changes a CPL angle value at assembly-file-generation time; it moves no XY position, breaks no clearance, and has no placement or routing consequence — it belongs squarely to the later CPL/BOM stage the panel is told to exclude ("do not report things that belong to routing/silkscreen stages... unless the placement makes them impossible"), and here placement is unaffected either way. That is a minor ("fix at a later stage") item, not a pre-routing major. Recommendation to walk the 22-family list in the JLC viewer before committing reels is sound and should be kept as a stage-6/CPL action item.
Confidence: 0.75.

## PLM-08 — three LCSC SKUs for one 1x02 header function — CONFIRMED as-is
supply_chain_report.md reproduces exactly: C492401/PZ254V-11-02P for J300, JP400, JP401; C358684/MTP125-1102S1 for JP500, JP510; C124375/B-2100S02P-A110 for JP600-607 (all Extended). C701 line also reproduces verbatim: 10uF 0805 X7R Extended C2182156/EMK212BB7106KG-T, with the report's own text confirming Basic X5R alternates C15850 (25V) and C440198 (50V) exist and are usable if X5R is acceptable. No placement consequence either way; minor/BOM-consolidation severity is correct.
Confidence: 0.85.

## PLM-09 — fiducial candidate scan — CONFIRMED overall, evidence CORRECTED (more favorable)
Re-ran the 3.35 mm keep-clear check against every F.Cu footprint's courtyard bbox, then again against full footprint bounding boxes (a stricter/more conservative test): (232.5, 50.5), (262.0, 50.0) and (262.0, 140.0) all came back clear at 3.35 mm, matching the finding. But (252.0, 140.0), which the finding says is clear only at 2.0 mm and fails at 3.35 mm, measured **clear at 3.35 mm** in both of my checks — I could not reproduce an obstruction there. This doesn't weaken the finding; it means there are more usable fiducial sites than reported, which only helps the stage-5 fiducial-placement task. Core claim (no fiducials exist yet, most natural corners are occupied, at least one/three candidates are genuinely clear) holds. Severity stays minor; keep the recommendation but note (252.0,140.0) can likely be used as a second/third site without waiting on the routing-corridor budget, loosening the "pick the other two after corridor budget is settled" caveat.
Confidence: 0.7.

## PLM-10 — component spacing is not an assembly problem — CONFIRMED exactly
Re-measured F.Fab body-to-body gaps directly: L200-C217 = 0.500 mm (finding: 0.500, exact match); U315-C315 = 0.774 mm (finding: 0.774, exact match); U200-C212 measured 0.855 mm body gap (finding's "0.774" figure was for U315-C315, not this pair — my own U200-C212 number differs but is still well above any bridging/placement risk threshold, so it doesn't change the conclusion). This is an informational note correctly closing section B.2 with no action; PM already ruled the courtyard-gap list out of scope. No change.
Confidence: 0.8.

## Notes
- Nothing routed, no DRC re-run (used drc_v22.json only where needed — not needed for these 5 items), no writes to the live board, no git commits, no GUI opened.
- Total tool calls kept within the 30-call budget.
