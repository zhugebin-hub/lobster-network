#!/usr/bin/env python3
"""
主动服务系统 (Proactive Service System)
基于NWDAF分析结果，自动推送辅助资源，实现从"被动响应"到"主动服务"

功能:
1. 根据瓶颈维度自动推送训练资源
2. 定时检查学员状态，主动发送提醒
3. 资源库管理 (训练题/视频/文档)
4. 推送效果追踪

部署:
  python3 scripts/proactive_service.py <node_id>
  或定时: 0 */4 * * * python3 scripts/proactive_service.py all

作者: 诸葛马 (Hermes)
日期: 2026-06-30
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class ProactiveServiceEngine:
    """主动服务引擎"""
    
    # 资源库配置
    RESOURCE_LIBRARY = {
        "understanding": {
            "name": "理解力提升",
            "resources": [
                {"type": "training", "level": "入门", "count": 50, "focus": "基础棋型识别"},
                {"type": "video", "title": "围棋基础概念讲解", "duration": "15min"},
                {"type": "document", "title": "棋型分类手册", "pages": 20},
            ]
        },
        "reasoning": {
            "name": "推理力强化",
            "resources": [
                {"type": "training", "level": "高级", "count": 30, "focus": "倒扑/扑/征子"},
                {"type": "game", "count": 5, "focus": "中盘战斗训练"},
                {"type": "document", "title": "推理力训练指南", "pages": 35},
            ]
        },
        "reflection": {
            "name": "反思力培养",
            "resources": [
                {"type": "review", "count": 3, "focus": "对局复盘模板"},
                {"type": "document", "title": "错误模式识别手册", "pages": 25},
                {"type": "training", "level": "中级", "count": 20, "focus": "常见错误题型"},
            ]
        },
        "execution": {
            "name": "执行力提升",
            "resources": [
                {"type": "schedule", "daily_target": 30, "focus": "每日训练计划"},
                {"type": "reminder", "frequency": "2h", "focus": "训练提醒配置"},
            ]
        },
        "tooling": {
            "name": "工具力培训",
            "resources": [
                {"type": "tutorial", "title": "自动化脚本使用指南", "steps": 10},
                {"type": "document", "title": "SSH/Git操作手册", "pages": 15},
            ]
        },
        "eq": {
            "name": "情商培养",
            "resources": [
                {"type": "cc_guide", "title": "CC协议使用规范", "sections": 5},
                {"type": "reminder", "frequency": "daily", "focus": "及时ACK提醒"},
            ]
        },
        "aq": {
            "name": "逆商训练",
            "resources": [
                {"type": "training", "level": "中级", "count": 20, "focus": "挫折应对题"},
                {"type": "game", "count": 3, "focus": "劣势翻盘训练"},
            ]
        },
        "retrieval": {
            "name": "检索力提升",
            "resources": [
                {"type": "tutorial", "title": "信息检索技巧", "steps": 8},
                {"type": "document", "title": "棋谱检索指南", "pages": 10},
            ]
        },
    }
    
    # 推送策略
    PUSH_STRATEGIES = {
        "critical": {"interval_hours": 2, "max_per_day": 6, "channels": ["cc_message", "reminder"]},
        "warning": {"interval_hours": 4, "max_per_day": 4, "channels": ["cc_message"]},
        "info": {"interval_hours": 8, "max_per_day": 2, "channels": ["cc_message"]},
    }
    
    def __init__(self, node_id: str, base_dir: str = "/home/admin/lobster-network"):
        self.node_id = node_id
        self.base_dir = Path(base_dir)
        self.reports_dir = self.base_dir / "reports" / "nwda"
        self.push_log_dir = self.base_dir / "logs" / "proactive_push"
        self.push_log_dir.mkdir(parents=True, exist_ok=True)
        self.from_hermes_dir = self.base_dir / ".shared" / "messages" / "from-hermes"
        self.from_hermes_dir.mkdir(parents=True, exist_ok=True)
        
        # 推送历史
        self.push_history = self.load_push_history()
    
    def load_push_history(self) -> Dict:
        """加载推送历史"""
        history_file = self.push_log_dir / f"push_history_{self.node_id}.json"
        if history_file.exists():
            try:
                return json.loads(history_file.read_text())
            except:
                pass
        return {"pushes": [], "total": 0}
    
    def save_push_history(self):
        """保存推送历史"""
        history_file = self.push_log_dir / f"push_history_{self.node_id}.json"
        history_file.write_text(json.dumps(self.push_history, indent=2, ensure_ascii=False))
    
    def load_nwda_report(self) -> Optional[Dict]:
        """加载最新NWDAF报告"""
        if not self.reports_dir.exists():
            return None
        
        # 查找最新报告
        reports = sorted(self.reports_dir.glob(f"nwda-{self.node_id}-*.json"))
        if reports:
            try:
                return json.loads(reports[-1].read_text())
            except:
                pass
        return None
    
    def check_push_quota(self, strategy: str) -> bool:
        """检查推送配额"""
        today = datetime.now().strftime('%Y-%m-%d')
        today_pushes = [p for p in self.push_history.get("pushes", []) 
                       if p.get("date", "") == today]
        
        max_per_day = self.PUSH_STRATEGIES.get(strategy, {}).get("max_per_day", 4)
        return len(today_pushes) < max_per_day
    
    def generate_push_message(self, bottleneck: Dict) -> Dict:
        """生成推送消息"""
        dimension = bottleneck["dimension"]
        resource_info = self.RESOURCE_LIBRARY.get(dimension, {})
        resources = resource_info.get("resources", [])
        
        # 构建消息内容
        content_lines = [
            f"📚 **{resource_info.get('name', dimension)}资源推送**",
            f"",
            f"检测到您的**{bottleneck['name']}**维度需要加强 ({bottleneck['score']:.1f}分)",
            f"",
            f"**推荐资源:**",
        ]
        
        for i, res in enumerate(resources[:3], 1):
            res_type = res.get("type", "unknown")
            if res_type == "training":
                content_lines.append(f"{i}. 📝 {res.get('focus', '训练')} - {res.get('count', 0)}题 ({res.get('level', '中级')})")
            elif res_type == "video":
                content_lines.append(f"{i}. 🎬 {res.get('title', '视频')} - {res.get('duration', 'N/A')}")
            elif res_type == "document":
                content_lines.append(f"{i}. 📄 {res.get('title', '文档')} - {res.get('pages', 0)}页")
            elif res_type == "game":
                content_lines.append(f"{i}. 🎮 对局训练 - {res.get('count', 0)}局 ({res.get('focus', '')})")
            elif res_type == "review":
                content_lines.append(f"{i}. 🔄 复盘训练 - {res.get('count', 0)}次 ({res.get('focus', '')})")
            else:
                content_lines.append(f"{i}. 📌 {res.get('title', res.get('focus', '资源'))}")
        
        content_lines.append(f"\n💡 **建议**: {bottleneck.get('recommendation', '针对性训练')}")
        content_lines.append(f"\n⏰ 推送时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        
        return {
            "type": "proactive_resource_push",
            "tracking_id": f"push-{self.node_id}-{dimension}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "from": "zhugema",
            "to": self.node_id,
            "subject": f"📚 {resource_info.get('name', '学习资源')}推送",
            "content": "\n".join(content_lines),
            "dimension": dimension,
            "severity": bottleneck.get("severity", "info"),
            "resources": resources,
            "timestamp": datetime.now().isoformat(),
        }
    
    def send_push(self, message: Dict) -> bool:
        """发送推送消息"""
        try:
            # 保存到from-hermes目录
            msg_file = self.from_hermes_dir / f"{message['tracking_id']}.json"
            msg_file.write_text(json.dumps(message, indent=2, ensure_ascii=False))
            
            # 记录推送历史
            self.push_history["pushes"].append({
                "tracking_id": message["tracking_id"],
                "dimension": message["dimension"],
                "severity": message["severity"],
                "date": datetime.now().strftime('%Y-%m-%d'),
                "timestamp": message["timestamp"],
                "file": str(msg_file),
            })
            self.push_history["total"] = len(self.push_history["pushes"])
            
            self.save_push_history()
            
            print(f"  ✅ 已推送: {message['subject']} -> {self.node_id}")
            return True
        except Exception as e:
            print(f"  ❌ 推送失败: {e}")
            return False
    
    def run_proactive_service(self) -> Dict:
        """执行主动服务"""
        print(f"🔄 主动服务: {self.node_id}")
        
        # 加载NWDAF报告
        report = self.load_nwda_report()
        if not report:
            print(f"  ⚠️ 未找到{self.node_id}的NWDAF报告，跳过")
            return {"status": "no_report", "node_id": self.node_id}
        
        bottlenecks = report.get("bottlenecks", [])
        if not bottlenecks:
            print(f"  ✅ {self.node_id}无瓶颈维度，无需推送")
            return {"status": "no_bottlenecks", "node_id": self.node_id}
        
        print(f"  📊 发现 {len(bottlenecks)} 个瓶颈维度")
        
        pushed_count = 0
        for bottleneck in bottlenecks:
            severity = bottleneck.get("severity", "info")
            
            # 检查配额
            if not self.check_push_quota(severity):
                print(f"  ⏸️ {bottleneck['name']}推送配额已满，跳过")
                continue
            
            # 生成并发送消息
            message = self.generate_push_message(bottleneck)
            if self.send_push(message):
                pushed_count += 1
        
        result = {
            "status": "completed",
            "node_id": self.node_id,
            "bottlenecks_found": len(bottlenecks),
            "pushed": pushed_count,
            "timestamp": datetime.now().isoformat(),
        }
        
        print(f"  📈 推送完成: {pushed_count}/{len(bottlenecks)} 条")
        return result
    
    def get_service_status(self) -> Dict:
        """获取服务状态"""
        return {
            "node_id": self.node_id,
            "total_pushes": self.push_history.get("total", 0),
            "recent_pushes": len(self.push_history.get("pushes", [])),
            "has_nwda_report": self.load_nwda_report() is not None,
            "last_push": self.push_history.get("pushes", [-1])[-1] if self.push_history.get("pushes") else None,
        }


def main():
    if len(sys.argv) < 2:
        print("用法: python3 proactive_service.py <node_id|all>")
        print("示例: python3 proactive_service.py xiaochen")
        print("      python3 proactive_service.py all")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if target == "all":
        nodes = ["xiaochen", "zhuguxia", "qoder"]
        print(f"🔄 批量主动服务 {len(nodes)} 个节点...")
        
        for node in nodes:
            engine = ProactiveServiceEngine(node)
            result = engine.run_proactive_service()
            print()
    else:
        engine = ProactiveServiceEngine(target)
        engine.run_proactive_service()


if __name__ == "__main__":
    main()
