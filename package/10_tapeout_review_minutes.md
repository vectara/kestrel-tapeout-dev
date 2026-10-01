# KESTREL Tape-out Readiness Review Minutes (TRR-3)

| Field | Value |
|---|---|
| Doc ID | KST-TRR-060 |
| Title | Tape-out Readiness Review Minutes |
| Revision | C (supersedes B) |
| Date | 2026-09-25 |
| Owner | Marcus Oyelaran (Program Manager) |
| Status | Final - issued to TRR board |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Meeting details

| Item | Detail |
|---|---|
| Meeting | TRR-3 (final tape-out readiness review) |
| Date / time | 2026-09-25, 09:00-11:10 PT |
| Location | Aldercrest HQ, Building 2, room "Kingfisher" + video bridge |
| Chair | Priya Raghavan (Chief Architect) |
| Minutes | Marcus Oyelaran (Program Manager) |
| Package under review | Tape-out package C (documents dated 2026-09-21 to 2026-09-24) |
| Netlist / layout | kst_top_nl_2026.09.19 (ECO-C-001..ECO-C-003 incorporated, see KST-ECO-062 rev C) |
| Checklist | ALD-QA-CHK-007 rev 7.2 (released 2026-06-30) |
| Program milestone | GDSII handoff to foundry 2026-10-30 (full-mask production tape-out); A0 silicon expected 2027-02 |

## 2. Attendees

| Name | Role | TRR board | Attendance |
|---|---|---|---|
| Priya Raghavan | Chief Architect (chair) | Yes (chair) | Present |
| Marcus Oyelaran | Program Manager | Yes | Present (minutes) |
| Oren Feldman | Quality & Tape-out Gatekeeper | Yes | Present |
| Tomasz Wierzbicki | Verification Lead | Domain lead | Present |
| Mei-Lin Chou | STA Lead | Domain lead | Present |
| Daniel Achterberg | Physical Design Lead | Domain lead | Present |
| Hiroshi Tanabe | CDC/RDC Owner | Domain lead | Present |
| Grace Adeyemi | Power Integrity Lead | Domain lead | Present |
| Samir Haddad | DFT Lead | Domain lead | Present |
| Rachel Lindqvist | Package & I/O Lead | Domain lead | Present |
| Beatriz Solano | IP Manager | Domain lead | Present |
| Jonah Pike | STA Engineer | No | Present |
| Ayesha Qureshi | DFT Engineer | No | Present (item 10) |
| Leo Brandt | PCIe Subsystem Owner | No | Present |
| Anjali Deshmukh | Memory Subsystem Owner (LPDDR5X) | No | Present (remote) |
| Ines Carvalho | Security Enclave Owner | No | Present |
| Kofi Mensah | PMU / Always-on Domain Owner | No | Present |
| Viktor Halloran | NPU Cluster Owner | No | Present |

Quorum: 3 of 3 board members present (ALD-QA-CHK-007 section 3.2); 8 of 8 domain leads present.

## 3. Agenda

| # | Topic | Presenter | Start |
|---|---|---|---|
| 1 | Opening, review of TRR-2 actions, package scope | Priya Raghavan | 09:00 |
| 2 | Program status and schedule | Marcus Oyelaran | 09:10 |
| 3 | Architecture spec, package and pinout | Priya Raghavan, Rachel Lindqvist | 09:15 |
| 4 | IP BOM and previous-generation errata review | Beatriz Solano | 09:20 |
| 5 | Verification: coverage, regression, bug DB, GLS | Tomasz Wierzbicki, Leo Brandt | 09:25 |
| 6 | Static timing analysis | Mei-Lin Chou, Jonah Pike | 09:50 |
| 7 | CDC / RDC | Hiroshi Tanabe | 10:05 |
| 8 | Power integrity and EM | Grace Adeyemi | 10:10 |
| 9 | Physical verification | Daniel Achterberg | 10:15 |
| 10 | DFT | Samir Haddad, Ayesha Qureshi | 10:20 |
| 11 | Subsystem owner statements | Brandt, Deshmukh, Carvalho, Mensah, Halloran | 10:25 |
| 12 | Quality position | Oren Feldman | 10:40 |
| 13 | Decision, sign-off and action items | Priya Raghavan | 10:50 |

