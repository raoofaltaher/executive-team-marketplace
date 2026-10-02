import json, os, shutil, subprocess, sys, tempfile, unittest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "scripts"))
import bump_version


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8", newline="") as fh:
        return fh.read()


class HookFileTests(unittest.TestCase):
    def test_hooks_json_registers_one_session_start_command(self):
        cfg = json.loads(read("hooks", "hooks.json"))
        self.assertEqual(list(cfg["hooks"]), ["SessionStart"])
        groups = cfg["hooks"]["SessionStart"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["matcher"], "startup|clear|compact")
        self.assertEqual(len(groups[0]["hooks"]), 1)
        h = groups[0]["hooks"][0]
        self.assertEqual(h["type"], "command")
        self.assertEqual(h["shell"], "bash")
        self.assertIs(h["async"], False)
        self.assertIn("${CLAUDE_PLUGIN_ROOT}", h["command"])
        self.assertTrue(h["command"].endswith('run-hook.cmd" session-start'), h["command"])

    def test_hook_files_are_executable_lf_and_comment_free(self):
        out = subprocess.run(["git", "ls-files", "-s", "hooks/run-hook.cmd", "hooks/session-start"],
                             cwd=ROOT, capture_output=True, text=True).stdout
        self.assertEqual([l.split()[0] for l in out.splitlines()], ["100755", "100755"], out)
        attrs = read(".gitattributes")
        self.assertIn("hooks/session-start text eol=lf", attrs)
        self.assertIn("*.cmd text eol=lf", attrs)
        for name in ("run-hook.cmd", "session-start"):
            text = read("hooks", name)
            self.assertNotIn("\r", text, name)
            for n, line in enumerate(text.splitlines(), 1):
                s = line.strip()
                self.assertFalse(s.upper().startswith("REM "), f"{name}:{n}")
                self.assertFalse(s.startswith("#") and not s.startswith("#!"), f"{name}:{n}")
        cmd = read("hooks", "run-hook.cmd")
        self.assertTrue(cmd.startswith(": << 'CMDBLOCK'\n"), cmd[:40])
        self.assertIn("\nCMDBLOCK\n", cmd)


class VersionToolTests(unittest.TestCase):
    def _copy_tree(self, d):
        shutil.copy(os.path.join(ROOT, ".version-bump.json"), d)
        shutil.copytree(os.path.join(ROOT, ".claude-plugin"), os.path.join(d, ".claude-plugin"))

    def test_declared_versions_agree_with_plugin_json(self):
        rows = bump_version.read_versions(ROOT)
        self.assertEqual(len(rows), 4, rows)
        self.assertEqual(len({v for *_, v in rows}), 1, rows)
        self.assertEqual(rows[0][3], json.loads(read(".claude-plugin", "plugin.json"))["version"])
        dev = [r for r in rows if r[1] == "plugins.1.version"][0]
        self.assertTrue(dev[2].endswith("-dev"), dev)

    def test_write_then_check_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            self._copy_tree(d)
            written = bump_version.write_version("9.9.9", root=d)
            self.assertEqual(written, [".claude-plugin/marketplace.json", ".claude-plugin/plugin.json"])
            self.assertEqual(bump_version.check(root=d), "9.9.9")
            catalog = json.loads(open(os.path.join(d, ".claude-plugin", "marketplace.json"), encoding="utf-8").read())
            self.assertEqual(catalog["plugins"][1]["version"], "9.9.9-dev")
            self.assertEqual(catalog["metadata"]["version"], "9.9.9")

    def test_check_fails_on_drift(self):
        with tempfile.TemporaryDirectory() as d:
            self._copy_tree(d)
            p = os.path.join(d, ".claude-plugin", "plugin.json")
            data = json.loads(open(p, encoding="utf-8").read())
            data["version"] = "1.2.3"
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            self.assertIsNone(bump_version.check(root=d))
            r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "bump_version.py"), "--check", "--root", d],
                               capture_output=True, text=True)
            self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
            self.assertIn("drift", r.stdout)

    def test_missing_field_is_an_error(self):
        with tempfile.TemporaryDirectory() as d:
            self._copy_tree(d)
            p = os.path.join(d, ".claude-plugin", "plugin.json")
            data = json.loads(open(p, encoding="utf-8").read())
            del data["version"]
            with open(p, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            with self.assertRaises(ValueError):
                bump_version.read_versions(d)

    def test_cli_check_and_audit_pass_on_the_committed_tree(self):
        for mode in ("--check", "--audit"):
            r = subprocess.run([sys.executable, "scripts/bump_version.py", mode], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, mode + "\n" + r.stdout + r.stderr)

    def test_cli_rejects_bad_version(self):
        r = subprocess.run([sys.executable, "scripts/bump_version.py", "1.2"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)


if __name__ == "__main__":
    unittest.main()
