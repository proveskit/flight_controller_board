# PROVES FlatSat V1 — Phase 2 stage 4 (Routing) report — attempt 2

**Date:** 2026-09-20 · **Stage:** 4 (Routing) · **Owner:** routing agent (Opus, attempt 2) ·
**Input:** the build stage's placed, unrouted board (floorplan v2.3, outline + ground + netclasses;
383 unconnected) · **Delivered board:** `scratchpad/layout_route2/deliver/FlatSat_V1.kicad_pcb`
(with its `.kicad_pro` / `.kicad_dru` / schematics / libraries beside it).

**Result — every hard gate passes; connectivity is not complete.**

| Gate | Result |
|---|---|
| `heritage.py check --allow-zone-growth --allow-edge` | **0 violations** |
| `heritage.py check --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2` | **0 violations** (two band-fill notes, §3) |
| `attachment_check.py` (L11) | **0 violations, 0 warnings**, 32 stub chains |
| DRC clearance / shorting_items / hole_clearance / hole_to_hole / copper_edge_clearance / track_width | **0 of each** |
| DRC schematic parity | **11 = exactly the brief §6 FC baseline** |
| DRC unconnected | **76** (triaged in §8; 0 is not reached) |
| DRC courtyards_overlap | 1 = the known pre-existing Rev2 SW2/TP2 item |

Attempt 1 (same date, superseded — kept as `route_report_attempt1.md`) handed back 1 heritage
violation, 13 `shorting_items`, 23 `clearance`, 8 `hole_clearance` and 116 unconnected, with 7 of the
37 L11 nets unstubbed. All of those are cleared here except the unconnected count, which is now 76
and fully attributed.

---

## 0. What changed versus attempt 1, and why

Attempt 1's own post-mortem named its root cause exactly: the stub planner checked candidate paths
against heritage **tracks** only — never heritage **vias** — and modelled pads by their *inscribed
circle* (`min(hx, hy)`), which under-estimates the clearance a stub needs when it runs alongside a
pad's long axis (5 of its 13 shorts were around U6 for that reason). This attempt replaced the
collision model rather than patching it.

* **Exact shapes, no approximations.** Every obstacle — pad (any shape/rotation), track (capsule),
  via (ring), copper-layer graphics (the FC has a poem in F.Cu text), board edge and board cut-out —
  is KiCad's own `BOARD_ITEM.TransformShapeToPolygon(…, clearance)` output, scanline-rasterised into
  a numpy grid at 0.05 mm (0.02 mm on the fine retries). Nothing is a circle or a bounding box.
* **A router, not a straight-line trial.** Each stub is a Dijkstra shortest path through that grid,
  two-layer with a single B.Cu→F.Cu transition where the owner's F6/PLR-01 amendment allows one
  (J2/J9/J13 only). The grid is masked by the per-pad band depth, and the path's length *inside* the
  Rev2 outline is measured against the per-pad allowance — so a route that comes back is compliant
  by construction, not by inspection afterwards.
* **Clearance budget.** Obstacles are inflated by `0.24 mm + half the track width`; the Default
  netclass clearance is 0.2 mm and 0.24 covers it plus the 0.035 mm worst-case quantisation of the
  0.05 mm grid, so every path keeps ≥ 0.205 mm of real clearance. Per-net class clearances are
  honoured item by item (DRC takes the larger of the two nets' classes, so BenchPower's 0.25 mm
  applies to anything running next to a BenchPower net). Heritage copper *of the stub's own net that
  lands on the attachment pad* is excluded — overlapping it is the same electrical node and is how a
  stub leaves an already-routed pad; all other same-net heritage copper keeps 0.08 mm so no new
  track touches an existing one.
* **Heritage pours are a cost, not an obstacle.** Cells inside a non-GND heritage zone fill cost 3×,
  so a stub prefers to leave the flight section without carving a power pour. That is what keeps the
  `+3V3` fill inside the flight *core* identical this time (attempt 1 lost 28 mm² of it, §3).
* **Difficulty-ordered placement with rip-up/retry.** Nets are ordered by the free area reachable
  from their attachment pad (a flood fill), hardest first; when a net fails, the stubs whose copper
  passes within 6 mm of its candidate pads are ripped up, the failed net is placed first and the
  others put back — the arrangement is kept only if the stub count rises. That is what let `F3_SCL`
  and `F3_SDA` both through J13's single usable via slot, and `F2_SDA` through J11's.
* **Smaller stub vias.** The nine J2/J9/J13 layer changes use **0.46 mm pad / 0.20 mm drill** — a
  0.13 mm annular ring, exactly the board's minimum (the panel's 0.45/0.20 would be 0.125 and fail
  DRC) — and 0.07 mm more room per side than 0.6/0.3. Two stubs only fit because of it.
* **The autorouter is kept out of the flight section entirely.** All 32 stubs are hand-routed and
  fixed before Freerouting runs, so nothing legitimate is left for it to do inside the Rev2 outline.
  The keep-out fixture is therefore a blanket one — the whole Rev2 outline, tracks **and** vias, all
  four copper layers (`make_full_keepout.py` → `fc_keepout_full.json`) — instead of the stock
  `fc_keepout.json`, which leaves the band open between the heritage-copper polygons. That gap is
  what let attempt 1's run drop its own `VSOLAR` vias beside the hand-routed face stubs and short
  them (6 of its 13 shorts). With the blanket fixture the L11 gate came back **0 violations with no
  pruning at all** (`PRUNE=0` was set and nothing needed removing).

The `tools/pcb/attachment_check.py` first-match-wins bug attempt 1 reported (the generic `J14` row
silently overwriting the J14 pins 10/12 22 mm exception) **is already fixed upstream** — the live
file now reads `limit_of.setdefault(…)` with a "first matching row wins" comment. No tool change was
needed in this attempt and none was made to any shared script.

## 1. Recipe invocation

```
KEEPOUT_JSON=<scratch>/fc_keepout_full.json \
HERITAGE_SNAP=FlatSat_V1/tools/baseline/heritage_rev2.json \
REF_BOARD=FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb \
FR_TIMEOUT_MIN=150 PRUNE=0 \
  tools/pcb/route.sh <scratch>/pre/FlatSat_V1.kicad_pcb <scratch>/routed/FlatSat_V1.kicad_pcb 3
```

The shared `tools/pcb/route.sh` was used unmodified. PRE and OUT each sit in a full project
directory (board + `.kicad_pro` + `.kicad_dru` + schematics + libraries), which is what attempt 1's
"route.sh only copies the `.kicad_pro`" finding asks for; done that way the script needs no change.

Freerouting 2.4.1, `-mp 3 -mt 1`, 06:41→08:00 (**79 min**):

