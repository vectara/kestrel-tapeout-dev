# KST-PI-040 Power Integrity (IR / EM) Sign-off Report

| Field | Value |
|---|---|
| Doc ID | KST-PI-040 |
| Title | Power Integrity (IR / EM) Sign-off Report |
| Revision | C (supersedes B) |
| Date | 2026-09-23 |
| Owner | Grace Adeyemi (PI Lead) |
| Status | Released for TRR-3 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Purpose and scope

This report records full-chip power-integrity sign-off of ALX-5100 (KESTREL) for TRR-3 (2026-09-25). It covers static IR drop, dynamic IR drop (vectorless and vector-based) and electromigration (signal and power/ground) on the core supply rails, checked against the tape-out readiness checklist ALD-QA-CHK-007 rev 7.2, rules CHK-PI-01, CHK-PI-02 and CHK-PI-03.

- Analysed netlist: `kst_top_nl_2026.09.19` (full chip, flat power/ground).
- Analysed layout: `kst_top_pnr_2026.09.19` (post-route, post-metal-fill).
- Process: foundry N5-class FinFET, 1P15M (two thick top metals + AP/RDL), 300 mm wafers. Die 19.20 mm x 18.80 mm.

### 1.1 Rails in scope

| Rail | Nominal | Operating range (sign-off) | Main loads | Supply |
|---|---|---|---|---|
| VDD_NPU | 0.750 V | 0.675 - 0.825 V | NPU clusters u_npu_c0..u_npu_c3 (16 tiles, u_npu_cN/u_tile0..u_tile3), u_npu_top | Dedicated PMIC rail |
| VDD_CORE | 0.750 V | 0.675 - 0.825 V | u_noc, u_cpu, u_sec_encl, u_pcie0_wrap (controller side), u_ddr_ss controllers u_mc0..u_mc3, u_gbuf logic and SRAM periphery, u_periph, u_core/u_pmu_if, u_core/u_crg; switched domain PD_PCIE1 (u_pcie1_wrap) | PMIC rail |
| VDD_SRAM | 0.800 V | 0.720 - 0.880 V | SRAM bit-cell arrays: NPU tile SRAM (16 x 4 MiB), u_gbuf (32 MiB), CPU L2 (1 MiB), security-enclave SRAM. Tracks VDD_CORE +50 mV | PMIC rail |
| VDD_AON | 0.750 V | 0.675 - 0.825 V | u_aon: PMU (u_aon/u_pmu, u_aon/u_pmu/u_wake_ctl), fuse shadow (u_aon/u_fuse_shadow), RTC, 25 MHz crystal oscillator | PMIC LDO rail |

PD_PCIE1 is analysed with its header switches OFF, matching the ALX-5100 SKU (PCIE1 fused off, `FUSE_PCIE1_DIS=1`). Only switch-fabric and isolation-cell leakage is drawn from VDD_CORE. PD_NPU0..PD_NPU3 (per-cluster header switches on VDD_NPU, KST-ARCH-001 section 8.2) are analysed with the switches ON, the worst case for IR; header-switch on-resistance is included in the VDD_NPU PG extraction, so every VDD_NPU result in this report includes the switch drop. LP-IDLE uses NPU clock gating (vec_idle_to_active_step); cluster power-up in-rush is analysed in a separate switch-enable run (section 7). No other power-gated domains exist on the core rails.

### 1.2 Out of scope

| Item | Covered by |
|---|---|
| VDDIO_A, VDDIO_B, VDDIO_C, VDDIO_D (GPIO bank I/O supplies) | I/O simultaneous-switching-noise (SSN) analysis owned by Package & I/O (Rachel Lindqvist) |
| PCIe PHY analog rails (VDDA_PCIE_*) | Vendor PHY PI models and PHY integration checklist |
| LPDDR5X PHY I/O and analog rails (VDDQ_LPX_*, VDDA_LPX_*) | Vendor PHY PI models and PHY integration checklist |
| PLL analog rail (VDDA_PLL_0V75) | PLL integration guide (on-package filter) |
| VPP_OTP | ATE-only programming supply; not powered in the application |

PHY hard macros are modelled as black boxes with vendor current models on their core-side pins (per KST-IPBOM-050). Their VDD_CORE pins are in scope.

## 2. Sign-off summary

**Result: PASS on all in-scope rails.** Static IR, dynamic IR and EM meet ALD-QA-CHK-007 rev 7.2 on netlist `kst_top_nl_2026.09.19`. No PI waivers are requested and there are no open PI items.

### 2.1 Rail summary

Percentages are of rail nominal. Dynamic IR is the worst of the vectorless run and all seven vector-based runs, using the worst per-cycle average (effective drop averaged over one period of the local clock). All drops are effective drops (VDD droop plus VSS bounce).

| Rail | Nominal | Static IR | Static budget | Dynamic IR (worst) | Dynamic budget | Result |
|---|---|---|---|---|---|---|
| VDD_NPU | 0.750 V | 1.6% (12.0 mV) | 2.5% | 7.4% (55.5 mV) | 8.0% (60.0 mV) | PASS |
| VDD_CORE | 0.750 V | 1.1% (8.3 mV) | 2.5% | 5.2% (39.0 mV) | 8.0% (60.0 mV) | PASS |
| VDD_SRAM | 0.800 V | 0.9% (7.2 mV) | 2.5% | 4.1% (32.8 mV) | 6.0% (48.0 mV) | PASS |
| VDD_AON | 0.750 V | 0.3% (2.3 mV) | 2.5% | 1.2% (9.0 mV) | 5.0% (37.5 mV) | PASS |

### 2.2 Worst location per rail

