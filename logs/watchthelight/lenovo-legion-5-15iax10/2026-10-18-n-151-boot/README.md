# N-151: NullMoth 2.3.6 + fork (2.3.6-nvgfx.1, without the icon fix): reproduce the lost icons

Installed 10:58 with the package's own installer; backup of 2.3.5-nvgfx.5 at
/Library/NullMoth/backup-20261018-105811.Ftg42a (undo: `sudo ./uninstall.sh <that folder>` from the package). Icon
caches cleared (iconservices store, iconservicesagent cache folder, Dock icon cache). Plugin b2532948c96d is the fork
build at 80e6f53 (the NVGFX-VERSION file says 879f9fe because package.sh records the branch head; the plugin binary
predates the fix). Kexts: NVRM (fork glue on 2.3.6), NVRMFB and NVAccel 15/26 from the fork build. Wi-Fi set
unchanged (native, N-150). `icons/fcprobe.txt` is the offline proof. Expected on this boot: System Settings icons as
empty squares, iconservicesagent log "called on a live path but no linked function supplies it" and no "DEFERRED to
pipeline creation" line. Then N-152 = 2.3.6-nvgfx.2 (plugin 879f9fe) for the fix.

## Result (11:10)

Booted, Metal active (system_profiler: Legion 5 panel on the RTX 5070, 165 Hz), power limit 115 W (nvgfx-smi). The
icon bug did NOT reproduce: System Settings General and the sidebar, the Dock, all icons drawn (`settings-general-2.png`).
What failed instead: the panel stopped updating for Bash ("i cannot see you, the driver isn't loaded right") while
`screencapture` still returned a correct composite; during an 8 s Finder drag `debug.nvaccel_iop_flips` and
`nvaccel_iop_ok` stayed at 0 and no `debug.*flip*/present*` counter moved (`sysctl-before-drag.txt`,
`sysctl-after-drag.txt`). 2.3.6 moved presentation ("Open the flip path as soon as the display is armed", cursor
thread in NVRMFB); our fork's NVRMFB/NVAccel build on top of it, or the kext mix, left the flip path dead. Rolled
back: `uninstall.sh <backup>` removed the driver rather than restoring, so 2.3.5-nvgfx.5 was reinstalled from its
package (backup of the 2.3.6 set: /Library/NullMoth/backup-20261018-110700.ZDN2w7); reboot N-152 loads it.
