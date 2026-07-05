# 🎨 小龙虾海报设计培训系统 V1.0

> **版本**: V1.0  
> **部署时间**: 2026-06-18  
> **教练**: 诸葛马 (Hermes)  
> **学员**: qoder小龙虾（主攻）、小陈（辅助）、诸葛虾（辅助）  
> **目标**: 通过系统化学习，使qoder小龙虾能独立生成专业级宣传海报

---

## 📊 现状分析

### 三版海报对比评测

| 维度 | 版1（Qoder自制） | 版2（Manus·高能直播） | 版3（Manus·清华出版社） |
|------|:-:|:-:|:-:|
| 视觉冲击力 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 信息层次 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 品牌一致性 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 图形创意 | ⭐⭐（纯emoji） | ⭐⭐⭐⭐⭐（电路板龙虾） | ⭐⭐⭐⭐⭐（3D书封+龙虾） |
| 排版美感 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 色彩运用 | ⭐⭐⭐（深蓝单色调） | ⭐⭐⭐⭐⭐（蓝+橙对比色） | ⭐⭐⭐⭐（紫+青+橙） |
| 二维码整合 | ⭐⭐⭐⭐（嵌入设计） | ⭐⭐（无） | ⭐⭐⭐⭐（底部独立区域） |
| 专业度总分 | 65/100 | 92/100 | 95/100 |

### Qoder当前核心短板

1. **图形素材匮乏** — 只会用emoji(🎯📊📝)，无法生成矢量图形、3D渲染、光效
2. **色彩理论薄弱** — 单色调为主，不会用对比色/互补色增强视觉冲击
3. **排版规则欠缺** — 缺乏网格系统、黄金比例、视觉动线设计知识
4. **品牌设计缺失** — 没有IP形象设计能力（对比Manus的电路板龙虾）
5. **工具链限制** — 只能用HTML+CSS+Chrome截图，缺乏专业设计工具链

---

## 📅 培训计划（7天速成 + 持续迭代）

### 网络架构复用方案

```
现有围棋网络:
  Hermes教练(go_coach_dispatcher_v4.py)
    ├── 小陈(xiaochen) — 围棋学员
    ├── 诸葛虾(zhuguxia) — 围棋学员  
    └── qoder(qoder) — 围棋学员

新增海报培训通道:
  Hermes教练(poster_coach_dispatcher_v1.py)
    ├── 小陈 — 配色与排版评审
    ├── 诸葛虾 — 图形创意评审
    └── qoder — 海报制作主力（被培训对象）
```

### 通信协议（复用现有SSH桥接）

```
/shared/training/poster/              # 海报培训目录
├── POSTER_TRAINING_PLAN_V1.md        # 本文件
├── problem_bank/                     # 设计题库
│   ├── color_theory.json             # 色彩理论 (15题)
│   ├── layout_design.json            # 排版设计 (15题)
│   ├── typography.json               # 字体设计 (10题)
│   ├── brand_design.json             # 品牌设计 (10题)
│   └── practical_cases.json          # 实战案例 (20题)
├── reference/                        # 参考素材库
│   ├── manus_poster_v2.png           # Manus版2（参考标杆）
│   ├── manus_poster_v3.png           # Manus版3（参考标杆）
│   └── design_principles.md          # 设计原则速查
├── qoder/                            # qoder学习档案
│   ├── profile.json                  # 学员档案
│   ├── submissions/                  # 作品提交
│   └── feedback/                     # 教练反馈
└── evaluation/                       # 评测记录
    └── scoring_rubric.json           # 评分标准

/shared/messages/queue/poster-qoder/  # 海报训练消息队列
├── inbox/                            # 接收任务
├── outbox/                           # 提交作品
└── processed/                        # 已处理
```

### 7天课程安排

| 天 | 主题 | 内容 | 作业 | 评审 |
|----|------|------|------|------|
| Day 1 | 色彩理论 | 对比色/互补色/三色组/60-30-10法则 | 为Manus海报重新配色3版 | 诸葛虾评审 |
| Day 2 | 排版基础 | 网格系统/视觉层次/F型阅读/Z型阅读 | 重构版1海报排版 | 小陈评审 |
| Day 3 | 字体设计 | 标题字/正文字/中英混排/字距行距 | 制作5组标题字体方案 | 教练评审 |
| Day 4 | 视觉元素 | 图标设计/3D效果/光效/渐变/蒙版 | 设计小龙虾IP形象3版 | 诸葛虾评审 |
| Day 5 | 品牌设计 | VI系统/品牌色/品牌字体/品牌图形 | 制作"小龙虾"品牌手册 | 教练评审 |
| Day 6 | 海报实战 | 信息架构/CTA设计/二维码整合/多尺寸适配 | 重做Manus版3同等质量海报 | 全员评审 |
| Day 7 | 综合考核 | 独立完成完整海报设计 | 为下一场直播设计全套海报(3版) | 教练+用户评审 |

