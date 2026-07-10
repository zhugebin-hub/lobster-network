#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 巴威台风预测脚本
================================

预测台风巴威 (2026 No.9) 的未来路径。

用法:
    python3 typhoon_predict_bavi.py --forecast 48h    # 48小时预测
    python3 typhoon_predict_bavi.py --forecast 7d      # 7天预测
    python3 typhoon_predict_bavi.py --forecast all     # 全部预测+对比报告
    python3 typhoon_predict_bavi.py --report           # 仅生成对比报告
    python3 typhoon_predict_bavi.py --json             # JSON 格式输出
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'domains', 'learning', 'problems'))
from typhoon_predict_engine import (
    TyphoonPredictEngine, TyphoonPredictTrainer,
    haversine, get_typhoon_level, move_point
)


# ===========================
# 巴威初始条件 (2026-07-10 17:00 CST = 09:00 UTC)
# ===========================

BAVI_INITIAL = {
    "name": "巴威 (Bavi)",
    "number": "2026-09",
    "time": "2026-07-10T17:00:00+08:00",
    "lat": 22.2,
    "lon": 126.6,
    "heading": 315.0,     # NW
    "speed": 22.5,        # km/h
    "intensity": 40.0,    # m/s, 台风级
    "pressure": 960.0,    # hPa
    "radius_7": 490,      # km, 七级风圈
    "radius_10": 315,     # km, 十级风圈
    "radius_12": 115,     # km, 十二级风圈
}

# ===========================
# 官方预报对比数据 (中央气象台 2026-07-10 18:00)
# ===========================

OFFICIAL_FORECAST = [
    {"hour": 0,  "lat": 22.2, "lon": 126.6, "intensity": 40, "pressure": 960, "note": "当前 (台风级)"},
    {"hour": 12, "lat": 23.5, "lon": 124.5, "intensity": 42, "pressure": 955, "note": "接近台湾北部"},
    {"hour": 24, "lat": 25.2, "lon": 122.5, "intensity": 43, "pressure": 950, "note": "台湾北部海面"},
    {"hour": 36, "lat": 27.0, "lon": 120.8, "intensity": 42, "pressure": 955, "note": "浙闽交界登陆"},
    {"hour": 48, "lat": 28.5, "lon": 119.2, "intensity": 35, "pressure": 970, "note": "进入浙江内陆"},
    {"hour": 60, "lat": 30.0, "lon": 117.8, "intensity": 28, "pressure": 980, "note": "安徽南部"},
    {"hour": 72, "lat": 31.5, "lon": 117.0, "intensity": 22, "pressure": 990, "note": "安徽中部"},
    {"hour": 84, "lat": 33.0, "lon": 116.5, "intensity": 18, "pressure": 995, "note": "安徽北部"},
    {"hour": 96, "lat": 34.5, "lon": 117.0, "intensity": 14, "pressure": 1000, "note": "进入山东 (热带低压)"},
    {"hour": 108,"lat": 36.0, "lon": 118.0, "intensity": 12, "pressure": 1003, "note": "山东中部"},
    {"hour": 120,"lat": 37.5, "lon": 119.5, "intensity": 10, "pressure": 1005, "note": "山东半岛"},
    {"hour": 132,"lat": 38.5, "lon": 121.0, "intensity": 8,  "pressure": 1008, "note": "渤海/黄海"},
]


# ===========================
# 关键城市影响评估
# ===========================

AFFECTED_CITIES = [
    {"name": "温州", "lat": 28.0, "lon": 120.7},
    {"name": "台州", "lat": 28.7, "lon": 121.4},
    {"name": "福州", "lat": 26.1, "lon": 119.3},
    {"name": "宁德", "lat": 26.7, "lon": 119.5},
    {"name": "杭州", "lat": 30.3, "lon": 120.2},
    {"name": "上海", "lat": 31.2, "lon": 121.5},
    {"name": "宁波", "lat": 29.9, "lon": 121.6},
    {"name": "合肥", "lat": 31.8, "lon": 117.2},
    {"name": "南京", "lat": 32.1, "lon": 118.8},
    {"name": "武汉", "lat": 30.6, "lon": 114.3},
    {"name": "济南", "lat": 36.7, "lon": 117.0},
    {"name": "青岛", "lat": 36.1, "lon": 120.4},
]


def assess_city_impact(track, cities):
    """评估台风对各城市的影响程度"""
    results = []
    for city in cities:
        min_dist = float('inf')
        min_hour = 0
        max_wind_near = 0

        for p in track:
            if p["hour"] > 168:
                break
            dist = haversine(city["lat"], city["lon"], p["lat"], p["lon"])
            if dist < min_dist:
                min_dist = dist
                min_hour = p["hour"]
                max_wind_near = p["intensity"]

        # 影响等级
        if min_dist < 100:
            impact = "🔴 严重"
        elif min_dist < 200:
            impact = "🟠 较强"
        elif min_dist < 400:
            impact = "🟡 一般"
        elif min_dist < 800:
            impact = "🟢 轻微"
        else:
            impact = "⚪ 无"

        results.append({
            "city": city["name"],
            "lat": city["lat"],
            "lon": city["lon"],
            "min_distance_km": round(min_dist, 1),
            "closest_hour": min_hour,
            "max_wind_near": max_wind_near,
            "impact": impact,
        })

    results.sort(key=lambda x: x["min_distance_km"])
    return results


