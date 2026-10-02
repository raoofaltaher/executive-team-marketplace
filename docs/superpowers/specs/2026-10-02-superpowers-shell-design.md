# Superpowers shell for executive-team: design

Date: 2026-10-02
Status: approved in conversation by the Owner; implementation plan follows this document.

## 1. Purpose

Rebuild the engineering shell of this repository on the pattern of obra/superpowers v6.4.2 and its fork raoofaltaher/ultrapowers v1.0.1, while leaving the executive-team content (the seven agents, the protocol skill and its references, the three user-invoked skills) untouched. "Shell" means: repository layout, session bootstrap through a hook, version and release tooling, test layout, continuous integration, documentation and contributor files.

Both templates were inventoried from clones on 2026-10-02. The facts that shaped the decisions below:

- Both ship one plugin at the repository root; the repository is also its own single-entry marketplace.
- Their one runtime mechanism is a SessionStart hook (or an in-process equivalent on other harnesses) that injects one short "using-X" skill into every session. Nothing else runs at runtime.
- Neither has telemetry. Superpowers had a single version beacon in an optional web page; ultrapowers removed it and wrote a rule against it.
- Neither has continuous integration. Tests are run by hand before a release pull request.
- Neither supports claude.ai or ChatGPT; they have no plugin surface.
- Neither ships agents to any harness other than Claude Code.

## 2. Decisions taken with the Owner

| Topic | Decision |
|---|---|
| Repository layout | Plugin at the repository root, ultrapowers shape. The repository is one plugin that is also its own marketplace. |
| Officers on other harnesses | Officers stay Claude Code agents. Only Claude Code is supported in this release. Other harnesses are not added now; the layout leaves room for them. |
| Template | Superpowers is the template for shape and voice; ultrapowers' hardened hook scripts are the version copied, because they fix Windows and broken-PATH cases upstream has not. |
| Bootstrap | A new one-screen skill `using-executive-team`, injected on startup, clear and compact, with a nudge when the project has no `org-profile.yaml`. |
| Telemetry | Left open. Nothing is shipped and no rule is written in this release. |
| Continuous integration | Yes: static checks on every pull request, no model calls. |
| Migration | Restructure in place with `git mv` so history follows every file. No fresh clone of either template. |

## 3. Out of scope

- Manifests, adapters and tool-mapping files for any harness other than Claude Code.
- claude.ai and ChatGPT bundles.
- Telemetry of any kind, and a written telemetry rule.
- A diagnosing skill.
- The officer ownership contract and the per-officer work-order path discussed on 2026-10-02. They are content changes and get their own specification after this one; that specification will extend the bootstrap skill by one paragraph.
- Changes to agent files, to `skills/executive-team/`, `skills/meet/`, `skills/setup/`, `skills/gaps-report/`, or to `scripts/build_references.py` beyond what the move requires (nothing: the script resolves paths from its own location).

## 4. Repository layout after the change

```
executive-team-marketplace/
├── .claude-plugin/
│   ├── plugin.json                  plugin manifest, version 0.2.0
│   └── marketplace.json             catalog: executive-team (source "./"), executive-team-dev (dev branch)
├── .claude/settings.json            local development registration, unchanged
├── .github/
│   ├── CODEOWNERS                   unchanged
│   ├── ISSUE_TEMPLATE/              bug_report.md, feature_request.md, config.yml
│   ├── PULL_REQUEST_TEMPLATE.md     restructured
│   └── workflows/ci.yml             new
├── agents/                          seven files, unchanged
├── assets/plugin.png                unchanged
├── docs/
│   ├── branch-protection.md         unchanged
│   ├── testing.md                   new
│   ├── windows-hooks.md             new
│   └── superpowers/specs/, plans/   this specification and its plan
├── hooks/
│   ├── hooks.json                   new
│   ├── run-hook.cmd                 new, polyglot dispatcher
│   └── session-start                new, extensionless bash
├── scripts/
│   ├── build_references.py          moved, unchanged
│   ├── bump_version.py              rewritten
│   └── protect-branches.sh          unchanged
├── skills/
│   ├── using-executive-team/SKILL.md   new, the bootstrap
│   ├── executive-team/              moved, unchanged
│   ├── meet/  setup/  gaps-report/  moved, unchanged
├── tests/
│   ├── fixtures/sample-officer.md   moved
│   ├── test_references.py           moved, paths adjusted
│   ├── test_repo_hygiene.py         moved, rules updated
│   ├── test_hooks.py                new
│   └── hooks/test-session-start.sh  new
├── .gitattributes                   extended
├── .gitignore                       unchanged
├── .version-bump.json               new
├── AGENTS.md                        rewritten
├── CLAUDE.md                        pointer to AGENTS.md, paths updated
├── CODE_OF_CONDUCT.md               unchanged
├── CONTRIBUTING.md                  paths and release flow updated
├── LICENSE                          unchanged
├── README.md                        single README, merged
└── RELEASE-NOTES.md                 v0.2.0 entry added
```

