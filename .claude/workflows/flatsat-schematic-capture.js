export const meta = {
  name: 'flatsat-schematic-capture',
  description: 'Capture KiCad sub-sheets from a PM brief: per-sheet implementer → skeptic verifier → fix loop, then one integrator folds them into the root and an independent checker confirms ERC/netlist exit criteria',
  whenToUse: 'Reusable schematic-capture stage. args: {project, root, rootUuid, brief, docs, scratch, kicad, baselineErc, baselineNetlist, sheets:[{key,file,name,uuid,page,refdes,model,section}], integrator:{model}, maxFixRounds, maxCheckRounds, context}',
  phases: [
    { title: 'Capture', detail: 'per sheet, no barrier: implement (model per sheet) → Opus skeptic → fix, up to maxFixRounds' },
    { title: 'Integrate', detail: 'one Opus agent: root sheet symbols, label promotions, project symbol lib, full ERC, connector trace' },
    { title: 'Check', detail: 'independent Opus checker re-runs the tools and judges the exit criteria; integrator fixes; repeat' },
  ],
}

const A = args
const MAX_FIX = A.maxFixRounds ?? 2
const MAX_CHECK = A.maxCheckRounds ?? 2

const COMMON = `
You are working on the PROVES FlatSat V1 KiCad 10 project. Return raw data only (structured output), no prose for humans.

PROJECT DIR:        ${A.project}
ROOT SCHEMATIC:     ${A.project}/${A.root}   (root uuid ${A.rootUuid})
PM BRIEF (the spec — read it completely before doing anything): ${A.brief}
DOCS DIR (reports go here): ${A.docs}
SCRATCH (reference PDFs, netlists, BOMs, upgraded reference schematics, symbol pantry): ${A.scratch}
  ${A.scratch}/refs/*.pdf, ${A.scratch}/refs/*.netlist.xml, ${A.scratch}/refs/bom/*.csv, ${A.scratch}/refs/upgraded/<board>/*.kicad_sch
  ${A.scratch}/pantry/INDEX.md and ${A.scratch}/pantry/*.sexp  (validated lib_symbols blocks)
  ${A.scratch}/baseline/FC_V5e_Rev2.pdf  (the whole FC schematic, rendered)
TOOLS (in ${A.project}/tools): kicad10_sch_primer.md, baseline/connector_nets.md, sch_lint.py, harness_erc.sh, erc_summary.py, netlist_diff.py, add_sheet_symbol.py, get_symbol.py
kicad-cli: ${A.kicad}
Baseline ERC / netlist (Rev2): ${A.baselineErc} / ${A.baselineNetlist}

HARD RULES (brief §3 — violating one fails the task): never touch FC_V5e_Production_Rev2/; one agent writes only its own files; write atomically (tmp + mv); schematic text notes are requirements; never write jlcpcb/project.db; nothing in series with a flight power path; no KiCad GUI; no git commit; strip every FC global label from any template you copy.
Use your own scratch subdirectory ${A.scratch}/work_<yourkey>/ for harness runs (SCRATCH=... env var to tools/harness_erc.sh) and generator drafts.
Datasheets: fetch them (WebFetch/WebSearch) when the brief asks you to confirm a fact; cite the section in your report.

CONTEXT FROM THE PRODUCT MANAGER:
${A.context}
`

const SHEET_RESULT = {
  type: 'object',
  properties: {
    key: { type: 'string' },
    sheet_path: { type: 'string' },
    report_path: { type: 'string' },
    generator_path: { type: 'string' },
    refdes_used: { type: 'array', items: { type: 'string' } },
    existing_nets_used: { type: 'array', items: { type: 'string' }, description: 'existing FC global nets this sheet connects to (exact names)' },
    new_nets_defined: { type: 'array', items: { type: 'string' } },
    new_nets_consumed: { type: 'array', items: { type: 'string' } },
    lcsc_missing: { type: 'array', items: { type: 'string' }, description: 'refdes/value pairs that still need an LCSC number' },
    lint_errors: { type: 'integer' },
    erc_errors_on_sheet: { type: 'integer' },
    erc_warnings_on_sheet: { type: 'integer' },
    warnings_summary: { type: 'string' },
    netlist_diff_summary: { type: 'string', description: 'which existing nets gained pins, how many components added' },
    deviations_from_brief: { type: 'array', items: { type: 'string' } },
    open_questions: { type: 'array', items: { type: 'string' } },
  },
  required: ['key', 'sheet_path', 'report_path', 'refdes_used', 'existing_nets_used', 'new_nets_defined', 'new_nets_consumed', 'lint_errors', 'erc_errors_on_sheet', 'erc_warnings_on_sheet', 'warnings_summary', 'netlist_diff_summary', 'deviations_from_brief', 'open_questions'],
}

