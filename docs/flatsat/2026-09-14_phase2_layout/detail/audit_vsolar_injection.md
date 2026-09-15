# Independent audit — block `vsolar_injection` (round 3, post fix-round-2)

**Refs:** D400, D401, F400, F401, J400, J401, JP400, JP401, TP400, TP401, TP402 (11)
**Auditor role:** independent datasheet auditor — job is to refute, not confirm, the placer's deliverable.
**Inputs audited:** `detail/placement_vsolar_injection.json`, `detail/placement_vsolar_injection.md` (fix
round 2, dated 2026-09-14, responding to `round2_state.json` key `vsolar_injection`), board
`.../scratchpad/detail_vsolar_injection/placed3.kicad_pcb`.
**Prior audit superseded by this file:** the round-2 version of this file (verdict `fail`, one
must-fix: R7/(a) J400/J401 vs. envelope). This round re-audits the fix-round-2 deliverable from
scratch — every number below was independently recomputed on `placed3.kicad_pcb`, not copied from
either the placer's report or my own prior round's numbers.
**Date:** 2026-09-14

---

## 1. Method

- Read `blocks.json`, `floorplan.json` (v1 placements for this block's 11 refs), `floorplan.md`
  §1/§3/§5 (block map, design notes, L11 attachment table) and `sheet_solar_power_injection.md`
  (Phase-1 sheet doc) independently, before opening the placer's checklist.
- Built my own rule set from the task's lettered PLACEMENT CONSTRAINTS (a)-(h) plus ruling F3,
  applied fresh to every ref, rather than starting from the placer's §2 rows.
- Independently re-ran `heritage.py check` and `attachment_check.py` against `placed3.kicad_pcb`
  myself (not re-quoting the placer's printed output) — both exit 0, 0 violations.
- Measured every pad position, real `F_CrtYd` courtyard polygon (via `SHAPE_POLY_SET.Distance()`,
  not a bounding-box approximation), and pairwise courtyard gap on `placed3.kicad_pcb` with a fresh
  `pcbnew` script of my own (`measure.py`), independent of both the placer's and the prior audit
  round's numbers.
- Extended the neighbor scan beyond this block's own 11 refs to every other footprint on the board
  within a generous box around the envelope — the placer's and the prior audit's checklists only
  checked cross-block clearance for one pair (TP400 vs. R360); I checked all of them.
- Independently re-verified the Littelfuse 2920L PPTC datasheet text already on disk
  (`farnell_2920l.pdf`/`.txt` in the placer's scratch dir) is a genuine 448 KB PDF 1.7 containing
  "2920L185" in its ratings table, and re-grepped the full extracted text myself for the cited
  Warnings-section sentence and for any numeric spacing/clearance figure anywhere else in the
  document.
- Made a **fresh** attempt (this round, a third independent access path — `comchiptech.com`'s own
  admin-hosted PDF link plus `alldatasheet.com`, neither tried in the prior two rounds) to reach the
  Comchip CDBA240LL-HF datasheet's layout section, to stress-test the "genuinely unreachable" claim
  a second time.
- Independently checked the physical Edge.Cuts geometry local to J400/J401's x-range (not just the
  board's overall max-Y, which a sibling block's audit flagged elsewhere as a misleading citation).
- Independently confirmed the PM ruling the placer's fix-round-2 report cites for J400/J401 — "A
  fixed anchor whose courtyard pokes past the block envelope (J400/J401/J701/SW703 ...) is NOT a
  violation" — is a real, verbatim instruction issued to the placer in this task's own pipeline
  script (`.claude/workflows/flatsat-detailed-placement.js`, `PM_ROUND2` constant), not a claim
  invented by the placer to bypass a gate.
- Ran a supplementary `kicad-cli pcb drc --severity-all` pass on `placed3.kicad_pcb` (870
  violations total, board-wide) to check whether any violation is newly attributable to this
  block's 11 refs, beyond the required gate list.

## 2. Gate re-verification (independent, on `placed3.kicad_pcb`)

```
$ heritage.py check tools/baseline/heritage_rev2.json placed3.kicad_pcb --allow-zone-growth --allow-edge
heritage check: 0 violation(s)   (only expected zone-reshape/clip "note" lines and the
                                   +221 footprints / +65 tracks-vias / +4 zones "new items" note)
exit 0

$ attachment_check.py tools/baseline/heritage_rev2.json placed3.kicad_pcb
attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
exit 0
```

0 overlaps / 0 outside is already established by the placer's `apply_placement.py` run (exit 0, `applied 218`,
`courtyard overlaps: 0`, `footprints not fully inside outline: 0`) — independently spot-checked below (§3, §4)
by directly re-measuring every footprint's real courtyard polygon and pairwise gap myself rather than
re-trusting the printed line.

## 3. Placement-constraint audit (my own rule set, applied fresh)

| Constraint | Result |
|---|---|
| (a) every part inside envelope `[223.2,142,255.8,168.3]` | **9/11 pass; J400/J401 poke 2.145 mm past the south edge (y-max 170.445 vs. 168.3) — disposed as a named PM-accepted exception, not a violation (§5).** |
| (b) fixed anchors unmoved/unrotated vs. `floorplan.json` v1 | **PASS** — J400 (228.96,165.3,0°,F), J401 (241.46,165.3,0°,F), JP400 (252.8,145.79,0°,F), JP401 (226.2,153.93,0°,F): bit-identical to the v1 record, confirmed against the placed board's own footprint transforms (my own script, not the placer's printout) |
| (c) anchor-IC ≤ 3 mm move | N/A — no IC in this block (`sheet_solar_power_injection.md` §2/§3: two identical fuse→Schottky→jumper chains, no active silicon) |
| (d) no courtyard overlap; nothing outside outline | **PASS** — independently re-run, 0/0 (§2) |
| (e) 12.6 mm lane (x 231.39–243.39, y ≤ 141.2) clear of > 2 mm parts | **PASS / N/A** — this block's northernmost courtyard edge (TP400/401/402) sits at y = 143.204, 2.004 mm south of the lane's y1 = 141.2; no part of this block reaches the lane's y-range regardless of x (independently recomputed) |
| (f) heritage frozen; no new part inside Rev2 outline | **PASS** (§2) |
| (g) rotations short-loop; TPs at reachable block edges | **PASS** — D400's 180° rotation independently re-verified correct and the sole placement change with electrical effect in this whole block (§4); TP400/401/402 sit in a row 1.2–2.6 mm inside the envelope's north edge |
| (h) ≥ 0.5 mm courtyard-to-courtyard where separation is wanted; not corner-packed | **9/11-refs' own pairwise gaps all pass** (worst same-block pair D400↔F401 = 0.933 mm); **one cross-block gap found below 0.5 mm** — D400 ↔ C315 (another block's part) = 0.412 mm — disposed as a transient, self-resolving merge artifact, not a defect (§5) |
| F3 ruling: support passives stay on F.Cu | **PASS** — all 11 refs report `F.Cu`, confirmed on the placed board |

