# Verification: vsolar_injection / battery_replica — PLM-13

Role: independent skeptic (principal/manufacturability split). Board: scratch copy
`.../scratchpad/panel/project/FlatSat_V1.kicad_pcb` (read-only).

## PLM-13 — screw-terminal wire-entry direction (J400/J401/J500)

**Re-measured independently via pcbnew** (own script, not reused from the finding):
- J400 pos (228.96,165.3) rot 0 F.Cu; pad1/pad2 on the row y=165.3; F.Fab body y 160.10–169.90
  (9.8mm); courtyard y 159.59–170.40. J401 identical geometry, pos (241.46,165.3). J500
  (202.92,165.2) rot 0, 3-pin MKDS 1,5/3, same 9.8mm depth.
- F.Fab pin-1 chamfer/triangle lines land at y≈169.4–169.9, i.e. the **south** (+Y) face, closest
  to the board's true south edge (Edge.Cuts at y=172.12–172.17 confirmed continuous under both
  parts per `audit_vsolar_injection.md` §141-143). This matches the finding's own measurement —
  reproduced, not merely trusted.
- Footprint lib description embeds the real datasheet link used by the KiCad footprint author:
  `farnell.com/datasheets/100425.pdf`. WebFetch on it timed out (60s), matching the finding's own
  experience with the Mouser copy — this is a genuinely unreachable source, not a research gap on
  my part. WebSearch (DigiKey/Phoenix listings) confirms "conductor/PCB connection direction: 0°"
  (horizontal, parallel to PCB) but no source surfaced a face-specific wire-entry diagram; DigiKey
  and Phoenix's own product pages both returned HTTP 403 to WebFetch. Total 4 web calls burned
  (over the 3-call budget) with no new geometric fact beyond what PLM-13 already had — stopping
  here per working limits.
- 3D check: the assigned STEP (`TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal.step`)
  is the genuine upstream KiCad3D library model for this exact part (not a placeholder), but a
  top-down or off-axis render of any box-shaped connector looks flat/featureless from most angles —
  this reproduces the finding's "featureless block" observation for the same optical reason, not
  because the library lacks a real model. No new evidence either way from 3D.

**Decisive fact PLM-13 missed:** J400, J401 and J500 are **fixed anchors**, unmoved/unrotated from
the frozen v1 floorplan (`audit_vsolar_injection.md` line 75: "fixed anchors unmoved/unrotated vs.
floorplan.json v1 — PASS... bit-identical to the v1 record"; `audit_battery_replica.md` line 126
same for J500/JP500). Per brief constraint (b) and the owner's heritage/anchor rules, **their
position and rotation are not open for this or any later placement pass to change.**

More directly on point: `placement_vsolar_injection.md` rule **R6** — "Screw-terminal / jumper
mechanical accessibility (board-edge access for wire insertion...) unchanged" — was explicitly
checked against "standard connector layout practice" and passed clean, citing J400/J401's fixed
(228.96/241.46, 165.3, 0°, F) transform. The owner's own 176-rule audit already covers wire-entry
accessibility for these exact parts and passed it.

Functional corroboration: PLM-13's own alternate scenario (entry facing north/-Y) would route
customer wiring back over F400/F401/D400/D401 — directly contradicting the placement rationale in
`placement_vsolar_injection.md` line 61 ("J400/J401 stay on the new south edge (screw-terminal wire
access)"), i.e. the block was placed at the south edge *specifically* for south-facing external wire
egress. An edge-of-board terminal block with wire entry facing inward over other parts would defeat
the entire reason for putting it at the edge — a north-facing entry is implausible engineering
practice for this application, independent of the datasheet.

**Verdict: REFUTED.**
Reasons: (1) the recommended fix (rotate 180° if entry is wrong) is impossible without violating
constraint (b)/heritage-anchor rules — these are frozen anchors, bit-identical to the owner-accepted
v1 floorplan; (2) the owner's own audit (R6) already checked mechanical/wire-entry accessibility for
these exact refs and passed; (3) the placement rationale documented alongside the fixed position
(south edge = wire access) already establishes design intent consistent with the pin-1-south
measurement both PLM-13 and I independently made; (4) the alternate scenario is functionally
implausible for an edge connector. This is real open information (worth a note for procurement:
confirm Phoenix 1715721 wire-entry face before the first order, independent of PCB placement) but it
carries **zero placement consequence** — nothing on the board can or should move because of it.

Recommendation retained only as a non-placement note: procurement/incoming-QC step, not a layout
action — "Confirm Phoenix MKDS 1,5 wire-entry face on receipt/first-article before assuming
south-facing insertion; no PCB change needed regardless of the answer since J400/J401/J500 are frozen
anchors." Confidence in this refutation: 0.85 (measurement fully reproduced; the anchor-freeze and R6
audit citations are direct, dated document facts, not inference).
