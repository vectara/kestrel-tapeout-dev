# KESTREL (ALX-5100) Verification Plan

| Field | Value |
|---|---|
| Doc ID | KST-VPLAN-010 |
| Title | Verification Plan |
| Revision | B (supersedes A) |
| Date | 2026-09-01 |
| Owner | Tomasz Wierzbicki (Verification Lead) |
| Status | Released for TRR-2 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Purpose and scope

This plan defines how the ALX-5100 (KESTREL) SoC RTL and sign-off netlist are verified for the tape-out readiness reviews (TRR-1, TRR-2, TRR-3) ahead of the GDSII handoff on 2026-10-30. It lists the features of each block and how each is verified, the functional coverage model (covergroups, tier, Escape-history classification, targets), the code coverage targets, the exclusion and waiver policy, and the sign-off criteria mapped to checklist ALD-QA-CHK-007 rev 7.2 (CHK-VER-01 to CHK-VER-08).

Scope is the full SoC (kst_top) in the ALX-5100 / ALX-5100I configuration: NPU (4 clusters x 4 tiles), GBUF, CPU, NOC, PCIE0 (Gen5 x16 endpoint), MEM (LPDDR5X-8533, 4 x 64-bit), SEC, AON, PMUIF, PERIPH, DBG and CRG. PCIE1 (Gen5 x8) is present in silicon but fused off in this SKU (FUSE_PCIE1_DIS=1); only its fuse decode, power gating, clock gating and output isolation are in scope (section 8, exclusion CE-004).

Results against this plan are reported in KST-COV-011 (Functional & Code Coverage Report).

## 2. Reference documents

| Doc ID | Title | Revision |
|---|---|---|
| KST-ARCH-001 | ALX-5100 (KESTREL) Architecture Specification | B |
| KST-PKG-002 | Package, Pinout & I/O Specification | B |
| KST-IPBOM-050 | IP Bill of Materials | B |
| KST-COV-011 | Functional & Code Coverage Report | B |
| KST-ECO-062 | ECO & Change Log | B |
| ALD-QA-CHK-007 | Tape-out Readiness Checklist | 7.2 |
| ALX4100-ERR | ALX-4100 (MERLIN) Silicon Errata | 3.1 |
| ALD-QA-PM-SUMMARY | Silicon Respin Post-mortems | 4 |
| PCIe Base Specification | L1 PM Substates, ASPM, LTR (PCI-SIG) | 5.0 |

## 3. Verification strategy

### 3.1 Verification levels

| Level | Scope | Method | Platform |
|---|---|---|---|
| Block | Each in-house block; integration wrapper of each third-party IP | UVM constrained-random and directed tests, SVA, code and functional coverage | Logic simulator |
| Subsystem | NPU cluster; PCIe subsystem (PCIE0 + PIPE PHY BFM); LPDDR5X subsystem (MC + PHY model + LPDDR5X memory model); SEC enclave; AON/PMU | UVM with protocol VIP (PCIe Gen5 host, LPDDR5X memory, I2C/SMBus, QSPI flash), scoreboards, SVA | Logic simulator |
| SoC | kst_top: boot, power states, interrupts, reset, end-to-end data paths | C tests on the control CPU with UVM stimulus and checkers on the host and memory interfaces | Logic simulator |
| Formal | Control FSMs and protocol logic (section 3.3) | Property checking (SVA), FSM reachability, deadlock, X-propagation; sequential equivalence for clock gating | Formal property verification tool |
| Emulation | Full SoC with firmware | Boot ROM to runtime firmware, host driver over a PCIe transactor, NPU workloads, power-state flows | Emulation platform |
| GLS | Sign-off netlist with SDF | Boot, reset and low-power entry/exit tests at min and max SDF corners (CHK-VER-06) | Logic simulator |

### 3.2 Testbench architecture

All UVM environments follow the Aldercrest layered template: sequencers and drivers per interface, passive monitors feeding scoreboards and the coverage collectors, and a register model generated from the IP-XACT register descriptions. The PCIE0 environment connects a PCIe Gen5 host VIP to the controller through a PIPE PHY BFM that models the PowerDown states (P0, P0s, P1, P1.1, P1.2, P2), rate change, REFCLK gating and refclk_valid, and drives the sideband pins PCIE0_CLKREQ_N, PCIE0_PERST_N and PCIE0_WAKE_N. An L1SS monitor classifies every L1 residency (entry trigger, exit trigger, T_POWER_ON, LTR value, rate) and samples the L1.1/L1.2 covergroups. The LPDDR5X environment uses the MIPV PHY simulation model with the training engines in full mode and a JEDEC-behaviour memory model per channel.

### 3.3 Formal verification