const VERDICT = {
  type: 'object',
  properties: {
    pass: { type: 'boolean', description: 'true only if there are no blocker or major defects' },
    checks_run: { type: 'string', description: 'what you actually executed and read' },
    defects: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          title: { type: 'string' },
          evidence: { type: 'string', description: 'file/refdes/net/coordinate or tool output or datasheet section' },
          fix: { type: 'string', description: 'concrete instruction for the implementer' },
        },
        required: ['severity', 'title', 'evidence', 'fix'],
      },
    },
    notes: { type: 'string' },
  },
  required: ['pass', 'checks_run', 'defects'],
}

const INTEGRATION = {
  type: 'object',
  properties: {
    root_path: { type: 'string' },
    report_path: { type: 'string' },
    trace_path: { type: 'string' },
    sheets_integrated: { type: 'array', items: { type: 'string' } },
    labels_promoted: { type: 'array', items: { type: 'string' } },
    project_lib_symbols: { type: 'array', items: { type: 'string' } },
    erc_errors_total: { type: 'integer' },
    erc_errors_baseline: { type: 'integer' },
    erc_errors_attributable_to_new_sheets: { type: 'integer' },
    erc_warnings_new: { type: 'integer' },
    warnings_triage: { type: 'string' },
    netlist_check: { type: 'string', description: 'result of netlist_diff vs baseline: lost pins? renames? additions?' },
    fixes_applied: { type: 'array', items: { type: 'string' }, description: 'cross-sheet problems you found and fixed (and in which file)' },
    open_issues: { type: 'array', items: { type: 'string' } },
  },
  required: ['root_path', 'report_path', 'trace_path', 'sheets_integrated', 'labels_promoted', 'erc_errors_total', 'erc_errors_baseline', 'erc_errors_attributable_to_new_sheets', 'erc_warnings_new', 'warnings_triage', 'netlist_check', 'fixes_applied', 'open_issues'],
}

const CHECK = {
  type: 'object',
  properties: {
    exit_criteria_met: { type: 'boolean' },
    erc_errors_total: { type: 'integer' },
    erc_errors_attributable_to_new_sheets: { type: 'integer' },
    netlist_baseline_preserved: { type: 'boolean' },
    trace_complete: { type: 'boolean' },
    discrepancies: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          title: { type: 'string' },
          evidence: { type: 'string' },
          fix: { type: 'string' },
        },
        required: ['severity', 'title', 'evidence', 'fix'],
      },
    },
    summary: { type: 'string' },
  },
  required: ['exit_criteria_met', 'erc_errors_total', 'erc_errors_attributable_to_new_sheets', 'netlist_baseline_preserved', 'trace_complete', 'discrepancies', 'summary'],
}

const sheetPath = s => `/${A.rootUuid}/${s.uuid}`

