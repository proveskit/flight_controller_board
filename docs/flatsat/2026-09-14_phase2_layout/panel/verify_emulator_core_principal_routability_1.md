# Verify pass — emulator_core — principal (routability) — relaunch run

Role: skeptic/refuter. Board: scratch copy of v2.2 (project/FlatSat_V1.kicad_pcb), unchanged from prior run.
Method: re-pulled exact pad coordinates via pcbnew for R703/R704/J701/J703/U200/U511/C204/C206/C209/C212/C213/C216/C217/C219/C511/C512/C516; cross-checked against principal_prior_measurements.md; 1 WebFetch to JLCPCB capability page for via cost tier.

## PLR-04 — USB pair fans out to 1.8mm at R703/R704 — VERDICT: downgraded (minor -> note)

Re-measured directly: R703.1 x=272.845, R704.1 x=274.645 (pitch 1.800mm, matches). U200 pin52 (EMU_USB_DP) x=273.545, pin51 (EMU_USB_DM) x=273.945 (0.400mm, matches). J701 A6/A7 x=274.750/275.250 (0.500mm, matches). Net order D+ west-of-D- preserved at all three points (272.845<274.645; 273.545<273.945; 274.750<275.250) — no crossing, confirmed.

This is not a placement defect, it is an ordinary series-resistor taper on a full-speed (12 Mbit/s) USB pair — a length- and skew-matched (0.04mm skew), single, monotonic taper over ~2mm of y, which any KiCad diff-pair router handles as a standard "uncoupled length" segment, not a "complex manoeuvre" (owner priority 3 wording). The 0.25mm coupled-pair class only needs to hold from J701 to the resistors and resistors to U200 (already true — this is exactly how series-termination pairs are always laid out: coupled up to the resistor, then a short single-ended run to the driver).

Checked the finding's own recommended fix: moving R703 to x=273.60 / R704 to x=274.40 (0.80mm pitch) leaves only 0.80-0.54(pad width)=0.26mm edge-to-edge between the two resistor pads, against the design's own USB_EMU 0.25mm-clearance class — a 0.01mm margin, tighter than what exists today and a fab-risk for no measurable electrical gain at FS speeds. Recommend NOT moving the parts.

**Verdict: downgraded, note.** Confirmed measurement, refuted the "fix it now" framing — it is routine, not a blocker to a clean, non-manoeuvring route, and the suggested move trades an imaginary problem for a real (if small) clearance risk. Confidence 0.85.

## PLR-08 — Default via doesn't fit U200/U511 escape rings — VERDICT: downgraded (major -> minor)

Independently re-derived one of the tightest cited numbers from raw pad geometry (not reused from prior file): U200 pad60 (EMU_QSPI_SS, size 0.200x0.875, center y=91.4175) top edge y=90.980; C212.2 (GND, size 0.560x0.620, center y=90.150) bottom edge y=90.460. Gap = 0.520mm — matches PRIOR's cited 0.520mm exactly. Also recounted the "13 wide alleys" claim from the raw N/S/W/E alley lists in principal_prior_measurements.md: N{0.890,0.895,1.160,0.905}=4, S{0.890,0.900,0.900}=3, W{0.890,0.890}=2, E{0.980,0.935,0.900,0.900}=4 → 13. Exact. The underlying measurements are reproduced and correct.

Where the finding overreaches is severity and scope. PM decisions (COMMON) already state "capacitors against the pin they serve may sit below 0.5mm courtyard gap" — the tight cap-to-QFN placement causing this via squeeze is the PM-approved, manufacturer-guideline-driven placement (176/176 audit PASS), not a defect. The finding's own recommendation is "no part moves needed" — it is purely a via-size/netclass choice for routing stage, and the review brief's scope rule says not to report routing-stage items unless the placement makes routing impossible. It does not: at least one legal via (0.4/0.2, needs 0.654mm clearance) fits in every alley identified, and the min annulus pads (15 of them) still escape sideways into the 13 wide alleys before via-ing down, exactly as the finding's own recommendation lays out.

Fetched JLCPCB's capability page directly: standard via is 0.15mm hole/0.25mm pad; a 0.2mm hole with pad <0.45mm "will cost more" but works on standard 4-layer, no HDI/blind-via needed. So the recommended 0.45/0.20 escape via is fabricable, just a minor line-item cost adder, not a capability risk (owner priority 2, manufacturability, is not threatened).

**Verdict: downgraded, minor.** Confirmed the geometry and alley counts exactly; refuted "major/must-change-before-routing" because it changes no placement (part positions untouched), doesn't block a legal via from fitting, and the tight geometry it complains about is a PM-endorsed, audit-passed placement outcome. Recommend carrying the finding forward as a *routing-stage* note: add a local 0.45/0.20 (or smaller) via override netclass for the U200/U511 escape rings before routing starts (not before placement is finalized), route the 15 tight pads (QSPI 57-60, 17-21, 29, 30, 46) sideways into the 1.160mm/0.905mm/0.900mm alleys first, and budget the JLCPCB small-via cost adder. Confidence 0.8.

## Summary
0 blockers confirmed at major+ severity in this pass. Both findings' *measurements* hold up under independent re-derivation; both were mis-scoped as placement-blocking when they are routing-stage housekeeping items with zero placement consequence, consistent with PM decisions already on record.
