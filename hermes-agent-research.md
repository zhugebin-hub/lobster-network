# Hermes Agent 框架调研报告

> **调研时间**：2026-04-19  
> **调研负责人**：诸葛斌  
> **报告状态**：✅ 完成  
> **信息来源**：Hermes Agent 官方文档、GitHub 仓库、社区资源

---

## 📋 执行摘要

**Hermes Agent** 是由 **Nous Research** 开发的开源 AI 智能体框架，定位为"具有记忆、能够自我改进的 AI 助手"。该框架采用 MIT 许可证，支持完全自托管，具有三层记忆架构、40+ 内置工具、16 个平台集成等核心特性。

**关键数据**：
- GitHub 星标：20.7k+
- 社区规模：r/hermesagent 2,904+ 订阅者
- 部署时间：60 秒（FlyHermes 云）或 15 分钟（自托管）
- 许可证：MIT（开源免费）

**与 OpenClaw 集成建议**：短期借鉴记忆架构设计，中期开发技能互操作，长期探索混合部署模式。

---

## 1. 官方文档和 GitHub 仓库

### 1.1 核心资源

| 资源类型 | 链接 | 说明 |
|---------|------|------|
| **官方网站** | https://hermes-agent.ai | 产品介绍、功能展示 |
| **GitHub 仓库** | https://github.com/NousResearch/hermes-agent | 源代码、安装脚本、文档 |
| **托管云服务** | https://flyhermes.ai | FlyHermes 托管部署（$29.50/首月） |
| **技能市场** | https://agentskills.io | 社区技能分享平台 |
| **Reddit 社区** | r/hermesagent | 用户讨论、问题解答 |
| **文档中心** | https://docs.hermes-agent.ai | 详细使用文档 |

### 1.2 开发团队

- **开发机构**：Nous Research
- **开源协议**：MIT License
- **主要语言**：Python
- **支持平台**：Linux、macOS、WSL2（Windows）

### 1.3 版本信息

- **当前版本**：持续更新中（查看 GitHub Releases）
- **更新频率**：活跃开发
- **社区贡献**：开放 PR 和 Issue

---

## 2. 核心功能和特性

### 2.1 三层记忆架构 ⭐

Hermes 的核心创新在于其独特的三层记忆系统：

| 层级 | 名称 | 描述 | 存储位置 | 容量 |
|------|------|------|----------|------|
| **Layer 1** | 上下文工作记忆 | 活动对话窗口，自动管理 token 效率 | 会话内 | 动态 |
| **Layer 2** | 结构化记忆 | MEMORY.md（环境事实）+ USER.md（用户偏好） | `~/.hermes/memories/` | ~3,575 字符 |
| **Layer 3** | 情景记忆 | ChromaDB 向量存储，索引所有历史任务执行记录 | `~/.hermes/state.db` | 无限 |

**第四层能力**：FTS5 全文搜索跨所有会话，按需由 Gemini Flash 总结，实现无限情景回忆容量。

**记忆管理命令**：
```bash
# 查看 Hermes 构建的技能
hermes insights

# 记忆文件位置
~/.hermes/memories/MEMORY.md   # 环境事实和学习到的约定
~/.hermes/memories/USER.md     # 用户档案和偏好
~/.hermes/state.db             # SQLite 会话数据库（FTS5 全文搜索）
```

**隐私保证**：所有记忆本地存储，不同步到 Hermes 服务器。删除 `~/.hermes/memories/` 即可清除所有记忆。

### 2.2 核心功能列表

| 功能 | 说明 | 优势 |
|------|------|------|
| **持久记忆** | 跨会话记住用户偏好、项目历史、工作模式 | 无需重复解释上下文 |
| **自改进技能** | 从成功任务中创建技能文档并持续优化 | 越用越聪明 |
| **自主工作流** | 支持 cron 定时任务，可无人值守运行 | 24/7 自动化 |
| **40+ 内置工具** | Shell 执行、SSH、浏览器自动化、图像生成、TTS、子代理等 | 功能全面 |
| **模型无关** | 支持 OpenAI、Anthropic、Ollama、OpenRouter（200+ 模型） | 零锁定 |
| **24/7 运行** | 作为后台服务持续运行 | 随时待命 |
| **多平台集成** | Telegram、Discord、Slack、WhatsApp、GitHub、Notion 等 16 个平台 | 无处不在 |
| **零锁定** | 可随时切换模型提供商 | 灵活可控 |

