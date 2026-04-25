# 诸葛斌老师新闻自动化流程

## 一、自动化任务

### 1.1 定时新闻抓取

**Cron 配置：**
```bash
0 9 * * 1 bash ~/.openclaw/workspace/zhugebin-news/scripts/weekly-news-check.sh
```

**执行时间：** 每周一上午 9:00

**功能：**
- 搜索诸葛斌老师相关新闻
- 抓取新文章 HTML
- 提取摘要
- 生成周报
- 更新索引

### 1.2 定时 PDF 生成

**Cron 配置：**
```bash
0 10 * * 3 bash ~/.openclaw/workspace/zhugebin-news/scripts/batch-generate-pdfs.sh
```

**执行时间：** 每周三上午 10:00

**功能：**
- 批量生成 PDF 文件
- 保存到 pdfs/ 目录
- 记录日志

---

## 二、手动操作

### 2.1 立即执行新闻抓取

```bash
bash ~/.openclaw/workspace/zhugebin-news/scripts/weekly-news-check.sh
```

### 2.2 立即生成 PDF

```bash
bash ~/.openclaw/workspace/zhugebin-news/scripts/batch-generate-pdfs.sh
```

### 2.3 查看日志

```bash
cat ~/.openclaw/workspace/zhugebin-news/logs/cron.log
```

### 2.4 查看报告

```bash
ls ~/.openclaw/workspace/zhugebin-news/reports/
```

---

## 三、文件结构

```
zhugebin-news/
├── index.md              # 文章索引
├── AUTOMATION.md         # 本文件
├── html/                 # 原始 HTML 文件
├── html_compressed/      # 压缩 HTML（图片内嵌）
├── pdfs/                 # PDF 文件
├── summaries/            # 摘要文档
├── case-studies/         # 教学案例
├── scripts/              # 脚本
│   ├── weekly-news-check.sh      # 定期新闻抓取
│   └── batch-generate-pdfs.sh    # 批量 PDF 生成
├── reports/              # 周报
└── logs/                 # 日志
```

---

## 四、工作流程

### 4.1 新闻抓取流程

```
搜索关键词 → 发现新链接 → 抓取 HTML → 提取摘要 → 生成报告 → 更新索引
```

### 4.2 PDF 生成流程

```
读取 HTML → 压缩图片 → 内嵌图片 → 生成 PDF → 保存到目录
```

### 4.3 自动化流程

```
Cron 触发 → 执行脚本 → 完成任务 → 记录日志 → 发送通知（可选）
```

---

## 五、维护建议

### 5.1 定期检查

- 每周检查日志文件，确认任务正常执行
- 每月检查 PDF 文件，确认生成质量
- 每季度更新教学案例

### 5.2 故障排查

**问题：Cron 任务未执行**
```bash
# 检查 cron 服务
systemctl status cron

# 检查 cron 日志
tail -f /var/log/cron.log
```

**问题：PDF 生成失败**
```bash
# 检查浏览器工具
openclaw gateway status

# 手动执行脚本
bash ~/.openclaw/workspace/zhugebin-news/scripts/batch-generate-pdfs.sh
```

### 5.3 性能优化

- 定期清理旧日志文件
- 压缩历史报告
- 优化搜索关键词

---

## 六、扩展功能

### 6.1 邮件通知

可以添加邮件通知功能，在完成任务后发送邮件提醒。

### 6.2 钉钉通知

可以添加钉钉通知功能，通过钉钉机器人发送任务完成通知。

### 6.3 数据可视化

可以添加数据可视化功能，生成新闻趋势图表。

---

## 七、联系方式

- **维护者**：小龙虾 - 诸葛虾
- **更新时间**：2026 年 4 月 25 日
- **问题反馈**：通过钉钉联系
