import argparse
import json
import random
from pathlib import Path

CITIES = ["杭州", "上海", "宁波", "苏州", "南京"]
BUILDINGS = ["A", "B", "C"]
DATES = [
    "2026-04-08", "2026-04-09", "2026-04-10", "2026-04-11", "2026-04-12",
    "2026-04-13", "2026-04-14", "2026-04-15", "2026-04-16", "2026-04-17"
]
TIME_SLOTS = [("09:00", "10:00"), ("10:00", "11:00"), ("14:00", "15:00"), ("15:00", "16:00")]
CAPACITIES = [8, 10, 12, 15, 20, 25, 30, 40]
STYLES = ["campus", "formal", "technical"]
JOBS = ["数据分析", "后端开发", "前端开发", "产品运营", "数据产品", "测试开发", "算法工程"]
CHANNELS = ["email", "sms", "dingtalk"]
STUDENTS = [f"2023{n:04d}" for n in range(1, 401)]
TEACHER_GROUPS = [
    ["t1", "t2", "t3"], ["t4", "t5", "t6"], ["t7", "t8", "t9"],
    ["a@example.com", "b@example.com"], ["c@example.com", "d@example.com", "e@example.com"]
]
TEMPLATE_IDS = ["resume_v1", "resume_v2", "resume_v3"]


def meeting_notice_case(i: int):
    date = DATES[(i + 2) % len(DATES)]
    building = BUILDINGS[(i + 1) % len(BUILDINGS)]
    start_time, end_time = TIME_SLOTS[i % len(TIME_SLOTS)]
    cap = CAPACITIES[(i + 3) % len(CAPACITIES)]
    recipients = TEACHER_GROUPS[i % len(TEACHER_GROUPS)]
    return {
        "instruction": f"查到{date} {building}楼 {start_time}-{end_time} 适合{cap}人开会的会议室后，给老师发送通知。",
        "gold_tools": ["query_meeting_room", "send_notification"],
        "gold_params": [
            {"date": date, "start_time": start_time, "end_time": end_time, "capacity": cap, "building": building},
            {"channel": CHANNELS[i % len(CHANNELS)], "recipients": recipients, "message": "会议室已预订"},
        ],
        "success_condition": "完成会议室查询并发送通知",
    }


def calendar_case(i: int):
    date = DATES[(i + 2) % len(DATES)]
    building = BUILDINGS[(i + 1) % len(BUILDINGS)]
    start_time, end_time = TIME_SLOTS[i % len(TIME_SLOTS)]
    cap = CAPACITIES[(i + 3) % len(CAPACITIES)]
    recipients = TEACHER_GROUPS[i % len(TEACHER_GROUPS)]
    return {
        "instruction": f"查到{date} {building}楼 {start_time}-{end_time} 适合{cap}人开会的会议室后，创建日历并给老师发送通知。",
        "gold_tools": ["query_meeting_room", "create_calendar_event", "send_notification"],
        "gold_params": [
            {"date": date, "start_time": start_time, "end_time": end_time, "capacity": cap, "building": building},
            {"title": "项目讨论会", "date": date, "start_time": start_time, "end_time": end_time, "attendees": recipients},
            {"channel": CHANNELS[i % len(CHANNELS)], "recipients": recipients, "message": "日历邀请已发送"},
        ],
        "success_condition": "完成查询、创建日历并发送通知",
    }


def resume_case(i: int):
    student_id = STUDENTS[(i * 5) % len(STUDENTS)]
    job = JOBS[(i + 1) % len(JOBS)]
    style = STYLES[(i + 1) % len(STYLES)]
    template_id = TEMPLATE_IDS[i % len(TEMPLATE_IDS)]
    return {
        "instruction": f"查询学号{student_id}的资料，生成一份面向{job}岗位的{style}风格简历，并导出为 PDF。",
        "gold_tools": ["query_student_profile", "generate_resume", "fill_pdf_template"],
        "gold_params": [
            {"student_id": student_id},
            {"student_id": student_id, "target_job": job, "style": style},
            {"template_id": template_id, "content_id": f"resume_content_{student_id}", "output_name": f"resume_{student_id}.pdf"},
        ],
        "success_condition": "完成资料查询、简历生成和 PDF 导出",
    }


def ranking_case(i: int):
    student_id = STUDENTS[(i * 5) % len(STUDENTS)]
    others = [STUDENTS[(i * 5 + 1) % len(STUDENTS)], STUDENTS[(i * 5 + 2) % len(STUDENTS)]]
    return {
        "instruction": f"查询学号{student_id}的资料，按 match 对候选人排序，并导出为 CSV。",
        "gold_tools": ["query_student_profile", "rank_candidates", "export_csv"],
        "gold_params": [
            {"student_id": student_id},
            {"candidate_ids": [student_id, *others], "criterion": "match"},
            {"records": [f"rank_result_{student_id}"], "filename": f"ranking_{student_id}.csv"},
        ],
        "success_condition": "完成资料查询、排序和 CSV 导出",
    }


def build_recovery_case(i: int):
    mode = i % 8
    if mode == 0:
        base = meeting_notice_case(i)
        fault = {"fault_type": "missing_required", "step": 0, "field": "building", "action": "remove", "description": "删除会议室查询中的必填字段 building"}
    elif mode == 1:
        base = meeting_notice_case(i)
        fault = {"fault_type": "wrong_type", "step": 0, "field": "capacity", "action": "replace", "bad_value": "20", "description": "把 capacity 从整数改成字符串"}
    elif mode == 2:
        base = calendar_case(i)
        fault = {"fault_type": "wrong_type", "step": 1, "field": "attendees", "action": "replace", "bad_value": "t1,t2,t3", "description": "把 attendees 从数组改成字符串"}
    elif mode == 3:
        base = calendar_case(i)
        fault = {"fault_type": "wrong_enum", "step": 2, "field": "channel", "action": "replace", "bad_value": "wechat", "description": "把通知渠道改成非法枚举值 wechat"}
    elif mode == 4:
        base = resume_case(i)
        fault = {"fault_type": "wrong_enum", "step": 1, "field": "style", "action": "replace", "bad_value": "campus-formal", "description": "把简历风格改成非法枚举值 campus-formal"}
    elif mode == 5:
        base = resume_case(i)
        fault = {"fault_type": "missing_required", "step": 2, "field": "content_id", "action": "remove", "description": "删除 PDF 填充步骤中的必填字段 content_id"}
    elif mode == 6:
        base = ranking_case(i)
        fault = {"fault_type": "wrong_enum", "step": 1, "field": "criterion", "action": "replace", "bad_value": "semantic", "description": "把排序 criterion 改成非法枚举 semantic"}
    else:
        base = ranking_case(i)
        fault = {"fault_type": "wrong_type", "step": 2, "field": "records", "action": "replace", "bad_value": "rank_result_as_string", "description": "把 records 从数组改成字符串"}

    return {
        "task_id": f"recovery_{i+1:03d}",
        "level": "recovery",
        "instruction": base["instruction"],
        "gold_tools": base["gold_tools"],
        "gold_params": base["gold_params"],
        "success_condition": base["success_condition"],
        "fault_type": fault["fault_type"],
        "fault_description": fault["description"],
        "recovery_target_step": fault["step"],
        "fault_plan": [fault],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--num_tasks", type=int, default=120)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    rows = [build_recovery_case(i) for i in range(args.num_tasks)]
    random.shuffle(rows)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Generated {len(rows)} recovery tasks to {out}")


if __name__ == "__main__":
    main()
