# Pantheon 0.3.0 — installable technical preview

## Install from a release candidate

Install upstream Hermes first, with profile-distribution support. Use `hermes profile install --help` and `hermes profile update --help` to check capabilities. Every profile declares `hermes_requires: '>=0.23.1'`, the earliest Hermes tested (see [Hermes compatibility](HERMES_COMPATIBILITY.md)). Install Hermes with its official installer; a shallow git clone reports version `unknown` and Hermes will refuse the profiles. Python 3.10+; Windows users should follow the upstream Hermes runtime guidance (WSL may be appropriate). The CLI itself is cross-platform Python; live Hermes acceptance has only been run on Linux.

```sh
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# PowerShell: .\.venv\Scripts\Activate.ps1
python -m pip install /path/to/pantheon_agent-0.3.0-py3-none-any.whl
pantheon version
pantheon init --preset executive
pantheon doctor
pantheon install --preset executive --apply
pantheon configure --agent hermes --apply
pantheon status
```

The local wheel requires the dependencies declared in pyproject.toml; pip can download them from an index. It is not an offline dependency bundle. `uv tool install /path/to/wheel.whl` or `pipx install /path/to/wheel.whl` are alternatives. The provisional name `pantheon-agent` has not been reserved or published on PyPI.

`init` and `install` default to dry-run. `--apply` stages immutable, versioned distribution sources under `~/.pantheon/distributions/0.3.0/` (override with `PANTHEON_HOME`) and invokes native Hermes with confirmation. Keep this source directory available for native profile updates. If a profile name exists, Hermes must refuse installation without force; no force flag is sent. If an install sequence fails, earlier successful profiles may remain; inspect status rather than blindly retrying. Optional `--alias` asks Hermes to create profile aliases. Pantheon starts no routine, gateway, or external integration. However, current Hermes multiplexes named profiles from a running default gateway: if one is running, newly installed profiles may be served by it immediately. `pantheon doctor` and `pantheon install --apply` warn before installing and list any Pantheon profiles served afterwards. Pantheon profiles ship no bot tokens or jobs, so nothing connects until you add platform credentials; run `hermes -p default gateway stop` first if nothing should be served. Native setup is interactive and may offer other configuration; review choices and skip gateways until authorized.

Presets: executive, developer, creative, academy, research, full. For an individual agent use `pantheon install --agents athena --apply`. Review all bundled SOUL/skills and effective Hermes toolsets before chatting. Profile configuration is not OS isolation. The existing profile config deny lists are a starting point, not verified security guarantees.

## Update and backup

`pantheon backup --agent athena --output /private/path/athena.tar.gz --apply` invokes the native profile export. This may contain conversation history or other personal information; do not publish it. Native exports exclude credentials, so maintain your separate secure backup procedure. The CLI refuses an existing output path. Back up the full runtime separately before upgrade.

`pantheon update --agent athena --apply` displays the recorded distribution origin, asks for confirmation, then delegates native update. Hermes keeps user data and preserves config by default, but may replace distribution-owned SOUL and skills. The command does not force config or overwrite a non-distribution profile.

A CLI wheel upgrade does NOT migrate existing installed profiles to a different source path. Existing v0.1.0 or v0.2.0 distributions installed from a local source checkout can receive the updated templates after that exact source is updated by a reviewed merge; verify `hermes profile info pantheon-athena`, then run native update. Keep local edits and backups. For version-pinned wheel sources, install the new bundle into a separate test profile using `hermes profile install /path/to/0.3.0/athena --name pantheon-athena-test` after extracting the standalone archive. A deliberate migration to the new origin needs a reviewed native workflow and live acceptance testing; do not delete the existing profile or use force as a shortcut. Git-based origins follow their configured upstream branch. Do not assume the CLI's version and each installed profile's version match.

## Developer installation

```sh
python -m pip install -e '.[dev]'
python scripts/sync_templates.py
python scripts/sync_resources.py
python scripts/validate.py
python scripts/sync_resources.py --check
python -m unittest discover -s tests -v
python -m build
python scripts/build_distributions.py --output dist/profiles
python scripts/check_artifacts.py --dist dist
```

Use a clean output directory for each release. The canonical templates live outside the Python package; generated resources are committed for repeatable builds and CI checks. Do not edit generated copies. Dependency ranges are declared; lockfiles and reproducibility across OSes remain release gates. CI configuration exists but hosted CI has not run here.

## Native distributions and hosting

Extract an individual distribution ZIP into a fresh directory and run `hermes profile install ./extracted-directory`. Each archive has its distribution.yaml at root. A maintainer may place each extracted bundle in a separate reviewed Git repository; GitHub, GitLab, Gitea or Forgejo are viable. The main project remains a monorepo; generated repositories must be synchronized from a single release commit. Native install from the monorepo root is not supported. No repository has been created or pushed.

Suggested GitHub release artifacts: wheel, sdist, source ZIP, eight standalone bundles, SHA256SUMS, release notes. Proposed package index is PyPI (trusted publishing, manual environment approval). Proposed container registry is GHCR. Documentation can be GitHub Pages/MkDocs. All publication is separately authorized. Current workflows build local/CI artifacts only; they contain no PyPI or GHCR publish job or token.

## Server/developer roadmap

0.4.0: pin a tested upstream Hermes Docker image, use Compose persistent state volumes, unprivileged services, opt-in gateways, no Docker socket, separate experimental worker, backup/recovery and resource sizing tests. Ubuntu LTS VPS is the initial target; local PC, NAS and ARM are alternatives. Cloud model inference avoids local GPU requirements. No Dockerfile or Compose service is released as working in this candidate.

0.5.0: native room lifecycle, authenticated approvals, Obsidian staging and Grokbot adapters; one routine owner and one authoritative work record. Preserve the local ledger as reference until server-side authentication and permission enforcement exist. Review platform-specific gateway setup against the installed Hermes version; current upstream may multiplex profiles on a shared gateway. Do not blindly reuse older multi-service commands.

0.6.0: versioned extension contracts and scaffolds for agents, skills, institutions and adapters. Developer templates may not grant permission or auto-install arbitrary code. Keep benchmark sessions isolated. Governed self-improvement: local proposal -> tests -> independent review -> explicit human approval -> PR -> CI -> versioned release. Personal memories and local learned skills never sync upstream automatically.

## Upstream references
- https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions
- https://hermes-agent.nousresearch.com/docs/reference/profile-commands
- https://hermes-agent.nousresearch.com/docs/reference/cli-commands