## 4. Review of previous actions (TRR-2)

| ID | Action | Owner | Status | Closure |
|---|---|---|---|---|
| AI-11 | Review CW-PCIE-003; readiness gate report on package B | Oren Feldman | Closed 2026-09-08 | Report and recommendation issued to chair; findings assigned under AI-15 |
| AI-12 | Decide on CW-PCIE-003 | Priya Raghavan | Closed 2026-09-08 | CW-PCIE-003 rejected (waiver not permitted under CHK-VER-07); closure of cg_pcie0_l12_entry_exit to the Tier-1 target required before GO; requester to withdraw the record once the target is met |
| AI-13 | Continue cg_pcie0_l12_entry_exit closure | Tomasz Wierzbicki, Leo Brandt | Closed 2026-09-22 | TB-C-001; 96.8% (120/124); PCIE-1187 found and fixed by ECO-C-003 |
| AI-14 | ECO window and netlist kst_top_nl_2026.09.19 | Daniel Achterberg | Closed 2026-09-19 | Netlist released with ECO-C-001..ECO-C-003 |
| AI-15 | Disposition package B readiness gate findings | All area owners | Closed 2026-09-12 | ECO-C-002 (security path re-balanced), verified by full 14-view MCMM run sta_kst_0911_c002 (2026-09-11); final re-sign-off on kst_top_nl_2026.09.19 under AI-14 |
| AI-16 | Schedule TRR-3; package C documents | Marcus Oyelaran | Closed 2026-09-24 | 11 package documents re-released at revision C (minutes issued after the meeting) |
| AI-17 | VDDIO_1V8_B rail routing to GPIO_B supply balls on card rev P2 | Rachel Lindqvist | Closed 2026-09-10 | Confirmed by board team |
| AI-18 | ATPG pattern set v1.0 on the final netlist | Samir Haddad | Closed 2026-09-23 | Delivered on kst_top_nl_2026.09.19 |

## 5. Program status (Marcus Oyelaran)

- Package C frozen 2026-09-24; the 11 pre-TRR package documents released at revision C (these minutes, KST-TRR-060 rev C, are issued after the meeting).
- Schedule: GDSII handoff 2026-10-30; mask-order slot confirmed for the week of 2026-11-02; A0 silicon expected 2027-02.
- No further ECO window is planned before GDSII; any change after this review requires chair approval and a full re-sign-off.
- SKUs: ALX-5100 (Tj 0 to +105 C) and ALX-5100I (Tj -40 to +105 C). PCIE1 is fused off in ALX-5100 (FUSE_PCIE1_DIS=1) and reserved for a future ALX-5100X.
- Reference card (CEM x16, 150 W, one 2x3 6-pin auxiliary power connector) rev P2 released for fabrication.

## 6. Per-area status as reported by owners

