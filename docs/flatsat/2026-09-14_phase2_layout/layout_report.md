# PROVES FlatSat V1 — Phase 2 stage 6 (Silkscreen + docs + preview) report

**Date:** 2026-09-23 · **Stage:** 6 of 7 (brief §7) · **Owner:** finish agent (Sonnet, closure round 3) ·
**Input board:** `round3/layout_cleanup/deliver/FlatSat_V1.kicad_pcb` (closure round 2 output; unconnected 1,
heritage 0, attachment 0, DRC parity = the 11 §6 baseline items, zero clearance/short/hole errors) ·
**Delivered board:** `round3/layout_finish/deliver/FlatSat_V1.kicad_pcb` (project directory beside it:
`.kicad_pro`/`.kicad_dru`/schematics/`footprints.pretty`/`Backup_Footprints`/`symbols`/`fp-lib-table`/`sym-lib-table`).

**What this stage did, and only this:** added L8 silkscreen (jumper/header function legends, screw-terminal
polarity marks, the J500 bench-mode legend, the SW600 SAFE/ARMED legend, "BENCH ONLY — NOT FOR FLIGHT",
and reference-designator visibility) to the new area as free-standing `PCB_TEXT` items on `F.SilkS`, ran the
final gates, rendered the board, and produced a `kicad-cli`-only production preview. **No track, via, zone,
footprint position or heritage item was touched.** Every gate below reproduces closure round 2's numbers
exactly (drc_triage.md §11 has the full delta).

## 1. Final gates

| Gate | Result |
|---|---|
| `heritage.py check --allow-zone-growth --allow-edge` | **0 violations** |
| `heritage.py check --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2` | **0 violations** (3 band notes, unchanged from every prior round — see §6) |
| `attachment_check.py` | **0 violations, 0 warnings**, 3019 new tracks/vias, 37 stub chains |
| `kicad-cli pcb drc --severity-all --all-track-errors --schematic-parity --refill-zones` | errors **2**, unconnected **1**, parity **11** |
| DRC clearance / shorting_items / hole_clearance / hole_to_hole / copper_edge_clearance / track_width | **0 of each** |
| `kicad-cli pcb export stats` | 483 footprints (343 top / 140 bottom), 1058 vias, board bbox 153.05 × 124.56 mm |

```
section            sev      type                             base    now  delta
schematic_parity   warning  extra_footprint                     1      1     +0
schematic_parity   warning  footprint_symbol_mismatch           5      5     +0
schematic_parity   warning  missing_footprint                 199      5   -194
schematic_parity   warning  net_conflict                       36      0    -36
unconnected_items  error    unconnected_items                   0      1     +1
violations         error    courtyards_overlap                  1      1     +0
violations         warning  footprint_type_mismatch             7      8     +1
violations         warning  isolated_copper                     4      4     +0
violations         warning  lib_footprint_issues                3      3     +0
total baseline 256, now 28
errors: 2  unconnected: 1  parity: 11
```

Every one of the 28 items is a brief §6 pre-existing FC baseline item, or a build-stage footprint-attribute
item already triaged as accepted-with-reason (`drc_triage.md` §10.2/§10.3): the 1 `unconnected_items` +
1 `courtyards_overlap` = the 2 errors are **U6.1↔U6.29** (FC heritage, F13(e)) and the **SW2/TP2** courtyard
(Rev2 item 1). `footprint_type_mismatch` = 7 baseline + **U200** (the flown U18 footprint, accepted).
`isolated_copper`/`lib_footprint_issues` are byte-identical to the pre-layout baseline. Nothing attributable
to this stage's silkscreen work appears in the DRC report — **kicad-cli's DRC has no silk-vs-pad or
silk-vs-mask rule class**; the silkscreen tool's own collision search (every candidate checked against the
real KiCad bounding box of every pad on the board, inflated 0.20 mm, and of every label already placed) is
what stands in for that gate, and its results were confirmed by rendering (§4, §5).

### 1.1 Attachment stub list (net → pad → length)

