# PROVES FlatSat V1 — Phase 2 floorplan (final)

**Date:** 2026-09-14 · **Stage:** 2 (floorplan) · **Decision by:** Opus judge, the one Opus call of this phase · **Status: awaiting owner review — no routing has started, nothing is committed.**

**Artifacts**

| File | What it is |
|---|---|
| `floorplan.json` | The floorplan of record: outline spec + 218 placements + 65 stitching points. Stage 3 starts from this file. |
| `floorplan_preview.kicad_pcb` (+ `.kicad_pro`, `.kicad_dru`) | The floorplan applied to a board copy, page set to A3. Nothing is routed. |
| `img/floorplan_top.png` / `img/floorplan_bottom.png` | 3D renders — the quickest way to see it. |
| `img/floorplan_top.pdf` / `img/floorplan_bottom.pdf` | Fab-style plots with courtyards, refdes readable at 100 %. |
| `img/floorplan_in1_gnd.pdf`, `img/floorplan_all_copper.pdf` | Grown In1 GND plane; all-copper overview. |

---

## 1. Owner summary — one page

### The board

```
   x=143.3                     x=227.5/231.4         x=296.4
 y ┌──────────────────────────────┬──────────────────────┐ y=47.6
47 │                              │  bench I/O cable     │
   │                              │  J701 USB-C  J702    │   ← new N edge
   │      FLIGHT SECTION          │  SWD  J703  SW701/2  │
   │      (Rev2, FROZEN,          ├──────┬───────────────┤
   │       byte-for-byte)         │ face │ emulator core │
   │                              │ atta-│  RP2350 U200  │   ← the 12 mm L3 lane
   │  U13  U30  U18  U3  U9 ...   │ chme-│  U201 U202    │     runs down x 231–244,
   │                              │ nt   │  Y200 L200    │     in front of every FC
   │  face connectors on the      │ col- │  27 decoupl.  │     face/USB/SWD connector
   │  right edge:  J1/J2  J6/J9   │ umn  ├───────────────┤
   │               J11/J13  J16   │ 7 ch │ Face-0 golden │
   │                              │ TCA- │ reference     │
   │                              │ 4311A│ U301–U303 J300│
 y └──────────────────────────────┤      ├───────────────┤ y=142.1
142│ pyro EN/  │ shunt  │ BATT ch. │ VSOLAR    │ BQ25886  │
   │ SAFE      │ headers│ U315     │ injection │ charger  │
   │ D600-602  │ JP602- │          │ J400 J401 │ U511     │
   │ SW600 LED │ 607    ├──────────┤           │          │
   │           │ battery replica   │           │          │
   │           │ J500 U500 Q500/1  │           │ J510     │   ← new S edge
   └───────────┴───────────────────┴───────────┴──────────┘ y=172.1
```

**Outline:** `tools/pcb/outline_L1.json` **unmodified** — the PM-validated brief-L1 default. Board **153.05 × 124.56 mm, 184.1 cm²** (bbox x 143.29–296.44, y 47.51–172.17). Right wing 65 mm (x 231.4 → 296.4, full height), bottom strip 30 mm (y 142.1 → 172.1, full new width). ~107 cm² of new area for ~50 cm² of new footprints. Three new M3 holes H10–H12 at the new corners, 4 mm inset like H1/H2. 65 GND stitching vias.

### Block map