| Area | Reported by | Self-reported status | Summary as reported |
|---|---|---|---|
| Architecture spec | Priya Raghavan | GREEN | KST-ARCH-001 rev C released 2026-09-21 for revision alignment; no functional change. Operating range covered by sign-off corners (m40c to 125c). |
| Package & pinout | Rachel Lindqvist | GREEN | KST-PKG-002 rev C released 2026-09-21; no change since rev B (CHG-B-001, CHG-B-002 retained). 0 unassigned interface signals. |
| IP BOM | Beatriz Solano | GREEN | KST-IPBOM-050 rev C: one in-house version bump, l1ss_ctl v3.0 -> v3.0.1 (ECO-C-003); third-party IP unchanged since rev B (MC-LP5X and PHY-LP5X-N5 at v2.7.0); netlist hash check 25/25 on kst_top_nl_2026.09.19. |
| Errata carry-forward | Beatriz Solano | GREEN | 11 carry-forward items resolved; ALX4100-E03 design fix re-verified (l1ss_ctl v3.0.1 = v3.0 + ECO-C-003). |
| Verification | Tomasz Wierzbicki | GREEN | Regression 99.8%; code coverage met; PCIe L1.2 covergroup at 96.8% (Tier-1 target met); CW-PCIE-003 Withdrawn; PCIE-1187 closed; bug DB 0 open P1/P2; full min/max SDF GLS on kst_top_nl_2026.09.19 pass. |
| STA | Mei-Lin Chou | GREEN | Full 14-view MCMM on kst_top_nl_2026.09.19 (SI + POCV): setup and hold positive on all functional views; ECO-C-002 security path re-balanced; 23 active waivers, all complete. |
| CDC / RDC | Hiroshi Tanabe | GREEN | Re-run on kst_top_nl_2026.09.19: 1,286 crossings, 0 unwaived violations (1,244 clean, 42 waived). RDC: 0 unwaived. |
| Power integrity / EM | Grace Adeyemi | GREEN | Re-run on kst_top_nl_2026.09.19: all rails pass static and dynamic IR budgets. EM: 0 violations at Tj 110 C, 10-year lifetime. |
| Physical verification | Daniel Achterberg | GREEN | DRC (foundry N5-class sign-off deck), LVS, ERC, antenna and density clean on the final layout. ESD and latch-up clean. |
| DFT | Samir Haddad | GREEN | ATPG pattern set v1.0 on kst_top_nl_2026.09.19: stuck-at 99.2%, transition 96.1%; MBIST on 100% of SRAM instances, repair enabled on NPU and GBUF macros. |

## 7. Discussion

**7.1 Architecture, package and pinout.** No change since TRR-2. Priya and Rachel confirmed rev C is a revision-alignment release. The board team confirmed the VDDIO_1V8_B rail routing to the GPIO_B supply balls on card rev P2 (AI-17).

**7.2 IP BOM and errata.** Beatriz reported one in-house version bump since TRR-2 (l1ss_ctl v3.0 -> v3.0.1, ECO-C-003), third-party IP unchanged; hash check 25/25 on the final netlist. Anjali reported the LPDDR5X subsystem regression on v2.7.0 clean on kst_top_nl_2026.09.19 and presented the A0 cold-boot characterization plan for ALX-5100I (AI-24).

**7.3 Verification and PCIE-1187.** Tomasz presented KST-COV-011 rev C. Regression is 99.8% over three consecutive nightlies. Following the chair's decision not to grant CW-PCIE-003 (AI-12), TB-C-001 added the L1.2 closure tests. The new directed test l12_clkreq_tpoweron_gen5 exposed PCIE-1187 (P1): u_pcie0_wrap/u_l1ss_ctl released the PHY from P1.2 before refclk_valid when CLKREQ# re-asserted within 2 us of T_POWER_ON expiry at Gen5, the ALX4100-E03 scenario appearing at Gen5. The re-assert branch of the exit FSM had restarted T_POWER_ON without clearing tpoweron_done; ECO-C-003 (RTL) clears it on CLKREQ# re-assertion and re-qualifies every P1.2 exit with refclk_valid; the fix was re-verified with the directed and constrained-random L1SS suites and regression is clean. cg_pcie0_l12_entry_exit is at 96.8% (120/124 bins); the four remaining bins are not CLKREQ-related. Leo reported CW-PCIE-003 status Withdrawn on 2026-09-22 (target met). Bug DB: 0 open P1/P2 (PCIE-1187 opened 2026-09-10, closed 2026-09-17). Full min/max SDF GLS on kst_top_nl_2026.09.19 passes boot, reset, low-power entry/exit and PCIe L1.2 entry/exit tests.

