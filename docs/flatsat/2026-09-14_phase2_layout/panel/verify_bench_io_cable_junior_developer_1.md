# Skeptic verification — bench_io_cable — junior developer report 1

Board checked: `/private/tmp/claude-501/-Users-ncc-michael-GitHut/76ce4476-5b98-4bdc-b249-03b85212b6e5/scratchpad/panel/project/FlatSat_V1.kicad_pcb` (scratch copy of v2.2, read-only). No writes to the live board or to `FC_V5e_Production_Rev2/`. No GUI opened. No commits.

## JD-07 — SW701/SW702 sit ~1.8 mm from J702 (SWD); BOOTSEL/RESET guess in the review checklist is backwards

**Verdict: downgraded (minor → note)**

**Re-measurement (pcbnew, this session):**

Pad-net dump on the scratch board confirms the claim exactly:
- `SW701`: pads A/A' = `EMU_RUN`, B/B' = `GND`
- `SW702`: pads A/A' = `EMU_BOOTSEL_SW`, B/B' = `GND`

So SW701 = RUN/RESET, SW702 = BOOTSEL — reproduced.

Courtyard-to-courtyard gaps (F.CrtYd bounding boxes, this session vs. the finding):

| pair | my measurement | finding | 
|---|---|---|
| SW701–J702 | 1.82 mm | 1.78 mm |
| SW702–J702 | 1.82 mm | 1.78 mm |
| SW701–SW702 | 1.97 mm | 1.93 mm |

Same order of magnitude and same conclusion (tight but workable); the ~0.04 mm difference is method noise (bounding-box vs. polygon courtyard extraction) and doesn't change anything.

**Where the "backwards guess" actually lives:** the finding's own `reference` field points at the *review workflow's* checklist question (`.claude/workflows/flatsat-floorplan-panel.js` step 6: "SW701 (BOOTSEL?) / SW702 (RESET?)"), not at any owner-facing project document. The project's actual placement documentation already has this right: `detail/placement_bench_io_cable.md` lines 32–33 state plainly —
> SW701 (fixed anchor) — EMU_RUN momentary button — RP2350 reset.
> SW702 (fixed anchor) — EMU_BOOTSEL_SW momentary button — RP2350 BOOTSEL entry (feeds D200 in emulator_core).

So there is no mislabeled owner document to fix — the "brief's own guess" was a reviewer's parenthetical question mark in a checklist prompt, already correctly resolved in the placement doc that predates this panel.

**Silkscreen check:** I grepped the board file for any BOOTSEL/RESET text tied to SW701/SW702 — none exists. Both footprints currently only carry `Value = "KMR2"` (the part number) on F.Fab; there is no silkscreen legend yet to be "backwards." Per the owner's L8 rule, silkscreen legends are a stage-6 deliverable, not part of this floor-plan review, and per the panel's own reporting rule ("do not report things that belong to... silkscreen stages unless the placement makes them impossible") this has no placement consequence at all — the finding itself says so ("No placement change needed").

**Mating-direction check (supports the finding's own reasoning):** J702 is JST SH `BM03B-SRSS-TB` (LCSC C160389). LCSC's listing describes it as "Surface Mount, Vertical" — i.e. a top-entry SH housing whose mating cable exits perpendicular to the board, not sideways across SW701/SW702. This corroborates the finding's claim that J702 "doesn't block side access" and that 1.8–2.0 mm of courtyard clearance is workable for thumb access to either button while a probe cable is plugged in.

**Disposition:** the factual content (net assignment, clearance figures, connector mating direction) all holds up and I could not refute any of it. But by the panel's own instructions this is exactly the class of finding to keep out of the placement review: zero placement consequence, and the thing it asks to fix (silkscreen legend text) does not exist yet at this stage. I'm downgrading severity from **minor** to **note** rather than refuting outright, because the underlying net-identity fact (SW701=RESET, SW702=BOOTSEL) is worth carrying forward so stage 6 silkscreen and any bring-up doc get it right the first time — but it is not a stage-2 layout action item.

**Improved recommendation:** No placement change (confirmed). Carry this note into the stage-6 silkscreen task and into the emulator bring-up procedure once it's written: label SW701 "RUN/RST", SW702 "BOOTSEL" (matching `EMU_RUN` / `EMU_BOOTSEL_SW` nets and the already-correct text in `detail/placement_bench_io_cable.md`). No datasheet checklist row in `placement_bench_io_cable.md` needs to change — the doc is already correct.

**Confidence:** 0.9 (nets and connector orientation independently confirmed from board data and LCSC; the only judgment call is the severity/scope disposition, which follows directly from the panel's own reporting rules).

**Sources fetched:** LCSC product page for C160389 (JST BM03B-SRSS-TB), queried for connector mating orientation.
