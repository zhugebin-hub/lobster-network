#!/usr/bin/env python3
"""
文档园丁
基于 Agent Harness工程实践设计

部署一个后台 Agent 做"文档园丁"：
- 定期扫描过期文档
- 检测架构漂移
- 提交清理 PR
- 持续小额偿还技术债，不要攒到爆雷
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta


class DocGardener:
    """
    文档园丁
    定期扫描、清理、更新文档
    """
    
    def __init__(self, workspace_dir: str = None):
        if workspace_dir is None:
            workspace_dir = os.path.join(os.path.dirname(__file__), "..", "workspace")
        
        self.workspace_dir = Path(workspace_dir)
        self.reports_dir = self.workspace_dir / "reports"
        self.docs_dir = self.workspace_dir / "docs"
        self.garden_log = self.workspace_dir / "garden_log.json"
        
        # 过期时间配置（天）
        self.expiry_config = {
            "reports": 30,      # 报告 30 天过期
            "logs": 7,          # 日志 7 天过期
            "temp": 3,          # 临时文件 3 天过期
            "docs": 90          # 文档 90 天过期
        }
    
    def scan(self) -> Dict:
        """
        扫描文档状态
        
        Returns:
            Dict: 扫描结果
        """
        print("[DocGardener] 开始扫描文档...")
        
        results = {
            "scanned_at": time.time(),
            "total_files": 0,
            "expired_files": [],
            "orphaned_files": [],
            "recommendations": []
        }
        
        # 扫描过期文件
        for dir_name, expiry_days in self.expiry_config.items():
            dir_path = self.workspace_dir / dir_name
            if dir_path.exists():
                expired = self._scan_expired(dir_path, expiry_days)
                results["expired_files"].extend(expired)
                results["total_files"] += len(list(dir_path.rglob("*")))
        
        # 扫描孤立文件（不属于任何目录）
        orphaned = self._scan_orphaned()
        results["orphaned_files"] = orphaned
        
        # 生成建议
        results["recommendations"] = self._generate_recommendations(results)
        
        # 保存扫描结果
        self._save_scan_results(results)
        
        print(f"[DocGardener] 扫描完成，发现 {len(results['expired_files'])} 个过期文件")
        return results
    
    def _scan_expired(self, dir_path: Path, expiry_days: int) -> List[Dict]:
        """扫描过期文件"""
        expired = []
        cutoff_date = datetime.now() - timedelta(days=expiry_days)
        
        for file_path in dir_path.rglob("*"):
            if file_path.is_file():
                # 获取文件修改时间
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if mtime < cutoff_date:
                    expired.append({
                        "path": str(file_path),
                        "modified_at": mtime.isoformat(),
                        "size": file_path.stat().st_size,
                        "days_old": (datetime.now() - mtime).days
                    })
        
        return expired
    
    def _scan_orphaned(self) -> List[str]:
        """扫描孤立文件"""
        orphaned = []
        
        # 检查根目录下的孤立文件
        for file_path in self.workspace_dir.iterdir():
            if file_path.is_file() and file_path.suffix in ['.md', '.txt', '.log']:
                if file_path.name not in ['README.md', 'SOUL.md', 'USER.md', 'AGENTS.md']:
                    orphaned.append(str(file_path))
        
        return orphaned
    
    def _generate_recommendations(self, results: Dict) -> List[str]:
        """生成建议"""
        recommendations = []
        
        expired_count = len(results["expired_files"])
        if expired_count > 10:
            recommendations.append(f"发现 {expired_count} 个过期文件，建议批量清理")
        elif expired_count > 0:
            recommendations.append(f"发现 {expired_count} 个过期文件，建议清理")
        
        orphaned_count = len(results["orphaned_files"])
        if orphaned_count > 0:
            recommendations.append(f"发现 {orphaned_count} 个孤立文件，建议归档或删除")
        
        # 检查磁盘使用
        total_size = sum(f["size"] for f in results["expired_files"])
        if total_size > 100 * 1024 * 1024:  # 100MB
            recommendations.append(f"过期文件总大小 {total_size / 1024 / 1024:.1f}MB，建议清理释放空间")
        
        return recommendations
    
    def cleanup(self, dry_run: bool = True) -> Dict:
        """
        清理过期文件
        
        Args:
            dry_run: 是否仅模拟运行
            
        Returns:
            Dict: 清理结果
        """
        print(f"[DocGardener] {'模拟' if dry_run else '实际'}清理过期文件...")
        
        scan_results = self.scan()
        cleaned = []
        
        for file_info in scan_results["expired_files"]:
            file_path = Path(file_info["path"])
            
            if dry_run:
                action = "would_delete"
            else:
                try:
                    file_path.unlink()
                    action = "deleted"
                except Exception as e:
                    action = f"error: {str(e)}"
            
            cleaned.append({
                "path": file_info["path"],
                "action": action,
                "size": file_info["size"]
            })
        
        result = {
            "cleaned_at": time.time(),
            "dry_run": dry_run,
            "cleaned_files": cleaned,
            "total_freed": sum(c["size"] for c in cleaned if c["action"] == "deleted")
        }
        
        # 保存清理结果
        self._save_cleanup_results(result)
        
        print(f"[DocGardener] 清理完成，{'模拟' if dry_run else '实际'}清理 {len(cleaned)} 个文件")
        return result
    
    def _save_scan_results(self, results: Dict):
        """保存扫描结果"""
        log_file = self.workspace_dir / "garden_scan_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def _save_cleanup_results(self, results: Dict):
        """保存清理结果"""
        log_file = self.workspace_dir / "garden_cleanup_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def get_status(self) -> Dict:
        """获取文档状态"""
        scan_results = self.scan()
        
        return {
            "total_files": scan_results["total_files"],
            "expired_files": len(scan_results["expired_files"]),
            "orphaned_files": len(scan_results["orphaned_files"]),
            "recommendations": scan_results["recommendations"],
            "last_scan": scan_results["scanned_at"]
        }


if __name__ == "__main__":
    # 测试文档园丁
    gardener = DocGardener()
    
    # 扫描
    print("\n=== 扫描文档状态 ===")
    status = gardener.get_status()
    print(f"状态: {json.dumps(status, ensure_ascii=False, indent=2)}")
    
    # 模拟清理
    print("\n=== 模拟清理 ===")
    cleanup_result = gardener.cleanup(dry_run=True)
    print(f"结果: {json.dumps(cleanup_result, ensure_ascii=False, indent=2)}")
    
    # 实际清理（谨慎使用）
    # print("\n=== 实际清理 ===")
    # cleanup_result = gardener.cleanup(dry_run=False)
    # print(f"结果: {json.dumps(cleanup_result, ensure_ascii=False, indent=2)}")
