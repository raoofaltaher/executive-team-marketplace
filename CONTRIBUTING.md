# Contributing

Thank you for helping improve the executive-team marketplace and its plugins.

## Branches

- `main` is the released branch. Every install from the marketplace reads it. Only the maintainer merges into it, and every merge is a release with a version bump and release notes.
- `dev` is the integration branch. All work lands here first. Pull requests must target `dev`; a PR opened against `main` will be asked to retarget.

## How to contribute

1. Fork the repository and switch to the `dev` branch.
2. Create a branch for your change, named for what it does (for example `fix/cso-invite-reason` or `feat/officer-answer-format`).
3. Make one change per branch. Bundled unrelated changes are closed without review.
4. Run the checks from the plugin folder before you open the PR:

   ```
   cd plugins/executive-team
   python scripts/build_references.py --check
   python -m unittest discover -s tests
   claude plugin validate . --strict
   claude plugin validate agents --strict
   claude plugin validate skills --strict
   ```

5. Open a pull request against `dev` and fill in every section of the template. A human must have reviewed the complete diff before submission.

## What is welcome

- Fixes to the meeting protocol, the Chief of Staff, or the user-invoked skills, with a transcript or minutes file that shows the problem and the fix.
- Clearer wording in agent or skill files, with evidence that agents follow the new wording better (run the scenario before and after).
- New plugins for this marketplace that follow the same conventions: agents with trigger-style descriptions and a "When to invoke" section, user-invoked skills with `allowed-tools`, no personal data.
- Documentation fixes.

## What is not accepted

- Changes to sections 1 to 4 of any officer agent. Those sections reproduce the source skills matrix verbatim and are the plugin's content of record. Gaps and defects in them are filled through `org-profile.yaml`, never by editing the files.
- Anything that stores, requests, or reproduces personal data about employees.
- Third-party service integrations, telemetry, or network calls inside agents or skills.
- Behaviour-shaping wording changes without a before/after scenario.
- Project-specific or personal configuration submitted as plugin defaults.

## Reporting problems

Open an issue with the template that fits. Include the harness and model versions, what you asked, what the agent did, and the minutes file or transcript excerpt. Search open and closed issues first.

## Maintainer release flow

1. Merge `dev` into `main` with a merge commit.
2. Run `python scripts/bump_version.py <x.y.z>` at the repository root; it updates the plugin manifest and the marketplace entry together.
3. Add a section to `RELEASE-NOTES.md`.
4. Commit, tag `executive-team--v<x.y.z>`, and push `main`, `dev`, and the tag.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).
