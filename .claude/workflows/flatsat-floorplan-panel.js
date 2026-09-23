export const meta = {
  name: 'flatsat-floorplan-panel',
  description: 'Two-persona review panel of the FlatSat floorplan (principal layout engineer = Opus, junior developer / bench user = Sonnet) → Sonnet skeptics refute every finding with measurements → Opus chair writes the report and a fix plan. Priorities: problematic placements, manufacturability, routing closure without complex manoeuvres.',
  whenToUse: 'Owner-requested review panel of a placed, unrouted board before routing. args: {project, board (scratch project board with siblings), docs, scratch, facts (dir with facts.json/facts.md), drcJson, floorplanJson, floorplanMd, blocksJson, brief, kicadPy, kicad, heritageSnap, refBoard, models?:{principal,junior,verify,chair}, context}',
  phases: [
    { title: 'Review', detail: 'principal layout engineer ×2 (routability, manufacturability; Opus) + junior developer / bench user (Sonnet)' },
    { title: 'Verify', detail: 'Sonnet skeptics, block batches of ≤ 8 findings, ≤ 2 at a time, prompted to refute with measurements' },
    { title: 'Chair', detail: 'Opus chair: merge, rank, report, fix plan', model: 'opus' },
  ],
}

const A = args
const M = Object.assign({ principal: 'opus', junior: 'sonnet', verify: 'sonnet', chair: 'opus' }, A.models || {})
const KPY = A.kicadPy
const OUT = `${A.docs}/panel`