Priya noted for the record that bins proposed for post-silicon coverage under CW-PCIE-003 contained a P1 bug; Oren will add this to the post-mortem lessons file (AI-25).

**7.4 STA and ECO-C-002.** Mei-Lin reported that the package B readiness gate review identified that the ECO-B-003 delay cells sat on the segment shared by the min and max paths of the security enclave key-load path, reducing setup margin at the slow corners. ECO-C-002 re-balanced the path: the two ECO-B-003 delay cells were removed and a single delay cell was placed on the ECC-bypass branch only (the hold-critical leg, with more than 1.5 ns setup margin). The full 14-view MCMM run on kst_top_nl_2026.09.19 is clean: setup and hold positive on all functional views, test-mode items covered by complete waivers in KST-STA-021 rev C. Mei-Lin confirmed that every post-ECO sign-off run is now on the full view set (CHK-STA-03, CHK-GOV-02). Jonah reported DRV clean.

**7.5 CDC / RDC.** Hiroshi reported the full CDC/RDC re-run on kst_top_nl_2026.09.19: 1,286 crossings, 1,244 clean, 42 waived, 0 unwaived. ECO-C-003 introduced no new crossings.

**7.6 Power integrity.** Grace reported all rails pass on kst_top_nl_2026.09.19; VDD_NPU dynamic IR unchanged at 7.4% (55.5 mV) against the 8.0% (60.0 mV) budget.

**7.7 Physical verification.** Daniel reported DRC, LVS, ERC, antenna and density clean on the final layout; spare and gate-array ECO filler retained at 1.5% density for post-tape-out metal-only ECOs.

**7.8 DFT.** Samir reported ATPG pattern set v1.0 delivered (stuck-at 99.2%, transition 96.1%) and MBIST on 100% of SRAM instances. Ayesha confirmed the NPU trace funnel scan-shift waiver (KST-DFT-EXC, TE-DFT-014) is unchanged.

**7.9 Subsystem owner statements.**

- Leo Brandt (PCIe): see 7.3; PCIE-1187 closed; A0 validation plan covers L1.2 CLKREQ# / T_POWER_ON scenarios at Gen1..Gen5 (AI-23).
- Anjali Deshmukh (LPDDR5X): see 7.2.
- Ines Carvalho (Security): key-load path timing clean on the full view set after ECO-C-002; secure-boot GLS with min and max SDF passes.
- Kofi Mensah (PMU/AON): no change since TRR-2; wake regression passes in ACTIVE and LP-IDLE on the final netlist.
- Viktor Halloran (NPU): no change since TRR-2; NPU regression passes.

**7.10 Quality position (Oren Feldman).** The readiness gate on package C shows all ALD-QA-CHK-007 rev 7.2 blocking rules passing and 0 open blocking findings (CHK-GOV-03). The sign-off tracker is 27/27 GREEN (CHK-GOV-01), and the final re-sign-off on kst_top_nl_2026.09.19 is dated after the last ECO (CHK-GOV-02). Quality recommends GO.

## 8. Decision

| Item | Record |
|---|---|
| Decision requested | GO for GDSII handoff on 2026-10-30. |
| Decision recorded | GO for GDSII handoff 2026-10-30, netlist kst_top_nl_2026.09.19 and package C. The three board members vote GO; the eight domain leads sign their areas. |
| Rationale | Tracker 27/27 GREEN; readiness gate 0 open blocking findings; full 14-view MCMM and all sign-offs re-run on kst_top_nl_2026.09.19. |
| Change control | Any change after TRR-3 requires chair approval and a full re-sign-off per CHK-GOV-02. |

### 8.1 Board vote and domain-lead sign-off

