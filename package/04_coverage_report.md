# KESTREL (ALX-5100) Functional & Code Coverage Report

| Field | Value |
|---|---|
| Doc ID | KST-COV-011 |
| Title | Functional & Code Coverage Report |
| Revision | C (supersedes B) |
| Date | 2026-09-23 |
| Owner | Tomasz Wierzbicki (Verification Lead) |
| Status | Released for TRR-3 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Summary

Package C: RTL kst_rtl_2026.09.17, netlist kst_top_nl_2026.09.19. Nightly regression is 99.8% over three consecutive nightlies; 0 open P1/P2 bugs; code coverage meets CHK-VER-01 on every measured block after approved exclusions CE-001 to CE-006; SDF-annotated GLS on the package-C netlist passes at the min and max corners.

TB-C-001 closed cg_pcie0_l12_entry_exit to 96.8% (120/124); all 57 in-scope covergroups meet their tier target. The new directed test l12_clkreq_tpoweron_gen5 found PCIE-1187 (P1) on 2026-09-10; it was fixed by RTL ECO-C-003, verified and closed on 2026-09-17 (section 4.3). CW-PCIE-003 was rejected by the chair (2026-09-08, TRR-2 AI-12); the requester withdrew the record on 2026-09-22 once the target was met. The four PCIE1 covergroups are excluded under CE-004 (PCIE1 fused off).

| Criterion | Rule | Threshold | Result | Status |
|---|---|---|---|---|
| Code coverage per block | CHK-VER-01 | Line >= 98.0%, branch >= 95.0%, toggle >= 95.0%, FSM state 100%, FSM transition >= 95.0% | All 14 measured blocks at target after approved exclusions | PASS |
| Functional coverage per covergroup | CHK-VER-02 | Tier-1 >= 95.0%, Tier-2 >= 90.0%, Tier-3 >= 80.0% (non-blocking) | 57 of 57 in-scope covergroups at target; cg_pcie0_l12_entry_exit 96.8% (120/124) | PASS |
| Bug database | CHK-VER-03 | 0 open P1/P2; every P3 triaged | 0 open P1/P2; all open P3 triaged with owner | PASS |
| Nightly regression | CHK-VER-04 | >= 99.5% on 3 consecutive nightlies | 99.8% (3-run aggregate; each nightly >= 99.5%) | PASS |
| Coverage exclusions | CHK-VER-05 | Approved record per exclusion | CE-001 to CE-006, each signed by Verification Lead and Chief Architect | PASS |
| Gate-level simulation | CHK-VER-06 | Boot, reset, low-power at min and max SDF | 9 of 9 tests pass at both corners on kst_top_nl_2026.09.19 | PASS |
| Coverage waivers | KST-VPLAN-010 section 8 | Signed before TRR | CW-PCIE-003 withdrawn 2026-09-22 (target met); none in effect | - |

## 2. Snapshot and environment

| Item | Value |
|---|---|
| RTL tag | kst_rtl_2026.09.17 (package-B RTL + RTL change of ECO-C-003; ECO-C-001/ECO-C-002 are physical-only; LEC-matched to the netlist) |
| Sign-off netlist (GLS) | kst_top_nl_2026.09.19; SDF written 2026-09-19 by the sign-off STA tool (SDF-generation run sta_kst_0919_sdf, same netlist and SPEF as sta_kst_0922_full) |
| Regression window | Nightlies 2026-09-19 .. 2026-09-21 |
| Coverage database | cov_kst_2026.09.21_merged (3 nightlies on kst_rtl_2026.09.17 plus the 2026-09-13 weekly 5x seed expansion for blocks without an RTL change; PCIE0 re-collected from scratch after ECO-C-003, nightlies only) |
| Simulator | Logic simulator, 4-state, UVM (IEEE 1800.2-2020) |
| Emulation build | emu_kst_0917 |
| Exclusion files | cov_excl/CE-001.el .. cov_excl/CE-006.el (version-controlled) |
| Verification plan | KST-VPLAN-010 rev C |

## 3. Regression results

| Nightly | RTL tag | Tests run | Passed | Failed | Pass rate |
|---|---|---|---|---|---|
| 2026-09-19 | kst_rtl_2026.09.17 | 19,262 | 19,227 | 35 | 99.8% |
| 2026-09-20 | kst_rtl_2026.09.17 | 19,262 | 19,221 | 41 | 99.8% |
| 2026-09-21 | kst_rtl_2026.09.17 | 19,262 | 19,224 | 38 | 99.8% |
| 3-run aggregate | | 57,786 | 57,672 | 114 | 99.8% |

Failure triage, nightly 2026-09-21 (38 failures):

