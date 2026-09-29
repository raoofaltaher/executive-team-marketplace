# Executive Team Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the `executive-team` Claude Code plugin: six officer subagents that reproduce the workbook's six position sheets, a Chief of Staff coordinator, three commands, a customization layer, and a verification script, in a git repository ready for GitHub.

**Architecture:** Plain-markdown agents carry each sheet inline (translated to English, with source pointers). A shared skill holds the protocol, brief format, and two generated files (routing index, gaps register). Two Python scripts handle extraction from the workbook and verification of the agent files. Company-specific data enters only through an ignored `org-profile.yaml`.

**Tech Stack:** Claude Code plugins (agents, commands, skills), Python 3.14 with openpyxl (present) and unittest (stdlib), git, `claude plugin validate`.

**Spec:** `docs/superpowers/specs/2026-09-29-executive-team-design.md`

## Global Constraints

- Plugin name `executive-team`, version `0.1.0`. Commands invoked as `/executive-team:meet`, `/executive-team:setup`, `/executive-team:gaps-report`.
- Agent frontmatter: `name` and `description` only. No `tools`, no `model`.
- Agent names: `chief-of-staff`, `chief-operating-officer`, `chief-information-security-officer`, `chief-technology-officer`, `chief-marketing-officer`, `chief-sales-officer`, `chief-financial-officer`.
- No employee names, ratings, or training rows anywhere in tracked files. The five individual names in the workbook must never appear in the repo.
- `.gitignore` excludes `.remember/`, `*.xlsx`, `org-profile.yaml`, `docs/executive/`, `.claude/settings.local.json`, `build/`, `__pycache__/`.
- All sheet text is translated to English. Each skill keeps `Source: <SHEET>!<cells> · FR: <original French skill name>`.
- Empty source fields read exactly `not specified in source`. Missing columns read exactly `column not present in source`. Strategic objectives block status is exactly `TEMPLATE`.
- Every commit message ends with the line `RAOOF A.`.
- Python scripts run with `python` (3.14) from the repo root; the workbook path defaults to the source skills workbook (a local `.xlsx`, never committed) in the repo root and scripts must degrade gracefully when it is absent (the file is not committed).

## Review Focus

1. A topic that matches no officer at level 2 or 3 (for example "office plants"): the Chief of Staff must say so and ask whether to invite level 1 holders or everyone, not invent a match. Pinned in Task 7 step 3.
2. An `org-profile.yaml` with a bad level override (`level_overrides: {3: 5}`): officers must report the invalid value and fall back to the sheet level. Pinned in Task 3 (SKILL.md override rule) and Task 8 setup validation.
3. CSO skills have no source level: the CSO file must show `not specified in source` for all 11 and the routing index must treat them as level 0 (never auto-invited) until overridden. Pinned in Task 3 verify test and Task 6.
4. A meeting topic phrased in French: officers answer in English unless the Owner writes in another language, in which case they answer in that language. Pinned in Task 3 SKILL.md.
5. Minutes folder missing or a minutes file for the same slug already existing today: create the folder; append `-2`, `-3` to the slug. Pinned in Task 7.

---

## File map

| Path | Responsibility |
|---|---|
| `.gitignore`, `LICENSE`, `README.md` | Repo hygiene and public documentation |
| `.claude-plugin/plugin.json` | Plugin manifest |
| `.claude-plugin/marketplace.json` | Self-hosting marketplace so the folder installs itself |
| `.claude/settings.json` | Enables the plugin when Claude Code opens this folder |
| `scripts/extract_positions.py` | Workbook -> `build/positions.json` (ignored) |
| `scripts/verify_agents.py` | Parses officer files, checks them against `build/positions.json`, regenerates `skills/executive-team/routing-index.md` and `gaps-register.md` |
| `tests/test_extract.py`, `tests/test_verify.py` | unittest suites for both scripts |
| `skills/executive-team/SKILL.md` | Level definitions, behaviour rules, meeting protocol, brief format, override rule |
| `skills/executive-team/routing-index.md` | Generated: officer x skill x level x keywords |
| `skills/executive-team/gaps-register.md` | Generated: every gap with sheet and cell |
| `templates/org-profile.yaml` | Customization template |
| `agents/*.md` | Seven agents |
| `commands/meet.md`, `setup.md`, `gaps-report.md` | Three commands |

## Officer file format (used by Tasks 4-6, parsed by Task 3's script)

```markdown
---
name: chief-operating-officer
description: <one paragraph: title, domains, "candid executive; reports to the Owner">
---
# <English job title> (<CODE>)

## 1. Position card
- Sheet: `COO` (workbook "the source skills workbook", sheet tab COO, cells B2:G19)
- Department: not specified in source -> `org-profile.positions.coo.department`
- Job title: <English> (source: <French verbatim>)
- Position manager: not specified in source -> default `Owner`; `org-profile.positions.coo.manager`
- Sheet instructions (verbatim): "<the instructions paragraph>"

## 2. Level reference (verbatim from sheet)
- 1 - Beginner: <three lines>
- 2 - Intermediate: <three lines>
- 3 - Expert: <three lines>

## 3. Skills table by position
Columns in source: Skill Name; Skill description; Required level        <- list what the sheet has

### Skill 1: Operational Management
- Required level: 3
- Source: COO!B8:D8 · FR: Gestion des opérations (Operational Management)
- Keywords: operations, planning, resource allocation, scheduling, service quality, delivery
- Flags: none
- Description: <English translation of the sheet's description column, or "column not present in source">
- Associated tasks: <English translation of the tasks column, or "column not present in source">

... one block per sheet row, in sheet order ...

## 4. Link with strategic objectives
Status: TEMPLATE (source cells COO!F11:G16 hold only the template's placeholder examples)
| Strategic objectives (placeholder) | Critical skills (placeholder) |
|---|---|
| Ex: SME customer growth | Ex: Needs analysis, Communication |
| Ex: Multi-project delivery | Ex: Development and revision of plans and diagrams, Project Management, Prioritization |
| Ex: Team autonomy | Ex: Autonomy, Digital Tools |
| Ex: Internal structure | Ex: Strategic visions |
Real objectives: read `org-profile.strategic_objectives`; map each `critical_skills` entry of the form `coo.<n>` to Skill n above.

## 5. How this officer operates
<the block defined in Task 4 step 1, identical across officers except the code and the peers line>
```

Parsing rules for `verify_agents.py`: a skill block starts at `### Skill <n>: <name>`; the next lines that start with `- Required level:`, `- Source:`, `- Keywords:`, `- Flags:` are read until the next `###` or `##`. `Required level` is `1`, `2`, `3`, or `not specified in source`. `Source` matches `^([A-Z]+)!([A-Z]+\d+:[A-Z]+\d+) · FR: (.+)$`.

## Skill name translations (fixed; use exactly these)

