# Reconciliation Watcher

The watcher is the part of this skill that keeps the docs honest **when people
change files outside Claude Code**. It is what turns the docs from a one-time
scaffold into a self-feeding loop (`se retroalimenta`): a consultant duplicates
an Excel into `v8`, drops in a new deck, or refreshes some numbers — and the next
fresh chat is still instantly smart.

This file is a design spec **and** a ready-to-run agent prompt. The skill's own
instructions stay in English; the docs the watcher writes stay in the project's
language; any questions it asks the last editor are asked in the user's language.

---

## 1. The problem

The audience is mostly non-engineers — strategy consultants, managers,
directors. They change files in ways that never touch git, an IDE, or Claude
Code:

- duplicate `Plan_v7.xlsx` into `Plan_v8.xlsx` and keep editing v8;
- drop a brand-new deck into a folder;
- refresh the numbers inside an existing workbook (same structure, new data);
- rename, move, or delete a file from Finder / Explorer / SharePoint / Drive.

A documentation system that only updates when someone runs Claude Code rots
within a day. The watcher closes that gap: **detection does not depend on who
edited the file or how.** It compares the current state of the filesystem (or
source) against a snapshot it took last time, so any change is visible regardless
of the tool that made it.

---

## 2. Snapshot-based detection

The watcher keeps one snapshot per knowledge subtree:

`knowledge/.okf-state.json`

```json
{
  "generated": "2026-06-30T12:00:00Z",
  "files": [
    { "path": "../Plan_v7.xlsx", "sha256": "…", "mtime": 1782734400, "size": 84213 }
  ]
}
```

`path` is relative to the `knowledge/` directory that holds the snapshot, so an
artifact sitting in the documented folder beside `knowledge/` (e.g.
`financials/Plan_v7.xlsx`) is `../Plan_v7.xlsx`, while a copy kept inside the
bundle is `_archive/…` — matching the paths in TEMPLATES.md's `.okf-state.json`
(`../models/…`, `_archive/…`). `sha256` is the content hash (the source of truth
for "did the bytes change"). `mtime` and `size` are cheap pre-filters and useful
tie-breakers.

Each run:

1. **Re-scan** the real artifacts under this folder (the files concepts point at
   via their `resource:` field, plus anything new sitting alongside them).
   Exclusions from the interview still apply — skip what the user said to skip.
2. **Recompute** `sha256`, `mtime`, `size` for every file found.
3. **Diff** against `.okf-state.json` to produce three lists:
   - **added** — path present now, absent in snapshot;
   - **modified** — path in both, but `sha256` differs;
   - **deleted** — path in snapshot, absent now.

Detection has three interchangeable backends; use whichever the source supports,
and they can be combined:

- **Filesystem scan (always works).** Walk the tree, hash files, diff. Needs no
  git, no IDE, no editor cooperation. This is the baseline and the reason the
  loop self-feeds.
- **git (when the tree is git-backed).** `git status --porcelain` lists
  uncommitted adds/mods/deletes (it needs no time anchor — it just reports the
  current working tree); `git log --since='<generated>' --name-status` lists what
  was committed since the last run, anchored on the `generated` timestamp the
  snapshot already stores. The snapshot keeps **no** commit SHA, so do not diff
  against a "last SHA." Git also unlocks real authorship (see §7); the `sha256`
  diff against `.okf-state.json` stays the source of truth for *what* changed.
- **Source "modified by/at" (Drive / SharePoint / BigQuery, etc.).** Query the
  source API for items changed since `generated`. Use this when the artifacts
  live behind a URL rather than on disk.

> The hash is what decides "changed," not `mtime`. A cloud sync or a re-save can
> bump `mtime` without changing content; compare `sha256` to avoid false
> positives, and only fall back to `mtime`/`size` when you cannot read the bytes.

---

## 3. Classify each change by READING the file

A diff entry alone does not tell you what to do. **Open the changed artifact and
read it** — headers, sheet/tab names (`abas`), slide titles — then classify.
Reading is bounded (see *Reading rules* below), never a full dump.

