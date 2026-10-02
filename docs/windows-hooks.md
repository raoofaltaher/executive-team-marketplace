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

The first prints the flat shape (no `CLAUDE_PLUGIN_ROOT`), the second the nested shape Claude Code consumes, with the nudge if that project is a git repository without `org-profile.yaml`. From cmd.exe, `hooks\run-hook.cmd session-start` exercises the batch half.
