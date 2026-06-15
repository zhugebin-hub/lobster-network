# md-tutorial-export

将 Markdown 教程批量转换为 PDF 并打包发送的自动化工具。

## 快速开始

### 一键导出（推荐）

```bash
cd /home/admin/.openclaw/workspace/skills/md-tutorial-export
./export-tutorial.sh ../../tutorial-deploy-lobster/ tutorial-deploy-lobster
```

输出：`tutorial-deploy-lobster-pdf.zip`

### 分步执行

```bash
# 1. MD → HTML
node md2pdf.js <input-dir> <output-dir>

# 2. HTML → PDF (在 output-dir 中执行)
for f in *.html; do
  google-chrome --headless --disable-gpu \
    --print-to-pdf="${f%.html}.pdf" \
    --print-to-pdf-no-header \
    --print-to-pdf-no-footer \
    "file://$(pwd)/$f"
done

# 3. 打包
zip output.zip *.pdf
```

## 依赖

- Node.js v16+
- `marked` npm 包（已内置在 workspace）
- Google Chrome / Chromium

## 输出示例

```
tutorial-deploy-lobster-pdf.zip
├── README-教程总览.pdf
├── L1-10 分钟拥有你的 AI 员工.pdf
├── L2-给你的龙虾办钉钉工牌.pdf
├── L3-教你的龙虾第一个技能.pdf
└── 飞书多维表格模板.pdf
```

## 集成到 OpenClaw

在对话中直接调用：

```
将 <dir> 目录下的教程转换为 PDF 发送给我
```

AI 会自动执行：
1. 调用 `md2pdf.js` 转换
2. 使用 Chrome Headless 生成 PDF
3. 打包并发送

## 自定义样式

编辑 `md2pdf.js` 中的 `<style>` 标签自定义 PDF 样式。

## License

MIT - 信电学院 🦞
