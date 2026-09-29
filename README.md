# executive-team-marketplace

<p align="center">
  <img src="assets/plugin.png" alt="The executive team around the table: COO, CTO, CISO, CFO, CMO and CSO, with the Chief of Staff at the whiteboard and the executive brief on the wall. The head seat is yours, the Owner." width="800">
</p>

A Claude Code plugin marketplace. Its first plugin, **executive-team**, gives you an AI executive team (COO, CISO, CTO, CMO, CSO, CFO) and a Chief of Staff who runs the meeting. You are the Owner: you bring a real business case, the right officers answer in parallel as candid executives, and you get one executive brief with positions, disagreements, risks, a recommended decision, and saved minutes.

## Installation

Register the marketplace, then install the plugin:

```
/plugin marketplace add raoofaltaher/executive-team-marketplace
/plugin install executive-team@executive-team-marketplace
```

From a terminal:

```
claude plugin marketplace add raoofaltaher/executive-team-marketplace
claude plugin install executive-team@executive-team-marketplace
```

To try the development branch (uninstall `executive-team` first; both register the same agents and skills):

```
claude plugin install executive-team-dev@executive-team-marketplace
```

## Available plugins

| Plugin | Description | Docs |
|---|---|---|
| `executive-team` | Six officers built from a skills-by-position matrix plus a Chief of Staff; `/executive-team:meet`, `/executive-team:setup`, `/executive-team:gaps-report` | [plugins/executive-team/README.md](plugins/executive-team/README.md) |
| `executive-team-dev` | The same plugin from the `dev` branch, for contributors and testers | same |

## Quick start

1. `/executive-team:gaps-report` to see which fields the source matrix left blank.
2. `/executive-team:setup` to fill departments, managers and your strategic objectives into a git-ignored `org-profile.yaml`, through multiple-choice questions.
3. `/executive-team:meet decide Should we move client onboarding to a self-serve portal next quarter?`

## Marketplace structure

```
executive-team-marketplace/
├── .claude-plugin/
│   └── marketplace.json        # plugin catalog
├── plugins/
│   └── executive-team/         # the plugin: agents/, skills/, scripts/, tests/
├── scripts/bump_version.py     # keeps plugin.json and the catalog entry in step
├── CONTRIBUTING.md             # branches, PR flow, release flow
├── AGENTS.md / CLAUDE.md       # rules for human and AI contributors
├── RELEASE-NOTES.md
└── LICENSE                     # MIT
```

## Branches

- `main`: released. Marketplace installs read this branch. Only the maintainer merges here.
- `dev`: integration. All pull requests target `dev`. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) and [AGENTS.md](AGENTS.md), fork, branch from `dev`, and open a pull request against `dev` with the template filled in. This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md).

## Support

- Issues: https://github.com/raoofaltaher/executive-team-marketplace/issues

## License

MIT. See [LICENSE](LICENSE).
