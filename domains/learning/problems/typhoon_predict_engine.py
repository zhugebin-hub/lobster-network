"""
🦞 小龙虾网络 · 台风路径预测引擎
================================

基于物理模型的台风路径与强度预测引擎。

核心模型：
1. 引导气流 + Beta 漂移 — 台风移动的主要驱动力
2. 陆地摩擦衰减 — 登陆后强度指数级衰减
3. 转向规律 — 副高边缘引导下的路径转向 (NW → N → NE)
4. 多模型融合 — 集合多种参数方案取加权平均

用法:
    from typhoon_predict_engine import TyphoonPredictEngine
    engine = TyphoonPredictEngine()
    forecast = engine.predict_track(lat=22.2, lon=126.6, heading=315, speed=22.5,
                                     intensity=40.0, pressure=960,
                                     hours=168, step_hours=3)
"""

import math
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple


# ===========================
# 常量与经验参数
# ===========================

# 地球半径 (km)
EARTH_RADIUS = 6371.0

# 度 → 公里 (近似，中纬度)
DEG_TO_KM_LAT = 111.32
DEG_TO_KM_LON = lambda lat: 111.32 * math.cos(math.radians(lat))

# 台风等级阈值 (m/s)
TYPHOON_LEVELS = [
    (0, 17.1, "热带低压", "TD"),
    (17.2, 24.4, "热带风暴", "TS"),
    (24.5, 32.6, "强热带风暴", "STS"),
    (32.7, 41.4, "台风", "TY"),
    (41.5, 50.9, "强台风", "STY"),
    (51.0, float("inf"), "超强台风", "SuperTY"),
]


def get_typhoon_level(max_wind: float) -> Tuple[str, str]:
    """根据最大风速获取台风等级"""
    for lo, hi, name_cn, name_en in TYPHOON_LEVELS:
        if lo <= max_wind <= hi:
            return name_cn, name_en
    return "未知", "UNK"


def haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算两点间距离 (km)"""
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return 2 * EARTH_RADIUS * math.asin(math.sqrt(a))


def bearing(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """计算从点1到点2的方位角 (0-360度)"""
    dlon = math.radians(lon2 - lon1)
    y = math.sin(dlon) * math.cos(math.radians(lat2))
    x = (math.cos(math.radians(lat1)) * math.sin(math.radians(lat2)) -
         math.sin(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.cos(dlon))
    brng = math.degrees(math.atan2(y, x))
    return (brng + 360) % 360


def move_point(lat: float, lon: float, heading_deg: float, distance_km: float) -> Tuple[float, float]:
    """从 (lat, lon) 沿 heading_deg 方向移动 distance_km 公里"""
    heading_rad = math.radians(heading_deg)
    dlat = distance_km * math.cos(heading_rad) / DEG_TO_KM_LAT
    dlon = distance_km * math.sin(heading_rad) / DEG_TO_KM_LON(lat)
    new_lat = lat + dlat
    new_lon = lon + dlon
    return round(new_lat, 4), round(new_lon, 4)


# ===========================
# 陆地判断
# ===========================


def is_over_land(lat: float, lon: float) -> bool:
    """
    简化判断是否在中国大陆/台湾上空

    基于关键城市经纬度和海岸线特征判断:
    - 西侧内陆: lon < coast_lon → 陆地
    - 东侧海洋: lon > coast_lon + margin → 海洋
    - 过渡带: 按纬度区间细化
    """
    # 大陆主体 (经度 117°E 以西肯定是内陆)
    if 22.0 <= lat <= 42.0 and lon <= 117.0:
        return True

    # 按纬度带判断海岸线
    # 台湾: 约 22°N-25.5°N, 海岸线 120-122°E
    if 22.0 <= lat <= 25.5 and 120.0 <= lon <= 122.0:
        return True

    # 浙江南部-福建北部: 约 26°N-28°N, 海岸线约 120.0-121.0°E
    # 霞浦 120.0E, 温州 120.7E, 温岭 121.4E
    if 26.0 <= lat <= 28.0 and lon <= 120.8:
        return True

    # 浙江北部: 约 28°N-30.5°N, 海岸线约 121.0-122.0°E
    # 台州 121.4E, 宁波 121.6E, 杭州湾 ~120.8E
    if 28.0 <= lat <= 30.5 and lon <= 121.3:
        return True

    # 上海-江苏南部: 约 30.5°N-33°N, 海岸线约 121.5-122.0°E
    # 上海 121.5E, 南京 118.8E, 南通 120.9E
    if 30.5 <= lat <= 33.5 and lon <= 120.5:
        return True

    # 山东: 约 34.5°N-38°N, 海岸线约 119-122°E
    # 青岛 120.4E, 济南 117.0E
    if 34.5 <= lat <= 38.5 and lon <= 119.5:
        return True

    # 更高纬度 (河北/辽宁): 海岸线约 118-122°E
    if 38.0 <= lat <= 42.0 and lon <= 119.0:
        return True

    return False


# ===========================
# 物理模型
# ===========================

class TyphoonPredictEngine:
    """台风路径与强度预测引擎"""

    def __init__(self, model_weights: Dict[str, float] = None):
        """
        初始化引擎

        Args:
            model_weights: 各模型权重, 默认等权
        """
        self.model_weights = model_weights or {
            "climatology": 0.15,      # 气候学模型
            "steering_flow": 0.45,    # 引导气流模型 (增加权重)
            "inertial": 0.20,         # 惯性外推模型
            "recurve": 0.20,          # 转向模型
        }
        self.history = []

    def _climatology_model(self, lat: float, lon: float, heading: float,
                           speed: float, hours: float) -> Tuple[float, float, float, float]:
        """
        气候学模型 — 基于历史台风统计规律

        西北太平洋台风典型路径:
        - 7月: 偏西→西北→登陆或转向
        - 在22°N-30°N之间平均转向角速率约 0.5-1.0 deg/hr
        - 低纬 (<22°N): 稳定 WNW 到 NW
        - 中纬 (22°N-30°N): 逐渐右转
        - 高纬 (>30°N): 明显转向 NE
        """
        dt = hours

        # 气候学转向率: 纬度越高, 转向越明显
        if lat < 22:
            recurve_rate = 0.0   # 热带: 稳定 NW, 几乎不转
        elif lat < 25:
            recurve_rate = 0.2   # 23°N-25°N: 微弱右转
        elif lat < 30:
            recurve_rate = 0.5   # 25°N-30°N: 转向区
        else:
            recurve_rate = 1.2   # >30°N: 加速转向NE

        new_heading = (heading + recurve_rate * dt) % 360

        # 速度微调
        if lat > 32:
            speed_factor = 1.05  # 西风带加速
        elif lat > 25:
            speed_factor = 1.0
        else:
            speed_factor = 1.02  # 热带海面略加速
        new_speed = speed * speed_factor

        new_lat, new_lon = move_point(lat, lon, new_heading, new_speed * dt)
        return new_lat, new_lon, new_heading, new_speed

    def _steering_flow_model(self, lat: float, lon: float, heading: float,
                             speed: float, hours: float) -> Tuple[float, float, float, float]:
        """
        引导气流模型 — 基于副热带高压引导

        7月副高典型位置: 中心约32°N, 140°E
        台风位于副高西南侧, 受东南气流引导向西北移动

        物理原理 (北半球反气旋):
        - 高压系统周围气流顺时针旋转
        - 台风位于副高中心方位角 θ (从副高指向台风)
        - 引导气流方向 = θ + 90° (顺时针切线方向)
        - 台风在副高SW侧 (θ≈225°) → 引导气流≈315° (NW) ✓
        - 随着台风北上到W侧 (θ≈270°) → 引导气流≈0° (N)
        - 再到NW侧 (θ≈315°) → 引导气流≈45° (NE) — 经典转向路径!
        """
        dt = hours

        # 副高中心近似位置 (7月中旬, 巴威期间副高偏强偏西)
        sh_center_lat, sh_center_lon = 33.0, 135.0

        # 从副高中心指向台风的方位角 (这是关键!)
        center_to_typhoon = bearing(sh_center_lat, sh_center_lon, lat, lon)
        dist_to_sh = haversine(lat, lon, sh_center_lat, sh_center_lon)

        # 引导气流方向: 绕副高顺时针切线
        # 北半球反气旋: 风向沿顺时针切线 = center_to_typhoon + 90°
        steer_heading = (center_to_typhoon + 90) % 360

        # 加入 Beta 效应和地形强迫修正 (向西偏转, 促进登陆)
        beta_correction = -10  # 加强西向分量
        steer_heading = (steer_heading + beta_correction) % 360

        # 引导气流强度随距离衰减
        steer_strength = min(1.0, 1000 / max(dist_to_sh, 100))

        # 混合: 65% 引导气流 + 35% 惯性 (使用圆形平均)
        sx = 0.65 * math.cos(math.radians(steer_heading)) + 0.35 * math.cos(math.radians(heading))
        sy = 0.65 * math.sin(math.radians(steer_heading)) + 0.35 * math.sin(math.radians(heading))
        new_heading = math.degrees(math.atan2(sy, sx)) % 360

        # 速度受引导气流影响
        new_speed = speed * (0.85 + 0.15 * steer_strength)

        new_lat, new_lon = move_point(lat, lon, new_heading, new_speed * dt)
        return new_lat, new_lon, new_heading, new_speed

    def _inertial_model(self, lat: float, lon: float, heading: float,
                        speed: float, hours: float) -> Tuple[float, float, float, float]:
        """
        惯性外推模型 — 保持当前运动趋势

        短时预测最有效 (0-24小时), 加上微弱的 Beta 漂移

        Beta 效应: 台风在行星涡度梯度作用下,
        - 向西北方向漂移 (约2-4 km/h 向北 + 偏西分量)
        - 简化为: 每小时约 0.1°-0.3° 顺时针偏转
        """
        dt = hours

        # Beta 漂移: 北半球, 台风趋向向西北漂移
        # 纬度越低, beta漂移越小
        if lat < 20:
            beta_drift = 0.08   # 极小偏转
        elif lat < 25:
            beta_drift = 0.15   # deg/hour
        elif lat < 30:
            beta_drift = 0.25
        else:
            beta_drift = 0.4

        new_heading = (heading + beta_drift * dt) % 360

        # 速度基本保持
        if lat > 30:
            speed *= 0.98  # 高纬略减速

        pt_lat, pt_lon = move_point(lat, lon, new_heading, speed * dt)
        return pt_lat, pt_lon, new_heading, speed

    def _recurve_model(self, lat: float, lon: float, heading: float,
                       speed: float, hours: float) -> Tuple[float, float, float, float]:
        """
        转向模型 — 模拟台风路径的经典抛物线/转向轨迹

        关键转向纬度约 25°N-30°N:
        - 低纬 (<25°N): 稳定 NW → 保持初始方向
        - 中纬 (25°N-30°N): 逐渐转向 N
        - 高纬 (>30°N): 转向 NE, 并入西风带
        """
        dt = hours
        recurve_lat = 28.0  # 转向纬度

        if lat < 24:
            # 低纬: 几乎不转向, 保持NW方向
            heading_change = 0.05 * dt
        elif lat < recurve_lat:
            # 接近转向区: 温和右转
            heading_change = 0.4 * dt
        elif lat < recurve_lat + 4:
            # 转向区: 加速右转
            heading_change = 1.0 * dt
            speed *= 0.98  # 转向时减速
        else:
            # 高纬: 转向NE, 并入西风带加速
            heading_change = 1.5 * dt
            speed *= 1.05  # 西风带加速

        new_heading = (heading + heading_change) % 360

        # 高纬减速因子 (摩擦)
        if lat > 35:
            speed *= 0.93

        pt_lat, pt_lon = move_point(lat, lon, new_heading, speed * dt)
        return pt_lat, pt_lon, new_heading, speed

    def _intensity_decay(self, max_wind: float, pressure: float,
                         lat: float, lon: float, prev_lat: float, prev_lon: float,
                         dt_hours: float) -> Tuple[float, float]:
        """
        强度衰减模型

        - 海面: 缓慢自然减弱或维持
        - 登陆后: 显著衰减 (陆地摩擦切断海洋能量)
        - 经过台湾: 受中央山脉摩擦, 强度明显减弱
        - 高纬: 海温降低 + 西风带切变
        """
        on_land = is_over_land(lat, lon)
        was_on_land = is_over_land(prev_lat, prev_lon)

        if on_land:
            if not was_on_land:
                # 刚登陆: 阶跃衰减 (强台风登陆衰减较慢)
                decay_rate = 0.04  # 每小时衰减4%
            else:
                # 陆地持续衰减
                decay_rate = 0.025
        else:
            # 海上: 缓慢自然变化
            if lat < 25:
                decay_rate = 0.002  # 热带海面几乎不衰减
            elif lat < 28:
                decay_rate = 0.005
            elif lat < 32:
                decay_rate = 0.01  # 东海/黄海: 海温较低
            else:
                decay_rate = 0.015  # 渤海/黄海北部

        new_wind = max_wind * (1 - decay_rate * dt_hours)

        # 海上短暂增强潜力 (低纬眼墙置换等)
        if not on_land and lat < 25 and max_wind < 55:
            new_wind = min(new_wind * 1.003, 55)

        # 气压与风速的近似关系
        wind_loss = max_wind - new_wind
        new_pressure = min(pressure + wind_loss * 2.5, 1013)

        return round(max(new_wind, 6.0), 1), round(new_pressure, 1)

    def predict_track(self,
                      lat: float,
                      lon: float,
                      heading: float,
                      speed: float,
                      intensity: float,
                      pressure: float,
                      hours: int = 168,
                      step_hours: int = 3,
                      start_time: datetime = None) -> List[Dict]:
        """
        预测台风完整路径

        Args:
            lat: 初始纬度
            lon: 初始经度
            heading: 移动方向 (度, 0=N, 90=E)
            speed: 移动速度 (km/h)
            intensity: 最大风速 (m/s)
            pressure: 中心气压 (hPa)
            hours: 预测时长
            step_hours: 时间步长
            start_time: 起始时间

        Returns:
            [{time, lat, lon, heading, speed, intensity, pressure, level, on_land,
              model_details, ...}, ...]
        """
        if start_time is None:
            start_time = datetime.now()

        track = []
        curr_lat, curr_lon = lat, lon
        curr_heading = heading
        curr_speed = speed
        curr_intensity = intensity
        curr_pressure = pressure

        # 初始点
        level_cn, level_en = get_typhoon_level(curr_intensity)
        track.append({
            "time": start_time.isoformat(),
            "hour": 0,
            "lat": curr_lat,
            "lon": curr_lon,
            "heading": curr_heading,
            "speed": curr_speed,
            "intensity": curr_intensity,
            "pressure": curr_pressure,
            "level_cn": level_cn,
            "level_en": level_en,
            "on_land": is_over_land(curr_lat, curr_lon),
            "is_landfall": False,
        })

        steps = int(hours / step_hours)

        for i in range(1, steps + 1):
            dt = step_hours
            prev_lat, prev_lon = curr_lat, curr_lon

            # === 各模型预测 ===
            c_lat, c_lon, c_hdg, c_spd = self._climatology_model(
                curr_lat, curr_lon, curr_heading, curr_speed, dt)
            s_lat, s_lon, s_hdg, s_spd = self._steering_flow_model(
                curr_lat, curr_lon, curr_heading, curr_speed, dt)
            i_lat, i_lon, i_hdg, i_spd = self._inertial_model(
                curr_lat, curr_lon, curr_heading, curr_speed, dt)
            r_lat, r_lon, r_hdg, r_spd = self._recurve_model(
                curr_lat, curr_lon, curr_heading, curr_speed, dt)

            # === 加权融合 (位置线性加权, 方向用圆形平均) ===
            w = self.model_weights
            fuse_lat = (w["climatology"] * c_lat + w["steering_flow"] * s_lat +
                        w["inertial"] * i_lat + w["recurve"] * r_lat)
            fuse_lon = (w["climatology"] * c_lon + w["steering_flow"] * s_lon +
                        w["inertial"] * i_lon + w["recurve"] * r_lon)

            # 圆形平均: 正确处理跨 0°/360° 的情况
            hdgs = [c_hdg, s_hdg, i_hdg, r_hdg]
            hwts = [w["climatology"], w["steering_flow"], w["inertial"], w["recurve"]]
            sx = sum(hwt * math.cos(math.radians(h)) for hwt, h in zip(hwts, hdgs))
            sy = sum(hwt * math.sin(math.radians(h)) for hwt, h in zip(hwts, hdgs))
            fuse_heading = math.degrees(math.atan2(sy, sx)) % 360

            fuse_speed = (w["climatology"] * c_spd + w["steering_flow"] * s_spd +
                          w["inertial"] * i_spd + w["recurve"] * r_spd)

            # === 强度衰减 ===
            new_intensity, new_pressure = self._intensity_decay(
                curr_intensity, curr_pressure, fuse_lat, fuse_lon,
                prev_lat, prev_lon, dt)

            # === 判断登陆 ===
            was_land = is_over_land(prev_lat, prev_lon)
            now_land = is_over_land(fuse_lat, fuse_lon)
            is_landfall = not was_land and now_land

            # 更新状态
            curr_lat, curr_lon = fuse_lat, fuse_lon
            curr_heading = fuse_heading
            curr_speed = fuse_speed
            curr_intensity = new_intensity
            curr_pressure = new_pressure

            level_cn, level_en = get_typhoon_level(curr_intensity)
            t = start_time + timedelta(hours=step_hours * i)

            entry = {
                "time": t.isoformat(),
                "hour": step_hours * i,
                "lat": round(curr_lat, 2),
                "lon": round(curr_lon, 2),
                "heading": round(curr_heading, 1),
                "speed": round(curr_speed, 1),
                "intensity": curr_intensity,
                "pressure": curr_pressure,
                "level_cn": level_cn,
                "level_en": level_en,
                "on_land": now_land,
                "is_landfall": is_landfall,
                "model_details": {
                    "climatology": {"lat": round(c_lat, 2), "lon": round(c_lon, 2)},
                    "steering_flow": {"lat": round(s_lat, 2), "lon": round(s_lon, 2)},
                    "inertial": {"lat": round(i_lat, 2), "lon": round(i_lon, 2)},
                    "recurve": {"lat": round(r_lat, 2), "lon": round(r_lon, 2)},
                }
            }

            track.append(entry)

            # 完全消散
            if curr_intensity < 6.0:
                break

        return track

    def get_48h_forecast(self, track: List[Dict]) -> List[Dict]:
        """提取48小时预测"""
        return [p for p in track if p["hour"] <= 48]

    def get_7day_forecast(self, track: List[Dict]) -> List[Dict]:
        """提取7天预测"""
        return [p for p in track if p["hour"] <= 168]

    def get_daily_snapshot(self, track: List[Dict]) -> List[Dict]:
        """提取每日快照 (00:00 UTC + 8)"""
        snapshots = []
        seen_days = set()
        for p in track:
            t = datetime.fromisoformat(p["time"])
            day = t.strftime("%m-%d")
            if day not in seen_days:
                snapshots.append(p)
                seen_days.add(day)
        return snapshots

    def format_track_table(self, track: List[Dict], max_points: int = 30) -> str:
        """格式化路径为表格"""
        header = f"{'时间':<22} {'时':>4} {'纬度':>8} {'经度':>8} {'方向':>6} {'速度':>6} {'风速':>6} {'气压':>6} {'等级':<10} {'陆地':>4}"
        sep = "-" * len(header)
        lines = [sep, header, sep]

        for p in track[:max_points]:
            t = datetime.fromisoformat(p["time"])
            t_str = t.strftime("%m-%d %H:%M")
            on_land = "陆" if p["on_land"] else "海"
            line = (f"{t_str:<22} {p['hour']:>4}h {p['lat']:>7.1f}°N {p['lon']:>7.1f}°E "
                    f"{p['heading']:>5.0f}° {p['speed']:>5.0f}km/h "
                    f"{p['intensity']:>5.0f}m/s {p['pressure']:>5.0f}hPa "
                    f"{p['level_cn']:<8} {on_land:>4}")
            if p["is_landfall"]:
                line += " ⚡登陆!"
            lines.append(line)

        lines.append(sep)
        return "\n".join(lines)

    def get_landfall_info(self, track: List[Dict]) -> Optional[Dict]:
        """获取登陆信息"""
        for p in track:
            if p["is_landfall"]:
                return p
        return None

    def compare_with_official(self, our_track: List[Dict],
                               official_track: List[Dict]) -> Dict:
        """与官方预报对比"""
        comparisons = []
        total_dist_error = 0
        n = 0

        for op in official_track:
            hour = op.get("hour", 0)
            # 找我们的对应时间点
            match = None
            for tp in our_track:
                if abs(tp["hour"] - hour) <= 1.5:
                    match = tp
                    break

            if match:
                dist = haversine(op["lat"], op["lon"], match["lat"], match["lon"])
                comparisons.append({
                    "hour": hour,
                    "official": {"lat": op["lat"], "lon": op["lon"]},
                    "our": {"lat": match["lat"], "lon": match["lon"]},
                    "distance_error_km": round(dist, 1),
                })
                total_dist_error += dist
                n += 1

        avg_error = round(total_dist_error / n, 1) if n > 0 else None

        return {
            "comparisons": comparisons,
            "average_distance_error_km": avg_error,
            "compared_points": n,
        }


# ===========================
# 学习训练接口
# ===========================

class TyphoonPredictTrainer:
    """台风预测训练器"""

    def __init__(self, engine: TyphoonPredictEngine = None):
        self.engine = engine or TyphoonPredictEngine()
        self.training_records = []

    def train_case(self, name: str, initial_conditions: Dict,
                   actual_track: List[Dict]) -> Dict:
        """训练单个台风案例, 对比预测与实际"""
        pred = self.engine.predict_track(
            lat=initial_conditions["lat"],
            lon=initial_conditions["lon"],
            heading=initial_conditions["heading"],
            speed=initial_conditions["speed"],
            intensity=initial_conditions["intensity"],
            pressure=initial_conditions["pressure"],
            hours=168,
            step_hours=6,
        )
        comparison = self.engine.compare_with_official(pred, actual_track)

        record = {
            "case": name,
            "initial": initial_conditions,
            "prediction": pred,
            "actual": actual_track,
            "comparison": comparison,
        }
        self.training_records.append(record)
        return record

    def get_accuracy_stats(self) -> Dict:
        """获取预测准确率统计"""
        if not self.training_records:
            return {"total_cases": 0, "average_error": None}

        errors = [r["comparison"]["average_distance_error_km"]
                  for r in self.training_records
                  if r["comparison"]["average_distance_error_km"] is not None]

        return {
            "total_cases": len(self.training_records),
            "average_error_km": round(sum(errors) / len(errors), 1) if errors else None,
            "min_error_km": round(min(errors), 1) if errors else None,
            "max_error_km": round(max(errors), 1) if errors else None,
        }


# ===========================
# 自测
# ===========================

if __name__ == "__main__":
    engine = TyphoonPredictEngine()
    print("✅ TyphoonPredictEngine 初始化成功")
    print(f"   模型权重: {engine.model_weights}")

    # 测试预测
    track = engine.predict_track(
        lat=22.2, lon=126.6, heading=315, speed=22.5,
        intensity=40.0, pressure=960, hours=24, step_hours=3,
    )
    print(f"   24小时预测: {len(track)} 个时间点")
    landfall = engine.get_landfall_info(track)
    if landfall:
        print(f"   登陆: {landfall['time']} @ {landfall['lat']}°N, {landfall['lon']}°E")
    else:
        print(f"   24小时内未登陆")