| Block | Parts | x (mm) | y (mm) | Size (mm) | Why there |
|---|---|---|---|---|---|
| bench I/O cable + buttons | 11 | 269.0–294.0 | 48.8–88.7 | 25 × 40 | **J701 USB-C flush with the new north edge** (1.2 mm); SWD, 2×5 bench header and the two buttons beside it |
| bench I/O FC-control drivers | 10 | 244.0–260.5 | 64.0–77.5 | 16 × 13 | Open-drain drivers for FC_RESET / USBBOOT / WDT_DISABLE, directly opposite **J16** |
| solar_emulation face column | 48 | 244.0–266.3 | 50.5–133.0 | 22 × 82 | The seven TCA4311A front-ends in FC-connector order, hugging the lane: **U316**(TOP)·**U313/U314**(F4/F5 @J1/J2)·**U300/U310**(F0/F1 @J6/J9)·**U311/U312**(F2/F3 @J11/J13). **U310/U312/U314 are on B.Cu**, the same layer as the bottom-side connectors J9/J13/J2 they tap |
| emulator core (RP2350) | 47 | 269.0–294.0 | 90.7–114.4 | 25 × 24 | Own pocket inboard of the bench I/O, over the solid grown In1 plane, one column away from every front-end it drives |
| Face-0 golden reference | 16 | 269.0–292.9 | 116.4–129.2 | 24 × 13 | Real TMP112 / VEML6031 / DRV2605L + coil header, next to their buffer U300 |
| pyro EN diodes / SAFE switch | 14 | 152.0–187.0 | 144.0–159.7 | 35 × 16 | Under **U6** and R100/R104 — the three EN taps |
| **shunt headers JP602–607** | 6 | 187.0–219.5 | 144.0–150.1 | 33 × 6 | **Each header sits directly under the connector it parallels** — J30, J10, J29, J7, J8, J15 left to right |
| battery replica + bench PSU | 21 | 188.5–222.9 | 152.4–170.7 | 34 × 18 | Under **J14**; **J500 screw terminal on the new south edge** (1.5 mm) |
| BATT emulation channel (U315) | 5 | 221.0–232.1 | 144.5–151.2 | 11 × 7 | Wing/strip junction, the closest reachable point to J14's BATT_SDA/SCL pins |
| VSOLAR injection A/B | 11 | 224.4–254.6 | 143.7–170.7 | 30 × 27 | **J400/J401 screw terminals on the new south edge** (1.4 mm); the JP400/JP401 tap jumpers stay high so the VSOLAR stub to the face connectors is short |
| BQ25886 bench charger | 29 | 255.5–293.0 | 143.5–170.2 | 38 × 27 | Right end of the strip per L2; **J510 USB-C on the new south edge** (1.9 mm); the four 1210 bulk caps ring U511 within 8.5 mm |

### Attachment map (brief L11) — headline numbers

Every net the new sheets share with the flight controller is picked up at one allowed pad and led straight out. **37 shared nets, all attached, none orphaned.**

| | max | median | total |
|---|---|---|---|
| FC pad → nearest new pad | **35.8 mm** | 26.4 mm | 959 mm |

- **All 12 face SDA/SCL: 27.5 – 35.8 mm** (target ≤ 40 mm) · all 7 face PWR: 25.2 – 25.7 mm
- **All 3 EN taps at U6: 19.4 / 22.5 / 22.9 mm** (target ≤ 30 mm)
- Six shunt headers: **11.1 – 22.5 mm**, four of six at 11.1–13.6 mm
- J14 → replica 25.4 mm; J14 → U315 BATT bus 26.4 / 31.9 mm; J16 → top-cap bus 27.5 / 30.2 mm
- USB pair `EMU_USB_DP`/`EMU_USB_DM`: **3.5 / 3.4 mm, matched to 0.1 mm** (L5 wants ≤ 1 mm)

Full table in §5.

### Checks (all run by me on a fresh board copy, not inherited)

| Check | Result |
|---|---|
| `heritage.py check --allow-zone-growth --allow-edge` | **0 violations** |
| `attachment_check.py` | **0 violations, 0 warnings** (65 new vias, none inside the flight section) |
| New parts outside the outline | **0 of 218** |
| Courtyard overlaps among new parts | **0** (real courtyard polygons) · new-vs-heritage: **0** |
| New parts intruding the Rev2 outline | **0** |
| kicad-cli DRC schematic parity | **11 items = exactly the §6 FC baseline** (+0 new) |
| kicad-cli DRC `courtyards_overlap` | 1 (+0 — the known Rev2 item) |
| L3 clear lane | **clear** in front of all of J1/J2, J6/J9, J11/J13, J16, J12/J22; lane depth 12.6 mm |
| RF keep-outs (U13→RF1, U30 8 mm) | clear — nearest new part is >45 mm away |

### Questions I would like answered before stage 3 starts

