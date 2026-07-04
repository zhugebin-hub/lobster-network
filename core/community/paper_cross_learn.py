#!/usr/bin/env python3
"""
跨域学习整合脚本 - 论文撰写域扩展
Paper Writing Cross-Domain Learning Integration Script

将围棋域、海报域的学习经验迁移到论文撰写域，
并反向输出论文域的结构化思维到其他域。
"""

import json
import os
from datetime import datetime
from pathlib import Path

# ============================================================
# 域注册表
# ============================================================
DOMAINS = {
    "go": {
        "name": "围棋域",
        "registry_path": "registry/nodes",
        "active_nodes": ["qoder", "xiaochen", "zhuguxia"],
    },
    "poster": {
        "name": "海报域",
        "registry_path": "registry/nodes",
        "active_nodes": ["qoder", "xiaochen", "zhuguxia"],
    },
    "paper": {
        "name": "论文撰写域",
        "registry_path": "registry/nodes",
        "active_nodes": ["qoder", "xiaochen", "zhuguxia", "zhugebin"],
    },
}

# ============================================================
# 跨域迁移映射
# ============================================================
TRANSFER_MAP = {
    "go_to_paper": {
        "source": "go",
        "target": "paper",
        "label": "围棋 → 论文",
        "transfers": [
            {
                "source_skill": "spaced repetition (间隔重复)",
                "target_skill": "iterative revision (迭代修改)",
                "description": "围棋中的间隔复习策略迁移到论文的反复修改流程",
            },
            {
                "source_skill": "game review (复盘)",
                "target_skill": "paper peer review (论文同行评审)",
                "description": "围棋复盘的系统化方法迁移到论文评审流程",
            },
            {
                "source_skill": "nine-dan levels (九段等级)",
                "target_skill": "paper skill levels (论文技能等级)",
                "description": "围棋段位体系迁移到论文写作能力分级评估",
            },
        ],
    },
    "poster_to_paper": {
        "source": "poster",
        "target": "paper",
        "label": "海报 → 论文",
        "transfers": [
            {
                "source_skill": "HTML pipeline (HTML管线)",
                "target_skill": "LaTeX pipeline (LaTeX管线)",
                "description": "海报域的HTML自动化管线经验迁移到LaTeX排版管线",
            },
            {
                "source_skill": "visual hierarchy (视觉层次)",
                "target_skill": "information hierarchy (信息层次)",
                "description": "海报设计中的视觉层次迁移到论文的信息组织结构",
            },
        ],
    },
    "paper_to_go": {
        "source": "paper",
        "target": "go",
        "label": "论文 → 围棋",
        "transfers": [
            {
                "source_skill": "structured argumentation (结构化论证)",
                "target_skill": "game strategy documentation (棋局策略文档化)",
                "description": "论文的结构化论证方法迁移到围棋策略的系统记录",
            },
            {
                "source_skill": "citation management (引用管理)",
                "target_skill": "opening book management (定式库管理)",
                "description": "论文的引用管理体系迁移到围棋定式的分类管理",
            },
        ],
    },
    "paper_to_poster": {
        "source": "paper",
        "target": "poster",
        "label": "论文 → 海报",
        "transfers": [
            {
                "source_skill": "academic formatting (学术排版)",
                "target_skill": "design formatting (设计排版)",
                "description": "论文的学术排版规范迁移到海报的设计排版标准",
            },
            {
                "source_skill": "IMRaD structure (IMRaD结构)",
                "target_skill": "poster layout structure (海报布局结构)",
                "description": "论文的IMRaD结构思维迁移到海报的信息布局规划",
            },
        ],
    },
}