| Rail | Worst static region | Worst dynamic region | Worst vector | Margin to dynamic budget |
|---|---|---|---|---|
| VDD_NPU | u_npu_c2/u_tile3 | u_npu_c2/u_tile3 | vec_resnet50_l3_burst | 0.6 pt (4.5 mV) |
| VDD_CORE | u_ddr_ss/u_mc2 | u_ddr_ss/u_mc2 | vec_mem_stream_273gbps | 2.8 pt (21.0 mV) |
| VDD_SRAM | u_gbuf (bit-cell arrays) | u_gbuf (bit-cell arrays) | vec_bert_attn_peak | 1.9 pt (15.2 mV) |
| VDD_AON | u_aon/u_pmu | u_aon/u_pmu | vec_boot_secure | 3.8 pt (28.5 mV) |

### 2.3 Checklist compliance

| Rule | Requirement (ALD-QA-CHK-007 rev 7.2) | Result on `kst_top_nl_2026.09.19` | Status |
|---|---|---|---|
| CHK-PI-01 | Static IR drop per rail <= 2.5% of nominal | Worst 1.6% (VDD_NPU); VDD_CORE 1.1%, VDD_SRAM 0.9%, VDD_AON 0.3% | PASS |
| CHK-PI-02 | Dynamic IR, worst of vectorless and vector-based, worst per-cycle effective drop: VDD_NPU and VDD_CORE <= 8.0%, VDD_SRAM <= 6.0%, VDD_AON <= 5.0% of nominal | VDD_NPU 7.4%, VDD_CORE 5.2%, VDD_SRAM 4.1%, VDD_AON 1.2% | PASS |
| CHK-PI-03 | EM on signal and PG nets: 0 violations at Tj = 110 C, 10-year lifetime (87,600 h) | 0 signal EM violations, 0 PG EM violations | PASS |

## 3. Analysis setup

### 3.1 Database, libraries and tools

| Item | Setting |
|---|---|
| Tool | IR/EM sign-off tool, production release qualified in the foundry N5-class reference flow. The same release and settings are used for every run in this report |
| Netlist | `kst_top_nl_2026.09.19` |
| Layout | `kst_top_pnr_2026.09.19` (post-route, post-metal-fill, spare cells tied) |
| Signal parasitics | Typical RC at 85 C, used for switching power (load capacitance) |
| PG extraction | In-tool PG grid extraction at rcworst, metal temperature 105 C, all layers M0-M15 + AP, vias as arrays |
| Current models | STDCELL-N5-H210 v1.2 (SVT/LVT/ULVT) tt_0p750v_85c current libraries; leakage scaled to Tj 105 C. SRAM-N5-COMP v2.1 macro current models. Vendor current models for PCIe and LPDDR5X PHY hard macros (core-side pins; PHY-LP5X-N5 v2.7.0 models from ECO-B-004, PCIE5-PHY-N5 v1.4) |
| Technology / EM rules | Foundry N5-class IR/EM technology file and EM rule set, sign-off revision |
| Package model | PKG-RLC-KST-v3, distributed RLC per bump group, from Package & I/O (Rachel Lindqvist), released 2026-07-24 (section 3.4) |
| Board / VRM model | Reference-card PDN model R2: PMIC output impedance plus bulk and MLCC network per core rail |
| Temperature | Tj 105 C for IR (leakage and metal resistance); Tj 110 C for EM |
| Transient solver | 10 ps time step; per-instance current waveforms from library current models; package and board RLC co-simulated |
| Dynamic IR metric | Per-instance effective drop (VDD droop + VSS bounce) averaged over one period of the region's own local clock (0.667 ns cpu_clk, 0.833 ns npu_clk, 0.938 ns mc_clk, 1.000 ns core_clk and pcie_core_clk, 2.000 ns sec_clk, 5.000 ns periph_clk, 40 ns aon_clk), i.e. the effective voltage seen by timing; the worst cycle over the analysed window is reported (CHK-PI-02 definition) |
| Run window | 2026-09-20 .. 2026-09-22 |
| Run IDs | `pi_kst_c0920_static`, `pi_kst_c0920_vl`, `pi_kst_c0920_vb01` .. `pi_kst_c0920_vb07`, `pi_kst_c0920_inrush`, `em_kst_c0920_sig`, `em_kst_c0920_pg` |

### 3.2 PDN grid (global grid on M13-M15 + AP)

The global power grid is built on the three upper layers. M14 and M15 are the thick top metals, and AP (aluminium RDL) carries bump landing and bump-to-grid redistribution. Below M13 the grid continues as a stapled intermediate mesh down to the M0 standard-cell follow-pin rails. VDD_NPU is confined to the NPU cluster regions. VDD_CORE and VDD_SRAM are interleaved in memory regions (VDD_CORE / VDD_SRAM / VSS stripe order on M13-M15). VDD_AON is an island in the AON region with its own bumps.

| Layer | Direction | Role | Strap width | Strap pitch (VDD/VSS pair) | PG track share |
|---|---|---|---|---|---|
| AP | - | Bump landing pads and RDL straps between bump columns | 31.5 µm | 150.0 µm (bump pitch) | 42.0% |
| M15 | Horizontal | Global grid, thick | 4.50 µm | 13.50 µm | 66.7% |
| M14 | Vertical | Global grid, thick | 4.50 µm | 13.50 µm | 66.7% |
| M13 | Horizontal | Global grid | 1.26 µm | 5.04 µm | 50.0% |
| M9-M12 | Alternating | Intermediate mesh | 0.36 µm | 3.60 µm | 20.0% |
| M4-M8 | Alternating | Intermediate mesh, via-pillar staples | 0.08 µm | 1.92 µm | 8.3% |
| M1-M3 | Alternating | Staples to M0 follow-pin rails | per cell row | every 2nd placement site column | - |
| M0 | Horizontal | Standard-cell follow-pin rails | library rail width | row height | - |

