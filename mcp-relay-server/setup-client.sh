#!/bin/bash
# 🦞 MCP 双向通道 - 客户端配置脚本
# 使用方法：在对方的服务器上执行此脚本
# bash setup-client.sh xiaochen 小陈

set -e

# === 颜色输出 ===
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }

# === 配置 ===
MCP_SERVER_URL="http://121.43.80.231:8721/sse/"
MCP_TOKEN="Hbmnldh4z6Nae-rIzJ-5EgT8etEin8mWLVF0zZ6v648"
MCP_HEALTH_URL="http://121.43.80.231:8721/health"

# === 参数 ===
AGENT_ID="${1:-}"
AGENT_NAME="${2:-}"

if [ -z "$AGENT_ID" ] || [ -z "$AGENT_NAME" ]; then
    echo -e "${BLUE}🦞 MCP 双向通道 - 客户端配置${NC}"
    echo ""
    echo "用法: bash setup-client.sh <agent_id> <agent_name>"
    echo ""
    echo "示例:"
    echo "  bash setup-client.sh xiaochen 小陈"
    echo "  bash setup-client.sh xiaozhu 小朱"
    echo ""
    echo "参数说明:"
    echo "  agent_id   - 你的唯一标识符（英文，如 xiaochen）"
    echo "  agent_name - 你的显示名称（中文，如 小陈）"
    exit 1
fi

echo -e "${BLUE}🦞 MCP 双向通道 - 客户端配置${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Agent ID:   $AGENT_ID"
echo "Agent Name: $AGENT_NAME"
echo "Server:     $MCP_SERVER_URL"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# === Step 1: 检查网络连接 ===
echo -e "${BLUE}📡 Step 1: 检查网络连接...${NC}"

if curl -s --connect-timeout 5 "$MCP_HEALTH_URL" > /dev/null 2>&1; then
    info "服务器连接正常"
else
    warn "无法连接到 MCP 服务器 ($MCP_SERVER_URL)"
    echo ""
    echo "可能的原因:"
    echo "  1. 阿里云安全组未放行 8721 端口（联系虾尔处理）"
    echo "  2. 网络防火墙阻止了出站连接"
    echo "  3. 服务器尚未启动"
    echo ""
    echo "是否继续配置？(y/n)"
    read -r continue_config
    if [ "$continue_config" != "y" ]; then
        error "配置已取消"
    fi
fi

# === Step 2: 验证 Token ===
echo ""
echo -e "${BLUE}🔑 Step 2: 验证 Token...${NC}"

AUTH_RESULT=$(curl -s --connect-timeout 5 "http://121.43.80.231:8721/auth?token=$MCP_TOKEN" 2>/dev/null)
if echo "$AUTH_RESULT" | grep -q '"authenticated":true'; then
    info "Token 验证通过"
else
    error "Token 验证失败，请检查 MCP_TOKEN 是否正确"
fi

# === Step 3: 注册 Agent ===
echo ""
echo -e "${BLUE}📝 Step 3: 注册 Agent...${NC}"

REGISTER_RESULT=$(curl -s --connect-timeout 5 \
    -H "Content-Type: application/json" \
    -d "{\"agent_id\":\"$AGENT_ID\",\"name\":\"$AGENT_NAME\"}" \
    "http://121.43.80.231:8721/register" 2>/dev/null)

if echo "$REGISTER_RESULT" | grep -q "registered\|注册成功"; then
    info "Agent 注册成功: $AGENT_NAME ($AGENT_ID)"
else
    warn "注册接口返回: $REGISTER_RESULT"
    echo "  (如果服务器使用 MCP 协议，注册将通过 MCP Client 完成)"
fi

# === Step 4: 生成配置文件 ===
echo ""
echo -e "${BLUE}⚙️  Step 4: 生成配置文件...${NC}"

CONFIG_DIR="$HOME/.mcp-relay"
mkdir -p "$CONFIG_DIR"

cat > "$CONFIG_DIR/config.json" << EOF
{
    "server_url": "$MCP_SERVER_URL",
    "token": "$MCP_TOKEN",
    "agent_id": "$AGENT_ID",
    "agent_name": "$AGENT_NAME",
    "health_url": "$MCP_HEALTH_URL",
    "auth_url": "http://121.43.80.231:8721/auth"
}
EOF

info "配置文件已生成: $CONFIG_DIR/config.json"

# === Step 5: 生成 MCP Client 配置 ===
echo ""
echo -e "${BLUE}🔌 Step 5: 生成 MCP Client 配置...${NC}"

# 为不同平台生成配置
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 MCP Client 连接配置（复制以下配置到你的 AI 客户端）"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

echo "【方案 A: SSE 直连】"
echo ""
echo "URL: $MCP_SERVER_URL?agent_id=$AGENT_ID&name=$AGENT_NAME"
echo "Header: x-agent-id: $AGENT_ID"
echo "Token: $MCP_TOKEN"
echo ""

echo "【方案 B: QoderWork / Cursor 配置】"
echo ""
echo "在 mcp_servers.json 中添加:"
echo ""
cat << 'QODER'
{
    "mcpServers": {
        "xiaolongxia-relay": {
            "url": "http://121.43.80.231:8721/sse/",
            "headers": {
                "x-agent-id": "YOUR_AGENT_ID",
                "Authorization": "Bearer YOUR_TOKEN"
            },
            "query": {
                "agent_id": "YOUR_AGENT_ID",
                "name": "YOUR_NAME"
            }
        }
    }
}
QODER
echo ""

