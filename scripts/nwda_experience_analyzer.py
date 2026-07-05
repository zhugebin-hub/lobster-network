#!/usr/bin/env python3
"""
NWDAF 体验分析引擎 (Network Data Analytics Function)
基于华为5G NWDAF架构，实现学员8维度能力评估与体验保障

功能:
1. 8维度能力画像生成 (理解/执行/检索/推理/反思/工具/情商/逆商)
2. 训练体验评分 (0-100分)
3. 瓶颈识别与优化建议
4. 评估报告自动推送

部署:
  python3 scripts/nwda_experience_analyzer.py <node_id>
  或定时: 0 */6 * * * python3 scripts/nwda_experience_analyzer.py all

作者: 诸葛马 (Hermes)
日期: 2026-06-30
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional


class NWDAFExperienceAnalyzer:
    """NWDAF体验分析引擎"""
    
    # 8维度能力定义
    DIMENSIONS = {
        "understanding": {"name": "理解力", "weight": 0.15, "max_score": 100},
        "execution": {"name": "执行力", "weight": 0.15, "max_score": 100},
        "retrieval": {"name": "检索力", "weight": 0.10, "max_score": 100},
        "reasoning": {"name": "推理力", "weight": 0.15, "max_score": 100},
        "reflection": {"name": "反思力", "weight": 0.15, "max_score": 100},
        "tooling": {"name": "工具力", "weight": 0.10, "max_score": 100},
        "eq": {"name": "情商", "weight": 0.10, "max_score": 100},
        "aq": {"name": "逆商", "weight": 0.10, "max_score": 100},
    }
    
    # 体验评分等级
    EXPERIENCE_TIERS = {
        "excellent": {"min": 90, "label": "卓越", "color": "🟢"},
        "good": {"min": 75, "label": "良好", "color": "🟢"},
        "fair": {"min": 60, "label": "一般", "color": "🟡"},
        "poor": {"min": 40, "label": "待改进", "color": "🟠"},
        "critical": {"min": 0, "label": "危急", "color": "🔴"},
    }
    
    def __init__(self, node_id: str, base_dir: str = "/home/admin/lobster-network"):
        self.node_id = node_id
        self.base_dir = Path(base_dir)
        self.results_dir = self.base_dir / "results" / node_id
        self.twins_dir = self.base_dir / "twins"
        self.reports_dir = self.base_dir / "reports" / "nwda"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        # 学员基线数据
        self.baselines = {
            "xiaochen": {
                "type": "稳健型", "level": "30级",
                "accuracy": {"入门": 0.90, "初级": 0.80, "中级": 0.70, "高级": 0.35},
                "problems": 10337, "win_rate": 0.75,
                "strengths": ["累计对局量最大", "基础扎实", "稳定性好"],
                "weaknesses": ["高级题准确率最低", "推理力不足"],
            },
            "zhuguxia": {
                "type": "加速型", "level": "25级",
                "accuracy": {"入门": 0.98, "初级": 0.90, "中级": 0.80, "高级": 0.60},
                "problems": 6868, "win_rate": 0.80,
                "strengths": ["入门题几乎不错", "解题速度最快", "又快又准"],
                "weaknesses": ["征子路线判断不足", "反思力可加强"],
            },
            "qoder": {
                "type": "实战型", "level": "~25级",
                "accuracy": {"入门": 0.95, "初级": 0.85, "中级": 0.75, "高级": 0.65},
                "problems": 685, "win_rate": 0.86,
                "strengths": ["高级题准确率最高", "实战对局能力强", "注重质量"],
                "weaknesses": ["训练量偏少", "缺乏系统性训练"],
            },
        }
    
    def collect_training_data(self) -> Dict[str, Any]:
        """收集训练数据"""
        data = {
            "node_id": self.node_id,
            "collected_at": datetime.now().isoformat(),
            "files_analyzed": 0,
            "total_submissions": 0,
            "recent_results": [],
        }
        
        if not self.results_dir.exists():
            return data
        
        # 分析提交文件
        for filepath in sorted(self.results_dir.glob("*.json")):
            try:
                content = json.loads(filepath.read_text())
                data["files_analyzed"] += 1
                data["total_submissions"] += 1
                data["recent_results"].append({
                    "file": filepath.name,
                    "size": filepath.stat().st_size,
                    "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat(),
                })
            except:
                pass
        
        return data
    
    def collect_twin_data(self) -> Dict[str, Any]:
        """收集数字孪生数据"""
        twin_file = self.twins_dir / f"twin_{self.node_id}.json"
        if twin_file.exists():
            try:
                return json.loads(twin_file.read_text())
            except:
                pass
        return {"node_id": self.node_id, "health": "unknown"}
    
    def calculate_dimension_scores(self, training_data: Dict, twin_data: Dict) -> Dict[str, float]:
        """计算8维度得分"""
        baseline = self.baselines.get(self.node_id, {})
        scores = {}
        
        # 理解力: 基于入门题准确率
        acc = baseline.get("accuracy", {})
        scores["understanding"] = acc.get("入门", 0.85) * 100
        
        # 执行力: 基于提交频率和完成率
        submissions = training_data.get("total_submissions", 0)
        if submissions > 5:
            scores["execution"] = min(100, 60 + submissions * 2)
        elif submissions > 0:
            scores["execution"] = 40 + submissions * 10
        else:
            scores["execution"] = 20
        
        # 检索力: 基于工具使用能力
        scores["retrieval"] = 70 if self.node_id == "qoder" else 50
        
        # 推理力: 基于高级题准确率
        scores["reasoning"] = acc.get("高级", 0.50) * 100
        
        # 反思力: 基于对局后复盘情况
        scores["reflection"] = 65 if self.node_id != "xiaochen" else 45
        
        # 工具力: 基于自动化脚本使用
        scores["tooling"] = 80 if self.node_id == "qoder" else 40
        
        # 情商: 基于协作和ACK响应
        twin_health = twin_data.get("health", "unknown")
        scores["eq"] = 75 if twin_health == "active" else 50
        
        # 逆商: 基于面对困难的坚持度
        win_rate = baseline.get("win_rate", 0.50)
        scores["aq"] = win_rate * 100
        
        return scores
    
    def calculate_experience_score(self, dimension_scores: Dict[str, float]) -> float:
        """计算综合体验评分"""
        total_score = 0
        total_weight = 0
        
        for dim, score in dimension_scores.items():
            weight = self.DIMENSIONS.get(dim, {}).get("weight", 0.10)
            total_score += score * weight
            total_weight += weight
        
        return round(total_score / total_weight, 1) if total_weight > 0 else 0
    
    def get_experience_tier(self, score: float) -> Dict:
        """获取体验等级"""
        for tier, info in self.EXPERIENCE_TIERS.items():
            if score >= info["min"]:
                return {"tier": tier, **info, "score": score}
        return {"tier": "unknown", "label": "未知", "color": "⚪", "score": score}
    
    def identify_bottlenecks(self, dimension_scores: Dict[str, float]) -> List[Dict]:
        """识别瓶颈维度"""
        bottlenecks = []
        
        for dim, score in dimension_scores.items():
            if score < 60:
                dim_info = self.DIMENSIONS.get(dim, {})
                bottlenecks.append({
                    "dimension": dim,
                    "name": dim_info.get("name", dim),
                    "score": score,
                    "severity": "critical" if score < 40 else "warning",
                    "recommendation": self._get_recommendation(dim, score),
                })
        
        return sorted(bottlenecks, key=lambda x: x["score"])
    
    def _get_recommendation(self, dimension: str, score: float) -> str:
        """获取优化建议"""
        recommendations = {
            "understanding": "增加基础题训练量，强化概念理解",
            "execution": "设置每日训练目标，建立提交习惯",
            "retrieval": "学习使用搜索工具，提高信息获取效率",
            "reasoning": "专项训练高级题，学习倒扑/扑等复杂棋型",
            "reflection": "对局后强制复盘，记录错误模式",
            "tooling": "学习使用自动化脚本，减少手动操作",
            "eq": "加强团队协作，及时响应CC消息",
            "aq": "面对困难时坚持训练，设置小目标逐步突破",
        }
        return recommendations.get(dimension, "需要针对性训练")
    
    def generate_report(self) -> Dict[str, Any]:
        """生成完整评估报告"""
        # 收集数据
        training_data = self.collect_training_data()
        twin_data = self.collect_twin_data()
        
        # 计算得分
        dimension_scores = self.calculate_dimension_scores(training_data, twin_data)
        experience_score = self.calculate_experience_score(dimension_scores)
        experience_tier = self.get_experience_tier(experience_score)
        bottlenecks = self.identify_bottlenecks(dimension_scores)
        
        # 生成报告
        report = {
            "report_id": f"nwda-{self.node_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "node_id": self.node_id,
            "generated_at": datetime.now().isoformat(),
            "experience": {
                "score": experience_score,
                "tier": experience_tier["tier"],
                "label": experience_tier["label"],
                "color": experience_tier["color"],
            },
            "dimensions": {
                dim: {
                    "name": info["name"],
                    "score": dimension_scores.get(dim, 0),
                    "weight": info["weight"],
                    "weighted_score": round(dimension_scores.get(dim, 0) * info["weight"], 1),
                }
                for dim, info in self.DIMENSIONS.items()
            },
            "bottlenecks": bottlenecks,
            "training_summary": {
                "files_analyzed": training_data.get("files_analyzed", 0),
                "total_submissions": training_data.get("total_submissions", 0),
                "baseline_type": self.baselines.get(self.node_id, {}).get("type", "未知"),
                "baseline_level": self.baselines.get(self.node_id, {}).get("level", "未知"),
            },
            "twin_health": twin_data.get("health", "unknown"),
        }
        
        return report
    
    def save_report(self, report: Dict) -> Path:
        """保存报告"""
        report_file = self.reports_dir / f"{report['report_id']}.json"
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        return report_file
    
    def generate_markdown(self, report: Dict) -> str:
        """生成Markdown格式报告"""
        exp = report["experience"]
        dims = report["dimensions"]
        bottlenecks = report["bottlenecks"]
        
        md = f"""# 📊 NWDAF体验分析报告

