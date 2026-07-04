#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
红楼梦人物关系共现分析
基于滑动窗口的人物共现统计
"""

import jieba
import networkx as nx
import json
from collections import defaultdict
from pathlib import Path

# 主要人物名单
MAIN_CHARACTERS = [
    # 核心主角
    "贾宝玉", "宝玉", "林黛玉", "黛玉", "薛宝钗", "宝钗",
    
    # 贾府长辈
    "贾母", "王夫人", "邢夫人", "贾政", "贾赦", "贾珍",
    
    # 王熙凤相关
    "王熙凤", "熙凤", "凤姐", "平儿",
    
    # 贾府姐妹
    "李纨", "贾元春", "贾迎春", "贾探春", "贾惜春", "史湘云", "妙玉",
    
    # 重要丫鬟
    "袭人", "晴雯", "麝月", "秋纹", "紫鹃", "雪雁", "鸳鸯", "司棋",
    
    # 薛家
    "薛姨妈", "薛蟠", "薛蝌", "薛宝琴",
    
    # 贾府男性
    "贾蓉", "贾蔷", "贾芸", "贾兰", "贾环",
    
    # 其他重要人物
    "秦可卿", "刘姥姥", "甄士隐", "贾雨村", "柳湘莲", "尤三姐", "尤二姐",
    "北静王", "蒋玉菡", "花袭人",
]

# 人物名称规范化映射
CHAR_NAME_MAP = {
    "宝玉": "贾宝玉",
    "黛玉": "林黛玉",
    "宝钗": "薛宝钗",
    "熙凤": "王熙凤",
    "凤姐": "王熙凤",
    "袭人": "花袭人",
}


def load_text(file_path):
    """加载文本文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()


def find_character_positions(text, characters):
    """
    查找所有人物在文本中的位置
    
    Returns:
        dict: {人物名：[位置列表]}
    """
    positions = defaultdict(list)
    
    for char in characters:
        pos = 0
        while True:
            pos = text.find(char, pos)
            if pos == -1:
                break
            positions[char].append(pos)
            pos += len(char)
    
    return positions


def extract_cooccurrence(positions, window_size=100):
    """
    基于共现窗口统计人物关系
    
    Args:
        positions: 人物位置字典
        window_size: 共现窗口大小（字符数）
    
    Returns:
        dict: {(人物 1, 人物 2): 共现次数}
    """
    relationships = defaultdict(int)
    
    # 构建所有位置列表
    all_positions = []
    for char, pos_list in positions.items():
        for pos in pos_list:
            all_positions.append((pos, char))
    
    all_positions.sort()
    
    # 滑动窗口统计共现
    for i, (pos1, char1) in enumerate(all_positions):
        for j in range(i + 1, len(all_positions)):
            pos2, char2 = all_positions[j]
            
            # 超出窗口则停止
            if pos2 - pos1 > window_size:
                break
            
            # 统计共现（不统计自己）
            if char1 != char2:
                pair = tuple(sorted([char1, char2]))
                relationships[pair] += 1
    
    return relationships


def normalize_characters(relationships, name_map):
    """
    规范化人物名称
    """
    normalized = defaultdict(int)
    
    for (char1, char2), count in relationships.items():
        c1 = name_map.get(char1, char1)
        c2 = name_map.get(char2, char2)
        pair = tuple(sorted([c1, c2]))
        if pair[0] != pair[1]:  # 排除自己
            normalized[pair] += count
    
    return normalized


def build_network(relationships, min_weight=3):
    """
    构建人物关系网络
    
    Args:
        relationships: 关系字典
        min_weight: 最小权重阈值
    
    Returns:
        networkx.Graph
    """
    G = nx.Graph()
    
    for (char1, char2), weight in relationships.items():
        if weight >= min_weight:
            G.add_edge(char1, char2, weight=weight)
    
    return G


def analyze_network(G):
    """
    网络分析
    """
    results = {
        'basic': {
            'nodes': G.number_of_nodes(),
            'edges': G.number_of_edges(),
            'density': nx.density(G),
            'avg_degree': sum(dict(G.degree()).values()) / max(G.number_of_nodes(), 1),
        },
        'centrality': {
            'degree': nx.degree_centrality(G),
            'betweenness': nx.betweenness_centrality(G),
            'closeness': nx.closeness_centrality(G),
        },
        'communities': list(nx.community.greedy_modularity_communities(G)) if G.number_of_nodes() > 0 else [],
    }
    
    if G.number_of_nodes() > 0 and nx.is_connected(G):
        results['basic']['avg_path_length'] = nx.average_shortest_path_length(G)
        results['basic']['clustering'] = nx.average_clustering(G)
    
    return results


