# Package, Pinout & I/O Specification

| Field | Value |
|---|---|
| Doc ID | KST-PKG-002 |
| Title | Package, Pinout & I/O Specification |
| Revision | C (supersedes B) |
| Date | 2026-09-21 |
| Owner | Rachel Lindqvist (Package & I/O Lead) |
| Status | Released for TRR-3 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

Applicable tape-out package: **C** (TRR-3, 2026-09-25). Netlist `kst_top_nl_2026.09.19`; pad-ring database release PR-15 (unchanged since B); substrate design SUB-R07; ball-map source file `kst_ballmap_revC.csv`.

## Revision history

| Rev | Date | Author | Description |
|---|---|---|---|
| A | 2026-08-11 | Rachel Lindqvist | Initial controlled release for TRR-1. Supersedes working draft 0.8 (2026-07-22). |
| B | 2026-09-01 | Rachel Lindqvist | CHG-B-001: NC balls AR44, AT44, AU44, AV44, AW44, AY44 re-labelled TP_0..TP_5 (documentation only). |
| B | 2026-09-01 | Rachel Lindqvist | CHG-B-002: GPIO_B I/O cells changed from IO_GPIO_1V2 to IO_GPIO_1V8 and VDDIO_B from 1.2 V to 1.8 V to match KST-ARCH-001 (1.8 V QSPI0 boot flash and SPI1 sensor); 16 pad-ring cells swapped; ball map unchanged. |
| C | 2026-09-21 | Rachel Lindqvist | No design change since B; section 9 checks re-run against netlist kst_top_nl_2026.09.19; re-issued for TRR-3. |

## 1. Scope and references

This specification defines the ALX-5100 package, the ball assignment, the composition of the GPIO pad-ring segment, the I/O cell selected for each bank, and the allocation of power and ground balls. ALX-5100 and ALX-5100I use the same package and ball map. Interface definitions are taken from KST-ARCH-001; the GPIO library release is listed in KST-IPBOM-050.

| Doc ID | Title / relationship |
|---|---|
| KST-ARCH-001 | Architecture Specification: interface signal list, SKUs, rails, power sequencing |
| KST-IPBOM-050 | IP Bill of Materials: GPIO-N5-LIB, PCIE5-PHY-N5, PHY-LP5X-N5 releases |
| KST-PI-040 | Power Integrity Sign-off Report: package model and power-ball allocation used for IR/EM |
| KST-RC1-SCH | Reference card (CEM x16, 150 W, one 2x3 6-pin aux) schematic, rev P2 (VDDIO_1V8_B rail) |
| SUB-R07 | Package substrate design database |
| ALD-QA-CHK-007 rev 7.2 | Tape-out Readiness Checklist |

## 2. Package summary

| Parameter | Value |
|---|---|
| Package type | Flip-chip BGA (FCBGA), lidded, single die |
| Body size | 45.0 mm x 45.0 mm |
| Ball count / array | 2,304 balls, 48 x 48 full array |
| Ball pitch | 0.8 mm |
| Ball composition / diameter | SAC305, 0.45 mm pre-reflow |
| Ball naming | Rows A..BH (JEDEC lettering; I, O, Q, S, X, Z not used), columns 1..48 |
| Substrate | 16-layer (7-2-7) build-up, 1.2 mm core |
| Die size | 19.20 mm x 18.80 mm (360.96 mm^2), foundry N5-class |
| Die attach | Cu-pillar bumps: 150 um pitch in the core power array, 130 um minimum in the PHY and I/O fields; ~14,600 bumps (10,168 core-rail power/ground: VDD_NPU, VDD_CORE, VDD_SRAM, VDD_AON, VSS; PHY and I/O supply bumps are counted in their own fields); capillary underfill |
| Lid / TIM1 | Nickel-plated copper lid; polymer TIM1 |
| Die-side capacitors (substrate top, around the die) | 44: VDD_NPU 24 x 2.2 uF, VDD_CORE 12 x 2.2 uF, VDD_SRAM 6 x 1.0 uF, VDD_AON 2 x 0.1 uF (low-ESL) |
| Package height | 3.40 mm max, seated |
| Coplanarity | 0.20 mm max |
| Theta-JC | 0.07 C/W |
| MSL / peak reflow | MSL 4 / 260 C |
| Operating Tj | 0 C to +105 C (ALX-5100); -40 C to +105 C (ALX-5100I) |
| ESD | HBM 1 kV, CDM 250 V (all balls) |

## 3. I/O cell library

### 3.1 Cells used in the pad ring

All cells are from the GPIO-N5-LIB library (release per KST-IPBOM-050).

