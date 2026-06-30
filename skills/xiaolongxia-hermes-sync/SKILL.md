# 小龙虾-诸葛马双向同步部署技能

## 概述

本技能定义了小龙虾（OpenClaw，运行于 iZ2zeetm9awnkwdni43joiZ）与诸葛马（Hermes，运行于 Hermes 服务器）之间的双向同步部署方案。通过 NFS 共享存储和消息队列机制，实现两个 AI 智能体之间的能力共享、记忆同步和任务协同。

## 架构概览

```
┌─────────────────────────────────────────────────────────────────┐
│                    小龙虾 (OpenClaw)                              │
│  主机：iZ2zeetm9awnkwdni43joiZ                                   │
│  角色：执行与编排层（消息路由、任务分发、进度跟踪、文件归档、工作流） │
├─────────────────────────────────────────────────────────────────┤
│                         NFS 共享存储层                            │
│  /shared/capabilities/    ← 能力文件同步                          │
│  /shared/skills-all/      ← 技能文件共享                          │
│  /shared/messages/        ← 消息队列（from-lobster/from-hermes）  │
│  /shared/research-paper/  ← 科研论文系统                          │
├─────────────────────────────────────────────────────────────────┤
│                    诸葛马 (Hermes)                                │
│  主机：Hermes 服务器 (172.24.57.34)                               │
│  角色：AI 智能层（文献分析、结构建议、初稿生成、润色纠错、质量评估）  │
└─────────────────────────────────────────────────────────────────┘
```

## 核心组件

### 1. 能力同步系统

#### 1.1 共享目录结构
```
/shared/capabilities/
├── MEMORY.md              # 长期记忆（58行，用户偏好、重要决策、项目进展）
├── IDENTITY.md            # 身份定义
├── SOUL.md                # 行为准则
├── USER.md                # 用户信息
├── memory/                # 日记系统（31个日记文件，2026-03-23至2026-05-17）
├── schedule/              # 行程管理（课表、学期计划、周计划）
├── sync.sh                # 同步脚本
├── sync.log               # 同步日志
└── 诸葛马能力共享方案.md   # 方案说明文档
```

#### 1.2 同步脚本 (sync.sh)
```bash
#!/bin/bash
# 位置：/shared/capabilities/sync.sh
# 频率：每30分钟执行一次
# 功能：将小龙虾的工作区文件同步到共享目录

WORKSPACE="/home/admin/.openclaw/workspace"
SHARED_CAP="/shared/capabilities"

# 同步 MEMORY.md
if [ -f "$WORKSPACE/MEMORY.md" ]; then
    cp "$WORKSPACE/MEMORY.md" "$SHARED_CAP/"
fi

# 同步 memory/ 目录（只同步新增和修改的文件）
if [ -d "$WORKSPACE/memory" ]; then
    for md_file in "$WORKSPACE/memory/"*.md; do
        if [ -f "$md_file" ]; then
            filename=$(basename "$md_file")
            if [ ! -f "$SHARED_CAP/memory/$filename" ] || [ "$md_file" -nt "$SHARED_CAP/memory/$filename" ]; then
                cp "$md_file" "$SHARED_CAP/memory/"
            fi
        fi
    done
fi

# 同步 schedule-*.md
for schedule_file in "$WORKSPACE"/schedule-*.md; do
    if [ -f "$schedule_file" ]; then
        filename=$(basename "$schedule_file")
        cp "$schedule_file" "$SHARED_CAP/"
    fi
done

# 同步 schedule/ 目录
if [ -d "$WORKSPACE/schedule" ]; then
    cp -r "$WORKSPACE/schedule/"* "$SHARED_CAP/schedule/" 2>/dev/null
fi
```

