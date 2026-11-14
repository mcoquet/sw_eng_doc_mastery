---
name: catch-up
description: Bring an existing codebase's living documentation up to where the doc-mastery rules expect it - scan the code and any existing docs, report what is missing, stale or misplaced, then write GLOSSARY.md, docs/domain-model.md, the C4 diagrams, ADRs and ARCHITECTURE.md to match the system as built. Use when doc-mastery is adopted in a project that already has code, when the user asks to catch up, backfill, bootstrap or audit the project's documentation, or when the living docs have drifted far from the code.
---

# Catch up the living documentation

The workflow rules keep the living documents current one change at a time. That assumes
they were current to begin with. This skill gets an existing project to that starting
point: it reads the code, compares it with the documents the rules name, and closes the
gap. It is safe to run again later; a second run is an audit that fixes drift.

It changes documentation only, never code, so it needs no design doc or plan. Don't start
it in the middle of other work: run it on its own branch and in its own PR.

**Two rules hold throughout:**

- **The code is the evidence.** Everything written traces to something in the repo: a
  file, a schema, a config, a commit, an existing document. Describe the system as built,
  not as intended, and not as the README once hoped.
- **The code cannot say what words mean or why a choice was made.** Those come from
  existing documents, the git history, or the user. Never invent a definition or a
  rationale; ask, and leave out what stays unanswered.

## 1. Preconditions

- `CLAUDE.md` should have the sections `setup-project` adds (`## Methodology`,
  `## Setup and test commands`). If it doesn't, carry on through the report (steps 2 to 4
  only read), say so in the report, and ask the user to run `/doc-mastery:setup-project`
  before anything is written.
- Check `git rev-parse --is-shallow-repository`. In a shallow clone the history is not
  there to read; fetch more (`git fetch --depth=500`) or say in the report that commit
  history was not available as evidence for decisions.
- Read the project's `CLAUDE.md` for overrides. They win: different doc locations, a
  multi-repo split. In a non-primary repo of a multi-repo project, catch up only what that
  repo owns (its own ADRs and internal diagrams) and report, rather than write, anything
  that belongs in the primary repo.
- If `## Setup and test commands` is still TODO, filling it in is part of this run (step 5).

## 2. Inventory what exists

Find every document that already does one of the living documents' jobs, wherever it lives
and whatever it is called:

| Living document | Also look for |
|---|---|
| `GLOSSARY.md` | `docs/glossary.md`, `CONTEXT.md`, "Terminology"/"Concepts" sections in READMEs or wikis |
| `docs/domain-model.md` | ER diagrams, "data model" docs, entity descriptions in design docs |
| `docs/architecture/` | `docs/arch*`, `ARCHITECTURE.md`, diagrams in the README, image or draw.io/PlantUML/Structurizr files |
| `docs/adr/` | `docs/decisions/`, `docs/rfcs/`, `adr/`, "Why we…" sections, design docs that record a choice |
| `ARCHITECTURE.md` | "Project structure"/"Code layout" sections in README or CONTRIBUTING |

Also note `docs/superpowers/specs/` and `plans/`: they are history, useful as evidence, and
are never edited. Documents with other jobs (requirements, runbooks, status pages) stay
where they are; read them as evidence of intent, and link to them where useful.

Read the other agent instruction files too (`AGENTS.md`, `.cursor/rules/`, and the like).
Where they contradict `CLAUDE.md` or the code, that goes in the report.

## 3. Scan the code

Read for what each document needs. In a large repo, give each row below (or each top-level
package or service) to a read-only subagent and have it return findings with file paths;
keep the conclusions, not the file contents.

| For | Read | To find |
|---|---|---|
| C4 context | auth and role definitions, UI entry points, public API surface, outbound HTTP/SDK clients, webhook handlers, env vars and secrets names | user types; external systems and how each is used |
| C4 containers | Dockerfiles, compose files, IaC (Terraform, Helm, CDK, serverless), CI deploy jobs, workspace/monorepo manifests, DB migrations and connection config, queue/topic/cron definitions | deployable units, datastores, queues; each one's technology; who calls whom and over what |
| Glossary | model/entity/type names, DB tables, API resources, UI labels, test names, README | domain nouns and verbs; synonyms used for one thing; one word used for two things |
| Domain model | models and their relations, foreign keys, validations, DB constraints, state enums and transition code, authorisation rules | relationships and cardinality; invariants; lifecycles |
| ADRs | dependency choices, unusual structure, existing decision docs, `git log` for large or explanatory commits, comments starting "we … because" | choices that are hard to reverse and surprising, with the reason if it is recorded |
| `ARCHITECTURE.md` | top-level directories, module boundaries, entry points, shared libraries, cross-cutting code (auth, logging, errors, config) | code map; architectural invariants; cross-cutting concerns |
| Commands | manifests' scripts, Makefile/justfile/taskfile, CI config, CONTRIBUTING | install, test (all and single), lint/format |