| Cell | Description | Operating VDDIO | Max VDDIO | Abs. max pad voltage | Drive strengths | Instances |
|---|---|---|---|---|---|---|
| IO_GPIO_1V2 | 1.2 V-only GPIO, 1.2 V I/O devices | 1.2 V | 1.32 V | VDDIO + 0.3 V (1.50 V at 1.2 V) | 2/4/8/12 mA | 16 |
| IO_GPIO_1V8 | 1.8 V/1.2 V dual-voltage GPIO, 1.8 V overdrive I/O devices | 1.8 V or 1.2 V | 1.98 V | VDDIO + 0.3 V (2.10 V at 1.8 V) | 2/4/8/12/16 mA | 36 |
| IO_IN_1V8_ST | Input-only Schmitt-trigger cell, 1.8 V overdrive devices | 1.8 V | 1.98 V | VDDIO + 0.3 V (2.10 V) | - | 2 |
| IO_XTAL_1V8 | Pierce crystal-oscillator cell, 25 MHz | 1.8 V | 1.98 V | VDDIO + 0.3 V (2.10 V) | - | 2 |
| IO_ANA | Analog pass-through with secondary ESD | - | - | 2.10 V | - | 3 |
| IO_PVDDIO_DV | Bank VDDIO supply cell with rail clamp (both GPIO families) | 1.2 V / 1.8 V | 1.98 V | - | - | 13 |
| IO_PVSS | I/O ground cell | - | - | - | - | 14 |
| IO_POC_DV | Power-on control: holds the bank outputs tri-stated until VDD_CORE is valid | 1.2 V / 1.8 V | 1.98 V | - | - | 4 |
| IO_BRK_DV | Ring breaker: splits VDDIO between banks, VSS continuous | - | - | - | - | 4 |
| IO_CORNER | Corner cell | - | - | - | - | 2 |

IO_GPIO_1V8 has a static supply-select pin V18 that is tied per bank (1 = 1.8 V operation, 0 = 1.2 V operation). Pull resistors are 50 kOhm typical (30 to 80 kOhm). Input leakage is +/-5 uA max.

### 3.2 DC characteristics (library data, worst case over PVT)

| Cell @ VDDIO | VIH min | VIL max | VOH min (at rated drive) | VOL max | Hysteresis | Max toggle rate |
|---|---|---|---|---|---|---|
| IO_GPIO_1V2 @ 1.2 V | 0.78 V | 0.42 V | 0.90 V | 0.30 V | 60 mV | 200 MHz |
| IO_GPIO_1V8 @ 1.8 V | 1.17 V | 0.63 V | 1.35 V | 0.45 V | 100 mV | 200 MHz |
| IO_GPIO_1V8 @ 1.2 V | 0.78 V | 0.42 V | 0.90 V | 0.30 V | 60 mV | 150 MHz |
| IO_IN_1V8_ST @ 1.8 V | 1.26 V | 0.54 V | - | - | 200 mV | - |

## 4. I/O banks

| Bank | Pins | I/O cell | VDDIO | Supply | V18 tie | Segment | Functions |
|---|---|---|---|---|---|---|---|
| GPIO_A | 12 | IO_GPIO_1V8 | 1.8 V | VDDIO_A | 1 | E2 | JTAG, UART0, boot/debug straps, 2 spare; scan channels in TEST_MODE |
| GPIO_B | 16 | IO_GPIO_1V8 | 1.8 V | VDDIO_B | 1 | E3 | QSPI0 boot flash, SPI1 telemetry sensor, SENSOR_ALERT_N, 4 spare (CHG-B-002) |
| GPIO_C | 16 | IO_GPIO_1V2 | 1.2 V | VDDIO_C | n/a | E4 | Card-management CPLD, LEDs, PWR_GOOD inputs, THERMTRIP_N, PROCHOT_N |
| GPIO_D | 8 | IO_GPIO_1V8 | 1.8 V | VDDIO_D | 1 | E5 | I2C0/I2C1 (SMBus), PCIE0_PERST_N, PCIE0_CLKREQ_N, PCIE0_WAKE_N, SMB_ALERT_N |

52 GPIO pins in 4 banks. Each bank has its own VDDIO balls and its own power-on-control cell; banks are separated by ring breakers.

## 5. Supplies and ball allocation

### 5.1 Supplies

| Supply | Nominal | Balls | Reference-card rail | Notes |
|---|---|---|---|---|
| VDD_CORE | 0.750 V | 220 | VR_CORE (multiphase) | Core logic; PD_PCIE1 header input |
| VDD_NPU | 0.750 V | 300 | VR_NPU (multiphase) | NPU clusters PD_NPU0..PD_NPU3 |
| VDD_SRAM | 0.800 V | 64 | VR_SRAM | SRAM arrays |
| VDD_AON | 0.750 V | 8 | LDO_AON | Always-on domain |
| VDDIO_A | 1.8 V | 3 | VDDIO_1V8 | GPIO_A bank supply; XTAL, PORST_N, TEST_MODE |
| VDDIO_B | 1.8 V | 4 | VDDIO_1V8_B (dedicated) | GPIO_B bank supply (CHG-B-002) |
| VDDIO_C | 1.2 V | 4 | VDDIO_1V2 | GPIO_C bank supply |
| VDDIO_D | 1.8 V | 2 | VDDIO_1V8 | GPIO_D bank supply |
| VDDA_PCIE_0V75 | 0.75 V | 24 | LDO_PCIE_0V75 | PCIE0 and PCIE1 PHY analog |
| VDDA_PCIE_1V2 | 1.2 V | 12 | LDO_PCIE_1V2 | PCIE0 and PCIE1 PHY analog |
| VDDQ_LPX_0V5 | 0.50 V | 64 | VR_VDDQ (shared with DRAM VDDQ) | LPDDR5X PHY I/O |
| VDDA_LPX_0V75 | 0.75 V | 24 | LDO_LPX_0V75 | LPDDR5X PHY analog |
| VDDA_PLL_0V75 | 0.75 V | 4 | LDO_PLL (ferrite-filtered) | 4 fractional PLLs |
| VPP_OTP | 1.8 V | 1 | ATE only; 10 kOhm to VSS on boards | OTP programming |
| VSS | 0 V | 803 | GND | Common ground, all regions |

