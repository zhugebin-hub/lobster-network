#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lobster Network - 消息队列清理脚本
===================================

功能说明:
  1. 扫描 .shared/messages/queue/{node}/inbox/ 下所有节点的收件箱
  2. 将超过指定天数（默认7天）的旧消息归档到 .shared/messages/archive/{node}/YYYY-MM/
  3. 生成清理摘要报告：各节点归档数、剩余数、释放空间
  4. 支持 --dry-run 预览模式（不实际移动文件）
  5. 支持 --days N 自定义过期天数阈值
  6. 优雅处理损坏的 JSON、缺失时间戳等异常情况

使用方式:
  python3 scripts/message_cleanup.py [--dry-run] [--days 7]

兼容: Python 3.6+
"""

import argparse
import json
import os
import shutil
import sys
import time
from datetime import datetime, timedelta
from collections import OrderedDict


# ============================================================
# 常量定义
# ============================================================

# 消息队列根目录（相对于 lobster-network 项目根）
QUEUE_REL = os.path.join('.shared', 'messages', 'queue')
# 归档根目录
ARCHIVE_REL = os.path.join('.shared', 'messages', 'archive')

# JSON 中可能包含时间戳的字段名列表（按优先级排列）
TIMESTAMP_FIELDS = [
    'timestamp',           # 标准消息时间戳
    'acknowledged_at',     # ACK 确认时间
    'sent_at',             # 发送时间
    'created_at',          # 创建时间
    'date',                # 日期字段（可能是 YYYY-MM-DD 格式）
]

# 支持的时间戳格式（按常见程度排列）
TIMESTAMP_FORMATS = [
    '%Y-%m-%dT%H:%M:%S.%f',     # ISO 8601 带微秒
    '%Y-%m-%dT%H:%M:%S',        # ISO 8601 不带微秒
    '%Y-%m-%dT%H:%M:%S.%fZ',    # ISO 8601 带 Z 后缀
    '%Y-%m-%dT%H:%M:%SZ',       # ISO 8601 带 Z 无微秒
    '%Y-%m-%d %H:%M:%S.%f',     # 空格分隔带微秒
    '%Y-%m-%d %H:%M:%S',        # 空格分隔
    '%Y-%m-%d',                  # 仅日期
]


# ============================================================
# 工具函数
# ============================================================

def parse_timestamp(value):
    """
    尝试将时间戳字段值解析为 datetime 对象。
    支持多种 ISO 8601 变体和纯日期格式。

    Args:
        value: 时间戳字符串或数字（Unix 时间戳）

    Returns:
        datetime 对象，解析失败时返回 None
    """
    if value is None:
        return None

    # 处理 Unix 时间戳（数字类型）
    if isinstance(value, (int, float)):
        try:
            return datetime.fromtimestamp(value)
        except (ValueError, OSError, OverflowError):
            return None

    # 必须是字符串才能继续解析
    if not isinstance(value, str):
        return None

    value = value.strip()
    if not value:
        return None

    # 尝试各种格式
    for fmt in TIMESTAMP_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return None


def get_message_age(filepath, days_threshold):
    """
    确定消息文件的年龄（时间戳）。

    优先级：
      1. JSON 中的时间戳字段（timestamp, acknowledged_at 等）
      2. 文件修改时间（mtime）作为后备方案

    Args:
        filepath: 消息 JSON 文件的绝对路径
        days_threshold: 过期天数阈值

    Returns:
        (msg_datetime, source) 元组:
          - msg_datetime: datetime 对象，消息的时间
          - source: 时间来源字符串 ('json:field_name' 或 'file_mtime')
        如果无法确定时间则返回 (None, None)
    """
    # --- 第一步：尝试从 JSON 内容中提取时间戳 ---
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError):
        # JSON 损坏，降级到文件修改时间
        data = None
    except (IOError, OSError):
        # 文件读取失败
        return None, None

    if isinstance(data, dict):
        for field in TIMESTAMP_FIELDS:
            if field in data:
                ts = parse_timestamp(data[field])
                if ts is not None:
                    return ts, 'json:%s' % field

    # --- 第二步：回退到文件修改时间 ---
    try:
        mtime = os.path.getmtime(filepath)
        return datetime.fromtimestamp(mtime), 'file_mtime'
    except (OSError, ValueError, OverflowError):
        return None, None


def get_file_size(filepath):
    """
    获取文件大小（字节）。读取失败时返回 0。
    """
    try:
        return os.path.getsize(filepath)
    except OSError:
        return 0


def format_size(size_bytes):
    """
    将字节数格式化为可读字符串（B / KB / MB / GB）。
    """
    if size_bytes < 1024:
        return '%d B' % size_bytes
    elif size_bytes < 1024 * 1024:
        return '%.1f KB' % (size_bytes / 1024.0)
    elif size_bytes < 1024 * 1024 * 1024:
        return '%.1f MB' % (size_bytes / (1024.0 * 1024.0))
    else:
        return '%.2f GB' % (size_bytes / (1024.0 * 1024.0 * 1024.0))


def discover_nodes(queue_base):
    """
    发现队列目录下所有包含 inbox 子目录的节点。

    Args:
        queue_base: queue 目录的绝对路径

    Returns:
        排序后的节点名称列表
    """
    nodes = []
    if not os.path.isdir(queue_base):
        return nodes

    for entry in sorted(os.listdir(queue_base)):
        node_path = os.path.join(queue_base, entry)
        inbox_path = os.path.join(node_path, 'inbox')
        if os.path.isdir(node_path) and os.path.isdir(inbox_path):
            nodes.append(entry)

    return nodes


def collect_inbox_messages(inbox_path):
    """
    收集 inbox 目录下所有 .json 消息文件。

    Args:
        inbox_path: inbox 目录的绝对路径

    Returns:
        JSON 文件路径列表
    """
    messages = []
    if not os.path.isdir(inbox_path):
        return messages

    for filename in os.listdir(inbox_path):
        if filename.endswith('.json'):
            filepath = os.path.join(inbox_path, filename)
            if os.path.isfile(filepath):
                messages.append(filepath)

    return messages


def archive_message(filepath, node, archive_base, dry_run=False):
    """
    将消息文件移动到归档目录。

    归档路径格式: {archive_base}/{node}/YYYY-MM/{filename}

    Args:
        filepath: 源消息文件路径
        node: 节点名称
        archive_base: 归档根目录的绝对路径
        dry_run: 若为 True 则只预览不实际移动

    Returns:
        (success, archive_path_or_error) 元组
    """
    # 根据文件时间确定归档月份
    msg_time, _ = get_message_age(filepath, 0)
    if msg_time is None:
        # 无法确定时间时使用当前时间
        msg_time = datetime.now()

    year_month = msg_time.strftime('%Y-%m')
    dest_dir = os.path.join(archive_base, node, year_month)
    filename = os.path.basename(filepath)
    dest_path = os.path.join(dest_dir, filename)

    if dry_run:
        return True, dest_path

    # 确保目标目录存在
    try:
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
    except OSError as e:
        return False, '无法创建归档目录 %s: %s' % (dest_dir, e)

    # 处理文件名冲突（在目标文件名后追加序号）
    if os.path.exists(dest_path):
        base, ext = os.path.splitext(filename)
        counter = 1
        while os.path.exists(dest_path):
            dest_path = os.path.join(dest_dir, '%s_%03d%s' % (base, counter, ext))
            counter += 1

    # 移动文件
    try:
        shutil.move(filepath, dest_path)
        return True, dest_path
    except (OSError, shutil.Error) as e:
        return False, '移动文件失败: %s' % str(e)


# ============================================================
# 主清理逻辑
# ============================================================

def run_cleanup(project_root, days, dry_run):
    """
    执行消息队列清理。

    Args:
        project_root: lobster-network 项目根目录
        days: 过期天数阈值
        dry_run: 是否为预览模式

    Returns:
        包含清理结果的摘要字典
    """
    queue_base = os.path.join(project_root, QUEUE_REL)
    archive_base = os.path.join(project_root, ARCHIVE_REL)
    cutoff = datetime.now() - timedelta(days=days)

    # 结果统计
    results = OrderedDict()  # node -> stats dict
    errors = []
    total_archived = 0
    total_remaining = 0
    total_size_freed = 0
    total_errors = 0

    # 发现所有节点
    nodes = discover_nodes(queue_base)

    if not nodes:
        print('[警告] 在 %s 下未找到任何节点收件箱' % queue_base)
        return results

    print('=' * 60)
    if dry_run:
        print('  Lobster Network 消息队列清理 [预览模式]')
    else:
        print('  Lobster Network 消息队列清理')
    print('=' * 60)
    print('')
    print('  项目根目录: %s' % project_root)
    print('  队列路径:   %s' % queue_base)
    print('  归档路径:   %s' % archive_base)
    print('  过期阈值:   %d 天（截止日期: %s）' % (days, cutoff.strftime('%Y-%m-%d %H:%M:%S')))
    print('  发现节点:   %s' % ', '.join(nodes))
    print('')
    print('-' * 60)

    for node in nodes:
        inbox_path = os.path.join(queue_base, node, 'inbox')
        messages = collect_inbox_messages(inbox_path)

        node_archived = 0
        node_remaining = 0
        node_size_freed = 0
        node_errors = 0

        for filepath in messages:
            filename = os.path.basename(filepath)
            msg_time, source = get_message_age(filepath, days)

            # 无法确定时间的文件：保留不动，记录警告
            if msg_time is None:
                node_remaining += 1
                msg = '[跳过] %s/%s - 无法确定消息时间' % (node, filename)
                errors.append(msg)
                continue

            # 判断是否过期
            if msg_time < cutoff:
                file_size = get_file_size(filepath)
                success, detail = archive_message(filepath, node, archive_base, dry_run)

                if success:
                    node_archived += 1
                    node_size_freed += file_size
                    time_str = msg_time.strftime('%Y-%m-%d %H:%M')
                    prefix = '[预览]' if dry_run else '[归档]'
                    print('  %s %s/%s (%s, 来源: %s)' % (
                        prefix, node, filename, time_str, source
                    ))
                else:
                    node_errors += 1
                    err_msg = '[错误] %s/%s - %s' % (node, filename, detail)
                    errors.append(err_msg)
                    print('  %s' % err_msg)
            else:
                node_remaining += 1

        # 记录该节点的统计
        results[node] = {
            'archived': node_archived,
            'remaining': node_remaining,
            'size_freed': node_size_freed,
            'errors': node_errors,
        }

        total_archived += node_archived
        total_remaining += node_remaining
        total_size_freed += node_size_freed
        total_errors += node_errors

    # ============================================================
    # 输出摘要报告
    # ============================================================
    print('')
    print('-' * 60)
    print('')
    print('  清理摘要报告')
    print('  ' + '=' * 56)
    print('')

    # 表头
    header = '  %-18s %8s %8s %12s %8s' % (
        '节点', '归档数', '剩余数', '释放空间', '错误数'
    )
    print(header)
    print('  ' + '-' * 56)

    # 各节点明细
    for node, stats in results.items():
        line = '  %-18s %8d %8d %12s %8d' % (
            node,
            stats['archived'],
            stats['remaining'],
            format_size(stats['size_freed']),
            stats['errors'],
        )
        print(line)

    # 合计行
    print('  ' + '-' * 56)
    total_line = '  %-18s %8d %8d %12s %8d' % (
        '合计',
        total_archived,
        total_remaining,
        format_size(total_size_freed),
        total_errors,
    )
    print(total_line)

    print('')
    print('  ' + '=' * 56)

    # 错误汇总
    if errors:
        print('')
        print('  异常与警告（共 %d 条）:' % len(errors))
        for err in errors:
            print('    %s' % err)

    # 预览模式提示
    if dry_run:
        print('')
        print('  ** 预览模式 - 未实际移动任何文件 **')
        print('  ** 移除 --dry-run 参数以执行实际清理 **')

    print('')
    print('  完成时间: %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print('')

    return {
        'nodes': results,
        'total_archived': total_archived,
        'total_remaining': total_remaining,
        'total_size_freed': total_size_freed,
        'total_errors': total_errors,
        'errors': errors,
    }


# ============================================================
# 命令行入口
# ============================================================

def main():
    """
    解析命令行参数并启动清理流程。
    """
    parser = argparse.ArgumentParser(
        description='Lobster Network 消息队列清理工具 - 归档过期消息并生成报告',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            '示例:\n'
            '  python3 scripts/message_cleanup.py              # 归档7天前的消息\n'
            '  python3 scripts/message_cleanup.py --dry-run     # 预览模式\n'
            '  python3 scripts/message_cleanup.py --days 30     # 归档30天前的消息\n'
            '  python3 scripts/message_cleanup.py --dry-run --days 14  # 预览14天前的消息\n'
        ),
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        default=False,
        help='预览模式：显示将要归档的消息但不实际移动文件',
    )
    parser.add_argument(
        '--days',
        type=int,
        default=7,
        metavar='N',
        help='消息过期天数阈值，超过该天数的消息将被归档（默认: 7）',
    )

    args = parser.parse_args()

    # 参数校验
    if args.days < 1:
        print('[错误] --days 参数必须大于等于 1')
        sys.exit(1)

    # 自动检测项目根目录
    # 策略: 从脚本所在目录向上查找，直到找到 .shared/messages/queue 目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = None

    # 先尝试脚本所在目录的父目录（scripts/ -> lobster-network/）
    candidate = os.path.dirname(script_dir)
    queue_path = os.path.join(candidate, QUEUE_REL)
    if os.path.isdir(queue_path):
        project_root = candidate
    else:
        # 再尝试当前工作目录
        cwd = os.getcwd()
        queue_path = os.path.join(cwd, QUEUE_REL)
        if os.path.isdir(queue_path):
            project_root = cwd
        else:
            # 从脚本目录逐级向上查找
            check_dir = script_dir
            for _ in range(5):  # 最多向上查5级
                check_dir = os.path.dirname(check_dir)
                queue_path = os.path.join(check_dir, QUEUE_REL)
                if os.path.isdir(queue_path):
                    project_root = check_dir
                    break

    if project_root is None:
        print('[错误] 无法定位项目根目录。')
        print('  请确保在 lobster-network 项目目录下运行此脚本。')
        print('  期望找到: %s' % QUEUE_REL)
        sys.exit(1)

    project_root = os.path.abspath(project_root)

    # 执行清理
    result = run_cleanup(project_root, args.days, args.dry_run)

    # 如果有错误则以非零状态退出
    if result['total_errors'] > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()
