# md-tutorial-export Skill

将 Markdown 教程批量转换为 PDF 并发送给用户。

## 功能

1. 读取指定目录下的所有 `.md` 文件
2. 转换为 HTML
3. 使用 Chrome Headless 生成 PDF
4. 打包为压缩包或直接逐个发送

## 使用方式

### 方式一：压缩包发送
```bash
# 执行转换并打包
node md2pdf.js <input-dir> <output-dir>
cd <output-dir> && zip tutorial-pdf.zip *.pdf
# 通过 message tool 发送压缩包
```

### 方式二：逐个发送
```bash
# 解压后逐个发送 PDF 文件
unzip tutorial-pdf.zip -d pdfs/
# 对每个 PDF 调用 message tool 发送
```

## 依赖

- Node.js
- `marked` npm 包
- Google Chrome (headless 模式)

## 文件结构

```
md-tutorial-export/
├── SKILL.md           # 本文件
├── md2pdf.js          # 转换脚本
└── references/        # 参考资料（可选）
```

## 示例

```bash
cd /home/admin/.openclaw/workspace
node skills/md-tutorial-export/md2pdf.js tutorial-deploy-lobster/ tutorial-deploy-lobster/
```

## 注意事项

- PDF 生成使用 Chrome Headless，确保 `google-chrome` 命令可用
- 中文文件名需要正确处理编码
- 大文件建议压缩包发送，避免消息过长