### 5.2 Ball-count summary

| Category | Balls |
|---|---|
| PCIE0: 16 lanes x (TXP, TXN, RXP, RXN), REFCLK_P/N, RESREF | 67 |
| PCIE1: 8 lanes x (TXP, TXN, RXP, RXN), REFCLK_P/N, RESREF | 35 |
| LPDDR5X: 32 byte lanes (BL0..BL31) x 13, 16 channels x 11 (CA, CS, CK), 4 x RESET_N, 4 x ZQ | 600 |
| GPIO_A..GPIO_D | 52 |
| Dedicated: XTAL_IN, XTAL_OUT, PORST_N, TEST_MODE, THERM_DP, THERM_DN, ATB0 | 7 |
| **Signal subtotal** | **761** |
| Power (14 supplies, section 5.1) | 734 |
| VSS | 803 |
| Reserved test pads TP_0..TP_5: AR44, AT44, AU44, AV44, AW44, AY44 (CHG-B-001) | 6 |
| **Total** | **2,304** |

### 5.3 Power and ground balls by region

| Rail | Center | West | North | South | East | Total |
|---|---|---|---|---|---|---|
| VDD_CORE | 190 | 10 | 10 | 6 | 4 | 220 |
| VDD_NPU | 300 | 0 | 0 | 0 | 0 | 300 |
| VDD_SRAM | 64 | 0 | 0 | 0 | 0 | 64 |
| VDD_AON | 4 | 0 | 0 | 0 | 4 | 8 |
| VDDIO_A | 0 | 0 | 0 | 0 | 3 | 3 |
| VDDIO_B | 0 | 0 | 0 | 0 | 4 | 4 |
| VDDIO_C | 0 | 0 | 0 | 0 | 4 | 4 |
| VDDIO_D | 0 | 0 | 0 | 0 | 2 | 2 |
| VDDA_PCIE_0V75 | 0 | 0 | 0 | 16 | 8 | 24 |
| VDDA_PCIE_1V2 | 0 | 0 | 0 | 8 | 4 | 12 |
| VDDQ_LPX_0V5 | 0 | 32 | 32 | 0 | 0 | 64 |
| VDDA_LPX_0V75 | 0 | 12 | 12 | 0 | 0 | 24 |
| VDDA_PLL_0V75 | 4 | 0 | 0 | 0 | 0 | 4 |
| VPP_OTP | 0 | 0 | 0 | 0 | 1 | 1 |
| VSS | 399 | 150 | 134 | 70 | 50 | 803 |
| Signal / TP balls | 0 | 300 | 300 | 67 | 100 | 767 |
| **Region total** | 961 | 504 | 488 | 167 | 184 | **2,304** |

Regions in this table are substrate power-plane quadrants; they differ from the signal-region boundaries in section 7.2. Ball current capacity is 0.35 A per ball at Tj = 105 C. Worst case is VDD_NPU at 0.21 A per ball at TDP.

## 6. Pad ring

### 6.1 Die-edge assignment

| Die edge | Contents |
|---|---|
| West | LPDDR5X PHY hard macros u_ddr_ss/u_phy0 and u_ddr_ss/u_phy1 |
| North | LPDDR5X PHY hard macros u_ddr_ss/u_phy2 and u_ddr_ss/u_phy3 |
| East (north part) | GPIO pad-ring segment E0..E6 (this section) |
| East (south part) | PCIE1 x8 PHY hard macro (u_pcie1_wrap) |
| South | PCIE0 x16 PHY hard macro (u_pcie0_wrap) |

### 6.2 GPIO segment order (east edge, north to south)

| Seq | Segment | Cells | Supply | Notes |
|---|---|---|---|---|
| E0 | Corner (NE) | 1 x IO_CORNER | - | |
| E1 | Dedicated | 2 x IO_XTAL_1V8, 2 x IO_IN_1V8_ST, 3 x IO_ANA | VDDIO_A | XTAL_IN/OUT, PORST_N, TEST_MODE; THERM_DP/DN, ATB0 |
| E2 | GPIO_A | 12 x IO_GPIO_1V8, 3 x IO_PVDDIO_DV, 4 x IO_PVSS, 1 x IO_POC_DV | VDDIO_A | V18 = 1 |
| - | Breaker | 1 x IO_BRK_DV | - | VDDIO_A / VDDIO_B split |
| E3 | GPIO_B | 16 x IO_GPIO_1V8, 4 x IO_PVDDIO_DV, 4 x IO_PVSS, 1 x IO_POC_DV | VDDIO_B | V18 = 1 (CHG-B-002) |
| - | Breaker | 1 x IO_BRK_DV | - | VDDIO_B / VDDIO_C split |
| E4 | GPIO_C | 16 x IO_GPIO_1V2, 4 x IO_PVDDIO_DV, 4 x IO_PVSS, 1 x IO_POC_DV | VDDIO_C | |
| - | Breaker | 1 x IO_BRK_DV | - | VDDIO_C / VDDIO_D split |
| E5 | GPIO_D | 8 x IO_GPIO_1V8, 2 x IO_PVDDIO_DV, 2 x IO_PVSS, 1 x IO_POC_DV | VDDIO_D | V18 = 1 |
| E6 | End cap | 1 x IO_BRK_DV, 1 x IO_CORNER | - | Segment end; PCIE1 PHY macro follows |

