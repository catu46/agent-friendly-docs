# agent-friendly-docs — basic (lite+)

A Claude Code skill for the folders you use to **organize and find** — where deliverables live
(decks, spreadsheets, PDFs, notes), usually filed by topic on SharePoint or Drive. Here the folder
is a **filing cabinet, a catalog — not a machine**: it stores things; nothing depends on it and it
doesn't evolve through versioned history. So its docs stay simple — one readable file that says
what's in the folder, plus a running log of what changed.

It is built for the real loop: walk into a folder, ask a question, the agent **reads the files,
knows how far to go, and helps** — and the docs feed themselves back, so tomorrow a fresh chat is
instantly smart again. The audience skews non-engineer (strategy consultants, managers, directors)
and the folders are *assuntos* / topic folders, so the docs route by reference and stay in plain,
human-readable prose.

This is the **lite+** sibling of **[`agent-friendly-docs-pro-max`](../README.md)** and a **strict
subset** of it — same backbone, less machinery. pro-max is for folders that are **infrastructure**
(a living knowledge graph of versioned, cross-linked concepts); basic is for folders that are
**storage**. The self-test you apply per folder: *does this folder just STORE things, or do things
DEPEND on it / does it EVOLVE with versioned history?* — store → basic; depend/evolve → escalate
that folder to pro-max.

---

## The lite+ shape (per meaningful folder)

Flat, not a bundle. Every meaningful folder gets exactly these files:

```
folder/
├── CLAUDE.md        # one line: @AGENTS.md  (the auto-load bridge)
├── AGENTS.md        # THIN router: Rules + "detail -> ./index.md" + up-pointer + Keep-current
├── index.md         # the folder's knowledge, inline (current state)
├── log.md           # APPEND-ONLY history (SharePoint has no git)
└── .okf-state.json  # (hidden) the watcher's snapshot
```

- **`CLAUDE.md` = `@AGENTS.md`** — Claude Code auto-loads `CLAUDE.md`, not `AGENTS.md`; this one-line
  stub bridges to the router (and AGENTS.md-native tools read it directly).
- **`AGENTS.md` = the thin router** — Rules / scope / what-not-to-touch, a DOWN pointer to
  `./index.md`, an UP pointer (`## If you opened only this folder` → `../AGENTS.md`), and the
  `## Keep this current` protocol. It routes; it holds no content.
- **`index.md` = the knowledge** — what's in this folder, where the real artifacts live, definitions,
  caveats. One file a non-technical person can actually read and trust.
- **`log.md` = memory** — every real change appends one dated line (what + why + who). Append-only,
  so "what we used to do" is never overwritten. This is the **"+"** that pure lite drops.
- **`.okf-state.json`** — the hidden per-file snapshot the watcher diffs against.

No `knowledge/` bundle, no per-concept files, no `status`/`supersede` frontmatter graph, no `graph.py`.
Templates for every file are in [TEMPLATES.md](TEMPLATES.md).

---

## How it works — the discovery loop