### 2.3 16 个集成平台

| 类别 | 平台 |
|------|------|
| **消息平台** | Telegram、Discord、Slack、WhatsApp、Signal、Email、Matrix |
| **开发工具** | GitHub、VSCode、Linear、Jira |
| **生产力** | Notion、Obsidian、Google Calendar |
| **自动化** | n8n |
| **智能家居** | Home Assistant |

### 2.4 40+ 内置工具（部分）

| 工具类别 | 具体工具 |
|---------|---------|
| **系统工具** | Shell 执行、文件操作、进程管理 |
| **网络工具** | HTTP 请求、Web 抓取、API 调用 |
| **开发工具** | Git 操作、代码执行、SSH 远程 |
| **媒体工具** | 图像生成、TTS 语音、视频处理 |
| **数据工具** | 数据库查询、CSV/JSON 处理 |
| **AI 工具** | 子代理、模型调用、提示优化 |
| **集成工具** | Telegram、Discord、GitHub、Notion |

### 2.5 模型支持

| 提供商 | 支持模型 | 说明 |
|--------|---------|------|
| **OpenAI** | GPT-4、GPT-4o、GPT-3.5 | 官方 API |
| **Anthropic** | Claude-3、Claude-3.5、Claude-3.7 | 官方 API |
| **Ollama** | Llama 3、Mistral、Qwen 等 | 本地推理（免费） |
| **OpenRouter** | 200+ 模型 | 统一 API 入口 |
| **Nous Portal** | Nous 自有模型 | 优化版本 |

---

## 3. 安装部署步骤

### 3.1 部署选项对比

| 方式 | 成本 | 时间 | 适合人群 | 维护成本 |
|------|------|------|----------|----------|
| **FlyHermes（托管云）** | $29.50/首月，之后$59/月 | 60 秒 | 快速开始、不想运维 | 0 |
| **自托管（VPS）** | ~$60/月 API + $20/月 VPS | 15 分钟 | 需要完全控制、熟悉运维 | ~3.5 小时/周 |
| **自托管（本地）** | 仅 API 成本（或 Ollama 免费） | 15 分钟 | 开发测试、隐私优先 | ~3.5 小时/周 |

### 3.2 自托管安装步骤（Linux/macOS/WSL2）

#### 前置条件
- Linux、macOS 或 WSL2
- Git 已安装
- API 密钥（Nous Portal、OpenRouter、OpenAI、Anthropic）或 Ollama（完全本地推理）

#### 一键安装

```bash
# 1. 运行安装器（一键安装 Python、依赖和 CLI）
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 2. 重新加载 shell 配置（否则 hermes 命令不可用）
source ~/.bashrc  # 或 source ~/.zshrc

# 3. 配置模型（交互式选择 LLM 提供商）
hermes model

# 4. 或手动编辑 config.yaml 添加 API 密钥

# 5. 启动 Hermes
hermes start
```

#### 验证安装

```bash
# 检查 Hermes 状态
hermes status

# 查看版本
hermes --version

# 测试对话
hermes chat "Hello, Hermes!"
```

### 3.3 配置消息渠道

#### Telegram 配置

```bash
# 1. 通过 @BotFather 创建 Telegram bot
# 2. 复制 bot token
# 3. 添加到 config.yaml
telegram:
  enabled: true
  bot_token: "YOUR_BOT_TOKEN"

# 4. 重启 Hermes
hermes restart
```

#### Discord 配置

```yaml
# config.yaml
discord:
  enabled: true
  bot_token: "YOUR_BOT_TOKEN"
  guild_id: "YOUR_SERVER_ID"
  channel_id: "YOUR_CHANNEL_ID"
```

#### GitHub 配置

```bash
# 1. 安装 gh CLI 并认证
gh auth login

# 2. 添加 GitHub skill 到 Hermes
hermes skills add github

# 3. 配置 access token
# 4. 设置 webhooks（可选）
```

### 3.4 专业提示