## 4. Independently measured geometry (`pcbnew`, on `placed3.kicad_pcb`, my own script)

**Courtyard real-polygon bounding boxes (mm):**

```
D400  [232.4550,147.8050,239.5450,151.3950]  inside envelope
D401  [240.9550,147.8050,248.0450,151.3950]  inside
F400  [229.1550,152.1750,238.4450,158.2250]  inside
F401  [239.7550,152.1750,249.0450,158.2250]  inside
J400  [225.8750,159.5450,237.1350,170.4450]  OUTSIDE (y-max +2.145 mm over env y1=168.3)
J401  [238.3750,159.5450,249.6350,170.4450]  OUTSIDE (same, +2.145 mm)
JP400 [250.9850,143.9750,254.6150,150.1550]  inside
JP401 [224.3850,152.1150,228.0150,158.2950]  inside
TP400 [230.7025,143.2038,233.2950,145.7962]  inside
TP401 [247.5025,143.2038,250.0950,145.7962]  inside
TP402 [237.2025,143.2038,239.7950,145.7962]  inside
```

**Chain-hop distances** (raw pad coordinates, real `SHAPE_POLY_SET`/pad-position API, not copied
from either the placer's or the prior audit's numbers):

- CH-A (D400 at rot 180°): J400.1(228.96,165.3)→F400.1(230.4125,155.2) = **10.204 mm**;
  F400.2(237.1875,155.2, net `Net-(D400-A)`)→D400.2(234.0,149.6, anode) = **6.444 mm**;
  D400.1(238.0,149.6, net `Net-(D400-K)`, cathode)→JP400.1(252.8,145.79) = **15.283 mm**;
  **total 31.931 mm.** Pad-net mapping read directly off the board (pad1=K, pad2=A, standard KiCad
  diode convention) — confirms the cathode pad really is the one now facing JP400 (east), matching
  the placer's rotation rationale exactly.
