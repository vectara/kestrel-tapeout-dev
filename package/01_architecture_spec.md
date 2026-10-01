# ALX-5100 (KESTREL) Architecture Specification

| Field | Value |
|---|---|
| Doc ID | KST-ARCH-001 |
| Title | ALX-5100 (KESTREL) Architecture Specification |
| Revision | B (supersedes A) |
| Date | 2026-08-31 |
| Owner | Priya Raghavan (Chief Architect) |
| Status | Released for TRR-2 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

Applicable tape-out package: **B** (TRR-2, 2026-09-04). Reference netlist: `kst_top_nl_2026.08.31` (RTL freeze tag `kst_rtl_2026.07.15`; ECOs per KST-ECO-062).

## Revision history

| Rev | Date | Author | Description |
|---|---|---|---|
| A | 2026-08-10 | Priya Raghavan | Initial controlled release for TRR-1. Supersedes working draft 0.9 (2026-07-24). |
| B | 2026-08-31 | Priya Raghavan | Added PMU wake synchronization note (ECO-B-005); editorial. |

## 1. Scope and references

### 1.1 Scope

Chip-level architecture of the Aldercrest ALX-5100 "KESTREL" SoC: SKUs, partitioning, memory map, clocks, power rails and states, PMU wake protocol, operating conditions, I/O bank interface voltages, interrupts, reset/boot and DFT. KST-PKG-002, KST-IPBOM-050, KST-VPLAN-010 and the sign-off reports are checked against this document.

### 1.2 Related documents

| Doc ID | Title / relationship |
|---|---|
| KST-PKG-002 | Package, Pinout & I/O Specification: implements section 11 (ball map, pad ring, I/O cells, straps) |
| KST-IPBOM-050 | IP Bill of Materials: authoritative IP versions (this document names IP by function only) |
| KST-VPLAN-010 | Verification Plan: covergroups traced to the "shall" statements in this document |
| KST-STA-020 / KST-STA-021 | STA Sign-off Report / Timing Waiver Log: clocks per section 7, corners per section 10.2 |
| KST-CDC-030 | CDC / RDC Sign-off Report: clock domains and groups per section 7.3 |
| KST-PI-040 | Power Integrity Sign-off Report: core rails per section 8.1 |
| KST-DFT-EXC | DFT Exception List (section 14) |
| ALD-QA-CHK-007 rev 7.2 | Tape-out Readiness Checklist |
| ALX4100-ERR rev 3.1 | ALX-4100 (MERLIN) Silicon Errata: carry-forward items considered here |
| PCIe Base 5.0, PCIe CEM 5.0, JESD209-5B | Industry standards for PCIE0/PCIE1, the add-in card and LPDDR5X |

### 1.3 Conventions

- Frequencies in MHz, periods in ns (three decimals), voltages as "0.750 V" / "1.8 V", temperatures as junction temperature (Tj) in C.
- Instance paths are relative to `kst_top`. "Shall" marks a requirement traced in KST-VPLAN-010. Active-low signals end in `_N`.

## 2. Product overview

### 2.1 Summary

KESTREL is Aldercrest's second-generation inference accelerator for PCIe add-in cards (75 W chip TDP; 150 W-class CEM x16 card with one 2x3 (6-pin, 75 W) auxiliary power connector) and edge servers. It succeeds ALX-4100 "MERLIN" (foundry N7-class) and moves to a foundry N5-class process with a wider NPU, an LPDDR5X memory system and a Gen5 host link.

| Parameter | Value |
|---|---|
| Process | Foundry N5-class FinFET, 1P15M metal stack (2 thick top metals + AP/RDL), 300 mm wafers |
| Die size | 19.20 mm x 18.80 mm = 360.96 mm^2; ~34 billion transistors; ~155 gross die per 300 mm wafer |
| Package | FCBGA 45.0 mm x 45.0 mm, 2,304 balls (48 x 48), 0.8 mm pitch (see KST-PKG-002) |
| NPU compute | 16 tiles x 8,192 INT8 MACs x 2 ops x 1.2 GHz = 314.6 TOPS INT8 dense; 78.6 TFLOPS BF16 |
| On-chip SRAM | 64 MiB NPU-local (4 MiB x 16 tiles) + 32 MiB global buffer = 96 MiB |
| DRAM | LPDDR5X-8533, 256-bit (4 x 64-bit subsystems): 8533 MT/s x 32 B = 273.1 GB/s; up to 64 GB |
| Host interface | PCIe Gen5 x16 endpoint: 32 GT/s per lane, 512 Gb/s raw per direction, ~63 GB/s after 128b/130b encoding |
| Control CPU | Quad-core RV64GC control cluster, 1.5 GHz, 1 MiB shared L2 |
| Security | Security enclave: secure boot, AES-256-GCM, SHA-384, ECDSA P-384, TRNG, 4 Kbit OTP, root-key ladder |
| Operating Tj | 0 C to +105 C (ALX-5100); -40 C to +105 C (ALX-5100I); sign-off corners cover -40 C to +125 C |
| ECO provisions | 1.5% spare / gate-array ECO filler cell density for metal-only ECOs |

### 2.2 SKUs

| SKU | Market | Operating range | Configuration |
|---|---|---|---|
| ALX-5100 | commercial (data-center add-in card) | Tj 0 C to +105 C | PCIE0 x16 endpoint; PCIE1 fused off (FUSE_PCIE1_DIS=1) |
| ALX-5100I | industrial/edge | Tj -40 C to +105 C, cold boot at -40 C required | Same die, package and fuse map as ALX-5100; extended-temperature screening at -40 C and +105 C |
| ALX-5100X | future SKU, outside the qualification scope of this tape-out | Not defined in this revision | PCIE1 enabled (FUSE_PCIE1_DIS=0); separate product definition |

ALX-5100 and ALX-5100I are the same die. The industrial SKU shall complete a full cold boot (power-on, secure boot, LPDDR5X training, PCIe link-up) at any Tj from -40 C to +105 C.

PCIE1 is present in silicon but fused off in ALX-5100 via eFuse FUSE_PCIE1_DIS=1: power domain PD_PCIE1 is power-gated, pcie1_core_clk is clock-gated at the CRG, and all PCIE1 outputs are isolated/clamped to their inactive values. PCIE1 is reserved for the future ALX-5100X.

## 3. Top-level organization

