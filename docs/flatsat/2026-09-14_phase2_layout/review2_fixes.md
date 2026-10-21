# FlatSat V1 review pass 2: fixes for items 1, 2, 3 and the item-6 note

Workspace `fix2/FlatSat_V1/` (repo `FlatSat_V1/` at 1ccbd07 without `jlcpcb/`). Changed files:
`FlatSat_V1.kicad_pcb` (refilled), `battery_protection_replica.kicad_sch`, `pyro_inhibit.kicad_sch`. Nothing else differs (`diff -rq`).
Edits are scripted and rerunnable: `j510_move.py` (via `ed.py`), `j500_legend.py` (via `ed.py`), `sch_review2.py` (idempotent).

## Gates

| | baseline (1ccbd07, refilled) | final |
|---|---|---|
| GATES | heritage=7 heritage_refill=0 attachment 0/7/37, errors 14, unconnected 1, parity 11, via-in-pad 0/0, track_width 95 | identical |
| DRC items vs baseline (all severities) | - | 0 new, 0 gone; one track_width item changes description only (`VBUS_CHG F.Cu length 5.7000 -> 8.5696 mm`, the same 0.25 mm J510 escape segment, stretched) |
| ERC | 12 errors / 693 items | 12 errors / 693 items, identical set |

```
GATES heritage=7 heritage_refill=0 attachment(viol,warn,stubs)=0 7 37 | errors: 14  unconnected: 1  parity: 11 | via-in-pad: 0 in-pad, 0 edge, 0 distinct vias | track_width: 95
```

## Item 1: J510 moved to the HRO edge line

| | before | after |
|---|---|---|
| J510 origin | (262.0,166.06) rot 0 | (262.0,168.93) rot 0 |
| shell face (F.Fab front) vs Edge.Cuts y=172.12 | 169.71, 2.41 mm behind | 172.58, 0.46 mm proud (HRO C165948 RECOMMEND P.C.B LAYOUT) |
| courtyard y | 160.745-170.255 | 163.615-173.125; 0 courtyard overlaps involving J510 |
| front shell slot pad copper to edge | - | pad bottom 170.78, 1.34 mm inside the edge (min 0.2) |
| VBUS_CHG escape | 0.25 mm F.Cu x=259.55, y 161.32-155.62 | same segment, pad end stretched to 164.19 (width unchanged) |
| VBUS A4-A9 strap under the pad row (6 segs, 0.25/0.3 mm) | y 162.7-163.2 | translated +2.87 with the part |
| CC1 / CC2 escapes | 0.25 mm to y 162.015 | same segments, pad end stretched to 164.885 |
| GND (A1/A12/B1/B12, shell) | zone | zone, refilled; unconnected stays 1 (the baseline item) |
| D+/D-/SBU | no-connect | no-connect |

No new segment was added, so no track_width item appears. The strip south of J510 held no other copper (confirmed: no tracks or vias of other nets in x 250-274, y 160-173; the three GND vias at y 169.1 lie outside the courtyard).
J510 F.SilkS now overhangs the edge to y 172.89. `silk_edge_clearance` is `ignore` in the project, and the fab clips silk at the outline.
For the order: J510 is a moved footprint, so the CPL changes. Check it in the JLC placement viewer (CLAUDE.md rule 5; `^USB_C_Receptacle_HRO_TYPE-C-31-M-12*` correction is 0). The `jlcpcb/preview/` gerbers are now stale (rerun `tools/pcb/preview.sh` after install).

## Item 2: J500 over-voltage note and legend

