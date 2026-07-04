#!/bin/bash
# 浙江省教育网络安全工作管理平台 - 每日平安上报脚本
# 用法: xxaq-report.sh <验证码>

PHONE="13511329697"
CODE="$1"
BASE_URL="https://xxaq.zjedu.gov.cn"
COOKIE_FILE="/tmp/xxaq_cookie_$$.txt"
LOG_FILE="/tmp/xxaq_report_$(date +%Y%m%d).log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

if [ -z "$CODE" ]; then
    log "ERROR: 请提供验证码"
    exit 1
fi

# 清理旧cookie
rm -f "$COOKIE_FILE"

log "=== 步骤1: 发送短信验证码 ==="
curl -s -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
  "$BASE_URL/api/login/code?phone=$PHONE" \
  -H "Content-Type: application/json" > /dev/null 2>&1

log "=== 步骤2: 使用验证码登录 ==="
LOGIN_RESPONSE=$(curl -s -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
  -X POST "$BASE_URL/api/login/code/$PHONE" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d "{\"code\":\"$CODE\"}" 2>/dev/null)

log "Login response: $LOGIN_RESPONSE"

# 检查登录是否成功
if echo "$LOGIN_RESPONSE" | grep -q "token"; then
    log "=== 登录成功 ==="
    
    # 提取token
    TOKEN=$(echo "$LOGIN_RESPONSE" | grep -oP '"token"\s*:\s*"\K[^"]+' | head -1)
    
    if [ -n "$TOKEN" ]; then
        log "=== 步骤3: 获取值班主题列表 ==="
        REPORTS=$(curl -s -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
          "$BASE_URL/api/safe-report?status=ongoing&pageNum=1&pageSize=10" \
          -H "Token: $TOKEN" \
          -H "Accept: application/json" 2>/dev/null)
        
        log "Reports: $REPORTS"
        
        # 提取第一个进行中的主题ID
        REPORT_ID=$(echo "$REPORTS" | grep -oP '"id"\s*:\s*\K[0-9]+' | head -1)
        THEME=$(echo "$REPORTS" | grep -oP '"theme"\s*:\s*"\K[^"]+' | head -1)
        ROUND=$(echo "$REPORTS" | grep -oP '"round"\s*:\s*\K[0-9]+' | head -1)
        
        log "Found report: id=$REPORT_ID, theme=$THEME, round=$ROUND"
        
        if [ -n "$REPORT_ID" ]; then
            log "=== 步骤4: 上报平安 ==="
            REPORT_RESPONSE=$(curl -s -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
              -X POST "$BASE_URL/api/safe-report/report" \
              -H "Token: $TOKEN" \
              -H "Content-Type: application/json" \
              -H "Accept: application/json" \
              -d "{\"status\":\"safe\",\"safetyReportId\":$REPORT_ID}" 2>/dev/null)
            
            log "Report response: $REPORT_RESPONSE"
            
            if echo "$REPORT_RESPONSE" | grep -q "成功\|success\|200"; then
                log "=== ✅ 上报平安成功！==="
                log "主题: $THEME"
                log "轮次: 第${ROUND}轮"
            else
                log "=== ❌ 上报失败 ==="
                log "响应: $REPORT_RESPONSE"
            fi
        else
            log "=== ⚠️ 未找到进行中的值班主题 ==="
        fi
    else
        log "=== ❌ 登录失败：未获取到token ==="
    fi
else
    log "=== ❌ 登录失败 ==="
    log "响应: $LOGIN_RESPONSE"
fi

# 清理
rm -f "$COOKIE_FILE"
