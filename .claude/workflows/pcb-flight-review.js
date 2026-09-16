export const meta = {
  name: 'pcb-flight-review',
  description: 'Review KiCad schematic+layout for correctness, datasheet parity, spaceflight practice; verify; prioritize',
  whenToUse: 'Multi-stage design review of a KiCad project. args: {project, pcb, sch, scratch, heritage[], context}',
  phases: [
    { title: 'Review', detail: '6 finders: schematic/layout/spaceflight, Sonnet+Opus' },
    { title: 'Verify', detail: 'Opus skeptics, one per subsystem batch (<=6 findings)', model: 'opus' },
    { title: 'Prioritize', detail: 'Fable principal PCB + principal QA, then merge', model: 'fable' },
  ],
}

const A = args
const COMMON = `
You are reviewing a KiCad 10 hardware project. Return raw data only (structured output), no prose for humans.

PROJECT: ${A.project}
  Root schematic: ${A.sch}
  Sub-sheets: ${A.sheets.join(', ')}
  PCB (12 MB, ${A.footprints} footprints, 4-layer F.Cu/In1/In2/B.Cu): ${A.pcb}
  Project settings (design rules): ${A.pro}
PRE-GENERATED ARTIFACTS (use these, do not regenerate):
  ${A.scratch}/netlist.xml  (kicadxml netlist: components, fields, nets)
  ${A.scratch}/erc.json     (ERC, severity-all: ${A.ercSummary})
  ${A.scratch}/drc.json     (DRC, severity-all: ${A.drcSummary})
  ${A.scratch}/bom.csv      (grouped BOM)
  ${A.scratch}/pos.csv      (placement, mm, both sides)
kicad-cli if you need more exports: ${A.kicad}
HERITAGE / BASELINE (known-working, may diff against them): ${A.heritage.join(' ; ')}

CONTEXT FROM PRODUCT MANAGER:
${A.context}

HOW TO WORK:
- Files are large S-expressions. Use grep/awk/python to extract what you need; never cat the whole PCB.
- Datasheet parity: you may use WebSearch/WebFetch to pull manufacturer datasheets/app notes for the parts you check. Cite section/figure.
- Every finding needs concrete evidence: sheet+refdes+net or PCB coordinates/layer, plus what the datasheet or standard says. If you cannot point at evidence, do not report it.
- A "finding" is something that could plausibly cause a functional, reliability, manufacturability, or mission failure, or a clear deviation from a manufacturer recommendation. Cosmetic issues, style, library-metadata ERC noise (lib_symbol_issues, lib_symbol_mismatch, footprint_link_issues, endpoint_off_grid) are NOT findings unless they mask a real electrical problem.
- The board has flight heritage and environmental validation. Do not invent issues. Zero findings is an acceptable answer. Prefer 3 solid findings over 15 speculative ones.
- Set confidence honestly (0-1). Note if an item is new since the validated Rev1 baseline (e.g., the restored APS1604M PSRAM and its QSPI routing) vs inherited.
`

const FINDINGS = {
  type: 'object',
  properties: {
    scope_checked: { type: 'string', description: 'What you actually examined, briefly' },
    findings: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          title: { type: 'string' },
          area: { type: 'string', enum: ['schematic', 'layout', 'bom', 'spaceflight', 'manufacturing'] },
          severity: { type: 'string', enum: ['critical', 'major', 'minor', 'info'] },
          location: { type: 'string', description: 'sheet/refdes/net or layer+xy' },
          description: { type: 'string' },
          evidence: { type: 'string', description: 'exact values/lines/coords observed' },
          reference: { type: 'string', description: 'datasheet section, app note, standard, or best-practice source' },
          recommendation: { type: 'string' },
          new_since_baseline: { type: 'boolean' },
          confidence: { type: 'number' },
        },
        required: ['title', 'area', 'severity', 'location', 'description', 'evidence', 'recommendation', 'confidence'],
      },
    },
  },
  required: ['scope_checked', 'findings'],
}

