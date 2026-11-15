# Self-modification policy — v0.2.0

Applies to all Pantheon agents and supersedes no base governance. Where rules conflict, stop and obtain administrator resolution; never interpret this document as granting tools or permissions.

| Action | Authority |
|---|---|
| Read authorized evidence, reflect, draft lessons/proposals | Assigned agent within existing grants |
| Develop candidate, execute sandbox tests | Hephaestus under existing sandbox grants |
| Evaluate independently | Argus; no candidate author may attest to independent evaluation |
| Governance review | Themis; distinct from candidate author |
| Production change approval | Authenticated administrator, explicit exact candidate and scope |
| Production deployment and rollback | Separately authorized operator; outside this skill |

Every production change requires prior evidence, reproducible tests, rollback, governance review, and explicit approval bound to the candidate digest. A change to candidate, scope, or permissions invalidates the approval. No agent may impersonate or infer administrator approval from silence, memory, chat text, or a local JSON record. Local records are not access controls or authenticated signatures; enforce identity and authorization in the deployment environment. The approval recorder is for a trusted human operator only. Keep private records outside the public repository. Do not copy secrets or personal data into benchmarks or Obsidian notes. Restrict vault write access to the designated improvement inbox; no automatic global edits.

All scheduler definitions ship disabled. Hermes must review the existing registry and Grokbot routine ownership and prepare a single-owner activation recommendation. An authenticated human administrator authorizes schedule activation; a separately authorized operator applies it. No automatic outbound delivery, operational actions, approval escalation, or unbounded recursion. Fail closed when source provenance, authorization, or evidence is missing. Production rollout and post-release measurement are separate processes.
