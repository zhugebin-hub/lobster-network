#!/usr/bin/env python3
"""
小龙虾网络V3.0 - 训练流水线集成
Integrates V3.0 components (vector_memory, federated_learning, agent_economy)
into the training workflow for the Lobster Network.
"""

import json
import sys
import os
import uuid
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# ============================================================
# Repository root and path setup
# ============================================================

REPO_ROOT = Path(__file__).parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ============================================================
# V3.0 module imports with graceful fallback
# ============================================================

_HAS_VECTOR_MEMORY = False
_HAS_FEDERATED = False
_HAS_ECONOMY = False

try:
    from vector_memory.vector_memory import VectorMemory
    _HAS_VECTOR_MEMORY = True
except ImportError:
    VectorMemory = None

try:
    from federated_learning.federated_learning import (
        FederatedLearning,
        ModelUpdate,
        AggregationStrategy,
    )
    _HAS_FEDERATED = True
except ImportError:
    FederatedLearning = None
    ModelUpdate = None
    AggregationStrategy = None

try:
    from agent_economy.economy_system import Agent, AgentEconomy, Task
    _HAS_ECONOMY = True
except ImportError:
    Agent = None
    AgentEconomy = None
    Task = None


# ============================================================
# Monkey-patch: economy system may try to write to /shared/
# which causes OSError on local dev machines.  Redirect any
# storage_path attribute to a safe local directory.
# ============================================================

def _patch_economy_storage_path():
    """Redirect AgentEconomy.storage_path to a local .shared/ dir
    so that the economy system does not raise OSError when it
    attempts to write under /shared/."""
    if not _HAS_ECONOMY or AgentEconomy is None:
        return
    safe_dir = REPO_ROOT / ".shared" / "economy"
    safe_dir.mkdir(parents=True, exist_ok=True)
    # Patch __init__ to set storage_path after construction
    _original_init = AgentEconomy.__init__

    def _patched_init(self, *args, **kwargs):
        _original_init(self, *args, **kwargs)
        self.storage_path = str(safe_dir)

    AgentEconomy.__init__ = _patched_init


_patch_economy_storage_path()


# ============================================================
# V3TrainingPipeline
# ============================================================

