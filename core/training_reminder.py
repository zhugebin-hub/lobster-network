#!/usr/bin/env python3
"""
Training Reminder - 小龙虾网络训练自动提醒系统
功能: 扫描训练任务定义与提交结果，识别逾期/未提交任务，通过CC广播发送提醒
作者: 诸葛马 (AI教练)
版本: 1.0

用法:
    # 检查提交状态
    python training_reminder.py check

    # 发送CC提醒给逾期学员
    python training_reminder.py remind

    # 生成 Markdown 汇总报告
    python training_reminder.py report

    # 指定训练天数
    python training_reminder.py check --day 4
"""

import json
import sys
import argparse
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# ============================================================
# 路径配置
# ============================================================

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))
SHARED_DIR = REPO_ROOT / ".shared"
TRAINING_DIR = SHARED_DIR / "training" / "go"

# 时区
CST = timezone(timedelta(hours=8))

# 活跃学员
ACTIVE_STUDENTS = ["qoder", "xiaochen", "zhuguxia", "xiaowei"]

# 教练
COACH = "zhugema"

# 任务文件命名模式: day*_*.json (位于 TRAINING_DIR 根)
# 提交目录: from-{student}/ 下包含 day*_result*.json 等提交文件

# 学员中文名称映射
STUDENT_NAMES = {
    "qoder": "qoder",
    "xiaochen": "小陈",
    "zhuguxia": "诸葛虾",
    "xiaowei": "小薇",
    "zhugema": "诸葛马",
}


# ============================================================
# 训练提醒主类
# ============================================================

