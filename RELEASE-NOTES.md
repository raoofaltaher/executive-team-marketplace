# Release Notes

## v0.1.1 (2026-09-30)

### executive-team

- The CSO now ships default required levels (sales-domain skills 3; executive leadership and corporate vision 2, matching the identical CMO skills). The source matrix has none, so each is marked `plugin default` in the agent file and in the gaps register; override any of them in `org-profile.positions.cso.level_overrides`. Setup no longer asks for them, and the CSO is now invited to meetings on its own merits.
- `/executive-team:setup` runs as an interactive multiple-choice interview: defaults are offered first, free text stays available through "Other", related questions are grouped. It no longer asks for a default meeting mode.
- The org-profile template moved into the setup skill's folder, so every harness can read it; the skill also resolves the gaps register and routing index relative to its own folder when the plugin-root variable is not substituted.
- The meeting mode is settled per meeting: explicit, detected from the request, or asked with a recommendation when unclear; confirmed in the first line of every reply; "now decide" or "mode: risk" reruns the last topic in another mode.

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
