# Owner rulings 2026-10-21 (Michael), closing HANDOFF_2026-09-24 §3

| # | Item | Ruling |
|---|---|---|
| F15 | attachment_check zone-fill test | **Accepted.** A heritage-zone fill change inside the flight section is reported as a WARNING by `tools/pcb/attachment_check.py`, not a violation. `heritage.py check --refill --core-inset 12 --ref-board FC_V5e_Production_Rev2` stays the fill gate (core must be identical). Reason: any genuinely refilled board fails the old test because the 37 stubs carve the band; production must refill. |
| F16 | Via-in-pad (45 centred + ~18 pad-edge vias from routing rounds 1-3) | **Option (a).** Move them off-pad (dogbone) starting from `routed_r3/`. Any via that genuinely cannot move is ordered filled-and-capped (POFV) at JLC and listed by refdes/net with the reason. |

The F15 edit to `attachment_check.py` is the owner's gate change, made at the owner's direction.
