#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
小龙虾网络健康监控脚本 v1.0
============================

功能概述：
  1. 检查各节点连通性（SSH 远程探测 / 本地文件心跳）
  2. 监控每个节点消息队列深度（.shared/messages/queue/{node}/inbox/）
  3. 追踪训练活跃度（近 7 天 git log 提交数）
  4. 综合评分（0-10）：连通性 + 消息新鲜度 + 训练活跃度
  5. 输出结构化报告（JSON + 可读文本）
  6. 告警阈值：critical < 3.0 | warning < 5.0 | healthy >= 7.0

兼容要求：
  - Python 3.6+（不使用 capture_output=True，改用 stdout/stderr=PIPE）

使用方法：
  python3 scripts/network_health.py              # 完整报告
  python3 scripts/network_health.py --json       # 仅输出 JSON
  python3 scripts/network_health.py --quiet      # 静默模式（仅告警）
  python3 scripts/network_health.py --timeout 8  # 自定义 SSH 超时（秒）

作者：Hermes / 小龙虾网络运维团队
"""

import json
import os
import sys
import subprocess
import time
import glob
from datetime import datetime, timedelta
from pathlib import Path

# ==============================================================================
#  全局配置
# ==============================================================================

# 仓库根目录（脚本上两级即为 lobster-network 根）
REPO_ROOT = Path(__file__).resolve().parent.parent

# 消息队列根目录
QUEUE_ROOT = REPO_ROOT / ".shared" / "messages" / "queue"

# SSH 私钥路径
SSH_KEY = os.path.expanduser("~/.ssh/id_rsa_hermes")

# 默认 SSH 连接超时（秒）
DEFAULT_SSH_TIMEOUT = 10

# 告警阈值
THRESHOLD_CRITICAL = 3.0   # 严重：分数 < 3.0
THRESHOLD_WARNING  = 5.0   # 警告：分数 < 5.0
THRESHOLD_HEALTHY  = 7.0   # 健康：分数 >= 7.0

# 心跳文件超时（秒）——超过此时间认为节点离线
HEARTBEAT_TIMEOUT_SEC = 600  # 10 分钟

# 消息新鲜度窗口（小时）
MSG_FRESHNESS_HOURS = 24

# 训练活跃度窗口（天）
TRAINING_WINDOW_DAYS = 7

# ==============================================================================
#  节点配置
# ==============================================================================

NODES = {
    "hermes": {
        "display_name": "诸葛马/Hermes",
        "role": "coach",          # 教练节点
        "type": "local",          # 本地，无需 SSH
        "host": None,
        "user": None,
        "ssh_key": None,
    },
    "xiaochen": {
        "display_name": "小陈",
        "role": "student",
        "type": "remote_ssh",
        "host": "121.43.80.231",
        "user": "admin",
        "ssh_key": SSH_KEY,
    },
    "zhuguxia": {
        "display_name": "诸葛虾",
        "role": "student",
        "type": "remote_ssh",
        "host": "60.205.139.51",
        "user": "admin",
        "ssh_key": SSH_KEY,
    },
    "qoder": {
        "display_name": "Qoder小龙虾",
        "role": "student",
        "type": "local",          # 本地节点
        "host": None,
        "user": None,
        "ssh_key": None,
    },
    "zhugema": {
        "display_name": "诸葛马(远端)",
        "role": "student",
        "type": "remote_ssh",
        "host": "47.93.6.57",
        "user": "admin",
        "ssh_key": SSH_KEY,
    },
    "zhugebin-001": {
        "display_name": "诸葛斌",
        "role": "admin",
        "type": "local",          # 本地 macOS 节点
        "host": None,
        "user": None,
        "ssh_key": None,
    },
}


# ==============================================================================
#  工具函数
# ==============================================================================

def ts_now():
    """获取当前时间戳字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_iso_time(time_str):
    """
    解析 ISO 格式时间字符串（兼容 Python 3.6）
    支持多种格式：带/不带微秒、带/不带时区
    """
    if not time_str:
        return None
    for fmt in (
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
    ):
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    return None


