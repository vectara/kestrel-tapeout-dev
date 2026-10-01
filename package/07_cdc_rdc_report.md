# KESTREL (ALX-5100) CDC / RDC Sign-off Report

| Field | Value |
|---|---|
| Doc ID | KST-CDC-030 |
| Title | CDC / RDC Sign-off Report |
| Revision | A |
| Date | 2026-08-12 |
| Owner | Hiroshi Tanabe (CDC/RDC Owner) |
| Status | Released for TRR-1 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Purpose and scope

This report records clock-domain-crossing (CDC) and reset-domain-crossing (RDC) sign-off for the full KESTREL chip (`kst_top`) on netlist **kst_top_nl_2026.08.07**, for TRR-1 (2026-08-14). Rules: ALD-QA-CHK-007 rev 7.2, CHK-CDC-01 to CHK-CDC-06. Clock plan and power states: KST-ARCH-001. Synchronous paths inside a clock group: KST-STA-020.

Hard macros (PCIe PHY, LPDDR5X controller and PHY, PLLs, OTP) use vendor CDC abstract models at the KST-IPBOM-050 versions for this package. PCIE1 (`u_pcie1_wrap`) is fused off (`FUSE_PCIE1_DIS=1`) but present in silicon, so its crossings are analyzed like any other block.

## 2. Sign-off summary

**Result: 1,284 crossings; 1,241 clean; 43 waived; 0 unwaived.** Reset-domain analysis: 318 RDC paths, 0 unwaived. CDC/RDC status for TRR-1: **GREEN**.

| Rule | Requirement | Result | Status |
|---|---|---|---|
| CHK-CDC-01 | 100% of crossings classified; 0 unwaived violations | 1,284 of 1,284 classified; 0 unwaived | PASS |
| CHK-CDC-02 | 2-FF for destination <= 800 MHz, 3-FF for destination > 800 MHz; MTBF >= 1,000 years per synchronizer | 0 depth violations; worst synchronizer MTBF 5.2E+11 years (Section 8) | PASS |
| CHK-CDC-03 | Multi-bit via gray code, req/ack handshake or async FIFO | 0 through independent synchronizers; others ASYNC_FIFO, HANDSHAKE, GRAY_CNT or quasi-static under CHK-CDC-04 waivers | PASS |
| CHK-CDC-04 | Quasi-static only for level signals with documented stability; never for pulses | 37 quasi-static waivers; 0 crossings declared pulse without PULSE_SYNC or HANDSHAKE | PASS |
| CHK-CDC-05 | RDC: async assert, sync de-assert; 0 unwaived RDC violations | 0 unsynchronized de-assertions; 0 unwaived RDC violations | PASS |
| CHK-CDC-06 | Waivers approved by CDC Owner and block owner | 43 of 43 active waivers carry both approvals | PASS |

## 3. Tool setup and methodology

### 3.1 Tools and inputs

| Item | Value |
|---|---|
| Design / netlist | `kst_top`, kst_top_nl_2026.08.07; runs 2026-08-09 .. 2026-08-10 |
| Structural CDC tool | Clock/reset inference, synchronizer recognition, reconvergence, glitch and logic-before-synchronizer checks |
| Formal CDC/RDC tool | Handshake protocol, gray-code and pulse-spacing properties, stability SVAs, reset ordering, RDC |
| Logic simulator | Metastability-injection simulation (random 0/1-cycle delay on every recognized synchronizer): 214 SoC tests, 0 failures |
| Constraints | `KST_func.sdc` r4.2 (as KST-STA-020); CDC intent `kst_cdc_intent.tcl` (clock groups, declared classes, reset ordering); waiver DB `kst_cdc_waivers` |
| Synchronizer cells | SYNC2_X2, SYNC3_X2, RSTSYNC2_X2, RSTSYNC3_X2 (STDCELL-N5-H210), tau/T0 characterized at all six PVT corners |

### 3.2 Analysis modes

| Mode | Setup | Purpose |
|---|---|---|
| MISSION | All PLL clocks at maximum frequency; test_mode=0 | Primary sign-off |
| LP-IDLE | core_clk = PLL_CORE/64 (15.625 MHz), npu_clk gated, PCIe in L1.2 | Power-state paths; pulse width vs destination period on declared pulse crossings |
| TEST | scan_mode=1, test_mode=1, tck active, OCC controllers active | JTAG TDR and test-static crossings |

### 3.3 Synchronizer and classification rules

- Crossings are counted per source-register-to-destination-register group (a bus is one crossing). Each carries a designer-declared class from the CDC intent file, checked by the tools against the structure found.
- Depth per CHK-CDC-02: SYNC3_X2 into core_clk, npu_clk, cpu_clk, mc_clk, pcie_core_clk, pcie1_core_clk; SYNC2_X2 into aon_clk, pcie_aux_clk, sec_clk, periph_clk, tck. Internal synchronizers of ASYNC_FIFO, HANDSHAKE, GRAY_CNT and PULSE_SYNC follow the same rule.
- Multi-bit crossings (CHK-CDC-03) use ASYNC_FIFO, HANDSHAKE or GRAY_CNT. Independent status bits synchronized one by one are declared `level` per bit; if they meet again in one register they are reported as reconvergence.
- Quasi-static waivers (CHK-CDC-04) must state the stability guarantee: reset-held destination, POR/boot-time write, SW programming rule or SVA/formal proof. Each waiver records the declared signal class (ALD-QA-CHK-007 section 7).
- Waivers are approved by the CDC Owner and the block owner (DFT Lead for test-mode crossings), per CHK-CDC-06; for fuse-shadow and strap sources into u_core infrastructure (u_crg, u_sysctl, u_pvt_ctl) the block owner is the AON/PMU Owner, who owns the fuse-shadow load and core_rst_n release timing. Waiver IDs are assigned at first triage; Section 7 dates are the formal request and approval dates.

## 4. Clock domains

| Clock | Frequency | Period (ns) | Source | Clock group | Sync depth as destination |
|---|---|---|---|---|---|
| xtal_clk | 25.000 MHz | 40.000 | Board 25 MHz crystal | G_REF | 2-FF |
| aon_clk | 25.000 MHz | 40.000 | xtal_clk (always-on) | G_REF | 2-FF |
| pcie_aux_clk | 25.000 MHz | 40.000 | aon_clk | G_REF | 2-FF |
| core_clk | 1000.0 MHz (LP-IDLE 15.625 MHz) | 1.000 (LP-IDLE 64.000) | PLL_CORE (LP-IDLE: /64) | G_CORE | 3-FF |
| sec_clk | 500.0 MHz | 2.000 | PLL_CORE/2 | G_CORE | 2-FF |
| periph_clk | 200.0 MHz | 5.000 | PLL_CORE/5 | G_CORE | 2-FF |
| npu_clk | 1200.0 MHz | 0.833 | PLL_NPU | G_NPU | 3-FF |
| cpu_clk | 1500.0 MHz | 0.667 | PLL_CPU | G_CPU | 3-FF |
| mc_clk | 1066.7 MHz | 0.938 | PLL_DDR | G_DDR | 3-FF |
| pcie_core_clk | 1000.0 MHz | 1.000 | PCIe PHY PLL (100 MHz host REFCLK) | G_PCIE | 3-FF |
| tck | 50.0 MHz | 20.000 | JTAG pad (test/debug) | G_TCK | 2-FF |