```
            +------------------------------- kst_top --------------------------------+
LPDDR5X <-> | u_ddr_ss (u_mc0..3, u_phy0..3)      u_npu_c0..u_npu_c3 (4 x 4 tiles)   |
            |         |                                 |                            |
            |         +------ u_noc (4x4 mesh, 512-bit) --------+------ u_gbuf       |
            |         |              |              |                                |
PCIe x16 <> | u_pcie0_wrap       u_cpu          u_sec_encl         u_periph          |
PCIe x8  <> | u_pcie1_wrap [PD_PCIE1, fused off]   u_core/u_crg   u_core/u_pmu_if    |
XTAL     -> | u_aon: u_pmu, u_pmu/u_wake_ctl, u_fuse_shadow, RTC (aon_clk)           |
            +------------------------------------------------------------------------+
```

All initiators and targets attach to the NoC.

## 4. Block summary

| ID | Instance(s) | Function | Clock | Rail / domain |
|---|---|---|---|---|
| NPU | u_npu_c0..u_npu_c3 (tiles u_npu_cN/u_tile0..u_tile3), u_npu_top | 4 clusters x 4 tiles; 8,192 INT8 MACs and 4 MiB SRAM per tile | npu_clk | VDD_NPU (PD_NPU0..3), VDD_SRAM |
| GBUF | u_gbuf | 32 MiB global buffer SRAM, 32 banks | core_clk | VDD_CORE / VDD_SRAM |
| CPU | u_cpu (u_cpu/u_l2, u_cpu/u_plic) | Quad-core RV64GC control cluster (licensed core IP), 1 MiB L2 | cpu_clk | VDD_CORE |
| NOC | u_noc (routers u_noc/u_rtr_R_C) | 4x4 2D mesh, 512-bit links, QoS arbitration | core_clk | VDD_CORE |
| PCIE0 | u_pcie0_wrap (u_pcie0_wrap/u_ctl, u_pcie0_wrap/u_l1ss_ctl) | PCIe Gen5 x16 endpoint + PHY; ASPM L0s/L1; L1 PM substates L1.1/L1.2 | pcie_core_clk / pcie_aux_clk | VDD_CORE, VDDA_PCIE_0V75, VDDA_PCIE_1V2 |
| PCIE1 | u_pcie1_wrap | PCIe Gen5 x8 controller + PHY (root-port/CXL-capable); fused off in ALX-5100 | pcie1_core_clk (gated) | VDD_CORE switched (PD_PCIE1) |
| MEM | u_ddr_ss (u_ddr_ss/u_mc0..u_mc3, u_ddr_ss/u_phy0..u_phy3) | LPDDR5X-8533, 4 x 64-bit | mc_clk | VDD_CORE, VDDQ_LPX_0V5, VDDA_LPX_0V75 |
| SEC | u_sec_encl (u_otp_if, u_keyldr, u_keyldr/u_secded) | Security enclave, OTP, root-key ladder | sec_clk | VDD_CORE |
| AON | u_aon (u_pmu, u_pmu/u_wake_ctl, u_fuse_shadow) | PMU, wake sources, fuse shadow, RTC, 25 MHz XO | aon_clk | VDD_AON (PD_AON) |
| PMUIF | u_core/u_pmu_if | Core-side PMU interface (wake and sleep handshakes from AON) | core_clk | VDD_CORE |
| PERIPH | u_periph (u_qspi0, u_spi1, u_i2c0, u_i2c1, u_uart0, u_gpio) | QSPI boot flash, SPI, 2x I2C/SMBus, UART, GPIO | periph_clk | VDD_CORE |
| DBG | u_dbg, u_npu_top/u_trace_funnel | JTAG TAP, debug module, NPU trace funnel | npu_clk / tck | VDD_NPU / VDD_CORE |
| CRG | u_core/u_crg | 4 fractional PLLs, dividers, OCC test-clock controllers | multiple | VDD_CORE, VDDA_PLL_0V75 |

Block owners (approvers for CHK-STA-05 / CHK-CDC-06): NPU/DBG Viktor Halloran; PCIE0/PCIE1 Leo Brandt; MEM Anjali Deshmukh; SEC Ines Carvalho; AON/PMUIF Kofi Mensah; top-level partitions GBUF, CPU, NOC, PERIPH and CRG Daniel Achterberg (implementation owner; architecture owner Priya Raghavan); for CDC waivers on pad-facing logic in u_periph (u_padctl, GPIO input capture, strap capture) Rachel Lindqvist; for fuse-shadow and strap sources into u_crg, u_sysctl and u_pvt_ctl Kofi Mensah (KST-CDC-030 section 3.3).

## 5. Subsystems

### 5.1 NPU

- 4 clusters (u_npu_c0..u_npu_c3), each with 4 tiles, a cluster controller, a cluster DMA engine and one NoC port pair.
- Each tile: 8,192 INT8 MAC array (64 x 128), vector/activation unit, 4 MiB local SRAM (32 banks x 128 KiB), sparse-weight decompressor (2:4 structured sparsity and all-zero 64-byte block skipping).
- Peak dense throughput 314.6 TOPS INT8; BF16 at one quarter of the INT8 rate (78.6 TFLOPS).
- Debug: each cluster has a debug TAP (u_npu_cN/u_dbg_tap) that feeds a 64-bit trace bus to u_npu_top/u_trace_funnel. The trace bus is unpipelined and is timed as a functional multicycle-4 path in npu_clk (budget 4 x 0.833 = 3.333 ns).

### 5.2 Global buffer (GBUF)

- 32 MiB SRAM in 32 banks of 1 MiB (u_gbuf/u_bank00..u_bank31), SECDED ECC per 64-bit word.
- Four 512-bit NoC ports; peak 256 GB/s aggregate at core_clk 1000.0 MHz.
- Per-bank arbiters u_gbuf/u_bankNN/u_arb under the round-robin bank-conflict controller u_gbuf/u_bank_arb.

### 5.3 Control CPU

- Quad-core RV64GC control cluster (licensed core IP), 1.5 GHz, 32 KiB I + 32 KiB D L1 per core, 1 MiB shared L2 (u_cpu/u_l2) with SECDED ECC, Sv39 MMU.
- Interrupt controller u_cpu/u_plic (32 sources, source 0 reserved, 4-bit priority) plus CLINT timers. The PLIC gateways and pending registers are clocked by core_clk; the external-interrupt lines to the harts are synchronized into cpu_clk.
- Released from reset by the security enclave after first-stage boot authentication.

### 5.4 Network-on-chip (NoC)

- 4x4 2D mesh, 16 routers (u_noc/u_rtr_0_0..u_rtr_3_3), 512-bit links at core_clk 1000.0 MHz: 64 GB/s per link per direction; bisection 256 GB/s per direction.
- Credit-based flow control with virtual channels; four QoS classes (one per VC, VC0..VC3) arbitrated by weighted round-robin, each with a programmable 4-bit WRR weight (0-15; weight 0 is served only by the starvation guard).
- Attach points (16 local router ports): NPU clusters (4 port pairs), GBUF (4 targets), MEM (4 targets), PCIE0, PCIE1 (fused off), CPU, and SEC + PERIPH/APB bridge (one shared network interface).