# ============================================================
# 项目根目录
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def log(message):
    """带时间戳的日志输出。"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] [paper_cross_learn] {message}")


def load_domain_stats(domain_key):
    """
    加载指定域的节点统计数据。

    读取该域注册目录下所有 *-paper.json 文件，
    返回 {node_id: paper_writing_dimensions} 的字典。
    """
    if domain_key not in DOMAINS:
        log(f"警告: 未知域 '{domain_key}'，可用域: {list(DOMAINS.keys())}")
        return {}

    registry_dir = PROJECT_ROOT / DOMAINS[domain_key]["registry_path"]
    stats = {}

    if not registry_dir.exists():
        log(f"注册目录不存在: {registry_dir}")
        return stats

    for json_file in sorted(registry_dir.glob("*-paper.json")):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                node = json.load(f)
            node_id = node.get("node_id", json_file.stem)
            pw = node.get("paper_writing", {})
            stats[node_id] = {
                "name": node.get("name", node_id),
                "type": node.get("type", "unknown"),
                "status": node.get("status", "unknown"),
                "current_level": pw.get("current_level", 0),
                "target_level": pw.get("target_level", 0),
                "dimensions": pw.get("dimensions", {}),
                "specialty": pw.get("specialty", "none"),
            }
        except (json.JSONDecodeError, IOError) as e:
            log(f"读取 {json_file} 失败: {e}")

    log(f"域 '{domain_key}' 加载了 {len(stats)} 个节点")
    return stats


def generate_transfer_report(month, year):
    """
    生成跨域迁移报告。

    遍历 TRANSFER_MAP，汇总每个迁移方向的技能条目数、
    涉及的源域/目标域节点数量，输出结构化报告。
    """
    log(f"=== 跨域迁移报告 {year}年{month}月 ===")
    report_lines = []
    report_lines.append(f"# 跨域迁移报告 — {year}年{month}月")
    report_lines.append("")

    total_transfers = 0

    for key, mapping in TRANSFER_MAP.items():
        source_stats = load_domain_stats(mapping["source"])
        target_stats = load_domain_stats(mapping["target"])
        transfer_count = len(mapping["transfers"])
        total_transfers += transfer_count

        report_lines.append(f"## {mapping['label']}")
        report_lines.append(f"- 迁移条目数: {transfer_count}")
        report_lines.append(f"- 源域节点数: {len(source_stats)}")
        report_lines.append(f"- 目标域节点数: {len(target_stats)}")
        report_lines.append("")

        for t in mapping["transfers"]:
            report_lines.append(f"  - **{t['source_skill']}** → **{t['target_skill']}**")
            report_lines.append(f"    {t['description']}")
        report_lines.append("")

    report_lines.append(f"---")
    report_lines.append(f"**迁移方向总数**: {len(TRANSFER_MAP)}")
    report_lines.append(f"**迁移条目总计**: {total_transfers}")

    report_text = "\n".join(report_lines)
    log(f"报告生成完毕，共 {len(TRANSFER_MAP)} 个迁移方向，{total_transfers} 条迁移")
    return report_text


def run_cross_domain(month_number, year_number):
    """
    执行一次跨域学习整合。

    1. 加载所有域的节点统计
    2. 计算各节点维度的平均值与短板
    3. 生成跨域迁移报告
    4. 将报告写入 outputs 目录
    """
    log(f"开始跨域整合: {year_number}年{month_number}月")

    # --- 加载所有域 ---
    all_stats = {}
    for domain_key in DOMAINS:
        all_stats[domain_key] = load_domain_stats(domain_key)

    # --- 维度汇总 ---
    log("--- 论文域节点维度汇总 ---")
    paper_stats = all_stats.get("paper", {})
    for node_id, info in paper_stats.items():
        dims = info.get("dimensions", {})
        if dims:
            avg = sum(dims.values()) / len(dims)
            weakest = min(dims, key=dims.get)
            strongest = max(dims, key=dims.get)
            log(
                f"  {info['name']} | 均分: {avg:.1f} | "
                f"最强: {strongest}({dims[strongest]}) | "
                f"最弱: {weakest}({dims[weakest]})"
            )

    # --- 生成报告 ---
    report = generate_transfer_report(month_number, year_number)

    # --- 写出报告 ---
    output_dir = PROJECT_ROOT / "outputs"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / f"cross_domain_report_{year_number}_{month_number:02d}.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    log(f"报告已写入: {report_path}")

    return report


def main():
    """入口函数：使用当前月份执行跨域整合。"""
    now = datetime.now()
    log("小龙虾网络 · 论文撰写域 · 跨域学习整合启动")
    run_cross_domain(now.month, now.year)
    log("整合完成")


if __name__ == "__main__":
    main()
