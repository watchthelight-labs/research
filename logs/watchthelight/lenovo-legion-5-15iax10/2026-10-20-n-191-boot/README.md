<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-191/README.md | author: watchthelight </wtl> -->
# N-191: 1401 Probe in BIOS Hybrid mode, then the Legion Xe capture (2026-10-20)

Plan `docs/plans/intel-xe.md`, task H152 (M0). The machine was in BIOS Hybrid mode (panel on the iGPU).

1. **Full scan** (17:40, release entry): report saved, all stages ok (`probe-summary-20261020-2140.txt`; the full zip
   with dmidecode is kept out of git in `private/probe1401/`). The probe then went on to its NVIDIA trace stage and a
   kworker oopsed at about 110 s in `pci_pm_runtime_suspend -> vmap_range_noflush` with nvidia and nouveau both
   loaded (screen photo, Claude web note 2367cc65). `probe-step.txt` records the step it will skip next time.
2. **Capture rerun** (18:29, added entry "Legion Xe capture shell", NVIDIA drivers blacklisted, `pcie_port_pm=off`):
   `native/tools/intel-xe/xe-capture.sh` ran to DONE after the stick was made writable by hand (the debug shell
   locks it read-only too). Step 4 lost most i915 debugfs files to a `:` in the folder name (FAT); the eDP connector
   files survived. Redacted copy: `xe-capture-20261020-222936/` (USB and PCI serials and nothing else changed).
   Script fixed afterwards: it clears the lock on the stick itself, uses `-` for `:`, powers off at the end.

## What it measured (firmware state, before any Intel driver)

| Item | Value | Reading |
|---|---|---|
| GMD_ID graphics | 0x03118004 | IP 12.70 rev 4: Xe-LPG (not the 12.71 / 12.74 variants) |
| GMD_ID media / display | 0x03400008 / 0x0380000c | media 13.00, display 14.00 (Xe-LPD+) |
| MTL_PCODE_STOLEN_ACCESS 0x138914 | 1 | firmware relaxed stolen access: direct DSM/GSM access is allowed (i915 Wa_22018444074 path) |
| GEN6_DSMBASE / GEN6_GSMBASE | 0x70800000 / 0x70000000 | the Hybrid GOP framebuffer (0x70800000) is the start of stolen memory; the GGTT sits 8 MiB below |
| Plane A | CTL 0x84000008 (on, XRGB8888, linear), 2560x1600, stride 160 x 64 = 10240 B, SURF 0xFF000000 | linear 32-bit, what NMIntelFB adopts; the GGTT offset lies far past the 256 MiB BAR2 window |
| Pipe A | HTOTAL 2720 / VTOTAL 1744, frame counter 165 per s | firmware lit the panel at 165 Hz (pixel clock 782.7 MHz, matches the EDID's DisplayID timing) |
| Panel power, backlight | PP_STATUS on; PCH PWM registers 0; Linux `intel_backlight` raw, max 504 | backlight is not on the PCH PWM (DPCD/AUX expected; VBT not captured) |
| eDP sink | PSR1 supported and enabled by i915, Panel Replay no; panel power-up delay 200 ms | |

## What i915 did (Linux 6.18.56, after `modprobe i915`, 2 s)

DMC `mtl_dmc.bin` v2.23 loaded; GT0 and GT1 GuC `mtl_guc_70.bin` 70.53.0, submission, SLPC and RC enabled; HuC 8.5.4
authenticated for clear media, then for all workloads after GSC `mtl_gsc_1.bin` r102.1.15.1926 loaded; GSC proxy
failed (no MEI component). Also on this machine: `PHY A failed to request refclk after 1us`, the C10 PHY message seen on
other 7D67 laptops (research `xe#9024`). After the takeover plane A scans out at GGTT 0 and the frame counter ran at
51 per s (PSR).