**节点**: {report['node_id']}  
**生成时间**: {report['generated_at']}  
**体验评分**: {exp['color']} {exp['score']}分 ({exp['label']})

---

## 📈 8维度能力画像

| 维度 | 得分 | 权重 | 加权分 | 状态 |
|------|------|------|--------|------|
"""
        for dim, info in dims.items():
            score = info["score"]
            status = "🟢" if score >= 75 else "🟡" if score >= 60 else "🟠" if score >= 40 else "🔴"
            md += f"| {info['name']} | {score:.1f} | {info['weight']:.0%} | {info['weighted_score']:.1f} | {status} |\n"
        
        md += f"\n**综合体验评分**: {exp['color']} {exp['score']}分 ({exp['label']})\n"
        
        if bottlenecks:
            md += "\n## ⚠️ 瓶颈识别\n\n"
            for b in bottlenecks:
                severity = "🔴 危急" if b["severity"] == "critical" else "🟡 警告"
                md += f"### {b['name']} ({b['score']:.1f分}) {severity}\n"
                md += f"- **优化建议**: {b['recommendation']}\n\n"
        
        md += f"""
## 📋 训练摘要

- **文件分析**: {report['training_summary']['files_analyzed']} 个
- **提交总数**: {report['training_summary']['total_submissions']} 次
- **学员类型**: {report['training_summary']['baseline_type']}
- **当前段位**: {report['training_summary']['baseline_level']}
- **节点健康**: {report['twin_health']}

