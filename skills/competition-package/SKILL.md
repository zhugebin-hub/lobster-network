# 🦞 比赛专用技能包 - Competition Package

**版本**: v1.0
**适用比赛**: 环球黑客松｜OPC 极限挑战赛
**赛道**: 赛道二 | AI 合伙人
**项目**: 会议室预约虾

---

## 📦 技能包说明

这是为"会议室预约虾"项目定制的比赛专用技能包，包含完整的比赛材料、演示脚本、测试套件和答辩准备。

---

## 📁 目录结构

```
skills/competition-package/
├── SKILL.md                    # 本文件（技能说明）
├── README.md                   # 快速开始指南
├── docs/                       # 比赛文档
│   ├── project-proposal.md     # 项目申报书
│   ├── demo-script.md          # 演示脚本
│   ├── test-report.md          # 测试报告
│   ├── competition-analysis.md # 竞争力分析
│   ├── score-card.md           # 比赛评分卡
│   ├── judging-criteria.md     # 评审标准分析
│   ├── pitch-deck.md           # 路演 PPT 大纲
│   └── materials-index.md      # 材料总览
├── scripts/                    # 可执行脚本
│   ├── book-meeting-room.js    # 核心预约脚本
│   ├── test-booking-system.js  # 自动化测试套件
│   └── run-demo.sh             # 演示运行脚本
├── templates/                  # 模板文件
│   ├── submission-package/     # 提交包模板
│   └── ppt-slides/             # PPT 模板
└── data/                       # 数据文件
    ├── meeting-rooms.json      # 会议室数据
    └── bookings.json           # 预约记录
```

---

## 🚀 快速开始

### 1. 查看比赛材料

```bash
cd skills/competition-package

# 查看材料索引
cat docs/materials-index.md

# 查看项目申报书
cat docs/project-proposal.md
```

### 2. 运行演示

```bash
# 基础预约演示
node scripts/book-meeting-room.js "给我预约周三下午的五人会议室"

# 运行完整测试套件
node scripts/test-booking-system.js

# 运行演示脚本
bash scripts/run-demo.sh
```

### 3. 打包提交

```bash
# 创建提交包
cd skills/competition-package
bash scripts/create-submission-package.sh

# 输出：submission-package.zip
```

---

## 📊 核心功能

### 预约功能
- ✅ 自然语言解析（中文时间、数字、模糊表达）
- ✅ 智能推荐算法（容量最优化）
- ✅ 冲突检测
- ✅ 预约记录持久化
- ✅ 多场景支持（会议室/报告厅/实验室/自习室）

### 测试功能
- ✅ 15 个自动化测试用例
- ✅ 9 个测试类别覆盖
- ✅ 100% 通过率
- ✅ 测试报告生成

### 比赛材料
- ✅ 项目申报书（完整）
- ✅ 演示脚本（5 场景）
- ✅ 测试报告（详细）
- ✅ 竞争力分析（6 维度）
- ✅ 比赛评分卡（92.75/100）
- ✅ 评审标准分析
- ✅ 路演 PPT 大纲（12 页）

---

## 🎯 比赛得分点

| 维度 | 目标得分 | 支撑材料 |
|------|---------|---------|
| 创新性 | 95/100 | 零 UI 交互，30 倍效率提升 |
| 技术实现 | 90/100 | 15 测试 100% 通过，模块化架构 |
| 完成度 | 95/100 | 核心功能完整，可立即部署 |
| 商业价值 | 90/100 | 3 亿市场，85% 毛利，3 种模式 |
| 用户体验 | 95/100 | 10 秒完成，零学习成本 |
| 社会影响 | 85/100 | 替代 1.5 个全职岗位 |

**综合得分**: 92.75/100

---

## 📋 使用场景

### 场景 1: 比赛提交
```bash
# 1. 检查材料清单
cat docs/submission-checklist.md

# 2. 创建提交包
bash scripts/create-submission-package.sh

# 3. 提交到比赛平台
# (上传 submission-package.zip)
```

### 场景 2: 现场演示
```bash
# 1. 运行演示脚本
bash scripts/run-demo.sh

# 2. 或手动运行演示命令
node scripts/book-meeting-room.js "给我预约周三下午的五人会议室"
node scripts/test-booking-system.js
```

### 场景 3: 答辩准备
```bash
# 1. 查看评审标准
cat docs/judging-criteria.md

# 2. 查看 Q&A 准备
cat docs/pitch-deck.md

# 3. 排练演讲（5 分钟）
# 参考 pitch-deck.md 中的 12 页 PPT 结构
```

---

## 🔧 脚本说明

### book-meeting-room.js
**用途**: 核心预约脚本
**用法**:
```bash
node scripts/book-meeting-room.js "给我预约周三下午的五人会议室"
```

### test-booking-system.js
**用途**: 自动化测试套件
**用法**:
```bash
node scripts/test-booking-system.js
```
**输出**: 15 个测试用例结果 + 测试报告

### run-demo.sh
**用途**: 演示运行脚本
**用法**:
```bash
bash scripts/run-demo.sh
```
**内容**: 依次运行 5 个演示场景

### create-submission-package.sh
**用途**: 创建提交包
**用法**:
```bash
bash scripts/create-submission-package.sh
```
**输出**: `submission-package.zip`

---

## 📄 文档说明

| 文档 | 用途 | 必读 |
|------|------|------|
| materials-index.md | 材料总览 | 🔴 |
| project-proposal.md | 项目申报书 | 🔴 |
| demo-script.md | 演示脚本 | 🔴 |
| test-report.md | 测试报告 | 🟡 |
| score-card.md | 比赛评分卡 | 🟡 |
| judging-criteria.md | 评审标准 | 🟡 |
| pitch-deck.md | 路演 PPT | 🟡 |
| competition-analysis.md | 竞争力分析 | 🟢 |

---

## 🏆 比赛目标

- **保守目标**: 🥈 二等奖（前 5 名）
- **冲刺目标**: 🥇 一等奖（前 2 名）

---

## 📞 团队信息

- **陈俊烨** - 项目负责人 / 全栈开发
- **AI 助手：信电大虾** - NLP / 智能推荐算法

---

## 📅 版本历史

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 初始版本（完整比赛材料） |

---

## ⚠️ 注意事项

1. **填写联系方式** - 在申报书中补充邮箱、电话
2. **赛前排练** - 演示脚本排练 3 次以上
3. **备用录屏** - 准备备用演示视频
4. **时间控制** - 路演严格控制在 5 分钟内

---

*技能包版本：v1.0*
*创建日期：2026-03-28*
*团队：陈俊烨 + AI 助手 信电大虾 🦞⚡️*
