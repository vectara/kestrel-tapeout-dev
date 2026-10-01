# Tape-out Readiness Checklist

| Field | Value |
|---|---|
| Doc ID | ALD-QA-CHK-007 |
| Title | Tape-out Readiness Checklist |
| Revision | 7.2 |
| Date | 2026-06-30 |
| Owner | Oren Feldman (Quality & Tape-out Gatekeeper) |
| Status | Released - mandatory for all production tape-outs from 2026-07-01 |
| Supersedes | Revision 7.1 (2025-12-01) |
| Project | KESTREL (ALX-5100), PRJ-2025-017 (reference copy; company-wide document) |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Purpose

This checklist defines the rules a chip program must meet before its GDSII database is released to the foundry. It is the only basis for the gate decision taken at a Tape-out Readiness Review (TRR). Every rule has an ID, an objective threshold and a blocking flag. Rules that were added after a silicon respin record the post-mortem that produced them; the post-mortems are summarized in ALD-QA-PM-SUMMARY.

## 2. Scope

- All Aldercrest production tape-outs: full-mask tape-outs (new products and base-layer respins) and metal-only ECO tape-outs.
- Shuttle / MPW test chips: CHK-PV-01, CHK-PV-02, CHK-STA-01..03 and CHK-IP-02 only.
- Third-party hard macros are covered by the IP rules (CHK-IP-01..03) and by the chip-level checks; CHK-PV-02 explicitly includes hard-macro pads.
- Program document IDs quoted in rule text (KST-...) refer to the program currently in the gate cycle, PRJ-2025-017 KESTREL. Other programs substitute their equivalent documents.

## 3. Gate procedure

### 3.1 Review schedule

| Review | Typical timing (T = GDSII handoff) | Package | Purpose |
|---|---|---|---|
| TRR-1 | Netlist freeze + 1 week (about T-11 weeks) | A | First formal review of the complete package; findings list issued |
| TRR-2 | After the first ECO window (about T-8 weeks) | B | Closure of TRR-1 findings; review of every ECO made since package A |
| TRR-3 | Final (about T-5 weeks) | C | Final gate on the tape-out netlist; last point at which GO can be given |

The board chair may schedule additional reviews. Any netlist or layout change after a GO decision re-opens the affected rules (CHK-GOV-02) and requires a delta review before handoff.

### 3.2 Review board

| Board role | Function at the TRR |
|---|---|
| Chief Architect | Chair; takes the gate decision |
| Program Manager | Owns schedule and cost; presents package status |
| Quality & Tape-out Gatekeeper | Owns this checklist; runs the rule-by-rule pre-check and records findings |

Domain leads (verification, STA, physical design, CDC, power integrity, DFT, package and I/O, IP) present their evidence and attend for their areas. Quorum is all three board members or their named delegates.

### 3.3 Steps

1. **Package freeze.** All standard documents are released at the package revision (CHK-SPEC-01) no later than one business day before the TRR.
2. **Quality pre-check.** The gatekeeper evaluates every rule in Section 5 against the evidence in the package: report tables, logs and signed records. Status summaries in the sign-off tracker or in presentations are not evidence (except the run-record table in the sign-off tracker, KST-TRK-061 section 6, which is the evidence of record for the rules listed against it in Section 3.4).
3. **Domain presentations.** Each lead presents results, open items and waivers for their area.
4. **Findings.** Each failing rule is recorded as a finding with rule ID, evidence reference, owner and, for blocking rules, the respin exposure class (Section 4.2).
5. **Decision.** The chair records the outcome per Section 4.1. Minutes are issued within two business days.

### 3.4 Standard package documents

