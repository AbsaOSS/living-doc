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
- every AC carries the values its header declares, by ``Aspect:`` or by keyword, as ``aspect``, and
  names its keyword, if any, in ``placeholder_values``;
- a ``.feature`` file outside the living-doc folders contributes no entity and no AC link;
- the checkout holds at least one of each construct these invariants are about, so none passes on
  nothing.

The checkout is read the way the collector reads it: ``tutorial*`` folders and ``@tutorial`` files
and scenarios are skipped, a wrapped id list is joined before it is split, and ``none`` is no id.

``case`` asserts what a derived problem case (``integration/testbed_cases.py``) must report: one
warning, of its code, at the line it changed.

Runs in the ``collector-gh`` venv that ``tools/collector-gh.sh`` builds: it imports nothing but the
standard library and ``living-doc-utilities``, which that venv holds through the collector's own
``requirements.txt``. ``tools/run-testbed-stage.sh`` runs both commands.

Usage:
    python tools/check_testbed_stage.py core <output-root> <testbed-checkout> \\
        --us <dir> --func <dir> --pages <dir> --scenarios <dir>   # each dir relative to the checkout
    python tools/check_testbed_stage.py case <output-root> <code> <line> <changed-file>
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
# A header comment line's `#` leader and the one space after it; the rest of the indent is the line's level.
_COMMENT_LEADER_RE = re.compile(r"^#+ ?")
# A `{<name>}` in an AC's text: what makes a `- <name>: <values>` bullet the AC's keyword.
_PLACEHOLDER_RE = re.compile(r"\{(?P<name>[^{}]+)\}")
# An AC bullet `<name>: <values>`: `Aspect:`, `Rationale:` or a keyword candidate.
_NAMED_BULLET_RE = re.compile(r"^(?P<name>.+?):\s*(?P<values>.+)$")
# A scenario: Gherkin's scenario keywords, `Example:` (singular) among them; `Examples:` is a table, not one.
_SCENARIO_RE = re.compile(r"^\s*(?:Scenario|Scenario Outline|Scenario Template|Example)\s*:")
# A scenario tag `@AC:<id>[/<param>:<value>]`.
_AC_TAG_RE = re.compile(r"^@AC:(?P<id>[^/\s]+)(?:/(?P<param>[^:/\s]+):(?P<value>[^/\s]+))?$")
# One tag on a tag line.
_TAG_TOKEN_RE = re.compile(r"@\S+")
# A tutorial walkthrough is not living doc: a file tagged with it above `Feature:`, or a scenario tagged with it.
_TUTORIAL_TAG = "@tutorial"
_FEATURE_LINE_RE = re.compile(r"^\s*Feature:")
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
    # AC id -> its variant declaration: `aspect` for `Aspect:`, else the keyword's folded name, and its values.
    variants: dict[str, tuple[str, list[str]]] = field(default_factory=dict)
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


def _id_list(value: str, nested: list[str]) -> list[str]:
    """A comma-separated id list, its wrapped lines joined to it with one space; `none` is no id."""
    joined = " ".join(part for part in (line.strip() for line in [value, *nested]) if part)
    if joined.lower() == "none":
        return []
    return [item.strip() for item in joined.split(",") if item.strip()]


def _fold(name: str) -> str:
    """A variant keyword's name as the canon compares it: case-insensitive, `-`, `_` and space equal."""
    return re.sub(r"[-_ ]", "_", name.lower())


def _ac_items(block: list[str]) -> list[str]:
    """An AC block's bullets at its first bullet's level, a wrapped line deeper than its `-` joined with one space;
    a key at that level (`preconditions:`) and the lines under it are not bullets."""
    items: list[str] = []
    level, in_item = None, False
    for line in block:
        text = line.lstrip()
        if not text:
            continue
        indent = len(line) - len(text)
        level = indent if level is None else level
        if indent <= level:
            in_item = text.startswith("- ")
            if in_item:
                items.append(text[2:].strip())
        elif in_item:
            items[-1] = f"{items[-1]} {text}"
    return items


def _ac_variants(header: list[str]) -> dict[str, tuple[str, list[str]]]:
    """Each declared AC's variant declaration, as the canon spells it: `- Aspect: <values>`, or
    `- <name>: <values>` when the AC's text (its first bullet) names `{<name>}`. An AC with neither is left out."""
    lines = [_COMMENT_LEADER_RE.sub("", line, count=1) for line in header]
    variants: dict[str, tuple[str, list[str]]] = {}
    for index, line in enumerate(header):
        declaration = _AC_DECLARATION_RE.match(line)
        if declaration is None:
            continue
        level = len(lines[index]) - len(lines[index].lstrip())
        block = []
        for deeper in lines[index + 1:]:
            if deeper.strip() and len(deeper) - len(deeper.lstrip()) <= level:
                break
            block.append(deeper)
        text, *bullets = _ac_items(block) or [""]
        placeholders = {_fold(match.group("name")) for match in _PLACEHOLDER_RE.finditer(text)}
        for bullet in bullets:
            match = _NAMED_BULLET_RE.match(bullet)
            if match is None:
                continue
            # `Aspect:` and `Rationale:` are reserved; any other name is a keyword only when the AC's text names it.
            raw = match.group("name")
            if raw == "Aspect":
                name = "aspect"
            elif raw != "Rationale" and _fold(raw) in placeholders - {"aspect"}:
                name = _fold(raw)
            else:
                continue
            variants[declaration.group("id")] = (name, [value.strip() for value in match.group("values").split(",")])
            break
    return variants


