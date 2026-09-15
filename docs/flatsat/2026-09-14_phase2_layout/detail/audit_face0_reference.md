# Independent datasheet audit — block `face0_reference` (round 2 — re-audit of fix round 1)

**Date:** 2026-09-14 · **Stage:** 2b detailed-placement audit, round 2 · **Role:** independent auditor (refute, don't confirm)
**Refs (16):** C301, C302, C303, C304, J300, R304, TP300–TP306, U301, U302, U303
**Board audited:** `/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_face0_reference/placed_r2.kicad_pcb`
(identical byte-for-byte to `placed_r2_final.kicad_pcb` in the same directory, confirmed by `diff`).

**Verdict: PASS** — 0 must-fix, 0 should-fix remaining. Both should-fix findings from round-0
audit are resolved: finding #1 (courtyard-clearance measurement error) is fully fixed and
independently re-confirmed; finding #2 (decoupling ground-return path) is fixed for C301 (the
case that was geometrically achievable) and, for C302/C303/C304, independently verified to be
bounded by the IC package's own pin geometry, not by an unexplored placement option — properly
disclosed by the placer, not silently dropped. All hard gates independently re-run clean. Two
new informational notes are recorded (razor-thin margin on one clearance pair, a footprint-family
naming mismatch on U303 that predates this placement stage) — neither is a placement-stage
violation.

---

## 1. Method (round 2)

Nothing from round-0/round-1 was taken on faith. For every claim in `placement_face0_reference.md`
(the round-1 report) I re-derived the number independently from `placed_r2.kicad_pcb` itself:

1. Loaded `placed_r2.kicad_pcb` in `pcbnew` and dumped, for all 16 refs, real position/rotation/
   side, every pad's actual **net name** (not the report's pin-function labels) and position.
