# Superpowers Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the executive-team plugin to the repository root and give it the superpowers engineering shell: a SessionStart bootstrap hook, a one-screen bootstrap skill, declared-location version tooling, hook tests, continuous integration, and the template's documentation and contributor files.

**Architecture:** The repository becomes one Claude Code plugin that is also its own single-entry marketplace. One hook (`hooks/hooks.json` → `hooks/run-hook.cmd` → `hooks/session-start`) injects `skills/using-executive-team/SKILL.md` plus an org-profile nudge at startup, clear and compact. Version locations are declared in `.version-bump.json` and driven by `scripts/bump_version.py`. Tests are Python unittest plus one bash hook test; CI runs them on Ubuntu and Windows.

**Tech Stack:** Bash (Git Bash on Windows), Python 3.10+ standard library, Claude Code plugin conventions, GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-10-02-superpowers-shell-design.md`

## Global Constraints

- Content is frozen: no change to `agents/*.md`, `skills/executive-team/**`, `skills/meet/**`, `skills/setup/**`, `skills/gaps-report/**`, `scripts/build_references.py` beyond the move.
- No comments in code files (`.py`, `.sh`, `.cmd`, `.json`, `.yml`, hook scripts). Python docstrings are allowed. Explanations go in `docs/`.
- No third-party dependencies: hooks use bash builtins (plus `cat` and `cygpath` guarded by `command -v`); scripts and tests use the Python standard library.
- No telemetry and no network calls at runtime.
- The banned-pattern scan in `tests/test_repo_hygiene.py` stays and, from the root, covers every tracked text file including `docs/superpowers/`. No file other than that test may name the retired spreadsheet file format, its Python library, or the retired importer and verifier scripts. Write "spreadsheet" or "spreadsheet importer" when the concept is needed.
- Line endings LF everywhere; hook files executable in the index (`100755`).
- Version in this release: `0.2.0`. Tag convention `vX.Y.Z`.
- All commands run from the repository root unless a step says otherwise. Shell is Git Bash.
- Commit messages end with the line `RAOOF A.`.

## Review Focus

1. A session started in a folder that is not a git repository (home directory, scratch folder) must receive the bootstrap with no nudge. Pinned in Task 3, hook test case 5.
2. A Windows path in the hook's stdin (`C:\Users\...`) must be understood when `cygpath` exists; the hook must not crash when it does not. Pinned in Task 3, hook test case 10 and case 8.
3. An `org-profile.yaml` in a parent folder of the working directory counts as present (monorepo with the profile at the root). Pinned in Task 3, hook test case 4.
4. A drifted or missing version field must fail `--check`, not silently pass. Pinned in Task 4, `test_check_fails_on_drift` and `test_missing_field_is_an_error`.
5. The hook must keep emitting valid JSON when the bootstrap skill file is unreadable, so a broken install never breaks a session. Pinned in Task 3, hook test case 11.

---

### Task 1: Move the plugin to the repository root

**Files:**
- Move: every tracked path under `plugins/executive-team/` to the root, except `plugins/executive-team/README.md` (deleted; merged in Task 6)
- Modify: `.claude-plugin/marketplace.json`
- Modify: `tests/test_repo_hygiene.py` (after the move)
- Delete: `.github/ISSUE_TEMPLATE/plugin_proposal.md`

**Interfaces:**
- Produces: the root layout every later task assumes (`agents/`, `skills/`, `scripts/`, `tests/`, `.claude-plugin/plugin.json`).

- [ ] **Step 1: Move the tree with history**

```bash
git mv plugins/executive-team/.claude-plugin/plugin.json .claude-plugin/plugin.json
git mv plugins/executive-team/agents agents
git mv plugins/executive-team/skills skills
git mv plugins/executive-team/scripts/build_references.py scripts/build_references.py
git mv plugins/executive-team/tests tests
git rm -q plugins/executive-team/README.md
git rm -q .github/ISSUE_TEMPLATE/plugin_proposal.md
rm -rf plugins
git status --short | head -40
```

Expected: every line is `R` (renamed) or `D`; no `plugins/` path remains in `git ls-files`.

- [ ] **Step 2: Point the catalog at the root**

Replace the `plugins` array in `.claude-plugin/marketplace.json` so the two entries read:

```json
  "plugins": [
    {
      "name": "executive-team",
      "source": "./",
      "description": "An AI executive team (COO, CISO, CTO, CMO, CSO, CFO) plus a Chief of Staff. Bring real business cases to a candid multi-officer deliberation and get an executive brief with minutes.",
      "version": "0.1.1",
      "category": "productivity",
      "keywords": [
        "executive-team",
        "agents",
        "skills-matrix",
        "decision-support",
        "coo",
        "ciso",
        "cto",
        "cmo",
        "cso",
        "cfo"
      ]
    },
    {
      "name": "executive-team-dev",
      "source": {
        "source": "github",
        "repo": "raoofaltaher/executive-team-marketplace",
        "ref": "dev"
      },
      "description": "DEV BRANCH of executive-team for contributors and testers. Uninstall executive-team before installing this; the two register the same agents and skills.",
      "version": "0.1.1-dev"
    }
  ]
```

Leave `name`, `owner` and `metadata` as they are.

- [ ] **Step 3: Validate the manifests at the root**

Run:
```bash
claude plugin validate . --strict && claude plugin validate agents --strict && claude plugin validate skills --strict
```
Expected: three successes. If the `github` source with `ref` is rejected, replace the dev entry's source with `{"source": "git-subdir", "url": "raoofaltaher/executive-team-marketplace", "path": ".", "ref": "dev"}`, rerun, and note the choice for the release notes in Task 7.

- [ ] **Step 4: Update the hygiene test for the root layout**

In `tests/test_repo_hygiene.py`:

Replace
```python
            self.assertFalse(f.startswith((".remember/", "build/", "docs/executive/")), f)
```
with
```python
            self.assertFalse(f.startswith((".remember/", "build/", "docs/executive/", "plugins/")), f)
```

In the method that bans the retired tooling (the one whose body compiles the `banned` pattern), make two edits and leave the pattern itself unchanged:

1. In its `for gone in (...)` tuple, replace the entry `"docs/superpowers"` with `"plugins"`. Specs and plans now live in `docs/superpowers/` by design; the `plugins/` folder must be gone.
2. Replace its extension filter
   ```python
   if f.endswith((".md", ".json", ".yaml", ".py", ".txt")) and f != "tests/test_repo_hygiene.py":
   ```
   with
   ```python
   if f.endswith((".md", ".json", ".yaml", ".yml", ".py", ".txt", ".sh", ".cmd")) and f != "tests/test_repo_hygiene.py":
   ```

Add to `test_orchestration_uses_namespaced_agents_and_plugin_root`, before the `for a in AGENTS[1:]` loop:
```python
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8") as fh:
            catalog = json.load(fh)
        by_name = {p["name"]: p for p in catalog["plugins"]}
        self.assertEqual(by_name["executive-team"]["source"], "./")
        self.assertEqual(by_name["executive-team-dev"]["source"]["ref"], "dev")
```
and add `json` to the first import line: `import json, os, re, subprocess, sys, unittest`.

- [ ] **Step 5: Run the suites and the references check**

Run:
```bash
python -m unittest discover -s tests -v 2>&1 | tail -5
python scripts/build_references.py --check
```
Expected: `OK` for both. The references check passes unchanged because the script resolves `agents/` and `skills/executive-team/references/` from its own location.

- [ ] **Step 6: Confirm history follows a moved file**

Run: `git log --follow --oneline -- agents/chief-of-staff.md | wc -l`
Expected: more than 1.

- [ ] **Step 7: Commit**

```bash
git add -A
git commit -m "refactor: move the executive-team plugin to the repository root

The repository is now one plugin that is also its own marketplace, the
superpowers layout. Catalog sources point at ./ and at the dev branch.

RAOOF A."
```

---

### Task 2: The bootstrap skill

**Files:**
- Create: `skills/using-executive-team/SKILL.md`
- Modify: `tests/test_repo_hygiene.py`

**Interfaces:**
- Produces: `skills/using-executive-team/SKILL.md`, read verbatim by `hooks/session-start` in Task 3. Its first body heading is `## Who is in the room` (the hook test asserts on it).

- [ ] **Step 1: Write the failing test**

Add to `tests/test_repo_hygiene.py`, inside `HygieneTests`:
```python
    def test_bootstrap_skill_introduces_the_team(self):
        t = read("skills", "using-executive-team", "SKILL.md")
        self.assertTrue(t.startswith("---\nname: using-executive-team\n"), t[:60])
        self.assertIn("<SUBAGENT-STOP>", t)
        self.assertIn("## Who is in the room", t)
        for code in ("COO", "CISO", "CTO", "CMO", "CSO", "CFO"):
            self.assertIn(code, t)
        for token in ("/executive-team:meet", "/executive-team:setup", "/executive-team:gaps-report",
                      "executive-team:executive-team", "Confidence:", "Consult:", "org-profile.yaml"):
            self.assertIn(token, t)
        self.assertLess(len(t.splitlines()), 60, "the bootstrap must stay one screen")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m unittest tests.test_repo_hygiene.HygieneTests.test_bootstrap_skill_introduces_the_team`
Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 3: Write the skill**

Create `skills/using-executive-team/SKILL.md`:

````markdown
---
name: using-executive-team
description: Use when starting any conversation - introduces the Owner's AI executive team (COO, CISO, CTO, CMO, CSO, CFO and a Chief of Staff), when to bring them in, and how to convene a meeting or ask one officer directly.
---

<SUBAGENT-STOP>
If you were dispatched as an officer or as the Chief of Staff to carry out a specific task, ignore this skill. Your agent file and the `executive-team:executive-team` protocol govern you.
</SUBAGENT-STOP>

You are working for the Owner, who has an AI executive team available in this session. Nobody on it decides for the Owner.

## Who is in the room

- **Owner**: chairs the team and makes every decision.
- **Chief of Staff** (`executive-team:chief-of-staff`): routes a topic to the right officers, runs them in parallel, synthesizes one executive brief, records minutes. Takes no business position.
- **COO** (`executive-team:chief-operating-officer`): operations, delivery, customer success, SOPs, KPIs, SLAs.
- **CISO** (`executive-team:chief-information-security-officer`): security strategy, compliance, risk assessment, incident response, identity and access.
- **CTO** (`executive-team:chief-technology-officer`): technology roadmap, architecture, engineering standards, tooling, technical delivery.
- **CMO** (`executive-team:chief-marketing-officer`): brand, positioning, content, growth marketing, market and competitive intelligence.
- **CSO** (`executive-team:chief-sales-officer`): revenue, pipeline, key accounts, pricing and packaging, partnerships.
- **CFO** (`executive-team:chief-financial-officer`): financial strategy, budgets, treasury and runway, pricing models, controls, reporting.

## When to bring them in

- The Owner raises a business decision, plan, review, idea or risk: convene the team with `/executive-team:meet [brainstorm|decide|review|plan|risk] <topic>`, or invoke the `executive-team:meet` skill when the Owner describes the need without typing the command.
- The Owner asks something squarely in one officer's domain ("what would my CTO say", "ask the CFO"): dispatch that officer's agent and relay the answer in the officer's voice.
- The team is used for the first time in a project with no `org-profile.yaml`: offer `/executive-team:setup`. `/executive-team:gaps-report` lists what the source matrix left blank.

## How the team works

- Officers answer as their position, candidly, position first, in at most 300 words, ending with `Confidence:` and `Consult:` lines. They say `outside my competence` rather than guess.
- Required skill levels shape authority: level 3 answers with authority, level 2 answers independently and flags complex cases, level 1 states the basics and names the officer who holds the skill at level 3.
- The Chief of Staff writes one executive brief (summary, positions, agreement, disagreement, risks, recommended decision, open questions, next steps) and saves minutes under the configured minutes folder, in the Owner's language.
- `org-profile.yaml` overrides matrix values (departments, managers, levels, strategic objectives) and is never committed.

## Where the rules live

- The protocol: the `executive-team:executive-team` skill (level definitions, officer rules, meeting modes, brief and minutes formats).
- The routing index and the gaps register: `references/` inside that skill.
- Each officer's full skills table with source pointers: its agent file.

## User instructions

The Owner's own instructions (CLAUDE.md, AGENTS.md, direct requests) take precedence over this skill and over the protocol.
````

- [ ] **Step 4: Run the tests**

Run: `python -m unittest discover -s tests 2>&1 | tail -3 && claude plugin validate skills --strict`
Expected: `OK` and a validation success.

- [ ] **Step 5: Commit**

```bash
git add skills/using-executive-team/SKILL.md tests/test_repo_hygiene.py
git commit -m "feat: add the using-executive-team bootstrap skill

RAOOF A."
```

---

### Task 3: The SessionStart hook

**Files:**
- Create: `hooks/hooks.json`, `hooks/run-hook.cmd`, `hooks/session-start`
- Create: `tests/hooks/test-session-start.sh`, `tests/test_hooks.py`
- Modify: `.gitattributes`

**Interfaces:**
- Consumes: `skills/using-executive-team/SKILL.md` (Task 2).
- Produces: a hook that prints one JSON object on stdout and exits 0. Environment: `CLAUDE_PLUGIN_ROOT` selects the nested shape; `EXECUTIVE_TEAM_NUDGE=off` disables the nudge. Stdin: Claude Code's hook JSON with a `cwd` field.

- [ ] **Step 1: Write the Python file-level tests (failing)**

Create `tests/test_hooks.py`:

```python
import json, os, subprocess, unittest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8", newline="") as fh:
        return fh.read()


class HookFileTests(unittest.TestCase):
    def test_hooks_json_registers_one_session_start_command(self):
        cfg = json.loads(read("hooks", "hooks.json"))
        self.assertEqual(list(cfg["hooks"]), ["SessionStart"])
        groups = cfg["hooks"]["SessionStart"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["matcher"], "startup|clear|compact")
        self.assertEqual(len(groups[0]["hooks"]), 1)
        h = groups[0]["hooks"][0]
        self.assertEqual(h["type"], "command")
        self.assertEqual(h["shell"], "bash")
        self.assertIs(h["async"], False)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", h["command"])
        self.assertTrue(h["command"].endswith('run-hook.cmd" session-start'), h["command"])

    def test_hook_files_are_executable_lf_and_comment_free(self):
        out = subprocess.run(["git", "ls-files", "-s", "hooks/run-hook.cmd", "hooks/session-start"],
                             cwd=ROOT, capture_output=True, text=True).stdout
        self.assertEqual([l.split()[0] for l in out.splitlines()], ["100755", "100755"], out)
        attrs = read(".gitattributes")
        self.assertIn("hooks/session-start text eol=lf", attrs)
        self.assertIn("*.cmd text eol=lf", attrs)
        for name in ("run-hook.cmd", "session-start"):
            text = read("hooks", name)
            self.assertNotIn("\r", text, name)
            for n, line in enumerate(text.splitlines(), 1):
                s = line.strip()
                self.assertFalse(s.upper().startswith("REM "), f"{name}:{n}")
                self.assertFalse(s.startswith("#") and not s.startswith("#!"), f"{name}:{n}")
        cmd = read("hooks", "run-hook.cmd")
        self.assertTrue(cmd.startswith(": << 'CMDBLOCK'\n"), cmd[:40])
        self.assertIn("\nCMDBLOCK\n", cmd)


if __name__ == "__main__":
    unittest.main()
```

Run: `python -m unittest tests.test_hooks -v`
Expected: both FAIL (`FileNotFoundError`).

- [ ] **Step 2: Write the shell test (failing)**

Create `tests/hooks/test-session-start.sh`:

```bash
#!/usr/bin/env bash
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
HOOK="$REPO_ROOT/hooks/session-start"
WRAPPER="$REPO_ROOT/hooks/run-hook.cmd"
PY=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c "import json" >/dev/null 2>&1; then
        PY="$candidate"
        break
    fi
done
if [ -z "$PY" ]; then
    echo "  [FAIL] no working python3 or python on PATH"
    exit 1
fi
FAILURES=0
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

pass() { echo "  [PASS] $1"; }
fail() { echo "  [FAIL] $1"; FAILURES=$((FAILURES + 1)); }
skip() { echo "  [SKIP] $1"; }

run_hook() {
    local stdin_json="$1"
    shift
    printf '%s' "$stdin_json" | env -i PATH="$PATH" HOME="$WORK" "$@" "$BASH" "$HOOK" 2>&1
}

CHECK_PY='
import json, os, sys
raw = sys.stdin.buffer.read().decode("utf-8")
try:
    payload = json.loads(raw)
except ValueError as e:
    sys.exit("invalid JSON: %s\n%s" % (e, raw[:300]))
if os.environ["SHAPE"] == "nested":
    if "additionalContext" in payload:
        sys.exit("top-level additionalContext present in nested shape")
    hso = payload["hookSpecificOutput"]
    if hso["hookEventName"] != "SessionStart":
        sys.exit("wrong hookEventName")
    ctx = hso["additionalContext"]
else:
    if "hookSpecificOutput" in payload:
        sys.exit("hookSpecificOutput present in flat shape")
    ctx = payload["additionalContext"]
c = os.environ["CONTAINS"]
n = os.environ["NOT_CONTAINS"]
if c and c not in ctx:
    sys.exit("missing: " + c)
if n and n in ctx:
    sys.exit("unexpected: " + n)
'

check_json() {
    local output="$1" shape="$2" contains="$3" not_contains="$4"
    printf '%s' "$output" | SHAPE="$shape" CONTAINS="$contains" NOT_CONTAINS="$not_contains" "$PY" -c "$CHECK_PY"
}

expect() {
    local description="$1" shape="$2" contains="$3" not_contains="$4" output="$5"
    local err
    if err="$(check_json "$output" "$shape" "$contains" "$not_contains" 2>&1)"; then
        pass "$description"
    else
        fail "$description"
        echo "    $err" | head -5
    fi
}

NUDGE="This project has no org-profile.yaml"
mkdir -p "$WORK/repo-noprofile/.git" "$WORK/repo-profile/.git" "$WORK/repo-profile/sub" "$WORK/plain"
: > "$WORK/repo-profile/org-profile.yaml"

echo "SessionStart hook"

out="$(run_hook '{}' CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
expect "1 nested shape under CLAUDE_PLUGIN_ROOT with the bootstrap body" nested "## Who is in the room" "" "$out"
expect "1b nested shape announces the team" nested "You have an executive team" "" "$out"

out="$(run_hook '{}')"
expect "2 flat shape without CLAUDE_PLUGIN_ROOT" flat "## Who is in the room" "" "$out"

out="$(run_hook "{\"cwd\": \"$WORK/repo-noprofile\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
expect "3 nudge in a git repo without org-profile.yaml" nested "$NUDGE" "" "$out"

out="$(run_hook "{\"cwd\": \"$WORK/repo-profile/sub\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
expect "4 no nudge when org-profile.yaml sits in a parent folder" nested "## Who is in the room" "$NUDGE" "$out"

ancestor_has_git=0
d="$WORK"
while [ -n "$d" ] && [ "$d" != "/" ] && [ "$d" != "." ]; do
    if [ -e "$d/.git" ]; then ancestor_has_git=1; fi
    d="${d%/*}"
done
if [ "$ancestor_has_git" = 1 ]; then
    skip "5 no nudge outside a git repo (temp dir lives inside a git repo)"
else
    out="$(run_hook "{\"cwd\": \"$WORK/plain\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
    expect "5 no nudge outside a git repo" nested "## Who is in the room" "$NUDGE" "$out"
fi

out="$(run_hook "{\"cwd\": \"$WORK/repo-noprofile\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" EXECUTIVE_TEAM_NUDGE=off)"
expect "6 EXECUTIVE_TEAM_NUDGE=off silences the nudge" nested "## Who is in the room" "$NUDGE" "$out"

out="$(run_hook '' CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
expect "7 empty stdin still yields valid JSON" nested "## Who is in the room" "" "$out"

out="$(printf '%s' "{\"cwd\": \"$WORK/repo-noprofile\"}" | env -i PATH= HOME="$WORK" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" "$BASH" "$HOOK" 2>&1)"
expect "8 empty PATH still yields the nudge and valid JSON" nested "$NUDGE" "" "$out"

direct="$(run_hook "{\"cwd\": \"$WORK/repo-noprofile\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
via_wrapper="$(printf '%s' "{\"cwd\": \"$WORK/repo-noprofile\"}" | env -i PATH="$PATH" HOME="$WORK" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" "$BASH" "$WRAPPER" session-start 2>&1)"
if [ "$direct" = "$via_wrapper" ]; then
    pass "9 run-hook.cmd dispatches to session-start with identical output"
else
    fail "9 run-hook.cmd dispatches to session-start with identical output"
    printf '%s\n' "$via_wrapper" | head -3
fi

if command -v cygpath >/dev/null 2>&1; then
    win="$(cygpath -w "$WORK/repo-noprofile")"
    win_json="${win//\\/\\\\}"
    out="$(run_hook "{\"cwd\": \"$win_json\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
    expect "10 Windows-style cwd is resolved" nested "$NUDGE" "" "$out"
else
    skip "10 Windows-style cwd (cygpath not available)"
fi

broken="$WORK/broken-plugin"
mkdir -p "$broken/hooks" "$broken/skills"
cp "$HOOK" "$broken/hooks/session-start"
out="$(printf '%s' '{}' | env -i PATH="$PATH" HOME="$WORK" CLAUDE_PLUGIN_ROOT="$broken" "$BASH" "$broken/hooks/session-start" 2>&1)"
expect "11 unreadable bootstrap skill still yields valid JSON" nested "Error reading using-executive-team skill" "" "$out"

echo
if [ "$FAILURES" -eq 0 ]; then
    echo "All hook tests passed"
else
    echo "$FAILURES hook test(s) failed"
fi
exit "$FAILURES"
```

Run: `bash tests/hooks/test-session-start.sh`
Expected: failures on every case (hook missing).

- [ ] **Step 3: Write `hooks/hooks.json`**

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

- [ ] **Step 4: Write `hooks/run-hook.cmd`**

Write the file with the Write tool (not a heredoc), LF endings:

```
: << 'CMDBLOCK'
@echo off
if "%~1"=="" (
    echo run-hook.cmd: missing script name >&2
    exit /b 1
)
setlocal
set "HOOK_DIR=%~dp0"
set "BASH_EXE="
if exist "C:\Program Files\Git\bin\bash.exe" set "BASH_EXE=C:\Program Files\Git\bin\bash.exe"
if not defined BASH_EXE if exist "C:\Program Files (x86)\Git\bin\bash.exe" set "BASH_EXE=C:\Program Files (x86)\Git\bin\bash.exe"
if not defined BASH_EXE if defined LOCALAPPDATA if exist "%LOCALAPPDATA%\Programs\Git\bin\bash.exe" set "BASH_EXE=%LOCALAPPDATA%\Programs\Git\bin\bash.exe"
if not defined BASH_EXE if defined SystemRoot for /f "delims=" %%B in ('"%SystemRoot%\System32\where.exe" $PATH:bash 2^>nul') do if not defined BASH_EXE if not "%%~xB"=="" if /i not "%%~dpB"=="%SystemRoot%\System32\" if /i not "%%~dpB"=="%SystemRoot%\Sysnative\" if /i not "%%~dpB"=="%LOCALAPPDATA%\Microsoft\WindowsApps\" set "BASH_EXE=%%B"
if not defined BASH_EXE exit /b 0
"%BASH_EXE%" "%HOOK_DIR%%~1" %2 %3 %4 %5 %6 %7 %8 %9
exit /b %ERRORLEVEL%
CMDBLOCK
case "$0" in
  */*|*\\*) SCRIPT_DIR="$(cd "${0%[/\\]*}" && pwd)" ;;
  *) SCRIPT_DIR="$(pwd)" ;;
