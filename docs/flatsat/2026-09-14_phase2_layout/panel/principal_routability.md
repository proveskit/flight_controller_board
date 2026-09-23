# Principal layout engineer — ROUTABILITY half — floorplan v2.2 pre-routing review

2026-09-19 (relaunch). Board measured: `scratchpad/panel/project/FlatSat_V1.kicad_pcb` (read-only scratch
copy). Scripts: `scratchpad/panel/principal_routability/r1.py … r9.py`. Prior-run measurements reused
from `scratchpad/panel/facts/principal_prior_measurements.md` (cited as PRIOR).

## A.1 — Fine-pitch escape (U200 / U511 / Q510)

**U200 RP2350 QFN-60**, pos (273.145, 94.855), pad 0.875 × 0.200 mm, pitch 0.400 mm
→ pad-to-pad edge gap **0.200 mm**. A 0.127 mm track at 0.127 mm clearance needs
0.127 + 2×0.127 = **0.381 mm**. **No track can pass between two U200 pads at any legal width.**
Escape is therefore purely radial: 15 pins per side, 45 signal pins, 15 power/GND.

Free annulus (nearest foreign F.Cu pad edge, PRIOR): min **0.520 mm** (pads 56–60 QSPI vs C212),
next band 0.540 mm (pads 17,18,19,20,21,29,30), median **1.030**, max **1.135**.
- via 0.4/0.2 needs 0.400 + 2×0.127 = **0.654 mm** → fits at annulus ≥ 0.654 (median and above).
- via 0.8/0.4 (the Default netclass via) needs 0.800 + 2×0.127 = **1.054 mm** → **fails at the median
  annulus (1.030) and at every pad below it.** The Default 0.8/0.4 via is unusable around U200.
- 15 pads (0.520–0.5411 mm annulus) take **no in-line via at all**; they must escape sideways into the
  alleys between cap courtyards: N alleys 0.400/0.890/0.400/0.895/**1.160**/0.905/0.560,
  S 0.400/0.890/0.400/0.900/0.560/0.900/0.400, W 0.400/0.890/0.400/0.890/0.400,
  E 0.980/0.935/0.900/0.900 (PRIOR). Of these, 13 alleys are ≥ 0.890 mm and take a 0.4/0.2 via.
- No via-in-pad anywhere: U200's only drilled pads are the 9 EP thermal vias 0.600/0.250 (heritage
  footprint, already in the EP), which are GND and usable as the local return.

Pins that genuinely need an inner-layer escape = the **10 signal pins whose destination lies on the
opposite side of the package** (PRIOR pin table): 16 TOP_SDA, 17 TOP_SCL, 19 CTL_USBBOOT, 24 SWCLK,
25 SWDIO, 27 UART_TX, 35 PYRO_INHIBIT_STATE, 36 F5_SENSE, 40 F1_SENSE, 43 F4_SENSE.
Rotation trial (PRIOR): 0° → 10, 90° → 8, 180° → 13, 270° → 12. **Do not rotate** (see PLR-05).

**U511 BQ25886 VQFN-24**, pos (277.000, 152.200), pad 0.825 × 0.250, pitch 0.500 → gap **0.250 mm**;
again < 0.381, so no track between pads. Annulus min **0.875 mm** (pads 19–24 vs C511), 0.900 mm
(pads 10–16 vs C512/C516). 0.4/0.2 via (needs 0.654) **fits** with 0.11 mm margin per side;
0.8/0.4 via (needs 1.054) **does not fit anywhere in U511's ring**.

**Q510 DFN2020-6E**, pos (270.000, 156.000). Pad 1 (VBUS_CHG) is a *custom* pad — `GetSize()` reports
0.010 × 0.010 but the real copper bbox is **1.170 × 2.410 mm** (x 268.925–270.095). Not a footprint
defect; it is the wide input tab. Pads 2/3 = 0.400 × 0.500, pad 4 = 0.300 × 0.920 at x ≈ 270.49;
clear gap pad1→pad4 = **0.245 mm** (the known intra-footprint DRC item). Routable: the BenchPower
1.0 mm class necks to ≤ 0.40 mm across Q510's own pads — a part limit, not a placement one.

## A.2 — Decoupling-cap GND returns

45 caps checked for a GND via ≥ 1.2 mm clear beside the GND terminal (PRIOR + `r2.py`).
**37 of 45 take an 0.8/0.4 via at 0.75 mm out.** The 8 that do not are all in U200's ring:

| cap | best 0.8 mm clr | largest via that fits | offset | clr to |
|---|---|---|---|---|
| C204 | 0.270 | **0.50 mm** | 0.39 | 0.220 → C219.1 |
| C206 | 0.280 | **0.60 mm** | 0.44 | **0.130** → C216.1 |
| C209 | 0.270 | **0.50 mm** | 0.39 | 0.220 → C206.1 |
| C212 | 0.270 | **0.50 mm** | 0.39 | 0.220 → C210.1 |
| C213 | 0.315 | **0.60 mm** | 0.44 | 0.210 → L200.1 |
| C216 | 0.235 | **0.60 mm** | 0.44 | **0.130** → C207.1 |
| C217 | 0.365 | **0.60 mm** | 0.44 | 0.260 → U200.44 |
| C219 | 0.270 | **0.50 mm** | 0.39 | 0.220 → C205.1 |

C206 and C216 clear by 0.130 mm against a 0.127 mm floor — a 0.003 mm margin, i.e. no margin.
JLCPCB 4-layer minimum via is **0.15 mm drill / 0.25 mm pad** (PRIOR, JLCPCB capability page), so a
0.45/0.20 via is well inside capability and is the right rule for this ring.
Escape hatch that costs nothing: the E–W lane at **y = 100.2–100.8 is completely free across
x 266.00–296.39 (30.39 mm, PRIOR)** — 0.5–1.2 mm south of the C209/C206/C216/C207 row. Put those
GND vias there instead of radially outward.

## A.3 — Corridors

**(a) face column → emulator core.** 33 distinct signal nets have pads on both sides of the
x 266.4–268.9 gap (`r2.py`; the 10 face SDA/SCL, 6 face PWR, 5 F_SENSE, TOP_SDA/SCL, FC_RESET,
USBBOOT, WDT_DISABLE, CTL_*, +3V3, F0_DEV_*). The gap column is **empty of parts for 94 mm of y**
(x = 259 / 262 / 265 / 267 all free 48.0–142.0 except R708 at y 76.67–77.31, PRIOR). 33 tracks at
0.25 + 0.20 mm pitch need 14.85 mm of that 94 mm. **Not a bottleneck — no finding.**

**(b) emulator core → bench I/O cable.** y = 100.5, 106.0, 110.0 are each free 266.00–296.39
(30.39 mm); x = 266.5 free y 86–116 (PRIOR). **No finding.**

**(c) USB pair J701 → R703/R704 → U200.** Geometry (`r2.py`):
J701 A6 D+ (274.750, 50.075), A7 D− (275.250, 50.075); R703.1 D+ (272.845, 88.590),
R704.1 D− (274.645, 88.590); R703.2 → U200.52 (273.545, 91.418), R704.2 → U200.51 (273.945, 91.418).
Run length J701 → series resistors **38.52 / 38.56 mm** (skew 0.04 mm); resistors → U200
1.939 / 1.939 mm (skew 0.000). Length matching is free.
Corridor: J703's THT pad columns block **x 269.94–271.64 and 272.49–274.19 for y 72.97–86.74** on
every layer; the free channel east of them is **274.19–296.39 (22.20 mm)** (PRIOR). The pair fits
there at x ≈ 274.5/275.0 with no part in the way, over a solid In1 GND plane. Net order is preserved
end to end (D+ west of D− at both ends) — **no crossing**.
Two real problems, both at the connector and at the resistors — see PLR-03 and PLR-04.

**(d) wing → strip.** 3V3_EMU MST 223 mm / 105 crossings; PYRO_INHIBIT_STATE one edge
U200.35 → R601.2 = **129.4 mm with 50 crossings — the worst single airwire on the board**.
The strip's north corridor (y 141.5 → first obstacle) is continuous at every sampled x, narrowest
**2.25 mm at x = 250 (TP401)**, then 2.55 at x = 265 (TP511), 3.09 at x = 220 (C315), 3.44 elsewhere
(PRIOR). At 0.25 + 0.20 mm that carries 4–5 tracks; at the BenchPower 1.00 mm width it carries one.
See PLR-06.

**(e) BenchPower.** J500 → Q500/Q501/U500 → JP602–607: free y bands at x = 190 widest 4.06 mm, at
x = 200 14.47 mm, at x = 210 15.42 mm — a 1.0 mm track + 2 × 0.25 needs 1.50 mm. Fine.
J400/J401 → F400/F401 → D400/D401 → JP400/JP401: x = 230 and x = 240 free 10.97 / 6.07 / 5.52 mm.
Fine. **VSOLAR is the exception — see PLR-07.**

## A.4 — L11 stubs (37 shared nets)

New-part courtyards crossed by the straight FC-pad → new-pad segment: **7 of 37** (PRIOR table) —
USBBOOT (Q701, Q703), FC_RESET (Q703), BATT_SCL (C315), VSOLAR (U315), F4_SCL (R353),
Dir_Chrg_In (JP602). All are 0402/SOT parts with free space either side; none forces a snake.
**That is not where the risk is.** The risk is the heritage copper inside the 12 mm band.

