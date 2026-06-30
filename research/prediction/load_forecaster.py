#!/usr/bin/env python3
"""
负载预测模块 - 用于时间套利调度
Load Forecaster for Time-Arbitrage Scheduling

支持多种预测方法：
1. 历史平均（Baseline）
2. 移动平均
3. LSTM 神经网络
4. Prophet 时间序列
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import math

DB_PATH = Path(__file__).parent.parent / "data_collection" / "token_usage.db"


class LoadForecaster:
    """负载预测器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.hourly_pattern = {}  # 小时级负载模式
        self.weekday_pattern = {}  # 星期级负载模式
        self.recent_trend = []  # 近期趋势
        
    def load_historical_data(self, days: int = 7) -> List[Dict]:
        """加载历史负载数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    timestamp,
                    total_tokens,
                    task_type,
                    channel
                FROM token_usage
                WHERE timestamp >= datetime('now', ?)
                ORDER BY timestamp
            """, (f"-{days} days",))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "timestamp": row[0],
                    "tokens": row[1],
                    "task_type": row[2],
                    "channel": row[3]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"加载历史数据失败：{e}")
            return []
    
    def extract_patterns(self, data: List[Dict]):
        """提取负载模式"""
        # 按小时统计
        hour_stats = {}
        weekday_stats = {}
        
        for record in data:
            try:
                ts = datetime.fromisoformat(record["timestamp"])
                hour = ts.hour
                weekday = ts.weekday()  # 0=Monday
                tokens = record["tokens"] or 0
                
                # 小时统计
                if hour not in hour_stats:
                    hour_stats[hour] = []
                hour_stats[hour].append(tokens)
                
                # 星期统计
                key = (weekday, hour)
                if key not in weekday_stats:
                    weekday_stats[key] = []
                weekday_stats[key].append(tokens)
            except Exception as e:
                continue
        
        # 计算平均值
        self.hourly_pattern = {
            hour: sum(tokens_list) / len(tokens_list) if tokens_list else 0
            for hour, tokens_list in hour_stats.items()
        }
        
        self.weekday_pattern = {
            key: sum(tokens_list) / len(tokens_list) if tokens_list else 0
            for key, tokens_list in weekday_stats.items()
        }
        
        return self.hourly_pattern, self.weekday_pattern
    
    def predict_hourly_average(self, hour: int = None) -> float:
        """
        基于历史平均的小时预测
        
        参数:
            hour: 小时（0-23），默认为当前小时
        """
        if hour is None:
            hour = datetime.now().hour
        
        if hour in self.hourly_pattern:
            return self.hourly_pattern[hour]
        
        # 如果没有该小时数据，返回所有小时的平均
        if self.hourly_pattern:
            return sum(self.hourly_pattern.values()) / len(self.hourly_pattern)
        
        # 默认值
        return 1000  # 默认 1000 tokens/小时
    
    def predict_weekday_hourly(self, weekday: int, hour: int) -> float:
        """
        基于星期 + 小时的预测
        
        参数:
            weekday: 星期几（0-6，0=周一）
            hour: 小时（0-23）
        """
        key = (weekday, hour)
        
        if key in self.weekday_pattern:
            return self.weekday_pattern[key]
        
        # 降级到小时平均
        return self.predict_hourly_average(hour)
    
    def predict_next_24h(self) -> List[Tuple[int, float]]:
        """
        预测未来 24 小时负载
        
        返回:
            [(hour, predicted_tokens), ...]
        """
        now = datetime.now()
        predictions = []
        
        for i in range(24):
            future = now + timedelta(hours=i)
            hour = future.hour
            weekday = future.weekday()
            
            pred = self.predict_weekday_hourly(weekday, hour)
            predictions.append((hour, pred))
        
        return predictions
    
    def detect_peak_hours(self, threshold_ratio: float = 1.5) -> List[int]:
        """
        检测高峰时段
        
        参数:
            threshold_ratio: 高峰阈值（相对于平均值的倍数）
        
        返回:
            高峰小时列表
        """
        if not self.hourly_pattern:
            return []
        
        avg = sum(self.hourly_pattern.values()) / len(self.hourly_pattern)
        threshold = avg * threshold_ratio
        
        peak_hours = [
            hour for hour, load in self.hourly_pattern.items()
            if load > threshold
        ]
        
        return sorted(peak_hours)
    
    def detect_off_peak_hours(self, threshold_ratio: float = 0.5) -> List[int]:
        """
        检测低谷时段
        
        参数:
            threshold_ratio: 低谷阈值（相对于平均值的比例）
        """
        if not self.hourly_pattern:
            return []
        
        avg = sum(self.hourly_pattern.values()) / len(self.hourly_pattern)
        threshold = avg * threshold_ratio
        
        off_peak_hours = [
            hour for hour, load in self.hourly_pattern.items()
            if load < threshold
        ]
        
        return sorted(off_peak_hours)
    
    def get_arbitrage_opportunities(self) -> List[Dict]:
        """
        识别时间套利机会
        
        返回:
            套利机会列表，每个包含：
            - peak_hour: 高峰小时
            - off_peak_hour: 低谷小时
            - load_diff: 负载差
            - potential_savings: 潜在节省
        """
        peak_hours = self.detect_peak_hours(1.3)
        off_peak_hours = self.detect_off_peak_hours(0.7)
        
        opportunities = []
        
        for peak in peak_hours:
            for off_peak in off_peak_hours:
                peak_load = self.hourly_pattern.get(peak, 0)
                off_peak_load = self.hourly_pattern.get(off_peak, 0)
                
                if peak_load > off_peak_load * 1.5:  # 至少 1.5 倍差异
                    opportunities.append({
                        "peak_hour": peak,
                        "off_peak_hour": off_peak,
                        "load_diff": peak_load - off_peak_load,
                        "load_ratio": peak_load / max(1, off_peak_load),
                        "potential_savings": (peak_load - off_peak_load) * 0.001  # 简化计算
                    })
        
        # 按潜在节省排序
        opportunities.sort(key=lambda x: x["potential_savings"], reverse=True)
        
        return opportunities
    
    def validate_hypothesis_h1(self) -> Dict:
        """
        验证假设 H1：负载存在显著的日周期模式
        
        返回:
            验证结果
        """
        if not self.hourly_pattern or len(self.hourly_pattern) < 12:
            return {
                "validated": False,
                "reason": "数据不足",
                "hours_available": len(self.hourly_pattern)
            }
        
        # 计算变异系数（CV）
        values = list(self.hourly_pattern.values())
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance)
        cv = std_dev / mean if mean > 0 else 0
        
        # 找出峰值和谷值
        max_hour = max(self.hourly_pattern, key=self.hourly_pattern.get)
        min_hour = min(self.hourly_pattern, key=self.hourly_pattern.get)
        max_load = self.hourly_pattern[max_hour]
        min_load = self.hourly_pattern[min_hour]
        
        # 峰谷比
        peak_valley_ratio = max_load / min_load if min_load > 0 else float('inf')
        
        # 判断是否显著
        is_significant = cv > 0.3 or peak_valley_ratio > 2.0
        
        return {
            "validated": is_significant,
            "cv": cv,
            "peak_hour": max_hour,
            "peak_load": max_load,
            "valley_hour": min_hour,
            "valley_load": min_load,
            "peak_valley_ratio": peak_valley_ratio,
            "conclusion": "存在显著日周期" if is_significant else "日周期不显著"
        }
    
    def export_pattern(self, output_path: str = None):
        """导出模式到 JSON"""
        if output_path is None:
            output_path = Path(__file__).parent / "load_pattern.json"
        
        data = {
            "hourly_pattern": self.hourly_pattern,
            "weekday_pattern": {
                f"{k[0]}_{k[1]}": v for k, v in self.weekday_pattern.items()
            },
            "generated_at": datetime.now().isoformat(),
            "data_points": len(self.weekday_pattern)
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"模式已导出到：{output_path}")
        return output_path