### 3.3 Bumps and rail currents

Cu-pillar bumps (KST-PKG-002); the core power/ground bump array is on a 150 µm pitch (130 µm minimum in the PHY and I/O bump fields). Static analysis uses, for each rail, the time-averaged current of the highest-power vector for that rail. These per-rail maxima are combined into an envelope of 63.4 W on the core rails. KST-ARCH-001 section 8.5 budgets 67.8 W on these rails at TDP; static IR scales linearly with current, so the budget case gives VDD_NPU 1.7% static, still within the 2.5% limit.

| Rail | PG bumps | Static analysis current | Peak cycle-average current | Average current per bump | Max current per bump | Bump EM limit (Tj 110 C) |
|---|---|---|---|---|---|---|
| VDD_NPU | 3,184 | 58.7 A | 71.4 A | 18.4 mA | 46.2 mA | 180 mA |
| VDD_CORE | 1,436 | 18.9 A | 24.6 A | 13.2 mA | 31.8 mA | 180 mA |
| VDD_SRAM | 412 | 6.4 A | 8.1 A | 15.5 mA | 29.4 mA | 180 mA |
| VDD_AON | 16 | 55 mA | 71 mA | 3.4 mA | 6.1 mA | 180 mA |
| VSS (common) | 5,120 | 84.1 A (return) | - | 16.4 mA | 44.7 mA | 180 mA |

### 3.4 Package and board model

Package: FCBGA 45.0 mm x 45.0 mm, 2,304 balls (48 x 48), 0.8 mm pitch. Model PKG-RLC-KST-v3 gives distributed R, L and C per 4 x 4 bump group from die bumps to ball groups, including the die-side capacitors (DSC) and plane-to-plane capacitance. The board model is lumped per rail. VDD_NPU, VDD_CORE and VDD_SRAM use differential remote sense from die-side sense bumps, so DC drop in the board and package is regulated out by the PMIC and static IR is reported from bump to instance. VDD_AON is sensed at the package balls, so its package DC drop (0.5 mV) is included in the VDD_AON static result.

| Rail | Package loop inductance (bumps to DSC) | Package DC resistance (bumps to balls) | Die-side capacitors | Voltage sense point |
|---|---|---|---|---|
| VDD_NPU | 6.2 pH | 0.11 mΩ | 24 x 2.2 µF | Die-side sense bumps |
| VDD_CORE | 11.8 pH | 0.24 mΩ | 12 x 2.2 µF | Die-side sense bumps |
| VDD_SRAM | 38 pH | 0.71 mΩ | 6 x 1.0 µF | Die-side sense bumps |
| VDD_AON | 410 pH | 9.8 mΩ | 2 x 0.1 µF | Package balls |

### 3.5 On-die decoupling

Intentional decap cells fill 7.8% of the placement area in the NPU tiles and 5.1% in the VDD_CORE partitions. The high-density MIM capacitor module is placed under the NPU and u_noc bump fields. Z target is the dynamic budget divided by the largest current step on the rail (section 7). Peak |Z| is the peak of the impedance seen from the bumps between 1 MHz and 500 MHz, including the package.

| Rail | Intentional decap cells | Intrinsic (non-switching) | MIM | Total on-die C | First-droop resonance | Peak \|Z\| at bumps | Z target | Result |
|---|---|---|---|---|---|---|---|---|
| VDD_NPU | 412 nF | 538 nF | 176 nF | 1,126 nF | 60.2 MHz | 1.41 mΩ | 2.78 mΩ | PASS |
| VDD_CORE | 214 nF | 286 nF | 64 nF | 564 nF | 61.7 MHz | 2.90 mΩ | 8.82 mΩ | PASS |
| VDD_SRAM | 96 nF | 188 nF | - | 284 nF | 48.4 MHz | 7.10 mΩ | 20.0 mΩ | PASS |
| VDD_AON | 1.9 nF | 0.8 nF | - | 2.7 nF | 151.3 MHz | 0.24 Ω | 1.79 Ω | PASS |

## 4. Vectors

### 4.1 Vectorless

State-propagation vectorless analysis with these settings: NPU datapath toggle rate 0.30, control logic 0.15, clock nets from the clock definitions (npu_clk 1200.0 MHz, core_clk 1000.0 MHz, cpu_clk 1500.0 MHz, mc_clk 1066.7 MHz, pcie_core_clk 1000.0 MHz, sec_clk 500.0 MHz, periph_clk 200.0 MHz, aon_clk 25.000 MHz), SRAM access probability 0.5 per cycle, 40 ns simulated. Total power per rail is scaled to the vector-based peak window current in section 3.3. The vectorless run covers regions and switching combinations that the workload vectors do not reach.

### 4.2 Vector-based windows

The windows were captured on the emulation platform from full-chip workload runs, as per-cycle activity. For each workload the peak-power window and the peak di/dt window were selected from the power profile. The activity is mapped to the analysed netlist by name (register mapping rate 99.7%); unmapped nets fall back to vectorless propagation. The windows are re-mapped by name for each netlist release.