1. **Mounting holes H10–H12 sit 4 mm in from the new corners, exactly at the centre of each 4 mm corner fillet** (same convention as H1/H2), which leaves a uniform 0.8 mm copper-to-edge all round the corner. Is there a FlatSat baseplate standoff pattern they must match instead? If yes, give me the pitch — moving them outward is not possible (the pad would leave the board), only inward.
2. **Do you want the F1/F3/F5 support passives flipped to B.Cu too?** U310/U312/U314 are already on B.Cu so those three face buses reach J9/J13/J2 without a layer change, but their pull-ups and decoupling are still on F.Cu, so stage 4 will add one via per net inside the extension. Flipping ~18 more parts would make those three channels single-layer end to end.
3. **U315 (BATT channel) is at the wing/strip junction, not in the face column**, to get BATT_SDA/SCL down from 43 mm to 26/32 mm on the flight-bus side. The cost is that its emulator-side bus grows to ~71 mm. Confirm you want the flight-side bus short (my assumption: it is the one shared with the real FC I2C).
4. **Is 12.6 mm enough for the L3 lane?** The brief asks for 12 mm. Proposal 2 argued for ~18 mm for real cable dressing; that costs ~6 mm on every face-bus length. I kept 12.6 mm.
5. **J702 (SWD) and J703 (bench header) are top-entry connectors placed 5.8 mm and 21 mm inboard.** That is fine electrically and for a vertical cable. Say the word if you want them on the edge too.
6. **The pyro strip has deliberate empty space at x 152–187, y 161–170** reserved for the L8 legends ("HEATER INH", "INH_S1 ∥ J8", the three bench modes, "BENCH ONLY — NOT FOR FLIGHT"). Confirm that is the right place for the legend block.

---

## 2. Decision

**Winner: Proposal 3 — "Attachment-Column Floorplan".** Grafts taken from Proposals 1 and 2 as listed in §4.

The floorplan's whole job is stated in the owner's first standing instruction and in brief L11: *place every block within reach of its attachment pads*, because new copper may only touch the flight section as a short stub from a connector pad. That makes the attachment-reach table the primary scoreboard, and Proposal 3 wins it on the nets that matter most — the twelve face I²C lines, which are the highest-count, most timing-sensitive nets on the board and the ones that load the FC's own bus.

Proposal 3 is also the only proposal that noticed that **J2, J9 and J13 are bottom-side connectors** and put their buffers (U310, U312, U314) on B.Cu. That single decision removes six layer changes from the attachment stubs and is visible in `img/floorplan_bottom.png`: three lone SOT-packages on the back of the wing, each facing its connector.

Proposal 1 is a close, competent second with a better bench-I/O edge and shorter EN taps — both of which I grafted. Proposal 2 optimised bench usability at a cost the brief does not permit: its face buses run 57–79 mm, roughly double the ≤ 40 mm bar, on a board grown by 47 cm².

### Scores (0–10)

| Axis | P1 West-Edge | P2 Bench-first | **P3 Attachment-Column** | Synthesis |
|---|---|---|---|---|
| Brief compliance (L1–L3, L6, L8, L11, keep-outs, lanes) | 8 | 3 | **9** | 9.5 |
| Routability (face buses, EN taps, replica, USB pair) | 7 | 3 | **9** | 9.5 |
| Bench usability (edge access, legend room) | 7 | 9 | **4** | 8.5 |
| EMC / ground (emulator over plane, 3 A strip paths) | 7 | 5 | **8** | 9 |
| Manufacturability (courtyards, 1210s at U511, outline) | 8 | 5 | **8** | 9 |
| **Overall** | **7.4** | **4.4** | **7.9** | **9.1** |

### Why each score

**P1 — 7.4.** Validated outline, L2 order followed, 12.6 mm lane, 0 courtyard overlaps, the best bench-I/O edge of the three (J701/J703/J510/J500 all flush), the shortest EN taps (13.1/15.4/17.8 mm) and tidy 1210s around U511. Marked down because U310 (the F1 buffer at J9) is pushed a column east — F1_SDA/SCL land at 45–46 mm, over the ≤ 40 mm bar — VSOLAR runs 44 mm, and moving U315 into the strip stretches `EMU_BATT_SDA/SCL` to 112 mm. Its emulator core is a 12 × 52 mm ribbon along the east edge, an awkward shape for a buck loop and a crystal. Total new-internal net span 3546 mm.

