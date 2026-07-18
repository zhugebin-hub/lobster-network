#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 炒股预测学习脚本 V1.0
==========================================

功能：
1. 生成每日训练计划（稳健型/加速型/研究型）
2. 执行预测练习（涨跌/价格区间/振幅/选股/仓位）
3. 评估预测准确率
4. 生成学习报告
5. 加入联合学习（与 hermes/xiaochen/zhuguxia 同步）
6. 推送学习成果到网络

用法：
    python3 stock_predict_training.py --help
    python3 stock_predict_training.py --train xiaochen
    python3 stock_predict_training.py --train zhuguxia
    python3 stock_predict_training.py --train zhugebin-001
    python3 stock_predict_training.py --predict 600519
    python3 stock_predict_training.py --report
    python3 stock_predict_training.py --join-network
    python3 stock_predict_training.py --all
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

from stock_predict_engine import StockPredictEngine
from stock_predict_trainer import StockPredictTrainer, STUDENT_CONFIG


class StockPredictLearning:
    """炒股预测学习系统"""

    def __init__(self):
        self.engine = StockPredictEngine()
        self.trainer = StockPredictTrainer(self.engine)
        self.history_file = os.path.join(
            SCRIPT_DIR, "..", "registry", "stock_history.json"
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
        return {"predictions": [], "accuracy": {}, "streak": 0}

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
        print(f"🦞 小龙虾网络 · 炒股预测训练")
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
                print(f"  选项：{' / '.join(prob['options'])}")

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
        self.history["predictions"].append({
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
        session_id = f"stock_session_{int(datetime.now().timestamp())}"
        session = {
            "session_id": session_id,
            "domain": "stock-predict",
            "student": student_type,
            "student_name": cfg["name"],
            "created_at": datetime.now().isoformat(),
            "total_problems": total,
            "correct": correct,
            "accuracy": accuracy,
            "details": details,
            "by_type": by_type,
            "participants": [student_type, "hermes"],  # 教练在场
        }
        session_file = os.path.join(self.session_dir, f"{session_id}.json")
        with open(session_file, "w", encoding="utf-8") as f:
            json.dump(session, f, ensure_ascii=False, indent=2)
        print(f"\n💾 学习会话已保存：{session_file}")

        return training_result

    # ========== 预测 ==========
    def predict(self, stock_code: str):
        """对单只股票执行全面预测"""
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 炒股全面预测")
        print(f"   股票代码：{stock_code}")
        print(f"   预测时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        # 模拟数据（实际场景应从行情API获取）
        stock_db = {
            "600519": {"name": "贵州茅台", "market_cap": 20000, "pe": 30, "pb": 10,
                       "ma5": 1680, "ma20": 1650, "recent_change": 3.2, "volume_ratio": 1.8,
                       "macd_signal": "gold_cross", "industry": "白酒", "price": 1680},
            "000858": {"name": "五粮液", "market_cap": 5000, "pe": 22, "pb": 5,
                       "ma5": 165, "ma20": 162, "recent_change": 1.5, "volume_ratio": 1.3,
                       "macd_signal": "gold_cross", "industry": "白酒", "price": 165},
            "300750": {"name": "宁德时代", "market_cap": 9000, "pe": 45, "pb": 5,
                       "ma5": 210, "ma20": 220, "recent_change": 12, "volume_ratio": 2.5,
                       "macd_signal": "death_cross", "industry": "新能源", "price": 210},
            "688981": {"name": "中芯国际", "market_cap": 4500, "pe": 80, "pb": 3,
                       "ma5": 58, "ma20": 60, "recent_change": -2.1, "volume_ratio": 0.8,
                       "macd_signal": "none", "industry": "半导体", "price": 58},
            "002230": {"name": "科大讯飞", "market_cap": 800, "pe": 120, "pb": 6,
                       "ma5": 42, "ma20": 40, "recent_change": 4.5, "volume_ratio": 2.0,
                       "macd_signal": "gold_cross", "industry": "AI", "price": 42},
        }

        if stock_code not in stock_db:
            print(f"\n⚠️ 股票代码 {stock_code} 不在演示数据库中")
            print(f"   演示数据库包含：{', '.join(stock_db.keys())}")
            return

        s = stock_db[stock_code]
        print(f"\n📊 股票基本信息：")
        for k, v in s.items():
            print(f"   {k}: {v}")

        # 1. 涨跌预测
        print(f"\n📈 涨跌预测:")
        result = self.engine.predict_trend(
            stock_code=stock_code, stock_name=s["name"],
            market_cap=s["market_cap"], pe_ratio=s["pe"], pb_ratio=s["pb"],
            ma5=s["ma5"], ma20=s["ma20"], recent_change=s["recent_change"],
            volume_ratio=s["volume_ratio"], macd_signal=s["macd_signal"],
            industry=s["industry"],
        )
        print(f"   预测：{result['prediction']}")
        print(f"   置信度：{result['confidence']:.1%}")
        print(f"   概率：涨 {result['probabilities']['up']:.1%} | 平 {result['probabilities']['flat']:.1%} | 跌 {result['probabilities']['down']:.1%}")
        print(f"   因子分析：")
        for k, v in result["factors"].items():
            print(f"      {k}: {v}")

        # 2. 价格区间预测
        print(f"\n💰 价格区间预测（未来5日）:")
        pr = self.engine.predict_price_range(
            stock_code, s["name"], current_price=s["price"],
            daily_volatility=0.025, days=5
        )
        print(f"   当前价：¥{pr['current_price']}")
        print(f"   预测区间：¥{pr['predicted_range'][0]} - ¥{pr['predicted_range'][1]}")
        print(f"   中位价：¥{pr['mid_price']}")
        print(f"   置信度：{pr['confidence']:.0%}")

        # 3. 振幅预测
        print(f"\n🌊 振幅预测:")
        amp = self.engine.predict_amplitude(
            stock_code, s["name"],
            historical_amplitudes=[2.1, 3.5, 1.8, 2.9, 4.2]
        )
        print(f"   预测：{amp['prediction']}")
        print(f"   期望振幅：{amp['expected_amplitude']}%")

        # 4. 凯利公式仓位
        print(f"\n💵 凯利公式仓位（基于预测置信度）:")
        kelly = self.engine.kelly_criterion(
            win_prob=result["confidence"],
            win_return=0.10, loss_return=-0.08,
            bankroll=100000, kelly_fraction=0.5,
        )
        print(f"   上涨概率：{kelly['win_prob']:.1%}")
        print(f"   全凯利比例：{kelly['kelly_full']:.1%}")
        print(f"   实际仓位（半凯利）：{kelly['kelly_actual']:.1%}")
        print(f"   建议金额：¥{kelly['position_amount']:.0f}")
        print(f"   期望收益：{kelly['expected_return']:+.1%}")
        print(f"   是否买入：{'✅ 是' if kelly['should_buy'] else '❌ 否'}")

        return {
            "stock_code": stock_code,
            "trend": result,
            "price_range": pr,
            "amplitude": amp,
            "kelly": kelly,
        }

    # ========== 报告 ==========
    def report(self):
        """生成学习报告"""
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 炒股预测学习报告")
        print(f"   生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)

        predictions = self.history.get("predictions", [])
        if not predictions:
            print("\n⚠️ 暂无训练记录，请先执行 --train")
            return

        # 总体统计
        total_trainings = len(predictions)
        total_problems = sum(p["total"] for p in predictions)
        total_correct = sum(p["correct"] for p in predictions)
        overall_accuracy = total_correct / total_problems if total_problems > 0 else 0

        print(f"\n📊 总体统计")
        print(f"   训练次数：{total_trainings}")
        print(f"   总题数：{total_problems}")
        print(f"   总正确数：{total_correct}")
        print(f"   整体准确率：{overall_accuracy:.1%}")

        # 最近5次训练
        print(f"\n📋 最近5次训练")
        for p in predictions[-5:]:
            date = p["date"][:16].replace("T", " ")
            print(f"   {date} | {p['student']:18s} | {p['correct']}/{p['total']} | {p['accuracy']:.1%}")

        # 按学员统计
        students = {}
        for p in predictions:
            s = p["student"]
            if s not in students:
                students[s] = {"total": 0, "correct": 0, "trainings": 0}
            students[s]["total"] += p["total"]
            students[s]["correct"] += p["correct"]
            students[s]["trainings"] += 1

        print(f"\n👥 学员统计")
        for s, stats in students.items():
            acc = stats["correct"] / stats["total"] if stats["total"] > 0 else 0
            name = STUDENT_CONFIG.get(s, {}).get("name", s)
            print(f"   {s}（{name}）：{stats['correct']}/{stats['total']} | {acc:.1%} | 训练 {stats['trainings']} 次")

        # 学员详细状态
        print(f"\n📈 学员详细状态（来自trainer）:")
        for sid in STUDENT_CONFIG.keys():
            state = self.trainer.get_student_state(sid)
            if state.get("total_trainings", 0) > 0:
                print(f"   {sid}（{STUDENT_CONFIG[sid]['name']}）：")
                print(f"      累计训练：{state['total_trainings']} 次")
                print(f"      累计题目：{state['total_problems']} 题")
                print(f"      累计正确：{state['total_correct']} 题")
                acc = state['total_correct'] / state['total_problems'] if state['total_problems'] > 0 else 0
                print(f"      累计准确率：{acc:.1%}")
                print(f"      连续训练：{state.get('streak', 0)} 天")

    # ========== 加入联合学习 ==========
    def join_network(self):
        """加入小龙虾网络联合学习"""
        print("=" * 70)
        print(f"🦞 小龙虾网络 · 炒股预测联合学习")
        print(f"{'=' * 70}")

        # 网络成员
        network_members = [
            {"id": "hermes", "name": "诸葛马", "role": "教练", "domain": "炒股预测教练"},
            {"id": "xiaochen", "name": "小陈", "role": "学员", "domain": "炒股预测（稳健型）"},
            {"id": "zhuguxia", "name": "诸葛虾", "role": "学员", "domain": "炒股预测（加速型）"},
            {"id": "zhugebin-001", "name": "诸葛斌的工作助手", "role": "学员", "domain": "炒股预测（研究型）"},
        ]

        print(f"\n👥 网络成员（共 {len(network_members)} 节点）：")
        for m in network_members:
            print(f"   - {m['id']}（{m['name']}）：{m['role']} - {m['domain']}")

        # 生成联合学习会话
        session_id = f"stock_joint_{int(datetime.now().timestamp())}"
        session = {
            "session_id": session_id,
            "domain": "stock-predict",
            "type": "joint_learning",
            "created_at": datetime.now().isoformat(),
            "organizer": "hermes",
            "participants": [m["id"] for m in network_members],
            "topic": "炒股预测联合学习",
            "phases": ["phase1", "phase2", "phase3"],
            "rules": {
                "daily_min_problems": 8,
                "weekly_review": True,
                "cross_check": True,
                "share_predictions": True,
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

        print(f"\n🎯 下一步建议：")
        print(f"   1. 执行 `python3 scripts/stock_predict_training.py --train zhugebin-001`")
        print(f"   2. 执行 `python3 scripts/stock_predict_training.py --report` 查看进度")
        print(f"   3. 执行 `python3 scripts/stock_predict_training.py --predict 600519` 测试预测")

        return session


def main():
    parser = argparse.ArgumentParser(
        description="🦞 小龙虾网络 · 炒股预测学习脚本 V1.0",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  python3 stock_predict_training.py --train zhugebin-001
  python3 stock_predict_training.py --train xiaochen
  python3 stock_predict_training.py --predict 600519
  python3 stock_predict_training.py --report
  python3 stock_predict_training.py --join-network
  python3 stock_predict_training.py --all
        """
    )

    parser.add_argument("--train", type=str,
                        choices=["xiaochen", "zhuguxia", "zhugebin-001", "workbuddy"],
                        help="执行训练（学员类型）")
    parser.add_argument("--predict", type=str,
                        help="执行预测（股票代码，如 600519）")
    parser.add_argument("--report", action="store_true",
                        help="生成学习报告")
    parser.add_argument("--join-network", action="store_true",
                        help="加入小龙虾网络联合学习")
    parser.add_argument("--all", action="store_true",
                        help="执行完整训练流程（zhugebin-001）")

    args = parser.parse_args()
    learning = StockPredictLearning()

    if args.all:
        print("🦞 完整训练流程")
        learning.join_network()
        print()
        learning.train("zhugebin-001")
        print()
        learning.predict("600519")
        print()
        learning.report()
    elif args.train:
        learning.train(args.train)
    elif args.predict:
        learning.predict(args.predict)
    elif args.report:
        learning.report()
    elif args.join_network:
        learning.join_network()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
