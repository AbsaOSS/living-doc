#!/bin/bash
# Serial trigger-eval driver. One skill at a time, --num-workers 1, nothing concurrent.
# Usage: run_triggers.sh [<skill> ...]     (default: all twelve, in the priority order below)
# Env:   TRIGGER_OUT    results dir (default: <workspace>/trigger-evals-2)
#        TRIGGER_PROJECT  empty project the queries run in (default: $TMPDIR/agentic-trigger-project)
#        SKILL_CREATOR  skill-creator skill dir (default: found under ~/.claude/plugins/marketplaces)
#        PYTHON         interpreter (default: the first of python3/python that runs — on Windows
#                       python3 can be a Microsoft Store stub)
REPO=$(cd "$(dirname "$0")/../../.." && { pwd -W 2>/dev/null || pwd; })
MP="$HOME/.claude/plugins/marketplaces"
SC=${SKILL_CREATOR:-$MP/claude-plugins-official/plugins/skill-creator/skills/skill-creator}
[ -d "$SC" ] || SC=$(ls -d "$MP"/*/plugins/skill-creator/skills/skill-creator 2>/dev/null | head -1)
OUT=${TRIGGER_OUT:-$REPO/agentic-evals-workspace/trigger-evals-2}
MODEL=claude-haiku-4-5-20251001
PY=$PYTHON
if [ -z "$PY" ]; then
  for c in python3 python; do "$c" -c 'import sys' 2>/dev/null && { PY=$c; break; }; done
fi
export PYTHONUTF8=1   # run_eval.py reads and writes text without an encoding
mkdir -p "$OUT"
# run_eval.py treats the nearest directory holding .claude/ above its cwd as the project, writes its
# temporary commands there, and runs `claude -p` in it. Started from the skill-creator directory that
# resolves to $HOME, so the user's home-project memory and settings leak in — a run once spent its
# first tool call reading MEMORY.md, which scores as a miss. An empty project keeps every query cold;
# it lives outside any repository, because Claude Code also reads a parent directory's setup.
ISO=${TRIGGER_PROJECT:-${TMPDIR:-/tmp}/agentic-trigger-project}
mkdir -p "$ISO/.claude/commands"
cd "$ISO" || exit 1
SKILLS=("$@")
# Priority order: the four the owner flagged as unsettled first.
[ ${#SKILLS[@]} -eq 0 ] && SKILLS=(
  living-doc-impact-analysis living-doc-pageobject-scan living-doc-scenario-creator living-doc-update
  bdd-maintain data-cy-instrument gherkin-living-doc-sync gherkin-step
  living-doc-create-feature living-doc-create-functionality living-doc-create-user-story living-doc-gap-finder)
for s in "${SKILLS[@]}"; do
  if [ -f "$OUT/$s.done" ]; then echo "SKIP $s (already done)"; continue; fi
  echo "=== START $s $(date +%H:%M:%S) ==="
  "$PY" "$REPO/agentic/scripts/evals/run_eval_compat.py" "$SC" \
    --eval-set "$REPO/agentic/skills/$s/evals/trigger-eval.json" \
    --skill-path "$REPO/agentic/skills/$s" \
    --model "$MODEL" \
    --runs-per-query 3 --num-workers 1 --timeout 120 --verbose \
    > "$OUT/$s.json" 2> "$OUT/$s.log"
  rc=$?
  echo "=== END $s rc=$rc $(date +%H:%M:%S) size=$(wc -c < "$OUT/$s.json") ==="
  [ $rc -eq 0 ] && touch "$OUT/$s.done"
done
echo "ALL TRIGGER RUNS FINISHED $(date +%H:%M:%S)"