`r4.py` ran the straight exit segment for all 37 taps against every heritage track/via on the pad's
own layer at 0.3 mm. `r7.py`/`r8.py` then scanned the band cell-by-cell with real pad rectangles.

**Bottom-side face stubs are blocked (PLR-01).** Two heritage B.Cu tracks form a continuous
north–south wall between J2/J9/J13 (pads at x ≈ 220.81–220.90) and the extension:

```
PAYLOAD_BATT  (223.70, 85.00)–(223.70, 129.70)  w 0.400  → occupies x 223.50–223.90
DEPLOY1       (224.50, 84.60)–(224.50, 132.31)  w 0.635  → occupies x 224.18–224.82
```

Scan of B.Cu at min rules (0.127 track, 0.127 clearance), y 85.0–128.0:
x = 223.5 / 224.0 / 224.5 / 225.0 → **0 free bands, 0.0 mm free**; x = 225.5 → 33.7 mm in 6 bands.
The gap between the two tracks is 223.90 → 224.18 = **0.28 mm**; a 0.127 mm track needs **0.381 mm**.
Nothing fits. The wall spans y 84.60–132.31, covering J2 (y 87.80–95.30), J9 (102.81–110.31) and
J13 (117.80–125.30) completely. North of it DEPLOY1 steps east to x = 226.80 and runs to y = 65.30;
south of it DEPLOY1 runs horizontally (202.95, 134.15)–(222.66, 134.15) and PAYLOAD_BATT diagonally
to (220.22, 133.18), so going round costs > 20 mm inside the flight section against L11's 12 mm cap.

F.Cu has no equivalent wall: **x = 224.0 on F.Cu is free the whole 43 mm of y 85–128**, and at
x = 222.8 the free bands are 89.4–102.3 (12.96 mm) and 104.8–122.8 (18.04 mm). The only F.Cu
blockers further east are the connectors' own mounting-peg pads (J1.MP 226.05, J6.MP 226.00,
J11.MP 226.09) with 5 usable bands between them. So the F-side stubs (J1/J6/J11) are fine.

Other measured band results: `INHIB_2` (J10.3) needs **18.7 mm** inside the outline — allowed
(L11 grants ≤ 24 mm for J7/J10/J20) but it runs within 0.3 mm of the heritage `IN_RBF` track.
`Dir_Chrg_In` (J14.1) 11.8 mm, `Deploy2_EN` (U6.6) 11.9 mm, `Heater_EN` (U6.5) 11.8 mm — all
within 0.2 mm of the 12 mm cap, zero slack. `BATT_SCL`/`BATT_SDA` taken at J14.12/J14.10
(x 209.00 / 209.00, y 121.20 / 123.20) are **20.9 / 18.9 mm from the nearest Rev2 edge**, not the
10.9 mm §2 records for J14 (that figure is J14.1 only) — see PLR-02.

## A.5 — Crossing hot-spots (870 MST crossings)

| # | hot-spot | measure | verdict |
|---|---|---|---|
| 1 | **U200** | 1019 crossing-incidences; 10 of 45 signal pins have their destination on the opposite side of the package | Rotation trial 0°→10, 90°→8, 180°→13, 270°→12. 90° saves 2 pins but moves the USB pair (N pins 51/52) away from J701/R703/R704 and the QSPI row (55–60) away from U201, breaking `detail/placement_emulator_core.md` D-rows. **Do not rotate.** Escape those 10 on In2. |
| 2 | **J703** | 119 incidences; all 8 of its signals (3V3_EMU, UART_TX/RX, GPIO_SPARE0/1, FC_RESET, USBBOOT, WDT_DISABLE) come from U200's S and E sides (pins 19, 27, 28, 29, 32, 33) yet J703 sits entirely **north** of U200 (y 72.97–86.74 vs U200 y 91.4–98.3) | Every one of the 8 must wrap the package. **PLR-05.** |
| 3 | **R601 / PYRO_INHIBIT_STATE** | 51 incidences; one 129.4 mm edge with 50 crossings | Unavoidable (R601 is anchored to the pyro jumper group at x 152–186). Route on In2. **PLR-06.** |
| 4 | **R602 / C209 / 3V3_EMU** | 35 + 35 incidences; MST 223 mm, 105 crossings | Same cause, same fix. **PLR-06.** |
| 5 | **U312 / U314 / U310** | 85 / 59 / 53 incidences; F1/F3/F5 SDA/SCL stubs are the longest in the attachment table (35.5–35.8 mm) | They are correctly aligned with the connectors they serve (U310 y 103.5–109.5 ↔ J9 y 102.8–110.3, etc.). The extra 8 mm vs the top-side buffers is the deliberate under-cap placement. **No change.** |

