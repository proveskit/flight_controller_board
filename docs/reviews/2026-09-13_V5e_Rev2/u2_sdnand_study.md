# U2 SD-NAND second-source study — FC_V5e_Production_Rev2

Date: 2026-09-13. JLC parts DB snapshot: 2026-09-13 (7,142,068 parts).
Current part: **Zetta ZDSD04GLGEAG**, 4 Gb (512 MB) SD-NAND, LGA-8 6x8, **LCSC C2875854, stock 0**.

## 1. How U2 is wired (as-designed)

Source: `FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_sch` (U2 is on the **root** sheet)
and `FC_V5e_Production_Rev2/FC_V5e_Production_Rev2.kicad_pcb`.

Symbol `easyeda2kicad:ZDSD04GLGEAG` pin names + nets from PCB:

| Pin | Name | Net | RP2350 (U18, RP2350_60QFN) |
|---|---|---|---|
| 1 | DAT2 | `unconnected-(U2-DAT2-Pad1)` | — (floating) |
| 2 | DAT3 (= /CS in SPI) | `SPI1_CS1` | pad 19 = **GPIO15** |
| 3 | CLK | `SPI1_SCK` | pad 29 = **GPIO18** |
| 4 | GND | `GND` | — |
| 5 | CMD (= DI/MOSI) | `SPI1_MOSI` | pad 31 = **GPIO19** |
| 6 | DAT0 (= DO/MISO) | `SPI1_MISO` | pad 27 = **GPIO16** |
| 7 | DAT1 | `unconnected-(U2-DAT1-Pad7)` | — (floating) |
| 8 | VDD | `+3V3` | — |

- **SPI mode, 1-bit.** DAT1/DAT2 deliberately left open. This matches PROVES firmware
  (`sdcardio.SDCard`, SPI) — see §4.
- **Pull-ups:** only **R11 = 10k from SPI1_CS1 to +3V3**. (R90 10k is the matching pull-up on
  `SPI1_CS0`, the E28-2G4M27S radio U30 CS.) **No pull-ups on CMD/DI or DAT0/DO** —
  SD spec recommends 10k–100k on DI/DO; currently absent. Not a blocker (existing design),
  but worth adding in Rev3.
- Bus is shared: `SPI1_SCK/MOSI/MISO` also go to **U30 (E28-2G4M27S radio)**, CS0 = GPIO7.
  Note the PROVES docs errata: "SPI1 and SPI0 are using the same hardware peripheral" on V5.
  On RP2350, GPIO16/18/19 are the **SPI0** peripheral (RX/SCK/TX) despite the `SPI1_` net names.
- Decoupling: nearest +3V3/GND caps to U2 are **C28 (100nF)** and **C39 (100nF)**, both ~5.8 mm away.
  Slightly far for a 50 MHz-capable part; consider a 100nF right at pin 8 in Rev3.

### Footprint on the PCB
`easyeda2kicad:LGA-8_L8.0-W6.0-P1.27-TL-1`, placed on **B.Cu** (bottom side) at (199.4, 99.6), rot −90.

- 8 SMD rect pads, **1.70 x 0.80 mm**, long axis pointing outward (radial, along X-local).
- Two rows at local **x = ±3.70 mm → 7.40 mm row-to-row centre spacing**.
- Pitch **1.27 mm** in Y; pad-column span 3.81 mm.
- Numbering: pins **1–4 top→bottom on the −X row**, pins **5–8 bottom→top on the +X row**
  (standard counter-clockwise). Pin 1 = DAT2 = corner at local (−3.7, +1.91).
- Pin-1 marker: B.SilkS circle at (−4.80, +2.80), B.Fab circle at (−4.00, +3.00),
  Cmts.User circle at (−4.40, +1.90). Silk body outline ±4.0 x ±3.0 mm. Courtyard 9.27 x 6.34 mm.
- No thermal/centre pad, no paste overrides, no mask overrides.

## 2. ZDSD04GLGEAG datasheet facts

Datasheet: "ZETTA SD NAND Product Datasheet 1Gb/2Gb/4Gb", rev 1.3 (2023-01-05) —
https://www.lcsc.com/datasheet/C2830323.pdf (covers ZDSD01G/02G/04G, one common package).

Top view, left column top→bottom = pins 1..4, right column bottom→top = pins 5..8:

```
 DAT2 (1)   (8) VDD
 DAT3 (2)   (7) DAT1
 CLK  (3)   (6) DAT0
 GND  (4)   (5) CMD
```
Confirms the KiCad symbol exactly. Note this is **not** the microSD 1–8 ordering — it is the
SD-NAND LGA-8 convention.