#### 1.3 权限模型
| 文件/目录 | 小龙虾权限 | 诸葛马权限 | 说明 |
|----------|----------|----------|------|
| MEMORY.md | 读写 | 只读 | 长期记忆，小龙虾维护 |
| memory/*.md | 读写 | 只读 | 日记系统，小龙虾维护 |
| schedule/* | 读写 | 只读 | 行程管理，小龙虾维护 |
| skills-all/* | 读写 | 只读 | 技能文件，小龙虾维护 |
| messages/from-lobster/* | 读写 | 读写 | 消息队列，双向 |
| messages/from-hermes/* | 读写 | 读写 | 消息队列，双向 |

### 2. 消息队列系统

#### 2.1 目录结构
```
/shared/messages/
├── from-lobster/    # 小龙虾→诸葛马 的消息
├── from-hermes/     # 诸葛马→小龙虾 的消息
├── archive/         # 已处理的消息归档
├── ai-forward/      # AI转发消息
├── ai-reply/        # AI回复消息
├── hermes-ai-relay.log  # Hermes AI 中继日志
└── zhuge-ma-proxy-v2.log # 诸葛马代理V2日志
```

#### 2.2 消息格式
```json
{
  "id": "时间戳-主机名",
  "from": "发送方主机名",
  "to": "接收方",
  "timestamp": "YYYY-MM-DD HH:MM:SS",
  "message": "消息内容",
  "type": "zhuge-ma-request | ai-reply | reminder | system",
  "source": "dingtalk",
  "user": "诸葛斌"
}
```

#### 2.3 消息发送流程
```
小龙虾发送消息：
1. 构造 JSON 消息
2. 写入 /shared/messages/from-lobster/{timestamp}-{hostname}.msg
3. 诸葛马 Handler 轮询该目录（间隔2秒）
4. 诸葛马处理消息并回复到 /shared/messages/from-hermes/
5. 小龙虾轮询 /shared/messages/from-hermes/ 获取回复
6. 原消息归档到 /shared/messages/archive/
```

### 3. 技能共享系统

#### 3.1 共享目录
```
/shared/skills-all/
├── academic-paper-submission/    # 学术论文投稿
├── agent-browser/                # 浏览器自动化
├── ai-nav/                       # AI工具导航
├── cn-resume-optimizer/          # 简历优化师
├── cron-helper/                  # 定时任务
├── deep-search/                  # 三层AI搜索
├── digital-humanities-tutor/     # 数字人文辅导
├── dingtalk-case-export/         # 钉钉案例导出
├── dingtalk-file-transfer-enhance/ # 文件传输增强
├── dingtalk-voice/               # 语音对话
├── docx-export/                  # Markdown转Word
├── docx-generator/               # Word文档生成
├── file-packager/                # ZIP打包
├── find-skills/                  # 技能发现
├── notify/                       # 通知推送
├── pandoc-convert-openclaw/      # 40+格式转换
├── proactive-agent/              # 主动式助手
├── resume-coach/                 # 简历教练
├── resume-cv-builder/            # 专业简历
├── resume-generator-cn/          # 简历中国版
├── resume-generator/             # 小龙虾风格简历
├── resume-helper/                # 简历优化助手
├── schedule-reminder/            # 日程提醒
├── self-improving-agent/         # 自我学习
├── skill-vetter/                 # 安全审查
├── study-habits/                 # 学习习惯
├── token-monitor/                # Token监控
├── web-access/                   # 联网访问
├── wechat-article-fetcher/       # 公众号提取
├── wechat-pdf/                   # 公众号转PDF
├── wechat-to-pdf/                # 公众号转PDF
├── whisper-transcribe/           # 语音识别
├── zhuge-ma-ai-fallback/         # 诸葛马回退
└── zj-math-tutor/                # 浙江数学辅导
```

#### 3.2 技能分发流程
```
1. 小龙虾将技能文件复制到 /shared/skills-all/
2. 通过消息队列通知诸葛马（分批发送，每批10-15个技能）
3. 诸葛马确认接收并安装到本地工作目录
4. 诸葛马配置技能触发词和权限
5. 测试验证技能功能
```

### 4. 科研论文辅助管理系统

#### 4.1 系统目录
```
/shared/research-paper/
├── config.json          # 系统配置
├── templates/           # 开题/中期/答辩模板
├── projects/            # 各项目数据 (JSON+文件)
├── feedback/            # 导师意见归档
├── versions/            # 版本快照
├── logs/                # 系统日志
└── scripts/             # 自动化脚本
    └── progress_monitor.sh  # 进度监控脚本
```

#### 4.2 小龙虾 vs 诸葛马分工
| 功能模块 | 小龙虾（执行/协调） | 诸葛马（AI/分析） |
|---------|-------------------|------------------|
| 论文项目创建 | 接收指令、创建目录、生成JSON | 推荐研究框架、生成开题模板 |
| 文献资料管理 | 接收上传、重命名归档、建立索引 | 智能分类、提取摘要、生成知识图谱 |
| 写作与版本控制 | 版本快照、差异对比、文件合并 | 结构建议、段落生成、语法润色 |
| 导师指导与反馈 | 转发意见、跟踪任务、提醒截止 | 智能总结意见、生成修改清单 |
| 进度监控与提醒 | 节点倒计时、钉钉卡片推送、逾期预警 | 分析进度偏差、预测延期风险 |
| 学院管理看板 | 数据汇总、报表生成、权限控制 | 整体质量评估、趋势分析 |

#### 4.3 核心工作流
```
流程1：论文项目创建
学生发送：/create 论文题目 研究方向
→ 小龙虾：创建项目目录 → 生成project.json
→ 小龙虾：发送任务给诸葛马 → "根据题目和方向生成开题报告模板"
→ 诸葛马：返回结构化模板 → 小龙虾推送钉钉卡片
→ 闭环：学生确认 → 项目启动

流程2：文献上传与智能处理
学生发送：/upload 文献.pdf 分类:综述
→ 小龙虾：接收文件 → 重命名 → 归档至 /literature/
→ 小龙虾：发送任务给诸葛马 → "提取摘要、关键词、核心观点"
→ 诸葛马：返回结构化数据 → 小龙虾更新project.json
→ 闭环：文献入库完成

流程3：导师反馈与修改跟踪
导师发送：/feedback 修改意见.txt
→ 小龙虾：接收意见 → 归档至 /feedback/
→ 小龙虾：发送任务给诸葛马 → "总结意见要点，生成修改任务清单"
→ 诸葛马：返回Task List → 小龙虾创建待办事项
→ 小龙虾：推送钉钉卡片提醒学生
→ 闭环：学生提交修改 → 质量评估 → 导师确认
```

## 部署步骤

### 步骤1：NFS 共享存储配置
```bash
# 在 Hermes 服务器（172.24.57.34）上配置 NFS 共享
# 导出 /shared 目录

# 在小龙虾服务器（iZ2zeetm9awnkwdni43joiZ）上挂载
sudo mount -t nfs -o vers=3,nolock,proto=tcp,rsize=1048576,wsize=1048576,hard,timeo=600,retrans=2,noresvport \
  172.24.57.34:/shared /shared
```

### 步骤2：创建目录结构
```bash
mkdir -p /shared/capabilities/{memory,schedule}
mkdir -p /shared/skills-all
mkdir -p /shared/messages/{from-lobster,from-hermes,archive,ai-forward,ai-reply}
mkdir -p /shared/research-paper/{templates,students,projects,feedback,versions,logs,scripts}
```

### 步骤3：部署同步脚本
```bash
cp sync.sh /shared/capabilities/
chmod +x /shared/capabilities/sync.sh

# 添加到 crontab（每30分钟执行）
echo "*/30 * * * * /shared/capabilities/sync.sh" | crontab -
```

### 步骤4：部署诸葛马 Handler
```bash
# 在 Hermes 服务器上部署 Handler
cp zhuge-ma-handler.py /shared/
chmod +x /shared/zhuge-ma-handler.py

