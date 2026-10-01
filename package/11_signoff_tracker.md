# KESTREL Sign-off Tracker

| Field | Value |
|---|---|
| Doc ID | KST-TRK-061 |
| Title | Sign-off Tracker |
| Revision | A |
| Date | 2026-08-13 |
| Owner | Marcus Oyelaran (Program Manager) |
| Status | Released for TRR-1 |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Scope

This tracker records the sign-off status of tape-out package A (netlist kst_top_nl_2026.08.07) for TRR-1 on 2026-08-14. Each row is self-reported by the named owner against the ALD-QA-CHK-007 rev 7.2 rules listed in the row. Supporting evidence is in the referenced package documents.

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
| Spec | Architecture spec KST-ARCH-001 | CHK-SPEC-01, CHK-SPEC-04 | Priya Raghavan | GREEN | 2026-08-10 | Rev A released and frozen; Tj -40 C to +125 C covered by sign-off corners |
| Spec | Package / pinout / IO spec KST-PKG-002 | CHK-SPEC-01, CHK-SPEC-02, CHK-SPEC-03 | Rachel Lindqvist | GREEN | 2026-08-11 | Pad ring frozen 2026-08-07; 2,304-ball map released; 0 unassigned signals; 4 GPIO banks, 52 GPIO pins |
| IP | IP BOM KST-IPBOM-050 | CHK-IP-01, CHK-IP-02 | Beatriz Solano | GREEN | 2026-08-10 | 25 line items frozen, all production-qualified; netlist hash check 25/25 match |
| IP | Previous-generation errata review (ALX4100-ERR) | CHK-IP-03 | Beatriz Solano | GREEN | 2026-08-10 | E01..E14 reviewed with subsystem owners; 11 carry-forward items dispositioned |
| Verification | Verification plan KST-VPLAN-010 | CHK-VER-02, CHK-VER-07 | Tomasz Wierzbicki | GREEN | 2026-08-10 | Tier and escape-history classification reviewed with block owners |
| Verification | Code coverage | CHK-VER-01 | Tomasz Wierzbicki | GREEN | 2026-08-12 | All blocks meet line 98.0% / branch 95.0% / toggle 95.0% / FSM targets after approved exclusions |
| Verification | Functional coverage | CHK-VER-02, CHK-VER-05, CHK-VER-07, CHK-VER-08 | Tomasz Wierzbicki | YELLOW | - | PCIe L1.2 71.0%, closure plan to TRR-2; all other Tier-1/Tier-2 at target; CE-004 (PCIE1 fused off) approved 2026-07-21 |
| Verification | Nightly regression | CHK-VER-04 | Tomasz Wierzbicki | GREEN | 2026-08-12 | 99.7%; 3 consecutive nightlies at or above 99.5% |
| Verification | Bug database | CHK-VER-03 | Tomasz Wierzbicki | GREEN | 2026-08-12 | 0 open P1/P2; all P3 triaged with owner |
| Verification | Gate-level simulation (SDF) | CHK-VER-06 | Tomasz Wierzbicki | GREEN | 2026-08-12 | Boot, reset and low-power entry/exit tests pass at min and max SDF corners |
| STA | Setup, functional views | CHK-STA-01, CHK-STA-03, CHK-STA-07 | Mei-Lin Chou | GREEN | 2026-08-12 | 14/14 views; SI + POCV; 24 waivers logged |
| STA | Hold, all views | CHK-STA-02, CHK-STA-03 | Mei-Lin Chou | GREEN | 2026-08-12 | 14/14 views; 24 waivers logged |
| STA | Timing waivers KST-STA-021 | CHK-STA-05, CHK-STA-06 | Mei-Lin Chou | GREEN | 2026-08-12 | 24 waivers logged; test-mode false paths per KST-DFT-EXC |
| STA | DRV (max transition / max capacitance) | CHK-STA-04 | Jonah Pike | GREEN | 2026-08-12 | 0 unwaived; DRV waivers on tie-off / spare-cell nets only |
| CDC | CDC structural + formal | CHK-CDC-01, CHK-CDC-02, CHK-CDC-03, CHK-CDC-04, CHK-CDC-06 | Hiroshi Tanabe | GREEN | 2026-08-12 | 1,284 crossings; 1,241 clean; 43 waived; 0 unwaived |
| CDC | RDC | CHK-CDC-05 | Hiroshi Tanabe | GREEN | 2026-08-12 | 0 unwaived RDC violations |
| PI | Static IR drop | CHK-PI-01 | Grace Adeyemi | GREEN | 2026-08-11 | All rails at or below 2.5%; worst VDD_NPU 1.6% (12.0 mV) |
| PI | Dynamic IR drop | CHK-PI-02 | Grace Adeyemi | GREEN | 2026-08-11 | All rails within budget; VDD_NPU 7.4% vs 8.0%, VDD_CORE 5.2%, VDD_SRAM 4.1%, VDD_AON 1.2% |
| PI | Electromigration | CHK-PI-03 | Grace Adeyemi | GREEN | 2026-08-11 | 0 violations at Tj 110 C, 10-year lifetime |
| PV | DRC incl. density | CHK-PV-01 | Daniel Achterberg | GREEN | 2026-08-12 | Foundry N5-class sign-off deck; 0 violations |
| PV | LVS | CHK-PV-01 | Daniel Achterberg | GREEN | 2026-08-12 | Clean, top level and all hard macros |
| PV | ERC / antenna | CHK-PV-01 | Daniel Achterberg | GREEN | 2026-08-12 | 0 violations |
| PV | ESD / latch-up | CHK-PV-02 | Rachel Lindqvist | GREEN | 2026-08-12 | HBM 1 kV / CDM 250 V checks and latch-up rules clean on all pads incl. hard-macro pads (vendor ESD reports cross-checked with discharge-path analysis) |
| PD | Formal equivalence (RTL vs netlist) | PD flow (no checklist rule) | Daniel Achterberg | GREEN | 2026-08-09 | kst_top_nl_2026.08.07 equivalent to RTL tag incl. ECO-A-001..007 |
| DFT | ATPG | CHK-DFT-01 | Samir Haddad | GREEN | 2026-08-12 | Stuck-at 99.2%, transition 96.1% |
| DFT | MBIST | CHK-DFT-02 | Samir Haddad | GREEN | 2026-08-12 | 100% SRAM instances; repair on NPU and GBUF macros |
| Governance | Package revision alignment | CHK-SPEC-01 | Marcus Oyelaran | GREEN | 2026-08-13 | All 11 pre-TRR package documents at revision A; minutes KST-TRR-060 rev A issued after TRR-1 |