def ssh_ping(host, user, ssh_key, timeout=DEFAULT_SSH_TIMEOUT):
    """
    通过 SSH 探测远程节点是否可达。

    返回值：
      (bool, str)  —— (是否在线, 描述信息)
    """
    if not host or not user:
        return False, "缺少主机或用户配置"

    cmd = [
        "ssh",
        "-i", ssh_key,
        "-o", "StrictHostKeyChecking=no",
        "-o", "ConnectTimeout=%d" % timeout,
        "-o", "BatchMode=yes",
        "%s@%s" % (user, host),
        "echo HEALTHY && uptime",
    ]
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = proc.communicate(timeout=timeout + 5)
        stdout_str = stdout.decode("utf-8", errors="replace").strip()
        stderr_str = stderr.decode("utf-8", errors="replace").strip()

        if proc.returncode == 0 and "HEALTHY" in stdout_str:
            # 提取 uptime 信息
            uptime_info = stdout_str.replace("HEALTHY", "").strip()
            return True, "SSH 可达 (%s)" % uptime_info[:80]
        else:
            # 分析错误原因
            reason = "SSH 连接失败 (rc=%d)" % proc.returncode
            if "Connection refused" in stderr_str:
                reason = "SSH 连接被拒绝"
            elif "Connection timed out" in stderr_str:
                reason = "SSH 连接超时"
            elif "Permission denied" in stderr_str:
                reason = "SSH 认证失败"
            elif "No route to host" in stderr_str:
                reason = "无路由到主机"
            elif "Could not resolve" in stderr_str:
                reason = "无法解析主机名"
            return False, reason

    except subprocess.TimeoutExpired:
        proc.kill()
        return False, "SSH 探测超时 (%ds)" % timeout
    except FileNotFoundError:
        return False, "ssh 命令不存在"
    except Exception as e:
        return False, "SSH 探测异常: %s" % str(e)


def check_local_heartbeat(node_id):
    """
    检查本地节点的文件心跳。
    查找 .shared/messages/queue/{node_id}/inbox/ 或 sent/ 中最新文件的修改时间。

    返回值：
      (bool, str)  —— (是否活跃, 描述信息)
    """
    # 检查多个可能的路径
    search_paths = []
    queue_dir = QUEUE_ROOT / node_id
    if queue_dir.exists():
        search_paths.append(queue_dir)

    # 也检查 from-{node} 目录
    from_dir = REPO_ROOT / ".shared" / "messages" / ("from-%s" % node_id)
    if from_dir.exists():
        search_paths.append(from_dir)

    # 也检查 to-{node} 目录
    to_dir = REPO_ROOT / ".shared" / "messages" / ("to-%s" % node_id)
    if to_dir.exists():
        search_paths.append(to_dir)

    if not search_paths:
        return False, "无消息目录"

    latest_mtime = 0
    latest_file = ""
    for search_dir in search_paths:
        # 递归查找所有文件
        for root, dirs, files in os.walk(str(search_dir)):
            for fname in files:
                fpath = os.path.join(root, fname)
                try:
                    mtime = os.path.getmtime(fpath)
                    if mtime > latest_mtime:
                        latest_mtime = mtime
                        latest_file = fname
                except OSError:
                    continue

    if latest_mtime == 0:
        return False, "目录为空，无文件活动"

    age_seconds = time.time() - latest_mtime
    age_hours = age_seconds / 3600.0

    if age_seconds < HEARTBEAT_TIMEOUT_SEC:
        return True, "活跃 (%.1f分钟前, %s)" % (age_seconds / 60.0, latest_file)
    elif age_hours < MSG_FRESHNESS_HOURS:
        return True, "较活跃 (%.1f小时前, %s)" % (age_hours, latest_file)
    else:
        return False, "不活跃 (%.1f小时前, %s)" % (age_hours, latest_file)


# ==============================================================================
#  检查项 1：节点连通性
# ==============================================================================

def check_connectivity(node_id, config, ssh_timeout=DEFAULT_SSH_TIMEOUT):
    """
    检查节点连通性。

    返回：
      dict 包含 online (bool), method (str), detail (str)
    """
    node_type = config.get("type", "unknown")

    if node_type == "local":
        # 本地节点 —— 检查文件心跳
        online, detail = check_local_heartbeat(node_id)
        return {
            "online": online,
            "method": "file_heartbeat",
            "detail": detail,
        }
    elif node_type == "remote_ssh":
        # 远程节点 —— SSH 探测
        online, detail = ssh_ping(
            host=config["host"],
            user=config["user"],
            ssh_key=config.get("ssh_key", SSH_KEY),
            timeout=ssh_timeout,
        )
        return {
            "online": online,
            "method": "ssh_ping",
            "detail": detail,
        }
    else:
        return {
            "online": False,
            "method": "unknown",
            "detail": "未知节点类型: %s" % node_type,
        }


