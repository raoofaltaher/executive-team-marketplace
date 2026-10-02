# Branch protection

Goal: only the maintainer (`@raoofaltaher`) can merge into `dev` and `main`; nobody, including the maintainer, pushes directly to `main`; every change arrives through a pull request.

The rules are GitHub repository rulesets. Apply them once after the repository exists, either with the script below or by hand in **Settings > Rules > Rulesets**.

## With the script

Requires the GitHub CLI signed in as the repository owner (`gh auth status`).

```
bash scripts/protect-branches.sh raoofaltaher/executive-team-marketplace
```

It creates two rulesets:

| Ruleset | Target | Rules |
|---|---|---|
| `protect-main` | `main` | no deletion, no force push, pull request required with 1 approval from a code owner, conversation resolution required, linear history off (merge commits allowed for releases); bypass: repository admin only |
| `protect-dev` | `dev` | no deletion, no force push, pull request required with 1 approval from a code owner; bypass: repository admin only |

`.github/CODEOWNERS` assigns every path to `@raoofaltaher`, so the required code-owner approval can only come from that account. Because the maintainer is the only admin, only that account can merge.

## By hand

1. Settings > Rules > Rulesets > New ruleset > New branch ruleset.
2. Name `protect-main`, enforcement Active, target branch `main`.
3. Bypass list: Repository admin, mode "Always".
4. Rules: Restrict deletions; Block force pushes; Require a pull request before merging (1 required approval, Require review from Code Owners, Dismiss stale approvals); Require conversation resolution before merging.
5. Repeat as `protect-dev` for `dev` with the same rules.

## Required status check

After the first green run of `.github/workflows/ci.yml` on a pull request, add the `checks` jobs as required status checks to both rulesets (Settings > Rules > Rulesets > edit > Require status checks to pass > add `checks (ubuntu-latest)` and `checks (windows-latest)`). The script does not do this because GitHub only offers a check name once it has run.

## Default branch

Keep `main` as the default branch so marketplace installs and `git clone` read released content. Contributors are told in `CONTRIBUTING.md` and the PR template to target `dev`.
