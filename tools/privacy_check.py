#!/usr/bin/env python3
# <wtl> project: research | file: tools/privacy_check.py | author: watchthelight </wtl>
"""Gate before every push: nothing identifying may be in the repo.

  python tools/privacy_check.py [--map <private map.json>]

Without --map (as in CI) it scans every tracked text file for identifier and secret shapes. With the private
map it also looks for every original value the map has ever replaced. Exit 1 on any hit. tests/ holds made-up
values on purpose and is skipped.
"""
import argparse
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from redact import PLACEHOLDER, PUBLIC_VALUES, TOKEN_SHAPE,leftovers, load_map, redact, save_map  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "tests", "__pycache__"}


def files():
    out = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=ROOT,
                         capture_output=True, text=True)
    names = out.stdout.split("\n") if out.returncode == 0 else [str(p.relative_to(ROOT)) for p in ROOT.rglob("*")]
    for n in names:
        p = ROOT / n
        if n and p.is_file() and not (set(Path(n).parts) & SKIP_DIRS):
            yield p


def rescrub(mapping) -> int:
    """Apply the whole map to every log of its machine. A value first seen in a later log was not known yet
    when earlier logs of the same machine were redacted; this closes that gap. Returns files changed."""
    import hashlib
    import json
    import re
    changed = 0
    for meta_p in (ROOT / "logs").glob("*/*/*/meta.json"):
        machine = "/".join(meta_p.parts[-4:-2])
        table = mapping["machines"].get(machine, {})
        pairs = sorted(((v, t) for kind in table.values() for v, t in kind.items()
                        if len(v) >= 4 and not PLACEHOLDER.match(v) and not TOKEN_SHAPE.match(v)), key=lambda p: -len(p[0]))
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        for f in meta_p.parent.iterdir():
            if f.name == "meta.json":
                continue
            text = f.read_text(encoding="utf-8")
            new = redact(text, machine, mapping)[0]   # idempotent: tokens are left as they are
            for value, token in pairs:
                new = re.sub(re.escape(value), token, new, flags=re.I)
            if new != text:
                with open(f, "w", encoding="utf-8", newline="\n") as out:
                    out.write(new)
                meta.setdefault("files", {})[f.name] = hashlib.sha256(new.encode()).hexdigest()
                changed += 1
        with open(meta_p, "w", encoding="utf-8", newline="\n") as out:
            out.write(json.dumps(meta, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
    return changed


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--map")
    ap.add_argument("--fix", action="store_true", help="re-apply the full map to every log first (needs --map)")
    a = ap.parse_args()
    mapping = load_map(a.map) if a.map else None
    if a.fix and mapping:
        print(f"rescrubbed {rescrub(mapping)} file(s)")
        save_map(a.map, mapping)
    values = []
    if mapping:
        values = sorted({v.lower() for m in mapping["machines"].values() for t in m.values() for v in t
                         if len(v) >= 4 and not PLACEHOLDER.match(v) and v.lower() not in PUBLIC_VALUES and not TOKEN_SHAPE.match(v)})
    bad, n = [], 0
    for p in files():
        try:
            text = p.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            bad.append(f"{p.relative_to(ROOT)}: binary file in the repo")
            continue
        n += 1
        for problem in leftovers(text):
            bad.append(f"{p.relative_to(ROOT)}: {problem}")
        low = text.lower()
        if any(v in low for v in values):
            bad.append(f"{p.relative_to(ROOT)}: holds a value from the private map")
    for b in bad[:50]:
        print(b)
    print(f"{n} files checked, {len(bad)} problem(s)" + (" (map values checked)" if mapping else ""))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