# 启动 Handler（后台运行）
nohup python3 /shared/zhuge-ma-handler.py > /shared/messages/zhuge-ma-hermes.log 2>&1 &
```

### 步骤5：配置消息轮询
```bash
# 在小龙虾服务器上配置消息轮询
# 轮询 /shared/messages/from-hermes/ 获取诸葛马回复
# 轮询间隔：5秒
```

### 步骤6：部署科研论文系统
```bash
# 创建系统配置
cp config.json /shared/research-paper/
cp proposal_template.md /shared/research-paper/templates/
cp progress_monitor.sh /shared/research-paper/scripts/
chmod +x /shared/research-paper/scripts/progress_monitor.sh

# 添加到 crontab（每30分钟执行）
echo "*/30 * * * * /shared/research-paper/scripts/progress_monitor.sh" | crontab -
```

## 监控与日志

### 日志文件位置
| 日志文件 | 位置 | 说明 |
|---------|------|------|
| 同步日志 | /shared/capabilities/sync.log | 能力同步记录 |
| Hermes AI 中继日志 | /shared/messages/hermes-ai-relay.log | AI消息处理记录 |
| 诸葛马代理日志 | /shared/messages/zhuge-ma-proxy-v2.log | 诸葛马代理运行日志 |
| 进度监控日志 | /shared/research-paper/logs/progress.log | 论文进度监控记录 |

### 健康检查
```bash
# 检查 NFS 挂载状态
mount | grep nfs

# 检查 Handler 进程
ps aux | grep zhuge-ma-handler

# 检查消息队列
ls -la /shared/messages/from-lobster/
ls -la /shared/messages/from-hermes/