| Category | Count | Disposition |
|---|---|---|
| Testbench or VIP issue (seed-specific constraint conflicts, scoreboard tolerance) | 16 | Filed against the testbench; no RTL change |
| Infrastructure (license wait, farm timeouts) | 13 | Re-run clean |
| Known open P3/P4 bugs (triaged, with owner) | 9 | Tracked in the bug DB |
| RTL defects, P1/P2 | 0 | - |

## 4. Bug status

### 4.1 Bug database at report date (2026-09-23)

| Priority | Filed | Closed | Open | Open, triaged with owner |
|---|---|---|---|---|
| P1 | 42 | 42 | 0 | - |
| P2 | 193 | 193 | 0 | - |
| P3 | 648 | 639 | 9 | 9 |
| P4 | 641 | 619 | 22 | 22 |
| Total | 1,524 | 1,493 | 31 | 31 |

Since package A (P2 187), P2 filed/closed includes 4 reports closed without a design change: 2 not-a-bug (testbench scoreboard misconfiguration, package B) and 2 raised during PCIE-1187 triage and closed as duplicates of PCIE-1187 (package C). Section 4.2 lists only bugs closed by a design change.

### 4.2 P1/P2 bugs closed since 2026-07-01

| Bug | Priority | Summary | Fix | Closed |
|---|---|---|---|---|
| NOC-0244 | P2 | Per-VC credit counter wrapped at 16 outstanding flits in NoC stress test | ECO-A-001 | 2026-07-21 |
| CPU-0412 | P2 | L2 ECC: three double-bit syndromes decoded as single-bit correctable (found by formal) | ECO-A-002 | 2026-07-24 |
| GBUF-0133 | P2 | Bank-conflict arbiter starvation under 4-way conflicts | ECO-A-006 | 2026-08-04 |
| PCIE-1142 | P2 | AER header log overwritten on back-to-back uncorrectable errors | RTL fix before freeze | 2026-07-10 |
| SEC-0309 | P1 | AES-GCM tag compare exited early on first mismatching byte | RTL fix before freeze | 2026-07-08 |
| NOC-0271 | P2 | Router (2,1) credit-return glitch on VC switch | ECO-B-001 | 2026-08-24 |
| NPU-2248 | P2 | DMA completion-interrupt coalescing counter not cleared on channel reset | ECO-B-002 | 2026-08-25 |
| PCIE-1187 | P1 | L1.2 exit at Gen5: PHY released from P1.2 before refclk_valid (section 4.3) | ECO-C-003 | 2026-09-17 |

### 4.3 Bugs found during closure

| Bug | Priority | Found | Found by | Description | Fix | Status |
|---|---|---|---|---|---|---|
| PCIE-1187 | P1 | 2026-09-10 | New directed test l12_clkreq_tpoweron_gen5 (TB-C-001) | u_pcie0_wrap/u_l1ss_ctl released the PHY from P1.2 before refclk_valid when CLKREQ# re-asserted within 2 us of T_POWER_ON expiry at Gen5: the re-assert branch of the exit FSM restarted T_POWER_ON without clearing tpoweron_done, so the stale flag released P1.2; LTSSM went to Detect on L1.2 exit (same failure signature as ALX4100-E03) | RTL ECO-C-003: tpoweron_done cleared on CLKREQ# re-assertion; every P1.2 exit branch re-qualified with synchronized refclk_valid | Verified, closed 2026-09-17 |

Fix verification: l12_clkreq_tpoweron_gen5 passes on all 164 offset/T_POWER_ON combinations; SVA a_l1ss_p12_exit_refclk_valid passes in simulation and is fully proven by formal on u_l1ss_ctl; full PCIE0 regression and l1ss_cr_lib (600 seeds per nightly, Gen1-Gen5) are clean on kst_rtl_2026.09.17; gls_pcie0_l12_entry_exit passes on kst_top_nl_2026.09.19 at both SDF corners. 0 open P1/P2 at TRR-3.

## 5. Code coverage per block

Measured on the merged database after applying approved exclusions (section 8). Third-party encrypted IP (CPU-RV64-Q4, PCIE5-CTL, MC-LP5X) is measured at its integration wrapper and unencrypted glue; the vendors' code-coverage reports are on file.

