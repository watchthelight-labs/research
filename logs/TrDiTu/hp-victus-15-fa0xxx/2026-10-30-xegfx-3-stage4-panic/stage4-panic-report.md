Hi @watchthelight , I saw the issue that you left on my repository about my hackintosh project and I wanna provide my info that I got when try to run your project:

I actually tried to run Stage 4 (sysctl debug.xegfx_stage=4), a kernel panic occurs due to a page fault (Type 14, `CR2: 0x0000000000000000`) inside `_xg_vsnprintf + 0x45`.
Stages 1, 2, and 3 all passed cleanly on this Alder Lake-P platform. The panic trace indicates that `_intel_detect_pch()` invokes LinuxKPI's `_lkpi_pci_get_class()` to probe the LPC/ISA bridge (`PCI_CLASS_BRIDGE_ISA`), which attempts to register a kobject with a `NULL` format string, causing an unguarded dereference in string formatting / `xg_has_pext`.

### System Environment
- **Target OS:** macOS 26 Tahoe (Darwin 25.6.0, Build `25G241`, x86_64)
- **XeGfx Version:** `v0.0.38` (Commit `78db6fceab4a6d50c3072c12e5ea89688f281d26`)
- **Device Model:** HP Victus 15-fa0xxx (Motherboard: HP `8A4F`)
- **CPU:** Intel Core i7-12650H (Alder Lake-H/P, 6P + 4E, 16 threads, Family 6 Model 154 Stepping 3)
- **Host Bridge:** `8086:4649`
- **iGPU:** Intel UHD / Iris Xe Graphics Alder Lake-P GT1 (`8086:46A3`, Rev `0x0C`, 64 EUs)
- **PCH Chipset:** Intel Alder Lake PCH-P LPC/ISA Bridge (`8086:5182`)
- **Discrete GPU:** NVIDIA GeForce RTX 3050 Ti Mobile (Completely powered down via ACPI `_OFF()`)
- **Boot Arguments:** `-v debug=0x100 keepsyms=1 -lilubetaall amfi_get_out_of_my_way=0x1 -vi2c-force-polling -wegnoegpu alcid=11`
- **SIP / Security:** SIP disabled (`csr-active-config = 0x0FEF`), `SecureBootModel = Disabled`, XeGfx loaded dynamically into AuxKC (not injected via OpenCore).

---

### Preceding Stage Results (All Passed)
1. **Stage 1 (Shim state & Vmap test):**
   - Result: `debug.xegfx_results = 0x00000001` (PASS)
   - `xegfx: vm: vmap selftest 0` succeeded without `-12` error.
2. **Stage 2 (Read-only GPU Probe):**
   - Result: `debug.xegfx_results = [Stage 1: 1, Stage 2: 1]` (PASS)
   - `XeGfxProbe` dictionary successfully populated in IORegistry:
     - `device-id = 0x9A49` (Tiger Lake spoof) / Physical hardware `8086:46A3`
     - `revision = 0x0C`, `bar0 = 16 MiB`, `bar2 = 256 MiB`
     - `pipe-a-lit = 1`, `boot-fb-size = 8294400` (1080p 32-bit eDP).
3. **Stage 3 (Newbus & DMA layer):**
   - Result: `debug.xegfx_results = [Stage 1: 1, Stage 2: 1, Stage 3: 1]` (PASS)
   - Device tree resolved: `hostb0 (8086:4649)` -> `vgapci0 (8086:9a49)` -> `drmn0`
   - Stolen memory: `base = 0x7c800000`, `size = 60 MiB`, DMA physical mapping active.

---

### Steps to Reproduce
1. Install and load `XeGfx.kext` into AuxKC via `sudo kmutil load -b org.watchthelight.XeGfx`.
2. Successfully execute Stages 1, 2, and 3:
   ```bash
   sudo sysctl debug.xegfx_stage=1
   sudo sysctl debug.xegfx_stage=2
   sudo sysctl debug.xegfx_stage=3
3. Trigger Stage 4:
sudo sysctl debug.xegfx_stage=4

---

Actual Behavior (Kernel Panic)

The system immediately panics with a page fault at CR2: 0x0000000000000000.

Panic Header & Registers:

panic(cpu 0 caller 0xffffff80184d528a): Kernel trap at 0xffffff7faeffcad5, type = 14=page fault, registers:
CR0: 0x000000008001003b, CR2: 0x0000000000000000, CR3: 0x0000000560b2e105, CR4: 0x00000000003626e0
RAX: 0xffffffb984b78910, RBX: 0x0000000000000000, RCX: 0xffffffb984b788b0, RDX: 0x0000000000000000
RSP: 0xffffffb984b78870, RBP: 0xffffffb984b78890, RSI: 0x0000000000000000, RDI: 0xffffffb984b788af
R8:  0xffffffb984b78a00, R9:  0xffffff9e4d4aea60, R10: 0x0000000000000000, R11: 0x0000000000000200
R12: 0xffffffb984b789c0, R13: 0xffffff7faf1405b8, R14: 0x0000000000000000, R15: 0xffffffa98102cf10
RFL: 0x0000000000010282, RIP: 0xffffff7faeffcad5, CS:  0x0000000000000008, SS:  0x0000000000000010
Fault CR2: 0x0000000000000000, Error code: 0x0000000000000000, Fault CPU: 0x0
Panicked task: pid 863: sysctl

Backtrace:

org.watchthelight.XeGfx : _xg_vsnprintf + 0x45
org.watchthelight.XeGfx : _kobject_set_name_vargs + 0x8a
org.watchthelight.XeGfx : _kobject_init_and_add + 0xc7
org.watchthelight.XeGfx : _lkpi_pci_dev_init_common + 0x3f
org.watchthelight.XeGfx : _lkpi_pci_get_class + 0x5f
org.watchthelight.XeGfx : _intel_detect_pch + 0x63
org.watchthelight.XeGfx : _i915_driver_probe + 0x56d
org.watchthelight.XeGfx : _linux_pci_attach_device + 0x50b
org.watchthelight.XeGfx : _device_attach + 0x5a
org.watchthelight.XeGfx : _bus_generic_driver_added + 0x3d
org.watchthelight.XeGfx : _xg_pci_driver_added + 0x35
org.watchthelight.XeGfx : _devclass_add_driver + 0xa9
org.watchthelight.XeGfx : _lkpi_pci_register_driver + 0xc5
org.watchthelight.XeGfx : _i915kms_evh + 0x2dc
org.watchthelight.XeGfx : _module_register_init + 0xa9
org.watchthelight.XeGfx : _xg_run_set + 0x22a
org.watchthelight.XeGfx : _xg_start_stage + 0x46
org.watchthelight.XeGfx : __ZL18xegfx_stage_sysctlP10sysctl_oidPviP10sysctl_req + 0x4f7

---

Root Cause Analysis

1. During _i915_driver_probe, the driver executes intel_detect_pch() to identify the platform's PCH (8086:5182 Alder Lake PCH-P) via pci_get_class(PCI_CLASS_BRIDGE_ISA << 8, ...).
2. LinuxKPI finds the device and calls _lkpi_pci_dev_init_common(), which calls kobject_init_and_add() -> kobject_set_name_vargs().
3. The format string pointer passed into _xg_vsnprintf is NULL (RDX = 0x0000000000000000).
4. In shim/src/xnu/xg_kext.cpp (or corresponding string helper), xg_has_pext(fmt) iterates through characters via for (; *f; f++) without an initial guard if (!f) return false; (or checking for nullptr), causing an immediate NULL pointer dereference.