# ==============================================================================
#  检查项 2：消息队列深度
# ==============================================================================

def check_message_queue(node_id):
    """
    检查节点消息队列状态。

    检查目录：.shared/messages/queue/{node_id}/inbox/
    统计：消息总数、未读消息数、最新消息时间、队列深度

    返回：
      dict
    """
    inbox_dir = QUEUE_ROOT / node_id / "inbox"
    sent_dir = QUEUE_ROOT / node_id / "sent"

    result = {
        "inbox_count": 0,
        "sent_count": 0,
        "latest_message_age_hours": None,
        "latest_message_file": None,
        "queue_depth": 0,       # 未处理的 inbox 消息数
        "fresh": False,         # 是否有 24 小时内的新消息
    }

    # 统计 inbox
    if inbox_dir.exists():
        inbox_files = []
        for fpath in inbox_dir.iterdir():
            if fpath.is_file():
                try:
                    mtime = fpath.stat().st_mtime
                    inbox_files.append((fpath.name, mtime))
                except OSError:
                    continue
        result["inbox_count"] = len(inbox_files)
        result["queue_depth"] = len(inbox_files)  # 所有 inbox 消息视为待处理

        if inbox_files:
            inbox_files.sort(key=lambda x: x[1], reverse=True)
            latest_name, latest_mtime = inbox_files[0]
            result["latest_message_file"] = latest_name
            age_hours = (time.time() - latest_mtime) / 3600.0
            result["latest_message_age_hours"] = round(age_hours, 2)
            result["fresh"] = age_hours < MSG_FRESHNESS_HOURS

    # 统计 sent
    if sent_dir.exists():
        sent_files = [f for f in sent_dir.iterdir() if f.is_file()]
        result["sent_count"] = len(sent_files)

    return result


# ==============================================================================
#  检查项 3：训练活跃度（git log）
# ==============================================================================