Clocks in one group are synchronous and timed by the sign-off STA tool (KST-STA-020), not by CDC: core_clk, sec_clk and periph_clk come from PLL_CORE; aon_clk and pcie_aux_clk from xtal_clk. All inter-group pairs are asynchronous, including each PLL against its reference. pcie1_core_clk (gated, PD_PCIE1) is its own group. scan_clk (200.0 MHz shift) and OCC test clocks exist only in TEST mode.

## 5. Crossing summary

### 5.1 By clock-domain pair

Unwaived crossings: 0 in every pair.

| Source -> destination | Crossings | Clean | Waived |
|---|---|---|---|
| core_clk -> npu_clk | 142 | 138 | 4 |
| npu_clk -> core_clk | 128 | 126 | 2 |
| core_clk -> cpu_clk | 61 | 61 | 0 |
| cpu_clk -> core_clk | 57 | 57 | 0 |
| core_clk -> mc_clk | 118 | 115 | 3 |
| mc_clk -> core_clk | 104 | 103 | 1 |
| core_clk -> pcie_core_clk | 96 | 94 | 2 |
| pcie_core_clk -> core_clk | 102 | 100 | 2 |
| core_clk -> pcie1_core_clk | 58 | 58 | 0 |
| pcie1_core_clk -> core_clk | 61 | 61 | 0 |
| pcie_core_clk -> pcie_aux_clk | 17 | 17 | 0 |
| pcie_aux_clk -> pcie_core_clk | 15 | 15 | 0 |
| aon_clk -> core_clk | 46 | 41 | 5 |
| core_clk -> aon_clk | 27 | 27 | 0 |
| aon_clk -> npu_clk | 9 | 7 | 2 |
| aon_clk -> cpu_clk | 3 | 3 | 0 |
| aon_clk -> mc_clk | 8 | 6 | 2 |
| aon_clk -> pcie_core_clk | 7 | 5 | 2 |
| aon_clk -> pcie1_core_clk | 2 | 1 | 1 |
| aon_clk -> sec_clk | 12 | 10 | 2 |
| aon_clk -> periph_clk | 9 | 7 | 2 |
| aon_clk -> tck | 2 | 1 | 1 |
| tck -> core_clk | 21 | 17 | 4 |
| tck -> npu_clk | 11 | 9 | 2 |
| tck -> cpu_clk | 9 | 8 | 1 |
| tck -> mc_clk | 4 | 3 | 1 |
| tck -> sec_clk | 3 | 3 | 0 |
| tck -> periph_clk | 3 | 2 | 1 |
| core_clk / npu_clk / cpu_clk -> tck | 14 | 14 | 0 |
| async (pads, PHY, PLL lock, ring osc) -> all domains | 135 | 132 | 3 |
| **Total** | **1,284** | **1,241** | **43** |

### 5.2 By synchronization scheme

| Scheme | Crossings | Clean | Waived | Notes |
|---|---|---|---|---|
| ASYNC_FIFO | 212 | 212 | 0 | Gray-coded pointers; gray property formally proven |
| HANDSHAKE | 187 | 187 | 0 | 4-phase req/ack; data held from req to ack (formal proof) |
| PULSE_SYNC | 64 | 64 | 0 | Source toggle + N-FF + edge detect; event spacing formally checked |
| GRAY_CNT | 23 | 23 | 0 | Hamming distance 1 per update (formal) |
| RESET_SYNC | 58 | 58 | 0 | RSTSYNC2_X2 / RSTSYNC3_X2 |
| SYNC_3FF | 486 | 481 | 5 | SYNC3_X2, destinations > 800 MHz; 5 reconvergence waivers |
| SYNC_2FF | 217 | 216 | 1 | SYNC2_X2, destinations <= 800 MHz; 1 reconvergence waiver |
| None (quasi-static) | 37 | 0 | 37 | Declared quasi_static; waiver required |
| **Total** | **1,284** | **1,241** | **43** | 37 quasi-static + 6 reconvergence waivers |

## 6. Top-level crossing groups

CDC-0101 to CDC-0160 are the top-level inter-block crossing groups (CDC-0150 is the LP-IDLE entry request, /1 -> /64, only; the exit walk is started by u_core/u_pmu_if on wake_pending_q, KST-ARCH-001 section 9.4); `{0..3}` marks a group replicated per cluster, channel or hart (Width is per instance). The full list is in `kst_cdc_crossings.csv`.