- CH-B (D401 at rot 0°, unrotated): J401.1(241.46,165.3)→F401.1(241.0125,155.2) = **10.110 mm**;
  F401.2(247.7875,155.2)→D401.2(246.5,149.6, anode) = **5.746 mm**;
  D401.1(242.5,149.6, cathode)→JP401.1(226.2,153.93) = **16.865 mm**; **total 32.721 mm.**
- Both totals match the placer's fix-round-1/2 numbers to the mm. I independently re-derived *why*
  D401 needs no rotation: JP401 sits west of D401, and D401's cathode pad (pin1) is already the
  west-facing pad at rot 0° — rotating it would move the cathode east, adding rather than removing
  length. Confirmed by direct calculation, not asserted.

**L11 attachment reach** (`VSOLAR`, J11.1 read directly off the board at (220.905,125.300) →
every `VSOLAR`-net pad in this block, recomputed from raw coordinates, not the placer's table):

| Pad | v1 distance | Fix-round-2 distance |
|---|---|---|
| JP400.2 (252.8,148.33) | 39.3405 mm (frozen) | 39.3405 mm |
| JP401.2 (226.2,156.47) | 31.6165 mm (frozen) | 31.6165 mm |
| TP401.1 | 31.1230 mm (v1 TP401 at 245.0,145.0) | 33.8640 mm (moved to 248.8,144.5) |
| **min (= L11 reach)** | **31.123 mm (via TP401)** | **31.617 mm (via frozen JP401)** |

**Δ = +0.494 mm**, independently confirmed — well inside any reasonable budget (this block has no
anchor IC, so constraint (c)'s 3 mm cap is applied only by analogy, as the placer itself discloses).

**Stitching-via clearance (R1's own criterion):** every via on the board within the block's
x/y neighborhood was enumerated directly. Only one relevant GND stitching via sits near this
block, at (234.0,144.8) — 7.375 mm from F400's courtyard bbox top edge and clear of F401's by a
wider margin. **0 stitching vias fall inside either F400's or F401's courtyard**, confirming R1's
disposition (see §6 datasheet check).

**Lane check:** independently confirmed — this block's northernmost courtyard edge is 2.0 mm south
of the lane's y1 = 141.2; no x-overlap analysis is even needed since the y-ranges are disjoint.

**Edge.Cuts local geometry (for the J400/J401 disposition, §5):** an Edge.Cuts line segment with
bounding box `(147.293,172.070)–(292.440,172.170)` was found on the board — this single segment
spans the *entire* x-range under both J400 (x≈228–237) and J401 (x≈238–250), confirming the
south-edge board material genuinely underlies both connectors' courtyards (which end at
y=170.445), not merely that *some* distant point on the board reaches y=172.17. This is a stronger,
more local confirmation than "the board's overall max Y is 172.17 mm."

## 5. Disposition of the two open items

### 5.1 — J400/J401 vs. the block's stated south envelope edge (2.145 mm over)

This is the same measured fact as the prior two audit rounds (courtyard y-max 170.445 mm vs. env
y1 168.3 mm), unchanged because constraint (b) forbids moving or rotating fixed anchors and neither
connector moved. The prior round of this audit scored this **must-fix**, reasoning that a measured
breach of a numbered PLACEMENT CONSTRAINT is a must-fix "by the task's own definition," independent
of whether this stage has authority to fix it.

This round downgrades that disposition, for a reason the prior round did not have available: I
independently found the exact ruling the placer's fix-round-2 report quotes —
*"A fixed anchor whose courtyard pokes past the block envelope (J400/J401/J701/SW703 — the
envelope was computed from part centres) is NOT a violation. Do not move it; say so in the .md."*
— verbatim in this task's own pipeline source (`.claude/workflows/flatsat-detailed-placement.js`,
the `PM_ROUND2` constant), naming J400/J401 explicitly. This is not the placer's own assertion; it
is the actual instruction the placer was given for this fix round, independently verifiable outside
the placer's report. Combined with the local Edge.Cuts confirmation above (both connectors sit on
real board material at the true south edge, not off-board), I accept this as a genuine, authorized
exception rather than an open constraint breach. **Disposition: not counted as a violation.**

