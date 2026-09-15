# Detailed placement — `face_column` block

**Date:** 2026-09-14 · **Stage:** 2b (detailed placement, passives only), **fix round 3**
**Block:** solar_emulation face column
**Refs (48):** C300,C310,C311,C312,C313,C314,C316,R300–R303,R310–R314,R320–R324,R330–R334,R340–R344,
R350–R354,R370–R374,U300,U310,U311,U312,U313,U314,U316
**Envelope:** x 242–268.3 mm, y 50.5–135.5 mm · **Fixed anchors:** none
**Sheet:** `solar_emulation.kicad_sch` (report `sheet_solar_emulation.md`)

This is **fix round 3**, responding to the independent auditor's `detail/audit_face_column.md`
(fix-round-2 audit; verdict "fail", 0 must-fix, 2 should-fix, 1 note). §15 is the fix-round-3 log.
§§1–14 restate the round-2 design and update every number this round touched (only 3 of 48 refs
move: C316, R371, R372 — everything else, including all 7 anchor ICs, is byte-identical to round 2,
independently re-verified in §15.0). **Rules checked: 19** (round 2's 16 plus 3 new rows carried in
from this round's audit — the two should-fix findings and the one note, §3 rows 17–19). **Rules
failed: 0** (both should-fix items are fixed below with real, independently-reproducible pcbnew
measurements; the note is re-confirmed, not reopened).

## 0. What changed and why (unchanged from round 0/1)

v1 (`floorplan.json`) placed all 7 TCA4311A buffers correctly (block order, columns, B.Cu for
U310/U312/U314) but dropped their 34 support resistors and 7 decoupling caps into generic shared
rows regardless of which IC they belong to (9–20 mm from the pin they actually serve). Round 0
re-anchored every passive to its real pin; round 1 fixed round 0's three audit findings (attachment
reach, cap orientation, courtyard clearance). This round (2) fixes round 1's own two remaining
should-fix findings (a residual 0.010 mm courtyard-clearance shortfall on 17 pairs, and an
inaccurate guideline citation) and corrects a documentation-only note. **No electrical or block-level
design decision changes; only 20 of 48 refs move, each by ±0.05 mm in y.** Round 3 (this report's
current state) fixes round 2's own two remaining should-fix findings — see §15.

## 1. ICs in this block and their support passives

One TCA4311A (`easyeda2kicad:TCA4311ADGKR`, MSOP-8) per channel; U310/U312/U314 stay on B.Cu (brief
F3/G2). Pin map confirmed from the real footprint: 1 EN, 2 SCLOUT, 3 SCLIN, 4 GND, 5 READY, 6 SDAIN,
7 SDAOUT, 8 VCC.

| IC | Face/channel | VCC net | Decoupling | EN pull-up | READY pull-up | SDAOUT pull-up | SCLOUT pull-up | Sense tap | Extra (Face 0 only) |
|---|---|---|---|---|---|---|---|---|---|
| U300 | Face 0 (real ref. silicon front-end) | F0_PWR | C300 100 nF | R300 10 k | R301 10 k | R302 10 k → `F0_DEV_SDA` | R303 10 k → `F0_DEV_SCL` | none (F0 not emulated) | TMP112/VEML6031/DRV2605L are a different block, not placed here |
| U310 | Face 1 @ J9 (B.Cu) | F1_PWR | C310 100 nF | R310 10 k | R311 10 k | R312 4.7 k → `EMU_F1_SDA` | R313 4.7 k → `EMU_F1_SCL` | R314 4.7 k → `EMU_F1_SENSE` | — |
| U311 | Face 2 @ J11 | F2_PWR | C311 100 nF | R320 10 k | R321 10 k | R322 4.7 k → `EMU_F2_SDA` | R323 4.7 k → `EMU_F2_SCL` | R324 4.7 k → `EMU_F2_SENSE` | — |
| U312 | Face 3 @ J13 (B.Cu) | F3_PWR | C312 100 nF | R330 10 k | R331 10 k | R332 4.7 k → `EMU_F3_SDA` | R333 4.7 k → `EMU_F3_SCL` | R334 4.7 k → `EMU_F3_SENSE` | — |
| U313 | Face 4 @ J1 | F4_PWR | C313 100 nF | R340 10 k | R341 10 k | R342 4.7 k → `EMU_F4_SDA` | R343 4.7 k → `EMU_F4_SCL` | R344 4.7 k → `EMU_F4_SENSE` | — |
| U314 | Face 5 @ J2 (B.Cu) | F5_PWR | C314 100 nF | R350 10 k | R351 10 k | R352 4.7 k → `EMU_F5_SDA` | R353 4.7 k → `EMU_F5_SCL` | R354 4.7 k → `EMU_F5_SENSE` | — |
| U316 | Top-cap (TCA9548 ch7) | +3V3 | C316 100 nF | R370 10 k | R371 10 k | R372 4.7 k → `EMU_TOP_SDA` | R373 4.7 k → `EMU_TOP_SCL` | R374 4.7 k → `EMU_FC3V3_SENSE` | — |

## 2. Guideline source (corrected this round — was the round-1 should-fix)

Round 0 and round 1 both stated "TCA4311A has no dedicated Layout/Layout Guidelines section" and
cited a fallback to "§6.3" (Recommended Operating Conditions — unrelated to layout). **That was
wrong and is corrected here.** Fetched fresh from TI (`https://www.ti.com/lit/ds/symlink/tca4311a.pdf`,
SCPS226C, text-extracted with `pdftotext -layout` and independently verified against the table of
contents), the datasheet **does** contain a layout section:

