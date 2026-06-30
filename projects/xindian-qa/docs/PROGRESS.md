# 信电学院 AI 知识问答系统 - 项目进度

## 当前状态
- ✅ 知识库层：6门课程、77个知识块、本地RAG系统（DashScope Embedding + SQLite）
- ✅ 智能体层：百炼API Skill + 本地RAG回退 + 三级记忆路由 + Prompt模板 + 主入口
- ✅ 应用交互层：钉钉机器人对接代码 + 配置 + 测试通过
- ✅ 启动脚本：`start.sh`（server/test/status/stop）

## 已完成的工作

### 1. 知识库层 ✅
- [x] 百炼 API Key 配置（`~/.openclaw/config/bailian-kb.json`）
- [x] 项目目录结构创建
- [x] 教材资源检索（MIT OCW + 中国大学 MOOC）
- [x] 课程材料入库脚本（`scripts/ingest_course_materials.py`）
- [x] 本地 RAG 系统构建（DashScope Embedding + SQLite + 余弦相似度）
- [x] 6门课程教材入库（77个知识块）：
  - 电路分析基础（8章，302行）
  - 信号与系统（8章，303行）
  - 数字电子技术基础（8章，287行）
  - 通信原理（9章，337行）
  - 电磁场与电磁波（8章，386行）
  - 嵌入式系统开发（8章，414行）

### 2. 智能体层 ✅
- [x] 百炼 API Skill（带本地RAG回退）（`bailian_api_skill.py`）
  - 修复：generate_answer 使用 DashScope 兼容模式 API
  - 回退机制：百炼 API → 本地 RAG
- [x] 本地 RAG 系统（`local_rag.py`）
  - DashScope text-embedding-v3 向量
  - SQLite 存储文档和向量
  - 余弦相似度检索
  - DashScope qwen-plus 生成答案
- [x] 三级记忆路由系统（`memory_router.py`）
  - L1 工作记忆（会话上下文，内存）
  - L2 知识记忆（百炼RAG/本地RAG）
  - L3 长期记忆（用户画像、FAQ统计、对话摘要）
- [x] Prompt 模板系统（`prompt_templates.py`）
  - 系统Prompt、问答Prompt、意图识别、摘要提取、用户画像更新、FAQ生成
- [x] 主入口脚本（`main.py`）
  - 意图识别（课程知识/系统操作/闲聊）
  - 路由查询到三级记忆
  - 记忆沉淀

### 3. 应用交互层 ✅
- [x] 钉钉机器人配置（`app-layer/dingtalk_config.json`）
  - AppKey: dinguyiasfrbtjioamwc
  - 账号名：虾尔
- [x] 钉钉机器人对接代码（`app-layer/dingtalk_bot.py`）
  - HTTP Server 接收钉钉消息
  - 调用 QA 系统处理
  - 返回 JSON 回复
- [x] 启动脚本（`start.sh`）
  - server：启动服务
  - test：运行测试
  - status：查看状态
  - stop：停止服务

### 4. 测试验证 ✅
- [x] 本地 RAG 检索测试（4个查询全部返回正确结果）
- [x] 主系统完整测试（基尔霍夫定律、傅里叶变换）
- [x] 钉钉Bot模拟消息测试（课程问题 + 闲聊）
- [x] 三级记忆系统测试（FAQ统计、用户画像、对话摘要）

## 文件结构
```
projects/xindian-qa/
├── agent-layer/
│   ├── bailian_api_skill.py    # 百炼 API Skill（带本地RAG回退）
│   ├── local_rag.py            # 本地 RAG 系统
│   ├── memory_router.py        # 三级记忆路由
│   ├── prompt_templates.py     # Prompt 模板
│   └── main.py                 # 主入口
├── app-layer/
│   ├── dingtalk_config.json    # 钉钉配置
│   └── dingtalk_bot.py         # 钉钉机器人对接
├── knowledge-base/
│   ├── course_content/         # 6门课程教材
│   ├── course_materials/       # 原始教材文件
│   └── vector_db.sqlite        # 向量数据库
├── scripts/
│   └── ingest_course_materials.py  # 教材入库脚本
├── docs/
│   ├── PROJECT_PLAN.md         # 项目计划
│   └── PROGRESS.md             # 项目进度（本文件）
├── attachments/                # 附件
├── start.sh                    # 启动脚本
└── logs/                       # 日志目录
```

## L3 长期记忆
- 目录：`~/workspace/xindian-qa/l3-memory/`
- 文件：
  - `user_profiles.json` - 用户画像
  - `faq_stats.json` - 高频问题统计
  - `conversation_summaries.json` - 对话摘要

## 使用方式

### 启动服务
```bash
cd projects/xindian-qa
./start.sh server
```

### 运行测试
```bash
./start.sh test
```

### 查看状态
```bash
./start.sh status
```

### 停止服务
```bash
./start.sh stop
```

## 技术方案
- **百炼知识库 API 认证失败** → 自建本地 RAG 系统（DashScope Embedding + SQLite + 余弦相似度检索）
- **本地 RAG 测试效果**：基尔霍夫定律(0.590)、傅里叶变换(0.735)、触发器(0.732)、卷积(0.637)
- **系统自动回退**：百炼 API → 本地 RAG

## 待优化事项
1. [ ] 百炼知识库 API 认证问题（联系阿里云确认权限）
2. [ ] 更多课程教材内容入库
3. [ ] 钉钉机器人正式部署（需公网 IP 或内网穿透）
4. [ ] 意图识别优化（从规则匹配 → LLM 识别）
5. [ ] 回答质量评估和反馈机制
