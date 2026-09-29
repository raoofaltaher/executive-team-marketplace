# Executive Team Plugin: Design Spec

Date: 2026-09-29
Source document: the source skills workbook (a local `.xlsx`, never committed) (workbook branded "Visées, Parcours de rehaussement des compétences")
Status: approved in brainstorming, awaiting written-spec review

## 1. Purpose

Convert the six "Skills table by position" sheets of the workbook into a team of Claude Code subagents that simulate a real executive team working for the Owner. The Owner chairs every discussion and makes every decision. The agents bring real-world cases to a candid, multi-officer deliberation and produce an executive brief.

The plugin is also a template. Wherever the workbook left a field blank, the plugin flags the gap and lets any company fill it through a configuration file, so the same agents fit other organizations.

## 2. Users and success criteria

**User:** the Owner of the organization, running Claude Code in this project or with the plugin installed elsewhere.

**Success looks like:**

1. Each officer file reproduces its sheet completely: job title, department, manager, sheet instructions, level reference, every skill with description, associated tasks, required level, and the strategic-objectives block. A reader can check any line against the workbook cell it came from.
2. `/org:meet <topic>` invites the right officers, runs them in parallel, and returns an executive brief with positions, disagreements, risks, a recommendation, and next steps. Minutes are saved.
3. `/org:setup` produces an org-profile that fills the gaps; `/org:gaps-report` shows what is still unfilled.
4. No employee names, ratings, or training rows exist anywhere in the plugin.

## 3. What the workbook contains (facts the design relies on)

Six position sheets share one template. Columns vary slightly:

| Sheet | Job title (source, French) | Skills | Required levels | Columns present |
|---|---|---|---|---|
| COO | Directeur des opérations et de l'expérience client (COO) | 12 | all filled | Skill name, Skill description, Level |
| CISO | Chef Information Security Officer (CISO) | 12 | all filled | Skill name, Skill description, Level |
| CTO | Directeur technique / CTO | 11 | all filled | Skill name, Skill description, Level |
| CMO | Communication Marketing & Branding (CMO) | 10 | all filled | Skill name, Skill description, Tâches associées, Level |
| CSO | Directeur des ventes (CSO) | 11 | none filled | Skill name, Skill description, Tâches associées, Level (empty) |
| CFO | Directeur des finances (CFO) | 9 | all filled | Skill name, Tâches associées, Level (no description column) |

Every sheet carries: `Department:` (empty), `Position manager:` (empty), an instructions paragraph, a level reference (1 Beginner, 2 Intermediate, 3 Expert, each with three definition lines), and a "Link with strategic objectives" block holding only the template's placeholder examples ("Ex: SME customer growth" paired with "Ex: Needs analysis, Communication", and four more pairs).

Known content defects in the source:

- CSO: no required level on any of the 11 skills.
- CFO skill 1 ("Gestion des stratégies financières"): no tasks.
- COO skill 4 ("Gestion de programme et de portefeuille"): description cell duplicates skill 3's client-relations text.
- Four competencies recur across sheets with role-specific wording: executive leadership, project management, continuous improvement, cross-team collaboration.

The remaining sheets (Skill Matrix, Skill Matrix (Icons), Training Log, Team Member Review, Team Dashboard, Instructions, hidden Calculations and Icon Gallery) hold ratings, training plans, and reviews for named individuals. They are excluded from the plugin. Only their column structures are reused (see section 5.4).

## 4. Decisions made in brainstorming

| Topic | Decision |
|---|---|
| Purpose | Executive team + standalone advisors + skill-matrix operators, all three |
| Chair | The Owner. No CEO agent. |
| Coordinator | A non-executive Chief of Staff agent routes, fans out, and synthesizes |
| Orchestration | Route, fan out in parallel, synthesize |
| People data | Positions only. No names, ratings, or training rows in any file |
| Strategic objectives | Reproduce placeholders verbatim, marked TEMPLATE; real ones come from org-profile |
| Language | English. Each skill keeps a source pointer with sheet, cells, and the original French skill name |
| Location | Project folder is the plugin root; usable in place and installable elsewhere |
| Source gaps | Reproduce as-is, flag each gap, list all gaps in a register |
| Runtime data for matrix ops | Conversation input only |
| Shared competencies | Inline in each officer, verbatim per sheet |
| Tools | Officers and Chief of Staff inherit all tools |
| Model | Inherit from session |
| Customization | org-profile.yaml + `/org:setup` interview |
| Sessions | One command `/org:meet` with modes: brainstorm, decide, review, plan, risk |
| Matrix ops | Agent capability on request, no dedicated commands |
| Memory | Decision log in `docs/executive/` |
| Pushback | Candid executives: take positions, disagree, flag risks, state limits |
| Levels | Drive confidence and scope of each officer's answers |
| Brief | Executive brief format |
| Storage approach | Inline agents + compact routing index |
| Naming | Full titles for agents; plugin `executive-team`; command namespace `org` |

## 5. Architecture

### 5.1 Layout

