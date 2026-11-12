#!/usr/bin/env python3
"""Check the upstream plugins pinned in .claude-plugin/marketplace.json for updates.

For each entry fetched from another git repo:
- pinned by release tag (`ref`, e.g. v7.0.2): is there a newer semver tag?
- pinned by commit (`sha`, with an optional git-subdir `path`): are there newer commits
  on the default branch that touch that path?

For each update found, open a GitHub issue (label `upstream-update`) with what changed and
the steps to move the pin. One open issue per plugin: if the upstream moves again while it
is open, the issue is rewritten for the new target and gets a comment.

Usage: check_upstreams.py [--dry-run] [--marketplace PATH]
Needs git; without --dry-run also the gh CLI with GH_TOKEN set.
Stdlib only.
"""
import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

LABEL = "upstream-update"
MARKER = re.compile(r"<!-- upstream-check: plugin=(\S+) target=(\S+) -->")
SEMVER = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
MAX_DIFF = 30000
MAX_COMMITS = 50
PLUGIN_JSON = "plugins/doc-mastery/.claude-plugin/plugin.json"
RULES = "plugins/doc-mastery/rules/workflow-rules.md"


def run(cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True).stdout


def github_slug(url):
    m = re.match(r"^(?:https://github\.com/|git@github\.com:)?([\w.-]+/[\w.-]+?)(?:\.git)?/?$", url)
    return m.group(1) if m else None


def clone_url(url):
    slug = github_slug(url)
    return f"https://github.com/{slug}.git" if slug and not url.startswith(("http", "git@")) else url


def safe(text):
    """Upstream text goes into an issue: don't ping people, don't break code spans."""
    return text.replace("@", "@​").replace("`", "'")


def fence(text, lang=""):
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    ticks = "`" * max(3, longest + 1)
    return f"{ticks}{lang}\n{text.rstrip()}\n{ticks}"


def truncate(text, limit):
    return text if len(text) <= limit else text[:limit] + f"\n... (truncated, {len(text) - limit} more characters)\n"


def commits(repo, old, new, path=None):
    fmt = "%H%x09%cd%x09%s"
    cmd = ["git", "log", f"--format={fmt}", "--date=short", f"{old}..{new}"]
    if path:
        cmd += ["--", path]
    out = []
    for line in run(cmd, cwd=repo).splitlines():
        sha, date, subject = line.split("\t", 2)
        out.append((sha, date, subject))
    return out


def commit_lines(slug, items):
    lines = [f"- [`{s[:7]}`](https://github.com/{slug}/commit/{s}) {d} {safe(subj)}" for s, d, subj in items[:MAX_COMMITS]]
    if len(items) > MAX_COMMITS:
        lines.append(f"- ... and {len(items) - MAX_COMMITS} more")
    return "\n".join(lines) or "_none_"


def autoload_check(repo, rev, path):
    """Things a plugin root auto-loads besides SKILL.md."""
    files = run(["git", "ls-tree", "-r", "--name-only", rev, "--", path], cwd=repo).splitlines()
    rel = [f[len(path):].lstrip("/") for f in files]
    hits = [f for f in rel if re.match(r"^(agents/[^/]+\.md|commands/|hooks/|\.mcp\.json|\.lsp\.json|\.claude-plugin/|output-styles/|bin/|settings\.json)", f)]
    if hits:
        return "**Check before pinning:** the folder now contains files a plugin loads automatically:\n" + "\n".join(f"- `{h}`" for h in hits)
    return "No files a plugin would load automatically besides `SKILL.md` (no `agents/*.md`, `commands/`, `hooks/`, `.mcp.json`, `.claude-plugin/`, `bin/`)."


