---
name: resume-builder-pro
description: 专业简历生成与优化技能。基于 ClawHub 多个简历技能最佳实践，提供 ATS 友好的中英文简历生成、美化、导出 PDF 一站式服务。适用于：快速生成专业简历、多模板选择、ATS 优化、批量导出。
metadata:
  openclaw:
    emoji: "📄"
    category: "productivity"
    tags: ["resume", "cv", "pdf", "ats", "career", "job"]
---

# Resume Builder Pro - 专业简历生成器

基于 ClawHub 多个简历技能（`resume-helper`、`cv`、`resume-generator-cn`、`resume-optimizer`）最佳实践沉淀而成的专业简历生成工具。

## 核心能力

1. **📄 简历生成** - 从用户信息生成专业简历
2. **✨ ATS 优化** - 符合 ATS 系统筛选标准
3. **🎨 多模板** - 支持多种风格模板
4. **📥 PDF 导出** - 一键生成可下载 PDF
5. **🔍 简历分析** - 提供改进建议

## 快速开始

### 基础用法

```bash
# 交互式生成简历
./scripts/generate-resume.sh

# 从 Markdown 生成 PDF
./scripts/export-pdf.sh resume.md

# 使用指定模板
./scripts/generate-resume.sh --template professional
```

### 技能触发词

用户说以下内容时触发此技能：
- "帮我生成简历"
- "美化简历"
- "导出简历 PDF"
- "优化简历"
- "简历模板"

## 工作流程

### 1. 收集信息

```markdown
必填信息：
- 姓名
- 联系方式（邮箱/电话/地址）
- 教育背景
- 工作/项目经历
- 技能列表

选填信息：
- 求职意向
- 个人网站/GitHub
- 获奖记录
- 证书/语言
```

### 2. 选择模板

| 模板名 | 风格 | 适用场景 |
|--------|------|----------|
| `professional` | 专业蓝白 | 大厂投递、国企 |
| `minimal` | 极简黑白 | 外企、咨询公司 |
| `tech` | 科技渐变 | 互联网公司、创业公司 |
| `academic` | 学术风格 | 科研岗位、博士申请 |

### 3. 内容优化（CAR 公式）

```markdown
❌ 负责开发智能体系统
✅ 设计并开发教育智能体系统，推动学院教学管理数字化转型

❌ 帮助提升销售额
✅ 通过自动化线索评分系统，提升企业销售额 34%（同比增长）

❌ 做了个会议室预约系统
✅ 开发会议室预约智能体，减少人工协调时间 60%
```

### 4. ATS 检查清单

```bash
./scripts/ats-check.sh resume.md

检查项：
□ 标准章节标题
□ 无表格/分栏
□ 关键词密度合理
□ 标准字体
□ 可解析 PDF
```

### 5. 导出 PDF

```bash
./scripts/export-pdf.sh \
  --input resume.html \
  --output 姓名_简历.pdf \
  --format A4
```

## 模板系统

### Professional（专业蓝白）

```html
<style>
/* 蓝色主调，适合大多数正式场合 */
.header { border-bottom: 2px solid #1a56db; }
.section-title { color: #1a56db; }
</style>
```

### Minimal（极简黑白）

```html
<style>
/* 纯黑白，外企最爱 */
body { color: #000; }
.header { border-bottom: 1px solid #000; }
</style>
```

### Tech（科技渐变）

```html
<style>
/* 紫蓝渐变，科技公司偏好 */
.header {
  background: linear-gradient(135deg, #667eea, #764ba2);
}
</style>
```

### Academic（学术风格）

```html
<style>
/* 类似论文排版，科研岗位适用 */
body {
  font-family: 'Times New Roman', serif;
  line-height: 1.8;
}
</style>
```

## 脚本工具

### generate-resume.sh

```bash
#!/bin/bash
# 交互式简历生成

TEMPLATE=${1:-professional}
OUTPUT_NAME=${2:-resume}

echo "选择模板：$TEMPLATE"
echo "生成简历：$OUTPUT_NAME.html"

# 调用 AI 生成内容
# 渲染 HTML 模板
# 输出到 workspace/resumes/
```

