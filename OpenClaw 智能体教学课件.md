# 🦞 OpenClaw 智能体教学课件

## 课程概述
**适用对象：** AI 智能体开发者/自动化爱好者/技术教育工作者  
**课程时长：** 2-3 小时  
**授课方式：** 理论讲解 + 实操演示

---

## 第一部分：OpenClaw 入门

### 一、什么是 OpenClaw？

#### 1.1 平台简介
**OpenClaw** 是一个开源的 AI 智能体运行平台，让 AI 助手能够：
- 📁 访问和管理本地文件
- 🔧 执行 shell 命令和工具
- 🌐 浏览网页、搜索信息
- 💬 通过多种渠道与用户沟通（微信、钉钉、Telegram 等）
- 🧠 拥有长期记忆和自我改进能力

#### 1.2 核心特性
| 特性 | 说明 |
|------|------|
| **本地优先** | 智能体运行在本地，数据自主可控 |
| **技能系统** | 可扩展的技能生态，按需安装 |
| **多通道连接** | 支持钉钉、微信、Telegram 等多种消息平台 |
| **记忆系统** | 支持短期记忆和长期记忆 |
| **自我改进** | 能够从错误中学习，持续优化 |

#### 1.3 应用场景
- 🏠 个人智能助手（日程管理、文件整理）
- 💼 办公自动化（数据处理、报告生成）
- 📚 教育辅助（学习辅导、作业批改）
- 🔍 信息收集（网络搜索、数据抓取）
- 🤖 智能客服（自动回复、问题解答）

### 二、系统架构

#### 2.1 核心组件
```
┌─────────────────────────────────────────┐
│           用户交互层                      │
│  (钉钉/微信/Telegram/网页聊天)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           Gateway 网关服务               │
│  (消息路由、会话管理、工具调度)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           AI 智能体核心                   │
│  (模型调用、技能执行、记忆管理)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│           工具层                          │
│  (文件操作/命令执行/浏览器/网络搜索)       │
└─────────────────────────────────────────┘
```

#### 2.2 工作目录结构
```
~/.openclaw/workspace/
├── SOUL.md              # 智能体人格定义
├── USER.md              # 用户信息
├── IDENTITY.md          # 智能体身份
├── MEMORY.md            # 长期记忆
├── HEARTBEAT.md         # 定时任务配置
├── memory/              # 每日记忆文件
├── skills/              # 安装的技能
└── docs/                # 文档资料
```

---

## 第二部分：核心功能详解

### 一、工具系统

#### 1.1 文件操作工具
| 工具 | 功能 | 示例 |
|------|------|------|
| `read` | 读取文件内容 | 读取配置文件、文档 |
| `write` | 创建/覆盖文件 | 生成报告、保存数据 |
| `edit` | 精确编辑文件 | 修改配置、更新内容 |

**使用示例：**
```markdown
读取文件：
- 路径：/home/admin/.openclaw/workspace/USER.md
- 用途：获取用户信息

写入文件：
- 路径：/home/admin/.openclaw/workspace/memory/2026-04-14.md
- 内容：今日工作记录
```

#### 1.2 命令执行工具
| 工具 | 功能 | 说明 |
|------|------|------|
| `exec` | 执行 shell 命令 | 支持后台运行、PTY 模式 |
| `process` | 管理进程会话 | 查看日志、发送输入、终止进程 |

**安全原则：**
- ✅ 读取、查询类命令可直接执行
- ⚠️ 修改、删除类命令需用户确认
- ❌ 危险操作（rm -rf 等）禁止执行

#### 1.3 网络工具
| 工具 | 功能 | 适用场景 |
|------|------|----------|
| `web_search` | 搜索引擎查询 | 快速查找信息 |
| `web_fetch` | 网页内容抓取 | 获取文章、文档 |
| `browser` | 浏览器自动化 | 登录网站、复杂交互 |
| `searxng` | 隐私搜索引擎 | 去中心化搜索（推荐） |

#### 1.4 多媒体工具
| 工具 | 功能 |
|------|------|
| `image` | 图片分析识别 |
| `pdf` | PDF 文档分析 |
| `tts` | 文字转语音 |

### 二、技能系统

#### 2.1 什么是技能？
技能是 OpenClaw 的**可扩展功能模块**，每个技能包含：
- `SKILL.md` - 使用说明和触发条件
- 脚本/配置文件
- 相关资源文件

