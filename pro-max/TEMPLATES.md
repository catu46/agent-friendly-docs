# TEMPLATES.md — copy-paste blocks for agent-friendly-docs

These are the canonical artifacts. They match the CONTRACT exactly, so the
`validate` script passes on a complete tree built from them — provided you also
create the two referenced concepts (`knowledge/metricas/nrr.md`,
`knowledge/decks/deck-board-q3.md`; see the note under template 9) and the real
artifact files the `resource` paths point to. Copy a block, fill the
`<placeholders>`, delete the inline `#` comments.

Conventions used in every template:

- **Skill instructions stay in English. The docs you GENERATE are written in the
  project's language.** The example bodies below are in Portuguese to show a real
  consultant folder ("modelo", "abas", "Board") — swap to whatever language the
  project uses.
- Timestamps are ISO-8601 UTC placeholders (`2026-06-30T12:00:00Z`). Restamp on
  every real edit.
- A concept's **identity is its file PATH**. `supersedes` / `superseded_by` /
  `resource` / cross-links are all **relative paths from the file they live in**.
- Outer fences are `~~~` so any nested triple-backtick fence inside a template won't break it.

---

## 1) Thin `AGENTS.md` (the router — auto-loaded front door)

Holds ONLY: Rules, a lazy DOWN pointer into `knowledge/`, an UP pointer to the
parent, and the "Keep this current" protocol. **No definitions. No full map.**

~~~markdown
---
type: agent-guide                 # required
title: <Folder name> — guia do agente   # required
description: <one line: what lives in this folder and who owns it>
resource: .                       # this folder (relative); omit if N/A
tags: [<tag>, <tag>]
timestamp: 2026-06-30T12:00:00Z   # required — ISO-8601 UTC; restamp on every edit
---

# <Folder name> — guia do agente

## Rules
- Escopo desta pasta: <o que esta pasta contém e até onde o agente deve ir>.
- Até onde ir ("how far to go"): <pare aqui / pode editar X / só leitura em Y>.
- NÃO mexa em: <arquivos/fontes que o agente nunca deve alterar — ex.: planilhas
  conectadas ao BigQuery, decks já enviados ao cliente>.
- Idioma dos docs: <pt-BR>. Datas/horas em ISO-8601 UTC.

## Knowledge
Conhecimento detalhado -> `./knowledge/index.md` ; abra o conceito que você precisa.
(Não carregue o bundle inteiro — abra só o conceito relevante. `index.md` NÃO é
auto-carregado; siga o link.)

## If you opened only this folder
Regras globais / mapa-mãe -> `../AGENTS.md` . Leia antes de agir se ainda não
estiver carregado. (O Claude Code sobe a árvore sozinho; outras ferramentas —
Copilot/Cursor — costumam ler só a pasta aberta, por isso este ponteiro existe.)

## Keep this current
Depois de mudanças reais nesta pasta:
1. Atualize este `AGENTS.md` e/ou o conceito afetado em `./knowledge/`.
2. APPEND uma linha em `./knowledge/log.md` (nunca reescreva o passado).
3. Restampe o `timestamp` dos arquivos que você tocou.
4. SUPERSEDA — nunca apague: o que foi substituído vira `status: superseded`
   com `superseded_by`, e o original é arquivado (veja template 4).
5. Suba para `../AGENTS.md` / raiz SÓ se a mudança realmente afeta o nível acima.
Mude apenas o que a edição tocou.
~~~

> **Root variant.** The "mother" `AGENTS.md` at the tree root is identical, except
> the `## If you opened only this folder` section says it IS the root, e.g.
> "Esta é a porta de entrada raiz. Não há `../AGENTS.md` acima." Keep the section
> present so the shape is uniform.

---

## 2) `CLAUDE.md` stub (the only auto-load bridge besides AGENTS.md)

Entire file. Exactly `@AGENTS.md`, optionally preceded by **one** HTML-comment
line. The `@import` is EAGER, so this stub must point at the THIN router only —
never at the whole bundle.

~~~text
<!-- Auto-load stub. Harnesses that read CLAUDE.md pick up AGENTS.md via this import. -->
@AGENTS.md
~~~

Minimal form (also valid):