class V3TrainingPipeline:
    """Orchestrates V3.0 components around a training session.

    Components
    ----------
    * VectorMemory  -- store / retrieve similar past problems
    * FederatedLearning -- participate in collaborative model rounds
    * AgentEconomy + Agent -- token rewards & reputation tracking
    """

    def __init__(self, student_id: str):
        self.student_id = student_id
        self.vector_memory = None
        self.federated = None
        self.economy = None
        self.agent = None
        self._tasks_completed = 0
        self.setup_components()

    # ------------------------------------------------------------------
    # Component bootstrap
    # ------------------------------------------------------------------

    def setup_components(self) -> Dict[str, bool]:
        """Instantiate V3.0 components for this student.

        Returns a dict indicating which components were successfully
        initialised so callers can adapt behaviour if needed.
        """
        status: Dict[str, bool] = {
            "vector_memory": False,
            "federated_learning": False,
            "agent_economy": False,
        }

        # -- Vector Memory --
        if _HAS_VECTOR_MEMORY:
            try:
                self.vector_memory = VectorMemory(dimension=768, max_entries=10000)
                status["vector_memory"] = True
            except Exception:
                self.vector_memory = None

        # -- Federated Learning --
        if _HAS_FEDERATED:
            try:
                self.federated = FederatedLearning(
                    model_dimension=100,
                    strategy=AggregationStrategy.FED_AVG,
                )
                status["federated_learning"] = True
            except Exception:
                self.federated = None

        # -- Agent Economy --
        if _HAS_ECONOMY:
            try:
                self.economy = AgentEconomy()
                self.agent = Agent(
                    agent_id=self.student_id,
                    name=f"Student-{self.student_id}",
                    balance=100.0,
                    reputation=5.0,
                    skills=["go-training"],
                )
                self.economy.register_agent(self.agent)
                status["agent_economy"] = True
            except Exception:
                self.economy = None
                self.agent = None

        return status

    # ------------------------------------------------------------------
    # Pre-training: search for similar problems
    # ------------------------------------------------------------------

    def pre_training(self, problem_list: List[str]) -> Dict[str, Any]:
        """Before training begins, search vector memory for similar past
        problems to provide context and hints.

        Parameters
        ----------
        problem_list : list[str]
            Descriptions of the problems the student will work on.

        Returns
        -------
        dict with keys ``similar_problems`` and ``memory_available``.
        """
        result: Dict[str, Any] = {
            "memory_available": self.vector_memory is not None,
            "similar_problems": [],
            "student_id": self.student_id,
            "timestamp": datetime.now().isoformat(),
        }

        if self.vector_memory is None:
            return result

        for problem in problem_list:
            matches = self.vector_memory.search(problem, top_k=3)
            similar = []
            for memory_id, score in matches:
                entry = self.vector_memory.get_memory(memory_id)
                if entry is not None:
                    similar.append({
                        "id": memory_id,
                        "content": entry.content,
                        "score": round(score, 4),
                        "metadata": entry.metadata,
                    })
            result["similar_problems"].append({
                "query": problem,
                "matches": similar,
            })

        return result

    # ------------------------------------------------------------------
    # Post-training: store results, federate, award tokens
    # ------------------------------------------------------------------

    def post_training(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """After a training session, perform three actions:

        1. Store the training results in vector memory.
        2. Submit a model update to the current federated learning round.
        3. Award tokens to the student's agent.

        Parameters
        ----------
        results : dict
            Must contain at least ``problems`` (list[str]) and ``score``
            (float 0-1).  Optional: ``duration_sec``, ``model_weights``.

        Returns
        -------
        dict summarising what each component did.
        """
        summary: Dict[str, Any] = {
            "student_id": self.student_id,
            "timestamp": datetime.now().isoformat(),
            "memory_stored": False,
            "federated_round": None,
            "tokens_awarded": 0.0,
        }

        problems = results.get("problems", [])
        score = results.get("score", 0.0)
        duration = results.get("duration_sec", 0)

        # -- 1. Store in Vector Memory --
        if self.vector_memory is not None:
            for problem in problems:
                content = f"[{self.student_id}] {problem} (score={score})"
                metadata = {
                    "student_id": self.student_id,
                    "score": score,
                    "duration_sec": duration,
                    "trained_at": datetime.now().isoformat(),
                }
                importance = min(1.0 + score, 2.0)
                self.vector_memory.add_memory(
                    content=content,
                    metadata=metadata,
                    importance=importance,
                )
            summary["memory_stored"] = True

        # -- 2. Federated Learning round --
        if self.federated is not None:
            round_id = self.federated.create_round()
            weights = results.get("model_weights", [score * 0.1] * 100)
            # Pad / trim to model_dimension (100)
            dim = self.federated.model_dimension
            if len(weights) < dim:
                weights = weights + [0.0] * (dim - len(weights))
            elif len(weights) > dim:
                weights = weights[:dim]

            update = ModelUpdate(
                node_id=self.student_id,
                weights=weights,
                sample_count=len(problems),
                round_id=round_id,
            )
            self.federated.submit_update(round_id, update)
            summary["federated_round"] = round_id

        # -- 3. Award tokens via economy --
        if self.economy is not None and self.agent is not None:
            reward_amount = 10.0 * score + 2.0 * len(problems)
            # Create a synthetic task for the training session
            task = Task(
                title=f"Training session {self.student_id}",
                description=f"Solved {len(problems)} problems, score={score}",
                reward=reward_amount,
                required_skills=[],
            )
            task_id = self.economy.create_task(task)
            self.economy.assign_task(task_id, self.agent.agent_id)
            self.economy.complete_task(task_id)
            self._tasks_completed += 1
            summary["tokens_awarded"] = round(reward_amount, 2)

        return summary

    # ------------------------------------------------------------------
    # Enhanced result generation
    # ------------------------------------------------------------------

    def generate_enhanced_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Take a raw training result dict and enhance it with V3.0
        metadata from all available components.

        Parameters
        ----------
        raw_result : dict
            Original training output (e.g. from the coach module).

        Returns
        -------
        A new dict that is a superset of *raw_result* with an added
        ``v3_enhancement`` key.
        """
        enhanced = dict(raw_result)
        v3_meta: Dict[str, Any] = {
            "enhanced_at": datetime.now().isoformat(),
            "student_id": self.student_id,
            "components_active": {
                "vector_memory": self.vector_memory is not None,
                "federated_learning": self.federated is not None,
                "agent_economy": self.economy is not None,
            },
            "enhancement_id": uuid.uuid4().hex[:12],
        }

        # Attach memory stats
        if self.vector_memory is not None:
            v3_meta["memory_stats"] = self.vector_memory.get_stats()

        # Attach federated training history
        if self.federated is not None:
            v3_meta["federated_history"] = self.federated.get_training_history()

        # Attach economy stats
        if self.economy is not None:
            v3_meta["economy_stats"] = self.economy.get_economy_stats()

        enhanced["v3_enhancement"] = v3_meta
        return enhanced

    # ------------------------------------------------------------------
    # Economy status
    # ------------------------------------------------------------------

    def get_economy_status(self) -> Dict[str, Any]:
        """Return a summary of the student's economic standing.

        Returns
        -------
        dict with ``balance``, ``reputation``, and ``tasks_completed``.
        """
        if self.agent is None:
            return {
                "balance": 0.0,
                "reputation": 0.0,
                "tasks_completed": self._tasks_completed,
                "economy_available": False,
            }
        return {
            "balance": self.agent.balance,
            "reputation": self.agent.reputation,
            "tasks_completed": self._tasks_completed,
            "economy_available": True,
        }


# ============================================================
# CLI commands
# ============================================================

def _cmd_demo(args: argparse.Namespace) -> None:
    """Run a demo training session through the V3 pipeline."""
    student_id = args.student or "demo-student"
    pipeline = V3TrainingPipeline(student_id)
    setup_status = pipeline.setup_components()

    print("=" * 60)
    print("  Lobster Network V3.0 - Training Pipeline Demo")
    print("=" * 60)
    print()

    # Show component status
    print("[1] Component Status:")
    for comp, ok in setup_status.items():
        mark = "OK" if ok else "UNAVAILABLE"
        print(f"    {comp:25s} ... {mark}")
    print()

    # Pre-training
    problems = [
        "围棋征子路线判断",
        "倒扑与扑的区分方法",
        "官子阶段目数计算",
    ]
    print(f"[2] Pre-training search for {len(problems)} problems:")
    pre = pipeline.pre_training(problems)
    for entry in pre.get("similar_problems", []):
        q = entry["query"]
        n = len(entry["matches"])
        print(f"    '{q}' -> {n} similar memories found")
    print()

    # Simulate training
    print("[3] Running training session ...")
    training_results = {
        "problems": problems,
        "score": 0.85,
        "duration_sec": 1800,
    }
    post = pipeline.post_training(training_results)
    print(f"    Memory stored  : {post['memory_stored']}")
    print(f"    Federated round: {post['federated_round']}")
    print(f"    Tokens awarded : {post['tokens_awarded']}")
    print()

    # Enhanced result
    print("[4] Generating enhanced result ...")
    enhanced = pipeline.generate_enhanced_result(training_results)
    v3 = enhanced.get("v3_enhancement", {})
    print(f"    Enhancement ID : {v3.get('enhancement_id')}")
    active = v3.get("components_active", {})
    for comp, ok in active.items():
        print(f"    {comp:25s} ... {'active' if ok else 'inactive'}")
    print()

    # Economy status
    print("[5] Economy status:")
    eco = pipeline.get_economy_status()
    print(f"    Balance        : {eco['balance']:.2f}")
    print(f"    Reputation     : {eco['reputation']:.2f}")
    print(f"    Tasks completed: {eco['tasks_completed']}")
    print()
    print("Demo complete.")


def _cmd_status(args: argparse.Namespace) -> None:
    """Show V3.0 component availability status."""
    student_id = args.student or "status-check"
    pipeline = V3TrainingPipeline(student_id)

    print("V3.0 Component Status")
    print("-" * 40)
    print(f"  vector_memory     : {'available' if _HAS_VECTOR_MEMORY else 'NOT available'}")
    print(f"  federated_learning: {'available' if _HAS_FEDERATED else 'NOT available'}")
    print(f"  agent_economy     : {'available' if _HAS_ECONOMY else 'NOT available'}")
    print()

    eco = pipeline.get_economy_status()
    print(f"  Agent balance     : {eco['balance']:.2f}")
    print(f"  Agent reputation  : {eco['reputation']:.2f}")
    print(f"  Tasks completed   : {eco['tasks_completed']}")


def _cmd_enhance(args: argparse.Namespace) -> None:
    """Enhance an existing result JSON file with V3.0 metadata."""
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    with open(input_path, "r", encoding="utf-8") as f:
        raw_result = json.load(f)

    student_id = args.student or "enhance-student"
    pipeline = V3TrainingPipeline(student_id)
    enhanced = pipeline.generate_enhanced_result(raw_result)

    output_path = Path(args.output) if args.output else input_path.with_suffix(".enhanced.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enhanced, f, indent=2, ensure_ascii=False)

    print(f"Enhanced result written to: {output_path}")
    v3 = enhanced.get("v3_enhancement", {})
    active = [k for k, v in v3.get("components_active", {}).items() if v]
    print(f"Active components: {', '.join(active) if active else 'none'}")


# ============================================================
# Entry point
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Lobster Network V3.0 Training Pipeline",
    )
    parser.add_argument(
        "--student", type=str, default=None,
        help="Student ID (default: command-specific)",
    )
    subparsers = parser.add_subparsers(dest="command")

    # demo
    sub_demo = subparsers.add_parser("demo", help="Run a demo training session")
    sub_demo.set_defaults(func=_cmd_demo)

    # status
    sub_status = subparsers.add_parser("status", help="Show V3.0 component status")
    sub_status.set_defaults(func=_cmd_status)

    # enhance
    sub_enhance = subparsers.add_parser(
        "enhance", help="Enhance a result JSON with V3.0 metadata",
    )
    sub_enhance.add_argument("input", type=str, help="Path to input JSON file")
    sub_enhance.add_argument(
        "--output", type=str, default=None,
        help="Output path (default: <input>.enhanced.json)",
    )
    sub_enhance.set_defaults(func=_cmd_enhance)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