class TrainingReminder:
    """训练自动提醒器

    扫描 .shared/training/go/ 中的任务定义和 from-*/ 中的提交结果，
    比较期望提交与实际提交，识别逾期/未提交任务，
    通过 cc_broadcast 模块发送 CC 提醒消息。
    """

    def __init__(self, training_dir=None, active_students=None, coach=None):
        """初始化提醒器

        Args:
            training_dir: 训练目录路径, 默认为 .shared/training/go/
            active_students: 活跃学员列表
            coach: 教练节点 ID
        """
        self.training_dir = Path(training_dir) if training_dir else TRAINING_DIR
        self.active_students = list(active_students) if active_students else list(ACTIVE_STUDENTS)
        self.coach = coach or COACH
        self._tasks = None
        self._submissions = None

    # ----------------------------------------------------------
    # 扫描任务定义
    # ----------------------------------------------------------

    def scan_tasks(self):
        """扫描训练目录中的任务定义文件 (day*_*.json)

        Returns:
            list[dict]: 找到的任务定义列表, 每条包含:
                - file: 文件路径
                - day: 训练天数 (int)
                - date: 任务日期 (str)
                - deadline: 截止时间 (datetime | None)
                - students: 学员任务配置 (dict)
                - raw: 原始 JSON 数据
        """
        tasks = []
        if not self.training_dir.exists():
            print(f"[WARN] 训练目录不存在: {self.training_dir}")
            return tasks

        for f in sorted(self.training_dir.glob("day*_*.json")):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    data = json.load(fh)
            except (json.JSONDecodeError, IOError) as e:
                print(f"[WARN] 无法解析任务文件 {f.name}: {e}")
                continue

            day = data.get("day")
            if day is None:
                # 尝试从文件名推断: day4_training_v3.json -> 4
                try:
                    day = int(f.stem.split("_")[0].replace("day", ""))
                except (ValueError, IndexError):
                    day = 0

            # 解析截止时间
            deadline = None
            deadline_str = data.get("deadline", "")
            if deadline_str:
                try:
                    deadline = datetime.strptime(deadline_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=CST)
                except ValueError:
                    print(f"[WARN] 无法解析截止时间 '{deadline_str}' in {f.name}")

            students = data.get("students", {})

            tasks.append({
                "file": f,
                "day": day,
                "date": data.get("date", ""),
                "deadline": deadline,
                "students": students,
                "raw": data,
            })

        self._tasks = tasks
        return tasks

    # ----------------------------------------------------------
    # 扫描提交结果
    # ----------------------------------------------------------

    def scan_submissions(self):
        """扫描 from-*/ 目录中的提交结果

        Returns:
            dict[str, dict]: 学员 -> {days: set[int], files: list[Path]}
                days: 已提交的训练天数集合
                files: 所有提交文件路径列表
        """
        submissions = {}

        for student in self.active_students:
            from_dir = self.training_dir / f"from-{student}"
            submitted_days = set()
            submitted_files = []

            if not from_dir.exists():
                submissions[student] = {"days": submitted_days, "files": submitted_files}
                continue

            for f in sorted(from_dir.iterdir()):
                if not f.is_file() or not f.suffix == ".json":
                    continue

                # 跳过非结果文件 (如 sync_v3_report.json, day4_xiaochen.json 任务副本)
                # 结果文件通常包含 "result" 在名称中
                name_lower = f.stem.lower()

                submitted_files.append(f)

                # 从文件名提取 day 编号
                day = self._extract_day_from_filename(f.name)
                if day is not None and "result" in name_lower:
                    submitted_days.add(day)
                elif day is not None:
                    # 也检查文件内容是否有 result 相关字段
                    try:
                        with open(f, "r", encoding="utf-8") as fh:
                            data = json.load(fh)
                        if data.get("type") in ("training_result", "submission") or "problems" in data and "reflection" in data:
                            submitted_days.add(day)
                    except (json.JSONDecodeError, IOError):
                        pass

            submissions[student] = {"days": submitted_days, "files": submitted_files}

        self._submissions = submissions
        return submissions

    # ----------------------------------------------------------
    # 查找逾期任务
    # ----------------------------------------------------------

    def find_overdue(self):
        """查找逾期/未提交的任务

        Returns:
            list[tuple]: 每条为 (student, day, deadline) 元组
                - student: 学员 ID (str)
                - day: 训练天数 (int)
                - deadline: 截止时间 (datetime | None)
        """
        if self._tasks is None:
            self.scan_tasks()
        if self._submissions is None:
            self.scan_submissions()

        overdue = []
        now = datetime.now(CST)

        for task in self._tasks:
            day = task["day"]
            deadline = task["deadline"]
            task_students = task["students"]

            for student in self.active_students:
                # 学员在此任务中有分配
                if student not in task_students:
                    continue

                # 检查是否已提交
                student_subs = self._submissions.get(student, {"days": set(), "files": []})
                if day in student_subs["days"]:
                    continue

                # 判断是否逾期: 截止时间已过, 或无截止时间但任务日期已过
                is_overdue = False
                if deadline and now > deadline:
                    is_overdue = True
                elif not deadline and task["date"]:
                    try:
                        task_date = datetime.strptime(task["date"], "%Y-%m-%d").replace(tzinfo=CST)
                        # 给一天时间, 次日 22:00 算逾期
                        implied_deadline = task_date + timedelta(hours=22)
                        if now > implied_deadline:
                            is_overdue = True
                    except ValueError:
                        # 无法判断, 保守地视为逾期
                        is_overdue = True
                elif not deadline:
                    # 没有截止时间也没有日期 -- 跳过
                    continue

                if is_overdue:
                    overdue.append((student, day, deadline))

        return overdue

    # ----------------------------------------------------------
    # 发送 CC 提醒
    # ----------------------------------------------------------

    def send_reminders(self, auto_cc=True):
        """向逾期学员发送 CC 提醒, 同时抄送教练

        Args:
            auto_cc: 是否真正发送 CC 消息 (False 则只打印不发送)

        Returns:
            list[dict]: 发送结果列表
        """
        overdue = self.find_overdue()
        if not overdue:
            print("[INFO] 无逾期任务, 无需发送提醒")
            return []

        # 按学员聚合
        student_overdue = {}  # student -> list of (day, deadline)
        for student, day, deadline in overdue:
            student_overdue.setdefault(student, []).append((day, deadline))

        results = []

        for student, days_info in student_overdue.items():
            name = STUDENT_NAMES.get(student, student)
            day_list = ", ".join(f"Day{d}" for d, _ in sorted(days_info))
            deadlines_str = ", ".join(
                dl.strftime("%Y-%m-%d %H:%M") if dl else "未设定"
                for _, dl in sorted(days_info)
            )

            subject = f"训练提醒: {day_list} 任务逾期"
            body = (
                f"{name} 你好,\n\n"
                f"以下训练任务已逾期, 请尽快完成并提交:\n"
                f"  逾期天数: {day_list}\n"
                f"  原始截止: {deadlines_str}\n\n"
                f"请将结果提交到 .shared/training/go/from-{student}/ 目录下。\n"
                f"如有疑问请联系教练 {STUDENT_NAMES.get(self.coach, self.coach)}。\n\n"
                f"-- 小龙虾网络训练提醒系统"
            )

            if auto_cc:
                try:
                    from core.cc_broadcast import send_cc
                    result = send_cc(
                        to_nodes=[student, self.coach],
                        subject=subject,
                        body=body,
                        category="training_report",
                        sender="qoder",
                        requires_ack=True,
                        git_push=False,
                    )
                    print(f"[CC] -> {student}, {self.coach}: {subject} (track: {result.get('tracking_id', '?')})")
                    results.append({"student": student, "status": "sent", "result": result})
                except ImportError:
                    print(f"[WARN] cc_broadcast 模块不可用, 跳过 CC 发送: {student}")
                    results.append({"student": student, "status": "import_error"})
                except Exception as e:
                    print(f"[ERROR] CC 发送失败 ({student}): {e}")
                    results.append({"student": student, "status": "error", "error": str(e)})
            else:
                print(f"[DRY-RUN] 将发送提醒给 {name} ({student}): {subject}")
                results.append({"student": student, "status": "dry_run"})

        return results

    # ----------------------------------------------------------
    # 生成报告
    # ----------------------------------------------------------

    def generate_report(self):
        """生成 Markdown 格式的汇总报告

        Returns:
            str: Markdown 报告内容
        """
        if self._tasks is None:
            self.scan_tasks()
        if self._submissions is None:
            self.scan_submissions()

        overdue = self.find_overdue()
        now = datetime.now(CST)

        lines = []
        lines.append("# 小龙虾网络 - 训练提交状态报告")
        lines.append("")
        lines.append(f"**生成时间**: {now.strftime('%Y-%m-%d %H:%M:%S')} (CST)")
        lines.append(f"**训练目录**: `{self.training_dir}`")
        lines.append("")

        # --- 任务概览 ---
        lines.append("## 任务定义")
        lines.append("")
        if self._tasks:
            lines.append("| 文件 | Day | 日期 | 截止时间 | 学员数 |")
            lines.append("|------|-----|------|----------|--------|")
            for task in self._tasks:
                dl = task["deadline"].strftime("%Y-%m-%d %H:%M") if task["deadline"] else "未设定"
                n_students = len(task["students"])
                lines.append(
                    f"| {task['file'].name} | Day{task['day']} | {task['date']} | {dl} | {n_students} |"
                )
        else:
            lines.append("*未找到任务定义文件*")
        lines.append("")

        # --- 学员提交状态 ---
        lines.append("## 学员提交状态")
        lines.append("")
        lines.append("| 学员 | 已提交天数 | 提交文件数 | 状态 |")
        lines.append("|------|-----------|-----------|------|")

        overdue_by_student = {}
        for student, day, deadline in overdue:
            overdue_by_student.setdefault(student, []).append(day)

        for student in self.active_students:
            name = STUDENT_NAMES.get(student, student)
            subs = self._submissions.get(student, {"days": set(), "files": []})
            days_str = ", ".join(f"Day{d}" for d in sorted(subs["days"])) or "-"
            file_count = len(subs["files"])

            if student in overdue_by_student:
                overdue_days = ", ".join(f"Day{d}" for d in sorted(overdue_by_student[student]))
                status = f"**逾期**: {overdue_days}"
            else:
                status = "正常"

            lines.append(f"| {name} ({student}) | {days_str} | {file_count} | {status} |")

        lines.append("")

        # --- 逾期详情 ---
        lines.append("## 逾期任务详情")
        lines.append("")
        if overdue:
            for student, day, deadline in overdue:
                name = STUDENT_NAMES.get(student, student)
                dl_str = deadline.strftime("%Y-%m-%d %H:%M") if deadline else "未设定"
                hours_overdue = ""
                if deadline:
                    delta = now - deadline
                    total_hours = delta.total_seconds() / 3600
                    if total_hours > 0:
                        hours_overdue = f" (逾期 {total_hours:.1f} 小时)"

                lines.append(f"- **{name}** ({student}): Day{day} -- 截止 {dl_str}{hours_overdue}")
        else:
            lines.append("*无逾期任务, 所有学员均已按时提交。*")

        lines.append("")

        # --- 目录结构 ---
        lines.append("## 目录结构")
        lines.append("")
        if self.training_dir.exists():
            for item in sorted(self.training_dir.iterdir()):
                if item.is_dir():
                    n_files = len(list(item.iterdir()))
                    lines.append(f"- `{item.name}/` ({n_files} files)")
                elif item.suffix == ".json":
                    lines.append(f"- `{item.name}`")
        else:
            lines.append(f"*目录不存在: `{self.training_dir}`*")

        lines.append("")
        lines.append("---")
        lines.append(f"*由 training_reminder.py 自动生成*")

        return "\n".join(lines)

    # ----------------------------------------------------------
    # 辅助方法
    # ----------------------------------------------------------

    @staticmethod
    def _extract_day_from_filename(filename):
        """从文件名中提取 day 编号

        支持的模式:
            day2_result.json -> 2
            day3_result_xiaochen.json -> 3
            day4_qoder.json -> 4
            day4_result.json -> 4

        Args:
            filename: 文件名 (str)

        Returns:
            int | None: day 编号, 无法解析时返回 None
        """
        name = filename.lower()
        if "day" not in name:
            return None
        try:
            # 找到 "day" 后面的数字
            idx = name.index("day") + 3
            digits = []
            while idx < len(name) and name[idx].isdigit():
                digits.append(name[idx])
                idx += 1
            if digits:
                return int("".join(digits))
        except (ValueError, IndexError):
            pass
        return None


