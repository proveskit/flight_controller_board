# Independent skeptic verification — vsolar_injection — routability panel

Role: refute/confirm findings from principal (routability) + junior reviewer, block vsolar_injection.
Board under test: scratch copy `/private/tmp/.../panel/project/FlatSat_V1.kicad_pcb` (READ-ONLY, measured via pcbnew only).

## PLR-07 — "VSOLAR needs a 43 mm detour around a Rev2 outline notch at x=227.5" — **REFUTED**

**Geometric premise is fabricated.** I dumped every `Edge.Cuts` drawing segment/arc on the scratch board for
`55 < y < 172` (the full span the finding cites, 62.5–127.7, plus margin). Result: the only Edge.Cuts
geometry in that y-band is (a) the heritage FC's own notch far to the west, x 143.34–155.5, and (b) one
continuous straight line at **x = 296.39** from y=51.58 to y=168.12 — i.e. the *entire* east edge of the
board in this y-range is flat at x=296.39. There is no vertex, line, or arc anywhere near x=227.5 or
x=231.39 in 62.5<y<127.7. The "outline steps back out to x=231.39 below y=127.7" and "inset to x=227.5
between y 62.5–127.7" claims do not correspond to any edge geometry on this board — command:
`pcbnew.LoadBoard(...).GetDrawings()` filtered to `GetLayer()==Edge_Cuts`, dumped start/end in mm.

Consequently the reasoning built on that notch — "a track leaving J11.1 eastward re-enters the flight
section unless it first moves east of x=231.4" — has no physical basis on this board revision. J11.1
(220.905, 125.300, measured) sits inside solid board area all the way to x=296.39; nothing in the outline
forces an eastward jog to x≈231.6 before heading south. (There may still be a *copper/component* corridor
argument for routing this way — heritage VSOLAR daisy-chain track, other parts — but that is a congestion
question for the router, not an outline constraint, and the finding's own evidence section only cites the
outline, not a component-congestion scan.)

**Reach number itself is already an accepted, gated metric, not a routing target.** Pad-to-pad remeasured
directly: J11.1 (220.905,125.300) → JP401.2 (226.200,156.470) = **31.617 mm** straight line (pcbnew),
matching floorplan_v2.md's own L11 table (31.62 mm) and the audit's R5 figure (31.617 mm) exactly. That
number is the *placement-stage attachment-reach gate* (FC pad → nearest new pad on the shared net, budget
±3 mm vs v1, audited PASS at +0.494 mm). It was never asserted to be the final routed track length, and
routed length legitimately differing from the airwire is routine and belongs to the routing stage per the
panel's own reporting rule ("do not report things that belong to routing... unless the placement makes
[routing] impossible"). The finding does not show routing is impossible — only longer than the airwire,
which is true of nearly every net on every board.

**The recommended fix is invalid: JP401 is a named fixed anchor.** `blocks.json` →
`vsolar_injection.fixed_anchors = ["J400","J401","JP400","JP401"]`. floorplan_v2.md's own audit (R6/R7)
re-confirms JP401 at (226.20, 153.93/156.47 pad) "bit-for-bit the v1 values... fixed anchors, not touched
by this pass" and that constraint (b) plus a PM ruling forbid moving J400/J401/JP400/JP401. Recommending
"Move JP401 east... to about (233.5, 156.5)" contradicts an owner-level fixed-anchor rule already locked
in v2.2 (screw-terminal/jumper mechanical accessibility, R6) — this is exactly the class of item COMMON
says not to re-litigate ("fixed-anchor envelope breaches are not findings"). Moving JP401 is out of scope
for this panel regardless of routing benefit.

**The "gate false positive" claim is also refuted.** `attachment_check.py` (lines 261-266) already exempts
exactly this case: "a stub may share the pad point with the heritage track that ends on the same pad; any
other coincidence is a tap" — only an off-pad endpoint coincidence is flagged as
`touches heritage track/via endpoint(s) off-pad`. Since J11.1 is the one allowed pad the VSOLAR stub must
land on, a heritage VSOLAR track also terminating there is the expected, already-handled case, not a bug
to pre-empt. Proximity (the finding's "within 0.3 mm") without endpoint coincidence does not trip this
check at all.

**Disposition:** REFUTED as a placement/panel finding.
- Outline-notch premise: not reproducible on the scratch board (no edge geometry near x=227.5/231.39 in
  the cited y-range).
- Reach-vs-route-length framing: conflates an already-PASS placement gate metric with routing-stage path
  length; no placement-impossibility shown.
- Recommendation (move JP401): violates the block's own fixed_anchors list and the audited R6/R7 PM
  ruling — not actionable at this stage.
- "Gate false positive" pre-emption: attachment_check.py already handles the shared-pad case correctly;
  nothing to pre-empt.

If the underlying worry is real (a congested corridor from heritage VSOLAR copper near J11.1 that could
make the router hunt), it should be re-raised at the routing stage as a routing note, citing actual
copper/component obstructions along a candidate path rather than a non-existent outline notch, and without
proposing to move a fixed anchor.

**Evidence commands:** pcbnew pad lookups (`FindFootprintByReference`, `GetPosition`) for J11.1/JP401.2/
JP400.2/TP401.1 on the scratch board; `GetDrawings()` filtered to `Edge_Cuts` layer, dumped in mm;
`grep` of `attachment_check.py` lines 1-320; `blocks.json` vsolar_injection entry; floorplan_v2.md L11
table row and audit rows R5/R6/R7/R9.

**Confidence:** 0.85 (own pcbnew geometry measurement + two independently-sourced documents, both
consistent; residual uncertainty only on whether a component-level, not outline-level, corridor argument
could still motivate a routing-stage note).