### export-pdf.sh

```bash
#!/bin/bash
# HTML 转 PDF（使用 Puppeteer）

INPUT=$1
OUTPUT=$2

node scripts/convert-to-pdf.js \
  --input "$INPUT" \
  --output "$OUTPUT"
```

### ats-check.sh

```bash
#!/bin/bash
# ATS 兼容性检查

RESUME=$1

# 检查章节标题
# 检查关键词密度
# 检查格式问题
# 输出报告
```

### optimize-resume.sh

```bash
#!/bin/bash
# 基于 JD 优化简历

RESUME=$1
JD=$2

# 提取 JD 关键词
# 对比简历关键词
# 生成优化建议
# 自动补充缺失关键词
```

## 最佳实践

### ✅ 推荐做法

1. **量化成果** - 每条经历尽量包含数字
2. **动词开头** - 使用主动语态（设计、开发、领导）
3. **关键词匹配** - 根据 JD 调整技能描述
4. **一页原则** - 5 年以下经验控制在 1 页
5. **PDF 命名** - `姓名_岗位_简历.pdf`

### ❌ 避免事项

1. 照片（除非明确要求）
2. 表格/分栏布局
3. 创意章节标题
4. 第一人称代词（"我"）
5. 错别字和语法错误

## 文件结构

```
resume-builder-pro/
├── SKILL.md
├── scripts/
│   ├── generate-resume.sh
│   ├── export-pdf.sh
│   ├── ats-check.sh
│   └── optimize-resume.sh
├── templates/
│   ├── professional.html
│   ├── minimal.html
│   ├── tech.html
│   └── academic.html
├── examples/
│   └── sample-resume.md
└── references/
    ├── best-practices.md
    ├── ats-optimization.md
    └── templates-guide.md
```

## 输出规范

### 文件命名

```
[姓名]_[岗位]_[类型].pdf
例：陈俊烨_AI 工程师_简历.pdf
```

### 保存位置

```
/home/admin/.openclaw/workspace/resumes/
```

### 发送方式

```javascript
// 通过 message 工具发送到群聊/私聊
message.send({
  target: "chat_id",
  path: "/path/to/resume.pdf",
  filename: "姓名_简历.pdf"
})
```

## 示例输出

### 输入（用户信息）

```markdown
姓名：陈俊烨
学校：浙江工商大学 人工智能学院（硕士）
项目：未来课堂智能体、小龙虾课程项目
获奖：GDPS 黑客松一等奖、商汤龙虾节二等奖
```

### 输出（简历 HTML）

```html
<!DOCTYPE html>
<html>
<head>
  <title>陈俊烨 - 简历</title>
  <style>/* 专业蓝白风格 */</style>
</head>
<body>
  <div class="header">
    <h1>陈俊烨 (CJY)</h1>
    <div class="title">AI 教育系统数字化工程师</div>
  </div>
  <!-- 教育背景、项目经历、获奖记录... -->
</body>
</html>
```

### 输出（PDF）

```
📄 陈俊烨_简历_专业版.pdf
- A4 尺寸
- 可文本选择
- ATS 友好格式
```

## 依赖安装

```bash
# Node.js 依赖
npm install puppeteer marked

# 系统依赖（可选）
apt-get install -y chromium-browser
```

## 版本历史

- **v1.0.0** (2026-04-15) - 初始版本，基于 ClawHub 多技能最佳实践沉淀

## 参考资源

- [ClawHub resume-helper](https://clawhub.com/beikeliu/resume-helper)
- [ClawHub cv](https://clawhub.com/ivangdavila/cv)
- [ClawHub resume-optimizer](https://clawhub.com/tomstools11/resume-optimizer)
- [ATS Optimization Guide](references/ats-optimization.md)

---

*本技能由 信电大虾 🦞 于 2026-04-15 沉淀自 ClawHub 多技能最佳实践*