Mode table: DAT3=/CS, CMD=DI, DAT0=DO, CLK=SCLK in SPI mode; DAT1/DAT2 = NC in SPI and SD-1bit.
Package: body D=8.00 (7.95–8.05), E=6.00 (5.90–6.10), A=0.80 thick; chip land L=0.80 nom,
b=0.60 nom, pitch e=1.27. Pin-1 dot at the DAT2 corner. Supports SD 4-bit / SD 1-bit / SPI,
SD 2.0, SDHC-capable (CCS in CMD58/ACMD41 R3). Standard init:
≥74 clocks → CMD0 → CMD8 → CMD55+ACMD41(HCS) → CMD58 → (SD mode: CMD2, CMD3).

Family: ZDSD512M / 01G / 02G / 04G / 08G / 16G / 32G / 64G, suffix `LGEAG` = extended −30..+85 °C,
`LGIAG` = industrial −40..+85 °C. **No EOL notice found**; rev 1.3 is recent.

## 3. In-stock LGA-8 6x8 SD-NAND candidates at JLC/LCSC (2026-09-13 DB)

All are **Extended** parts at JLCPCB (extended-part fee + possible MOQ/reel handling). Prices CNY.

### Zetta — same family, same datasheet, same land pattern (only capacity differs)
| LCSC | MPN | Cap | Temp | Pkg | Stock | Price 1-9 / 100+ |
|---|---|---|---|---|---|---|
| C2875854 | ZDSD04GLGEAG (**current**) | 4 Gb | −30..85 | LGA-8(6x8) | **0** | 17.24 / 13.35 |
| **C2875853** | **ZDSD02GLGEAG** | **2 Gb** | −30..85 | LGA-8(6x8) | **732** | 9.11 / 6.25 |
| C2830323 | ZDSD01GLGEAG | 1 Gb | −30..85 | LGA-8(6x8) | 313 | 6.96 / 4.57 |
| C5349317 | ZDSD01GLGIAG | 1 Gb | **−40..85** | LGA8(6x8) | 12 | 8.79 / 5.87 |
| C22379765 | ZDSD512MLGEAG | 512 Mb | −30..85 | LGA-8(6x8) | 570 | 6.90 / 4.96 |
| C22370395 | ZDSD512MLGIAG | 512 Mb | **−40..85** | LGA-8(6x8) | 729 | 8.51 / 6.06 |
| C19727141 | ZDSD16GLGIAG | 16 Gb | −40..85 | LGA-8(**6.2**x8) | 1 | — |

**The Zetta line is NOT gone** — only the 4 Gb SKU is at zero. 2 Gb has 732 pcs.

### MK (MK Founder) — same LGA-8 6x8, same pinout, **4 Gb available**
| LCSC | MPN | Cap | Temp | Pkg | Stock | Price 1-9 / 100+ |
|---|---|---|---|---|---|---|
| **C26159626** | **MKDV4GIL-AST** | **4 Gb** | **−40..+85** | LGA-8(6x8) | **2087** | 18.80 / 15.39 |
| C7500178 | MKDV4GCL-ABB | 4 Gb | −25..85 | LGA-8(6x8) | 1943 | 14.02 / 10.97 |
| C51966232 | MKDV4GCL-ABF | 4 Gb | −25..85 | LGA-8(6x8) | 21 | 12.83 / 10.26 |
| C42381022 | MKDV4GCL-ABG | 4 Gb | −25..85 | LGA-8(6x8) | 2 | — |
| C26159627 | MKDV8GIL-AST | 8 Gb | −40..85 | LGA-8(6x8) | 1305 | 28.89 / 27.61 |
| C26159625 | MKDV2GIL-AST | 2 Gb | −40..85 | LGA-8(6x8) | 1552 | 11.54 / 8.42 |
| C51966231 | MKDV2GCL-ABF | 2 Gb | −25..85 | LGA-8(6x8) | 4270 | 8.61 / 6.20 |
| C51966230 | MKDV1GCL-ABF | 1 Gb | −25..85 | LGA-8(6x8) | 7434 | 5.59 / 3.87 |
| C6152616 | MKDV1GCL-ABA | 1 Gb | −25..85 | LGA-8(6x8) | 1580 | 5.88 / 4.41 |
| C726726 | MKDV1GIL-AS | 1 Gb | −40..85 | LGA-8(6x8) | 118 | 8.63 / 6.06 |

