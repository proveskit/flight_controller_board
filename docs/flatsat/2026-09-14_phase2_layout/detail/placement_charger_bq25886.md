# Detailed placement — `charger_bq25886` (stage 2b, **fix round 5**)

**Block:** BQ25886 USB-C bench charger, sheet `battery_protection_replica.kicad_sch` (block B, "USB-C → BQ25886 charger"), refs
C510–C518, D510, J510, JP510, L510, Q510, R510–R519, TP510–TP512, U510, U511 (29 parts).
**Envelope:** `[254.3, 141.8, 294.5, 171.9]` mm. **Fixed anchors:** J510 (USB-C receptacle), JP510 (CHG OUT jumper) — neither moved (bit-for-bit unchanged, confirmed §9).
**Anchor IC (brief constraint (c) / PM ruling):** U511 (BQ25886) — **0.0 mm move** (kept at its v1/round-1..5 position/rotation, 277.0/152.2, rot 0). U510 and Q510 are **not** anchor ICs under the enumerated PM list (U200, U511, U500, U315, the seven TCA4311As, U301–U303, Q701–Q703) — see §5.

This is **fix round 5**, responding to this round's independent audit of `placement_charger_bq25886.json`
(the round-4-delivered board), which returned **1 should-fix and 3 notes**. The one should-fix — the
`L510↔U511` courtyard gap this delivery had itself disclosed since round 1 (§4 of every prior round's
report) — is fixed this round by a single-axis nudge of the non-anchor inductor L510. The three notes (an
`R515` documentation‑label error, a favorable observation about ground‑pad coverage, and the pre‑existing
J510 ESD/TVS absence) are addressed in §1/§2/§4 below; none required a placement change.

**This round's audit finding, quoted (should-fix item):**
> L510, U511 — Brief placement constraint (h): >=0.5 mm courtyard-to-courtyard, except this round's PM
> carve-out ("the near part is a decoupling / bootstrap / input / output capacitor"). Measured 0.430 mm real
> `GetCourtyard()` rect-to-rect gap; unchanged since round 1, never previously scored by any of the 4 prior
> audit rounds. Required: >=0.5 mm, or a decoupling-capacitor-against-its-pin exemption; L510 is an
> inductor, not a capacitor, so the current carve-out wording does not cover it, even though it is
> satisfying BQ25886 SLUSD88A §11.1 priority 3 ("place inductor input terminal to SW pins as close as
> possible... minimize copper area"). Severity: should-fix.

**Note, on the block-specific "PM NOTES" text carried in this round's task packet:** that text is a verbatim
repeat of the round-4 PM ruling (R517↔U511 and J510↔R510/R511 courtyard fixes) — both of those fixes were
already delivered in round 4 (see §8.10/§8.11 there; re-confirmed unchanged in §2/§9 below, still ≥0.5 mm).
This round's actual audit output (quoted above and in the task's structured findings list) raises exactly
one should-fix — `L510↔U511` — plus the three notes handled below; that is what this delivery fixes and
documents. Nothing else in the block was touched.

---

## 1. ICs and support passives — function of every part

