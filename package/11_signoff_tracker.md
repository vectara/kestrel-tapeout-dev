# KESTREL Sign-off Tracker

| Field | Value |
|---|---|
| Doc ID | KST-TRK-061 |
| Title | Sign-off Tracker |
| Revision | B (supersedes A) |
| Date | 2026-09-03 |
| Owner | Marcus Oyelaran (Program Manager) |
| Status | Released for TRR-2 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Scope

This tracker records the sign-off status of tape-out package B (netlist kst_top_nl_2026.08.31) for TRR-2 on 2026-09-04. Each row is self-reported by the named owner against the ALD-QA-CHK-007 rev 7.2 rules listed in the row. Supporting evidence is in the referenced package documents.

Status legend:

| Status | Meaning |
|---|---|
| GREEN | Signed off by the owner against the listed rules on the listed date |
| YELLOW | Not yet signed off; closure plan and date agreed |
| RED | Not signed off; no agreed closure plan |

Per CHK-GOV-01 a YELLOW or RED row counts as not signed off.

## 2. Summary

| Status | Rows |
|---|---|
| GREEN | 26 |
| YELLOW | 1 |
| RED | 0 |
| Total | 27 |

## 3. Sign-off rows

| Area | Item | Rule IDs | Owner | Status | Sign-off date | Notes |
|---|---|---|---|---|---|---|
| Spec | Architecture spec KST-ARCH-001 | CHK-SPEC-01, CHK-SPEC-04 | Priya Raghavan | GREEN | 2026-08-31 | Rev B released (revision alignment, no functional change); Tj -40 C to +125 C covered by sign-off corners |
| Spec | Package / pinout / IO spec KST-PKG-002 | CHK-SPEC-01, CHK-SPEC-02, CHK-SPEC-03 | Rachel Lindqvist | GREEN | 2026-09-01 | Rev B: CHG-B-001 (TP_0..TP_5), CHG-B-002 (GPIO_B IO_GPIO_1V8, VDDIO_B 1.8 V); 2,304-ball map; 0 unassigned signals; 4 GPIO banks, 52 GPIO pins |
| IP | IP BOM KST-IPBOM-050 | CHK-IP-01, CHK-IP-02 | Beatriz Solano | GREEN | 2026-08-31 | 25 line items, all production-qualified; MC-LP5X / PHY-LP5X-N5 v2.7.0 (ECO-B-004); netlist hash check 25/25 match |
| IP | Previous-generation errata review (ALX4100-ERR) | CHK-IP-03 | Beatriz Solano | GREEN | 2026-08-31 | E01..E14 re-reviewed; 10 carry-forward items resolved by IP version, ALX4100-E07 by v2.7.0 (LPX-1182); E03 in-house l1ss_ctl v3.0, verification under the functional-coverage row |
| Verification | Verification plan KST-VPLAN-010 | CHK-VER-02, CHK-VER-07 | Tomasz Wierzbicki | GREEN | 2026-09-01 | Tier and escape-history classification unchanged |
| Verification | Code coverage | CHK-VER-01 | Tomasz Wierzbicki | GREEN | 2026-09-02 | All blocks meet line 98.0% / branch 95.0% / toggle 95.0% / FSM targets after approved exclusions |
| Verification | Functional coverage | CHK-VER-02, CHK-VER-05, CHK-VER-07, CHK-VER-08 | Tomasz Wierzbicki | YELLOW | - | PCIe L1.2 91.1%, waiver CW-PCIE-003 pending (requested 2026-09-02, Leo Brandt); all other Tier-1/Tier-2 at target; CE-004 (PCIE1 fused off) approved 2026-07-21 |
| Verification | Nightly regression | CHK-VER-04 | Tomasz Wierzbicki | GREEN | 2026-09-02 | 99.6%; 3 consecutive nightlies at or above 99.5% |
| Verification | Bug database | CHK-VER-03 | Tomasz Wierzbicki | GREEN | 2026-09-02 | 0 open P1/P2; all P3 triaged with owner |
| Verification | Gate-level simulation (SDF) | CHK-VER-06 | Tomasz Wierzbicki | GREEN | 2026-09-02 | Boot, reset and low-power entry/exit tests pass; ECO-B-003 partition (SEC) re-run with min-corner SDF; ECO-B-005 partition (PMUIF) re-run at both corners |
| STA | Setup, functional views | CHK-STA-01, CHK-STA-03, CHK-STA-07 | Mei-Lin Chou | GREEN | 2026-09-02 | 14/14 views; SI + POCV; post-ECO incremental timing clean |
| STA | Hold, all views | CHK-STA-02, CHK-STA-03 | Mei-Lin Chou | GREEN | 2026-09-02 | 14/14 views; hold closed by ECO-B-003; W-017 withdrawn |
| STA | Timing waivers KST-STA-021 | CHK-STA-05, CHK-STA-06 | Mei-Lin Chou | GREEN | 2026-09-02 | 24 waivers logged, 23 active; W-017 withdrawn (ECO-B-003); test-mode false paths per KST-DFT-EXC |
| STA | DRV (max transition / max capacitance) | CHK-STA-04 | Jonah Pike | GREEN | 2026-09-02 | 0 unwaived; DRV waivers on tie-off / spare-cell nets only |
| CDC | CDC structural + formal | CHK-CDC-01, CHK-CDC-02, CHK-CDC-03, CHK-CDC-04, CHK-CDC-06 | Hiroshi Tanabe | GREEN | 2026-09-02 | 1,286 crossings; 1,244 clean; 42 waived; 0 unwaived; W-CDC-022 withdrawn (ECO-B-005) |
| CDC | RDC | CHK-CDC-05 | Hiroshi Tanabe | GREEN | 2026-09-02 | 0 unwaived RDC violations |
| PI | Static IR drop | CHK-PI-01 | Grace Adeyemi | GREEN | 2026-09-02 | All rails at or below 2.5%; worst VDD_NPU 1.6% (12.0 mV) |
| PI | Dynamic IR drop | CHK-PI-02 | Grace Adeyemi | GREEN | 2026-09-02 | All rails within budget; VDD_NPU 7.4% vs 8.0%, VDD_CORE 5.2%, VDD_SRAM 4.1%, VDD_AON 1.2% |
| PI | Electromigration | CHK-PI-03 | Grace Adeyemi | GREEN | 2026-09-02 | 0 violations at Tj 110 C, 10-year lifetime |
| PV | DRC incl. density | CHK-PV-01 | Daniel Achterberg | GREEN | 2026-09-02 | Foundry N5-class sign-off deck; 0 violations; includes CHG-B-002 pad ring and PHY-LP5X-N5 v2.7.0 macro |
| PV | LVS | CHK-PV-01 | Daniel Achterberg | GREEN | 2026-09-02 | Clean, top level and all hard macros |
| PV | ERC / antenna | CHK-PV-01 | Daniel Achterberg | GREEN | 2026-09-02 | 0 violations |
| PV | ESD / latch-up | CHK-PV-02 | Rachel Lindqvist | GREEN | 2026-09-01 | HBM 1 kV / CDM 250 V checks and latch-up rules clean on all pads incl. hard-macro pads (vendor ESD reports cross-checked with discharge-path analysis); pad ring re-checked after CHG-B-002 |
| PD | Formal equivalence (RTL vs netlist) | PD flow (no checklist rule) | Daniel Achterberg | GREEN | 2026-08-31 | kst_top_nl_2026.08.31 equivalent to RTL tag incl. ECO-B-001..006 |
| DFT | ATPG | CHK-DFT-01 | Samir Haddad | GREEN | 2026-09-02 | Stuck-at 99.2%, transition 96.1% (re-run on kst_top_nl_2026.08.31) |
| DFT | MBIST | CHK-DFT-02 | Samir Haddad | GREEN | 2026-09-02 | 100% SRAM instances; repair on NPU and GBUF macros |
| Governance | Package revision alignment | CHK-SPEC-01 | Marcus Oyelaran | GREEN | 2026-09-03 | All 11 pre-TRR package documents at revision B; minutes KST-TRR-060 rev B issued after TRR-2 |

