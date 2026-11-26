<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-380/README.md | author: watchthelight </wtl> -->
# N-380: WTLWireless 0.15.3 against the range extender network (I-142)

Staged on 2026-11-26 away from home, Bash at the machine and online through the iPhone tether.

## Change
`WTLWireless.kext` 0.15.3 from branch `wifi-0.15.3` (2d93009b), worktree `~/src/legion-wt-wifi0152`, built with
`NO_KMUTIL=1 NO_LINKCHECK=1` (I-116). Core dcfd63104939da86, native plugin cdffc44ce73e3218, Bluetooth plugin
117c68a0ea4d4adb. Against the booted 0.15.0 it carries three steps at once:
- 0.15.1: last `kMap7925` window 0x200000 long, MT7927 band index (MT7925 hardware trace identical);
- 0.15.2: report script, LQM noise and SNR, rx drop ring. Both driver parts are off without their boot-args, and
  the boot-args are not set here;
- 0.15.3: the I-142 fix (`evidence/native/N-379/README.md`).

wifi-guard stage E, boot-args unchanged (`mtkfe=native mtknativeif=1`). The guard asks macOS for the network that
was joined when the boot was staged.

## Pass
- wifi-guard: `~/.cache/legion/wifi/N-380-pass` (a lease on `en1`, the gateway answers).
- `kmutil showloaded`: the three parts at 0.15.3.
- `MtkW6RxTransInfo`: "ok" counts up; `MtkW6RxPackets` follows it.

## If it fails
- No lease within 240 s: the guard restores `EFI/OC/wifi-lastgood` (0.15.0) and restarts once. The tether keeps
  working either way. Its capture holds the ioreg of the driver: read `MtkW6RxTransInfo` there. "undecrypted" high
  means the hardware did not decrypt the translated frames; "nogroup4" high means no sequence numbers.
- A panic halts the machine (`debug=0x100`): power cycle, read `Kernel-*.panic` first.

## Result: pass (2026-11-26 12:38:54 EST boot)

- wifi-guard: PASS at 12:39:36, 38 s after the guard started: lease on `en1`, the gateway answers. The known-good
  set on OCEFI is now 0.15.3.
- Mode: Hybrid again (OpenCore log: "Current FB at 0x70800000"). No panic file, no crash report.
- `kmutil showloaded`: WTLWireless, WTLWireless.Native and WTLWireless.Bt at 0.15.3. State "W6 pass: en1 passing
  traffic".
- Link: WPA2 Personal, 11ac, channel 44, 80 MHz, 2 streams, MCS 9, 866 Mbps, RSSI -39. One handshake (m1 to m4 =
  1), no deauth, no rejoin. Default route on `en1`; HTTPS over `en1` answers (200 in 0.56 s), ping to IP-2 0 %
  loss.
- Counters 8 minutes in: `MtkW6RxPackets` 1037370, `MtkW6TxPackets` 726853, `MtkW6RxTrans` 657,
  `MtkW2Sec` "trans" (dropped translated frames) 0, `MtkW6RxBad` 2, `MtkW6RxDropped` 0.
- `MtkW6RxTransInfo`: "ok 657 undecrypted 0 amsdu 0 nogroup4 0 last 01310104".

## What the reading says about I-142

`last 01310104` decodes to: SEC_MODE 4 (CCMP), decrypted, a plain MSDU, group 4 present, WLAN index 19. Index 19 is
the entry that holds the group key. So the translated frames are the broadcast and multicast frames of this AP;
unicast frames arrive as 802.11 as everywhere else (over a million through the normal path). About 100 translated
frames a minute, the same rate as the 3513 in the half hour of N-379.

The guard's packet capture shows why that cost the lease: every DHCP reply on this network arrives with the
broadcast destination address (four replies, all broadcast). 0.15.0 dropped them with the other translated frames,
so the client never saw an offer. ARP requests from the gateway are broadcast as well.

Still open: why this AP's group frames are translated and the home AP's are not (`MtkW6RxTrans` 0 to 27 at home).
It does not matter for the fix, which takes them either way.

Not exercised by this boot: A-MSDU bursts on the translated path (amsdu 0), a rekey through the translated path
(g1 0), and the two boot-arg features of 0.15.2 (not set). The MT7925 changes of 0.15.1 ran without a fault.

Files: `boot-state.txt` (the readings above), `opencore-2026-11-26-173848.txt` (redacted). The guard's full
capture stays in `~/.cache/legion/wifi/N-380-pass` (it holds addresses and the network name).
