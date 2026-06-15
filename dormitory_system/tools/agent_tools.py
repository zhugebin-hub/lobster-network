#!/usr/bin/env python3
"""
新生选寝系统 - 业务小龙虾工具层
将系统能力封装为智能体可调用的工具
"""

import json
import sys
import os
from pathlib import Path

# 添加父目录到路径（tools/ -> dormitory_system/ -> workspace/）
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from dormitory_system.server import (
    try_read_file, parse_students, find_header_row,
    merge_students, normalize_student, match_dormitories,
    export_to_excel, save_version, list_versions, restore_version,
    current_plans, check_hard_conflict, check_avoid_conflict,
    calc_bond_score, calc_preference_score,
)

def tool_match_dormitories(official_path, survey_path, room_size=4):
    """
    工具1：读取两份文件并生成宿舍分配方案
    输入：official_file, survey_file, room_size
    输出：plan_id + 方案摘要
    """
    try:
        official_path = Path(official_path)
        survey_path = Path(survey_path)
        
        if not official_path.exists():
            return {"error": f"官方名单文件不存在: {official_path}"}
        if not survey_path.exists():
            return {"error": f"问卷表文件不存在: {survey_path}"}
        
        with open(official_path, "rb") as f:
            official_data = f.read()
        with open(survey_path, "rb") as f:
            survey_data = f.read()
        
        official_rows = try_read_file(official_data, official_path.name)
        survey_rows = try_read_file(survey_data, survey_path.name)
        
        official_students, _ = parse_students(official_rows, find_header_row(official_rows))
        survey_students, _ = parse_students(survey_rows, find_header_row(survey_rows))
        
        merged, merge_warnings = merge_students(official_students, survey_students)
        normalized = [normalize_student(s) for s in merged]
        
        result = match_dormitories(normalized, room_size)
        result["room_size"] = room_size
        result["warnings"].extend(merge_warnings)
        
        # 生成 plan_id
        import uuid
        plan_id = str(uuid.uuid4())[:8]
        
        # 存储到内存（实际应该持久化）
        plans_file = Path(__file__).parent.parent / "plans.json"
        plans = {}
        if plans_file.exists():
            plans = json.loads(plans_file.read_text())
        
        # 转换房间数据为可序列化
        serializable_result = _make_serializable(result)
        plans[plan_id] = serializable_result
        plans_file.write_text(json.dumps(plans, ensure_ascii=False, indent=2))
        
        result["plan_id"] = plan_id
        
        return {
            "ok": True,
            "plan_id": plan_id,
            "summary": result["summary"],
            "warnings": result["warnings"],
            "advice": result["advice"],
        }
        
    except Exception as e:
        return {"error": f"匹配失败: {str(e)}"}

def tool_get_plan_summary(plan_id):
    """
    工具2：获取方案摘要
    """
    plans_file = Path(__file__).parent.parent / "plans.json"
    if not plans_file.exists():
        return {"error": "没有任何方案"}
    
    plans = json.loads(plans_file.read_text())
    if plan_id not in plans:
        return {"error": f"方案不存在: {plan_id}"}
    
    plan = plans[plan_id]
    summary = plan.get("summary", {})
    
    return {
        "ok": True,
        "plan_id": plan_id,
        "总人数": summary.get("total_students", 0),
        "寝室数": summary.get("room_count", 0),
        "挂起人数": summary.get("suspended_count", 0),
        "冲突寝室数": summary.get("conflict_count", 0),
        "每寝人数": summary.get("room_size", 4),
        "生成时间": summary.get("generated_at", ""),
        "warnings": plan.get("warnings", []),
        "advice": plan.get("advice", []),
    }

