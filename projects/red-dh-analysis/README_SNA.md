# 📊 《红楼梦》社会网络分析 (SNA)

**专业的社会网络分析框架 - 量化解读经典文学**

---

## 🎯 分析内容

### 1. 中心性分析 (Centrality Analysis)
| 指标 | 意义 | 识别 |
|------|------|------|
| 度中心性 | 连接数量 | 人气王 |
| 中介中心性 | 控制信息流 | 桥梁人物 |
| 接近中心性 | 信息传播速度 | 信息中心 |
| 特征向量中心性 | 与重要人物相连 | 贵人相助 |
| PageRank | 综合影响力 | 核心人物 |

### 2. 社群检测 (Community Detection)
- **Louvain 算法**: 基于模块度优化
- **Girvan-Newman**: 基于边介数分裂
- **标签传播**: 快速社群划分
- **贪婪模块度**: 高效社群发现

### 3. 角色分析 (Role Analysis)
- **核心 - 边缘结构**: 识别人物层级
- **结构洞分析**: 发现信息经纪人
- **桥梁人物**: 连接不同群体

### 4. 网络特性 (Network Properties)
- **小世界特性**: 六度分隔验证
- **聚类系数**: 群体凝聚程度
- **平均路径长度**: 信息传播效率

---

## 🚀 快速开始

### 完整分析流程

```bash
# 1. 进入项目目录
cd /home/admin/.openclaw/workspace/projects/red-dh-analysis

# 2. 激活虚拟环境
source venv/bin/activate

# 3. 安装依赖
pip install -r requirements.txt

# 4. 准备数据（如未准备）
mkdir -p data
curl -o data/hongloumeng.txt "https://www.gutenberg.org/files/24260/24260-0.txt"

# 5. 提取人物关系
python scripts/cooccurrence.py

# 6. 社会网络分析
python scripts/sna_analysis.py

# 7. 生成可视化
python scripts/sna_visualization.py

# 8. (可选) 简单网络图
python scripts/visualize.py
```

---

## 📁 项目结构

```
red-dh-analysis/
├── data/
│   └── hongloumeng.txt          # 红楼梦原文
├── scripts/
│   ├── cooccurrence.py          # 共现分析
│   ├── sna_analysis.py          # SNA 分析 ⭐
│   ├── sna_visualization.py     # SNA 可视化 ⭐
│   └── visualize.py             # 简单可视化
├── output/
│   ├── relationships.json       # 关系数据
│   ├── sna_full_report.md       # SNA 完整报告 ⭐
│   ├── sna_results.json         # SNA 原始数据
│   ├── sna_network_overview.png # 网络总览图
│   ├── sna_centrality_comparison.png  # 中心性对比
│   ├── sna_community_structure.png    # 社群结构
│   ├── sna_core_periphery.png         # 核心 - 边缘
│   └── sna_degree_distribution.png    # 度分布
├── README.md
└── requirements.txt
```

---

## 📊 输出说明

### 文本报告
| 文件 | 内容 |
|------|------|
| `sna_full_report.md` | 完整 SNA 分析报告（Markdown） |
| `sna_results.json` | 所有分析指标原始数据（JSON） |

### 可视化图表
| 文件 | 说明 |
|------|------|
| `sna_network_overview.png` | 网络总览图 |
| `sna_centrality_comparison.png` | 三种中心性对比 |
| `sna_community_structure.png` | 社群结构图 |
| `sna_core_periphery.png` | 核心 - 边缘结构 |
| `sna_degree_distribution.png` | 度分布图 |

---

## 🔬 分析方法详解

### 中心性分析

**度中心性 (Degree Centrality)**
```
衡量人物直接连接的数量
公式：CD(v) = deg(v) / (n-1)
解读：数值越高，人物越"受欢迎"
```

**中介中心性 (Betweenness Centrality)**
```
衡量人物作为"桥梁"的程度
公式：CB(v) = Σ(σst(v) / σst)
解读：数值越高，人物越能控制信息流
```

**特征向量中心性 (Eigenvector Centrality)**
```
衡量人物与重要人物的连接程度
公式：Ax = λx
解读：数值越高，人物的"朋友圈"越有权势
```

### 社群检测

**模块度 (Modularity)**
```
衡量社群划分质量
公式：Q = (1/2m) Σ[Aij - ki*kj/2m]δ(ci,cj)
解读：Q > 0.3 表示明显的社群结构
```

### 结构洞

**约束系数 (Constraint)**
```
衡量人物缺乏结构洞的程度
公式：Cij = (pij + Σ pik*pkj)²
解读：约束越低，结构洞越丰富
```

---

## 📖 预期发现

### 核心人物
根据以往研究，预期发现：
1. **贾宝玉** - 最高度中心性（连接最多）
2. **王熙凤** - 高中介中心性（信息枢纽）
3. **林黛玉/薛宝钗** - 高特征向量中心性（与核心人物相连）

### 社群结构
预期发现以下社群：
1. **贾府核心圈** - 贾母、王夫人、邢夫人等
2. **宝玉圈** - 黛玉、宝钗、袭人、晴雯等
3. **管家圈** - 王熙凤、平儿、贾琏等
4. **丫鬟圈** - 各房大丫鬟
5. **外来人物** - 刘姥姥、妙玉等

### 桥梁人物
预期发现：
- **平儿** - 连接王熙凤与其他人物
- **鸳鸯** - 连接贾母与各房
- **袭人** - 连接宝玉与各房

---

## 🎓 学术应用

### 论文写作
本分析框架可用于：
- 古典文学量化研究
- 人物关系对比研究
- 叙事结构分析
- 数字人文方法论

### 可引用指标
```bibtex
@analysis{hongloumeng-sna-2026,
  title = {红楼梦社会网络分析},
  method = {SNA + 共现分析},
  metrics = [度中心性，中介中心性，社群检测，结构洞],
  year = {2026}
}
```

---

## 🔧 故障排除

### 常见问题

**1. 中文字体显示问题**
```bash
# Ubuntu/Debian
sudo apt-get install fonts-wqy-microhei fonts-wqy-zenhei

# macOS
brew install --cask font-simhei
```

**2. python-louvain 安装失败**
```bash
# 使用替代方案
pip install community
# 或跳过社群检测，使用贪婪算法
```

**3. 内存不足**
```bash
# 减少分析人物数量
# 或增加共现阈值（在 cooccurrence.py 中修改 min_weight）
```

---

## 📚 参考文献

1. Newman, M. E. J. (2010). Networks: An Introduction. Oxford University Press.
2. 刘军 (2014). 社会网络分析导论. 社会科学文献出版社.
3. Moretti, F. (2013). Distant Reading. Verso Books.
4. 王军 (2020). 数字人文与古典文学研究. 北京大学出版社.

---

## 🤖 需要帮助？

作为你的**数字人文学习助手**，我可以帮你：

- 📝 **解释分析结果** - 任何指标不理解都可以问我
- 🎯 **调整分析参数** - 修改阈值、人物名单等
- 📖 **深入解读** - 从文学角度解释 SNA 发现
- 📊 **扩展分析** - 添加情感分析、时间演化等
- ✍️ **论文写作** - 帮助撰写分析报告

随时提问！🦞

---

*最后更新：2026-03-27*
