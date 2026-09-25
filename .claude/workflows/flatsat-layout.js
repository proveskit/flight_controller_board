export const meta = {
  name: 'flatsat-layout',
  description: 'FlatSat Phase-2 layout: floorplan judge panel (Sonnet proposals, Opus judge) → outline/ground → autoroute with heritage lock → DRC cleanup rounds → silkscreen/docs/production preview; every hand-back gated by heritage + DRC + parity checks',
  whenToUse: 'Phase-2 stages 2-6 on a synced board, in two runs with an owner review gate between them. args: {stage:"floorplan"|"build", floorplanJson?(build), keepoutJson, project, board, docs, scratch, brief, kicadPy, kicad, heritageSnap, drcBaseline, netlist, models?:{proposal,judge,build,route,fix,fixEscalate,docs}, proposals?:3, maxFixRounds?:3, context}',
  phases: [
    { title: 'Floorplan', detail: 'N Sonnet proposals → Opus judge/synthesis → Sonnet applies + verifies' },
    { title: 'Build', detail: 'Sonnet: outline, GND planes, holes, stitching, netclasses' },
    { title: 'Route', detail: 'Sonnet: Freerouting round trip with heritage lock, power/USB nets per L5' },
    { title: 'Cleanup', detail: 'Sonnet fixers per DRC class; Opus escalation' },
    { title: 'Finish', detail: 'Sonnet: silkscreen, layout report, renders, production preview' },
  ],
}

const A = args
const M = Object.assign({ proposal: 'sonnet', judge: 'opus', build: 'sonnet', route: 'sonnet', fix: 'sonnet', fixEscalate: 'opus', docs: 'sonnet' }, A.models || {})
const EFF = m => (m === 'fable' ? 'xhigh' : m === 'opus' ? 'xhigh' : 'high')
const NPROP = A.proposals ?? 3
const MAX_FIX = A.maxFixRounds ?? 3
const OK_ERR = A.acceptErrors ?? 0   // drc_summary errors that are attributed baseline (accepted unconnected items + pre-existing Rev2 errors)
const OK_UNCONN = A.acceptUnconnected ?? 0   // attributed baseline items the cleanup loop must not chase (e.g. the pre-existing FC U6.1/U6.29 item)
const RUN_STAGE = A.stage || 'floorplan'   // 'floorplan' = propose/judge/apply, then STOP for the owner's review; 'build' = from an approved floorplan.json
const KEEPOUT = A.keepoutJson || `${A.project}/tools/pcb/fc_keepout.json`
const REF_BOARD = A.refBoard || `${A.project}/../FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb`   // read-only reference for the refilled core-fill check
const ATTACH = `${A.kicadPy} tools/pcb/attachment_check.py ${A.heritageSnap} <board>   → 0 violations (brief L11: new copper enters the flight section only as stubs from connector pads / R104,R100,R103 pad 1)`