## 7. Ball map

### 7.1 Convention

Viewed from the top (lid side), ball A1 is the top-left corner (marked on the lid). Letters index rows A..BH from top to bottom; numbers index columns 1..48 from left to right. Example: AR44 is row AR, column 44. North = rows A..N, south = rows BC..BH, west = columns 1..12, east = columns 43..48.

### 7.2 Region map

| Region | Rows | Columns | Contents |
|---|---|---|---|
| West | C..BA | 1..12 | MEM0 (rows C..Y) and MEM1 (rows AA..BA) LPDDR5X signals, VDDQ_LPX_0V5, VDDA_LPX_0V75, VSS |
| North | A..N | 13..42 | MEM2 (columns 13..27) and MEM3 (columns 28..42) LPDDR5X signals, VDDQ_LPX_0V5, VDDA_LPX_0V75, VSS |
| North-east | A..D | 43..44 (and A45..A47, C45) | XTAL_IN, XTAL_OUT, PORST_N, TEST_MODE (row A), THERM_DP/DN, ATB0 (C44, C45, D44), VSS |
| East, upper | B..AG | 45..48 | GPIO_A..GPIO_D, VDDIO_A..VDDIO_D, VDD_AON, VPP_OTP, VSS |
| East, lower | AH..BC | 44..48 | PCIE1 lanes, REFCLK, RESREF, VDDA_PCIE_*, VSS; column 44 rows AR..AY reserved test pads TP_0..TP_5 (section 7.12) |
| South | BC..BH | 2..37 | PCIE0 lanes, REFCLK, RESREF, VDDA_PCIE_0V75, VDDA_PCIE_1V2, VSS |
| Center | P..BB | 13..43 | Core power array: VDD_CORE, VDD_NPU, VDD_SRAM, VDD_AON, VDDA_PLL_0V75, VSS |

### 7.3 GPIO_A

| Ball | Pin / function | Bank | I/O cell | Drive | Pull | Dir | Notes |
|---|---|---|---|---|---|---|---|
| B48 | GPIO_A0 / JTAG_TCK | GPIO_A | IO_GPIO_1V8 | - | PD | I | Schmitt input |
| B47 | GPIO_A1 / JTAG_TMS | GPIO_A | IO_GPIO_1V8 | - | PU | I |  |
| C48 | GPIO_A2 / JTAG_TDI | GPIO_A | IO_GPIO_1V8 | - | PU | I |  |
| C47 | GPIO_A3 / JTAG_TDO | GPIO_A | IO_GPIO_1V8 | 8 mA | none | O | Tri-state outside Shift-DR/Shift-IR |
| D48 | GPIO_A4 / JTAG_TRST_N | GPIO_A | IO_GPIO_1V8 | - | PD | I | TAP held in reset when undriven |
| D47 | GPIO_A5 / UART0_TXD | GPIO_A | IO_GPIO_1V8 | 4 mA | none | O | TEST_MODE: scan out 0 |
| E48 | GPIO_A6 / UART0_RXD | GPIO_A | IO_GPIO_1V8 | - | PU | I | TEST_MODE: scan in 0 |
| E47 | GPIO_A7 / BOOT_SEL0 | GPIO_A | IO_GPIO_1V8 | - | PD | I | Strap, sampled at PORST_N release; TEST_MODE: scan in 1 |
| F48 | GPIO_A8 / BOOT_SEL1 | GPIO_A | IO_GPIO_1V8 | - | PD | I | Strap; TEST_MODE: scan out 1 |
| F47 | GPIO_A9 / SEC_DBG_REQ | GPIO_A | IO_GPIO_1V8 | - | PD | I | Strap; TEST_MODE: scan in 2 |
| G48 | GPIO_A10 | GPIO_A | IO_GPIO_1V8 | 4 mA | PD | I/O | Spare; TEST_MODE: scan out 2 |
| G47 | GPIO_A11 | GPIO_A | IO_GPIO_1V8 | 4 mA | PD | I/O | Spare; TEST_MODE: optional low-speed (<= 50 MHz) external shift clock for bring-up; production shift uses the internal OCC scan_clk |

GPIO_A supply balls: B46, D46, F46.

### 7.4 GPIO_B

