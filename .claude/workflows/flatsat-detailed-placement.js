export const meta = {
  name: 'flatsat-detailed-placement',
  description: 'FlatSat Phase-2 stage 2b: per-block detailed placement of the support passives per manufacturer layout guidelines (Sonnet placers → Sonnet datasheet auditors → fix rounds) → one Opus integrator that merges, re-gates, re-renders and writes the v2 owner review package. Stops for owner review; no routing.',
  whenToUse: 'After the block-level floorplan is settled but the owner wants every block\'s passives placed to the datasheet layout guidelines. args: {project, board, docs, scratch, brief, floorplanJson, previewBoard, blocksJson, blocks:{name:{refs,sheets,envelope_mm,fixed_anchors}}, kicadPy, kicad, heritageSnap, refBoard, drcBaseline, models?:{place,audit,fix,integrate}, maxAuditRounds?:2, context}',
  phases: [
    { title: 'Place', detail: 'one Sonnet placer per block: datasheet checklist → placement → measured compliance' },
    { title: 'Audit', detail: 'independent Sonnet datasheet auditor per block, refute-style' },
    { title: 'Fix', detail: 'placer fixes the audited violations, re-audited' },
    { title: 'Integrate', detail: 'Opus merges all blocks, re-runs every gate, re-renders, writes floorplan_v2.md for the owner', model: 'opus' },
  ],
}

const A = args
const B = A.blocks
const M = Object.assign({ place: 'sonnet', audit: 'sonnet', fix: 'sonnet', integrate: 'opus' }, A.models || {})
const MAXR = A.maxAuditRounds || 2
const DETAIL = `${A.docs}/detail`

