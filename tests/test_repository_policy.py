import pathlib
import re

ROOT = pathlib.Path(__file__).parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"


def _read(path):
    return path.read_text(encoding="utf-8")


def test_external_actions_are_pinned_to_commit_shas():
    for path in WORKFLOWS.glob("*.yml"):
        for reference in re.findall(r"uses:\s+([^\s#]+)", _read(path)):
            if reference.startswith("./"):
                continue
            assert re.fullmatch(r"[^@]+@[0-9a-f]{40}", reference), (
                f"{path.name}: mutable action reference {reference}"
            )


def test_base_images_are_versioned_and_digest_pinned():
    images = re.findall(r"^FROM\s+(\S+)", _read(ROOT / "Dockerfile"), re.MULTILINE)
    assert images
    for image in images:
        assert re.fullmatch(r"[^:]+:\d+\.\d+\.\d+[^@]*@sha256:[0-9a-f]{64}", image), image


def test_ci_python_matches_base_image():
    image = re.search(r"^FROM\s+python:(\d+\.\d+)", _read(ROOT / "Dockerfile"), re.MULTILINE)
    ci = re.search(r'PYTHON_VERSION:\s*"(\d+\.\d+)"', _read(WORKFLOWS / "ci.yml"))
    assert image and ci and image.group(1) == ci.group(1)


def test_ci_scans_the_built_image():
    workflow = _read(WORKFLOWS / "ci.yml")
    assert "aquasecurity/trivy-action@" in workflow
    assert "severity: CRITICAL,HIGH" in workflow
    assert 'exit-code: "1"' in workflow


def test_release_reuses_ci_and_guards_main():
    workflow = _read(WORKFLOWS / "release.yml")
    assert "uses: ./.github/workflows/ci.yml" in workflow
    assert "git merge-base --is-ancestor" in workflow
    assert "provenance: mode=max" in workflow
    assert "sbom: true" in workflow
    for flag in ("is_latest", "is_major", "is_minor"):
        assert f"enable=${{{{ needs.prepare.outputs.{flag} }}}}" in workflow


def test_dockerignore_is_an_allowlist():
    lines = [line for line in _read(ROOT / ".dockerignore").splitlines() if line.strip()]
    assert lines[0] == "*"
    assert all(line.startswith("!") for line in lines[1:])
