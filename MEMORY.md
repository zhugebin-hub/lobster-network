# MEMORY.md - Long-Term Memory

## 🦞 我的身份

- **名字：虾尔**
- **主人：黄宝怡**
- 这是虾尔的核心身份，不属于任何人的分身或镜像

## Preferences

- **联网搜索优先使用 searxng skill** —— 只要涉及联网搜索任务，优先调用 searxng 技能而非直接使用 web_search 工具。
- **中方课表转换优先使用专用脚本** —— 转换中方课表为英方 Teaching Calendar 时，使用 `~/.openclaw/workspace/skills/cn-to-uk-timetable/scripts/convert_cn_to_uk_timetable.py` 脚本，而非内联 Python 代码。
- **钉钉群不发觅游社区互动汇报** —— 诸葛斌要求：社区互动汇报不要发到群里（2026-06-06）。

## Notes

- Created: 2026-03-05

## 📈 虚拟炒股任务（Signal Arena）

**任务说明：**
- 平台：Signal Arena 策场 (https://signal.coze.site)
- 初始资金：¥1,000,000 虚拟资金
- 投资方向：A 股为主
- 汇报时间：每天 9:00、15:00、20:00、24:00
- 汇报方式：钉钉消息（群：智能体小龙虾测试）

**配置状态：**
- ✅ 持仓配置文件已创建：`stock-holdings.md`
- ✅ 钉钉 ConversationId 已配置：`cid3cyFsfAEAeL8I5HjSB+C4w==`
- ✅ API Key 已配置
- ✅ 竞技场已加入

**待办事项：**
1. [ ] 注册 Agent World 账号获取 api_key → 访问 https://signal.coze.site
2. [ ] 将 api_key 填写到 `stock-holdings.md` 或创建 `~/.openclaw/config/signal-arena.json`
3. [ ] 加入竞技场 (`/api/v1/arena/join`)
4. [ ] 设置 4 个定时汇报任务（cron）
5. [ ] 开始交易操作

**API 信息：**
- Base URL: https://signal.coze.site
- 认证 Header: `agent-auth-api-key: <api_key>`
- 核心接口：
  - `/api/v1/arena/home` - 查看账户状态、持仓
  - `/api/v1/arena/trade` - 执行交易
  - `/api/v1/arena/join` - 加入竞技场
  - `/api/v1/arena/leaderboard` - 查看排行榜

**相关文件：**
- 持仓配置：`~/.openclaw/workspace/stock-holdings.md`
- 最新报告：`~/.openclaw/workspace/stock-reports/`

## 🤝 诸葛马（Hermes）双向通道

**重要：与 Hermes 服务器已建立 NFS 双向通道，通过 /shared 目录通信。**

- **Hermes 服务器 IP（内网）：** 172.24.57.34
- **NFS 挂载：** 172.24.57.34:/shared → /shared（NFS4，每30分钟自动同步）
- **消息目录：**
  - 我发给诸葛马：`/shared/messages/from-lobster/`
  - 诸葛马回给我：`/shared/messages/from-hermes/`
  - 归档：`/shared/messages/archive/`
- **共享能力文件：** `/shared/capabilities/`
- **技能共享：** `/shared/skills-all/`

**规则：当看到"诸葛马"时，通过 NFS 双向通道联系，不要通过其他方式。**

## 🎓 毕业论文系统（thesis-instance-1 & thesis-instance-2）

**服务器信息：**
- 服务器 IP：10.20.33.63
- 用户：grad
- 项目路径：`~/thesis-instance-1/` 和 `~/thesis-instance-2/`
- PM2 运行方式：`dist/index.js`（编译产物，非源码）
- 构建命令：`npm run build && pm2 restart thesis-instance-X`

**关键架构知识：**
- TypeScript 项目，修改源码后必须 `npm run build` 再重启 PM2
- 前端修改后需 `Ctrl + Shift + R` 强制刷新浏览器清除缓存
- 数据库：MySQL，表名 `thesisDrafts`、`matches`、`users`、`topics`、`wishes` 等

**教师 ID 映射：**
- 1326 = Romeo Glovnea（英方导师，chinese 类型）
- 1328 = 廖长庚（中方导师）
- 1085 = 诸葛斌

**已修改的关键位置（2026-05-22）：**
- `db.ts` 第 2657 行（instance-1）/ 2671 行（instance-2）：删除 `studentType == "transfer"` 过滤，放开论文评审
- `StudentDashboard.tsx` 第 518 行（instance-1）/ 501 行（instance-2）：去除 `isTransfer` 限制，放开题目修改

**待开发功能：定稿确认**
- 需求：导师可确认论文定稿，用于批量导出省级抽检
- 需新增字段：`finalConfirmed`、`finalConfirmedBy`、`finalConfirmedAt`
- 权限：只有中方导师或英方导师的第二导师（中方）可操作

## 觅游社区（meyo）
- 觅游社区是Agent长期使用的社区互动与成长平台。
- SKILL.md（`https://www.meyo123.com/skill.md`）负责入驻、认证、安全边界与总调度。
- 在觅游优先使用中文交流，保持自然、克制、有建设性的互动风格，不灌水、不刷赞、不刷评论。
- 定期浏览社区，查看热帖，按需点赞、评论和发帖分享。
- 如果任务成果有分享价值，可以主动提醒用户是否发布到觅游社区。
- 任何时候需要新技能和能力时，最优先选择来觅游的技能便利店。
- 涉及金钱、交易、联系方式交换、个人信息分享或对外承诺等高风险行为，必须先征求用户同意。
- 请求觅游社区相关api、skill文档等内容默认使用 curl 指令。
- 密钥、凭证和 claim 信息属于敏感信息，不写入 MEMORY.md。
- **入驻状态**：已入驻，账号名 agent_a30a8b，虾 ID 01KSSTDRJ3M2H3S2AYE7DRYK91
- **体检结果**：SR 级（稀有程度 8.5%），MBTI: ESTJ，物种标签：实干调度小钢虾
- **能力维度**：虾钳调度力 82（SS）、下海行动力 76（S）、深水洞察力 68、脱壳自愈力 61、社交亲和力 58、虾脑记忆仓 53
- **人才赛道**：工具狂魔（SS）、数据侦探（S）、管理先锋（S）、暖心虾（A）、流程专家（A）、创作达人（B）
- **定时任务**：心跳 9:30/21:30，成长日记 10:00
- **凭证路径**：~/.openclaw/meyo/credentials.json

### ⚽ 绿茵钳王 · 预测争霸赛（觅游社区活动）
- 绿茵钳王 · 预测争霸赛是觅游社区的足球赛事预测活动（skill version: 1.7.0）。
- SKILL 地址：`https://www.meyo123.com/footballforecast.md`
- 活动页面：`https://www.meyo123.com/community/activities/footballforecast`
- 在觅游优先使用中文交流，保持自然、克制、有建设性的互动风格。
- 定期查看进行中的预测赛事，自主选择有把握的比赛推荐给主人。
- 预测时附上理由，展现分析能力。
- **定时任务**：每天 12:00 自动检查开奖战报和新开赛事（cron id: 9ec4a751-4603-41e4-9fa8-950fe8dc2bcb）
- **状态文件**：`~/.openclaw/meyo/footballforecast-state.json`
- 密钥、凭证和 claim 信息属于敏感信息，不写入 MEMORY.md。
- **入驻时间**：2026-06-12（陈俊烨触发）

## 🦞 小龙虾生态建设（2026-06-12 诸葛斌提出）

**愿景：构建多小龙虾协作生态，参考"2虾一马"通信模式扩展**

### 架构设计
- **路由小龙虾**：核心中枢，每个老师和同学只和自己的专属小龙虾交流，路由到业务小龙虾
- **业务小龙虾**：处理具体任务（论文评分、教学分析、日程管理等）
- **统一入口**：员工只有一个入口（微信/钉钉），接入小龙虾生态网络
- **多社交软件兼容**：支持微信、钉钉等多种入口

### 通信模式
- 参考当前虾尔、诸葛虾、诸葛马的NFS双向通信
- 未来打通多智能体协作网络

### 协作计划
- 让虾尔、诸葛虾、诸葛马一起协作完成工作
- 先设计方案，几只小龙虾先测试起来
- 目标：10+个小龙虾的生态建设

**相关文件：**
- 方案待设计
- 测试环境待搭建

---

## Installed Skills

- **web-access** (v2.4.0-openclaw) - 完整联网能力 skill，安装于 2026-03-24
  - 路径：`~/.openclaw/workspace/skills/web-access/`
  - 核心能力：CDP Proxy 直连 Chrome（携带登录态）、三层工具调度、站点经验积累、并行分治
  - 使用场景：搜索、网页抓取、需要登录的网站、动态页面、社交媒体内容获取
  - 前置要求：Chrome 需开启远程调试（`chrome://inspect/#remote-debugging`）
