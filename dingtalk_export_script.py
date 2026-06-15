#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉聊天记录导出脚本
使用钉钉官方 API 导出企业会话记录
"""

import requests
import json
import time
from datetime import datetime

# 钉钉应用凭证
APP_KEY = "dingfejaknepsm96bud"
APP_SECRET = "t3cTDKp31RS9DMsSnK7YO8YbsuAuqCiWD5d6xCzcL9gGwHuxjD0PTykIgK2ETPpM"

# 输出目录
OUTPUT_DIR = "/home/admin/.openclaw/workspace/dingtalk_export"

def get_access_token():
    """获取 access token"""
    url = "https://oapi.dingtalk.com/gettoken"
    params = {
        "appkey": APP_KEY,
        "appsecret": APP_SECRET
    }
    
    response = requests.get(url, params=params)
    data = response.json()
    
    if data.get("errcode") == 0:
        return data["access_token"]
    else:
        print(f"获取 token 失败：{data}")
        return None

def get_chat_list(access_token, limit=100):
    """获取会话列表"""
    url = "https://oapi.dingtalk.com/topapi/chat/list"
    
    params = {
        "access_token": access_token
    }
    
    data = {
        "limit": limit,
        "cursor": 0
    }
    
    response = requests.post(url, params=params, json=data)
    result = response.json()
    
    if result.get("errcode") == 0:
        return result["result"]
    else:
        print(f"获取会话列表失败：{result}")
        return None

def get_chat_messages(access_token, chat_id):
    """获取会话消息"""
    url = "https://oapi.dingtalk.com/topapi/chat/get"
    
    params = {
        "access_token": access_token
    }
    
    data = {
        "chatid": chat_id
    }
    
    response = requests.post(url, params=params, json=data)
    result = response.json()
    
    if result.get("errcode") == 0:
        return result["result"]
    else:
        print(f"获取消息失败 (chat_id={chat_id}): {result}")
        return None

def export_to_json(messages, filename):
    """导出为 JSON 文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)
    print(f"已导出：{filename}")

def export_to_text(messages, filename):
    """导出为文本文件"""
    with open(filename, 'w', encoding='utf-8') as f:
        for msg in messages.get("messages", []):
            sender = msg.get("senderNick", "未知")
            text = msg.get("text", {}).get("content", "")
            timestamp = msg.get("createAt", 0)
            dt = datetime.fromtimestamp(timestamp / 1000) if timestamp else "未知时间"
            f.write(f"[{dt}] {sender}: {text}\n")
    print(f"已导出：{filename}")

def main():
    print("=" * 50)
    print("钉钉聊天记录导出工具")
    print("=" * 50)
    
    # 检查凭证
    if APP_SECRET == "你的新 AppSecret":
        print("\n⚠️ 错误：请先在脚本中设置正确的 AppSecret！")
        print("提示：你在钉钉开发者平台看到的 Client Secret")
        return
    
    # 获取 access token
    print("\n[1/4] 获取 access token...")
    access_token = get_access_token()
    if not access_token:
        print("❌ 获取 token 失败，请检查 AppKey 和 AppSecret")
        return
    print(f"✅ Token 获取成功")
    
    # 获取会话列表
    print("\n[2/4] 获取会话列表...")
    chat_list = get_chat_list(access_token)
    if not chat_list:
        print("❌ 获取会话列表失败")
        print("可能原因：应用没有聊天会话权限")
        print("请在钉钉开发者后台添加「内部群」或「会话」权限")
        return
    
    chats = chat_list.get("chat_list", [])
    print(f"✅ 找到 {len(chats)} 个会话")
    
    # 创建输出目录
    import os
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 导出每个会话
    print("\n[3/4] 导出会话消息...")
    exported_count = 0
    for i, chat in enumerate(chats):
        chat_id = chat.get("chatid")
        chat_title = chat.get("title", "未命名会话")
        print(f"  处理 {i+1}/{len(chats)}: {chat_title}")
        
        messages = get_chat_messages(access_token, chat_id)
        if messages:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join([c for c in chat_title if c.isalnum() or c in "-_"]).strip()[:50]
            
            # 导出 JSON
            json_file = f"{OUTPUT_DIR}/{timestamp}_{safe_title}.json"
            export_to_json(messages, json_file)
            
            # 导出文本
            txt_file = f"{OUTPUT_DIR}/{timestamp}_{safe_title}.txt"
            export_to_text(messages, txt_file)
            
            exported_count += 1
    
    # 打包
    print("\n[4/4] 打包导出文件...")
    import subprocess
    zip_file = f"{OUTPUT_DIR}_export.zip"
    subprocess.run(["zip", "-r", zip_file, OUTPUT_DIR])
    
    print("\n" + "=" * 50)
    print(f"✅ 导出完成！")
    print(f"   导出会话数：{exported_count}/{len(chats)}")
    print(f"   输出目录：{OUTPUT_DIR}")
    print(f"   压缩包：{zip_file}")
    print("=" * 50)

if __name__ == "__main__":
    main()
