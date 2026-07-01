# Reconciliation Watcher — Basic (lite+)

Keeps `index.md` + `log.md` honest when people change the real artifacts
**outside Claude Code** — SharePoint, Drive, Finder/Explorer. The watcher is a
scheduled agent run; **the master prompt lives in one place, `scripts/watcher-prompt.txt`**
— that is the single source of truth. Do not paste copies of it into this file
or anywhere else: the pro-max audit found duplicated prompt copies drift out of
sync with each other. This doc is the design spec; that file is the prompt.
(`arm-watcher.sh` copies that master into the target tree at `<tree>/.okf/watcher-prompt.txt`
and the cron job runs it from there, logging to `<tree>/.okf/.watcher.log`. The
`.okf/` dir is hidden so `validate.py` prunes it — re-arming just refreshes the copy.)

## 1. The problem

The audience is mostly non-engineers, and they change files in ways that never
touch git or an IDE: duplicating `Plan_v7.xlsx` into `Plan_v8.xlsx`, dropping a
new deck into a folder, refreshing numbers in place, renaming or deleting a
file in Finder/Explorer/SharePoint/Drive. SharePoint and Drive have no git —
there is no commit log to diff against. A doc system that only updates when
someone happens to run Claude Code rots within a day. Detection must not
depend on who edited the file or how.

## 2. Snapshot-diff detection

Each folder keeps its own `.okf-state.json` (paths relative to **that folder**
— basic has no `knowledge/` subdir to nest it under):

```json
{ "generated": "2026-07-01T12:00:00Z",
  "files": [{ "path": "modelo_q3_v8.xlsx", "sha256": "…", "mtime": 1782900000, "size": 184320 }] }
```

Each run: rescan the folder's real artifacts, recompute `sha256`/`mtime`/`size`,
diff against the snapshot → `added` / `modified` / `deleted`. Compare by
**`sha256`**, not `mtime` — a cloud sync or re-save can bump `mtime` without
changing a byte. Backends, strongest first, combinable:
- **filesystem walk + hash** — always works, the baseline;
- **git** — `git status --porcelain` plus `git log --since=<generated> --name-status`
  (anchor on the snapshot's `generated`; no commit SHA is stored);
- **source "modified since" API** (Drive/SharePoint/etc.) when artifacts live
  behind a URL;
- **MCP connector** — the same, over Model Context Protocol; the most
  ergonomic cloud option, but session-scoped (see §6).

Then **classify by reading** the changed artifact (bounded — PDF via native
page ranges, `.pptx`/`.xlsx`/`.docx` via `python-pptx`/`openpyxl`/`python-docx`
or `unzip`+strip-XML, legacy `.doc`/`.ppt`/`.xls` via `textutil`/`soffice`) —
same reading rules as the discovery loop in SKILL.md. A diff alone never tells
you *what* to write; opening the file does.

## 3. The lite+ apply — update `index.md`, APPEND to `log.md`, never overwrite

For an ordinary change (data refreshed, new artifact, structure edited in
place): update the relevant `index.md` section (`What's here` /
`Definitions & assumptions` / `How to work here`) to match the new reality,
then **append** one dated line to `log.md` — what changed, why, who/source.
Never rewrite a past `log.md` line; never silently drop an `index.md` fact,
only move it forward.

For a **v7→v8 supersede** specifically:
1. archive the old artifact into `_archive/` (or rely on the source's own
   version history);
2. point `index.md`'s `What's here` entry at the **new** file;
3. summarize the *why* under `index.md`'s `Decisions` section (short — the
   full timeline is `log.md`);
4. append one `log.md` line noting old→new, the archive path, and who/source.

This is lite+'s stand-in for pro-max's per-concept `status`/`supersede`
frontmatter graph, collapsed onto one file: `index.md` always shows the
current state, `log.md` always shows every state that came before it.

## 4. When reading doesn't resolve it: ask the last editor

Don't guess — ask. Attribution is source-dependent; state it honestly:
git-backed → `git log -1 --format='%an <%ae>' -- <file>`; Drive/SharePoint →
the item's "last modified by" API field; plain filesystem → the OS file
owner (often an account, not the human); otherwise a configured folder owner.
Default delivery is an `ASKS.md` queue at the folder root (a tracker issue,
Slack, or email work too — pick one per project). `ASKS.md` is created on the
first question and is append-only; one block each:

```
## 2026-06-30T09:12:00Z — Plan_v8.xlsx
- change: CHANGED Modelo!A2: 100 -> 120 (premise); new tab "Scenario_C"
- unclear: was the premise change intentional, and what is Scenario_C?
- editor: a.gonzalez (source: git author)
- status: open
```

Leave the change un-applied or flagged until it's answered. To force a question
for critical files (never auto-apply), list globs one per line in a
`.okf/always-ask` at the tree root.

**Materiality gate — only report what changes what's inside.** `index.md` exists to
say what a folder *contains*, so the watcher ignores cosmetic edits and acts only on
shape/inventory changes. For `.xlsx/.pptx/.docx/.pdf`, `scripts/artifact-diff.py`
fingerprints each file and diffs it against a baseline at
`.okf/fingerprints/<relpath>.json`. **By default it is structural**: xlsx = sheet
names + used range + headers; pptx = slide count + titles; docx = heading outline +
paragraph count; pdf = page count + page headings. So a retuned constant, a premise
nudged 100→120, a reworded bullet or a typo is **"no material change"** — the docs are
left alone; a new tab, a new/retitled slide, a new section, a new/deleted file shows
up and drives an `index.md`/`log.md` update. For a critical file you want every number
move on, list it in `.okf/always-ask`; there the watcher runs `--detail` (Excel by
formula + typed input value, the rest by paragraph) and always asks. Stdlib only (PDF
needs `pdftotext`, degrades gracefully without it).

## 5. Autonomy — arm it and forget it

One command: `scripts/arm-watcher.sh <tree> --install` (see SKILL.md). It
schedules the chosen runner against `scripts/watcher-prompt.txt`. Two ways to
run it:
- **cron + a headless CLI** (local, simplest; needs the machine on);
- **a cloud Routine** (survives laptops off, best for shared team folders;
  `/schedule` or the routines web UI).

(`/loop` and in-session cron tools are session-scoped and expire after 7 days
— not a substitute for either.)

## 6. Agnostic by design

Nothing above is Claude-specific; three things swap 1:1 and nothing else
changes:
- **the runner** — `claude -p` / `codex exec` / `gemini -p` / any headless
  agent, via `arm-watcher.sh --runner`;
- **the scheduler** — cron / a desktop scheduled task / a cloud Routine / CI;
- **PDF reading** — Claude Code's native `Read` tool vs. `pdftotext`/`unzip`
  elsewhere.

**MCP connectors can be absent in a headless cron.** An interactively
authenticated connector (e.g. a claude.ai Drive connector) is tied to that
session — a `claude -p` cron run usually won't have it. Run the watcher where
the connector lives (a cloud Routine), or fall back to the filesystem/API
backends in §2; a locally-synced folder sidesteps this entirely, at the cost
of weaker attribution.

---

Escalate a folder to `agent-friendly-docs-pro-max` once its supersedes need
their own linkable concept history — see SKILL.md, "When to escalate."
