#
# Copyright 2026 ABSA Group Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Tests for tests/examples/normalize_snapshot.py — the snapshot normalizer.

Run: ``python -m pytest tests/examples/test_normalize_snapshot.py`` (needs pytest only).
Every case normalizes an artifact built here, so nothing here goes online.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from normalize_snapshot import _normalize

COMMIT = "0123456789abcdef0123456789abcdef01234567"
BLOB = "https://github.com/AbsaOSS/living-doc/blob/"
NORMALIZED_BLOB = f"{BLOB}<normalized-for-snapshot>/"
PAGE = "docs/examples/pageobject/LoginPage.ts"
FEATURE_FILE = "docs/examples/gherkin/liv_doc_func/login.feature"


def artifact(source_url: str | None) -> dict:
    """A doc-source shaped artifact: one entity with a ``source_ref.url``, one warning with ``source_url``."""
    return {
        "features": [{"entity_id": "FEAT-001", "source_ref": {"url": f"{BLOB}{COMMIT}/{PAGE}"}}],
        "warnings": [{
            "code": "UNRESOLVED_RELATION",
            "entity_id": "FEAT-001",
            "line_no": 3 if source_url else None,
            "path": FEATURE_FILE if source_url else None,
            "source_url": source_url,
        }],
    }


def test_commit_in_url_and_source_url_is_replaced_and_path_kept() -> None:
    normalized = _normalize(artifact(f"{BLOB}{COMMIT}/{FEATURE_FILE}"))

    assert normalized["features"][0]["source_ref"]["url"] == f"{NORMALIZED_BLOB}{PAGE}"
    assert normalized["warnings"][0]["source_url"] == f"{NORMALIZED_BLOB}{FEATURE_FILE}"


def test_null_source_url_stays_null() -> None:
    normalized = _normalize(artifact(None))

    assert normalized["warnings"][0]["source_url"] is None
    assert normalized["features"][0]["source_ref"]["url"] == f"{NORMALIZED_BLOB}{PAGE}"


@pytest.mark.parametrize("key", ["url", "source_url"])
@pytest.mark.parametrize("ref", ["master", COMMIT[:7], COMMIT.upper()])
def test_url_without_a_full_lowercase_commit_is_kept(key: str, ref: str) -> None:
    value = f"{BLOB}{ref}/{FEATURE_FILE}"

    assert _normalize({key: value}) == {key: value}


def test_cli_writes_the_placeholder_with_sorted_keys() -> None:
    script = Path(__file__).with_name("normalize_snapshot.py")
    raw = json.dumps(artifact(f"{BLOB}{COMMIT}/{FEATURE_FILE}"))

    result = subprocess.run([sys.executable, str(script)], input=raw.encode("utf-8"),
                            capture_output=True, check=True)
    out = result.stdout.decode("utf-8")

    assert COMMIT not in out
    assert json.loads(out)["warnings"][0]["source_url"] == f"{NORMALIZED_BLOB}{FEATURE_FILE}"
    assert out.index('"path"') < out.index('"source_url"')
