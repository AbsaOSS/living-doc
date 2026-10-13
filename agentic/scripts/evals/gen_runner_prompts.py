"""Usage: gen_runner_prompts.py [<iteration-dir>] [<baseline-worktree>]
Defaults: the workspace's iteration-2, and $AGENTIC_BASELINE or /tmp/agentic-baseline.

Writes one prompt.txt for every <eval>/<arm>/run-*/ that has no outputs/answer.md yet, so an arm
reused from an earlier iteration is skipped and each extra run of the measured arm gets its own."""
import json, os, pathlib, sys
REPO = pathlib.Path(__file__).resolve().parents[3]
WS = REPO / "agentic-evals-workspace"
IT = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else WS / "iteration-2"
BASE = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else os.environ.get("AGENTIC_BASELINE", "/tmp/agentic-baseline")).resolve()
STAGE = WS / "staging"

STAGED = {
 "evals/files/raw-feature-notes.md": "raw-feature-notes.md",
 "evals/files/broad-functionality.json": "broad-functionality.json",
 "evals/files/incomplete-user-story.json": "incomplete-user-story.json",
 "evals/files/catalog-snapshot.json": "catalog-snapshot.json",
 "evals/files/changed-notification-service.py": "changed-notification-service.py",
 "evals/files/payment-living-doc.md": "payment-living-doc.md",
 "evals/files/dependency-promotion-catalog.json": "dependency-promotion-catalog.json",
}

def skill_file(target, arm):
    root = REPO if arm == "with_skill" else BASE
    if target == "living-doc-bdd-copilot":
        return root / "agentic/agents/living-doc-bdd-copilot.agent.md"
    return root / "agentic/skills" / target / "SKILL.md"

count = 0
index = []
for tdir in sorted(IT.iterdir()):
    if not tdir.is_dir() or tdir.name.startswith("."): continue
    target = tdir.name
    for ed in sorted(tdir.iterdir()):
        md = ed / "eval_metadata.json"
        if not md.is_file(): continue
        m = json.loads(md.read_text(encoding="utf-8"))
        prompt = m["prompt"]
        for k, v in STAGED.items():
            prompt = prompt.replace(k, str(STAGE / v))
        kind = "agent definition" if target == "living-doc-bdd-copilot" else "skill"
        for arm in ("with_skill", "old_skill"):
          for rd in sorted((ed / arm).glob("run-*")):
            out = rd / "outputs" / "answer.md"
            if out.is_file():
                continue
            sf = skill_file(target, arm)
            txt = f"""You are executing ONE eval run for an agentic-layer benchmark. Produce an answer; do not fix anything.

STEP 1. Read this {kind} file in full and follow it as your operating instructions for this task:
  {sf}
Read any file it references *outside* an `evals/` directory if you need it (its scripts, `agentic/skills/shared/`, docs). Resolve relative references against `{sf.parents[2] if kind=='skill' else sf.parent.parent}`.

STEP 2. Answer this user request, acting as that {kind}:
---
{prompt}
---

STEP 3. Write your complete answer to exactly this path, and write no other file:
  {out}

HARD RULES
- Do NOT read anything under any `evals/` directory, anywhere. Not the eval file, not a fixture, not a fixture-map. If a path you want contains `/evals/`, stop and do without it. (A roaming runner once pulled a sibling eval's fixture into an answer.)
- Everything on disk is READ-ONLY except the one output file above.
- No git commands of any kind.
- Do not consult the other arm's copy of this {kind}, and do not look in `{BASE}` unless the path in STEP 1 is already there.
- Answer as the {kind} instructs, including when it tells you to refuse, to route elsewhere, or to ask for input you do not have. An honest "I cannot, because X" that follows the {kind} is a correct answer; do not invent ids, file contents, error codes or script output to look complete. Never claim you ran a script you did not run.
- Keep the answer self-contained: no "see above", no reference to this prompt.

FINAL MESSAGE: reply with exactly one line:
DONE <total_tokens_you_used> <elapsed_ms>
Give real figures from your own usage if you can see them; if you genuinely cannot, write `DONE missing missing`."""
            pf = rd / "prompt.txt"
            pf.write_text(txt, encoding="utf-8")
            count += 1
            index.append(f"{target}\t{ed.name}\t{arm}/{rd.name}\t{pf}")

(IT.parent / "prompt-index.tsv").write_text("\n".join(index) + "\n", encoding="utf-8")
print(f"{count} prompt files written")