| Block | Instance(s) | Line | Branch | Toggle | FSM state | FSM transition | Exclusions | Status |
|---|---|---|---|---|---|---|---|---|
| NPU | u_npu_c0..u_npu_c3, u_npu_top | 99.3% | 97.1% | 96.8% | 100.0% | 98.4% | CE-006 | PASS |
| GBUF | u_gbuf | 99.6% | 98.2% | 97.9% | 100.0% | 100.0% | CE-006 | PASS |
| CPU | u_cpu | 98.7% | 96.2% | 95.9% | 100.0% | 97.3% | CE-001, CE-006 | PASS |
| NOC | u_noc | 99.1% | 96.9% | 96.2% | 100.0% | 98.8% | CE-005 | PASS |
| PCIE0 | u_pcie0_wrap | 98.9% | 96.5% | 95.9% | 100.0% | 97.6% | - | PASS |
| PCIE1 | u_pcie1_wrap (PD_PCIE1 logic) | Excluded (CE-004) | Excluded (CE-004) | Excluded (CE-004) | Excluded (CE-004) | Excluded (CE-004) | CE-004 | Excluded |
| PCIE1 isolation | u_pcie1_wrap/u_pd_ctl, fuse decode | 100.0% | 100.0% | 100.0% | 100.0% | 100.0% | - | PASS |
| MEM | u_ddr_ss | 98.6% | 96.0% | 95.6% | 100.0% | 96.9% | CE-002 | PASS |
| SEC | u_sec_encl | 99.4% | 97.8% | 96.5% | 100.0% | 99.1% | - | PASS |
| AON | u_aon | 99.7% | 98.6% | 97.4% | 100.0% | 100.0% | - | PASS |
| PMUIF | u_core/u_pmu_if | 100.0% | 100.0% | 99.1% | 100.0% | 100.0% | - | PASS |
| PERIPH | u_periph | 98.8% | 96.0% | 95.7% | 100.0% | 98.1% | CE-003 | PASS |
| DBG | u_dbg, u_npu_top/u_trace_funnel | 98.4% | 95.6% | 95.4% | 100.0% | 96.2% | - | PASS |
| CRG | u_core/u_crg | 99.2% | 97.3% | 96.2% | 100.0% | 98.0% | - | PASS |
| SoC top | kst_top glue logic | 99.0% | 96.6% | 97.2% | n/a | n/a | - | PASS |

## 6. Functional coverage per covergroup

| Tier | Covergroups | At or above target | Below target |
|---|---|---|---|
| Tier-1 | 37 | 37 | 0 |
| Tier-2 | 15 | 15 | 0 |
| Tier-3 | 5 | 5 | 0 |
| Excluded (CE-004) | 4 | - | - |