def run_forecast(hours, output_format="text"):
    """执行预测"""
    engine = TyphoonPredictEngine()
    start_time = datetime.fromisoformat("2026-07-10T17:00:00+08:00")
    start_time = start_time.replace(tzinfo=None)

    track = engine.predict_track(
        lat=BAVI_INITIAL["lat"],
        lon=BAVI_INITIAL["lon"],
        heading=BAVI_INITIAL["heading"],
        speed=BAVI_INITIAL["speed"],
        intensity=BAVI_INITIAL["intensity"],
        pressure=BAVI_INITIAL["pressure"],
        hours=hours,
        step_hours=3,
        start_time=start_time,
    )

    if output_format == "json":
        return track

    return format_forecast_report(track, engine, hours)


def format_forecast_report(track, engine, hours):
    """格式化预测报告"""
    lines = []
    lines.append("=" * 80)
    lines.append("🦞 小龙虾网络 · 台风巴威路径预测")
    lines.append("=" * 80)
    lines.append(f"  模型: 四模型加权融合 (气候学20% + 引导气流35% + 惯性25% + 转向20%)")
    lines.append(f"  初始: {BAVI_INITIAL['time']}")
    lines.append(f"  位置: {BAVI_INITIAL['lat']}°N, {BAVI_INITIAL['lon']}°E")
    lines.append(f"  强度: {BAVI_INITIAL['intensity']}m/s ({BAVI_INITIAL['pressure']}hPa) 台风级")
    lines.append(f"  移动: {BAVI_INITIAL['heading']}° (NW) @ {BAVI_INITIAL['speed']}km/h")
    lines.append(f"  预测: {hours}小时 ({hours//24}天), 步长3小时")
    lines.append("")

    # 登陆信息
    landfall = engine.get_landfall_info(track)
    if landfall:
        lt = datetime.fromisoformat(landfall["time"])
        lines.append(f"⚡ 预测登陆: {lt.strftime('%m月%d日 %H:%M')} CST")
        lines.append(f"   登陆点: {landfall['lat']}°N, {landfall['lon']}°E")
        lines.append(f"   登陆强度: {landfall['intensity']}m/s, {landfall['pressure']}hPa ({landfall['level_cn']})")
    lines.append("")

    # 路径表格
    lines.append("【完整路径预测表】")
    lines.append(engine.format_track_table(track, max_points=40))
    lines.append("")

    # 每日快照
    lines.append("【每日关键快照】")
    lines.append("-" * 80)
    daily = engine.get_daily_snapshot(track)
    for p in daily:
        t = datetime.fromisoformat(p["time"])
        lines.append(f"  {t.strftime('%m/%d %H:%M')} | "
                     f"{p['lat']:>6.1f}°N {p['lon']:>7.1f}°E | "
                     f"{p['heading']:>5.0f}° @ {p['speed']:>4.0f}km/h | "
                     f"{p['intensity']:>4.0f}m/s {p['pressure']:>5.0f}hPa | "
                     f"{p['level_cn']}")
    lines.append("")

    # 城市影响评估
    lines.append("【受影响城市评估】")
    lines.append("-" * 80)
    impacts = assess_city_impact(track, AFFECTED_CITIES)
    lines.append(f"  {'城市':<6} {'最近距离':>8} {'接近时间':>10} {'台风强度':>8} {'影响等级'}")
    lines.append(f"  {'-'*55}")
    for imp in impacts:
        closest_time = datetime.fromisoformat(track[0]["time"]) + timedelta(hours=imp["closest_hour"])
        lines.append(f"  {imp['city']:<6} {imp['min_distance_km']:>6.0f}km "
                     f"{closest_time.strftime('%m/%d %H:%M'):>12} "
                     f"{imp['max_wind_near']:>5.0f}m/s "
                     f"{imp['impact']}")

    lines.append("")
    lines.append("=" * 80)

    # 与官方对比
    lines.append("")
    lines.append("【与中央气象台官方预报对比】")
    lines.append("-" * 80)
    comparison = engine.compare_with_official(track, OFFICIAL_FORECAST)
    lines.append(f"  {'时次':<6} {'官方位置':<20} {'预测位置':<20} {'距离误差':>10}")
    lines.append(f"  {'-'*60}")
    for c in comparison["comparisons"]:
        t = start_time + timedelta(hours=c["hour"])
        lines.append(f"  +{c['hour']:>3}h  "
                     f"({c['official']['lat']:.1f}°N,{c['official']['lon']:.1f}°E)   "
                     f"({c['our']['lat']:.1f}°N,{c['our']['lon']:.1f}°E)   "
                     f"{c['distance_error_km']:>6.1f}km")
    lines.append(f"  {'-'*60}")
    lines.append(f"  平均距离误差: {comparison['average_distance_error_km']} km "
                 f"(共{comparison['compared_points']}个对比点)")
    lines.append("")

    return "\n".join(lines), track