| Target | Instance | Property classes | Owner |
|---|---|---|---|
| PMU power-state FSM | u_aon/u_pmu | Legal transitions, one-hot encoding, no deadlock, sleep-abort handling | Kofi Mensah |
| L1 PM substates sequencer | u_pcie0_wrap/u_l1ss_ctl | FSM reachability, no deadlock, CLKREQ# handshake ordering on entry, timer reload | Leo Brandt |
| Security lifecycle FSM | u_sec_encl/u_lc_ctl | No illegal lifecycle transition, fuse-lock monotonicity, debug-unlock gating | Ines Carvalho |
| Fuse-shadow load | u_aon/u_fuse_shadow | Load once after POR, ECC check, lock, outputs stable after fuse_load_done | Kofi Mensah |
| Reset sequencer | u_core/u_crg | Reset ordering, synchronous de-assertion, reset during PLL relock | SoC integration |
| NoC credit counters | u_noc | Credit conservation, no overflow/underflow per VC | NoC team |
| CPU L2 ECC decode | u_cpu/u_l2/u_ecc_dec | Every 1-bit syndrome corrected, every 2-bit syndrome flagged | CPU subsystem team |
| NPU DMA ring pointers | u_npu_cN/u_dma | Wrap at ring end and 4 KiB page boundary, no descriptor skip or duplicate | Viktor Halloran |
| PCIE1 isolation | u_pcie1_wrap/u_pd_ctl | FUSE_PCIE1_DIS=1 implies PD_PCIE1 off, pcie1_core_clk gated, all outputs clamped to reset-safe values | Leo Brandt |
| Clock-gating equivalence | All partitions | Sequential equivalence of ICG-inserted vs. ungated RTL | SoC integration |

### 3.4 Emulation

The emulation platform runs the full kst_top with boot ROM, BL1 and runtime firmware, and the host driver on a PCIe host transactor. Scope: secure-boot flow end to end (ROM, BL1, runtime), PCIe enumeration and BAR/DMA traffic, NPU workloads (ResNet-50, BERT-large and a 7B-parameter decoder at INT8), PMU firmware power-state flows (ACTIVE, LP-IDLE, SLEEP) and LPDDR5X initialization with the PHY emulation model. Emulation also produces the activity windows for vector-based IR analysis in KST-PI-040 (for example vec_resnet50_l3_burst). Three builds per week; 212 firmware tests per build.

### 3.5 Gate-level simulation

SDF-annotated GLS runs on the sign-off netlist (kst_top_nl_2026.08.31 for this package) with SDF written by the sign-off STA tool at two corners: min = ff_0p825v_m40c_cbest_ccbest and max = ss_0p675v_m40c_cworst_ccworst (at 0.675 V the -40 C corner is the setup-worst corner because of temperature inversion). Timing checks are enabled on all sequential cells and X-propagation is monitored. The GLS list covers boot, reset and low-power entry/exit (CHK-VER-06) and is re-run on every sign-off netlist release, including after each ECO (CHK-GOV-02). SDF back-annotates cell and interconnect delays only: clock uncertainty, SI and POCV are not modelled and the OTP and flash models load fixed test images, so setup and hold closure is owned by STA (CHK-STA-01..03). Scan and MBIST pattern simulation is owned by DFT and is not part of this plan.

### 3.6 Regression, bug tracking and coverage merge

- Nightly regression on the compute farm: all directed tests plus constrained-random seeds (about 18.6k tests at package A). Weekly: 5x seed expansion for Tier-1 covergroups.
- Coverage is merged per RTL tag. When a block's RTL changes, its coverage database is reset and re-collected on the new RTL; results from earlier tags are not carried across an RTL change.
- SoC and subsystem power-state tests run the LP-IDLE core_clk divider in simulation-acceleration mode (divide ratio forced to /1 via plusarg +crg_fast_lp) to keep run time within the nightly budget; the /64 setting is exercised by GLS test gls_lp_idle_entry_exit (single timer wake).
- Since ECO-B-005 the PMU wake regression (pmu_wake_lp64_*: GPIO, RTC timer, SMBus-alert and PCIe L1.2-exit wakes, back-to-back wakes, 500 seeds) also runs nightly with +crg_fast_lp off (/64 divider enabled).
- Pass-rate criterion: >= 99.5% on 3 consecutive nightlies (CHK-VER-04).
- Bugs are filed in the bug DB as P1 (silicon-fatal, no workaround) to P4 (cosmetic). CHK-VER-03 requires 0 open P1/P2 and every P3 triaged with an owner.

## 4. Coverage model

### 4.1 Code coverage targets (CHK-VER-01)

| Metric | Target (per block, after approved exclusions) |
|---|---|
| Line | >= 98.0% |
| Branch | >= 95.0% |
| Toggle | >= 95.0% |
| FSM state | 100% |
| FSM transition | >= 95.0% |

### 4.2 Functional coverage tiers (CHK-VER-02)

| Tier | Definition | Target | Blocking |
|---|---|---|---|
| Tier-1 | Architecturally visible behaviour: host interface, boot, security, power states, memory interface, anything whose failure needs a silicon fix | >= 95.0% | Yes |
| Tier-2 | Performance, QoS and configurable options that have a firmware workaround | >= 90.0% | Yes |
| Tier-3 | Debug, test and convenience features | >= 80.0% | No (tracked) |

### 4.3 Escape-history classification (CHK-VER-07)

A covergroup is classified **Escape-history** when the feature it covers escaped to silicon on a previous Aldercrest product (an erratum in ALX4100-ERR or a respin post-mortem in ALD-QA-PM-SUMMARY) and the KESTREL fix is in logic that this plan verifies. Escape-history covergroups must reach the Tier-1 target of 95.0%, and coverage waivers are not permitted for them (ALD-QA-CHK-007 CHK-VER-07, origin PM-2024-02). Classification was reviewed with the block owners on 2026-07-08 against ALX4100-ERR rev 3.1.

