---
name: setup
description: This skill should be used when the user asks to "set up the executive team", "configure org-profile", "onboard the plugin", "fill the gaps", "add our strategic objectives", "customize the officers for my company", or invokes /executive-team:setup. Interviews the Owner with multiple-choice questions and writes org-profile.yaml.
allowed-tools: Read, Write, Glob, AskUserQuestion
disable-model-invocation: true
---
Create or update `org-profile.yaml` in the current project root for the executive-team plugin.

## Files
- Template: `org-profile.template.yaml` in this skill's own folder (next to this SKILL.md). Read it from the skill base directory; `${CLAUDE_PLUGIN_ROOT}/skills/setup/org-profile.template.yaml` is the same file when that variable is set.
- Gaps register: `../executive-team/references/gaps-register.md` relative to this skill's folder (`${CLAUDE_PLUGIN_ROOT}/skills/executive-team/references/gaps-register.md`).
- Routing index: `../executive-team/references/routing-index.md` (skill numbers per officer).
- Output: `org-profile.yaml` in the current project root (the folder the session runs in, not the plugin folder).

If a file cannot be found by either path, say which one and continue from the documented shapes in this file; do not stop the interview.

## How to ask
Use the harness's interactive multiple-choice tool for every question (AskUserQuestion in Claude Code; the equivalent prompt in Claude Desktop and claude.ai). Offer the sensible default as the first option marked "(Recommended)", two or three alternatives, and rely on the built-in "Other" for free text. Fall back to a plain text question only when the harness has no such tool. Group up to four related questions in one prompt. Accept "skip" or "keep" on any item, which keeps the matrix value. Never ask for or record information about individual employees (names, ratings, training history).

## The interview
1. **Existing profile.** If `org-profile.yaml` exists, read it and report in one short table which fields are already set. Otherwise start from the template.
2. **Company and Owner.** Options for the Owner's title: `Owner` (Recommended), `Founder`, `CEO`, `Founder / Owner`. Company name: `Leave blank` (Recommended) or Other.
3. **Departments.** One question: `Standard names` (Recommended: Operations, Information Security, Technology, Marketing, Sales, Finance), `I will name them` (then one question per position), `Keep blank`.
4. **Managers.** One question: `All six report to the Owner` (Recommended), `Some report elsewhere` (then ask which), `Keep blank`.
5. **Level overrides.** Explain in one line that every officer already has required levels, and that the CSO's are plugin defaults (sales-domain skills 3, executive leadership and corporate vision 2) because the source matrix left them empty. Ask: `Keep all levels as shipped` (Recommended), `Override some levels` (then ask officer, skill number, level; show the routing index when asked).
6. **Strategic objectives.** Ask: `None for now` (Recommended for a first setup), `Add objectives`. For each objective ask for an id, a name, and the critical skills as `<code>.<n>` references; offer to suggest references from a plain-words description and confirm them with a multiple-choice question.
7. **Extra skills.** Ask: `None` (Recommended), `Add a skill to a position` (skill, description, tasks, level 1-3).
8. **Minutes folder.** Ask: `docs/executive` (Recommended) or Other. Do not ask for a default meeting mode; the mode is settled per meeting from the request.
9. **Validate.** Every level is 1, 2, or 3; every critical-skill reference matches an officer skill number in the routing index; position codes are among coo, ciso, cto, cmo, cso, cfo. Report each invalid entry with a multiple-choice question to fix or drop it.
10. **Write.** Write `org-profile.yaml` with the template's YAML comments on every write, so an updated file keeps its documentation. Show a summary table of what is set and what still reads "use matrix value".
11. **Git.** If the project has a `.gitignore` without `/org-profile.yaml`, say so and offer to add the line.

## Profile shape (for the fallback when the template cannot be read)
```yaml
company: { name: "", owner_title: "Owner" }
positions:
  coo:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  ciso: { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  cto:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  cmo:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  cso:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  cfo:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
strategic_objectives: []      # items: { id, name, critical_skills: ["cso.2", "cmo.6"] }
meeting_defaults: { minutes_dir: docs/executive }
```