| ID | Vector | Scenario | Active clocks | Analysed length | Selection criterion |
|---|---|---|---|---|---|
| VB01 | vec_resnet50_l3_burst | ResNet-50 INT8, batch 32, layer-3 convolution burst; all 16 tiles at >= 94% MAC utilization | npu_clk, core_clk, mc_clk | 400 ns | Peak NPU power and largest layer-boundary current step |
| VB02 | vec_bert_attn_peak | BERT-Large INT8 attention block, sequence 384; peak tile-SRAM and u_gbuf read bandwidth | npu_clk, core_clk, mc_clk | 400 ns | Peak VDD_SRAM current |
| VB03 | vec_llm_decode_kv | 7B-parameter LLM INT8 decode step with KV-cache streaming from LPDDR5X | npu_clk, core_clk, cpu_clk, mc_clk | 400 ns | Mixed CPU, NoC and memory activity |
| VB04 | vec_mem_stream_273gbps | LPDDR5X read/write stream on all four sub-systems at 273.1 GB/s aggregate | core_clk, mc_clk | 400 ns | Peak u_ddr_ss and u_noc current |
| VB05 | vec_boot_secure | POR release, fuse-shadow load, secure-boot ROM (SHA-384, ECDSA P-384 verify, AES-256-GCM), root-key ladder load | aon_clk, sec_clk, core_clk, periph_clk | 1,600 ns (stitched: fuse-shadow load, SHA-384 / ECDSA verify burst, AES-256-GCM decrypt and key-ladder load) | Peak VDD_AON and u_sec_encl current |
| VB06 | vec_pcie_dma_saturate | PCIe Gen5 x16 DMA read and write at link saturation into u_gbuf through u_noc | pcie_core_clk, core_clk, npu_clk | 400 ns | Peak u_pcie0_wrap current |
| VB07 | vec_idle_to_active_step | LP-IDLE to ACTIVE: core_clk from 15.625 MHz to 1000.0 MHz, NPU cluster clock ungating with hardware stagger, CPU wake | all functional clocks | 1,200 ns | Largest supply ramp (di/dt) |

Scan shift (test mode; owned by DFT, KST-DFT-EXC section 2): ATPG pattern set v1.0 analysed at 200 MHz shift with low-power (adjacent) fill and 4 staggered chain groups, run `pi_kst_c0921_shift`; worst effective drop VDD_NPU 6.3%, VDD_CORE 4.9%, inside the CHK-PI-02 budgets.

## 5. Static IR results

Rail-level results are in section 2.1. The table below lists the worst regions per rail.

| Rail | Region / instance | Static IR | Budget | Result |
|---|---|---|---|---|
| VDD_NPU | u_npu_c2/u_tile3 | 1.6% (12.0 mV) | 2.5% | PASS |
| VDD_NPU | u_npu_c2/u_tile2 | 1.5% (11.6 mV) | 2.5% | PASS |
| VDD_NPU | u_npu_c1/u_tile3 | 1.5% (11.3 mV) | 2.5% | PASS |
| VDD_NPU | u_npu_c3/u_tile0 | 1.5% (10.9 mV) | 2.5% | PASS |
| VDD_NPU | u_npu_c0/u_tile0 | 1.3% (9.4 mV) | 2.5% | PASS |
| VDD_NPU | u_npu_top | 0.8% (6.1 mV) | 2.5% | PASS |
| VDD_CORE | u_ddr_ss/u_mc2 | 1.1% (8.3 mV) | 2.5% | PASS |
| VDD_CORE | u_noc | 1.0% (7.4 mV) | 2.5% | PASS |
| VDD_CORE | u_cpu | 0.9% (6.9 mV) | 2.5% | PASS |
| VDD_CORE | u_pcie0_wrap | 0.9% (6.6 mV) | 2.5% | PASS |
| VDD_CORE | u_sec_encl | 0.6% (4.2 mV) | 2.5% | PASS |
| VDD_CORE | u_core/u_pmu_if | 0.4% (3.1 mV) | 2.5% | PASS |
| VDD_SRAM | u_gbuf (bit-cell arrays) | 0.9% (7.2 mV) | 2.5% | PASS |
| VDD_SRAM | u_npu_c2/u_tile3 (tile SRAM arrays) | 0.8% (6.5 mV) | 2.5% | PASS |
| VDD_AON | u_aon/u_pmu | 0.3% (2.3 mV) | 2.5% | PASS |
| VDD_AON | u_aon/u_fuse_shadow | 0.3% (2.0 mV) | 2.5% | PASS |

Rail-average static drop: VDD_NPU 0.9% (6.8 mV), VDD_CORE 0.6% (4.5 mV), VDD_SRAM 0.5% (4.0 mV), VDD_AON 0.2% (1.4 mV).

## 6. Dynamic IR results

### 6.1 Per-vector results

Worst per-cycle effective drop per rail for each run, with the region where it occurs.

| Vector | VDD_NPU (worst region) | VDD_CORE (worst region) | VDD_SRAM (worst region) | VDD_AON (worst region) | Result |
|---|---|---|---|---|---|
| vectorless | 6.9% (51.8 mV) at u_npu_c2/u_tile3 | 4.6% (34.5 mV) at u_ddr_ss/u_mc2 | 3.6% (28.8 mV) at u_gbuf | 0.9% (6.8 mV) at u_aon/u_pmu | PASS |
| vec_resnet50_l3_burst | 7.4% (55.5 mV) at u_npu_c2/u_tile3 | 3.8% (28.5 mV) at u_noc | 3.9% (31.2 mV) at u_npu_c2/u_tile3 | 0.8% (6.0 mV) at u_aon/u_pmu | PASS |
| vec_bert_attn_peak | 7.1% (53.3 mV) at u_npu_c1/u_tile3 | 4.2% (31.5 mV) at u_gbuf | 4.1% (32.8 mV) at u_gbuf | 0.8% (6.0 mV) at u_aon/u_pmu | PASS |
| vec_llm_decode_kv | 6.4% (48.0 mV) at u_npu_c1/u_tile1 | 4.4% (33.0 mV) at u_cpu | 3.7% (29.6 mV) at u_gbuf | 0.8% (6.0 mV) at u_aon/u_pmu | PASS |
| vec_mem_stream_273gbps | 4.4% (33.0 mV) at u_npu_c2/u_tile3 | 5.2% (39.0 mV) at u_ddr_ss/u_mc2 | 3.2% (25.6 mV) at u_gbuf | 0.8% (6.0 mV) at u_aon/u_pmu | PASS |
| vec_boot_secure | 0.9% (6.8 mV) at u_npu_top | 3.2% (24.0 mV) at u_sec_encl | 1.9% (15.2 mV) at u_sec_encl | 1.2% (9.0 mV) at u_aon/u_pmu | PASS |
| vec_pcie_dma_saturate | 5.1% (38.3 mV) at u_npu_c3/u_tile0 | 4.5% (33.8 mV) at u_pcie0_wrap | 3.4% (27.2 mV) at u_gbuf | 0.8% (6.0 mV) at u_aon/u_pmu | PASS |
| vec_idle_to_active_step | 6.7% (50.3 mV) at u_npu_c3/u_tile1 | 4.0% (30.0 mV) at u_noc | 2.9% (23.2 mV) at u_npu_c3/u_tile1 | 1.0% (7.5 mV) at u_aon/u_pmu | PASS |
| **Worst of all runs** | **7.4% (55.5 mV)** | **5.2% (39.0 mV)** | **4.1% (32.8 mV)** | **1.2% (9.0 mV)** | **PASS** |

