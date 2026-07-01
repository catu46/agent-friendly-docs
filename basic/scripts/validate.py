#!/usr/bin/env python3
"""validate.py - shape checker for agent-friendly-docs-BASIC (lite+) trees.

Stdlib only; Python 3.8+. The lite+ shape per folder is FLAT: a thin AGENTS.md
router + a one-line "@AGENTS.md" CLAUDE.md stub + one index.md (the folder's
knowledge) + an append-only log.md. No knowledge/ bundle, no concept files, no
graph. (For that, use agent-friendly-docs-pro-max and its validate.py.)

ERROR checks (exit 1 on any):
  1. every non-excluded dir with content has BOTH AGENTS.md and CLAUDE.md
  2. each CLAUDE.md is exactly "@AGENTS.md" (one optional leading HTML-comment line)
  3. AGENTS.md / index.md / log.md frontmatter has type + title + timestamp
  3b. the fixed-name files carry their canonical type
      (AGENTS.md->agent-guide, index.md->index, log.md->log)
  4. every relative markdown link resolves
  5. timestamps parse as ISO-8601
  6. a folder that has an AGENTS.md also has an index.md (the router points to it)

WARN checks (printed, never fail the run):
  7. a folder with an AGENTS.md has no log.md
  8. AGENTS.md missing "## Rules" / "## Knowledge" / "## Keep this current"
  9. AGENTS.md lacks the "If you opened only this folder" up-pointer while a parent
     AGENTS.md exists

Excluded from the walk: dotfiles/dirs, common build/dep dirs (node_modules, venv,
env, *.egg-info, ...), plus any glob listed one-per-line in a root .okfignore
(use it to skip folders the rules say NOT to touch: client inputs, old versions).
"""

import argparse
import datetime
import fnmatch
import os
import re
import sys

EXCLUDED = {".git", "node_modules", "dist", "build", ".next", "target",
            "vendor", "__pycache__", "_archive",
            "venv", "env", ".venv"}          # Python virtualenvs
EXCLUDED_GLOBS = ("*.egg-info",)             # matched against the basename
EXPECTED_TYPE = {"AGENTS.md": "agent-guide", "index.md": "index", "log.md": "log"}
UP_POINTER = "## If you opened only this folder"
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")

errors, warnings = [], []


def err(p, m):
    errors.append((p, m))


def warn(p, m):
    warnings.append((p, m))


def is_url(v):
    return bool(re.match(r"^[a-zA-Z][a-zA-Z0-9+.\-]*://", v)) or v.startswith("mailto:")


def parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        return None, text
    fm = {}
    for raw in lines[1:end]:
        line = raw.rstrip()
        s = line.strip()
        if not s or s.startswith("#") or ":" not in line:
            continue
        key, _, value = line.partition(":")
        value = value.strip()
        m = re.search(r"\s+#", value)
        if m:
            value = value[:m.start()].strip()
        if len(value) >= 2 and value[0] in "\"'" and value[-1] == value[0]:
            value = value[1:-1]
        fm[key.strip()] = value
    return fm, "\n".join(lines[end + 1:])


def parse_timestamp(v):
    v = v.strip()
    if v.endswith("Z"):
        v = v[:-1] + "+00:00"
    try:
        datetime.datetime.fromisoformat(v)
        return True
    except ValueError:
        return False


def strip_code_fences(text):
    out, fence = [], None
    for line in text.splitlines():
        m = re.match(r"(`{3,}|~{3,})", line.lstrip())
        if fence is None:
            if m:
                fence = m.group(1)[0]
                continue
            out.append(line)
        elif m and m.group(1)[0] == fence:
            fence = None
    return "\n".join(out)


def check_links(path, body, base):
    for m in LINK_RE.finditer(strip_code_fences(body)):
        t = m.group(1).strip()
        mt = re.match(r'^(.*?)\s+"[^"]*"$', t)
        if mt:
            t = mt.group(1).strip()
        if t.startswith("<") and t.endswith(">"):
            t = t[1:-1].strip()
        if not t or is_url(t) or t.startswith("#") or t.startswith("/"):
            continue
        t = t.split("#", 1)[0]
        if t and not os.path.exists(os.path.normpath(os.path.join(base, t))):
            err(path, 'markdown link does not resolve: "%s"' % t)


def load_ignore_patterns(root):
    """Read an optional .okfignore at the root: one glob per line, '#' comments
    and blank lines skipped, trailing '/' stripped. Lets a lite+ tree exclude
    folders the rules say NOT to touch (client inputs, old versions)."""
    patterns = []
    ignore_file = os.path.join(root, ".okfignore")
    if os.path.isfile(ignore_file):
        try:
            with open(ignore_file, encoding="utf-8") as f:
                for line in f:
                    s = line.strip()
                    if s and not s.startswith("#"):
                        patterns.append(s.rstrip("/"))
        except OSError:
            pass
    return patterns


