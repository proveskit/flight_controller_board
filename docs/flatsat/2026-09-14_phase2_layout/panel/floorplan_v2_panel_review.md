# FlatSat V1 — floorplan v2.2 panel review (pre-routing)

Chair: panel chair (Opus). Reviewers: principal_routability, principal_manufacturability,
junior_developer. Every finding independently verified by a skeptic; severities below are the
skeptic's unless stated.
Board reviewed: scratch copy of floorplan v2.2, commit `d56c9df` (branch `flatsat-v1`).
Nothing routed, nothing committed, live board untouched.

## Verdict

**fix-then-route.** The v2.2 placement is sound: of 218 new parts exactly **one** needs to move
(J701, rotated 180°). The other three blockers are not placement errors — two are owner rule
decisions (L11 via amendment, L11 stub-length exception) and one is a board-outline decision
(J12's plug envelope). All three must be settled before routing starts because they change
copper topology, not after. The extension turns out to have **three** usable signal layers over a
solid In1 GND plane (In2 is completely empty over the wing and strip), so routing has more
headroom than the brief assumed — the difficulty is concentrated inside the 12 mm attachment
band, where the budget is zero.

| | count |
|---|---|
| blockers | 4 |
| majors | 1 |
| minors | 9 |
| notes | 7 |
| refuted | 8 |
| total findings | 29 |

### Blockers — must be settled before routing starts

| id | refs | evidence | fix | owner |
|---|---|---|---|---|
| PLR-01 | J2, J9, J13 → U310/U312/U314 (9 nets) | Heritage B.Cu PAYLOAD_BATT (x 223.500–223.900) and DEPLOY1 (x 224.183–224.818) form a continuous wall y 84.8–129.9; inter-track gap **0.283 mm** vs **0.381 mm** needed for a 0.127 track at 0.127 clearance. Min-rule scan: 0 free bands at x = 223.5/224.0/224.5/225.0 over y 85–128. F.Cu control at x = 224.0: 43.0 mm free. | Owner amends L11: allow **one B.Cu→F.Cu via per net (9 total)** inside the attachment band west of the wall. Verify each via individually against F.Cu heritage copper — J9 SCL/SDA fit near x 222.2–223.3, J13.5/J13.6 need x 221.5–222.0 (F.Cu band at x = 222.8 stops at y = 122.8), J2 not yet measured. Update `fc_keepout.json` (via_keepout = flight core, not the band) and relax `attachment_check.py` to "≤ 1 via per stub, inside the band". If declined: drop F1/F3/F5, populate only J1/J6/J11. | rule / `face_column` |
| PLR-02 | J14.10, J14.12 → U315 (BATT_SDA, BATT_SCL) | Pads at (209.00, 123.20)/(209.00, 121.20); nearest Rev2 edge x = 227.5 → **18.50 mm** vs `attachment_check.py` ALLOWED_PADS cap **14.0 mm** for J14. J14 is heritage (L4), cannot move. The reviewer's proposed x = 211 south corridor is **not clear**: J19, J8, J15, R80, C53, C29, U8, D3 all intersect it between y 121 and 142.1. | Owner grants a named per-pad exception: J14 pins 10/12 → **20–22 mm** max stub (precedent: the existing 24 mm J7/J10/J20 row), recorded in floorplan_v2.md §2. Require a **hand-traced jogged path** (between J19/C53/R80/D3, or C29/U8/J8/J15) verified before the exception length is accepted. Also fix the stale "12 mm" figure in 00_pm_brief.md to match the code's 14 mm table. | rule / `battery_replica` |
| PLM-01 | J701 | Footprint courtyard is asymmetric: local −5.27 (pad side) / +4.15 (mating side). At rot 0 the **pad side** sits 1.246 mm from the north edge (y 47.579) and the mating slot faces the board interior. Flown reference J12 (same HRO part, FC Rev2) places the **shallow/non-pad** side 0.165 mm from its board edge — opposite sense. No USB-C plug can be inserted; the emulator has no other port. | **J701 → (275.000, 51.874) rot 180, F.Cu.** Mating face then lands 0.145 mm off the north edge, reproducing the flown J12 offset. New courtyard max y = 57.144 → 1.14 mm to R701/R702 courtyards (above the 0.5 mm floor). Destination window x 269.4–280.6 / y 46.6–57.3 measured empty. Re-verify D+/D−/CC1/CC2 pad assignment for R703/R704 and R701/R702 after the flip. | `bench_io_cable` |
| PLM-02 | J12 | J12 (B.Cu, rot −90, courtyard x 217.845–227.355) opens **+X into the new wing**. Edge.Cuts scan x 224–246 / y 54–136 found **zero** cutout — solid board from 227.5 to 296.44 across J12's full height. USB-C plug shell needs x 226.81–233.3; overmold ≤ 6.5 mm. Not a part collision — the PCB itself is the obstruction, so L3 (height rule) does not help. | Owner picks: **(a)** cut a relief slot through the wing at ≈ x 228.5–241 / y 72.0–85.2 (measured free of parts both sides), accepting the GND-plane split and stitching cost; or **(b)** record J12 as not-matable on FlatSat V1 in the build/ATP docs and drive the FC over J703/J702/J701. **Decide before routing** — (a) changes plane topology. | floorplan-level |

### Major — should change before routing

| id | refs | evidence | fix | owner |
|---|---|---|---|---|
| PLR-06 | U200.35, R601, R602, LED600, C209 | PYRO_INHIBIT_STATE = one 129.4 mm airwire, 50 crossings (worst single edge). 3V3_EMU: 34 pads, MST 223 mm, 105 crossings, driven by one west outlier R602.2 (157.5, 158.6). The strip's only continuous E–W corridor narrows to **2.25 mm** at x = 250 (TP401), 2.55 at x = 265, 3.09 at x = 220; a BenchPower 1.0 mm track needs 1.500 mm of it. In2 heritage pours all stop at x ≤ 231.14 / y ≤ 141.87 → In2 is **empty over the whole wing and strip**. | No part moves. **(1)** Pour 3V3_EMU on **In2 over x 265–296, y 86–112 only** (covers 24 of 34 pads), priority below GND; route its single west branch to R602.2 as one **0.5 mm In2 track** (indicator LED, not bench power) — i.e. take 3V3_EMU out of the blanket BenchPower width for that branch. **(2)** Route PYRO_INHIBIT_STATE on In2 in the same corridor. Leaves the 2.25 mm F.Cu north band free for the strip's local signals. **Do not** pour 3V3_EMU across the whole wing/strip — In2 is worth more as a routing layer. | routing / `strip_left_pyro_shunts` |

---

## Manufacturability scorecard (JLCPCB, 4-layer JLC04161H-7628, both sides assembled)

| item | JLC / datasheet figure | measured on v2.2 | verdict |
|---|---|---|---|
| copper-to-edge | ≥ 0.2 mm (4-layer std) | min pad copper to Edge.Cuts **0.915 mm** (C200); TP200/TP201 1.040, U202 1.015, C201 0.930, J701 1.771, J510 4.210, J400/J401 5.520, J500 5.620 | **PASS**, >4× margin |
| component-free edge band | ≥ 5 mm on two opposite edges preferred (JLC adds rails otherwise) | east 0.50 mm courtyard, north 1.23, south 1.43 — **no edge qualifies** | minor (PLM-03). Board is 153 × 125 mm, far above JLC's 70 × 70 mm single-board minimum, so not order-blocking. Flag the east edge on the order; do **not** move C200/C201/U202 (audited rules 19/20/29) |
| body/pad spacing vs pick-and-place | min IC pin spacing 0.35 mm; ~0.2 mm body-to-body | finest pitch U200 QFN-60 **0.40 mm**, U511 VQFN-24 0.50, Q510 DFN 0.65. Worst body gap 0.500 mm (L200–C217); worst pad-pad 0.520 mm (U200–C212) | **PASS** — the 29 sub-0.5 mm entries are *courtyard* gaps, not assembly gaps (PLM-10) |
| double-sided assembly | supported both tiers | 3 new bottom parts (U310/U312/U314, MSOP-8, ~1.1 mm), no new process class; nothing bottom-side under a top-side connector (only C310/C312/C314 above them) | **PASS** (PLM-12) |
| mounting-hole clearance | M3 pan head Ø 6.0 mm (ISO 7045) | nearest new part to a hole centre **6.67 mm** (TP701–H10); J4–H1 8.06, D15–H2 7.70; H11/H12 nothing within 3.5 mm | **PASS**, ≥ 3.6 mm spare |
| thermal / EP vias | via-in-pad tenting required for filled EPs | U200 EP footprint **byte-identical to flown FC U18** (9 × 0.6/0.25 sub-pads, 50 % paste) — heritage, leave alone. U511 EP 2.7 × 2.7 mm, no vias yet: 3×3 array of 0.4/0.2 at 0.9 mm pitch leaves 0.25 mm to EP edge. B.Cu clear ±3 mm (U511/Q500/Q501), ±4 mm (L510), ±2 mm (Q510) | **PASS with routing action** (PLM-11) |
| Extended-library / feeder count | — | 63 distinct LCSC codes; 67 Extended instances vs 121 Basic. 15 identical 1×02 2.54 mm headers split across **3** Extended SKUs (C492401 / C358684 / C124375) | minor (PLM-08): collapse to C492401 (1.22 M stock) → −2 Extended part types, −2 feeders, zero design change. Optional: C701 → Basic C15850 |
| CPL rotations | plugin `corrections.db`, 62 regexes | 22 of 40 new footprint families are first-use with **no** rotation rule (U511 VQFN-24, D400/D401 D_SMA, D600–602 SOT-323, U301 SOT-563, MKDS ×2, SW600, J703, fuses, R_0805/R_2010). Separately `^SOT-363` = 180 **mis-fires** on easyeda2kicad `SOT-363_L2.0-W1.3-P0.65-LS2.1-BR` (U510), which is already drawn in JLC orientation | minor/note (PLM-05, PLM-04) — CPL-stage, no board effect. Board angle of U510 is 0.0° and correct |
| fiducials | 3–4 × 1 mm copper / 2 mm mask, ≥ 3.35 mm clear | **none on the board**. Of 9 natural sites, (232.5, 50.5), (252.0, 140.0), (262.0, 50.0) and (262.0, 140.0) verified clear at 3.35 mm; the other five are occupied. FC heritage flew with no fiducials and a 0.4 mm QFN-60 | minor (PLM-09): reserve (232.5, 50.5) + (252.0, 140.0) now, add copper at stage 5 |
| USB-C edge offset | flown FC J12: 0.145 mm courtyard / 0.69 mm body to edge | **J701 reversed** (blocker PLM-01). J510 correct sense but 2.36 mm body recess vs J12's 0.64 — plugs still seat (6.5 mm shell) | J701 fix above; J510 **no change** (fixed anchor, no mating failure) — PLM-06 refuted |
| screw-terminal orientation | Phoenix MKDS 1,5/2-5.08, conductor direction 0° | J400/J401/J500 pin-1 silk triangle and F.Fab chamfer both on local +Y = the south board edge; body face 2.22 mm from edge, strip south of them free. Dimensional drawing unobtainable (403/timeout ×4) | note (PLM-13): all three are frozen anchors and audit R6 already passed wire access. Confirm entry face on first-article inspection only |
| courtyard gate coverage | gate reports "0 overlaps" | **SW703's F.CrtYd and B.CrtYd are empty** — the only one of the 218 new parts; real bbox x 244.000–256.950, y 64.000–70.950, nearest neighbours Q701/Q702 0.995 mm, Q703 1.000 mm (no actual overlap) | minor (PLM-07): add an F.CrtYd rect to the project-local footprint at x 243.75–257.20 / y 63.75–71.20, or make the gate fall back to bbox |

---

## Routing-complexity forecast

**Layer budget (measured, all 44 zones).** In1.Cu is a single GND polygon x 139.8–298.5 / y 45.1–174.5
covering the whole grown board — solid reference under U200 (x 267–280, y 88–101) and under the
entire 38.5 mm USB corridor (x 274–276, y 50–89). Keep it uncut in those two rectangles; put
stitching vias outside them. Every heritage In2 pour stops at the Rev2 outline (x ≤ 231.14,
y ≤ 141.87), so **In2 is completely empty over the wing and the strip**. F.Cu and B.Cu already
carry GND pours in the new area (wing x 232.0–295.5 / y 48.5–171.2 prio 1; strip x 144.3–232.0 /
y 143.0–171.2 prio 2). Net: the extension has **three** usable signal layers over a solid plane;
the 12 mm attachment band inside the flight section has **zero** (In1/In2 keyed out by
`fc_keepout.json` rule 3, F.Cu/B.Cu occupied by heritage pours and tracks). Be generous in the
extension, surgical in the band.

**Order of work.**
1. Settle PLR-01 (L11 via amendment) and PLR-02 (J14 stub-length exception) — both gate copper
   topology and neither is discoverable by the autorouter.
2. Hand-route all **37 L11 stubs** on the pad's own layer, then re-run `attachment_check.py`.
   Freerouting will not respect the band and its output gets pruned anyway.
3. Hand-route the **USB pair** end to end on F.Cu: two vias per net at J701 (Default class, no
   restriction — see refuted PLR-03), then straight down the 22.20 mm free channel east of J703
   at x ≈ 274.5/275.0 for the full 38.5 mm. Fix it. Skew today is 0.04 mm.
4. Hand-route the **U200 and U511 escapes** with 0.45/0.20 vias (see PLR-08), then fix them.
5. Only then release Freerouting on the remainder.

**Easy.** Face-column → core: 33 signal nets cross the x 266.4–268.9 gap and that column is free
of parts for 94 mm of y (only obstacle at x = 259 is R708, y 76.67–77.31); 33 tracks at 0.45 mm
pitch need 14.85 mm. Core → bench I/O: y = 100.5, 106.0 and 110.0 each free across the full
30.39 mm width. Strip BenchPower runs (J500 → Q500/Q501/U500 → JP602-607; J400/J401 → F400/F401 →
D400/D401 → JP400/JP401) have 4.06–15.42 mm free y-bands against the 1.50 mm a 1.0 mm track needs.

**Hard, and why.**
- **B.Cu behind J2/J9/J13** — a hard wall, zero free copper at minimum rules across 43 mm of y
  (PLR-01). Needs the rule amendment, then nine individually-verified vias.
- **U200's north side** is the congestion peak: the QSPI escape (pads 56–60, 0.520 mm annulus),
  the USB fan-in (pins 51/52 at 0.400 mm pitch) and the VREG_LX/AVDD loop share one edge, with
  C210/C212/C213 at 0.700–0.737 mm. Escape QSPI **laterally** through the 1.160 mm alley at
  x 273.165–274.325 and drop to In2. Keep the USB pair on F.Cu the whole way (In1 reference).
- **Ten of U200's 45 signal pins** have their destination on the opposite side of the package —
  TOP_SDA, TOP_SCL, CTL_USBBOOT, SWCLK, SWDIO, UART_TX, PYRO_INHIBIT_STATE, F5_SENSE, F1_SENSE,
  F4_SENSE. Drop them straight onto In2 and carry them under the package. **Do not rotate U200**:
  90° only improves 10 → 8 and costs the USB and QSPI placements.
- **J703's eight signals** all wrap the package (PLR-05, minor — J703 is a fixed anchor, it does
  not move). Add 3V3_EMU, EMU_UART_TX/RX, EMU_GPIO_SPARE0/1, FC_RESET, USBBOOT, WDT_DISABLE to
  the In2 population; keep their vias clear of the USB F.Cu corridor and off U200's QFN pads.