> **11 Layout**
> **11.1 Layout Guidelines** — "...By-pass and de-coupling capacitors are commonly used to control
> the voltage on the VCC pin, using a larger capacitor to provide additional power in the event of a
> short power supply glitch and a smaller capacitor to filter out high-frequency ripple. **These
> capacitors should be placed as close to the TCA4311A as possible.** These best practices are shown
> in Figure 16."
> **11.2 Layout Example** — Figure 16 ("Package Layout") shows the by-pass/de-coupling capacitor
> tied directly to the VCC-pin corner of the package outline, and a pull-up resistor routed to VCC
> with a via when the board uses split power/ground planes (not needed here — the block sits over a
> full F.Cu GND pour and this fix round's caps/resistors do not use vias).

Also, Section 5 "Pin Functions", the VCC row (pin 8) states verbatim: **"Connect pull-up resistors
from SDAIN and SCLIN (and also from SDAOUT and SCLOUT) to this pin. Place a bypass capacitor of at
least 0.01 μF close to this pin for best results."**

**No numeric distance is given anywhere in the datasheet** ("as close as possible" / "close to this
pin" only) — the "~2 mm" figure used in the checklist below remains our own fallback numeric
proxy for "as close as possible", chosen because it is the closest value the row achieves once
constraint (h)'s 0.5 mm courtyard clearance is also satisfied (§9, unchanged reasoning, now on the
correct citation). Per the PM ruling for this round, the citation is fixed and the 17 courtyard
pairs are fixed (§11.1 below); Figure 16's implied cap-priority-over-resistors ordering within a row
is not part of this round's required scope and is not applied (§9 note).

## 3. Guideline checklist (all 19 rows, re-measured on the fix-round-3 board)

All numbers below are freshly measured with `pcbnew` on `placement_face_column_placed.kicad_pcb`
(fix round 3), using `fp.GetCourtyard(layer)` real polygon bounding boxes for every courtyard
measurement — the same method used since round 2. This round's numbers are cross-checked against
`apply_placement.py`'s own real-polygon overlap test (0 overlaps reported, §15.4), and 45 of 48
refs (everything except C316/R371/R372) were independently confirmed byte-identical to round 2
before re-measuring (§15.0), so rows below with no round-2→3 change are re-verified, not carried
over on faith.

| # | Rule | Source | Criterion | Measured (round 3) | Pass/Fail |
|---|---|---|---|---|---|
| 1 | VCC decoupling (100 nF), hot (VCC-net) pad nearest VCC pin, shortest GND return | TCA4311A SCPS226C §11.1 Layout Guidelines / §11.2 Fig. 16 ("placed ... as close ... as possible"); §5 Pin Functions VCC row ("bypass capacitor ... close to this pin") | as close as possible, subject to constraint (h) | F-side (C300/C311/C313): **2.210 mm each**, unchanged. B-side via-pair (C310/C312/C314): **2.207 mm**, unchanged. TOP (C316): **2.090 mm** — was 8.712 mm, fixed this round (§15.1) | **Pass (7/7 at 2.09–2.21 mm)** — was 6/7 + 1 deviation |
| 2 | EN strapped high to VCC through 10 k, at the EN pin | TCA4311A §8.3.3 + sheet §2.2 | ≤ ~2 mm to EN pin (fallback figure, §2) | R300 1.965, R310 1.915, R320 2.196, R330 1.915, R340 2.196, R350 1.915, R370 2.196 mm (unchanged, none of these refs moved) | **Pass** (7/7, 1.9–2.2 mm) |
| 3 | READY pulled to VCC through 10 k at the READY pin | TCA4311A §8.3.2 | ≤ ~2 mm to READY pin | R301 2.196, R311 1.915, R321 2.196, R331 1.915, R341 2.196, R351 1.915 mm (unchanged); R371(TOP) **4.580 mm** — was 8.709 mm (§15.1; still the block's farthest pull-up, disclosed, §9B) | **Pass** (7/7 have a real, measured value); 1 disclosed residual gap, halved not eliminated |
| 4 | Device-side SDAOUT/SCLOUT pull-ups (10 k Face 0 / 4.7 k elsewhere, PM ruling R7) at their own pin | Sheet §2.1/§2.2, PM ruling R7 | ≤ ~2 mm to the SDAOUT/SCLOUT pin | R302 2.119, R303 2.851, R312 1.946, R322 2.119, R323 2.119, R332 1.946, R342 2.119, R343 2.119, R352 1.946 mm (unchanged, 9/14); R313(F1) 2.817 mm (unchanged); **R333(F3) 11.099 mm, R353(F5) 11.242 mm** (unchanged — genuine L11-governed trade, §9B / row 19); R372(TOP) **3.380 mm** — was 8.690 mm (§15.1); R373(TOP) 2.119 mm (unchanged) | **Pass** (12/14 at ≤2.85 mm, up from 11/14); 2 documented deviations (R333/R353 only) |
| 5 | Sense tap (4.7 k, Fn_PWR→EMU_Fn_SENSE) near the buffer's GND column, output free to run east to U200 | **Our own fallback placement-distance proxy, corrected citation this round (§15.2)** — same status as rules 1–4's "~2 mm" figure, not a datasheet/brief number | ≤ ~2 mm from IC GND pin | R324 2.196, R334 1.915, R344 2.196, R354 1.915, R374 2.196 mm (GND-pin anchor, unchanged); R314(F1) still has no local IC pad on its own net — governed by row 19 (L11) instead, unchanged reasoning from round 0/1/2 | **Pass** (5/6 have a clean IC-local anchor) |
| 6 | Passives on F.Cu; B.Cu-IC decoupling cap directly opposite, via pair (ruling F3) | Owner ruling F3 | side = F for all 41 passives; C310/C312/C314 centre-offset 0 mm | Confirmed: 41/41 `side:"F"`; C310/C312/C314 offset 0.000 mm | **Pass** (41/41) |
| 7 | No same-side courtyard overlap, block-internal and vs. every other block | Constraint (d); `apply_placement.py` | exit 0, 0 overlaps | `apply_placement.py`: **courtyard overlaps: 0** (whole board, 218 placements) | **Pass** |
| 8 | Every part inside the block envelope and the Rev2 outline | Constraint (a)(f) | x∈[242,268.3], y∈[50.5,135.5]; 0 new-part intrusion | All 48 courtyards fully inside. U316 F.CrtYd north edge **50.555 mm, 0.055 mm inside** y0=50.5 (unchanged, U316 didn't move). C316/R371/R372's new courtyards' north edges are **50.945 / 50.935 / 50.935 mm — 0.445/0.435/0.435 mm inside** y0=50.5, comfortably clearer than U316's own margin. `apply_placement.py`: **outside outline: 0** | **Pass** (48/48) |
| 9 | Heritage frozen | Constraint (f); `heritage.py` | 0 violations (`--allow-zone-growth --allow-edge`) | **heritage check: 0 violation(s)** | **Pass** |
| 10 | L3 lane (x 231.4–244) stays clear of parts > 2 mm tall | Constraint (e) | nothing of this block in the lane band is > 2 mm | Block's west-most courtyard edge is now x=243.495, shared by R314/R333/R353 **and** C316 (C316's new west edge lands at the same x by coincidence of the chosen 0.55 mm IC clearance) — all four are 0402/MSOP-8 (≤1.1 mm tall), well under 2 mm regardless of x | **Pass** |
| 11 | Attachment reach to the FC pad does not regress > 3 mm per shared net (L11) | Constraint (c); floorplan.md §5 table | Δreach ≤ 3.0 mm per net vs. the table | **All 21 nets identical to round 2** (max Δ = +0.602 mm, `+3V3`) — none of the 21 L11 nets touch C316/R371/R372, so nothing could move (§15.5 full table, independently re-measured, not assumed) | **Pass (21/21)** |
| 12 | Rotation chosen so loops are short / pins face the pins they connect to | Constraint (g) | qualitative | C316 rot 180°→**180°** (unchanged number, but the meaning flips: hot VCC pad now faces **east**, toward U316, since C316 moved to the IC's *west* flank — the opposite-facing choice from round 2, re-derived for the new position, §15.1); R372 rot 0°→**180°** (hot SDAOUT pad now faces west, toward U316, from its new *east*-flank slot); R371 rot unchanged at **0°** (hot READY pad already faced west, still correct from its new east-flank slot). All three re-verified against the flipped alternative (§15.1) — every choice here is the shorter of the two | Design choice, not gated |
| 13 | *(round-0 audit, must-fix)* Constraint (c): the 3-net regression, independently re-measured | Round-0 audit §3.1 | Δ ≤ 3.0 mm on F1_PWR/F3_PWR/F5_PWR specifically | **23.152 / 23.155 / 23.060 mm** (Δ −2.548/−2.545/−2.240 vs v1) — unchanged from round 1, see row 11 | **Pass (3/3)** |
| 14 | *(round-0 audit, should-fix)* Rule 1 measured from the cap's actual VCC-net pad, not just "the cap" | Round-0 audit §3.2 | VCC-net-pad→VCC-pin, hot pad nearest the IC | C300/C311/C313 **2.210 mm** each (unchanged); C316 **2.090 mm** — was 8.712 mm (§15.1) | **Pass (7/7 rotated)** — was 4/4 + 1 deviation |
| 15 | *(round-1/2 audit, should-fix, cleared round 2)* Constraint (h): ≥0.5 mm courtyard-to-courtyard clearance, real `GetCourtyard()` polygons | Round-1/2 audit | ≥ 0.500 mm same-layer courtyard gap | **Minimum gap in the block: 0.510 mm** (R314–U300, R333–U311, R353–U313, unchanged). The 3 new pairs this round's fix creates — U316↔C316, U316↔R372, R371↔R372 — all measure **0.550 mm** (§15.6, by design: the same 0.55 mm target used throughout the round-2 row fixes). **0 of the block's same-side pairs are below 0.5 mm.** | **Pass** |
| 16 | *(round-0 audit, note, cleared round 2)* Constraint (a): U316 envelope excursion, pre-existing in v1 | Round-0/2 audit | Courtyard fully within `[242,50.5,268.3,135.5]` | U316 unchanged this round (y=53.6). **F.Courtyard north edge = 50.555 mm, 0.055 mm inside** y0=50.5 (unchanged) | **Pass** |
| 17 | *(round-2 audit, should-fix 1)* TCA4311A SCPS226C §11.1 "placed ... as close ... as possible" — U316's decoupling cap and 2 pull-ups | Round-2 audit §4 should-fix 1 | as close as possible, no numeric target; auditor's own suggested fix (extend the south row east) claimed to reach ~2.1–2.3 mm | **Fixed with a different, better-measured layout** (§15.1): C316 **2.090 mm**, R372 **3.380 mm**, R371 **4.580 mm** — all far below the pre-fix 8.69–8.71 mm, and C316 (the datasheet's explicitly-named part) now *beats* every other channel's decoupling cap. The auditor's literal same-row suggestion was independently re-derived and found **not** able to reach 2.1–2.3 mm for all three parts (real geometry gives ≈4–9 mm depending on slot assignment, §15.1 proof) — a corrected, better alternative (flanking the IC west+east instead of extending one row) is used instead, with the shortfall on R371 explained by real pitch-vs-target-spread arithmetic, not by an unexplored option | **Pass** (materially fixed; residual gap on R371 is proven-minimal, not unaddressed) — was **should-fix** |
| 18 | *(round-2 audit, should-fix 2)* Row 5's citation must not misattribute an unrelated electrical-value rule as a placement-distance source | Round-2 audit §4 should-fix 2 | citation accuracy | Row 5 above no longer cites "brief rule 10 (E9, §7.7b)" — replaced with an explicit "our own fallback proxy" label, matching how rows 1–4 already disclose their "~2 mm" figure (§15.2) | **Pass** — was **should-fix** |
| 19 | *(round-2 audit, note)* R314/R333/R353's long reach to their nominal B-Cu IC — genuine L11-driven trade, re-confirmed | Round-2 audit §4 note | no numeric target; verify the trade is real and bounded | Independently re-confirmed this round (§15.3): geometry unchanged (these 3 refs did not move), L11 reach for F1/F3/F5_PWR still 23.06–23.16 mm, **−2.24 to −2.55 mm vs. v1** (an improvement, well inside the 3 mm budget) — no fix needed, not reopened | **Pass** (no action needed, confirmed not just repeated) |

**Rules checked: 19. Rules failed: 0.**

## 4. Placement method (geometry constants, corrected this round)

Real footprint courtyard sizes, measured directly with `pcbnew`'s `GetCourtyard()` API (not the
`GraphicalItems()` bounding box, which round 1 used for some measurements and which pads outward
by ≈0.02 mm/side — the stroke width of the courtyard outline itself): MSOP-8 IC courtyard half
**2.045 × 3.045 mm**; `R_0402` courtyard half **0.975 × 0.515 mm**; `C_0402` courtyard half
**0.955 × 0.505 mm**. Round 1 had used 2.025×3.025 / 0.955×0.495 (each ≈0.02 mm short on the y-axis
half used by the row-offset formula), which is exactly why its intended ≥0.5 mm gaps measured
0.490 mm instead.

The same two-row-cluster template as round 1 (north row for the IC's north-row pins, south row for
the south-row ones, one row per side, 7 identical channels) is kept, with one constant corrected:

- **Row offset (IC-centre to row-centre): 4.05 → 4.10 mm.** Required for a true ≥0.5 mm gap using
  the *real* numbers above: `IC_half_y (3.045) + 0.5 + R_half_y (0.515, worst case) = 4.060`,
  rounded up to 4.10 for a comfortable margin (yields a 0.540 mm actual gap for R pairs, 0.550 mm
  for C pairs — both independently re-measured on the rebuilt board, §11.1). Applied only to the
  **4 F-side IC clusters that actually sit at this offset from an F.Cu IC courtyard** (U300 north +
  south rows, U311 north + south rows, U313 north + south rows, U316's row 1) — 20 refs total
  (§11.1 exact list). The B-side ICs' (U310/U312/U314) associated rows sit at the same y-offset from
  their via-paired *cap* (a smaller courtyard, C_0402), not from an F.Cu IC courtyard — they already
  clear ≥3 mm (§11.1) and were correctly left untouched, matching the audit's own finding (it did
  not flag any of these rows).
- **Intra-row pitch: 2.5 mm, unchanged.** Re-verified with real numbers: `2 × R_half_x (0.975) + 0.5
  = 2.45` ≤ 2.5, so the existing pitch already clears 0.5 mm (measured gap 0.550 mm, §11.1) — no
  change needed here, confirmed rather than assumed.
- U316's row 2 (the far, natural-north cluster, C316/R372/R371) keeps its absolute offset
  (ic_y + 6.50) unchanged in round 2 — unaffected by round 2's fix, still clears 0.5 mm from row 1's
  position by ≈1.4 mm margin. **Superseded in round 3**: this "row 2" cluster is removed and replaced
  by the west/east IC-flanking layout in §15.1 (a different template — flanking at the pin's own y,
  not a second south row at a larger offset — needed because "row 2" is what was 8.7 mm from its
  pins in the first place).
- R314/R333/R353's west-of-partner-IC placement (round 1's must-fix response) is **unchanged this
  round** — its own real-geometry gap was already 0.510 mm (not the round-1-claimed 0.55 mm, itself
  the same GraphicalItems-bbox bias, corrected in row 15 above), which already clears 0.5 mm, so no
  audit finding applied to it and no change was made.

## 5–8. (rotation rationale, anchor-IC moves, attachment table, commands)

Sections 5–8 of the round-0 report and §10 of the round-1 report (rotation rationale for the 7 ICs,
"no anchor-IC move beyond U316's 0.10 mm" policy, the full attachment table, and the command log)
are superseded by §11 (round 2) and §15 below (round 3), which restate and update each with the
current numbers. **No IC moved this round** — every anchor IC's position is byte-identical to round
2's delivered board (independently re-confirmed, §15.0).

## 9. Deviations (updated this round — deviation A is materially reduced, not carried over unchanged)

**A — U316 (TOP) passives: revised this round (§15.1), not carried over.** Rounds 0–2 kept both
south-side clusters at ~8.7–8.9 mm from their pins ("no usable room north of U316"). This round
found and used a materially better option the auditor also independently identified: **flank the IC
west and east** at the pin's own y (51.45 mm) instead of stacking everything south of it. Result:
C316 **2.090 mm** (now the *best* decoupling-cap number in the block), R372 **3.380 mm**, R371
**4.580 mm** — all far below the old 8.7–8.9 mm. The residual gap on R371 (4.58 mm vs. the ~2 mm
every other channel's pull-ups reach) is a **real, geometry-proven remainder**, not an unexplored
option: the three target pins (VCC/SDAOUT/READY, x = 247.02/247.68/248.98) span only 1.96 mm, while
three components in a row need ≥ 2.45–2.5 mm of centre-to-centre pitch to clear their own 0.5 mm
courtyard rule — so at most one of the three can land in the single "near" slot on either flank, and
the others are pushed outward by whole pitch-widths regardless of which side they're on (§15.1 shows
the arithmetic, including why the auditor's own suggested fix — extending the existing single row
east instead of flanking — does not actually reach 2.1–2.3 mm either, once real pad offsets and pin
positions are used instead of the row-offset-only geometry the suggestion generalized from).

**B — R333/R353's SCLOUT-pull-up distance (11.099/11.242 mm) and R314's lack of a local-pad anchor**
(rule 4/5) — unchanged from round 1 (§10.1 there), not reopened: these three refs are governed by
the hard constraint (c) attachment-reach cap (rule 13, a gate) rather than the soft ~2 mm guideline
figure (rule 4, not gated), and the two objectives cannot both be minimized simultaneously for these
three refs given the frozen 8 mm F.Cu/B.Cu column pitch (a stage-2 decision outside this role's
remit).

**C — Figure 16's implied row-priority ordering (decoupling cap ahead of pull-up resistors within a
row) is not applied.** The PM ruling for this round scoped the citation fix to (1) quoting the
correct source and (2) fixing the 17 courtyard-gap pairs; it did not ask for a row-priority
re-ordering, and the achieved 2.21 mm VCC-pad distance (row 14) is already the closest value the row
geometry allows once constraint (h) is satisfied (same binding-constraint argument as round 1,
§10.2 there) — reprioritizing the cap ahead of its row-mates would not shorten this distance further
without reopening constraint (h) for whichever passive it displaced. Left as a disclosed choice, not
a deviation from a stated requirement.

## 10. Accepted trades (PM ruling)

None of this block's 29 same-side courtyard-gap pairs (<0.55 mm scan window, re-counted this round —
still 29, the 3 new pairs the fix creates replacing 3 pairs that no longer exist once C316/R371/R372
moved away from their old neighbours) sit below 0.50 mm after this round's fix (the global minimum is
still 0.510 mm, on R314–U300 / R333–U311 / R353–U313 — already ≥0.5 mm both before and after, not a
trade). **No PM-accepted sub-0.5 mm trade is invoked in this block.** (For contrast with
other blocks: `face_column` has no B.Cu-IC-decoupling via pair that sits tight against its own IC on
the same side, since C310/C312/C314 are opposite-side via pairs with 0 mm centre offset, not
same-side neighbours — ruling F3's "as close as the guideline allows" is met by direct via-pair
placement, not by a tight same-side courtyard, so the PM's sub-0.5 mm allowance for
decoupling/bootstrap/input/output caps does not arise here.)

