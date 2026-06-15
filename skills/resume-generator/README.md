# 🦞 Resume Generator · 小龙虾简历生成器

快速生成专业且有个性的简历，支持多种风格模板。

## 🚀 快速开始

### 方法一：使用脚本（推荐）

```bash
cd /home/admin/.openclaw/workspace/skills/resume-generator

# 使用示例数据生成
./scripts/generate.sh -i example-data.json -o resume.pdf

# 仅预览 HTML
./scripts/generate.sh -i example-data.json -p
```

### 方法二：直接调用 AI 助手

在聊天中说：
- "帮我生成简历"
- "做个小龙虾风格简历"
- "把我的经历做成简历"

AI 会自动收集信息并生成简历。

## 📋 数据格式

创建 JSON 文件描述你的简历内容：

```json
{
  "name": "你的姓名",
  "badge": "个人标签/徽章",
  "title": "职业定位/标题",
  "contact_items": ["📧 邮箱", "📱 手机", "🌐 网站"],
  "summary": "个人总结（150-300 字）",
  "keywords": ["关键词 1", "关键词 2"],
  "skills": [
    {"name": "技能名称", "desc": "技能描述"}
  ],
  "education": [
    {"school": "学校", "degree": "学历", "major": "专业", "details": "详情"}
  ],
  "experience": [
    {"role": "职位", "company": "公司", "period": "时间", "points": ["成就 1", "成就 2"]}
  ],
  "awards": [
    {"title": "奖项", "date": "日期", "level": "gold|silver|bronze", "badge": "🏆 一等奖"}
  ],
  "highlights": ["核心亮点 1", "核心亮点 2"]
}
```

## 🎨 可用风格

| 风格 | 代码 | 适用场景 |
|------|------|----------|
| 🦞 小龙虾 | `lobster` | AI/创意/教育行业 |
| 💼 极简专业 | `minimal` | 传统商务/金融 |
| 💻 科技极客 | `tech` | 程序员/技术岗位 |
| 📚 学术风格 | `academic` | 科研/教育岗位 |

## 📁 文件结构

```
skills/resume-generator/
├── SKILL.md                 # 技能说明
├── README.md                # 使用指南
├── example-data.json        # 示例数据
├── templates/
│   ├── lobster.html         # 小龙虾模板
│   ├── minimal.html         # 极简模板
│   ├── tech.html            # 科技模板
│   └── academic.html        # 学术模板
└── scripts/
    └── generate.sh          # 生成脚本
```

## 💡 最佳实践

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

## 🔧 依赖要求

- **Chrome/Chromium** - PDF 生成必需
- **Node.js** - 模板处理
- **Bash** - 脚本执行

## 📝 更新日志

- **v1.0.0** (2026-04-15) - 初始版本
  - 🦞 小龙虾风格模板
  - 📄 HTML + PDF 双输出
  - 🎨 渐变配色 + 动画效果
  - 📋 CAR 法则内容优化

## 🙏 致谢

灵感来源于陈俊烨 (CJY) 的简历生成需求，小龙虾记忆研究群荣誉出品 🦞
