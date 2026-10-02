# executive-team-marketplace: Contributor Guidelines

Read and follow [AGENTS.md](AGENTS.md) before doing anything in this repository.

Short version:

- Branch from `dev`, open pull requests against `dev`, never commit to `main`.
- Never edit sections 1 to 4 of an officer agent in `plugins/executive-team/agents/`; they are the content of record. Fill gaps through `org-profile.yaml`.
- After any agent edit, run `python scripts/build_references.py` in `plugins/executive-team` and commit the regenerated references.
- Before a PR: `python -m unittest discover -s tests` and `claude plugin validate . --strict` (also `agents`, `skills`) from `plugins/executive-team`.
- No personal data, no spreadsheet importers, no third-party integrations in this plugin.
