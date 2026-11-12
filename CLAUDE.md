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
- **Upstream plugins** (`superpowers`, `c4-architecture`, `domain-modeling`) are listed in
  `marketplace.json`, fetched from their authors' repos and never copied or modified here.
  `doc-mastery` depends on them by bare name, which resolves in this marketplace. Anything we
  need to change about how they're used (e.g. ADRs in `docs/adr/`, not the `docs/decisions/`
  that `c4-architecture` suggests) goes in the rules file.
- **Moving a pin:** Superpowers is pinned by release tag (`ref`); the two skills by commit
  (`sha`, with a `git-subdir` `path`). To move one, read the upstream diff for that path or
  the release notes, check it against the rules file (skill names, file paths, ledger path,
  worktree skill), update the pin, and bump the `doc-mastery` version in the same commit so
  installs pick it up. Before adding a skill's folder, check it holds nothing a plugin would
  auto-load unexpectedly (`agents/*.md`, `hooks/`, `.mcp.json`).
- **Names are public API:** the marketplace name, plugin name and skill names appear in
  users' settings and commands. Don't rename them without a migration note in `README.md`.
