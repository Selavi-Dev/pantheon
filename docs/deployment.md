# Deployment guide

Compatibility was reviewed against current upstream documentation on 2026-11-13 America/New_York (2026-11-14 UTC) and source revision `652c0c9cd06bd8706d14d60ddfb69cc66ccdd8ab`; the latest release observed was v0.23.1. The installed Hermes version is unavailable in this workspace. This is a source review, not a live deployment test. See [the compatibility report](HERMES_COMPATIBILITY.md) for evidence and limits.

## Inventory and install

1. Record installed Hermes version, profile list, active gateways, model providers, current jobs and operational owner inventory. Back up state privately. Inspect `hermes --help`, `hermes profile install --help`, `hermes gateway --help` and `hermes cron create --help`.
2. Install one profile with the README commands. Configure a model via `hermes -p pantheon-hermes setup` or `model`; do not overwrite existing state. Repeat for others only after security checks. Profile install may share or inherit local auth depending on upstream setup; verify credential isolation.
3. Check effective tools on CLI, Bot Mode, cron and each gateway; test denied capabilities. Setup may change tool selections. Configure scoped external access separately.
4. Begin with Hermes, Athena, Argus and Themis. Add other agents only after acceptance. Provision native rooms using `registry/groups.json` as a policy reference; it is not a native import file. Plain profiles do not automatically have Bot Mode messaging: provision canonical Bot Chats and Bot Mode metadata through supported installed-version setup, then test actual delivery. See [Bot Mode](https://hermes-agent.nousresearch.com/docs/user-guide/bot-mode).

## Telegram — Pocket Office

Expose Hermes (DM, executive brief), Argus (Watchtower) and Socrates (Academy). Use one unique BotFather token per profile. Configure each using `hermes -p pantheon-<agent> gateway setup`, restrict allowed user IDs and groups, and confirm home destination. Optional example env variables (consult upstream and use your private profile `.env`):

```dotenv
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USERS=
TELEGRAM_GROUP_ALLOWED_USERS=
TELEGRAM_GROUP_ALLOWED_CHATS=
TELEGRAM_HOME_CHANNEL=
```

`TELEGRAM_ALLOWED_USERS` grants sender access across chat types. `TELEGRAM_GROUP_ALLOWED_USERS` grants sender access in groups only. `TELEGRAM_GROUP_ALLOWED_CHATS` authorizes every member of each listed group. Choose the intended policy; a group ID is not a sender ID. Keep guest mode and wildcard access disabled unless deliberately approved.

Recommended profile config additions (merge, do not replace the baseline):

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns: []
```

Test that explicitly mentioning Argus does not trigger Hermes. Test unauthorized user and group denial. Use Hermes native messaging for inter-agent coordination where available; platform bot delivery rules may prevent direct bot-to-bot messages. Do not depend on ambient group traffic. Telegram is not a confidential channel for private records.

## Discord — institutional workspace

Create a separate bot application/token per exposed profile. Grant view, read history and send only in approved channels; avoid Administrator and moderation permissions. Keep personal records out of Discord. Configure authorized users/roles and channels using the installed version's documented gateway settings. Current Hermes requires Message Content Intent; usernames or role allowlists also require Server Members Intent. Prefer numeric user IDs. User and role authorization are alternatives (OR); an allowed role in a mutual guild can also authorize DMs. Test that consequence explicitly.

Suggested channels:

- Executive Office: executive-briefings, decision-queue, approvals, agent-handoffs (Hermes; Themis read-only where relevant).
- Intelligence: the-council, the-watchtower, the-tribunal.
- Creative & Engineering: the-forge, the-atelier, model-arena (reporting only).
- Knowledge & Learning: the-academy, the-archive.
- Governance: routine-registry, agent-status, audit-log, system-alerts.

Translate group registry membership into actual platform channel permissions and gateway policy. Configure explicit mentions and test denial outside designated channels. Disable unsolicited bot-to-bot loops; keep native Bot Mode group and Discord routing separate.

## Signal — private executive interface

Expose Hermes only, using a dedicated Signal account and `signal-cli` HTTP daemon. Upstream example:

```bash
signal-cli --account +YOUR_NUMBER daemon --http 127.0.0.1:8080
```

Configure `SIGNAL_HTTP_URL`, `SIGNAL_ACCOUNT`, `SIGNAL_ALLOWED_USERS` and `SIGNAL_HOME_CHANNEL` with the verified delivery target per the [Signal guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/signal). Bind locally or use secured private networking. Omit `SIGNAL_GROUP_ALLOWED_USERS` to disable groups; use explicit group IDs only after approval. No cross-platform forwarding. Signal transport encryption does not protect decrypted content from the agent host or model provider. If using a shared Hermes profile for Signal and Telegram, do not store sensitive Signal data in shared profile memory; for stronger confidentiality use a separate restricted profile and separate provider/host, not included in the eight-profile baseline.

## Start, check, stop

Inventory existing gateway processes and services before startup. Current upstream defaults to one host gateway serving named profiles. After setup and testing, start/check the host from its default profile:

```bash
hermes -p default gateway start
hermes -p default gateway status
```

On a running multiplexer, `hermes -p pantheon-hermes gateway stop` parks that profile and `gateway start` unparks it; stopping the host affects its served profiles. A new named-profile standalone gateway may be refused with exit 78. Do not add `--force` or migrate an existing fleet automatically. Separate OS users or independent containers may be intentional confidentiality boundaries. Follow the installed version and [dedicated gateway topology guide](https://hermes-agent.nousresearch.com/docs/user-guide/multi-profile-gateways); the current Telegram page still includes older per-profile startup advice.

Use supported service installation or supervised container deployment for persistence. Never reuse a live bot token in two profiles. Verify which profiles the host actually serves, restart behavior, scheduler health and shared restart impact. Configure only the selected platforms per profile; no real IDs or tokens are shipped.

## Scheduled routines

Use `scripts/plan_routines.py` to print paused jobs, check existing jobs by ID/name and semantic purpose, then manually create/resume one canary. The planner puts the Pantheon routine ID in the job name; Hermes generates its own native job ID. Record both after creation and refresh the private inventory before every apply. Re-running printed create commands is not idempotent. Current upstream parser syntax accepts `--paused`, `--timezone` and `--skill`; verify the installed help before use. Pausing does not block an operator's explicit Run now action.

Default local delivery prevents accidental fan-out. The desired delivery fields are recommendations; use the configured home or an explicitly verified target. All proposed times are Eastern; change to the operator's timezone before generating commands. Shared staging or a supported upstream context mechanism must be configured before Hermes can consume Argus reports.

Upstream: [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram), [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Signal](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/signal), [Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron).