| Ball | Pin / function | Bank | I/O cell | Drive | Pull | Dir | Notes |
|---|---|---|---|---|---|---|---|
| J48 | GPIO_B0 / QSPI0_CLK | GPIO_B | IO_GPIO_1V8 | 8 mA | none | O | Boot flash clock, 133 MHz SDR; 22 ohm series R on card |
| J47 | GPIO_B1 / QSPI0_CS0_N | GPIO_B | IO_GPIO_1V8 | 4 mA | PU | O |  |
| K48 | GPIO_B2 / QSPI0_DQ0 | GPIO_B | IO_GPIO_1V8 | 8 mA | none | I/O |  |
| K47 | GPIO_B3 / QSPI0_DQ1 | GPIO_B | IO_GPIO_1V8 | 8 mA | none | I/O |  |
| L48 | GPIO_B4 / QSPI0_DQ2 | GPIO_B | IO_GPIO_1V8 | 8 mA | PU | I/O | WP_N in single-SPI mode |
| L47 | GPIO_B5 / QSPI0_DQ3 | GPIO_B | IO_GPIO_1V8 | 8 mA | PU | I/O | HOLD_N in single-SPI mode |
| M48 | GPIO_B6 / QSPI0_RST_N | GPIO_B | IO_GPIO_1V8 | 4 mA | PD | O | Released by boot ROM |
| M47 | GPIO_B7 / SPI1_SCLK | GPIO_B | IO_GPIO_1V8 | 4 mA | none | O | Telemetry sensor, 20 MHz |
| N48 | GPIO_B8 / SPI1_CS0_N | GPIO_B | IO_GPIO_1V8 | 4 mA | PU | O |  |
| N47 | GPIO_B9 / SPI1_MOSI | GPIO_B | IO_GPIO_1V8 | 4 mA | none | O |  |
| P48 | GPIO_B10 / SPI1_MISO | GPIO_B | IO_GPIO_1V8 | - | PD | I |  |
| P47 | GPIO_B11 / SENSOR_ALERT_N | GPIO_B | IO_GPIO_1V8 | - | PU | I | Wake-capable |
| R48 | GPIO_B12 | GPIO_B | IO_GPIO_1V8 | 4 mA | PD | I/O | Spare |
| R47 | GPIO_B13 | GPIO_B | IO_GPIO_1V8 | 4 mA | PD | I/O | Spare |
| T48 | GPIO_B14 | GPIO_B | IO_GPIO_1V8 | 4 mA | PD | I/O | Spare |
| T47 | GPIO_B15 | GPIO_B | IO_GPIO_1V8 | 4 mA | PD | I/O | Spare |

GPIO_B supply balls: J46, L46, N46, R46.

### 7.5 GPIO_C

| Ball | Pin / function | Bank | I/O cell | Drive | Pull | Dir | Notes |
|---|---|---|---|---|---|---|---|
| V48 | GPIO_C0 / CMC_SCLK | GPIO_C | IO_GPIO_1V2 | 4 mA | none | O | Card-management CPLD sideband |
| V47 | GPIO_C1 / CMC_CS_N | GPIO_C | IO_GPIO_1V2 | 4 mA | PU | O |  |
| W48 | GPIO_C2 / CMC_MOSI | GPIO_C | IO_GPIO_1V2 | 4 mA | none | O |  |
| W47 | GPIO_C3 / CMC_MISO | GPIO_C | IO_GPIO_1V2 | - | PD | I |  |
| Y48 | GPIO_C4 / CMC_IRQ_N | GPIO_C | IO_GPIO_1V2 | - | PU | I | Wake-capable |
| Y47 | GPIO_C5 / CMC_RST_REQ_N | GPIO_C | IO_GPIO_1V2 | 4 mA | PU | O |  |
| AA48 | GPIO_C6 / LED0 | GPIO_C | IO_GPIO_1V2 | 2 mA | none | O | Via board buffer |
| AA47 | GPIO_C7 / LED1 | GPIO_C | IO_GPIO_1V2 | 2 mA | none | O | Via board buffer |
| AB48 | GPIO_C8 / LED2 | GPIO_C | IO_GPIO_1V2 | 2 mA | none | O | Via board buffer |
| AB47 | GPIO_C9 / LED3 | GPIO_C | IO_GPIO_1V2 | 2 mA | none | O | Via board buffer |
| AC48 | GPIO_C10 / PG_VDD_CORE | GPIO_C | IO_GPIO_1V2 | - | PD | I | Power-good |
| AC47 | GPIO_C11 / PG_VDD_NPU | GPIO_C | IO_GPIO_1V2 | - | PD | I | Power-good |
| AD48 | GPIO_C12 / PG_VDDQ_LPX | GPIO_C | IO_GPIO_1V2 | - | PD | I | Power-good |
| AD47 | GPIO_C13 / PG_BOARD | GPIO_C | IO_GPIO_1V2 | - | PD | I | Power-good |
| AE48 | GPIO_C14 / THERMTRIP_N | GPIO_C | IO_GPIO_1V2 | 8 mA | none | O (OD) | Board pull-up; asserted at Tj = 120 C |
| AE47 | GPIO_C15 / PROCHOT_N | GPIO_C | IO_GPIO_1V2 | 8 mA | none | I/O (OD) | Board pull-up |

GPIO_C supply balls: V46, Y46, AB46, AD46.

### 7.6 GPIO_D

