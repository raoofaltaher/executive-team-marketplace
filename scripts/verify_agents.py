"""Verify officer agent files against the extracted workbook and regenerate the routing index and gaps register.

Usage:
  python scripts/verify_agents.py            # verify agents/ against build/positions.json (if present) and regenerate
  python scripts/verify_agents.py --check    # fail if regenerated files differ from committed ones
"""
import glob
import json
import os
import re
import sys
import tempfile

SRC_RE = re.compile(r"^([A-Z]+)!([A-Z]+\d+:[A-Z]+\d+) · FR: (.+)$")
SKILL_RE = re.compile(r"^### Skill (\d+): (.+)$")
FM_RE = re.compile(r"^---\n(.*?)\n---\n", re.S)
LEVEL_VALUES = ("1", "2", "3", "not specified in source")


def _fm(text):
    m = FM_RE.match(text)
    if not m:
        raise ValueError("missing frontmatter")
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    if "name" not in fm or "description" not in fm:
        raise ValueError("frontmatter needs name and description")
    if "tools" in fm:
        raise ValueError("frontmatter must not set tools (officers inherit all tools by Owner decision)")
    if fm.get("model", "inherit") != "inherit":
        raise ValueError("frontmatter model must be 'inherit' or omitted")
    return fm


def parse_officer(path):
    text = open(path, encoding="utf-8").read()
    fm = _fm(text)
    code_m = re.search(r"^# .+\((\w+)\)\s*$", text, re.M)
    if not code_m:
        raise ValueError(f"{path}: title line must end with (CODE)")
    o = {
        "path": path, "name": fm["name"], "description": fm["description"],
        "code": code_m.group(1), "skills": [],
        "department_missing": bool(re.search(r"^- Department: not specified in source", text, re.M)),
        "manager_missing": bool(re.search(r"^- Position manager: not specified in source", text, re.M)),
        "objectives_template": "Status: TEMPLATE" in text,
    }
    obj = re.search(r"Status: TEMPLATE \(source cells (\S+)", text)
    o["objectives_cells"] = obj.group(1) if obj else "?"
    o["missing_columns"] = sorted({m.group(1) for m in re.finditer(r"^- (Description|Associated tasks): column not present in source", text, re.M)})
    cur = None
    for line in text.splitlines():
        m = SKILL_RE.match(line)
        if m:
            cur = {"n": int(m.group(1)), "name": m.group(2).strip(), "level": None, "level_raw": None,
                   "sheet": None, "cells": None, "fr": None, "keywords": "", "flags": "none"}
            o["skills"].append(cur)
            continue
        if line.startswith("## "):
            cur = None
            continue
        if cur is None:
            continue
        if line.startswith("- Required level:"):
            v = line.split(":", 1)[1].strip()
            if v not in LEVEL_VALUES:
                raise ValueError(f"{path}: skill {cur['n']} bad level '{v}'")
            cur["level_raw"] = v
            cur["level"] = int(v) if v in ("1", "2", "3") else None
        elif line.startswith("- Source:"):
            sm = SRC_RE.match(line.split(":", 1)[1].strip())
            if not sm:
                raise ValueError(f"{path}: skill {cur['n']} bad Source line")
            cur["sheet"], cur["cells"], cur["fr"] = sm.group(1), sm.group(2), sm.group(3).strip()
        elif line.startswith("- Keywords:"):
            cur["keywords"] = line.split(":", 1)[1].strip()
        elif line.startswith("- Flags:"):
            cur["flags"] = line.split(":", 1)[1].strip()
    return o


def load_officers(agents_dir):
    files = sorted(glob.glob(os.path.join(agents_dir, "*.md")))
    return [parse_officer(f) for f in files if "chief-of-staff" not in os.path.basename(f)]