def tool_query_student(plan_id, keyword):
    """
    工具3：查找学生
    输入：plan_id, keyword（姓名/学号/城市/学校）
    输出：匹配学生画像与当前位置
    """
    plans_file = Path(__file__).parent.parent / "plans.json"
    if not plans_file.exists():
        return {"error": "没有任何方案"}
    
    plans = json.loads(plans_file.read_text())
    if plan_id not in plans:
        return {"error": f"方案不存在: {plan_id}"}
    
    plan = plans[plan_id]
    results = []
    
    # 在所有房间中查找
    for room in plan.get("rooms", []):
        for s in room:
            if _student_matches(s, keyword):
                results.append({
                    **s,
                    "_location": f"寝室 {s.get('_room_id', '?')}",
                    "_room_conflicts": s.get("_room_conflicts", []),
                    "_room_bonds": s.get("_room_bonds", []),
                })
    
    # 在挂起池中查找
    for s in plan.get("suspended", []):
        if _student_matches(s, keyword):
            results.append({
                **s,
                "_location": "混寝挂起池",
            })
    
    return {
        "ok": True,
        "count": len(results),
        "students": results,
    }

def tool_query_rooms(plan_id, gender=None, risk_only=False, keyword=None):
    """
    工具4：查询房间
    输入：plan_id, 性别过滤, 只看风险, 关键词
    输出：房间列表及风险/纽带
    """
    plans_file = Path(__file__).parent.parent / "plans.json"
    if not plans_file.exists():
        return {"error": "没有任何方案"}
    
    plans = json.loads(plans_file.read_text())
    if plan_id not in plans:
        return {"error": f"方案不存在: {plan_id}"}
    
    plan = plans[plan_id]
    rooms_info = []
    
    for room in plan.get("rooms", []):
        if not room:
            continue
        
        room_id = room[0].get("_room_id", "?")
        
        # 性别过滤
        if gender:
            room_genders = set(s.get("gender") for s in room)
            if gender not in room_genders:
                continue
        
        # 风险过滤
        if risk_only:
            room_conflicts = room[0].get("_room_conflicts", []) if room else []
            if not room_conflicts:
                continue
        
        # 关键词搜索
        if keyword:
            room_text = " ".join(s.get("name", "") + " " + s.get("origin", "") + " " + s.get("undergrad_school", "") for s in room)
            if keyword.lower() not in room_text.lower():
                continue
        
        room_conflicts = room[0].get("_room_conflicts", []) if room else []
        room_bonds = room[0].get("_room_bonds", []) if room else []
        room_score = room[0].get("_room_score", 0) if room else 0
        
        rooms_info.append({
            "room_id": room_id,
            "人数": len(room),
            "分数": room_score,
            "学生": [{"name": s.get("name"), "id": s.get("id"), "gender": s.get("gender")} for s in room],
            "conflicts": room_conflicts,
            "bonds": room_bonds,
        })
    
    # 挂起池
    suspended_info = []
    for s in plan.get("suspended", []):
        suspended_info.append({
            "name": s.get("name"),
            "id": s.get("id"),
            "gender": s.get("gender"),
        })
    
    return {
        "ok": True,
        "rooms": rooms_info,
        "suspended_count": len(suspended_info),
        "suspended": suspended_info,
    }

def tool_move_student(plan_id, student_key, target_room_id):
    """
    工具5：移动学生到指定寝室
    """
    plans_file = Path(__file__).parent.parent / "plans.json"
    if not plans_file.exists():
        return {"error": "没有任何方案"}
    
    plans = json.loads(plans_file.read_text())
    if plan_id not in plans:
        return {"error": f"方案不存在: {plan_id}"}
    
    plan = plans[plan_id]
    student, source_room = _find_student_in_plan(plan, student_key)
    
    if not student:
        return {"error": f"未找到学生: {student_key}"}
    
    # 从原位置移除
    if source_room is not None:
        source_room.remove(student)
    else:
        plan["suspended"] = [s for s in plan["suspended"] if s.get("id") != student.get("id") and s.get("name") != student.get("name")]
    
    # 找到目标房间
    target_room = None
    for room in plan["rooms"]:
        if room and room[0].get("_room_id") == target_room_id:
            target_room = room
            break
    
    if target_room:
        target_room.append(student)
        student["_room_id"] = target_room_id
        msg = f"已将 {student.get('name')} 移动到寝室 {target_room_id}"
    else:
        plan["suspended"].append(student)
        student.pop("_room_id", None)
        msg = f"已将 {student.get('name')} 移入挂起池"
    
    # 保存
    plans[plan_id] = plan
    plans_file.write_text(json.dumps(plans, ensure_ascii=False, indent=2))
    
    return {"ok": True, "message": msg}

