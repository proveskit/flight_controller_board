# FlatSat V1 floorplan v2.2 — junior developer / bench-user review

**Reviewer role:** I'm the person who gets handed this board assembled and has to run flight software
against it every day on a bench — solar sim into it, battery replica, probe on it, SWD cable in it. I am
not a layout engineer. Everything below is measured on the scratch copy of v2.2
(`/private/tmp/.../panel/project/FlatSat_V1.kicad_pcb`, read-only) with KiCad's `pcbnew` (courtyard
polygons, `fp.GetCourtyard(layer).BBox()`, plus direct pad/net queries), cross-checked against
`floorplan_v2.md`, `00_pm_brief.md`, and `panel/facts/facts.md`. Nothing was written to the live board.

**What I fetched:** I tried to pull manufacturer drawings for Phoenix MKDS 1,5/2-5.08 & 1,5/3-5.08, the
HRO TYPE-C-31-M-12 USB-C receptacle, JST SH BM03B-SRSS-TB, and MSK12C02 (WebSearch + WebFetch against
Phoenix Contact, Mouser/Octopart PDFs, SnapEDA, JST/Datasheet.live). Every one of those either 403'd or
returned dimensions baked into vector/image drawings that the fetch tool couldn't OCR — I got only
fragments (MSK12C02 "8x2.8mm SMD, 1.4mm travel"; SH connector "3.0mm high, side-entry"; USB-C receptacle
"8.94×7.35×3.16mm" for a similar part). Where a manufacturer number wasn't recoverable I fell back to the
**actual KiCad courtyard geometry already on the board** (which is a real, sourced footprint, not a guess)
and to generic knowledge of these connector families, and I say explicitly below which is which.

---

## 1. Can everything be plugged in at once?

Yes, physically, with one real asterisk. I measured the mating-face orientation of every connector from
its courtyard vs. the nearest board edge and its pad layout (pads cluster at the "tail" end, the open end
of the courtyard box faces the mating direction):