| Erratum (carry-forward) | Feature | KESTREL fix | Treatment in this plan |
|---|---|---|---|
| ALX4100-E01 | NPU DMA descriptor prefetch at 4 KiB ring wrap | NPU-DMA v1.4 (in-house) | Escape-history: cg_npu_dma_ring_wrap |
| ALX4100-E03 | PCIe L1.2 exit with CLKREQ# re-assert during T_POWER_ON | l1ss_ctl v3.0 (in-house redesign) | Escape-history: cg_pcie0_l12_entry_exit. PCIE1 L1SS logic is unreachable in ALX-5100/ALX-5100I (fused off, CE-004); cg_pcie1_l1ss is to be classified Escape-history for any ALX-5100X release |
| ALX4100-E04 | LPDDR5X RFM activation counter | MC-LP5X vendor fix (version per KST-IPBOM-050) | IP version, CHK-IP-03; integration coverage in cg_mem_refresh_rfm (Tier-1) |
| ALX4100-E05 | I2C/SMBus clock-stretch timeout | I2C-CTL v1.5 plus in-house SMBus timeout wrapper | Escape-history: cg_i2c_clk_stretch |
| ALX4100-E07 | LPDDR5X RDQS gate training at cold | MC-LP5X / PHY-LP5X-N5 vendor fix (version per KST-IPBOM-050) | IP version, CHK-IP-03; temperature-dependent PHY behaviour is outside RTL simulation |
| ALX4100-E08 | PVT sensor offset above 110 C | PVT-MON-N5 v1.1 | IP version, CHK-IP-03 |
| ALX4100-E10 | PLL lock-detect during SSC ramp | PLL-N5-FRAC v3.1 | IP version, CHK-IP-03; integration coverage in cg_crg_pll_lock (Tier-1) |
| ALX4100-E11 | UART RX overrun flag | UART-16550C v1.2 | IP version, CHK-IP-03; integration coverage in cg_uart_fifo_baud (Tier-3) |
| ALX4100-E12 | OTP read margin at low VDD | OTP-N5-4K v2.0 | IP version, CHK-IP-03 (analog) |
| ALX4100-E13 | QSPI DTR sampling at 200 MHz | QSPI-CTL v2.3 | IP version, CHK-IP-03; KESTREL boots in SDR at 133 MHz |
| ALX4100-E14 | NPU sparse decompressor all-zero block | NPU-TILE v3.0 (in-house) | Escape-history: cg_npu_sparse_decomp_zero_blk |

For errata whose fix lies inside third-party IP (E04, E07, E08, E10, E11, E12, E13) the fix is confirmed by IP version under CHK-IP-03; the integration covergroups listed for them are held to the 95.0% target whatever their tier. The E11 overrun-clear behaviour is also checked by directed test uart_lsr_ovr_clear.

Post-mortems PM-2021-02 (ESD), PM-2022-01 (I/O bank voltage) and PM-2023-03 (wake-pulse clock-domain crossing) concern physical and structural checks. They are governed by CHK-PV-02, CHK-SPEC-03 and CHK-CDC-04 in the respective sign-off reports and are not simulation-coverage items.

## 5. Feature list per block

| Block | Instance(s) | Features verified | Methods | Owner |
|---|---|---|---|---|
| NPU | u_npu_c0..u_npu_c3, u_npu_top | MAC array (INT8, INT4, BF16, FP16), tile scheduler, 4 MiB tile SRAM with SECDED, DMA engine (1D/2D/3D, scatter-gather, descriptor rings), sparse-weight decompressor, activation LUT, barriers, tile clock gating | Block and cluster UVM, SoC C tests, emulation workloads, formal (DMA ring pointers) | Viktor Halloran |
| GBUF | u_gbuf | 32 MiB global buffer, 32 banks, bank arbitration, SECDED, NoC target port | Block UVM, SoC traffic | SoC integration team |
| NOC | u_noc | 4x4 mesh XY routing, 512-bit links, 4 VCs, credit flow control, QoS weighted round-robin, error responses | Block UVM, formal (credit counters), SoC traffic | NoC team |
| CPU | u_cpu | CPU-RV64-Q4 integration: boot, 1 MiB L2 with ECC, PLIC/CLINT, PMP, debug module | SoC C tests, integration UVM, formal (L2 ECC decode) | CPU subsystem team |
| MEM | u_ddr_ss | MC-LP5X + PHY-LP5X-N5 integration on 4 x 64-bit channels: init and training sequence, refresh/RFM, DFI low-power, inline ECC and scrub, FSP switch/DVFSC, command scheduling | Subsystem UVM with PHY model and LPDDR5X memory model, emulation (init flow) | Anjali Deshmukh |
| SEC | u_sec_encl | Secure-boot ROM flow, root-key load from OTP (u_otp_if, u_keyldr, u_secded), key ladder, AES-256-GCM, SHA-384, ECDSA P-384, TRNG, lifecycle | Block UVM, SoC boot tests, formal (lifecycle FSM), emulation, GLS | Ines Carvalho |
| AON | u_aon | Power-state FSM (ACTIVE, LP-IDLE, SLEEP, OFF), wake sources, fuse shadow, RTC, 25 MHz oscillator control | Block UVM, SoC power tests, formal (PMU FSM, fuse shadow), GLS | Kofi Mensah |
| PMUIF | u_core/u_pmu_if | Core-side wake and sleep handshakes with AON | SoC power tests, GLS | Kofi Mensah |
| PCIE0 | u_pcie0_wrap (u_ctl, u_l1ss_ctl) | Gen5 x16 endpoint: LTSSM, equalization, TLP layer, AER, MSI-X, SR-IOV, FLR/Hot Reset/PERST#, ASPM L0s/L1, L1.1, L1.2 | Subsystem UVM with PCIe Gen5 host VIP and PIPE PHY BFM, formal (u_l1ss_ctl), emulation | Leo Brandt |
| PCIE1 | u_pcie1_wrap | Fused off in ALX-5100 (FUSE_PCIE1_DIS=1): fuse decode, PD_PCIE1 power gating, clock gating, output isolation clamps | SoC UVM, formal (isolation) | Leo Brandt |
| PERIPH | u_periph | QSPI0 boot flash (133 MHz SDR), SPI1, I2C0/I2C1 with SMBus, UART0, GPIO | Block UVM with flash, I2C and UART models, SoC boot | Peripherals team |
| DBG | u_dbg, u_npu_top/u_trace_funnel | JTAG TAP, lifecycle-gated debug, NPU trace funnel | Block UVM, SoC | Viktor Halloran |
| CRG | u_core/u_crg | 4 fractional PLLs, dividers, reset sequencing, OCC controllers | SoC tests, formal (reset sequencer) | SoC integration team |

