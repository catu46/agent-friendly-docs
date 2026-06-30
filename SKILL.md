---
name: agent-friendly-docs
description: Scaffold an agent-friendly documentation architecture for a codebase — a canonical root AGENTS.md (cross-agent standard) plus a CLAUDE.md import stub, and a self-contained AGENTS.md + CLAUDE.md stub in each meaningful folder so any folder can be opened in isolation by an AI agent. Every generated doc embeds a self-updating protocol so context never goes stale. Use when starting a project's docs from scratch or with little existing documentation, organizing folders to be agent-friendly, building a "mother" index doc that routes to per-folder docs, or making CLAUDE.md-based docs agent-agnostic. Triggers (English): "organize folders", "agent-friendly docs", "AGENTS.md", "mother CLAUDE.md", "docs for agents". Triggers (Portuguese): "organizar pastinhas", "deixar agent-friendly", "documentação para agentes", "CLAUDE.md mãe".
---

# Agent-Friendly Docs

Scaffold a documentation architecture any AI coding agent can navigate, with `AGENTS.md` as the
cross-agent source of truth and `CLAUDE.md` as a thin auto-load stub. Best when starting a project's
docs from zero, or with very little existing documentation, and you want an agentic-friendly foundation.

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

### Phase 1 — Interview the human (in the user's language; conversation only, do NOT open code yet)

Goal: understand the project AND the folder organization that fits *this* person's mental model.
Ask (group related questions with AskUserQuestion; otherwise just converse), then reflect a one-paragraph
summary back and confirm before moving on:

- What is the project — domain, purpose, who/what it's for, stage (greenfield vs. existing code)?
- Stack, key tools, services, runtime.
- How does the user already think about the parts? What are the natural modules / areas / pastinhas?
- Desired granularity — how deep should docs nest? Any folders that must / must not get their own doc?
- Docs language, and which agents will consume them.

Do not propose a structure yet. First capture intent.

### Phase 2 — Explore the code & build (ask clarifying questions throughout)

1. **Dive in.** Map the real folder tree, entry points, and how things actually relate.
2. **Reconcile** what you find with Phase 1. Surface mismatches and **ask** whenever reality is
   ambiguous ("folder X mixes Y and Z — split or keep as one?"). Keep asking until the plan is clean.
3. **Pick folders** that are a meaningful unit (service / package / feature / dataset). Skip
   generated & dependency dirs (`node_modules`, `dist`, `build`, `.git`, `vendor`, `.next`, `target`)
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
