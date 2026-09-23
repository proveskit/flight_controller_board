# Verify: emulator_core / principal-manufacturability panel, PLM-03

## PLM-03 — No 5mm JLC edge-rail band on east edge (TP200/TP201/C200/C201/U202)

**Verdict: DOWNGRADED (major -> minor)**

**Re-measurement (pcbnew, this session, script `manuf_reviewer/verify_plm03.py`):**
pad-copper to east Edge.Cuts (x=296.390): TP200 1.040, TP201 1.040, C200 0.915,
C201 0.930, U202 1.015 mm — matches the reported figures exactly. The
underlying observation is confirmed accurate.

**JLC source re-fetched** (jlcpcb.com/help/article/how-to-add-edge-rails-fiducials-for-pcb-assembly-order):
"Edge rails are added to increase the distance between components and the
board edge. The minimum width of edge rails should be at least 5 mm."
Fiducials: 1 mm copper pad, 2 mm mask opening, 3-4 marks, >=3.35 mm keepout.
The page does NOT say rails are mandatory for every order — it describes
rails as something JLC *adds* (an option/DFM response), and does not
condition it on board size. This board (153x125 mm) is well above JLC's
70x70 mm single-board Standard-PCBA minimum, so it does not need
panelization or rail-based handling; a DFM engineer can place fiducials
directly on open board copper and use a support fixture for pick-and-place,
which JLC does routinely for boards with tight edges. So the "no edge
qualifies -> panelisation forced" framing in the finding is not supported;
the correct framing is "this edge is not ideal for a clearance band," not
"the board cannot be assembled."

**Conflict with already-accepted v2.2 audit (176/176 PASS) — this is the
decisive point.** floorplan_v2.md audit rows for emulator_core:
- Rule 19/20: C200/C201 must stay <=2 mm from U202's VIN pad and C202/C203
  <=2 mm from VOUT pad (AP2112K generic layout note) — currently PASS at
  1.788/1.869 mm. Moving C200/C201 ~5 mm west while leaving U202 in place
  (or moving U202 with them) breaks this PASS.
- Rule 29: "Anchor ICs move <=3 mm" — U202 has ALREADY used its full anchor
  budget (0.000 mm net translation, rotation only, PASS). The recommendation
  asks to move U202 west to x<=291.4, i.e. ~2.2-3.8 mm further — this would
  push U202 past its audited anchor-move allowance and is not a placement
  change this panel can wave through without re-auditing rule 29.
- Rule 21 (test points reachable at a block edge): TP200/TP201 were
  deliberately audited PASS sitting near the block/east edge for probe
  access; moving them is fine (they are explicitly "free to move" per the
  finding), but moving them alone does not achieve a 5 mm band since
  C200/C201/U202 must stay put.

**blocks.json**: emulator_core has no fixed_anchors listed for these refs,
so there's no hard PM lock beyond the audited rules above — but those
audited rules are themselves the reason not to move C200/C201/U202.

**Owner-rule check**: not a heritage (L4), L11 attachment, or L3 lane
violation (all at x~293-295, outside the 231.39-243.39 lane). No PM
decision directly covers this, so it is not pre-decided — but it also
carries no routing consequence (pure component/edge proximity), so it
fails the panel's "blocker/major" bar of "cannot be assembled" or "routing
needs a detour."

**Revised recommendation**: Do not move C200, C201, or U202 — they are
protected by audited PASS rules 19/20/29. TP200/TP201 may still be nudged
if it helps handling, but that alone won't create a 5 mm band. Instead,
treat as a fab-order note: call out the east edge as tight on the JLC
order and let their DFM engineer choose fixture/carrier handling or place
fiducials elsewhere (J400/J401/J500 already clear 5.5+ mm on other edges
per the finding's own data) — no placement change required before routing.

**Confidence**: 0.75 (measurement solid; JLC mandatory-vs-optional
distinction still not perfectly documented, but the audit conflict alone
is enough to downgrade off "major").
