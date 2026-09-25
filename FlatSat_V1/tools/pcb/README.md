# Freerouting round-trip recipe: routing only the new connections, heritage byte-for-byte

Validated on a synced copy of `FlatSat_V1.kicad_pcb` (Rev2 flight-controller layout + 218 new
footprints staged east of the outline, x >= 245 mm, all their nets unrouted). Goal: route the new
connections with Freerouting without disturbing any pre-existing (flight-heritage) track, via, zone
or footprint. Everything below was run on copies in a scratch directory; nothing under
`FlatSat_V1/` was modified except this file and `tools/pcb/route_merge.py`.

## TL;DR recipe

```
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
TOOLS=tools/pcb

# 1. Fix the board so DSN export will actually work (see "DSN export fails" below)
$KPY $TOOLS/route_merge.py prep synced.kicad_pcb prepped.kicad_pcb

# 2. Export DSN, mark every existing wire/via (type fix), drop degenerate wire stubs
$KPY - prepped.kicad_pcb prepped.dsn <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
pcbnew.ExportSpecctraDSN(b, sys.argv[2])
PY
$KPY $TOOLS/route_merge.py fixdsn prepped.dsn prepped_fixed.dsn

# 3. Route. Use -mt 1 (see "multi-threaded optimization" below). Be patient -- see "timing".
java -jar ~/Documents/KiCad/10.0/3rdparty/freerouting/freerouting-2.4.1.jar \
    -de prepped_fixed.dsn -do routed.ses -mp 3 -mt 1

# 4. Import the SES into a copy (this is what route.sh's import step does)
$KPY - prepped.kicad_pcb routed.ses routed.kicad_pcb <<'PY'
import sys, pcbnew
b = pcbnew.LoadBoard(sys.argv[1])
pcbnew.ImportSpecctraSES(b, sys.argv[2])
pcbnew.SaveBoard(sys.argv[3], b)
PY

# 5. Merge: adopt only the new tracks/vias, restore heritage byte-for-byte from PRE
$KPY $TOOLS/route_merge.py merge prepped.kicad_pcb routed.kicad_pcb merged.kicad_pcb --report

# 6. Prove it
$KPY $TOOLS/heritage.py check heritage.json merged.kicad_pcb --allow-zone-growth --allow-edge
```

**`route.sh PRE OUT [passes]` now runs this whole recipe in one shot** (since 2026-09-14): prep →
keep-out fixture from `fc_keepout.json` on the export copy only (see §6/§7; the run aborts if the
fixture did not apply) → DSN export → fixdsn → Freerouting `-mt 1` in the background with a
`FR_TIMEOUT_MIN` guard → SES import into a fresh copy of PRE → merge (with the heritage-echo
filter, §7) → attachment gate + automatic prune (§7) → heritage check (refilled, core/band, §7 when
`REF_BOARD` is set) → DRC. The manual steps above are what it does, kept here for debugging one
stage at a time. Never edit `route.sh` (or any script) while a run of it is in progress: bash
reads scripts by byte offset, so an edit corrupts the running instance — copy `tools/pcb` to a
scratch dir and run the copy if you need to change something mid-run.

## What we found, in the order we found it

### 1. DSN export fails outright (before any Freerouting question even arises)

`pcbnew.ExportSpecctraDSN(board, path)` returns `False` and writes nothing on the synced board as
delivered. Root cause: 5 pre-existing heritage footprints -- silkscreen "LOGO" graphics, 0 pads --
share the unannotated reference `G***`. Specctra DSN requires unique component identifiers; KiCad's
exporter silently fails (no exception, no log message) when it finds duplicates. This is a heritage
board defect, unrelated to the sync, and will block every future route attempt on this board until
fixed.

Confirmed by renaming the 5 refs to unique placeholders (`G***` -> `G***__dup2` .. `__dup5`) in a
scratch copy: export immediately succeeds (596 KB DSN, vs. 0 bytes before). `heritage.py` never
compares the reference string (only uuid/position/rotation/layer/fpid/pad-nets), so this rename is
invisible to the heritage check -- safe to do on every routing copy.

**Fix**: `route_merge.py prep BOARD OUT` -- finds every duplicate/blank reference on the board and
renames all but the first occurrence to `REF__dup2`, `REF__dup3`, etc. Run this first, always.

### 2. Every existing wire/via is exported as `(type route)`

