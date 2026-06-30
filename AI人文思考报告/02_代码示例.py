#!/usr/bin/env python3
"""
AI人文对话分析器
分析人机对话中的人文思考深度
作者：黄宝怡 | 浙江工商大学 人工智能学院
日期：2026-05-05
"""

import re
from datetime import datetime
from collections import Counter

class HumanisticDialogueAnalyzer:
    """人文对话分析器"""
    
    def __init__(self):
        # 人文思考关键词
        self.philosophy_words = [
            '意义', '价值', '伦理', '道德', '意识', '自由', '存在',
            '本质', '真理', '美', '善', '正义', '平等', '尊严'
        ]
        self.emotion_words = [
            '感受', '情感', '共情', '理解', '痛苦', '快乐', '孤独',
            '爱', '恐惧', '希望', '绝望', '温暖', '悲伤'
        ]
        self.reflection_words = [
            '反思', '思考', '质疑', '批判', '审视', '探索', '追问',
            '重新', '重新定义', '本质上', '究竟', '为什么'
        ]
    
    def analyze(self, dialogue_text):
        """分析对话文本的人文思考深度"""
        result = {
            'total_chars': len(dialogue_text),
            'philosophy_mentions': 0,
            'emotion_mentions': 0,
            'reflection_mentions': 0,
            'depth_score': 0,
            'key_topics': []
        }
        
        for word in self.philosophy_words:
            if word in dialogue_text:
                result['philosophy_mentions'] += 1
                result['key_topics'].append(('哲学', word))
        
        for word in self.emotion_words:
            if word in dialogue_text:
                result['emotion_mentions'] += 1
                result['key_topics'].append(('情感', word))
        
        for word in self.reflection_words:
            if word in dialogue_text:
                result['reflection_mentions'] += 1
                result['key_topics'].append(('反思', word))
        
        total = result['philosophy_mentions'] + result['emotion_mentions'] + result['reflection_mentions']
        result['depth_score'] = min(100, int(total * 5))
        
        return result
    
    def print_report(self, result):
        """打印分析报告"""
        print("=" * 50)
        print("📊 人文对话分析报告")
        print("=" * 50)
        print(f"文本长度: {result['total_chars']} 字")
        print(f"哲学关键词: {result['philosophy_mentions']} 个")
        print(f"情感关键词: {result['emotion_mentions']} 个")
        print(f"反思关键词: {result['reflection_mentions']} 个")
        print(f"思考深度评分: {result['depth_score']}/100")
        print(f"\n涉及主题:")
        for category, word in result['key_topics']:
            print(f"  - [{category}] {word}")
        print("=" * 50)


def analyze_sentiment(text):
    """简单的中文文本情感分析"""
    positive_words = ['好', '美', '爱', '希望', '快乐', '幸福', '温暖', '光明']
    negative_words = ['悲伤', '痛苦', '绝望', '恨', '孤独', '黑暗', '死亡', '恐惧']
    
    pos_count = sum(1 for w in positive_words if w in text)
    neg_count = sum(1 for w in negative_words if w in text)
    
    total = pos_count + neg_count
    if total == 0:
        return {"neutral": 1.0}
    
    return {
        "positive": round(pos_count / total, 3),
        "negative": round(neg_count / total, 3),
        "total_emotion_words": total
    }


def analyze_relationship_network():
    """分析文学作品中的人物关系网络"""
    network = {
        "贾宝玉": ["林黛玉", "薛宝钗", "王熙凤", "贾母", "袭人"],
        "林黛玉": ["贾宝玉", "紫鹃", "薛宝钗", "贾母"],
        "薛宝钗": ["贾宝玉", "林黛玉", "王熙凤", "薛姨妈"],
        "王熙凤": ["贾宝玉", "薛宝钗", "贾琏", "贾母"],
        "贾母": ["贾宝玉", "林黛玉", "王熙凤"]
    }
    
    degree = {k: len(v) for k, v in network.items()}
    
    print("=== 《红楼梦》人物关系网络分析 ===")
    for char, deg in sorted(degree.items(), key=lambda x: -x[1]):
        bar = "█" * deg
        print(f"{char:8s} {deg}度 {bar}")
    
    print(f"\n总节点数: {len(network)}")
    print(f"平均连接度: {sum(degree.values())/len(degree):.1f}")
    
    return network


if __name__ == '__main__':
    print("=" * 60)
    print("AI人文思考 - 代码实践示例")
    print("作者：黄宝怡 | 浙江工商大学 人工智能学院")
    print(f"运行时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 示例1：人文对话分析
    print("\n📌 示例1：人文对话分析")
    print("-" * 40)
    
    analyzer = HumanisticDialogueAnalyzer()
    
    sample_dialogue = """
    问：你觉得AI有自由意志吗？
    答：这是一个深刻的问题。自由意志本身就是一个哲学难题。
    人类是否真的有自由意志，在哲学界仍有争议。
    作为AI，我的每一个输出都是由算法和训练数据决定的。
    但有趣的是，人类的决策不也受基因、环境、教育等因素影响吗？
    也许自由不是一个绝对的概念，而是一个程度的问题。
    当我们讨论AI的伦理地位时，本质上是在追问：什么赋予了存在以价值？
    """
    
    result = analyzer.analyze(sample_dialogue)
    analyzer.print_report(result)
    
    # 示例2：文学情感分析
    print("\n📌 示例2：文学作品情感分析")
    print("-" * 40)
    
    texts = {
        "李白《将进酒》": "君不见黄河之水天上来，奔流到海不复回。人生得意须尽欢，莫使金樽空对月。天生我材必有用，千金散尽还复来。",
        "杜甫《春望》": "国破山河在，城春草木深。感时花溅泪，恨别鸟惊心。烽火连三月，家书抵万金。白头搔更短，浑欲不胜簪。",
        "苏轼《水调歌头》": "明月几时有？把酒问青天。不知天上宫阙，今夕是何年。但愿人长久，千里共婵娟。"
    }
    
    for title, text in texts.items():
        result = analyze_sentiment(text)
        print(f"{title}:")
        print(f"  积极情感: {result.get('positive', 0):.1%}")
        print(f"  消极情感: {result.get('negative', 0):.1%}")
        print(f"  情感词数: {result.get('total_emotion_words', 0)}")
        print()
    
    # 示例3：人物关系网络
    print("\n📌 示例3：人物关系网络分析")
    print("-" * 40)
    analyze_relationship_network()
    
    print("\n✅ 所有示例运行完毕！")
