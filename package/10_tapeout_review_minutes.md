# KESTREL Tape-out Readiness Review Minutes (TRR-2)

| Field | Value |
|---|---|
| Doc ID | KST-TRR-060 |
| Title | Tape-out Readiness Review Minutes |
| Revision | B (supersedes A) |
| Date | 2026-09-04 |
| Owner | Marcus Oyelaran (Program Manager) |
| Status | Final - issued to TRR board |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Meeting details

| Item | Detail |
|---|---|
| Meeting | TRR-2 (second formal tape-out readiness review) |
| Date / time | 2026-09-04, 09:00-11:25 PT |
| Location | Aldercrest HQ, Building 2, room "Kingfisher" + video bridge |
| Chair | Priya Raghavan (Chief Architect) |
| Minutes | Marcus Oyelaran (Program Manager) |
| Package under review | Tape-out package B (documents dated 2026-08-31 to 2026-09-03) |
| Netlist / layout | kst_top_nl_2026.08.31 (CHG-B-002, ECO-B-001..ECO-B-006 incorporated, see KST-ECO-062 rev B) |
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
| Grace Adeyemi | Power Integrity Lead | Domain lead | Present (remote) |
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
| 1 | Opening, review of TRR-1 actions, package scope | Priya Raghavan | 09:00 |
| 2 | Program status and schedule | Marcus Oyelaran | 09:10 |
| 3 | Architecture spec, package and pinout | Priya Raghavan, Rachel Lindqvist | 09:15 |
| 4 | IP BOM and previous-generation errata review | Beatriz Solano | 09:25 |
| 5 | Verification: coverage, regression, bug DB, GLS | Tomasz Wierzbicki | 09:35 |
| 6 | Static timing analysis | Mei-Lin Chou, Jonah Pike | 10:00 |
| 7 | CDC / RDC | Hiroshi Tanabe | 10:10 |
| 8 | Power integrity and EM | Grace Adeyemi | 10:20 |
| 9 | Physical verification | Daniel Achterberg | 10:25 |
| 10 | DFT | Samir Haddad, Ayesha Qureshi | 10:35 |
| 11 | Subsystem owner statements | Brandt, Deshmukh, Carvalho, Mensah, Halloran | 10:40 |
| 12 | Quality position | Oren Feldman | 11:00 |
| 13 | Decision and action items | Priya Raghavan | 11:10 |

## 4. Review of previous actions (TRR-1)

| ID | Action | Owner | Status | Closure |
|---|---|---|---|---|
| AI-01 | Bin-level closure plan for cg_pcie0_l12_entry_exit | Tomasz Wierzbicki | Closed 2026-08-21 | Plan presented; tests delivered under TB-B-001 |
| AI-02 | Directed L1.2 sequences and constrained-random L1SS library | Leo Brandt | Closed 2026-08-21 | TB-B-001: 14 directed sequences + constrained-random L1SS sequence library |
| AI-03 | Readiness gate report on package A | Oren Feldman | Closed 2026-08-17 | Report issued to all owners; findings assigned under AI-04 |
| AI-04 | Disposition readiness gate findings | All area owners | Closed 2026-08-28 | TRR-1 action items closed: CHG-B-002 (GPIO_B cells), ECO-B-003 (security-path hold, W-017 withdrawn), ECO-B-004 (LPDDR5X IP to v2.7.0 per errata review), ECO-B-005 (PMU wake synchronizer); L1.2 coverage tracked under AI-01 |
| AI-05 | ECO window and netlist kst_top_nl_2026.08.31 | Daniel Achterberg | Closed 2026-08-31 | Netlist released with CHG-B-002 and ECO-B-001..ECO-B-006 |
| AI-06 | Package documents at revision B | All document owners | Closed 2026-09-03 | 11 package documents re-released at revision B (minutes issued after the meeting) |
| AI-07 | Re-label the six NC balls in column 44 (AR44..AY44) | Rachel Lindqvist | Closed 2026-08-17 | CHG-B-001 (TP_0..TP_5, documentation only) |
| AI-08 | Confirm mask-order slot and GDSII date | Marcus Oyelaran | Closed 2026-08-20 | Foundry confirmed slot for week of 2026-11-02; GDSII handoff 2026-10-30 |
| AI-09 | ATPG pattern set v0.9 | Samir Haddad | Closed 2026-08-27 | Delivered to test program team |
| AI-10 | Schedule TRR-2 and circulate package B index | Marcus Oyelaran | Closed 2026-08-28 | Done |

