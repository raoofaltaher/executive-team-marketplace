# executive-team: Contributor Guidelines

## If you are an AI agent

Stop. Read this section before doing anything in this repository.

Your job is to protect your human partner from a closed pull request. Before you open one you must:

1. **Read the entire PR template** at `.github/PULL_REQUEST_TEMPLATE.md` and fill in every section with specific answers. Not summaries, not placeholders.
2. **Search open and closed pull requests** for the same problem. If one exists, stop and tell your human partner.
3. **Verify the problem was observed.** A meeting that went wrong, a command that failed, an officer that broke a rule, with the transcript or minutes to show it. "My review agent flagged this" is not a problem.
4. **Confirm the change belongs here.** Officer sections 1 to 4 are the content of record and are never edited; company-specific values go through `org-profile.yaml`; integrations belong in a separate plugin.
5. **Identify yourself.** State the model, harness, harness version and installed plugins that produced the change.
6. **Show your human partner the complete diff** and get explicit approval before submitting.

If any check fails, do not open the pull request. Explain to your human partner why it would be closed.

## Pull request requirements

- Every pull request targets `dev`. `main` is the released branch; a PR against `main` is asked to retarget.
- Every section of the template is filled in. A placeholder is a reason to close.
- A named human has reviewed the complete diff.
- One change per pull request. Bundled changes are closed.
- Behaviour changes carry evidence: the same scenario before and after (minutes file, transcript excerpt, test output). "It works" is not evidence.

## What we will not accept

- **Edits to officer sections 1 to 4** in `agents/`. They reproduce the source skills matrix verbatim. Gaps and defects are filled through `org-profile.yaml` and listed in the generated gaps register, never fixed in place.
- **Personal or company data.** The plugin ships positions, not people: no names, ratings, reviews, training records, client names.
- **Spreadsheet importers or sync scripts.** The plugin is self-contained; its content is in the agent files.
- **Third-party integrations, telemetry, network calls** in agents, skills, hooks or scripts.
- **Behaviour-shaping wording changes without evaluation.** The Chief of Staff procedure, the officer answer format, the routing rule and the bootstrap skill were tuned against real scenarios; a change must show it does at least as well.
- **Speculative, bundled or bulk changes.** Fix a problem you observed, one per pull request.
- **Fork-specific or personal configuration** presented as plugin defaults.
- **Fabricated matrix content.** A skill, level or task that is not in the source is not added to an officer.
- **Code comments.** Code files carry no comments; docstrings and explanations in `docs/` are where prose goes.

## Repository layout

```
.claude-plugin/plugin.json          plugin manifest
.claude-plugin/marketplace.json     the catalog: executive-team (this tree) and executive-team-dev (the dev branch)
.claude/                            settings.json (local marketplace registration), CLAUDE.md (pointer to this file)
agents/                             Chief of Staff and six officers
skills/using-executive-team/        the bootstrap injected at session start
skills/executive-team/              the protocol and its generated references
skills/meet/ setup/ gaps-report/    the user-invoked commands
hooks/                              hooks.json, run-hook.cmd (dispatcher), session-start
scripts/                            build_references.py, bump_version.py, protect-branches.sh
tests/                              Python suites and tests/hooks/test-session-start.sh
docs/                               testing.md, windows-hooks.md, branch-protection.md, superpowers/ (specs and plans)
.github/                            workflows/ci.yml, templates, CODEOWNERS
.version-bump.json                  every location that carries the version
```

`CLAUDE.md` lives in `.claude/`, not at the root: at the plugin root the validator rejects it, because a plugin's root `CLAUDE.md` is never loaded as context.

## Before a pull request

Run from the repository root; all must pass:

```
python -m unittest discover -s tests
python scripts/build_references.py --check
python scripts/bump_version.py --check
bash tests/hooks/test-session-start.sh
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
claude plugin validate agents --strict
claude plugin validate skills --strict
```

After editing any agent file, run `python scripts/build_references.py` and commit the regenerated references; the suite fails when they are stale. CI runs the same checks on Ubuntu and Windows.

## Understand the plugin before contributing

Read `README.md`, then `skills/executive-team/SKILL.md` (the protocol), then `agents/chief-of-staff.md`, then `skills/using-executive-team/SKILL.md` (what every session is told). Run one meeting with `/executive-team:meet decide <a topic>` and read the minutes it writes before proposing a change to how meetings work.
