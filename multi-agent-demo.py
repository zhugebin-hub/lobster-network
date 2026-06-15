#!/usr/bin/env python3
"""
多智能体协作知识问答系统 Demo
Author: 李皓然
Date: 2026-06-11

功能：演示通过 NFS 共享存储实现 OpenClaw（小龙虾）与 Hermes（诸葛马）
     之间的跨服务器消息通信与知识问答协作。

使用方式：
  python3 multi-agent-demo.py [--send "问题内容"] [--wait msg_id] [--test]
"""

import json
import os
import sys
import time
import uuid
import argparse
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════
# 配置区
# ═══════════════════════════════════════════════════════

NFS_BASE = "/shared/messages"
LOBSTER_DIR = os.path.join(NFS_BASE, "from-lobster")
HERMES_DIR = os.path.join(NFS_BASE, "from-hermes")
ARCHIVE_DIR = os.path.join(NFS_BASE, "archive")

AGENT_ID = "lobster-001"
DEFAULT_TIMEOUT = 120  # 秒

# ═══════════════════════════════════════════════════════
# 核心类
# ═══════════════════════════════════════════════════════

class MultiAgentDemo:
    """多智能体协作 Demo 主类"""

    def __init__(self, lobster_dir=None, hermes_dir=None):
        self.agent_id = AGENT_ID
        self.lobster_dir = lobster_dir or LOBSTER_DIR
        self.hermes_dir = hermes_dir or HERMES_DIR
        self._ensure_dirs()

    def _ensure_dirs(self):
        """确保消息目录存在"""
        for d in [self.lobster_dir, self.hermes_dir, ARCHIVE_DIR]:
            os.makedirs(d, exist_ok=True)

    # ── 发送 ──────────────────────────────────────────

    def send_query(self, question, priority="normal", task_type="knowledge_query"):
        """发送知识检索请求到诸葛马

        Args:
            question: 用户问题
            priority: 优先级 (low / normal / high / critical)
            task_type: 任务类型

        Returns:
            str: 消息 ID
        """
        msg_id = f"demo-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        message = {
            "id": msg_id,
            "from": self.agent_id,
            "to": "hermes",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "type": task_type,
            "priority": priority,
            "question": question,
            "response_path": self.hermes_dir,
            "demo": True,
        }

        filepath = os.path.join(self.lobster_dir, f"{msg_id}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(message, f, ensure_ascii=False, indent=2)

        self._log(f"📤 发送请求: {question}")
        self._log(f"   消息 ID: {msg_id}")
        self._log(f"   优先级: {priority}")
        return msg_id

    # ── 接收 ──────────────────────────────────────────

    def wait_for_response(self, msg_id, timeout=None):
        """等待诸葛马的回复

        Args:
            msg_id: 请求消息 ID
            timeout: 超时时间（秒）

        Returns:
            dict | None: 回复消息，超时返回 None
        """
        timeout = timeout or DEFAULT_TIMEOUT
        start_time = time.time()
        checked = set()

        self._log(f"⏳ 等待回复 (超时 {timeout}s)...")

        while time.time() - start_time < timeout:
            elapsed = int(time.time() - start_time)

            # 扫描诸葛马回复目录
            try:
                filenames = os.listdir(self.hermes_dir)
            except FileNotFoundError:
                time.sleep(2)
                continue

            for filename in filenames:
                if filename in checked:
                    continue
                if not filename.endswith(".json"):
                    continue

                filepath = os.path.join(self.hermes_dir, filename)
                checked.add(filename)

                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        response = json.load(f)
                except (json.JSONDecodeError, IOError):
                    continue

                # 匹配回复
                if response.get("in_reply_to") == msg_id:
                    self._log(f"📥 收到回复! (耗时 {elapsed}s)")
                    self._archive(filepath, filename)
                    return response

            # 每 5 秒打印一次等待提示
            if elapsed % 5 == 0 and elapsed > 0:
                self._log(f"   ... 已等待 {elapsed}s")

            time.sleep(2)

        self._log(f"⏰ 超时：{timeout}s 内未收到回复")
        return None

    # ── 处理 ──────────────────────────────────────────

    def process_answer(self, response):
        """处理诸葛马返回的答案

        Args:
            response: 回复消息 dict

        Returns:
            dict: 处理后的结果
        """
        if not response:
            return {"error": "未收到有效回复"}

        return {
            "summary": response.get("summary", ""),
            "answer": response.get("answer", ""),
            "data": response.get("data", []),
            "sources": response.get("sources", []),
            "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    # ── 工具 ──────────────────────────────────────────

    def _archive(self, filepath, filename):
        """归档已处理的消息"""
        try:
            dest = os.path.join(ARCHIVE_DIR, filename)
            os.rename(filepath, dest)
        except Exception:
            pass

    def _log(self, msg):
        """打印日志"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

    # ── 批量测试 ──────────────────────────────────────

    def run_test_suite(self, questions=None):
        """运行测试套件

        Args:
            questions: 问题列表
        """
        if questions is None:
            questions = [
                {
                    "question": "道教在 AI 时代如何传承和发展？",
                    "priority": "high",
                },
                {
                    "question": "AI 技术如何应用于传统文化保护？",
                    "priority": "normal",
                },
                {
                    "question": "请分析道教'道法自然'思想对现代 AI 伦理的启示",
                    "priority": "high",
                },
            ]

        results = []
        for i, q in enumerate(questions, 1):
            self._log(f"\n{'='*50}")
            self._log(f"🧪 测试用例 {i}: {q['question']}")
            self._log(f"{'='*50}")

            msg_id = self.send_query(
                q["question"],
                priority=q.get("priority", "normal"),
            )
            response = self.wait_for_response(msg_id)
            result = self.process_answer(response)
            result["question"] = q["question"]
            result["msg_id"] = msg_id
            results.append(result)

            self._log(f"\n📊 结果摘要: {result.get('summary', 'N/A')[:100]}")

        # 输出汇总
        self._log(f"\n{'='*50}")
        self._log("📋 测试汇总")
        self._log(f"{'='*50}")
        self._log(f"  总测试数: {len(results)}")
        success = sum(1 for r in results if "error" not in r)
        self._log(f"  成功: {success} / 失败: {len(results) - success}")

        return results


# ═══════════════════════════════════════════════════════
# 模拟模式（本地演示，不依赖 NFS）
# ═══════════════════════════════════════════════════════

class SimulatedDemo:
    """本地模拟演示模式 — 不需要 NFS 即可运行

    用于演示消息格式、交互流程和处理逻辑。
    """

    MOCK_ANSWERS = {
        "道教在 AI 时代如何传承和发展？": {
            "summary": "道教在 AI 时代可通过数字化经典、智能问答系统、VR 修炼体验等方式实现传承与创新。",
            "answer": (
                "道教在 AI 时代的传承与发展可以从以下维度展开：\n\n"
                "1. **经典数字化**：利用 NLP 技术对《道德经》《庄子》等经典进行语义解析，"
                "构建道教文化知识图谱。\n\n"
                "2. **智能问答**：开发道教义理智能问答系统，为信众和研究者提供即时解答。\n\n"
                "3. **修炼体验创新**：结合 VR/AR 技术，打造沉浸式道教文化体验。\n\n"
                "4. **心理疏导应用**：将道教'道法自然''清静无为'等智慧转化为现代心理疏导方法。\n\n"
                "5. **跨文化对话**：利用 AI 翻译和交流工具，促进道教文化与国际学术界的对话。"
            ),
            "sources": ["中国道教协会数字化项目", "道教学术研究", "AI 文化传承案例"],
        },
        "AI 技术如何应用于传统文化保护？": {
            "summary": "AI 在传统文化保护中的应用包括数字化修复、智能分类、语音保存、创意生成等。",
            "answer": (
                "AI 技术在传统文化保护中的主要应用：\n\n"
                "1. **数字化修复**：计算机视觉技术修复残损壁画、古籍、文物。\n\n"
                "2. **智能分类与标注**：利用图像识别对传统纹样、器型、书法等进行自动分类。\n\n"
                "3. **语音保存**：方言语音合成与识别，保护濒危语言资源。\n\n"
                "4. **创意生成**：基于传统风格生成新的设计方案，推动文化创新。\n\n"
                "5. **多模态记录**：对戏曲、舞蹈等表演艺术进行全方位数字化记录。"
            ),
            "sources": ["敦煌研究院 AI 实验室", "清华美院 AI 设计实验室", "中国艺术研究院"],
        },
        "请分析道教'道法自然'思想对现代 AI 伦理的启示": {
            "summary": "'道法自然'强调顺应自然规律，为 AI 伦理提供了'以人为本、技术向善'的哲学基础。",
            "answer": (
                "道教'道法自然'思想对现代 AI 伦理的启示：\n\n"
                "1. **顺应而非对抗**：AI 发展应顺应人类自然需求，而非强制改变人类行为模式。\n\n"
                "2. **无为而治**：在 AI 治理中，避免过度干预，让技术自然演化与自我调节。\n\n"
                "3. **阴阳平衡**：AI 的效率与公平、创新与安全需要保持动态平衡。\n\n"
                "4. **万物一体**：AI 应服务于全人类福祉，而非少数群体利益。\n\n"
                "5. **返璞归真**：在算法日益复杂的今天，回归简单、透明、可解释的设计原则。"
            ),
            "sources": ["老庄哲学研究", "AI 伦理学", "科技哲学"],
        },
    }

    def send_query(self, question, priority="normal"):
        msg_id = f"demo-sim-{int(time.time())}-{uuid.uuid4().hex[:8]}"
        self._log(f"📤 [模拟] 发送请求: {question}")
        self._log(f"   消息 ID: {msg_id}")
        return msg_id

    def wait_for_response(self, msg_id, timeout=5):
        self._log("⏳ [模拟] 等待回复...")
        time.sleep(1.5)  # 模拟网络延迟

        # 匹配最接近的问题
        best_match = None
        best_score = 0
        for q, ans in self.MOCK_ANSWERS.items():
            # 简单关键词匹配
            score = sum(1 for word in q.split() if word in msg_id or word in str(msg_id))
            # 直接用问题原文匹配
            if q in str(msg_id):
                best_match = ans
                break

        if best_match is None:
            # 返回默认答案
            best_match = {
                "summary": "这是一个模拟回复，展示多智能体协作的消息格式。",
                "answer": "模拟模式下，返回通用答案。实际运行时需要连接真实的诸葛马服务。",
                "sources": ["模拟数据"],
            }

        self._log(f"📥 [模拟] 收到回复! (耗时 1.5s)")
        return best_match

    def process_answer(self, response):
        if not response:
            return {"error": "未收到有效回复"}
        return {
            "summary": response.get("summary", ""),
            "answer": response.get("answer", ""),
            "sources": response.get("sources", []),
            "processed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    def run_test_suite(self, questions=None):
        if questions is None:
            questions = [
                {"question": "道教在 AI 时代如何传承和发展？", "priority": "high"},
                {"question": "AI 技术如何应用于传统文化保护？", "priority": "normal"},
                {"question": "请分析道教'道法自然'思想对现代 AI 伦理的启示", "priority": "high"},
            ]

        results = []
        for i, q in enumerate(questions, 1):
            self._log(f"\n{'='*50}")
            self._log(f"🧪 测试用例 {i}: {q['question']}")
            self._log(f"{'='*50}")

            msg_id = self.send_query(q["question"], priority=q.get("priority", "normal"))
            response = self.wait_for_response(msg_id)
            result = self.process_answer(response)
            result["question"] = q["question"]
            result["msg_id"] = msg_id
            results.append(result)

            self._log(f"\n📊 摘要: {result.get('summary', 'N/A')}")

        self._log(f"\n{'='*50}")
        self._log("📋 测试汇总")
        self._log(f"{'='*50}")
        self._log(f"  总测试数: {len(results)}")
        success = sum(1 for r in results if "error" not in r)
        self._log(f"  成功: {success} / 失败: {len(results) - success}")
        return results

    def _log(self, msg):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


# ═══════════════════════════════════════════════════════
# CLI 入口
# ═══════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="多智能体协作知识问答系统 Demo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 模拟模式（本地演示，无需 NFS）
  python3 multi-agent-demo.py --simulate --test

  # 发送单个问题（需要 NFS）
  python3 multi-agent-demo.py --send "道教在 AI 时代如何传承？"

  # 运行测试套件（需要 NFS）
  python3 multi-agent-demo.py --test

  # 等待指定消息 ID 的回复
  python3 multi-agent-demo.py --wait demo-1718092800-abc12345
        """,
    )

    parser.add_argument("--send", type=str, help="发送一个问题到诸葛马")
    parser.add_argument("--wait", type=str, help="等待指定消息 ID 的回复")
    parser.add_argument("--test", action="store_true", help="运行测试套件")
    parser.add_argument(
        "--simulate",
        action="store_true",
        help="使用模拟模式（无需 NFS，本地演示）",
    )
    parser.add_argument("--timeout", type=int, default=120, help="超时时间（秒）")
    parser.add_argument("--priority", choices=["low", "normal", "high", "critical"], default="normal")

    args = parser.parse_args()

    print("🦞 多智能体协作知识问答系统 Demo")
    print(f"   作者: 李皓然 | 日期: {datetime.now().strftime('%Y-%m-%d')}")
    print()

    if args.simulate:
        # ── 模拟模式 ──
        demo = SimulatedDemo()
        if args.test:
            demo.run_test_suite()
        elif args.send:
            msg_id = demo.send_query(args.send, priority=args.priority)
            response = demo.wait_for_response(msg_id)
            result = demo.process_answer(response)
            print(f"\n📝 答案:\n{result.get('answer', 'N/A')}")
            print(f"\n📚 来源: {', '.join(result.get('sources', []))}")
        else:
            demo.run_test_suite()
    else:
        # ── 真实模式（需要 NFS） ──
        if not os.path.exists(NFS_BASE):
            print(f"⚠️  NFS 目录不存在: {NFS_BASE}")
            print("   请使用 --simulate 模式进行本地演示")
            print("   或确保 NFS 已正确挂载")
            sys.exit(1)

        demo = MultiAgentDemo()

        if args.test:
            demo.run_test_suite()
        elif args.send:
            msg_id = demo.send_query(args.send, priority=args.priority)
            response = demo.wait_for_response(msg_id, timeout=args.timeout)
            result = demo.process_answer(response)
            if "error" not in result:
                print(f"\n📝 答案:\n{result.get('answer', 'N/A')}")
                print(f"\n📚 来源: {', '.join(result.get('sources', []))}")
            else:
                print(f"\n❌ {result['error']}")
        elif args.wait:
            response = demo.wait_for_response(args.wait, timeout=args.timeout)
            result = demo.process_answer(response)
            if "error" not in result:
                print(f"\n📝 答案:\n{result.get('answer', 'N/A')}")
            else:
                print(f"\n❌ {result['error']}")
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