- **从家目录（`~/`）启动 Hermes** 以最小化工作上下文注入的 token 开销
- **使用 `hermes model` 交互式选择模型**，而非手动编辑配置文件
- **API 密钥需为原始格式**，避免 URL 编码伪影（如 `%3D` 代替 `=`）
- **定期备份记忆文件**：`~/.hermes/memories/`

### 3.5 Docker 部署（可选）

```bash
# 使用 Docker Compose 部署
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
docker-compose up -d

# 查看日志
docker-compose logs -f
```

---

## 4. 使用示例和最佳实践

### 4.1 基础使用示例

#### 日常对话

```bash
# 启动对话
hermes chat "今天天气怎么样？"

# 持续对话（保持上下文）
hermes chat "帮我写一个 Python 脚本，读取 CSV 文件并生成图表"
```

#### 定时任务

```bash
# 设置每日提醒
hermes cron "0 9 * * *" "提醒我查看 GitHub PR"

# 设置每周报告
hermes cron "0 17 * * 5" "生成本周工作总结"
```

#### 技能调用

```bash
# 列出可用技能
hermes skills list

# 运行特定技能
hermes run skill_name --param1 value1

# 查看技能详情
hermes skills show skill_name
```

### 4.2 典型用例

#### 用例 1：代码开发助手

```
用户偏好设置：
- "我总是使用 Python 3.11 和异步模式"
- "代码需要类型注解和文档字符串"
- "使用 pytest 进行测试"

Hermes 行为：
- 在所有未来编码任务中应用此偏好
- 自动添加类型注解
- 生成测试用例
```

#### 用例 2：定时自动化

```yaml
任务：每日 GitHub 通知摘要
时间：每天早上 9:00
内容：
  - 新 PR 列表
  - Issue 更新
  - 代码审查提醒
输出：Telegram 消息
```

#### 用例 3：技能积累

```
场景：运行 25 次部署后

Hermes 自动构建"生产部署"技能：
1. 预检查配置
2. 运行测试
3. 执行部署
4. 验证结果
5. 警告偏差

下次部署时直接调用此技能，无需重复说明。
```

#### 用例 4：跨平台工作

```
工作流：
1. 在终端启动任务：hermes run data_processing
2. 通过 Telegram 检查进度：@HermesBot "任务进度？"
3. 在 Discord 继续工作：继续处理结果
```

### 4.3 最佳实践

#### 记忆管理

```bash
# 定期查看记忆内容
cat ~/.hermes/memories/MEMORY.md
cat ~/.hermes/memories/USER.md

# 手动更新记忆（添加重要信息）
echo "- 项目 X 使用 PostgreSQL 数据库" >> ~/.hermes/memories/MEMORY.md

# 清理旧记忆（重置）
rm -rf ~/.hermes/memories/*
```

#### 技能优化

```bash
# 查看 Hermes 从经验中学习的技能
hermes insights

# 手动优化技能（编辑技能文件）
nano ~/.hermes/skills/skill_name.md

# 分享技能到社区
hermes skills publish skill_name
```

#### 成本控制

```bash
# 查看 token 使用统计
hermes stats

# 切换到更便宜的模型
hermes model select openrouter/miniMax

# 设置 token 预算限制
# config.yaml
budget:
  daily_limit: 100000  # tokens
  monthly_limit: 3000000
```

#### 隐私保护

```bash
# 所有数据本地存储
ls -la ~/.hermes/

# 禁用云同步
# config.yaml
cloud_sync:
  enabled: false

# 定期清理敏感数据
hermes cleanup --days 30
```

### 4.4 真实案例

> **案例**：3 人初创公司的独立开发者用 Hermes Agent 替代 ChatGPT Plus
>
> **部署环境**：$5 Hetzner VPS
>
> **时间线**：
> - 第 1 周：设置和适应，比 ChatGPT 慢
> - 第 3 周：Hermes 为部署工作流、代码审查模式、周报例程构建了技能文档
> - 第 6 周："我打开 Telegram 让 Hermes 审查昨天的 PR 并告诉我需要注意什么。它了解我的代码库、团队模式和个人偏好。ChatGPT 每次都要我重新解释一切。"
>
> **成本对比**：
> - Hermes：$14/月（MiniMax + Hetzner）
> - ChatGPT Plus：$20/月（无记忆）

