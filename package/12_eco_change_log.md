# KESTREL ECO & Change Log

| Field | Value |
|---|---|
| Doc ID | KST-ECO-062 |
| Title | ECO & Change Log |
| Revision | C (supersedes B) |
| Date | 2026-09-24 |
| Owner | Daniel Achterberg (PD Lead) |
| Status | Released for TRR-3 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Scope and process

This log records every change applied to the KESTREL implementation database after RTL freeze (tag kst_rtl_2026.07.15, first sign-off netlist kst_top_nl_2026.07.17): netlist ECOs, pad-ring and package changes, third-party IP drops and testbench changes that affect sign-off.

- Change requests are raised in the ECO tracker and reviewed at the weekly ECO board (chair: Daniel Achterberg; members: block owner, STA Lead, Verification Lead, and DFT Lead for scan-affecting changes).
- Before tape-out, netlist ECOs are implemented as all-layer changes in the place-and-route tool with legalized placement; spare and gate-array ECO filler cells (1.5% density) are reserved for post-tape-out metal-only ECOs and are not consumed.
- Change types: **netlist ECO**, **pad-ring**, **IP drop**, **testbench**.
- Date = date the change was merged into the implementation database.
- Verification requirement per CHK-GOV-02: affected sign-off checks re-run after the change and dated after it.

## 2. Change log