37 stub chains, unchanged from closure round 2 — this stage added no copper inside the Rev2 outline.

| Net | Pad | Layer(s) | Inside (mm) | Via |
|---|---|---|---|---|
| +3V3 | J16.6 | F.Cu | 3.0 | — |
| B- | J15.1 | F.Cu | 7.3 | — |
| BATT_SCL | J14.12 | B/F.Cu | 23.9 | (216.28,129.62) |
| BATT_SDA | J14.10 | F.Cu | 19.3 | — |
| Deploy1_EN | U6.3 | B.Cu | 10.8 | — |
| Deploy2_EN | U6.6 | B/F.Cu | 15.1 | (169.98,130.90); TAP F12 |
| Dir_Chrg_In | J16.8 | F.Cu | 3.0 | — |
| F0_PWR | J6.4 | F.Cu | 7.3 | — |
| F0_SCL | J6.5 | F.Cu | 13.4 | TAP F12 |
| F0_SDA | J6.6 | F.Cu | 6.9 | — |
| F1_PWR | J9.4 | B/F.Cu | 6.4 | (222.28,107.93) |
| F1_SCL | J9.5 | B/F.Cu | 9.8 | (222.98,111.98) |
| F1_SDA | J9.6 | B/F.Cu | 12.7 | (222.98,118.58) |
| F2_PWR | J11.4 | F.Cu | 6.7 | — |
| F2_SCL | J11.5 | F.Cu | 6.8 | — |
| F2_SDA | J11.6 | F.Cu | 6.9 | — |
| F3_PWR | J13.4 | B/F.Cu | 7.1 | (222.58,122.43) |
| F3_SCL | J13.5 | B/F.Cu | 10.3 | (220.28,124.53) |
| F3_SDA | J13.6 | B/F.Cu | 10.7 | (222.98,121.72) |
| F4_PWR | J1.4 | F.Cu | 6.1 | — |
| F4_SCL | J1.5 | F.Cu | 6.5 | — |
| F4_SDA | J1.6 | F.Cu | 18.8 | TAP F12 |
| F5_PWR | J2.4 | B/F.Cu | 6.2 | (223.03,92.83) |
| F5_SCL | J2.5 | B/F.Cu | 6.3 | (223.03,94.88) |
| F5_SDA | J2.6 | B/F.Cu | 6.2 | (223.03,95.78) |
| FC_RESET | J16.2 | F.Cu | 3.0 | — |
| Heater_EN | R100.1 | B.Cu | 12.4 | — |
| IN_RBF | J29.1 | F.Cu | 7.3 | — |
| INHIB_1 | J8.1 | F.Cu | 7.5 | — |
| INHIB_2 | J10.3 | F.Cu | 18.6 | — |
| SCL_Top | J16.7 | F.Cu | 5.4 | — |
| SDA_Top | J16.5 | F.Cu | 5.4 | — |
| USBBOOT | J16.1 | B/F.Cu | 4.4 | (225.93,70.03) |
| VBATT_SENSE | J8.2 | F.Cu | 7.3 | — |
| VBUSP | J30.1 | F.Cu | 8.1 | — |
| VSOLAR | J9.2 | B/F.Cu | 7.1 | (222.73,106.38) |
| WDT_DISABLE | J16.9 | F.Cu | 5.3 | — |

All 13 layer-change vias are 0.46/0.20 mm (0.13 mm annular ring, the board minimum), inside the F6/F11/F14
allowance band, on none of them a heritage endpoint. The three `TAP` entries are the F12 T-junctions onto
the net's own heritage copper within 2.5 mm of the pad (`F0_SCL`, `F4_SDA`, `Deploy2_EN` — the three nets
with no compliant connector-pad path, per owner ruling F12).

## 2. What's on the board (outline, area, holes, zones, netclasses)