| Ball | Pin / function | Bank | I/O cell | Drive | Pull | Dir | Notes |
|---|---|---|---|---|---|---|---|
| AF48 | GPIO_D0 / I2C0_SCL | GPIO_D | IO_GPIO_1V8 | 8 mA | none | I/O (OD) | SMBus to host; level-shifted to 3.3 V on card |
| AF47 | GPIO_D1 / I2C0_SDA | GPIO_D | IO_GPIO_1V8 | 8 mA | none | I/O (OD) | SMBus to host; level-shifted to 3.3 V on card |
| AF46 | GPIO_D2 / I2C1_SCL | GPIO_D | IO_GPIO_1V8 | 8 mA | none | I/O (OD) | Local devices; 2.2 kOhm pull-up on card |
| AF45 | GPIO_D3 / I2C1_SDA | GPIO_D | IO_GPIO_1V8 | 8 mA | none | I/O (OD) | Local devices; 2.2 kOhm pull-up on card |
| AG48 | GPIO_D4 / PCIE0_PERST_N | GPIO_D | IO_GPIO_1V8 | - | none | I | Level-shifted from 3.3 V on card |
| AG47 | GPIO_D5 / PCIE0_CLKREQ_N | GPIO_D | IO_GPIO_1V8 | 8 mA | none | I/O (OD) | Level-shifted from 3.3 V on card |
| AG46 | GPIO_D6 / PCIE0_WAKE_N | GPIO_D | IO_GPIO_1V8 | 8 mA | none | O (OD) | Level-shifted from 3.3 V on card |
| AG45 | GPIO_D7 / SMB_ALERT_N | GPIO_D | IO_GPIO_1V8 | - | PU | I | Wake-capable |

GPIO_D supply balls: AE45, AE46.

### 7.7 Dedicated pins and special supplies

| Ball | Signal | Cell | Supply | Notes |
|---|---|---|---|---|
| A44 | XTAL_IN | IO_XTAL_1V8 | VDDIO_A | 25 MHz crystal, 12 pF load |
| A45 | XTAL_OUT | IO_XTAL_1V8 | VDDIO_A |  |
| A46 | PORST_N | IO_IN_1V8_ST | VDDIO_A | From board supervisor |
| A47 | TEST_MODE | IO_IN_1V8_ST | VDDIO_A | Internal pull-down; tie to VSS on production boards |
| C45 | THERM_DP | IO_ANA | - | Remote thermal diode anode |
| C44 | THERM_DN | IO_ANA | - | Remote thermal diode cathode |
| D44 | ATB0 | IO_ANA | - | Analog test bus; no connect on production boards |
| G46 | VPP_OTP | supply | - | ATE only; 10 kOhm to VSS on boards |
| H46, K45, T45, U46 | VDD_AON | supply | - | East-edge VDD_AON balls (4 of 8) |

### 7.8 PCIE0 (Gen5 x16 endpoint)

| Lane | TXP | TXN | RXP | RXN |
|---|---|---|---|---|
| 0 | BH3 | BG3 | BD3 | BC3 |
| 1 | BH5 | BG5 | BD5 | BC5 |
| 2 | BH7 | BG7 | BD7 | BC7 |
| 3 | BH9 | BG9 | BD9 | BC9 |
| 4 | BH11 | BG11 | BD11 | BC11 |
| 5 | BH13 | BG13 | BD13 | BC13 |
| 6 | BH15 | BG15 | BD15 | BC15 |
| 7 | BH17 | BG17 | BD17 | BC17 |
| 8 | BH19 | BG19 | BD19 | BC19 |
| 9 | BH21 | BG21 | BD21 | BC21 |
| 10 | BH23 | BG23 | BD23 | BC23 |
| 11 | BH25 | BG25 | BD25 | BC25 |
| 12 | BH27 | BG27 | BD27 | BC27 |
| 13 | BH29 | BG29 | BD29 | BC29 |
| 14 | BH31 | BG31 | BD31 | BC31 |
| 15 | BH33 | BG33 | BD33 | BC33 |

PCIE0_REFCLK_P BF35, PCIE0_REFCLK_N BE35 (100 MHz HCSL from the edge connector); PCIE0_RESREF BE37 (200 ohm 1% to VSS). Even columns between lanes in rows BC, BD, BG, BH are VSS. Signal names: PCIE0_TXP[n], PCIE0_TXN[n], PCIE0_RXP[n], PCIE0_RXN[n].

### 7.9 PCIE1 (Gen5 x8, fused off in ALX-5100)

| Lane | TXP | TXN | RXP | RXN | Board connection |
|---|---|---|---|---|---|
| 0 | AJ48 | AJ47 | AJ46 | AJ45 | NC on ALX-5100 boards, reserved ALX-5100X |
| 1 | AL48 | AL47 | AL46 | AL45 | NC on ALX-5100 boards, reserved ALX-5100X |
| 2 | AN48 | AN47 | AN46 | AN45 | NC on ALX-5100 boards, reserved ALX-5100X |
| 3 | AR48 | AR47 | AR46 | AR45 | NC on ALX-5100 boards, reserved ALX-5100X |
| 4 | AU48 | AU47 | AU46 | AU45 | NC on ALX-5100 boards, reserved ALX-5100X |
| 5 | AW48 | AW47 | AW46 | AW45 | NC on ALX-5100 boards, reserved ALX-5100X |
| 6 | BA48 | BA47 | BA46 | BA45 | NC on ALX-5100 boards, reserved ALX-5100X |
| 7 | BC48 | BC47 | BC46 | BC45 | NC on ALX-5100 boards, reserved ALX-5100X |

PCIE1_REFCLK_P AH48, PCIE1_REFCLK_N AH47, PCIE1_RESREF AH45: NC on ALX-5100 boards, reserved ALX-5100X. The PCIE1 lanes are bonded out; with FUSE_PCIE1_DIS=1 the PHY lanes are held powered down. VDDA_PCIE_0V75 and VDDA_PCIE_1V2 are shared with PCIE0 and remain connected.

