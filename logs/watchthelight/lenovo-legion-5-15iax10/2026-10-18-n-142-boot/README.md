# N-142: stage D, MtkWlan 0.11.0 + MtkWlanNative 0.4.1, boot-args mtkfe=native mtknativeif=1

Guard result: PASS 75 s after boot (lease IP-185, gateway answers, SSID reported); the native set stayed and the
known-good set was refreshed from it.

**Stage D passes.** The guard's one `networksetup -setairportnetwork en1 "SSID-1"` produced the full sequence
(`MtkNativeCalls`): `I:1ab S:20d` low-latency info, `I:170 S:1d6` SET_MAC_ADDRESS (trace `if:setMacAddress
MAC-53 -> 0`, the per-network private address the firmware then answers to), `I:1ba S:25c` ASSOCIATE
(`assoc:request ssidLen=11 cipher=0 keyLen=0`, core `MtkW1Join joins 1`), events `P:d8 P:4e P:d3 P:d4 P:d5`, then the
Family's link-up: `S:20e` x3 WCL_BSS_INFO (ch 108, 340 bytes of IEs), `S:215` EXTENDED_BSS_INFO (6 rates), `S:1d4` x2
LINK_STATE_UPDATE, `S:27b` fast lane, `S:20f` traffic counters, `S:25d` QoS, `S:258` ARP mode, `S:25e` LINK_UP_DONE.
airportd: "IPv4/ROUTER ASSIGNED [ip=IP-185, router=IP-6]", "Successfully updated Wi-Fi configuration
following association". `MtkNativeJoin requests 1 ok 1`. macOS saved the network (known-networks plist, SystemMode,
cached private MAC) and **auto-joined it by itself on the next two boots** (07:05 and 07:10, from the plist's BSSList).

**What is still missing for apps (I-065):** Boingo is a captive network. configd's captive controller probed, found
WISPr, launched the Captive Network Assistant and kept en1 ranked Never (`configd-captive.txt`), so the default route
stayed interface-scoped (`netstat-rn.txt`: UGScIg). The Ethernet front end never saw this because the portal already
knows the factory MAC; the private address is a new client to it. A real Mac behaves the same: log in once in the
assistant, or turn "Private Wi-Fi address" off for that network. Bash put the Ethernet boot-args back by hand at 07:15.

Cosmetic: the Family showed "Firmware Version: MtkWlanNative 0.1.0" (a stale string in getDRIVER_VERSION, fixed in 0.4.2)
and Country Code XZ. The en1 network service in preferences.plist is still the stale Ethernet-type one ("Status: Network
Service Inactive" in the profile): stage E item.
