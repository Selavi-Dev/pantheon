# Security policy

This is a technical preview. Report security vulnerabilities privately to the repository maintainers using GitHub private vulnerability reporting if enabled. Do not post secrets, private logs or exploit details in public issues. Until a maintainer configures a disclosure contact, avoid sharing confidential details in issues.

Profile separation is not an OS sandbox. SOUL and skills are instructions, not enforcement. The starter config disables many high-risk toolsets, but actual effective permissions depend on upstream version, local configuration, connectors and credentials. Never connect write-capable credentials or mount private vaults by default. The local ledger trusts the local operating-system operator; it does not authenticate mobile users, implement external dispatch or protect against a compromised host. See docs/security.md.