2. Wrote a fresh courtyard-clearance tool (independent of the placer's `polydist.py`) using
   `GetCourtyard()` real polygon vertices, segment-to-segment distance, and point-in-polygon for
   overlap detection — same input convention `apply_placement.py`'s hard gate consumes, written
   from scratch rather than trusted from the placer's tool.
3. Re-ran `heritage.py check ... --allow-zone-growth --allow-edge` and `attachment_check.py`
   myself on `placed_r2.kicad_pcb`.
4. Diffed the placer's `merged_face0_reference_r2.json` against the current `floorplan.json`
   programmatically to confirm only this block's refs changed and no other of the 218 placements
   or any non-`placements` key (outline/pours/holes/stitching/lanes/keepouts) was touched.
5. Independently confirmed the attachment-reach exemption claim (§5 of the placer's report)
   against `floorplan.md` §5 directly — not the report's re-statement of it.
6. Re-fetched the primary datasheets myself (TI DRV2605L `SLOS854D`, TI TMP112/TMP112D
   `SBOS473L` rev. July 2024) via `WebFetch`→raw-PDF fallback→`pdftotext -layout`, and checked
   every pin-table and layout-guideline quote against the actual document text, plus checked one
   thing round 0/round 1 did not: **which physical package DRV2605LDGS actually is**, per TI's own
   orderable-part table.
7. Computed, from the real board geometry, whether the two residual ground-return distances
   (C302, C303/C304) could be reduced further without violating another constraint — not just
   accepted the report's claim that they can't.

## 2. Independent re-measurement — everything the round-1 report claims changed

| Claim (round-1 report) | My independent measurement | Result |
|---|---|---|
| C301 rotated 270°, both pads now 1.505 mm from U301 V+ (pad5) and GND (pad4) | pad C301.1 (272.425,128.030, net F0_PWR) ↔ U301 pad5 (270.9375,128.260): **1.5052 mm**. pad C301.2 (272.425,128.990, net GND) ↔ U301 pad4 (270.9375,128.760): **1.5052 mm** | confirmed, symmetric as claimed |
| C302 re-centered at (280.9125,118.006), 1.4875 mm from U302 VDD (pad6), y-aligned | pad C302.1 (280.9125,118.486,F0_PWR) ↔ U302 pad6 (282.400,118.486): **1.4875 mm**, same y — confirmed pure horizontal | confirmed |
| C302 GND-return now 2.724 mm (slightly worse than round-0's 2.679 mm, accepted trade) | pad C302.2 (280.9125,117.526,GND) ↔ U302 pad4 (283.550,116.846, nearest GND): **2.7238 mm** | confirmed |
| U302 moved total 1.025 mm from v1 (x only) | v1 (282.525,117.886) → placed (283.550,117.886): **1.025 mm**, ≤ 3 mm budget | confirmed |
| U303 moved 1.5 mm from v1 (y only), unchanged since round 0 | v1 (276.745,118.18) → placed (276.745,119.68): **1.500 mm**, ≤ 3 mm budget | confirmed |
| U301 unmoved (0.000 mm) | v1 (270.225,128.26) = placed (270.225,128.26) | confirmed |
| J300 fixed anchor unmoved/unrotated | v1 (270.795,118.175,0°,F) = placed identical | confirmed |
| All 3 previously-failing courtyard pairs now ≥0.5 mm: C302↔U303 0.5875, C302↔U302 0.5875, C302↔R304 0.974 | Independent polygon-vertex tool (own implementation): C302↔U303 **0.5875 mm**, C302↔U302 **0.5875 mm**, C302↔R304 **0.9740 mm** | confirmed, all pass |
| All other pairs in the block still ≥0.5 mm | Full pairwise sweep of all 120 pairs among the 16 refs: **worst is R304↔U302 at 0.5040 mm**, next-worst R304↔TP303/TP304 at 0.5138 mm, C301↔U301 at 0.5500 mm — all ≥ 0.5 mm, none below | confirmed, 0 pairs below target |
| Envelope containment | True courtyard-vertex bbox: x[269.027,292.820], y[116.395,129.415] ⊂ [267.2,114.9,294.6,131.3] | confirmed |
| Heritage 0 violations | Re-ran myself: `heritage check: 0 violation(s)` | confirmed |
| Attachment 0 violations, 0 warnings | Re-ran myself: `65 new tracks/vias, 0 stub chain(s), 0 violation(s), 0 warning(s)` | confirmed |
| F.Cu ruling — all 16 refs side=F | Independently dumped every footprint's layer: **all F** | confirmed |
| Lane N/A (block x-range doesn't intersect lane x 231.4–244) | block x[267.2,294.6] vs lane: no overlap | confirmed |
| Merge hygiene — only this block's refs differ from `floorplan.json` | Programmatic diff of `merged_face0_reference_r2.json` vs current `floorplan.json`: identical ref *set* (218=218), all non-`placements` keys byte-identical, **exactly 7 refs differ in value** (C301, C302, C303, C304, R304, U302, U303 — the only ones this block's placer ever moved from v1; U301/J300/TP300–306 correctly untouched) | confirmed |
| Attachment-reach exemption (block owns no FC pad on F0_PWR/F0_SCL/F0_SDA) | Checked `floorplan.md` §5 directly (not the report's copy of it): `F0_PWR`→J6.4→**R300.1** (face column), `F0_SCL`→J6.5→**U300.3** (face column), `F0_SDA`→J6.6→**U300.6** (face column) — none in `face0_reference` | confirmed, 0.000 mm effect is correct |

Every one of the round-1 report's quantitative claims reproduces exactly under independent
re-derivation. This is not a rubber stamp — see §3 and §4 for the residual items checked and
why they don't rise to a violation.

## 3. Round-0 finding #2 (ground-return path) — checked whether the "package floor" claim is real, not just accepted

Round-1 explains C302/C303/C304's un-reduced ground-return distances as bounded by where the
relevant GND pin physically sits on each package, not by an unexplored placement option. I did
not accept this — I recomputed the package-internal pin geometry myself and checked whether a
same-technique fix as C301's (rotate the cap onto the package's own hot/GND pin pitch) was
actually infeasible, rather than just unattempted.

- **U302 (VEML6031X00) pin6 VDD → nearest GND (pad1):** (282.400,118.486) → (283.550,118.926):
  **1.2313 mm**, diagonal — VDD and its nearest GND pin are on *opposite sides* of this 6-pad part
  (VDD at x=282.4, GND column at x=283.55), 1.15 mm apart on the package itself. A cap cannot sit
  inside the package outline, so 1.2313 mm plus the ≥0.5 mm courtyard standoff is close to a hard
  floor for this cap regardless of orientation — confirmed, not merely asserted.
- **U303 (DRV2605L) pin10 VDD → nearest GND (pad8):** (278.895,118.68) → (278.895,119.68):
  **1.0000 mm**, straight down the same package edge, but this GND pad sits at the *midpoint* of
  that edge (inside the courtyard's right-side "nub," y-range [118.285,121.075]), not at a corner
  a cap could wrap around from outside. **Pin1 REG → nearest GND (pad4):** **1.5000 mm**, same
  situation on the mirror edge. I extracted U303's real courtyard polygon and confirmed C303's
  and C304's headroom before violating the 0.5 mm soft-clearance gate is only **0.13 mm** (measured
  clearance 0.630 mm against the 0.5 mm floor) — matching the report's own number, independently
  reproduced, not copied.
- Unlike C301/U301 (TMP112), where V+ and its nearest GND sit on a *shared, external, symmetric*
  pitch (0.5 mm apart, both reachable from outside the package by rotating the cap), U302 and U303
  do not offer that geometry: the relevant GND pin is either on the far side of the part (U302) or
  mid-edge inside the courtyard's own protrusion (U303), not at a corner. **Independently confirmed:
  no rotation or reposition of C302/C303/C304 within the 0.5 mm clearance budget can materially
  shorten these loops** — the round-1 report's claim holds up under a from-scratch recheck of the
  package geometry, not just its own arithmetic.
- Additionally: TI's DRV2605L §11.1 "Layout Guidelines" (re-fetched and read directly, `pdftotext`)
  names only *"The decoupling capacitor for the power supply (VDD) should be placed closed [sic,
  TI's own typo] to the device pin"* and *"The filtering capacitor for the regulator (REG) should
  be placed close to the device REG pin"* — **no ground pin is named** in this rule, unlike
  TMP112's SBOS473L §8.3.1, which explicitly names *"the supply and ground pins."* This means the
  two-sided datasheet rule that motivated round-0's finding #2 does not even apply, textually, to
  C303/C304 — it only applies to C301 (TMP112) and, by the Vishay app note's similar "close to the
  VDD pin" wording (no GND named), not strongly to C302 either. **Disposition: downgraded from
  should-fix to a note.** The practice is followed to the full extent any cited datasheet asks for
  it (C301, fixed) and to the full extent physically possible where no datasheet names a ground-pin
  requirement at all (C302/C303/C304).

## 4. New checks this round (not just a rerun of round-0's list)

**(a) DRV2605LDGS package identity vs. the assigned KiCad footprint.** Re-fetching TI's DRV2605L
datasheet (`SLOS854D`) and reading its "13 Mechanical, Packaging, and Orderable Information"
section directly: the `DGS` suffix is TI's **VSSOP-10** package code (`DRV2605LDGSR` / `...DGST`,
"Package | Pins: VSSOP (DGS) | 10", body 3.00 mm × 3.00 mm). The datasheet's only two layout-example
figures are Fig. 66 (DSBGA) and **Fig. 67, explicitly labeled "DRV2605L Layout Example VSSOP."**
The board's actual footprint assignment for U303, however, is `TSSOP-10_3x3mm_P0.5mm` (confirmed
from the loaded board). VSSOP and TSSOP are different lead-frame families (gull-wing lead shape
and standard pitch/foot-length differ) even when a body size coincidentally matches — this is a
real footprint-family mismatch. **It is not a placement-stage defect**: no footprint or schematic
edits are authorized in this stage, and it predates this block's placement (inherited from
Phase-1 part/footprint assignment). It also does not invalidate any measurement in this audit or
the round-1 report: I independently confirmed the physical pin arrangement actually present on
the board (pins 1–5 down the left edge, 6–10 up the right edge, REG/SCL/SDA/IN·TRIG/EN then
VDD/NC/OUT+/GND/OUT−/VDD) matches Fig. 67's VSSOP pinout **exactly**, pin-for-pin, so every
guideline-fidelity claim built on Fig. 67 in this and the prior report is still correctly applied
to the real net topology. **Recorded as a note for the record** (footprint-assignment issue,
out of scope here), not a should-fix.

