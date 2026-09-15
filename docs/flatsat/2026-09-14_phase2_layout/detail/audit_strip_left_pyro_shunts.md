# Independent audit — `strip_left_pyro_shunts` detail placement (2026-09-14)

**Role:** refute, not confirm. Own checklist built from primary sources; placer's md not trusted for
any pass/fail claim without a re-measurement on `placed.kicad_pcb` via pcbnew, or an independent gate
re-run. **Verdict: PASS — 0 must-fix, 0 should-fix.** Two note-level observations recorded below.

## 0. Scope recap

20 refs, no supported IC (3 BAT54W diodes, 8 fixed 2-pin headers, 1 SPDT-as-SPST slide switch, 1 LED,
3 resistors, 4 test points). Envelope `[150.5,142.8,220.7,161.9]`. Fixed anchors: JP600–JP607, SW600.
Board audited: `/private/tmp/claude-501/.../scratchpad/detail_strip_left_pyro_shunts/placed.kicad_pcb`.

## 1. Sources fetched and read myself

- **Nexperia `BAT54W_SER.pdf`** — fetched directly (11 pages, all read, not summarized from a search
  snippet). Confirmed: **no PCB layout / application-circuit section exists** in this datasheet
  (ToC: Product profile, Pinning, Ordering, Marking, Limiting values, Thermal characteristics,
  Characteristics, Test information, Package outline, Packing, Soldering, Revision history, Legal,
  Contact, Contents — 15 sections, none titled layout/application). Placer's "no layout section,
  fallback applied" claim is **accurate**, not an evasion. Also confirmed directly from the datasheet:
  pin 1 = anode, pin 2 = n.c., pin 3 = cathode (BAT54W single-diode variant, SOT323/SC-70) — matches
  the placer's row 1 claim exactly.
- **LCSC `MSK12C02` and `KT-0603W` PDFs** — attempted fetch myself (WebFetch, then a direct `curl`
  with a browser UA as a second attempt). Both attempts returned LCSC's Nuxt.js app shell (`<title>`
  only, no PDF bytes) — reproduced the same bot-check the placer's md reported. Fallback-to-generic-
  practice is justified for SW600 and LED600; neither part's *position* is placer-controlled anyway
  (SW600 is a fixed anchor; LED600 is unchanged from v1).
- **Cankemeng `B-2100S02P-A110` (2-pin header)** — not fetched (same bot-check expected, not
  re-attempted — moot regardless: JP600–607 are all fixed anchors, no placement decision to audit).
- Schematic text notes on `pyro_inhibit.kicad_sch` (grepped directly, all 20 `(text ...)` blocks) —
  read in full for hidden requirements per CLAUDE.md's "schematic text notes are requirements" lesson.
  Nothing there constrains footprint position/rotation beyond what's already in the placement table;
  the notes are about **net topology** (R600 to FC +3V3 not 3V3_EMU, JP600 population state, SAFE-LED
  logic) — correctly out of a placement audit's remit, and unaffected by any move in this pass.

## 2. Net-level ground truth (from pcbnew on the delivered board, not the placer's prose)

Dumped every pad/net for all 20 refs directly. Confirms the placer's functional description is
electrically accurate, not just plausible:

- D600 anode(pin1)=`Deploy1_EN`, D601 anode(pin1)=`Net-(D601-A)` (fed from `Heater_EN` via JP600),
  D602 anode(pin1)=`Deploy2_EN`; all three cathodes(pin3) commoned on `PYRO_INH_COM`, in x-monotonic
  chain order (178.51 → 182.46 → 186.41 mm) — matches row 1's chain-continuation claim.
  Anode pads sit at y=151.685 (0.65 mm **north** of body centre, toward the y=142.1 boundary every EN
  net arrives from); cathode pads sit 0.887 mm **east** of body centre. Independently re-derived, not
  copied from the md.
