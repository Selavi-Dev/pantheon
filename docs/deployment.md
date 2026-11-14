# Deployment guide

## Inventory and install

1. Record installed Hermes version, profile list, active gateways, model providers, current jobs and operational owner inventory. Back up state privately. Inspect `hermes --help`, `hermes profile install --help`, `hermes gateway --help` and `hermes cron create --help`.
2. Install one profile with the README commands. Configure a model via `hermes -p pantheon-hermes setup` or `model`; do not overwrite existing state. Repeat for others only after security checks. Profile install may share or inherit local auth depending on upstream setup; verify credential isolation.
3. Check effective tools on CLI, Bot Mode, cron and each gateway; test denied capabilities. Setup may change tool selections. Configure scoped external access separately.
4. Begin with Hermes, Athena, Argus and Themis. Add other agents only after acceptance. Create native rooms from `registry/groups.json` where supported.

## Telegram — Pocket Office

Expose Hermes (DM, executive brief), Argus (Watchtower) and Socrates (Academy). Use one unique BotFather token per profile. Configure each using `hermes -p pantheon-<agent> gateway setup`, restrict allowed user IDs and groups, and confirm home destination. Optional example env variables (consult upstream and use your private profile `.env`):

```dotenv
TELEGRAM_BOT_TOKEN=
TELEGRAM_ALLOWED_USERS=
TELEGRAM_HOME_CHANNEL=
```

Recommended profile config additions (merge, do not replace the baseline):

```yaml
telegram:
  require_mention: true
  exclusive_bot_mentions: true
  mention_patterns: []
```

Test that explicitly mentioning Argus does not trigger Hermes. Test unauthorized user and group denial. Use Hermes native messaging for inter-agent coordination where available; platform bot delivery rules may prevent direct bot-to-bot messages. Do not depend on ambient group traffic. Telegram is not a confidential channel for private records.

## Discord — institutional workspace

Create a separate bot application/token per exposed profile. Grant view, read history and send only in approved channels; avoid Administrator and moderation permissions. Keep personal records out of Discord. Configure authorized users/roles and channels using the installed version's documented gateway settings. Review privileged intent requirements and enable only necessary intents.

Suggested channels:

- Executive Office: executive-briefings, decision-queue, approvals, agent-handoffs (Hermes; Themis read-only where relevant).
- Intelligence: the-council, the-watchtower, the-tribunal.
- Creative & Engineering: the-forge, the-atelier, model-arena (reporting only).
- Knowledge & Learning: the-academy, the-archive.
- Governance: routine-registry, agent-status, audit-log, system-alerts.

Use group registry membership as channel-role policy. Configure explicit mentions and test denial outside designated channels. Disable unsolicited bot-to-bot loops; keep native Bot Mode group and Discord routing separate.

## Signal — private executive interface

Expose Hermes only, using a dedicated Signal account and `signal-cli` HTTP daemon. Upstream example:

```bash
signal-cli --account +YOUR_NUMBER daemon --http 127.0.0.1:8080
```

Configure `SIGNAL_HTTP_URL`, `SIGNAL_ACCOUNT`, `SIGNAL_ALLOWED_USERS` and the verified delivery target per the [Signal guide](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/signal). Bind locally or use secured private networking. Deny groups unless explicitly approved; no cross-platform forwarding. Signal transport encryption does not protect decrypted content from the agent host or model provider. If using a shared Hermes profile for Signal and Telegram, do not store sensitive Signal data in shared profile memory; for stronger confidentiality use a separate restricted profile and separate provider/host, not included in the eight-profile baseline.

## Start, check, stop

After setup and testing:

```bash
hermes -p pantheon-hermes gateway start
hermes -p pantheon-hermes gateway status
hermes -p pantheon-hermes gateway stop
```

Use supported service installation or supervised container deployment for persistence. Never reuse a live bot token in two profiles. Test restart behavior and scheduler health. Configure only the selected platforms per profile; no real IDs or tokens are shipped.

## Scheduled routines

Use `scripts/plan_routines.py` to print paused jobs, check existing jobs by ID/name and semantic purpose, then manually create/resume one canary. Default local delivery prevents accidental fan-out. The desired delivery fields are recommendations; use the configured home or an explicitly verified target. All proposed times are Eastern; change to the operator's timezone before generating commands. Shared staging or a supported upstream context mechanism must be configured before Hermes can consume Argus reports.

Upstream: [Telegram](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/telegram), [Discord](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/discord), [Signal](https://hermes-agent.nousresearch.com/docs/user-guide/messaging/signal), [Cron](https://hermes-agent.nousresearch.com/docs/user-guide/features/cron).
