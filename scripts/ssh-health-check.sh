#!/bin/bash
# SSH健康检查 - 每30分钟检查各节点连通性

LOG="/home/admin/.openclaw/workspace/reports/ssh-health-$(date +%Y%m%d).log"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$TIMESTAMP] SSH健康检查开始" >> $LOG

# 检查小陈
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no admin@121.43.80.231 "echo OK" >/dev/null 2>&1; then
    echo "[$TIMESTAMP] 小陈(121.43.80.231): 在线" >> $LOG
else
    echo "[$TIMESTAMP] 小陈(121.43.80.231): 离线" >> $LOG
fi

# 检查诸葛虾
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no admin@60.205.139.51 "echo OK" >/dev/null 2>&1; then
    echo "[$TIMESTAMP] 诸葛虾(60.205.139.51): 在线" >> $LOG
else
    echo "[$TIMESTAMP] 诸葛虾(60.205.139.51): 离线" >> $LOG
fi

# 检查诸葛马
if ssh -o ConnectTimeout=10 -o StrictHostKeyChecking=no admin@172.24.57.34 "echo OK" >/dev/null 2>&1; then
    echo "[$TIMESTAMP] 诸葛马(172.24.57.34): 在线" >> $LOG
else
    echo "[$TIMESTAMP] 诸葛马(172.24.57.34): 离线" >> $LOG
fi

echo "[$TIMESTAMP] SSH健康检查完成" >> $LOG
