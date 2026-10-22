<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-193/README.md | author: watchthelight </wtl> -->
# N-193: NMIntelFB 0.1 in Hybrid with -nvoff (I-090), read from Windows

Read on 2026-10-20 from Windows, read-only: OCEFI OpenCore log, the Tahoe Data volume (`scripts/diag/apfs-read.py`), the Tahoe unified log store. Times UTC.

## Boot
- OpenCore log `opencore-2026-10-20-224453.txt`: `Current FB at 0x70800000` (Intel GOP, so the BIOS was in Hybrid), `Should boot from 0. Tahoe`. Boot-args ended in `-nvoff` (NVIDIA driver off); NMIntelFB 0.1 was in the AuxKC (staged by the Mac session, note 86e37f8a).
- Claude web photo ~22:55 UTC (note 9d531e3a): verbose text only. Key lines: `NMIntelFB: 8086:7d67 display version 14`, `NMIntelFB: pipe A: surface at GGTT 0xff000000 lies past the 256 MiB BAR2 window` (informational in e582a7a), then other subsystems (VoodooHDA, DriverKit HID, MtkBt, MtkWlanNative scans). The photo transcription has no later NMIntelFB line (`pipe A: WxH ... Hz`, `scanout: console ...`, `built-in panel published` or a "leaving the firmware screen" decline).

## The machine stopped writing early
- bootdump folder `20261020-224458Z` holds only `00-info.txt` (written 22:45:03); its 20 s dump (dmesg, ioreg, sysctl) never appeared.
- The unified log store has no entry from this boot: the newest Persist/Special files (`00000000000001b5`, `00000000000001c5`) end at 22:44:09, the previous boot.
- So the system most likely stopped making progress (a hang, or at least stalled I/O) within about 20 s of the logger starting, with the console frozen on its last text. Bash's "Is it hung here now?" fits.

## Reading (Medium-Low until reproduced with more logging)
In `NMIntelFB::adoptFirmwareMode()` the BAR2 line is printed right after the PLANE_* reads; the next log line follows the HTOTAL/VTOTAL/HSYNC/VSYNC reads, two FRMCOUNT reads and `IOSleep(250)`. Its absence suggests the start thread stalled there or in the steps right after it (console info, the write-combined mapping of the console range at 0x70800000, which is the DSM base). Not proven: the photo may simply not show the line.

## N-194 (applied on OCEFI from Windows)
`-nvoff` removed again (backup `EFI/OC/config.n194-pre.plist.bak`). With the BIOS back on Discrete this is a normal NVIDIA boot (NMIntelFB has no Intel GPU to match there). The NMIntelFB NVRAM guard counted one strike for N-193.

For the next NMIntelFB attempt: log every step of `start()` (each register read group, the console info, the mapping) with IOLog and a boot-arg to stop before publishing, so a hang points at one step.
