<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-214/README.md | author: watchthelight </wtl> -->
# N-214: XeGfx 0.0.2 armed by the xe-guard (staged 2026-10-21 09:10 EDT), BIOS Hybrid

## Changes since N-213
- XeGfx 0.0.2 (NvGfx branch `xe`, GPL-clean overlay build) in the aux collection. Nothing loads it at boot: its one
  personality waits for `XeGfxArm`, which `_start` publishes after `kmutil load`. I-094 fix: FreeBSD copies of 44
  kernel-exported names renamed; link and shadow checks pass against macOS 11, 12, 13, 14, 15 and 26 collections.
- xe-guard installed (LaunchDaemon org.watchthelight.xe-guard), first real run.
- OCEFI: XeGfxBlock entry removed (backup config.n214-pre.plist.bak; kext moved to EFI/OC/Kexts-off); make_config
  mirrored.

## Queue (judged by the xe-guard, no Good needed)
| Entry | Stages | Settings |
|---|---|---|
| N-214a | 1-2 (shim, read-only probe incl. TCO watchdog registers) | wdog 60 s |
| N-214b | 3 (newbus over every PCI device, DMA) | wdog 120 s |
| N-214c | 4 (drm + i915 with display disabled, then the GGTT/pipe display check) | wdog 180 s, reboot_on_fail |

Expected: a normal boot (XeGfx not loaded until the guard runs), then results in
/Users/Shared/legion-diag/xe-guard/results/N-214*.json and evidence/ there.

## Result (checked live 2026-10-21 11:05 EDT): XeGfx loads and runs stages 1-4 without harm; i915 did not bind (PARTIAL)

### The boot itself
- The N-214 restart at 09:05 reached OpenCore (13:05:50 UTC) and **stopped at the picker for 100 minutes**:
  `Should boot from 0. OCEFI` then `Showing menu... (polling hotkeys)`. At 6030 s someone chose Windows. The Mac came
  back through OpenCore at 14:54:20 UTC, picker again, Tahoe chosen after 60 s. Cause, new issue I-098: since
  ~09:44 UTC a firmware entry `Boot0004` (`HD(5,...)/\EFI\OC\OpenCore.efi`, OCEFI by short path) is first in BootOrder,
  so OpenCore's default is itself; with Timeout 0 the picker waits forever. Every boot since 09:44 UTC shows it
  (opencore-*.txt from 094453 on). Fixing it means editing firmware boot entries: Bash's OK needed.
- So this 10:55 boot is the N-214 boot (aux collection with XeGfx 0.0.2, xe-guard installed).

### XeGfx (xe-guard verdicts, evidence in xe-guard/)
- **Loaded by kmutil without incident: I-094 is fixed** (first time XeGfx ran on this machine).
- Stage 1 (shim) passed. The guard crashed parsing `sysctl -x` output ("Format:S Length:20 Dump:0x..."), fixed and
  restarted by hand, so N-214a has no verdict file; N-214b covers stages 2-3.
- N-214b: stages 2 and 3 pass, WindowServer stable 60 s.
- N-214c: stage 4 "pass", WindowServer stable 120 s, display check passed (GGTT entry behind the panel unchanged
  0x800003, pipe A +17 frames in 100 ms). **But i915 never bound the GPU**: the console ring has only the stolen
  memory quirk line and "ran 56 sysinit_set entries", no i915 probe output, no /dev/dri node. The 0.0.3 build fails
  stage 4 with ENODEV in that case and dumps the newbus tree.

### Probe (XeGfxProbe, read-only)
| Field | Value | Meaning |
|---|---|---|
| device-id / revision | 0x7D67 / 0x06 | ARL-S |
| gmd-id-graphics | 0x03118004 | IP 12.70 |
| gmd-id-display | 0x0380000C | display 14.0 |
| bar0 | 0x6018000000, 16 MiB | GTTMMADR (GGTT at +8 MiB) |
| bar2 | 0x6000000000, 256 MiB | aperture |
| dsm-base | 0x70800000 | the GOP framebuffer's stolen memory |
| ggc | 0x04C0 | |
| pcode-stolen-access | 1 | **Wa_22018444074 applies**: no CPU access to stolen memory through a BAR |
| plane-surf-1-a / GGTT PTE | 0xFF000000 / 0x800003 | GOP surface mapped by GGTT to 0x800000 |
| tco-base / tco1-cnt | 0x8E00 / 0x1800 | **TCO_LOCK set, timer halted: no hardware watchdog** |