Files removed: `plugins/` (everything moved up), `plugins/executive-team/README.md` (merged into the root README), `.github/ISSUE_TEMPLATE/plugin_proposal.md` (the repository is one plugin).

### 4.1 Manifests

`.claude-plugin/plugin.json` keeps its fields; `version` becomes `0.2.0`. No `skills`, `agents` or `hooks` keys: Claude Code discovers `skills/`, `agents/` and `hooks/hooks.json` by convention when they sit beside `.claude-plugin/`.

`.claude-plugin/marketplace.json` keeps `name: executive-team-marketplace`, the owner block and the metadata block. The `executive-team` entry's source becomes the string `"./"`. The `executive-team-dev` entry's source becomes `{"source": "github", "repo": "raoofaltaher/executive-team-marketplace", "ref": "dev"}`; its version stays `<version>-dev`. If `claude plugin validate` rejects `ref` on a `github` source, the entry uses `{"source": "git-subdir", "url": "raoofaltaher/executive-team-marketplace", "path": ".", "ref": "dev"}` instead, and the choice is recorded in the release notes.

`.claude/settings.json` is unchanged: a `directory` marketplace at `./` with the plugin enabled. With the plugin at the root, the catalog's `"./"` source resolves to the repository itself.

### 4.2 Tags

Tags become `vX.Y.Z`. The previous `executive-team--vX.Y.Z` tags stay as they are.

## 5. The bootstrap

### 5.1 `hooks/hooks.json`

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "shell": "bash",
            "async": false
          }
        ]
      }
    ]
  }
}
```

`compact` is in the matcher so the bootstrap is re-injected after context compaction.

### 5.2 `hooks/run-hook.cmd`

Ultrapowers' dispatcher, with these properties kept exactly:

- First line `: << 'CMDBLOCK'`, so bash treats the cmd.exe block as a heredoc and cmd.exe runs it.
- cmd.exe half: requires a script name; looks for `bash.exe` in `C:\Program Files\Git\bin`, `C:\Program Files (x86)\Git\bin`, `%LOCALAPPDATA%\Programs\Git\bin` (only when `LOCALAPPDATA` is defined), then on PATH through `%SystemRoot%\System32\where.exe $PATH:bash`, skipping extensionless matches and the WSL launchers under System32, Sysnative and WindowsApps; exits 0 silently when no bash is found; runs bash outside any parenthesised block and returns its exit code.
- bash half: derives its directory by splitting `$0` on the last `/` or `\` (no `dirname`), then `exec "${BASH:-bash}" "<dir>/<script>" "$@"`.

The repository rule "no comments in code files" applies: the `REM` lines and `#` comments of the template are removed and their content moves to `docs/windows-hooks.md`.

### 5.3 `hooks/session-start`