## 4. Open items

| Row | Item | Owner | Plan | Target |
|---|---|---|---|---|
| Functional coverage | cg_pcie0_l12_entry_exit at 91.1%; coverage waiver CW-PCIE-003 pending | Tomasz Wierzbicki / Leo Brandt | Waiver decision by Chief Architect at TRR-2 (2026-09-04); closure work continues | TRR-2 (2026-09-04) |

## 5. Referenced documents (package B)

| Doc ID | Title | Revision | Date |
|---|---|---|---|
| KST-ARCH-001 | Architecture Specification | B | 2026-08-31 |
| KST-PKG-002 | Package, Pinout and I/O Specification | B | 2026-09-01 |
| KST-VPLAN-010 | Verification Plan | B | 2026-09-01 |
| KST-COV-011 | Coverage Report | B | 2026-09-02 |
| KST-STA-020 | STA Sign-off Report | B | 2026-09-02 |
| KST-STA-021 | Timing Waiver Log | B | 2026-09-02 |
| KST-CDC-030 | CDC/RDC Report | B | 2026-09-02 |
| KST-PI-040 | Power Integrity Report | B | 2026-09-02 |
| KST-IPBOM-050 | IP BOM | B | 2026-08-31 |
| KST-ECO-062 | ECO & Change Log | B | 2026-09-03 |

