#!/usr/bin/env python3
"""
Markdown to DOCX 转换脚本
使用 pandoc 将 Markdown 文件转换为 Word 文档
"""

import argparse
import subprocess
import sys
from pathlib import Path


def check_pandoc():
    """检查 pandoc 是否已安装"""
    try:
        result = subprocess.run(
            ["pandoc", "--version"],
            capture_output=True,
            text=True,
            check=True
        )
        return True, result.stdout.split('\n')[0]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False, "pandoc 未安装"


def convert_md_to_docx(
    input_file: str,
    output_file: str = None,
    title: str = None,
    author: str = None,
    date: str = None,
    reference_doc: str = None,
    verbose: bool = False
):
    """
    将 Markdown 转换为 DOCX
    
    Args:
        input_file: 输入 Markdown 文件路径
        output_file: 输出 DOCX 文件路径（可选，默认与输入文件同名）
        title: 文档标题
        author: 作者名
        date: 日期
        reference_doc: 参考文档模板路径
        verbose: 是否显示详细信息
    """
    input_path = Path(input_file)
    
    if not input_path.exists():
        print(f"错误：输入文件不存在：{input_file}", file=sys.stderr)
        return False
    
    # 生成输出文件名
    if output_file is None:
        output_file = str(input_path.with_suffix('.docx'))
    
    # 构建 pandoc 命令
    cmd = ["pandoc", str(input_path), "-o", output_file]
    
    # 添加元数据
    metadata = []
    if title:
        metadata.append(("title", title))
    if author:
        metadata.append(("author", author))
    if date:
        metadata.append(("date", date))
    
    for key, value in metadata:
        cmd.extend(["--metadata", f"{key}={value}"])
    
    # 添加参考文档
    if reference_doc:
        cmd.extend(["--reference-doc", reference_doc])
    
    if verbose:
        print(f"执行命令：{' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        if verbose:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
        
        # 验证输出文件
        output_path = Path(output_file)
        if output_path.exists():
            size_kb = output_path.stat().st_size / 1024
            print(f"✓ 转换成功：{output_file} ({size_kb:.1f} KB)")
            return True
        else:
            print(f"错误：输出文件未创建：{output_file}", file=sys.stderr)
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"错误：转换失败", file=sys.stderr)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        return False
    except Exception as e:
        print(f"错误：{e}", file=sys.stderr)
        return False


def batch_convert(
    input_files: list,
    output_dir: str = None,
    title: str = None,
    author: str = None,
    date: str = None,
    verbose: bool = False
):
    """
    批量转换多个 Markdown 文件
    
    Args:
        input_files: 输入文件列表
        output_dir: 输出目录（可选）
        title: 文档标题
        author: 作者名
        date: 日期
        verbose: 是否显示详细信息
    """
    success_count = 0
    fail_count = 0
    
    for input_file in input_files:
        input_path = Path(input_file)
        
        if output_dir:
            output_path = Path(output_dir) / input_path.with_suffix('.docx').name
            Path(output_dir).mkdir(parents=True, exist_ok=True)
        else:
            output_path = input_path.with_suffix('.docx')
        
        if convert_md_to_docx(
            str(input_path),
            str(output_path),
            title=title,
            author=author,
            date=date,
            verbose=verbose
        ):
            success_count += 1
        else:
            fail_count += 1
    
    print(f"\n转换完成：成功 {success_count} 个，失败 {fail_count} 个")
    return fail_count == 0


def main():
    parser = argparse.ArgumentParser(
        description="Markdown to DOCX 转换器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s input.md                          # 基本转换
  %(prog)s input.md -o output.docx           # 指定输出文件
  %(prog)s input.md --title "标题"           # 添加标题
  %(prog)s input.md --author "作者"          # 添加作者
  %(prog)s *.md --output-dir ./docx/         # 批量转换
        """
    )
    
    parser.add_argument(
        "input",
        nargs="*",
        help="输入 Markdown 文件（支持多个文件进行批量转换）"
    )
    
    parser.add_argument(
        "-o", "--output",
        help="输出 DOCX 文件路径（批量转换时使用 --output-dir）"
    )
    
    parser.add_argument(
        "--output-dir",
        help="批量转换时的输出目录"
    )
    
    parser.add_argument(
        "--title",
        help="文档标题"
    )
    
    parser.add_argument(
        "--author",
        help="作者名"
    )
    
    parser.add_argument(
        "--date",
        help="日期（格式：YYYY-MM-DD）"
    )
    
    parser.add_argument(
        "--reference-doc",
        help="参考文档模板（.docx 格式）"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="显示详细信息"
    )
    
    parser.add_argument(
        "--check",
        action="store_true",
        help="仅检查 pandoc 是否安装"
    )
    
    args = parser.parse_args()
    
    # 检查 pandoc
    has_pandoc, version_info = check_pandoc()
    
    if args.check:
        if has_pandoc:
            print(f"✓ pandoc 已安装：{version_info}")
            sys.exit(0)
        else:
            print(f"✗ {version_info}", file=sys.stderr)
            print("\n安装方法:", file=sys.stderr)
            print("  macOS:  brew install pandoc", file=sys.stderr)
            print("  Linux: sudo apt install pandoc", file=sys.stderr)
            print("  Windows: 从 https://pandoc.org 下载安装", file=sys.stderr)
            sys.exit(1)
    
    if not has_pandoc:
        print(f"错误：{version_info}", file=sys.stderr)
        sys.exit(1)
    
    if args.verbose:
        print(f"使用 {version_info}")
    
    # 执行转换
    if len(args.input) > 1 or args.output_dir:
        # 批量转换
        success = batch_convert(
            args.input,
            output_dir=args.output_dir,
            title=args.title,
            author=args.author,
            date=args.date,
            verbose=args.verbose
        )
    else:
        # 单个文件转换
        success = convert_md_to_docx(
            args.input[0],
            output_file=args.output,
            title=args.title,
            author=args.author,
            date=args.date,
            reference_doc=args.reference_doc,
            verbose=args.verbose
        )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
