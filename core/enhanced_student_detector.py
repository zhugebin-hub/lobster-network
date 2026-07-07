#!/usr/bin/env python3
"""
小龙虾网络 · 增强版学员状态检测器 V2
优化：增加GitHub commit检测、OpenClaw会话检测、多路径成果识别

解决原cronjob检测偏差问题：
1. 原检测仅依赖SSH连接和共享目录
2. 实际学员可能通过GitHub、OpenClaw对话等方式提交成果
3. 需要多路径检测避免误判"离线"
"""
import json
import os
import subprocess
import re
from datetime import datetime, timedelta
from pathlib import Path

class EnhancedStudentDetector:
    """增强版学员状态检测器"""
    
    def __init__(self):
        self.repo_path = Path("/home/admin/lobster-network")
        self.shared_dir = Path("/home/admin/go-training/shared")
        self.now = datetime.now()
        
        # 学员配置
        self.students = {
            "xiaochen": {
                "name": "小陈",
                "role": "实验数据分析师",
                "server": "121.43.80.231",
                "github_user": None,  # 待确认
                "ssh_user": "admin"
            },
            "zhuguxia": {
                "name": "诸葛虾",
                "role": "工具链与可视化专家",
                "server": "60.205.139.51",  # 实际IP
                "github_user": "zhugebin",
                "ssh_user": "admin"
            },
            "qoder": {
                "name": "qoder小龙虾",
                "role": "系统架构专家",
                "server": None,
                "github_user": None,  # 待确认
                "ssh_user": None
            },
            "hermes": {
                "name": "诸葛马(Hermes)",
                "role": "总导师/统稿评审",
                "server": "172.24.57.34",
                "github_user": "zhugebin-hub",
                "ssh_user": "admin"
            }
        }
    
    def run_cmd(self, cmd, timeout=30):
        """执行命令"""
        try:
            result = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)
    
    def check_ssh_connection(self, student_id):
        """检查SSH连接"""
        student = self.students[student_id]
        if not student.get("server"):
            return False, "无服务器配置"
        
        rc, out, err = self.run_cmd(
            f"ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "
            f"{student['ssh_user']}@{student['server']} 'echo ok'"
        )
        
        if rc == 0 and out == "ok":
            return True, "SSH连接正常"
        else:
            return False, f"SSH连接失败: {err[:100]}"
    
    def check_shared_directory(self, student_id):
        """检查共享目录提交"""
        from_dir = self.shared_dir / f"from-{student_id}"
        
        if not from_dir.exists():
            return False, 0, "目录不存在"
        
        # 查找最近24小时的文件
        files = list(from_dir.glob("*"))
        recent_files = []
        
        for f in files:
            if f.is_file():
                mtime = datetime.fromtimestamp(f.stat().st_mtime)
                if self.now - mtime < timedelta(hours=24):
                    recent_files.append(f)
        
        if recent_files:
            return True, len(recent_files), f"{len(recent_files)}个新文件"
        else:
            return False, 0, "无新文件"
    
    def check_github_commits(self, student_id):
        """检查GitHub提交（24小时内）"""
        student = self.students[student_id]
        
        # 使用git log检查最近提交
        rc, out, err = self.run_cmd(
            f"cd {self.repo_path} && git log --since='24 hours ago' "
            f"--all --oneline --author='{student.get('github_user', '')}' 2>/dev/null || "
            f"git log --since='24 hours ago' --all --oneline | head -20"
        )
        
        if rc == 0 and out:
            commits = [line for line in out.split('\n') if line.strip()]
            
            # 检查是否包含学员相关关键词
            relevant_commits = []
            keywords = [student_id, student['name'], 'zhuguxia', 'xiaochen', 'qoder', 'hermes']
            
            for commit in commits:
                for keyword in keywords:
                    if keyword.lower() in commit.lower():
                        relevant_commits.append(commit)
                        break
            
            if relevant_commits:
                return True, len(relevant_commits), f"{len(relevant_commits)}次提交"
            elif commits:
                # 有提交但不确定是否属于该学员
                return True, len(commits), f"仓库有{len(commits)}次提交"
        
        return False, 0, "无GitHub提交"
    
    def check_openclaw_session(self, student_id):
        """检查OpenClaw会话活跃度"""
        if student_id != "zhuguxia":
            return False, "非诸葛虾节点"
        
        # 检查OpenClaw Gateway进程
        rc, out, err = self.run_cmd(
            "ps aux | grep -i openclaw | grep -v grep"
        )
        
        if rc == 0 and out:
            return True, "OpenClaw Gateway运行中"
        
        # 检查端口
        rc, out, err = self.run_cmd(
            "ss -tlnp | grep 11676"
        )
        
        if rc == 0 and out:
            return True, "OpenClaw Gateway端口活跃"
        
        return False, "OpenClaw未检测到"
    
    def check_disk_space(self, student_id):
        """检查磁盘空间"""
        student = self.students[student_id]
        
        if not student.get("server"):
            return None, "无服务器配置"
        
        # 通过SSH检查
        rc, out, err = self.run_cmd(
            f"ssh -o ConnectTimeout=5 {student['ssh_user']}@{student['server']} "
            f"'df -h / | tail -1 | awk \"{{print \\\"\\$5\\\"}}\"'",
            timeout=10
        )
        
        if rc == 0 and out:
            usage = out.replace('%', '')
            try:
                usage_pct = int(usage)
                if usage_pct < 80:
                    return True, f"磁盘{usage_pct}%正常"
                elif usage_pct < 90:
                    return True, f"磁盘{usage_pct}%偏高"
                else:
                    return False, f"磁盘{usage_pct}%告警"
            except ValueError:
                return None, f"磁盘解析失败: {out}"
        
        return None, f"磁盘检查失败: {err[:50]}"
    
    def detect_student_status(self, student_id):
        """综合检测学员状态"""
        print(f"\n{'='*60}")
        print(f"🔍 检测学员: {self.students[student_id]['name']} ({student_id})")
        print(f"{'='*60}")
        
        results = {
            "student_id": student_id,
            "name": self.students[student_id]['name'],
            "detection_time": self.now.isoformat(),
            "checks": {}
        }
        
        # 1. SSH连接检测
        ssh_ok, ssh_msg = self.check_ssh_connection(student_id)
        results["checks"]["ssh"] = {"status": ssh_ok, "message": ssh_msg}
        print(f"  SSH连接: {'✅' if ssh_ok else '❌'} {ssh_msg}")
        
        # 2. 共享目录检测
        shared_ok, shared_count, shared_msg = self.check_shared_directory(student_id)
        results["checks"]["shared_dir"] = {
            "status": shared_ok,
            "file_count": shared_count,
            "message": shared_msg
        }
        print(f"  共享目录: {'✅' if shared_ok else '❌'} {shared_msg}")
        
        # 3. GitHub提交检测（新增）
        github_ok, github_count, github_msg = self.check_github_commits(student_id)
        results["checks"]["github"] = {
            "status": github_ok,
            "commit_count": github_count,
            "message": github_msg
        }
        print(f"  GitHub提交: {'✅' if github_ok else '❌'} {github_msg}")
        
        # 4. OpenClaw会话检测（新增）
        openclaw_ok, openclaw_msg = self.check_openclaw_session(student_id)
        results["checks"]["openclaw"] = {
            "status": openclaw_ok,
            "message": openclaw_msg
        }
        print(f"  OpenClaw会话: {'✅' if openclaw_ok else '❌'} {openclaw_msg}")
        
        # 5. 磁盘空间检测
        disk_ok, disk_msg = self.check_disk_space(student_id)
        results["checks"]["disk"] = {
            "status": disk_ok if disk_ok is not None else "unknown",
            "message": disk_msg
        }
        if disk_ok is not None:
            print(f"  磁盘空间: {'✅' if disk_ok else '⚠️'} {disk_msg}")
        else:
            print(f"  磁盘空间: ❓ {disk_msg}")
        
        # 综合判断
        active_checks = [
            ssh_ok,
            shared_ok,
            github_ok,
            openclaw_ok
        ]
        
        active_count = sum(1 for x in active_checks if x)
        total_checks = len([x for x in active_checks if x is not False])
        
        if active_count >= 2:
            overall_status = "active"
            emoji = "🟢"
        elif active_count == 1:
            overall_status = "warning"
            emoji = "🟡"
        else:
            overall_status = "offline"
            emoji = "🔴"
        
        results["overall_status"] = overall_status
        results["active_checks"] = f"{active_count}/{total_checks}"
        
        print(f"\n  {emoji} 综合状态: {overall_status} ({active_count}/{total_checks}项活跃)")
        
        return results
    
    def generate_report(self):
        """生成检测报告"""
        print("\n" + "="*60)
        print("📊 小龙虾网络 · 增强版学员状态检测报告")
        print(f"检测时间: {self.now.strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60)
        
        all_results = {}
        
        for student_id in self.students:
            result = self.detect_student_status(student_id)
            all_results[student_id] = result
        
        # 汇总
        print(f"\n{'='*60}")
        print("📋 汇总")
        print(f"{'='*60}")
        
        active_count = sum(1 for r in all_results.values() if r["overall_status"] == "active")
        warning_count = sum(1 for r in all_results.values() if r["overall_status"] == "warning")
        offline_count = sum(1 for r in all_results.values() if r["overall_status"] == "offline")
        
        print(f"  🟢 活跃: {active_count}人")
        print(f"  🟡 警告: {warning_count}人")
        print(f"  🔴 离线: {offline_count}人")
        print(f"  📊 活跃度: {active_count}/{len(all_results)} ({active_count/len(all_results)*100:.0f}%)")
        
        # 保存报告
        report_dir = Path("/home/admin/lobster-network/docs/detection_reports")
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = report_dir / f"detection_{self.now.strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n  📄 报告已保存: {report_file}")
        
        return all_results

def main():
    detector = EnhancedStudentDetector()
    results = detector.generate_report()
    
    # 更新学员状态文件
    for student_id, result in results.items():
        status_file = Path(
            f"/home/admin/lobster-network/domains/go/student_data/"
            f"{student_id}/detection_status.json"
        )
        status_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(status_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"  ✅ 更新状态: {status_file}")

if __name__ == "__main__":
    main()
