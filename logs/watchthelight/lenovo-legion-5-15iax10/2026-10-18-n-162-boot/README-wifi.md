<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-162/README-wifi.md | author: watchthelight </wtl> -->
# N-162: Wi-Fi front-end race fix, forced late path (I-072)

Kexts only, under the wifi-guard (stage E). No GPU package staged; the GPU driver stays 2.3.5-nvgfx.5 from N-161.

**Why:** on N-161 the Wi-Fi menu was gone. The core's 15 s fallback started the Ethernet front end at 13:31:44.569;
MtkWlanNative reached `bindCore` 230 ms later and was refused for the whole boot. The time went into Apple's
`IO80211SkywalkInterface` start (13:31:27.615 to 13:31:44.798). Same gap on earlier boots today, core publish to
"Skywalk Interface added monitor timers": 10:17 19.4 s, 13:03 26.3 s, 13:10 0.005 s, 13:25 15.3 s.

**Staged:** MtkWlan 0.11.1 (MTK_CORE_FE_CLAIM, 90 s window once claimed, `MtkFrontEndClaimMs`, `MtkFrontEndBoundMs`,
PCI match adds 0x071714c3) and MtkWlanNative 0.4.10 (claim at the end of probe, decline on every give-up in start,
debug `mtknativedelay`). Boot-args `mtkfe=native mtknativeif=1 mtknativedelay=25000`.

**Pass:** guard PASS; `MtkFrontEnd` native and no `MtkFrontEndFallback`; `MtkFrontEndClaimMs` set; `MtkFrontEndBoundMs`
above 25000; MtkWlanNative trace has `ctl:delay 25000 ms` then `dp:bound`; `networksetup -listallhardwareports` shows a
Wi-Fi port for en1 and the menu lists networks.

**Next:** N-163 = same kexts without the delay (normal boot), then release and the RZ717 kit.

## Result (checked 14:33 by the GPU session; the Wi-Fi session was not running)

wifi-guard: stage E pass (lease, gateway answers), auto_reboots 0. Kexts MtkWlan 0.11.1, MtkWlanNative 0.4.10. en1
is listed as "Hardware Port: Wi-Fi", `ipconfig getsummary en1` shows InterfaceType WiFi and an SSID, default route
on en1, ping to IP-2 works (83 to 299 ms). But at 14:33 `networksetup -getairportnetwork en1` says "not
associated", MtkNativeJoin reads "requests 2 ok 2 failed 0 leaves 1 linkdowns 1 linkup 1 beaconreports 0" and
MtkNativeInterface "No": the Family saw a leave and a link-down after the pass, and no beacon/LQM reports were
posted this boot (0.4.9 posted one per second while linked). Worth checking before N-163: whether the forced 25 s
delay path skips the beacon/LQM service, and whether the menu shows the network. GPU side of this boot: first boot
with plugin 2.3.5-nvgfx.6 in WindowServer, 1680x1050 HiDPI at 165 Hz, Finder drag 58 to 59 flips/s, 0 crashes.