### 每日训练流程

```
07:30  Hermes教练派发当日设计任务 → poster-qoder/inbox/
08:00  qoder收到任务，开始学习理论知识
09:00  qoder研究reference/中的Manus标杆作品
10:00  qoder完成设计方案(HTML/CSS/SVG)
12:00  qoder提交作品 → poster-qoder/outbox/
14:00  教练/同伴评审，给出评分和反馈
16:00  qoder根据反馈修改作品
18:00  提交最终版本
20:00  教练确认，归档到 evaluation/
```

---

## 🛠 技术提升路线

### Phase 1: 工具链升级（Day 1-2）

**当前**: HTML + CSS + Chrome headless截图

**升级目标**:
- SVG内嵌图形（替代emoji，实现矢量图标和光效）
- CSS渐变+滤镜+混合模式（实现Manus风格的霓虹光效）
- CSS 3D transform（实现3D书封效果）
- Canvas API（更精细的图形控制）
- 多图层合成（背景层+内容层+光效层+前景层）

### Phase 2: 设计知识体系（Day 3-5）

**色彩模块**:
- 60-30-10法则（主色60%+辅色30%+强调色10%）
- 对比色搭配（蓝+橙，紫+黄，如Manus版2）
- 深色模式配色（深紫/深蓝底 + 霓虹高光，如Manus版3）
- 色彩心理学（蓝色=信任/科技，橙色=活力/创新）

**排版模块**:
- 网格系统（12列栅格，信息分区）
- 视觉动线（Z型：标题→图片→CTA）
- 留白比例（内容占60%，留白40%）
- 信息层次（大中小三级字号比例 3:2:1）

**图形模块**:
- SVG滤镜实现光晕/发光效果
- CSS clip-path实现异形容器
- 径向渐变+线性渐变组合
- 阴影层叠（多层box-shadow制造深度感）

### Phase 3: 实战迭代（Day 6-7+）

**对标分析法**:
1. 拆解Manus标杆海报的DOM结构和CSS实现
2. 逐元素复现（书封、龙虾、光效、排版）
3. 教练评分 ≥ 85分视为达标

**持续改进循环**:
```
设计 → 提交 → 评审(1-100分) → 反馈 → 修改 → 复评
目标: 每次迭代提升5-10分，7天后稳定在85+
```

---

## 📈 评分标准 (Scoring Rubric)

| 维度 | 权重 | 60分(及格) | 80分(良好) | 95分(优秀) |
|------|------|-----------|-----------|-----------|
| 色彩运用 | 20% | 单色调，对比不足 | 双色搭配，有对比 | 三色组合，和谐且有冲击力 |
| 排版设计 | 20% | 信息堆砌，无层次 | 有基本层次和留白 | 网格系统，视觉动线清晰 |
| 图形创意 | 25% | emoji或简单色块 | SVG矢量图形 | 3D效果+光效+IP形象 |
| 信息传达 | 15% | 信息完整但拥挤 | 重点突出，阅读流畅 | 一眼抓住注意力 |
| 品牌一致 | 10% | 无品牌感 | 有基本品牌元素 | 完整VI体系 |
| 技术实现 | 10% | 基础HTML/CSS | 渐变+滤镜+动画 | Canvas/SVG高级技术 |

---

## 🚀 立即行动计划

### Step 1: 部署海报培训通道到服务器
```bash
# 在服务器上创建目录结构
mkdir -p /shared/training/poster/{problem_bank,reference,qoder/{submissions,feedback},evaluation}
mkdir -p /shared/messages/queue/poster-qoder/{inbox,outbox,processed}
```

### Step 2: 上传Manus标杆作品作为参考
```bash
# 将三版海报上传到reference/目录供学习
scp manus_poster_v2.png server:/shared/training/poster/reference/
scp manus_poster_v3.png server:/shared/training/poster/reference/
```

### Step 3: 创建海报教练调度器
```bash
# poster_coach_dispatcher_v1.py — 复用go_coach_dispatcher框架
# 每日7:30派发设计任务到poster-qoder/inbox/
```

### Step 4: qoder开始Day 1自学
- 研究Manus版2/版3的配色方案（提取主色、辅色、强调色的HEX值）
- 用CSS复现霓虹光效和渐变背景
- 提交3版配色方案到outbox

---

**制定**: qoder小龙虾 + 诸葛马（教练）  
**审核**: 诸葛斌  
**部署**: 2026-06-18  
**目标**: 7天后能独立生成90+分的专业海报