def tool_swap_students(plan_id, student_a_key, student_b_key):
    """
    工具6：互换两个学生
    """
    plans_file = Path(__file__).parent.parent / "plans.json"
    if not plans_file.exists():
        return {"error": "没有任何方案"}
    
    plans = json.loads(plans_file.read_text())
    if plan_id not in plans:
        return {"error": f"方案不存在: {plan_id}"}
    
    plan = plans[plan_id]
    sa, ra = _find_student_in_plan(plan, student_a_key)
    sb, rb = _find_student_in_plan(plan, student_b_key)
    
    if not sa or not sb:
        return {"error": "未找到一个或两个学生"}
    
    # 移除
    if ra is not None:
        ra.remove(sa)
    else:
        plan["suspended"] = [s for s in plan["suspended"] if s.get("id") != sa.get("id")]
    
    if rb is not None:
        rb.remove(sb)
    else:
        plan["suspended"] = [s for s in plan["suspended"] if s.get("id") != sb.get("id")]
    
    # 交换
    if rb is not None:
        rb.append(sa)
        sa["_room_id"] = rb[0].get("_room_id", "?")
    else:
        plan["suspended"].append(sa)
        sa.pop("_room_id", None)
    
    if ra is not None:
        ra.append(sb)
        sb["_room_id"] = ra[0].get("_room_id", "?")
    else:
        plan["suspended"].append(sb)
        sb.pop("_room_id", None)
    
    plans[plan_id] = plan
    plans_file.write_text(json.dumps(plans, ensure_ascii=False, indent=2))
    
    return {"ok": True, "message": f"已互换 {sa.get('name')} 和 {sb.get('name')}"}

def tool_move_to_suspended(plan_id, student_key):
    """
    工具7：将学生移入挂起池
    """
    plans_file = Path(__file__).parent.parent / "plans.json"
    if not plans_file.exists():
        return {"error": "没有任何方案"}
    
    plans = json.loads(plans_file.read_text())
    if plan_id not in plans:
        return {"error": f"方案不存在: {plan_id}"}
    
    plan = plans[plan_id]
    student, source_room = _find_student_in_plan(plan, student_key)
    
    if not student:
        return {"error": f"未找到学生: {student_key}"}
    
    if source_room is not None:
        source_room.remove(student)
    
    plan["suspended"].append(student)
    student.pop("_room_id", None)
    
    plans[plan_id] = plan
    plans_file.write_text(json.dumps(plans, ensure_ascii=False, indent=2))
    
    return {"ok": True, "message": f"已将 {student.get('name')} 移入挂起池"}

def tool_save_version(plan_id, version_name):
    """
    工具8：保存版本
    """
    plans_file = Path(__file__).parent.parent / "plans.json"
    if not plans_file.exists():
        return {"error": "没有任何方案"}
    
    plans = json.loads(plans_file.read_text())
    if plan_id not in plans:
        return {"error": f"方案不存在: {plan_id}"}
    
    plan_data = plans[plan_id]
    import uuid
    version_id = str(uuid.uuid4())[:8]
    
    versions_file = Path(__file__).parent.parent / "versions.json"
    versions = {}
    if versions_file.exists():
        versions = json.loads(versions_file.read_text())
    
    from datetime import datetime
    versions[version_id] = {
        "version_id": version_id,
        "plan_id": plan_id,
        "version_name": version_name,
        "created_at": datetime.now().isoformat(),
        "data": plan_data,
    }
    
    versions_file.write_text(json.dumps(versions, ensure_ascii=False, indent=2))
    
    return {"ok": True, "version_id": version_id, "version_name": version_name}