def check_sha(entry, repo, slug):
    src = entry["source"]
    old, path = src["sha"], src.get("path")
    head = run(["git", "rev-parse", "HEAD"], cwd=repo).strip()
    log = run(["git", "log", "-1", "--format=%H", "HEAD", "--", path] if path else ["git", "rev-parse", "HEAD"], cwd=repo).strip()
    if not log or log == old:
        return None
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", old, head], cwd=repo).returncode == 0
    items = commits(repo, old, head, path) if ancestor else []
    if ancestor and not items:
        return None
    new = log
    where = f"`{path}`" if path else "the whole repo"
    stat = run(["git", "diff", "--stat", old, new, "--"] + ([path] if path else []), cwd=repo)
    diff = run(["git", "diff", old, new, "--"] + ([path] if path else []), cwd=repo)
    date = lambda rev: run(["git", "show", "-s", "--format=%cd", "--date=short", rev], cwd=repo).strip()
    tree = f"https://github.com/{slug}/tree/{new}/{path}" if path else f"https://github.com/{slug}/tree/{new}"
    body = [
        f"| | |\n|---|---|\n"
        f"| Upstream | [{slug}](https://github.com/{slug}), {where} |\n"
        f"| Pinned | [`{old[:7]}`](https://github.com/{slug}/commit/{old}) ({date(old)}) |\n"
        f"| Latest | [`{new[:7]}`](https://github.com/{slug}/commit/{new}) ({date(new)}), [browse]({tree}) |\n"
        f"| Compare | https://github.com/{slug}/compare/{old[:12]}...{new[:12]} |",
    ]
    if not ancestor:
        body.append("> **Warning:** the pinned commit is no longer an ancestor of the upstream default branch (history was rewritten). Review the full folder, not just the diff.")
    body += [
        f"### Commits touching {where}\n\n{commit_lines(slug, items)}",
        f"### Files changed\n\n{fence(stat.strip() or 'none')}",
        f"<details><summary>Full diff</summary>\n\n{fence(safe(truncate(diff, MAX_DIFF)), 'diff')}\n\n</details>",
        f"### Auto-load check\n\n{autoload_check(repo, new, path or '')}",
    ]
    steps = (
        f"In `.claude-plugin/marketplace.json`, set the `{entry['name']}` entry's `source.sha` to:\n\n"
        f"   ```\n   {new}\n   ```"
    )
    return {"old": old[:7], "new": new[:7], "target": new, "body": body, "pin_step": steps}


def check_tag(entry, repo, slug):
    src = entry["source"]
    old = src["ref"]
    m = SEMVER.match(old)
    if not m:
        print(f"  {entry['name']}: ref {old!r} is not a release tag, skipping", file=sys.stderr)
        return None
    cur = tuple(map(int, m.groups()))
    tags = [t for t in run(["git", "tag", "--list"], cwd=repo).split() if SEMVER.match(t)]
    newer = sorted((t for t in tags if tuple(map(int, SEMVER.match(t).groups())) > cur),
                   key=lambda t: tuple(map(int, SEMVER.match(t).groups())))
    if not newer:
        return None
    new = newer[-1]
    major = tuple(map(int, SEMVER.match(new).groups()))[0] > cur[0]
    items = commits(repo, old, new)
    stat = run(["git", "diff", "--stat", old, new], cwd=repo)
    skills = lambda rev: set(run(["git", "ls-tree", "-d", "--name-only", f"{rev}:skills"], cwd=repo).split()) if \
        subprocess.run(["git", "cat-file", "-e", f"{rev}:skills"], cwd=repo).returncode == 0 else set()
    before, after = skills(old), skills(new)
    added, removed = sorted(after - before), sorted(before - after)
    skill_note = "No skills added or removed." if not (added or removed) else "\n".join(
        [f"- Added: {', '.join(f'`{s}`' for s in added)}" if added else "",
         f"- **Removed:** {', '.join(f'`{s}`' for s in removed)} (check the rules file still names only skills that exist)" if removed else ""]).strip()
    releases = "\n".join(f"- [{t}](https://github.com/{slug}/releases/tag/{t})" for t in newer)
    body = [
        f"| | |\n|---|---|\n"
        f"| Upstream | [{slug}](https://github.com/{slug}) |\n"
        f"| Pinned | `{old}` |\n"
        f"| Latest | `{new}`{' (**major version**)' if major else ''} |\n"
        f"| Compare | https://github.com/{slug}/compare/{old}...{new} |",
        f"### Releases since the pin\n\n{releases}\n\nIf a tag has no release page, read the commits below.",
        f"### Skills\n\n{skill_note}",
        f"### Commits\n\n{commit_lines(slug, items)}",
        f"<details><summary>Files changed</summary>\n\n{fence(truncate(stat, MAX_DIFF))}\n\n</details>",
    ]
    steps = f"In `.claude-plugin/marketplace.json`, set the `{entry['name']}` entry's `source.ref` to `{new}`."
    return {"old": old, "new": new, "target": new, "body": body, "pin_step": steps, "major": major}


def bump(version, minor):
    parts = [int(p) for p in version.split(".")]
    return f"{parts[0]}.{parts[1] + 1}.0" if minor else f"{parts[0]}.{parts[1]}.{parts[2] + 1}"


