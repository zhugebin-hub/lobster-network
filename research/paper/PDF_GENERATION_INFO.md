# 论文 PDF 生成说明

**创建时间**：2026-03-28 11:45  
**状态**：⚠️ 需要 LaTeX 环境

---

## 📄 当前可用版本

| 格式 | 文件 | 状态 |
|------|------|------|
| **Markdown** | `paper_draft_v1.md` | ✅ 可用 |
| **LaTeX** | `paper_v1.tex` | ✅ 可用 |
| **HTML** | `paper_draft_v1.html` | ✅ 可用 |
| **PDF** | `paper_draft_v1.pdf` | ⚠️ 需要生成 |

---

## 🔧 PDF 生成方法

### 方法 1：使用 LaTeX（推荐）

```bash
cd /home/admin/.openclaw/workspace/research/paper

# 安装 LaTeX（如果未安装）
# Ubuntu/Debian:
sudo apt-get install texlive-latex-base texlive-latex-extra texlive-fonts-recommended

# macOS:
brew install mactex

# 编译 PDF
pdflatex paper_v1.tex
bibtex paper_v1
pdflatex paper_v1.tex
pdflatex paper_v1.tex
```

输出：`paper_v1.pdf`

### 方法 2：使用 Overleaf（在线）

1. 访问 https://www.overleaf.com
2. 创建新项目
3. 上传 `paper_v1.tex` 和 `references.bib`
4. 点击 "Recompile" 生成 PDF

### 方法 3：使用 Pandoc（简化版）

```bash
# 安装 pandoc 和 LaTeX 引擎
brew install pandoc mactex  # macOS
sudo apt-get install pandoc texlive  # Linux

# 从 Markdown 生成
pandoc paper_draft_v1.md -o paper_draft_v1.pdf --pdf-engine=xelatex
```

### 方法 4：从 HTML 打印（最简单）

1. 用浏览器打开 `paper_draft_v1.html`
2. Ctrl+P (或 Cmd+P) 打印
3. 选择"另存为 PDF"
4. 保存

---

## 📊 论文内容概览

**标题**：Time-Arbitrage Scheduling for Heterogeneous Cloud Computing

**长度**：
- 字数：~6,500 词
- 页数：~9 页（双栏 LaTeX 格式）
- 图表：8 个

**章节**：
1. Introduction
2. Related Work
3. System Model
4. Scheduler Design
5. Evaluation
6. Conclusion
7. References (25 篇)

---

## 🎯 快速预览

如需快速查看论文内容：

```bash
# 查看 Markdown 版
cat /home/admin/.openclaw/workspace/research/paper/paper_draft_v1.md

# 或查看 HTML 版（浏览器打开）
open /home/admin/.openclaw/workspace/research/paper/paper_draft_v1.html
```

---

## 💡 建议

**如果您需要 PDF 版本**：

1. **最简单**：使用 Overleaf 在线编译
2. **最快速**：从 HTML 打印为 PDF
3. **最正式**：安装 LaTeX 本地编译

**我可以帮您**：
- 提供 LaTeX 编译命令
- 优化论文格式
- 生成更多预览版本

---

*当前时间：2026-03-28 11:45*  
*需要帮助请告诉我！*