~~~text
@AGENTS.md
~~~

---

## 3) ACTIVE OKF concept — Excel model (the consultant sweet spot)

A concept is a **POINTER + DESCRIPTION**, separate from the artifact. `resource`
points at the real `.xlsx`. This v8 `supersedes` the v7 concept (template 4).

File: `knowledge/modelo-q3.md`

~~~markdown
---
type: excel-model                 # required
title: Modelo financeiro Q3 (v8)  # required
description: Projeção de receita e NRR do trimestre Q3, base do deck do Board.
resource: ../models/modelo_q3_v8.xlsx   # the real artifact (relative path)
status: active
supersedes: ./modelo-q3-v7.md     # this concept replaces the v7 concept
tags: [financeiro, nrr, q3, board]
timestamp: 2026-06-30T12:00:00Z   # required
---

# Modelo financeiro Q3 (v8)

Planilha-mãe que alimenta o deck do Board. Abrir o artefato real em
`../models/modelo_q3_v8.xlsx`.

## Abas
- `Premissas` — drivers de entrada (preço, churn, novos logos). Editável.
- `Receita` — cálculo mês a mês; fórmulas, não digitar à mão.
- `NRR` — Net Revenue Retention; ver definição em [NRR](./metricas/nrr.md).
- `Resumo` — números que vão para o deck; ver [Deck do Board Q3](./decks/deck-board-q3.md).

## Premissas
- Câmbio fixo de R$/US$ informado na aba `Premissas` (não puxa cotação ao vivo).
- Serviços profissionais EXCLUÍDOS do NRR a partir de v8 — ver a decisão
  [NRR exclui serviços](./decisoes/nrr-exclui-servicos.md).

## Caveats
- Linhas ocultas na aba `Receita` contêm cenário pessimista; não apagar.
- O que mudou de v7 -> v8 está registrado em `./log.md` e na decisão linkada acima.
- Versão anterior preservada em [Modelo Q3 v7 (superseded)](./modelo-q3-v7.md).

## Links
- Métrica: [NRR](./metricas/nrr.md)
- Entrega: [Deck do Board Q3](./decks/deck-board-q3.md)
- Decisão: [NRR exclui serviços](./decisoes/nrr-exclui-servicos.md)
~~~

> For BIG spreadsheets, the body describes **headers + abas + dtypes + sample
> rows + used range** (e.g. `A1:F50000`), NOT every cell. The agent reads the
> artifact on demand via the `resource` path.

---

## 4) SUPERSEDED concept — the v7, KEPT (memory layer, append-only)

When v7 -> v8, you do NOT delete v7. You set it `superseded`, link forward to v8,
and repoint its `resource` at the archived bytes. This is how an agent later
recovers "what we used to do."

File: `knowledge/modelo-q3-v7.md`

~~~markdown
---
type: excel-model
title: Modelo financeiro Q3 (v7 — superseded)
description: Versão anterior do modelo Q3, substituída pela v8. Mantida para histórico.
resource: ./_archive/modelo_q3_v7.xlsx   # archived bytes (relative to this file)
status: superseded
superseded_by: ./modelo-q3.md            # the v8 concept that replaced this
tags: [financeiro, nrr, q3, board, historico]
timestamp: 2026-06-30T12:00:00Z
---

# Modelo financeiro Q3 (v7 — superseded)

> SUPERSEDED por [Modelo financeiro Q3 (v8)](./modelo-q3.md) em 2026-06-30.
> Não usar para números atuais. Mantido para recuperar a abordagem anterior.

## O que esta versão fazia diferente
- NRR INCLUÍA serviços profissionais (na v8 passou a excluir).
- Câmbio era puxado de uma aba externa (na v8 virou premissa fixa).

## Como recuperar
O artefato original está em `./_archive/modelo_q3_v7.xlsx`. O PORQUÊ da mudança
está em [NRR exclui serviços](./decisoes/nrr-exclui-servicos.md).
~~~

> **Archiving honesty.** git / Drive / SharePoint version the *bytes*; this layer
> adds the readable *story*. Keep a real copy of the old artifact at the `resource`
> path (here `knowledge/_archive/modelo_q3_v7.xlsx`) so `validate` check #5 passes
> and the recovery actually works.