def _is_under_tutorial(path: Path, root: Path) -> bool:
    """True when the scan root, or a folder between it and the file, is a `tutorial*` folder: not living doc."""
    return any(part.lower().startswith("tutorial") for part in (root.name, *path.relative_to(root).parts[:-1]))


def _feature_files(root: Path) -> list[Path]:
    """The `.feature` files the collector reads under a scan root: every one outside a `tutorial*` folder."""
    return [path for path in sorted(root.rglob("*.feature")) if not _is_under_tutorial(path, root)]


def _is_tutorial_file(lines: list[str]) -> bool:
    """True when a tag line above `Feature:` carries `@tutorial`."""
    for line in lines:
        if _FEATURE_LINE_RE.match(line):
            return False
        stripped = line.strip()
        if stripped.startswith("@") and _TUTORIAL_TAG in stripped.split():
            return True
    return False


def read_checkout(root: Path, us: str, func: str, pages: str, scenarios: str) -> Checkout:
    """Reads what the checkout authors under the collector's folders, each relative to ``root``,
    the way the collector discovers it: every ``.feature`` file under a folder, every ``.ts`` file
    under ``pages`` whose first comment names ``LIVING DOC``."""
    checkout = Checkout()

    def native_id(path: Path) -> str:
        return path.relative_to(root).as_posix()

    for folder, entity_type in ((us, "DocumentedUserStory"), (func, "DocumentedFunctionality")):
        for path in _feature_files(root / folder):
            header = _comment_header(path.read_text(encoding="utf-8"))
            checkout.entity_files[native_id(path)] = entity_type
            checkout.declared_acs[native_id(path)] = [
                match.group("id") for line in header if (match := _AC_DECLARATION_RE.match(line))
            ]
            checkout.variants.update(_ac_variants(header))

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
            functionalities=_id_list(*functionalities) if functionalities else [],
            notes=_bullets(notes[1]) if notes else [],
        ))

    living_doc_folders = [(root / us).resolve(), (root / func).resolve()]
    for path in _feature_files(root / scenarios):
        lines = path.read_text(encoding="utf-8").splitlines()
        if _is_tutorial_file(lines):
            continue
        file_id = native_id(path)
        checkout.scenario_files.append(file_id)
        if not any(path.resolve().is_relative_to(folder) for folder in living_doc_folders):
            checkout.outside.append(file_id)
        # A tag line's tags belong to the scenario right below them; any other construct drops them.
        pending: list[str] = []
        for line in lines:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("@"):
                pending.extend(_TAG_TOKEN_RE.findall(stripped))
                continue
            if _SCENARIO_RE.match(line) and _TUTORIAL_TAG not in pending:
                checkout.scenarios[file_id] += 1
                for token in pending:
                    if token.startswith("@AC:"):
                        match = _AC_TAG_RE.match(token)
                        checkout.tags.append(AcTag(file_id, *(match.group("id", "param", "value") if match
                                                              else (token, None, None))))
            pending = []
    return checkout