| Sheet | n | French (verbatim first line of the cell) | English |
|---|---|---|---|
| COO | 1 | Gestion des opérations (Operational Management) | Operational Management |
| COO | 2 | Gestion des processus & standardisation (SOP / Process Management) | Process Management and Standardization (SOP) |
| COO | 3 | Gestion de la relation client (Stakeholder & Client Management) | Stakeholder and Client Relationship Management |
| COO | 4 | Gestion de programme et de portefeuille (Program/Portfolio Management) | Program and Portfolio Management |
| COO | 5 | Expérience client & Customer Success Operations | Customer Experience and Customer Success Operations |
| COO | 6 | Gestion financière des projets (Project Profitability & Commercial Delivery) | Project Financial Management (Project Profitability and Commercial Delivery) |
| COO | 7 | Pilotage de la performance (KPI / Tableaux de bord) | Performance Management (KPIs and Dashboards) |
| COO | 8 | Agilité & gestion de sprint (Agile Delivery) | Agility and Sprint Management (Agile Delivery) |
| COO | 9 | Exercer un leadership exécutif stratégique et piloter la performance des équipes | Strategic Executive Leadership and Team Performance |
| COO | 10 | Gestion de projet (Project Management) | Project Management |
| COO | 11 | Excellence opérationnelle & amélioration continue (Lean/Continuous Improvement) | Operational Excellence and Continuous Improvement (Lean) |
| COO | 12 | Collaboration interéquipes et multidisciplinaire | Cross-Team and Multidisciplinary Collaboration |
| CISO | 1 | Stratégie de cybersécurité | Cybersecurity Strategy |
| CISO | 2 | Gouvernance, risque et conformité (GRC) | Governance, Risk and Compliance (GRC) |
| CISO | 3 | Posture de sécurité interne | Internal Security Posture |
| CISO | 4 | Gestion des risques de cybersécurité | Cybersecurity Risk Management |
| CISO | 5 | Assurance qualité des services de sécurité | Quality Assurance of Security Services |
| CISO | 6 | Réponse aux incidents de sécurité | Security Incident Response |
| CISO | 7 | Gestion des accès et des identités | Identity and Access Management |
| CISO | 8 | Représentation et crédibilité externe | External Representation and Credibility |
| CISO | 9 | Exercer un leadership exécutif stratégique et piloter la performance des équipes | Strategic Executive Leadership and Team Performance |
| CISO | 10 | Gestion de projet (Project Management) | Project Management |
| CISO | 11 | Excellence opérationnelle & amélioration continue (Lean/Continuous Improvement) | Operational Excellence and Continuous Improvement (Lean) |
| CISO | 12 | Collaboration interéquipes et multidisciplinaire | Cross-Team and Multidisciplinary Collaboration |
| CTO | 1 | Vision et stratégie technologique | Technology Vision and Strategy |
| CTO | 2 | Architecture des systèmes et solutions | Systems and Solutions Architecture |
| CTO | 3 | Excellence en ingénierie et standards techniques | Engineering Excellence and Technical Standards |
| CTO | 4 | Sécurité applicative et infrastructurelle (DevSecOps) | Application and Infrastructure Security (DevSecOps) |
| CTO | 5 | Gestion des outils et plateformes technologiques | Technology Tools and Platforms Management |
| CTO | 6 | Leadership technique senior | Senior Technical Leadership |
| CTO | 7 | Exécution technique et livraison | Technical Execution and Delivery |
| CTO | 8 | Exercer un leadership exécutif stratégique et piloter la performance des équipes | Strategic Executive Leadership and Team Performance |
| CTO | 9 | Gestion de projet (Project Management) | Project Management |
| CTO | 10 | Excellence opérationnelle & amélioration continue (Lean/Continuous Improvement) | Operational Excellence and Continuous Improvement (Lean) |
| CTO | 11 | Collaboration interéquipes et multidisciplinaire | Cross-Team and Multidisciplinary Collaboration |
| CMO | 1 | Gouvernance et pilotage stratégique | Governance and Strategic Steering |
| CMO | 2 | Alignement Marketing et Ventes (CMO / CSO) | Marketing and Sales Alignment (CMO / CSO) |
| CMO | 3 | Communication, image de marque et représentation | Communication, Brand Image and Representation |
| CMO | 4 | Développer le positionnement et l'identité de marque | Develop Brand Positioning and Identity |
| CMO | 5 | Produire et coordonner du contenu marketing | Produce and Coordinate Marketing Content |
| CMO | 6 | Contribuer aux initiatives de growth marketing | Contribute to Growth Marketing Initiatives |
| CMO | 7 | Effectuer une veille stratégique et concurrentielle | Conduct Strategic and Competitive Intelligence |
| CMO | 8 | Gérer les partenaires et fournisseurs externes | Manage External Partners and Suppliers |
| CMO | 9 | Leadership exécutif et management de la direction | Executive Leadership and Management of the Leadership Team |
| CMO | 10 | Vision et stratégie d'entreprise | Corporate Vision and Strategy |
| CSO | 1 | Pilotage de l'exécution stratégique | Steering Strategic Execution |
| CSO | 2 | Croissance commerciale et développement des revenus | Commercial Growth and Revenue Development |
| CSO | 3 | Relations clients stratégiques | Strategic Client Relationships |
| CSO | 4 | Analyser les besoins d'affaires des client | Analyze Clients' Business Needs |
| CSO | 5 | Recommander et vendre des solutions logicielles et informatiques | Recommend and Sell Software and IT Solutions |
| CSO | 6 | Gérer le cycle de vente complet | Manage the Full Sales Cycle |
| CSO | 7 | Atteindre les objectifs de vente et contribuer à la croissance | Achieve Sales Targets and Contribute to Growth |
| CSO | 8 | Effectuer une veille du marché et contribuer à la stratégie commerciale | Conduct Market Intelligence and Contribute to Commercial Strategy |
| CSO | 9 | Leadership exécutif et management de la direction | Executive Leadership and Management of the Leadership Team |
| CSO | 10 | Développement de partenariats stratégiques et écosystème | Strategic Partnerships and Ecosystem Development |
| CSO | 11 | Vision et stratégie d'entreprise | Corporate Vision and Strategy |
| CFO | 1 | Gestion des stratégies financières | Financial Strategy Management |
| CFO | 2 | Gestion financière de l'entreprise | Corporate Financial Management |
| CFO | 3 | Gestion des rapports gouvernementaux | Government Reporting Management |
| CFO | 4 | Gestion de la trésorerie | Treasury Management |
| CFO | 5 | Gestion des risques et conformité | Risk Management and Compliance |
| CFO | 6 | Budget et prévisions | Budget and Forecasting |
| CFO | 7 | Relations investisseurs | Investor Relations |
| CFO | 8 | Leadership exécutif et gestion d'équipes | Executive Leadership and Team Management |
| CFO | 9 | Gestion opérationnelle financière | Financial Operations Management |

Sheet cell layouts (row of first skill, columns name/description/tasks/level):

| Sheet | Rows | Name | Description | Tasks | Level | Instructions cell | Level ref cells | Objectives cells |
|---|---|---|---|---|---|---|---|---|
| COO | 8-19 | B | C | none | D | B6 | F6:G8 | F11:G16 |
| CISO | 8-19 | A | B | none | C | A6 | E6:F8 | E10:F15 |
| CTO | 7-17 | A | B | none | C | A5 | E5:F7 | E10:F15 |
| CMO | 8-17 | B | C | D | E | B6 | G6:H8 | G11:H16 |
| CSO | 8-18 | B | C | D | E | B6 | G6:H8 | G11:H16 |
| CFO | 8-16 | B | none | C | D | B6 | F6:G8 | F11:G16 |

Job titles (French -> English): COO "Directeur des opérations et de l'expérience client (COO)" -> "Director of Operations and Customer Experience (COO)"; CISO "Chef Information Security Officer (CISO)" -> "Chief Information Security Officer (CISO)"; CTO "Directeur technique / CTO" -> "Technical Director / CTO"; CMO "Communication Marketing & Branding  (CMO)" -> "Communication, Marketing and Branding (CMO)"; CSO "Directeur des ventes (CSO)" -> "Director of Sales (CSO)"; CFO "Directeur des finances (CFO)" -> "Director of Finance (CFO)".

---

### Task 1: Repository scaffold and plugin manifests

**Files:**
- Create: `.gitignore`, `LICENSE`, `README.md`, `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.claude/settings.json`

**Interfaces:**
- Produces: a git repo with the plugin skeleton that `claude plugin validate .` accepts.

- [ ] **Step 1: Initialize git and write `.gitignore`**

```bash
cd S:/Org_Agents && git init -b main
```

`.gitignore`:
```
# session and memory tooling
.remember/
.claude/settings.local.json
# source workbook (contains employee data; never commit)
*.xlsx
# company-specific configuration and meeting minutes
org-profile.yaml
docs/executive/
# build artifacts
build/
__pycache__/
*.pyc
```

- [ ] **Step 2: Write `LICENSE` (MIT, year 2026, holder "RAOOF A.")**

Standard MIT text with the line `Copyright (c) 2026 RAOOF A.`

- [ ] **Step 3: Write `.claude-plugin/plugin.json`**

```json
{
  "name": "executive-team",
  "description": "An AI executive team (COO, CISO, CTO, CMO, CSO, CFO) plus a Chief of Staff, built from a skills-by-position matrix. Bring real business cases to a candid multi-officer deliberation and get an executive brief.",
  "version": "0.1.0",
  "author": { "name": "RAOOF A." },
  "license": "MIT",
  "keywords": ["executive-team", "agents", "skills-matrix", "coo", "ciso", "cto", "cmo", "cso", "cfo", "decision-support"]
}
```

- [ ] **Step 4: Write `.claude-plugin/marketplace.json`**

```json
{
  "name": "executive-team",
  "owner": { "name": "RAOOF A." },
  "metadata": { "description": "Marketplace hosting the executive-team plugin", "version": "0.1.0" },
  "plugins": [
    {
      "name": "executive-team",
      "description": "AI executive team built from a skills-by-position matrix",
      "source": "./",
      "strict": false
    }
  ]
}
```

- [ ] **Step 5: Write `.claude/settings.json`**

```json
{
  "extraKnownMarketplaces": {
    "executive-team": { "source": { "source": "directory", "path": "./" } }
  },
  "enabledPlugins": { "executive-team@executive-team": true }
}
```

If `claude plugin validate .` or a later `claude` start reports an unknown shape for `extraKnownMarketplaces`, replace the object with the documented array form `["./"]` and the plugin key with `"executive-team": true`; record which form worked in README.

- [ ] **Step 6: Write a minimal `README.md`** (title, one-paragraph purpose, "Under construction, see docs/superpowers/specs"). Task 9 replaces it.

- [ ] **Step 7: Validate**

Run: `claude plugin validate .`
Expected: no errors (warnings about missing agents/commands are acceptable at this stage).

- [ ] **Step 8: Confirm the workbook and `.remember/` are ignored**

Run: `git status --porcelain --ignored | grep -E "xlsx|\.remember"`
Expected: both lines start with `!!`.