esac
SCRIPT_NAME="$1"
shift
exec "${BASH:-bash}" "${SCRIPT_DIR}/${SCRIPT_NAME}" "$@"
```

- [ ] **Step 5: Write `hooks/session-start`**

Write with the Write tool, LF endings, no `.sh` extension:

```bash
#!/usr/bin/env bash
set -euo pipefail

case "$0" in
  */*|*\\*) SCRIPT_DIR="$(cd "${0%[/\\]*}" && pwd)" ;;
  *) SCRIPT_DIR="$(pwd)" ;;
esac
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

skill_md="${PLUGIN_ROOT}/skills/using-executive-team/SKILL.md"
if [ -r "$skill_md" ]; then
  skill_content="$(<"$skill_md")"
else
  skill_content="Error reading using-executive-team skill"
fi

NUDGE_NO_PROFILE="This project has no org-profile.yaml. When the Owner first calls on the executive team here, offer /executive-team:setup before the first meeting."

escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}

read_hook_input() {
    local input=""
    if [ ! -t 0 ]; then
        IFS= read -r -d '' -t 1 input || true
    fi
    printf '%s' "$input"
}

json_string_value() {
    local json="$1" key="$2" rest value="" ch
    case "$json" in
        *"\"$key\""*) ;;
        *) return 1 ;;
    esac
    rest="${json#*\"$key\"}"
    rest="${rest#"${rest%%[![:space:]]*}"}"
    [ "${rest:0:1}" = ":" ] || return 1
    rest="${rest:1}"
    rest="${rest#"${rest%%[![:space:]]*}"}"
    [ "${rest:0:1}" = '"' ] || return 1
    rest="${rest:1:4096}"
    while [ -n "$rest" ]; do
        ch="${rest:0:1}"
        case "$ch" in
            '"')
                printf '%s' "$value"
                return 0
                ;;
            '\')
                case "${rest:1:1}" in
                    '"' | '\' | '/') value+="${rest:1:1}" ;;
                    *) return 1 ;;
                esac
                rest="${rest:2}"
                ;;
            *)
                value+="$ch"
                rest="${rest:1}"
                ;;
        esac
    done
    return 1
}

to_posix_dir() {
    local dir="$1"
    case "$dir" in
        [A-Za-z]:\\* | [A-Za-z]:/* | *\\*)
            if command -v cygpath >/dev/null 2>&1; then
                dir="$(cygpath -u "$dir" 2>/dev/null || printf '%s' "$dir")"
            else
                dir="${dir//\\//}"
            fi
            ;;
    esac
    printf '%s' "$dir"
}

parent_dir() {
    local d="${1%/}"
    case "$d" in
        */*) d="${d%/*}"; printf '%s' "${d:-/}" ;;
        *) printf '.' ;;
    esac
}

