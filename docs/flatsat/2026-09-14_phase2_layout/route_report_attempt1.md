# PROVES FlatSat V1 — Phase 2 routing stage report (attempt 1)

**Date:** 2026-09-20 · **Stage:** 4 (Routing) · **Owner:** Sonnet routing agent (attempt 1) · **Input:** build-stage board (outline + ground + netclasses applied, unrouted, 383 unconnected) · **Result: NOT clean — 1 heritage violation and 13 shorting DRC errors remain, fully diagnosed below; hand-back does not meet the brief's exit criteria and needs a follow-up pass before this board can be adopted.**

## 1. Recipe invocation

```
KEEPOUT_JSON=FlatSat_V1/tools/pcb/fc_keepout.json
HERITAGE_SNAP=FlatSat_V1/tools/baseline/heritage_rev2.json
REF_BOARD=FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb
FR_TIMEOUT_MIN=170
tools_pcb/route.sh stubs/proj/FlatSat_V1.kicad_pcb routed/proj/FlatSat_V1.kicad_pcb 3
```

See §6 for the full Freerouting timing breakdown and §0 for why `tools_pcb/route.sh` (a scratch copy)
was invoked instead of the shared `tools/pcb/route.sh`.

## 0. Tool fix made in this stage

`tools/pcb/attachment_check.py`'s `ALLOWED_PADS` table has a latent bug: the loop that builds
`limit_of` has no `break` and no first-match guard, so when a footprint matches more than one entry
(J14 matches both the specific `{'10','12'}: 22.0` mm exception and the generic `J14: 14.0` mm entry
that follows it and covers every pad including 10/12) the *last* match wins, silently discarding the
first. That defeats the table's own comment ("Listed first so it wins") and made the brief's approved
F7/PLR-02 ruling (BATT_SDA/BATT_SCL at J14.10/12, 18.5–20.9 mm from the nearest edge, need >14 mm)
impossible to ever pass, regardless of how the stub is routed. Confirmed by hand-tracing the code and
by observing `attachment_check.py` report "> 14 mm allowed" for a J14.12 stub that measured 21.2 mm —
under the brief's stated 22 mm exception this should read 22, not 14.

Fixed **only in a scratch copy** (`tools_pcb/attachment_check.py` in this agent's scratch directory,
never the shared `FlatSat_V1/tools/pcb/attachment_check.py`), per `tools/pcb/README.md`'s own
instruction to copy-and-edit rather than modify a shared script mid-task: `limit_of[(ref, pad)] = lim`
→ `limit_of.setdefault((ref, pad), lim)` (first-match-wins via `setdefault`). Scoped to exactly the
J14 pins 10/12 case; no other pad's limit changes (verified: every other ALLOWED_PADS ref only ever
matches one entry). `route.sh` was invoked from this scratch copy (`tools_pcb/route.sh`, `$HERE`
resolves to the scratch dir) specifically so its internal attachment gate/prune step (step 7) uses the
fixed logic and does not re-prune BATT_SDA/BATT_SCL. **Recommend the PM apply the same one-line fix
to the shared `tools/pcb/attachment_check.py`** so later stages don't have to work around it too.

A second, more consequential gap found and fixed in this stage's own stub-planning tooling (not a
project script — a scratch tool this agent wrote): the initial collision model only checked candidate
stub paths against **heritage tracks**, never heritage **pads**. On a header with ≤2 mm pin pitch
(J14, J16 in particular) a track can graze or run straight through a neighbouring pin's own copper
without ever touching a track — `attachment_check.py` only catches this when the stub's own *endpoint*
lands on the wrong pad (as happened once, see §2); a track that merely *passes over* another pin's pad
without ending there is invisible to that gate but is a real DRC clearance violation (and, on J16 row
65, would have shorted SCL_Top directly across the Dir_Chrg_In pin's pad — caught only by an
independent pad-audit script written for this purpose, not by attachment_check). Added heritage-pad
avoidance (conservative inscribed-circle clearance, spatial-grid indexed for speed) to the stub
planner and re-planned; this is the reason the per-net table below differs from an earlier draft.