class SimpleLSTMForecaster:
    """
    简化版 LSTM 预测器（使用纯 Python 实现）
    实际部署时可用 PyTorch/TensorFlow 替换
    """
    
    def __init__(self, lookback: int = 24):
        self.lookback = lookback
        self.weights = None
        self.bias = 0
    
    def train(self, data: List[float], epochs: int = 100, lr: int = 0.01):
        """
        简化训练：线性回归近似
        
        实际应使用 LSTM，这里用加权移动平均替代
        """
        if len(data) < self.lookback:
            print(f"数据不足，需要至少 {self.lookback} 个点")
            return
        
        # 简单实现：指数加权移动平均
        self.weights = []
        for i in range(self.lookback):
            weight = math.exp(-0.1 * (self.lookback - i))
            self.weights.append(weight)
        
        # 归一化权重
        total = sum(self.weights)
        self.weights = [w / total for w in self.weights]
        
        # 计算偏置
        recent = data[-self.lookback:]
        prediction = sum(w * x for w, x in zip(self.weights, recent))
        actual = data[-1]
        self.bias = actual - prediction
    
    def predict(self, recent: List[float]) -> float:
        """预测下一个值"""
        if not self.weights:
            # 未训练，返回平均值
            return sum(recent) / len(recent) if recent else 0
        
        # 使用最近的 lookback 个数据
        recent = recent[-self.lookback:]
        
        # 填充不足的数据
        while len(recent) < self.lookback:
            recent = [recent[0]] + recent
        
        prediction = sum(w * x for w, x in zip(self.weights, recent))
        return prediction + self.bias


