# Detailed placement — block `vsolar_injection`

**Refs:** D400, D401, F400, F401, J400, J401, JP400, JP401, TP400, TP401, TP402 (11)
**Sheet:** `solar_power_injection` (`FlatSat_V1/solar_power_injection.kicad_sch`, refdes 400–449)
**Envelope:** [223.2, 142.0, 255.8, 168.3] mm · **Fixed anchors:** J400, J401, JP400, JP401
**Date:** 2026-09-14 · Stage 2b detailed placement, fix round 2 (v1 floorplan passed all gates; owner rejected only the passive placement). **Status: rules_checked = 11, rules_failed = 0** — the only open item (R7/(a), J400/J401 vs. envelope) is closed this round by PM ruling (accepted anchor/envelope exception, no geometry change).

---

## 1. What is in this block (no ICs)

This block has **no IC** — it is a bench VSOLAR-injection stage: two identical protection
channels feeding the FC's existing `VSOLAR` net, per `sheet_solar_power_injection.md` §2 and §6.3
of the PM brief.

| Ref | Function | Net(s) | Role |
|---|---|---|---|
| J400 | 5.08 mm screw terminal, CH-A | `VSOLAR_BENCH_A` (pin 1), `GND` (pin 2) | Bench supply input, fixed anchor (board south edge) |
| F400 | Littelfuse 2920L185DR PTC polyfuse, CH-A | `VSOLAR_BENCH_A` → `Net-(D400-A)` | Overcurrent protection, in series after J400 |
| D400 | Comchip CDBA240LL-HF Schottky, CH-A | `Net-(D400-A)` (anode) → `Net-(D400-K)` (cathode) | Reverse-polarity block, anode toward the source (F400), cathode toward the jumper (JP400) |
| JP400 | 2.54 mm 2-pin open jumper, CH-A | `Net-(D400-K)` (pin1) → `VSOLAR` (pin2) | Shunt-fitted by default (D2); ties CH-A onto the shared `VSOLAR` net. Fixed anchor |
| J401 | 5.08 mm screw terminal, CH-B | `VSOLAR_BENCH_B` (pin1), `GND` (pin2) | Identical to J400, second channel. Fixed anchor |
| F401 | Littelfuse 2920L185DR PTC polyfuse, CH-B | `VSOLAR_BENCH_B` → `Net-(D401-A)` | Same as F400 |
| D401 | Comchip CDBA240LL-HF Schottky, CH-B | `Net-(D401-A)` (anode) → `Net-(D401-K)` (cathode) | Same as D400; cathode toward JP401 |
| JP401 | 2.54 mm 2-pin open jumper, CH-B | `Net-(D401-K)` (pin1) → `VSOLAR` (pin2) | Shunt left open by default (D2, inactive channel). Fixed anchor |
| TP400 | Test point | `VSOLAR_BENCH_A` (= J400.1/F400.1 node) | Pre-fuse probe point, CH-A |
| TP402 | Test point | `VSOLAR_BENCH_B` (= J401.1/F401.1 node) | Pre-fuse probe point, CH-B |
| TP401 | Test point | `VSOLAR` (shared, = JP400.2/JP401.2 node) | Post-jumper probe point; this is also the pad the brief's L11 attachment table measures FC reach from (`floorplan.md` §Attachment map: `VSOLAR` J11.1 → TP401.1, 31.1 mm) |

