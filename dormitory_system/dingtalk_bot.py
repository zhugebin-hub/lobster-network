#!/usr/bin/env python3
"""
新生选寝系统 - 钉钉对话入口
辅导员直接在钉钉对话中完成排寝操作
"""

import json
import os
import re
import time
import uuid
from pathlib import Path
from datetime import datetime

# 钉钉 webhook 配置（替换为实际的 webhook URL）
DINGTALK_WEBHOOK = os.environ.get("DORM_DINGTALK_WEBHOOK", "")

# 选寝系统 API 配置
DORM_API_BASE = "http://127.0.0.1:8765/api"
DORM_TOKEN_FILE = Path(__file__).parent / ".api_tokens"

def get_dorm_token():
    if DORM_TOKEN_FILE.exists():
        for line in DORM_TOKEN_FILE.read_text().strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    return ""

def send_dingtalk(text, at_all=False):
    """发送钉钉消息"""
    if not DINGTALK_WEBHOOK:
        print(f"[钉钉消息] {text}")
        return
    
    data = {
        "msgtype": "text",
        "text": {"content": text},
        "at": {"isAtAll": at_all}
    }
    try:
        import urllib.request
        req = urllib.request.Request(
            DINGTALK_WEBHOOK,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode()
    except Exception as e:
        print(f"[钉钉发送失败] {e}")

def send_dingtalk_markdown(title, text):
    """发送 Markdown 格式钉钉消息"""
    if not DINGTALK_WEBHOOK:
        print(f"[钉钉 Markdown] {title}\n{text}")
        return
    
    data = {
        "msgtype": "markdown",
        "markdown": {"title": title, "text": text}
    }
    try:
        import urllib.request
        req = urllib.request.Request(
            DINGTALK_WEBHOOK,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read().decode()
    except Exception as e:
        print(f"[钉钉发送失败] {e}")

def dorm_api_get(endpoint):
    """调用选寝系统 GET API"""
    import urllib.request
    url = f"{DORM_API_BASE}/{endpoint}"
    headers = {}
    t = get_dorm_token()
    if t:
        headers["Authorization"] = f"Bearer {t}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def dorm_api_post(endpoint, data):
    """调用选寝系统 POST API"""
    import urllib.request
    url = f"{DORM_API_BASE}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    t = get_dorm_token()
    if t:
        headers["Authorization"] = f"Bearer {t}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        ct = resp.headers.get("Content-Type", "")
        if "application/json" in ct:
            return json.loads(resp.read().decode())
        return {"_binary": True, "size": len(resp.read())}

def dorm_api_post_file(endpoint, files, extra_data=None):
    """调用选寝系统文件上传 API"""
    import urllib.request, io
    url = f"{DORM_API_BASE}/{endpoint}"
    headers = {}
    t = get_dorm_token()
    if t:
        headers["Authorization"] = f"Bearer {t}"
    boundary = "----DormBoundary"
    headers["Content-Type"] = f"multipart/form-data; boundary={boundary}"
    body = io.BytesIO()
    for name, filepath in files.items():
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="{name}"; filename="{os.path.basename(filepath)}"\r\n'.encode())
        body.write(b"Content-Type: application/octet-stream\r\n\r\n")
        with open(filepath, "rb") as f:
            body.write(f.read())
        body.write(b"\r\n")
    for k, v in (extra_data or {}).items():
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="{k}"\r\n\r\n'.encode())
        body.write(f"{v}\r\n".encode())
    body.write(f"--{boundary}--\r\n".encode())
    req = urllib.request.Request(url, data=body.getvalue(), headers=headers)
    with urllib.request.urlopen(req, timeout=60) as resp:
        ct = resp.headers.get("Content-Type", "")
        if "application/json" in ct:
            return json.loads(resp.read().decode())
        return {"_binary": True, "size": len(resp.read())}

# 会话状态存储
SESSIONS = {}

def get_session(user_id):
    if user_id not in SESSIONS:
        SESSIONS[user_id] = {"plan_id": None, "state": "idle"}
    return SESSIONS[user_id]

def handle_message(user_id, text, files=None):
    """处理用户消息"""
    session = get_session(user_id)
    text_lower = text.strip().lower()
    
    # 帮助命令
    if text_lower in ("帮助", "help", "菜单"):
        return """🦞 **新生选寝系统 - 操作指南**

**1. 生成方案**
上传官方名单 + 问卷表，回复"排寝"或"生成方案"

**2. 查看结果**
- "查看方案" - 显示分配摘要
- "查看所有寝室" - 显示全部寝室
- "查看风险寝室" - 只看有冲突的
- "查张三" - 查某学生在哪个寝室

**3. 调整寝室**
- "把张三换到102" - 移动学生
- "张三李四互换" - 互换两个学生
- "把王五移入挂起池" - 临时移出

**4. 版本管理**
- "保存为A方案" - 保存当前方案
- "查看所有版本" - 列出历史版本
- "恢复A方案" - 恢复历史版本

**5. 导出**
- "导出Excel" - 下载最终方案"""

    # 查看方案
    if text_lower in ("查看方案", "方案摘要", "看结果", "结果"):
        if not session["plan_id"]:
            return "还没有生成方案，请先上传名单和问卷表 📂"
        plan_id = session["plan_id"]
        try:
            # 从 plans.json 读取
            plans_file = Path(__file__).parent / "plans.json"
            if not plans_file.exists():
                return "没有可用方案，请重新生成 📂"
            plans = json.loads(plans_file.read_text())
            if plan_id not in plans:
                return "方案已过期，请重新生成 📂"
            plan = plans[plan_id]
            s = plan.get("summary", {})
            msg = f"📊 **方案摘要**\n\n"
            msg += f"总人数：{s.get('total_students', 0)}人\n"
            msg += f"寝室数：{s.get('room_count', 0)}间\n"
            msg += f"挂起人数：{s.get('suspended_count', 0)}人\n"
            msg += f"冲突寝室：{s.get('conflict_count', 0)}间\n"
            msg += f"每寝人数：{s.get('room_size', 4)}人\n"
            msg += f"生成时间：{s.get('generated_at', '')}"
            
            warnings = plan.get("warnings", [])
            if warnings:
                msg += "\n\n⚠️ **警告：**\n" + "\n".join(warnings)
            
            advice = plan.get("advice", [])
            if advice:
                msg += "\n\n💡 **建议：**\n" + "\n".join(advice)
            
            return msg
        except Exception as e:
            return f"查看方案失败：{e}"

    # 查看所有寝室
    if text_lower in ("查看所有寝室", "全部寝室", "寝室列表"):
        return _render_rooms_list("all")

    # 查看风险寝室
    if text_lower in ("查看风险寝室", "风险寝室", "只看风险"):
        return _render_rooms_list("risk")

    # 查学生
    match = re.match(r"^查(.+)$", text_lower)
    if match:
        keyword = match.group(1)
        return _search_student(keyword)

    # 移动学生
    match = re.match(r"^把(.+?)换到(\d+)$", text)
    if match:
        student = match.group(1)
        room = match.group(2)
        return _move_student(student, room)

    # 互换学生
    match = re.match(r"^(.+?)[和与](.+?)互换$", text)
    if match:
        a, b = match.group(1), match.group(2)
        return _swap_students(a, b)

    # 移入挂起池
    match = re.match(r"^把(.+?)移入挂起池$", text)
    if match:
        return _move_to_suspended(match.group(1))

    # 保存版本
    match = re.match(r"^保存为(.+)$", text)
    if match:
        return _save_version(match.group(1))

    # 查看版本
    if text_lower in ("查看所有版本", "版本列表", "历史版本"):
        return _list_versions()

    # 恢复版本
    match = re.match(r"^恢复(.+)$", text)
    if match:
        return _restore_version(match.group(1))

    # 导出
    if text_lower in ("导出excel", "导出", "下载方案", "导出方案"):
        return _export_excel()

    # 排寝/生成方案
    if text_lower in ("排寝", "生成方案", "开始匹配", "智能匹配", "分宿舍"):
        if files and len(files) >= 2:
            return _do_match(files)
        else:
            return "请上传两个文件：官方新生名单 + 问卷星意向表 📂\n\n您可以直接在钉钉中发送文件给我。"

    return f"🦞 收到：{text}\n\n发送「帮助」查看可用操作"

def _render_rooms_list(filter_type):
    """渲染寝室列表"""
    session = get_session(None)  # 简化处理
    plans_file = Path(__file__).parent / "plans.json"
    if not plans_file.exists():
        return "没有可用方案"
    
    plans = json.loads(plans_file.read_text())
    # 取最新的 plan
    if not plans:
        return "没有可用方案"
    
    # 取最后一个 plan
    plan_id = list(plans.keys())[-1]
    plan = plans[plan_id]
    
    rooms = plan.get("rooms", [])
    if filter_type == "risk":
        rooms = [r for r in rooms if r and r[0].get("_room_conflicts")]
    
    msg = f"🏠 **寝室列表**（共{len(rooms)}间）\n\n"
    for room in rooms:
        if not room:
            continue
        room_id = room[0].get("_room_id", "?")
        names = " | ".join(s["name"] for s in room)
        conflicts = room[0].get("_room_conflicts", [])
        bonds = room[0].get("_room_bonds", [])
        
        msg += f"**{room_id}**：{names}\n"
        if conflicts:
            msg += f"  ⚠️ {' | '.join(conflicts)}\n"
        if bonds:
            msg += f"  🔗 {bonds[0]}"
            if len(bonds) > 1:
                msg += f" (+{len(bonds)-1})"
        msg += "\n\n"
    
    return msg.strip()

def _search_student(keyword):
    """搜索学生"""
    plans_file = Path(__file__).parent / "plans.json"
    if not plans_file.exists():
        return "没有可用方案"
    
    plans = json.loads(plans_file.read_text())
    if not plans:
        return "没有可用方案"
    
    plan = list(plans.values())[-1]
    kw = keyword.lower()
    
    for room in plan.get("rooms", []):
        for s in room:
            fields = [s.get("name", ""), s.get("id", ""), s.get("origin", ""), s.get("undergrad_school", "")]
            if kw in " ".join(str(f) for f in fields).lower():
                conflicts = s.get("_room_conflicts", [])
                bonds = s.get("_room_bonds", [])
                msg = f"🔍 **{s['name']}**\n\n"
                msg += f"学号：{s.get('id', '')}\n"
                msg += f"性别：{s.get('gender', '')}\n"
                msg += f"生源地：{s.get('origin', '')}\n"
                msg += f"本科院校：{s.get('undergrad_school', '')}\n"
                msg += f"所在寝室：{s.get('_room_id', '')}\n"
                if conflicts:
                    msg += f"\n⚠️ 冲突：{' | '.join(conflicts)}"
                if bonds:
                    msg += f"\n🔗 纽带：{bonds[0]}"
                return msg
    
    return f"未找到与「{keyword}」匹配的学生"

def _move_student(student, room_id):
    return f"📝 已将 {student} 移动到寝室 {room_id}\n\n（实际操作需通过 API 调用）"

def _swap_students(a, b):
    return f"📝 已将 {a} 和 {b} 互换\n\n（实际操作需通过 API 调用）"

def _move_to_suspended(student):
    return f"📝 已将 {student} 移入挂起池\n\n（实际操作需通过 API 调用）"

def _save_version(name):
    return f"💾 方案「{name}」已保存\n\n（实际操作需通过 API 调用）"

def _list_versions():
    return "📋 暂无已保存版本"

def _restore_version(name):
    return f"📋 已恢复版本「{name}」\n\n（实际操作需通过 API 调用）"

def _export_excel():
    return "📥 Excel 导出功能\n\n（实际操作需通过 API 调用，导出文件将通过钉钉发送）"

def _do_match(files):
    return f"🦞 收到 {len(files)} 个文件，正在生成方案...\n\n（实际操作需上传文件到 API）"

if __name__ == "__main__":
    print("🦞 新生选寝系统 - 钉钉对话入口")
    print("用法：将此脚本集成到钉钉机器人 webhook")
    print(f"选寝 API: {DORM_API_BASE}")
    print(f"Token: {'已配置' if get_dorm_token() else '未配置'}")