```
executive-team/                          (this repo root, S:\Org_Agents)
  .claude-plugin/
    plugin.json
    marketplace.json                     local marketplace so the folder installs itself
  .claude/settings.json                  enables the plugin when Claude Code opens this folder
  agents/
    chief-of-staff.md
    chief-operating-officer.md
    chief-information-security-officer.md
    chief-technology-officer.md
    chief-marketing-officer.md
    chief-sales-officer.md
    chief-financial-officer.md
  commands/
    meet.md
    setup.md
    gaps-report.md
  skills/executive-team/
    SKILL.md                             level definitions, meeting protocol, brief format, override rule
    routing-index.md                     officer x skill x level x keywords
    gaps-register.md                     every gap in the source, with sheet and cell
  templates/
    org-profile.yaml
  docs/
    executive/                           minutes (created on first meeting)
    superpowers/specs/                   this spec
  scripts/
    verify_agents.py                     checks agent files against the workbook
  README.md
```

### 5.2 Officer agent file

Frontmatter carries `name` and `description` only, so tools and model inherit from the session. The description names the position and lists its domains so Claude delegates correctly.

Body, in order:

1. **Position card.** Department, job title, position manager, sheet instructions. Empty source fields read `not specified in source` followed by the org-profile key that fills them. Manager defaults to `Owner`.
2. **Level reference.** The sheet's three levels and their definition lines, verbatim.
3. **Skills table by position.** One row per sheet row: number, skill, description, associated tasks, required level, source pointer, flags. Columns the sheet lacks read `column not present in source`. Flags mark the defects listed in section 3.
4. **Link with strategic objectives.** Status `TEMPLATE`. The placeholder pairs verbatim. A note that real objectives come from `org-profile.strategic_objectives` and are mapped to skills at read time.
5. **How this officer operates.** Persona, level behaviour, peer consultation, matrix operations, startup reads, output rules (detailed in 5.4).

Source pointer format: `COO!B8:D8 · FR: Gestion des opérations (Operational Management)`.

### 5.3 Chief of Staff agent

A non-executive agent that serves the Owner and never takes a business position. On `/org:meet` it:

1. Reads `org-profile.yaml` if present, `routing-index.md`, and the three most recent files in `docs/executive/`.
2. Selects officers whose skills match the topic at level 2 or 3. Level 1 holders are named but not invited unless nobody else covers the domain. It states who it invited and why; the Owner can override before it proceeds.
3. Determines the mode from the command argument, else from the Owner's wording. Modes and what they ask each officer:
   - `brainstorm`: three options from your domain, each with a one-line risk.
   - `decide`: yes, no, or yes-with-conditions, plus the single strongest reason.
   - `review`: strengths, weaknesses, what you would change.
   - `plan`: milestones, dependencies on other officers, resource needs.
   - `risk`: top three risks in your domain, likelihood, impact, mitigation.
4. Runs the selected officers in parallel as subagents. Each receives the topic, the mode, the relevant minutes, and the org-profile.
5. Writes the executive brief (5.5) to chat.
6. Writes minutes to `docs/executive/YYYY-MM-DD-<slug>.md`: brief, each officer's full response, and a `Decision` section the Owner fills or the Chief of Staff appends when the Owner states a decision in chat.

### 5.4 Officer behaviour rules (shared skill)

- **Candid.** Take a position first, reasoning second. Disagree with the Owner and with peers when warranted. Name risks plainly. Say `outside my competence` when the topic falls outside the skills table.
- **Levels.** Level 3: answer with authority, coach, and supervise. Level 2: answer independently, flag complex cases. Level 1: state the basics and recommend the officer who holds the skill at level 3 (found in the routing index).
- **Peers.** Recommend consulting a named officer. Never speak for another officer.
- **Matrix operations on request.** Assess a person or the role against the skills table using the Team Member Review columns (skill, current, target, gap, areas for improvement, notes). Propose training entries using the Training Log columns (training description, related skill, priority Critical/High/Medium/Low, starting level, completed level, start, finish, status Scheduled/In Progress/Completed/Cancelled/On Hold). All inputs come from the conversation. Write nothing personal to disk unless the Owner asks for a specific file.
- **Override rule.** A value in `org-profile.yaml` wins over the sheet value. The sheet value remains visible in the file as source.
- **Startup.** Read org-profile if present. When invoked by the Chief of Staff, use the minutes it passes rather than reading the folder.

### 5.5 Executive brief format

```
# Executive brief: <topic>            mode: <mode>   date: <date>
Invited: <officers and why>
## Summary                             3-5 lines
## Positions                           per officer, 2-4 lines each
## Agreement
## Disagreement                        who, on what, why
## Risks
## Recommended decision                one, with conditions
## Open questions
## Next steps                          action, owner officer, when
```

### 5.6 Customization layer

`templates/org-profile.yaml` is copied to the project root by `/org:setup`:

```yaml
company:
  name: ""
  owner_title: "Owner"
positions:
  coo:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  ciso: { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  cto:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  cmo:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  cso:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  cfo:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
strategic_objectives: []       # items: { id, name, critical_skills: ["coo.3", "cfo.5"] }
meeting_defaults:
  mode: brainstorm
  minutes_dir: docs/executive
```