find_upward() {
    local dir="$1" name="$2" parent
    while [ -n "$dir" ]; do
        if [ -e "${dir%/}/$name" ]; then
            return 0
        fi
        parent="$(parent_dir "$dir")"
        if [ "$parent" = "$dir" ] || [ "$parent" = "." ]; then
            return 1
        fi
        dir="$parent"
    done
    return 1
}

project_nudge() {
    local input dir
    case "${EXECUTIVE_TEAM_NUDGE:-}" in
        [Oo][Ff][Ff]) return 0 ;;
    esac
    input="$(read_hook_input)"
    dir="$(json_string_value "$input" cwd || true)"
    dir="$(to_posix_dir "$dir")"
    if [ -z "$dir" ] || [ ! -d "$dir" ]; then
        dir="$PWD"
    fi
    if find_upward "$dir" org-profile.yaml; then
        return 0
    fi
    if find_upward "$dir" .git; then
        printf '%s' "$NUDGE_NO_PROFILE"
    fi
    return 0
}

skill_escaped="$(escape_for_json "$skill_content")"
nudge_line="$(project_nudge || true)"
nudge_escaped=""
if [ -n "$nudge_line" ]; then
    nudge_escaped="\n\n$(escape_for_json "$nudge_line")"
fi
session_context="<EXTREMELY_IMPORTANT>\nYou have an executive team.\n\n**Below is the full content of your 'executive-team:using-executive-team' skill. It tells you who the team is and how to use it. For everything else, use the 'Skill' tool and the agents:**\n\n${skill_escaped}${nudge_escaped}\n</EXTREMELY_IMPORTANT>"