def save_results(relationships, G, analysis, output_dir="output"):
    """保存结果"""
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # 保存关系数据
    with open(output_path / "relationships.json", 'w', encoding='utf-8') as f:
        json.dump({f"{k[0]}|{k[1]}": v for k, v in relationships.items()}, f, ensure_ascii=False, indent=2)
    
    # 保存分析结果
    with open(output_path / "analysis.json", 'w', encoding='utf-8') as f:
        # 转换中心性数据（networkx 的 Key 不能直接 JSON 序列化）
        analysis_json = {
            'basic': analysis['basic'],
            'top_degree': sorted(analysis['centrality']['degree'].items(), key=lambda x: x[1], reverse=True)[:20],
            'top_betweenness': sorted(analysis['centrality']['betweenness'].items(), key=lambda x: x[1], reverse=True)[:20],
            'communities': [list(c) for c in analysis['communities']],
        }
        json.dump(analysis_json, f, ensure_ascii=False, indent=2)
    
    # 保存边列表（供 Gephi 使用）
    with open(output_path / "edges_for_gephi.csv", 'w', encoding='utf-8') as f:
        f.write("Source,Target,Weight,Type\n")
        for u, v, data in G.edges(data=True):
            f.write(f"{u},{v},{data.get('weight', 1)},Undirected\n")
    
    print(f"结果已保存至 {output_dir}/")


def main():
    """主函数"""
    print("📖 红楼梦人物关系分析开始...")
    
    # 1. 加载文本
    text_file = "data/hongloumeng.txt"
    try:
        text = load_text(text_file)
        print(f"✓ 已加载文本：{len(text)} 字符")
    except FileNotFoundError:
        print(f"✗ 未找到文本文件：{text_file}")
        print("  请从以下地址下载红楼梦文本:")
        print("  - https://www.gutenberg.org/files/24260/24260-0.txt")
        print("  - https://ctext.org/honglou-meng")
        return
    
    # 2. 查找人物位置
    print("正在查找人物位置...")
    positions = find_character_positions(text, MAIN_CHARACTERS)
    print(f"✓ 找到 {len(positions)} 个人物")
    
    # 3. 提取共现关系
    print("正在提取共现关系...")
    relationships = extract_cooccurrence(positions, window_size=100)
    print(f"✓ 提取 {len(relationships)} 个关系对")
    
    # 4. 规范化人物名称
    relationships = normalize_characters(relationships, CHAR_NAME_MAP)
    print(f"✓ 规范化后 {len(relationships)} 个关系对")
    
    # 5. 构建网络
    print("正在构建网络...")
    G = build_network(relationships, min_weight=3)
    print(f"✓ 网络：{G.number_of_nodes()} 个节点，{G.number_of_edges()} 条边")
    
    # 6. 分析网络
    print("正在分析网络...")
    analysis = analyze_network(G)
    
    # 7. 输出结果
    print("\n" + "="*50)
    print("📊 分析结果")
    print("="*50)
    print(f"人物数量：{analysis['basic']['nodes']}")
    print(f"关系数量：{analysis['basic']['edges']}")
    print(f"网络密度：{analysis['basic']['density']:.4f}")
    
    print("\n🏆 核心人物 TOP 10 (按度中心性):")
    for i, (char, score) in enumerate(analysis['centrality']['degree'].items(), 1):
        if i > 10:
            break
        print(f"  {i}. {char}: {score:.4f}")
    
    print("\n🔗 桥梁人物 TOP 10 (按中介中心性):")
    for i, (char, score) in enumerate(analysis['centrality']['betweenness'].items(), 1):
        if i > 10:
            break
        print(f"  {i}. {char}: {score:.4f}")
    
    print(f"\n👥 社群数量：{len(analysis['communities'])}")
    
    # 8. 保存结果
    save_results(relationships, G, analysis)
    
    print("\n✓ 分析完成！")
    print("\n下一步:")
    print("  1. 运行 python scripts/visualize.py 生成可视化")
    print("  2. 用 Gephi 打开 output/edges_for_gephi.csv 进行美化")
    print("  3. 查看 output/analysis.json 获取详细数据")


if __name__ == "__main__":
    main()
