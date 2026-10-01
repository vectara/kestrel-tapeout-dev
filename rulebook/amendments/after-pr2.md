# Proposed rulebook amendments after tape-out PR #2

Proposed by the retrospective agent `rsp_kst_retro` after the KESTREL package was released to the factory (merge `bdab94e`). It read every gate report of the PR's review rounds plus the rulebook, the respin post-mortems and the errata. **Nothing here is in force until a person approves this PR.**

## What happened in the review loop

The gate moved from NO-GO at revision A with five blocking findings, to NO-GO at revision B with two blocking findings after four closures and one fix-induced timing/GLS regression, to GO at revision C after the remaining PCIe and SEC issues closed. The loop closed the GPIO_B I/O-bank voltage mismatch, PCIE0 Escape-history verification gap, SEC hold/setup/GLS path, AON wake-pulse CDC, and LPDDR5X cold-training carry-forward erratum. The multi-revision review caught what a single revision review would have missed: the SEC hold fix creating a setup and stale-GLS failure, and PCIe closure work finding real bug PCIE-1187 before tape-out.

## Lessons

- A status cell or summary row is not evidence; the gate must join the summary back to the detailed table that carries the measured result. The SEC timing rows showed both tracker-level and report-summary contradictions that would have hidden real negative slack.
- Escape-history closure must exercise the named failure mechanism, not just improve the percentage. Refusing the PCIE0 waiver forced Gen5 CLKREQ#/T_POWER_ON testing, found PCIE-1187 with the same failure signature as ALX4100-E03, and fixed it before tape-out.
- A min-corner timing fix is also a max-corner timing change. ECO-B-003 fixed hold but moved the same SEC endpoint into setup failure and made prior max-SDF GLS stale.
- Carry-forward errata are resolved only by the fixed issue on the exact installed release line and configuration. A production maintenance release and predecessor silicon experience did not resolve LPX-1182 for an industrial cold-boot SKU.
- For CDC waivers, the shape of the signal must come from architecture or source behavior, not from the waiver label. A rare event pulse is still a pulse and can be missed when the destination clock is divided in low power.
- Look-alikes should be accepted when their evidence satisfies the rule: PCIE1 fused-off exclusions, NC/test pads, closed historical waivers and near-threshold but passing coverage/timing/IR rows were not findings. The gate’s value comes from separating these from real blockers by objective evidence.

## Proposed amendments to ALD-QA-CHK-007

### AM-1: new rule `CHK-GOV-04` (Governance)

| Rule ID | Area | Requirement | Threshold | Blocking | Origin |
|---|---|---|---|---|---|
| CHK-GOV-04 | Governance | Summary, status and disposition fields in package documents must agree with the evidence-of-record tables they summarize. A summary row, tracker cell, waiver status, errata disposition or owner statement that contradicts the detailed evidence is not accepted as closure; the detailed evidence governs and the contradiction is a blocking finding until corrected. | 0 contradictions between summaries/status fields and evidence of record | Yes | KST TRR loop review (2026) |

**Why:** Origin: KST TRR loop review (2026). KESTREL package A and B contained summaries that said GREEN, MET, approved quasi-static or N/A while the evidence tables showed negative slack, a pulse crossing, or an unresolved carry-forward erratum. CHK-GOV-01 catches tracker status rows, but the same masking pattern also appeared inside an STA report summary, a CDC waiver classification and an IP BOM errata disposition. The check is a consistency audit: for each claimed closure/status/disposition, compare the claim to the evidence-of-record rows and fail the gate when they disagree.

**Guard against false alarms:** The rule must still accept summaries that are backed by matching detailed rows, withdrawn historical waivers kept for traceability, and tracker section 6 run records where the checklist names the tracker run-record table as the evidence of record.

**Change-history row:** `7.3 | 2026-10 | O. Feldman | Proposed CHK-GOV-04: summary/status/disposition fields must agree with evidence-of-record tables, after the KST TRR loop found GREEN/MET/N/A/quasi-static claims contradicted by detailed evidence.`

### AM-2: tighten rule `CHK-VER-07` (Verification)

| Rule ID | Area | Requirement | Threshold | Blocking | Origin |
|---|---|---|---|---|---|
| CHK-VER-07 | Verification | Covergroups for features with silicon-escape history (a previous-generation erratum or respin post-mortem) whose fix lies in logic the program verifies in simulation (in-house or redesigned RTL) are classified 'Escape-history' in the vplan. They must reach the Tier-1 target (>= 95.0%), coverage waivers are NOT permitted, and every scenario bin or formal property named by the erratum/post-mortem as part of the failure mechanism must be hit or proven on the final fix. | >= 95.0%, no waivers, all named failure-mechanism bins hit or properties proven | Yes | PM-2024-02 (ALX-4100 MERLIN); tightened after KST TRR loop review (2026) |