emit() {
    if command -v cat >/dev/null 2>&1; then
        printf '%s\n' "$1" | cat
    else
        printf '%s\n' "$1"
    fi
}

if [ -n "${CLAUDE_PLUGIN_ROOT:-}" ]; then
    emit "{\"hookSpecificOutput\": {\"hookEventName\": \"SessionStart\", \"additionalContext\": \"${session_context}\"}}"
else
    emit "{\"additionalContext\": \"${session_context}\"}"
fi

exit 0
```

- [ ] **Step 6: Line endings and executable bits**

Append to `.gitattributes`:
```
hooks/session-start text eol=lf
*.cmd text eol=lf
*.sh text eol=lf
*.png binary
```

Run:
```bash
git add .gitattributes hooks tests/hooks/test-session-start.sh tests/test_hooks.py
git update-index --chmod=+x hooks/run-hook.cmd hooks/session-start tests/hooks/test-session-start.sh
git ls-files -s hooks tests/hooks
```
Expected: `100755` for the two hook files and the test script, `100644` for `hooks.json`.

- [ ] **Step 7: Run the hook tests**

Run:
```bash
bash tests/hooks/test-session-start.sh
python -m unittest tests.test_hooks -v
shellcheck --severity=warning hooks/session-start
```
Expected: `All hook tests passed` (case 5 or 10 may print `[SKIP]` with a reason), both Python tests pass, ShellCheck prints nothing.

If case 8 fails on Git Bash because `cd`/`pwd` need PATH, inspect the error text printed under the case; the script must use only builtins before `emit`, so the fix is in the script, never in the test.

- [ ] **Step 8: Validate the plugin with hooks present**

Run: `claude plugin validate . --strict`
Expected: success; the validator reads `hooks/hooks.json` by convention.

- [ ] **Step 9: Commit**

```bash
git add -A
git commit -m "feat: SessionStart bootstrap hook with org-profile nudge

Polyglot dispatcher and builtins-only hook script after ultrapowers'
hardened versions; nested output under CLAUDE_PLUGIN_ROOT, flat otherwise.

RAOOF A."
```

---

### Task 4: Declared-location version tooling

**Files:**
- Create: `.version-bump.json`
- Rewrite: `scripts/bump_version.py`
- Modify: `tests/test_hooks.py` (add `VersionToolTests`)

**Interfaces:**
- Produces: `bump_version.declared_locations(root)`, `read_versions(root)`, `write_version(version, root)`, `check(root)`, `audit(root)`, and the CLI `bump_version.py <x.y.z> | --check | --audit [--root DIR]`. Task 7 runs `bump_version.py 0.2.0` and `--audit`.

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_hooks.py` (after the imports add `import shutil, sys, tempfile` and `sys.path.insert(0, os.path.join(ROOT, "scripts"))` followed by `import bump_version`):

```python
class VersionToolTests(unittest.TestCase):
    def _copy_tree(self, d):
        shutil.copy(os.path.join(ROOT, ".version-bump.json"), d)
        shutil.copytree(os.path.join(ROOT, ".claude-plugin"), os.path.join(d, ".claude-plugin"))

    def test_declared_versions_agree_with_plugin_json(self):
        rows = bump_version.read_versions(ROOT)
        self.assertEqual(len(rows), 4, rows)
        self.assertEqual(len({v for *_, v in rows}), 1, rows)
        self.assertEqual(rows[0][3], json.loads(read(".claude-plugin", "plugin.json"))["version"])
        dev = [r for r in rows if r[1] == "plugins.1.version"][0]
        self.assertTrue(dev[2].endswith("-dev"), dev)

    def test_write_then_check_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            self._copy_tree(d)
            written = bump_version.write_version("9.9.9", root=d)
            self.assertEqual(written, [".claude-plugin/marketplace.json", ".claude-plugin/plugin.json"])
            self.assertEqual(bump_version.check(root=d), "9.9.9")
            catalog = json.loads(open(os.path.join(d, ".claude-plugin", "marketplace.json"), encoding="utf-8").read())
            self.assertEqual(catalog["plugins"][1]["version"], "9.9.9-dev")
            self.assertEqual(catalog["metadata"]["version"], "9.9.9")

    def test_check_fails_on_drift(self):
        with tempfile.TemporaryDirectory() as d:
            self._copy_tree(d)
            p = os.path.join(d, ".claude-plugin", "plugin.json")
            data = json.loads(open(p, encoding="utf-8").read())
            data["version"] = "1.2.3"
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            self.assertIsNone(bump_version.check(root=d))
            r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "bump_version.py"), "--check", "--root", d],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("drift", r.stdout)

    def test_missing_field_is_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            self._copy_tree(d)
            p = os.path.join(d, ".claude-plugin", "plugin.json")
            data = json.loads(open(p, encoding="utf-8").read())
            del data["version"]
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            with self.assertRaises(ValueError):
                bump_version.read_versions(d)

    def test_cli_check_and_audit_pass_on_the_committed_tree(self):
        for mode in ("--check", "--audit"):
            r = subprocess.run([sys.executable, "scripts/bump_version.py", mode], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, mode + "\n" + r.stdout + r.stderr)

    def test_cli_rejects_bad_version(self):
        r = subprocess.run([sys.executable, "scripts/bump_version.py", "1.2"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
```

Run: `python -m unittest tests.test_hooks.VersionToolTests`
Expected: FAIL (`AttributeError` on the new functions, `FileNotFoundError` on `.version-bump.json`).

- [ ] **Step 2: Create `.version-bump.json`**

```json
{
  "files": [
    { "path": ".claude-plugin/plugin.json", "field": "version" },
    { "path": ".claude-plugin/marketplace.json", "field": "metadata.version" },
    { "path": ".claude-plugin/marketplace.json", "field": "plugins.0.version" },
    { "path": ".claude-plugin/marketplace.json", "field": "plugins.1.version", "suffix": "-dev" }
  ],
  "audit": {
    "exclude": [
      "RELEASE-NOTES.md",
      "docs",
      "tests",
      ".version-bump.json",
      "scripts/bump_version.py"
    ]
  }
}
```

- [ ] **Step 3: Rewrite `scripts/bump_version.py`**

