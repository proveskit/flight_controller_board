export const meta = {
  name: 'flatsat-schematic-review',
  description: 'Fable review-and-fix round for captured KiCad sheets: five Fable lenses → dedup → Fable refuters per sheet → Fable chair fix list → owner-per-file fixers → independent re-check → Fable sign-off report',
  whenToUse: 'After flatsat-schematic-capture. args: {project, root, rootUuid, brief, docs, scratch, kicad, baselineErc, baselineNetlist, sheets:[{key,file,name,uuid,page,refdes,model,section}], captureResult, context, maxFixRounds, models?:{review,verify,prioritize,signoff}, verifyModelByIndex?:{"<i>":"sonnet"}}',
  phases: [
    { title: 'Review', detail: '5 Fable reviewers, distinct lenses, whole project', model: 'fable' },
    { title: 'Verify', detail: 'Fable skeptics batched by sheet, prompted to refute', model: 'fable' },
    { title: 'Prioritize', detail: 'Fable chair: dispositions fix-now / layout / accept', model: 'fable' },
    { title: 'Fix', detail: 'owner-per-file: one Opus agent per affected sheet, integrator for root/existing sheets' },
    { title: 'Confirm', detail: 'Opus checker re-runs ERC/netlist; Fable sign-off writes the review report', model: 'fable' },
  ],
}

const A = args
const MAX_FIX = A.maxFixRounds ?? 2
// Per-stage model selection. Defaults reproduce the original all-Fable design; args.models overrides a stage
// ({review, verify, prioritize, signoff}) and args.verifyModelByIndex overrides single verify batches by index
// ({"10": "sonnet"}). On a resume, a stage whose (prompt, opts) are unchanged replays from cache, so only change
// the model of stages that have not completed.
const M = Object.assign({ review: 'fable', verify: 'fable', prioritize: 'fable', signoff: 'fable' }, A.models || {})
const VM = A.verifyModelByIndex || {}
const EFF = m => (m === 'fable' ? 'xhigh' : 'high')

const SHEET_LIST = A.sheets.map(s => `  ${s.key}: ${A.project}/${s.file}  ("${s.name}", page ${s.page}, uuid ${s.uuid}, refdes ${s.refdes}, brief §${s.section})`).join('\n')

const COMMON = `
You are reviewing the PROVES FlatSat V1 KiCad 10 project after Phase-1 schematic capture. Return raw data only (structured output), no prose for humans.

PROJECT DIR:        ${A.project}
ROOT SCHEMATIC:     ${A.project}/${A.root}   (root uuid ${A.rootUuid}); existing FC sheets: eps_side.kicad_sch (Power Systems), load_switches.kicad_sch, RP2350.kicad_sch, watchdog.kicad_sch
NEW SHEETS (Phase 1):
${SHEET_LIST}
PM BRIEF (the spec; §2 decisions, §4 net contract, §6 per-sheet requirements, §10 exit criteria): ${A.brief}
DOCS (sheet reports sheet_<key>.md, integration_report.md, connector_trace.md, 01_brief_critique.md): ${A.docs}
CAPTURE WORKFLOW RESULT (what implementers/verifiers/integrator/checker reported): ${A.captureResult}
SCRATCH (reference PDFs, netlists, BOMs, upgraded reference schematics, symbol pantry, rendered FC schematic): ${A.scratch}
TOOLS (${A.project}/tools): sch_lint.py, harness_erc.sh, erc_summary.py, netlist_diff.py, get_symbol.py, kicad10_sch_primer.md, baseline/connector_nets.md
kicad-cli: ${A.kicad}; baseline ERC/netlist (Rev2): ${A.baselineErc} / ${A.baselineNetlist}
Use your own scratch subdirectory ${A.scratch}/review_<yourlabel>/ for exports.

HOW TO WORK:
- Files are large S-expressions; grep/python, never cat a whole sheet. Render with kicad-cli sch export pdf and Read the pages you review.
- Datasheets: fetch them (WebFetch/WebSearch); cite section/figure/table.
- Every finding needs concrete evidence: sheet + refdes + net (+ coordinate if useful), plus what the brief/reference design/datasheet/standard says. No evidence, no finding.
- A finding is something that would make the FlatSat not work, be unsafe on a bench, damage the FC, mislead flight software, be unbuildable at JLCPCB, or contradict the plan/brief/user rules. Library-metadata ERC noise (lib_symbol_issues, lib_symbol_mismatch, footprint_link_issues, endpoint_off_grid) is not a finding unless it hides a real problem. Cosmetics are minor at most.
- The FC portion has flight heritage; findings about unchanged FC circuitry are out of scope for this round (note them as info at most).
- Prefer a few solid findings over many speculative ones. Zero findings is acceptable. Set confidence honestly.

CONTEXT FROM THE PRODUCT MANAGER:
${A.context}
`

