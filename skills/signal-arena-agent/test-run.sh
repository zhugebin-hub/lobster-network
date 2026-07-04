#!/bin/bash
# Signal Arena 测试运行脚本
cd ~/.openclaw/workspace/skills/signal-arena-agent
echo "=== 测试运行 $(date) ===" >> logs/cron.log
node -e "require('./strategy').runStrategy()" 2>&1 | tee -a logs/cron.log