| ID | Source (instance, clock) | Destination (instance, clock) | Width | Designer-declared class | Sync scheme | Rule | Status |
|---|---|---|---|---|---|---|---|
| CDC-0101 | u_noc/u_ni_npu{0..3}/u_afifo_tx (core_clk) | u_npu_c{0..3}/u_nbr/u_afifo_rx (npu_clk) | 580 | fifo | ASYNC_FIFO | CDC_FIFO_OK | Clean |
| CDC-0102 | u_npu_c{0..3}/u_nbr/u_afifo_tx (npu_clk) | u_noc/u_ni_npu{0..3}/u_afifo_rx (core_clk) | 580 | fifo | ASYNC_FIFO | CDC_FIFO_OK | Clean |
| CDC-0103 | u_npu_c{0..3}/u_dma/done_irq_q (npu_clk) | u_cpu/u_plic/u_psync_npu{0..3} (core_clk) | 1 | pulse | PULSE_SYNC | CDC_PSYNC_OK | Clean |
| CDC-0104 | u_npu_c{0..3}/u_dma/err_irq_q (npu_clk) | u_cpu/u_plic/u_psync_npuerr{0..3} (core_clk) | 1 | pulse | PULSE_SYNC | CDC_PSYNC_OK | Clean |
| CDC-0105 | u_core/u_npu_csr/u_apb_brg req/addr/wdata (core_clk) | u_npu_c{0..3}/u_ctl/u_apb_brg (npu_clk) | 45 | bus | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0106 | u_core/u_crg/npu_clk_en_q (core_clk) | u_npu_c{0..3}/u_cgc/en_sync_q (npu_clk) | 1 | level | SYNC_3FF | CDC_SYNC_OK | Clean |
| CDC-0107 | u_npu_top/u_tstamp/ts_gray_q[31:0] (npu_clk) | u_core/u_dbg_ts/ts_sync_q[31:0] (core_clk) | 32 | gray | GRAY_CNT | CDC_GRAY_OK | Clean |
| CDC-0108 | u_npu_top/u_trace_funnel/tf_ovf_q (npu_clk) | u_dbg/u_trace_ctl/ovf_sts_q (tck) | 1 | level | SYNC_2FF | CDC_SYNC_OK | Clean |
| CDC-0109 | u_dbg/u_tap/tdr_trace_en_q (tck) | u_npu_top/u_trace_funnel/tf_en_sync_q (npu_clk) | 1 | level | SYNC_3FF | CDC_SYNC_OK | Clean |
| CDC-0110 | u_dbg/u_tap/tdr_trace_cfg_q[15:0] (tck) | u_npu_top/u_trace_funnel/cfg_q[15:0] (npu_clk) | 16 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-007) |
| CDC-0111 | u_cpu/u_biu/u_afifo_tx (cpu_clk) | u_noc/u_ni_cpu/u_afifo_rx (core_clk) | 580 | fifo | ASYNC_FIFO | CDC_FIFO_OK | Clean |
| CDC-0112 | u_aon/u_fuse_shadow/fuse_cfg_q[31:0] (aon_clk) | u_core/u_crg/pll_cfg_q[31:0] (core_clk) | 32 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-009) |
| CDC-0113 | u_noc/u_ni_cpu/u_afifo_tx (core_clk) | u_cpu/u_biu/u_afifo_rx (cpu_clk) | 580 | fifo | ASYNC_FIFO | CDC_FIFO_OK | Clean |
| CDC-0114 | u_cpu/u_plic/eip_q[3:0] (core_clk) | u_cpu/u_hart{0..3}/meip_sync_q (cpu_clk) | 4 x 1 | level | SYNC_3FF | CDC_SYNC_OK | Clean |
| CDC-0115 | u_aon/u_rtc/mtime_gray_q[63:0] (aon_clk) | u_cpu/u_clint/mtime_q[63:0] (cpu_clk) | 64 | gray | GRAY_CNT | CDC_GRAY_OK | Clean |
| CDC-0116 | u_dbg/u_dtm/dmi_req_q[40:0] (tck) | u_cpu/u_dm/dmi_req_q[40:0] (cpu_clk) | 41 | bus | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0117 | u_cpu/u_dm/dmi_rsp_q[33:0] (cpu_clk) | u_dbg/u_dtm/dmi_rsp_q[33:0] (tck) | 34 | bus | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0118 | u_cpu/u_hart{0..3}/halted_q (cpu_clk) | u_dbg/u_dtm/halt_sts_q[3:0] (tck) | 4 x 1 | level | SYNC_2FF | CDC_SYNC_OK | Clean |
| CDC-0119 | u_noc/u_ni_mc{0..3}/u_afifo_tx (core_clk) | u_ddr_ss/u_mc{0..3}/u_afifo_rx (mc_clk) | 612 | fifo | ASYNC_FIFO | CDC_FIFO_OK | Clean |
| CDC-0120 | u_ddr_ss/u_mc{0..3}/u_afifo_tx (mc_clk) | u_noc/u_ni_mc{0..3}/u_afifo_rx (core_clk) | 588 | fifo | ASYNC_FIFO | CDC_FIFO_OK | Clean |
| CDC-0121 | u_core/u_mc_csr/dram_tmg_q[255:0] (core_clk) | u_ddr_ss/u_mc{0..3}/tmg_q[255:0] (mc_clk) | 256 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-014) |
| CDC-0122 | u_ddr_ss/u_mc{0..3}/init_done_q (mc_clk) | u_core/u_mc_csr/init_done_sync_q (core_clk) | 1 | level | SYNC_3FF | CDC_SYNC_OK | Clean |
| CDC-0123 | u_ddr_ss/u_mc{0..3}/ecc_irq_q (mc_clk) | u_cpu/u_plic/u_psync_mc{0..3} (core_clk) | 1 | pulse | PULSE_SYNC | CDC_PSYNC_OK | Clean |
| CDC-0124 | u_core/u_pmu_if/mc_lp_req_q (core_clk) | u_ddr_ss/u_mc{0..3}/lp_req_sync_q (mc_clk) | 1 | req_ack | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0125 | u_ddr_ss/u_mc{0..3}/lp_ack_q (mc_clk) | u_core/u_pmu_if/mc_lp_ack_sync_q (core_clk) | 1 | req_ack | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0126 | u_core/u_mc_csr/u_apb_brg req/addr/wdata (core_clk) | u_ddr_ss/u_mc{0..3}/u_apb_brg (mc_clk) | 45 | bus | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0127 | u_pcie0_wrap/u_ctl/u_afifo_tx (pcie_core_clk) | u_noc/u_ni_pcie0/u_afifo_rx (core_clk) | 588 | fifo | ASYNC_FIFO | CDC_FIFO_OK | Clean |
| CDC-0128 | u_noc/u_ni_pcie0/u_afifo_tx (core_clk) | u_pcie0_wrap/u_ctl/u_afifo_rx (pcie_core_clk) | 588 | fifo | ASYNC_FIFO | CDC_FIFO_OK | Clean |
| CDC-0129 | u_pcie0_wrap/u_ctl/ltssm_q[5:0] (pcie_core_clk) | u_core/u_pcie_csr/ltssm_sts_q[5:0] (core_clk) | 6 | bus | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0130 | u_pcie0_wrap/u_ctl/link_up_q (pcie_core_clk) | u_core/u_pcie_csr/link_up_sync_q (core_clk) | 1 | level | SYNC_3FF | CDC_SYNC_OK | Clean |
| CDC-0131 | u_pcie0_wrap/u_ctl/flr_req_q (pcie_core_clk) | u_core/u_pcie_csr/u_flr_psync (core_clk) | 1 | pulse | PULSE_SYNC | CDC_PSYNC_OK | Clean |
| CDC-0132 | u_core/u_msi_gen/msi_req_q + msi_vec_q[4:0] (core_clk) | u_pcie0_wrap/u_ctl/msi_req_sync_q (pcie_core_clk) | 6 | bus | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0133 | PCIE0_PERST_N pad (async) | u_pcie0_wrap/u_rst/perst_sync_q (pcie_aux_clk) | 1 | reset | RESET_SYNC | CDC_RSTSYNC_OK | Clean |
| CDC-0134 | PCIE0_CLKREQ_N pad (async) | u_pcie0_wrap/u_l1ss_ctl/clkreq_sync_q (pcie_aux_clk) | 1 | level | SYNC_2FF | CDC_SYNC_OK | Clean |
| CDC-0135 | u_pcie0_wrap/u_phy/refclk_valid (async) | u_pcie0_wrap/u_l1ss_ctl/refclk_valid_sync_q (pcie_aux_clk) | 1 | level | SYNC_2FF | CDC_SYNC_OK | Clean |
| CDC-0136 | u_pcie0_wrap/u_ctl/l1_entry_req_q (pcie_core_clk) | u_pcie0_wrap/u_l1ss_ctl/entry_req_sync_q (pcie_aux_clk) | 1 | req_ack | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0137 | u_pcie0_wrap/u_l1ss_ctl/l1ss_state_q[3:0] (pcie_aux_clk) | u_pcie0_wrap/u_ctl/l1ss_sts_q[3:0] (pcie_core_clk) | 4 | bus | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0138 | u_pcie0_wrap/u_l1ss_ctl/p12_exit_q (pcie_aux_clk) | u_pcie0_wrap/u_ctl/p12_exit_sync_q (pcie_core_clk) | 1 | level | SYNC_3FF | CDC_SYNC_OK | Clean |
| CDC-0139 | u_aon/u_fuse_shadow/pcie1_dis_q (aon_clk) | u_pcie1_wrap/u_iso/fuse_dis_q (pcie1_core_clk) | 1 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-012) |
| CDC-0140 | u_core/u_pcie_csr/lane_cfg_q[7:0] (core_clk) | u_pcie0_wrap/u_ctl/lane_cfg_q[7:0] (pcie_core_clk) | 8 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-013) |
| CDC-0141 | u_pcie1_wrap/u_ctl/u_afifo_tx (pcie1_core_clk) | u_noc/u_ni_pcie1/u_afifo_rx (core_clk) | 588 | fifo | ASYNC_FIFO | CDC_FIFO_OK | Clean |
| CDC-0142 | u_aon/u_fuse_shadow/lc_state_q[7:0] (aon_clk) | u_sec_encl/u_lc/lc_state_q[7:0] (sec_clk) | 8 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-017) |
| CDC-0143 | u_sec_encl/u_trng/u_ent/ro_bit[3:0] ring osc (async) | u_sec_encl/u_trng/raw_sync_q[3:0] (sec_clk) | 4 x 1 | level | SYNC_2FF | CDC_SYNC_OK | Clean |
| CDC-0144 | u_aon/u_tamper/tamper_q (aon_clk) | u_sec_encl/u_alert/tamper_sync_q (sec_clk) | 1 | level | SYNC_2FF | CDC_SYNC_OK | Clean |
| CDC-0145 | u_dbg/u_tap/sec_unlock_req_q (tck) | u_sec_encl/u_dbg_auth/req_sync_q (sec_clk) | 1 | req_ack | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0146 | u_aon/u_pmu/u_pstate_fsm/pmu_sleep_req_q (aon_clk) | u_core/u_pmu_if/sleep_req_sync_q (core_clk) | 1 | req_ack | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0147 | u_aon/u_pmu/u_wake_ctl/wake_req_q (aon_clk) | u_core/u_pmu_if/wake_pending_q (core_clk) | 1 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-022) |
| CDC-0148 | u_core/u_pmu_if/core_sleep_ack_q + core_lp_req_q[1:0] (core_clk) | u_aon/u_pmu/u_pstate_fsm/sleep_ack_sync_q (aon_clk) | 3 | req_ack | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0149 | u_aon/u_pmu/u_pstate_fsm/pstate_gray_q[1:0] (aon_clk) | u_core/u_pmu_if/pstate_sts_q[1:0] (core_clk) | 2 | gray | GRAY_CNT | CDC_GRAY_OK | Clean |
| CDC-0150 | u_aon/u_pmu/u_pstate_fsm/div64_entry_req_q (aon_clk) | u_core/u_crg/u_div64_ctl/entry_req_sync_q (core_clk) | 1 | req_ack | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0151 | u_aon/u_strap/boot_mode_q[2:0] (aon_clk) | u_core/u_sysctl/boot_mode_q[2:0] (core_clk) | 3 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-008) |
| CDC-0152 | u_aon/u_fuse_shadow/sram_trim_q[11:0] (aon_clk) | u_npu_c{0..3}/u_sram_ctl/trim_q[11:0] (npu_clk) | 12 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-010) |
| CDC-0153 | u_aon/u_fuse_shadow/pvt_trim_q[15:0] (aon_clk) | u_core/u_pvt_ctl/trim_q[15:0] (core_clk) | 16 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-011) |
| CDC-0154 | u_aon/u_rtc/alarm_irq_q (aon_clk) | u_cpu/u_plic/u_psync_rtc (core_clk) | 1 | pulse | PULSE_SYNC | CDC_PSYNC_OK | Clean |
| CDC-0155 | u_aon/u_rst_ctl/core_rst_req_n (aon_clk) | u_core/u_crg/u_rst_sync_core (core_clk) | 1 | reset | RESET_SYNC | CDC_RSTSYNC_OK | Clean |
| CDC-0156 | u_core/u_aon_brg req/addr/wdata (core_clk) | u_aon/u_apb_brg/req_sync_q (aon_clk) | 45 | bus | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0157 | u_aon/u_apb_brg rdata_q[31:0] + ack (aon_clk) | u_core/u_aon_brg/rdata_q[31:0] (core_clk) | 33 | bus | HANDSHAKE | CDC_HSK_OK | Clean |
| CDC-0158 | u_dbg/u_tap/tdr_occ_cfg_q[63:0] (tck) | u_core/u_crg/u_occ{0..5}/cfg_q (core_clk) | 64 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-001) |
| CDC-0159 | u_dbg/u_tap/tdr_mbist_cfg_q[31:0] (tck) | u_npu_c{0..3}/u_mbist_ctl/cfg_q[31:0] (npu_clk) | 32 | quasi_static | None | CDC_NO_SYNC | Waived (W-CDC-002) |
| CDC-0160 | TRST_N pad & por_n (async) | u_dbg/u_tap/u_rst_sync (tck) | 1 | reset | RESET_SYNC | CDC_RSTSYNC_OK | Clean |

