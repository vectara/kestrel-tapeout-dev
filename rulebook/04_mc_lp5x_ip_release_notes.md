# MC-LP5X / PHY-LP5X Release Notes

| Field | Value |
|---|---|
| Doc ID | MIPV-RN-LP5X-027 |
| Title | MC-LP5X / PHY-LP5X Release Notes (vendor) |
| Revision | 27 |
| Date | 2026-05-14 |
| Owner | MIPV (third-party memory-interface IP vendor) |
| Status | Released to licensees |
| Products | MC-LP5X LPDDR5X/LPDDR5 memory controller (soft IP); PHY-LP5X-N7 and PHY-LP5X-N5 hardened PHY macros |
| Project | KESTREL (ALX-5100), PRJ-2025-017 (licensee reference copy) |
| Classification | Aldercrest Confidential - synthetic demo data |

## 1. About this document

These release notes cover the MC-LP5X memory controller and its matching hardened PHY macros, PHY-LP5X-N7 (foundry N7-class) and PHY-LP5X-N5 (foundry N5-class). They list every general-availability and early-access release still in support, with fixed and known issues. Release candidates and engineering drops are not listed. Ticket numbers (LPX-nnnn) are the vendor's issue-tracking IDs; quote them in support requests.

## 2. Release summary

| Version | Date | Status | Fixed issues | Known issues |
|---|---|---|---|---|
| v2.5.0 | 2023-03-10 | Superseded | LPX-1034, LPX-1051, LPX-1066 | LPX-1107 (RFM counter); LPX-1182 (cold RDQS gate training; affects all releases before v2.7.0) |
| v2.6.0 | 2023-09-22 | Superseded | LPX-1107, LPX-1119, LPX-1128; LPX-1112 (feature: LPDDR5X-8533) | LPX-1150, LPX-1163, LPX-1182 |
| v2.6.1 | 2024-06-18 | Production (maintenance branch) | LPX-1150, LPX-1163 | LPX-1182: RDQS gate training may fail at Tj <= -10 C - NOT fixed in 2.6.x; fix only in 2.7.0; no back-port planned to the 2.6.x branch |
| v2.7.0 | 2025-02-27 | Production-qualified (silicon-proven on vendor N5-class test chip) | LPX-1182 (FIXED: cold RDQS gate training; requires PHY-LP5X v2.7.0), LPX-1171, LPX-1190, LPX-1204; includes all 2.6.x fixes (LPX-1107, LPX-1119, LPX-1128, LPX-1150, LPX-1163) | LPX-1231 (performance counter saturation; SW workaround) |
| v2.8.0-EA | 2026-05-14 | Early access - NOT production-qualified | LPX-1231, LPX-1238 | LPX-1246, LPX-1252; not for production tape-outs |

Recommended release for new foundry N5-class production tape-outs: **v2.7.0** (controller and PHY).

## 3. Release details

### 3.1 v2.5.0 (2023-03-10) - Superseded

LPDDR5X-7500 support. Controller and PHY-LP5X-N7 only; no N5-class PHY at this release.

| Ticket | Component | Severity | Description | Status |
|---|---|---|---|---|
| LPX-1034 | MC | High | DFI read-data-valid latency miscalculated for RL settings above 20 at 7500 MT/s | Fixed |
| LPX-1051 | MC | Medium | WCK2CK synchronization timing (tWCKENL_FS) violated on frequency-set-point switch | Fixed |
| LPX-1066 | PHY | Medium | Write-leveling results not retained across frequency-set-point switch | Fixed |
| LPX-1107 | MC | Medium | Refresh-management (RFM) activation counter off by one; RFM issued one ACT late | Known issue, fixed in v2.6.0 |

### 3.2 v2.6.0 (2023-09-22) - Superseded

LPDDR5X-8533 support (LPX-1112). First release of PHY-LP5X-N5. Silicon-proven in licensee N7-class production silicon with PHY-LP5X-N7 v2.6.0.

| Ticket | Component | Severity | Description | Status |
|---|---|---|---|---|
| LPX-1107 | MC | Medium | RFM activation counter off by one | Fixed |
| LPX-1112 | MC + PHY | Feature | LPDDR5X-8533 timing parameter set and WCK 4266.7 MHz support | Added |
| LPX-1119 | MC | Medium | Periodic ZQ calibration command could collide with self-refresh entry | Fixed |
| LPX-1128 | PHY | Low | Duty-cycle adjuster (DCA) code not restored after retention exit | Fixed |

### 3.3 v2.6.1 (2024-06-18) - Production (maintenance branch)

Maintenance release on the 2.6.x line. Controller RTL update and PHY training-firmware and register-default update. PHY hard-macro base layers are unchanged from v2.6.0. PHY-LP5X-N5 v2.6.1 training sequence validated from Tj 0 C to +110 C; timing LIBs delivered at all foundry sign-off corners. Training at Tj <= -10 C is not supported on this release line (LPX-1182).

| Ticket | Component | Severity | Description | Status |
|---|---|---|---|---|
| LPX-1150 | MC | High | DFI low-power handshake (dfi_lp_ctrl_req / dfi_lp_ctrl_ack) timeout when the PHY is in retention | Fixed |
| LPX-1163 | MC | Low | ECC scrub-rate register reset value incorrect (0x0 instead of 0x40) | Fixed |
| LPX-1182 | MC + PHY | High | RDQS gate training may fail at Tj <= -10 C: tWCK2DQO drift (WCK-to-RDQS/DQ output offset) moves the RDQS preamble outside the gate-training search window; training can report PASS with a mis-centred gate | KNOWN ISSUE - not fixed in 2.6.x; fix in v2.7.0 only; no back-port planned |