Where development and production differ (a local compose file next to a deploy one, SQLite
locally and Postgres deployed), the diagrams show production; note the differences in
`ARCHITECTURE.md`.

For every capability the existing documents claim (access checks, anonymisation, audit
logging, sync), find the code that does it. Existing docs in a codebase that has never
had living documentation often describe the plan, not the system.

Ignore vendored, generated and dependency directories. Stay at the level each document
works at: containers are things that are deployed or run separately, not folders; the
glossary and domain model hold domain concepts, not `UserController` or `BaseRepository`.

## 4. Report the gap and get answers

Before writing anything, show the user one report:

- **Per living document:** missing, present and current, present but stale (list what
  differs from the code), or present elsewhere (say where, and what you propose: move it,
  convert it, or leave it and link to it).
- **What you would write:** the containers and externals found, the candidate terms, the
  concepts and relationships, the candidate ADRs with the evidence for each.
- **Claimed but not built:** what the existing documents say the system does and the code
  does not, or only partly. Put anything that bears on security or privacy first. The
  living documents will describe what the code does (a proxy that "forwards requests",
  not one that "authorises" them, if it has no check); say so here, so nobody is
  surprised by what the diagrams show.
- **Contradictions:** where an existing document and the code disagree in other ways, or
  two parts of the code do. Don't silently pick one.
- **Questions only the user can answer**, batched and specific: which of two synonyms is
  canonical; what a term means where the code is ambiguous; whether something that looks
  unused is live; why a surprising choice was made. Ask about the things that change what
  gets written, not everything.

Wait for the answers. If the user wants only part of it done now, do that part and list
the rest in the final report.

## 5. Write, in this order

Each document builds on the one before, so keep the order. Use the owning skill for each
and follow its format; the workflow rules say where files go.

1. **`GLOSSARY.md`** (`domain-modeling`). One entry per confirmed term, with the synonyms
   to avoid. Where code names differ from the canonical term, say so in the report; don't
   rename code here.
2. **`docs/domain-model.md`** (`domain-model`). Only concepts already in the glossary.
   Relationships and invariants the code enforces; a rule that exists only in someone's
   head is a question for the user, not an invariant.
3. **`docs/architecture/`** (`c4-architecture`). Always `c4-context.md` and
   `c4-containers.md`, plus `README.md` indexing them. Add a component, deployment or
   dynamic diagram only where the system is complex enough that the user would otherwise
   have to explain it. Convert existing diagrams in other formats rather than keeping two
   versions; delete the old one once the user agrees it is superseded.
4. **`docs/adr/`** (`domain-modeling`). Move existing decision records here with
   `git mv`, keeping their text, and give them `NNNN-<slug>.md` names in their original
   order. Write a new, retroactive ADR only for a decision that passes all three tests
   **and** whose reason is recorded or confirmed by the user. Mark it as retroactive, with
   today's date and the evidence (commit, document, or "as recalled by …"). A handful of
   real ones beats a backlog of guesses. Then add `%% See docs/adr/NNNN-...` comments to
   the diagrams those decisions shaped.
5. **`ARCHITECTURE.md`** at the root, since source modules already exist: code map,
   architectural invariants, cross-cutting concerns, linking to `docs/architecture/` for
   the system view. Add its update triggers to `CLAUDE.md`.
6. **`CLAUDE.md`**: fill `## Setup and test commands` with commands you ran and saw work,
   and add any override this run settled (for example a doc location the user chose to keep).

Planned or half-built things are not written as if they exist. Where a gap would mislead
by its silence, state the current behaviour plainly in the document ("requests are
forwarded without an access check") and link to the issue that tracks it if there is one.

When an existing document is current and in the right place, leave it alone. When it is
stale, correct it rather than rewriting it; keep the author's structure where it fits the
format. Fix links that pointed at moved files.

Commit as you go, one commit per document, so the review can follow it.

## 6. Verify

- **Trace:** every container, external system, concept, relationship and invariant written
  points to code you can name. Re-read each document against the code once it is written,
  as a reviewer would; in a large repo, hand this to a fresh subagent that did not write it.
- **Consistency:** names are identical across the glossary, the domain model and the
  diagrams. Every domain-model concept has a glossary entry. Every diagram is in
  `docs/architecture/README.md`.
- **Diagrams:** run the project's Mermaid render-check, and the checklist at the end of
  the `c4-architecture` skill's `references/common-mistakes.md`.
- **Links** between the documents resolve.

## 7. Report and hand over

Open the PR (or, with none, give the user the summary) with:

- a `Docs` line listing each document created, updated or moved;
- **Open questions:** what was left out because it could not be confirmed, so it isn't
  lost: unanswered terms, suspected invariants, decisions with no recorded reason;
- **Code findings:** contradictions, naming mismatches and dead parts noticed on the way.
  They are for the user to schedule; this skill does not fix code.

From here the workflow rules keep the documents current with every change.