const COMMON = `PROJECT CONTEXT: ${A.context}

HARD RULES (repo CLAUDE.md + owner): never write ${A.project}/FlatSat_V1.kicad_pcb (the live board) or anything under FC_V5e_Production_Rev2/; never open the KiCad GUI; no git commits. The board under review is ${A.board} (a scratch copy of floorplan v2.2 with its .kicad_pro/.kicad_dru/.kicad_prl and all schematics next to it, so kicad-cli DRC with parity works there) — treat it as READ-ONLY; if you want to try a move, copy it into your own scratch dir ${A.scratch}/panel/<your-role>/ first. KiCad python = ${KPY} (module pcbnew; pipe stderr through grep -vE 'stdpbase|pcb_track|memory leak|Debug:'); kicad-cli = ${A.kicad}. Run tools from ${A.project} (cd there). WebFetch/WebSearch are available through ToolSearch — use them for connector drawings, datasheets and JLCPCB capability pages, and cite what you fetched.

THE BOARD: FlatSat V1 = the flight controller Rev2 layout (frozen, byte-for-byte; 265 heritage parts, 128 top / 137 bottom) grown into an L: right wing x 231.4–296.4, bottom strip y 142.1–172.1; board 153 × 125 mm, 4 layers (F.Cu / In1 GND plane / In2 / B.Cu), JLC04161H-7628 stackup. 218 new parts (215 top, 3 bottom: the TCA4311A buffers U310/U312/U314 opposite the FC's bottom-side face connectors J9/J13/J2), 40 distinct footprints, 88 distinct footprint+value. Design rules (.kicad_pro): min clearance 0.127, min track 0.127, min via 0.4/0.2 drill, copper-to-edge 0.2, hole-to-hole 0.5; Default class 0.2 clearance / 0.25 track / via 0.8/0.4; BenchPower class 1.0 mm track / 0.25 clearance / via 0.8/0.4 (VBAT_BENCH_N, VSOLAR_BENCH_A/B, VBUS_CHG, CHG_SYS/BAT/PMID, VBUS_EMU, 3V3_EMU, MID_BENCH; and new copper on Dir_Chrg_In / B- / VBUSP / VBATT_SENSE / INHIB_x / IN_RBF / VSOLAR at 1.0–1.5 mm); USB_EMU class 0.25 mm coupled pair on F.Cu (EMU_USB_DP/DM, length-matched ≤ 1 mm, no vias if avoidable). Fab/assembly at JLCPCB (both sides already assembled on the FC). The FC has no fiducials. Nothing is routed yet (383 unconnected items is the expected state).

OWNER'S STANDING RULES: (L4) heritage frozen — no existing part/track/zone changes; (L11) new copper enters the flight section only as short stubs from allowed connector pads (attachment map in ${A.floorplanMd} §2; enforced by tools/pcb/attachment_check.py and a Freerouting keep-out); (L3) the 12.00 mm lane x 231.39–243.39 in front of the FC's right-edge connectors J1/J2/J6/J9/J11/J13/J16/J12/J22 stays free of parts taller than 2 mm and of headers; (L2) block order per the brief; (L8) silkscreen legends come at stage 6 but need room now; brief §12: block plan, lane, holes and F.Cu passives accepted by the owner; passives placed to manufacturer layout guidelines (176 rules checked, all blocks audited PASS). PM decisions already taken (do not re-litigate unless you have a measured reason): support parts may move inside switching loops; capacitors against the pin they serve may sit below 0.5 mm courtyard gap; fixed-anchor envelope breaches are not findings; 0402 parts poking 0.5 mm into the wider 12.6 mm band are fine.

READ FIRST (in this order): ${A.floorplanMd} §1 (owner summary, gate table, attachment reach) and §3 (per-block checklists); ${A.brief} §2 (board facts), §3 (L1–L11), §12; ${A.blocksJson} (block → refs, envelopes, fixed anchors); ${A.facts}/facts.md (PRE-MEASURED: courtyard gaps < 1 mm, parts near mounting holes / board edge, per-net airwire MST length + longest edge + crossings, per-block crossings and edges leaving, the 37 shared-net attachment stubs with allowed-pad vs any-pad distance, top-40 longest airwires, full placement table with LCSC) and ${A.facts}/facts.json (same, machine-readable; nets[net].edges has every airwire with endpoints); ${A.drcJson} (kicad-cli DRC with parity on this board: 7 clearance errors all intra-footprint inside U301/Q510, 1 courtyard overlap = the heritage SW2/TP2 item, parity 11 = the known FC baseline). Renders: ${A.docs}/img/floorplan_v2_top.png / _bottom.png (3D), floorplan_v2_top.pdf / _bottom.pdf / _in1_gnd.pdf / _in2.pdf / _all_copper.pdf (fab-style with courtyards), and per-block close-ups floorplan_v2_block_<block>.png (+ face_column_n/m/s tiles and face_column_bcu). Make your own close-ups when you need them: cd to the directory holding ${A.board}; ${A.kicad} pcb render --side top --width 1400 --height 1000 --zoom Z --pivot (cx-219.866)/10,(109.842-cy)/10,0 -o out.png FlatSat_V1.kicad_pcb (pivot in cm from the board centre, +Y toward smaller board y; zoom = min(220/(W+4), 157/(H+4)) for a W×H mm window). Per-block datasheet checklists: ${A.docs}/detail/placement_<block>.md and audit_<block>.md. Supply chain (Basic/Extended, stock): ${A.docs}/supply_chain_report.md. Connector footprints in use on the new area: Phoenix MKDS 1,5/2-5.08 (J400/J401) and 1,5/3-5.08 (J500) horizontal screw terminals; HRO TYPE-C-31-M-12 USB-C (J701, J510; the FC's own J12 is the same part); JST SH BM03B-SRSS-TB (J702 SWD); 2x05 2.54 mm header (J703); 1x02 2.54 mm headers (JP400/401/500/510/600–607); 1x06 2.54 mm header (J300); MSK12C02 SPDT slide switch (SW600, SW703); tactile switches SW701/SW702; the FC's face connectors are Molex Pico-Lock 504050 1x06 horizontal (J1/J2/J6/J9/J11/J13) and Hirose DF11 2x06 (J16), JST SH (J22).

WORKING LIMITS (the first run of this panel stalled on hung web fetches and over-long single responses — these rules are mandatory): at most 3 WebFetch/WebSearch calls per agent, and only for a figure you cannot get from the local files; every Bash command must finish within 90 s (load the board once per script, never run kicad-cli DRC — use ${A.drcJson}); write your notes file in sections of at most 60 lines per Write/Edit call and update it as you go (a stalled agent loses everything it has not written); keep each response short — measure, decide, record, move on; aim for at most 30 tool calls in total. Salvaged measurements from the previous attempt are in ${A.facts}/principal_prior_measurements.md (U200 escape gaps, corridor free-channel scans, stub straight-line crossings, top crossing edges, the U200 pin table, USB-C footprint geometry, JLCPCB figures: standard PCBA needs edge rails ≥ 5 mm or ≥ 3.35 mm fiducial clearance, 3–4 fiducials of 1 mm copper / 2 mm mask opening, minimum IC pin spacing 0.35 mm, 4-layer 0.09/0.09 mm track/space, via 0.15/0.25 mm, copper-to-edge ≥ 0.2 mm) — reuse them and cite them instead of re-measuring; the scripts that produced them are ${A.scratch}/panel/s1.py … s14.py and scan.py (corridor scanner).

HOW TO REPORT: every finding needs (a) refs, (b) a measured number or a quoted drawing/datasheet/capability figure, (c) a concrete recommendation (which part moves where, or which rule/order setting changes) and (d) an honest confidence 0–1. Severity: blocker = must change before routing starts (a placement that cannot be routed within the rules, cannot be assembled, cannot be mated/used, or breaks an owner rule); major = should change before routing (routing would need a detour/extra layer changes/via farms or manufacturability/usability is measurably worse); minor = fix at a later stage or accept; note = information. Prefer 8 solid, measured findings over 30 speculative ones. Zero blockers is an acceptable answer. Do not report things the PM already decided (above) or that belong to routing/silkscreen stages unless the placement makes them impossible.`

