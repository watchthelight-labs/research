# Two upstream PRs, prepared for Bash to open

Prepared on 2026-10-17 by Claude Code at Bash's request. The two branches live in ~/src/upstream-nmd on top of
nullmoth/nvidia-macos-driver main (8b120f3, v2.3.5), one commit each, authored as watchthelight:

| branch | commit | what |
|---|---|---|
| `fetch-off-zero-reads` | NVMTLDriver: give fetch-off [[color(n)]] reads a zeroed image | plugin only |
| `a8-render-targets` | NVMTLDriver: A8Unorm render targets take alpha in the red lane | plugin + translator |

The draft descriptions are in PR-fetch-off-zero-reads.md and PR-a8-render-targets.md. Both follow the template's three
headings. The code and the drafts were written by Claude Code from the fork's commits and this project's test results.
Upstream's CONTRIBUTING.md says AI-written PRs are closed without review and the template has a checkbox "I wrote this
change and this description myself (not an AI tool)". That checkbox is left unticked in the drafts; whether to open the
PRs, and what to declare, is Bash's decision. Every claim in "How I tested it" is backed by a tracker row or an evidence
folder in this repo (N-96, N-109, N-112 to N-116, a8rt output in evidence/native/N-112/check.txt).

## Opening them

There is no fork of nullmoth/nvidia-macos-driver under watchthelight or watchthelight-labs yet (a new public repo, so
not created by the assistant). From a terminal, as Bash:

    export PATH=$HOME/.local/bin:$PATH
    gh repo fork nullmoth/nvidia-macos-driver --clone=false            # creates github.com/watchthelight/nvidia-macos-driver
    cd ~/src/upstream-nmd
    git remote add fork https://github.com/watchthelight/nvidia-macos-driver.git
    git push -u fork fetch-off-zero-reads a8-render-targets
    gh pr create --repo nullmoth/nvidia-macos-driver --base main --head watchthelight:fetch-off-zero-reads \
        --title "NVMTLDriver: give fetch-off [[color(n)]] reads a zeroed image" --body-file PR-fetch-off-zero-reads.md
    gh pr create --repo nullmoth/nvidia-macos-driver --base main --head watchthelight:a8-render-targets \
        --title "NVMTLDriver: A8Unorm render targets take alpha in the red lane" --body-file PR-a8-render-targets.md

or push and use the "Compare & pull request" button on GitHub and paste the text under "Draft description". Trim the
header lines (branch, files, patch) from the body before posting; they are for you.

## mip-autofill (2026-10-17)

Branch `mip-autofill` in `~/src/upstream-nmd`, commit e563f14 on top of upstream main 8b120f3: two files, 46 lines
(`plugin/NVMTLObjects.h`, `plugin/NVMTLObjects.m`). Built with upstream's `build_plugin_release.sh` line, minos 15.0,
no errors. Draft body: `PR-mip-autofill.md` (lint 0 hard, 0 soft). Patch: `0001-mip-autofill.patch`.

To open it after editing the draft:

    nullpr mip-autofill "Dock badges show their numbers again" evidence/native/N-111/upstream-port/PR-mip-autofill.md