echo "【方案 C: Claude Desktop 配置】"
echo ""
cat << 'CLAUDE'
在 claude_desktop_config.json 中:
{
    "mcpServers": {
        "xiaolongxia-relay": {
            "command": "npx",
            "args": ["mcp-client", "sse", "http://121.43.80.231:8721/sse/?agent_id=YOUR_ID&name=YOUR_NAME"],
            "env": {
                "MCP_AUTH_TOKEN": "YOUR_TOKEN"
            }
        }
    }
}
CLAUDE
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🛠️  测试命令"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 生成测试脚本
cat > "$CONFIG_DIR/test.sh" << TESTEOF
#!/bin/bash
# MCP 双向通道 - 连接测试脚本

TOKEN="$MCP_TOKEN"
AGENT_ID="$AGENT_ID"
AGENT_NAME="$AGENT_NAME"
SERVER="http://121.43.80.231:8721"

echo "🦞 MCP 双向通道 - 连接测试"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. 健康检查
echo ""
echo "1️⃣ 健康检查..."
HEALTH=\$(curl -s --connect-timeout 5 "\$SERVER/health")
if [ "\$HEALTH" = "ok" ]; then
    echo "✅ 服务器正常"
else
    echo "❌ 服务器连接失败"
    exit 1
fi

# 2. Token 验证
echo ""
echo "2️⃣ Token 验证..."
AUTH=\$(curl -s --connect-timeout 5 "\$SERVER/auth?token=\$TOKEN")
if echo "\$AUTH" | grep -q "true"; then
    echo "✅ Token 有效"
else
    echo "❌ Token 无效"
    exit 1
fi

# 3. 列出 Agent
echo ""
echo "3️⃣ 已注册的 Agent..."
curl -s --connect-timeout 5 "\$SERVER/list-agents" | python3 -m json.tool 2>/dev/null || echo "(使用 MCP Client 查看)"

# 4. 发送测试消息
echo ""
echo "4️⃣ 发送测试消息给 xiasher..."
curl -s --connect-timeout 5 \
    -H "x-agent-id: \$AGENT_ID" \
    -H "Content-Type: application/json" \
    -d "{\"to\":\"xiasher\",\"content\":\"🦞 你好！我是 \$AGENT_NAME (\$AGENT_ID)，MCP 双向通道测试消息。\"}" \
    "\$SERVER/send-message" | python3 -m json.tool 2>/dev/null

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 测试完成！"
echo ""
echo "查看收到的消息:"
echo "  curl -s -H \"x-agent-id: \$AGENT_ID\" http://121.43.80.231:8721/get-messages"
TESTEOF

chmod +x "$CONFIG_DIR/test.sh"
info "测试脚本已生成: $CONFIG_DIR/test.sh"

# === Step 6: 生成消息收发脚本 ===
echo ""
echo -e "${BLUE}📬 Step 6: 生成消息收发脚本...${NC}"

cat > "$CONFIG_DIR/send.sh" << 'SENDEOF'
#!/bin/bash
# MCP 双向通道 - 发送消息
# 用法: bash send.sh <to_agent> <message>

CONFIG_DIR="$HOME/.mcp-relay"
source "$CONFIG_DIR/config.json" 2>/dev/null || true

# 读取配置
AGENT_ID=$(python3 -c "import json; print(json.load(open('$CONFIG_DIR/config.json'))['agent_id'])" 2>/dev/null)
TOKEN=$(python3 -c "import json; print(json.load(open('$CONFIG_DIR/config.json'))['token'])" 2>/dev/null)
SERVER="http://121.43.80.231:8721"

TO_AGENT="${1:-}"
MESSAGE="${2:-}"

if [ -z "$TO_AGENT" ] || [ -z "$MESSAGE" ]; then
    echo "用法: bash send.sh <目标Agent> <消息内容>"
    echo "示例: bash send.sh xiasher 你好！"
    exit 1
fi

echo "📤 发送消息给 $TO_AGENT..."
curl -s --connect-timeout 5 \
    -H "x-agent-id: $AGENT_ID" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "{\"to\":\"$TO_AGENT\",\"content\":\"$MESSAGE\"}" \
    "$SERVER/send-message" | python3 -m json.tool 2>/dev/null
SENDEOF

chmod +x "$CONFIG_DIR/send.sh"

cat > "$CONFIG_DIR/receive.sh" << 'RECEIVEEOF'
#!/bin/bash
# MCP 双向通道 - 接收消息
# 用法: bash receive.sh [mark_read]

CONFIG_DIR="$HOME/.mcp-relay"
AGENT_ID=$(python3 -c "import json; print(json.load(open('$CONFIG_DIR/config.json'))['agent_id'])" 2>/dev/null)
SERVER="http://121.43.80.231:8721"
MARK_READ="${1:-true}"

echo "📥 获取消息..."
curl -s --connect-timeout 5 \
    -H "x-agent-id: $AGENT_ID" \
    "$SERVER/get-messages?mark_read=$MARK_READ" | python3 -m json.tool 2>/dev/null
RECEIVEEOF

chmod +x "$CONFIG_DIR/receive.sh"

info "消息脚本已生成:"
echo "   发送: bash $CONFIG_DIR/send.sh <目标> <消息>"
echo "   接收: bash $CONFIG_DIR/receive.sh"

# === 完成 ===
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🦞 MCP 双向通道配置完成！${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📁 配置文件: $CONFIG_DIR/"
echo "   config.json  - 连接配置"
echo "   test.sh      - 连接测试"
echo "   send.sh      - 发送消息"
echo "   receive.sh   - 接收消息"
echo ""
echo "🚀 快速开始:"
echo "   bash $CONFIG_DIR/test.sh          # 测试连接"
echo "   bash $CONFIG_DIR/send.sh xiasher '你好！'  # 发消息给虾尔"
echo "   bash $CONFIG_DIR/receive.sh       # 收消息"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