```python
"""Keep the plugin version identical in every location .version-bump.json declares.

Usage:
  python scripts/bump_version.py <x.y.z>            write the version into every declared field
  python scripts/bump_version.py --check            print every declared location; fail on drift
  python scripts/bump_version.py --audit            --check, then fail if the version appears in an undeclared tracked file
  python scripts/bump_version.py ... --root <dir>   operate on another checkout (tests use this)

A declared entry may carry "suffix": the stored value is <version><suffix> and
comparisons strip it. The audit skips the paths under audit.exclude.
"""
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")


def load_config(root=ROOT):
    with open(os.path.join(root, ".version-bump.json"), encoding="utf-8") as fh:
        return json.load(fh)


def declared_locations(root=ROOT):
    return [(e["path"], e["field"], e.get("suffix", "")) for e in load_config(root)["files"]]


def _descend(data, parts):
    for p in parts:
        data = data[int(p)] if isinstance(data, list) else data[p]
    return data


def _load_json(root, path):
    with open(os.path.join(root, path), encoding="utf-8") as fh:
        return json.load(fh)


def _save_json(root, path, data):
    with open(os.path.join(root, path), "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)
        fh.write("\n")


def read_versions(root=ROOT):
    rows = []
    for path, field, suffix in declared_locations(root):
        try:
            raw = str(_descend(_load_json(root, path), field.split(".")))
        except (KeyError, IndexError, TypeError):
            raise ValueError(f"{path}: field {field} is missing")
        if suffix and not raw.endswith(suffix):
            raise ValueError(f"{path}: field {field} should end with {suffix}, found {raw}")
        rows.append((path, field, raw, raw[: len(raw) - len(suffix)] if suffix else raw))
    return rows


def write_version(version, root=ROOT):
    written = set()
    for path, field, suffix in declared_locations(root):
        data = _load_json(root, path)
        parts = field.split(".")
        parent = _descend(data, parts[:-1])
        key = int(parts[-1]) if isinstance(parent, list) else parts[-1]
        parent[key] = version + suffix
        _save_json(root, path, data)
        written.add(path)
    return sorted(written)


def check(root=ROOT):
    rows = read_versions(root)
    for path, field, raw, _ in rows:
        print(f"{path} {field} = {raw}")
    distinct = sorted({v for _, _, _, v in rows})
    if len(distinct) != 1:
        print(f"ERROR: version drift across declared locations: {distinct}")
        return None
    return distinct[0]


def audit(root=ROOT):
    version = check(root)
    if version is None:
        return None, []
    excluded = [e.rstrip("/") for e in load_config(root).get("audit", {}).get("exclude", [])]
    declared = {p for p, _, _ in declared_locations(root)}
    tracked = subprocess.run(["git", "ls-files"], cwd=root, capture_output=True, text=True).stdout.splitlines()
    hits = []
    for f in tracked:
        if not f or f in declared or any(f == e or f.startswith(e + "/") for e in excluded):
            continue
        try:
            with open(os.path.join(root, f), encoding="utf-8") as fh:
                for n, line in enumerate(fh, 1):
                    if version in line:
                        hits.append(f"{f}:{n}: {line.strip()}")
        except (UnicodeDecodeError, OSError):
            continue
    for h in hits:
        print("ERROR: version string outside declared files:", h)
    return version, hits


def main(argv):
    root = ROOT
    if "--root" in argv:
        i = argv.index("--root")
        root = os.path.abspath(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    if argv == ["--check"]:
        try:
            return 0 if check(root) else 1
        except ValueError as e:
            print("ERROR:", e)
            return 1
    if argv == ["--audit"]:
        try:
            version, hits = audit(root)
        except ValueError as e:
            print("ERROR:", e)
            return 1
        if version is None or hits:
            return 1
        print(f"All clear: {version}")
        return 0
    if len(argv) == 1 and VERSION_RE.match(argv[0]):
        for path in write_version(argv[0], root):
            print(f"updated {path}")
        print(f"next: git commit -am 'release: v{argv[0]}' && git tag v{argv[0]}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 4: Run the tests**

Run: `python -m unittest tests.test_hooks -v 2>&1 | tail -12 && python scripts/bump_version.py --audit`
Expected: all tests pass; the audit prints the four locations at `0.1.1` and `All clear: 0.1.1`.

If the audit reports a hit in `README.md` or `CONTRIBUTING.md`, that is a real stale version string: remove it from the prose (the README must not state the version number).

- [ ] **Step 5: Commit**

```bash
git add .version-bump.json scripts/bump_version.py tests/test_hooks.py
git commit -m "feat: version tooling driven by .version-bump.json with --check and --audit

RAOOF A."
```

---

### Task 5: Continuous integration

**Files:**
- Create: `.github/workflows/ci.yml`
- Modify: `tests/test_repo_hygiene.py`

**Interfaces:**
- Consumes: every command from Tasks 1 to 4.
- Produces: the job name `checks` that Task 6's branch-protection note refers to.

- [ ] **Step 1: Write the failing test**

Add to `HygieneTests` in `tests/test_repo_hygiene.py`:
```python
    def test_ci_workflow_runs_every_static_check(self):
        wf = read(".github", "workflows", "ci.yml")
        for cmd in ("python -m unittest discover -s tests", "build_references.py --check", "bump_version.py --check",
                    "bash tests/hooks/test-session-start.sh", "shellcheck", "claude plugin validate . --strict"):
            self.assertIn(cmd, wf, cmd)
        self.assertIn("windows-latest", wf)
        self.assertIn("ubuntu-latest", wf)
```
Run: `python -m unittest tests.test_repo_hygiene.HygieneTests.test_ci_workflow_runs_every_static_check`
Expected: FAIL with `FileNotFoundError`.

- [ ] **Step 2: Check that plugin validation needs no login**

Run (Git Bash):
```bash
CLAUDE_CONFIG_DIR="$(mktemp -d)" claude plugin validate . --strict; echo "exit=$?"
```
Expected: success with `exit=0`. If it fails for lack of authentication, drop the three `claude plugin validate` lines from the workflow in Step 3, remove `claude plugin validate . --strict` from the test in Step 1, and add this test instead:
```python
    def test_plugin_manifests_parse_with_required_keys(self):
        plugin = json.loads(read(".claude-plugin", "plugin.json"))
        catalog = json.loads(read(".claude-plugin", "marketplace.json"))
        for k in ("name", "description", "version", "author", "license"):
            self.assertIn(k, plugin, k)
        self.assertEqual(catalog["name"], "executive-team-marketplace")
        self.assertTrue(all("name" in p and "source" in p and "version" in p for p in catalog["plugins"]))
```
Record which branch was taken; Task 6's `docs/testing.md` states it.

- [ ] **Step 3: Write `.github/workflows/ci.yml`**

```yaml
name: ci

on:
  pull_request:
    branches: [dev, main]
  push:
    branches: [main]

jobs:
  checks:
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: python -m unittest discover -s tests
      - run: python scripts/build_references.py --check
      - run: python scripts/bump_version.py --check
      - run: bash tests/hooks/test-session-start.sh
        shell: bash
      - if: runner.os == 'Linux'
        run: shellcheck --severity=warning hooks/session-start
      - if: runner.os == 'Linux'
        uses: actions/setup-node@v4
        with:
          node-version: "22"
      - if: runner.os == 'Linux'
        run: |
          npm install -g @anthropic-ai/claude-code
          claude plugin validate . --strict
          claude plugin validate agents --strict
          claude plugin validate skills --strict
```

- [ ] **Step 4: Run the suite**

Run: `python -m unittest discover -s tests 2>&1 | tail -3`
Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add .github/workflows/ci.yml tests/test_repo_hygiene.py
git commit -m "ci: static checks on pull requests to dev and main, Ubuntu and Windows

RAOOF A."
```

---

### Task 6: Documentation and contributor files

**Files:**
- Rewrite: `README.md`, `AGENTS.md`, `CLAUDE.md`, `CONTRIBUTING.md`, `.github/PULL_REQUEST_TEMPLATE.md`, `.github/ISSUE_TEMPLATE/bug_report.md`, `.github/ISSUE_TEMPLATE/feature_request.md`
- Create: `docs/testing.md`, `docs/windows-hooks.md`
- Modify: `docs/branch-protection.md`

**Interfaces:**
- Consumes: the commands and file names from Tasks 1 to 5. If Task 5 Step 2 took the fallback branch, `docs/testing.md` says validation runs locally before a release and is not in CI.

- [ ] **Step 1: Write `README.md`**

````markdown
# executive-team

<p align="center">
  <img src="assets/plugin.png" alt="The executive team around the table: COO, CTO, CISO, CFO, CMO and CSO, with the Chief of Staff at the whiteboard and the executive brief on the wall. The head seat is yours, the Owner." width="800">
</p>

A Claude Code plugin that gives you an AI executive team: a COO, CISO, CTO, CMO, CSO and CFO, plus a Chief of Staff who runs the meeting. You are the Owner. You bring a real business case, the Chief of Staff invites the right officers, they answer in parallel as candid executives, and you get one executive brief with positions, disagreements, risks, a recommended decision and next steps. Minutes are saved so the team remembers what was decided. This repository is the plugin and its own marketplace.

## How it works

At the start of every session the plugin introduces the team in a short bootstrap, so the model knows who is available and how to convene them. Every officer is built from a skills-by-position matrix: job title, required competencies, level per competency (1 Beginner, 2 Intermediate, 3 Expert), and associated tasks. The levels shape how each officer answers. Where the source matrix left fields blank, the plugin says so and lets you fill them for your own company through a git-ignored `org-profile.yaml`.

## Installation

In Claude Code:

```
/plugin marketplace add raoofaltaher/executive-team-marketplace
/plugin install executive-team@executive-team-marketplace
```

From a terminal:

```
claude plugin marketplace add raoofaltaher/executive-team-marketplace
claude plugin install executive-team@executive-team-marketplace
```

To try the development branch (uninstall `executive-team` first; both register the same agents and skills):

```
claude plugin install executive-team-dev@executive-team-marketplace
```

### Updating

```
/plugin marketplace update executive-team-marketplace
/plugin update executive-team
```

### Local development

Open this repository in Claude Code: `.claude/settings.json` registers it as a marketplace and enables the plugin (Claude Code asks you to trust the marketplace once). For a one-off session from another folder:

```
claude --plugin-dir <path-to-this-repository>
```

## The basic workflow

1. `/executive-team:gaps-report` to see what the source matrix left blank.
2. `/executive-team:setup` to fill departments, managers and your strategic objectives through multiple-choice questions.
3. `/executive-team:meet decide Should we move client onboarding to a self-serve portal next quarter?`

The bootstrap offers step 2 on its own the first time you call on the team in a git repository that has no `org-profile.yaml`. Set `EXECUTIVE_TEAM_NUDGE=off` to silence that line.

## What's inside

**Agents** (`agents/`)

| Agent | Position | Skills |
|---|---|---|
| `chief-of-staff` | Serves the Owner: routes, fans out, synthesizes, records. Takes no business position. | n/a |
| `chief-operating-officer` | Director of Operations and Customer Experience (COO) | 12 |
| `chief-information-security-officer` | Chief Information Security Officer (CISO) | 12 |
| `chief-technology-officer` | Technical Director / CTO | 11 |
| `chief-marketing-officer` | Communication, Marketing and Branding (CMO) | 10 |
| `chief-sales-officer` | Director of Sales (CSO) | 11 |
| `chief-financial-officer` | Director of Finance (CFO) | 9 |

**Commands** (`skills/meet`, `skills/setup`, `skills/gaps-report`)

| Command | What it does |
|---|---|
| `/executive-team:meet [mode] [officers: coo,cfo] <topic>` | Runs a meeting. Modes: `brainstorm`, `decide`, `review`, `plan`, `risk`. Detected from your wording when omitted, confirmed in the first line, asked only when unclear. `officers:` forces the invite list; `now decide` or `mode: risk` reruns the last topic in another mode. |
| `/executive-team:setup` | Interviews you and writes `org-profile.yaml`: departments, managers, missing levels, strategic objectives, extra skills. |
| `/executive-team:gaps-report` | Lists every gap in the source matrix and which ones your org-profile still leaves unfilled. |

**Skills loaded by the model** (`skills/`)

- `using-executive-team`: the one-screen bootstrap injected at session start, clear and compaction by `hooks/session-start`.
- `executive-team`: the protocol (level definitions, behaviour rules, officer answer format, meeting modes, brief and minutes formats, override rule) with `references/routing-index.md` and `references/gaps-register.md` (both generated) and `references/matrix-operations.md`.

## How a meeting works

1. The Chief of Staff reads the protocol, the routing index, your org-profile and the three most recent minutes, then settles the mode: explicit if you gave one, otherwise detected from your wording, otherwise it asks you. The first line of every reply confirms the mode and how to change it.
2. It invites every officer whose skills govern the decision at level 2 or 3, and tells you who and why. If nobody matches, it asks you instead of guessing. Re-run with `officers: coo,cto` to force the list.
3. It runs the invited officers in parallel. Each answers as its position, position first, at most 300 words, ending with a confidence level and any peer it wants consulted.
4. One consult round follows: officers named in a `Consult:` line who hold a relevant level 2 or 3 skill answer once.
5. It writes the executive brief: summary, positions, agreement, disagreement, risks, recommended decision, open questions, next steps with an owner officer.
6. It saves minutes to `<minutes_dir>/YYYY-MM-DD-<topic>.md` (default `docs/executive`) in the language you wrote in, and records your decision when you state it.

Officers are candid. They disagree with you and with each other when the facts warrant it, name risks plainly, and say `outside my competence` when a topic is not in their skills table. A level 3 skill answers with authority; level 2 answers independently and flags complex cases; level 1 gives the basics and points you to the officer who holds that skill at level 3.

Any officer can also be asked directly, outside a meeting, and can assess a role against its skills table (current, target, gap, areas for improvement) or propose training entries. Inputs for that come only from your conversation.

## Customizing for your company

`/executive-team:setup` interviews you with multiple-choice questions (defaults offered first, free text always possible) and writes `org-profile.yaml` in the project root (git-ignored). Keys:

```yaml
company: { name: "", owner_title: "Owner" }
positions:
  coo:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  # ciso, cto, cmo, cso, cfo: same shape
strategic_objectives:
  - { id: SO1, name: "SME customer growth", critical_skills: ["cso.2", "cmo.6", "coo.5"] }
meeting_defaults: { minutes_dir: docs/executive }   # the meeting mode is never a profile setting
```

A non-empty value in the profile overrides the matrix value; the matrix value stays visible in the agent file as the source. The CSO sheet in the source has no required levels, so the plugin ships defaults (sales-domain skills at 3, executive leadership and corporate vision at 2), marked `plugin default` in the agent file; override any of them in `positions.cso.level_overrides`.

## Source and traceability

The six officers were built from a skills-by-position matrix: one sheet per position with the job title, every required competency, its description and tasks, and the required level. Each skill in an agent file carries a source pointer (sheet, cell range, original French skill name) so any line can be traced to the matrix it came from. Fields the matrix left blank are marked `not specified in source` rather than filled in; defects in the matrix are reproduced and flagged rather than corrected. They are listed in `skills/executive-team/references/gaps-register.md`: empty department and manager fields, placeholder-only strategic objectives, no CSO levels (the plugin ships defaults), an empty tasks cell for the CFO's first skill, a duplicated description on the COO's fourth skill, a pasted sentence in the CMO's and CSO's "Corporate Vision and Strategy" descriptions, and columns some sheets lack (no description column on the CFO sheet, no tasks column on the COO, CISO and CTO sheets). Fill them for your company with `/executive-team:setup`.

## Privacy

The plugin holds positions, not people. No employee names, ratings, reviews or training records exist in this repository, and the agents are instructed never to store personal data. Assessments and training plans use only what you type in the conversation. `org-profile.yaml` and meeting minutes are git-ignored. Nothing in the plugin fetches from or reports to a remote host at runtime.

## When something goes wrong

Open an issue with the bug template: plugin and Claude Code versions, the exact command, what the Chief of Staff or officer did, and the relevant part of the brief or minutes with anything confidential removed. To see what the bootstrap injects, run `bash hooks/session-start` from the repository root; it prints the JSON Claude Code receives.

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md). Branch from `dev`, open pull requests against `dev`, fill in the template. `main` is the released branch and only the maintainer merges into it. This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).

## Development

```
python -m unittest discover -s tests          # test suites
python scripts/build_references.py --check    # fail if the generated references are stale
python scripts/bump_version.py --check        # every declared version location agrees
bash tests/hooks/test-session-start.sh        # the SessionStart hook
claude plugin validate . --strict             # manifests; also: agents, skills
```

`python scripts/build_references.py` regenerates the routing index and gaps register after an agent edit. See [docs/testing.md](docs/testing.md) for what each suite proves and [docs/windows-hooks.md](docs/windows-hooks.md) for how the hook runs on Windows.

## License

MIT. See [LICENSE](LICENSE).
````

- [ ] **Step 2: Write `AGENTS.md`**

````markdown
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

## Before a pull request

Run from the repository root; all must pass:

```
python -m unittest discover -s tests
python scripts/build_references.py --check
python scripts/bump_version.py --check
bash tests/hooks/test-session-start.sh
claude plugin validate . --strict
claude plugin validate agents --strict
claude plugin validate skills --strict
```

After editing any agent file, run `python scripts/build_references.py` and commit the regenerated references; the suite fails when they are stale. CI runs the same checks on Ubuntu and Windows.

## Understand the plugin before contributing

Read `README.md`, then `skills/executive-team/SKILL.md` (the protocol), then `agents/chief-of-staff.md`, then `skills/using-executive-team/SKILL.md` (what every session is told). Run one meeting with `/executive-team:meet decide <a topic>` and read the minutes it writes before proposing a change to how meetings work.
````

- [ ] **Step 3: Write `CLAUDE.md`**

```markdown
# executive-team: Contributor Guidelines

Read and follow [AGENTS.md](AGENTS.md) before doing anything in this repository.

Short version:

- Branch from `dev`, open pull requests against `dev`, never commit to `main`.
- Never edit sections 1 to 4 of an officer agent in `agents/`; they are the content of record. Fill gaps through `org-profile.yaml`.
- After any agent edit, run `python scripts/build_references.py` and commit the regenerated references.
- Before a PR, from the repository root: `python -m unittest discover -s tests`, `python scripts/build_references.py --check`, `python scripts/bump_version.py --check`, `bash tests/hooks/test-session-start.sh`, and `claude plugin validate . --strict` (also `agents`, `skills`).
- No personal data, no spreadsheet importers, no third-party integrations, no telemetry, no comments in code files.
```

- [ ] **Step 4: Write `CONTRIBUTING.md`**

````markdown
# Contributing

Thank you for helping improve the executive-team plugin.

## Branches

- `main` is the released branch. Every install from the marketplace reads it. Only the maintainer merges into it, and every merge is a release with a version bump and release notes.
- `dev` is the integration branch. All work lands here first. Pull requests must target `dev`; a PR opened against `main` will be asked to retarget.

## How to contribute