**P2 — 4.4.** Best bench usability by a distance and the source of two good ideas. But: *(a)* the delivered `floorplan_proposal_2.json` has no `add_edges` key, so `outline.py` falls into its legacy closed-polygon mode and draws a chord from (143.343, 139.074) to (228.441, 47.579) — **a straight cut across the middle of the flight section**. On my run that produced 11 real heritage violations (F.Cu/B.Cu/In1 GND, In2 +3V3, RF_VCC and two F.Mask zones all refilling differently inside the Rev2 outline). Its own checks were run against a different spec file in its scratch directory, so the hand-back was never verified as delivered. *(b)* With the spec repaired the placement is clean (heritage 0, 0 overlaps, 0 outside) but the routing is not: max attachment reach 82.2 mm, median 62.2 mm, every face bus 57–79 mm. *(c)* It spends nearly the whole ±15 mm budget on both axes (168 × 140 mm, 151.5 cm² of new area) to get there, and interleaves the BQ25886 switcher with the R5460N replica.

**P3 — 7.9.** Best routability and brief compliance; lowest new-internal span (2827 mm); compact central emulator core; the B-side buffer insight. Marked down hard on bench usability: **every cable connector and screw terminal is buried inboard** — J701 USB-C 10.4 mm from the nearest edge, J510 18.7 mm, J500/J400/J401 17 mm. A USB-C plug physically cannot mate with a receptacle 10 mm inside the board. Its USB pair is also mismatched by 20 mm (R703 25.3 mm from U200, R704 4.7 mm), which fails L5's 1 mm length-match outright. Its shunt headers sit 3–33 mm west of the connectors they parallel, so the 3 A paths wander. All three are placement-local and were grafted away.

### A correction to all three hand-backs

All three proposals reported **"4 pre-existing heritage zone-fill violations"** from `outline.py` and recommended a PM/tool investigation. **They do not exist.** My control run — `outline_L1.json` applied to a fresh copy of the live board with an empty placement — gives `heritage check: 0 violation(s)` and `attachment check: 0 violations, 0 warnings`. `heritage.py` was modified at 12:43 and `attachment_check.py` at 13:28 today; proposals 1 and 3 were written at 12:09–12:16, i.e. against the older tool. The tool was fixed under them mid-flight. No outline-stage investigation is needed and the risk can be struck from all three reports.

Similarly, the large blocks of DRC violations proposal 2 attributed to a "scratch-copy DRC environment artifact" were real but self-inflicted: `kicad-cli pcb drc` on a bare `.kicad_pcb` with no sibling `.kicad_pro` falls back to KiCad's factory default rules (0.2 mm track / 0.5 mm via / 0.3 mm hole / 0.5 mm edge), which is exactly what their reports quote. Run against a directory holding the board *and* its `.kicad_pro`/`.kicad_dru`/`.kicad_sch`, the project's real rules apply and those categories are all zero — see §6. Their diagnosis was right; the fix is one directory, not a toolchain change.

---

## 3. What the floorplan does (design notes)

**The wing is two columns.** The west column (x 244–266) is the *attachment column*: everything that touches an FC net sits here, ordered top-to-bottom to match the FC's own connector order, so every stub is a short horizontal run across the lane. The east column (x 269–294) is the *core column*: the RP2350, its flash, LDO, crystal, buck and 27 decoupling caps, plus the Face-0 golden reference — none of which touches an FC net at all (GND only). This separates the one switching node and the one 150 MHz part on the new area from every analog and I²C attachment, and it means the noisy column never has to cross the lane.

**The 12 mm L3 lane is real, not nominal.** The westmost new part anywhere on the wing is Q703 at x = 244.0, i.e. 12.6 mm clear of the new edge line at x = 231.4 — and in front of J1/J2, J6/J9 and J11/J13 the FC's own edge is inset to x = 227.5, so the mating clearance there is 16.5 mm. A real face board, the antenna cable, or the FC's own USB/SWD can still be plugged in.

