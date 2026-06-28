#!/usr/bin/env python3
"""
小龙虾网络同步状态管理器 V4.0
统一路径、消息格式、同步状态追踪

功能:
1. 路径验证 - 确保所有节点使用统一路径
2. 消息格式标准化 - JSON格式校验
3. 同步状态追踪 - 实时记录各节点同步状态
4. 自动修复 - 检测并修复常见同步问题
"""
import os
import json
import sys
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

# ========== 统一路径配置 ==========
BASE_DIR = str(Path(__file__).resolve().parent.parent.parent)
SHARED_DIR = f'{BASE_DIR}/.shared'
MESSAGES_DIR = f'{SHARED_DIR}/messages'
TRAINING_DIR = f'{SHARED_DIR}/training'
ROUTING_DIR = f'{MESSAGES_DIR}/routing'

# 标准目录结构
STANDARD_DIRS = {
    'messages': MESSAGES_DIR,
    'routing': ROUTING_DIR,
    'training': TRAINING_DIR,
    'from_hermes': f'{MESSAGES_DIR}/from-hermes',
    'from_xiaochen': f'{MESSAGES_DIR}/from-xiaochen',
    'from_zhuguxia': f'{MESSAGES_DIR}/from-zhuguxia',
    'from_qoder': f'{MESSAGES_DIR}/from-qoder',
    'to_xiaochen': f'{MESSAGES_DIR}/to-xiaochen',
    'to_zhuguxia': f'{MESSAGES_DIR}/to-zhuguxia',
    'to_qoder': f'{MESSAGES_DIR}/to-qoder',
    'results': f'{TRAINING_DIR}/results',
    'queue': f'{MESSAGES_DIR}/queue',
}

# 学员配置
STUDENTS = {
    'xiaochen': {
        'name': '小陈',
        'server': '121.43.80.231',
        'inbox': f'{MESSAGES_DIR}/queue/xiaochen/inbox/',
    },
    'zhuguxia': {
        'name': '诸葛虾',
        'server': '60.205.139.51',
        'inbox': f'{MESSAGES_DIR}/queue/zhuguxia/inbox/',
    },
    'qoder': {
        'name': 'qoder',
        'server': '192.168.1.161',
        'inbox': f'{MESSAGES_DIR}/queue/qoder/inbox/',
    },
}

# 同步状态文件
SYNC_STATUS_FILE = f'{BASE_DIR}/.shared/sync_status.json'