| Class | Signal | Action |
|---|---|---|
| **data-refresh** | Same structure/schema/tabs, only values changed | Restamp the concept's `timestamp`; no body edit. Log it. |
| **new-version** | `v7 → v8` naming, or a near-duplicate of an existing artifact | **Append-only supersede (see §4):** KEEP the old concept (set `status: superseded`, `superseded_by → new`, repoint its `resource → archived old file`); draft a **new** concept for the new version (`status: active`, `supersedes → old`); write a `type: decision` concept if the WHY is inferable, else queue an ask; append to `log.md`. **Never** repoint a single concept onto the new file, and never delete the old concept. |
| **new-concept** | A genuinely new artifact with no existing concept | Draft a new concept file (OKF frontmatter + body), add it to `index.md`, log it. |
| **structural** | Schema, columns, tabs (`abas`), or slide structure changed *in place* | Update the concept **body** (schema / abas / assumptions / caveats), restamp, log. |
| **deletion** | Artifact gone, no replacement | Mark the concept `status: deprecated` in its frontmatter, annotate its `index.md` entry, log it. Keep the concept file as an audit trail — never erase. |

When classifying, change only what the edit actually touched — do not rewrite a
whole concept because one number moved. On a **deletion**, keep the concept but
never leave its `resource:` pointing at the vanished file: archive the bytes and
repoint it if they are still recoverable (trash, git, source version history),
otherwise drop the optional `resource:` line and note in the body that the artifact
is gone — so `validate` check #5 (resource paths must resolve) keeps passing.

### Reading rules (bounded, aligned with the skill's facts)

- **PDF** — the Read tool reads PDFs natively via the `pages` range (max 20 pages
  per request; a range is **required** above 10 pages). Target the pages you need.
- **`.pptx` / `.xlsx` / `.docx`** are ZIP+XML. Cleanest path: `python-pptx` /
  `openpyxl` / `python-docx` (third-party — `pip install` if missing). Zero-install
  fallback: `unzip -p file.xlsx xl/sharedStrings.xml`,
  `unzip -p file.pptx ppt/slides/slide1.xml`, `unzip -p file.docx word/document.xml`,
  then strip XML tags. Caveat: `sharedStrings.xml` is the string **pool** — the
  cell→string mapping lives in `xl/worksheets/sheetN.xml`, and you must iterate all
  parts (`slide2.xml…`, `sheet2.xml…`). The libraries do that reconstruction for you.
- **Legacy `.doc` / `.ppt` / `.xls`** are binary, not ZIP — the `unzip` trick fails.
  On macOS `.doc` has a zero-install path: `textutil -convert txt old.doc`.
  `.ppt` / `.xls` need LibreOffice headless: `soffice --headless --convert-to txt|csv file.ppt`.
  (pandoc cannot read legacy binary Office files — do not reach for it here.)
- **Big spreadsheets** — never dump every cell. Get the used range cheaply:
  `unzip -p file.xlsx xl/worksheets/sheet1.xml | grep -oE '<dimension ref="[^"]+"'`,
  then with `openpyxl` use `read_only=True` and bound the iteration
  (`ws.iter_rows(min_row=1, max_row=20, values_only=True)`). Report sheet names,
  dimensions, headers, dtypes, and ~20 sample rows — enough to classify, not the
  whole grid.

---

## 4. Append-only memory: how a v7 → v8 supersede works

This is the heart of the watcher and the design's sweet spot. Replacing an
artifact must **add** memory, never overwrite it — so "what we used to do" stays
recoverable. The file PATH is each concept's ID, so a new version gets its **own**
concept; the old one is kept and marked, not edited away.

### Status transitions

Concept frontmatter carries `status: active | superseded | deprecated`:

- **active → superseded** — the artifact was replaced by a newer version. The old
  concept gains `superseded_by: <new concept>`; the new concept gains
  `supersedes: <old concept>`. Both files persist.
- **active → deprecated** — the artifact was retired/deleted with **no** successor.
  No `superseded_by`; the concept stays as a tombstone.
- A `superseded` or `deprecated` concept is **never deleted**. `index.md` keeps it
  (marked) so the history stays navigable, and the validate script will warn if a
  `superseded` concept is missing its `superseded_by` pointer.

### The four moves on a v7 → v8 detection