### 6.2 Hotspot table

Top regions per rail: worst dynamic IR per region across all eight runs (vectorless + VB01..VB07); the switch-enable in-rush run is reported in section 7. Window start times are measured from the start of the analysed window of the named vector.

| # | Rail | Region / instance | Worst vector | Worst cycle starts at (ns) | Worst dynamic IR | Budget | Result |
|---|---|---|---|---|---|---|---|
| H01 | VDD_NPU | u_npu_c2/u_tile3 | vec_resnet50_l3_burst | 212.4 | 7.4% (55.5 mV) | 8.0% | PASS |
| H02 | VDD_NPU | u_npu_c2/u_tile2 | vec_resnet50_l3_burst | 212.6 | 7.2% (54.0 mV) | 8.0% | PASS |
| H03 | VDD_NPU | u_npu_c1/u_tile3 | vec_bert_attn_peak | 148.9 | 7.1% (53.3 mV) | 8.0% | PASS |
| H04 | VDD_NPU | u_npu_c2/u_tile1 | vec_resnet50_l3_burst | 213.1 | 7.0% (52.5 mV) | 8.0% | PASS |
| H05 | VDD_NPU | u_npu_c3/u_tile0 | vec_bert_attn_peak | 149.3 | 6.9% (51.8 mV) | 8.0% | PASS |
| H06 | VDD_NPU | u_npu_c1/u_tile2 | vec_resnet50_l3_burst | 211.8 | 6.8% (51.0 mV) | 8.0% | PASS |
| H07 | VDD_NPU | u_npu_c3/u_tile1 | vec_idle_to_active_step | 702.5 | 6.7% (50.3 mV) | 8.0% | PASS |
| H08 | VDD_NPU | u_npu_c2/u_tile0 | vec_resnet50_l3_burst | 213.4 | 6.6% (49.5 mV) | 8.0% | PASS |
| H09 | VDD_NPU | u_npu_c0/u_tile3 | vec_bert_attn_peak | 150.2 | 6.5% (48.8 mV) | 8.0% | PASS |
| H10 | VDD_NPU | u_npu_c1/u_tile1 | vec_llm_decode_kv | 87.6 | 6.4% (48.0 mV) | 8.0% | PASS |
| H11 | VDD_NPU | u_npu_c3/u_tile3 | vec_resnet50_l3_burst | 214.0 | 6.3% (47.3 mV) | 8.0% | PASS |
| H12 | VDD_NPU | u_npu_c0/u_tile2 | vec_resnet50_l3_burst | 211.5 | 6.3% (47.0 mV) | 8.0% | PASS |
| H13 | VDD_NPU | u_npu_c1/u_tile0 | vectorless | 21.6 | 6.2% (46.5 mV) | 8.0% | PASS |
| H14 | VDD_NPU | u_npu_c0/u_tile1 | vec_bert_attn_peak | 150.7 | 6.1% (45.8 mV) | 8.0% | PASS |
| H15 | VDD_NPU | u_npu_c3/u_tile2 | vec_llm_decode_kv | 88.1 | 6.0% (45.0 mV) | 8.0% | PASS |
| H16 | VDD_NPU | u_npu_c0/u_tile0 | vectorless | 18.2 | 5.9% (44.3 mV) | 8.0% | PASS |
| H17 | VDD_NPU | u_npu_top (cluster interconnect, trace funnel) | vec_resnet50_l3_burst | 215.2 | 4.8% (36.0 mV) | 8.0% | PASS |
| H18 | VDD_CORE | u_ddr_ss/u_mc2 | vec_mem_stream_273gbps | 301.7 | 5.2% (39.0 mV) | 8.0% | PASS |
| H19 | VDD_CORE | u_ddr_ss/u_mc1 | vec_mem_stream_273gbps | 301.9 | 5.0% (37.5 mV) | 8.0% | PASS |
| H20 | VDD_CORE | u_ddr_ss/u_mc3 | vec_mem_stream_273gbps | 302.3 | 4.9% (36.8 mV) | 8.0% | PASS |
| H21 | VDD_CORE | u_ddr_ss/u_mc0 | vec_mem_stream_273gbps | 302.0 | 4.8% (36.0 mV) | 8.0% | PASS |
| H22 | VDD_CORE | u_noc | vec_mem_stream_273gbps | 303.4 | 4.7% (35.3 mV) | 8.0% | PASS |
| H23 | VDD_CORE | u_pcie0_wrap | vec_pcie_dma_saturate | 126.8 | 4.5% (33.8 mV) | 8.0% | PASS |
| H24 | VDD_CORE | u_cpu | vec_llm_decode_kv | 92.3 | 4.4% (33.0 mV) | 8.0% | PASS |
| H25 | VDD_CORE | u_gbuf (logic and SRAM periphery) | vec_bert_attn_peak | 151.0 | 4.2% (31.5 mV) | 8.0% | PASS |
| H26 | VDD_CORE | u_sec_encl | vec_boot_secure | 1,466.2 | 3.2% (24.0 mV) | 8.0% | PASS |
| H27 | VDD_CORE | u_core/u_crg | vec_idle_to_active_step | 655.0 | 2.6% (19.5 mV) | 8.0% | PASS |
| H28 | VDD_CORE | u_core/u_pmu_if | vec_idle_to_active_step | 651.8 | 2.4% (18.0 mV) | 8.0% | PASS |
| H29 | VDD_CORE | u_periph | vec_boot_secure | 1,512.4 | 2.1% (15.8 mV) | 8.0% | PASS |
| H30 | VDD_SRAM | u_gbuf (bit-cell arrays) | vec_bert_attn_peak | 151.3 | 4.1% (32.8 mV) | 6.0% | PASS |
| H31 | VDD_SRAM | u_npu_c2/u_tile3 (tile SRAM arrays) | vec_resnet50_l3_burst | 212.9 | 3.9% (31.2 mV) | 6.0% | PASS |
| H32 | VDD_SRAM | u_cpu (L2 arrays) | vec_llm_decode_kv | 92.8 | 3.1% (24.8 mV) | 6.0% | PASS |
| H33 | VDD_AON | u_aon/u_pmu | vec_boot_secure | 36.4 | 1.2% (9.0 mV) | 5.0% | PASS |
| H34 | VDD_AON | u_aon/u_fuse_shadow | vec_boot_secure | 38.1 | 1.1% (8.3 mV) | 5.0% | PASS |