Inspected the DSN text directly: every one of the 2586 `(wire ...)` and 486 `(via ...)` records in
the `wiring` section (full board) carries `(type route)`, KiCad's default. Nothing marks
pre-existing copper as immovable. Per the Specctra spec and Freerouting's own behavior, `(type
route)` items are fair game for rip-up, fanout via insertion, and the optimizer.

### 3. Does heritage survive a naive round trip? No -- and worse, it wasn't clear it would ever finish.

First attempt: `route.sh` end to end (after fixing #1) with `-mp 2` on the full board. Freerouting's
**fanout** stage (a pre-pass that inserts vias near SMD pads to reach other layers, independent of
`-mp`) reported **1275 of 1475 SMD pins "needing fanout"** -- i.e. nearly every pad on the whole
board, heritage included -- and proceeded to add vias near them (+107, +21, +6, +1, +1, +2... across
12 passes, ~250 s total). Then **auto-routing** started ("613 unrouted items") and produced zero
further log output for 13+ minutes before we killed it. Two more attempts (with DSN-level fixes, see
below) hit what looked like the same wall at 5 minutes each.

We initially assumed this was a genuine hang. It mostly wasn't -- see "Freerouting is just slow"
below -- but two real, fixable problems were tangled up in it and are worth fixing regardless:

**3a. Mark every existing wire/via `(type fix)`.** Tested: on the full board, this had **zero
effect on the fanout stage** -- pass-by-pass via counts were pixel-for-pixel identical between the
naive DSN and the `(type fix)`-marked one (pass 1: 474 fanouted / +107 vias in both). `(type fix)`
stops Freerouting from *ripping up or deleting* a wire, but fanout's via insertion is a different
code path: it will still plant a new via wherever it likes, including directly on top of an existing
"fixed" wire -- which splits that wire into two pieces in the router's internal model. Net effect:
`(type fix)` is necessary (it stops wholesale rerouting of heritage nets) but **not sufficient** to
guarantee unchanged heritage geometry.

**3b. Degenerate wire stubs.** The DSN's `wiring` section contains 4 zero-length or
duplicate-consecutive-point `(wire ...)` records (nets GND, USB_DM, RF_VCC, USB_DP) -- artifacts
already present in the heritage board's own tracks (e.g. `(wire (path B.Cu 250  167000 -76400
167000 -76400))`). Freerouting chokes on these: `BasicBoard.normalizeTraces` hits a capped
2000-iteration "oscillating geometry" warning for a handful of *other* nets (harmless, self-limiting
-- unrelated nets, not caused by the stubs), but separately, an uncapped `"Polyline: must contain at
least 2 different points"` warning fires continuously from Freerouting's GUI repaint thread
(`BoardRenderer.renderConductionArea` -> `ConductionArea.ensureDetailedFillCache` ->
`ShapeSearchTree.overlappingObjects`, which throws `NullPointerException: currentObject is null` on
the degenerate geometry, gets caught, and the Swing `RepaintManager` just retries forever). This
spams the log (tens of thousands of lines/run) and burns CPU, but -- confirmed empirically --
**does not block forward progress**: real "Fanout pass N completed" / "Auto-routing pass N
completed" lines kept interleaving with the spam throughout. Still worth cleaning up: it's free,
removes noise, and the renderer crash-loop is wasted CPU competing with the router's own threads.

**Fix for both**: `route_merge.py fixdsn DSN OUT` -- rewrites every `(wire ...)` record, dropping
ones that collapse to a single point and de-duplicating consecutive duplicate points in the rest,
then replaces every remaining `(type route)` with `(type fix)`.

**3c. Freerouting says its own multi-threaded optimizer is broken.** Once `-mp` passes are
exhausted, Freerouting runs an additional, separate "Optimization" stage. Its log says, verbatim:
`WARN Multi-threaded route optimization is broken and it is known to generate clearance violations.
It is highly recommended to use the single-threaded route optimization instead by setting the
number of threads to 1 with the '-mt 1' command line argument.` We adopted `-mt 1`.

**Freerouting is just slow, not hung -- the real lesson.** To get a fast, complete round trip to
actually observe the auto-routing stage finish, we built a *reduced* test board (still all 480
footprints -- heritage.py needs every heritage footprint present or it reports them "removed" --
but only 177 footprints' and 288 heritage tracks' worth of copper kept, everything else pruned, plus
our own fresh `heritage.py snapshot` taken of that reduced board so the check is self-consistent).
On that board, each stage's timing was **completely deterministic and reproducible** across repeated
runs (same via counts, same scores, same seconds, to two decimal places): fanout 78 s (10 passes),
auto-route passes 117 s / 92 s / 83 s (`-mp 3`), optimization 140 s. Total ~9 minutes, non-hanging,
every time. The first time we ran this reduced board we killed it at the 111-second mark of
auto-routing pass 1 -- 6 seconds before it would have printed "pass #1 completed". **We had simply
not waited long enough**, on both the reduced board and, very plausibly, on the full board too (613
unrouted items is ~3.8x the reduced board's 163; a full-board auto-route pass taking 10+ minutes is
entirely consistent with what we measured). Lesson for the layout stage: budget a genuinely long,
unattended run (30-60+ minutes, more for higher `-mp`) for the full board, or route it in
per-subsystem batches the way we reduced it here. Don't kill a Freerouting run for "no log output in
N minutes" without first checking `ps` CPU% -- 100%+ CPU with no new line can just mean a slow pass.

### 4. Does the merge step actually restore heritage exactly? Yes -- confirmed, and here's why anything less would have failed.

SES import (`pcbnew.ImportSpecctraSES`) deletes and recreates every track/via on the board, heritage
included -- new uuids across the board, confirmed: checking the raw post-import board against a
snapshot taken immediately before export reports every one of the **288 heritage tracks/vias as
"removed"** (plus 288+1208=1496 tracks now present). This alone would fail a uuid-keyed heritage
check even if geometry were pixel-identical.

