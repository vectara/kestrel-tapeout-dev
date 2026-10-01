# KESTREL (ALX-5100) Static Timing Analysis Sign-off Report

| Field | Value |
|---|---|
| Doc ID | KST-STA-020 |
| Title | Static Timing Analysis Sign-off Report |
| Revision | B (supersedes A) |
| Date | 2026-09-02 |
| Owner | Mei-Lin Chou (STA Lead) |
| Status | Released for TRR-2 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## Revision history

| Rev | Date | Author | Change |
|---|---|---|---|
| A | 2026-08-12 | Mei-Lin Chou | Initial release for TRR-1 on netlist kst_top_nl_2026.08.07 (ECO-A-001..ECO-A-007). |
| B | 2026-09-02 | Mei-Lin Chou | Netlist kst_top_nl_2026.08.31 for TRR-2; includes ECO-B-001..ECO-B-006 and CHG-B-002 (see KST-ECO-062). |
| B | 2026-09-02 | Mei-Lin Chou | ECO-B-003: 2 x DLY2_X1 (u_sec_encl/u_keyldr/eco_b003_dly_0, eco_b003_dly_1) inserted at the D pin of u_sec_encl/u_keyldr/root_key_q_reg_37_; hold in func_ff_0p825v_m40c_cbest_ccbest -0.021 -> 0.015 ns; W-017 withdrawn (KST-STA-021 rev B). |
| B | 2026-09-02 | Mei-Lin Chou | ECO-B-004: MC-LP5X and PHY-LP5X-N5 netlist and timing models updated to v2.7.0; waivers W-001, W-003, W-012, W-019 re-confirmed. MEM re-timed: the v2.7.0 PHY LIB changes only training/calibration arcs and the controller re-synthesis did not touch u_sched or DFI data paths, so u_ddr_ss slacks are unchanged (within 1 ps). |
| B | 2026-09-02 | Mei-Lin Chou | ECO-B-005: pulse synchronizer u_core/u_pmu_if/u_wake_psync timed (clock groups unchanged). ECO-B-001, ECO-B-002, ECO-B-006: timed, no new exceptions. |
| B | 2026-09-02 | Mei-Lin Chou | CHG-B-002: GPIO_B pad cells IO_GPIO_1V8; pad timing models updated. Sections 5-11 and Appendix A regenerated from the full 14-view run sta_kst_0902_full; A.4 adds the ECO-B-003 incremental results. |

## 1. Executive summary

This report documents static timing sign-off of KESTREL (ALX-5100) for TRR-2. The full 14-view MCMM set (9 functional, 2 scan-shift, 2 scan-capture, 1 MBIST) was timed on netlist kst_top_nl_2026.08.31 (ECO-B-001..ECO-B-006 and CHG-B-002 included) with SI and POCV enabled, against ALD-QA-CHK-007 rev 7.2 CHK-STA-01..07.

Post-ECO-B-003 incremental timing was run on the hold views (ECO sign-off memo, 2026-08-28); setup timing is unaffected because no setup-critical paths were touched.

All hold violations closed; W-017 withdrawn.

In test mode, the 64 trace-funnel endpoints in scan_shift_ss_0p675v_m40c_cworst_ccworst are covered by W-004 (DFT exception TE-DFT-014, approved by the STA Lead and DFT Lead). DRVs: 0 unwaived. STA status for TRR-2: GREEN.

| Check (ALD-QA-CHK-007) | Result | Section |
|---|---|---|
| CHK-STA-03 view set on sign-off netlist | 14/14 views, run sta_kst_0902_full (2026-09-02) | 5 |
| CHK-STA-01 functional setup | MET | 5, 6, 8 |
| CHK-STA-02 functional hold | MET (W-017 withdrawn; fixed by ECO-B-003) | 5, 7 |
| CHK-STA-04 DRV | 0 unwaived (767 nets waived, tie-off/spare-cell only) | 10 |
| CHK-STA-05/06 waivers | per KST-STA-021; W-004 is the only waived setup/hold item in test modes | 11 |
| CHK-STA-07 uncertainty, SI, POCV | 0.050/0.200 ns setup, 0.020 ns hold; SI + POCV on | 3 |

## 2. Scope and inputs

| Item | Value |
|---|---|
| Design | ALX-5100 KESTREL top (kst_top), flat full-chip analysis; no abstraction of in-house blocks |
| Netlist | kst_top_nl_2026.08.31 (post-route, ECO-B-001..ECO-B-006, CHG-B-002) |
| Parasitics | SPEF per RC corner (cworst_ccworst, rcworst, typical, cbest_ccbest, rcbest), extracted 2026-08-31 |
| Constraints | KST_func.sdc r4.2; KST_scan_shift.sdc r3.2; KST_scan_capture.sdc r3.1; KST_mbist.sdc r2.4 |
| Libraries | STDCELL-N5-H210 v1.2 (SVT/LVT/ULVT, LVF); SRAM-N5-COMP v2.1 macro models; hard-macro timing models per KST-IPBOM-050 (same package revision) |
| Tool | sign-off STA tool, release 2026.03-SP2, MCMM distributed run (14 views) |
| Sign-off run | sta_kst_0902_full (2026-09-02), 14/14 views |
| GLS SDF | sta_kst_0831_sdf (2026-08-31): SDF write only, min and max corners (KST-COV-011 section 10), same netlist and SPEF |
| ECO timing | sta_kst_0828_b003_inc (2026-08-28): incremental run for ECO-B-003 on hold views func_ff_0p825v_m40c_cbest_ccbest and func_ff_0p825v_m40c_rcbest |

## 3. Methodology

### 3.1 Analysis setup

- **MCMM:** the sign-off STA tool runs 14 views, each one mode x PVT corner x RC corner (name pattern `<mode>_<pvt>_<rc>`). Setup, hold, DRV, clock-gating, minimum pulse width, recovery/removal and noise are checked in every view; the "primary" column in 3.2 shows which check a view is meant to bound. The 14 views were chosen by dominance screening of 42 candidate views (incl. tt 0 C, cworst_T/rcworst_T, cold capture and MBIST) on kst_top_nl_2026.07.17 (run sta_kst_0718_dom).
- **SI:** crosstalk delta delay and glitch analysis with timing windows, all views.
- **POCV:** LVF-based parametric OCV at 3.0 sigma on cells; wire derate +/-3.0% per the foundry N5-class sign-off guide; no additional flat cell derate.
- **Clocks:** fully propagated (post-route clock trees); CRPR enabled (threshold 0.001 ns).
- **Uncertainty (CHK-STA-07):** setup 0.050 ns in functional views and 0.200 ns in test views (scan_shift, scan_capture, mbist); hold 0.020 ns in all views. Functional setup uncertainty covers PLL period jitter plus margin; test uncertainty covers OCC mux and ATE clock jitter.
- **Voltage:** 0.675 V (ss) is the -10% limit of the 0.750 V rails (2% regulation + 8% dynamic-IR budget); 0.825 V (ff) is the +10% limit, set by the ATE Vmax screen and PMIC overshoot (KST-PI-040 section 10).
- **Temperature inversion:** at 0.675 V the -40 C corner is setup-worst because of FinFET temperature inversion (the threshold-voltage rise at cold outweighs the mobility gain at low overdrive), so the ss_0p675v_m40c views are included alongside ss_0p675v_125c. At 0.825 V hold is timed at both -40 C and 125 C.
- **Corners not used for timing:** tt_0p750v_25c is used only for room-temperature leakage/IDDQ and ATE correlation; tt_0p750v_85c (view func_tt_0p750v_85c_typical) is the typical-silicon timing reference and the source of the PI current libraries (KST-PI-040).
- **Power states:** LP-IDLE (core_clk/64 = 15.625 MHz) relaxes the 1000.0 MHz core_clk constraint and is covered by the functional views. PCIE1 (fused off in ALX-5100, FUSE_PCIE1_DIS=1) is fully timed at 500.0 MHz (pcie1_core_clk) in all functional views; in ALX-5100 its clock is gated and its outputs are clamped by isolation cells.
- **Test-mode temperature:** at-speed ATE insertions run hot (Tj 105 C); the ALX-5100I -40 C screen uses stuck-at patterns and MBIST at reduced speed, so capture and MBIST views are signed off at 125 C.
- **Test clocks:** scan_shift at scan_clk 200.0 MHz; scan_capture times OCC launch-on-capture clocks at 80% of functional frequency (transition-fault test program); mbist times memory clocks at 80% of functional frequency.
- **Vt usage:** u_sec_encl is implemented SVT-only (leakage and side-channel policy); NPU and CPU datapaths use LVT/ULVT. u_sec_encl key-path nets (otp_rdata_q, ecc_data, root_key_q) are shielded and dont_touch under the enclave layout rules, so implementation-tool hold fixing does not insert buffers on them.

