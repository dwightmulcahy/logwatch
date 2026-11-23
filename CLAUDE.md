# logwatcher

- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `ci:` ...). They drive version bumps and release notes (`scripts/release_notes.py`).
- Keep `README.md` settings tables in sync with the `os.getenv` defaults in `logwatch.py`.
- Releases: `.github/workflows/release.yml` (manual run or `v*.*.*` tag) builds/pushes `dwightmulcahy/logwatcher` and creates the GitHub Release.
- Before committing: `ruff check . && pyflakes logwatch.py scripts tests && python -m pytest -q` (deps: `requirements-dev.txt`).
- Pin new actions to commit SHAs and the base image to version + digest; `tests/test_repository_policy.py` enforces it. Keep `PYTHON_VERSION` in `ci.yml` equal to the Dockerfile's Python minor.

## Git workflow (applies to every change)

1. **One PR per change.** Every change goes through its own pull request and is merged only after CI passes. If CI fails, keep fixing it on the same branch until it is green.
2. **Merge order.** When several PRs are open, merge them in a deliberate order (dependencies first), rebasing each onto the updated default branch before merging.
3. **Conventional Commits.** Commit messages and PR titles use `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `build:`, `refactor:`, `chore:` … (release notes and version bumps are built from them).
4. **No direct commits to the default branch.** It only changes by merging or rebasing PRs.
