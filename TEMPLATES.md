# Templates

Write docs in the **project's language**. Replace every `<placeholder>`. Delete sections that don't
apply — shorter is better. Keep the root high-level and push detail into folder docs. The
**"Keep this current"** section is mandatory in every `AGENTS.md` — copy it verbatim.

## 1. Root `AGENTS.md` (the "mother")

~~~md
# <Project name>

<One sentence: what this project is and who/what it's for.>

## Overview
<2–4 sentences: the problem it solves and the big-picture shape.>

## Stack & key tools
<Languages, frameworks, services. Omit if trivial.>

## Repository map
<The index that routes agents to each folder's doc. One line each — this is the routing.>

| Folder | What lives here | Doc |
|--------|-----------------|-----|
| `<folder-a>/` | <one-line purpose> | [AGENTS.md](<folder-a>/AGENTS.md) |
| `<folder-b>/` | <one-line purpose> | [AGENTS.md](<folder-b>/AGENTS.md) |

## Conventions
- Docs language: <language>
- <Code style / naming / commit / branch rules that apply everywhere.>

## Common commands
<Build / test / run / lint. Omit if not a code project.>

```bash
<command>
```

## Glossary
<Domain terms an agent must know to work here. Optional.>

## Keep this current
This file is the source of truth for the whole project. Whenever you change a folder, after updating
that folder's `AGENTS.md`, update **this** file **only if** the change affects the overview, stack,
repository map, shared conventions, or glossary:
- Add a row to the repository map when a newly documented folder appears; remove one when a folder goes away.
- Touch only what the change actually affected — do not rewrite unrelated parts.
~~~

## 2. Folder `AGENTS.md` (self-contained)

Each folder doc must stand alone — assume the agent opened **only** this folder as its root.

For a **document / asset folder**, read these sections loosely: *Key files* → what's here + naming &
versioning + where the latest / source-of-truth version lives; *How to work here* → how to find, add,
or update a deliverable.

~~~md
# <Folder name>

<One sentence: what this module/folder is responsible for.>

> Part of **[<Project / parent name>](../AGENTS.md)**. Read the parent doc for broader context.

## Purpose
<What this folder solves and where it sits in the larger system.>

## Key files
<The files that matter and what each does. Skip the obvious.>
- `<file>` — <role>

## How to work here
<Common tasks and how to do them; gotchas; what NOT to touch.>

## Conventions
<Anything specific to this folder that differs from the parent.>

## Related
<Sibling folders this depends on or is used by — link, don't restate.>
- [<sibling>](../<sibling>/AGENTS.md)

## Keep this current
After you change code or content in this folder, **before you finish**:
1. Update the sections above if the change touched this folder's purpose, key files, conventions, or how-to.
2. Walk **up**: open the parent `AGENTS.md` (and on up to the root) and update its repository map,
   overview, or shared conventions **only at the levels the change actually affects**.
3. If a sibling's relationship changed, fix that link.
Change only what the edit touched; leave the rest untouched.
~~~

## 3. `CLAUDE.md` stub (root and every folder — identical)

The entire file is one line:

~~~md
@AGENTS.md
~~~

That import makes Claude Code auto-load the canonical `AGENTS.md` in the **same directory** (the `@`
path resolves relative to the stub's location). Other agents read `AGENTS.md` directly, so nothing is
Claude-specific. Optionally add a human comment above it:

~~~md
<!-- Canonical docs live in AGENTS.md (cross-agent standard). This stub just imports it. -->
@AGENTS.md
~~~

## Resulting tree

```
project/
├── AGENTS.md        ← mother: overview + repository map (routing) + keep-current rule
├── CLAUDE.md        ← @AGENTS.md
├── module-a/
│   ├── AGENTS.md    ← self-contained folder doc + keep-current rule (points upward)
│   └── CLAUDE.md    ← @AGENTS.md
└── module-b/
    ├── AGENTS.md
    └── CLAUDE.md
```