# --- The checks ------------------------------------------------------------------------------------------------------


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

    # Each AC's variants against its header: `aspect` holds the declared values, by `Aspect:` or by its keyword,
    # and `placeholder_values` names the keyword, or nothing on an `Aspect:` AC or an AC with no variants.
    acs = {ac.id: ac for entity in entities for ac in entity.acceptance_criteria}
    for ac_id in sorted(ac_id for declared in checkout.declared_acs.values() for ac_id in declared):
        if ac_id not in acs:
            continue
        ac = acs[ac_id]
        declaration, values = checkout.variants.get(ac_id, ("no variants", []))
        keywords = [declaration] if ac_id in checkout.variants and declaration != "aspect" else []
        if ac.aspect != values or [_fold(name) for name in ac.placeholder_values] != keywords:
            failures.append(f"doc-source: AC:{ac_id} aspect is {ac.aspect} by keyword {list(ac.placeholder_values)}, "
                            f"its header declares {values} by {declaration}")
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

    # A tag's parameter is the name its AC's header declares the variants by: `aspect`, or the keyword.
    for tag in checkout.tags:
        if tag.param is None:
            continue
        expected = checkout.variants.get(tag.ac_id, ("no variant declaration", []))[0]
        if _fold(tag.param) != expected:
            failures.append(f"ui-tests: {tag.native_id} tags AC:{tag.ac_id} with '{tag.param}', expected "
                            f"'{expected}'")


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

    types = Counter(checkout.entity_files.values())
    declarations = Counter("Aspect" if name == "aspect" else "keyword" for name, _ in checkout.variants.values())
    tags = Counter("bare" if tag.param is None else "aspect" if _fold(tag.param) == "aspect" else "keyword"
                   for tag in checkout.tags if tag.param is not None or tag.ac_id in checkout.variants)
    outside_scenarios = sum(checkout.scenarios[native_id] for native_id in checkout.outside)
    # At least one of each construct an invariant is about: an emptied folder only logs a collector message, and
    # both sides empty would pass every comparison above. A floor, not core's counts, which are read at run time.
    for construct, count in (
        ("User Story", types["DocumentedUserStory"]),
        ("Functionality", types["DocumentedFunctionality"]),
        ("Feature", types["DocumentedFeature"]),
        ("cross-reference page", len(checkout.cross_references)),
        ("cross-reference page with notes", sum(1 for reference in checkout.cross_references if reference.notes)),
        ("cross-reference page with functionalities",
         sum(1 for reference in checkout.cross_references if reference.functionalities)),
        ("keyword AC", declarations["keyword"]),
        ("Aspect: AC", declarations["Aspect"]),
        ("aspect tag", tags["aspect"]),
        ("keyword tag", tags["keyword"]),
        ("bare tag on an AC with variants", tags["bare"]),
        ("scenario outside the living-doc folders", outside_scenarios),
    ):
        if count == 0:
            failures.append(f"nothing to assert: the checkout has no {construct}")

    if failures:
        print(f"testbed core: {len(failures)} invariant(s) failed")
        for failure in failures:
            print(f"  FAIL {failure}")
        return 1

    print(f"  OK: {len(checkout.entity_files)} entities, one per file: {types['DocumentedUserStory']} User Stories "
          f"(.feature files under {us}), {types['DocumentedFunctionality']} Functionalities (under {func}), "
          f"{types['DocumentedFeature']} Features (full-header PageObjects under {pages}), every Feature state "
          f"derived")
    print(f"      {len(acs)} acceptance criteria (the AC: declarations in those headers): {len(checkout.variants)} "
          f"with variants, {declarations['Aspect']} by Aspect: and {declarations['keyword']} by keyword, each "
          f"carrying its declared values as aspect")
    print(f"      {len(checkout.cross_references)} cross-reference pages (PageObjects with parent-feat:), each a "
          f"non-primary page on its Feature with its own functionalities and notes; every primary page is its "
          f"Feature's full-header file")
    print(f"      {sum(checkout.scenarios.values())} scenarios (the scenario keywords in "
          f"{len(checkout.scenario_files)} .feature files under {scenarios}), {outside_scenarios} of them in "
          f"{len(checkout.outside)} file(s) outside the living-doc folders, with no entity and no AC link")
    print(f"      {len(checkout.tags)} AC links (the @AC: tags in those files), all resolved: "
          f"{tags['aspect']} aspect tags, {tags['keyword']} keyword tags, {tags['bare']} bare tag(s) on an AC with "
          f"variants (aspect: null)")
    print("      warnings: none")
    return 0


def check_case(output_root: Path, code: str, line: int, changed: Path) -> int:
    failures: list[str] = []
    result = _read(output_root, "doc-source", failures)
    if result is not None:
        for warning in result.warnings:
            print(f"    {_describe(warning)}")
        # `path` is relative to the scan root the file was found under, so it is a suffix of the changed file.
        located = [warning for warning in result.warnings if warning.code == code and warning.line_no == line
                   and warning.path and changed.as_posix().endswith(f"/{warning.path}")]
        if len(result.warnings) != 1 or len(located) != 1:
            got = [f"{warning.code} at line {warning.line_no} of {warning.path}" for warning in result.warnings]
            failures.append(f"doc-source: expected exactly one warning, {code} at line {line} of {changed.name}; "
                            f"got {got}")
    if failures:
        for failure in failures:
            print(f"  FAIL {failure}")
        return 1
    print(f"  OK: exactly one {code}, at line {line} of {changed.name}")
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
    case.add_argument("line", type=int, help="the 1-based line the case changed")
    case.add_argument("changed", type=Path)
    args = parser.parse_args(argv)
    if args.command == "core":
        return check_core(args.output_root, args.testbed, args.us, args.func, args.pages, args.scenarios)
    return check_case(args.output_root, args.code, args.line, args.changed)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
