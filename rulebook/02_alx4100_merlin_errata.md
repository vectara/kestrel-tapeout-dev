# ALX-4100 (MERLIN) Silicon Errata

| Field | Value |
|---|---|
| Doc ID | ALX4100-ERR |
| Title | ALX-4100 (MERLIN) Silicon Errata |
| Revision | 3.1 |
| Date | 2025-11-12 |
| Owner | Leo Brandt / Anjali Deshmukh (errata board) |
| Status | Released |
| Applies to | ALX-4100 A0 (engineering samples) and A1 (production) silicon |
| Project | KESTREL (ALX-5100), PRJ-2025-017 (reference copy; source program MERLIN, ALX-4100, MRL) |
| Classification | Aldercrest Confidential - synthetic demo data |


## 1. Introduction

This document lists the known functional deviations of the ALX-4100 (MERLIN) inference accelerator (foundry N7-class) from its datasheet. It covers A0 engineering samples and A1 production silicon. A1 has been in production since 2024-Q3.

Each erratum states the conditions under which it occurs, its implications, the workaround and its status. The last column of the summary table is an internal assessment for the next-generation program. **Carry-forward = Yes** means the root cause lies in IP or logic that is expected to be reused, so the next program must show that its IP version contains the fix or that an in-house fix has been verified (carry-forward errata rule proposed for ALD-QA-CHK-007 rev 7.1).

### 1.1 Silicon revision identification

| Stepping | Status | Marking | IDCODE version [31:28] | Notes |
|---|---|---|---|---|
| A0 | Engineering samples only, not for production | ALX-4100-A0 | 0x0 | First silicon 2024-01 |
| A1 | Production | ALX-4100-A1 | 0x1 (0x0 on date codes before 2432, see ALX4100-E09) | Full base-layer respin; production since 2024-Q3 |

Aldercrest numbers production steppings sequentially (A0, A1, A2, ...) whether a respin changes base layers or metal only; the respin type is recorded in the post-mortem and the product change notice.

### 1.2 Memory interface IP

ALX-4100 A1 integrates LPDDR5X controller MC-LP5X v2.6.0 and hardened PHY PHY-LP5X-N7 v2.6.0 from vendor code MIPV. A0 integrated a pre-release controller drop.

## 2. Summary