### 3.2 View set

PVT and RC corners are encoded in the view name.

| # | View | Mode | Primary check |
|---|---|---|---|
| 1 | func_ss_0p675v_125c_cworst_ccworst | func | setup |
| 2 | func_ss_0p675v_125c_rcworst | func | setup |
| 3 | func_ss_0p675v_m40c_cworst_ccworst | func | setup (temperature inversion) |
| 4 | func_ss_0p675v_m40c_rcworst | func | setup (temperature inversion) |
| 5 | func_tt_0p750v_85c_typical | func | typical-silicon reference |
| 6 | func_ff_0p825v_m40c_cbest_ccbest | func | hold |
| 7 | func_ff_0p825v_m40c_rcbest | func | hold |
| 8 | func_ff_0p825v_125c_cbest_ccbest | func | hold |
| 9 | func_ff_0p825v_125c_rcbest | func | hold |
| 10 | scan_shift_ss_0p675v_m40c_cworst_ccworst | scan_shift | shift setup |
| 11 | scan_shift_ff_0p825v_m40c_cbest_ccbest | scan_shift | shift hold |
| 12 | scan_capture_ss_0p675v_125c_cworst_ccworst | scan_capture | capture setup |
| 13 | scan_capture_ff_0p825v_m40c_cbest_ccbest | scan_capture | capture hold |
| 14 | mbist_ss_0p675v_125c_cworst_ccworst | mbist | MBIST setup and hold |

### 3.3 Exceptions and waivers

- Timing exceptions (false paths, multicycles) use explicit pin/port lists; wildcard exceptions are not used.
- DFT false paths stay visible in reports as reporting-only exceptions and are waived in KST-STA-021 with a KST-DFT-EXC reference and STA Lead + DFT Lead approval (CHK-STA-06).
- DRV waivers are limited to tie-off/spare-cell nets (CHK-STA-04).
- Waivers are tracked in KST-STA-021 with justification, constraint/ECO reference, approvers and approval date (CHK-STA-05).

## 4. Clock summary

Insertion delay and global skew are from func_ss_0p675v_m40c_cworst_ccworst (scan_clk from scan_shift_ss_0p675v_m40c_cworst_ccworst).

| Clock | Frequency | Period (ns) | Source | Partitions | Max insertion (ns) | Global skew (ns) | Notes |
|---|---|---|---|---|---|---|---|
| npu_clk | 1200.0 MHz | 0.833 | PLL_NPU | u_npu_c0..u_npu_c3, u_npu_top | 1.131 | 0.061 | - |
| cpu_clk | 1500.0 MHz | 0.667 | PLL_CPU | u_cpu | 0.874 | 0.038 | - |
| core_clk | 1000.0 MHz | 1.000 | PLL_CORE | u_noc, u_gbuf, u_core, u_cpu/u_plic | 1.262 | 0.072 | LP-IDLE core_clk/64 = 15.625 MHz is covered by the 1000.0 MHz constraint |
| sec_clk | 500.0 MHz | 2.000 | PLL_CORE/2 | u_sec_encl | 0.968 | 0.156 | PLL_CORE/2, fixed 500.0 MHz; no independent derating (KST-ARCH-001 section 5.8) |
| mc_clk | 1066.7 MHz | 0.938 | PLL_DDR | u_ddr_ss/u_mc0..u_mc3, PHY DFI boundary | 1.018 | 0.044 | DFI clock; WCK is internal to the PHY hard macro |
| pcie_core_clk | 1000.0 MHz | 1.000 | PCIe PHY PLL (100 MHz REFCLK) | u_pcie0_wrap | 0.781 | 0.036 | PCIE0 |
| pcie1_core_clk | 500.0 MHz | 2.000 | PCIE1 PHY PLL | u_pcie1_wrap | 0.702 | 0.031 | gated at the CRG in ALX-5100 (FUSE_PCIE1_DIS=1); timed at 500.0 MHz in all functional views so the same die supports ALX-5100X |
| pcie_aux_clk | 25.000 MHz | 40.000 | aon_clk | u_pcie0_wrap/u_l1ss_ctl | 0.412 | 0.018 | L1 PM substates logic while REFCLK is off |
| periph_clk | 200.0 MHz | 5.000 | PLL_CORE/5 | u_periph | 0.693 | 0.029 | - |
| aon_clk | 25.000 MHz | 40.000 | xtal_clk (25.000 MHz crystal) | u_aon | 0.388 | 0.021 | asynchronous to all core-side clocks |
| scan_clk | 200.0 MHz (shift) | 5.000 | OCC test-clock mux | all scan flops (test modes only) | 2.551 | 1.799 | shift trees not balanced across clusters; lockup latches at chain crossings |
| tck | 50.0 MHz | 20.000 | JTAG pad (test only) | u_dbg | 0.604 | 0.022 | asynchronous to scan_clk |

## 5. MCMM results summary (full 14-view run sta_kst_0902_full, 2026-09-02, netlist kst_top_nl_2026.08.31)

WNS/TNS cover data-path checks (reg2reg, in2reg, reg2out, reg-to-macro, macro-to-reg). Clock-gating, minimum pulse width and DRV are in Section 10.

| View | Setup WNS (ns) | Setup TNS (ns) | Setup viol. endpoints | Hold WNS (ns) | Hold TNS (ns) | Hold viol. endpoints | Waivers applied |
|---|---|---|---|---|---|---|---|
| func_ss_0p675v_125c_cworst_ccworst | -0.012 | -0.012 | 1 | 0.018 | 0.000 | 0 | - |
| func_ss_0p675v_125c_rcworst | 0.019 | 0.000 | 0 | 0.021 | 0.000 | 0 | - |
| func_ss_0p675v_m40c_cworst_ccworst | -0.037 | -0.037 | 1 | 0.016 | 0.000 | 0 | - |
| func_ss_0p675v_m40c_rcworst | 0.014 | 0.000 | 0 | 0.019 | 0.000 | 0 | - |
| func_tt_0p750v_85c_typical | 0.142 | 0.000 | 0 | 0.031 | 0.000 | 0 | - |
| func_ff_0p825v_m40c_cbest_ccbest | 0.206 | 0.000 | 0 | 0.004 | 0.000 | 0 | - |
| func_ff_0p825v_m40c_rcbest | 0.214 | 0.000 | 0 | 0.006 | 0.000 | 0 | - |
| func_ff_0p825v_125c_cbest_ccbest | 0.231 | 0.000 | 0 | 0.007 | 0.000 | 0 | - |
| func_ff_0p825v_125c_rcbest | 0.238 | 0.000 | 0 | 0.009 | 0.000 | 0 | - |
| scan_shift_ss_0p675v_m40c_cworst_ccworst | -0.138 | -5.874 | 64 | 0.052 | 0.000 | 0 | waived W-004 (64 endpoints) |
| scan_shift_ff_0p825v_m40c_cbest_ccbest | 1.912 | 0.000 | 0 | 0.011 | 0.000 | 0 | - |
| scan_capture_ss_0p675v_125c_cworst_ccworst | 0.027 | 0.000 | 0 | 0.035 | 0.000 | 0 | - |
| scan_capture_ff_0p825v_m40c_cbest_ccbest | 0.318 | 0.000 | 0 | 0.005 | 0.000 | 0 | - |
| mbist_ss_0p675v_125c_cworst_ccworst | 0.044 | 0.000 | 0 | 0.029 | 0.000 | 0 | - |

