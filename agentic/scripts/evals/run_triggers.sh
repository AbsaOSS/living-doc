#!/bin/bash
# Serial trigger-eval driver. One skill at a time, --num-workers 1, nothing concurrent.
REPO=/Users/admin/repos/AbsaOSS/living-doc
SC=/Users/admin/.claude/plugins/marketplaces/claude-plugins-official/plugins/skill-creator/skills/skill-creator
OUT=$REPO/agentic-evals-workspace/trigger-evals-2
MODEL=claude-haiku-4-5-20251001
cd "$SC" || exit 1
# Priority order: the four the owner flagged as unsettled first.
for s in living-doc-impact-analysis living-doc-pageobject-scan living-doc-scenario-creator living-doc-update \
         bdd-maintain data-cy-instrument gherkin-living-doc-sync gherkin-step \
         living-doc-create-feature living-doc-create-functionality living-doc-create-user-story living-doc-gap-finder; do
  if [ -f "$OUT/$s.done" ]; then echo "SKIP $s (already done)"; continue; fi
  echo "=== START $s $(date +%H:%M:%S) ==="
  python3 -m scripts.run_eval \
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