**The strip is two rows.** The upper row (y 144–150) is everything that must reach a bottom-edge FC connector: the pyro EN diodes and SAFE switch under U6/R100, then the six shunt headers each directly under the connector it parallels, then the BATT channel at the wing junction. The lower row (y 152–171) is the battery replica, with J500 on the south edge under J14. That ordering is the opposite of Proposal 1's and it is deliberate: the shunt headers carry up to 3 A and parallel a connector pin pair, so they belong as close to that connector as the outline allows; the replica taps J14, whose pads are already 10.9 mm deep, so 8 mm more costs it nothing.

**Ground.** The In1 GND plane is grown over the whole new outline; F.Cu and B.Cu GND pours cover the wing (priority 1) and the strip (priority 2). The emulator core sits entirely over unbroken In1 copper. 65 stitching vias run the new perimeter at ~9 mm, along the old/new seam on both the right and bottom edges, and as a ring around the emulator core at ~7 mm. In2 gets no new pours, per L6.

**Nothing new enters the flight section.** `attachment_check.py` reports 0 stub chains and 0 violations; no stitching via lies inside the Rev2 outline; no new footprint's bounding box touches it.

---

## 4. Grafts taken from the other two proposals

| # | From | Graft | Measured effect |
|---|---|---|---|
| G1 | P1 + P2 | **J701 USB-C to the new north edge** (courtyard 1.2 mm from the edge) | was 10.4 mm inboard — unmateable |
| G2 | P1 + P2 | **J510 charger USB-C to the new south edge** (1.9 mm) | was 18.7 mm inboard |
| G3 | P1 + P2 | **J500 bench-PSU terminal to the south edge under J14** (1.5 mm) | was 17.0 mm inboard |
| G4 | P2 | **J400/J401 VSOLAR terminals to the south edge** (1.4 mm), with JP400/JP401 left high in the block | was 17.0 mm inboard; VSOLAR tap unchanged at 31.1 mm because the jumper, not the terminal, is the tap point |
| G5 | P1 | **R703/R704 repositioned as an adjacent matched pair** north of U200 | `EMU_USB_DP`/`DM` 25.3/4.7 mm → **3.5/3.4 mm, matched to 0.1 mm** (L5 needs ≤ 1 mm) |
| G6 | P1 | **Shunt headers JP602–607 x-aligned under J30/J10/J29/J7/J8/J15**, replica moved to the strip's lower row to make room | INHIB_1 32.8 → **11.1**, VBATT_SENSE 37.0 → **11.1**, B- 22.9 → **11.4**, INHIB_2 30.1 → **22.5**, IN_RBF 13.8 → 11.1, VBUSP 15.1 → 13.6 |
| G7 | P1 | **U315 BATT channel to the wing/strip junction** | BATT_SDA 42.7 → **26.4**, BATT_SCL 44.7 → **31.9** |
| G8 | P1 | **Q701/Q702 moved west** to the driver row opposite J16 | FC_RESET 36.7 → **27.6**, USBBOOT 43.6 → **34.5** |
| G9 | P2 | **Stitching vias filtered against the placement** — P3's 63 points included 22 landing inside a footprint, 5 on the board edge and 2 within 0.1 mm of each other | regenerated: 65 points, **0 footprint collisions, 0 copper-edge-clearance errors, 0 hole-to-hole errors** (these were 5 + 2 real DRC errors before the fix) |
| — | P2 | **Considered and rejected:** 7 mm mounting-hole inset. P2's inset clears `apply_placement.py`'s bounding-box check, but at the validated 4 mm inset the hole centre *is* the fillet arc centre, giving a uniform 0.8 mm copper-to-edge — the geometric optimum. The flag is a checker artifact (see §6). Kept at 4 mm, matching H1/H2. |
| — | P2 | **Considered and rejected:** growing the wing/strip by the full ±15 mm. Buys ~6 mm more lane and edge room; costs 15–25 mm on every face bus and 47 cm² of board. |

**Kept from Proposal 3 unchanged:** the outline (validated `outline_L1.json`), the two-column wing, the seven front-ends in FC-connector order in the attachment column, U310/U312/U314 on B.Cu, the emulator core pocket, the Face-0 reference stack, the pyro EN/SAFE cluster under U6, and the strip's left-to-right block order.

---

## 5. Attachment map (brief L11) — net → pad → block

