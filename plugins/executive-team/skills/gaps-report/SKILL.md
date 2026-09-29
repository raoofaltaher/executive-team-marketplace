---
name: gaps-report
description: This skill should be used when the user asks "what is still missing", "show the gaps", "what did the matrix leave blank", "which fields are unfilled in org-profile", or invokes /executive-team:gaps-report. Reports every gap in the source skills matrix and which ones org-profile.yaml still leaves open.
allowed-tools: Read, Glob
---
Produce the gaps report for the executive-team plugin. Modify no file.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`.

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/executive-team/references/gaps-register.md` (generated from the agent files).
2. Read `org-profile.yaml` in the current project root if it exists.
3. Mark each register row `filled` when the matching org-profile key holds a non-empty value: department, manager, `level_overrides.<n>`, or, for an officer's strategic-objectives row, at least one objective whose `critical_skills` references that officer. Otherwise mark it `open`. Mark rows whose fix mentions "edit the matrix" as `open (source defect)` regardless of the profile.
4. Print a table: Officer | Item | Location | Status | Fill with. Then print the totals: filled, open, source defects.
5. End with the single command that fixes most open rows: `/executive-team:setup`.
