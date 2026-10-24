<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-274/README.md | author: watchthelight </wtl> -->
# N-274: Ubuntu probe stick first boot on the Legion, Linux 7.0 i915 reference for XeGfx (2026-10-24)

Session: Claude Code on the probe stick itself (Ubuntu 26.04, kernel 7.0.0-38, tty1). Issues: I-112 (fixed here),
I-111 (Linux control). Task H152 (M0 reference capture). N-273 was queued for XeGfx on 2026-10-23 and dropped unbooted,
so this boot is N-274 (N-273 stays retired).

## Boot (OpenCore logs in `oc-logs/`, redacted)
| OC log (UTC) | Picker | Result |
|---|---|---|
| 00:07:54 | 1. Tahoe, 5 s after "Showing menu" (timeout default) | macOS to `EXITBS:START` 00:08:02, next OC start 23 s later |
| 00:08:25 | 3. Ubuntu probe | LegionProbeBoot ran, log ends (warm reset), firmware came back to OpenCore |
| 00:09:07 | 3. Ubuntu probe | LegionProbeBoot, firmware `Boot0F0E`, systemd-boot, `legion-probe` UKI, tty1 autologin |

- `efibootmgr`: `BootCurrent: 0F0E` ("Legion probe stick (Ubuntu)"). I-112 is fixed on hardware.
- Open: the first LegionProbeBoot pick returned to the picker; the second worked. Same pattern on 2026-10-23 21:30 (pick,
  then 21:33 picker again, Windows chosen). Watch on the next probe boot; not an issue row yet.
- Open: what ended the 00:08 Tahoe boot after 23 s (most likely Bash restarting after the picker timeout). The Mac
  session checks `/Library/Logs/DiagnosticReports` for a panic near 2026-10-24 00:08 UTC. APFS is not read from the stick.

## Hardware state under Linux 7.0 i915 (`xe-live/`, after the rebind; `xe-boot-state/`, before it)
| Item | N-274 (Linux 7.0.0-38) | N-191 (Linux 6.18.56) |
|---|---|---|
| GMD_ID graphics / media / display | 0x03118004 / 0x03400008 / 0x0380000c | 12.70 / 13.00 / 14.00 |
| MTL_PCODE_STOLEN_ACCESS | 1 | 1 |
| DSM / GSM base | 0x70800000 / 0x70000000 | same |
| DMC | mtl_dmc.bin v2.23 | v2.23 |
| GuC (GT0 and GT1) | mtl_guc_70.bin 70.53.0, submission + SLPC + RC | 70.53.0 |
| HuC | mtl_huc_gsc.bin 8.5.4, authenticated for all workloads | 8.5.4 |
| GSC | mtl_gsc_1.bin 102.1.15.1926 | same |
| eDP | 2560x1600 165 Hz, HBR3 (810000) x4, PSR1 on (SRDONACK) | 165 Hz, PSR1 |
| dmesg | "PHY A failed to request refclk" at boot | same line |

- Panel EDID: EDO EF10QBC64.C, made week 25 of 2024 (serial fields zeroed in the copy).
- **DPCD, first capture** (`xe-live/dpcd-drm_dp_aux0-*.bin`, AUX A): DPCD 1.4, max rate HBR3 x4, eDP rev 0x05,
  SUPPORTED_LINK_RATES 1.62/2.16/2.43/2.7/3.24/4.32/5.4/8.1 Gbps, PSR support 0x03 (the sink offers PSR2; i915 picks
  PSR1). Linux 7.0 has no `i915_dpcd` debugfs file any more; the dump comes from `/dev/drm_dp_aux0`.
- `xe-live/debugfs/i915_wa_registers.txt`: the engine workaround lists Linux 7.0 applies (rcs0 7, bcs0 2, vcs0/vcs1/
  vecs0/ccs0 1 each), to compare against XeGfx.