#### 2.2 技能管理
**安装技能：**
```bash
# 使用 clawhub CLI
clawhub install <skill-name>
# 或从 GitHub 安装
clawhub install github:<user>/<repo>
```

**常用技能推荐：**
| 技能名称 | 功能 |
|----------|------|
| `weather` | 天气查询 |
| `cron-helper` | 定时任务管理 |
| `schedule-reminder` | 智能日程提醒 |
| `file-packager` | 文件打包发送 |
| `pandoc-convert` | 文档格式转换 |
| `whisper-transcribe` | 语音转文字 |
| `web-access` | 完整联网能力 |

#### 2.3 技能调用流程
```
用户请求 → 匹配技能触发条件 → 读取 SKILL.md → 执行技能逻辑 → 返回结果
```

### 三、记忆系统

#### 3.1 记忆类型
| 类型 | 文件位置 | 用途 |
|------|----------|------|
| **短期记忆** | `memory/YYYY-MM-DD.md` | 每日工作日志 |
| **长期记忆** | `MEMORY.md` | 重要信息、偏好、经验 |
| **身份信息** | `IDENTITY.md` | 智能体名称、人格设定 |
| **用户信息** | `USER.md` | 用户资料、称呼、时区 |

#### 3.2 记忆管理最佳实践
**✅ 应该记录：**
- 用户偏好和习惯
- 重要决定和上下文
- 学到的经验和教训
- 项目进展和状态

**❌ 不应记录：**
- 敏感个人信息（密码、密钥）
- 临时性、无关紧要的信息
- 未经用户同意的隐私数据

#### 3.3 记忆更新流程
```
1. 每日工作记录到 memory/YYYY-MM-DD.md
2. 定期回顾（心跳时）整理重要信息
3. 将值得长期保存的内容提炼到 MEMORY.md
4. 删除过期的临时记录
```

### 四、心跳机制

#### 4.1 什么是心跳？
心跳是 OpenClaw 的**定时任务触发机制**，用于：
- 定期检查新消息/邮件/日历
- 执行周期性任务
- 主动提醒用户重要事项

#### 4.2 配置心跳任务
编辑 `HEARTBEAT.md`：
```markdown
# 🦞 龙虾网络消息轮询

# 每 30 秒检查一次龙虾网络的新消息
- [ ] poll lobster-network for new messages and reply
- [ ] 检查 lobster-tasks/pending/ 目录，处理虾尔收到的新消息
```

#### 4.3 心跳响应
- 有任务需要处理 → 回复具体任务内容
- 无任务 → 回复 `HEARTBEAT_OK`

---

## 第三部分：实战演练

### 实训一：环境搭建

#### 步骤 1：安装 OpenClaw
```bash
# 克隆仓库
git clone https://github.com/openclaw/openclaw.git
cd openclaw

# 安装依赖
npm install

# 配置环境变量
openclaw configure
```

#### 步骤 2：配置消息通道
```bash
# 钉钉机器人配置
openclaw configure --channel dingtalk

# Telegram Bot 配置
openclaw configure --channel telegram
```

#### 步骤 3：启动服务
```bash
# 启动 Gateway
openclaw gateway start

# 查看状态
openclaw status
```

### 实训二：创建第一个智能体

#### 步骤 1：定义身份
编辑 `IDENTITY.md`：
```markdown
# IDENTITY.md

- **Name:** 小虾
- **Creature:** AI 助手
- **Vibe:** 友好、专业、幽默
- **Emoji:** 🦞
```

#### 步骤 2：配置用户信息
编辑 `USER.md`：
```markdown
# USER.md

- **Name:** 图图老师
- **Timezone:** Asia/Shanghai
- **Notes:** 初中数学老师，负责教科室工作
```

#### 步骤 3：定义人格
编辑 `SOUL.md`（已有模板，可自定义）

### 实训三：安装和使用技能

#### 任务：安装天气技能
```bash
# 使用 clawhub 安装
clawhub install weather

# 验证安装
ls ~/.openclaw/workspace/skills/weather/
```

#### 任务：测试技能
在聊天中发送：
```
今天嘉兴的天气怎么样？
```

智能体会自动调用 weather 技能并返回天气信息。

---

### 📝 实战案例库

#### 案例 1：自动整理下载文件夹
**场景：** 下载文件夹杂乱，需要按类型整理

