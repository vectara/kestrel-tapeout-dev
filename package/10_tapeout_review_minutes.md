# KESTREL Tape-out Readiness Review Minutes (TRR-1)

| Field | Value |
|---|---|
| Doc ID | KST-TRR-060 |
| Title | Tape-out Readiness Review Minutes |
| Revision | A |
| Date | 2026-08-14 |
| Owner | Marcus Oyelaran (Program Manager) |
| Status | Final - issued to TRR board |
| Project | KESTREL (ALX-5100), PRJ-2025-017 |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Meeting details

| Item | Detail |
|---|---|
| Meeting | TRR-1 (first formal tape-out readiness review) |
| Date / time | 2026-08-14, 09:00-11:40 PT |
| Location | Aldercrest HQ, Building 2, room "Kingfisher" + video bridge |
| Chair | Priya Raghavan (Chief Architect) |
| Minutes | Marcus Oyelaran (Program Manager) |
| Package under review | Tape-out package A (documents dated 2026-08-10 to 2026-08-13) |
| Netlist / layout | kst_top_nl_2026.08.07 (ECO-A-001..ECO-A-007 incorporated, see KST-ECO-062 rev A) |
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
| 1 | Opening, TRR entry criteria, package scope | Priya Raghavan | 09:00 |
| 2 | Program status and schedule | Marcus Oyelaran | 09:05 |
| 3 | Architecture spec, package and pinout | Priya Raghavan, Rachel Lindqvist | 09:15 |
| 4 | IP BOM and previous-generation errata review | Beatriz Solano | 09:25 |
| 5 | Verification: coverage, regression, bug DB, GLS | Tomasz Wierzbicki | 09:35 |
| 6 | Static timing analysis | Mei-Lin Chou, Jonah Pike | 10:00 |
| 7 | CDC / RDC | Hiroshi Tanabe | 10:15 |
| 8 | Power integrity and EM | Grace Adeyemi | 10:25 |
| 9 | Physical verification | Daniel Achterberg | 10:35 |
| 10 | DFT | Samir Haddad, Ayesha Qureshi | 10:45 |
| 11 | Subsystem owner statements | Brandt, Deshmukh, Carvalho, Mensah, Halloran | 10:55 |
| 12 | Quality position | Oren Feldman | 11:15 |
| 13 | Decision and action items | Priya Raghavan | 11:25 |

## 4. Review of previous actions

None. TRR-1 is the first formal readiness review; actions from the pre-TRR design review (2026-07-10) were closed before package A was frozen.

## 5. Program status (Marcus Oyelaran)

- Package A frozen 2026-08-13; the 11 pre-TRR package documents released at revision A (these minutes, KST-TRR-060 rev A, are issued after the meeting).
- Schedule: TRR-2 2026-09-04, TRR-3 2026-09-25, GDSII handoff 2026-10-30. Mask-order slot with the foundry is held for the week of 2026-11-02.
- Post-TRR-1 ECO window: 2026-08-17 to 2026-08-30; next netlist drop kst_top_nl_2026.08.31.
- SKUs: ALX-5100 (Tj 0 to +105 C) and ALX-5100I (Tj -40 to +105 C). PCIE1 is fused off in ALX-5100 (FUSE_PCIE1_DIS=1) and reserved for a future ALX-5100X.
- Reference card (CEM x16, 150 W, one 2x3 6-pin auxiliary power connector) schematics frozen to the released ball map.

## 6. Per-area status as reported by owners