| ID | Title | Affected | Workaround | Status / fixed-in | Carry-forward to next generation |
|---|---|---|---|---|---|
| ALX4100-E01 | NPU DMA descriptor prefetch stalls when the descriptor ring wraps at a 4 KiB boundary | A0, A1 | Driver pads the ring so its end is not 4 KiB aligned (SDK 2.1+) | Open on ALX-4100 (SW workaround); fixed in NPU-DMA v1.3 (in-house) | Yes |
| ALX4100-E02 | PCIe AER correctable-error counter saturates at 0xFFFF without interrupt | A0, A1 | Driver reads and clears the counter every 10 s | Won't fix (SW workaround) | No |
| ALX4100-E03 | PCIe link-down on L1.2 exit when the host re-asserts CLKREQ# during T_POWER_ON | A0 | A0 only: disable ASPM L1.2 (L1.1 permitted) | Fixed in A1 (in-house l1ss_ctl rev 2) | Yes |
| ALX4100-E04 | LPDDR5X refresh-management (RFM) activation counter off by one | A0 | A0 only: program RAAIMT one step lower | Fixed in A1 by MC-LP5X v2.6.0 (vendor ticket LPX-1107) | Yes |
| ALX4100-E05 | I2C/SMBus clock-stretch timeout (25 ms) not honored | A0, A1 | Firmware watchdog aborts the transfer after 30 ms and issues a bus clear | Open on ALX-4100 (FW workaround); fixed in I2C-CTL v1.4 | Yes |
| ALX4100-E06 | UART baud-rate error 3.1% at 3 Mbaud | A0, A1 | Use 1.5 Mbaud or lower (error 0.5% or less) | Closed - documentation update (datasheet maximum 1.5 Mbaud) | No |
| ALX4100-E07 | LPDDR5X RDQS gate training fails at cold (Tj <= -10 C); training reports PASS with a mis-centred gate | A0, A1 | Datasheet restricts cold boot to Tj >= 0 C | Open on ALX-4100 (no fix in 2.6.x IP); fixed in MC-LP5X v2.7.0 + PHY-LP5X v2.7.0 (LPX-1182) | Yes |
| ALX4100-E08 | PVT thermal sensor reads +3 C high above 110 C | A0, A1 | Firmware thermal trip threshold raised by 3 C | Open on ALX-4100 (FW workaround); fixed in PVT-MON v1.1 (digital trim) | Yes |
| ALX4100-E09 | JTAG IDCODE version field reports A0 on A1 silicon | A1 (date code before 2432) | Read silicon revision from OTP field SILICON_REV | Fixed from date code 2432 by a final-test change (OTP IDCODE_VER_OVR; no mask change) | No |
| ALX4100-E10 | PLL lock-detect falsely asserts during spread-spectrum clocking ramp | A0, A1 | Enable SSC only after lock, or wait 100 us after lock-detect before switching the clock mux | Open on ALX-4100 (FW workaround); fixed in PLL-FRAC v3.0 | Yes |
| ALX4100-E11 | UART RX overrun flag not cleared by read of LSR | A0, A1 | Clear with an RX FIFO reset (FCR bit 1) | Open on ALX-4100 (SW workaround); fixed in UART-16550C v1.2 | Yes |
| ALX4100-E12 | OTP read margin failure at VDD < 0.70 V | A0, A1 | Boot ROM holds VDD_CORE >= 0.72 V (AVS disabled) until OTP shadowing completes | Open on ALX-4100 (boot ROM workaround); fixed in OTP v2.0 | Yes |
| ALX4100-E13 | QSPI DTR-mode read sampling failure at 200 MHz | A0, A1 | Use SDR up to 133 MHz or DTR up to 166 MHz | Open on ALX-4100 (configuration limit); fixed in QSPI-CTL v2.2 | Yes |
| ALX4100-E14 | NPU sparse-weight decompressor hangs on an all-zero 64-byte block | A0 | A0 only: compiler emits dense encoding for all-zero blocks | Fixed in A1 (in-house NPU tile) | Yes |

Carry-forward summary: 11 errata marked Yes (E01, E03, E04, E05, E07, E08, E10, E11, E12, E13, E14); 3 marked No (E02, E06, E09).

## 3. Erratum details

### ALX4100-E01: NPU DMA descriptor prefetch stalls when descriptor ring wraps at a 4 KiB boundary

- **Description:** When a descriptor ring wraps and the wrap point falls on a 4 KiB address boundary, the descriptor prefetcher fetches the address after the boundary instead of the ring base address. The channel waits for a descriptor that never becomes valid.
- **Conditions:** Descriptor ring whose end address is 4 KiB aligned. Observed with ring sizes of 4 KiB and 8 KiB allocated on page boundaries.
- **Implication:** DMA channel hang; recovery requires a channel reset. No data corruption.
- **Affected steppings:** A0, A1
- **Workaround:** Driver pads the ring so its end is not 4 KiB aligned (SDK 2.1+).
- **Status:** Open on ALX-4100 (SW workaround); fixed in NPU-DMA v1.3 (in-house).
- **Fixed in:** NPU-DMA v1.3 (in-house).
- **Carry-forward:** Yes. NPU-DMA is reused in the next generation. The next program must integrate NPU-DMA v1.3 or later and cover the ring-wrap case with an Escape-history covergroup.

### ALX4100-E02: PCIe AER correctable-error counter saturates at 0xFFFF without interrupt

- **Description:** The correctable-error counter in the ALX-4100 PCIe wrapper saturates at 0xFFFF. No interrupt or status bit indicates saturation.
- **Conditions:** Links with a very high correctable error rate (more than 6,500 errors per second) between driver polls.
- **Implication:** Error-rate telemetry under-reports. No data-integrity impact; uncorrectable errors are reported normally.
- **Affected steppings:** A0, A1
- **Workaround:** Driver reads and clears the counter every 10 s.
- **Status:** Won't fix (SW workaround).
- **Fixed in:** Won't fix (SW workaround).
- **Carry-forward:** No. Not carried forward: the counter is in the ALX-4100 PCIe wrapper, which is not reused.