### 5.5 PCIE0: host interface (Gen5 x16 endpoint)

- PCIe Gen5 x16 endpoint, 32 GT/s per lane, backward compatible with Gen1..Gen4; controller u_pcie0_wrap/u_ctl, PHY hard macro on the south die edge.
- 512-bit datapath at pcie_core_clk 1000.0 MHz; 8-channel DMA; MSI-X (2,048 vectors); BAR0 CSR (64 MiB), BAR2 GBUF (32 MiB), BAR4 DRAM (resizable to 64 GiB).
- Power management: ASPM L0s and L1; L1 PM substates L1.1 and L1.2 (ASPM and PCI-PM variants); LTR; CLKREQ#-based REFCLK removal. L1 PM substates are sequenced by the in-house sequencer u_pcie0_wrap/u_l1ss_ctl, redesigned for KESTREL after ALX4100-E03. u_l1ss_ctl runs on pcie_aux_clk (25.000 MHz from aon_clk) while REFCLK is off in L1.2.
- T_POWER_ON is programmable from 10 us to 130 us (default 40 us); LTR_L1.2_THRESHOLD is programmable.

L1.2 exit requirements:

| Req ID | Requirement |
|---|---|
| PCIE-ARCH-L12-01 | On CLKREQ# assertion in L1.2 (by the host or by the endpoint), u_l1ss_ctl shall not release the PHY from P1.2 until REFCLK is valid and T_POWER_ON has expired. |
| PCIE-ARCH-L12-02 | A CLKREQ# re-assertion that occurs while the T_POWER_ON timer is still running shall complete the L1.2 exit without releasing the PHY early and without a link-down (escape history: ALX4100-E03). |
| PCIE-ARCH-L12-03 | L1.2 exit shall meet the programmed T_POWER_ON at all supported link rates (Gen1..Gen5). |
| PCIE-ARCH-L12-04 | A host-initiated L1.2 exit while the chip is in LP-IDLE or SLEEP shall also raise a PMU wake event (section 9). |
| PCIE-ARCH-L12-05 | PCIE0_PERST_N assertion in any L1 substate shall return the link to Detect without hanging u_l1ss_ctl. |

### 5.6 PCIE1 (fused off in ALX-5100)

- PCIe Gen5 x8 controller + PHY (u_pcie1_wrap), root-port and CXL-capable, intended for the future ALX-5100X.
- In ALX-5100 and ALX-5100I the fuse FUSE_PCIE1_DIS=1 is read from the fuse shadow (u_aon/u_fuse_shadow) at POR. The PMU keeps PD_PCIE1 off, the CRG keeps pcie1_core_clk gated, isolation cells clamp all PD_PCIE1 outputs, the NoC target port for PCIE1 returns a decode error, and the PCIE1 PHY lanes are held powered down.
- The PCIE1 lanes are bonded out in the package but are not connected on ALX-5100 boards (KST-PKG-002).

### 5.7 MEM: LPDDR5X-8533 subsystem

- Four 64-bit subsystems (u_ddr_ss/u_mc0..u_mc3 + u_ddr_ss/u_phy0..u_phy3), each driving four x16 channels: 16 channels, 256 bits total, 273.1 GB/s peak.
- Third-party IP from vendor code MIPV: controller MC-LP5X and PHY PHY-LP5X-N5, versions per KST-IPBOM-050.
- Clocking: DFI clock mc_clk 1066.7 MHz (1:4 to WCK); WCK 4266.7 MHz; data rate 8533 MT/s.
- Up to 64 GB with dual-rank x16 channels; refresh management (RFM) enabled; link ECC optional per channel.
- Training at every cold boot: command-bus training, WCK2CK leveling, read RDQS gate training, read and write DQ eye training; periodic re-training driven by the DRAM oscillator counters.
- Training shall complete across the full operating Tj range of each SKU, including the ALX-5100I cold-boot condition.

### 5.8 SEC: security enclave

- u_sec_encl: RV32 secure core with 64 KiB boot ROM and 256 KiB secure SRAM; AES-256-GCM, SHA-384 and ECDSA P-384 engines; TRNG; 4 Kbit OTP behind u_sec_encl/u_otp_if.
- Root-key ladder u_sec_encl/u_keyldr: the 256-bit root key is loaded from OTP rows through the SECDED check/correct block u_sec_encl/u_keyldr/u_secded into root_key_q. An ECC-bypass (raw read) branch, selected per bit by ecc_bypass_mux, is used in PROVISION for raw read-back at ATE and, in every lifecycle state, by the boot ROM's raw-read integrity check on each cold boot: every key row is first captured raw into root_key_q and compared with the SECDED-corrected value before first key use; any mismatch that is not a flagged single-bit correction halts secure boot. During key load u_otp_if streams one word per sec_clk cycle from its OTP read buffer onto otp_rdata_q and root_key_q captures it on the next sec_clk edge (raw and SECDED-corrected passes); the otp_rdata_q -> root_key_q transfer is single-cycle and no multicycle exception is permitted on it in KST_func.sdc.
- Lifecycle states: TEST, PROVISION, PRODUCTION, RMA (OTP-encoded, monotonic).
- sec_clk is PLL_CORE/2 and is fixed at 500.0 MHz. It cannot be derated independently of core_clk (NoC, GBUF), and the mask-ROM OTP-read and TRNG-sampling timers are cycle-count constants calibrated for 500 MHz; no derating or DVFS of sec_clk is permitted. The 150 ms secure-boot budget (section 13.4) assumes 500 MHz.
- VPP_OTP (1.8 V) is supplied only at ATE for OTP programming.

### 5.9 AON / PMU

- u_aon on VDD_AON, clocked by aon_clk (25.000 MHz from the crystal oscillator); runs in every power state except OFF.
- Power-state FSM (ACTIVE, LP-IDLE, SLEEP, OFF) in u_aon/u_pmu; wake-event control in u_aon/u_pmu/u_wake_ctl (section 9).
- Fuse shadow u_aon/u_fuse_shadow: loads the eFuse array at POR and asserts fuse_load_done; provides FUSE_PCIE1_DIS, PLL trim, SRAM repair and lifecycle hints to the core.
- RTC (64-bit mtime counter at aon_clk, 40 ns resolution) with compare-match wake.
- Power-switch sequencing and isolation control for PD_NPU0..PD_NPU3 and PD_PCIE1; clock-stop control for PD_CORE.

### 5.10 Peripherals

