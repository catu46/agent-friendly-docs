---
name: agent-friendly-docs
description: Scaffold an agent-friendly documentation architecture for any folder tree — code or documents (slide decks, spreadsheets, PDFs, datasets, assets, or a mix) — a canonical root AGENTS.md (cross-agent standard) plus a CLAUDE.md import stub, and a self-contained AGENTS.md + CLAUDE.md stub in each meaningful folder so any folder can be opened in isolation by an AI agent. Every generated doc embeds a self-updating protocol so context never goes stale. Use when starting a project's docs from scratch or with little existing documentation, organizing folders (code OR document/Excel/PowerPoint folders) to be agent-friendly, building a "mother" index doc that routes to per-folder docs, or making CLAUDE.md-based docs agent-agnostic. Triggers (English): "organize folders", "agent-friendly docs", "AGENTS.md", "mother CLAUDE.md", "docs for agents", "document/Excel/PowerPoint folder". Triggers (Portuguese): "organizar pastinhas", "deixar agent-friendly", "documentação para agentes", "CLAUDE.md mãe".
---

# Agent-Friendly Docs

Scaffold a documentation architecture any AI agent can navigate, with `AGENTS.md` as the cross-agent
source of truth and `CLAUDE.md` as a thin auto-load stub. Best when starting a project's docs from
zero, or with very little existing documentation, and you want an agentic-friendly foundation.

## Works for any folder (not just code)

This applies to code **and** to folders of documents — slide decks (`.pptx`), spreadsheets (`.xlsx`),
docs (`.docx` / `.pdf`), datasets, design assets, research, or a mix. The architecture is identical;
only the **exploration** changes — and you *can* open these files, you don't have to guess:

- **PDF** — the Read tool reads PDFs directly (use the `pages` range).
- **Modern Office** (`.pptx` / `.xlsx` / `.docx`) are ZIP+XML. Cleanest: `python` with
  `python-pptx` / `openpyxl` / `python-docx` (`pip install` them if missing). Zero-install fallback
  with `unzip`: `unzip -p file.xlsx xl/sharedStrings.xml` (spreadsheet text),
  `unzip -p file.pptx ppt/slides/slide1.xml` (slide text) — crude but it works.
- **Legacy** `.ppt` / `.xls` / `.doc` need a converter (LibreOffice headless or `pandoc`).

Opening every file is slow and noisy, so **inventory first** (names, types, folders, counts, dates),
then **open the files that matter** — the ones the interview flagged, or whatever you need to resolve
ambiguity. The interview tells you *which* files to open; it doesn't replace opening them.

## Core architecture (always)

- **`AGENTS.md` is canonical.** All real content lives here. It is the cross-agent open standard
  (agents.md) — Codex, Cursor, Copilot, Gemini, etc. read it natively.
- **`CLAUDE.md` is a one-line stub** that imports it: `@AGENTS.md`. Claude Code only auto-loads
  `CLAUDE.md`, so the stub bridges it. Never duplicate content; never use a symlink (breaks on
  Windows / in zips / across some git setups).
- **Every meaningful folder gets its own `AGENTS.md` + `CLAUDE.md` stub**, self-contained so the user
  can open *just that folder* as the agent's root and still have working context.
- **Root `AGENTS.md` is the "mother":** project overview + an index that routes to each folder's
  `AGENTS.md`. Keep it high-level; push detail down into folder docs (progressive disclosure keeps
  agent context lean).
- **Language:** conduct the **entire interview and all clarifying questions in the user's language**
  — match the language they write to you in (e.g. Portuguese for a Portuguese-speaking user). Write
  the **docs in the project's primary language** (detect from existing files / the user; ask if
  unclear). Only these skill instructions stay in English.

## Workflow — two phases (always run both, in order)

### Phase 1 — Interview the human (in the user's language; conversation only, do NOT open files yet)