### ALX4100-E03: PCIe link-down (LTSSM -> Detect) on L1.2 exit when host re-asserts CLKREQ# while the endpoint T_POWER_ON timer is still running; PHY released from P1.2 before REFCLK valid (~1 in 3,000 exits)

- **Description:** On exit from L1.2, if the host re-asserts CLKREQ# while the endpoint's T_POWER_ON timer is still running, the L1 PM substates sequencer (l1ss_ctl rev 1) releases the PHY from P1.2 before REFCLK is valid. The PHY receiver fails to lock, the LTSSM falls through Recovery to Detect and the link goes down.
- **Conditions:** L1.2 enabled; host platforms that briefly release and re-assert CLKREQ# early in the T_POWER_ON window (root-port behaviour at the edge of the L1 PM Substates timing that the endpoint must tolerate). Measured rate about 1 in 3,000 L1.2 exits on affected hosts.
- **Implication:** Surprise link-down; the host sees the endpoint disappear and must re-enumerate it. Not recoverable by the device driver.
- **Affected steppings:** A0
- **Workaround:** A0 only: disable ASPM L1.2 (L1.1 permitted).
- **Status:** Fixed in A1 (in-house l1ss_ctl rev 2).
- **Fixed in:** ALX-4100 A1 (in-house l1ss_ctl rev 2); KESTREL uses redesigned l1ss_ctl v3.0.
- **Carry-forward:** Yes. The L1 PM substates logic is redesigned for the next generation (in-house l1ss_ctl v3.0). The redesign must be verified to the Escape-history target (CHK-VER-07, >= 95.0%, no waiver) for L1.2 entry/exit, with every CLKREQ# re-assertion during T_POWER_ON bin covered at every link rate. See PM-2024-02.

### ALX4100-E04: LPDDR5X refresh-management (RFM) activation counter off by one

- **Description:** The rolling accumulated ACT (RAA) counter is compared with the RAAIMT threshold using a greater-than instead of a greater-than-or-equal comparison, so the controller issues RFM one ACT later than required.
- **Conditions:** RFM enabled (required by the LPDDR5X devices used). A0 integrated a pre-release controller drop.
- **Implication:** Under sustained single-bank activation patterns the device RAA limit can be exceeded by one ACT. No functional failure observed.
- **Affected steppings:** A0
- **Workaround:** A0 only: program RAAIMT one step lower.
- **Status:** Fixed in A1 by MC-LP5X v2.6.0 (vendor ticket LPX-1107).
- **Fixed in:** MC-LP5X v2.6.0.
- **Carry-forward:** Yes. MC-LP5X is reused. The next program must integrate MC-LP5X v2.6.0 or later.

### ALX4100-E05: I2C/SMBus clock-stretch timeout (25 ms) not honored

- **Description:** The controller waits indefinitely when a target holds SCL low. The SMBus tTIMEOUT limit of 25 ms is not enforced.
- **Conditions:** A target device that stretches SCL beyond 25 ms, typically during a target reset or firmware update.
- **Implication:** SMBus management interface to the host hangs until the firmware watchdog intervenes.
- **Affected steppings:** A0, A1
- **Workaround:** Firmware watchdog aborts the transfer after 30 ms and issues a bus clear.
- **Status:** Open on ALX-4100 (FW workaround); fixed in I2C-CTL v1.4.
- **Fixed in:** I2C-CTL v1.4.
- **Carry-forward:** Yes. I2C-CTL is reused. The next program must integrate I2C-CTL v1.4 or later and keep the clock-stretch covergroup as Escape-history.

### ALX4100-E06: UART baud-rate error 3.1% at 3 Mbaud

- **Description:** At 3 Mbaud the integer divisor available from the ALX-4100 UART reference clock at 16x oversampling gives a baud-rate error of 3.1%.
- **Conditions:** Baud rates above 1.5 Mbaud.
- **Implication:** Exceeds the +/-2.0% receiver tolerance of common host UARTs; framing errors.
- **Affected steppings:** A0, A1
- **Workaround:** Use 1.5 Mbaud or lower (error 0.5% or less).
- **Status:** Closed - documentation update (datasheet maximum 1.5 Mbaud).
- **Fixed in:** Documentation update.
- **Carry-forward:** No. Not carried forward: the divisor granularity is a property of the ALX-4100 clock plan; KESTREL UART0 uses a fractional baud-rate divisor (KST-ARCH-001 section 5.10).