- QSPI0 (u_periph/u_qspi0): boot-flash controller, quad SPI, 133 MHz SDR, 1-1-4 and 1-4-4 reads, 64 MiB XIP window.
- SPI1 (u_periph/u_spi1): SPI controller (up to 50 MHz) to the board telemetry sensor.
- I2C0 (u_periph/u_i2c0): SMBus target to the host via the edge connector, 100/400 kHz, PEC, 25 ms clock-stretch timeout. I2C1 (u_periph/u_i2c1): controller for local board devices.
- UART0 (u_periph/u_uart0): 16550-compatible console with fractional baud-rate divisor (DLF, 4-bit fraction), baud error <= 0.5% up to 3 Mbaud at periph_clk 200.0 MHz. GPIO (u_periph/u_gpio): 52 pins, per-pin interrupt, wake-enable on selected pins.

### 5.11 Debug and trace

- JTAG TAP (IEEE 1149.1) on GPIO_A; RISC-V debug module for the control cluster; secure-debug unlock by challenge-response, gated by OTP lifecycle state and the SEC_DBG_REQ strap.
- NPU trace funnel (u_npu_top/u_trace_funnel) merges the four cluster trace buses into a 256 KiB on-chip trace buffer readable over JTAG or PCIE0.

### 5.12 Clock and reset generation (CRG)

- Four fractional PLLs (PLL_CORE, PLL_NPU, PLL_CPU, PLL_DDR) referenced to the 25 MHz crystal, supplied from VDDA_PLL_0V75. The PCIe PHY PLLs are inside the PHY hard macros.
- Glitch-free dividers and clock muxes; clock gating per domain; OCC test-clock controllers per functional clock for at-speed test.
- Until PLL_CORE locks, core_clk (and its sec_clk / periph_clk dividers) runs from xtal_clk through the glitch-free PLL bypass mux in u_core/u_crg. pll_cfg_q captures fuse_cfg_q on the bypass clock after core_rst_n release and programs the PLL dividers and trims before lock is enabled. CDC analysis treats core_clk as asynchronous to aon_clk in all modes.
- Reset controller: cold (PORST_N), warm (PCIE0_PERST_N, watchdog, software) and per-domain resets; asynchronous assertion, synchronous de-assertion per domain.

## 6. Memory map summary

40-bit physical address space (control CPU and NoC initiators).

| Base | Size | Region |
|---|---|---|
| 0x00_0001_0000 | 64 KiB | Control-CPU boot ROM (reset vector); 0x00_0000_0000..0x00_0000_FFFF is a null guard |
| 0x00_0400_0000 | 256 KiB | SEC mailbox / shared SRAM window (secure-world filtered) |
| 0x00_0800_0000 | 64 MiB | QSPI0 XIP window (boot NOR flash) |
| 0x00_1000_0000 | 32 MiB | GBUF |
| 0x00_2000_0000 | 3 MiB | PERIPH APB; AON/PMU registers incl. PMU_WAKE_CAUSE and RTC (async APB bridge); CRG, PVT monitors, fuse shadow (read-only) |
| 0x00_2100_0000 | 16 MiB | MEM controller and PHY CSRs (4 x 4 MiB) |
| 0x00_2200_0000 | 16 MiB | PCIE0 controller, DBI, ATU, DMA |
| 0x00_2300_0000 | 16 MiB | PCIE1 CSRs (decode error when FUSE_PCIE1_DIS=1) |
| 0x00_2400_0000 | 16 MiB | NoC and QoS configuration |
| 0x00_2800_0000 | 64 MiB | PLIC, CLINT, debug module |
| 0x00_4000_0000 | 80 MiB | NPU local SRAM windows (16 x 4 MiB) and NPU CSRs |
| 0x10_0000_0000 | 64 GiB | LPDDR5X DRAM, interleaved across 4 subsystems |
| 0x40_0000_0000 | 256 GiB | PCIE0 outbound window (host memory) |
| 0x80_0000_0000 | 64 GiB | PCIE1 outbound window (reserved; decode error in ALX-5100) |

## 7. Clocking

### 7.1 Clock table

| Clock | Frequency | Period (ns) | Source | Domains / notes |
|---|---|---|---|---|
| xtal_clk | 25.000 MHz | 40.000 | Board 25 MHz crystal (XTAL_IN / XTAL_OUT) | Reference for all PLLs |
| aon_clk | 25.000 MHz | 40.000 | xtal_clk (always-on) | PMU/AON domain; runs in all power states except OFF |
| core_clk | 1000.0 MHz (ACTIVE); 15.625 MHz (LP-IDLE, core_clk/64); stopped (SLEEP) | 1.000 (ACTIVE) / 64.000 (LP-IDLE) | PLL_CORE | NoC, GBUF, PMU interface u_core/u_pmu_if, PLIC gateways (u_cpu/u_plic) |
| npu_clk | 1200.0 MHz | 0.833 | PLL_NPU | NPU clusters, trace funnel |
| cpu_clk | 1500.0 MHz | 0.667 | PLL_CPU | Control CPU cluster |
| sec_clk | 500.0 MHz | 2.000 | PLL_CORE/2 | Fixed 500.0 MHz; no derating or DVFS (section 5.8) |
| mc_clk | 1066.7 MHz | 0.938 | PLL_DDR | DFI clock; WCK = 4266.7 MHz; 8533 MT/s |
| pcie_core_clk | 1000.0 MHz | 1.000 | PCIe PHY PLL (from 100 MHz host REFCLK) | 512-bit datapath at Gen5 |
| pcie_aux_clk | 25.000 MHz | 40.000 | aon_clk | L1 PM substates logic while REFCLK is off (L1.2) |
| pcie1_core_clk | 500.0 MHz (x8 Gen5) | 2.000 | PCIE1 PHY PLL | Gated in ALX-5100 (FUSE_PCIE1_DIS=1) |
| periph_clk | 200.0 MHz | 5.000 | PLL_CORE/5 | QSPI0, SPI1, I2C0/I2C1, UART0, GPIO |
| tck | 50.0 MHz | 20.000 | JTAG pad (test only) | TAP, IJTAG network |
| scan_clk | 200.0 MHz (shift) | 5.000 | OCC test-clock mux (test mode only) | Scan shift; at-speed capture uses functional PLL clocks via OCC |

### 7.2 PLLs

PLL_CORE (1000.0 MHz: core_clk, sec_clk /2, periph_clk /5), PLL_NPU (1200.0 MHz), PLL_CPU (1500.0 MHz) and PLL_DDR (1066.7 MHz) are fractional PLLs referenced to the 25 MHz xtal_clk. Down-spread (0.5%) is optional on PLL_CORE and PLL_NPU and disabled on PLL_CPU and PLL_DDR. PLL_CORE stays locked in LP-IDLE; only the core_clk branch divider in u_core/u_crg changes (glitch-free; entry /1 to /64, exit stepped /64, /16, /4, /1 to limit di/dt on VDD_CORE), so sec_clk and periph_clk are unaffected by LP-IDLE.

