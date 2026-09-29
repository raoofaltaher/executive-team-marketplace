# Release Notes

## v0.1.0 (2026-09-29)

First release of the `executive-team` plugin and this marketplace.

### executive-team

- Six officer agents built from a skills-by-position matrix: COO (12 skills), CISO (12), CTO (11), CMO (10), CSO (11), CFO (9). Every skill carries its description, associated tasks, required level, and a source pointer. Fields the matrix left blank are marked `not specified in source`; defects are reproduced and flagged in a generated gaps register.
- A Chief of Staff agent that routes a topic to the officers whose skills govern it, runs them in parallel, runs one consult round, writes an executive brief (summary, positions, agreement, disagreement, risks, recommended decision, open questions, next steps) and saves minutes.
- User-invoked skills: `/executive-team:meet [mode] [officers: ...] <topic>` with modes brainstorm, decide, review, plan, risk; `/executive-team:setup` to write a git-ignored `org-profile.yaml`; `/executive-team:gaps-report`.
- Required skill levels shape each officer's confidence and scope; the CSO, which has no levels in the source, answers at level 1 until the profile sets them.
- Officers answer in the Owner's language; briefs keep English headings and literal tokens.
- Privacy: positions only, no employee data, assessments and training plans use conversation input only.

### Marketplace

- Catalog with `executive-team` (from `main`) and `executive-team-dev` (from the `dev` branch).
- Contribution flow with `main` and `dev` branches, PR and issue templates, contributor guidelines for people and AI agents, Contributor Covenant.
