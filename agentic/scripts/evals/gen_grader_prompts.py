"""Usage: gen_grader_prompts.py [<iteration-dir>] [<target> ...]  (default: the workspace's iteration-2, all targets)"""
import json, pathlib, sys
REPO = pathlib.Path(__file__).resolve().parents[3]
IT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else REPO / "agentic-evals-workspace" / "iteration-2"
ONLY = set(sys.argv[2:])
for tdir in sorted(IT.iterdir()):
    if not tdir.is_dir() or tdir.name.startswith("."): continue
    if ONLY and tdir.name not in ONLY: continue
    evals = sorted([d for d in tdir.iterdir() if (d/"eval_metadata.json").is_file()],
                   key=lambda d: json.loads((d/"eval_metadata.json").read_text(encoding="utf-8"))["eval_id"])
    lines = []
    for ed in evals:
        m = json.loads((ed/"eval_metadata.json").read_text(encoding="utf-8"))
        runs = ", ".join(str(r.relative_to(ed)).replace("\\", "/") for r in sorted(ed.glob("*/run-*")) if (r / "outputs" / "answer.md").is_file())
        req = f"; requires: {', '.join(m['requires'])}" if m.get("requires") else ""
        lines.append(f"  - {ed.name}  (eval_id {m['eval_id']}, {len(m['assertions'])} assertions; runs: {runs}{req})")
    listing = "\n".join(lines)
    txt = f"""You are the GRADER for one target of an agentic-layer benchmark. You judge; you do not fix, edit or rerun anything.

TARGET: {tdir.name}
TARGET DIR: {tdir}

Each eval directory below contains `eval_metadata.json` (the prompt, the expected_output, and an `assertions` array) and two arms, `with_skill/` and `old_skill/`, each holding one or more runs `run-<k>/outputs/answer.md`. The runs present are listed per eval.

{listing}

FOR EVERY eval directory AND EVERY listed run, write:
  <eval_dir>/<arm>/run-<k>/grading.json

with exactly this shape — these field names are load-bearing, anything else renders blank:

{{
  "eval_id": <int>,
  "configuration": "<with_skill|old_skill>",
  "expectations": [
    {{"text": "<the assertion verbatim from eval_metadata.json assertions[]>",
      "passed": true|false,
      "evidence": "<a short quote from answer.md that settles it, or why nothing in the answer satisfies it>"}}
  ]
}}

One entry per assertion, in the same order, with `text` copied verbatim. Do not add, merge or reword assertions.

GRADING RULES (these come from a protocol that was paid for by wrong numbers last time — follow them over your instincts):
1. **Grade against the assertion as written.** Do not credit an answer for something it did not say. Do not credit a near-miss because the answer is "obviously competent".
2. **Do not reward guessing.** If an assertion can only be satisfied by inventing an entity id, a file's contents, an error code or script output that the prompt never supplied, and the answer honestly refuses or asks for it instead — mark the assertion `failed`, but ALSO record it in the findings list below as a suspect assertion with the reason. An honest refusal losing to a confident fabrication is an eval defect, not a skill defect.
3. **"Ran: <script>" claims.** If an answer claims to have run a script, check whether it could have. A claimed run with fabricated output is a defect even if the assertion rewards it; note it in the findings.
4. **Cannot discriminate.** An eval listed with `requires:` names what it needs and the runs did not have; expect it here. If both arms hard-stop identically because a live service, an MCP server or a project fixture is absent, grade them honestly (usually both fail) and record the eval in the findings as NON-DISCRIMINATING — it measures the environment, not the target.
5. **Passed but unreliable.** An assertion satisfied by a schema-shaped example from an answer that did no real work is a gap. Grade it as the text requires, then flag it in the findings.

AFTER grading, write a findings file at {tdir}/GRADER-NOTES.md containing:
  - a markdown table: eval_id | assertions | with_skill passed | old_skill passed | one-line note
  - a section "Suspect assertions" — every assertion you think is wrong rather than the target, each with `file:line` into {tdir.parent.parent.parent}/agentic/skills/{tdir.name}/evals/evals.json (or agentic/agents/evals/<agent>/evals.json for the agent target) and the reason
  - a section "Candidate target defects" — real problems in the SKILL.md / agent file, each with a `file:line` citation you have actually opened and confirmed. If you cannot confirm it in the file, label it UNVERIFIED and say what would settle it.
  - a section "Non-discriminating evals" — ids and why
  - a section "Arm comparison" — every eval where with_skill scored BELOW old_skill. For each, read the assertion first and say whether it is a genuine regression or an assertion that rewards guessing.

HARD RULES
- Read-only everywhere except the grading.json files and GRADER-NOTES.md you write.
- No git commands.
- Do NOT edit any SKILL.md, agent file or eval file. You report; you do not fix.
- Do not rerun any eval.
- You MAY read the eval files and the SKILL.md / agent file — you are the grader, the no-evals rule applied to the runners, not to you.

FINAL MESSAGE: a compact summary only — target name, per-arm totals (assertions passed / assertions graded for each arm), the count of suspect assertions, the count of non-discriminating evals, and the ids where with_skill < old_skill. Under 25 lines. Do not paste the notes file."""
    (tdir/"grader-prompt.txt").write_text(txt, encoding="utf-8")
    print(f"{tdir.name}: {len(evals)} evals")
