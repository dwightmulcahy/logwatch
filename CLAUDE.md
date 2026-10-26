# logwatcher

- Commit directly to `main` and push. No branches or pull requests.
- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `ci:` ...). They drive version bumps and release notes (`scripts/release_notes.py`).
- Keep `README.md` settings tables in sync with the `os.getenv` defaults in `logwatch.py`.
- Releases: `.github/workflows/release.yml` (manual run or `v*.*.*` tag) builds/pushes `dwightmulcahy/logwatcher` and creates the GitHub Release.
- Before committing: `ruff check . && pyflakes logwatch.py scripts tests && python -m pytest -q` (deps: `requirements-dev.txt`).
- Pin new actions to commit SHAs and the base image to version + digest; `tests/test_repository_policy.py` enforces it. Keep `PYTHON_VERSION` in `ci.yml` equal to the Dockerfile's Python minor.