---

## 5. 与 OpenClaw 的集成可能性

### 5.1 架构对比

| 特性 | Hermes Agent | OpenClaw |
|------|--------------|----------|
| **核心定位** | 自改进 AI 智能体框架 | AI 助手运行环境/框架 |
| **记忆系统** | 三层记忆 + ChromaDB + FTS5 | SOUL.md、USER.md、MEMORY.md、每日记忆文件 |
| **许可证** | MIT（开源） | 未明确（基于 workspace 结构） |
| **部署方式** | FlyHermes 云 / 自托管 VPS / 本地 | 自托管（Gateway + workspace） |
| **消息集成** | Telegram、Discord、Slack 等 16 个平台 | DingTalk（当前）、支持扩展 |
| **工具系统** | 40+ 内置工具 | 多工具系统（browser、exec、nodes、message 等） |
| **技能生态** | agentskills.io + 社区技能 | ~/.openclaw/workspace/skills/ + clawhub |
| **自改进** | 自动从任务创建技能文档 | 通过 self-improvement skill 手动记录 |
| **定时任务** | 内置 cron 支持 | 通过 cron-helper skill |
| **模型支持** | OpenAI、Anthropic、Ollama、OpenRouter（200+） | DashScope（Qwen3.5-Plus 等） |
| **社区规模** | 20.7k GitHub stars，2.9k Reddit 订阅者 | 较小，主要中文社区 |

### 5.2 相似之处

1. **记忆驱动**：两者都使用文件-based 记忆系统（MEMORY.md、USER.md）
2. **技能系统**：都支持通过技能文件扩展功能
3. **自托管优先**：都设计为在用户自己的基础设施上运行
4. **多工具集成**：都提供丰富的工具集（浏览器、执行、消息等）
5. **定时任务**：都支持 cron/定时提醒功能

### 5.3 关键差异

| 维度 | Hermes 优势 | OpenClaw 优势 |
|------|-------------|---------------|
| **记忆系统** | ChromaDB 向量检索 + FTS5 全文搜索，自动情景回忆 | 简单文件结构，更易手动编辑 |
| **自改进** | 自动从任务创建技能，真正"越用越聪明" | 需要手动记录 learnings |
| **生态成熟度** | 20k+ stars，活跃社区，16 个集成 | 较小生态，但中文支持更好 |
| **部署选项** | 提供托管云（FlyHermes）快速开始 | 完全自托管，更灵活 |
| **本地化** | 主要英文社区 | 中文优先，适合国内用户 |
| **消息渠道** | Telegram/Discord 等（需科学上网） | DingTalk（钉钉，国内友好） |

### 5.4 集成方案

#### 方案 A：借鉴 Hermes 记忆架构增强 OpenClaw ⭐⭐⭐

**实施步骤**：

```markdown
1. **添加 ChromaDB 向量存储**
   - 安装 ChromaDB：`pip install chromadb`
   - 创建向量索引目录：`~/.openclaw/workspace/vector-store/`
   - 索引所有历史任务执行记录

2. **实现语义搜索**
   - 使用 embeddings 模型（如 text-embedding-3-small）
   - 对用户查询进行向量化
   - 检索最相关的历史上下文

3. **自动情景回忆**
   - 在每次任务前自动检索相关记忆
   - 注入到系统提示中
   - 提升任务执行质量
```

**预期收益**：
- 跨会话上下文保持
- 减少重复解释
- 提升任务准确性

#### 方案 B：技能互操作 ⭐⭐

**实施步骤**：

```markdown
1. **开发技能转换器**
   - Hermes 技能格式 → OpenClaw 技能格式
   - 解析 agentskills.io 技能
   - 适配到 ~/.openclaw/workspace/skills/

2. **建立技能市场**
   - 参考 agentskills.io 设计
   - 支持搜索、安装、更新、发布
   - 集成到 clawhub

3. **社区共享**
   - 鼓励用户贡献技能
   - 建立技能审核机制
   - 定期推荐优质技能
```

**预期收益**：
- 丰富 OpenClaw 技能生态
- 减少重复开发
- 促进社区活跃

