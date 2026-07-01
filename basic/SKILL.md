---
name: agent-friendly-docs-basic
description: The lite tier of agent-friendly-docs — scaffold AND maintain simple, human-readable agent docs for a folder tree, great for SharePoint/Drive folders organized by topic (assuntos, decks, spreadsheets, PDFs). Each meaningful folder gets a thin auto-loaded AGENTS.md router + a CLAUDE.md stub pointing to ONE index.md (the folder's knowledge, inline) plus an append-only log.md (history, since SharePoint has no git). Includes the reconciliation watcher for changes made outside Claude Code. No OKF concept bundle and no graph — escalate a folder to agent-friendly-docs-pro-max when it needs versioned concept history, cross-folder reuse, or a knowledge graph. Use when organizing document/topic folders simply and keeping them agent-navigable + self-updating. Triggers (English): "basic agent docs", "lite docs", "index.md per folder", "simple folder docs", "SharePoint docs". Triggers (Portuguese): "organizar pastinhas simples", "docs lite", "index.md por pasta", "deixar agent-friendly simples".
---

# Agent-Friendly Docs — Basic (lite+)

The simple sibling of **`agent-friendly-docs-pro-max`**. Same backbone — a thin, auto-loaded `AGENTS.md`
router per folder — but the folder's knowledge lives in **one `index.md`**, with history in an
**append-only `log.md`**. No concept bundle, no graph. Built for **non-technical, topic-organized folders**
(SharePoint / Drive: assuntos, decks, planilhas) where clarity beats machinery.

## Shape (per meaningful folder)

```
folder/
├── CLAUDE.md        # one line: @AGENTS.md  (the auto-load bridge)
├── AGENTS.md        # THIN router: rules + "detail -> ./index.md" + up-pointer + Keep-current
├── index.md         # the folder's knowledge (current state), inline
├── log.md           # APPEND-ONLY history: what changed & why (SharePoint has no git)
└── .okf-state.json  # (hidden) the watcher's snapshot
```

- **`CLAUDE.md` = `@AGENTS.md`** — Claude Code auto-loads `CLAUDE.md` (not `AGENTS.md`); the stub bridges,
  and `AGENTS.md`-native tools read it directly.
- **`AGENTS.md` = thin router** — rules / scope / what-not-to-touch; a DOWN pointer to `./index.md`; an
  UP pointer (`## If you opened only this folder` → `../AGENTS.md`); the `## Keep this current` protocol.
  It routes; it holds no content.
- **`index.md` = the knowledge** — what's in this folder, where the real artifacts live, definitions,
  caveats. One readable file a non-technical person can actually read and trust.
- **`log.md` = memory** — every real change appends one dated line (what + why + who). Append-only, so
  "what we used to do" is never overwritten. This is the **"+"** that pure lite drops.

## Discovery loop (interview ⇄ read)

Same as pro-max, just a simpler output. **Interview** (in the user's language: goals + what to SKIP) ⇄
**read** the content by default (PDF natively; `.pptx`/`.xlsx`/`.docx` via `python` or `unzip`) ⇄
**re-ask** sharper, evidence-based questions ⇄ **converge** → **propose** the tree → confirm → **BUILD**
(`AGENTS.md` + `index.md` + `log.md` per folder) → **verify** with a fresh-eyes agent → **arm the watcher**.
Agnostic to the starting state; **decompose, don't copy** a bloated `CLAUDE.md` into the router + `index.md`
(never dump the wall into `AGENTS.md`); preserve the original as a backup until the user validates.

## The watcher (its home turf)

For SharePoint / Drive folders edited **outside** Claude Code, arm the reconciliation watcher: it snapshots
the artifacts (`.okf-state.json`), diffs each run, classifies changes by reading them, then **updates the
relevant section of `index.md` and APPENDS a line to `log.md`** (never overwrites history), and asks the
last editor when it can't tell. Arm it in one command:
`bash scripts/arm-watcher.sh <tree> --install`. Full spec: [WATCHER.md](WATCHER.md).

## Validate

`python3 scripts/validate.py <tree>` checks the shape: `AGENTS.md` + `CLAUDE.md` present, the stub is exactly
`@AGENTS.md`, the router has its sections and points to `./index.md`, `index.md` and `log.md` present,
timestamps parse, the up-pointer exists. Templates: [TEMPLATES.md](TEMPLATES.md).

## When to escalate a folder to pro-max

Move a specific folder up to `agent-friendly-docs-pro-max` (OKF concept bundle + graph) when it has:
- **versioned artifacts with real history** worth linkable nodes (v6→v7→v8 + the "why");
- **knowledge reused across many folders** (one canonical definition linked everywhere);
- **too many artifacts** for a single `index.md`.

Otherwise, basic is the right, simpler default. Skill instructions stay English; the interview is in the
user's language; the docs are written in the project's language.