const FINDINGS = {
  type: 'object',
  properties: {
    scope_checked: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          sheet: { type: 'string', description: 'sheet key (emulator_mcu, …), "root", "eps_side", "load_switches", "docs", or "cross-sheet"' },
          severity: { type: 'string', enum: ['critical', 'major', 'minor', 'info'] },
          location: { type: 'string', description: 'refdes/net/coordinate or file:line' },
          description: { type: 'string' },
          evidence: { type: 'string' },
          reference: { type: 'string', description: 'brief §, reference design file, datasheet section, standard' },
          recommendation: { type: 'string', description: 'concrete fix: part, value, net, wiring' },
          confidence: { type: 'number' },
        },
        required: ['title', 'sheet', 'severity', 'location', 'description', 'evidence', 'recommendation', 'confidence'],
      },
    },
  },
  required: ['scope_checked', 'findings'],
}

const LENSES = [
  { key: 'electrical', prompt: `
LENS: Electrical correctness and contract compliance. For every new sheet and the integrated root: connectivity against brief §4 (exact net names; defined-by vs consumed-by; pull-up rails; 10 k series taps), §6 requirements item by item, §3 hard rules (nothing in series with a flight power path; no FC global label leaked from a template onto the emulator sheet; emulator never sources current into an unpowered FC and vice versa — trace every path between 3V3_EMU/VBUS_EMU and +3V3/Fn_PWR/VBUSP through pull-ups, ESD diodes, buffers, FET body diodes), power pins on the right rails, floating inputs, address strapping (TMP112 0x48, VEML6031 0x29, DRV2605L 0x5A), the promoted labels (§4.3) still forming the same nets, the pyro inhibit clamp reaching VIL with the 4.7 k sources, the R5460N replica seeing a sane midpoint, the BQ25886 output jumper default, the inhibit shunt headers paralleling the right connector pairs. Use the netlist: export it and read the nodes of every §4 net.` },
  { key: 'datasheet', prompt: `
LENS: Datasheet parity for every NEW part. Parts: RP2350A (hardware design guide: decoupling per rail, 1V1 inductor/caps, crystal load caps and series R, USB series R, RUN, QSPI_SS/BOOTSEL, XIN/XOUT), W25Q128JVS, the emulator regulator (TPS62085 + XFL4015 per its datasheet typical application, or AP2112K dissipation/dropout), TCA4311A (VCC/EN/READY behaviour, pull-up values, capacitance, what happens with VCC=0 on each side), TMP112, VEML6031X00, DRV2605LDGS (EN, IN/TRIG, output load range vs the header/dummy load), R5460N208AA (2-cell application circuit R/C values, VC, DOUT/COUT gate drive, delay caps), IRF7458 (Vgs rating vs pack voltage, orientation of the back-to-back pair, body-diode direction), BQ25886 (input, ILIM/programming, no-battery behaviour, output arrangement copied from debug_board_v1), the injection Schottky/fuse (current, voltage vs 12–18 V bench, LT3652 VIN ≥ VFLOAT+3.3 V with the float voltage programmed on eps_side), BAT54W (Vf at the clamp current) vs TPS4H160-Q1 IN VIL(max), 2N7002-class open-drain FETs on FC_RESET/USBBOOT/WDT_DISABLE (what those FC nodes look like: pull-ups, RC, comparator input), USB-C CC/series/ESD, KMR2 buttons, JST-SH SWD. Report only material deviations or missing datasheet-required components; give the value that should be there.` },
  { key: 'bench-safety', prompt: `
LENS: Bench usability and safety, from the point of view of the technician who will use this board and the flight software engineer who will trust it. Walk through the bench modes: (a) PSU through the protection replica, (b) USB→BQ25886, (c) VSOLAR injection on/off, (d) pyro inhibit engaged/released, (e) emulator on with FC off and FC on with emulator off, (f) inhibit shunt headers fitted/removed in wrong combinations, (g) a real solar face or real battery pack plugged into J6/J14 while the FlatSat replicas are also active. For each: can anything be damaged, can a flight net be raised by bench circuitry, can the inhibit be defeated accidentally, is the default jumper state safe, are there enough test points/labels/notes for a person to operate it without reading the schematic, is the "SAFE" indication truthful (e.g. LED lit but a diode leg jumper removed). Check that text notes on the new sheets state the jumper tables and bench settings the brief §6 asks for. Check that the FlatSat still allows plugging the real boards in (connectors kept, no conflicts).` },
  { key: 'integrity', prompt: `
LENS: Project integrity, ERC/netlist, KiCad hygiene, documentation completeness. Re-run: full ERC (kicad-cli sch erc --severity-all --format json) with tools/erc_summary.py --baseline --ignore-noise and --list of every error and every new warning; netlist export + tools/netlist_diff.py against the baseline (no existing net may lose a pin; promotions are pure renames; everything else additions); tools/sch_lint.py on each new sheet with its --path and --refdes-block. Check: every footprint string on new symbols resolves to a real footprint (KiCad standard footprints dir, ~/Documents/KiCad/easyeda2kicad/easyeda2kicad.pretty, project fp-lib-table libs) — list any that do not; every lib_id on new sheets resolves through sym-lib-table or the global table or is a flatsat:* symbol present in symbols/flatsat.kicad_sym; LCSC numbers on new parts trace to a BOM CSV in the scratch refs or are marked "needs LCSC" in the reports; refdes unique project-wide; sheet symbols in the root match brief §5 (uuid, page, file, placement, no overlap — render the root page); connector_trace.md covers every pin of every connector in tools/baseline/connector_nets.md with a destination that is true (spot-check ten against the sheets); integration_report.md triages every non-noise warning; each sheet report exists and its pasted tool output matches what you reproduce.` },
  { key: 'firmware', prompt: `
LENS: Will this hardware let Phase-3 firmware and Phase-4 HWIL tests do their job? Read the plan's Phase 3/4 rows (brief §1, §2 D7-D9) and the flight-software expectations in /Users/ncc-michael/GitHut/proves-core-reference (grep for Drv2605, DetumbleManager, tca9548, TMP112, VEML, load switch / face enable handling, burnwire/antenna deployer tests, power monitor tests) to learn what the flight software actually does on each face channel and on the deploy/heater outputs. Then judge the emulator hardware: GPIO map allows one PIO I2C-slave engine per mux channel with SDA/SCL on PIO-compatible pins; Fn_PWR sensing edges are visible (RC/series values, no filtering that hides a short power cycle); the TCA4311A front-ends behave like the real boards on power-up (READY/EN timing) so the DRV2605 init handshake can be reproduced; the golden-reference face can actually run the existing drv2605_test/power_monitor_test (real coil/dummy load current draw); the pyro inhibit does not prevent the HWIL suite from at least observing the EN commands (test points); the bench_io open-drain control of FC_RESET/USBBOOT/WDT_DISABLE matches how the watchdog and boot circuits work (WDT_DISABLE node RC, USBBOOT via D4, RUN pull-up); the emulator console has UART/USB paths that do not contend with the FC's own USB (J12). Findings must say what firmware behaviour would break and where.` },
]