- **The two 129 mm west runs** (PYRO_INHIBIT_STATE, the 3V3_EMU/R602 branch) own the strip — put
  both on In2, not in the F.Cu north corridor whose narrowest point is 2.25 mm at x = 250 (PLR-06).
- **Escape vias**: the Default 0.8/0.4 via needs 1.054 mm of annulus and does **not** fit at U200
  (median 1.030, max 1.135) or anywhere at U511 (0.875–0.900). Add a local **0.45/0.20** via class
  for both rings (JLC floor is 0.25 pad / 0.15 drill; 0.20 drill under 0.45 pad costs more but is
  standard process, no HDI). 15 U200 pads (QSPI 57–60, 17–21, 29, 30, 46) at 0.520–0.541 mm take
  no in-line via at all — escape sideways into the 13 alleys of 0.890–1.160 mm first. Eight caps
  have no room for an 0.8/0.4 GND via: C204/C209/C212/C219 take 0.50 mm at 0.39 mm out; C213/C217
  take 0.60 mm; **C206 and C216 clear by only 0.130 mm** — put their GND vias in the E–W lane at
  y 100.2–100.8 instead (free across x 266.00–296.39). No track of any legal width passes between
  adjacent pads on either part (U200 gap 0.200, U511 0.250, vs 0.381 required) — escape is radial.