## 7. CDC waiver register

43 active waivers: 37 quasi-static and 6 reconvergence. Approvals follow CHK-CDC-06.

| Waiver | Crossing | Signal (source -> destination) | Declared class; category | Justification and stability guarantee | Requested | Approved | Status |
|---|---|---|---|---|---|---|---|
| W-CDC-001 | CDC-0158 | u_tap/tdr_occ_cfg_q[63:0] (tck) -> u_crg/u_occ{0..5}/cfg_q (core_clk) | Level; quasi-static (test) | Test mode only: forced to reset value while test_mode=0; TDR updated only with OCC clocks stopped (TE-DFT-006); SVA a_occ_cfg_stable | A. Qureshi, 2026-06-16 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-22 | Approved |
| W-CDC-002 | CDC-0159 | u_tap/tdr_mbist_cfg_q[31:0] (tck) -> u_npu_c{0..3}/u_mbist_ctl/cfg_q (npu_clk) | Level; quasi-static (test) | Written before mbist_start with npu_clk gated (TE-DFT-011); MBIST controller held in reset in mission mode; SVA a_mbist_cfg_stable | A. Qureshi, 2026-06-16 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-22 | Approved |
| W-CDC-003 | CDC-0231 | u_tap/tdr_mbist_cfg_q[31:0] (tck) -> u_cpu/u_mbist_ctl/cfg_q (cpu_clk) | Level; quasi-static (test) | As W-CDC-002 with cpu_clk gated (TE-DFT-011); held in reset in mission mode; SVA a_mbist_cfg_stable | A. Qureshi, 2026-06-16 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-22 | Approved |
| W-CDC-004 | CDC-0232 | u_tap/tdr_mbist_cfg_q[31:0] (tck) -> u_ddr_ss/u_mbist_ctl/cfg_q (mc_clk) | Level; quasi-static (test) | As W-CDC-002 with mc_clk gated (TE-DFT-011); held in reset in mission mode; SVA a_mbist_cfg_stable | A. Qureshi, 2026-06-16 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-22 | Approved |
| W-CDC-005 | CDC-0233 | u_tap/tdr_cmp_cfg_q[23:0] (tck) -> u_cmp_ctl/cfg_q[23:0] (core_clk) | Level; quasi-static (test) | Scan-compression setup loaded before the first shift with clocks stopped (TE-DFT-003); tied off by test_mode=0; SVA a_cmp_cfg_stable | A. Qureshi, 2026-06-17 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-22 | Approved |
| W-CDC-006 | CDC-0234 | TEST_MODE pad (async; scan_mode decode) -> u_crg/u_occ{0..5}/scan_mode_q (core_clk) | Level; quasi-static (test) | ATE-static pin set before any clock starts; board pull-down and life-cycle test lock force 0 in mission mode (TE-DFT-001) | A. Qureshi, 2026-06-17 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-22 | Approved |
| W-CDC-007 | CDC-0110 | u_tap/tdr_trace_cfg_q[15:0] (tck) -> u_trace_funnel/cfg_q[15:0] (npu_clk) | Level; quasi-static (SW rule) | Rule DBG-PG 4.2: written only while tf_en=0, funnel clock gated; tf_en re-synchronized by CDC-0109; SVA a_tf_cfg_stable_when_en | V. Halloran, 2026-07-01 | H. Tanabe (CDC Owner); V. Halloran (NPU Owner), 2026-07-06 | Approved |
| W-CDC-008 | CDC-0151 | u_strap/boot_mode_q[2:0] (aon_clk) -> u_sysctl/boot_mode_q[2:0] (core_clk) | Level; quasi-static (strap) | Latched on PORST_N de-assertion; core_rst_n released >= 1,024 aon_clk cycles later; no re-capture until POR; SVA a_boot_mode_stable | K. Mensah, 2026-06-25 | H. Tanabe (CDC Owner); K. Mensah (PMU Owner), 2026-06-29 | Approved |
| W-CDC-009 | CDC-0112 | u_fuse_shadow/fuse_cfg_q[31:0] (aon_clk) -> u_crg/pll_cfg_q[31:0] (core_clk) | Level; quasi-static (OTP) | Written once by fuse-shadow load during POR while the core domain is held in reset (core_rst_n released >= 1,024 aon_clk cycles after fuse_load_done); never changes afterwards; stability proven by SVA a_fuse_cfg_stable (formal, full proof) | K. Mensah, 2026-07-10 | H. Tanabe (CDC Owner); K. Mensah (PMU Owner), 2026-07-15 | Approved |
| W-CDC-010 | CDC-0152 | u_fuse_shadow/sram_trim_q[11:0] (aon_clk) -> u_npu_c{0..3}/u_sram_ctl/trim_q (npu_clk) | Level; quasi-static (OTP) | Loaded during POR; npu_clk not enabled until trim_valid (PLL_NPU output gate in u_crg); never rewritten; SVA a_sram_trim_stable | V. Halloran, 2026-07-08 | H. Tanabe (CDC Owner); V. Halloran (NPU Owner), 2026-07-13 | Approved |
| W-CDC-011 | CDC-0153 | u_fuse_shadow/pvt_trim_q[15:0] (aon_clk) -> u_pvt_ctl/trim_q[15:0] (core_clk) | Level; quasi-static (OTP) | Loaded during POR while core_rst_n is asserted; never changes afterwards; SVA a_pvt_trim_stable | K. Mensah, 2026-07-08 | H. Tanabe (CDC Owner); K. Mensah (PMU Owner), 2026-07-13 | Approved |
| W-CDC-012 | CDC-0139 | u_fuse_shadow/pcie1_dis_q (aon_clk) -> u_pcie1_wrap/u_iso/fuse_dis_q (pcie1_core_clk) | Level; quasi-static (OTP) | FUSE_PCIE1_DIS=1, loaded at POR; PD_PCIE1 stays off and the PCIE1 domain in reset for the life of the part; SVA a_pcie1_dis_stable | L. Brandt, 2026-07-09 | H. Tanabe (CDC Owner); L. Brandt (PCIe Owner), 2026-07-14 | Approved |
| W-CDC-013 | CDC-0140 | u_pcie_csr/lane_cfg_q[7:0] (core_clk) -> u_pcie0_wrap/u_ctl/lane_cfg_q[7:0] (pcie_core_clk) | Level; quasi-static (SW rule) | Boot ROM writes before app_ltssm_en while u_ctl is in pcie_core reset; HW write-lock once LTSSM is enabled; SVA a_lane_cfg_stable | L. Brandt, 2026-07-09 | H. Tanabe (CDC Owner); L. Brandt (PCIe Owner), 2026-07-14 | Approved |
| W-CDC-014 | CDC-0121 | u_mc_csr/dram_tmg_q[255:0] (core_clk) -> u_mc{0..3}/tmg_q (mc_clk) | Level; quasi-static (SW rule) | Vendor static register: written with the controller in reset, before DFI init; HW write-lock after mc_init_start; SVA a_mc_tmg_stable | A. Deshmukh, 2026-07-15 | H. Tanabe (CDC Owner); A. Deshmukh (Memory Owner), 2026-07-20 | Approved |
| W-CDC-015 | CDC-0311 | u_mc_csr/addr_map_q[63:0] (core_clk) -> u_mc{0..3}/addr_map_q (mc_clk) | Level; quasi-static (SW rule) | Vendor static register: written with the controller in reset, before DFI init; HW write-lock after mc_init_start; SVA a_mc_amap_stable | A. Deshmukh, 2026-07-15 | H. Tanabe (CDC Owner); A. Deshmukh (Memory Owner), 2026-07-20 | Approved |
| W-CDC-016 | CDC-0312 | u_mc_csr/phy_static_q[127:0] (core_clk) -> u_phy{0..3}/static_cfg_q (mc_clk) | Level; quasi-static (SW rule) | Vendor static register: programmed before PHY init with the DFI clock gated; HW write-lock after init; SVA a_phy_static_stable | A. Deshmukh, 2026-07-15 | H. Tanabe (CDC Owner); A. Deshmukh (Memory Owner), 2026-07-20 | Approved |
| W-CDC-017 | CDC-0142 | u_fuse_shadow/lc_state_q[7:0] (aon_clk) -> u_sec_encl/u_lc/lc_state_q[7:0] (sec_clk) | Level; quasi-static (OTP) | Loaded at POR; u_sec_encl in reset until lc_valid; changes only by OTP programming plus POR; SVA a_lc_state_stable | I. Carvalho, 2026-07-10 | H. Tanabe (CDC Owner); I. Carvalho (Security Owner), 2026-07-15 | Approved |
| W-CDC-018 | CDC-0321 | u_fuse_shadow/sboot_cfg_q[15:0] (aon_clk) -> u_sec_encl/u_boot/sboot_cfg_q (sec_clk) | Level; quasi-static (OTP) | Secure-boot policy and key-slot select loaded at POR while u_sec_encl is in reset; never rewritten; SVA a_sboot_cfg_stable | I. Carvalho, 2026-07-10 | H. Tanabe (CDC Owner); I. Carvalho (Security Owner), 2026-07-15 | Approved |
| W-CDC-019 | CDC-0322 | u_fuse_shadow/dev_id_q[63:0] (aon_clk) -> u_sysctl/dev_id_q[63:0] (core_clk) | Level; quasi-static (OTP) | Device ID / lot-trace fuses loaded at POR while core_rst_n is asserted; read-only afterwards; SVA a_dev_id_stable | K. Mensah, 2026-07-10 | H. Tanabe (CDC Owner); K. Mensah (PMU Owner), 2026-07-15 | Approved |
| W-CDC-020 | CDC-0331 | u_npu_csr/tile_en_q[15:0] (core_clk) -> u_npu_c{0..3}/u_ctl/tile_en_q (npu_clk) | Level; quasi-static (SW rule) | Boot firmware writes with clusters in npu_rst_n, npu_clk gated (NPU PG 2.3); HW ignores writes outside reset; SVA a_tile_en_stable | V. Halloran, 2026-07-20 | H. Tanabe (CDC Owner); V. Halloran (NPU Owner), 2026-07-24 | Approved |
| W-CDC-021 | CDC-0341 | u_fuse_shadow/io_drv_cfg_q[31:0] (aon_clk) -> u_padctl/drv_cfg_q[31:0] (periph_clk) | Level; quasi-static (OTP) | Pad drive/slew defaults loaded at POR with u_periph in reset; SW overrides use a separate register; SVA a_io_drv_cfg_stable | R. Lindqvist, 2026-07-16 | H. Tanabe (CDC Owner); R. Lindqvist (Package & I/O Lead), 2026-07-21 | Approved |
| W-CDC-022 | CDC-0147 | u_wake_ctl/wake_req_q (aon_clk) -> u_pmu_if/wake_pending_q (core_clk) | Level; quasi-static (power-state) | Signal is quasi-static; only toggles on power-state transitions. | K. Mensah, 2026-08-05 | H. Tanabe (CDC Owner); K. Mensah (PMU Owner), 2026-08-07 | Approved |
| W-CDC-023 | CDC-0332 | u_npu_csr/sparse_cfg_q[31:0] (core_clk) -> u_tile{0..3}/sparse_cfg_q (npu_clk) | Level; quasi-static (SW rule) | Driver rule NPU PG 3.4: written only while the cluster is idle and clock-gated; HW guard on cluster_busy; SVA a_sparse_cfg_stable | V. Halloran, 2026-07-20 | H. Tanabe (CDC Owner); V. Halloran (NPU Owner), 2026-07-24 | Approved |
| W-CDC-024 | CDC-0333 | u_npu_csr/qos_cfg_q[15:0] (core_clk) -> u_nbr/qos_cfg_q[15:0] (npu_clk) | Level; quasi-static (SW rule) | Written before cluster enable with npu_clk gated (NPU PG 2.5); HW write-guard on npu_clk_en; SVA a_nbr_qos_stable | V. Halloran, 2026-07-20 | H. Tanabe (CDC Owner); V. Halloran (NPU Owner), 2026-07-24 | Approved |
| W-CDC-025 | CDC-0701 | u_mc{0..3}/init_done_q, train_err_q (mc_clk) -> u_mc_csr/init_sts_q[1:0] (core_clk) | Level (per bit); reconvergence (status) | Independent SYNC_3FF bits meet only in a SW-read register; no HW consumer; driver polls init_done, then reads train_err | A. Deshmukh, 2026-07-15 | H. Tanabe (CDC Owner); A. Deshmukh (Memory Owner), 2026-07-20 | Approved |
| W-CDC-026 | CDC-0702 | u_ctl/link_up_q, dl_up_q (pcie_core_clk) -> u_pcie_csr/link_sts_q[1:0] (core_clk) | Level (per bit); reconvergence (status) | Independent SYNC_3FF status bits, SW-read only; link events are also reported by interrupt; no coherency required | L. Brandt, 2026-07-09 | H. Tanabe (CDC Owner); L. Brandt (PCIe Owner), 2026-07-14 | Approved |
| W-CDC-027 | CDC-0703 | u_npu_c{0..3}/u_ctl/busy_q (npu_clk) -> u_npu_csr/busy_sts_q[3:0] (core_clk) | Level (per bit); reconvergence (status) | Per-cluster SYNC_3FF bits, independent and SW-read only; completion uses the done interrupts (CDC-0103) | V. Halloran, 2026-07-01 | H. Tanabe (CDC Owner); V. Halloran (NPU Owner), 2026-07-06 | Approved |
| W-CDC-028 | CDC-0704 | u_dma/ch_sts_q[7:0] (npu_clk) -> u_npu_csr/dma_sts_q[31:0] (core_clk) | Level (per bit); reconvergence (status) | Per-channel SYNC_3FF flags, independent and SW-read only; no multi-bit coherency defined | V. Halloran, 2026-07-01 | H. Tanabe (CDC Owner); V. Halloran (NPU Owner), 2026-07-06 | Approved |
| W-CDC-029 | CDC-0705 | GPIO input pads (async) -> u_gpio/in_reg_q[31:0] (periph_clk) | Level (per bit); reconvergence (status) | Independent pins, each through SYNC_2FF into a SW-read register; no multi-bit coherency defined for GPIO | R. Lindqvist, 2026-07-16 | H. Tanabe (CDC Owner); R. Lindqvist (Package & I/O Lead), 2026-07-21 | Approved |
| W-CDC-030 | CDC-0361 | u_fuse_shadow/pcie_phy_trim_q[47:0] (aon_clk) -> u_pcie0_wrap/u_phy/trim_q (pcie_core_clk) | Level; quasi-static (OTP) | PHY trim loaded at POR; PHY held in reset until trim_valid and PERST_N de-assertion; never rewritten; SVA a_pcie_phy_trim_stable | L. Brandt, 2026-07-09 | H. Tanabe (CDC Owner); L. Brandt (PCIe Owner), 2026-07-14 | Approved |
| W-CDC-031 | CDC-0362 | u_pcie_csr/bar_cfg_q[191:0] (core_clk) -> u_ctl/bar_cfg_q (pcie_core_clk) | Level; quasi-static (SW rule) | Boot ROM writes BAR sizes and class code before app_ltssm_en; DBI write-lock once link training starts; SVA a_bar_cfg_stable | L. Brandt, 2026-07-09 | H. Tanabe (CDC Owner); L. Brandt (PCIe Owner), 2026-07-14 | Approved |
| W-CDC-032 | CDC-0334 | u_npu_csr/perf_sel_q[63:0] (core_clk) -> u_perf/evt_sel_q[15:0] (npu_clk) | Level; quasi-static (SW rule) | Written only while perf_en=0 (enable re-synchronized SYNC_3FF); driver rule NPU PG 6.1; SVA a_perf_sel_stable | V. Halloran, 2026-07-29 | H. Tanabe (CDC Owner); V. Halloran (NPU Owner), 2026-08-03 | Approved |
| W-CDC-033 | CDC-0335 | u_fuse_shadow/npu_harvest_q[15:0] (aon_clk) -> u_harvest/tile_dis_q[15:0] (npu_clk) | Level; quasi-static (OTP) | Tile-harvest fuses loaded at POR with all clusters in npu_rst_n; never rewritten; SVA a_harvest_stable (formal, full proof) | V. Halloran, 2026-07-08 | H. Tanabe (CDC Owner); V. Halloran (NPU Owner), 2026-07-13 | Approved |
| W-CDC-034 | CDC-0381 | u_fuse_shadow/ddr_phy_trim_q[63:0] (aon_clk) -> u_phy{0..3}/trim_q (mc_clk) | Level; quasi-static (OTP) | PHY trim loaded at POR; PHY held in reset until trim_valid; never rewritten; SVA a_ddr_phy_trim_stable | A. Deshmukh, 2026-07-15 | H. Tanabe (CDC Owner); A. Deshmukh (Memory Owner), 2026-07-20 | Approved |
| W-CDC-035 | CDC-0391 | u_tap/tdr_bscan_cfg_q[7:0] (tck) -> u_padctl/bscan_ctl_q[7:0] (periph_clk) | Level; quasi-static (test) | EXTEST/INTEST only (test_mode=1); periph_clk stopped during boundary scan (TE-DFT-009); SVA a_bscan_cfg_stable | A. Qureshi, 2026-06-18 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-24 | Approved |
| W-CDC-036 | CDC-0392 | TEST_MODE pad (async) -> u_rstmux/test_mode_q (core_clk) | Level; quasi-static (test) | ATE-static pin set before any clock starts; board pull-down and life-cycle test lock force 0 in mission mode (TE-DFT-001) | A. Qureshi, 2026-06-18 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-24 | Approved |
| W-CDC-037 | CDC-0393 | u_tap/tdr_pll_test_q[15:0] (tck) -> u_crg/pll_test_cfg_q (core_clk) | Level; quasi-static (test) | test_mode=1 only; written with PLLs in bypass and OCC clocks stopped (TE-DFT-017); SVA a_pll_test_stable | A. Qureshi, 2026-06-18 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-24 | Approved |
| W-CDC-038 | CDC-0394 | u_tap/tdr_iddq_cfg_q[3:0] (tck) -> u_crg/iddq_q[3:0] (core_clk) | Level; quasi-static (test) | IDDQ setup, test_mode=1 only; all functional clocks stopped during measurement (TE-DFT-019) | A. Qureshi, 2026-06-18 | H. Tanabe (CDC Owner); S. Haddad (DFT Lead), 2026-06-24 | Approved |
| W-CDC-039 | CDC-0421 | u_strap/strap_qspi_q[1:0] (aon_clk) -> u_qspi0/boot_cfg_q[1:0] (periph_clk) | Level; quasi-static (strap) | Latched on PORST_N de-assertion; u_periph in reset until core_rst_n release; never re-captured; SVA a_strap_qspi_stable | R. Lindqvist, 2026-07-16 | H. Tanabe (CDC Owner); R. Lindqvist (Package & I/O Lead), 2026-07-21 | Approved |
| W-CDC-040 | CDC-0422 | u_strap/strap_pcie_q[2:0] (aon_clk) -> u_ctl/strap_q[2:0] (pcie_core_clk) | Level; quasi-static (strap) | Lane-reversal / max-width straps latched on PORST_N de-assertion; u_ctl in reset until PERST_N de-assertion; never re-captured; SVA a_strap_pcie_stable | L. Brandt, 2026-07-09 | H. Tanabe (CDC Owner); L. Brandt (PCIe Owner), 2026-07-14 | Approved |
| W-CDC-041 | CDC-0706 | u_ctl/err_sts_q[15:0] (pcie_core_clk) -> u_pcie_csr/err_sts_q[15:0] (core_clk) | Level (per bit); reconvergence (status) | Sticky independent error flags, each SYNC_3FF; W1C clear returns through the CSR handshake bridge; SW-read only | L. Brandt, 2026-08-03 | H. Tanabe (CDC Owner); L. Brandt (PCIe Owner), 2026-08-06 | Approved |
| W-CDC-042 | CDC-0351 | u_fuse_shadow/mc_cfg_q[31:0] (aon_clk) -> u_mc{0..3}/fuse_cfg_q (mc_clk) | Level; quasi-static (OTP) | Speed-bin / channel-disable fuses loaded at POR with the controllers in reset; never rewritten; SVA a_mc_fuse_cfg_stable | A. Deshmukh, 2026-07-15 | H. Tanabe (CDC Owner); A. Deshmukh (Memory Owner), 2026-07-20 | Approved |
| W-CDC-043 | CDC-0342 | u_fuse_shadow/dbg_lock_q (aon_clk) -> u_tap/dbg_lock_q (tck) | Level; quasi-static (OTP) | Loaded at POR; TAP held in reset by por_n until fuse_load_done; never rewritten; SVA a_dbg_lock_stable (formal, full proof) | I. Carvalho, 2026-07-10 | H. Tanabe (CDC Owner); V. Halloran (NPU/DBG Owner); I. Carvalho (Security Owner), 2026-07-15 | Approved |

