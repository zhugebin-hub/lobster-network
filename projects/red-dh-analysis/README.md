# 📖 红楼梦人物关系分析项目

快速启动指南

## 1. 环境准备

```bash
# 创建项目目录
mkdir -p red-dh-analysis/{data,scripts,output}
cd red-dh-analysis

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install networkx matplotlib jieba pyvis pandas numpy
```

## 2. 准备数据

下载红楼梦文本到 `data/hongloumeng.txt`

推荐来源：
- https://www.gutenberg.org/files/24260/24260-0.txt
- https://ctext.org/honglou-meng

## 3. 运行分析

```bash
# 第一步：提取人物共现关系
python scripts/cooccurrence.py

# 第二步：构建和分析网络
python scripts/build_network.py

# 第三步：生成可视化
python scripts/visualize.py

# 第四步：生成报告
python scripts/analysis.py
```

## 4. 查看结果

- `output/network_simple.png` - 静态网络图
- `output/network_interactive.html` - 交互式网络（浏览器打开）
- `output/analysis_report.md` - 分析报告

## 5. 使用 Gephi（可选）

1. 下载 Gephi: https://gephi.org/
2. 导入 `output/network_for_gephi.csv`
3. 使用 Force Atlas 2 布局
4. 调整节点大小和颜色
5. 导出高清图片

---

祝你分析愉快！🦞
