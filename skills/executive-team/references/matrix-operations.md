# Matrix operations

Column formats an officer uses when the Owner asks for an assessment or a training plan. They mirror the review and training-log structures of the source workbook. Every value comes from the conversation; nothing about a person is written to disk unless the Owner names the file.

## Assessment (Team Member Review columns)

| # | Skill | Current | Target | Gap | Areas for improvement | Notes |
|---|---|---|---|---|---|---|

- `Current` and `Target` are 1, 2, or 3 (or `x` for exempt). `Gap` = Target minus Current, never negative.
- Default `Target` is the required level from the officer's skills table (after org-profile overrides).
- Close with `Current top 5 skills`, `Future top 5 skills` (largest gaps first), and `Growth opportunities`.

## Training plan (Training Log columns)

| ID | Training description | Related skill | Priority | Starting skill level | Completed skill level | Training start | Training finish | Status |
|---|---|---|---|---|---|---|---|---|

- `Priority`: Critical, High, Medium, Low.
- `Status`: Scheduled, In Progress, Completed, Cancelled, On Hold.
- `Related skill` is a skill name from the officer's table, with its number.
- Propose one entry per gap of 1 or more, largest gap first, and ask the Owner for dates rather than inventing them.
