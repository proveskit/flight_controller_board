# Principal layout engineer — manufacturability + problematic placement, floorplan v2.2

Board under review: scratchpad/panel/project/FlatSat_V1.kicad_pcb (read-only scratch copy).
Role: JLCPCB fab + assembly. Sections B (manufacturability) and C (problematic placements).

## Calibration: which side of USB_C_Receptacle_HRO_TYPE-C-31-M-12 is the mating face

The KiCad footprint is ambiguous from silk alone, so I calibrated it against the **flown FC board**
(`FC_V5e_Production_Rev2.kicad_pcb`, J12, same HRO part, validated hardware):

- Footprint local geometry (`Connector_USB.pretty/USB_C_Receptacle_HRO_TYPE-C-31-M-12.kicad_mod`):
  F.Fab body `-4.47..4.47 x`, `-3.65..3.65 y` (8.94 x 7.30 mm); courtyard `-5.27..+4.15 y`.
  The 12 signal tails + the 4 shell pads sit on the **local -Y** side (pad row at local y = -4.045).
- FC Rev2 Edge.Cuts has a notch: vertical edge at **x = 227.50, y 62.50..127.74**, the band in front of
  the face connectors. J12 is at (223.160, 78.600) rot -90 on B.Cu; its courtyard spans x 217.845..227.355.
  The side facing that notch edge is the side **opposite the pads** = local **+Y**.
- Therefore **the mating opening is the local +Y face**, and the flown reference offset is
  body face 226.81 → edge 227.50 = **0.69 mm recess** (courtyard 0.145 mm from the edge).

Everything in §B.9 / PLM-01 below follows from that calibration.

## PLM-01 (BLOCKER) J701 is rotated 180 deg — the USB-C opening faces into the board

- `J701 (275.000, 54.120) rot 0, F.Cu`, courtyard y 48.805..58.315, north board edge y = 47.579.
- The courtyard side facing that edge is `local -5.27` = the **pad/tail** side (pad row at board
  y = 50.075 = local -4.045). On the flown FC, J12 presents the **opposite** (local +4.15) side to its
  board edge, 0.145 mm away. J701 is therefore mounted back-to-front: its mating slot points south,
  into the wing, and the 12 solder tails point at the board edge.
- Confirmed in a 3D close-up (`scratchpad/panel/principal_mfg/j701.png`): the silk U closes on the
  south side (footprint local +3.9), pads and shell pads sit against the north edge.
- **No USB-C plug can be inserted into J701 as placed.** The emulator's only USB port is dead.
- Recommendation: **J701 -> (275.000, 51.874) rot 180**. That puts the local +4.15 courtyard face at
  y = 47.724, i.e. the same 0.145 mm edge offset the FC's J12 was built and flown with (body face
  48.224, 0.645 mm recess). The destination window x 269.4..280.6 / y 46.6..57.3 is measured **empty**
  (pm3.py), and the new courtyard max y = 57.14 still clears R701/R702 at y ~= 59.5-60.5 by > 2.3 mm.
- Confidence 0.88. The only way this is not a defect is if the HRO drawing puts the tails on the
  mating face, which the FC's own edge geometry contradicts.

## PLM-02 (MAJOR) J12's USB-C mating envelope is destroyed by the new board outline

- On `FC_V5e_Production_Rev2` the board edge in the face-connector band is the notch
  **x = 227.50, y 62.50..127.74**; J12's courtyard ends at x = 227.355, 0.145 mm short of it, and the
  Pico-Lock courtyards (J1 227.52, J2 227.56) actually overhang it. The FC's face column was flush
  with a real board edge.
- On FlatSat that edge is **gone**: a scan of every Edge.Cuts shape with a point in x 225..245 finds
  nothing in y 55..135 (only the north-edge slot at x 223.6..229.2, y 50.6..54.1). The wing is solid
  board from x 227.5 to 296.44 across the whole connector band.
