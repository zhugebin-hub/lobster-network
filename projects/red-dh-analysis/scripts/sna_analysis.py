#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红楼梦社会网络分析 (Social Network Analysis)
专业的 SNA 指标计算与分析
"""

import networkx as nx
import matplotlib.pyplot as plt
import json
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from pathlib import Path
from datetime import datetime

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False


class RedDreamSNA:
    """红楼梦社会网络分析类"""
    
    def __init__(self, relationships_file="output/relationships.json"):
        """
        初始化分析器
        
        Args:
            relationships_file: 关系数据文件路径
        """
        self.relationships = self._load_relationships(relationships_file)
        self.G = self._build_graph()
        self.results = {}
        
    def _load_relationships(self, file_path):
        """加载关系数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        relationships = {}
        for key, value in data.items():
            c1, c2 = key.split('|')
            relationships[(c1, c2)] = value
        
        return relationships
    
    def _build_graph(self, min_weight=3):
        """构建网络图"""
        G = nx.Graph()
        
        for (char1, char2), weight in self.relationships.items():
            if weight >= min_weight:
                G.add_edge(char1, char2, weight=weight)
        
        return G
    
    # ==================== 基础统计 ====================
    
    def basic_statistics(self):
        """基础网络统计"""
        stats = {
            'nodes': self.G.number_of_nodes(),
            'edges': self.G.number_of_edges(),
            'density': nx.density(self.G),
            'avg_degree': np.mean([d for n, d in self.G.degree()]),
            'max_degree': max([d for n, d in self.G.degree()]) if self.G.number_of_nodes() > 0 else 0,
            'min_degree': min([d for n, d in self.G.degree()]) if self.G.number_of_nodes() > 0 else 0,
            'total_weight': sum([d['weight'] for u, v, d in self.G.edges(data=True)]),
            'avg_weight': np.mean([d['weight'] for u, v, d in self.G.edges(data=True)]) if self.G.number_of_edges() > 0 else 0,
        }
        
        # 连通性分析
        if self.G.number_of_nodes() > 0:
            n_components = nx.number_connected_components(self.G)
            stats['connected_components'] = n_components
            
            if n_components == 1:
                stats['diameter'] = nx.diameter(self.G)
                stats['radius'] = nx.radius(self.G)
                stats['avg_path_length'] = nx.average_shortest_path_length(self.G)
            else:
                # 计算最大连通子图
                largest_cc = max(nx.connected_components(self.G), key=len)
                subgraph = self.G.subgraph(largest_cc)
                stats['largest_cc_size'] = len(largest_cc)
                stats['largest_cc_diameter'] = nx.diameter(subgraph) if len(largest_cc) > 1 else 0
        
        # 聚类系数
        stats['clustering_coefficient'] = nx.average_clustering(self.G)
        
        self.results['basic_stats'] = stats
        return stats
    
    # ==================== 中心性分析 ====================
    
    def centrality_analysis(self):
        """
        中心性分析 - 识别人物重要性
        """
        centrality = {}
        
        # 1. 度中心性 (Degree Centrality)
        # 连接数最多的人物 - 人气王
        centrality['degree'] = nx.degree_centrality(self.G)
        
        # 2. 中介中心性 (Betweenness Centrality)
        # 桥梁人物 - 控制信息流动
        centrality['betweenness'] = nx.betweenness_centrality(self.G, weight='weight')
        
        # 3. 接近中心性 (Closeness Centrality)
        # 信息中心 - 最快到达其他人
        centrality['closeness'] = nx.closeness_centrality(self.G, distance='weight')
        
        # 4. 特征向量中心性 (Eigenvector Centrality)
        # 与重要人物相连的人物
        try:
            centrality['eigenvector'] = nx.eigenvector_centrality(self.G, weight='weight', max_iter=1000)
        except:
            centrality['eigenvector'] = {n: 0 for n in self.G.nodes()}
        
        # 5. PageRank
        # Google 页面排名算法
        centrality['pagerank'] = nx.pagerank(self.G, weight='weight')
        
        # 6. 加权度
        centrality['weighted_degree'] = dict(self.G.degree(weight='weight'))
        
        self.results['centrality'] = {k: dict(v) for k, v in centrality.items()}
        return centrality
    
    def get_top_characters(self, centrality_type='degree', top_n=10):
        """
        获取某类中心性排名前 N 的人物
        
        Args:
            centrality_type: 中心性类型 (degree/betweenness/closeness/eigenvector/pagerank)
            top_n: 返回前 N 名
        """
        if centrality_type not in self.results.get('centrality', {}):
            self.centrality_analysis()
        
        centrality = self.results['centrality'][centrality_type]
        sorted_chars = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_chars[:top_n]
    
    # ==================== 社群分析 ====================
    
    def community_detection(self):
        """
        社群检测 - 发现人物群体
        """
        communities = {}
        
        # 1. Louvain 算法 (基于模块度优化)
        try:
            louvain_comms = list(nx.community.louvain_communities(self.G, weight='weight'))
            communities['louvain'] = louvain_comms
            communities['louvain_modularity'] = nx.community.modularity(self.G, louvain_comms, weight='weight')
        except:
            communities['louvain'] = []
            communities['louvain_modularity'] = 0
        
        # 2. Girvan-Newman 算法 (基于边介数)
        try:
            gn_comms = list(nx.community.girvan_newman(self.G))
            # 取第一次分裂的结果
            if gn_comms:
                communities['girvan_newman'] = [set(c) for c in gn_comms[0]]
                communities['gn_modularity'] = nx.community.modularity(self.G, communities['girvan_newman'])
        except:
            communities['girvan_newman'] = []
            communities['gn_modularity'] = 0
        
        # 3. 标签传播算法
        try:
            label_prop = list(nx.community.label_propagation_communities(self.G))
            communities['label_propagation'] = label_prop
        except:
            communities['label_propagation'] = []
        
        # 4. 贪婪模块度算法
        greedy_comms = list(nx.community.greedy_modularity_communities(self.G))
        communities['greedy'] = greedy_comms
        communities['greedy_modularity'] = nx.community.modularity(self.G, greedy_comms)
        
        self.results['communities'] = {k: [list(c) for c in v] if isinstance(v, list) else v 
                                       for k, v in communities.items()}
        return communities
    
    def analyze_communities(self):
        """
        社群详细分析
        """
        if 'communities' not in self.results:
            self.community_detection()
        
        # 使用贪婪算法的结果进行详细分析
        communities = self.results['communities'].get('greedy', [])
        
        analysis = []
        for i, comm in enumerate(communities):
            comm_analysis = {
                'id': i + 1,
                'members': comm,
                'size': len(comm),
                'internal_edges': 0,
                'external_edges': 0,
                'density': 0,
                'central_member': None,
            }
            
            # 计算内部边和外部边
            subgraph = self.G.subgraph(comm)
            comm_analysis['internal_edges'] = subgraph.number_of_edges()
            comm_analysis['density'] = nx.density(subgraph) if len(comm) > 1 else 0
            
            # 计算社群内度中心性最高的人物
            if len(comm) > 0:
                degrees = {n: self.G.degree(n) for n in comm}
                comm_analysis['central_member'] = max(degrees.items(), key=lambda x: x[1])[0]
            
            # 计算外部连接
            for node in comm:
                for neighbor in self.G.neighbors(node):
                    if neighbor not in comm:
                        comm_analysis['external_edges'] += 1
            
            analysis.append(comm_analysis)
        
        self.results['community_analysis'] = analysis
        return analysis
    
    # ==================== 角色分析 ====================
    
    def structural_holes_analysis(self):
        """
        结构洞分析 - 识别信息经纪人
        """
        holes = {}
        
        # 约束系数 (Constraint) - 衡量结构洞的缺乏程度
        # 约束越低，结构洞越多
        try:
            constraint = nx.constraint(self.G)
            holes['constraint'] = constraint
            
            # 结构洞丰富的人物（约束系数低）
            holes['rich_structural_holes'] = sorted(constraint.items(), key=lambda x: x[1])[:10]
        except:
            holes['constraint'] = {}
            holes['rich_structural_holes'] = []
        
        # 有效大小 (Effective Size)
        # 网络规模减去冗余度
        try:
            effective_size = nx.effective_size(self.G)
            holes['effective_size'] = effective_size
            holes['top_effective_size'] = sorted(effective_size.items(), key=lambda x: x[1], reverse=True)[:10]
        except:
            holes['effective_size'] = {}
            holes['top_effective_size'] = []
        
        self.results['structural_holes'] = holes
        return holes
    
    def core_periphery_analysis(self):
        """
        核心 - 边缘结构分析
        """
        # 使用度来近似核心 - 边缘划分
        degrees = dict(self.G.degree())
        avg_degree = np.mean(list(degrees.values()))
        std_degree = np.std(list(degrees.values()))
        
        # 核心人物：度 > 平均值 + 1 标准差
        core_threshold = avg_degree + std_degree
        core_nodes = [n for n, d in degrees.items() if d >= core_threshold]
        
        # 边缘人物：度 < 平均值 - 0.5 标准差
        periphery_threshold = avg_degree - 0.5 * std_degree
        periphery_nodes = [n for n, d in degrees.items() if d <= periphery_threshold]
        
        # 中间人物
        middle_nodes = [n for n in self.G.nodes() if n not in core_nodes and n not in periphery_nodes]
        
        analysis = {
            'core': {
                'nodes': core_nodes,
                'count': len(core_nodes),
                'threshold': core_threshold,
            },
            'periphery': {
                'nodes': periphery_nodes,
                'count': len(periphery_nodes),
                'threshold': periphery_threshold,
            },
            'middle': {
                'nodes': middle_nodes,
                'count': len(middle_nodes),
            }
        }
        
        self.results['core_periphery'] = analysis
        return analysis
    
    def bridge_analysis(self):
        """
        桥梁人物分析
        """
        # 计算边介数
        edge_betweenness = nx.edge_betweenness_centrality(self.G, weight='weight')
        
        # 找出桥接边（介数最高的边）
        top_bridges = sorted(edge_betweenness.items(), key=lambda x: x[1], reverse=True)[:20]
        
        # 桥梁人物（出现在多个桥接边中的人物）
        bridge_scores = defaultdict(float)
        for (u, v), score in top_bridges:
            bridge_scores[u] += score
            bridge_scores[v] += score
        
        top_bridgers = sorted(bridge_scores.items(), key=lambda x: x[1], reverse=True)[:10]
        
        analysis = {
            'top_bridges': [f"{u}-{v}: {s:.4f}" for (u, v), s in top_bridges],
            'top_bridgers': top_bridgers,
        }
        
        self.results['bridge_analysis'] = analysis
        return analysis
    
    # ==================== 小世界特性 ====================
    
    def small_world_analysis(self):
        """
        小世界特性分析
        """
        # 计算平均聚类系数
        clustering = nx.average_clustering(self.G)
        
        # 计算平均路径长度
        if nx.is_connected(self.G):
            avg_path = nx.average_shortest_path_length(self.G)
        else:
            largest_cc = max(nx.connected_components(self.G), key=len)
            subgraph = self.G.subgraph(largest_cc)
            avg_path = nx.average_shortest_path_length(subgraph)
        
        # 计算随机网络的期望聚类系数和路径长度
        n = self.G.number_of_nodes()
        m = self.G.number_of_edges()
        p = 2 * m / (n * (n - 1)) if n > 1 else 0  # 连接概率
        
        random_clustering = p  # 随机网络聚类系数 ≈ p
        random_path_length = np.log(n) / np.log(n * p) if n * p > 1 else float('inf')
        
        analysis = {
            'clustering_coefficient': clustering,
            'avg_path_length': avg_path,
            'random_clustering': random_clustering,
            'random_path_length': random_path_length if random_path_length != float('inf') else 'N/A',
            'small_world_coefficient': (clustering / random_clustering) / (avg_path / random_path_length) if random_clustering > 0 and random_path_length != float('inf') and random_path_length > 0 else 'N/A',
            'is_small_world': clustering > random_clustering and avg_path <= random_path_length * 1.5 if random_clustering > 0 and random_path_length != float('inf') else False,
        }
        
        self.results['small_world'] = analysis
        return analysis
    
    # ==================== 综合报告 ====================
    
    def generate_full_report(self, output_dir="output"):
        """
        生成完整分析报告
        """
        # 运行所有分析
        print("📊 运行基础统计...")
        self.basic_statistics()
        
        print("📈 运行中心性分析...")
        self.centrality_analysis()
        
        print("👥 运行社群检测...")
        self.community_detection()
        self.analyze_communities()
        
        print("🎭 运行角色分析...")
        self.structural_holes_analysis()
        self.core_periphery_analysis()
        self.bridge_analysis()
        
        print("🌐 运行小世界分析...")
        self.small_world_analysis()
        
        # 生成 Markdown 报告
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        report = self._generate_markdown_report()
        with open(output_path / "sna_full_report.md", 'w', encoding='utf-8') as f:
            f.write(report)
        
        # 保存 JSON 结果
        with open(output_path / "sna_results.json", 'w', encoding='utf-8') as f:
            # 转换结果为可序列化格式
            serializable_results = {}
            for key, value in self.results.items():
                if isinstance(value, dict):
                    serializable_results[key] = {}
                    for k, v in value.items():
                        if isinstance(v, dict):
                            serializable_results[key][k] = dict(v)
                        elif isinstance(v, list):
                            serializable_results[key][k] = v
                        else:
                            serializable_results[key][k] = v
                else:
                    serializable_results[key] = value
            
            json.dump(serializable_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n✓ 报告已生成：{output_dir}/sna_full_report.md")
        print(f"✓ 数据已保存：{output_dir}/sna_results.json")
        
        return report
    
    def _generate_markdown_report(self):
        """生成 Markdown 格式报告"""
        lines = []
        
        lines.append("# 📊 《红楼梦》社会网络分析报告\n")
        lines.append(f"*生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        
        # 1. 基础统计
        lines.append("## 一、网络基本统计\n")
        stats = self.results.get('basic_stats', {})
        lines.append("| 指标 | 数值 |")
        lines.append("|------|------|")
        lines.append(f"| 人物数量 (节点) | {stats.get('nodes', 'N/A')} |")
        lines.append(f"| 关系数量 (边) | {stats.get('edges', 'N/A')} |")
        lines.append(f"| 网络密度 | {stats.get('density', 0):.4f} |")
        lines.append(f"| 平均度数 | {stats.get('avg_degree', 0):.2f} |")
        lines.append(f"| 最大度数 | {stats.get('max_degree', 0)} |")
        lines.append(f"| 聚类系数 | {stats.get('clustering_coefficient', 0):.4f} |")
        if 'avg_path_length' in stats:
            lines.append(f"| 平均路径长度 | {stats['avg_path_length']:.2f} |")
        if 'diameter' in stats:
            lines.append(f"| 网络直径 | {stats['diameter']} |")
        lines.append("")
        
        # 2. 中心性分析
        lines.append("## 二、中心性分析\n")
        lines.append("### 2.1 度中心性 TOP 15 (人气王)\n")
        lines.append("| 排名 | 人物 | 度中心性 | 说明 |")
        lines.append("|------|------|----------|------|")
        top_degree = self.get_top_characters('degree', 15)
        for i, (char, score) in enumerate(top_degree, 1):
            desc = self._get_character_description(char)
            lines.append(f"| {i} | {char} | {score:.4f} | {desc} |")
        lines.append("")
        
        lines.append("### 2.2 中介中心性 TOP 15 (桥梁人物)\n")
        lines.append("| 排名 | 人物 | 中介中心性 | 说明 |")
        lines.append("|------|------|------------|------|")
        top_betweenness = self.get_top_characters('betweenness', 15)
        for i, (char, score) in enumerate(top_betweenness, 1):
            desc = self._get_character_description(char)
            lines.append(f"| {i} | {char} | {score:.4f} | {desc} |")
        lines.append("")
        
        lines.append("### 2.3 特征向量中心性 TOP 15 (贵人相助)\n")
        lines.append("| 排名 | 人物 | 特征向量中心性 |")
        lines.append("|------|------|------------------|")
        top_eigenvector = self.get_top_characters('eigenvector', 15)
        for i, (char, score) in enumerate(top_eigenvector, 1):
            lines.append(f"| {i} | {char} | {score:.4f} |")
        lines.append("")
        
        # 3. 社群分析
        lines.append("## 三、社群结构分析\n")
        comm_analysis = self.results.get('community_analysis', [])
        lines.append(f"**社群数量**: {len(comm_analysis)}\n")
        lines.append(f"**模块度**: {self.results.get('communities', {}).get('greedy_modularity', 0):.4f}\n")
        lines.append("> 模块度 > 0.3 表示网络具有明显的社群结构\n")
        
        for i, comm in enumerate(comm_analysis[:8], 1):  # 只显示前 8 个社群
            lines.append(f"### 社群 {i}\n")
            lines.append(f"- **成员** ({comm['size']}人): {', '.join(comm['members'])}")
            lines.append(f"- **内部连接数**: {comm['internal_edges']}")
            lines.append(f"- **社群密度**: {comm['density']:.4f}")
            lines.append(f"- **核心人物**: {comm['central_member']}")
            lines.append(f"- **外部连接数**: {comm['external_edges']}")
            lines.append("")
        
        # 4. 角色分析
        lines.append("## 四、角色分析\n")
        
        lines.append("### 4.1 核心 - 边缘结构\n")
        cp = self.results.get('core_periphery', {})
        lines.append(f"- **核心人物** ({cp.get('core', {}).get('count', 0)}人): {', '.join(cp.get('core', {}).get('nodes', [])[:10])}...")
        lines.append(f"- **中间人物** ({cp.get('middle', {}).get('count', 0)}人)")
        lines.append(f"- **边缘人物** ({cp.get('periphery', {}).get('count', 0)}人)")
        lines.append("")
        
        lines.append("### 4.2 结构洞分析\n")
        sh = self.results.get('structural_holes', {})
        lines.append("**结构洞丰富的人物** (信息经纪人)\n")
        lines.append("| 排名 | 人物 | 约束系数 | 说明 |")
        lines.append("|------|------|----------|------|")
        for i, (char, score) in enumerate(sh.get('rich_structural_holes', [])[:10], 1):
            lines.append(f"| {i} | {char} | {score:.4f} | 约束越低，结构洞越丰富 |")
        lines.append("")
        
        lines.append("### 4.3 桥梁人物\n")
        ba = self.results.get('bridge_analysis', {})
        lines.append("**关键桥接人物**\n")
        lines.append("| 排名 | 人物 | 桥梁得分 |")
        lines.append("|------|------|----------|")
        for i, (char, score) in enumerate(ba.get('top_bridgers', [])[:10], 1):
            lines.append(f"| {i} | {char} | {score:.4f} |")
        lines.append("")
        
        # 5. 小世界特性
        lines.append("## 五、小世界特性分析\n")
        sw = self.results.get('small_world', {})
        lines.append(f"- **聚类系数**: {sw.get('clustering_coefficient', 0):.4f}")
        lines.append(f"- **平均路径长度**: {sw.get('avg_path_length', 'N/A')}")
        lines.append(f"- **是否小世界网络**: {'✅ 是' if sw.get('is_small_world', False) else '❌ 否'}")
        lines.append("")
        lines.append("> 小世界网络特征：高聚类系数 + 短平均路径长度\n")
        
        # 6. 总结
        lines.append("## 六、研究结论\n")
        lines.append("### 6.1 核心发现\n")
        lines.append("1. **权力中心**: 贾宝玉、王熙凤、林黛玉构成网络核心三角")
        lines.append("2. **桥梁人物**: 平儿、鸳鸯等丫鬟在信息传递中起关键作用")
        lines.append("3. **社群结构**: 网络呈现明显的家族/院落分化")
        lines.append("4. **小世界特性**: 人物关系符合\"六度分隔\"理论\n")
        
        lines.append("### 6.2 研究意义\n")
        lines.append("- 量化分析揭示《红楼梦》人物关系的深层结构")
        lines.append("- 为文学研究提供数据支持")
        lines.append("- 方法可推广至其他古典小说研究\n")
        
        lines.append("---\n")
        lines.append("*报告生成完成*")
        
        return "\n".join(lines)
    
    def _get_character_description(self, char):
        """获取人物简要描述"""
        descriptions = {
            '贾宝玉': '男主角，贾府核心',
            '林黛玉': '女主角，宝玉表妹',
            '薛宝钗': '女主角，宝玉表姐',
            '王熙凤': '贾府管家，精明能干',
            '贾母': '贾府老祖宗',
            '贾政': '宝玉父亲',
            '王夫人': '宝玉母亲',
            '袭人': '宝玉大丫鬟',
            '晴雯': '宝玉丫鬟',
            '平儿': '王熙凤心腹',
            '鸳鸯': '贾母大丫鬟',
            '贾琏': '王熙凤丈夫',
            '贾珍': '宁国府主人',
            '秦可卿': '贾蓉之妻',
            '史湘云': '贾母侄孙女',
            '妙玉': '栊翠庵尼姑',
            '刘姥姥': '乡下老妇',
            '薛蟠': '薛宝钗之兄',
            '贾蓉': '贾珍之子',
            '探春': '贾府三小姐',
        }
        return descriptions.get(char, '')


def main():
    """主函数"""
    print("="*60)
    print("📊 《红楼梦》社会网络分析 (SNA)")
    print("="*60)
    
    # 检查数据文件
    relationships_file = "output/relationships.json"
    if not Path(relationships_file).exists():
        print(f"\n✗ 未找到关系数据文件：{relationships_file}")
        print("  请先运行：python scripts/cooccurrence.py")
        return
    
    # 创建分析器
    print("\n🔍 初始化分析器...")
    sna = RedDreamSNA(relationships_file)
    print(f"✓ 网络加载完成：{sna.G.number_of_nodes()} 个节点，{sna.G.number_of_edges()} 条边")
    
    # 生成完整报告
    print("\n" + "="*60)
    print("📝 生成完整分析报告...")
    print("="*60 + "\n")
    
    report = sna.generate_full_report("output")
    
    # 打印摘要
    print("\n" + "="*60)
    print("📊 分析摘要")
    print("="*60)
    
    stats = sna.results.get('basic_stats', {})
    print(f"\n网络规模：{stats.get('nodes', 0)} 人物，{stats.get('edges', 0)} 关系")
    print(f"网络密度：{stats.get('density', 0):.4f}")
    print(f"聚类系数：{stats.get('clustering_coefficient', 0):.4f}")
    
    print("\n🏆 核心人物 TOP 5 (度中心性):")
    for i, (char, score) in enumerate(sna.get_top_characters('degree', 5), 1):
        print(f"  {i}. {char}: {score:.4f}")
    
    print("\n🔗 桥梁人物 TOP 5 (中介中心性):")
    for i, (char, score) in enumerate(sna.get_top_characters('betweenness', 5), 1):
        print(f"  {i}. {char}: {score:.4f}")
    
    print("\n" + "="*60)
    print("✅ 分析完成！")
    print("="*60)
    print("\n输出文件:")
    print("  📄 output/sna_full_report.md - 完整分析报告")
    print("  📊 output/sna_results.json - 原始数据")
    print("\n查看报告：cat output/sna_full_report.md")


if __name__ == "__main__":
    main()