### 7.10 LPDDR5X data by byte lane

Each byte lane carries DQ[7:0], DMI, RDQS_T/RDQS_C and WCK_T/WCK_C (13 balls). Signal names: LP5X_CHn_DQ[15:0], LP5X_CHn_DMI[1:0], LP5X_CHn_RDQS[1:0]_T/C, LP5X_CHn_WCK[1:0]_T/C.

| Byte lane | Channel | PHY (subsystem) | Region | DQ | DMI / RDQS / WCK | Balls |
|---|---|---|---|---|---|---|
| BL0 | CH0 | u_ddr_ss/u_phy0 (MEM0) | West | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL1 | CH0 | u_ddr_ss/u_phy0 (MEM0) | West | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL2 | CH1 | u_ddr_ss/u_phy0 (MEM0) | West | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL3 | CH1 | u_ddr_ss/u_phy0 (MEM0) | West | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL4 | CH2 | u_ddr_ss/u_phy0 (MEM0) | West | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL5 | CH2 | u_ddr_ss/u_phy0 (MEM0) | West | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL6 | CH3 | u_ddr_ss/u_phy0 (MEM0) | West | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL7 | CH3 | u_ddr_ss/u_phy0 (MEM0) | West | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL8 | CH4 | u_ddr_ss/u_phy1 (MEM1) | West | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL9 | CH4 | u_ddr_ss/u_phy1 (MEM1) | West | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL10 | CH5 | u_ddr_ss/u_phy1 (MEM1) | West | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL11 | CH5 | u_ddr_ss/u_phy1 (MEM1) | West | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL12 | CH6 | u_ddr_ss/u_phy1 (MEM1) | West | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL13 | CH6 | u_ddr_ss/u_phy1 (MEM1) | West | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL14 | CH7 | u_ddr_ss/u_phy1 (MEM1) | West | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL15 | CH7 | u_ddr_ss/u_phy1 (MEM1) | West | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL16 | CH8 | u_ddr_ss/u_phy2 (MEM2) | North | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL17 | CH8 | u_ddr_ss/u_phy2 (MEM2) | North | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL18 | CH9 | u_ddr_ss/u_phy2 (MEM2) | North | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL19 | CH9 | u_ddr_ss/u_phy2 (MEM2) | North | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL20 | CH10 | u_ddr_ss/u_phy2 (MEM2) | North | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL21 | CH10 | u_ddr_ss/u_phy2 (MEM2) | North | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL22 | CH11 | u_ddr_ss/u_phy2 (MEM2) | North | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL23 | CH11 | u_ddr_ss/u_phy2 (MEM2) | North | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL24 | CH12 | u_ddr_ss/u_phy3 (MEM3) | North | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL25 | CH12 | u_ddr_ss/u_phy3 (MEM3) | North | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL26 | CH13 | u_ddr_ss/u_phy3 (MEM3) | North | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL27 | CH13 | u_ddr_ss/u_phy3 (MEM3) | North | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL28 | CH14 | u_ddr_ss/u_phy3 (MEM3) | North | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL29 | CH14 | u_ddr_ss/u_phy3 (MEM3) | North | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |
| BL30 | CH15 | u_ddr_ss/u_phy3 (MEM3) | North | DQ[7:0] | DMI0, RDQS0_T/C, WCK0_T/C | 13 |
| BL31 | CH15 | u_ddr_ss/u_phy3 (MEM3) | North | DQ[15:8] | DMI1, RDQS1_T/C, WCK1_T/C | 13 |

### 7.11 LPDDR5X command, clock and control

| Subsystem | Channels | Per channel | Per subsystem | Balls |
|---|---|---|---|---|
| MEM0 (u_ddr_ss/u_phy0) | CH0..CH3 | CA[6:0], CS[1:0], CK_T/C (11) | LP5X_0_RESET_N, LP5X_0_ZQ | 46 |
| MEM1 (u_ddr_ss/u_phy1) | CH4..CH7 | CA[6:0], CS[1:0], CK_T/C (11) | LP5X_1_RESET_N, LP5X_1_ZQ | 46 |
| MEM2 (u_ddr_ss/u_phy2) | CH8..CH11 | CA[6:0], CS[1:0], CK_T/C (11) | LP5X_2_RESET_N, LP5X_2_ZQ | 46 |
| MEM3 (u_ddr_ss/u_phy3) | CH12..CH15 | CA[6:0], CS[1:0], CK_T/C (11) | LP5X_3_RESET_N, LP5X_3_ZQ | 46 |

Total LPDDR5X signal balls: 32 x 13 + 4 x 46 = 600.

### 7.12 Reserved test pads