- [ ] **Step 9: Commit**

```bash
git add .gitignore LICENSE README.md .claude-plugin .claude/settings.json docs/
git commit -m "chore: scaffold executive-team plugin repository

RAOOF A."
```

---

### Task 2: Workbook extraction script

**Files:**
- Create: `scripts/extract_positions.py`, `tests/test_extract.py`

**Interfaces:**
- Produces: `build/positions.json` with the schema below, and the function `extract(workbook_path) -> dict`.

Schema:
```json
{
  "coo": {
    "sheet": "COO",
    "job_title_fr": "Directeur des opérations et de l’expérience client (COO)",
    "department": null,
    "manager": null,
    "instructions": "Use this table to identify ...",
    "levels": { "1": "Basic mastery: ...", "2": "Proficient: ...", "3": "Complete mastery: ..." },
    "columns": ["name", "description", "level"],
    "skills": [
      { "n": 1, "name_fr": "Gestion des opérations (Operational Management)", "name_full_fr": "<whole cell>", "description_fr": "...", "tasks_fr": null, "level": 3, "cells": "B8:D8" }
    ],
    "objectives_examples": [["Ex: SME customer growth", "Ex: Needs analysis, Communication"], ["Ex: Multi-project delivery", "..."], ["Ex:Team autonomy", "Ex: Autonomy, Digital Tools"], ["Ex: Internal structure", "Ex: Strategic visions"]],
    "objectives_cells": "F11:G16"
  }
}
```

- [ ] **Step 1: Write the failing test**

`tests/test_extract.py`:
```python
import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
WB = os.path.join(os.path.dirname(__file__), "..", "the source skills workbook")

@unittest.skipUnless(os.path.exists(WB), "workbook not present")
class ExtractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from extract_positions import extract
        cls.data = extract(WB)

    def test_six_positions_with_expected_skill_counts(self):
        counts = {k: len(v["skills"]) for k, v in self.data.items()}
        self.assertEqual(counts, {"coo": 12, "ciso": 12, "cto": 11, "cmo": 10, "cso": 11, "cfo": 9})

    def test_cso_levels_are_none(self):
        self.assertTrue(all(s["level"] is None for s in self.data["cso"]["skills"]))

    def test_coo_first_skill(self):
        s = self.data["coo"]["skills"][0]
        self.assertEqual(s["name_fr"], "Gestion des opérations (Operational Management)")
        self.assertEqual(s["level"], 3)
        self.assertEqual(s["cells"], "B8:D8")
        self.assertIsNone(s["tasks_fr"])

    def test_cfo_has_tasks_but_no_description(self):
        self.assertEqual(self.data["cfo"]["columns"], ["name", "tasks", "level"])
        self.assertIsNone(self.data["cfo"]["skills"][0]["tasks_fr"])
        self.assertIsNotNone(self.data["cfo"]["skills"][1]["tasks_fr"])

    def test_department_and_manager_empty_everywhere(self):
        for v in self.data.values():
            self.assertIsNone(v["department"]); self.assertIsNone(v["manager"])

    def test_objectives_are_placeholders(self):
        for v in self.data.values():
            self.assertEqual(len(v["objectives_examples"]), 4)
            self.assertTrue(all(p[0].startswith("Ex:") for p in v["objectives_examples"]))

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m unittest tests.test_extract -v`
Expected: ImportError / ModuleNotFoundError for `extract_positions`.

- [ ] **Step 3: Write `scripts/extract_positions.py`**

```python
"""Extract the six position sheets of the skills workbook into build/positions.json.

Usage: python scripts/extract_positions.py [workbook.xlsx] [--out build/positions.json]
The workbook is not committed; this script only runs locally.
"""
import json, os, sys, warnings
warnings.filterwarnings("ignore")
import openpyxl

# sheet -> (code, first_row, last_row, name_col, desc_col, tasks_col, level_col, instr_cell, lvl_cols, lvl_first_row, obj_cols, obj_rows, title_cell)
LAYOUT = {
    "COO":  ("coo",  8, 19, "B", "C", None, "D", "B6", ("F", "G"), 6, ("F", "G"), (13, 16), "C4"),
    "CISO": ("ciso", 8, 19, "A", "B", None, "C", "A6", ("E", "F"), 6, ("E", "F"), (12, 15), "B4"),
    "CTO":  ("cto",  7, 17, "A", "B", None, "C", "A5", ("E", "F"), 5, ("E", "F"), (12, 15), "B3"),
    "CMO":  ("cmo",  8, 17, "B", "C", "D",  "E", "B6", ("G", "H"), 6, ("G", "H"), (13, 16), "C4"),
    "CSO":  ("cso",  8, 18, "B", "C", "D",  "E", "B6", ("G", "H"), 6, ("G", "H"), (13, 16), "C4"),
    "CFO":  ("cfo",  8, 16, "B", None, "C", "D", "B6", ("F", "G"), 6, ("F", "G"), (13, 16), "C4"),
}

def _s(v):
    if v is None: return None
    v = str(v).replace("\ufeff", "").replace("\u2028", "\n").strip()
    return v or None

def extract(path):
    wb = openpyxl.load_workbook(path, data_only=True)
    out = {}
    for sheet, (code, r0, r1, nc, dc, tc, lc, instr, lvl_cols, lvl_r0, obj_cols, obj_rows, title) in LAYOUT.items():
        ws = wb[sheet]
        cols = ["name"] + (["description"] if dc else []) + (["tasks"] if tc else []) + ["level"]
        skills = []
        for i, r in enumerate(range(r0, r1 + 1), start=1):
            full = _s(ws[f"{nc}{r}"].value)
            lvl = ws[f"{lc}{r}"].value
            skills.append({
                "n": i,
                "name_fr": full.split("\n")[0].strip() if full else None,
                "name_full_fr": full,
                "description_fr": _s(ws[f"{dc}{r}"].value) if dc else None,
                "tasks_fr": _s(ws[f"{tc}{r}"].value) if tc else None,
                "level": int(lvl) if isinstance(lvl, (int, float)) else None,
                "cells": f"{nc}{r}:{lc}{r}",
            })
        levels = {str(k): _s(ws[f"{lvl_cols[1]}{lvl_r0 + k - 1}"].value) for k in (1, 2, 3)}
        objs = [[_s(ws[f"{obj_cols[0]}{r}"].value), _s(ws[f"{obj_cols[1]}{r}"].value)] for r in range(obj_rows[0], obj_rows[1] + 1)]
        # department / manager labels sit next to empty cells on every sheet; capture whatever is there
        dep_row = int(instr[1:]) - 3; man_row = int(instr[1:]) - 1
        dep = _s(ws[f"{chr(ord(instr[0]) + 1)}{dep_row}"].value)
        man = _s(ws[f"{chr(ord(instr[0]) + 1)}{man_row}"].value)
        out[code] = {
            "sheet": sheet, "job_title_fr": _s(ws[title].value), "department": dep, "manager": man,
            "instructions": _s(ws[instr].value), "levels": levels, "columns": cols, "skills": skills,
            "objectives_examples": objs, "objectives_cells": f"{obj_cols[0]}{obj_rows[0]-2}:{obj_cols[1]}{obj_rows[1]}",
        }
    return out

def main(argv):
    wb = argv[1] if len(argv) > 1 and not argv[1].startswith("--") else "the source skills workbook"
    outp = "build/positions.json"
    if "--out" in argv: outp = argv[argv.index("--out") + 1]
    if not os.path.exists(wb):
        print(f"workbook not found: {wb}"); return 2
    data = extract(wb)
    os.makedirs(os.path.dirname(outp), exist_ok=True)
    with open(outp, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"wrote {outp}: " + ", ".join(f"{k}={len(v['skills'])}" for k, v in data.items()))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

Note on the department/manager cells: on every sheet the label sits in the instructions column and the value cell is one column to the right, three rows above (department) and one row above (manager) the instructions row. The test asserts both are `None`.

- [ ] **Step 4: Run the tests**

Run: `python -m unittest tests.test_extract -v`
Expected: 6 tests PASS. If `test_department_and_manager_empty_everywhere` fails, print the two cells and fix the row arithmetic.

- [ ] **Step 5: Generate the build file and inspect one entry**

Run: `python scripts/extract_positions.py && python -c "import json;d=json.load(open('build/positions.json',encoding='utf-8'));print(d['cmo']['skills'][3])"`
Expected: the CMO skill 4 entry with `tasks_fr` containing four lines and `level` 3.

- [ ] **Step 6: Commit**

```bash
git add scripts/extract_positions.py tests/test_extract.py
git commit -m "feat: extract position sheets from the skills workbook

