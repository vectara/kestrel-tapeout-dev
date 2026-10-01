# KESTREL Sign-off Tracker

| Field | Value |
|---|---|
| Doc ID | KST-TRK-061 |
| Title | Sign-off Tracker |
| Revision | C (supersedes B) |
| Date | 2026-09-24 |
| Owner | Marcus Oyelaran (Program Manager) |
| Status | Released for TRR-3 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Scope

This tracker records the sign-off status of tape-out package C (netlist kst_top_nl_2026.09.19) for TRR-3 on 2026-09-25. Each row is self-reported by the named owner against the ALD-QA-CHK-007 rev 7.2 rules listed in the row. Supporting evidence is in the referenced package documents.

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
| GREEN | 27 |
| YELLOW | 0 |
| RED | 0 |
| Total | 27 |

## 3. Sign-off rows

| Area | Item | Rule IDs | Owner | Status | Sign-off date | Notes |
|---|---|---|---|---|---|---|
| Spec | Architecture spec KST-ARCH-001 | CHK-SPEC-01, CHK-SPEC-04 | Priya Raghavan | GREEN | 2026-09-22 | Rev C released (revision alignment, no functional change); Tj -40 C to +125 C covered by sign-off corners |
| Spec | Package / pinout / IO spec KST-PKG-002 | CHK-SPEC-01, CHK-SPEC-02, CHK-SPEC-03 | Rachel Lindqvist | GREEN | 2026-09-22 | Rev C, no change since B (CHG-B-001, CHG-B-002 retained); 2,304-ball map; 0 unassigned signals; 4 GPIO banks, 52 GPIO pins |
| IP | IP BOM KST-IPBOM-050 | CHK-IP-01, CHK-IP-02 | Beatriz Solano | GREEN | 2026-09-22 | 25 line items, all production-qualified; MC-LP5X / PHY-LP5X-N5 v2.7.0; l1ss_ctl v3.0.1 (ECO-C-003); netlist hash check 25/25 on kst_top_nl_2026.09.19 |
| IP | Previous-generation errata review (ALX4100-ERR) | CHK-IP-03 | Beatriz Solano | GREEN | 2026-09-22 | 11 carry-forward items resolved; ALX4100-E03 design fix re-verified (l1ss_ctl v3.0.1 = v3.0 + ECO-C-003) |
| Verification | Verification plan KST-VPLAN-010 | CHK-VER-02, CHK-VER-07 | Tomasz Wierzbicki | GREEN | 2026-09-22 | Tier and escape-history classification unchanged; l12_clkreq_tpoweron_gen5 added to the L1.2 test list |
| Verification | Code coverage | CHK-VER-01 | Tomasz Wierzbicki | GREEN | 2026-09-23 | All blocks meet line 98.0% / branch 95.0% / toggle 95.0% / FSM targets after approved exclusions |
| Verification | Functional coverage | CHK-VER-02, CHK-VER-05, CHK-VER-07, CHK-VER-08 | Tomasz Wierzbicki | GREEN | 2026-09-23 | PCIe L1.2 96.8% (120/124), Tier-1 target met; CW-PCIE-003 withdrawn 2026-09-22; all Tier-1/Tier-2 at target; CE-004 (PCIE1 fused off) approved 2026-07-21 |
| Verification | Nightly regression | CHK-VER-04 | Tomasz Wierzbicki | GREEN | 2026-09-23 | 99.8%; 3 consecutive nightlies at or above 99.5% |
| Verification | Bug database | CHK-VER-03 | Tomasz Wierzbicki | GREEN | 2026-09-23 | 0 open P1/P2 (PCIE-1187 P1 opened 2026-09-10, closed 2026-09-17 by ECO-C-003); all P3 triaged with owner |
| Verification | Gate-level simulation (SDF) | CHK-VER-06 | Tomasz Wierzbicki | GREEN | 2026-09-23 | Boot, reset, low-power and PCIe L1.2 entry/exit tests pass at min and max SDF corners on kst_top_nl_2026.09.19 |
| STA | Setup, functional views | CHK-STA-01, CHK-STA-03, CHK-STA-07 | Mei-Lin Chou | GREEN | 2026-09-23 | Full 14/14-view MCMM on kst_top_nl_2026.09.19; SI + POCV; ECO-C-002 included |
| STA | Hold, all views | CHK-STA-02, CHK-STA-03 | Mei-Lin Chou | GREEN | 2026-09-23 | Full 14/14-view MCMM on kst_top_nl_2026.09.19; ECO-C-002 included |
| STA | Timing waivers KST-STA-021 | CHK-STA-05, CHK-STA-06 | Mei-Lin Chou | GREEN | 2026-09-23 | 24 waivers logged, 23 active, all four fields complete; W-017 withdrawn (ECO-B-003, superseded by ECO-C-002); test-mode false paths per KST-DFT-EXC |
| STA | DRV (max transition / max capacitance) | CHK-STA-04 | Jonah Pike | GREEN | 2026-09-23 | 0 unwaived; DRV waivers on tie-off / spare-cell nets only |
| CDC | CDC structural + formal | CHK-CDC-01, CHK-CDC-02, CHK-CDC-03, CHK-CDC-04, CHK-CDC-06 | Hiroshi Tanabe | GREEN | 2026-09-23 | Re-run on kst_top_nl_2026.09.19: 1,286 crossings; 1,244 clean; 42 waived; 0 unwaived |
| CDC | RDC | CHK-CDC-05 | Hiroshi Tanabe | GREEN | 2026-09-23 | 0 unwaived RDC violations |
| PI | Static IR drop | CHK-PI-01 | Grace Adeyemi | GREEN | 2026-09-23 | All rails at or below 2.5%; worst VDD_NPU 1.6% (12.0 mV) |
| PI | Dynamic IR drop | CHK-PI-02 | Grace Adeyemi | GREEN | 2026-09-23 | All rails within budget; VDD_NPU 7.4% vs 8.0%, VDD_CORE 5.2%, VDD_SRAM 4.1%, VDD_AON 1.2% |
| PI | Electromigration | CHK-PI-03 | Grace Adeyemi | GREEN | 2026-09-23 | 0 violations at Tj 110 C, 10-year lifetime |
| PV | DRC incl. density | CHK-PV-01 | Daniel Achterberg | GREEN | 2026-09-23 | Foundry N5-class sign-off deck; 0 violations on the final layout |
| PV | LVS | CHK-PV-01 | Daniel Achterberg | GREEN | 2026-09-23 | Clean, top level and all hard macros |
| PV | ERC / antenna | CHK-PV-01 | Daniel Achterberg | GREEN | 2026-09-23 | 0 violations |
| PV | ESD / latch-up | CHK-PV-02 | Rachel Lindqvist | GREEN | 2026-09-23 | HBM 1 kV / CDM 250 V checks and latch-up rules clean on all pads incl. hard-macro pads (vendor ESD reports cross-checked with discharge-path analysis) |
| PD | Formal equivalence (RTL vs netlist) | PD flow (no checklist rule) | Daniel Achterberg | GREEN | 2026-09-22 | kst_top_nl_2026.09.19 equivalent to RTL tag incl. ECO-C-001..003 |
| DFT | ATPG | CHK-DFT-01 | Samir Haddad | GREEN | 2026-09-23 | Stuck-at 99.2%, transition 96.1% (pattern set v1.0 on kst_top_nl_2026.09.19) |
| DFT | MBIST | CHK-DFT-02 | Samir Haddad | GREEN | 2026-09-23 | 100% SRAM instances; repair on NPU and GBUF macros |
| Governance | Package revision alignment and post-ECO re-sign-off | CHK-SPEC-01, CHK-GOV-02 | Marcus Oyelaran | GREEN | 2026-09-24 | All 11 pre-TRR package documents at revision C; minutes KST-TRR-060 rev C issued after TRR-3; re-sign-off runs dated after the last ECO (see KST-ECO-062 rev C) |