An extensionless bash script (Claude Code on Windows prepends `bash` to any command containing `.sh`, which would break the dispatcher's quoting). Structure, following ultrapowers:

1. `set -euo pipefail`. Resolve `SCRIPT_DIR` from `$0` with builtins; `PLUGIN_ROOT` is its parent.
2. Read `skills/using-executive-team/SKILL.md` with `$(<file)`; if unreadable, the content is the string `Error reading using-executive-team skill`.
3. `escape_for_json` with parameter substitution for backslash, double quote, newline, carriage return and tab.
4. The nudge (section 5.4), computed from the hook's stdin JSON.
5. The context string:

   ```
   <EXTREMELY_IMPORTANT>\nYou have an executive team.\n\n**Below is the full content of your 'executive-team:using-executive-team' skill. It tells you who the team is and how to use it. For everything else, use the 'Skill' tool and the agents:**\n\n<skill content><nudge>\n</EXTREMELY_IMPORTANT>
   ```

   where `<nudge>` is empty or `\n\n` followed by the escaped nudge line.
6. Output through `emit_json`, which pipes `printf` through `cat` when `cat` is on PATH (absorbs EPIPE on Git Bash) and falls back to bare `printf`. Two shapes only:
   - `CLAUDE_PLUGIN_ROOT` set: `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}`
   - otherwise: `{"additionalContext": "..."}`
7. `exit 0` always. The script never writes to disk.

Builtins only, except `cat` and `cygpath`, both guarded by `command -v`.

### 5.4 The nudge

Inputs: the hook's stdin JSON, read with `read -r -d '' -t 1` when stdin is not a terminal; the `cwd` string field, parsed with the builtin JSON string reader from ultrapowers (handles `\"`, `\\`, `\/`; caps values at 4096 characters); Windows paths converted with `cygpath -u` when available, else backslashes replaced. When `cwd` is missing or not a directory, `$PWD` is used.

Rules, evaluated in order:

1. `EXECUTIVE_TEAM_NUDGE` equal to `off` (any case): no nudge.
2. Walk from the directory upward. If an `org-profile.yaml` file is found at any level: no nudge.
3. Otherwise, if a `.git` entry is found at any level: the nudge line is

   `This project has no org-profile.yaml. When the Owner first calls on the executive team here, offer /executive-team:setup before the first meeting.`

4. Otherwise (not inside a git repository): no nudge.

The wording is deliberately weaker than the template's "before other work": most projects are not executive-team projects, and the line must not push setup on a session that never asks for the team.

### 5.5 `skills/using-executive-team/SKILL.md`

Frontmatter: `name: using-executive-team`; `description: Use when starting any conversation - introduces the Owner's AI executive team (COO, CISO, CTO, CMO, CSO, CFO and a Chief of Staff), when to bring them in, and how to convene a meeting or ask one officer directly.`

Body, in this order and at this length (about 45 lines):

1. A `<SUBAGENT-STOP>` block: an officer or Chief of Staff dispatched as a subagent for a specific task ignores this skill and follows its own agent file and the protocol.
2. **Who is in the room.** One line each: the Owner chairs and decides; the Chief of Staff routes, fans out, synthesizes and records, taking no business position; then COO, CISO, CTO, CMO, CSO, CFO, each with its position title and three or four domain words taken from the agent descriptions.
3. **When to bring them in.** Three bullets: a business decision, plan, review or risk the Owner raises (convene through `/executive-team:meet`, or invoke the `executive-team:meet` skill when the Owner describes the need without the command); a question in one officer's domain (dispatch that officer by its `executive-team:<name>` agent and relay the answer in the officer's voice); the first time the team is used in a project with no `org-profile.yaml` (offer `/executive-team:setup`; `/executive-team:gaps-report` shows what the source matrix left blank).
4. **How the team works.** Four bullets stating today's behaviour: officers answer as their position, candidly, at most 300 words, ending with `Confidence:` and `Consult:` lines; required levels shape authority (3 leads, 2 answers and flags complex cases, 1 states basics and points to the level-3 holder); the Chief of Staff writes one executive brief and saves minutes under the configured minutes folder; `org-profile.yaml` overrides matrix values and is never committed.
5. **Where the rules live.** The protocol is the `executive-team:executive-team` skill; the routing index and gaps register are in its `references/` folder; each officer's full skills table is in its agent file.
6. **User instructions.** The Owner's own instructions (CLAUDE.md, AGENTS.md, direct requests) take precedence over this skill and over the protocol.

No red-flags table and no "1% chance" imperative: those shape coding-workflow behaviour in the template and have no equivalent here. The skill states facts about the team and the three entry points.

## 6. Version and release tooling

### 6.1 `.version-bump.json`