Goal: understand the project AND the folder organization that fits *this* person's mental model. For
non-code folders this phase matters a lot — it tells you which files are worth opening and what they
mean. Ask (group related questions with AskUserQuestion; otherwise just converse), then reflect a
one-paragraph summary back and confirm before moving on:

- What is the project — domain, purpose, who/what it's for, stage (greenfield vs. existing material)?
- **What kind of folder is this** — code, documents (decks / sheets / PDFs), data, assets, or mixed?
  What are the deliverables, and how are they named / versioned (e.g. "final", "v2", dates)?
- Stack / key tools / services (for code), or the tools and formats in play (for documents).
- How does the user already think about the parts? What are the natural modules / areas / pastinhas?
- Desired granularity — how deep should docs nest? Any folders that must / must not get their own doc?
- Docs language, and which agents will consume them.

Do not propose a structure yet. First capture intent.

### Phase 2 — Explore the contents & build (ask clarifying questions throughout)

1. **Dive in.** Map the real folder tree and how things relate. For **code**, read entry points and key
   modules. For **documents**, inventory the files first (names, types, counts, dates, groupings), then
   **open the ones that matter** to understand them — see *Works for any folder* for how to read each
   format. Be selective; don't open everything.
2. **Reconcile** what you find with Phase 1. Surface mismatches and **ask** whenever reality is
   ambiguous ("folder X mixes Y and Z — split or keep as one?"). Keep asking until the plan is clean.
3. **Pick folders** that are a meaningful unit (service / package / feature / dataset / deliverable set
   / topic / client / asset group). Skip generated & dependency dirs *(code)* — `node_modules`,
   `dist`, `build`, `.git`, `vendor`, `.next`, `target` — plus system cruft (`.DS_Store`, temp files)
   and trivial leaves. Depth 1–2 unless complexity warrants more. Don't over-fragment.
4. **Show the proposed tree** (which folders get docs) and confirm before writing.
5. **Write** root `AGENTS.md` + `CLAUDE.md` stub, then each folder's `AGENTS.md` + stub.
6. **Wire links:** root indexes every child with a one-line description; each child links up to its
   parent. No content duplicated across levels.
7. **Embed the self-updating protocol in every `AGENTS.md`** (see below). Non-negotiable.
8. **Report** the final tree and exactly what the user should fill in next.

## Self-updating context — MUST embed in every generated doc

The whole point is that the docs never go stale, so the upkeep rule lives **inside the docs**, not only
in this skill. Every `AGENTS.md` you generate MUST end with a "Keep this current" section (use the
canonical blocks in [TEMPLATES.md](TEMPLATES.md) verbatim). The rule it states:

> After making real code/content changes in a folder, **before finishing**: update **this** folder's
> `AGENTS.md` if the change touched its purpose, key files, conventions, or how-to — then walk **up**
> and check the parent `AGENTS.md` (and on up to the root: repository map, overview, shared
> conventions), updating those **only at the levels the change actually affects**. Change only what the
> edit touched; leave the rest alone.

Folder docs point the update **upward** (folder → parent → root). The root doc states the global rule
so it applies to every agent working anywhere in the repo.

Templates for all files: [TEMPLATES.md](TEMPLATES.md).

## Migration (existing CLAUDE.md with content)

When folders already use `CLAUDE.md` to hold content:
1. Move/rename the content into `AGENTS.md` in the same folder.
2. Replace `CLAUDE.md` with the `@AGENTS.md` stub.
3. Add the "Keep this current" section if missing.
4. Preserve everything; never delete content silently. Go folder by folder, root first.

## Rules

- One source of truth per fact. Root = global; folder = local; never repeat across levels.
- The "Keep this current" section is **required output**, not optional.
- Keep each file short — agents pay a token cost for every line loaded.
- Prefer links over copies. A folder doc may link to a sibling instead of restating it.
- Don't invent project facts. Leave `<placeholder>` / `TODO` markers where you lack info and tell the
  user exactly what to fill in.
