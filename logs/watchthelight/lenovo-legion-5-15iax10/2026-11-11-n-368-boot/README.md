# N-368: first boot of the WTLWireless bundle (MT792x phase 2, step 2)

Staged 2026-11-10 after the N-367 pass. The Wi-Fi core and the native front end load from one bundle,
`WTLWireless.kext` 0.14.0, in place of `MtkWlan.kext` 0.13.0 and `MtkWlanNative.kext` 0.4.17. Boot-args stay
"mtkfe=native mtknativeif=1". `MtkBt.kext` 0.2.4 is not touched in this boot: it has no guard, so the Bluetooth
plugin gets its own boot after this one passes.

## Change

- Six C++ classes and three bundle IDs renamed (MtkWlan to WTLWireless and so on, list in
  `docs/mt792x-unified.md`, "Phase 2 step 2 as built"). One version for the three parts, 0.14.0.
- `native/drivers/WTLWireless/build.sh` builds the parts and puts the bundle together.
- The core steps aside when the older `MtkWlan` class is in the kernel too (`MtkConflict` on the PCI device).
- OCEFI: `Kexts/WTLWireless.kext` added. Kernel > Add: `WTLWireless.kext` right after the `MtkWlan.kext` entry and
  `WTLWireless.kext/Contents/PlugIns/WTLWirelessNative.kext` right after the `MtkWlanNative.kext` entry (same kernel
  limits, 25.0.0 to 25.99.99); the two old entries are disabled, their folders stay. `config.n-368.plist.bak` is the
  config from before.

## Checked before the boot

- `tests/hwtrace/run.sh`: 3589 events, two runs identical, UBSan clean, ops v6 agrees with v5, a card without a chip
  row is not touched, and with the old class present the core touches nothing and publishes `MtkConflict`.
- `tests/hwtrace/compare.sh 7d8476f4` (0.13.0): the 3573 hardware lines are identical; one status line differs, the
  one that names the native front end. `selftest.sh` still catches both planted changes; `tests/run.sh` passes.
- Kernel imports (`nm -u`) of the three new binaries against the released ones: the native and Bluetooth parts
  are identical; the core adds `OSMetaClass::getMetaClassWithName` and `OSSymbol::withCString`, which the running
  MtkWlanNative 0.4.17 already imports. The kernel collection checks (kmutil, linkcheck) were skipped (I-116).
- Native part: 23 and 225 overrides on Apple's slots for 25G416, 0 wrong; allow-list holds 25G241, 25G332, 25G416.
- `entries.py` on a scratch copy of the OCEFI config: the switch changes nothing but the four entries; turning the
  pairs round gives the original enabled list back; a plugin without its core entry, or before it, is refused.
- `abi-check` picks the kext the config loads (old config: MtkWlanNative.kext; switched config: the plugin).
- `mtkwifi` built with both class names reads the running 0.13.0 core.

## Pass criteria

1. wifi-guard stage E pass, and "lastgood refreshed from the passing set: WTLWireless.kext"; `wifi-lastgood/Kexts`
   then holds only the bundle and its config equals the live one.
2. `kextstat`: org.watchthelight.WTLWireless and org.watchthelight.WTLWireless.Native at 0.14.0, neither old ID;
   org.watchthelight.MtkBt 0.2.4 still there and `MtkBtState` as before.
3. `ioreg -c WTLWireless`: W6 pass, `MtkNativeCoreOps` 6, `MtkNativeVersion` 0.14.0; no `MtkConflict` on the card.
4. Channel list, PHY modes, card type and `IO80211HardwareVersion` identical to `../N-364/baseline-n363.txt`; link
   as in N-367 (5 GHz, 80 MHz, 2 streams).
5. The capture holds `ioreg-wtlwireless.txt` and `ioreg-wtlwirelessnative.txt`; `mtkwifi status` works;
   `abi-check` reports the plugin as allow-listed.

A failure is rolled back by the guard: it puts the two old kexts and the old config back from `wifi-lastgood`.

## Result

**Pass** (boot 2026-11-10 20:17:31 EST, 25G416, Hybrid: "Current FB at 0x70800000").

1. Guard: start 20:17:35, pass at 20:18:08, capture and "lastgood refreshed from the passing set: WTLWireless.kext"
   at 20:18:24. `wifi-lastgood/Kexts` holds only the bundle, equal to the live folder; its config equals the live one.
2. OpenCore injected `WTLWireless.kext` v0.14.0, `MtkBt.kext` v0.2.4 and the native plugin v0.14.0, each "Success".
   `kextstat`: org.watchthelight.WTLWireless (0.14.0), org.watchthelight.WTLWireless.Native (0.14.0),
   org.watchthelight.MtkBt (0.2.4); neither old Wi-Fi ID. `MtkBtState` ready, Bluetooth on.
3. `ioreg -c WTLWireless`: "W6 pass: en1 passing traffic", `MtkNativeCoreOps` 6, `MtkNativeVersion` 0.14.0. No
   `MtkConflict` anywhere in the registry. The classes under the core and under the native service are the same as
   in N-367 apart from the names.
4. Channel list, PHY modes, card type and `IO80211HardwareVersion` identical to `../N-364/baseline-n363.txt`. Link
   5g44/80, 11ac, MCS 9, 2 streams, 866 Mbit/s, WPA2 Personal. System Information shows firmware version
   "WTLWirelessNative 0.14.0".
5. The capture holds `ioreg-wtlwireless.txt` and `ioreg-wtlwirelessnative.txt` (eleven files as before);
   `mtkwifi status` reads the new core; `abi-check` ran at boot against the plugin's plist and found the build
   allow-listed.

Not exercised: the conflict path on the machine (both sets enabled at once; host test only), the Ethernet fallback
with the new class name (`mtknative=0`), a rollback from the bundle to the old kexts, and the Bluetooth plugin
(N-369).

Files: `state.txt`, `opencore-2026-11-11-011722.txt` (redacted).