| # | Document | Primary evidence for |
|---|---|---|
| 01 | Architecture specification | CHK-SPEC-01..04 |
| 02 | Package, pinout and I/O specification | CHK-SPEC-02, CHK-SPEC-03, CHK-PV-02 |
| 03 | Verification plan (tiers, Escape-history classification) | CHK-VER-02, CHK-VER-05, CHK-VER-07 |
| 04 | Coverage report (code, functional, exclusions, waivers) | CHK-VER-01..08 |
| 05 | STA sign-off report | CHK-STA-01..04, CHK-STA-07 |
| 06 | Timing waiver log | CHK-STA-05, CHK-STA-06 |
| 07 | CDC/RDC report | CHK-CDC-01..06 |
| 08 | Power integrity report | CHK-PI-01..03 |
| 09 | IP bill of materials | CHK-IP-01..03, CHK-SPEC-01 |
| 10 | Tape-out review minutes | Record of decision and actions |
| 11 | Sign-off tracker | CHK-GOV-01; run record (section 6) for CHK-PV-01, CHK-PV-02 (chip level), CHK-DFT-01, CHK-DFT-02 |
| 12 | ECO change log | CHK-GOV-02 |

Physical-verification and DFT tool reports are held in the sign-off database. The evidence of record in the package is the run-record table in KST-TRK-061 section 6 (run ID, log file, netlist or layout, date, result). A tracker status cell without a run record is not evidence.

Reference documents that are not revisioned with the package: this checklist, the previous-generation errata sheet (for KESTREL: ALX4100-ERR), the respin post-mortem summary (ALD-QA-PM-SUMMARY) and the vendor release notes for every third-party IP in the BOM (held in the IP vault; each is cited by document ID in the IP BOM errata cross-check).

## 4. Gate outcome

### 4.1 Outcome definitions

| Outcome | Condition | Consequence |
|---|---|---|
| GO | No blocking rule fails (CHK-GOV-03). Every non-blocking finding has an owner and a due date. | The program may proceed to GDSII handoff on the reviewed netlist. |
| NO-GO | One or more blocking rules fail, or the evidence for a blocking rule is missing or out of date. | The package returns to the team. The next TRR reviews closure of every finding. |

A "conditional GO" is not a gate outcome. A finding against a blocking rule cannot be deferred past tape-out by an action item, a pending waiver or a tracker comment. A waiver counts only when it is complete and approved before the TRR (CHK-STA-05, CHK-CDC-06, CHK-VER-08).

### 4.2 Respin exposure classes

Blocking findings are ranked by the respin they would cause if they reached silicon. Reference values for an N5-class full-mask program (program finance, FY2026):

| Class | Applies when | Direct cost | Schedule |
|---|---|---|---|
| Full base-layer respin | The fix changes front-end layers (device type, implant, gate oxide, hard-macro base layers) or exceeds spare-cell capacity | $15-20M: new mask set of about 80 masks including EUV layers, 25-wafer 300 mm hot lot, re-characterization and requalification | 4-6 months |
| Metal-only ECO | The fix can be made in via and metal layers only, using the spare / gate-array ECO cells; FEOL and MOL masks are reused | $1-3M: re-cut of the via and metal masks from the lowest layer the ECO touches up to about M8, plus metal-hold wafers. Spare-cell rewiring from V1/M2 up (about 16 masks) is typically $1.5-2.5M; gate-array personalization from V0/M0 up also re-cuts the tightest-pitch EUV / multi-patterned layers (about 24 masks) and sits at the top of the range (about $3M) | 2-3 months |

Schedule slip is valued separately at about $2.0M per month. Exposures of individual findings are not additive: one base-layer respin also absorbs any metal fixes.

## 5. Rules

Blocking = Yes means that a failure of the rule makes the gate outcome NO-GO (CHK-GOV-03). Origin = Baseline means the rule predates the post-mortem process or was part of the rev 7.0 restructure.

