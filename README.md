# agent-friendly-docs

One idea, two tiers: **agent-navigable, self-updating folder documentation**. Every meaningful
folder gets a thin, auto-loaded **`AGENTS.md` router** (bridged by a one-line **`CLAUDE.md`** stub,
since Claude Code auto-loads `CLAUDE.md`, not `AGENTS.md`) plus a **reconciliation watcher** that
keeps the docs honest even when people edit files *outside* Claude Code — duplicating an Excel
into `v8`, dropping a new deck into a folder, renaming things in Drive/SharePoint. The docs feed
themselves back (*se retroalimenta*), so a fresh chat tomorrow is instantly smart again.

This repo ships that idea as **two Claude Code skills** sharing the same backbone but different
weight:

```
folders-organizer/
├── pro-max/   agent-friendly-docs-pro-max   — full: OKF knowledge/ bundle + graph + watcher
└── basic/     agent-friendly-docs-basic     — lite+: index.md + log.md + watcher
```

---

## The two skills

### `pro-max` — full

For **code, complex domains, versioned history, cross-folder reuse, or a graph**. Per folder:
a thin `AGENTS.md` router pointing at a lazy `knowledge/` bundle — one file per concept
(frontmatter + body + cross-links), `status`/`supersedes` frontmatter so a `v7 → v8` swap keeps
the old concept (`status: superseded`) instead of erasing it, an append-only `log.md`, and
`scripts/graph.py` to render the whole `knowledge/` bundle as a self-contained interactive HTML
graph (concepts = nodes, `supersedes` = edges). See [`pro-max/README.md`](pro-max/README.md).

### `basic` — lite+

For **non-technical, topic-organized folders** — SharePoint / Drive folders of *assuntos*, decks,
spreadsheets, PDFs — where clarity beats machinery. Per folder: the same thin `AGENTS.md` router,
but the knowledge lives in **one `index.md`** (current state, inline) and history in an
**append-only `log.md`**. No `knowledge/` bundle, no concept files, no `status`/`supersede`
frontmatter graph, no `graph.py` — a strict subset of pro-max. See [`basic/SKILL.md`](basic/SKILL.md).

Both ship the identical backbone: `CLAUDE.md` (`@AGENTS.md` stub) + `AGENTS.md` (thin router,
never a content store) auto-loading per folder, the interview ⇄ read discovery loop, **decompose
— don't copy** when slimming a bloated `CLAUDE.md`, and reading file **content** by default (PDFs
natively, `.pptx/.xlsx/.docx` as ZIP+XML), not just filenames.

---

## Two independent dials

Don't conflate them — they're separate decisions:

1. **Structure: full vs lite+.** How rich does a folder's knowledge need to be — a graph of
   linked, versioned concepts (`pro-max`), or one readable `index.md` + an append-only `log.md`
   (`basic`)?
2. **Change-source: watcher on vs off.** Do files here change **outside** Claude Code — someone
   drops a new deck, duplicates a spreadsheet into `v8`, renames things in Drive/SharePoint — so
   a scheduled reconciliation run is worth arming? Or is this folder only ever touched inside
   Claude Code, where the in-session "Keep this current" step is already enough?

A folder can be lite+ with the watcher armed, full with no watcher, or any other combination —
pick each dial on its own merits, per folder.

---

## When to use which (and when to escalate)

Default to **`basic`** for topic/document folders (SharePoint, Drive, decks, spreadsheets, PDFs)
and **`pro-max`** for code or any domain with real versioned history, reused definitions, or a
graph worth visualizing. You don't have to pick once for the whole tree — **escalate a single
folder** from `basic` to `pro-max` when it grows:

- **versioned artifacts with real history** worth linkable, superseded nodes (`v6 → v7 → v8` +
  the "why" behind each jump);
- **knowledge reused across many folders** (one canonical definition linked everywhere, not
  copy-pasted);
- **too many artifacts** for a single `index.md` to stay readable.

Everything else, `basic` is the right, simpler default — clarity over machinery.

---

## Install

Clone the repo once, then symlink (or copy) whichever tier(s) you want into `~/.claude/skills/`:

```bash
git clone https://github.com/catu46/agent-friendly-docs ~/folders-organizer

# pro-max (full)
ln -s ~/folders-organizer/pro-max ~/.claude/skills/agent-friendly-docs-pro-max
# — or copy instead of symlink:
# cp -R ~/folders-organizer/pro-max ~/.claude/skills/agent-friendly-docs-pro-max

# basic (lite+)
ln -s ~/folders-organizer/basic ~/.claude/skills/agent-friendly-docs-basic
# — or copy instead of symlink:
# cp -R ~/folders-organizer/basic ~/.claude/skills/agent-friendly-docs-basic
```

Install either one alone, or both — they don't conflict; you choose per project (and per folder)
which tier applies. Invoke explicitly (`/agent-friendly-docs-pro-max`, `/agent-friendly-docs-basic`)
or just ask in natural language — English or Portuguese; see each skill's own README/SKILL.md for
trigger phrases.

---

## Português

Os dois skills funcionam em português de ponta a ponta: a **entrevista** é conduzida no seu
idioma e a **documentação gerada** é escrita no idioma do projeto (as instruções internas do
skill permanecem em inglês). Use **`basic`** para pastas de assuntos/documentos (SharePoint,
Drive, decks, planilhas) e **`pro-max`** para código ou domínios com histórico versionado,
reaproveitamento de definições entre pastas, ou que valem um grafo.

---

## OKF and honesty

`pro-max`'s `knowledge/` bundle follows the **Open Knowledge Format (OKF) v0.1**, announced
June 12, 2026 by Google Cloud. Lock-in is near-zero: an OKF concept is just a markdown file with
one required `type` field (plus `title`, `description`, `resource`, `status`, `supersedes`/
`superseded_by`, `tags`, `timestamp`) — readable and portable with or without any tool. Auto-load
is a **harness** feature tied to the filenames `CLAUDE.md` / `AGENTS.md`, not to OKF: Claude Code
reads `CLAUDE.md` (walking up from the cwd), not `AGENTS.md` — the one-line `@AGENTS.md` stub is
what bridges to the router (AGENTS.md-native tools read it directly). Nothing beyond that
filename convention is required to read or reuse these docs.

---

## License

MIT — see [LICENSE](./LICENSE).
