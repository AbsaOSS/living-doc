#!/usr/bin/env python3
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
"""The collector stage's invariants over the testbed's ``core``, read at its ``master``.

``core`` follows the canon 100 %, so any warning over it is a defect. It is read at ``master``, so
its content is never written down here: every count and every id this checker compares comes from
the checkout at run time. ``core`` asserts, on the artifacts ``living-doc-collector-gh`` wrote
(each re-read with ``read_artifact``, which validates it against its contract):

- every artifact validates, ``sources_failed`` is 0 and there is no warning at all;
- every living-doc ``.feature`` file and every PageObject with a full header is one entity of its
  type, carrying every ``AC:`` its header declares, and nothing else is an entity;
- every Feature has a derived state;
- every cross-reference PageObject (``parent-feat:``) is a non-primary page on the Feature it
  names, with its own ``functionalities`` and ``notes`` as authored, and each Feature's primary
  page is its full-header file;
- every scenario in the checkout is mined, and every ``@AC:`` tag is a link with the tag's value;
  every link resolves to a declared AC and every value to one of that AC's values, and a tag's
  parameter is ``aspect`` on an ``Aspect:`` AC or the AC's own keyword;
- every keyword AC carries its keyword's values as ``aspect``;
- a ``.feature`` file outside the living-doc folders contributes no entity and no AC link.

``case`` asserts what a derived problem case (``integration/testbed_cases.py``) must report: one
warning, of its code, in the file it changed.

Runs in the ``collector-gh`` venv that ``tools/collector-gh.sh`` builds: it imports nothing but the
standard library and ``living-doc-utilities``, which that venv holds through the collector's own
``requirements.txt``. ``tools/run-testbed-stage.sh`` runs both commands.

Usage:
    python tools/check_testbed_stage.py core <output-root> <testbed-checkout> \\
        --us <dir> --func <dir> --pages <dir> --scenarios <dir>   # each dir relative to the checkout
    python tools/check_testbed_stage.py case <output-root> <code> <changed-file>
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from living_doc_utilities.contracts.codes import ContractError
from living_doc_utilities.contracts.io import read_artifact

# --- What the checkout authors ---------------------------------------------------------------------------------------

# An `AC:<id> (…)` declaration in a .feature file's header comment.
_AC_DECLARATION_RE = re.compile(r"^#\s*AC:(?P<id>\S+)\s*\(")
# A scenario: Gherkin's scenario keywords, `Example:` (singular) among them; `Examples:` is a table, not one.
_SCENARIO_RE = re.compile(r"^\s*(?:Scenario|Scenario Outline|Scenario Template|Example)\s*:")
# A scenario tag `@AC:<id>[/<param>:<value>]`.
_AC_TAG_RE = re.compile(r"^@AC:(?P<id>[^/\s]+)(?:/(?P<param>[^:/\s]+):(?P<value>[^/\s]+))?$")
# A PageObject header line once its ` * ` gutter is gone: `key: value`, at the header's own level.
_HEADER_KEY_RE = re.compile(r"^(?P<key>[a-z][a-z0-9_-]*):[ \t]*(?P<value>.*)$")
# The marker every PageObject header names in its banner (`LIVING DOC — <id> · <title>`).
_LIVING_DOC_MARKER = "LIVING DOC"


@dataclass(frozen=True)
class AcTag:
    """One `@AC:` tag as authored."""

    native_id: str
    ac_id: str
    param: str | None
    value: str | None


@dataclass(frozen=True)
class CrossReference:
    """A cross-reference PageObject's header: the Feature it names and what it authors for itself."""

    native_id: str
    parent_feat: str
    functionalities: list[str]
    notes: list[str]


@dataclass
class Checkout:
    """What the testbed checkout authors, read at run time; every check compares against this."""

    # native_id (path from the checkout root) -> the entity type that file must yield.
    entity_files: dict[str, str] = field(default_factory=dict)
    # native_id -> the AC ids its header declares.
    declared_acs: dict[str, list[str]] = field(default_factory=dict)
    cross_references: list[CrossReference] = field(default_factory=list)
    # Every .feature file under the scenario folder, and each one's number of scenarios.
    scenario_files: list[str] = field(default_factory=list)
    scenarios: Counter = field(default_factory=Counter)
    tags: list[AcTag] = field(default_factory=list)
    # The .feature files under the scenario folder but outside both living-doc folders.
    outside: list[str] = field(default_factory=list)