---

## 5) `type: decision` concept — lightweight ADR (the WHY)

Records context -> what changed -> why. Linked from the concepts it explains.

File: `knowledge/decisoes/nrr-exclui-servicos.md`

~~~markdown
---
type: decision
title: NRR passa a excluir serviços profissionais (Q2)
description: Por que o cálculo de NRR mudou entre v7 e v8 do modelo Q3.
status: active
tags: [decisao, adr, nrr, q3]
timestamp: 2026-06-30T12:00:00Z
---

# NRR passa a excluir serviços profissionais (Q2)

## Contexto
Até a v7, o NRR somava receita de serviços profissionais (one-off) junto da
receita recorrente. Ver [NRR](../metricas/nrr.md) e
[Modelo Q3 v7](../modelo-q3-v7.md).

## O que mudou
A partir da v8 ([Modelo Q3 v8](../modelo-q3.md)), serviços profissionais ficam
FORA do NRR; entram só na receita total.

## Por quê
Serviços one-off inflavam o NRR e não refletiam retenção real do recorrente. O
Board pediu uma métrica comparável com benchmarks de mercado (que excluem serviços).

## Consequências
- Números de NRR pós-v8 não são comparáveis aos de v7 sem reprocessar.
- A definição em [NRR](../metricas/nrr.md) foi atualizada.
~~~

---

## 6) `knowledge/index.md` — the navigable MAP (lazy, on demand)

The map of concepts + subfolders. NOT auto-loaded — the `AGENTS.md` down-pointer
sends the agent here when it needs detail.

File: `knowledge/index.md`

~~~markdown
---
type: index                       # required
title: Mapa de conhecimento — <Folder name>   # required (title)
timestamp: 2026-06-30T12:00:00Z   # required
---

# Mapa de conhecimento — <Folder name>

Abra só o conceito que você precisa.

## Conceitos
| Conceito | Tipo | Status | Resumo |
|---|---|---|---|
| [Modelo Q3 v8](./modelo-q3.md) | excel-model | active | Modelo-mãe do trimestre; alimenta o deck. |
| [Modelo Q3 v7](./modelo-q3-v7.md) | excel-model | superseded | Versão anterior, mantida para histórico. |
| [NRR](./metricas/nrr.md) | metric | active | Net Revenue Retention; exclui serviços a partir do Q2. |
| [Deck do Board Q3](./decks/deck-board-q3.md) | deck | active | Apresentação do Board com os números do modelo. |
| [NRR exclui serviços](./decisoes/nrr-exclui-servicos.md) | decision | active | Por que o NRR mudou de v7 para v8. |

## Subpastas
- `metricas/` — definições de métricas.
- `decks/` — conceitos das apresentações.
- `decisoes/` — ADRs (decisões e seus porquês).
- `_archive/` — artefatos arquivados (bytes das versões superseded).

## Histórico
Mudanças recentes: [log.md](./log.md).
~~~

---

## 7) `knowledge/log.md` — APPEND-ONLY change history

Reverse-chronological. Never rewrite past lines; only prepend new ones.

File: `knowledge/log.md`

~~~markdown
---
type: log                         # required
title: Histórico de mudanças — <Folder name>   # required (title)
timestamp: 2026-06-30T12:00:00Z   # required — stamp of the latest entry
---

# Histórico de mudanças — <Folder name>

- 2026-06-30T12:00:00Z — modelo_q3_v7.xlsx substituído por v8; v7 marcado superseded e arquivado em `_archive/`; NRR passou a excluir serviços (ver decisão). (artur — git log)
- 2026-06-29T09:00:00Z — adicionado conceito do Deck do Board Q3. (artur — Drive: modificado por)
- 2026-06-28T15:30:00Z — scaffold inicial do bundle knowledge/. (agent)
~~~

> Attribution is **source-dependent and stated honestly**: git -> `git log -1
> --format=%an <file>`; Drive/SharePoint -> "última modificação por"; plain
> filesystem -> OS owner, else the configured folder owner.

---

## 8) `knowledge/.okf-state.json` — reconciliation-watcher snapshot