## 8. Metastability MTBF

Worst resolution corner ss_0p675v_m40c: tau = 20.5 ps, T0 = 24.0 ps (SYNC2_X2, SYNC3_X2). t_r = (stages - 1) x T_dest - 0.098 ns (clock-to-Q, setup, jitter, skew). f_data = 25% of the fastest source clock (async sources: of the toggle rate, e.g. TRNG ring oscillator ~1.6 GHz into sec_clk, pads 200 MHz into periph_clk). MTBF = exp(t_r / tau) / (T0 x f_dest x f_data).

All rows PASS the 1,000-year limit.

| Synchronizer | Destination clock | f_dest (MHz) | f_data (MHz) | t_r (ns) | MTBF per synchronizer (years) |
|---|---|---|---|---|---|
| SYNC3_X2 | cpu_clk | 1500.0 | 250.0 | 1.235 | 5.2E+11 |
| SYNC3_X2 | npu_clk | 1200.0 | 250.0 | 1.569 | 7.5E+18 |
| SYNC3_X2 | mc_clk | 1066.7 | 250.0 | 1.777 | 2.2E+23 |
| SYNC3_X2 | core_clk | 1000.0 | 375.0 | 1.902 | 6.9E+25 |
| SYNC3_X2 | pcie_core_clk | 1000.0 | 250.0 | 1.902 | 1.0E+26 |
| SYNC3_X2 | pcie1_core_clk | 500.0 | 250.0 | 3.902 | > 1.0E+30 |
| SYNC2_X2 | sec_clk | 500.0 | 400.0 | 1.902 | 1.3E+26 |
| SYNC2_X2 | periph_clk | 200.0 | 50.0 | 4.902 | > 1.0E+30 |
| SYNC2_X2 | tck | 50.0 | 375.0 | 19.902 | > 1.0E+30 |
| SYNC2_X2 | aon_clk / pcie_aux_clk | 25.000 | 250.0 | 39.902 | > 1.0E+30 |

