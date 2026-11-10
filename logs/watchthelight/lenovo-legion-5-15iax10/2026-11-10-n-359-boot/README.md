# N-359: macOS Tahoe 26.7.3 beta build 25G416, from 25G342

Staged 2026-11-09 ~22:30 EST. Bash approved 25G416 on 2026-11-08 ("Install now") and said on 2026-11-09 that the betas are the development target.

## State before
- 26.7.3 release build 25G342 (N-358), Hybrid boot, no XeGfx* and no LegionCpuPower loaded.
- Beta enrolment restored after it was removed by mistake earlier this evening (CatalogURL = index-26seed, DeveloperSeed).
- XeGfxIntelFB/XeGfxAGDC parked again in `~/src/XeGfx-build/parked-2026-11-09`, aux KC rebuilt without them (backup `/Library/XeGfx/backup-park-20261109-222708`).
- OCEFI: LegionCpuPower Enabled=false for the update boots (backup config.n359-pre.plist.bak, ocvalidate clean). I-116 rule.

## Change
`softwareupdate -i "macOS Tahoe 26.7.3-25G416" --restart`. From 25G342 it is offered as a full update (17.9 GB), not a delta.

## Pass list
- `sw_vers` 25G416.
- abi-check: MtkWlanNative allow-listed or verdict UNCHANGED; otherwise `native/tools/kcabi/refresh.py`.
- en1 lease and internet, Bluetooth on, LegionBtFix windows 1 and 1.
- No panics.
- NVIDIA line only on a Discrete boot (gpu-guard, Bash's Good).

## After the pass
- Unpark XeGfxIntelFB/XeGfxAGDC (aux KC rebuild), OCEFI LegionCpuPower Enabled=true.
- If prepare is refused again (I-131), record it there; the route is then a full installer for the seed build.

## Result
Pass for the install: prepare was not refused this time, the Legion restarted by itself and came up on 25G416. The Wi-Fi line of the pass list failed first (N-360, I-132) and passed in N-361 after the allow-list entry. NVIDIA line still open.

Reported by Bash in Claude Code on 2026-11-10 (no photo): macOS updated, no network afterwards.

Checked from Windows on 2026-11-10 (read-only). The no-network boots are tracker row N-360; its evidence is this folder.
- Two OpenCore boots of Tahoe at 21:55 and 21:58 UTC, both Hybrid (FB at 0x70800000), kernel 25.6.0, every kext injected, no panic file on OCEFI. Logs here, redacted.
- Likely cause (not confirmed, the Mac could not be read): MtkWlanNative 0.4.15 allow-lists the xnu tags of 25G241 and 25G332 only. 25G342 shared 25G332's tag; a seed build with a newer xnu makes `probe()` decline, the core falls back to its Ethernet front end and nothing joins the saved network through airportd. I-132.
- Not repaired from Windows: the allow-list entry needs the xnu tag and class sizes of 25G416, read from its kernel collection on the APFS volume. Adding a build without that check is what the guard exists to prevent.

Repair on the Mac (no network needed, the repo is local):
1. `ioreg -r -c MtkWlan -l -w0 | grep -E 'MtkFrontEnd|MtkNativeAbi'` shows the decline reason.
2. `python3 native/tools/kcabi/refresh.py --dry-run`, then without `--dry-run` if the verdict is unchanged. It rebuilds the kext with 25G416 allow-listed.
3. Copy the rebuilt kext to OCEFI (old one kept as `.kext.0415`), reboot.
Network in the meantime: `sudo mtkwifi join` (saved network, Ethernet front end), a cable on the Realtek port, or iPhone USB tethering.

## 2026-11-10 evening: cause confirmed and kext patched from Windows (I-132)
Bash: "You should be able to use tools to read it from Windows". Done with `scripts/diag/apfs_read.py` (new, read-only raw APFS reader).
- Preboot `SystemVersion.plist`: 26.7.3, 25G416. Boot kernel collection copied out (67600384 bytes, sha256 6d84ddbc500aa570...).
- Its kernel is `xnu-12377.161.15.702.13~1`. The allow-list had 700.19~2 and 701.48~2, so MtkWlanNative declined. Cause confirmed.
- `kcabi/dump.py` on Windows (llvm-objdump 23.1.3 from MSYS2) wrote `abi/native-wifi/25G416`. Against 25G342:
  - instance sizes: all unchanged (sizes.txt identical);
  - vtables: all 50 unchanged; request tables get/set 1..586: 0 IDs differ;
  - missing-functions list identical;
  - functions: 2230 identical, 94 changed. 58 differ in addresses or order only. 36 differ in one immediate that moves by a constant per source file (+6 in IO80211InfraInterface, +13 in IO80211VirtualInterface): log line numbers. One real change: `IO80211InfraInterface::updateCountryCodeProperty` now calls `IO80211_io80211isSensitiveInfoAllowed`. The 25G342 function dumps came from the Mac's data volume.
  - `linkcheck.py` with the installed 0.4.15 binary against the 25G416 collection: ok.
- Change on OCEFI: `MtkWlanNative.kext/Contents/Info.plist` gained a 25G416 entry (same Sizes as 25G332, the new xnu tag). Binary untouched (sha256 58be03d84c5f...). Old kext kept as `MtkWlanNative.kext.0.4.15.bak`. Same entry in `native/drivers/MtkWlanNative/Info.plist`.
- Undo: copy `Info.plist` back from the `.bak` folder.
- Not booted yet. After the boot: `ioreg -r -c MtkWlan -l -w0 | grep -E 'MtkFrontEnd|MtkNativeAbi'`, Wi-Fi menu, lease on en1. Then regenerate headers (`refresh.py`), release as 0.4.16 with 25G416 allow-listed, README builds line, rsync to the stick.