It is not pixel-identical either. We hypothesized the difference might be pure floating-point/DSN-unit
rounding noise (DSN resolution is 0.1 um) and tried matching post-route tracks back to pre-route
tracks by rounded geometry+net signature instead of uuid. **Zero of the 288 heritage tracks matched**,
even at 10 um rounding. Manually chasing one heritage track (net F4_PWR, a straight 3.47 mm run) to
its closest post-route counterpart found the nearest match 3.47 mm of combined endpoint distance
away -- i.e. Freerouting's fanout stage had planted a via partway along that "fixed" wire during
this run, splitting it into two separate track segments. **Neither uuid matching nor geometry
matching survives the round trip.** The only robust strategy is the one `route_merge.py merge`
uses: never trust the post-route board for what heritage geometry should be. Reconstruct the output
as an untouched copy of the pre-route board, and *add* whatever the post-route board has that the
pre-route board didn't (by signature diff) -- never derive, match, or "recognize" a heritage item in
the post-route board.

Result on the reduced test board (own fresh snapshot, not the project's `heritage.json` -- see
"Known caveats" for why):

```
$ heritage.py check reduced_heritage.json routed4.kicad_pcb --allow-zone-growth --allow-edge   # BEFORE merge
note: new items: footprints +0, tracks/vias +1208, zones +0
HERITAGE VIOLATION: footprint R38: x 191.1312 -> 191.1313
HERITAGE VIOLATION: footprint U10: x 186.2312 -> 186.2313
HERITAGE VIOLATION: PCB_TRACK F4_PWR on F.Cu at [217.3922, 90.5944] removed
... (287 more "removed" track/via lines)
heritage check: 290 violation(s)

$ route_merge.py merge reduced.kicad_pcb routed4.kicad_pcb merged4.kicad_pcb --report
PRE tracks/vias: 288   POST tracks/vias: 1496   new (by geometry+net): 1496
  touching a new (Phase-1, ref 200-799) footprint pad: 168
  review (no new-footprint pad on this item ...): 1328
wrote merged4.kicad_pcb: 288 heritage tracks/vias untouched (original uuids) + 1496 new tracks/vias adopted

$ heritage.py check reduced_heritage.json merged4.kicad_pcb --allow-zone-growth --allow-edge      # AFTER merge
note: bbox before [143.29, 47.5137, 260.05, 142.1249] after [143.29, 47.5137, 260.05, 142.1249]
note: new items: footprints +0, tracks/vias +1496, zones +0
heritage check: 0 violation(s)
```

**0 violations, reproduced.** The "review" bucket (no directly-touched new-footprint pad) is mostly
Freerouting's redraws/splits of existing heritage-net copper (like the F4_PWR example above) plus
chains between two new footprints via an intermediate point -- all of it is redundant/extra copper
sitting on top of the untouched original, safe to keep for this experiment and worth a human pass
before fab (see caveats).

### 5. Zones / GND planes and footprint positions (item 4)

Freerouting and the DSN/SES round trip never touch zones -- the `wiring` section covers tracks and
vias only, `(plane ...)` records are informational context for the router, not something it writes
back. All 41 zones came through with `+0` zones changed in every run, no outline changes, no
`--allow-zone-growth` note ever fired in these tests (nothing to allow -- the polygons were
bit-identical). Footprint positions likewise: SES import never repositions a footprint. The two
sub-micron "violations" seen in one raw (pre-merge) check (`R38 x 191.1312 -> 191.1313`, a 100 nm
delta) are DSN-round-trip floating-point noise, not real movement -- see caveats. They also
disappear after merge, since merge starts from the untouched PRE board's footprints unconditionally.

### 6. Flight-section keep-out (owner requirement: never route inside the flight-controller area)

Tested whether Freerouting can be kept out of the original Rev2 board footprint entirely, using a
pcbnew rule-area zone rather than trusting Freerouting's routing choices:

```python
poly = pcbnew.SHAPE_POLY_SET()
board.GetBoardPolygonOutlines(poly, False)          # on the ORIGINAL, un-synced FlatSat_V1.kicad_pcb
poly.Inflate(-pcbnew.FromMM(12), pcbnew.CORNER_STRATEGY_ROUND_ALL_CORNERS, pcbnew.FromMM(0.05))

z = pcbnew.ZONE(board)
z.SetIsRuleArea(True)
z.SetDoNotAllowTracks(True)
z.SetDoNotAllowVias(True)
z.SetDoNotAllowZoneFills(False)      # copper pour/zone fill still allowed inside it
ls = pcbnew.LSET()
for l in (pcbnew.F_Cu, pcbnew.In1_Cu, pcbnew.In2_Cu, pcbnew.B_Cu):
    ls.AddLayer(l)
z.SetLayerSet(ls)
# ... build z.Outline() from the deflated polygon, board.Add(z)
```

**KiCad's `ExportSpecctraDSN` does emit this as a proper Specctra keepout** -- confirmed by grepping
the exported DSN: 4 records, one per copper layer, e.g.
`(keepout "" (polygon F.Cu 0  212005 -59563.7  212833 -60778.1  ...))` -- placed in the `structure`
section alongside the existing 41 `(plane ...)` GND/power-plane records (which were unaffected,
still exactly 41). No DSN post-processing was needed for this part; a plain rule area with
`SetDoNotAllowTracks(True)` + `SetDoNotAllowVias(True)` round-trips through `ExportSpecctraDSN`
as-is.