const implementPrompt = (s, prior, defects) => COMMON + `
ROLE: Implementer of ONE schematic sheet.
YOUR SHEET: key=${s.key}, file=${A.project}/${s.file}, Sheetname="${s.name}", sheet-symbol uuid=${s.uuid}, page ${s.page}, instances path "${sheetPath(s)}", refdes block ${s.refdes}. Specification: brief §${s.section}, interface contract brief §4, format/validation brief §7, deliverables brief §8.
${prior ? `\nYOU ALREADY PRODUCED A VERSION (${prior.sheet_path}, report ${prior.report_path}). An independent verifier found these defects; fix every one, re-run the full validation loop, update the report (append a "Fix round" section), and return the updated result:\n${JSON.stringify(defects, null, 2)}\n` : `
HOW TO WORK:
1. Read the brief completely, then tools/kicad10_sch_primer.md, tools/baseline/connector_nets.md, ${A.scratch}/pantry/INDEX.md, and the reference schematics/PDF/BOM the brief names for your sheet. Look at ${A.scratch}/baseline/FC_V5e_Rev2.pdf pages for the sheets you interface with.
2. Design first: write the parts list, net list and (for the emulator) GPIO map into your report skeleton before generating the sheet.
3. Generate the sheet with a Python generator saved at ${A.project}/tools/gen/${s.key}_gen.py (pantry blocks for lib_symbols; compute pin coordinates from the lib pin positions; wires end exactly on pins; every item on the 1.27 mm grid; fresh uuid4 everywhere; instances block per brief §5). Write atomically.
4. Validate per brief §7 until done: sch_lint (0 errors), tools/harness_erc.sh "${s.name}" (no ERC errors on your sheet, no new errors elsewhere, only single_global_label warnings for contract nets whose partner sheet is absent), netlist_diff shows only the existing nets §4 says you touch. Export the harness root to PDF and Read your page to check readability.
5. Write the report ${A.docs}/sheet_${s.key}.md per brief §8, with tool outputs pasted.
`}
Return the structured result. Be precise about erc/lint counts (copy them from tool output).`

const verifyPrompt = (s, result, round) => COMMON + `
ROLE: Independent skeptical verifier (round ${round}) for sheet "${s.name}" (${A.project}/${s.file}, spec brief §${s.section}). The implementer reported:
${JSON.stringify(result, null, 2)}

Try to REFUTE the claim that this sheet is done. Do not trust the report; reproduce everything:
- Run: python3 tools/sch_lint.py ${s.file} --project FlatSat_V1 --path ${sheetPath(s)} --refdes-block ${s.refdes} ; SCRATCH=${A.scratch}/work_verify_${s.key} tools/harness_erc.sh "${s.name}" ; then export the harness root to PDF (kicad-cli sch export pdf) and Read the page for this sheet.
- Compare the sheet against brief §${s.section} item by item, against the interface contract §4 (exact net names, which sheet defines vs consumes, pull-up rails, series resistors), against the hard rules §3, and against the reference design it copies (open the reference schematic in ${A.scratch}/refs/upgraded/ and diff part values, pin strapping, pull-ups, decoupling; a copied circuit with a changed value is a defect unless the report justifies it).
- Check electrical sanity yourself: power pins on the right rails, no path that back-powers an unpowered FC or emulator, no bench part that could raise a flight net, pin-to-pin ERC conflicts, unconnected inputs, address strapping, ERC power_pin_not_driven on new rails (PWR_FLAG present?), refdes inside the block and unique, footprints assigned and plausible for the LCSC part quoted, LCSC numbers traceable to the BOM CSVs in ${A.scratch}/refs/bom/ (a number not in any BOM and not verified is a defect).
- Fetch the datasheet for any part-specific claim in the report and check it.
Classify: blocker = wrong connectivity, hard-rule violation, ERC error, file will not load, contract net name mismatch; major = missing brief requirement, wrong value vs reference/datasheet, unverifiable LCSC, readability so poor a human cannot review it; minor = cosmetics, note wording. pass=true only with zero blocker/major. Report only what you can evidence. Zero defects is a valid answer.`

phase('Capture')
log(`Capture: ${A.sheets.length} sheets → implement → verify → fix (≤${MAX_FIX} rounds each)`)