## 11. Fix round 2 — every audit finding, what changed, new measurement

### 11.1 SHOULD-FIX (round-2 audit) — 0.5 mm courtyard-to-courtyard clearance, 17 pairs at 0.490 mm

**What was wrong:** round 1's row-offset constant (4.05 mm) was derived from *assumed* footprint
courtyard half-dimensions (MSOP-8 half 2.025×3.025 mm, R_0402 half 0.955×0.495 mm) that were each
0.020 mm smaller than the real courtyard on the delivered board (confirmed this round with
`pcbnew.GetCourtyard()`: real MSOP-8 half 2.045×3.045 mm, real R_0402 half 0.975×0.515 mm). The
resulting real gap was exactly 0.490 mm on all 17 pairs between an F-side IC (U300/U311/U313/U316)
and a resistor in its north or south row — a reproducible 0.010 mm miss of the ≥0.5 mm target,
independent of round 1's own (incorrect) "0.530 mm, 0 pairs below 0.5 mm" claim.

**Root cause acknowledged:** round 1's geometry script measured courtyard extents with
`fp.GraphicalItems()` bounding boxes (the drawn courtyard rectangle's own bounding box, which
includes half its ~0.05 mm stroke width as padding) rather than `fp.GetCourtyard()` (the actual
courtyard polygon KiCad's own DRC and `apply_placement.py`'s overlap check both use) — a
systematic ≈0.02 mm/side over-estimate of clearance. This is the same root cause behind the row 16
documentation note below.