const FINDINGS = {
  type: 'object',
  properties: {
    scope_checked: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string', description: 'short unique id, e.g. PLE-03 or JD-07' },
          title: { type: 'string' },
          category: { type: 'string', enum: ['placement', 'manufacturability', 'routability', 'usability'] },
          severity: { type: 'string', enum: ['blocker', 'major', 'minor', 'note'] },
          refs: { type: 'string', description: 'comma-separated refdes involved' },
          block: { type: 'string', description: 'block name from blocks.json, or "board"' },
          location: { type: 'string', description: 'x,y mm / layer / side' },
          description: { type: 'string' },
          evidence: { type: 'string', description: 'measured numbers, quoted figures, file+line' },
          reference: { type: 'string', description: 'drawing / datasheet / JLCPCB capability page / brief rule' },
          recommendation: { type: 'string', description: 'concrete: ref → x,y,rot or block-level change' },
          confidence: { type: 'number' },
        },
        required: ['id', 'title', 'category', 'severity', 'refs', 'block', 'location', 'description', 'evidence', 'reference', 'recommendation', 'confidence'],
      },
    },
    routing_forecast: { type: 'string', description: 'principal only: the nets/corridors that will need care and why; junior: leave empty' },
    report_md_path: { type: 'string', description: 'where you wrote your full notes' },
  },
  required: ['scope_checked', 'findings', 'routing_forecast', 'report_md_path'],
}

const VERDICTS = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'string' },
          verdict: { type: 'string', enum: ['confirmed', 'refuted', 'downgraded', 'upgraded'] },
          severity_after: { type: 'string', enum: ['blocker', 'major', 'minor', 'note'] },
          reason: { type: 'string' },
          evidence: { type: 'string', description: 'your own measurements / fetched figures' },
          recommendation_after: { type: 'string' },
        },
        required: ['id', 'verdict', 'severity_after', 'reason', 'evidence', 'recommendation_after'],
      },
    },
    notes_md_path: { type: 'string' },
  },
  required: ['verdicts', 'notes_md_path'],
}

const CHAIR = {
  type: 'object',
  properties: {
    report_path: { type: 'string' },
    fix_plan_path: { type: 'string' },
    counts: { type: 'string', description: 'blockers / majors / minors / notes / refuted after verification' },
    blockers: { type: 'array', items: { type: 'string' } },
    majors: { type: 'array', items: { type: 'string' } },
    recommendation: { type: 'string', enum: ['route-now', 'fix-then-route', 'rework-blocks'] },
    routing_forecast: { type: 'string' },
    summary: { type: 'string' },
  },
  required: ['report_path', 'fix_plan_path', 'counts', 'blockers', 'majors', 'recommendation', 'routing_forecast', 'summary'],
}