const captured = await pipeline(
  A.sheets,
  s => agent(implementPrompt(s, null, null), { label: `implement:${s.key}`, phase: 'Capture', model: s.model, effort: s.model === 'opus' ? 'xhigh' : 'high', schema: SHEET_RESULT })
    .then(r => r && { ...r, key: s.key }),
  async (result, s) => {
    if (!result) { log(`${s.key}: implementer returned nothing`); return null }
    let current = result
    const rounds = []
    for (let round = 1; round <= MAX_FIX + 1; round++) {
      const v = await agent(verifyPrompt(s, current, round), { label: `verify:${s.key}#${round}`, phase: 'Capture', model: 'opus', effort: 'xhigh', schema: VERDICT })
      if (!v) { log(`${s.key}: verifier #${round} returned nothing; keeping current version`); rounds.push({ round, verdict: null }); break }
      const serious = (v.defects || []).filter(d => d.severity !== 'minor')
      rounds.push({ round, verdict: v })
      log(`${s.key}: verify #${round}: ${v.pass ? 'PASS' : 'FAIL'} — ${serious.length} blocker/major, ${(v.defects || []).length - serious.length} minor`)
      if (v.pass || serious.length === 0) break
      if (round > MAX_FIX) { log(`${s.key}: still failing after ${MAX_FIX} fix rounds; carrying defects forward to the review workflow`); break }
      const fixed = await agent(implementPrompt(s, current, v.defects), { label: `fix:${s.key}#${round}`, phase: 'Capture', model: s.model, effort: s.model === 'opus' ? 'xhigh' : 'high', schema: SHEET_RESULT })
      if (!fixed) { log(`${s.key}: fix #${round} returned nothing; keeping previous version`); break }
      current = { ...fixed, key: s.key }
    }
    return { sheet: s, result: current, rounds }
  },
)

const done = captured.filter(Boolean)
const missing = A.sheets.filter(s => !done.find(d => d.sheet.key === s.key)).map(s => s.key)
if (missing.length) log(`Capture: sheets with no result: ${missing.join(', ')}`)
log(`Capture done: ${done.length}/${A.sheets.length} sheets captured`)

