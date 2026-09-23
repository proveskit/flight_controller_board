# Independent-skeptic verification — strip_left_pyro_shunts (junior developer findings, run 1)

Board: `/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/panel/project/FlatSat_V1.kicad_pcb` (read-only, v2.2 scratch copy). Measurements re-taken directly in pcbnew (F_CrtYd and F_Fab bounding boxes, text graphics excluded from Fab bboxes to avoid silkscreen-on-Fab inflation).

## Method note (applies to both findings)

Both JD-03 and JD-08 measure **courtyard-to-courtyard** clearance and treat that number as the physical clearance available to a hand/tool. Courtyards intentionally carry a manufacturing/DRC safety margin beyond the part's actual body outline (confirmed here: KiCad's default ~0.5 mm/side margin on these `Conn_01x02_P2.54mm_Vertical` and `SW_SPDT_Shouhan_MSK12C02` footprints). For a *usability* question (can fingers/pliers/a fingernail physically reach between two populated parts), the relevant number is body-to-body (F.Fab outline) clearance, not courtyard-to-courtyard. I re-measured both using F.Fab.

## JD-03 — JP602–JP607 bench shunt bank spacing

**Reproduced base facts:** header centers at x = 188.75 / 194.50 / 200.30 / 206.10 / 211.90 / 217.70, pitch 5.75–5.80 mm, matches finding. Courtyard bbox w=3.59–3.63 mm — matches finding's courtyard-gap arithmetic (2.12–2.17 mm) exactly; that part of the measurement is correct.

**New measurement — F.Fab (actual header body) gaps, all six adjacent pairs:**
| pair | Fab-Fab gap |
|---|---|
| JP606–JP605 | 3.11 mm |
| JP605–JP603 | 3.16 mm |
| JP603–JP604 | 3.16 mm |
| JP604–JP602 | 3.16 mm |
| JP602–JP607 | 3.16 mm |

Real body-to-body clearance is ~3.1–3.2 mm, **43–46% more** than the 2.12–2.17 mm courtyard figure the finding leads with. A 2.54 mm shorting-block cap's housing is normally sized close to the header body it plugs onto (the header body itself measures ~2.64 mm across in this footprint), so adjacent-shunt-to-shunt clearance is of the same order as the Fab-to-Fab number, not the courtyard number. 3.1 mm of clear space between adjacent populated 2-pin headers on a 5.75–5.8 mm pitch is a very ordinary shunt-bank spacing (it's the ordinary consequence of using 0.1" headers at typical net-per-header layout density) — workable with fingertips and comfortable with fine pliers/tweezers.

**Verdict: downgraded, major → minor.** The usability concern isn't wrong in kind, but the evidence supporting "major" (2.17 mm, described as "tight to pull with fingers and tighter with pliers") used the wrong clearance metric and overstates the tightness by ~45%. At the corrected ~3.1 mm body clearance this is a normal, workable bench jumper bank, not a placement problem — no move is warranted before routing.

**Recommendation (kept, downgraded to informational):** No layout change. For the bring-up/assembly doc: note the 5.75–5.8 mm shunt-bank pitch (~3.1 mm clear between adjacent header bodies) so bench techs know needle-nose pliers or fine tweezers work more comfortably than thick-tipped pliers on this bank — but fingers are adequate too. This does not touch `placement_strip_left_pyro_shunts.md` checklist rows (courtyard/DRC rows already pass; this was never a courtyard-overlap item).

**Confidence: 0.8** (direct pcbnew re-measurement of Fab outlines on the live scratch board; the only residual uncertainty is the exact molded width of the physical shunt cap product the owner will source, which isn't pinned down in the brief).

## JD-08 — SW600 clearance to JP600/601 and LED600/R602

**Reproduced base facts:** courtyard-to-courtyard gaps ~0.96–1.00 mm to JP600/JP601 above and to LED600/R600 below — matches `facts.md` and the finding's citation.

**New measurement — F.Fab (actual body) gaps:**
- JP600/JP601 bottom edge (Fab) y=149.655 → SW600 top edge (Fab, text excluded) y=152.565 → **gap = 2.91 mm**, not 0.957 mm.
- SW600 actual Fab body footprint is 6.80 mm (x) × 4.35 mm (y) — a naive first pass that included silkscreen/value text on the F.Fab layer wrongly returned an inflated/overlapping bbox; excluding text items gives this consistent, non-overlapping outline.
- LED600/R602 are ~4.2 mm below SW600's Fab bottom edge (156.915) at their Fab top edges (~158.3–158.5 mm) → also comfortably clear, consistent with "no move needed" in the original finding.

Real clearance from SW600's actual body to the JP600/601 headers above it is essentially 2.9 mm — three times the courtyard-based 0.957 mm figure the finding cites, and enough that a shunt cap seated on JP600 or JP601 (typically a housing similar in footprint to the header body, i.e. not encroaching meaningfully past the header's own Fab edge) does not meaningfully crowd the slide switch's actuator/finger-access zone.

**Verdict: refuted (downgrade to note-only, or drop).** The "very little vertical room ... for a fingernail or small tool" claim rests on the courtyard number, which the PM has already treated as not diagnostic of real usability/assembly conflicts in this same block context (PM decision: "capacitors against the pin they serve may sit below 0.5 mm courtyard gap" — courtyard proximity alone is accepted where the physical/functional outcome is fine). Recomputing with actual body geometry shows ~2.9 mm free — there is no realistic actuation interference from JP600/601 shunts, with or without a shunt seated. The severity was already "minor" in the original report; on the corrected evidence this is not a real finding at all.

**Recommendation:** No bring-up-doc callout needed on this specific point; drop it. (If the panel still wants a general note that SW600 is a safety-relevant slide switch, that's independent of this clearance claim and out of scope for this refutation.)

**Confidence: 0.8** (same direct-measurement method as JD-03; residual uncertainty only in the exact molded shunt-cap product dimensions, which don't change the conclusion at a 2.9 mm margin).

## Summary
| id | verdict | severity after |
|---|---|---|
| JD-03 | downgraded | minor |
| JD-08 | refuted | note (drop) |