One stub per net, on the pad's own layer, from the pad listed to the block listed. Distances are pad-centre to pad-centre on the placed board; the portion inside the flight section is bounded by the pad depth (faces 3.8–3.9 mm, J8/J29/J30/J15 4.5 mm, J16 5.0 mm, J14 10.9 mm, U6 8–10 mm, J7/J10 20.5 mm) and stays inside L11's allowance in every case.

| Net | FC attachment pad | Pad layer | Consumed at | Block | Pad→pad (mm) |
|---|---|---|---|---|---|
| `+3V3` | J16.6 | THT | R370.1 | face column | 21.9 |
| `F0_PWR` | J6.4 | F.Cu | R300.1 | face column | 25.6 |
| `F0_SCL` | J6.5 | F.Cu | U300.3 | face column | 27.9 |
| `F0_SDA` | J6.6 | F.Cu | U300.6 | face column | 27.6 |
| `F1_PWR` | J9.4 | B.Cu | R314.1 | face column | 25.7 |
| `F1_SCL` | J9.5 | B.Cu | U310.3 | face column | 35.8 |
| `F1_SDA` | J9.6 | B.Cu | U310.6 | face column | 35.6 |
| `F2_PWR` | J11.4 | F.Cu | R320.1 | face column | 25.5 |
| `F2_SCL` | J11.5 | F.Cu | U311.3 | face column | 27.8 |
| `F2_SDA` | J11.6 | F.Cu | U311.6 | face column | 27.5 |
| `F3_PWR` | J13.4 | B.Cu | R333.1 | face column | 25.7 |
| `F3_SCL` | J13.5 | B.Cu | U312.3 | face column | 35.8 |
| `F3_SDA` | J13.6 | B.Cu | U312.6 | face column | 35.6 |
| `F4_PWR` | J1.4 | F.Cu | R340.1 | face column | 25.2 |
| `F4_SCL` | J1.5 | F.Cu | U313.3 | face column | 27.8 |
| `F4_SDA` | J1.6 | F.Cu | U313.6 | face column | 27.5 |
| `F5_PWR` | J2.4 | B.Cu | R353.1 | face column | 25.3 |
| `F5_SCL` | J2.5 | B.Cu | U314.3 | face column | 35.8 |
| `F5_SDA` | J2.6 | B.Cu | U314.6 | face column | 35.5 |
| `SCL_Top` | J16.7 | THT | U316.3 | face column | 27.5 |
| `SDA_Top` | J16.5 | THT | U316.6 | face column | 30.2 |
| `BATT_SCL` | J14.12 | THT | U315.3 | BATT channel | 31.9 |
| `BATT_SDA` | J14.10 | THT | U315.6 | BATT channel | 26.4 |
| `FC_RESET` | J16.2 | THT | Q701.3 | bench I/O drivers | 27.6 |
| `USBBOOT` | J16.1 | THT | Q702.3 | bench I/O drivers | 34.5 |
| `WDT_DISABLE` | J16.9 | THT | SW703.1 | bench I/O drivers | 23.6 |
| `B-` | J15.1 | F.Cu | JP607.1 | shunt headers | 11.4 |
| `INHIB_1` | J29.2 | F.Cu | JP603.1 | shunt headers | 11.1 |
| `INHIB_2` | J10.3 | THT | JP605.1 | shunt headers | 22.5 |
| `IN_RBF` | J30.2 | F.Cu | JP606.1 | shunt headers | 11.1 |
| `VBATT_SENSE` | J8.2 | F.Cu | JP604.1 | shunt headers | 11.1 |
| `VBUSP` | J30.1 | F.Cu | JP606.2 | shunt headers | 13.6 |
| `Deploy1_EN` | U6.3 | B.Cu | D600.1 | pyro EN/SAFE | 19.4 |
| `Deploy2_EN` | U6.6 | B.Cu | TP602.1 | pyro EN/SAFE | 22.5 |
| `Heater_EN` | U6.5 | B.Cu | TP601.1 | pyro EN/SAFE | 22.9 |
| `Dir_Chrg_In` | J14.1 | THT | TP500.1 | battery replica | 25.4 |
| `VSOLAR` | J11.1 | F.Cu | TP401.1 | VSOLAR injection | 31.1 |