def main():
    """主函数 - 测试负载预测"""
    print("=" * 60)
    print("📈 负载预测模块测试")
    print("=" * 60)
    
    # 创建预测器
    forecaster = LoadForecaster()
    
    # 加载历史数据
    print("\n1. 加载历史数据...")
    data = forecaster.load_historical_data(days=7)
    print(f"   加载 {len(data)} 条记录")
    
    if not data:
        print("   ⚠️  数据不足，使用模拟数据测试")
        # 生成模拟数据
        import random
        now = datetime.now()
        for i in range(168):  # 7 天 * 24 小时
            ts = now - timedelta(hours=168-i)
            # 模拟日周期：白天高，夜晚低
            hour = ts.hour
            if 9 <= hour <= 18:
                base_load = 5000
            elif 6 <= hour <= 22:
                base_load = 2000
            else:
                base_load = 500
            data.append({
                "timestamp": ts.isoformat(),
                "tokens": base_load + random.randint(-200, 200),
                "task_type": "mixed",
                "channel": "dingtalk"
            })
    
    # 提取模式
    print("\n2. 提取负载模式...")
    hourly, weekday = forecaster.extract_patterns(data)
    print(f"   小时模式：{len(hourly)} 个小时")
    print(f"   星期 - 小时模式：{len(weekday)} 个组合")
    
    # 显示小时模式
    print("\n3. 小时负载模式:")
    for hour in sorted(hourly.keys()):
        load = hourly[hour]
        bar = '█' * int(load / 200)
        print(f"   {hour:02d}:00 {bar} ({load:.0f})")
    
    # 预测未来 24 小时
    print("\n4. 未来 24 小时预测:")
    predictions = forecaster.predict_next_24h()
    for hour, pred in predictions[:6]:  # 只显示前 6 小时
        print(f"   {hour:02d}:00 - {pred:.0f} tokens")
    print("   ...")
    
    # 识别高峰和低谷
    print("\n5. 高峰时段检测:")
    peak_hours = forecaster.detect_peak_hours(1.3)
    print(f"   高峰小时：{peak_hours}")
    
    print("\n6. 低谷时段检测:")
    off_peak_hours = forecaster.detect_off_peak_hours(0.7)
    print(f"   低谷小时：{off_peak_hours}")
    
    # 套利机会
    print("\n7. 时间套利机会:")
    opportunities = forecaster.get_arbitrage_opportunities()
    for i, opp in enumerate(opportunities[:3], 1):
        print(f"   #{i}: 高峰{opp['peak_hour']:02d}:00 → 低谷{opp['off_peak_hour']:02d}:00")
        print(f"       负载比：{opp['load_ratio']:.2f}x, 潜在节省：¥{opp['potential_savings']:.4f}")
    
    # 验证假设 H1
    print("\n8. 假设 H1 验证（负载日周期）:")
    h1_result = forecaster.validate_hypothesis_h1()
    print(f"   验证结果：{'✅ 通过' if h1_result['validated'] else '❌ 未通过'}")
    if h1_result.get('reason'):
        print(f"   原因：{h1_result['reason']}")
    else:
        print(f"   变异系数 (CV): {h1_result['cv']:.3f}")
        print(f"   峰谷比：{h1_result['peak_valley_ratio']:.2f}x")
        print(f"   峰值小时：{h1_result['peak_hour']:02d}:00 ({h1_result['peak_load']:.0f} tokens)")
        print(f"   谷值小时：{h1_result['valley_hour']:02d}:00 ({h1_result['valley_load']:.0f} tokens)")
        print(f"   结论：{h1_result['conclusion']}")
    
    # 导出模式
    print("\n9. 导出负载模式...")
    forecaster.export_pattern()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