| Rule ID | Area | Rule | Threshold | Blocking | Origin |
|---|---|---|---|---|---|
| CHK-GOV-01 | Governance | Every sign-off tracker row must be GREEN with a named owner and sign-off date. 'Conditional', 'pending waiver' or 'YELLOW' rows count as NOT signed off. | 100% rows GREEN | Yes | Baseline |
| CHK-GOV-02 | Governance | After ANY netlist/layout ECO, all affected sign-off checks must be re-run on the FULL view set (STA full MCMM per CHK-STA-03; DRC/LVS; CDC if logic changed; GLS for affected blocks). Results must be dated after the ECO. | re-run dated after last ECO | Yes | Baseline |
| CHK-GOV-03 | Governance | Gate outcome is GO only if no Blocking rule fails. Any open Blocking finding => NO-GO. | 0 open blocking findings | Yes | Baseline |
| CHK-SPEC-01 | Spec | Architecture spec (KST-ARCH-001), package/pinout/IO spec (KST-PKG-002) and IP BOM (KST-IPBOM-050) released and revision-aligned to the tape-out package revision. | same package revision | Yes | Baseline |
| CHK-SPEC-02 | Spec | Every interface signal in the architecture spec is assigned to a ball in the ball map, and every signal ball traces to an architecture-spec signal (NC, reserved and power/ground balls excluded). | 0 unassigned | Yes | Baseline |
| CHK-SPEC-03 | Spec | For every I/O bank, the VDDIO voltage and I/O cell type in the pad-ring/package spec must match the interface voltage in the architecture spec, and the I/O cell's maximum rated VDDIO must be >= the bank's operating VDDIO. | exact match per bank | Yes | PM-2022-01 (ALX-2200 OSPREY) |
| CHK-SPEC-04 | Spec | Operating conditions in the architecture spec (Tj range, supply tolerance) must be covered by the sign-off PVT corners. | Tj -40 C..+125 C covered | Yes | Baseline |
| CHK-VER-01 | Verification | Code coverage per block after approved exclusions. | line >= 98.0%, branch >= 95.0%, toggle >= 95.0%, FSM state = 100%, FSM transition >= 95.0% | Yes | Baseline |
| CHK-VER-02 | Verification | Functional coverage per covergroup, by vplan tier. | Tier-1 >= 95.0%; Tier-2 >= 90.0%; Tier-3 >= 80.0% (Tier-3 non-blocking, tracked) | Yes | Baseline |
| CHK-VER-03 | Verification | Bug database. | 0 open P1/P2 bugs; all P3 triaged with owner | Yes | Baseline |
| CHK-VER-04 | Verification | Final nightly regression pass rate. | >= 99.5% on 3 consecutive nightly runs | Yes | Baseline |
| CHK-VER-05 | Verification | Coverage exclusions are permitted only for logic that is unreachable in the shipped SKU (fused off or tied off), provided the isolation/fuse/clamp logic itself is verified to >= 95%, and the exclusion is approved by the Verification Lead AND the Chief Architect with a dated record. | approved exclusion record | Yes | Baseline |
| CHK-VER-06 | Verification | SDF-annotated gate-level simulation at min and max corners passes for boot, reset and low-power entry/exit tests. | all GLS tests pass | Yes | Baseline |
| CHK-VER-07 | Verification | Covergroups for features with silicon-escape history (a previous-generation erratum or respin post-mortem) whose fix lies in logic the program verifies in simulation (in-house or redesigned RTL) are classified 'Escape-history' in the vplan. They must reach the Tier-1 target (>= 95.0%) and coverage waivers are NOT permitted for them. Escapes fixed inside third-party IP are resolved under CHK-IP-03; their integration covergroups carry the Tier-1 target. | >= 95.0%, no waivers | Yes | PM-2024-02 (ALX-4100 MERLIN) |
| CHK-VER-08 | Verification | Coverage waivers for non-escape covergroups require a written risk assessment and approval by the Verification Lead and Chief Architect before TRR. | approved before TRR | Yes | Baseline |
| CHK-STA-01 | STA | Setup slack >= 0 ps on every functional-mode sign-off view. | setup WNS >= 0.000 ns (functional views) | Yes | Baseline |
| CHK-STA-02 | STA | Hold slack >= 0 ps on every sign-off view. Hold violations in any functional-mode view may NEVER be waived; they must be fixed. | hold WNS >= 0.000 ns; no functional hold waivers | Yes | Baseline |
| CHK-STA-03 | STA | Sign-off STA must be run on the full program sign-off view set (KESTREL: 14-view MCMM, KST-STA-020) on the final netlist, with SI and POCV enabled. Incremental or partial-view runs are not acceptable for sign-off. | 14/14 views on final netlist | Yes | Baseline |
| CHK-STA-04 | STA | Max transition / max capacitance DRVs. | 0 unwaived; waivers allowed only on tie-off/spare-cell nets | Yes | Baseline |
| CHK-STA-05 | STA | Every timing waiver must have: (a) technical justification, (b) constraint or ECO reference, (c) approver = STA Lead plus block owner (or DFT Lead for test modes), (d) approval date. A waiver missing any field is INVALID and the violation counts as open. | 4/4 fields | Yes | Baseline |
| CHK-STA-06 | STA | Test-mode-only (scan_shift/scan_capture/mbist) paths may be waived as false paths when the path is not sensitizable in that mode, the justification references the DFT exception list (KST-DFT-EXC), and the waiver is approved by the STA Lead and DFT Lead. Team policy: DFT false paths are waived rather than masked with wildcard constraints, so they stay visible in reports. | approved DFT exception | No | Baseline |
| CHK-STA-07 | STA | Clock uncertainty per the Aldercrest N5 timing methodology; OCV/POCV derates per the foundry N5-class sign-off guide. | setup uncertainty 50 ps (functional) / 200 ps (test); hold uncertainty 20 ps; POCV + SI enabled | Yes | Baseline |
| CHK-CDC-01 | CDC | Structural + formal CDC clean. | 100% crossings classified; 0 unwaived violations | Yes | Baseline |
| CHK-CDC-02 | CDC | Single-bit level signals use a qualified synchronizer cell. | 2-FF for destination <= 800 MHz; 3-FF for destination > 800 MHz; MTBF >= 1,000 years per synchronizer at worst corner | Yes | Baseline |
| CHK-CDC-03 | CDC | Multi-bit crossings whose value changes during operation use gray code, req/ack handshake, or async FIFO; quasi-static multi-bit buses are permitted only under an approved CHK-CDC-04 waiver; no multi-bit bus through independent synchronizers. | 0 multi-bit crossings without gray/handshake/FIFO or an approved CHK-CDC-04 waiver | Yes | Baseline |
| CHK-CDC-04 | CDC | Quasi-static waivers are permitted only for LEVEL signals that (a) change only while the destination domain is held in reset or its clock is stopped, or are written once during boot before first use, (b) are stable >= 3 destination clock cycles before being sampled, and (c) have the stability guarantee documented (SVA/formal proof or SW programming rule). Pulses and event strobes may NEVER be waived as quasi-static; they require a pulse synchronizer or req/ack handshake. | 0 pulse crossings without pulse sync/handshake | Yes | PM-2023-03 (ALX-3100 HARRIER) |
| CHK-CDC-05 | CDC | Reset-domain crossings analyzed; asynchronous resets asserted asynchronously and de-asserted synchronously. | 0 unwaived RDC violations | Yes | Baseline |
| CHK-CDC-06 | CDC | CDC waivers approved by CDC Owner and the block owner. | 2 approvals | Yes | Baseline |
| CHK-PI-01 | Power integrity | Static IR drop per rail. | <= 2.5% of nominal | Yes | Baseline |
| CHK-PI-02 | Power integrity | Dynamic IR drop (worst of vectorless and vector-based): worst per-cycle effective drop, VDD droop plus VSS bounce averaged over one period of the local clock, i.e. the effective voltage seen by timing. | VDD_NPU and VDD_CORE <= 8.0%; VDD_SRAM <= 6.0%; VDD_AON <= 5.0% of nominal | Yes | Baseline |
| CHK-PI-03 | Power integrity | Electromigration on signal and power/ground nets. | 0 violations at Tj = 110 C, 10-year lifetime (87,600 h) | Yes | Baseline |
| CHK-IP-01 | IP | All third-party IP at a production-qualified release (not EA/beta) per vendor release notes, or with signed risk acceptance by the Chief Architect. | production-qualified | Yes | Baseline |
| CHK-IP-02 | IP | IP BOM versions match the versions integrated in the netlist/GDS (hash check). | 100% match | Yes | Baseline |
| CHK-IP-03 | IP | Every previous-generation erratum marked 'Carry-forward: Yes' must be resolved in the new chip: the IP version in the BOM must be >= the erratum's fixed-in version (as confirmed by vendor release notes), or an in-house design fix must be documented and verified. | 0 unresolved carry-forward errata | Yes | ALX-4100 errata carry-forward review (2025, ALX4100-ERR rev 3.1) and PM-2024-02 |
| CHK-PV-01 | Physical verification | DRC (foundry N5-class sign-off deck), LVS, ERC, antenna, density. | 0 violations (foundry-approved waivers only) | Yes | Baseline |
| CHK-PV-02 | Physical verification | ESD (HBM 1 kV, CDM 250 V) and latch-up checks. | 0 violations | Yes | PM-2021-02 (ALX-1500 WREN) |
| CHK-DFT-01 | DFT | ATPG test coverage. | stuck-at >= 99.0%; transition-delay >= 95.0% | Yes | Baseline |
| CHK-DFT-02 | DFT | MBIST on all SRAM instances with repair where available. | 100% SRAM instances | Yes | Baseline |