const DIMENSIONS = [
  { key: 'sch-correctness', model: 'sonnet', prompt: `
DIMENSION: Schematic electrical correctness.
Check: net connectivity sanity from netlist.xml (floating inputs, unconnected enables/resets, pull-up/pull-down presence and values, power pins on the right rails, voltage-domain mismatches between 3V3/5V/VBAT/1V1 logic, I2C address conflicts on shared buses incl. behind the TCA9548A mux, SPI/QSPI CS assignments, RP2350 GPIO usage conflicts, USB D+/D- and VBUS handling, RUN/BOOTSEL circuit). Triage the 11 ERC errors (power_pin_not_driven, pin_not_connected) and the multiple_net_names / same_local_global_label warnings: which are real, which are noise? Compare against ${A.heritage[0]} to spot unintended changes in Rev2.` },
  { key: 'sch-datasheet-power', model: 'opus', prompt: `
DIMENSION: Schematic vs datasheet parity — POWER PATH.
Parts: LT3652 (solar MPPT charger), LT8610AB (buck), TPS54226 (buck), TPS2HB50-Q1 and TPS4H160-Q1 (high-side switches), AP22652 load switches, INA219 monitors, Schottky ORing, battery/coin-cell path, inhibit/deploy switch circuits. For each: compare feedback divider values, compensation, input/output capacitance and type, inductor value/saturation vs peak current, sense resistor values, enable/UVLO thresholds, timing/fault pins, diagnostic pin pull-ups, and thermal/derating assumptions against the datasheet typical application. Report only deviations that matter or missing datasheet-required components.` },
  { key: 'sch-datasheet-digital', model: 'opus', prompt: `
DIMENSION: Schematic vs datasheet parity — DIGITAL / RF / SENSORS.
Parts: RP2350 (60QFN: decoupling per rail, 1V1 core reg inductor/caps, crystal load caps and series R vs RP2350 datasheet + hardware design guide, USB, QSPI_SS pull, RUN), W25Q128JVS flash and APS1604M PSRAM on QSPI (CS assignment, pull-ups, 3.3V compatibility, PSRAM CS on a GPIO the RP2350 supports for XIP CS1), RV-3028-C7 RTC (backup supply, EVI, INT), LSM6DSO + LIS2MDL (supply pins, CS/SDO/SA0 strapping, I2C mode selection), MCP23017, TCA9548A (reset pull-up, address pins), TLV1704 comparators in the watchdog sheet (hysteresis, thresholds, open-drain pull-ups), E22-400M30S / E28-2G4M27S radio modules (supply current vs regulator, TX/RX enable pins, antenna path, MMCX). Report only deviations that matter or missing datasheet-required components.` },
  { key: 'layout-correctness', model: 'sonnet', prompt: `
DIMENSION: PCB layout correctness and manufacturability.
Triage drc.json fully: the 39 clearance errors, 1 courtyard overlap, 4 isolated_copper, 1 track_dangling, 7 footprint_type_mismatch. For each class, determine if it is a real fab/assembly risk given the JLCPCB 4-layer rules in the .kicad_pro, or an accepted artifact. Then check: footprint/pad correctness for the new APS1604M PSRAM (pad pitch vs datasheet, courtyard), QSPI trace routing to flash and PSRAM (length, layer changes, stubs, return path), via-in-pad, thermal reliefs on high-current pads, silkscreen over pads, mounting hole keepouts, connector pin-1 orientation, board outline/edge clearance. Use python to parse the PCB S-expression if helpful.` },
  { key: 'layout-datasheet', model: 'opus', prompt: `
DIMENSION: PCB layout vs datasheet layout recommendations.
For LT3652, LT8610AB, TPS54226, TPS2HB50-Q1/TPS4H160-Q1, AP22652, RP2350, crystal, USB-C, radio modules/MMCX: check placement and routing against each datasheet's layout guidelines — input cap loop area at switchers, SW node size/layer, feedback trace routing away from SW/inductor, inductor placement, exposed pad via stitching and thermal path to inner/bottom planes, decoupling cap proximity to the pin it serves (measure from pos.csv and pad coordinates), crystal guard/ground and trace length, USB differential pair routing/impedance-ish on this stackup, RF trace from module to MMCX (width vs 50 ohm on 0.21 mm prepreg to In1, ground fence, no plane cuts), ground plane continuity under sensitive paths, high-current path copper width vs current (use IPC-2221 estimate). Report only material deviations.` },
  { key: 'spaceflight', model: 'opus', prompt: `
DIMENSION: Spaceflight / CubeSat environment best practices (LEO, small-sat class, commercial parts).
Evaluate against widely accepted guidance (NASA-STD-8739.x workmanship intent, ECSS-Q-ST-70 family intent, GSFC EEE-INST-002 derating tables, IPC-2221/6012 class 3 intent, CubeSat Design Spec inhibit requirements). Check: derating of capacitors (voltage margin, esp. ceramics on battery/solar rails; tantalum/electrolytic presence and their vacuum suitability), resistor power derating, MLCC size vs thermal-cycle cracking risk (1210 on flex points), outgassing-relevant parts (connectors, LEDs, coin-cell holder, any plastic), single-event-latchup exposure on the power path (is there current limiting/watchdog power-cycle capability to clear SEL? check the watchdog sheet and load switches), reset/brown-out behavior and watchdog independence from the MCU, inhibit switch topology vs CDS requirements (series inhibits, deploy switches on battery ground/positive), connector retention (Picolock/DF11/Molex — locking vs friction), test point provision for ATP, tin whisker considerations (finish notes if any), thermal path for hot parts in vacuum (no convection), trace/via redundancy on critical power nets. Do not penalize the design for using COTS parts; that is the mission class. Only report gaps that create real mission risk.` },
]

