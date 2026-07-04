#!/usr/bin/env python3
"""
safe_git.py - 小龙虾网络安全Git操作封装
解决lobster-network中常见的git push失败、rebase冲突、token过期等问题。

用法:
    python scripts/safe_git.py pull          # 安全拉取（自动rebase）
    python scripts/safe_git.py push          # 安全推送（自动重试3次）
    python scripts/safe_git.py push-all      # 同时推送到GitHub和Gitee
    python scripts/safe_git.py sync          # pull + push 一步到位
    python scripts/safe_git.py status        # 检查仓库状态
"""

import subprocess
import sys
import os
import time
import json
from pathlib import Path
from datetime import datetime

# === 配置 ===
MAX_RETRIES = 3
RETRY_DELAY = 5  # 秒，指数退避基数
GITHUB_USER = "zhugebin-hub"
GITHUB_REPO = "zhugebin-hub/lobster-network"
GITEE_REPO = "zhugebin-zj/lobster-network"

# 自动检测仓库根目录
def get_repo_root():
    """获取git仓库根目录"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, check=True
        )
        return Path(result.stdout.strip())
    except subprocess.CalledProcessError:
        print("[ERROR] 当前目录不在git仓库中")
        sys.exit(1)

REPO_ROOT = get_repo_root()

def run_git(*args, check=True, timeout=60):
    """执行git命令，返回结果"""
    cmd = ["git"] + list(args)
    print(f"  [git] {' '.join(args)}")
    try:
        result = subprocess.run(
            cmd, cwd=str(REPO_ROOT),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=timeout
        )
        if check and result.returncode != 0:
            print(f"  [WARN] git返回非零: {result.returncode}")
            if result.stderr:
                print(f"  [STDERR] {result.stderr.strip()}")
        return result
    except subprocess.TimeoutExpired:
        print(f"  [ERROR] git命令超时({timeout}s)")
        return None
    except Exception as e:
        print(f"  [ERROR] git执行失败: {e}")
        return None

def get_token():
    """从git credential获取GitHub token"""
    try:
        result = subprocess.run(
            ["git", "credential-osxkeychain", "get"],
            input="protocol=https\nhost=github.com\n",
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, timeout=10
        )
        for line in result.stdout.split("\n"):
            if line.startswith("password="):
                return line.split("=", 1)[1]
    except Exception:
        pass
    # 尝试从环境变量
    return os.environ.get("GITHUB_TOKEN", "")

def ensure_authenticated_remote():
    """确保origin remote带有认证信息"""
    result = run_git("remote", "get-url", "origin", check=False)
    if not result or result.returncode != 0:
        return False
    
    url = result.stdout.strip()
    
    # 如果URL已经包含token，跳过
    if "@" in url and "github.com" in url and url.count("@") >= 1:
        return True
    
    # 获取token并设置带认证的URL
    token = get_token()
    if token:
        auth_url = f"https://{GITHUB_USER}:{token}@github.com/{GITHUB_REPO}.git"
        run_git("remote", "set-url", "origin", auth_url, check=False)
        print(f"  [OK] origin已设置认证URL")
        return True
    else:
        print("  [WARN] 无法获取GitHub token，使用原始URL")
        return False

def safe_pull():
    """安全拉取：stash → pull --rebase → pop"""
    print("\n=== Safe Pull ===")
    
    # 检查是否有未提交的更改
    status = run_git("status", "--porcelain")
    has_changes = status and status.stdout.strip()
    
    if has_changes:
        print("  [INFO] 检测到未提交更改，先stash...")
        stash_result = run_git("stash", "push", "-m", f"safe_git_auto_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        if not stash_result or stash_result.returncode != 0:
            print("  [ERROR] stash失败")
            return False
    else:
        print("  [INFO] 工作区干净，直接pull")
    
    # 确保remote有认证
    ensure_authenticated_remote()
    
    # Pull with rebase
    pull_result = run_git("pull", "--rebase", "origin", "master", timeout=120)
    
    if not pull_result or pull_result.returncode != 0:
        print("  [WARN] rebase失败，尝试merge...")
        run_git("rebase", "--abort", check=False)
        pull_result = run_git("pull", "origin", "master", "--no-rebase", timeout=120)
    
    if not pull_result or pull_result.returncode != 0:
        print("  [ERROR] pull失败")
        if has_changes:
            run_git("stash", "pop", check=False)
        return False
    
    # 恢复stash
    if has_changes:
        pop_result = run_git("stash", "pop", check=False)
        if pop_result and pop_result.returncode != 0:
            print("  [WARN] stash pop有冲突，请手动解决")
            # 使用theirs策略解决shared文件的冲突
            run_git("checkout", "--theirs", ".shared/", check=False)
            run_git("add", ".shared/", check=False)
    
    print("  [OK] Pull完成")
    return True

def safe_push(remote="origin", branch="master", retries=MAX_RETRIES):
    """安全推送：带重试和指数退避"""
    print(f"\n=== Safe Push to {remote}/{branch} ===")
    
    ensure_authenticated_remote()
    
    for attempt in range(1, retries + 1):
        print(f"  [尝试 {attempt}/{retries}]")
        
        result = run_git("push", remote, branch, timeout=120)
        
        if result and result.returncode == 0:
            print(f"  [OK] Push成功")
            return True
        
        if result is None:
            print(f"  [WARN] Push超时")
        elif "rejected" in (result.stderr or ""):
            print(f"  [WARN] Push被reject，先pull再push...")
            if not safe_pull():
                print("  [ERROR] pull失败，无法push")
                return False
            # pull成功后再push
            result = run_git("push", remote, branch, timeout=120)
            if result and result.returncode == 0:
                print(f"  [OK] Push成功（pull后）")
                return True
        else:
            print(f"  [WARN] Push失败: {(result.stderr or 'unknown')[:200]}")
        
        if attempt < retries:
            delay = RETRY_DELAY * (2 ** (attempt - 1))
            print(f"  [INFO] {delay}秒后重试...")
            time.sleep(delay)
    
    print(f"  [ERROR] Push在{retries}次尝试后仍失败")
    return False

def safe_push_all():
    """同时推送到GitHub和Gitee"""
    print("\n=== Push All Remotes ===")
    
    gh_ok = safe_push("origin", "master")
    
    # 检查gitee remote是否存在
    gitee_result = run_git("remote", "get-url", "gitee", check=False)
    if gitee_result and gitee_result.returncode == 0:
        ge_ok = safe_push("gitee", "master")
    else:
        print("  [INFO] 未配置gitee remote，跳过")
        ge_ok = None
    
    return gh_ok, ge_ok

def safe_sync():
    """一步到位：pull + push"""
    print("\n=== Safe Sync ===")
    
    if not safe_pull():
        print("[ERROR] Pull失败，中止sync")
        return False
    
    if not safe_push():
        print("[ERROR] Push失败")
        return False
    
    print("\n[OK] Sync完成")
    return True

def show_status():
    """显示仓库状态"""
    print("\n=== 仓库状态 ===")
    
    # 当前分支和commit
    run_git("log", "--oneline", "-1")
    
    # 分支信息
    run_git("branch", "-v")
    
    # 远程状态
    print("\n--- 远程仓库 ---")
    run_git("remote", "-v")
    
    # 未提交更改
    print("\n--- 工作区状态 ---")
    status = run_git("status", "-s")
    if status and not status.stdout.strip():
        print("  工作区干净")
    
    # 与远程的差异
    print("\n--- 与远程差异 ---")
    run_git("fetch", "origin", check=False)
    run_git("log", "--oneline", "master..origin/master", check=False)

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "pull":
        ok = safe_pull()
    elif action == "push":
        ok = safe_push()
    elif action == "push-all":
        gh, ge = safe_push_all()
        ok = gh
    elif action == "sync":
        ok = safe_sync()
    elif action == "status":
        show_status()
        ok = True
    else:
        print(f"未知操作: {action}")
        print("支持: pull, push, push-all, sync, status")
        ok = False
    
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