- R600.1/R601.1/R602.1(via LED600) all on `PYRO_INH_COM`; R600.2=`+3V3`, R601.2=`PYRO_INHIBIT_STATE`,
  R602.2=`3V3_EMU`, LED600.2=`Net-(LED600-A)`=R602.1. Matches the sheet's function table exactly.
- SW600 pad1=unconnected (the NC/ARMED throw, correctly dead-ended), pad2=`PYRO_INH_COM` (pole),
  pad3=`GND` (the CLOSED=SAFE throw) — consistent with the schematic note "SW600 closed ... pulls
  PYRO_INH_COM low."

## 3. Gates re-run independently (not trusted from the md)

```
heritage.py check tools/baseline/heritage_rev2.json placed.kicad_pcb --allow-zone-growth --allow-edge
  -> heritage check: 0 violation(s)  (all zone/edge notes are outline-growth deltas already in v1)

attachment_check.py tools/baseline/heritage_rev2.json placed.kicad_pcb
  -> attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)

apply_placement.py --board outlined.kicad_pcb --placement merged_floorplan.json --out reverify_placed.kicad_pcb
  (merged_floorplan.json rebuilt independently from floorplan.json + this block's placement JSON, not reused from the placer's copy)
  -> applied 218; refused (heritage) []; missing refs []
  -> footprints not fully inside the outline: 0
  -> courtyard overlaps (same-side, real polygons): 0
  -> exit 0
```

All three gates independently reproduced clean. `apply_placement.py`'s **real courtyard-polygon**
overlap check (the authoritative one, not my own bbox approximation below) reports 0 — none of the 7
footprints it had to fall back to bbox/pad-shape for (BT1, G***, REF**, RF1, SW703, U12, U30) are in
this block.

## 4. Measurements taken myself with pcbnew (not copied from the placement md)

**Fixed anchors — bit-for-bit position/rotation/side check against `floorplan.json` (v1):**
JP600–JP607 and SW600 all match v1 x/y/rot/side to the value printed in the JSON, exactly, for all 9
refs. **0 mm / 0° move confirmed independently.**

**Envelope containment** (courtyard bounding box, all 20 refs): every ref's courtyard bbox lies fully
inside `[150.5,142.8]–[220.7,161.9]`. Nearest to an edge: SW600/JP600 west edge at x=152.0 (1.5 mm
clear of 150.5); LED600 south edge 2.21 mm clear of 161.9. **0 violations.**

**Courtyard-to-courtyard clearance** (all 190 internal pairs, bbox distance — apply_placement.py's
real-polygon check above is the authoritative confirmation): 0 pairs below 0.5 mm. Minimum internal
gap ≈ 1.0 mm (D600↔D601, D600↔TP603 row, JP600/601↔TP600–603 row, R602↔LED600, SW600↔TP600 row —
consistent with, and slightly more conservative than, the placer's reported 0.957–0.960 mm since bbox
vs. real-polygon distance differ slightly). **Block-to-rest-of-board**: nearest neighbors are Q500
(1.875 mm from D602) and U315 (1.480 mm from JP607) — both clear.

**Attachment-reach re-measurement** (pad-to-pad, not trusted from the md): `U6.3`→`D600.1`
(`Deploy1_EN`) = **19.449 mm**; `U6.6`→`TP602.1` (`Deploy2_EN`) = **22.491 mm**; `U6.5`→`TP601.1`
(`Heater_EN`) = **22.852 mm**. All three reach pads are unmoved (bit-for-bit identical to v1), so
**Δ = 0.00 mm** for all three, independently confirmed, well inside the ≤3 mm allowance. No anchor IC
exists in this block (confirmed — no `U*` ref present), so constraint (c)'s "anchor IC ≤3 mm" clause
is correctly N/A rather than silently skipped.

**Lane clearance**: block envelope max x = 220.7 mm; L3 lane starts at x=231.4 mm → 10.7 mm clear.
N/A/PASS, trivially.

