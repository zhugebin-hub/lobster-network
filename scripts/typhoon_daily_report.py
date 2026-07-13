#!/usr/bin/env python3
"""
🦞 小龙虾网络 · 巴威台风每日对比汇总报告
==========================================

每天运行: 对比小龙虾预测 vs 官方预报 vs 实际路径
用法:
    python3 typhoon_daily_report.py                    # 生成今日对比报告
    python3 typhoon_daily_report.py --date 2026-07-11  # 指定日期
    python3 typhoon_daily_report.py --week             # 本周汇总
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'domains', 'learning', 'problems'))
from typhoon_predict_engine import TyphoonPredictEngine, haversine

# ===========================
# 路径配置
# ===========================

PROJECT_ROOT = Path(__file__).parent.parent
PREDICTIONS_DIR = PROJECT_ROOT / "registry" / "typhoon_predictions"
OBSERVATIONS_FILE = PROJECT_ROOT / "registry" / "typhoon_predictions" / "bavi_actual_track.json"
REPORTS_DIR = PROJECT_ROOT / "docs" / "typhoon_reports"
LEARNING_DIR = PROJECT_ROOT / "domains" / "learning" / "problems" / "typhoon-track"


# ===========================
# 实际观测数据模板
# ===========================

def load_or_create_observations():
    """加载或创建实际观测数据"""
    if OBSERVATIONS_FILE.exists():
        with open(OBSERVATIONS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "typhoon_name": "巴威 (Bavi)",
        "number": "2026-09",
        "observations": [],
        "last_updated": None,
    }


def save_observations(data):
    """保存实际观测数据"""
    OBSERVATIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OBSERVATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def add_observation(lat, lon, intensity, pressure, time_str, source="官方"):
    """添加一条实际观测记录"""
    data = load_or_create_observations()
    data["observations"].append({
        "time": time_str,
        "lat": lat,
        "lon": lon,
        "intensity": intensity,
        "pressure": pressure,
        "source": source,
    })
    data["observations"].sort(key=lambda x: x["time"])
    data["last_updated"] = datetime.now().isoformat()
    save_observations(data)
    return data


def load_latest_prediction():
    """加载最新的预测数据"""
    if not PREDICTIONS_DIR.exists():
        return None

    pred_files = sorted(PREDICTIONS_DIR.glob("bavi_prediction_*.json"))
    if not pred_files:
        return None

    with open(pred_files[-1], "r", encoding="utf-8") as f:
        return json.load(f)


def load_all_predictions():
    """加载所有历史预测"""
    predictions = []
    if not PREDICTIONS_DIR.exists():
        return predictions

    for f in sorted(PREDICTIONS_DIR.glob("bavi_prediction_*.json")):
        with open(f, "r", encoding="utf-8") as fp:
            predictions.append(json.load(fp))
    return predictions


def _naive(dt):
    """将 datetime 转为 offset-naive（去掉时区信息），确保可做减法"""
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def find_closest_point(track, target_time):
    """在轨迹中找到最接近目标时间的点"""
    best = None
    best_diff = float("inf")
    target = _naive(datetime.fromisoformat(target_time))

    for p in track:
        pt = _naive(datetime.fromisoformat(p["time"]))
        diff = abs((pt - target).total_seconds())
        if diff < best_diff:
            best_diff = diff
            best = p

    return best


def generate_daily_report(date_str=None):
    """生成每日对比报告"""
    if date_str is None:
        target_date = datetime.now()
    else:
        target_date = datetime.strptime(date_str, "%Y-%m-%d")

    predictions = load_all_predictions()
    observations = load_or_create_observations()

    if not predictions:
        return "❌ 无预测数据"

    latest = predictions[-1]
    pred_track = latest["track"]

    lines = []
    lines.append("=" * 80)
    lines.append(f"🦞 小龙虾网络 · 巴威台风每日对比报告")
    lines.append(f"   日期: {target_date.strftime('%Y年%m月%d日')}")
    lines.append(f"   模型: TyphoonPredictEngine v1.0 (四模型融合)")
    lines.append("=" * 80)
    lines.append("")

    # 1. 当前预测摘要
    init = latest["initial_conditions"]
    lines.append("【预测基线】")
    lines.append(f"  初始条件: {init['time']}")
    lines.append(f"  初始位置: {init['lat']}°N, {init['lon']}°E")
    lines.append(f"  初始强度: {init['intensity']}m/s, {init['pressure']}hPa (台风级)")
    lines.append("")

    # 2. 每日预测快照
    lines.append("【7天路径预测快照】")
    lines.append(f"  {'日期':<14} {'位置':<20} {'强度':<16} {'等级':<10} {'状态'}")
    lines.append(f"  {'-'*75}")

    daily = {}
    for p in pred_track:
        pt = datetime.fromisoformat(p["time"])
        day_key = pt.strftime("%Y-%m-%d")
        if day_key not in daily:
            daily[day_key] = p

    for day_key in sorted(daily.keys()):
        p = daily[day_key]
        pt = datetime.fromisoformat(p["time"])
        pos = f"({p['lat']:.1f}°N, {p['lon']:.1f}°E)"
        strength = f"{p['intensity']:.0f}m/s/{p['pressure']:.0f}hPa"
        status = "🟫内陆" if p["on_land"] else "🌊海上"
        lines.append(f"  {pt.strftime('%m/%d %a'):<14} {pos:<20} {strength:<16} {p['level_cn']:<10} {status}")

    lines.append("")

    # 3. 与实际观测对比 (如果有)
    if observations["observations"]:
        lines.append("【预测 vs 实际对比】")
        lines.append(f"  {'时间':<22} {'预测位置':<20} {'实际位置':<20} {'距离误差':>10} {'强度误差':>10}")
        lines.append(f"  {'-'*85}")

        total_dist_err = 0
        total_int_err = 0
        n = 0

        for obs in observations["observations"]:
            closest = find_closest_point(pred_track, obs["time"])
            if closest:
                dist_err = haversine(obs["lat"], obs["lon"], closest["lat"], closest["lon"])
                int_err = abs(obs["intensity"] - closest["intensity"])
                total_dist_err += dist_err
                total_int_err += int_err
                n += 1

                indicator = "✅" if dist_err < 50 else ("⚠️" if dist_err < 100 else "❌")
                t = datetime.fromisoformat(obs["time"])
                pred_pos = f"({closest['lat']:.1f}N,{closest['lon']:.1f}E)"
                real_pos = f"({obs['lat']:.1f}N,{obs['lon']:.1f}E)"
                lines.append(f"  {t.strftime('%m/%d %H:%M'):<22} {pred_pos:<20} {real_pos:<20} "
                            f"{indicator} {dist_err:>6.0f}km  {int_err:>7.0f}m/s")

        if n > 0:
            lines.append(f"  {'-'*85}")
            lines.append(f"  平均位置误差: {total_dist_err/n:.0f}km | 平均强度误差: {total_int_err/n:.0f}m/s | 对比点: {n}")
    else:
        lines.append("【预测 vs 实际对比】")
        lines.append("  ⚠️ 暂无实际观测数据。将每天更新。")
        lines.append("")
        lines.append("  可通过以下方式添加观测:")
        lines.append(f"  1. 手动编辑: {OBSERVATIONS_FILE}")
        lines.append(f"  2. 运行: python3 scripts/typhoon_daily_report.py --add-obs <lat> <lon> <intensity> <pressure> <time>")

    lines.append("")

    # 4. 城市影响更新
    lines.append("【重点城市影响评估 (预测)】")
    AFFECTED = [
        ("温州", 28.0, 120.7), ("台州", 28.7, 121.4), ("宁波", 29.9, 121.6),
        ("杭州", 30.3, 120.2), ("上海", 31.2, 121.5), ("福州", 26.1, 119.3),
        ("合肥", 31.8, 117.2), ("南京", 32.1, 118.8), ("济南", 36.7, 117.0),
    ]

    lines.append(f"  {'城市':<6} {'最近距离':>8} {'最接近时间':>12} {'影响等级'}")
    lines.append(f"  {'-'*45}")
    for name, clat, clon in AFFECTED:
        min_dist = float('inf')
        min_time = ""
        for p in pred_track:
            dist = haversine(clat, clon, p["lat"], p["lon"])
            if dist < min_dist:
                min_dist = dist
                min_time = datetime.fromisoformat(p["time"]).strftime("%m/%d %H:%M")

        if min_dist < 100:
            level = "🔴 严重"
        elif min_dist < 200:
            level = "🟠 较强"
        elif min_dist < 400:
            level = "🟡 一般"
        else:
            level = "🟢 轻微"

        lines.append(f"  {name:<6} {min_dist:>6.0f}km {min_time:>14} {level}")

    lines.append("")
    lines.append("=" * 80)
    lines.append(f"  小龙虾网络 · TyphoonPredictEngine v1.0")
    lines.append(f"  报告生成: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 80)

    return "\n".join(lines)


def generate_week_summary():
    """生成本周汇总"""
    predictions = load_all_predictions()
    observations = load_or_create_observations()

    lines = []
    lines.append("=" * 80)
    lines.append("🦞 小龙虾网络 · 巴威台风 7天追踪汇总报告")
    lines.append("=" * 80)

    if not predictions:
        lines.append("❌ 无预测数据")
        return "\n".join(lines)

    latest = predictions[-1]
    lines.append(f"  预测版本: {latest['prediction_id']}")
    lines.append(f"  初始时间: {latest['initial_conditions']['time']}")
    lines.append(f"  模型: TyphoonPredictEngine v1.0")
    lines.append("")

    # 路径汇总表
    lines.append("【完整7天路径预测 (每6h)】")
    track = latest["track"]
    lines.append(f"{'时次':>5} {'日期时间':<18} {'纬度':>8} {'经度':>8} {'方向':>6} {'速度':>6} {'风速':>6} {'气压':>6} {'等级':<10}")
    lines.append("-" * 80)

    for p in track:
        t = datetime.fromisoformat(p["time"])
        lm = "陆" if p["on_land"] else "海"
        lf = "⚡登陆!" if p["is_landfall"] else ""
        lines.append(f"+{p['hour']:>3}h {t.strftime('%m/%d %H:%M'):<18} "
                    f"{p['lat']:>6.1f}°N {p['lon']:>6.1f}°E "
                    f"{p['heading']:>4.0f}° {p['speed']:>4.0f}km/h "
                    f"{p['intensity']:>4.0f}m/s {p['pressure']:>4.0f}hPa "
                    f"{p['level_cn']:<8} {lm} {lf}")

    lines.append("")

    # 观测对比
    if observations["observations"]:
        lines.append("【预测准确率统计】")
        total_err = 0
        n = 0
        for obs in observations["observations"]:
            closest = find_closest_point(track, obs["time"])
            if closest:
                err = haversine(obs["lat"], obs["lon"], closest["lat"], closest["lon"])
                total_err += err
                n += 1
        if n > 0:
            lines.append(f"  已观测: {n} 个时次")
            lines.append(f"  平均位置误差: {total_err/n:.0f} km")
            if total_err/n < 50:
                lines.append(f"  评级: ⭐⭐⭐ 优秀")
            elif total_err/n < 100:
                lines.append(f"  评级: ⭐⭐ 良好")
            else:
                lines.append(f"  评级: ⭐ 需改进")
        else:
            lines.append("  暂无实际观测数据对比")
    else:
        lines.append("【预测准确率统计】")
        lines.append("  暂无实际观测数据 (将随台风发展每日更新)")

    lines.append("")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="巴威台风每日对比报告")
    parser.add_argument("--date", "-d", type=str, help="指定日期 (YYYY-MM-DD)")
    parser.add_argument("--week", action="store_true", help="生成本周汇总")
    parser.add_argument("--add-obs", nargs=5, metavar=("LAT", "LON", "INTENSITY", "PRESSURE", "TIME"),
                       help="添加实际观测: lat lon intensity(m/s) pressure(hPa) time(ISO)")
    parser.add_argument("--output", "-o", type=str, help="输出文件路径")
    parser.add_argument("--save", action="store_true", help="保存报告到 docs/typhoon_reports/")
    args = parser.parse_args()

    if args.add_obs:
        lat, lon, intensity, pressure, time_str = args.add_obs
        add_observation(float(lat), float(lon), float(intensity), float(pressure), time_str)
        print(f"✅ 已添加观测: ({lat}°N, {lon}°E) @ {time_str}")
        return

    if args.week:
        report = generate_week_summary()
    else:
        report = generate_daily_report(args.date)

    print(report)

    if args.save or args.output:
        output_path = args.output
        if not output_path:
            REPORTS_DIR.mkdir(parents=True, exist_ok=True)
            date_str = args.date if args.date else datetime.now().strftime("%Y%m%d")
            output_path = str(REPORTS_DIR / f"bavi_daily_{date_str}.md")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"\n✅ 报告已保存: {output_path}")

    # 同时保存到 outputs
    outputs_dir = PROJECT_ROOT.parent / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    latest_report = outputs_dir / "bavi_latest_report.md"
    with open(latest_report, "w", encoding="utf-8") as f:
        f.write(report)


if __name__ == "__main__":
    main()