### 3.4 v2.7.0 (2025-02-27) - Production-qualified

Silicon-proven on the vendor N5-class test chip at 8533 MT/s. PHY-LP5X-N5 v2.7.0 training sequence validated from Tj -40 C to +125 C. Controller and PHY must be upgraded together (Section 6). v2.7.0 is branched from v2.6.1 and includes all fixes released on the 2.6.x line (LPX-1107, LPX-1119, LPX-1128, LPX-1150, LPX-1163).

| Ticket | Component | Severity | Description | Status |
|---|---|---|---|---|
| LPX-1182 | MC + PHY | High | Cold RDQS gate training. Root cause: at Tj <= -10 C the tWCK2DQO drift exceeds the coarse range of the per-byte RDQS receive-enable delay line in the hardened PHY. v2.7.0 adds 2 UI of coarse delay taps and re-hardens the training FSM in the PHY hard macro (base-layer change; GDS re-released), widens the firmware search window and adds temperature-compensated re-centering. Firmware alone cannot search beyond the physical delay-line range | FIXED in v2.7.0; requires matching PHY-LP5X-N5 / PHY-LP5X-N7 v2.7.0 |
| LPX-1171 | MC | Medium | Link-ECC error counter not cleared on read | Fixed |
| LPX-1190 | PHY | Medium | Read DQ deskew training could time out with DBI enabled | Fixed |
| LPX-1204 | PHY | Low | VREF(DQ) training step-size register field one bit too narrow | Fixed |
| LPX-1231 | MC | Low | Performance-monitor counters saturate without setting the overflow flag | Known issue; SW workaround: read counters at least every 2 s. Fix planned for v2.7.1 |

### 3.5 v2.8.0-EA (2026-05-14) - Early access, NOT production-qualified

LPDDR6 preparatory features. For evaluation and early integration only. Not for production tape-outs.

| Ticket | Component | Severity | Description | Status |
|---|---|---|---|---|
| LPX-1231 | MC | Low | Performance-monitor counter overflow flag | Fixed |
| LPX-1238 | MC | Medium | Command-bus parity error not logged when the error interrupt is masked | Fixed |
| LPX-1246 | MC | Medium | LPDDR6 preparatory mode registers not validated in silicon | Known issue |
| LPX-1252 | PHY | Medium | Timing constraints for PHY-LP5X-N5 v2.8.0-EA incomplete for the test-mode views | Known issue |

## 4. Deliverables

| Product | Deliverable views |
|---|---|
| MC-LP5X | Encrypted RTL, synthesis constraints, CDC/RDC waiver file, DFI 5.1 interface guide, register map (IP-XACT), verification IP and example testbench |
| PHY-LP5X-N7 / PHY-LP5X-N5 | GDS, LEF (footprint, pin and bump map), LIB at the foundry sign-off corners, Verilog behavioral and timing-annotated models, IBIS, training firmware image, integration guide, ESD and latch-up report |

Controller and PHY deliverables are released as a matched pair under one version number. Licensees must verify package checksums against the release manifest (sha256) before integration.

## 5. Compatibility matrix

The controller and PHY versions must match. Mixed combinations are not supported because the training-sequencer interface between controller and PHY changes between release lines.

| Controller | PHY-LP5X-N7 | PHY-LP5X-N5 | Notes |
|---|---|---|---|
| MC-LP5X v2.5.0 | v2.5.0 | Not released | Superseded |
| MC-LP5X v2.6.0 | v2.6.0 | v2.6.0 | Superseded |
| MC-LP5X v2.6.1 | v2.6.1 | v2.6.1 | Maintenance branch; LPX-1182 open |
| MC-LP5X v2.7.0 | v2.7.0 | v2.7.0 | Recommended for production |
| MC-LP5X v2.8.0-EA | Not released | v2.8.0-EA | Early access only |

## 6. Upgrade notes

### 6.1 v2.6.0 -> v2.6.1

Drop-in maintenance update. Replace the controller RTL and the PHY training firmware image. The PHY hard-macro GDS base layers are unchanged; the LIB views are unchanged apart from the version attribute.

### 6.2 v2.6.x -> v2.7.0

- The controller and PHY must be upgraded together. MC-LP5X v2.7.0 requires PHY-LP5X-N5 v2.7.0 (or PHY-LP5X-N7 v2.7.0).
- v2.7.0 contains every fix released on the 2.6.x line up to v2.6.1 (LPX-1107, LPX-1119, LPX-1128, LPX-1150, LPX-1163); no 2.6.x fix needs to be re-applied.
- The PHY hard-macro GDS is re-released: the training FSM is re-hardened, which changes the base layers. The macro footprint, pin and bump locations in the LEF are unchanged, so the macro can be swapped in place before tape-out.
- Re-deliver the LIB views (all corners), the Verilog models and the training firmware image v2.7.0. New training registers TRN_GATE_WIN_EXT and TRN_TCOMP_EN default to enabled.
- Because the PHY base layers change, the LPX-1182 fix cannot be applied to silicon already built on 2.6.x by a metal-only change or by a firmware update.

### 6.3 v2.7.0 -> v2.8.0-EA

Not for production. Early-access licensees should keep production tape-outs on v2.7.0.

## 7. Support lifecycle

| Release line | Status | End of maintenance |
|---|---|---|
| 2.5.x | Superseded | Ended 2024-12-31 |
| 2.6.x | Maintenance: critical and security fixes only; no new features; LPX-1182 not back-ported | 2026-12-31 |
| 2.7.x | Production, recommended for new designs | Active |
| 2.8.x | Early access | Not applicable |