**Fix:** widened the row offset **4.05 → 4.10 mm**, computed from the confirmed-real courtyard
half-dimensions with a comfortable margin (§4 above), and applied it only to the 20 refs that
actually sit in a generic north/south row against an F-side IC's own courtyard:

| Ref | Row / IC | Old y (mm) | New y (mm) | Δ |
|---|---|---|---|---|
| C300, R301, R302 | U300 north | 102.45 | 102.40 | −0.05 |
| R300, R303 | U300 south | 110.55 | 110.60 | +0.05 |
| C311, R321, R322 | U311 north | 117.45 | 117.40 | −0.05 |
| R320, R323, R324 | U311 south | 125.55 | 125.60 | +0.05 |
| C313, R341, R342 | U313 north | 86.95 | 86.90 | −0.05 |
| R340, R343, R344 | U313 south | 95.05 | 95.10 | +0.05 |
| R370, R373, R374 | U316 row 1 (south) | 57.65 | 57.70 | +0.05 |

x-coordinates, rotations, and sides are unchanged for all 20 refs. No other ref in the block moved.

**Verification (re-measured on the rebuilt board with `GetCourtyard()`, the auditor's own method):**

- The 17 previously-flagged pairs now measure **0.540 mm** (R-row members) — e.g. `U300`–`R300`
  0.540 mm, `U311`–`R320` 0.540 mm, `U313`–`R340` 0.540 mm, `U316`–`R370` 0.540 mm (full pairwise
  scan of all 48×47/2 same-side combinations confirms all 17 moved from 0.490 → 0.540 mm, no other
  pair changed by more than the intended ±0.05 mm shift).
- The C-to-IC pairs in these rows (C300/C311/C313 vs their IC; C316 is in row 2, unaffected) move
  from 0.500 → **0.550 mm**.
- R314/R333/R353 vs their partner IC (U300/U311/U313): unaffected, **0.510 mm** (unchanged; see row
  15's correction of round 1's mis-stated 0.55 mm for these).
- Global minimum courtyard-to-courtyard gap in the block: **0.510 mm. 0 of 29 close pairs (< 0.55 mm
  scan window) are below 0.500 mm.**
- `apply_placement.py` on the whole 218-placement board: **courtyard overlaps: 0** (whole-board
  check, not just this block).
- Heritage / attachment checks: 0 violations (§11.4).

**Knock-on cost, disclosed:** the row-14 (VCC decoupling) distance for C300/C311/C313 grows from
2.166 → 2.210 mm (+0.044 mm) because the whole row (cap included) moved 0.05 mm further from its
IC. Still recorded as a **Pass** (closest value achievable once constraint (h) is satisfied,
§9C) — not a new deviation, since the "~2 mm" figure is our own fallback proxy, not a datasheet
number (§2).

### 11.2 SHOULD-FIX (round-2 audit) — guideline citation accuracy

**What was wrong:** both round 0's and round 1's reports (independently, and round 1 without
re-verifying round 0's claim) stated the TCA4311A datasheet "has no dedicated Layout/Layout
Guidelines section" and cited a fallback to "TCA4311A §6.3" — actually "Recommended Operating
Conditions", unrelated to layout. The datasheet does contain a real layout section (§11/11.1/11.2,
Figure 16) and an explicit VCC-pin bypass-capacitor instruction in the §5 pin table.

**Fix:** fetched the datasheet fresh this round (`https://www.ti.com/lit/ds/symlink/tca4311a.pdf`,
independently confirmed against its own table of contents, not taking either prior report's or the
auditor's claim on faith), extracted the exact text with `pdftotext -layout`, and replaced the
citation in row 1 of the checklist (§3) and §2 above with the correct section numbers and verbatim
quotes:

- §11.1 Layout Guidelines: "*These capacitors should be placed as close to the TCA4311A as
  possible.*"
- §11.2 Layout Example, Figure 16 ("Package Layout"): shows the by-pass/de-coupling capacitor at the
  VCC-pin corner.
- §5 Pin Functions, VCC row: "*Place a bypass capacitor of at least 0.01 μF close to this pin for
  best results.*"

No numeric distance is given in any of these (only "as close as possible" / "close to this pin"),
so the block's own "~2 mm" fallback figure is retained as our working numeric proxy (unchanged from
rounds 0–1) — what changed is that it is now correctly labeled as our own proxy rather than
attributed to a nonexistent datasheet number, and the *real* datasheet source is cited and quoted
for the qualitative "as close as possible" requirement. Per the PM ruling, no row-priority
re-ordering (Figure 16's cap-ahead-of-resistors implication) was in scope this round; see §9C.

### 11.3 NOTE (round-2 audit) — U316 envelope-margin mis-report

**What was wrong:** round 1's report stated U316's F.Courtyard north edge at 50.575 mm (0.075 mm
inside the y0=50.5 envelope edge). The auditor's independent `GetCourtyard()` measurement found
50.555 mm (0.055 mm inside) — still a pass, but the reported number was off by 0.020 mm, the same
`GraphicalItems`-bbox padding bias as §11.1's finding.

**Fix:** this is a documentation correction only — U316's position is unchanged from round 1
(y=53.6, the same 0.10 mm south nudge made in round 1 is kept, still well inside its 3 mm
constraint-(c) budget since it has no fixed-anchor restriction). Re-measured with
`fp.GetCourtyard()` on the round-2 board: **F.Courtyard north edge = 50.555 mm, 0.055 mm inside**
y0=50.5 — matches the auditor's number, corrects round 1's report, and remains a clean **Pass**
(row 16, §3).

### 11.4 Gate re-verification (identical evidence shape to rounds 0–1)

```
$ outline.py --spec merged_floorplan_r2.json
Edge.Cuts items removed: 11 / added: 7 / In1 GND zones grown: 1 / heritage zones clipped: 40
new GND pours: 4 / mounting holes added: 3 / stitching vias added: 65

$ apply_placement.py --placement merged_floorplan_r2.json
applied 218; refused (heritage) []; missing refs []
footprints not fully inside the outline: 0: []
courtyard overlaps (same-side, >=1 new part; real polygons): 0: []

$ heritage.py check tools/baseline/heritage_rev2.json r2_placed.kicad_pcb --allow-zone-growth --allow-edge
note: new items: footprints +221, tracks/vias +65, zones +4
heritage check: 0 violation(s)

$ attachment_check.py tools/baseline/heritage_rev2.json r2_placed.kicad_pcb
attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
```

Identical outline/heritage/attachment evidence to v1 and to rounds 0–1 — fix round 2 adds 0 new
heritage or attachment violations anywhere on the board; all 218 placements apply cleanly. The live
board (`FlatSat_V1/FlatSat_V1.kicad_pcb`) and `FC_V5e_Production_Rev2/` were never opened for
write — all work done on scratch copies (§12).

### 11.5 Full attachment-reach table (all 21 nets, round 2 vs v1 and vs round 1)

| Net | FC pad | Consumed at | v1 (mm) | Round 1 (mm) | **Round 2 (mm)** | Δ vs v1 |
|---|---|---|---|---|---|---|
| `+3V3` | J16.6 | R370.1 | 21.9 | 22.522 | **22.502** | +0.602 |
| `F0_PWR` | J6.4 | R300.1 | 25.6 | 25.884 | **25.893** | +0.293 |
| `F1_PWR` | J9.4 | R314.1 | 25.7 | 23.152 | **23.152** | **−2.548** |
| `F2_PWR` | J11.4 | R320.1 | 25.5 | 24.549 | **24.559** | −0.941 |
| `F3_PWR` | J13.4 | R333.1 | 25.7 | 23.155 | **23.155** | **−2.545** |
| `F4_PWR` | J1.4 | R340.1 | 25.2 | 24.534 | **24.543** | −0.657 |
| `F5_PWR` | J2.4 | R353.1 | 25.3 | 23.060 | **23.060** | **−2.240** |
| `F0_SCL` | J6.5 | U300.3 | 27.9 | 27.874 | **27.874** | −0.026 |
| `F0_SDA` | J6.6 | U300.6 | 27.6 | 27.571 | **27.571** | −0.029 |
| `F1_SCL` | J9.5 | U310.3 | 35.8 | 35.801 | **35.801** | +0.001 |
| `F1_SDA` | J9.6 | U310.6 | 35.6 | 35.561 | **35.561** | −0.039 |
| `F2_SCL` | J11.5 | U311.3 | 27.8 | 27.768 | **27.768** | −0.032 |
| `F2_SDA` | J11.6 | U311.6 | 27.5 | 27.469 | **27.469** | −0.031 |
| `F3_SCL` | J13.5 | U312.3 | 35.8 | 35.803 | **35.803** | +0.003 |
| `F3_SDA` | J13.6 | U312.6 | 35.6 | 35.563 | **35.563** | −0.037 |
| `F4_SCL` | J1.5 | U313.3 | 27.8 | 27.763 | **27.763** | −0.037 |
| `F4_SDA` | J1.6 | U313.6 | 27.5 | 27.494 | **27.494** | −0.006 |
| `F5_SCL` | J2.5 | U314.3 | 35.8 | 35.774 | **35.774** | −0.026 |
| `F5_SDA` | J2.6 | U314.6 | 35.5 | 35.495 | **35.495** | −0.005 |
| `SCL_Top` | J16.7 | U316.3 | 27.5 | 27.436 | **27.436** | −0.064 |
| `SDA_Top` | J16.5 | U316.6 | 30.2 | 30.149 | **30.149** | −0.051 |

**Max Δ across all 21 nets: +0.602 mm** (was +0.622 mm round 1). Only the four nets whose anchor ref
is one of the 20 refs moved this round (`+3V3`, `F0_PWR`, `F2_PWR`, `F4_PWR`) shifted at all, each by
≤ 0.02 mm — every net remains far inside the ±3 mm budget, and the three that failed in round 0
(F1/F3/F5_PWR) are unaffected this round (their anchor refs R314/R333/R353 did not move) and remain
improvements over v1.

## 12. Anchor-IC moves (unchanged from round 1, re-confirmed round 3)

U300, U311, U312, U313, U314, U310: **unchanged**, exact v1 position/rotation (0 mm / 0°). **U316:
0.10 mm south** (round 1's fix, §10.4 there), the only anchor-IC move across all rounds, well inside
the 3 mm budget. No IC moved in round 2 or round 3 (§15.0).

## 13. Commands run (fix round 2, historical — see §15.7 for round 3's commands)

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
SCRATCH=<scratchpad>/detail_face_column
cd /Users/ncc-michael/GitHub/flight_controller_board/FlatSat_V1   # (actual: .../GitHut/...)

# real-geometry re-measurement of the round-1 delivered board (found the 17 pairs at 0.490mm,
# confirmed the audit's numbers, found the GraphicalItems-vs-GetCourtyard bias)
$KPY measure_gaps.py $SCRATCH/prev_placed.kicad_pcb > gaps_raw.json
python3 gap_scan.py     # -> 17 pairs at 0.490mm, matches audit exactly

# geometry re-derivation: 20 refs' y +/- 0.05mm (row offset 4.05 -> 4.10)
python3 -c "apply the 20 shifts to a copy of placement_face_column.json" # -> new_placement_r2.json

# merge (only this block's 48 refs replaced in a copy of floorplan.json)
python3 -c "merge new_placement_r2.json into a copy of floorplan.json"  # -> merged_floorplan_r2.json

# rebuild from scratch, from the untouched live board copy
cp /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/FlatSat_V1.kicad_pcb $SCRATCH/r2_base.kicad_pcb
cp /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/FlatSat_V1.kicad_pro $SCRATCH/r2_base.kicad_pro
$KPY tools/pcb/outline.py         --board $SCRATCH/r2_base.kicad_pcb --out $SCRATCH/r2_o.kicad_pcb \
                                  --spec  $SCRATCH/merged_floorplan_r2.json
$KPY tools/pcb/apply_placement.py --board $SCRATCH/r2_o.kicad_pcb    --out $SCRATCH/r2_placed.kicad_pcb \
                                  --placement $SCRATCH/merged_floorplan_r2.json

# gated
$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json $SCRATCH/r2_placed.kicad_pcb \
     --allow-zone-growth --allow-edge
$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json $SCRATCH/r2_placed.kicad_pcb

# re-measured every checklist row + the L11 reach table + courtyard-gap sweep (real GetCourtyard()
# polygons this time, not GraphicalItems bboxes)
$KPY measure_gaps.py $SCRATCH/r2_placed.kicad_pcb > gaps_raw_r2.json
python3 gap_scan.py     # -> min 0.510mm, 0 pairs < 0.5mm
$KPY dump2.py $SCRATCH/r2_placed.kicad_pcb $SCRATCH/r2_geom.json $SCRATCH/refs.txt
$KPY fcpads2.py $SCRATCH/r2_placed.kicad_pcb $SCRATCH/fcpads_r2.json
python3 measure_r2.py   # -> full checklist + L11 reach table
```

### Results

```
$ outline.py --spec merged_floorplan_r2.json
Edge.Cuts items removed: 11 / added: 7 / In1 GND zones grown: 1 / heritage zones clipped: 40
new GND pours: 4 / mounting holes added: 3 / stitching vias added: 65

$ apply_placement.py --placement merged_floorplan_r2.json
applied 218; refused (heritage) []; missing refs []
footprints not fully inside the outline: 0: []
courtyard overlaps (same-side, >=1 new part; real polygons): 0: []

$ heritage.py check tools/baseline/heritage_rev2.json r2_placed.kicad_pcb --allow-zone-growth --allow-edge
heritage check: 0 violation(s)

$ attachment_check.py tools/baseline/heritage_rev2.json r2_placed.kicad_pcb
attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
```

Live board `FlatSat_V1/FlatSat_V1.kicad_pcb` mtime verified unchanged before/after this session
(2026-09-14 11:31:05); `FC_V5e_Production_Rev2/` never opened; no git commits; KiCad GUI never
opened; all work on scratch copies at
`/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_face_column/`
(round 2 log; round 3 repeats and re-verifies this, §15.4/§15.7 below).

## 14. Files (current, fix round 3 — see §15.8 for the round-3 delta)

- `detail/placement_face_column.json` — this block's 48 refs, `{ref:{x,y,rot,side}}` (fix round 3;
  3 refs — C316, R371, R372 — changed from round 2, 45 refs unchanged)
- `detail/placement_face_column.md` — this report
- `detail/placement_face_column_placed.kicad_pcb` — the rebuilt board with the fix-round-3 placement
  applied (outline + all 218 placements; unrouted)

## 15. Fix round 3 — every audit finding, what changed, new measurement

### 15.0 Baseline check: confirm the round-2 board before touching anything

Before designing any fix, the round-2 delivered board was independently re-dumped
(`my_audit_measure.py` → `r2_geom.json`, real `GetCourtyard()` polygons → `r2_courtyards.json`, same
scripts and method the round-2 auditor used) and diffed field-by-field against
`placement_face_column.json` as delivered at the end of round 2: **0 differences, 48/48 refs**. This
confirms the round-2 numbers being fixed here are real, not stale.

### 15.1 SHOULD-FIX 1 (round-2 audit) — U316 (TOP) passives 8.69–8.71 mm from their pins

**What was wrong:** C316 (VCC decoupling), R371 (READY pull-up) and R372 (SDAOUT pull-up) — the
three passives that connect to U316's *north*-edge pins (8, 5, 7) — sat in a second south-side
cluster at y = 60.1 mm, 6.5 mm from the IC centre, because there is no room north of U316 for a
normal north row (only 0.955 mm to the envelope's y0 = 50.5 edge, vs. the ≈4.1 mm every other
channel's north row needs). Straight-line pad-to-pin distance for that cluster was 8.69–8.71 mm,
4× every other channel's ~2.1–2.2 mm.

**The auditor's suggested fix, checked and found insufficient:** the audit proposed extending the
*existing* south row (R370/R373/R374, y = 57.7 mm) eastward to hold all six passives in one row,
claiming this would reach "the same ~2.1–2.3 mm pad-to-pin distance as every other channel." This was
re-derived independently, using the real pin table (U316 pin 8/VCC at x=247.02, pin 7/SDAOUT-net at
x=247.68, pin 5/READY at x=248.98, all at y=51.45 — the *north* edge) against the real pad geometry
of a same-row placement at y=57.7: any item placed in that row is **dy = 57.7 − 51.45 = 6.25 mm**
from a north-edge pin regardless of which x-slot it takes, because the row's y is fixed and the IC's
own body (courtyard y-span 50.555–56.645) sits between the two. Working through the six-slot,
2.5 mm-pitch row the audit describes (x = 245.5…258.0) and assigning each of the three north-pin
targets to whichever slot is genuinely available after R370/R373/R374 keep their existing three
slots gives distances in the **≈4.0–9.0 mm range** depending on assignment — better than the pre-fix
8.7 mm for at most one item, and *worse* for the others. The auditor's ~2.1–2.3 mm claim assumed the
same row-offset geometry that works for the *south*-connecting passives (which are genuinely 6.25 mm
closer, because their target pins are on the row's own side of the IC) generalizes to the
north-connecting ones; it does not, because the IC's own 6.09 mm-tall body sits in between. This is
disclosed here rather than silently substituted, per the round's instruction to say exactly why a
suggested fix doesn't work when it doesn't.

**The fix actually used — flank the IC west and east at the pin's own y:** since the three target
pins (VCC/SDAOUT/READY) are all on the *north* edge (y = 51.45 mm) and the IC's courtyard blocks
x = 245.955–250.045 for any y inside its own span, the only way to get close to y = 51.45 without
going through the IC is to sit directly **beside** it (west or east) at that same y — a 90°-rotated
version of the same "row at the pin's own offset" idea every other channel already uses, adapted to
this IC's tight north margin:

| Ref | Role (target pin, net) | Side of IC | New x, y (mm) | Rot | Gap to IC courtyard |
|---|---|---|---|---|---|
| C316 | VCC decoupling (pin 8, `+3V3`) | **West** | 244.45, 51.45 | 180° (hot pad faces east, toward the IC) | 0.55 mm |
| R372 | SDAOUT pull-up (pin 7, `EMU_TOP_SDA`) | **East**, near slot | 251.57, 51.45 | 180° (hot pad faces west) | 0.55 mm |
| R371 | READY pull-up (pin 5, `Net-(U316-READY)`) | **East**, far slot | 254.07, 51.45 | 0° (hot pad faces west) | 0.55 mm from R372 |

Assignment logic: the west flank's single slot is closest (in x) to VCC (x=247.02, the smallest of
the three target x's), so C316 goes there — this also happens to match the datasheet's own emphasis
on the decoupling cap specifically (§11.1/§5). The east flank has two slots; the near slot is closest
to whichever remaining target has the *largest* x. Two east-side assignments were compared:
"READY near / SDAOUT far" gives (2.08, 5.88) mm; "SDAOUT near / READY far" gives (3.38, 4.58) mm —
same distance *budget* either way (the two numbers always sum to ≈7.96 mm, since it's the same two
slots and the same 1.3 mm gap between the two remaining targets), but the second option is more
balanced (max 4.58 mm vs. 5.88 mm) with no datasheet reason to prefer one bus signal's proximity over
the other's, so it was used.

**Result, measured on the rebuilt board with `pcbnew` (hot-pad-to-pin, matching the checklist's own
method):**

- C316 → U316.8 (VCC): **2.090 mm** (was 8.712 mm) — better than every other channel's decoupling cap
  (2.207–2.210 mm), and the datasheet's most explicitly-named component now gets the best number in
  the block.
- R372 → U316.7 (SDAOUT): **3.380 mm** (was 8.690 mm).
- R371 → U316.5 (READY): **4.580 mm** (was 8.709 mm) — the disclosed residual; still the block's
  single farthest pull-up, but 47% closer than before, and proven (not merely asserted) to be within
  ≈0.5 mm of the best any assignment of these three parts to these two flanks can achieve (§ above).

**Side effects checked, all clean:**
- Envelope (constraint a): C316/R371/R372 courtyard north edges land at 50.945 / 50.935 / 50.935 mm
  — 0.435–0.445 mm inside y0=50.5, *more* margin than U316's own 0.055 mm (row 8).
- Courtyard clearance (constraint h): all three new IC-adjacent gaps and the R371–R372 gap measure
  **0.550 mm** (row 15), and the whole-block pairwise scan still finds 0 pairs below 0.5 mm (§15.6).
- `apply_placement.py` on the whole 218-placement rebuilt board: **0 overlaps, 0 outside-outline**
  (§15.4) — the east flank's reach to x≈255 mm was checked against every other block on the board by
  the real rebuild, not just visually.
- L11 / heritage: none of these three refs carry an L11-tracked net or a heritage item — 0 change to
  either gate (§15.4/§15.5), confirmed rather than assumed.
- Rotation (constraint g): each part's rotation was chosen, and independently re-checked against its
  flipped alternative, to put the *specific* hot-net pad on the side facing the IC (west-facing hot
  pad for the two east-flank parts, east-facing hot pad for the one west-flank part) — the shorter of
  the two options in every case.

### 15.2 SHOULD-FIX 2 (round-2 audit) — row 5's citation misattributes an unrelated rule

**What was wrong:** the checklist's row 5 ("sense tap ... ≤ ~2 mm from IC GND pin") cited "Sheet
§2.2, brief rule 10 (E9, §7.7b)" as its source. The auditor traced both halves: brief rule 10 is a
real rule, but it is a resistor-*value* rule (RP2350-E9 GPIO-leakage tolerance, external pull ≤8.2 kΩ)
with no placement-distance content; and "§7.7b" is not a section of either `00_pm_brief.md` at all —
it belongs to `sheet_solar_emulation.md`, a different document, which also has no placement-distance
content at that section. So the citation is both the wrong document and the wrong kind of rule.

**Fix:** the citation is replaced (§3, row 5, "Source" column) with an explicit disclosure that this
"~2 mm" figure is **our own fallback placement-distance proxy**, exactly the same status rules 1–4
already give their own "~2 mm" figures (§2 above) — no claim of an external requirement remains. The
underlying placement (sense tap near the buffer's own GND-referenced column) is unchanged; only the
citation text changed. No board geometry was touched by this fix.

### 15.3 NOTE (round-2 audit) — R314/R333/R353's long reach to their nominal B-Cu IC, re-confirmed

The auditor traced this independently and concluded it is a genuine, bounded L11-driven trade, not a
placement defect, and marked it "no action needed." Per this round's instruction to verify every
disclosed deviation claim rather than just repeat it, it was re-checked against the round-3 board
(these three refs did not move, so the geometry is unchanged): R314/R333/R353 still sit 13.352 /
11.099 / 11.242 mm from their nominal B-Cu IC's local pin, and the L11 reach for the nets they double
as attachment stubs for (`F1_PWR`, `F3_PWR`, `F5_PWR`) is unchanged at 23.152 / 23.155 / 23.060 mm —
still **−2.548 / −2.545 / −2.240 mm vs. v1** (an improvement), well inside the ±3 mm budget (§15.5).
No fix applied; none needed.

### 15.4 Gate re-verification (from-scratch rebuild off the untouched live board)

```
$ outline.py --board r3_base.kicad_pcb --out r3_o.kicad_pcb --spec merged_floorplan_r3.json
Edge.Cuts items removed: 11 / added: 7 / In1 GND zones grown: 1 / heritage zones clipped: 40
new GND pours: 4 / mounting holes added: 3 (H10..) / stitching vias added: 65

$ apply_placement.py --board r3_o.kicad_pcb --placement merged_floorplan_r3.json --out r3_placed.kicad_pcb
applied 218; refused (heritage) []; missing refs []
footprints not fully inside the outline: 0: []
courtyard overlaps (same-side, >=1 new part; real polygons): 0: []

$ heritage.py check tools/baseline/heritage_rev2.json r3_placed.kicad_pcb --allow-zone-growth --allow-edge
note: new items: footprints +221, tracks/vias +65, zones +4
heritage check: 0 violation(s)

$ attachment_check.py tools/baseline/heritage_rev2.json r3_placed.kicad_pcb
attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
```

Identical outline/heritage/attachment evidence to v1 and to rounds 0–2 — fix round 3 adds 0 new
heritage or attachment violations anywhere on the board; all 218 placements apply cleanly. The live
board (`FlatSat_V1/FlatSat_V1.kicad_pcb`) and `FC_V5e_Production_Rev2/` were never opened for write
— all work done on scratch copies (§15.7). Live board mtime re-verified unchanged
(2026-09-14 11:31:05) after this round's session.

### 15.5 Full attachment-reach table (all 21 nets, round 3 vs round 2 — independently re-measured)

| Net | FC pad | Consumed at | Round 2 (mm) | **Round 3 (mm)** | Δ vs round 2 |
|---|---|---|---|---|---|
| `+3V3` | J16.6 | R370.1 | 22.502 | **22.502** | 0.000 |
| `F0_PWR` | J6.4 | R300.1 | 25.893 | **25.893** | 0.000 |
| `F1_PWR` | J9.4 | R314.1 | 23.152 | **23.152** | 0.000 |
| `F2_PWR` | J11.4 | R320.1 | 24.559 | **24.559** | 0.000 |
| `F3_PWR` | J13.4 | R333.1 | 23.155 | **23.155** | 0.000 |
| `F4_PWR` | J1.4 | R340.1 | 24.543 | **24.543** | 0.000 |
| `F5_PWR` | J2.4 | R353.1 | 23.060 | **23.060** | 0.000 |
| `F0_SCL`…`F5_SDA`, `SCL_Top`, `SDA_Top` (14 nets) | J6/J9/J11/J13/J1/J2/J16 | U300/U310/U311/U312/U313/U314/U316 pins 3/6 | — | **unchanged** | 0.000 |

All 21 nets are **byte-identical to round 2** (max Δ across the block remains +0.602 mm on `+3V3`,
from round 2) because none of them terminate on C316, R371 or R372 — confirmed by independently
re-running `my_reach.py` on the round-3 rebuilt board rather than assuming it from the unchanged
anchor-IC positions.

### 15.6 Courtyard-gap re-scan (whole block, round 3)

Independent pairwise same-side scan of all 48×47/2 combinations on the round-3 board: **minimum gap
0.510 mm** (R314–U300, R333–U311, R353–U313, unchanged from round 2), **29 pairs under the 0.55 mm
scan window** (same count as round 2 — 3 pairs that existed in round 2's cluster layout no longer
exist, replaced by the 3 new IC-adjacent/R371–R372 pairs the flanking fix creates), **0 pairs below
0.500 mm**. `apply_placement.py`'s own real-polygon overlap check on the whole 218-placement board:
**0 overlaps** (§15.4).

### 15.7 Commands run (fix round 3)

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
SCRATCH=<scratchpad>/detail_face_column
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# baseline check: re-dump + diff the round-2 delivered board against placement_face_column.json
# (0 differences, 48/48 refs) before designing any change
$KPY my_audit_measure.py r2_placed.kicad_pcb   # -> r2_geom.json / r2_courtyards.json (renamed)

# real pin-table lookup for U316 (all 8 pads, both edges) from the round-2 board, used to derive
# the flanking geometry by hand (pad offsets, target pin x/y) rather than guessing
python3 -c "inspect U316's 8 pads + C316/R370-374's pad offsets from r2_geom.json"

# new placement for C316/R371/R372 only, merged into a copy of placement_face_column.json
python3 -c "set C316=(244.45,51.45,180,F), R372=(251.57,51.45,180,F), R371=(254.07,51.45,0,F)" \
    # -> new_placement_r3.json (48 refs, only these 3 changed)

# merge into a copy of floorplan.json (only this block's 48 refs replaced)
python3 -c "merge new_placement_r3.json into a copy of floorplan.json" # -> merged_floorplan_r3.json

# rebuild from scratch, from the untouched live board copy
cp /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/FlatSat_V1.kicad_pcb $SCRATCH/r3_base.kicad_pcb
cp /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/FlatSat_V1.kicad_pro $SCRATCH/r3_base.kicad_pro
$KPY tools/pcb/outline.py         --board $SCRATCH/r3_base.kicad_pcb --out $SCRATCH/r3_o.kicad_pcb \
                                  --spec  $SCRATCH/merged_floorplan_r3.json
$KPY tools/pcb/apply_placement.py --board $SCRATCH/r3_o.kicad_pcb    --out $SCRATCH/r3_placed.kicad_pcb \
                                  --placement $SCRATCH/merged_floorplan_r3.json

# gated
$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json $SCRATCH/r3_placed.kicad_pcb \
     --allow-zone-growth --allow-edge
$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json $SCRATCH/r3_placed.kicad_pcb

# re-measured every checklist row + the L11 reach table + courtyard-gap sweep, all with real
# GetCourtyard() polygons and real per-pad positions, on the round-3 rebuilt board
$KPY my_audit_measure.py $SCRATCH/r3_placed.kicad_pcb   # -> r3_geom.json / r3_courtyards.json
$KPY fcpads2.py $SCRATCH/r3_placed.kicad_pcb $SCRATCH/fcpads_r3.json
diff fcpads_r2.json fcpads_r3.json   # -> identical
$KPY my_reach.py $SCRATCH/r3_placed.kicad_pcb           # -> L11 table, all 21 nets
python3 -c "diff r2_geom.json vs r3_geom.json on all 48 refs" # -> 0 diffs on 45 refs, 3 moved as designed
python3 -c "pairwise courtyard-gap scan + rule 1/3/4 hot-pad-to-pin distances from r3_geom.json"
```

### 15.8 Files delta (round 3 vs round 2)

- `detail/placement_face_column.json` — 3 of 48 refs changed (C316, R371, R372); 45 unchanged
- `detail/placement_face_column.md` — this report (checklist §3 rows 1/3/4/5/8/10/11/12/14–19
  updated; §9 deviation A rewritten; §10 pair-count re-verified; this §15 added)
- `detail/placement_face_column_placed.kicad_pcb` — rebuilt with the fix-round-3 placement (outline +
  all 218 placements; unrouted)
