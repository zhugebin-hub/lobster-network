---
name: file-packager
description: 通用文件打包发送技能。支持将多个文件/文件夹打包成 ZIP，并通过消息发送给用户。
---

# 文件打包发送技能

## 技能概述

本技能提供通用的文件打包和发送能力，可将多个文件/文件夹打包成 ZIP 压缩包，并通过消息工具发送给用户。

## 核心功能

1. **多文件打包** - 支持打包多个文件或整个文件夹
2. **智能命名** - 自动生成有意义的压缩包名称
3. **相对路径处理** - 确保打包后路径正确
4. **消息发送** - 通过 `message` 工具发送压缩包给用户
5. **临时清理** - 可选自动清理临时文件

## 使用场景

- 📦 打包项目文件发送给用户
- 📁 整理多个产出物为单一压缩包
- 📤 批量文件传输
- 🗂️ 案例/文档归档

## 工作流程

### 步骤 1：确定要打包的文件

收集需要打包的文件路径列表：

```python
files_to_pack = [
    "/path/to/file1.docx",
    "/path/to/file2.pdf",
    "/path/to/folder/"
]
```

### 步骤 2：执行打包

使用 `pack_file.py` 脚本执行打包：

```bash
python3 scripts/pack_file.py \
  --output "我的项目包.zip" \
  --files file1.docx file2.pdf folder/ \
  --base-dir /path/to/base/
```

### 步骤 3：发送给用户

使用 `message` 工具发送压缩包：

```python
message(
    action="send",
    channel="dingtalk",
    target="用户 ID",
    filePath="/path/to/我的项目包.zip"
)
```

## 脚本说明

### pack_file.py

**功能：** 将多个文件/文件夹打包成 ZIP

**输入参数：**
- `--output` - 输出 ZIP 文件路径
- `--files` - 要打包的文件列表（空格分隔）
- `--base-dir` - 基础目录（可选，用于计算相对路径）
- `--prefix` - 文件名前缀（可选）

**输出：** ZIP 文件路径

**示例：**

```bash
# 简单打包
python3 scripts/pack_file.py \
  --output ./output.zip \
  --files file1.txt file2.txt

# 带基础目录打包（保持相对路径结构）
python3 scripts/pack_file.py \
  --output ./project.zip \
  --files docs/ src/ README.md \
  --base-dir /home/admin/workspace/myproject
```

## 使用示例

### 示例 1：打包单个文件

**用户输入：**
> 把这个文档打包发给我

**技能响应：**
```bash
python3 scripts/pack_file.py \
  --output "文档包_20260411.zip" \
  --files /home/admin/.openclaw/workspace/document.docx
```

然后发送：
```python
message(action="send", filePath="文档包_20260411.zip", target="用户 ID")
```

### 示例 2：打包多个文件

**用户输入：**
> 把这三个文件打包成一个 ZIP

**技能响应：**
```bash
python3 scripts/pack_file.py \
  --output "项目文件包.zip" \
  --files file1.pdf file2.docx image.png
```

### 示例 3：打包整个文件夹

**用户输入：**
> 把这个项目文件夹打包发给我

**技能响应：**
```bash
python3 scripts/pack_file.py \
  --output "myproject_20260411.zip" \
  --files myproject/ \
  --base-dir /home/admin/.openclaw/workspace/
```

### 示例 4：智能命名

**用户输入：**
> 打包第 5 周的作业文件

**技能响应：**
```bash
python3 scripts/pack_file.py \
  --output "week5_homework_20260411.zip" \
  --files week5/*.pdf week5/*.docx
```

## 文件命名规范

### 默认命名

```
{前缀}_{YYYYMMDD}.zip

示例：
- package_20260411.zip
- project_20260411.zip
```

### 智能命名

根据内容自动生成有意义的名称：

```
{描述}_{YYYYMMDD}.zip

示例：
- 教学案例_20260411.zip
- 项目文档_20260411.zip
- week5_homework_20260411.zip
```

## 路径处理

### 相对路径打包

当使用 `--base-dir` 参数时，脚本会保持相对路径结构：

```
源结构：
/workspace/project/
├── docs/
│   └── readme.md
├── src/
│   └── main.py
└── README.md

打包后 ZIP 结构：
project.zip
├── docs/
│   └── readme.md
├── src/
│   └── main.py
└── README.md
```

### 绝对路径处理

如果不使用 `--base-dir`，文件会以完整路径打包（不推荐）：