# ============================================================
# 命令行接口
# ============================================================

def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="小龙虾网络 - 训练自动提醒系统",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例:\n"
            "  python training_reminder.py check          # 检查提交状态\n"
            "  python training_reminder.py check --day 4  # 检查 Day4 状态\n"
            "  python training_reminder.py remind         # 发送 CC 提醒\n"
            "  python training_reminder.py remind --dry-run  # 预览提醒(不发送)\n"
            "  python training_reminder.py report         # 生成报告\n"
        ),
    )
    sub = parser.add_subparsers(dest="command", help="可用命令")

    # check
    p_check = sub.add_parser("check", help="检查学员提交状态")
    p_check.add_argument("--day", type=int, default=None, help="只检查指定天数")

    # remind
    p_remind = sub.add_parser("remind", help="向逾期学员发送 CC 提醒")
    p_remind.add_argument("--dry-run", action="store_true", help="预览提醒内容, 不实际发送")

    # report
    p_report = sub.add_parser("report", help="生成 Markdown 汇总报告")
    p_report.add_argument("--output", "-o", type=str, default=None, help="输出文件路径 (默认打印到 stdout)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    reminder = TrainingReminder()

    if args.command == "check":
        reminder.scan_tasks()
        reminder.scan_submissions()

        # 如果指定了 day, 过滤只保留该 day 的任务
        if args.day is not None:
            reminder._tasks = [t for t in reminder._tasks if t["day"] == args.day]

        overdue = reminder.find_overdue()

        print(f"\n{'=' * 60}")
        print(f"  小龙虾网络 - 训练提交状态检查")
        print(f"  时间: {datetime.now(CST).strftime('%Y-%m-%d %H:%M:%S')} CST")
        print(f"{'=' * 60}\n")

        # 任务概览
        print(f"[任务定义] 共 {len(reminder._tasks)} 个任务文件")
        for task in reminder._tasks:
            dl = task["deadline"].strftime("%Y-%m-%d %H:%M") if task["deadline"] else "未设定"
            students_list = ", ".join(task["students"].keys())
            print(f"  Day{task['day']} ({task['date']}) | 截止: {dl} | 学员: {students_list}")

        print()

        # 提交状态
        print("[提交状态]")
        for student in reminder.active_students:
            name = STUDENT_NAMES.get(student, student)
            subs = reminder._submissions.get(student, {"days": set(), "files": []})
            days_display = ", ".join(f"Day{d}" for d in sorted(subs["days"])) or "(无)"
            print(f"  {name:8s} ({student}): 已提交 {days_display}")

        print()

        # 逾期
        if overdue:
            print(f"[逾期] 共 {len(overdue)} 项逾期:")
            for student, day, deadline in overdue:
                name = STUDENT_NAMES.get(student, student)
                dl = deadline.strftime("%Y-%m-%d %H:%M") if deadline else "未设定"
                print(f"  !! {name} ({student}) - Day{day} 截止: {dl}")
        else:
            print("[OK] 无逾期任务")

        print()

    elif args.command == "remind":
        auto_cc = not args.dry_run
        results = reminder.send_reminders(auto_cc=auto_cc)

        if not results:
            print("\n[INFO] 无逾期学员, 未发送提醒")
        else:
            sent = sum(1 for r in results if r["status"] == "sent")
            dry = sum(1 for r in results if r["status"] == "dry_run")
            errors = sum(1 for r in results if r["status"] in ("error", "import_error"))
            print(f"\n[汇总] 发送: {sent}, 预览: {dry}, 失败: {errors}")

    elif args.command == "report":
        report = reminder.generate_report()

        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)
            print(f"[OK] 报告已写入: {output_path}")
        else:
            print(report)


if __name__ == "__main__":
    main()