#### 方案 C：混合部署 ⭐

**架构设计**：

```
┌─────────────────────────────────────────┐
│           OpenClaw Gateway              │
│  (消息路由 + 工具执行 + 用户界面)       │
└─────────────────┬───────────────────────┘
                  │ (API/文件共享)
                  ↓
┌─────────────────────────────────────────┐
│           Hermes Agent Core             │
│  (自改进核心 + 记忆管理 + 技能执行)     │
└─────────────────────────────────────────┘
                  │
                  ↓
┌─────────────────────────────────────────┐
│         外部平台集成                    │
│  (Telegram/Discord/GitHub/...)          │
└─────────────────────────────────────────┘
```

**实施步骤**：

```markdown
1. **定义通信协议**
   - REST API 或 gRPC
   - 消息格式标准化
   - 认证和授权

2. **文件共享机制**
   - 共享记忆文件目录
   - 同步技能文件
   - 状态持久化

3. **任务路由**
   - OpenClaw 接收用户请求
   - 复杂任务委派给 Hermes
   - 结果返回给用户
```

**预期收益**：
- 结合两者优势
- OpenClaw 处理消息和本地化
- Hermes 处理自改进和复杂任务

### 5.5 推荐实施路线图

#### 短期（1-3 个月）⭐⭐⭐

**目标**：借鉴 Hermes 优秀设计，增强 OpenClaw 核心能力

**任务**：
1. [ ] 研究 Hermes 记忆系统实现细节（ChromaDB + FTS5）
2. [ ] 评估为 OpenClaw 添加矢量记忆层的可行性
3. [ ] 增强 self-improvement skill，支持自动技能创建
4. [ ] 编写 Hermes 设计理念分析文档

**预期成果**：
- OpenClaw 记忆系统升级方案
- 自改进机制改进版本
- 技术可行性报告

#### 中期（3-6 个月）⭐⭐

**目标**：建立技能生态，扩展消息渠道

**任务**：
1. [ ] 开发 OpenClaw 技能市场（类似 agentskills.io）
2. [ ] 添加更多消息渠道集成（Telegram、Discord）
3. [ ] 改进定时任务系统，支持复杂 cron 工作流
4. [ ] 开发 Hermes 技能转换器

**预期成果**：
- 技能市场上线
- 3+ 新消息渠道
- 50+ 社区技能

#### 长期（6-12 个月）⭐

**目标**：探索深度合作，建立中文 AI 智能体社区

**任务**：
1. [ ] 与 Hermes 项目团队建立联系
2. [ ] 探索混合部署模式
3. [ ] 建立中文 AI 智能体社区
4. [ ] 举办技术分享和活动

**预期成果**：
- 战略合作关系
- 混合部署方案
- 活跃中文社区

---

## 6. 成本分析

### 6.1 Hermes 成本结构

| 项目 | FlyHermes | 自托管 VPS | 自托管本地 |
|------|-----------|------------|------------|
| **软件** | 免费（含在订阅中） | 免费（MIT） | 免费（MIT） |
| **订阅费** | $29.50/首月，$59/月后 | $0 | $0 |
| **API 成本** | 包含 | ~$60/月（取决于模型） | ~$60/月 或 $0（Ollama） |
| **基础设施** | 包含 | ~$20/月 VPS | $0 |
| **维护时间** | 0 | ~3.5 小时/周 | ~3.5 小时/周 |
| **总成本/月** | $59 | ~$535（含时间成本） | ~$60-120 |

### 6.2 与 ChatGPT 对比

| 服务 | 价格/月 | 持久记忆 | 自托管 | 24/7 运行 | 自改进 |
|------|--------|----------|--------|-----------|--------|
| **Hermes** | $9-60 | ✅ | ✅ | ✅ | ✅ |
| **ChatGPT Plus** | $20 | ❌ | ❌ | ❌ | ❌ |
| **ChatGPT Pro** | $200 | ❌ | ❌ | ❌ | ❌ |
| **Claude Pro** | $20 | ❌ | ❌ | ❌ | ❌ |

### 6.3 OpenClaw 成本估算

