# IP Bill of Materials

| Field | Value |
|---|---|
| Doc ID | KST-IPBOM-050 |
| Title | IP Bill of Materials |
| Revision | A |
| Date | 2026-08-10 |
| Owner | Beatriz Solano (IP Manager) |
| Status | Released for TRR-1 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |


## 1. Scope

This document lists every IP block integrated in KESTREL (ALX-5100) for tape-out package A, with version, source, qualification status, the carry-forward errata cross-check (CHK-IP-03) and the integration hash check (CHK-IP-02). Versions are as integrated in netlist kst_top_nl_2026.08.07 and the matching implementation database.

Reference documents: KST-ARCH-001, KST-PKG-002, KST-VPLAN-010, ALD-QA-CHK-007 rev 7.2, ALX4100-ERR rev 3.1, vendor release notes for each third-party IP (for MC-LP5X / PHY-LP5X: MIPV-RN-LP5X-027).

## 2. IP list


| # | Function | IP | Version | Source | Qualification | Integrated hash check | Notes |
|---|---|---|---|---|---|---|---|
| 1 | Standard-cell library | STDCELL-N5-H210 (SVT/LVT/ULVT) | v1.2 | foundry N5-class | Foundry-qualified (PDK sign-off release) | MATCH sha256:09973d53 |  |
| 2 | SRAM compilers (1P/2P/RF) | SRAM-N5-COMP | v2.1 | foundry N5-class | Foundry-qualified; instances characterized at 6/6 sign-off PVT corners | MATCH sha256:0a1dab98 | 3,412 instances (1P/2P/RF) |
| 3 | GPIO library | GPIO-N5-LIB | v1.3 | foundry N5-class (I/O library) | Foundry-qualified (ESD HBM 1 kV / CDM 250 V certified) | MATCH sha256:b6d7ce6f | cells IO_GPIO_1V8 on GPIO_A, GPIO_D; IO_GPIO_1V2 on GPIO_B, GPIO_C |
| 4 | RISC-V control CPU cluster | CPU-RV64-Q4 | v3.0.2 | licensed core IP | Production release from licensor | MATCH sha256:4d3a16c5 | 4 cores, 1 MiB L2 |
| 5 | NoC generator | NOCGEN | v4.1 | licensed | Production release (generator); generated RTL verified per KST-VPLAN-010 | MATCH sha256:5e76f735 | 4x4 mesh, 512-bit links |
| 6 | PCIe Gen5 controller (PCIE0 x16, PCIE1 x8) | PCIE5-CTL | v5.2.1 | third-party | Production-qualified; Gen5 compliance-tested by vendor | MATCH sha256:1d60aa68 | PCIE0 x16 active; PCIE1 x8 fused off (FUSE_PCIE1_DIS=1) |
| 7 | PCIe Gen5 PHY | PCIE5-PHY-N5 | v1.4 | third-party hard macro | Production-qualified; silicon-proven on vendor N5-class test chip | MATCH sha256:76c02daa | 2 instances (PCIE0, PCIE1) |
| 8 | PCIe L1 PM substates sequencer | l1ss_ctl | v3.0 | in-house | In-house; verification per KST-VPLAN-010 | MATCH (repo release tag) | in-house (redesigned after ALX4100-E03) |
| 9 | LPDDR5X memory controller | MC-LP5X | v2.6.1 | third-party (vendor code MIPV) | Production (maintenance branch) | MATCH sha256:a22b4f08 | 2.6.x lineage silicon-proven on ALX-4100; matched with PHY-LP5X-N5 v2.6.1 |
| 10 | LPDDR5X PHY | PHY-LP5X-N5 | v2.6.1 | third-party hard macro (vendor code MIPV) | Production (maintenance branch) | MATCH sha256:3a454936 | 2.6.x lineage silicon-proven on ALX-4100 (PHY-LP5X-N7); 4 instances (u_ddr_ss/u_phy0..u_phy3) |
| 11 | Fractional PLL | PLL-N5-FRAC | v3.1 | third-party | Production-qualified; silicon-proven | MATCH sha256:02caf4a6 | 4 instances (PLL_CORE, PLL_NPU, PLL_CPU, PLL_DDR) |
| 12 | OTP / eFuse | OTP-N5-4K | v2.0 | third-party | Production-qualified | MATCH sha256:af53a0fa | 4 Kbit shared: SEC key and lifecycle rows access-controlled; trims, harvest and compressed SRAM repair signatures (~1.5 Kbit) in general rows; read margin qualified at 0.675 V |
| 13 | TRNG | TRNG-ENT | v1.3 | third-party | Production-qualified | MATCH sha256:234c9994 | Entropy source with on-line health tests |
| 14 | Crypto engines (AES/SHA/PKA) | SEC-CRYPTO | v2.2 | in-house | In-house; verification per KST-VPLAN-010 | MATCH (repo release tag) | AES-256-GCM, SHA-384, ECDSA P-384 PKA |
| 15 | PVT monitors (24 sensors) | PVT-MON-N5 | v1.1 | third-party | Production-qualified; silicon-proven | MATCH sha256:34d21921 | 24 sensors |
| 16 | I2C/SMBus controller | I2C-CTL | v1.5 | third-party | Production-qualified | MATCH sha256:b7da40a6 | I2C0, I2C1 (SMBus) |
| 17 | QSPI controller | QSPI-CTL | v2.3 | third-party | Production-qualified | MATCH sha256:0a3beebb | QSPI0 boot flash, 133 MHz SDR |
| 18 | UART | UART-16550C | v1.2 | third-party | Production-qualified | MATCH sha256:d736852e | UART0 |
| 19 | NPU DMA engine | NPU-DMA | v1.4 | in-house | In-house; verification per KST-VPLAN-010 | MATCH (repo release tag) | 16 channels per cluster |
| 20 | NPU tile | NPU-TILE | v3.0 | in-house | In-house; verification per KST-VPLAN-010 | MATCH (repo release tag) | 16 tiles (4 clusters x 4) |
| 21 | PMU / always-on | PMU-AON | v2.1 | in-house | In-house; verification per KST-VPLAN-010 | MATCH (repo release tag) | u_aon |
| 22 | Clock/reset generator | CRG | v3.0 | in-house | In-house; verification per KST-VPLAN-010 | MATCH (repo release tag) | Clock/reset generation for all domains |
| 23 | Interrupt controller (PLIC/CLINT) | RV-PLIC | v1.0 | in-house | In-house; verification per KST-VPLAN-010 | MATCH (repo release tag) | PLIC + CLINT |
| 24 | MBIST controller | MBIST-CTL | v4.0 | generic DFT IP | Production release | MATCH sha256:9d0b0529 | All SRAM instances, with repair |
| 25 | Scan compression / OCC | DFT-CMP-OCC | 2026.1 | generic DFT IP | Production release | MATCH sha256:ec28a5fd | Scan compression and on-chip clock control |