`level_overrides` maps a skill number to 1, 2, or 3. `extra_skills` items use the sheet columns: skill, description, tasks, level.

`/org:setup` interviews the Owner one topic at a time (company, departments, managers, CSO levels, objectives, extra skills) and writes or updates the file. It never asks for information about individual employees.

`gaps-register.md` is written at build time and lists every `not specified in source`, `column not present in source`, `TEMPLATE`, and defect flag with sheet and cell. `/org:gaps-report` reads the register and the org-profile and prints what remains unfilled.

### 5.7 Routing index

`routing-index.md` holds one row per officer skill: officer, skill number, English skill name, required level, five to eight keywords. The Chief of Staff reads only this file to route. The verification script regenerates it from the agent files so it cannot drift.

## 6. Packaging and local use

Verified against the Claude Code docs (plugins/components, plugins/install, plugins/create, sub-agents) on 2026-09-29.

- `.claude-plugin/plugin.json`: name `executive-team`, version `0.1.0`, description, author.
- `.claude-plugin/marketplace.json`: a marketplace with one plugin entry whose `source` is `./`, so `claude plugin marketplace add <path>` works for this folder and for a git clone. The docs do not fix the file's exact content, so the plan copies the shape used by the official marketplace and tests it.
- `.claude/settings.json`: `extraKnownMarketplaces` lists this folder as `./` (a relative path must start with `./` or `../`; a bare `name/name` is read as a GitHub repository), and `enabledPlugins` sets `"executive-team": true`. Opening the folder in Claude Code then loads the agents and commands without a separate install. For a one-off session elsewhere, `claude --plugin-dir <path>` loads the plugin from disk.
- Command files are `commands/meet.md`, `commands/setup.md`, `commands/gaps-report.md`. Claude Code namespaces plugin commands as `/<plugin>:<command>`, and a subfolder adds a segment (`commands/org/meet.md` becomes `/executive-team:org:meet`). The only way to get `/org:meet` is to name the plugin `org`. Decision: the plugin stays `executive-team` and commands are `/executive-team:meet`, `/executive-team:setup`, `/executive-team:gaps-report`. Elsewhere in this spec `/org:meet` is shorthand for `/executive-team:meet`.
- Agent frontmatter: `name` and `description` are required. Omitting `tools` inherits all tools; omitting `model` follows the session model. Plugin agents ignore `permissionMode`, `hooks`, `mcpServers`, and `initialPrompt`, none of which this design uses.
- Skills: `skills/executive-team/SKILL.md` with supporting files `routing-index.md` and `gaps-register.md` in the same folder, which the SKILL.md tells agents to read.

### 6.1 Repository and future publication

The project becomes a git repository intended for GitHub. The goal is a public plugin, first for Claude Code and later for other coding agents and AI tools. Consequences for this build:

- Initialize git in the project root. `.gitignore` excludes `.remember/`, `*.xlsx` (the source workbook), `org-profile.yaml` (company-specific), `docs/executive/` minutes, and `.claude/settings.local.json`.
- The tracked tree contains no company facts, no employee data, and no workbook. Everything company-specific enters through the ignored org-profile.
- README.md documents installation from GitHub (`claude plugin marketplace add <owner>/<repo>`), local use, the three commands, the seven agents, and how to fill gaps.
- A permissive open-source `LICENSE` file (MIT) is included so the plugin can be published; the Owner can change it before publishing.
- Portability to other agents is out of scope for this build, but the content layout keeps agent bodies as plain markdown so they can be reused elsewhere.

## 7. Error handling

- Missing org-profile: agents run on sheet values and say so once per session.
- Malformed org-profile: the reading agent reports the line and continues with sheet values.
- Topic matches no officer at level 2 or 3: the Chief of Staff says so and asks the Owner whether to invite level 1 holders or all officers.
- An officer subagent fails: the brief lists the officer as `no response` and continues.
- `docs/executive/` missing: created on first write.

## 8. Verification

1. `scripts/verify_agents.py` opens the workbook with openpyxl and checks, per officer file: every sheet row present in order, required level equal to the sheet value, source pointer cells valid, no sheet row missing, gap flags present where section 3 lists defects. It regenerates `routing-index.md` and `gaps-register.md` and fails if the committed copies differ.
2. Frontmatter check for all seven agents and three commands (valid YAML, required keys).
3. Smoke meeting: `/org:meet` on a sample topic must invite the expected officers, print the brief in the 5.5 format, and write a minutes file.
4. `/org:gaps-report` on an empty profile lists exactly: 6 departments, 6 managers, 6 objective blocks, 11 CSO levels, CFO skill 1 tasks, COO skill 4 duplicated description, CFO missing description column.
5. A grep across the plugin for the individual names present in the workbook returns nothing.

## 9. Out of scope

Reading the workbook at runtime; storing employee ratings or training rows; a CEO agent; hooks; MCP servers; per-officer tool allowlists; translation back to French.
