# 教学案例：AI 助手驱动的微信公众号新闻自动化归档与 PDF 生成

## 一、案例基本信息

| 项目 | 内容 |
|------|------|
| **案例名称** | AI 助手驱动的微信公众号新闻自动化归档与 PDF 生成 |
| **案例类型** | AI Agent 实战应用 / 教育数字化转型 |
| **适用对象** | 高校教师、教育技术工作者、AI 应用开发者 |
| **案例日期** | 2026 年 4 月 25 日 |
| **编写者** | 小龙虾 - 诸葛虾 |
| **模型** | 通义千问 Qwen 3.6 Plus |

---

## 二、案例背景

### 2.1 需求场景

诸葛斌老师（浙江工商大学信息与电子工程学院教授）希望：
1. 能够便捷地查看微信公众号文章（特别是与自己相关的新闻）
2. 将重要文章保存为 PDF 格式，便于归档和分享
3. 建立个人新闻档案库，持续跟踪媒体报道
4. 实现自动化流程，减少手动操作

### 2.2 技术挑战

- **微信公众号反爬机制**：正文通过 JavaScript 动态渲染，轻量抓取器无法获取内容
- **图片处理难题**：图片通过 data-src 属性懒加载，需要额外处理
- **PDF 生成复杂**：需要浏览器渲染，无头浏览器会被检测
- **批量处理需求**：14 篇文章需要统一处理和管理

---

## 三、教学过程

### 3.1 第一阶段：问题识别与方案探索

#### 3.1.1 初始尝试（失败）

**用户行为**：分享微信公众号文章链接

**AI 尝试**：
- 使用 `web_fetch` 工具直接抓取
- **结果**：只拿到标题，正文为空
- **原因**：微信公众号文章正文是 JavaScript 动态渲染的

#### 3.1.2 用户辅助

**用户行为**：发送文章截图，展示完整内容

**关键发现**：
- 用户通过截图确认文章内容
- 这为后续技术突破提供了验证基准

#### 3.1.3 技术突破

**解决方案**：
```bash
curl -s -L \
    -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..." \
    -H "Accept-Language: zh-CN,zh;q=0.9" \
    "https://mp.weixin.qq.com/s/xxxxx" | python3 -c "
import sys, re, html
content = sys.stdin.read()
match = re.search(r'id=\"js_content\"[^>]*>(.*?)</div>\s*<script', content, re.DOTALL)
if match:
    text = match.group(1)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    print('\n'.join(lines))
"
```

**关键技巧**：
- 使用真实 User-Agent 模拟浏览器
- 直接解析 HTML 源码中的 `js_content` div
- 不需要执行 JavaScript，因为源码中已包含完整内容

### 3.2 第二阶段：技能封装与 PDF 生成

#### 3.2.1 创建 wechat-to-pdf 技能

**文件结构**：
```
skills/wechat-to-pdf/
├── SKILL.md              # 技能说明文档
├── scripts/
│   ├── wechat-to-pdf.sh  # 主脚本
│   ├── extract_wechat.py # Python 提取脚本
│   └── generate_html.py  # HTML 生成脚本
└── references/
    └── mp.weixin.qq.com.md  # 站点经验
```

**核心功能**：
1. 抓取 HTML 源码（curl）
2. 提取正文内容（Python 正则）
3. 下载图片（urllib）
4. 内嵌图片为 base64（Pillow 压缩）
5. 生成自包含 HTML
6. 浏览器渲染导出 PDF

#### 3.2.2 PDF 生成问题

**遇到的问题**：
- 浏览器服务不可用
- 钉钉文件上传限制（文件大小）
- 图片内嵌导致文件过大

**解决方案**：
- 压缩图片：质量 50%，最大尺寸 600px
- 发送 HTML 打包文件替代 PDF
- 提供后续批量生成方案

### 3.3 第三阶段：批量处理与新闻归档

#### 3.3.1 需求扩展

**用户行为**：发送 17 个微信公众号链接（去重后 14 个）

**处理结果**：

| 项目 | 数量 |
|------|------|
| 总链接数 | 17 个 |
| 去重后 | 14 个 |
| 成功抓取 | 13 篇 |
| 特殊格式 | 1 个（腾讯链接） |

#### 3.3.2 文章列表

1. 信息与电子工程学院举办"拥抱'AI+'时代"教学开放周活动
2. 数智赋能 智启未来——特级管理会计师研讨会
3. 解锁 AI 新生产力 | 浙青创"小龙虾"AI 数字员工分享会
4. 深化教育数字化转型 | CIO 培训班（已生成 PDF）
5. AI 助理赋能智慧图书馆
6. 我院学子荣获首届阿里小龙虾大会"黑客松勇士"称号
7. 2025 年度高光｜教学提质攀新高
8. 快乐校园×青年·爱学习 | 博研人才培训班
9. 【研会】星空夜话 | 拥抱"AI+"时代
10. 讲座报名丨诸葛斌教授讲授"人工智能 Deepseek"
11. 教师教学发展中心举办"Deepseek 在教学科研中的应用"
12. 腾讯链接（格式特殊，未能处理）
13. 新书速递 | 袁非牛等著《数字人文》
14. AI 执笔，绘学术新章 | 研究生 DeepSeek 课程结课