const PRINCIPAL_A = `${COMMON}

ROLE: Principal layout engineer — ROUTABILITY half. You will route this board next; you are reviewing the placement so that the routing closes without complex manoeuvres. Write your notes to ${OUT}/principal_routability.md (mkdir -p ${OUT}); finding ids PLR-01…. Work through ALL of section A below and report what you measured, not what you assume. Put your routing forecast (§A.6) in routing_forecast.

A. ROUTABILITY / CLOSURE RISK (use facts.json nets[].edges, crossings and blocks, then look at the board):
 1. U200 (RP2350 QFN-60) escape: pad pitch and pad width from the footprint; with 0.127 min track/clearance can one 0.127 track pass between pads? Which pins need an inner-layer escape (via 0.4/0.2 or 0.8/0.4, no via-in-pad)? Is there room for the escape vias between U200 and its ring of decoupling caps (caps sit 0.035–0.055 mm from the body — measure the free annulus)? Same for U511 (BQ25886 QFN-24) with its bootstrap/input caps, and Q510 (DFN2020).
 2. Decoupling-cap GND returns: for every cap sitting against its IC pin, is there ≥ 1.2 mm free beside its GND terminal for a 0.8/0.4 via (or 0.6/0.3) to In1 without crossing another pad? List the caps where a via does not fit and what the router will have to do instead.
 3. Corridors: (a) face column → emulator core: 7 channels × (SDA, SCL, EN?) = count the signals crossing the gap between the column (x ≤ 266.3) and the core (x ≥ 269); measure the free width of that gap and what parts sit in it; (b) emulator core → bench I/O cable (USB pair, SWD, buttons); (c) the USB pair J701 → R703/R704 → U200 on F.Cu as a 0.25 mm coupled pair with no vias — is the straight corridor free of parts, and what is its length; (d) wing → strip: 3V3_EMU (MST 223 mm, 105 crossings), PYRO_INHIBIT_STATE (129 mm), Dir_Chrg_In, WDT_DISABLE — where do they cross the wing/strip corner and is there a channel; (e) BenchPower 1.0–1.5 mm tracks in the 30 mm strip: J500 → Q500/Q501/U500 → JP602–607 and J14; J400/J401 → F400/F401 → D400/D401 → JP400/JP401 → the face connectors' VSOLAR pins (J11.1 etc.: the 1.0 mm VSOLAR track has to travel from the strip up the wing into the lane — trace its corridor); J510 → U511 → L510 → JP510. Measure the narrowest passage each corridor must pass (between courtyards) and compare with the track width + 2 × clearance (+ via) it needs.
 4. L11 stubs: for each of the 37 shared nets (facts.json stubs + floorplan_v2.md §2), draw the straight segment from the allowed FC pad to the new pad and list the new-part courtyards it crosses (script it with pcbnew: segment–bbox intersection). A stub that must snake around parts is a "complex manoeuvre"; the three bottom-side buffers' stubs run on B.Cu — check they are clear on B.Cu too.
 5. Crossing hot-spots: facts.json says 870 MST crossings in the new area (emulator_core 1318 touching, face_column 884, battery_replica 252, bench_io_cable 229). Identify the 5 worst local hot-spots (which parts / which nets) and whether a rotation or swap of two parts would remove most crossings without breaking the datasheet checklist rows in detail/placement_<block>.md.
 6. Layer budget: with In1 = GND plane (must stay solid under U200 and the USB pair) and In2 carrying the FC's power pours inside the Rev2 outline, how many signal layers do the wing and strip effectively have (F.Cu, B.Cu, In2 where free)? Is a 3V3_EMU pour on In2 across the wing/strip (brief L6 says In2 gets no new FC-power pours — 3V3_EMU is a NEW net) the right call? Give a routing forecast.

Return the schema. Skip anything the PM already decided (COMMON).`

