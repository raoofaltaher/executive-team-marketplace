import os, sys, tempfile, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from build_references import parse_officer, check_structure, write_index, write_gaps
FIX = os.path.join(os.path.dirname(__file__), "fixtures")


def fixture_text():
    with open(os.path.join(FIX, "sample-officer.md"), encoding="utf-8") as fh:
        return fh.read()


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
        self.assertEqual(check_structure(o), [])


class FrontmatterTests(unittest.TestCase):
    def _with_fm(self, extra):
        marker = "description: Sample officer for tests.\n"
        return fixture_text().replace(marker, marker + extra)

    def test_model_inherit_allowed_other_models_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            ok = os.path.join(d, "ok.md"); bad = os.path.join(d, "bad.md")
            with open(ok, "w", encoding="utf-8") as fh:
                fh.write(self._with_fm("model: inherit\ncolor: blue\n"))
            with open(bad, "w", encoding="utf-8") as fh:
                fh.write(self._with_fm("model: opus\n"))
            self.assertEqual(parse_officer(ok)["name"], "chief-sample-officer")
            with self.assertRaises(ValueError):
                parse_officer(bad)


class StructureTests(unittest.TestCase):
    def test_out_of_order_skill_and_wrong_sheet_are_reported(self):
        text = fixture_text().replace("### Skill 2: Second Thing", "### Skill 3: Second Thing").replace("SMP!B8:D8", "XXX!B8:D8")
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "o.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
            errs = check_structure(parse_officer(p))
        self.assertTrue(any("not numbered" in e for e in errs), errs)
        self.assertTrue(any("source sheet XXX" in e for e in errs), errs)


class PluginDefaultLevelTests(unittest.TestCase):
    def test_plugin_default_level_counts_as_level_and_is_registered(self):
        text = fixture_text().replace("- Required level: not specified in source",
                                      "- Required level: 2 (plugin default; not specified in source)")
        with tempfile.TemporaryDirectory() as d:
            agents = os.path.join(d, "agents")  # generated files must not land in the agents folder
            os.makedirs(agents)
            p = os.path.join(agents, "o.md")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
            o = parse_officer(p)
            self.assertEqual(o["skills"][1]["level"], 2)
            self.assertTrue(o["skills"][1]["plugin_default"])
            self.assertEqual(check_structure(o), [])
            idx = os.path.join(d, "i.md"); gaps = os.path.join(d, "g.md")
            write_index(agents, idx); write_gaps(agents, gaps)
            with open(idx, encoding="utf-8") as fh:
                self.assertIn("| SMP | chief-sample-officer | 2 | Second Thing | 2 | second |", fh.read())
            with open(gaps, encoding="utf-8") as fh:
                g = fh.read()
            self.assertIn("| SMP | Skill 2 required level is a plugin default (2); source has none |", g)
            self.assertNotIn("| SMP | Skill 2 required level |", g)


class GenerateTests(unittest.TestCase):
    def test_index_and_gaps(self):
        with tempfile.TemporaryDirectory() as d:
            idx = os.path.join(d, "routing-index.md"); gaps = os.path.join(d, "gaps-register.md")
            write_index(FIX, idx); write_gaps(FIX, gaps)
            with open(idx, encoding="utf-8") as fh:
                i = fh.read()
            with open(gaps, encoding="utf-8") as fh:
                g = fh.read()
            self.assertIn("| SMP | chief-sample-officer | 1 | First Thing | 3 | first, thing |", i)
            self.assertIn("| SMP | chief-sample-officer | 2 | Second Thing | 0 | second |", i)
            self.assertIn("| SMP | Department |", g)
            self.assertIn("| SMP | Skill 2 required level |", g)
            self.assertIn("org-profile.positions.smp.level_overrides.2", g)
            self.assertIn("Skill 2 flag: description duplicates skill 1 in source", g)
            self.assertIn("| SMP | Strategic objectives (TEMPLATE) | SMP!F11:G16 |", g)
            self.assertIn("| SMP | Associated tasks column | SMP sheet |", g)


if __name__ == "__main__":
    unittest.main()
