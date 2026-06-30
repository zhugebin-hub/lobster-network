#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红楼梦社会网络分析可视化
专业的 SNA 图表生成
"""

import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import json
import numpy as np
from pathlib import Path
from community import community_louvain

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class SNAVisualizer:
    """SNA 可视化类"""
    
    def __init__(self, relationships_file="output/relationships.json", 
                 results_file="output/sna_results.json"):
        """初始化可视化器"""
        self.relationships = self._load_json(relationships_file)
        self.results = self._load_json(results_file) if Path(results_file).exists() else None
        self.G = self._build_graph()
        
    def _load_json(self, file_path):
        """加载 JSON 文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _build_graph(self, min_weight=3):
        """构建网络图"""
        G = nx.Graph()
        
        for key, value in self.relationships.items():
            c1, c2 = key.split('|')
            if value >= min_weight:
                G.add_edge(c1, c2, weight=value)
        
        return G
    
    def plot_network_overview(self, output_file="output/sna_network_overview.png"):
        """
        网络总览图
        """
        print("正在生成网络总览图...")
        
        fig, ax = plt.subplots(figsize=(20, 20))
        
        # 使用 Kamada-Kawai 布局
        pos = nx.kamada_kawai_layout(self.G)
        
        # 计算节点属性
        degrees = dict(self.G.degree())
        node_sizes = [degrees[n] * 300 for n in self.G.nodes()]
        
        # 计算边属性
        edge_weights = [self.G[u][v]['weight'] for u, v in self.G.edges()]
        edge_widths = [w * 0.8 for w in edge_weights]
        
        # 绘制
        nodes = nx.draw_networkx_nodes(
            self.G, pos,
            node_size=node_sizes,
            node_color='lightcoral',
            alpha=0.8,
            edgecolors='darkred',
            linewidths=2,
            ax=ax
        )
        
        edges = nx.draw_networkx_edges(
            self.G, pos,
            width=edge_widths,
            alpha=0.4,
            edge_color='gray',
            ax=ax
        )
        
        labels = nx.draw_networkx_labels(
            self.G, pos,
            font_size=10,
            font_weight='bold',
            font_family='SimHei',
            ax=ax
        )
        
        plt.title("《红楼梦》人物关系网络总览", fontsize=24, fontfamily='SimHei', pad=30)
        plt.axis('off')
        plt.tight_layout()
        
        Path(output_file).parent.mkdir(exist_ok=True)
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 网络总览图：{output_file}")
    
    def plot_centrality_comparison(self, output_file="output/sna_centrality_comparison.png"):
        """
        中心性对比图
        """
        print("正在生成中心性对比图...")
        
        if not self.results:
            print("⚠ 缺少 SNA 结果数据，跳过")
            return
        
        centrality = self.results.get('centrality', {})
        
        # 获取各中心性排名前 15 的人物
        top_n = 15
        
        degree_top = sorted(centrality.get('degree', {}).items(), key=lambda x: x[1], reverse=True)[:top_n]
        betweenness_top = sorted(centrality.get('betweenness', {}).items(), key=lambda x: x[1], reverse=True)[:top_n]
        eigenvector_top = sorted(centrality.get('eigenvector', {}).items(), key=lambda x: x[1], reverse=True)[:top_n]
        
        # 创建图表
        fig, axes = plt.subplots(1, 3, figsize=(18, 8))
        
        # 1. 度中心性
        ax1 = axes[0]
        chars = [c[0] for c in degree_top[::-1]]
        scores = [c[1] for c in degree_top[::-1]]
        bars1 = ax1.barh(chars, scores, color='lightcoral', edgecolor='darkred')
        ax1.set_xlabel('度中心性', fontsize=12)
        ax1.set_title('度中心性 TOP 15\n(人气王)', fontsize=14, fontfamily='SimHei')
        ax1.grid(axis='x', alpha=0.3)
        
        # 2. 中介中心性
        ax2 = axes[1]
        chars = [c[0] for c in betweenness_top[::-1]]
        scores = [c[1] for c in betweenness_top[::-1]]
        bars2 = ax2.barh(chars, scores, color='lightblue', edgecolor='darkblue')
        ax2.set_xlabel('中介中心性', fontsize=12)
        ax2.set_title('中介中心性 TOP 15\n(桥梁人物)', fontsize=14, fontfamily='SimHei')
        ax2.grid(axis='x', alpha=0.3)
        
        # 3. 特征向量中心性
        ax3 = axes[2]
        chars = [c[0] for c in eigenvector_top[::-1]]
        scores = [c[1] for c in eigenvector_top[::-1]]
        bars3 = ax3.barh(chars, scores, color='lightgreen', edgecolor='darkgreen')
        ax3.set_xlabel('特征向量中心性', fontsize=12)
        ax3.set_title('特征向量中心性 TOP 15\n(贵人相助)', fontsize=14, fontfamily='SimHei')
        ax3.grid(axis='x', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 中心性对比图：{output_file}")
    
    def plot_community_structure(self, output_file="output/sna_community_structure.png"):
        """
        社群结构图
        """
        print("正在生成社群结构图...")
        
        # 使用 Louvain 算法检测社群
        try:
            partition = community_louvain.best_partition(self.G, weight='weight', random_state=42)
        except:
            # 如果 python-louvain 不可用，使用贪婪算法
            communities = list(nx.community.greedy_modularity_communities(self.G))
            partition = {}
            for i, comm in enumerate(communities):
                for node in comm:
                    partition[node] = i
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(18, 18))
        
        # 使用弹簧布局
        pos = nx.spring_layout(self.G, k=2, iterations=50, seed=42)
        
        # 为每个社群分配颜色
        n_communities = len(set(partition.values()))
        colors = plt.cm.Set3(np.linspace(0, 1, n_communities))
        
        # 按社群绘制节点
        for comm_id in range(n_communities):
            nodes = [n for n, c in partition.items() if c == comm_id]
            nx.draw_networkx_nodes(
                self.G, pos,
                nodelist=nodes,
                node_size=500,
                node_color=[colors[comm_id]],
                alpha=0.8,
                edgecolors='white',
                linewidths=2,
                ax=ax,
                label=f'社群{comm_id + 1}'
            )
        
        # 绘制边
        nx.draw_networkx_edges(
            self.G, pos,
            width=1,
            alpha=0.3,
            edge_color='gray',
            ax=ax
        )
        
        # 绘制标签
        nx.draw_networkx_labels(
            self.G, pos,
            font_size=8,
            font_family='SimHei',
            ax=ax
        )
        
        plt.title("《红楼梦》人物社群结构分析", fontsize=20, fontfamily='SimHei', pad=20)
        plt.axis('off')
        plt.legend(loc='upper left', fontsize=10)
        plt.tight_layout()
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 社群结构图：{output_file}")
    
    def plot_core_periphery(self, output_file="output/sna_core_periphery.png"):
        """
        核心 - 边缘结构图
        """
        print("正在生成核心 - 边缘结构图...")
        
        if not self.results:
            print("⚠ 缺少 SNA 结果数据，跳过")
            return
        
        cp = self.results.get('core_periphery', {})
        
        core_nodes = set(cp.get('core', {}).get('nodes', []))
        periphery_nodes = set(cp.get('periphery', {}).get('nodes', []))
        middle_nodes = set(cp.get('middle', {}).get('nodes', []))
        
        # 创建图表
        fig, ax = plt.subplots(figsize=(18, 18))
        
        # 使用圆形布局
        pos = nx.circular_layout(self.G)
        
        # 绘制核心人物（红色大节点）
        if core_nodes:
            nx.draw_networkx_nodes(
                self.G, pos,
                nodelist=list(core_nodes),
                node_size=1500,
                node_color='red',
                alpha=0.9,
                edgecolors='darkred',
                linewidths=3,
                ax=ax,
                label='核心人物'
            )
        
        # 绘制中间人物（橙色中节点）
        if middle_nodes:
            nx.draw_networkx_nodes(
                self.G, pos,
                nodelist=list(middle_nodes),
                node_size=800,
                node_color='orange',
                alpha=0.8,
                edgecolors='darkorange',
                linewidths=2,
                ax=ax,
                label='中间人物'
            )
        
        # 绘制边缘人物（蓝色小节点）
        if periphery_nodes:
            nx.draw_networkx_nodes(
                self.G, pos,
                nodelist=list(periphery_nodes),
                node_size=400,
                node_color='lightblue',
                alpha=0.7,
                edgecolors='darkblue',
                linewidths=1,
                ax=ax,
                label='边缘人物'
            )
        
        # 绘制边
        nx.draw_networkx_edges(
            self.G, pos,
            width=1,
            alpha=0.3,
            edge_color='gray',
            ax=ax
        )
        
        # 绘制标签
        nx.draw_networkx_labels(
            self.G, pos,
            font_size=8,
            font_family='SimHei',
            ax=ax
        )
        
        plt.title("《红楼梦》人物核心 - 边缘结构", fontsize=20, fontfamily='SimHei', pad=20)
        plt.axis('off')
        plt.legend(loc='upper left', fontsize=12)
        plt.tight_layout()
        
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 核心 - 边缘结构图：{output_file}")
    
    def plot_degree_distribution(self, output_file="output/sna_degree_distribution.png"):
        """
        度分布图
        """
        print("正在生成度分布图...")
        
        degrees = [d for n, d in self.G.degree()]
        
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # 1. 度分布直方图
        ax1 = axes[0]
        ax1.hist(degrees, bins=20, color='lightcoral', edgecolor='darkred', alpha=0.7)
        ax1.set_xlabel('度数', fontsize=12)
        ax1.set_ylabel('人物数量', fontsize=12)
        ax1.set_title('人物度分布直方图', fontsize=14, fontfamily='SimHei')
        ax1.grid(axis='y', alpha=0.3)
        
        # 2. 度分布累积图
        ax2 = axes[1]
        sorted_degrees = sorted(degrees, reverse=True)
        ax2.plot(range(len(sorted_degrees)), sorted_degrees, 'o-', color='darkblue')
        ax2.set_xlabel('人物排名', fontsize=12)
        ax2.set_ylabel('度数', fontsize=12)
        ax2.set_title('人物度分布累积图', fontsize=14, fontfamily='SimHei')
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✓ 度分布图：{output_file}")
    
    def generate_all_plots(self):
        """生成所有图表"""
        print("\n" + "="*60)
        print("📊 生成 SNA 可视化图表")
        print("="*60 + "\n")
        
        self.plot_network_overview()
        self.plot_centrality_comparison()
        self.plot_community_structure()
        self.plot_core_periphery()
        self.plot_degree_distribution()
        
        print("\n" + "="*60)
        print("✅ 所有图表生成完成！")
        print("="*60)
        print("\n输出文件:")
        print("  📷 output/sna_network_overview.png - 网络总览")
        print("  📊 output/sna_centrality_comparison.png - 中心性对比")
        print("  👥 output/sna_community_structure.png - 社群结构")
        print("  🎯 output/sna_core_periphery.png - 核心 - 边缘")
        print("  📈 output/sna_degree_distribution.png - 度分布")


def main():
    """主函数"""
    # 检查数据文件
    relationships_file = "output/relationships.json"
    if not Path(relationships_file).exists():
        print(f"✗ 未找到关系数据文件：{relationships_file}")
        print("  请先运行：python scripts/cooccurrence.py")
        return
    
    # 创建可视化器
    print("🔍 初始化可视化器...")
    viz = SNAVisualizer(relationships_file)
    print(f"✓ 网络加载完成：{viz.G.number_of_nodes()} 个节点")
    
    # 生成所有图表
    viz.generate_all_plots()


if __name__ == "__main__":
    main()