## 6. Rationale for selected rules

### 6.1 CHK-GOV-02 (full re-sign-off after any ECO)

Late ECOs carry the highest risk in a program: they are made under schedule pressure and are usually checked on the narrowest possible scope. A fix that repairs one check can break another. For example, delay cells inserted to fix a fast-corner hold violation also add delay at the slow corners, often two to three times as much, and can create a setup violation on the same endpoint. The re-run must therefore cover every sign-off view and every affected check, and its results must be dated after the last ECO. An incremental run on the views where the original violation was reported is not evidence of closure.

### 6.2 CHK-SPEC-03 (I/O bank voltage cross-check)

Origin: PM-2022-01 (ALX-2200 OSPREY). The GPIO bank serving a 1.8 V SPI boot flash was built with 1.2 V-only I/O cells because the pad-ring specification was inherited from an earlier template and never cross-checked against the architecture specification. DRC and LVS cannot detect this class of error because the cells are legal library cells, and functional simulation with ideal pad models cannot detect it either. The check is a document cross-check. For each bank, compare the interface voltage in the architecture specification with the VDDIO and cell type in the package/pad-ring specification and the IP BOM, and confirm that the cell's maximum rated VDDIO covers the bank voltage. Replacing a 1.2 V-only cell with a 1.8 V-capable cell changes the I/O transistor type (implant and gate layers, FEOL masks), so a miss costs a full base-layer respin.

