# Verification — battery_replica — PLR-02 (independent skeptic, routability)

## PLR-02 — J14.10/J14.12 (BATT_SDA/BATT_SCL) stub distance exceeds L11 cap

**Verdict: UPGRADED (major -> blocker). Core claim confirmed; two supporting details wrong; the
recommended reroute corridor is refuted by re-measurement.**

### Re-measured facts (pcbnew on the scratch board)
- J14 pad coords confirmed exactly as claimed: pin10 BATT_SDA (209.0, 123.2), pin12 BATT_SCL
  (209.0, 121.2), pin1 Dir_Chrg_In (207.0, 131.2), THT.
- Rev2 outline (00_pm_brief.md §2): right edge inset to x=227.5 for 62.5<y<127.7; bottom edge
  y=142.12. Distances: pin12->right edge 18.50 mm, pin12->bottom edge 20.92 mm; pin10->right edge
  18.50 mm, pin10->bottom edge 18.92 mm. Nearest edge for both pins is the **right** edge at 18.5 mm
  (finding said "nearest Rev2 edges x=227.5 and y=142.12" — correct that both are candidates, and
  right edge is in fact the shorter of the two, confirmed).

### Correction 1 — the cap is 14 mm, not 12 mm
Read `FlatSat_V1/tools/pcb/attachment_check.py` directly (not just the PM-brief's prose summary of
it). `ALLOWED_PADS` line: `(re.compile(r'^J(1|2|6|9|11|13|8|29|30|15|14|16|19)$'), None, 14.0)` — J14
is in the group with a **per-pad max-stub of 14.0 mm**, matching L11's prose figure exactly. The
docstring's usage example (`[--band 12] [--max-stub 12]`) and 00_pm_brief.md's own tool description
("stays within the 12 mm edge band, <= 12 mm") are both stale/misleading paraphrases of the CLI
argparse *default*, which the code itself overrides to 14.0 for J14 via `ALLOWED_PADS`. There is no
12-vs-14 mm inconsistency to reconcile — 14 mm is the one real number for J14. The finding's
"twice the L11 stub cap" and "exceed... the 12 mm stub cap" should read: exceeds the real 14 mm
cap by 4.5 mm (18.5/14 = 1.32x), not 2x.

### Correction 2 — "zero slack" for Dir_Chrg_In/Deploy2_EN/Heater_EN is wrong
Against the real 14 mm cap, Dir_Chrg_In (11.8 mm), Deploy2_EN (11.9 mm), Heater_EN (11.8 mm) have
**~2.1-2.2 mm of slack**, not "zero slack ... within 0.2 mm of the same cap." Drop this claim from
the writeup; it was measured against the wrong (12 mm) cap.

### Correction 3 (important) — the recommended F.Cu x=211 corridor is NOT clear
I re-ran the corridor check myself (bounding-box scan, not r10.py) over x 209-213, y 121-143 on the
live scratch board:
```
J19  211.1 124.8 218.6 133.4
J8   199.1 133.0 214.4 142.9
J15  207.9 133.7 223.6 142.9
R80  212.4 124.0 216.4 127.1
C53  212.6 121.0 215.1 125.9
C29  208.5 120.1 213.3 122.6
U8   203.5 116.5 213.7 121.6
D3   212.9 122.5 215.9 125.6
```
Every one of these heritage footprints' bounding boxes intersects the claimed-clear x=211 lane
somewhere between y=121 and y=142.1 — including J19, J8 and J15, which are themselves L11 allowed
attachment connectors for other nets (inhibit chain / battery). A straight stub south at x≈211
would run directly through/beside these parts, not through open board. r10.py's "unbroken free
band" result does not reproduce; either it used a different tool footprint clearance or scanned a
different x. The east route toward the right-edge wall (x 209-228, y 118-128) is even more
congested (J11, J13, U22, U24, R47/R49/R65, C49/C51/C55, the G*** logo footprint) and is not usable
either.

### Net effect
The core finding is right and, if anything, understated: BATT_SDA/BATT_SCL are tapped at fixed
heritage THT pads (L4, cannot move) that sit 18.5 mm from the nearest Rev2 edge against a real
14 mm attachment_check.py cap, and neither straight-line escape direction is geometrically clear —
a real stub would have to jog between J19/J8/J15 or C29/D3/R80/C53, adding length on top of the
18.5 mm floor and risking "touches no heritage track/via" violations along the way. This cannot be
fixed by repositioning battery_replica's own parts (J14 is heritage); it can only be fixed by an
owner-approved rule change (extend the ALLOWED_PADS per-pad max-stub for J14 pins 10/12, the same
mechanism already used for J7/J10/J20's 24 mm exception) plus a verified, hand-checked jogged path.
That combination — breaks a hard gate (L11), no placement-only fix exists, needs owner sign-off
before routing — is the definition of **blocker**, not major.

### Revised recommendation
1. Extend `attachment_check.py`'s `ALLOWED_PADS` for J14 pins 10 and 12 specifically (not the whole
   J14 group) to a 20-22 mm per-pad max-stub, precedented by the existing J7/J10/J20 24 mm
   exception — file this as an explicit, named exception in floorplan_v2.md §2/L11, not a silent
   band-width change.
2. Do not assume the x=211 corridor: before routing, hand-trace a jogged path from J14.10/12 that
   thread between J19/C53/R80 and D3, or between C29/U8 and J8/J15, keeping heritage courtyard
   clearance; confirm the actual jogged length fits inside whatever cap is granted in (1).
3. Fix the stale "12 mm" figure in 00_pm_brief.md's `attachment_check.py` row (it should say the
   real per-pad table, e.g. "14 mm for most J*, 24 mm for J7/J10/J20") so this kind of
   cap-vs-code mismatch isn't repeated by future reviewers.
4. `detail/placement_battery_replica.md` doesn't need a checklist-row change — J14 is outside the
   block's own envelope/checklist scope — but its "L11 attachment nets to J14" note (SDAIN/SCLIN
   row) should flag this distance so the routing-stage engineer isn't surprised.

**Confidence: 0.85** (pad coordinates, outline geometry and the attachment_check.py cap value are
directly re-measured/re-read; the jogged-path feasibility in recommendation 2 is not fully solved
here and should be treated as unverified until someone hand-traces it).