def _comment_header(text: str) -> list[str]:
    """A .feature file's header: its leading `#` lines."""
    header = []
    for line in text.splitlines():
        if not line.startswith("#"):
            break
        header.append(line)
    return header


def _page_header(text: str) -> list[str] | None:
    """A PageObject's header: the file's first `/* … */` comment, each line without its ` * `
    gutter; None when that comment never names `LIVING DOC` (the file is code, not documentation)."""
    lines = text.splitlines()
    start = next((index for index, line in enumerate(lines) if "/*" in line), None)
    if start is None:
        return None
    block = []
    for line in lines[start + 1:]:
        if "*/" in line:
            break
        block.append(re.sub(r"^\s*\*(?: |$)", "", line, count=1))
    return block if any(_LIVING_DOC_MARKER in line for line in [lines[start], *block]) else None


def _header_value(block: list[str], key: str) -> tuple[str, list[str]] | None:
    """A PageObject header key's inline value and the lines below it that sit deeper than the key."""
    for index, line in enumerate(block):
        match = _HEADER_KEY_RE.match(line)
        if match and match.group("key") == key:
            nested = []
            for deeper in block[index + 1:]:
                if not deeper.strip() or not deeper[0].isspace():
                    break
                nested.append(deeper)
            return match.group("value").strip(), nested
    return None


def _bullets(lines: list[str]) -> list[str]:
    """`- item` bullets, a wrapped line deeper than its `-` joined to its item with one space."""
    items: list[str] = []
    marker_indent = None
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        if stripped.startswith("- ") and (marker_indent is None or indent <= marker_indent):
            items.append(stripped[2:].strip())
            marker_indent = indent
        elif items:
            items[-1] = f"{items[-1]} {stripped}"
    return items


def read_checkout(root: Path, us: str, func: str, pages: str, scenarios: str) -> Checkout:
    """Reads what the checkout authors under the collector's folders, each relative to ``root``,
    the way the collector discovers it: every ``.feature`` file under a folder, every ``.ts`` file
    under ``pages`` whose first comment names ``LIVING DOC``."""
    checkout = Checkout()

    def native_id(path: Path) -> str:
        return path.relative_to(root).as_posix()

    for folder, entity_type in ((us, "DocumentedUserStory"), (func, "DocumentedFunctionality")):
        for path in sorted((root / folder).rglob("*.feature")):
            checkout.entity_files[native_id(path)] = entity_type
            checkout.declared_acs[native_id(path)] = [
                match.group("id") for line in _comment_header(path.read_text(encoding="utf-8"))
                if (match := _AC_DECLARATION_RE.match(line))
            ]

    for path in sorted((root / pages).rglob("*.ts")):
        block = _page_header(path.read_text(encoding="utf-8"))
        if block is None:
            continue
        parent = _header_value(block, "parent-feat")
        if parent is None:
            checkout.entity_files[native_id(path)] = "DocumentedFeature"
            continue
        functionalities = _header_value(block, "functionalities")
        notes = _header_value(block, "notes")
        checkout.cross_references.append(CrossReference(
            native_id=native_id(path),
            parent_feat=parent[0],
            functionalities=[item.strip() for item in functionalities[0].split(",") if item.strip()]
            if functionalities else [],
            notes=_bullets(notes[1]) if notes else [],
        ))

    living_doc_folders = [(root / us).resolve(), (root / func).resolve()]
    for path in sorted((root / scenarios).rglob("*.feature")):
        file_id = native_id(path)
        checkout.scenario_files.append(file_id)
        if not any(path.resolve().is_relative_to(folder) for folder in living_doc_folders):
            checkout.outside.append(file_id)
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith("#"):
                continue
            if _SCENARIO_RE.match(line):
                checkout.scenarios[file_id] += 1
            for token in line.split():
                if token.startswith("@AC:"):
                    match = _AC_TAG_RE.match(token)
                    checkout.tags.append(AcTag(file_id, *(match.group("id", "param", "value") if match
                                                          else (token, None, None))))
    return checkout