| Covergroup | Tier | Bins hit/total | Coverage | Target | Status |
|---|---|---|---|---|---|
| cg_npu_dma_desc_types | Tier-1 | 188/192 | 97.9% | 95.0% | PASS |
| cg_npu_dma_ring_wrap | Tier-1 | 62/63 | 98.4% | 95.0% | PASS |
| cg_npu_sparse_decomp_zero_blk | Tier-1 | 46/47 | 97.9% | 95.0% | PASS |
| cg_npu_mac_dtypes | Tier-1 | 96/96 | 100.0% | 95.0% | PASS |
| cg_npu_tile_barrier | Tier-1 | 70/72 | 97.2% | 95.0% | PASS |
| cg_npu_sram_ecc | Tier-1 | 64/64 | 100.0% | 95.0% | PASS |
| cg_npu_sram_bank_conflict | Tier-2 | 118/128 | 92.2% | 90.0% | PASS |
| cg_npu_act_lut | Tier-2 | 57/60 | 95.0% | 90.0% | PASS |
| cg_npu_clk_gate | Tier-2 | 30/32 | 93.8% | 90.0% | PASS |
| cg_npu_trace_funnel | Tier-3 | 43/48 | 89.6% | 80.0% | PASS (non-blocking) |
| cg_gbuf_bank_arb | Tier-2 | 244/256 | 95.3% | 90.0% | PASS |
| cg_gbuf_ecc | Tier-1 | 40/40 | 100.0% | 95.0% | PASS |
| cg_noc_routing_xy | Tier-1 | 240/240 | 100.0% | 95.0% | PASS |
| cg_noc_credit_flow | Tier-1 | 78/80 | 97.5% | 95.0% | PASS |
| cg_noc_qos_arb_weights | Tier-2 | 139/152 | 91.4% | 90.0% | PASS |
| cg_noc_vc_alloc | Tier-2 | 60/64 | 93.8% | 90.0% | PASS |
| cg_noc_err_resp | Tier-1 | 36/36 | 100.0% | 95.0% | PASS |
| cg_cpu_boot_modes | Tier-1 | 24/24 | 100.0% | 95.0% | PASS |
| cg_cpu_l2_ecc | Tier-1 | 46/48 | 95.8% | 95.0% | PASS |
| cg_cpu_plic_irq | Tier-1 | 154/158 | 97.5% | 95.0% | PASS |
| cg_cpu_pmp_regions | Tier-2 | 58/64 | 90.6% | 90.0% | PASS |
| cg_cpu_debug_halt | Tier-2 | 22/24 | 91.7% | 90.0% | PASS |
| cg_mem_lp5x_training | Tier-1 | 119/120 | 99.2% | 95.0% | PASS |
| cg_mem_refresh_rfm | Tier-1 | 101/104 | 97.1% | 95.0% | PASS |
| cg_mem_dfi_lp | Tier-1 | 58/60 | 96.7% | 95.0% | PASS |
| cg_mem_ecc_scrub | Tier-2 | 29/32 | 90.6% | 90.0% | PASS |
| cg_mem_fsp_switch | Tier-2 | 34/36 | 94.4% | 90.0% | PASS |
| cg_mem_cmd_sched | Tier-2 | 211/224 | 94.2% | 90.0% | PASS |
| cg_sec_boot_flow | Tier-1 | 52/52 | 100.0% | 95.0% | PASS |
| cg_sec_key_ladder | Tier-1 | 44/45 | 97.8% | 95.0% | PASS |
| cg_sec_otp_ecc | Tier-1 | 32/32 | 100.0% | 95.0% | PASS |
| cg_sec_crypto_modes | Tier-1 | 87/90 | 96.7% | 95.0% | PASS |
| cg_sec_lifecycle | Tier-1 | 20/20 | 100.0% | 95.0% | PASS |
| cg_sec_trng_health | Tier-2 | 19/20 | 95.0% | 90.0% | PASS |
| cg_aon_pwr_state_trans | Tier-1 | 39/39 | 100.0% | 95.0% | PASS |
| cg_aon_wake_sources | Tier-1 | 46/48 | 95.8% | 95.0% | PASS |
| cg_aon_fuse_shadow_load | Tier-1 | 28/28 | 100.0% | 95.0% | PASS |
| cg_aon_rtc_timer | Tier-3 | 21/24 | 87.5% | 80.0% | PASS (non-blocking) |
| cg_pcie0_ltssm | Tier-1 | 403/417 | 96.6% | 95.0% | PASS |
| cg_pcie0_tlp_types | Tier-1 | 184/186 | 98.9% | 95.0% | PASS |
| cg_pcie0_aer | Tier-1 | 61/62 | 98.4% | 95.0% | PASS |
| cg_pcie0_eq_presets | Tier-1 | 98/99 | 99.0% | 95.0% | PASS |
| cg_pcie0_aspm_l1 | Tier-1 | 42/43 | 97.7% | 95.0% | PASS |
| cg_pcie0_l11_entry_exit | Tier-1 | 41/42 | 97.6% | 95.0% | PASS |
| cg_pcie0_l12_entry_exit | Tier-1 | 120/124 | 96.8% | 95.0% | PASS |
| cg_pcie0_reset_flr | Tier-1 | 30/30 | 100.0% | 95.0% | PASS |
| cg_pcie0_msix_sriov | Tier-2 | 88/96 | 91.7% | 90.0% | PASS |
| cg_pcie1_ltssm | Excluded | 0/398 | 0.0% | Excluded (CE-004) | Excluded (CE-004) |
| cg_pcie1_tlp_types | Excluded | 0/186 | 0.0% | Excluded (CE-004) | Excluded (CE-004) |
| cg_pcie1_l1ss | Excluded | 0/96 | 0.0% | Excluded (CE-004) | Excluded (CE-004) |
| cg_pcie1_cxl_io | Excluded | 0/74 | 0.0% | Excluded (CE-004) | Excluded (CE-004) |
| cg_pcie1_fuse_isolation | Tier-1 | 36/36 | 100.0% | 95.0% | PASS |
| cg_i2c_clk_stretch | Tier-1 | 24/24 | 100.0% | 95.0% | PASS |
| cg_i2c_smbus_proto | Tier-2 | 51/54 | 94.4% | 90.0% | PASS |
| cg_qspi_boot_read | Tier-1 | 36/36 | 100.0% | 95.0% | PASS |
| cg_spi_modes | Tier-3 | 28/32 | 87.5% | 80.0% | PASS (non-blocking) |
| cg_uart_fifo_baud | Tier-3 | 29/30 | 96.7% | 95.0% (E11 integration hold, KST-VPLAN-010 section 4.3) | PASS |
| cg_gpio_irq | Tier-2 | 44/48 | 91.7% | 90.0% | PASS |
| cg_crg_reset_seq | Tier-1 | 34/34 | 100.0% | 95.0% | PASS |
| cg_crg_pll_lock | Tier-1 | 27/28 | 96.4% | 95.0% | PASS |
| cg_dbg_jtag_tap | Tier-3 | 38/44 | 86.4% | 80.0% | PASS (non-blocking) |

## 7. Uncovered bins

### 7.1 cg_pcie0_l12_entry_exit

