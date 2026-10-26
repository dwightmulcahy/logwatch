# logwatcher

- Commit directly to `main` and push. No branches or pull requests.
- Commit messages: Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`, `ci:` ...). They drive release notes (`scripts/release_notes.py`); version tags are created manually.
- Keep `README.md` settings tables in sync with the `os.getenv` defaults in `logwatch.py`.
- Releases: `.github/workflows/release.yml` (manually pushed `v*.*.*` tag) builds/pushes `dwightmulcahy/logwatcher` and creates the GitHub Release.
- Before committing: `python -m pyflakes logwatch.py scripts/release_notes.py`.
