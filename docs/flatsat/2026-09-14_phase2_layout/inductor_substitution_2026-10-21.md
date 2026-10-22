# L3 / L200 core-regulator inductor: substitution check (2026-10-21)

Owner request (2026-10-21): pick a lower supply-chain-risk part for the 3.3 µH inductor on L3 (flight FC RP2350 U18, heritage) and L200 (emulator RP2350 U200), ideally on the same footprint or from the same family.

## Verdict

| Question | Answer |
|---|---|
| Swap made? | **No.** No schematic, board, or `project.db` edits. |
| Why | No JLC-stocked part on the `L_pol_2016` pads meets the RP2350 requirement for a **polarity-marked** inductor (see the spec table). Every stocked 3.3 µH 2016 part is unmarked, so the winding direction is random along the reel. |
| Same MPN under another LCSC code | None. JLC search `AOTA-B201610` returns 7 codes. The only 3.3 µH one is C42411119. |
| Same family (AOTA-B201610) | 2.2, 1.0, 1.5, 0.47, and 4.7 µH codes are stocked. None is 3.3 µH, and none is polarity-marked. Only `-101-T` carries the dot. |
| Recommendation | Keep AOTA-B201610S3R3-101-T on both refs. Buy it at a distributor and consign it to JLC, or use a JLC pre-order. Details are in **Options**. |

## RP2350 requirement (fetched)

| Parameter | Requirement | Source |
|---|---|---|
| L | 3.3 µH ±20% | RP2350 Datasheet (build 2026-10-01), §6.3.8.2 "Component values", printed p. 412 |
| Construction | Fully shielded | same |
| DCR | ≤ 250 mΩ max | same |
| Isat | ≥ 1.5 A ("generally the higher saturation current the better") | §6.3.8.2, p. 412, and §6.3.8.3 "Regulator sensitivities", p. 413 |
| Polarity | "must be marked for polarity" and placed as in Figure 26. Field orientation affects the control loop and output voltage. | §6.3.8.2 p. 412, §6.3.8.3 p. 413, Figure 28 |
| Size | Figure 29 shows the Abracon part at 2.0 × 1.6 × 1.0 mm max. This is a reference drawing, not a stated limit. | §6.3.8, p. 414 |
| Recommended part | AOTA-B201610S3R3-101-T | §6.3.8.2–6.3.8.3 |
| Design-guide note | "we could find no suitable [polarity-marked] ones in the 0806 (2016 metric) case size". Abracon made the dotted part, reeled all aligned the same way. "if you choose not to use our example, then you do so at your own risk." | Hardware design with RP2350 (build 2026-08-20), §2.1 "Core voltage regulator", printed pp. 6–7 |

## Side-by-side (live JLC 2026-10-21)

Pass/fail is against the spec table. Candidate sizes come from the MPN size code (for example `201612` = 2.0 × 1.6 × 1.2 mm), so they are **inferred**. "Unmarked" means the JLC listing and part family show no polarity mark. Candidate datasheets on LCSC were bot-blocked, so their marking is **inferred** from the listing, not read from the datasheet.