## 6. Covergroup plan

Targets per section 4.2. Escape-history per section 4.3. Excluded covergroups per section 8 (approved exclusion record in KST-COV-011).

| Covergroup | Block | Description | Tier | Escape-history | Target |
|---|---|---|---|---|---|
| cg_npu_dma_desc_types | NPU | DMA descriptor types (1D, 2D, 3D strided, scatter-gather, chained) x transfer size x alignment x channel (16 per cluster) | Tier-1 | - | 95.0% |
| cg_npu_dma_ring_wrap | NPU | Descriptor ring wrap at 4 KiB page boundary x ring size x prefetch depth x outstanding descriptors | Tier-1 | Escape-history (ALX4100-E01) | 95.0% |
| cg_npu_sparse_decomp_zero_blk | NPU | Sparse-weight decompressor block patterns incl. all-zero 64-byte block, back-to-back zero blocks, zero block at row end, per sparsity format (2:4, 1:4, bitmap) | Tier-1 | Escape-history (ALX4100-E14) | 95.0% |
| cg_npu_mac_dtypes | NPU | MAC array operand types (INT8, INT4, BF16, FP16) x accumulator precision x rounding/saturation mode | Tier-1 | - | 95.0% |
| cg_npu_tile_barrier | NPU | Inter-tile and inter-cluster barrier sync, barrier timeout, abort on error | Tier-1 | - | 95.0% |
| cg_npu_sram_ecc | NPU | Tile SRAM (4 MiB) SECDED: 1-bit correct, 2-bit detect, per bank, scrub interaction | Tier-1 | - | 95.0% |
| cg_npu_sram_bank_conflict | NPU | Tile SRAM bank-conflict patterns across MAC, DMA and decompressor ports | Tier-2 | - | 90.0% |
| cg_npu_act_lut | NPU | Activation LUT (ReLU, GELU, SiLU, sigmoid) segment interpolation, LUT reload while idle | Tier-2 | - | 90.0% |
| cg_npu_clk_gate | NPU | Tile clock-gate entry/exit, wake latency, gating with outstanding DMA | Tier-2 | - | 90.0% |
| cg_npu_trace_funnel | DBG | NPU trace funnel source select, FIFO overflow, multicycle-4 capture | Tier-3 | - | 80.0% |
| cg_gbuf_bank_arb | GBUF | Global buffer bank arbitration x requester class (NPU, DMA, CPU, PCIe) x conflict depth | Tier-2 | - | 90.0% |
| cg_gbuf_ecc | GBUF | SECDED correct/detect per bank, poison propagation to the NoC | Tier-1 | - | 95.0% |
| cg_noc_routing_xy | NOC | XY routing for all source/destination node pairs of the 4x4 mesh | Tier-1 | - | 95.0% |
| cg_noc_credit_flow | NOC | Credit return, back-pressure, credit-zero stall per port and VC | Tier-1 | - | 95.0% |
| cg_noc_qos_arb_weights | NOC | QoS weighted round-robin arbitration: WRR weight value (w0..w15) x VC x output port x number of contending inputs | Tier-2 | - | 90.0% |
| cg_noc_vc_alloc | NOC | Virtual-channel allocation and VC remap at router boundaries | Tier-2 | - | 90.0% |
| cg_noc_err_resp | NOC | Decode error, slave error, timeout and poison responses per initiator | Tier-1 | - | 95.0% |
| cg_cpu_boot_modes | CPU | Boot source (QSPI0 flash, PCIe host-load, secure recovery) x lifecycle state x boot straps | Tier-1 | - | 95.0% |
| cg_cpu_l2_ecc | CPU | 1 MiB L2 ECC: correct/detect per way, syndrome logging, scrub | Tier-1 | - | 95.0% |
| cg_cpu_plic_irq | CPU | PLIC priority/threshold/claim-complete across 31 sources (1..31; source 0 reserved), per hart, nesting | Tier-1 | - | 95.0% |
| cg_cpu_pmp_regions | CPU | PMP region modes (TOR, NA4, NAPOT) x permission x lock | Tier-2 | - | 90.0% |
| cg_cpu_debug_halt | CPU | Debug halt/resume, single-step, abstract commands per hart | Tier-2 | - | 90.0% |
| cg_mem_lp5x_training | MEM | LPDDR5X training steps (CBT, WCK2CK leveling, RDQS gate, read DQ, write DQ) x FSP x channel, retrain on DVFSC | Tier-1 | - | 95.0% |
| cg_mem_refresh_rfm | MEM | All-bank/per-bank refresh, postponed/pulled-in refresh, RFM at RAAIMT/RAAMMT, MR4 refresh-rate derating | Tier-1 | - | 95.0% |
| cg_mem_dfi_lp | MEM | DFI low-power control/data handshake, dfi_lp_wakeup values, handshake abort, per channel | Tier-1 | - | 95.0% |
| cg_mem_ecc_scrub | MEM | Inline ECC error injection and patrol-scrub rates | Tier-2 | - | 90.0% |
| cg_mem_fsp_switch | MEM | Frequency set-point switch (FSP-OP0/1) and DVFSC under traffic | Tier-2 | - | 90.0% |
| cg_mem_cmd_sched | MEM | Command scheduler: page policy, read/write turnaround, bank-group interleave, starvation limits | Tier-2 | - | 90.0% |
| cg_sec_boot_flow | SEC | Secure-boot ROM stages, image authentication pass/fail, anti-rollback, recovery path | Tier-1 | - | 95.0% |
| cg_sec_key_ladder | SEC | Root-key load from OTP (SECDED-corrected load, raw-read integrity compare on every cold boot, PROVISION raw read-back), derivation levels, zeroize | Tier-1 | - | 95.0% |
| cg_sec_otp_ecc | SEC | OTP read ECC: no error, 1-bit corrected, 2-bit detected, blank check, lock bits | Tier-1 | - | 95.0% |
| cg_sec_crypto_modes | SEC | AES-256-GCM (AAD/payload lengths, tag check), SHA-384, ECDSA P-384 sign/verify, error paths | Tier-1 | - | 95.0% |
| cg_sec_lifecycle | SEC | Lifecycle transitions TEST -> PROVISION -> PRODUCTION -> RMA incl. illegal requests | Tier-1 | - | 95.0% |
| cg_sec_trng_health | SEC | TRNG health tests (repetition count, adaptive proportion) and failure handling | Tier-2 | - | 90.0% |
| cg_aon_pwr_state_trans | AON | Power-state FSM transitions (ACTIVE, LP-IDLE, SLEEP, OFF), aborts, nested requests | Tier-1 | - | 95.0% |
| cg_aon_wake_sources | AON | Wake source (PCIe L1.2 exit request, GPIO, timer, SMBus alert) x originating power state x simultaneous wakes | Tier-1 | - | 95.0% |
| cg_aon_fuse_shadow_load | AON | Fuse-shadow load at POR, ECC, lock, readback (incl. FUSE_PCIE1_DIS) | Tier-1 | - | 95.0% |
| cg_aon_rtc_timer | AON | RTC alarm, wake timer, counter rollover | Tier-3 | - | 80.0% |
| cg_pcie0_ltssm | PCIE0 | LTSSM states and transitions x rate (Gen1-Gen5) x width, incl. Recovery, EQ, Hot Reset, Disabled, Loopback | Tier-1 | - | 95.0% |
| cg_pcie0_tlp_types | PCIE0 | TLP types (MRd, MWr, CplD, Msg, AtomicOp) x size x TC x ordering attributes | Tier-1 | - | 95.0% |
| cg_pcie0_aer | PCIE0 | AER correctable/uncorrectable errors, header log, error messages | Tier-1 | - | 95.0% |
| cg_pcie0_eq_presets | PCIE0 | Gen3/Gen4/Gen5 equalization phases, TX presets P0-P10, coefficient requests | Tier-1 | - | 95.0% |
| cg_pcie0_aspm_l1 | PCIE0 | ASPM L0s and L1 (no substate) entry/exit per rate | Tier-1 | - | 95.0% |
| cg_pcie0_l11_entry_exit | PCIE0 | L1 PM substate L1.1 entry/exit, CLKREQ# handshake, per link rate | Tier-1 | - | 95.0% |
| cg_pcie0_l12_entry_exit | PCIE0 | L1 PM substate L1.2 entry/exit incl. CLKREQ# handshake, T_POWER_ON, REFCLK stop/restart, per link rate | Tier-1 | Escape-history (ALX4100-E03, PM-2024-02) | 95.0% |
| cg_pcie0_reset_flr | PCIE0 | FLR, Hot Reset, PERST#, link-down reset and config-space recovery | Tier-1 | - | 95.0% |
| cg_pcie0_msix_sriov | PCIE0 | MSI-X vectors and masking, SR-IOV PF/VF (8 VFs) configuration | Tier-2 | - | 90.0% |
| cg_pcie1_ltssm | PCIE1 | LTSSM states and transitions, root-port mode | - | - | Excluded (CE-004) - PCIE1 fused off (FUSE_PCIE1_DIS) |
| cg_pcie1_tlp_types | PCIE1 | TLP types, root-port mode | - | - | Excluded (CE-004) - PCIE1 fused off (FUSE_PCIE1_DIS) |
| cg_pcie1_l1ss | PCIE1 | L1 PM substates L1.1/L1.2 | - | - | Excluded (CE-004) - PCIE1 fused off (FUSE_PCIE1_DIS) |
| cg_pcie1_cxl_io | PCIE1 | CXL.io protocol layer | - | - | Excluded (CE-004) - PCIE1 fused off (FUSE_PCIE1_DIS) |
| cg_pcie1_fuse_isolation | PCIE1 | FUSE_PCIE1_DIS decode, PD_PCIE1 power-gate, pcie1_core_clk gate, isolation clamp values, register access to the disabled controller | Tier-1 | - | 95.0% |
| cg_i2c_clk_stretch | PERIPH | I2C/SMBus target clock stretching, 25 ms SMBus timeout, stretch during ACK and data, per I2C0/I2C1 | Tier-1 | Escape-history (ALX4100-E05) | 95.0% |
| cg_i2c_smbus_proto | PERIPH | SMBus PEC, ARP, SMBALERT#, block read/write | Tier-2 | - | 90.0% |
| cg_qspi_boot_read | PERIPH | QSPI0 boot read modes (1-1-1, 1-1-4, 1-4-4 SDR at 133 MHz), dummy cycles, XIP | Tier-1 | - | 95.0% |
| cg_spi_modes | PERIPH | SPI1 CPOL/CPHA modes, chip-select timing, FIFO levels | Tier-3 | - | 80.0% |
| cg_uart_fifo_baud | PERIPH | UART0 baud divisors (integer and fractional DLF), FIFO thresholds, overrun/framing errors | Tier-3 | - | 95.0% (E11 integration hold, section 4.3) |
| cg_gpio_irq | PERIPH | GPIO interrupt modes (level, edge, both), debounce, per bank | Tier-2 | - | 90.0% |
| cg_crg_reset_seq | CRG | POR, warm, watchdog and software reset sequencing, reset during power-state transitions | Tier-1 | - | 95.0% |
| cg_crg_pll_lock | CRG | PLL lock/relock, SSC on/off ramp vs lock-detect, frequency change | Tier-1 | - | 95.0% |
| cg_dbg_jtag_tap | DBG | JTAG TAP instructions, lifecycle-gated debug access | Tier-3 | - | 80.0% |