phase('Review')
log(`Review: ${LENSES.length} Fable lenses over ${A.sheets.length} new sheets + integration`)
const reviews = await parallel(LENSES.map(l => () =>
  agent(COMMON + l.prompt, { label: `review:${l.key}`, phase: 'Review', model: M.review, effort: EFF(M.review), schema: FINDINGS })
    .then(r => r && { ...r, lens: l.key })))

const all = reviews.filter(Boolean).flatMap(r => r.findings.map(f => ({ ...f, lens: r.lens })))
const key = f => (f.sheet + '|' + f.location + '|' + f.title).toLowerCase().replace(/[^a-z0-9|]/g, '').slice(0, 90)
const seen = new Map()
for (const f of all) { const k = key(f); if (!seen.has(k)) seen.set(k, f) }
let findings = [...seen.values()]
findings.forEach((f, i) => { f.id = i + 1 })
log(`Review done: ${all.length} raw findings, ${findings.length} after dedup (${findings.filter(f => f.severity === 'critical').length} critical, ${findings.filter(f => f.severity === 'major').length} major)`)

if (findings.length === 0) {
  const clean = await agent(COMMON + `
ROLE: Review-board chair. Five Fable reviewers (${LENSES.map(l => l.key).join(', ')}) reported zero findings. Write ${A.docs}/02_review_report.md recording what each lens checked (scopes below) and stating that the Phase-1 exit criteria (brief §10) are met, after re-running ERC and netlist_diff yourself and pasting the results. Return a one-paragraph summary.
SCOPES:
${JSON.stringify(reviews.filter(Boolean).map(r => ({ lens: r.lens, scope: r.scope_checked })), null, 2)}`, { label: 'signoff:clean', phase: 'Confirm', model: M.signoff, effort: 'high' })
  return { findings: [], reviews: reviews.filter(Boolean).map(r => ({ lens: r.lens, scope: r.scope_checked })), signoff: clean }
}

