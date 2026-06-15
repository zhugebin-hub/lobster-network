# Resume Generator · 简历生成技能

🦞 **小龙虾风格简历生成器** - 将用户经历快速转化为专业且有个性的简历

## 触发场景

当用户说：
- "帮我生成简历"
- "做个简历"
- "简历模板"
- "小龙虾风格简历"
- "把我的经历做成简历"

## 核心能力

### 🎨 多风格支持
- **小龙虾风格** - 活泼有趣，适合 AI/创意行业
- **极简专业** - 传统商务风格
- **科技极客** - 程序员/技术岗位
- **学术风格** - 科研/教育岗位

### 📋 内容优化
- 自动提取用户经历信息
- CAR 法则优化描述（Context-Action-Result）
- 关键词优化（ATS 友好）
- 量化成就展示

### 📄 输出格式
- HTML 版本（可预览/打印）
- PDF 版本（正式提交）
- Markdown 版本（快速编辑）

## 使用流程

### 1️⃣ 收集信息
```markdown
请提供以下信息：
- 姓名/联系方式
- 教育背景（学校/专业/学历/时间）
- 工作/项目经历
- 技能列表
- 荣誉奖项
- 目标岗位/行业
```

### 2️⃣ 选择风格
```markdown
可选风格：
- 🦞 小龙虾风格（活泼创意）
- 💼 极简专业（传统商务）
- 💻 科技极客（技术岗位）
- 📚 学术风格（科研教育）
```

### 3️⃣ 生成预览
- 生成 HTML 版本供预览
- 用户确认内容无误

### 4️⃣ 导出 PDF
- 使用 Chrome 无头模式生成 PDF
- 发送给用户

## 文件结构

```
skills/resume-generator/
├── SKILL.md                 # 技能说明
├── templates/
│   ├── lobster.html         # 小龙虾风格模板
│   ├── minimal.html         # 极简专业模板
│   ├── tech.html            # 科技极客模板
│   └── academic.html        # 学术风格模板
└── scripts/
    └── generate.sh          # 生成脚本
```

## 模板变量

所有模板支持以下变量（使用 `{{variable}}` 格式）：

- `{{name}}` - 姓名
- `{{title}}` - 标题/定位
- `{{contact_email}}` - 邮箱
- `{{contact_phone}}` - 手机
- `{{contact_website}}` - 网站/作品集
- `{{summary}}` - 个人总结
- `{{education}}` - 教育背景（数组）
- `{{experience}}` - 工作经历（数组）
- `{{projects}}` - 项目经历（数组）
- `{{skills}}` - 技能列表（数组）
- `{{awards}}` - 荣誉奖项（数组）
- `{{style}}` - 风格标识

## 示例调用

### 快速生成（小龙虾风格）
```bash
./scripts/generate.sh --style lobster --input user-data.json --output resume.pdf
```

### 自定义模板
```bash
./scripts/generate.sh --template custom.html --input user-data.json --output resume.html
```

## 最佳实践

### ✅ 内容优化
- 使用动词开头（主导/开发/优化/提升）
- 量化成果（提升 30%/服务 1000+ 用户）
- 突出关键词（岗位 JD 中的核心技能）
- 保持简洁（每段经历 3-5 个 bullet points）

### ✅ 视觉设计
- 保持一页（除非 10+ 年经验）
- 留白充足（便于阅读）
- 字体统一（最多 2 种字体）
- 颜色协调（主色 + 辅色不超过 3 种）

### ✅ ATS 友好
- 使用标准章节标题（Experience/Education/Skills）
- 避免图片/表格（影响解析）
- 包含岗位关键词
- 使用标准日期格式（YYYY-MM）

## 注意事项

- PDF 生成需要 Chrome/Chromium
- 首次使用需安装依赖（pandoc 可选）
- 中文需要合适字体支持
- 建议先预览 HTML 再导出 PDF

## 更新日志

- **v1.0.0** (2026-04-15) - 初始版本，支持小龙虾风格
  - 🦞 小龙虾主题模板
  - 📄 HTML + PDF 双输出
  - 🎨 渐变配色 + 动画效果
  - 📋 CAR 法则内容优化

## 相关文件

- 模板文件：`/home/admin/.openclaw/workspace/skills/resume-generator/templates/`
- 示例简历：`/home/admin/.openclaw/workspace/resume-cjy-lobster.html`
- 输出目录：`/home/admin/.openclaw/workspace/`
