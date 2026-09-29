---
description: Show every gap in the source skills matrix and which ones org-profile.yaml still leaves unfilled.
---
Produce the gaps report for the executive-team plugin.

1. Read `skills/executive-team/gaps-register.md` (generated from the agent files).
2. Read `org-profile.yaml` in the project root if it exists.
3. For each register row, mark it `filled` when the corresponding org-profile key holds a non-empty value (department, manager, `level_overrides.<n>`, `strategic_objectives` non-empty), else `open`. Rows whose fix is "edit the workbook" are always `open (source defect)`.
4. Print a table: Officer | Item | Location | Status | Fill with. Then totals: filled, open, source defects.
5. End with the single command that fixes most open rows: `/executive-team:setup`.

Do not modify any file.
