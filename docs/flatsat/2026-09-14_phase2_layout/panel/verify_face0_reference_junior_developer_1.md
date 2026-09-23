# Independent-skeptic verification — face0_reference — junior_developer batch 1

## JD-06 — TP courtyard pitch vs hook-clip/probe-tip width

**Verdict: CONFIRMED, severity downgraded minor -> note**

Re-measured courtyard-to-courtyard gaps directly with pcbnew on the scratch
copy (`cy_bbox` per footprint, F.Cu courtyard bounding boxes, gap = bbox
separation along the row axis):

| pair | measured gap (mm) | claim (mm) |
|---|---|---|
| TP300-TP301 | 1.00 | 0.96 |
| TP301-TP302 | 1.00 | (0.957 in facts.md) |
| TP600-TP601 | 1.00 | 0.957 |
| TP202-TP203 | 1.45 | 1.41 |
| TP500-TP501 | 1.45 | 1.41 |
| TP501-TP502 | 1.45 | (not quoted) |

Courtyard width both footprints = 2.55 mm (TestPoint_Pad_D1.5mm), matching
the finding's stated pad/courtyard geometry. My numbers run ~0.04 mm above
the finding's (courtyard-outline vs bbox rounding) — same order of
magnitude, claim's central fact holds: neighbouring TP courtyards on these
banks clear each other by ~1.0-1.45 mm, well under a typical hook-clip jaw
or a 2.5 mm bare probe tip (generic bench-tooling fact the finding itself
cites; not re-verified against a specific manufacturer page since it does
not change the verdict either way).

**Why downgraded, not just confirmed as-is:** the finding's own
recommendation already asks for *no placement change* — only a bring-up-doc
note about probe choice. That makes it pure information, not something to
"fix at a later stage or accept" (the minor definition). It also duplicates
ground already covered in `detail/placement_face0_reference.md` lines
102-105, which reviewed this exact TP300-306 row and closed it: "already
the best 'probe from the top edge, hand-reachable' row a bench tester could
ask for... there was nothing to improve." That is a closed placement
decision for this block; re-flagging it as an actionable minor conflates
"placement is fine" with "bring-up procedure needs a footnote." A pure
procedure note belongs at `note` severity per the panel's own rubric
(information, no placement consequence), while `minor` implies a residual
placement compromise being accepted — there isn't one; the row is at design
intent.

**Recommendation (improved):** keep the placement as-is (no board change).
Add one line to the bring-up/test procedure doc (not the layout doc): "TP300-306,
TP500-505, TP600-603, TP202/203 banks are on 3.5-4.0 mm pitch (courtyard
clearance 1.0-1.45 mm) — use a fine needle probe, not a hook/alligator
clip, on these banks." No datasheet/JLCPCB fetch needed since this doesn't
touch fab/assembly rules; it's a bench-tooling note only.

**Confidence: 0.85** (measurement reproduced within rounding; severity call
is a judgment on the note/minor boundary, not a factual dispute).
