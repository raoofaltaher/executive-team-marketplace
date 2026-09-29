---
description: Interview the Owner and write org-profile.yaml (departments, managers, missing levels, strategic objectives, extra skills). Safe to re-run; updates in place.
---
Create or update `org-profile.yaml` in the project root for the executive-team plugin.

1. If `org-profile.yaml` exists, read it and say which fields are already filled. Otherwise copy `templates/org-profile.yaml` (from this plugin's directory) as the starting point.
2. Read `skills/executive-team/gaps-register.md` to know what the workbook left blank.
3. Ask one topic at a time, using AskUserQuestion when options exist, and accept "skip" for any item:
   a. Company name and the Owner's title (default "Owner").
   b. For each position (COO, CISO, CTO, CMO, CSO, CFO): department name; manager (default Owner).
   c. CSO required levels for its 11 skills (the source has none): offer "all 3", "all 2", or per-skill entry.
   d. Any other level overrides the Owner wants.
   e. Strategic objectives: for each, an id, a name, and the critical skills as `<code>.<n>` references; show the skill numbers from the routing index when asked.
   f. Extra skills per position (skill, description, tasks, level), if any.
   g. Meeting defaults: default mode and minutes directory.
4. Validate: every level is 1, 2, or 3; every critical-skill reference matches an existing officer skill number in `skills/executive-team/routing-index.md`; position codes are among the six. Report each invalid entry and ask again or drop it.
5. Write `org-profile.yaml` with the YAML comments preserved from the template. Show a summary table of what is set and what still reads "use workbook value".
6. Remind the Owner that `org-profile.yaml` is git-ignored and never leaves the machine unless they share it.

Never ask for or record information about individual employees (names, ratings, training history).
