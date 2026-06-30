
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


def build_single(i: int):
    mode = i % 5
    student_id = STUDENTS[i % len(STUDENTS)]
    city = CITIES[i % len(CITIES)]
    date = DATES[i % len(DATES)]
    building = BUILDINGS[i % len(BUILDINGS)]
    start_time, end_time = TIME_SLOTS[i % len(TIME_SLOTS)]
    cap = CAPACITIES[i % len(CAPACITIES)]
    job = JOBS[i % len(JOBS)]
    style = STYLES[i % len(STYLES)]

    if mode in (0, 1):
        return {
            "task_id": f"single_{i+1:03d}",
            "level": "single",
            "instruction": f"帮我查询{date} {building} 楼 {start_time}-{end_time} 能容纳 {cap} 人的会议室。",
            "gold_tools": ["query_meeting_room"],
            "gold_params": [{
                "date": date, "start_time": start_time, "end_time": end_time,
                "capacity": cap, "building": building
            }],
            "success_condition": "返回合法会议室列表"
        }
    elif mode == 2:
        return {
            "task_id": f"single_{i+1:03d}",
            "level": "single",
            "instruction": f"帮我查一下{city}{date}的天气。",
            "gold_tools": ["get_weather"],
            "gold_params": [{"city": city, "date": date}],
            "success_condition": "返回天气结果"
        }
    elif mode == 3:
        return {
            "task_id": f"single_{i+1:03d}",
            "level": "single",
            "instruction": f"查询学号 {student_id} 的学生资料。",
            "gold_tools": ["query_student_profile"],
            "gold_params": [{"student_id": student_id}],
            "success_condition": "返回学生资料"
        }
    else:
        return {
            "task_id": f"single_{i+1:03d}",
            "level": "single",
            "instruction": f"给学号 {student_id} 生成一份面向{job}岗位的{style}风格简历。",
            "gold_tools": ["generate_resume"],
            "gold_params": [{"student_id": student_id, "target_job": job, "style": style}],
            "success_condition": "成功生成简历内容"
        }


def build_double(i: int):
    student_id = STUDENTS[(i*3) % len(STUDENTS)]
    city = CITIES[i % len(CITIES)]
    date = DATES[(i+2) % len(DATES)]
    building = BUILDINGS[(i+1) % len(BUILDINGS)]
    start_time, end_time = TIME_SLOTS[(i+1) % len(TIME_SLOTS)]
    cap = CAPACITIES[(i+2) % len(CAPACITIES)]
    job = JOBS[(i+1) % len(JOBS)]
    style = STYLES[(i+1) % len(STYLES)]
    recipients = TEACHER_GROUPS[i % len(TEACHER_GROUPS)]
    channel = CHANNELS[i % len(CHANNELS)]
    mode = i % 4

    if mode == 0:
        return {
            "task_id": f"double_{i+1:03d}",
            "level": "double",
            "instruction": f"查到{date} {building} 楼 {start_time}-{end_time} 适合 {cap} 人开会的会议室后，给相关老师发送通知。",
            "gold_tools": ["query_meeting_room", "send_notification"],
            "gold_params": [
                {"date": date, "start_time": start_time, "end_time": end_time, "capacity": cap, "building": building},
                {"channel": channel, "recipients": recipients, "message": "会议室已预订"}
            ],
            "success_condition": "完成查询并发送通知"
        }
    elif mode == 1:
        return {
            "task_id": f"double_{i+1:03d}",
            "level": "double",
            "instruction": f"先查询学号 {student_id} 的资料，再生成一份面向{job}岗位的{style}风格简历。",
            "gold_tools": ["query_student_profile", "generate_resume"],
            "gold_params": [
                {"student_id": student_id},
                {"student_id": student_id, "target_job": job, "style": style}
            ],
            "success_condition": "完成资料查询并生成简历"
        }
    elif mode == 2:
        return {
            "task_id": f"double_{i+1:03d}",
            "level": "double",
            "instruction": f"查询{job}岗位在{city}的招聘信息，并把结果导出为 CSV。",
            "gold_tools": ["query_job_posting", "export_csv"],
            "gold_params": [
                {"keyword": job, "city": city},
                {"records": [f"{job}_{city}_top3"], "filename": f"jobs_{i+1:03d}.csv"}
            ],
            "success_condition": "完成查询并导出 CSV"
        }
    else:
        return {
            "task_id": f"double_{i+1:03d}",
            "level": "double",
            "instruction": f"先查询{city}{date}的天气，再通过短信提醒出差同事注意出行。",
            "gold_tools": ["get_weather", "send_notification"],
            "gold_params": [
                {"city": city, "date": date},
                {"channel": "sms", "recipients": recipients, "message": "请关注天气并注意出行"}
            ],
            "success_condition": "完成天气查询并发送提醒"
        }