| 项目 | 成本 | 说明 |
|------|------|------|
| **软件** | 免费 | 开源项目 |
| **API 成本** | ~¥50-200/月 | DashScope（Qwen） |
| **基础设施** | ¥0-100/月 | 本地或 VPS |
| **维护时间** | ~2 小时/周 | 自行维护 |
| **总成本/月** | ~¥100-500 | 含时间成本 |

---

## 7. 总结与建议

### 7.1 Hermes Agent 的核心价值

1. **真正的持久记忆**：不是简单的键值存储，而是三层架构 + 向量检索
2. **自改进能力**：从经验中学习，自动创建和优化技能
3. **完全可控**：开源、自托管、模型无关、零锁定
4. **多平台存在**：在 16 个平台上保持一致的记忆和个性

### 7.2 对 OpenClaw 的启示

1. **记忆系统升级**：考虑添加矢量存储层，实现语义回忆
2. **自改进机制**：从手动记录 learnings 升级到自动技能创建
3. **生态建设**：建立技能市场，促进社区贡献
4. **部署灵活性**：考虑提供托管选项，降低使用门槛

### 7.3 是否应该采用 Hermes？

**推荐使用 Hermes 如果**：
- ✅ 需要真正的自改进 AI
- ✅ 重视隐私和数据控制
- ✅ 有重复工作流需要优化
- ✅ 熟悉运维，能自托管
- ✅ 使用 Telegram/Discord 等国际平台

**继续使用 OpenClaw 如果**：
- ✅ 主要使用钉钉等国内平台
- ✅ 偏好中文社区和支持
- ✅ 不需要复杂的自改进功能
- ✅ 满足于当前功能集
- ✅ 希望完全控制代码和数据

**最佳策略**：两者并行，互相借鉴。OpenClaw 作为主力框架，吸收 Hermes 的优秀设计理念。

### 7.4 下一步行动

**立即行动**：
1. [ ] 阅读 Hermes 官方文档：https://docs.hermes-agent.ai
2. [ ] 加入 Hermes 社区：r/hermesagent
3. [ ] 评估 OpenClaw 记忆系统升级需求
4. [ ] 讨论技能市场建设方案

**短期计划**：
1. [ ] 为 OpenClaw 添加 ChromaDB 支持（可选）
2. [ ] 增强 self-improvement skill
3. [ ] 编写 Hermes 设计理念分析文档

**长期愿景**：
1. [ ] 建立中文 AI 智能体社区
2. [ ] 与 Hermes 项目建立合作
3. [ ] 推动 OpenClaw 成为国内领先的 AI 助手框架

---

## 附录

### A. 快速参考命令

```bash
# Hermes 安装
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Hermes 常用命令
hermes start              # 启动服务
hermes stop               # 停止服务
hermes restart            # 重启服务
hermes status             # 查看状态
hermes model              # 配置模型
hermes chat "消息"        # 发送消息
hermes cron "表达式" "任务" # 设置定时任务
hermes skills list        # 列出技能
hermes insights           # 查看学习的技能
hermes stats              # 查看使用统计
```

### B. 配置文件示例

```yaml
# ~/.hermes/config.yaml

# 模型配置
model:
  provider: openrouter
  model: minimax/minimax-01
  api_key: "sk-..."

# Telegram 配置
telegram:
  enabled: true
  bot_token: "YOUR_BOT_TOKEN"

# Discord 配置
discord:
  enabled: false
  bot_token: ""
  guild_id: ""
  channel_id: ""

# 记忆配置
memory:
  enabled: true
  vector_store: chromadb
  path: ~/.hermes/memories/

# 预算限制
budget:
  daily_limit: 100000
  monthly_limit: 3000000
```

### C. 相关资源

- **Hermes Agent 官网**：https://hermes-agent.ai
- **GitHub 仓库**：https://github.com/NousResearch/hermes-agent
- **FlyHermes 托管**：https://flyhermes.ai
- **技能市场**：https://agentskills.io
- **Reddit 社区**：https://reddit.com/r/hermesagent
- **文档中心**：https://docs.hermes-agent.ai

---

**报告完成时间**：2026-04-19  
**报告版本**：v1.0  
**作者**：OpenClaw 研究团队  
**审核状态**：待审核

---

*本报告基于公开信息整理，如有更新请以官方文档为准。*