## 5. Program status (Marcus Oyelaran)

- Package B frozen 2026-09-03; the 11 pre-TRR package documents released at revision B (these minutes, KST-TRR-060 rev B, are issued after the meeting).
- Schedule: TRR-3 2026-09-25, GDSII handoff 2026-10-30. Mask-order slot with the foundry confirmed for the week of 2026-11-02.
- Post-TRR-2 ECO window: 2026-09-07 to 2026-09-18; next netlist drop kst_top_nl_2026.09.19.
- SKUs: ALX-5100 (Tj 0 to +105 C) and ALX-5100I (Tj -40 to +105 C). PCIE1 is fused off in ALX-5100 (FUSE_PCIE1_DIS=1) and reserved for a future ALX-5100X.
- Reference card (CEM x16, 150 W, one 2x3 6-pin auxiliary power connector): rail plan updated for CHG-B-002 (separate 1.8 V rail VDDIO_1V8_B) on card rev P2.

## 6. Per-area status as reported by owners

| Area | Reported by | Self-reported status | Summary as reported |
|---|---|---|---|
| Architecture spec | Priya Raghavan | GREEN | KST-ARCH-001 rev B released 2026-08-31 for revision alignment; no functional change. Operating range covered by sign-off corners (m40c to 125c). |
| Package & pinout | Rachel Lindqvist | GREEN | KST-PKG-002 rev B released 2026-09-01 with CHG-B-001 (TP_0..TP_5) and CHG-B-002 (GPIO_B pad-ring cells to IO_GPIO_1V8, VDDIO_B 1.8 V per KST-ARCH-001). Ball map otherwise unchanged; 0 unassigned interface signals. |
| IP BOM | Beatriz Solano | GREEN | KST-IPBOM-050 rev B: MC-LP5X and PHY-LP5X-N5 at v2.7.0 (ECO-B-004); 25 line items, all production-qualified; netlist hash check 25/25. |
| Errata carry-forward | Beatriz Solano | GREEN | ALX4100-ERR re-reviewed after TRR-1; 10 carry-forward items resolved by IP version, ALX4100-E07 closed by v2.7.0 (LPX-1182); E03 in-house l1ss_ctl v3.0, verification under functional coverage. |
| Verification | Tomasz Wierzbicki | YELLOW | Regression 99.6%; code coverage met on all blocks; bug DB 0 open P1/P2. PCIe L1.2 covergroup at 91.1% after TB-B-001; coverage waiver CW-PCIE-003 requested. All other Tier-1 and Tier-2 covergroups at target. |
| STA | Mei-Lin Chou | GREEN | Post-ECO incremental hold timing clean. Hold closed by ECO-B-003; W-017 withdrawn; 23 active waivers in KST-STA-021 rev B. |
| CDC / RDC | Hiroshi Tanabe | GREEN | 1,286 crossings, 0 unwaived violations (1,244 clean, 42 waived). CDC-0147 now synchronized by ECO-B-005; W-CDC-022 withdrawn. RDC: 0 unwaived. |
| Power integrity / EM | Grace Adeyemi | GREEN | Re-run on kst_top_nl_2026.08.31: all rails pass static and dynamic IR budgets. EM: 0 violations at Tj 110 C, 10-year lifetime. |
| Physical verification | Daniel Achterberg | GREEN | DRC (foundry N5-class sign-off deck), LVS, ERC, antenna and density clean on the kst_top_nl_2026.08.31 layout incl. the pad-ring change and the PHY-LP5X-N5 v2.7.0 macro. ESD and latch-up clean. |
| DFT | Samir Haddad | GREEN | ATPG re-run on kst_top_nl_2026.08.31: stuck-at 99.2%, transition 96.1%; MBIST on 100% of SRAM instances, repair enabled on NPU and GBUF macros. |

