---
name: setup
description: This skill should be used when the user asks to "set up the executive team", "configure org-profile", "fill the gaps", "set the CSO levels", "add our strategic objectives", "customize the officers for my company", or invokes /executive-team:setup. Interviews the Owner and writes org-profile.yaml.
allowed-tools: Read, Write, Glob, AskUserQuestion
disable-model-invocation: true
---
Create or update `org-profile.yaml` in the current project root for the executive-team plugin.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`. Plugin files below are relative to it; `org-profile.yaml` lives in the current project root.

1. If `org-profile.yaml` exists, read it and report which fields are already filled. Otherwise start from `${CLAUDE_PLUGIN_ROOT}/templates/org-profile.yaml`.
2. Read `${CLAUDE_PLUGIN_ROOT}/skills/executive-team/references/gaps-register.md` to know what the matrix left blank.
3. Ask one topic at a time, use AskUserQuestion when options exist, and accept "skip" for any item:
   a. Company name and the Owner's title (default "Owner").
   b. For each position (COO, CISO, CTO, CMO, CSO, CFO): department name; manager (default Owner).
   c. CSO required levels for its 11 skills (the source has none): offer "all 3", "all 2", or per-skill entry.
   d. Any other level overrides.
   e. Strategic objectives: for each, an id, a name, and the critical skills as `<code>.<n>` references; show skill numbers from `${CLAUDE_PLUGIN_ROOT}/skills/executive-team/references/routing-index.md` when asked.
   f. Extra skills per position (skill, description, tasks, level), if any.
   g. Minutes directory (default `docs/executive`). Do not ask for a default meeting mode; the mode is settled per meeting from the request.
4. Validate: every level is 1, 2, or 3; every critical-skill reference matches an officer skill number in the routing index; position codes are among the six. Report each invalid entry and ask again or drop it.
5. Write `org-profile.yaml`. Take the YAML comments from the template on every write, so an updated file keeps the documentation even when the existing file lacked it. Show a summary table of what is set and what still reads "use matrix value".
6. Confirm that `.gitignore` in the project lists `/org-profile.yaml`; if the project has a `.gitignore` without it, say so and offer to add the line.

Never ask for or record information about individual employees (names, ratings, training history).