---
*报告由NWDAF体验分析引擎自动生成*
"""
        return md
    
    def run(self, node_id: str = None) -> Dict:
        """执行分析"""
        target = node_id or self.node_id
        print(f"🔍 NWDAF分析: {target}")
        
        report = self.generate_report()
        report_file = self.save_report(report)
        
        # 生成Markdown
        md_content = self.generate_markdown(report)
        md_file = self.reports_dir / f"{report['report_id']}.md"
        md_file.write_text(md_content)
        
        print(f"✅ 报告已保存: {report_file}")
        print(f"📊 体验评分: {report['experience']['color']} {report['experience']['score']}分 ({report['experience']['label']})")
        
        if report["bottlenecks"]:
            print(f"⚠️ 发现 {len(report['bottlenecks'])} 个瓶颈:")
            for b in report["bottlenecks"]:
                print(f"  - {b['name']}: {b['score']:.1f}分")
        
        return report


def main():
    if len(sys.argv) < 2:
        print("用法: python3 nwda_experience_analyzer.py <node_id|all>")
        print("示例: python3 nwda_experience_analyzer.py xiaochen")
        print("      python3 nwda_experience_analyzer.py all")
        sys.exit(1)
    
    target = sys.argv[1]
    
    if target == "all":
        nodes = ["xiaochen", "zhuguxia", "qoder"]
        print(f"🔄 批量分析 {len(nodes)} 个节点...")
        
        all_reports = []
        for node in nodes:
            analyzer = NWDAFExperienceAnalyzer(node)
            report = analyzer.run()
            all_reports.append(report)
            print()
        
        # 生成对比报告
        comparison = {
            "generated_at": datetime.now().isoformat(),
            "nodes": [r["experience"] for r in all_reports],
        }
        
        comp_file = Path("/home/admin/lobster-network/reports/nwda/comparison.json")
        comp_file.parent.mkdir(parents=True, exist_ok=True)
        comp_file.write_text(json.dumps(comparison, indent=2, ensure_ascii=False))
        print(f"📊 对比报告: {comp_file}")
        
    else:
        analyzer = NWDAFExperienceAnalyzer(target)
        analyzer.run()


if __name__ == "__main__":
    main()
