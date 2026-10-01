# Silicon Respin Post-mortems

| Field | Value |
|---|---|
| Doc ID | ALD-QA-PM-SUMMARY |
| Title | Silicon Respin Post-mortems |
| Revision | 4 |
| Date | 2025-12-05 |
| Owner | Oren Feldman (Quality) |
| Status | Released |
| Project | KESTREL (ALX-5100), PRJ-2025-017 (reference copy; company-wide document) |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. Purpose

This document summarizes every Aldercrest silicon respin since 2021: what failed, why the failure escaped the tape-out review, what it cost, and which rule was added to the Tape-out Readiness Checklist (ALD-QA-CHK-007) as a result. Program teams read it before TRR-1. The gatekeeper uses it to judge the severity of findings that match a known failure pattern.

Steppings are numbered sequentially (A0, A1, ...) for base-layer and metal-only respins alike, and the respin type is recorded in the summary table; WREN (2021) predates this convention and used B0 for its base-layer respin. Costs are direct costs (masks, wafers, requalification, board and debug effort). Schedule slip is reported separately and is measured from the planned production release.

## 2. Summary

| PM ID | Codename | Chip / node | Respin type | Failure | Direct cost | Slip | Checklist rule added |
|---|---|---|---|---|---|---|---|
| PM-2021-02 | WREN | ALX-1500, N16-class | Partial base-layer respin (about 45 of 60 masks) | CDM ESD failure on SerDes RX pads; hard-macro pads excluded from the chip-level ESD check | $2.9M | 17 weeks | CHK-PV-02 |
| PM-2022-01 | OSPREY | ALX-2200, N12-class | Full base-layer respin | GPIO bank for a 1.8 V SPI boot flash built with 1.2 V-only I/O cells; pad-ring spec not cross-checked against the architecture spec | $4.9M | 19 weeks | CHK-SPEC-03 |
| PM-2023-03 | HARRIER | ALX-3100, N7-class | Metal-only ECO (spare flops) | Single-cycle AON wake pulse into the core domain without a synchronizer, waived as quasi-static; resume failure about 1 in 4,000 wakes in the field, about 1 in 3 at /64 idle | $1.7M | 11 weeks | CHK-CDC-04 |
| PM-2024-02 | MERLIN | ALX-4100, N7-class | Full base-layer respin (A0 -> A1) | PCIe link-down on L1.2 exit when CLKREQ# is re-asserted during T_POWER_ON (ALX4100-E03); L1.2 entry/exit covergroup at 78% at tape-out under a coverage waiver | $11.6M (masks $9.8M) | 22 weeks | CHK-VER-07; later CHK-IP-03 |

Total direct cost 2021-2025: $21.1M. Total slip: 69 weeks.

## 3. PM-2021-02: ALX-1500 WREN (N16-class) - CDM ESD failure on SerDes RX pads

### 3.1 Timeline

| Date | Event |
|---|---|
| 2020-10-16 | A0 tape-out (TRR passed; ESD check reported clean) |
| 2021-01-11 | A0 first silicon |
| 2021-02-22 | Qualification: CDM failures at 250 V on the SerDes RX inputs |
| 2021-03-12 | Root cause confirmed by failure analysis |
| 2021-04-09 | B0 tape-out (base-layer respin) |
| 2021-06-25 | B0 passes qualification |

### 3.2 Symptom

12 of 15 qualification units failed CDM at 250 V (all passed at 125 V). The failing pins were the SerDes RX differential inputs. After stress the RX input leakage exceeded 10 uA, and failure analysis found gate-oxide rupture in the RX input pair.

### 3.3 Root cause

The SerDes hard-macro RX pads relied on a primary diode clamp only. The secondary clamp and series resistor needed to protect the thin-oxide input gate during a CDM discharge were missing.

### 3.4 Why it escaped

The chip-level ESD check covered library I/O pads only. The hard macro was treated as a black box with a vendor ESD rating, and the rating assumed a package-level discharge path that the WREN package did not provide.

### 3.5 Cost and schedule

$2.9M: partial mask set $2.2M (about 45 of 60 masks: implant, poly, contact and the metal stack for the SerDes ESD clamp; the remaining front-end masks were reused), wafers $0.2M, ESD requalification $0.3M, sample-delay commitments $0.2M. 17 weeks.

### 3.6 Corrective actions

- Chip-level ESD and latch-up checks run on every pad, including hard-macro pads, with discharge-path resistance analysis.
- Hard-macro ESD ratings accepted only with the vendor's test conditions stated.
- Checklist rule added: CHK-PV-02 (ESD HBM 1 kV, CDM 250 V and latch-up; 0 violations).

## 4. PM-2022-01: ALX-2200 OSPREY (N12-class) - 1.2 V-only I/O cells on a 1.8 V flash bank

### 4.1 Timeline