4 of 124 bins uncovered (120/124 = 96.8%) after TB-C-001. PCIE0 coverage was re-collected from scratch on kst_rtl_2026.09.17 after the ECO-C-003 RTL change to u_l1ss_ctl.

| Bin | Coverpoint / cross | Hits | Closure plan | Owner |
|---|---|---|---|---|
| pci_pm_d3hot_x_ep_wake | cx_entry_x_exit | 0 | Target met; D3hot exit on endpoint wake needs PME sequencing in the host VIP, scheduled post-TRR (non-blocking) | Tomasz Wierzbicki |
| tpoweron_130us_x_perst_assert | cx_tpoweron_x_exit | 0 | Target met; directed variant scheduled post-TRR (non-blocking) | Leo Brandt |
| perst_assert__gen1 | cx_exit_trigger_x_rate | 0 | Target met; hit in the package-B database; PCIE0 coverage was reset after the ECO-C-003 RTL change to u_l1ss_ctl; l12_perst_in_l12 draws its link rate per seed (Gen1/Gen2) and the three post-ECO nightlies (2026-09-19..21) all drew Gen2; l1ss_cr_lib weights perst_assert low because PERST# ends the residency; fixed-rate Gen1 run scheduled post-TRR (non-blocking) | Leo Brandt |
| b2b_entry_lt_10us__gen3 | cx_b2b_x_rate | 0 | Target met; Gen3 variant of l12_b2b_entry scheduled post-TRR (non-blocking) | Leo Brandt |

### 7.2 Other covergroups below 100%

All covergroups in this table are at or above their tier target; uncovered bins are tracked in the closure plan (Tier-3 non-blocking).