const COMMON = `PROJECT CONTEXT: ${A.context}

HARD RULES (repo CLAUDE.md + owner): never write ${A.board} (the live board) or anything under FC_V5e_Production_Rev2/; never open the KiCad GUI; no git commits. Work only on copies inside your own scratch directory ${A.scratch}/detail_<block>/ (mkdir -p it). KiCad python = ${A.kicadPy} (module pcbnew; pipe its stderr through grep -vE 'stdpbase|pcb_track|memory leak|Debug:'); kicad-cli = ${A.kicad}. Run tools from ${A.project} (cd there) so relative paths in their docstrings work. Read tools/pcb/README.md §7 and each tool's docstring before using it.

THE BOARD: ${A.previewBoard} is the v1 floorplan already applied (outline + pours + 218 placements), unrouted, with its .kicad_pro/.kicad_dru/.kicad_prl next to it — copy all four to your scratch dir and work on that copy. The floorplan of record is ${A.floorplanJson} (keys: placements {ref:{x,y,rot,side}}, plus outline/pours/holes/stitching/lanes/keepouts that you must not change). The owner reviewed it and ruled (brief §12): the block-level plan stands (outline_L1 unmodified, block order, edge connectors, 12.6 mm L3 lane at x 231.4–244 in front of the FC face/USB/SWD connectors, mounting holes as they are), but the SUPPORT PASSIVES ARE NOT LAID OUT WELL — every block's passives must follow the manufacturer's layout guidelines and reference designs. Ruling F3: passives stay on F.Cu; U310/U312/U314 stay on B.Cu and their decoupling caps go on F.Cu directly opposite the IC (via pair planned), as close as the guideline allows.

PLACEMENT CONSTRAINTS FOR EVERY BLOCK: (a) every part of the block stays inside the block envelope (mm, [x0,y0,x1,y1]); (b) fixed anchors (connectors, headers, switches listed per block) do not move or rotate; (c) the block's anchor ICs may move at most 3 mm from their v1 position (the attachment reach to the FC pads must not get worse by more than 3 mm for any shared net — brief L11 / floorplan.md §5 is the reference table); (d) no courtyard overlap with any part of any block (real courtyard polygons; tools/pcb/apply_placement.py now checks this) and nothing outside the outline; (e) the 12.6 mm lane stays free of parts taller than 2 mm; (f) heritage frozen (tools/pcb/heritage.py check … --allow-zone-growth --allow-edge → 0) and no new part inside the Rev2 outline; (g) rotations are yours to choose — orient parts so the guideline loops are short and pins face the pins they connect to; test points go where a probe can reach (block edges), LEDs/switches where a hand can reach; (h) leave routing room: 0.5 mm courtyard-to-courtyard where the guideline does not want parts touching, and do not pack the whole block into a corner just because you can.

HOW TO PLACE AND PROVE IT (the canonical path other stages use): write your block's placements as JSON {ref:{x,y,rot,side}} for YOUR refs only, merge them into a copy of ${A.floorplanJson} (same keys, only your refs' entries replaced) and rebuild the board from scratch to prove it: cp ${A.board} + its .kicad_pro to your scratch dir; ${A.kicadPy} tools/pcb/outline.py --board <copy> --out <o.kicad_pcb> --spec <merged.json>; ${A.kicadPy} tools/pcb/apply_placement.py --board <o.kicad_pcb> --placement <merged.json> --out <placed.kicad_pcb> (prints applied/refused/outside/overlap lines and exits 0 only when clean); ${A.kicadPy} tools/pcb/heritage.py check ${A.heritageSnap} <placed> --allow-zone-growth --allow-edge; ${A.kicadPy} tools/pcb/attachment_check.py ${A.heritageSnap} <placed>. For DRC put the board in a directory with its .kicad_pro/.kicad_dru siblings (else kicad-cli uses factory rules — floorplan.md §2 explains). Measure every guideline criterion with pcbnew on the placed board (pad-centre / pad-edge distances between the specific pins the rule names, same-layer or not, loop perimeter for switching loops) — numbers, not adjectives.

MANUFACTURER GUIDELINES: get the layout section of the real datasheet / reference design / EVM layout for every IC in the block. Sources: the symbol's Datasheet field in the sheet (.kicad_sch), the Phase-1 sheet doc (${A.docs}/../2026-09-14_phase1_schematic/sheet_<sheet>.md), and these starting points — verify each: RP2350 datasheet https://datasheets.raspberrypi.com/rp2350/rp2350-datasheet.pdf and "Hardware design with RP2350" https://datasheets.raspberrypi.com/rp2350/hardware-design-with-rp2350.pdf (decoupling per supply pin group, 1V1 core caps, crystal + load caps, QSPI flash placement, USB series resistors, the RP2350-E9 pull-down erratum); BQ25886 https://www.ti.com/lit/ds/symlink/bq25886.pdf ("Layout Guidelines" + EVM); TCA4311A https://www.ti.com/lit/ds/symlink/tca4311a.pdf; R5460N (Nisshinbo/Ricoh) battery-protection IC datasheet + its standard application circuit (VC series R < 1 kΩ ruling, sense/FET placement); TMP112 https://www.ti.com/lit/ds/symlink/tmp112.pdf; VEML6031 (Vishay); DRV2605L https://www.ti.com/lit/ds/symlink/drv2605l.pdf; USB-C receptacles/ESD per the ESD part's datasheet. Load WebFetch/WebSearch through ToolSearch. If a PDF cannot be read, find the HTML datasheet or an app note; if nothing is reachable, apply the standard guideline for that circuit type (decoupling cap on the pin's side within 1–2 mm with the shortest ground return; buck: input cap across VBUS/PGND adjacent to the pins, inductor adjacent to SW, output cap adjacent to the inductor, bootstrap cap adjacent to BTST/SW, feedback divider at the FB pin away from SW; crystal: ≤ 5 mm from XIN/XOUT, load caps adjacent and symmetric, nothing noisy under it; QSPI flash close to the MCU on the same side; USB series R within 5 mm of the pins; ESD diode at the connector before anything else; gate resistors at the FET gate; sense resistors with Kelvin-able pads) AND SAY that you fell back and why. Every checklist row cites its source (document + section/figure) and states a measurable criterion.`

const PLACE_SCHEMA = {
  type: 'object',
  properties: {
    block: { type: 'string' },
    json_path: { type: 'string', description: 'placement_<block>.json with this block\'s refs only' },
    md_path: { type: 'string', description: 'placement_<block>.md: checklist table (rule, source, criterion, measured, pass/fail), rationale, deviations, anchor moves, reach effect' },
    board_path: { type: 'string', description: 'the rebuilt, placed scratch board with the merged placement applied' },
    rules_checked: { type: 'integer' },
    rules_failed: { type: 'integer' },
    gates: { type: 'string', description: 'one line: heritage/attachment/overlaps/outside results as printed' },
    notes: { type: 'string' },
  },
  required: ['block', 'json_path', 'md_path', 'board_path', 'rules_checked', 'rules_failed', 'gates', 'notes'],
}

