# executive-team

<p align="center">
  <img src="assets/plugin.png" alt="The executive team around the table: COO, CTO, CISO, CFO, CMO and CSO, with the Chief of Staff at the whiteboard and the executive brief on the wall. The head seat is yours, the Owner." width="800">
</p>

A Claude Code plugin that gives you an AI executive team: a COO, CISO, CTO, CMO, CSO and CFO, plus a Chief of Staff who runs the meeting. You are the Owner. You bring a real business case, the Chief of Staff invites the right officers, they answer in parallel as candid executives, and you get one executive brief with positions, disagreements, risks, a recommended decision and next steps. Minutes are saved so the team remembers what was decided. This repository is the plugin and its own marketplace.

## How it works

At the start of every session the plugin introduces the team in a short bootstrap, so the model knows who is available and how to convene them. Every officer is built from a skills-by-position matrix: job title, required competencies, level per competency (1 Beginner, 2 Intermediate, 3 Expert), and associated tasks. The levels shape how each officer answers. Where the source matrix left fields blank, the plugin says so and lets you fill them for your own company through a git-ignored `org-profile.yaml`.

## Installation

In Claude Code:

```
/plugin marketplace add raoofaltaher/executive-team-marketplace
/plugin install executive-team@executive-team-marketplace
```

From a terminal:

```
claude plugin marketplace add raoofaltaher/executive-team-marketplace
claude plugin install executive-team@executive-team-marketplace
```

To try the development branch (uninstall `executive-team` first; both register the same agents and skills):

```
claude plugin install executive-team-dev@executive-team-marketplace
```

### Updating

```
/plugin marketplace update executive-team-marketplace
/plugin update executive-team
```

### Local development

Open this repository in Claude Code: `.claude/settings.json` registers it as a marketplace and enables the plugin (Claude Code asks you to trust the marketplace once). For a one-off session from another folder:

```
claude --plugin-dir <path-to-this-repository>
```

## The basic workflow

1. `/executive-team:gaps-report` to see what the source matrix left blank.
2. `/executive-team:setup` to fill departments, managers and your strategic objectives through multiple-choice questions.
3. `/executive-team:meet decide Should we move client onboarding to a self-serve portal next quarter?`

The bootstrap offers step 2 on its own the first time you call on the team in a git repository that has no `org-profile.yaml`. Set `EXECUTIVE_TEAM_NUDGE=off` to silence that line.

## What's inside

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

**Commands** (`skills/meet`, `skills/setup`, `skills/gaps-report`)

| Command | What it does |
|---|---|
| `/executive-team:meet [mode] [officers: coo,cfo] <topic>` | Runs a meeting. Modes: `brainstorm`, `decide`, `review`, `plan`, `risk`. Detected from your wording when omitted, confirmed in the first line, asked only when unclear. `officers:` forces the invite list; `now decide` or `mode: risk` reruns the last topic in another mode. |
| `/executive-team:setup` | Interviews you and writes `org-profile.yaml`: departments, managers, missing levels, strategic objectives, extra skills. |
| `/executive-team:gaps-report` | Lists every gap in the source matrix and which ones your org-profile still leaves unfilled. |

**Skills loaded by the model** (`skills/`)

- `using-executive-team`: the one-screen bootstrap injected at session start, after `/clear` and after compaction by `hooks/session-start`.
- `executive-team`: the protocol (level definitions, behaviour rules, officer answer format, meeting modes, brief and minutes formats, override rule) with `references/routing-index.md` and `references/gaps-register.md` (both generated) and `references/matrix-operations.md`.

## How a meeting works

1. The Chief of Staff reads the protocol, the routing index, your org-profile and the three most recent minutes, then settles the mode: explicit if you gave one, otherwise detected from your wording, otherwise it asks you. The first line of every reply confirms the mode and how to change it.
2. It invites every officer whose skills govern the decision at level 2 or 3, and tells you who and why. If nobody matches, it asks you instead of guessing. Re-run with `officers: coo,cto` to force the list.
3. It runs the invited officers in parallel. Each answers as its position, position first, at most 300 words, ending with a confidence level and any peer it wants consulted.
4. One consult round follows: officers named in a `Consult:` line who hold a relevant level 2 or 3 skill answer once.
5. It writes the executive brief: summary, positions, agreement, disagreement, risks, recommended decision, open questions, next steps with an owner officer.
6. It saves minutes to `<minutes_dir>/YYYY-MM-DD-<topic>.md` (default `docs/executive`) in the language you wrote in, and records your decision when you state it.