| Covergroup | Tier | Uncovered | Uncovered bins |
|---|---|---|---|
| cg_npu_dma_desc_types | Tier-1 | 4 | desc_3d_neg_stride__ch13, sg_chain_max_len__ch15, desc_2d_unaligned_63b__ch11, chain_1d_to_3d__size_4k_m1 |
| cg_npu_dma_ring_wrap | Tier-1 | 1 | ring_4096__prefetch_8__outst_16 |
| cg_npu_sparse_decomp_zero_blk | Tier-1 | 1 | zero_blk_b2b_4__fmt_bitmap__row_end |
| cg_npu_tile_barrier | Tier-1 | 2 | xcluster_all16_abort_simul, barrier_timeout_during_abort |
| cg_npu_sram_bank_conflict | Tier-2 | 10 | 3-way MAC/DMA/decompressor conflict on banks 12-15 at both priorities (8); dma_vs_scrub__bank7, dma_vs_scrub__bank15 |
| cg_npu_act_lut | Tier-2 | 3 | gelu_seg31_reload_on_idle_exit, silu_seg0_underflow, sigmoid_seg31_sat |
| cg_npu_clk_gate | Tier-2 | 2 | gate_with_outst_dma_max, wake_latency_max__tile3 |
| cg_npu_trace_funnel | Tier-3 | 5 | src_sel_x_overflow for trace sources 0-3 (4); mc4_capture_b2b |
| cg_gbuf_bank_arb | Tier-2 | 12 | 4-way conflict with PCIe requester on banks 24-31 (8); CPU+PCIe+DMA 3-way on banks 0-3 (4) |
| cg_noc_credit_flow | Tier-1 | 2 | credit_zero_stall__port_L__vc3, credit_return_at_zero__port_E__vc3 |
| cg_noc_qos_arb_weights | Tier-2 | 13 | w0 (starvation guard) x VC3 x 4-5 contending inputs (4); w15 x VC2/VC3 x 5 contending inputs on output ports N/S/L (6); weight update during active arbitration on VC3 (3) |
| cg_noc_vc_alloc | Tier-2 | 4 | vc3_to_vc0_remap at routers (0,0), (0,3), (3,0), (3,3) |
| cg_cpu_l2_ecc | Tier-1 | 2 | dbl_err_way7_during_scrub, sgl_err_way3_evict_same_cycle |
| cg_cpu_plic_irq | Tier-1 | 4 | claim_during_threshold_change__hart3, nested_pri7_x_src31, complete_wrong_id__hart2, pending_clear_race__src27 |
| cg_cpu_pmp_regions | Tier-2 | 6 | NA4 locked regions 12-15 with X-only permission (4); TOR region 0 locked with base 0 (2) |
| cg_cpu_debug_halt | Tier-2 | 2 | halt_during_wfi__hart3, step_over_ecall__hart1 |
| cg_mem_lp5x_training | Tier-1 | 1 | wdq_train__fsp1__ch2__abort_by_refresh |
| cg_mem_refresh_rfm | Tier-1 | 3 | rfm_raammt_x_pb_refresh_postponed_8, pulled_in_8__fsp1, mr4_derate_step_0p25x_to_4x |
| cg_mem_dfi_lp | Tier-1 | 2 | dfi_lp_data_abort__ch3, lp_wakeup_max_during_ctrl_lp__ch1 |
| cg_mem_ecc_scrub | Tier-2 | 3 | scrub_rate_max_x_2bit_inject__ch0..ch2 (3) |
| cg_mem_fsp_switch | Tier-2 | 2 | fsp_switch_during_rfm__ch1, dvfsc_exit_with_pending_refresh__ch3 |
| cg_mem_cmd_sched | Tier-2 | 13 | bank-group starvation limit x 4 channels x write-heavy mix (8); tWTR_L-max turnaround with close-page policy (5) |
| cg_sec_key_ladder | Tier-1 | 1 | derive_lvl3_x_zeroize_during_derive |
| cg_sec_crypto_modes | Tier-1 | 3 | gcm_aad_len_max_x_payload_0, ecdsa_verify_fail_x_pka_abort, sha384_len_65535 |
| cg_sec_trng_health | Tier-2 | 1 | adaptive_prop_fail_x_reseed |
| cg_aon_wake_sources | Tier-1 | 2 | smbus_alert__sleep__simul_gpio, timer__sleep__simul_smbus_alert |
| cg_aon_rtc_timer | Tier-3 | 3 | alarm_at_rollover, alarm_write_during_tick, rollover_x_sleep_entry |
| cg_pcie0_ltssm | Tier-1 | 14 | Loopback follower at Gen4/Gen5 x8/x4 (4); Recovery.Speed Gen5 -> Gen2 on EQ failure (2); Disabled from Recovery at Gen3-Gen5 (3); Hot Reset from Recovery.Idle at Gen2-Gen5 (4); Polling.Compliance via Enter_Compliance at x1 (1) |
| cg_pcie0_tlp_types | Tier-1 | 2 | atomic_cas_128b__tc7, msg_vendor_type1__ro_ido |
| cg_pcie0_aer | Tier-1 | 1 | surprise_down__header_log_overflow |
| cg_pcie0_eq_presets | Tier-1 | 1 | gen5_phase3_preset_p10_reject |
| cg_pcie0_aspm_l1 | Tier-1 | 1 | l0s_exit_during_l1_entry__gen5 |
| cg_pcie0_l11_entry_exit | Tier-1 | 1 | l11_exit_by_perst__gen5 |
| cg_pcie0_msix_sriov | Tier-2 | 8 | VF5-VF8 MSI-X mask/unmask during VF FLR (8) |
| cg_i2c_smbus_proto | Tier-2 | 3 | arp_reset_during_block_read, pec_err_x_block_write_32b, alert_during_arp |
| cg_spi_modes | Tier-3 | 4 | cpol1_cpha1_x_cs_hold_max, fifo_full_x_cs_deassert (x3 lengths) |
| cg_uart_fifo_baud | Tier-3 | 1 | div_1_x_fifo_trig_14 |
| cg_gpio_irq | Tier-2 | 4 | both_edge_x_debounce_max on GPIO_B/GPIO_C (4) |
| cg_crg_pll_lock | Tier-1 | 1 | ssc_on_relock_during_freq_change__pll_npu |
| cg_dbg_jtag_tap | Tier-3 | 6 | bypass_chain_len_max, idcode_x_lc_rma, user instr 0x1A-0x1D (4) |

## 8. Coverage exclusions

All exclusions satisfy CHK-VER-05: the excluded logic is unreachable in ALX-5100 and ALX-5100I (same die and fuse map; fused off or tied off), the fuse/tie-off/isolation logic is verified to >= 95%, and each record is signed by the Verification Lead and the Chief Architect.