Totals: 61 covergroups; Tier-1 37 (of which Escape-history 4), Tier-2 15, Tier-3 5, excluded 4 (CE-004).

## 7. cg_pcie0_l12_entry_exit coverage model

L1.2 is implemented by the in-house sequencer u_pcie0_wrap/u_l1ss_ctl (l1ss_ctl v3.0, redesigned after ALX4100-E03). It owns PCIE0_CLKREQ_N, the PHY PowerDown request to P1.2 and back, REFCLK-valid detection and the T_POWER_ON and Common_Mode_Restore_Time (T_COMMONMODE) timers, running on pcie_aux_clk (25 MHz) while REFCLK is off. The L1SS monitor samples the covergroup once per L1.2 residency, at L0 re-entry.

| Coverpoint / cross | Kind | Bins counted | Bins |
|---|---|---|---|
| cp_entry_trigger | coverpoint | 3 | aspm_l1_idle_timer, pci_pm_d3hot, host_directed |
| cp_exit_trigger | coverpoint | 6 | host_clkreq_assert, ep_data_pending, ep_wake, ltr_update, perst_assert, clkreq_reassert_during_tpoweron |
| cp_rate | coverpoint | 5 | gen1, gen2, gen3, gen4, gen5 (link rate at L1 entry) |
| cp_tpoweron | coverpoint | 4 | 10us, 40us, 70us, 130us (programmed T_POWER_ON; bins tpoweron_10us .. tpoweron_130us) |
| cp_ltr | coverpoint, cross input only (option.weight = 0) | 0 | ltr_below_thr, ltr_above_thr, ltr_no_req (against LTR_L1.2_THRESHOLD) |
| cp_b2b_entry | coverpoint, cross input only (option.weight = 0) | 0 | b2b_entry_lt_10us, b2b_entry_ge_10us (previous L1.2 exit to next entry) |
| cx_exit_trigger_x_rate | cross | 30 | '<trigger>__<rate>', e.g. host_clkreq_assert__gen1, clkreq_reassert_during_tpoweron__gen5 |
| cx_entry_x_exit | cross | 18 | '<entry>_x_<exit>', e.g. pci_pm_d3hot_x_ep_wake |
| cx_tpoweron_x_exit | cross | 24 | 'tpoweron_<t>_x_<exit>', e.g. tpoweron_130us_x_ltr_update |
| cx_tpoweron_x_rate | cross | 20 | 'tpoweron_<t>__<rate>', e.g. tpoweron_70us__gen5 |
| cx_entry_x_ltr | cross | 9 | '<entry>_x_<ltr>', e.g. pci_pm_d3hot_x_ltr_no_req |
| cx_b2b_x_rate | cross | 5 | 'b2b_entry_lt_10us__<rate>' (b2b_entry_ge_10us is ignore_bins) |
| **Total** | | **124** | |

