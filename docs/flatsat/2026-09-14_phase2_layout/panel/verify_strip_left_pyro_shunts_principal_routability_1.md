# Skeptic verification — strip_left_pyro_shunts — PLR-06

Board re-measured: `.../scratchpad/panel/project/FlatSat_V1.kicad_pcb` (v2.2 scratch copy), pcbnew.

## PLR-06 — "3V3_EMU and PYRO_INHIBIT_STATE must cross the whole strip at BenchPower 1.0mm width through a 2.25mm corridor"

**Verdict: CONFIRMED (major).**

Independent re-checks, all matched the finding:

1. Airwires — `facts.md` line 277/280, 494/495: PYRO_INHIBIT_STATE 2 pads, U200.35(276.6,96.1)→R601.2(163.3,158.6), 129.4mm, 50 crossings. 3V3_EMU 34 pads, MST 223.4mm, 105 crossings, longest edge C209.1→R602.2(157.5,158.6) 125.8mm. Exact match.
2. Corridor scan (`principal_prior_measurements.md` lines 609-630, strip N-S free-band scan): x=250 free 141.50-143.75 = **2.25mm** (blocker TP401 143.75-145.25); x=265 free 141.50-144.05 = **2.55mm** (TP511); x=220 free 141.50-144.59 = **3.09mm** (C315). Exact match to the finding's numbers.
3. BenchPower geometry: re-derived 1.000mm track + 2×0.250mm clearance = 1.500mm minimum lane. Arithmetic correct.
4. In2 availability — **independently re-measured via pcbnew** (not just cited from prior notes): all 7 In2 zones (INHIB_2, VSOLAR, B-, VBUSP, +3V3, RF_VCC, Dir_Chrg_In) bound at maxX=231.14, maxY=141.87. This lands within 0.04mm of the finding's claimed "x≤231.1/y≤141.9" — In2 is genuinely empty over the entire strip and wing extension. This is the load-bearing fact for the recommendation and it holds.
5. L6 checked against `00_pm_brief.md` line 39: "In2 gets no new FC-power pours (leave the FC's In2 nets as they are)" — restriction is scoped to *FC-power* pours. 3V3_EMU/PYRO_INHIBIT_STATE are new emulator/pyro-bench nets, not FC power, so the citation is used correctly and the recommendation does not violate L6.

One caveat noted, not a refutation: the project's `net_settings` in this scratch copy currently defines **only the Default class** (0.25mm track / 0.2mm clearance) — no BenchPower netclass object exists yet, and pcbnew reports both 3V3_EMU and PYRO_INHIBIT_STATE as `Default` today. This just reflects that netclasses haven't been created yet (a routing-setup step per the brief's rule table), not an error in the finding — the BenchPower assignment is the owner's documented design rule for these nets and will be applied before routing. Doesn't change the verdict.

Additional check performed (widens confidence): scanned neighboring columns (x=230/240) — free channel there is 10.97mm, i.e., TP401/TP511/C315 are narrow point-obstacles, not a wall across the whole strip. A track *could* jog south locally around each one using the wide channel just past it (145.25-172.12 at x=250, 145.55-159.36 at x=265, 146.11-153.30 at x=220). So a single track alone is not strictly forced through the 2.25mm pinch. But the finding is about **two** nets sharing the same corridor at BenchPower width, and it correctly identifies that routing them as ordinary F.Cu tracks would require either a 1.5mm-lane squeeze at the tightest point or repeated jogs for both nets around three obstacles in series — exactly the "extra layer changes / detour" condition in the major-severity definition. The In2 escape avoids all of that. Recommendation is sound as written; no better placement-only fix exists (moving TP401/TP511/C315 would touch other datasheet-driven placements already audited PASS, and the PM brief prefers no part churn once audited).

**Confidence: 0.85** (up from reported 0.8 — corridor and In2-emptiness figures independently re-measured and matched almost exactly).

**Recommendation stands as reported**, restated for the checklist:
- Do NOT route 3V3_EMU or PYRO_INHIBIT_STATE as ordinary BenchPower/Default F.Cu tracks straight across the strip's north band.
- Pour 3V3_EMU on In2 over x 265-296 / y 86-112 (holds 24/34 pads incl. U200, C204-214, R200-211); single 0.5mm In2 stub west to R602.2.
- Route PYRO_INHIBIT_STATE (U200.35→R601.2) on In2 through the same now-clear corridor.
- Net effect: the 2.25mm F.Cu north band at x=250 (and the 2.55mm/3.09mm points) stays free for the strip's own local signals, and no via-farm/extra-layer improvisation is needed later in routing — satisfies owner priority #3 (no complex routing maneuvers to close).

No datasheet-checklist row in `detail/placement_strip_left_pyro_shunts.md` is contradicted by this (it is a routing-layer decision, not a part move; no PM-decided item is re-litigated).