Chip-level MTBF (all synchronizers, MISSION mode) is 4.4E+09 years, dominated by cpu_clk destinations. For reference, 2-FF at npu_clk would give about 17 years, hence 3-FF above 800 MHz (CHK-CDC-02); none is used.

## 9. Reset-domain crossing (RDC)

### 9.1 Reset domains

All resets below are asserted asynchronously and de-asserted through the listed synchronizer.

| Reset | Source | De-assertion synchronizer | Clock | Stages |
|---|---|---|---|---|
| por_n | POR cell u_aon/u_por (VDD_AON) | u_aon/u_rst_sync_por | aon_clk | 2 |
| aon_rst_n | u_aon/u_rst_ctl (PORST_N and AON POR detector) | u_aon/u_rst_sync_aon | aon_clk | 2 |
| core_rst_n | u_aon/u_rst_ctl; released >= 1,024 aon_clk cycles after fuse_load_done | u_core/u_crg/u_rst_sync_core (CDC-0155) | core_clk | 3 |
| sec_rst_n | core_rst_n or tamper reset | u_sec_encl/u_rst_sync | sec_clk | 2 |
| periph_rst_n | core_rst_n | u_periph/u_rst_sync | periph_clk | 2 |
| npu_rst_n[3:0] | u_core/u_npu_csr (per cluster, SW) | u_npu_c{0..3}/u_rst_sync | npu_clk | 3 |
| cpu_rst_n[3:0] | u_core/u_sysctl (per hart) | u_cpu/u_rst_sync{0..3} | cpu_clk | 3 |
| mc_rst_n[3:0] | u_core/u_mc_csr (per channel) | u_ddr_ss/u_mc{0..3}/u_rst_sync | mc_clk | 3 |
| pcie0_perst_n | PCIE0_PERST_N pad | u_pcie0_wrap/u_rst/perst_sync_q (CDC-0133); u_pcie0_wrap/u_rst/core_rst_sync | pcie_aux_clk; pcie_core_clk | 2; 3 |
| pcie1_rst_n | Held asserted (FUSE_PCIE1_DIS=1) | u_pcie1_wrap/u_rst_sync | pcie1_core_clk | 3 |
| trst_n | TRST_N pad and por_n | u_dbg/u_tap/u_rst_sync (CDC-0160) | tck | 2 |

