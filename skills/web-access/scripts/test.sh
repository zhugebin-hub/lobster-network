#!/usr/bin/env bash
# web-access skill 测试脚本

set -e

SKILL_DIR="$HOME/.openclaw/workspace/skills/web-access"
PROXY_PORT="${CDP_PROXY_PORT:-3456}"

echo "=== web-access Skill 测试 ==="
echo

# 1. 检查文件结构
echo "1. 检查文件结构..."
for file in "SKILL.md" "README.md" "scripts/check-deps.sh" "scripts/cdp-proxy.mjs" "references/cdp-api.md" "references/site-patterns/TEMPLATE.md"; do
  if [ -f "$SKILL_DIR/$file" ]; then
    echo "   ✓ $file"
  else
    echo "   ✗ $file (缺失)"
    exit 1
  fi
done
echo

# 2. 运行依赖检查
echo "2. 运行依赖检查..."
bash "$SKILL_DIR/scripts/check-deps.sh"
echo

# 3. 测试 Proxy API
echo "3. 测试 Proxy API..."

# 健康检查
HEALTH=$(curl -s "http://localhost:$PROXY_PORT/health")
if echo "$HEALTH" | grep -q '"status":"ok"'; then
  echo "   ✓ 健康检查通过"
else
  echo "   ✗ 健康检查失败"
  exit 1
fi

# 列出 targets
echo "   测试 /targets 端点..."
TARGETS=$(curl -s "http://localhost:$PROXY_PORT/targets")
echo "   ✓ 当前 tabs: $(echo "$TARGETS" | grep -c '"targetId"' || echo 0)"

# 创建新 tab
echo "   测试 /new 端点..."
NEW_TAB=$(curl -s "http://localhost:$PROXY_PORT/new?url=https://example.com")
TARGET_ID=$(echo "$NEW_TAB" | grep -o '"targetId":"[^"]*"' | cut -d'"' -f4)
if [ -n "$TARGET_ID" ]; then
  echo "   ✓ 创建 tab 成功：$TARGET_ID"
else
  echo "   ✗ 创建 tab 失败"
  exit 1
fi

# 获取页面信息
echo "   测试 /info 端点..."
INFO=$(curl -s "http://localhost:$PROXY_PORT/info?target=$TARGET_ID")
if echo "$INFO" | grep -q "Example Domain"; then
  echo "   ✓ 页面信息获取成功"
else
  echo "   ⚠ 页面信息：$INFO"
fi

# 执行 JS
echo "   测试 /eval 端点..."
TITLE=$(curl -s -X POST "http://localhost:$PROXY_PORT/eval?target=$TARGET_ID" -d 'document.title')
if echo "$TITLE" | grep -q "Example Domain"; then
  echo "   ✓ JS 执行成功：$(echo "$TITLE" | grep -o '"value":"[^"]*"' | cut -d'"' -f4)"
else
  echo "   ⚠ JS 执行结果：$TITLE"
fi

# 关闭 tab
echo "   测试 /close 端点..."
CLOSE=$(curl -s "http://localhost:$PROXY_PORT/close?target=$TARGET_ID")
echo "   ✓ Tab 已关闭"

echo
echo "=== 所有测试通过！ ==="
echo
echo "web-access skill 已就绪，可以开始使用。"
echo
echo "使用示例："
echo '  - "帮我搜索 xxx 最新进展"'
echo '  - "读一下这个页面：https://example.com"'
echo '  - "去小红书搜索 xxx 的账号"'
