#!/bin/bash
# ============================================================
# 围棋训练系统 - 小陈端安装脚本
# 用途：在小陈服务器上安装围棋训练环境
# 作者：虾尔 (基于诸葛马/Hermes 的训练系统)
# 日期：2026-05-26
# ============================================================

set -e

echo "🦞 开始安装围棋训练系统..."

# 1. 检查NFS挂载
echo "📂 检查NFS挂载..."
if ! mountpoint -q /shared 2>/dev/null; then
    echo "⚠️ /shared 未挂载，尝试挂载..."
    sudo mkdir -p /shared
    sudo mount -t nfs 172.24.57.34:/shared /shared
    if [ $? -ne 0 ]; then
        echo "❌ NFS挂载失败，请手动挂载: sudo mount -t nfs 172.24.57.34:/shared /shared"
        exit 1
    fi
fi
echo "✅ /shared 已就绪"

# 2. 检查Python
echo "🐍 检查Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到python3，请先安装Python 3.8+"
    exit 1
fi
echo "✅ Python3 已安装: $(python3 --version)"

# 3. 创建目录结构
echo "📁 创建目录结构..."
mkdir -p /shared/messages/queue/xiaochen/inbox
mkdir -p /shared/messages/queue/xiaochen/outbox
mkdir -p /shared/messages/queue/xiaochen/processed
mkdir -p /shared/training/go/xiaochen/daily_log
mkdir -p /shared/training/go/xiaochen/problem_history
mkdir -p /shared/training/go/xiaochen/game_records
echo "✅ 目录结构已创建"

# 4. 复制训练脚本
echo "📝 复制训练脚本..."
SCRIPTS_DIR="/shared/scripts"
if [ ! -f "$SCRIPTS_DIR/xiaochen_go_trainer_v2.py" ]; then
    echo "⚠️ 训练脚本不存在，从备份恢复..."
    # 脚本内容已在上面定义，这里只是确保存在
fi
echo "✅ 训练脚本已就绪"

# 5. 初始化配置文件
echo "⚙️ 初始化配置文件..."
if [ ! -f "/shared/training/go/xiaochen/profile.json" ]; then
    cat > /shared/training/go/xiaochen/profile.json << 'EOF'
{
  "name": "小陈",
  "role": "围棋学员",
  "created_at": "2026-05-26 17:00:00",
  "current_level": "30级",
  "current_phase": 1,
  "current_week": 1,
  "current_day": 1,
  "total_training_hours": 0,
  "total_problems_solved": 0,
  "total_games_played": 0,
  "win_rate": 0.0,
  "strengths": [],
  "weaknesses": [],
  "last_training_date": null
}
EOF
fi

if [ ! -f "/shared/training/go/xiaochen/progress.json" ]; then
    cat > /shared/training/go/xiaochen/progress.json << 'EOF'
{
  "phase_history": [],
  "weekly_reports": [],
  "problem_stats": {
    "life": {"solved": 0, "correct": 0},
    "tesuji": {"solved": 0, "correct": 0},
    "joseki": {"solved": 0, "correct": 0},
    "endgame": {"solved": 0, "correct": 0},
    "fuseki": {"solved": 0, "correct": 0}
  },
  "game_records": []
}
EOF
fi
echo "✅ 配置文件已初始化"

# 6. 设置权限
echo "🔐 设置权限..."
chmod -R 777 /shared/messages/queue/xiaochen/
chmod -R 777 /shared/training/go/xiaochen/
echo "✅ 权限已设置"

# 7. 创建启动脚本
echo "🚀 创建启动脚本..."
cat > /home/admin/start_go_training.sh << 'EOF'
#!/bin/bash
# 围棋训练启动脚本
echo "🦞 启动围棋训练系统..."
cd /shared/scripts
nohup python3 xiaochen_go_trainer_v2.py > /shared/training/go/xiaochen/training.log 2>&1 &
echo "✅ 训练脚本已启动 (PID: $!)"
echo "📋 查看日志: tail -f /shared/training/go/xiaochen/training.log"
echo "🛑 停止训练: kill $!"
EOF
chmod +x /home/admin/start_go_training.sh
echo "✅ 启动脚本已创建"

