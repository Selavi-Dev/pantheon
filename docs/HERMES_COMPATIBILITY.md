# Hermes compatibility review

Review date: 2026-11-13 America/New_York (2026-11-14 UTC). Scope: Pantheon v0.2.0 source candidate; read-only upstream review plus parser-only checks. No Hermes installation, gateway, scheduled job, provider call, Obsidian connection, credential read, or deployment was performed.

## Decision

**Source-compatible in the reviewed areas; deployment documentation corrected. Runtime compatibility with the user's installed Hermes is unverified.** There is no `hermes` executable available in this workspace and no mounted Overflow directory or Obsidian vault. Do not describe this review as an installed-version certification or deployment acceptance.

Latest upstream release observed: [v0.23.1](https://github.com/NousResearch/hermes-agent/releases/tag/v0.23.1). Upstream `main` revision captured through GitHub: [652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab](https://github.com/NousResearch/hermes-agent/commit/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab), commit timestamp 2026-11-14T01:47:22Z. Current website documentation and current `main` are moving targets; this does not establish that every reviewed feature exists in the released v0.23.1 package. The release page itself distinguishes the patch release from fuller upcoming release notes. Pantheon version and Hermes version are independent.

## Findings and required follow-up

| Area | Finding | Action |
|---|---|---|
| Gateway topology | `docs/deployment.md` now distinguishes host startup from named-profile park/unpark operations. Current dedicated multi-profile documentation and source default to one host multiplexer. New standalone named-profile starts/installs can be refused with exit 78. A named-profile start can instead unpark an already served profile. | The corrected deployment guide covers host startup, served/parked status and shared restart impact. Inventory the host and existing services before following it. Do not automatically run migration or add `--force`. Keep separate OS/container identities where confidentiality requires a kernel boundary. |
| Upstream documentation conflict | The current Telegram page still recommends one gateway per profile, while the dedicated multi-profile guide and current gateway guard implement multiplexing. | Cite the dedicated topology guide and exact installed `gateway --help`/runtime behavior. Do not copy the Telegram lifecycle example unqualified. |
| Distribution manifests | All eight manifests have valid-looking names, descriptions, authors and MIT identifiers. All eight now declare Pantheon `version: 0.2.0`; they omit `hermes_requires`. | Add a Hermes requirement only after establishing the earliest runtime actually tested. Do not invent a minimum from the documentation examples. |
| Installer source layout | `scripts/install_profiles.py` correctly selects a local directory with a root `distribution.yaml` and uses supported `--alias`. Installing the monorepo root is unsupported by this manifest layout. | Retain the local per-profile installation path. For separate remotely installable distributions, publish each profile as a repository root. Do not claim GitHub subdirectory URLs work. |
| Capability configuration | Every denylist toolset name in the baseline is present in current upstream toolsets. `agent.disabled_toolsets` is recognized across CLI and gateway platforms; `gateway.bot_loop_guard` with these fields is supported. | Preserve the denylist and test the actual tools after setup. A tool enable operation can remove covered entries from the denylist; re-inspect after configuration changes. This is mutable configuration, not an authorization service. |
| Cron command syntax | All 21 scheduled routine command lines accepted current pinned upstream parser definitions: positional schedule/prompt plus `--name`, `--skill`, `--timezone`, `--deliver local`, `--paused`. The event-triggered entry with a null schedule produces no command. | Retain paused local creation. Verify semantics on installed Hermes before manually running even a canary. A paused job can still be explicitly run by an operator. |
| Cron idempotency | Pantheon's planner puts a routine ID into the Hermes job **name**, not its generated job ID. It checks only the supplied inventory; it neither queries Hermes nor writes the newly created job back into that inventory. | Export all profiles' job IDs, names and ownership/purpose mapping before every apply. After creation, record the native ID and Pantheon routine name. Do not imply repeated execution of printed commands is idempotent. |
| Native Bot coordination | Plain CLI profiles do not automatically gain native `message_agent`. Current Bot Mode requires a canonical `Bot Chat` session and a Bot-Mode-managed profile metadata marker. Current source intentionally has no generic agent-callable `send_message` in its core bundles. | Add explicit Bot Mode provisioning and acceptance instructions if native coordination is advertised. Treat `registry/groups.json` as a proposed room policy, not an imported native room configuration. Keep unsupported messaging as a reported integration gap. |
| Telegram authorization | The mention configuration matches current docs. User authorization and group authorization are distinct: `TELEGRAM_ALLOWED_USERS` applies across chat types; `TELEGRAM_GROUP_ALLOWED_USERS` is group sender access; `TELEGRAM_GROUP_ALLOWED_CHATS` authorizes every member of a listed group. | Document sender-versus-chat semantics explicitly and test unauthorized DMs, out-of-scope groups, explicit mentions of another bot, and wildcard/guest-mode absence. Do not use a group chat ID as a new sender allowlist entry. |
| Discord authorization | Current docs support user/role/channel scoping and require Message Content Intent; usernames or role allowlists also require Server Members Intent. Role authorization uses OR semantics with users and can authorize DMs via mutual guild roles. | Prefer numeric IDs and platform channel permissions. Test role holders' DM access and unauthorized channels. Avoid claiming the agent role registry itself enforces Discord policy. |
| Signal | The daemon command and `SIGNAL_HTTP_URL`, `SIGNAL_ACCOUNT`, `SIGNAL_ALLOWED_USERS` settings match current docs. Group control uses `SIGNAL_GROUP_ALLOWED_USERS`; omit it to keep groups disabled. | Include the exact group and home-channel settings in the operator checklist. A separate Signal profile/provider/host remains necessary for stronger separation from Telegram memory; transport encryption does not separate shared profile state. |
| Obsidian and adapters | No Obsidian write adapter, task dispatch service, authorization broker, or external routine store is supplied; repo docs correctly identify these as integration work. | Preserve that boundary. Do not claim vault compatibility, live approval enforcement, or operational deduplication was tested without the actual private environment. |

Current distribution source accepts a single version comparison such as `>=X.Y.Z` or `==X.Y.Z`; do not assume a compound range is supported. Manifest `config.yaml` updates are preserved by default, so shipping a stricter baseline does not prove existing installations adopted it. Local-directory distributions remember a local source path; they are not automatically tied to a later public GitHub release.

For the two self-improvement cron routines, `--catch-up off --grace-minutes 0` is accepted and reaches persisted scheduler fields. Current upstream still allows a 120-second ticker tolerance before treating a recurring occurrence as missed; these flags suppress catch-up beyond that tolerance. They do not prohibit an operator's explicit Run now action. This behavior was traced through the pinned cron parser, CLI argument forwarding, job persistence and missed-run policy; it was not exercised in a live scheduler.

## Verification performed

- Retrieved authoritative NousResearch documentation and upstream source; inspected profile manifests/configs, installer, planner, routine registry and deployment/security/release instructions.
- Ran a parser-only harness against `hermes_cli/subcommands/{cron,profile,tools}.py` fetched at the captured revision. All 21 generated cron commands, eight per-profile local install commands and `tools list` parsed successfully. The harness stubbed the parser's hook-flag registration and did not load the Hermes runtime.
- Checked baseline denylist names against current `toolsets.py`. Checked bot loop guard keys against `hermes_cli/config_defaults.py` and Bot Mode documentation.
- Confirmed the current gateway source contains the named-profile startup/install guard and explicit temporary standalone handling.
- Verified missed-slot policy in pinned `cron/jobs.py` and `cron/missed_runs.py`, including preservation of boolean false and zero-valued grace settings.

These checks establish command grammar and source correspondence only. They do not validate model credentials, package dependencies, platform ingress, effective runtime tool discovery, scheduler delivery, live room behavior, existing profile migration or private data access.

## Installed-environment acceptance still required

A trusted operator must capture the installed version and revision privately, inspect `hermes --help`, `hermes profile install --help`, `hermes gateway --help` and `hermes cron create --help`, and inventory profiles, services, credentials ownership and all existing schedules. Use a disposable profile/environment for an install and inspect effective tools for CLI, cron and every exposed gateway platform. Perform positive and negative ingress tests, profile-memory separation checks, one paused local canary and restart/stop checks before any rollout. Do not attach credentials, full configuration dumps, private job prompts or vault records to public compatibility evidence.

## Authoritative sources

Documentation was retrieved on the review date. These are durable source URLs; current website pages may change after review.

| Source | Exact URL |
|---|---|
| Latest release | https://github.com/NousResearch/hermes-agent/releases/tag/v0.23.1 |
| Profile distributions | https://hermes-agent.nousresearch.com/docs/user-guide/profile-distributions |
| Profiles | https://hermes-agent.nousresearch.com/docs/user-guide/profiles |
| Configuration | https://hermes-agent.nousresearch.com/docs/user-guide/configuration |
| Toolsets | https://hermes-agent.nousresearch.com/docs/reference/toolsets-reference |
| Cron | https://hermes-agent.nousresearch.com/docs/user-guide/features/cron |
| Gateway topology | https://hermes-agent.nousresearch.com/docs/user-guide/multi-profile-gateways |
| Telegram | https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram |
| Discord | https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord |
| Signal | https://hermes-agent.nousresearch.com/docs/user-guide/messaging/signal |
| Bot Mode | https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode |
| Cron parser (web view) | https://github.com/NousResearch/hermes-agent/blob/main/hermes_cli/subcommands/cron.py |

Direct upstream source inspection supplied these files: `hermes_cli/profile_distribution.py`, `hermes_cli/gateway.py`, `hermes_cli/config_defaults.py`, `toolsets.py`; all inspected source file contents were verified against the captured revision. Immutable source links:

- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/hermes_cli/profile_distribution.py
- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/hermes_cli/gateway.py
- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/hermes_cli/config_defaults.py
- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/toolsets.py
- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/hermes_cli/subcommands/cron.py
- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/hermes_cli/subcommands/profile.py
- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/hermes_cli/subcommands/tools.py
- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/hermes_cli/cron.py
- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/cron/jobs.py
- https://github.com/NousResearch/hermes-agent/blob/652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab/cron/missed_runs.py
