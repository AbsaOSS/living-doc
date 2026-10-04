## Overview

The canon now says where each part of a header starts and ends, and what the reader does with a line it cannot place. Until now it said only that indentation is significant. The rules it adds are the ones `living-doc-utilities` reads by, from its framing pass and its line accounting (`living-doc-utilities` #183, `P35-UT10`). The two must not diverge.

`docs/guides/living-doc-header-types.md` § Indentation gets a new block, *Where a part starts and ends*:

- **A key sits at the key level**, the indent of the header's first key. A line shaped `key:` any deeper is content, never a new key.
- **A header names its entity.** It exists only when its title carries the entity's id; without one, nothing in it is read or normalised, and the file is reported.
- **A blank line is layout**, with or without its comment marker. It ends no item, key or criterion.
- **A part ends where the next one starts.** A criterion ends at the next `AC:` header, at a key at the key level, or at a `# =====` rule. A rule inside the header is an optional end of a block, and the last rule ends the header. So a `notes:` written after the criteria is the entity's note, no longer dropped.
- **One criterion level.** In a `.feature` header every `AC:` line sits at the same indent, the first one's (template: 2). An `AC:` line elsewhere is text, and it is reported.
- **Every header line carries its marker** (`# `, ` * `). A line with text and no marker inside a header is not read and is reported as an error. Gherkin rejects such a line above `Feature:` anyway.
- **A value's type decides whether it may wrap.** A single-token key (state, date, id, URL, route, file name, surface type) takes one line, and a further line is an error. Text and id lists may wrap.
- **Recommended key order:** the template's, with `acceptance_criteria:` last. It is a recommendation only, because indentation decides.
- Every line the reader does not take into a field is reported, with its line number.

The level table marks that every criterion header sits at one level. The cross-reference header gains an optional **`notes`** field: notes about that page, kept with the page and its data and never merged into the parent Feature's notes. A cross-reference page is a part of its Feature with data of its own (route, owners, purpose, functionalities, now notes).

No example file changes. `tools/examples_check.py` and its tests pass unchanged.

## Release Notes

- The canon defines where each part of a header starts and ends: keys at the key level, blank lines as layout, one criterion level, and a `# =====` rule as an optional end of a block.
- A header line without its comment marker, and a second line under a single-value key, break the format and are reported.
- A cross-reference PageObject header may carry `notes:` about its own page; they stay with the page.

## Framework

- [x] Stays inside the frame (F1–F7)
- [ ] Bends frame row F_ — exception E_ added to `docs/introduction/principles.md` in this PR

F1 (entities and their header formats): the header format gains rules on where its parts start and end. No other row changes.
