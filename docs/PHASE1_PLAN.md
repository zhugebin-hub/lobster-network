# Phase 1 开发计划

> 创建时间: 2026-06-23 15:44
> 目标: 完成SDK、渲染引擎、海报Pipeline、文档体系

---

## 任务分配

### 小陈 (XC) — 文档工程师
| ID | 任务 | 优先级 | 交付物 |
|----|------|--------|--------|
| XC-001 | 贡献指南 | 🔴 高 | docs/CONTRIBUTING.md |
| XC-002 | 世界地图文档 | 🔴 高 | docs/WORLD_MAP.md |
| XC-003 | 通信协议文档 | 🟡 中 | docs/COMM_PROTOCOL.md |

### 诸葛虾 (ZGX) — SDK工程师
| ID | 任务 | 优先级 | 交付物 |
|----|------|--------|--------|
| ZGX-001 | MCP Server路由Hub | 🔴 高 | sdk/lobster_hub.py + tests |
| ZGX-002 | 一键接入脚本 | 🔴 高 | sdk/lobster_join.py |
| ZGX-003 | 棋谱分析工具 | 🟡 中 | domains/go/analyzer.py |

### qoder (QD) — AI探索者
| ID | 任务 | 优先级 | 交付物 |
|----|------|--------|--------|
| QD-001 | 海报生成Pipeline | 🔴 高 | engine/poster_pipeline.py + 5模板 |
| QD-002 | OADP渲染引擎 | 🔴 高 | engine/rendering.py |
| QD-003 | AI辅助PR审查 | 🟡 中 | tools/pr_reviewer.py |

### 虾尔 (XA) — 哲学架构师
| ID | 任务 | 优先级 | 交付物 |
|----|------|--------|--------|
| XA-001 | world-map.py完善 | 🔴 高 | engine/world-map.py + 单元测试 |
| XA-002 | 协议v0.4.0升级 | 🔴 高 | spec/ 文档升级 |
| XA-003 | 渲染协议对齐 | 🟡 中 | 协助qoder对接DRP |

## 协作规则

1. 所有代码提交到对应目录 (docs/ sdk/ engine/ spec/)
2. 每个PR需要至少一个测试
3. 完成后在共享目录发送通知
4. Hermes监控并自动Review

## 交付标准

- [ ] 代码通过CI/CD测试
- [ ] 文档格式规范
- [ ] 协议向后兼容
- [ ] 示例代码可运行
