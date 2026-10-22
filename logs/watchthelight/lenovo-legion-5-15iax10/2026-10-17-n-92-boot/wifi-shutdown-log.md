<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-92/wifi-shutdown-log.md | author: watchthelight </wtl> -->
# N-92: Wi-Fi and Shut Down, read from Windows

Read on 2026-10-17 from Windows, read-only: the Tahoe Data volume via `scripts/diag/apfs-read.py` (bootdump 20261017-145547Z, DiagnosticReports, mtkwifi.log) and the Tahoe unified log parsed with unifiedlog_iterator 0.7.0. Times are UTC. MAC addresses left out.

## Boots in the log
- N-91, boot UUID 7B56ACE2..., until 14:55.
- N-92, boot UUID 653F7F3B..., 14:55:49 to 14:59:57 (bootdump says boot 14:55:47, kernel 25.6.0, Tahoe 26.7.1 25G241).

## Wi-Fi (MtkWlan 0.9.0)
- dmesg (bootdump, 20 s): `W3 pass: firmware running (N9 ready)`, `W4 pass: station ready (MAC, domain, power), scanning from the tick`, `W6 interface attached (link down until a network is joined)`. No W5 line. Later W-lines were lost, because the 128 KB dmesg ring had wrapped by the 60 s snapshot. The unified log keeps no MtkWlan IOLog lines.
- configd / IPConfiguration: en1 attached 14:56:45, `DHCP en1: start`, `en1 link INACTIVE`, `status = 'media inactive'` at 14:56:46. There's no link-active event before the end of the boot.
- launchd: org.watchthelight.mtkwifi spawned 14:56:47, `exited due to exit(0), ran for 247ms`. mtkwifi.log was last written at 14:44 (N-91, while 0.8.0 was loaded: "no user client").
- Cause (I-054): the OCEFI kext's Info.plist has `MtkAutoOpenSsids = ["Boingo"]`, and `MtkJoin.cpp` `cmPickOpen()` only accepts an exact match (`pl == b.ssidLen && !memcmp(...)`). The network is "SSID-1", so the open fallback never picks it.

## Shut Down
- 14:55:00, N-91: loginwindow `RECEIVED:(aevt,rsdn)`, `logoutType:3 - Shutdown`. PackageUIKit "Install in Progress" ran during the logout. `shutdown_stall_2026-10-17-075512` (14:55:12). The machine came back up as N-92 about 40 s later. That shutdown ran on N-91's ACPI tables, which don't have SSDT-FIXSHUTDOWN, so it does not test the N-92 fix.
- 14:59:52, N-92: loginwindow `RECEIVED:(aevt,rrst)` (Restart, sent from Terminal), `SLOStartLogoutOfType, mainType: 2`. `shutdown_stall_2026-10-17-080003` (15:00:03) belongs to this restart.
- N-92 OC log: `Applying 5 byte ACPI patch (N-92 Method (_PTS, 1) -> ZPTS (SSDT-FIXSHUTDOWN wraps it)) ... count 1`.
- Result: the Shut Down fix is still untested. Test it with Apple menu > Shut Down from a boot that loaded the fix (N-93).

## Other
- No new bluetoothd-*.ips during N-92 (the last ones are 13:07 to 13:12, N-91).
- Both stall reports are binary spindumps (`spindump -i` on macOS turns them into text).