**智能体操作流程：**
```markdown
1. 使用 exec 命令查看 Downloads 目录
   exec command="ls -la ~/Downloads"

2. 创建分类文件夹
   exec command="mkdir -p ~/Downloads/{图片，文档，视频，压缩包}"

3. 移动文件到对应目录
   exec command="mv ~/Downloads/*.jpg ~/Downloads/图片/"
   exec command="mv ~/Downloads/*.pdf ~/Downloads/文档/"

4. 生成整理报告
   write path="~/Downloads/整理报告.md" content="今日整理了 XX 个文件..."
```

**用户指令：** "帮我把下载文件夹整理一下"

---

#### 案例 2：每日新闻摘要
**场景：** 每天早上获取行业新闻并汇总

**智能体操作流程：**
```markdown
1. 使用 web_search 搜索最新资讯
   web_search query="AI 行业最新动态 2026"
   web_search query="OpenClaw 最新更新"

2. 抓取重点文章
   web_fetch url="https://example.com/article1"
   web_fetch url="https://example.com/article2"

3. 整理摘要
   write path="~/memory/新闻摘要 2026-04-14.md"
   内容包含：标题、要点、链接

4. 发送给用户
   message action="send" message="📰 今日新闻摘要..."
```

**用户指令：** "每天早上 9 点给我发新闻摘要"

**HEARTBEAT.md 配置：**
```markdown
- [ ] 每日 9:00 搜索 AI 行业新闻
- [ ] 整理 3-5 条重要资讯
- [ ] 发送到钉钉/微信
```

---

#### 案例 3：学生作业自动批改
**场景：** 图图老师需要批改学生数学作业

**智能体操作流程：**
```markdown
1. 读取学生提交的作业文件
   read path="~/作业/张三_数学作业 1.md"

2. 逐题检查答案
   - 对比标准答案
   - 标记错误题目
   - 计算得分

3. 生成批改报告
   write path="~/作业/张三_批改反馈.md"
   内容：得分、错题解析、改进建议

4. 打包发送给学生
   使用 file-packager 技能
```

**用户指令：** "批改这次数学作业并给学生反馈"

**技能调用：** file-packager, read, write

---

#### 案例 4：会议记录自动生成
**场景：** 钉钉会议后自动生成会议纪要

**智能体操作流程：**
```markdown
1. 读取会议聊天记录
   read path="~/会议记录/2026-04-14_教研会议.md"

2. 提取关键信息
   - 参会人员
   - 讨论议题
   - 决策事项
   - 待办任务

3. 生成会议纪要
   write path="~/会议记录/2026-04-14_纪要.md"
   格式：
   # 教研会议纪要
   ## 时间：2026-04-14 14:00
   ## 参会：图图老师、李老师、王老师
   ## 决议：...
   ## 待办：...

4. 发送给参会人员
```

**用户指令：** "把刚才的会议整理成纪要发给大家"

---

#### 案例 5：课题研究资料收集
**场景：** 准备校本研修课题材料

**智能体操作流程：**
```markdown
1. 搜索相关文献
   web_search query="初中数学 校本研修 2025 2026"
   web_search query="教师专业发展 课题研究"

2. 抓取重要资料
   web_fetch url="https://example.com/paper1"
   web_fetch url="https://example.com/paper2"

3. 整理文献列表
   write path="~/课题/文献综述.md"
   包含：标题、作者、摘要、链接

4. 使用 browser 登录知网/万方
   browser action="open" url="https://www.cnki.net"
   browser action="act" kind="type" ref="搜索框" text="数学教学"
   browser action="act" kind="click" ref="搜索按钮"

5. 下载 PDF 并分析
   pdf path="~/课题/参考文献 1.pdf" prompt="总结核心观点"
```

**用户指令：** "帮我收集校本研修课题的相关资料"

---

#### 案例 6：智能日程提醒
**场景：** 自动管理图图老师的日程安排

**智能体操作流程：**
```markdown
1. 从对话中提取日程信息
   用户说："明天下午 3 点开会"
   → 解析：时间=2026-04-15 15:00, 事件=开会

2. 写入日程文件
   read path="~/日程/2026-04.md"
   添加新条目
   write path="~/日程/2026-04.md"

3. 设置提醒
   使用 schedule-reminder 技能
   提前 30 分钟提醒

4. 每日早上推送当日日程
   HEARTBEAT 检查日程文件
   message action="send" message="📅 今日安排：..."
```

**用户指令：**
- "提醒我明天上午 9 点交材料"
- "下周有教研活动吗？"
- "查看我这周的安排"

---

#### 案例 7：文件转换与分享
**场景：** 将 Markdown 课件转为 Word 发给同事