const PRINCIPAL_B = `${COMMON}

ROLE: Principal layout engineer — MANUFACTURABILITY and PROBLEMATIC-PLACEMENT half. You will send this board to JLCPCB; you are reviewing the placement so that it is cheap and safe to build and nothing has to be reworked after assembly. Write your notes to ${OUT}/principal_manufacturability.md (mkdir -p ${OUT}); finding ids PLM-01…. Work through ALL of sections B and C below and report what you measured, not what you assume; leave routing_forecast empty.

B. MANUFACTURABILITY (fetch https://jlcpcb.com/capabilities/pcb-assembly-capabilities and https://jlcpcb.com/capabilities/pcb-capabilities; quote the figures you use):
 1. Component-to-board-edge: facts.md lists TP200/TP201 at 0.50 mm, C200 0.61, U202 0.72, C201 0.73, J701 1.23 mm from the edge. Compare with JLC's SMT edge clearance / panel rail rule; recommend moves.
 2. Component spacing: JLC's minimum spacing between components vs the tight pairs in facts.md (U315–C315 0.01 mm, U200–C210/212/213 0.035, L200–C217 0.05, C220–U201 0.055, U200–C216/206/209/207 0.055, U202–C200 0.22 …). Which of these are genuinely below the assembler's limit (pick-and-place nozzle, reflow bridging, rework), not just below a routing-room preference?
 3. Both-sides assembly: the 3 bottom-side new parts — any extra cost or process class beyond what the FC's 137 bottom parts already trigger? Any bottom-side new part under a top-side connector (standoff/clash)?
 4. Extended-part / feeder count: from supply_chain_report.md, how many Extended parts and distinct reels does the new area add; any cheap consolidation (same value, different footprint; 88 distinct values across 218 parts)?
 5. Thermal pads: U200, U511 (1.5 A charger), Q510, Q500/Q501 (3 A replica FETs), L510 — is there room for the thermal-via arrays the datasheets ask for, without vias landing under neighbouring caps?
 6. Known JLC rotation corrections in the repo's CLAUDE.md (Hirose DF11 +180, DF11CZ +180, L_pol_2016 +180, USB-C HRO 0) — which new footprints fall under them; any new footprint family whose first-order rotation must be checked (MSK12C02, Phoenix MKDS, tactile switches, DFN2020, QFN-60).
 7. Fiducials: the FC has none; does the new area need two (JLC guidance) and where would they go?
 8. Mounting: M3 screw head / standoff (~6 mm diameter) clearance around H1/H2/H10–H12 (facts: 0 parts within 3.5 mm — confirm with the head diameter you find), and any tall part that stops the board sitting flat on standoffs on the bottom side.
 9. USB-C receptacle edge offset: measure J701 and J510 (front of the receptacle body vs the board edge) against the FC's own J12 (same HRO TYPE-C-31-M-12 part, validated on the flying board) and the connector drawing's recommended edge offset; a plug overmold that bottoms on the board edge before the shell seats is a failure.
 10. Screw terminals J400/J401/J500: wire entry direction (rotation) must face outward past the south edge; screws accessible from above; the Phoenix MKDS drawing's wire-entry clearance behind the terminal.

C. PROBLEMATIC PLACEMENTS: anything you would refuse to route as-is: parts inside connector mating envelopes (USB-C plug overmold ≈ 12.5 × 6.5 mm cross-section, body ≥ 10 mm beyond the receptacle face; DF11 / Pico-Lock cable exits into the lane; header shunts ~6 mm tall), test points a probe cannot reach, LEDs/switches you cannot see or operate, polarised parts with inconsistent orientation, 0402s wedged between 1210s, anything within 8 mm of U30 or the U13→RF1 corridor (should be none).

Return the schema. Aim for the findings that change what the assembler will do; skip anything the PM already decided (COMMON).`