RAOOF A."
```

---

### Task 3: Shared skill, org-profile template, and verification script

**Files:**
- Create: `skills/executive-team/SKILL.md`, `templates/org-profile.yaml`, `scripts/verify_agents.py`, `tests/test_verify.py`, `tests/fixtures/sample-officer.md`

**Interfaces:**
- Consumes: `build/positions.json` from Task 2 (optional at runtime).
- Produces: `parse_officer(path) -> dict`, `verify(agents_dir, positions_json) -> list[str]` (errors), `write_index(agents_dir, out_path)`, `write_gaps(agents_dir, out_path)`; the generated `routing-index.md` and `gaps-register.md` formats below.

Routing index format (one table):
```
| Officer | Agent | # | Skill | Level | Keywords |
|---|---|---|---|---|---|
| COO | chief-operating-officer | 1 | Operational Management | 3 | operations, planning, ... |
```
Level column shows `0` when the source says `not specified in source` and no override exists.

Gaps register format:
```
| Officer | Item | Location | Fill with |
|---|---|---|---|
| COO | Department | COO!C3 | org-profile.positions.coo.department |
| COO | Position manager | COO!C5 | org-profile.positions.coo.manager |
| COO | Strategic objectives (TEMPLATE) | COO!F11:G16 | org-profile.strategic_objectives |
| COO | Skill 4 flag: description duplicates skill 3 in source | COO!C11 | edit the workbook |
| CSO | Skill 1 required level | CSO!E8 | org-profile.positions.cso.level_overrides.1 |
```

- [ ] **Step 1: Write `skills/executive-team/SKILL.md`**

```markdown
---
name: executive-team
description: Shared protocol for the executive-team plugin: level definitions, officer behaviour rules, meeting modes, executive brief format, org-profile override rule. Loaded by the Chief of Staff and all six officers.
---
# Executive Team Protocol

## Files in this folder
- `routing-index.md`: officer x skill x required level x keywords. The Chief of Staff reads only this to choose officers.
- `gaps-register.md`: every field the source workbook left blank or defective, with the org-profile key that fills it.

## Who is who
- The **Owner** chairs the team and makes every decision. Nobody decides for the Owner.
- The **Chief of Staff** serves the Owner: routes, fans out, synthesizes. Takes no business position.
- The six **officers** (COO, CISO, CTO, CMO, CSO, CFO) hold the positions defined in their agent files. Manager of each is the Owner unless `org-profile.yaml` says otherwise.

## Level definitions (verbatim from the workbook)
- **1 - Beginner.** Basic mastery: Knows and understands the fundamental concepts of the skill. Limited application: Performs simple, well-defined tasks related to the skill in well-defined situations. Supervision required: Requires frequent supervision and guidance to complete tasks.
- **2 - Intermediate.** Proficient: Possesses a deep understanding and can explain complex concepts within the skill set. Moderately proficient: Performs a variety of tasks and can handle more complex situations. Partially proficient: Works independently on routine tasks but may still require occasional assistance with more complex situations.
- **3 - Expert.** Complete mastery: Demonstrates complete mastery of the skill and can participate in its transmission to others. Extensive application: Addresses complex situations and solves diverse problems by applying the skill in innovative ways. Full autonomy: Works completely independently and can supervise or advise others on the application of the skill.

## How levels shape an officer's answer
- Level 3: answer with authority; coach; supervise; propose the plan.
- Level 2: answer independently; flag complex cases explicitly as "needs a second look".
- Level 1: state the basics only; recommend the officer who holds the skill at level 3 (look it up in `routing-index.md`).
- `not specified in source` (level 0 in the index): say so, answer as level 1, and point to the gaps register.

## Officer behaviour rules
1. Position first, reasoning second. Two to four lines of position before any detail.
2. Be candid. Disagree with the Owner and with peers when warranted. Name risks plainly.
3. Say `outside my competence` when the topic is not in your skills table, then name who should take it.
4. Never speak for another officer. Recommend consulting them by name.
5. Answer in the language the Owner writes in. Default English.
6. Matrix operations on request only: assess a person or the role against your table using the columns Skill / Current / Target / Gap / Areas for improvement / Notes; propose training entries with the columns Training description / Related skill / Priority (Critical, High, Medium, Low) / Starting skill level / Completed skill level / Training start / Training finish / Status (Scheduled, In Progress, Completed, Cancelled, On Hold). All inputs come from the conversation. Write nothing about a person to disk unless the Owner names the file.
7. Never store or repeat personal data about employees beyond what the Owner typed in the current conversation.

## Override rule (org-profile.yaml)
1. If `org-profile.yaml` exists in the project root, read it once at startup.
2. A non-empty value there replaces the sheet value: `positions.<code>.department`, `positions.<code>.manager`, `positions.<code>.level_overrides.<n>` (must be 1, 2, or 3), `positions.<code>.extra_skills[]`, `strategic_objectives[]`.
3. An invalid override (level outside 1-3, unknown skill number, unknown position code) is reported in one line and ignored; the sheet value stays.
4. The sheet value remains visible in the agent file as the source. Do not rewrite agent files to apply overrides.
5. If the file is missing, say once per session: "No org-profile.yaml found; using workbook values. Run /executive-team:setup to customize."

## Meeting modes (what the Chief of Staff asks each invited officer)
- `brainstorm`: three options from your domain, each with one line of risk.
- `decide`: yes, no, or yes-with-conditions, plus the single strongest reason.
- `review`: strengths, weaknesses, what you would change.
- `plan`: milestones, dependencies on other officers, resource needs.
- `risk`: top three risks in your domain with likelihood, impact, mitigation.
Mode detection from wording when not given: "should we", "go or no-go", "approve" -> decide; "ideas", "options", "how might we" -> brainstorm; "feedback", "review", "critique" -> review; "roadmap", "plan", "sequence" -> plan; "what could go wrong", "risks" -> risk. Otherwise `meeting_defaults.mode` from org-profile, else `brainstorm`.

## Executive brief format
```
# Executive brief: <topic>
Mode: <mode> | Date: <YYYY-MM-DD> | Invited: <officer codes and one reason each>

## Summary
<3-5 lines>

## Positions
### <Officer title>
<2-4 lines>

## Agreement
## Disagreement
<who, on what, why>
## Risks
## Recommended decision
<one, with conditions>
## Open questions
## Next steps
| Action | Owner officer | When |
```

## Minutes file
Path `docs/executive/YYYY-MM-DD-<slug>.md` (slug: topic lowercased, non-alphanumerics to `-`, max 60 chars; if the file exists append `-2`, `-3`). Content: the brief, then `## Full responses` with each officer's complete answer under its own heading, then `## Decision` with `Pending Owner decision` until the Owner states one, which the Chief of Staff then records verbatim with the date.
```

- [ ] **Step 2: Write `templates/org-profile.yaml`**

```yaml
# executive-team plugin: organization profile
# Copy to the project root as org-profile.yaml (git-ignored) or run /executive-team:setup.
# Empty strings mean "use the workbook value". Levels must be 1, 2, or 3.
company:
  name: ""
  owner_title: "Owner"

positions:
  coo:
    department: ""
    manager: "Owner"
    level_overrides: {}        # e.g. { 4: 2 }
    extra_skills: []           # e.g. - { skill: "...", description: "...", tasks: "...", level: 2 }
  ciso:
    department: ""
    manager: "Owner"
    level_overrides: {}
    extra_skills: []
  cto:
    department: ""
    manager: "Owner"
    level_overrides: {}
    extra_skills: []
  cmo:
    department: ""
    manager: "Owner"
    level_overrides: {}
    extra_skills: []
  cso:
    department: ""
    manager: "Owner"
    level_overrides: {}        # the workbook has no CSO levels; set all 11 here, e.g. { 1: 3, 2: 3, ... }
    extra_skills: []
  cfo:
    department: ""
    manager: "Owner"
    level_overrides: {}
    extra_skills: []

strategic_objectives: []
# - id: SO1
#   name: "SME customer growth"
#   critical_skills: ["cso.2", "cmo.6", "coo.5"]   # <position code>.<skill number>

meeting_defaults:
  mode: brainstorm             # brainstorm | decide | review | plan | risk
  minutes_dir: docs/executive
```

- [ ] **Step 3: Write the failing tests for the verifier**

`tests/fixtures/sample-officer.md` (a two-skill officer used only by tests):
```markdown
---
name: chief-sample-officer
description: Sample officer for tests.
---
# Sample Officer (SMP)

## 1. Position card
- Sheet: `SMP`
- Department: not specified in source -> `org-profile.positions.smp.department`
- Job title: Sample Officer (source: Officier exemple)
- Position manager: not specified in source -> default `Owner`

## 2. Level reference (verbatim from sheet)
- 1 - Beginner: x
- 2 - Intermediate: y
- 3 - Expert: z

## 3. Skills table by position
Columns in source: Skill Name; Skill description; Required level

### Skill 1: First Thing
- Required level: 3
- Source: SMP!B8:D8 · FR: Première chose
- Keywords: first, thing
- Flags: none
- Description: d1
- Associated tasks: column not present in source

### Skill 2: Second Thing
- Required level: not specified in source
- Source: SMP!B9:D9 · FR: Deuxième chose
- Keywords: second
- Flags: description duplicates skill 1 in source
- Description: d1
- Associated tasks: column not present in source