1. Fork the repository and switch to the `dev` branch.
2. Create a branch for your change, named for what it does (for example `fix/cso-invite-reason` or `feat/officer-answer-format`).
3. Make one change per branch. Bundled unrelated changes are closed without review.
4. Run the checks from the repository root before you open the PR:

   ```
   python -m unittest discover -s tests
   python scripts/build_references.py --check
   python scripts/bump_version.py --check
   bash tests/hooks/test-session-start.sh
   claude plugin validate . --strict
   claude plugin validate agents --strict
   claude plugin validate skills --strict
   ```

5. Open a pull request against `dev` and fill in every section of the template. A human must have reviewed the complete diff before submission.

## What is welcome

- Fixes to the meeting protocol, the Chief of Staff, the bootstrap or the user-invoked skills, with a transcript or minutes file that shows the problem and the fix.
- Clearer wording in agent or skill files, with evidence that agents follow the new wording better (run the scenario before and after).
- Fixes to the hook, the scripts or the tests, with the failing case added to the suite.
- Documentation fixes.

## What is not accepted

- Changes to sections 1 to 4 of any officer agent. Those sections reproduce the source skills matrix verbatim and are the plugin's content of record. Gaps and defects in them are filled through `org-profile.yaml`, never by editing the files.
- Anything that stores, requests, or reproduces personal data about employees.
- Third-party service integrations, telemetry, or network calls inside agents, skills, hooks or scripts.
- Behaviour-shaping wording changes without a before/after scenario.
- Project-specific or personal configuration submitted as plugin defaults.
- Comments in code files.

## Reporting problems

Open an issue with the template that fits. Include the plugin and Claude Code versions, what you asked, what the agent did, and the minutes file or transcript excerpt. Search open and closed issues first.

## Maintainer release flow

1. On `dev`: `python scripts/bump_version.py <x.y.z>`, then `python scripts/bump_version.py --audit` (must print `All clear`).
2. Add a section to `RELEASE-NOTES.md`.
3. Commit, open the `dev` to `main` pull request, wait for CI, merge with a merge commit.
4. Tag `v<x.y.z>` on `main`, push the tag, publish the GitHub release with the notes entry.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
````

- [ ] **Step 5: Write the pull request template**

`.github/PULL_REQUEST_TEMPLATE.md`:

```markdown
<!--
BEFORE SUBMITTING: read every section. PRs that leave sections blank,
bundle unrelated changes, or show no human review are closed without review.
-->

> **This PR must target the `dev` branch, not `main`.** `main` is the released
> branch; work lands on `dev` first. PRs opened against `main` will be asked to
> retarget before review.

## Who is submitting this PR? (required)

| Field | Value |
|-------|-------|
| Model + version that wrote the change (or "human") | |
| Harness + version (Claude Code, other) | |
| All plugins installed | |
| Human who reviewed the complete diff | |

## What problem does this solve?
<!-- What broke or what was missing, with the exact behaviour you saw:
     the command you ran, what the Chief of Staff or officer did, and a
     transcript excerpt or minutes file. "Improving X" is not a problem. -->

## What does this PR change?
<!-- One to three sentences. -->

## Is this change appropriate for this plugin?
<!-- Does it touch officer sections 1 to 4 (frozen)? Does it add personal
     or company data, an importer, an integration, telemetry? If yes to
     any, it does not belong here. -->

## What alternatives did you consider?
<!-- What else did you try or evaluate, and why was it worse? -->

## Evidence
<!-- For behaviour changes: the same scenario run before and after, with the
     difference described. For structural changes: the check output. -->

- [ ] `python -m unittest discover -s tests` passes
- [ ] `python scripts/build_references.py --check` passes
- [ ] `python scripts/bump_version.py --check` passes
- [ ] `bash tests/hooks/test-session-start.sh` passes
- [ ] `claude plugin validate . --strict`, `agents --strict`, `skills --strict` pass

## Related issues and PRs
<!-- #number, or "none found" after searching open and closed items -->

## Human review
- [ ] A human has reviewed the complete diff before submission
```

- [ ] **Step 6: Write the issue templates**

`.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug report
about: A meeting, officer, skill or the session bootstrap did not behave as documented
labels: bug
---

- [ ] I searched open and closed issues and this is not a duplicate

## Environment (required)

| Field | Value |
|-------|-------|
| executive-team version (`.claude-plugin/plugin.json`) | |
| Claude Code version (`claude --version`) | |
| Model | |
| Operating system | |
| Installed from (`main` / `dev` / local folder) | |
| Other plugins installed | |

## What did you run?
<!-- The exact command or message, e.g. `/executive-team:meet decide ...`, and whether org-profile.yaml exists -->

## What happened?
<!-- Quote the relevant part of the brief, the minutes file, or the transcript. Remove anything confidential. For bootstrap problems, paste the output of `bash hooks/session-start` run from the plugin folder. -->

## What did you expect?
<!-- Point to the rule in skills/executive-team/SKILL.md, agents/chief-of-staff.md or skills/using-executive-team/SKILL.md that was not followed, if you can. -->
```

`.github/ISSUE_TEMPLATE/feature_request.md`:

```markdown
---
name: Feature request
about: Propose a change to how the team works
labels: enhancement
---

- [ ] I searched open and closed issues and this is not a duplicate

## What problem would this solve?
<!-- The situation where the team let you down, with a concrete example. -->

## What do you propose?

## Which part does it touch?
<!-- The Chief of Staff, an officer's behaviour (section 5 or 6), a command, the protocol, the bootstrap, the hook, the tooling -->

## Does it need new matrix content?
<!-- Officer sections 1 to 4 are frozen. If the idea needs a new skill, level or task on an officer, say so; it will be discussed as an org-profile extension instead. -->
```

- [ ] **Step 7: Write `docs/testing.md`**

```markdown
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
| Plugin validation | `claude plugin validate . --strict`, `agents --strict`, `skills --strict` | Manifests, agent and skill frontmatter accepted by Claude Code. Runs without a login. |

`.github/workflows/ci.yml` runs all of these on every pull request to `dev` and `main` and on pushes to `main`, on Ubuntu and Windows (ShellCheck and plugin validation on Ubuntu only).

## Not gated

Meeting behaviour (routing, the consult round, the brief, minutes, language) is checked by hand: run a scenario with `/executive-team:meet` before and after a change and compare the minutes. Those runs are not in CI because they call a model.

## Seeing the bootstrap

`bash hooks/session-start` prints the JSON Claude Code receives. Pipe a hook payload to see the nudge logic: `printf '{"cwd": "/path/to/a/project"}' | CLAUDE_PLUGIN_ROOT=$PWD bash hooks/session-start`.
```

If Task 5 took the fallback branch, change the "Plugin validation" row's last sentence to "Run locally before a release; not in CI because the CLI needs a login on a runner." and the CI sentence accordingly.

- [ ] **Step 8: Write `docs/windows-hooks.md`**

```markdown
# How the SessionStart hook runs on Windows

Claude Code runs plugin hooks through a shell. On Windows that shell is Git Bash when the hook declares `"shell": "bash"`, but several details of the Windows launch path shaped the two files in `hooks/`. Code files in this repository carry no comments, so the reasoning lives here.

## Why `run-hook.cmd` is a polyglot file

`hooks/hooks.json` points at `run-hook.cmd`, not at the bash script. The file starts with `: << 'CMDBLOCK'`. To bash, `:` is a no-op and the heredoc swallows everything up to the line `CMDBLOCK`, so bash skips the cmd.exe section and runs the Unix tail, which re-executes the named script with bash. To cmd.exe, `:` begins a label, so the first line is ignored and the batch section runs; it finds `bash.exe` and runs the named script with it. One file therefore works whether Claude Code launches it through cmd.exe or through bash.

## Why hook scripts have no `.sh` extension

Claude Code on Windows prepends `bash` to any hook command whose text contains `.sh`. With the dispatcher's quoting that rewrite breaks the command line. Extensionless script names (`session-start`) avoid the rewrite entirely.

## How the dispatcher finds bash

In order: `C:\Program Files\Git\bin\bash.exe`, `C:\Program Files (x86)\Git\bin\bash.exe`, `%LOCALAPPDATA%\Programs\Git\bin\bash.exe` (only when `LOCALAPPDATA` is defined, otherwise the path would collapse to a location any user could create), then `bash` on PATH through `%SystemRoot%\System32\where.exe` with the `$PATH:` prefix so neither `where` nor `bash` can be picked up from the current directory. Matches without an extension and the WSL launchers under `System32`, `Sysnative` and `WindowsApps` are skipped: they fail when no Linux distribution is installed. If no bash is found the dispatcher exits 0 silently: the plugin keeps working, only the session bootstrap is missing. The bash call sits outside any parenthesised block because cmd.exe expands `%ERRORLEVEL%` inside a block when it parses the block, which would lose the hook's exit code.

## Why the scripts use bash builtins

Claude Code can spawn the startup hook with an empty or broken PATH. Both scripts therefore derive their directory by splitting `$0` instead of calling `dirname`, re-execute bash through `$BASH` (bash's own path, always set once bash runs) instead of a PATH lookup, read the skill file with `$(< file)` instead of `cat`, and parse the hook's stdin JSON with a small builtin reader. `cat` and `cygpath` are used only when `command -v` finds them.

## Why output goes through `cat`

On Git Bash, `printf` reports a closed stdout as `write error: Permission denied`, which `set -euo pipefail` would turn into a failing hook on every session. Piping the final JSON through `cat` absorbs that case. With an empty PATH the script falls back to bare `printf`.

## Why `printf`, not a heredoc

bash 5.3 can hang on a heredoc in this launch path, so the JSON is assembled in a variable and printed.

## Seeing the hook's output

From the repository root in Git Bash:

```
bash hooks/run-hook.cmd session-start
printf '{"cwd": "C:\\\\Users\\\\you\\\\project"}' | CLAUDE_PLUGIN_ROOT="$PWD" bash hooks/session-start
```

The first prints the flat shape (no `CLAUDE_PLUGIN_ROOT`), the second the nested shape Claude Code consumes, with the nudge if that project is a git repository without `org-profile.yaml`.
```