const AUDIT_SCHEMA = {
  type: 'object',
  properties: {
    block: { type: 'string' },
    verdict: { type: 'string', enum: ['pass', 'fail'] },
    violations: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          refs: { type: 'string' }, rule: { type: 'string' }, source: { type: 'string' },
          measured: { type: 'string' }, required: { type: 'string' }, severity: { type: 'string', enum: ['must-fix', 'should-fix', 'note'] },
        },
        required: ['refs', 'rule', 'source', 'measured', 'required', 'severity'],
      },
    },
    rules_audited: { type: 'integer' },
    notes: { type: 'string' },
  },
  required: ['block', 'verdict', 'violations', 'rules_audited', 'notes'],
}

const INTEG_SCHEMA = {
  type: 'object',
  properties: {
    json_path: { type: 'string' }, md_path: { type: 'string' }, board_path: { type: 'string' },
    renders: { type: 'array', items: { type: 'string' } },
    gates: { type: 'string', description: 'heritage / attachment / overlaps / outside / lane / DRC parity+courtyard lines as printed' },
    reach_max_mm: { type: 'number' }, reach_worsened: { type: 'string', description: 'nets whose FC-pad→new-pad reach got worse by >3 mm vs floorplan.md §5, or "none"' },
    blocks_summary: { type: 'string', description: 'per block: rules checked / passed / deviations kept, one line each' },
    open_questions: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['json_path', 'md_path', 'board_path', 'renders', 'gates', 'reach_max_mm', 'reach_worsened', 'blocks_summary', 'open_questions', 'summary'],
}

const blockDesc = (name, b) => `BLOCK "${name}": refs ${b.refs.join(', ')} (${b.refs.length} parts) from sheet(s) ${b.sheets.join(', ')} (${A.project}/<sheet>.kicad_sch); envelope_mm ${JSON.stringify(b.envelope_mm)}; fixed anchors ${b.fixed_anchors.length ? b.fixed_anchors.join(', ') : 'none'}. v1 positions of every ref are in ${A.floorplanJson}; the v1 rationale for this block is in ${A.docs}/floorplan.md (§1 block map, §3, §5).`

const placePrompt = (name, b) => `${COMMON}

ROLE: Detailed-placement owner for one block. ${blockDesc(name, b)}
Do, in order: (1) read the sheet(s) and the Phase-1 sheet doc; list every IC in the block with its support passives and what each one does (decoupling for which pin, bootstrap, feedback, pull-up on which bus, series termination, ESD, sense, gate); (2) build the guideline checklist from the manufacturer documents (see MANUFACTURER GUIDELINES) — one row per rule with source and a measurable criterion; (3) place the block on your scratch copy of the preview board with pcbnew scripting (SetPosition / SetOrientationDegrees / Flip only where the rules allow; F.Cu for passives per ruling F3) so every checklist row is met, within the PLACEMENT CONSTRAINTS; (4) export your refs' placements to ${DETAIL}/placement_${name}.json (mkdir -p ${DETAIL}; format {ref:{x,y,rot,side}}), merge into a copy of the floorplan and rebuild + gate the board the canonical way (HOW TO PLACE AND PROVE IT) — iterate until apply_placement exits 0, heritage 0, attachment 0; (5) measure every checklist row on the rebuilt board and write ${DETAIL}/placement_${name}.md: the checklist table (rule | source | criterion | measured | pass/fail), the placement rationale per IC (why each passive is where it is), any rule you could not meet and why, any anchor IC moved (from → to, why), the attachment-reach effect (distance from each of this block's attachment pads to its FC pad before/after — measure with pcbnew), and the exact commands you ran. Return the schema. rules_failed must be 0 unless a deviation is genuinely forced by the envelope/anchors — then explain it in notes.`

const auditPrompt = (name, b, placed) => `${COMMON}

ROLE: Independent datasheet auditor for one block — your job is to REFUTE the placement, not to confirm it. ${blockDesc(name, b)}
The placer delivered ${placed.json_path} (placements), ${placed.md_path} (its checklist and claims) and the placed board ${placed.board_path}. Do NOT trust its checklist: build your own from the manufacturer documents (fetch them yourself; see MANUFACTURER GUIDELINES), including rules the placer may have omitted (ground return path of each decoupling cap, loop area of the switching loops, crystal isolation, ESD-first ordering at connectors, sense-resistor Kelvin access, thermal/keep-out around the inductor, anything the datasheet's layout section or reference layout shows). Then measure every rule yourself with pcbnew on ${placed.board_path} (numbers). Also re-run the gates on that board (apply_placement.py --check-only style: overlaps/outside via the canonical rebuild if needed, heritage.py check, attachment_check.py) and check the PLACEMENT CONSTRAINTS (envelope, fixed anchors unmoved vs ${A.floorplanJson}, anchor ICs ≤ 3 mm, lane clear, F.Cu ruling). Report every violation with refs, rule, source, measured vs required, severity (must-fix = datasheet rule or constraint broken; should-fix = reference-design practice not followed; note = judgement call). verdict = fail if any must-fix or should-fix remains. Return the schema; write nothing into ${DETAIL} except ${DETAIL}/audit_${name}.md with your full findings.`

// PM rulings issued after reading the round-2 audits (2026-09-14). Appended only to fix rounds >= 2 so the
// cached round-1 prompts stay byte-identical on resume.
const PM_ROUND2 = `
PM RULINGS FOR THIS ROUND (they override the generic constraints where they conflict):
- Constraint (c) "anchor ICs" means the block's main IC(s) only (U200, U511, U500, U315, the seven TCA4311As, U301–U303, Q701–Q703 as a group). Inductors, pass FETs, ideal-diode controllers, caps, resistors, diodes, test points are support parts and may move anywhere inside the envelope — the v2 moves of L200, L510, Q510, U510 are accepted.
- A fixed anchor whose courtyard pokes past the block envelope (J400/J401/J701/SW703 — the envelope was computed from part centres) is NOT a violation. Do not move it; say so in the .md.
- Courtyard gaps below 0.5 mm are ACCEPTED where the near part is a decoupling / bootstrap / input / output capacitor sitting against the pin it serves (that is what ruling F1 asked for). Record those as "accepted trade (PM)", not as deviations. Everywhere else restore >= 0.50 mm measured on KiCad's real courtyard polygons (the auditor's convention).
- Every decoupling capacitor serves a named pin or pin group and must sit adjacent to it (RP2350: per the hardware-design guide each IOVDD / DVDD / USB / ADC_AVDD / VREG pin group gets its own cap at that group; a cap 6–16 mm away decouples nothing). If a cap truly cannot reach its pin, name the pin, the distance, and why — do not leave a "fallback target missed" row without that.
- face_column: cite TCA4311A SCPS226C §11.1 Layout Guidelines / §11.2 Figure 16 and the VCC pin-table sentence ("bypass capacitor of at least 0.01 µF close to this pin") as the source for the decoupling row (fetch it; quote it); fix the 17 pairs measured at 0.490 mm to >= 0.50 mm.
- bench_io_cable: evaluate C701 in the column between J701 and J702 (x ≈ 280.3–283.8) as close to J701's VBUS pins as the courtyards allow and keep the better of the two positions with numbers; re-tune R703/R704 so the pad-to-pad legs to U200's D+/D− pins match within 0.15 mm while staying <= 3.6 mm.
- charger_bq25886: correct every checklist number the auditor found wrong (measure again); the tight cap pairs of the SW/input/bootstrap loop are accepted trades.
- vsolar_injection: the only open item is the anchor/envelope artefact above — confirm the block is otherwise clean and return.`

const fixPrompt = (name, b, placed, audit, round) => `${COMMON}
${round >= 2 ? PM_ROUND2 : ''}
ROLE: Detailed-placement owner for one block, fix round ${round}. ${blockDesc(name, b)}
Your previous delivery: ${placed.json_path}, ${placed.md_path}, board ${placed.board_path}. The independent auditor (${DETAIL}/audit_${name}.md) found these violations: ${JSON.stringify(audit.violations)}. Fix every must-fix and should-fix by moving/rotating parts within the PLACEMENT CONSTRAINTS (if one is impossible without breaking a constraint, say exactly why in notes and in the .md — do not silently ignore it); re-run the canonical rebuild + gates; re-measure the whole checklist (yours plus the auditor's rules — add the auditor's rules to your table); overwrite ${DETAIL}/placement_${name}.json and .md (add a "fix round ${round}" section listing each violation → what changed → new measurement). Return the schema.`

const integratePrompt = (results) => `${COMMON}

ROLE: Integrator (the one Opus call of this stage). Inputs — one per block: ${JSON.stringify(results.map(r => ({ block: r.name, json: r.placed.json_path, md: r.placed.md_path, audit_verdict: r.audit ? r.audit.verdict : 'n/a', open_violations: r.audit ? r.audit.violations.filter(v => v.severity !== 'note').length : -1, rules_checked: r.placed.rules_checked, rules_failed: r.placed.rules_failed })))}.
Do: (1) merge every placement_<block>.json into a copy of ${A.floorplanJson} → ${A.docs}/floorplan_v2.json (every other key unchanged; record "based_on" and the block list); (2) rebuild from the live board the canonical way (outline.py + apply_placement.py) → ${A.docs}/floorplan_v2_preview.kicad_pcb with .kicad_pro/.kicad_dru/.kicad_prl next to it (copy the ones next to ${A.previewBoard}; set the page to A3 the way the v1 preview did); (3) run every gate and paste the output lines: apply_placement (0 overlaps, 0 outside, exit 0), ${A.kicadPy} tools/pcb/heritage.py check ${A.heritageSnap} <board> --allow-zone-growth --allow-edge --refill --core-inset 12 --ref-board ${A.refBoard} (0 violations), attachment_check (0), lane check (no part > 2 mm tall inside x 231.4–244 in front of J1/J2/J6/J9/J11/J13/J16/J12/J22 — measure), the RF keep-outs (brief §2), kicad-cli DRC with the sibling files (parity exactly the 11 §6 baseline items, courtyards_overlap ≤ 1, everything else unconnected only — list any other error class with a disposition); (4) re-measure the L11 attachment reach for every shared net (FC allowed pad → nearest new pad on that net; the method and the v1 table are in ${A.docs}/floorplan.md §5) and diff against v1: report max/median/sum and every net that got worse by > 3 mm; (5) resolve block-boundary conflicts if two blocks moved parts toward each other (overlaps or < 0.5 mm courtyard gaps across a boundary): adjust the minimum number of passives, never an anchor, re-gate, and record it; (6) renders into ${A.docs}/img/: floorplan_v2_top.png / floorplan_v2_bottom.png (kicad-cli pcb render --side top/bottom, same settings as v1), the fab-style PDFs via tools/pcb/render.sh with the v2 prefix, and one close-up PNG per block if kicad-cli render's --zoom/--pan lets you frame it (try; skip with a note if not); (6b) STITCHING (PM authorises editing the "stitching" key for this one purpose): every new stitching via must land on GND — after the rebuild check every new via's net with pcbnew; any stitching point within 1.2 mm of a non-GND pad (the v2 integration found three: 3V3_EMU at (293.40, 98.88) and (293.40, 107.66), MID_BENCH at (198.90, 169.10)) is moved >= 1.5 mm along its perimeter / ring line to a spot >= 1.5 mm from any non-GND pad and >= 3 mm from the board edge, then rebuild and re-gate; list every moved point. (6c) If this is a re-integration (a v2 package already exists), OVERWRITE floorplan_v2.json / floorplan_v2.md / floorplan_v2_preview.* / img/floorplan_v2_* in place (the build stage points at those names) and put a "changes since the previous integration" section right under the owner summary. Fixed anchors whose courtyards poke past a block envelope (J400/J401/J701/SW703) are not findings. Courtyard gaps < 0.5 mm for a cap against the pin it serves are PM-accepted trades — list them as such, not as open questions. Only put a question to the owner if a decision genuinely needs them; PM decisions go in a "decisions taken" list the owner can override. (7) write ${A.docs}/floorplan_v2.md for the owner: at the top a one-page owner summary — what changed since v1 (per block: parts moved, the guideline rules checked/passed, deviations kept and why, anchor ICs moved), the gate table, the attachment-reach table vs v1, the render list, and the questions the owner must answer; then per-block sections that quote each block's checklist table (from the placement_<block>.md files) and the auditor's verdict; then evidence (every command + output) and "reproducing this". Be exact and terse; numbers over adjectives. Return the schema.`

// ---------------------------------------------------------------------------
// Round-3 mode: args.round3 = {stateJson, fixBlocks:[...], passedBlocks:[...]} — resume a finished run from its
// last audits without replaying the place/audit stages (the Workflow prefix cache does not survive pipeline
// reordering, so a plain resume re-runs everything). stateJson holds, per block, the last placement result and
// the last audit (written by the PM from the journal). Blocks in fixBlocks get fix → audit (→ fix → audit);
// passedBlocks go straight to the integrator unchanged.
if (A.round3) {
  const R = A.round3
  const fixPrompt3 = (name, b, round) => `${COMMON}
${PM_ROUND2}
${(R.blockNotes || {})[name] ? 'PM NOTES FOR THIS BLOCK: ' + R.blockNotes[name] : ''}
ROLE: Detailed-placement owner for one block, fix round ${round} (resumed). ${blockDesc(name, b)}
Your previous delivery is ${DETAIL}/placement_${name}.json + ${DETAIL}/placement_${name}.md; the placed board path, your previous checklist counts and the LAST AUDIT (verdict + violations) are in ${R.stateJson} under the key "${name}" — read that file first and treat its "audit.violations" as the authoritative finding list (the ${DETAIL}/audit_${name}.md file may be stale or partially overwritten). Fix every must-fix and should-fix by moving/rotating parts within the PLACEMENT CONSTRAINTS as amended by the PM RULINGS above (if one is impossible, say exactly why in notes and in the .md — do not silently ignore it); re-run the canonical rebuild + gates; re-measure the whole checklist (yours plus the auditor's rules — add the auditor's rules to your table); overwrite ${DETAIL}/placement_${name}.json and .md (add a "fix round ${round}" section listing each violation → what changed → new measurement, and list every PM-accepted trade as such). Return the schema.`
  const fixItems = R.fixBlocks.map(n => [n, B[n]])
  log(`round 3: fixing ${R.fixBlocks.join(', ')}; carrying ${R.passedBlocks.join(', ')} unchanged`)
  const fixed = await pipeline(
    fixItems,
    ([name, b]) => agent(fixPrompt3(name, b, R.startRound || 2), { label: `fix:${name}:${R.startRound || 2}`, phase: 'Fix', model: (R.fixModelByBlock || {})[name] || M.fix, effort: 'high', schema: PLACE_SCHEMA }),
    async (cur, [name, b]) => {
      if (!cur) { log(`${name}: fixer returned nothing`); return null }
      const r0 = (R.startRound || 2) + 1
      const fixModel = (R.fixModelByBlock || {})[name] || M.fix
      let audit = await agent(auditPrompt(name, b, cur), { label: `audit:${name}:${r0}`, phase: 'Audit', model: M.audit, effort: 'high', schema: AUDIT_SCHEMA })
      let open = audit ? audit.violations.filter(v => v.severity !== 'note') : []
      log(`${name}: audit ${r0} → ${audit ? audit.verdict : 'no result'} (${open.length} open)`)
      if (audit && audit.verdict !== 'pass' && open.length) {
        const again = await agent(fixPrompt(name, b, cur, audit, r0) + ((R.blockNotes || {})[name] ? `\nPM NOTES FOR THIS BLOCK: ${R.blockNotes[name]}` : ''), { label: `fix:${name}:${r0}`, phase: 'Fix', model: fixModel, effort: 'high', schema: PLACE_SCHEMA })
        if (again) {
          cur = again
          audit = await agent(auditPrompt(name, b, cur), { label: `audit:${name}:${r0 + 1}`, phase: 'Audit', model: M.audit, effort: 'high', schema: AUDIT_SCHEMA })
          open = audit ? audit.violations.filter(v => v.severity !== 'note') : []
          log(`${name}: audit ${r0 + 1} → ${audit ? audit.verdict : 'no result'} (${open.length} open)`)
        }
      }
      return { name, placed: cur, audit }
    },
  )
  const carried = R.passedBlocks.map(n => ({
    name: n,
    placed: { block: n, json_path: `${DETAIL}/placement_${n}.json`, md_path: `${DETAIL}/placement_${n}.md`, board_path: `(see ${R.stateJson} key ${n})`, rules_checked: -1, rules_failed: 0, gates: 'unchanged since the previous integration', notes: 'passed its audit in the previous run; unchanged' },
    audit: { block: n, verdict: 'pass', violations: [], rules_audited: -1, notes: 'previous run' },
  }))
  const all = [...fixed.filter(Boolean), ...carried]
  log(`round 3 delivered ${fixed.filter(Boolean).length}/${fixItems.length} fixed blocks + ${carried.length} carried; open: ${all.map(r => `${r.name}=${r.audit ? r.audit.violations.filter(v => v.severity !== 'note').length : '?'}`).join(' ')}`)
  phase('Integrate')
  const integ = await agent(integratePrompt(all) + `\nThis is a RE-INTEGRATION after a PM-directed fix round: the previous v2 package exists; overwrite it in place per (6c) and start the owner summary with "changes since the previous integration" (per block: what moved, which audit items closed, which trades the PM accepted). ${R.stateJson} holds each block's previous state for your diff. ${R.integrateNotes || ''}`, { label: `integrate:${R.integrateLabel || 'v2.1'}`, phase: 'Integrate', model: M.integrate, effort: 'high', schema: INTEG_SCHEMA })
  return {
    stage: 'detailed-placement-round3',
    blocks: all.map(r => ({ block: r.name, json: r.placed.json_path, md: r.placed.md_path, rules_checked: r.placed.rules_checked, rules_failed: r.placed.rules_failed, audit_verdict: r.audit ? r.audit.verdict : 'n/a', open_violations: r.audit ? r.audit.violations.filter(v => v.severity !== 'note') : [] })),
    integration: integ,
  }
}

const items = Object.entries(B)
log(`detailed placement: ${items.length} blocks, ${items.reduce((n, [, b]) => n + b.refs.length, 0)} parts; models ${JSON.stringify(M)}; ≤ ${MAXR} audit rounds per block`)

const results = await pipeline(
  items,
  ([name, b]) => agent(placePrompt(name, b), { label: `place:${name}`, phase: 'Place', model: M.place, effort: 'high', schema: PLACE_SCHEMA }),
  async (placed, [name, b]) => {
    if (!placed) { log(`${name}: placer returned nothing — block skipped`); return null }
    let cur = placed
    let audit = null
    for (let r = 1; r <= MAXR; r++) {
      audit = await agent(auditPrompt(name, b, cur), { label: `audit:${name}:${r}`, phase: 'Audit', model: M.audit, effort: 'high', schema: AUDIT_SCHEMA })
      const open = audit ? audit.violations.filter(v => v.severity !== 'note') : []
      log(`${name}: audit ${r} → ${audit ? audit.verdict : 'no result'} (${open.length} open, ${audit ? audit.rules_audited : 0} rules)`)
      if (!audit || audit.verdict === 'pass' || open.length === 0) break
      if (r === MAXR) { log(`${name}: ${open.length} violation(s) still open after ${MAXR} audit rounds — handed to the integrator/owner`); break }
      const fixed = await agent(fixPrompt(name, b, cur, audit, r), { label: `fix:${name}:${r}`, phase: 'Fix', model: M.fix, effort: 'high', schema: PLACE_SCHEMA })
      if (fixed) cur = fixed
    }
    return { name, placed: cur, audit }
  },
)

const ok = results.filter(Boolean)
log(`blocks delivered: ${ok.length}/${items.length}; open violations: ${ok.map(r => `${r.name}=${r.audit ? r.audit.violations.filter(v => v.severity !== 'note').length : '?'}`).join(' ')}`)

phase('Integrate')
const integration = await agent(integratePrompt(ok), { label: 'integrate:v2', phase: 'Integrate', model: M.integrate, effort: 'high', schema: INTEG_SCHEMA })

return {
  stage: 'detailed-placement',
  blocks: ok.map(r => ({ block: r.name, json: r.placed.json_path, md: r.placed.md_path, rules_checked: r.placed.rules_checked, rules_failed: r.placed.rules_failed, audit_verdict: r.audit ? r.audit.verdict : 'n/a', open_violations: r.audit ? r.audit.violations.filter(v => v.severity !== 'note') : [] })),
  integration,
}
