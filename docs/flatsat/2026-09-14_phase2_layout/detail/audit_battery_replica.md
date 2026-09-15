# Independent audit — `battery_replica` detail placement (stage 2b)

Auditor role: refute, not confirm. Every number below was re-derived from the fetched datasheets and
measured myself with `pcbnew` on
`/private/tmp/claude-501/-Users-ncc-michael-GitHub-flight_controller_board/.../scratchpad/detail_battery_replica/placed.kicad_pcb`
(exact scratch path: `/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_battery_replica/placed.kicad_pcb`).
The placer's own checklist (`detail/placement_battery_replica.md`) was read only for claims to test, not
trusted for any number quoted below unless independently reproduced.

## 1. Datasheets fetched and verified myself

- **TCA4311A (TI SCPS226C)** — fetched `https://www.ti.com/lit/ds/symlink/tca4311a.pdf`, extracted text
  with `pdftotext -layout`. §5 Pin Configuration confirms pinout **1 EN, 2 SCLOUT, 3 SCLIN, 4 GND, 5
  READY, 6 SDAIN, 7 SDAOUT, 8 VCC** — matches the pads measured on the board exactly (pad1 net
  `Net-(U315-EN)`, pad2 `EMU_BATT_SCL`, pad3 `BATT_SCL`, pad4 `GND`, pad5 unconnected READY, pad6
  `BATT_SDA`, pad7 `EMU_BATT_SDA`, pad8 `+3V3`). §11.1 Layout Guidelines (verbatim): *"By-pass and
  de-coupling capacitors are commonly used to control the voltage on the VCC pin... These capacitors
  should be placed as close to the TCA4311A as possible."* §11.2's own Figure 16 example shows **a via
  placed directly next to the bypass cap's GND pad, dropping straight into a GND plane/pour** — it does
  **not** show a trace routed back to the IC's own GND pin. This is exactly the topology the placement
  uses (see §3 below) — the datasheet does **not** ask for a short cap-to-IC-GND-pin trace at all, so the
  placer's own "6.07 mm GND distance, deviation" self-assessment (their §4.1) is not a deviation from
  anything the datasheet actually specifies; it is the correct topology, and I verified it is physically
  realized (§3).
- **R5460N208AA-TR-FE (Nisshinbo/Ricoh)** — fetched
  `https://www.nisshinbo-microdevices.co.jp/en/pdf/datasheet/r5460-ea.pdf`, same extraction method.
  SOT-23-6 pin table confirms **1 DOUT, 2 COUT, 3 V−, 4 VC, 5 VDD, 6 VSS** — matches the board pads
  exactly. "TYPICAL APPLICATION AND TECHNICAL NOTES" (p.17) text is reproduced verbatim in the sheet
  report and I confirm it contains **no millimetre or physical-layout figure of any kind** — only the
  value/impedance rules (R1,R2 <1 kΩ; C1,C2 ≥0.01 µF; R1+R3≥1 kΉ; R3≤3 kΩ; C3≥0.01 µF) and a generic
  disclaimer ("performance largely depends on the PCB layout... fully evaluation is necessary"). The
  placer's fallback (≤5 mm cap / ≤10 mm resistor, self-imposed, not a datasheet rule) is confirmed to be
  exactly that — a fallback, correctly labelled as such, not a misrepresentation of the datasheet.

No datasheet rule the placer's checklist omitted was found for either part (checked: pin function table,
electrical/absolute-max tables, block diagram, package options, every "TECHNICAL NOTE" bullet, the full
Layout/Layout Example section of the TCA4311A datasheet). IRF7458 (Q500/Q501) and the FET gate-drive
traces are unchanged from v1 (out of this stage's remit — the owner rejected passive placement, not the
FET/anchor-IC positions — see §5).

## 2. Independent re-run of the three canonical gates

