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

"""
Normalize a collector / toolkit JSON artifact for snapshot comparison.

The real collector and the coverage-matrix CLI stamp every run with volatile values
(wall-clock timestamps, and — inside GitHub Actions — the run id / attempt / actor /
sha, plus ``metadata.producer.build``). Those carry no signal about whether the *mined content* changed, so they are
replaced with fixed placeholders before the file is diffed against the committed
expected snapshot under ``docs/examples/_expected/``.

Everything else, including ``metadata.producer.version``, is kept verbatim: a
collector version bump that moves the parser output is exactly the drift this snapshot
is meant to catch.

Usage:
    python tools/normalize_snapshot.py < raw.json > normalized.json
"""

import json
import sys

_PLACEHOLDER = "<normalized-for-snapshot>"

# Keys whose value is replaced with the placeholder string wherever they appear.
_VOLATILE_SCALAR_KEYS = {"generated_at"}

# Keys whose value is blanked to None wherever they appear. ``producer.build`` is the
# CI run id when the collector runs inside GitHub Actions and absent (None) otherwise -
# volatile run identity, exactly like the ``run`` block, and no signal about mined content.
_VOLATILE_NULLED_KEYS = {"build"}


def _normalize(node):
    """Recursively replace volatile values in place and return the node."""
    if isinstance(node, dict):
        # Any dict named "run" (in practice metadata.run) is a whole block of
        # CI-run identity — blank every leaf.
        run = node.get("run")
        if isinstance(run, dict):
            node["run"] = {key: None for key in run}

        for key, value in node.items():
            if key in _VOLATILE_SCALAR_KEYS and not isinstance(value, (dict, list)):
                node[key] = _PLACEHOLDER
            elif key in _VOLATILE_NULLED_KEYS and not isinstance(value, (dict, list)):
                node[key] = None
            else:
                _normalize(value)
    elif isinstance(node, list):
        for item in node:
            _normalize(item)
    return node


def main() -> None:
    """Read JSON from stdin, normalize it, and print it back deterministically."""
    data = json.load(sys.stdin)
    normalized = _normalize(data)
    json.dump(normalized, sys.stdout, indent=2, sort_keys=True, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