Per-file fingerprint from the last run. The watcher diffs the live filesystem
(and/or `git diff`, and/or a source API's "modified at/by") against this to detect
add/modify/delete **regardless of who edited or whether they used Claude Code**.

File: `knowledge/.okf-state.json`

~~~json
{
  "generated": "2026-06-30T12:00:00Z",
  "files": [
    {
      "path": "../models/modelo_q3_v8.xlsx",
      "sha256": "9f2c0a7b8e1d4c5a6b3f0d2e1a7c9b4d8e6f0a1b2c3d4e5f60718293a4b5c6d7",
      "mtime": 1782820800,
      "size": 184320
    },
    {
      "path": "_archive/modelo_q3_v7.xlsx",
      "sha256": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b",
      "mtime": 1782734400,
      "size": 180224
    },
    {
      "path": "../decks/board_q3.pptx",
      "sha256": "abcdef0123456789abcdef0123456789abcdef0123456789abcdef0123456789",
      "mtime": 1782730000,
      "size": 2457600
    }
  ]
}
~~~

---

## 9) Resulting folder tree (with `_archive/` and `knowledge/`)

Every meaningful folder is self-contained: its own thin `AGENTS.md` + `CLAUDE.md`
stub, so opening JUST that folder auto-loads its context.

~~~text
projeto-cliente-x/
├── CLAUDE.md                      # @AGENTS.md  (template 2)
├── AGENTS.md                      # thin router / mother front door (template 1)
├── knowledge/                     # OKF v0.1 bundle — lazy, opened on demand
│   ├── index.md                   # the navigable MAP (template 6)
│   ├── log.md                     # APPEND-ONLY history (template 7)
│   ├── .okf-state.json            # watcher snapshot (template 8)
│   ├── modelo-q3.md               # ACTIVE concept, v8 (template 3)
│   ├── modelo-q3-v7.md            # SUPERSEDED concept, v7 kept (template 4)
│   ├── metricas/
│   │   └── nrr.md                 # type: metric concept
│   ├── decks/
│   │   └── deck-board-q3.md       # type: deck concept (resource -> ../../decks/board_q3.pptx)
│   ├── decisoes/
│   │   └── nrr-exclui-servicos.md # type: decision / ADR (template 5)
│   └── _archive/
│       └── modelo_q3_v7.xlsx      # archived BYTES of the old artifact
├── models/                        # real artifacts (a meaningful subfolder)
│   ├── CLAUDE.md                  # @AGENTS.md
│   ├── AGENTS.md                  # thin router (up-pointer -> ../AGENTS.md)
│   ├── knowledge/                 # its own bundle (index.md, log.md, .okf-state.json, concepts)
│   │   └── index.md
│   └── modelo_q3_v8.xlsx          # current model (resource of the active concept)
└── decks/
    ├── CLAUDE.md                  # @AGENTS.md
    ├── AGENTS.md                  # thin router (up-pointer -> ../AGENTS.md)
    ├── knowledge/
    │   └── index.md
    └── board_q3.pptx
~~~

Notes on the tree:

- **`knowledge/_archive/`** holds the archived *bytes* so the superseded concept's
  `resource: ./_archive/modelo_q3_v7.xlsx` resolves and recovery works. (Alternative:
  archive next to the live artifact in `models/_archive/`; then the concept's
  `resource` becomes the path to that location. Pick one and stay consistent — the
  `validate` script only requires that the `resource` path exists.)
- Each subfolder that has real content gets its **own** `AGENTS.md` + `CLAUDE.md`
  + `knowledge/` so it is useful when opened alone. The up-pointer in each
  `## If you opened only this folder` walks to `../AGENTS.md`.
- **Two referenced concepts must also exist.** The examples link to
  `knowledge/metricas/nrr.md` (`type: metric`) and `knowledge/decks/deck-board-q3.md`
  (`type: deck`) from templates 3, 5, and 6. Those are real markdown links, so
  `validate` check #4 requires the target files to exist — create each from the OKF
  concept pattern (templates 3/5, with `type: metric` / `type: deck`). They are left
  out as standalone copy-paste blocks only to keep this file short, not because they
  are optional.
- At scale (hundreds of folders), generate these per leaf folder with **one
  subagent per folder**, then roll summaries leaf -> mid -> root.