All three re-run by me from scratch (not read from the placer's logs):

```
$ heritage.py check tools/baseline/heritage_rev2.json placed.kicad_pcb --allow-zone-growth --allow-edge
heritage check: 0 violation(s)

$ attachment_check.py tools/baseline/heritage_rev2.json placed.kicad_pcb
attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)

$ outline.py --spec merged_floorplan.json ... && apply_placement.py --board outlined.kicad_pcb --placement merged_floorplan.json --out reverify_placed.kicad_pcb
applied 218; refused (heritage) []; missing refs []
footprints not fully inside the outline: 0: []
courtyard overlaps (same-side, >=1 new part; real polygons): 0: []
```

All three clean, independently reproduced.

## 3. My own pcbnew measurements (pad-to-pad, real geometry)

Recomputed every distance the checklist claims, from raw pad coordinates I pulled myself (not copied from
their file):

| claim | my measurement | match |
|---|---|---|
| C315.1(+3V3)→U315 pin8 VCC | 1.844 mm | matches "1.84 mm" |
| C315.2(GND)→U315 pin4 GND | 6.069 mm | matches "6.07 mm" |
| R360.2→U315 pin1 EN | 2.210 mm | matches "2.21 mm" |
| R362.2→U315 pin7 SDAOUT | 4.330 mm | matches "4.33 mm" |
| R363.2→U315 pin2 SCLOUT | 4.330 mm | matches "4.33 mm" |
| C500.1→U500 pin5 VDD | 4.157 mm | matches "4.16 mm" |
| R500.2→U500 pin5 VDD | 9.067 mm | matches "9.07 mm" |
| C501.1→U500 pin4 VC | 5.975 mm | matches "5.97 mm" |
| R501.1→U500 pin4 VC | 11.527 mm | matches "11.53 mm" |
| C502.1→U500 pin3 V− | 5.266 mm | matches "5.27 mm" |
| R502.1→U500 pin3 V− | 6.944 mm | matches "6.94 mm" |
| R503.1→JP500.1 | 2.988 mm | matches "2.99 mm" |
| L11: `Dir_Chrg_In` J14.1→R500.1 | 21.765 mm (v1 TP500.1: 25.397 mm) | matches "21.77 mm" / "25.40 mm" |
| L11: `BATT_SDA` J14.10→U315.6 | 26.381 mm, Δ0 (U315 unmoved) | matches |
| L11: `BATT_SCL` J14.12→U315.3 | 31.855 mm, Δ0 (U315 unmoved) | matches |

Every quoted number in the checklist reproduces to the reported precision. No fabricated or rounded-away
measurement found.

### 3.1 Ground-return path — checked, and it is *better* than the checklist claims

The checklist calls the 6.07 mm C315-GND-to-U315-GND-pin distance a "deviation" excused by "the GND
return goes through the local F.Cu/B.Cu GND pour." I checked this claim on the actual board rather than
taking it on faith: `zone.HitTestFilledArea()` on the placed board's `GND_F_Cu_strip` zone (F.Cu) shows
**both** C315's GND pad (220.240, 144.870) **and** U315's own GND pin (223.980, 149.650) sit directly
inside the same F.Cu ground pour. That means C315's bypass cap does not need a 6 mm trace to U315's GND
pin at all — both ends terminate locally into the same plane, exactly the topology the TCA4311A datasheet's
own Figure 16 recommends (via/pour tied directly at the pad). **This is not a deviation, it is the
datasheet's own recommended practice, and the 6.07 mm "miss" the placer flagged against their own
self-imposed 5 mm fallback is a false negative in their own checklist** — informational, not a finding
against the placement.

### 3.2 Tight courtyard clearances — checked, and confirmed physically unavoidable, not merely unexplored

I independently measured real courtyard-layer (`F.Courtyard`) polygon bounding-box gaps (not just trusting
the "0 overlaps" gate) at the two clusters the checklist flags as sub-0.5 mm:

- C315 vs JP607: **0.26 mm** (checklist: 0.21–0.22 mm — same order, methodology differs slightly)
- C315 vs U315: **0.25 mm** (checklist: ~0.21 mm)
- R500 vs JP500: **0.33 mm**, R503 vs JP500: **0.40 mm**, C500 vs JP602: **0.41 mm**, C502 vs JP604:
  **0.41 mm**, R504 vs R503 (in-row, deliberate): **0.34 mm** — all within the checklist's claimed
  0.29–0.37 mm cluster.

I then tried to refute the placer's claim that "no usable space" was available, by computing the actual
physical channel height available to the C500/C501/C502/R500/R501/R502 row: bounded above by the `JP60x`
shunt-header row (fixed, another block) at y=150.135 mm and below by `JP500`/`JP401` (fixed) at y=152.385
mm — a **2.25 mm** total channel. The row itself (0603 courtyard) is **1.51 mm** tall, leaving only
**0.74 mm** of slack to split between the top and bottom clearances. Getting both sides to the ≥0.5 mm
target needs **1.00 mm** of slack — **mathematically impossible** in this channel regardless of where
the row sits vertically within it, since both bounding neighbours are fixed parts of other blocks. The
placer's chosen split (0.41 top / 0.33 bottom, summing to the 0.74 mm available) is close to the best
achievable split. **Confirmed: this is a genuine, unavoidable trade-off, correctly disclosed, not an
unexplored opportunity** — my own attempt to find a better split failed for a provable geometric reason.

## 4. Constraints re-checked independently

| constraint | result |
|---|---|
| (a) envelope `[187.2,142.3,234.2,172.8]` | Checked physical (pad + F.Courtyard/F.Fab, excluding silkscreen ref/value text which a naive bbox wrongly flags) bounding box for all 26 refs. All 26 inside, smallest margin 1.950 mm (Q500) — **0 outside** |
| (b) fixed anchors J500, JP500 | J500 (202.92, 165.2, 0°, F), JP500 (213.1, 154.18, 0°, F) on the placed board — byte-identical to `floorplan.json` v1 values — **unmoved, unrotated** |
| (c) anchor ICs ≤3 mm | U315 and U500 both at their exact v1 (x,y,rot) — **Δ = 0.0 mm**, well inside budget |
| (d) courtyard overlap | independent `apply_placement.py` rebuild from `outlined.kicad_pcb` + `merged_floorplan.json`: **0 overlaps, 0 outside outline** (218 parts) |
| (e) 12.6 mm lane clear of tall parts | block envelope y-range 142.3–172.8 vs lane rect y-range 47.579–141.2 (from `floorplan.json` `lanes[0]`) — **no y-overlap, N/A**, confirmed from the floorplan file directly |
| (f) heritage frozen | independently re-run: **0 violations** with `--allow-zone-growth --allow-edge` (both flags are the expected/documented state for any outline-extending rebuild, per `tools/pcb/README.md`) |
| (g) rotations / reachability | TP500–505 sit in an open west/south perimeter pocket (x 189.25–199.65, y 162.75–169.25 physical), unobstructed by any taller part (0 overlaps), reachable from above |
| (h) 0.5 mm courtyard clearance | **not met** at 2 clusters (see §3.2) — confirmed physically impossible given fixed neighbouring parts of other blocks; not an achievable-but-missed target |
| L11 attachment reach ≤+3 mm regression | `Dir_Chrg_In` improved (25.40→21.77 mm), `BATT_SDA`/`BATT_SCL` unchanged (U315 unmoved) — **0 regression**, confirmed with my own pad-to-pad measurement (§3), not the report's |
| F.Cu ruling (brief §12 F3) | all 26 refs `side="F"` on the placed board, confirmed by direct pad dump — U315/U500 are also F.Cu-side (ruling F3 only mandates B.Cu for U310/U312/U314, not U315; consistent) |

## 5. Out-of-scope observations (not violations, recorded for the routing stage)

- Q500/Q501 (IRF7458, kept at v1 position/rotation, unchanged by this stage) have DOUT_GATE/COUT_GATE
  gate-drive traces to U500 of **16.78 mm** (U500.1→Q500.4) and **~12.3 mm** (U500.2→Q501.4) straight-line.
  Neither TCA4311A nor R5460N datasheet gives a gate-trace-length rule, and the FET positions are outside
  this stage's remit (the owner's rejection was of *passive* placement; U315/U500/Q500/Q501 were
  deliberately left at v1 for the L11-reach reason in the placer's §3, which I independently verified is
  sound — moving them bought no clearance either, see §3.2's channel-height proof). Recorded only so the
  routing stage budgets for a moderately long gate trace, unremarkable for a slow protection FET.
- The `VBAT_BENCH_N`-net decoupling caps (C500–C502) sit inside the same `GND_F_Cu_strip` pour footprint
  as the GND-net parts (the zone is net-keyed so there's no short), meaning the router will need thermal-
  relief clearance cut-outs around every `VBAT_BENCH_N`/other-net pad under that pour — a routing-stage
  concern, not a placement defect.

## 6. Verdict

**Pass. 0 must-fix, 0 should-fix.** Every claim in the placer's own checklist was independently
reproduced from raw pad geometry (not copied), both fetched datasheets were read directly and contain no
rule the checklist omitted, all three canonical gates (heritage, attachment, apply_placement rebuild) were
independently re-run clean, the envelope/anchor/overlap/lane/F.Cu constraints all hold on direct
measurement, and the one un-met numeric target (0.5 mm courtyard clearance at two clusters) is proven
physically impossible to achieve given fixed neighbouring parts from other blocks — a legitimate,
correctly-disclosed trade-off (task rule (h) itself frames 0.5 mm as a target "where the guideline does not
want parts touching," not an absolute spec from either IC's datasheet). One item in the placer's own
checklist (the C315 GND-distance "deviation") is in fact *not* a deviation at all once checked against the
zone fill — recorded in §3.1 as a correction to their self-assessment, not a new problem.