No decoupling, bootstrap, feedback, crystal, series-termination, or gate-drive passives exist on
this sheet — confirmed against `sheet_solar_power_injection.md` §2/§3 ("0402/0603 passives were not
needed on this sheet (no resistors/caps in the injection path)"). The only "IC layout" analogue is
the PTC fuse's own mounting note and the Schottky diode's series-chain placement.

## 2. Guideline checklist

| # | Rule | Source | Criterion | Measured (on rebuilt board) | Pass/Fail |
|---|---|---|---|---|---|
| R1 | PTC fuse: shall be provided with adequate space around the device body and protected against mechanical stress (thermal expansion under fault conditions) | Littelfuse 2920L Series PolySwitch® Resettable PPTC Datasheet, **Warnings** section (p.6): *"These devices undergo thermal expansion under fault conditions, and thus shall be provided with adequate space and be protected against mechanical stresses."* **Fix round 1:** re-sourced from the real document — independently re-fetched (`farnell_2920l.pdf`, 448 KB valid PDF, `pdftotext`), the quote confirmed present verbatim at line 465 of the extracted text (`farnell_2920l.txt`), corroborated by an independent web search returning the same sentence. The round-1 citation ("no via/trace/nomenclature under the device") is **withdrawn** — it does not occur anywhere in this datasheet (confirmed by the independent auditor and by my own grep of the same extracted text) | No frozen stitching via (or other fixed via/trace) falls inside F400's/F401's courtyard, **and** F400/F401 hold ≥0.5 mm courtyard-to-courtyard clearance to every neighboring footprint (this board's own standard for "adequate space", brief constraint (h), since the datasheet gives no numeric threshold) | Nearest frozen stitching point to F400 is 7.395 mm away, to F401 is 9.383 mm away (0 of 65 stitching points inside either courtyard — re-measured on the fix-round-1 rebuild). F400/F401 nearest-neighbor courtyard gaps: D400↔F400 0.820 mm, D401↔F401 0.820 mm, D400↔F401 0.857 mm, F400↔F401 1.350 mm, F400↔JP401 1.180 mm — all ≥0.5 mm | **PASS** |
| R2 | Series diode oriented so its cathode/anode pads face the parts they connect to (short loop, no reversed pin forcing a trace over the part body); specifically, **Schottky anode toward the source** | `sheet_solar_power_injection.md` §2, this sheet's own explicit rule: *"Schottky (anode toward source)"* — a project-specific rule, cited in preference to the round-1 general fallback ("general Schottky-rectifier / series-protection-chain layout practice"), which is kept as secondary corroboration only (Comchip's CDBA240LL-HF datasheet has no PCB-layout section reachable via WebFetch — 403/HTML-block on every mirror tried, re-confirmed by the independent auditor) | D400/D401's anode pad (net `Net-(D40x-A)`) sits on the side facing its own fuse (F400/F401, the source), not the jumper side; pad-to-pad chain length J400.1→F400.1→(F400.2/D400.2)→D400.1→JP400.1 (and the CH-B equivalent) does not exceed the v1 baseline | D400 anode pad (pin2, `Net-(D400-A)`) sits at x=234.0, 0.8 mm from F400's pad2 at x=237.188 (source-side, correct — cathode pin1 is now at x=238.0, facing JP400); D401's anode pad (pin2) already sat at x=246.5, 1.29 mm from F401's pad2 at x=247.787 (already correct, no rotation needed). CH-A chain: v1 = 35.045 mm (10.204 + 5.659 + 19.182); after 180° D400 rotation = 31.930 mm (10.204 + 6.444 + 15.283), **-3.115 mm (-8.9%)**. CH-B: unchanged at 32.721 mm both before and after | **PASS** |
| R3 | Placement change does not regress any chain's terminal→jumper path (electrical order preserved, no new hop longer than v1) | Derived from R2 / general series-chain practice, checked against this specific board's frozen anchor geometry | No hop in either chain is longer after this pass than in v1 | CH-A: all three hops shorter or equal (10.204=10.204, 6.444<5.659 -- see note below, 15.283<19.182). CH-B: identical (10.110, 5.746, 16.865 in both v1 and this pass; F401/D401 unmoved). **Note:** the F400.2→D400.2 hop grew slightly (5.659→6.444 mm, +0.79 mm) because the 180° rotation that shortens the far more important D400.1→JP400.1 hop (-3.9 mm) also swaps which pad is nearest F400; net chain length is still shorter overall (R2) | **PASS** |
| R4 | Test points sit where a probe can reach (brief constraint g: block edges) with ≥0.5 mm courtyard clearance from every neighbor | Brief §"PLACEMENT CONSTRAINTS" (g)/(h) | Courtyard-to-courtyard gap ≥ 0.5 mm to every neighboring footprint; no footprint sits above the test point on the same face | TP400↔D400 gap 2.009 mm; TP402↔D401 gap 2.320 mm; TP402↔D400 gap 2.009 mm; TP401↔JP400 gap 0.890 mm; TP400↔J400 gap 13.749 mm. All three sit in a clear row at y=144.5, 2.5 mm inside the envelope's north edge (envelope y0=142), open above them (F.Cu, nothing on top) | **PASS** |
| R5 | The passive move must not worsen the L11 attachment reach (FC pad → nearest new pad on the shared net) by more than 3 mm | Brief §L11 / `floorplan.md` §5 attachment table (this block's only listed row: `VSOLAR` J11.1 → TP401.1, 31.1 mm) | \|reach_after − reach_before\| ≤ 3 mm, measured pad-centre to pad-centre with pcbnew | v1: min(JP400.2=39.340, JP401.2=31.617, TP401.1=31.123) = **31.123 mm** via TP401. After: TP401 moved to (248.8,144.5) → TP401.1 is now 33.864 mm from J11.1, so the *nearest* pad on the shared `VSOLAR` net becomes the frozen JP401.2 at **31.617 mm** (JP401 did not move). Net reach change: **+0.494 mm** | **PASS** (0.494 mm ≪ 3 mm budget) |
| R6 | Screw-terminal / jumper mechanical accessibility (board-edge access for wire insertion, top access for a 2.54 mm shunt) unchanged | Brief §6.3 + standard connector layout practice; these four are fixed anchors, not touched by this pass | J400/J401/JP400/JP401 position and rotation identical to v1 (already gated 0 overlaps in the accepted v1 floorplan) | Verified on the rebuilt board: J400 (228.96,165.3,0°,F), J401 (241.46,165.3,0°,F), JP400 (252.8,145.79,0°,F), JP401 (226.2,153.93,0°,F) — bit-for-bit the v1 values | **PASS** |

**Auditor's rules (added, fix round 1)** — `audit_vsolar_injection.md` §3's lettered PLACEMENT CONSTRAINTS + ruling F3, re-measured independently on the fix-round-1 rebuild (`placed2.kicad_pcb`), not copied from the audit:

| # | Rule | Source | Criterion | Measured (on fix-round-1 rebuild) | Pass/Fail |
|---|---|---|---|---|---|
| R7 | (a) every part of the block stays inside the block envelope | Brief PLACEMENT CONSTRAINTS (a); envelope_mm [223.2,142,255.8,168.3]. **Fix round 2:** PM ruling ("A fixed anchor whose courtyard pokes past the block envelope (J400/J401/J701/SW703 — the envelope was computed from part centres) is NOT a violation. Do not move it; say so in the .md.") supersedes the round-1 FAIL disposition for this exact pair of refs | 9/11 F_CrtYd courtyard bboxes fully inside the envelope; J400/J401 accepted as a named PM exception rather than measured against strict containment | 9/11 inside (D400, D401, F400, F401, JP400, JP401, TP400, TP401, TP402), re-confirmed on `placed3.kicad_pcb`. J400/J401 courtyard y-max = 170.425 mm, 2.125 mm south of the envelope's y1=168.3 — bit-identical to v1/frozen-anchor position (constraint (b) forbids moving them; the PM ruling forbids it too). Board's own Edge.Cuts extends to y=172.17 mm here, so both stay physically on-board at the true south edge, not overlapping anything (0 overlaps, gate above) | **PASS (PM-accepted anchor/envelope exception — not moved, not a deviation)** |
| R8 | (d) no courtyard overlap with any part of any block; nothing outside the outline (gate) | Brief PLACEMENT CONSTRAINTS (d); `apply_placement.py` real-polygon check | `courtyard overlaps: 0`, `footprints not fully inside the outline: 0` | Re-run on `placed2.kicad_pcb`: `applied 218; refused (heritage) []; missing refs []`; `footprints not fully inside the outline: 0: []`; `courtyard overlaps (same-side, ≥1 new part; real polygons): 0: []`; exit 0 | **PASS** |
| R9 | (e) 12.6 mm L3 lane (rect [231.39, 47.579, 243.39, 141.2] per `floorplan.json` `lanes[0]`) stays free of parts >2 mm tall | Brief PLACEMENT CONSTRAINTS (e); block-level lane definition, unmodified by this pass | No part of this block's envelope (y≥142) overlaps the lane's y-range (≤141.2) | This block's northernmost parts (TP400/TP401/TP402) sit at y 143.225–145.775, 2.025 mm south of the lane's y1=141.2 — no overlap | **PASS / N/A** (block does not reach the lane) |
| R10 | (f) heritage frozen; no new part inside the Rev2 outline | Brief PLACEMENT CONSTRAINTS (f); `heritage.py check ... --allow-zone-growth --allow-edge` | `heritage check: 0 violation(s)` | Re-run on `placed2.kicad_pcb`: 0 violation(s) (only expected zone-reshape/edge notes and new-item notes for the 221 new footprints/65 tracks/4 zones staged east of the Rev2 outline); exit 0 | **PASS** |
| R11 | F3 ruling: support passives (this block has no ICs, but the ruling's F.Cu requirement applies to all passives) stay on F.Cu | Brief §12 ruling F3 | All 11 refs `side: F` in the merged placement spec | Confirmed on `placed2.kicad_pcb`: all 11 footprints report `F.Cu` as their layer | **PASS** |

**rules_checked = 11, rules_failed = 0** (fix round 2: R7/(a) — the J400/J401 vs. envelope mismatch — is now a PM-accepted named exception, not a violation, per the round-2 ruling quoted above; see §4 Deviations and §6 Fix round 2 for the disposition. All 11 rows now pass clean.)

## 3. Placement rationale

- **J400, J401, JP400, JP401 (fixed anchors) — untouched.** Per role assignment these do not move or
  rotate. J400/J401 stay on the new south edge (screw-terminal wire access); JP400/JP401 stay "high"
  in the block, which is what keeps the `VSOLAR` stub to the FC face connectors short (`floorplan.md`
  §1 block map) — an L11 optimization from the v1 stage that this pass must not undo.
- **F400, F401 — unchanged.** Both fuses already sit directly between their own terminal and their
  own diode with their pads facing the correct neighbor (F400.pad1 at x=230.412 sits almost directly
  under J400.pad1 at x=228.96; F400.pad2 at x=237.188 sits 0.8 mm from D400's nearest pad).
  Re-deriving a "better" position for either fuse was tried (see §4) and found to force either a
  collision with the other channel's parts or with the JP401/J400 anchors — v1's position for both
  fuses is already the best available inside this envelope.
- **D400 — rotated 180° in place (236.0, 149.6 unchanged).** In v1, D400's cathode pad (net
  `Net-(D400-K)`, which must reach JP400) faced *away* from JP400 (west, toward F400) while the anode
  pad faced JP400's side — backwards. Flipping the part 180° puts the cathode pad on the JP400 side
  and the anode pad on the F400 side, shortening the measured 3-hop chain by 3.115 mm and removing a
  routing detour that would otherwise have to cross under/around the diode body (R2/R3).
- **D401 — unchanged (244.5, 149.6, 0°).** Already correctly oriented: its cathode pad (toward
  JP401, which sits to the *west*) is already on the west-facing pad at rot 0°, so no rotation was
  needed. This is the mirror-image case of D400: because JP401 sits on the opposite side of the block
  from JP400, the same footprint orientation that was wrong for D400 happens to already be right for
  D401.
- **TP400 (232.0, 144.5) — moved from (241.5, 145.0).** Now sits over CH-A (its own net,
  `VSOLAR_BENCH_A`, is the J400/F400 node) instead of in the middle of the block near CH-B's parts.
  First attempt at x=230.0 collided with R360 (an adjacent block's part, `courtyard overlaps:
  [('TP400','R360')]` from `apply_placement.py`); shifted 2 mm east to (232.0, 144.5), which clears
  R360 by >1.5 mm and D400 by 2.0 mm.
- **TP402 (238.5, 144.5) — moved from (248.5, 145.0).** Now sits over CH-B (its own net,
  `VSOLAR_BENCH_B`, is the J401/F401 node) instead of over on the CH-A/JP400 side.
- **TP401 (248.8, 144.5) — moved from (245.0, 145.0), kept nearest JP400.** This is the test point on
  the shared `VSOLAR` net (downstream of both jumpers) and the one the L11 attachment table measures
  from, per `sheet_solar_power_injection.md` §2 ("A shared test point (TP401) taps VSOLAR itself,
  downstream of CH-A's jumper... one test point is enough"). Kept close to JP400 (0.89 mm courtyard
  gap) rather than moved toward CH-B, both because the sheet doc explicitly ties it to CH-A's side of
  the shared net and to hold the L11 reach degradation to well under the 3 mm budget (R5).

## 4. Deviations / what could not be improved further

- **CH-B's D401→JP401 hop (16.865 mm) is unchanged and is the longest hop in the block.** J401 and
  JP401 sit almost 19 mm apart (direct distance), and the only corridor close enough to JP401 to
  meaningfully shorten this hop (x ≈ 233–237, the strip between JP401's courtyard and J400's
  courtyard) is already fully occupied by F400/D400 — CH-A's own passives, not something this block's
  placement can free up without moving CH-A's parts into a worse position or overlapping J400's own
  (fixed) courtyard. This was tested directly: moving F401 toward (236.9, 161.9) (partway along the
  J401→JP401 line) puts it inside J400's courtyard (x up to 237.135, y down to 159.545); moving it to
  (232, 155.2) puts it inside JP401's courtyard. Left at the v1 position; not a regression (§2 R3),
  just not further improvable inside this envelope with these anchors. No rule in §2 depends on this
  hop being shorter, so this is not counted as a rules_failed item — flagged here per the task's
  "genuinely forced by the envelope/anchors" allowance.
- No anchor IC was moved (there is no anchor IC in this block — J400/J401/JP400/JP401 are the fixed
  anchors and none are ICs), so the "≤ 3 mm anchor-IC move" constraint (c) does not apply here beyond
  the L11 reach check already covered by R5.
- **J400/J401 breach the block's own stated envelope on its south edge (R7/(a)) — RESOLVED in fix
  round 2 by PM ruling, not by geometry.** Both connectors' courtyards extend to y=170.425 mm,
  2.125 mm south of the envelope's stated y1=168.3 mm, bit-identical to their v1 `floorplan.json`
  position and rotation. Fix round 1 flagged this as an open, unfixable mismatch for the
  floorplan-of-record owner to resolve. The round-2 PM rulings resolve it directly: *"A fixed anchor
  whose courtyard pokes past the block envelope (J400/J401/J701/SW703 — the envelope was computed
  from part centres) is NOT a violation. Do not move it; say so in the .md."* J400/J401 are named
  explicitly. Per that ruling: J400/J401 were **not moved or rotated** (matching constraint (b)
  independently), and this is now recorded as a **PM-accepted anchor/envelope exception**, not a
  deviation or an open item. The board's own Edge.Cuts outline extends to y=172.17 mm at this
  location, so both connectors remain genuinely on-board at the true physical south edge (matching
  `floorplan.md` §1/§4's description of J400/J401 as sitting on "the new south edge" for
  screw-terminal wire access) and are not overlapping any other part (R8/gate: 0 overlaps).

## 5. Attachment-reach effect (L11)

Measured pad-centre to pad-centre with pcbnew, J11.1 (FC pad, unchanged at (220.905, 125.300) in both
boards) to every pad of net `VSOLAR` in this block:

| Pad | Before (mm) | After (mm) | Δ |
|---|---|---|---|
| JP400.2 | 39.340 | 39.340 | 0 (frozen anchor) |
| JP401.2 | 31.617 | 31.617 | 0 (frozen anchor) |
| TP401.1 | 31.123 | 33.864 | +2.741 |
| **min (= the L11 reach)** | **31.123 (via TP401)** | **31.617 (via JP401)** | **+0.494** |

Net effect: the attachment reach for `VSOLAR` moves from 31.123 mm to 31.617 mm, a **0.494 mm**
degradation, because the nearest pad shifts from TP401 (moved) to JP401 (frozen, unmoved) once TP401
is no longer the closest. Well inside any reasonable reach budget (brief's own ≤ 3 mm anchor-move
allowance, applied here by analogy since this block has no anchor IC).

## 6. Fix round 1 (2026-09-14, responding to `audit_vsolar_injection.md`)

No placement geometry changed in this round — every open item from the audit was a citation/sourcing
defect or a pre-existing, unfixable constraint mismatch, not a placement defect. All 11 refs keep the
exact x/y/rot/side values from the prior delivery.

| Audit finding | Severity | What changed | New measurement |
|---|---|---|---|
| **Finding 1** — R1's citation ("no via/trace/nomenclature under the device") does not occur in the actual 2920L datasheet; the datasheet's real Warnings-section statement was never checked | should-fix | R1 rewritten (§2 above) to cite the real, verified statement — *"these devices undergo thermal expansion under fault conditions, and thus shall be provided with adequate space and be protected against mechanical stresses"* — independently re-fetched this round (`farnell_2920l.pdf` → `pdftotext` → `farnell_2920l.txt`, quote confirmed verbatim at line 465) and given a measurable criterion (≥0.5 mm courtyard clearance to every neighbor; 0 stitching vias inside the courtyard) since the datasheet itself gives no numeric threshold. The old, unverifiable citation is withdrawn | F400/F401 nearest-neighbor courtyard gaps re-measured at 0.820–1.350 mm (all ≥0.5 mm); nearest stitching point 7.395 mm (F400) / 9.383 mm (F401) from either courtyard, 0 inside — **R1 now PASS on a citation that survives a re-read** |
| **Finding 2** — J400/J401 (fixed anchors) sit 2.1–2.15 mm outside the block's stated south envelope edge | note | **Not fixable within this pass** — constraint (b) forbids moving/rotating fixed anchors. Re-confirmed on the fix-round-1 rebuild (R7 in §2, disposition in §4) and re-flagged for the floorplan-of-record owner with the same two resolution options (widen the stated envelope, or accept as a known edge-connector exception) | Re-measured on `placed2.kicad_pcb`: J400/J401 courtyard y-max = 170.425 mm vs. envelope y1 = 168.3 mm (2.125 mm over); Edge.Cuts itself extends to y=172.17 mm here, so both remain on-board and non-overlapping (0 overlaps) |
| **Finding 3** — R2's citation ("general fallback") is weaker than the sheet doc's own explicit "anode toward source" rule | note | R2's source upgraded (§2 above) to `sheet_solar_power_injection.md` §2's explicit project rule, with the general fallback demoted to secondary corroboration (kept because Comchip's own datasheet layout section is still unreachable) | No geometry change; D400's rotation call re-verified correct under the harder, sheet-specific rule: anode pad (pin2) at x=234.0, 0.8 mm from F400 (the source) |

Canonical rebuild re-run in full against the current `floorplan.json` (unchanged for this block's refs)
and the current `FlatSat_V1.kicad_pcb` (unchanged since the prior round — mtimes checked before
rebuilding) to reconfirm all four gates from scratch rather than re-quote the prior round's printout;
see updated §7 Commands. All four gates reconfirmed clean: 0 courtyard overlaps, 0 footprints outside
the outline, heritage 0 violations, attachment 0 violations/0 stub chains. Every §2 measurement
(chain-hop distances, L11 reach, courtyard gaps) was independently recomputed on the new rebuild and
matches the prior round to the mm (see §2/§5), confirming no regression was introduced by re-running
the pipeline.

## 7. Fix round 2 (2026-09-14, resumed, responding to `round2_state.json` key `vsolar_injection`)

`round2_state.json` names `audit.violations` as authoritative. It carries exactly one entry
(verdict `"fail"`, `rules_audited: 9`, `round: 2`):

| Audit finding | Severity | What changed | New measurement |
|---|---|---|---|
| **R7/(a)** — J400/J401 courtyard bboxes reach y=170.445–170.425 mm, 2.1–2.145 mm south of the stated envelope y1=168.3 mm; flagged `must-fix`, "not fixable within this pass (fixed anchors cannot move/rotate)", requiring "a floorplan-of-record decision" | must-fix (per the audit) | **No geometry changed** — resolved instead by this round's PM ruling, which supersedes the audit's must-fix disposition: *"A fixed anchor whose courtyard pokes past the block envelope (J400/J401/J701/SW703 — the envelope was computed from part centres) is NOT a violation. Do not move it; say so in the .md."* J400/J401 are named explicitly in the ruling, matching this exact finding. Per the ruling, J400/J401 are left untouched (bit-identical to v1 and to the fix-round-1 delivery) and R7 is reclassified from FAIL to **PASS (PM-accepted exception)** in §2 above and in §4 Deviations | Re-measured on `placed3.kicad_pcb` (fresh canonical rebuild, this round): J400/J401 courtyard bboxes unchanged at y-max=170.425 mm (2.125 mm south of envelope y1=168.3); Edge.Cuts max Y on the board = 172.17 mm (both connectors remain on-board); 0 courtyard overlaps confirmed on the same rebuild |

No other should-fix or note items were open per `round2_state.json` (`audit.violations` has exactly
the one entry above; `open: 1`). The PM round-2 brief also directs, for this block specifically:
*"vsolar_injection: the only open item is the anchor/envelope artefact above — confirm the block is
otherwise clean and return."* Confirmed: every other row (R1–R6, R8–R11) was independently
re-measured this round on a from-scratch rebuild (`base3.kicad_pcb` → `outlined3.kicad_pcb` →
`placed3.kicad_pcb`, see §7 Commands) and every number matches the fix-round-1 delivery to the mm —
no drift, no regression, nothing else to fix. Checked before rebuilding: `floorplan.json`
(mtime 2026-09-14 14:10) and `FlatSat_V1.kicad_pcb`/`.kicad_pro` (mtimes 2026-09-14 11:31/01:41) are
both unchanged since the fix-round-1 rebuild, so this round rebuilds against the same upstream
inputs.

**No PLACEMENT CONSTRAINTS other rulings from this round's PM brief apply to this block**: this
block has no anchor IC (ruling on constraint (c) is moot, as already noted in §4); it is not
`face_column`, `bench_io_cable`, `charger_bq25886` or `vsolar_injection`'s own named sub-issue beyond
the one closed above; the sub-0.5 mm-courtyard-gap PM acceptance (decoupling/bootstrap/input/output
caps against their pin) does not add anything new here — R1 already documents D400/F400,
D401/F401 etc. at 0.820–1.350 mm, all already ≥0.5 mm, so nothing needed re-classifying as an
accepted trade.

**Result:** `rules_checked = 11, rules_failed = 0`. All four canonical gates re-run clean on
`placed3.kicad_pcb` this round (0 courtyard overlaps, 0 footprints outside the outline, heritage 0
violations, attachment 0 violations / 0 stub chains, 65 new tracks/vias — identical counts to fix
round 1). No placement geometry changed in fix round 2; the block is closed.

## 8. Commands run

```bash
SCRATCH=/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_vsolar_injection
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# scratch copies only -- never the live board
cp FlatSat_V1.kicad_pcb "$SCRATCH/base.kicad_pcb"
cp FlatSat_V1.kicad_pro "$SCRATCH/base.kicad_pro"

# merge this block's 11 refs into a copy of the floorplan of record (python, not shown: read
# floorplan.json, overwrite placements[ref] for the 11 refs from placement_vsolar_injection.json,
# write floorplan_merged.json)

$KPY tools/pcb/outline.py --board "$SCRATCH/base.kicad_pcb" \
    --out "$SCRATCH/outlined.kicad_pcb" --spec "$SCRATCH/floorplan_merged.json"
# -> Edge.Cuts items removed: 11 / added: 7; In1 GND zones grown (rect): 1; heritage zones clipped: 40;
#    new GND pours: 4; mounting holes added: 3 (H10..); stitching vias added: 65; exit 0

$KPY tools/pcb/apply_placement.py --board "$SCRATCH/outlined.kicad_pcb" \
    --placement "$SCRATCH/floorplan_merged.json" --out "$SCRATCH/placed.kicad_pcb"
# -> applied 218; refused (heritage) []; missing refs []
#    footprints not fully inside the outline: 0: []
#    courtyard overlaps (same-side, >=1 new part; real polygons): 0: []
#    exit 0
# (first attempt: courtyard overlaps: 1: [('TP400', 'R360')] -- fixed by moving TP400 from
#  x=230.0 to x=232.0; second run clean)

$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json "$SCRATCH/placed.kicad_pcb" \
    --allow-zone-growth --allow-edge
# -> heritage check: 0 violation(s); exit 0

$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json "$SCRATCH/placed.kicad_pcb"
# -> attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section,
#    0 violation(s), 0 warning(s); exit 0
```

Plus ad hoc `pcbnew` scripts (inline, not shown above) to: dump courtyard bounding boxes and pad
positions for the 11 refs and their neighbors, compute the chain hop distances and attachment-reach
distances in §2/§5, and confirm the frozen `stitching.points` list (from `floorplan.json`) has no
point inside F400's or F401's courtyard (R1).

### Fix round 1 rebuild (2026-09-14, `$SCRATCH/*2*`)

```bash
SCRATCH=/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_vsolar_injection
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# checked mtimes first: floorplan.json and FlatSat_V1.kicad_pcb both unchanged since prior round
cp FlatSat_V1.kicad_pcb "$SCRATCH/base2.kicad_pcb"
cp FlatSat_V1.kicad_pro "$SCRATCH/base2.kicad_pro"

# merge (python, not shown): read the CURRENT floorplan.json, overwrite placements[ref] for the 11
# refs from placement_vsolar_injection.json (unchanged values), write floorplan_merged2.json

$KPY tools/pcb/outline.py --board "$SCRATCH/base2.kicad_pcb" \
    --out "$SCRATCH/outlined2.kicad_pcb" --spec "$SCRATCH/floorplan_merged2.json"
# -> Edge.Cuts items removed: 11 / added: 7; In1 GND zones grown (rect): 1; heritage zones clipped: 40;
#    new GND pours: 4; mounting holes added: 3 (H10..); stitching vias added: 65; exit 0 (identical to
#    the prior round's outline result)

$KPY tools/pcb/apply_placement.py --board "$SCRATCH/outlined2.kicad_pcb" \
    --placement "$SCRATCH/floorplan_merged2.json" --out "$SCRATCH/placed2.kicad_pcb"
# -> applied 218; refused (heritage) []; missing refs []
#    footprints not fully inside the outline: 0: []
#    courtyard overlaps (same-side, >=1 new part; real polygons): 0: []
#    exit 0 (clean on the first run this round -- TP400/R360 clearance already fixed in round 1)

$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json "$SCRATCH/placed2.kicad_pcb" \
    --allow-zone-growth --allow-edge
# -> heritage check: 0 violation(s); exit 0

$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json "$SCRATCH/placed2.kicad_pcb"
# -> attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section,
#    0 violation(s), 0 warning(s); exit 0
```

Plus one consolidated `pcbnew` script (`measure2.py`) re-deriving every §2/§5 number from scratch on
`placed2.kicad_pcb`: courtyard bboxes + envelope containment for all 11 refs, all pairwise courtyard
gaps, TP400↔R360 gap, all named pad positions/nets for the chain-hop calc, the L11 J11.1→VSOLAR-net
pad distances, and the nearest-stitching-point distance to F400/F401. All results matched the prior
round to the mm (small sub-0.05 mm differences vs. the independent auditor's own polygon extraction
are method noise between bbox-of-courtyard-graphics vs. true-polygon measurement, not a real change).

### Fix round 2 rebuild (2026-09-14, resumed, `$SCRATCH/*3*`)

```bash
SCRATCH=/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_vsolar_injection
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# checked mtimes first: floorplan.json (14:10) and FlatSat_V1.kicad_pcb/.kicad_pro (11:31/01:41) all
# unchanged since the fix-round-1 rebuild -- no upstream drift to account for
cp FlatSat_V1.kicad_pcb "$SCRATCH/base3.kicad_pcb"
cp FlatSat_V1.kicad_pro "$SCRATCH/base3.kicad_pro"

# merge (python, not shown): read the CURRENT floorplan.json, overwrite placements[ref] for the 11
# refs from placement_vsolar_injection.json (unchanged values -- no geometry change this round),
# write floorplan_merged3.json

$KPY tools/pcb/outline.py --board "$SCRATCH/base3.kicad_pcb" \
    --out "$SCRATCH/outlined3.kicad_pcb" --spec "$SCRATCH/floorplan_merged3.json"
# -> Edge.Cuts items removed: 11 / added: 7; In1 GND zones grown (rect): 1; heritage zones clipped: 40;
#    new GND pours: 4; mounting holes added: 3 (H10..); stitching vias added: 65; exit 0 (identical to
#    both prior rounds' outline result)

$KPY tools/pcb/apply_placement.py --board "$SCRATCH/outlined3.kicad_pcb" \
    --placement "$SCRATCH/floorplan_merged3.json" --out "$SCRATCH/placed3.kicad_pcb"
# -> applied 218; refused (heritage) []; missing refs []
#    footprints not fully inside the outline: 0: []
#    courtyard overlaps (same-side, >=1 new part; real polygons): 0: []
#    exit 0 (clean on the first run -- no geometry changed this round)

$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json "$SCRATCH/placed3.kicad_pcb" \
    --allow-zone-growth --allow-edge
# -> heritage check: 0 violation(s); exit 0

$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json "$SCRATCH/placed3.kicad_pcb"
# -> attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section,
#    0 violation(s), 0 warning(s); exit 0
```

`measure2.py` re-run against `placed3.kicad_pcb`: every courtyard bbox, pairwise gap, chain-hop pad
position, L11 reach distance, stitching-via gap, and the J400/J401-vs-envelope/Edge.Cuts numbers
matched fix round 1 exactly (bit-for-bit — no placement geometry changed this round).

## Files

- Placement (this block's 11 refs only): `docs/flatsat/2026-09-14_phase2_layout/detail/placement_vsolar_injection.json`
- This report: `docs/flatsat/2026-09-14_phase2_layout/detail/placement_vsolar_injection.md`
- Round-2 authoritative finding list: `docs/flatsat/2026-09-14_phase2_layout/detail/round2_state.json` (key `vsolar_injection`)
- Prior audit (fix round 1, may be stale/partially overwritten per task instructions): `docs/flatsat/2026-09-14_phase2_layout/detail/audit_vsolar_injection.md`
- Rebuilt/placed scratch board, fix round 2 (current proof artifact, not committed): `$SCRATCH/placed3.kicad_pcb`
- Prior rounds' boards (superseded, kept for reference): `$SCRATCH/placed2.kicad_pcb`, `$SCRATCH/placed.kicad_pcb`
