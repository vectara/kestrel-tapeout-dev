# KESTREL ECO & Change Log

| Field | Value |
|---|---|
| Doc ID | KST-ECO-062 |
| Title | ECO & Change Log |
| Revision | A |
| Date | 2026-08-13 |
| Owner | Daniel Achterberg (PD Lead) |
| Status | Released for TRR-1 |
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

## 5. Netlist releases

| Netlist | Date | Contents | Sign-off |
|---|---|---|---|
| kst_top_nl_2026.07.17 | 2026-07-17 | Synthesis of RTL tag kst_rtl_2026.07.15 | Pre-ECO baseline |
| kst_top_nl_2026.08.07 | 2026-08-07 | kst_top_nl_2026.07.17 + ECO-A-001..ECO-A-007 | Package A: full 14-view MCMM STA, CDC/RDC, LEC and DRC/LVS re-run dated 2026-08-08 to 2026-08-12 |

## 6. ECO resources

| Resource | Status after package A |
|---|---|
| Spare / gate-array ECO filler density | 1.5% retained (0 consumed by package A ECOs) |
| Spare flops per partition | 0.4% of partition flop count, distributed on a 60 um grid |
| Always-on island pcie_aux_clk (u_pcie0_wrap/u_l1ss_ctl, PHY power-state control) | 6 spare flops and about 90 gate-array filler sites (island area-limited; below the partition average) |
| Metal-only ECO scope | Pre-placed spare cells (DFF, DLY2/DLY4, NAND/NOR/MUX) rewired from V1/M2 up; gate-array ECO fillers personalized from V0/M0-M1 up; a metal-only ECO re-cuts the via and metal masks from the lowest layer it touches up to about M8 (about 16-24 masks including several EUV layers); FEOL and MOL masks are reused (ALD-QA-CHK-007 section 4.2) |

## 7. Open change requests

None at package A freeze (2026-08-13). Requests raised after TRR-1 are handled in the ECO window 2026-08-17 to 2026-08-30.