- J12 is a bottom-side receptacle, so the plug approaches under the board: shell centreline sits
  ~1.6 mm below the board's bottom face, and the USB-C plug overmold is up to 6.5 mm tall (3.25 mm
  half-height). Overmold top = 3.25 - 1.6 = **~1.65 mm above the board's bottom face**, i.e. 1.65 mm
  inside a 1.6 mm board. The shell fully inserted occupies x 226.8..233.3; the overmold then starts at
  x >= 233.3, which is solid wing.
- Bottom-side parts are *not* the obstruction (corridor x 227.3..240 / y 72.35..84.85 on B.Cu holds
  only the corner of J2) — the **board itself** is.
- Recommendation: either (a) cut a relief slot ~x 228.5..241 / y 72.0..85.2 through the wing (measured
  free of parts on both sides), accepting the plane/stitching cost, or (b) record J12 as
  not-matable on FlatSat V1 in the build documentation and route the FC's USB through J701/J703.
  This is an outline decision, so it needs the owner, not the layout stage.
- Confidence 0.72 (geometry certain; the 1.6 mm shell-centreline height is the typical figure for
  TYPE-C-31-M-12 rather than one I could re-read from the drawing this run).

## B.1 Component-to-board-edge (PLM-03, major)

Measured (pm2.py, real pad-corner to real Edge.Cuts geometry, arcs flattened):

| ref | courtyard-to-edge (facts.md) | **pad copper to edge** | edge |
|---|---|---|---|
| TP200 / TP201 | 0.50 | 1.040 | east x=296.39 |
| C200 | 0.61 | 0.915 | east |
| U202 | 0.72 | 1.015 | east |
| C201 | 0.73 | 0.930 | east |
| J701 | 1.23 | 1.771 | north y=47.58 |
| J510 | 1.89 | 4.210 | south y=172.12 |
| J400 / J401 / J500 | 1.43 | 5.52 / 5.52 / 5.62 | south |

Fab is fine: min copper-to-edge 0.915 mm vs the project's 0.2 mm rule and JLC's 0.2 mm 4-layer figure.
Assembly is the issue. JLC Standard PCBA takes a single board from 70x70 mm (ours is 153 x 125 mm),
so panelisation is not forced, but their assembly guidance still wants a >= 5 mm component-free band
on two opposite edges, otherwise edge rails get added and the break tabs land beside the parts.
**No edge of this board has 5 mm clear**: east 0.50 mm, north 1.23 mm, south 1.43 mm.
The cheapest fix is the east edge: TP200, TP201, C200, C201, U202 are all emulator-block parts with
slack to their west. Moving those five to x <= 291.4 (i.e. >= 5 mm clear of x = 296.39) makes the
125 mm east edge a clean rail/handling edge and leaves the north and south edges to the connectors
that must be there. TP200/TP201 are test points and cost nothing to move.
Confidence 0.6 on the 5 mm figure (my WebFetch of the JLC assembly page timed out; the number is the
one salvaged from the first run of this panel), 1.0 on the measurements.

## B.2 Component spacing — measured, and **not** an assembler problem (PLM-10, note)

The 29 sub-0.5 mm pairs are courtyard-to-courtyard. What the assembler sees is body and pad:

| pair | courtyard | **body (F.Fab)** | **pad-to-pad** |
|---|---|---|---|
| U315-C315 | 0.010 | 0.774 | 1.090 |
| U200-C212 / C213 | 0.035 | 0.855 | 0.520 / 0.565 |
| U200-C210 | 0.035 | 1.036 | 0.522 |
| L200-C217 | 0.050 | **0.500** | 0.535 |
| C220-U201 | 0.055 | 0.595 | 0.965 |
| U200-C206/207/209/216 | 0.055 | 0.875 | 0.540-0.585 |
| U202-C200 | 0.220 | 1.147 | 1.015 |

Worst case across the whole board: **body gap 0.500 mm (L200-C217), pad gap 0.520 mm (U200-C212)**.
Both are above the 0.2 mm body-to-body figure JLC's PCBA guidance uses and far above their quoted
0.35 mm minimum IC pin spacing. Finest pitch on the board is U200 at 0.40 mm (QFN-60) and U511 at
0.50 mm — both above 0.35 mm. Nozzle access, bridging and rework are all fine. **Nothing in B.2 is a
finding**; the sub-0.5 mm list is a routing-room list, and the PM already ruled on it.