| ID | Scope | Reason (unreachable in ALX-5100/ALX-5100I) | Isolation / tie-off verification | Verification Lead | Chief Architect | Date | Status |
|---|---|---|---|---|---|---|---|
| CE-001 | CPU debug-ROM patch slots 8-15 (u_cpu), code coverage | Patch-enable inputs of slots 8-15 tied off to 0 at CPU integration; slots unused | Formal constant proof on the tie-off (0 CEX); tie cells checked in LEC | Tomasz Wierzbicki | Priya Raghavan | 2026-07-09 | Approved |
| CE-002 | LPDDR4X legacy-mode logic in u_ddr_ss/u_mc0..u_mc3, code coverage | Memory-type strap tied off to LPDDR5X in the u_ddr_ss wrapper | Formal proof lp4x_mode == 0; cg_mem_lp5x_training at target | Tomasz Wierzbicki | Priya Raghavan | 2026-07-09 | Approved |
| CE-003 | UART0 IrDA SIR encoder/decoder (u_periph/u_uart0), code coverage | irda_en tied off to 0 at integration; no IrDA pins in the ball map | Formal constant proof (0 CEX) | Tomasz Wierzbicki | Priya Raghavan | 2026-07-14 | Approved |
| CE-004 | u_pcie1_wrap (all PD_PCIE1 logic), code coverage; cg_pcie1_ltssm, cg_pcie1_tlp_types, cg_pcie1_l1ss, cg_pcie1_cxl_io | PCIE1 fused off in ALX-5100 and ALX-5100I (FUSE_PCIE1_DIS=1; same fuse map): PD_PCIE1 power-gated, pcie1_core_clk gated, outputs clamped by isolation cells; reserved for ALX-5100X | cg_pcie1_fuse_isolation 100.0%; formal clamp proof 214/214 properties | Tomasz Wierzbicki | Priya Raghavan | 2026-07-21 | Approved |
| CE-005 | u_noc router ports facing the mesh edge (16 ports), code and functional coverage | Ports tied off by the NoC generator configuration (no link) | Formal proof that edge-port valid and credit inputs are constant; cg_noc_routing_xy 100.0% | Tomasz Wierzbicki | Priya Raghavan | 2026-07-17 | Approved |
| CE-006 | MBIST-only test-mux legs of SRAM wrappers (NPU tile SRAM, GBUF banks, CPU L2), code and functional coverage | Excluded from functional-simulation coverage only: the mux legs are exercised by MBIST pattern simulation (mbist runs, 3,412/3,412 instances) under CHK-DFT-02 and at ATE; in the shipped SKU (PRODUCTION lifecycle) the test-mux select is forced inactive by the lifecycle fuse gate | Formal proof mbist_sel == 0 when lc_state == PRODUCTION; mux legs verified by MBIST pattern simulation (CHK-DFT-02) | Tomasz Wierzbicki | Priya Raghavan | 2026-07-24 | Approved |

## 9. Coverage waivers

Waivers follow KST-VPLAN-010 section 8.2 (risk assessment; signatures of the Verification Lead and the Chief Architect before the TRR at which the waiver is used).

No coverage waivers are in effect for TRR-3. CW-PCIE-003 was withdrawn after cg_pcie0_l12_entry_exit reached target.

| ID | Covergroup | Requested | Requested by | Rationale | Approver(s) | Status |
|---|---|---|---|---|---|---|
| CW-PCIE-001 | cg_pcie0_eq_presets | 2026-05-29 | Leo Brandt | Gen5 phase-3 preset bins pending host VIP update (RTL-freeze milestone only) | Tomasz Wierzbicki, Priya Raghavan | Closed 2026-06-26 (target met) |
| CW-PCIE-002 | cg_pcie0_msix_sriov | 2026-06-05 | Leo Brandt | VF MSI-X bins pending SR-IOV sequence library (RTL-freeze milestone only) | Tomasz Wierzbicki, Priya Raghavan | Closed 2026-07-10 (target met) |
| CW-PCIE-003 | cg_pcie0_l12_entry_exit (91.1% at request) | 2026-09-02 | Leo Brandt | remaining bins are Gen5 corner cases; to be covered in post-silicon validation | Tomasz Wierzbicki (Verification Lead), Priya Raghavan (Chief Architect): not signed | Rejected 2026-09-08 (TRR-2 AI-12); request record closed 2026-09-22: Withdrawn by requester (target met) |

## 10. Gate-level simulation

Netlist kst_top_nl_2026.09.19; SDF from the sign-off STA tool; runs 2026-09-20 .. 2026-09-21. Timing checks enabled on all sequential cells; X-propagation monitored. This suite is the affected-block GLS set of CHK-GOV-02 and is run on the final netlist of each package, after its last ECO, rather than per change; every netlist ECO in KST-ECO-062 maps to at least one test (NoC, GBUF and NPU datapath: gls_warm_reset and gls_npu_smoke; CPU L2 and PLIC: gls_por_qspi_boot and gls_wdt_reset; boot, reset, security and low-power logic: the remaining tests).