class SyncManager:
    """同步状态管理器"""
    
    def __init__(self):
        self.status = self.load_status()
        self.errors = []
        self.fixes = []
    
    def load_status(self):
        """加载同步状态"""
        if os.path.exists(SYNC_STATUS_FILE):
            try:
                with open(SYNC_STATUS_FILE) as f:
                    return json.load(f)
            except:
                pass
        return {
            'version': '4.0',
            'last_updated': datetime.now().isoformat(),
            'nodes': {},
            'training': {},
            'messages': {},
            'errors': [],
        }
    
    def save_status(self):
        """保存同步状态"""
        self.status['last_updated'] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(SYNC_STATUS_FILE), exist_ok=True)
        with open(SYNC_STATUS_FILE, 'w') as f:
            json.dump(self.status, f, ensure_ascii=False, indent=2)
    
    def verify_paths(self):
        """验证标准目录结构"""
        missing = []
        for name, path in STANDARD_DIRS.items():
            if not os.path.exists(path):
                missing.append((name, path))
        
        if missing:
            print(f"⚠️ 发现 {len(missing)} 个缺失目录:")
            for name, path in missing:
                print(f"  - {name}: {path}")
                try:
                    os.makedirs(path, exist_ok=True)
                    self.fixes.append(f"创建目录: {path}")
                    print(f"  ✅ 已创建: {path}")
                except Exception as e:
                    self.errors.append(f"创建目录失败 {path}: {e}")
                    print(f"  ❌ 创建失败: {e}")
        else:
            print("✅ 所有标准目录存在")
        
        return len(missing) == 0
    
    def validate_message_format(self, filepath):
        """验证消息JSON格式"""
        try:
            with open(filepath) as f:
                data = json.load(f)
            
            # 检查必需字段
            required = ['id', 'from', 'to', 'timestamp', 'message']
            missing = [f for f in required if f not in data]
            
            if missing:
                return False, f"缺少字段: {', '.join(missing)}"
            
            # 验证时间戳格式
            try:
                datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
            except:
                return False, "时间戳格式无效"
            
            return True, "格式正确"
        except json.JSONDecodeError as e:
            return False, f"JSON解析错误: {e}"
        except Exception as e:
            return False, f"验证失败: {e}"
    
    def scan_messages(self):
        """扫描所有消息文件"""
        stats = {
            'total': 0,
            'valid': 0,
            'invalid': 0,
            'errors': []
        }
        
        for dir_name in ['from-hermes', 'from-xiaochen', 'from-zhuguxia', 'from-qoder']:
            dir_path = STANDARD_DIRS.get(dir_name)
            if not dir_path or not os.path.exists(dir_path):
                continue
            
            for fname in os.listdir(dir_path):
                if not fname.endswith('.json'):
                    continue
                
                filepath = os.path.join(dir_path, fname)
                stats['total'] += 1
                
                valid, msg = self.validate_message_format(filepath)
                if valid:
                    stats['valid'] += 1
                else:
                    stats['invalid'] += 1
                    stats['errors'].append(f"{dir_name}/{fname}: {msg}")
        
        print(f"\n📊 消息扫描结果:")
        print(f"  总计: {stats['total']}")
        print(f"  有效: {stats['valid']}")
        print(f"  无效: {stats['invalid']}")
        
        if stats['errors']:
            print(f"  错误详情:")
            for err in stats['errors'][:5]:
                print(f"    - {err}")
        
        return stats
    
    def scan_training_files(self):
        """扫描训练文件"""
        training_stats = {
            'days': {},
            'students': {},
            'files': []
        }
        
        results_dir = STANDARD_DIRS.get('results')
        if not results_dir or not os.path.exists(results_dir):
            return training_stats
        
        for fname in os.listdir(results_dir):
            if not fname.endswith('.json'):
                continue
            
            filepath = os.path.join(results_dir, fname)
            try:
                with open(filepath) as f:
                    data = json.load(f)
                
                # 解析文件名: day3_zhuguxia_20260627.json
                parts = fname.replace('.json', '').split('_')
                if len(parts) >= 2:
                    day = parts[0]
                    student = parts[1]
                    
                    if day not in training_stats['days']:
                        training_stats['days'][day] = []
                    training_stats['days'][day].append(student)
                    
                    if student not in training_stats['students']:
                        training_stats['students'][student] = []
                    training_stats['students'][student].append(day)
                
                training_stats['files'].append({
                    'name': fname,
                    'size': os.path.getsize(filepath),
                    'modified': datetime.fromtimestamp(
                        os.path.getmtime(filepath)
                    ).isoformat()
                })
            except:
                pass
        
        print(f"\n📊 训练文件扫描结果:")
        for day, students in training_stats['days'].items():
            print(f"  {day}: {', '.join(students)}")
        
        return training_stats
    
    def check_node_status(self):
        """检查各节点状态"""
        node_status = {}
        
        for student_id, config in STUDENTS.items():
            status = {
                'name': config['name'],
                'server': config['server'],
                'inbox_exists': False,
                'inbox_files': 0,
                'last_message': None,
            }
            
            inbox = config.get('inbox')
            if inbox and os.path.exists(inbox):
                status['inbox_exists'] = True
                files = [f for f in os.listdir(inbox) if f.endswith('.json')]
                status['inbox_files'] = len(files)
                
                if files:
                    latest = sorted(files)[-1]
                    status['last_message'] = latest
            
            node_status[student_id] = status
            print(f"  {config['name']} ({student_id}):")
            print(f"    服务器: {config['server']}")
            print(f"    Inbox: {'✅ 存在' if status['inbox_exists'] else '❌ 不存在'}")
            print(f"    待处理消息: {status['inbox_files']}")
        
        return node_status
    
    def generate_report(self):
        """生成同步报告"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'version': '4.0',
            'paths_verified': self.verify_paths(),
            'messages': self.scan_messages(),
            'training': self.scan_training_files(),
            'nodes': self.check_node_status(),
            'errors': self.errors,
            'fixes': self.fixes,
        }
        
        # 保存报告
        report_file = f'{BASE_DIR}/.shared/sync_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        os.makedirs(os.path.dirname(report_file), exist_ok=True)
        with open(report_file, 'w') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 报告已保存: {report_file}")
        return report


def main():
    if len(sys.argv) < 2:
        print("小龙虾网络同步管理器 V4.0")
        print("用法:")
        print("  python3 sync_manager.py status    - 查看同步状态")
        print("  python3 sync_manager.py verify    - 验证路径和消息")
        print("  python3 sync_manager.py report    - 生成完整报告")
        print("  python3 sync_manager.py scan      - 扫描所有文件")
        sys.exit(0)
    
    cmd = sys.argv[1]
    manager = SyncManager()
    
    if cmd == 'status':
        node_status = manager.check_node_status()
        print(json.dumps(node_status, ensure_ascii=False, indent=2))
    
    elif cmd == 'verify':
        manager.verify_paths()
        manager.scan_messages()
    
    elif cmd == 'report':
        report = manager.generate_report()
        print(json.dumps(report, ensure_ascii=False, indent=2))
    
    elif cmd == 'scan':
        manager.verify_paths()
        manager.scan_messages()
        manager.scan_training_files()
        manager.check_node_status()
    
    else:
        print(f"未知命令: {cmd}")
        sys.exit(1)


if __name__ == '__main__':
    main()
