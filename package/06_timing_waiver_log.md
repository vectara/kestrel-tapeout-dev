# KESTREL (ALX-5100) Timing Waiver Log

| Field | Value |
|---|---|
| Doc ID | KST-STA-021 |
| Title | Timing Waiver Log |
| Revision | A |
| Date | 2026-08-12 |
| Owner | Mei-Lin Chou (STA Lead) |
| Status | Released for TRR-1 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Purpose

This log is the register of timing waivers and timing exceptions referenced by KST-STA-020 (Static Timing Analysis Sign-off Report) rev A. It covers:

- violations that remain visible in the sign-off reports and are waived (for example DFT reporting-only exceptions);
- multicycle exceptions in test modes that are added to the SDC as explicit from-lists;
- non-slack checks (max transition, max capacitance, minimum pulse width, clock-gating) and unconstrained analog-test or asynchronous pins.

Entries are raised and approved under ALD-QA-CHK-007 rev 7.2 (CHK-STA-04, CHK-STA-05, CHK-STA-06). Sign-off netlist for this revision: kst_top_nl_2026.08.07; STA run sta_kst_0811_full (2026-08-11). Entries raised before kst_top_nl_2026.07.17 were first triaged on pre-freeze trial netlists; every entry is re-validated on the sign-off run named above, and the slack shown is from that run.

## 2. Approver matrix

| Scope | Block owner (co-approver with STA Lead Mei-Lin Chou) |
|---|---|
| NPU (u_npu_c0..u_npu_c3, u_npu_top) | Viktor Halloran (NPU Cluster Owner) |
| PCIe (u_pcie0_wrap) | Leo Brandt (PCIe Subsystem Owner) |
| LPDDR5X (u_ddr_ss) | Anjali Deshmukh (Memory Subsystem Owner) |
| Security enclave (u_sec_encl) | Ines Carvalho (Security Enclave Owner) |
| AON / PMU (u_aon, u_core/u_pmu_if), PVT monitors | Kofi Mensah (PMU / Always-on Domain Owner) |
| Top-level partitions (u_noc, u_gbuf, u_cpu, u_periph, u_core/u_crg) | Daniel Achterberg (Physical Design Lead) |
| Test modes (scan_shift, scan_capture, mbist) | Samir Haddad (DFT Lead) |

## 3. Waiver register

