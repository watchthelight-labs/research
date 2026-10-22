# N-141: stage D, MtkWlan 0.11.0 + MtkWlanNative 0.4.0, boot-args mtkfe=native mtknativeif=1

Guard result: FAIL after 240 s (no IPv4 lease), rolled back by itself, rebooted into the known-good set.

Stage C is now proven end to end: airportd parsed our 48 scan results ("AUTO-JOIN: Scan SUCCEEDED ... results=48",
one line per BSS with security, channel, phy and rssi; `airport-profile.txt` lists them under Other Local Wi-Fi Networks).

Stage D did not reach the association. The guard's seven `networksetup -setairportnetwork en1 "SSID-1"` requests each
produced: a directed scan (`scan:request ssidLen=11`), "Will associate to [... channel=108, rssi=-53]" with a private MAC,
GET WCL_LOW_LATENCY_INFO (answered 0), **SET SET_MAC_ADDRESS (0x170) refused with 58** by our ioctl allowlist, then
APPLE80211_IOC_ASSOCIATE failed with 58 ("Failed to associate ... returned error code 58, retrying"). `MtkNativeCalls`:
`I:1ab=14 S:20d=14 I:170=14 I:22d=14`, no `S:25c`. The core stayed idle (`MtkW1Join state 0 joins 0`), as designed with
auto-open off. 0x22d is DBRG_ENTROPY (slot 662, new on 25G241), also refused.

Fix in 0.4.1: admit 0x170 (dispatches to IO80211SkywalkInterface::setSET_MAC_ADDRESS, the Family's own code, which ends in
our slot 470 setMacAddress) and 0x22d (setDBRG_ENTROPY accepts the bytes); setMacAddress answers NotPermitted, not Error,
when the firmware refuses an address (the only refusal WCLJoinManager tolerates). Files: guard capture, the first join
attempt's log lines, a summary of the Family's INTERNAL ioctls.