**F.Cu ruling (brief F3)**: every part in this block sits on F.Cu (confirmed via pad-layer dump for
all 20 refs — no B.Cu part in this block). No B.Cu IC (U310/U312/U314 are in a different block), so
the "decoupling cap opposite on F.Cu, via pair" clause of F3 is correctly N/A here.

**Attachment-map cross-check on R600's `+3V3` tap** (a rule the placer's checklist did not
mention at all): R600.2 taps `+3V3`, a heritage net. I checked whether this creates an *undocumented*
second flight-section entry point outside the L11 allowed-pad list in `attachment_check.py`
(`ALLOWED_PADS` has no regex for a `+3V3`-net pad). Resolution: **not a violation** — `+3V3` already
has its own, separate L11 attachment stub at `J16.6 → R370.1` in the face-column block per
floorplan.md §5's attachment table; R600's tap is ordinary Phase-2-internal copper from R370 across
the new area to R600, not a second crossing into the flight section. Checked and cleared, not left
as an assumption.

## 5. DRC (kicad-cli), run for completeness — one systemic note, not attributed to this pass

`kicad-cli pcb drc` on the reverified board reports clearance / hole-clearance / solder-mask-bridge
violations against the `GND_F_Cu_strip` / `GND_B_Cu_strip` / In1 GND zones touching **every pad of
every part in this block** — including the 9 **fixed, unmoved** anchors (JP600–607, SW600) and the
unmoved D600/D602/TP600/TP602/TP603/LED600. Since the violation is present identically on parts this
pass never touched, it is a pre-existing zone-fill staleness artifact from `outline.py`'s pour
generation (the fill predates/doesn't reflect per-pad keep-outs for this row), not something the
passive re-placement introduced or could fix by repositioning. **Note, not a finding against this
placement**: flag for whoever owns the next zone-refill/final-DRC pass to confirm a clean refill
before sign-off; out of scope for a placement-only audit and not caused by any ref this pass moved.

## 6. Findings

**0 must-fix. 0 should-fix.**

Two note-level (judgement-call) observations, neither a rule violation:

1. **Note** — Fixing the LED-loop defect (R602 permuted to the LED-adjacent slot) unavoidably pushes
   whichever of R600/R601 ends up in the farthest of the three interchangeable slots ~1.4 mm farther
   from the `PYRO_INH_COM` source cluster (SW600/JP601) than in v1 (6.92 mm → 8.31 mm for R601 in the
   delivered arrangement). Verified this is an unavoidable consequence of using the only 3 available
   fixed slot coordinates (157.005 / 159.915 / 162.825 mm) once the closest slot is reassigned to
   R602 — not an oversight, and there is no electrical reason to prefer R600 over R601 for the middle
   slot (both tap the same net, neither is an attachment/anchor pad, still single-digit mm either
   way). Not a rule violation (no criterion in the brief or any datasheet bounds this distance
   tighter than "single-digit mm," which both values satisfy); recorded for owner visibility only,
   since the placer's checklist reported all three PASS without flagging the R601-specific
   trade-off against its own v1 baseline.
2. **Note** — see §5: pre-existing GND-zone clearance/solder-mask-bridge DRC noise across the whole
   block (present on unmoved fixed anchors too), unrelated to this placement pass, flagged for the
   team's zone-refill/final-DRC stage rather than as a finding here.

## 7. What I checked and could not fault

- Diode anode/cathode orientation and chain continuity (re-derived from pad coordinates, not
  inherited rotation).
- Courtyard spacing, envelope containment, fixed-anchor immobility, attachment-reach Δ, lane
  clearance, F.Cu ruling — all re-measured independently on the delivered board, all pass.
- The one substantive change this pass made (R600/R601/R602 permutation) demonstrably shortens the
  LED-series-resistor loop (7.99 mm → ~2.16 mm pad-to-pad, independently measured) with no new
  overlap and no rule regression.
- Heritage and attachment gates reproduced clean from scratch (own merged floorplan, own
  `apply_placement.py`/`heritage.py`/`attachment_check.py` invocations), not just re-quoted from the
  delivered md.
