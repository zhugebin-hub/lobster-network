#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
科学智能体任务调度器

负责将食物过敏药物研制任务分发给各节点的科学智能体，
协调多节点并行研究，并汇总研究结果。

节点分工：
- qoder: 化合物设计 + 虚拟筛选
- xiaochen: 靶点发现 + 文献挖掘
- zhuguxia: ADMET预测 + 毒性评估
- hermes: 全局协调 + 假设验证 + 质量把控
- zhugema: 任务路由 + 进度监控
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("science_dispatcher")
logger.setLevel(logging.INFO)


# ============================================================
# 研究计划模板
# ============================================================

RESEARCH_PLAN = {
    "topic": "食物过敏防治药物研制",
    "stages": [
        {
            "id": 1,
            "name": "靶点发现与验证",
            "description": "识别食物过敏相关靶点蛋白，进行表位映射与假设生成",
            "agents": ["allergen-target-agent"],
            "node": "xiaochen",
            "inputs": ["allergen_database", "epitope_data"],
            "outputs": ["target_list", "hypothesis_report"],
            "status": "pending",
        },
        {
            "id": 2,
            "name": "文献调研与知识整合",
            "description": "挖掘食物过敏领域文献，提取关键知识与研究趋势",
            "agents": ["literature-mining-agent"],
            "node": "xiaochen",
            "inputs": ["pubmed_query", "patent_data"],
            "outputs": ["knowledge_graph", "trend_report"],
            "status": "pending",
        },
        {
            "id": 3,
            "name": "化合物设计与优化",
            "description": "基于靶点结构设计候选化合物，进行先导化合物优化",
            "agents": ["compound-design-agent"],
            "node": "qoder",
            "inputs": ["target_list", "knowledge_graph"],
            "outputs": ["compound_library", "lead_candidates"],
            "status": "pending",
        },
        {
            "id": 4,
            "name": "虚拟筛选与分子对接",
            "description": "对候选化合物进行高通量虚拟筛选和分子对接评分排序",
            "agents": ["virtual-screening-agent"],
            "node": "qoder",
            "inputs": ["compound_library", "target_structures"],
            "outputs": ["screening_results", "hit_ranking"],
            "status": "pending",
        },
        {
            "id": 5,
            "name": "ADMET性质预测",
            "description": "预测候选化合物的吸收、分布、代谢、排泄及毒性性质",
            "agents": ["admet-prediction-agent"],
            "node": "zhuguxia",
            "inputs": ["hit_ranking", "compound_structures"],
            "outputs": ["admet_profiles", "drug_likeness_scores"],
            "status": "pending",
        },
        {
            "id": 6,
            "name": "毒性评估与安全分析",
            "description": "对优选化合物进行毒性评估，包括hERG预测和脱靶效应分析",
            "agents": ["toxicity-assessment-agent"],
            "node": "zhuguxia",
            "inputs": ["admet_profiles", "lead_candidates"],
            "outputs": ["safety_report", "risk_assessment"],
            "status": "pending",
        },
    ],
    "coordinator": "hermes",
    "router": "zhugema",
}


# ============================================================
# 节点-智能体映射
# ============================================================

NODE_AGENT_MAP = {
    "qoder": {
        "agents": ["compound-design-agent", "virtual-screening-agent"],
        "specialization": "compound_design_and_screening",
        "role": "lead_researcher",
    },
    "xiaochen": {
        "agents": ["allergen-target-agent", "literature-mining-agent"],
        "specialization": "target_discovery_and_literature",
        "role": "researcher",
    },
    "zhuguxia": {
        "agents": ["admet-prediction-agent", "toxicity-assessment-agent"],
        "specialization": "safety_and_admet_evaluation",
        "role": "researcher",
    },
    "hermes": {
        "agents": [],
        "specialization": "global_coordination_and_quality_control",
        "role": "coordinator",
    },
    "zhugema": {
        "agents": [],
        "specialization": "task_routing_and_progress_monitoring",
        "role": "router",
    },
}


