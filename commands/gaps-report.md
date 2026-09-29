---
description: Show every gap in the source skills matrix and which ones org-profile.yaml still leaves unfilled.
---
Produce the gaps report for the executive-team plugin.

Plugin root: `${CLAUDE_PLUGIN_ROOT}`.

1. Read `${CLAUDE_PLUGIN_ROOT}/skills/executive-team/gaps-register.md` (generated from the agent files).
2. Read `org-profile.yaml` in the project root if it exists.
3. For each register row, mark it `filled` when the corresponding org-profile key holds a non-empty value: department, manager, `level_overrides.<n>`, or, for the strategic-objectives row of an officer, at least one objective whose `critical_skills` references that officer. Otherwise `open`. Rows whose fix mentions "edit the workbook" are always `open (source defect)`.
4. Print a table: Officer | Item | Location | Status | Fill with. Then totals: filled, open, source defects.
5. End with the single command that fixes most open rows: `/executive-team:setup`.

Do not modify any file.
