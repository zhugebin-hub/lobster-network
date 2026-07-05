#!/usr/bin/env python3
"""
小龙虾网络 · 网络协议学习脚本 V1.0
==========================================

对齐 Meyo 推送：90题 / 三只Agent / 联邦学习融合

功能：
1. 执行网络协议答题训练（OSI/TCP-IP/路由/SDN/安全）
2. 评估答题准确率，跟踪阶段进度
3. 生成学习报告
4. 支持多学员（xiaochen / zhuguxia / zhugebin-001）

用法：
    python3 network_protocol_training.py --help
    python3 network_protocol_training.py --train xiaochen
    python3 network_protocol_training.py --train zhuguxia
    python3 network_protocol_training.py --train zhugebin-001
    python3 network_protocol_training.py --quiz phase1
    python3 network_protocol_training.py --report
    python3 network_protocol_training.py --all
"""

import sys
import os
import json
import argparse
import random
from datetime import datetime

# 路径设置
BASE_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(BASE_DIR, "domains", "learning", "problems"))

from network_protocol_engine import NetworkProtocolEngine
from network_protocol_trainer import NetworkProtocolTrainer, STUDENT_CONFIG

STUDENTS = ["xiaochen", "zhuguxia", "zhugebin-001"]


def run_training_session(engine, trainer, verbose=True):
    """执行一场训练会话（模拟答题）"""
    student = trainer.student_type
    config = trainer.config
    phase = trainer.state["current_phase"]
    questions = trainer.get_next_questions()

    if verbose:
        print("=" * 60)
        print(f"小龙虾网络 · 网络协议训练")
        print(f"  学员：{config['name']} ({student})")
        print(f"  当前阶段：{phase}")
        print(f"  题目数：{len(questions)}")
        print(f"  目标准确率：{config['target_accuracy']:.0%}")
        print("=" * 60)

    results = []
    for i, q in enumerate(questions, 1):
        if verbose:
            print(f"\n{'-' * 40}")
            print(f"  [{i}/{len(questions)}] {q['question']}")
            if "options" in q:
                for j, opt in enumerate(q["options"]):
                    marker = "✅" if j == q["correct"] else "  "
                    print(f"      {marker} {chr(65 + j)}. {opt}")

        # 模拟答题（准确率随学员类型变化）
        base_acc = config["learning_rate"] + 0.60
        is_correct = random.random() < base_acc
        results.append({"id": q["id"], "correct": is_correct})

        if verbose:
            status = "✅ 正确" if is_correct else "❌ 错误"
            expl = q.get("explanation", "")[:50]
            print(f"   → {status}  |  解析：{expl}...")

    session = trainer.submit_answers(results)

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"📊 本场结果：{session['correct']}/{session['count']}  ({session['accuracy']:.1%})")
        report = trainer.get_report()
        print(f"📈 累计准确率：{report['overall_accuracy']:.1%}")
        if session["accuracy"] >= config["target_accuracy"]:
            print(f"   🌟 达标！可进入下一阶段")
        print("=" * 60)

    return session


def main():
    parser = argparse.ArgumentParser(description="小龙虾网络 · 网络协议学习脚本 V1.0")
    parser.add_argument("--train", type=str, choices=STUDENTS, help="训练指定学员")
    parser.add_argument("--quiz", type=str, choices=["phase1", "phase2", "phase3"], help="测验指定阶段（5题）")
    parser.add_argument("--report", action="store_true", help="生成全部学员学习报告")
    parser.add_argument("--reset", type=str, choices=STUDENTS, help="重置指定学员状态")
    parser.add_argument("--all", action="store_true", help="完整流程：所有学员各训练一场")
    args = parser.parse_args()

    engine = NetworkProtocolEngine()

    if args.all:
        print("小龙虾网络 · 完整训练流程（所有学员）")
        for student in STUDENTS:
            t = NetworkProtocolTrainer(engine, student)
            run_training_session(engine, t, verbose=True)
        # 最终汇总
        print("\n" + "=" * 60)
        print("📋 最终汇总")
        for student in STUDENTS:
            t = NetworkProtocolTrainer(engine, student)
            r = t.get_report()
            print(f"   {r['student_name']}: {r['overall_accuracy']:.1%}  "
                  f"({r['total_correct']}/{r['total_answered']})  "
                  f"阶段：{r['current_phase']}")
        print("=" * 60)

    elif args.train:
        trainer = NetworkProtocolTrainer(engine, args.train)
        run_training_session(engine, trainer, verbose=True)

    elif args.quiz:
        print("=" * 60)
        print(f"📝 网络协议测验 — {args.quiz}")
        print("=" * 60)
        quiz = engine.quiz(phase=args.quiz, count=5)
        for i, q in enumerate(quiz, 1):
            print(f"\n[{i}] {q['question']}")
            if "options" in q:
                for j, opt in enumerate(q["options"]):
                    print(f"    {chr(65 + j)}. {opt}")
            print(f"   ✅ 答案：{chr(65 + q['correct'])}  |  {q.get('explanation', '')[:60]}...")
        print()

    elif args.report:
        print("=" * 60)
        print(f"📊 网络协议学习报告  {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 60)
        for student in STUDENTS:
            t = NetworkProtocolTrainer(engine, student)
            r = t.get_report()
            print(f"\n👤 {r['student_name']} ({student})")
            print(f"   当前阶段：{r['current_phase']}")
            print(f"   已完成  ：{', '.join(r['completed_phases']) or '（无）'}")
            print(f"   答题统计：{r['total_correct']}/{r['total_answered']}  "
                  f"准确率 {r['overall_accuracy']:.1%}")
            for phase_key, scores in r.get("phase_scores", {}).items():
                total = scores.get("total", 0)
                correct = scores.get("correct", 0)
                acc = correct / total if total > 0 else 0
                print(f"   {phase_key}: {correct}/{total} ({acc:.1%})")
        print()

    elif args.reset:
        t = NetworkProtocolTrainer(engine, args.reset)
        t.reset()
        print(f"✅ 已重置 {args.reset} 的学习状态")

    else:
        # 默认：显示题目库概况
        print("=" * 60)
        print("小龙虾网络 · 网络协议学习系统 V1.0")
        print("=" * 60)
        for phase in ["phase1", "phase2", "phase3"]:
            info = engine.get_phase_info(phase)
            if info:
                print(f"   {phase}: {info['title']}（{info['question_count']} 题）")
        print(f"\n   总题数：{len(engine.get_problems())}")
        print(f"   支持学员：{', '.join(STUDENTS)}")
        print(f"\n   用法：python3 network_protocol_training.py --train <学员名>")
        print("=" * 60)


if __name__ == "__main__":
    main()