1. **Archive the old bytes and keep the old concept.** Move the prior artifact into
   `_archive/` (or rely on the source's version history) and repoint the **old**
   concept's `resource:` at that archived copy, so the pointer still resolves. Set
   `status: superseded` and `superseded_by:` the new concept. Do **not** touch its
   body's description of what v7 meant — that *is* the memory. Keep the original as
   a backup (in `_archive/` and in git) until the user validates the supersede.
2. **Draft the new concept** for the new artifact, `status: active`, `supersedes:`
   the old concept, `resource:` the live file. Carry forward the schema/abas the
   classifier read.
3. **Record the WHY** as a `type: decision` concept (a lightweight ADR) **when you
   can infer it** from the diff ("the `NRR` tab now subtracts one-off credits"). If
   the why is not inferable, do **not** invent it — queue an ask (§7) and link it
   later.
4. **Append to `log.md`** one reverse-chronological line, and restamp every doc you
   touched (§6).

### Worked example

Folder `financials/`, after `Plan_v7.xlsx` is duplicated into `Plan_v8.xlsx` and
edited. The watcher moves `Plan_v7.xlsx` into `financials/_archive/` and writes:

`financials/knowledge/concepts/plan-v7.md`

```md
---
type: excel-model
title: Operating plan (v7)
description: FY26 operating plan — superseded by v8.
resource: ../../_archive/Plan_v7.xlsx
status: superseded
superseded_by: ./plan-v8.md
tags: [plan, financials]
timestamp: 2026-06-30T12:00:00Z
---
# Operating plan (v7)

Tabs: `Assumptions`, `P&L`, `NRR`. **NRR included one-off credits** in the
retention numerator (see [decision](../decisions/nrr-excludes-one-off-credits.md)).
Replaced by [v8](./plan-v8.md).
```

`financials/knowledge/concepts/plan-v8.md`

```md
---
type: excel-model
title: Operating plan (v8)
description: FY26 operating plan — current.
resource: ../../Plan_v8.xlsx
status: active
supersedes: ./plan-v7.md
tags: [plan, financials]
timestamp: 2026-06-30T12:00:00Z
---
# Operating plan (v8)

Same tabs as [v7](./plan-v7.md). Change: **NRR now excludes one-off credits**
(see [decision](../decisions/nrr-excludes-one-off-credits.md)).
```

`financials/knowledge/decisions/nrr-excludes-one-off-credits.md`

```md
---
type: decision
title: NRR excludes one-off credits (v7 → v8)
description: Why the NRR formula changed between plan versions.
status: active
tags: [decision, adr, nrr]
timestamp: 2026-06-30T12:00:00Z
---
# NRR excludes one-off credits (v7 → v8)

We used to compute NRR **including** one-off credits ([v7](../concepts/plan-v7.md)).
From v8 we **exclude** them, because one-offs overstated retention in renewal
quarters. Inferred from the formula change in the `NRR` tab; confirm with the
last editor if the rationale matters. Applies to: [v8](../concepts/plan-v8.md).
```

`financials/knowledge/log.md` (append one line)

```
- 2026-06-30T12:00:00Z — superseded plan-v7 → plan-v8; archived Plan_v7.xlsx; drafted NRR decision (git: a.gonzalez)
```

Nothing was overwritten. The old description, the old artifact, and the reason
for the change all still exist.

---

## 5. Recover the old approach (a walkthrough)

Six months later someone asks: *"How did we use to calculate NRR, and why did we
change it?"* An agent recovers the full story from the docs alone:

1. Opens `financials/AGENTS.md` → follows the Knowledge down-pointer to
   `knowledge/index.md`.
2. Finds the active concept `plan-v8.md`; its `supersedes:` points to `plan-v7.md`.
3. Opens `plan-v7.md` (`status: superseded`). Its body says **NRR included one-off
   credits**, and its `resource:` resolves to `_archive/Plan_v7.xlsx` — so the agent
   can open the *actual old workbook* and read the old formula.
4. Follows the cross-link to the `type: decision` concept, which states **what
   changed and why** ("excluded one-offs because they overstated retention").

Git, Drive, and SharePoint version the **bytes**; this layer adds the readable
**story**. The agent recovers both the old artifact and its rationale without
anyone having memorized either.

---

## 6. Apply, restamp, and rewrite the snapshot

For every change, in the folder that owns it (these steps **are** the
"Keep this current" protocol that each AGENTS.md and concept already embeds — the
watcher just runs it automatically against detected changes):

1. **Update the co-located concept(s)** per §3/§4 — draft, supersede, restamp body,
   or deprecate. Touch the folder **AGENTS.md** only if rules/scope changed.
2. **Update `index.md`** if a concept was added, superseded, deprecated, or renamed
   (keep superseded/deprecated entries, marked).
3. **Append one line to `log.md`** (reverse-chronological, never rewrite past lines):
   `- 2026-06-30T12:00:00Z — <what changed> (<who / source>)`.
4. **Restamp `timestamp`** on every doc you touched (ISO-8601 UTC).
5. **Walk UP** only where the change actually matters — parent / root AGENTS.md or
   index — and restamp those too. If nothing upstream is affected, stop.
6. **Rewrite `.okf-state.json`**: set `generated` to now and replace `files[]` with
   the freshly scanned state, so the next run diffs against reality.

---

## 7. When the watcher cannot understand a change: ask the last editor

If reading the file does not make the change classifiable (ambiguous rename, a
deck whose intent is unclear, a schema change with no obvious meaning), **do not
guess.** Ask the person who last edited it.

**Attribution is source-dependent and must be stated honestly** — say where the
name came from, and admit when you cannot get one:

- **git-backed** → `git log -1 --format='%an <%ae>' -- <file>` (reliable author).
- **Drive / SharePoint** → the item's "last modified by" field from the source API.
- **plain filesystem** → the OS file owner (`stat`), which often names only an
  account, **not the human** who made the change.
- **fallback** → a configured **folder owner** when none of the above yields a
  person.

**Delivery is configurable** (pick per project): append the question to an
`ASKS.md` queue at the folder root, open a tracker issue, post to Slack, or send an
email. Default is `ASKS.md` because it needs no integration and lives next to the
docs. Each ask records the file, the detected change, what's unclear, the
attributed editor, and the attribution source — e.g.:

```
- [ ] 2026-06-30 — Plan_v8.xlsx: new tab "Scenario_C" with no header row.
      What does it represent? (last editor: a.gonzalez — source: git author)
```

Leave the change un-applied — or applied tentatively and flagged — until it is
answered, so the docs never assert something the watcher invented.

---

## 8. Autonomy: how the watcher runs on its own

The watcher is just an agent run; schedule it. In order of preference:

1. **Claude Code Routine (cloud, recommended).** Runs on Anthropic-managed
   infrastructure on a schedule — no local machine needed, survives laptops being
   off. Create it with the `/schedule` CLI command or the routines web UI
   (`claude.ai/code/routines`). Best for shared team folders.
2. **Desktop scheduled task (local).** Runs on the user's machine and survives
   restarts. Good when the artifacts only exist on that machine.
3. **Cron + headless CLI (local, scriptable).** A plain cron entry invoking
   `claude -p` with the prompt below. Simplest to reason about; depends on the
   machine being on.

(Note: `/loop` + in-session cron tools are **session-scoped** — they need an open
session and expire after 7 days — so they are not a substitute for a Routine for
truly autonomous, recurring work.)

A daily cadence is usually right for consulting folders; tighten to hourly for
fast-moving shared drives.

Example cron (local, headless):

```
# 07:30 every weekday — reconcile the docs for a project folder
30 7 * * 1-5  cd /path/to/project && claude -p "$(cat knowledge/watcher-prompt.txt)" >> knowledge/.watcher.log 2>&1
```

---

## 9. Daily-run agent prompt (copy-paste)

Save this as the routine's prompt (or `knowledge/watcher-prompt.txt`). It is
self-contained.

```
You are the reconciliation watcher for an OKF-documented folder tree. Work in
English internally; write any docs in the project's language; ask any questions
in the user's language. Do not invent facts. Append-only: never delete a concept,
never overwrite history.

GOAL: detect changes made to the real artifacts since the last run — by anyone,
through any tool — and bring the co-located docs back in sync.

1. LOCATE SNAPSHOTS. Find every knowledge/.okf-state.json under the tree. Treat
   each owning folder as a scope.

2. DETECT. For each scope, rebuild current file state (respect exclusions). Use
   the strongest backend available:
     - git: `git status --porcelain` plus
       `git log --since='<generated>' --name-status`; no commit SHA is stored, so
       anchor on the snapshot's `generated`;
     - else filesystem walk + sha256 per file;
     - else the source API's "modified since <generated>" (Drive/SharePoint).
   Diff vs .okf-state.json -> added / modified / deleted. Compare by sha256, not
   mtime (sync/re-save bumps mtime without changing bytes).

3. CLASSIFY by READING each changed artifact (bounded reads):
     - PDF: your agent's native PDF reader (e.g. Claude Code's Read tool with a
       page range), else `pdftotext -f <first> -l <last> file.pdf -`.
     - pptx/xlsx/docx: python-pptx/openpyxl/python-docx if present, else
       `unzip -p` the XML parts and strip tags.
     - legacy doc/ppt/xls: textutil (.doc on macOS) or
       `soffice --headless --convert-to txt|csv`.
     - big xlsx: read the <dimension> range + headers + ~20 sample rows only.
   Pick one class: data-refresh | new-version (v7->v8) | new-concept | structural
   | deletion.

4. APPLY per change, in the owning folder:
     - data-refresh -> restamp the concept timestamp only.
     - new-version -> APPEND-ONLY SUPERSEDE: keep the old concept, set its
       status: superseded + superseded_by -> new, and repoint its resource at the
       archived old file (move it into _archive/ or use source version history);
       draft a NEW concept for the new version with status: active + supersedes ->
       old; if you can infer WHY it changed, write a type: decision concept and
       cross-link both versions, else queue an ask. Never delete the old concept;
       never repoint a single concept onto the new file.
     - new-concept -> draft a concept (OKF frontmatter: type,title,description,
       resource,tags,timestamp + body) and add it to index.md.
     - structural -> edit the concept body (schema/abas/caveats), restamp.
     - deletion -> set the concept status: deprecated, annotate index.md, keep the
       concept; if the bytes are recoverable archive them and repoint resource, else
       drop the optional resource line (never leave it dangling) and note it is gone.
   Append one reverse-chronological line to log.md with timestamp, what changed,
   and who/source. Restamp every doc you touched. Walk UP to parent/root only
   where the change actually affects them. Change only what the edit touched.

5. WHEN UNSURE, ASK — never guess. Attribute the last editor honestly by source:
   git -> `git log -1 --format=%an -- <file>`; Drive/SharePoint -> "last modified
   by"; plain filesystem -> OS owner; else configured folder owner. STATE which
   source the name came from. Deliver via the configured channel (default: append
   to ASKS.md). Leave the change flagged, not silently applied.

6. REWRITE SNAPSHOT. Set generated=<now ISO-8601 UTC> and replace files[] with the
   freshly scanned {path,sha256,mtime,size}.

7. REPORT. Summarize: counts of added/modified/deleted, what you applied, what you
   queued as asks. Run the validate script if present and report PASS/FAIL.
```

---

## 10. Honest limits

State these plainly; they are why `timestamp` + the watcher exist in the first
place.

- **Plain filesystem may not reveal WHO.** OS ownership often names an account, not
  the human who edited; without git or a source "modified by", attribution falls
  back to a configured folder owner.
- **Non-git sources need their own change feed.** Drive/SharePoint/BigQuery
  reconciliation depends on those APIs exposing "modified by/at" and the watcher
  having read access. No access -> no detection.
- **The watcher needs read access** to the artifacts to classify changes;
  permission gaps degrade it to "something changed, please review."
- **Descriptions can drift from artifacts.** A concept is a pointer + description,
  deliberately separate from the artifact, so it can lag reality between runs. The
  `timestamp` tells you how fresh a description is, and the watcher shrinks the
  drift window — it does not eliminate it.
- **Classification is heuristic.** `v7 → v8` by filename, "same structure" by schema
  read, the *why* of a change by formula diff — confident cases auto-apply;
  ambiguous ones go to the ask queue rather than a wrong edit.

---

## 11. Agnostic by design — swap the runner, keep the brain

Everything above is **model- and agent-agnostic.** The reconciliation *logic* —
snapshot-diff detection, read-then-classify, append-only supersede, ask-the-last-
editor — has nothing Claude-specific in it. Codex, Gemini, a local Qwen / DeepSeek,
or any agent that can read files and run a shell does the same job. Only three
things are runtime-specific, and each swaps 1:1:

- **The runner.** `claude -p "<prompt>"` is one example. Replace it with any
  headless agent — `codex exec`, `gemini -p`, `qwen-code`, or your own API loop —
  in the same cron line. `scripts/arm-watcher.sh` takes `--runner`, so the binary
  is never hardcoded.
- **The scheduler.** A Claude Code Routine is one option; OS cron, a desktop task,
  GitHub Actions, or any cloud scheduler invoking your agent works identically.
- **PDF reading.** "the Read tool reads PDFs natively" is a Claude convenience; the
  agnostic fallback (`pdftotext`, or `unzip` the XML for Office) in §3 covers every
  other runtime. The other extractors (`unzip`, `python`, `textutil`, `soffice`)
  are plain shell — already agnostic.

The **docs** are agnostic too: `AGENTS.md` is the cross-agent canonical
(Codex / Cursor / Gemini read it natively); the one-line `CLAUDE.md` stub is just
the Claude Code bridge. For another harness that auto-loads its own file, add an
equivalent one-line stub pointing at `AGENTS.md` — same trick, different filename.
The reconciliation logic and the knowledge bundle never change.

