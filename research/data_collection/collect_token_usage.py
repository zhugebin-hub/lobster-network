#!/usr/bin/env python3
"""
OpenClaw Token Usage Data Collector
用于收集 token 消耗数据，支持算力调度研究
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

# 数据库配置
DB_PATH = Path(__file__).parent / "token_usage.db"

def init_db():
    """初始化数据库"""
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
            response_time_ms INTEGER
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
            channel TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def record_token_usage(session_key, model, input_tokens, output_tokens, 
                       cost, task_type="unknown", channel="dingtalk", 
                       response_time_ms=0):
    """记录一次 token 使用"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO token_usage 
        (timestamp, session_key, model, input_tokens, output_tokens, 
         total_tokens, cost, task_type, channel, response_time_ms)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
        response_time_ms
    ))
    
    conn.commit()
    conn.close()

def record_api_call(api_name, endpoint, request_size=0, response_size=0,
                    latency_ms=0, status_code=200, channel="dingtalk"):
    """记录一次 API 调用"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO api_calls
        (timestamp, api_name, endpoint, request_size, response_size,
         latency_ms, status_code, channel)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().isoformat(),
        api_name,
        endpoint,
        request_size,
        response_size,
        latency_ms,
        status_code,
        channel
    ))
    
    conn.commit()
    conn.close()

def get_usage_stats(start_date=None, end_date=None):
    """获取使用统计"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as calls,
            SUM(total_tokens) as total_tokens,
            AVG(total_tokens) as avg_tokens,
            SUM(cost) as total_cost,
            AVG(response_time_ms) as avg_response_time
        FROM token_usage
        WHERE 1=1
    """
    params = []
    
    if start_date:
        query += " AND timestamp >= ?"
        params.append(start_date)
    if end_date:
        query += " AND timestamp <= ?"
        params.append(end_date)
    
    query += " GROUP BY DATE(timestamp) ORDER BY date"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "date": row[0],
            "calls": row[1],
            "total_tokens": row[2],
            "avg_tokens": row[3],
            "total_cost": row[4],
            "avg_response_time": row[5]
        }
        for row in results
    ]

def get_hourly_pattern(days=7):
    """获取小时级使用模式（用于负载预测）"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            strftime('%H', timestamp) as hour,
            strftime('%w', timestamp) as weekday,
            COUNT(*) as calls,
            SUM(total_tokens) as total_tokens,
            AVG(response_time_ms) as avg_response_time
        FROM token_usage
        WHERE timestamp >= datetime('now', ?)
        GROUP BY hour, weekday
        ORDER BY weekday, hour
    """, (f"-{days} days",))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            "hour": int(row[0]),
            "weekday": int(row[1]),
            "calls": row[2],
            "total_tokens": row[3],
            "avg_response_time": row[4]
        }
        for row in results
    ]

if __name__ == "__main__":
    # 初始化数据库
    init_db()
    print(f"数据库初始化完成：{DB_PATH}")
    
    # 测试记录
    record_token_usage(
        session_key="test_session",
        model="dashscope-coding/qwen3.5-plus",
        input_tokens=1000,
        output_tokens=500,
        cost=0.015,
        task_type="research_planning",
        response_time_ms=2300
    )
    
    record_api_call(
        api_name="message.send",
        endpoint="/v1/messages/send",
        request_size=2048,
        response_size=512,
        latency_ms=150,
        channel="dingtalk"
    )
    
    print("测试数据写入完成")
    
    # 获取统计
    stats = get_usage_stats()
    print(f"\n使用统计：{json.dumps(stats, indent=2, ensure_ascii=False)}")
    
    # 获取小时模式
    pattern = get_hourly_pattern()
    print(f"\n小时模式（前 10 条）：{json.dumps(pattern[:10], indent=2, ensure_ascii=False)}")
