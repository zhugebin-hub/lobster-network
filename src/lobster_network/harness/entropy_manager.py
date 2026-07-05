"""
Entropy Management — 熵管理与文档园丁

模式六: 防止代码库与文档随时间腐化。

核心机制:
1. DocGardener（文档园丁）: 后台 Agent 定期扫描过期文档、检测架构漂移、提交清理 PR
2. DriftDetector（漂移检测器）: 检测代码实际状态与文档描述之间的差距
3. 持续性小额债务偿还: 不追求一次清理干净，而是持续蚕食

铁律落地:
- 每个清理 PR 都必须可 review
- 文档更新与架构变更同步
- 过期文档不能留，要么更新，要么归档

参考: 悟空AI 的文档园丁 Skill 每天扫描 JD 库
"""

import os
import json
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class StaleDocument:
    """过期文档"""
    path: str
    last_modified: str
    days_since_modified: int = 0
    references: List[str] = field(default_factory=list)  # 被哪些文件引用
    content_hash: str = ""
    reason: str = ""  # 过期原因


@dataclass
class DriftReport:
    """漂移报告"""
    component: str                    # 组件名
    doc_description: str             # 文档描述
    actual_state: str                # 实际状态
    drift_severity: str = "low"      # low/medium/high
    action: str = ""                 # 建议操作


class DocGardener:
    """
    文档园丁 — 定期扫描并维护文档健康。

    功能:
    1. 扫描过期文档 (N天未修改)
    2. 检测死引用 (引用了不存在的文件)
    3. 生成清理建议
    4. 输出清理报告
    """

    def __init__(self, root_dir: str, max_age_days: int = 30):
        self.root_dir = Path(root_dir)
        self.max_age_days = max_age_days
        self.scan_results: List[StaleDocument] = []

    def scan_docs(self, pattern: str = "**/*.md") -> List[StaleDocument]:
        """扫描过期文档"""
        stale_docs = []
        tz = timezone(timedelta(hours=8))
        now = datetime.now(tz)

        doc_dir = self.root_dir / "docs"
        if not doc_dir.exists():
            return stale_docs

        for doc_path in doc_dir.glob(pattern):
            # 跳过隐藏文件
            if any(part.startswith('.') for part in doc_path.parts):
                continue

            stat = doc_path.stat()
            mtime = datetime.fromtimestamp(stat.st_mtime, tz=tz)
            age_days = (now - mtime).days

            if age_days >= self.max_age_days:
                stale = StaleDocument(
                    path=str(doc_path.relative_to(self.root_dir)),
                    last_modified=mtime.strftime("%Y-%m-%d"),
                    days_since_modified=age_days,
                    content_hash=str(stat.st_size),  # 简化: 用大小作为hash
                    reason=f"超过 {self.max_age_days} 天未更新",
                )
                stale_docs.append(stale)

        self.scan_results = stale_docs
        return stale_docs

    def find_stale_docs(self) -> List[StaleDocument]:
        """查找超过最大年龄的文档"""
        return self.scan_docs()

    def find_dead_references(self) -> List[StaleDocument]:
        """检测死引用"""
        dead_refs = []
        doc_dir = self.root_dir / "docs"

        if not doc_dir.exists():
            return dead_refs

        for doc_path in doc_dir.glob("**/*.md"):
            try:
                content = doc_path.read_text(encoding='utf-8')
            except Exception:
                continue

            # 查找 markdown 链接
            refs = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            for ref_text, ref_target in refs:
                # 检查本地文件引用
                if not ref_target.startswith('http'):
                    target_path = (doc_path.parent / ref_target).resolve()
                    if not target_path.exists():
                        dead_refs.append(StaleDocument(
                            path=str(doc_path.relative_to(self.root_dir)),
                            last_modified="",
                            reason=f"死引用: [{ref_text}]({ref_target})",
                        ))

        return dead_refs

    def generate_cleanup_plan(self) -> Dict:
        """生成清理计划"""
        stale_docs = self.find_stale_docs()
        dead_refs = self.find_dead_references()

        return {
            "generated_at": datetime.now(timezone(timedelta(hours=8))).isoformat(),
            "stale_documents": [
                {"path": d.path, "age_days": d.days_since_modified, "reason": d.reason}
                for d in stale_docs
            ],
            "dead_references": [
                {"path": d.path, "reason": d.reason}
                for d in dead_refs
            ],
            "suggested_actions": self._suggest_actions(stale_docs, dead_refs),
            "total_stale": len(stale_docs),
            "total_dead_refs": len(dead_refs),
        }

    def _suggest_actions(self, stale_docs: List[StaleDocument],
                         dead_refs: List[StaleDocument]) -> List[str]:
        actions = []

        for d in stale_docs:
            if d.days_since_modified > 90:
                actions.append(f"归档: {d.path} (超过90天未更新)")
            elif d.days_since_modified > 30:
                actions.append(f"审核: {d.path} ({d.days_since_modified}天未更新，确认是否需要保留)")

        for d in dead_refs:
            actions.append(f"修复: {d.path} 中的死引用 ({d.reason})")

        if not actions:
            actions.append("✅ 文档库健康，无需清理")

        return actions

    def archive_stale_doc(self, doc_path: str) -> bool:
        """归档过期文档到 archive/ 目录"""
        full_path = self.root_dir / doc_path
        if not full_path.exists():
            return False

        archive_dir = self.root_dir / "docs" / "archive"
        archive_dir.mkdir(parents=True, exist_ok=True)

        try:
            import shutil
            dest = archive_dir / full_path.name
            shutil.move(str(full_path), str(dest))
            return True
        except Exception:
            return False


