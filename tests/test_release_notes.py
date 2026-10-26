import subprocess
from unittest.mock import patch

import pytest

from scripts import release_notes as rn

TAGS = ["v0.2.0", "v0.1.10", "v0.1.9", "v0.1.0"]  # as `git tag --sort=-v:refname` returns them


def _tag_exists(returncode):
    return patch.object(rn.subprocess, "run",
                        return_value=subprocess.CompletedProcess([], returncode))


@pytest.mark.parametrize(
    "items, expected",
    [
        ([("fix: a", ""), ("docs: b", "")], "v0.2.1"),
        ([("feat(x): a", ""), ("fix: b", "")], "v0.3.0"),
        ([("feat!: drop thing", "")], "v0.3.0"),                 # breaking stays minor below 1.0
        ([("fix: a", "BREAKING CHANGE: moved")], "v0.3.0"),
    ],
)
def test_next_version_bumps_pre_1_0(items, expected):
    with patch.object(rn, "tags", return_value=TAGS), patch.object(rn, "commits", return_value=items):
        assert rn.next_version() == expected


def test_next_version_breaking_bumps_major_after_1_0():
    with patch.object(rn, "tags", return_value=["v1.4.2"]), \
         patch.object(rn, "commits", return_value=[("feat!: new config", "")]):
        assert rn.next_version() == "v2.0.0"


def test_next_version_first_release():
    with patch.object(rn, "tags", return_value=[]):
        assert rn.next_version() == "v0.1.0"


def test_next_version_refuses_empty_release():
    with patch.object(rn, "tags", return_value=TAGS), patch.object(rn, "commits", return_value=[]):
        with pytest.raises(SystemExit):
            rn.next_version()


def test_notes_group_by_type_and_link_previous_tag():
    items = [("docs: explain tags", ""), ("fix(email): escape html", ""), ("feat(rules): add z-score", "")]
    with patch.object(rn, "tags", return_value=TAGS), \
         patch.object(rn, "commits", return_value=items) as commits, _tag_exists(0):
        out = rn.notes("v0.2.0")
    commits.assert_called_once_with("v0.1.10..v0.2.0")  # numeric, not lexical, previous tag
    assert out.index("## ✨ Features") < out.index("## 🐛 Bug Fixes") < out.index("## 📝 Documentation")
    assert "- **rules:** Add z-score" in out
    assert "docker pull dwightmulcahy/logwatcher:0.2.0" in out
    assert "compare/v0.1.10...v0.2.0" in out


def test_notes_mark_breaking_and_keep_unknown_types():
    items = [("feat!: replace config", ""), ("fix: x", "BREAKING CHANGE: path moved"), ("Merge stuff", "")]
    with patch.object(rn, "tags", return_value=TAGS), patch.object(rn, "commits", return_value=items), _tag_exists(0):
        out = rn.notes("v0.2.0")
    assert "**BREAKING:** Replace config" in out
    assert "**BREAKING:** X" in out
    assert "## 📦 Other Changes" in out


def test_notes_for_prerelease_use_previous_stable_and_head_when_untagged():
    with patch.object(rn, "tags", return_value=TAGS), \
         patch.object(rn, "commits", return_value=[("fix: y", "")]) as commits, _tag_exists(1):
        rn.notes("v0.2.0-rc.1")
    commits.assert_called_once_with("v0.1.10..HEAD")


def test_notes_reject_non_version():
    with pytest.raises(SystemExit):
        rn.notes("latest")