Entry-trigger definitions: aspm_l1_idle_timer = ASPM L1 entry started by the endpoint's L1 entry idle timer; pci_pm_d3hot = PCI-PM L1 entry after the host programs the endpoint to D3hot; host_directed = PCI-PM L1 entry after the host programs the endpoint to D1 (PM_Enter_L1 DLLP), as opposed to pci_pm_d3hot.

Exit-trigger definitions: host_clkreq_assert = host asserts CLKREQ# to request exit; ep_data_pending = endpoint asserts CLKREQ# for a pending TLP; ep_wake = endpoint exit on a PMU wake event; ltr_update = exit to send an LTR message below LTR_L1.2_THRESHOLD; perst_assert = PERST# asserted during L1.2; clkreq_reassert_during_tpoweron = CLKREQ# de-asserted and re-asserted by the host while the endpoint T_POWER_ON timer is running.

Associated checks: SVA a_l1ss_entry_cond (LTR and CLKREQ# conditions for L1.2 entry), a_l1ss_tpoweron_min (no P1.2 exit request before T_POWER_ON has elapsed), a_l1ss_tcommon_mode, and the link-state scoreboard (no LTSSM transition to Detect on any L1.2 exit).

## 8. Exclusion and waiver policy

### 8.1 Coverage exclusions (CHK-VER-05)

Code or functional coverage may be excluded only for logic that is unreachable in the shipped SKU because it is fused off or tied off. Each exclusion requires (a) the fuse, tie-off or isolation logic that makes it unreachable to be verified to >= 95% (covergroup, formal proof or both), (b) a dated record approved by the Verification Lead and the Chief Architect, and (c) an ID CE-nnn recorded in KST-COV-011 section 8. Exclusions are applied as version-controlled exclusion files (cov_excl/CE-nnn.el), never as manual edits in the coverage database.

| ID | Scope | Basis |
|---|---|---|
| CE-001 | CPU debug-ROM patch slots 8-15 (u_cpu) | Patch-enable inputs tied off at CPU integration; slots unused in ALX-5100 |
| CE-002 | LPDDR4X legacy mode in MC-LP5X (u_ddr_ss/u_mc0..u_mc3) | Memory-type strap tied off to LPDDR5X |
| CE-003 | UART0 IrDA SIR mode (u_periph/u_uart0) | irda_en tied off |
| CE-004 | PCIE1 (u_pcie1_wrap); cg_pcie1_ltssm, cg_pcie1_tlp_types, cg_pcie1_l1ss, cg_pcie1_cxl_io | Fused off (FUSE_PCIE1_DIS=1), PD_PCIE1 power-gated, outputs isolated; isolation covered by cg_pcie1_fuse_isolation |
| CE-005 | NoC router ports facing the mesh edge (u_noc, 16 ports) | Tied off by the NoC generator configuration |
| CE-006 | MBIST-only test-mux legs of SRAM wrappers (NPU, GBUF, CPU L2) | Functional-simulation coverage only; legs exercised by MBIST pattern simulation (CHK-DFT-02) and at ATE; in the shipped SKU (PRODUCTION lifecycle) the select is forced inactive by the lifecycle fuse gate |

### 8.2 Coverage waivers (CHK-VER-08)

A coverage waiver accepts a Tier-1 or Tier-2 covergroup below target for tape-out. Waivers are permitted only for covergroups that are not Escape-history. Each waiver needs a written risk assessment (uncovered bins, failure mode, post-silicon detectability, workaround) and must be signed by the Verification Lead and the Chief Architect before the TRR at which it is used. IDs are CW-<block>-nnn, recorded in KST-COV-011 section 9.

### 8.3 Escape-history covergroups (CHK-VER-07)

Escape-history covergroups (section 4.3) must reach 95.0%. No coverage waiver and no bin exclusion may be applied to them.

## 9. Key directed tests

### 9.1 PCIE0 L1 PM substates tests at package A (selection)

| Test | Scenario | Rates |
|---|---|---|
| l11_basic_entry_exit | ASPM L1.1 entry via idle timer, exit by host CLKREQ# assertion | Gen1-Gen5 |
| l12_basic_entry_exit | L1.2 entry via ASPM idle timer (LTR above threshold), REFCLK stop/restart, exit by host CLKREQ# assertion; T_POWER_ON randomized | Gen1-Gen5 |
| l12_ep_data_pending_exit | Endpoint-initiated exit for a pending TLP | Gen1-Gen4 |
| l12_ep_wake_exit | Exit on endpoint PMU wake event | Gen1-Gen3 |
| l12_ltr_update_exit | Exit to send LTR below LTR_L1.2_THRESHOLD | Gen1-Gen3 |
| l12_perst_in_l12 | PERST# asserted while in L1.2 | Gen1-Gen2 (rate drawn per seed) |
| l12_d3hot_entry | L1.2 entry after PCI-PM D3hot, exit by host | Gen1-Gen5 |
| l12_host_directed | Host-directed L1 entry with L1.2 enabled, LTR sweep | Gen1-Gen5 |
| l12_b2b_entry | Back-to-back L1.2 entry less than 10 us after exit | Gen1 |

### 9.2 TB-B-001: L1.2 closure sequences (package B)

TB-B-001 (testbench change, merged 2026-08-17 .. 2026-08-21; KST-ECO-062) adds 14 directed L1.2 sequences and a constrained-random L1SS sequence library to close cg_pcie0_l12_entry_exit (TRR-1 actions AI-01, AI-02). Owner: Leo Brandt with the PCIe verification team; review: Tomasz Wierzbicki.

| # | Sequence | Scenario | Rates | Target bins |
|---|---|---|---|---|
| 1 | l12_clkreq_tpoweron_gen1 | Host de-asserts and re-asserts CLKREQ# inside the T_POWER_ON window, offset swept 0-10 us | Gen1 | clkreq_reassert_during_tpoweron__gen1 |
| 2 | l12_clkreq_tpoweron_gen2 | As 1 | Gen2 | clkreq_reassert_during_tpoweron__gen2 |
| 3 | l12_clkreq_tpoweron_gen3 | As 1 | Gen3 | clkreq_reassert_during_tpoweron__gen3 |
| 4 | l12_clkreq_tpoweron_gen4 | As 1 | Gen4 | clkreq_reassert_during_tpoweron__gen4 |
| 5 | l12_clkreq_tpoweron_sweep | Re-assert inside T_POWER_ON for T_POWER_ON 10/40/70/130 us and all three entry triggers | Gen1-Gen4 | tpoweron_*_x_clkreq_reassert_during_tpoweron, *_x_clkreq_reassert_during_tpoweron |
| 6 | l12_ltr_update_exit_gen4 | Exit to send LTR below threshold | Gen4 | ltr_update__gen4 |
| 7 | l12_ep_wake_exit_gen4 | Endpoint wake exit, T_POWER_ON 130 us | Gen4 | ep_wake__gen4, tpoweron_130us_x_ep_wake |
| 8 | l12_ep_data_pending_gen5 | Pending-TLP exit, T_POWER_ON 70/130 us | Gen5 | ep_data_pending__gen5, tpoweron_130us_x_ep_data_pending, tpoweron_70us__gen5, tpoweron_130us__gen5 |
| 9 | l12_perst_in_l12_gen3 | PERST# asserted in L1.2, T_POWER_ON 70 us | Gen3 | perst_assert__gen3, tpoweron_70us_x_perst_assert |
| 10 | l12_b2b_entry_gen2 | Back-to-back entry less than 10 us after exit | Gen2 | b2b_entry_lt_10us__gen2 |
| 11 | l12_host_directed_ltr_update | Host-directed entry, exit on LTR update | Gen1-Gen3 | host_directed_x_ltr_update |
| 12 | l12_d3hot_ltr_no_req | D3hot entry with LTR 'no requirement' | Gen1-Gen3 | pci_pm_d3hot_x_ltr_no_req |
| 13 | l12_tpoweron_130us_gen4 | Host-initiated exit with T_POWER_ON 130 us | Gen4 | tpoweron_130us__gen4 |
| 14 | l12_entry_abort_clkreq | L1.2 entry aborted by CLKREQ# assertion before REFCLK stop | Gen1-Gen5 | Checker scenario (no new bins) |

Constrained-random library l1ss_cr_lib: randomizes entry trigger, exit trigger (including CLKREQ# re-assert inside T_POWER_ON), T_POWER_ON, LTR value and back-to-back spacing; Gen1-Gen4; 400 seeds per nightly. The library weights PERST# assertion and back-to-back re-entry below 10 us low (both end or reset the L1.2 residency), so their per-rate bins are closed by directed sequences 9 and 10. Sequences 9 and 10 run at Gen3 and Gen2 in this package and their higher-rate variants are planned. The Gen5 variant of the CLKREQ# re-assert sequences (1-4) is planned with the PIPE PHY BFM Gen5 P1.2 exit-latency update (refclk_valid timing after PLL relock); Gen5 variants of sequences 6 and 7 are planned.

## 10. TRR sign-off criteria

| Rule | Criterion | Evidence (KST-COV-011) |
|---|---|---|
| CHK-VER-01 | Line >= 98.0%, branch >= 95.0%, toggle >= 95.0%, FSM state 100%, FSM transition >= 95.0% per block after approved exclusions | Section 5 |
| CHK-VER-02 | Tier-1 >= 95.0%, Tier-2 >= 90.0%, Tier-3 >= 80.0% (non-blocking) per covergroup | Sections 6 and 7 |
| CHK-VER-03 | 0 open P1/P2 bugs; every P3 triaged with an owner | Section 4 |
| CHK-VER-04 | >= 99.5% pass rate on 3 consecutive nightlies | Section 3 |
| CHK-VER-05 | Approved exclusion record for every exclusion | Section 8 |
| CHK-VER-06 | SDF GLS at min and max corners passes boot, reset and low-power entry/exit | Section 10 |
| CHK-VER-07 | Escape-history covergroups (this plan, section 4.3) >= 95.0%, no waivers | Section 6 |
| CHK-VER-08 | Coverage waivers signed before TRR | Section 9 |

## 11. Approvals

| Role | Name | Date |
|---|---|---|
| Verification Lead (owner) | Tomasz Wierzbicki | 2026-09-01 |
| Chief Architect | Priya Raghavan | 2026-09-01 |
| PCIe Subsystem Owner | Leo Brandt | 2026-09-01 |
| Memory Subsystem Owner | Anjali Deshmukh | 2026-09-01 |
| Security Enclave Owner | Ines Carvalho | 2026-09-01 |
| PMU / Always-on Domain Owner | Kofi Mensah | 2026-09-01 |
| NPU Cluster Owner | Viktor Halloran | 2026-09-01 |

## Revision history

| Rev | Date | Author | Change |
|---|---|---|---|
| A | 2026-08-10 | Tomasz Wierzbicki | Released for TRR-1 (netlist kst_top_nl_2026.08.07) |
| B | 2026-09-01 | Tomasz Wierzbicki | TB-B-001 L1.2 tests added (section 9.2: 14 directed sequences and constrained-random L1SS library); results in KST-COV-011 rev B; GLS netlist kst_top_nl_2026.08.31; section 3.6: nightly /64 PMU wake regression added (ECO-B-005) |