const VERDICTS = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'integer' },
          verdict: { type: 'string', enum: ['confirmed', 'refuted', 'uncertain'] },
          severity_adjusted: { type: 'string', enum: ['critical', 'major', 'minor', 'info'] },
          evidence_checked: { type: 'string' },
          reasoning: { type: 'string' },
          corrected_description: { type: 'string' },
          corrected_recommendation: { type: 'string' },
          duplicate_of: { type: 'integer' },
        },
        required: ['id', 'verdict', 'severity_adjusted', 'evidence_checked', 'reasoning'],
      },
    },
  },
  required: ['verdicts'],
}

// batch by sheet so one verifier loads that sheet + its datasheets once
const groups = new Map()
for (const f of findings) { const b = f.sheet || 'cross-sheet'; if (!groups.has(b)) groups.set(b, []); groups.get(b).push(f) }
const MAX_PER_BATCH = 8
const batches = []
for (const [name, fs] of groups) for (let i = 0; i < fs.length; i += MAX_PER_BATCH) batches.push({ name, items: fs.slice(i, i + MAX_PER_BATCH) })
log(`Verify: ${findings.length} findings in ${batches.length} batches: ` + batches.map(b => `${b.name}(${b.items.length})`).join(', '))

phase('Verify')
const batchResults = await parallel(batches.map((b, bi) => () =>
  agent(COMMON + `
ROLE: Independent skeptical verifier for "${b.name}". Reviewers reported the ${b.items.length} findings below. For EACH, try to REFUTE it: open the sheet, the netlist, the reference design, the brief section and the datasheet (fetch once, reuse). Reproduce the evidence yourself. Consider whether the item is an explicit PM decision (brief §2) or a documented deviation in the sheet report rather than a defect. If you cannot reproduce the evidence → refuted. If the evidence holds but severity is off → confirmed with severity_adjusted. "uncertain" only when the answer depends on information not in the repo or datasheet; say what is missing. Flag duplicates within the batch. One verdict per id, none skipped.

FINDINGS:
${JSON.stringify(b.items, null, 2)}
`, { label: `verify:${b.name}`, phase: 'Verify', model: VM[bi] || M.verify, effort: EFF(VM[bi] || M.verify), schema: VERDICTS })
    .then(r => ({ batch: b, r }))))