def excluded(name, relpath="", ignore_patterns=()):
    if name in EXCLUDED or name.startswith("."):
        return True
    if any(fnmatch.fnmatch(name, g) for g in EXCLUDED_GLOBS):
        return True
    relpath = relpath.replace(os.sep, "/")
    for pat in ignore_patterns:
        if fnmatch.fnmatch(name, pat) or fnmatch.fnmatch(relpath, pat) \
                or fnmatch.fnmatch(relpath, pat + "/*"):
            return True
    return False


def has_content(dirpath):
    try:
        return any(os.path.isfile(os.path.join(dirpath, e)) and not e.startswith(".")
                   for e in os.listdir(dirpath))
    except OSError:
        return False


def parent_agents_exists(dirpath, root):
    root = os.path.abspath(root)
    cur = os.path.abspath(os.path.dirname(dirpath))
    while cur == root or cur.startswith(root + os.sep):
        if os.path.isfile(os.path.join(cur, "AGENTS.md")):
            return True
        if cur == root:
            break
        nxt = os.path.dirname(cur)
        if nxt == cur:
            break
        cur = nxt
    return False


def check_claude_stub(path):
    lines = [l.rstrip() for l in open(path, encoding="utf-8").read().splitlines()]
    i = 0
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    if i < len(lines) and re.match(r"^\s*<!--.*-->\s*$", lines[i]):
        i += 1
        while i < len(lines) and lines[i].strip() == "":
            i += 1
    if [l for l in lines[i:] if l.strip()] != ["@AGENTS.md"]:
        err(path, 'CLAUDE.md must be exactly "@AGENTS.md" '
                  "(one optional leading HTML-comment line allowed)")


def check_md(path, root):
    text = open(path, encoding="utf-8").read()
    fm, body = parse_frontmatter(text)
    base = os.path.dirname(path)
    name = os.path.basename(path)
    check_links(path, body if fm is not None else text, base)
    if fm is None:
        # A canonical fixed-name doc must carry frontmatter; silently passing one
        # with its whole `---` block deleted would defeat the type/title checks.
        if name in EXPECTED_TYPE:
            err(path, "missing YAML frontmatter (canonical docs require type + title + timestamp)")
        return
    for k in ("type", "title", "timestamp"):
        if k not in fm:
            err(path, 'frontmatter missing required key "%s"' % k)
    if "timestamp" in fm and not parse_timestamp(fm["timestamp"]):
        err(path, 'timestamp is not valid ISO-8601: "%s"' % fm["timestamp"])
    exp = EXPECTED_TYPE.get(name)
    if exp and fm.get("type") and fm["type"] != exp:
        err(path, 'type "%s" should be "%s" for %s' % (fm["type"], exp, name))
    if name == "AGENTS.md":
        if UP_POINTER not in body and parent_agents_exists(base, root):
            warn(path, 'AGENTS.md lacks the "If you opened only this folder" up-pointer')
        for h in ("## Rules", "## Knowledge", "## Keep this current"):
            if h not in body:
                warn(path, 'AGENTS.md is missing the "%s" section' % h)


def run(root):
    md_files = []
    ignore_patterns = load_ignore_patterns(root)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not excluded(
            d, os.path.relpath(os.path.join(dirpath, d), root), ignore_patterns)]
        if has_content(dirpath):
            miss = [f for f in ("AGENTS.md", "CLAUDE.md") if f not in filenames]
            if miss:
                err(dirpath, "folder with content is missing %s" % ", ".join(miss))
        if "AGENTS.md" in filenames:
            if "index.md" not in filenames:
                err(dirpath, "folder has AGENTS.md but no index.md")
            if "log.md" not in filenames:
                warn(dirpath, "folder has AGENTS.md but no log.md")
        for fn in filenames:
            fp = os.path.join(dirpath, fn)
            if fn == "CLAUDE.md":
                check_claude_stub(fp)
            if fn.endswith(".md"):
                md_files.append(fp)
    for fp in md_files:
        check_md(fp, root)
    return md_files


def main(argv):
    ap = argparse.ArgumentParser(
        prog="validate.py",
        description="Shape checker for agent-friendly-docs-basic (lite+). Stdlib only. "
                    "Exits 1 only on an ERROR; WARN findings never fail.")
    ap.add_argument("path", nargs="?", default=".",
                    help="root directory to validate (default: current directory)")
    a = ap.parse_args(argv[1:])
    root = os.path.abspath(a.path)
    if not os.path.isdir(root):
        sys.stderr.write("ERROR: not a directory: %s\n" % root)
        return 2
    md_files = run(root)
    print("agent-friendly-docs-basic :: validate")
    print("root: %s" % root)
    print("markdown files scanned: %d" % len(md_files))
    if warnings:
        print("\nWARN (%d):" % len(warnings))
        for p, m in warnings:
            print("  WARN  %s: %s" % (os.path.relpath(p, root), m))
    if errors:
        print("\nERROR (%d):" % len(errors))
        for p, m in errors:
            print("  ERROR %s: %s" % (os.path.relpath(p, root), m))
        print("\nFAIL - %d error(s), %d warning(s)" % (len(errors), len(warnings)))
        return 1
    print("\nPASS - 0 errors, %d warning(s)" % len(warnings))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
