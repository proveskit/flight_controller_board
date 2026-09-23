# Verify — vsolar_injection — junior developer findings (JD-02, JD-04)

Independent skeptic pass. Board re-measured with pcbnew on the read-only scratch copy
(`panel/project/FlatSat_V1.kicad_pcb`); positions below are my own fresh reads, not copied from the
junior developer's report.

## JD-02 — J400/J401 1.24 mm gap, no room for a legend between them

**Verdict: DOWNGRADED major → minor.**

Re-measured: J400 (228.960, 165.300, 0°, F), J401 (241.460, 165.300, 0°, F) — pitch 12.500 mm,
matches the report and matches the frozen v1/fix-round-2 record already on file
(`detail/audit_vsolar_injection.md` R6/§2). Courtyard width 11.26 mm (Phoenix MKDS-1,5-2-5.08 1x02,
standard KiCad courtyard) ⇒ 12.500 − 11.26 = 1.24 mm gap — the arithmetic reproduces cleanly; not
disputing the number.

What the finding misses: there is already a clear cross-block corridor for the legend that does not
need "planning" as new risk — it needs recording. Between F400/F401's courtyard bottom (≈156.2 mm,
F400/F401 at y=155.2 with a ~2 mm-tall courtyard) and J400/J401's courtyard top (159.545 mm) there is
a ~3.3 mm-tall band spanning the full x-range of the pair (225.9–249.6 mm) with no footprint in it —
confirmed against the block's own 11-ref list (D400/D401/F400/F401/J400/J401/JP400/JP401/TP400/TP401/
TP402; none of the others sit in y 156.2–159.5). A 1.2 mm-high legend line ("VSOLAR A/B" + polarity
marks) fits there with margin, on either side of the D400/F400 vs. D401/F401 midline, without touching
either courtyard. Below the pair there genuinely is no room (courtyard bottom 170.445 vs. Edge.Cuts
172.17 → 1.725 mm, too thin) — so the report's "above/below" framing partly overstates the option
space, but understates how much room exists above.

Per the report rules, a usability item that has a real placement consequence (no legal legend
position) is major; one where the fix is "write it down for stage 6, room already exists" is minor/
informational. Since the north corridor is free and adequately sized, this is a minor documentation
item, not a before-routing placement blocker. **No placement change needed.**

**Improved recommendation:** record in `detail/placement_vsolar_injection.md` (a new L8 sub-row) that
the "VSOLAR A/B" + polarity legend for J400/J401 sits in the F400/F401→J400/J401 corridor, y ≈
156.5–159.0, spanning x 226–249, not between the two terminal bodies. No geometry change; carry into
stage 6 (§L8).

**Confidence: 0.75.**

## JD-04 — JP400/JP510 0.87 mm gap, cross-block jumper confusion

**Verdict: REFUTED (as a new major finding).**

Re-measured: JP400 (252.800, 145.790, 0°, F), JP510 (257.300, 145.790, 0°, F) — pitch 4.500 mm;
courtyard width 3.63 mm (standard KiCad PinHeader_1x02_P2.54mm_Vertical courtyard) ⇒ 4.500 − 3.63 =
0.870 mm gap. The number is correct and reproduces the report's own figure.

But this exact pair, at this exact gap, is not new information — it is already measured, named, and
dispositioned in the record: `floorplan_v2.md` (whole-board audit) states "0 real or sub-0.5 mm
overlaps beyond the already-known, non-block-caused `JP400↔JP510` at 0.870 mm," and
`detail/audit_charger_bq25886.md` §round 6 independently re-derives the same 0.870 mm and calls it
"another block's fixed part vs. this block's fixed anchor — comfortably clear" with "0 cross-block
pairs" below the 0.5 mm PM-accepted threshold. 0.87 mm is not a courtyard overlap and is not a DRC
clearance violation (min clearance rule is 0.127 mm copper-to-copper; this is a silk/mechanical
courtyard gap, not copper). JP400 and JP401 are both named fixed anchors for vsolar_injection (R6,
`detail/audit_vsolar_injection.md` §2), and JP510 is charger_bq25886's own fixed anchor — moving either
re-litigates an already-accepted fixed-anchor position across two different accepted blocks, which the
PM decisions explicitly discourage absent a new measured reason. This finding presents no new
measurement beyond the one already on file, and the "usability/legend" concern it raises is squarely
an L8 stage-6 planning item (own function labels per header, e.g. "VSOLAR SEL" over JP400 and "CHG OUT"
over JP510, placed above/below each header individually rather than in the shared 0.87 mm gap) with no
placement consequence — it does not require moving either jumper.

**Improved recommendation:** no placement change (both are fixed anchors, already accepted, already
on record). For stage 6, put each header's own function label close to its own body (JP400: "VSOLAR
SEL" above/left; JP510: "CHG OUT" above/right) rather than a shared label in the 0.87 mm gap; this is a
label-placement note, not a layout finding.

**Confidence: 0.85.**

## Summary

| id | verdict | severity |
|---|---|---|
| JD-02 | downgraded | minor |
| JD-04 | refuted | n/a (no placement finding) |