Recipe: add the rule-area zone to the **DSN-export copy only** (never to the copy SES gets imported
into -- that board should come out clean, with no leftover keepout zone object). Concretely: run
step 1-2 of the TL;DR recipe, then add the keepout zone to `prepped.kicad_pcb` before the DSN
export sub-step (a `route_merge.py keepout` helper does this -- see below), export, `fixdsn`, route,
then import the resulting SES into the **un-keepout'd** `prepped.kicad_pcb` (not the keepout copy)
so the keepout zone never appears in the delivered board.

Ran the full recipe with this keepout added, on the reduced test board (`reduced.kicad_pcb` as
PRE, keepout inset 12 mm from the *original, un-synced Rev2* outline read straight off
`/Users/ncc-michael/GitHut/flight_controller_board/FlatSat_V1/FlatSat_V1.kicad_pcb`):

```
$ route_merge.py keepout reduced.kicad_pcb reduced_keepout.kicad_pcb \
      --outline-source .../FlatSat_V1/FlatSat_V1.kicad_pcb --inset-mm 12
deflated outline(s): [29] points, inset 12.0 mm
rule-area keepout zone(s) added: 1, on layers ['F.Cu', 'In1.Cu', 'In2.Cu', 'B.Cu']

# ExportSpecctraDSN on reduced_keepout.kicad_pcb -> grep the DSN:
(keepout "" (polygon F.Cu 0  212005 -59563.7  212833 -60778.1  212994 -60979.9  214234 -62311.3 ...
(keepout "" (polygon B.Cu 0  ... same polygon ...
(keepout "" (polygon In1.Cu 0  ... same polygon ...
(keepout "" (polygon In2.Cu 0  ... same polygon ...
# 41 (plane ...) records (the existing GND/power planes) unaffected, still exactly 41.

# fixdsn, then freerouting -mp 3 -mt 1: fanout was visibly more constrained by the keepout
# (pass 2: "40 SMD pins fanouted, 207 not routed" vs. ~74/23 without the keepout) and the
# auto-router finished with a worse score (517.88, 200 unrouted, 321 violations, vs. 852.18/60/105
# without the keepout) -- expected: the keepout removes the direct/short paths through the flight
# section, so more nets are left unrouted or take longer detours. Total time ~9 min, same ballpark
# as without the keepout.

# SES imported into reduced.kicad_pcb -- the PRE copy, WITHOUT the keepout zone -- not the
# DSN-export copy:
$ route_merge.py keepout-check reduced.kicad_pcb routed5.kicad_pcb \
      --outline-source .../FlatSat_V1/FlatSat_V1.kicad_pcb --inset-mm 12
new tracks/vias checked: 727
keepout check: 0 violation(s)

$ route_merge.py merge reduced.kicad_pcb routed5.kicad_pcb merged5.kicad_pcb --report
PRE tracks/vias: 288   POST tracks/vias: 727   new (by geometry+net): 727
  touching a new (Phase-1, ref 200-799) footprint pad: 165
  review (...): 562

$ heritage.py check reduced_heritage.json merged5.kicad_pcb --allow-zone-growth --allow-edge
note: new items: footprints +0, tracks/vias +727, zones +0
heritage check: 0 violation(s)

$ route_merge.py keepout-check reduced.kicad_pcb merged5.kicad_pcb \
      --outline-source .../FlatSat_V1/FlatSat_V1.kicad_pcb --inset-mm 12
new tracks/vias checked: 727
keepout check: 0 violation(s)

# and the delivered board carries no leftover rule-area zone:
merged5.kicad_pcb: 41 zones total, 0 of them rule areas.
```

### 7. Full-board smoke run of `route.sh` (2026-09-14) — four fixes that came out of it

Ran `route.sh pre.kicad_pcb routed.kicad_pcb 1` on the synced board (218 new footprints still
staged east at x ≥ 245 mm, so the routing itself was meaningless; the point was the composition).
Exit 0, heritage 0, 337 new items adopted, 1 pass = 28 min routing + 24 min optimizer; then the
L11 gate (`attachment_check.py`) reported 91 violations on 98 stub chains. Digging into them:

1. **The keep-out fixture had silently not been applied.** The inline pcbnew snippet in `route.sh`
   called `ZONE.SetDoNotAllowCopperPour`, which does not exist in KiCad 10 (`SetDoNotAllowZoneFills`
   is the name); the AttributeError scrolled past under `set -uo pipefail` without `-e`, and the "26
   keepout records in DSN" line was the mounting-hole rings. Freerouting ran unconstrained.
   Fixed: the snippet uses the right call, prints `KEEPOUT_APPLIED`, and `route.sh` re-opens the
   export copy and **aborts (exit 2) unless FC_* rule areas are present**.

