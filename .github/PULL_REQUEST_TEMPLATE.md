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
| Human who reviewed the complete diff | |

## What problem does this solve?
<!-- What broke or what was missing, with the exact behaviour you saw:
     the command you ran, what the Chief of Staff or officer did, and a
     transcript excerpt or minutes file. "Improving X" is not a problem. -->

## What does this PR change?
<!-- One to three sentences. -->

## Evidence
<!-- For behaviour changes: the same scenario run before and after, with the
     difference described. For structural changes: the check output. -->

- [ ] `python scripts/build_references.py --check` passes in `plugins/executive-team`
- [ ] `python -m unittest discover -s tests` passes
- [ ] `claude plugin validate . --strict`, `agents --strict`, `skills --strict` pass

## Boundaries
- [ ] I did not edit sections 1 to 4 of any officer agent
- [ ] This PR adds no personal data, spreadsheet importer, telemetry, or third-party integration
- [ ] This PR contains one change, not several unrelated ones

## Related issues and PRs
<!-- #number, or "none found" after searching open and closed items -->

## Human review
- [ ] A human has reviewed the complete diff before submission