| Date | Event |
|---|---|
| 2021-11-19 | A0 tape-out |
| 2022-02-14 | A0 first silicon |
| 2022-02-16 | No boot from SPI flash on any unit; JTAG-loaded bring-up works |
| 2022-03-04 | Root cause confirmed |
| 2022-04-22 | A1 tape-out (full base-layer respin) |
| 2022-07-29 | A1 production release |

### 4.2 Symptom

No unit booted from the SPI NOR boot flash. With the flash powered, the flash supply current was 35-40 mA higher than expected and the bank's 1.2 V VDDIO rail was back-powered to about 1.35 V through the pad ESD diodes (the rail LDO cannot sink current).

### 4.3 Root cause

The architecture specification had moved the boot flash to a 1.8 V part during development. The pad-ring specification was inherited from an ALX-1500 template in which the bank was 1.2 V, and it was never updated. The bank was built with 1.2 V-only GPIO cells (maximum VDDIO 1.32 V). The chip's output high level of about 1.2 V was below the flash's VIH(min) of 1.26 V (0.7 x 1.8 V). The flash drove 1.8 V into pads rated for 1.32 V maximum VDDIO and about 1.5 V absolute maximum (VDDIO + 0.3 V), forward-biasing the ESD diodes to VDDIO and overstressing the input gate oxide.

Board level-shifters were tried as a workaround. They added about 4.5 ns in each direction and broke SPI read timing at 104 MHz, so they were usable only for bring-up at 25 MHz.

### 4.4 Why it escaped

The architecture specification and the pad-ring specification were owned by different teams, and no step compared them. DRC and LVS passed because the cells were legal library cells. Functional simulation used ideal pad models with no voltage checks.

### 4.5 Cost and schedule

$4.9M: mask set $3.8M, hot lot $0.25M, requalification $0.45M, board re-spin and bring-up $0.4M. 19 weeks. The fix changed the I/O device type (thick gate oxide and extra implant), so it required new base-layer masks.

### 4.6 Corrective actions

- Per-bank cross-check of architecture interface voltage, pad-ring VDDIO, cell type and cell maximum rated VDDIO, signed by the Package & I/O lead and the Chief Architect.
- IP BOM records the I/O cell type used on each bank.
- Checklist rule added: CHK-SPEC-03.

## 5. PM-2023-03: ALX-3100 HARRIER (N7-class) - unsynchronized wake pulse waived as quasi-static

### 5.1 Timeline

| Date | Event |
|---|---|
| 2022-12-09 | A0 tape-out |
| 2023-03-06 | A0 first silicon |
| 2023-04-12 | System validation: intermittent resume failures from idle |
| 2023-04-28 | Root cause confirmed |
| 2023-05-19 | A1 tape-out (metal-only ECO) |
| 2023-07-21 | A1 production release |

### 5.2 Symptom

About 1 in 4,000 resume attempts from low-power idle failed in the field, where the deepest idle divider (/64) was used only after long idle periods. The device stayed in idle until the watchdog reset it. With the idle divider forced to /64 in the lab (core clock 12.5 MHz, 80 ns period), about one wake in three was lost.

### 5.3 Root cause

The always-on domain generated the wake request as a single-cycle pulse (one AON clock cycle, 52 ns at 19.2 MHz). It entered the core domain directly into a flop with no synchronizer. The structural CDC tool flagged the crossing, and it was waived as "quasi-static" on the grounds that wake events occur milliseconds apart. With the divided idle clock the pulse was shorter than the destination clock period and could be missed completely. At full clock rate it was sampled asynchronously, which is a metastability hazard.

### 5.4 Why it escaped

The waiver review asked how often the signal changes rather than whether it is a level or a pulse. The CDC report named the signal "wake request" and did not describe its shape. RTL simulations of idle entry and exit ran with the undivided clock, and gate-level simulation with the divided idle clock was not in the verification plan.

### 5.5 Cost and schedule

$1.7M: 14 metal and via masks $1.1M, metal-hold wafer processing $0.15M, requalification $0.3M, engineering $0.15M. 11 weeks. The fix used spare flops: a toggle flop in the AON domain, a 2-FF synchronizer and an edge detector in the core domain.

### 5.6 Corrective actions

- Quasi-static waivers restricted to level signals with a documented stability guarantee; pulses and event strobes require a pulse synchronizer or handshake.
- CDC waiver records state the signal class (level or pulse) and the destination clock period in every power state.
- Low-power entry/exit GLS runs with every idle clock divider setting.
- Checklist rule added: CHK-CDC-04.

## 6. PM-2024-02: ALX-4100 MERLIN (N7-class) - PCIe L1.2 exit link-down, A0 -> A1

### 6.1 Timeline

