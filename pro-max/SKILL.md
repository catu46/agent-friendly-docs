---
name: agent-friendly-docs-pro-max
description: The FULL/PRO tier (lite sibling: agent-friendly-docs-basic). For folders that are INFRASTRUCTURE — parts of a system that depend on each other, evolve through versions, and share definitions (code modules, operational models); the folder is wired into a machine, not just storage. Scaffold AND maintain an agent-navigable documentation architecture (a living knowledge graph) for any folder tree — code or documents (slide decks, spreadsheets, PDFs, SQL, HTML/dashboards, datasets, assets, or a mix). Produces a thin router AGENTS.md + a CLAUDE.md import stub in every meaningful folder (each self-contained, so any folder can be opened in isolation by an AI agent) backed by a lazy OKF knowledge/ bundle, and a reconciliation watcher that keeps the docs honest even when non-engineers edit files OUTSIDE Claude Code (duplicating an Excel into v8, dropping a new deck into a folder, renaming in Drive/SharePoint). Every doc embeds a self-updating, append-only protocol so context never goes stale and you can always recover "what we used to do, and why". Use when a folder is INFRASTRUCTURE (things depend on it, it evolves through versions, definitions are reused across folders) — a codebase, or a versioned document system such as operational models or versioned spreadsheets/SQL — building a "mother" index that routes to per-folder docs, slimming a bloated CLAUDE.md into a router, wiring a knowledge graph, or setting up the watcher. For a plain topic/deliverable folder you just STORE and FIND in (a filing cabinet, no versioned history), use agent-friendly-docs-basic instead. Triggers (English): "knowledge graph for a folder tree", "living knowledge graph", "versioned concept history", "cross-folder reuse", "mother CLAUDE.md", "slim a bloated CLAUDE.md into a router", "reconciliation watcher", "AGENTS.md". Triggers (Portuguese): "grafo de conhecimento das pastas", "organizar pastinhas de código/infraestrutura", "histórico de conceitos versionado", "CLAUDE.md mãe", "watcher de reconciliação".
---

# Agent-Friendly Docs

Scaffold and maintain documentation any AI agent can navigate. The north-star loop: walk into a
folder, ask a question, the agent **reads the files**, knows *how far to go*, helps — and the docs
**feed themselves back** (*se retroalimenta*), so tomorrow a fresh chat is instantly smart again.

The audience skews non-engineer (strategy consultants, managers, directors) who often change files
outside any IDE/git/Claude Code. So the docs **route by reference** instead of dumping everything
into context, and a watcher reconciles them on a schedule. Skill instructions stay in English; the
**docs are written in the project's language**; the **interview is conducted in the user's language**.

## Survey and adapt — do NOT classify into modes

There are **no named modes** and **no "detect the mode" step.** The TARGET architecture (below) and the
discovery loop are invariant. Whatever you find — nothing, thin docs, or folders full of `.md` with a
bloated mega-`CLAUDE.md` — you apply the **same** architecture; only the ratio of create-vs-reorganize
shifts, and that is self-evident from what you read.

The one non-obvious rule: **DECOMPOSE, DON'T COPY.** When existing docs are bloated, route each chunk to
its layer instead of dumping the wall into `AGENTS.md`:

- a **RULE / scope / what-not-to-touch** → the thin `AGENTS.md` router;
- a **DEFINITION / reference / data-dictionary** → an OKF concept under `knowledge/`;
- an **OLD / replaced** thing → a `superseded` concept + a `log.md` line (keep it);
- a **STALE** claim → ask "still true?" and archive.

