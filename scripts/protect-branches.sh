#!/usr/bin/env bash
# Create the branch rulesets described in docs/branch-protection.md.
# Usage: bash scripts/protect-branches.sh owner/repo
# Requires: gh (GitHub CLI) authenticated as the repository owner.
set -euo pipefail
REPO="${1:?usage: protect-branches.sh owner/repo}"

make_ruleset() {
  local name="$1" branch="$2"
  gh api --method POST "repos/${REPO}/rulesets" \
    --input - <<JSON
{
  "name": "${name}",
  "target": "branch",
  "enforcement": "active",
  "bypass_actors": [
    { "actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always" }
  ],
  "conditions": { "ref_name": { "include": ["refs/heads/${branch}"], "exclude": [] } },
  "rules": [
    { "type": "deletion" },
    { "type": "non_fast_forward" },
    { "type": "required_pull_request",
      "parameters": {
        "required_approving_review_count": 1,
        "dismiss_stale_reviews_on_push": true,
        "require_code_owner_review": true,
        "require_last_push_approval": false,
        "required_review_thread_resolution": true,
        "allowed_merge_methods": ["merge", "squash"]
      }
    }
  ]
}
JSON
  echo "created ruleset ${name} for ${branch}"
}

make_ruleset protect-main main
make_ruleset protect-dev dev
echo "done. Verify at https://github.com/${REPO}/settings/rules"
