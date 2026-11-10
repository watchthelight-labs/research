# N-362: MtkWlanNative 0.4.16 on 25G416, baseline restored

Staged 2026-11-10 18:32 EST from the N-361 boot (Hybrid, OCEFI) with `native/tools/wifi-guard/stage.sh N-362 E`. The guard's rollback set (`wifi-lastgood`) got the 25G416 plist entry first, so a rollback lands on the proven N-361 state and not on I-132.

## Change since N-361
- MtkWlanNative 0.4.16 on OCEFI in place of 0.4.15 with the hand-added plist entry. Same source; headers regenerated
  from the 25G416 dump, allow-list 25G241, 25G332, 25G416, binary sha256 719768fc2964. MtkWlan stays 0.12.1 (the staged
  copy is the same binary, sha a15f492e7ca9).
- Baseline back to the N-358 state: OCEFI `LegionCpuPower.kext` enabled again, XeGfxIntelFB and XeGfxAGDC back in the aux
  collection (both were taken out only for the macOS update, N-359). LegionCpuPower has not run on 25G416 yet.
- boot-args unchanged (`mtkfe=native mtknativeif=1`).

## Pass means
- wifi-guard stage E verdict pass (en1 lease, native front end active).
- `ioreg -r -c MtkWlan -l -w0 | grep -E 'MtkFrontEnd|MtkNativeAbi'`: native, build 25G416, kext version 0.4.16.
- `sysctl debug.legioncpu.status` answers; no panic file.

## Rollback
The guard restores `EFI/OC/wifi-lastgood` (0.4.15 with the 25G416 plist entry, config) and restarts when stage E fails.
`config.n-362.plist.bak` is the config before staging. LegionCpuPower off again: Enabled=false in Kernel>Add.

## After a pass
Export 0.4.16 (`scripts/publish/export.py MtkWlanNative`), README builds line, release with the bundle (it also carries
the `mtkwifi add` fix, I-130), then rsync OCEFI to the stick (stick copy: LauncherOption Disabled, ShowPicker true).

## Result: pass
Boot 2026-11-10 18:28 EST, Hybrid (FB at 0x70800000), OCEFI. Files: `state.txt`, `opencore-2026-11-10-232755.txt`
(redacted). The guard's capture is in `~/.cache/legion/wifi/N-362-pass`.
- wifi-guard stage E: pass (lease on en1, gateway answers), no rollback, lastgood refreshed by the guard.
- MtkWlanNative 0.4.16 loaded, `MtkFrontEndActive native`, `MtkNativeAbiBuild 25G416`. Link as before the update
  (N-356): 5g44/80, 11ac, 866 Mbps, WPA2 Personal, US, RSSI -38 dBm.
- LegionCpuPower 0.4.1 runs on 25G416: hwp 1, pl 1, guard on, MCHBAR mapped, fan control and scheduler hints up.
- XeGfxIntelFB 0.9 and XeGfxAGDC 0.1.1 loaded again, MtkBt ready, Bluetooth on.
- No panic. One bluetoothd ExcUserFault report 32 s after boot; the same single report exists for every boot since
  2026-11-09 (also before the 25G416 update), and Bluetooth works, so it is not this attempt's.

## Not checked
The Wi-Fi menu on screen, a Bluetooth device connection, sleep (unsupported).

## Done after the pass (2026-11-10)
- MtkWlanNative 0.4.16 exported and released: https://github.com/watchthelight-labs/WTLWifiMenu/releases/tag/0.4.16
  (public build is byte-identical to the booted kext, sha256 719768fc2964). README and CHANGELOG name 25G342 and 25G416.
- Bundle `mt7925-wifi-bundle-0.12.1+0.4.16.zip` on the WTLMtkWireless 0.12.1 release; its Recovery folder has the
  `mtkwifi` with the I-130 fix. `make-bundle.sh` now downloads from the renamed repos.
- WTLMtkWireless #6 answered (MtkFrontEnd against MtkFrontEndActive, country US against CN, the bundle); the tester's HP
  OMEN (103C:8C38) is in the README card table. The misleading property is in the tracker as a new issue.
- README now says what really happens on an unlisted build: the Ethernet front end comes up and nothing joins until
  `sudo mtkwifi join` (that was N-360).
- NOT done: the stick. It is not plugged in, so OCEFI was not copied to it.