- [ ] **Step 9: Add the status-check note to `docs/branch-protection.md`**

Append before `## Default branch`:

```markdown
## Required status check

After the first green run of `.github/workflows/ci.yml` on a pull request, add the job `checks` as a required status check to both rulesets (Settings > Rules > Rulesets > edit > Require status checks to pass > add `checks`). The script does not do this because GitHub only offers a check name once it has run.
```

- [ ] **Step 10: Run every check and the audit**

Run:
```bash
python -m unittest discover -s tests 2>&1 | tail -3
python scripts/bump_version.py --audit
claude plugin validate . --strict
```
Expected: `OK`, `All clear: 0.1.1`, success. The audit reads README and CONTRIBUTING; neither may contain a version number.

- [ ] **Step 11: Commit**

```bash
git add -A
git commit -m "docs: single README, contributor files and hook docs on the superpowers pattern

RAOOF A."
```

---

### Task 7: Live check, release 0.2.0, pull request

**Files:**
- Modify: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (through the bump script), `RELEASE-NOTES.md`

**Interfaces:**
- Consumes: everything above.

- [ ] **Step 1: Live bootstrap check in a session**

Run from a temporary git repository without a profile (Git Bash):
```bash
tmp="$(mktemp -d)" && git -C "$tmp" init -q && cd "$tmp" && \
claude --plugin-dir /s/Org_Agents -p "Quote, verbatim, the first line and the last sentence of the EXTREMELY_IMPORTANT block in your context. Do nothing else." --max-turns 1
```
Expected: the answer quotes `You have an executive team.` and the nudge sentence ending `before the first meeting.` Then create `org-profile.yaml` in the same folder (`: > org-profile.yaml`), rerun, and expect the nudge gone. Return to the repository root afterwards. If the hook did not fire, run `claude --debug --plugin-dir /s/Org_Agents -p "hi" --max-turns 1 2>&1 | grep -i -A3 sessionstart` and fix the cause before continuing; do not mark this step done on an assumption.

- [ ] **Step 2: Bump the version**

Run:
```bash
python scripts/bump_version.py 0.2.0 && python scripts/bump_version.py --audit
```
Expected: two files updated, `All clear: 0.2.0`.

- [ ] **Step 3: Release notes**

Insert after the `# Release Notes` heading in `RELEASE-NOTES.md`:

```markdown
## v0.2.0 (2026-10-02)

The repository is rebuilt on the obra/superpowers shell. Content is unchanged: the seven agents, the protocol and the three commands are the same files as v0.1.1, moved.

### Layout

- The plugin now lives at the repository root; the repository is one plugin that is also its own marketplace. Install commands are unchanged. Existing installs move over with `/plugin marketplace update executive-team-marketplace` and `/plugin update executive-team`.
- `executive-team-dev` installs the whole repository from the `dev` branch.
- Tags are now `vX.Y.Z`.

### Session bootstrap

- A SessionStart hook injects the new one-screen `using-executive-team` skill at startup, after `/clear` and after compaction: who the team is, when to bring it in, how a meeting works, where the rules live.
- In a git repository with no `org-profile.yaml`, the bootstrap adds one line offering `/executive-team:setup` the first time the team is called on. `EXECUTIVE_TEAM_NUDGE=off` silences it.
- The hook is a polyglot dispatcher plus a builtins-only bash script, after ultrapowers' hardened versions, so it runs on Windows through Git Bash and survives a broken PATH at startup. `docs/windows-hooks.md` explains the mechanics.

### Tooling

- `.version-bump.json` declares every location that carries the version; `scripts/bump_version.py` writes them, `--check` detects drift, `--audit` finds the version string in undeclared files.
- New tests: `tests/test_hooks.py` and `tests/hooks/test-session-start.sh` (eleven cases, including empty PATH, Windows paths and an unreadable skill).
- Continuous integration on every pull request to `dev` and `main`, on Ubuntu and Windows: unit tests, references check, version check, hook test, ShellCheck, plugin validation.

### Documentation

- One README. AGENTS.md, CONTRIBUTING.md and the pull request and issue templates follow the superpowers pattern. New `docs/testing.md` and `docs/windows-hooks.md`.
```

If Task 1 Step 3 fell back to the `git-subdir` source for the dev entry, add under Layout: "- The dev entry uses a `git-subdir` source with path `.` because the validator rejected a branch ref on a `github` source."

- [ ] **Step 4: Final full run**

Run:
```bash
python -m unittest discover -s tests 2>&1 | tail -3
python scripts/build_references.py --check
python scripts/bump_version.py --audit
bash tests/hooks/test-session-start.sh | tail -3
shellcheck --severity=warning hooks/session-start
claude plugin validate . --strict && claude plugin validate agents --strict && claude plugin validate skills --strict
git diff --stat dev -- agents skills/executive-team skills/meet skills/setup skills/gaps-report scripts/build_references.py
```
Expected: all pass; the last command prints nothing (content unchanged apart from the move, which `git diff` with rename detection shows as no content change). Then: `git grep -n "plugins/executive-team" -- . ':!docs/superpowers'` prints only `RELEASE-NOTES.md` lines from older entries, if any. `git grep` reads tracked files only, so ignored local minutes under `docs/executive/` cannot produce false hits.

- [ ] **Step 5: Commit and push**

```bash
git add -A
git commit -m "release: v0.2.0

RAOOF A."
git push -u origin feat/superpowers-shell
```

- [ ] **Step 6: Open the pull request against dev**

```bash
gh pr create --base dev --head feat/superpowers-shell --title "Rebuild the repository shell on the superpowers pattern (v0.2.0)" --body-file - <<'EOF'
> Targets `dev`.

## Who is submitting this PR? (required)

| Field | Value |
|-------|-------|
| Model + version that wrote the change (or "human") | Claude Fable 5.1 (claude-fable-5-1) |
| Harness + version (Claude Code, other) | Claude Code 2.1.287 |
| All plugins installed | superpowers, plugin-dev, executive-team (local) |
| Human who reviewed the complete diff | @raoofaltaher |

## What problem does this solve?

The repository was a multi-plugin marketplace with the plugin in a subfolder, no session bootstrap, hand-maintained version fields, and no CI. The Owner asked for the engineering shell of obra/superpowers and raoofaltaher/ultrapowers around the unchanged executive-team content. Spec: `docs/superpowers/specs/2026-10-02-superpowers-shell-design.md`.

## What does this PR change?

Moves the plugin to the root (history preserved), adds the SessionStart bootstrap hook and the `using-executive-team` skill, declared-location version tooling, hook tests, a CI workflow, and the template's documentation and contributor files. Version 0.2.0.

## Is this change appropriate for this plugin?

Yes. No officer section 1 to 4 changed; no data, importer, integration or telemetry added.

## What alternatives did you consider?

Starting from an ultrapowers clone and deleting its content (rejected: 400 files to remove, same end state). Keeping the `plugins/` folder with root shims (rejected: every other harness expects the plugin at the root).

## Evidence

- [x] `python -m unittest discover -s tests` passes
- [x] `python scripts/build_references.py --check` passes
- [x] `python scripts/bump_version.py --check` passes
- [x] `bash tests/hooks/test-session-start.sh` passes
- [x] `claude plugin validate . --strict`, `agents --strict`, `skills --strict` pass
- Live check: a `claude -p` session in a fresh git repository quoted the bootstrap and the nudge; with `org-profile.yaml` present the nudge was gone.

## Related issues and PRs

none found

## Human review
- [x] A human has reviewed the complete diff before submission

RAOOF A.
EOF
```

Expected: a PR URL. CI starts on it; wait for both runners and fix anything red before reporting completion.

- [ ] **Step 7: Report**

State what was verified (test outputs, live check, CI status) and what remains for the Owner: merge to `dev`, then the `dev` to `main` release PR, the `v0.2.0` tag and GitHub release, and adding the `checks` job as a required status check once it has run.
