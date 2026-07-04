#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红楼梦人物关系网络可视化
"""

import networkx as nx
import matplotlib.pyplot as plt
import json
from pathlib import Path

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


def load_analysis_data(file_path):
    """加载分析数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_relationships(file_path):
    """加载关系数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    relationships = {}
    for key, value in data.items():
        c1, c2 = key.split('|')
        relationships[(c1, c2)] = value
    
    return relationships


def build_graph(relationships, min_weight=3):
    """构建网络图"""
    G = nx.Graph()
    
    for (char1, char2), weight in relationships.items():
        if weight >= min_weight:
            G.add_edge(char1, char2, weight=weight)
    
    return G


def visualize_simple(G, output_file="output/network_simple.png"):
    """
    简单静态可视化
    """
    print("正在生成静态网络图...")
    
    fig, ax = plt.subplots(figsize=(16, 16))
    
    # 使用弹簧布局
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    # 计算节点大小（基于度）
    node_sizes = [G.degree(n) * 200 for n in G.nodes()]
    
    # 计算边的宽度（基于权重）
    edge_weights = [G[u][v]['weight'] * 0.5 for u, v in G.edges()]
    
    # 绘制网络
    nx.draw_networkx_nodes(
        G, pos, 
        node_size=node_sizes, 
        node_color='lightcoral', 
        alpha=0.8,
        edgecolors='darkred',
        linewidths=2
    )
    
    nx.draw_networkx_edges(
        G, pos, 
        width=edge_weights, 
        alpha=0.5,
        edge_color='gray'
    )
    
    nx.draw_networkx_labels(
        G, pos, 
        font_size=9, 
        font_family='SimHei',
        font_weight='bold'
    )
    
    plt.title("《红楼梦》人物关系网络图", fontsize=20, fontfamily='SimHei', pad=20)
    plt.axis('off')
    plt.tight_layout()
    
    # 保存
    Path(output_file).parent.mkdir(exist_ok=True)
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    print(f"✓ 静态图已保存：{output_file}")
    
    plt.close()


def visualize_interactive(G, output_file="output/network_interactive.html"):
    """
    交互式可视化（使用 pyvis）
    """
    try:
        from pyvis.network import Network
        print("正在生成交互式网络图...")
        
        net = Network(
            height="800px", 
            width="100%", 
            bgcolor="#222222",
            font_color="white",
            notebook=False
        )
        
        # 添加节点
        for node in G.nodes():
            degree = G.degree(node)
            net.add_node(
                node, 
                label=node, 
                size=degree * 8,
                title=f"{node} - 连接数：{degree}"
            )
        
        # 添加边
        for u, v, data in G.edges(data=True):
            net.add_edge(u, v, value=data.get('weight', 1))
        
        # 设置物理布局
        net.set_options("""
        {
            "physics": {
                "forceAtlas2Based": {
                    "gravitationalConstant": -80,
                    "centralGravity": 0.02,
                    "springLength": 150,
                    "springConstant": 0.08
                },
                "maxVelocity": 50,
                "solver": "forceAtlas2Based",
                "timestep": 0.35
            },
            "interaction": {
                "hover": true,
                "tooltipDelay": 200
            }
        }
        """)
        
        # 保存
        Path(output_file).parent.mkdir(exist_ok=True)
        net.show(output_file)
        print(f"✓ 交互图已保存：{output_file}")
        print(f"  用浏览器打开查看：{output_file}")
        
    except ImportError:
        print("⚠ pyvis 未安装，跳过高交互可视化")
        print("  安装：pip install pyvis")


def generate_report(analysis, output_file="output/analysis_report.md"):
    """
    生成分析报告
    """
    print("正在生成分析报告...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 📖 《红楼梦》人物关系网络分析报告\n\n")
        f.write(f"*自动生成报告*\n\n")
        
        f.write("## 一、网络基本统计\n\n")
        basic = analysis['basic']
        f.write(f"| 指标 | 数值 |\n")
        f.write(f"|------|------|\n")
        f.write(f"| 人物数量 | {basic.get('nodes', 'N/A')} |\n")
        f.write(f"| 关系数量 | {basic.get('edges', 'N/A')} |\n")
        f.write(f"| 网络密度 | {basic.get('density', 0):.4f} |\n")
        f.write(f"| 平均度数 | {basic.get('avg_degree', 0):.2f} |\n")
        if 'avg_path_length' in basic:
            f.write(f"| 平均路径长度 | {basic['avg_path_length']:.2f} |\n")
        if 'clustering' in basic:
            f.write(f"| 聚类系数 | {basic['clustering']:.4f} |\n")
        f.write("\n")
        
        f.write("## 二、核心人物分析\n\n")
        f.write("### 按度中心性排名（连接最多的人物）\n\n")
        f.write("| 排名 | 人物 | 度中心性 |\n")
        f.write("|------|------|----------|\n")
        for i, (char, score) in enumerate(analysis['top_degree'][:15], 1):
            f.write(f"| {i} | {char} | {score:.4f} |\n")
        f.write("\n")
        
        f.write("### 按中介中心性排名（桥梁人物）\n\n")
        f.write("| 排名 | 人物 | 中介中心性 |\n")
        f.write("|------|------|------------|\n")
        for i, (char, score) in enumerate(analysis['top_betweenness'][:15], 1):
            f.write(f"| {i} | {char} | {score:.4f} |\n")
        f.write("\n")
        
        f.write("## 三、社群分析\n\n")
        communities = analysis['communities']
        f.write(f"- **社群数量**: {len(communities)}\n\n")
        
        for i, comm in enumerate(communities, 1):
            f.write(f"### 社群 {i}\n\n")
            f.write(f"**成员**: {', '.join(comm)}\n\n")
            f.write(f"**人数**: {len(comm)}\n\n")
        
        f.write("---\n\n")
        f.write("*报告生成完成*\n")
    
    print(f"✓ 报告已保存：{output_file}")


def main():
    """主函数"""
    print("📊 红楼梦人物关系可视化开始...\n")
    
    # 检查数据文件
    relationships_file = "output/relationships.json"
    analysis_file = "output/analysis.json"
    
    if not Path(relationships_file).exists():
        print(f"✗ 未找到关系数据文件：{relationships_file}")
        print("  请先运行：python scripts/cooccurrence.py")
        return
    
    # 加载数据
    print("正在加载数据...")
    relationships = load_relationships(relationships_file)
    
    if Path(analysis_file).exists():
        analysis = load_analysis_data(analysis_file)
    else:
        analysis = None
    
    # 构建网络
    print("正在构建网络...")
    G = build_graph(relationships, min_weight=3)
    print(f"✓ 网络：{G.number_of_nodes()} 个节点，{G.number_of_edges()} 条边\n")
    
    # 生成可视化
    visualize_simple(G, "output/network_simple.png")
    visualize_interactive(G, "output/network_interactive.html")
    
    # 生成报告
    if analysis:
        generate_report(analysis, "output/analysis_report.md")
    
    print("\n" + "="*50)
    print("✓ 可视化完成！")
    print("="*50)
    print("\n输出文件:")
    print("  📷 output/network_simple.png - 静态网络图")
    print("  🌐 output/network_interactive.html - 交互式网络（浏览器打开）")
    print("  📄 output/analysis_report.md - 分析报告")
    print("\n可选：使用 Gephi 进行更专业的可视化")
    print("  1. 下载 Gephi: https://gephi.org/")
    print("  2. 导入 output/edges_for_gephi.csv")
    print("  3. 使用 Force Atlas 2 布局美化")


if __name__ == "__main__":
    main()