Source legend: foundry N5-class = foundry PDK library or compiler; third-party = licensed from an IP vendor (vendor code shown where the license requires it); licensed = licensed core or generator; in-house = Aldercrest RTL; generic DFT IP = inserted by the DFT flow.

## 3. Hard macros and libraries: integrated views

| IP | Instances | Views integrated | LIB corners |
|---|---|---|---|
| STDCELL-N5-H210 | Full chip | LIB, LEF, GDS, Verilog, CDL | 6/6 sign-off PVT corners |
| SRAM-N5-COMP | 3,412 | LIB, LEF, GDS, Verilog, MBIST description | 6/6 |
| GPIO-N5-LIB | 52 signal I/O cells (GPIO_A 12, GPIO_B 16, GPIO_C 16, GPIO_D 8) plus power and ESD cells | LIB, LEF, GDS, Verilog, IBIS | 6/6 |
| PCIE5-PHY-N5 | 2 | LIB, LEF, GDS, Verilog, IBIS-AMI | 6/6 |
| PHY-LP5X-N5 | 4 | LIB, LEF, GDS, Verilog, IBIS, training firmware image | 6/6 |
| PLL-N5-FRAC | 4 | LIB, LEF, GDS, Verilog | 6/6 |
| OTP-N5-4K | 1 | LIB, LEF, GDS, Verilog | 6/6 |
| TRNG-ENT | 1 | LIB, LEF, GDS, Verilog | 6/6 |
| PVT-MON-N5 | 24 | LIB, LEF, GDS, Verilog | 6/6 |

Sign-off PVT corners: ss_0p675v_125c, ss_0p675v_m40c, tt_0p750v_25c, tt_0p750v_85c, ff_0p825v_m40c, ff_0p825v_125c.

## 4. Qualification (CHK-IP-01)

All third-party IP is at a production release per the vendor release notes. No early-access or beta release is integrated; MC-LP5X v2.8.0-EA was reviewed and not adopted. Result: PASS.

## 5. Errata cross-check (CHK-IP-03)

Source: ALX4100-ERR rev 3.1 (2025-11-12). All 14 ALX-4100 errata are listed. Carry-forward errata are checked against the KESTREL IP version or the in-house design fix.


