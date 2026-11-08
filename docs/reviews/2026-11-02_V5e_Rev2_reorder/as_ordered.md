# V5e Rev2 as ordered, November 2026

JLC order W2026110300110689: 5 assembled boards, $701.77. The production files committed at `b5efd32` (`origin/v5e-rev2` after PR 56) were uploaded, with the swaps below made in JLC's cart. The files on this branch now match what was built, except R75.

## Parts that differ from the b5efd32 BOM

| Ref | b5efd32 BOM | As built | Source on the order | Files now |
|---|---|---|---|---|
| U6 | TPS4H160AQPWPRQ1, C485918 | TPS4H160BQPWPRQ1, C471053 | JLC stock | C471053 |
| C21, C22, C23 | 10 uF 10 V, C19702 | Samsung CL10A106MA8NRNC 10 uF 25 V, C96446 | JLC stock | C96446 |
| IC3 | RV-3028-C7 TA QA, C3304278 | RV-3028-C7 32.768kHz 1ppm TA QC, C3019759 | My Parts | C3019759 |
| L3 | Abracon AOTA-B201610S3R3-101-T, C42411119 | same part | Michael's own stock | C42411119 |
| R75 | 0.12 ohm, C81248 | 0.12 ohm, C81248 | JLC stock | 0.1 ohm, C154690 |

R75 sets the LT3652 charge current (100 mV across R75), so the November boards charge at about 0.83 A instead of the designed 1 A.

## Fitted by hand

| Ref | Part | Files now |
|---|---|---|
| J3, J4 | pin headers | do not place |
| JP6 | solder jumper | do not place |
| R9 | DNF resistor | do not place |
| TP2, TP5, TP6, TP8 | loop test points | do not place |
| J23 | Hirose DF11CZ-4DP-2V(27), C597838 | populated (JLC places it) |

J23 stays assigned in the files. JLC stock of C597838 was 7 on 2026-11-08, enough for 5 boards but not 10.

## Order settings

| Setting | Value |
|---|---|
| Stackup | JLC04161H-7628 |
| Electrical test | 4-wire Kelvin |
| Cleaning | No |
| Conformal coat | None |
| Product description | Development Board, HS 847330 |
| Confirm Parts Placement | On, auto-confirm off |
| BT1 (C964818) middle pad | Paste, yes (JLC asked) |
| Placement rotations | Eight fixed in JLC's viewer, see `placement_rotations.md` |

## Stock on 2026-11-08 for the next order

| LCSC | Part | JLC stock |
|---|---|---|
| C471053 | TPS4H160BQPWPRQ1 (U6) | 36 |
| C3019759 | RV-3028-C7 TA QC (IC3) | 0 |
| C42411119 | AOTA-B201610S3R3-101-T (L3) | 1,741 |
| C154690 | RALEC LR2512-2AR100F4 (R75) | 29,820 |
| C597838 | DF11CZ-4DP-2V(27) (J23) | 7 |