### 7.3 Clock groups

| Group | Clocks | Relationship |
|---|---|---|
| G_REF | xtal_clk, aon_clk, pcie_aux_clk | Synchronous to each other (always-on reference group) |
| G_CORE | core_clk, sec_clk, periph_clk | Derived from PLL_CORE; synchronous to each other |
| G_NPU | npu_clk | Asynchronous to all other groups |
| G_CPU | cpu_clk | Asynchronous to all other groups |
| G_DDR | mc_clk | Asynchronous to all other groups |
| G_PCIE | pcie_core_clk | Asynchronous to all other groups |
| G_PCIE1 | pcie1_core_clk | Asynchronous; gated in ALX-5100 |
| G_TCK | tck | Test/debug only; scan_clk exists only in test mode (OCC) |

G_REF and G_CORE are asynchronous to each other.

## 8. Power architecture

### 8.1 Power rails

| Rail | Nominal | Regulation range (DC + ripple) | Sign-off range | Powers | Power domains | Seq. |
|---|---|---|---|---|---|---|
| VDD_AON | 0.750 V | 0.735 - 0.765 V (+/-2%, at ball) | 0.675 - 0.825 V | Always-on / PMU, RTC, fuse shadow, XO | PD_AON | 1 |
| VDDA_PLL_0V75 | 0.75 V | 0.7125 - 0.7875 V | - | PLLs (filtered) | - | 1 |
| VDDIO_A | 1.8 V | 1.71 - 1.89 V | - | GPIO bank A, XTAL, PORST_N, TEST_MODE | - | 2 |
| VDDIO_B | 1.8 V | 1.71 - 1.89 V | - | GPIO bank B (QSPI0 boot flash, SPI1 sensor) | - | 2 |
| VDDIO_C | 1.2 V | 1.14 - 1.26 V | - | GPIO bank C (card-management CPLD) | - | 2 |
| VDDIO_D | 1.8 V | 1.71 - 1.89 V | - | GPIO bank D (SMBus, PCIe sideband) | - | 2 |
| VDD_CORE | 0.750 V | 0.735 - 0.765 V (+/-2%, die-side sense) | 0.675 - 0.825 V (-10% incl. IR budget; +10% ATE Vmax) | NoC, CPU, SEC, PCIe/MC controllers, PERIPH, PMUIF, GBUF logic | PD_CORE, PD_PCIE1 (switched) | 3 |
| VDD_SRAM | 0.800 V | 0.784 - 0.816 V (+/-2%, die-side sense) | 0.720 - 0.880 V | SRAM bit-cell arrays (tracks VDD_CORE +50 mV) | follows parent domain | 3 |
| VDD_NPU | 0.750 V | 0.735 - 0.765 V (+/-2%, die-side sense) | 0.675 - 0.825 V | NPU clusters (separate PMIC rail) | PD_NPU0..PD_NPU3 | 4 |
| VDDA_PCIE_0V75 / VDDA_PCIE_1V2 | 0.75 V / 1.2 V | +/-3% | - | PCIe PHY analog (PCIE0 and PCIE1 PHYs) | - | 5 |
| VDDQ_LPX_0V5 / VDDA_LPX_0V75 | 0.50 V / 0.75 V | +/-3% | - | LPDDR5X PHY I/O and analog | - | 5 |
| VPP_OTP | 1.8 V | 1.71 - 1.89 V | - | OTP programming (ATE only) | - | ATE only |

### 8.2 Power domains

| Domain | Rail | Switchable | Contents | Retention |
|---|---|---|---|---|
| PD_AON | VDD_AON | No | u_aon (PMU, wake control, fuse shadow, RTC, XO) | n/a (always on) |
| PD_CORE | VDD_CORE | No (clock-stopped in SLEEP) | NoC, GBUF logic, CPU, SEC, MEM controllers, PCIE0, PERIPH, CRG, u_core/u_pmu_if | Full (state retained in SLEEP) |
| PD_NPU0..PD_NPU3 | VDD_NPU | Yes, per cluster (header switches, daisy-chained enables) | u_npu_c0..u_npu_c3 | None (reloaded by firmware) |
| PD_PCIE1 | VDD_CORE (switched) | Yes; permanently off when FUSE_PCIE1_DIS=1 | u_pcie1_wrap except u_pcie1_wrap/u_pd_ctl and the output isolation cells (unswitched VDD_CORE) | None |

Isolation cells on every switched-domain output clamp to the inactive value; isolation enables are driven from PD_AON.

### 8.3 Power states

| State | Definition | core_clk | NPU | PCIe0 link | LPDDR5X | Entry | Exit |
|---|---|---|---|---|---|---|---|
| ACTIVE | All clocks at full rate | 1000.0 MHz | on | L0 / L0s / L1 | active | - | - |
| LP-IDLE | core_clk divided by 64, NPU clock-gated, PCIe may be in L1.2 | 15.625 MHz | clock-gated, powered | L1 or L1.2 | self-refresh | Firmware request via core_lp_req, all cores in WFI | Wake event (section 9) |
| SLEEP | Core power domain retained, core_clk stopped; AON running | stopped | power-gated | L1.2 | self-refresh | Firmware request via core_lp_req | Wake event; PMU restarts clocks first |
| OFF | All off except board | off | off | L3 | off | Board removes supplies | PORST_N (cold boot) |

PWR-IDLE-01 (OEM platform requirement): card idle power at the edge connector in LP-IDLE with PCIE0 in L1.2 <= 9.0 W (estimate 8.4 W). ASPM L1.2 stays enabled in production: L1.1 keeps the lane common-mode voltages and PHY bias powered on all 16 lanes (+0.8 W, 9.2 W) and plain L1 with REFCLK and PHY PLLs running adds +1.9 W; either fails PWR-IDLE-01.

Exit latency targets: LP-IDLE to ACTIVE <= 2 us; SLEEP to ACTIVE <= 150 us (PLL_CORE relock <= 40 us plus domain restore); OFF to firmware-ready <= 150 ms (section 13.4).

### 8.4 Power-up and power-down sequencing

1. VDD_AON and VDDA_PLL_0V75 ramp first (sequence step 1); PORST_N held low by the board.
2. VDDIO_A..VDDIO_D ramp (step 2). Bank power-on-control cells hold all GPIO outputs tri-stated until VDD_CORE is valid.
3. VDD_CORE and VDD_SRAM ramp together (step 3); VDD_SRAM shall not lag VDD_CORE by more than 50 mV during the ramp.
4. VDD_NPU ramps (step 4); PD_NPU0..3 remain off until enabled by firmware.
5. PHY analog rails ramp (step 5). PORST_N is released by the board >= 10 ms after the last rail is within tolerance.
6. Power-down is the reverse order. VDD_AON may stay up in board standby.