## A.6 — Layer budget and routing forecast

Measured zone inventory (`r3.py`, 44 zones):

| layer | in the new area (wing x > 231.4 / strip y > 142.1) |
|---|---|
| **F.Cu** | GND pours already present: wing x 232.0–295.5 y 48.5–171.2 (prio 1), strip x 144.3–232.0 y 143.0–171.2 (prio 2). Signal layer flooded with GND. |
| **In1.Cu** | GND plane **x 139.8–298.5, y 45.1–174.5** — one polygon over the *entire* grown board. Solid reference under U200 (x 267–280, y 88–101) and under the whole USB corridor (x 274–276, y 50–89). |
| **In2.Cu** | Every heritage In2 pour stops at the Rev2 outline: +3V3 x 143.5–231.1 y 47.8–141.9; VBUSP 180.0–189.9 × 102.7–129.1; RF_VCC 171.4–188.5 × 101.0–112.8; Dir_Chrg_In 204.3–208.1 × 113.8–131.8; VSOLAR and B− (In2+B.Cu) both inside the old outline. **In2 is completely empty over the wing and the strip.** |
| **B.Cu** | GND pours wing x 232.0–295.5 y 48.5–171.2 (prio 1), strip x 144.3–232.0 y 143.0–171.2 (prio 2). |

So the extension has **three usable signal layers (F.Cu, In2, B.Cu) over a solid In1 GND plane** —
far better than the two I had assumed. The flight section, by contrast, has **zero** free layers in
the 12 mm attachment band: L11's Freerouting fixture blocks In1 and In2 across the whole band ring,
and F.Cu/B.Cu are occupied by heritage pours and tracks.

**Is a 3V3_EMU pour on In2 across the wing and strip the right call?** Partly. It is *allowed*
(L6 bars new **FC-power** pours on In2; 3V3_EMU is a new net) and physically free. But a full
wing + strip In2 pour spends the only unencumbered signal layer on one net, and 3V3_EMU only needs
plane treatment where its pads are: **24 of its 34 pads lie in x 267–295, y 88–108** (emulator core).
Recommendation: pour 3V3_EMU on In2 over **x 265–296, y 86–112 only**, priority below GND, and leave
the rest of In2 as the wing's north–south and the strip's east–west signal layer. Run the single
long west branch (R602 at 157.5, 158.6) as one track, not as a plane arm — and at 0.5 mm, not the
BenchPower 1.0 mm, since it feeds one indicator LED through R602 (see PLR-06).

## Findings index

PLR-01 blocker  B.Cu exit wall (DEPLOY1 + PAYLOAD_BATT) blocks all 9 bottom-side face stubs
PLR-02 major    BATT_SDA / BATT_SCL taps at J14.10/J14.12 are 18.9 / 20.9 mm from the Rev2 edge
PLR-03 major    J701 A6↔B6 / A7↔B7 links cannot be made on F.Cu — "no vias" is unachievable
PLR-04 minor    USB pair pitch opens to 1.800 mm at R703/R704
PLR-05 major    J703 sits north of U200 while all 8 of its signals leave U200 south/east
PLR-06 major    3V3_EMU and PYRO_INHIBIT_STATE cross the strip at BenchPower 1.0 mm width
PLR-07 minor    VSOLAR's 1.0 mm run must detour around the Rev2 outline notch (~43 mm)
PLR-08 note     Default 0.8/0.4 via does not fit in U200's or U511's escape ring

## Addendum — J14 southern exit corridor (`r10.py`)

Min-rule scan, y 121.0 → 142.1, for a route from J14's even-pin column to the strip:

```
F.Cu x=208.5/209.0/210.0  blocked by J14's own pad column (0.4 mm slots only)
F.Cu x=211.0              CLEAR 121.0–142.1, one band, no blockers at all
F.Cu x=212.0              clear except J15.MP at 138.8–141.0
B.Cu x=211.0/212.0        blocked below y 131.8 by DEPLOY1 / PAYLOAD_BATT / Dir_Chrg_In
```

So a clean, heritage-copper-free path for `BATT_SDA` / `BATT_SCL` exists **on F.Cu at x ≈ 211**,
length ≈ 21 mm from J14.10/J14.12 to the old bottom edge at y = 142.12. It needs an L11 stub-length
amendment of the same kind already granted to J7/J10/J20 (≤ 24 mm) — not a new placement.
Confirms the B.Cu wall of PLR-01 extends across the bottom of the flight section too.
