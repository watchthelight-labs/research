# N-143: stage E, MtkWlan 0.11.0 + MtkWlanNative 0.4.2, native boot-args, Boingo private address off

Kernel panic 160 s after boot (07:34), machine halted until Bash power-cycled at 07:43; the guard then saw a started
attempt with no result and rolled back to the Ethernet set. `Kernel-2026-10-18-074255.panic`: page fault in
`CCDataPipe::enqueueBlob` called from `CCDataStream::saveData` <- `CCFaultReport::triggerCoreCapture` <-
`CCFaultReporter::completeReport` (a timer on the IOTimerEventSource path). The null pointer is the data pipe's notify
timer (`pipe->priv + 0x38`), which only `CCDataPipe::start` creates; the CoreCapture factories (`withOwnerNameCapacity`,
`withPipeAndName`) alloc and init only, nobody starts a pipe that no catalogue personality matches, and our pipe sat in
the registry as "!registered, !matched". The first fault report the Family completed (something on the join path of
this boot; the boot's log is not persisted) walked into it (I-066). The reference driver (24H32) had the same latent
setup and never completed a fault report.

Fix in 0.4.3: `IOService::start(owner)` on the data pipe, the data stream and the log pipe right after creation (what
IOKit would do for a matched service); traces `ctl:fault pipe start=1`. The guard did not reach its 240 s deadline
because the kernel was halted at 160 s.
