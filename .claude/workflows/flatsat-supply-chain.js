export const meta = {
  name: 'flatsat-supply-chain',
  description: 'Supply-chain pass for the FlatSat Phase-1 sheets: one Sonnet agent per sheet fills LCSC/Datasheet fields from the JLCPCB parts database, a Sonnet skeptic re-verifies every number, then the board is re-synced',
  whenToUse: 'Phase-2 stage 1. args: {project, docs, netlist, partsDb, sheets:[{key,file,name,uuid,refdes}], kicadPy, scratch, context}',
  phases: [
    { title: 'Source', detail: 'per sheet: Sonnet fills LCSC + Datasheet on sheet and generator, regenerates, proves netlist unchanged' },
    { title: 'Verify', detail: 'Sonnet skeptic per sheet: every LCSC re-queried in the DB, package/value/footprint parity' },
    { title: 'Fix', detail: 'sheet owner applies verifier defects' },
    { title: 'Report', detail: 'one Sonnet writes supply_chain_report.md' },
  ],
}

const A = args
const COMMON = `
You are working on the PROVES FlatSat V1 KiCad 10 project. Return raw data only (structured output).

PROJECT DIR: ${A.project}
DOCS DIR:    ${A.docs}
PHASE-2 BRIEF (read §3 L9, §4 rules, and the Phase-1 brief §3 rule 5 it references): ${A.docs}/00_pm_brief.md
FINAL PHASE-1 NETLIST (kicadxml; the reference for "nothing but fields may change"): ${A.netlist}
JLCPCB PARTS DATABASE (sqlite, fts5; the kicad-jlcpcb-tools plugin's catalogue, refreshed 2026-09-13): ${A.partsDb}
  Table 'parts' (or as found — inspect the schema with sqlite3 first): columns include LCSC Part, First Category, Second Category, MFR.Part, Package, Solder Joint, Manufacturer, Library Type (Basic/Extended), Description, Datasheet, Price, Stock. Query with python3's sqlite3 module. Prefer Basic parts in stock; for a part the schematic already names by MPN, find that exact MPN; for generic passives pick the Basic part in the right package/tolerance/voltage; for connectors/headers pick the standard JLC Basic/Preferred part in the exact footprint (2.54 mm headers, 5.08 mm screw terminals).
TOOLS: ${A.project}/tools/get_symbol.py, sch_lint.py, harness_erc.sh, netlist_diff.py; generators in ${A.project}/tools/gen/<key>_gen.py regenerate each sheet (run them with the pantry at ${A.project}/tools/pantry — see tools/pantry/README.md); kicad-cli: /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli.
Use your own scratch dir ${A.scratch}/supply_<key>/ for exports.

HARD RULES: one agent, one sheet (+ its generator + its report); write atomically; never write jlcpcb/project.db; never open the KiCad GUI; no git commit; the netlist must not change except symbol fields (LCSC Part, Datasheet, Description, MPN): prove it with tools/netlist_diff.py against ${A.netlist} (0 added/removed/changed nets, 0 component value/footprint changes). Test points: follow the FC convention — no LCSC, and mark them exclude-from-BOM/position in the symbol only if the FC's own TP symbols do (check TP1..TP8 on the root sheet); otherwise leave as they are and say so. Never guess a number: every LCSC must come from the database query you ran (record the query and the row) or from a repo as-ordered BOM (cite the CSV line); anything unresolved stays blank and is listed.

CONTEXT: ${A.context}
`

const SHEET_RESULT = {
  type: 'object',
  properties: {
    key: { type: 'string' },
    filled: { type: 'array', items: { type: 'object', properties: { ref: { type: 'string' }, value: { type: 'string' }, footprint: { type: 'string' }, lcsc: { type: 'string' }, mpn: { type: 'string' }, lib_type: { type: 'string' }, stock: { type: 'integer' }, source: { type: 'string' } }, required: ['ref', 'value', 'lcsc', 'source'] } },
    reverified: { type: 'array', items: { type: 'object', properties: { ref: { type: 'string' }, lcsc: { type: 'string' }, ok: { type: 'boolean' }, note: { type: 'string' } }, required: ['ref', 'lcsc', 'ok'] } },
    still_blank: { type: 'array', items: { type: 'string' } },
    datasheet_urls_added: { type: 'integer' },
    netlist_diff_summary: { type: 'string' },
    files_changed: { type: 'array', items: { type: 'string' } },
    report_path: { type: 'string' },
  },
  required: ['key', 'filled', 'reverified', 'still_blank', 'datasheet_urls_added', 'netlist_diff_summary', 'files_changed', 'report_path'],
}

const VERDICT = {
  type: 'object',
  properties: {
    pass: { type: 'boolean' },
    checks_run: { type: 'string' },
    defects: { type: 'array', items: { type: 'object', properties: { severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, ref: { type: 'string' }, title: { type: 'string' }, evidence: { type: 'string' }, fix: { type: 'string' } }, required: ['severity', 'ref', 'title', 'evidence', 'fix'] } },
  },
  required: ['pass', 'checks_run', 'defects'],
}