**Pour strategy.** 3V3_EMU on In2 over x 265–296 / y 86–112 only, below GND in priority (covers
24 of 34 pads, kills ~90 of 105 crossings). Leave the rest of In2 as the wing's N–S and the strip's
E–W signal layer. Keep the existing F.Cu/B.Cu GND pours and let signal routing carve them. **No new
pour anywhere inside the Rev2 outline.**

**Residual risk that cannot be retired before routing.** (a) `attachment_check.py` same-net false
positives on the VSOLAR stub at J11.1 and the six face stubs whose heritage traces leave the same
pads — expect a handful on first run; the shared-pad case is already exempted in code (lines
261-266), off-pad coincidences are not. (b) Whether the F.Cu band at x = 222.8 reaches J13.5/J13.6
(free only to y = 122.8 against pads at 123.80/125.30) once PLR-01 lands — that pair may need its
via ~1 mm further west.

---

## Bench usability

**What can be plugged at once.** Every daily-use bench connector is top-side — J701 (emulator
USB-C, after the PLM-01 fix), J510 (charger USB-C), J500/J400/J401 (screw terminals), J702 and J22
(SWD), J703 (ribbon). The one exception is **J12**, the FC's own laptop USB-C, on B.Cu — and it is
currently unmatable at all (PLM-02). Even with a relief slot, a fixture that lets a laptop into
J12 while everything else is plugged needs **open underside access**: the board cannot rest flat
on a solid plate. Document the standoff height in the bring-up guide (JD-05). Geometrically the
lane is fine: 16.16 mm clear from J12's mating face to the face_column west edge at x 243.495.

