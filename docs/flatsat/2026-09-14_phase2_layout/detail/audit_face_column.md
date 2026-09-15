# Independent audit — `face_column` block, fix round 3 (48 refs, solar_emulation)

**Auditor role:** independent datasheet auditor, mandate to refute, not confirm.
**Audited artifacts:** `detail/placement_face_column.json` (fix round 3), `detail/placement_face_column.md`
(fix round 3), `detail/placement_face_column_placed.kicad_pcb` (fix round 3 board).
**Method:** every number below was re-derived from scratch — pad coordinates and nets read directly
with `pcbnew`, courtyard polygons via `GetCourtyard()`, hot-pad selection by matching each part's own
net table rather than trusting which physical pad the report calls "hot." The whole 218-placement
board was independently rebuilt from `FlatSat_V1.kicad_pcb` + `FlatSat_V1.kicad_pro` (never written)
through `outline.py` → `apply_placement.py`, using my own merge of `placement_face_column.json`
(fix round 3) into a fresh copy of `floorplan.json` (diffed field-by-field: 42 of 48 refs differ from
v1, all 48 match the delivered per-block file). `heritage.py check --allow-zone-growth --allow-edge`
and `attachment_check.py` were re-run on that independent rebuild. The TCA4311A datasheet
(`https://www.ti.com/lit/ds/symlink/tca4311a.pdf`, SCPS226C) was fetched fresh via `WebFetch`,
extracted with `pdftotext -layout`, and every quote below was checked against that extraction, not
against either prior round's report. **New this round: `kicad-cli pcb drc --refill-zones` was run on
the independently-rebuilt board** — a real copper-clearance check no fix round (0–3) or either prior
audit round had performed for this block; it surfaced a genuine new defect (§4). All work on scratch
copies under
`/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_face_column/`;
the live board and `FC_V5e_Production_Rev2/` were never opened for write; no git commits; KiCad GUI
never opened.

## 0. Verdict