def build_multi(i: int):
    student_id = STUDENTS[(i*5) % len(STUDENTS)]
    city = CITIES[(i+2) % len(CITIES)]
    date = DATES[(i+4) % len(DATES)]
    building = BUILDINGS[(i+2) % len(BUILDINGS)]
    start_time, end_time = TIME_SLOTS[(i+2) % len(TIME_SLOTS)]
    cap = CAPACITIES[(i+3) % len(CAPACITIES)]
    job = JOBS[(i+2) % len(JOBS)]
    style = STYLES[(i+2) % len(STYLES)]
    recipients = TEACHER_GROUPS[(i+1) % len(TEACHER_GROUPS)]
    template_id = TEMPLATE_IDS[i % len(TEMPLATE_IDS)]
    mode = i % 4

    if mode == 0:
        return {
            "task_id": f"multi_{i+1:03d}",
            "level": "multi",
            "instruction": f"为学号 {student_id} 的同学匹配{job}岗位，生成{style}风格简历，并导出为 pdf。",
            "gold_tools": ["query_student_profile", "query_job_posting", "generate_resume", "fill_pdf_template"],
            "gold_params": [
                {"student_id": student_id},
                {"keyword": job, "city": city},
                {"student_id": student_id, "target_job": job, "style": style},
                {"template_id": template_id, "content_id": f"resume_content_{student_id}", "output_name": f"resume_{student_id}.pdf"}
            ],
            "success_condition": "完成匹配、生成与导出"
        }
    elif mode == 1:
        return {
            "task_id": f"multi_{i+1:03d}",
            "level": "multi",
            "instruction": f"查{date} {building} 楼 {cap} 人会议室，创建日历，并给参会人发邮件。",
            "gold_tools": ["query_meeting_room", "create_calendar_event", "send_notification"],
            "gold_params": [
                {"date": date, "start_time": start_time, "end_time": end_time, "capacity": cap, "building": building},
                {"title": "项目讨论会", "date": date, "start_time": start_time, "end_time": end_time, "attendees": recipients},
                {"channel": "email", "recipients": recipients, "message": "日历邀请已发送"}
            ],
            "success_condition": "完成查询、建历和通知"
        }
    elif mode == 2:
        return {
            "task_id": f"multi_{i+1:03d}",
            "level": "multi",
            "instruction": f"查询学号 {student_id} 的资料，按 match 对候选人排序，并导出为 CSV。",
            "gold_tools": ["query_student_profile", "rank_candidates", "export_csv"],
            "gold_params": [
                {"student_id": student_id},
                {"candidate_ids": [student_id, STUDENTS[(i*5+1)%len(STUDENTS)], STUDENTS[(i*5+2)%len(STUDENTS)]], "criterion": "match"},
                {"records": [f"rank_result_{student_id}"], "filename": f"ranking_{student_id}.csv"}
            ],
            "success_condition": "完成查询、排序与导出"
        }
    else:
        return {
            "task_id": f"multi_{i+1:03d}",
            "level": "multi",
            "instruction": f"查询{city}{date}天气，检索{job}岗位，并给求职群发送提醒。",
            "gold_tools": ["get_weather", "query_job_posting", "send_notification"],
            "gold_params": [
                {"city": city, "date": date},
                {"keyword": job, "city": city},
                {"channel": "dingtalk", "recipients": recipients, "message": f"{job}岗位与天气信息已整理"}
            ],
            "success_condition": "完成天气查询、岗位检索与群提醒"
        }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_single', type=int, default=70)
    parser.add_argument('--num_double', type=int, default=60)
    parser.add_argument('--num_multi', type=int, default=70)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()

    random.seed(args.seed)
    rows = []
    rows.extend(build_single(i) for i in range(args.num_single))
    rows.extend(build_double(i) for i in range(args.num_double))
    rows.extend(build_multi(i) for i in range(args.num_multi))
    random.shuffle(rows)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('w', encoding='utf-8') as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')

    print(f'Generated {len(rows)} tasks to {out}')


if __name__ == '__main__':
    main()