MK datasheet (MKDV1/2/4G, rev 1.4 2023, via `lcsc_datasheet_2207051415_MK-MKDV4GIL-AS_C379093.pdf`):
pin 1=DAT2, 2=DAT3/CS, 3=CLK, 4=GND, 5=CMD/DI, 6=DAT0/DO, 7=DAT1, 8=VDD — **identical to Zetta**.
Body E=8.00 (7.90–8.10) x D=6.00 (5.90–6.10), pitch e=1.27 BSC, column span D1=3.81 BSC,
chip pad b=0.55–0.60 wide, L=0.80–0.85 long. SD+SPI, standard CMD0/CMD8/ACMD41(HCS)/CMD58 init.
**Same land pattern family as the current footprint.**

### CS / Creat Storage World (CSNP) — mostly wrong body or no stock
| LCSC | MPN | Cap | Pkg | Stock | Note |
|---|---|---|---|---|---|
| C2691593 | CSNP1GCR01-BOW | 1 Gb | LGA-8(6x8) | 672 | fits; SD interface only per LCSC desc |
| C47345841 | CSNP4GCR01-BPW | 4 Gb | LGA-8(6x8) | **1** | unusable qty |
| C7527488 / C2841139 / C5440134 | CSNP16G/32G | 16–32 Gb | LGA-8(**6.2**x8) | 102/973/656 | wider body, verify land |
| C5365291 / C41380595 | CSNP64GCR01 | 64 Gb | LGA-8(**7x8.5**) | 12/275 | **different package — not drop-in** |

CSNP datasheet pinout = same as Zetta/MK (SCLK=3, VSS=4, CMD=5, VCC=8); SPI mode supported.

### XTX — not viable in this package
XTX LGA-8 SD-NANDs in stock are `XTSDQ01GLAIGA` etc. in **LGA-8 (6x5)** — a *different, smaller*
body (195 pcs). The 6x8 `XTSD0xGLGEAG` line (which IS pin-identical to Zetta) shows **no stock**
in this DB. XTX's 6x8 stock is WSON-8 (`XTSDQ02GWSIGA`) — raw SPI-NAND, wrong package and wrong
protocol.

### FORESEE / Longsys — not viable
Only `F35SQxxxx-WWT` in **WSON-8 (6x8)** in stock. Those are raw **SPI NAND** (no SD/FTL), not
SD-NAND, and the WSON land pattern (staggered, with exposed pad) does **not** match LGA-8.
No FORESEE NCard SD-NAND LGA-8 6x8 with stock found.

### MK 6.6x8 family (`MKDVxxGCL-STP*`, 16/32/64 Gb)
Larger body (6.6 x 8). Would need footprint re-verification — **not** a blind drop-in.

## 4. Capacity impact on firmware

PROVES flight software mounts the SD-NAND as a plain SPI SD card:

`pysquared/.../hardware/sd_card/manager/sd_card.py`
```python
sd = sdcardio.SDCard(spi_bus, chip_select, baudrate)   # baudrate default 400_000
vfs = storage.VfsFat(sd); storage.mount(vfs, "/sd")
```
- **SPI mode confirmed** (`sdcardio`, not `sdioio`). Matches the hardware wiring above.
- Board pin defs expose `SPI1_SCK/MOSI/MISO = GPIO18/19/16`, `SPI1_CS1 = GPIO15` — exactly U2's nets.
- **Zero capacity assumptions anywhere**: no format, no block-count, no free-space check,
  no size-based log rotation, no MB cap. Docs only say "any SD card up to 16Gb is supported".
- **Conclusion: 4 Gb → 2 Gb (256 MB) or 1 Gb (128 MB) needs no firmware change.**
  `sdcardio` auto-detects CSD capacity and `VfsFat` handles FAT12/16/32. Going *up* (8 Gb) is
  also fine. Only operational consequence is less log/telemetry headroom before wraparound —
  and since there is no rotation logic today, a smaller card fills sooner. That is a mission-ops
  consideration, not a code change.
- Default baudrate is 400 kHz, far below the 50 MHz these parts support — no timing risk from
  any candidate.
- Related open item: proveskit/pysquared#91 (clock-speed vs SD throughput). Unrelated to part choice.

## 5. Off-JLC sourcing of the exact ZDSD04GLGEAG (consignment)

- **LCSC.com direct**: C2875854 listed but **out of stock**; historic price $17.58 / $13.62@100,
  480 pcs per tray. Stock has historically returned (497 → 192 → 0 since Feb 2026 is a
  drawdown, not a discontinuation notice).