### 5.2 — D400 ↔ C315 courtyard gap = 0.412 mm (new finding, not raised by either prior round)

Extending the neighbor scan past the one pair (TP400 vs. R360) that both the placer and the prior
audit round checked, I found D400's courtyard sits 0.412 mm from C315 — another block's
part (`battery_replica`'s U315 VCC-bypass cap) — below the constraint-(h) 0.5 mm target. Neither
the placer's checklist nor the round-2 audit disclosed this.

However, three independent checks show this is not a live defect in either block's final placement:

1. C315's position on `placed3.kicad_pcb` (231.2,147.5) is `floorplan.json`'s **v1** position for
   C315, not `battery_replica`'s own delivered placement — confirmed by diffing
   `docs/flatsat/2026-09-14_phase2_layout/floorplan.json` against
   `detail/placement_battery_replica.json`, which relocates C315 to (220.24,145.35), rot 90°, more
   than 10 mm away. This is the expected, documented behaviour of the per-block canonical process
   (each block's detail-placement stage merges only its own refs into a copy of the *current*
   `floorplan.json`; every other block's parts sit at v1 until the integrator merges all of them),
   not a defect introduced by this pass.
2. D400 did not move in x/y this round or the prior one (only rotated 180° in place); the `D_SMA`
   footprint's courtyard is rectangular and symmetric about its center, so the 180° rotation does
   not change its bounding box. The 0.412 mm gap to C315's v1 position therefore already existed in
   the owner-accepted v1 floorplan — it is inherited, not introduced by this block's passive
   placement.
3. Once the integrator merges `battery_replica`'s own delivered C315 position, this specific tight
   spot disappears on its own; moving D400 now to open it up would trade away its correctly-derived,
   R2/R3-verified chain-shortening position for a problem that is about to stop existing.

**Disposition: note**, not a should-fix — flagged for the integrator to re-confirm ≥ 0.5 mm between
D400/D401 and whatever `battery_replica` parts land nearest them once all blocks are merged (this
mirrors how `battery_replica`'s own audit round classified comparable forced/cross-block sub-0.5 mm
gaps against other blocks' fixed parts as `note`, not `should-fix`, for the same "mathematically
following from parts this stage does not own" reason).

## 6. Datasheet verification (independent, this round)

- **Littelfuse 2920L Series PPTC datasheet** (`farnell_2920l.pdf`/`.txt`, already on disk from the
  prior round; independently re-verified this round as a genuine 448 KB PDF 1.7 whose ratings table
  contains the row `2920L185 / LF185` with the exact Ihold/Itrip/Vmax/Imax/Rmin/R1max figures the
  sheet doc quotes): the cited Warnings-section sentence — *"These devices undergo thermal
  expansion under fault conditions, and thus shall be provided with adequate space and be protected
  against mechanical stresses"* — is present verbatim at line 465 of the extracted text, re-grepped
  by me directly. **No numeric spacing, keepout, or land-pattern-clearance figure exists anywhere
  else in the 475-line document** (re-grepped the whole extract for
  `clearance|keepout|spacing|mm from|distance from|do not place|no component`: zero hits). The
  ≥ 0.5 mm courtyard-gap fallback (this board's own standard, since the datasheet gives no number)
  is therefore the correct substitute, and it is met: F400/F401's worst same-block neighbor gap is
  0.933 mm (D400↔F401), and 0 stitching vias sit inside either courtyard. **Confirmed correct.**
- **Comchip CDBA240LL-HF**: made a third independent attempt, via two access paths neither of the
  first two rounds tried (`comchiptech.com`'s own admin-hosted "RevD" PDF link, and
  `alldatasheet.com`). The manufacturer's own site link resolves to a generic privacy-policy page,
  not the datasheet; `alldatasheet.com` returned HTTP 403. **Confirms the "genuinely unreachable"
  finding a second time, independently, via yet another route.** The fallback — general
  Schottky/series-diode layout practice, reinforced by `sheet_solar_power_injection.md` §2's
  explicit project rule "Schottky (anode toward source)" — remains the correct substitute, and the
  measured geometry (§4) shows it is met: D400's anode pad is 0.8 mm from F400 (the source) after
  rotation; D401's anode pad was already 1.29 mm from F401 (the source) with no rotation needed.
- J400/J401 (5.08 mm screw terminal) and JP400/JP401 (2.54 mm 1×02 header): ordinary connector
  datasheets of this class carry no PCB-layout section; not re-checked further since these are
  fixed anchors outside this pass's authority regardless.

## 7. Supplementary check: board-wide DRC (not a required gate for this stage)

`kicad-cli pcb drc --severity-all` on `placed3.kicad_pcb`: 870 violations board-wide (500
`clearance`, 383 `unconnected_items`, 199 `solder_mask_bridge`, 128 `hole_clearance`, 27
`lib_footprint_issues`, 9 `footprint_type_mismatch`, 4 `isolated_copper`, 1 `via_dangling`, 1
`courtyards_overlap`, 1 `copper_edge_clearance`). This block's 11 refs appear only in the expected
`clearance`/`hole_clearance` noise against unrefilled zones (a board-wide, pre-existing artifact of
an unrouted, not-yet-refilled board — the same class every other block's audit in this pipeline has
found and dismissed as out of scope for a placement-only stage) and in the universal
`unconnected_items` count (nothing is routed yet, by design — brief explicitly says "nothing is
routed"). The one `courtyards_overlap` violation on the board is SW2↔TP2 at x≈194 mm, unrelated to
this block (confirmed present in the untouched v1 floorplan, as a sibling block's audit already
established for the same pair). **No DRC class is newly attributable to this block's placement.**

## 8. Items re-verified from the prior audit round and confirmed closed (not re-opened)

- **Prior round's should-fix/note items (R1 citation accuracy, R2 citation strength)** — both
  remain fixed; re-verified independently this round rather than re-quoted (§6).
- **Prior round's sole must-fix (R7/(a), J400/J401 vs. envelope)** — downgraded to "not a
  violation" this round on the strength of independently confirming the PM ruling's authenticity
  outside the placer's own report (§5.1), which the prior round did not have available.
- No regression was found anywhere in the chain-hop geometry, L11 reach, F.Cu ruling, lane
  clearance, or same-block courtyard-gap budget — every number was independently recomputed from
  raw board geometry (§4) and matches the placer's fix-round-2 claims to the mm.

## 9. Summary

Gates (heritage, attachment, overlap/outside, fixed-anchor freeze, L11 reach, F.Cu ruling) all
independently re-measured clean on `placed3.kicad_pcb`. Every numeric claim in the fix-round-2
checklist was recomputed or re-read from source by me and matches. Extending the audit beyond what
either the placer or the prior round checked (a full cross-block neighbor scan, a local
Edge.Cuts check, a third independent datasheet-access attempt, and independent verification of the
PM ruling's authenticity in the actual pipeline source) surfaced one previously-undisclosed
sub-0.5 mm cross-block gap (D400↔C315), which on inspection is a transient artifact of the
canonical per-block merge process rather than a live defect, and confirmed the sole prior must-fix
(the J400/J401 envelope overflow) is now properly and verifiably disposed of by an authentic PM
ruling rather than by a hopeful self-report.

**rules_audited = 9** (the 8 lettered PLACEMENT CONSTRAINTS a–h, plus the F3 F.Cu-side ruling, each
applied fresh to every ref in the block, plus the two open items carried in from the prior round).
**verdict = pass** — zero must-fix, zero should-fix; one note (D400↔C315, transient/self-resolving,
flagged for the integrator) and one note (J400/J401 envelope exception, verified authentic and
correctly disposed).
