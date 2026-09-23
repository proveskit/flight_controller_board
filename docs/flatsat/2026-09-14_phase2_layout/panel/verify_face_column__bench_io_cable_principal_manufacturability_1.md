# Verify panel — face_column, bench_io_cable — principal/manufacturability role 1

## PLM-12 — Bottom-side assembly and mounting-hole clearance both pass with margin

**Verdict: CONFIRMED (severity unchanged: note)**

Re-measured directly from pcbnew on the scratch board
(`/private/tmp/.../panel/project/FlatSat_V1.kicad_pcb`), cross-checked against
`facts.md`/`facts.json`:

- Mounting holes (footprint `MountingHole_3.2mm_M3_DIN965_Pad`, confirmed by FPID):
  H1 (147.300,138.000), H2 (227.300,138.000), H10 (292.390,51.580),
  H11 (292.390,168.120), H12 (147.300,168.120) — matches the finding's location
  string exactly.
- Actual nearest-part distances (pcbnew `GetPosition()`, mm, Euclidean):
  - TP701 (286.00, 53.50) → H10: **6.67 mm** (finding claimed 5.13 mm)
  - J4 (150.905, 130.79) → H1: **8.06 mm** (finding claimed 5.40 mm)
  - D15 (223.375, 131.375) → H2: **7.70 mm** (finding claimed 5.46 mm)
  - `facts.md` line 738 independently gives TP701 = (286.00, 53.50), i.e. it
    agrees with my pcbnew reading, not with the finding's quoted distances.
  - So the finding's three specific numbers are wrong (likely stale/transposed
    from an earlier board state), but the *direction* of the error only
    strengthens the conclusion: real margins are larger, not smaller.
  - `facts.md` "New parts within 3.5 mm of a mounting-hole centre" table is
    confirmed empty — no new part is within 3.5 mm of any hole centre.
- Clearance math (ISO 7045 M3 pan head, max head diameter 6.0 mm → 3.0 mm
  radius; standard M3 hex standoff ≈5–6 mm across corners, reused from
  `principal_prior_measurements.md`): with nearest part at 6.67 mm from a hole
  centre, spare clearance beyond the 3.0 mm head radius is **≥3.6 mm**, not the
  ">2 mm" the finding claims — still comfortably passes, with more margin than
  stated.
- Bottom-side parts vs. top-side stack: queried every F.Cu footprint within
  3 mm of U310/U312/U314 (B.Cu). Result: only C310, C312, C314 respectively,
  each at **0.00 mm** offset (i.e. placed back-to-back with their IC, standard
  decoupling-cap-behind-IC practice) — no connector or tall part sits over any
  of the three new bottom-side ICs. This exactly matches the finding's
  description.
- Bottom-side part count/process class: TCA4311A bottom placement adds no new
  process step — the FC already has 137 bottom-side parts assembled at JLCPCB
  (per project brief), so double-sided PCBA is already the baseline service
  tier for this board, not a new cost driver introduced by v2.2.

**Corrected recommendation:** No action needed; strengthen the note's cited
distances to the pcbnew-verified values above (6.67 / 8.06 / 7.70 mm) rather
than the original 5.13 / 5.40 / 5.46 mm, and keep the standing caveat: if
fiducials land near H11/H12 (per PLM-09), keep them ≥3.35 mm from the hole's
annular ring as well as from parts, per JLCPCB standard-PCBA fiducial rules
already cited in `principal_prior_measurements.md`.

**Confidence: 0.9** (measured directly from the scratch board via pcbnew;
JLCPCB double-sided-assembly and ISO 7045 figures reused from prior
measurements, not re-fetched, per the working-limits budget).