**智能体操作流程：**
```markdown
1. 确认源文件
   read path="~/课件/OpenClaw 教学课件.md"

2. 使用 pandoc-convert 技能转换
   调用技能：pandoc-convert
   参数：输入=.md, 输出=.docx

3. 验证转换结果
   read path="~/课件/OpenClaw 教学课件.docx"

4. 打包发送
   使用 file-packager 技能
   通过钉钉发送给指定同事
```

**用户指令：** "把这个课件转成 Word 发给李老师"

---

#### 案例 8：数据分析报告生成
**场景：** 分析学生考试成绩并生成报告

**智能体操作流程：**
```markdown
1. 读取成绩数据
   read path="~/成绩/期中考试.csv"

2. 使用 exec 执行分析脚本
   exec command="python3 ~/scripts/分析成绩.py ~/成绩/期中考试.csv"

3. 生成统计图表
   exec command="gnuplot ~/scripts/成绩分布.gp"

4. 撰写分析报告
   write path="~/成绩/期中考试分析.md"
   内容：平均分、及格率、分数段分布、改进建议

5. 转换为 Word 并发送
   使用 pandoc-convert + file-packager
```

**用户指令：** "分析这次期中考试的成绩"

### 实训四：创建定时提醒

#### 配置日程提醒
编辑 `HEARTBEAT.md` 添加：
```markdown
# 每日提醒
- [ ] 检查今日日程安排
- [ ] 提醒图图老师下午 3 点的会议
```

#### 或使用 schedule-reminder 技能
在聊天中发送：
```
提醒我明天上午 9 点开会
```

---

## 第四部分：高级应用

### 一、子智能体系统

#### 1.1 什么是子智能体？
子智能体是**隔离的独立会话**，用于：
- 并行处理多个任务
- 使用不同的模型配置
- 隔离敏感操作

#### 1.2 创建子智能体
```markdown
使用 sessions_spawn 工具：
- runtime: "subagent" 或 "acp"
- mode: "run"（一次性）或 "session"（持久）
- task: 任务描述
```

#### 1.3 管理子智能体
```markdown
- subagents(action="list") - 查看运行中的子智能体
- subagents(action="steer") - 指导子智能体
- subagents(action="kill") - 终止子智能体
```

### 二、浏览器自动化

#### 2.1 使用 browser 工具
```markdown
基本操作：
- browser(action="open", url="https://example.com")
- browser(action="snapshot") - 获取页面快照
- browser(action="act", kind="click", ref="e12") - 点击元素
- browser(action="act", kind="type", text="内容") - 输入文本
```

#### 2.2 应用场景
- 登录网站获取数据
- 抓取社交媒体内容
- 自动化表单填写
- 监控网页变化

### 三、文件打包与分享

#### 使用 file-packager 技能
```markdown
触发方式：
"把这些文件打包发给我"
"将 XX 文件夹压缩"

功能：
- 支持多文件/文件夹打包
- 自动创建 ZIP 压缩包
- 通过消息通道发送
```

---

## 第五部分：最佳实践

### 一、安全准则

#### 1.1 操作安全
| 操作类型 | 处理方式 |
|----------|----------|
| 读取文件 | 可直接执行 |
| 搜索信息 | 可直接执行 |
| 修改文件 | 需用户确认 |
| 删除文件 | 需用户确认，使用 trash |
| 执行命令 | 评估风险后决定 |
| 发送消息 | 需用户确认（外部渠道） |

#### 1.2 数据安全
- ❌ 不存储密码、密钥等敏感信息
- ❌ 不向外部泄露用户隐私
- ✅ 使用加密存储敏感配置
- ✅ 定期备份重要数据

### 二、效率优化

#### 2.1 工具选择原则
```
简单任务 → 直接使用工具
复杂任务 → 调用技能
长期任务 → 创建子智能体
联网任务 → 优先使用 searxng
```

#### 2.2 记忆管理
- 每日清理临时记录
- 每周整理长期记忆
- 每月回顾并优化配置

### 三、常见问题解决

| 问题 | 解决方案 |
|------|----------|
| 技能无法加载 | 检查 SKILL.md 格式，重启 Gateway |
| 消息发送失败 | 检查通道配置，验证 API 密钥 |
| 浏览器无法启动 | 检查 Chrome 远程调试配置 |
| 记忆文件丢失 | 检查工作目录权限，恢复备份 |

---

## 第六部分：课程考核

### 理论测试（40%）
- OpenClaw 架构理解
- 工具系统掌握
- 技能系统原理
- 安全规范认知