```bash
# ❌ 不推荐 - 会包含完整路径
python3 scripts/pack_file.py \
  --output output.zip \
  --files /home/admin/workspace/file.txt

# ✅ 推荐 - 使用相对路径
cd /home/admin/workspace/
python3 scripts/pack_file.py \
  --output output.zip \
  --files file.txt \
  --base-dir /home/admin/workspace/
```

## 错误处理

### 常见错误及解决方案

| 错误 | 原因 | 解决方案 |
|------|------|---------|
| `zip command not found` | 未安装 zip 工具 | `sudo apt install zip` |
| `file not found` | 文件路径错误 | 检查文件是否存在 |
| `permission denied` | 权限不足 | 检查文件读取权限 |
| `disk full` | 磁盘空间不足 | 清理空间或压缩单个文件 |

## 质量检查清单

打包前检查：

- [ ] 所有文件路径正确
- [ ] 文件存在且可读
- [ ] 输出目录可写
- [ ] 压缩包名称有意义
- [ ] 临时文件会清理

发送前检查：

- [ ] ZIP 文件已生成
- [ ] ZIP 文件大小合理
- [ ] 目标用户 ID 正确
- [ ] 消息通道正确

## 相关技能

- **dingtalk-case-export** - 钉钉聊天记录导出为教学案例（使用本技能打包）
- **dingtalk-file-transfer-enhance** - 增强钉钉文件传输能力

## 注意事项

1. **文件大小限制** - 注意消息平台的大小限制（钉钉通常 100MB）
2. **隐私保护** - 打包前检查是否包含敏感信息
3. **临时清理** - 发送后清理临时 ZIP 文件，避免占用空间
4. **路径安全** - 使用相对路径，避免绝对路径泄露

## 脚本实现

### pack_file.py 核心代码

```python
#!/usr/bin/env python3
"""
文件打包脚本
将多个文件/文件夹打包成 ZIP
"""

import os
import sys
import zipfile
import argparse
from datetime import datetime
from pathlib import Path

def pack_files(output_path, files, base_dir=None, prefix=None):
    """
    打包文件到 ZIP
    
    Args:
        output_path: 输出 ZIP 路径
        files: 文件列表
        base_dir: 基础目录（用于计算相对路径）
        prefix: 文件名前缀
    """
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    
    # 创建 ZIP 文件
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file_path in files:
            if not os.path.exists(file_path):
                print(f"警告：文件不存在 {file_path}", file=sys.stderr)
                continue
            
            # 计算相对路径
            if base_dir:
                arcname = os.path.relpath(file_path, base_dir)
            else:
                arcname = os.path.basename(file_path)
            
            # 添加到 ZIP
            if os.path.isfile(file_path):
                zipf.write(file_path, arcname)
            elif os.path.isdir(file_path):
                for root, dirs, files_in_dir in os.walk(file_path):
                    for file_in_dir in files_in_dir:
                        full_path = os.path.join(root, file_in_dir)
                        rel_path = os.path.relpath(full_path, base_dir or file_path)
                        zipf.write(full_path, rel_path)
    
    return output_path

def generate_output_name(prefix=None, files=None):
    """生成输出文件名"""
    date_str = datetime.now().strftime('%Y%m%d')
    
    if prefix:
        return f"{prefix}_{date_str}.zip"
    
    # 根据文件内容智能生成
    if files:
        # 取第一个文件名作为前缀
        first_file = os.path.basename(files[0])
        name = os.path.splitext(first_file)[0]
        return f"{name}_package_{date_str}.zip"
    
    return f"package_{date_str}.zip"

def main():
    parser = argparse.ArgumentParser(description='文件打包工具')
    parser.add_argument('--output', '-o', help='输出 ZIP 路径')
    parser.add_argument('--files', '-f', nargs='+', help='要打包的文件列表')
    parser.add_argument('--base-dir', '-b', help='基础目录')
    parser.add_argument('--prefix', '-p', help='文件名前缀')
    
    args = parser.parse_args()
    
    # 生成输出路径
    output_path = args.output or generate_output_name(args.prefix, args.files)
    
    # 执行打包
    pack_files(output_path, args.files, args.base_dir)
    
    print(f"✅ 打包完成：{output_path}")
    return output_path

if __name__ == '__main__':
    main()
```

## 版本历史

### v1.0.0 (2026-04-11)
- 初始版本
- 支持多文件打包
- 支持文件夹打包
- 智能文件命名
- 相对路径处理

## 待开发功能

- [ ] 压缩级别配置
- [ ] 密码保护
- [ ] 分卷压缩（大文件）
- [ ] 进度显示
- [ ] 断点续传支持