class DriftDetector:
    """
    漂移检测器 — 检测文档与代码实际状态的差距。

    这是防止"文档腐化"的关键:
    - 代码更新了，但文档还停留在旧版本
    - README 里的示例代码在新版本中无法运行
    - API 签名变更了，但文档没有同步更新
    """

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)

    def detect_doc_code_drift(self, doc_path: str, code_dir: str) -> DriftReport:
        """
        检测文档中描述的代码与实际代码之间的漂移。

        简单实现: 检查文档中提到的模块/函数是否存在。
        """
        full_doc = self.root_dir / doc_path
        full_code = self.root_dir / code_dir

        if not full_doc.exists():
            return DriftReport(
                component=doc_path,
                doc_description="文档不存在",
                actual_state="N/A",
                drift_severity="high",
                action="创建文档或删除引用",
            )

        try:
            doc_content = full_doc.read_text(encoding='utf-8')
        except Exception:
            return DriftReport(component=doc_path, doc_description="无法读取", actual_state="N/A")

        # 从文档中提取模块引用
        module_refs = re.findall(r'`([a-zA-Z_][a-zA-Z0-9_.]*)`', doc_content)
        missing_modules = []

        for module_ref in module_refs:
            if '.' in module_ref:
                parts = module_ref.split('.')
                # 尝试定位文件
                potential_path = full_code.joinpath(*(parts[:-1])) / f"{parts[-1]}.py"
                if not potential_path.exists():
                    missing_modules.append(module_ref)

        if missing_modules:
            return DriftReport(
                component=doc_path,
                doc_description=f"文档引用 {len(module_refs)} 个模块",
                actual_state=f"其中 {len(missing_modules)} 个已不存在: {', '.join(missing_modules[:5])}",
                drift_severity="medium" if len(missing_modules) < 3 else "high",
                action=f"更新文档，移除或修正这些引用: {', '.join(missing_modules[:3])}...",
            )

        return DriftReport(
            component=doc_path,
            doc_description=f"引用 {len(module_refs)} 个模块",
            actual_state="全部存在",
            drift_severity="low",
        )


class EntropyManager:
    """
    熵管理器 — 综合文档园丁和漂移检测器。

    用法:
        manager = EntropyManager("/path/to/lobster-network")
        manager.run_health_check()  # 运行完整健康检查
        plan = manager.get_cleanup_plan()  # 获取清理计划
        manager.execute_cleanup(plan)  # 执行清理
    """

    def __init__(self, root_dir: str, max_doc_age: int = 30):
        self.root_dir = root_dir
        self.gardener = DocGardener(root_dir, max_age_days=max_doc_age)
        self.detector = DriftDetector(root_dir)
        self.last_check: str = ""
        self.health_report: Dict = {}

    def run_health_check(self) -> Dict:
        """运行完整健康检查"""
        tz = timezone(timedelta(hours=8))
        self.last_check = datetime.now(tz).isoformat()

        # 文档健康
        stale_docs = self.gardener.find_stale_docs()
        dead_refs = self.gardener.find_dead_references()

        # 代码漂移
        drift_reports = []
        docs_dir = Path(self.root_dir) / "docs"
        if docs_dir.exists():
            for doc in docs_dir.glob("*.md"):
                report = self.detector.detect_doc_code_drift(
                    f"docs/{doc.name}",
                    "src/lobster_network"
                )
                if report.drift_severity != "low":
                    drift_reports.append(report)

        self.health_report = {
            "checked_at": self.last_check,
            "document_health": {
                "total_docs": len(list(docs_dir.glob("*.md"))) if docs_dir.exists() else 0,
                "stale_docs": len(stale_docs),
                "dead_references": len(dead_refs),
            },
            "drift_detection": [
                {
                    "component": r.component,
                    "severity": r.drift_severity,
                    "action": r.action,
                }
                for r in drift_reports
            ],
            "overall_health": "good" if len(stale_docs) == 0 and len(drift_reports) == 0 else "needs_attention",
        }

        return self.health_report

    def get_cleanup_plan(self) -> Dict:
        """获取清理计划"""
        return self.gardener.generate_cleanup_plan()

    def execute_cleanup(self, dry_run: bool = True) -> Dict:
        """执行清理"""
        plan = self.gardener.generate_cleanup_plan()
        results = {"dry_run": dry_run, "actions": []}

        if not dry_run:
            for doc in self.gardener.find_stale_docs():
                if doc.days_since_modified > 90:
                    success = self.gardener.archive_stale_doc(doc.path)
                    results["actions"].append({
                        "action": "archive",
                        "path": doc.path,
                        "success": success,
                    })

        return results