## 6. Physical-verification and DFT run record

Tool reports are held in the sign-off database. This table is the evidence of record for CHK-PV-01, CHK-PV-02 (chip level) and CHK-DFT-01..02 (ALD-QA-CHK-007 section 3.4).

| Rule | Check | Run ID | Tool / deck | Input | Log | Run date | Result |
|---|---|---|---|---|---|---|---|
| CHK-PV-01 | DRC incl. density | pv_kst_0902_drc | Physical verification tool, foundry N5-class sign-off deck | kst_top_pnr_2026.08.31 (GDS, post-metal-fill) | signoff/pv/pv_kst_0902_drc/drc.sum | 2026-09-02 | 0 violations |
| CHK-PV-01 | LVS | pv_kst_0902_lvs | Physical verification tool, foundry N5-class LVS deck | kst_top_pnr_2026.08.31 vs kst_top_nl_2026.08.31, top level and all hard macros | signoff/pv/pv_kst_0902_lvs/lvs.rep | 2026-09-02 | Clean (0 unmatched nets or devices) |
| CHK-PV-01 | ERC / antenna | pv_kst_0902_erc_ant | Physical verification tool, foundry N5-class sign-off deck | kst_top_pnr_2026.08.31 | signoff/pv/pv_kst_0902_erc_ant/erc_ant.sum | 2026-09-02 | 0 violations |
| CHK-PV-02 | ESD network (HBM 1 kV, CDM 250 V) and latch-up, chip level | pv_kst_0901_esd_lu | Physical verification tool, foundry ESD/latch-up rule deck | kst_top_pnr_2026.08.31: pad ring, core and all hard-macro pads (PCIE5-PHY-N5 x2, PHY-LP5X-N5 x4 incl. v2.7.0 macro pads after ECO-B-004, PLL/OTP/PVT analog pins) | signoff/pv/pv_kst_0901_esd_lu/esd_lu.sum | 2026-09-01 | 0 violations |
| CHK-DFT-01 | ATPG stuck-at and transition | atpg_kst_0902 | ATPG tool | kst_top_nl_2026.08.31, pattern set v0.9.1 (v0.9 regenerated on this netlist) | signoff/dft/atpg_kst_0902/coverage.rpt | 2026-09-02 | Stuck-at 99.2%, transition 96.1% |
| CHK-DFT-02 | MBIST insertion and pattern simulation | mbist_kst_0902 | MBIST tool + logic simulator | kst_top_nl_2026.08.31 | signoff/dft/mbist_kst_0902/mbist.rpt | 2026-09-02 | 3,412/3,412 SRAM instances tested, 0 failures; repair enabled on NPU and GBUF macros |

## 7. Revision history

| Rev | Date | Changes |
|---|---|---|
| A | 2026-08-13 | Baseline for TRR-1 (package A, netlist kst_top_nl_2026.08.07): 26 GREEN, 1 YELLOW (functional coverage) |
| B | 2026-09-03 | Updated for TRR-2 (package B, netlist kst_top_nl_2026.08.31): all rows re-signed on revision B documents; package row updated for CHG-B-001/CHG-B-002; IP BOM and errata rows updated for ECO-B-004; STA hold and waiver rows updated for ECO-B-003 (W-017 withdrawn); CDC row updated for ECO-B-005 (W-CDC-022 withdrawn); functional coverage 91.1% with CW-PCIE-003 pending (row stays YELLOW) |
