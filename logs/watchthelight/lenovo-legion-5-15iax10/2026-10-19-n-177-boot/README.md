<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-177/README.md | author: watchthelight </wtl> -->
# N-177: MT7925 gone after a warm restart (I-081)

Public issue: https://github.com/watchthelight-labs/WTLMtkWireless/issues/1

Read on 2026-10-19 from Windows, read-only: the Tahoe Data volume via `scripts/diag/apfs-read.py` (bootdumps 20261019-150015Z = N-176 and 20261019-152509Z = N-177, DiagnosticReports), and the Windows System event log and PnP device properties. Times UTC unless marked local (EDT).

## Symptom (Bash, reported in claude.ai, note e56bdf34)
On the latest macOS boot Wi-Fi stopped working. A warm restart into Windows did not bring it back: the MT7925 was missing in Windows too. After a later shutdown and power-on it was back.

## Timeline
| Time | What |
|---|---|
| 15:00:15 | N-176 boots (MtkWlan 0.11.3 + MtkWlanNative 0.4.11, native front end). Normal bring-up: `W3 patch done`, `W3 pass: firmware running (N9 ready)`, `W4 pass`, native front end starts. |
| 15:24:36 | N-176 ends: shutdown_stall report, then a warm restart. |
| 15:25:09 | N-177 boots. `W2 pass: WFDMA rings up`, then `W3 fail: patch download`, so no Wi-Fi. |
| 15:29:06 | N-177 ends: shutdown_stall report, warm restart into Windows. |
| 11:29:27 local | Windows boot (type 0x0): the MT7925 is not enumerated at all. Its `DEVPKEY_Device_LastArrivalDate` is 11:34:24, so it never arrived in this boot. |
| 11:33:02 local | Event 1074: Explorer, "Shutdown Type: power off" (Bash chose Shut Down). |
| 11:34:24 local | Windows boot after the power-off: the MT7925 is back (status OK, driver IP-205, problem code 0). |

So a warm restart keeps the fault and a cold power-off clears it.

## Cause
MtkWlan has no restart or power-off handling: it never joins the IOKit power plane (no PMinit/joinPMtree), so `systemWillShutdown` is never called, and `stop()` does not run on a restart. A warm restart does not power-cycle the card, so the chip keeps running the previous session's firmware with its DMA rings pointing at host memory the next boot reuses. The bring-up's own WFSYS reset (`bringUp`, mt792x_wfsys_reset) and the PATCH_IS_DL check were not enough in N-177: the patch semaphore/download failed. After a second warm restart the card no longer showed up on the PCIe bus in Windows. Linux does this at shutdown (`mt7925_pci_shutdown` -> `mt7925e_unregister_device`: `__mt792x_mcu_drv_pmctrl`, `mt792x_dma_cleanup`, `mt792x_wfsys_reset`, tooling/reference/linux-mt76-v6.18/drivers/net/wireless/mediatek/mt76/mt7925/pci.c lines 30-54 and 597-600). Same family as I-050 (touchpad needs a cold power-off after Windows), opposite direction. Confidence: High that the card kept bad state across the warm reset; Medium that the missing shutdown quiesce is what caused it (not yet tested).

## Fix (branch wifi-shutdown-quiesce, commit 9f2215799ab, not built yet)
MtkWlan 0.11.4: joins the power plane in `start()` before `bringUp()` (so even a failed download is covered), acknowledges power states (sleep is off on this machine), and on `kIOMessageSystemWillRestart` / `kIOMessageSystemWillPowerOff` runs `quiesce()`: timer off, interrupt off, WFDMA host and PCIe MAC interrupt masks cleared, driver own, TX/RX DMA off (wait for busy clear), WFSYS reset, bus master off. It logs `MtkWlan: quiesced for restart (drv_own N, dma idle N, wfsys reset N)`.

## Test plan for the Mac
1. Build and install 0.11.4 on OCEFI (same bundle path).
2. Boot, use Wi-Fi, then Apple menu > Restart five times in a row: Wi-Fi up on every boot, `W3 pass` each time, the quiesce line in the previous boot's log.
3. Restart from macOS into Windows (F12, Windows Boot Manager): the MT7925 is present in Windows.
4. Shut Down still powers off (I-024 stays fixed).

## Workaround until then
When leaving macOS, or if Wi-Fi is missing in either OS, use Shut Down and power on again rather than Restart.

## Other notes
- `scripts/diag/apfs-read.py` needed a fix to read Tahoe after the Sequoia volumes were deleted (libfsapfs indexed the container's volume list without skipping empty slots). Commit 33306055aac on main.
- Both N-176 and N-177 ended with a shutdown_stall report (binary spindumps, `spindump -i` on macOS). Not read yet.