| ID | Mode/View | Check | Endpoint(s) | Slack (ns) | Justification | Constraint/ECO ref | Requested by / date | Approver(s) | Approval date | Status |
|---|---|---|---|---|---|---|---|---|---|---|
| W-001 | func (all 9 functional views) | Unconstrained endpoint | u_ddr_ss/u_phy0..u_phy3/ATB[1:0] (8 pins) | n/a | Analog test-bus outputs of the PHY-LP5X-N5 hard macro; no timing arc in the macro timing model; used only for ATE characterization with the PHY in test mode. Vendor integration app note specifies no timing requirement. | KST_func.sdc r4.2 (explicit pin list); vendor code MIPV PHY-LP5X-N5 integration app note sec. 6.4 | Jonah Pike / 2026-07-06 | Mei-Lin Chou, Anjali Deshmukh | 2026-07-09 | Approved |
| W-002 | func (all 9 functional views) | Unconstrained endpoint | u_pcie0_wrap/u_phy/ATB_OUT[3:0], EYEMON_DBG[1:0] (6 pins) | n/a | Analog test-bus and eye-monitor debug outputs of the PCIE5-PHY-N5 hard macro; asynchronous, read by debug firmware through a 2-FF synchronizer only. | KST_func.sdc r4.2 (explicit pin list); PCIE5-PHY-N5 integration guide sec. 9.3 | Jonah Pike / 2026-07-06 | Mei-Lin Chou, Leo Brandt | 2026-07-09 | Approved |
| W-003 | scan_capture_ss_0p675v_125c_cworst_ccworst | Min pulse width (high) | u_ddr_ss/u_phy0..u_phy3/DFT_TCLK (4 pins) | -0.009 | OCC at-speed capture pulse on the PHY boundary-wrapper test clock is 0.009 ns below the macro model limit. Wrapper chains are shift-only; at-speed capture into the wrapper is masked in ATPG. Vendor app note permits at-speed pulses on DFT_TCLK when wrapper capture is masked. | KST-DFT-EXC rev 3 entry TE-DFT-012; vendor code MIPV PHY-LP5X-N5 integration app note sec. 8.2 | Ayesha Qureshi / 2026-07-14 | Mei-Lin Chou, Samir Haddad | 2026-07-17 | Approved |
| W-004 | scan_shift_ss_0p675v_m40c_cworst_ccworst | Setup | u_npu_top/u_trace_funnel/tf_data_q_reg_0_ .. tf_data_q_reg_63_ (64, explicit list) | -0.138 | Functional D-pin path not sensitizable in scan_shift (SE=1 selects SI); SE is pipelined (3-stage se_pipe) and deliberately not case-analyzed, as the se_pipe outputs also drive the OCC shift-clock gates (W-014); scan path Q->SI meets +0.212 ns | KST-DFT-EXC rev 3 entry TE-DFT-014; KST_scan_shift.sdc r3.2 (reporting-only exception) | Ayesha Qureshi / 2026-07-28 | Mei-Lin Chou, Samir Haddad | 2026-07-30 | Approved |
| W-005 | scan_capture_ss_0p675v_125c_cworst_ccworst | Clock-gating setup | u_core/u_crg/u_occ0..u_occ5/u_pls_cg/E (6) | -0.031 | OCC pulse-enable is loaded through the OCC shift register during scan load and is static for the whole capture procedure (settles at least one shift cycle before the first capture pulse); the check is not sensitized in capture. | KST-DFT-EXC rev 3 entry TE-DFT-005; KST_scan_capture.sdc r3.1 | Ayesha Qureshi / 2026-07-02 | Mei-Lin Chou, Samir Haddad | 2026-07-06 | Approved |
| W-006 | mbist_ss_0p675v_125c_cworst_ccworst | Clock-gating setup | u_gbuf/u_bank00..u_bank31/u_mbist_wrap/u_wrap_cg/E (32) | -0.018 | Wrapper clock-gate enable (mbist_en; ICGs added by ECO-A-003) is set by the MBIST controller before the first march element and held static for the whole run; the single-cycle clock-gating check does not apply in mbist. | ECO-A-003; KST-DFT-EXC rev 3 entry TE-DFT-021; KST_mbist.sdc r2.4 | Ayesha Qureshi / 2026-07-26 | Mei-Lin Chou, Samir Haddad | 2026-07-27 | Approved |
| W-007 | mbist_ss_0p675v_125c_cworst_ccworst | Multicycle (setup 2 / hold 1) | u_npu_c0..u_npu_c3/u_mbist_ctl/cfg_q_reg_* -> u_npu_c*/u_tile*/u_lsram_b*/TEST_* (2,048) | -0.066 (1-cycle); +0.976 with exception | MBIST configuration registers are written over IJTAG before mbist_start with the memory clock gated and stay static during each march element; 2-cycle multicycle per MBIST-CTL v4.0 integration manual. | KST-DFT-EXC rev 3 entry TE-DFT-011; KST_mbist.sdc r2.4 (explicit from-list) | Ayesha Qureshi / 2026-07-16 | Mei-Lin Chou, Samir Haddad | 2026-07-20 | Approved |
| W-008 | scan_capture_ss_0p675v_125c_cworst_ccworst | Multicycle (setup 2 / hold 1) | u_core/u_crg/u_occ0..u_occ5/cfg_q_reg_* -> u_core/u_crg/u_occ0..u_occ5/pls_cnt_q_reg_* (24) | -0.041 (1-cycle); +0.792 with exception | OCC configuration (pulse count, domain select) is updated only with the OCC clocks stopped and is static in capture; 2-cycle multicycle from configuration to pulse counters (worst case in the cpu_clk OCC at 1200.0 MHz capture). | KST-DFT-EXC rev 3 entry TE-DFT-006; KST_scan_capture.sdc r3.1 (explicit from-list) | Ayesha Qureshi / 2026-07-02 | Mei-Lin Chou, Samir Haddad | 2026-07-06 | Approved |
| W-009 | all 14 views | Max transition | TIEHI/TIELO nets of spare cells in u_npu_c0..u_npu_c3 (412 nets) | -0.018 (transition) | Non-switching nets: tie cells holding inputs of unused spare/gate-array cells; the transition limit applies to switching nets; no timing arc through these nets. | KST-PD-SPARE rev 2 (spare-cell and tie-off plan) | Daniel Achterberg / 2026-07-21 | Mei-Lin Chou, Viktor Halloran | 2026-07-23 | Approved |
| W-010 | all 14 views | Max transition | TIEHI/TIELO nets of spare cells in u_noc, u_gbuf, u_cpu (268 nets) | -0.011 (transition) | Non-switching tie-off nets of spare cells; no timing arc. | KST-PD-SPARE rev 2 | Jonah Pike / 2026-07-21 | Mei-Lin Chou, Daniel Achterberg | 2026-07-23 | Approved |
| W-011 | all 14 views | Max capacitance | TIEHI/TIELO nets of spare cells in u_periph, u_core/u_crg (57 nets) | n/a (cap -0.003 pF) | Shared tie nets of spare cells (non-switching). ECO-A-007 tied the remaining floating spare-cell inputs (+306 tie cells); residual overshoot at most 0.003 pF. | KST-PD-SPARE rev 2; ECO-A-007 | Jonah Pike / 2026-08-06 | Mei-Lin Chou, Daniel Achterberg | 2026-08-07 | Approved |
| W-012 | func (all 9 functional views) | Unconstrained endpoint | u_ddr_ss/u_phy0..u_phy3/DFI_INIT_COMPLETE, DFI_LP_CTRL_ACK, DFI_LP_DATA_ACK (12 pins) | n/a | Asynchronous init and low-power handshake outputs of the PHY-LP5X-N5 hard macro, re-synchronized in the controller by 2-FF synchronizers; no clocked arc in the macro timing model per vendor app note. | KST_func.sdc r4.2 (explicit pin list); vendor code MIPV PHY-LP5X-N5 integration app note sec. 5.1 | Jonah Pike / 2026-07-06 | Mei-Lin Chou, Anjali Deshmukh | 2026-07-09 | Approved |
| W-013 | scan_capture_ss_0p675v_125c_cworst_ccworst | Min pulse width (high) | u_pcie0_wrap/u_phy/DFT_ACLK (1 pin) | -0.007 | PHY loopback-BIST clock pin. Production test runs PHY loopback BIST from the PHY internal divider, not from OCC capture pulses; during scan capture the PHY test logic is held in bypass. | KST-DFT-EXC rev 3 entry TE-DFT-013; PCIE5-PHY-N5 integration guide sec. 11.4 | Ayesha Qureshi / 2026-07-14 | Mei-Lin Chou, Samir Haddad | 2026-07-17 | Approved |
| W-014 | scan_shift_ss_0p675v_m40c_cworst_ccworst | Clock-gating setup | u_core/u_crg/u_occ0..u_occ5/u_shift_cg/E (6) | -0.022 | Shift-clock gate enables are driven by stage 3 of the pipelined scan enable (se_pipe); the ATPG protocol inserts 4 dead cycles after every SE transition before the first shift or capture pulse. | KST-DFT-EXC rev 3 entry TE-DFT-008; KST_scan_shift.sdc r3.2; ATPG protocol KST_atpg_proto r5 | Ayesha Qureshi / 2026-07-02 | Mei-Lin Chou, Samir Haddad | 2026-07-06 | Approved |
| W-015 | func (all 9 functional views) | Unconstrained endpoint | u_core/u_pvt_mon_00..u_pvt_mon_23/ANA_TEST (24 pins) | n/a | PVT-MON-N5 analog test outputs, ATE characterization only; no digital receiver. | KST_func.sdc r4.2 (explicit pin list); PVT-MON-N5 integration note sec. 4 | Jonah Pike / 2026-07-06 | Mei-Lin Chou, Kofi Mensah | 2026-07-09 | Approved |
| W-016 | func (all 9 functional views) | Unconstrained startpoint | u_core/u_crg/u_pll_core, u_pll_npu, u_pll_cpu, u_pll_ddr /LOCK (4 pins) | n/a | PLL lock indicators are asynchronous outputs, synchronized by 2-FF synchronizers in u_core/u_crg/u_lock_sync before use. | KST_func.sdc r4.2 (explicit pin list); PLL-N5-FRAC integration note sec. 3.2 | Jonah Pike / 2026-07-06 | Mei-Lin Chou, Daniel Achterberg | 2026-07-09 | Approved |
| W-017 | func_ff_0p825v_m40c_cbest_ccbest | Hold | u_sec_encl/u_keyldr/root_key_q_reg_37_ | -0.021 | TBD | (none) | Jonah Pike / 2026-08-06 | (none) | (none) | Waived |
| W-018 | mbist_ss_0p675v_125c_cworst_ccworst | Multicycle (setup 2 / hold 1) | u_cpu/u_mbist_ctl/cfg_q_reg_* -> u_cpu/u_l2/u_data_ram*/TEST_* (512) | -0.029 (1-cycle); +0.804 with exception | CPU L2 MBIST configuration registers are static during each march element (as W-007); 2-cycle multicycle. | KST-DFT-EXC rev 3 entry TE-DFT-011; KST_mbist.sdc r2.4 (explicit from-list) | Ayesha Qureshi / 2026-07-16 | Mei-Lin Chou, Samir Haddad | 2026-07-20 | Approved |
| W-019 | mbist_ss_0p675v_125c_cworst_ccworst | Multicycle (setup 2 / hold 1) | u_ddr_ss/u_mbist_ctl/cfg_q_reg_* -> u_ddr_ss/u_mc0..u_mc3/u_*_ram*/TEST_* (256) | -0.022 (1-cycle); +1.150 with exception | LPDDR5X controller-buffer MBIST configuration registers are static during each march element (as W-007); 2-cycle multicycle. | KST-DFT-EXC rev 3 entry TE-DFT-011; KST_mbist.sdc r2.4 (explicit from-list) | Ayesha Qureshi / 2026-07-16 | Mei-Lin Chou, Samir Haddad | 2026-07-20 | Approved |
| W-020 | func (all 9 functional views) | Unconstrained startpoint | UART0_RXD, PWR_GOOD[3:0], 13 GPIO_A/GPIO_C interrupt inputs (18 ports) | n/a | Asynchronous input ports, each synchronized by a 2-FF synchronizer in u_periph/u_gpio or u_core/u_crg before use; no synchronous capture. | KST_func.sdc r4.2 (explicit port list) | Jonah Pike / 2026-07-06 | Mei-Lin Chou, Daniel Achterberg | 2026-07-09 | Approved |
| W-021 | mbist_ss_0p675v_125c_cworst_ccworst | Multicycle (setup 2 / hold 1) | u_gbuf/u_mbist_ctl/cfg_q_reg_* -> u_gbuf/u_bank*/u_ram_*/TEST_* (1,024) | -0.038 (1-cycle); +1.212 with exception | GBUF MBIST configuration registers are static during each march element (as W-007); 2-cycle multicycle. | KST-DFT-EXC rev 3 entry TE-DFT-011; KST_mbist.sdc r2.4 (explicit from-list) | Ayesha Qureshi / 2026-07-16 | Mei-Lin Chou, Samir Haddad | 2026-07-20 | Approved |
| W-022 | all 14 views | Max transition | TIEHI/TIELO nets of spare cells in u_sec_encl (21 nets) | -0.006 (transition) | Non-switching tie-off nets of spare cells; no timing arc. Tie cells kept inside the enclave shield boundary per security layout rules. | KST-PD-SPARE rev 2 | Jonah Pike / 2026-07-24 | Mei-Lin Chou, Ines Carvalho | 2026-07-27 | Approved |
| W-023 | all 14 views | Max transition | TIEHI/TIELO nets of spare cells in u_aon (9 nets) | -0.004 (transition) | Non-switching tie-off nets of spare cells; no timing arc. | KST-PD-SPARE rev 2 | Jonah Pike / 2026-07-24 | Mei-Lin Chou, Kofi Mensah | 2026-07-27 | Approved |
| W-024 | func (all 9 functional views) | Unconstrained startpoint | u_sec_encl/u_trng/u_ent/RAW_OUT (1 pin) | n/a | Free-running TRNG-ENT entropy source with no clock relationship to sec_clk; its output is sampled through a 2-FF synchronizer into the health-test and conditioning logic. Asynchronous by design per the TRNG-ENT integration guide. | KST_func.sdc r4.2 (explicit pin list); TRNG-ENT integration guide sec. 5 | Jonah Pike / 2026-08-04 | Mei-Lin Chou, Ines Carvalho | 2026-08-06 | Approved |

