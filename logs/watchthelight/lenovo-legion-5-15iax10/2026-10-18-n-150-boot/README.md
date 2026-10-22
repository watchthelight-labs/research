# Upstream PR branches from the fork (prepared 2026-10-18, NullMoth main = 2.3.6, commit 6372823)

Branches in `~/src/upstream-nmd`, one fork commit each, rebased onto 2.3.6 (all applied without conflicts; each
branch's code change is identical to its fork commit, checked by diffing the diffs), squashed, authored watchthelight,
plugin built with upstream's release line (0 errors, minos 15.0):

| branch | commit | fork commit | status |
|---|---|---|---|
| submit-ahead-commit | 071110c | 6b998bb | OPENED by Bash as nullmoth/nvidia-macos-driver PR 289 (2026-10-18, +16 -3, one file); measured alone on N-134 (35/45 -> 63/64 flips per second) |
| function-memo | 5209966 | b3d34ec | not clean yet: only measured together with fetch-set-per-pass on N-135, where drag was lower than N-134 and a plain CA animation dropped too (cause not isolated) |
| fetch-set-per-pass | 1932f21 | ee917a4 | same as above; the candidate for the N-135 regression (the plan was to revert it in a .6 build) |

The drafts carry exactly the three template headings and say what was measured, including the N-135 result; the
attestation line is not in them. Before sending the second and third, build each alone on 2.3.6, boot, and repeat the
drag measurement (`evidence/native/N-134/drag2.swift`, `caanim.swift`, `run.sh`) on a quiet desktop.

To open one (pushes to github.com/watchthelight/nvidia-macos-driver and opens the PR against nullmoth:main):

    nullpr submit-ahead-commit "NVMTLDriver: run the submit-ahead pass at commit while the worker waits" evidence/native/N-150/upstream-port/PR-submit-ahead-commit.md
    nullpr function-memo "NVMTLDriver: keep the per-module work of newFunctionWithName across libraries" evidence/native/N-150/upstream-port/PR-function-memo.md
    nullpr fetch-set-per-pass "NVMTLDriver: one framebuffer fetch descriptor set per pass and mask" evidence/native/N-150/upstream-port/PR-fetch-set-per-pass.md

Note on 2.3.6 itself: the other session's plan (`~/.claude/plans/frolicking-chasing-corbato.md`) says 2.3.6 loses the
System Settings icons on other machines because the plugin no longer defers a visible-function refusal; our installed
plugin is still 2.3.5-nvgfx.5, so these branches have not been booted on 2.3.6 here.