const JUNIOR = `${COMMON}

ROLE: Junior developer / bench user. You are the person who will receive this board assembled and use it every day on a desk to run flight software against emulated solar panels, battery and antenna. You are NOT a layout expert — your job is to catch everything that will be awkward, confusing or impossible when the board is actually in your hands, and to say so with measurements. Write your notes to ${OUT}/junior_developer.md (mkdir -p ${OUT}). Fetch the connector drawings you need (Phoenix MKDS 1,5/2-5.08 and 1,5/3-5.08; HRO TYPE-C-31-M-12; JST SH BM03B-SRSS-TB; Molex Pico-Lock 504050-0691; Hirose DF11-12DP; MSK12C02; 2.54 mm headers + standard 6 mm shunts; the tactile switches SW701/SW702 — check their footprint) and a USB-C plug overmold envelope (typical 12.5 × 6.5 mm, ≥ 10 mm long beyond the receptacle face). Then walk through each workflow physically on the board (measure with pcbnew on ${A.board}, look at the renders, make close-ups):

 1. Setup: bench PSU into J500 (3-pin screw terminal), solar simulator into J400/J401 (2-pin screw terminals), USB-C into J701 (emulator MCU) and J510 (charger test), a laptop USB-C into the FC's own J12 and an SWD probe into the FC's J22 and the emulator's J702, a bench header ribbon on J703. Can every one of these be plugged in AT THE SAME TIME? Measure plug-to-plug and plug-to-part clearances (J701 vs J702/J703/SW701/SW702/TP701; J510 vs the 1210 caps / L510 / H11; J12 and J22 vs the lane and the face column parts; the three screw terminals vs each other and vs TP500–TP505 / F400 / D400).
 2. Wrong-plug risk: J500 (bench battery/PSU, up to 3 A) sits next to J400/J401 (solar injection) — same connector family, same pitch. What stops a student from swapping them, and is there room for the L8 legend + polarity marks (text ≥ 1.2 mm high needs ≥ 1.0 mm per character) beside each terminal and each jumper JP400/401/500/510/600–607? Where exactly would the legend go, and is that space free of pads?
 3. Bench modes: the six shunt headers JP602–JP607 in a row at 2.54 mm pitch plus JP600/JP601 and SW600 (pyro SAFE) — can you move shunts with fingers or pliers with the neighbouring parts (D600–D602, R600–R602, TP600–603, LED600, the battery replica below)? Is the SAFE switch operable and LED600 visible while cables are plugged in? Is it obvious which header parallels which FC connector (they are meant to sit directly under J30/J10/J29/J7/J8/J15)?
 4. Probing: with a 2.5 mm scope-probe tip and a hook clip, which of TP200–TP203, TP300–TP306, TP400–TP402, TP500–TP505, TP510–TP512, TP600–TP603, TP701 can you reach without touching a neighbouring pad or a connector body? Which important nets have NO test point (e.g. the emulator's 1V1/3V3 rails, VBAT_BENCH, the shared I2C buses)?
 5. Handling and mounting: five M3 holes (H1/H2 on the FC, H10–H12 on the new corners) — will the board sit flat on standoffs with the bottom-side parts (U310/U312/U314 + the FC's bottom side)? Where do you hold the board without touching exposed 3 A terminals or the 0402 field? Is anything fragile (crystal Y200, DFN Q510) at a corner where it gets bumped?
 6. Firmware bring-up: SW701 (BOOTSEL?) / SW702 (RESET?) reachable while J701 is plugged (a plug overmold covers ~12 mm)? J702 SWD and J703 pin-1 orientation consistent with the FC's J22/J16? Are the emulator's USB-C and the FC's USB-C distinguishable at a glance (they will be labelled later — is there room)?
 7. FC's own edges: with the wing and strip in place, can you still reach the FC's left/top-edge connectors (J21/J24 heater/deploy, J23, J4 WDT jumper, J3/J5, RF1 MMCX, the antenna modules U13/U30)? Anything on the strip's left end (pyro block at x 150–187) that blocks the FC's bottom-left area?
 8. Anything else that would make you send it back: components you cannot identify by eye, identical-looking headers with different voltages side by side, a slide switch that can be knocked, test points on the board edge that a bench clamp covers.

Return the schema with your findings (ids JD-01…); leave routing_forecast empty. Measured numbers in every finding; say what you fetched.`