* **Outline:** the Rev2 88.1 × 94.6 mm flight-controller outline (unchanged) plus decision L1's L-shaped
  extension — a 65 mm-wide right wing (x 231.39→296.39, full height) and a 30 mm-tall bottom strip
  (y 142.12→172.12, full new width). Board bbox now **153.05 × 124.56 mm** (vs. the brief's nominal
  153×125 mm / 184 cm² — the difference is the corner radii). One extra cutout: the **J12 relief slot**
  (F8, x 228.0–243.0, y 71.5–85.7, r 1.5) so the FC's own bottom-side USB-C can still take a plug.
* **Mounting holes:** the flown H1/H2 (untouched) plus **H10/H11/H12**, new board-only M3 holes at the new
  corners (4 mm inset, F4), exempt from parity per §5's tool table.
* **Zones:** 41 heritage zones (unchanged fills inside the flight core, per §6 below) + **6 new zone
  objects** (wing/strip GND pours on F.Cu at priorities 1/2, a 3V3_EMU F.Cu pour, plus small closure pours)
  on top of the **grown** In1 GND plane (heritage zone, same uuid, polygon extended over the whole new
  area) and the reshaped/clipped heritage F.Cu/B.Cu/In2.Cu pours (clipped to the Rev2 outline inset 0.2 mm
  so no FC net pours into the extension, per L11/`outline.py`). Stitching vias every ≤10 mm along the new
  perimeter and around the emulator, plus a 5-point GND ring around the J12 relief slot (F8).