const COMMON = `
You are doing PCB layout work on the PROVES FlatSat V1 KiCad 10 project. Return raw data only (structured output).

PROJECT DIR:   ${A.project}
LIVE BOARD:    ${A.board}   (never edit in place — copy to your scratch dir, work there, return the path of your result copy)
DOCS DIR:      ${A.docs}
PHASE-2 BRIEF (the spec — read it completely first; §2 board facts, §3 decisions L1–L10, §4 hard rules, §5 tools, §6 pre-existing items, §9 exit criteria): ${A.brief}
PHASE-1 DOCS (what the circuits are): ${A.project}/../docs/flatsat/2026-09-14_phase1_schematic/ (00_pm_brief.md §6 per sheet, sheet_*.md, 02_review_report.md)
SCRATCH: ${A.scratch}  (use your own subdirectory ${A.scratch}/layout_<yourlabel>/)
KiCad python (pcbnew): ${A.kicadPy}   kicad-cli: ${A.kicad}
TOOLS (${A.project}/tools/pcb/, read each docstring; kicad-py = run with KiCad's python): heritage.py (kicad-py) — snapshot/check; drc_summary.py; apply_placement.py (kicad-py); outline.py (kicad-py); netclasses.py; route.sh + README.md (validated Freerouting recipe and helper); render.sh.
BASELINES: heritage snapshot of the Rev2 layout ${A.heritageSnap}; pre-layout DRC ${A.drcBaseline}; schematic netlist ${A.netlist}.
CHECKS EVERY HAND-BACK MUST PASS (paste the outputs in your result):
  ${A.kicadPy} tools/pcb/heritage.py check ${A.heritageSnap} <board> --allow-zone-growth --allow-edge   → 0 violations
  ${ATTACH}
  ${A.kicad} pcb drc --format json --severity-all --all-track-errors --schematic-parity --refill-zones --output <x.json> <board> ; python3 tools/pcb/drc_summary.py <x.json> --baseline ${A.drcBaseline}  (parity must stay at the §6 pre-existing items; errors/unconnected as the stage requires)
  tools/pcb/render.sh <board> <outdir> and Read top.pdf / bottom.pdf to look at what you produced.
HARD RULES (brief §4): heritage frozen; L11 attachment rule (new copper meets the flight section only as short stubs from connector pads, one per net, on the pad's layer, ≤ 12 mm, inside the 12 mm edge band; EN taps at R104/R100/R103 pad 1; no new via inside the Rev2 outline; nothing routed across the flight section); one writable board per agent (your copy); pcbnew scripting / kicad-cli only; no GUI; no git commit; no new copper joining two existing FC nets; RF keep-outs; jlcpcb/project.db read-only; parts outside the outline are defects.

CONTEXT: ${A.context}
`

const PROPOSAL = {
  type: 'object',
  properties: {
    name: { type: 'string' },
    floorplan_json_path: { type: 'string', description: 'path to the proposal JSON: {outline:[[x,y]...], fillet_vertices:[...], remove_edge_regions:[...], mounting_holes:[[x,y]...], new_gnd_pours:[...], stitching:{...}, placements:{ref:{x,y,rot,side}}, lanes:[...], keepouts:[...]}' },
    rationale_md_path: { type: 'string' },
    outline_bbox: { type: 'string' },
    area_new_cm2: { type: 'number' },
    blocks: { type: 'array', items: { type: 'object', properties: { block: { type: 'string' }, region: { type: 'string' }, refs: { type: 'array', items: { type: 'string' } }, connects_to: { type: 'string' } }, required: ['block', 'region', 'refs', 'connects_to'] } },
    estimated_longest_net_mm: { type: 'number' },
    check_results: { type: 'string', description: 'apply_placement.py --check-only output on a board copy with the placement applied: parts outside outline, courtyard overlaps from DRC' },
    risks: { type: 'array', items: { type: 'string' } },
  },
  required: ['name', 'floorplan_json_path', 'rationale_md_path', 'outline_bbox', 'area_new_cm2', 'blocks', 'check_results', 'risks'],
}

const JUDGEMENT = {
  type: 'object',
  properties: {
    winner: { type: 'string' },
    scores: { type: 'array', items: { type: 'object', properties: { name: { type: 'string' }, score: { type: 'number' }, why: { type: 'string' } }, required: ['name', 'score', 'why'] } },
    synthesized_json_path: { type: 'string', description: 'the floorplan to build (winner plus grafted improvements), same schema' },
    changes_from_winner: { type: 'array', items: { type: 'string' } },
    open_risks: { type: 'array', items: { type: 'string' } },
  },
  required: ['winner', 'scores', 'synthesized_json_path', 'changes_from_winner', 'open_risks'],
}

