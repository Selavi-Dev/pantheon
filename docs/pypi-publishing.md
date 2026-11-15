# PyPI publishing

Status: prepared, not performed. Nothing has been uploaded. `pantheon-agent` was unclaimed on PyPI when checked on 2026-11-14; the plain name `pantheon` belongs to an unrelated project. Package names and released versions on PyPI are permanent: a deleted version can never be re-uploaded.

## One-time setup (owner)

1. Confirm the public GitHub repository (owner and slug). Then add to `pyproject.toml`:

   ```toml
   [project.urls]
   Homepage = "https://github.com/<owner>/<repo>"
   Source = "https://github.com/<owner>/<repo>"
   Issues = "https://github.com/<owner>/<repo>/issues"
   Changelog = "https://github.com/<owner>/<repo>/blob/main/CHANGELOG.md"
   ```
2. On pypi.org, under the publishing account, add a **pending trusted publisher** for project `pantheon-agent`: owner `<owner>`, repository `<repo>`, workflow `publish.yml`, environment `pypi`. This does **not** reserve the name: PyPI only claims it on the first successful upload, and the pending publisher is invalidated if someone else registers `pantheon-agent` first ([PyPI docs](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/)). The only way to hold the name is to publish a release.
3. In the GitHub repository, create environment `pypi` with required reviewers (at least the owner) and restrict it to release tags.
4. Optional rehearsal: repeat steps 2–3 on test.pypi.org with environment `testpypi`, and point a copy of the workflow at `repository-url: https://test.pypi.org/legacy/`.

## Each release

1. Merge the reviewed branch; CI must pass on Linux, macOS and Windows.
2. Run the build-only **Build release candidates** workflow; review its artifacts, `pip-audit` output and SBOM.
3. Tag `vX.Y.Z` matching `pyproject.toml` and publish a GitHub release with the wheel, sdist, profile archives and SHA256SUMS.
4. Approve the `pypi` environment deployment. `publish.yml` rebuilds, re-verifies, refuses a tag/version mismatch, uploads via OIDC (no stored token) and publishes PEP 740 attestations.

The README is used as the PyPI description; its relative `docs/` links only resolve on GitHub. Replace them with absolute links once the repository URL is known.
