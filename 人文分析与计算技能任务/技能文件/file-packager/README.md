# 📦 file-packager - 文件打包发送技能

> 通用文件打包技能，让 OpenClaw 智能体能够将多个文件/文件夹打包成 ZIP 并发送给用户

## 快速开始

### 安装

```bash
# 克隆或复制到 skills 目录
cp -r file-packager ~/.openclaw/workspace/skills/

# 验证安装
ls ~/.openclaw/workspace/skills/file-packager/
```

### 依赖

- Python 3.8+
- zip 工具（通常系统自带）

```bash
# Ubuntu/Debian
sudo apt install zip

# macOS
brew install zip

# CentOS/RHEL
sudo yum install zip
```

## 使用方法

### 在技能中调用

```python
# 打包文件
exec_command = """
python3 ~/.openclaw/workspace/skills/file-packager/scripts/pack_file.py \\
  --output "我的项目包.zip" \\
  --files file1.docx file2.pdf folder/ \\
  --base-dir /home/admin/.openclaw/workspace/
"""

# 发送给用户
message(action="send", filePath="我的项目包.zip", target="用户 ID")
```

### 命令行使用

```bash
# 简单打包
python3 scripts/pack_file.py --output output.zip --files file1.txt file2.txt

# 带基础目录打包（保持相对路径）
python3 scripts/pack_file.py \\
  --output project.zip \\
  --files docs/ src/ README.md \\
  --base-dir /home/admin/workspace/myproject

# 自动命名
python3 scripts/pack_file.py --files myfile.pdf --prefix myproject
```

## 功能特性

- ✅ 多文件打包
- ✅ 文件夹递归打包
- ✅ 相对路径处理
- ✅ 智能文件命名
- ✅ 压缩统计信息
- ✅ 错误处理和验证

## 参数说明

| 参数 | 简写 | 说明 | 必填 |
|------|------|------|------|
| `--output` | `-o` | 输出 ZIP 文件路径 | 否（可自动命名） |
| `--files` | `-f` | 要打包的文件列表 | 是 |
| `--base-dir` | `-b` | 基础目录（用于相对路径） | 否 |
| `--prefix` | `-p` | 文件名前缀 | 否 |
| `--dir` | `-d` | 输出目录 | 否（默认当前目录） |
| `--no-compress` | | 不压缩（仅存储） | 否 |
| `--verbose` | `-v` | 详细输出 | 否 |

## 示例场景

### 场景 1：打包文档

```bash
python3 scripts/pack_file.py \\
  --output "docs_20260411.zip" \\
  --files report.docx presentation.pptx data.xlsx
```

### 场景 2：打包项目

```bash
cd /home/admin/projects/myapp
python3 scripts/pack_file.py \\
  --output myapp_backup.zip \\
  --files src/ tests/ README.md package.json \\
  --base-dir /home/admin/projects/myapp
```

### 场景 3：自动命名

```bash
python3 scripts/pack_file.py \\
  --files weekly_report.pdf \\
  --prefix weekly_report
# 输出：weekly_report_20260411.zip
```

## 输出示例

```
✓ report.docx
✓ presentation.pptx
✓ data.xlsx
✓ docs/readme.md
✓ src/main.py

✅ 打包完成：myproject.zip
   文件数：15
   原始大小：2.34 MB
   压缩后：1.87 MB
   压缩率：20.1%

📦 压缩包已生成：/home/admin/workspace/myproject.zip
```

## 注意事项

1. **文件大小** - 注意消息平台的大小限制
2. **路径安全** - 使用相对路径避免泄露系统信息
3. **临时清理** - 发送后清理临时文件
4. **隐私保护** - 打包前检查敏感信息

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 相关链接

- [OpenClaw 文档](https://docs.openclaw.ai)
- [技能商店](https://clawhub.com)