## 7. Discussion

**7.1 Architecture, package and pinout.** Priya confirmed no functional change to the architecture; rev B is re-released for revision alignment (CHK-SPEC-01). Rachel reported CHG-B-001 and CHG-B-002 in KST-PKG-002 rev B: GPIO_B now uses IO_GPIO_1V8 cells with VDDIO_B at 1.8 V, matching KST-ARCH-001; 16 pad-ring cells swapped, ball map unchanged; pad-ring DRC/LVS and ESD re-checked clean. The board team moved VDDIO_B to its own 1.8 V rail (VDDIO_1V8_B) on card rev P2.

**7.2 IP BOM and errata.** Beatriz reported ECO-B-004: MC-LP5X and PHY-LP5X-N5 moved together from the 2.6.x line to v2.7.0 per the errata review (ALX4100-E07, vendor ticket LPX-1182); the re-released PHY hard macro GDS is integrated and the netlist hash check is 25/25. Anjali confirmed the vendor integration test suite and the LPDDR5X subsystem regression pass on v2.7.0, and reviewed the vendor's v2.7.0 characterization (PHY-LP5X-N5 training validated from Tj -40 C to +125 C on the vendor N5-class test chip); cold-boot characterization of ALX-5100I is planned for A0.

**7.3 Verification.** Tomasz presented KST-COV-011 rev B. Regression is 99.6% over three consecutive nightlies. TB-B-001 added 14 directed L1.2 sequences and a constrained-random L1SS sequence library; cg_pcie0_l12_entry_exit rose from 71.0% to 91.1% (113/124 bins). Leo Brandt requested coverage waiver CW-PCIE-003 for cg_pcie0_l12_entry_exit at 91.1%: the remaining bins are Gen5 corner cases to be covered in post-silicon validation. Escape-history covergroups for NPU DMA ring wrap (98.4%), I2C clock stretch (100.0%) and NPU sparse decompressor (97.9%) remain at target; CE-004 (PCIE1 fused off) unchanged. Bug DB: 0 open P1/P2; all P3 triaged. GLS for the ECO-B-003 partition (SEC) re-run with min-corner SDF: pass; all other GLS tests, including the PMUIF LP-IDLE and SLEEP wake tests, pass at both corners.

**7.4 STA.** Mei-Lin reported post-ECO incremental hold timing clean. ECO-B-003 closed the hold item on the security enclave key-load path and W-017 is withdrawn; KST-STA-021 rev B lists 24 waivers, 23 active. SI and POCV enabled per CHK-STA-07. Jonah reported DRV clean on kst_top_nl_2026.08.31: 0 unwaived max-transition / max-capacitance violations.

**7.5 CDC / RDC.** Hiroshi reported 1,286 crossings: 1,244 clean, 42 waived, 0 unwaived. ECO-B-005 added the pulse synchronizer u_core/u_pmu_if/u_wake_psync on CDC-0147 and W-CDC-022 is withdrawn; the two new crossings inside the synchronizer are classified clean. RDC analysis shows 0 unwaived violations.

**7.6 Power integrity.** Grace reported all rails pass on kst_top_nl_2026.08.31. VDD_NPU dynamic IR is unchanged at 7.4% (55.5 mV) against the 8.0% (60.0 mV) budget; the package B ECOs change VDD_CORE and VDD_NPU dynamic IR by less than 0.1 mV.

**7.7 Physical verification.** Daniel reported DRC, LVS, ERC, antenna and density clean. Spare and gate-array ECO filler is retained at 1.5% density.

**7.8 DFT.** Samir reported ATPG re-run results unchanged (stuck-at 99.2%, transition 96.1%) and MBIST on 100% of SRAM instances. Ayesha confirmed the NPU trace funnel scan-shift waiver (KST-DFT-EXC, TE-DFT-014) is unchanged.

**7.9 Subsystem owner statements.**