const STAGE = {
  type: 'object',
  properties: {
    board_path: { type: 'string', description: 'your result board copy (the workflow adopts it into the live board only after the checks pass)' },
    heritage_violations: { type: 'integer' },
    drc_errors: { type: 'integer' },
    drc_unconnected: { type: 'integer' },
    drc_parity: { type: 'integer' },
    drc_warnings_new: { type: 'integer' },
    drc_by_type: { type: 'string' },
    outside_outline: { type: 'integer' },
    summary: { type: 'string' },
    report_path: { type: 'string' },
    open_issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['board_path', 'heritage_violations', 'drc_errors', 'drc_unconnected', 'drc_parity', 'drc_warnings_new', 'drc_by_type', 'outside_outline', 'summary', 'open_issues'],
}

// ---------- Floorplan: judge panel (stage 'floorplan' only) ----------
let judged = null
if (RUN_STAGE === 'floorplan') {
phase('Floorplan')
const ANGLES = [
  'shortest-connections-first: minimise the length of every new-to-existing net (face buses to their TCA4311A, U6 EN taps, J14/B- to the replica), accept a less regular block layout',
  'bench-usability-first: every cable/jumper/switch on the outer edges with generous finger room, silkscreen legends, L3 lanes 15 mm not 12, accept longer traces',
  'manufacturing-and-EMC-first: keep the emulator core and USB tight and over solid ground, cluster 1210 caps and the inductor by U511, isolate the 3 A bench paths on the bottom strip, minimise via count and outline complexity',
]
log(`Floorplan: ${NPROP} ${M.proposal} proposals → ${M.judge} judge`)
const proposals = (await parallel(Array.from({ length: NPROP }, (_, i) => () =>
  agent(COMMON + `
ROLE: Floorplan proposer #${i + 1}. Design the board extension and the placement of all 218 new parts according to brief §3 L1–L3, L6, L8, **L11 (attachment rule: every block must sit within reach of the connector pads it attaches to — faces column opposite J1/J2/J6/J9/J11/J13, BATT/TOP buffers near J14/J16, inhibit headers under J7/J8/J10/J15/J19/J20/J29/J30, replica under J14, pyro taps beside R100/R103/R104 at U6's edge; include an "attachments" table in the rationale: net → pad → block)** and §2 keep-outs, with this emphasis: ${ANGLES[i % ANGLES.length]}.
HOW: read the brief; inspect the live board with pcbnew (footprint positions/sides/bounding boxes of the heritage parts near the right and bottom edges; the Edge.Cuts geometry — corner arcs, cut-outs); read the six Phase-1 sheet reports for what each block is; group parts by block; write the floorplan JSON (schema in the result) with an L-shaped outline per L1 (you may adjust the wing/strip sizes by up to ±15 mm with reasons), fillet vertices, the Edge.Cuts remove regions (the old right edge and bottom edge segments that the extension replaces — keep everything else), mounting holes, GND pours, stitching points, and per-refdes placements (mm, rot, side). Then on a board copy: run outline.py with your JSON, apply_placement.py with your placements, run DRC (courtyard overlaps must be 0 among new parts; parts outside outline 0) and heritage check (0), render, and Read the top/bottom PDFs to sanity-check. Iterate until clean. Save the JSON and a rationale markdown into ${A.docs}/floorplan_proposal_${i + 1}.json / .md. Do not route.`, { label: `proposal:${i + 1}`, phase: 'Floorplan', model: M.proposal, effort: EFF(M.proposal), schema: PROPOSAL })))).filter(Boolean)
log(`Floorplan: ${proposals.length} proposals`)

judged = await agent(COMMON + `
ROLE: Floorplan judge and synthesiser (the one Opus decision of this phase). ${proposals.length} proposals:
${JSON.stringify(proposals, null, 2)}
Open each JSON and rationale, apply each to a fresh board copy yourself (outline.py + apply_placement.py + DRC courtyard/outside checks + heritage), render and look at them. Score 0-10 on: brief compliance (L1–L3, L6, L8, L11 attachment reach, keep-outs, lanes), routability (short critical nets: face buses ≤ 40 mm to their buffer, U6 EN taps ≤ 30 mm, replica/J14 path short and wide-able, USB pair short), bench usability (edge access, legends room), EMC/ground (emulator over solid ground, 3 A paths on the strip), manufacturability (courtyards, 1210s near U511, outline simplicity). Pick the winner, graft the best ideas from the others, write ${A.docs}/floorplan.json (final, same schema) and ${A.docs}/floorplan.md (decision, scores, grafts, attachments table net → pad → block, remaining risks). Apply the final floorplan to a board copy, set its page to A3 (board.GetPageSettings().SetType("A3")), prove: outside-outline 0, courtyard overlaps among new parts 0, heritage 0; save that copy as ${A.docs}/floorplan_preview.kicad_pcb (with the .kicad_pro next to it) and render it FOR THE OWNER'S REVIEW: tools/pcb/render.sh → ${A.docs}/img/floorplan_top.pdf / floorplan_bottom.pdf, plus PNGs via "${A.kicad} pcb render --side top --output ${A.docs}/img/floorplan_top.png" and "--side bottom … floorplan_bottom.png" (fall back to kicad-cli pcb export svg of F.Cu/B.Cu/Edge.Cuts/F.SilkS with courtyards if render is unavailable). Put a one-page owner summary at the top of floorplan.md: a labelled block map (which block where, sizes), the outline dimensions, the attachment map, and the questions you want the owner to answer.`, { label: 'judge:floorplan', phase: 'Floorplan', model: M.judge, effort: EFF(M.judge), schema: JUDGEMENT })
if (!judged) throw new Error('floorplan judge returned nothing')
log(`Floorplan: winner ${judged.winner}; final ${judged.synthesized_json_path}`)
return { stage: 'floorplan', floorplan: judged, proposals: proposals.map(p => ({ name: p.name, json: p.floorplan_json_path, md: p.rationale_md_path, area: p.area_new_cm2, risks: p.risks })), next: 'owner review gate: rerun with stage:"build", floorplanJson:<approved floorplan.json>' }
}
if (!A.floorplanJson) throw new Error('stage "build" needs args.floorplanJson (the owner-approved floorplan)')
judged = { synthesized_json_path: A.floorplanJson, winner: 'owner-approved' }
const FLOORPLAN_MD = A.floorplanMd || `${A.docs}/floorplan.md`   // the owner-reviewed report that goes with floorplanJson (floorplan_v2.md after stage 2b)
const PANEL = A.panelFixPlan ? `PANEL FIX PLAN (stage 2c review, binding): ${A.panelFixPlan} — read it first. Its "routing_instructions" are the routing owner's order of work (hand-route the 37 L11 stubs first, then the USB pair on F.Cu, then the U200/U511 escapes with the 0.45/0.20 via class, then Freerouting; 3V3_EMU pour on In2 over the emulator core only; PYRO_INHIBIT_STATE and U200's opposite-side signals on In2; decoupling GND vias per its table), its "floorplan_level" items are the build owner's (netclass instantiation, fiducial sites, SW703 courtyard), and "deferred" lists what is NOT to be done now. The brief §12 F5–F10 records the owner/PM rulings behind it (one B.Cu→F.Cu via allowed per J2/J9/J13 stub; J14 pins 10/12 stub up to 22 mm with a hand-traced path; J12 relief slot already in the floorplan).` : ''

// ---------- Close: resume from a routed-but-incomplete board with new rulings (stage "close") ----------
let built = null
let routed = null
if (RUN_STAGE === 'close') {
  if (!A.boardPath) throw new Error('stage "close" needs args.boardPath (the routed board to continue from, with its project siblings next to it)')
  built = { board_path: A.boardPath, summary: 'routed board from the previous run (project siblings next to it)', heritage_violations: 0, drc_errors: -1, drc_unconnected: -1, outside_outline: 0 }
  phase('Route')
  if (A.closePlan) {
    // Plan mode (round 3+): independent workstreams on their own copies of boardPath, each writes a delta JSON of the
    // items it added/removed; a merge step applies the deltas to one board; serial steps then chain board_path.
    const P = A.closePlan
    const STEP = (s, input, extra) => COMMON + `
${PANEL}
${A.closureNotes ? 'PM NOTES FOR THIS CLOSURE ROUND (binding; they supersede generic instructions above where they conflict): ' + A.closureNotes : ''}
ROLE: ${s.label} (${s.model || M.fixEscalate}). Input board: ${input} (project siblings next to it — copy the whole directory, never work on a bare .kicad_pcb). Workstream brief: ${s.prompt}
${extra || ''}`
    const opts = s => ({ label: `close:${s.key}`, phase: 'Route', model: s.model || M.fixEscalate, effort: EFF(s.model || M.fixEscalate), schema: STAGE })
    const streams = (await parallel((P.parallel || []).map(s => () => agent(STEP(s, A.boardPath), opts(s)).then(r => r && Object.assign(r, { key: s.key })))))
    streams.forEach((r, i) => log(r ? `Workstream ${r.key}: unconnected ${r.drc_unconnected}, errors ${r.drc_errors}, heritage ${r.heritage_violations}` : `Workstream ${P.parallel[i].key}: returned nothing`))
    routed = { board_path: A.boardPath, drc_unconnected: A.priorUnconnected ?? -1, drc_errors: -1, heritage_violations: 0, open_issues: [] }
    if (P.merge && streams.filter(Boolean).length) {
      routed = await agent(STEP(P.merge, A.boardPath, 'WORKSTREAM RESULTS (each names its board and its delta JSON in summary/report_path): ' + JSON.stringify(streams.filter(Boolean))), opts(P.merge))
      if (!routed) throw new Error('merge returned nothing')
      log(`Merge: unconnected ${routed.drc_unconnected}, errors ${routed.drc_errors}, heritage ${routed.heritage_violations}`)
    }
    for (const s of P.serial || []) {
      const prev = routed
      routed = await agent(STEP(s, prev.board_path, 'PREVIOUS STEP LEFT: ' + JSON.stringify({ unconnected: prev.drc_unconnected, errors: prev.drc_errors, issues: prev.open_issues })), opts(s))
      if (!routed) throw new Error(`${s.key} returned nothing`)
      log(`${s.key}: unconnected ${routed.drc_unconnected}, errors ${routed.drc_errors}, heritage ${routed.heritage_violations}`)
    }
  }
  for (let attempt = 1; attempt <= 2 && !A.closePlan; attempt++) {
    const model = attempt === 1 ? M.fixEscalate : M.fixEscalate
    routed = await agent(COMMON + `
${PANEL}
ROLE: Routing CLOSURE owner (attempt ${attempt}, ${model}). Input: ${A.boardPath} — the previous run's routed board (heritage 0, attachment 0, DRC clean except ${A.priorUnconnected || 'the'} unconnected items, all attributed in ${A.docs}/route_report.md §9 and in the summary below). Your job is to close the remaining connections. NEW RULINGS since that board (brief §12 F11–F12, already implemented in tools/pcb/attachment_check.py — read its header): (1) the single B.Cu→F.Cu via allowance now also covers J16 pin 1 (USBBOOT) and J14 pins 10/12 (BATT_SDA/SCL), and J14 pins 10/12 allow 24 mm — route USBBOOT and BATT_SCL with the paths the previous attempt measured; (2) OWNER RULING: F0_SCL (J6.5), F4_SDA (J1.6) and Deploy2_EN (U6.6) may be attached by a T-tap ending ON the same net's heritage track or via within 2.5 mm of that pad (NET_TAP_EXCEPTIONS) — the heritage geometry stays byte-identical (heritage.py enforces it), DRC clearance to everything else applies, exactly one tap per net; (3) PM: 3V3_EMU's EmuRail class (1.0 mm / 0.20 clearance / via 0.46/0.20) and 0.46/0.20 stub vias are accepted; (4) PM: to open the RP2350/U303/U511 escapes you MAY move decoupling / bootstrap capacitors at U200, U303 and U511 OUTWARD by at most 0.30 mm each (keep them against their pin group per detail/placement_emulator_core.md; record every move with before/after coordinates), and you may use 0.46/0.20 vias for GND pads that have no via site within 5 mm by placing the via wherever the GND plane is reachable (a GND track of any length to a via is fine); (5) give Freerouting more wall-clock on the emulator core: FR_TIMEOUT_MIN=240 and up to 6 passes, or route the escapes by pcbnew scripting yourself where the router fails — the panel forecast said U200's north edge escapes QSPI laterally through the 1.16 mm alley at x 273.165–274.325 and the ten opposite-side signals go to In2. Order: taps and via-allowance stubs first (attachment_check must stay 0), then escapes (hand or router), then a final route.sh pass for anything left, then refill. Every hand-back: heritage.py check with --refill --core-inset 12 --ref-board ${REF_BOARD} (0; carve-out notes are fine), attachment_check (0), DRC with --schematic-parity --refill-zones inside a directory holding the .kicad_pro/.kicad_dru/lib siblings. Never write the live board. Append a "closure" section to ${A.docs}/route_report.md: what closed, how, the cap moves, what (if anything) is still open with the reason. Return board_path.
${A.closureNotes ? 'PM NOTES FOR THIS CLOSURE ROUND (binding, they supersede the generic instructions above where they conflict): ' + A.closureNotes : ''}
${attempt > 1 ? 'The previous closure attempt left: ' + JSON.stringify(routed && { unconnected: routed.drc_unconnected, errors: routed.drc_errors, issues: routed.open_issues }) : ''}`, { label: `close:${attempt}`, phase: 'Route', model, effort: EFF(model), schema: STAGE })
    if (!routed) throw new Error('closure returned nothing')
    log(`Closure attempt ${attempt}: unconnected ${routed.drc_unconnected}, errors ${routed.drc_errors}, heritage ${routed.heritage_violations}`)
    if (routed.drc_unconnected === 0 && routed.heritage_violations === 0) break
  }
}

// ---------- Build: outline, ground, holes, stitching, netclasses, placement on the live board copy ----------
if (RUN_STAGE !== 'close') {
phase('Build')
built = await agent(COMMON + `
${PANEL}
ROLE: Build owner. Take the OWNER-APPROVED floorplan ${judged.synthesized_json_path} (and ${FLOORPLAN_MD}, including any owner change notes recorded there and in the brief §12) and produce the placed, unrouted board with ONE command: tools/pcb/build_floorplan.sh <floorplan.json> <your scratch OUT_DIR> ${REF_BOARD} — it copies the live board into OUT_DIR/proj/ WITH the project files beside it (KiCad's zone filler and kicad-cli silently use factory-default rules on a board that has no sibling .kicad_pro, which changes every fill — never fill or DRC a bare copy), runs outline.py (incl. the J12 relief-slot cutout), apply_placement.py, sets page A3, and runs heritage (refilled vs Rev2), attachment_check and DRC with parity; read its log. Then python3 tools/pcb/netclasses.py on OUT_DIR/proj/FlatSat_V1.kicad_pro (report the exact classes written; scope USB_EMU to EMU_USB_DP/EMU_USB_DM only), add the panel's floorplan-level items (fiducial pads at (232.5, 50.5) and (252.0, 140.0) as board-only 1 mm copper / 2 mm mask footprints or record them for stage 5; an F.CrtYd rectangle x 243.75–257.20 / y 63.75–71.20 for SW703 in the project-local copy of its footprint), refill zones, re-run the gates; then the hand-back checks: heritage (0), attachment_check (0 — there are no new tracks yet, it must still run clean), parity (§6 only), outside-outline 0, courtyard overlaps 0 among new parts, DRC errors limited to unconnected items (routing comes next), and render. Expect pad-to-pad clearance errors inside the new fine-pitch footprints (the 2026-09-14 smoke run showed ~40 such "Pad n / Pad n+1" items once the L5 netclass clearances applied): resolve them the way the FC does (CLAUDE.md) — memberOfFootprint('REF') exemptions in FlatSat_V1.kicad_dru for those new refs, never by lowering a class clearance — and list the exempted refs in build_report.md. Write ${A.docs}/build_report.md with the outline coordinates, holes, zone list, netclass table, and pasted check outputs. Return board_path = your result copy and the .kicad_pro path you produced.`, { label: 'build:outline-ground', phase: 'Build', model: M.build, effort: EFF(M.build), schema: STAGE })
if (!built) throw new Error('build returned nothing')
log(`Build: heritage ${built.heritage_violations}, errors ${built.drc_errors}, unconnected ${built.drc_unconnected}, outside ${built.outside_outline}`)

// ---------- Route ----------
phase('Route')
for (let attempt = 1; attempt <= 2; attempt++) {
  const model = attempt === 1 ? M.route : M.fixEscalate
  routed = await agent(COMMON + `
${PANEL}
ROLE: Routing owner (attempt ${attempt}, ${model}). Input board: ${built.board_path} (with its .kicad_pro next to it: ${built.summary}). Follow tools/pcb/README.md exactly (the validated Freerouting recipe with the heritage lock, the flight-section keep-out and the merge/adopt steps). L11 first: for every shared net, script the attachment stub yourself with pcbnew — from the allowed connector pad (or R104/R100 pad 1 / U6 pins 3–6 for the EN taps) straight out to the extension on the pad's own layer, within the per-pad allowance in tools/pcb/attachment_check.py ALLOWED_PADS (14 mm; 24 mm for J7/J10/J20; 22 mm for J14 pins 10/12 with a hand-traced jog), one stub per net; the nine stubs from the bottom-side connectors J2/J9/J13 each take exactly ONE B.Cu→F.Cu via inside the band at a spot you verify free of F.Cu heritage copper (attachment_check enforces this: VIA_ALLOWED_PADS), every other stub has no via inside the Rev2 outline — and run attachment_check (0 violations) before anything else. Then pre-route by pcbnew scripting the nets brief L5 calls out — the BenchPower nets and the new copper on Dir_Chrg_In / B- / VBUSP / VBATT_SENSE / INHIB_x / IN_RBF / VSOLAR at ≥ 1.0 mm (1.5 mm where possible) from the stub ends to the shunt headers / replica / injection, and the EMU_USB_DP/DM pair as a coupled 0.25 mm pair on F.Cu — so the autorouter does not do them at default width; then run: KEEPOUT_JSON=${KEEPOUT} REF_BOARD=${REF_BOARD} tools/pcb/route.sh PRE OUT <passes> (it implements the full README recipe: prep → keep-out fixture from ${KEEPOUT} on the export copy [flight core + via_keepout over the flight section + heritage copper in the band; the run aborts if the fixture did not apply] → DSN + fixdsn → Freerouting -mt 1 → SES into a fresh copy → merge that keeps heritage byte-for-byte and adopts only chains reaching a new-footprint pad [Freerouting's redraws of fixed heritage wires are dropped] → attachment_check and AUTOMATIC PRUNE of everything the L11 gate rejects [unpruned copy kept as OUT.unpruned.kicad_pcb] → heritage check with zones refilled in memory against the Rev2 board [core fills identical, band carve-out reported] → DRC). Freerouting on the full board takes 30-60+ minutes and prints nothing for long stretches: launch route.sh with the Bash tool's run_in_background option and wait for it (Monitor with an until-loop on the OUT file or the log), never kill it for silence — check CPU% instead; FR_TIMEOUT_MIN defaults to 180. NEVER edit a shell script while a run of it is in progress (bash reads it by byte offset) — copy tools/pcb to your scratch dir first if you need to change anything. After the run: every pruned connection is a DRC unconnected item; route those by hand as stubs from the allowed pads (pcbnew scripting), or fix the placement of the NEW part that made the autorouter reach for a heritage trace, and re-run route.sh on the pruned board (the stubs are fixed wires in the DSN, so they survive). Iterate (more passes, local rip-up via re-running on a copy) until heritage 0, attachment 0 and unconnected 0, or you can prove the remaining connections are blocked by placement (then list them with the reason and do NOT move heritage parts). Refill zones. Write ${A.docs}/route_report.md with the recipe invocation, pass count, unconnected before/after, via count added, width audit of the L5 nets (query track widths per net with pcbnew and paste), USB pair length match, heritage output. Return board_path.
${attempt > 1 ? 'The previous attempt left problems: ' + JSON.stringify(routed && { unconnected: routed.drc_unconnected, issues: routed.open_issues }) : ''}`, { label: `route:${attempt}`, phase: 'Route', model, effort: EFF(model), schema: STAGE })
  if (!routed) throw new Error('route returned nothing')
  log(`Route attempt ${attempt}: unconnected ${routed.drc_unconnected}, errors ${routed.drc_errors}, heritage ${routed.heritage_violations}`)
  if (routed.drc_unconnected === 0 && routed.heritage_violations === 0) break
}
}  // end of the build+route path

// ---------- Cleanup: DRC classes ----------
phase('Cleanup')
let current = routed
for (let round = 1; round <= MAX_FIX; round++) {
  if (current.drc_errors <= OK_ERR && current.heritage_violations === 0 && current.drc_unconnected <= OK_UNCONN && !(A.cleanupNotes && round === 1)) { log('Cleanup: nothing to fix'); break }
  const model = round < MAX_FIX ? M.fix : M.fixEscalate
  const fixed = await agent(COMMON + `
ROLE: DRC cleanup (round ${round}, ${model}). Input board: ${current.board_path}. Current state: errors ${current.drc_errors}, unconnected ${current.drc_unconnected}, heritage ${current.heritage_violations}; by type: ${current.drc_by_type}; open issues: ${JSON.stringify(current.open_issues)}.
Run DRC yourself (--all-track-errors --schematic-parity --refill-zones), list every error with --list and --new-only, and fix them by class with pcbnew scripting on a copy (clearance: move/reroute the offending new track/via; courtyard: nudge new parts only; copper-edge: pull back; unconnected: route the missing connection; solder-mask bridge / silk over pad: adjust; hole-to-hole: move new vias). Never touch heritage items — if an error involves only heritage items it is pre-existing (compare with the baseline) and is triaged, not fixed. After each class re-run DRC + heritage + attachment_check (0 violations; a fix may not push copper into the flight section). Write/append ${A.docs}/drc_triage.md: every remaining warning with a disposition (fixed / pre-existing / accepted-with-reason). Return board_path.
${A.cleanupNotes ? 'PM NOTES FOR THIS CLEANUP (binding; they supersede the generic instructions above where they conflict): ' + A.cleanupNotes : ''}`, { label: `cleanup:${round}`, phase: 'Cleanup', model, effort: EFF(model), schema: STAGE })
  if (!fixed) break
  current = fixed
  log(`Cleanup round ${round}: errors ${current.drc_errors}, unconnected ${current.drc_unconnected}, heritage ${current.heritage_violations}`)
}

// ---------- Finish: silkscreen, docs, preview ----------
phase('Finish')
const finished = await agent(COMMON + `
ROLE: Finish owner. Input board: ${current.board_path}. (1) Silkscreen per brief L8 on the new area only (pcbnew scripting: PCB_TEXT on F.SilkS/B.SilkS; jumper legends, polarity, mode legend at J500, "BENCH ONLY — NOT FOR FLIGHT", pin-1 marks; make sure new refdes are visible and not over pads; DRC silk-over-pad/mask clean for new items). (2) Final checks: heritage 0, attachment_check 0 (paste its stub list: net → pad → length), DRC errors 0 / unconnected 0 / parity §6-only, warnings triaged in drc_triage.md; kicad-cli pcb export stats. (3) Renders into ${A.docs}/img/ (render.sh → PDFs; also kicad-cli pcb render --side top / bottom PNGs if available). (4) Production PREVIEW into ${A.project}/jlcpcb/preview/ (kicad-cli pcb export gerbers/drill/pos with the FC's plot settings, kicad-cli sch export bom grouped with the LCSC Part field) clearly labelled preview — the official production files come from the owner's JLCPCB-plugin GUI step. (5) Write ${A.docs}/layout_report.md: what was built (outline, area, holes, zones, netclasses), placement summary per block, routing stats (tracks/vias added, longest nets, USB pair), DRC/parity/heritage final tables, silkscreen list, preview file list, and the open items for the review (pcb-flight-review) and for the owner. Return board_path (final).`, { label: 'finish:silk-docs-preview', phase: 'Finish', model: M.docs, effort: EFF(M.docs), schema: STAGE })
if (!finished) throw new Error('finish returned nothing')

return {
  floorplan: judged,
  build: { board: built.board_path, heritage: built.heritage_violations, errors: built.drc_errors },
  route: { board: routed.board_path, unconnected: routed.drc_unconnected, heritage: routed.heritage_violations },
  cleanup: { board: current.board_path, errors: current.drc_errors, unconnected: current.drc_unconnected, heritage: current.heritage_violations, by_type: current.drc_by_type },
  final: finished,
}
