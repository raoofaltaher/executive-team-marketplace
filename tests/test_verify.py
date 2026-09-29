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
            self.assertIn("| SMP | Strategic objectives (TEMPLATE) | SMP!F11:G16 |", g)
            self.assertIn("| SMP | Associated tasks column | SMP sheet | column not present in source; edit the workbook |", g)


if __name__ == "__main__":
    unittest.main()