## 4. Open items

None. All rows GREEN for TRR-3.

## 5. Referenced documents (package C)

| Doc ID | Title | Revision | Date |
|---|---|---|---|
| KST-ARCH-001 | Architecture Specification | C | 2026-09-21 |
| KST-PKG-002 | Package, Pinout and I/O Specification | C | 2026-09-21 |
| KST-VPLAN-010 | Verification Plan | C | 2026-09-22 |
| KST-COV-011 | Coverage Report | C | 2026-09-23 |
| KST-STA-020 | STA Sign-off Report | C | 2026-09-23 |
| KST-STA-021 | Timing Waiver Log | C | 2026-09-23 |
| KST-CDC-030 | CDC/RDC Report | C | 2026-09-23 |
| KST-PI-040 | Power Integrity Report | C | 2026-09-23 |
| KST-IPBOM-050 | IP BOM | C | 2026-09-21 |
| KST-ECO-062 | ECO & Change Log | C | 2026-09-24 |

## 6. Physical-verification and DFT run record

Tool reports are held in the sign-off database. This table is the evidence of record for CHK-PV-01, CHK-PV-02 (chip level) and CHK-DFT-01..02 (ALD-QA-CHK-007 section 3.4).

| Rule | Check | Run ID | Tool / deck | Input | Log | Run date | Result |
|---|---|---|---|---|---|---|---|
| CHK-PV-01 | DRC incl. density | pv_kst_0923_drc | Physical verification tool, foundry N5-class sign-off deck | kst_top_pnr_2026.09.19 (GDS, post-metal-fill) | signoff/pv/pv_kst_0923_drc/drc.sum | 2026-09-23 | 0 violations |
| CHK-PV-01 | LVS | pv_kst_0923_lvs | Physical verification tool, foundry N5-class LVS deck | kst_top_pnr_2026.09.19 vs kst_top_nl_2026.09.19, top level and all hard macros | signoff/pv/pv_kst_0923_lvs/lvs.rep | 2026-09-23 | Clean (0 unmatched nets or devices) |
| CHK-PV-01 | ERC / antenna | pv_kst_0923_erc_ant | Physical verification tool, foundry N5-class sign-off deck | kst_top_pnr_2026.09.19 | signoff/pv/pv_kst_0923_erc_ant/erc_ant.sum | 2026-09-23 | 0 violations |
| CHK-PV-02 | ESD network (HBM 1 kV, CDM 250 V) and latch-up, chip level | pv_kst_0923_esd_lu | Physical verification tool, foundry ESD/latch-up rule deck | kst_top_pnr_2026.09.19: pad ring, core and all hard-macro pads (PCIE5-PHY-N5 x2, PHY-LP5X-N5 x4, PLL/OTP/PVT analog pins) | signoff/pv/pv_kst_0923_esd_lu/esd_lu.sum | 2026-09-23 | 0 violations |
| CHK-DFT-01 | ATPG stuck-at and transition | atpg_kst_0923 | ATPG tool | kst_top_nl_2026.09.19, pattern set v1.0 | signoff/dft/atpg_kst_0923/coverage.rpt | 2026-09-23 | Stuck-at 99.2%, transition 96.1% |
| CHK-DFT-02 | MBIST insertion and pattern simulation | mbist_kst_0923 | MBIST tool + logic simulator | kst_top_nl_2026.09.19 | signoff/dft/mbist_kst_0923/mbist.rpt | 2026-09-23 | 3,412/3,412 SRAM instances tested, 0 failures; repair enabled on NPU and GBUF macros |

## 7. Revision history

| Rev | Date | Changes |
|---|---|---|
| A | 2026-08-13 | Baseline for TRR-1 (package A, netlist kst_top_nl_2026.08.07): 26 GREEN, 1 YELLOW (functional coverage) |
| B | 2026-09-03 | Updated for TRR-2 (package B, netlist kst_top_nl_2026.08.31): all rows re-signed on revision B documents; package row updated for CHG-B-001/CHG-B-002; IP BOM and errata rows updated for ECO-B-004; STA hold and waiver rows updated for ECO-B-003 (W-017 withdrawn); CDC row updated for ECO-B-005 (W-CDC-022 withdrawn); functional coverage 91.1% with CW-PCIE-003 pending (row stays YELLOW) |
| C | 2026-09-24 | Updated for TRR-3 (package C, netlist kst_top_nl_2026.09.19): all rows re-signed 2026-09-22 to 2026-09-24 on revision C documents; STA rows on full 14-view MCMM incl. ECO-C-002; functional coverage 96.8% and CW-PCIE-003 withdrawn (row GREEN); bug DB row notes PCIE-1187 closed (ECO-C-003); governance row extended to CHK-GOV-02; 27 GREEN |
