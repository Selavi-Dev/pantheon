# Security and capability policy

## Default posture

All profiles ship with no credentials, MCP servers or schedules. High-risk built-in toolsets (shell, file, browser, code execution, cron management, computer use, Discord actions/admin, connectors, catalog, Kanban and delegation) are disabled in the baseline. Image generation is disabled except for Apollo. These are denylist defaults, not a complete allowlist or security boundary. Hermes version changes can add capabilities; verify effective tools with `hermes -p pantheon-<agent> tools list` and negative tests. The native skills toolset may modify local skill state; canonical repo changes require operator review. Web and memory may contain private information; scope access and retention. Native messaging availability depends on session and upstream configuration.

Profiles are not security sandboxes. `agent.disabled_toolsets` removes configured tool capabilities, but it does not isolate the operating system or authenticate approval. Current upstream tool-enable flows can remove covered denylist entries; inspect configuration and effective tools again after setup, enabling tools or upgrades. Distribution updates normally preserve existing `config.yaml`, so a new published baseline does not prove old installations adopted it. See [compatibility evidence and remaining runtime checks](HERMES_COMPATIBILITY.md).

## Intended capability matrix (requires integration)

| Agent | Authorized input | Output | Prohibited / gated |
|---|---|---|---|
| Hermes | Scoped agenda, correspondence, operational reports, project records | Briefs, proposed decisions, drafts | Send, calendar/Linear writes and dispatch gated |
| Athena | Public and scoped strategy records | Decision memo | No transactions or execution |
| Argus | Public research | Intelligence staging | No surveillance, internal operational duplication |
| Themis | Read-only evidence and audits | Append-only audit proposals | No evidence edits, no self-audit |
| Hephaestus | Read-only specs and repo evidence | Architecture, isolated prototypes after approval | No production writes, no default shell |
| Apollo | Approved brand records | Creative drafts | No publishing |
| Mnemosyne | Scoped knowledge sources | Reviewed record promotions | No deletion, unrestricted vault access or silent overwrites |
| Socrates | Approved learning material | Exercises and feedback | No private administrative access |

For every integration use a service identity with least-privilege credentials, server-side object scoping, read-only APIs where possible and explicit tool allowlists. Do not expose generic shell, API request, SQL or browser tools as substitutes for narrowly scoped APIs. Do not grant agents database write access or authenticated approval credentials.

## Defense in depth

- OS users or containers: each execution identity receives only its mounted workspace; no host home, Docker socket, production SSH keys or vault secrets. A working directory is not a sandbox.
- Gateway topology: multiplexed profiles share one process. Preserve separate host/container or OS-user boundaries when needed for confidential data; per-profile state separation does not replace them.
- Provider data policy: verify retention, logging and processing for each model. Do not send confidential data to unapproved providers. Signal is not end-to-end encrypted through the model pipeline.
- Gateway allowlists: numeric user IDs, restricted channels, separate credentials, no admin bot roles, no untrusted bot commands. Apply least privilege even if a gateway is misconfigured.
- Approval boundary: authenticated human, immutable proposal digest, recipient, scope, expiry, revocation, single claim. Never infer approval from plain chat or agent output.
- Prompt injection: external messages, files and websites are untrusted. Credentials must remain outside agent context. Review allowed network destinations and connectors.
- Audit and recovery: log attempts and evidence without secrets. A claimed or interrupted external action is not safe to retry automatically; reconcile actual state first.

The sample local ledger assumes a trusted operator and local database owner; it has no authentication, encryption, network isolation or dispatch. A production broker needs authenticated request handling, scoped credentials, durable outbox/receipt reconciliation, and independent reviewer access. See docs/governance.md.