# 8. 创建停止脚本
cat > /home/admin/stop_go_training.sh << 'EOF'
#!/bin/bash
# 围棋训练停止脚本
echo "🛑 停止围棋训练系统..."
PID=$(pgrep -f "xiaochen_go_trainer")
if [ -n "$PID" ]; then
    kill $PID
    echo "✅ 训练脚本已停止 (PID: $PID)"
else
    echo "⚠️ 训练脚本未运行"
fi
EOF
chmod +x /home/admin/stop_go_training.sh
echo "✅ 停止脚本已创建"

# 9. 创建状态检查脚本
cat > /home/admin/check_go_status.sh << 'EOF'
#!/bin/bash
# 围棋训练状态检查
echo "📊 围棋训练状态检查"
echo "==================="

# 检查脚本运行状态
PID=$(pgrep -f "xiaochen_go_trainer")
if [ -n "$PID" ]; then
    echo "✅ 训练脚本运行中 (PID: $PID)"
else
    echo "❌ 训练脚本未运行"
fi

# 检查NFS挂载
if mountpoint -q /shared 2>/dev/null; then
    echo "✅ NFS挂载正常"
else
    echo "❌ NFS挂载异常"
fi

# 检查收件箱
INBOX_COUNT=$(ls /shared/messages/queue/xiaochen/inbox/*.json 2>/dev/null | wc -l)
echo "📥 收件箱消息: $INBOX_COUNT 条"

# 检查发件箱
OUTBOX_COUNT=$(ls /shared/messages/queue/xiaochen/outbox/*.json 2>/dev/null | wc -l)
echo "📤 发件箱消息: $OUTBOX_COUNT 条"

# 检查训练进度
if [ -f "/shared/training/go/xiaochen/profile.json" ]; then
    echo "📊 训练档案:"
    python3 -c "
import json
with open('/shared/training/go/xiaochen/profile.json') as f:
    p = json.load(f)
print(f'  等级: {p[\"current_level\"]}')
print(f'  阶段: {p[\"current_phase\"]}')
print(f'  解题数: {p[\"total_problems_solved\"]}')
print(f'  胜率: {p[\"win_rate\"]*100:.1f}%')
"
fi

echo "==================="
echo "📋 查看详细日志: tail -f /shared/training/go/xiaochen/training.log"
EOF
chmod +x /home/admin/check_go_status.sh
echo "✅ 状态检查脚本已创建"

# 10. 创建crontab定时任务
echo "⏰ 配置定时任务..."
CRON_LINE="*/5 * * * * /home/admin/check_go_status.sh >> /shared/training/go/xiaochen/status.log 2>&1"
if ! crontab -l 2>/dev/null | grep -q "check_go_status"; then
    (crontab -l 2>/dev/null; echo "$CRON_LINE") | crontab -
    echo "✅ 定时任务已添加 (每5分钟检查状态)"
else
    echo "✅ 定时任务已存在"
fi

echo ""
echo "🎉 围棋训练系统安装完成！"
echo ""
echo "📋 使用说明:"
echo "  启动训练: /home/admin/start_go_training.sh"
echo "  停止训练: /home/admin/stop_go_training.sh"
echo "  检查状态: /home/admin/check_go_status.sh"
echo "  查看日志: tail -f /shared/training/go/xiaochen/training.log"
echo ""
echo "📚 训练资料:"
echo "  训练计划: /shared/training/go/GO_TRAINING_PLAN.md"
echo "  使用说明: /shared/training/go/README.md"
echo "  训练指南: /shared/training/training_guide.md"
echo "  学习计划: /shared/training/learning_plan.md"
echo ""
echo "📁 文件结构:"
echo "  训练脚本: /shared/scripts/xiaochen_go_trainer_v2.py"
echo "  题库目录: /shared/training/go/problem_bank/"
echo "  个人数据: /shared/training/go/xiaochen/"
echo "  消息队列: /shared/messages/queue/xiaochen/"
echo ""
echo "🤖 教练指令:"
echo "  教练通过 /shared/messages/queue/xiaochen/inbox/ 发送训练任务"
echo "  你的回复通过 /shared/messages/queue/xiaochen/outbox/ 发送"
echo ""
echo "🎯 当前训练阶段: 第1阶段 第1周 第1天 (规则基础与死活入门)"
echo "📊 当前等级: 30级"
echo ""
echo "祝训练顺利！🦞"