## 4. Open items

| Row | Item | Owner | Plan | Target |
|---|---|---|---|---|
| Functional coverage | cg_pcie0_l12_entry_exit closure | Tomasz Wierzbicki / Leo Brandt | Directed L1.2 sequences and constrained-random L1SS library | TRR-2 (2026-09-04) |

## 5. Referenced documents (package A)

| Doc ID | Title | Revision | Date |
|---|---|---|---|
| KST-ARCH-001 | Architecture Specification | A | 2026-08-10 |
| KST-PKG-002 | Package, Pinout and I/O Specification | A | 2026-08-11 |
| KST-VPLAN-010 | Verification Plan | A | 2026-08-10 |
| KST-COV-011 | Coverage Report | A | 2026-08-12 |
| KST-STA-020 | STA Sign-off Report | A | 2026-08-12 |
| KST-STA-021 | Timing Waiver Log | A | 2026-08-12 |
| KST-CDC-030 | CDC/RDC Report | A | 2026-08-12 |
| KST-PI-040 | Power Integrity Report | A | 2026-08-11 |
| KST-IPBOM-050 | IP BOM | A | 2026-08-10 |
| KST-ECO-062 | ECO & Change Log | A | 2026-08-13 |

## 6. Physical-verification and DFT run record

Tool reports are held in the sign-off database. This table is the evidence of record for CHK-PV-01, CHK-PV-02 (chip level) and CHK-DFT-01..02 (ALD-QA-CHK-007 section 3.4).

| Rule | Check | Run ID | Tool / deck | Input | Log | Run date | Result |
|---|---|---|---|---|---|---|---|
| CHK-PV-01 | DRC incl. density | pv_kst_0812_drc | Physical verification tool, foundry N5-class sign-off deck | kst_top_pnr_2026.08.07 (GDS, post-metal-fill) | signoff/pv/pv_kst_0812_drc/drc.sum | 2026-08-12 | 0 violations |
| CHK-PV-01 | LVS | pv_kst_0812_lvs | Physical verification tool, foundry N5-class LVS deck | kst_top_pnr_2026.08.07 vs kst_top_nl_2026.08.07, top level and all hard macros | signoff/pv/pv_kst_0812_lvs/lvs.rep | 2026-08-12 | Clean (0 unmatched nets or devices) |
| CHK-PV-01 | ERC / antenna | pv_kst_0812_erc_ant | Physical verification tool, foundry N5-class sign-off deck | kst_top_pnr_2026.08.07 | signoff/pv/pv_kst_0812_erc_ant/erc_ant.sum | 2026-08-12 | 0 violations |
| CHK-PV-02 | ESD network (HBM 1 kV, CDM 250 V) and latch-up, chip level | pv_kst_0812_esd_lu | Physical verification tool, foundry ESD/latch-up rule deck | kst_top_pnr_2026.08.07: pad ring, core and all hard-macro pads (PCIE5-PHY-N5 x2, PHY-LP5X-N5 x4, PLL/OTP/PVT analog pins) | signoff/pv/pv_kst_0812_esd_lu/esd_lu.sum | 2026-08-12 | 0 violations |
| CHK-DFT-01 | ATPG stuck-at and transition | atpg_kst_0811 | ATPG tool | kst_top_nl_2026.08.07, engineering pattern set v0.8 | signoff/dft/atpg_kst_0811/coverage.rpt | 2026-08-11 | Stuck-at 99.2%, transition 96.1% |
| CHK-DFT-02 | MBIST insertion and pattern simulation | mbist_kst_0811 | MBIST tool + logic simulator | kst_top_nl_2026.08.07 | signoff/dft/mbist_kst_0811/mbist.rpt | 2026-08-11 | 3,412/3,412 SRAM instances tested, 0 failures; repair enabled on NPU and GBUF macros |