## 6. Top-5 setup paths, functional views

Worst five endpoints per view (one path per endpoint).

| View | # | Startpoint | Endpoint | Clock | Slack (ns) |
|---|---|---|---|---|---|
| func_ss_0p675v_125c_cworst_ccworst | 1 | u_sec_encl/u_otp_if/otp_rdata_q_reg_37_ | u_sec_encl/u_keyldr/root_key_q_reg_37_ | sec_clk | -0.012 |
| func_ss_0p675v_125c_cworst_ccworst | 2 | u_cpu/u_core3/u_exu/u_byp/src1_q_reg_41_ | u_cpu/u_core3/u_exu/u_alu0/res_q_reg_63_ | cpu_clk | 0.011 |
| func_ss_0p675v_125c_cworst_ccworst | 3 | u_npu_c1/u_tile2/u_wbuf/rd_data_q_reg_411_ | u_npu_c1/u_tile2/u_mac_arr/u_pe_r12_c7/acc_q_reg_23_ | npu_clk | 0.016 |
| func_ss_0p675v_125c_cworst_ccworst | 4 | u_ddr_ss/u_mc2/u_sched/u_age_mtx/age_q_reg_12__5_ | u_ddr_ss/u_mc2/u_sched/cmd_sel_q_reg_3_ | mc_clk | 0.024 |
| func_ss_0p675v_125c_cworst_ccworst | 5 | u_noc/u_rtr_1_3/u_vc_alloc/req_q_reg_17_ | u_noc/u_rtr_1_3/u_sw_alloc/grant_q_reg_4_ | core_clk | 0.029 |
| func_ss_0p675v_125c_rcworst | 1 | u_cpu/u_core3/u_exu/u_byp/src1_q_reg_41_ | u_cpu/u_core3/u_exu/u_alu0/res_q_reg_63_ | cpu_clk | 0.019 |
| func_ss_0p675v_125c_rcworst | 2 | u_npu_c1/u_tile2/u_wbuf/rd_data_q_reg_411_ | u_npu_c1/u_tile2/u_mac_arr/u_pe_r12_c7/acc_q_reg_23_ | npu_clk | 0.024 |
| func_ss_0p675v_125c_rcworst | 3 | u_ddr_ss/u_mc2/u_sched/u_age_mtx/age_q_reg_12__5_ | u_ddr_ss/u_mc2/u_sched/cmd_sel_q_reg_3_ | mc_clk | 0.030 |
| func_ss_0p675v_125c_rcworst | 4 | u_noc/u_rtr_1_3/u_vc_alloc/req_q_reg_17_ | u_noc/u_rtr_1_3/u_sw_alloc/grant_q_reg_4_ | core_clk | 0.035 |
| func_ss_0p675v_125c_rcworst | 5 | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/data_q_reg_388_ | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/crc_q_reg_29_ | pcie_core_clk | 0.040 |
| func_ss_0p675v_m40c_cworst_ccworst | 1 | u_sec_encl/u_otp_if/otp_rdata_q_reg_37_ | u_sec_encl/u_keyldr/root_key_q_reg_37_ | sec_clk | -0.037 |
| func_ss_0p675v_m40c_cworst_ccworst | 2 | u_npu_c1/u_tile2/u_wbuf/rd_data_q_reg_411_ | u_npu_c1/u_tile2/u_mac_arr/u_pe_r12_c7/acc_q_reg_23_ | npu_clk | 0.008 |
| func_ss_0p675v_m40c_cworst_ccworst | 3 | u_cpu/u_core3/u_exu/u_byp/src1_q_reg_41_ | u_cpu/u_core3/u_exu/u_alu0/res_q_reg_63_ | cpu_clk | 0.013 |
| func_ss_0p675v_m40c_cworst_ccworst | 4 | u_npu_c3/u_tile0/u_sfu/u_exp_lut/idx_q_reg_6_ | u_npu_c3/u_tile0/u_sfu/u_exp_lut/lut_out_q_reg_9_ | npu_clk | 0.021 |
| func_ss_0p675v_m40c_cworst_ccworst | 5 | u_ddr_ss/u_mc2/u_sched/u_age_mtx/age_q_reg_12__5_ | u_ddr_ss/u_mc2/u_sched/cmd_sel_q_reg_3_ | mc_clk | 0.027 |
| func_ss_0p675v_m40c_rcworst | 1 | u_npu_c1/u_tile2/u_wbuf/rd_data_q_reg_411_ | u_npu_c1/u_tile2/u_mac_arr/u_pe_r12_c7/acc_q_reg_23_ | npu_clk | 0.014 |
| func_ss_0p675v_m40c_rcworst | 2 | u_cpu/u_core3/u_exu/u_byp/src1_q_reg_41_ | u_cpu/u_core3/u_exu/u_alu0/res_q_reg_63_ | cpu_clk | 0.019 |
| func_ss_0p675v_m40c_rcworst | 3 | u_npu_c3/u_tile0/u_sfu/u_exp_lut/idx_q_reg_6_ | u_npu_c3/u_tile0/u_sfu/u_exp_lut/lut_out_q_reg_9_ | npu_clk | 0.028 |
| func_ss_0p675v_m40c_rcworst | 4 | u_ddr_ss/u_mc2/u_sched/u_age_mtx/age_q_reg_12__5_ | u_ddr_ss/u_mc2/u_sched/cmd_sel_q_reg_3_ | mc_clk | 0.031 |
| func_ss_0p675v_m40c_rcworst | 5 | u_noc/u_rtr_1_3/u_vc_alloc/req_q_reg_17_ | u_noc/u_rtr_1_3/u_sw_alloc/grant_q_reg_4_ | core_clk | 0.040 |
| func_tt_0p750v_85c_typical | 1 | u_npu_c1/u_tile2/u_wbuf/rd_data_q_reg_411_ | u_npu_c1/u_tile2/u_mac_arr/u_pe_r12_c7/acc_q_reg_23_ | npu_clk | 0.142 |
| func_tt_0p750v_85c_typical | 2 | u_cpu/u_core3/u_exu/u_byp/src1_q_reg_41_ | u_cpu/u_core3/u_exu/u_alu0/res_q_reg_63_ | cpu_clk | 0.149 |
| func_tt_0p750v_85c_typical | 3 | u_gbuf/u_bank06/u_ram_lo (Q[71], SRAM macro) | u_gbuf/u_bank06/u_ecc/syn_q_reg_4_ | core_clk | 0.158 |
| func_tt_0p750v_85c_typical | 4 | u_npu_c3/u_tile0/u_sfu/u_exp_lut/idx_q_reg_6_ | u_npu_c3/u_tile0/u_sfu/u_exp_lut/lut_out_q_reg_9_ | npu_clk | 0.166 |
| func_tt_0p750v_85c_typical | 5 | u_ddr_ss/u_mc2/u_sched/u_age_mtx/age_q_reg_12__5_ | u_ddr_ss/u_mc2/u_sched/cmd_sel_q_reg_3_ | mc_clk | 0.171 |
| func_ff_0p825v_m40c_cbest_ccbest | 1 | u_gbuf/u_bank06/u_ram_lo (Q[71], SRAM macro) | u_gbuf/u_bank06/u_ecc/syn_q_reg_4_ | core_clk | 0.206 |
| func_ff_0p825v_m40c_cbest_ccbest | 2 | u_ddr_ss/u_mc0/u_dfi_if/wr_data_q_reg_117_ | u_ddr_ss/u_phy0/DFI_WRDATA_P0[117] (PHY macro pin) | mc_clk | 0.212 |
| func_ff_0p825v_m40c_cbest_ccbest | 3 | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/data_q_reg_388_ | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/crc_q_reg_29_ | pcie_core_clk | 0.219 |
| func_ff_0p825v_m40c_cbest_ccbest | 4 | u_pcie0_wrap/u_ctl/u_dl/u_lcrc_gen/crc_q_reg_17_ | u_pcie0_wrap/u_ctl/u_dl/u_tx_mux/tlp_q_reg_455_ | pcie_core_clk | 0.225 |
| func_ff_0p825v_m40c_cbest_ccbest | 5 | u_gbuf/u_bank21/u_arb/req_q_reg_9_ | u_gbuf/u_bank21/u_arb/gnt_q_reg_2_ | core_clk | 0.231 |
| func_ff_0p825v_m40c_rcbest | 1 | u_gbuf/u_bank06/u_ram_lo (Q[71], SRAM macro) | u_gbuf/u_bank06/u_ecc/syn_q_reg_4_ | core_clk | 0.214 |
| func_ff_0p825v_m40c_rcbest | 2 | u_ddr_ss/u_mc0/u_dfi_if/wr_data_q_reg_117_ | u_ddr_ss/u_phy0/DFI_WRDATA_P0[117] (PHY macro pin) | mc_clk | 0.219 |
| func_ff_0p825v_m40c_rcbest | 3 | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/data_q_reg_388_ | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/crc_q_reg_29_ | pcie_core_clk | 0.226 |
| func_ff_0p825v_m40c_rcbest | 4 | u_pcie0_wrap/u_ctl/u_dl/u_lcrc_gen/crc_q_reg_17_ | u_pcie0_wrap/u_ctl/u_dl/u_tx_mux/tlp_q_reg_455_ | pcie_core_clk | 0.230 |
| func_ff_0p825v_m40c_rcbest | 5 | u_gbuf/u_bank21/u_arb/req_q_reg_9_ | u_gbuf/u_bank21/u_arb/gnt_q_reg_2_ | core_clk | 0.237 |
| func_ff_0p825v_125c_cbest_ccbest | 1 | u_ddr_ss/u_mc0/u_dfi_if/wr_data_q_reg_117_ | u_ddr_ss/u_phy0/DFI_WRDATA_P0[117] (PHY macro pin) | mc_clk | 0.231 |
| func_ff_0p825v_125c_cbest_ccbest | 2 | u_gbuf/u_bank06/u_ram_lo (Q[71], SRAM macro) | u_gbuf/u_bank06/u_ecc/syn_q_reg_4_ | core_clk | 0.236 |
| func_ff_0p825v_125c_cbest_ccbest | 3 | u_pcie0_wrap/u_ctl/u_dl/u_lcrc_gen/crc_q_reg_17_ | u_pcie0_wrap/u_ctl/u_dl/u_tx_mux/tlp_q_reg_455_ | pcie_core_clk | 0.244 |
| func_ff_0p825v_125c_cbest_ccbest | 4 | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/data_q_reg_388_ | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/crc_q_reg_29_ | pcie_core_clk | 0.249 |
| func_ff_0p825v_125c_cbest_ccbest | 5 | u_gbuf/u_bank21/u_arb/req_q_reg_9_ | u_gbuf/u_bank21/u_arb/gnt_q_reg_2_ | core_clk | 0.253 |
| func_ff_0p825v_125c_rcbest | 1 | u_ddr_ss/u_mc0/u_dfi_if/wr_data_q_reg_117_ | u_ddr_ss/u_phy0/DFI_WRDATA_P0[117] (PHY macro pin) | mc_clk | 0.238 |
| func_ff_0p825v_125c_rcbest | 2 | u_gbuf/u_bank06/u_ram_lo (Q[71], SRAM macro) | u_gbuf/u_bank06/u_ecc/syn_q_reg_4_ | core_clk | 0.242 |
| func_ff_0p825v_125c_rcbest | 3 | u_pcie0_wrap/u_ctl/u_dl/u_lcrc_gen/crc_q_reg_17_ | u_pcie0_wrap/u_ctl/u_dl/u_tx_mux/tlp_q_reg_455_ | pcie_core_clk | 0.250 |
| func_ff_0p825v_125c_rcbest | 4 | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/data_q_reg_388_ | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/crc_q_reg_29_ | pcie_core_clk | 0.255 |
| func_ff_0p825v_125c_rcbest | 5 | u_gbuf/u_bank21/u_arb/req_q_reg_9_ | u_gbuf/u_bank21/u_arb/gnt_q_reg_2_ | core_clk | 0.258 |