**37 nets · max 35.8 mm · median 26.4 mm · total 959 mm.** `GND` is not in the table: it reaches the extension only through the grown In1 plane and the new pours, with no new via inside the flight section (L11).

R104.1 / R100.1 remain available as alternative Deploy1_EN / Heater_EN taps; the placement reaches all three EN nets at U6's own IN pads, which are closer.

---

## 6. Evidence — every check, run by me on a fresh copy

Pipeline: `base = cp FlatSat_V1.kicad_pcb` → `outline.py --spec floorplan.json` → `apply_placement.py --placement floorplan.json` → page A3 → checks.

```
$ outline.py --board base.kicad_pcb --out final_outline.kicad_pcb --spec floorplan.json
Edge.Cuts items removed: 11
Edge.Cuts items added: 7
In1 GND zones grown (rect): 1
heritage zones clipped to the Rev2 outline: 40
new GND pours: 4
mounting holes added: 3 (H10..)
stitching vias added: 65
saved final_outline.kicad_pcb new bbox x 143.29..296.44 y 47.51..172.17

$ apply_placement.py --board final_outline.kicad_pcb --placement floorplan.json --out final_placed.kicad_pcb
applied 218; refused (heritage) []; missing refs []
footprints not fully inside the outline: 8: ['H10', 'H11', 'H12', 'J21', 'J24', 'J4', 'U13', 'U30']
```

```
$ heritage.py check tools/baseline/heritage_rev2.json floorplan_preview.kicad_pcb --allow-zone-growth --allow-edge
note: bbox before [143.2916, 47.5137, 231.3932, 142.1248] after [143.2916, 47.5137, 296.44, 172.17]
note: new items: footprints +221, tracks/vias +65, zones +4
heritage check: 0 violation(s)

$ attachment_check.py tools/baseline/heritage_rev2.json floorplan_preview.kicad_pcb
attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
```

```
$ kicad-cli pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones ...
$ drc_summary.py drc_final.json --baseline tools/baseline/drc_prelayout.json
section            sev      type                             base    now  delta
schematic_parity   warning  extra_footprint                     1      1     +0
schematic_parity   warning  footprint_symbol_mismatch           5      5     +0
schematic_parity   warning  missing_footprint                 199      5   -194
schematic_parity   warning  net_conflict                       36      0    -36
unconnected_items  error    unconnected_items                   0    383   +383
violations         error    clearance                           0      7     +7
violations         error    courtyards_overlap                  1      1     +0
violations         warning  footprint_type_mismatch             7      9     +2
violations         warning  isolated_copper                     4      4     +0
violations         warning  lib_footprint_issues                3     21    +18
total baseline 256, now 436
errors: 391  unconnected: 383  parity: 11
```

Reading that DRC:

- **Parity is 11 — exactly the brief §6 FC baseline** (H1/H2 no footprint field, R26/R27 BOM-exclude, U10 footprint-vs-symbol, TP9–TP13 no footprint, REF**/G*** extra). **Zero** parity items come from the 218 new placements. The 199 → 5 and 36 → 0 deltas are the sync landing, not a regression.
- **`unconnected_items` 383 is the expected floorplan-stage state** — nothing is routed yet. It goes to 0 in stage 4.
- **`courtyards_overlap` 1 (+0)** — the accepted Rev2 item (SW2/TP2) only. Independently confirmed with a real-courtyard-polygon scan: **0 overlaps among the 218 new parts and 0 new-vs-heritage**.
- **`clearance` 7 are all intra-footprint pad-to-pad** inside U301 (TMP112 DFN, 0.15 mm) and Q510 (U-DFN2020-6E, 0.19 mm). They are a property of the packages, not of where the parts sit, and they are exactly the class `FlatSat_V1.kicad_dru` already exempts for U7/U15/U8/U16 via `memberOfFootprint`. **Fix: add `U301` and `Q510` to that rule — two lines, stage 3 or 5.** No placement change can clear them.
- **`footprint_type_mismatch` +2** (U200 marked through-hole with SMD pads, U302 the reverse) is a schematic symbol attribute, not layout. Stage 6/7.
- **`lib_footprint_issues` +18** are the new footprints differing from their library copies — triage, not a defect.
- **`copper_edge_clearance`, `hole_to_hole`, `via_dangling` are all 0.** They were 5, 2 and 5 before graft G9; the stitching-via regeneration cleared them.

