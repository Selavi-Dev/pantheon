# Pantheon

**Eight specialist agents. One accountable intelligence system.**

Pantheon is an independent, open-source starter kit for [Hermes Agent](https://github.com/NousResearch/hermes-agent). It separates executive administration, strategy, intelligence, assurance, architecture, creativity, knowledge and learning from operational execution. Designed for persistent profiles, mobile gateways and an Obsidian knowledge base.

> v0.1.0 — starter kit / technical preview. Not affiliated with Nous Research. No live deployments, credentials, external connectors or personal data are included. The local governance ledger is a reference implementation, not a production authorization service.

## The roster

| Agent | Responsibility | Default model class |
|---|---|---|
| Hermes | Chief of Staff, administration, delegation | Professional |
| Athena | Strategy and decision analysis | Reasoning |
| Argus | Public intelligence and opportunities | Utility |
| Themis | Independent assurance and falsification | Independent reasoning |
| Hephaestus | Systems, robotics and architecture | Reasoning |
| Apollo | Creative direction and brand concepts | Multimodal |
| Mnemosyne | Knowledge and provenance | Professional |
| Socrates | Critical reasoning and education | Professional |

```mermaid
flowchart TD
  Owner[Human executive] --> H[Hermes]
  H --> A[Athena]
  H --> Ar[Argus]
  H --> T[Themis]
  H --> He[Hephaestus]
  H --> Ap[Apollo]
  H --> M[Mnemosyne]
  H --> S[Socrates]
  H --> G[Operations agent / Grokbot]
  H --> E[Engineering executors]
  M --> V[Obsidian / knowledge records]
  T -. independent audit .-> H
```

## Quick start

Prerequisites: Python 3.10+, Git, a current Hermes Agent install with `hermes profile install` support, and your own model credentials. Install Hermes using its upstream instructions. No dependency installation or network calls are made by Pantheon's validation tools.

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python scripts/install_profiles.py                 # prints plan only
python scripts/install_profiles.py --apply --agent hermes
# or install a specialist directly:
hermes profile install ./profiles/athena --alias
hermes -p pantheon-athena setup
hermes -p pantheon-athena tools list
hermes -p pantheon-athena chat
```

The default names are `pantheon-hermes`, `pantheon-athena`, etc. This avoids colliding with your existing default Hermes identity (the name `hermes` is reserved by the distribution installer). The installer never uses `--force`, does not skip confirmations, and never starts a gateway. Inspect every profile's effective capabilities before connecting a messaging platform. Installation uses local profile distributions, not an unsupported monorepo-root install. Configure existing installations manually rather than overwriting memory or credentials.

### Routines: review before activation

Copy `examples/operations-inventory.example.json` to a private file and replace its placeholder with **all** existing operational routines. Normalize purpose keys to match equivalent activities, even when names differ. Then:

```bash
python scripts/plan_routines.py --inventory /path/to/private-inventory.json
python scripts/plan_routines.py --inventory /path/to/private-inventory.json --routine H-01
```

The planner only prints commands, defaults to local delivery, and uses `--paused`. Review the command against `hermes cron create --help`; run it manually, inspect existing jobs, configure sources, and resume explicitly. No scheduled jobs ship in profiles. Equivalent purpose detection depends on an honest and complete inventory and normalized purpose keys, not semantic AI matching.

### Local governance ledger

The standard-library reference ledger records proposed handoffs, enforces idempotency, binds human approval to the immutable proposal digest, allows one atomic claim, and distinguishes claimed completion from independent verification. It **does not** dispatch or execute tasks, authenticate chat users, or connect to external systems.

```bash
python -m pantheon.ledger --db .local/ledger.sqlite propose examples/handoff.json
python -m pantheon.ledger --db .local/ledger.sqlite show PTH-HO-0001
# Review payload + digest; a trusted local operator can approve:
python -m pantheon.ledger --db .local/ledger.sqlite approve PTH-HO-0001 --digest <digest> --actor operator --ttl 3600
```

See [governance](docs/governance.md) for the full lifecycle and threat model. Never grant agent processes write access to this database in a production deployment.

## Repository map

| Path | Contents |
|---|---|
| `profiles/` | Eight native profile distributions with SOUL, baseline config and bundled skills |
| `skills/` | Canonical reusable procedural skills |
| `registry/` | Agent, model, group and disabled routine definitions |
| `governance/` | Shared constitution and operational boundary contract |
| `docs/` | Architecture, deployment, permissions, integrations, rollout and release guidance |
| `schemas/`, `examples/` | Handoff and knowledge proposal contracts and sanitized examples |
| `pantheon/` | Local reference governance ledger |
| `scripts/`, `tests/` | Validation, installer, routine planner and unit tests |

## Guides

- [Architecture and group institutions](docs/architecture.md)
- [Mobile deployment](docs/deployment.md)
- [Security and permissions](docs/security.md)
- [Obsidian and Grokbot integration](docs/integrations.md)
- [Governance and approval ledger](docs/governance.md)
- [Rollout and acceptance](docs/rollout.md)
- [Publishing a release](docs/releasing.md)

## Upstream references

[Profiles](https://hermes-agent.nousresearch.com/docs/user-guide/profiles) · [Profile distributions](https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions) · [Bot Mode](https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode) · [Configuration](https://hermes-agent.nousresearch.com/docs/user-guide/configuration) · [Toolsets](https://hermes-agent.nousresearch.com/docs/reference/toolsets-reference) · [Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron) · [Skills](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills/)

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and [LICENSE](LICENSE). Keep secrets, live vaults, session history and private identifiers out of the repository.