2. **84 of the 91 "violations" were echoes of heritage wires, not routing.** Freerouting redraws,
   splits or merges `(type fix)` wires when it writes the SES (`Invalid traces after autoroute: 519
   traces not 45 degree` in its log is the same phenomenon), and KiCad's SES import rebuilds every
   track from the file. Those segments have no PRE signature, so the old merge adopted them: 37
   were 0.0 mm long, most of the rest 0.1–1 mm sitting on top of untouched heritage copper deep in
   the flight section. Fixed: `route_merge.py merge` now groups the new-signature items into
   connected chains (coincident endpoints per layer, vias join layers) and **adopts only chains that
   reach a pad of a new (ref 200–799) footprint** (`PAD.HitTest` on the pad's layer); echo chains
   and degenerate (< 0.01 mm) segments are dropped (`--adopt-all` restores the old behaviour).
   Result on the same SES: 337 → 215 adopted, 91 → 11 gate violations, all 11 genuine
   (Freerouting tapping heritage trace ends inside the band, plus 4 vias in the flight section —
   exactly what the missing keep-out allowed).

3. **The keep-out is now a real L11 fixture, not just the core.** `make_keepout.py SNAP PRE OUT`
   builds `fc_keepout.json` from the heritage snapshot + the board: flight core (outline − 12 mm,
   tracks+vias, all layers), `via_keepout` over the whole Rev2 outline, the whole band ring on
   In1/In2, and on F.Cu/B.Cu every heritage track/via/non-allowed pad in the band inflated by
   0.3 mm minus the allowed attachment pads (`attachment_check.ALLOWED_PADS`), fractured into 163
   polygons. Freerouting 2.4.1's DSN parser knows `keepout`, `via_keepout` and `place_keepout`
   only — KiCad exports a tracks-only rule area as `wire_keepout`, which it ignores — so every
   record is tracks+vias or vias-only (`forbid: both|vias`, `layers: all|[…]` in the JSON).
   Heritage pour fills are deliberately not in the fixture (a stub must cross the F/B pours to leave
   the flight section); a tap into a pour edge is still caught by the gate.

4. **Heritage fill check was blind.** `heritage.py check` measured the fills stored in the file,
   which nobody refills after routing, so copper carved by new tracks never showed. It now takes
   `--refill` (ZONE_FILLER in memory, 2.5 s), `--core-inset 12 --ref-board <Rev2 .kicad_pcb>`
   (reference fills measured on the refilled Rev2 board with the same filler, read-only): fills
   inside the core must be identical (0.1 %), the carve-out in the band is a note per zone.
   Verified: live synced board → 0 violations; the smoke board's deep taps → GND B.Cu 1921.5 →
   1917.8 mm² and In1 3188.7 → 3176.9 mm² flagged. `route.sh` runs this form when `REF_BOARD` is
   set, and **prunes automatically** (`PRUNE=1`, unpruned copy kept as `OUT.unpruned.kicad_pcb`,
   full gate output in `OUT.attach.txt`) so OUT always passes the gate; pruned connections come
   back as DRC unconnected items to be routed by hand from the allowed pads. The prune also trims
   whatever it left dangling (a new track end touching no track/via/pad, a new via reached on fewer
   than two layers), repeating until stable, so the pruned board carries no `via_dangling` /
   `track_dangling` debris (the v3 run: 5 rejected items + 16 trimmed).

**Re-run with all four fixes (same staged board, 1 pass):** keep-out fixture applied (166 tracks+vias
+ 1 vias-only rule areas → 195 `keepout` + 4 `via_keepout` records in the DSN), Freerouting pass 1
16.5 min + optimizer 21 min (it reports "7308 violations, score 0.00" because the fixed heritage
wires sit inside their own keep-out polygons — cosmetic, they are fixed and never ripped up; the
optimizer achieves nothing in this state), merge adopted 206 items, the gate found 5 stub chains
into the flight section with 2 violations (a 1.5 mm `+3V3` tap into the pour edge, an 18 mm `B-`
stub from J15.1 over the 14 mm allowance), auto-prune removed them, 0 violations after, heritage 0
with one band note (`+3V3` F.Cu band fill −2.8 %, the carve-out around the remaining stubs). The
unconnected count (444) is meaningless with the parts still staged 15–60 mm from their connectors;
it is the placement stage's job to make every shared net's nearest copper the allowed pad.

**0 keepout violations, 0 heritage violations, both confirmed on the same merged board.**
Freerouting fully honoured the DSN `(keepout ...)` records -- every one of the 727 new tracks/vias
routed around the deflated flight-section polygon. Since `keepout-check`'s new-item set is exactly
`merge`'s new-item set (same PRE/POST signature diff), and `merge` never touches anything already
inside the flight section (all 288 heritage items there are copied verbatim from PRE, never
re-derived from POST), the two checks are complementary: `heritage.py` proves nothing *heritage*
changed, `keepout-check` proves nothing *new* landed where it shouldn't -- together they cover the
whole board.

Practical note: don't skip `keepout-check`. The keepout zone only constrains what Freerouting
*chooses* to do; it is not a physical guarantee, and a future Freerouting version, a bug, or a
`--allow`-style override could ignore it silently. `keepout-check` re-derives the answer from the
actual output geometry, independent of whether the router behaved.

**If a future KiCad/Freerouting version does not export rule areas as DSN keepouts**, two
fallbacks, in preference order: (a) append Freerouting-native keepout records directly to the DSN
text after export (same `(keepout "" (polygon LAYER 0  x1 y1 x2 y2 ...))` syntax demonstrated
above, one per copper layer, inserted into the `structure` section before `(placement`) -- purely
textual, no KiCad involvement needed; (b) skip DSN-side prevention altogether and post-filter: after
`route_merge.py merge` (or on the raw SES-imported board), delete every new track/via whose any
endpoint falls inside the deflated polygon (point-in-polygon, same routine `heritage.py` already
uses for `--allow-zone-growth` containment checks) and report the nets that go unrouted as a result,
so the layout stage knows what still needs a human-placed or manually-approved crossing.

## Helper: `tools/pcb/route_merge.py`

Five subcommands, run with KiCad's bundled python3 (`heritage.py` and `route.sh` are unmodified):

- **`prep BOARD OUT`** -- disambiguates duplicate/blank footprint references (`REF__dup2`, ...) so
  `ExportSpecctraDSN` succeeds. Safe: `heritage.py` never compares the reference string.
- **`fixdsn DSN OUT`** -- drops zero-length/duplicate-point wire stubs, then marks every remaining
  `(type route)` wire/via `(type fix)`. Run on the DSN `route.sh`'s export step produces (or your
  own `ExportSpecctraDSN` call), before invoking Freerouting.
