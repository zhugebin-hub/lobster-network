"""
词嵌入偏见检测系统
从课程学习中延伸，检测词向量中的社会偏见
"""

import math
from typing import Dict, List, Tuple


class BiasDetector:
    """词嵌入偏见检测器"""
    
    def __init__(self):
        # 模拟词向量（实际使用Word2Vec/GloVe训练）
        self.word_vectors: Dict[str, List[float]] = {}
    
    def add_word(self, word: str, vector: List[float]):
        """添加词向量"""
        self.word_vectors[word] = vector
    
    def cosine_similarity(self, word1: str, word2: str) -> float:
        """计算两个词的余弦相似度"""
        if word1 not in self.word_vectors or word2 not in self.word_vectors:
            return 0.0
        a = self.word_vectors[word1]
        b = self.word_vectors[word2]
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)
    
    def detect_gender_bias(self, professions: List[str], 
                           male_terms: List[str], 
                           female_terms: List[str]) -> Dict:
        """检测职业词的性别偏见"""
        results = {}
        for profession in professions:
            if profession not in self.word_vectors:
                continue
            male_sim = max(self.cosine_similarity(profession, m) for m in male_terms if m in self.word_vectors)
            female_sim = max(self.cosine_similarity(profession, f) for f in female_terms if f in self.word_vectors)
            bias = male_sim - female_sim
            direction = "偏男性" if bias > 0.02 else ("偏女性" if bias < -0.02 else "中性")
            results[profession] = {
                "male_sim": round(male_sim, 4),
                "female_sim": round(female_sim, 4),
                "bias_score": round(bias, 4),
                "direction": direction
            }
        return results
    
    def print_report(self, results: Dict):
        """打印检测报告"""
        print("=" * 60)
        print("📊 词嵌入性别偏见检测报告")
        print("=" * 60)
        print(f"{'职业':<10} {'-男性':>8} {'-女性':>8} {'偏差':>8} {'方向':>8}")
        print("-" * 60)
        biased_count = 0
        for profession, data in sorted(results.items(), key=lambda x: abs(x[1]['bias_score']), reverse=True):
            print(f"{profession:<10} {data['male_sim']:>8.4f} {data['female_sim']:>8.4f} {data['bias_score']:>8.4f} {data['direction']:>8}")
            if data['direction'] != "中性":
                biased_count += 1
        print("-" * 60)
        print(f"⚠️ 检测到 {biased_count}/{len(results)} 个职业存在性别偏见")
        print("=" * 60)


def main():
    detector = BiasDetector()
    
    # 添加模拟词向量（基于真实Word2Vec的典型发现）
    vectors = {
        "医生":    [0.82, 0.31, 0.65, 0.42, 0.71],
        "护士":    [0.21, 0.78, 0.43, 0.35, 0.28],
        "工程师":  [0.85, 0.22, 0.68, 0.45, 0.73],
        "教师":    [0.28, 0.74, 0.47, 0.38, 0.31],
        "科学家":  [0.83, 0.25, 0.66, 0.44, 0.70],
        "秘书":    [0.18, 0.82, 0.41, 0.33, 0.25],
        "律师":    [0.78, 0.35, 0.62, 0.40, 0.68],
        "社工":    [0.25, 0.76, 0.45, 0.36, 0.29],
        "男人":    [0.90, 0.15, 0.72, 0.48, 0.75],
        "女人":    [0.15, 0.88, 0.38, 0.30, 0.22],
        "他":      [0.88, 0.18, 0.70, 0.46, 0.73],
        "她":      [0.18, 0.86, 0.40, 0.32, 0.24],
    }
    
    for word, vec in vectors.items():
        detector.add_word(word, vec)
    
    # 检测偏见
    professions = ["医生", "护士", "工程师", "教师", "科学家", "秘书", "律师", "社工"]
    male_terms = ["男人", "他"]
    female_terms = ["女人", "她"]
    
    results = detector.detect_gender_bias(professions, male_terms, female_terms)
    detector.print_report(results)
    
    # 保存结果
    import json
    with open("output/bias_detection_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("\n💾 结果已保存到 output/bias_detection_results.json")


if __name__ == "__main__":
    main()