# --- The checks ------------------------------------------------------------------------------------------------------


def _fold(name: str) -> str:
    """A variant keyword's name as the canon compares it: case-insensitive, `-`, `_` and space equal."""
    return re.sub(r"[-_ ]", "_", name.lower())


def _describe(warning) -> str:
    """A warning with every typed field that locates it: code, entity, AC, line and file."""
    line = warning.line_no if warning.line_no is not None else "-"
    return (f"{warning.code} entity={warning.entity_id or '-'} ac={warning.ac_id or '-'} line={line} "
            f"path={warning.path or '-'}: {warning.message}")


def _read(root: Path, mode: str, failures: list[str]):
    """Re-reads one artifact with `read_artifact`, which validates it; asserts `sources_failed: 0`."""
    path = root / mode / f"{mode}.json"
    try:
        result = read_artifact(path, mode)
    except (ContractError, OSError, ValueError) as exc:
        failures.append(f"{mode}: {path} does not validate against its contract: {exc}")
        return None
    cardinality = result.metadata.stats.cardinality
    print(f"  {mode}: valid ({result.schema_version}); sources_failed {cardinality.sources_failed}; "
          f"warnings: {len(result.warnings) or 'none'}")
    if cardinality.sources_failed:
        failures.append(f"{mode}: sources_failed is {cardinality.sources_failed}, expected 0")
    return result


def check_doc_source(result, checkout: Checkout, failures: list[str]) -> dict:
    """Asserts the entities, their ACs, the Features' derived states and the pages; returns the ACs by id."""
    entities = [*result.user_stories, *result.features, *result.functionalities]
    by_file: dict[str, list] = {}
    for entity in entities:
        by_file.setdefault(entity.source_ref.native_id, []).append(entity)

    for native_id, entity_type in checkout.entity_files.items():
        found = by_file.get(native_id, [])
        if [entity.type for entity in found] != [entity_type]:
            failures.append(f"doc-source: {native_id} yields {[f'{e.entity_id} ({e.type})' for e in found]}, "
                            f"expected one {entity_type}")
            continue
        if native_id in checkout.declared_acs:
            mined = sorted(ac.id for ac in found[0].acceptance_criteria)
            if mined != sorted(checkout.declared_acs[native_id]):
                failures.append(f"doc-source: {found[0].entity_id} carries ACs {mined}, its header declares "
                                f"{sorted(checkout.declared_acs[native_id])}")
    for native_id in sorted(set(by_file) - set(checkout.entity_files)):
        where = " (outside the living-doc folders)" if native_id in checkout.outside else ""
        failures.append(f"doc-source: {native_id}{where} yields {[e.entity_id for e in by_file[native_id]]}, "
                        f"expected no entity")

    features = {feature.entity_id: feature for feature in result.features}
    for feature in features.values():
        if feature.state_origin != "derived":
            failures.append(f"doc-source: {feature.entity_id} state is {feature.state_origin}, expected derived")

    expected_pages: dict[str, list[str]] = {}
    for native_id, entity_type in checkout.entity_files.items():
        if entity_type == "DocumentedFeature" and len(by_file.get(native_id, [])) == 1:
            feature = by_file[native_id][0]
            expected_pages[feature.entity_id] = [Path(native_id).name]
            primary = [page.page_object for page in feature.pages if page.is_primary]
            if primary != [Path(native_id).name]:
                failures.append(f"doc-source: {feature.entity_id} primary page is {primary}, expected its full-header "
                                f"file {Path(native_id).name}")
    for reference in checkout.cross_references:
        name = Path(reference.native_id).name
        feature = features.get(reference.parent_feat)
        if feature is None:
            failures.append(f"doc-source: {reference.native_id} names parent-feat {reference.parent_feat}, "
                            f"which is not a mined Feature")
            continue
        expected_pages.setdefault(feature.entity_id, []).append(name)
        pages = [page for page in feature.pages if page.page_object == name]
        if len(pages) != 1 or pages[0].is_primary:
            failures.append(f"doc-source: {reference.native_id} is {len(pages)} page(s) on {feature.entity_id}"
                            f"{' (primary)' if any(page.is_primary for page in pages) else ''}, "
                            f"expected one non-primary page")
            continue
        if pages[0].functionalities != reference.functionalities:
            failures.append(f"doc-source: {feature.entity_id} page {name} functionalities is "
                            f"{pages[0].functionalities}, authored {reference.functionalities}")
        if pages[0].notes != reference.notes:
            failures.append(f"doc-source: {feature.entity_id} page {name} notes is {pages[0].notes}, "
                            f"authored {reference.notes}")
    for feature_id, names in expected_pages.items():
        mined = sorted(page.page_object for page in features[feature_id].pages)
        if mined != sorted(names):
            failures.append(f"doc-source: {feature_id} pages are {mined}, expected {sorted(names)}")

    acs = {ac.id: ac for entity in entities for ac in entity.acceptance_criteria}
    for ac in acs.values():
        if ac.placeholder_values:
            values = list(ac.placeholder_values.values())
            if len(values) != 1 or ac.aspect != values[0]:
                failures.append(f"doc-source: AC:{ac.id} aspect is {ac.aspect}, expected its keyword's values "
                                f"{ac.placeholder_values}")
    return acs


