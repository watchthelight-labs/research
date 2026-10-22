<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-142/n142-freeze-summary.md | author: watchthelight </wtl> -->
# N-142 freeze and the two panics, read from Windows

Read on 2026-10-18 from Windows, read-only: OCEFI (disk0s5) and the Tahoe Data volume via `scripts/diag/apfs-read.py`. Times are UTC.

Bash (Claude Code on Windows, no photo): the overnight Wi-Fi loop (Fable session) was frozen in the morning. After a reboot the mouse moved for a few seconds, then everything froze again. The rollback script did not seem to do anything.

## Boots (OCEFI OpenCore logs)
- 05:58:36 N-142 (MtkWlan 0.11.0 + MtkWlanNative 0.4.1, boot-args `mtkfe=native mtknativeif=1`). The guard passed at 06:00:47 (`pending.json`: result pass, "lease IP-185, gateway IP-6 answers"), so stage D association with DHCP worked. The machine later froze (panic, see below).
- 11:03:31: froze seconds after the desktop (panic).
- 11:08:21: same config. Bash then switched to Windows.

## Panics
`Kernel-2026-10-18-070423.panic` (written 11:04, for the overnight boot) and `Kernel-2026-10-18-070914.panic` (written 11:09, for the 11:03 boot) are identical in substance:
- `Kernel trap ... type = 14=page fault`, CR2 0x0 (NULL dereference), kernel_task.
- Backtrace: `CCDataPipe::enqueueBlob(CCDataPipeBlob*) + 0x128` <- `CCDataStream::saveData(...)` <- `CCFaultReport::triggerCoreCapture(CCDataStream*, OSSet*, bool)` <- `CCFaultReporter::completeReport(CCFaultReport*)` <- `IOTimerEventSource::timeoutSignaled`.
- Only com.apple.driver.corecapture 1.0.4 is in the backtrace. The fault reporter in play is the one MtkWlanNative creates at start (dmesg: "Created CCDataPipe (Owner: org.watchthelight.MtkWlanNative - Name: MtkWlanNativeFault)", "ctl:fault reporter ok"). When the IO80211 family files a fault report and the report completes, the data pipe behind it gets dereferenced while NULL.

## Why the rollback did nothing
- The guard rolls back only when an attempt fails. N-142 passed, so the guard copied the N-142 set into `EFI/OC/wifi-lastgood/` (MtkWlanNative 0.4.1, config with `mtkfe=native mtknativeif=1`) and marked the attempt done.
- The freeze came later, from a different bug, and the guard cannot act during a kernel panic. On the next boots it saw no pending attempt, and lastgood already pointed at the panicking setup anyway.

## N-143 (applied on OCEFI from Windows)
- `EFI/OC/config.plist` and `EFI/OC/wifi-lastgood/config.plist`: `mtkfe=native mtknativeif=1` -> `mtkfe=ethernet mtknativeif=0`, which is the N-95/N-97 stage A path: Wi-Fi through MtkWlanEth en1, MtkWlanNative as controller only, no native interface. Backups `EFI/OC/config.n-143.plist.bak` and `EFI/OC/wifi-lastgood/config.n142.plist.bak`. Kexts unchanged.
- To fix in MtkWlanNative before native returns: give the fault reporter a valid CCDataPipe/CCDataStream that stays alive (or skip registering the fault reporter until it is complete), and check the CoreCapture objects' lifetime against the 25G241 IO80211 family.