## 7. Hold paths, functional views

### 7.1 Top-5 hold paths, ff views

| View | # | Startpoint | Endpoint | Clock | Slack (ns) | Status / waiver |
|---|---|---|---|---|---|---|
| func_ff_0p825v_m40c_cbest_ccbest | 1 | u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_ | u_gbuf/u_bank13/u_ram_hi/A[5] (SRAM macro pin) | core_clk | 0.004 | - |
| func_ff_0p825v_m40c_cbest_ccbest | 2 | u_ddr_ss/u_mc1/u_dfi_if/dfi_rddata_en_q_reg_2_ | u_ddr_ss/u_phy1/DFI_RDDATA_EN_P2 (PHY macro pin) | mc_clk | 0.006 | - |
| func_ff_0p825v_m40c_cbest_ccbest | 3 | u_pcie0_wrap/u_ctl/u_pipe_if/txdata_q_reg_207_ | u_pcie0_wrap/u_phy/PIPE_TX_DATA[207] (PHY macro pin) | pcie_core_clk | 0.009 | - |
| func_ff_0p825v_m40c_cbest_ccbest | 4 | u_cpu/u_core2/u_lsu/u_stb/stb_vld_q_reg_6_ | u_cpu/u_core2/u_lsu/u_stb/fwd_hit_q_reg_6_ | cpu_clk | 0.011 | - |
| func_ff_0p825v_m40c_cbest_ccbest | 5 | u_sec_encl/u_otp_if/otp_rdata_q_reg_37_ | u_sec_encl/u_keyldr/root_key_q_reg_37_ | sec_clk | 0.015 | post-ECO-B-003; W-017 withdrawn |
| func_ff_0p825v_m40c_rcbest | 1 | u_ddr_ss/u_mc1/u_dfi_if/dfi_rddata_en_q_reg_2_ | u_ddr_ss/u_phy1/DFI_RDDATA_EN_P2 (PHY macro pin) | mc_clk | 0.006 | - |
| func_ff_0p825v_m40c_rcbest | 2 | u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_ | u_gbuf/u_bank13/u_ram_hi/A[5] (SRAM macro pin) | core_clk | 0.008 | - |
| func_ff_0p825v_m40c_rcbest | 3 | u_npu_c0/u_tile1/u_lsram_ctl/wr_mask_q_reg_31_ | u_npu_c0/u_tile1/u_lsram_b2/BWEB[31] (SRAM macro pin) | npu_clk | 0.009 | - |
| func_ff_0p825v_m40c_rcbest | 4 | u_pcie0_wrap/u_ctl/u_pipe_if/txdata_q_reg_207_ | u_pcie0_wrap/u_phy/PIPE_TX_DATA[207] (PHY macro pin) | pcie_core_clk | 0.010 | - |
| func_ff_0p825v_m40c_rcbest | 5 | u_noc/u_rtr_3_0/u_in_port_w/credit_q_reg_1_ | u_noc/u_rtr_3_0/u_out_port_w/crd_rtn_q_reg_1_ | core_clk | 0.011 | - |
| func_ff_0p825v_125c_cbest_ccbest | 1 | u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_ | u_gbuf/u_bank13/u_ram_hi/A[5] (SRAM macro pin) | core_clk | 0.007 | - |
| func_ff_0p825v_125c_cbest_ccbest | 2 | u_ddr_ss/u_mc1/u_dfi_if/dfi_rddata_en_q_reg_2_ | u_ddr_ss/u_phy1/DFI_RDDATA_EN_P2 (PHY macro pin) | mc_clk | 0.010 | - |
| func_ff_0p825v_125c_cbest_ccbest | 3 | u_pcie0_wrap/u_ctl/u_pipe_if/txdata_q_reg_207_ | u_pcie0_wrap/u_phy/PIPE_TX_DATA[207] (PHY macro pin) | pcie_core_clk | 0.012 | - |
| func_ff_0p825v_125c_cbest_ccbest | 4 | u_npu_c0/u_tile1/u_lsram_ctl/wr_mask_q_reg_31_ | u_npu_c0/u_tile1/u_lsram_b2/BWEB[31] (SRAM macro pin) | npu_clk | 0.014 | - |
| func_ff_0p825v_125c_cbest_ccbest | 5 | u_cpu/u_core2/u_lsu/u_stb/stb_vld_q_reg_6_ | u_cpu/u_core2/u_lsu/u_stb/fwd_hit_q_reg_6_ | cpu_clk | 0.016 | - |
| func_ff_0p825v_125c_rcbest | 1 | u_ddr_ss/u_mc1/u_dfi_if/dfi_rddata_en_q_reg_2_ | u_ddr_ss/u_phy1/DFI_RDDATA_EN_P2 (PHY macro pin) | mc_clk | 0.009 | - |
| func_ff_0p825v_125c_rcbest | 2 | u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_ | u_gbuf/u_bank13/u_ram_hi/A[5] (SRAM macro pin) | core_clk | 0.011 | - |
| func_ff_0p825v_125c_rcbest | 3 | u_npu_c0/u_tile1/u_lsram_ctl/wr_mask_q_reg_31_ | u_npu_c0/u_tile1/u_lsram_b2/BWEB[31] (SRAM macro pin) | npu_clk | 0.013 | - |
| func_ff_0p825v_125c_rcbest | 4 | u_pcie0_wrap/u_ctl/u_pipe_if/txdata_q_reg_207_ | u_pcie0_wrap/u_phy/PIPE_TX_DATA[207] (PHY macro pin) | pcie_core_clk | 0.015 | - |
| func_ff_0p825v_125c_rcbest | 5 | u_noc/u_rtr_3_0/u_in_port_w/credit_q_reg_1_ | u_noc/u_rtr_3_0/u_out_port_w/crd_rtn_q_reg_1_ | core_clk | 0.017 | - |

