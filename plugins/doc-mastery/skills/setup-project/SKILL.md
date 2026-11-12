---
name: setup-project
description: Set up the current repository to use the doc-mastery plugin - commit the plugin and Superpowers to .claude/settings.json and add the project-specific CLAUDE.md sections the workflow rules expect. Also migrates a repo that has vendored copies of these skills and rules. Use when the user asks to set up, adopt, install or migrate to doc-mastery in a project.
disable-model-invocation: true
---

# Set up a project for doc-mastery

The workflow rules and skills come from the plugin. The project only commits two things:
the settings that turn the plugins on, and a `CLAUDE.md` with what is specific to it. Work
through the steps in order, show the user each change, and commit at the end on the
branch you are told to use.

## 1. Look first

Read `CLAUDE.md`, `.claude/settings.json` and `.claude/skills/` if they exist, and skim the
repo (manifests, README, `docs/`) to learn the stack and whether there is code yet. Ask the
user whether this project spans several repos; if it does, ask which one is the **primary**
repo (it holds the system-wide living docs) and whether this one is it.

## 2. `.claude/settings.json`

Merge, keeping every key already there:

```json
{
  "env": { "SUPERPOWERS_DISABLE_TELEMETRY": "1" },
  "extraKnownMarketplaces": {
    "superpowers-marketplace": {
      "source": { "source": "github", "repo": "obra/superpowers-marketplace" }
    },
    "sw-eng-doc-mastery": {
      "source": { "source": "github", "repo": "mcoquet/sw_eng_doc_mastery" }
    }
  },
  "enabledPlugins": {
    "superpowers@superpowers-marketplace": true,
    "doc-mastery@sw-eng-doc-mastery": true
  }
}
```

## 3. `CLAUDE.md`

Keep everything already there. Add only what is missing:

- **`## Methodology`**, short: "This project uses the `doc-mastery` plugin (Superpowers plus
  living documentation; see `.claude/settings.json`). Its rules load at session start. This
  file records only what is specific to this project and wins over the plugin's rules."
- **`## Setup and test commands`**, with real commands if you can find and run them;
  otherwise this TODO block, adapted to what is known about the stack:

  ```md
  > **TODO — not yet defined.** Fill this in as part of the first design/plan.

  - Install / setup: _TBD_
  - Run the full test suite: _TBD_
  - Run a single test: _TBD_
  - Lint / format: _TBD_
  - Render-check Mermaid diagrams (C4, domain model): _TBD_
  ```

  Only list commands you ran and saw work.
- **Overrides**, only where this project departs from the plugin's defaults (spec or plan
  locations, doc locations, a different worktree policy). Say what differs, not the rule.

### Multi-repo projects

In the **primary** repo, add to `CLAUDE.md`: its living docs are system-wide and cover the
other repos (name them); the other repos keep only their own ADRs and internal diagrams; its
`docs/architecture/README.md` also lists diagrams kept in the other repos; design docs for
the whole system live here; plans live in the repo whose code they change.

In every **other** repo, add a `## Living documentation` override section:

- `GLOSSARY.md`, `docs/domain-model.md`, the C4 context and containers diagrams and
  system-wide ADRs live in the primary repo. Where a skill says "`GLOSSARY.md` at the root"
  or "`docs/domain-model.md`", read and edit the primary repo's copy; never create them here.
- This repo keeps its own ADRs in `docs/adr/` and, only when they add value, C4 diagrams
  that zoom into its own container (components, deployment), never the system view. If it
  gets a `docs/architecture/`, that has its own `README.md` and the primary repo's index
  lists it too.
- When a change here touches a document in the primary repo, update it there in a
  companion PR and link the two. The PR's `Docs` line covers both repos.
- Design docs live in the primary repo; plans for this repo's code live here.

## 4. Migrating a repo with vendored copies

If `.claude/skills/` holds `c4-architecture`, `domain-model` or `domain-modeling`, or
`CLAUDE.md` restates the plugin's rules (sections such as "What counts as a change", "When,
in the Superpowers workflow", "C4 conventions", "Worktrees"), they now come from the plugin
and would load twice. Show the user what would go, and on their OK remove the vendored skill
folders and the restated rules. Keep anything project-specific, rewritten as an override.

## 5. Cloud sessions

Tell the user: Claude Code cloud sessions don't install plugins from a repo's
`.claude/settings.json`. To get them there, add these lines to the cloud environment's
setup script (this needs `mcoquet/sw_eng_doc_mastery` to be public):

```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin marketplace add mcoquet/sw_eng_doc_mastery
claude plugin install doc-mastery@sw-eng-doc-mastery
```