| Connector | Mates | Opens toward | Clearance to nearest obstruction |
|---|---|---|---|
| J701 (emulator USB-C) | bench laptop | north, off the wing's top edge (y=47.58) — courtyard top edge 48.805, **1.23 mm** from Edge.Cuts | nothing north of it but open air |
| J510 (charger USB-C) | bench PSU-style USB charger | south, off the bottom-right corner (y=172.12) — courtyard bottom 170.255, **1.87 mm** from Edge.Cuts | nothing south of it but open air |
| J12 (FC's own USB-C, **B side**) | laptop | east, into the L3 lane — courtyard face at x=227.36 | **16.14 mm** clear to face_column's west edge (x=243.495) — the 12.6 mm lane is exactly sized for this cable |
| J22 (FC's own SWD, F side) | probe | east, into the lane — courtyard face x=226.05 | **17.34 mm** clear |
| J702 (emulator SWD) | probe | straight up (vertical SMD header, mates out-of-plane) | 1.78 mm to SW701/SW702 (see §6) |
| J703 (bench ribbon) | ribbon cable | straight up (vertical 2×5 header) | 11.5 mm clear of J701 |
| J500 (bench PSU, 3-pin) | PSU leads | south, off the strip's bottom edge (172.12) | terminal body 0.35 mm from Edge.Cuts |
| J400/J401 (solar sim, 2-pin×2) | solar sim leads | south, same edge | see §2 — they're 1.24 mm apart from *each other* |

So every mating direction clears the board or the lane with real margin, and nothing physically blocks a
second connector's cable path. **The one asterisk is J12**: it's mounted on the **bottom (B) side** of the
board (confirmed: `side=B`, `rot=-90°`), while J701/J510/J500/J400/J401/J22/J702/J703 are all **F side**.
To plug a laptop into J12 *and* have everything else plugged in at the same time, the bench fixture has to
give clean access to the underside of the board simultaneously with the top — i.e. tall standoffs with
open sides, not a board sitting flat on a plate. This is a pre-existing Rev2/heritage placement (frozen,
L4) — not something this review can move — but it's the kind of thing that bites a bench user on day one if
the fixture isn't planned for it, so I'm flagging it (JD-05).

---

## 2. Wrong-plug risk: J500 vs J400/J401, and the jumpers

**J400 and J401 are the sharp one.** Both are `TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02` — same part,
same pitch, same pole count, 12.5 mm apart center-to-center — and their **courtyard-to-courtyard gap is
only 1.24 mm** (J400 right edge x=237.135, J401 left edge x=238.375). Pin 1 of each carries a different
solar channel (`VSOLAR_BENCH_A` on J400, `VSOLAR_BENCH_B` on J401), pin 2 is GND on both. Nothing
mechanical stops a wire going into the wrong block — MKDS terminals aren't a keyed pluggable connector,
they're a fixed screw block the user wires directly into. L8's legend plan ("VSOLAR A/B" beside each
terminal, polarity marks, text ≥1.2 mm high) is the only thing that will disambiguate them, and **1.24 mm
of clear board between the two bodies is not enough room to put a legend *between* them** — the label has
to go above or below instead, which is workable but needs to be planned now, not assumed.

**J500 vs J400/401 is lower-risk than it looks.** J500 is a *3*-position block (`MKDS 1,5/3-5.08`, visibly
wider — courtyard 16.34 mm vs. 11.26 mm) and sits 9.7 mm of clear board from J400 — a bench user comparing
"3 screws vs. 2 screws, 26 mm apart" is much less likely to miswire than "2 screws vs. 2 screws, 1.24 mm
apart." I'm not scoring that pair as a separate finding.

**JP400 (VSOLAR select) and JP510 (charger CHG OUT select)** are the other sharp case: both
`PinHeader_1x02_P2.54mm_Vertical`, identical part, and their **courtyard gap is 0.87 mm** (JP400
250.985–254.615, JP510 255.485–259.115, same y row, 4.5 mm center-to-center) — confirmed against
`facts.md`'s own courtyard-gap table (`JP510 | JP400 | 0.870 | F`). A shunt cap moved one slot over
silently reconfigures a completely different subsystem (solar-channel routing vs. charger output
routing), and neither jumper sits anywhere near the block its own function belongs to (JP400 is 19.5 mm
from J400/J401's screw terminals; JP510 is 15.9 mm from J510) — so there's no positional cue either, only
a legend that hasn't been drawn yet and has under a millimeter of gap to fit between the two.

---

## 3. Bench-mode shunts (JP600–JP607, SW600)

The six main-bank jumpers (JP602–607) sit on a clean 5.75–5.80 mm pitch — but each is a
`PinHeader_1x02_P2.54mm_Vertical` with courtyard width 3.63 mm, so **the clear gap between neighboring
header bodies is only 2.17 mm** (measured on all five adjacent pairs: 606–605, 605–603, 603–604, 604–602,
602–607, all 2.12–2.17 mm). The brief's own bench-hardware list calls out "2.54 mm headers + standard 6 mm
shunts" — a standard 2.54 mm shorting-block body is typically flared for a finger/plier grip, and 2.17 mm
of clearance to the next header is tight for pulling one shunt without nudging its neighbor, worse if
you're using pliers rather than fingernails. This is a row you'll be reaching into every time you change
bench mode, so it's worth a second look before routing locks the spacing in (JD-03).

**SW600 (pyro SAFE slide switch)** sits in a genuinely pinched pocket: JP600/JP601 are **0.957 mm** above
it, LED600/R602 are **~1.0 mm** below it (both from `facts.md`'s courtyard table). SW600 itself is an SMD
MSK12C02 (per the JLC listing, an 8×2.8 mm body with ~1.4 mm of slide travel) — low-profile, so it won't
get bumped by accident (good for the "can a switch get knocked" question), but if a shunt cap is seated on
JP600/601 right above it, there's very little vertical room left to get a fingernail or a small tool onto
the slider to arm/safe the pyro circuit (JD-08). LED600 is directly below/adjacent and unobstructed by
anything taller, so it stays visible.

**Shunt-to-connector alignment** (the "is it obvious which header parallels which FC connector" question):
it mostly works. JP606 (`IN_RBF`/`VBUSP`) sits at x=188.75, exactly under J30 (x=188.75, 0.0 mm offset).
JP604 (`VBATT_SENSE`) is 0.65 mm off J8. JP607 (`B-`) is 1.95 mm off J15. JP603 (`INHIB_1`) is 2.58 mm off
J29. That's a real, visible column correspondence — I'm not filing this as a problem, just confirming the
brief's intent measures out.

---

## 4. Probing

Every net a bench user would actually want mid-bring-up **does** have a test point — `VBUS_EMU`,
`3V3_EMU`, `1V1_EMU` (TP200/201/202), `Dir_Chrg_In`, `VBAT_BENCH_N`, `B-`, `DOUT_GATE`, `COUT_GATE`,
`MID_BENCH` (TP500–505), `VBUS_CHG`/`CHG_SYS`/`CHG_BAT` (TP510–512), `Deploy1/2_EN`, `Heater_EN`,
`PYRO_INH_COM` (TP600–603), F0–F5_PWR and `+3V3` (TP300–306) — I checked every TP's actual net via
`pcbnew`, not just its silkscreen value field.

**What has no test point anywhere on the board: every I2C signal.** I checked all 218 new pads and there
is no test point on `F0_SCL/SDA` … `F5_SCL/SDA`, `SCL_Top`/`SDA_Top`, `BATT_SCL`/`BATT_SDA`, or any of the
emulator-side `EMU_F*_SCL/SDA` nets — 14 buffered I2C signal nets (7 TCA4311A channels' worth) plus the
raw emulator-side bus, zero test points between them. That's the one thing I'd genuinely want before I
start debugging "face 3 isn't responding" on the bench (JD-01).

**Probe/hook-clip clearance is tight almost everywhere test points do exist.** Every `TestPoint_Pad_D1.5mm`
bank on the board is spaced at 3.5–4.0 mm pitch, which leaves only **0.96–1.41 mm clear** between
neighboring TP courtyards (TP300–306: 0.96 mm; TP600–603: 0.957 mm; TP202–203: 1.41 mm; TP500–505: 1.41
mm). A standard hook-clip jaw or even a 2.5 mm bare probe tip is wider than that gap, so touching one TP
risks brushing its neighbor — on TP500–505 that's `Dir_Chrg_In` next to `VBAT_BENCH_N` next to `B-`, i.e.
adjacent nets you really don't want shorted together even briefly (JD-06).

---

## 5. Handling and mounting

Five M3 holes: H1/H2 (heritage) plus H10/H11/H12 (new corners). I checked courtyard clearance from each
new hole to its nearest neighbor: **H10 and H12 have nothing within 3.5 mm** (clean corners to grip or rest
a standoff against). **H11** has J702's courtyard 3.28 mm away and TP701 2.0 mm away — still fine, no
finding.

Bottom-side parts (U310/U312/U314 + the FC's own 137 B-side heritage parts, plus J12/J2/J9/J13) mean the
board needs standoff height on **both** faces to sit flat without resting on a populated pad — this is
pre-existing to the FC and not something this pass changed.

Y200 (crystal) and Q510 (DFN charger FET) — the two "fragile part at a corner" candidates — are **not**
near any board corner: Y200 is ~65 mm from the nearest mounting hole/corner, Q510 is 25.5 mm from H11. No
corner-bump risk for either.

---

## 6. Firmware bring-up

**SW701/SW702 net check — the task brief's own guess was backwards.** I read the actual pads: `SW701` is
on net `EMU_RUN` (run/reset control), `SW702` is on net `EMU_BOOTSEL_SW`. So **SW702 = BOOTSEL, SW701 =
RUN/RESET**, not the other way around — worth getting right in the silkscreen and the bring-up doc.

Both buttons sit close to J702 (SWD): **1.78 mm** courtyard gap from each button to J702, and **1.93 mm**
between the two buttons themselves. J702 mates straight up (vertical SMD header, cable exits out of plane)
so it doesn't block finger access to either button from the side, but an SWD probe housing overhanging its
footprint even slightly will be right where your thumb wants to land on SW702 for a BOOTSEL-hold-and-plug
sequence (JD-07).

J701 itself is well clear of both buttons and of J702/J703 (6.7–21 mm to each), and its plug direction
(north, off the board) doesn't cross their positions at all, so plugging the emulator's own USB doesn't
interfere with either button or the ribbon header.

J12 vs. J22: J22 (SWD) is F-side, J12 (USB) is B-side — different faces, see §1/§5.

---

## 7. FC's own edges

The new strip (`strip_left_pyro_shunts` envelope x 150.5–220.7, y 142.8–161.9) sits entirely **south of
y=142.1**, which is south of every FC connector I was asked to check (J21/J24 at y=118.6, J23 at y=111.9,
J4 at y=130.8, J3/J5 at y=61–67, RF1 at y=87, U13 at y=71, U30 at y=96.5 — all above y=138). None of them
sit inside the new strip's footprint or lose side/top access because of it. No finding here — this one
checks out clean.

---

## 8. Anything that would make me send it back

Nothing here rises to "send it back" — no part is unreachable, unmateable, or physically wrong. The two
things closest to that bar are the J400/J401 legend-space squeeze (§2) and the missing I2C test points
(§4), because both get materially harder to fix once routing and silkscreen lock in behind them.

---

## Findings summary

See structured findings JD-01 … JD-08 returned with this review. Severities: 4 major (JD-01 I2C test
points, JD-02 J400/J401 legend space, JD-03 shunt-bank grip clearance, JD-04 JP400/JP510 swap risk), 3
minor (JD-06 TP probe-pitch, JD-07 SW701/SW702-vs-J702 clearance + BOOTSEL/RESET mislabel risk, JD-08 SW600
pocket), 1 note (JD-05 J12 bottom-side access). Zero blockers — everything can be built, wired, and used;
these are things that make the bench experience worse or make bring-up harder to debug, exactly the lens
I was asked to apply.