### ALX4100-E07: LPDDR5X RDQS gate training fails at cold: at Tj <= -10 C, tWCK2DQO drift (WCK-to-RDQS/DQ output offset) moves the RDQS preamble outside the gate-training search window; training reports PASS with a mis-centred gate, causing read errors after boot

- **Description:** At Tj <= -10 C, tWCK2DQO drift (WCK-to-RDQS/DQ output offset) moves the RDQS preamble outside the gate-training search window of the 2.6.x training sequencer. Training reports PASS with a mis-centred read gate. Read errors appear after boot: first as ECC-corrected errors, then as uncorrectable errors under high-bandwidth traffic.
- **Conditions:** DRAM initialization and training (cold boot or exit from a power state that requires full retraining) at Tj <= -10 C. Training at Tj >= 0 C is unaffected; once trained warm, periodic retraining keeps the gate centred across the full range.
- **Implication:** Boot failure or silent read errors after a cold boot.
- **Affected steppings:** A0, A1
- **Workaround:** Datasheet restricts cold boot to Tj >= 0 C. A warm-up workaround (self-heat, then retrain) is not viable for a part that must boot cold: the die cannot rise from -40 C to above -10 C within a typical 150 ms power-on-to-firmware-ready budget.
- **Status:** Open on ALX-4100 (no fix in 2.6.x IP); fixed in MC-LP5X v2.7.0 + PHY-LP5X v2.7.0 (LPX-1182).
- **Fixed in:** MC-LP5X v2.7.0 + PHY-LP5X v2.7.0 (vendor ticket LPX-1182).
- **Carry-forward:** Yes. The Tj >= 0 C datasheet restriction is not available to a derivative with an industrial temperature grade that must cold-boot below 0 C. Such a device must integrate MC-LP5X and PHY-LP5X v2.7.0 or later. The vendor states that the fix is not back-ported to the 2.6.x maintenance branch.

### ALX4100-E08: PVT thermal sensor reads +3 C high above 110 C

- **Description:** Non-linearity in the sensor's digital conversion above 110 C makes the reading 3 C higher than the actual junction temperature.
- **Conditions:** Tj above 110 C (thermal-trip region).
- **Implication:** Premature thermal throttling or shutdown.
- **Affected steppings:** A0, A1
- **Workaround:** Firmware thermal trip threshold raised by 3 C.
- **Status:** Open on ALX-4100 (FW workaround); fixed in PVT-MON v1.1 (digital trim).
- **Fixed in:** PVT-MON v1.1 (digital trim).
- **Carry-forward:** Yes. PVT-MON is reused. The next program must integrate PVT-MON v1.1 or later.

### ALX4100-E09: JTAG IDCODE version field reports A0 on A1 silicon

- **Description:** The IDCODE version field [31:28] reads 0x0 on early A1 lots because the metal-programmable version cell was not updated for A1.
- **Conditions:** A1 units with date code before 2432.
- **Implication:** Test programs and software that identify the stepping from IDCODE apply A0 workarounds to A1 parts.
- **Affected steppings:** A1 (date code before 2432)
- **Workaround:** Read silicon revision from OTP field SILICON_REV.
- **Status:** Fixed from date code 2432 by a final-test change: the test program blows the OTP IDCODE_VER_OVR field, which the TAP uses in place of the version cell (no mask change).
- **Fixed in:** A1 final-test program (date code 2432).
- **Carry-forward:** No. Specific to the ALX-4100 A1 test flow.

### ALX4100-E10: PLL lock-detect falsely asserts during spread-spectrum clocking ramp

- **Description:** During the SSC down-spread ramp at start-up the lock detector reports lock while the loop is still settling.
- **Conditions:** SSC enabled before first lock.
- **Implication:** The downstream clock mux can switch to an unsettled clock; intermittent boot hang.
- **Affected steppings:** A0, A1
- **Workaround:** Enable SSC only after lock, or wait 100 us after lock-detect before switching the clock mux.
- **Status:** Open on ALX-4100 (FW workaround); fixed in PLL-FRAC v3.0.
- **Fixed in:** PLL-FRAC v3.0.
- **Carry-forward:** Yes. The fractional PLL is reused. The next program must integrate PLL-FRAC v3.0 or later.

