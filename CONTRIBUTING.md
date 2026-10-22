<!-- <wtl> project: research | file: CONTRIBUTING.md | author: watchthelight </wtl> -->
# Contributing

## Logs

Use the **Submit logs** issue form, or attach the logs to an issue in the project repo they're about. By sending
logs you agree that they're published here, redacted, under CC BY 4.0, filed under your GitHub username and a
name for your machine.

You don't need to redact anything yourself, but you can. If you'd rather a log stays private, say so in the issue
and it won't be copied here.

Things that help:
- the machine (vendor and model, or board for a desktop), CPU, GPU, Wi-Fi/Bluetooth card
- macOS version and build (`sw_vers`), OpenCore version, the kext versions
- what you did and what happened, in a sentence or two
- text, not screenshots, where you can

## Corrections

If a log or a write-up is wrong, or something identifying slipped through, open an issue. For anything
identifying, describe where it is without pasting it.

## Code

`tools/` is plain Python 3.9+ with no dependencies. Run `python tests/test_redact.py` and
`python tools/privacy_check.py` before a pull request; CI runs the second one on every push.
