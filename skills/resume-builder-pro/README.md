# Resume Builder Pro

专业简历生成与优化技能，基于 ClawHub 多技能最佳实践沉淀。

## 快速开始

```bash
# 1. 安装依赖
cd skills/resume-builder-pro
npm install

# 2. 生成简历
./scripts/generate-resume.sh --template professional

# 3. 导出 PDF
./scripts/export-pdf.sh resume.html 陈俊烨_简历.pdf

# 4. ATS 检查
./scripts/ats-check.sh 陈俊烨_简历.pdf
```

## 模板

| 模板 | 风格 | 适用 |
|------|------|------|
| `professional` | 专业蓝白 | 大厂、国企 |
| `minimal` | 极简黑白 | 外企、咨询 |
| `tech` | 科技渐变 | 互联网、创业 |
| `academic` | 学术风格 | 科研、博士 |

## 文档

- [最佳实践](references/best-practices.md)
- [ATS 优化指南](references/ats-optimization.md)
- [模板开发](templates/README.md)

## 示例

```bash
# 生成陈俊烨的简历
./scripts/generate-resume.sh \
  --template professional \
  --output 陈俊烨_简历

# 批量导出
for template in professional minimal tech; do
  ./scripts/export-pdf.sh \
    resumes/resume_$template.html \
    resumes/陈俊烨_简历_$template.pdf
done
```

---

🦞 由 信电大虾 于 2026-04-15 创建
