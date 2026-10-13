---
name: gherkin-living-doc-sync
description: >
  Synchronise Gherkin feature files and BDD scenarios with the living documentation catalog.
  Corrects existing links — distinct from living-doc-gap-finder (which detects missing coverage).
  Activate when `@AC:` tags or `# AC:` comments are missing or stale, step text drifts after
  a refactor, ACs are descoped, or AC changes must propagate from the living doc to feature files.
  Run scan_ac_links.py to audit AC link health before a sync pass.
  Triggers on: "sync gherkin to living doc", "feature file out of sync", "scenario not linked
  to AC", "step text changed", "gherkin drift", "BDD sync", "AC link missing in feature file",
  "sync scenarios", "traceability broken", "propagate AC changes", "AC was descoped".
  Does NOT trigger for: writing new scenarios (use living-doc-scenario-creator); implementing
  step definitions (use gherkin-step); finding gaps (use living-doc-gap-finder);
  creating entities (use living-doc-create-*).
  Pairs with living-doc-update (upstream) and gherkin-step (downstream).
license: Apache-2.0
---

# Gherkin ↔ Living Doc Sync

> **Glossary:** Feature, Functionality, User Story, AC — see [living-doc-glossary](../shared/references/living-doc-glossary.md) ([remote](https://github.com/AbsaOSS/living-doc/blob/master/docs/guides/living-doc-glossary.md)).
> **BDD schemas:** US and Functionality feature file headers, `# Acceptance Criteria:` block format — see [living-doc-bdd-schemas](../shared/references/living-doc-bdd-schemas.md) ([remote](https://github.com/AbsaOSS/living-doc/blob/master/docs/guides/living-doc-header-types.md)).

Sync runs in three directions: (1) feature file to living doc, (2) living doc AC to feature file,
(3) step text to PageObject method signature.

> **Script paths are relative to this skill's own directory**, not to your working directory — a skill installs as a self-contained directory with its `scripts/` inside it. Commands are written as `python …`, which assumes an activated virtual environment; on a system where only `python3` exists, activate a venv first or substitute `python3`.

Use `scripts/scan_ac_links.py` to detect missing or malformed `@AC:` tags and missing `# AC:`
comments before a full sync run. The script only checks the living-doc feature directories
(`feature_dirs.user_story` and `feature_dirs.functionality` from the Project Profile, defaults
`features/liv_doc_us/` and `features/liv_doc_func/`; pass them via `--us-dir`/`--func-dir`) — other
feature files are skipped.
For a full audit, run:

```bash
python scripts/scan_ac_links.py <features_dir> \
  --us-dir <feature_dirs.user_story> \
  --func-dir <feature_dirs.functionality>
```

The script takes only those arguments plus `--allow-empty`; it has no `--catalog` option, so it
never reads the catalog and cannot tell a stale AC ID from a valid one. It reports exactly four
findings:

| Finding | Meaning |
|---|---|
| `missing_ac_tag` | a scenario has no `@AC:` tag |
| `malformed_ac_id` | an `@AC:` tag whose ID does not match the grammar |
| `duplicate_ac_link` | the same AC linked from more than one scenario |
| `missing_ac_comment` | an `@AC:` tag with no matching `# AC:` comment |

Use the report in this repair order: malformed IDs first, then missing tags and comments, then
duplicates. **Stale AC IDs and mismatched `# AC:` / `@AC:` detail are not covered by this script**
— they need the catalog, so check them against it separately.

---

## Step 1 — Detect the sync direction

**Upstream dependencies:** Directions that flow from the living documentation into feature files are initiated by catalog-layer operations from `@living-doc-bdd-copilot`:
- `living-doc-update` modified, added, or deprecated an AC → triggers directions 2 and 4 below
- `living-doc-impact-analysis` identified High-impact AC changes that require resync → may trigger directions 2 and 3

| Change event | Sync direction | Action |
|---|---|---|
| New `.feature` file added | Feature file to living doc | Link each scenario to an AC; create AC if missing |
| User Story AC modified or added | Living doc to feature file | Update or add the corresponding scenario |
| UI refactored (selector / method renamed) | Step text to PageObject | Update step text and `@AC:` tag if scenario intent changed; for the PageObject side of the rename (method signature or locator), load `living-doc-pageobject-scan` HEALING scope - this skill owns only the Gherkin step text, not the PageObject code |
| US deprecated | Living doc to feature file | Emit one sync action per linked scenario; add `@deprecated`, record the reason, and flag `@review-needed` |
| Scenario added without an `@AC:` tag | Feature file to living doc | Propose an AC and add the `@AC:` tag |

---

## Step 2 - Audit `@AC:` traceability tags

> **Authoritative source:** The `@AC:` format is defined in `living-doc-scenario-creator`. The spec below is a reference copy for sync validation - load `living-doc-scenario-creator` for the canonical definition.

**Required traceability format** for living-doc feature files (from the glossary):

```gherkin
# AC:US-1-01 (v1.0.0 - active) - customer places an order with a saved payment method
@AC:US-1-01
Scenario: Customer successfully places an order
```

With a variant parameter - when the scenario covers one declared value of the AC. The
parameter name is the AC's own: `aspect` when it declared `- Aspect:`, otherwise its keyword,
spelled the same in the AC text, the declaration and the tag:

```gherkin
# the AC declared `- Aspect: username-input, password-input`
# AC:US-1-01 (v1.0.0 - active) - displays the required field on the login screen
@AC:US-1-01/aspect:username-input
Scenario: Login form shows the username input field
```

```gherkin
# the AC named it in its text and declared `- channel: email, sms`
# AC:US-2-01 (v1.0.0 - active) - the reset link is sent to the customer's {channel}
@AC:US-2-01/channel:email
Scenario: Reset link is sent by email
```

- `# AC:` comment: human-readable context - ID, version, state, description, optional aspect.
- `@AC:` Cucumber tag: `@AC:<id>[/<param>:<value>]` - machine-readable link, with **at most one** `/<param>:<value>` segment. A scenario covers one value, so one scenario is tagged per value; a tag carrying two parameters is `MALFORMED_AC`. `<param>` is the AC's own variant name - `aspect`, or its keyword - in lowercase kebab-case. A `<value>` the AC does not declare is `STALE_AC_REF`: report it with the declared values, and either correct the tag to one of them or add the value to the AC's declaration first (through `living-doc-update`) - never leave the tag pointing at an undeclared value. See [AC variants](../shared/references/living-doc-bdd-schemas.md#ac-variants).
- The `@AC:` tag(s) must appear on the lines immediately above `Scenario:` or `Scenario Outline:`. Additional tags (e.g. `@Regression`, `@skip`) may appear in the same block.
- Full AC details (version, state, description) live in the file's `# Acceptance Criteria:` header block.

**Deprecated US detection (Direction 4):** When the trigger is a deprecated User Story, first
build the list of affected scenarios before running the standard checklist:

1. Collect all AC IDs owned by the deprecated US (from the US entity or its feature file header).
2. Search all `.feature` files under the living-doc directories (`feature_dirs.user_story` and
   `feature_dirs.functionality`) for
   `@AC:` tags matching those IDs.
3. For each matching scenario, emit a SYNC ACTION to add `@deprecated` and `@review-needed`,
   with a comment recording the deprecation date and reason from the US entity.
4. After tagging, continue with the standard checklist below to catch any remaining link issues.

**Audit checklist:**
1. Does every `Scenario:` / `Scenario Outline:` in living-doc files have at least one `@AC:` tag?
2. Is the corresponding `# AC:` comment present and matching the tag's AC ID?
3. Does the referenced AC ID exist in the living documentation?
4. Does the AC state match (logically `active` — not `deprecated`, `planned`, or `in_review`, per the profile `ac_states`)?
5. Does the AC description (in the file header) match the scenario intent?

For each missing or mismatched tag:

```
SYNC ACTION: checkout.feature:14
  Scenario: "Customer successfully places an order"
  Missing @AC: tag
  Proposed tag: @AC:US-001-01
  Confirm or select a different AC
```

For each missing or mismatched `# AC:` comment, emit the same style of block and propose the full
comment line:

```text
SYNC ACTION: checkout.feature:14 — Missing AC link header
  Scenario: "Customer successfully places an order"
  Proposed link: # AC:US-001-01 (v1.0.0 - active) - customer places an order with a saved payment method
  Apply change? (y/n)
```

When multiple scenarios are affected, emit one `SYNC ACTION` block per scenario and identify each
scenario by file path, line number, and title before proposing the `# AC:` line. Preserve every
scenario — syncing missing headers never deletes or restructures the scenario itself.
If the prompt states a concrete count (for example “3 scenarios”), say that all 3 scenarios are
missing AC link headers, then emit 3 separate `SYNC ACTION` blocks and propose a matching AC for
each scenario from the living doc catalog. Do not hedge with “for example” or generic placeholders
in that answer — show the concrete proposed mappings directly in the blocks.
**A mapping needs the catalog.** Propose a concrete AC ID, version and description only when the
catalog (or the AC list) is actually available in the session. Without it, still emit one block per
scenario, write the proposed link as `# AC:<id needed> - <matching AC from the catalog>`, and ask for
the catalog — never invent an AC ID, version or description to fill the block.

If only one of `@AC:` or `# AC:` is present, that is still a sync issue - raise a SYNC ACTION and
repair the missing side rather than treating the scenario as already synced.

## Step 3 — Detect step text drift

When step text changes after a UI refactor, the step definition binding breaks:

```
DRIFT DETECTED: checkout.feature:17
  Step: "When the customer clicks the Confirm Purchase button"
  No matching step definition found
  Previous match: "When the customer confirms the order" (checkout_steps.py:34)
  PageObject method: CheckoutPage.confirm_order()
  Suggested fix: update step text to "When the customer confirms the order"
    OR update the step definition regex to match the new wording
```

> **Scope boundary with `living-doc-pageobject-scan` HEALING:** This step corrects step text in `.feature` files and step definition pattern strings. If the underlying PageObject selector or method signature drifted (renamed in the DOM or PageObject class), use `living-doc-pageobject-scan` HEALING mode to fix the PageObject class first, then re-run this sync to align feature files.
>
> **Step definition code changes:** When a step definition regex pattern must be updated (not just the feature file wording), load `gherkin-step` to apply the code change correctly.
>
> **Output rule:** Always emit the full `DRIFT DETECTED` block header with file path, line number,
> broken step text, previous matching definition, PageObject method, and the two fix options. Prefer
> fixing the `.feature` file wording first because it is the lower-risk change when the existing step
> definition and PageObject method still work.

---

## Step 4 — Apply sync changes

Apply the minimum necessary change per action:

- **Add missing `@AC:` tag**: insert `@AC:<id>` above `Scenario:`
- **Update stale AC reference**: this is **living doc → feature file** sync. Update the `# AC:` comment directly ABOVE the affected scenario to reflect the new version, state, and description from the living doc. The `@AC:` tag on the scenario stays unchanged. Show the exact change as `OLD:` and `NEW:` lines, and mirror the current version/state text from the living doc in the `NEW:` line (for example `v1.0.0` → `v1.1.0` when the AC version changed). If the revised AC intent changed materially, add an explicit `Step text review:` note so the linked step wording can be checked before any scenario restructuring. Also update the matching `AC:<id>` entry in the file header's `# acceptance_criteria:` block (see `living-doc-bdd-schemas.md`) to the same version, state, and description in the same sync action — the header entry is mined US/Functionality metadata, not decorative, and a stale copy there lets a collector read outdated AC data even after the scenario-level comment is fixed.
- **Update scenario to match revised AC**: update step text; keep the `@AC:` tag unchanged
- **Fix broken step text**: prefer updating the `.feature` file to match the existing step definition and PageObject method; only update the step definition regex when the business wording genuinely changed
- **Mark deprecated scenarios**: add `@deprecated` and `@review-needed`, plus a comment with the date and reason. Emit one action per affected scenario with file and line number.
- **Mark descoped scenarios**: there is no `descoped` state — the AC keeps its `planned` state and drops any target version, reading `AC:<id> (planned)`. Update the existing `# AC:` comment's header to `AC:<id> (planned)` while keeping its description unchanged — the description is required and must still match the catalog AC — then add a separate `# Rationale: ...` comment line mirroring the AC's `- Rationale:` bullet. Also update the matching `AC:<id>` entry in the file header's `# acceptance_criteria:` block (see `living-doc-bdd-schemas.md`) in the same sync action — drop its target version to match `AC:<id> (planned)` and add the `- Rationale:` bullet there too — the header entry is mined US/Functionality metadata, not decorative, and a stale copy there lets a collector keep mining the old target version even after the scenario-level comment is fixed. Add `@wip` and `@review-needed` to the scenario. Preserve the scenario — never delete it — so it can be reinstated when the AC is re-targeted to a release. Emit one SYNC ACTION per affected scenario.
- **Broken AC reference**: never silently remove the `@AC:` tag. Either relink it to the correct AC ID, or create the missing living doc entity with `living-doc-create-user-story` / `living-doc-create-functionality`, then update the tag.
- **AC split into multiple ACs**: update the existing scenario's `@AC:` tag to the primary AC; emit a separate `SYNC ACTION` proposing each additional scenario, including the required `# AC:` header and `@AC:` tag for the new AC. Developer confirmation is still required before any new scenario is created.
- **Aspect mismatch** (`@AC:.../aspect:...` present but comment missing the aspect): raise a SYNC ACTION and update the comment to include the human-readable `| aspect: ...` suffix. Confirm before applying.

Never delete a scenario during sync — flag it with `@review-needed` for developer decision.

---

## Step 5 — Output sync report

Do **not** apply sync changes automatically. Report `DRIFT DETECTED` blocks first (tests fail), then `SYNC ACTION` blocks (traceability), and ask the developer to confirm each action before editing files. List every affected scenario with file path and line number. This confirmation rule also applies to comment-only edits such as updating a `# AC:` description or adding an aspect suffix.
Prioritise repair in this order: broken step bindings first because they cause immediate test
failures, then stale / broken AC links because they create traceability gaps, then lower-risk
comment/tag mismatches.

```
DRIFT DETECTED: checkout.feature:17
  Step: "When the customer clicks the Confirm Purchase button"
  No matching step definition found
  Previous match: "When the customer confirms the order" (checkout_steps.py:34)
  PageObject method: CheckoutPage.confirm_order()
  Recommended fix: update the feature file step text to match the existing step definition
    OR update the step definition regex to match the new wording
  Apply change? (y/n)

SYNC ACTION: checkout.feature:14
  Scenario: "Customer successfully places an order"
  Missing @AC: tag
  Proposed tag: @AC:US-001-01
  Apply change? (y/n)

SYNC ACTION: checkout.feature:32
  Scenario: "Customer reviews order totals before payment"
  Missing @AC: tag
  Proposed tag: @AC:US-001-02
  Apply change? (y/n)

Summary: 2 missing AC links, 1 step text drift detected — apply changes? (y/n per action)
```

For deprecated or descoped entities, emit one `SYNC ACTION` per affected scenario, each with its own
file path and line number, plus the added tags/comments (`@deprecated` + `@review-needed`, or
`@wip` + `@review-needed` mirroring the AC's `- Rationale:` bullet).
For missing-link report examples, include the full proposed `# AC:` comment (ID, version, state,
description, and aspect if relevant) - not just the `@AC:` tag.

---

## Anti-patterns to flag

| Anti-pattern | Flag |
|---|---|
| Scenario with no `@AC:` tag | Missing traceability - add tag or create AC |
| Two scenarios linked to the same AC | Usually a duplicate — review |
| AC linked from a scenario in a different User Story's feature file | Passive cross-US coverage — permitted but note it in the sync report. Only flag if the scenario's primary intent belongs to a different User Story (misplaced scenario) |
| Step text describes implementation (selector, endpoint) | Gherkin business-language violation — refer to `living-doc-scenario-creator` |

---

## Indentation is significant

A header is read part by part, and indentation decides where each part ends. Full rule:
[Indentation](../shared/references/living-doc-bdd-schemas.md#indentation). What bites while
writing one:

- **Every header line carries its marker** — `# ` in a `.feature` header. A line with text and
  no marker is not read, and the file is reported.
- **A key sits at the key level**, the indent of the header's first key. A line shaped `key:`
  any deeper is content of the part above it, never a new key.
- **A deeper line belongs to the item above it** — wrapped text or a nested item, never a
  sibling and never a new key.
- **One criterion level.** Every `AC:` line sits at the same indent, the first one setting it
  (template: 2), with nothing but spaces after the `# `.
- **A one-token value takes one line** — a state, a date, an id, a URL, a route, a file name, a
  surface type. A further line under it is not read.
- **Nest only in a bullet-list field** (`business_value`, `preconditions`, `not_in_scope`,
  `rationale`, `notes`) — never in an id-list field (`user_stories`, `functionalities`,
  `feature_dependencies`, `parent`, `superseded_by`), which holds one id per entry.
- **A blank line is layout**: it ends nothing — not an item, not a key, not a criterion.
- Indent with spaces. Levels are relative, so no column is fixed, and a flat layout where
  items sit at their key's own indent stays valid.

## Out-of-scope routing

| Request | Use instead |
|---|---|
| Writing new Gherkin scenarios from scratch | `living-doc-scenario-creator` |
| Implementing step definition code | `gherkin-step` |
| Finding ACs with no scenario coverage | `living-doc-gap-finder` |
| Creating new User Story, Feature, or Functionality entities | `living-doc-create-user-story` / `living-doc-create-functionality` |