- F.SilkS `8.4V MAX`, 1.0 mm / 0.15 mm, at (208.0,171.2), same justification and row as the two `18V MAX` legends. Box 204.4-211.6 x 170.35-172.05. It touches no pad (0.2 mm margin) and no other text, and does not collide with the J500 silk outline (bottom at 169.98; pin-1 mark at x 202.4-203.4).
- `battery_protection_replica.kicad_sch`: the BENCH PSU WINDOW line gains `  PSU OVP <= 9 V: see J500 OVER-VOLTAGE, right.`. New block at (205, 248.25) under the D11 note:
  - `J500 OVER-VOLTAGE (no OV element on J500 this rev; legend 8.4V MAX on the board):`
  - `  PSU OVP <= 9 V; verify the trip with J500 disconnected before each session;`
  - `  never use the 12-18 V VSOLAR supply on J500 (heritage C42/C1/C3 are 10 V`
  - `  rated, U500 VDD abs max 12 V).`

## Item 6: Mode 2 note (text only)

- `battery_protection_replica.kicad_sch`: the Mode 2 line gains `  See MODE 2 note, right.`; same right-column block, under the J500 note:
  `MODE 2 returns through board GND: the ISS inhibit (J15/J19/JP607) and the R5460 replica are NOT in circuit; JP607 is needed in Mode 1 only; safe the bus with JP606/RBF; run ISS-inhibit, deployment-switch and protection-trip tests in Mode 1 only.` (4 lines).
- `pyro_inhibit.kicad_sch`: POWER-UP RECIPE line now reads `JP607 (B- return; Mode 1 only, see right) + JP606 ...`; new 1.0 mm note beside the recipe at (107.95,265.43): `MODE 2 (battery sheet: USB charger via JP510) returns through board GND: ...` with the same sentence.

## Item 3: gate-drive probing text

- `battery_protection_replica.kicad_sch`: new block at (142.24,102.87), beside Q500/Q501 in the free space above TEST POINTS, with the action's text verbatim:
  `GATE-DRIVE PROBING (TP501-TP504):` / `TP501/TP503 are referenced to VBAT_BENCH_N and TP502/TP504 to B-, not GND. Measure gate drive with a floating DMM, a differential probe or an isolated scope; or clip the scope ground to board GND (JP607.2) with JP607 closed and read gates relative to TP501/TP502 by subtraction. Never earth TP501 or J500.3 while J701 or FC USB is on an earthed host.`
- The ATP text that names TP503/TP504 lives outside FlatSat_V1, in `docs/reviews/2026-10-21_FlatSat_V1/final_list.md`. There is no separate bench-procedure doc in the repo (grep "bench procedure"), so the sheet notes are the bench procedure. Text for the parent to apply:

**final_list.md line 33 (item 3 Verification), replace** `ATP: 2.0 A load for 60 s cold and after 10 min at 1.5 A: TP503/TP504 gate drive stays high, no DOUT latch.` **with:**
`ATP: 2.0 A load for 60 s cold and after 10 min at 1.5 A: TP503/TP504 gate drive stays high, no DOUT latch. TP501/TP503 are referenced to VBAT_BENCH_N and TP502/TP504 to B-, not GND. Measure gate drive with a floating DMM, a differential probe or an isolated scope; or clip the scope ground to board GND (JP607.2) with JP607 closed and read gates relative to TP501/TP502 by subtraction. Never earth TP501 or J500.3 while J701 or FC USB is on an earthed host. Gate check: current into J500.1 equals current out of J500.3 within 2 % at 2.0 A (no earth-loop diversion).`

**final_list.md line 91 (item 9 Action), replace** `verify TP503/TP504 gate drive, R500 value` **with** `verify TP503/TP504 gate drive (TP503 vs TP501, TP504 vs TP502, floating or differential measurement; see the GATE-DRIVE PROBING sheet note), R500 value`.

Optional for the parent, same doc: item 2 and item 6 bench-procedure lines are the sheet blocks above verbatim.

## Not done (out of scope)

Items 4, 5, 7. The C516 rotation offered in item 4 as an owner's option was not taken. Next-rev items from 1/2/3 (J500 OV switch, GND test point in the TP cluster, `VBAT_N` silk) are unchanged.