def run_comparison_report():
    """生成详细对比报告"""
    engine = TyphoonPredictEngine()
    start_time = datetime.fromisoformat("2026-07-10T17:00:00+08:00")
    start_time = start_time.replace(tzinfo=None)

    track = engine.predict_track(
        lat=BAVI_INITIAL["lat"],
        lon=BAVI_INITIAL["lon"],
        heading=BAVI_INITIAL["heading"],
        speed=BAVI_INITIAL["speed"],
        intensity=BAVI_INITIAL["intensity"],
        pressure=BAVI_INITIAL["pressure"],
        hours=168,
        step_hours=6,
        start_time=start_time,
    )

    comparison = engine.compare_with_official(track, OFFICIAL_FORECAST)

    lines = []
    lines.append("=" * 80)
    lines.append("🦞 小龙虾网络 · 巴威台风预测 vs 官方预报 对比报告")
    lines.append("=" * 80)
    lines.append(f"  模型版本: TyphoonPredictEngine v1.0")
    lines.append(f"  预测时间: {BAVI_INITIAL['time']}")
    lines.append(f"  对比基准: 中央气象台 2026-07-10 18:00 预报")
    lines.append("")

    # 比较表格
    lines.append("【位置对比】")
    lines.append(f"{'时次':<8} {'小龙虾预测':<22} {'中央气象台':<22} {'距离差':>8} {'官方描述'}")
    lines.append("-" * 85)

    for c in comparison["comparisons"]:
        op = None
        for of in OFFICIAL_FORECAST:
            if of["hour"] == c["hour"]:
                op = of
                break

        our_pos = f"({c['our']['lat']:.1f}°N, {c['our']['lon']:.1f}°E)"
        off_pos = f"({c['official']['lat']:.1f}°N, {c['official']['lon']:.1f}°E)"

        err = c['distance_error_km']
        if err < 50:
            indicator = "✅"
        elif err < 100:
            indicator = "⚠️"
        else:
            indicator = "❌"

        note = op.get("note", "") if op else ""
        lines.append(f"+{c['hour']:>3}h   {our_pos:<22} {off_pos:<22} {indicator} {err:>5.0f}km  {note}")

    lines.append("-" * 85)
    lines.append(f"  平均误差: {comparison['average_distance_error_km']} km | "
                 f"对比点: {comparison['compared_points']} | "
                 f"模型等级: {'优秀' if comparison['average_distance_error_km'] and comparison['average_distance_error_km'] < 100 else '良好' if comparison['average_distance_error_km'] and comparison['average_distance_error_km'] < 200 else '需优化'}")
    lines.append("")

    # 城市影响
    impacts = assess_city_impact(track, AFFECTED_CITIES)
    lines.append("【城市影响预测 vs 官方】")
    lines.append("-" * 60)
    for imp in impacts:
        lines.append(f"  {imp['city']:<6} 最近{imp['min_distance_km']:>5.0f}km "
                     f"(+{imp['closest_hour']}h) → {imp['impact']}")
    lines.append("")

    lines.append("=" * 80)

    return "\n".join(lines), track, comparison


def main():
    parser = argparse.ArgumentParser(description="巴威台风路径预测")
    parser.add_argument("--forecast", choices=["48h", "7d", "all"], default="all",
                       help="预测时长 (default: all)")
    parser.add_argument("--report", action="store_true", help="生成对比报告")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")
    parser.add_argument("--output", "-o", type=str, help="输出文件路径")
    parser.add_argument("--save-prediction", action="store_true",
                       help="保存预测数据到 registry/typhoon_predictions/")
    args = parser.parse_args()

    if args.report or args.forecast == "all":
        report, track, comparison = run_comparison_report()
        print(report)

        # 保存预测
        if args.save_prediction or True:
            save_dir = Path(__file__).parent.parent / "registry" / "typhoon_predictions"
            save_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            pred_data = {
                "prediction_id": f"bavi_{timestamp}",
                "model_version": "TyphoonPredictEngine v1.0",
                "initial_conditions": BAVI_INITIAL,
                "prediction_time": datetime.now().isoformat(),
                "track": track,
                "comparison_with_official": comparison,
            }

            save_path = save_dir / f"bavi_prediction_{timestamp}.json"
            with open(save_path, "w", encoding="utf-8") as f:
                json.dump(pred_data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ 预测数据已保存: {save_path}")

    elif args.forecast == "48h":
        report, track = run_forecast(48)
        print(report)

    elif args.forecast == "7d":
        report, track = run_forecast(168)
        print(report)

    if args.json and 'track' in dir():
        print("\n--- JSON ---")
        print(json.dumps(track[:10], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
