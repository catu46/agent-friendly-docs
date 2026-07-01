# Templates — Basic (lite+)

Write docs in the **project's language**. Replace every `<placeholder>`. Timestamps are ISO-8601 UTC.
The `## If you opened only this folder` and `## Keep this current` sections are **mandatory** in every
`AGENTS.md`. Outer fences are `~~~` so nested ``` blocks render.

## 1. `AGENTS.md` (the thin router — root and every folder)

~~~md
---
type: agent-guide
title: <Folder name>
description: <one line: what this folder is for>
resource: .
tags: [<tag>, <tag>]
timestamp: 2026-07-01T12:00:00Z
---

# <Folder name>

## Rules
- Scope: <what this folder is responsible for; how far to go>.
- Do NOT touch: <what's off-limits — client inputs, other folders, sent deliverables>.

## Knowledge
This folder's knowledge → [`./index.md`](./index.md). History → [`./log.md`](./log.md).

## If you opened only this folder
Global rules and the parent map → [`../AGENTS.md`](../AGENTS.md). Read it before acting if it isn't
already in context. (At the repo root, drop this section.)

## Keep this current
After changing anything here, before you finish: update the relevant part of `index.md`, **append** one
line to `log.md`, and restamp `timestamp`. **Never overwrite history** (log is append-only; supersede,
don't delete). Then walk up to `../AGENTS.md` only if the change affects global rules or the map.
~~~

## 2. `CLAUDE.md` stub (root and every folder — identical)

~~~md
@AGENTS.md
~~~

The whole file is that one line: Claude Code only auto-loads `CLAUDE.md`, and `@AGENTS.md` imports the
router in the same directory. (You may add a single `<!-- comment -->` line above it.)

## 3. `index.md` (the folder's knowledge — current state, inline)

~~~md
---
type: index
title: <Folder name> — knowledge
description: <one line>
tags: [<tag>]
timestamp: 2026-07-01T12:00:00Z
---

# <Folder name> — knowledge

## What's here
<The deliverables/artifacts in this folder and what each is for. Where the real file lives.>
- `<file>` — <what it is; the current version>. See [decisions](#decisions) if it changed.

## Definitions & assumptions
<Terms, metrics, premises a reader needs. Keep it readable — this is for a human too.>

## How to work here
<Common tasks; what NOT to touch; where a value comes from.>

## Decisions
<The "why" behind the current state — short. Full timeline is in log.md.>
~~~

> For a **document folder**, `## What's here` is the heart: name each deck/sheet/PDF, its current version,
> and where it lives (path or Drive/SharePoint URL). Point at the real artifact; don't paste it in.

## 4. `log.md` (append-only history — the memory)

~~~md
---
type: log
title: <Folder name> — change log
timestamp: 2026-07-01T12:00:00Z
---

# <Folder name> — change log

Append-only. Newest first. Never rewrite a past line.

- 2026-06-28T10:00:00Z — modelo v7→v8: NRR passou a excluir one-offs (superestimava retenção).
  v7 arquivada em _archive/modelo_q3_v7.xlsx. (Fulano, via Drive)
- 2026-05-10T09:00:00Z — modelo v7 criado.
~~~

## 5. `.okf-state.json` (the watcher's snapshot)

~~~json
{
  "generated": "2026-07-01T12:00:00Z",
  "files": [
    { "path": "modelo_q3_v8.xlsx", "sha256": "<hex>", "mtime": 1782900000, "size": 184320 }
  ]
}
~~~

## Resulting tree

```
your-folder/
├── CLAUDE.md            # @AGENTS.md
├── AGENTS.md            # thin router (Rules + pointers + Keep current)
├── index.md            # the folder's knowledge (inline)
├── log.md              # append-only history
├── .okf-state.json     # watcher snapshot
├── _archive/           # old artifacts kept for recall (e.g. modelo_q3_v7.xlsx)
└── subfolder/          # every meaningful subfolder is self-contained:
    ├── CLAUDE.md       #   open it alone and its context still auto-loads
    ├── AGENTS.md       #   (carries its own "If you opened only this folder" up-pointer)
    ├── index.md
    └── log.md
```