| stage | result |
|---|---|
| keep-out fixture | 39 `(keepout …)` + 4 `(via_keepout …)` records in the DSN; `FC_ALL` present on F.Cu/In1.Cu/In2.Cu/B.Cu |
| fanout | 9 passes, 279 s, 736/1448 SMD pins escaped (attempt 1: 20 passes, 648 s — the blanket keep-out removes the flight section's pins from the problem) |
| auto-routing | 455 unrouted at start → 346 (pass 1, 994 s) → 333 (pass 2, 841 s) → 333 (pass 3, 834 s) |
| optimisation | 1 pass, 822 s, stopped early ("50 consecutive items could not be improved") |
| merge | PRE 3472 + **1441 adopted** new tracks/vias; heritage byte-for-byte from PRE |
| gates straight out of route.sh | attachment **0 violations** (no prune), heritage **0 violations** |

The `score 0.00 (… 7395 violations)` reading throughout is the benign artefact `tools/pcb/README.md`
§7 documents: the fixed heritage wires sit inside their own DSN keep-out polygons.

## 2. L11 attachment stubs — 32 of 37 nets

37 shared nets (a pad on a heritage footprint **and** a pad on a Phase-2 footprint, GND excluded —
it is carried by the In1 plane and the new pours, brief L6). Each stub starts on one allowed pad,
stays on that pad's own layer (except the permitted J2/J9/J13 layer change), stays inside the band
and inside the per-pad length allowance. Every candidate pad of a net and both layers of every THT
pad were searched, so the pad chosen is the best of all legal options, not the first one tried.

| Net | Pad | Layer | Width (mm) | Inside (mm) / allowed | Via (0.46/0.20) |
|---|---|---|---|---|---|
| +3V3 | J16.6 | F.Cu | 0.500 | 3.03 / 14 | — |
| B- | J15.1 | F.Cu | 1.000 | 7.33 / 14 | — |
| BATT_SDA | J14.10 | F.Cu | 0.250 | 19.51 / 22 | — |
| Deploy1_EN | U6.3 | B.Cu | 0.250 | 10.72 / 14 | — |
| Dir_Chrg_In | J16.8 | F.Cu | 1.000 | 3.03 / 14 | — |
| F0_PWR | J6.4 | F.Cu | 0.300 | 10.82 / 14 | — |
| F0_SDA | J6.6 | F.Cu | 0.250 | 7.27 / 14 | — |
| F1_PWR | J9.4 | B.Cu | 0.300 | 8.77 / 14 | (221.63, 106.38) 0.46/0.20 |
| F1_SCL | J9.5 | B.Cu | 0.250 | 7.49 / 14 | (221.38, 109.48) 0.46/0.20 |
| F1_SDA | J9.6 | B.Cu | 0.250 | 7.98 / 14 | (221.38, 110.98) 0.46/0.20 |
| F2_PWR | J11.4 | F.Cu | 0.300 | 6.76 / 14 | — |
| F2_SCL | J11.5 | F.Cu | 0.250 | 6.77 / 14 | — |
| F2_SDA | J11.6 | F.Cu | 0.250 | 7.02 / 14 | — |
| F3_PWR | J13.4 | B.Cu | 0.300 | 7.04 / 14 | (222.58, 122.43) 0.46/0.20 |
| F3_SCL | J13.5 | B.Cu | 0.250 | 10.31 / 14 | (220.28, 124.53) 0.46/0.20 |
| F3_SDA | J13.6 | B.Cu | 0.152 | 10.73 / 14 | (222.98, 121.72) 0.46/0.20 |
| F4_PWR | J1.4 | F.Cu | 0.300 | 6.81 / 14 | — |
| F4_SCL | J1.5 | F.Cu | 0.250 | 8.10 / 14 | — |
| F5_PWR | J2.4 | B.Cu | 0.300 | 7.84 / 14 | (221.53, 92.83) 0.46/0.20 |
| F5_SCL | J2.5 | B.Cu | 0.250 | 7.34 / 14 | (222.38, 94.38) 0.46/0.20 |
| F5_SDA | J2.6 | B.Cu | 0.250 | 7.78 / 14 | (221.47, 95.88) 0.46/0.20 |
| FC_RESET | J16.2 | F.Cu | 0.250 | 3.03 / 14 | — |
| Heater_EN | R100.1 | B.Cu | 0.250 | 12.41 / 14 | — |
| INHIB_1 | J8.1 | F.Cu | 0.800 | 7.56 / 14 | — |
| INHIB_2 | J10.3 | F.Cu | 0.250 | 18.73 / 24 | — |
| IN_RBF | J29.1 | F.Cu | 0.250 | 7.24 / 14 | — |
| SCL_Top | J16.7 | F.Cu | 0.250 | 5.36 / 14 | — |
| SDA_Top | J16.5 | F.Cu | 0.250 | 5.36 / 14 | — |
| VBATT_SENSE | J8.2 | F.Cu | 0.800 | 7.32 / 14 | — |
| VBUSP | J30.1 | F.Cu | 0.250 | 8.12 / 14 | — |
| VSOLAR | J9.2 | B.Cu | 1.000 | 7.96 / 14 | (222.73, 106.68) 0.46/0.20 |
| WDT_DISABLE | J16.9 | F.Cu | 0.250 | 5.38 / 14 | — |

Nine of the thirty-two use the one permitted B.Cu→F.Cu layer change (owner ruling F6 / panel
PLR-01): F1_PWR/SCL/SDA at J9, F3_PWR/SCL/SDA at J13, F5_PWR/SCL/SDA at J2. Every via position was
individually verified free of F.Cu heritage copper and of every heritage drill — not assumed to be
at a common x. `BATT_SDA` uses the owner's 22 mm per-pad exception at J14.10 (F7 / PLR-02) with a
hand-traced jogged path, measured at 19.51 mm.

### The five nets with no legal stub — proven, not assumed

Each was re-run **first, on the bare placed board** (so no other stub could be blamed), on every
layer its pad carries, at every width down to 0.127 mm, and then again with a hypothetical 60 mm
length budget and with a hypothetical layer change permitted:

| Net | Pad | Free area reachable from the pad | Shortest path that exists at all | What would unblock it |
|---|---|---|---|---|
| `Deploy2_EN` | U6.6 (B.Cu) | **0.72 mm²** — the pad itself | none at any length, with or without a via | nothing short of moving heritage (L4 forbids it) or dropping the signal |
| `F0_SCL` | J6.5 (F.Cu) | **1.32 mm²** | none at any length, with or without a via | as above |
| `F4_SDA` | J1.6 (F.Cu) | **4.17 mm²** | none at any length, with or without a via | as above |
| `USBBOOT` | J16.1 (F.Cu 3.67 mm² / B.Cu 45.77 mm²) | none on either layer alone | **5.28 mm** with one B.Cu→F.Cu via at (225.97, 70.03) | **extending the F6/PLR-01 one-via amendment to J16** — that alone fixes it |
| `BATT_SCL` | J14.12 | large but no exit within 22 mm | **23.8 mm** with one layer change | the F6 amendment at J14 **and** a 24 mm allowance (the J7/J10/J20 precedent) |

The walls, item by item (`blocked.py`, exact-shape flood fill at the thinnest legal 0.127 mm track):

* **`Deploy2_EN` / U6.6** — U6's own GND thermal pad U6.29 (bbox 176.15–179.25) leaves 0.46 mm to
  the pad column's east edge (a 0.127 mm track needs 0.65 mm), the 0.65 mm-pitch pads U6.5 and U6.7
  box it north and south, and west the heritage `Heater_EN` diagonal (173.305,131.030)–(172.500,130.225),
  the `Deploy1_EN` via at (173.400,131.683) and the R100.1 pad close the last throat.
* **`F0_SCL` / J6.5** — heritage `F0_PWR` wraps the pin completely: (219.918,103.581)→(221.348,103.581)
  →(221.800,104.034)→(221.800,105.300)→(221.500,105.600)→J6.4, plus the `F0_PWR` via at
  (219.918,103.581), the GND via at (219.700,105.000) and the J6.4 pad.
* **`F4_SDA` / J1.6** — J1.5 and the R57/R58 pads, the `F4_SCL` escape, `FIRE_DEPLOY1_A`
  (217.870,85.444)–(220.092,85.444)–(223.020,88.372), the `+3V3` via at (219.200,86.000) and the two
  `VSOLAR` vias at (221.931,88.069) and (222.100,89.380).
* **`USBBOOT` / J16.1** — on F.Cu the heritage `FC_RESET` and `USB_D-` traces; on B.Cu the same
  `DEPLOY1` (226.800,82.300)–(226.800,65.300) / `PAYLOAD_BATT` wall the panel identified as PLR-01,
  **which extends further north than the panel's y 84.8–129.9 survey covered**. One via inside the
  band clears it.

**Recommendation to the PM/owner:** two of the five are one ruling away. Extending F6's "exactly one
B.Cu→F.Cu layer change inside the band" to **J16.1** recovers `USBBOOT` outright; extending it to
**J14.12** together with a 24 mm allowance (precedent: the J7/J10/J20 row already at 24 mm) recovers
`BATT_SCL`. The other three are hard geometry with heritage frozen: either the signal is dropped
from FlatSat V1 or the owner accepts a heritage change, which L4 forbids.

## 3. Heritage

```
$ heritage.py check tools/baseline/heritage_rev2.json <board> --allow-zone-growth --allow-edge
note: new items: footprints +221, tracks/vias +1974, zones +5
heritage check: 0 violation(s)

$ heritage.py check … --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb
note: zones refilled in memory before measuring (reference board too)
note: zone +3V3 on F.Cu:      band fill 311.3 -> 284.1 mm² (-8.7 %, stub carve-out)
note: zone VSOLAR on In2.Cu:  band fill 103.3 -> 102.7 mm² (-0.6 %, stub carve-out)
heritage check: 0 violation(s)
```

Two band-fill notes, both expected and explicitly allowed by L11 (the pours necessarily carve around
a stub inside the band). **Filled copper inside the flight core is identical to the refilled Rev2
board on every zone** — attempt 1's `+3V3` core loss of 384.8 → 356.5 mm² does not recur. The zone
penalty in the router (§0) is what bought that: stubs route around the `+3V3` F.Cu pour rather than
through it, so no island near the 12 mm line is orphaned by the refill.

## 4. L11 attachment gate

```
$ attachment_check.py tools/baseline/heritage_rev2.json <board>
attachment check: 1974 new tracks/vias, 32 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
```

No stub was pruned at any point: `route.sh` ran with `PRUNE=0` and its own gate reported 0 straight
out of the merge. `postmerge.py` (drop anything Freerouting adopted inside the Rev2 outline) was
written as a safety net and turned out to have nothing to do — the blanket keep-out held.

## 5. DRC

```
$ kicad-cli pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones …
$ drc_summary.py … --baseline tools/baseline/drc_prelayout.json
section            sev      type                             base    now  delta
schematic_parity   warning  extra_footprint                     1      1     +0
schematic_parity   warning  footprint_symbol_mismatch           5      5     +0
schematic_parity   warning  missing_footprint                 199      5   -194
schematic_parity   warning  net_conflict                       36      0    -36
unconnected_items  error    unconnected_items                   0     76    +76
violations         error    courtyards_overlap                  1      1     +0
violations         warning  footprint_type_mismatch             7      9     +2
violations         warning  isolated_copper                     4      4     +0
violations         warning  lib_footprint_issues                3      3     +0
violations         warning  track_dangling                      0     27    +27
violations         warning  via_dangling                        0      2     +2
errors: 77  unconnected: 76  parity: 11
```

`parity: 11` is exactly the brief §6 FC baseline. `courtyards_overlap: 1` is the accepted Rev2
SW2/TP2 item. `footprint_type_mismatch +2` (U200, U302) and `isolated_copper 4` / `lib_footprint_issues 3`
are unchanged build-stage/heritage items. **No `clearance`, `shorting_items`, `hole_clearance`,
`hole_to_hole`, `copper_edge_clearance` or `track_width` error remains** — the class attempt 1 could
not clear. 27 of the 29 dangling warnings are the L11 stubs' exposed outer ends, which stay open
until the extension side reaches them (the five blocked nets plus the connections in §8).

Reaching this state needed two rule-file changes, both of the kind the FC already uses and both
recorded here:

1. **`FlatSat_V1.kicad_dru`**: U511 (BQ25886, Texas RGE0024H VQFN-24) added to the existing
   `phase2-fine-pitch-pad-pitch` `memberOfFootprint` exemption. Its manufacturer land pattern has
   0.200 mm pad-to-pad gaps, which were legal at the Default 0.2 mm clearance and became violations
   the moment `CHG_BAT`/`CHG_SYS` actually reached the BenchPower class (see 2 below). 0.200 mm
   clears JLCPCB's 0.127 mm 4-layer minimum with margin; this is an intra-footprint exemption only,
   never a class-wide clearance reduction.
2. **`FlatSat_V1.kicad_pro` netclass patterns**: `VBAT_BENCH_N`, `CHG_SYS`, `CHG_BAT` and
   `MID_BENCH` are hierarchical nets (`/Battery Replica and Bench Power/…`), so the build stage's
   plain patterns matched **zero** nets and those four L5 BenchPower nets were silently on Default
   (0.25 mm track). Patterns corrected to `*/NAME`. `CHG_PMID` (listed in L5) does not exist on this
   board under any name and its pattern was dropped.

## 6. Netclasses applied for routing

| Class | Track | Clearance | Via | Nets |
|---|---|---|---|---|
| Default | 0.25 | 0.20 | **0.46/0.20** | everything else |
| BenchPower | 1.0 | 0.25 | 0.8/0.4 | VBUS_CHG, VBUS_EMU, VSOLAR_BENCH_A/B, `*/VBAT_BENCH_N`, `*/CHG_SYS`, `*/CHG_BAT`, `*/MID_BENCH` |
| **FCPower** (new) | 1.0 | 0.20 | 0.8/0.4 | Dir_Chrg_In, B-, VBUSP, VBATT_SENSE, INHIB_1, INHIB_2, IN_RBF, VSOLAR |
| **EmuRail** (new) | 1.0 | 0.20 | 0.46/0.20 | 3V3_EMU |
| USB_EMU | 0.25 | 0.20 | 0.6/0.3 | EMU_USB_DP, EMU_USB_DM |

* **FCPower** implements brief L5's "new tracks on Dir_Chrg_In / B- / VBUSP / VBATT_SENSE / INHIB_x /
  IN_RBF / VSOLAR at 1.5 mm where space allows, 1.0 mm minimum" by giving Freerouting the width
  directly. Its clearance is deliberately the Default 0.20 mm, not BenchPower's 0.25: those nets
  carry flight copper that was laid out to 0.2 mm, and re-judging it at 0.25 would have invented
  violations on frozen geometry. Verified empirically on this board first: **KiCad 10 DRC does not
  enforce a netclass track width**, so the heritage 0.152–0.635 mm tracks on these nets raise no
  `track_width` violation — the class only sets what new copper is routed at.
* **EmuRail** exists because 3V3_EMU is both an L5 BenchPower net *and* a rail that has to escape
  U200's 0.4 mm-pitch QFN ring. At BenchPower's 0.25 mm clearance no escape exists at all from the
  RP2350's 0.2 mm lands; at the Default 0.20 mm they do. The 1.0 mm L5 width is kept. The panel's
  own PLR-06 instruction already treats 3V3_EMU specially (In2 pour, 0.5 mm west branch), so this is
  within its intent, but it is a deviation from a literal reading of L5 and is flagged for the PM.
* **Default via 0.8/0.4 → 0.46/0.20** implements the panel's "U200 ESCAPE"/"U511 THERMAL"
  instruction. 0.45/0.20 as written would give a 0.125 mm annular ring and fail the board's 0.13 mm
  minimum; 0.46/0.20 is exactly 0.13. BenchPower and FCPower keep 0.8/0.4 for the bench currents.

The panel's **In2 3V3_EMU pour** (MAJOR PLR-06 / brief F9) was added: x 265–296, y 86–112, priority 0,
over the emulator core only. In2 carries 300 new tracks in total (the extension's third signal
layer, as the panel's layer budget intends).

## 7. Width audit of the L5 nets

Queried with pcbnew, per net, new copper separated from heritage copper (`audit.py`):

```
L5 nets -- brief L5 asks for 1.5 mm where space allows, 1.0 mm minimum on NEW copper
net                                new widths (mm: length)                   new mm    her mm layers
Dir_Chrg_In                        0.801:1.6, 1.000:49.9, 1.200:3.8, 1.500:34.4      89.7      89.9 F.Cu,In1.Cu,In2.Cu (+3 via)
B-                                 0.800:1.8, 0.801:1.2, 1.000:28.4, 1.200:4.8, 1.500:18.1      54.3       7.4 F.Cu,In1.Cu,In2.Cu (+5 via)
VBUSP                              0.250:1.4, 0.300:6.8, 0.500:0.8, 1.000:2.2      11.1     138.8 B.Cu,F.Cu 
VBATT_SENSE                        0.800:8.2, 1.500:5.8                        14.0      28.0 F.Cu,In2.Cu 
INHIB_1                            0.800:8.0, 1.000:8.8, 1.200:5.9             22.7       7.9 F.Cu,In2.Cu 
INHIB_2                            0.300:19.5, 1.000:10.0, 1.500:3.9           33.4       0.0 F.Cu,In2.Cu 
IN_RBF                             0.400:8.1, 1.500:12.6                       20.7       9.9 F.Cu,In2.Cu 
VSOLAR                             1.000:14.2, 1.500:30.1                      44.3      29.0 B.Cu,F.Cu,In2.Cu (+1 via)
VBAT_BENCH_N                       0.300:3.2, 0.400:7.1, 0.600:1.8, 0.800:5.7, 1.000:30.6, 1.200:2.8, 1.500:28.2      79.4       0.0 F.Cu,In1.Cu,In2.Cu (+3 via)
VSOLAR_BENCH_A                     1.500:33.6                                  33.6       0.0 F.Cu,In1.Cu (+1 via)
VSOLAR_BENCH_B                     1.000:17.5, 1.500:15.3                      32.8       0.0 F.Cu,In1.Cu (+1 via)
VBUS_CHG                           0.250:6.7, 0.300:5.1, 0.500:1.4, 1.000:11.8, 1.200:2.0, 1.500:13.4      40.4       0.0 B.Cu,F.Cu (+3 via)
CHG_SYS                            0.250:3.8, 0.600:4.1, 1.000:17.2, 1.500:12.8      37.9       0.0 F.Cu,In2.Cu (+2 via)
CHG_BAT                            0.250:18.3, 0.300:3.8, 0.500:1.6, 0.600:2.5, 1.500:15.9      42.1       0.0 F.Cu,In1.Cu,In2.Cu (+2 via)
VBUS_EMU                           0.250:6.0, 0.300:5.0, 0.400:0.3, 0.800:4.4, 1.000:36.9, 1.200:1.0, 1.500:13.8      67.4       0.0 F.Cu,In2.Cu (+8 via)
MID_BENCH                          0.400:14.1, 0.500:10.3, 0.600:5.9, 1.000:2.5, 1.200:1.2, 1.500:12.4      46.4       0.0 B.Cu,F.Cu,In1.Cu,In2.Cu (+2 via)
3V3_EMU                            0.127:15.2, 0.152:2.1, 0.200:2.3, 0.250:0.9, 0.400:3.1, 0.500:9.8, 0.600:8.5, 0.800:0.7, 1.000:164.7, 1.200:5.8, 1.500:16.8     229.8       0.0 B.Cu,F.Cu,In2.Cu (+17 via)
```

Every FCPower and BenchPower net carries 1.0–1.5 mm on its new copper. The sub-1.0 mm entries are
all L11 stub segments *inside the attachment band*, where the heritage density sets the width — the
router took the widest that fits and a post-pass (`widen.py`, exact-shape re-test of every segment's
whole centre line) grew 173 segments afterwards, most of them to 1.5 mm. The two that stayed thin:

* `VBUSP` — 0.25–0.5 mm on its J30.1 stub; the bottom-edge wall of `IN_RBF`/`INHIB_1`/`FIRE_DEPLOY1_A`
  traces leaves no more.
* `INHIB_2` — 0.30 mm through the J10.3 → strip run for the same reason, 1.0/1.5 mm beyond it.

Both are bench-current paths only at their far end; the narrow section is the stub inside the flight
section, which is also the shortest.

## 8. USB pair

```
USB pair
  EMU_USB_DP               2 seg, 1.644 mm, widths [0.127], layers F.Cu, 0 via(s)
  EMU_USB_DM               2 seg, 1.644 mm, widths [0.127], layers F.Cu, 0 via(s)
  Net-(J701-D+-PadA6)      17 seg, 52.591 mm, widths [0.2, 0.25], layers F.Cu, 0 via(s)
  Net-(J701-D--PadA7)      9 seg, 43.026 mm, widths [0.2, 0.25], layers B.Cu,F.Cu,In2.Cu, 5 via(s)
  EMU_USB_DP/DM skew: 0.000 mm (L5 tolerance 1 mm)
  J701 D+/D- (pre-resistor) skew: 9.565 mm
```

`EMU_USB_DP` / `EMU_USB_DM` are the coupled pair proper (from R703/R704 to U200): **F.Cu only, zero
vias, 1.644 mm each, skew 0.000 mm** against L5's 1 mm tolerance, over the uncut In1 GND plane. They
run at 0.127 mm rather than L5's 0.25 mm because the RP2350's 0.200 mm QFN lands cannot carry a
0.25 mm track without breaking the 0.2 mm clearance to pins 51/53 — a neck-down at the pad, over
1.6 mm. Getting them placed needed the copper in x 269.5–278.5 / y 87.5–93.5 ripped up and the pair
laid down first; the rest of that region was then re-routed around them.

`Net-(J701-D+-PadA6)` / `Net-(J701-D--PadA7)` are the pre-resistor nets (Default class; panel PLR-03
confirms the "no vias" rule begins at R703/R704). J701's rows interleave — physical order along x is
B5 CC2, **B6 D+**, **A7 D−**, **A6 D+**, **B7 D−**, A5 CC1 — so each pair is joined round the pad
field, never across it. This is the pad-pairing attempt 1's `usb_pair.py` got wrong and shorted.
Their 9.6 mm length difference is not a matched-pair requirement, but it is worth tightening at
stage 5 or 6.

## 9. Unconnected — all 76 triaged

| # | Cause | Items |
|---|---|---|
| A | the five nets with no legal L11 stub (§2) | 5 |
| B | emulator-core escape: U200's QFN-60 ring is saturated | 29 |
| C | a GND pad with no reachable via site within 5 mm | 16 |
| D | everything else, all with one end on the U200/U511 fine-pitch rings or their immediate corridors | 26 |

**B and D are one problem.** The RP2350 QFN-60 has 0.200 mm lands on 0.4 mm pitch: no track of any
legal width fits between adjacent pads, so every escape is radial, and a 0.46/0.20 via needs
0.86 mm of free annulus. The panel measured U200's median annulus at 1.030 mm with 15 pads at
0.520–0.541 mm, and its own instruction was to reserve the thirteen 0.890–1.160 mm alleys for the
QSPI group. With the datasheet-audited decoupling placed 0.5–1 mm off the package (stage 2b, and
correctly so), there is room for roughly one staggered via row, not two — so a fraction of the 60
pins cannot escape at all in the space available. 342 connections in that core *were* closed; these
are the remainder. Nothing here is a rule violation: the copper that exists is DRC-clean.

**C**: GND is carried by the In1 plane and the new F.Cu/B.Cu pours, and `gndvia.py` stitched 11
pads to it with a short track and a 0.46/0.20 via (which also discharges the panel's "DECOUPLING GND
VIAS" instruction for the caps it reached). The 16 that remain are pads whose own escape is blocked:
U316.4, C205.2, U303.4, U303.8, U200.47, U511.20 and their partners. Same cause as B.

Closing B/C/D needs one of: (a) a further routing pass with more wall-clock budget than this stage
had, now that the board is DRC-clean and every remaining item is isolated; (b) a small placement
relaxation around U200 and U303 (moving two or three decoupling caps 0.2–0.3 mm further out would
open a second via row) — that is a stage-2b decision, not a routing one; or (c) accepting a handful
of emulator signals as unpopulated on FlatSat V1.

## 10. Tooling written for this stage (scratch, not shared repo files)

`rgeo.py` (exact-shape raster geometry + Dijkstra), `plan2.py` (L11 stub planner with difficulty
ordering and rip-up/retry), `pairfix.py`, `blocked.py` / `whatif.py` / `probe.py` (the blockage
proofs in §2), `make_full_keepout.py`, `postmerge.py`, `mlroute.py` (F.Cu/In2.Cu/B.Cu router),
`closeup.py` (route what DRC calls unconnected), `fixdrc.py` (rip up what DRC objects to, never
heritage or a stub), `trimdangle.py`, `gndvia.py`, `widen.py`, `usb.py`, `audit.py`, `gates.sh`.
All live in the routing scratch directory. **No shared script under `FlatSat_V1/tools/` was
modified by this stage.**

## 11. Open issues for the PM

1. **76 unconnected** (§9). Not a rule violation; needs another routing pass, a small placement
   relaxation at U200/U303, or a scope decision.
2. **Two owner rulings would recover two more L11 nets** (§2): extend F6's one-via amendment to
   J16.1 (`USBBOOT`, verified 5.28 mm path) and to J14.12 with a 24 mm allowance (`BATT_SCL`,
   verified 23.8 mm path). `Deploy2_EN`, `F0_SCL` and `F4_SDA` have no path at any length on any
   layer and need a scope decision.
3. **`EmuRail` netclass for 3V3_EMU** (§6) is a documented deviation from a literal L5 reading
   (clearance 0.20 instead of BenchPower's 0.25, width unchanged at 1.0 mm); it is required for the
   rail to escape U200 at all. Please confirm or overrule.
4. **`FlatSat_V1.kicad_pro` netclass patterns were wrong in the build-stage board** (§5.2): four L5
   BenchPower nets matched nothing. Worth a check in `netclasses.py` so hierarchical net names are
   handled at the source.
5. **68 short signal segments on In1.Cu** placed by Freerouting nick the GND plane in the extension.
   Only one was inside the panel's protected zones (under U200 / the USB corridor) and it was
   removed and re-routed. The remaining 68 are in the wing/strip and are a stage-5 tidy-up item, not
   a rule breach.
6. **`Net-(J701-D+-PadA6)` vs `Net-(J701-D--PadA7)` differ by 9.6 mm** (§8). Not a matched pair by
   L5, but worth tightening.
7. **`route.sh` and the project siblings**: running it with PRE and OUT inside full project
   directories avoids attempt 1's inflated `lib_footprint_issues`/`clearance` counts without any
   change to the shared script. Worth writing into `tools/pcb/README.md`.

---

# Closure stage (attempt 1, Opus, 2026-09-20)

**Input:** `scratchpad/layout_route2/deliver/FlatSat_V1.kicad_pcb` (attempt 2: heritage 0, attachment 0,
DRC clean except **76 unconnected**).
**Delivered board:** `scratchpad/layout_close1/deliver/FlatSat_V1.kicad_pcb` (with its
`.kicad_pro` / `.kicad_dru` / schematics / libraries beside it).
**Renders:** `scratchpad/layout_close1/render/{top,bottom,in1,in2,all_copper}.pdf`.

| Gate | Attempt 2 in | Closure out |
|---|---|---|
| `heritage.py check --allow-zone-growth --allow-edge` | 0 | **0** |
| `heritage.py check --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2` | 0 (2 band notes) | **0** (2 band notes: `+3V3` F.Cu 291.8 → 273.7 mm², `VSOLAR` In2 85.8 → 85.2 mm², both stub carve-out) |
| `attachment_check.py` (L11) | 0 viol / 0 warn, 32 stubs | **0 viol / 0 warn, 35 stubs** |
| DRC `clearance` / `shorting_items` / `hole_clearance` / `hole_to_hole` / `copper_edge_clearance` / `track_width` | 0 | **0 of each** |
| DRC `courtyards_overlap` | 1 (Rev2 SW2/TP2) | 1 (same) |
| DRC schematic parity | 11 = §6 baseline | **11 = §6 baseline** |
| DRC unconnected | 76 | **39** (−37, −49 %) |
| DRC `track_dangling` / `via_dangling` | 27 / 2 | 19 / 0 |

## C1. What closed, and how

**C1.1 The three new attachments (F11/F12 rulings), +3 stubs → 35.**

| Net | Pad | How | Inside / allowed |
|---|---|---|---|
| `USBBOOT` | J16.1 | B.Cu stub with the one permitted B.Cu→F.Cu via at **(225.93, 70.03)** (F11a) | 4.4 / 14 mm |
| `BATT_SCL` | J14.12 | B.Cu stub with one via at **(216.28, 129.62)**, 0.152 mm width (F11a + the 24 mm allowance) | 23.9 / 24 mm |
| `F0_SCL` | J6.5 | **F12 trace tap**: the stub ends *on* the net's own heritage F.Cu trace at **(219.030, 104.011)**, 1.79 mm from the pad (limit 2.5 mm). Heritage geometry byte-identical; `attachment_check` reports `TAP on heritage F.Cu … (F12)` | 13.4 / 14 mm |

The first via attempt for `USBBOOT` landed 0.194 mm from the heritage `Dir_Chrg_In` In2 track: the
stub planner's via-obstacle mask only covered the two **outer** layers. A through via meets In1/In2
copper too — fixed, and the same bug is worth checking in any future stub planner.

**C1.2 The J6+J9 face pair had to be replanned as one group.** `F0_SCL`'s tap escapes only if
`F0_PWR`'s stub is not already in the single 0.29 mm-wide throat between the J6.3 and J6.2 lands
(y 107.85–108.15, the only F.Cu link between x < 220 and x > 222.4 at that height). And J9's
bottom-side stubs surface onto F.Cu **inside J6's escape region** (`F1_PWR`'s via was at
(221.63, 106.38), its diagonal crossing J6.4/J6.5's only exit). So J6 and J9 are one routing problem,
not two. Ripping the seven stubs of the pair and replanning them in the order
`F0_SCL → F0_PWR → F0_SDA → VSOLAR → F1_PWR → F1_SCL → F1_SDA` places **7 of 7**; five other orders
place only 6. All nine J6/J9/J16/J14 stubs are re-measured in the table at the end of this section.

**C1.3 Connectivity is now driven by KiCad's own connected components, not by the DRC item list.**
Attempt 2's `closeup.py` took the two items kicad-cli names for an unconnected pair and substituted
"the nearest new-track endpoint outside the Rev2 outline" for any anchor inside the flight section.
That substitution frequently landed **in the island it was starting from**, and the router then
"closed" the connection with a 0.0 mm path — 20 of its 40 reported closures did nothing.
`close2.py` instead builds the real clusters with `CONNECTIVITY_DATA::GetConnectedItems`, routes
between the two nearest *clusters* with masks rasterised from those clusters' own copper, merges and
repeats. A second defect fell out of the same review: the "nearest pair of points" must be chosen
from points **outside** the Rev2 outline, or the routing window is laid across the flight core and
the net (e.g. `Dir_Chrg_In`, `+3V3`, `VSOLAR`) fails for a reason that has nothing to do with the
real path. With both fixed, 43 connections closed, including every remaining
stub-to-extension join: `+3V3`, `B-`, `Dir_Chrg_In`, `INHIB_1`, `INHIB_2`, `IN_RBF`, `VBATT_SENSE`,
`VBUSP`, `VSOLAR`, `WDT_DISABLE`, `FC_RESET`, `USBBOOT`, `BATT_SCL`, `F0_SCL`, `F0_PWR`, `F0_SDA`,
`F1_PWR`, `F1_SCL`, `F1_SDA`, `F4_SCL`, `EMU_BATT_SCL`, `EMU_F1_SCL`, `EMU_F2_SCL`, `EMU_F4_SCL`,
`EMU_F4_SDA`, `EMU_GPIO_SPARE0`, `F0_DEV_SDA`, `MID_BENCH`, `CHG_SYS`, `VBAT_BENCH_N` (×2), `3V3_EMU` (×5).

**C1.4 `EMU_VREG_LX` — the RP2350's buck switch node — is connected.** U200.48 → L200.1 was open
because a 0.600 mm `3V3_EMU` track sat 0.285 mm off the pin 46–50 land tips, closing the north alley.
Removing that one 5-item branch (x 274.55–277.20, y 90.00–91.00) let an exact-geometry fan-out place
a 0.46/0.20 via at **(275.145, 90.550)**; the node then routed in 3.10 mm, and `3V3_EMU` re-routed
around it. `EMU_QSPI_SS` and two `3V3_EMU` joins came with it.

**C1.5 Three GND pads stitched to the In1 plane** under F11(4) (a GND track of any length to a
reachable via): `C213.2` via (277.380, 89.658), `C200.2` via (293.490, 95.677) — 1.55 mm out —
and `U303.4` via (273.474, 121.390) with a 2-segment 0.3 mm track. Every candidate was tested
against KiCad's own polygons, not a raster.

**C1.6 One degenerate double via collapsed.** `close2` had produced a `VSOLAR` F.Cu→In2→B.Cu pair
0.283 mm apart (hole-to-hole minimum 0.4995 mm, a new DRC error). `tidy.py` removes the inner-layer
stub and the second via and extends the 1.000 mm F.Cu track to the surviving via at
(235.883, 131.234) — the replacement segment is exact-geometry verified before it is kept. DRC
`hole_to_hole` is back to 0.

## C2. Capacitor moves — attempted under F11(4), **reverted**, nothing moved

The ruling allows moving decoupling/bootstrap capacitors at U200/U303/U511 outward by ≤ 0.30 mm.
That was tried at U200 and measured:

| Ref | Before (mm) | After (mm) | Delta |
|---|---|---|---|
| C204 | (267.910, 92.120) | (267.644, 91.981) | (−0.266, −0.139) |
| C205 | (267.910, 96.940) | (267.631, 97.051) | (−0.279, +0.111) |
| C212 | (270.870, 90.150) | (270.739, 89.880) | (−0.131, −0.270) |
| C217 | (278.800, 92.400) | (279.075, 92.281) | (+0.275, −0.119) |
| C219 | (267.910, 94.530) | (267.611, 94.511) | (−0.299, −0.019) |

**Result: the move opened no new via site and cost one** (C213.2's stitch, which succeeds without the
move, fails with it). The binding constraint at U200 is not the caps' standoff — it is routed copper
already occupying the annulus, and underneath that the 0.4 mm land pitch (see C3). The moves were
therefore reverted and **the delivered board's placement is bit-identical to floorplan v2.3**
(`heritage.py` sees footprints +221 unchanged; no `apply_placement` diff). Recorded here because the
PM asked for before/after coordinates whether or not the move is kept.

## C3. Why the U200 ring cannot be finished with the rules as they stand

21 of the 23 remaining signal connections have one end on a U200 land. This was measured three ways.

* **The lands.** U200's pads are **0.200 × 0.875 mm on 0.400 mm pitch**. At the Default 0.20 mm
  clearance a 0.127 mm track leaving a land along its own axis has **0.0015 mm** of lateral slack
  against its neighbours (0.400 − 0.100 − 0.200 − 0.0635). No practical raster can represent that, which
  is why every raster attempt (attempt 2's and this stage's) reports "escape room = 0.038 mm² = the
  pad itself". A fan-out therefore has to be **constructed and checked with KiCad's own polygons**
  (`TransformShapeToPolygon` + boolean intersection), which is what `fanout.py` does.
* **The via arithmetic.** A 0.46/0.20 via (0.13 mm annular ring = the board minimum; smaller fails
  the rule) needs 0.66 mm centre-to-centre for clearance and **0.70 mm for hole-to-hole**. On 0.400 mm
  land pitch that is one via per *two* lands. A second, outer via row is geometrically fine
  (0.6 mm further out clears 0.70 mm diagonally) but **unreachable**: the track to it must pass
  between two inner-row vias 0.80 mm apart, a 0.34 mm gap where 0.127 + 2 × 0.20 = **0.527 mm** is needed.
  So a single fan-out row is the hard limit for through vias at this pitch: **≈ 1 escape per 0.8 mm
  of package edge ≈ 35 for U200's 28 mm perimeter.**
* **The empirical check.** Stripping every new item from U200's 0.85 mm alley ring (124 items) and
  re-running the exact fan-out places **20 vias + 27 radial stubs** — *worse* than the 35 escapes the
  board already carries. The delivered arrangement is therefore kept; it is at or very near the
  practical maximum for this footprint, this via, and this clearance rule.

For reference, the flight board solves the same problem differently: **U18 (the flown RP2350) has only
24 vias within 5.5 mm of the package and 266 tracks at 0.152 mm** — it fans out on F.Cu and vias down
well clear of the ring. FlatSat's U200 cannot copy that because the datasheet-audited decoupling ring
(stage 2b) occupies the annulus at ~1.03 mm, leaving ~3 circumferential track slots per side.

**What would close them** (owner/PM decisions, none taken here):
1. **Via-in-pad on U200** (JLCPCB resin-plug + cap): removes the pitch limit outright. Fab-spec change.
2. **A 0.40/0.20 via for the U200 ring only** (0.10 mm annular ring vs the board's 0.13 mm minimum):
   a `.kicad_dru`/board-setup change scoped to the ring, worth ~8 more escapes by arithmetic.
3. **Re-place the emulator core** with a larger decoupling standoff than 0.3 mm — a stage-2b decision,
   and it would re-open the audited datasheet rules.
4. **Scope**: accept the 21 emulator signals below as unpopulated on FlatSat V1.

## C4. Still open — 39 unconnected

**16 GND** — GND is carried by the In1 plane and the new F.Cu/B.Cu pours (L6). What remains:
* 9 pads inside the U200 annulus with no legal 0.46/0.20 via site within 6 mm at any width down to
  0.127 mm (C204.2, C205.2, C212.2, C217.2, C219.2, U200.47, U303.8, U316.4, and the U200 EP return
  path) — same cause as C3.
* 5 isolated islands of the `GND_F_Cu_wing` pour that need a stitching via each (a stage-5 item:
  the island positions are not in the DRC output, they need a `FillIsolatedIslandsMap` pass).
* 1 pre-existing item between **U6.1 and U6.29** — both heritage pads on a heritage footprint. It was
  present in attempt 2 as well. Adding copper there would breach L4/L11, so it is left alone and is
  listed here as an FC-baseline observation, not Phase-2 work.

**21 emulator signals on U200 lands** (C3): `1V1_EMU` (×2), `EMU_QSPI_SD0`, `EMU_QSPI_SD2`,
`EMU_SWCLK`, `EMU_SWDIO`, `EMU_UART_TX`, `EMU_CTL_FC_RESET`, `EMU_CTL_USBBOOT`, `EMU_CTL_WDT_DIS`,
`EMU_TOP_SCL`, `EMU_BATT_SDA`, `EMU_F2_SDA`, `EMU_F3_SCL`, `EMU_F1_SENSE`, `EMU_F2_SENSE`,
`EMU_F3_SENSE`, `EMU_F5_SENSE`, `EMU_FC3V3_SENSE`, `EMU_STATUS_LED`, `PYRO_INHIBIT_STATE`.
Note `EMU_SWCLK`/`EMU_SWDIO` (the emulator's own SWD header J702) and `EMU_QSPI_SD0/SD2` (two of the
four flash data lines) are in this set — an unpopulated-scope decision would have to cover them.

**2 that need an owner ruling** — both re-measured on the delivered board:

| Net | Pad | Measured | Ruling that would close it |
|---|---|---|---|
| `F4_SDA` | J1.6 | The F12 tap **works** (a path exists from the heritage trace at (219.61, 87.59)), but the shortest path to the extension is **17.9 mm inside** the flight section at 0.127 mm — J1's allowance is 14 mm. Re-measured with the J1 *and* J2 stubs ripped and with the zone penalty off, so it is the true minimum: the direct east exit is closed by the heritage `FIRE_DEPLOY1_A` diagonal (220.092, 85.444)–(223.020, 88.372) touching the `VSOLAR` via at (221.931, 88.069) (0.556 mm centre-to-line vs the 0.618 mm needed), so the path has to go south around J1/J2. | A **per-pad allowance of 20 mm for J1 pin 6**, precedent J7/J10/J20 and J14.10/12 at 24 mm. One line in `attachment_check.ALLOWED_PADS`. |
| `Deploy2_EN` | U6.6 | **No path at any width on any layer, with or without the tap.** The F12 via tap at (173.500, 130.100) gives a 9.26 mm² F.Cu pocket bounded by a 0.635 mm heritage diagonal to the east, the bottom-edge F.Cu wall (y 136.2–141.1 solid for x < 178.7) to the south, and the 14 mm band cap to the north. Proven by exact-shape flood fill at 0.127 mm with `Deploy1_EN` and `Heater_EN` also ripped, so no other stub is to blame. | Only a heritage change (L4 forbids), a band allowance past 14 mm **and** a route through the x 178.7–182 corridor, or dropping the signal. The extension side is already routed to (173.25, 149.49) and waits for a tap. |

## C5. Tooling written for this stage

Scratch only (`scratchpad/layout_close1/`), **no shared file under `FlatSat_V1/tools/` was modified**:
`plan3.py` (L11 stub + F12 tap planner), `escape.py` / `map.py` / `probe2.py` (blockage proofs),
`ripstub.py` / `ripbox.py` / `ripring.py` (surgical rip-up), `clusters.py` (KiCad-connectivity
components), `close2.py` (cluster-aware closer), `fanout.py` (exact-geometry fine-pitch fan-out),
`gndclose.py` (GND-to-plane stitching), `movecaps.py` (the F11(4) cap move, with track ends carried),
`tidy.py` (double-via collapse), `gates.sh`.

Two of these are worth promoting into `tools/pcb/` for the next stage: **`clusters.py`** (every
"is this net connected" question in Phase 2 has been answered wrongly at least once by reading the
DRC list instead) and **`fanout.py`** (nothing else on the board can escape a 0.4 mm-pitch land).

---

# Closure stage, round 2 (attempt 1, Opus, 2026-09-20)

**Input:** `scratchpad/layout_close1/deliver/FlatSat_V1.kicad_pcb` (closure round 1: heritage 0, attachment 0,
DRC clean except **39 unconnected**).
**Delivered board:** `scratchpad/layout_close2/work/deliver/FlatSat_V1.kicad_pcb`
(`.kicad_pro` / **`.kicad_dru`** / schematics / libraries beside it — the `.kicad_dru` is part of the
deliverable, it carries the two new `EMU_FANOUT` rules).
**Renders:** `scratchpad/layout_close2/render/{top,bottom,in1,in2,all_copper}.pdf`.

| Gate | Round 1 in | Round 2 out |
|---|---|---|
| `heritage.py check --allow-zone-growth --allow-edge` | 0 | **0** |
| `heritage.py check --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2` | 0 (2 band notes) | **0** (2 band notes: `+3V3` F.Cu 291.3 → 274.0 mm², `VSOLAR` In2 91.8 → 91.2 mm², both stub carve-out) |
| `attachment_check.py` (L11) | 0 viol / 0 warn, 35 stubs | **0 viol / 0 warn, 36 stubs** |
| DRC `clearance` / `shorting_items` / `hole_clearance` / `hole_to_hole` / `copper_edge_clearance` / `track_width` / `annular_width` / `via_diameter` | 0 | **0 of each** |
| DRC `courtyards_overlap` | 1 (Rev2 SW2/TP2) | 1 (same) |
| DRC schematic parity | 11 = §6 baseline | **11 = §6 baseline** |
| DRC unconnected | 39 | **29** (−10, −26 %) |
| DRC `track_dangling` / `via_dangling` | 19 / 0 | 15 / 23 (each one is an escape via whose onward route is still open — see D5) |

Board statistics: min track clearance 0.1338 mm (inside `EMU_FANOUT` only), min track width 0.127 mm,
min drill 0.200 mm, 945 through vias, 483 footprints.

## D1. EMU_FANOUT — the rule area, and the proof that it does what the PM specified

A constraint-only rule area (`pcbnew.ZONE` with `SetIsRuleArea(True)`, every keep-out flag **off**,
all four copper layers) named **`EMU_FANOUT`** covers **x 266.5–280.0 / y 88.0–101.5**, and
`FlatSat_V1.kicad_dru` gained:

```
(rule "emu_fanout"
	(condition "A.intersectsArea('EMU_FANOUT') && B.intersectsArea('EMU_FANOUT')")
	(constraint clearance (min 0.127mm)))

(rule "emu_fanout_via"
	(condition "A.Type == 'Via' && A.intersectsArea('EMU_FANOUT')")
	(constraint annular_width (min 0.10mm))
	(constraint via_diameter (min 0.40mm))
	(constraint hole_size (min 0.20mm)))
```

**Verification (deliberate probes, DRC'd, then removed).** Four identical test items were inserted,
two inside the area and two outside, and `kicad-cli pcb drc` was run on the project directory:

| Probe | Geometry | Inside EMU_FANOUT | Outside |
|---|---|---|---|
| Track pair, 0.127 mm wide, **0.130 mm** edge gap | (266.80, 88.30)/(266.80, 88.557) vs (283.50, 88.30)/(283.50, 88.557) | **no violation** | `clearance` error: *netclass 'Default' clearance 0.2000 mm; actual 0.1300 mm* |
| Via **0.40 / 0.20** (0.10 mm annular ring) | (278.10, 99.40) vs (287.00, 92.00) | **no `annular_width` violation** | `annular_width` error: *board setup constraints min annular width 0.1300 mm; actual 0.1000 mm* |

The in-area probe also produced a `clearance` error reading *rule 'emu_fanout' clearance 0.1270 mm*
against unrelated copper it happened to land on, which is the positive proof that the named rule is
the one being applied there. **`hole_clearance` (0.20 mm) and `hole_to_hole` (0.50 mm) are NOT
relaxed by these rules** — DRC reported them at the board minimum inside the area as well — so the
fan-out below is designed against 0.70 mm centre-to-centre for 0.20 mm drills.

Both relaxed numbers sit inside JLCPCB's published 4-layer capability (0.09/0.09 mm track/space,
0.15 mm hole / 0.25 mm via pad) and follow the same scoped-relaxation practice as the FC's own
`fine-pitch-pad-pitch` rule.

## D2. U200 re-fan — what the geometry actually allows

**The ring was ripped and rebuilt.** 236 new tracks/vias inside x 268.34–277.95 / y 90.05–99.66 were
removed (everything except `EMU_USB_DP`, `EMU_USB_DM`, `EMU_XIN`, `EMU_XOUT`, `EMU_VREG_LX`,
`VREG_AVDD_EMU`, whose short local links are datasheet-critical and already correct), and all 53
escapable lands were re-planned by `fan2.py`, an exact-polygon planner
(`TransformShapeToPolygon` + boolean intersection) that applies the real per-item rule: 0.127 mm
where both items intersect `EMU_FANOUT`, 0.20 mm otherwise, 0.20 mm hole clearance, 0.50 mm
hole-to-hole, 0.20 mm copper-to-edge. **51 of 53 placed.**

**The rows that made it work.** U200's lands are 0.200 × 0.875 mm on 0.400 mm pitch, tips at
x 269.270 / 277.020 and y 90.980 / 98.730.

* **Outer row** — 0.55 mm past the land tips (west x 268.720, east x 277.570, north y 90.430,
  south y 99.280). Within a row, vias are 0.80 mm apart (≥ the 0.70 mm that two 0.20 mm drills need
  for the un-relaxed 0.50 mm hole-to-hole rule), i.e. one via per two lands.
* **Inner alley** — the 1.30 mm gap between the land inner ends and U200's exposed pad
  (west x 270.145→271.445, east 274.845→276.145, north 91.855→93.155, south 96.555→97.855).
  This is the second row, and because it is 1.30 mm wide it takes **two radially staggered
  sub-rows** 0.58 mm apart (west x 270.505 / 271.085, east 275.205 / 275.785, north y 92.215 /
  92.795, south y 97.205 / 97.495). Diagonal neighbours are then
  √(0.58² + 0.40²) = **0.705 mm** apart — just over the 0.70 mm hole-to-hole floor — so the alley
  alone can take a via at **every** 0.400 mm land. That stagger, not the outer row, is what turns
  ≈ 35 escapes into 51.
* **0.127 mm tracks** from the land to its via. Where a land's own row slot is occupied the track
  passes **between two row vias**: 0.80 mm centres − 0.40 mm via = **0.400 mm** of gap against the
  0.127 + 2 × 0.127 = **0.381 mm** a minimum track needs (margin 0.0095 mm). These are constructed
  and verified, never searched — the planner tries 1-, 2- and 3-segment paths (radial out, lateral
  jog, run to the via) and keeps only what the exact polygon test passes.
* **Rail lands share.** A 3V3_EMU or 1V1_EMU land whose row slot is gone connects on F.Cu to its own
  decoupling-cap pad or to a neighbouring same-net land's via instead of consuming a via of its own
  (U200.1 → C204.1, .6 → C219.1, .11 → C205.1, .23 → C216.1, .30 → C207.1, .39 → C218.1,
  .45 → pad 44's via, .49 → C213.1, .54 → pad 53's via). That is the datasheet connection anyway and
  it freed nine ring slots for signals.

**69 vias at 0.40 / 0.20** are now in the ring; the 47 pre-existing 0.46 mm vias inside the area were
shrunk to 0.40 mm (legal under `emu_fanout_via`, and the 0.03 mm it frees all round is exactly what
opens the "pass between two vias" corridors).

**The two lands with no site:** `U200.18` (`EMU_CTL_FC_RESET`, south x 271.145) and `U200.60`
(`EMU_QSPI_SS`, north x 270.345) — both corner lands whose outer-row window is closed by a
decoupling cap (C206 at 0.540 mm from the south tips, C212 at 0.520 mm from the north tips: a
0.40 mm via needs 0.654 mm) and whose alley slots are taken by the adjacent side's alley, which
crosses at the corner. Moving one 0603 cap 0.30 mm outward (ruling F11(4), still open) would give
each of them an outer-row site.

## D3. Capacitor moves — none

The PM's note for this round says to keep the caps where they are, and nothing was moved. The
delivered placement is bit-identical to floorplan v2.3 (`heritage.py` reports footprints +221
unchanged, no `apply_placement` diff). Round 1's measured before/after table (C204, C205, C212,
C217, C219) stands in section C2 above and is the record of the only move ever attempted.

## D4. The two L11 attachments

| Net | Pad | How | Inside / allowed |
|---|---|---|---|
| `F4_SDA` | J1.6 | **Closed.** F12 trace tap ending on the net's own heritage F.Cu track at **(218.685, 88.515)**, 1.36 mm from the pad. The J1/J2 group had to be replanned as one: with the six stubs `F4_SDA, F4_SCL, F4_PWR, F5_PWR, F5_SCL, F5_SDA` ripped and replanned **in that order** all six place; with `F4_SDA` anywhere later, `F4_SCL` or `F4_SDA` loses its corridor. Zone penalty off. | **18.8 / 20 mm** (F13c) |
| `Deploy2_EN` | U6.6 | **Still open — no compliant path exists at 24 mm either.** See D6. | — |

36 stubs now enter the flight section, 0 violations, 0 warnings.

## D5. What closed, and how

* **+6 U200 signals** closed outright by the re-fan and the onward routing:
  `1V1_EMU` (×2), `EMU_QSPI_SD0`, `EMU_QSPI_SD2`, `EMU_CTL_USBBOOT`, `EMU_F5_SENSE`.
* **F4_SDA** closed (D4).
* **+5 GND** closed: `U202.2`, `C204.2`, `C205.2`, `C209.2`, `C213.2`, `Y200.4`, `U311.4`,
  `R515.2`, `R517.2` stitched to the In1 plane with a 0.30 mm F.Cu track to a via; one
  `GND_F_Cu_wing` island joined by a 2.89 mm F.Cu link at (269.940, 101.650)→(271.960, 99.580).
* **47 reconnections** of nets whose ring copper the rip removed: 17 by `stitch.py`
  (exact-geometry 1- and 2-segment links, rule-area aware) and 30 by `close2.py` (the round-1
  cluster-aware raster closer).
* **4 more** by `micro.py`, a new area-aware fine router written for this round (see D7):
  `3V3_EMU`, `EMU_GPIO_SPARE0`, `EMU_GPIO_SPARE1`, `EMU_TOP_SDA`.

The 23 `via_dangling` warnings are one-for-one the escape vias of the 17 signals in D6 that have a
verified escape out of the QFN ring but no onward route yet — they are deliberately kept, because
the expensive part (getting off a 0.4 mm-pitch land) is done and the next stage only has to route
from the via.

## D6. Still open — 29 unconnected

**11 GND.**
* 9 pads with no legal via site inside the now much denser ring and no clear F.Cu path to the
  exposed pad: `C207.2`, `C208.2`, `C212.2`, `C215.2`/`C217.2` (one pair), `C216.2`, `C218.2`,
  `C219.2`, `U200.47`, `U303.8`, `U316.4`. `U200.47` is the only actual GND **land**; the PM's
  "inward on F.Cu to the exposed pad" route for it is blocked because x 275.545 southbound runs
  between the east alley's two sub-rows (vias at x 275.205 and 275.785, 0.29 mm each side against
  the 0.39 mm a 0.127 mm track needs against a via). U200 itself is still grounded through the nine
  via-in-pad thermal vias of its exposed pad.
* 1 isolated `3V3_EMU_In2` pour island (zone-to-zone).
* 1 **pre-existing** item between `U6.1` and `U6.29`, both heritage pads on a heritage footprint,
  present on Rev2 and in every Phase-2 board. FC baseline; not touched (L4/L11).

**17 emulator signals** that have a verified escape from the U200 land but no onward route across
the wing: `EMU_BATT_SDA`, `EMU_CTL_FC_RESET`, `EMU_CTL_WDT_DIS`, `EMU_F1_SENSE`, `EMU_F2_SDA`,
`EMU_F2_SENSE`, `EMU_F3_SCL`, `EMU_F3_SENSE`, `EMU_FC3V3_SENSE`, `EMU_GPIO_SPARE1`, `EMU_STATUS_LED`,
`EMU_SWCLK`, `EMU_SWDIO`, `EMU_TOP_SCL`, `EMU_UART_TX`, `PYRO_INHIBIT_STATE`, and one `3V3_EMU`
branch. Their remaining gaps are 8–129 mm across the wing (`PYRO_INHIBIT_STATE` 129.4 mm to R601 in
the strip, `EMU_BATT_SDA` 64.3 mm, `EMU_TOP_SCL`/`EMU_FC3V3_SENSE` ≈ 45 mm to the bench-I/O column,
`EMU_SWCLK`/`EMU_SWDIO` 37.8 mm to J702). **This is autorouter work, not fan-out work** — see D8.

**1 `Deploy2_EN`** — proven unreachable, with the numbers:

| Layer | What separates U6.6 from the extension | Free gap | Needed |
|---|---|---|---|
| F.Cu | the heritage `Deploy1_EN` track (173.400, 131.683)–(176.018, 134.301), w 0.200, continuing east to x 185.151, meeting the `~{3v3_RESET}` chain (JP6.2 → (175.200, 129.350), w 0.300) at the `Deploy1_EN` via (173.400, 131.683, ⌀0.60). The one hole in that fence is between the 3v3_RESET track and that via: **0.2019 mm** | 0.202 mm | 0.527 mm (0.127 track + 2 × 0.20) |
| B.Cu | heritage `Heater_EN` (173.305, 131.030)–(172.500, 130.225), w 0.152, against R100.1's pad corner (172.820, 130.180): **0.182 mm** | 0.182 mm | 0.527 mm |

Measured by exact flood fill at 0.127 mm with the net's own heritage treated as free, `Deploy1_EN`
and `Heater_EN` stubs ripped, and the band opened to 24 mm **and** to 40 mm — the F.Cu pocket
(455 mm²) does not grow and never touches the extension-reachable set, so **depth is not the
constraint, the heritage fence is**. Neither hole can be opened by a narrower track or a scoped
clearance rule: even 0.09 mm track / 0.09 mm space (JLCPCB's floor) needs 0.27 mm.

**Smallest rule change that would close it:** extend the F6/F11 single-via allowance to **U6 pin 6**
(`attachment_check.VIA_ALLOWED` gains `(r'^U6$', {'6'})`). Measured on the delivered board:
the U6.6 F.Cu pocket and the B.Cu region that reaches the extension overlap over 732 222 cells, and
**505 450 of them take a legal 0.40/0.20 via** at ≤ 24 mm depth (e.g. (182.0, 131.0) at 11 mm, or
(165.4, 121.2) at 16.5 mm) — one B.Cu→F.Cu layer change inside the band, exactly the shape of the
allowance J2/J9/J13/J16.1/J14.10-12 already have. No other change (no heritage edit, no new band
allowance, no fab-spec change) closes it.

## D7. Tooling written for this round

Scratch only (`scratchpad/layout_close2/`); **no shared file under `FlatSat_V1/tools/` was
modified**. `FlatSat_V1.kicad_dru` in the delivery directory **is** changed (D1) and must travel with
the board.

| Tool | What it does |
|---|---|
| `mkarea.py` | creates the `EMU_FANOUT` constraint-only rule area |
| `drutest.py` | the deliberate DRC probes of D1 |
| `shrink.py` | 0.46 → 0.40 mm for new vias fully inside the rule area |
| `fan2.py` | the exact-polygon staggered fan-out: outer row + two staggered alley sub-rows, same-net pad/via sharing, 1/2/3-segment verified tracks, true per-item clearance |
| `rip2.py`, `ripin1.py` | box/net-scoped rip-up; removal of signal tracks from In1 inside the emulator core |
| `stitch.py` | exact-geometry cluster stitching (straight / L links, rule-area aware, never on In1, never into the Rev2 outline) |
| `micro.py` | **area-aware fine router.** Rasterises two obstacle sets (0.20 mm and 0.127 mm) and uses the relaxed one only ≥ 0.6 mm inside `EMU_FANOUT`, which guarantees the obstacle also intersects the area; every segment and via it emits is then re-checked with the exact polygon test before it is kept. This is the only router on the project that can leave the fan-out ring. |
| `gnd3.py` | GND pad → via → In1 stitching, pour-island detection via KiCad connectivity, and the F13b "inward to the exposed pad" fallback |
| `gap.py`, `flood.py`, `twolayer.py` | the reachability proofs of D6 (flood fill, narrowest-separation search, "would one via close it") |
| `restorefills.py` | puts the heritage zones' **stored** fill polygons back after `gnd3` refills the board in memory to find islands (KiCad 10 refills the FC's own `+3V3`/`VSOLAR` pours slightly differently from what Rev2 stored, which the stored-fill checks read) |

Worth promoting into `tools/pcb/` for the next stage: **`micro.py`** and **`fan2.py`**.

## D8. Why Freerouting did not finish the wing, and what should happen next

`route.sh` was run on the delivered geometry (`FR_TIMEOUT_MIN=240`, 4 passes, the L11 keep-out
fixture applied). Fan-out completed; auto-routing pass #1 took 1378 s and ended with **429 of 479
items still unrouted and 8428 violations**, i.e. it was spending the pass ripping up rather than
converging. The run was stopped and the merge was not taken, so nothing from it is in the delivered
board. The cause is structural: the DSN carries one global clearance, so every 0.127 mm fan-out
track inside `EMU_FANOUT` reads to Freerouting as a violation it must fix and cannot.

**Recommendation for the next round (PM decision):** export the DSN with the **rule area's own
clearance class** (Freerouting supports per-net-class clearance in the DSN `(rule …)` block) or,
simpler, add the ring to `fc_keepout.json` as a routing keep-out for the Freerouting pass only, so
the router treats the 51 escape vias as fixed terminals and routes the wing from them outward. The
17 open signals of D6 are all "via → destination across the wing" hops with no fine-pitch geometry
left in them, which is the case Freerouting handles well.

---

# Closure stage, round 3 (Opus, 2026-09-22)

**Workstreams merged before this step:** Deploy2_EN (F14, `round3/layout_deploy2en`), GND/3V3 island
(`round3/layout_gnd`), tool promotion (`round3/layout_toolpromo_sonnet`, no board change), delta merge
(`round3/layout_deltamerge_sonnet`). **This step (wing closure):** `round3/layout_wing` — notes in
`round3/layout_wing/notes.md`, progress log `round3/layout_wing/PROGRESS.md`.
**Delivered board:** `.flatsat_work/phase2/round3/layout_wing/deliver/FlatSat_V1.kicad_pcb` (whole project
directory beside it, `.kicad_dru` unchanged from round 2).

| Gate | Round 3 input (after delta merge) | Round 3 out |
|---|---|---|
| `heritage.py check --allow-zone-growth --allow-edge` | 0 | **0** |
| `heritage.py … --refill --core-inset 12 --ref-board Rev2` | 0 (3 band notes) | **0** (same 3 notes: +3V3 F.Cu band 291.0 → 273.7 mm², VSOLAR In2 91.8 → 91.2, B- In2 core 20.2 → 20.1 all touching stubs) |
| `attachment_check.py` | 5 (zone-fill, see E6) | **0 violations, 0 warnings, 37 stubs** |
| DRC clearance / short / hole / edge / width / annular | 0 | **0** |
| DRC `courtyards_overlap` | 1 (Rev2 SW2/TP2) | 1 (same) |
| DRC schematic parity | 11 = §6 baseline | **11 = §6 baseline** |
| DRC unconnected | 23 | **2** — U6.1↔U6.29 (heritage, accepted) + **C207.2 GND** (E4) |

## E1. Deploy2_EN, GND and the merge (the three earlier workstreams, from their notes)

* **Deploy2_EN (F14):** stub from U6.6 = F12 T-tap on the net's own heritage via (173.500, 130.100), F.Cu
  3.85 mm to the single F14 via (169.980, 130.900) 11.2 mm deep, B.Cu out of the outline to an extension via
  (170.380, 143.300), F.Cu to the existing Deploy2_EN via; 15.1 mm inside the Rev2 outline (limit 24).
  The PM fixed `attachment_check.py` (tap detected before the via rule; a legal layer change overrides the
  tap's single-layer rule) — `layout_deploy2en/PM_RULING.md`. 29 → 28.
* **GND/3V3 island (layout_gnd):** 5 of 11 GND items closed (U200.47 inward to the exposed pad; C217.2 and
  C219.2 by 0.40/0.20 vias; C215.2+C218.2 chained to C217.2) and the isolated `3V3_EMU_In2` island stitched
  by one 0.46/0.20 via; the remaining six pads were proven fenced by signal copper (fence/what-if proofs).
  28/29 → 24.
* **Delta merge:** both deltas applied by exact geometry (29 added, 1 removed, 0 conflicts) → 23. It saved a
  full zone refill, which is why `attachment_check.py` then read 5 zone-fill changes (E6).

## E2. Why the PM breakout method needed a ring re-plan first

A raster flood (F/In2/B, legal 0.40 vias) from each of the 16 open escape vias showed every one sealed in a
pocket by *other* nets' round-2 In2/B.Cu ring copper (`layout_wing/img/reach_f3scl.png`); micro.py-style
single-net routing broke out 2 of 14. So step (1) was widened to a re-plan of the whole ring:

* `rip.py` removed the 175 In2/B.Cu segments of the 23 signal nets crossing EMU_FANOUT + 1 mm (outside
  parts kept as clipped stubs; F.Cu lands/links/caps and the 3V3/1V1/VREG/XIN/XOUT/USB copper untouched).
* `ringplan.py` routed all 39 U200 nets / 48 connections **together** by negotiated congestion (PathFinder):
  raster on U200's 0.4 mm land lattice (0.025 mm; cell centres fall on the 0.40 mm gaps between 0.8 mm-pitch
  ring vias), C Dijkstra (`gdijk.c`), 0.127 mm only ≥ 0.6 mm inside EMU_FANOUT, 0.40/0.20 vias inside and
  0.46/0.20 outside; the 16 open nets end on a **0.46/0.20 breakout via 0.3–1.5 mm outside the rectangle**,
  pulled toward their destination; converged at iteration 12. Every emitted segment/via was checked with
  `world.py` (KiCad `SHAPE::Collide`, per-pair rule, shape-exact `intersectsArea`); `shortcut.py` then
  straightened the staircases (1136 → 260 segments) under the same exact check.
* **One footprint move, under F11(d):** C206 (0402, U200.20 IOVDD decoupling) 0.30 mm south, which gives
  U200.18 / EMU_CTL_FC_RESET — the land §D2 proved had no site — a 0.40/0.20 via on its own axis at
  (271.145, 99.150). C206's GND track end, the U200.20→C206.1 link and C206.1's 3V3 via (now (270.570,
  100.140)) were carried and exact-checked (`mod_c206.py`).

## E3. Hops: Freerouting as specified, then the exact router

**Freerouting (PM step 2, run exactly as specified):** export copy with U200 and every footprint inside the
rectangle removed, all tracks clipped at the rectangle (outside parts kept, so breakout stubs stay visible),
vias inside removed, the rectangle added to a private copy of `fc_keepout.json`
(`layout_wing/fr/keepout_wing.json`; the shared file untouched); `route.sh exp routed 8`, `PRUNE=1`,
`REF_BOARD`, `FR_TIMEOUT_MIN=150`, in the background. Fanout: 297 SMD pins "not routed"; auto-routing passes
1–8: **364 → 360 unrouted, 7852 violations on every pass**, 14–20 min per pass ("auto-routing stage
completed: started with 438 unrouted nets … 360 unrouted and 7852 violations" after 8761 s); `route.sh`'s
150-min timeout then stopped it in the optimizer, no SES (exit 4, `layout_wing/fr/route_sh.log`). The export copy still carries every connection whose ring copper was removed (all 51 U200 nets plus
the ring caps' rails), and Freerouting spends each pass on those. **Nothing from it was adopted.**

**Own router (`hop.py`, `hopr.py`):** C Dijkstra on a 0.05 mm raster over the wing and strip, new copper barred
from the Rev2 outline (+0.25 mm) and from EMU_FANOUT, vias only outside both, exact emission. `hopr.py` adds
rip-up: other nets' new copper is passable at 40× cost, the items the chosen path collides with are ripped
and their nets re-routed cluster-to-cluster; nets with any pad on a heritage footprint (all L11 stub nets)
and every power/bench net are never ripped. Results (breakout via → destination, routed length):
STATUS_LED 6.6 mm, UART_TX 16.6, FC3V3_SENSE 37.7, TOP_SCL 36.2, F1_SENSE 36.5, F3_SENSE 39.4, F3_SCL 59.5,
BATT_SDA 63.8 (to U315/R362 in the strip), SWCLK 52.4, WDT_DIS 55.0, FC_RESET 52.6, F1_SDA 45.1,
F2_SENSE 51.8; SWDIO, F2_SDA, PYRO_INHIBIT_STATE and GPIO_SPARE0 needed rip-up (victims all re-routed:
QSPI_SCLK/SD1/SD2/SD3, GPIO_RSVD, SPARE1, SWCLK, D200-A, F1_SDA, F4_SCL, F4_SENSE, F5_SCL, F5_SDA, U310-EN,
BOOTSEL_SW, F3_SENSE, RUN, UART_RX, F2_SENSE). Widths 0.20 mm where they fit, 0.152/0.127 mm where not.
**PYRO_INHIBIT_STATE** (F9): 163.8 mm on In2, 8.7 mm B.Cu and 6.2 mm F.Cu (breakout and two crossings), 9 vias,
to R601.2 (163.3, 158.6).

## E4. GND pads, 3V3_EMU and the one item left

Each fenced GND pad was attacked with `gndwhat.py` (single- and pair-item "what unlocks this pad" proofs on
the real rules) and closed with `gndfix.py` (pad → GND copper, or → an off-pad 0.40/0.46 GND via), the
displaced signal re-routed immediately:

| Pad | Unlock (ripped) → re-route | Closed by |
|---|---|---|
| U316.4 | EMU_TOP_SCL loop segment that wrapped pin 4 → U316.2→R373.2 re-drawn without the wrap | via (249.420, 56.130) |
| U303.8 | F0_COIL_P (281.288,120.204)–(278.920,120.204) → 3.0 mm, one via, B.Cu | via (279.345, 121.555) |
| C216.2 | redundant 1V1_EMU F.Cu segment (net stayed connected) | GND copper at (274.620, 101.005) |
| U201.4 | one QSPI_SD1 In2 segment → QSPI_SD1 re-routed | via (282.495, 97.880) |
| C208.2 | two EMU_GPIO_SPARE0 F.Cu segments → SPARE0 re-routed | GND copper at (279.495, 95.630) |
| C212.2 | QSPI_SD1's own land link + escape via (269.745, 90.530) → QSPI_SD1 re-escaped from U200.59, nothing else ripped | via (269.870, 90.280) |
| C215/C217/C218 return (PM item 2) | — | 0.40/0.20 via **(279.730, 95.845)** + 0.25 mm stub to C218.2; 0.035 mm from the PM's point so the via copper clears the pad |

**3V3_EMU:** the re-plan's In2 tracks cut the core In2 pour; after a refill the rail split into the U202
side and the south-east group (C206–C209, C211, C214, R200/R205/R207, the R602 west branch, U200.20/.30),
plus U200.38 alone. Joined by a 0.30 mm track with 2 vias (`joincl.py`) and, for U200.38, after re-routing
one EMU_UART_TX In2 segment. One cluster in DRC.

**Still open: C207.2 (GND), the only non-heritage unconnected item.** On F.Cu the pad sits in a closed pocket:
3V3_EMU 0.5 mm link C207.1→(278.137, 99.630) to the north, EMU_UART_RX (275.570,100.188)–(281.420,100.188)
to the south, C207.1 to the west, the 3V3_EMU via (278.137, 99.630) to the east; inside it no off-pad via
site is legal because In2/B.Cu carry 1V1_EMU (276.789,101.199)–(278.189,97.799), EMU_STATUS_LED and
EMU_CTL_WDT_DIS under it. Only **pairs** unlock it ({1V1 F.Cu stub + UART_RX F.Cu},
{1V1 In2 + STATUS_LED B.Cu}); both were executed — each closes C207.2, but the displaced ring net can only
re-escape by ripping further ring nets, and all four cascades tried ended with one other net open (best:
C207.2 closed, EMU_GPIO_RSVD open — `layout_wing/fix/p3d`); a full re-plan with the pad as a negotiated job
did not converge. **Smallest rule change that closes it:** one filled-and-capped via-in-pad (JLC POFV) on
C207.2 — a 0.40/0.20 GND via centred at **(276.975, 99.370)** passes every other rule (exact check; legal
centres span (276.950–277.000, 99.345–99.395)) and closes the pad with no other change. Electrically C207
(U200 IOVDD decoupling) has no ground return until then.

## E5. Numbers

Against the round-3 input board: **+757 / −221 tracks and vias** (the −221 are the 175 ripped ring segments,
16 vias and the pieces the rip-up/victim re-routes replaced); **145 new vias** — 133 × 0.46/0.20 (breakout,
hop layer changes, GND stitching of U316/U303/U201 outside EMU_FANOUT) and 12 × 0.40/0.20 inside EMU_FANOUT
(FC_RESET escape (271.145, 99.150), QSPI_SD1 re-escape (269.320, 90.730), GND for C212.2 (269.870, 90.280) and
C218 (279.730, 95.845), 3V3_EMU ×3 incl. C206.1's re-sited via, and 5 ring layer changes on F1_SDA, UART_TX,
WDT_DIS, SPARE0, F3_SENSE). Most vias per net: 9–10 (SWDIO, FC_RESET, PYRO; the hops change layer to cross
existing wing routing); new track length
In2 711 mm, B.Cu 560 mm, F.Cu 114 mm. 45 nets touched (all emulator-side, plus GND, 3V3_EMU, 1V1_EMU,
F0_COIL_P, D200-A, U310-EN — no net shared with the FC). One footprint moved: C206, (271.48, 99.58) →
(271.48, 99.88). No new copper inside the Rev2 outline (routers barred it; `attachment_check.py` 37 stubs,
0 violations).

## E6. `attachment_check.py` and the stored zone fills

The delta merge saved a full zone refill, so the heritage zones' **stored** fills in the flight section
changed (KiCad 10 refills the FC's own pours slightly differently from what Rev2 stored, plus the band
carve-out), and `attachment_check.py` — which reads stored fills with a 0.1 % tolerance over the whole
flight section — reported 5 zone violations. The delivered board follows the round-1/2 practice
(`restorefills.py`): all zones refilled, then the 41 heritage zones' stored fills copied back from
`round3/base` (whose heritage fills are the Rev2 ones). The comparison that matters —
`heritage.py --refill --core-inset 12 --ref-board` — refills in memory and reports 0 violations with the
same three band notes as rounds 1–2. The checker itself was not changed.

## E7. Tooling written for this round

Scratch only (`.flatsat_work/phase2/round3/layout_wing/tools/`); **no shared file under `FlatSat_V1/tools/`
was modified** and `fc_keepout.json` was only copied. The ones worth promoting into `tools/pcb/closure/`:

| Tool | What it does |
|---|---|
| `gdijk.c` (+ ctypes wrapper in `ringplan.py`) | multi-layer grid Dijkstra with via transitions, per-cell cost and terminal cost, plus flood fill; ~100× the pure-Python `mlroute` search — the reason whole-wing hops take seconds |
| `wr.py` | router core: raster aligned to U200's land lattice, EMU_FANOUT-aware obstacle sets, exact emission through `world.py` (KiCad `SHAPE::Collide`) |
| `ringplan.py` | negotiated-congestion re-plan of every connection inside a rule area, with breakout / either / GND-pad jobs, outside-reach filter and rip-up repair |
| `hopr.py` | long hops with rip-up and automatic victim re-route; never rips FC-shared or power nets |
| `gndwhat.py` | "which one or two items unlock this pad" proofs on the real rules |
| `gate.sh` / `finalize.sh` | gates in a sibling-complete directory; final refill with heritage stored fills restored |

## E8. What remains and what to do next

* **C207.2 GND** — see E4; the smallest change is one via-in-pad (PM/owner ruling); alternatively accept
  `layout_wing/fix/p3d` (C207.2 closed, EMU_GPIO_RSVD — the RP2350 reserved GPIO to R210/TP203 — open).
* **U6.1↔U6.29** — FC heritage, accepted (§D6, F13e).
* Warnings: `track_dangling` 15 → 30, `via_dangling` 23 → 17 against the round-3 input (every other warning
  +0). They are dead-end pieces left by the rip-ups; a DRC-verified trim (`trimloop2.py`: remove a batch, keep it
  only if the unconnected count does not rise, bisect otherwise) removed 34 this-round items in four passes; the
  rest are ends that DRC flags although removing them would disconnect a net (T-joins), so they stay.
* Quality flags for review: the hops use 0.20 mm (0.127–0.152 mm where needed) and change layer often (up to
  10 vias per net) because they thread existing wing routing; QSPI_SD0–SD3/SCLK/SS were re-routed inside the
  ring and toward U201 by the rip-up passes (lengths not matched — the RP2350 QSPI at bench speeds is not
  length-critical, but a reviewer should look); 3V3_EMU's south-east group now hangs on a 0.30 mm link
  because the In2 3V3 pour over the core is cut by the re-planned escapes (F9's pour intent is only partly
  met — a wider link or a second one is a cheap improvement).

# Cleanup after round 3 (Opus, 2026-09-23)

**Input:** `round3/layout_wing/deliver/FlatSat_V1.kicad_pcb`. **Delivered:** `round3/layout_cleanup/deliver/FlatSat_V1.kicad_pcb`
(whole project directory beside it, `.kicad_dru` unchanged; finalised with the round-1/2/3 stored-fill convention).
Full triage in `drc_triage.md` §10.

**Result:** unconnected 2 → **1** (only the accepted FC-heritage U6.1↔U6.29 is left); DRC errors 3 → **2** (that item + the Rev2
SW2/TP2 courtyard); track_dangling 30 → **0**; via_dangling 17 → **0**; footprint_type_mismatch 9 → **8** (U302 retyped
SMD; U200 = the flown U18 footprint, accepted); parity **11 = §6**. Zero clearance/short/hole/edge/width items.
heritage 0 (plain and `--refill --core-inset 12 --ref-board`, the same three band notes as round 3). attachment_check 0 violations, 37 stubs.
No new via inside the Rev2 outline (the same 13 stub vias). No via-in-pad added. No heritage item touched. No footprint moved (C206 stays where F11(d) put it).
The one footprint property change: U302 type "Through hole" → SMD.

**(1) 3V3_EMU.** The south-east group now reaches the U202 side through **two new 1.0 mm B.Cu links** from the SE In2 pour
piece to the east In2 3V3_EMU pour: (287.370,103.555)–(290.020,103.555) and (286.845,105.780)–(290.020,105.780), each with 2 × 0.46/0.20 vias.
U202.5 now feeds that east pour through **two vias** instead of one; the new one is at (291.970,95.080). The old west
link becomes the redundant second path. It is widened to the clearance limit: B.Cu/F.Cu 0.30 → 0.40, and the rest of the chain 0.127–0.25 → 0.275–0.50.
The thread at C204.1 (0.48 mm, 0.127) has no room. Series resistance U202.5 → SE pads falls from 43–65 mΩ over 9–13 vias to 10–23 mΩ over 4–6 vias. Node-disjoint
paths go from 1 to 2. U200.38: its land link 0.127 → 0.200 mm. The 0.127 mm In2 link cannot be widened (0.41 mm channel). A second path needs
EMU_RUN or EMU_F3_SENSE re-escaped from the ring; both were tried, and neither victim could be re-routed. The other 3V3 land links went to 0.200 mm.
(2) **C207.2 closed.** The pair unlock {1V1 In2, STATUS_LED B.Cu} was executed with an off-pad 0.40/0.20 GND via at (277.320,99.705).
The victims were re-routed in the other order (STATUS_LED first) with a wider window: STATUS_LED 6.1 mm with 1 via; 1V1 6.65 mm on In2. Cost:
the 1V1 path to DVDD pin 23 / C216 +10 mΩ and +2 vias. (3) **Dangling:** 79 dead ends/redundant vias removed, 9 one-layer vias
turned into segments inside their own copper, 13 T-join overshoots shortened. Every step was checked by connectivity and the board was DRC'd after every
pass. This includes 3 dead F5_PWR segments on **In1.Cu** (the GND plane), which are now gone. (4) **QSPI** was not re-routed. Pad-to-pad lengths: SCLK 30.0, SD0 45.7,
SD1 44.2, SD2 46.0, SD3 30.9, SS 22.2 + 4.1 mm; 3–8 vias. The FC's own U18→U11 bus is 8.3–12.8 mm with 0–2 vias. Table in `drc_triage.md` §10.7.
**For the review:** 45 via-in-pad and 19 via-at-pad-edge contacts from routing rounds 1–3 need the owner's POFV/move decision
(`drc_triage.md` §10.8). Tools (scratch): `layout_cleanup/tools/` — `g33*.py` (power-net graph, max-flow, series R),
`join33.py` (second-path router), `widen33.py`, `unlock33.py`, `fixdangle.py`, `padlen.py`, `viapad2.py`.