| LCSC | MPN | L / tol | DCR | Isat / Irms | Size (mm) | Polarity mark | Fits `L_pol_2016` | JLC stock | $ @1 | Lib | vs RP2350 |
|---|---|---|---|---|---|---|---|--:|--:|---|---|
| **C42411119** | **Abracon AOTA-B201610S3R3-101-T** (current) | 3.3 µH ±20% | 115 typ / 140 max mΩ | 2.8 typ / 2.4 max A (−30%); Irms 2.1 A | 2.0×1.6×1.0 | **White dot, winding shown** (datasheet p. 4) | Yes (current part) | **1** | 0.2846 | Ext | **Pass** (named part) |
| C17701150 | MetalLions MTQH201612S3R3MBT | 3.3 µH ±20% | 135 mΩ | 2.4 / 2.7 A | 2.0×1.6×**1.2** | Unmarked | Pads yes; 1.2 mm tall | 1,659 | 0.045 | Ext | Fail: polarity |
| C41405891 | YJYCOIN YSMC201612H-3R3MB | 3.3 µH ±20% | 135 mΩ | 2.3 / 2.0 A | 2.0×1.6×1.2 | Unmarked | Pads yes; 1.2 mm tall | 2,609 | 0.0601 | Ext | Fail: polarity |
| C22459316 | Magnetsyc AFE201610S3R3MBT | 3.3 µH ±20% | 140 mΩ | 2.0 / 1.5 A | 2.0×1.6×1.0 | Unmarked | Yes | 3,725 | 0.0375 | Ext | Fail: polarity |
| C48689490 | SOREDE SRTC.201610.YB3R3MT00 | 3.3 µH ±20% | 170 mΩ | 2.0 / 1.5 A | 2.0×1.6×1.0 | Unmarked | Yes | 2,785 | 0.0386 | Ext | Fail: polarity |
| C2042572 | TDK VLS201612HBX-3R3M-1 | 3.3 µH ±20% | 174 mΩ | 1.57 / 1.6 A | 2.0×1.6×1.2 | Unmarked | Pads yes; 1.2 mm tall | 763 | 0.0885 | Ext | Fail: polarity; Isat margin thin |
| C5349598 | APV APH201610T3R3M | 3.3 µH ±20% | 180 mΩ | 2.0 / 1.5 A | 2.0×1.6×1.0 | Unmarked | Yes | 641 | 0.0673 | Ext | Fail: polarity |
| C48945398 | ZE ZET-CORE-201608ST3R3MBCA | 3.3 µH ±20% | 200 mΩ | 2.0 / 2.3 A | 2.0×1.6×0.8 | Unmarked | Yes | 2,473 | 0.0512 | Ext | Fail: polarity |
| C22412022 | Abracon AOTA-B201610S2R2MT (same family) | **2.2 µH** | 66 mΩ | 2.6 / 2.0 A | 2.0×1.6×1.0 | Unmarked | Yes | 4 | 0.1887 | Ext | Fail: L, polarity |
| C27999766 | Abracon AOTA-B201610S4R7MT (same family) | **4.7 µH** | 213 mΩ | 1.6 / 1.3 A | 2.0×1.6×1.0 | Unmarked | Yes | 765 | 0.2497 | Ext | Fail: L, Isat, polarity |

`L_pol_2016` pads on the board (both refs): two 0.7 × 1.7 mm rects at x = ±0.7 mm, so 0.7 mm gap and 2.1 mm outer span. Any 2.0 × 1.6 mm body fits. L3's footprint is rotated 315° on the board, L200's is at 0°.

Low-DCR, high-Isat parts are easy to find in 2016. The polarity mark is the one requirement no stocked alternative meets. The design guide reports the same finding, and it is the reason the custom Abracon part exists. Fitting an unmarked part would leave half the boards (statistically) with the field the "wrong way round". The datasheet says that degrades regulation at higher currents and during load transients, so it fails the brief's option (c) gate.

## Abracon part availability outside JLC

| Source | Stock | Price | Status |
|---|--:|---|---|
| JLC assembly library (C42411119) | 1 | $0.2846 @ 1–49, $0.2252 @ 50, MOQ 5, attrition 1 | Live API, 2026-10-21 |
| Newark | 30,960 | $0.0968–0.1723 | FindChips, 2026-10-21 |
| IBS Electronics | 18,000 | $0.1317–0.2594 | FindChips |
| New Advantage | 6,000 | $0.1996 | FindChips |
| TME | 450 | $0.131–0.26 | FindChips |
| DigiKey, Mouser | not confirmed | n/a | Product pages returned 403 / timed out to scripted fetch. Check by hand. |

## Options