const byId = new Map(findings.map(f => [f.id, f]))
const verified = []
for (const br of batchResults.filter(Boolean)) {
  const got = new Set()
  for (const v of (br.r && br.r.verdicts) || []) {
    const f = byId.get(v.id); if (!f) continue
    got.add(v.id); verified.push({ finding: f, verdict: v })
  }
  for (const f of br.batch.items) if (!got.has(f.id)) {
    log(`Verifier ${br.batch.name} returned no verdict for #${f.id} "${f.title}"; carrying as uncertain`)
    verified.push({ finding: f, verdict: { id: f.id, verdict: 'uncertain', severity_adjusted: f.severity, evidence_checked: 'none', reasoning: 'verifier omitted this id' } })
  }
}
const isDup = v => v.verdict.duplicate_of && v.verdict.duplicate_of !== v.finding.id && byId.has(v.verdict.duplicate_of)
const kept = verified.filter(v => v.verdict.verdict !== 'refuted' && !isDup(v))
const refuted = verified.filter(v => v.verdict.verdict === 'refuted')
log(`Verify done: ${kept.length} confirmed/uncertain, ${refuted.length} refuted, ${verified.filter(isDup).length} duplicates`)

const FIXLIST = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    items: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'integer' },
          rank: { type: 'integer' },
          title: { type: 'string' },
          severity: { type: 'string', enum: ['critical', 'major', 'minor', 'info'] },
          disposition: { type: 'string', enum: ['fix-now', 'fix-in-layout-phase', 'accept-with-rationale', 'ask-hardware-lead', 'no-action'] },
          owner_file: { type: 'string', description: 'which single file the fix touches: a new sheet key, "root", "eps_side", "load_switches", "symbols", or "docs"' },
          location: { type: 'string' },
          action: { type: 'string', description: 'exact change: part/value/net/wiring/text' },
          rationale: { type: 'string' },
          verification: { type: 'string', description: 'how the fixer proves it (tool/output to paste)' },
        },
        required: ['id', 'rank', 'title', 'severity', 'disposition', 'owner_file', 'location', 'action', 'rationale', 'verification'],
      },
    },
    dropped: { type: 'array', items: { type: 'string' } },
  },
  required: ['summary', 'items'],
}

phase('Prioritize')
const packet = JSON.stringify({ kept, refuted: refuted.map(r => ({ id: r.finding.id, title: r.finding.title, why: r.verdict.reasoning })) }, null, 2)
const fixlist = await agent(COMMON + `
ROLE: Review-board chair (principal PCB engineer + QA in one). You receive the verified findings (with verifier verdicts) and the refuted list. Produce ONE ranked fix list. Every kept item gets a disposition: fix-now (schematic change in this round), fix-in-layout-phase (needs the PCB, e.g. copper/placement), accept-with-rationale (PM decision in brief §2 or sheet-report deviation stands), ask-hardware-lead (needs a human decision; still say the default), no-action. Assign each fix-now item to exactly one owner_file so fixes can run in parallel without write conflicts (a cross-sheet contract mismatch is fixed on the CONSUMING sheet unless the defining sheet is clearly wrong). Be concrete: part, value, net, wire. Merge duplicates. Keep refuted reasoning in dropped.

PACKET:
${packet}
`, { label: 'prioritize:chair', phase: 'Prioritize', model: M.prioritize, effort: EFF(M.prioritize), schema: FIXLIST })

const fixNow = ((fixlist && fixlist.items) || []).filter(i => i.disposition === 'fix-now')
log(`Prioritize done: ${(fixlist && fixlist.items || []).length} items, ${fixNow.length} fix-now, ${((fixlist && fixlist.items) || []).filter(i => i.disposition === 'ask-hardware-lead').length} ask-hardware-lead`)

const FIXRESULT = {
  type: 'object',
  properties: {
    owner_file: { type: 'string' },
    fixed_ids: { type: 'array', items: { type: 'integer' } },
    not_fixed: { type: 'array', items: { type: 'object', properties: { id: { type: 'integer' }, why: { type: 'string' } }, required: ['id', 'why'] } },
    files_changed: { type: 'array', items: { type: 'string' } },
    verification: { type: 'string', description: 'lint/harness/netlist output after the fixes' },
  },
  required: ['owner_file', 'fixed_ids', 'not_fixed', 'files_changed', 'verification'],
}