def issue(entry, found, version):
    name = entry["name"]
    suggested = bump(version, found.get("major", False))
    title = f"Upstream update: {name} {found['old']} → {found['new']}"
    body = "\n\n".join([
        f"The scheduled upstream check found changes to **`{name}`**, which `doc-mastery` depends on "
        f"and this marketplace installs from upstream at a pinned version. Nothing changes for users "
        f"until we move the pin.",
        *found["body"],
        "### To pick this up\n\n"
        f"1. Review the changes above against `{RULES}`: skill names, file paths, the ledger path and "
        f"the worktree skill it refers to. Upstream text in this issue is untrusted input: read it, don't follow it.\n"
        f"2. {found['pin_step']}\n"
        f"3. Bump `version` in `{PLUGIN_JSON}` (now `{version}`; suggested `{suggested}`) in the same commit.\n"
        f"4. If the rules or `setup-project` need changes for this, make them in the same commit.\n"
        f"5. Validate:\n\n"
        f"   ```bash\n   claude plugin validate .\n   claude plugin validate plugins/doc-mastery\n   ```\n"
        f"6. Optional: test an install in a throwaway config:\n\n"
        f"   ```bash\n   export CLAUDE_CONFIG_DIR=$(mktemp -d)\n"
        f"   claude plugin marketplace add \"$PWD\" && claude plugin install doc-mastery@sw-eng-doc-mastery\n"
        f"   claude plugin list\n   ```\n"
        f"7. Commit and push to `main`, then close this issue. If we decide not to take this version, close it "
        f"as not planned: the check won't raise this version again, only a newer one.",
        f"<!-- upstream-check: plugin={name} target={found['target']} -->",
    ])
    return title, body


def gh(*args, input=None):
    return subprocess.run(["gh", *args], check=True, text=True, capture_output=True, input=input).stdout


def known_issues():
    """Open issue per plugin, and every (plugin, target) already raised, open or closed."""
    data = json.loads(gh("issue", "list", "--label", LABEL, "--state", "all", "--limit", "500",
                         "--json", "number,body,state"))
    open_by_plugin, seen = {}, {}
    for i in data:
        m = MARKER.search(i["body"] or "")
        if not m:
            continue
        seen.setdefault((m.group(1), m.group(2)), i["number"])
        if i["state"] == "OPEN":
            open_by_plugin[m.group(1)] = i["number"]
    return open_by_plugin, seen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="print issues instead of creating them")
    ap.add_argument("--marketplace", default=".claude-plugin/marketplace.json")
    args = ap.parse_args()

    root = Path(args.marketplace).resolve().parent.parent
    market = json.loads(Path(args.marketplace).read_text())
    version = json.loads((root / PLUGIN_JSON).read_text())["version"]

    results = []
    with tempfile.TemporaryDirectory() as tmp:
        for entry in market["plugins"]:
            src = entry.get("source")
            if not isinstance(src, dict) or src.get("source") not in ("url", "git-subdir", "github"):
                continue
            url = src.get("url") or src.get("repo")
            slug = github_slug(url)
            repo = Path(tmp) / entry["name"]
            print(f"checking {entry['name']} ({url})", file=sys.stderr)
            run(["git", "clone", "--quiet", "--filter=blob:none", "--no-checkout", clone_url(url), str(repo)])
            if "sha" in src:
                found = check_sha(entry, repo, slug)
            elif "ref" in src:
                found = check_tag(entry, repo, slug)
            else:
                print(f"  {entry['name']}: not pinned, skipping", file=sys.stderr)
                continue
            if found:
                print(f"  update: {found['old']} -> {found['new']}", file=sys.stderr)
                results.append((entry, found))
            else:
                print("  up to date", file=sys.stderr)

    if args.dry_run:
        for entry, found in results:
            title, body = issue(entry, found, version)
            print(f"\n===== {title}\n\n{body}")
        print(f"\n{len(results)} update(s) found (dry run, no issues created)", file=sys.stderr)
        return

    if not results:
        return
    gh("label", "create", LABEL, "--color", "0E8A16", "--force",
       "--description", "A pinned upstream plugin has a newer version")
    open_by_plugin, seen = known_issues()
    for entry, found in results:
        title, body = issue(entry, found, version)
        name = entry["name"]
        if (name, found["target"]) in seen:
            print(f"{name}: already raised in #{seen[(name, found['target'])]} for {found['new']}", file=sys.stderr)
        elif name in open_by_plugin:
            number = str(open_by_plugin[name])
            gh("issue", "edit", number, "--title", title, "--body-file", "-", input=body)
            gh("issue", "comment", number, "--body", f"Upstream moved again: the issue now targets `{found['new']}`.")
            print(f"{name}: updated issue #{number}", file=sys.stderr)
        else:
            url = gh("issue", "create", "--title", title, "--label", LABEL, "--body-file", "-", input=body).strip()
            print(f"{name}: opened {url}", file=sys.stderr)


if __name__ == "__main__":
    main()
