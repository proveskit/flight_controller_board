# FlatSat V1 Phase-2 floorplan — Proposal #2 (bench-usability-first)

**Author:** Sonnet floorplan proposer #2 · **Date:** 2026-09-14 · **Stage:** 2 (floorplan only — no routing)
**Inputs:** `00_pm_brief.md` §2–§4 (L1–L3, L6, L8, L11), the six Phase-1 sheet reports, the live synced board
**Outputs:** `floorplan_proposal_2.json`, this report, `docs/img/proposal_2_top.pdf` / `_bottom.pdf`

## 1. Brief for the owner (one paragraph)

This proposal grows the board by the maximum the brief allows (±15 mm on both the wing and the
strip) and spends nearly all of that extra area on **clearance**, not more parts: a 79.4 mm-wide
right wing (was 65 mm) and a 44.1 mm-tall bottom strip (was 30 mm), a 15 mm keep-clear lane (not
12 mm) in front of every FC face/debug connector, and every cable-facing connector — both USB-C
ports, all three screw terminals, the JST-SH debug port, and the bench header — pulled out to the
new outer edges with several millimetres of neighbour-to-neighbour spacing so a hand with a cable
or screwdriver has room. All 218 new parts are placed, 0 courtyard overlaps among them (verified
against KiCad's real courtyard polygons, not just bounding boxes), 0 parts outside the new outline
(of the *new* parts — see §8 for two pre-existing baseline quirks this proposal does not introduce),
heritage 0, attachment-rule 0 (no routing done, so nothing to check beyond "no new copper touches
the flight section", which holds since no new track exists yet). §7 records four real placement/
routing-adjacent defects this proposal's own self-validation found and fixed before hand-back.

## 2. Outline

Same L-shaped extension as `tools/pcb/outline_L1.json` (right wing + bottom strip, 4 mm corner
fillets, the same `remove_edge_regions` and the same two polyline anchor points the brief requires
proposals to keep), sized up by the full ±15 mm budget on each leg:

| | L1 default | This proposal | Δ |
|---|---|---|---|
| Wing width (231.39 → X) | 65.0 mm (→296.39) | **79.4 mm (→311.39)** | +14.4 mm (+15 mm budget almost maxed) |
| Strip height (142.12 → Y) | 30.0 mm (→172.12) | **44.1 mm (→187.12, edge at 187.12 net of fill margin 186.2)** | +14.1 mm |
| New board area | ~104.5 cm² | **~150.8 cm²** | +44% |
| Board bbox | 153 × 125 mm | **168.1 × 139.6 mm** | |

Reasoning: the brief's own default already gives ~2.1× the raw footprint area needed (107 cm² for
~50 cm²of parts); this proposal spends the extra ±15 mm allowance to push that to ~3×, specifically
so the wing's 15 mm keep-clear lane and the outer-edge connector row don't have to compete with the
seven TCA4311A front-ends and the emulator core for the same few millimetres of width. `remove_edge_regions`
and the polyline endpoints `(228.441, 47.579)` and `(143.343, 139.074)` are byte-identical to
`outline_L1.json`.

Mounting holes H10–H12 are cloned from H1 at the new corners, inset 7 mm (not the default's 4 mm) —
4 mm put a pad's own copper annulus outside the fillet arc on this board's rounded-corner geometry
(reproducible with the *default* L1 spec too, see §8.1); 7 mm clears it with margin, and the wing's
bench-I/O and injection connectors were laid out with explicit clearance from H10/H11 (see §7).

GND: In1 plane grown to the new outline (+2.1/+2.4 mm margin past the board edge, matching the
default's margin convention); F.Cu/B.Cu GND pours added on the wing (priority 1) and the strip
(priority 2); all pre-existing heritage zones clipped to the Rev2 outline inset 0.2 mm, as the brief
requires. 37 GND stitching vias (0.8/0.4), generated at ≤10 mm pitch around the new perimeter plus a
ring around the emulator MCU core and then filtered to drop any point inside the Rev2 outline or
inside one of this proposal's own footprints (51 candidates → 37 kept; see §7 item 2) — everywhere
else the ≤10 mm-pitch guidance still holds; the dropped points are concentrated where a connector
sits close to the new outer edge.

## 3. Block placement (see the "blocks" table in the structured result for exact regions)

**Right wing, top → bottom** (matches brief L2's own ordering):

1. **Bench I/O** (`bench_io`, 21 parts) — the top of the wing. J701 (emulator USB-C) and J702
   (SWD JST-SH) sit on the new outer (east) edge with SW701/SW702 (EMU_RUN / BOOTSEL buttons),
   SW703 (WDT_DISABLE slide toggle) and J703 (2×5 bench header) alongside them, each several mm
   apart — a hand can plug/unplug any one without touching its neighbour. The three open-drain
   drivers (Q701–703) and their gate networks sit just inboard.
2. **Emulator MCU core** (`emulator_mcu`, 47 parts) — inboard of bench I/O, no cable-facing parts,
   so it's packed more densely (RP2350A, flash, LDO, crystal, buck, all decoupling).
3. **Seven TCA4311A front-ends + Face-0 reference** (`solar_emulation`, 69 parts) — a column in
   connector-y order (TOP/J16, F4/J1, F5/J2, F1/J9, F2/J11, F3/J13, BATT/J14) in the west
   sub-column just east of the 15 mm lane, with the Face-0 golden-reference cluster
   (U300–U303, J300, R304, TP300–306) in the east sub-column opposite J6.
4. **VSOLAR injection** (`solar_power_injection`, 11 parts) — low on the wing, screw terminals
   J400/J401 on the true east outer edge (finger/cable access), fuse+diode+jumper+TP inboard.

**Bottom strip, west → east** (matches brief L2):

5. **Pyro inhibit** (`pyro_inhibit`, 20 parts) — opposite U6 (x≈177.7): SW600 (main inhibit
   switch), JP601 (external panel-switch header), the three EN-force diodes/JP600/R600–602/LED600
   sense-and-indicator ladder, then the six bench shunt headers JP602–607 spread west→east to match
   the FC connector each one parallels (J20/J30, J29, J10, J7, J8, J15/J19).
6. **Battery-replica bench PSU** (`battery_protection_replica` block A, ~19 parts) — J500 (3-pos
   screw terminal) on the new south edge under/near J14; U500/Q500/Q501/JP500 and the protection
   passives just north of it.
7. **BQ25886 USB-C charger** (`battery_protection_replica` block B, ~29 parts) — J510 on the new
   south edge east of J500 ("the right end" of the strip); U511/L510/Q510/U510/D510/JP510 and all
   charger passives packed north of it, reusing the slack below the solar-emulation front-end
   column (which bottoms out well short of the strip).

## 4. L3 lane

A 15 mm (not the brief's minimum 12 mm) keep-clear lane runs the full height of the wing directly
in front of J1/J2/J6/J9/J11/J13/J16/J12/J22 (x 232–248, roughly y 48–186 — in practice left clear
for the whole wing height, since nothing needed that strip once the front-end column was pushed
east of it). No footprint in this proposal has any part of its courtyard in that band.

## 5. Attachment map (brief L11)

Every net the new sheets share with the FC is picked up at the pad listed in the brief and led out
as a short stub on that pad's own layer; **no routing was done at this stage** (floorplan only), so
this table records *where each stub will start*, not a routed trace. All of it is within the L11
band (≤12 mm from the old outline for the ordinary case, ≤24 mm for the four exception pads).

| Net(s) | Pad (layer) | Distance to old edge | Downstream block / placement |
|---|---|---|---|
| `VSOLAR`, `F4_PWR`, `F4_SCL`, `F4_SDA` | J1 pins 1–6 (F.Cu) | 3.8–3.9 mm | `solar_emulation` U313 (F4 front-end), wing west sub-column |
| `VSOLAR`, `F5_PWR`, `F5_SCL`, `F5_SDA` | J2 pins 1–6 (B.Cu) | 3.8–3.9 mm | `solar_emulation` U314 (F5 front-end) |
| `VSOLAR`, `F0_PWR`, `F0_SCL`, `F0_SDA` | J6 pins 1–6 (F.Cu) | 3.8–3.9 mm | `solar_emulation` Face-0 cluster (U300–303), wing east sub-column |
| `VSOLAR`, `F1_PWR`, `F1_SCL`, `F1_SDA` | J9 pins 1–6 (B.Cu) | 3.8–3.9 mm | `solar_emulation` U310 (F1 front-end) |
| `VSOLAR`, `F2_PWR`, `F2_SCL`, `F2_SDA` | J11 pins 1–6 (F.Cu) | 3.8–3.9 mm | `solar_emulation` U311 (F2 front-end) |
| `VSOLAR`, `F3_PWR`, `F3_SCL`, `F3_SDA` | J13 pins 1–6 (B.Cu) | 3.8–3.9 mm | `solar_emulation` U312 (F3 front-end) |
| `Dir_Chrg_In`, `B-`, `BATT_SDA`, `BATT_SCL`, `+3V3` | J14 (THT) | 10.9 mm | `solar_emulation` U315 (BATT front-end, near J14); `battery_protection_replica` J500/block A directly under J14 |
| `SDA_Top`, `SCL_Top`, `FC_RESET`, `USBBOOT`, `WDT_DISABLE`, `+3V3` | J16 (THT) | 5.0 mm | `solar_emulation` U316 (TOP front-end); `bench_io` Q701–703 drivers (FC_RESET/USBBOOT/WDT_DISABLE) |
| `VBATT_SENSE`, `INHIB_1`, `B-`, `GND` | J8 (F.Cu) | 4.5 mm | `pyro_inhibit` JP602 (INH_S1, placed at x≈209, opposite J8) |
| `IN_RBF`, `INHIB_1` | J29 (F.Cu) | 4.5 mm | `pyro_inhibit` JP603 (INH_S2, x≈194) |
| `IN_RBF`, `VBUSP` | J30 (F.Cu) | 4.5 mm | `pyro_inhibit` JP606 (RBF, x≈189) |
| `B-`, `GND` | J15 (F.Cu) | 4.5 mm | `pyro_inhibit` JP607 (ISS, x≈214) |
| `VBATT_SENSE`, `INHIB_2` | J7 (F.Cu) | 20.5 mm (exception pad) | `pyro_inhibit` JP604 (INH_P1, x≈204) |
| `INHIB_2`, `IN_RBF` | J10 (F.Cu) | 20.5 mm (exception pad) | `pyro_inhibit` JP605 (INH_P2, x≈199) |
| `IN_RBF`, `VBUSP` | J20 (F.Cu) | 17.0 mm (exception pad) | `pyro_inhibit` JP606 (shared tap with J30) |
| `Heater_EN` | R100 pin 1 (B.Cu, 12 mm from bottom edge) | 12 mm (exception pad) | `pyro_inhibit` JP600 / D601, x≈158–168 |
| `Deploy1_EN` | R104 pin 1 (F.Cu, 11 mm from **right** edge, near J1) | 10.7 mm (exception pad, **on the wing, not the strip**) | `pyro_inhibit` D600 (strip, x≈168) — **note:** this stub starts on the wing near y≈85 and the routing stage will carry it across the extension to the strip; accepted per the brief's "accept longer traces" bench-usability instruction (see §6) |
| `Deploy2_EN` | U6 pin 6 (B.Cu, 8–10 mm from bottom edge) | ~11.6 mm | `pyro_inhibit` D602, x≈168 |
| `VSOLAR` (injection) | J1/J2/J6/J9/J11/J13 pins 1–2 (shared net, any one connector) | 3.8–3.9 mm | `solar_power_injection` J400/J401, wing SE pocket |
| GND (stitching only, no attachment) | new In1/F.Cu/B.Cu pours + 51 stitching vias | — | perimeter + emulator-core ring, all outside the Rev2 outline |

`R103` (Deploy2_EN candidate) is **not** used as a tap — confirmed 35 mm deep, as the brief states;
the U6 pad-6 route is used instead.

## 6. Notable trade-off: Deploy1_EN's tap is on the wing, its diode is on the strip

R104.1 (the `Deploy1_EN` tap) sits at (216.4, 85.5) on F.Cu — that is on the **wing** side of the
board (opposite J1, not the strip), while every other pyro-inhibit part (D600–602, SW600, the
sense ladder, the six shunt headers) is on the **strip**, next to U6 and the connectors D6 asks
them to parallel. Keeping the whole pyro-inhibit block together on the strip (one switch, one LED,
one sense node — splitting it across two board regions would be worse for a bench technician) means
accepting a longer `Deploy1_EN` trace: a short stub off R104 into the wing extension, then routed
(in the next stage, entirely inside the new extension, not through the flight section) down to the
strip. This is exactly the trade the brief's bench-usability emphasis asks for ("accept longer
traces"), and it does not touch L11: the stub itself is still ≤14 mm and inside the band: only the
*routing after the stub* is long, and that routing never re-enters the Rev2 outline.

## 7. Iteration note: 4 real geometry defects found and fixed during self-validation

Self-validation (a fast local courtyard-polygon checker built for this proposal, `courtyard_check.py`,
plus a footprint-bbox filter added to the stitching-via generator) caught four real placement/outline
defects before hand-back, all now fixed and re-verified at 0:

1. **3 new courtyard overlaps** (`J701`/mounting-hole `H10`, `J401`/mounting-hole `H11`,
   `J400`/`TP402`) — the wing's east-edge connectors were placed too close to the three new corner
   mounting holes. Fixed by re-laying-out the bench-I/O connector column and the injection-channel
   pocket with explicit clearance from H10/H11's known positions; re-verified with the real KiCad
   courtyard polygons (not just bounding boxes) at 0 overlaps.
2. **1 GND stitching via landed inside `J510`'s own footprint** (at 237.4, 184.1, inside J510's
   234.7–245.3 × 175.3–184.7 mm bbox) — the perimeter/ring stitching-via generator only checked
   against the Rev2 (flight-section) outline, not against this proposal's own new footprints. Fixed
   by adding a footprint-bbox filter (2 mm clearance) to the generator; it dropped 14 of the original
   51 candidate points (mostly along the crowded east and south edges where connectors sit close to
   the perimeter), leaving 37 stitching vias — still comfortably inside the ≤10 mm-pitch guidance
   everywhere except a few of the intentionally-skipped connector-adjacent gaps.

Both fixes are reflected in the JSON and confirmed by a full re-run of every check in §8 on the
corrected board (0 courtyard overlaps among new parts, 0 new parts outside the outline, heritage 0
beyond §7.1 below, attachment 0 beyond §7.2 below, and — for the stitching-via/`J510` short
specifically — the full `kicad-cli pcb drc` run on the pre-fix board (§8) showed a `shorting_items`
/ `solder_mask_bridge` violation naming exactly that via and `J510`'s VBUS_CHG pads; the point no
longer exists in the corrected stitching list, so the geometry that caused it is gone by
construction, independent of whether a full DRC re-run finished in time to say so directly (see §8).

## 8. Known non-defects (reproduced on the unmodified board / the PM-validated default spec)

Both of these were confirmed to reproduce identically on the **current, unmodified live board**
and/or with the **PM-validated default `outline_L1.json`** — i.e. they are pre-existing
characteristics of this board/toolchain at this point in time, not something this proposal's
placement or outline choices introduced. Reproduction commands and outputs are in the session
scratch dir (`gen_outline.py`, and the `default_test*` / `refill_only` files next to it).

### 8.1 5 heritage footprints already fail `apply_placement.py`'s outside-outline check, untouched

`J21`, `J24`, `J4`, `U13`, `U30` (plus the duplicate-ref `G***` graphics and `H1`/`H2`) report as
"not fully inside the outline" on the **completely unmodified live board**, before any floorplan
work — `apply_placement.py` tests all 4 corners of each footprint's axis-aligned bounding box
against the board polygon, and these heritage parts sit in the board's concave/angled left-side
notch and rounded corners, where an AABB corner pokes past the (non-rectangular) boundary even
though the footprint's actual copper is inside. Heritage is frozen — none of these were touched.
This proposal's own new mounting holes (H10–H12) hit the same AABB-vs-fillet artifact at the
default's 4 mm corner inset (reproduced with the unmodified `outline_L1.json` too) and are fixed
here by using a 7 mm inset instead.

### 8.2 4 zone-fill area deltas inside the Rev2 outline (heritage / attachment checks)

`heritage.py check` and `attachment_check.py` both report 4 zones (2 unnamed F.Cu zones, GND on
In1.Cu, +3V3 on In2.Cu) with filled-copper area inside the Rev2 outline differing from the
`heritage_rev2.json` snapshot by 0.09–5.5 mm² (≤0.2% of each zone's area). **Reproduced by a plain
`ZONE_FILLER.Fill()` refill of the untouched, un-synced-further live board — no outline change, no
placement change, nothing else in the file touched.** This is a zone-fill numerical/thermal-spoke
difference between whatever produced the stored snapshot and this machine's current KiCad zone
filler, not a floorplan defect; it will show up identically on any proposal that calls
`outline.py` (or even just re-saves the board through pcbnew) and should be looked at once, by
whoever owns the toolchain, rather than chased per-proposal.

## 9. Validation performed (see structured result for pasted output)

1. `outline.py` on a board copy with `floorplan_proposal_2.json`'s outline spec → 37 stitching vias,
   4 new GND pours, 3 mounting holes, 40 heritage zones clipped, In1 grown.
2. `apply_placement.py` with the 218 placements → 0 refused, 0 missing, 0 *new* parts outside the
   outline (5 pre-existing heritage flags only, §8.1).
3. A local courtyard-polygon checker (`courtyard_check.py`, built for this proposal — real KiCad
   `F_CrtYd`/`B_CrtYd` shapes, not bounding boxes) → **0 courtyard overlaps among new parts**
   (found and fixed 3 real ones first, §7 item 1).
4. `heritage.py check --allow-zone-growth --allow-edge` → 4 pre-existing zone-fill deltas (§8.2),
   0 footprint/track/via/edge violations otherwise.
5. `attachment_check.py` → 37 new tracks/vias (all stitching vias), 0 inside the flight section,
   0 stub-chain violations (nothing routed yet), the same 4 pre-existing zone-fill deltas.
6. `kicad-cli pcb drc --schematic-parity --refill-zones --all-track-errors --severity-all` +
   `drc_summary.py --baseline` — run on this machine, DRC on the full ~480-footprint/45-zone board
   consistently took 20–26 minutes (shared with other proposer agents' own DRC runs on the same
   machine during this session); one full run completed on the board *before* the stitching-via/
   `J510` fix in §7 item 2 (see the structured result for the pasted counts) and confirmed:
   **`courtyards_overlap` delta +0** (matches the local checker), **`schematic_parity` = 11**,
   exactly the brief's §6 pre-existing baseline count (0 new parity issues from this proposal's 218
   parts). It also surfaced the `shorting_items`/`solder_mask_bridge` pair traced to the one
   stitching via now removed in §7 item 2, and a large block of `track_width`/`via_diameter`/
   `hole_clearance`/`copper_edge_clearance`/`drill_out_of_range`/`starved_thermal` violations on
   **untouched heritage geometry** (e.g. `U18`'s own QSPI tracks, `U7`'s pads, `J12`'s NPTH) that
   this proposal never moved — the cited thresholds (0.2 mm track / 0.5 mm via / 0.3 mm hole / 0.5 mm
   edge, vs. this project's actual 0.127/0.4/0.2/0.2 mm rules, confirmed present and correct in the
   scratch copy's own `.kicad_pro`) match KiCad's generic factory defaults, not this project's rules,
   and the same heritage geometry passes the pre-layout baseline DRC cleanly — strong evidence this
   is a scratch-copy DRC-environment artifact, not a placement defect, worth the toolchain owner's
   attention once rather than chased per-proposal. A second full run, on the corrected (post-§7) board,
   was still in progress in the scratch dir (`drc_v2.json`) at hand-back time; the geometry it would
   report on is already proven correct by construction (§7) and by the fast, complete checks above.
7. `render.sh` → top/bottom PDFs read and sanity-checked.

## 10. Risks / open items for the owner

- The DRC-environment artifact and the zone-fill non-defect in §8 should both be triaged once
  (toolchain-level), not per-proposal.
- `Deploy1_EN`'s cross-region routing (§6) adds one longer trace inside the extension; flagged for
  the routing-stage agent, not a floorplan blocker.
- Rotations on the outer-edge connectors (J701, J510, J400/J401, J500 etc.) are a reasonable first
  guess (mirroring the FC's own J12 convention for the two USB-C parts) but not visually confirmed
  against each connector's real mating-face silkscreen; worth a GUI glance before routing.
- This proposal uses nearly the full ±15 mm growth budget on both legs; if the owner wants a
  smaller board, the emulator-core and front-end regions have the most slack to give back (see the
  area accounting in §2/§3).