### ALX4100-E11: UART RX overrun flag not cleared by read of LSR

- **Description:** With FIFOs enabled, the overrun error flag LSR[1] stays set after LSR is read.
- **Conditions:** FIFO mode, after an RX overrun.
- **Implication:** Drivers that poll LSR report continuous overruns.
- **Affected steppings:** A0, A1
- **Workaround:** Clear with an RX FIFO reset (FCR bit 1).
- **Status:** Open on ALX-4100 (SW workaround); fixed in UART-16550C v1.2.
- **Fixed in:** UART-16550C v1.2.
- **Carry-forward:** Yes. UART-16550C is reused. The next program must integrate v1.2 or later.

### ALX4100-E12: OTP read margin failure at VDD < 0.70 V

- **Description:** The OTP sense-amplifier margin is insufficient below 0.70 V; programmed bits intermittently read as 0.
- **Conditions:** OTP read with VDD_CORE below 0.70 V, for example with adaptive voltage scaling active at a fast-process part.
- **Implication:** Corrupted configuration or key material read from OTP.
- **Affected steppings:** A0, A1
- **Workaround:** Boot ROM holds VDD_CORE >= 0.72 V (AVS disabled) until OTP shadowing completes.
- **Status:** Open on ALX-4100 (boot ROM workaround); fixed in OTP v2.0.
- **Fixed in:** OTP v2.0.
- **Carry-forward:** Yes. The OTP macro is reused. The next program must integrate OTP v2.0 or later.

### ALX4100-E13: QSPI DTR-mode read sampling failure at 200 MHz

- **Description:** The read sampling point is not adjustable; at 200 MHz DTR the sampled data eye is closed across PVT.
- **Conditions:** DTR reads at clock frequencies above 166 MHz.
- **Implication:** Read data errors from the boot flash at 200 MHz DTR.
- **Affected steppings:** A0, A1
- **Workaround:** Use SDR up to 133 MHz or DTR up to 166 MHz.
- **Status:** Open on ALX-4100 (configuration limit); fixed in QSPI-CTL v2.2.
- **Fixed in:** QSPI-CTL v2.2.
- **Carry-forward:** Yes. QSPI-CTL is reused. The next program must integrate v2.2 or later (programmable sample delay).

### ALX4100-E14: NPU sparse-weight decompressor hangs on an all-zero 64-byte block

- **Description:** A compressed 64-byte block with an all-zero occupancy bitmap has a payload length of 0. The decompressor state machine waits for a payload beat that never arrives.
- **Conditions:** Sparse weight tensors that contain an all-zero 64-byte block.
- **Implication:** NPU tile hang; recovery requires a tile reset.
- **Affected steppings:** A0
- **Workaround:** A0 only: compiler emits dense encoding for all-zero blocks.
- **Status:** Fixed in A1 (in-house NPU tile).
- **Fixed in:** ALX-4100 A1 (in-house NPU tile).
- **Carry-forward:** Yes. The NPU tile is reused. The next program must carry the fix and keep the all-zero block covergroup as Escape-history.

## 4. Document history

| Rev | Date | Change |
|---|---|---|
| 1.0 | 2024-02-16 | Initial release for A0 engineering samples (E01..E07). |
| 1.1 | 2024-04-05 | Added E08, E10 and E14 from A0 characterization and NPU bring-up; E03 root cause updated. |
| 2.0 | 2024-08-30 | A1 production release. E03, E04, E14 fixed in A1. Added E09, E11, E12, E13. |
| 3.0 | 2025-06-20 | E07: vendor fix available in MC-LP5X v2.7.0 + PHY-LP5X v2.7.0 (LPX-1182); fixed-in updated. E06 closed by datasheet update. |
| 3.1 | 2025-11-12 | Added the carry-forward assessment column and per-erratum carry-forward notes for the next-generation errata review. No change to the A1 workarounds. |

## 5. Errata board

| Role | Name |
|---|---|
| PCIe subsystem | Leo Brandt |
| Memory subsystem (LPDDR5X) | Anjali Deshmukh |
| Quality | Oren Feldman |
| Chief Architect | Priya Raghavan |