| Name | Role | Vote | Signed |
|---|---|---|---|
| Priya Raghavan | Chief Architect (chair) | GO | 2026-09-25 |
| Marcus Oyelaran | Program Manager | GO | 2026-09-25 |
| Oren Feldman | Quality & Tape-out Gatekeeper | GO | 2026-09-25 |
| Tomasz Wierzbicki | Verification Lead | Concur (area signed off) | 2026-09-25 |
| Mei-Lin Chou | STA Lead | Concur (area signed off) | 2026-09-25 |
| Daniel Achterberg | Physical Design Lead | Concur (area signed off) | 2026-09-25 |
| Hiroshi Tanabe | CDC/RDC Owner | Concur (area signed off) | 2026-09-25 |
| Grace Adeyemi | Power Integrity Lead | Concur (area signed off) | 2026-09-25 |
| Samir Haddad | DFT Lead | Concur (area signed off) | 2026-09-25 |
| Rachel Lindqvist | Package & I/O Lead | Concur (area signed off) | 2026-09-25 |
| Beatriz Solano | IP Manager | Concur (area signed off) | 2026-09-25 |

## 9. Action items

| ID | Action | Owner | Due | Status |
|---|---|---|---|---|
| AI-19 | Final GDSII stream-out, layer map and checksum; handoff to the foundry | Daniel Achterberg | 2026-10-30 | Open |
| AI-20 | Obtain foundry tape-out DRC acknowledgement and mask-order confirmation | Daniel Achterberg, Marcus Oyelaran | 2026-11-06 | Open |
| AI-21 | Release final substrate design and ball map to the package house | Rachel Lindqvist | 2026-10-09 | Open |
| AI-22 | Deliver the production test program and ATPG patterns to the ATE team | Samir Haddad | 2026-12-15 | Open |
| AI-23 | A0 post-silicon validation plan incl. L1.2 CLKREQ# / T_POWER_ON scenarios at Gen1..Gen5 | Leo Brandt, Tomasz Wierzbicki | 2026-11-20 | Open |
| AI-24 | ALX-5100I cold-boot (-40 C) LPDDR5X characterization plan for A0 | Anjali Deshmukh | 2026-11-20 | Open |
| AI-25 | Archive package C, the gate reports and TRR minutes; add the CW-PCIE-003 / PCIE-1187 lesson to the post-mortem candidate list | Oren Feldman | 2026-10-09 | Open |
| AI-26 | Schedule the A0 bring-up readiness review | Marcus Oyelaran | 2027-01-15 | Open |

## 10. References

- KST-TRK-061 Sign-off Tracker, rev C (2026-09-24)
- KST-ECO-062 ECO & Change Log, rev C (2026-09-24)
- KST-COV-011 Coverage Report, rev C; KST-STA-020 STA Sign-off Report, rev C; KST-CDC-030 CDC/RDC Report, rev C; KST-PI-040 Power Integrity Report, rev C
- ALD-QA-CHK-007 rev 7.2 Tape-out Readiness Checklist

Next meeting: A0 bring-up readiness review (date per AI-26).

## 11. Revision history

| Rev | Date | Meeting | Summary |
|---|---|---|---|
| A | 2026-08-14 | TRR-1 | Package A review; conditional GO proposed; decision deferred to TRR-2; actions AI-01..AI-10 |
| B | 2026-09-04 | TRR-2 | Package B review; TRR-1 actions AI-01..AI-10 closed (CHG-B-001/002, ECO-B-003/004/005, TB-B-001); L1.2 coverage 91.1% and CW-PCIE-003 requested; decision on CW-PCIE-003 taken offline by the chair; actions AI-11..AI-18 |
| C | 2026-09-25 | TRR-3 | Package C review; TRR-2 actions AI-11..AI-18 closed; ECO-C-002 (security path re-balanced), ECO-C-003 (PCIE-1187), TB-C-001; L1.2 coverage 96.8%, CW-PCIE-003 Withdrawn; GO for GDSII handoff 2026-10-30 voted by the board and signed by the domain leads; actions AI-19..AI-26 |
