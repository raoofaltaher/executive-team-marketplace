import json, os, re, subprocess, sys, unittest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS = ["chief-of-staff", "chief-operating-officer", "chief-information-security-officer", "chief-technology-officer",
          "chief-marketing-officer", "chief-sales-officer", "chief-financial-officer"]
USER_SKILLS = ("meet", "setup", "gaps-report")


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as fh:
        return fh.read()


class HygieneTests(unittest.TestCase):
    def tracked(self):
        out = subprocess.run(["git", "ls-files"], cwd=ROOT, capture_output=True, text=True).stdout
        return [l for l in out.splitlines() if l]

    def test_only_plugin_files_are_tracked(self):
        for f in self.tracked():
            self.assertFalse(f.endswith((".xlsx", ".xls", ".csv")), f)
            self.assertFalse(f.startswith((".remember/", "build/", "docs/executive/", "plugins/")), f)
            self.assertNotEqual(f, "org-profile.yaml")

    def test_seven_agents_follow_agent_frontmatter_conventions(self):
        for a in AGENTS:
            t = read("agents", a + ".md")
            self.assertTrue(t.startswith("---\nname: " + a + "\n"), a)
            fm = t.split("---")[1]
            self.assertIn("description:", fm)
            self.assertNotIn("tools:", fm)
            self.assertIn("model: inherit", fm)
            self.assertRegex(fm, r"\ncolor: (blue|cyan|green|yellow|magenta|red)\n")
            self.assertRegex(fm, r'description: Use this agent when .*Typical triggers include .*See "When to invoke"')
            self.assertRegex(t, r"\n## (\d\. )?When to invoke\n")
            self.assertIn("**Do not use", t)

    def test_orchestration_uses_namespaced_agents_and_plugin_root(self):
        cos = read("agents", "chief-of-staff.md")
        meet = read("skills", "meet", "SKILL.md")
        skill = read("skills", "executive-team", "SKILL.md")
        self.assertIn("executive-team:chief-of-staff", meet)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", meet)
        self.assertIn("executive-team:chief-financial-officer", cos)
        self.assertIn("minutes_dir", cos)
        self.assertIn("Respond in:", cos)
        self.assertIn("Consulted:", skill)
        self.assertIn("## Officer answer format", skill)
        setup = read("skills", "setup", "SKILL.md")
        template = read("skills", "setup", "org-profile.template.yaml")
        for f in (cos, skill, meet, template, setup):
            self.assertNotIn("meeting_defaults.mode", f)
            self.assertNotIn("mode: brainstorm", f)
        self.assertFalse(os.path.exists(os.path.join(ROOT, "templates")), "template lives inside skills/setup now")
        self.assertIn("AskUserQuestion", setup)
        self.assertIn("multiple-choice", setup)
        cso = read("agents", "chief-sales-officer.md")
        self.assertNotIn("answers at level 1", cso)
        self.assertIn("(plugin default; not specified in source)", cso)
        self.assertIn('Reply "mode: <other>"', skill)
        self.assertIn("Previous meeting:", cos)
        self.assertIn("AskUserQuestion", meet)
        self.assertTrue(skill.splitlines()[2].startswith("description: This skill should be used when"), skill.splitlines()[2])
        with open(os.path.join(ROOT, ".claude-plugin", "marketplace.json"), encoding="utf-8") as fh:
            catalog = json.load(fh)
        by_name = {p["name"]: p for p in catalog["plugins"]}
        self.assertEqual(by_name["executive-team"]["source"], "./")
        self.assertEqual(by_name["executive-team-dev"]["source"]["ref"], "dev")
        for a in AGENTS[1:]:
            self.assertIn("executive-team:executive-team", read("agents", a + ".md"), a)

    def test_bootstrap_skill_introduces_the_team(self):
        t = read("skills", "using-executive-team", "SKILL.md")
        self.assertTrue(t.startswith("---\nname: using-executive-team\n"), t[:60])
        self.assertIn("<SUBAGENT-STOP>", t)
        self.assertIn("## Who is in the room", t)
        for code in ("COO", "CISO", "CTO", "CMO", "CSO", "CFO"):
            self.assertIn(code, t)
        for token in ("/executive-team:meet", "/executive-team:setup", "/executive-team:gaps-report",
                      "executive-team:executive-team", "Confidence:", "Consult:", "org-profile.yaml"):
            self.assertIn(token, t)
        self.assertLess(len(t.splitlines()), 60, "the bootstrap must stay one screen")

    def test_ci_workflow_runs_every_static_check(self):
        wf = read(".github", "workflows", "ci.yml")
        for cmd in ("python -m unittest discover -s tests", "build_references.py --check", "bump_version.py --check",
                    "bash tests/hooks/test-session-start.sh", "shellcheck",
                    "claude plugin validate . --strict", "claude plugin validate .claude-plugin/plugin.json --strict"):
            self.assertIn(cmd, wf, cmd)
        self.assertIn("windows-latest", wf)
        self.assertIn("ubuntu-latest", wf)

    def test_pr_template_asks_for_evidence_like_pr_5(self):
        t = read(".github", "PULL_REQUEST_TEMPLATE.md")
        for section in ("## Who is submitting this PR? (required)", "## What problem does this solve?",
                        "## What does this PR change?", "## Is this change appropriate for this plugin?",
                        "## What alternatives did you consider?", "## Evidence", "## Related issues and PRs",
                        "## Human review", "Live check:", "Exercised by hand:", "Review:", "(N tests)", "(N cases)"):
            self.assertIn(section, t, section)

    def test_user_invoked_skills_replace_legacy_commands(self):
        self.assertFalse(os.path.exists(os.path.join(ROOT, "commands")), "commands/ must be migrated to skills/")
        for s in USER_SKILLS:
            fm = read("skills", s, "SKILL.md").split("---")[1]
            self.assertIn("allowed-tools:", fm, s)
            self.assertIn("description: This skill should be used when", fm, s)
        for gen in ("routing-index.md", "gaps-register.md", "matrix-operations.md"):
            self.assertTrue(os.path.exists(os.path.join(ROOT, "skills", "executive-team", "references", gen)), gen)

    def test_no_workbook_tooling_or_mentions_ship(self):
        for gone in ("scripts/extract_positions.py", "scripts/verify_agents.py", "tests/test_extract.py", "plugins"):
            self.assertFalse(os.path.exists(os.path.join(ROOT, gone)), gone)
        banned = re.compile(r"xlsx|openpyxl|SKILLS_WORKBOOK|extract_positions|verify_agents|workbook", re.I)
        for f in self.tracked():
            if f.endswith((".md", ".json", ".yaml", ".yml", ".py", ".txt", ".sh", ".cmd")) and f != "tests/test_repo_hygiene.py":
                self.assertIsNone(banned.search(read(f)), f)

    def test_generated_files_fresh(self):
        r = subprocess.run([sys.executable, "scripts/build_references.py", "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