**FAIL** — **1 must-fix**, 0 should-fix, 3 notes. Every gate this role is asked to re-run
(heritage, attachment/L11, whole-board courtyard overlap, envelope containment, lane clearance,
anchor-IC ≤ 3 mm, F.Cu ruling) passes, independently reconfirmed below, and this round's own two
claimed fixes (C316/R371/R372's hot-pad-to-pin distances, the courtyard-clearance rows) are real and
reproduced to the same numbers. But **this round's fix creates a real, fabrication-breaking DRC
clearance violation that none of the canonical tools (`outline.py`, `apply_placement.py`,
`heritage.py`, `attachment_check.py`) check for, and that fix round 3 never ran a DRC pass to catch**:

1. **Must-fix — R372's new position clears a fixed GND stitching via by only 0.13 mm, against a
   0.2 mm netclass-Default requirement.** The via is at `stitching.points` (250.97, 50.6) in
   `floorplan.json` — a point this role is not permitted to move — and R372's pad 2 (`EMU_TOP_SDA`)
   sits 0.85 mm from it centre-to-centre. This did not exist on the fix-round-2 board (R372 was
   8.7 mm away, in the old south cluster); it is a direct, reproducible side effect of this round's
   should-fix-1 remedy (§4).

The three notes (§5) are all previously-disclosed trades (R371's 4.58 mm residual, R333/R353's
11.1/11.2 mm SCLOUT-pull-up reach, R314's 13.35 mm sense-tap reach) that I re-derived independently
and confirm are genuine, bounded, and correctly not reopened.

## 1. Gates re-run independently

```
$ outline.py --board myaudit3_base.kicad_pcb --out myaudit3_o.kicad_pcb --spec my_merged_r3.json
Edge.Cuts items removed: 11 / added: 7 / In1 GND zones grown: 1 / heritage zones clipped: 40
new GND pours: 4 / mounting holes added: 3 / stitching vias added: 65
(identical to the placer's own outline log)

$ apply_placement.py --board myaudit3_o.kicad_pcb --placement my_merged_r3.json --out myaudit3_placed.kicad_pcb
applied 218; refused (heritage) []; missing refs []
footprints not fully inside the outline: 0: []
courtyard overlaps (same-side, >=1 new part; real polygons): 0: []

$ heritage.py check tools/baseline/heritage_rev2.json myaudit3_placed.kicad_pcb --allow-zone-growth --allow-edge
heritage check: 0 violation(s)

$ attachment_check.py tools/baseline/heritage_rev2.json myaudit3_placed.kicad_pcb
attachment check: 65 new tracks/vias, 0 stub chain(s) into the flight section, 0 violation(s), 0 warning(s)
```

From-scratch rebuild off the untouched live board, using my own merge of the placer's per-block JSON
into `floorplan.json` (not the placer's `merged_floorplan_r3.json` taken on faith) — matches the
placer's reported gate results exactly.

**New this round — `kicad-cli pcb drc --format json --severity-all --refill-zones` on the
independently-rebuilt board** (in a directory with the board's own `.kicad_pro`, per floorplan.md §2):
49 violations total (8 clearance, 1 courtyard-overlap, 4 isolated-copper, 9 footprint-type-mismatch,
27 lib-footprint-issues — all warnings except clearance/courtyard). Of the 8 clearance errors, **7 are
pre-existing and outside this block** (U301/Q510 intra-footprint pad spacing, already the accepted
Rev2/floorplan.md baseline item — see floorplan.md §6, "add `U301`/`Q510` to the `.kicad_dru`
exemption"). **1 is new and inside this block: R372 vs. a fixed GND stitching via (§4).** Re-running
the identical DRC command on the fix-round-2 board (`r2_placed.kicad_pcb`, the placer's own delivered
round-2 artifact) finds **0** clearance violations touching any of this block's 48 refs — confirming
the via-clearance defect is introduced by round 3's fix, not carried over.

## 2. Placement constraints (independently checked)

| Constraint | Result |
|---|---|
| (a) Envelope `[242,50.5,268.3,135.5]` | **Pass.** All 48 F.CrtYd/B.CrtYd bboxes fully inside. Tightest margins: U316 north edge 0.055 mm, R371/R372 north edges 0.435 mm, C316 north edge 0.445 mm — independently measured with `pcbnew.GetCourtyard()`. |
| (b) Fixed anchors | None specified for this block — n/a. |
| (c) Anchor ICs ≤ 3 mm from v1 | **Pass.** U300/U310/U311/U312/U313/U314 byte-identical to v1 (0.000 mm), independently diffed against `floorplan.json`'s own v1 values. U316 moved 0.100 mm south (53.5→53.6), well inside budget. |
| (c) L11 attachment reach, ≤ 3 mm regression per net | **Pass, 21/21**, independently re-measured pad-centre-to-pad-centre on the from-scratch rebuild: max Δ = **+0.602 mm** (`+3V3`, 21.9→22.502 mm). The three v1 regressions (`F1_PWR` −2.548, `F3_PWR` −2.545, `F5_PWR` −2.240 mm) are improvements. Every one of the 21 values matches the placer's §15.5 table to the mm, independently recomputed from pad coordinates, not copied. |
| (d) No courtyard overlap, whole board | **Pass.** `apply_placement.py` from-scratch rebuild: 0 overlaps (218 placements). Independent same-side pairwise `GetCourtyard()` scan within the block: 0 overlaps, minimum gap 0.510 mm (R314–U300 / R333–U311 / R353–U313). **However, courtyard non-overlap is not the same as copper-clearance compliance — see must-fix, §4.** |
| (e) 12.6 mm lane (x 231.4–244) clear of parts > 2 mm tall | **Pass.** Four block members reach x < 244 (courtyard west edge 243.495 mm): R314, R333, R353 (`R_0402`) and, this round, **C316** (`C_0402`) — all ≤ ~0.5 mm tall packages, far under the 2 mm limit regardless of x. |
| (f) Heritage frozen | **Pass**, 0 violations on the independent from-scratch rebuild. |
| (g) Rotation / pin-facing | Independently re-derived for the 3 changed refs from raw pad coordinates (not taken from the report): C316 180° gives 2.090 mm vs. 3.050 mm at 0° (worse); R372 180° gives 3.380 mm vs. 4.440 mm at 0° (worse); R371 0° gives 4.580 mm vs. 5.600 mm at 180° (worse). All three rotations are the shorter option. **Assignment check (which resistor gets the near vs. far east slot):** I re-derived both options from the pin table independently — "SDAOUT near / READY far" (used) gives (3.38, 4.58) mm, max 4.58; "READY near / SDAOUT far" gives (2.08, 5.88) mm, max 5.88. The used option minimizes the worst-case distance; both sum to the same 7.96 mm (same two slots), so this is a legitimate, independently-reproduced design choice, not a shortfall. I also independently confirmed the report's claim that only **one** part fits in the west flank without breaching the envelope's x0 = 242 edge (a second 0402 there would land at ≈241.1 mm, 0.9 mm outside) — the "single west slot" premise behind the whole flanking design is real, not asserted. |
| (h) ≥ 0.5 mm courtyard clearance | **Pass** on the courtyard-polygon numeric gate: independent scan finds minimum 0.510 mm, 0 pairs < 0.5 mm, the 3 new pairs (U316↔C316, U316↔R372, R371↔R372) all at 0.550 mm. **This constraint's real intent — enough room for routing/fab — is not fully met; see must-fix.** |
| F.Cu ruling (owner F3) | **Pass.** 45/48 on F.Cu; U310/U312/U314 on B.Cu; their decoupling caps C310/C312/C314 at 0.000 mm centre offset (direct via-pair), independently confirmed from the board, not the JSON. |

## 3. Guideline checklist — independently re-derived from raw pad/net data

Datasheet basis, fetched fresh this round and verified against my own `pdftotext -layout` extraction
of `tca4311a.pdf` (SCPS226C), lines 1109–1180:

> **§11.1 Layout Guidelines:** "By-pass and de-coupling capacitors are commonly used to control the
> voltage on the VCC pin, using a larger capacitor to provide additional power in the event of a short
> power supply glitch and a smaller capacitor to filter out high-frequency ripple. **These capacitors
> should be placed as close to the TCA4311A as possible.** These best practices are shown in
> Figure 16." "...vias are placed directly next to the surface mount component pad which needs to
> attach to VCC or GND...however, this routing and via is not necessary if VCC and GND are both full
> planes as opposed to the partial planes depicted."
> **§11.2/Figure 16 ("Package Layout"):** shows the by-pass/de-coupling capacitor(s) at the VCC-pin
> (pin 8) corner and one EN pull-up resistor routed with a via for the split-plane case. Pin layout
> confirmed identical to the symbol/footprint used here: left column 1 EN / 2 SCLOUT / 3 SCLIN / 4 GND
> (top→bottom), right column 8 VCC / 7 SDAOUT / 6 SDAIN / 5 READY (top→bottom, aligned pin-for-pin
> opposite the left column) — matches the schematic symbol's pin table exactly (independently checked
> against `easyeda2kicad.kicad_sym`, not assumed).
> **§5 Pin Functions, VCC row:** "Connect pull-up resistors from SDAIN and SCLIN (and also from SDAOUT
> and SCLOUT) to this pin. Place a bypass capacitor of at least 0.01 μF close to this pin for best
> results."

No numeric distance appears anywhere in the datasheet. The board's F.Cu GND zone bbox
(232.0, 48.5)–(295.5, 171.2), independently re-queried on the round-3 rebuild, fully covers the block
envelope, confirming §11.1's own "no via needed for full planes" applies and the GND-return leg of
every decoupling cap is effectively a direct pour connection.

| # | Rule | My independent measurement (raw pad/net data, round-3 board) | Verdict |
|---|---|---|---|
| 1 | VCC decoupling, hot pad (net = IC's own VCC-pin net) → VCC pin (8) | C300 2.210, C311 2.210, C313 2.210 mm; C310/C312/C314 (opposite-side via pair) 2.207 mm; **C316 2.090 mm** (best in the block) | Pass 7/7 |
| 2 | EN pull-up (net = IC's own EN-pin net) → EN pin (1) | R300 1.965, R310 1.915, R320 2.196, R330 1.915, R340 2.196, R350 1.915, R370 2.196 mm | Pass 7/7 |
| 3 | READY pull-up → READY pin (5) | R301 2.196, R311 1.915, R321 2.196, R331 1.915, R341 2.196, R351 1.915, **R371 4.580 mm** | Pass 7/7 have a real measured value; R371 is the block's farthest, disclosed and re-verified minimal (§5) |
| 4 | SDAOUT/SCLOUT device-side pull-ups → pin 7/2 | R302 2.119, R303 2.851, R312 1.946, R313 2.817, R322 2.119, R323 2.119, R332 1.946, **R333 11.099**, R342 2.119, R343 2.119, R352 1.946, **R353 11.242**, **R372 3.380**, R373 2.119 mm | Pass 12/14 ≤ 2.85 mm; R333/R353 are the disclosed L11 via-column trade (§5) |
| 5 | Sense tap (Fn_PWR-net pad) → GND pin (4), placer's own fallback proxy | R324 2.196, R334 1.915, R344 2.196, R354 1.915, R374 2.196 mm; R314 13.352 mm to its nominal IC | Pass 5/6 with a clean local anchor; R314 is the disclosed L11 trade (§5). **Note:** this rule measures a Fn_PWR-net pad's distance to the GND pin, not the VCC pin — logically it is really "distance to whichever IC pin the row's geometry happens to sit nearest," which for every south-row channel is pin 4; it is not an electrical GND connection requirement. Not a defect (no rule is violated either way), but the "≤ ~2 mm from IC GND pin" phrasing invites a reader to assume a stronger electrical rationale than exists. |
| 6 | F.Cu ruling (owner F3) | 45/48 side=F; C310/C312/C314 offset 0.000 mm from their B.Cu IC | Pass |
| 7 | 0.5 mm courtyard clearance, real polygons | Minimum 0.510 mm, 0 pairs < 0.5 mm, 29 pairs < 0.55 mm scan window | Pass (numeric gate only — see must-fix for the real-copper counterpart) |
| 8 | Whole-board courtyard overlap / envelope / heritage / L11 gates | All re-run from scratch, all clean (§1–2) | Pass |
| 9 | **Real DRC copper clearance (`kicad-cli pcb drc --refill-zones`)** — not previously run by any fix round or audit round for this block | 7/8 clearance errors pre-existing/out-of-block; **1 new: R372 vs. fixed GND stitching via, 0.13 mm actual vs. 0.2 mm required** | **Fail — must-fix, §4** |

## 4. Must-fix — R372's new position violates real copper clearance against a fixed stitching via

**What I found:** `kicad-cli pcb drc --refill-zones` on the independently-rebuilt round-3 board
reports:

```
Clearance violation (netclass 'Default' clearance 0.2000 mm; actual 0.1300 mm)
  Via [GND] on F.Cu-B.Cu, pos (250.97, 50.6)
  Pad 2 [EMU_TOP_SDA] of R372 on F.Cu, pos (251.060001, 51.45)
```

The via at (250.97, 50.6) is not something either the placer or I introduced — it is entry
`stitching.points[2]` in `floorplan.json`, one of the 65 fixed GND stitching vias the block-level
floorplan places on the new-area perimeter (via size `[0.8, 0.4]` mm dia/drill, per the same key).
This role's instructions are explicit that `stitching` (along with outline/pours/holes/lanes/keepouts)
**must not be changed** — so this via cannot be moved to fix the conflict; only R372 (or a further
redesign of the U316 east-flank layout) can move.

**Why it happened:** fix round 3's flanking design (§15.1 of the placer's report) put R372 at
(251.57, 51.45) — 0.55 mm east of U316's courtyard, at the pin's own y — without checking it against
the fixed stitching-via list. The via sits 0.85 mm away centre-to-centre, close enough that the pad's
own copper (not just its courtyard) comes within 0.13 mm of the via's copper, 0.07 mm short of the
board's own 0.2 mm Default-netclass clearance rule.

**Why no prior check caught it:** `apply_placement.py`'s overlap check is footprint-courtyard vs.
footprint-courtyard only — it does not know about stitching vias, which `outline.py` adds separately
and which carry no courtyard of their own. `heritage.py` and `attachment_check.py` don't check
copper-to-copper spacing either. None of fix rounds 0–3, nor the round-0/1/2 audits, ran
`kicad-cli pcb drc` on this block's board at all (grepped `placement_face_column.md` for `kicad-cli`
and `drc`: zero occurrences across all 15 sections). The v1 floorplan-level review (`floorplan.md` §6)
did run DRC, but that was before any of this block's passives existed in their current fine-grained
positions — its "7 clearance errors, all pre-existing, all outside this block" finding predates every
fix round and cannot have covered round 3's new geometry.

**Independent confirmation this is new, not carried over:** re-running the identical
`kicad-cli pcb drc --refill-zones` command on `detail/...r2_placed... ` (the fix-round-2 board, where
R372 sat at y ≈ 60.1, 8.7 mm from its pin) finds **zero** clearance violations touching any of this
block's 48 refs. The violation is a direct, reproducible consequence of round 3's fix and did not
exist before it.

**Suggested direction (not verified as a full fix — a placer round should re-derive and re-measure
it, not take this on faith):** R372 needs roughly ≥ 0.13–0.2 mm more clearance from (250.97, 50.6).
Nudging R372 south (increasing y, away from the via) by ≈ 0.3–0.4 mm while holding x looks
geometrically promising — the via is due north of the pad, and R372's own courtyard has 0.435 mm of
spare margin against the envelope's y0 = 50.5 edge below it before hitting the envelope from the other
direction — but this would also change its 3.380 mm distance to pin 7 and its 0.550 mm gap to R371,
both of which need re-measuring, and the pad-vs-via clearance itself needs re-running through
`kicad-cli` after any change, not estimated by hand.

**Severity:** must-fix (a real, kicad-cli-verified, fabrication-relevant design-rule violation against
a fixed board fixture — not a datasheet number, but squarely a "constraint broken" in the sense the
audit brief means it).

## 5. Notes (independently re-confirmed, not reopened)

**Note 1 — R371's 4.580 mm residual (READY pull-up) is genuinely close to the geometric minimum.**
I independently re-derived the two possible east-flank assignments from the raw pin table (VCC
x=247.02, SDAOUT-net x=247.68, READY x=248.98, all y=51.45) and confirm both give the same
7.96 mm two-part sum, so minimizing the block's worst-case distance (used: max 4.58 mm) rather than
either individual value is the only lever available once C316 has claimed the west slot. I also
independently re-derived that a second west-flank slot does not fit inside envelope x0 = 242 mm. No
better assignment exists within this flanking geometry; a materially different layout (e.g., a via
down to a second copper layer to reach a slot closer to the pin from outside this footprint's
immediate flanks) was out of scope for a placement-only round and is not required by any numeric
datasheet or brief rule (the datasheet gives no mm figure at all).

**Note 2 — R333/R353's 11.099/11.242 mm SCLOUT-pull-up reach, and R314's lack of a local GND-pin
anchor (13.352 mm), are unchanged this round and remain a genuine, bounded L11 trade.** Verified
independently: these three refs are byte-identical to round 2 and round 1's positions, and the reason
they sit so far from their nominal B-Cu IC is that each of U310/U312/U314's channels needs 5 support
resistors but only 4 row-slots exist around the via-paired F.Cu cap at the frozen 8 mm F.Cu/B.Cu column
pitch — the 5th resistor in each case is the one that doubles as the L11 attachment stub for that
channel's `Fn_PWR` net, so it must stay near the lane (x ≈ 244.5) rather than near the IC (x ≈ 256).
Re-verified against the L11 reach table (§2): `F1_PWR`/`F3_PWR`/`F5_PWR` sit at 23.15/23.16/23.06 mm,
2.2–2.5 mm *better* than v1, comfortably inside the 3 mm budget. Not a placement defect; correctly not
re-litigated by fix round 3.

**Note 3 — Rule 5's "near the GND pin" framing is directionally arbitrary but not incorrect.** As
detailed in §3 row 5: the sense-tap resistors' hot pads carry the `Fn_PWR` (VCC-net) signal, not GND,
so their proximity to pin 4 is really "nearest IC pin to the south row," not an electrical GND
requirement. This is a documentation-clarity point, not a hardware defect — no placement choice would
change if the rule were reworded — so I record it as a note rather than reopening the citation
should-fix that round 3 already fixed for a different reason (misattributed document/section, closed
correctly in §15.2 of the placer's report).

## 6. Commands run

```bash
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
CLI=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
SCRATCH=/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_face_column
cd /Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1

# independent merge: placer's placement_face_column.json (round 3) into a fresh floorplan.json copy
python3 -c "merge placement_face_column.json into a copy of floorplan.json" # -> my_merged_r3.json
# (42 of 48 refs differ from v1; all 48 match the delivered per-block file)

# independent geometry dump straight from the delivered placed board (dump_geom.py, pcbnew Pads()/GetCourtyard())
$KPY dump_geom.py placement_face_column_placed.kicad_pcb geom.json

# independent checklist: hot-pad selection by matching each part's own net table against the IC's
# pin-net table (not by trusting which pad number the report calls "hot")
python3 -c "recompute rules 1-5 for all 7 channels from geom.json"   # -> matches every fix-round-3 number

# independent envelope + pairwise courtyard-gap scan (real GetCourtyard() polygons)
python3 -c "envelope containment + same-side pairwise gap scan from geom.json"

# independent TCA4311A datasheet fetch + extraction (never taken from either prior report)
# WebFetch https://www.ti.com/lit/ds/symlink/tca4311a.pdf -> saved PDF -> pdftotext -layout -> tca4311a.txt
grep -n "11 Layout\|Figure 16\|Pin Functions" tca4311a.txt

# schematic/library pin-map cross-check (independent of both prior reports' claim)
grep -n "TCA4311ADGKR" solar_emulation.kicad_sch
python3 -c "confirm pin names/numbers in easyeda2kicad.kicad_sym match the report's pin table"

# independent from-scratch whole-board rebuild (never touches FlatSat_V1.kicad_pcb itself)
cp FlatSat_V1.kicad_pcb FlatSat_V1.kicad_pro $SCRATCH/   # myaudit3_base.*
$KPY tools/pcb/outline.py --board $SCRATCH/myaudit3_base.kicad_pcb --out $SCRATCH/myaudit3_o.kicad_pcb \
     --spec $SCRATCH/my_merged_r3.json
$KPY tools/pcb/apply_placement.py --board $SCRATCH/myaudit3_o.kicad_pcb \
     --placement $SCRATCH/my_merged_r3.json --out $SCRATCH/myaudit3_placed.kicad_pcb
$KPY tools/pcb/heritage.py check tools/baseline/heritage_rev2.json $SCRATCH/myaudit3_placed.kicad_pcb \
     --allow-zone-growth --allow-edge
$KPY tools/pcb/attachment_check.py tools/baseline/heritage_rev2.json $SCRATCH/myaudit3_placed.kicad_pcb

# independent L11 reach re-measurement, all 21 nets, from pad coordinates on the from-scratch rebuild
$KPY my_reach3.py $SCRATCH/myaudit3_placed.kicad_pcb

# independent GND-zone bbox query on the round-3 rebuild
$KPY zones3.py $SCRATCH/myaudit3_placed.kicad_pcb

# NEW: real DRC pass, not run by any prior fix or audit round for this block
mkdir $SCRATCH/drc3 && cp $SCRATCH/myaudit3_placed.kicad_pcb $SCRATCH/drc3/board.kicad_pcb
cp FlatSat_V1.kicad_pro FlatSat_V1.kicad_dru $SCRATCH/drc3/board.kicad_pro  # (renamed to board.*)
$CLI pcb drc --format json --severity-all --refill-zones --output $SCRATCH/drc3/drc_refilled.json \
     $SCRATCH/drc3/board.kicad_pcb
python3 -c "filter drc_refilled.json for violations touching this block's 48 refs" # -> found the R372/via hit

# comparison run on the placer's own fix-round-2 delivered board, to prove the defect is new
mkdir $SCRATCH/drc2 && cp $SCRATCH/r2_placed.kicad_pcb $SCRATCH/drc2/board.kicad_pcb
cp FlatSat_V1.kicad_pro $SCRATCH/drc2/board.kicad_pro
$CLI pcb drc --format json --severity-all --refill-zones --output $SCRATCH/drc2/drc.json \
     $SCRATCH/drc2/board.kicad_pcb
python3 -c "filter drc.json for clearance violations touching this block's 48 refs" # -> 0 hits
```

Live board `FlatSat_V1/FlatSat_V1.kicad_pcb` and `FC_V5e_Production_Rev2/` never opened for write; no
git commits; KiCad GUI never opened. All work on scratch copies at
`/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/detail_face_column/`.