| Ref | Part | Function |
|---|---|---|
| U511 | BQ25886RGE (VQFN‑24, 4×4 mm, EP) | 2‑cell Li‑ion charger, boost‑mode PowerPath, USB BC1.2 detect |
| U510 | DZDH0401DW‑7 (SOT‑363) | Ideal‑diode controller driving Q510 as a reverse‑blocking P‑FET between J510 VBUS and the charger's VBUS/PMID input |
| Q510 | DMP4047LFDE‑7 (P‑FET, DFN2020‑6) | The reverse‑blocking pass FET U510 drives |
| C510 | 1 µF 0805 | VBUS‑pin bypass (U511 pin 23) |
| C511 | 22 µF 25 V X5R 1210 | PMID input‑rail bypass (U511 pins 21/22), datasheet priority‑2 cap |
| L510 | 1.0 µH SPM6530T‑1R0M120 | Boost/buck inductor, PMID↔SW — **relocated +0.13 mm in x this round, see §8.12** |
| C512 | 47 nF 0603 | BTST bootstrap cap, SW↔BTST (high‑side driver supply) |
| C513, C514, C517, C518 | 22 µF 25 V X5R 1210 ×4 | SYS output bypass (U511 pins 15/16), datasheet priority‑1 caps, 4× for the 44 µF‑after‑derating target (sheet §6/§9.2.2.3) |
| C515 | 22 µF 25 V X5R 1210 | BAT‑pin bypass (U511 pins 13/14) |
| R514 | 750 Ω | ILIM: sets input current limit (1.48 A) |
| R515 | **5.62 kΩ** (1% E96) | ICHGSET: sets fast‑charge current — `battery_protection_replica.kicad_sch` text note: "R515 = 5.62k -> ICHG = RICHGSET/KICHGSET = 5620/3810 = 1.475 A (9.2.2.5)... PM ruling S1: 5.7k not E24/E96; 5.62k 1% E96 fitted (1.48 A ILIM dominates)." **Corrected this round — see §1a; was mislabelled "5.7 kΩ" in rounds 1–4's table (a documentation error only, flagged as a note by this round's audit; every pad‑distance number computed for R515 in every prior round was already derived from the real, correctly‑valued placed part, not from this prose label, so no measurement changes.** |
| C516 | 4.7 µF 0603 | REGN bypass (gate‑drive rail) |
| R516/R517/R518 | 5.23 k / 30.1 k / 10 k | REGN–RT1–TS–RT2‖RT3(103AT stand‑in) thermal‑qualification divider — unchanged this round (round‑4 positions confirmed unchanged, still ≥0.5 mm from U511) |
| D510, R519 | LED 0603, 1 kΩ | STAT charge‑status indicator (STAT pin sinks through the LED+R to VBUS_CHG) — unchanged this round |
| J510 | USB‑C receptacle (fixed) | Bench‑charger power‑only USB‑C input |
| R510, R511 | 5.1 kΩ 0402 | USB‑C CC1/CC2 pull‑downs — UFP/sink signature on J510 — unchanged this round (round‑4 positions confirmed unchanged, still ≥0.5 mm from J510) |
| R512 | 1 MΩ | U510 "Rbias": BIAS→GND, sets ideal‑diode turn‑off speed |
| R513 | 1 MΩ | U510 "Rref": REF→GND, sets the ideal‑diode reference |
| JP510 | 2‑pin header (fixed, open by default) | Charger BAT → `Dir_Chrg_In`, isolatable so the charger can't push into a bench PSU |
| TP510/511/512 | Test points | VBUS_CHG / CHG_SYS / CHG_BAT probe points — unchanged |

### 1a. Note — R515 documentation label (this round's audit note, no placement action)

The auditor found `placement_charger_bq25886.md` (rounds 1–4) listed R515 as "5.7 kΩ" in the §1 function
table, while the schematic's own text note and the placed footprint's `Value` field both read **5.62 kΩ**
(1% E96 — the schematic note explains 5.7 kΩ is not an E24/E96 standard value; 5.62 kΩ was fitted instead,
since ILIM at 1.48 A already dominates the actual charge‑current ceiling). Confirmed directly against the
placed board this round: `fps['R515'].GetValue() == '5.62k'`. **This is a documentation‑table correction
only** — every R515 pad‑distance figure in every round's checklist (row 14/#R515→ICHGSET) was computed from
the real placed part, which has always carried the correct 5.62 kΩ value, so no measurement in this or any
prior round changes. Fixed in the table above.

---

## 2. Guideline checklist (all rows re-measured on this round's placed board)

Source A: **BQ25886 datasheet (TI SLUSD88A, ti.com/lit/ds/symlink/bq25886.pdf), §11.1 "Layout Guidelines" +
§11.2 "Layout Example" (Fig. 35)** and pin table (p.4‑5). Source B: **DZDH0401DW datasheet (Diodes DS42784
Rev.3‑2, diodes.com)** — confirmed rounds 2–4: no numbered PCB‑layout section exists anywhere in the
document (fallback stands). Source C: **USB Type‑C spec** (CC pull‑down placement, brief §6.6). No re‑fetch
was needed this round — this round's audit did not dispute any datasheet fact, pin mapping, or component
value; the one should‑fix was a geometry fix (L510↔U511), already correctly identified and disclosed by
this delivery's own §4 since round 1.