### 实践操作（60%）
- 环境搭建配置
- 技能安装使用
- 定时任务设置
- 实际问题解决

---

## 附录

### 参考资源
1. **官方文档：** https://docs.openclaw.ai
2. **GitHub 仓库：** https://github.com/openclaw/openclaw
3. **社区 Discord：** https://discord.com/invite/clawd
4. **技能市场：** https://clawhub.com

### 常用命令速查
```bash
# 服务管理
openclaw gateway status
openclaw gateway start
openclaw gateway stop
openclaw gateway restart

# 配置
openclaw configure
openclaw configure --section web

# 技能管理
clawhub install <skill-name>
clawhub update
clawhub list
```

### 工具调用速查表

#### 文件操作
```markdown
读取文件：
read path="/path/to/file.md"

写入文件：
write path="/path/to/file.md" content="内容"

编辑文件（精确替换）：
edit path="/path/to/file.md" oldText="原文" newText="新内容"
```

#### 命令执行
```markdown
执行简单命令：
exec command="ls -la"

后台运行长时间任务：
exec command="python3 script.py" yieldMs=30000

PTY 模式（需要交互）：
exec command="vim file.txt" pty=true
```

#### 网络搜索
```markdown
使用 searxng（推荐）：
调用 searxng 技能

使用 web_search：
web_search query="关键词" count=5

抓取网页：
web_fetch url="https://example.com"
```

#### 浏览器自动化
```markdown
打开网页：
browser action="open" url="https://example.com"

获取快照：
browser action="snapshot"

点击元素：
browser action="act" kind="click" ref="e12"

输入文本：
browser action="act" kind="type" text="内容" ref="搜索框"
```

#### 消息发送
```markdown
发送消息：
message action="send" message="内容"

发送到指定渠道：
message action="send" channel="dingtalk" message="内容"

发送文件：
message action="send" path="/path/to/file.pdf"
```

#### 子智能体管理
```markdown
创建子智能体：
sessions_spawn task="任务描述" runtime="subagent" mode="run"

查看子智能体：
subagents action="list"

指导子智能体：
subagents action="steer" message="新指令"

终止子智能体：
subagents action="kill" target="子智能体 ID"
```

### 常见错误排查

| 错误现象 | 可能原因 | 解决方案 |
|----------|----------|----------|
| Gateway 无法启动 | 端口被占用 | `lsof -i :端口号` 查看并关闭占用进程 |
| 技能无法加载 | SKILL.md 格式错误 | 检查 YAML/Markdown 语法 |
| 浏览器无法连接 | Chrome 未开启远程调试 | `chrome://inspect` 开启调试端口 |
| 消息发送失败 | API 密钥过期 | 重新配置 channel 密钥 |
| 文件读取失败 | 路径错误或权限不足 | 检查文件路径和读写权限 |
| 网络搜索无结果 | API 密钥缺失 | `openclaw configure --section web` |
| 子智能体无响应 | 任务超时 | 增加 timeoutSeconds 或优化任务 |

### 实战检查清单

#### 部署前检查
- [ ] OpenClaw 版本最新
- [ ] Gateway 服务正常运行
- [ ] 消息通道配置正确
- [ ] 工作目录权限正确
- [ ] 必要技能已安装

#### 日常运维检查
- [ ] 检查 memory 文件是否正常写入
- [ ] 验证 HEARTBEAT 任务执行
- [ ] 清理过期的临时文件
- [ ] 备份 MEMORY.md 等重要文件
- [ ] 查看日志有无错误

#### 新技能安装检查
- [ ] 使用 skill-vetter 技能安全检查
- [ ] 验证 SKILL.md 格式
- [ ] 测试技能触发条件
- [ ] 确认权限范围合理
- [ ] 记录到已安装技能列表

### 工具速查表
| 工具 | 用途 | 示例 |
|------|------|------|
| read | 读文件 | `read path="file.md"` |
| write | 写文件 | `write path="file.md" content="..."` |
| edit | 编辑文件 | `edit path="file.md" oldText="..." newText="..."` |
| exec | 执行命令 | `exec command="ls -la"` |
| web_search | 搜索 | `web_search query="关键词"` |
| browser | 浏览器 | `browser action="open" url="..."` |
| message | 发消息 | `message action="send" message="..."` |

---

**课件制作日期：** 2026 年 4 月 14 日  
**适用场景：** OpenClaw 培训/智能体开发教学/技术分享  
**版本：** v1.0