- **JLCPCB**: jlcpcb.com/partdetail/Zetta-ZDSD04GLGEAG/C2875854 — same zero.
- **DigiKey / Mouser / Arrow**: **no listings.** Zetta SD-NAND is not carried by Western
  franchised distributors at all.
- Gray-market / Asian brokers that list it: SemiKey, Walsoon, YYIC, Unikeyic, Sekorm.
  **No verifiable live stock or lead time** retrievable. Broker-sourced managed-NAND for a
  flight article is a counterfeit/remarking risk — not recommended without incoming inspection.
- Factory: zettadevice.com — direct/distributor lead time not published; would need an RFQ.
  Typical SD-NAND factory lead time is 8–12 weeks, which likely misses the build window.

**Consignment verdict:** only worth pursuing if you can get a franchised/factory-direct quote
with a firm date. Otherwise it adds schedule risk plus a JLCPCB consignment handling fee and
a hand-placed part.

## 6. Recommendation

### Primary: **ZDSD02GLGEAG — LCSC C2875853** (2 Gb / 256 MB). Confidence: **HIGH.**
- Same manufacturer, same product family, **same datasheet document** as the current part —
  the ZDSD01G/02G/04G datasheet covers all three with one package drawing and one pin table.
  Pinout and land pattern are guaranteed identical; the only delta is die capacity.
- 732 in stock, −30..+85 °C (identical grade to the current part), ~CNY 6.25 @100 (cheaper).
- **Zero PCB change. Zero firmware change.** Only the BOM `Value`/`LCSC Part` fields on U2.
- Cost: halved storage, 512 MB → 256 MB.

**Must verify before committing (short):**
1. Confirm C2875853 stock is still ≥ your build qty at order time (it is an Extended part —
   JLCPCB may require ordering full qty + extended-part fee).
2. Confirm JLCPCB has it in the **assembly** (SMT) catalogue, not just LCSC retail.

### If you want to keep 4 Gb: **MKDV4GIL-AST — LCSC C26159626.** Confidence: **MEDIUM-HIGH.**
- 4 Gb, LGA-8 6x8, **−40..+85 °C industrial** (better than the Zetta −30 part for a CubeSat),
  2087 in stock, ~CNY 15.39 @100, SPI + SD mode, ECC + bad-block management, 100k cycles.
- MK datasheet pin table is pin-for-pin identical to Zetta (1 DAT2, 2 DAT3/CS, 3 CLK, 4 GND,
  5 CMD, 6 DAT0, 7 DAT1, 8 VDD); body 8.00 x 6.00, pitch 1.27, column span 3.81 BSC.
- **Must verify before committing:**
  1. Download the **-AST**-specific datasheet from LCSC (C26159626), not the older -AS rev —
     confirm the pin table and package drawing (the -AST is a newer generation).
  2. Chip pad width b (0.55–0.60) vs Zetta (0.60): your 0.80 mm pad width gives ≥0.10 mm
     side clearance either way — **fine, no change needed**.
  3. Chip pad length L 0.80–0.85 vs your 1.70 mm land: gives ~0.85 mm outward toe fillet. Fine.
  4. Confirm the pin-1 dot is on the DAT2 corner in the same orientation (all vendors show it
     at the DAT2/pin-1 corner) — **do not rotate the footprint**; U2 is on B.Cu at −90°, pin 1
     at footprint-local (−3.7, +1.91).
  5. Confirm SPI-mode support is present in the exact SKU (the -AST LCSC description says
     "SPI、SD interface"; the -ABF 1G/2G/4G describe "SD interface" only — **avoid the -ABF
     parts** unless SPI is confirmed, since our board is SPI-only wired).
  6. Confirm CMD0-entry-to-SPI behaves with `sdcardio` at 400 kHz init (standard; low risk).

### Do NOT choose
- `CSNP4GCR01-BPW` (C47345841): stock = 1.
- Any `LGA-8(6.2x8)`, `(6.6x8)` or `(7x8.5)` part (CSNP16G/32G/64G, MKDV*-STP): **different body,
  land pattern not verified** — would need a footprint change.
- Any `WSON-8` FORESEE/XTX part: raw SPI-NAND, wrong protocol *and* wrong land pattern.
- XTX `XTSDQ01GLAIGA`: LGA-8 **6x5**, wrong body.

### Footprint change / Rev3
**Not required.** The existing `LGA-8_L8.0-W6.0-P1.27-TL-1` footprint is correct and is the common
land pattern for the whole 8x6 SD-NAND class (Zetta, MK, CSNP 6x8, XTX 6x8). Nothing to change
to ship this board.

