#!/bin/bash
# Token 使用记录增强脚本 - 支持用户维度统计
# 用法：./update-token-usage.sh <userId> <userName> <channel> <chatType> <conversationId> <messageId> <inputTokens> <outputTokens> <model>

set -e

WORKSPACE="/home/admin/.openclaw/workspace"
MEMORY_DIR="$WORKSPACE/memory"
TOKEN_LOG="$MEMORY_DIR/token-usage.jsonl"
USER_PROFILES="$MEMORY_DIR/user-profiles.json"

# 参数
USER_ID="${1:-unknown}"
USER_NAME="${2:-未知用户}"
CHANNEL="${3:-unknown}"
CHAT_TYPE="${4:-unknown}"
CONVERSATION_ID="${5:-unknown}"
MESSAGE_ID="${6:-unknown}"
INPUT_TOKENS="${7:-0}"
OUTPUT_TOKENS="${8:-0}"
MODEL="${9:-qwen3.5-plus}"

# 计算
TOTAL_TOKENS=$((INPUT_TOKENS + OUTPUT_TOKENS))
TIMESTAMP=$(date -Iseconds)

# 计算成本 (qwen3.5-plus: 输入¥0.004/1K, 输出¥0.012/1K)
INPUT_COST=$(echo "scale=6; $INPUT_TOKENS * 0.004 / 1000" | bc)
OUTPUT_COST=$(echo "scale=6; $OUTPUT_TOKENS * 0.012 / 1000" | bc)
ESTIMATED_COST=$(echo "scale=6; $INPUT_COST + $OUTPUT_COST" | bc)

# 记录 token 使用
echo "{\"timestamp\":\"$TIMESTAMP\",\"sessionKey\":\"$CONVERSATION_ID\",\"model\":\"$MODEL\",\"inputTokens\":$INPUT_TOKENS,\"outputTokens\":$OUTPUT_TOKENS,\"totalTokens\":$TOTAL_TOKENS,\"estimatedCost\":$ESTIMATED_COST,\"userId\":\"$USER_ID\",\"userName\":\"$USER_NAME\",\"channel\":\"$CHANNEL\",\"chatType\":\"$CHAT_TYPE\",\"conversationId\":\"$CONVERSATION_ID\",\"messageId\":\"$MESSAGE_ID\"}" >> "$TOKEN_LOG"

echo "✅ Token 记录已添加：$USER_ID ($USER_NAME) - $TOTAL_TOKENS tokens, ¥$ESTIMATED_COST"

# 更新用户档案
if [ -f "$USER_PROFILES" ]; then
    # 检查用户是否存在
    USER_EXISTS=$(jq -r ".users[\"$USER_ID\"] // \"null\"" "$USER_PROFILES")
    
    if [ "$USER_EXISTS" = "null" ]; then
        # 新用户，创建档案
        jq --arg uid "$USER_ID" \
           --arg name "$USER_NAME" \
           --arg ts "$TIMESTAMP" \
           --arg ch "$CHANNEL" \
           --arg ct "$CHAT_TYPE" \
           --arg cid "$CONVERSATION_ID" \
           --argjson tokens "$TOTAL_TOKENS" \
           --argjson cost "$ESTIMATED_COST" \
           '.users[$uid] = {
             "userId": $uid,
             "displayName": $name,
             "firstSeen": $ts,
             "lastSeen": $ts,
             "channel": $ch,
             "chatType": $ct,
             "conversationId": $cid,
             "messageCount": 1,
             "totalTokens": $tokens,
             "totalCost": ($cost | tonumber),
             "tags": []
           } | .lastUpdated = $ts' "$USER_PROFILES" > "${USER_PROFILES}.tmp" && mv "${USER_PROFILES}.tmp" "$USER_PROFILES"
    else
        # 现有用户，更新统计
        jq --arg uid "$USER_ID" \
           --arg ts "$TIMESTAMP" \
           --argjson tokens "$TOTAL_TOKENS" \
           --argjson cost "$ESTIMATED_COST" \
           '.users[$uid].lastSeen = $ts |
            .users[$uid].messageCount += 1 |
            .users[$uid].totalTokens += $tokens |
            .users[$uid].totalCost += ($cost | tonumber) |
            .lastUpdated = $ts' "$USER_PROFILES" > "${USER_PROFILES}.tmp" && mv "${USER_PROFILES}.tmp" "$USER_PROFILES"
    fi
    
    echo "✅ 用户档案已更新：$USER_ID"
fi