- Leo Brandt (PCIe): see 7.3. Requests CW-PCIE-003 so that the L1.2 item does not hold the GDSII date.
- Anjali Deshmukh (LPDDR5X): see 7.2.
- Ines Carvalho (Security): key-load path hold fixed by ECO-B-003; secure-boot GLS with min-corner SDF passes.
- Kofi Mensah (PMU/AON): ECO-B-005 pulse synchronizer (toggle + 3-FF + edge detect) on pmu_wake_req; wake regression passes in ACTIVE and LP-IDLE with the /64 divider enabled.
- Viktor Halloran (NPU): ECO-B-002 (DMA completion interrupt coalescing) integrated; NPU regression passes.

**7.10 Quality position (Oren Feldman).** Quality will review CW-PCIE-003 against ALD-QA-CHK-007 rev 7.2 and send a recommendation to the chair by 2026-09-08, together with the readiness gate report on package B (AI-11).

## 8. Decision

| Item | Record |
|---|---|
| Decision requested | Marcus Oyelaran proposed to proceed to tape-out with coverage waiver CW-PCIE-003, keeping GDSII handoff on 2026-10-30. |
| Decision recorded | No GO/NO-GO vote at TRR-2; outcome recorded by the chair: not GO, package B returns to the team. The Chief Architect will decide on CW-PCIE-003 offline after the Quality recommendation; decision to be recorded by 2026-09-09. |
| Rationale | Verification row YELLOW pending CW-PCIE-003; all other areas reported GREEN. |
| Conditions for TRR-3 | Tracker fully GREEN; readiness gate findings on package B closed; package C revision-aligned (CHK-SPEC-01). |

## 9. Action items

| ID | Action | Owner | Due | Status |
|---|---|---|---|---|
| AI-11 | Review CW-PCIE-003 against the checklist and issue the readiness gate report on package B | Oren Feldman | 2026-09-08 | Open |
| AI-12 | Decide on CW-PCIE-003 and record the decision | Priya Raghavan | 2026-09-09 | Open |
| AI-13 | Continue cg_pcie0_l12_entry_exit closure regardless of the waiver outcome | Tomasz Wierzbicki, Leo Brandt | 2026-09-18 | Open |
| AI-14 | Run ECO window 2026-09-07 to 2026-09-18 and release netlist kst_top_nl_2026.09.19 | Daniel Achterberg | 2026-09-19 | Open |
| AI-15 | Disposition every package B readiness gate finding | All area owners | 2026-09-12 | Open |
| AI-16 | Schedule TRR-3 (2026-09-25); package C documents due 2026-09-24 | Marcus Oyelaran | 2026-09-11 | Open |
| AI-17 | Board only (no chip or package impact; chip-side CHG-B-002 complete and closed): card rev P2 layout review of VDDIO_1V8_B routing to the GPIO_B supply balls | Rachel Lindqvist | 2026-09-11 | Open |
| AI-18 | Deliver ATPG pattern set v1.0 on the final netlist | Samir Haddad | 2026-09-23 | Open |

## 10. References

- KST-TRK-061 Sign-off Tracker, rev B (2026-09-03)
- KST-ECO-062 ECO & Change Log, rev B (2026-09-03)
- KST-COV-011 Coverage Report, rev B; KST-STA-020 STA Sign-off Report, rev B; KST-CDC-030 CDC/RDC Report, rev B; KST-PI-040 Power Integrity Report, rev B
- ALD-QA-CHK-007 rev 7.2 Tape-out Readiness Checklist

Next meeting: TRR-3, 2026-09-25, 09:00 PT.

## 11. Revision history

| Rev | Date | Meeting | Summary |
|---|---|---|---|
| A | 2026-08-14 | TRR-1 | Package A review; conditional GO proposed; decision deferred to TRR-2; actions AI-01..AI-10 |
| B | 2026-09-04 | TRR-2 | Package B review; TRR-1 actions AI-01..AI-10 closed (CHG-B-001/002, ECO-B-003/004/005, TB-B-001); L1.2 coverage 91.1% and CW-PCIE-003 requested; decision on CW-PCIE-003 taken offline by the chair; actions AI-11..AI-18 |