Notes on the hotspot results:

- u_npu_c2/u_tile3 is next to the u_ddr_ss/u_phy2 bump field, where the VDD_NPU bump density is 18% lower than in the cluster interior. Its worst window is the vec_resnet50_l3_burst layer-3 start, when all four tiles of cluster 2 ramp together. The result is 7.4% (55.5 mV) against the 8.0% (60.0 mV) budget.
- The other NPU tiles range from 5.9% to 7.2%. All four cluster 2 tiles peak in vec_resnet50_l3_burst. Tiles in clusters 0, 1 and 3 peak in a mix of vec_resnet50_l3_burst, vec_bert_attn_peak, vec_llm_decode_kv, vec_idle_to_active_step and the vectorless run.
- On VDD_CORE the LPDDR5X controllers u_ddr_ss/u_mc0..u_mc3 are highest in vec_mem_stream_273gbps (4.8% to 5.2%). u_noc, u_pcie0_wrap, u_cpu and u_sec_encl are between 3.2% and 4.7%.
- The VDD_AON effective drop is mostly shared-VSS bounce. The AON-only contribution in vec_boot_secure (fuse-shadow load) is 3.1 mV.

### 6.3 Drop distribution (share of instances per rail, worst run)

| Rail | < 2.0% | 2.0% - 4.0% | 4.0% - 6.0% | 6.0% - 7.0% | > 7.0% |
|---|---|---|---|---|---|
| VDD_NPU | 6.4% | 41.7% | 45.8% | 5.8% | 0.3% |
| VDD_CORE | 38.2% | 55.1% | 6.7% | 0.0% | 0.0% |
| VDD_SRAM | 51.6% | 47.9% | 0.5% | 0.0% | 0.0% |
| VDD_AON | 100.0% | 0.0% | 0.0% | 0.0% | 0.0% |

## 7. Current ramp (di/dt) and decap summary

| Event | Vector | Rail | Current step | Ramp time | di/dt | Mechanism | Worst drop | Result |
|---|---|---|---|---|---|---|---|---|
| NPU layer-boundary burst, cluster 2 | vec_resnet50_l3_burst | VDD_NPU | 21.6 A | 20 ns | 1.08 A/ns | Four tiles start the layer-3 MAC arrays together | 7.4% (55.5 mV) | PASS |
| NPU clock ungating, LP-IDLE to ACTIVE | vec_idle_to_active_step | VDD_NPU | 4 x 14.5 A | 53.3 ns per cluster, 213.3 ns stagger | 0.27 A/ns | Hardware cluster-enable stagger (256 npu_clk cycles) and 4-step MAC-array enable (25/50/75/100%) | 6.7% (50.3 mV) | PASS |
| core_clk divider walk, 15.625 MHz to 1000.0 MHz (largest sub-step /4 -> /1 shown) | vec_idle_to_active_step | VDD_CORE | 4.0 A (of 5.3 A over the whole walk) | 16 ns (activity ramp after the /1 edge) | 0.25 A/ns | Stepped divider walk /64, /16, /4, /1 in u_core/u_crg, 8 cycles per step (about 0.2 us in total); current scales with frequency, so /4 -> /1 is the largest sub-step | 4.0% (30.0 mV) | PASS |
| CPU cluster wake | vec_idle_to_active_step | VDD_CORE | 4.2 A | 30 ns | 0.14 A/ns | Cores released in two pairs | 2.9% (21.8 mV) | PASS |
| LPDDR5X four-channel read burst | vec_mem_stream_273gbps | VDD_CORE | 6.8 A | 12 ns | 0.57 A/ns | u_mc0..u_mc3 read-data path and DFI activity | 5.2% (39.0 mV) | PASS |
| PCIe DMA burst | vec_pcie_dma_saturate | VDD_CORE | 3.9 A | 16 ns | 0.24 A/ns | 512-bit datapath at pcie_core_clk | 4.5% (33.8 mV) | PASS |
| Secure-boot crypto start | vec_boot_secure | VDD_CORE | 1.1 A | 10 ns | 0.11 A/ns | SHA-384 and AES-256-GCM engines enabled | 3.2% (24.0 mV) | PASS |
| Attention SRAM read burst | vec_bert_attn_peak | VDD_SRAM | 2.4 A | 10 ns | 0.24 A/ns | u_gbuf and tile SRAM bank reads | 4.1% (32.8 mV) | PASS |
| PD_NPU2 power-up while PD_NPU0/1/3 run (firmware cluster enable) | switch-enable in-rush run (vec_llm_decode_kv on running clusters) | VDD_NPU | 3.2 A in-rush | 1.6 us | 0.002 A/ns | Weak-then-strong header-switch daisy chain (npu_pwr_ack) | 5.1% (38.3 mV) at u_npu_c1/u_tile3 | PASS |
| Fuse-shadow load at POR | vec_boot_secure | VDD_AON | 21 mA | 40 ns | 0.5 mA/ns | u_aon/u_fuse_shadow load sequence | 1.2% (9.0 mV) | PASS |