def tool_restore_version(version_id):
    """
    工具9：恢复版本
    """
    versions_file = Path(__file__).parent.parent / "versions.json"
    if not versions_file.exists():
        return {"error": "没有任何已保存版本"}
    
    versions = json.loads(versions_file.read_text())
    if version_id not in versions:
        return {"error": f"版本不存在: {version_id}"}
    
    version = versions[version_id]
    plan_id = version["plan_id"]
    plan_data = version["data"]
    
    # 恢复到当前方案
    plans_file = Path(__file__).parent.parent / "plans.json"
    plans = {}
    if plans_file.exists():
        plans = json.loads(plans_file.read_text())
    
    plans[plan_id] = plan_data
    plans_file.write_text(json.dumps(plans, ensure_ascii=False, indent=2))
    
    return {"ok": True, "plan_id": plan_id, "version_name": version["version_name"]}

def tool_export_assignment(plan_id, output_path=None):
    """
    工具10：导出 Excel
    """
    plans_file = Path(__file__).parent.parent / "plans.json"
    if not plans_file.exists():
        return {"error": "没有任何方案"}
    
    plans = json.loads(plans_file.read_text())
    if plan_id not in plans:
        return {"error": f"方案不存在: {plan_id}"}
    
    plan = plans[plan_id]
    
    # 恢复 _restore_rooms 需要的结构
    plan_data = _make_exportable(plan)
    
    try:
        output = export_to_excel(plan_data)
        return {"ok": True, "output_path": str(output)}
    except Exception as e:
        return {"error": f"导出失败: {str(e)}"}

# ==================== 内部辅助函数 ====================

def _find_student_in_plan(plan, student_key):
    """在方案中查找学生"""
    for room in plan.get("rooms", []):
        for s in room:
            if s.get("id") == student_key or s.get("name") == student_key:
                return s, room
    for s in plan.get("suspended", []):
        if s.get("id") == student_key or s.get("name") == student_key:
            return s, None
    return None, None

def _student_matches(student, keyword):
    """检查学生是否匹配关键词"""
    kw = keyword.lower()
    fields = [
        student.get("name", ""),
        student.get("id", ""),
        student.get("origin", ""),
        student.get("origin_city", ""),
        student.get("undergrad_school", ""),
        student.get("undergrad_city", ""),
        student.get("gender", ""),
        student.get("schedule", ""),
        student.get("game_freq", ""),
    ]
    return any(kw in str(f).lower() for f in fields)

def _make_serializable(obj):
    """将方案数据转为可 JSON 序列化的格式"""
    if isinstance(obj, dict):
        return {k: _make_serializable(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_make_serializable(item) for item in obj]
    elif isinstance(obj, set):
        return list(obj)
    elif isinstance(obj, Path):
        return str(obj)
    return obj

def _make_exportable(plan):
    """将方案数据转为可导出的格式"""
    return {
        "students": [s for room in plan.get("rooms", []) for s in room] + plan.get("suspended", []),
        "rooms": plan.get("rooms", []),
        "suspended": plan.get("suspended", []),
        "room_size": plan.get("room_size", 4),
    }

# ==================== CLI 接口 ====================
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法：python agent_tools.py <tool_name> [args...]")
        print("可用工具：")
        print("  match <official.xlsx> <survey.xlsx> [room_size]")
        print("  summary <plan_id>")
        print("  query_student <plan_id> <keyword>")
        print("  query_rooms <plan_id> [gender] [risk_only] [keyword]")
        print("  move <plan_id> <student> <target_room>")
        print("  swap <plan_id> <student_a> <student_b>")
        print("  suspend <plan_id> <student>")
        print("  save_version <plan_id> <version_name>")
        print("  restore_version <version_id>")
        print("  export <plan_id> [output_path]")
        sys.exit(1)
    
    tool_name = sys.argv[1]
    
    tools = {
        "match": tool_match_dormitories,
        "summary": tool_get_plan_summary,
        "query_student": tool_query_student,
        "query_rooms": tool_query_rooms,
        "move": tool_move_student,
        "swap": tool_swap_students,
        "suspend": tool_move_to_suspended,
        "save_version": tool_save_version,
        "restore_version": tool_restore_version,
        "export": tool_export_assignment,
    }
    
    if tool_name not in tools:
        print(f"未知工具: {tool_name}")
        sys.exit(1)
    
    tool_func = tools[tool_name]
    args = sys.argv[2:]
    
    try:
        result = tool_func(*args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        print(json.dumps({"error": str(e)}, ensure_ascii=False, indent=2))
        sys.exit(1)
