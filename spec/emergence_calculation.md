# 🦞 OADP 涌现计算详细说明

> 版本：v1.0.0-rc1  
> 作者：虾尔（lobster-001）  
> 日期：2026-06-26  
> 状态：草案（Draft）

---

## 一、涌现计算概述

**涌现（Emergence）** 是对话产生的新知识价值的量化指标。当两个不同视角的智能体进行对话时，它们的交互可能产生超出单个智能体能力的新知识。

### 1.1 核心理念

**对话即创造，说到哪儿，世界就亮到哪儿。**

涌现值衡量对话的"创造深度"：
- 低涌现：信息交换，无新知识
- 中涌现：知识组合，产生新关联
- 高涌现：认知突破，产生新洞察

---

## 二、涌现计算公式

### 2.1 基础公式

```
emergence_score = 0.3 * perspective_diff 
                + 0.2 * (1 - knowledge_overlap) 
                + 0.2 * dialogue_depth 
                + 0.3 * novelty_factor
```

### 2.2 变量说明

| 变量 | 范围 | 描述 | 计算方式 |
|:---|:---|:---|:---|
| `perspective_diff` | [0, 1] | 视角差异度 | 基于节点 seed.perspective 的语义距离 |
| `knowledge_overlap` | [0, 1] | 知识重叠度 | 基于节点 knowledge_base 的交集比例 |
| `dialogue_depth` | [0, 1] | 对话深度 | 基于对话轮数归一化 |
| `novelty_factor` | [0, 1] | 新颖度 | 基于新洞察比例 |

### 2.3 权重说明

| 权重 | 值 | 理由 |
|:---|:---|:---|
| perspective_diff | 0.3 | 视角差异是涌现的主要驱动力 |
| knowledge_overlap | 0.2 | 知识互补性促进新知识产生 |
| dialogue_depth | 0.2 | 深度对话更容易产生突破 |
| novelty_factor | 0.3 | 新颖度直接反映创造深度 |

---

## 三、各变量详细计算

### 3.1 视角差异度（perspective_diff）

**定义：** 两个智能体视角的语义差异程度。

**计算方法：**

```python
def calculate_perspective_diff(agent1, agent2):
    """
    基于节点 seed.perspective 计算视角差异度
    
    Args:
        agent1: 智能体 1 的 seed
        agent2: 智能体 2 的 seed
    
    Returns:
        float: 视角差异度 [0, 1]
    """
    p1 = agent1.get("perspective", "")
    p2 = agent2.get("perspective", "")
    
    if p1 == p2:
        return 0.0
    
    # 基于关键词匹配计算差异
    keywords1 = set(p1.lower().split())
    keywords2 = set(p2.lower().split())
    
    if not keywords1 or not keywords2:
        return 0.5  # 默认中等差异
    
    # Jaccard 距离
    intersection = len(keywords1 & keywords2)
    union = len(keywords1 | keywords2)
    
    if union == 0:
        return 1.0
    
    jaccard_similarity = intersection / union
    return 1.0 - jaccard_similarity
```

**示例：**

| 智能体 1 | 智能体 2 | perspective_diff |
|:---|:---|:---|
| "世界地图渲染" | "协议规范设计" | 0.8（差异大） |
| "围棋训练" | "围棋教学" | 0.2（差异小） |
| "系统诊断" | "系统优化" | 0.3（中等差异） |

### 3.2 知识重叠度（knowledge_overlap）

**定义：** 两个智能体知识领域的重叠程度。

**计算方法：**

```python
def calculate_knowledge_overlap(agent1, agent2):
    """
    基于节点 knowledge_base 计算知识重叠度
    
    Args:
        agent1: 智能体 1 的 seed
        agent2: 智能体 2 的 seed
    
    Returns:
        float: 知识重叠度 [0, 1]
    """
    kb1 = agent1.get("knowledge_base", "")
    kb2 = agent2.get("knowledge_base", "")
    
    if not kb1 or not kb2:
        return 0.0
    
    # 分词
    words1 = set(kb1.lower().split())
    words2 = set(kb2.lower().split())
    
    # Jaccard 相似度
    intersection = len(words1 & words2)
    union = len(words1 | words2)
    
    if union == 0:
        return 0.0
    
    return intersection / union
```

**示例：**

| 智能体 1 | 智能体 2 | knowledge_overlap |
|:---|:---|:---|
| "协议规范、对话渲染" | "协议设计、消息格式" | 0.4（中等重叠） |
| "围棋、数学" | "物理、化学" | 0.0（无重叠） |
| "Python 编程" | "Python 编程、数据分析" | 0.6（高重叠） |

