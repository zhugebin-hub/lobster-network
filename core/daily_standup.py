#!/usr/bin/env python3
"""
小龙虾网络 · 每日站会协议 (Daily Standup Protocol) V1
功能：强制每日汇报，提升节点执行率

流程：
1. 检查学员昨日任务完成情况
2. 生成站会报告
3. 发送提醒/奖励通知
4. 更新仪表盘状态
"""
import json
import os
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

# 路径配置
REPO_ROOT = Path("/home/admin/lobster-network")
SHARED_DIR = Path("/home/admin/go-training/shared")
QUEUE_DIR = REPO_ROOT / "lobster-data" / "messages" / "queue"
PAPER_DIR = REPO_ROOT / "domains" / "paper"
STUDENT_DIR = PAPER_DIR / "student_data"

# 学员配置
STUDENTS = {
    "qoder": {"name": "qoder小龙虾", "role": "系统架构专家", "level": "六段"},
    "xiaochen": {"name": "小陈", "role": "实验数据分析师", "level": "二段"},
    "zhuguxia": {"name": "诸葛虾", "role": "工具链与可视化专家", "level": "二段"},
    "hermes": {"name": "诸葛马 (Hermes)", "role": "总导师/统稿评审", "level": "八段"}
}

# 龙虾币奖励规则
REWARDS = {
    "submit_paper": 50,      # 提交精读笔记
    "submit_writing": 30,    # 提交写作练习
    "daily_standup": 10,     # 每日站会汇报
    "complete_task": 20,     # 完成任务
    "help_other": 15         # 帮助其他学员
}