Officers are candid. They disagree with you and with each other when the facts warrant it, name risks plainly, and say `outside my competence` when a topic is not in their skills table. A level 3 skill answers with authority; level 2 answers independently and flags complex cases; level 1 gives the basics and points you to the officer who holds that skill at level 3.

Any officer can also be asked directly, outside a meeting, and can assess a role against its skills table (current, target, gap, areas for improvement) or propose training entries. Inputs for that come only from your conversation.

## Customizing for your company

`/executive-team:setup` interviews you with multiple-choice questions (defaults offered first, free text always possible) and writes `org-profile.yaml` in the project root (git-ignored). Keys:

```yaml
company: { name: "", owner_title: "Owner" }
positions:
  coo:  { department: "", manager: "Owner", level_overrides: {}, extra_skills: [] }
  # ciso, cto, cmo, cso, cfo: same shape
strategic_objectives:
  - { id: SO1, name: "SME customer growth", critical_skills: ["cso.2", "cmo.6", "coo.5"] }
meeting_defaults: { minutes_dir: docs/executive }   # the meeting mode is never a profile setting
```

A non-empty value in the profile overrides the matrix value; the matrix value stays visible in the agent file as the source. The CSO sheet in the source has no required levels, so the plugin ships defaults (sales-domain skills at 3, executive leadership and corporate vision at 2), marked `plugin default` in the agent file; override any of them in `positions.cso.level_overrides`.

## Source and traceability

The six officers were built from a skills-by-position matrix: one sheet per position with the job title, every required competency, its description and tasks, and the required level. Each skill in an agent file carries a source pointer (sheet, cell range, original French skill name) so any line can be traced to the matrix it came from. Fields the matrix left blank are marked `not specified in source` rather than filled in; defects in the matrix are reproduced and flagged rather than corrected. They are listed in `skills/executive-team/references/gaps-register.md`: empty department and manager fields, placeholder-only strategic objectives, no CSO levels (the plugin ships defaults), an empty tasks cell for the CFO's first skill, a duplicated description on the COO's fourth skill, a pasted sentence in the CMO's and CSO's "Corporate Vision and Strategy" descriptions, and columns some sheets lack (no description column on the CFO sheet, no tasks column on the COO, CISO and CTO sheets). Fill them for your company with `/executive-team:setup`.

## Privacy

The plugin holds positions, not people. No employee names, ratings, reviews or training records exist in this repository, and the agents are instructed never to store personal data. Assessments and training plans use only what you type in the conversation. `org-profile.yaml` and meeting minutes are git-ignored. Nothing in the plugin fetches from or reports to a remote host at runtime.

## When something goes wrong

Open an issue with the bug template: plugin and Claude Code versions, the exact command, what the Chief of Staff or officer did, and the relevant part of the brief or minutes with anything confidential removed. To see what the bootstrap injects, run `bash hooks/session-start` from the repository root; it prints the JSON Claude Code receives.

## Contributing

Pull requests are not accepted. Report bugs and request features through issues, and ask questions in Discussions. See [CONTRIBUTING.md](CONTRIBUTING.md). This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).

## Development

```
python -m unittest discover -s tests                        # test suites
python scripts/build_references.py --check                  # fail if the generated references are stale
python scripts/bump_version.py --check                      # every declared version location agrees
bash tests/hooks/test-session-start.sh                      # the SessionStart hook
claude plugin validate . --strict                           # the marketplace manifest
claude plugin validate .claude-plugin/plugin.json --strict  # the plugin manifest; also: agents, skills
```

`python scripts/build_references.py` regenerates the routing index and gaps register after an agent edit. See [docs/testing.md](docs/testing.md) for what each suite proves and [docs/windows-hooks.md](docs/windows-hooks.md) for how the hook runs on Windows.

## License

Proprietary, source-available. Copyright (c) 2026 RAOOF ALTAHER. All rights reserved. You may install the plugin in your AI agent or coding tool and use it there; you may not copy, modify, redistribute or sell it. See [LICENSE](LICENSE). Releases published before this license were under the MIT License; section 6 of the license sets the cutoff.
