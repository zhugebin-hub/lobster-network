#!/usr/bin/env python3
"""
🦞 小龙虾网络 — 节点注册脚本 (Git-Friendly版)

将节点信息写入仓库内的 registry/nodes/ 目录，
方便通过 git commit + PR 提交到中央注册表。

用法:
    python3 register_node.py --id <node_id> --name <名称> [选项]

示例:
    python3 register_node.py --id wukong --name "悟空" --perspective "企业AI助手"

完整参数:
    --id             节点唯一标识 (必填, 英文+下划线)
    --name           节点显示名称 (必填)
    --type           节点类型: agent/human/hybrid/coach (默认: agent)
    --perspective    你的独特视角 (默认: 通用型)
    --knowledge      你的知识领域 (默认: 通用知识)
    --capabilities   你的能力标签, 逗号分隔 (默认: dialogue,research)
    --value          价值取向 (默认: 协作创新)
    --learning-rate  学习速度: slow/medium/fast (默认: medium)
    --platform       运行平台 (默认: 自动检测)
    --repo-dir       仓库根目录 (默认: 自动检测, 向上查找 .git)
"""

import argparse
import json
import os
import platform
import sys
from datetime import datetime
from pathlib import Path


def detect_platform():
    system = platform.system().lower()
    if system == "darwin":
        return "macOS"
    elif system == "linux":
        return "Docker/Linux" if os.path.exists("/.dockerenv") else "Linux"
    elif system == "windows":
        return "Windows"
    return system


def find_repo_root(start_dir=None):
    """从当前目录向上查找 .git 目录，定位仓库根目录"""
    current = Path(start_dir or os.getcwd()).resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="🦞 注册节点到小龙虾网络 (写入 registry/nodes/)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 register_node.py --id wukong --name "悟空"
  python3 register_node.py --id wukong --name "悟空" --perspective "企业AI助手" --capabilities dialogue,research,code_review
        """,
    )
    parser.add_argument("--id", required=True, help="节点唯一标识 (英文+下划线)")
    parser.add_argument("--name", required=True, help="节点显示名称")
    parser.add_argument("--type", default="agent",
                        choices=["agent", "human", "hybrid", "coach"],
                        help="节点类型 (默认: agent)")
    parser.add_argument("--perspective", default="通用型", help="独特视角")
    parser.add_argument("--knowledge", default="通用知识", help="知识领域")
    parser.add_argument("--capabilities", default="dialogue,research",
                        help="能力标签, 逗号分隔")
    parser.add_argument("--value", default="协作创新", help="价值取向")
    parser.add_argument("--learning-rate", default="medium",
                        choices=["slow", "medium", "fast"],
                        help="学习速度")
    parser.add_argument("--platform", default=None, help="运行平台 (默认: 自动检测)")
    parser.add_argument("--repo-dir", default=None, help="仓库根目录 (默认: 自动检测)")
    return parser.parse_args()


def main():
    args = parse_args()

    # 定位仓库根目录
    if args.repo_dir:
        repo_root = Path(args.repo_dir).resolve()
    else:
        repo_root = find_repo_root()
        if repo_root is None:
            # 回退：使用当前目录
            repo_root = Path.cwd()

    nodes_dir = repo_root / "registry" / "nodes"
    nodes_dir.mkdir(parents=True, exist_ok=True)

    capabilities = [c.strip() for c in args.capabilities.split(",")]
    plat = args.platform or detect_platform()

    node_data = {
        "node_id": args.id,
        "name": args.name,
        "type": args.type,
        "perspective": args.perspective,
        "knowledge_base": args.knowledge,
        "value_orientation": args.value,
        "learning_rate": args.learning_rate,
        "capabilities": capabilities,
        "platform": plat,
        "registered_at": datetime.now().isoformat(),
        "status": "active",
        "version": "0.5.0",
    }

    # 写入节点文件
    node_file = nodes_dir / f"{args.id}.json"
    with open(node_file, "w", encoding="utf-8") as f:
        json.dump(node_data, f, ensure_ascii=False, indent=2)

    print("=" * 50)
    print("  🦞 小龙虾网络 — 节点注册完成!")
    print("=" * 50)
    print(f"  节点ID:   {args.id}")
    print(f"  名称:     {args.name}")
    print(f"  类型:     {args.type}")
    print(f"  视角:     {args.perspective}")
    print(f"  能力:     {', '.join(capabilities)}")
    print(f"  平台:     {plat}")
    print(f"  注册文件: {node_file}")
    print("=" * 50)

    # 列出当前所有节点
    all_nodes = sorted(nodes_dir.glob("*.json"))
    print(f"\n  📊 当前网络节点 ({len(all_nodes)} 个):")
    for nf in all_nodes:
        with open(nf, "r", encoding="utf-8") as f:
            nd = json.load(f)
        icon = "🟢" if nd.get("status") == "active" else "🔴"
        me = " ← 你在这里" if nd["node_id"] == args.id else ""
        print(f"    {icon} {nd['node_id']:15s} ({nd['name']}){me}")

    print(f"\n  📝 下一步: 提交注册文件到 GitHub")
    print(f"    git add registry/nodes/{args.id}.json")
    print(f'    git commit -m "feat: 注册新节点 {args.id}"')
    print(f"    git push origin main")
    print()


if __name__ == "__main__":
    main()