#### 3.3.3 目录结构

```
zhugebin-news/
├── index.md              # 文章索引（14 篇）
├── AUTOMATION.md         # 自动化流程文档
├── html/                 # 原始 HTML（13 篇）
├── html_compressed/      # 压缩 HTML（13 篇，图片内嵌）
├── pdfs/                 # PDF 目录（待填充）
├── summaries/            # 摘要文档（13 篇）
├── case-studies/         # 教学案例（1 篇）
├── scripts/              # 脚本
│   ├── weekly-news-check.sh      # 定期新闻抓取
│   └── batch-generate-pdfs.sh    # 批量 PDF 生成
├── reports/              # 周报目录
└── logs/                 # 日志目录
```

### 3.4 第四阶段：自动化流程设计

#### 3.4.1 定时任务配置

| 任务 | Cron 表达式 | 执行时间 | 功能 |
|------|-------------|----------|------|
| 新闻抓取 | `0 9 * * 1` | 每周一上午 9:00 | 搜索新闻、抓取 HTML、提取摘要、生成报告 |
| PDF 生成 | `0 10 * * 3` | 每周三上午 10:00 | 批量生成 PDF、保存到目录 |

#### 3.4.2 工作流程

```
新闻抓取流程：
Cron 触发 → 搜索关键词 → 发现新链接 → 抓取 HTML → 提取摘要 → 生成报告 → 更新索引

PDF 生成流程：
Cron 触发 → 读取 HTML → 压缩图片 → 内嵌图片 → 生成 PDF → 保存目录
```

#### 3.4.3 文件交付

| 文件 | 大小 | 内容 |
|------|------|------|
| zhugebin-news-html.zip | 16MB | 13 篇自包含 HTML 文件（图片内嵌） |
| zhugebin-news-summaries.zip | 29KB | 13 篇新闻摘要文档 |
| zhugebin-news-case-study.zip | 4.8KB | 诸葛斌老师与小龙虾教学案例 |

### 3.5 第五阶段：模型切换与案例整理

#### 3.5.1 模型切换

**用户指令**：切换为最新的 3.6

**操作**：
```
session_status(model="qwen3.6-plus")
```

**结果**：成功切换到通义千问 Qwen 3.6 Plus

#### 3.5.2 案例整理

**用户指令**：把今天的聊天记录整理为一个教学案例

**输出**：本文档

---

## 四、技术要点

### 4.1 微信公众号反爬处理

| 方法 | 结果 | 原因 |
|------|------|------|
| `web_fetch` | ❌ 只有标题 | 不执行 JS，正文未渲染 |
| `browser` 工具 | ❌ 滑块验证 | 无头浏览器被反爬检测 |
| Jina Reader | ❌ 连接失败 | 微信屏蔽 Jina 爬虫 |
| curl + Python 解析 | ✅ 成功 | 源码中已包含完整内容 |

### 4.2 图片处理策略

```python
# 1. 下载图片
urllib.request.urlretrieve(img_url, img_path)

# 2. 转换为 RGB 模式
img = Image.open(img_path).convert('RGB')

# 3. 调整尺寸
if max(img.size) > max_dim:
    ratio = max_dim / max(img.size)
    img = img.resize(new_size, Image.Resampling.LANCZOS)

# 4. 压缩保存
img.save(buffer, format='JPEG', quality=50)

# 5. 编码为 base64
img_data = base64.b64encode(buffer.getvalue()).decode()
data_uri = f'data:image/jpeg;base64,{img_data}'
```

### 4.3 批量处理脚本

```bash
# 批量处理 HTML 文件
for file in wechat_*.html; do
    id=$(echo "$file" | sed 's/wechat_//' | sed 's/.html//')
    python3 batch_wechat_to_pdf.py "$file" "../html_compressed/${id}.html"
done
```

---

## 五、成果展示

### 5.1 量化成果

| 指标 | 数值 |
|------|------|
| 处理文章数 | 14 篇 |
| 成功抓取 | 13 篇 |
| 生成摘要 | 13 篇 |
| 生成 HTML | 13 篇（含图片内嵌） |
| 生成 PDF | 1 篇 |
| 创建技能 | 1 个（wechat-to-pdf） |
| 创建脚本 | 2 个（定时抓取、批量 PDF） |
| 定时任务 | 2 个 |
| Git 提交 | 4 次 |
| 交付文件 | 3 个 ZIP 包 |

### 5.2 文件结构

