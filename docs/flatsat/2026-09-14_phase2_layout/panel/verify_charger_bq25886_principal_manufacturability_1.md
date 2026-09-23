# Verification panel — charger_bq25886 — manufacturability skeptic

Board under review (read-only): scratch copy of v2.2 at
`/private/tmp/claude-501/.../scratchpad/panel/project/FlatSat_V1.kicad_pcb`.
Reference: `FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb` (heritage, read-only).

## PLM-04 — SOT-363 corrections.db mis-fire on U510 — REFUTED (out of scope for this panel)

Re-measured and the technical claim is correct:
- `sqlite3 corrections.db "SELECT * FROM correction WHERE regex LIKE '%SOT-363%'"` →
  `^SOT-363|180|0|0` — the rule exists exactly as described, 62 rows total in the table.
- U510's footprint on the board is literally named
  `SOT-363_L2.0-W1.3-P0.65-LS2.1-BR` (confirmed via pcbnew `GetFPID().GetLibItemName()`),
  which does match `^SOT-363`, so the regex will fire for this part.

So the evidence is reproducible and the mechanism is real. Refuting anyway, on scope:
this is a `jlcpcb-tools` **CPL/rotation-correction database** entry — it only affects the
position file generated when assembly data is exported for a JLCPCB order. It does not
touch the footprint's angle on the PCB (U510 sits at 0.0° on the board right now,
independent of this table), does not change any placement, and the finding's own
recommendation ("add a corrections.db row … check U510 in the JLC placement viewer on
the first order") requires no board edit at all. Per the panel's scope rule ("do not
report things that belong to routing/silkscreen stages unless the placement makes them
impossible" — CPL/assembly-file generation is even further downstream than routing),
this has zero placement consequence and belongs to the CPL-generation stage, not to a
floorplan review before routing.

**Verdict: refuted** (for this panel's purpose only — the underlying tooling bug is
real and worth fixing before the JLC order is placed, just not a layout finding).
**Severity: note.** Recommendation carried forward unchanged, tagged for stage 6+
(assembly-file generation), not for layout: add `^SOT-363_L2.0-W1.3-P0.65-LS2.1-BR|0|0|0`
to corrections.db (or anchor the generic rule with `^SOT-363$`) before CPL export, and
visually confirm U510 in the JLC placement viewer on the first order PCBA proof.
**Confidence: 0.85** (rule and footprint name both directly verified; scope call is a
judgment application of the panel's own stage-boundary rule).

## PLM-06 — J510 recessed 2.4 mm vs J12's 0.69 mm (flown) — REFUTED (fixed anchor, PM-locked)

Re-measured directly on both boards with pcbnew:

| quantity | finding claim | measured | 
|---|---|---|
| J510 F.Fab mating face (y) | 169.71 | 169.76 |
| South board edge (composite, x 147.3–292.4) | 172.120 | 172.120 (exact) |
| J510 body-to-edge | 2.41 | 2.36 |
| J510 F.Courtyard-to-edge | 1.87 | 1.885 |
| J510 min pad copper-to-edge | 4.210 | 4.210 (exact) |
| J12 B.Fab mating face (x, FC_V5e_Production_Rev2) | 226.81 | 226.86 |
| FC board edge at J12 (x, same file, edge segment 227.5,62.5→227.5,127.7) | 227.50 | 227.50 (exact) |
| J12 body-to-edge (as flown) | 0.69 | 0.64 |
| J12 B.Courtyard-to-edge | 0.145 | 0.165 |

All numbers reproduce within ≤0.05 mm (rounding from which fab-outline vertex the tool's
bbox picks up) — the measurement stands.

Refuting on PM-decision grounds, not measurement grounds. `blocks.json` for
`charger_bq25886` lists `"fixed_anchors": ["J510", "JP510"]`, and
`detail/placement_charger_bq25886.md` documents J510 as bit-for-bit unmoved across
rounds 3, 4 and 5 (lines 5, 25, 328, 364: "J510/JP510 unmoved (bit-for-bit, confirmed by
direct position read)"). This is exactly the class of decision the panel brief says not
to re-litigate without a measured functional reason ("PM decisions already taken … do
not re-litigate unless you have a measured reason"; "fixed-anchor envelope breaches are
not findings" — the same fixed-anchor deference applies to a fixed anchor's exact
placement, not only its envelope). The finding's own text concedes there is no mating
failure ("plugs still seat — 6.5 mm of shell against 2.41 mm of recess") — it is a
margin preference, not a usability break, and USB-C plug shells (6.5 mm typical, per
HRO TYPE-C-31-M-12 drawing already on file from the prior run) leave >4 mm of margin
even at the measured 2.36 mm recess.

**Verdict: refuted** (measurement correct; J510 is a PM-fixed anchor with no functional
mating failure — a preference for more margin isn't grounds to move a locked anchor five
rounds in). **Severity: note.** If the owner still wants the extra margin banked for a
future connector/boot change, that's a stage-6+ silkscreen/BOM-note item ("record J510's
reduced edge margin vs. flown J12 as a watch-item"), not a placement change now.
**Confidence: 0.8.**

## Summary

| id | verdict | severity |
|---|---|---|
| PLM-04 | refuted (out of scope: CPL-generation stage, no placement consequence) | note |
| PLM-06 | refuted (J510 is a PM-fixed anchor, no functional mating failure) | note |

Both findings' underlying measurements were reproduced and are numerically accurate;
neither survives as a layout-review action item for this panel.