**(b) Margin audit on the tightest clearance pairs.** Two pairs pass the 0.5 mm soft target by a
razor-thin margin, unchanged since round 0 (round 1's fix did not touch these): **R304↔U302 =
0.5040 mm** (4 µm of margin) and **R304↔TP303 / R304↔TP304 = 0.5138 mm** (13.8 µm of margin). These
technically pass and are not a rule violation, but the margin is small enough that ordinary
footprint/courtyard-definition tolerances could plausibly erase it. **Recorded as a note**, not a
should-fix, since the measured value is what the tool's own gate convention returns and it is
≥ 0.5 mm.

## 5. Notes carried forward unchanged (round-0 items, still valid, still informational)

- **TMP112 ALERT pull-up / no-GND-tie.** Re-verified directly against SBOS473L §5 Table 5-1's own
  footnote: *"Note: Connecting to GND if Alert pin is not used is preferred."* U301 pad 3 (ALERT)
  is fully unconnected on this board (`unconnected-(U301-ALERT-Pad3)`), not tied to GND and with
  no pull-up — a real, verified departure from a directly-quoted datasheet preference, but one that
  requires a schematic/net edit (a resistor or a GND tie), not a placement change, and is explicitly
  out of this 16-ref placement scope. Unchanged from round 0/round 1.
- **R304/U302 thermal proximity.** R304 (dummy coil load) ↔ U302 (ambient-light sensor) true
  courtyard clearance **0.504 mm**, the block's single tightest pair (see §4b) — no manufacturer
  keepout exists for this combination, so it is an owner judgement call, not a rule failure.
  Unchanged from round 0/round 1 (U302's round-1 shift was in x only; R304 is a y-direction
  neighbor, so the gap did not move).
- The placer's round-1 fix log (§7 of `placement_face0_reference.md`) is accurate: every number
  I could independently re-derive from the board matches what it claims, including the two
  numbers it flags as "not further reducible" — which I verified are genuinely bounded by package
  geometry, not merely asserted to be.

## 6. Commands run (round 2)

```
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
S=/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_face0_reference
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json "$S/placed_r2.kicad_pcb" --allow-zone-growth --allow-edge
# -> heritage check: 0 violation(s)

$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json "$S/placed_r2.kicad_pcb"
# -> 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)

# independent pad/net/position dump: $S/audit2_dump.py
# independent courtyard true-polygon pairwise-clearance tool (own implementation, not the
# placer's polydist.py): $S/audit2_courtyard.py — full pairwise sweep of all 16 refs plus a
# neighbor-block proximity check (nothing outside the block within 8 mm of the envelope came
# closer than 1.5 mm to any block part)
# courtyard-polygon geometry dump for U303/C303/C304/U302/C302: $S/audit2_geom.py

# merge-hygiene diff: floorplan.json vs merged_face0_reference_r2.json, programmatic, all keys

# Datasheets re-fetched fresh this round (WebFetch -> raw PDF fallback -> pdftotext -layout):
#   TI DRV2605L SLOS854D  (confirmed §11.1 Layout Guidelines wording, Fig. 66/67, and — new this
#     round — the DGS=VSSOP-10 package identity from §13 Orderable Information)
#   TI TMP112/TMP112D SBOS473L, rev. July 2024 (confirmed §8.3.1 wording verbatim, Table 5-1 DRL/
#     SOT563 pin table, and the ALERT-pin GND-tie preference footnote)
```

Board handed back as `board_path` for this round: `placed_r2.kicad_pcb` (identical to
`placed_r2_final.kicad_pcb`, diffed byte-for-byte).