### 6.3 CHK-VER-07 (Escape-history covergroups)

Origin: PM-2024-02 (ALX-4100 MERLIN). At MERLIN tape-out the PCIe L1.2 entry/exit covergroup stood at 78% and a coverage waiver was granted under schedule pressure. The uncovered cross bins included CLKREQ# re-assertion during T_POWER_ON, which is the scenario behind erratum ALX4100-E03 and the full base-layer respin that followed ($11.6M, 22 weeks). A feature that has already escaped to silicon is, by definition, one where the unexercised corner cases are known to matter. The verification plan classifies such covergroups as Escape-history when the fix lies in logic the program verifies itself (in-house or redesigned RTL). They carry the Tier-1 target and cannot be waived at any percentage. Escapes fixed inside third-party IP are closed under CHK-IP-03 against the vendor's fixed-issue list, and the program's integration covergroups for them are held to the Tier-1 target. Between 2024-06 and checklist revision 7.1 the rule was enforced as interim quality directive QD-2024-05.

### 6.4 CHK-STA-02 and CHK-STA-05 (hold violations and waiver completeness)

A setup violation can, in the worst case, be recovered on silicon by lowering the clock frequency. A hold violation cannot: it does not depend on the clock period, so parts that fail hold at the fast corner fail at every frequency. A functional-mode hold violation must therefore be fixed in the netlist before tape-out, and there is no waiver path for it.

CHK-STA-05 addresses incomplete waivers. A waiver record created to clear a report, with justification, reference or approver left as TBD, is not a technical decision. The gate treats it as an open violation, whatever status the record shows.

### 6.5 CHK-CDC-04 (quasi-static waivers)

Origin: PM-2023-03 (ALX-3100 HARRIER). A single-cycle wake pulse from the always-on domain was waived as "quasi-static" because wake events are rare. Quasi-static describes a level that holds its value for a long time, not an event that happens infrequently. A pulse carries its information in its edges. If it is narrower than the destination clock period it can be missed altogether; otherwise it is sampled asynchronously. HARRIER lost about 1 in 4,000 wake events in the field and about one in three with the idle clock divided by 64. The reviewer must establish the shape of the signal (level or pulse) from the source logic or the architecture specification, not from the signal name in the CDC report, and must check the destination clock period in every power state, including divided idle clocks.