**Measurement method (unchanged since round 3):** "Courtyard gap" = real rectangle‑to‑rectangle Euclidean
distance between `pcbnew.FOOTPRINT.GetCourtyard()` bounding boxes — `dx=max(l2-r1,l1-r2,0)`,
`dy=max(t2-b1,t1-b2,0)`, `gap=sqrt(dx²+dy²)` when both axes are separated, else `max(dx,dy)`. "Pad
distance" = pad‑centre to pad‑centre, to the nearest of the candidate same‑net pins. All measurements from
`pcbnew` on **`placed7.kicad_pcb`** (this round's canonical rebuild — §7).

| # | Rule | Source | Criterion | Measured (this round) | Pass/Fail |
|---|---|---|---|---|---|
| 1 | "Put SYS output capacitor as close to SYS and GND pins as possible" | §11.1 priority 1 | Nearest SYS cap, pad‑to‑nearest‑pin | **C513 → nearest(pin15/16) = 4.512 mm**, courtyard gap 0.301 mm | **PASS** |
| 2 | "Place PMID input capacitor as close as possible to PMID and PGND pins" | §11.1 priority 2 | C511 pad‑to‑PMID‑pin | **1.879 mm**, courtyard gap 0.280 mm (unchanged) | **PASS** |
| 3 | "Place inductor input terminal to SW pins as close as possible… minimize copper area" | §11.1 priority 3 | L510 SW‑side pad to nearest SW pin | **4.021 mm** (was 3.946 mm — +0.075 mm from this round's +0.13 mm x‑move, still tight/reasonable for a boost/buck inductor), courtyard gap to U511 **0.560 mm** (was 0.430 mm — fixed, §8.12) | **PASS (guideline intent preserved, courtyard gap now also passes)** |
| 4 | "Decoupling capacitors should be placed on the same side of and next to the IC, trace as short as possible" | §11.1 priority 4 | Courtyard gap to U511, all 9 caps, each individually | C510 0.280, C511 0.280, C512 0.300, C513 0.301, C516 0.300 — **5 of 9 at 0.28–0.30 mm**; C515 3.832, C514 5.290, C518 6.729, C517 7.616 mm (unchanged) | **PASS (4 caps disclosed farther, §4)** |
| 5 | "Route analog ground separately… tie at the thermal pad" | §11.1 priority 5 | Not a placement action | N/A — pins 4/19/20/25(EP) are the only U511 GND pins | **N/A (placement stage)** |
| 6 | "Exposed thermal pad soldered to PCB ground, sufficient thermal vias" | §11.1 priority 6 | Routing‑stage | Footprint's EP pad unchanged | **N/A (placement stage)** |
| 7 | "Via size/number sufficient for current path" | §11.1 priority 7 | Routing‑stage | N/A | **N/A (placement stage)** |
| 8 | Ideal‑diode controller: DRAIN/SOURCE sense the pass FET's D/S (Kelvin), BIAS drives the gate | DZDH0401DW p.5 | U510→Q510 cluster intact | Unchanged | **PASS** |
| 9 | Rbias/Rref close to BIAS/REF pins | DZDH0401DW p.5 | R512→BIAS, R513→REF | R512→pin3 **4.416 mm**; R513→pin2 **5.149 mm** (unchanged) | **PASS** |
| 10 | USB‑C CC1/CC2 pull‑downs close to J510's CC pins | USB Type‑C spec + round‑4 PM ruling (≤5 mm) | R510→CC1, R511→CC2, pad‑to‑pin | **R510: 2.390 mm; R511: 2.390 mm** (unchanged since round 4) | **PASS (unchanged)** |
| 11 | Ruling F3: passives stay on F.Cu | Brief §12 ruling F3 | All 27 placed refs `side: F` | Confirmed | **PASS** |
| 12 | BTST cap inherits the SW‑node "minimize copper area" rule | §11.1 priority 3 + pin table BTST row | C512's SW‑leg / BTST‑leg pad‑to‑pin, both stated | **SW‑leg 2.997 mm; BTST‑leg 3.115 mm** (unchanged) | **PASS** |
| 13 | BAT cap "closely to the BAT pin and GND" | BQ25886 pin table, BAT row | C515 pad‑to‑nearest(pin13/14) | **7.143 mm**, courtyard gap 3.832 mm (unchanged) | **DISCLOSED, §4** |
| 14 | ICHGSET/REGN not the farthest south‑row items without reason | General practice + REGN pin‑table bypass instruction | R515→ICHGSET, C516→REGN vs. R514/R516 | **R515→pin10 6.921 mm; C516→pin11 3.316 mm** (courtyard gap 0.300 mm, unchanged); R514 (ILIM) 10.549 mm, R516 (REGN pad) 10.977 mm, R516 (TS pad) 9.079 mm | **PASS** |
| 15 | R512/R513 courtyard‑to‑courtyard routing room | Brief constraint (h), ≥0.5 mm | Real rect‑to‑rect gap | **0.650 mm** (unchanged) | **PASS** |
| 16–21 | *(round‑1/2 audit items, all previously fixed — history preserved)* | — | — | — | **RESOLVED — see round‑2/3 deliveries, unchanged since** |
| 22 | D510↔U511 courtyard gap (round‑3 should‑fix, fixed round 3) | Round‑3 audit §3.1 | Real rect‑to‑rect gap, ≥0.5 mm | **0.570 mm** (unchanged this round) | **PASS (unchanged)** |
| 23 | C515↔C518 courtyard gap (round‑3 should‑fix, fixed round 3) | Round‑3 audit §3.2 | Real rect‑to‑rect gap, ≥0.5 mm | **0.550 mm** (unchanged this round) | **PASS (unchanged)** |
| 24 | R517↔U511 courtyard gap (round‑4 should‑fix, fixed round 4) | Round‑4 audit | Real rect‑to‑rect gap, ≥0.5 mm | **0.560 mm** (unchanged this round — the block‑specific PM note repeated in this round's task packet was already satisfied by round 4; re‑confirmed here) | **PASS (unchanged)** |
| 25 | J510↔R510 / J510↔R511 courtyard gaps (round‑4 should‑fix, fixed round 4) | Round‑4 audit | Real rect‑to‑rect gap, ≥0.5 mm, and ≤5 mm to CC pin | **J510↔R510 0.550 mm, J510↔R511 0.550 mm; R510→CC1 2.390 mm, R511→CC2 2.390 mm** (all unchanged this round — re‑confirmed) | **PASS (unchanged)** |
| 26 | *(round‑5 audit, should‑fix)* L510↔U511 courtyard gap 0.430 mm, inductor, no cap exemption applies per carve‑out wording | This round's audit finding (quoted above); consistent with prior self‑disclosure in §4 rounds 1‑4 | Real rect‑to‑rect gap, ≥0.5 mm | **L510 moved +0.13 mm in x (284.00→284.13, y/rot/side unchanged). New gap: 0.560 mm** (was 0.430 mm) — see §8.12 | **FIXED** |
| 27 | *(round‑5 audit, note)* R515 documentation‑table label said "5.7 kΩ", schematic/footprint value is 5.62 kΩ | This round's audit finding (quoted above) | Doc‑table value matches schematic note + placed `Value` field | **Table corrected to 5.62 kΩ in §1/§1a — not a placement defect; no pad‑distance number changes** | **FIXED (documentation)** |
| 28 | *(round‑5 audit, note)* GND‑side pads of C514/C515/C517/C518/R516/R517/R518 all sit inside the filled F.Cu ground pour — favorable disclosure, not a defect | This round's audit finding (quoted above) | `zone.HitTestFilledArea()` against `GND_F_Cu_wing` | Re‑confirmed this round on `placed7.kicad_pcb`: every one of those refs' GND pads sits inside the filled pour footprint (0 mm hot‑to‑plane trace‑length cost for ground return; only the hot‑side distances in row 4/§4 are real costs) | **N/A — favorable note, no action** |
| 29 | *(round‑5 audit, note)* J510 has no ESD/TVS part — schematic‑author decision, outside placement scope | This round's audit finding (quoted above); consistent with rounds 3/4's identical note | Whether an ESD/TVS device exists among the 29 refs | Reconfirmed a **fifth** consecutive round: none of the 29 refs is an ESD/TVS part; `battery_protection_replica.kicad_sch` labels J510 "USB‑C, power only" | **N/A — no part to place, unchanged** |

**Rows not independently measurable / not applicable at the placement stage:** #5–#7 (analog/power‑ground separation, thermal‑via count, via sizing) are routing/fab actions.

---

## 3. Placement rationale, IC by IC

**U511 (BQ25886) — unchanged, 0.0 mm move, no finding this round.**

- **North edge (PMID/VBUS/D+):** C510/C511 unchanged since round 1; **L510 moved +0.13 mm in x this
  round** — see §8.12 — to open its courtyard gap to U511 from 0.430 mm to 0.560 mm, while the SW‑side pad
  moves only from 3.946 mm to 4.021 mm from the nearest SW pin (a negligible cost against §11.1 priority 3's
  "as close as possible" intent, which remains well satisfied).
- **NE corner, directly south of L510:** C512 (BTST cap) — unchanged since round 1; its own gap to L510
  (0.340 mm, an accepted cap‑carve‑out trade) is unaffected by L510's x‑only move because the two parts'
  gap there is governed by y‑separation, not x (confirmed §8.12 side‑effect check).
- **East edge, two‑column bank:** C513/C515/C517 (near column, x=282.32) and C514/C518 (far column) —
  unchanged this round.
- **South edge (TS/ILIM/PG/ICHGSET/REGN):** R516/R517/R518 (the REGN‑RT1‑TS‑RT2 divider column at x=275.4,
  y‑shifted +0.26 mm as a group in round 4) and R514/R515 (x=277.6 column) and C516 — all unchanged this
  round; round‑4's fix re‑confirmed still passing (R517↔U511 0.560 mm).
- **West edge (D‑/STAT):** D510/R519 unchanged this round (fixed round 3).
- **U510+Q510 input‑protection pocket, R512/R513 (Rbias/Rref):** unchanged, no finding this round.
- **R510/R511 CC pull‑downs:** unchanged this round (relocated round 4, re‑confirmed still ≥0.5 mm from
  J510 and ≤5 mm from their CC pins).

---

## 4. Deviations / rules not fully met

Two disclosed, unavoidable trade‑offs remain, unchanged in substance from rounds 1–4 (no audit round has
challenged the substance of either, only, in earlier rounds, the reported numbers):

1. **Not all 9 decoupling caps can sit at ~0.3 mm.** Four 3.2×2.5 mm 1210 packages (four SYS caps) plus a
   fifth 1210 (BAT) cannot all be adjacent to a 6‑pin band that is only 2.5 mm tall. Every net that has *no
   redundant partner* (PMID, VBUS, both BTST legs, REGN) sits at a true 0.28–0.30 mm courtyard gap; BAT
   (also no redundant partner) gets the next‑best slot (3.832 mm gap / 7.143 mm pad distance); only the
   three *redundant* SYS caps (C514, C517, C518 — one SYS cap, C513, already holds the near slot) sit
   farther out, at 5.290 / 6.729 / 7.616 mm courtyard gap and 8.003 / 10.629 / 11.831 mm pad distance
   respectively.
2. **BAT cap (C515) is 7.143 mm from its nearest pin**, not single‑digit‑mm‑tight like PMID/VBUS/REGN/BTST.
   Giving BAT the very closest slot would require demoting the numbered priority‑1 SYS representative
   (C513, a confirmed‑PASS row) to fix an unnumbered pin‑table instruction — a genuine priority trade‑off,
   disclosed rather than silently taken.

**Item closed this round (was disclosed rounds 1–4, now fixed):**

3. **L510↔U511 courtyard gap was 0.430 mm** (below the 0.5 mm floor) since round 1, correctly disclosed in
   every prior round's §4/§9 as the functional twin of the PM's capacitor carve‑out (an SW‑node support part
   packed against the specific U511 pins it must be electrically close to, per BQ25886 §11.1 priority 3),
   but never fixed because the carve‑out's literal wording named only capacitors. This round's audit turned
   that disclosure into a formal should‑fix, so it is now fixed (§8.12): L510 moved +0.13 mm in x, raising
   the courtyard gap to 0.560 mm while the SW‑pin pad distance grows by only 0.075 mm (3.946 mm → 4.021 mm)
   — the priority‑3 "as close as possible" intent remains well satisfied and no new deviation is created.

**PM‑accepted trades (courtyard gap, not deviations) — see the full table in §9:** every remaining sub‑0.5 mm
pair involves a capacitor sitting against the specific pin(s) it decouples/bypasses — exactly the case this
round's PM carve‑out names. With L510↔U511 fixed, there are no more sub‑0.5 mm pairs outside that carve‑out.

---

## 5. Anchor IC move

**U511: 0.0 mm** (277.0, 152.2, rot 0 — identical to v1/round‑1..5). This block's only constraint‑(c)
anchor IC has no reach change. This round's single fix (L510) touches neither U511 nor either fixed anchor.

**U510 and Q510 are not constraint‑(c) anchor ICs** (see round‑3 delivery §5 for the full PM‑ruling
citation and history; unchanged, re‑confirmed this round, not re‑litigated).

---

## 6. Attachment‑reach effect

Unchanged: this block has no entry in the L11 attachment map (floorplan.md §5) — its only path to the
flight section is `Dir_Chrg_In` through the normally‑**open** JP510 jumper, and GND only through the grown
In1 plane/pours. Constraint (c)'s "attachment reach must not get worse by more than 3 mm" is **vacuously
satisfied** for U511 (the only ref this constraint applies to in this block) — confirmed again this round by
`attachment_check.py`: 0 stub chains, 0 violations, 65 new tracks/vias.

---

## 7. Exact commands run (fix round 5)

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
SCRATCH=/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_charger_bq25886
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# 1. Took the round-4-delivered placement_charger_bq25886.json (29 refs, includes round 4's
#    R517/R518/R516 and R510/R511 fixes) as the starting point and independently re-measured
#    L510<->U511 on the round-4 board (placed6.kicad_pcb) with the same GetCourtyard()-based
#    method used since round 3, confirming the auditor's number before changing anything:
#      L510<->U511: 0.430 mm  (confirmed; matches every prior round's own self-disclosure)

# 2. One placement change (1 ref), a nudge of a non-anchor support part (inductor -- movable
#    anywhere in the envelope per this round's PM ruling on constraint (c)):
#      L510: (284.00, 147.70) -> (284.13, 147.70)  (+0.13 mm in x only; y/rot/side unchanged)
#    Chosen because the L510<->U511 gap is purely x-governed (their y-ranges already overlap),
#    so an x-only move raises the courtyard gap 1:1 without perturbing any y-governed neighbour
#    pair (verified against every footprint within reach before acceptance -- see 8.12).
#    Wrote this block's 29 refs (including the two unmoved fixed anchors, for completeness) to
#    full_block_v7.json, merged into a fresh copy of the floorplan of record (floorplan_v2.json --
#    note floorplan_v2.json still carries this block's pre-round-4 positions, since the v2.1
#    integration predates this block's round-4/round-5 fixes; this round's merge supersedes them
#    with the full round-4+round-5 fixed set):
python3 -c "
import json
base = json.load(open('/Users/ncc-michael/GitHut/flight_controller_board/docs/flatsat/2026-09-14_phase2_layout/floorplan_v2.json'))
newp = json.load(open('$SCRATCH/full_block_v7.json'))
base['placements'].update(newp)
json.dump(base, open('$SCRATCH/merged_floorplan7.json','w'), indent=2)
"

# 3. rebuilt from scratch on a fresh copy of the real v1 board (not the preview)
cp /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/FlatSat_V1.kicad_pcb "$SCRATCH/rebuild_base7.kicad_pcb"
cp /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/FlatSat_V1.kicad_pro "$SCRATCH/rebuild_base7.kicad_pro"

$KPY tools/pcb/outline.py --board "$SCRATCH/rebuild_base7.kicad_pcb" \
    --out "$SCRATCH/outlined7.kicad_pcb" --spec "$SCRATCH/merged_floorplan7.json"
# -> Edge.Cuts +7/-11, In1 GND grown, 4 new pours, 3 mounting holes, 65 stitching vias (identical
#    to rounds 1-6 -- outline/pour spec unchanged, only 1 ref's placement.json entry changed)

$KPY tools/pcb/apply_placement.py --board "$SCRATCH/outlined7.kicad_pcb" \
    --placement "$SCRATCH/merged_floorplan7.json" --out "$SCRATCH/placed7.kicad_pcb"
# -> applied 218; refused (heritage) []; missing refs []
# -> footprints not fully inside the outline: 0
# -> courtyard overlaps (same-side, >=1 new part; real polygons): 0
# -> exit 0
# (the same informational bbox/pad-shape-fallback line for BT1/G***/REF**/RF1/SW703/U12/U30
#  reappeared -- none is in this block, does not affect the 0/0/0 counts.)

$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json \
    "$SCRATCH/placed7.kicad_pcb" --allow-zone-growth --allow-edge
# -> heritage check: 0 violation(s)

$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json "$SCRATCH/placed7.kicad_pcb"
# -> attachment check: 65 new tracks/vias, 0 stub chain(s), 0 violation(s), 0 warning(s)

# 4. re-measured every checklist row plus a full 29x29 block-internal all-pairs real-courtyard
#    gap scan directly on placed7.kicad_pcb with $SCRATCH/final_measure7.py
$KPY "$SCRATCH/final_measure7.py"

# 5. delivered board copied into the delivery path
cp "$SCRATCH/placed7.kicad_pcb" "$SCRATCH/placed.kicad_pcb"
cp "$SCRATCH/placed7.kicad_pro" "$SCRATCH/placed.kicad_pro"
```

Datasheet sources: unchanged from round 2/3 — BQ25886 (`ti.com/lit/ds/symlink/bq25886.pdf`, pp. 4–5 pin
table, pp. 31–32 §11 Layout); DZDH0401DW (Diodes DS42784 Rev.3‑2, local copy `dz2.pdf`, all 10 pages). No
re‑fetch needed this round.

---

## 8. Fix history — violation → what changed → new measurement

*(Rounds 1–4's fix history, §§8.1–8.11, is preserved unchanged in the round‑4 delivery of this file and is
not re‑pasted here in full to keep this section focused on round 5's one new item; every number in §2
above that carries forward from round 4 was independently re‑measured on this round's own rebuild, not
copied, and matches.)*

### 8.12 SHOULD‑FIX — L510↔U511 courtyard gap 0.430 mm, inductor, no cap exemption applies per the carve‑out's literal wording

**Root cause:** L510 (the PMID↔SW boost/buck inductor) sits directly against U511's north‑east edge; its
SW‑side pad (pin 1) faces U511's SW pins (17/18) at 3.946 mm, and the courtyard boxes overlap fully in y
(L510: y 144.105–151.215; U511: y 149.525–154.875) so the whole 0.430 mm gap is x‑governed:
`L510.left (280.105) − U511.right (279.675) = 0.430 mm`. This has been the case unchanged since round 1;
every prior round's §4 disclosed it explicitly as the functional twin of the PM's capacitor carve‑out (a
support part packed against the exact IC pins a numbered datasheet priority tells it to minimize distance
to), but because L510 is an inductor, not a "decoupling / bootstrap / input / output capacitor", the
carve‑out's literal wording never covered it, and no round's audit before this one scored it as a finding.
This round's audit does score it, as a should‑fix, so it is fixed here rather than re‑disclosed.

**What changed:** L510 moved **+0.13 mm in x only** (y, rotation, side unchanged):
- L510: (284.00, 147.70) → (284.13, 147.70)

Because the L510↔U511 gap is entirely x‑governed (y‑ranges already overlap and continue to after an x‑only
move), this single move raises the gap 1:1 by the move distance: 0.430 + 0.13 = 0.560 mm.

**Side‑effect check (verified on the rebuilt board, not assumed):**
- L510↔C512 (south neighbour, the BTST bootstrap cap): **0.340 mm, unchanged.** This pair's gap is governed
  by y‑separation (L510's courtyard bottom edge vs. C512's courtyard top edge); an x‑only move of L510
  cannot affect a y‑governed gap, confirmed by direct re‑measurement, not just algebraic reasoning.
- L510's new right (east) courtyard edge: 288.075 mm — 6.425 mm clear of the envelope's x1=294.5 mm
  boundary; no envelope violation, and no other block-internal ref sits east of L510 within reach (nearest
  is C511 to the west, unaffected).
- L510's SW‑side (pin 1) pad‑to‑nearest‑SW‑pin distance: **4.021 mm** (was 3.946 mm — a +0.075 mm increase,
  the direct, expected cost of the fix; still comfortably satisfies BQ25886 §11.1 priority 3's "as close as
  possible" intent, and is smaller than several other same‑block pad‑to‑pin distances that already pass,
  e.g. R512→BIAS at 4.416 mm).
- L510's PMID‑side (pin 2) net (`Net-(C511-Pad1)`, shared with C511's PMID bypass) pad position shifts by
  the same +0.13 mm; no other constraint depends on this pad's absolute position.
- No new block‑internal courtyard overlap anywhere on the board (confirmed by the full 29×29 overlap scan
  in §9 — "none"); L510↔U511 itself no longer appears in the sub‑0.5 mm table at all (dropped out, rather
  than merely crossing the floor by a hair — see §9).

**New measurement:** L510↔U511 courtyard gap **0.560 mm** (`GetCourtyard()` convention) — was 0.430 mm.
Margin over the 0.5 mm target: 0.06 mm (the same margin style used for round 4's R517↔U511 fix).
**Verdict:** Fixed, with the one adjacent pair (L510↔C512) confirmed unregressed and the guideline‑intent
pad distance cost (+0.075 mm) disclosed as negligible.

---

## 9. Gates re‑run this round (fix round 5, all clean) + full all‑pairs gap scan

```
apply_placement.py: applied 218; refused (heritage) []; missing refs []
                     footprints not fully inside the outline: 0
                     courtyard overlaps (same-side, >=1 new part; real polygons): 0
                     exit 0
heritage.py check:   0 violation(s)  (--allow-zone-growth --allow-edge; only allowed zone-reshape/
                     edge notes, identical class to rounds 1-6, from the unchanged outline/pour spec)
attachment_check.py: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
```

**Placement constraints re‑checked:** (a) all 27 movable refs inside `[254.3,141.8,294.5,171.9]` (confirmed
by `final_measure7.py`); (b) J510/JP510 unmoved (bit‑for‑bit, confirmed by direct position read: J510
(262.0000,166.0600) rot 0.00, JP510 (257.3000,145.7900) rot 0.00 — identical to every prior round); (c) U511
0.0 mm move (277.0000,152.2000, rot 0.00 — confirmed), attachment reach vacuously satisfied (0 stub chains,
0 violations); (d) 0 courtyard overlaps board‑wide (`apply_placement.py`) and block‑internal
(`final_measure7.py`'s full 29×29 pairwise real‑polygon scan — **none**); (e) N/A, block entirely east of
the 12.6 mm lane; (f) heritage 0 violations; (g) rotations unchanged (only L510's x moved, side/rotation
unchanged); test points/LED unchanged; (h) **this round's should‑fix pair now ≥0.5 mm** (L510‑U511:
0.560 mm), every round‑3/4 pair re‑confirmed unregressed, and the complete all‑pairs table below accounts
for every sub‑0.5 mm gap left on the board.

### Complete table — every block‑internal courtyard pair below 0.5 mm (29×29 scan, real `GetCourtyard()` polygons, `placed7.kicad_pcb`)

| Pair | Gap (mm) | Disposition |
|---|---|---|
| C510 ↔ U511 | 0.280 | accepted trade (capacitor against the pin it serves — C510 is U511's VBUS‑pin bypass cap, packed against pin 23) |
| C511 ↔ U511 | 0.280 | accepted trade (PMID decoupling cap against pins 21/22) |
| C513 ↔ C514 | 0.300 | accepted trade (C513, the near part, is the priority‑1 SYS cap against pins 15/16 — PM's own worked example from round 3, unchanged) |
| C512 ↔ C513 | 0.300 | accepted trade (both are decoupling caps — BTST and SYS respectively — each packed against its own U511 pin group; this is the boundary between the two caps' own tight slots) |
| C512 ↔ U511 | 0.300 | accepted trade (BTST bootstrap cap against SW/BTST pins) |
| C516 ↔ U511 | 0.300 | accepted trade (REGN decoupling cap against pin 11) |
| C513 ↔ U511 | 0.302 | accepted trade (SYS decoupling cap against pins 15/16, priority‑1) |
| C510 ↔ D510 | 0.330 | accepted trade (C510 is U511's VBUS‑pin bypass cap, packed against pin 23; D510 is the adjacent STAT LED, unmoved) |
| C510 ↔ C511 | 0.330 | accepted trade (both are decoupling caps packed against their own adjacent U511 pin groups — VBUS pin 23 and PMID pins 21/22) |
| C512 ↔ L510 | 0.340 | accepted trade (C512 is the BTST bootstrap cap sitting against the SW/BTST node it serves, per §11.1 priority 3; L510 is the adjacent SW‑node inductor) — **unaffected by this round's L510 move, confirmed §8.12** |

**Total: 10 pairs below 0.5 mm — all 10 are accepted trades** (a decoupling/bootstrap capacitor packed
against the specific pin(s) it serves, exactly this round's PM carve‑out wording). **L510↔U511 — the one
pair that was not literally covered by the carve‑out's wording — has been fixed this round (§8.12) and no
longer appears in this table at all** (its gap is now 0.560 mm, above the 0.5 mm floor).

Every pair that does **not** qualify for the carve‑out and was flagged by any audit round (R517↔U511,
J510↔R510, J510↔R511, D510↔U511, C515↔C518 — rounds 3/4 — and now L510↔U511, round 5) is fixed at ≥0.5 mm,
confirmed above and in §2.

**Open items closed this round:** this round's audit `verdict` listed exactly 1 should‑fix (L510↔U511,
fixed §8.12, row 26 in §2) and 3 notes (R515 doc label, fixed §1a/row 27; GND‑pad favorable disclosure,
re‑confirmed row 28; J510 ESD absence, re‑confirmed row 29 — neither of the latter two required a
placement action). 0 new courtyard overlaps, 0 heritage violations, 0 attachment‑gate violations on the
full rebuild. Nothing else in the block was touched.