Optional Rev3 improvements (not blockers):
- Add 10k pull-ups on `SPI1_MOSI` (DI) and `SPI1_MISO` (DO) per SD-spec recommendation.
- Move a 100nF decoupling cap to within ~2 mm of U2 pin 8 (nearest is currently 5.8 mm).
- Consider tying DAT1/DAT2 (pins 7/1) to +3V3 through 10k–100k rather than leaving them floating.
- Fit a second-source-friendly BOM note: this footprint accepts Zetta ZDSD*, MK MKDV*-A**(6x8),
  CSNP*CR01 (6x8) and XTX XTSD*GLGEAG interchangeably.

### Bottom line
Swap U2 to **C2875853 (ZDSD02GLGEAG, 2 Gb)** and order now — no layout change, no firmware change,
and it is the same silicon family you already validated. If 512 MB is a hard requirement, use
**C26159626 (MKDV4GIL-AST)** after a 10-minute datasheet pad/pin check; it is also the better
temperature grade.

---

## Addendum — local PROVES repos (found after initial write)

Local clones under `/Users/ncc-michael/GitHut/`: `pysquared`, `proves-core-reference` (Zephyr),
`proves_circuitpython`, `proves-zephyr`, `pysquared_zephyr`, `proves-prime-mainboard`, etc.
Both flight-software stacks were checked; **neither changes the conclusion**.

### CircuitPython stack — `pysquared` (local clone confirms the web finding)
`/Users/ncc-michael/GitHut/pysquared/pysquared/circuitpython-workspaces/flight-software/src/pysquared/hardware/sd_card/manager/sd_card.py`
line 24: `sd = sdcardio.SDCard(spi_bus, chip_select, baudrate)` → `storage.VfsFat` → `storage.mount`.
No capacity, block-count, FAT-type or rotation logic. `sdioio` is never used anywhere.

### Zephyr stack — `proves-core-reference` (**new, and it corroborates the wiring**)
`/Users/ncc-michael/GitHut/proves-core-reference/boards/bronco_space/proves_flight_control_board_v5/proves_flight_control_board_v5.dtsi`:
```dts
&spi0 {
    cs-gpios = <&gpio0 15 GPIO_ACTIVE_LOW>, <&gpio0 7 GPIO_ACTIVE_LOW>;
    sdhc0: sdhc@0 {
        compatible = "zephyr,sdhc-spi-slot";
        reg = <0>;
        mmc { compatible = "zephyr,sdmmc-disk"; disk-name = "SD"; };
        spi-max-frequency = <24000000>;
    };
};
```
- **`zephyr,sdhc-spi-slot` = SPI mode**, on **spi0 CS index 0 = GPIO15** — exactly U2's `SPI1_CS1`.
  GPIO7 is CS index 1 (the radio). This independently confirms the §1 pin mapping.
- **`spi-max-frequency = 24 MHz`** (vs CircuitPython's 400 kHz default). Every candidate part is
  rated 50 MHz, so 24 MHz is safe for Zetta ZDSD02G, MK MKDV4GIL-AST and CSNP alike. Note the
  one exception in the candidate table: `CSNP1GCR01-BOW` is spec'd **25 MHz**, still ≥24 MHz but
  with no margin — another reason to prefer the 50 MHz parts.
- `prj.conf` lines 69–77: `CONFIG_SDHC`, `CONFIG_DISK_ACCESS`, `CONFIG_FAT_FILESYSTEM_ELM`,
  `CONFIG_FS_FATFS_EXFAT`, `CONFIG_FS_FATFS_MOUNT_MKFS`, `CONFIG_FS_FATFS_FSTAB_AUTOMOUNT`,
  `CONFIG_FILE_SYSTEM_MKFS`.
  - **No capacity/partition/size constant anywhere** (`grep` for `DISK_`, `statvfs`, `f_getfree`,
    `fs_mount`, `mkfs` in `src`/`app`/`boards` returns only the `disk-name = "SD"` line).
  - `MOUNT_MKFS` means it auto-formats on mount failure; ELM FatFs picks FAT12/FAT16/FAT32 from
    the volume size on its own, so a 256 MB or 128 MB device formats fine. exFAT is enabled but
    not required at these sizes.

### Net effect on §4 and §6
**Unchanged: 4 Gb → 2 Gb (or 1 Gb) requires no firmware change in either stack.** Both drive the
part as a generic SPI-mode SD card with auto-detected capacity and auto-selected FAT type.
The only added constraint the Zephyr DTS introduces is a **24 MHz SPI clock floor**, which the
recommended parts (ZDSD02GLGEAG and MKDV4GIL-AST, both 50 MHz) clear comfortably.