## B.6 JLC rotation corrections — the real risk list (PLM-04 major, PLM-05 major)

**22 of the 40 new footprint families have no heritage instance on this board**, so their CPL rotation
has never been validated at JLC. I matched every one against the plugin's `corrections.db`
(62 regex rules, matched on the footprint name):

| footprint | refs | corrections.db rule |
|---|---|---|
| `easyeda2kicad:SOT-363_L2.0-W1.3-P0.65-LS2.1-BR` | U510 | **`^SOT-363` = +180 — MIS-FIRE** |
| `Package_DFN_QFN:Texas_RGE0024H_VQFN-24-1EP_4x4mm...` | U511 (BQ25886) | none |
| `Package_TO_SOT_SMD:SOT-323_SC-70` | D600-602 (BAT54W, polarised) | none |
| `Package_TO_SOT_SMD:SOT-563` | U301 | none |
| `easyeda2kicad:MSOP-8_L3.0-W3.0-P0.65-LS5.0-BL` | U300, U310-U316 (**8x TCA4311A**) | none (correct — EasyEDA) |
| `easyeda2kicad:U-DFN2020-6E...` / `SENSOR-SMD_VEML6031X00` / `SW-TH_...SS12D10G4` | Q510 / U302 / SW703 | none (correct) |
| `Diode_SMD:D_SMA` | D400, D401 (polarised) | none |
| `TerminalBlock_Phoenix_MKDS-...Horizontal` x2 | J400, J401, J500 | none |
| `SW_SPDT_Shouhan_MSK12C02`, `PinHeader_2x05`, `Fuse_2920`, `R_0805`, `R_2010` | SW600, J703, F400/401, R503/504, R304 | none |
| `SOIC-8_3.9x4.9mm_P1.27mm` / `TSSOP-10_3x3mm` / `SOT-23`,`-5`,`-6` | Q500/501, U303, Q701-703, U202, U500 | `^SOIC-`=270 / `^TSSOP-`=270 / `^SOT-23`=-90 (covered) |

