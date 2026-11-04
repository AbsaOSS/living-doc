# Error codes

## Purpose

This page tells you, for every code in `living-doc-utilities`' [Errors and warnings][ut-codes] registry, who raises
it, what it means for you and what to do. Each code's kind and the exact conditions that raise it are defined
there; this page says what they mean for you.

Read before: [Contracts](contracts.md) · Next: back to [Data flows](data-flows.md)

## Contents

- [Who raises a code](#who-raises-a-code)
- [Codes](#codes)

## Who raises a code

- `collector-gh`, `toolkit`, `generator-markdown`: that step, in its log when it fails, or as a warning in its file.
- `collector-gh`'s authoring warnings come from the header parsers it runs, which `living-doc-utilities` provides.
- every component: `living-doc-utilities`' reader and writer, through which every step reads and writes its files.
- planned: no shipped component raises it; the row names the planned component, mode or capability that will.
- The inner view of a document shows the collector warnings ([What was not loaded](rendering-rules.md#what-was-not-loaded)).

## Codes

| Code | Raised by | What it means for you | What to do |
|---|---|---|---|
| `INVALID_CONTRACT_ID` | every component | The step does not recognise the file's contract id, or that version of it, so it cannot read the file. | If the two `living-doc-utilities` versions the message names differ, pin actions released together, as the [example][example] does. Otherwise regenerate the file with the step that writes it instead of editing it. |
| `CONTRACT_MISMATCH` | `toolkit`, `generator-markdown` | The step was given a file of another contract, usually through a wrong path. | Point the input at the file this step reads ([Files][files]); given a collector output, `generator-markdown`'s message names the `toolkit` command that writes the file it reads. |
| `SCHEMA_VALIDATION_FAILED` | every component | The file names the right contract, but its content does not fit it. | If the two `living-doc-utilities` versions the message names differ, pin actions released together ([example][example]). Otherwise regenerate the file, and report the message to the component that wrote it if that fails again. |
| `MISSING_INPUT` | `toolkit` | A path the command was given points at no file. | Point `input`, and `tests-input` for `coverage-matrix`, at the files earlier steps wrote, and run those steps first ([`toolkit` inputs][tk-inputs], [Files][files]). |
| `UNKNOWN_PRODUCER` | `toolkit` | The file was written by a tool `toolkit` does not read from. | Give it the file `collector-gh` wrote ([Files][files]). |
| `PROJECT_MISMATCH` | `toolkit` `coverage-matrix` | The documentation and the tests belong to different projects. | Set the same `project-id` on every collector step ([`collector-gh` inputs][cgh-inputs], [Project id][pr-project-id]). |
| `MULTIPLE_DOCUMENTATION_SOURCES` | `toolkit` `coverage-matrix` | The command was given more than one documentation file. | Pass one, and collect every repository of the project in one `collector-gh` step ([`collector-gh` inputs][cgh-inputs], [One project, one pipeline, one documentation source][pr-one]). |
| `MIXED_DOCUMENTATION_SOURCES` | planned: `toolkit`, once it reads `doc-entities` | Documentation from an issue tracker and from source files would meet in one run. | Choose one documentation source for the project ([One project, one pipeline, one documentation source][pr-one]). |
| `DUPLICATE_ENTITY_ID` | `toolkit` `normalize-docs`, `coverage-matrix` | Two entities claim one id, so the documents cannot tell them apart. | Renumber all but one in their headers ([ID uniqueness][ids]). |
| `DUPLICATE_AC_ID` | `toolkit` `normalize-docs`, `coverage-matrix` | One entity has two criteria with the same id. | Renumber one of them in the entity's header ([ID uniqueness][ids]). |
| `FIELD_LOSS` | `toolkit` | `toolkit` lost data its input held: a defect in `toolkit`, not in your files. | Report it to [`living-doc-toolkit`](https://github.com/AbsaOSS/living-doc-toolkit/issues) with the input file and the message. |
| `PLANNED_AC_HAS_TESTS` | `toolkit` `coverage-matrix` | A test exists for a criterion its header still calls `planned`. | If the behaviour is built, update the criterion's state ([Acceptance Criterion][ac]); if not, the test is early and needs no change. |
| `IN_REVIEW_AC_HAS_TESTS` | `toolkit` `coverage-matrix` | A test exists for a criterion still `in_review`. | Set the criterion to `active` once its branch is accepted ([Acceptance Criterion][ac]). |
| `STALE_AC_REF` | `toolkit` `coverage-matrix` | A test's `@AC:` tag points at a criterion or value the documentation does not hold, so it covers nothing. | Correct the tag, or declare the value on its criterion ([Acceptance Criterion][ac], [AC variants][variants]). |
| `INVALID_CONFIGURATION` | `collector-gh` | An input of the `collector-gh` step is wrong, so nothing was collected. | Fix the input the log names ([`collector-gh` inputs][cgh-inputs]); leave `doc-issues` off, as GitHub issues are planned. |
| `SOURCE_UNAVAILABLE` | `collector-gh` | A repository path the step was given could not be read. | Check out the repository before the collector step, and give the path as an absolute directory ([`collector-gh` inputs][cgh-inputs]). Set `allow-partial` only if the document may go out without that source. |
| `EMPTY_SOURCE` | `collector-gh` | None of a repository entry's paths held anything the mode reads. | Point the entry's paths at the directories that hold the headers or scenarios, or remove the entry ([`collector-gh` inputs][cgh-inputs]). |
| `MALFORMED_AC` | `collector-gh` | A criterion or an `@AC:` tag you wrote is not in the document. | Write it in the criterion grammar ([Acceptance Criterion][ac]); the common slips are in [What it never guesses][never-guesses]. |
| `LEGACY_AC_STATE` | `collector-gh` | A criterion uses a state the format no longer has. | Replace it with one of the four states ([Acceptance Criterion][ac]). |
| `UNPARSED_AC_LINE` | `collector-gh` | A line in a criterion block is not in the document. | Write it as a bullet of the criterion, or name its variant in the description as `{<name>}` ([AC variants][variants]). |
| `UNPARSED_BULLET_LINE` | `collector-gh` | Text in a list field is not in the document. | Put it in a `- ` bullet on its own line under the key ([Indentation][indent]). |
| `MISINDENTED_LINE` | `collector-gh` | A list line's indent puts it at no level of its list, so it is lost. | Align it with an item of its list, or indent it deeper than the item it belongs to ([Indentation][indent]). |
| `UNKNOWN_SECTION` | planned: `collector-gh` mode `doc-issues`, `collector-ad` | A section of an issue body would not reach the document. | Use the headings of the [GitHub issue-body layout](authoring-formats.md#github-issue-body-layout). |
| `MISSING_ENTITY_ID` | `collector-gh` | A `.feature` file has no living-doc header, a PageObject's banner is not its first block comment, or a title has no id the collector can read, so no entity is read from that file. | Put the entity's id in the title, as its [header format][formats] shows ([What it never guesses][never-guesses]), and a PageObject's banner first ([Discovery][cgh-discovery]). Add a header to a `.feature` file that documents an entity, or keep one that does not out of `us-paths` and `func-paths` ([`collector-gh` inputs][cgh-inputs]). |
| `IGNORED_AUTHORED_KEY` | `collector-gh` | A key you wrote is not in the document: the header format has no such key for that entity. | Remove the key, or rename it to one the [header format][formats] has; a Feature's state comes from its Functionalities ([Feature](glossary.md#feature)). |
| `MALFORMED_STATUS` | `collector-gh` | The status you wrote is not one of the states, so it is not read. | Write one of the four states ([User Story](glossary.md#user-story-us), [Functionality](glossary.md#functionality-func)). |
| `MISSING_STATUS` | `collector-gh` | The User Story or Functionality has no status of its own. | Add a `status:` line to its header ([User Story](authoring-formats.md#1-user-story-in-a-gherkin-feature-file), [Functionality](authoring-formats.md#3-functionality-in-a-gherkin-feature-file)). |
| `STATUS_AC_MISMATCH` | `collector-gh` | The status you wrote contradicts the entity's own criteria. | Change the status, or the criteria's states, until they agree ([Acceptance Criterion][ac]). |
| `FEATURE_WITHOUT_FUNCTIONALITY` | `collector-gh` | A Feature has no Functionality in the run, so its state has nothing to come from. | Add the Functionalities that carry its behaviour, each with a `parent:` naming it ([Functionality](authoring-formats.md#3-functionality-in-a-gherkin-feature-file), [Feature](glossary.md#feature)); the message names the other choice. |
| `RELATION_MISMATCH` | `collector-gh` | Two headers disagree about how their entities relate. | Make a Functionality's `parent:` and its Feature's `functionalities` name each other, and correct the `feature_dependencies` the message names ([Required fields](authoring-formats.md#required-fields)). |
| `UNRESOLVED_RELATION` | `collector-gh` | A relation names an entity this run did not collect. | Correct the id, or add the path that holds that entity to the collector step ([`collector-gh` inputs][cgh-inputs]). |
| `RELATION_TYPE_MISMATCH` | `collector-gh` | A relation names an entity of the wrong type. | Name an entity of the type the field takes ([Required fields](authoring-formats.md#required-fields), [Relationship diagram](glossary.md#relationship-diagram)). |
| `NO_SOURCE_URL` | `collector-gh` | The document cannot link this file's entities and warnings back to the repository. | Scan a git checkout made by `actions/checkout` ([`collector-gh` prerequisites][cgh-prereq]). |
| `HTML_CONTENT_DROPPED` | planned: `collector-ad` | Part of a work item's formatting would not reach the document. | Simplify the work item's formatting ([Azure DevOps work items][ado]). |
| `DUPLICATE_AC_SOURCE` | planned: `collector-ad` | A work item would state one criterion in two places. | Keep each criterion in one place ([Azure DevOps work items][ado]). |
| `EXCLUDED_STATE` | planned: `collector-ad` | A work item's state would keep it out of the document. | If it belongs in the document, change its state, or the states the collector leaves out ([collector-ad](../projects/collector-ad.md)). |
| `AUTHORING_WARNING` | `collector-gh` | A line in a header is not in the document: no field reads it. | If it comes with a `MALFORMED_AC`, fix that criterion; otherwise move the line under a field the [header format][formats] has. |
| `AUTHORING_ERROR` | `collector-gh` | A header line breaks its format, an entity breaks its contract, or an entity or scenario repeats an id from another file, so that line or item is not read. | Fix what the message names: the header's [format][formats], a criterion id that is not its entity's ([Acceptance Criterion][ac]), or an entity id another file already uses ([ID uniqueness][ids]). For a repeated scenario, make sure no two repository entries reach the same file ([`collector-gh` inputs][cgh-inputs]). |
| `TEMPLATE_KEY_MISSING` | `generator-markdown` | A template needs data its input lacks: a defect in the generator, not in your files. | Report it to [`living-doc-generator-markdown`](https://github.com/AbsaOSS/living-doc-generator-markdown/issues) with the input file. |
| `URL_FETCH_REFUSED` | planned: `generator-pdf` | A PDF would miss an image or link from outside its template's directory. | Keep a custom template's images in its own directory ([generator-pdf](../projects/generator-pdf.md)). |

[ut-codes]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/errors.md#codes
[pr-one]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#one-project-one-pipeline-one-documentation-source
[pr-project-id]: https://github.com/AbsaOSS/living-doc-utilities/blob/master/docs/contracts/pipeline-rules.md#project-id
[cgh-inputs]: https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md#inputs
[cgh-prereq]: https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/docs/action.md#prerequisites
[cgh-discovery]: https://github.com/AbsaOSS/living-doc-collector-gh/blob/master/doc_source/README.md#discovery
[tk-inputs]: https://github.com/AbsaOSS/living-doc-toolkit/blob/master/docs/action.md#inputs
[example]: data-flows.md#example
[files]: data-flows.md#files
[ac]: glossary.md#acceptance-criterion-ac
[ids]: glossary.md#id-uniqueness
[variants]: authoring-formats.md#ac-variants
[indent]: authoring-formats.md#indentation
[formats]: authoring-formats.md
[never-guesses]: ../guides/authoring-documentation.md#what-it-never-guesses
[ado]: authoring-formats.md#azure-devops-work-items
