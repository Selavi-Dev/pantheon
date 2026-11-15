# Release and publication plan

The proposed release is **v0.3.0 installable technical preview**, pending host acceptance and explicit administrator publication approval. The source version identifies the candidate; no release tag or deployment is implied.

This monorepo contains eight native profile distributions. Install locally from `profiles/<agent>` after cloning. Do not point `hermes profile install` at the monorepo root. Separate remotely installable distributions require independently reviewed profile repositories or distribution branches; do not promise subdirectory URL support.

## Gates before publication

1. Confirm the intended Overflow organization and repository slug, maintainer ownership and MIT licensing. Confirmed owner and repository: `Selavi-Dev/pantheon` (GitHub organization). Creating it and pushing remain separate approvals.
2. Mount the existing Overflow directory and inspect its AGENTS.md, Git status, paths and infrastructure. Integrate on an isolated preparation branch without overwriting existing work. The current candidate is prepared in staging because the existing directory is unavailable here.
3. Load the relevant Obsidian Project and Current State notes from the actual vault. Reconcile institutional decisions and record a reviewed handoff; never publish the vault or private operational inventory.
4. Run `python scripts/validate.py`, `python -O scripts/validate.py`, `python scripts/sync_resources.py --check` and `python -m unittest discover -s tests -v`; build with `python -m build` and verify with `python scripts/check_artifacts.py --dist dist`. CI covers Python 3.10 and 3.12; a local 3.12 run is not evidence of the 3.10 job passing.
5. Review the exact candidate commit and archive for credentials, private records, third-party content and license consistency. The built-in recognizable-secret scan is intentionally limited; it is not a comprehensive credential audit. Use an organization-approved scanner before releasing any imported history.
6. Perform the disposable-host acceptance checklist in [Hermes compatibility](HERMES_COMPATIBILITY.md) against the actual installed version. Verify effective tools, group/gateway isolation, injected-content refusal, paused jobs, no send/publish/production-write capability, and staging rollback. Check both gateway and cron-host timezone behavior.
7. Reconcile every routine with the private Grokbot/Pantheon inventory, including paused jobs and semantically equivalent purposes. All 22 source routines remain disabled. Activation is a separate decision; publication does not activate schedules.
8. Configure branch protection, required checks, maintainer access and a private security disclosure contact. A passing local suite is not a GitHub Actions run.
9. Present the final commit, source archive checksum, test evidence, runtime limits and release notes to the administrator. Obtain explicit approval to publish this exact candidate under the confirmed owner. Recheck any changed files before proceeding.

## Publication after approval

Create or select the confirmed repository, push the reviewed source history, and run its required CI checks. After those checks pass, tag the approved commit `v0.3.0` and create a GitHub prerelease titled `Pantheon v0.3.0 — installable technical preview`. Attach the reviewed wheel, sdist, source archive, eight profile archives and SHA-256 checksums. PyPI publication is a separate approval (see [PyPI publishing](pypi-publishing.md)). Do not push unrelated history or include private state. No publishing command is executed by this preparation workflow.

Release notes should describe the eight profiles, 25 shared skills, seven groups, 22 disabled routines, bounded self-improvement review and its human approval boundary. Explicitly state that the ledger and improvement recorder are trusted local reference tools, not authentication or deployment services. Link the exact Hermes compatibility evidence and untested environments.

## Rollback

Before publication, discard or revise the candidate branch without touching production. For source integration, revert the reviewed integration commit and rerun checks. For a published defective release, mark it superseded and publish a corrective version; preserve audit history. Any later installation needs a separate approved host backup and rollback plan. Keep private evidence, Obsidian history and operator credentials outside source rollbacks.
