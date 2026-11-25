# Changelog

## 0.3.0 — installable technical preview

- Builds on the 0.2.0 integrated source (self-improvement skill, routines, review workflow); nothing from 0.2.0 is removed.
- Python wheel and source distribution (`olympus-pantheon`; the CLI command and import package stay `pantheon`) with bundled, synchronized profiles, 25 skills and registries.
- Typer/Rich CLI: init, install, configure, doctor, status, update, backup, agents, groups, routines and version. Dry-run default, explicit native install, immutable staged source; never passes `--force` or `--yes`.
- Six presets; eight standalone native distribution archives with artifact verification.
- Ledger `show()` reads the handoff and its events in one snapshot (fixes an inconsistent read under concurrent approval).
- UTF-8 is explicit for all repository text reads and writes; CI adds a Windows `PYTHONUTF8=0` run.
- CI matrix: Linux, macOS and Windows on Python 3.10 and 3.12; build-only release-candidate workflow; publishing runs only through the separate trusted-publishing workflows, each gated on a protected environment.
- `doctor` and `install --apply` warn when a Hermes gateway is already running, since current Hermes may serve newly installed profiles from it; after install they list any Pantheon profiles now served.
- Live Hermes acceptance on Linux and Windows WSL2; macOS is covered by CI only.
- TestPyPI rehearsal workflow (`publish-testpypi.yml`, manual) alongside the PyPI trusted-publishing workflow.
- Hosting and production interoperability remain release gates.

## 0.2.0 — integrated source candidate

- Shared self-improvement skill granted to all eight profiles, preserving existing roles, skills and baseline tool configurations.
- Agent-specific draft responsibilities, governance boundaries and Obsidian lesson guidance; Grokbot retains operational ownership.
- Two native registry routine definitions, disabled and local-only, with bounded candidates, single-scheduler guidance, idempotent run IDs and no catch-up loops.
- Local private review workflow, candidate-bound evidence and approval records, draft lesson export, and supporting evaluation playbooks.
- Updated source/profile metadata and integration documentation. Native Hermes installation, host policy enforcement and production acceptance remain pending; no scheduler activation or deployment is included.

## 0.1.0 — initial technical preview

- Eight independent Hermes profile distributions and shared constitution.
- Twenty-four canonical skills, seven proposed institutions and twenty inactive routine definitions.
- Dry-run-first installer and routine planner.
- Local reference SQLite handoff ledger with approval digest, expiry and atomic claim.
- Deployment, permission, governance, Obsidian and operations integration guides.
- Automated repository and ledger tests. Live Hermes integration remains to be validated.