### 6.6 CHK-IP-03 (carry-forward errata)

Origin: ALX-4100 errata carry-forward review (2025, ALX4100-ERR rev 3.1) and PM-2024-02. The rule closes the gap between a known erratum on the previous chip and the IP selected for the next one. Resolution is confirmed against the vendor release notes' fixed-issue list for the exact version in the BOM. A higher version number is not sufficient on its own: a maintenance release on an older release line contains only the fixes listed for it and does not inherit fixes made on a newer line unless the vendor states a back-port. A workaround that restricted the previous product's operating range, such as a datasheet temperature limit, carries over only if the new product's specification accepts the same restriction. Otherwise the erratum must be fixed in the IP.

## 7. Waiver and exclusion records

| Record type | ID format | Required content | Approvers | Rules |
|---|---|---|---|---|
| Timing waiver | W-nnn (program waiver log) | Technical justification, constraint or ECO reference, approvers, approval date | STA Lead + block owner (DFT Lead for test modes) | CHK-STA-02, CHK-STA-05, CHK-STA-06 |
| CDC/RDC waiver | W-CDC-nnn | Crossing ID, signal class (level or pulse), stability guarantee and its proof, approvers, date | CDC Owner + block owner | CHK-CDC-04, CHK-CDC-06 |
| Coverage exclusion | CE-nnn | Unreachable-logic evidence (fuse, tie-off, clamp), isolation coverage >= 95%, approvers, date | Verification Lead + Chief Architect | CHK-VER-05 |
| Coverage waiver | CW-<block>-nnn | Written risk assessment, approvers, date; not permitted for Escape-history covergroups | Verification Lead + Chief Architect | CHK-VER-07, CHK-VER-08 |
| DRC waiver | Foundry waiver number | Foundry approval | Foundry + PD Lead | CHK-PV-01 |

A record in status "requested", "pending" or "TBD" is not a waiver. A withdrawn waiver is kept in the log with the reason for withdrawal.

## 8. Approval

| Role | Name | Decision | Date |
|---|---|---|---|
| Owner, Quality & Tape-out Gatekeeper | Oren Feldman | Released | 2026-06-30 |
| Chief Architect, TRR board chair | Priya Raghavan | Approved | 2026-06-29 |
| Program Manager | Marcus Oyelaran | Acknowledged | 2026-06-30 |
| STA Lead (review of CHK-STA-06 change) | Mei-Lin Chou | Reviewed | 2026-06-24 |
| DFT Lead (review of CHK-STA-06 change) | Samir Haddad | Reviewed | 2026-06-24 |

## 9. Change history

| Rev | Date | Author | Change |
|---|---|---|---|
| 4.0 | 2021-11 | O. Feldman | Added chip-level ESD (HBM 1 kV, CDM 250 V) and latch-up check on all pads including hard-macro pads, after PM-2021-02 (now CHK-PV-02). |
| 5.0 | 2022-06 | O. Feldman | Added per-bank I/O voltage and cell-type cross-check between architecture and pad-ring specifications, after PM-2022-01 (now CHK-SPEC-03). |
| 6.0 | 2023-09 | O. Feldman | Added the quasi-static waiver conditions and the pulse prohibition, after PM-2023-03 (now CHK-CDC-04). |
| 7.0 | 2025-01 | O. Feldman | Restructured into area-prefixed rule IDs (CHK-GOV, SPEC, VER, STA, CDC, PI, IP, PV, DFT). Added governance rules CHK-GOV-01..03 and gate outcome definitions. |
| 7.1 | 2025-12 | O. Feldman | Added CHK-VER-07 (Escape-history covergroups, no waivers; formalizes interim directive QD-2024-05) and CHK-IP-03 (carry-forward errata), after PM-2024-02 and the ALX-4100 errata review. |
| 7.2 | 2026-06 | O. Feldman | Clarified CHK-STA-06: test-mode false paths are waived with a KST-DFT-EXC reference and STA Lead + DFT Lead approval rather than masked with wildcard constraints, so that they stay visible in reports. Program document IDs in rule text updated to PRJ-2025-017. |