class ScienceDispatcher:
    """
    科学智能体任务调度器。

    负责将药物研制任务分发给各节点的科学智能体，
    协调多节点并行研究，并汇总研究结果。
    """

    def __init__(self, shared_path: str):
        """
        初始化科学调度器。

        Args:
            shared_path: .shared 目录路径
        """
        self.shared_path = Path(shared_path)
        self.output_dir = self.shared_path / "science_outputs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.task_log: List[Dict[str, Any]] = []
        self.node_results: Dict[str, Dict[str, Any]] = {}
        self.research_plan = json.loads(json.dumps(RESEARCH_PLAN))  # deep copy
        self.created_at = datetime.now().isoformat()

        logger.info(f"ScienceDispatcher 初始化 | shared_path={self.shared_path}")
        logger.info(f"输出目录: {self.output_dir}")

    def dispatch_research_task(
        self,
        task_name: str,
        description: str,
        target_nodes: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        分发科学研究任务到各节点。

        Args:
            task_name: 任务名称
            description: 任务描述
            target_nodes: 目标节点列表，None 表示所有节点

        Returns:
            分发结果摘要
        """
        if target_nodes is None:
            target_nodes = list(NODE_AGENT_MAP.keys())

        dispatch_record = {
            "task_name": task_name,
            "description": description,
            "dispatched_at": datetime.now().isoformat(),
            "target_nodes": target_nodes,
            "node_messages": {},
        }

        for node_id in target_nodes:
            node_config = NODE_AGENT_MAP.get(node_id)
            if not node_config:
                logger.warning(f"未知节点: {node_id}，跳过")
                continue

            message = {
                "msg_type": "science_task",
                "from": "science_dispatcher",
                "to": node_id,
                "task_name": task_name,
                "description": description,
                "assigned_agents": node_config["agents"],
                "specialization": node_config["specialization"],
                "role": node_config["role"],
                "timestamp": datetime.now().isoformat(),
            }
            dispatch_record["node_messages"][node_id] = message

            # 写入节点任务文件
            node_task_dir = self.output_dir / node_id
            node_task_dir.mkdir(parents=True, exist_ok=True)
            task_file = node_task_dir / f"task_{task_name.replace(' ', '_')}.json"
            task_file.write_text(json.dumps(message, ensure_ascii=False, indent=2), encoding="utf-8")

            logger.info(f"任务已分发到 [{node_id}] -> agents: {node_config['agents']}")

        self.task_log.append(dispatch_record)
        logger.info(f"任务 [{task_name}] 分发完成，目标节点: {target_nodes}")
        return dispatch_record

    def assign_agents_to_nodes(self) -> Dict[str, List[str]]:
        """
        根据节点配置文件将科学智能体映射到各节点。

        Returns:
            {node_id: [agent_ids]} 映射关系
        """
        assignments = {}
        profiles_dir = self.shared_path / "profiles"

        for node_id, node_config in NODE_AGENT_MAP.items():
            profile_file = profiles_dir / f"{node_id}.json"
            assigned_agents = node_config["agents"]

            if profile_file.exists():
                try:
                    profile = json.loads(profile_file.read_text(encoding="utf-8"))
                    drug_domain = profile.get("domains", {}).get("drug_discovery", {})
                    profile_agents = drug_domain.get("agents_assigned", [])
                    # 合并配置中的 agent 和 profile 中的 agent
                    merged = list(set(assigned_agents + profile_agents))
                    assignments[node_id] = merged
                    logger.info(
                        f"节点 [{node_id}] 智能体分配: config={assigned_agents} "
                        f"profile={profile_agents} merged={merged}"
                    )
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"读取 profile [{node_id}] 失败: {e}，使用默认配置")
                    assignments[node_id] = assigned_agents
            else:
                assignments[node_id] = assigned_agents
                logger.info(f"节点 [{node_id}] 无 profile 文件，使用默认配置: {assigned_agents}")

        return assignments

    def create_research_plan(self, topic: str = "food_allergy_drug_discovery") -> Dict[str, Any]:
        """
        创建结构化研究计划。

        Args:
            topic: 研究主题

        Returns:
            完整的研究计划
        """
        plan = {
            "topic": RESEARCH_PLAN["topic"],
            "topic_key": topic,
            "created_at": datetime.now().isoformat(),
            "stages": [],
            "coordinator": RESEARCH_PLAN["coordinator"],
            "router": RESEARCH_PLAN["router"],
            "dependencies": [],
        }

        for stage in RESEARCH_PLAN["stages"]:
            stage_entry = {
                "id": stage["id"],
                "name": stage["name"],
                "description": stage["description"],
                "agents": stage["agents"],
                "node": stage["node"],
                "status": "pending",
                "progress_pct": 0.0,
                "started_at": None,
                "completed_at": None,
            }
            plan["stages"].append(stage_entry)

            # 定义阶段依赖：每个阶段依赖前一阶段完成
            if stage["id"] > 1:
                plan["dependencies"].append({
                    "from_stage": stage["id"] - 1,
                    "to_stage": stage["id"],
                    "type": "sequential",
                })

        # 保存研究计划
        plan_file = self.output_dir / "research_plan.json"
        plan_file.write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"研究计划已创建: {plan_file}")

        return plan

    def collect_results(self, node_id: str) -> Dict[str, Any]:
        """
        收集指定节点的研究结果。

        Args:
            node_id: 节点 ID

        Returns:
            节点结果汇总
        """
        node_output_dir = self.output_dir / node_id
        results = {
            "node_id": node_id,
            "collected_at": datetime.now().isoformat(),
            "tasks": [],
            "status": "no_data",
        }

        if not node_output_dir.exists():
            logger.info(f"节点 [{node_id}] 无输出目录")
            return results

        task_files = list(node_output_dir.glob("task_*.json"))
        for tf in task_files:
            try:
                task_data = json.loads(tf.read_text(encoding="utf-8"))
                results["tasks"].append({
                    "file": tf.name,
                    "task_name": task_data.get("task_name", "unknown"),
                    "status": task_data.get("status", "pending"),
                })
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"读取任务文件失败 [{tf}]: {e}")

        if results["tasks"]:
            results["status"] = "collected"

        self.node_results[node_id] = results
        logger.info(f"节点 [{node_id}] 结果已收集: {len(results['tasks'])} 个任务")
        return results

    def generate_progress_report(self) -> Dict[str, Any]:
        """
        生成整体研究进度报告。

        Returns:
            进度报告字典
        """
        report = {
            "report_type": "science_progress",
            "generated_at": datetime.now().isoformat(),
            "topic": RESEARCH_PLAN["topic"],
            "overall_progress": {},
            "node_status": {},
            "stage_status": [],
        }

        # 各阶段状态
        total_stages = len(self.research_plan.get("stages", RESEARCH_PLAN["stages"]))
        completed_stages = 0
        for stage in RESEARCH_PLAN["stages"]:
            stage_info = {
                "id": stage["id"],
                "name": stage["name"],
                "node": stage["node"],
                "agents": stage["agents"],
                "status": stage.get("status", "pending"),
            }
            report["stage_status"].append(stage_info)
            if stage.get("status") == "completed":
                completed_stages += 1

        report["overall_progress"] = {
            "total_stages": total_stages,
            "completed_stages": completed_stages,
            "progress_pct": round(completed_stages / max(total_stages, 1) * 100, 1),
            "total_tasks_dispatched": len(self.task_log),
        }

        # 各节点状态
        for node_id in NODE_AGENT_MAP:
            node_dir = self.output_dir / node_id
            task_count = len(list(node_dir.glob("task_*.json"))) if node_dir.exists() else 0
            result_data = self.node_results.get(node_id, {})
            report["node_status"][node_id] = {
                "agents": NODE_AGENT_MAP[node_id]["agents"],
                "role": NODE_AGENT_MAP[node_id]["role"],
                "tasks_dispatched": task_count,
                "results_collected": result_data.get("status", "no_data"),
            }

        # 保存报告
        report_file = self.output_dir / "progress_report.json"
        report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"进度报告已生成: {report_file}")

        return report

    def broadcast_research_start(self, topic: str, all_nodes: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        向所有节点广播研究启动消息（SCIENCE_HELLO）。

        Args:
            topic: 研究主题
            all_nodes: 所有节点列表，None 表示使用默认全部节点

        Returns:
            广播结果
        """
        if all_nodes is None:
            all_nodes = list(NODE_AGENT_MAP.keys())

        broadcast = {
            "msg_type": "SCIENCE_HELLO",
            "protocol": "OADP-Science",
            "from": "hermes",
            "topic": topic,
            "topic_display": RESEARCH_PLAN["topic"],
            "timestamp": datetime.now().isoformat(),
            "to_nodes": all_nodes,
            "message": (
                f"科学研究项目 [{RESEARCH_PLAN['topic']}] 已启动。"
                f"共 {len(RESEARCH_PLAN['stages'])} 个研究阶段，"
                f"涉及 {len(all_nodes)} 个节点协同工作。"
                f"请各节点确认就绪。"
            ),
            "ack_deadline_hours": 24,
            "tracking_id": f"science-hello-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        }

        # 写入广播文件
        broadcast_file = self.output_dir / "science_hello.json"
        broadcast_file.write_text(json.dumps(broadcast, ensure_ascii=False, indent=2), encoding="utf-8")

        logger.info(f"SCIENCE_HELLO 广播已发送 | topic={topic} | nodes={all_nodes}")
        return broadcast


# ============================================================
# 主函数
# ============================================================

def main():
    """初始化科学调度器并演示研究流程。"""
    # 定位 .shared 目录
    base_path = Path(__file__).resolve().parent.parent.parent
    shared_path = base_path / ".shared"

    print("=" * 60)
    print("  科学智能体任务调度器 - 食物过敏防治药物研制")
    print("=" * 60)
    print()

    # 1. 初始化调度器
    dispatcher = ScienceDispatcher(str(shared_path))
    print(f"[OK] 调度器初始化完成")
    print(f"     共享路径: {shared_path}")
    print(f"     输出目录: {dispatcher.output_dir}")
    print()

    # 2. 创建研究计划
    plan = dispatcher.create_research_plan("food_allergy_drug_discovery")
    print(f"[OK] 研究计划已创建")
    print(f"     主题: {plan['topic']}")
    print(f"     阶段数: {len(plan['stages'])}")
    print(f"     协调节点: {plan['coordinator']}")
    print(f"     路由节点: {plan['router']}")
    print()

    # 打印研究阶段
    print("研究阶段：")
    print("-" * 50)
    for stage in plan["stages"]:
        print(f"  [{stage['id']}] {stage['name']}")
        print(f"      节点: {stage['node']}  智能体: {stage['agents']}")
    print()

    # 3. 分配智能体到节点
    assignments = dispatcher.assign_agents_to_nodes()
    print(f"[OK] 智能体分配完成")
    for node_id, agents in assignments.items():
        role = NODE_AGENT_MAP[node_id]["role"]
        print(f"     {node_id} ({role}): {agents}")
    print()

    # 4. 广播研究启动
    broadcast = dispatcher.broadcast_research_start("food_allergy_drug_discovery")
    print(f"[OK] SCIENCE_HELLO 已广播")
    print(f"     目标节点: {broadcast['to_nodes']}")
    print(f"     追踪 ID: {broadcast['tracking_id']}")
    print()

    # 5. 分发示例任务
    dispatch_result = dispatcher.dispatch_research_task(
        task_name="initial_setup",
        description="初始化各节点科学研究环境，确认智能体就绪",
        target_nodes=["qoder", "xiaochen", "zhuguxia"],
    )
    print(f"[OK] 初始任务已分发")
    for node_id in dispatch_result["node_messages"]:
        print(f"     -> {node_id}")
    print()

    # 6. 生成进度报告
    report = dispatcher.generate_progress_report()
    print(f"[OK] 进度报告已生成")
    print(f"     总阶段: {report['overall_progress']['total_stages']}")
    print(f"     进度: {report['overall_progress']['progress_pct']}%")
    print()

    print("=" * 60)
    print("  食物过敏防治药物研制项目已就绪，等待各节点确认。")
    print("=" * 60)


if __name__ == "__main__":
    main()
