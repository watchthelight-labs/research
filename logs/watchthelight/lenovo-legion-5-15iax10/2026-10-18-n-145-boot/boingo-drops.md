<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-145/boingo-drops.md | author: watchthelight </wtl> -->
# N-145: Boingo keeps disconnecting on the native path (I-067), read from Windows

Read on 2026-10-18 from Windows, read-only: the Tahoe Data volume via `scripts/diag/apfs-read.py` (wifi-guard folder N-145-pass, known-networks plist, DiagnosticReports) and the Tahoe unified log for 12:08 to 12:24 UTC, parsed with unifiedlog_iterator 0.7.0. MAC addresses and private addresses left out.

Bash: macOS "keeps disconnecting from SSID-1" and shows Boingo's login page. He wants Boingo on the factory address and rotating private addresses for normal networks.

## Setup
N-145 = MtkWlan 0.11.0 + MtkWlanNative 0.4.4, `mtkfe=native mtknativeif=1`, stage E. Guard PASS 12:12:25 ("lease IP-185, gateway IP-6 answers"). No kernel panic: the I-066 pipe fix holds. One user-space `corecaptured` SIGSEGV at 12:11:31 in `CCCrashTracerFormatter::writeLog` <- `CCDataFile::writeLog` <- `CCDataTap::processEvent`, so our fault-report blobs are not well formed (low).

## The drops follow macOS background scans
Spontaneous link losses ("_handleLinkEvent: Link down event. Triggering auto-join", after the driver posts BSSID_CHANGED and LINK_CHANGED, and the Family runs WCL_LEAVE_NETWORK) against the last `Set type=<APPLE80211_IOC_WCL_SCAN_REQ>` before each one:

| Link down | Last WCL scan request | Gap |
|---|---|---|
| 12:11:30.016 | 12:11:15.975 | 14 s |
| 12:13:17.132 | 12:12:39.163 | 38 s |
| 12:14:37.536 | 12:14:37.533 | 3 ms |
| 12:15:47.618 | 12:15:47.615 | 3 ms |
| 12:17:05.978 | 12:16:55.491 | 10 s |
| 12:18:44.288 | 12:18:44.286 | 2 ms |
| 12:20:03.639 | 12:20:03.634 | 5 ms |
| 12:21:50.275 | 12:21:49.479 | 0.8 s |

So one link loss every 70 to 107 s, each one either right after a scan request or while a scan runs. Counts in the window: 111 WCL_SCAN_REQ, 245 SCAN_REQ, 10 WCL_SCAN_ABORT, 110 SET_SCAN_HOME_AWAY_TIME. The core snapshot at 12:12:25 shows `MtkW1Scan` "scans 26 ... running 1 ... userpending 1" and `MtkNativeJoin` "requests 5 ok 5 ... leaves 4 linkdowns 4". Traffic worked between drops (TCP 443 connections on en1 just before 12:13:17). On the Ethernet front end macOS never scans through our driver, and that path stays up for hours.

Conclusion (I-067): a scan request while associated tears down the link in the core / native path. Scans while connected must keep the station associated (off-channel scan with home/away dwell, honouring SET_SCAN_HOME_AWAY_TIME), or be answered from the BSS cache while associated.

## Captive portal and the private address
- SSID-1 in `com.apple.wifi.known-networks.plist`: `PrivateMACAddressModeUserSetting = 'static'` (updated 12:21:36, the System Settings "Fixed" choice), `CaptiveProfile.CaptiveWebSheetLoginDate` 12:14:03 (portal login done), `NetworkWasCaptive` true, a cached private address. The earlier hand-set value `"none"` (07:28) was not a value macOS uses; the airport profile at 12:12 still showed the private address.
- The login at 12:14:03 did not stop the drops (12:14:37 onward), so the captive portal does not cause them.
- A second captive network, Boingo_Wireless, was also joined (12:11:51).
- For Boingo the factory address is wanted (the portal already knows it from Windows). The System Settings value for that is "Off", not "Fixed".

## N-146 (applied on OCEFI from Windows)
`EFI/OC/config.plist` and `EFI/OC/wifi-lastgood/config.plist`: `mtkfe=native mtknativeif=1` -> `mtkfe=ethernet mtknativeif=0` (Ethernet front end: factory address, no macOS scans, no drops). Backups `EFI/OC/config.n-146.plist.bak` and `EFI/OC/wifi-lastgood/config.n145.plist.bak`. Kexts unchanged (MtkWlan 0.11.0, MtkWlanNative 0.4.4).