- **`keepout BOARD OUT --outline-source SRC [--inset-mm 12]`** -- adds a rule-area zone (no tracks/
  vias, copper pour still allowed) covering SRC's Edge.Cuts outline inset by `--inset-mm`, on every
  copper layer, to BOARD. Add to the DSN-export copy only; see "Flight-section keep-out" above.
- **`keepout-check PRE POST --outline-source SRC [--inset-mm 12]`** -- lists (and exits 1 on) any
  track/via in POST that is new relative to PRE and has an endpoint inside SRC's outline inset by
  `--inset-mm`. Run this regardless of whether a keepout zone was used -- it is the actual proof,
  independent of whether Freerouting honoured the zone.
- **`merge PRE POST OUT [--report]`** -- writes OUT as an untouched copy of PRE (every heritage
  footprint/track/via/zone/edge keeps its exact uuid and geometry) plus every track/via from POST
  whose (net, layer, start, end, width) -- or for vias, (net, position, pad size, drill) -- signature
  has no match anywhere in PRE. `--report` breaks the adopted set down into "touches a new (Phase-1,
  ref 200-799) footprint pad" vs. "review" (no such pad touched directly -- likely a Freerouting
  redraw/split of an existing heritage-net segment; harmless, since the original segment is
  untouched underneath, but worth a human pass before fab to drop the redundant copper).

`route.sh` needs no code changes for this recipe; wrap it with `prep` before and `merge` after (or,
since `route.sh` bundles export+route+import+DRC in one non-resumable shot, replicate its two
`pcbnew` heredocs by hand around a `fixdsn` step in between, as the TL;DR above does).

## Known caveats

- **`heritage.py`'s comparisons have zero numeric tolerance.** A DSN/SES round trip can introduce
  ~100 nm (0.0001 mm) noise in reported footprint positions even though nothing was meant to move
  (seen on the raw, pre-merge board: `R38 x 191.1312 -> 191.1313`). This is below any physically
  meaningful threshold (KiCad's internal unit is 1 nm; JLCPCB placement tolerance is measured in
  tens of microns) but will show as a "violation" on an unmerged/raw post-route board. It vanishes
  after `route_merge.py merge` (which starts from PRE's footprints unconditionally) -- one more
  reason to always run merge rather than accept a raw SES-imported board directly.
- **`(type fix)` does not prevent Freerouting from splitting a heritage wire.** It stops rip-up and
  deletion, not fanout via insertion mid-wire. Confirmed via direct geometry chase (see section 4).
  This is exactly why the merge step exists and is not optional -- do not skip it and trust
  `(type fix)` alone, even though it's still worth doing (it reduces disturbance and keeps the
  router from wasting effort re-deriving already-good topology).
- **The "review" bucket from `merge --report`** (no new-footprint pad touched) is mostly redundant
  copper -- Freerouting redrawing part of an existing connection. It does not violate heritage (the
  original segment underneath is untouched) but it is wasted/overlapping copper that a human should
  review and likely delete before this board goes to fab. This experiment did not attempt to
  auto-detect and strip it; a future improvement to `route_merge.py merge` could flag or drop
  "review" items that don't touch any Phase-1 footprint pad at all (fully heritage-net-internal),
  since those provide no new connectivity.
- **We validated the full recipe end-to-end on a reduced board (177/480 footprints' worth of
  copper kept), using a heritage snapshot taken fresh from that reduced board**, not the project's
  `heritage.json` (which describes the full 480-footprint/3271-track board and would report every
  pruned item "removed" against a deliberately-shrunk test board -- a self-inflicted, uninteresting
  failure). The mechanism (prep -> fixdsn -> route -> merge -> check) does not depend on board size;
  running it on the real, full synced board against the real `heritage.json` should reproduce the
  same 0-violation result, just much more slowly (see timing below) -- we did not have a run of the
  full board complete within this session's time budget to paste a literal 0-violation transcript
  against `heritage.json` itself, and that is an honest gap the layout stage should close by running
  the recipe once, unattended, for long enough.
- **DRC is not clean on the merged board** (848 violations, 103 unconnected, mostly clearance/hole
  clearance/courtyard overlap) -- expected and not a heritage problem: the 218 new footprints were
  routed from a crude rectangular test notch stapled onto the outline (not the eventual real outline
  from `outline.py`), and only a curated subset of new nets were given anywhere legal to route to in
  this experiment. The layout stage should use `outline.py` for a proper contoured outline extension
  (with the real GND pour grow, mounting holes, stitching) before a production routing pass, not this
  notch hack.
