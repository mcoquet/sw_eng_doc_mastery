# CLAUDE.md

This repo is a Claude Code plugin marketplace (`sw-eng-doc-mastery`) holding one plugin,
`doc-mastery`, in `plugins/doc-mastery/`. See `README.md` for what it contains.

## Rules for changing it

- **Validate before committing:** `claude plugin validate .` (marketplace) and
  `claude plugin validate plugins/doc-mastery` (plugin). Marketplace validation doesn't check
  plugin files, so run both. Both must pass with no errors.
- **Rules size:** `rules/workflow-rules.md` is printed by a `SessionStart` hook, and hook
  output over 10,000 characters gets cut to a preview. Keep it well under that
  (`wc -c plugins/doc-mastery/rules/workflow-rules.md`); move detail into a skill instead.
- **Rules stay generic.** Nothing specific to one client or project goes in the plugin;
  that belongs in the project's `CLAUDE.md` as an override.
- **Version bumps:** installs only update when `version` in `plugins/doc-mastery/.claude-plugin/plugin.json`
  changes. Bump it (semver) in every change that users should receive. Set the version only
  there, not in `marketplace.json`.
- **Vendored skills** (`c4-architecture`, `domain-modeling`) stay unmodified. Each has a
  `SOURCE.md` with the upstream commit and how to update; overrides go in the rules file.
- **Names are public API:** the marketplace name, plugin name and skill names appear in
  users' settings and commands. Don't rename them without a migration note in `README.md`.
