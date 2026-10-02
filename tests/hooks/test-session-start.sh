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

run_hook_in() {
    local run_dir="$1" stdin_json="$2"
    shift 2
    (cd "$run_dir" && printf '%s' "$stdin_json" | env -i PATH="$PATH" HOME="$WORK" "$@" "$BASH" "$HOOK" 2>&1)
}

json_escape() {
    printf '%s' "$1" | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
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
NO_NUDGE_DIR="$WORK/repo-profile"
NUDGE_DIR="$WORK/repo-noprofile"

echo "SessionStart hook"

out="$(run_hook_in "$NO_NUDGE_DIR" '{}' CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
expect "1 nested shape under CLAUDE_PLUGIN_ROOT with the bootstrap body" nested "## Who is in the room" "" "$out"
expect "1b nested shape announces the team" nested "You have an executive team" "" "$out"

out="$(run_hook_in "$NO_NUDGE_DIR" '{}')"
expect "2 flat shape without CLAUDE_PLUGIN_ROOT" flat "## Who is in the room" "" "$out"

out="$(run_hook_in "$NO_NUDGE_DIR" "{\"cwd\": \"$(json_escape "$WORK/repo-noprofile")\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
expect "3 nudge in a git repo without org-profile.yaml" nested "$NUDGE" "" "$out"

out="$(run_hook_in "$NUDGE_DIR" "{\"cwd\": \"$(json_escape "$WORK/repo-profile/sub")\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
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
    out="$(run_hook_in "$NUDGE_DIR" "{\"cwd\": \"$(json_escape "$WORK/plain")\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
    expect "5 no nudge outside a git repo" nested "## Who is in the room" "$NUDGE" "$out"
fi

out="$(run_hook_in "$NUDGE_DIR" "{\"cwd\": \"$(json_escape "$WORK/repo-noprofile")\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" EXECUTIVE_TEAM_NUDGE=off)"
expect "6 EXECUTIVE_TEAM_NUDGE=off silences the nudge" nested "## Who is in the room" "$NUDGE" "$out"

out="$(run_hook_in "$NO_NUDGE_DIR" '' CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
expect "7 empty stdin still yields valid JSON" nested "## Who is in the room" "" "$out"

out="$(cd "$NO_NUDGE_DIR" && printf '%s' "{\"cwd\": \"$(json_escape "$WORK/repo-noprofile")\"}" | env -i PATH= HOME="$WORK" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" "$BASH" "$HOOK" 2>&1)"
expect "8 empty PATH still yields the nudge and valid JSON" nested "$NUDGE" "" "$out"

direct="$(run_hook_in "$NO_NUDGE_DIR" "{\"cwd\": \"$(json_escape "$WORK/repo-noprofile")\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
via_wrapper="$(cd "$NO_NUDGE_DIR" && printf '%s' "{\"cwd\": \"$(json_escape "$WORK/repo-noprofile")\"}" | env -i PATH="$PATH" HOME="$WORK" CLAUDE_PLUGIN_ROOT="$REPO_ROOT" "$BASH" "$WRAPPER" session-start 2>&1)"
if [ "$direct" = "$via_wrapper" ] && [[ "$via_wrapper" == *"$NUDGE"* ]]; then
    pass "9 run-hook.cmd dispatches to session-start with identical output"
else
    fail "9 run-hook.cmd dispatches to session-start with identical output"
    printf '%s\n' "$via_wrapper" | head -3
fi

if command -v cygpath >/dev/null 2>&1; then
    win="$(cygpath -w "$WORK/repo-noprofile")"
    out="$(run_hook_in "$NO_NUDGE_DIR" "{\"cwd\": \"$(json_escape "$win")\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
    expect "10 Windows-style cwd is resolved" nested "$NUDGE" "" "$out"
    spaced="$WORK/My Project été"
    mkdir -p "$spaced/.git"
    out="$(run_hook_in "$NO_NUDGE_DIR" "{\"cwd\": \"$(json_escape "$(cygpath -w "$spaced")")\"}" CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
    expect "10b Windows-style cwd with a space and accents is resolved" nested "$NUDGE" "" "$out"
else
    skip "10 Windows-style cwd (cygpath not available)"
fi

broken="$WORK/broken-plugin"
mkdir -p "$broken/hooks" "$broken/skills"
cp "$HOOK" "$broken/hooks/session-start"
out="$(cd "$NO_NUDGE_DIR" && printf '%s' '{}' | env -i PATH="$PATH" HOME="$WORK" CLAUDE_PLUGIN_ROOT="$broken" "$BASH" "$broken/hooks/session-start" 2>&1)"
expect "11 unreadable bootstrap skill still yields valid JSON" nested "Error reading using-executive-team skill" "" "$out"

out="$(run_hook_in "$NUDGE_DIR" '{"cwd": "C:\Bad\Escape"}' CLAUDE_PLUGIN_ROOT="$REPO_ROOT")"
expect "12 an unparseable cwd falls back to the working directory" nested "$NUDGE" "" "$out"

echo
if [ "$FAILURES" -eq 0 ]; then
    echo "All hook tests passed"
else
    echo "$FAILURES hook test(s) failed"
fi
exit "$FAILURES"