**PLM-04 (major).** `corrections.db` rules are prefix regexes on the footprint *name*, so
`SOT-363_L2.0-W1.3-P0.65-LS2.1-BR` — an **easyeda2kicad** footprint, i.e. one already drawn in JLC's
own pin-1 convention and needing 0 — is caught by the `^SOT-363` = +180 rule written for the KiCad
library part. U510 (the charger's load switch, a 6-pin SOT-363) will be placed 180 deg out, which is
not a rotation AOI reliably rejects on a symmetric 6-pin body. Fix: add an explicit
`^SOT-363_L2.0-W1.3-P0.65-LS2.1-BR` = 0 row ahead of the generic rule, or rename/re-anchor the rule.
The same trap will bite any future `easyeda2kicad:SOIC-*`, `TSSOP-*` or `DFN-*` import.

**PLM-05 (major).** Of the families with no rule, two are ones a wrong rotation destroys silently:
**U511** (BQ25886, VQFN-24 0.5 mm pitch, the only 1.5 A charger, LCSC C2765094 Extended, 6,948 in
stock) and **D600-602 / D400-401** (polarised diodes; SOT-323 sits right beside SOT-353 and SOT-363,
both of which the table corrects by 180, so 0 is unlikely to be right for SOT-323 either).
CLAUDE.md rule 5 already says to check the JLC placement viewer on the first order of any footprint —
this list is what that check has to cover, and it should be done before the reels are committed.
Note too that the recorded `USB_C_Receptacle_HRO_TYPE-C-31-M-12 = 0` correction was validated on
**J12, a bottom-side instance**; J701/J510 are top-side and need their own look in the viewer.

## B.3 Both-sides assembly (note, PLM-12)

3 new bottom-side parts: U310 / U312 / U314, all `easyeda2kicad:MSOP-8` TCA4311A, courtyards
x 253.955..258.045, y 87.955..94.045 / 103.455..109.545 / 118.455..124.545. The FC already carries
137 bottom-side parts, so double-sided reflow is the existing process class — **no new cost, no new
process**. The only top-side parts above them are C314 / C310 / C312 (0402/0603 decoupling), not
connectors, so there is no standoff or clash issue; nothing on the bottom side is under a top-side
connector. Nothing changes about board flatness on standoffs (MSOP-8 body ~1.1 mm).

## B.5 Thermal pads (note, PLM-11)

- **U200** uses `RP2350_60QFN_minimal:RP2350-QFN-60-1EP_7x7_P0.4mm_EP3.4x3.4mm_ThermalVias`, which is
  **byte-identical to the FC's own U18** footprint (verified from the board). Its 9 via-in-pad
  0.25 mm-drill / 0.6 mm sub-pads and 4 x 1.2 mm paste windows (50% EP paste coverage) are flown
  hardware; unplugged via-in-pad under the EP is already JLC-validated on this exact part. No action.
- **U511** (Texas RGE0024H, EP 2.7 x 2.7 mm) has **no vias in the footprint** — they must be added at
  routing. A 3x3 array of the project's minimum 0.4/0.2 via at 0.9 mm pitch spans 2.25 mm, leaving
  0.22 mm to the EP edge, and B.Cu is **clear for +/-3 mm around U511**, so nothing lands under a
  neighbour. C510/C511/C512/C516 sit 0.28-0.30 mm outside the courtyard, well outside the EP.
- **Q500/Q501** (IRF7458, SOIC-8, 3 A): no exposed pad; drain-side copper spreading is free —
  B.Cu clear +/-3 mm around both. **L510**: B.Cu clear +/-4 mm. **Q510** (DFN2020-6E): clear +/-2 mm.
- Nothing in B.5 is a finding.

## B.7 Fiducials (PLM-09, minor)

The board has **no fiducials** (FC precedent: none, and the FC's own 0.4 mm-pitch QFN-60 U18 was
assembled successfully without them). JLC's guidance is 3 fiducials, 1 mm copper / 2 mm mask opening,
>= 3.35 mm clear of other copper. A coarse scan of nine natural corner/edge positions on F.Cu found
only **(232.5, 50.5)** with a clear 3.35 mm radius; (252.0, 140.0) is clear at 2.0 mm but not 3.35 mm,
and the other seven are occupied. So fiducials cannot just be dropped in at stage 5 — they need a
deliberate pass. The free N-S channel at x 262-266 is clear from y 48 to 142
(principal_prior_measurements, corridor scan), e.g. (262.0, 50.0) and (262.0, 140.0), but that channel
is also the wing's only wide routing corridor, so spending it on fiducials has a routing cost.
Recommendation: add 3 fiducials in stage 5, starting from (232.5, 50.5), and pick the other two after
the corridor budget is settled. Not a blocker — heritage says JLC copes without them.

## B.8 Mounting / standoffs (note, PLM-12)

Nearest part to any mounting hole centre: **TP701 5.13 mm from H10**, J4 5.40 mm from H1,
D15 5.46 mm from H2; **H11 (292.39, 168.12) and H12 (147.30, 168.12) have nothing within 3.5 mm**.
An ISO 7045 M3 pan head is 6.0 mm max diameter (3.0 mm radius) and a standard M3 hex standoff is
5-6 mm across corners, so every hole has >= 2.1 mm of margin beyond the screw head. `facts.md`'s
"0 parts within 3.5 mm" is confirmed and comfortable. No tall bottom-side part interferes with the
board sitting on standoffs (bottom side is the FC's existing 137 parts plus three MSOP-8s).

## B.9 USB-C edge offset (PLM-06, minor) — J510 vs the flown J12

| receptacle | body mating face | board edge | **recess** |
|---|---|---|---|
| J12 (FC, flown, B.Cu) | x = 226.81 | x = 227.50 | **0.69 mm** |
| J510 (new, F.Cu, rot 0) | y = 169.71 | y = 172.12 | **2.41 mm** (courtyard 1.87 mm) |
| J701 (new, F.Cu, rot 0) | faces the wrong way — see PLM-01 | | |

J510's orientation is **correct** (its non-pad face points at the south edge, same sense as J12), but
it sits 1.72 mm deeper than the offset the FC was built and flown with. A USB-C plug still seats — the
shell is ~6.5 mm long, so 2.41 mm of recess leaves the overmold standing proud of the edge rather than
bottoming on it — but plugs with a chamfered boot or a thick strain relief lose margin, and there is
no reason to give it away: the strip south of J510 (x 254..270, y 170.2..172.2) is **measured empty**.
Recommendation: **J510 -> (262.000, 167.780)** (+1.72 mm y), which reproduces J12's 0.145 mm
courtyard-to-edge offset exactly; min pad copper to edge then 2.49 mm, still 12x the 0.2 mm rule.
Confidence 0.6 — this is a margin improvement, not a defect.

## B.10 Screw terminals J400 / J401 / J500 (PLM-13, minor — verify before order)

Geometry as placed (all rot 0, F.Cu): pin row y = 165.3; footprint body local -5.2 (y = 160.10) to
+4.6 (y = 169.90); overall body 10.2 x 9.8 mm (footprint descr). South board edge y = 172.12.

- **Screws are top-access**: the F.Fab screw crosses are centred on the pads (local (0,0) and (5.08,0)),
  i.e. directly above the pins — reachable from above with nothing over them (verified in the 3D
  close-up `scratchpad/panel/principal_mfg/j400.png`; note the KiCad 3D model is a crude block, so it
  tells you nothing about the wire-entry face).
- **Wire entry face**: the footprint's pin-1 silk triangle (0, 4.72)-(+/-0.44, 5.33) and the F.Fab
  pin-1 chamfer (-2.04, 4.6)-(-2.54, 4.1) are both on the **local +Y** face, which on this board points
  **south, at the board edge** — 2.22 mm from it, with the strip y 169.90..172.12 measured free of any
  other part. If that reading is right, the orientation is correct and conductors leave over the south
  edge as intended.
- I could not confirm it against the Phoenix drawing this run (the datasheet WebFetch timed out at
  60 s; the web search returned the electrical data — 17.5 A, 1.5 mm^2, 5.08 mm pitch, "conductor/PCB
  connection direction 0 deg", solder pin 0.9 x 0.9 mm, hole 1.3 mm — but no depth dimensions).
- Recommendation: confirm the wire-entry face on the Phoenix 1715721 drawing before the first order.
  **If the entry face is the local -Y (5.2 mm) side instead, all three blocks are backwards** — wires
  would enter northward over F400/F401/D400/D401 — and they must be rotated 180 deg and re-seated so
  the entry face sits ~1.5 mm from y = 172.12. Confidence 0.5 on the orientation, 1.0 on the geometry.

## B.4 Extended parts / feeders (PLM-08, minor)

From `supply_chain_report.md`: the new area uses **63 distinct LCSC codes = 63 reels/feeders**,
188 of 218 refs carrying a number (28 test points by policy, R515 and SW600 unresolved);
**67 component instances are Extended-library, 121 Basic**. Cheap consolidation, in order of value:

1. **Three different SKUs for the same 1x02 2.54 mm header**, 15 parts total —
   C492401 (PZ254V-11-02P: J300, JP400, JP401), C358684 (MTP125-1102S1: JP500, JP510) and
   C124375 (B-2100S02P-A110: JP600-607). All three are Extended, all in stock in the 10^5-10^6 range,
   all mechanically interchangeable. Collapsing to one removes **2 Extended part types and 2 feeder
   slots** for zero design change.
2. **C701** (10 uF 0805 X7R, Extended C2182156, 82 k stock) has Basic X5R drop-ins at the same
   package — C15850 (25 V, 7.04 M) or C440198 (50 V, 1.53 M). It is bench-side VBUS decoupling;
   X5R is acceptable there. One fewer Extended line.
3. Leave the rest alone: §10 of the supply-chain report already proved no Basic equivalent exists for
   the 2010 43R, the 5.08 mm terminals, BSS138, BAT54W or the 0603 1% precision values.

Supply risk unchanged and out of my scope, but worth repeating to the owner: **Q500/Q501 (IRF7458,
C10879) has 57 units in stock = ~28 boards**, and U200's RP2350 draws on the same scarce SKU as the
flight board's U18.

## C. Problematic placements

**PLM-07 (minor) — SW703's footprint has no courtyard, so the "0 courtyard overlaps" gate never
checked it.** `easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4` is the **only** new footprint on the board
whose F.CrtYd polygon is empty (checked all 218). Its real body/pad bbox is
**x 244.000..256.950, y 64.000..70.950** — a 12.95 x 6.95 mm THT slide switch, the largest part in the
bench-IO block. Measured against real bboxes it does **not** overlap anything: Q702 0.97 mm,
Q703 0.98 mm and Q701 0.97 mm below it in y. So there is no actual collision — but the hard gate that
the owner is relying on ("courtyard overlaps 0") is blind to this part, and it will stay blind through
routing and any later nudge. Recommendation: add an F.CrtYd rectangle to the footprint (body + 0.25 mm)
in the project library, or carry SW703 in the gate script by bbox, before the gate is cited again.

**Checked and clean:**

- **Connector mating envelopes.** J510's plug envelope south of the board edge is empty
  (x 254..270, y 170.2..172.2 holds only J510). J400/J401/J500's south strip is empty. J702 (JST SH,
  vertical) and J703 (2x05, vertical) take their cables straight up; the free-channel scan shows the
  band above J703 (y 87.0..88.0) completely clear for 30.39 mm. The two failures are PLM-01 (J701) and
  PLM-02 (J12) above.
- **Header shunts (~6 mm tall) vs the L3 lane.** No header sits in the 12.00 mm lane; JP401 is at
  x = 226.2 (west of the lane), JP400 at x = 252.8 and TP401 at x = 248.8 (east of it). The lane rect
  of record is empty — the integrator's §5.3 item 5 measurement stands.
- **SW600 (pyro inhibit, safety-relevant) is operable.** Body x 152.000..160.950, y 151.140..157.140;
  the actuator travels along x and the x direction is clear (nearest obstruction TP600 at x = 161.93,
  0.98 mm, and it is a flat 1.5 mm test-point pad). The 6 mm-tall shunt headers JP600/JP601 are 0.98 mm
  **north** in y, and LED600/R600/R602 1.02 mm south — neither is in the actuator's travel or in the
  way of a fingertip coming straight down. Tight, but usable.
- **Probe access.** All 28 new test points are 1.5 mm round pads; the closest anything comes to one is
  TP303/TP304/TP305 at 0.414 mm from R304 (a 2010 resistor) — a spring probe or hook clip on a 1.5 mm
  pad has room. TP200/TP201 sit 0.50 mm from the east board edge, which helps probing, not hurts it.
- **U30 and the U13 -> RF1 corridor.** U30 is at (171.4, 88.9); the nearest new part is in the bottom
  strip at y >= 142, more than 53 mm away. Nothing new is within 8 mm of either. Clean by construction.
- **0402 between 1210s / polarised-part consistency.** No 0402 is boxed in by a large chip part: the
  only 2010 on the new area is R304, and its neighbours are 1.5 mm test-point pads and U302/U303 at
  0.40-0.46 mm. Polarised new parts (D400/D401 SMA, D600-602 SOT-323, C701, L_pol none) are a rotation
  question, not a placement one — see PLM-05.

## Scripts and artefacts

`scratchpad/panel/pm1.py` (connector facing vs Edge.Cuts), `pm2.py` (footprint families vs heritage,
pad-copper-to-edge), `pm3.py` (SW703 neighbours, J12 plug corridor, J701/J510 windows, B.Cu occupancy),
`pm4.py` (empty courtyards, fiducial candidates) + an inline `corrections.db` regex matcher.
Renders: `scratchpad/panel/principal_mfg/{south,back,back2,j400,j701,j510}.png`.
No file under `FlatSat_V1/` or `FC_V5e_Production_Rev2/` was written; `FC_V5e_Production_Rev2.kicad_pcb`
was read as text only. kicad-cli DRC was not run (drc_v22.json used).
