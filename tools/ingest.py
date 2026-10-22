#!/usr/bin/env python3
# <wtl> project: research | file: tools/ingest.py | author: watchthelight </wtl>
"""File logs into logs/<username>/<machine>/<date>-<source>-<topic>/, redacted, with a meta.json.

From a GitHub issue (every comment's code blocks and text attachments, filed under the comment's author):
  python tools/ingest.py --map <private map> --issue https://github.com/OWNER/REPO/issues/N [--machine slug]
From local files:
  python tools/ingest.py --map <private map> --user watchthelight --machine lenovo-legion-5-15iax10 \
      --source N-218 --project project-legion --component boot --topic boot FILE...

A file that still looks identifying after redaction is not written; the run stops with exit code 2.
Already ingested sources (comment URLs, file hashes) are skipped, so running it twice adds nothing.
Machine details (model, board, CPU, GPU, chips, macOS builds) go into machines.json with --model etc.
Python 3.9+, stdlib only; --issue needs the gh CLI.
"""
import argparse
import datetime as dt
import hashlib
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import index  # noqa: E402
from redact import VERSION as REDACT_VERSION, leftovers, load_map, redact, save_map  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOGS = ROOT / "logs"
LEDGER = LOGS / "ingested.json"
MACHINES = ROOT / "machines.json"
SELF = "watchthelight"
TEXT_EXT = {".txt", ".log", ".panic", ".ips", ".json", ".plist", ".md", ".ioreg", ".out", ".spin", ".diag", ""}
MARKERS = [("ioreg", r"\+-o |ioreg -"), ("panic", r"panic\(|Panicked task|Backtrace"),
           ("opencore", r"\bOC[A-Z]*: |OpenCore"), ("profile", r"system_profiler|Hardware Overview|Bluetooth Controller:"),
           ("kernel-log", r"log show|kernel\[|\(kernel\)"), ("kext", r"kmutil|kextstat|org\.\w+\.\w+ \(")]
MIN_LINES = 5


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60] or "log"


def load_json(p: Path, default):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default


def save_json(p: Path, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=1, sort_keys=True, ensure_ascii=False) + "\n")


def topic_of(text: str, fallback: str = "log") -> str:
    for name, pat in MARKERS:
        if re.search(pat, text):
            return name
    return fallback


def gh_json(path: str):
    out = subprocess.run(["gh", "api", "--paginate", path], capture_output=True, text=True, encoding="utf-8")
    if out.returncode:
        sys.exit(f"gh api {path}: {out.stderr.strip()}")
    # --paginate concatenates JSON arrays as ][ ; join them
    return json.loads(out.stdout.replace("]\n[", ",").replace("][", ","))


def blocks_of(body: str):
    """Fenced code blocks worth keeping, plus links to text attachments."""
    found = []
    for m in re.finditer(r"```[^\n]*\n(.*?)```", body or "", re.S):
        text = m.group(1).strip("\n")
        if text and (text.count("\n") + 1 >= MIN_LINES or topic_of(text, "") != ""):
            found.append(("block", text))
    for m in re.finditer(r"https://github\.com/(?:user-attachments/files|[^/\s]+/[^/\s]+/files)/[^\s)\]]+", body or ""):
        url = m.group(0)
        if Path(url.split("?")[0]).suffix.lower() in TEXT_EXT:
            found.append(("attachment", url))
    return found


