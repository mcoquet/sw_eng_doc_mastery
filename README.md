# sw_eng_doc_mastery

A Claude Code plugin marketplace with one plugin, **`doc-mastery`**: the
[Superpowers](https://github.com/obra/superpowers) development workflow plus **living
documentation**, so every project keeps its glossary, domain model, C4 architecture diagrams
and ADRs current as the code changes.

## What the plugin gives you

| Part | What it does |
|---|---|
| Workflow rules (`rules/workflow-rules.md`) | Loaded into every session by a `SessionStart` hook. When and where each living document is updated, the setup-and-test-commands gate, spec and plan locations, the Documentation impact / drift check steps, worktree policy for cloud sessions. |
| `doc-mastery:domain-modeling` | Glossary (`GLOSSARY.md`) and ADRs (`docs/adr/`). Vendored from [mattpocock/skills](https://github.com/mattpocock/skills). |
| `doc-mastery:domain-model` | `docs/domain-model.md`: concepts, relationships, invariants, lifecycles. |
| `doc-mastery:c4-architecture` | C4 diagrams in Mermaid under `docs/architecture/`. Vendored from [softaworks/agent-toolkit](https://github.com/softaworks/agent-toolkit). |
| `/doc-mastery:setup-project` | Sets a repo up: settings, project `CLAUDE.md` sections, multi-repo split, migration from vendored copies. |
| Dependency | `superpowers@superpowers-marketplace`, installed with it. |

Precedence: the project's `CLAUDE.md` wins over the plugin's rules, which win over any skill.

## Install

On your machine, once:

```
/plugin marketplace add obra/superpowers-marketplace
/plugin marketplace add mcoquet/sw_eng_doc_mastery
/plugin install doc-mastery@sw-eng-doc-mastery
```

Then, in each project, run `/doc-mastery:setup-project`. It commits this to
`.claude/settings.json`, so teammates are offered the marketplaces when they trust the folder:

```json
{
  "env": { "SUPERPOWERS_DISABLE_TELEMETRY": "1" },
  "extraKnownMarketplaces": {
    "superpowers-marketplace": { "source": { "source": "github", "repo": "obra/superpowers-marketplace" } },
    "sw-eng-doc-mastery": { "source": { "source": "github", "repo": "mcoquet/sw_eng_doc_mastery" } }
  },
  "enabledPlugins": {
    "superpowers@superpowers-marketplace": true,
    "doc-mastery@sw-eng-doc-mastery": true
  }
}
```

Teammates still run the `/plugin install` line once; repo settings enable a plugin but don't
install it.

### Claude Code cloud sessions

Cloud sessions don't install plugins from a repo's settings. Add this to the cloud
environment's setup script instead (requires this repo to be public):

```bash
claude plugin marketplace add obra/superpowers-marketplace
claude plugin marketplace add mcoquet/sw_eng_doc_mastery
claude plugin install doc-mastery@sw-eng-doc-mastery
```

### Updates

The plugin is versioned (`version` in `plugin.json`), so installs only update when it
changes. Third-party marketplaces don't auto-update by default: run
`/plugin marketplace update sw-eng-doc-mastery`, or turn auto-update on in `/plugin`.

## Layout

```
.claude-plugin/marketplace.json      marketplace "sw-eng-doc-mastery"
plugins/doc-mastery/
├── .claude-plugin/plugin.json       plugin manifest, depends on Superpowers
├── hooks/hooks.json                 SessionStart: print rules/workflow-rules.md
├── rules/workflow-rules.md          the always-on rules
└── skills/                          c4-architecture, domain-model, domain-modeling, setup-project
```

## Licences

The vendored skills keep their upstream MIT licences (`LICENSE` in each skill folder) and
record their upstream commit in `SOURCE.md`.