| Date | Event |
|---|---|
| 2023-10-06 | Coverage waiver granted for the PCIe L1.2 entry/exit covergroup at 78% (84 of 108 bins) |
| 2023-10-13 | A0 tape-out |
| 2024-01-08 | A0 first silicon |
| 2024-01-29 | System validation: link-down on L1.2 exit on host platforms with aggressive ASPM |
| 2024-02-12 | A0 cold characterization: LPDDR5X RDQS gate training fails at Tj <= -10 C (later ALX4100-E07) |
| 2024-02-20 | Root cause of the link-down confirmed (ALX4100-E03) |
| 2024-02-23 | Decision: full base-layer respin |
| 2024-03-29 | A1 tape-out |
| 2024-06-24 | A1 first silicon |
| 2024-08-30 | A1 production release |

### 6.2 Symptom

The link went down on about 1 in 3,000 L1.2 exits on hosts that re-assert CLKREQ# early. The LTSSM fell from Recovery to Detect and the host lost the endpoint. The only A0 workaround was to disable L1.2, which broke the idle-power requirement of the target add-in-card platforms.

### 6.3 Root cause

When the host re-asserted CLKREQ# while the endpoint's T_POWER_ON timer was still running, the in-house L1 PM substates sequencer (l1ss_ctl rev 1) released the PHY from P1.2 before REFCLK was valid. The PHY receiver could not lock.

### 6.4 Why it escaped

At tape-out the L1.2 entry/exit covergroup stood at 78%. A coverage waiver was granted under schedule pressure on the grounds that the remaining bins were low-risk corner cases. The uncovered cross bins included CLKREQ# re-assertion during T_POWER_ON at every link rate, which is exactly the failing scenario. No directed test drove CLKREQ# during the T_POWER_ON window.

### 6.5 Cost and schedule

$11.6M: N7-class mask set $9.8M, 300 mm hot lot $0.35M, re-characterization and requalification $0.9M, debug and bring-up $0.55M. 22 weeks. The fix touched the L1 substates sequencer and the PHY power-state interface and exceeded spare-cell capacity. The A1 respin also carried the fixes for ALX4100-E04 and ALX4100-E14.

The RDQS cold-training issue (ALX4100-E07) was also found on A0. No fix was available from the IP vendor before A1 tape-out, so it was handled by a datasheet restriction: cold boot at Tj >= 0 C, which is acceptable for a part specified at Tj 0 to +105 C. The vendor fix (LPX-1182) was released later in MC-LP5X / PHY-LP5X v2.7.0 (2025-02-27). The erratum is tracked for the next generation as carry-forward erratum ALX4100-E07.

### 6.6 Corrective actions

| Action | Owner | Status |
|---|---|---|
| Covergroups for features with an escape history are classified Escape-history and cannot be waived (interim directive QD-2024-05, 2024-06) | O. Feldman | Closed: formalized as CHK-VER-07 in checklist rev 7.1 |
| Redesign the L1 PM substates sequencer for the next generation (l1ss_ctl v3.0): P1.2 exit gated on REFCLK valid and T_POWER_ON expiry | L. Brandt | Closed 2025-09 |
| Directed and constrained-random L1.2 sequences with CLKREQ# re-assertion throughout the T_POWER_ON window, at every link rate | T. Wierzbicki | Transferred to the next-generation verification plan (KST-VPLAN-010 sections 7 and 9); delivery tracked at the KESTREL TRRs |
| Track the vendor fix for RDQS cold training (LPX-1182) | A. Deshmukh | Closed 2025-03 (fix in v2.7.0) |
| Review every ALX-4100 erratum for carry-forward to the next generation | L. Brandt / A. Deshmukh | Closed 2025-11 (ALX4100-ERR rev 3.1) |
| Require resolution of every carry-forward erratum at tape-out | O. Feldman | Closed: CHK-IP-03 in checklist rev 7.1 |

Checklist rules added: CHK-VER-07, and later CHK-IP-03 after the errata review.

## 7. Cross-program observations

| Pattern | Post-mortems | Rule |
|---|---|---|
| Two documents owned by different teams disagree and nothing compares them | PM-2022-01 | CHK-SPEC-03 |
| A waiver or exclusion is approved under schedule pressure on a qualitative argument | PM-2023-03, PM-2024-02 | CHK-CDC-04, CHK-VER-07 |
| A check is run on a subset of the relevant cases (pads, bins, power states) | PM-2021-02, PM-2023-03, PM-2024-02 | CHK-PV-02, CHK-CDC-04, CHK-VER-07 |
| A known issue on the previous chip is handled by a workaround that the next chip cannot use | PM-2024-02 | CHK-IP-03 |

## 8. Revision history

| Rev | Date | Change |
|---|---|---|
| 1 | 2021-05-14 | PM-2021-02 |
| 2 | 2022-05-20 | Added PM-2022-01 |
| 3 | 2023-08-11 | Added PM-2023-03 |
| 4 | 2025-12-05 | Added PM-2024-02 with final cost; corrective-action status updated; cross-program observations added |
