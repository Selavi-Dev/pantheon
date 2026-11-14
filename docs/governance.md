# Governance ledger (local reference)

Run with Python 3.10+. The SQLite ledger stores immutable proposal JSON and SHA-256 digest, unique handoff ID and semantic idempotency key. It supports `propose`, `show`, `approve`, `revoke`, `claim`, `complete`, and `verify`. Each mutation uses a transaction. Exact proposal replay is idempotent; the same ID or key with different content is rejected. Approval is scoped to the digest and expiration; a claim is atomic and single-use. Verification requires evidence and a reviewer distinct from the claimant and proposal author.

```bash
python -m pantheon.ledger --db .local/ledger.sqlite propose examples/handoff.json
python -m pantheon.ledger --db .local/ledger.sqlite show PTH-HO-0001
# Replace DIGEST with the returned digest.
python -m pantheon.ledger --db .local/ledger.sqlite approve PTH-HO-0001 --digest DIGEST --actor operator --ttl 3600
python -m pantheon.ledger --db .local/ledger.sqlite claim PTH-HO-0001 --actor grokbot
# After external execution and receipt reconciliation, if actually performed:
python -m pantheon.ledger --db .local/ledger.sqlite complete PTH-HO-0001 --actor grokbot --evidence 'artifact:example-only'
python -m pantheon.ledger --db .local/ledger.sqlite verify PTH-HO-0001 --actor themis --evidence 'audit:example-only'
```

The example evidence strings are placeholders, not valid real evidence. The ledger stores supplied evidence references but does not inspect them or authenticate actor names. It deliberately never calls external APIs or performs dispatch. `claim` means local reservation only; external execution still needs a real authorization broker, receiver authentication and dispatch receipt. Revocation before claim blocks claim. After claim, stop/reconcile externally; revocation cannot undo execution. Expired authorization cannot be claimed. Do not share write access with agents. Local database records can be altered by a privileged host operator; audit records are not tamper-proof. Integrate a real identity provider and scoped approval/dispatch service before enabling consequential actions. No automatic lease reclaim, retry, or cross-system transactional guarantees are implemented.

New SQLite databases are created with owner-only file permissions (`0600` on POSIX); the final new parent directory is requested as `0700`. Existing files and directory permissions are preserved. Operators must still audit existing state, ancestor directories, backups and platform ACLs. This is local privacy hardening, not encryption or authentication.