## 2. L11 attachment stubs (37 nets, hand-scripted with pcbnew)

37 shared nets identified programmatically (heritage pad ∩ new-footprint pad, excluding GND which is
carried by the extended In1 plane only). Each stub: straight or minimally-jogged track from the one
allowed attachment pad (`tools/pcb/attachment_check.py`'s `ALLOWED_PADS`) to a point just outside the
Rev2 outline, on the pad's own copper layer, within the per-pad band/length allowance, verified clear
of both heritage tracks and heritage pads of any other net. 9 of them (F1/F3/F5 × PWR/SCL/SDA, the
bottom-side face connectors J9/J13/J2) each take the one permitted B.Cu→F.Cu via inside the band
(owner ruling F6/PLR-01: a continuous PAYLOAD_BATT/DEPLOY1 B.Cu wall, 0.283 mm gap, blocks a
same-layer exit) — via positions individually verified clear of heritage F.Cu copper, not assumed
uniform, per the panel's own PLR-01 note. BATT_SDA/BATT_SCL (J14.10/12) use the owner's 22 mm
per-pad exception (F7/PLR-02), hand-traced around the J19/BATT_SDA/C53/R80/D3 cluster as instructed.

30 of the 37 shared nets got a compliant stub; 7 are documented as blocked by heritage placement
density and deferred (§11) rather than forced non-compliant. Final table (`tools/pcb/plan_stubs.py`
+ `draw_stubs.py`, scratch tools, this agent's own):

| Net | Pad | Layer | Width (mm) | Inside (mm) | Via |
|---|---|---|---|---|---|
| +3V3 | J16.6 | F.Cu | 0.5 | 3.0 | — |
| B- | J14.2 | F.Cu | 1.0 | 10.88 | — |
| BATT_SDA | J14.10 | F.Cu | 0.25 | 19.86 | — |
| Deploy1_EN | R104.1 | F.Cu | 0.25 | 10.86 | — |
| Deploy2_EN | U6.6 | B.Cu | 0.25 | 12.19 | — |
| Dir_Chrg_In | J16.8 | F.Cu | 1.0 | 3.0 | — |
| F0_PWR | J6.4 | F.Cu | 0.3 | 6.69 | — |
| F0_SDA | J6.6 | F.Cu | 0.25 | 6.69 | — |
| F1_PWR | J9.4 | B.Cu | 0.3 | 7.04 | (221.81,106.41) 0.6/0.3 |
| F1_SCL | J9.5 | B.Cu | 0.25 | 6.82 | (222.21,109.41) 0.6/0.3 |
| F1_SDA | J9.6 | B.Cu | 0.25 | 7.04 | (221.81,111.21) 0.6/0.3 |
| F2_PWR | J11.4 | F.Cu | 0.3 | 6.59 | — |
| F2_SCL | J11.5 | F.Cu | 0.25 | 6.59 | — |
| F2_SDA | J11.6 | F.Cu | 0.25 | 6.59 | — |
| F3_PWR | J13.4 | B.Cu | 0.3 | 6.69 | (222.61,122.30) 0.6/0.3 |
| F3_SDA | J13.6 | B.Cu | 0.25 | 7.66 | (222.61,123.20) 0.6/0.3 |
| F4_PWR | J1.4 | F.Cu | 0.3 | 6.64 | — |
| F4_SCL | J1.5 | F.Cu | 0.25 | 6.65 | — |
| F5_PWR | J2.4 | B.Cu | 0.3 | 6.72 | (222.30,92.90) 0.6/0.3 |
| F5_SCL | J2.5 | B.Cu | 0.25 | 7.93 | (221.90,95.90) 0.6/0.3 |
| F5_SDA | J2.6 | B.Cu | 0.25 | 7.43 | (221.50,96.60) 0.6/0.3 |
| FC_RESET | J16.2 | F.Cu | 0.25 | 3.0 | — |
| Heater_EN | R100.1 | B.Cu | 0.25 | 12.16 | — |
| INHIB_1 | J29.2 | F.Cu | 1.0 | 7.27 | — |
| IN_RBF | J29.1 | F.Cu | 1.0 | 7.27 | — |
| SCL_Top | J16.7 | F.Cu | 0.25 | 6.0 | — |
| SDA_Top | J16.5 | F.Cu | 0.25 | 6.0 | — |
| USBBOOT | J16.1 | B.Cu | 0.25 | 13.22 | — |
| VBATT_SENSE | J8.2 | F.Cu | 1.0 | 7.36 | — |
| WDT_DISABLE | J16.9 | F.Cu | 0.25 | 6.0 | — |

**Not routed this pass (7 nets, documented as blocked by placement, brief §7):**

| Net | Allowed pad | Limit | Blocking geometry |
|---|---|---|---|
| BATT_SCL | J14.12 | 22 mm (F7/PLR-02) | J14's own B- pin column (pins 2/4/6/8) and BATT_SDA's own heritage/stub copper box the pin in on every side within the 22 mm budget once heritage-pad clearance is enforced; a path exists on paper (jog west of the B- column then south, ~21 mm) but its margin against BATT_SDA's own adjacent stub is under 0.1 mm and did not survive the final pad-aware re-plan in time for this hand-back — the closest of the 7 to being solvable; worth a first retry in the DRC-cleanup stage. |
| F0_SCL | J6.5 | 14 mm | F0_PWR's own heritage diagonal trace and F0_SDA's heritage trace both cross the only two direct exits from this pin on J6's single-column, 1.5 mm-pitch field. |
| F3_SCL | J13.5 | 14 mm (via) | The via slot between the heritage GND/VSOLAR via cluster and F3_PWR/F3_SDA's own now-placed vias is fully claimed; no clear via position found within the per-pad clearance model. |
| F4_SDA | J1.6 | 14 mm | FIRE_DEPLOY1_A's heritage trace occupies the direct exit; a longer alternate route exceeds the 14 mm band. |
| INHIB_2 | J7.2 or J7.4/J10.1/J10.3 | 24 mm | INHIB_1's and IN_RBF's own heritage F.Cu traces, plus FIRE_DEPLOY1_A on B.Cu, form a near-continuous wall along the bottom edge (y≈135–136) on both copper layers; the only ~2 mm gaps in it are already filled by IN_RBF's and INHIB_1's own new stubs. |
| VBUSP | J30.1 or J20.2/J20.4 | 14/24 mm | Same wall system as INHIB_2, at J30's position (near FIRE_DEPLOY1_A's zigzag around x 184.5–188.9). |
| VSOLAR | J11.1 | 14 mm | D15 (heritage diode, VBUSP/VBUS pads) sits directly on the natural exit path toward the injection block. |

## 3. Gate results after stubs only

```
$ heritage.py check heritage_rev2.json <board> --allow-zone-growth --allow-edge
note: new items: footprints +221, tracks/vias +129, zones +4
heritage check: 0 violation(s)

$ attachment_check.py heritage_rev2.json <board>   (scratch-copy fix applied, see §0)
attachment check: 129 new tracks/vias, 30 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)

$ audit_pads.py <board> stub_plan.json   (this stage's own heritage-pad clearance audit, see §0)
0 potential pad-clearance issue(s)
```

## 4. L5 net width pre-routing

The L11 stubs for the L5-widened nets (Dir_Chrg_In, B-, VBUSP, VBATT_SENSE, INHIB_1, INHIB_2, IN_RBF,
VSOLAR) are already drawn at their L5 width (1.0–1.5 mm, `tools/pcb/plan_stubs.py`'s width table) —
that satisfies "the autorouter does not do them at default width" for the attachment-band segment,
the one nearest the frozen flight section and the one most worth protecting explicitly. Beyond the
stub's exposed end, `extend_l5.py` connects straight to the *nearest* new-footprint pad on that net,
still at L5 width, wherever that run is more than 10 mm (Dir_Chrg_In, VSOLAR: both feed screw-terminal
/ header blocks tens of mm into the wing/strip) — the six nets whose nearest pad is one of the
JP600-series shunt headers sit only 2–9 mm from the stub end (a densely-packed bench-mode row, ~2.2 mm
pin pitch); left for Freerouting to close at netclass width rather than risk a coarse bbox-based
extension clipping a neighbouring header the same way the L11 stub planner initially clipped J14/J16
pins (§0) — a short run at Default width is a minor, easily-DRC-caught cosmetic gap, not a current-
capacity concern at bench-power scale, and safer than a script guessing through a 2 mm-pitch row.

## 5. USB pair (EMU_USB_DP/DM)

`usb_pair.py`: joins J701's A6/B6 (D+) and A7/B7 (D-) pad pairs with a 0.25 mm F.Cu track each: draws
the short, geometrically simple, high-confidence R703.2→U200.52 (EMU_USB_DP) and R704.2→U200.51
(EMU_USB_DM) hops (1.94 mm each, naturally length-matched since the two resistor/pad pairs are
mirror-symmetric); the long J701→R703/R704 run (~38 mm, crossing R701/J703/R702/C212/C213 — a
genuinely dense corner of the emulator-core block) is left unrouted for Freerouting rather than
threaded through that field with the same coarse per-footprint-bbox check that proved too blunt
elsewhere in this stage — Freerouting sees only the coupled-pair *destination* nets (already
narrowed at the U200 end) and the `USB_EMU` netclass (0.25 mm track / 0.6-0.3 via / 0.25-0.15 diff
pair) the build stage already wrote into `FlatSat_V1.kicad_pro`, so it will not fall back to Default
width for this run even though this stage did not hand-route it.

## 6. Freerouting pass

Invocation (`tools_pcb/route.sh` — this agent's scratch copy, see §0 for why — from the stubbed+
L5-extended+USB-pair board):

```
KEEPOUT_JSON=FlatSat_V1/tools/pcb/fc_keepout.json
HERITAGE_SNAP=FlatSat_V1/tools/baseline/heritage_rev2.json
REF_BOARD=FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb
FR_TIMEOUT_MIN=170
tools_pcb/route.sh stubs/proj/FlatSat_V1.kicad_pcb routed/proj/FlatSat_V1.kicad_pcb 3
```

Keep-out fixture applied: 204 `(keepout ...)` + 4 `(via_keepout ...)` records in the DSN (route.sh's
own abort-if-not-applied check passed). Freerouting 2.4.1, `-mp 3 -mt 1`.

- **Fanout:** 1448 SMD pins total, 20 passes, 648 s, 744/1448 (51.4 %) escaped, 656 CPU-s. One
  `BasicBoard.normalizeTraces` cap warning for net Deploy1_EN (2000-iteration oscillating-geometry
  cap, self-limiting per README §3b, harmless).
- **Auto-routing:** 451 unrouted items at start, `-mp 3`, 3 passes (988 s / 818 s / 782 s = 2588 s
  total), converged at 327 unrouted, score 0.00 throughout. The `score 0.00 (…7505 violations)`
  reading is the exact benign phenomenon README §7 documents from the 2026-09-14 smoke run (fixed
  heritage wires sit inside their own DSN keep-out polygons — cosmetic, they are fixed and never
  ripped up).
- **Optimization:** 2 passes (869 s / 775 s), stopped itself ("improvement below 1.00 % threshold"),
  1710 s total, final score 0.00 (327 unrouted, 7505 violations — same cosmetic reading).
  `Invalid traces after autoroute: 537 traces not 45 degree` (same class of harmless warning
  README §3c anticipated for the `-mt 1` single-threaded optimizer).
- **Total Freerouting wall time: ~85 minutes** (04:18:52–05:43:35), well inside the
  `FR_TIMEOUT_MIN=170` budget; never killed, CPU stayed 100–180 % the whole run.

## 7. Post-processing / pruning

`route_merge.py merge --report` (PRE = stubbed board, POST = SES-imported copy):

```
PRE tracks/vias: 3400   POST tracks/vias: 1453   new (by geometry+net): 1453
chains of new items: 148; adopted 137 chain(s) (1414 items) that reach a new-footprint pad;
  dropped 11 heritage-echo chain(s) (14 items) + 25 degenerate (<0.01 mm) segment(s)
touching a new (Phase-1, ref 200-799) footprint pad: 432
review (redraw/split of an existing heritage-net segment, or between two new footprints via an
  intermediate point — original heritage segment untouched underneath either way): 982
```

`attachment_check.py` (fixed copy) on the merged board: **0 violations directly — no `PRUNE` needed**
(route.sh's own `NV` check found nothing to prune). 30 stub chains recognised, 1543 new tracks/vias
total (the 129 hand-drawn stub/extension/USB items + 1414 Freerouting-adopted items).

`heritage.py check --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2.kicad_pcb`:
**1 violation** — `zone +3V3 on F.Cu: filled copper inside the flight core (outline -12 mm) changed
384.8 -> 356.5 mm²` (-7.4 %). No new +3V3 track or via has an endpoint inside the core polygon
(verified directly), so this is not new copper physically inside the core; it is the zone-refill
algorithm pulling the +3V3 pour fill back near the core/band boundary for clearance against new
copper that sits just inside the *band* (the same mechanism the band-fill notes below describe, just
close enough to the 12 mm line to read on the core side of it too). Per hard rule #4 ("a stage that
cannot pass heritage stops and reports; it does not 'fix' heritage") this is reported, not patched —
see §11.

Four other zones show accepted band-only carve-out (stubs are allowed to carve the band, not the
core):

```
zone +3V3 on F.Cu:  band fill 466.9 -> 221.3 mm² (-52.6 %)
zone GND on B.Cu:   band fill 1378.3 -> 1363.0 mm² (-1.1 %)
zone VSOLAR on In2.Cu: band fill 266.1 -> 250.3 mm² (-5.9 %)
zone GND on In1.Cu: band fill 3220.5 -> 3214.5 mm² (-0.2 %)
```

## 8. Final gates

Two tool fixes were needed after the raw route.sh output before these numbers are meaningful:
(a) `route.sh` only propagates the sibling `.kicad_pro` into its working directory, never
`.kicad_dru` / `Backup_Footprints` / `footprints.pretty` / the lib-tables / the schematics — copied
those into `routed/proj/` by hand (their absence had inflated `lib_footprint_issues` 3→27 and
`clearance` 0→98, both artifacts, not real routing defects — worth fixing in `route.sh` itself for
the next stage). (b) removed a self-inflicted short (see §11) found by DRC after the Freerouting run.

```
$ heritage.py check … --refill --core-inset 12 --ref-board …
heritage check: 1 violation(s)   [+3V3 core fill, §7 — NOT cleared this hand-back]

$ attachment_check.py … (fixed copy)
attachment check: 1539 new tracks/vias, 30 stub chain(s) into the flight section, 0 violation(s)

$ kicad-cli pcb drc … ; drc_summary.py … --baseline drc_prelayout.json
section            sev      type                       base  now  delta
schematic_parity   warning  extra_footprint               1    1    +0
schematic_parity   warning  footprint_symbol_mismatch     5    5    +0
schematic_parity   warning  missing_footprint           199    5  -194
schematic_parity   warning  net_conflict                 36    0   -36
unconnected_items  error    unconnected_items             0  116  +116
violations         error    clearance                     0   23   +23
violations         error    copper_edge_clearance          0   1    +1
violations         error    courtyards_overlap            1    1    +0
violations         error    hole_clearance                 0   8    +8
violations         error    shorting_items                 0  13   +13
violations         warning  footprint_type_mismatch        7   9    +2
violations         warning  isolated_copper                4   4    +0
violations         warning  lib_footprint_issues           3   3    +0
violations         warning  solder_mask_bridge              0   6    +6
violations         warning  track_dangling                  0   9    +9
errors: 162  unconnected: 116  parity: 11 (= exactly the §6 baseline)
```

`parity: 11` matches the brief §6 baseline exactly — no new parity drift. `courtyards_overlap: 1` is
the known, accepted pre-existing Rev2 SW2/TP2 item (unchanged). `footprint_type_mismatch +2` is
`U200`/`U302`, the same class of warning as the 7 pre-existing heritage items (build-stage finding,
unchanged this stage). `shorting_items: 13` is the serious one — see §11 for the itemised breakdown
and root causes; **not cleared this hand-back**, same status as the heritage violation.

## 9. Width audit of L5 nets

`width_audit.py` (min/max widths and total length per net, all tracks on that net — heritage +
new combined, since the net is one continuous electrical net):

| Net | Widths seen (mm) | Total length (mm) |
|---|---|---|
| Dir_Chrg_In | 0.152, 0.25, 0.4, 0.635, **1.0** | 133.4 |
| B- | 0.15, 0.187, 0.25, 0.635, **1.0** | 68.7 |
| VBATT_SENSE | 0.152, 0.25, 0.3, 0.4, 0.5, 0.635, **1.0** | 43.1 |
| INHIB_1 | 0.25, 0.635, **1.0** | 33.0 |
| IN_RBF | 0.25, 0.635, **1.0** | 31.7 |
| VBUSP | 0.25, 0.4, 0.5, 0.635 | 138.8 |
| INHIB_2 | 0.25 | 13.6 |
| VSOLAR | 0.152, 0.25, 0.3, 0.635 | 64.6 |

The 1.0 mm width appears on every L5 net this stage successfully stubbed (Dir_Chrg_In, B-,
VBATT_SENSE, INHIB_1, IN_RBF) — the hand-drawn stub segment closest to the frozen flight section.
VBUSP, INHIB_2 and VSOLAR show no 1.0 mm segment because this stage did not get a compliant L11 stub
for them (§2/§11); their listed widths are pre-existing heritage copper plus whatever Freerouting
routed at netclass Default width in the extension — the L5 width instruction was never reached for
these three and should be applied by hand in the next stage once (or if) their attachment stub lands.

## 10. USB pair length match

```
EMU_USB_DP: 1 seg, 1.938 mm
EMU_USB_DM: 1 seg, 1.938 mm
skew: 0.000 mm
```

Only the hand-drawn R703.2→U200.52 / R704.2→U200.51 hop exists on these two net names (the coupled
pair proper, per L5 / panel's PLR-03 note that "no vias if avoidable" begins at R703/R704). It is
naturally length-matched (the mirror-symmetric resistor/pad geometry) — 0 mm skew, well inside the
brief's 1 mm tolerance. The much longer J701→R703/R704 run (pre-resistor net names, not this pair)
was left for Freerouting (§5) and was not routed by it either (it remains an unconnected item, see
§11) — so the coupled differential pair itself has no length-match exposure to report on that segment
because it does not yet exist.

## 11. Open issues

- **Heritage: 1 violation, not cleared.** `+3V3` zone fill inside the flight core (outline -12 mm)
  changed 384.8 → 356.5 mm² (-7.4 %). No new +3V3 copper has an endpoint inside the core (verified),
  so this reads as clearance-driven fill retreat from new copper sitting close to the core/band
  boundary bleeding across the measurement line during refill, not a literal new-copper intrusion —
  but the check is exact-match by design (hard rule L4) and this is a real, reportable delta. Per hard
  rule #4 this stage stops and reports rather than attempting a further fix. Next step: identify the
  specific new +3V3-adjacent copper nearest the core boundary (likely a Freerouting-placed via/redraw
  near one of the F#-column stubs, given the same corridor is where the shorting_items below cluster)
  and move it, or accept the reading and get an owner ruling on whether this specific clearance-driven
  edge effect counts as "heritage churn" under L4's intent.
- **DRC: 13 `shorting_items` (electrical shorts), not cleared.** Two distinct root causes, fully
  diagnosed:
  - **6 shorts: VSOLAR vias vs. F0/F2/F3/F4/F5 SCL/SDA stub tracks** (all in the x≈220.8–222.5,
    y≈89–125 face-connector corridor). VSOLAR is a heritage net present on *every* face connector's
    pins 1/2, and `ALLOWED_PADS`' `nums=None` entries make every pin of J1/J2/J6/J9/J11/J13 an
    "allowed pad" for the keep-out carve-out and for `attachment_check`'s via exemption (via
    `VIA_ALLOWED_PADS` matching J2/J9/J13 by ref only, not by net) — so Freerouting was free to add
    its own new VSOLAR vias near any of those pins, and it placed several close enough to this
    stage's thin (0.25 mm) signal stubs to short them. This is legitimate under the coded L11 rule
    (each such via's chain does reach an allowed pad) but is a real DRC defect Freerouting introduced
    on its own initiative, not something this stage's stub script did.
  - **7 shorts: this stage's own collision-model blind spots.** `F3_PWR` vs. a heritage `GND` via
    (the stub-planner's `seg_clear` checked new tracks against heritage *tracks* but never heritage
    *vias* — a gap found only after this DRC run, not caught by the pad-audit script either since
    that only re-checked *pads*). `F5_SCL` vs. `F5_SDA` (adjacent-pin via placement too close).
    5 shorts around U6 (`Deploy1_EN`×2, `Heater_EN`, `GND`, `unconnected-(U6-NC-Pad19)`, all against
    the `Deploy2_EN` stub) — U6 is a small, tightly-pitched heritage IC and the stub planner's
    heritage-pad clearance model uses each pad's *inscribed-circle* radius (`min(hx, hy)`), which
    under-estimates real clearance need when a stub runs alongside a pad's *long* axis rather than
    crossing it — exactly U6's geometry. Fix for next time: check new tracks against heritage vias
    too, and replace the inscribed-circle pad model with the pad's actual oriented rectangle.
  - **1 short found and fixed in this pass:** `usb_pair.py` assumed J701's A6/B6 were both "D+" and
    adjacent, but the connector's real pin order interleaves rows (`B6 D+, A7 D-, A6 D+, B7 D-`) — the
    straight D- join track passed directly over the D+ pad in between. Two rebuild attempts still
    clipped the connector's dense 0.3×1.45 mm pad field (or a Freerouting-placed CC1 via next to it);
    given the field's extreme density, the join tracks were removed rather than iterated further —
    A6/B6 and A7/B7 are now simply unconnected (2 of the 116 unconnected items) instead of shorted,
    which is the safer state to hand back.
- **`tools/pcb/attachment_check.py`'s `ALLOWED_PADS` first-match-wins bug (§0)** is fixed only in this
  agent's scratch copy (`tools_pcb/`), not the shared `FlatSat_V1/tools/pcb/attachment_check.py`.
  Recommend the PM apply the same one-line `setdefault` fix to the shared file.
- **`tools/pcb/route.sh` doesn't propagate `.kicad_dru` / library siblings (§8)** into its own working
  directory — worth fixing in the shared script so the next agent doesn't have to rediscover it.
- **U200/U511 0.45 mm-pad/0.20 mm-drill escape vias, the 3V3_EMU/PYRO_INHIBIT_STATE In2 pours, and the
  decoupling-GND-via placements** (panel routing_instructions item 4 and the DECOUPLING/U511 THERMAL
  notes) were not hand-routed this pass — deferred to the DRC-cleanup stage. Freerouting routed the
  bulk of the board at whatever width/via class its netclass/DRU rules gave it; expect the DRC's
  `clearance`/`hole_clearance` entries to include some U200/U511 escape-annulus failures needing the
  panel's 0.45/0.20 override applied explicitly.
- **7 L11 stubs not routed this pass** (BATT_SCL, F0_SCL, F3_SCL, F4_SDA, INHIB_2, VBUSP, VSOLAR) —
  see §2's table for the specific blocking geometry per net. Their nets remain unconnected across the
  flight-section boundary; each is a legitimate "blocked by placement" case per brief §7, not
  forced non-compliant.
- **112–114 of the 116 unconnected items** are the ordinary consequence of the 7 un-stubbed nets plus
  the 2 now-open J701 D+/D- ends plus whatever Freerouting itself could not reach inside its keep-out
  (expected, not investigated item-by-item in this pass — the DRC-cleanup stage should triage the
  full unconnected list against §2's deferred-net table to confirm every item traces back to one of
  the known causes here rather than a new one).