- `xe-live/intel_reg-dump.txt` and `gpu/intel_reg.txt`: first `intel_reg dump` on this machine. `xe-live/acpi/`:
  ACPI tables with iasl disassembly. `xe-live/vbt-decode.txt`: VBT decode.
- FRMCOUNT on pipe A advances about 117/s with PSR1 in self refresh, not 165/s: expected with PSR, not a fault.

## i915 full init register trace (`i915-trace/`)
`native/tools/probe-stick/i915-rebind-trace.sh`: unbind i915 from 00:02.0, rebind with `i915:i915_reg_rw` on, then
one 2560x1600@165 modeset with modetest. 89,870 traced accesses, 0 overruns, clean re-probe in `dmesg-delta.txt`.
`reg-trace-summary.py` wrote `regs-<phase>.csv` (t_us, rw, offset, value, name, block) and `summary.md`:
- unbind: 802 accesses, 219 registers, 0.9 s.
- bind: 66,500 accesses, 13,244 registers, 12.8 s; 11,516 writes are the DMC program upload (0x80000-0x84FFF and the
  per-pipe pages at 0x90000+), most reads are vblank/scanline polling on the pipe registers.
- modeset: 17,158 accesses, 79 registers, 5.6 s.
The tracepoint only covers i915's traced accessors (not raw `_fw` reads), so it is the driver's own logged sequence,
not a full mmiotrace. The full raw trace is `trace.txt.xz`.

## I-111 Linux control: userptr import and teardown (`vkhost-linux/`)
`native/tools/probe-stick/vkhost-linux.c` follows vkhost on ANV: mmap 4 MiB, import with
`VK_EXT_external_memory_host` (an i915 userptr object), `vkCmdFillBuffer` 1M dwords, CPU check.
| Variant | Runs | Wrong | Import avg | Submit+wait avg |
|---|---|---|---|---|
| free (buffer, memory, munmap) | 500 | 0 | 0.004 ms | 1.047 ms |
| unmap (munmap first, object live) | 500 | 0 | 0.003 ms | 1.063 ms |
| exit (child exits with everything live) | 500 | 0 | 0.046 ms | 1.975 ms |
| par (8 children at once, exit) | 496 | 0 | 0.057 ms | 2.119 ms |

- No hang, GPU reset, RCU stall or lockup in `dmesg-delta.txt` (only a nouveau HDA line).
- XeGfx on macOS in N-271: import 0.02 ms, submit+wait 1.79 ms. Linux is in the same range.
- `i915_gem_object_destroy` by context (`userptr-timing.txt`): the kworker free worker releases nearly every object
  in every order (free 4093 of 4111, exit 55,807 of 59,500). Deferred release after the owning process is gone is the
  normal i915 path and is safe on this hardware. Userptr objects do not fire `i915_gem_object_create`, so per-object
  userptr lifetimes are not in this trace.
- Readout for I-111: the hardware, GuC 70.53.0 and the i915 design survive this pattern. The lead stays in the port:
  Linux holds a reference on the process mm in the userptr object until release; check that XeGfx keeps the task's
  vm_map (and the pages' IOMemoryDescriptor) alive until its free worker runs, rather than touching a map torn down at
  task exit. Upstream-ready note: none yet (port-side).

## Source delta
`../intel-xe/linux-6.14-to-7.0-i915-delta.md`: i915 commits between the port's base (drm-kmod c16de0f, Linux 6.14
level) and Linux 7.0 that may matter for I-111, I-109, I-108 and the eDP path.

## Redaction
Captures were copied with `scripts/diag/redact-linux.py`: serials, UUIDs, PCIe DSNs, USB iSerial and MAC addresses
read REDACTED; EDID serial bytes zeroed. dmidecode output is only in `private/probe-stick/2026-10-24/` (gitignored).
OC logs went through `scripts/diag/redact-oclog.py` (ROM, MLB, SSN read REDACTED; the NVMe EUI in device paths is
in the OC logs since N-01).
