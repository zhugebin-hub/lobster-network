#!/usr/bin/env bash
set -e

python -m pip install jsonschema

python scripts/generate_recovery_tasks.py --num_tasks 120 --output data/tasks_recovery_120.jsonl

for method in zero_shot react openclaw_wo_validator openclaw_wo_retry openclaw_full; do
  python scripts/run_simbench_v2.py \
    --tasks data/tasks_recovery_120.jsonl \
    --tools data/tools.json \
    --method "$method" \
    --output "outputs/recovery_${method}_results.jsonl"

  python scripts/evaluate_metrics_v2.py \
    --input "outputs/recovery_${method}_results.jsonl" \
    --output "outputs/recovery_${method}_metrics.json"
done
