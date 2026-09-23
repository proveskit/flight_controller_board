# Verification — bench_io_cable — principal_manufacturability (skeptic pass)

Board under review: scratch copy `.../panel/project/FlatSat_V1.kicad_pcb` (read-only). Reference (flown) board read-only: `FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb`. Footprint source: `Connector_USB.pretty/USB_C_Receptacle_HRO_TYPE-C-31-M-12.kicad_mod`.

## PLM-01 — J701 USB-C rotated 180°, mating opening faces into the board — blocker

**Re-measured independently via pcbnew, all numbers reproduce:**

- Footprint local geometry (from the `.kicad_mod` itself, not assumed): F.CrtYd four `fp_line`s give courtyard y = **-5.27 .. +4.15** (asymmetric); pads A1/A12 at local `(±3.25, -4.045)` — pad row sits on the local **-Y** (deep, -5.27) side, confirming the finding's premise exactly. Two NPTH mounting legs at local y=-2.6 are on the same -Y side, reinforcing that -Y is the tail/solder side and +Y (shallow, no pads, no legs) is the mating-slot side.
- J701 on the board: pos (275.000, 54.120) rot 0°, F.Cu. Measured courtyard bbox y = **48.825 .. 58.295** (matches local -5.27/+4.15 off center 54.12 to within footprint origin rounding). Pad A1 at y=50.075, i.e. north of centre — pad/deep side is the **north** side.
- North board edge near J701: Edge.Cuts segment y = 47.529–47.629 (centre 47.579) — matches the finding exactly.
- Gap from courtyard north (48.825) to board edge (47.579) = **1.246 mm**, and it is the **deep/pad side** that is near the edge, so the shallow/mating (+4.15) side faces **south, into the board interior**. This reproduces the finding's central claim without relying on its numbers — independently derived from the raw courtyard/pad geometry.

**Cross-check against the flown reference (J12, FC_V5e_Production_Rev2.kicad_pcb, read-only):**

- J12: pos (223.16, 78.60), rot -90°, B.Cu. Courtyard bbox x = 217.865..227.335 (asymmetric, same -5.27/+4.15 split rotated onto X). Pads (A1/A12/S1) all at x=219.115, i.e. on the **217.865-side (deep/-Y-local)** — the west side, away from the board edge.
- Edge.Cuts near J12: vertical segment x=227.45..227.55, y 62.45..127.79 (the FC's real right-hand edge). Gap from J12 courtyard's shallow/non-pad side (227.335) to this edge (227.5) = **0.165 mm** (finding quoted 0.145 mm from the same reference — same order, small variance is footprint-origin vs board-edge-centreline rounding, not a substantive discrepancy).
- So on the one connector of this exact footprint that is flown and known to work, the **shallow/non-pad (mating) side is the side placed near the board edge**, 0.165 mm off it — and the pad side sits ~8.2 mm into the board interior. J701 has this reversed: its deep/pad side is 1.246 mm from the edge and its mating side points ~4–10 mm further into the board interior instead. **Confirmed independently, not just re-derived from the reviewer's own numbers.**

**Recommendation, re-checked:**
- Proposed fix (275.000, 51.874) rot 180°: recomputing the courtyard from the local ±5.27/4.15 split with the axes flipped: shallow side → north = 51.874 − 4.15 = **47.724** (0.145 mm off the 47.579 edge — reproduces the FC's own J12 offset almost exactly, as claimed). Deep side → south = 51.874 + 5.27 = **57.144** (matches the recommendation's stated 57.14).
- Destination window (x 269–281, y 46–58) re-checked in pcbnew: **no other footprint origin falls in this window** — confirms it is otherwise empty, as claimed.
- One correction to the recommendation's own supporting number: the "clears R701/R702 by >2.3 mm" figure is off. R701/R702 courtyard bbox top = y 58.28. Gap from the new J701 courtyard south edge (57.144) to that = **1.14 mm**, not 2.3 mm (2.3–2.9 mm is roughly the distance to R701/R702's *pad centres*, not courtyard). 1.14 mm is still comfortably ≥ the 0.5 mm courtyard floor with no PM exception needed, so this does not change the verdict, but the recommendation text should say **1.14 mm**, not 2.3 mm, when it's carried into the block's placement doc.

**Verdict: CONFIRMED, severity blocker unchanged.** This is not a routing/silkscreen-stage issue — it is a placement error with an assembly/usability consequence (the emulator's only USB port would be physically unusable as placed) and is not covered by any PM decision in COMMON (fixed-anchor breach exception applies to *envelope* pokes, not to rotation being backwards; J701 is a fixed anchor for later rounds but this round's finding is about the anchor's own orientation being wrong to begin with, which the PM decisions never ruled on). Confidence 0.9 (up from reporter's 0.88 — both the footprint-local premise and the flown-reference cross-check independently reproduce without relying on the reporter's arithmetic).

**Recommendation to carry into `detail/placement_bench_io_cable.md`:** J701 → (275.000, 51.874) mm, rot 180°, F.Cu (unchanged layer). Correct the clearance citation to "R701/R702 courtyard clearance 1.14 mm (≥0.5 mm floor met)" rather than 2.3 mm. Flag for the router: J701's pad order is mirrored front-to-back by this rotation (A-row/B-row swap sides relative to the rest of the block), so R703/R704 (USB D+/D- series termination) and the CC1/CC2 pull-down nets to R701/R702 must be re-checked for which physical pad each lands on after the flip — no length/value change needed, just a footprint-pin re-verification before routing starts.