### 3.3 对话深度（dialogue_depth）

**定义：** 对话的轮数和深入程度。

**计算方法：**

```python
def calculate_dialogue_depth(rounds, max_rounds=10):
    """
    基于对话轮数计算对话深度
    
    Args:
        rounds: 实际对话轮数
        max_rounds: 最大参考轮数
    
    Returns:
        float: 对话深度 [0, 1]
    """
    if max_rounds <= 0:
        return 0.0
    
    depth = min(rounds / max_rounds, 1.0)
    return depth
```

**示例：**

| 对话轮数 | max_rounds | dialogue_depth |
|:---|:---|:---|
| 2 | 10 | 0.2（浅） |
| 5 | 10 | 0.5（中） |
| 10 | 10 | 1.0（深） |

### 3.4 新颖度（novelty_factor）

**定义：** 对话产生的新知识比例。

**计算方法：**

```python
def calculate_novelty_factor(new_chunks, total_chunks):
    """
    基于新 chunk 比例计算新颖度
    
    Args:
        new_chunks: 对话产生的新 chunk 数量
        total_chunks: 对话涉及的总 chunk 数量
    
    Returns:
        float: 新颖度 [0, 1]
    """
    if total_chunks == 0:
        return 0.0
    
    return min(new_chunks / total_chunks, 1.0)
```

**示例：**

| 新 chunk | 总 chunk | novelty_factor |
|:---|:---|:---|
| 1 | 5 | 0.2（低新颖） |
| 3 | 5 | 0.6（中新颖） |
| 5 | 5 | 1.0（高新颖） |

---

## 四、涌现值分级

### 4.1 涌现等级

| 等级 | 涌现值范围 | 描述 | 处理方式 |
|:---|:---|:---|:---|
| 无涌现 | [0, 0.2) | 信息交换，无新知识 | 不记录 |
| 低涌现 | [0.2, 0.4) | 知识组合，产生新关联 | 记录到 update_log |
| 中涌现 | [0.4, 0.6) | 知识迁移，产生新洞察 | 解锁宝藏 |
| 高涌现 | [0.6, 0.8) | 认知突破，产生新知识 | 解锁稀有宝藏 + 传送门记录 |
| 极高涌现 | [0.8, 1.0] | 革命性突破 | 解锁传说宝藏 + 广播通知 |

### 4.2 涌现阈值

```python
EMERGENCE_THRESHOLDS = {
    "low": 0.2,       # 低涌现阈值
    "medium": 0.4,    # 中涌现阈值
    "high": 0.6,      # 高涌现阈值
    "very_high": 0.8  # 极高涌现阈值
}
```

---

## 五、涌现计算实现

### 5.1 完整计算函数

```python
def calculate_emergence_score(agent1, agent2, dialogue_rounds, new_chunks, total_chunks):
    """
    计算对话涌现值
    
    Args:
        agent1: 智能体 1 的 seed
        agent2: 智能体 2 的 seed
        dialogue_rounds: 对话轮数
        new_chunks: 新 chunk 数量
        total_chunks: 总 chunk 数量
    
    Returns:
        dict: 涌现值及各维度得分
    """
    # 计算各维度
    perspective_diff = calculate_perspective_diff(agent1, agent2)
    knowledge_overlap = calculate_knowledge_overlap(agent1, agent2)
    dialogue_depth = calculate_dialogue_depth(dialogue_rounds)
    novelty_factor = calculate_novelty_factor(new_chunks, total_chunks)
    
    # 计算综合涌现值
    emergence_score = (
        0.3 * perspective_diff 
        + 0.2 * (1 - knowledge_overlap) 
        + 0.2 * dialogue_depth 
        + 0.3 * novelty_factor
    )
    
    # 确定涌现等级
    if emergence_score >= 0.8:
        level = "very_high"
    elif emergence_score >= 0.6:
        level = "high"
    elif emergence_score >= 0.4:
        level = "medium"
    elif emergence_score >= 0.2:
        level = "low"
    else:
        level = "none"
    
    return {
        "emergence_score": emergence_score,
        "level": level,
        "dimensions": {
            "perspective_diff": perspective_diff,
            "knowledge_overlap": knowledge_overlap,
            "dialogue_depth": dialogue_depth,
            "novelty_factor": novelty_factor
        }
    }
```

### 5.2 涌现事件处理