## 4. Summary

### 4.1 By status

| Status | Count | IDs |
|---|---|---|
| Approved | 23 | W-001..W-016, W-018..W-024 |
| Waived | 1 | W-017 |

### 4.2 By category

| Category | IDs | Count |
|---|---|---|
| Unconstrained analog-test / asynchronous pins (functional) | W-001, W-002, W-012, W-015, W-016, W-020, W-024 | 7 |
| DRV on tie-off/spare-cell nets (CHK-STA-04) | W-009, W-010, W-011, W-022, W-023 | 5 |
| Test-mode reporting-only exception (CHK-STA-06) | W-004 | 1 |
| Test-mode multicycle exceptions (MBIST, OCC) | W-007, W-008, W-018, W-019, W-021 | 5 |
| Test-mode clock-gating checks on OCC/MBIST enables | W-005, W-006, W-014 | 3 |
| Test-mode minimum pulse width on PHY macro test pins | W-003, W-013 | 2 |
| Functional hold | W-017 | 1 |

## 5. References

- KST-STA-020 Static Timing Analysis Sign-off Report (same package revision).
- KST-DFT-EXC rev 3, DFT timing exception list (TE-DFT-005, -006, -008, -011, -012, -013, -014, -021).
- KST-PD-SPARE rev 2, spare-cell and tie-off plan.
- SDC set: KST_func.sdc r4.2, KST_scan_shift.sdc r3.2, KST_scan_capture.sdc r3.1, KST_mbist.sdc r2.4.
- Hard-macro and IP integration notes: vendor code MIPV PHY-LP5X-N5 integration app note; PCIE5-PHY-N5 integration guide; PVT-MON-N5, PLL-N5-FRAC and TRNG-ENT integration notes.
- ALD-QA-CHK-007 rev 7.2, Tape-out Readiness Checklist.
