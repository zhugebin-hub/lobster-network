#!/usr/bin/env python3
"""
文件打包脚本 - File Packager Script
将多个文件/文件夹打包成 ZIP，支持相对路径处理

使用示例：
    python3 pack_file.py --output mypackage.zip --files file1.txt file2.txt
    python3 pack_file.py --output project.zip --files docs/ src/ --base-dir /path/to/project
"""

import os
import sys
import zipfile
import argparse
from datetime import datetime
from pathlib import Path


def pack_files(output_path, files, base_dir=None, prefix=None, compression=zipfile.ZIP_DEFLATED):
    """
    打包文件到 ZIP
    
    Args:
        output_path: 输出 ZIP 路径
        files: 文件列表
        base_dir: 基础目录（用于计算相对路径）
        prefix: 文件名前缀
        compression: 压缩方式（默认 ZIP_DEFLATED）
    
    Returns:
        str: 输出的 ZIP 文件路径
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # 统计信息
    total_files = 0
    total_size = 0
    
    # 创建 ZIP 文件
    with zipfile.ZipFile(output_path, 'w', compression) as zipf:
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"⚠️  警告：文件不存在 {file_path}", file=sys.stderr)
                continue
            
            # 计算相对路径
            if base_dir:
                arcname = os.path.relpath(file_path, base_dir)
            else:
                arcname = os.path.basename(file_path)
            
            # 添加到 ZIP
            if os.path.isfile(file_path):
                zipf.write(file_path, arcname)
                total_files += 1
                total_size += os.path.getsize(file_path)
                print(f"  ✓ {arcname}")
            elif os.path.isdir(file_path):
                dir_name = os.path.basename(file_path.rstrip('/'))
                for root, dirs, filenames in os.walk(file_path):
                    # 跳过隐藏目录
                    dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for filename in filenames:
                        if filename.startswith('.'):
                            continue
                        
                        full_path = os.path.join(root, filename)
                        
                        # 计算在 ZIP 中的相对路径
                        if base_dir:
                            rel_path = os.path.relpath(full_path, base_dir)
                        else:
                            rel_path = os.path.join(dir_name, os.path.relpath(full_path, file_path))
                        
                        zipf.write(full_path, rel_path)
                        total_files += 1
                        total_size += os.path.getsize(full_path)
                        print(f"  ✓ {rel_path}")
    
    # 输出统计
    compressed_size = os.path.getsize(output_path)
    ratio = (1 - compressed_size / total_size) * 100 if total_size > 0 else 0
    
    print(f"\n✅ 打包完成：{output_path}")
    print(f"   文件数：{total_files}")
    print(f"   原始大小：{format_size(total_size)}")
    print(f"   压缩后：{format_size(compressed_size)}")
    print(f"   压缩率：{ratio:.1f}%")
    
    return output_path


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def generate_output_name(prefix=None, files=None, output_dir='.'):
    """生成输出文件名"""
    date_str = datetime.now().strftime('%Y%m%d')
    time_str = datetime.now().strftime('%H%M%S')
    
    if prefix:
        filename = f"{prefix}_{date_str}.zip"
    elif files:
        # 根据文件内容智能生成
        first_file = os.path.basename(files[0].rstrip('/'))
        name = os.path.splitext(first_file)[0]
        # 清理文件名中的非法字符
        name = ''.join(c for c in name if c.isalnum() or c in '-_')
        filename = f"{name}_package_{date_str}.zip"
    else:
        filename = f"package_{date_str}.zip"
    
    return os.path.join(output_dir, filename)


def validate_files(files):
    """验证文件列表"""
    valid_files = []
    for f in files:
        if os.path.exists(f):
            valid_files.append(f)
        else:
            print(f"⚠️  警告：文件不存在 {f}", file=sys.stderr)
    return valid_files


def main():
    parser = argparse.ArgumentParser(
        description='文件打包工具 - 将多个文件/文件夹打包成 ZIP',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 简单打包
  python3 pack_file.py --output output.zip --files file1.txt file2.txt
  
  # 带基础目录打包（保持相对路径结构）
  python3 pack_file.py --output project.zip --files docs/ src/ README.md --base-dir /path/to/project
  
  # 自动命名
  python3 pack_file.py --files myfile.pdf --prefix myproject
        """
    )
    
    parser.add_argument('--output', '-o', help='输出 ZIP 文件路径')
    parser.add_argument('--files', '-f', nargs='+', required=True, help='要打包的文件列表')
    parser.add_argument('--base-dir', '-b', help='基础目录（用于计算相对路径）')
    parser.add_argument('--prefix', '-p', help='文件名前缀（用于自动生成输出名）')
    parser.add_argument('--dir', '-d', default='.', help='输出目录（默认当前目录）')
    parser.add_argument('--no-compress', action='store_true', help='不压缩（仅存储）')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    # 验证文件
    valid_files = validate_files(args.files)
    if not valid_files:
        print("❌ 错误：没有有效的文件可打包", file=sys.stderr)
        sys.exit(1)
    
    # 确定压缩方式
    compression = zipfile.ZIP_STORED if args.no_compress else zipfile.ZIP_DEFLATED
    
    # 生成输出路径
    if args.output:
        output_path = args.output
    else:
        output_path = generate_output_name(args.prefix, valid_files, args.dir)
    
    # 确定基础目录
    base_dir = args.base_dir
    if not base_dir and len(valid_files) > 1:
        # 自动计算共同父目录
        common_path = os.path.commonpath([os.path.abspath(f) for f in valid_files if os.path.isfile(f)])
        base_dir = os.path.dirname(common_path) if os.path.isfile(common_path) else common_path
    
    # 执行打包
    try:
        pack_files(output_path, valid_files, base_dir, args.prefix, compression)
        print(f"\n📦 压缩包已生成：{os.path.abspath(output_path)}")
        return 0
    except Exception as e:
        print(f"❌ 错误：{e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