| ID | Date | Type | Block | Description | Instances/cells | Reason / ref | Verification performed | Owner |
|---|---|---|---|---|---|---|---|---|
| ECO-A-001 | 2026-07-20 | netlist ECO | NOC (u_noc) | Per-VC credit counter widened from 4 to 5 bits on all 16 mesh routers to support 16-flit VC buffers on the GBUF-attached ports | u_noc/u_rtr_*_*/u_vc_credit: +256 DFF (64 connected router ports x 4 VCs; the 16 mesh-edge ports are tied off, CE-005), +627 comb cells | NOC-0244 (P2): credit counter wrap at 16 outstanding flits in NoC stress test | Full 14-view MCMM STA (SI + POCV) clean; LEC pass; LVS/DRC clean; NoC regression 100% pass | Daniel Achterberg |
| ECO-A-002 | 2026-07-23 | netlist ECO | CPU (u_cpu/u_l2) | L2 ECC syndrome decode fix: three double-bit syndromes were decoded as single-bit correctable | u_cpu/u_l2/u_ecc_dec: 42 cells changed | CPU-0412 (P2), found by formal ECC property check | Full 14-view MCMM STA clean; LEC pass; LVS/DRC clean; ECC formal proof pass | Daniel Achterberg |
| ECO-A-003 | 2026-07-25 | netlist ECO | GBUF / DFT (u_gbuf) | MBIST wrapper clock gating: wrapper clocks gated when mbist_en = 0 in mission mode (about 38 mW saved at core_clk 1000 MHz) | u_gbuf/u_bank*/u_mbist_wrap: +32 ICG cells | DFT-0219 | Full 14-view MCMM STA clean incl. mbist_ss_0p675v_125c_cworst_ccworst; LEC pass; LVS/DRC clean; MBIST pattern simulation pass | Samir Haddad |
| ECO-A-004 | 2026-07-28 | netlist ECO | NPU (u_npu_c1, u_npu_c3) | Scan chain rebalance: 96 internal chains re-stitched, max chain length 684 -> 652 flops; no functional change | 96 chains; 188 scan-in / scan-out connections re-ordered | DFT-0226: tester vector memory depth | Full 14-view MCMM STA: no new violations, incl. scan_shift and scan_capture views (trace-funnel D-pin paths per KST-DFT-EXC TE-DFT-014 unchanged); LEC (scan disabled) pass; ATPG re-run; LVS/DRC clean | Samir Haddad |
| ECO-A-005 | 2026-07-31 | netlist ECO | CPU (u_cpu/u_plic) | PLIC interrupt priority registers reset value 1 -> 0 (all sources disabled at reset; boot firmware enables) | u_cpu/u_plic: 31 flops (bit 0 of each 4-bit priority register, sources 1..31; source 0 reserved) re-typed from set to reset | SW-0077 (boot firmware request) | Full 14-view MCMM STA clean; LEC pass; LVS/DRC clean; boot regression pass | Daniel Achterberg |
| ECO-A-006 | 2026-08-03 | netlist ECO | GBUF (u_gbuf/u_bank_arb) | Bank-conflict arbiter: round-robin pointer now advances on grant instead of on request; removes starvation under 4-way bank conflicts | u_gbuf/u_bank_arb: 61 cells changed | GBUF-0133 (P2) | Full 14-view MCMM STA clean; LEC pass; LVS/DRC clean; GBUF stress regression pass | Daniel Achterberg |
| ECO-A-007 | 2026-08-06 | netlist ECO | Top level (all partitions) | Spare-cell tie-off: floating inputs of spare cells tied to TIELO/TIEHI per foundry N5-class guidance | 2,418 spare cells; +306 tie cells | PD-0301: ERC floating-input report | Full 14-view MCMM STA clean; DRV clean; ERC/LVS/DRC clean | Daniel Achterberg |
| CHG-B-001 | 2026-08-17 | pad-ring | Package / ball map | NC balls AR44, AT44, AU44, AV44, AW44, AY44 re-labelled TP_0..TP_5, documentation only; no electrical change | None (ball map text only) | TRR-1 AI-07; test-engineering request for ATE socket continuity-check pads | Ball map vs pad-ring netlist cross-check: 0 unassigned signals; no layout change | Rachel Lindqvist |
| CHG-B-002 | 2026-08-18 | pad-ring | Pad ring (GPIO_B bank) | GPIO_B cells IO_GPIO_1V2 -> IO_GPIO_1V8, VDDIO_B 1.2 V -> 1.8 V, 16 pad-ring cells, per KST-ARCH-001; board rail moved to separate VDDIO_1V8_B; ball map unchanged | u_padring/u_gpio_b_io_0..u_gpio_b_io_15 (16 x IO_GPIO_1V8); V18 supply-select tied to 1 on all 16 cells; IO_PVDDIO_DV supply/rail-clamp and IO_POC_DV cells unchanged (dual-voltage, KST-PKG-002 section 3.1) | TRR-1 readiness gate finding (AI-04); CHK-SPEC-03 | Pad-ring DRC/LVS/ERC clean; ESD/latch-up re-check clean; QSPI0 I/O timing at 133 MHz met; full 14-view MCMM STA clean | Rachel Lindqvist |
| ECO-B-001 | 2026-08-19 | netlist ECO | NOC (u_noc/u_rtr_2_1) | NoC router (2,1) credit-return glitch: credit-return valid on the west port now registered, removing a glitch when VC2 and VC3 return credits in the same cycle | u_noc/u_rtr_2_1/u_port_w: +9 DFF, 14 comb cells | NOC-0271 (P2) | Full 14-view MCMM STA clean; LEC pass; LVS/DRC clean; NoC regression pass | Daniel Achterberg |
| ECO-B-002 | 2026-08-20 | netlist ECO | NPU (u_npu_c0..u_npu_c3/u_dma) | NPU DMA completion interrupt coalescing: coalescing counter now cleared on channel reset (a stale count delayed the first completion interrupt after reset) | u_npu_c0..u_npu_c3/u_dma/u_irq_coal: 27 cells changed per cluster | NPU-2248 (P2) | Full 14-view MCMM STA clean; LEC pass; LVS/DRC clean; NPU DMA regression pass | Viktor Halloran / Daniel Achterberg |
| ECO-B-003 | 2026-08-28 | netlist ECO | SEC (u_sec_encl/u_keyldr) | 2 x DLY2_X1 (eco_b003_dly_0, eco_b003_dly_1) inserted at D pin of u_sec_encl/u_keyldr/root_key_q_reg_37_ to fix hold (+0.015 ns at func_ff_0p825v_m40c_cbest_ccbest after ECO) | u_sec_encl/u_keyldr/eco_b003_dly_0, u_sec_encl/u_keyldr/eco_b003_dly_1 (2 x DLY2_X1) | TRR-1 readiness gate finding (AI-04); OTP key-load path hold; CHK-STA-02; W-017 withdrawn | incremental STA, hold views only (func_ff_0p825v_m40c_cbest_ccbest, func_ff_0p825v_m40c_rcbest) - clean; LVS/DRC clean; superseded: delay cells removed by ECO-C-002, re-verified on full 14-view MCMM runs sta_kst_0911_c002 and sta_kst_0922_full (section 7) | Daniel Achterberg / Jonah Pike |
| ECO-B-004 | 2026-08-24 | IP drop | MEM (u_ddr_ss) | IP drop MC-LP5X v2.6.1 -> v2.7.0 and PHY-LP5X-N5 v2.6.1 -> v2.7.0; controller and PHY upgraded together as required by the vendor | u_ddr_ss/u_mc0..u_mc3: incremental re-synthesis limited to the training sequencer, the controller/PHY training interface and the link-ECC error counter (LPX-1182, LPX-1171; < 1% of controller cells changed, ECO-legalized placement); u_ddr_ss/u_phy0..u_phy3 hard macro GDS/LEF/LIB v2.7.0 swapped in place (identical LEF footprint, pins and bumps) | LPX-1182 / ALX4100-E07 (errata review, TRR-1 AI-04); CHK-IP-03 | Full 14-view MCMM STA clean; LVS/DRC clean; vendor integration test suite pass; LPDDR5X subsystem regression pass; IP hash check pass | Beatriz Solano / Anjali Deshmukh |
| ECO-B-005 | 2026-08-25 | netlist ECO | PMUIF / AON (u_core/u_pmu_if) | Pulse synchronizer u_core/u_pmu_if/u_wake_psync on pmu_wake_req: toggle + 3-FF + edge detect; replaces the direct capture into wake_pending_q | u_core/u_pmu_if/u_wake_psync: toggle flop (aon_clk), 3-FF synchronizer + edge detect (core_clk), ack-toggle return (2-FF, aon_clk) and busy status (3-FF, core_clk); 12 DFF + 6 comb cells | TRR-1 readiness gate finding (AI-04); CHK-CDC-04; CDC-0147; W-CDC-022 withdrawn | Full 14-view MCMM STA clean; CDC re-run clean (1,286 crossings, 0 unwaived); LEC pass; LVS/DRC clean; PMU wake regression pass in ACTIVE and LP-IDLE with the /64 divider enabled (+crg_fast_lp off) | Daniel Achterberg / Kofi Mensah |
| ECO-B-006 | 2026-08-26 | netlist ECO | PERIPH (u_periph/u_i2c0) | I2C0 glitch-filter reset default changed from 0 to 50 ns (10 periph_clk cycles) per SMBus spike-suppression requirement | u_periph/u_i2c0: 2 flops (bits 1 and 3 of the 4-bit filter-length field) re-typed from reset to set | I2C-0057 (SMBus spike-suppression compliance review) | Full 14-view MCMM STA clean; LEC pass; LVS/DRC clean; I2C regression pass | Daniel Achterberg |
| TB-B-001 | 2026-08-21 | testbench | PCIE0 verification environment | Verification only: 14 new L1.2 directed sequences + constrained-random L1SS sequence library; no netlist change | n/a (testbench) | TRR-1 AI-01 / AI-02; cg_pcie0_l12_entry_exit closure | Nightly regression 99.6%; L1.2 covergroup 71.0% -> 91.1% | Tomasz Wierzbicki / Leo Brandt |
| ECO-C-001 | 2026-09-08 | netlist ECO | PERIPH (u_periph) | Spare-cell tie-off cleanup in u_periph: 37 spare cells whose inputs were left on long shared TIELO/TIEHI nets (up to about 180 um) after the ECO-B-006 legalization re-tied to local tie cells per KST-PD-SPARE rev 2 (no ERC violation before or after) | 37 spare cells; +12 tie cells | PD-0318: spare-cell tie-net length/fanout audit on kst_top_nl_2026.08.31 | Full 14-view MCMM STA clean; DRV clean; ERC/LVS/DRC clean | Daniel Achterberg |
| ECO-C-002 | 2026-09-10 | netlist ECO | SEC (u_sec_encl/u_keyldr) | Security key-load path re-balanced: removed eco_b003_dly_0/1 from the shared D-pin segment of root_key_q_reg_37_; inserted 1 x DLY4_X1 eco_c002_dly_0 at u_sec_encl/u_keyldr/ecc_bypass_mux_37/I1 (ECC-bypass leg: hold-critical, > 1.5 ns setup margin); max path through u_secded untouched | -2 x DLY2_X1 (u_sec_encl/u_keyldr/eco_b003_dly_0, eco_b003_dly_1); +1 x DLY4_X1 (u_sec_encl/u_keyldr/eco_c002_dly_0) | Package B readiness gate review (TRR-2 AI-15): ECO-B-003 cells on the shared segment reduced setup on root_key_q_reg_37_ to -0.037 ns (func_ss_0p675v_m40c_cworst_ccworst) and -0.012 ns (func_ss_0p675v_125c_cworst_ccworst) on kst_top_nl_2026.08.31; CHK-STA-01, CHK-GOV-02 | Full 14-view MCMM STA (SI + POCV): root_key_q_reg_37_ setup +0.064 ns (func_ss_0p675v_m40c_cworst_ccworst), +0.082 ns (func_ss_0p675v_125c_cworst_ccworst), hold +0.013 ns (func_ff_0p825v_m40c_cbest_ccbest); LEC pass; LVS/DRC clean; secure-boot GLS min/max SDF pass | Daniel Achterberg / Jonah Pike |
| ECO-C-003 | 2026-09-15 | netlist ECO (RTL) | PCIE0 (u_pcie0_wrap/u_l1ss_ctl) | PCIE-1187 fix: the CLKREQ# re-assert branch of the u_pcie0_wrap/u_l1ss_ctl exit FSM restarted T_POWER_ON without clearing tpoweron_done, so a stale done flag released the PHY from P1.2 before REFCLK was valid; exit sub-FSM re-encoded to clear tpoweron_done on CLKREQ# re-assertion and to re-qualify every P1.2 exit branch with synchronized refclk_valid | u_pcie0_wrap/u_l1ss_ctl re-synthesized: +38 DFF incl. 11-bit refclk-settle timer, ~410 comb cells (about 640 gate-array-site equivalents; the pcie_aux_clk island holds 6 spare flops and about 90 gate-array filler sites, so the fix exceeds metal-only capacity, ALD-QA-CHK-007 section 4.2); l1ss_ctl v3.0 -> v3.0.1 | PCIE-1187 (P1), found 2026-09-10 by TB-C-001 test l12_clkreq_tpoweron_gen5 (ALX4100-E03 scenario at Gen5) | RTL regression clean; L1.2 directed and constrained-random L1SS suites pass; LEC pass; full 14-view MCMM STA clean; CDC/RDC re-run clean; GLS PCIe L1.2 entry/exit incl. CLKREQ# re-assert during T_POWER_ON, min/max SDF pass; 38 new flops stitched into the pcie_aux scan chain, ATPG re-run on kst_top_nl_2026.09.19 (atpg_kst_0923, pattern set v1.0); LVS/DRC clean | Leo Brandt / Daniel Achterberg |
| TB-C-001 | 2026-09-09 | testbench | PCIE0 verification environment | Verification only: L1.2 coverage closure tests incl. l12_clkreq_tpoweron_gen5 (CLKREQ# re-assertion during T_POWER_ON at Gen5, offset swept in 250 ns steps) and PIPE PHY BFM Gen5 P1.2 exit-latency update; l1ss_cr_lib extended to Gen1..Gen5; no netlist change | n/a (testbench) | TRR-2 AI-12 / AI-13; cg_pcie0_l12_entry_exit closure to the Tier-1 target | Nightly regression 99.8%; L1.2 covergroup 91.1% -> 96.8% (120/124); exposed PCIE-1187 | Tomasz Wierzbicki / Leo Brandt |

## 3. Per-change sign-off run record

| ID | STA run tag | STA views | STA run date | CDC/RDC re-run | LEC | DRC/LVS run date |
|---|---|---|---|---|---|---|
| ECO-A-001 | sta_kst_0721_a001 | 14/14 (MCMM) | 2026-07-21 | Yes (NoC partition) | Pass | 2026-07-21 |
| ECO-A-002 | sta_kst_0724_a002 | 14/14 (MCMM) | 2026-07-24 | Not required (single clock domain) | Pass | 2026-07-24 |
| ECO-A-003 | sta_kst_0726_a003 | 14/14 (MCMM) | 2026-07-26 | Yes (GBUF partition) | Pass | 2026-07-26 |
| ECO-A-004 | sta_kst_0729_a004 | 14/14 (MCMM) | 2026-07-29 | Not required (scan stitching only) | Pass (scan disabled) | 2026-07-29 |
| ECO-A-005 | sta_kst_0801_a005 | 14/14 (MCMM) | 2026-08-01 | Yes (CPU partition, RDC) | Pass | 2026-08-01 |
| ECO-A-006 | sta_kst_0804_a006 | 14/14 (MCMM) | 2026-08-04 | Not required (single clock domain) | Pass | 2026-08-04 |
| ECO-A-007 | sta_kst_0807_a007 | 14/14 (MCMM) | 2026-08-07 | Not required (tie-off only) | Pass | 2026-08-07 |
| CHG-B-001 | n/a (documentation only) | - | - | Not required | Not required | Not required |
| CHG-B-002 | sta_kst_0819_chg002 | 14/14 (MCMM) + I/O timing | 2026-08-19 | Not required (pad ring only) | Pass | 2026-08-19 |
| ECO-B-001 | sta_kst_0820_b001 | 14/14 (MCMM) | 2026-08-20 | Not required (single clock domain) | Pass | 2026-08-20 |
| ECO-B-002 | sta_kst_0821_b002 | 14/14 (MCMM) | 2026-08-21 | Yes (NPU partition) | Pass | 2026-08-21 |
| ECO-B-004 | sta_kst_0825_b004 | 14/14 (MCMM) | 2026-08-25 | Yes (MEM partition) | Pass | 2026-08-25 |
| ECO-B-005 | sta_kst_0826_b005 | 14/14 (MCMM) | 2026-08-26 | Yes (full-chip CDC/RDC) | Pass | 2026-08-26 |
| ECO-B-006 | sta_kst_0827_b006 | 14/14 (MCMM) | 2026-08-27 | Not required (single clock domain) | Pass | 2026-08-27 |
| ECO-B-003 | sta_kst_0828_b003_inc | 2/14 (incremental, hold); superseded by ECO-C-002 (14/14) | 2026-08-28 | Not required | Pass | 2026-08-29 |
| TB-B-001 | n/a (testbench) | - | - | Not required | Not required | Not required |
| ECO-C-001 | sta_kst_0909_c001 | 14/14 (MCMM) | 2026-09-09 | Not required (tie-off only) | Pass | 2026-09-09 |
| ECO-C-002 | sta_kst_0911_c002 | 14/14 (MCMM) | 2026-09-11 | Not required (single clock domain) | Pass | 2026-09-11 |
| TB-C-001 | n/a (testbench) | - | - | Not required | Not required | Not required |
| ECO-C-003 | sta_kst_0916_c003 | 14/14 (MCMM) | 2026-09-16 | Yes (full-chip CDC/RDC) | Pass | 2026-09-16 |

All runs use the sign-off STA tool with SI and POCV enabled and the CHK-STA-07 uncertainty settings. Results are recorded against the waivers in KST-STA-021 at the time of the run.

Gate-level simulation for the affected blocks is recorded per netlist release, not per change: see KST-COV-011 section 10 for the suite, its netlist and its run dates.

## 4. ECO board decisions on requests not implemented

| Request | Date raised | Block | Request | Decision | Decided by |
|---|---|---|---|---|---|
| ECR-0412 | 2026-07-22 | DBG (u_npu_top/u_trace_funnel) | Add a pipeline stage on the NPU trace funnel data bus | Deferred to the next base-layer derivative (not required for ALX-5100/ALX-5100I); functional multicycle-4 path meets timing; test-mode scan-shift path handled per KST-DFT-EXC | Viktor Halloran, Samir Haddad |
| ECR-0415 | 2026-07-24 | NOC (u_noc) | Upsize row-3 link repeaters for extra setup margin | Rejected: all NoC paths positive on 14/14 views; +0.4 mW leakage not justified | Daniel Achterberg, Mei-Lin Chou |
| ECR-0419 | 2026-07-29 | NPU (u_npu_c2/u_tile3) | Add a 25th PVT sensor at the tile-3 hot spot | Rejected after RTL freeze; nearest existing sensor is within 180 um | Viktor Halloran |
| ECR-0423 | 2026-08-04 | PERIPH (u_periph/u_uart0) | Change UART0 reset baud divisor | Rejected: handled in boot firmware | Daniel Achterberg |
| ECR-0426 | 2026-08-05 | PCIE1 (u_pcie1_wrap) | Add clock gating on the PCIE1 debug bus | Not required: PD_PCIE1 is power-gated and clamped when FUSE_PCIE1_DIS=1 | Leo Brandt |
| ECR-0431 | 2026-08-17 | Board / GPIO_B | Keep the pad ring and add board level-shifters on the QSPI0 and SPI1 signals | Rejected: translator delay (about 9 ns round trip) breaks QSPI0 read timing at 133 MHz and exceeds the 5.0 ns sub-cycle read-capture delay line; CHG-B-002 chosen | Rachel Lindqvist, Priya Raghavan |
| ECR-0432 | 2026-08-17 | Board / GPIO_B | Keep the pad ring and move the boot flash to a 1.2 V NOR, or boot via PCIe host-load | Rejected: no 1.2 V 512 Mbit NOR on the AVL is qualified to Tj -40 C; the SPI1 telemetry sensor is 1.8 V-only; PCIe host-load is disabled by OTP in PRODUCTION (KST-ARCH-001 sections 13.2/13.3, BOOT-01; KST-PKG-002 section 8); CHG-B-002 chosen | Rachel Lindqvist, Priya Raghavan |
| ECR-0433 | 2026-08-18 | MEM (u_ddr_ss) | Stay on the 2.6.x line and restrict cold boot to Tj >= 0 C | Rejected: ALX-5100I must cold-boot at Tj -40 C; ECO-B-004 chosen | Anjali Deshmukh, Beatriz Solano |
| ECR-0435 | 2026-08-19 | AON / PMUIF | Re-qualify W-CDC-022 with an additional stability assertion | Rejected: a single-cycle pulse cannot be waived as quasi-static (CHK-CDC-04); ECO-B-005 chosen | Hiroshi Tanabe, Kofi Mensah |
| ECR-0441 | 2026-09-08 | SEC (u_sec_encl) | Relax sec_clk from 500 MHz to 475 MHz to recover setup margin on the key-load path | Rejected: sec_clk = PLL_CORE/2 is fixed at 500.0 MHz by KST-ARCH-001 section 5.8 (no derating or DVFS); 475 MHz would require re-planning PLL_CORE, which also sources core_clk; ECO-C-002 chosen | Ines Carvalho, Mei-Lin Chou |
| ECR-0444 | 2026-09-12 | PCIE0 (u_pcie0_wrap) | Add a firmware-selectable L1.2 disable chicken bit alongside ECO-C-003 | Deferred to A0 validation; ECO-C-003 fixes the sequencing and ASPM L1.2 can already be disabled through the standard L1 PM Substates control register; disabling L1.2 is a debug fallback only and violates PWR-IDLE-01 (KST-ARCH-001 section 8.3) | Leo Brandt, Priya Raghavan |

## 5. Netlist releases

| Netlist | Date | Contents | Sign-off |
|---|---|---|---|
| kst_top_nl_2026.07.17 | 2026-07-17 | Synthesis of RTL tag kst_rtl_2026.07.15 | Pre-ECO baseline |
| kst_top_nl_2026.08.07 | 2026-08-07 | kst_top_nl_2026.07.17 + ECO-A-001..ECO-A-007 | Package A: full 14-view MCMM STA, CDC/RDC, LEC and DRC/LVS re-run dated 2026-08-08 to 2026-08-12 |
| kst_top_nl_2026.08.31 | 2026-08-31 | kst_top_nl_2026.08.07 + CHG-B-002 (pad ring) + ECO-B-001..ECO-B-006 (incl. IP drop ECO-B-004) | Package B: results in KST-STA-020 rev B, KST-CDC-030 rev B, KST-PI-040 rev B and KST-TRK-061 rev B |
| kst_top_nl_2026.09.19 | 2026-09-19 | kst_top_nl_2026.08.31 + ECO-C-001..ECO-C-003 | Package C (final): full re-sign-off dated 2026-09-20 to 2026-09-23, see section 7 |

## 6. ECO resources

| Resource | Status after package C |
|---|---|
| Spare / gate-array ECO filler density | 1.5% retained (0 consumed by package A, B and C ECOs) |
| Spare flops per partition | 0.4% of partition flop count, distributed on a 60 um grid |
| Always-on island pcie_aux_clk (u_pcie0_wrap/u_l1ss_ctl, PHY power-state control) | 6 spare flops and about 90 gate-array filler sites (island area-limited; below the partition average) |
| Metal-only ECO scope | Pre-placed spare cells (DFF, DLY2/DLY4, NAND/NOR/MUX) rewired from V1/M2 up; gate-array ECO fillers personalized from V0/M0-M1 up; a metal-only ECO re-cuts the via and metal masks from the lowest layer it touches up to about M8 (about 16-24 masks including several EUV layers); FEOL and MOL masks are reused (ALD-QA-CHK-007 section 4.2) |

## 7. Final re-sign-off

Final re-sign-off: full 14-view MCMM STA, CDC/RDC, GLS, DRC/LVS, ATPG/MBIST on kst_top_nl_2026.09.19 dated 2026-09-20..23 (CHK-GOV-02).

| Check | Tool | Scope | Run date | Result |
|---|---|---|---|---|
| Formal equivalence (LEC) | Equivalence checker | RTL tag vs kst_top_nl_2026.09.19 | 2026-09-20 | Equivalent |
| STA, full 14-view MCMM (SI + POCV) | Sign-off STA tool | 9 func, 2 scan_shift, 2 scan_capture, 1 mbist views | 2026-09-22 | Setup and hold positive on all functional views; test-mode items covered by complete waivers (KST-STA-021 rev C) |
| DRV (max transition / max capacitance) | Sign-off STA tool | Full chip | 2026-09-22 | 0 unwaived |
| CDC / RDC | Structural CDC tool + formal CDC/RDC tool | Full chip, 1,286 crossings | 2026-09-20..21 | 0 unwaived (1,244 clean, 42 waived) |
| GLS (SDF min and max) | Logic simulator | Boot, reset, low-power entry/exit, PCIe L1.2 entry/exit | 2026-09-20..21 | All tests pass |
| IR drop / EM | IR/EM sign-off tool | VDD_CORE, VDD_NPU, VDD_SRAM, VDD_AON | 2026-09-22 | All rails within budget; EM 0 violations |
| DRC incl. density, LVS, ERC, antenna | Physical verification tool, foundry N5-class sign-off deck | Final GDS | 2026-09-23 | 0 violations |
| ESD / latch-up | Physical verification tool | Pad ring, core and all hard-macro pads | 2026-09-23 | 0 violations |
| ATPG stuck-at / transition | ATPG tool | kst_top_nl_2026.09.19, pattern set v1.0 | 2026-09-23 | 99.2% / 96.1% |
| MBIST | MBIST tool + logic simulator | 3,412 SRAM instances | 2026-09-23 | 0 failures |

All runs are dated after the last netlist change (ECO-C-003, merged 2026-09-15; netlist released 2026-09-19).

## 8. Open change requests

None at package C freeze (2026-09-24). No further ECO window is planned before GDSII handoff on 2026-10-30; any change requires chair approval and a full re-sign-off per CHK-GOV-02.

## 9. Revision history

| Rev | Date | Changes |
|---|---|---|
| A | 2026-08-13 | ECO-A-001..ECO-A-007; netlist kst_top_nl_2026.08.07 for TRR-1 |
| B | 2026-09-03 | Added CHG-B-001, CHG-B-002, ECO-B-001..ECO-B-006 and TB-B-001 (ECO window 2026-08-17 to 2026-08-30); ECR-0431, ECR-0432, ECR-0433, ECR-0435 decisions; netlist kst_top_nl_2026.08.31 for TRR-2 |
| C | 2026-09-24 | Added ECO-C-001..ECO-C-003 and TB-C-001 (ECO window 2026-09-07 to 2026-09-18); ECR-0441, ECR-0444 decisions; netlist kst_top_nl_2026.09.19; final re-sign-off section added for TRR-3 |