The transient runs include the package and board RLC, so the first-droop response (48 MHz to 62 MHz on the high-current rails, section 3.5) is part of every reported worst drop. Decap sufficiency is confirmed by the transient runs: every rail's worst drop is inside its budget with the decap and package model in section 3.

## 8. Electromigration

EM limits come from the foundry N5-class EM rule set at Tj = 110 C and a 10-year lifetime (87,600 h, 100% power-on). Signal EM uses sign-off activity (toggle rates from the vector set, minimum 0.20 on data nets) and the actual slew and load. Self-heating is included for clock mesh and spine nets; the largest self-heating temperature rise is 4.1 C.

| Check | Scope | Violations | Worst utilization | Worst location |
|---|---|---|---|---|
| Signal EM, RMS | All routed signal nets including clock (926 M nets) | 0 | 64.7% | npu_clk mesh driver output, u_npu_c1 (M11) |
| Signal EM, peak | All routed signal nets | 0 | 48.3% | cpu_clk spine, u_cpu (M9) |
| Signal EM, average (unidirectional) | All routed signal nets | 0 | 41.2% | u_noc router 3,2 output buffer net (M6) |
| PG EM, wires M0-M12 | VDD_NPU, VDD_CORE, VDD_SRAM, VDD_AON, VSS | 0 | 58.9% | VSS M2 staple, u_npu_c2/u_tile3 |
| PG EM, wires M13-M15 | All core rails and VSS | 0 | 62.3% | VDD_NPU M13 strap, u_npu_c2 |
| PG EM, AP / RDL | All core rails and VSS | 0 | 44.0% | VDD_NPU AP strap next to u_ddr_ss/u_phy2 |
| PG EM, vias (all levels) | All core rails and VSS | 0 | 67.8% | VIA13 array (M13-M14), VDD_NPU, u_npu_c2/u_tile3 |
| Bump EM | 10,168 core-rail PG bumps (VDD_NPU, VDD_CORE, VDD_SRAM, VDD_AON, VSS) | 0 | 25.7% (46.2 mA of 180 mA) | VDD_NPU bump, u_npu_c2 |

**EM total: 0 signal EM violations and 0 PG EM violations** (CHK-PI-03 PASS).

## 9. Power-grid integrity checks

| Check | Result |
|---|---|
| Unconnected PG pins (standard cells and macros) | 0 |
| Floating PG shapes | 0 |
| Missing vias or under-populated PG via arrays | 0 |
| Shorts between rails | 0 (confirmed by LVS) |
| Macro PG pin connection (SRAM, PHY, PLL, OTP) | 100% connected to the specified rails |
| PD_PCIE1 switch state in analysis | OFF (`FUSE_PCIE1_DIS=1`); switch-fabric leakage included in VDD_CORE static |
| PD_NPU0..PD_NPU3 switch state in analysis | ON (all four clusters powered); header-switch on-resistance extracted into the VDD_NPU grid; switch-on in-rush in a separate run (section 7) |

Effective resistance (Reff) from bumps to instance PG pins, VDD plus VSS loop:

| Rail | Median Reff | 99.9th percentile | Max | Project limit | Result |
|---|---|---|---|---|---|
| VDD_NPU | 7.2 Ω | 15.8 Ω | 19.6 Ω | 40 Ω | PASS |
| VDD_CORE | 8.9 Ω | 19.4 Ω | 24.1 Ω | 40 Ω | PASS |
| VDD_SRAM | 5.4 Ω | 11.2 Ω | 13.7 Ω | 40 Ω | PASS |
| VDD_AON | 12.6 Ω | 22.3 Ω | 26.8 Ω | 40 Ω | PASS |

## 10. Timing and IR correlation

The setup-critical STA corners in KST-STA-020 (ss_0p675v_125c and ss_0p675v_m40c) use 0.675 V, which already includes the IR guardband. For VDD_NPU and VDD_CORE the 10% below nominal (75.0 mV) is split into 2.0% (15.0 mV) for PMIC DC accuracy and ripple and 8.0% (60.0 mV) for dynamic IR, which is the CHK-PI-02 budget; the 2.0% PMIC allowance is the regulation tolerance in KST-ARCH-001 sections 8.1 and 10.1. For VDD_SRAM the low end is 0.720 V (80.0 mV below nominal), which covers the 16.0 mV PMIC allowance and the 6.0% (48.0 mV) budget; VDD_AON uses 15.0 mV and its 5.0% (37.5 mV) budget, leaving 22.5 mV (3.0%) unallocated margin (KST-ARCH-001 section 10.1). Because every measured worst-window drop is inside its budget, no IR-annotated derate is applied in STA. Measured worst-window drops depend on the vector set and are not credited as STA margin; timing is guaranteed only down to the 0.675 V corner. The hold-critical ff corners use 0.825 V with no IR drop, which is the worst case for hold. The 0.825 V corner is not an IR construction: it bounds the ATE Vmax screen and burn-in stress (VDD_CORE / VDD_NPU at 0.825 V, including the ALX-5100I -40 C insertion) and PMIC load-release overshoot, so a part that fails hold at ff / -40 C fails the cold Vmax screen.