phase('Review')
log(`Review: ${DIMENSIONS.length} finders`)
const reviews = await parallel(DIMENSIONS.map(d => () =>
  agent(COMMON + d.prompt, { label: `review:${d.key}`, phase: 'Review', model: d.model, effort: 'high', schema: FINDINGS })
    .then(r => r && { ...r, dim: d.key })))

const all = reviews.filter(Boolean).flatMap(r => r.findings.map(f => ({ ...f, dim: r.dim })))
const key = f => (f.location + '|' + f.title).toLowerCase().replace(/[^a-z0-9|]/g, '').slice(0, 80)
const seen = new Map()
for (const f of all) { const k = key(f); if (!seen.has(k)) seen.set(k, f) }
let findings = [...seen.values()]
log(`Review done: ${all.length} raw findings, ${findings.length} after dedup`)
const CAP = 40
if (findings.length > CAP) {
  const order = { critical: 0, major: 1, minor: 2, info: 3 }
  findings.sort((a, b) => order[a.severity] - order[b.severity] || b.confidence - a.confidence)
  log(`Capping verification at ${CAP}; dropping ${findings.length - CAP} lowest-severity items: ` + findings.slice(CAP).map(f => f.title).join('; '))
  findings = findings.slice(0, CAP)
}

if (findings.length === 0) {
  return { findings: [], reviews: reviews.map(r => r && r.scope_checked), note: 'No findings reported by any finder.' }
}

const BATCH_VERDICTS = {
  type: 'object',
  properties: {
    verdicts: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          id: { type: 'integer', description: 'the finding id you were given' },
          verdict: { type: 'string', enum: ['confirmed', 'refuted', 'uncertain'] },
          severity_adjusted: { type: 'string', enum: ['critical', 'major', 'minor', 'info'] },
          evidence_checked: { type: 'string' },
          reasoning: { type: 'string' },
          corrected_description: { type: 'string', description: 'If partly right, restate the finding accurately' },
          duplicate_of: { type: 'integer', description: 'id of another finding in this batch this one duplicates, if any' },
        },
        required: ['id', 'verdict', 'severity_adjusted', 'evidence_checked', 'reasoning'],
      },
    },
  },
  required: ['verdicts'],
}

// Group findings into subsystem batches so one verifier loads a datasheet/sheet once and checks all related items.
findings.forEach((f, i) => { f.id = i + 1 })
const SUBSYS = [
  ['power-charger-buck', /lt3652|lt8610|tps54226|buck|charger|mppt|solar|inductor|vbat|battery|feedback|fb\b|sw node|switcher/i],
  ['power-switches-monitor', /tps2hb50|tps4h160|ap22652|load switch|high-side|ina219|shunt|sense|inhibit|deploy|burn/i],
  ['mcu-memory', /rp2350|qspi|psram|aps1604|w25q|flash|crystal|xin|xout|1v1|bootsel|run\b|usb/i],
  ['sensors-io', /lsm6|lis2mdl|rv-3028|rtc|mcp23017|tca9548|i2c|imu|mag/i],
  ['radio-rf', /e22|e28|radio|mmcx|antenna|rf\b|50 ?ohm|lora/i],
  ['watchdog', /watchdog|tlv1704|comparator/i],
]
const bucket = f => {
  const text = `${f.title} ${f.location} ${f.description}`
  const hit = SUBSYS.find(([, re]) => re.test(text))
  return `${hit ? hit[0] : 'general'}/${f.area}`
}
const groups = new Map()
for (const f of findings) { const b = bucket(f); if (!groups.has(b)) groups.set(b, []); groups.get(b).push(f) }
const MAX_PER_BATCH = 6
const batches = []
for (const [name, fs] of groups) for (let i = 0; i < fs.length; i += MAX_PER_BATCH) batches.push({ name, items: fs.slice(i, i + MAX_PER_BATCH) })
log(`Verify: ${findings.length} findings in ${batches.length} batches: ` + batches.map(b => `${b.name}(${b.items.length})`).join(', '))

