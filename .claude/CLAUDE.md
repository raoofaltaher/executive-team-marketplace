# executive-team: Contributor Guidelines

Read and follow [AGENTS.md](../AGENTS.md) before doing anything in this repository.

Short version:

- Branch from `dev`, open pull requests against `dev`, never commit to `main`.
- Never edit sections 1 to 4 of an officer agent in `agents/`; they are the content of record. Fill gaps through `org-profile.yaml`.
- After any agent edit, run `python scripts/build_references.py` and commit the regenerated references.
- Before a PR, from the repository root: `python -m unittest discover -s tests`, `python scripts/build_references.py --check`, `python scripts/bump_version.py --check`, `bash tests/hooks/test-session-start.sh`, `claude plugin validate . --strict` and `claude plugin validate .claude-plugin/plugin.json --strict` (also `agents`, `skills`).
- No personal data, no spreadsheet importers, no third-party integrations, no telemetry, no comments in code files.