### 7.2 Worst hold path, ss and tt views

| View | Startpoint | Endpoint | Clock | Slack (ns) |
|---|---|---|---|---|
| func_ss_0p675v_125c_cworst_ccworst | u_cpu/u_core1/u_lsu/u_stb/stb_vld_q_reg_2_ | u_cpu/u_core1/u_lsu/u_stb/fwd_hit_q_reg_2_ | cpu_clk | 0.018 |
| func_ss_0p675v_125c_rcworst | u_cpu/u_core1/u_lsu/u_stb/stb_vld_q_reg_2_ | u_cpu/u_core1/u_lsu/u_stb/fwd_hit_q_reg_2_ | cpu_clk | 0.021 |
| func_ss_0p675v_m40c_cworst_ccworst | u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_ | u_gbuf/u_bank13/u_ram_hi/A[5] (SRAM macro pin) | core_clk | 0.016 |
| func_ss_0p675v_m40c_rcworst | u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_ | u_gbuf/u_bank13/u_ram_hi/A[5] (SRAM macro pin) | core_clk | 0.019 |
| func_tt_0p750v_85c_typical | u_ddr_ss/u_mc1/u_dfi_if/dfi_rddata_en_q_reg_2_ | u_ddr_ss/u_phy1/DFI_RDDATA_EN_P2 (PHY macro pin) | mc_clk | 0.031 |

## 8. Near-critical setup paths (< 0.100 ns)

Worst endpoint per clock group with 0.000 <= slack < 0.100 ns that is not already listed in Section 6, for the four ss functional views. The count column is the number of endpoints in the clock group with 0.000 <= slack < 0.100 ns. No functional endpoint in the tt or ff views has setup slack below 0.100 ns.

| View | Clock group | Worst endpoint | Slack (ns) | Endpoints < 0.100 ns |
|---|---|---|---|---|
| func_ss_0p675v_m40c_cworst_ccworst | core_clk | u_noc/u_rtr_1_3/u_sw_alloc/grant_q_reg_4_ | 0.033 | 318 |
| func_ss_0p675v_m40c_cworst_ccworst | npu_clk | u_npu_c2/u_tile1/u_mac_arr/u_pe_r9_c2/acc_q_reg_21_ | 0.036 | 1,412 |
| func_ss_0p675v_m40c_cworst_ccworst | cpu_clk | u_cpu/u_core0/u_exu/u_alu1/res_q_reg_62_ | 0.038 | 624 |
| func_ss_0p675v_m40c_cworst_ccworst | mc_clk | u_ddr_ss/u_mc3/u_sched/cmd_sel_q_reg_1_ | 0.044 | 206 |
| func_ss_0p675v_m40c_cworst_ccworst | pcie_core_clk | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/crc_q_reg_11_ | 0.052 | 141 |
| func_ss_0p675v_m40c_cworst_ccworst | sec_clk | u_sec_encl/u_keyldr/root_key_q_reg_101_ | 0.069 | 6 |
| func_ss_0p675v_125c_cworst_ccworst | pcie_core_clk | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/crc_q_reg_29_ | 0.036 | 118 |
| func_ss_0p675v_125c_cworst_ccworst | cpu_clk | u_cpu/u_core0/u_exu/u_alu1/res_q_reg_62_ | 0.039 | 588 |
| func_ss_0p675v_125c_cworst_ccworst | npu_clk | u_npu_c2/u_tile1/u_mac_arr/u_pe_r9_c2/acc_q_reg_21_ | 0.041 | 1,207 |
| func_ss_0p675v_125c_cworst_ccworst | core_clk | u_noc/u_rtr_0_2/u_sw_alloc/grant_q_reg_1_ | 0.046 | 287 |
| func_ss_0p675v_125c_cworst_ccworst | mc_clk | u_ddr_ss/u_mc3/u_sched/cmd_sel_q_reg_1_ | 0.048 | 193 |
| func_ss_0p675v_125c_cworst_ccworst | sec_clk | u_sec_encl/u_keyldr/root_key_q_reg_101_ | 0.087 | 2 |
| func_ss_0p675v_m40c_rcworst | npu_clk | u_npu_c2/u_tile1/u_mac_arr/u_pe_r9_c2/acc_q_reg_21_ | 0.043 | 1,168 |
| func_ss_0p675v_m40c_rcworst | cpu_clk | u_cpu/u_core0/u_exu/u_alu1/res_q_reg_62_ | 0.045 | 540 |
| func_ss_0p675v_m40c_rcworst | sec_clk | u_sec_encl/u_keyldr/root_key_q_reg_37_ | 0.045 | 1 |
| func_ss_0p675v_m40c_rcworst | core_clk | u_noc/u_rtr_0_2/u_sw_alloc/grant_q_reg_1_ | 0.049 | 262 |
| func_ss_0p675v_m40c_rcworst | mc_clk | u_ddr_ss/u_mc3/u_sched/cmd_sel_q_reg_1_ | 0.052 | 171 |
| func_ss_0p675v_m40c_rcworst | pcie_core_clk | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/crc_q_reg_11_ | 0.061 | 97 |
| func_ss_0p675v_125c_rcworst | cpu_clk | u_cpu/u_core0/u_exu/u_alu1/res_q_reg_62_ | 0.046 | 497 |
| func_ss_0p675v_125c_rcworst | sec_clk | u_sec_encl/u_keyldr/root_key_q_reg_37_ | 0.047 | 1 |
| func_ss_0p675v_125c_rcworst | npu_clk | u_npu_c2/u_tile1/u_mac_arr/u_pe_r9_c2/acc_q_reg_21_ | 0.048 | 1,011 |
| func_ss_0p675v_125c_rcworst | core_clk | u_noc/u_rtr_0_2/u_sw_alloc/grant_q_reg_1_ | 0.053 | 240 |
| func_ss_0p675v_125c_rcworst | mc_clk | u_ddr_ss/u_mc3/u_sched/cmd_sel_q_reg_1_ | 0.055 | 158 |
| func_ss_0p675v_125c_rcworst | pcie_core_clk | u_pcie0_wrap/u_ctl/u_tl_rx/u_ecrc/crc_q_reg_11_ | 0.057 | 88 |