**Wrong-plug / wrong-shunt risk.**
- **J400 / J401** (VSOLAR_BENCH_A / _B) are the identical Phoenix MKDS 1×02, 12.500 mm pitch,
  **1.24 mm** of clear board between courtyards, unkeyed screw terminals — nothing mechanical
  stops a solar-sim wire going into the wrong channel. There *is* a component-free corridor
  ≈ y 156.5–159.0 / x 226–249 (between F400/F401 and the terminals) big enough for a 1.2 mm legend;
  below the pair there is only 1.725 mm to Edge.Cuts. Record the legend location now (JD-02).
- **JP400 (VSOLAR select) / JP510 (charger CHG OUT select)**: identical 1×02 headers, same y-row,
  **0.870 mm** apart, both far from their own blocks (19.5 mm and 15.9 mm). Already measured and
  accepted in the v2.2 audit; both are fixed anchors. Give each its **own** nearby label
  ("VSOLAR SEL", "CHG OUT") rather than a shared one in the 0.87 mm gap (JD-04, refuted as a
  placement finding, kept as an L8 instruction).

**Jumper and switch access.**
- **JP602–JP607** bench-mode shunt bank: 5.75–5.80 mm pitch, **3.11–3.16 mm body-to-body** (the
  2.17 mm figure was courtyard-to-courtyard and understated it). Workable with fingers,
  comfortable with fine pliers. No move (JD-03).
