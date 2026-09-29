import os, sys, unittest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_XLSX = sorted(f for f in os.listdir(_ROOT) if f.lower().endswith(".xlsx"))
WB = os.environ.get("SKILLS_WORKBOOK") or (os.path.join(_ROOT, _XLSX[0]) if _XLSX else "")

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

    def test_forbidden_names_tokens_come_from_people_cells(self):
        from extract_positions import forbidden_names
        tokens = forbidden_names(WB)
        self.assertGreaterEqual(len(tokens), 4)
        self.assertTrue(all(len(t) >= 3 and t == t.lower() for t in tokens))
        # tokens must not be ordinary words from the skills tables
        self.assertNotIn("gestion", tokens)

    def test_workbook_basename_helper(self):
        from extract_positions import workbook_basename
        self.assertEqual(workbook_basename("some/dir/My Book.xlsx"), "My Book")


if __name__ == "__main__":
    unittest.main()
