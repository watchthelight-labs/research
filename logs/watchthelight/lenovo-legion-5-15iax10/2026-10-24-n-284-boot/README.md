<!-- <wtl> project: legion-hackintosh | file: evidence/native/N-284/README.md | author: watchthelight </wtl> -->
# N-284 (2026-10-24 09:53 EDT): ws=1 with XeGfx 0.0.39 userptr-hold logs (Bash's go)

Result: **fail**, same death as N-283 (WindowServer 1969 died in the wait; 29 IOPresentment transactions on head 4,
0 fail, Metal compositor), but the new log names the cause (`guard/ws-xegfx-log.txt`):

    xegfx: userptr hold: prepare 0x2 for 0x10298b000 + 5 pages (pid 1969)
    xegfx: ioctl 0x80406469 (nr 0x69) inst 823 pid 1969 -> errno 14

One line pair per WindowServer pid. 0x2 is KERN_PROTECTION_FAILURE: wiring a 5-page (20 KiB) user range for writing
fails because the range is mapped read-only. The plugin imports buffers as host pointers (VK_EXT_external_memory_host
-> i915 userptr, held writable), so a Metal buffer made over read-only memory (constant data or a mapped file,
newBufferWithBytesNoCopy) fails at the next execbuffer with EFAULT and ANV loses the device. Linux i915 refuses the
same case (pin_user_pages with FOLL_WRITE on a read-only VMA). Wiring read-only in the shim would let GPU writes reach
shared copy-on-write pages, so the fix is in the plugin.

Fix (NvGfx-xe e60f462, installed, not booted): nvmtl_vk_buffer_import_host checks with mach_vm_region that the whole
range is writable and otherwise returns -1, so the buffer is copied.

Also: XeGfxIntelFB 0.3's guard never cleared (WindowServer's connection does not pass the 4-argument newUserClient);
0.4 clears it 120 s after start. Counter cleared by hand. XeGfxBlock back on (config.n284-post.plist.bak).