| # | Option | Board change | Part cost (qty 2 / qty 5 order) | Lead-time risk | Recommendation |
|---|---|---|---|---|---|
| 1 | Buy AOTA-B201610S3R3-101-T at Newark (or DigiKey/Mouser if stocked), ship to JLC as consigned parts | None | ~$1–2 for 10 pcs + shipping | Distributor ship + JLC receiving (several days) | **Recommended.** Same part, deep US stock, ~31k at Newark. |
| 2 | JLC pre-order / global sourcing of C42411119 (min 32 per the earlier pass) | None | 32 × $0.2846 ≈ $9.11 (vs $1.42 / $3.13 in the cost estimate) | JLC sourcing lead time | Fallback if consignment is inconvenient. Same part, same price class, one less shipment. |
| 3 | Fit an unmarked stocked part (e.g. C22459316 AFE201610S3R3MBT) | Field edit only | ~$1 | None | **Not recommended.** It fails the RP2350 polarity requirement. L3 is heritage, and the flown design uses the marked part. |
| 4 | Order JLC with L3/L200 unpopulated, hand-place the Abracon part with the dot per the silk | DNP the two refs at order time | n/a | None | Workable for a 2-board bench run. It adds two 2016 hand placements next to a QFN-60, with a polarity check. |

The owner has pre-ordered IC3 (RV-3028), so it is out of scope here.

## Update 2026-10-22 08:57 PT: JLC restocked C42411119; lead-time check

The owner tentatively approved a JLC pre-order of 32, conditional on its lead time. The live check found the part back in stock, so no pre-order is needed.

| Source (fetched 2026-10-22) | Raw fields |
|---|---|
| `https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode=C42411119` | `componentModelEn: "AOTA-B201610S3R3-101-T"`, `componentLibraryType: "expand"`, `stockCount: 407` (was 1 on 2026-10-21), `minPurchaseNum: 26`, `preMinPurchaseNum: 26`, `canPresaleNumber: 0`, `componentPresaleType: null`; price tiers 1+: $0.3608, 50+: $0.2854, 150+: $0.2532 |
| `https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=C42411119` | `productModel: "AOTA-B201610S3R3-101-T"`, brand ABRACON, `stockNumber: 405`, `domesticStockVO.shipImmediately: 405`, `ship3Days: 0`, `isPreSale: false`, `productCycle: "normal"` |

| Question | Answer | Confidence |
|---|---|---|
| Lead time for C42411119 | **Not needed now: 407 in JLC stock.** Five boards need 11 (10 placed + attrition). | High (two live APIs agree) |
| Pre-order lead-time field | Neither API exposes one. JLC returns pre-order fields only (`preMinPurchaseNum`, `canPresaleNumber`); LCSC returns `shipImmediately` / `ship3Days`. | High |
| JLC published pre-order lead time | Not obtained by script. `jlcpcb.com/help/article/{pre-order-parts, how-to-pre-order-parts, global-sourcing-parts}` return HTTP 200 but only a client-rendered shell with no article text. Read the "PCBA Parts Sourcing" help pages in a browser if a figure is still wanted. | n/a |

Order action: none. The owner's JLCPCB Tools / `project.db` pass picks up C42411119 at the current Extended price (about $0.36 each below 50). Stock moves daily, so recheck right before ordering. The pre-order plan is only a fallback if stock falls below 11 again.

Fallback if stock disappears (unmarked, fails RP2350 DS §6.3.8.2 polarity marking, so it needs an owner waiver; nothing changed):

| Part | LCSC | Stock 2026-10-22 | Price | DCR / Isat | Note |
|---|---|---|---|---|---|
| Magnetsyc AFE201610S3R3MBT | C22459316 | 3,725 | $0.0375 | 140 mOhm / 2 A | best stock, fits L_pol_2016 pads, Extended |
| MetalLions MTQH201612S3R3MBT | C17701150 | 1,659 | $0.045 | 135 mOhm / 2.4 A | second choice, Extended |