```json
{
  "files": [
    { "path": ".claude-plugin/plugin.json", "field": "version" },
    { "path": ".claude-plugin/marketplace.json", "field": "metadata.version" },
    { "path": ".claude-plugin/marketplace.json", "field": "plugins.0.version" },
    { "path": ".claude-plugin/marketplace.json", "field": "plugins.1.version", "suffix": "-dev" }
  ],
  "audit": {
    "exclude": ["RELEASE-NOTES.md", "docs", "tests", ".git", ".version-bump.json", "scripts/bump_version.py", "__pycache__"]
  }
}
```

A `suffix` entry means the stored value is `<version><suffix>` and the check compares after stripping the suffix.

### 6.2 `scripts/bump_version.py`

Python, standard library only. Modes:

- `bump_version.py <x.y.z>`: writes the version into every declared field (JSON files only; a non-JSON path is an error), preserving two-space indentation and a trailing newline. Prints each file written and the next commands: commit, tag `v<x.y.z>`.
- `bump_version.py --check`: prints each declared location and its value; exits 1 if the values differ after suffix stripping, or if any field is missing.
- `bump_version.py --audit`: runs `--check`, then walks the tree (skipping the `audit.exclude` paths and anything git-ignored, using `git ls-files`) and greps for the current version string outside the declared files; exits 1 and lists any hit. The README and CONTRIBUTING are therefore audited; a stale version in them fails the release.

The module exposes `declared_locations()`, `read_versions()`, `write_version()` and `audit()` so the tests import them.

### 6.3 Release flow (CONTRIBUTING.md)

1. On `dev`: `python scripts/bump_version.py <x.y.z>` and `python scripts/bump_version.py --audit`.
2. Add the `RELEASE-NOTES.md` entry.
3. Commit, open the `dev` to `main` pull request, merge with a merge commit.
4. Tag `v<x.y.z>` on `main`, push the tag, publish the GitHub release with the notes entry.

## 7. Tests

All suites run from the repository root. Prerequisites: Python 3.10 or later, bash (Git Bash on Windows), git. No Node, no `jq`, no `yq`.

### 7.1 Python suites (`python -m unittest discover -s tests`)

- `test_references.py`: unchanged assertions; the import path becomes `../scripts` relative to `tests/`.
- `test_repo_hygiene.py`, updated:
  - `ROOT` is the repository root.
  - Tracked-file rules: no `.xlsx`, `.xls`, `.csv`; nothing under `.remember/`, `build/`, `docs/executive/`, `plugins/`; no `org-profile.yaml`.
  - The ban on `docs/superpowers` is removed; the bans on the retired spreadsheet tooling stay.
  - Agent, skill and orchestration conventions as today, with root-relative paths.
  - New: `skills/using-executive-team/SKILL.md` exists, its frontmatter `name` is `using-executive-team`, its body contains `<SUBAGENT-STOP>`, the six officer codes and the strings `/executive-team:meet`, `/executive-team:setup`, `/executive-team:gaps-report`.
  - New: the catalog's `executive-team` entry has source `"./"` and the dev entry references ref `dev`.
  - New: `.github/workflows/ci.yml` exists.
- `test_hooks.py`, new:
  - `hooks/hooks.json` parses; it has exactly one `SessionStart` group with matcher `startup|clear|compact`, whose single hook has `type: command`, `shell: bash`, `async: false`, and a command ending in `run-hook.cmd" session-start`.
  - `git ls-files -s hooks/run-hook.cmd hooks/session-start` reports mode `100755` for both.
  - `.gitattributes` pins `hooks/session-start` and `*.cmd` to `eol=lf`; neither file contains a carriage return.
  - `hooks/run-hook.cmd` starts with `: << 'CMDBLOCK'` and contains `CMDBLOCK` on its own line later; neither hook file contains a `REM` or `#` comment line (the shebang is allowed).
  - `scripts/bump_version.py --check` exits 0 on the committed tree; `read_versions()` returns one distinct version; a temporary copy of the tree with a drifted field makes `--check` exit 1; `--audit` on the committed tree exits 0.

### 7.2 Hook shell test (`bash tests/hooks/test-session-start.sh`)

Written on the template's structure, with Python (`python3`, falling back to `python`) parsing the JSON output instead of Node. Every case runs the hook through `env -i` with a controlled `PATH`, `HOME` and the stdin JSON, from a temporary directory tree created by the test. Cases:

1. `CLAUDE_PLUGIN_ROOT` set: output parses as JSON; has `hookSpecificOutput.hookEventName == "SessionStart"`; `additionalContext` contains `You have an executive team` and the first heading of the bootstrap skill; no top-level `additionalContext` key.
2. No `CLAUDE_PLUGIN_ROOT`: output has top-level `additionalContext` and no `hookSpecificOutput`.
3. stdin `{"cwd": "<temp git repo without profile>"}`: context contains `This project has no org-profile.yaml`.
4. stdin `cwd` pointing at a subfolder of a temp git repo whose root holds `org-profile.yaml`: no nudge text.
5. stdin `cwd` pointing at a temp directory with no `.git` at or above it: no nudge text.
6. Case 3 with `EXECUTIVE_TEAM_NUDGE=off`: no nudge text.
7. stdin empty and no `cwd`: the hook exits 0 and emits valid JSON.
8. `PATH` empty: the hook exits 0 and emits valid JSON (builtins-only guarantee).
9. The dispatcher: `bash hooks/run-hook.cmd session-start` produces the same JSON as calling the script directly.
10. A Windows-style `cwd` with backslashes and a drive letter, when `cygpath` is available, is resolved and the nudge rules still apply; when `cygpath` is absent the case is reported as skipped.

The script prints `[PASS]`/`[FAIL]` per case and exits with the failure count.

### 7.3 `docs/testing.md`

One table: suite, command, what it proves, prerequisites. Plus the pre-pull-request command list and the note that the model-driven smoke scenarios (a meeting run by a subagent) are manual and not gated.

## 8. Continuous integration

`.github/workflows/ci.yml`:

- Triggers: `pull_request` targeting `dev` or `main`; `push` to `main`.
- Matrix: `ubuntu-latest` and `windows-latest`.
- Steps on both: checkout; set up Python 3.12; `python -m unittest discover -s tests`; `python scripts/build_references.py --check`; `python scripts/bump_version.py --check`; `bash tests/hooks/test-session-start.sh` (on Windows the runner's Git Bash, via `shell: bash`).
- Steps on Ubuntu only: ShellCheck on `hooks/session-start` at warning severity; `npm install -g @anthropic-ai/claude-code`, then `claude plugin validate . --strict`, `claude plugin validate agents --strict`, `claude plugin validate skills --strict`.
- No secrets, no model calls, no network beyond package installs.

Implementation must verify that `claude plugin validate` runs on a runner without a login. If it does not, the validate steps are replaced by a Python check in `test_hooks.py` that the manifest files parse and carry the required keys, and the workflow file states that `plugin validate` runs locally before a release. The outcome is recorded in `docs/testing.md`.

After the workflow's first green run, the `protect-main` and `protect-dev` rulesets get the workflow's job as a required status check (`docs/branch-protection.md` gains one line describing this; `scripts/protect-branches.sh` is not changed, since the check name only exists after the first run).

## 9. Documentation and community files

### 9.1 README.md (single)

Sections, in this order: title and illustration; one-paragraph "How it works"; Installation (marketplace add and plugin install, both as slash commands and as terminal commands; Updating with `/plugin marketplace update` and `/plugin update executive-team`; local development by opening the repository in Claude Code or `claude --plugin-dir <repo>`); The basic workflow (gaps report, setup, first meeting); What's inside (agents table, commands table, the protocol skill and the bootstrap skill, each with one line); How a meeting works (the current six steps); Customizing for your company (org-profile keys as today); Source and traceability (as today); Privacy (as today); When something goes wrong (open an issue with the bug template; what to include); Contributing (pointer to CONTRIBUTING.md and AGENTS.md, branch rules, Contributor Covenant); Development (the five check commands); License.

The plugin-level README is deleted; its content is the basis of the merged file. The illustration is referenced as `assets/plugin.png` by relative path.

### 9.2 AGENTS.md

Rewritten on the template's structure and voice, adapted to this project:

1. **If you are an AI agent.** Read before anything. Numbered mandatory checks: read the whole PR template; search open and closed PRs; confirm the problem was observed, not imagined; confirm the change belongs here and not in a separate plugin; disclose model, harness, harness version and installed plugins; show the complete diff to the human partner and get approval.
2. **Pull request requirements.** Target `dev`; full template; human reviewer named; one change per PR; evidence for behaviour changes.
3. **What we will not accept.** Edits to officer sections 1 to 4 (content of record; fixes go through `org-profile.yaml`); personal or company data; spreadsheet importers or sync scripts; third-party integrations, telemetry and network calls in agents, skills or hooks; behaviour-shaping wording changes without a before/after scenario; bundled or speculative changes; fork-specific or personal configuration as defaults; fabricated matrix content.
4. **Repository layout.** The tree from section 4, one line per entry.
5. **Before a pull request.** The command list: unit tests, references check, version check, hook test, `claude plugin validate` on the manifest, agents and skills.
6. **Understand the plugin before contributing.** Read the README, the protocol skill, the Chief of Staff, the bootstrap skill; run one meeting and read its minutes.

`CLAUDE.md` stays a short pointer to AGENTS.md with the updated paths and commands.

### 9.3 CONTRIBUTING.md

Same sections as today with: check commands run from the repository root; "What is welcome" no longer lists new plugins for the marketplace; the release flow of section 6.3; tag convention `vX.Y.Z`.

### 9.4 Templates

- `PULL_REQUEST_TEMPLATE.md`: the template's structure trimmed to: target-dev banner; Who is submitting (model and version, harness and version, installed plugins, human reviewer); What problem; What changes; Is this appropriate for this plugin (content-of-record and personal-data questions); Alternatives considered; Evidence (the check commands as checkboxes plus before/after for behaviour changes); Related issues and PRs; Human review checkbox.
- `ISSUE_TEMPLATE/bug_report.md`: environment table (plugin version, Claude Code version, model, OS, installed from, other plugins); what you ran; what happened; what you expected; the search-first checkbox.
- `ISSUE_TEMPLATE/feature_request.md`: problem, proposal, which officer or skill it touches, whether it needs matrix content (which is frozen).
- `ISSUE_TEMPLATE/config.yml`: unchanged.
- `ISSUE_TEMPLATE/plugin_proposal.md`: removed.

### 9.5 `docs/windows-hooks.md`

Why the dispatcher is a polyglot file; why hook scripts are extensionless; the bash lookup order on Windows and why the WSL launchers are skipped; the broken-PATH startup case and why the scripts use builtins; why output goes through `cat`; how to run the hook by hand to see its JSON. This is where the template's code comments now live.

## 10. Migration steps (summary; the plan details them)

1. Branch `feat/superpowers-shell` from `dev`.
2. `git mv` every tracked path under `plugins/executive-team/` to the root, except its README; delete `plugins/`.
3. Update the catalog, manifests, settings, tests and docs for the new paths; confirm `build_references.py --check` and the Python suites pass before adding anything new.
4. Add the hook files, the bootstrap skill, `.version-bump.json`, the rewritten bump script, the new tests, the workflow, the docs.
5. Set the executable bit on the two hook files with `git update-index --chmod=+x`, extend `.gitattributes`.
6. Run every check from section 7 and `claude plugin validate` locally; run a live session from the repository with the hook enabled and confirm the bootstrap appears and the nudge behaves in a project with and without a profile.
7. Bump to 0.2.0, add release notes, commit, open the pull request against `dev`.

## 11. Acceptance criteria

- A fresh Claude Code session opened in a project with the plugin enabled receives the bootstrap context at startup, after `/clear`, and after compaction; the nudge appears only in a git repository with no `org-profile.yaml` at or above the working directory.
- `claude plugin validate . --strict`, `agents --strict` and `skills --strict` pass at the repository root.
- `python -m unittest discover -s tests`, `python scripts/build_references.py --check`, `python scripts/bump_version.py --audit` and `bash tests/hooks/test-session-start.sh` pass on Windows (Git Bash) and on Linux.
- The CI workflow is green on the pull request to `dev` on both runners.
- `git log --follow` on any moved file shows its pre-move history.
- No agent file, protocol file or user-invoked skill differs from `dev` except by path.
- The repository contains no code comments in `.py`, `.sh`, `.cmd`, `.json` or hook files (docstrings and YAML template comments remain allowed, as before).