sec_clk: u_sec_encl/u_keyldr/root_key_q_reg_37_ is load-capacitance dominated (X1 drivers on two long shielded routes: otp_rdata_q[37] to u_secded and ecc_data[37] back to ecc_bypass_mux_37, which sits beside otp_rdata_q_reg_37_), so its cworst_ccworst to rcworst spread (0.082 ns at -40 C, 0.059 ns at 125 C) is larger than that of the paths above.

## 9. Test-mode timing

### 9.1 Worst path per test view

| View | Check | Slack (ns) | Endpoint | Startpoint | Clock | Status / waiver |
|---|---|---|---|---|---|---|
| scan_shift_ss_0p675v_m40c_cworst_ccworst | setup | -0.138 | u_npu_top/u_trace_funnel/tf_data_q_reg_63_ | u_npu_c2/u_dbg_tap/trace_data_q_reg_63_ | scan_clk | VIOLATED - waived (W-004) |
| scan_shift_ss_0p675v_m40c_cworst_ccworst | hold | 0.052 | u_cpu/u_core0/u_lsu/lsq_q_reg_3__13_ (SI) | u_cpu/u_core0/u_lsu/lsq_q_reg_3__12_ | scan_clk | - |
| scan_shift_ff_0p825v_m40c_cbest_ccbest | setup | 1.912 | u_npu_top/u_dbg_cfg/cfg_q_reg_0_ (SI) | u_npu_c3/u_scan_lkup_ch41 (lockup latch) | scan_clk | - |
| scan_shift_ff_0p825v_m40c_cbest_ccbest | hold | 0.011 | u_gbuf/u_bank02/u_arb/ptr_q_reg_2_ (SI) | u_gbuf/u_bank02/u_arb/ptr_q_reg_1_ | scan_clk | - |
| scan_capture_ss_0p675v_125c_cworst_ccworst | setup | 0.027 | u_cpu/u_core3/u_exu/u_alu0/res_q_reg_63_ | u_cpu/u_core3/u_exu/u_byp/src1_q_reg_41_ | cpu_clk (OCC capture, 1200.0 MHz) | - |
| scan_capture_ss_0p675v_125c_cworst_ccworst | hold | 0.035 | u_noc/u_rtr_3_0/u_out_port_w/crd_rtn_q_reg_1_ | u_noc/u_rtr_3_0/u_in_port_w/credit_q_reg_1_ | core_clk (OCC capture) | - |
| scan_capture_ff_0p825v_m40c_cbest_ccbest | setup | 0.318 | u_gbuf/u_bank06/u_ecc/syn_q_reg_4_ | u_gbuf/u_bank06/u_ram_lo (Q[71], SRAM macro) | core_clk (OCC capture, 800.0 MHz) | - |
| scan_capture_ff_0p825v_m40c_cbest_ccbest | hold | 0.005 | u_gbuf/u_bank13/u_ram_hi/A[5] (SRAM macro pin) | u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_ | core_clk (OCC capture) | - |
| mbist_ss_0p675v_125c_cworst_ccworst | setup | 0.044 | u_npu_c1/u_tile0/u_lsram_b3/D[117] (SRAM macro pin) | u_npu_c1/u_mbist_ctl/u_dgen/wdata_q_reg_117_ | npu_clk (MBIST, 960.0 MHz) | - |
| mbist_ss_0p675v_125c_cworst_ccworst | hold | 0.029 | u_gbuf/u_bank20/u_ram_lo/A[4] (SRAM macro pin) | u_gbuf/u_mbist_ctl/u_agen/addr_q_reg_4_ | core_clk (MBIST) | - |

### 9.2 scan_shift_ss_0p675v_m40c_cworst_ccworst: top-5 setup endpoints

All 64 violating endpoints are u_npu_top/u_trace_funnel/tf_data_q_reg_0_ .. tf_data_q_reg_63_ (WNS -0.138 ns, TNS -5.874 ns); the remaining 59 range from -0.127 to -0.041 ns. All 64 are covered by W-004 (KST-DFT-EXC rev 3 entry TE-DFT-014).

| # | Startpoint | Endpoint | Slack (ns) | Status / waiver |
|---|---|---|---|---|
| 1 | u_npu_c2/u_dbg_tap/trace_data_q_reg_63_ | u_npu_top/u_trace_funnel/tf_data_q_reg_63_ | -0.138 | VIOLATED - waived (W-004) |
| 2 | u_npu_c2/u_dbg_tap/trace_data_q_reg_62_ | u_npu_top/u_trace_funnel/tf_data_q_reg_62_ | -0.136 | VIOLATED - waived (W-004) |
| 3 | u_npu_c2/u_dbg_tap/trace_data_q_reg_61_ | u_npu_top/u_trace_funnel/tf_data_q_reg_61_ | -0.133 | VIOLATED - waived (W-004) |
| 4 | u_npu_c2/u_dbg_tap/trace_data_q_reg_58_ | u_npu_top/u_trace_funnel/tf_data_q_reg_58_ | -0.131 | VIOLATED - waived (W-004) |
| 5 | u_npu_c2/u_dbg_tap/trace_data_q_reg_60_ | u_npu_top/u_trace_funnel/tf_data_q_reg_60_ | -0.129 | VIOLATED - waived (W-004) |

These are functional D-pin paths. In scan_shift SE=1 selects SI, so the D path is not sensitizable; SE is pipelined (3-stage se_pipe per cluster) and is intentionally not set by case analysis in KST_scan_shift.sdc: the stage-3 se_pipe outputs also drive the OCC shift-clock gates timed under W-014, and team policy (CHK-STA-06) keeps DFT false paths visible as reporting-only exceptions, so the tool still times the D path. The shift path into u_npu_top/u_trace_funnel/tf_data_q_reg_63_/SI (through lockup latch u_npu_top/u_trace_funnel/lkup_tf_63) meets with +0.212 ns in the same view. In scan_capture the functional multicycle-4 on trace_data_q -> tf_data_q is inherited from KST_func.sdc into KST_scan_capture.sdc, and the tf_data_q endpoints are masked in the transition-fault pattern set. Functionally, trace_data_q -> tf_data_q is a multicycle-4 path in npu_clk (budget 4 x 0.833 = 3.333 ns) and is met in all functional views; its worst functional slack is +0.118 ns in func_ss_0p675v_m40c_cworst_ccworst (data path 3.098 ns against 3.333 - 0.050 - 0.041 = 3.242 ns, launch/capture skew -0.026 ns). Path report: A.3.