| Test | Scenario | Min SDF (ff_0p825v_m40c_cbest_ccbest) | Max SDF (ss_0p675v_m40c_cworst_ccworst) |
|---|---|---|---|
| gls_por_qspi_boot | POR, fuse-shadow load, boot ROM to BL1 fetch with u_keyldr key_load_done forced by the testbench (key ladder covered by gls_secure_boot_auth), QSPI0 1-1-4 SDR read of BL1 | PASS | PASS |
| gls_secure_boot_auth | Root-key load from the OTP model, ECDSA P-384 verification of BL1 | PASS | PASS |
| gls_warm_reset | Warm reset under NoC and NPU traffic | PASS | PASS |
| gls_wdt_reset | Watchdog-expiry reset | PASS | PASS |
| gls_lp_idle_entry_exit | ACTIVE -> LP-IDLE -> ACTIVE, timer wake | PASS | PASS |
| gls_sleep_gpio_wake | ACTIVE -> SLEEP -> ACTIVE, GPIO wake | PASS | PASS |
| gls_pcie0_l12_entry_exit | L1.2 entry/exit: host CLKREQ# exit and CLKREQ# re-assert during T_POWER_ON (PCIE-1187 scenario), Gen1 PIPE model | PASS | PASS |
| gls_ddr_init | LPDDR5X init and training with the PHY simulation model | PASS | PASS |
| gls_npu_smoke | Single-tile INT8 GEMM smoke | PASS | PASS |

## 11. Formal verification summary

| Target | Instance | Properties | Proven | Bounded | Failing |
|---|---|---|---|---|---|
| PMU power-state FSM | u_aon/u_pmu | 64 | 64 | 0 | 0 |
| L1 PM substates sequencer (incl. a_l1ss_p12_exit_refclk_valid) | u_pcie0_wrap/u_l1ss_ctl | 49 | 46 (incl. a_l1ss_p12_exit_refclk_valid, full proof) | 3 (depth 120, timer counters abstracted): T_COMMONMODE and LTR entry-timer properties, re-run on kst_rtl_2026.09.17; bound as in rev A | 0 |
| Security lifecycle FSM | u_sec_encl/u_lc_ctl | 36 | 36 | 0 | 0 |
| Fuse-shadow load | u_aon/u_fuse_shadow | 22 | 22 | 0 | 0 |
| Reset sequencer | u_core/u_crg | 30 | 30 | 0 | 0 |
| NoC credit counters | u_noc | 128 | 128 | 0 | 0 |
| CPU L2 ECC decode | u_cpu/u_l2/u_ecc_dec | 18 | 18 | 0 | 0 |
| NPU DMA ring pointers | u_npu_cN/u_dma | 40 | 40 | 0 | 0 |
| PCIE1 isolation | u_pcie1_wrap/u_pd_ctl | 214 | 214 | 0 | 0 |
| Clock-gating equivalence | All partitions (sequential equivalence) | 1,862 | 1,862 | 0 | 0 |

## 12. Open items

| ID | Item | Owner | Due |
|---|---|---|---|
| OI-1 | cg_pcie0_l12_entry_exit: 4 remaining bins, directed runs (non-blocking, target met) | Leo Brandt | Post-TRR |
| OI-2 | Tier-3 closure (non-blocking) | Tomasz Wierzbicki | Post-TRR |

## 13. Sign-off

| Item | Signatory | Status | Date |
|---|---|---|---|
| Code coverage (CHK-VER-01) | Tomasz Wierzbicki | Signed | 2026-09-23 |
| Functional coverage (CHK-VER-02) | Tomasz Wierzbicki | Signed | 2026-09-23 |
| Bug database and regression (CHK-VER-03, CHK-VER-04) | Tomasz Wierzbicki | Signed | 2026-09-23 |
| Coverage exclusions (CHK-VER-05) | Tomasz Wierzbicki, Priya Raghavan | Signed | Per record (section 8) |
| Gate-level simulation (CHK-VER-06) | Tomasz Wierzbicki | Signed | 2026-09-23 |

## Revision history

| Rev | Date | Author | Change |
|---|---|---|---|
| A | 2026-08-12 | Tomasz Wierzbicki | Released for TRR-1 (RTL kst_rtl_2026.08.06, netlist kst_top_nl_2026.08.07) |
| B | 2026-09-02 | Tomasz Wierzbicki | TB-B-001 L1.2 tests; L1.2 71.0% -> 91.1%; CW-PCIE-003 requested; coverage databases reset and re-collected on kst_rtl_2026.08.28 for every block with an RTL change: MEM (ECO-B-004, MC-LP5X / PHY-LP5X-N5 v2.7.0 models), NOC (ECO-B-001, u_noc/u_rtr_2_1), NPU (ECO-B-002), PMUIF (ECO-B-005) and PERIPH/I2C0 (ECO-B-006), re-collected with deltas <= 0.2 points, all blocks at target; regression, bug DB and GLS refreshed for kst_top_nl_2026.08.31 |
| C | 2026-09-23 | Tomasz Wierzbicki | TB-C-001; L1.2 96.8%; PCIE-1187 found/fixed (ECO-C-003); CW-PCIE-003 withdrawn; regression, bug DB and GLS refreshed for kst_top_nl_2026.09.19 |
