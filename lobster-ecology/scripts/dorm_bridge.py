#!/usr/bin/env python3
"""
新生选寝小龙虾 - 路由桥接器
通过 HTTP API 调用选寝系统能力
用法: python3 dorm_bridge.py <capability> <args_json>
"""

import json
import sys
import os
import urllib.request
import io
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent / "dormitory_system"
TOKENS_FILE = BASE_DIR / ".api_tokens"
API_BASE = "http://127.0.0.1:8765/api"

def get_token():
    if TOKENS_FILE.exists():
        for line in TOKENS_FILE.read_text().strip().split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                return line
    return ""

def api_get(endpoint):
    url = f"{API_BASE}/{endpoint}"
    headers = {}
    t = get_token()
    if t:
        headers["Authorization"] = f"Bearer {t}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())

def api_post_json(endpoint, data):
    url = f"{API_BASE}/{endpoint}"
    headers = {"Content-Type": "application/json"}
    t = get_token()
    if t:
        headers["Authorization"] = f"Bearer {t}"
    req = urllib.request.Request(url, data=json.dumps(data).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        ct = resp.headers.get("Content-Type", "")
        if "application/json" in ct:
            return json.loads(resp.read().decode())
        return {"_binary": True, "size": len(resp.read())}

def api_post_multipart(endpoint, files, extra_data=None):
    url = f"{API_BASE}/{endpoint}"
    headers = {}
    t = get_token()
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

def main():
    if len(sys.argv) < 2:
        print("用法: python3 dorm_bridge.py <capability> [args_json]")
        print("能力: match_dormitories, get_plan_summary, query_student, query_rooms,")
        print("      move_student, swap_students, move_to_suspended,")
        print("      save_version, restore_version, export_assignment")
        sys.exit(1)

    cap = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}

    try:
        if cap == "match_dormitories":
            result = api_post_multipart("match",
                {"official": args.pop("official_file"), "survey": args.pop("survey_file")},
                {"roomSize": args.get("room_size", 4)})

        elif cap == "get_plan_summary":
            pid = args.get("plan_id", "demo")
            result = api_get("demo") if pid == "demo" else {"error": "需 plan_id，非 demo 方案请先调用 match"}

        elif cap == "query_student":
            pid = args.get("plan_id", "demo")
            kw = args.get("keyword", "")
            plan = api_get("demo") if pid == "demo" else {"error": "无方案"}
            if "error" not in plan:
                results = []
                for room in plan.get("rooms", []):
                    for s in room:
                        if kw.lower() in " ".join(str(s.get(f, "")) for f in ["name","id","origin","undergrad_school"]).lower():
                            results.append({"name": s["name"], "id": s["id"], "location": f"寝室{s.get('_room_id','?')}"})
                result = {"ok": True, "count": len(results), "students": results}
            else:
                result = plan

        elif cap == "query_rooms":
            plan = api_get("demo")
            if "error" not in plan:
                rooms = []
                for room in plan.get("rooms", []):
                    if not room: continue
                    rooms.append({"room_id": room[0].get("_room_id","?"), "count": len(room),
                                  "students": [s["name"] for s in room],
                                  "conflicts": room[0].get("_room_conflicts",[])})
                result = {"ok": True, "rooms": rooms}
            else:
                result = plan

        elif cap in ("move_student", "swap_students", "move_to_suspended", "save_version", "restore_version"):
            ep = cap.replace("_student", "_student").replace("move_to_suspended", "move_to_suspended")
            result = api_post_json(ep, args)

        elif cap == "export_assignment":
            result = api_post_json("export", args)

        else:
            result = {"error": f"未知能力: {cap}"}

        if result.get("_binary"):
            result.pop("content", None)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