phase('Fix')
const byOwner = new Map()
for (const it of fixNow) { const o = it.owner_file; if (!byOwner.has(o)) byOwner.set(o, []); byOwner.get(o).push(it) }
const ownerToSheet = new Map(A.sheets.map(s => [s.key, s]))
let fixResults = []
if (byOwner.size) {
  log(`Fix: ${byOwner.size} owner files: ` + [...byOwner.keys()].map(o => `${o}(${byOwner.get(o).length})`).join(', '))
  fixResults = await parallel([...byOwner.entries()].map(([owner, items]) => () => {
    const s = ownerToSheet.get(owner)
    const isSheet = !!s
    const fileDesc = isSheet
      ? `the new sheet ${A.project}/${s.file} ("${s.name}", uuid ${s.uuid}, instances path /${A.rootUuid}/${s.uuid}, refdes block ${s.refdes}, spec brief §${s.section}); you may also update ${A.docs}/sheet_${s.key}.md and ${A.project}/tools/gen/${s.key}_gen.py`
      : owner === 'docs' ? `documentation files in ${A.docs} only`
        : owner === 'symbols' ? `${A.project}/symbols/flatsat.kicad_sym and sym-lib-table only`
          : `${A.project}/${owner === 'root' ? A.root : owner + '.kicad_sch'} only (existing FC sheet: minimal, surgical edits; every changed net must be shown unchanged in membership by tools/netlist_diff.py unless the fix says otherwise) plus ${A.docs}/integration_report.md`
    return agent(COMMON + `
ROLE: Fixer. You own exactly ONE writable target: ${fileDesc}. Other agents are editing other files right now; touch nothing else. Write atomically (tmp + mv).
Apply each fix below exactly as specified (if you believe an item is wrong, do not apply it and explain in not_fixed). After all fixes: run tools/sch_lint.py (for a sheet) and SCRATCH=${A.scratch}/review_fix_${owner} tools/harness_erc.sh, re-export the PDF page and Read it, then paste the outputs in verification. Update the relevant report with a "Review fixes" section listing ids applied.

FIXES:
${JSON.stringify(items, null, 2)}
`, { label: `fix:${owner}`, phase: 'Fix', model: isSheet && s.model ? s.model : 'opus', effort: 'xhigh', schema: FIXRESULT })
  }))
  fixResults = fixResults.filter(Boolean)
  const fixedIds = new Set(fixResults.flatMap(r => r.fixed_ids || []))
  log(`Fix done: ${fixedIds.size}/${fixNow.length} items applied; not fixed: ${fixResults.flatMap(r => r.not_fixed || []).map(n => '#' + n.id).join(', ') || 'none'}`)
} else {
  log('Fix: nothing dispositioned fix-now')
}

const CHECK = {
  type: 'object',
  properties: {
    erc_errors_total: { type: 'integer' },
    erc_errors_attributable_to_new_sheets: { type: 'integer' },
    netlist_baseline_preserved: { type: 'boolean' },
    fixes_verified: { type: 'array', items: { type: 'integer' } },
    fixes_not_verified: { type: 'array', items: { type: 'object', properties: { id: { type: 'integer' }, why: { type: 'string' } }, required: ['id', 'why'] } },
    regressions: { type: 'array', items: { type: 'string' } },
    summary: { type: 'string' },
  },
  required: ['erc_errors_total', 'erc_errors_attributable_to_new_sheets', 'netlist_baseline_preserved', 'fixes_verified', 'fixes_not_verified', 'regressions', 'summary'],
}