Reset ordering declared in the CDC intent and proven by the formal tool: por_n implies aon_rst_n; aon_rst_n implies core_rst_n; core_rst_n implies sec_rst_n, periph_rst_n, npu_rst_n, cpu_rst_n and mc_rst_n. DFT reset bypass (`u_core/u_rstmux`) is active only with test_mode=1.

### 9.2 RDC results

| Check | Result |
|---|---|
| Asynchronous reset pins driven from a RESET_SYNC output (or the DFT bypass mux, test_mode only) | 100% |
| Reset de-assertion not synchronized to the destination clock | 0 |
| Combinational logic on reset paths other than RSTMUX and AND of synchronized resets | 0 |
| RDC paths (source and destination flops on different reset domains) | 318 |
| Clean by proven reset ordering | 251 |
| Clean by isolation or qualifier (destination gated or isolated while source is in reset) | 64 |
| Waived (W-RDC-001 to W-RDC-003) | 3 |
| Unwaived | 0 |

### 9.3 RDC waivers

| Waiver | Path | Justification | Approved |
|---|---|---|---|
| W-RDC-001 | trst_n domain (u_dbg/u_dtm) -> cpu_rst_n domain (u_cpu/u_dm), DMI request | JTAG reset mid-access only aborts that debug access; the debug module times out and clears dmi_busy; no mission-mode effect | H. Tanabe (CDC Owner); D. Achterberg (CPU partition owner); S. Haddad (DFT Lead), 2026-07-02 |
| W-RDC-002 | pcie0_perst_n domain (u_pcie0_wrap/u_ctl) -> core_rst_n domain (u_core/u_pcie_csr) status bits | SW-read status only, treated as invalid while perst_sts=1; interrupt path isolated by perst_iso first; SVA a_pcie_sts_iso | H. Tanabe (CDC Owner); L. Brandt (PCIe Owner), 2026-07-14 |
| W-RDC-003 | mc_rst_n[n] domain (u_ddr_ss/u_mc{0..3}) -> core_rst_n domain (u_noc/u_ni_mc{0..3}) read FIFO | Channel reset only after the NI drains and quiesces the port (MC PG 5.2); both FIFO sides reset through the reset handshake; SVA a_mc_quiesce_before_rst | H. Tanabe (CDC Owner); A. Deshmukh (Memory Owner), 2026-07-20 |

## 10. Open items and sign-off

Open CDC/RDC items: none. All CHK-CDC rules PASS on this netlist.

| Role | Name | Action | Date |
|---|---|---|---|
| CDC/RDC Owner | Hiroshi Tanabe | Signed off | 2026-08-12 |
| Quality & Tape-out Gatekeeper | Oren Feldman | Received for TRR-1 | 2026-08-12 |