| Erratum | KESTREL resolution | Carry-forward | KESTREL IP / version | Reviewed with | Date | Release-note reference |
|---|---|---|---|---|---|---|
| ALX4100-E01 | resolved - NPU-DMA v1.4 (fixed in v1.3); covergroup cg_npu_dma_ring_wrap (Escape-history) | Yes | NPU-DMA v1.4 | V. Halloran | 2026-08-06 | - |
| ALX4100-E02 | No carry-forward (won't fix; SW workaround) | No | - | L. Brandt | 2026-08-06 | - |
| ALX4100-E03 | in-house l1ss_ctl v3.0 redesign; verify per CHK-VER-07 | Yes | l1ss_ctl v3.0 | L. Brandt | 2026-08-06 | - |
| ALX4100-E04 | resolved - MC-LP5X v2.6.1 (fixed in v2.6.0, LPX-1107) | Yes | MC-LP5X v2.6.1 | A. Deshmukh | 2026-08-06 | MIPV-RN-LP5X-027 |
| ALX4100-E05 | resolved - I2C-CTL v1.5 (fixed in v1.4, same release line); covergroup cg_i2c_clk_stretch (Escape-history) | Yes | I2C-CTL v1.5 | K. Mensah | 2026-08-06 | I2C-CTL RN rev 9: v1.5 fixed-issue list includes I2CC-0049 (25 ms clock-stretch timeout), carried from v1.4 |
| ALX4100-E06 | No carry-forward (documentation update) | No | - | B. Solano | 2026-08-06 | - |
| ALX4100-E07 | N/A - MC-LP5X 2.6.x lineage silicon-proven on ALX-4100 | Yes | MC-LP5X v2.6.1 / PHY-LP5X-N5 v2.6.1 | A. Deshmukh | 2026-08-06 | MIPV-RN-LP5X-027 |
| ALX4100-E08 | resolved - PVT-MON-N5 v1.1 (digital trim; N5 port of the PVT-MON v1.1 fix) | Yes | PVT-MON-N5 v1.1 | K. Mensah | 2026-08-06 | PVT-MON-N5 RN rev 4: v1.1 fixed-issue list includes PVTM-0133 (+3 C reading error above 110 C) |
| ALX4100-E09 | No carry-forward (ALX-4100 A1 test-flow OTP IDCODE override) | No | - | B. Solano | 2026-08-06 | - |
| ALX4100-E10 | resolved - PLL-N5-FRAC v3.1 (N5 port of the PLL-FRAC v3.0 fix) | Yes | PLL-N5-FRAC v3.1 | D. Achterberg | 2026-08-06 | PLL-N5-FRAC RN rev 6: v3.1 fixed-issue list includes PLLF-0412 (lock-detect during SSC ramp) |
| ALX4100-E11 | resolved - UART-16550C v1.2 (fixed-in version) | Yes | UART-16550C v1.2 | B. Solano | 2026-08-06 | UART-16550C RN rev 3: v1.2 fixed-issue list includes U16C-0118 (LSR overrun flag not cleared on read) |
| ALX4100-E12 | resolved - OTP-N5-4K v2.0 (N5 port of the OTP v2.0 fix) | Yes | OTP-N5-4K v2.0 | I. Carvalho | 2026-08-06 | OTP-N5-4K RN rev 5: v2.0 fixed-issue list includes OTPN-0087 (read margin at VDD < 0.70 V; qualified at 0.675 V) |
| ALX4100-E13 | resolved - QSPI-CTL v2.3 (fixed in v2.2, same release line); KESTREL uses 133 MHz SDR | Yes | QSPI-CTL v2.3 | R. Lindqvist | 2026-08-06 | QSPI-CTL RN rev 7: v2.3 fixed-issue list includes QSPC-0231 (DTR read sampling at 200 MHz), carried from v2.2 |
| ALX4100-E14 | resolved - NPU-TILE v3.0 includes fix; covergroup cg_npu_sparse_decomp_zero_blk (Escape-history) | Yes | NPU-TILE v3.0 | V. Halloran | 2026-08-06 | - |

Result: 11 carry-forward errata reviewed; 9 resolved by IP version; 1 in-house redesign (E03) with verification tracked in KST-VPLAN-010 / KST-COV-011; 1 N/A (E07). 3 errata not carried forward (E02, E06, E09).

## 6. Hash check (CHK-IP-02)

Hash check (CHK-IP-02): 25/25 match

Method: the sha256 of each delivered IP package in the IP vault is compared with the files referenced by the implementation database used to build netlist kst_top_nl_2026.08.07 (RTL file lists, LIB, LEF and GDS views). In-house IP is compared against the tagged release in the design repository. Run 2026-08-09 by B. Solano; log ipbom_hash_2026-08-09.log. Result: 25/25 match, 0 mismatches, 0 missing views.

## 7. Approvals

| Role | Name | Date |
|---|---|---|
| Prepared: IP Manager | Beatriz Solano | 2026-08-10 |
| Reviewed: Memory Subsystem Owner (MIPV IP) | Anjali Deshmukh | 2026-08-07 |
| Reviewed: PCIe Subsystem Owner | Leo Brandt | 2026-08-07 |
| Reviewed: Physical Design Lead (hard-macro views) | Daniel Achterberg | 2026-08-07 |
| Approved: Chief Architect | Priya Raghavan | 2026-08-10 |
