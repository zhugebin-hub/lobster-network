#!/bin/bash
# 🦞 小龙虾网络服务器加固脚本
# 基于诸葛马反馈：SSH安全、防火墙、NFS、日志优化
# 执行: sudo bash scripts/server_hardening.sh

set -e

echo "🦞 开始服务器加固..."

# 1. SSH安全加固
echo "🔒 1. 加固SSH配置..."
sudo sed -i 's/^PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo sed -i 's/^#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/^#PasswordAuthentication yes/PasswordAuthentication no/' /etc/ssh/sshd_config
sudo systemctl restart sshd
echo "✅ SSH已加固（禁用root登录+密码认证）"

# 2. 启用防火墙
echo "🛡️ 2. 配置防火墙..."
sudo systemctl enable firewalld
sudo systemctl start firewalld
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-port=8765/tcp  # WebSocket
sudo firewall-cmd --permanent --add-port=9119/tcp  # 监控
sudo firewall-cmd --reload
echo "✅ 防火墙已启用（SSH/8765/9119放行）"

# 3. 修复NFS自挂载问题
echo "💾 3. 修复NFS配置..."
if grep -q "172.24.57.34:/shared" /etc/fstab; then
    sudo sed -i '/172.24.57.34:\/shared/d' /etc/fstab
    sudo umount /shared 2>/dev/null || true
    sudo mkdir -p /shared
    echo "✅ NFS自挂载已移除，改用本地目录"
else
    echo "ℹ️ NFS配置正常"
fi

# 4. 日志轮转优化
echo "📝 4. 优化日志配置..."
sudo journalctl --vacuum-size=500M
sudo sed -i 's/^#SystemMaxUse=.*/SystemMaxUse=500M/' /etc/systemd/journald.conf
sudo sed -i 's/^#MaxRetentionSec=.*/MaxRetentionSec=1week/' /etc/systemd/journald.conf
sudo systemctl restart systemd-journald
echo "✅ 日志已限制为500MB，保留1周"

# 5. 清理冲突Cron
echo "⏰ 5. 清理Cron冲突..."
crontab -l 2>/dev/null | grep -v "30.*broadcast" | grep -v "rsync.*block" | crontab - 2>/dev/null || true
echo "✅ 冲突Cron已清理"

echo "🎉 服务器加固完成！请重启验证: sudo reboot"
