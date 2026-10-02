# Release Notes

## v0.2.0 (2026-10-02)

The repository is rebuilt on the obra/superpowers shell. Content is unchanged: the seven agents, the protocol and the three commands are the same files as v0.1.1, moved.

### Layout

- The plugin now lives at the repository root; the repository is one plugin that is also its own marketplace. Install commands are unchanged. Existing installs move over with `/plugin marketplace update executive-team-marketplace` and `/plugin update executive-team`.
- `executive-team-dev` installs the whole repository from the `dev` branch.
- Tags are now `vX.Y.Z`.
- The contributor pointer `CLAUDE.md` moved to `.claude/CLAUDE.md`: at a plugin root Claude Code's validator rejects it, because a plugin's root `CLAUDE.md` is never loaded as context. Claude Code still reads it as project instructions when you work in this repository.

### Session bootstrap

- A SessionStart hook injects the new one-screen `using-executive-team` skill at startup, after `/clear` and after compaction: who the team is, when to bring it in, how a meeting works, where the rules live.
- In a git repository with no `org-profile.yaml`, the bootstrap adds one line offering `/executive-team:setup` the first time the team is called on. `EXECUTIVE_TEAM_NUDGE=off` silences it.
- The hook is a polyglot dispatcher plus a builtins-only bash script, after ultrapowers' hardened versions, so it runs on Windows through Git Bash and survives a broken PATH at startup. `docs/windows-hooks.md` explains the mechanics.

### Tooling

- `.version-bump.json` declares every location that carries the version; `scripts/bump_version.py` writes them, `--check` detects drift, `--audit` finds the version string in undeclared files.
- New tests: `tests/test_hooks.py` and `tests/hooks/test-session-start.sh` (fourteen cases, including empty PATH, Windows paths with spaces and accents, an unreadable skill and an unparseable `cwd`).
- Continuous integration on every pull request to `dev` and `main`, on Ubuntu and Windows: unit tests, references check, version check, hook test, ShellCheck, and plugin validation of both the marketplace and the plugin manifest.

### Documentation

- One README. AGENTS.md, CONTRIBUTING.md and the pull request and issue templates follow the superpowers pattern. New `docs/testing.md` and `docs/windows-hooks.md`.
- The pull request template asks for evidence the way PR #5 gave it: each model and the stage it did, links to the spec and plan, test counts, a live check, what was exercised by hand, and who reviewed the branch.

## v0.1.1 (2026-09-30)

### executive-team

- The CSO now ships default required levels (sales-domain skills 3; executive leadership and corporate vision 2, matching the identical CMO skills). The source matrix has none, so each is marked `plugin default` in the agent file and in the gaps register; override any of them in `org-profile.positions.cso.level_overrides`. Setup no longer asks for them, and the CSO is now invited to meetings on its own merits.
- `/executive-team:setup` runs as an interactive multiple-choice interview: defaults are offered first, free text stays available through "Other", related questions are grouped. It no longer asks for a default meeting mode.
- The org-profile template moved into the setup skill's folder, so every harness can read it; the skill also resolves the gaps register and routing index relative to its own folder when the plugin-root variable is not substituted.
- The meeting mode is settled per meeting: explicit, detected from the request, or asked with a recommendation when unclear; confirmed in the first line of every reply; "now decide" or "mode: risk" reruns the last topic in another mode.

## v0.1.0 (2026-09-29)

First release of the `executive-team` plugin and this marketplace.

### executive-team

- Six officer agents built from a skills-by-position matrix: COO (12 skills), CISO (12), CTO (11), CMO (10), CSO (11), CFO (9). Every skill carries its description, associated tasks, required level, and a source pointer. Fields the matrix left blank are marked `not specified in source`; defects are reproduced and flagged in a generated gaps register.
- A Chief of Staff agent that routes a topic to the officers whose skills govern it, runs them in parallel, runs one consult round, writes an executive brief (summary, positions, agreement, disagreement, risks, recommended decision, open questions, next steps) and saves minutes.
- User-invoked skills: `/executive-team:meet [mode] [officers: ...] <topic>` with modes brainstorm, decide, review, plan, risk; `/executive-team:setup` to write a git-ignored `org-profile.yaml`; `/executive-team:gaps-report`.
- Required skill levels shape each officer's confidence and scope; the CSO, which has no levels in the source, answers at level 1 until the profile sets them.
- Officers answer in the Owner's language; briefs keep English headings and literal tokens.
- Privacy: positions only, no employee data, assessments and training plans use conversation input only.

### Marketplace

- Catalog with `executive-team` (from `main`) and `executive-team-dev` (from the `dev` branch).
- Contribution flow with `main` and `dev` branches, PR and issue templates, contributor guidelines for people and AI agents, Contributor Covenant.
