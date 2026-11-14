# Release and publication

This repository is a monorepo of eight native profile distributions. Upstream `hermes profile install` expects a distribution manifest at the root of the selected source. Install locally from `profiles/<agent>` after cloning; do not point it at the monorepo root. To publish an individually remotely installable distribution, copy the reviewed profile directory into its own Git repository (or a dedicated distribution branch/repository), including its LICENSE, and use the upstream documented git install/update mechanism. Do not promise subdirectory URL support.

Before publication:

1. Confirm project name and copyright owner; MIT is the proposed license. Review third-party terms and branding. This is independent of Nous Research; no upstream source code or imagery is bundled.
2. Run `python scripts/validate.py` and `python -m unittest discover -s tests -v`.
3. Review every staged file for secrets, identifiers, private vaults, chat exports and keys. Verify `.gitignore`; upstream installers cannot protect your public git history.
4. Test native installation from a disposable Hermes environment. Verify effective tools and model setup, then test live gateways and paused routines before claiming compatibility.
5. Enable private vulnerability reporting, branch protection and CI. Publish as v0.1.0 technical preview, not production-ready.

```bash
git init -b main
git add .
git diff --cached --stat
git diff --cached
git commit -m "Initial Pantheon technical preview"
git tag v0.1.0
# Create a repository with your chosen owner/name, then:
git remote add origin <YOUR_REPOSITORY_URL>
git push -u origin main --tags
```

No GitHub repository has been created or published by this package. Keep actual profiles and operational records outside the public repository.