**The 8 "not fully inside the outline" items are all tool artifacts, and none of them is one of the 218 placements:**

- **J4, J21, J24, U13, U30** are frozen heritage footprints. They fail the same check on the completely unmodified live board — `apply_placement.py` tests all four corners of an axis-aligned bounding box against the non-convex Rev2 outline, and these five sit at the left-hand notch where a bbox corner falls outside the polygon while the part does not.
- **H10, H11, H12** are the mounting holes `outline.py` itself adds, not placements. Each sits at the centre of a 4 mm corner fillet, so its 3.075 mm-radius pad keeps a uniform **0.925 mm** clearance to the arc — but the bbox corner at 45° is 4.34 mm from the arc centre, i.e. 0.34 mm outside a 4 mm radius. The check is wrong for a circular pad; the geometry is right. (Verified directly: H10 bbox `[289.31, 48.51, 295.46, 54.66]`, arc centre `(292.39, 51.579)`, r = 4.0.)

My own measurement, which uses the real footprint bounding boxes of the new parts only: **`new_outside_outline: []`** — 0 of 218.

---

## 7. Remaining risks and handovers

1. **Nothing is routed.** 383 unconnected items is the correct state at this gate. Stage 4 owns them.
2. **U301 and Q510 need a `.kicad_dru` pad-to-pad exemption** (7 DRC clearance errors). One line each, following the existing `memberOfFootprint('U7')` pattern. Cannot be fixed by placement. → stage 3 or 5.
3. **F1/F3/F5 will need one via each inside the extension.** U310/U312/U314 are on B.Cu with their connectors, but their pull-ups and decoupling are on F.Cu. Legal (L11 only forbids vias inside the Rev2 outline) but worth a deliberate decision — see owner question 2.
4. **`3V3_EMU` spans 154 mm and `PYRO_INHIBIT_STATE` 132 mm.** Both cross from the wing to the strip. `3V3_EMU` is a 34-pad supply that should be poured or run wide, not autorouted as a net; `PYRO_INHIBIT_STATE` is a slow sense line. Flag for stage 4's netclass work.
5. **The 65 stitching vias are a starting set,** placed on the new perimeter, along the old/new seam and as a ring around the emulator, then filtered against the placement, the board edge, the Rev2 outline and mutual spacing. Pitch opens past 10 mm where the perimeter runs behind a part. Brief L6 and stage 3 own the authoritative pass.
6. **Rotations were not re-optimised.** Each part keeps the rotation `board_sync.py` staged it with (0° or 180°), except that the winner already oriented the B-side buffers. Screw-terminal and USB-C mating-face orientation reads correctly in the 3D render, but a GUI glance before fab is cheap. → stage 6.
7. **No silkscreen yet.** L8's legends, polarity marks and the "BENCH ONLY — NOT FOR FLIGHT" text are stage 6; the floorplan reserves whitespace for them at x 152–187, y 161–170 in the strip and along the wing's east margin.
8. **`apply_placement.py` exits non-zero on this floorplan** because of the 8 bbox artifacts in §6. If stage 3 gates on that exit code, it will need `--allow`-style handling or the checker needs to test courtyard polygons rather than bounding boxes. Worth fixing once in the tool.

---

## 8. Reproducing this

```bash
cd FlatSat_V1
PY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
F=../docs/flatsat/2026-09-14_phase2_layout/floorplan.json
cp FlatSat_V1.kicad_pcb /tmp/base.kicad_pcb
$PY tools/pcb/outline.py        --board /tmp/base.kicad_pcb --out /tmp/o.kicad_pcb --spec $F
$PY tools/pcb/apply_placement.py --board /tmp/o.kicad_pcb    --out /tmp/p.kicad_pcb --placement $F
$PY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json /tmp/p.kicad_pcb --allow-zone-growth --allow-edge
$PY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json /tmp/p.kicad_pcb
# for DRC, put the board in a directory with its .kicad_pro / .kicad_dru / .kicad_sch siblings,
# otherwise kicad-cli falls back to KiCad's factory default design rules (see §2).
```