const verifyPrompt = (batch, block) => `${COMMON}

ROLE: Independent skeptic for the block/area "${block}". Two reviewers (a principal layout engineer and a junior developer / bench user) reported the findings below. Your job is to REFUTE each one: re-measure it yourself with pcbnew on ${A.board}, fetch the drawing / datasheet / JLCPCB capability page it relies on, and check it against the owner's rules and the PM decisions in COMMON. For each finding return: confirmed (evidence holds, severity right), downgraded / upgraded (evidence holds, severity wrong — give the right one), or refuted (the measurement is wrong, the rule is misread, the PM already decided it, or it belongs to a later stage without any placement consequence). Default to refuted if you cannot reproduce the evidence. Improve the recommendation where you can (a concrete move that also keeps the block's datasheet checklist rows in ${A.docs}/detail/placement_<block>.md). Write your notes to ${OUT}/verify_${block.replace(/[^A-Za-z0-9_]/g, '_')}_${batch.tag}.md.

FINDINGS TO VERIFY:
${JSON.stringify(batch.items, null, 1)}

Return the schema (one verdict per finding id).`

const chairPrompt = (reviews, verified) => `${COMMON}

ROLE: Panel chair (the one Opus call after the reviewers). Inputs: the reviewers' structured results and notes (${OUT}/principal_routability.md, ${OUT}/principal_manufacturability.md, ${OUT}/junior_developer.md) and the skeptics' verdicts for every finding — all of it is in this prompt and in those three files; do NOT re-read ${A.floorplanMd} or facts.md in full (use them only to look up a specific number). Write the report in sections of ≤ 60 lines per Write/Edit call (first the summary, then append the sections) so nothing is lost if you are interrupted; keep the whole report under ~400 lines. Reviewer results: ${JSON.stringify(reviews.map(r => ({ role: r.role, scope: r.scope_checked, findings: r.findings.length, routing_forecast: r.routing_forecast })))}. Verified findings (finding + verdict): ${JSON.stringify(verified, null, 0)}.

Do: (1) merge and dedupe (the two personas will overlap on connectors, test points, legends); keep the skeptic's severity unless you have a measured reason; drop refuted items into a short "refuted" list with the reason; (2) rank: blockers (must change before routing), majors (should change before routing), minors (later stage), notes; for every blocker/major write the concrete fix (ref → x,y,rot / side, or a block-level instruction) and which block owns it; (3) write ${OUT}/floorplan_v2_panel_review.md for the owner: a one-page summary at the top (verdict, counts, the blockers and majors in one table each with refs / evidence / fix / owner block), then a manufacturability scorecard against the JLCPCB figures the reviewers fetched (edge clearance, spacing, both-sides, Extended count, thermal vias, rotations, fiducials, USB-C edge offset, screw-terminal orientation), a routing-complexity forecast (from the principal's §A: escape, corridors, stubs, crossing hot-spots, layer budget, the 3V3_EMU pour question) with the nets/corridors that will need hand routing, a bench-usability section (from the junior developer: what can be plugged simultaneously, wrong-plug risk, jumper/probe access, legend space), then every finding in full (id, severity, refs, evidence, skeptic verdict, fix), then the refuted list; (4) write ${OUT}/panel_fix_plan.json: { "recommendation": "route-now" | "fix-then-route" | "rework-blocks", "blockNotes": { "<block>": "<PM-style instruction for that block's fixer: what to move where and which checklist rows must still hold>" }, "floorplan_level": [ "<changes outside any block: lane, stitching, outline, fiducials, netclass/pour decisions for routing>" ], "routing_instructions": [ "<instructions for the routing stage: corridors, pours, hand-routed nets, layer use>" ], "deferred": [ "<minor/note items with their stage>" ] } — blockNotes must be directly usable as the "blockNotes" argument of .claude/workflows/flatsat-detailed-placement.js round-3 mode (one entry per block that needs a fix; empty object if none). Be exact and terse; numbers over adjectives. Return the schema.`

// ---------------------------------------------------------------------------
const blocksJson = A.blocks || {}
const blockOf = (refs) => {
  for (const r of String(refs).split(/[,\s]+/).filter(Boolean)) {
    for (const [name, b] of Object.entries(blocksJson)) if (b.refs.includes(r)) return name
  }
  return 'board'
}