## 4. Link with strategic objectives
Status: TEMPLATE (source cells SMP!F11:G16 hold only the template's placeholder examples)

## 5. How this officer operates
text
```

`tests/test_verify.py`:
```python
import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from verify_agents import parse_officer, verify, write_index, write_gaps
FIX = os.path.join(os.path.dirname(__file__), "fixtures")

class ParseTests(unittest.TestCase):
    def test_parse_fixture(self):
        o = parse_officer(os.path.join(FIX, "sample-officer.md"))
        self.assertEqual(o["name"], "chief-sample-officer")
        self.assertEqual(o["code"], "SMP")
        self.assertEqual([s["n"] for s in o["skills"]], [1, 2])
        self.assertEqual(o["skills"][0]["level"], 3)
        self.assertIsNone(o["skills"][1]["level"])
        self.assertEqual(o["skills"][0]["fr"], "Première chose")
        self.assertEqual(o["skills"][0]["cells"], "B8:D8")
        self.assertEqual(o["skills"][1]["flags"], "description duplicates skill 1 in source")
        self.assertTrue(o["department_missing"]); self.assertTrue(o["manager_missing"]); self.assertTrue(o["objectives_template"])

class VerifyTests(unittest.TestCase):
    def test_verify_against_positions(self):
        positions = {"smp": {"sheet": "SMP", "skills": [
            {"n": 1, "name_fr": "Première chose", "level": 3, "cells": "B8:D8"},
            {"n": 2, "name_fr": "Deuxième chose", "level": None, "cells": "B9:D9"}]}}
        self.assertEqual(verify(FIX, positions), [])

    def test_verify_reports_level_mismatch_and_missing_row(self):
        positions = {"smp": {"sheet": "SMP", "skills": [
            {"n": 1, "name_fr": "Première chose", "level": 2, "cells": "B8:D8"},
            {"n": 2, "name_fr": "Deuxième chose", "level": None, "cells": "B9:D9"},
            {"n": 3, "name_fr": "Troisième", "level": 1, "cells": "B10:D10"}]}}
        errs = verify(FIX, positions)
        self.assertTrue(any("level" in e and "skill 1" in e for e in errs))
        self.assertTrue(any("missing skill 3" in e for e in errs))

class GenerateTests(unittest.TestCase):
    def test_index_and_gaps(self):
        with tempfile.TemporaryDirectory() as d:
            idx = os.path.join(d, "routing-index.md"); gaps = os.path.join(d, "gaps-register.md")
            write_index(FIX, idx); write_gaps(FIX, gaps)
            i = open(idx, encoding="utf-8").read(); g = open(gaps, encoding="utf-8").read()
            self.assertIn("| SMP | chief-sample-officer | 1 | First Thing | 3 | first, thing |", i)
            self.assertIn("| SMP | chief-sample-officer | 2 | Second Thing | 0 | second |", i)
            self.assertIn("| SMP | Department |", g)
            self.assertIn("| SMP | Skill 2 required level |", g)
            self.assertIn("org-profile.positions.smp.level_overrides.2", g)
            self.assertIn("Skill 2 flag: description duplicates skill 1 in source", g)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 4: Run to verify failure**

Run: `python -m unittest tests.test_verify -v`
Expected: ModuleNotFoundError for `verify_agents`.

- [ ] **Step 5: Write `scripts/verify_agents.py`**

```python
"""Verify officer agent files against the extracted workbook and regenerate the routing index and gaps register.

Usage:
  python scripts/verify_agents.py                 # verify agents/ against build/positions.json (if present) and regenerate
  python scripts/verify_agents.py --check         # fail if regenerated files differ from committed ones
"""
import glob, json, os, re, sys

CODE_MAP = {"coo": "COO", "ciso": "CISO", "cto": "CTO", "cmo": "CMO", "cso": "CSO", "cfo": "CFO"}
SRC_RE = re.compile(r"^([A-Z]+)!([A-Z]+\d+:[A-Z]+\d+) · FR: (.+)$")
SKILL_RE = re.compile(r"^### Skill (\d+): (.+)$")
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)

def _fm(text):
    m = FM_RE.match(text)
    if not m: raise ValueError("missing frontmatter")
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1); fm[k.strip()] = v.strip()
    if "name" not in fm or "description" not in fm: raise ValueError("frontmatter needs name and description")
    for bad in ("tools", "model"):
        if bad in fm: raise ValueError(f"frontmatter must not set {bad}")
    return fm

def parse_officer(path):
    text = open(path, encoding="utf-8").read()
    fm = _fm(text)
    code_m = re.search(r"^# .+\((\w+)\)\s*$", text, re.M)
    if not code_m: raise ValueError(f"{path}: title line must end with (CODE)")
    o = {"path": path, "name": fm["name"], "description": fm["description"], "code": code_m.group(1), "skills": []}
    o["department_missing"] = bool(re.search(r"^- Department: not specified in source", text, re.M))
    o["manager_missing"] = bool(re.search(r"^- Position manager: not specified in source", text, re.M))
    o["objectives_template"] = "Status: TEMPLATE" in text
    obj = re.search(r"Status: TEMPLATE \(source cells (\S+)", text); o["objectives_cells"] = obj.group(1) if obj else "?"
    cur = None
    for line in text.splitlines():
        m = SKILL_RE.match(line)
        if m:
            cur = {"n": int(m.group(1)), "name": m.group(2).strip(), "level": None, "level_raw": None, "cells": None, "fr": None, "keywords": "", "flags": "none"}
            o["skills"].append(cur); continue
        if line.startswith("## "): cur = None; continue
        if cur is None: continue
        if line.startswith("- Required level:"):
            v = line.split(":", 1)[1].strip(); cur["level_raw"] = v
            cur["level"] = int(v) if v in ("1", "2", "3") else None
            if v not in ("1", "2", "3", "not specified in source"): raise ValueError(f"{path}: skill {cur['n']} bad level '{v}'")
        elif line.startswith("- Source:"):
            sm = SRC_RE.match(line.split(":", 1)[1].strip())
            if not sm: raise ValueError(f"{path}: skill {cur['n']} bad Source line")
            cur["sheet"], cur["cells"], cur["fr"] = sm.group(1), sm.group(2), sm.group(3).strip()
        elif line.startswith("- Keywords:"): cur["keywords"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Flags:"): cur["flags"] = line.split(":", 1)[1].strip()
    return o

def load_officers(agents_dir):
    files = sorted(glob.glob(os.path.join(agents_dir, "*.md")))
    return [parse_officer(f) for f in files if "chief-of-staff" not in os.path.basename(f)]

def verify(agents_dir, positions):
    errs = []
    for o in load_officers(agents_dir):
        code = o["code"].lower()
        pos = positions.get(code)
        if pos is None: errs.append(f"{o['name']}: no position '{code}' in positions.json"); continue
        by_n = {s["n"]: s for s in o["skills"]}
        for ps in pos["skills"]:
            s = by_n.get(ps["n"])
            if s is None: errs.append(f"{o['name']}: missing skill {ps['n']} ({ps['name_fr']})"); continue
            if s["fr"] != ps["name_fr"]: errs.append(f"{o['name']}: skill {ps['n']} FR name '{s['fr']}' != source '{ps['name_fr']}'")
            if s["level"] != ps["level"]: errs.append(f"{o['name']}: skill {ps['n']} level {s['level_raw']} != source {ps['level']}")
            if s["cells"] != ps["cells"]: errs.append(f"{o['name']}: skill {ps['n']} cells {s['cells']} != source {ps['cells']}")
        extra = set(by_n) - {ps["n"] for ps in pos["skills"]}
        for n in sorted(extra): errs.append(f"{o['name']}: skill {n} not in source")
    return errs

def write_index(agents_dir, out_path):
    rows = ["| Officer | Agent | # | Skill | Level | Keywords |", "|---|---|---|---|---|---|"]
    for o in load_officers(agents_dir):
        for s in o["skills"]:
            rows.append(f"| {o['code']} | {o['name']} | {s['n']} | {s['name']} | {s['level'] or 0} | {s['keywords']} |")
    body = "# Routing index\n\nGenerated by `scripts/verify_agents.py`. Do not edit by hand. Level 0 = not specified in source; use `org-profile.positions.<code>.level_overrides` to set it.\n\n" + "\n".join(rows) + "\n"
    with open(out_path, "w", encoding="utf-8", newline="\n") as f: f.write(body)

def write_gaps(agents_dir, out_path):
    rows = ["| Officer | Item | Location | Fill with |", "|---|---|---|---|"]
    for o in load_officers(agents_dir):
        c = o["code"]; lc = c.lower()
        if o["department_missing"]: rows.append(f"| {c} | Department | {c} sheet, Department cell | org-profile.positions.{lc}.department |")
        if o["manager_missing"]: rows.append(f"| {c} | Position manager | {c} sheet, Position manager cell | org-profile.positions.{lc}.manager |")
        if o["objectives_template"]: rows.append(f"| {c} | Strategic objectives (TEMPLATE) | {o['objectives_cells']} | org-profile.strategic_objectives |")
        for s in o["skills"]:
            if s["level"] is None: rows.append(f"| {c} | Skill {s['n']} required level | {c}!{s['cells']} | org-profile.positions.{lc}.level_overrides.{s['n']} |")
            if s["flags"] and s["flags"] != "none": rows.append(f"| {c} | Skill {s['n']} flag: {s['flags']} | {c}!{s['cells']} | edit the workbook |")
    body = "# Gaps register\n\nGenerated by `scripts/verify_agents.py`. Every field the source workbook left blank or defective, and where to fill it.\n\n" + "\n".join(rows) + "\n"
    with open(out_path, "w", encoding="utf-8", newline="\n") as f: f.write(body)

def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agents = os.path.join(root, "agents"); skill = os.path.join(root, "skills", "executive-team")
    pj = os.path.join(root, "build", "positions.json")
    errs = []
    if os.path.exists(pj):
        errs = verify(agents, json.load(open(pj, encoding="utf-8")))
    else:
        print("build/positions.json not found; skipping workbook comparison (run scripts/extract_positions.py)")
    idx, gaps = os.path.join(skill, "routing-index.md"), os.path.join(skill, "gaps-register.md")
    if "--check" in argv:
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            ti, tg = os.path.join(d, "i.md"), os.path.join(d, "g.md"); write_index(agents, ti); write_gaps(agents, tg)
            for a, b, label in ((ti, idx, "routing-index.md"), (tg, gaps, "gaps-register.md")):
                if not os.path.exists(b) or open(a, encoding="utf-8").read() != open(b, encoding="utf-8").read(): errs.append(f"{label} is stale; run scripts/verify_agents.py")
    else:
        write_index(agents, idx); write_gaps(agents, gaps); print(f"wrote {idx}\nwrote {gaps}")
    for e in errs: print("ERROR:", e)
    print("OK" if not errs else f"{len(errs)} error(s)")
    return 1 if errs else 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 6: Run the tests**

Run: `python -m unittest tests.test_verify -v`
Expected: 4 tests PASS.

- [ ] **Step 7: Commit**

```bash
git add skills/executive-team/SKILL.md templates/org-profile.yaml scripts/verify_agents.py tests/test_verify.py tests/fixtures/sample-officer.md
git commit -m "feat: shared executive-team protocol, org-profile template, agent verifier

RAOOF A."
```

---

### Task 4: COO and CISO officer agents

**Files:**
- Create: `agents/chief-operating-officer.md`, `agents/chief-information-security-officer.md`

**Interfaces:**
- Consumes: the officer file format and translation table at the top of this plan; `build/positions.json` for the exact French text to translate.
- Produces: two officer files that `verify_agents.py` accepts.

- [ ] **Step 1: Write the shared "How this officer operates" block** (paste into section 5 of every officer, replacing `<CODE>` and `<peers>`):

```markdown
## 5. How this officer operates
- Read `skills/executive-team/SKILL.md` first; it holds the level definitions, behaviour rules, brief format, and override rule.
- Read `org-profile.yaml` in the project root if it exists and apply `positions.<code>` overrides and `strategic_objectives`; report invalid overrides in one line and keep the sheet value.
- Persona: candid executive holding this position. Position first, reasoning second. Disagree with the Owner or a peer when the facts warrant it. Name risks plainly. Say `outside my competence` when a topic is not in the table above, and name the officer who should take it.
- Level behaviour: apply the level of the skill in play. Level 3: authoritative, can coach and supervise. Level 2: independent, flags complex cases. Level 1 or not specified: basics only, recommend the level-3 holder from `skills/executive-team/routing-index.md`.
- Peers: <peers line>. Recommend consulting them by name; never speak for them.
- Matrix operations on request: assess a person or this role against the table using Skill / Current / Target / Gap / Areas for improvement / Notes; propose training entries with Training description / Related skill / Priority / Starting level / Completed level / Start / Finish / Status. Inputs come only from the conversation; write nothing about a person to disk unless the Owner names the file.
- In a meeting: answer the mode question the Chief of Staff sends (brainstorm, decide, review, plan, risk) in at most 300 words, then add a `Confidence:` line (high, medium, low) and a `Consult:` line naming any peer.
- Language: the Owner's language; default English.
```

Peers lines: COO "CTO for technical delivery, CFO for margins and contracts, CSO for client escalations, CISO for security in operations"; CISO "CTO for architecture and DevSecOps, COO for operational controls, CFO for compliance cost and audits, CMO for external representation".

- [ ] **Step 2: Write `agents/chief-operating-officer.md`**

Frontmatter description: "Director of Operations and Customer Experience (COO). Use for daily operations, SOPs and process standardization, client relationship during delivery, program and portfolio management, customer success operations, project profitability and contractual commitments, KPIs and dashboards, agile cadence and sprint reviews, operational team leadership, project management, continuous improvement, cross-team coordination. Candid executive; reports to the Owner."

Section 3 must contain all 12 COO skills in the format above with these exact `Source` lines and levels: 1 `COO!B8:D8` 3; 2 `COO!B9:D9` 3; 3 `COO!B10:D10` 3; 4 `COO!B11:D11` 3 with `Flags: description duplicates skill 3 in source`; 5 `COO!B12:D12` 2; 6 `COO!B13:D13` 2; 7 `COO!B14:D14` 3; 8 `COO!B15:D15` 3; 9 `COO!B16:D16` 3; 10 `COO!B17:D17` 2; 11 `COO!B18:D18` 3; 12 `COO!B19:D19` 3. `Description:` is the English translation of the full name cell's second line (the sheet's skill summary) followed by the description column, both translated faithfully; `Associated tasks: column not present in source`. `Keywords:` five to eight lowercase English terms per skill.

Job title line: `Director of Operations and Customer Experience (COO)`; title heading `# Director of Operations and Customer Experience (COO)`.

- [ ] **Step 3: Write `agents/chief-information-security-officer.md`**

Description: "Chief Information Security Officer (CISO). Use for cybersecurity strategy, governance risk and compliance, internal security posture and policies, cyber risk assessment and mitigation, quality of security deliverables and reports, incident response and crisis communication, identity and access management, external representation in the security ecosystem, security team leadership, project management for security initiatives, threat watch and test standards, cross-team coordination. Candid executive; reports to the Owner."

Source lines and levels: 1 `CISO!A8:C8` 2; 2 `CISO!A9:C9` 3; 3 `CISO!A10:C10` 3; 4 `CISO!A11:C11` 3; 5 `CISO!A12:C12` 3; 6 `CISO!A13:C13` 3; 7 `CISO!A14:C14` 3; 8 `CISO!A15:C15` 2; 9 `CISO!A16:C16` 2; 10 `CISO!A17:C17` 1; 11 `CISO!A18:C18` 1; 12 `CISO!A19:C19` 2. Objectives cells `CISO!E10:F15`. Title `# Chief Information Security Officer (CISO)`.

- [ ] **Step 4: Verify**

Run: `python scripts/verify_agents.py`
Expected: `OK`, and `routing-index.md` lists 24 rows. Fix any reported mismatch by correcting the agent file, not the script.

- [ ] **Step 5: Commit**

```bash
git add agents/chief-operating-officer.md agents/chief-information-security-officer.md skills/executive-team/routing-index.md skills/executive-team/gaps-register.md
git commit -m "feat: add COO and CISO officer agents from the skills matrix

RAOOF A."
```

---

### Task 5: CTO and CMO officer agents

**Files:**
- Create: `agents/chief-technology-officer.md`, `agents/chief-marketing-officer.md`

**Interfaces:** same as Task 4.

- [ ] **Step 1: Write `agents/chief-technology-officer.md`**

Description: "Technical Director / CTO. Use for technology vision and roadmap, systems and solutions architecture (cloud, network, IAM, DevSecOps), engineering standards and maintainability, application and infrastructure security in CI/CD, tooling and platform selection (SIEM, EDR, scanners, ticketing), senior technical leadership and escalations, technical execution and delivery, engineering team leadership, project and product management, continuous improvement of development practices, coordination with AI, backend, frontend, ERP and infrastructure teams. Candid executive; reports to the Owner."

Source lines and levels: 1 `CTO!A7:C7` 3; 2 `CTO!A8:C8` 3; 3 `CTO!A9:C9` 2; 4 `CTO!A10:C10` 1; 5 `CTO!A11:C11` 1; 6 `CTO!A12:C12` 3; 7 `CTO!A13:C13` 3; 8 `CTO!A14:C14` 3; 9 `CTO!A15:C15` 2; 10 `CTO!A16:C16` 2; 11 `CTO!A17:C17` 3. Objectives cells `CTO!E10:F15`. Title `# Technical Director / CTO (CTO)`. Peers line: "CISO for security governance and incidents, COO for delivery cadence, CFO for technology investment, CSO for solution selling".

- [ ] **Step 2: Write `agents/chief-marketing-officer.md`**

Description: "Communication, Marketing and Branding (CMO). Use for governance and KPI/OKR steering, marketing and sales alignment, brand image and external communication, brand positioning and identity, marketing content production, growth marketing and campaign analytics, market and competitive intelligence, agencies and freelancers, executive leadership of the leadership team, corporate vision and strategy. Candid executive; reports to the Owner."

Columns in source: Skill Name; Skill description; Tâches associées (Associated tasks); Required level. Source lines and levels: 1 `CMO!B8:E8` 3; 2 `CMO!B9:E9` 3; 3 `CMO!B10:E10` 3; 4 `CMO!B11:E11` 3; 5 `CMO!B12:E12` 3; 6 `CMO!B13:E13` 3; 7 `CMO!B14:E14` 2; 8 `CMO!B15:E15` 2; 9 `CMO!B16:E16` 2; 10 `CMO!B17:E17` 2. Both `Description:` and `Associated tasks:` are filled from the sheet. Objectives cells `CMO!G11:H16`. Title `# Communication, Marketing and Branding (CMO)`. Peers line: "CSO for demand and conversion, CFO for marketing budget, CTO for product maturity, COO for customer experience".

- [ ] **Step 3: Verify**

Run: `python scripts/verify_agents.py`
Expected: `OK`; routing index has 45 rows.

- [ ] **Step 4: Commit**

```bash
git add agents/chief-technology-officer.md agents/chief-marketing-officer.md skills/executive-team/routing-index.md skills/executive-team/gaps-register.md
git commit -m "feat: add CTO and CMO officer agents from the skills matrix

RAOOF A."
```

---

### Task 6: CSO and CFO officer agents

**Files:**
- Create: `agents/chief-sales-officer.md`, `agents/chief-financial-officer.md`

**Interfaces:** same as Task 4.

- [ ] **Step 1: Write `agents/chief-sales-officer.md`**

Description: "Director of Sales (CSO). Use for strategic execution steering, commercial growth and revenue, strategic client relationships and executive escalations, client business-needs analysis, recommending and selling software and IT solutions, the full sales cycle from prospecting to close, sales targets and performance, market intelligence and commercial strategy, executive leadership of the leadership team, strategic partnerships and ecosystem, corporate vision and strategy. Candid executive; reports to the Owner. Note: the source sets no required levels for this position."

Columns in source: Skill Name; Skill description; Tâches associées (Associated tasks); Required level (empty). All 11 skills have `Required level: not specified in source`. Source lines: 1 `CSO!B8:E8`; 2 `CSO!B9:E9`; 3 `CSO!B10:E10`; 4 `CSO!B11:E11`; 5 `CSO!B12:E12`; 6 `CSO!B13:E13`; 7 `CSO!B14:E14`; 8 `CSO!B15:E15`; 9 `CSO!B16:E16`; 10 `CSO!B17:E17`; 11 `CSO!B18:E18`. Objectives cells `CSO!G11:H16`. Title `# Director of Sales (CSO)`. Peers line: "CMO for demand generation, COO for delivery and customer success, CFO for pricing and margins, CTO for solution feasibility". Add to section 5: "Until `org-profile.positions.cso.level_overrides` sets levels, answer every skill as level 1 and say so once per conversation."

- [ ] **Step 2: Write `agents/chief-financial-officer.md`**

Description: "Director of Finance (CFO). Use for financial strategy, corporate financial management and profitability, government and tax reporting, treasury (burn rate, runway, cash flow, financing), financial risk and internal controls, budgets and forecasts and pricing models, investor relations and fundraising, finance team leadership, billing, collections, supplier payments and bookkeeping with the external accountant. Candid executive; reports to the Owner."

Columns in source: Skill Name; Tâches associées (Associated tasks); Required level. `Description: column not present in source` for all nine skills. Source lines and levels: 1 `CFO!B8:D8` 3 with `Associated tasks: not specified in source` and `Flags: tasks cell empty in source`; 2 `CFO!B9:D9` 3; 3 `CFO!B10:D10` 2; 4 `CFO!B11:D11` 3; 5 `CFO!B12:D12` 2; 6 `CFO!B13:D13` 3; 7 `CFO!B14:D14` 1; 8 `CFO!B15:D15` 2; 9 `CFO!B16:D16` 3. Objectives cells `CFO!F11:G16`. Title `# Director of Finance (CFO)`. Peers line: "COO for project margins and SLAs, CSO for pricing and deals, CTO for technology investment, CISO for compliance and audits".

- [ ] **Step 3: Verify and confirm the gaps register**

Run: `python scripts/verify_agents.py && grep -c "^| " skills/executive-team/routing-index.md && grep -c "^| CSO | Skill" skills/executive-team/gaps-register.md`
Expected: `OK`; 66 lines starting with `| ` in the index (65 skill rows plus the header row; the separator row starts with `|-`); 12 CSO rows (11 skill-level gaps plus the skill 11 flag).

- [ ] **Step 4: Confirm no personal names**

Run: `python scripts/extract_positions.py --names && python -c "import re,subprocess;p=re.compile('|'.join(map(re.escape,open('build/forbidden-names.txt',encoding='utf-8').read().split())),re.I);files=subprocess.run(['git','ls-files'],capture_output=True,text=True).stdout.split();print([f for f in files if p.search(open(f,encoding='utf-8',errors='ignore').read())])"`
Expected: `[]`. The forbidden-name tokens are generated from the workbook's people cells into the git-ignored `build/forbidden-names.txt`; the names themselves never appear in any tracked file, including this plan.

- [ ] **Step 5: Commit**

```bash
git add agents/chief-sales-officer.md agents/chief-financial-officer.md skills/executive-team/routing-index.md skills/executive-team/gaps-register.md
git commit -m "feat: add CSO and CFO officer agents from the skills matrix

RAOOF A."
```

---

### Task 7: Chief of Staff agent

**Files:**
- Create: `agents/chief-of-staff.md`

**Interfaces:**
- Consumes: `skills/executive-team/SKILL.md`, `routing-index.md`, the six officer agent names.
- Produces: the coordinator that `commands/meet.md` delegates to.

- [ ] **Step 1: Write `agents/chief-of-staff.md`**

```markdown
---
name: chief-of-staff
description: Chief of Staff to the Owner. Use to run an executive-team meeting on any business topic: picks the right officers (COO, CISO, CTO, CMO, CSO, CFO) from the routing index, runs them in parallel, synthesizes an executive brief with positions, disagreements, risks and a recommended decision, and writes minutes. Never takes a business position of its own.
---
# Chief of Staff

You serve the Owner, who chairs the executive team and makes every decision. You route, fan out, synthesize, and record. You never argue a business position; you report the officers' positions faithfully, including disagreement.

## Startup
1. Read `skills/executive-team/SKILL.md` (protocol, modes, brief format, override rule).
2. Read `skills/executive-team/routing-index.md`.
3. Read `org-profile.yaml` in the project root if present. Note `meeting_defaults`.
4. List `docs/executive/` if present and read the three most recent `.md` files for context. Do not fail if the folder is missing.

## Running a meeting
Input: a topic, an optional mode (`brainstorm`, `decide`, `review`, `plan`, `risk`), optional explicit officer list.

1. **Mode.** Use the given mode; otherwise detect it with the wording rules in SKILL.md; otherwise `meeting_defaults.mode`; otherwise `brainstorm`.
2. **Invite.** Match the topic against the routing index keywords and skill names. Invite every officer with a matching skill at level 2 or 3. Officers whose only matches are level 1 or 0 are listed as "available on request". If no officer matches at level 2 or 3, stop and ask the Owner: invite level 1 or 0 holders, invite everyone, or rephrase. Print the invite list with one reason each and continue unless the Owner objected in the same message.
3. **Fan out.** Use the Agent tool to run every invited officer in parallel in one message. Each prompt contains: the topic; the mode and its question from SKILL.md; the relevant excerpts of recent minutes (max 40 lines); the org-profile contents if present; the instruction "Answer as your position. Position first. Max 300 words. End with Confidence: and Consult: lines." Subagent type is the officer's agent name (for example `chief-financial-officer`).
4. **Consult requests.** If an officer's `Consult:` line names an officer who was not invited and who holds a relevant skill at level 2 or 3, run that officer once with the same prompt plus the requesting officer's answer. Do this at most once per meeting.
5. **Synthesize.** Write the executive brief exactly in the SKILL.md format. Positions are two to four lines per officer in the officer's own terms. Disagreement lists who, on what, why. Recommended decision is one recommendation with conditions, attributed to the officers who support it. If an officer failed to respond, list it under Positions as `no response`.
6. **Record.** Write the minutes file per SKILL.md (create `docs/executive/` if missing; add `-2`, `-3` if the slug exists today). Tell the Owner the path.
7. **Decision.** When the Owner states a decision in a later message, append it verbatim under `## Decision` with the date.

## What you never do
- Take a business position or soften an officer's disagreement.
- Invent an officer match when the index has none.
- Store or repeat personal data about employees.
- Rewrite agent files or the org-profile; `/executive-team:setup` owns the profile.
```

- [ ] **Step 2: Validate frontmatter and structure**

Run: `claude plugin validate .`
Expected: no errors for `agents/`.

- [ ] **Step 3: Pin the no-match behaviour in the file** (Review Focus item 1): confirm step 2 of "Running a meeting" contains the sentence beginning "If no officer matches at level 2 or 3, stop and ask the Owner". Run: `grep -c "stop and ask the Owner" agents/chief-of-staff.md` Expected: `1`.

- [ ] **Step 4: Commit**

```bash
git add agents/chief-of-staff.md
git commit -m "feat: add Chief of Staff coordinator agent

RAOOF A."
```

---

### Task 8: Commands meet, setup, gaps-report

**Files:**
- Create: `commands/meet.md`, `commands/setup.md`, `commands/gaps-report.md`

**Interfaces:**
- Consumes: `chief-of-staff` agent, `templates/org-profile.yaml`, `skills/executive-team/gaps-register.md`.

- [ ] **Step 1: Write `commands/meet.md`**

```markdown
---
description: Run an executive-team meeting on a topic. Usage: /executive-team:meet [mode] <topic>. Modes: brainstorm, decide, review, plan, risk.
argument-hint: "[brainstorm|decide|review|plan|risk] <topic>"
---
Run an executive-team meeting.

Arguments: `$ARGUMENTS`. If the first word is one of brainstorm, decide, review, plan, risk, it is the mode and the rest is the topic. Otherwise the whole string is the topic and the mode is detected.

Delegate to the `chief-of-staff` agent with this exact instruction:

"Run a meeting. Topic: <topic>. Mode: <mode or 'detect'>. Follow your Running a meeting procedure end to end: invite, fan out in parallel, synthesize the executive brief, write the minutes file, and report its path. Ask the Owner only if no officer matches at level 2 or 3."

When the agent returns, print its brief unchanged and the minutes path. If the Owner then states a decision, send it to the same `chief-of-staff` agent to record under `## Decision`.
```

- [ ] **Step 2: Write `commands/setup.md`**

```markdown
---
description: Interview the Owner and write org-profile.yaml (departments, managers, missing levels, strategic objectives, extra skills). Safe to re-run; updates in place.
---
Create or update `org-profile.yaml` in the project root for the executive-team plugin.

1. If `org-profile.yaml` exists, read it and say which fields are already filled. Otherwise copy `templates/org-profile.yaml` (from this plugin's directory) as the starting point.
2. Read `skills/executive-team/gaps-register.md` to know what the workbook left blank.
3. Ask one topic at a time, using AskUserQuestion when options exist, and accept "skip" for any item:
   a. Company name and the Owner's title (default "Owner").
   b. For each position (COO, CISO, CTO, CMO, CSO, CFO): department name; manager (default Owner).
   c. CSO required levels for its 11 skills (the source has none): offer "all 3", "all 2", or per-skill entry.
   d. Any other level overrides the Owner wants.
   e. Strategic objectives: for each, an id, a name, and the critical skills as `<code>.<n>` references; show the skill numbers from the routing index when asked.
   f. Extra skills per position (skill, description, tasks, level), if any.
   g. Meeting defaults: default mode and minutes directory.
4. Validate: every level is 1, 2, or 3; every critical-skill reference matches an existing officer skill number in `skills/executive-team/routing-index.md`; position codes are among the six. Report each invalid entry and ask again or drop it.
5. Write `org-profile.yaml` with YAML comments preserved from the template. Show a summary table of what is set and what still reads "use workbook value".
6. Remind the Owner that `org-profile.yaml` is git-ignored and never leaves the machine unless they share it.

Never ask for or record information about individual employees (names, ratings, training history).
```

- [ ] **Step 3: Write `commands/gaps-report.md`**

```markdown
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
```

- [ ] **Step 4: Validate**

Run: `claude plugin validate . --strict`
Expected: passes, or only warnings that name fields this plan intentionally omits. Fix real errors.

- [ ] **Step 5: Commit**

```bash
git add commands/
git commit -m "feat: add meet, setup and gaps-report commands

RAOOF A."
```

---

### Task 9: README, final verification, and smoke test

**Files:**
- Modify: `README.md`
- Create: `tests/test_repo_hygiene.py`

**Interfaces:**
- Consumes: everything above.

- [ ] **Step 1: Write `tests/test_repo_hygiene.py`**

```python
import os, re, subprocess, unittest
ROOT = os.path.join(os.path.dirname(__file__), "..")
NAMES_FILE = os.path.join(ROOT, "build", "forbidden-names.txt")  # generated by extract_positions.py --names; git-ignored
AGENTS = ["chief-of-staff", "chief-operating-officer", "chief-information-security-officer", "chief-technology-officer", "chief-marketing-officer", "chief-sales-officer", "chief-financial-officer"]

class HygieneTests(unittest.TestCase):
    def tracked(self):
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
        return [l for l in out.splitlines() if l]

    def test_no_workbook_or_remember_tracked(self):
        for f in self.tracked():
            self.assertFalse(f.endswith(".xlsx"), f); self.assertFalse(f.startswith(".remember/"), f)
            self.assertNotEqual(f, "org-profile.yaml")

    @unittest.skipUnless(os.path.exists(NAMES_FILE), "build/forbidden-names.txt not generated")
    def test_no_personal_names_in_tracked_text(self):
        tokens = open(NAMES_FILE, encoding="utf-8").read().split()
        names = re.compile("|".join(map(re.escape, tokens)), re.I)
        for f in self.tracked():
            p = os.path.join(ROOT, f)
            if f.endswith((".md", ".json", ".yaml", ".py", ".txt")):
                self.assertIsNone(names.search(open(p, encoding="utf-8", errors="ignore").read()), f)

    def test_seven_agents_present_with_minimal_frontmatter(self):
        for a in AGENTS:
            t = open(os.path.join(ROOT, "agents", a + ".md"), encoding="utf-8").read()
            self.assertTrue(t.startswith("---\nname: " + a + "\n"), a)
            fm = t.split("---")[1]
            self.assertIn("description:", fm); self.assertNotIn("tools:", fm); self.assertNotIn("model:", fm)

    def test_generated_files_fresh(self):
        r = subprocess.run(["python", "scripts/verify_agents.py", "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the whole suite**

Run: `python -m unittest discover -s tests -v`
Expected: all tests PASS (extract tests run because the workbook is present locally).

- [ ] **Step 3: Write the full `README.md`**

Sections, in order: title and one-paragraph purpose; "What you get" (7 agents, 3 commands, 1 skill, listed with one line each); "Install" (from GitHub: `claude plugin marketplace add <owner>/<repo>` then `claude plugin install executive-team@executive-team`; local: open the folder, or `claude --plugin-dir <path>`); "First run" (`/executive-team:gaps-report`, then `/executive-team:setup`, then `/executive-team:meet decide <topic>`); "How a meeting works" (the six steps from the Chief of Staff); "Customizing for your company" (org-profile keys, with the CSO-levels note); "Source and fidelity" (built from a skills-by-position workbook; each skill carries a source pointer; the workbook and any org-profile are never committed; the four source defects are listed in `skills/executive-team/gaps-register.md`); "Privacy" (no employee data; matrix operations take input from chat only); "Development" (`python scripts/extract_positions.py`, `python scripts/verify_agents.py`, `python -m unittest discover -s tests`, `claude plugin validate .`); "Roadmap" (publish to GitHub, public marketplace listing, portability to other coding agents); "License" (MIT).

- [ ] **Step 4: Validate the plugin strictly and count components**

Run: `claude plugin validate . --strict && ls agents commands skills/executive-team`
Expected: validation passes; 7 agent files, 3 command files, 3 skill files.

- [ ] **Step 5: Smoke test the meeting flow without a reload**

Because plugin agents load at session start, simulate one meeting in the current session: use the Agent tool with `subagent_type: general-purpose` and a prompt that says "You are the chief-of-staff agent. Your instructions are the contents of agents/chief-of-staff.md (read it). Run a meeting. Topic: 'Should we move our client onboarding to a self-serve portal next quarter?' Mode: decide." Then check: the invite list names COO, CTO, CSO and CFO at least; a file appeared under `docs/executive/`; the brief has the eight headings from SKILL.md. Record the result in the final report. Delete the sample minutes file afterwards (`docs/executive/` is ignored anyway).

- [ ] **Step 6: Commit and tag**

```bash
git add README.md tests/test_repo_hygiene.py
git commit -m "docs: README, repo hygiene tests, smoke-tested v0.1.0

RAOOF A."
git tag executive-team--v0.1.0
```

- [ ] **Step 7: Report**

Tell the Owner: the repo path, the seven agents, the three commands, that a `/reload-plugins` or new session is needed to use them, the smoke-test outcome, and the next steps (create the GitHub repository and push; run `/executive-team:setup`).