- **The synced board's baseline (before any of this) already passes heritage** with 0 violations
  (218 new footprints, 0 new tracks/zones) -- confirmed first, before touching anything, as the
  starting point for every experiment above.
- **This is a shared, actively-edited repo.** `tools/pcb/heritage.py` and `tools/pcb/route.sh`
  changed under us mid-task (other concurrent work, not this experiment -- we never wrote to either
  file). All results above were re-verified against the live versions of both before writing them
  down (still 0 violations throughout). Notably, the live `route.sh` has grown its own inline
  `KEEPOUT_JSON`-driven rule-area mechanism (an env var naming a JSON file of keepout polygons,
  applied to the export copy the same way section 6 describes) -- that is not something this
  experiment added, wrote, or validated; `route_merge.py keepout` / `keepout-check` are independent
  of it and were what we actually tested end to end. If using `route.sh`'s `KEEPOUT_JSON` instead,
  still run `route_merge.py keepout-check` afterward -- it re-derives the answer from output
  geometry and doesn't care which mechanism produced the DSN keepout.

## Timing summary

| stage | full board (480 fp / 3271 tracks / 41 zones) | reduced test board (177 fp / 288 heritage tracks / 41 zones) |
|---|---|---|
| DSN export (after `prep`) | ~1-2 s | <1 s |
| Freerouting fanout | ~250 s (12 passes, stops on no-progress) | ~78 s (10 passes) |
| Freerouting auto-route, `-mp 3` | not completed in this session (each pass plausibly 10+ min; see "Freerouting is just slow") | 116.5 s + 92.3-92.8 s + 82.6-83.4 s (3 runs, near-identical each time) |
| Freerouting optimization, `-mt 1` | not reached | 140 s |
| SES import | <1 s | <1 s |
| `route_merge.py merge` | not run (no full-board SES) | <5 s |
| `heritage.py check` | ~0.6 s | ~0.5 s |
| **total, reduced board, start to 0-violation merged board** | -- | **~9 minutes** |

## How the layout stage should use this