| Area | Reported by | Self-reported status | Summary as reported |
|---|---|---|---|
| Architecture spec | Priya Raghavan | GREEN | KST-ARCH-001 rev A released 2026-08-10 and frozen; no open architecture change requests. Operating range covered by sign-off corners (m40c to 125c). |
| Package & pinout | Rachel Lindqvist | GREEN | KST-PKG-002 rev A released 2026-08-11; pad ring frozen 2026-08-07. FCBGA 45.0 x 45.0 mm, 2,304 balls, 0.8 mm pitch; ball map released for substrate routing; 0 unassigned interface signals. |
| IP BOM | Beatriz Solano | GREEN | KST-IPBOM-050 rev A frozen; 25 line items, all production-qualified releases; netlist hash check 25/25. LPDDR5X: MC-LP5X 2.6.x silicon-proven on MERLIN. |
| Errata carry-forward | Beatriz Solano | GREEN | ALX4100-ERR E01..E14 reviewed with subsystem owners; 11 carry-forward items dispositioned. |
| Verification | Tomasz Wierzbicki | YELLOW | Regression 99.7%; code coverage met on all blocks; bug DB 0 open P1/P2. PCIe L1.2 covergroup at 71.0%, closure in progress, target TRR-2. All other Tier-1 and Tier-2 covergroups at target. |
| STA | Mei-Lin Chou | GREEN | All 14 views closed, remaining items covered by approved-process waivers. SI and POCV enabled; 24 waivers logged in KST-STA-021. |
| CDC / RDC | Hiroshi Tanabe | GREEN | 1,284 crossings, 0 unwaived violations (1,241 clean, 43 waived with CDC owner and block owner approval). RDC: 0 unwaived. |
| Power integrity / EM | Grace Adeyemi | GREEN | All rails pass static and dynamic IR budgets. EM: 0 violations at Tj 110 C, 10-year lifetime. |
| Physical verification | Daniel Achterberg | GREEN | DRC (foundry N5-class sign-off deck), LVS, ERC, antenna and density clean on the kst_top_nl_2026.08.07 layout. ESD and latch-up clean. |
| DFT | Samir Haddad | GREEN | ATPG stuck-at 99.2%, transition 96.1%; MBIST on 100% of SRAM instances, repair enabled on NPU and GBUF macros. |

## 7. Discussion

**7.1 Architecture, package and pinout.** Priya confirmed no open architecture change requests against rev A. Rachel reported the pad ring frozen 2026-08-07 and the 2,304-ball map released for substrate routing. Test engineering asked for the six NC balls in column 44 (AR44..AY44) to be labelled as reserved test pads for ATE socket continuity checks; Rachel will handle this as a documentation-only change in package B (AI-07).

**7.2 IP BOM and errata.** Beatriz reported the BOM frozen with no early-access or beta releases. The LPDDR5X controller and PHY (vendor code MIPV) stay on the 2.6.x line; MC-LP5X 2.6.x is silicon-proven on MERLIN. Anjali confirmed LPDDR5X-8533 training sequences pass in RTL simulation with the vendor PHY models and that DFI timing is closed at mc_clk 1066.7 MHz. The MERLIN errata review covered E01..E14; 11 items are marked carry-forward and each has a disposition in the BOM or the vplan.

**7.3 Verification.** Tomasz presented the coverage summary (KST-COV-011 rev A). Regression is 99.7% over three consecutive nightlies. Code coverage meets CHK-VER-01 on every block after approved exclusions. PCIe L1.2 covergroup cg_pcie0_l12_entry_exit is at 71.0% (88/124 bins); closure in progress, target TRR-2. Leo Brandt and the verification team are writing directed L1.2 sequences and a constrained-random L1SS sequence library (AI-01, AI-02). Escape-history covergroups for NPU DMA ring wrap (98.4%), I2C clock stretch (100.0%) and NPU sparse decompressor (97.9%) are at target. Coverage exclusion CE-004 (PCIE1 fused off, cg_pcie1_* at 0.0%, isolation covergroup at 100.0%) was approved by Tomasz and Priya on 2026-07-21. Bug DB: 0 open P1/P2; all P3 triaged with owners. SDF-annotated GLS (min and max corners) passes boot, reset and low-power entry/exit tests.

**7.4 STA.** Mei-Lin reported all 14 views (9 func, 2 scan_shift, 2 scan_capture, 1 mbist) run on kst_top_nl_2026.08.07 with SI and POCV per CHK-STA-07; all 14 views closed, remaining items covered by approved-process waivers (24 logged in KST-STA-021). At 0.675 V the -40 C corner is setup-limiting because of temperature inversion, as expected for this process. Jonah reported DRV clean: 0 unwaived max-transition / max-capacitance violations, DRV waivers on spare and tie-off nets only.

**7.5 CDC / RDC.** Hiroshi reported 1,284 crossings: 1,241 clean, 43 waived, 0 unwaived. Every waiver carries the CDC owner and block owner approvals (CHK-CDC-06). RDC analysis shows 0 unwaived violations.

**7.6 Power integrity.** Grace reported all rails pass. The closest rail is VDD_NPU dynamic IR at 7.4% (55.5 mV) against the 8.0% (60.0 mV) budget, worst region u_npu_c2/u_tile3 under vector vec_resnet50_l3_burst. Viktor accepted the margin; no action.

**7.7 Physical verification.** Daniel reported DRC, LVS, ERC, antenna and density clean. Spare and gate-array ECO filler is retained at 1.5% density for any post-tape-out metal-only ECO.

