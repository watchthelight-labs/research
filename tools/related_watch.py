#!/usr/bin/env python3
# <wtl> project: research | file: tools/related_watch.py | author: watchthelight </wtl>
"""Post one Discord digest of what moved in the projects scout/watchlist.json follows: new releases, commits on
the default branch (minus obvious noise), and new comments from other people on watchthelight-labs issues.
No AI and no writes; the daily scout run reads the details. Run by .github/workflows/related-watch.yml.

Env: GITHUB_TOKEN, DISCORD_WEBHOOK, SINCE (ISO time of the last successful run), TEST=1 to post even when quiet.
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

GH = "https://api.github.com"
TOKEN = os.environ.get("GITHUB_TOKEN", "")
HOOK = os.environ.get("DISCORD_WEBHOOK", "")
SINCE = os.environ["SINCE"]
ROOT = Path(__file__).resolve().parents[1]
NOISE = re.compile(r"(?i)^(bump|chore\(deps\)|merge branch|ci:|fix typo|typo|translations?|\[bot\])")


def gh(path, params=None):
    url = GH + path + ("?" + urllib.parse.urlencode(params) if params else "")
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "Authorization": f"Bearer {TOKEN}",
                                               "X-GitHub-Api-Version": "2022-11-28"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:   # noqa: BLE001  one broken repo must not stop the digest
        print(f"{path}: {e}", file=sys.stderr)
        return []
    return data["items"] if isinstance(data, dict) and "items" in data else data


def main():
    wl = json.loads((ROOT / "scout" / "watchlist.json").read_text(encoding="utf-8"))
    repos = {}
    for name, t in wl["targets"].items():
        for r in t["related"]:
            repos.setdefault(r["repo"], set()).add(name)
    lines = []
    for repo, targets in sorted(repos.items()):
        rel = [r for r in gh(f"/repos/{repo}/releases", {"per_page": 5}) or [] if (r.get("published_at") or "") >= SINCE]
        com = [c for c in gh(f"/repos/{repo}/commits", {"since": SINCE, "per_page": 30}) or []
               if not NOISE.search(c["commit"]["message"].split("\n", 1)[0])]
        if not rel and not com:
            continue
        bits = [f"release [{r['tag_name']}]({r['html_url']})" for r in rel]
        if com:
            first = com[0]["commit"]["message"].split("\n", 1)[0][:70]
            bits.append(f"[{len(com)} commit(s)](https://github.com/{repo}/commits) e.g. \"{first}\"")
        lines.append(f"**{repo}** ({', '.join(sorted(targets))}): " + "; ".join(bits))
    issues = gh("/search/issues", {"q": f"org:watchthelight-labs updated:>={SINCE[:19]}", "per_page": 50}) or []
    for it in issues:
        repo = it["repository_url"].split("/repos/", 1)[1]
        new = [c for c in gh(f"/repos/{repo}/issues/{it['number']}/comments", {"since": SINCE}) or []
               if c["user"]["login"] != "watchthelight"]
        if new:
            logs = " (has logs)" if any("```" in (c.get("body") or "") for c in new) else ""
            lines.append(f"**{repo}#{it['number']}**: {len(new)} new comment(s) from "
                         f"{', '.join(sorted({c['user']['login'] for c in new}))}{logs}: [{it['title'][:60]}]({it['html_url']})")
    if not lines and os.environ.get("TEST") != "1":
        print("nothing new")
        return
    desc = "\n".join(lines)[:3900] or "nothing new since " + SINCE
    payload = {"username": "related-watch", "embeds": [{"title": f"Related projects since {SINCE[:16].replace('T', ' ')} UTC",
                                                         "description": desc, "color": 0x2ECC71}]}
    if not HOOK:
        print(desc)
        return
    req = urllib.request.Request(HOOK, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json",
                                                                                   "User-Agent": "related-watch"})
    urllib.request.urlopen(req, timeout=30).read()
    print(f"posted {len(lines)} line(s)")


if __name__ == "__main__":
    main()
