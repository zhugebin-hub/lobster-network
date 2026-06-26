"""
炒股预测引擎 V1.0
=================

支持：
1. 涨跌预测（涨/平/跌）—— 多因子加权模型
2. 价格区间预测（基于波动率与近期均价）
3. 振幅预测（基于历史波动率分位）
4. 选股预测（多股票排序）
5. 仓位管理（凯利公式）

设计参考：domains/learning/problems/football_predict_engine.py
"""

import json
import os
import math
from typing import Dict, List, Optional, Tuple
from datetime import datetime


# ========== 行业景气度系数（简化版）==========
INDUSTRY_BIAS = {
    "白酒": 0.05, "新能源": 0.08, "半导体": 0.10, "医药": 0.03,
    "银行": -0.02, "地产": -0.05, "钢铁": 0.00, "消费": 0.02,
    "TMT": 0.06, "汽车": 0.04, "化工": 0.01, "电力设备": 0.05,
    "AI": 0.12, "机器人": 0.10, "default": 0.00,
}


class StockPredictEngine:
    """炒股预测引擎"""

    def __init__(self, problems_dir: str = None):
        if problems_dir is None:
            problems_dir = os.path.join(
                os.path.dirname(__file__),
                "problems", "stock-predict"
            )
        self.problems_dir = problems_dir
        self.phases = {}
        self._load_problems()

    def _load_problems(self):
        for phase in ["phase1", "phase2", "phase3"]:
            phase_dir = os.path.join(self.problems_dir, phase)
            problems_file = os.path.join(phase_dir, "problems.json")
            if os.path.exists(problems_file):
                with open(problems_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.phases[phase] = data

    def get_problems(self, phase: str = None, problem_type: str = None,
                     difficulty: str = None, limit: int = 10) -> List[Dict]:
        problems = []
        phases_to_check = [phase] if phase else list(self.phases.keys())
        for p in phases_to_check:
            if p not in self.phases:
                continue
            for prob in self.phases[p]["problems"]:
                if problem_type and prob.get("type") != problem_type:
                    continue
                if difficulty and prob.get("difficulty") != difficulty:
                    continue
                problems.append(prob)
        return problems[:limit]

    # ========================================================
    # 涨跌预测：多因子加权模型
    # ========================================================
    def predict_trend(self, stock_code: str, stock_name: str,
                      market_cap: float = None, pe_ratio: float = None,
                      pb_ratio: float = None, ma5: float = None,
                      ma20: float = None, recent_change: float = 0.0,
                      volume_ratio: float = 1.0, macd_signal: str = "none",
                      industry: str = "default") -> Dict:
        """
        涨跌预测（多因子加权模型）

        Args:
            stock_code: 股票代码
            stock_name: 股票名称
            market_cap: 市值（亿元）
            pe_ratio: 市盈率（倍）
            pb_ratio: 市净率（倍）
            ma5: 5日均价
            ma20: 20日均价
            recent_change: 近5日累计涨跌幅（%）
            volume_ratio: 量比
            macd_signal: gold_cross / death_cross / none
            industry: 所属行业

        Returns:
            预测结果
        """
        # 基础分（0.5 = 中性）
        bull_score = 0.5
        bear_score = 0.3
        flat_prob = 0.2

        # 因子1：均线趋势（ma5 vs ma20）
        if ma5 and ma20 and ma20 > 0:
            ma_diff = (ma5 - ma20) / ma20
            # 金叉（ma5 上穿 ma20）+0.10；死叉 -0.10
            bull_score += max(-0.10, min(0.10, ma_diff * 2))

        # 因子2：近5日涨跌幅（动量）
        # 涨多了有回调压力，跌多了有反弹机会 —— 倒U型
        if recent_change > 10:
            bull_score -= 0.08
        elif recent_change > 5:
            bull_score -= 0.03
        elif -5 < recent_change < 5:
            bull_score += 0.02
        elif -10 < recent_change <= -5:
            bull_score += 0.05
        else:
            bull_score += 0.08  # 超跌反弹

        # 因子3：量比（成交量放大=资金活跃）
        if volume_ratio > 2.0:
            bull_score += 0.06  # 放量上涨概率高
        elif volume_ratio > 1.5:
            bull_score += 0.03
        elif volume_ratio < 0.5:
            bull_score -= 0.04  # 缩量调整

        # 因子4：MACD信号
        if macd_signal == "gold_cross":
            bull_score += 0.08
        elif macd_signal == "death_cross":
            bull_score -= 0.08

        # 因子5：行业景气度
        industry_bias = INDUSTRY_BIAS.get(industry, INDUSTRY_BIAS["default"])
        bull_score += industry_bias

        # 因子6：估值（PE）
        if pe_ratio is not None and pe_ratio > 0:
            if pe_ratio < 15:
                bull_score += 0.04  # 低估
            elif pe_ratio > 80:
                bull_score -= 0.05  # 高估
            elif pe_ratio > 200:
                bull_score -= 0.08

        # 因子7：市值（小市值弹性大）
        if market_cap is not None:
            if market_cap < 100:
                bull_score += 0.03  # 小盘股弹性
            elif market_cap > 2000:
                bull_score -= 0.02  # 大盘股稳

        # 归一化
        total = max(bull_score + bear_score + flat_prob, 0.01)
        bull_prob = bull_score / total
        bear_prob = bear_score / total
        flat_prob = flat_prob / total

        # 决策
        if bull_prob > bear_prob and bull_prob > flat_prob:
            result = "涨"
            confidence = bull_prob
        elif bear_prob > bull_prob and bear_prob > flat_prob:
            result = "跌"
            confidence = bear_prob
        else:
            result = "平"
            confidence = flat_prob

        return {
            "stock": f"{stock_name}({stock_code})",
            "prediction": result,
            "confidence": round(confidence, 3),
            "probabilities": {
                "up": round(bull_prob, 3),
                "flat": round(flat_prob, 3),
                "down": round(bear_prob, 3),
            },
            "factors": {
                "ma_trend": "金叉" if (ma5 and ma20 and ma5 > ma20) else "死叉" if (ma5 and ma20 and ma5 < ma20) else "未知",
                "momentum": f"{recent_change:+.2f}%",
                "volume_ratio": volume_ratio,
                "macd": macd_signal,
                "industry": industry,
                "pe": pe_ratio,
                "market_cap": market_cap,
            },
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 价格区间预测：基于波动率
    # ========================================================
    def predict_price_range(self, stock_code: str, stock_name: str,
                            current_price: float, daily_volatility: float = 0.025,
                            days: int = 5) -> Dict:
        """
        预测未来 N 日价格区间（基于日波动率）

        Args:
            current_price: 当前价格
            daily_volatility: 日波动率（默认2.5%）
            days: 预测天数

        Returns:
            价格区间
        """
        # N日波动率放大
        period_volatility = daily_volatility * math.sqrt(days)

        lower = current_price * (1 - period_volatility * 1.96)  # 95% 置信区间下界
        upper = current_price * (1 + period_volatility * 1.96)  # 95% 置信区间上界
        mid = current_price

        return {
            "stock": f"{stock_name}({stock_code})",
            "current_price": current_price,
            "predicted_range": [round(lower, 2), round(upper, 2)],
            "mid_price": round(mid, 2),
            "daily_volatility": daily_volatility,
            "days": days,
            "confidence": 0.95,
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 振幅预测：基于历史波动率分位
    # ========================================================
    def predict_amplitude(self, stock_code: str, stock_name: str,
                          historical_amplitudes: List[float] = None) -> Dict:
        """
        预测当日振幅（最高-最低）/ 昨收

        Args:
            historical_amplitudes: 近N日振幅列表（如 [2.1, 3.5, 1.8, 2.9, 4.2]）

        Returns:
            振幅预测
        """
        if not historical_amplitudes:
            historical_amplitudes = [2.5, 3.0, 2.8, 3.2, 2.9]

        # 计算分位
        sorted_amps = sorted(historical_amplitudes)
        n = len(sorted_amps)

        p25 = sorted_amps[max(0, int(n * 0.25) - 1)]
        p50 = sorted_amps[int(n * 0.5)]
        p75 = sorted_amps[min(n - 1, int(n * 0.75))]
        mean_amp = sum(historical_amplitudes) / n

        # 决策区间
        if mean_amp < 2.0:
            range_pred = "低振幅(<2%)"
        elif mean_amp < 4.0:
            range_pred = "中振幅(2-4%)"
        elif mean_amp < 6.0:
            range_pred = "高振幅(4-6%)"
        else:
            range_pred = "极高振幅(>6%)"

        return {
            "stock": f"{stock_name}({stock_code})",
            "prediction": range_pred,
            "expected_amplitude": round(mean_amp, 2),
            "percentiles": {
                "p25": round(p25, 2),
                "p50": round(p50, 2),
                "p75": round(p75, 2),
            },
            "historical": historical_amplitudes,
            "confidence": 0.70,
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 选股预测：多股票排序
    # ========================================================
    def predict_portfolio(self, stocks: List[Dict]) -> Dict:
        """
        多股票综合评分排序选股

        Args:
            stocks: 股票列表，每个含 code/name/market_cap/pe/recent_change/macd_signal/industry

        Returns:
            选股预测
        """
        scores = []
        for s in stocks:
            score = 0.5  # 基础分

            # 估值分（PE 越低越好）
            if "pe" in s and s["pe"] and s["pe"] > 0:
                if s["pe"] < 15:
                    score += 0.10
                elif s["pe"] < 30:
                    score += 0.05
                elif s["pe"] > 100:
                    score -= 0.05

            # 动量分（近5日小幅上涨最佳）
            chg = s.get("recent_change", 0)
            if 0 < chg < 5:
                score += 0.06
            elif -5 < chg < 0:
                score += 0.04  # 小幅回调反弹机会
            elif chg > 10:
                score -= 0.04  # 涨太多风险

            # 行业景气度
            industry = s.get("industry", "default")
            score += INDUSTRY_BIAS.get(industry, 0)

            # MACD 信号
            if s.get("macd_signal") == "gold_cross":
                score += 0.05
            elif s.get("macd_signal") == "death_cross":
                score -= 0.05

            # 市值弹性
            mc = s.get("market_cap", 500)
            if mc < 200:
                score += 0.03  # 中小盘弹性
            elif mc > 3000:
                score -= 0.02

            scores.append((s["name"], s.get("code", ""), score))

        scores.sort(key=lambda x: x[2], reverse=True)

        total = sum(s for _, _, s in scores) or 0.01
        probs = [(name, code, score / total) for name, code, score in scores]

        return {
            "predicted_best": probs[0][0] if probs else None,
            "predicted_best_code": probs[0][1] if probs else None,
            "confidence": round(probs[0][2], 3) if probs else 0,
            "ranking": [
                {"name": n, "code": c, "prob": round(p, 3)}
                for n, c, p in probs[:10]
            ],
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 凯利公式仓位管理
    # ========================================================
    def kelly_criterion(self, win_prob: float, win_return: float = 0.10,
                        loss_return: float = -0.08, bankroll: float = 100000,
                        kelly_fraction: float = 0.5) -> Dict:
        """
        凯利公式计算最优仓位（半凯利更稳健）

        Args:
            win_prob: 上涨概率
            win_return: 上涨预期收益率（默认+10%）
            loss_return: 下跌预期收益率（默认-8%）
            bankroll: 总资金
            kelly_fraction: 凯利比例（0.5 = 半凯利）

        Returns:
            仓位建议
        """
        # 凯利公式：f = (p*b - q) / b，其中 b = win_return / |loss_return|
        b = win_return / abs(loss_return) if loss_return != 0 else 0
        q = 1 - win_prob
        kelly = (win_prob * b - q) / b if b > 0 else 0

        # 应用比例（半凯利）
        actual_kelly = kelly * kelly_fraction

        # 仓位金额
        position_amount = max(0, actual_kelly * bankroll)

        # 期望收益
        ev = win_prob * win_return + q * loss_return

        return {
            "win_prob": win_prob,
            "win_return": win_return,
            "loss_return": loss_return,
            "kelly_full": round(kelly, 3),
            "kelly_actual": round(actual_kelly, 3),
            "position_ratio": round(actual_kelly, 3),
            "position_amount": round(position_amount, 2),
            "expected_return": round(ev, 3),
            "should_buy": kelly > 0 and ev > 0,
            "timestamp": datetime.now().isoformat(),
        }

    # ========================================================
    # 期望值计算
    # ========================================================
    def expected_value(self, win_prob: float, win_return: float = 0.10,
                       loss_return: float = -0.08) -> float:
        """计算期望收益率"""
        return win_prob * win_return + (1 - win_prob) * loss_return


# 演示
if __name__ == "__main__":
    engine = StockPredictEngine()

    print("=" * 60)
    print("🦞 小龙虾网络 · 炒股预测引擎 V1.0")
    print("=" * 60)

    # 1. 涨跌预测
    print("\n📊 涨跌预测（贵州茅台）:")
    result = engine.predict_trend(
        stock_code="600519",
        stock_name="贵州茅台",
        market_cap=20000,
        pe_ratio=30,
        pb_ratio=10,
        ma5=1680.0,
        ma20=1650.0,
        recent_change=3.2,
        volume_ratio=1.8,
        macd_signal="gold_cross",
        industry="白酒",
    )
    print(f"  股票：{result['stock']}")
    print(f"  预测：{result['prediction']}")
    print(f"  置信度：{result['confidence']:.1%}")
    print(f"  概率：涨 {result['probabilities']['up']:.1%} | 平 {result['probabilities']['flat']:.1%} | 跌 {result['probabilities']['down']:.1%}")

    # 2. 价格区间预测
    print("\n💰 价格区间预测:")
    pr = engine.predict_price_range("600519", "贵州茅台", current_price=1680, daily_volatility=0.018, days=5)
    print(f"  当前价：{pr['current_price']}")
    print(f"  预测区间：{pr['predicted_range'][0]} - {pr['predicted_range'][1]}")
    print(f"  置信度：{pr['confidence']:.0%}")

    # 3. 振幅预测
    print("\n🌊 振幅预测:")
    amp = engine.predict_amplitude("600519", "贵州茅台", [2.1, 3.5, 1.8, 2.9, 4.2])
    print(f"  预测：{amp['prediction']}")
    print(f"  期望振幅：{amp['expected_amplitude']}%")

    # 4. 选股预测
    print("\n🏆 选股预测:")
    stocks = [
        {"code": "600519", "name": "贵州茅台", "market_cap": 20000, "pe": 30, "recent_change": 3.2, "macd_signal": "gold_cross", "industry": "白酒"},
        {"code": "000858", "name": "五粮液", "market_cap": 5000, "pe": 22, "recent_change": 1.5, "macd_signal": "gold_cross", "industry": "白酒"},
        {"code": "300750", "name": "宁德时代", "market_cap": 9000, "pe": 45, "recent_change": 5.8, "macd_signal": "gold_cross", "industry": "新能源"},
        {"code": "688981", "name": "中芯国际", "market_cap": 4500, "pe": 80, "recent_change": -2.1, "macd_signal": "none", "industry": "半导体"},
    ]
    port = engine.predict_portfolio(stocks)
    print(f"  推荐首选：{port['predicted_best']} ({port['predicted_best_code']})")
    print(f"  置信度：{port['confidence']:.1%}")
    for r in port["ranking"]:
        print(f"    {r['name']}: {r['prob']:.1%}")

    # 5. 凯利公式
    print("\n💵 凯利公式仓位:")
    kelly = engine.kelly_criterion(win_prob=0.65, win_return=0.10, loss_return=-0.08, bankroll=100000)
    print(f"  上涨概率：{kelly['win_prob']:.0%}")
    print(f"  全凯利比例：{kelly['kelly_full']:.1%}")
    print(f"  实际仓位（半凯利）：{kelly['kelly_actual']:.1%}")
    print(f"  建议金额：¥{kelly['position_amount']:.0f}")
    print(f"  是否买入：{'✅ 是' if kelly['should_buy'] else '❌ 否'}")

    # 6. 题库统计
    print("\n📚 题库统计:")
    for phase, data in engine.phases.items():
        print(f"  {phase}: {data['name']} - {len(data['problems'])} 题")

    print("\n" + "=" * 60)
    print("✅ 炒股预测引擎测试完成！")