### 8.5 Power budget (architecture estimate, Tj = 105 C, TDP workload)

| Rail / block | Estimate |
|---|---|
| VDD_NPU (NPU clusters) | 46.5 W |
| VDD_CORE (NoC, GBUF, CPU, SEC, controllers) | 16.5 W |
| VDD_SRAM | 4.8 W |
| LPDDR5X PHY (VDDQ_LPX_0V5, VDDA_LPX_0V75) | 3.4 W |
| PCIe PHY (VDDA_PCIE_0V75, VDDA_PCIE_1V2) | 2.6 W |
| AON, PLLs, GPIO | 0.5 W |
| **Total** | **74.3 W (TDP 75 W)** |

## 9. PMU wake protocol

### 9.1 Overview

The always-on domain owns all wake events. pmu_wake_req is a single-cycle pulse (1 aon_clk cycle = 40 ns) generated by u_aon/u_pmu/u_wake_ctl on each wake event (PCIe L1.2 exit request / CLKREQ#, GPIO interrupt, RTC timer, SMBus alert) and consumed by u_core/u_pmu_if in the core_clk domain.

pmu_wake_req crosses into core_clk through the pulse synchronizer u_core/u_pmu_if/u_wake_psync (toggle + 3-FF + edge detect), see ECO-B-005.

On receipt, u_core/u_pmu_if sets wake_pending_q, steps the core_clk divider from /64 back to /1, re-enables the NPU clock gates selected in PMU_WAKE_CFG and raises PLIC source 24 (PMU wake). The wake cause is recorded in the always-on register PMU_WAKE_CAUSE (sticky, write-1-to-clear) so that firmware can identify every event, including events that arrive while a previous wake is being processed.

### 9.2 Wake sources

| Source | Event | Detected by | Active in |
|---|---|---|---|
| PCIe L1.2 exit request | Host asserts PCIE0_CLKREQ_N (CLKREQ#) while the link is in L1.2 | u_pcie0_wrap/u_l1ss_ctl (pcie_aux_clk), forwarded to u_aon/u_pmu/u_wake_ctl | LP-IDLE, SLEEP |
| GPIO interrupt | Programmed edge or level on a wake-enabled GPIO (SENSOR_ALERT_N, CMC_IRQ_N, spare pins) | GPIO wake detector in u_aon (aon_clk) | LP-IDLE, SLEEP |
| RTC timer | RTC compare match | u_aon RTC | LP-IDLE, SLEEP |
| SMBus alert | SMB_ALERT_N asserted by a board SMBus device | GPIO_D wake detector in u_aon | LP-IDLE, SLEEP |
| PCIE0_PERST_N | Fundamental reset from host | u_aon reset controller | All states (treated as warm reset, not a wake) |

### 9.3 AON / core interface signals

| Signal | Source | Destination | Source clock | Destination clock | Shape | Function |
|---|---|---|---|---|---|---|
| pmu_wake_req | u_aon/u_pmu/u_wake_ctl | u_core/u_pmu_if | aon_clk | core_clk | Single-cycle pulse, 1 aon_clk cycle (40 ns), one per wake event | Wake request to the core |
| pmu_sleep_req | u_aon/u_pmu | u_core/u_pmu_if | aon_clk | core_clk | Level; 4-phase request/acknowledge with core_sleep_ack | Request to quiesce for LP-IDLE / SLEEP |
| core_sleep_ack | u_core/u_pmu_if | u_aon/u_pmu | core_clk | aon_clk | Level | NoC drained, LPDDR5X in self-refresh, cores in WFI |
| core_lp_req[1:0] | u_core/u_pmu_if | u_aon/u_pmu | core_clk | aon_clk | Level, held until pmu_sleep_req | Firmware target state (01 LP-IDLE, 10 SLEEP) |
| pmu_iso_en[4:0] | u_aon/u_pmu | Isolation cells (PD_NPU0..3, PD_PCIE1) | aon_clk | - | Level | Isolation enables |
| pmu_npu_pwr_en[3:0] / npu_pwr_ack[3:0] | u_aon/u_pmu | PD_NPU0..3 switch chains | aon_clk | aon_clk | Level | Power-switch enable and daisy-chain acknowledge |
| fuse_cfg_q[31:0] | u_aon/u_fuse_shadow | u_core/u_crg (pll_cfg_q) | aon_clk | core_clk (quasi-static, KST-CDC-030 W-CDC-009) | Level; written once by the fuse-shadow load during POR while the core domain is held in reset | PLL and CRG configuration from fuses |
| fuse_pcie1_dis | u_aon/u_fuse_shadow | PMU, CRG, NoC decode, u_pcie1_wrap/u_iso | aon_clk | pcie1_core_clk (CDC-0139 / W-CDC-012); core_clk via fuse_cfg_q[31] (CDC-0112 / W-CDC-009); PMU same domain | Level, static after POR | FUSE_PCIE1_DIS |

### 9.4 Wake sequences

| From | Sequence |
|---|---|
| LP-IDLE | Wake event -> u_wake_ctl issues pmu_wake_req -> u_core/u_pmu_if sets wake_pending_q -> core_clk divider stepped /64 -> /16 -> /4 -> /1 (each step held for 8 cycles of the new clock, about 0.2 us in total) -> NPU clock gates re-enabled -> PLIC source 24 -> firmware reads PMU_WAKE_CAUSE. Target <= 2 us. |
| SLEEP | Wake event -> PMU FSM restarts PLL_CORE (lock <= 40 us) -> PD_NPU clusters re-powered per PMU_WAKE_CFG, isolation released -> core_clk running at /64 -> u_wake_ctl issues pmu_wake_req -> as LP-IDLE. Target <= 150 us. |
| ACTIVE | Wake-enabled events still produce pmu_wake_req; u_core/u_pmu_if forwards them as PLIC source 24 only (no state change). |
| L1.2 exit in LP-IDLE | Host CLKREQ# -> u_l1ss_ctl starts the L1.2 exit (REFCLK restore, T_POWER_ON) and in parallel signals u_wake_ctl -> pmu_wake_req -> core_clk returns to 1000.0 MHz before the link reaches L0. |

## 10. Operating conditions

### 10.1 Recommended operating conditions

| Parameter | ALX-5100 | ALX-5100I | Notes |
|---|---|---|---|
| Junction temperature Tj | 0 C to +105 C | -40 C to +105 C | Cold boot at -40 C required for ALX-5100I |
| VDD_CORE, VDD_NPU | 0.750 V +/-2% (DC + ripple at the PMIC sense point) | same | Sign-off -10% = 2% regulation + 8% dynamic-IR budget (CHK-PI-02); +10% = ATE Vmax screen and overshoot (KST-PI-040 section 10) |
| VDD_AON | 0.750 V +/-2% (DC + ripple at the PMIC sense point) | same | Same sign-off corners; -10% = 2% regulation + 5% dynamic-IR budget (CHK-PI-02) + 3% margin (KST-PI-040 section 10) |
| VDD_SRAM | 0.800 V +/-2% | same | |
| VDDIO_A, VDDIO_B, VDDIO_D | 1.8 V +/-5% | same | |
| VDDIO_C | 1.2 V +/-5% | same | |
| Thermal shutdown | THERMTRIP_N asserted at Tj = 120 C | same | Hardware, independent of firmware |
| Throttle | PROCHOT_N / firmware throttle at Tj = 105 C | same | |
| ESD | HBM 1 kV, CDM 250 V | same | CHK-PV-02 |
| Lifetime | 10 years, EM checked at Tj = 110 C | same | CHK-PI-03 |

### 10.2 Sign-off PVT corners

| Corner | Process | Voltage | Tj | Purpose |
|---|---|---|---|---|
| ss_0p675v_125c | SS | 0.675 V | +125 C | Setup (hot) |
| ss_0p675v_m40c | SS | 0.675 V | -40 C | Setup (cold; worst at low voltage due to temperature inversion) |
| tt_0p750v_25c | TT | 0.750 V | +25 C | Typical, leakage/IDDQ at room temperature and ATE correlation |
| tt_0p750v_85c | TT | 0.750 V | +85 C | Typical-silicon timing reference; PI current libraries (KST-PI-040) |
| ff_0p825v_m40c | FF | 0.825 V | -40 C | Hold (cold) |
| ff_0p825v_125c | FF | 0.825 V | +125 C | Hold (hot), leakage |

Corners cover Tj -40 C to +125 C, which includes the operating range of both SKUs (CHK-SPEC-04). At 0.675 V the -40 C corner is setup-critical because of FinFET temperature inversion, so both the -40 C and the +125 C slow corners are signed off. RC corners: cworst_ccworst, rcworst, typical, cbest_ccbest, rcbest. The 14 MCMM views (func, scan_shift, scan_capture, mbist) are defined in KST-STA-020.

## 11. I/O banks and board interfaces

### 11.1 GPIO banks

| Bank | Pins | Interface voltage | Supply | Functions |
|---|---|---|---|---|
| GPIO_A | 12 | 1.8 V | VDDIO_A | JTAG (TCK, TMS, TDI, TDO, TRST_N), UART0 TX/RX, boot/debug straps, 2 spare; scan channels in TEST_MODE |
| GPIO_B | 16 | 1.8 V | VDDIO_B | QSPI0 boot NOR flash (1.8 V serial NOR, 133 MHz SDR: CLK, CS0_N, DQ[3:0], RST_N), SPI1 telemetry sensor (1.8 V) + SENSOR_ALERT_N, 4 spare |
| GPIO_C | 16 | 1.2 V | VDDIO_C | Card-management CPLD interface (1.2 V LVCMOS), status LEDs (via board buffer), PWR_GOOD inputs, THERMTRIP_N, PROCHOT_N |
| GPIO_D | 8 | 1.8 V | VDDIO_D | I2C0/I2C1 (SMBus to host via edge connector, board level-shifted), PCIE0_PERST_N, PCIE0_CLKREQ_N, PCIE0_WAKE_N (board level-shifted from 3.3 V), SMB_ALERT_N |

52 GPIO pins in total. The interface voltage of each bank is set by the device it connects to on the reference card; I/O cell selection and ball assignment are defined in KST-PKG-002.

### 11.2 Pin allocation

| Pins | Function (mission mode) |
|---|---|
| GPIO_A0..A6 | JTAG_TCK, JTAG_TMS, JTAG_TDI, JTAG_TDO, JTAG_TRST_N, UART0_TXD, UART0_RXD |
| GPIO_A7..A11 | BOOT_SEL0, BOOT_SEL1 (straps, section 13.3), SEC_DBG_REQ (strap), 2 spare (scan channel in TEST_MODE; GPIO_A11 optional low-speed external shift clock, <= 50 MHz, for bring-up) |
| GPIO_B0..B6 | QSPI0_CLK, QSPI0_CS0_N, QSPI0_DQ0..QSPI0_DQ3, QSPI0_RST_N (boot flash) |
| GPIO_B7..B11 | SPI1_SCLK, SPI1_CS0_N, SPI1_MOSI, SPI1_MISO, SENSOR_ALERT_N (telemetry sensor; alert is wake-capable) |
| GPIO_B12..B15 | Spare GPIO |
| GPIO_C0..C5 | CMC_SCLK, CMC_CS_N, CMC_MOSI, CMC_MISO, CMC_IRQ_N (wake-capable), CMC_RST_REQ_N |
| GPIO_C6..C15 | LED0..LED3, PG_VDD_CORE, PG_VDD_NPU, PG_VDDQ_LPX, PG_BOARD, THERMTRIP_N (open-drain), PROCHOT_N (open-drain) |
| GPIO_D0..D3 | I2C0_SCL, I2C0_SDA (SMBus to host), I2C1_SCL, I2C1_SDA (local devices), open-drain |
| GPIO_D4..D7 | PCIE0_PERST_N, PCIE0_CLKREQ_N (open-drain), PCIE0_WAKE_N (open-drain), SMB_ALERT_N (wake-capable) |

### 11.3 Dedicated (non-GPIO) pins

| Pin | Function | Notes |
|---|---|---|
| XTAL_IN / XTAL_OUT | 25 MHz crystal | Supplied from VDDIO_A |
| PORST_N | Power-on reset input | Schmitt trigger, VDDIO_A |
| TEST_MODE | Test-mode select | Internal pull-down; tied low on production boards |
| THERM_DP / THERM_DN | Remote thermal diode | Read by the board CPLD / BMC |
| ATB0 | Analog test bus | Test only; no connect on production boards |
| PCIE0_REFCLK_P/N, PCIE0_RESREF | PCIe 100 MHz reference clock, PHY calibration resistor | |
| PCIE1_REFCLK_P/N, PCIE1_RESREF | PCIE1 reference and calibration | Not connected on ALX-5100 boards |

### 11.4 Interface notes

- Boot flash: 1.8 V serial NOR, 512 Mbit, quad I/O read, 133 MHz SDR, 8 dummy cycles; no 1.2 V 512 Mbit NOR on the Aldercrest AVL is qualified to Tj -40 C. QSPI0 samples read data with a programmable delay line (64 taps x 78 ps = 5.0 ns, sub-cycle only).
- Telemetry sensor on SPI1: 1.8 V, 20 MHz, alert on SENSOR_ALERT_N.
- The card-management CPLD is a 1.2 V LVCMOS device.
- SMBus and PCIe sideband signals are level-shifted between 3.3 V (edge connector) and 1.8 V (GPIO_D) on the reference card.

## 12. Interrupts

PLIC u_cpu/u_plic, 32 sources (source 0 reserved), 4-bit priority, all sources disabled at reset.

| Src | Name | Src | Name |
|---|---|---|---|
| 1 | UART0 | 17 | PCIE0 link / power-management events |
| 2 | I2C0 (SMBus target) | 18 | PCIE1 (reserved, masked when fused off) |
| 3 | I2C1 | 19..22 | MEM0..MEM3 (ECC, training, RFM) |
| 4 | SPI1 | 23 | SEC mailbox |
| 5 | QSPI0 | 24 | PMU wake (u_core/u_pmu_if) |
| 6..9 | GPIO_A, GPIO_B, GPIO_C, GPIO_D | 25 | PVT monitor alarm (24 sensors) |
| 10..13 | NPU cluster 0..3 done | 26 | NoC error |
| 14 | NPU DMA completion (coalesced) | 27 | GBUF ECC |
| 15 | NPU error (ECC, sparse decoder, watchdog) | 28 | Watchdog |
| 16 | PCIE0 DMA | 29..31 | RTC compare, PLL loss of lock, host doorbell |

## 13. Reset and boot

### 13.1 Reset sources

| Reset | Source | Scope |
|---|---|---|
| Cold | PORST_N (board) | Entire chip incl. AON and fuse shadow |
| PCIe fundamental | PCIE0_PERST_N | PD_CORE and PD_NPU domains (warm); AON retained |
| Watchdog | u_core watchdog | PD_CORE and PD_NPU (warm) |
| Software | CRG reset register | Selected domains |
| Thermal | THERMTRIP at Tj = 120 C | Board removes power via THERMTRIP_N |

core_rst_n is released >= 1,024 aon_clk cycles (40.96 us) after fuse_load_done.

### 13.2 Boot sources

Production cards of both SKUs shall boot standalone from the QSPI0 boot flash (OEM requirement BOOT-01): the card must answer SMBus telemetry and complete secure-boot attestation before any host driver loads. PCIe host-load is for lab bring-up and RMA only. The security enclave always boots first from its ROM; the control CPU is released only after the first-stage boot loader (FSBL) is authenticated.

### 13.3 Boot-mode straps

| BOOT_SEL[1:0] | Mode |
|---|---|
| 00 | QSPI0 boot flash (default; pull-downs); PCIe fallback outside PRODUCTION only |
| 01 | PCIe boot only via BAR0 mailbox (disabled by OTP in PRODUCTION lifecycle) |
| 10 | UART recovery (disabled by OTP in PRODUCTION lifecycle) |
| 11 | Reserved |

In mode 00 the ROM tries the primary and the recovery FSBL images in the boot flash. If both fail authentication, a PRODUCTION part halts and reports the failure over SMBus; in the other lifecycle states the ROM enables the PCIE0 BAR0 mailbox for a host-pushed image (same signature checks).

### 13.4 Boot sequence and secure-boot budget

| Step | Action | Budget |
|---|---|---|
| 1 | PORST_N de-assertion; crystal start-up; fuse shadow load, fuse_load_done | 2.0 ms |
| 2 | core_rst_n release; PLL_CORE lock; sec_clk 500.0 MHz | 0.1 ms |
| 3 | Secure-core ROM: lifecycle check, root-key raw-read integrity check and SECDED-corrected load from OTP through u_keyldr | 1.0 ms |
| 4 | Read FSBL (512 KiB) from the QSPI0 boot flash, quad 133 MHz SDR (~66.5 MB/s) | 8.0 ms |
| 5 | SHA-384 hash and ECDSA P-384 signature verification | 6.0 ms |
| 6 | Release control CPU; FSBL starts | 0.5 ms |
| 7 | LPDDR5X initialization and training (4 subsystems in parallel) | 60.0 ms |
| 8 | Load and verify runtime firmware (2 MiB) into LPDDR5X | 40.0 ms |
| 9 | Set PCIE0 configuration-ready; host enumeration proceeds | - |
| **Total** | PORST_N to firmware-ready | **117.6 ms (budget 150 ms)** |

PCIE0 link training is started by hardware 10 ms after PCIE0_PERST_N de-assertion, independent of boot progress; configuration requests receive CRS completions until step 9. The 150 ms budget assumes sec_clk = 500.0 MHz.

## 14. DFT summary

| Item | Architecture |
|---|---|
| Test access | IEEE 1149.1 TAP on GPIO_A; IEEE 1687 (IJTAG) network for MBIST, PVT monitors and PLL test; dedicated TEST_MODE pin |
| Scan | Full scan with on-chip compression; scan channels on GPIO_A in TEST_MODE; scan_clk 200.0 MHz shift from the OCC test-clock mux (PLL_CORE/5); optional low-speed (<= 50 MHz) external shift clock on GPIO_A11 for bring-up |
| Scan enable | Distributed to each NPU cluster through a 3-stage pipeline (se_pipe flops) to meet 200 MHz shift timing |
| At-speed test | Launch-on-capture through OCC test-clock controllers on every functional PLL clock |
| STA modes | func, scan_shift, scan_capture, mbist (14 MCMM views, KST-STA-020); DFT timing exceptions in KST-DFT-EXC |
| Targets | ATPG stuck-at >= 99.0%, transition-delay >= 95.0% (CHK-DFT-01); MBIST on 100% of SRAM instances with repair on NPU-local and GBUF SRAMs (CHK-DFT-02) |
| PHY test | PCIe and LPDDR5X PHY internal loopback and PRBS via vendor test interfaces |

## 15. Review and approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Chief Architect (author) | Priya Raghavan | Approved | 2026-08-31 |
| Program Manager | Marcus Oyelaran | Approved | 2026-08-31 |
| PCIe Subsystem Owner | Leo Brandt | Reviewed, no comments open | 2026-08-07 |
| Memory Subsystem Owner (LPDDR5X) | Anjali Deshmukh | Reviewed, no comments open | 2026-08-07 |
| Security Enclave Owner | Ines Carvalho | Reviewed, no comments open | 2026-08-07 |
| PMU / Always-on Domain Owner | Kofi Mensah | Reviewed (section 9.1 change), no comments open | 2026-08-28 |
| NPU Cluster Owner | Viktor Halloran | Reviewed, no comments open | 2026-08-06 |
| Package & I/O Lead | Rachel Lindqvist | Reviewed, no comments open | 2026-08-07 |
| Quality & Tape-out Gatekeeper | Oren Feldman | Document-control check complete | 2026-08-31 |
