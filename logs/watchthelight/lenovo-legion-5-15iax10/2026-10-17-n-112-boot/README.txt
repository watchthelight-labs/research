parity build: upstream v2.3.5 tree (worktree, no fork glue), harness b7824ae+, OGKM 610.57.04, fsp patch on, clang clang-1700.0.13.5
shipped NVRM 2.3.5: 303225b3058a84ee
parity NVRM: 074013d9fe870a52
fork NVRM (power glue): 117a34c539de6b65
functions compared 29432  identical (normalised) 29356  different 76
same class of delta as the 2.1.0 harness result (67 functions then): glue compiled here differs by 1-11 instructions per function, kfsp* differ by the fsp patch (shipped kfspStateDestroy 44 insns, patched 18), nvkms-rm.c / nvkms-kapi.c recompiled by build-completion-archive.py differ by 2-61 instructions; the 1055 RM objects proper are identical.
