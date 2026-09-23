# Verification — bench_io_cable — principal (routability) findings

Board checked: `.../panel/project/FlatSat_V1.kicad_pcb` (scratch copy of v2.2), read-only, via pcbnew.
Scripts: `panel/bench_io_cable_routability/verify1.py`, `verify2.py`.

## PLR-03 — J701 D+/D- links geometrically forced to a via inside the pad field

**Verdict: REFUTED (as stated) — geometry is real, but the cited rule does not govern this segment.**

Re-measured on-board (verify1.py), exact match to the finding's evidence:
- A6 (274.750,50.075) net `Net-(J701-D+-PadA6)`; B6 (275.750,50.075) same net.
- A7 (275.250,50.075) / B7 (274.250,50.075) net `Net-(J701-D--PadA7)`.
- Adjacent pad-edge gap = 0.500 pitch − 0.300 pad width = **0.200 mm**, less than the 0.381 mm a Default-class 0.127 mm track + 2×0.127 mm clearance needs. The interleave and the geometric block are confirmed.

But the finding's rule citation is wrong. `.kicad_pro` `net_settings` on this board defines **only** the `Default` class (0.2 clearance / 0.25 track / via 0.8/0.4) — no `USB_EMU`, `BenchPower`, etc. classes exist yet (`net_settings.classes` = `[Default]`, `netclass_patterns` = `[]`). The brief's L5 row (00_pm_brief.md line 38) is explicit that `USB_EMU` (0.25 mm, coupled, no-vias-if-avoidable) is scoped to **`EMU_USB_DP`/`EMU_USB_DM` only** — traced with verify2.py: those net names exist only on the **R703/R704-to-U200** segment (R703.2/R704.2 at (272.845/274.645, 89.61), 1.938 mm from U200, per placement_bench_io_cable.md row 2). The J701 pad-field segment carries **`Net-(J701-D+-PadA6)`/`Net-(J701-D--PadA7)`** — a distinct, differently-named net upstream of R703/R704 — which per L5's own text falls into "everything else... Default." The no-vias constraint therefore never applies at J701's pad field; ordinary vias there are unrestricted Default-class routing, exactly like the FC's own heritage J12 (same HRO part), which the finding's own evidence cites as already using 0.80/0.40 vias in this identical geometry. There is no rule conflict to flag, and J701 is a fixed anchor (placement_bench_io_cable.md §5) so no placement move is available or needed anyway.

**Recommendation:** No placement or netclass-note change required. If anything, clarify in floorplan_v2.md/00_pm_brief.md L5 that `USB_EMU` begins at R703/R704, not at J701, to prevent a router or a future reviewer making the same misattribution. This is a documentation-clarity note, not a routability blocker.
**Confidence: 0.85**

## PLR-05 — J703 placed north of U200 against its signals' exit sides

**Verdict: DOWNGRADED — congestion measurement holds, but the recommended fix (move/rotate J703) is disallowed by an already-passed gate; redirect to a routing-stage note.**

Re-confirmed on-board (verify1.py): J703 pos (270.795, 74.765), rot 0°, matches placement_bench_io_cable.md §5 exactly; U200 pos (273.145, 94.855). The 119-incidence crossing count, the pin-side table (pins 19/27/28/29 south, 32/33 east — all opposite J703), and the free-lane measurements at y=100.5/106.0/110.0 and x=281.5/293 are all carried from `principal_prior_measurements.md` and are internally consistent; I did not need to re-run the crossing/lane scan (WORKING LIMITS: reuse prior measurements) and have no reason to doubt them.

The problem is the recommendation, not the measurement. `J703` is one of five **fixed anchors** for this block (J701/J702/J703/SW701/SW702), gated explicitly under Brief PLACEMENT CONSTRAINT (b) "Fixed anchors do not move or rotate" — checked and passed identical, position/rotation/side, across every fix round of `placement_bench_io_cable.md` (§2 row 7, §5). This gate was accepted by the owner as part of v2.2 (176-rule audit, 0 failed). PM standing rule: fixed-anchor placement is not to be re-litigated absent a measured reason — but "measured reason" here would have to justify *breaking an owner-accepted, already-passing hard gate*, which a crossing-count/wrap-length argument does not meet (that's a routing-quality argument, not a placement-illegality one: nothing about the current position makes routing impossible, only longer/more mundane). Rotating or relocating J703 at this stage is out of scope for a floorplan-review panel and would require re-opening §2 row 7/§5 of the accepted block doc.

The finding's own fallback (its last sentence) is the right disposition: keep J703 in place and route its eight signals on **In2** (largely empty over this area — no local passives besides C211 nearby, per the crossing-table evidence), accepting the ~20-25 mm wrap. That is a routing-stage layer-assignment note, not a blocking or major placement finding — it does not meet the panel's "blocker/major" bar since nothing here is unroutable or non-manufacturable.

**Recommendation:** Downgrade to **minor/note**: instruct the router to assign J703's eight nets (3V3_EMU, EMU_UART_TX/RX, EMU_GPIO_SPARE0/1, FC_RESET, USBBOOT, WDT_DISABLE) to In2 for their U200-side wrap, entering/exiting In2 via vias placed clear of the USB_EMU F.Cu corridor and clear of J701/C701 (west) — no via-in-pad on U200's fine-pitch QFN pads. No change to `detail/placement_bench_io_cable.md` (J703 stays a fixed anchor, unmoved) — this is a routing-order instruction, add it to the routing-stage brief rather than the placement checklist.
**Confidence: 0.7**
