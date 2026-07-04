#!/usr/bin/env python3
"""
OpenClaw Token Usage Auto-Collector
自动采集 OpenClaw 会话的 token 使用数据

使用方法：
1. 手动调用：每次会话结束后调用 record_session()
2. 定时任务：设置 cron 定期执行

集成到 OpenClaw 会话：
- 在会话结束时自动调用 record_session()
- 记录 model, tokens, cost, task_type 等信息
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "token_usage.db"


def init_db():
    """初始化数据库（如果不存在）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS token_usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            session_key TEXT,
            model TEXT,
            input_tokens INTEGER,
            output_tokens INTEGER,
            total_tokens INTEGER,
            cost REAL,
            task_type TEXT,
            channel TEXT,
            response_time_ms INTEGER,
            user_id TEXT,
            message_id TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS api_calls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            api_name TEXT,
            endpoint TEXT,
            request_size INTEGER,
            response_size INTEGER,
            latency_ms INTEGER,
            status_code INTEGER,
            channel TEXT,
            user_id TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hourly_stats (
            date_hour TEXT PRIMARY KEY,
            total_calls INTEGER,
            total_tokens INTEGER,
            total_cost REAL,
            avg_response_time REAL,
            unique_users INTEGER
        )
    """)
    
    conn.commit()
    conn.close()


def record_session(session_key: str, model: str, input_tokens: int, 
                   output_tokens: int, cost: float, task_type: str = "unknown",
                   channel: str = "dingtalk", response_time_ms: int = 0,
                   user_id: str = "", message_id: str = ""):
    """
    记录一次会话的 token 使用
    
    参数:
        session_key: 会话标识
        model: 使用的模型
        input_tokens: 输入 token 数
        output_tokens: 输出 token 数
        cost: 成本（元）
        task_type: 任务类型（research/chat/code/analysis 等）
        channel: 渠道（dingtalk/wechat 等）
        response_time_ms: 响应时间（毫秒）
        user_id: 用户 ID
        message_id: 消息 ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO token_usage 
        (timestamp, session_key, model, input_tokens, output_tokens, 
         total_tokens, cost, task_type, channel, response_time_ms,
         user_id, message_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        session_key,
        model,
        input_tokens,
        output_tokens,
        input_tokens + output_tokens,
        cost,
        task_type,
        channel,
        response_time_ms,
        user_id,
        message_id
    ))
    
    conn.commit()
    conn.close()
    
    # 更新小时统计
    _update_hourly_stats()


def record_api_call(api_name: str, endpoint: str, request_size: int = 0, 
                    response_size: int = 0, latency_ms: int = 0, 
                    status_code: int = 200, channel: str = "dingtalk",
                    user_id: str = ""):
    """
    记录一次 API 调用
    
    参数:
        api_name: API 名称（如 message.send, sessions_spawn 等）
        endpoint: API 端点
        request_size: 请求大小（字节）
        response_size: 响应大小（字节）
        latency_ms: 延迟（毫秒）
        status_code: 状态码
        channel: 渠道
        user_id: 用户 ID
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO api_calls
        (timestamp, api_name, endpoint, request_size, response_size,
         latency_ms, status_code, channel, user_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        api_name,
        endpoint,
        request_size,
        response_size,
        latency_ms,
        status_code,
        channel,
        user_id
    ))
    
    conn.commit()
    conn.close()


def _update_hourly_stats():
    """更新小时级统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取当前小时
    current_hour = datetime.now().strftime("%Y-%m-%d-%H")
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_calls,
            SUM(total_tokens) as total_tokens,
            SUM(cost) as total_cost,
            AVG(response_time_ms) as avg_response_time,
            COUNT(DISTINCT user_id) as unique_users
        FROM token_usage
        WHERE strftime('%Y-%m-%d-%H', timestamp) = ?
    """, (current_hour,))
    
    row = cursor.fetchone()
    
    cursor.execute("""
        INSERT OR REPLACE INTO hourly_stats
        (date_hour, total_calls, total_tokens, total_cost, avg_response_time, unique_users)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        current_hour,
        row[0] or 0,
        row[1] or 0,
        row[2] or 0.0,
        row[3] or 0.0,
        row[4] or 0
    ))
    
    conn.commit()
    conn.close()