def fetch(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as r:
        data = r.read(5_000_001)
    if len(data) > 5_000_000:
        raise ValueError("over 5 MB")
    return data.decode("utf-8", "replace")


def machine_for(user: str, given: str, machines: dict) -> str:
    if given:
        return given
    mine = [k.split("/", 1)[1] for k in machines if k.startswith(user + "/")]
    if len(mine) == 1:
        return mine[0]
    sys.exit(f"which machine is {user}'s? pass --machine <vendor-model slug>" + (f" (known: {', '.join(mine)})" if mine else ""))


def note_machine(machines: dict, user: str, machine: str, a, build: str = None):
    key = f"{user}/{machine}"
    e = machines.setdefault(key, {"username": user, "machine": machine, "first_seen": str(dt.date.today())})
    for field in ("model", "board", "cpu", "gpu", "chips"):
        v = getattr(a, field, None)
        if v:
            e[field] = v
    if build:
        e.setdefault("macos_builds", [])
        if build not in e["macos_builds"]:
            e["macos_builds"].append(build)
    e["last_seen"] = str(dt.date.today())
    return key


def macos_build(text: str):
    # 25G241, 24H32, 24A335a (users type 25g241), only next to a label that means a macOS build, so hex dumps and
    # counters that happen to look like a build are not taken
    m = re.search(r"(?i)(?:ProductBuildVersion|BuildVersion|Build Version|OS Version[^\n]{0,40}?|macOS[^\n]{0,30}?"
                  r"|Darwin Kernel[^\n]{0,60}?|\bbuild)\W{0,4}\(?\b(2[0-9])([A-H])(\d{2,4})([a-z]?)\b", text)
    if not m:   # "26.7.1 (25g241)": a macOS version followed by its build in brackets
        m = re.search(r"\b1[0-9]\.\d+(?:\.\d+)?\s*\((2[0-9])([A-Ha-h])(\d{2,4})([a-z]?)\)|\b2[0-9]\.\d+(?:\.\d+)?\s*"
                      r"\((2[0-9])([A-Ha-h])(\d{2,4})([a-z]?)\)", text)
        if m:
            g = [x for x in m.groups() if x is not None]
            return f"{g[0]}{g[1].upper()}{g[2]}{g[3]}"
    return f"{m.group(1)}{m.group(2).upper()}{m.group(3)}{m.group(4)}" if m else None


def write_entry(user, machine, date, source_slug, topic, files, meta, mapping, dry):
    """files: [(name, raw text)]. Redacts all of them first; writes nothing if one is still identifying."""
    folder = LOGS / user / machine / f"{date}-{source_slug}-{topic}"
    out, hits_all = [], {}
    for name, raw in files:
        name = re.sub(r"[^\w.+-]", "_", redact(name, f"{user}/{machine}", mapping)[0])   # names can carry a hostname
        text, hits = redact(raw, f"{user}/{machine}", mapping)
        left = leftovers(text, mapping)
        if left:
            print(f"REFUSED {folder.relative_to(ROOT)}/{name}: " + "; ".join(left[:5]), file=sys.stderr)
            return None
        for k, v in hits.items():
            hits_all[k] = hits_all.get(k, 0) + v
        out.append((name, text))
    meta = dict(meta, username=user, machine=machine, collected=date,
                redaction={"tool": f"tools/redact.py v{REDACT_VERSION}", "replaced": hits_all},
                files={n: hashlib.sha256(t.encode()).hexdigest() for n, t in out})
    if dry:
        print(f"would write {folder.relative_to(ROOT)} ({len(out)} files, replaced {hits_all or 'nothing'})")
        return folder
    folder.mkdir(parents=True, exist_ok=True)
    for name, text in out:
        with open(folder / name, "w", encoding="utf-8", newline="\n") as f:
            f.write(text if text.endswith("\n") else text + "\n")
    save_json(folder / "meta.json", meta)
    print(f"wrote {folder.relative_to(ROOT)} ({len(out)} files, replaced {hits_all or 'nothing'})")
    return folder


def ingest_issue(a, mapping, ledger, machines):
    m = re.match(r"https://github\.com/([^/]+)/([^/]+)/(?:issues|pull)/(\d+)", a.issue)
    if not m:
        sys.exit("--issue wants https://github.com/OWNER/REPO/issues/N")
    owner, repo, num = m.groups()
    issue = gh_json(f"repos/{owner}/{repo}/issues/{num}")
    comments = gh_json(f"repos/{owner}/{repo}/issues/{num}/comments")
    posts = [(issue["html_url"], issue["user"]["login"], issue["created_at"], issue.get("body") or "")]
    posts += [(c["html_url"], c["user"]["login"], c["created_at"], c.get("body") or "") for c in comments]
    wrote = 0
    for url, user, created, body in posts:
        if url in ledger or (user == SELF and not a.include_self):
            continue
        items = blocks_of(body)
        if not items:
            continue
        machine = machine_for(user, a.machine, machines)
        files = []
        for n, (kind, val) in enumerate(items, 1):
            try:
                text = fetch(val) if kind == "attachment" else val
            except Exception as e:   # noqa: BLE001
                print(f"skipped attachment {val}: {e}", file=sys.stderr)
                continue
            post_id = "c" + url.split("#issuecomment-")[1] if "#issuecomment-" in url else "issue"
            files.append((f"{post_id}-{n}-{topic_of(text)}.txt", text))
        if not files:
            continue
        date = created[:10]
        build = macos_build(body)
        meta = {"source": url, "project": repo, "component": a.component or "", "macos_build": build or "",
                "opencore": "", "kexts": {}, "issue_title": issue["title"]}
        folder = write_entry(user, machine, date, f"{repo}-{num}", a.topic or topic_of(files[0][1]), files, meta,
                             mapping, a.dry_run)
        if folder is None:
            return 2
        if not a.dry_run:
            ledger[url] = str(folder.relative_to(ROOT)).replace("\\", "/")
            note_machine(machines, user, machine, a, build)
        wrote += 1
    print(f"{wrote} new post(s) from {owner}/{repo}#{num}")
    return 0


def ingest_files(a, mapping, ledger, machines):
    if not (a.user and a.machine and a.source):
        sys.exit("local files need --user, --machine and --source")
    files = []
    for f in a.files:
        p = Path(f)
        if p.stat().st_size > 5_000_000 or p.suffix.lower() not in TEXT_EXT:
            print(f"skipped {p.name} (binary or over 5 MB)", file=sys.stderr)
            continue
        raw = p.read_bytes()
        key = "sha256:" + hashlib.sha256(raw).hexdigest()
        if key in ledger:
            continue
        files.append((p.name, raw.decode("utf-8", "replace"), key))
    if not files:
        print("nothing new")
        return 0
    date = a.date or str(dt.date.today())
    build = next((b for b in (macos_build(t) for _, t, _ in files) if b), None)
    meta = {"source": a.source, "project": a.project or "", "component": a.component or "",
            "macos_build": a.macos_build or build or "", "opencore": a.opencore or "", "kexts": {}}
    folder = write_entry(a.user, a.machine, date, slug(a.source), a.topic or topic_of(files[0][1]),
                         [(n, t) for n, t, _ in files], meta, mapping, a.dry_run)
    if folder is None:
        return 2
    if not a.dry_run:
        for _, _, key in files:
            ledger[key] = str(folder.relative_to(ROOT)).replace("\\", "/")
        note_machine(machines, a.user, a.machine, a, meta["macos_build"])
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--map", required=True, help="private value-to-token map (outside this repo)")
    ap.add_argument("--issue")
    ap.add_argument("--include-self", action="store_true", help="also take watchthelight's own comments")
    ap.add_argument("--user")
    ap.add_argument("--machine", help="vendor-model slug, e.g. lenovo-legion-5-15iax10")
    ap.add_argument("--source", help="N-xx, a URL or another short name")
    ap.add_argument("--project"); ap.add_argument("--component"); ap.add_argument("--topic")
    ap.add_argument("--date"); ap.add_argument("--macos-build"); ap.add_argument("--opencore")
    for field in ("model", "board", "cpu", "gpu", "chips"):
        ap.add_argument(f"--{field}", help=f"machine {field} for machines.json")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("files", nargs="*")
    a = ap.parse_args()
    mapping = load_map(a.map)
    ledger = load_json(LEDGER, {})
    machines = load_json(MACHINES, {})
    rc = ingest_issue(a, mapping, ledger, machines) if a.issue else ingest_files(a, mapping, ledger, machines)
    if rc == 0 and not a.dry_run:
        save_map(a.map, mapping)
        save_json(LEDGER, ledger)
        save_json(MACHINES, machines)
        index.build()
    sys.exit(rc)


if __name__ == "__main__":
    main()