1. Copy the synced board; never route in place.
2. `route_merge.py prep` it.
3. If growing the outline for real (not this experiment's notch hack), use `outline.py` first, on
   the same copy, before the DSN export.
4. Export DSN, `route_merge.py fixdsn` it.
5. Run Freerouting with `-mt 1` and a generous, unattended time budget -- do not judge it hung from
   log silence alone; check CPU%. Use `-mp` as low as gets an acceptable score in the time available;
   higher `-mp` costs roughly linearly more wall time per the numbers above.
6. Import the SES into a **fresh copy of the pre-route board** (step 2's output, or step 3's if the
   outline was grown), not into the DSN-export copy if it carried extra fixtures (like a keepout
   zone) that shouldn't end up in the delivered board.
7. `route_merge.py merge PRE POST OUT --report`. Read the report; delete/rework anything obviously
   redundant in the "review" bucket before proceeding.
8. `heritage.py check heritage.json OUT --allow-zone-growth --allow-edge` -- must be 0 violations.
   `--allow-edge` only matters if the outline was actually grown in step 3; `--allow-zone-growth`
   only matters if `outline.py`'s GND-plane grow was used.
9. If the flight-controller section must stay untouched (owner requirement -- see "Flight-section
   keep-out"): run `route_merge.py keepout` on the DSN-export copy before step 4, and
   `route_merge.py keepout-check PRE OUT --outline-source ... --inset-mm 12` after step 7, exit code
   must be 0. Do this in addition to, not instead of, the heritage check in step 8 -- they prove
   different things.
10. Only then run a full DRC pass and hand the board to the normal pre-order review procedure.

### 8. Routing attempt 1 on floorplan v2.3 (2026-09-20) — three more tool fixes

1. `attachment_check.py` ALLOWED_PADS was last-match-wins, so the J14 pins 10/12 exception (22 mm) listed
   first was overwritten by the general J14 row (14 mm). Now first-match-wins (`setdefault`).
2. `route.sh` copied only the `.kicad_pro` beside its intermediate boards. KiCad falls back to factory-default
   design rules when `.kicad_dru` / lib tables are missing, which inflated clearance and lib-footprint DRC
   counts and shifted zone fills. `siblings()` now copies `.kicad_pro`, `.kicad_dru`, both lib tables and the
   local libraries next to PREP / EXPORT / POST / OUT. Same lesson as `build_floorplan.sh`.
3. `heritage.py check` flagged the FC's F.Cu +3V3 pour: −28 mm² inside the 12 mm core, −110 mm² in the band.
   Cause: compliant stubs (14–24 mm deep, wider than the pour's slivers between adjacent connectors) carve the
   pour and isolate slivers that KiCad removes as islands — so the change reaches past the 12 mm line without
   any new copper there. The check now excludes fill changes within `--exclude-new-mm` (1.0) of new copper and
   classifies a core loss whose every piece touches new copper as a note ("stub carve-out / removed island");
   lost copper that touches no new copper still fails. The +3V3 net is carried by the In2 plane; the F.Cu pour
   loss along the right edge is the accepted price of the L11 stubs.

### 9. Closure rounds (2026-09-20) — what closed the last connections

Routing attempt 2 (Opus) delivered a heritage-clean, DRC-clean board with 76 unconnected items; the two Sonnet
DRC-cleanup rounds could not move that number, so the workflow gained a `stage: "close"` mode (args `boardPath`,
`priorUnconnected`, `closureNotes`) that resumes from a routed board with new rulings. Closure attempt 1 took 76 → 39
and measured the rest: the RP2350's 0.4 mm QFN-60 ring cannot escape 21 more signals under the Default 0.20 mm
clearance with 0.46/0.20 vias (one via per two lands; the 0.34 mm gap between first-row vias is less than the
0.527 mm a track needs, so no second row). Rulings F11–F13 (brief §12): single-via allowance extended to J16.1 and
J14.10/12 (24 mm); trace taps for F0_SCL / F4_SDA / Deploy2_EN (`NET_TAP_EXCEPTIONS`); J1.6 → 20 mm, U6.6 → 24 mm;
an `EMU_FANOUT` constraint-only rule area with a `.kicad_dru` rule (clearance 0.127 mm, via 0.40/0.20) so a
0.127 mm track passes between 0.40 mm first-row vias and a second row exists — inside JLCPCB's 4-layer capability
(0.09/0.09 mm, via 0.15/0.25) and the same scoped-0.127 practice as the FC's own `.kicad_dru`; GND lands go inward
on F.Cu to the exposed pad, as the flown FC's U18 does (same footprint, rotated 45°, 34 of 60 lands surface-routed).

## 10. `tools/pcb/closure/` — promoted closure-round tooling (2026-09-22)

Three tools from the closure-round scratchpad (`.flatsat_work/phase2/`), worth keeping because
nothing else on the project does what they do (route_report.md D2/D7/C5): every path is now an
argument (no hard-coded scratch paths), read `--help` on any of them for the full option list.

| Tool | What it does | Exactness guarantee |
|---|---|---|
| `clusters.py` | Connected-component view of a net via KiCad's own connectivity engine (`BuildConnectivity`/`GetConnectivity`). With no net args, lists every net that has more than one cluster and a lower-bound "extra clusters" count; with net args, lists every item in every cluster. Read-only — never calls `SaveBoard`. | Uses the same connectivity engine DRC's unconnected-item count uses, not an independent geometry model. |
| `fan2.py` | Exact-polygon staggered fan-out for a fine-pitch part (default U200) inside a relaxed-clearance rule area (default the `EMU_FANOUT` bbox, brief 12 F13a): two staggered via rows, 1/2/3-segment tracks, same-net pad/via sharing. | Every emitted track/via is checked with KiCad's own `TransformShapeToPolygon` + boolean intersection at the true per-pair rule (area-relaxed clearance only when both items intersect `--area`) before being kept — not an inscribed-circle approximation. |
| `micro.py` | Area-aware fine router for short hops out of a fan-out ring — the only router on the project that can leave a rule area, because it is the only one that rasterises two obstacle sets (default netclass and the relaxed rule-area clearance) and only trusts the relaxed set `--inset` mm inside the area. Depends on `rgeo.py`/`mlroute.py` (multi-layer Dijkstra) and `clusters.py`, copied alongside unchanged. | The raster search is a heuristic accelerator only: every segment/via it proposes is re-verified with `fan2.py`'s exact-polygon check before being added, and a raster win that fails that check is discarded, never emitted. |

All three (and `rgeo.py`/`mlroute.py`, promoted alongside `micro.py` as its unmodified
dependencies) keep their original algorithms; the only functional fix was `fan2.py`'s and
`micro.py`'s `load_cls()`/snapshot calls, which previously pointed at one hard-coded session
scratchpad `.kicad_pro`/heritage-snapshot path regardless of the board passed in — both now
default to the board's own sibling / the repo's `tools/baseline/heritage_rev2.json` and accept
`--project`/`--snap` overrides. `micro.py` and `fan2.py` also gained `--dry-run` (do everything
except `SaveBoard`, so they can be smoke-tested against a board copy without writing to it).

Smoke-tested 2026-09-22 against a read-only copy of the closure-round-3 input board
(`.flatsat_work/phase2/round3/base/`, copied whole so `.kicad_pro`/`.kicad_dru`/libraries travel
with it): `clusters.py` with no net args reproduced the input board's open-item picture (28 of the
documented 29 unconnected shown as named multi-cluster nets — GND's ten extra clusters plus 18
single-extra-cluster emulator/Deploy2_EN nets; the 29th is the pre-existing heritage U6.1/U6.29
GND item folded into GND's own count); `fan2.py --dry-run --pads 18,60` on U200 reproduced route_
report.md D2's documented "no site" result for exactly those two lands (U200.18, U200.60), with
`OUT.json` written and the input board's checksum unchanged; `micro.py --dry-run --only
EMU_CTL_FC_RESET` ran the full raster-Dijkstra-then-exact-check pipeline end to end and correctly
reported no route at 29.83 mm gap (consistent with D8: this class of net needs autorouter work,
not fan-out routing), again with the input board's checksum unchanged. `--help` on all three was
also verified. No board file was modified by any of this — see `--dry-run`/`--dry` above.
