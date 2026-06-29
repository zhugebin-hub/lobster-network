#!/usr/bin/env python3
"""
学员端消息轮询脚本 (Student Message Polling Script)
部署在每个学员节点上，定期从诸葛马服务器拉取新消息并处理

功能:
1. 每5分钟检查 from-hermes/ 目录新消息
2. 自动处理训练任务、对局通知、系统通知
3. 发送ACK回执到 cc-ack/ 目录
4. 提交训练结果到 results/ 目录
5. 清理已处理消息

部署方式:
  crontab -e
  */5 * * * * /usr/bin/python3 /home/admin/lobster-network/scripts/student_poller.py <node_id>
  
示例:
  python3 student_poller.py xiaochen
  python3 student_poller.py zhuguxia
  python3 student_poller.py qoder
"""

import json
import os
import sys
import time
import subprocess
import hashlib
from datetime import datetime, timedelta
from pathlib import Path


class StudentPoller:
    """学员端消息轮询器"""
    
    def __init__(self, node_id, hermes_host="47.93.6.57", hermes_user="admin"):
        self.node_id = node_id
        self.hermes_host = hermes_host
        self.hermes_user = hermes_user
        
        # 路径配置
        self.base_dir = Path("/home/admin/lobster-network")
        self.shared_dir = self.base_dir / ".shared" / "messages"
        self.from_hermes_dir = self.shared_dir / "from-hermes"
        self.cc_ack_dir = self.shared_dir / "cc-ack"
        self.results_dir = self.base_dir / "results" / node_id
        self.state_file = self.base_dir / f".poller_state_{node_id}.json"
        self.log_file = self.base_dir / f"poller_{node_id}.log"
        
        # 已处理消息哈希集合
        self.processed = self.load_state()
        
        # 统计
        self.stats = {
            "checked": 0,
            "new": 0,
            "processed": 0,
            "acked": 0,
            "errors": 0,
            "last_run": None
        }
    
    def load_state(self):
        """加载已处理消息状态"""
        if self.state_file.exists():
            try:
                data = json.loads(self.state_file.read_text())
                return set(data.get("processed_hashes", []))
            except:
                pass
        return set()
    
    def save_state(self):
        """保存已处理消息状态"""
        # 只保留最近1000个哈希，防止文件过大
        recent = list(self.processed)[-1000:]
        data = {
            "node_id": self.node_id,
            "processed_hashes": recent,
            "last_run": datetime.now().isoformat(),
            "total_processed": len(recent)
        }
        self.state_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def log(self, level, message):
        """记录日志"""
        timestamp = datetime.now().isoformat()
        log_line = f"[{timestamp}] [{level}] {message}\n"
        print(log_line.strip())
        try:
            with open(self.log_file, "a") as f:
                f.write(log_line)
        except:
            pass
    
    def get_message_hash(self, filename):
        """计算消息文件哈希"""
        filepath = self.from_hermes_dir / filename
        if not filepath.exists():
            return None
        try:
            content = filepath.read_bytes()
            return hashlib.md5(content).hexdigest()
        except:
            return None
    
    def fetch_new_messages(self):
        """从诸葛马服务器获取新消息"""
        self.log("INFO", f"检查新消息: {self.from_hermes_dir}")
        
        if not self.from_hermes_dir.exists():
            self.from_hermes_dir.mkdir(parents=True, exist_ok=True)
        
        new_messages = []
        
        try:
            for filepath in sorted(self.from_hermes_dir.glob("*.json")):
                filename = filepath.name
                msg_hash = self.get_message_hash(filename)
                
                if msg_hash and msg_hash not in self.processed:
                    new_messages.append({
                        "filename": filename,
                        "hash": msg_hash,
                        "path": str(filepath)
                    })
                    self.stats["new"] += 1
                
                self.stats["checked"] += 1
        except Exception as e:
            self.log("ERROR", f"读取消息目录失败: {e}")
            self.stats["errors"] += 1
        
        return new_messages
    
    def process_message(self, msg):
        """处理单条消息"""
        filename = msg["filename"]
        filepath = Path(msg["path"])
        
        try:
            content = filepath.read_text()
            data = json.loads(content)
        except json.JSONDecodeError as e:
            self.log("ERROR", f"解析消息失败 {filename}: {e}")
            # 尝试作为原始文本保存
            try:
                backup = filepath.parent / f"backup_{filepath.name}"
                filepath.rename(backup)
                self.log("WARN", f"已备份到: backup_{filepath.name}")
            except:
                pass
            self.stats["errors"] += 1
            return False
        
        msg_type = data.get("type", "unknown")
        subject = data.get("subject", data.get("title", "无主题"))
        tracking_id = data.get("tracking_id", "")
        
        self.log("INFO", f"处理消息: [{msg_type}] {subject}")
        
        # 根据消息类型处理
        if msg_type == "training_task":
            self._handle_training_task(data, filename)
        elif msg_type == "go_match":
            self._handle_go_match(data, filename)
        elif msg_type == "cc_message":
            self._handle_cc_message(data, filename)
        elif msg_type == "system_notification":
            self._handle_system_notification(data, filename)
        else:
            self._handle_generic(data, filename)
        
        # 标记为已处理
        self.processed.add(msg["hash"])
        self.stats["processed"] += 1
        
        # 发送ACK
        if tracking_id:
            self.send_ack(tracking_id, filename)
        
        return True
    
    def _handle_training_task(self, data, filename):
        """处理训练任务"""
        day = data.get("day", "unknown")
        tasks = data.get("tasks", [])
        
        self.log("INFO", f"收到训练任务: Day{day}, {len(tasks)}项")
        
        # 创建任务文件
        task_file = self.results_dir / f"task_{day}_{Path(filename).stem}.json"
        task_file.parent.mkdir(parents=True, exist_ok=True)
        task_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
        
        # 执行训练（如果是qoder节点）
        if self.node_id == "qoder":
            self._execute_training(data)
    
    def _handle_go_match(self, data, filename):
        """处理对局通知"""
        match_id = data.get("match_id", "unknown")
        opponent = data.get("opponent", "unknown")
        deadline = data.get("deadline", "unknown")
        
        self.log("INFO", f"收到对局通知: {match_id} vs {opponent}, 截止: {deadline}")
        
        # 记录对局任务
        match_file = self.results_dir / f"match_{match_id}.json"
        match_file.parent.mkdir(parents=True, exist_ok=True)
        match_file.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    
    def _handle_cc_message(self, data, filename):
        """处理CC协议消息"""
        tracking_id = data.get("tracking_id", "")
        requires_ack = data.get("requires_ack", False)
        
        if requires_ack and tracking_id:
            self.log("INFO", f"CC消息需要ACK: {tracking_id}")
            # ACK将在process_message中统一发送
    
    def _handle_system_notification(self, data, filename):
        """处理系统通知"""
        level = data.get("level", "info")
        message = data.get("message", "")
        self.log("INFO", f"系统通知: {message}")
    
    def _handle_generic(self, data, filename):
        """处理通用消息"""
        self.log("INFO", f"通用消息已接收: {filename}")
    
    def _execute_training(self, data):
        """执行训练（仅qoder节点）"""
        day = data.get("day", "")
        self.log("INFO", f"qoder开始执行Day{day}训练")
        
        # 触发训练脚本
        try:
            training_script = self.base_dir / "scripts" / "run_training.py"
            if training_script.exists():
                result = subprocess.run(
                    ["python3", str(training_script), f"day{day}"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                if result.returncode == 0:
                    self.log("INFO", f"Day{day}训练完成")
                else:
                    self.log("ERROR", f"Day{day}训练失败: {result.stderr}")
        except Exception as e:
            self.log("ERROR", f"训练执行异常: {e}")
    
    def send_ack(self, tracking_id, source_filename):
        """发送ACK回执"""
        ack_data = {
            "type": "cc_ack",
            "tracking_id": tracking_id,
            "from": self.node_id,
            "to": "zhugema",
            "timestamp": datetime.now().isoformat(),
            "status": "acknowledged",
            "source_message": source_filename
        }
        
        ack_filename = f"ack_{tracking_id}_{self.node_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        ack_filepath = self.cc_ack_dir / ack_filename
        
        try:
            self.cc_ack_dir.mkdir(parents=True, exist_ok=True)
            ack_filepath.write_text(json.dumps(ack_data, indent=2, ensure_ascii=False))
            self.stats["acked"] += 1
            self.log("INFO", f"ACK已发送: {tracking_id} -> {ack_filename}")
        except Exception as e:
            self.log("ERROR", f"ACK发送失败: {e}")
            self.stats["errors"] += 1
    
    def cleanup_old_messages(self, max_age_hours=24):
        """清理旧消息文件"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        cleaned = 0
        
        try:
            for filepath in self.from_hermes_dir.glob("*.json"):
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                if mtime < cutoff:
                    msg_hash = self.get_message_hash(filepath.name)
                    if msg_hash in self.processed:
                        filepath.unlink()
                        cleaned += 1
        except Exception as e:
            self.log("ERROR", f"清理失败: {e}")
        
        if cleaned > 0:
            self.log("INFO", f"清理了 {cleaned} 个旧消息文件")
        
        return cleaned
    
    def run(self):
        """执行轮询"""
        self.stats["last_run"] = datetime.now().isoformat()
        self.log("INFO", f"=== 轮询开始 [{self.node_id}] ===")
        
        # 获取新消息
        new_messages = self.fetch_new_messages()
        
        if new_messages:
            self.log("INFO", f"发现 {len(new_messages)} 条新消息")
            
            for msg in new_messages:
                self.process_message(msg)
        else:
            self.log("INFO", "无新消息")
        
        # 清理旧消息
        self.cleanup_old_messages()
        
        # 保存状态
        self.save_state()
        
        # 输出统计
        self.log("INFO", f"=== 轮询完成: 检查={self.stats['checked']} 新={self.stats['new']} 处理={self.stats['processed']} ACK={self.stats['acked']} 错误={self.stats['errors']} ===")
        
        return self.stats


def main():
    if len(sys.argv) < 2:
        print("用法: python3 student_poller.py <node_id>")
        print("示例: python3 student_poller.py xiaochen")
        sys.exit(1)
    
    node_id = sys.argv[1]
    
    # 创建轮询器
    poller = StudentPoller(node_id)
    
    # 执行轮询
    stats = poller.run()
    
    # 返回状态码
    sys.exit(1 if stats["errors"] > 0 else 0)


if __name__ == "__main__":
    main()
