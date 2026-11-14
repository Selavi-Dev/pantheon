# Systems of record and integrations

## Obsidian

Preserve existing vault organization. Add a namespace such as `Pantheon/` with `Governance`, `Executive/Decisions`, `Executive/Commitments`, `Intelligence`, `Engineering`, `Creative`, `Academy`, `Audit`, and `Inbox/<agent>`. Do not mount the complete personal vault to every profile. Keep personal and confidential work in a separate restricted vault or access-controlled service. Use stable IDs, classification, source dates, status and related links. See `schemas/knowledge.schema.json` and `examples/knowledge.json`.

Agents submit a proposed record through a controlled API or operator-managed file exchange; Mnemosyne reconciles duplicates, verifies provenance and requests review before promotion. Preserve historical revisions and dissent. Themis audits evidence; authors must not approve their own high-risk work. No Obsidian write adapter is implemented in this starter kit.

Systems of record: Linear for work orders, GitHub for code and releases, Drive for formal documents, Gmail for original messages, Notion for designated structured registers, Obsidian for durable knowledge and decision history. Link canonical IDs rather than maintaining independently writable copies of tasks.

## Grokbot / operations agent

The operations agent owns operational execution, workflow monitoring, marketing execution and routine business reports. Pantheon consumes outputs and escalates exceptions. Athena owns strategy; Argus public discovery; Hephaestus architecture; Apollo creative concepts; Themis independent review; Mnemosyne knowledge; Socrates learning. The shared contract is in `governance/GROKBOT_CONTRACT.md`.

Adapter design:

1. Inventory all existing schedules, work orders and owners; normalize semantic purpose keys. `scripts/plan_routines.py` detects equal active purpose keys, not fuzzy equivalence.
2. Receive attributed reports with source ID, event and retrieval time, evidence, status, classification and owner. Validate schema and freshness; never reinterpret an agent report as authorization.
3. Propose a handoff with immutable ID and key. Trusted human approves the exact digest. Claim once; dispatch with the same idempotency key in the downstream system.
4. Persist receipt and reconcile uncertain delivery rather than blindly retrying. Record completion claim separately from evidence-backed verification. Escalate conflicts, stale input and ownership ambiguity.

No live Grokbot API is assumed or supplied. The local reference ledger demonstrates a subset of this contract; the dispatch adapter, authentication and shared routine store must be implemented for your deployment. Do not create a new operational routine solely because the agent can generate one.