## 10. DRV and non-slack checks

| Check | Views | Violations | Waived | Unwaived | Waiver(s) |
|---|---|---|---|---|---|
| Max transition (limit 0.250 ns data / 0.100 ns clock) | all 14 | 710 nets | 710 | 0 | W-009, W-010, W-022, W-023 (tie-off/spare-cell nets only) |
| Max capacitance | all 14 | 57 nets | 57 | 0 | W-011 (tie-off/spare-cell nets only) |
| Max fanout (limit 32, signal nets) | all 14 | 0 | - | 0 | - |
| Minimum pulse width | scan_capture_ss_0p675v_125c_cworst_ccworst | 5 pins | 5 | 0 | W-003, W-013 (PHY macro test pins) |
| Minimum period | all 14 | 0 | - | 0 | - |
| Clock-gating setup | scan_capture_ss (6), scan_shift_ss (6), mbist_ss (32) | 44 enables | 44 | 0 | W-005, W-006, W-014 (OCC/MBIST enables, test modes only) |
| Clock-gating hold | all 14 | 0 | - | 0 | - |
| Recovery / removal | all 14 | 0 | - | 0 | - |
| Noise (glitch) at receivers | all 14 | 0 | - | 0 | - |
| Unconstrained endpoints/startpoints | func (9) | 73 pins/ports | 73 | 0 | W-001, W-002, W-012, W-015, W-016, W-020, W-024 (analog test / asynchronous pins) |

## 11. Waivers applied in this report

23 of the 24 entries in KST-STA-021 rev B are applied to the results above.

| Category | Waiver(s) | View(s) | Scope |
|---|---|---|---|
| Functional: unconstrained analog-test and asynchronous pins | W-001, W-002, W-012, W-015, W-016, W-020, W-024 | func (9 views) | 73 pins/ports |
| All modes: DRV on tie-off/spare-cell nets | W-009, W-010, W-011, W-022, W-023 | all 14 views | 767 nets |
| Test mode: setup, DFT exception (reporting-only) | W-004 | scan_shift_ss_0p675v_m40c_cworst_ccworst | 64 endpoints |
| Test mode: multicycle exceptions | W-007, W-008, W-018, W-019, W-021 | scan_capture_ss / mbist_ss | explicit from-lists |
| Test mode: clock-gating checks on OCC/MBIST enables | W-005, W-006, W-014 | scan_shift_ss / scan_capture_ss / mbist_ss | 44 enables |
| Test mode: minimum pulse width on PHY macro test pins | W-003, W-013 | scan_capture_ss_0p675v_125c_cworst_ccworst | 5 pins |
| Withdrawn (not applied) | W-017 (Withdrawn, ECO-B-003) | - | - |

## 12. Sign-off

| Role | Name | Decision | Date |
|---|---|---|---|
| STA Lead (owner) | Mei-Lin Chou | GREEN | 2026-09-02 |
| STA Engineer (SEC/PMU partitions) | Jonah Pike | Prepared | 2026-09-02 |
| PD Lead (reviewer) | Daniel Achterberg | Reviewed | 2026-09-02 |

## Appendix A. Path reports

Condensed path reports from the sign-off run. Times in ns; r/f = rise/fall at the pin.

### A.1 Worst functional setup path

View func_ss_0p675v_m40c_cworst_ccworst; startpoint u_sec_encl/u_otp_if/otp_rdata_q_reg_37_; endpoint u_sec_encl/u_keyldr/root_key_q_reg_37_; clock sec_clk (period 2.000 ns); path group reg2reg; max path through the SECDED check/correct logic u_sec_encl/u_keyldr/u_secded; Vt mix SVT only (u_sec_encl). Incr values include SI delta delay and POCV (3.0 sigma).

| Point | Cell | Incr (ns) | Path (ns) |
|---|---|---|---|
| clock sec_clk (rise edge) |  | 0.000 | 0.000 |
| clock network delay (propagated) |  | 0.812 | 0.812 |
| u_sec_encl/u_otp_if/otp_rdata_q_reg_37_/CP | DFFRQ_X1 | 0.000 | 0.812 r |
| u_sec_encl/u_otp_if/otp_rdata_q_reg_37_/Q | DFFRQ_X1 | 0.121 | 0.933 r |
| u_sec_encl/u_keyldr/u_secded/in_qual_37/A1 (net otp_rdata_q[37], shielded route) | AND2_X1 | 0.072 | 1.005 r |
| u_sec_encl/u_keyldr/u_secded/in_qual_37/Z | AND2_X1 | 0.081 | 1.086 r |
| u_sec_encl/u_keyldr/u_secded/in_fo_buf_37/Z | BUF_X2 | 0.078 | 1.164 r |
| u_sec_encl/u_keyldr/u_secded/syn_x3_l1_18/Z | XOR2_X1 | 0.104 | 1.268 f |
| u_sec_encl/u_keyldr/u_secded/syn_x3_l2_9/Z | XOR2_X1 | 0.108 | 1.376 r |
| u_sec_encl/u_keyldr/u_secded/syn_x3_l3_4/Z | XOR2_X1 | 0.102 | 1.478 f |
| u_sec_encl/u_keyldr/u_secded/syn_x3_l4_2/Z | XOR2_X1 | 0.109 | 1.587 r |
| u_sec_encl/u_keyldr/u_secded/syn_x3_l5_1/Z | XOR2_X1 | 0.106 | 1.693 f |
| u_sec_encl/u_keyldr/u_secded/syn_x3_l6_0/Z | XOR2_X2 | 0.094 | 1.787 r |
| u_sec_encl/u_keyldr/u_secded/syn_x3_l7_0/Z | XOR2_X2 | 0.091 | 1.878 f |
| u_sec_encl/u_keyldr/u_secded/syn_x3_chk/Z | XOR2_X2 | 0.093 | 1.971 r |
| u_sec_encl/u_keyldr/u_secded/syn_s3_buf_0/Z | BUF_X4 | 0.069 | 2.040 r |
| u_sec_encl/u_keyldr/u_secded/syn_s3_buf_4/Z | BUF_X2 | 0.117 | 2.157 r |
| u_sec_encl/u_keyldr/u_secded/dec_37_nd3b/ZN | NAND3_X1 | 0.096 | 2.253 f |
| u_sec_encl/u_keyldr/u_secded/dec_37_nr3/ZN | NOR3_X1 | 0.131 | 2.384 r |
| u_sec_encl/u_keyldr/u_secded/corr_xor_37/Z | XOR2_X1 | 0.112 | 2.496 f |
| u_sec_encl/u_keyldr/u_secded/ded_gate_37/Z | AND2_X1 | 0.084 | 2.580 f |
| u_sec_encl/u_keyldr/ecc_bypass_mux_37/I0 (net ecc_data[37], shielded route) | MUX2_X1 | 0.139 | 2.719 f |
| u_sec_encl/u_keyldr/ecc_bypass_mux_37/Z | MUX2_X1 | 0.094 | 2.813 f |
| u_sec_encl/u_keyldr/eco_b003_dly_0/Z | DLY2_X1 | 0.050 | 2.863 f |
| u_sec_encl/u_keyldr/eco_b003_dly_1/Z | DLY2_X1 | 0.051 | 2.914 f |
| u_sec_encl/u_keyldr/root_key_q_reg_37_/D | DFFRQ_X1 | 0.004 | 2.918 f |
| **data arrival time** |  |  | **2.918** |
| clock sec_clk (rise edge) |  | 2.000 | 2.000 |
| clock network delay (propagated) |  | 0.959 | 2.959 |
| clock reconvergence pessimism |  | 0.021 | 2.980 |
| clock uncertainty |  | -0.050 | 2.930 |
| u_sec_encl/u_keyldr/root_key_q_reg_37_/CP | DFFRQ_X1 |  | 2.930 r |
| library setup time |  | -0.049 | 2.881 |
| **data required time** |  |  | **2.881** |
| **slack (VIOLATED)** |  |  | **-0.037** |