// Prior results (args.prior = {junior_developer: <FINDINGS result>, verdicts: [<VERDICT>...]}) are reused verbatim so a
// relaunch after an infrastructure stall does not repeat finished work.
const PRIOR = A.prior || {}
const priorVerdicts = Object.fromEntries((PRIOR.verdicts || []).map(v => [v.id, v]))

// verification: batches of ≤ 8 findings grouped by block, run at most `VERIFY_PAR` at a time (the first run stalled with 6+ concurrent agents)
const VERIFY_PAR = A.verifyParallel || 2
async function verifyAll(role, findings) {
  const todo = findings.filter(f => !priorVerdicts[f.id])
  const byBlock = {}
  for (const f of todo) { const b = f.block && f.block !== '' ? f.block : blockOf(f.refs); (byBlock[b] = byBlock[b] || []).push(f) }
  const batches = []
  for (const [b, items] of Object.entries(byBlock)) for (let i = 0; i < items.length; i += 8) batches.push({ block: b, tag: `${role}_${i / 8 + 1}`, items: items.slice(i, i + 8) })
  const verdicts = []
  for (let i = 0; i < batches.length; i += VERIFY_PAR) {
    const slice = batches.slice(i, i + VERIFY_PAR)
    const got = await parallel(slice.map(bt => () =>
      agent(verifyPrompt(bt, bt.block), { label: `verify:${bt.block}:${bt.tag}`, phase: 'Verify', model: M.verify, effort: 'medium', schema: VERDICTS })
        .then(v => (v ? v.verdicts : []))))
    verdicts.push(...got.filter(Boolean).flat())
  }
  const vmap = Object.assign({}, priorVerdicts, Object.fromEntries(verdicts.map(v => [v.id, v])))
  return findings.map(f => ({ ...f, reviewer: role, verdict: vmap[f.id] || { verdict: 'unverified', severity_after: f.severity, reason: 'no verdict returned', evidence: '', recommendation_after: f.recommendation } }))
}

phase('Review')
log(`panel: principal layout engineer ×2 (${M.principal}) + junior developer (${PRIOR.junior_developer ? 'reused from the previous run' : M.junior}) reviewing floorplan v2.2`)
const reviewers = [
  { role: 'principal_routability', prompt: PRINCIPAL_A, model: M.principal },
  { role: 'principal_manufacturability', prompt: PRINCIPAL_B, model: M.principal },
  { role: 'junior_developer', prompt: JUNIOR, model: M.junior, prior: PRIOR.junior_developer },
]
const results = await pipeline(
  reviewers,
  (r) => (r.prior ? Promise.resolve(r.prior) : agent(r.prompt, { label: `review:${r.role}`, phase: 'Review', model: r.model, effort: 'high', schema: FINDINGS })),
  async (res, r) => {
    if (!res) { log(`${r.role}: no result`); return null }
    log(`${r.role}: ${res.findings.length} findings (${res.findings.filter(f => f.severity === 'blocker').length} blockers, ${res.findings.filter(f => f.severity === 'major').length} majors)`)
    const verified = await verifyAll(r.role, res.findings)
    const kept = verified.filter(v => v.verdict.verdict !== 'refuted')
    log(`${r.role}: verified — ${kept.length} kept (${kept.filter(v => v.verdict.severity_after === 'blocker').length} blockers, ${kept.filter(v => v.verdict.severity_after === 'major').length} majors), ${verified.length - kept.length} refuted`)
    return { role: r.role, scope_checked: res.scope_checked, routing_forecast: res.routing_forecast, findings: res.findings, verified }
  },
)

const ok = results.filter(Boolean)
const allVerified = ok.flatMap(r => r.verified)
phase('Chair')
const chair = await agent(chairPrompt(ok, allVerified), { label: 'chair:panel', phase: 'Chair', model: M.chair, effort: 'medium', schema: CHAIR })

return {
  stage: 'floorplan-panel',
  reviewers: ok.map(r => ({ role: r.role, findings: r.findings.length, kept: r.verified.filter(v => v.verdict.verdict !== 'refuted').length })),
  chair,
}
