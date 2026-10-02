<!--
BEFORE SUBMITTING: read every section. PRs that leave sections blank,
bundle unrelated changes, or show no human review are closed without review.
-->

> **This PR must target the `dev` branch, not `main`.** `main` is the released
> branch; work lands on `dev` first. PRs opened against `main` will be asked to
> retarget before review.

## Who is submitting this PR? (required)

| Field | Value |
|-------|-------|
| Model + version that wrote the change (or "human") | |
| Harness + version (Claude Code, other) | |
| All plugins installed | |
| Human who reviewed the complete diff | |

## What problem does this solve?
<!-- What broke or what was missing, with the exact behaviour you saw:
     the command you ran, what the Chief of Staff or officer did, and a
     transcript excerpt or minutes file. "Improving X" is not a problem. -->

## What does this PR change?
<!-- One to three sentences. -->

## Is this change appropriate for this plugin?
<!-- Does it touch officer sections 1 to 4 (frozen)? Does it add personal
     or company data, an importer, an integration, telemetry? If yes to
     any, it does not belong here. -->

## What alternatives did you consider?
<!-- What else did you try or evaluate, and why was it worse? -->

## Evidence
<!-- For behaviour changes: the same scenario run before and after, with the
     difference described. For structural changes: the check output. -->

- [ ] `python -m unittest discover -s tests` passes
- [ ] `python scripts/build_references.py --check` passes
- [ ] `python scripts/bump_version.py --check` passes
- [ ] `bash tests/hooks/test-session-start.sh` passes
- [ ] `claude plugin validate . --strict`, `.claude-plugin/plugin.json --strict`, `agents --strict`, `skills --strict` pass

## Related issues and PRs
<!-- #number, or "none found" after searching open and closed items -->

## Human review
- [ ] A human has reviewed the complete diff before submission