phase('Integrate')
const integratorPrompt = (prior, discrepancies) => COMMON + `
ROLE: Integrator. You are the only agent allowed to edit ${A.root}, eps_side.kicad_sch, load_switches.kicad_sch, symbols/flatsat.kicad_sym and sym-lib-table. Specification: brief §4.3 (label promotions), §5 (sheet table: uuids, pages, placements), §9 (deliverables), §7 (tools).
SHEET RESULTS FROM THE IMPLEMENTERS (each verified by an independent skeptic; the rounds show what was found and fixed):
${JSON.stringify(done.map(d => ({ sheet: d.sheet, result: d.result, last_verdict: d.rounds[d.rounds.length - 1]?.verdict })), null, 2)}
${missing.length ? `SHEETS MISSING (no implementer result): ${missing.join(', ')} — integrate what exists, list the gap in open_issues.` : ''}
${prior ? `\nYOU ALREADY INTEGRATED ONCE (${prior.report_path}). An independent checker found these discrepancies; fix every one, re-run everything, update the reports, and return the updated result:\n${JSON.stringify(discrepancies, null, 2)}\n` : `
HOW TO WORK:
1. Read the brief §4, §5, §9 and each sheet report in ${A.docs}. Run tools/harness_erc.sh once to see the combined state before you change anything (it adds all six sheets to a scratch copy).
2. Add the six sheet symbols to the real root with tools/add_sheet_symbol.py (exact uuid/page/placement/size from brief §5; Sheetname/Sheetfile as in the table), plus a (text ...) title block near them: "PROVES FlatSat V1 additions — see docs/flatsat/2026-09-14_phase1_schematic/". Write atomically.
3. Promote the eight local labels (brief §4.3) on eps_side/load_switches: convert EVERY occurrence of each named local label on that sheet to a global_label with (shape passive) at the same anchor and rotation (grep first; use the primer's global_label sample for the format, including the hidden Intersheetrefs property). Check first that no sheet already has a global label or power symbol with that name.
4. Populate symbols/flatsat.kicad_sym with every "flatsat:*" symbol the new sheets embed (extract the lib_symbols blocks from the sheets; a .kicad_sym entry is the same block without the "flatsat:" prefix in its name; keep the file header (version 20251024)). Confirm the sym-lib-table entry exists.
5. Run full ERC on the real root (kicad-cli sch erc --severity-all --format json) and netlist export; use tools/erc_summary.py --baseline ${A.baselineErc} --ignore-noise and tools/netlist_diff.py ${A.baselineNetlist} <new>. Fix cross-sheet problems you find (duplicate refdes across sheets, a contract net spelled differently on two sheets, a rail with no driver, single_global_label that should have a partner) — you may edit a new sheet ONLY for such cross-sheet integration defects, and you must record each edit in fixes_applied and in the integration report. Existing FC nets must not lose pins; the eight promotions must appear as pure renames; everything else must be additions.
6. Triage every remaining non-noise ERC warning in the whole project (baseline ones vs new ones) in ${A.docs}/integration_report.md, with the netlist_diff output and the ERC delta table pasted.
7. Write ${A.docs}/connector_trace.md per brief §9: every FC connector pin (J1..J30, RF1, J12, J16, J18, J22 — use tools/baseline/connector_nets.md) → net → FlatSat destination (sheet + refdes, "unchanged: external connector kept", or "unpopulated"), and a second table of every promoted/new global net → sheets that carry it.
8. Export the whole project to PDF (${A.scratch}/work_integrate/FlatSat_V1.pdf) and Read the root page to confirm the six sheet symbols sit in free space (brief §5 placements were chosen for that) and nothing overlaps.
`}
Return the structured result with exact counts from tool output.`

let integration = await agent(integratorPrompt(null, null), { label: 'integrate:root', phase: 'Integrate', model: (A.integrator && A.integrator.model) || 'opus', effort: 'xhigh', schema: INTEGRATION })
if (!integration) log('Integrate: integrator returned nothing')

phase('Check')
const checks = []
for (let round = 1; integration && round <= MAX_CHECK; round++) {
  const c = await agent(COMMON + `
ROLE: Independent exit-criteria checker (round ${round}). The integrator reported:
${JSON.stringify(integration, null, 2)}
Do not trust it. Reproduce from scratch in ${A.scratch}/work_check_${round}/:
- kicad-cli sch erc --severity-all --format json on ${A.project}/${A.root}; tools/erc_summary.py with --baseline ${A.baselineErc} --ignore-noise, then --list for every error and for every new warning; attribute each error to a sheet (baseline sheets vs new sheets).
- kicad-cli sch export netlist --format kicadxml; tools/netlist_diff.py ${A.baselineNetlist} <new> --ignore-unconnected: any existing net that LOST a pin, any existing component changed, any net merge between two previously distinct FC nets = blocker. The eight promotions (brief §4.3) must appear as removed "/Power Systems/X" (or "/Power Systems/Load Switches/X") + added "X" with identical membership.
- Read ${A.docs}/connector_trace.md against tools/baseline/connector_nets.md: every connector pin present with a destination; spot-check five destinations against the actual sheets (grep the global label on the destination sheet).
- Read the root sheet's sheet blocks: six sheets, uuids/pages/files per brief §5; every Sheetfile exists; every new sheet's instances path uses the right sheet uuid (tools/sch_lint.py per sheet with --path).
- Cross-sheet contract: for every net in brief §4.2, grep which sheets carry it; a net defined but never consumed (or vice versa) is a major unless the brief says so.
- Read the plan's Phase-1 exit criteria (brief §10) and judge each.
Report discrepancies with evidence; exit_criteria_met=true only with zero blocker/major discrepancies.`, { label: `check:exit-criteria#${round}`, phase: 'Check', model: 'opus', effort: 'xhigh', schema: CHECK })
  if (!c) { log(`Check #${round}: checker returned nothing`); break }
  checks.push({ round, check: c })
  const serious = (c.discrepancies || []).filter(d => d.severity !== 'minor')
  log(`Check #${round}: ${c.exit_criteria_met ? 'EXIT CRITERIA MET' : 'NOT MET'} — ${serious.length} blocker/major, ${(c.discrepancies || []).length - serious.length} minor; ERC errors total ${c.erc_errors_total}, attributable to new sheets ${c.erc_errors_attributable_to_new_sheets}`)
  if (c.exit_criteria_met || serious.length === 0) break
  if (round === MAX_CHECK) { log(`Check: discrepancies remain after ${MAX_CHECK} rounds; carried to the review workflow`); break }
  const again = await agent(integratorPrompt(integration, c.discrepancies), { label: `integrate:fix#${round}`, phase: 'Integrate', model: (A.integrator && A.integrator.model) || 'opus', effort: 'xhigh', schema: INTEGRATION })
  if (!again) { log(`Integrate fix #${round}: returned nothing`); break }
  integration = again
}

return {
  sheets: done.map(d => ({ key: d.sheet.key, result: d.result, rounds: d.rounds.map(r => ({ round: r.round, pass: r.verdict && r.verdict.pass, defects: r.verdict && r.verdict.defects })) })),
  missing,
  integration,
  checks,
}