Never dump the whole wall into `AGENTS.md`. **Preserve everything (supersede, don't delete);** keep the
ORIGINAL file as a backup (and in git) until the user validates the new tree.

## The architecture (hybrid — final)

- **`CLAUDE.md`** = one-line stub `@AGENTS.md`. The only auto-load bridge besides `AGENTS.md`.
- **`AGENTS.md`** = the THIN front door, a **ROUTER, not a content store**. Holds ONLY: (a) **Rules** —
  how to act, scope / how far to go, what NOT to touch; (b) a lazy **DOWN pointer** into the bundle
  (`Detailed knowledge → ./knowledge/index.md ; open the concept you need`); (c) an **UP pointer**,
  `## If you opened only this folder → ../AGENTS.md`; (d) the **Keep this current** protocol. It does
  NOT hold definitions and does NOT hold the full map.
- **`knowledge/`** = OKF v0.1 bundle, lazy, opened on demand:
  - `index.md` — the navigable **MAP** (what concepts/subfolders exist here);
  - **concept files** — DEFINITIONS. OKF frontmatter (required `type` + `title` + `timestamp`; plus
    `description`, `resource`, `status`/`supersedes`/`superseded_by`, `tags`), a markdown body (meaning /
    schema / abas / caveats), and
    cross-links to other concepts. **The file PATH is the concept's ID.** `resource` points at the
    REAL artifact (relative path to the `.xlsx`/`.pptx`/`.sql`, or a SharePoint/Drive/BigQuery URL) —
    the concept is a **pointer + description, separate from the artifact**;
  - `log.md` — APPEND-ONLY reverse-chronological change history.
- **Every meaningful folder** gets its own thin `AGENTS.md` + `CLAUDE.md` stub, self-contained. The root
  `AGENTS.md` is the *mother* front door.

Exact shapes and copy-paste blocks: [TEMPLATES.md](TEMPLATES.md).

## Split by LOAD-TIMING, not by category

- **Always-needed + small** (rules, scope, pointers) → `AGENTS.md`, **eager / auto-loaded**.
- **Sometimes-needed + large** (the map, the definitions, the history) → `knowledge/`, **lazy, on demand**.
- **`@import`** (the `@path` syntax in `CLAUDE.md`) is **eager** — it pulls the whole file into context at
  load (recursively, up to four hops). Use it ONLY for a tiny always-needed core (e.g. a short shared
  glossary). **Never `@import` the bundle** — that re-bloats context. The payoff: a per-folder
  mega-`CLAUDE.md` (loaded eagerly every chat = token bloat) becomes a ~15-line router that loads almost
  nothing eagerly and pulls detail on demand.

## Opened-in-isolation reality (why the up-pointer)

Auto-load is the harness's job and is **filename-based**. Claude Code walks **up** the `CLAUDE.md`
ancestor chain (cwd up to home) — and each `CLAUDE.md` imports its folder's `@AGENTS.md` — so opening a
SUBfolder still loads its ancestors' routers including the mother's. (It reads `CLAUDE.md`, not `AGENTS.md`
directly — the stub is the bridge.) But **other tools (Copilot/Cursor/etc.) often scope only to the opened workspace
root** and do not read above it. That is why every folder's `AGENTS.md` carries an explicit
`## If you opened only this folder` section pointing to `../AGENTS.md` — the folder stays useful when
opened alone (it works as long as the agent can read `../`). "Understand the whole context" means *follow
the references* (down to local OKF, up to the parent), NOT load everything.

## Memory and history — keep current AND keep history

The self-update protocol is **APPEND-ONLY / SUPERSEDE, never destructive.** Distinguish current-state
(active concepts) from memory (history):

- Concept frontmatter carries `status: active|superseded|deprecated`, plus `supersedes:` /
  `superseded_by:` (relative paths).
- When an artifact is replaced (**v7 → v8**): KEEP v7's concept, set `status: superseded` +
  `superseded_by → v8`, and repoint its `resource` at the **archived** old file (e.g.
  `./_archive/...v7.xlsx`, or the source's version history). Set v8 `status: active` + `supersedes → v7`.
  Append a `log.md` line. **Never delete the old concept.**
- A **`type: decision`** concept is a lightweight ADR capturing the WHY ("we used to compute NRR including
  X; changed to exclude it in Q2 because Y").
- **Recover use-case:** an agent finds the superseded concept → follows `resource` to the archived
  artifact + reads the linked decision → recovers the old approach AND its rationale. Honesty: git / Drive
  / SharePoint version the **bytes**; this layer adds the readable **story**.

## Works for any folder — read content by default

This applies to code **and** to document folders. The architecture is identical; only the reading
changes — and you *can* open these files, so **read the content by default, not just filenames.** The
interview decides what to **skip**, not what to open.

- **PDF** — the Read tool reads PDFs natively via the `pages` range (max 20 pages/request; a range is
  **required** above 10 pages).
- **Modern `.pptx` / `.xlsx` / `.docx`** are ZIP+XML. Cleanest: `python-pptx` / `openpyxl` /
  `python-docx` (third-party — `pip install` if missing). Zero-install fallback:
  `unzip -p file.xlsx xl/sharedStrings.xml`, `unzip -p file.pptx ppt/slides/slide1.xml`,
  `unzip -p file.docx word/document.xml`, then strip tags (iterate all parts; `sharedStrings.xml` is the
  string *pool*, cell→string mapping lives in `xl/worksheets/sheetN.xml` — the libraries reconstruct it).
- **Legacy `.doc` / `.ppt` / `.xls`** are binary, not ZIP. On macOS `.doc` has a zero-install path:
  `textutil -convert txt old.doc`. `.ppt` / `.xls` need LibreOffice headless:
  `soffice --headless --convert-to txt|csv file.ppt`. (pandoc cannot read legacy binary Office files.)
- **Big spreadsheets** — never dump every cell. Read the used range cheaply, then headers + dtypes + ~20
  sample rows (`openpyxl` `read_only=True`, bounded `iter_rows`).

## The discovery loop (interview ⇄ read — co-equal, alternating)

Understanding a real, messy tree is **iterative, not linear phases.** The interview and the reading are
**co-equal and alternate** — neither is subordinate. Reading reveals WHAT IS; the human reveals WHAT
MATTERS and WHAT'S STILL TRUE.

1. **Interview** (in the user's language): goals, what to **SKIP** (required exclusion step), what's
   stale. Group questions; don't interrogate forever.
2. **Read**: survey the tree, then read the **content** the answers point to — by default.
3. **Re-interview**, sharper and evidence-based: *"you said the Q3 model is canonical, but there's v8,
   v8_FINAL, v8_FINAL_real — which? this CLAUDE.md claims X but the data shows Y — stale?"*
4. **Read deeper** → … **converge.** Usually 2–3 rounds (more for messy trees). **Stop** when reading
   stops surprising and the human confirms the picture.
5. Then **propose** the tree, **confirm**, and **BUILD**: write `AGENTS.md` + `knowledge/`, wire links,
   embed the self-update protocol, and write `knowledge/.okf-state.json`.
6. **Verify with fresh eyes** — the acceptance test that closes the loop. **Deploy a subagent carrying
   none of this conversation's context**, rooted at the built tree (or a representative folder), as if a
   brand-new agent just opened the repo. Have it, using ONLY the docs: (a) state what this folder/project
   is and how it would do a representative task; (b) flag anything it could **not** determine. Whatever
   the cold agent stumbles on is a **real gap** → fix the docs and re-verify. This proves the north-star
   loop empirically: *a fresh chat gets oriented from the docs alone.* At scale, point the fresh agent at
   a sample of folders (incl. one opened **in isolation**, to test the up-pointer). `validate.py` checks
   the **shape**; this checks **comprehension** — ship only when both pass.
7. **Arm the watcher** — the last step of the task. Once the tree passes shape + comprehension, the docs
   are built but static; arm the daily reconciliation so they self-feed from day one. Run
   `scripts/arm-watcher.sh <tree> --install` (runner-agnostic via `--runner`), choosing the backend for
   the project's source — **git / Google Drive / SharePoint / plain folder** (see
   [WATCHER.md](WATCHER.md) §8 + §11 and the README's per-source table). **Confirm before installing a
   scheduled job:** it is a recurring system change, and API-backed sources (Drive/Graph) need
   credentials and usually a cloud Routine rather than a local cron.

**At scale (hundreds of folders), DECENTRALIZE:** one subagent per leaf folder reads its files and writes
that folder's docs; roll summaries **leaf → mid → root** so no context ever holds the whole tree.

**Keep this current** (embedded in every `AGENTS.md` and concept): after real changes, update this
folder's doc + APPEND to `log.md` + restamp `timestamp`; SUPERSEDE (never delete) anything replaced; then
walk UP to parent/root **only where the change actually affects them**. Change only what the edit touched.

## The reconciliation watcher

How the docs self-feed when people edit **outside** Claude Code: a snapshot in `knowledge/.okf-state.json`
records `{path, sha256, mtime, size}`; each run scans the filesystem (and/or `git diff`, and/or a source
API's "modified by/at") and diffs against it to find added/modified/deleted files — **independent of how
or who edited.** It classifies each change by reading the file (data-refresh → restamp; v7→v8 → supersede;
new artifact → draft a concept; schema change → update the body; deletion → mark deprecated), applies the
update append-only, and rewrites the snapshot. If it cannot understand a change it does **not guess** — it
asks the **last editor** (attributed honestly per source) via a configurable channel. It runs on a
schedule (a Claude Code routine in the cloud, or a local cron invoking `claude -p`). Full spec and the
copy-paste agent prompt: **[WATCHER.md](WATCHER.md).**

## Honesty notes (state these plainly)

- **OKF is v0.1** (announced June 12, 2026 by Google Cloud). Near-zero lock-in — it is just markdown +
  one required `type` field.
- **Auto-load is a harness feature tied to the filenames `CLAUDE.md` / `AGENTS.md`, not to OKF.** Claude
  Code reads `CLAUDE.md` (walking cwd up the tree), **not `AGENTS.md`** — the `@AGENTS.md` stub bridges
  it (AGENTS.md-native tools read it directly). `index.md` and concept files **do not auto-load** — they
  are opened on demand. That lazy boundary is the whole point.
- **Descriptions can drift** from the artifacts they point at — which is exactly why every doc carries a
  `timestamp` and why the watcher exists. Plain-filesystem edits may not reveal *who*; non-git sources need
  their own "modified by"; the watcher needs read access.

## Validate

A bundled **[scripts/validate.py](scripts/validate.py)** (Python 3, **stdlib only**, runs anywhere)
enforces the shapes: both `AGENTS.md` + `CLAUDE.md` present, the stub is exactly `@AGENTS.md`, required
frontmatter keys, links and `resource:` paths resolve, `knowledge/` has an `index.md`, timestamps parse,
`status` and supersede pointers are valid — failing on errors and listing warnings. Run it after building
and after every watcher pass. It is the **shape** half of acceptance; pair it with the **fresh-eyes**
comprehension check (loop step 6) before declaring a tree done.

It skips dotfiles and common build/dependency dirs (`node_modules`, `venv`, `env`, `*.egg-info`, `dist`,
`build`, `vendor`, …) so a Python/JS project's deps don't flood it with errors. To exclude anything else —
folders you deliberately don't document (client inputs, old versions) — drop a **`.okfignore`** at the tree
root, one glob per line (`#` comments allowed). The lite+ `validate.py` honors the same file.

## Visualize (optional)

`scripts/graph.py` turns any `knowledge/` bundle into a **self-contained interactive graph**:
`python3 scripts/graph.py <tree>` writes `knowledge-graph.html` (nodes = docs, edges = cross-links +
`supersedes`; colored by `type`, superseded faded, click a node to open it). You never hand-edit the HTML —
it is **generated**, so re-running the script (or letting the **watcher / "Keep this current" step** call
it) keeps the visual tree in sync with the docs. The graph data is embedded (nothing about your content
leaves the page); the render library loads from a CDN, or pass `--vendor <path>` for a fully offline file.
The graph shines in the OKF-bundle shape; a single-`index.md` folder has little to interconnect.