class DailyStandup:
    """每日站会管理器"""
    
    def __init__(self):
        self.now = datetime.now()
        self.yesterday = self.now - timedelta(days=1)
        self.report = {
            "date": self.now.strftime("%Y-%m-%d"),
            "standup_time": self.now.strftime("%H:%M"),
            "students": {},
            "total_rewards": 0,
            "issues": [],
            "highlights": []
        }
    
    def check_student_activity(self, student_id):
        """检查学员活动情况"""
        student_info = STUDENTS[student_id]
        
        # 检查论文模块提交
        paper_path = STUDENT_DIR / student_id
        profile_path = paper_path / "profile.json"
        
        papers_read = 0
        notes_completed = 0
        words_written = 0
        exercises_done = 0
        
        if profile_path.exists():
            try:
                with open(profile_path) as f:
                    profile = json.load(f)
                papers_read = profile.get("papers_read", 0)
                notes_completed = profile.get("notes_completed", 0)
                words_written = profile.get("words_written", 0)
                exercises_done = len(profile.get("exercises_done", []))
            except:
                pass
        
        # 检查共享目录提交
        from_dir = SHARED_DIR / f"from-{student_id}"
        recent_submissions = 0
        if from_dir.exists():
            files = list(from_dir.glob("*.json"))
            # 检查最近24小时的提交
            for f in files:
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if (self.now - mtime).total_seconds() < 86400:
                    recent_submissions += 1
        
        # 计算奖励
        rewards = 0
        if recent_submissions > 0:
            rewards += REWARDS["daily_standup"]
        if papers_read > 0:
            rewards += papers_read * REWARDS["submit_paper"]
        if notes_completed > 0:
            rewards += notes_completed * REWARDS["submit_writing"]
        
        activity = {
            "name": student_info["name"],
            "role": student_info["role"],
            "level": student_info["level"],
            "papers_read": papers_read,
            "notes_completed": notes_completed,
            "words_written": words_written,
            "exercises_done": exercises_done,
            "recent_submissions": recent_submissions,
            "rewards": rewards,
            "status": "active" if recent_submissions > 0 else "inactive",
            "last_active": "今天" if recent_submissions > 0 else "未知"
        }
        
        return activity
    
    def generate_report(self):
        """生成站会报告"""
        print(f"\n{'='*60}")
        print(f"📅 小龙虾网络 · 每日站会报告")
        print(f"日期: {self.report['date']} | 时间: {self.report['standup_time']}")
        print(f"{'='*60}")
        
        for student_id in STUDENTS:
            activity = self.check_student_activity(student_id)
            self.report["students"][student_id] = activity
            
            status_icon = "✅" if activity["status"] == "active" else "⚠️"
            print(f"\n{status_icon} {activity['name']} ({activity['role']})")
            print(f"   段位: {activity['level']}")
            print(f"   论文阅读: {activity['papers_read']} 篇")
            print(f"   精读笔记: {activity['notes_completed']} 篇")
            print(f"   写作字数: {activity['words_written']} 字")
            print(f"   练习完成: {activity['exercises_done']} 题")
            print(f"   昨日提交: {activity['recent_submissions']} 次")
            print(f"   龙虾币奖励: {activity['rewards']} 🦞")
            
            if activity["status"] == "inactive":
                self.report["issues"].append(f"{activity['name']} 昨日无提交")
            else:
                self.report["highlights"].append(f"{activity['name']} 完成 {activity['recent_submissions']} 次提交")
            
            self.report["total_rewards"] += activity["rewards"]
        
        print(f"\n{'='*60}")
        print(f"📊 汇总")
        print(f"   总奖励: {self.report['total_rewards']} 🦞")
        print(f"   活跃学员: {sum(1 for s in self.report['students'].values() if s['status'] == 'active')}/{len(STUDENTS)}")
        
        if self.report["issues"]:
            print(f"\n⚠️ 问题:")
            for issue in self.report["issues"]:
                print(f"   - {issue}")
        
        if self.report["highlights"]:
            print(f"\n✨ 亮点:")
            for highlight in self.report["highlights"]:
                print(f"   - {highlight}")
        
        print(f"{'='*60}")
        
        return self.report
    
    def send_reminders(self):
        """发送提醒通知"""
        print(f"\n📤 发送提醒通知...")
        
        for student_id, activity in self.report["students"].items():
            if activity["status"] == "inactive":
                # 发送提醒消息
                msg = {
                    "id": str(uuid.uuid4()),
                    "from": "hermes",
                    "to": student_id,
                    "type": "daily_standup_reminder",
                    "timestamp": self.now.isoformat(),
                    "title": "📅 每日站会提醒",
                    "content": f"{activity['name']}，昨日无提交记录。请完成今日任务并提交到 domains/paper/student_data/{student_id}/",
                    "action_required": True
                }
                
                # 写入队列
                inbox_dir = QUEUE_DIR / student_id / "inbox"
                inbox_dir.mkdir(parents=True, exist_ok=True)
                
                filename = f"standup_reminder_{student_id}_{self.now.strftime('%Y%m%d_%H%M%S')}.json"
                filepath = inbox_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(msg, f, ensure_ascii=False, indent=2)
                
                print(f"  ✅ 提醒已发送给 {student_id}")
            else:
                # 发送奖励通知
                msg = {
                    "id": str(uuid.uuid4()),
                    "from": "hermes",
                    "to": student_id,
                    "type": "daily_standup_reward",
                    "timestamp": self.now.isoformat(),
                    "title": "🦞 龙虾币奖励",
                    "content": f"{activity['name']}，昨日完成 {activity['recent_submissions']} 次提交，获得 {activity['rewards']} 龙虾币奖励！",
                    "action_required": False
                }
                
                inbox_dir = QUEUE_DIR / student_id / "inbox"
                inbox_dir.mkdir(parents=True, exist_ok=True)
                
                filename = f"standup_reward_{student_id}_{self.now.strftime('%Y%m%d_%H%M%S')}.json"
                filepath = inbox_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(msg, f, ensure_ascii=False, indent=2)
                
                print(f"  🦞 奖励已发放给 {student_id} ({activity['rewards']} 🦞)")
    
    def save_report(self):
        """保存报告"""
        report_dir = REPO_ROOT / "docs" / "daily_reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"standup_{self.now.strftime('%Y%m%d')}.json"
        filepath = report_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 报告已保存: {filepath}")

def main():
    """主函数"""
    standup = DailyStandup()
    
    # 生成报告
    report = standup.generate_report()
    
    # 发送提醒
    standup.send_reminders()
    
    # 保存报告
    standup.save_report()
    
    print(f"\n✅ 每日站会流程完成")

if __name__ == "__main__":
    main()
