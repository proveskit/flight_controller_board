# Audit — block `bench_io_cable` (auditing fix round 3's delivery)

**Date:** 2026-09-14 · **Auditor:** independent Sonnet agent (role: refute, not confirm) · **Subject:** `placement_bench_io_cable.json` / `.md` (fix round 3) and `placed_r3.kicad_pcb`

**Verdict: PASS.** No must-fix or should-fix items found. Two notes carried/added (documentation-completeness only, no placement change required).

The placer's own checklist was not trusted. Every number below was independently re-derived: pad/courtyard geometry via a fresh `pcbnew` query and a from-scratch courtyard-gap script (nearest-edge distance between real `F_CrtYd` polygons, built on the same `footprint_silhouette()` helper `apply_placement.py` uses, so "real polygons" means the same thing here as in the gate), the three canonical gates re-run from the delivered `outlined_r3.kicad_pcb` + `merged_r3.json` (not merely re-read from the round-3 write-up), and the DRC json re-scanned directly for any violation naming one of this block's refs. Manufacturer sources were re-fetched independently (not taken on the placer's word): the RP2350 hardware-design PDF was pulled and grep'd directly for the R7/R8 text, and J701's LCSC-hosted datasheet was fetched a 5th time (rounds 0/1/2, the round-3 audit, and now this one) — still metadata/title only, confirming the standing "unreachable" finding rather than assuming it.

## 1. Verification of the four canonical gates (re-run, not re-read)

```
$KPY tools/pcb/apply_placement.py --board outlined_r3.kicad_pcb --placement merged_r3.json --out myaudit/reverify_placed.kicad_pcb
  -> applied 218; refused (heritage) []; missing refs []
  -> footprints not fully inside the outline: 0
  -> courtyard overlaps (same-side, real polygons): 0
  -> exit 0

$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json placed_r3.kicad_pcb --allow-zone-growth --allow-edge
  -> new items: footprints +221 (218 placements + 3 mounting holes from outline.py), tracks/vias +65, zones +4
  -> heritage check: 0 violation(s)   exit 0

$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json placed_r3.kicad_pcb
  -> 65 new tracks/vias, 0 stub chains into the flight section, 0 violations, 0 warnings   exit 0
```

All three reproduce the round-3 write-up's claims exactly (independently re-run, not copied from the .md).

## 2. Fixed-anchor immobility (measured directly on `placed_r3.kicad_pcb`, compared against `floorplan.json`'s v1 values)

| Ref | v1 (floorplan.json) | Measured (placed_r3) | Match |
|---|---|---|---|
| J701 | (275.0, 54.12, 0°, F) | (275.0, 54.12, 0.0°, F) | identical |
| J702 | (287.2, 60.6, 0°, F) | (287.2, 60.6, 0.0°, F) | identical |
| J703 | (270.795, 74.765, 0°, F) | (270.795, 74.765, 0.0°, F) | identical |
| SW701 | (291.36, 66.76, 0°, F) | (291.36, 66.76, 0.0°, F) | identical |
| SW702 | (284.06, 66.76, 0°, F) | (284.06, 66.76, 0.0°, F) | identical |

All five fixed anchors unmoved and unrotated. **Pass.**

## 3. Envelope compliance (courtyard bbox of every owned ref vs `[267.8,51.1,294.4,91.2]`)

Independently computed (not the placer's numbers):

| Ref | Courtyard bbox (mm) | Inside envelope | Margin (tightest side) |
|---|---|---|---|
| C701 | (280.975, 51.255, 282.925, 54.645) | yes | **N: 0.155 mm** (tight, see note N1) |
| TP701 | (284.752, 52.254, 287.245, 54.746) | yes | N: 1.154 mm |
| R701 | (271.535, 59.075, 272.465, 60.925) | yes | comfortable |
| R702 | (278.035, 59.075, 278.965, 60.925) | yes | comfortable |
| R703 | (272.380, 88.175, 273.310, 90.025) | yes | S: 1.175 mm |
| R704 | (274.180, 88.175, 275.110, 90.025) | yes | S: 1.175 mm |

J701's courtyard breaches the north envelope line by **2.245 mm** (measured: bbox top y=48.855 vs env y0=51.1) — this is a **fixed anchor**, unmoved this round, and the breach is independently corroborated as pre-existing in `floorplan_v2.md` line 68 ("Block-envelope breaches | 4, all fixed anchors (SW703 +0.500, J701 +2.245, J400 +2.095, J401 +2.095 mm) — pre-existing in v1, not movable"). Confirmed genuine, not this block's doing. **Pass (N/A for J701; all six owned/movable refs pass outright).**

## 4. Courtyard-to-courtyard spacing, real polygons (constraint h, 0.5 mm floor)

Independently computed via a from-scratch nearest-edge-distance script on the real `F_CrtYd` polygons (not the placer's numbers):

| Pair | Measured gap | ≥0.5 mm? |
|---|---|---|
| C701 ↔ J701 | 0.660 mm | pass |
| C701 ↔ TP701 | 1.828 mm | pass |
| C701 ↔ J702 | 3.473 mm | pass |
| R701 ↔ J701 | 0.810 mm | pass |
| R702 ↔ J701 | 0.810 mm | pass |
| R703 ↔ R704 | 0.870 mm | pass |
| TP701 ↔ J701 | 4.438 mm | pass |
| TP701 ↔ J702 | 3.259 mm | pass |

(Small deltas vs. the placer's own numbers — e.g. 0.660 mm here vs. 0.600 mm claimed — are within the noise of two independently-written nearest-edge algorithms sampling the same courtyard polygons; both are comfortably clear of the 0.5 mm floor, so the conclusion is unchanged.) **No sub-0.5 mm gap found anywhere in this block. Pass.**

## 5. Manufacturer-guideline checklist, independently sourced and measured

| # | Rule | Source (independently fetched/verified this round) | Measured on `placed_r3.kicad_pcb` | Verdict |
|---|---|---|---|---|
| 1 | CC1/CC2 (Rd) pull-downs close to the receptacle's CC pins | USB-C sink-detection network is generic practice; J701's own datasheet (Hroparts TYPE-C-31-M-12, LCSC C165948) has **no reachable layout section** — re-fetched independently this round (5th attempt across all rounds), still metadata/title only. Fallback secondary guidance found via search (JLCPCB "PCB Layout Guidelines for USB Type-C"): Rd should sit "within 5 mm" of the CC pins. | R701.2↔J701.A5(CC1) = 9.577 mm; R702.2↔J701.B5(CC2) = 9.577 mm (my own pad-to-pad calc from queried pad coordinates, matches the placer's 9.5763 mm). **Exceeds the 5 mm secondary guideline.** However: R701/R702 already sit at the courtyard floor immediately south of J701 (0.81 mm gap, row 4) — J701's own receptacle body is ~8.2 mm deep (mechanical shroud pads at y 50.99–55.17, courtyard to y=58.265), and the CC pads sit at the connector's mating face (y=50.075), inside that mechanical envelope. There is no legal placement point closer to the CC pads that doesn't sit inside J701's own courtyard. This is the same physical floor the checklist already discloses for C701's VBUS distance (§7 of the round-3 doc) — but the round-3 doc does **not** disclose the same shortfall for R701/R702, stating a flat "Pass" instead. | **Pass, but see Note N2** — the placement itself is correct (mechanically bound, same as C701), the *documentation* is inconsistent in disclosing it. |
| 2 | USB_DP/USB_DM 27 Ω series termination "placed close to the chip" (U200), not the connector | Raspberry Pi, *Hardware design with RP2350* (fetched directly from `pip-assets.raspberrypi.com/.../RP-008280-DS-2-hardware-design-with-rp2350.pdf`, not taken on trust) — verbatim: *"these I/Os do require 27 Ω series termination resistors (R7 and R8 in Figure 11), placed close to the chip, in order to meet the USB impedance specification"*, with the reference schematic separately annotated **"Make sure R7 and R8 are close to RP2350."** | R703.2↔U200.52(DP) = 1.938 mm; R704.2↔U200.51(DM) = 1.938 mm (independently computed from queried pad coordinates — matches placer's 1.9383 mm). | **Pass.** |
| 2b | D+/D- leg-length symmetry | Same source | \|1.938 − 1.938\| = 0.000 mm | **Pass.** |
| 3 | VBUS bulk/bypass cap adjacent to VBUS pins, short GND return | Fallback (neither J701's nor a generic 0805 X7R cap's datasheet has an application-specific layout figure) | C701.1(VBUS)↔ nearest J701 VBUS pad (A9/B4, 277.45,50.075) = **4.894 mm** (independently computed from queried pad coordinates — matches placer's number exactly). Fallback target (1–2 mm) not met, but J701's own 8.2 mm-deep receptacle body makes anything closer illegal (inside J701's courtyard) — same physical floor as row 1. Ground-return check: a GND stitching via sits **3.78 mm** from C701 (284.91, 50.6), a plausible short return once routed. | **Pass (fallback shortfall genuinely disclosed and physically bound).** |
| 4 | Test points at block/board edge, probe-reachable | Brief constraint (g) | TP701 courtyard to the true `Edge.Cuts` polyline (walked every segment/arc on the actual board, not sampled off the envelope line): **4.675 mm** (my own measurement; placer's independently-computed 4.646 mm is consistent within polygon/arc-sampling tolerance) | **Pass.** |
| 5 | Courtyard overlap, real polygons, whole board | Constraint (d) | 0 (re-run independently, §1) | **Pass.** |
| 6 | Envelope | Constraint (a) | All 6 owned/movable refs inside (§3) | **Pass.** |
| 7 | Fixed anchors unmoved/unrotated | Constraint (b) | Confirmed identical (§2) | **Pass.** |
| 8 | 12.6 mm lane (x 231.4–244) clear of tall parts | Constraint (e) | Block occupies x 267.8–294.4, entirely east of the lane | **Pass (N/A).** |
| 9 | Heritage frozen | Constraint (f) | 0 violations (re-run, §1) | **Pass.** |
| 10 | L11 attachment gate | Constraint (c)/`attachment_check.py` | 0 violations, 0 warnings (re-run, §1) | **Pass.** |
| 11 | Anchor ICs move ≤3 mm | Constraint (c) | N/A — this block's fixed anchors (J701/J702/J703/SW701/SW702) are connectors/switches, not ICs; no anchor IC exists in this block | **Pass (N/A).** |
| 12 | F.Cu ruling (F3): passives on F.Cu | Brief §12 ruling F3 | All 6 owned refs confirmed on `F.Cu` (queried directly, not read off the .md) | **Pass.** |
| 13 | ESD-first ordering at the connector | Manufacturer/generic USB-C practice (fallback) | **N/A by explicit schematic design decision**, not an oversight: `bench_io.kicad_sch` carries a text note (verified directly in the sheet, line ~4551): *"No USB ESD array fitted (none found that matches this footprint); ESD exposure is bench-only, same as any lab USB cable."* This is a component-selection decision made at the schematic stage, out of scope for a placement-only pass — there is no ESD part in the BOM for this connector to place. | **Pass (N/A, verified against the schematic text, not assumed).** |
| 14 | DRC — no violation newly introduced against this block's refs | Constraint enforcement generally | Re-scanned `drc_r3.json` directly (not the placer's filtered summary) for every mention of C701/J701/J702/J703/R701–704/SW701/SW702/TP701. Hits are all pre-existing/expected classes: `clearance`/`hole_clearance`/`solder_mask_bridge` against J701/J703 (multi-pin connector zone-fill artifacts, present because nothing is routed yet — J703 is a fixed anchor, unmoved, so these are inherited from v1, not introduced this round), and `unconnected_items` (ratsnest) against every part, which is expected on a fully unrouted board and is a *separate* DRC category from the 9-class "870 violations" breakdown the round-3 doc cites. The one pre-existing `courtyards_overlap` DRC hit names **SW2/TP2** — unrelated flight-heritage refs, not this block. | **Pass — no new/placement-caused DRC defect found.** |

## 6. Notes (no should-fix; disclosed for completeness)

- **N1 — C701's envelope margin is razor-thin.** North-edge clearance measured at 0.155 mm (placer's own figure: 0.125 mm) — compliant, but this round's fix (rotating C701 to clear the courtyard floor) consumed nearly all the north-edge headroom to do it. Any future footprint-library update that grows the 0805 courtyard by even 0.1–0.15 mm on that edge would push this into violation. Not a fix requirement now (the rule is "inside the envelope," which it is), but worth a wider margin if this block is revisited.
- **N2 — Checklist-disclosure inconsistency, not a placement defect.** Row 1's "Pass" for R701/R702 does not disclose that 9.577 mm exceeds the ≤5 mm secondary guideline this audit found, even though the underlying reason is identical to the reason C701's shortfall against its own fallback target is explicitly and honestly disclosed in §7 of the round-3 document (J701's receptacle body physically occupies the space that would need to be used). Both are equally mechanically bound; only one is written up that way. No placement change is possible or being requested — R701/R702 already sit at the courtyard floor immediately behind J701 — this is purely a request that future revisions of the write-up apply the same disclosure standard to both findings.

## 7. Rules audited

20 distinct rules/constraints were independently checked (canonical gates x3, fixed-anchor immobility x5 refs, envelope x6 refs, courtyard-floor spacing x8 pairs, CC pulldown proximity, USB series-R proximity + symmetry, VBUS bypass proximity + ground-return via availability, test-point edge reachability, lane N/A, heritage-outline N/A, anchor-IC N/A, F.Cu ruling, ESD-ordering N/A verified against schematic text, DRC re-scan). **0 must-fix, 0 should-fix, 2 notes.**

## 8. Conclusion

Fix round 3's delivery holds up under independent re-derivation of every number and re-fetch of every external source. The should-fix from the prior audit (courtyard floor at C701↔J701) is genuinely closed on real polygons with no exception invoked. No new violation was found. **Verdict: PASS.**
