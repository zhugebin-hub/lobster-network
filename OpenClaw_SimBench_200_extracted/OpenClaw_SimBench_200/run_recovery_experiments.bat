@echo off
REM 在 OpenClaw_SimBench_200 根目录下运行
python -m pip install jsonschema

python scripts\generate_recovery_tasks.py --num_tasks 120 --output data\tasks_recovery_120.jsonl

python scripts\run_simbench_v2.py --tasks data\tasks_recovery_120.jsonl --tools data\tools.json --method zero_shot --output outputs\recovery_zero_shot_results.jsonl
python scripts\evaluate_metrics_v2.py --input outputs\recovery_zero_shot_results.jsonl --output outputs\recovery_zero_shot_metrics.json

python scripts\run_simbench_v2.py --tasks data\tasks_recovery_120.jsonl --tools data\tools.json --method react --output outputs\recovery_react_results.jsonl
python scripts\evaluate_metrics_v2.py --input outputs\recovery_react_results.jsonl --output outputs\recovery_react_metrics.json

python scripts\run_simbench_v2.py --tasks data\tasks_recovery_120.jsonl --tools data\tools.json --method openclaw_wo_validator --output outputs\recovery_openclaw_wo_validator_results.jsonl
python scripts\evaluate_metrics_v2.py --input outputs\recovery_openclaw_wo_validator_results.jsonl --output outputs\recovery_openclaw_wo_validator_metrics.json

python scripts\run_simbench_v2.py --tasks data\tasks_recovery_120.jsonl --tools data\tools.json --method openclaw_wo_retry --output outputs\recovery_openclaw_wo_retry_results.jsonl
python scripts\evaluate_metrics_v2.py --input outputs\recovery_openclaw_wo_retry_results.jsonl --output outputs\recovery_openclaw_wo_retry_metrics.json

python scripts\run_simbench_v2.py --tasks data\tasks_recovery_120.jsonl --tools data\tools.json --method openclaw_full --output outputs\recovery_openclaw_full_results.jsonl
python scripts\evaluate_metrics_v2.py --input outputs\recovery_openclaw_full_results.jsonl --output outputs\recovery_openclaw_full_metrics.json