Same discovery loop as pro-max, just a simpler output. It runs as an alternating **interview ⇄ read**
loop, co-equal — not rigid phases. The **interview** (in the user's language) covers the goals, the
organization, and — required — *what to skip* (you decide what to exclude, not what to read). The
**reading** opens **content by default**, not just filenames: PDFs natively, modern
`.pptx/.xlsx/.docx` as ZIP+XML (via `python` or `unzip`). Reading reveals what *is*; you reveal what
*matters* — so it **re-asks** sharper, evidence-based questions and reads deeper until the picture
**converges**. Then it **proposes** the tree, confirms it, **builds** `AGENTS.md` + `index.md` +
`log.md` per folder, **verifies** with a fresh-eyes agent, and **arms the watcher**.

It's agnostic to the starting state. When you're slimming a bloated mega-`CLAUDE.md`, the rule is
**decompose, don't copy**: split the wall into the router (`AGENTS.md`) plus the knowledge
(`index.md`) — never dump it into `AGENTS.md` — and keep the original as a backup until you validate.

---

## The reconciliation watcher

This is the watcher's home turf: SharePoint / Drive folders edited **outside** Claude Code, where
there's **no git** — no commit log to diff against. Someone duplicates `Plan_v7.xlsx` into
`Plan_v8.xlsx`, drops a new deck in, refreshes numbers in place, or renames a file in Finder. A doc
system that only updates when someone runs Claude Code rots within a day.

Each run the watcher snapshots the real artifacts (`.okf-state.json`, compared by `sha256` — a cloud
sync can bump `mtime` without changing a byte), diffs against the last snapshot, and **classifies
each change by reading it**. Then it **updates the relevant section of `index.md`** (`What's here` /
`Definitions & assumptions` / `How to work here`) and **APPENDS one dated line to `log.md`** — never
overwriting history. When reading can't resolve a change, it doesn't guess: it asks the last editor
(attributed honestly per source) via an `ASKS.md` queue.

Arm it in one command — it's a bash script, and arming is the last step of the skill run:

```bash
bash scripts/arm-watcher.sh <tree> --install
```

That schedules the chosen runner (local cron, or a cloud Routine for shared team folders) against the
single prompt in `scripts/watcher-prompt.txt`. Full design spec, backends, and attribution: [WATCHER.md](WATCHER.md).

---

## Memory & history

Updates are **append-only / supersede — never destructive**. `index.md` always shows the *current*
state; `log.md` always shows *every* state that came before it. A `v7 → v8` supersede is four moves:

1. archive the old artifact into `_archive/` (or rely on the source's own version history);
2. repoint `index.md`'s **What's here** entry at the new file;
3. note the *why* under `index.md`'s **Decisions** section (short — the full timeline is `log.md`);
4. **append** one `log.md` line: old → new, the archive path, and who/source.

That's lite+'s stand-in for pro-max's per-concept `status`/`supersede` graph, collapsed onto one
file — so an agent (and a human) can always recover **what we used to do, and why**.

---

## Install & use

Full install (both tiers) lives in the **[monorepo README](../README.md)**. In short: clone the repo,
then symlink this folder as the skill —

```bash
ln -s <repo>/basic ~/.claude/skills/agent-friendly-docs-basic
```

Invoke `/agent-friendly-docs-basic`, or just ask in natural language — English or Portuguese
("organize this SharePoint folder to be agent-friendly, keep it simple" / "deixa essas pastinhas de
assuntos agent-friendly, versão lite"). Skill instructions and triggers are in [SKILL.md](SKILL.md).

---

## When to escalate a folder to pro-max

basic is the right, simpler default for topic/document folders. Move a **single folder** up to
[`agent-friendly-docs-pro-max`](../README.md) (OKF `knowledge/` bundle + concept graph + `graph.py`)
when it stops being just storage and starts being infrastructure:

- things **depend on it**, or it **evolves through versioned history** worth linkable, superseded
  nodes (`v6 → v7 → v8` + the "why" behind each jump);
- **definitions are reused across many folders** (one canonical definition linked everywhere, not
  copy-pasted);
- there are **too many artifacts** for a single `index.md` to stay readable.

You escalate per folder, not per tree — a lite+ folder and a pro-max folder can live side by side.

---

## Validate

A bundled shape-checker (Python 3, **stdlib only**, runs anywhere) enforces the lite+ shape:

```bash
python3 scripts/validate.py <tree>
```

It checks that `AGENTS.md` + `CLAUDE.md` are present, the stub is exactly `@AGENTS.md`, the router has
its sections and points to `./index.md`, `index.md` and `log.md` exist, timestamps parse, and the
up-pointer is there.

---

## Português

Funciona em português de ponta a ponta: a **entrevista** é conduzida no seu idioma e a
**documentação gerada** é escrita no idioma do projeto. (As instruções internas do skill permanecem
em inglês — só isso.) Use **basic** para pastas de assuntos / documentos (SharePoint, Drive, decks,
planilhas) que só **guardam** coisas.

---

## License

MIT — see [LICENSE](../LICENSE).
