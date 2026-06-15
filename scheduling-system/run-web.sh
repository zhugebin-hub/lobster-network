#!/bin/bash
# Web 版启动脚本

cd "$(dirname "$0")"
echo "🚀 启动排课系统 Web 版..."
python3 app.py
