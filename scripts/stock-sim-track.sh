#!/bin/bash
# 模拟炒股跟踪脚本 - 中国石油 601857
STOCK_CODE="sh601857"
CONFIG_FILE="/home/admin/.openclaw/workspace/sim-trade-20260609.md"

# 获取实时行情
DATA=$(curl -s "https://qt.gtimg.cn/q=${STOCK_CODE}" 2>/dev/null | iconv -f GBK -t UTF-8)
if [ -z "$DATA" ]; then
    echo "获取行情失败"
    exit 1
fi

# 解析关键字段
NAME=$(echo "$DATA" | awk -F '~' '{print $2}')
PRICE=$(echo "$DATA" | awk -F '~' '{print $4}')
PREV_CLOSE=$(echo "$DATA" | awk -F '~' '{print $5}')
OPEN=$(echo "$DATA" | awk -F '~' '{print $6}')
HIGH=$(echo "$DATA" | awk -F '~' '{print $41}')
LOW=$(echo "$DATA" | awk -F '~' '{print $42}')
CHANGE=$(echo "$DATA" | awk -F '~' '{print $31}')
CHANGE_PCT=$(echo "$DATA" | awk -F '~' '{print $32}')
VOLUME=$(echo "$DATA" | awk -F '~' '{print $7}')
TIME=$(echo "$DATA" | grep -oP '\d{8}\d{6}')

echo "股票: $NAME ($STOCK_CODE)"
echo "当前价: $PRICE"
echo "昨收: $PREV_CLOSE"
echo "今开: $OPEN"
echo "最高: $HIGH"
echo "最低: $LOW"
echo "涨跌: $CHANGE ($CHANGE_PCT%)"
echo "成交量: $VOLUME手"
echo "时间: $TIME"
