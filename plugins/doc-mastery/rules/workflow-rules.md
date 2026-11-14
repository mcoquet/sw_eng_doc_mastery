# doc-mastery workflow rules

Standing rules from the `doc-mastery` plugin, in force in every project that enables it.
Follow them like `CLAUDE.md` instructions. **Precedence:** the project's `CLAUDE.md` wins
over these rules, and these rules win over any skill (including Superpowers).

## Methodology

Follow **Superpowers** (installed with this plugin): brainstorm → design doc →
plan → implement with TDD → review → finish. The project's `CLAUDE.md` records only what is
specific to that project.

## Setup and test commands gate

The project's `CLAUDE.md` has a `## Setup and test commands` section: install/setup, full
test suite, single test, lint/format, and Mermaid render-check (until set, check diagram
syntax against the `c4-architecture` skill's `references/c4-syntax.md`). No implementation
work (writing-plans execution, subagent-driven-development, executing-plans) starts until it
has real, working commands: the clean-baseline check and red/green TDD depend on them. If the
section is missing or TODO, say so and fill it in as part of the first design or plan.

## Specs and plans

Unless the project's `CLAUDE.md` says otherwise, committed to the repo:

- Design docs (brainstorming): `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- Implementation plans (writing-plans): `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`

## Living documentation

Specs and plans are point-in-time records and are never updated. These documents describe
the system **as it is now** and must be kept current:

| Document | Owns | Skill |
|---|---|---|
| `GLOSSARY.md` | What words mean | `domain-modeling` |
| `docs/domain-model.md` | How concepts relate; invariants; lifecycles | `domain-model` |
| `docs/architecture/` | C4 diagrams: actors, externals, containers, flows | `c4-architecture` |
| `docs/adr/NNNN-<slug>.md` | Why a hard-to-reverse choice was made | `domain-modeling` |

Create each lazily, when there is first something to write. They link to each other rather
than restating each other. A project that already has code but lacks these documents, or
whose documents have drifted well behind it, is brought level with the `catch-up` skill
(docs only, own branch, no design doc or plan needed); suggest it when you notice. ADRs go
in `docs/adr/` (not `docs/decisions/`). A project that spans several repos may keep these
in one primary repo; its `CLAUDE.md` says where.

### What counts as a change

- **Glossary:** a term is introduced, renamed, redefined or retired.
- **Domain model:** a concept, relationship, cardinality, invariant or lifecycle changes.
- **C4 context** (`c4-context.md`): a user type or external system is added or removed, or
  how one interacts with the system changes.
- **C4 containers** (`c4-containers.md`): a deployable unit, datastore or queue/topic is
  added or removed; a container's technology changes; a relationship or protocol between
  containers changes.
- **C4 components / deployment / dynamic:** a container with a component diagram changes
  internally; an environment or its infrastructure changes; a flow that has a dynamic
  diagram changes. Create these only when the design calls for one.
- **ADR:** a decision is settled (an approved design doc, a ruling during implementation,
  or a choice already built) and passes all three tests: hard to reverse, surprising without context, the result of a
  real trade-off.

### When, in the Superpowers workflow

1. **Brainstorming:** use `domain-modeling` and `domain-model` alongside `brainstorming`.
   Record terms in `GLOSSARY.md` as they're resolved. Write no ADR yet: until the design doc
   is approved a choice is still a proposal, and the doc's Approaches part holds the
   reasoning. Where `domain-modeling` would offer an ADR, list it as a candidate under
   Documentation impact instead.
   Every design doc ends with a `## Documentation impact` section listing, for each document
   above, what changes or "none". Proposed C4 and domain-model diagrams go **in the design
   doc**; `docs/architecture/` and `docs/domain-model.md` show only what is built.
2. **Writing plans:** for every non-"none" line in Documentation impact, the plan has an
   explicit task, after the implementation tasks it depends on, to update that document. Its
   verification step: the document matches the code as built, and changed C4 diagrams pass
   the checklist at the end of the `c4-architecture` skill's `references/common-mistakes.md`.
   ADR tasks are the exception: the decision was made when the design was approved, so they
   come first, and their check is that the ADR states the decision as approved.
   Doc updates thus get the same per-task and final review as code. A design doc written
   before these rules has no Documentation impact section: don't add one (specs are never
   updated); the plan lists the doc tasks itself.
3. **Before deleting the ledger** (`.superpowers/sdd/<plan>/progress.md`), and before opening a
   PR for any change made without a plan:
   - **Drift check:** compare the branch diff against "What counts as a change". Anything
     changed but not documented gets documented now, including changes the design didn't
     foresee. Delete diagrams whose subject no longer exists.
   - Copy every `Ruling:` and `minor (deferred)` line into the PR description (or, with no
     PR, append them to the plan file under `## Rulings and deferred minors`). They must
     never exist only in chat. Turn any ruling that passes the ADR test into an ADR.
   - The PR description has a `Docs` line: each document updated, or "no doc changes".

### C4 conventions

- Always `docs/architecture/c4-context.md` and `docs/architecture/c4-containers.md`, created
  by the first design that defines the system. Other levels only when they add value.
- `docs/architecture/README.md` indexes every diagram, one line each, so readers and agents
  see what exists without opening every file. Keep it in sync when adding or deleting one.
- Diagrams link to the ADRs that shaped them (`%% See docs/adr/NNNN-...` comments).
- Names match `GLOSSARY.md` and the domain model exactly.

### Later: `ARCHITECTURE.md`

Once the first real source modules exist, the plan that creates them also adds a root
`ARCHITECTURE.md` (matklad-style: code map, invariants, cross-cutting concerns), linking to
`docs/architecture/` for the system view, and adds its update triggers to `CLAUDE.md`.

## Worktrees

Check `CLAUDE_CODE_REMOTE` before the `using-git-worktrees` step:

- **`true` (Claude Code cloud session):** skip `using-git-worktrees`. The container is already
  isolated; work directly on the session's assigned branch and push only to that branch.
- **unset (local session):** use `using-git-worktrees` as normal.
