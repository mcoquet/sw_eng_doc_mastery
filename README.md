# sw_eng_doc_mastery

A Claude Code plugin marketplace with two plugins of its own:

- **`doc-mastery`**: the
[Superpowers](https://github.com/obra/superpowers) development workflow plus **living
documentation**, so every project keeps its glossary, domain model, C4 architecture diagrams
and ADRs current as the code changes.
- **`workload-orchestrator`**: a coordinator playbook for working a backlog as parallel Claude
  Code cloud sessions ("workers"), with a mobile roadmap artifact as the control surface. See
  [below](#workload-orchestrator).

## What doc-mastery gives you

| Part | What it does |
|---|---|
| Workflow rules (`rules/workflow-rules.md`) | Loaded into every session by a `SessionStart` hook. When and where each living document is updated, the setup-and-test-commands gate, spec and plan locations, the Documentation impact / drift check steps, worktree policy for cloud sessions. |
| `doc-mastery:domain-model` | `docs/domain-model.md`: concepts, relationships, invariants, lifecycles. |
| `/doc-mastery:setup-project` | Sets a repo up: settings, project `CLAUDE.md` sections, multi-repo split, migration from vendored copies. |
| `/doc-mastery:catch-up` | For a project that already has code: scans it, reports which living documents are missing, stale or misplaced, then writes them to match the system as built. Run again later as a drift audit. |
| `domain-modeling:domain-modeling` | Glossary (`GLOSSARY.md`) and ADRs (`docs/adr/`). From [mattpocock/skills](https://github.com/mattpocock/skills). |
| `c4-architecture:c4-architecture` | C4 diagrams in Mermaid under `docs/architecture/`. From [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit). |
| `superpowers:*` | The [Superpowers](https://github.com/obra/superpowers) workflow skills. |

Only `doc-mastery` (and `workload-orchestrator`) live in this repo. The other three are installed automatically as its
dependencies: this marketplace lists them, fetched unmodified from their upstream repos and
pinned (Superpowers to a release tag, the two skills to a commit, one folder each), so
nothing is copied here and installs are reproducible.

Precedence: the project's `CLAUDE.md` wins over the plugin's rules, which win over any skill.

## Install

On your machine, once (Superpowers comes with it):

```
/plugin marketplace add mcoquet/sw_eng_doc_mastery
/plugin install doc-mastery@sw-eng-doc-mastery
```

Then, in each project, run `/doc-mastery:setup-project`. It commits this to
`.claude/settings.json`, so teammates are offered the marketplaces when they trust the folder:

```json
{
  "env": { "SUPERPOWERS_DISABLE_TELEMETRY": "1" },
  "extraKnownMarketplaces": {
    "sw-eng-doc-mastery": { "source": { "source": "github", "repo": "mcoquet/sw_eng_doc_mastery" } }
  },
  "enabledPlugins": {
    "superpowers@sw-eng-doc-mastery": true,
    "doc-mastery@sw-eng-doc-mastery": true
  }
}
```

**Project already has code?** Run `/doc-mastery:catch-up` next, on its own branch. It reads
the code and any existing docs, shows you the gap and asks what only you can answer (what
terms mean, why choices were made), then writes the glossary, domain model, C4 diagrams,
ADRs and `ARCHITECTURE.md`. It never changes code.

**Already have Superpowers from `superpowers-marketplace`?** Then it would load twice. Remove
that copy with `claude plugin uninstall superpowers@superpowers-marketplace`, and in project
settings replace `superpowers@superpowers-marketplace` with `superpowers@sw-eng-doc-mastery`
(`/doc-mastery:setup-project` does this).

Teammates still run the `/plugin install` line once; repo settings enable a plugin but don't
install it.

### Claude Code cloud sessions

Cloud sessions don't install plugins from a repo's settings. Add this to the cloud
environment's setup script instead (requires this repo to be public):

```bash
claude plugin marketplace add mcoquet/sw_eng_doc_mastery
claude plugin install doc-mastery@sw-eng-doc-mastery
```

### Updates

The plugin is versioned (`version` in `plugin.json`), so installs only update when it
changes. Third-party marketplaces don't auto-update by default: run
`/plugin marketplace update sw-eng-doc-mastery`, or turn auto-update on in `/plugin`.

### Upstream update checks

A scheduled GitHub Action (`.github/workflows/check-upstreams.yml`, Mondays 07:17 UTC, or run
it by hand from the Actions tab) checks each pinned upstream for a newer release tag or for
new commits in the pinned folder. For each one it opens an issue labelled `upstream-update`
with the commits, the diff, a check for files a plugin would auto-load, and the exact steps
to move the pin. It never changes the pins itself. A version that was already raised, even in
an issue closed as not planned, isn't raised again; if upstream moves again while an issue is
open, that issue is updated.

## workload-orchestrator

One skill, `workload-orchestrator:workload-orchestrator`, for a session acting as **coordinator**:

- It splits the tickets you put in **Now** into file-disjoint groups and starts one cloud
  session (a worker) per group, each ending in a PR.
- It merges those PRs on the worker's tests plus a results page with proof (screenshots,
  command output). It never deploys.
- It keeps one roadmap artifact as the shared control surface: Decide / Now / Next / Later
  tabs, a worker plan from areas and dependencies, a progress bar, and a **Send** button that
  wakes the coordinator. It's built for a phone.

It is independent of `doc-mastery` and opt-in:

```
/plugin install workload-orchestrator@sw-eng-doc-mastery
```

or add `"workload-orchestrator@sw-eng-doc-mastery": true` to a project's `enabledPlugins`. In
cloud sessions, add the install line to the environment's setup script, next to the
doc-mastery one.

Inside the skill:
- `SKILL.md`: the workflow, standing rules, merge steps and check-in trigger.
- `assets/roadmap.html`: the roadmap app.
- `references/roadmap-schema.md`: its database and capabilities.
- `references/worker-prompt-template.md`: the base prompt for workers.
- `references/lessons.md`: what went wrong in practice.

## Layout

```
.claude-plugin/marketplace.json      marketplace "sw-eng-doc-mastery"
                                     also lists superpowers, c4-architecture, domain-modeling (upstream)
plugins/doc-mastery/
├── .claude-plugin/plugin.json       plugin manifest and its dependencies
├── hooks/hooks.json                 SessionStart: print rules/workflow-rules.md
├── rules/workflow-rules.md          the always-on rules
└── skills/                          catch-up, domain-model, setup-project
plugins/workload-orchestrator/
├── .claude-plugin/plugin.json       plugin manifest
└── skills/workload-orchestrator/        SKILL.md, assets/roadmap.html, references/
.github/workflows/check-upstreams.yml  weekly upstream check
.github/scripts/check_upstreams.py     the check (stdlib Python + git + gh)
```

## Licences

Superpowers (Jesse Vincent), `c4-architecture` (softaworks) and `domain-modeling` (Matt
Pocock) are MIT licensed by their authors and fetched from their own repos at install time;
nothing of theirs is copied into this repo.

This repo's own content (the `doc-mastery` and `workload-orchestrator` plugins, its rules and skills, and the upstream
check script) is MIT licensed; see `LICENSE`.
