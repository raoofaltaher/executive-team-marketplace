# Contributing

Thank you for helping improve the executive-team plugin.

This repository is source-available, not open source. The code is public so you can see what you install, but every right in it belongs to the owner. Read [LICENSE](LICENSE): you may install the plugin in your AI agent or coding tool and use it, and nothing else.

## How you can help

- **Report a bug.** Open an issue with the bug template.
- **Request a feature or a change.** Open an issue with the feature template. Describe the problem you hit, not a patch.
- **Ask a question or start a discussion.** Use [Discussions](https://github.com/raoofaltaher/executive-team-marketplace/discussions).

Ideas and reports submitted in issues and discussions may be used by the owner freely, as section 3 of the license sets out.

## What is not accepted

- Pull requests, patches or code from anyone other than the owner. They are closed without review.
- Forks, copies, mirrors or modified versions of the plugin published elsewhere.

## Reporting problems

Include the plugin and Claude Code versions, what you asked, what the agent did, and the minutes file or transcript excerpt with anything confidential removed. Search open and closed issues first.

## Maintainer workflow

These rules apply to the owner's own work.

### Branches

- `main` is the released branch. Every install from the marketplace reads it. Every merge into it is a release with a version bump and release notes.
- `dev` is the integration branch. All work lands here first through a pull request.

### Checks

Run from the repository root before every pull request:

```
python -m unittest discover -s tests
python scripts/build_references.py --check
python scripts/bump_version.py --check
bash tests/hooks/test-session-start.sh
claude plugin validate . --strict
claude plugin validate .claude-plugin/plugin.json --strict
claude plugin validate agents --strict
claude plugin validate skills --strict
```

### Content rules

- Sections 1 to 4 of any officer agent are never edited. They reproduce the source skills matrix verbatim. Gaps and defects are filled through `org-profile.yaml`.
- No personal data about employees, no third-party integrations, no telemetry or network calls, no comments in code files.

### Release flow

1. On `dev`: `python scripts/bump_version.py <x.y.z>`, then `python scripts/bump_version.py --audit` (must print `All clear`).
2. Add a section to `RELEASE-NOTES.md`.
3. Commit, open the `dev` to `main` pull request, wait for CI, merge with a merge commit.
4. Tag `v<x.y.z>` on `main`, push the tag, publish the GitHub release with the notes entry.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
