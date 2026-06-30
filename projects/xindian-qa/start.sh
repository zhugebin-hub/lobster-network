#!/bin/bash
# 信电学院 AI 知识问答系统 - 启动脚本
# 用法: ./start.sh [mode]
#   mode: server (默认) | test | status

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
AGENT_DIR="$PROJECT_DIR/agent-layer"
APP_DIR="$PROJECT_DIR/app-layer"
LOG_DIR="$PROJECT_DIR/logs"
PID_FILE="$PROJECT_DIR/qa-bot.pid"

mkdir -p "$LOG_DIR"

case "${1:-server}" in
  server)
    echo "🚀 启动信电学院 AI 知识问答系统..."
    cd "$APP_DIR"
    nohup python3 dingtalk_bot.py > "$LOG_DIR/bot.log" 2>&1 &
    echo $! > "$PID_FILE"
    echo "✅ 服务已启动 (PID: $(cat $PID_FILE))"
    echo "   日志: tail -f $LOG_DIR/bot.log"
    ;;
  
  test)
    echo "🧪 运行系统测试..."
    cd "$AGENT_DIR"
    python3 main.py
    echo ""
    echo "🧪 运行钉钉Bot模拟测试..."
    cd "$APP_DIR"
    python3 -c "
import sys; sys.path.insert(0, '.')
from dingtalk_bot import DingTalkBot
bot = DingTalkBot()
msg = {'msgtype': 'text', 'text': {'content': '触发器有哪些类型？'}, 'senderId': 'test', 'senderNick': '测试', 'conversationId': 'test_conv'}
reply = bot.process_message(msg)
print(f'📤 回复: {reply[\"text\"][\"content\"][:200]}...')
"
    ;;
  
  status)
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
      echo "✅ 服务运行中 (PID: $(cat $PID_FILE))"
    else
      echo "❌ 服务未运行"
    fi
    echo ""
    echo "📚 知识库状态:"
    python3 -c "
import sqlite3, json
db = '$(cat ~/.openclaw/config/bailian-kb.json | python3 -c \"import sys,json; print(json.load(sys.stdin)['local_db']['path'])\")'
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM documents')
doc_count = cur.fetchone()[0]
cur.execute('SELECT DISTINCT course FROM documents')
courses = [r[0] for r in cur.fetchall()]
conn.close()
print(f'   文档数: {doc_count}')
print(f'   课程: {\", \".join(courses)}')
"
    echo ""
    echo "📊 L3 记忆状态:"
    if [ -f ~/workspace/xindian-qa/l3-memory/faq_stats.json ]; then
      python3 -c "
import json
with open('~/workspace/xindian-qa/l3-memory/faq_stats.json') as f:
    stats = json.load(f)
print(f'   FAQ 条目: {len(stats)}')
with open('~/workspace/xindian-qa/l3-memory/user_profiles.json') as f:
    profiles = json.load(f)
print(f'   用户画像: {len(profiles)}')
"
    fi
    ;;
  
  stop)
    if [ -f "$PID_FILE" ]; then
      kill $(cat "$PID_FILE") 2>/dev/null && echo "✅ 服务已停止" || echo "⚠️ 服务未运行"
      rm -f "$PID_FILE"
    else
      echo "⚠️ PID 文件不存在"
    fi
    ;;
  
  *)
    echo "用法: $0 [server|test|status|stop]"
    exit 1
    ;;
esac