def verify(agents_dir, positions):
    errs = []
    for o in load_officers(agents_dir):
        code = o["code"].lower()
        pos = positions.get(code)
        if pos is None:
            errs.append(f"{o['name']}: no position '{code}' in positions.json")
            continue
        by_n = {s["n"]: s for s in o["skills"]}
        for ps in pos["skills"]:
            s = by_n.get(ps["n"])
            if s is None:
                errs.append(f"{o['name']}: missing skill {ps['n']} ({ps['name_fr']})")
                continue
            if s["fr"] != ps["name_fr"]:
                errs.append(f"{o['name']}: skill {ps['n']} FR name '{s['fr']}' != source '{ps['name_fr']}'")
            if s["level"] != ps["level"]:
                errs.append(f"{o['name']}: skill {ps['n']} level {s['level_raw']} != source {ps['level']}")
            if s["cells"] != ps["cells"]:
                errs.append(f"{o['name']}: skill {ps['n']} cells {s['cells']} != source {ps['cells']}")
        for n in sorted(set(by_n) - {ps["n"] for ps in pos["skills"]}):
            errs.append(f"{o['name']}: skill {n} not in source")
    return errs


def write_index(agents_dir, out_path):
    rows = ["| Officer | Agent | # | Skill | Level | Keywords |", "|---|---|---|---|---|---|"]
    for o in load_officers(agents_dir):
        for s in o["skills"]:
            rows.append(f"| {o['code']} | {o['name']} | {s['n']} | {s['name']} | {s['level'] or 0} | {s['keywords']} |")
    body = ("# Routing index\n\nGenerated by `scripts/verify_agents.py`. Do not edit by hand. "
            "Level 0 = not specified in source; use `org-profile.positions.<code>.level_overrides` to set it.\n\n"
            + "\n".join(rows) + "\n")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)


def write_gaps(agents_dir, out_path):
    rows = ["| Officer | Item | Location | Fill with |", "|---|---|---|---|"]
    for o in load_officers(agents_dir):
        c = o["code"]
        lc = c.lower()
        if o["department_missing"]:
            rows.append(f"| {c} | Department | {c} sheet, Department cell | org-profile.positions.{lc}.department |")
        if o["manager_missing"]:
            rows.append(f"| {c} | Position manager | {c} sheet, Position manager cell | org-profile.positions.{lc}.manager |")
        if o["objectives_template"]:
            rows.append(f"| {c} | Strategic objectives (TEMPLATE) | {o['objectives_cells']} | org-profile.strategic_objectives |")
        for col in o["missing_columns"]:
            rows.append(f"| {c} | {col} column | {c} sheet | column not present in source; edit the workbook |")
        for s in o["skills"]:
            if s["level"] is None:
                rows.append(f"| {c} | Skill {s['n']} required level | {c}!{s['cells']} | org-profile.positions.{lc}.level_overrides.{s['n']} |")
            if s["flags"] and s["flags"] != "none":
                rows.append(f"| {c} | Skill {s['n']} flag: {s['flags']} | {c}!{s['cells']} | edit the workbook |")
    body = ("# Gaps register\n\nGenerated by `scripts/verify_agents.py`. Every field the source workbook left blank "
            "or defective, and where to fill it.\n\n" + "\n".join(rows) + "\n")
    with open(out_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(body)


def main(argv):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    agents = os.path.join(root, "agents")
    skill = os.path.join(root, "skills", "executive-team")
    pj = os.path.join(root, "build", "positions.json")
    errs = []
    if os.path.exists(pj):
        errs = verify(agents, json.load(open(pj, encoding="utf-8")))
    else:
        print("build/positions.json not found; skipping workbook comparison (run scripts/extract_positions.py)")
    refs = os.path.join(skill, "references")
    os.makedirs(refs, exist_ok=True)
    idx = os.path.join(refs, "routing-index.md")
    gaps = os.path.join(refs, "gaps-register.md")
    if "--check" in argv:
        with tempfile.TemporaryDirectory() as d:
            ti, tg = os.path.join(d, "i.md"), os.path.join(d, "g.md")
            write_index(agents, ti)
            write_gaps(agents, tg)
            for a, b, label in ((ti, idx, "routing-index.md"), (tg, gaps, "gaps-register.md")):
                if not os.path.exists(b) or open(a, encoding="utf-8").read() != open(b, encoding="utf-8").read():
                    errs.append(f"{label} is stale; run scripts/verify_agents.py")
    else:
        write_index(agents, idx)
        write_gaps(agents, gaps)
        print(f"wrote {idx}\nwrote {gaps}")
    for e in errs:
        print("ERROR:", e)
    print("OK" if not errs else f"{len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
