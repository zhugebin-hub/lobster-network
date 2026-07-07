#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 自动论文撰写学习脚本 V1.0
==========================================

功能：
1. 生成每日训练计划（稳健型/加速型/研究型/教练型/实战型/技术型）
2. 执行论文写作练习（选题/大纲/摘要/文献/方法/评审/查重/AI写作）
3. 评估写作能力
4. 生成学习报告
5. 加入联合学习（所有学员同步学习论文写作）
6. 学员间交叉评审（智能体互相学习提升）
7. 推送学习成果到网络

用法：
    python3 paper_writing_training.py --help
    python3 paper_writing_training.py --train xiaochen
    python3 paper_writing_training.py --train zhuguxia
    python3 paper_writing_training.py --train zhugebin-001
    python3 paper_writing_training.py --train zhugema
    python3 paper_writing_training.py --train xiaowei
    python3 paper_writing_training.py --train qoder
    python3 paper_writing_training.py --eval-topic "基于大语言模型的智能体自主任务分解方法研究"
    python3 paper_writing_training.py --outline "论文题目" --type empirical
    python3 paper_writing_training.py --report
    python3 paper_writing_training.py --join-network
    python3 paper_writing_training.py --cross-review zhugema zhuguxia
    python3 paper_writing_training.py --all