phase('Confirm')
let check = null
for (let round = 1; round <= MAX_FIX; round++) {
  check = await agent(COMMON + `
ROLE: Independent checker (round ${round}). Fixers reported:
${JSON.stringify(fixResults, null, 2)}
The fix list was:
${JSON.stringify(fixNow, null, 2)}
Reproduce in ${A.scratch}/review_check_${round}/: full ERC (--severity-all json) + tools/erc_summary.py --baseline ${A.baselineErc} --ignore-noise --list for every error; netlist export + tools/netlist_diff.py ${A.baselineNetlist} <new> --ignore-unconnected (no existing net lost pins; promotions are pure renames); tools/sch_lint.py on every new sheet. For each fix-now id, open the file and confirm the change is present as specified (grep the net/refdes/value). List regressions (a new ERC error, a lost pin, a broken contract net). Be exact.`, { label: `check:post-fix#${round}`, phase: 'Confirm', model: 'opus', effort: 'xhigh', schema: CHECK })
  if (!check) { log(`Check #${round}: checker returned nothing`); break }
  log(`Check #${round}: ERC errors ${check.erc_errors_total} (new-sheet attributable ${check.erc_errors_attributable_to_new_sheets}), baseline preserved ${check.netlist_baseline_preserved}, fixes verified ${check.fixes_verified.length}/${fixNow.length}, regressions ${check.regressions.length}`)
  const problems = [...check.regressions.map(r => ({ id: 0, title: 'regression', action: r })), ...check.fixes_not_verified.map(n => ({ id: n.id, title: 'fix not present', action: n.why }))]
  if (problems.length === 0 && check.erc_errors_attributable_to_new_sheets === 0 && check.netlist_baseline_preserved) break
  if (round === MAX_FIX) { log('Confirm: problems remain after the last round; recorded for the sign-off'); break }
  const redo = await agent(COMMON + `
ROLE: Integrator/fixer (round ${round + 1}). The checker found these problems after the fix round; resolve them (you may edit any project file, one at a time, atomically; record each edit in ${A.docs}/integration_report.md):
${JSON.stringify(problems, null, 2)}
Checker summary: ${check.summary}
Re-run ERC/netlist tools and paste outputs.`, { label: `fix:regressions#${round}`, phase: 'Fix', model: 'opus', effort: 'xhigh', schema: FIXRESULT })
  if (redo) fixResults.push(redo)
}

const signoff = await agent(COMMON + `
ROLE: Review-board chair, final sign-off. Write ${A.docs}/02_review_report.md: (1) scope of the five lenses (scopes below), (2) the prioritized list with dispositions and, for each fix-now item, whether the checker verified the fix, (3) accept-with-rationale and ask-hardware-lead items spelled out for the hardware lead with your recommended default, (4) refuted findings with why, (5) the final ERC delta table and netlist_diff summary (re-run them yourself and paste), (6) a verdict on the Phase-1 exit criteria (brief §10) and what layout (the next phase) must pick up. Keep it factual; no padding. Return summary + the exit-criteria verdict.

LENS SCOPES: ${JSON.stringify(reviews.filter(Boolean).map(r => ({ lens: r.lens, scope: r.scope_checked })), null, 2)}
FIX LIST: ${JSON.stringify(fixlist, null, 2)}
FIX RESULTS: ${JSON.stringify(fixResults, null, 2)}
FINAL CHECK: ${JSON.stringify(check, null, 2)}
REFUTED: ${JSON.stringify(refuted.map(r => ({ id: r.finding.id, title: r.finding.title, why: r.verdict.reasoning })), null, 2)}
`, { label: 'signoff:chair', phase: 'Confirm', model: M.signoff, effort: EFF(M.signoff), schema: { type: 'object', properties: { summary: { type: 'string' }, exit_criteria_met: { type: 'boolean' }, report_path: { type: 'string' }, for_hardware_lead: { type: 'array', items: { type: 'string' } }, for_layout_phase: { type: 'array', items: { type: 'string' } } }, required: ['summary', 'exit_criteria_met', 'report_path', 'for_hardware_lead', 'for_layout_phase'] } })

return {
  signoff,
  fixlist,
  fixResults,
  check,
  refuted: refuted.map(r => ({ id: r.finding.id, title: r.finding.title, lens: r.finding.lens, why: r.verdict.reasoning })),
  scopes: reviews.filter(Boolean).map(r => ({ lens: r.lens, scope: r.scope_checked })),
}