def check_ui_tests(result, checkout: Checkout, acs: dict, failures: list[str]) -> None:
    mined_scenarios = Counter(scenario.source_ref.native_id for scenario in result.scenarios)
    for native_id in sorted(set(mined_scenarios) | set(checkout.scenarios)):
        if mined_scenarios[native_id] != checkout.scenarios[native_id]:
            failures.append(f"ui-tests: {native_id} mined {mined_scenarios[native_id]} scenario(s), "
                            f"it has {checkout.scenarios[native_id]}")

    links = [(scenario.source_ref.native_id, link) for scenario in result.scenarios
             for link in scenario.acceptance_criteria]
    mined = Counter((native_id, link.id, link.aspect) for native_id, link in links)
    authored = Counter((tag.native_id, tag.ac_id, tag.value) for tag in checkout.tags)
    for key in sorted(set(mined) | set(authored), key=str):
        if mined[key] != authored[key]:
            native_id, ac_id, value = key
            tag = f"@AC:{ac_id}" + (f"/…:{value}" if value else "")
            failures.append(f"ui-tests: {native_id} tags {tag} {authored[key]} time(s), mined as "
                            f"{mined[key]} link(s)")

    for native_id, link in links:
        ac = acs.get(link.id)
        if ac is None:
            failures.append(f"ui-tests: {native_id} links AC:{link.id}, which no entity declares")
        elif link.aspect is not None and link.aspect not in ac.aspect:
            failures.append(f"ui-tests: {native_id} links AC:{link.id} as '{link.aspect}', not one of its "
                            f"declared values {ac.aspect}")
        if native_id in checkout.outside:
            failures.append(f"ui-tests: {native_id} is outside the living-doc folders and links AC:{link.id}")

    for tag in checkout.tags:
        ac = acs.get(tag.ac_id)
        if tag.param is None or ac is None:
            continue
        keywords = [_fold(name) for name in ac.placeholder_values]
        expected = keywords or ["aspect"]
        if _fold(tag.param) != expected[0] or len(expected) != 1:
            failures.append(f"ui-tests: {tag.native_id} tags AC:{tag.ac_id} with '{tag.param}', expected "
                            f"'{'/'.join(expected)}'")


