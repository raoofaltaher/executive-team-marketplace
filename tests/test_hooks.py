import json, os, subprocess, unittest
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


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


if __name__ == "__main__":
    unittest.main()