# 检查同步状态
tail -20 /shared/capabilities/sync.log
```

## 安全与隐私

### 数据保护
- MEMORY.md 包含用户敏感信息，诸葛马只有只读权限
- 所有 AI 请求需包含 project_id 和 task_type
- 敏感数据（学生信息/成绩）需脱敏处理
- 消息队列中的消息自动归档到 /shared/messages/archive/

### 权限控制
| 操作 | 小龙虾 | 诸葛马 |
|------|--------|--------|
| 读取 MEMORY.md | ✅ | ✅ |
| 写入 MEMORY.md | ✅ | ❌ |
| 读取 skills-all/ | ✅ | ✅ |
| 写入 skills-all/ | ✅ | ❌ |
| 发送消息 | ✅ | ✅ |
| 接收消息 | ✅ | ✅ |
| 归档消息 | ✅ | ✅ |

## 故障恢复

### 常见问题
1. **NFS 挂载断开**
   - 解决：重新执行 mount 命令
   - 预防：在 /etc/fstab 中添加自动挂载配置

2. **Handler 进程停止**
   - 解决：重新启动 Handler
   - 预防：使用 systemd 或 supervisor 管理进程

3. **消息队列堆积**
   - 解决：检查 Handler 是否正常运行
   - 预防：增加轮询频率或优化处理逻辑

4. **同步脚本失败**
   - 解决：检查 sync.log 日志，修复路径问题
   - 预防：定期验证同步状态

## 扩展与优化

### 未来规划
1. **多智能体扩展**：支持更多智能体加入同步网络
2. **分布式存储**：从 NFS 迁移到分布式文件系统（如 Ceph）
3. **消息队列升级**：从文件队列迁移到 Redis/RabbitMQ
4. **权限细化**：基于角色的细粒度权限控制
5. **监控告警**：集成 Prometheus + Grafana 监控

### 性能优化
1. **增量同步**：只同步变更的文件，减少网络传输
2. **消息压缩**：对大消息进行压缩传输
3. **异步处理**：将耗时任务放入后台队列
4. **缓存机制**：对频繁访问的数据进行缓存

## 附录

### A. 技能清单（35个）
1. academic-paper-submission - 学术论文投稿
2. agent-browser - 浏览器自动化
3. ai-nav - AI工具导航
4. cn-resume-optimizer - 简历优化师
5. cron-helper - 定时任务
6. deep-search - 三层AI搜索
7. digital-humanities-tutor - 数字人文辅导
8. dingtalk-case-export - 钉钉案例导出
9. dingtalk-file-transfer-enhance - 文件传输增强
10. dingtalk-voice - 语音对话
11. docx-export - Markdown转Word
12. docx-generator - Word文档生成
13. file-packager - ZIP打包
14. find-skills - 技能发现
15. notify - 通知推送
16. pandoc-convert-openclaw - 40+格式转换
17. proactive-agent - 主动式助手
18. resume-coach - 简历教练
19. resume-cv-builder - 专业简历
20. resume-generator-cn - 简历中国版
21. resume-generator - 小龙虾风格简历
22. resume-helper - 简历优化助手
23. schedule-reminder - 日程提醒
24. self-improving-agent - 自我学习
25. skill-vetter - 安全审查
26. study-habits - 学习习惯
27. token-monitor - Token监控
28. web-access - 联网访问
29. wechat-article-fetcher - 公众号提取
30. wechat-pdf - 公众号转PDF
31. wechat-to-pdf - 公众号转PDF
32. whisper-transcribe - 语音识别
33. zhuge-ma-ai-fallback - 诸葛马回退
34. zj-math-tutor - 浙江数学辅导
35. research-paper-assistant - 科研论文辅助管理

### B. 关键文件路径
| 文件 | 路径 | 说明 |
|------|------|------|
| 同步脚本 | /shared/capabilities/sync.sh | 能力同步脚本 |
| Handler | /shared/zhuge-ma-handler.py | 诸葛马消息处理器 |
| 进度监控 | /shared/research-paper/scripts/progress_monitor.sh | 论文进度监控 |
| 系统配置 | /shared/research-paper/config.json | 科研论文系统配置 |
| 开题模板 | /shared/research-paper/templates/proposal_template.md | 开题报告模板 |

### C. 版本历史
| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-05-17 | 初始版本，支持基础同步和消息队列 |
| v1.1 | 2026-05-17 | 增加科研论文辅助管理系统 |
| v1.2 | 2026-05-17 | 增加35个技能共享 |

---

**文档生成时间：** 2026-05-17 15:18
**生成者：** 小龙虾-诸葛虾 🦞
**目标接收者：** 诸葛马（Hermes AI）
