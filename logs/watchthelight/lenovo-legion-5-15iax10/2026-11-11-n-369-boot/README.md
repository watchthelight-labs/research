# N-369: Bluetooth from the WTLWireless bundle (MT792x phase 2, step 3)

Staged 2026-11-10 after the N-368 pass with `--no-kexts`: the bundle on OCEFI is the one N-368 booted. Only the
Kernel > Add list changes. `WTLWireless.kext/Contents/PlugIns/WTLWirelessBt.kext` 0.14.0 takes the place of
`MtkBt.kext` 0.2.4, whose entry stays in the list, disabled, with its folder.

## Change

The plugin is MtkBt 0.2.4 with the class and bundle ID renamed (`WTLWirelessBt`, org.watchthelight.WTLWireless.Bt)
and the version set to 0.14.0. Its kernel imports are the same as 0.2.4. The `MtkBt*` registry properties keep
their names. It links nothing from the Wi-Fi core.

## Before the boot (N-368, MtkBt 0.2.4)

`MtkBtState` ready, `MtkBtStep` done, one pass, 1265 ms, chip ID 31013 (0x7925), firmware version 16896.
System Information: Bluetooth on, chipset THIRD_PARTY_DONGLE, firmware v9736 c4881, transport UART, no device
connected, two known devices.

## Pass criteria

1. `kextstat`: org.watchthelight.WTLWireless.Bt (0.14.0), no org.watchthelight.MtkBt.
2. `ioreg -c WTLWirelessBt`: `MtkBtState` ready, `MtkBtStep` done, `MtkBtVersion` 0.14.0, same chip ID and
   firmware version.
3. System Information: Bluetooth on with the same chipset and firmware lines; the two known devices still listed.
4. Wi-Fi unchanged: guard stage E pass, "lastgood refreshed from the passing set: WTLWireless.kext", baseline
   identical.

Bluetooth has no guard. If it does not come up while Wi-Fi passes, the pair is turned round
(`WIFI_STAGE_ENTRIES="MtkBt.kext=WTLWireless.kext/Contents/PlugIns/WTLWirelessBt.kext"`) and the next boot is back
on MtkBt 0.2.4. A Wi-Fi failure is rolled back by the guard to the N-368 config, which loads MtkBt.kext.

Not covered by this boot: pairing a new device and audio over Bluetooth (nobody is at the machine to do it).

## Result

**Pass** (boot 2026-11-10 20:24:47 EST, 25G416, Hybrid: "Current FB at 0x70800000").

1. OpenCore injected `WTLWireless.kext` v0.14.0, the Bluetooth plugin v0.14.0 and the native plugin v0.14.0, each
   "Success"; no line for any of the three old kexts. `kextstat`: org.watchthelight.WTLWireless.Bt (0.14.0), no
   org.watchthelight.MtkBt.
2. `ioreg -c WTLWirelessBt`: `MtkBtState` ready, `MtkBtStep` done, `MtkBtVersion` 0.14.0, one pass, 1251 ms (1265 ms
   before), chip ID 31013, firmware version 16896, firmware build 20260813113236. No `MtkBt` class in the registry.
3. System Information: Bluetooth on, chipset THIRD_PARTY_DONGLE, firmware v9736 c4881, transport UART. Both known
   devices (headphones, phone) are still listed, none connected. One `bluetoothd` process. It wrote its usual
   user-fault report 30 s after boot (EXC_GUARD, the process goes on), the same one as in N-367 and N-368 with MtkBt
   0.2.4.
4. Wi-Fi guard: start 20:24:51, pass at 20:25:25, capture and "lastgood refreshed from the passing set:
   WTLWireless.kext" at 20:25:40. `wifi-lastgood/config.plist` now equals the live config, so a later Wi-Fi rollback
   keeps the Bluetooth plugin. Baseline identical (5 of 5 lines), link 5g44/80, 11ac, MCS 9, 2 streams, 866 Mbit/s,
   "W6 pass: en1 passing traffic", core ops 6, no `MtkConflict`.

With this boot all three parts load from the one bundle. The three old entries are still in Kernel > Add, disabled,
and the old kext folders are still on OCEFI.

Not exercised: pairing a new device, a connection to one of the known devices, audio over Bluetooth.

Files: `state.txt`, `opencore-2026-11-11-012439.txt` (redacted).
