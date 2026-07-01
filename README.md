# agent-friendly-docs

A Claude Code skill that **scaffolds AND maintains** agent-navigable documentation
for any folder tree — code *or* documents (PowerPoint, Excel, SQL, HTML/dashboards,
PDFs, datasets). The docs are [OKF](#okf-and-honesty)-conformant, **self-updating**,
and shipped with a **reconciliation watcher** that keeps them honest even when people
edit files *outside* Claude Code (duplicating an Excel into `v8`, dropping a new deck
into a folder, renaming things in Drive/SharePoint).

It is built for the real loop: walk into a folder, ask a question, the agent reads the
files, knows *how far to go*, helps — and the docs feed themselves back (*se retroalimenta*),
so tomorrow a fresh chat is instantly smart again.

The audience skews non-engineer (strategy consultants, managers, directors), so the
docs route by reference instead of dumping everything into context.

---

## What it produces

A thin, eager **front door** in every meaningful folder, plus a lazy **knowledge bundle**
that is opened only on demand:

```
your-folder/
├── CLAUDE.md                  # one-line stub: @AGENTS.md  (the only auto-load bridge)
├── AGENTS.md                  # THIN router: Rules + pointers (loaded via the CLAUDE.md stub)
├── knowledge/                 # OKF v0.1 bundle — lazy, opened concept-by-concept
│   ├── index.md               #   the navigable MAP (what concepts/subfolders exist here)
│   ├── <concept>.md           #   a DEFINITION (frontmatter + body + cross-links); PATH = its ID
│   ├── <decision>.md          #   type: decision — a lightweight ADR capturing WHY
│   ├── log.md                 #   APPEND-ONLY reverse-chronological change history
│   ├── .okf-state.json        #   per-file snapshot the watcher diffs against
│   └── _archive/              #   superseded artifacts (e.g. model_v7.xlsx) kept for recall
└── subfolder/                 # every meaningful subfolder is self-contained:
    ├── CLAUDE.md              #   open it alone and its context still auto-loads
    ├── AGENTS.md              #   (carries its own "If you opened only this folder" up-pointer)
    └── knowledge/ ...         #   its own lazy OKF bundle
```

**The split is by load-timing, not by topic.** Always-needed and small (rules, scope,
pointers) lives in `AGENTS.md` and loads eagerly (pulled into context by the `CLAUDE.md`
stub). Sometimes-needed and large (the map, the definitions, the history) lives in
`knowledge/` and is opened lazily. The root `AGENTS.md` is the *mother* front door; each
folder's `AGENTS.md` carries an explicit **"If you opened only this folder"** up-pointer to
`../AGENTS.md`, so the folder stays useful even in tools (Copilot, Cursor) that scope to the
opened root and never read upward.

`AGENTS.md` is a **router, not a content store**: it holds the rules, a down-pointer into
`knowledge/index.md`, an up-pointer to the parent, and the "Keep this current" protocol —
never the definitions and never the full map.

---

## How it works — a discovery loop

There are **no named modes** and no "detect the mode" step. Whatever you have — nothing, thin
docs, or folders full of `.md` behind a bloated mega-`CLAUDE.md` — gets the **same** target
architecture; only the ratio of create-vs-reorganize shifts, and that is self-evident from what
the skill reads.

It runs as an **alternating interview ⇄ read loop**, co-equal — not rigid phases. The
**interview** (in your language) covers the goals and the organization and — required — asks
*what to skip* (it decides what to exclude, not what to read). The **reading** opens file
**content by default** (not just filenames): PDFs natively, modern `.pptx/.xlsx/.docx` as
ZIP+XML, big spreadsheets as headers + structure + a sample of rows. Reading reveals what *is*;
you reveal what *matters* and what's *still true* — so the skill re-interviews against the
evidence ("you said the Q3 model is canonical, but there's a `v8_FINAL_real` — which?") and
reads deeper until the picture converges. Then it proposes a tree, confirms it, and writes the
`AGENTS.md` / `knowledge/` scaffold, wires the cross-links, and embeds the self-update protocol
in every doc. At scale (hundreds of folders) it decentralizes: one subagent per leaf folder,
rolling summaries leaf → mid → root.

---

## The reconciliation watcher

People change files without git, without an IDE, without Claude Code — so detection cannot
depend on anyone using Claude Code. On each run the watcher takes a filesystem snapshot
(`knowledge/.okf-state.json` records `{path, sha256, mtime, size}`) and diffs it against the
last run — optionally cross-checked with `git diff` or a source API's "modified by/at" for
Drive/SharePoint — to find added, modified, and deleted files regardless of *how* or *who*
edited them. It then **classifies each change by reading the changed file** (data-refresh →
just restamp; `v7→v8` → supersede the old concept and keep it; new artifact → draft a concept;
schema/abas changed → update the body; deletion → mark deprecated, never erase), applies the
update append-only, and rewrites the snapshot. If it cannot understand a change it does **not
guess** — it asks the *last editor* (attributed honestly per source: `git log -1 --format=%an`,
Drive/SharePoint "last modified by", or the OS owner / a configured folder owner) via an
`ASKS.md` queue, an issue, Slack, or email. It runs on a schedule — a Claude Code routine in
the cloud, or a local cron invoking `claude -p`.

### Arming the daily run (per source)

Arming the watcher is the **last step of the skill run**: once the tree is built and verified,
one command schedules the daily reconciliation so the docs self-feed from day one.

```bash
~/.claude/skills/agent-friendly-docs/scripts/arm-watcher.sh "<your-tree>" --install
# --runner "claude -p"  (default; or "codex exec", "gemini -p", an API loop)
# --cron   "30 7 * * 1-5"  (default: 07:30 on weekdays)
```

It drops `knowledge/watcher-prompt.txt` into the tree and adds the cron line. Runner- and
source-agnostic — pick the backend for where the files actually live:

| Source | Detection | How to arm | Attribution |
|---|---|---|---|
| **git** | `git status` + `git log --since` (else sha256 walk) | local cron, **or** a cloud Routine on the repo | `git log` author — reliable |
| **Google Drive** | synced folder → filesystem; or Drive **API / MCP** "modified since" | **synced** (Drive for desktop): local cron on the synced path. **API/MCP:** a cloud Routine (or self-hosted MCP) with Drive access | synced → OS owner (weak); API/MCP → real "last modified by" |
| **SharePoint / OneDrive** | synced folder → filesystem; or Microsoft Graph "modified since" | **synced** (OneDrive client): local cron on the synced path. **Graph:** cloud Routine + an app registration | synced → OS owner (weak); Graph → "last modified by" |
| **Plain / network folder** | sha256 filesystem walk | local cron | OS owner, else a configured folder owner |

Three honest rules of thumb:

- **Synced locally = works today, zero API.** The watcher is just a local cron on the synced
  path; the only loss is *who* edited (OS owner, not the human).
- **Want real "modified by", or a run that doesn't depend on your laptop?** Use the source's
  API (git author / Drive / Graph). That needs credentials or an app registration — and note
  that interactively-authenticated connectors can be **absent in a headless `claude -p` cron**,
  so API-backed runs usually mean a cloud **Routine**, not local cron.
- **A Google Drive (or SharePoint) MCP is the cleanest cloud backend** — `list`/`search` for the
  diff, `get metadata` for real *"modified by"*, `read`/`export` to classify native Google
  Docs/Sheets/Slides, all with no app registration. Same caveat: a claude.ai-style connector is
  **session-bound**, so a plain `claude -p` cron won't have it — run it where the connector lives
  (a Routine) or via a **self-hosted MCP with a service account** any runner can use.

---

## Memory and history

Updates are **append-only / supersede — never destructive**. When `v7` becomes `v8`, the old
concept is *kept* (`status: superseded`, `superseded_by:` the new one, `resource:` pointed at
the archived `_archive/...v7.xlsx`), the new one is marked `status: active` + `supersedes:`,
a `decision` concept records *why*, and `log.md` gets one more line. So an agent can always
recover **what you used to do, and why** — git and Drive version the bytes; this layer adds
the readable story.

---

## Visualize

Because the `knowledge/` bundle is already a graph (concepts = nodes; cross-links and `supersedes` =
edges), `scripts/graph.py` renders it as a **self-contained interactive HTML** — Obsidian-style, colored
by type, superseded nodes faded, click to open:

```bash
python3 ~/.claude/skills/agent-friendly-docs/scripts/graph.py "<your-tree>"
# writes <your-tree>/knowledge-graph.html
```

You never edit the HTML — it is generated, so the watcher (or the "Keep this current" step) regenerates it
and the visual tree tracks the docs. The graph data is embedded so nothing about your content leaves the
page; the render library loads from a CDN, or use `--vendor <path>` for a fully offline file.

---

## Install

```bash
git clone https://github.com/catu46/agent-friendly-docs ~/.claude/skills/agent-friendly-docs
```

(Or drop the folder into `~/.claude/skills/`.)

## Use

Invoke it explicitly, or just ask in natural language — English or Portuguese:

```
/agent-friendly-docs
```

> "organize these folders to be agent-friendly"
> "build a mother CLAUDE.md that routes to per-folder docs"
> "deixa essas pastinhas agent-friendly"
> "monta o CLAUDE.md mãe e a documentação pros agentes"

### Português

Funciona em português de ponta a ponta: a **entrevista** é conduzida no seu idioma e a
**documentação gerada** é escrita no idioma do projeto. (As instruções internas do skill
permanecem em inglês — só isso.)

---

## OKF and honesty

The `knowledge/` bundle follows the **Open Knowledge Format (OKF) v0.1**, announced
**June 12, 2026** by Google Cloud. Lock-in is near-zero: an OKF concept is just a markdown
file with one required `type` field (plus `title`, `description`, `resource`, `status`,
`supersedes`/`superseded_by`, `tags`, `timestamp`) — readable and portable with or without any tool.

A few things stated plainly:

- **Auto-load is a *harness* feature tied to the filenames `CLAUDE.md` / `AGENTS.md`, not to
  OKF.** Claude Code reads `CLAUDE.md` (walking from the cwd up the directory tree), **not
  `AGENTS.md`** — the one-line `@AGENTS.md` stub is what bridges to the front door (and
  AGENTS.md-native tools read it directly). `index.md` and the concept files do **not**
  auto-load — they are opened on demand. That lazy boundary is the whole point.
- `@import` (the `@path` syntax in `CLAUDE.md`) is **eager** — it pulls the whole file into
  context at load (recursively, up to four hops deep). Use it only for a tiny always-needed
  core (e.g. a short shared glossary). Never `@import` the knowledge bundle, or you re-bloat
  context.
- Descriptions can drift from the artifacts they point at — which is exactly why every doc
  carries a `timestamp` and why the watcher exists. Plain-filesystem edits may not reveal
  *who* changed a file; non-git sources need their own "modified by"; the watcher needs read
  access. Stated up front so nothing is overpromised.

A bundled `validate.py` (Python 3, **stdlib only**, runs anywhere) enforces the shapes:
both `AGENTS.md` + `CLAUDE.md` present, the stub is exactly `@AGENTS.md`, required frontmatter
keys, links and `resource:` paths resolve, `knowledge/` has an `index.md`, timestamps parse,
`status` and supersede pointers are valid — failing on errors and listing warnings.

---

## License

MIT — see [LICENSE](./LICENSE).
