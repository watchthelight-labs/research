<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-216/README.md | author: watchthelight </wtl> -->
# N-216: XeGfx 0.0.4, first real i915 probe of the 7D67 (staged 2026-10-21 11:15 EDT), BIOS Hybrid

Change since N-215: stage 3 now scans every IOPCIDevice into newbus (config reads only) and claims the Intel display
function for vgapci, so stage 4's i915 driver gets the device. xe-guard queue: N-216a (stages 1-3, check the tree),
N-216b (stage 4: i915 probe with display disabled, GuC firmware from Resources, display check; wdog 180 s;
reboot_on_fail to restore the panel).

## Result (2026-10-21 11:18 EDT): FREEZE after stage 3 (Bash: "Laptop froze", powered off)
- Stages 1-3 passed (11:14:50-11:14:57). The stage 3 tree is complete this time: pci0 with every function,
  `vgapci0` attached to 8086:7D67, `drmn0` waiting (evidence `xe-guard/N-216a/xegfx-log.txt`).
- The persisted log stops at 11:15:04.289, 7 s after stage 3, during the guard's 30 s settle; N-216b (i915) never
  started. No panic report: a hard hang, so the stall watchdog could not fire (and the TCO watchdog is locked).
- The scan and claim do no BAR sizing writes and no config writes. Suspect (inference, I-099): for every device
  `xg_pci_xnu_intx_index()` walks `IOPCIDevice::getInterruptType()`, and resolving message-signalled interrupts on
  devices other drivers own (NVMe, xHCI, MT7925) can reconfigure them.
- The guard held the rest of the queue (queue.jsonl.held), as designed.
- Fix: XeGfx 0.0.5 scans only bus 0's display function, host bridge and ISA bridge, and resolves interrupts only for
  the GPU (`xegfx.pci_scan_all=1` restores the full scan for a later A/B).