* **Netclasses** (`.kicad_pro` `net_settings`, applied by `netclasses.py`, visible in DRC — no width below
  class was flagged):

  | Class | Track | Clearance | Via | Nets |
  |---|---|---|---|---|
  | Default | 0.25 mm | 0.20 mm | 0.46/0.20 | I2C, senses, controls, most signals |
  | BenchPower | 1.00 mm | 0.25 mm | 0.80/0.40 | `VBAT_BENCH_N`, `VSOLAR_BENCH_A/B`, `VBUS_CHG`, `CHG_*`, `VBUS_EMU`, `MID_BENCH`, and the widened shunt/replica/injection taps |
  | FCPower | 1.00 mm | 0.20 mm | 0.80/0.40 | new tracks on `Dir_Chrg_In`, `B-`, `VBUSP`, `VBATT_SENSE`, `INHIB_1/2`, `IN_RBF`, `VSOLAR` |
  | EmuRail | 1.00 mm | 0.20 mm | 0.46/0.20 | `3V3_EMU` (F11(b) — moved out of BenchPower so it can escape the RP2350's 0.2 mm lands) |
  | USB_EMU | 0.25 mm | 0.20 mm | 0.60/0.30 | `EMU_USB_DP`/`EMU_USB_DM` (coupled pair) |

## 3. Placement summary (per block; full detail in `floorplan_v2.md` / `floorplan_v2_3.md`)

Floorplan v2.3 (owner-approved) placed all 218 new parts inside the outline with 0 courtyard overlaps and
the L3 12.6 mm lane kept clear in front of J1/J2/J6/J9/J11/J13/J16/J12/J22:

| Block | Refs (anchor) | Notes |
|---|---|---|
| Bench I/O | J701 (USB-C), J702 (SWD), SW701/702 (RUN/BOOTSEL), SW703 (WDT toggle), J703 (bench header) | Top-right of the wing; J701 rotated 180° per panel fix F5 so its mating face is 0.10 mm off the north edge |
| Emulator core | U200 (RP2350, EMU_FANOUT rule area per F13(a)), U201 (flash), U202, Y200, supporting passives | Centre of the wing; 9 via-in-pad GND thermal vias on U200's exposed pad, footprint heritage-identical to the FC's own U18 |
| Face front-ends | U310–U314 (TCA4311A, B.Cu), U315 (BATT), U316 (TOP) | Column facing J9/J11/J13/J1/J2/J14/J16 |
| Face-0 reference | U300–U303, J300, R304 | Opposite J6 |
| VSOLAR injection | J400/J401 (screw terminals), F400/F401, D400/D401, JP400/JP401 | Low on the wing, near the face connectors' VSOLAR pins |
| Pyro inhibit + shunts | JP600–JP607, SW600, LED600, D600–D602, R600–R602 | Under U6/J8/J29/J30, each shunt header within 15 mm of the connector it parallels |
| Battery replica | J500, JP500, JP510, Q500/Q501, U500 | New bottom edge, under J14 |
| BQ25886 charger | U511, J510 (USB-C), U510, L510, and support passives | Bottom-right, at the strip's right end |
| Mounting/relief | H10–H12, the J12 relief slot | Corners / wing |

## 4. Routing (attempt 2 → wing closure round 3 → cleanup)

* **New copper:** 2446 tracks + 573 vias = **3019 items** (matches `attachment_check.py`'s count exactly),
  5736.9 mm of new track. By netclass: Default 4620.9 mm (2515 items, mostly the emulator's I2C/signal
  fan-out), FCPower 459.1 mm (129), BenchPower 394.2 mm (190), EmuRail 259.4 mm (181), USB_EMU 3.3 mm (4).
* **Longest nets** (new track length): `+3V3` 296.4 mm, `3V3_EMU` 259.4 mm, `Dir_Chrg_In` 196.6 mm,
  `PYRO_INHIBIT_STATE` 178.4 mm, the five face `*_PWR` nets 77–104 mm each.
* **USB pair:** `EMU_USB_DP`/`EMU_USB_DM` — **1.644 mm each, 0 mm mismatch, 0 vias** (L5: "length-matched
  within 1 mm, no vias if avoidable" — met exactly; the pair is short because J701's D+/D− land directly
  on R703/R704 next to the connector).
* **Vias:** 1058 through vias total on the board; 133 × 0.46/0.20 (breakout/hop/GND stitching) + 12 ×
  0.40/0.20 inside EMU_FANOUT from the wing-closure round, plus the 13 × 0.46/0.20 L11 layer-change stub
  vias (§1.1). No new via inside the Rev2 outline anywhere else (`attachment_check.py`, every round).
* Full routing narrative, the Freerouting/exact-router recipe, and the three-round closure history
  (76 → 29 → 1 unconnected) are in `route_report.md`; DRC-class triage in `drc_triage.md` §§1–11.

## 5. Silkscreen (this stage, brief L8)

All items are free-standing `PCB_TEXT` on `F.SilkS` (or a footprint's own `Reference` field, made visible),
placed by a collision-searching script (`layout_finish/silkscreen.py`, kept in the scratch dir) that checks
every candidate against the real KiCad bounding box of every pad on the board (0.20 mm clearance) and of
every label already placed (0.15 mm clearance) before committing it — nothing new sits over a pad, and
nothing new sits on top of another new label. 48 items placed, 0 left unplaced after widening the search
(development history: two placements initially collided visually — `JP500`'s "DIV" landed on `J500`'s own
"B-" pin label, and the JP602–607 legends first sprawled into a crowded cluster near J500 with two-line
text — both found by rendering and fixed by reordering the placement passes and shortening the legends to
one line; see `drc_triage.md` §11 for the residual crowding note carried to the review).

* **Reference-designator visibility** — turned on for the 21 new "human-facing" footprints (connectors,
  jumpers, switches, mounting holes, ICs, the crystal) that routing-stage tooling left at the library
  default (hidden), matching this board's own convention of hiding bulk 0402/0603 R/C refdes and keeping
  connectors/jumpers/switches/ICs visible (verified against the heritage board: 25 of 262 heritage refdes
  are visible, all in those same categories, 0 of 194 heritage R/C/D are): `J300, J510, J701, J702, JP400,
  JP401, JP500, JP510, JP600–JP607, SW701, SW702, U200, U201, Y200`. Each was repositioned (small search
  around its own library-default offset) only when the default collided with a pad or a neighbour's label —
  9 of the 21 needed to move (up to ~9 mm) to clear a same-pitch neighbour (e.g. JP600/JP601 are 4.6 mm
  apart and share the same default offset).
* **Jumper / header function legends** (one compact line each, F.SilkS): `JP600` "HTR INH", `JP601`
  "PANEL SW", `JP602` "S1/J8", `JP603` "S2/J29", `JP604` "P1/J7", `JP605` "P2/J10", `JP606` "RBF", `JP607`
  "ISS", `JP400` "VSOLAR A", `JP401` "VSOLAR B", `JP500` "MID DIV", `JP510` "CHG OUT" — content from the
  Phase-1 jumper tables (`sheet_pyro_inhibit.md` §5, `sheet_solar_power_injection.md` §5,
  `sheet_battery_protection_replica.md` §5), abbreviated to fit the 4.6–11.6 mm header pitch (font down to
  0.6 mm / 0.11 mm stroke against the project's 1.0 mm default, per §1's density note).
* **Screw-terminal polarity:** `J500` "B+ / MID / B-" over its three pins (the pin-order callout
  `sheet_battery_protection_replica.md` §4 flagged as "needs a silkscreen callout at layout"); `J400`/`J401`
  "+" / "-" over their VSOLAR/GND pins.
* **J500 bench-mode legend** (from the sheet's own mode table): `MODE JP500 JP510` / `1 PSU  IN   OUT` /
  `2 USB  OUT  IN` / `3 OFF  OUT  OUT`.
* **SW600 SAFE/ARMED legend** (supply-chain ruling S2 — "silkscreen/legend 'SAFE ↔ ARMED' retained", the
  DIP-slide footprint itself only prints "on"): `CLOSED=SAFE` / `OPEN=ARMED`.
* **"BENCH ONLY — NOT FOR FLIGHT"** — two lines, 1.4 mm, on the open strip area near H12, the most visible
  clear silk region on the new area.
* **Pin-1 marks:** every new connector's library footprint already carries one (rectangular pad 1 vs. round
  on the THT headers/screw terminals; a drawn F.Silkscreen pin-1 arrow, same as heritage `J22`, on the
  SMD `J702`/`J701`/`J510` footprints) — confirmed by inspecting each footprint's pads and
  `GraphicalItems()`; no board-level addition was needed or made.

## 6. Heritage / zone-fill notes (unchanged from closure rounds; reproduced for completeness)

`heritage.py check --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2` reports the same **3 band
notes** this stage as every prior round (all "every piece of lost copper touches new copper" — accepted,
not violations): `+3V3` F.Cu band fill 291.0 → 273.7 mm² (−5.9 %, stub carve-out), `VSOLAR` In2.Cu band
fill 91.8 → 91.2 mm² (−0.6 %, stub carve-out), `B-` In2.Cu core fill 20.2 → 20.1 mm² (2.2 mm² lost, all
adjacent to new copper). Fills **inside** the flight core (old outline deflated by the 12 mm band) are
otherwise byte-identical to the refilled Rev2 board.

## 7. Renders

`docs/flatsat/2026-09-14_phase2_layout/img/`:

| File | What |
|---|---|
| `layout_final_top.pdf` / `_bottom.pdf` | F.Cu+F.SilkS+F.Mask+Edge.Cuts / B.Cu+B.SilkS+Edge.Cuts (mirrored), via `render.sh` |
| `layout_final_in1.pdf` / `_in2.pdf` | In1.Cu (GND plane) / In2.Cu (VSOLAR/B-/VBUSP/+3V3/RF_VCC/Dir_Chrg_In/3V3_EMU/PYRO_INHIBIT_STATE pours) |
| `layout_final_all_copper.pdf` | All four copper layers overlaid |
| `layout_final_stats.txt` | `kicad-cli pcb export stats` |
| `layout_final_top.png` / `_bottom.png` | `kicad-cli pcb render --side top/bottom --quality high --floor`, 2200×1500, photorealistic 3D — both read back and inspected during this stage; the wing/strip read cleanly, the J12 relief slot renders as an actual cutout, and the flight section is visibly untouched |

## 8. Production preview (`FlatSat_V1/jlcpcb/preview/`, `kicad-cli` only, clearly labelled — see its own `README.md`)

| Dir | Contents |
|---|---|
| `gerber/` | 11 layers (F/In1/In2/B Cu, F/B SilkS, F/B Mask, F/B Paste, Edge.Cuts) + job file, `--board-plot-params` (the board's own `pcbplotparams`, inherited byte-for-byte from `FC_V5e_Production_Rev2` — confirmed identical block in both `.kicad_pcb` files) |
| `drill/` | PTH/NPTH Excellon (mm, absolute origin) + PDF drill maps + text report |
| `pos/` | Both-side placement CSV (474 rows) |
| `bom/` | Grouped BOM, 182 lines, `Designator,Value,Footprint,LCSC,Datasheet,Quantity,DNP`, grouped by Value+Footprint+LCSC |

**Not** the order package — the JLCPCB-plugin GUI step (`project.db`, F8, Generate) is the owner's, per
brief §1 and `CLAUDE.md`'s pre-order procedure step 6; `jlcpcb/project.db` was not read or written.
BOM check: of 182 grouped lines, 81 are heritage-only (blank `LCSC` by repo convention — heritage LCSC
numbers live only in `project.db`, not the schematic field); of the 101 groups containing a Phase-2 part,
80 carry an LCSC number and the remaining 21 are exactly the new test points (`TP2xx`–`TP7xx`), which
S5 rules carry none, matching the FC's own `TP1`–`TP8` convention — **every new part that should have an
LCSC number has one**.

## 9. Open items for `pcb-flight-review` and the owner

1. **Via-in-pad (drc_triage.md §10.8):** 45 vias centred inside an SMD pad of their own net, 19 more on a
   pad edge, all from routing rounds 1–3 (none added or removed this stage). Needs an owner decision:
   order filled-and-capped (POFV) vias, or move them off-pad in a future revision.
2. **C207.2 GND** closed with an off-pad via per the owner's pair-unlock ruling (drc_triage.md §10.5) — the
   1V1_EMU return to U200's DVDD pin 23/C216 is now 6.65 mm / +2 vias longer as a result; flagged for the
   review, not disputed.
3. **EMU QSPI bus** (U200↔U201) is 30.0–46.0 mm with 3–8 vias per net, vs. the flown FC's own U18↔U11 bus
   at 8.3–12.8 mm / 0–2 vias (drc_triage.md §10.7) — not length-critical at bench QSPI clocks, flagged for
   the review to confirm.
4. **U6.1↔U6.29** unconnected item and the **SW2/TP2** courtyard overlap are both FC-baseline / heritage
   observations (brief §6, F13(e)) — reported, not fixed, per the brief's own instruction.
5. **Silkscreen density in the JP602/JP603/JP604/JP607 + JP500 + J500-mode-legend pocket** (§5, §1): every
   label is legible and clear of every pad and of every other label, but the pocket is busy at 1:1 scale
   (font down to 0.6 mm against the 1.0 mm project default). A human pass with more room to negotiate could
   make it easier to read; not a functional defect.
6. **BOM/LCSC:** every Phase-2 part that should carry an LCSC number has one in the schematic; the board
   has not been re-synced against `jlcpcb/project.db` in this stage (that sync, and the live
   cart.jlcpcb.com stock check on the 8 critical ICs named in supply_chain_report.md §S4, are the owner's
   pre-order steps).
7. Reserve fiducial sites (232.5, 50.5) and (252.0, 140.0) named in panel item F10/PLM-09 have not had
   copper added — deferred to the pre-order pass, as the panel specified.

## 10. Files

* Board (result copy): `.flatsat_work/phase2/round3/layout_finish/deliver/FlatSat_V1.kicad_pcb` (+ project
  directory beside it)
* This report: `docs/flatsat/2026-09-14_phase2_layout/layout_report.md`
* DRC triage addendum: `docs/flatsat/2026-09-14_phase2_layout/drc_triage.md` §11
* Renders: `docs/flatsat/2026-09-14_phase2_layout/img/layout_final_*`
* Production preview: `FlatSat_V1/jlcpcb/preview/` (+ its own `README.md`)
* Silkscreen tool (scratch, not promoted to `tools/pcb/`): `.flatsat_work/phase2/round3/layout_finish/silkscreen.py`