```
zhugebin-news/
├── index.md              # 文章索引（14 篇）
├── AUTOMATION.md         # 自动化流程文档
├── html/                 # 原始 HTML（13 篇）
├── html_compressed/      # 压缩 HTML（13 篇，图片内嵌）
├── pdfs/                 # PDF 目录（待填充）
├── summaries/            # 摘要文档（13 篇）
├── case-studies/         # 教学案例（2 篇）
├── scripts/              # 脚本（2 个）
├── reports/              # 周报目录
└── logs/                 # 日志目录
```

---

## 六、经验总结

### 6.1 成功要素

| 要素 | 说明 |
|------|------|
| 问题诊断 | 快速识别微信公众号反爬机制 |
| 技术突破 | curl + Python 直接解析 HTML 源码 |
| 技能封装 | 将解决方案封装为可复用技能 |
| 批量处理 | 自动化处理 14 篇文章 |
| 持续优化 | 设置定时任务实现自动化 |
| 模型切换 | 灵活切换最新模型提升效果 |

### 6.2 技术亮点

1. **绕过反爬**：不需要执行 JS，直接从 HTML 源码提取内容
2. **图片压缩**：使用 Pillow 压缩图片，控制文件大小
3. **技能封装**：将解决方案封装为可复用技能（wechat-to-pdf）
4. **自动化流程**：设置 cron 定时任务，实现新闻自动抓取和 PDF 生成
5. **版本管理**：使用 Git 管理所有文件和脚本

### 6.3 遇到的挑战

| 挑战 | 解决方案 |
|------|----------|
| 微信公众号反爬 | curl + Python 直接解析 HTML 源码 |
| 图片路径问题 | 内嵌为 base64 data URI |
| 浏览器服务不可用 | 发送 HTML 打包文件替代 |
| 文件大小限制 | 压缩图片质量到 50% |
| 批量处理效率 | 使用脚本自动化处理 |

### 6.4 可复制经验

1. **技术民主化**：通过 AI 助手，非技术人员也能完成复杂的技术任务
2. **技能封装**：将解决方案封装为技能，便于复用和分享
3. **自动化优先**：设置定时任务，减少手动操作
4. **持续迭代**：根据反馈不断优化和改进

---

## 七、教学启示

### 7.1 对教育技术工作者的启示

1. **AI 助手的应用**：AI 助手可以显著提升工作效率，特别是在数据处理和内容生成方面
2. **技能封装的重要性**：将解决方案封装为技能，便于复用和分享
3. **自动化流程的价值**：设置定时任务，实现新闻自动抓取和 PDF 生成

### 7.2 对 AI 应用开发者的启示

1. **问题诊断能力**：快速识别问题的根本原因
2. **技术突破能力**：找到绕过反爬机制的方法
3. **批量处理能力**：使用脚本自动化处理大量数据
4. **持续优化能力**：根据反馈不断优化和改进

### 7.3 对未来发展的展望

1. **AI Agent 时代**：AI 助手将成为教育和工作的核心工具
2. **技能生态**：技能封装和分享将成为重要趋势
3. **自动化流程**：定时任务和自动化流程将普及
4. **模型迭代**：模型将持续升级，能力不断提升

---

## 八、附录

### 8.1 关键代码片段

**微信公众号文章抓取**：
```bash
curl -s -L \
    -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..." \
    -H "Accept-Language: zh-CN,zh;q=0.9" \
    "https://mp.weixin.qq.com/s/xxxxx" | python3 extract.py
```

**图片压缩与内嵌**：
```python
img = Image.open(img_path).convert('RGB')
if max(img.size) > max_dim:
    ratio = max_dim / max(img.size)
    img = img.resize(new_size, Image.Resampling.LANCZOS)
img.save(buffer, format='JPEG', quality=50)
img_data = base64.b64encode(buffer.getvalue()).decode()
```

**定时任务配置**：
```bash
# 新闻抓取 - 每周一上午 9 点
0 9 * * 1 bash ~/.openclaw/workspace/zhugebin-news/scripts/weekly-news-check.sh

# PDF 生成 - 每周三上午 10 点
0 10 * * 3 bash ~/.openclaw/workspace/zhugebin-news/scripts/batch-generate-pdfs.sh
```

### 8.2 相关文件

- [wechat-to-pdf 技能](skills/wechat-to-pdf/SKILL.md)
- [新闻归档](zhugebin-news/index.md)
- [自动化流程](zhugebin-news/AUTOMATION.md)
- [诸葛斌老师与小龙虾教学案例](zhugebin-news/case-studies/zhugebin-xiaolongxia-teaching-case.md)

---

**案例编写**：小龙虾 - 诸葛虾  
**编写时间**：2026 年 4 月 25 日 14:58  
**案例版本**：v1.0  
**适用模型**：通义千问 Qwen 3.6 Plus