| Ball | Name | Notes |
|---|---|---|
| AR44 | TP_0 | Reserved test pad, shorted in pairs in the substrate for ATE socket continuity check; no die connection; leave unconnected on boards (CHG-B-001) |
| AT44 | TP_1 | Reserved test pad, shorted in pairs in the substrate for ATE socket continuity check; no die connection; leave unconnected on boards (CHG-B-001) |
| AU44 | TP_2 | Reserved test pad, shorted in pairs in the substrate for ATE socket continuity check; no die connection; leave unconnected on boards (CHG-B-001) |
| AV44 | TP_3 | Reserved test pad, shorted in pairs in the substrate for ATE socket continuity check; no die connection; leave unconnected on boards (CHG-B-001) |
| AW44 | TP_4 | Reserved test pad, shorted in pairs in the substrate for ATE socket continuity check; no die connection; leave unconnected on boards (CHG-B-001) |
| AY44 | TP_5 | Reserved test pad, shorted in pairs in the substrate for ATE socket continuity check; no die connection; leave unconnected on boards (CHG-B-001) |

## 8. Reference-card design notes

- PCIE0 TX pairs: 220 nF AC-coupling capacitors (0201) placed near the package; RX pairs are AC-coupled on the host side. Intra-pair skew <= 0.1 mm.
- PCIE1 balls and PCIE1_RESREF are left unconnected on ALX-5100 boards (section 7.9).
- LPDDR5X: byte-lane length match +/-0.25 mm; WCK and CK pairs +/-0.05 mm; VDDQ_LPX_0V5 shared with the DRAM VDDQ plane.
- XTAL: 25 MHz, +/-20 ppm, 12 pF load; guard ring to VSS.
- PORST_N from the board supervisor, released >= 10 ms after the last rail is in tolerance (KST-ARCH-001 section 8.4).
- TEST_MODE tied to VSS through 0 ohm; ATB0 no connect; VPP_OTP 10 kOhm to VSS.
- Boot: production cards boot standalone from the QSPI0 flash (BOOT_SEL = 00): the card must answer SMBus telemetry and complete secure-boot attestation before any host driver loads. PCIe host-load (BOOT_SEL = 01 and the mode-00 fallback, KST-ARCH-001 sections 13.2 and 13.3, requirement BOOT-01) is for lab bring-up and RMA only and is disabled by OTP in the PRODUCTION lifecycle.
- SMBus (I2C0) and PCIe sideband (PCIE0_PERST_N, PCIE0_CLKREQ_N, PCIE0_WAKE_N) level-shifted between 3.3 V at the edge connector and VDDIO_D.
- Decoupling for VDD_NPU, VDD_CORE and VDD_SRAM per the PI model in KST-PI-040.

## 9. Checks performed

| Check | Result | Date | By |
|---|---|---|---|
| Ball map vs. KST-ARCH-001 interface signal list (CHK-SPEC-02) | PASS: 761/761 signal balls assigned; 0 unassigned interface signals; 6 reserved test pads TP_0..TP_5 (section 7.12) excluded | 2026-09-21 | Rachel Lindqvist |
| Ball map vs. top-level ports of kst_top_nl_2026.09.19 | PASS: 761 ports matched | 2026-09-20 | Rachel Lindqvist |
| I/O cell max VDDIO >= bank VDDIO (section 3.1 vs section 4) | PASS (4/4 banks) | 2026-09-21 | Rachel Lindqvist |
| Pad-ring LVS / ERC, GPIO segment incl. ring breakers | PASS, 0 errors | 2026-09-20 | Daniel Achterberg |
| ESD network check (HBM 1 kV, CDM 250 V), per GPIO bank and all PHY hard-macro pads | PASS (pad ring PR-15 unchanged since B; per-bank ESD network re-verified; chip-level ESD/latch-up on the final GDS is recorded in KST-TRK-061 section 6) | 2026-09-21 | Rachel Lindqvist |
| Bump-to-ball netlist (package / die co-design) | PASS, 0 opens, 0 shorts | 2026-08-29 | Rachel Lindqvist |
| Substrate DRC (SUB-R07) | PASS | 2026-08-06 | Rachel Lindqvist |
| Power-ball current capacity (0.35 A per ball at 105 C) | PASS, worst VDD_NPU 0.21 A per ball | 2026-08-10 | Grace Adeyemi |
| SSO / ground bounce per GPIO bank | PASS, worst bank 76 mV (budget 120 mV) | 2026-08-31 | Rachel Lindqvist |
| PCIE0 package channel, lanes 0..15 | PASS, worst insertion loss 2.9 dB at 16 GHz | 2026-08-07 | Leo Brandt |
| LPDDR5X package SI, byte-lane skew | PASS, worst 4.1 ps (budget 5 ps) | 2026-08-07 | Anjali Deshmukh |

Package-level checks dated 2026-08-06 .. 2026-08-31 are carried from package B: ECO-C-001..003 are core-only changes (pad ring PR-15 and substrate SUB-R07 unchanged).

## 10. Review and approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Package & I/O Lead (author) | Rachel Lindqvist | Approved | 2026-09-21 |
| Chief Architect | Priya Raghavan | Approved | 2026-09-21 |
| Physical Design Lead | Daniel Achterberg | Approved | 2026-09-21 |
| Power Integrity Lead | Grace Adeyemi | Reviewed (power-ball allocation) | 2026-08-10 |
| PCIe Subsystem Owner | Leo Brandt | Reviewed (PCIE0/PCIE1 ball-out) | 2026-08-09 |
| Memory Subsystem Owner (LPDDR5X) | Anjali Deshmukh | Reviewed (LPDDR5X ball-out) | 2026-08-09 |
| DFT Lead | Samir Haddad | Reviewed (test-mode pin use) | 2026-08-09 |
