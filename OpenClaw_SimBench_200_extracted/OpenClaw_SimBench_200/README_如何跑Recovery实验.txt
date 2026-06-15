1. 把本目录下 3 个 Python 脚本复制到你自己的 OpenClaw_SimBench_200/scripts/ 目录：
   - generate_recovery_tasks.py
   - run_simbench_v2.py
   - evaluate_metrics_v2.py

2. Windows 用户：把 run_recovery_experiments.bat 复制到 OpenClaw_SimBench_200 根目录，双击运行；
   或者在 cmd 中进入 OpenClaw_SimBench_200 后执行它。

3. macOS / Linux 用户：把 run_recovery_experiments.sh 复制到 OpenClaw_SimBench_200 根目录，
   然后执行：
   chmod +x run_recovery_experiments.sh
   ./run_recovery_experiments.sh

4. 主要输出文件：
   - data/tasks_recovery_120.jsonl
   - outputs/recovery_openclaw_full_metrics.json
   - outputs/recovery_openclaw_wo_retry_metrics.json
   - outputs/recovery_react_metrics.json
   - outputs/recovery_zero_shot_metrics.json

5. 论文里最关键看两项：
   - RRR：恢复成功率
   - RecoverySR：recovery 子实验中的任务成功率

6. 如果你只想先跑完整版和去掉 Retry 的对比，最少跑这两条：
   python scripts/run_simbench_v2.py --tasks data/tasks_recovery_120.jsonl --tools data/tools.json --method openclaw_wo_retry --output outputs/recovery_openclaw_wo_retry_results.jsonl
   python scripts/evaluate_metrics_v2.py --input outputs/recovery_openclaw_wo_retry_results.jsonl --output outputs/recovery_openclaw_wo_retry_metrics.json
   python scripts/run_simbench_v2.py --tasks data/tasks_recovery_120.jsonl --tools data/tools.json --method openclaw_full --output outputs/recovery_openclaw_full_results.jsonl
   python scripts/evaluate_metrics_v2.py --input outputs/recovery_openclaw_full_results.jsonl --output outputs/recovery_openclaw_full_metrics.json