def check_training_activity():
    """
    通过 git log 检查仓库近 7 天的训练活跃度。

    返回：
      dict 包含 commit_count, latest_commit_age_hours, authors, active_days
    """
    result = {
        "commit_count": 0,
        "latest_commit_age_hours": None,
        "authors": [],
        "active_days": 0,
        "recent_commits": [],
        "active": False,
    }

    since_date = (datetime.now() - timedelta(days=TRAINING_WINDOW_DAYS)).strftime("%Y-%m-%d")

    try:
        # 获取近 7 天的 git log
        proc = subprocess.Popen(
            [
                "git", "log",
                "--since=%s" % since_date,
                "--format=%H|%an|%ae|%aI|%s",
                "--all",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=str(REPO_ROOT),
        )
        stdout, stderr = proc.communicate(timeout=30)

        if proc.returncode != 0:
            result["error"] = "git log 执行失败: %s" % stderr.decode("utf-8", errors="replace")[:200]
            return result

        lines = stdout.decode("utf-8", errors="replace").strip().split("\n")
        lines = [l for l in lines if l.strip()]

        if not lines:
            return result

        result["commit_count"] = len(lines)
        authors_set = set()
        days_set = set()
        latest_ts = None

        for line in lines:
            parts = line.split("|", 4)
            if len(parts) >= 5:
                commit_hash, author_name, author_email, author_date, subject = parts
                authors_set.add(author_name)
                # 解析日期（去除时区信息以便与 naive datetime 比较）
                parsed = parse_iso_time(author_date)
                if parsed:
                    # 统一为 naive datetime（去掉时区信息）
                    if parsed.tzinfo is not None:
                        parsed = parsed.replace(tzinfo=None)
                    day_str = parsed.strftime("%Y-%m-%d")
                    days_set.add(day_str)
                    if latest_ts is None or parsed > latest_ts:
                        latest_ts = parsed

            # 收集最近 5 条提交
            if len(result["recent_commits"]) < 5:
                parts_short = line.split("|", 4)
                if len(parts_short) >= 5:
                    result["recent_commits"].append({
                        "hash": parts_short[0][:8],
                        "author": parts_short[1],
                        "date": parts_short[3][:19],
                        "subject": parts_short[4][:80],
                    })

        result["authors"] = sorted(list(authors_set))
        result["active_days"] = len(days_set)

        if latest_ts:
            age_hours = (datetime.now() - latest_ts).total_seconds() / 3600.0
            result["latest_commit_age_hours"] = round(age_hours, 2)

        # 判定是否活跃：7 天内有 3 天以上有提交，或至少有 3 次提交
        result["active"] = (
            result["active_days"] >= 3 or result["commit_count"] >= 3
        )

    except subprocess.TimeoutExpired:
        result["error"] = "git log 执行超时"
    except FileNotFoundError:
        result["error"] = "git 命令不存在"
    except Exception as e:
        result["error"] = "训练活跃度检查异常: %s" % str(e)

    return result


# ==============================================================================
#  综合健康评分
# ==============================================================================

def calculate_health_score(connectivity, queue_info, training_info):
    """
    综合计算节点健康分数（0-10）。

    权重分配：
      - 连通性（connectivity）:  4.0 分（40%）
      - 消息新鲜度（freshness）: 3.0 分（30%）
      - 训练活跃度（activity）:  3.0 分（30%）

    返回：
      float  —— 0.0 ~ 10.0
    """
    score = 0.0

    # ── 连通性得分（0 ~ 4.0）──
    if connectivity.get("online"):
        score += 4.0
    # 如果在线但方法为 file_heartbeat 且详情含"不活跃"，扣 1 分
    if connectivity.get("online") and "不活跃" in connectivity.get("detail", ""):
        score -= 1.0

    # ── 消息新鲜度得分（0 ~ 3.0）──
    freshness = 0.0
    age_hours = queue_info.get("latest_message_age_hours")
    if age_hours is not None:
        if age_hours < 1:
            freshness = 3.0       # 1 小时内有消息：满分
        elif age_hours < 6:
            freshness = 2.5       # 6 小时内
        elif age_hours < 24:
            freshness = 2.0       # 24 小时内
        elif age_hours < 72:
            freshness = 1.0       # 3 天内
        elif age_hours < 168:
            freshness = 0.5       # 7 天内
        else:
            freshness = 0.0       # 超过 7 天
    else:
        # 无消息记录
        freshness = 0.0

    # 额外：如果 inbox 堆积过多（>20 条未处理），扣 0.5 分
    if queue_info.get("queue_depth", 0) > 20:
        freshness = max(0, freshness - 0.5)

    score += freshness

    # ── 训练活跃度得分（0 ~ 3.0）──
    activity = 0.0
    commit_count = training_info.get("commit_count", 0)
    active_days = training_info.get("active_days", 0)

    if commit_count > 0:
        # 提交数量分
        if commit_count >= 20:
            activity += 1.5
        elif commit_count >= 10:
            activity += 1.0
        elif commit_count >= 5:
            activity += 0.7
        elif commit_count >= 2:
            activity += 0.4
        else:
            activity += 0.2

        # 活跃天数分
        if active_days >= 5:
            activity += 1.5
        elif active_days >= 3:
            activity += 1.0
        elif active_days >= 2:
            activity += 0.5
        else:
            activity += 0.2

    # 限制最高 3.0
    activity = min(activity, 3.0)
    score += activity

    # 确保范围 [0, 10]
    score = max(0.0, min(10.0, score))
    return round(score, 2)


def get_alert_level(score):
    """
    根据分数判定告警等级。

    返回：
      str  —— "critical" / "warning" / "healthy"
    """
    if score < THRESHOLD_CRITICAL:
        return "critical"
    elif score < THRESHOLD_WARNING:
        return "warning"
    else:
        return "healthy"


def get_alert_icon(level):
    """获取告警图标"""
    icons = {
        "critical": "[CRITICAL]",
        "warning":  "[WARNING]",
        "healthy":  "[HEALTHY]",
    }
    return icons.get(level, "[UNKNOWN]")


# ==============================================================================
#  报告生成
# ==============================================================================

def generate_node_report(node_id, config, connectivity, queue_info, score, ssh_timeout):
    """
    为单个节点生成完整检测数据。

    返回：
      dict  —— 节点检测报告
    """
    alert_level = get_alert_level(score)
    return {
        "node_id": node_id,
        "display_name": config.get("display_name", node_id),
        "role": config.get("role", "unknown"),
        "type": config.get("type", "unknown"),
        "host": config.get("host"),
        "connectivity": connectivity,
        "message_queue": queue_info,
        "health_score": score,
        "alert_level": alert_level,
        "alert_icon": get_alert_icon(alert_level),
    }


def generate_training_section(training_info):
    """生成训练活跃度部分的数据"""
    return {
        "commit_count_7d": training_info.get("commit_count", 0),
        "active_days": training_info.get("active_days", 0),
        "authors": training_info.get("authors", []),
        "latest_commit_age_hours": training_info.get("latest_commit_age_hours"),
        "active": training_info.get("active", False),
        "recent_commits": training_info.get("recent_commits", []),
        "error": training_info.get("error"),
    }


def generate_network_score(node_reports):
    """
    计算网络整体健康分数（所有节点的平均分，教练节点权重更高）。

    返回：
      float
    """
    if not node_reports:
        return 0.0

    total_weight = 0.0
    weighted_sum = 0.0

    for report in node_reports:
        # 教练节点权重 2.0，管理员 1.5，学员 1.0
        role = report.get("role", "student")
        if role == "coach":
            weight = 2.0
        elif role == "admin":
            weight = 1.5
        else:
            weight = 1.0

        weighted_sum += report["health_score"] * weight
        total_weight += weight

    if total_weight == 0:
        return 0.0

    return round(weighted_sum / total_weight, 2)


# ==============================================================================
#  输出格式化
# ==============================================================================

def format_text_report(node_reports, training_section, network_score, report_time):
    """
    生成人类可读的文本报告（兼容 Hermes 日报风格）。

    返回：
      str
    """
    w = 64  # 分隔线宽度

    lines = []
    lines.append("")
    lines.append("=" * w)
    lines.append("  小龙虾网络健康报告")
    lines.append("  %s" % report_time)
    lines.append("=" * w)
    lines.append("")

    # ── 网络总览 ──
    net_level = get_alert_level(network_score)
    lines.append("  网络整体健康分数: %.2f / 10.00  %s" % (
        network_score, get_alert_icon(net_level)))
    lines.append("")

    total = len(node_reports)
    online_count = sum(1 for r in node_reports if r["connectivity"]["online"])
    critical_count = sum(1 for r in node_reports if r["alert_level"] == "critical")
    warning_count = sum(1 for r in node_reports if r["alert_level"] == "warning")
    healthy_count = sum(1 for r in node_reports if r["alert_level"] == "healthy")

    lines.append("  节点总数: %d" % total)
    lines.append("  在线节点: %d" % online_count)
    lines.append("  健康分布: %d healthy / %d warning / %d critical" % (
        healthy_count, warning_count, critical_count))
    lines.append("")
    lines.append("-" * w)

    # ── 各节点详情 ──
    for report in node_reports:
        nid = report["node_id"]
        name = report["display_name"]
        score = report["health_score"]
        level = report["alert_level"]
        icon = report["alert_icon"]

        lines.append("")
        lines.append("  [%s] %s (%s)" % (icon, name, nid))
        lines.append("  " + "-" * 40)
        lines.append("    角色: %s | 类型: %s" % (report["role"], report["type"]))

        # 连通性
        conn = report["connectivity"]
        conn_status = "ONLINE" if conn["online"] else "OFFLINE"
        lines.append("    连通性: %s (%s)" % (conn_status, conn["detail"]))
        lines.append("    检测方法: %s" % conn["method"])

        # 消息队列
        mq = report["message_queue"]
        lines.append("    消息队列: inbox=%d, sent=%d, 待处理=%d" % (
            mq["inbox_count"], mq["sent_count"], mq["queue_depth"]))
        if mq["latest_message_age_hours"] is not None:
            lines.append("    最新消息: %.1f小时前 (%s)" % (
                mq["latest_message_age_hours"],
                mq.get("latest_message_file", "N/A")))
            fresh_label = "FRESH" if mq["fresh"] else "STALE"
            lines.append("    消息新鲜度: %s" % fresh_label)
        else:
            lines.append("    最新消息: 无记录")

        # 健康分数
        lines.append("    健康分数: %.2f / 10.00" % score)
        lines.append("")

    # ── 训练活跃度 ──
    lines.append("-" * w)
    lines.append("")
    lines.append("  训练活跃度（近 %d 天 Git 提交）" % TRAINING_WINDOW_DAYS)
    lines.append("  " + "-" * 40)

    ts = training_section
    lines.append("    提交总数: %d" % ts["commit_count_7d"])
    lines.append("    活跃天数: %d" % ts["active_days"])
    lines.append("    贡献者: %s" % (", ".join(ts["authors"]) if ts["authors"] else "无"))
    if ts["latest_commit_age_hours"] is not None:
        lines.append("    最近提交: %.1f小时前" % ts["latest_commit_age_hours"])
    lines.append("    活跃状态: %s" % ("ACTIVE" if ts["active"] else "INACTIVE"))

    if ts.get("recent_commits"):
        lines.append("")
        lines.append("    最近提交记录:")
        for c in ts["recent_commits"]:
            lines.append("      %s %s [%s] %s" % (
                c["hash"], c["date"][:10], c["author"][:10], c["subject"][:50]))

    if ts.get("error"):
        lines.append("    [ERROR] %s" % ts["error"])

    # ── 告警摘要 ──
    alerts = [r for r in node_reports if r["alert_level"] in ("critical", "warning")]
    if alerts:
        lines.append("")
        lines.append("-" * w)
        lines.append("")
        lines.append("  *** 告警摘要 ***")
        lines.append("")
        for r in alerts:
            lines.append("    %s %s (%s): %.2f分 - %s" % (
                r["alert_icon"], r["display_name"], r["node_id"],
                r["health_score"], r["connectivity"]["detail"]))

    # ── 建议 ──
    lines.append("")
    lines.append("-" * w)
    lines.append("")
    lines.append("  优化建议:")
    lines.append("")

    suggestions = []
    for r in node_reports:
        if r["alert_level"] == "critical":
            if not r["connectivity"]["online"]:
                suggestions.append("  - [%s] 节点离线，请检查网络连接和 SSH 服务" % r["display_name"])
            if r["message_queue"]["inbox_count"] > 20:
                suggestions.append("  - [%s] 消息堆积 %d 条，请及时处理" % (
                    r["display_name"], r["message_queue"]["inbox_count"]))
        elif r["alert_level"] == "warning":
            if r["message_queue"].get("latest_message_age_hours", 999) > MSG_FRESHNESS_HOURS:
                suggestions.append("  - [%s] 消息超过 %d 小时未更新，请检查通信链路" % (
                    r["display_name"], int(r["message_queue"]["latest_message_age_hours"] or 0)))

    if not ts["active"]:
        suggestions.append("  - 近 %d 天训练不活跃，请推进围棋/金融等训练任务" % TRAINING_WINDOW_DAYS)

    if not suggestions:
        suggestions.append("  - 网络运行正常，继续保持！")

    for s in suggestions:
        lines.append(s)

    lines.append("")
    lines.append("=" * w)
    lines.append("  报告人: Hermes 网络健康监控")
    lines.append("  阈值: critical < %.1f | warning < %.1f | healthy >= %.1f" % (
        THRESHOLD_CRITICAL, THRESHOLD_WARNING, THRESHOLD_HEALTHY))
    lines.append("=" * w)
    lines.append("")

    return "\n".join(lines)


def format_json_report(node_reports, training_section, network_score, report_time):
    """
    生成 JSON 格式报告。

    返回：
      dict
    """
    net_level = get_alert_level(network_score)
    alerts = []
    for r in node_reports:
        if r["alert_level"] in ("critical", "warning"):
            alerts.append({
                "node_id": r["node_id"],
                "display_name": r["display_name"],
                "level": r["alert_level"],
                "score": r["health_score"],
                "detail": r["connectivity"]["detail"],
            })

    return {
        "report_type": "lobster_network_health",
        "version": "1.0.0",
        "generated_at": report_time,
        "network_score": network_score,
        "network_alert_level": net_level,
        "total_nodes": len(node_reports),
        "online_nodes": sum(1 for r in node_reports if r["connectivity"]["online"]),
        "summary": {
            "healthy": sum(1 for r in node_reports if r["alert_level"] == "healthy"),
            "warning": sum(1 for r in node_reports if r["alert_level"] == "warning"),
            "critical": sum(1 for r in node_reports if r["alert_level"] == "critical"),
        },
        "thresholds": {
            "critical_below": THRESHOLD_CRITICAL,
            "warning_below": THRESHOLD_WARNING,
            "healthy_above": THRESHOLD_HEALTHY,
        },
        "nodes": node_reports,
        "training_activity": training_section,
        "alerts": alerts,
    }


# ==============================================================================
#  主入口
# ==============================================================================

def parse_cli_args():
    """解析命令行参数"""
    args = {
        "json_only": False,
        "quiet": False,
        "ssh_timeout": DEFAULT_SSH_TIMEOUT,
    }
    argv = sys.argv[1:]
    i = 0
    while i < len(argv):
        if argv[i] == "--json":
            args["json_only"] = True
        elif argv[i] == "--quiet":
            args["quiet"] = True
        elif argv[i] == "--timeout" and i + 1 < len(argv):
            try:
                args["ssh_timeout"] = int(argv[i + 1])
            except ValueError:
                pass
            i += 1
        i += 1
    return args


def main():
    """
    主函数：遍历所有节点，执行健康检查，生成报告。
    """
    args = parse_cli_args()
    report_time = ts_now()
    ssh_timeout = args["ssh_timeout"]

    # ── 1. 检查各节点 ──
    node_reports = []

    for node_id, config in NODES.items():
        # 连通性检查
        connectivity = check_connectivity(node_id, config, ssh_timeout=ssh_timeout)

        # 消息队列检查
        queue_info = check_message_queue(node_id)

        # 计算健康分数（训练活跃度是全局的，先用占位）
        # 训练活跃度稍后统一计算
        node_reports.append({
            "node_id": node_id,
            "config": config,
            "connectivity": connectivity,
            "queue_info": queue_info,
        })

    # ── 2. 训练活跃度（全局） ──
    training_info = check_training_activity()
    training_section = generate_training_section(training_info)

    # ── 3. 计算各节点健康分数并生成报告数据 ──
    final_reports = []
    for item in node_reports:
        score = calculate_health_score(
            item["connectivity"],
            item["queue_info"],
            training_info,
        )
        report = generate_node_report(
            node_id=item["node_id"],
            config=item["config"],
            connectivity=item["connectivity"],
            queue_info=item["queue_info"],
            score=score,
            ssh_timeout=ssh_timeout,
        )
        final_reports.append(report)

    # ── 4. 网络整体分数 ──
    network_score = generate_network_score(final_reports)

    # ── 5. 输出报告 ──
    if args["json_only"]:
        # 仅输出 JSON
        json_data = format_json_report(
            final_reports, training_section, network_score, report_time)
        print(json.dumps(json_data, ensure_ascii=False, indent=2))
    elif args["quiet"]:
        # 静默模式：仅在有告警时输出
        alerts = [r for r in final_reports if r["alert_level"] in ("critical", "warning")]
        if alerts:
            text = format_text_report(
                final_reports, training_section, network_score, report_time)
            print(text)
            sys.exit(2)  # 退出码 2 表示有告警
        else:
            # 无告警，仅输出 OK
            print("[%s] 小龙虾网络健康: %.2f/10.00 - 全部正常" % (
                report_time, network_score))
            sys.exit(0)
    else:
        # 完整报告：文本 + JSON 文件
        text = format_text_report(
            final_reports, training_section, network_score, report_time)
        print(text)

        # 同时输出 JSON 到文件
        reports_dir = REPO_ROOT / "reports"
        try:
            os.makedirs(str(reports_dir), exist_ok=True)
            json_file = reports_dir / ("network_health_%s.json" % datetime.now().strftime("%Y%m%d_%H%M%S"))
            json_data = format_json_report(
                final_reports, training_section, network_score, report_time)
            with open(str(json_file), "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
            print("  JSON 报告已保存: %s" % json_file)
        except Exception as e:
            print("  [WARN] JSON 报告保存失败: %s" % str(e))

    # ── 6. 退出码 ──
    net_level = get_alert_level(network_score)
    if net_level == "critical":
        sys.exit(2)
    elif net_level == "warning":
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