- **SW600** pyro SAFE/ARM slide switch: **2.91 mm** body clear to JP600/JP601 above (not the
  0.96 mm courtyard figure), ~1.4–1.6 mm to LED600/R602 below. Actuable with a shunt seated.
  No callout needed (JD-08, refuted).
- **SW701/SW702**: 1.82 mm to J702's courtyard, 1.97 mm to each other — workable. But the real
  nets are **SW701 = EMU_RUN (RUN/RESET)** and **SW702 = EMU_BOOTSEL_SW (BOOTSEL)**, the reverse
  of the review brief's guess. Label them that way at stage 6 (JD-07).

**Probe access.** All TestPoint_Pad_D1.5mm banks are on 3.5–4.0 mm pitch = **1.00–1.45 mm** clear
between courtyards (TP300–306, TP500–505, TP600–603, TP202/203). A 2.5 mm probe tip or a hook clip
is wider than that gap; on TP500–505 the neighbours are Dir_Chrg_In / VBAT_BENCH_N / B−. Use a fine
needle probe on these banks — procedure note, no board change (JD-06). Separately, **no test point
exists on any I²C net** (0 of 32 TPs touch an SCL/SDA net; TP300–306 are F0_PWR…F5_PWR/+3V3, not
I²C). That is a Phase-1 schematic decision, already closed, and no placement move can fix it — if
the owner wants I²C bring-up probes it is a schematic-revision item (JD-01).

**Legend room (L8).** Space exists everywhere it is needed, but two locations must be *reserved*
now rather than discovered at stage 6: the F400/F401→J400/J401 corridor for the VSOLAR A/B legend,
and per-header labels beside JP400 and JP510.

---

## All findings

Blockers PLR-01, PLR-02, PLM-01, PLM-02 and major PLR-06 are given in full in the summary tables
above and are not repeated here.

### Minors — fix at a later stage or accept