| Rail | Nominal | STA low corner | PMIC allowance | Dynamic IR budget | Measured worst dynamic drop | Lowest effective voltage (nominal - PMIC - measured) | Covered by STA low corner |
|---|---|---|---|---|---|---|---|
| VDD_NPU | 0.750 V | 0.675 V | 15.0 mV | 60.0 mV | 55.5 mV | 0.6795 V | Yes |
| VDD_CORE | 0.750 V | 0.675 V | 15.0 mV | 60.0 mV | 39.0 mV | 0.6960 V | Yes |
| VDD_SRAM | 0.800 V | 0.720 V | 16.0 mV | 48.0 mV | 32.8 mV | 0.7512 V | Yes |
| VDD_AON | 0.750 V | 0.675 V | 15.0 mV | 37.5 mV | 9.0 mV | 0.7260 V | Yes |

SRAM macros are characterized at VDD_SRAM 0.720 V in the ss corners, which matches the VDD_SRAM low end in the table.

## 11. Post-silicon correlation plan

During A0 bring-up the PVT-MON-N5 supply-voltage sensors on the core rails will be read while running workloads equivalent to vec_resnet50_l3_burst, vec_mem_stream_273gbps and vec_idle_to_active_step. The measured droop will be compared with this report and the result filed with the A0 characterization data. The PMIC load-line and remote-sense settings on the reference card match the board model in section 3.4.

## 12. References

| Doc ID | Title / use in this report |
|---|---|
| ALD-QA-CHK-007 rev 7.2 | Tape-out readiness checklist: CHK-PI-01, CHK-PI-02, CHK-PI-03 |
| KST-ARCH-001 | Architecture specification: rails, power states, clocks |
| KST-PKG-002 | Package, pinout and I/O specification: FCBGA 45.0 mm x 45.0 mm, 2,304 balls |
| KST-STA-020 | STA sign-off report: PVT corners and sign-off voltages |
| KST-IPBOM-050 | IP BOM: library and hard-macro model sources |
| KST-ECO-062 | ECO change log: ECO content of each netlist release |

## 13. Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| PI Lead (author) | Grace Adeyemi | Signed off: PASS, all in-scope rails | 2026-09-23 |
| Physical Design Lead | Daniel Achterberg | Reviewed: agree | 2026-09-23 |
| NPU Cluster Owner | Viktor Halloran | Reviewed VDD_NPU results: agree | 2026-09-23 |
| Package & I/O Lead | Rachel Lindqvist | Confirmed PKG-RLC-KST-v3 as the package model for this run | 2026-09-23 |

## 14. Revision history

| Rev | Date | Author | Change |
|---|---|---|---|
| A | 2026-08-11 | Grace Adeyemi | Initial release for TRR-1 on kst_top_nl_2026.08.07. |
| B | 2026-09-02 | Grace Adeyemi | Re-run on kst_top_nl_2026.08.31 (B); ECOs are in VDD_CORE partitions except ECO-B-002 (u_npu_c0..u_npu_c3/u_dma, VDD_NPU); worst-region delta < 0.1 mV on VDD_CORE and VDD_NPU; PHY-LP5X-N5 v2.7.0 current models integrated (ECO-B-004); all results unchanged. |
| C | 2026-09-23 | Grace Adeyemi | Re-run on kst_top_nl_2026.09.19 (C); ECOs are in VDD_CORE partitions; VDD_CORE dynamic change < 0.1 mV; all results unchanged. |

Rev B details:

- Netlist `kst_top_nl_2026.08.31` includes ECO-B-001 .. ECO-B-006 (see KST-ECO-062). Static IR, vectorless and vector-based dynamic IR (VB01..VB07) and signal and PG EM were re-run in full on `kst_top_pnr_2026.08.31`. The package model (PKG-RLC-KST-v3), board model and emulation windows are unchanged.
- VDD_CORE and VDD_NPU worst-region deltas against rev A are below 0.1 mV in every region (ECO-B-002 changes 27 cells per cluster in u_npu_c0..u_npu_c3/u_dma, away from the u_npu_c2/u_tile3 hotspot), below the reporting resolution. u_ddr_ss uses the PHY-LP5X-N5 v2.7.0 vendor current models delivered with ECO-B-004. The v2.7.0 core-side current models differ from v2.6.1 only in the training/calibration block, which is idle in vec_mem_stream_273gbps, and the incremental u_mc0..u_mc3 re-synthesis (training sequencer, training interface and link-ECC counter only) changed fewer than 1% of controller cells; the u_ddr_ss/u_mc2 worst window moves by +0.04 mV. Reported values are unchanged.
- CHG-B-002 is a pad-ring I/O cell change on an I/O bank supply and is outside the scope of this report (section 1.2).
- EM: 0 signal EM and 0 PG EM violations, the same as rev A.

Rev C details:

- Netlist `kst_top_nl_2026.09.19` includes ECO-C-001 .. ECO-C-003 (see KST-ECO-062). Static IR, vectorless and vector-based dynamic IR (VB01..VB07) and signal and PG EM were re-run in full on `kst_top_pnr_2026.09.19`. The package model (PKG-RLC-KST-v3), board model and emulation windows are unchanged.
- VDD_CORE worst-region delta against rev B is below 0.1 mV in every region, below the reporting resolution. Reported values are unchanged.
- EM: 0 signal EM and 0 PG EM violations, the same as rev A and rev B.
