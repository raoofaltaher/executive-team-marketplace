# executive-team

A Claude Code plugin that gives you an AI executive team: a COO, CISO, CTO, CMO, CSO and CFO, plus a Chief of Staff who runs the meeting. You are the Owner. You bring a real business case, the Chief of Staff invites the right officers, they answer in parallel as candid executives, and you get one executive brief with positions, disagreements, risks, a recommended decision and next steps. Minutes are saved so the team remembers what was decided.

Every officer is built from a skills-by-position matrix: job title, required competencies, level per competency (1 Beginner, 2 Intermediate, 3 Expert), and associated tasks. The levels shape how each officer answers. Where the source matrix left fields blank, the plugin says so and lets you fill them for your own company.

## What you get

**Agents** (`agents/`)

| Agent | Position | Skills |
|---|---|---|
| `chief-of-staff` | Serves the Owner: routes, fans out, synthesizes, records. Takes no business position. | n/a |
| `chief-operating-officer` | Director of Operations and Customer Experience (COO) | 12 |
| `chief-information-security-officer` | Chief Information Security Officer (CISO) | 12 |
| `chief-technology-officer` | Technical Director / CTO | 11 |
| `chief-marketing-officer` | Communication, Marketing and Branding (CMO) | 10 |
| `chief-sales-officer` | Director of Sales (CSO) | 11 |
| `chief-financial-officer` | Director of Finance (CFO) | 9 |

**Commands** (`commands/`)

| Command | What it does |
|---|---|
| `/executive-team:meet [mode] [officers: coo,cfo] <topic>` | Runs a meeting. Modes: `brainstorm`, `decide`, `review`, `plan`, `risk`; detected from your wording if omitted. `officers:` forces the invite list. |
| `/executive-team:setup` | Interviews you and writes `org-profile.yaml`: departments, managers, missing levels, strategic objectives, extra skills. |
| `/executive-team:gaps-report` | Lists every gap in the source matrix and which ones your org-profile still leaves unfilled. |

**Skill** (`skills/executive-team/`): the shared protocol (level definitions, behaviour rules, meeting modes, brief format, override rule), the generated `routing-index.md` (officer x skill x level x keywords) and the generated `gaps-register.md`.

## Install

From GitHub, once published:

```
claude plugin marketplace add <owner>/<repo>
claude plugin install executive-team@executive-team
```

Locally: open this folder in Claude Code. `.claude/settings.json` registers the folder as a marketplace and enables the plugin; Claude Code asks you to trust the marketplace the first time. For a one-off session from another folder:

```
claude --plugin-dir <path-to-this-folder>
```

## First run

1. `/executive-team:gaps-report` to see what the source left blank.
2. `/executive-team:setup` to fill departments, managers, the CSO levels and your strategic objectives.
3. `/executive-team:meet decide Should we move client onboarding to a self-serve portal next quarter?`

## How a meeting works

1. The Chief of Staff reads the protocol, the routing index, your org-profile and the three most recent minutes.
2. It invites every officer whose skills govern the decision at level 2 or 3, and tells you who and why. If nobody matches, it asks you instead of guessing. Re-run with `officers: coo,cto` to force the list.
3. It runs the invited officers in parallel. Each answers as its position, position first, at most 300 words, ending with a confidence level and any peer it wants consulted.
4. One consult round follows: officers named in a `Consult:` line who hold a relevant level 2 or 3 skill answer once.
5. It writes the executive brief: summary, positions, agreement, disagreement, risks, recommended decision, open questions, next steps with an owner officer.
6. It saves minutes to `<minutes_dir>/YYYY-MM-DD-<topic>.md` (default `docs/executive`) in the language you wrote in, and records your decision when you state it.

Officers are candid. They disagree with you and with each other when the facts warrant it, name risks plainly, and say `outside my competence` when a topic is not in their skills table. A level 3 skill answers with authority; level 2 answers independently and flags complex cases; level 1 gives the basics and points you to the officer who holds that skill at level 3.

Any officer can also be asked directly, outside a meeting, and can assess a role against its skills table (current, target, gap, areas for improvement) or propose training entries. Inputs for that come only from your conversation.

## Customizing for your company

`/executive-team:setup` writes `org-profile.yaml` in the project root (git-ignored). Keys:

```yaml
company: { name: "", owner_title: "Owner" }
positions:
  coo:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  # ciso, cto, cmo, cso, cfo: same shape
strategic_objectives:
  - { id: SO1, name: "SME customer growth", critical_skills: ["cso.2", "cmo.6", "coo.5"] }
meeting_defaults: { mode: brainstorm, minutes_dir: docs/executive }
```

A non-empty value in the profile overrides the matrix value; the matrix value stays visible in the agent file as the source. The CSO sheet in the source has no required levels, so set all 11 in `positions.cso.level_overrides` (the setup command offers "all 3" or "all 2" as shortcuts). Until then the CSO answers everything at level 1 and says so.

## Source and fidelity

The officers were built from a skills-by-position workbook (six sheets: COO, CISO, CTO, CMO, CSO, CFO). Every skill in an agent file carries a source pointer with the sheet, the cell range and the original French skill name, so any line can be traced back. The workbook itself and any org-profile are never committed.

Gaps and defects found in the source are reproduced as-is and flagged, never silently fixed. They are listed in `skills/executive-team/gaps-register.md`: empty department and manager fields, placeholder-only strategic objectives, no CSO levels, an empty tasks cell for the CFO's first skill, a duplicated description on the COO's fourth skill, a pasted sentence in the CMO's and CSO's "Corporate Vision and Strategy" descriptions, and columns some sheets lack (no description column on the CFO sheet, no tasks column on the COO, CISO and CTO sheets).

## Privacy

The plugin holds positions, not people. No employee names, ratings, reviews or training records exist in this repository, and the agents are instructed never to store personal data. Assessments and training plans use only what you type in the conversation.

## Development

```
python scripts/extract_positions.py           # workbook -> build/positions.json (workbook: $SKILLS_WORKBOOK or the first *.xlsx here)
python scripts/extract_positions.py --names   # workbook -> build/forbidden-names.txt for the hygiene test
python scripts/verify_agents.py               # check agents against the workbook, regenerate index and register
python scripts/verify_agents.py --check       # fail if the generated files are stale
python -m unittest discover -s tests          # full suite
claude plugin validate . --strict             # manifests
claude plugin validate agents --strict        # also: commands, skills
```

## Roadmap

- Publish to GitHub and list the marketplace publicly.
- Portability of the officer definitions to other coding agents and AI tools (agent bodies are plain markdown).

## License

MIT. See `LICENSE`.