def get_daily_report(date: str = None) -> dict:
    """
    获取日报
    
    参数:
        date: 日期字符串（YYYY-MM-DD），默认为今天
    """
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 总体统计
    cursor.execute("""
        SELECT 
            COUNT(*) as total_calls,
            SUM(total_tokens) as total_tokens,
            SUM(cost) as total_cost,
            AVG(response_time_ms) as avg_response_time,
            COUNT(DISTINCT user_id) as unique_users
        FROM token_usage
        WHERE DATE(timestamp) = ?
    """, (date,))
    
    row = cursor.fetchone()
    
    # 按任务类型统计
    cursor.execute("""
        SELECT 
            task_type,
            COUNT(*) as calls,
            SUM(total_tokens) as tokens,
            SUM(cost) as cost
        FROM token_usage
        WHERE DATE(timestamp) = ?
        GROUP BY task_type
    """, (date,))
    
    by_type = cursor.fetchall()
    
    # 按小时统计
    cursor.execute("""
        SELECT 
            strftime('%H', timestamp) as hour,
            COUNT(*) as calls
        FROM token_usage
        WHERE DATE(timestamp) = ?
        GROUP BY hour
        ORDER BY hour
    """, (date,))
    
    by_hour = cursor.fetchall()
    
    conn.close()
    
    return {
        "date": date,
        "summary": {
            "total_calls": row[0] or 0,
            "total_tokens": row[1] or 0,
            "total_cost": row[2] or 0.0,
            "avg_response_time": row[3] or 0.0,
            "unique_users": row[4] or 0
        },
        "by_type": [
            {"type": r[0], "calls": r[1], "tokens": r[2], "cost": r[3]}
            for r in by_type
        ],
        "by_hour": [
            {"hour": r[0], "calls": r[1]}
            for r in by_hour
        ]
    }


def get_load_pattern(days: int = 7) -> list:
    """
    获取负载模式（用于预测）
    
    参数:
        days: 分析的天数
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            strftime('%w', timestamp) as weekday,
            strftime('%H', timestamp) as hour,
            COUNT(*) as calls,
            SUM(total_tokens) as tokens,
            AVG(response_time_ms) as avg_latency
        FROM token_usage
        WHERE timestamp >= datetime('now', ?)
        GROUP BY weekday, hour
        ORDER BY weekday, hour
    """, (f"-{days} days",))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "weekday": int(r[0]),
            "hour": int(r[1]),
            "calls": r[2],
            "tokens": r[3],
            "avg_latency": r[4]
        }
        for r in results
    ]


def export_to_csv(output_path: str = None):
    """导出数据到 CSV"""
    import csv
    
    if output_path is None:
        output_path = Path(__file__).parent / "token_usage_export.csv"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM token_usage ORDER BY timestamp")
    rows = cursor.fetchall()
    
    # 获取列名
    columns = [description[0] for description in cursor.description]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)
    
    conn.close()
    print(f"数据已导出到：{output_path}")


def print_summary():
    """打印摘要报告"""
    report = get_daily_report()
    
    print(f"\n{'='*50}")
    print(f"📊 OpenClaw Token 使用日报 ({report['date']})")
    print(f"{'='*50}")
    print(f"总会话数：{report['summary']['total_calls']}")
    print(f"总 Token 数：{report['summary']['total_tokens']:,}")
    print(f"总成本：¥{report['summary']['total_cost']:.4f}")
    print(f"平均响应时间：{report['summary']['avg_response_time']:.0f}ms")
    print(f"活跃用户：{report['summary']['unique_users']}")
    
    if report['by_type']:
        print(f"\n📁 按任务类型:")
        for item in report['by_type']:
            print(f"  {item['type']}: {item['calls']} 次，{item['tokens']:,} tokens，¥{item['cost']:.4f}")
    
    if report['by_hour']:
        print(f"\n🕐 按小时分布:")
        for item in report['by_hour']:
            bar = '█' * min(item['calls'], 20)
            print(f"  {item['hour']}:00 {bar} ({item['calls']})")
    
    print(f"{'='*50}\n")


if __name__ == "__main__":
    # 初始化数据库
    init_db()
    print("✅ 数据库初始化完成")
    
    # 打印摘要
    print_summary()
    
    # 获取负载模式
    pattern = get_load_pattern(7)
    print(f"📈 负载模式数据点：{len(pattern)}")
