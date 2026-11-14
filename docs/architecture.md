# Architecture

Pantheon is a control plane, not a second execution engine. Human authority owns consequential decisions. Hermes routes administrative work; Grokbot or another operations agent owns recurring operational execution. Engineering agents implement. Themis verifies independently; Mnemosyne maintains institutional knowledge.

## Institutions

| Group | Lead | Members | Artifact |
|---|---|---|---|
| Council | Athena | Hermes, Athena, Argus, Themis | Decision memo |
| Forge | Hephaestus | Hephaestus, Athena, Apollo, Themis | Design specification |
| Watchtower | Argus | Argus, Athena, Hermes | Intelligence brief |
| Atelier | Apollo | Apollo, Athena, Hephaestus | Creative directions |
| Academy | Socrates | Socrates, Athena, Hephaestus, Mnemosyne | Learning exercise |
| Archive | Mnemosyne | Mnemosyne, Argus, Themis | Provenance-backed records |
| Tribunal | Themis | Themis, Socrates, Hephaestus | Independent audit |

Create rooms in supported Hermes Bot Mode versions; `registry/groups.json` is a custom design registry, not an upstream import. Set lead routing; one review round is the starting policy, not a runtime guarantee. Frame → independent findings → challenge → synthesis → close/escalate. Recuse anyone who authored the work from independent grading. If the native room lacks a feature, run separate sessions and consolidate manually. Do not treat Discord or Telegram groups as equivalent to Bot Mode rooms.

## Model routing

See registry/model-routing.md. Profile-specific providers, no automatic tier switching. Separate audit models/providers where practical. For model benchmarking, run competitors in isolated sessions with identical tasks, pinned models, identical tool policy and hidden peer results until submission. Record harness version, token/cost data, elapsed time, artifacts and rubric. Themis independently grades; Mnemosyne preserves results. No benchmark harness is shipped.

## Runtime boundaries

Native Hermes: profiles, SOUL, skills, selected tool configuration, gateways, cron, supported Bot Mode rooms and profile distributions. Custom: routine ownership, semantic deduplication, Obsidian staging, mobile approval broker, Grokbot adapters, and cross-platform session continuity. The reference ledger is local only. Do not conflate profile isolation with process isolation.
