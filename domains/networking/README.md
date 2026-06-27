# 🌐 高级网络通信原理 - 交互式学习模块

> 基于Manus案例集的16章网络课程交互式学习平台

## 课程概述

本模块基于Manus平台生成的16章交互式动画演示，将抽象的网络通信原理转化为可视化的学习体验。涵盖从基础网络演进到SDN、VXLAN、云网一体化的完整知识体系。

## 课程结构

| 阶段 | 章节 | 主题 | 类型 |
|------|------|------|------|
| **基础篇** | 1 | 绪论（网络演进4阶段） | 演进展示 |
| | 2-3 | 交换机原理 + STP算法 | 协议动画 |
| | 4-5 | 路由器原理 + 路由协议 | 协议动画 |
| **进阶篇** | 6-12 | *(待补充)* | - |
| **SDN篇** | 13 | OpenFlow流表实战 | 交互实战 |
| | 14 | VXLAN网络虚拟化 | 交互实战 |
| | 15 | OpenFlow计量表+组表 | 交互实战 |
| **融合篇** | 16 | 云网一体化（OpenStack+ODL） | 配置实战 |

## 技术架构

```
┌─────────────────────────────────────────────┐
│              学习场景层 (Scenarios)           │
│  ┌─────────────┐ ┌─────────────┐ ┌────────┐ │
│  │ 动画演示    │ │ 交互式配置  │ │ 流量模拟│ │
│  │ Animation   │ │ Config      │ │ Traffic │ │
│  └──────┬──────┘ └──────┬──────┘ └───┬────┘ │
└─────────┼───────────────┼─────────────┼──────┘
          │               │             │
┌─────────┼───────────────┼─────────────┼──────┐
│         ▼               ▼             ▼       │
│              题库系统 (Problems)               │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐      │
│  │ 选择题   │ │ 配置题   │ │ 分析题   │      │
│  └──────────┘ └──────────┘ └──────────┘      │
└──────────────────────────────────────────────┘
```

## 快速开始

```bash
# 运行测试
cd docs/lobster-network
python -m pytest domains/networking/tests/ -v

# 生成题库
python domains/networking/problems/problem_generator.py

# 查看学习场景
python domains/networking/scenarios/scene_manager.py
```

## Manus演示链接

| 章 | 演示 | 回放 |
|----|------|------|
| 1 | [netanimat](https://netanimat-etqrydu8.manus.space) | [回放](https://manus.im/share/eOYk8rGG3isVMtkWTzubEb?replay=1) |
| 2-3 | [switchanim](https://switchanim-vpufrziz.manus.space) | [回放](https://manus.im/share/3RvE1nL9y5G0BIt1tEoGww?replay=1) |
| 13 | [openflowweb](https://openflowweb-3a49zyfd.manus.space) | [回放](https://manus.im/share/AKGUSJvLReB7vsdiTmKsu1?replay=1) |
| 14 | [vxlananim](https://vxlananim-f9tuwrva.manus.space) | [回放](https://manus.im/share/cmmsMVoGdsOZcYUz0uIRKI?replay=1) |
| 15 | [openflowdemo](https://openflowdemo-2remyxaz.manus.space) | [回放](https://manus.im/share/w8MsNkXbY2UNRpgAoHYRhw?replay=1) |
| 16 | [cloudnetint](https://cloudnetint-22vpubkm.manus.space) | [回放](https://manus.im/share/MsukIoiDbhkBjEw6ohl8GK?replay=1) |

## 版本

- v1.0.0 (2026-06-25): 初始版本，基于Manus案例集
