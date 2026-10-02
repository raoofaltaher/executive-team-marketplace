# Testing

Everything runs from the repository root. Prerequisites: Python 3.10 or later, bash (Git Bash on Windows), git. ShellCheck and the Claude Code CLI are needed for the last two rows only.

| Suite | Command | What it proves |
|---|---|---|
| References | `python -m unittest tests.test_references` | The officer-file parser, structural checks, plugin-default levels, index and gaps generation, against a fixture officer. |
| Repository hygiene | `python -m unittest tests.test_repo_hygiene` | No spreadsheet, personal-data or retired-tooling files are tracked; agent frontmatter conventions; namespaced orchestration; the bootstrap skill's content; the catalog points at the root and the dev branch; the CI workflow runs every static check; generated references are fresh. |
| Hooks and version tooling | `python -m unittest tests.test_hooks` | `hooks.json` registers one SessionStart command; hook files are executable, LF-only and comment-free; declared version locations agree; `--check` fails on drift and on a missing field; `--audit` passes on the committed tree. |
| SessionStart hook | `bash tests/hooks/test-session-start.sh` | Output shape with and without `CLAUDE_PLUGIN_ROOT`; the nudge appears only inside a git repository with no `org-profile.yaml` at or above the working directory; `EXECUTIVE_TEAM_NUDGE=off`; empty stdin; empty PATH; the dispatcher; Windows-style paths; an unreadable bootstrap skill. Cases that cannot run on the machine print `[SKIP]` with the reason. |
| Generated references | `python scripts/build_references.py --check` | The routing index and gaps register match the agent files. |
| Version locations | `python scripts/bump_version.py --check` | Every location in `.version-bump.json` carries the same version. `--audit` also fails if the version string appears in an undeclared tracked file. |
| Shell lint | `shellcheck --severity=warning hooks/session-start` | No ShellCheck warnings in the hook script. |
| Plugin validation | `claude plugin validate . --strict`, `claude plugin validate .claude-plugin/plugin.json --strict`, `agents --strict`, `skills --strict` | The marketplace manifest, the plugin manifest (which `validate .` does not reach once a marketplace manifest sits beside it), and agent and skill frontmatter, as Claude Code reads them. Runs without a login. |

`.github/workflows/ci.yml` runs all of these on every pull request to `dev` and `main` and on pushes to `main`, on Ubuntu and Windows (ShellCheck and plugin validation on Ubuntu only).

## Not gated

Meeting behaviour (routing, the consult round, the brief, minutes, language) is checked by hand: run a scenario with `/executive-team:meet` before and after a change and compare the minutes. Those runs are not in CI because they call a model.

## Seeing the bootstrap

`bash hooks/session-start` prints the JSON Claude Code receives. Pipe a hook payload to see the nudge logic: `printf '{"cwd": "/path/to/a/project"}' | CLAUDE_PLUGIN_ROOT=$PWD bash hooks/session-start`.
