#!/usr/bin/env python3
"""
V4.0 Phase 3 编排器 (Business Intelligence Orchestrator)
协调NWDAF体验分析、主动服务、知识沉淀、跨领域联动

功能:
1. 统一调度Phase 3所有组件
2. 数据流编排 (分析→服务→沉淀→联动)
3. 定时任务管理
4. 执行报告生成

部署:
  python3 scripts/v4_phase3_orchestrator.py run
  或定时: 0 */6 * * * python3 scripts/v4_phase3_orchestrator.py run

作者: 诸葛马 (Hermes)
日期: 2026-06-30
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


class V4Phase3Orchestrator:
    """V4.0 Phase 3 编排器"""
    
    def __init__(self, base_dir: str = "/home/admin/lobster-network"):
        self.base_dir = Path(base_dir)
        self.scripts_dir = self.base_dir / "scripts"
        self.reports_dir = self.base_dir / "reports" / "phase3"
        self.reports_dir.mkdir(parents=True, exist_ok=True)
        
        self.nodes = ["xiaochen", "zhuguxia", "qoder"]
        self.domain_pairs = ["go_stock", "go_protocol", "stock_protocol"]
    
    def run_nwda_analysis(self) -> Dict:
        """执行NWDAF体验分析"""
        print("\n📊 Step 1: NWDAF体验分析")
        print("=" * 50)
        
        results = {}
        for node in self.nodes:
            try:
                script = self.scripts_dir / "nwda_experience_analyzer.py"
                if script.exists():
                    result = subprocess.run(
                        ["python3", str(script), node],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=str(self.base_dir)
                    )
                    results[node] = {
                        "status": "success" if result.returncode == 0 else "failed",
                        "output": result.stdout.strip(),
                        "error": result.stderr.strip() if result.stderr else "",
                    }
                    print(result.stdout.strip())
                else:
                    results[node] = {"status": "script_not_found"}
                    print(f"  ⚠️ 脚本不存在: {script}")
            except Exception as e:
                results[node] = {"status": "error", "error": str(e)}
                print(f"  ❌ {node}分析失败: {e}")
        
        return {"step": "nwda_analysis", "results": results}
    
    def run_proactive_service(self) -> Dict:
        """执行主动服务"""
        print("\n📚 Step 2: 主动服务推送")
        print("=" * 50)
        
        results = {}
        for node in self.nodes:
            try:
                script = self.scripts_dir / "proactive_service.py"
                if script.exists():
                    result = subprocess.run(
                        ["python3", str(script), node],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=str(self.base_dir)
                    )
                    results[node] = {
                        "status": "success" if result.returncode == 0 else "failed",
                        "output": result.stdout.strip(),
                        "error": result.stderr.strip() if result.stderr else "",
                    }
                    print(result.stdout.strip())
                else:
                    results[node] = {"status": "script_not_found"}
                    print(f"  ⚠️ 脚本不存在: {script}")
            except Exception as e:
                results[node] = {"status": "error", "error": str(e)}
                print(f"  ❌ {node}服务失败: {e}")
        
        return {"step": "proactive_service", "results": results}
    
    def run_knowledge_accumulation(self) -> Dict:
        """执行知识沉淀"""
        print("\n📖 Step 3: 知识沉淀")
        print("=" * 50)
        
        results = {}
        for node in self.nodes:
            try:
                script = self.scripts_dir / "knowledge_accumulator.py"
                if script.exists():
                    result = subprocess.run(
                        ["python3", str(script), node],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=str(self.base_dir)
                    )
                    results[node] = {
                        "status": "success" if result.returncode == 0 else "failed",
                        "output": result.stdout.strip(),
                        "error": result.stderr.strip() if result.stderr else "",
                    }
                    print(result.stdout.strip())
                else:
                    results[node] = {"status": "script_not_found"}
                    print(f"  ⚠️ 脚本不存在: {script}")
            except Exception as e:
                results[node] = {"status": "error", "error": str(e)}
                print(f"  ❌ {node}沉淀失败: {e}")
        
        return {"step": "knowledge_accumulation", "results": results}
    
    def run_cross_domain_analysis(self) -> Dict:
        """执行跨领域分析"""
        print("\n🔄 Step 4: 跨领域联动")
        print("=" * 50)
        
        results = {}
        for pair in self.domain_pairs:
            try:
                script = self.scripts_dir / "cross_domain_engine.py"
                if script.exists():
                    result = subprocess.run(
                        ["python3", str(script), pair],
                        capture_output=True,
                        text=True,
                        timeout=60,
                        cwd=str(self.base_dir)
                    )
                    results[pair] = {
                        "status": "success" if result.returncode == 0 else "failed",
                        "output": result.stdout.strip(),
                        "error": result.stderr.strip() if result.stderr else "",
                    }
                    print(result.stdout.strip())
                else:
                    results[pair] = {"status": "script_not_found"}
                    print(f"  ⚠️ 脚本不存在: {script}")
            except Exception as e:
                results[pair] = {"status": "error", "error": str(e)}
                print(f"  ❌ {pair}分析失败: {e}")
        
        return {"step": "cross_domain_analysis", "results": results}
    
    def generate_execution_report(self, step_results: List[Dict]) -> Dict:
        """生成执行报告"""
        report = {
            "report_id": f"phase3-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "phase": "Phase 3: 业务智能",
            "steps_executed": len(step_results),
            "steps": step_results,
            "summary": {
                "total_steps": 4,
                "completed_steps": sum(1 for s in step_results if any(
                    r.get("status") == "success" for r in s.get("results", {}).values()
                )),
                "nodes_processed": len(self.nodes),
                "domain_pairs_analyzed": len(self.domain_pairs),
            },
        }
        
        return report
    
    def run(self) -> Dict:
        """执行完整Phase 3流程"""
        print("=" * 60)
        print("🦞 小龙虾网络 V4.0 Phase 3: 业务智能编排")
        print("=" * 60)
        print(f"📅 执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC+8")
        print(f"🖥️ 节点: {', '.join(self.nodes)}")
        print(f"🔄 领域对: {', '.join(self.domain_pairs)}")
        
        start_time = datetime.now()
        step_results = []
        
        # Step 1: NWDAF体验分析
        try:
            result1 = self.run_nwda_analysis()
            step_results.append(result1)
        except Exception as e:
            print(f"❌ NWDAF分析失败: {e}")
            step_results.append({"step": "nwda_analysis", "status": "error", "error": str(e)})
        
        # Step 2: 主动服务推送
        try:
            result2 = self.run_proactive_service()
            step_results.append(result2)
        except Exception as e:
            print(f"❌ 主动服务失败: {e}")
            step_results.append({"step": "proactive_service", "status": "error", "error": str(e)})
        
        # Step 3: 知识沉淀
        try:
            result3 = self.run_knowledge_accumulation()
            step_results.append(result3)
        except Exception as e:
            print(f"❌ 知识沉淀失败: {e}")
            step_results.append({"step": "knowledge_accumulation", "status": "error", "error": str(e)})
        
        # Step 4: 跨领域分析
        try:
            result4 = self.run_cross_domain_analysis()
            step_results.append(result4)
        except Exception as e:
            print(f"❌ 跨领域分析失败: {e}")
            step_results.append({"step": "cross_domain_analysis", "status": "error", "error": str(e)})
        
        # 生成报告
        report = self.generate_execution_report(step_results)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        report["duration_seconds"] = round(duration, 2)
        
        # 保存报告
        report_file = self.reports_dir / f"{report['report_id']}.json"
        report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False))
        
        # 输出总结
        print("\n" + "=" * 60)
        print("📊 Phase 3 执行总结")
        print("=" * 60)
        print(f"⏱️  执行耗时: {duration:.1f}秒")
        print(f"✅ 完成步骤: {report['summary']['completed_steps']}/{report['summary']['total_steps']}")
        print(f"📄 报告路径: {report_file}")
        
        return report


def main():
    if len(sys.argv) < 2 or sys.argv[1] != "run":
        print("用法: python3 v4_phase3_orchestrator.py run")
        sys.exit(1)
    
    orchestrator = V4Phase3Orchestrator()
    report = orchestrator.run()
    
    # 返回状态码
    completed = report["summary"]["completed_steps"]
    total = report["summary"]["total_steps"]
    sys.exit(0 if completed == total else 1)


if __name__ == "__main__":
    main()
