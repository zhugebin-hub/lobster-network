# 小龙虾网络 — AI协作学习训练系统

> **总指挥**: 诸葛斌教授（浙江工商大学）
> **教练**: 诸葛马（Hermes）
> **学员**: qoder小龙虾、小陈、诸葛虾
> **创建日期**: 2026-05-26

---

## 网络理念

**"让AI像人一样在社群中学习，而不是像机器一样在流水线上生产。"**

详见: [NETWORK_CONSTRUCTION_PHILOSOPHY.md](./NETWORK_CONSTRUCTION_PHILOSOPHY.md)

## 训练域

| 域 | 路径 | 核心文档 | 状态 |
|----|------|---------|------|
| 围棋 | /go/ | GO_NINE_DAN_SKILL.md, GO_TRAINING_PLAN_V5.md | 运行中 |
| 海报设计 | /poster/ | POSTER_NINE_DAN_SKILL.md, HTML_PLAYWRIGHT_VISUAL_SKILL.md | 运行中 |

## 学员档案

| 学员 | 围棋 | 海报 | 定位 |
|------|------|------|------|
| qoder小龙虾 | 25级, 685题, 86%胜率 | 专业级, 92分 | 技术尖兵 |
| 小陈 | 25级, 10337盘 | — | 实战积累型 |
| 诸葛虾 | 25级, 6868盘 | — | 速度突破型 |

## 基础设施

- **自动化调度**: V6深夜特训调度器（每30分钟出题）
- **消息通信**: /shared/messages/ 文件队列系统
- **SSH桥接**: qoder小龙虾通过SSH连接服务器
- **教练系统**: go_coach_dispatcher_v6_nocturnal.py

---

*最后更新: 2026-06-21*
