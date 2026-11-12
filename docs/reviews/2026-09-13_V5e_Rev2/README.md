# FC V5e Production Rev2 pre-order review, 2026-09-13

Multi-agent design and supply-chain review of `FC_V5e_Production_Rev2` before the JLCPCB order. Branch `v5e-rev2`, commits `ef211d6` through `4b1cbc6`.

| File | What |
|---|---|
| [RETRO.md](RETRO.md) | What we did, what went well, what went wrong, lessons |
| [design_review.md](design_review.md) | Final prioritized list from the review workflow, plus refuted and dropped items with reasoning |
| [supply_chain_report.md](supply_chain_report.md) | JLCPCB stock check of every LCSC assignment, risk register, alternates |
| [rtc_trade_study.md](rtc_trade_study.md) | RV-3028-C7 sourcing vs RV-3032-C7 migration |
| [u2_sdnand_study.md](u2_sdnand_study.md) | ZDSD04GLGEAG replacement study, 2 Gb Zetta chosen for Rev2 |
| [img/](img/) | Board renders and screenshots from the session |

The review workflow script is at [`.claude/workflows/pcb-flight-review.js`](../../../.claude/workflows/pcb-flight-review.js). Repo-level lessons and the review procedure are in [`CLAUDE.md`](../../../CLAUDE.md).

## Order configuration

- Stackup JLC04161H-7628 (0.2104 mm prepreg, 1.065 mm core) — RF traces were tuned to this
- 4-wire Kelvin test
- Solvent-based board cleaning
- No conformal coating (in-house after ATP)
- L3, J12, and all DF11 connectors rotated 180° in the JLC viewer; plugin corrections table updated so future exports are correct