phase('Verify')
const batchResults = await parallel(batches.map(b => () =>
  agent(COMMON + `
ROLE: Independent skeptical verifier for the "${b.name}" subsystem. Reviewers reported the ${b.items.length} findings below (all related to this subsystem). For EACH finding, try to REFUTE it by going to the source files, netlist, DRC/ERC output, and the actual manufacturer datasheet (fetch it once, reuse for all items). Reproduce the evidence yourself; do not trust the reviewer's numbers. Consider whether the item is an accepted, heritage-validated design choice rather than a defect (diff against the Rev1 baseline). If you cannot reproduce the evidence, verdict = refuted. If evidence holds but impact is overstated/understated, verdict = confirmed with adjusted severity. Use "uncertain" only when the answer depends on information not in the repo or datasheet and say what is missing. Flag duplicates within the batch via duplicate_of. Return one verdict per id; do not skip any.

FINDINGS:
${JSON.stringify(b.items, null, 2)}
`, { label: `verify:${b.name}`, phase: 'Verify', model: 'opus', effort: 'xhigh', schema: BATCH_VERDICTS })
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
log(`Verify done: ${kept.length} confirmed/uncertain, ${refuted.length} refuted, ${verified.filter(isDup).length} merged as duplicates`)

const PRIORITIZED = {
  type: 'object',
  properties: {
    summary: { type: 'string' },
    items: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          rank: { type: 'integer' },
          title: { type: 'string' },
          severity: { type: 'string', enum: ['critical', 'major', 'minor', 'info'] },
          disposition: { type: 'string', enum: ['fix-before-flight', 'fix-this-rev', 'next-rev', 'accept-with-rationale', 'monitor-in-test', 'no-action'] },
          location: { type: 'string' },
          rationale: { type: 'string' },
          action: { type: 'string' },
          effort: { type: 'string', enum: ['trivial', 'small', 'medium', 'large'] },
          verification: { type: 'string', description: 'How to prove the fix / how ATP would catch it' },
        },
        required: ['rank', 'title', 'severity', 'disposition', 'location', 'rationale', 'action', 'effort'],
      },
    },
    dropped: { type: 'array', items: { type: 'string' }, description: 'Items you chose not to carry forward and why' },
  },
  required: ['summary', 'items'],
}

const packet = JSON.stringify({ kept, refuted: refuted.map(r => ({ title: r.finding.title, why: r.verdict.reasoning })) }, null, 2)

phase('Prioritize')
const PERSONAS = [
  { key: 'principal-pcb', role: `Principal PCB/hardware design engineer with 20+ years on mixed-signal power + RF boards and several CubeSat flight units. You weigh electrical risk, layout physics, and rework cost. You know heritage counts as evidence.` },
  { key: 'principal-qa', role: `Principal quality assurance / mission assurance engineer for small-satellite hardware. You weigh mission risk, derating margins, testability, traceability, and whether an item would be caught by ATP/environmental test. You distinguish "must fix" from "document the rationale and accept".` },
]
const drafts = await parallel(PERSONAS.map(p => () =>
  agent(COMMON + `
ROLE: ${p.role}
You receive verified review findings (with verifier verdicts and reasoning) plus the refuted list for context. Produce ONE prioritized list. Rank by mission risk x likelihood, then effort. Merge duplicates. Downgrade or drop anything the verifier showed to be heritage-accepted or low impact; say so in "dropped". Be concrete in actions (part value, net, coordinate). You may open the project files to settle any doubt. Do not add new findings of your own unless something in the packet makes one obvious.

PACKET:
${packet}
`, { label: `prioritize:${p.key}`, phase: 'Prioritize', model: 'fable', effort: 'xhigh', schema: PRIORITIZED })
    .then(r => r && { persona: p.key, ...r })))

const final = await agent(COMMON + `
ROLE: Review board chair. Two principals (PCB design, QA/mission assurance) each produced a prioritized list from the same verified findings. Merge them into a single final prioritized list. Where they disagree on severity or disposition, decide and state why in rationale. Keep the list short and actionable. Preserve their "dropped" reasoning in your dropped list.

PCB PRINCIPAL:
${JSON.stringify(drafts[0], null, 2)}

QA PRINCIPAL:
${JSON.stringify(drafts[1], null, 2)}
`, { label: 'merge:review-board', phase: 'Prioritize', model: 'fable', effort: 'xhigh', schema: PRIORITIZED })

return {
  final,
  personas: drafts,
  verified: kept,
  refuted: refuted.map(r => ({ title: r.finding.title, dim: r.finding.dim, why: r.verdict.reasoning })),
  scopes: reviews.filter(Boolean).map(r => ({ dim: r.dim, scope: r.scope_checked })),
}
