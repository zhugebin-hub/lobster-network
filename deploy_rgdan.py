#!/usr/bin/env python3
"""RGDAN 一键部署脚本 - 上传代码到服务器并启动训练"""

from fabric import Connection
import os
import sys

# ===== 配置 =====
SERVER = '10.20.33.210'
USER = 'gama'
REMOTE_DIR = '/data/gama/rgdan'
LOCAL_DIR = '.'  # 当前目录

# 使用密码还是密钥？
# 方式1: 密码
PASSWORD = ''  # ← 填密码
# 方式2: SSH 密钥（推荐）
KEY_FILE = '~/.ssh/id_rsa'  # ← 你的私钥路径

def get_connection():
    """建立 SSH 连接"""
    if PASSWORD:
        return Connection(SERVER, user=USER,
                         connect_kwargs={"password": PASSWORD})
    else:
        return Connection(SERVER, user=USER,
                         connect_kwargs={"key_filename": KEY_FILE})

def upload_files():
    """上传所有代码和数据文件"""
    files_to_upload = [
        'train.py',
        'train_BJ.py',
        'model.py',
        'utils.py',
        'README.md',
    ]
    dirs_to_upload = ['data']

    print("🔌 连接服务器...")
    conn = get_connection()

    # 创建远程目录
    conn.run(f'mkdir -p {REMOTE_DIR}')

    # 上传文件
    for f in files_to_upload:
        if os.path.exists(f):
            print(f"📤 上传 {f}...")
            conn.put(f, f'{REMOTE_DIR}/{f}')
        else:
            print(f"⚠️  文件不存在: {f}")

    # 上传目录
    for d in dirs_to_upload:
        if os.path.exists(d):
            print(f"📤 上传目录 {d}/...")
            conn.put(d, f'{REMOTE_DIR}/{d}')
        else:
            print(f"⚠️  目录不存在: {d}")

    print("✅ 上传完成！")
    conn.close()

def run_train(dataset='PeMS'):
    """在服务器上启动训练"""
    print(f"\n🚀 启动 {dataset} 训练...")
    conn = get_connection()

    if dataset == 'PeMS':
        cmd = f'cd {REMOTE_DIR} && source /data/miniconda/etc/profile.d/conda.sh && conda activate base && python train.py --dataset PeMS'
    elif dataset == 'BJ500':
        cmd = f'cd {REMOTE_DIR} && source /data/miniconda/etc/profile.d/conda.sh && conda activate base && python train_BJ.py --dataset BJ500'
    else:
        print(f"⚠️  未知数据集: {dataset}")
        return

    # 后台运行
    full_cmd = f'nohup {cmd} > {REMOTE_DIR}/train_{dataset}.log 2>&1 &'
    conn.run(full_cmd)
    print(f"✅ {dataset} 训练已后台启动！")
    print(f"📋 查看日志: tail -f {REMOTE_DIR}/train_{dataset}.log")
    conn.close()

def check_status():
    """检查训练状态"""
    conn = get_connection()
    print("\n📊 训练状态:")
    result = conn.run(f'ps aux | grep python | grep train', hide=True, warn=True)
    print(result.stdout if result.stdout else "没有运行中的训练进程")
    conn.close()

def view_log(dataset='PeMS'):
    """查看训练日志"""
    conn = get_connection()
    print(f"\n📋 {dataset} 训练日志 (最后30行):")
    result = conn.run(f'tail -30 {REMOTE_DIR}/train_{dataset}.log', warn=True)
    print(result.stdout)
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("""
🦞 RGDAN 一键部署工具

用法:
  python deploy_rgdan.py upload              # 上传文件到服务器
  python deploy_rgdan.py train PeMS          # 启动 PeMS 训练
  python deploy_rgdan.py train BJ500         # 启动 BJ500 训练
  python deploy_rgdan.py status              # 查看训练状态
  python deploy_rgdan.py log PeMS            # 查看训练日志
  python deploy_rgdan.py all                 # 上传 + 启动两个数据集训练
        """)
        sys.exit(0)

    action = sys.argv[1]

    if action == 'upload':
        upload_files()
    elif action == 'train':
        dataset = sys.argv[2] if len(sys.argv) > 2 else 'PeMS'
        run_train(dataset)
    elif action == 'status':
        check_status()
    elif action == 'log':
        dataset = sys.argv[2] if len(sys.argv) > 2 else 'PeMS'
        view_log(dataset)
    elif action == 'all':
        upload_files()
        run_train('PeMS')
        run_train('BJ500')
    else:
        print(f"未知命令: {action}")