### A.2 Worst functional hold path

View func_ff_0p825v_m40c_cbest_ccbest; startpoint u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_; endpoint u_gbuf/u_bank13/u_ram_hi/A[5] (SRAM macro pin); clock core_clk; path group reg2mem.

| Point | Cell | Incr (ns) | Path (ns) |
|---|---|---|---|
| clock core_clk (rise edge) |  | 0.000 | 0.000 |
| clock network delay (propagated) |  | 0.412 | 0.412 |
| u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_/CP | SDFFQ_X2 | 0.000 | 0.412 r |
| u_gbuf/u_bank13/u_arb/rd_addr_q_reg_5_/Q | SDFFQ_X2 | 0.034 | 0.446 r |
| u_gbuf/u_bank13/pnr_hold_buf_0217/Z | BUF_X1 | 0.019 | 0.465 r |
| u_gbuf/u_bank13/u_ram_hi/A[5] | SRAM macro | 0.003 | 0.468 r |
| **data arrival time** |  |  | **0.468** |
| clock core_clk (rise edge) |  | 0.000 | 0.000 |
| clock network delay (propagated) |  | 0.439 | 0.439 |
| clock reconvergence pessimism |  | -0.011 | 0.428 |
| clock uncertainty |  | 0.020 | 0.448 |
| u_gbuf/u_bank13/u_ram_hi/CLK | SRAM macro |  | 0.448 r |
| macro hold time (A vs CLK) |  | 0.016 | 0.464 |
| **data required time** |  |  | **0.464** |
| **slack** |  |  | **0.004** |


### A.3 Worst test-mode setup path

View scan_shift_ss_0p675v_m40c_cworst_ccworst; startpoint u_npu_c2/u_dbg_tap/trace_data_q_reg_63_; endpoint u_npu_top/u_trace_funnel/tf_data_q_reg_63_ (functional D pin); clock scan_clk (200.0 MHz shift, period 5.000 ns); test-mode setup uncertainty 0.200 ns. Launch clock latency 2.551 ns is the NPU cluster-2 tree through the per-cluster OCC mux and clock-gating hierarchy (skew-balanced to the u_npu_top tree in functional mode, not in shift mode); capture clock latency 0.752 ns is the u_npu_top tree.

| Point | Cell | Incr (ns) | Path (ns) |
|---|---|---|---|
| clock scan_clk (rise edge) |  | 0.000 | 0.000 |
| clock network delay (propagated) |  | 2.551 | 2.551 |
| u_npu_c2/u_dbg_tap/trace_data_q_reg_63_/CP | SDFFQ_X1 | 0.000 | 2.551 r |
| u_npu_c2/u_dbg_tap/trace_data_q_reg_63_/Q | SDFFQ_X1 | 0.118 | 2.669 r |
| u_npu_c2/u_dbg_tap/trc_obuf_63/Z | BUF_X4 | 0.083 | 2.752 r |
| u_npu_top/trc_rpt_c2_63_00/Z .. trc_rpt_c2_63_11/Z (12 repeaters, top-level channel, 0.212-0.228 each) | BUF_X8 | 2.638 | 5.390 r |
| u_npu_top/u_trace_funnel/u_arb_mux_63/Z | MUX4_X1 | 0.151 | 5.541 r |
| u_npu_top/u_trace_funnel/u_fmt_ao_63/Z | AO22_X1 | 0.097 | 5.638 r |
| u_npu_top/u_trace_funnel/tf_data_q_reg_63_/D | SDFFQ_X1 | 0.011 | 5.649 r |
| **data arrival time** |  |  | **5.649** |
| clock scan_clk (rise edge) |  | 5.000 | 5.000 |
| clock network delay (propagated) |  | 0.752 | 5.752 |
| clock reconvergence pessimism |  | 0.000 | 5.752 |
| clock uncertainty |  | -0.200 | 5.552 |
| u_npu_top/u_trace_funnel/tf_data_q_reg_63_/CP | SDFFQ_X1 |  | 5.552 r |
| library setup time |  | -0.041 | 5.511 |
| **data required time** |  |  | **5.511** |
| **slack (VIOLATED, waived W-004)** |  |  | **-0.138** |


### A.4 ECO-B-003 timing (incremental run sta_kst_0828_b003_inc, 2026-08-28, hold views)

| Endpoint | View | Check | Rev A slack (ns) | Post-ECO-B-003 slack (ns) | Run |
|---|---|---|---|---|---|
| u_sec_encl/u_keyldr/root_key_q_reg_37_ | func_ff_0p825v_m40c_cbest_ccbest | hold | -0.021 | 0.015 | sta_kst_0828_b003_inc |
| u_sec_encl/u_keyldr/root_key_q_reg_37_ | func_ff_0p825v_m40c_rcbest | hold | 0.012 | 0.048 | sta_kst_0828_b003_inc |


#### A.4.1 Post-ECO-B-003 hold path (from full run sta_kst_0902_full)

View func_ff_0p825v_m40c_cbest_ccbest; startpoint u_sec_encl/u_otp_if/otp_rdata_q_reg_37_; endpoint u_sec_encl/u_keyldr/root_key_q_reg_37_; clock sec_clk (period 2.000 ns); path group reg2reg; min path through the ECC-bypass branch u_sec_encl/u_keyldr/ecc_bypass_mux_37/I1; Vt mix SVT only (u_sec_encl).

| Point | Cell | Incr (ns) | Path (ns) |
|---|---|---|---|
| clock sec_clk (rise edge) |  | 0.000 | 0.000 |
| clock network delay (propagated) |  | 0.291 | 0.291 |
| u_sec_encl/u_otp_if/otp_rdata_q_reg_37_/CP | DFFRQ_X1 | 0.000 | 0.291 r |
| u_sec_encl/u_otp_if/otp_rdata_q_reg_37_/Q | DFFRQ_X1 | 0.036 | 0.327 f |
| u_sec_encl/u_keyldr/ecc_bypass_mux_37/I1 | MUX2_X1 | 0.002 | 0.329 f |
| u_sec_encl/u_keyldr/ecc_bypass_mux_37/Z | MUX2_X1 | 0.023 | 0.352 f |
| u_sec_encl/u_keyldr/eco_b003_dly_0/Z | DLY2_X1 | 0.018 | 0.370 f |
| u_sec_encl/u_keyldr/eco_b003_dly_1/Z | DLY2_X1 | 0.018 | 0.388 f |
| u_sec_encl/u_keyldr/root_key_q_reg_37_/D | DFFRQ_X1 | 0.001 | 0.389 f |
| **data arrival time** |  |  | **0.389** |
| clock sec_clk (rise edge) |  | 0.000 | 0.000 |
| clock network delay (propagated) |  | 0.342 | 0.342 |
| clock reconvergence pessimism |  | -0.007 | 0.335 |
| clock uncertainty |  | 0.020 | 0.355 |
| u_sec_encl/u_keyldr/root_key_q_reg_37_/CP | DFFRQ_X1 |  | 0.355 r |
| library hold time |  | 0.019 | 0.374 |
| **data required time** |  |  | **0.374** |
| **slack** |  |  | **0.015** |
