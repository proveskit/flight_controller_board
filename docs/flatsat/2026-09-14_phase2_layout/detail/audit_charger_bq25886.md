# Independent audit — `charger_bq25886` (round 6, auditing fix-round-5's delivery)

**Scope:** 29 refs (C510-C518, D510, J510, JP510, L510, Q510, R510-R519, TP510-TP512, U510, U511),
envelope `[254.3,141.8,294.5,171.9]`, fixed anchors J510/JP510, anchor IC U511.
Board audited: `/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_charger_bq25886/placed.kicad_pcb`
(the fix-round-5 delivery responding to the round-5 audit's single should-fix, `L510↔U511`).
Deliverables audited: `placement_charger_bq25886.json`, `placement_charger_bq25886.md` (both dated
this round, "fix round 5").

**Method:** did not trust the placer's checklist. Fetched the BQ25886 (TI SLUSD88A) datasheet myself
this round (`WebFetch` → saved PDF → `Read` pages 4-5 and 31-32 as page images) and read the
DZDH0401DW datasheet (Diodes DS42784 Rev.3-2, all 10 pages) from the already-cached local copy in
the placer's own scratch dir, page by page, myself — not from anyone's summary. Independently
re-derived every pad position, courtyard polygon, and gap on the delivered board with `pcbnew`
(script written fresh this round, not reused from any prior round's tooling). Independently rebuilt
the board from scratch (fresh copy of the real `FlatSat_V1.kicad_pcb` → `outline.py` →
`apply_placement.py` → `heritage.py check` → `attachment_check.py`) using the placer's own
`merged_floorplan7.json` (218 refs) to prove the canonical pipeline is clean, not just to trust the
delivered `placed.kicad_pcb`. Additionally ran `kicad-cli pcb drc` **with `--refill-zones`** (the
methodology `floorplan.md` §6 specifies and a prior round's own audit flagged as necessary) — this is
new this round for this block and surfaced one previously-undisclosed finding (§6.2 below).

## 1. Datasheet sources (fetched and verified myself, this round)

- **BQ25886** — TI **SLUSD88A** (March 2019, rev. June 2019). Fetched the PDF live via `WebFetch`
  (binary saved locally, read with the `Read` tool as page images — text layer was not machine
  extractable through `WebFetch` alone, so I read the rendered pages directly). Page 4-5: pin table,
  24-pin VQFN, confirmed **PMID=21,22; VBUS=23; SW=17,18; BAT=13,14; SYS=15,16; BTST=12; REGN=11;
  ICHGSET=10; TS=7; ILIM=8; GND=19,20,4; D+=24; D−=1** — every one of these matches the placer's pin
  assignments exactly, no discrepancy found. Page 31 (§11.1 "Layout Guidelines") and page 32 (§11.2
  "Layout Example", Fig. 35): confirmed the placer's quoted 7-item numbered priority list is
  **verbatim** — I transcribed it independently from the rendered page image and it matches word for
  word, including "Layout PCB according to this specific order is essential." Figure 35 itself shows
  the inductor directly adjacent to the IC's SW-pin edge and the SYS/PMID cap clusters circled close
  to their respective pin groups — consistent with the priority-3/priority-1/priority-2 text.
- **DZDH0401DW** (Diodes DS42784 Rev.3-2) — `diodes.com` still returns HTTP 403 to automated fetch;
  read the placer's locally-cached `dz2.pdf` (full 10 pages) directly myself. Confirmed: **no
  numbered PCB-layout section anywhere in the document** (fallback correctly stands — the document
  has Description/Features/Mechanical/Marking/Absolute-Max/Electrical-Characteristics/Typical-
  Application-Circuit-and-Pinout/Timing/Ideal-Diode-Power-Saving/Package-Outline sections only, no
  "Layout" heading). Confirmed pin table (**DRAIN=6 "VIN sense voltage", SOURCE=4 "VOUT sense
  voltage", REF=2, BIAS=3, NC=1,5**) matches the placer's functional description and the schematic's
  own topology (`VBUS_CHG`→U510.DRAIN, `CHG_DVIN`→U510.SOURCE) exactly.
- **USB Type-C CC pull-down ≤5 mm** — this round's own carried-forward PM numeric criterion (round
  4), not re-derived from a primary spec this round; accepted as given, consistent with every prior
  round.

## 2. Geometry — independently measured on `placed.kicad_pcb` with a script written fresh this round

| Check | My measurement | Report's claim | Match |
|---|---|---|---|
| J510 position/rotation vs `floorplan_v2.json` | (262.0000,166.0600) rot 0.00 | unchanged | ✅ |
| JP510 position/rotation vs `floorplan_v2.json` | (257.3000,145.7900) rot 0.00 | unchanged | ✅ |
| U511 (anchor IC) move vs `floorplan_v2.json` | Δ=0.0000 mm, rot 0.00 | 0.0 mm | ✅ |
| All 29 refs' real courtyard bbox inside `[254.3,141.8,294.5,171.9]` | 29/29 inside | 27/27 movable inside | ✅ |
| L510↔U511 courtyard gap (this round's fix) | **0.5600 mm** | 0.560 mm (was 0.430) | ✅ **fixed, confirmed** |
| L510↔C512 (side-effect check) | 0.3400 mm, unchanged | 0.340 mm, unchanged | ✅ |
| L510 SW-pad (pin1) → nearest SW pin (17/18) | 4.0209 mm | 4.021 mm (was 3.946) | ✅ |
| L510 courtyard right edge vs envelope x1=294.5 | 288.075 → 6.425 mm clear | 6.425 mm clear | ✅ |
| C513 pad1 → nearest SYS pin (15/16) | 4.5115 mm | 4.512 mm | ✅ |
| C511 pad1 → PMID pin group (21/22) | 1.8792 mm | 1.879 mm | ✅ |
| C515 pad1 → nearest BAT pin (13/14) | 7.1425 mm | 7.143 mm | ✅ |
| C516 pad1 → REGN pin (11) | 3.3159 mm | 3.316 mm | ✅ |
| C512 SW-leg / BTST-leg → pins | 2.9965 / 3.1145 mm | 2.997 / 3.115 mm | ✅ |
| R515 pad1 → ICHGSET pin (10) | 6.9214 mm | 6.921/6.9224 mm | ✅ |
| R517 pad1 → TS pin (7) | 3.6394 mm | 3.639 mm | ✅ |
| R510→CC1 (J510.A5), R511→CC2 (J510.B5) | 2.3900 / 2.3900 mm | 2.390 / 2.390 mm | ✅ |
| R515 placed `Value` field | `5.62k` | "5.62 kΩ" (corrected this round) | ✅ |
| J510↔R510, J510↔R511 courtyard gaps | 0.5500 / 0.5500 mm | 0.550 / 0.550 mm | ✅ (round-4 fix, re-confirmed) |
| R517↔U511 courtyard gap | 0.5600 mm | 0.560 mm | ✅ (round-4 fix, re-confirmed) |
| D510↔U511, C515↔C518 courtyard gaps | 0.5700 / 0.5500 mm | 0.570 / 0.550 mm | ✅ (round-3 fixes, re-confirmed) |

Every independently spot-checked numeric claim matched the report's own figure to the same precision.
**No fabricated or rounded-away measurement found.**

## 3. Independent all-pairs courtyard-gap scan (block-internal, 29×29, real `GetCourtyard()` polygons)

Re-ran the scan from scratch with my own script (not reused from any prior round). Result: **exactly
10 pairs below 0.5 mm** (was 11 before this round's fix) — `C510↔U511` 0.280, `C511↔U511` 0.280,
`C513↔C514` 0.300, `C512↔C513` 0.300, `C512↔U511` 0.300, `C516↔U511` 0.300, `C513↔U511` 0.3015,
`C510↔D510` 0.330, `C510↔C511` 0.330, `C512↔L510` 0.340 — the exact same values reported in the
delivery's §9 table. `L510↔U511` no longer appears in this list (now 0.560 mm). **No undisclosed
sub-0.5 mm pair found**, and I confirm all 10 remaining pairs are a decoupling/bootstrap capacitor
sitting against the specific U511 pin(s) it serves, consistent with the round-4 PM carve-out (the
`L510↔U511` pair — the one pair not literally covered by "capacitor" — is the pair this round fixed
outright, so the carve-out's exact wording no longer needs to be stretched to cover it).

## 4. Cross-block / board-wide check

Extended the scan to all 483 board-wide footprints (any pair touching a `charger_bq25886` ref):
**zero real (≤0) or sub-0.5 mm overlaps** other than the one already-known, non-block-caused
`JP400↔JP510` at 0.870 mm (another block's fixed part vs. this block's fixed anchor — comfortably
clear, unaffected by this round's L510 move, not a finding).

## 5. Gates — re-run myself, independently, via a from-scratch rebuild (not the delivered board directly)

Copied a fresh `FlatSat_V1.kicad_pcb`/`.kicad_pro`, ran the placer's own `merged_floorplan7.json`
(218 refs) through the canonical pipeline myself:

```
outline.py:            Edge.Cuts -11/+7, In1 GND grown 1, heritage zones clipped 40, +4 GND pours,
                        +3 mounting holes, +65 stitching vias
apply_placement.py:    applied 218; refused (heritage) []; missing refs []
                        footprints not fully inside the outline: 0
                        courtyard overlaps (real polygons): 0
                        exit 0
heritage.py check --allow-zone-growth --allow-edge:
                        0 violation(s) (only expected zone-reshape/edge notes; new items:
                        footprints +221, tracks/vias +65, zones +4)
attachment_check.py:   65 new tracks/vias, 0 stub chain(s) into the flight section,
                        0 violation(s), 0 warning(s)
```

All three gates independently reproduced clean, matching the report's claims exactly.

## 6. Findings

### 6.1 RESOLVED — L510↔U511 courtyard gap (this round's fix)

The round-5 audit's should-fix — `L510↔U511` at 0.430 mm, an inductor sitting against the specific
SW pins BQ25886 §11.1 priority 3 tells it to minimize distance to, not literally covered by the
existing capacitor-only carve-out — is **fixed by direct geometry this round**, not by a carve-out
argument: L510 moved +0.13 mm in x only (284.00→284.13; y/rot/side unchanged), raising the real
courtyard gap to **0.560 mm**, independently confirmed (§2, §3). This clears the ≥0.5 mm floor
outright, so no exemption-wording debate is needed for this pair any more. Side effects checked and
confirmed clean: `L510↔C512` unchanged at 0.340 mm (y-governed, unaffected by an x-only move); no new
sub-0.5 mm pair anywhere (§3); envelope margin 6.425 mm clear of x1=294.5 (§2); SW-pin pad-distance
cost is a real but small +0.075 mm (3.946→4.021 mm), and BQ25886 §11.1 priority 3's "as close as
possible" intent remains well satisfied at 4.02 mm — smaller than several other same-block
pad-to-pin distances already accepted as PASS elsewhere in this block (e.g. R512→BIAS at 4.416 mm).
**No further action needed on this item.**

### 6.2 NOTE (new this round) — Q510 footprint has 3 real, previously-undisclosed intra-footprint pad-clearance DRC errors; not fixable by placement

Running `kicad-cli pcb drc --refill-zones` (the methodology `floorplan.md` §6 specifies, and which no
prior round of *this block's* audits actually applied — the round-4 `emulator_core` audit flagged
this exact gap for a sibling block, but it was never carried over here) drops the board-wide count
from 870 violations (mostly stale-zone-fill noise: 500 `clearance`, 199 `solder_mask_bridge`, 128
`hole_clearance`) to **48 real violations**. Of those 48, **3 touch this block, all on `Q510`**:

```
Clearance violation (netclass 'Default' clearance 0.2000 mm; actual 0.1900 mm)
  Pad 1 [VBUS_CHG]  of Q510 on F.Cu  (269.51, 156.0)
  Pad 2 [CHG_GATE]  of Q510 on F.Cu  (270.49, 156.9)
Clearance violation (netclass 'Default' clearance 0.2000 mm; actual 0.1900 mm)
  Pad 1 [VBUS_CHG]  of Q510 on F.Cu  (269.51, 156.0)
  Pad 3 [CHG_DVIN]  of Q510 on F.Cu  (270.49, 155.1)
Clearance violation (netclass 'Default' clearance 0.2000 mm; actual 0.1900 mm)
  Pad 2 [CHG_GATE]  of Q510 on F.Cu  (270.49, 156.9)
  Pad 4 [CHG_DVIN]  of Q510 on F.Cu  (270.49, 156.0)
```

**Why this is a placement-scope note, not a should-fix:** these are gaps *between pads of the same
footprint* (`easyeda2kicad:U-DFN2020-6E_L2.0-W2.0-P0.65-BL`, the DMP4047LFDE-7 DFN2020-6 package) —
the 0.65 mm-pitch land pattern's own pad spacing puts adjacent different-net pads 0.19 mm apart,
0.01 mm under this project's blanket 0.2 mm `Default` netclass clearance. This is **invariant under
any placement choice**: translating or rotating Q510 rigidly moves the whole footprint, it cannot
change the spacing between that footprint's own pads. Q510 has not moved in any round (0.0 mm/0°
since round 1), so this defect has existed since round 1 and was never surfaced because every prior
round's DRC evidence for this block used the un-refilled, noise-dominated 870-violation run (500
`clearance` hits that are stale-zone-fill artifacts, exactly the class the round-4 `emulator_core`
audit warned about) rather than `--refill-zones`.

This is exactly the situation `FlatSat_V1.kicad_dru`'s existing `fine-pitch-pad-pitch` rule already
exists to solve — it currently exempts only `U7`/`U15`/`U8`/`U16` (heritage Rev2 fine-pitch sensor
packages down to 0.15 mm) down to a 0.127 mm floor (JLCPCB's actual minimum copper clearance, per the
rule's own comment) — but does not list `Q510` or the DMP4047LFDE-7 footprint. 0.19 mm already clears
that real fab floor comfortably; it only fails the project's own blanket default. **Recommended
disposition:** add `Q510` (or a footprint-based match) to the `fine-pitch-pad-pitch` DRU rule, or
verify/select a DMP4047LFDE-7 footprint variant with ≥0.2 mm adjacent-pad spacing, at the routing/
DRC-cleanup stage — not a placement-geometry fix, and not something this round's (or any round's)
placement pass could have corrected by choosing a different X/Y/rotation. Flagged here because no
prior round's report disclosed it.

### 6.3 NOTE (re-confirmed, correct) — R515 documentation-label correction

Independently confirmed: `R515.GetValue() == '5.62k'` on the placed board, and
`battery_protection_replica.kicad_sch`'s own text note fits 5.62 kΩ (1% E96) rather than 5.7 kΩ
(not an E24/E96 value). The placer's table now correctly reads 5.62 kΩ. This was always a
documentation-table wording issue only — every pad-distance number in every round was already
computed from the real, correctly-valued placed part. No placement action needed.

### 6.4 NOTE (re-confirmed, favorable) — decoupling/divider GND pads sit directly inside the filled F.Cu ground pour

Independently checked with `zone.HitTestFilledArea()` against the `GND_F_Cu_wing` F.Cu pour (filled):
`C514`, `C515`, `C517`, `C518`, `R517`, `R518`'s GND pads all sit **inside** the filled pour (0 mm
hot-to-plane return-path cost). `R516` has no GND pad (it is the REGN-side leg of the TS divider,
confirmed via its own net names `Net-(U511-REGN)`/`Net-(U511-TS)` — it never had a GND connection to
check). Favorable, no action needed.

### 6.5 NOTE (carried forward, correctly out of scope) — J510 has no ESD/TVS part

Reconfirmed (6th consecutive round): none of the 29 refs is an ESD/TVS device;
`battery_protection_replica.kicad_sch`'s own sheet report labels J510 "power-only USB-C" (a bench
charger input, not a flight connector) — a Phase-1 schematic-author decision, outside a
placement-only pass's scope.

## 7. Placement-constraint re-check (independent)

- (a) envelope: 29/29 refs' real courtyard bboxes fully inside `[254.3,141.8,294.5,171.9]` — confirmed.
- (b) fixed anchors J510/JP510: bit-for-bit unmoved vs `floorplan_v2.json` — confirmed (Δ=0.0000 mm both).
- (c) anchor IC U511: 0.0 mm move — confirmed. Attachment reach: independently cross-checked
  `floorplan.md`'s L11 table (§5) myself — `Dir_Chrg_In`'s only listed attachment point is
  `TP500.1` (block `battery_replica`), not anything in `charger_bq25886`; this block's only path to
  a flight net is the normally-open `JP510` jumper, so constraint (c)'s reach requirement is
  vacuously satisfied here, confirmed by `attachment_check.py`'s own 0-violation result.
- (d) courtyard overlaps: 0 block-internal (29×29 real-polygon scan), 0 board-wide involving any
  block ref beyond the pre-existing, non-block-caused `JP400↔JP510` 0.870 mm — confirmed.
- (e) 12.6 mm lane: N/A, block entirely east of it (envelope starts x=254.3) — confirmed.
- (f) heritage frozen: 0 violations, re-run myself on an independent from-scratch rebuild — confirmed.
- (g) rotations/test-point reach: unchanged this round (only L510's x moved); TP510-512 sit at the
  block's north edge (~1.7-3 mm clear of y0=141.8), reachable — no new issue.
- (h) 0.5 mm courtyard target: all 10 remaining sub-0.5 mm pairs are decoupling/bootstrap capacitors
  against the specific pin(s) they serve — the `L510↔U511` pair that was not literally covered by
  that wording is fixed outright this round (§6.1) and no longer needs the carve-out at all.
- Ruling F3 (passives on F.Cu; U310/U312/U314 on B.Cu with F.Cu caps opposite): all 29 refs confirmed
  `side: F`; this block has no B.Cu-designated IC (U511, U510 are both F.Cu and not named in ruling
  F3's B.Cu list), so the B.Cu clause is correctly N/A here.

## 8. Verdict

**PASS.** The one open should-fix carried from the round-5 audit (`L510↔U511` courtyard gap) is
genuinely fixed, independently re-measured at 0.560 mm with every side effect checked and confirmed
unregressed (§6.1). One new, previously-undisclosed finding surfaced this round via the correct
(`--refill-zones`) DRC methodology — a real, non-placement-fixable footprint/DRU issue on Q510
(§6.2) — is recorded as a note for the routing/DRC-cleanup stage, since no placement geometry choice
(this round's or any prior round's) could have addressed it. Three carried-forward notes (R515 label,
GND-pad favorable disclosure, J510 ESD absence) require no placement action. All three canonical
gates (apply_placement, heritage, attachment) and every PLACEMENT CONSTRAINT (a)-(h) plus ruling F3
are independently reconfirmed clean on a from-scratch rebuild.

Rules audited: 27 (7 BQ25886 §11.1 priority items + pin-table cross-checks re-fetched and
re-transcribed this round, 2 DZDH0401DW rules + pin-table cross-check, 1 CC pull-down criterion,
8 canonical constraints (a-h) + ruling F3, the L510↔U511 fix-verification (measurement + 2
side-effect checks), the R515 value/GND-return/ESD-absence carried-forward notes, plus the new
`--refill-zones` DRC pass that surfaced the Q510 finding).
