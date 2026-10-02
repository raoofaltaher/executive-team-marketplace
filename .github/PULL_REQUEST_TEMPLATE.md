<!--
Pull requests are accepted from the repository owner only; see LICENSE and
CONTRIBUTING.md. Others: open an issue instead.

BEFORE SUBMITTING: fill in every section with specifics. PRs that leave
sections blank, bundle unrelated changes, or show no human review are
closed without review. PR #5 is a worked example of a complete description.
-->

> Targets `dev`. <!-- `main` is the released branch; only release PRs from `dev` target it. -->

## Who is submitting this PR? (required)

| Field | Value |
|-------|-------|
| Model + version that wrote the change (or "human") | <!-- name each model and the stage it did, e.g. "Model A (spec and plan), Model B (execution)" --> |
| Harness + version (Claude Code, other) | |
| All plugins installed | |
| Human who reviewed the complete diff | |

## What problem does this solve?
<!-- What broke or what was missing, with the exact behaviour you saw:
     the command you ran, what the Chief of Staff or officer did, and a
     transcript excerpt or minutes file. "Improving X" is not a problem.
     Link the spec and plan if there are any:
     docs/superpowers/specs/<date>-<topic>-design.md, docs/superpowers/plans/<date>-<topic>.md -->

## What does this PR change?
<!-- One to three sentences. Name any file that moved and why. Name the
     version if this PR bumps it. -->

## Is this change appropriate for this plugin?
<!-- Say it plainly: did officer sections 1 to 4 change? Were content files
     edited, or only moved? Does it add personal or company data, an
     importer, an integration, telemetry? If yes to any of the last four,
     it does not belong here. -->

## What alternatives did you consider?
<!-- Each alternative and why it lost, one sentence each. -->

## Evidence
<!-- Tick only what you ran on the final commit, and give the counts. -->

- [ ] `python -m unittest discover -s tests` passes (N tests)
- [ ] `python scripts/build_references.py --check` passes
- [ ] `python scripts/bump_version.py --check` passes (and `--audit` for a release)
- [ ] `bash tests/hooks/test-session-start.sh` passes (N cases)
- [ ] `claude plugin validate . --strict`, `.claude-plugin/plugin.json --strict`, `agents --strict`, `skills --strict` pass
- Live check: <!-- what you ran in a real session and what you saw: a meeting before and after the change, or `claude -p --plugin-dir .` quoting the bootstrap -->
- Exercised by hand: <!-- what the suites do not cover and you tried yourself: Windows cmd.exe, paths with spaces, Claude Desktop, an upgrade from the previous release -->
- Review: <!-- who reviewed the branch before this PR (a fresh reviewer, which model) or "self-review only", and why -->

## Related issues and PRs
<!-- #number, or "none found" after searching open and closed items -->

## Human review
- [ ] A human has reviewed the complete diff before submission
