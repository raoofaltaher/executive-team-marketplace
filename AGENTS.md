# executive-team-marketplace: Contributor Guidelines

Read this file before changing anything in this repository. It applies to people and to AI agents alike.

## If you are an AI agent

- Work on a branch cut from `dev`, never from `main`, and open pull requests against `dev`.
- Say in the pull request which model and harness produced the change and which human reviewed the full diff. A PR without a named human reviewer is closed.
- Do not touch sections 1 to 4 of any officer agent under `plugins/executive-team/agents/`. They reproduce the source skills matrix verbatim and are the content of record. If something there is wrong or missing, the fix goes through `org-profile.yaml` or a note in `references/gaps-register.md`, never through an edit.
- After editing any agent file, run `python scripts/build_references.py` inside `plugins/executive-team` and commit the regenerated references; the test suite fails when they are stale.
- Do not add personal data, employee names, ratings, or training records anywhere. Do not add scripts that import spreadsheets or sync agents from external files; the plugin is self-contained by design.
- Do not add third-party integrations, telemetry, hooks, or MCP servers to this plugin. A new integration belongs in its own plugin in `plugins/`.

## Repository layout

```
.claude-plugin/marketplace.json     catalog of plugins in this repository
plugins/executive-team/             the executive-team plugin (agents, skills, templates, scripts, tests)
CONTRIBUTING.md                     how to contribute and the release flow
RELEASE-NOTES.md                    user-facing changes per release
scripts/bump_version.py             updates plugin.json and the marketplace entry together
.github/                            PR and issue templates, CODEOWNERS
```

## Pull request requirements

- One change per PR. Split unrelated changes.
- Every section of the PR template filled in. Placeholder text is a reason to close.
- Evidence for behaviour changes: a before/after scenario (minutes file, transcript excerpt, or test output). "It works" is not evidence.
- Checks pass locally: `build_references.py --check`, the unit tests, and `claude plugin validate --strict` on the plugin, its agents, and its skills.

## What we will not accept

- **Edits to the officers' matrix content.** Sections 1 to 4 are frozen. See above.
- **Personal or company data.** The plugin ships positions, not people.
- **Behaviour-shaping wording changes without evaluation.** The Chief of Staff procedure, the officer answer format, and the routing rule were tuned against smoke scenarios; a change must show it does at least as well.
- **Bundled or speculative changes.** Fix a problem you observed, not one you imagine.
- **Fork-specific or personal configuration** presented as defaults.

## Understand the plugin before contributing

Read `plugins/executive-team/README.md`, then `plugins/executive-team/skills/executive-team/SKILL.md` (the protocol), then `plugins/executive-team/agents/chief-of-staff.md`. Run one meeting with `/executive-team:meet decide <a topic>` and read the minutes it writes before proposing a change to how meetings work.
