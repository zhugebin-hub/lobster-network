#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一训练提交脚本
解决 P0-问题 2：训练路径不统一

功能：
1. 统一提交到 .shared/training/go/from-{node_id}/
2. 同时保留 docs/training_results/ 作为镜像
3. 自动处理路径、格式验证、git 提交
4. 消除监控误报

作者：信电大虾 (小龙虾网络)
日期：2026-06-30
"""

import json
import os
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# 路径配置（使用自适应路径）
REPO_ROOT = Path(__file__).resolve().parent.parent
SHARED_DIR = REPO_ROOT / ".shared" / "training" / "go"
DOCS_DIR = REPO_ROOT / "docs" / "training_results"


class TrainingSubmitter:
    """训练提交器"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.submit_dir = SHARED_DIR / f"from-{node_id}"
        self.mirror_dir = DOCS_DIR / f"from-{node_id}"
        
        # 确保目录存在
        self.submit_dir.mkdir(parents=True, exist_ok=True)
        self.mirror_dir.mkdir(parents=True, exist_ok=True)
        
    def validate_result(self, result: Dict) -> bool:
        """验证训练结果格式"""
        required_fields = ['node_id', 'day', 'problems', 'games', 'accuracy']
        
        for field in required_fields:
            if field not in result:
                print(f"❌ 缺少必需字段：{field}")
                return False
                
        # 验证数据类型
        if not isinstance(result['problems'], (int, list)):
            print("❌ problems 字段类型错误")
            return False
            
        if not isinstance(result['games'], (int, list)):
            print("❌ games 字段类型错误")
            return False
            
        if not isinstance(result['accuracy'], (int, float)):
            print("❌ accuracy 字段类型错误")
            return False
            
        return True
        
    def submit(self, day: int, results: Dict) -> Dict:
        """提交训练结果"""
        # 添加元数据
        results['node_id'] = self.node_id
        results['day'] = day
        results['submitted_at'] = datetime.now().isoformat()
        results['version'] = '1.0'
        
        # 验证结果
        if not self.validate_result(results):
            return {'status': 'error', 'message': '结果格式验证失败'}
            
        # 生成文件名
        filename = f"day{day}_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # 提交到统一路径
        submit_file = self.submit_dir / filename
        with open(submit_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        # 镜像到 docs 目录
        mirror_file = self.mirror_dir / filename
        with open(mirror_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
            
        print(f"✅ 提交成功：{filename}")
        print(f"   统一路径：{submit_file}")
        print(f"   镜像路径：{mirror_file}")
        
        return {
            'status': 'success',
            'submit_file': str(submit_file),
            'mirror_file': str(mirror_file),
        }
        
    def get_submission_history(self) -> List[Dict]:
        """获取提交历史"""
        history = []
        
        if self.submit_dir.exists():
            for file in sorted(self.submit_dir.glob("*.json")):
                try:
                    with open(file, 'r') as f:
                        data = json.load(f)
                    history.append({
                        'file': file.name,
                        'day': data.get('day'),
                        'submitted_at': data.get('submitted_at'),
                        'accuracy': data.get('accuracy'),
                    })
                except Exception as e:
                    print(f"⚠️ 读取 {file.name} 失败：{e}")
                    
        return history


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='统一训练提交脚本')
    parser.add_argument('--domain', type=str, default='go', help='训练领域（默认：go）')
    parser.add_argument('--day', type=int, required=True, help='训练天数')
    parser.add_argument('--results', type=str, required=True, help='结果文件路径')
    parser.add_argument('--node-id', type=str, required=True, help='节点 ID')
    
    args = parser.parse_args()
    
    # 创建提交器
    submitter = TrainingSubmitter(args.node_id)
    
    # 读取结果文件
    results_file = Path(args.results)
    if not results_file.exists():
        print(f"❌ 结果文件不存在：{results_file}")
        sys.exit(1)
        
    with open(results_file, 'r') as f:
        results = json.load(f)
        
    # 提交结果
    result = submitter.submit(args.day, results)
    
    if result['status'] == 'success':
        print(f"\n📊 提交完成")
        print(f"   节点：{args.node_id}")
        print(f"   天数：Day {args.day}")
        print(f"   准确率：{results.get('accuracy', 'N/A')}")
    else:
        print(f"\n❌ 提交失败：{result.get('message', '未知错误')}")
        sys.exit(1)


if __name__ == "__main__":
    main()