def check_core(output_root: Path, testbed: Path, us: str, func: str, pages: str, scenarios: str) -> int:
    checkout = read_checkout(testbed, us, func, pages, scenarios)
    failures: list[str] = []
    doc_source = _read(output_root, "doc-source", failures)
    ui_tests = _read(output_root, "ui-tests", failures)
    for mode, result in (("doc-source", doc_source), ("ui-tests", ui_tests)):
        failures.extend(f"{mode}: warning {_describe(warning)}" for warning in (result.warnings if result else []))
    acs = check_doc_source(doc_source, checkout, failures) if doc_source is not None else {}
    if ui_tests is not None and doc_source is not None:
        check_ui_tests(ui_tests, checkout, acs, failures)

    if failures:
        print(f"testbed core: {len(failures)} invariant(s) failed")
        for failure in failures:
            print(f"  FAIL {failure}")
        return 1

    types = Counter(checkout.entity_files.values())
    keyword_acs = [ac for ac in acs.values() if ac.placeholder_values]
    variant_acs = {ac.id for ac in acs.values() if ac.aspect}
    outside_scenarios = sum(checkout.scenarios[native_id] for native_id in checkout.outside)
    print(f"  OK: {len(checkout.entity_files)} entities, one per file: {types['DocumentedUserStory']} User Stories "
          f"(.feature files under {us}), {types['DocumentedFunctionality']} Functionalities (under {func}), "
          f"{types['DocumentedFeature']} Features (full-header PageObjects under {pages}), every Feature state "
          f"derived")
    print(f"      {len(acs)} acceptance criteria (the AC: declarations in those headers): {len(variant_acs)} with "
          f"variants, {len(keyword_acs)} of them by keyword, each carrying its keyword's values as aspect")
    print(f"      {len(checkout.cross_references)} cross-reference pages (PageObjects with parent-feat:), each a "
          f"non-primary page on its Feature with its own functionalities and notes; every primary page is its "
          f"Feature's full-header file")
    print(f"      {sum(checkout.scenarios.values())} scenarios (the scenario keywords in "
          f"{len(checkout.scenario_files)} .feature files under {scenarios}), {outside_scenarios} of them in "
          f"{len(checkout.outside)} file(s) outside the living-doc folders, with no entity and no AC link")
    print(f"      {len(checkout.tags)} AC links (the @AC: tags in those files), all resolved: "
          f"{sum(1 for tag in checkout.tags if tag.param and _fold(tag.param) == 'aspect')} aspect tags, "
          f"{sum(1 for tag in checkout.tags if tag.param and _fold(tag.param) != 'aspect')} keyword tags, "
          f"{sum(1 for tag in checkout.tags if tag.param is None and tag.ac_id in variant_acs)} bare tag(s) on an "
          f"AC with variants (aspect: null)")
    print("      warnings: none")
    return 0


def check_case(output_root: Path, code: str, changed: Path) -> int:
    failures: list[str] = []
    result = _read(output_root, "doc-source", failures)
    if result is not None:
        for warning in result.warnings:
            print(f"    {_describe(warning)}")
        # `path` is relative to the scan root the file was found under, so it is a suffix of the changed file.
        located = [warning for warning in result.warnings if warning.code == code and warning.path
                   and changed.as_posix().endswith(f"/{warning.path}")]
        if len(result.warnings) != 1 or len(located) != 1:
            failures.append(f"doc-source: expected exactly one warning, {code} in {changed.name}; got "
                            f"{[f'{warning.code} in {warning.path}' for warning in result.warnings]}")
    if failures:
        for failure in failures:
            print(f"  FAIL {failure}")
        return 1
    print(f"  OK: exactly one {code}, in {changed.name}")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    core = commands.add_parser("core", help="the invariants over core")
    core.add_argument("output_root", type=Path)
    core.add_argument("testbed", type=Path)
    for name in ("us", "func", "pages", "scenarios"):
        core.add_argument(f"--{name}", required=True, help="a folder, relative to the testbed checkout")
    case = commands.add_parser("case", help="the one warning a derived case must report")
    case.add_argument("output_root", type=Path)
    case.add_argument("code")
    case.add_argument("changed", type=Path)
    args = parser.parse_args(argv)
    if args.command == "core":
        return check_core(args.output_root, args.testbed, args.us, args.func, args.pages, args.scenarios)
    return check_case(args.output_root, args.code, args.changed)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