const implement = (s, prior, defects) => COMMON + `
ROLE: Supply-chain owner of sheet "${s.name}" (${A.project}/${s.file}, refdes ${s.refdes}, generator ${A.project}/tools/gen/${s.key}_gen.py).
${prior ? `You already did a pass (report ${prior.report_path}). A verifier found these defects; fix each, re-run the proofs, update the report:\n${JSON.stringify(defects, null, 2)}` : `
HOW TO WORK:
1. List every symbol on your sheet with its Value, Footprint, LCSC Part (may be blank), MPN/Datasheet: parse the netlist XML (components with sheetpath names "/${s.name}/").
2. For each blank LCSC: query the parts database (inspect schema; use fts5 MATCH or LIKE on MFR.Part / Description / Package), choose per the rules above, record LCSC, MPN, package, Library Type, stock, price. For each existing LCSC: re-query it and confirm the row's package/value agree with the symbol (flag mismatches as defects to fix).
3. Apply the fields to the sheet through the generator (edit the generator's part table so a regeneration reproduces the sheet) and regenerate; if the generator cannot express a field, edit the sheet and mirror the change in the generator — both files must agree (regenerate into a scratch file and diff, uuid-stripped).
4. Prove: sch_lint 0 errors; tools/harness_erc.sh "${s.name}" no new errors; tools/netlist_diff.py ${A.netlist} <fresh netlist> → 0 net changes and 0 value/footprint changes (field-only).
5. Write ${A.docs}/supply_${s.key}.md: table per part (ref, value, footprint, LCSC, MPN, Basic/Extended, stock, price, source query/BOM line), unresolved parts with why, test-point handling, datasheet URLs added.`}
Return the structured result.`

const verify = (s, r) => COMMON + `
ROLE: Skeptical verifier for sheet "${s.name}" supply-chain data. The owner reported:
${JSON.stringify(r, null, 2)}
Reproduce independently: parse the current netlist of the project (export it yourself) for this sheet's components; for EVERY LCSC number present, query the parts database and check package ↔ footprint (0402/0603/0805/1210/SOT-23/SOT-323/SOIC-8/VQFN-24/…), value/tolerance/voltage ↔ Value field, MPN ↔ Value for named parts (R5460N208AA-TR-FE C259714, IRF7458 C10879, TCA4311ADGKR C130025, TMP112 C28927, VEML6031X00 C3678616, DRV2605LDGS C527464, RP2350A C42411118, W25Q128JVS C97521, ABM8-272-T3 C20625731, AP2112K-3.3 C51118, BQ25886RGE, SPM6530T-1R0M120 C87572, USB-C C165948, JST-SH C160389, KMR2 C72443, CDBA240LL-HF C2886093, PTC 2920L185DR C207086, BSS138, BAT54W, 2N7002 …), Basic vs Extended and stock. Confirm the generator regenerates the sheet (uuid-stripped diff 0) and that netlist_diff vs ${A.netlist} shows field-only changes. Any number not traceable to a DB row or BOM line = blocker. pass=true only with zero blocker/major.`

phase('Source')
log(`Supply chain: ${A.sheets.length} sheets, Sonnet owners`)
const results = await pipeline(
  A.sheets,
  s => agent(implement(s, null, null), { label: `source:${s.key}`, phase: 'Source', model: 'sonnet', effort: 'high', schema: SHEET_RESULT }).then(r => r && { ...r, key: s.key }),
  async (r, s) => {
    if (!r) return null
    let cur = r
    for (let round = 1; round <= 2; round++) {
      const v = await agent(verify(s, cur), { label: `verify:${s.key}#${round}`, phase: 'Verify', model: 'sonnet', effort: 'high', schema: VERDICT })
      if (!v) break
      const serious = (v.defects || []).filter(d => d.severity !== 'minor')
      log(`${s.key}: verify #${round}: ${v.pass ? 'PASS' : 'FAIL'} (${serious.length} blocker/major, ${(v.defects || []).length - serious.length} minor)`)
      if (v.pass || !serious.length) { cur = { ...cur, verdict: v }; break }
      if (round === 2) { cur = { ...cur, verdict: v, unresolved: true }; break }
      const f = await agent(implement(s, cur, v.defects), { label: `fix:${s.key}#${round}`, phase: 'Fix', model: 'sonnet', effort: 'high', schema: SHEET_RESULT })
      if (!f) break
      cur = { ...f, key: s.key }
    }
    return cur
  },
)

const done = results.filter(Boolean)
phase('Report')
const report = await agent(COMMON + `
ROLE: Supply-chain reporter. Six sheet owners and verifiers produced:
${JSON.stringify(done, null, 2)}
Write ${A.docs}/supply_chain_report.md in the style of ${A.project}/../docs/reviews/2026-09-13_V5e_Rev2/supply_chain_report.md: summary counts (filled / re-verified / still blank), risk register (Extended parts, low stock, single-source ICs: RP2350A, BQ25886, R5460N, TCA4311A, VEML6031, DRV2605L, IRF7458), alternates where the DB offers Basic equivalents, the test-point policy applied, and the list of parts still without a number with the reason. Then export a fresh netlist of the project (kicad-cli sch export netlist --format kicadxml) and count symbols in refdes 200-799 with/without an LCSC Part field; paste the count. Return {report_path, filled, blank, extended_count, risks}.`, { label: 'report:supply-chain', phase: 'Report', model: 'sonnet', effort: 'high', schema: { type: 'object', properties: { report_path: { type: 'string' }, filled: { type: 'integer' }, blank: { type: 'integer' }, extended_count: { type: 'integer' }, risks: { type: 'array', items: { type: 'string' } } }, required: ['report_path', 'filled', 'blank', 'extended_count', 'risks'] } })

return { sheets: done, report }