**7.8 DFT.** Samir reported stuck-at 99.2% and transition 96.1%, MBIST on 100% of SRAM instances. Ayesha summarized the scan-shift false paths on the NPU trace funnel: waived per KST-DFT-EXC (TE-DFT-014), approved by Mei-Lin and Samir on 2026-07-30.

**7.9 Subsystem owner statements.**

- Leo Brandt (PCIe): PCIE0 Gen5 x16 link training, equalization and compliance tests pass; L1.1/L1.2 functional tests pass with the redesigned l1ss_ctl v3.0. Coverage closure with Tomasz as above.
- Anjali Deshmukh (LPDDR5X): 4 x 64-bit subsystem integrated; see 7.2.
- Ines Carvalho (Security): secure-boot ROM flow, key ladder and OTP read pass in RTL and GLS; secure-boot time budget (150 ms) met at sec_clk 500 MHz.
- Kofi Mensah (PMU/AON): power-state FSM (ACTIVE, LP-IDLE, SLEEP, OFF) state and transition coverage 100%.
- Viktor Halloran (NPU): 16 tiles closed at npu_clk 1.2 GHz, 314.6 TOPS INT8 dense.

**7.10 Quality position (Oren Feldman).** Under CHK-GOV-01 a YELLOW tracker row counts as not signed off, and CHK-GOV-03 has no "conditional GO" outcome. Quality will issue the ALD-QA-CHK-007 rev 7.2 readiness gate report on package A (all rules, cross-document) on 2026-08-17 (AI-03). Owners are asked to disposition any findings before the ECO window closes.

## 8. Decision

| Item | Record |
|---|---|
| Decision requested | Marcus Oyelaran proposed a conditional GO pending L1.2 coverage, to protect the mask-order slot. |
| Decision recorded | GO/NO-GO decision deferred to TRR-2 (2026-09-04); outcome recorded by the chair: not GO for package A as submitted. |
| Rationale | Verification row is YELLOW (L1.2 closure in progress); Quality readiness gate report on package A due 2026-08-17. |
| Conditions for TRR-2 | Tracker fully GREEN or dispositioned; readiness gate findings closed; package B revision-aligned (CHK-SPEC-01). |

## 9. Action items

| ID | Action | Owner | Due | Status |
|---|---|---|---|---|
| AI-01 | Present bin-level closure plan for cg_pcie0_l12_entry_exit to reach the Tier-1 target by TRR-2 | Tomasz Wierzbicki | 2026-08-21 | Open |
| AI-02 | Deliver directed L1.2 entry/exit sequences and a constrained-random L1SS sequence library | Leo Brandt | 2026-08-28 | Open |
| AI-03 | Issue the ALD-QA-CHK-007 rev 7.2 readiness gate report on package A to all owners | Oren Feldman | 2026-08-17 | Open |
| AI-04 | Disposition every readiness gate finding; raise ECO/CHG requests through the PD ECO board | All area owners | 2026-08-28 | Open |
| AI-05 | Run ECO window 2026-08-17 to 2026-08-30 and release netlist kst_top_nl_2026.08.31 | Daniel Achterberg | 2026-08-31 | Open |
| AI-06 | Re-release all package documents at revision B, revision-aligned | All document owners | 2026-09-03 | Open |
| AI-07 | Re-label the six NC balls in column 44 (AR44..AY44) as reserved ATE test pads (documentation only) | Rachel Lindqvist | 2026-08-21 | Open |
| AI-08 | Confirm mask-order slot and GDSII handoff date with the foundry | Marcus Oyelaran | 2026-08-21 | Open |
| AI-09 | Deliver ATPG pattern set v0.9 to the test program team | Samir Haddad | 2026-08-28 | Open |
| AI-10 | Schedule TRR-2 (2026-09-04) and circulate the package B index | Marcus Oyelaran | 2026-08-28 | Open |

## 10. References

- KST-TRK-061 Sign-off Tracker, rev A (2026-08-13)
- KST-ECO-062 ECO & Change Log, rev A (2026-08-13)
- KST-COV-011 Coverage Report, rev A; KST-STA-020 STA Sign-off Report, rev A; KST-CDC-030 CDC/RDC Report, rev A; KST-PI-040 Power Integrity Report, rev A
- ALD-QA-CHK-007 rev 7.2 Tape-out Readiness Checklist

Next meeting: TRR-2, 2026-09-04, 09:00 PT.