| id | refs | evidence | verdict | fix / stage |
|---|---|---|---|---|
| PLR-05 | J703, U200 (pins 19, 27, 28, 29, 32, 33) | J703 is the 2nd-worst crossing hot-spot (119 incidences, behind U200's 1019); all 8 of its signals originate on U200's south/east rows while J703 sits due north, adding ~20–25 mm each and cutting the QSPI escape. 5 of the top-25 worst airwires are J703 edges. | **downgraded** from major: J703 is a named fixed anchor of `bench_io_cable` ("do not move or rotate", identical across every placement round, part of the owner-accepted v2.2). A crossing count shows longer routing, not illegal routing. | Do not move. Routing-stage instruction: put all 8 J703 nets on In2 for their run to U200, vias clear of the USB F.Cu corridor and off U200's pads (no via-in-pad). Record in the routing brief, not in `placement_bench_io_cable.md`. |
| PLR-08 | U200, U511, C204, C206, C209, C212, C213, C216, C217, C219 | Default 0.8/0.4 via needs 1.054 mm annulus; U200 median 1.030 / max 1.135, U511 0.875–0.900 → does not fit. 15 U200 pads at 0.520–0.541 mm take no in-line via. C206/C216 clear an 0.8/0.4 GND via by only 0.130 mm. 13 alleys at 0.890–1.160 mm confirmed. | **downgraded** from major: the fix needs zero part moves, and the tight geometry is the direct consequence of PM-approved manufacturer-guideline cap placement (176/176 PASS). A 0.4/0.2 via (0.654 mm) fits every identified alley. | Routing stage: local 0.45/0.20 via class for the U200 and U511 escape rings; route the 15 tight pads sideways into the alleys before via-ing down; C206/C216 GND vias into the free y 100.2–100.8 lane. Budget JLC's small per-via premium. |
| PLM-03 | TP200, TP201, C200, C201, U202 | Pad copper to east Edge.Cuts: C200 0.915, C201 0.930, U202 1.015, TP200/TP201 1.040 mm. No edge has JLC's preferred 5 mm component-free band (east 0.50, north 1.23, south 1.43 courtyard). | **downgraded** from major: fab rule (0.2 mm) met with >4× margin; board is 153 × 125 mm, well above JLC's 70 × 70 single-board minimum, and edge rails are something JLC adds, not an order gate. Moving C200/C201/U202 would break audited rules 19/20 (≤ 2 mm to U202's VIN pad) and 29 (U202's anchor-move budget already spent). | Do not move C200/C201/U202. Fab-order note: flag the east edge as tight so JLC's DFM picks carrier handling / puts fiducials elsewhere. TP200/TP201 may be nudged if convenient. |
| PLM-05 | U511, D400, D401, D600–602, U301, J400, J401, J500, SW600, SW703, J703, F400, F401 | 22 of 40 new footprint families are first-use with no `corrections.db` rotation rule; the silent-and-expensive ones are U511 (VQFN-24 0.5 mm), D_SMA (D400/D401) and SOT-323 (D600–602) — whose neighbours SOT-353 and SOT-363 are both corrected by 180. | **downgraded** from major: rotation affects the CPL angle only; no XY, clearance, placement or routing consequence. | Stage 6 / CPL: walk the 22-family list in the JLC placement viewer before committing reels, starting U511, D400/D401, D600–602; record each fix as a `corrections.db` row. Note that `USB_C_...HRO_TYPE-C-31-M-12 = 0` was validated on **bottom-side** J12 — J701 and J510 are top-side and need their own check. |
| PLM-07 | SW703 | `easyeda2kicad:SW-TH_SHOU-HAN_SS12D10G4` has `OutlineCount() == 0` on both F.CrtYd and B.CrtYd — the only one of the 218 new parts (10 other empty-courtyard footprints exist but are all heritage at x < 211). Real bbox x 244.000–256.950 / y 64.000–70.950; nearest gaps Q701 0.995, Q702 0.995, Q703 1.000 mm — no actual overlap. | **confirmed** minor: no collision today, but the "courtyard overlaps = 0" hard gate is blind to the largest part in `bench_io_drivers` and stays blind through routing and any later nudge. | Add an F.CrtYd rectangle to the **project-local** copy of the footprint: x 243.75–257.20 / y 63.75–71.20 (body + 0.25 mm). Plain S-expression edit, no GUI, L4-safe. Optionally make the gate script fall back to real bbox when the courtyard is empty. |
| PLM-08 | J300, JP400, JP401, JP500, JP510, JP600–607, C701 | 15 mechanically identical 1×02 2.54 mm headers across 3 Extended SKUs: C492401 (J300/JP400/JP401), C358684 (JP500/JP510), C124375 (JP600–607). 63 distinct LCSC codes, 67 Extended instances. | **confirmed** minor: pure BOM/feeder, no placement consequence. | BOM stage: collapse to **C492401** (1.22 M stock) → −2 Extended part types, −2 feeders. Optional: C701 → Basic C15850 (X5R is fine for bench-side VBUS decoupling). Leave the 2010 43R, 5.08 mm terminals, BSS138, BAT54W and 0603 1% values alone — §10 already proves no Basic equivalent. |
| PLM-09 | board | No fiducials anywhere. Of 9 natural sites, **(232.5, 50.5), (252.0, 140.0), (262.0, 50.0) and (262.0, 140.0)** verified clear at the 3.35 mm keep-clear (the reviewer's claim that (252.0, 140.0) fails was wrong — it clears in both courtyard and full-bbox checks); the other five are occupied. FC heritage flew a 0.4 mm QFN-60 with none. | **downgraded** to minor: should, not must, but the top side is nearly full so sites must be reserved now. | Reserve (232.5, 50.5) and (252.0, 140.0) now; add 3 F.Cu fiducials (1 mm copper / 2 mm mask) at stage 5. (262.0, 50/140) are fallbacks — that N–S channel is the wing's widest routing corridor. Keep ≥ 3.35 mm from H11/H12 annular rings too. |
| JD-02 | J400, J401, J500 | J400/J401 identical Phoenix MKDS 1×02, 12.500 mm pitch, courtyard gap **1.24 mm**, unkeyed screw terminals on unrelated channels (VSOLAR_BENCH_A / _B). J500 is differentiated by width (16.34 vs 11.26 mm) and 9.7 mm distance. | **downgraded** from major: a component-free corridor ~3.3 mm tall spans the full width of the pair between F400/F401 (y ≈ 156.2) and the terminals (y 159.545) — a 1.2 mm legend fits there with margin. Below the pair there is genuinely no room (1.725 mm to Edge.Cuts). | No geometry change. Add an L8 sub-row to `detail/placement_vsolar_injection.md`: "VSOLAR A/B" + polarity legend goes at y ≈ 156.5–159.0 / x 226–249, **not** between the two bodies. Stage 6. |
| JD-03 | JP602–JP607 | 5.75–5.80 mm pitch; courtyard gaps 2.12–2.17 mm but **F.Fab body-to-body 3.11–3.16 mm** (courtyard carries ~0.5 mm/side margin). | **downgraded** from major: 3.1 mm clear between adjacent 2-pin headers is ordinary bench-shunt spacing — fingers adequate, fine pliers comfortable. | No move. One line in the bring-up/assembly doc noting the 3.1 mm spacing and preferring fine pliers/tweezers over thick-jaw pliers. |

### Notes — information, no action before routing

| id | refs | substance | verdict |
|---|---|---|---|
| PLR-04 | R703, R704, U200 pins 51/52, J701 | USB pair pitch is 0.500 mm at J701, **1.800 mm** at the series resistors, 0.400 mm at U200 — it fans out and back over ~5 mm. Net order preserved end to end (no crossing); straight-line skew 0.04 mm; corridor east of J703 is 22.20 mm wide. | **downgraded** from minor: an ordinary series-termination taper on a 12 Mbit/s full-speed pair. The proposed 0.80 mm resistor pitch would leave only 0.26 mm pad-edge gap against the 0.25 mm class minimum — a worse trade. **Do not move R703/R704.** |
| PLM-10 | L200, C217, U200, C212, U315, C315, U511 | The 29 sub-0.5 mm pairs are courtyard-to-courtyard. Real body gap worst case 0.500 mm (L200–C217); worst pad-to-pad 0.520 mm (U200–C212); U315–C315 courtyard 0.010 but body 0.774 / pad 1.090. Finest pitch 0.40 mm vs JLC's 0.35 mm minimum. | **confirmed**: section B.2 closes with no finding. Do not spend placement moves on the sub-0.5 mm courtyard list for manufacturability reasons — it is a routing-room list and the PM has ruled. |
| PLM-11 | U200, U511, Q500, Q501, Q510, L510 | U200's EP footprint is byte-identical to the flown FC U18 (74 pads, 9 via-in-pad) — heritage, L4-frozen. U511's EP is 2.7 × 2.7 mm with drill = 0.000 (no vias yet); a 3×3 array of 0.4/0.2 at 0.9 mm pitch leaves 0.25 mm to the EP edge. B.Cu clear ±3 mm (U511/Q500/Q501), ±4 mm (L510), ±2 mm (Q510). | **confirmed**: routing-stage action only — add the U511 EP array and spread Q500/Q501 drain copper on B.Cu; confirm JLC's via-in-pad plugging at that pitch. Leave U200 alone. |
| PLM-12 | U310, U312, U314, TP701, H1, H2, H10, H11, H12 | 3 new bottom parts add no process class; only C310/C312/C314 sit above them. Nearest new part to a hole centre **6.67 mm** (TP701–H10), J4–H1 8.06, D15–H2 7.70; H11/H12 nothing within 3.5 mm. | **confirmed**, and understated — the reviewer's 5.13/5.40/5.46 mm figures were stale; real values above. ≥ 3.6 mm spare against an M3 pan head. |
| JD-05 | J12 | J12 is the only B-side bench connector; all others are F-side. 16.16 mm clear from its mating face to the face_column west edge. | **confirmed** note; merged into blocker PLM-02. Document required underside access / fixture standoff in the bring-up guide. J12 is heritage-frozen. |
| JD-06 | TP300–306, TP500–505, TP600–603, TP202/203 | TestPoint_Pad_D1.5mm banks on 3.5–4.0 mm pitch → **1.00–1.45 mm** clear between courtyards, narrower than a hook clip or a 2.5 mm tip. On TP500–505 the neighbours are Dir_Chrg_In / VBAT_BENCH_N / B−. | **downgraded** to note: `placement_face0_reference.md` already reviewed and closed this row as optimal. Test-procedure line only: use a fine needle probe, not a hook/alligator clip, on these banks. |
| JD-07 | SW701, SW702, J702 | Pad-net dump: **SW701 = EMU_RUN**, **SW702 = EMU_BOOTSEL_SW** — the reverse of the review brief's guess. Courtyard gaps SW701/SW702→J702 1.82 mm, SW701→SW702 1.97 mm. J702 is a vertical top-entry JST SH, so it does not block side access. | **downgraded** to note: the wrong mapping exists only in the review checklist; `placement_bench_io_cable.md` already has it right, and no silkscreen text exists yet. Stage-6 legend: SW701 "RUN/RST", SW702 "BOOTSEL". |

---

## Refuted

| id | claim | why it does not stand |
|---|---|---|
| PLR-03 | J701's A6/B6–A7/B7 links violate the USB_EMU "no vias" rule | Pad geometry and the 0.200 mm gap are right, but the rule is misattributed. Per 00_pm_brief.md L5 the USB_EMU class is scoped to nets **EMU_USB_DP/EMU_USB_DM**, which exist only on the 1.938 mm R703/R704→U200 segment. J701's pads carry `Net-(J701-D+-PadA6)`/`Net-(J701-D--PadA7)` = Default class, no via restriction. The finding's own precedent — flown FC J12, same connector, routed with 0.80/0.40 vias — shows this is normal. Optionally clarify in L5 that the no-vias rule begins at R703/R704. |
| PLR-07 | VSOLAR must detour ~43 mm around a Rev2 outline notch; move JP401 | **The notch does not exist on this board.** Edge.Cuts in 55 < y < 172 contains only the heritage notch at x 143.34–155.5 and one straight line at x = 296.39 — nothing near x = 227.5/231.39. The 31.617 mm figure is the already-PASS L11 attachment-reach metric, not a routing length. JP401 is a fixed anchor of `vsolar_injection`, frozen bit-for-bit. The feared gate false positive is already handled: `attachment_check.py` lines 261-266 exempt a stub sharing its pad point with the heritage track ending there. |
| PLM-04 | `^SOT-363` rotation rule will rotate U510 by 180° | The rule and the name match are real (`^SOT-363\|180\|0\|0`; U510's footprint is `SOT-363_L2.0-W1.3-P0.65-LS2.1-BR`), but it only affects the **CPL export**, not the board — U510 sits at 0.0° and correct. CPL-stage item: add `^SOT-363_L2.0-W1.3-P0.65-LS2.1-BR\|0\|0\|0` (or anchor the generic rule to `^SOT-363$`) before generating the CPL, and check U510 in the JLC viewer on the first order. |
| PLM-06 | J510's receptacle sits 1.72 mm deeper than the flown J12 offset | Numbers reproduce (2.36 vs 0.64 mm), but J510 is a named fixed anchor of `charger_bq25886`, documented unmoved bit-for-bit across PM rounds 3–5, and the finding concedes plugs still seat (6.5 mm shell vs 2.36 mm recess). Margin preference, not a mating failure. Log as a stage-6+ watch item if the owner wants the margin banked. |
| PLM-13 | Screw-terminal wire-entry direction unverified; may need 180° rotation | J400/J401/J500 are frozen anchors bit-identical to v1 — the proposed rotation is not available under constraint (b). Audit R6 in `placement_vsolar_injection.md` already checks and passes board-edge wire access at the current transform, and the block rationale documents south-facing entry ("J400/J401 stay on the new south edge (screw-terminal wire access)"). Pin-1 silk triangle and F.Fab chamfer both sit on the south face. North-facing entry would route wiring back over F400/F401/D400/D401 — implausible. 4 external fetches (Farnell timeout, DigiKey/Phoenix 403) yielded nothing determinative. Confirm on first-article inspection. |
| JD-01 | No test point on any I²C bus net | Measurement reproduces exactly (0 of 32 TPs touch SCL/SDA; TP300–306 are F0_PWR…F5_PWR/+3V3). But the TP roster was fixed in Phase-1 schematic capture, already reviewed and closed (00_pm_brief.md S5), and **no move of any placed part can add a test point** — the finding's own fix needs a schematic-level part addition. Log for the next schematic revision (TestPoints on U300/U310–U316 pins 3/6, or 2 TPs on EMU_SCL/EMU_SDA). |
| JD-04 | JP400/JP510 are 0.87 mm apart with no positional cue | The gap is right (4.500 mm pitch − 3.63 mm courtyard) but already measured and dispositioned in the accepted record: floorplan_v2.md and `audit_charger_bq25886.md` round 6 both re-derive 0.870 mm and classify it "comfortably clear, non-block-caused", 0 cross-block pairs below the 0.5 mm PM threshold. Both are fixed anchors in two accepted blocks. Courtyard gap, not copper clearance. Kept as an L8 label instruction (see Bench usability). |
| JD-08 | SW600 pinched with < 1 mm on both sides | Courtyard, not body. F.Fab: JP600/JP601 bottom edge 149.655 vs SW600 top 152.565 → **2.91 mm**, ~3× the cited figure; LED600/R602 side ~1.4–1.6 mm. Ample for a fingernail or small tool even with a shunt seated. No bring-up callout needed. |

---

*Chair note: the panel found one real part-placement error in 218 new parts. Three of the four
blockers are decisions the owner must take (two rule amendments, one outline choice) and none of
them can be discovered or worked around by the autorouter — which is why they belong here, before
routing, rather than in the routing stage.*