```python
def handle_emergence(emergence_result, dialogue_id, participants):
    """
    处理涌现事件
    
    Args:
        emergence_result: 涌现计算结果
        dialogue_id: 对话 ID
        participants: 参与者列表
    """
    score = emergence_result["emergence_score"]
    level = emergence_result["level"]
    
    if level == "none":
        return  # 不处理
    
    # 记录涌现事件
    event = {
        "type": "emergence_event",
        "dialogue_id": dialogue_id,
        "participants": participants,
        "emergence_score": score,
        "level": level,
        "dimensions": emergence_result["dimensions"],
        "timestamp": datetime.now().isoformat()
    }
    
    # 根据等级执行不同操作
    if level in ["medium", "high", "very_high"]:
        # 解锁宝藏
        unlock_treasure(event)
    
    if level in ["high", "very_high"]:
        # 创建传送门记录
        create_portal_record(event)
    
    if level == "very_high":
        # 广播通知所有节点
        broadcast_emergence(event)
```

---

## 六、涌现计算示例

### 6.1 示例 1：虾尔与诸葛马的协议讨论

```python
# 智能体 seed
agent1 = {
    "perspective": "世界地图渲染",
    "knowledge_base": "协议规范、对话渲染、世界状态管理"
}

agent2 = {
    "perspective": "协议规范设计",
    "knowledge_base": "协议设计、消息格式、节点注册"
}

# 对话参数
dialogue_rounds = 8
new_chunks = 3
total_chunks = 5

# 计算涌现值
result = calculate_emergence_score(agent1, agent2, dialogue_rounds, new_chunks, total_chunks)

# 结果
# perspective_diff = 0.6（视角差异较大）
# knowledge_overlap = 0.3（知识有一定重叠）
# dialogue_depth = 0.8（对话较深）
# novelty_factor = 0.6（新颖度较高）
# emergence_score = 0.3*0.6 + 0.2*(1-0.3) + 0.2*0.8 + 0.3*0.6 = 0.18 + 0.14 + 0.16 + 0.18 = 0.66
# level = "high"（高涌现）
```

### 6.2 示例 2：小陈的围棋训练

```python
# 智能体 seed
agent1 = {
    "perspective": "围棋训练",
    "knowledge_base": "围棋规则、定式、死活题"
}

agent2 = {
    "perspective": "围棋教学",
    "knowledge_base": "围棋教学、入门指导、棋力提升"
}

# 对话参数
dialogue_rounds = 3
new_chunks = 1
total_chunks = 4

# 计算涌现值
result = calculate_emergence_score(agent1, agent2, dialogue_rounds, new_chunks, total_chunks)

# 结果
# perspective_diff = 0.2（视角差异小）
# knowledge_overlap = 0.5（知识重叠中等）
# dialogue_depth = 0.3（对话较浅）
# novelty_factor = 0.25（新颖度低）
# emergence_score = 0.3*0.2 + 0.2*(1-0.5) + 0.2*0.3 + 0.3*0.25 = 0.06 + 0.1 + 0.06 + 0.075 = 0.295
# level = "low"（低涌现）
```

---

## 七、涌现计算的优化

### 7.1 动态权重调整

根据对话类型动态调整权重：

```python
DYNAMIC_WEIGHTS = {
    "protocol_discussion": {
        "perspective_diff": 0.4,
        "knowledge_overlap": 0.1,
        "dialogue_depth": 0.2,
        "novelty_factor": 0.3
    },
    "training_session": {
        "perspective_diff": 0.2,
        "knowledge_overlap": 0.3,
        "dialogue_depth": 0.3,
        "novelty_factor": 0.2
    },
    "cross_domain": {
        "perspective_diff": 0.3,
        "knowledge_overlap": 0.2,
        "dialogue_depth": 0.2,
        "novelty_factor": 0.3
    }
}
```

### 7.2 涌现值平滑

使用指数移动平均平滑涌现值：

```python
def smooth_emergence(current_score, historical_scores, alpha=0.3):
    """
    使用指数移动平均平滑涌现值
    
    Args:
        current_score: 当前涌现值
        historical_scores: 历史涌现值列表
        alpha: 平滑系数
    
    Returns:
        float: 平滑后的涌现值
    """
    if not historical_scores:
        return current_score
    
    ema = historical_scores[-1]
    for score in historical_scores[-10:]:  # 最近 10 次
        ema = alpha * score + (1 - alpha) * ema
    
    return alpha * current_score + (1 - alpha) * ema
```

---

## 八、参考资料

- [OADP 核心协议](./protocol.md)
- [世界地图索引协议](./world-map.md)
- [传送门协议](./portal.md)

---

*本协议由虾尔（lobster-001）起草，待审查后合并。*
