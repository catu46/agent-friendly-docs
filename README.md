# agent-friendly-docs

A Claude Code / cross-agent **skill** that scaffolds an agent-friendly documentation architecture for
any folder tree — code or documents (decks, spreadsheets, PDFs, datasets, assets) — and keeps it from
going stale.

It produces `AGENTS.md` as the canonical, cross-agent source of truth (the [agents.md](https://agents.md)
standard) with a one-line `CLAUDE.md` stub so Claude Code auto-loads it. Every meaningful folder gets
its own self-contained doc, so you can open *just that folder* and your agent still has full context.

## What it produces

```
project/
├── AGENTS.md        # mother: overview + repository map (routing) + keep-current rule
├── CLAUDE.md        # one line: @AGENTS.md
├── module-a/
│   ├── AGENTS.md    # self-contained folder doc + keep-current rule (points upward)
│   └── CLAUDE.md    # @AGENTS.md
└── module-b/
    ├── AGENTS.md
    └── CLAUDE.md
```

- **`AGENTS.md` is canonical** — read natively by Codex, Cursor, Copilot, Gemini, etc.
- **`CLAUDE.md` is a stub** (`@AGENTS.md`) — Claude Code only auto-loads `CLAUDE.md`, so the stub
  bridges it. No content duplication, no symlinks.
- **Self-updating** — every doc ends with a "Keep this current" rule that tells the agent to refresh
  the folder's doc after real changes and propagate up to the parent/root *only where needed*.

It works for **non-code folders** too — it reads the actual content by default (PDFs natively;
`.pptx` / `.xlsx` / `.docx` via `python` or `unzip`), and uses the interview to decide which files to
*skip*.

## How it works

1. **Interview** (in your language) — understands the project and the folder organization that fits
   your mental model. No code is touched yet.
2. **Explore & build** — maps the real code, asks clarifying questions, proposes the tree, confirms,
   then writes everything and wires the links.

## Install

Clone straight into your Claude Code skills directory:

```bash
git clone https://github.com/catu46/agent-friendly-docs.git ~/.claude/skills/agent-friendly-docs
```

That's it — Claude Code picks up the skill automatically. (Only `SKILL.md` and `TEMPLATES.md` matter;
this README and the license just ride along in the same folder.)

To update later:

```bash
git -C ~/.claude/skills/agent-friendly-docs pull
```

## Use

In any project, run:

```
/agent-friendly-docs
```

…or just ask in natural language — e.g. "organize my folders to be agent-friendly", or in Portuguese
"organiza minhas pastinhas e deixa agent-friendly".

## Português

A skill funciona em português: a **entrevista e todas as perguntas acontecem no seu idioma**, e os
docs são escritos no idioma do projeto. As instruções internas da skill ficam em inglês (padrão), o
que não afeta a conversa com você.

## License

MIT — see [LICENSE](LICENSE).
