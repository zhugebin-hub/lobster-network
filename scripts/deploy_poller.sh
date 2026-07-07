#!/usr/bin/env bash
# 小龙虾网络 - 学员端消息轮询器部署脚本
# 用法: bash scripts/deploy_poller.sh <student_id> [--start|--stop|--status]

set -euo pipefail

STUDENT_ID="${1:-}"
ACTION="${2:-deploy}"

# 去除前缀 --
ACTION="${ACTION#--}"

if [ -z "$STUDENT_ID" ]; then
  echo "用法: $0 <student_id> [--start|--stop|--status|--deploy|--logs]"
  echo "示例: $0 xiaochen --start"
  exit 1
fi

# 配置
LOBSTER_DIR="/home/admin/lobster-network"
SERVICE_NAME="lobster-poller-${STUDENT_ID}"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
LOG_DIR="/home/admin/go-training/shared/logs"
STATE_DIR="/home/admin/go-training/shared/processed/${STUDENT_ID}"

echo "🦞 小龙虾网络 - 学员端消息轮询器部署"
echo "========================================="
echo "学员 ID: ${STUDENT_ID}"
echo "操作: ${ACTION}"
echo ""

# 创建必要目录
mkdir -p "${LOG_DIR}"
mkdir -p "${STATE_DIR}"

if [ "${ACTION}" == "deploy" ] || [ "${ACTION}" == "start" ]; then
  # 创建 systemd 服务文件（需要 sudo）
  sudo bash -c "cat > ${SERVICE_FILE} << EOF
[Unit]
Description=Lobster Network Message Poller - ${STUDENT_ID}
After=network.target

[Service]
Type=simple
User=admin
WorkingDirectory=${LOBSTER_DIR}
ExecStart=/home/admin/.hermes/hermes-agent/venv/bin/python3 ${LOBSTER_DIR}/core/student_poller_v4.py --student ${STUDENT_ID}
Restart=always
RestartSec=10
StandardOutput=append:${LOG_DIR}/${STUDENT_ID}_poller_stdout.log
StandardError=append:${LOG_DIR}/${STUDENT_ID}_poller_stderr.log

# 环境变量
Environment=PYTHONUNBUFFERED=1
Environment=LOBSTER_SHARED_DIR=/home/admin/go-training/shared

[Install]
WantedBy=multi-user.target
EOF"

  echo "✅ 服务文件已创建: ${SERVICE_FILE}"

  # 重载 systemd
  sudo systemctl daemon-reload
  echo "✅ systemd 已重载"

  # 启用服务
  sudo systemctl enable "${SERVICE_NAME}"
  echo "✅ 服务已启用（开机自启动）"
fi

if [ "${ACTION}" == "deploy" ] || [ "${ACTION}" == "start" ]; then
  # 启动服务
  sudo systemctl start "${SERVICE_NAME}"
  echo "✅ 服务已启动"

  # 等待启动
  sleep 2

  # 检查状态
  if sudo systemctl is-active --quiet "${SERVICE_NAME}"; then
    echo "✅ 服务运行正常"
  else
    echo "❌ 服务启动失败，请检查日志:"
    echo "   journalctl -u ${SERVICE_NAME} -n 20"
    exit 1
  fi
fi

if [ "${ACTION}" == "stop" ]; then
  sudo systemctl stop "${SERVICE_NAME}"
  sudo systemctl disable "${SERVICE_NAME}"
  echo "✅ 服务已停止并禁用"
fi

if [ "${ACTION}" == "status" ]; then
  echo "📊 服务状态:"
  sudo systemctl status "${SERVICE_NAME}" --no-pager || true
  echo ""
  echo "📝 最近日志:"
  sudo journalctl -u "${SERVICE_NAME}" -n 10 --no-pager || true
fi

if [ "${ACTION}" == "logs" ]; then
  sudo journalctl -u "${SERVICE_NAME}" -f
fi

echo ""
echo "========================================="
echo "常用命令:"
echo "  查看状态: bash scripts/deploy_poller.sh ${STUDENT_ID} --status"
echo "  查看日志: bash scripts/deploy_poller.sh ${STUDENT_ID} --logs"
echo "  停止服务: bash scripts/deploy_poller.sh ${STUDENT_ID} --stop"
echo "  重启服务: sudo systemctl restart ${SERVICE_NAME}"
echo ""
echo "🦞 轮询器已就绪，每 15 秒检查一次消息"