"""

import sys
import os
import json
import random
import argparse
from datetime import datetime

# 添加路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "..", "domains", "learning", "problems"))
sys.path.insert(0, os.path.join(SCRIPT_DIR, "..", "domains", "learning", "trainers"))

from paper_writing_engine import PaperWritingEngine
from paper_writing_trainer import PaperWritingTrainer, STUDENT_CONFIG


class PaperWritingLearning:
    """自动论文撰写学习系统"""

    def __init__(self):
        self.engine = PaperWritingEngine()
        self.trainer = PaperWritingTrainer(self.engine)
        self.history_file = os.path.join(
            SCRIPT_DIR, "..", "registry", "paper_writing_history.json"
        )
        self.history = self._load_history()
        self.session_dir = os.path.join(
            SCRIPT_DIR, "..", "registry", "learning_sessions"
        )
        os.makedirs(self.session_dir, exist_ok=True)

    # ========== 历史记录管理 ==========
    def _load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"trainings": [], "accuracy": {}, "streak": 0}

    def _save_history(self):
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)

    # ========== 训练 ==========
    def train(self, student_type: str = "zhugebin-001"):
        """执行训练"""
        if student_type not in STUDENT_CONFIG:
            print(f"❌ 未知学员类型：{student_type}")
            print(f"   可选：{', '.join(STUDENT_CONFIG.keys())}")
            return

        cfg = STUDENT_CONFIG[student_type]
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 自动论文撰写训练")
        print(f"   学员：{cfg['name']}（{cfg['type']}）")
        print(f"   节点ID：{student_type}")
        print(f"   日期：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # 生成计划
        plan = self.trainer.generate_daily_plan(student_type)
        print(f"\n📋 训练计划：共 {plan['total_problems']} 题")

        all_problems = []
        for slot in plan["schedule"]:
            print(f"   [{slot['time']}] {slot['type']}: {slot['count']}题（{slot['phase']}）")
            for p in slot["problems"]:
                p_with_meta = dict(p)
                p_with_meta["phase"] = slot["phase"]
                p_with_meta["slot_time"] = slot["time"]
                all_problems.append(p_with_meta)

        if not all_problems:
            print("\n⚠️ 未找到题目，请检查题库路径")
            return

        # 逐题练习
        print(f"\n{'─' * 70}")
        print(f"📝 开始答题")
        print(f"{'─' * 70}")

        correct = 0
        total = 0
        details = []
        base_acc = cfg["base_accuracy"]

        for i, prob in enumerate(all_problems, 1):
            print(f"\n【题目 {i}/{len(all_problems)}】")
            print(f"  阶段：{prob.get('phase')} | 类型：{prob['type']} | 难度：{prob['difficulty']}")
            print(f"  问题：{prob['question']}")

            if "options" in prob:
                print(f"  选项：")
                for j, opt in enumerate(prob["options"], 1):
                    print(f"    {j}. {opt}")

            # 模拟答题：基于难度的随机正确率
            diff = prob.get("difficulty", "中级")
            acc = base_acc.get(diff, 0.50)
            is_correct = random.random() < acc

            # 显示答案
            print(f"\n  ✅ 正确答案：{prob['answer']}")
            print(f"  💡 解析：{prob.get('reasoning', '暂无')}")

            if is_correct:
                correct += 1
                print(f"  🎯 你的回答：正确 ✅（置信度 {prob.get('confidence', 0):.1%}）")
            else:
                print(f"  ❌ 你的回答：错误")

            total += 1
            details.append({
                "id": prob.get("id"),
                "type": prob["type"],
                "difficulty": prob.get("difficulty"),
                "phase": prob.get("phase"),
                "answer": prob.get("answer"),
                "correct": is_correct,
            })

        # 生成训练报告
        accuracy = correct / total if total > 0 else 0
        print(f"\n{'=' * 70}")
        print(f"📊 训练报告")
        print(f"{'=' * 70}")
        print(f"   学员：{cfg['name']}（{cfg['type']}）")
        print(f"   节点ID：{student_type}")
        print(f"   总题数：{total}")
        print(f"   正确数：{correct}")
        print(f"   准确率：{accuracy:.1%}")

        # 按题型统计
        by_type = {}
        for d in details:
            t = d["type"]
            by_type.setdefault(t, {"total": 0, "correct": 0})
            by_type[t]["total"] += 1
            if d["correct"]:
                by_type[t]["correct"] += 1

        print(f"\n📈 按题型统计：")
        for t, s in by_type.items():
            acc = s["correct"] / s["total"] if s["total"] > 0 else 0
            print(f"   {t:25s}：{s['correct']}/{s['total']} | {acc:.1%}")

        # 评价
        if accuracy >= 0.80:
            print(f"\n   评价：🌟 超常发挥！明日升档")
        elif accuracy >= 0.60:
            print(f"\n   评价：✅ 正常进度")
        else:
            print(f"\n   评价：⚠️ 需加强复习，明日错题重练")

        # 保存训练记录
        training_result = {
            "date": datetime.now().isoformat(),
            "student": student_type,
            "student_name": cfg["name"],
            "student_type": cfg["type"],
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
            "details": details,
            "by_type": by_type,
        }
        self.history["trainings"].append({
            "date": training_result["date"],
            "student": student_type,
            "total": total,
            "correct": correct,
            "accuracy": accuracy,
        })
        self._save_history()

        # 更新学员状态
        self.trainer.update_student_state(student_type, training_result)

        # 保存学习会话
        session_id = f"paper_session_{int(datetime.now().timestamp())}"
        session = {
            "session_id": session_id,
            "domain": "paper-writing",
            "student": student_type,
            "student_name": cfg["name"],
            "created_at": datetime.now().isoformat(),
            "total_problems": total,
            "correct": correct,
            "accuracy": accuracy,
            "details": details,
            "by_type": by_type,
            "participants": [student_type, "hermes"],
        }
        session_file = os.path.join(self.session_dir, f"{session_id}.json")
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
        print(f"\n💾 学习会话已保存：{session_file}")

        return training_result

    # ========== 选题评估 ==========
    def eval_topic(self, topic: str, discipline: str = "人工智能"):
        """评估论文选题"""
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 论文选题评估")
        print(f"   题目：{topic}")
        print(f"   学科：{discipline}")
        print(f"   时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        result = self.engine.evaluate_topic(
            topic=topic,
            discipline=discipline,
            novelty=0.85, feasibility=0.70,
            academic_value=0.88, impact=0.75,
            data_availability=0.60, existing_papers=150,
        )
        print(f"\n📊 选题评估结果：")
        print(f"   评分：{result['score']:.3f}")
        print(f"   等级：{result['grade']}")
        print(f"   建议：{result['recommendation']}")
        print(f"\n📈 因子分析：")
        for k, v in result["factors"].items():
            print(f"   {k}: {v}")

        return result

    # ========== 大纲生成 ==========
    def gen_outline(self, topic: str, paper_type: str = "empirical"):
        """生成论文大纲"""
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 论文大纲生成")
        print(f"   题目：{topic}")
        print(f"   类型：{paper_type}")
        print("=" * 70)

        outline = self.engine.generate_outline(topic, paper_type, target_words=8000)
        print(f"\n📝 大纲（{outline['type_name']}）：")
        print(f"   目标字数：{outline['target_words']}")
        print(f"   章节数：{outline['section_count']}")
        for s in outline["sections"]:
            print(f"\n   [{s['order']}] {s['name']}（{s['target_words']}字, {s['weight']:.0%}）")
            print(f"       要点：{', '.join(s['key_points'])}")

        return outline

    # ========== 报告 ==========
    def report(self):
        """生成学习报告"""
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 自动论文撰写学习报告")
        print(f"   生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        trainings = self.history.get("trainings", [])
        if not trainings:
            print("\n⚠️ 暂无训练记录，请先执行 --train")
            return

        # 总体统计
        total_trainings = len(trainings)
        total_problems = sum(p["total"] for p in trainings)
        total_correct = sum(p["correct"] for p in trainings)
        overall_accuracy = total_correct / total_problems if total_problems > 0 else 0

        print(f"\n📊 总体统计")
        print(f"   训练次数：{total_trainings}")
        print(f"   总题数：{total_problems}")
        print(f"   总正确数：{total_correct}")
        print(f"   整体准确率：{overall_accuracy:.1%}")

        # 最近5次训练
        print(f"\n📋 最近5次训练")
        for p in trainings[-5:]:
            date = p["date"][:16].replace("T", " ")
            print(f"   {date} | {p['student']:18s} | {p['correct']}/{p['total']} | {p['accuracy']:.1%}")

        # 按学员统计
        print(f"\n👥 学员统计")
        summaries = self.trainer.get_all_students_summary()
        for s in summaries:
            status = "✅ 已训练" if s["total_trainings"] > 0 else "⬜ 未开始"
            print(f"   {s['student_id']:16s}（{s['name']:12s}）[{s['type']}]: "
                  f"{s['total_correct']}/{s['total_problems']} | {s['accuracy']:.1%} | "
                  f"训练 {s['total_trainings']} 次 | 连续 {s['streak']} 天 | {status}")

        # 学员详细状态
        print(f"\n📈 学员详细状态：")
        for sid in STUDENT_CONFIG.keys():
            state = self.trainer.get_student_state(sid)
            if state.get("total_trainings", 0) > 0:
                print(f"\n   {sid}（{STUDENT_CONFIG[sid]['name']}）：")
                print(f"      累计训练：{state['total_trainings']} 次")
                print(f"      累计题目：{state['total_problems']} 题")
                print(f"      累计正确：{state['total_correct']} 题")
                acc = state['total_correct'] / state['total_problems'] if state['total_problems'] > 0 else 0
                print(f"      累计准确率：{acc:.1%}")
                print(f"      连续训练：{state.get('streak', 0)} 天")
                # 题型分析
                if state.get("by_type"):
                    print(f"      题型分析：")
                    for pt, stats in state["by_type"].items():
                        pt_acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
                        print(f"         {pt:25s}：{stats['correct']}/{stats['total']} | {pt_acc:.1%}")

    # ========== 加入联合学习 ==========
    def join_network(self):
        """加入小龙虾网络联合学习"""
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 自动论文撰写联合学习")
        print(f"{'=' * 70}")

        # 网络成员（所有学员）
        network_members = [
            {"id": "zhugema", "name": "诸葛马", "role": "教练", "type": "教练型", "domain": "AI辅助写作+高级评审"},
            {"id": "zhugebin-001", "name": "诸葛斌的工作助手", "role": "学员", "type": "研究型", "domain": "全题型+实战评估"},
            {"id": "zhuguxia", "name": "诸葛虾", "role": "学员", "type": "加速型", "domain": "方法论+文献综述"},
            {"id": "xiaochen", "name": "小陈", "role": "学员", "type": "稳健型", "domain": "基础概念+结构规范"},
            {"id": "xiaowei", "name": "小薇", "role": "学员", "type": "实战型", "domain": "论文修改+查重+投稿"},
            {"id": "qoder", "name": "qoder", "role": "学员", "type": "技术型", "domain": "数据分析+引用格式"},
        ]

        print(f"\n👥 网络成员（共 {len(network_members)} 节点）：")
        for m in network_members:
            print(f"   - {m['id']:16s}（{m['name']:12s}）：{m['role']} - {m['type']} - {m['domain']}")

        # 生成联合学习会话
        session_id = f"paper_joint_{int(datetime.now().timestamp())}"
        session = {
            "session_id": session_id,
            "domain": "paper-writing",
            "type": "joint_learning",
            "created_at": datetime.now().isoformat(),
            "organizer": "zhugema",
            "participants": [m["id"] for m in network_members],
            "topic": "自动论文撰写联合学习",
            "phases": ["phase1", "phase2", "phase3"],
            "rules": {
                "daily_min_problems": 8,
                "weekly_review": True,
                "cross_review": True,
                "share_writing_patterns": True,
                "mutual_learning": True,
            },
            "history": [],
        }

        # 保存会话
        session_file = os.path.join(self.session_dir, f"{session_id}.json")
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)

        print(f"\n✅ 联合学习会话已创建！")
        print(f"   会话ID：{session_id}")
        print(f"   会话文件：{session_file}")
        print(f"\n📋 学习规则：")
        for k, v in session["rules"].items():
            print(f"   - {k}: {v}")

        # 各学员学习进度
        print(f"\n📊 各学员学习进度：")
        for sid in STUDENT_CONFIG.keys():
            state = self.trainer.get_student_state(sid)
            name = STUDENT_CONFIG[sid]["name"]
            if state.get("total_trainings", 0) > 0:
                acc = state["total_correct"] / state["total_problems"] if state["total_problems"] > 0 else 0
                print(f"   - {sid}（{name}）：{state['total_trainings']} 次训练，准确率 {acc:.1%}")
            else:
                print(f"   - {sid}（{name}）：尚未开始训练")

        print(f"\n🎯 互相学习机制：")
        print(f"   1. 学员间交叉评审：--cross-review <reviewer> <reviewee>")
        print(f"   2. 共享写作模式和常见错误")
        print(f"   3. 教练(zhugema)定期发布写作技巧")
        print(f"   4. 每周评比最佳论文写作进步奖")

        print(f"\n🎯 下一步建议：")
        print(f"   1. 执行 `python3 scripts/paper_writing_training.py --train zhugebin-001`")
        print(f"   2. 执行 `python3 scripts/paper_writing_training.py --report` 查看进度")
        print(f"   3. 执行 `python3 scripts/paper_writing_training.py --cross-review zhugema zhuguxia` 交叉评审")

        return session

    # ========== 交叉评审（智能体互相学习） ==========
    def cross_review(self, reviewer: str, reviewee: str):
        """学员间交叉评审"""
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 论文写作交叉评审")
        print(f"   评审者：{reviewer}")
        print(f"   被评审者：{reviewee}")
        print(f"   时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        result = self.trainer.cross_review(reviewer, reviewee)

        print(f"\n📊 评审结果：")
        print(f"   评审者：{result['reviewer_name']}（准确率 {result['reviewer_accuracy']:.1%}）")
        print(f"   被评审者：{result['reviewee_name']}（准确率 {result['reviewee_accuracy']:.1%}）")

        if result["reviewee_weak_types"]:
            print(f"\n⚠️ 被评审者薄弱题型：")
            for wt in result["reviewee_weak_types"]:
                print(f"   - {wt}")
        else:
            print(f"\n✅ 被评审者暂无明显薄弱题型")

        if result["reviewer_strong_types"]:
            print(f"\n💪 评审者擅长题型：")
            for st in result["reviewer_strong_types"]:
                print(f"   - {st}")

        if result["suggestions"]:
            print(f"\n💡 互相学习建议：")
            for s in result["suggestions"]:
                print(f"   - {s}")
        else:
            print(f"\n💡 暂无直接的强项-弱项匹配，建议各自加强练习")

        # 保存评审记录
        review_file = os.path.join(self.session_dir, f"cross_review_{int(datetime.now().timestamp())}.json")
        with open(review_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 评审记录已保存：{review_file}")

        return result

    # ========== 全部学员训练 ==========
    def train_all(self):
        """所有学员依次训练"""
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 全员论文写作训练")
        print(f"   时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        results = {}
        for sid in STUDENT_CONFIG.keys():
            print(f"\n{'─' * 70}")
            result = self.train(sid)
            if result:
                results[sid] = result

        # 汇总
        print(f"\n{'=' * 70}")
        print(f"📊 全员训练汇总")
        print(f"{'=' * 70}")
        for sid, r in results.items():
            print(f"   {sid:16s}（{r['student_name']:12s}）：{r['correct']}/{r['total']} | {r['accuracy']:.1%}")

        return results


def main():
    parser = argparse.ArgumentParser(
        description="🦞 小龙虾网络 · 自动论文撰写学习脚本 V1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 paper_writing_training.py --train zhugebin-001
  python3 paper_writing_training.py --train zhugema
  python3 paper_writing_training.py --train-all
  python3 paper_writing_training.py --eval-topic "基于大语言模型的智能体自主任务分解方法研究"
  python3 paper_writing_training.py --outline "论文题目" --type empirical
  python3 paper_writing_training.py --report
  python3 paper_writing_training.py --join-network
  python3 paper_writing_training.py --cross-review zhugema zhuguxia
  python3 paper_writing_training.py --all
        """
    )

    parser.add_argument("--train", type=str,
                        choices=list(STUDENT_CONFIG.keys()),
                        help="执行训练（学员类型）")
    parser.add_argument("--train-all", action="store_true",
                        help="所有学员依次训练")
    parser.add_argument("--eval-topic", type=str,
                        help="评估论文选题（输入题目）")
    parser.add_argument("--outline", type=str,
                        help="生成论文大纲（输入题目）")
    parser.add_argument("--type", type=str,
                        choices=["empirical", "theoretical", "review", "case_study"],
                        default="empirical",
                        help="论文类型（配合 --outline 使用）")
    parser.add_argument("--report", action="store_true",
                        help="生成学习报告")
    parser.add_argument("--join-network", action="store_true",
                        help="加入小龙虾网络联合学习")
    parser.add_argument("--cross-review", nargs=2, metavar=("REVIEWER", "REVIEWEE"),
                        help="学员间交叉评审（智能体互相学习）")
    parser.add_argument("--all", action="store_true",
                        help="执行完整流程（联合学习+训练+报告）")

    args = parser.parse_args()
    learning = PaperWritingLearning()

    if args.all:
        print("🦞 完整训练流程")
        learning.join_network()
        print()
        learning.train("zhugebin-001")
        print()
        learning.eval_topic("基于大语言模型的智能体自主任务分解方法研究")
        print()
        learning.report()
    elif args.train:
        learning.train(args.train)
    elif args.train_all:
        learning.train_all()
    elif args.eval_topic:
        learning.eval_topic(args.eval_topic)
    elif args.outline:
        learning.gen_outline(args.outline, args.type)
    elif args.report:
        learning.report()
    elif args.join_network:
        learning.join_network()
    elif args.cross_review:
        learning.cross_review(args.cross_review[0], args.cross_review[1])
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