**Why:** Origin: PM-2024-02, tightened after the KST TRR loop. Revision B improved PCIE0 L1.2 coverage to 91.1% but still left the named Gen5 CLKREQ# re-assertion during T_POWER_ON bin at 0 hits, and the requested waiver called the remaining bins corner cases. Closure of that exact gap found PCIE-1187 with the same failure signature as ALX4100-E03. The check is to require both the Escape-history percentage and explicit closure of the bins/properties that encode the known failure mechanism.

**Guard against false alarms:** The rule must still accept unreachable shipped-SKU exclusions such as PCIE1 under approved CE-004, and it must still accept covergroups above 95% with non-failure-mechanism bins unhit when no waiver or exclusion is used.

**Change-history row:** `7.3 | 2026-10 | O. Feldman | Proposed tightening of CHK-VER-07: Escape-history closure must hit/prove every erratum/post-mortem named failure-mechanism bin, after KST PCIE0 closure found PCIE-1187 in a remaining Gen5 CLKREQ#/T_POWER_ON bin.`

### AM-3: clarify rule `CHK-VER-06` (Verification)

| Rule ID | Area | Requirement | Threshold | Blocking | Origin |
|---|---|---|---|---|---|
| CHK-VER-06 | Verification | SDF-annotated gate-level simulation at min and max corners passes for boot, reset and low-power entry/exit tests on the final netlist after the last netlist/layout ECO affecting the tested block or path. A carried-forward GLS result from an earlier netlist, corner or SDF is not evidence for an affected test. | all GLS tests pass at min and max SDF on the final netlist after affected ECOs | Yes | Baseline; clarified after KST TRR loop review (2026) |

**Why:** Origin: Baseline, clarified after the KST TRR loop. ECO-B-003 changed the SEC key-loader path and the package carried forward the max-SDF gls_secure_boot_auth result from package A while rerunning only min SDF. CHK-GOV-02 caught the stale date, but CHK-VER-06 should itself state that min and max GLS evidence is tied to the final netlist and affected SDF. The check is to compare GLS run netlist/SDF dates against the last ECO touching the tested block or path.

**Guard against false alarms:** The rule must still accept documentation-only changes with no netlist/layout/SDF impact and tests whose block/path is demonstrably unaffected by the ECO-impact table.

**Change-history row:** `7.3 | 2026-10 | O. Feldman | Proposed clarification of CHK-VER-06: affected GLS tests must pass at min and max SDF on the final netlist after the last ECO; carried-forward GLS is not evidence, after KST SEC ECO-B-003.`

### AM-4: clarify rule `CHK-IP-03` (IP)

| Rule ID | Area | Requirement | Threshold | Blocking | Origin |
|---|---|---|---|---|---|
| CHK-IP-03 | IP | Every previous-generation erratum marked 'Carry-forward: Yes' must be resolved in the new chip: the IP version in the BOM must be the fixed-in version or later on the release line that contains the fix, as confirmed by vendor release notes for the exact installed controller/PHY or macro pair, or an in-house design fix must be documented and verified. 'N/A', predecessor silicon-proven lineage, a maintenance release without the fixed issue, or an operating-range workaround not allowed by the new architecture is not a resolution. | 0 unresolved carry-forward errata | Yes | ALX-4100 errata carry-forward review (2025, ALX4100-ERR rev 3.1) and PM-2024-02; clarified after KST TRR loop review (2026) |

**Why:** Origin: ALX-4100 errata carry-forward review and PM-2024-02, clarified after the KST TRR loop. KESTREL package A marked ALX4100-E07 as N/A because the 2.6.x lineage was silicon-proven, but the release notes said LPX-1182 was not fixed in v2.6.1 and was fixed only in the matched v2.7.0 controller/PHY pair. The check is to audit each carry-forward row against the exact fixed-issue list, release line and required pairing, and against the new product operating range.

**Guard against false alarms:** The rule must still accept non-carried-forward errata with documented reasons, vendor fixes present in the exact installed release, in-house fixes verified under CHK-VER-07, and early-access releases that are reviewed but not integrated.

**Change-history row:** `7.3 | 2026-10 | O. Feldman | Proposed clarification of CHK-IP-03: predecessor lineage, N/A dispositions and unfixed maintenance branches do not close carry-forward errata; exact fixed issue and required IP pairing must be shown, after KST ALX4100-E07.`

---
<sub>🤖 Opened by the tape-out CI bot. The AI proposes; the checklist owner decides.</sub>