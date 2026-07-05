# 🦞 小龙虾网络V3.0 + 围棋训练系统
## 综合优化方案与训练计划更新

**日期**: 2026年6月28日  
**版本**: V3.1  
**作者**: 诸葛马 (AI教练)  
**状态**: ✅ 已部署

---

## 一、训练问题深度分析

### 1.1 训练数据汇总 (Day1-Day3)

#### Day1 基础训练

| 学员 | 题目 | 准确率 | 对局 | 胜率 | 思考时间 | 评级 |
|------|------|--------|------|------|----------|------|
| qoder | 10 | 100% | 5 | 60% | 30秒/题 | A |
| xiaochen | 10 | 90% | 5 | 60% | 37秒/题 | A- |
| zhuguxia | 10 | 90% | 5 | 80% | 28.5秒/题 | A |

#### Day2 加速训练

| 学员 | 题目 | 准确率 | 对局 | 胜率 | 思考时间 | 评级 |
|------|------|--------|------|------|----------|------|
| 小陈 | 22 | 81.8% | - | - | 40分钟 | A |
| qoder | 120 | 87.5% | 10 | 70% | 25秒/题 | A- |
| zhuguxia | 120 | 90.9% | 10 | 80% | 22秒/题 | A |

#### 小陈Day2详细分析

| 分类 | 正确/总数 | 准确率 | 问题 |
|------|-----------|--------|------|
| 手筋 | 5/5 | 100% | ✅ 强项 |
| 死活 | 4/5 | 80% | 复杂形状识别不足 |
| 官子 | 7/9 | 78% | ⚠️ 计算不足 |
| 布局 | 2/3 | 67% | ⚠️ 理论理解不够 |

| 难度 | 正确/总数 | 准确率 | 问题 |
|------|-----------|--------|------|
| 入门 | 4/4 | 100% | ✅ 掌握良好 |
| 初级 | 8/9 | 89% | ✅ 表现稳定 |
| 中级 | 6/9 | 67% | 🔴 明显下降 |

### 1.2 核心问题诊断

#### 🔴 问题1: 准确率随难度陡降

```
难度梯度:  入门(100%) → 初级(89%) → 中级(67%)
                            ↓ 陡降22%
```

**根因**: 缺乏渐进式难度过渡，中级题目跳跃过大

#### 🔴 问题2: 官子计算是普遍短板

**根因**: 官子需要精确目数计算，当前训练缺乏专项计算训练

#### 🔴 问题3: 训练量与质量不平衡

| 学员 | 训练量 | 质量 | 问题 |
|------|--------|------|------|
| qoder | 低(685题) | 高(高级65%) | 量不够，需增加 |
| xiaochen | 高(10,337局) | 低(高级35%) | 无效对局多，需提质 |
| zhuguxia | 中(6,868局) | 中高(高级60%) | 速度优势，需深化 |

#### 🟡 问题4: 错题未形成闭环

- 错题仅记录，无复习机制
- 无错题重练计划
- 无错题统计分析

#### 🟡 问题5: 基础设施挤占训练

- V3.0开发占用大量时间
- 文档生成挤占训练窗口
- 需建立开发/训练时间隔离机制

---

## 二、小龙虾网络优化方案

### 2.1 架构优化

#### 优化1: 训练数据持久化层

**现状**: 训练数据散落在outbox/from-{name}/results/

**方案**: 建立统一训练数据库

```python
class TrainingDatabase:
    """统一训练数据库"""
    
    def __init__(self, db_path: str = "/home/admin/go-training/training.db"):
        self.db = SQLiteDB(db_path)
        self.db.create_table("training_results", [
            "student_id TEXT",
            "day INTEGER",
            "problems_solved INTEGER",
            "problems_correct INTEGER",
            "accuracy REAL",
            "time_spent REAL",
            "by_category TEXT",
            "by_difficulty TEXT",
            "wrong_answers TEXT",
            "reflection TEXT",
            "timestamp TEXT"
        ])
    
    def insert_result(self, student_id: str, result: Dict):
        """插入训练结果"""
        self.db.insert("training_results", {
            "student_id": student_id,
            "day": result.get("day"),
            "problems_solved": result.get("problems_solved"),
            "problems_correct": result.get("problems_correct"),
            "accuracy": result.get("accuracy"),
            "time_spent": result.get("time_spent_minutes"),
            "by_category": json.dumps(result.get("by_category", {})),
            "by_difficulty": json.dumps(result.get("by_difficulty", {})),
            "wrong_answers": json.dumps(result.get("wrong_answers", [])),
            "reflection": result.get("summary", ""),
            "timestamp": datetime.now().isoformat()
        })
    
    def get_student_trend(self, student_id: str) -> List[Dict]:
        """获取学员趋势"""
        return self.db.query(
            "SELECT * FROM training_results WHERE student_id = ? ORDER BY day",
            (student_id,)
        )
    
    def get_weak_categories(self, student_id: str) -> Dict:
        """获取学员弱项分类"""
        results = self.get_student_trend(student_id)
        category_stats = {}
        
        for r in results:
            by_cat = json.loads(r["by_category"])
            for cat, stats in by_cat.items():
                if cat not in category_stats:
                    category_stats[cat] = {"solved": 0, "correct": 0}
                category_stats[cat]["solved"] += stats["solved"]
                category_stats[cat]["correct"] += stats["correct"]
        
        # 计算准确率并排序
        for cat in category_stats:
            stats = category_stats[cat]
            stats["accuracy"] = stats["correct"] / stats["solved"] if stats["solved"] > 0 else 0
        
        # 返回准确率最低的3个分类
        sorted_cats = sorted(category_stats.items(), key=lambda x: x[1]["accuracy"])
        return dict(sorted_cats[:3])
```

#### 优化2: 错题复习引擎

**现状**: 错题仅记录，无复习

**方案**: 基于Ebbinghaus遗忘曲线的错题复习系统

```python
class WrongAnswerReview:
    """错题复习引擎"""
    
    # Ebbinghaus遗忘曲线间隔 (小时)
    REVIEW_INTERVALS = [1, 4, 12, 24, 48, 96, 192]  # 1h, 4h, 12h, 1d, 2d, 4d, 8d
    
    def __init__(self):
        self.wrong_answers = {}  # {student_id: [{problem_id, first_wrong, review_count, next_review}]}
    
    def add_wrong_answer(self, student_id: str, problem: Dict):
        """添加错题"""
        if student_id not in self.wrong_answers:
            self.wrong_answers[student_id] = {}
        
        problem_id = problem["problem_id"]
        self.wrong_answers[student_id][problem_id] = {
            "problem": problem,
            "first_wrong": datetime.now(),
            "review_count": 0,
            "next_review": datetime.now() + timedelta(hours=self.REVIEW_INTERVALS[0]),
            "mastery": 0.0  # 掌握程度 0-1
        }
    
    def get_review_problems(self, student_id: str) -> List[Dict]:
        """获取需要复习的错题"""
        if student_id not in self.wrong_answers:
            return []
        
        now = datetime.now()
        review_problems = []
        
        for problem_id, data in self.wrong_answers[student_id].items():
            if now >= data["next_review"]:
                review_problems.append(data["problem"])
        
        return review_problems
    
    def record_review_result(self, student_id: str, problem_id: str, is_correct: bool):
        """记录复习结果"""
        if student_id not in self.wrong_answers:
            return
        
        if problem_id not in self.wrong_answers[student_id]:
            return
        
        data = self.wrong_answers[student_id][problem_id]
        data["review_count"] += 1
        
        if is_correct:
            # 正确: 掌握程度提升，延长复习间隔
            data["mastery"] = min(1.0, data["mastery"] + 0.2)
            next_interval_idx = min(data["review_count"], len(self.REVIEW_INTERVALS) - 1)
            data["next_review"] = datetime.now() + timedelta(
                hours=self.REVIEW_INTERVALS[next_interval_idx]
            )
        else:
            # 错误: 掌握程度降低，缩短复习间隔
            data["mastery"] = max(0.0, data["mastery"] - 0.1)
            data["next_review"] = datetime.now() + timedelta(
                hours=self.REVIEW_INTERVALS[max(0, data["review_count"] - 1)]
            )
        
        # 掌握程度达到1.0时标记为已掌握
        if data["mastery"] >= 1.0:
            data["status"] = "mastered"
```

#### 优化3: 渐进式难度调节器

**现状**: 难度跳跃大 (初级→中级陡降22%)

**方案**: 动态难度调节 (类似ELO评级)

```python
class AdaptiveDifficulty:
    """渐进式难度调节器"""
    
    def __init__(self):
        self.student_levels = {}  # {student_id: current_level}
        self.difficulty_thresholds = {
            "入门": (0, 0.8),      # 准确率<80%时降级
            "初级": (0.75, 0.9),   # 准确率75-90%保持，>90%升级
            "中级": (0.8, 0.92),   # 准确率80-92%保持
            "高级": (0.85, 1.0)    # 准确率85%+保持
        }
    
    def adjust_level(self, student_id: str, accuracy: float, category: str = None) -> str:
        """根据准确率调整难度"""
        current_level = self.student_levels.get(student_id, "入门")
        
        thresholds = self.difficulty_thresholds[current_level]
        
        if accuracy < thresholds[0]:
            # 降级
            new_level = self._downgrade(current_level)
        elif accuracy > thresholds[1]:
            # 升级
            new_level = self._upgrade(current_level)
        else:
            new_level = current_level
        
        self.student_levels[student_id] = new_level
        return new_level
    
    def generate_problem_set(self, student_id: str, target_count: int = 50) -> List[Dict]:
        """生成题目集 (渐进式)"""
        current_level = self.student_levels.get(student_id, "入门")
        
        # 题目分布: 60%当前难度 + 20%低一级 + 20%高一级
        distribution = {
            current_level: int(target_count * 0.6),
            self._downgrade(current_level): int(target_count * 0.2),
            self._upgrade(current_level): int(target_count * 0.2)
        }
        
        # 从题库中按分布选题
        problems = []
        for level, count in distribution.items():
            if level and count > 0:
                problems.extend(self._select_problems(level, count))
        
        return problems[:target_count]
```

### 2.2 通信优化

#### 优化4: WebSocket实时通道

**现状**: SSH+GitHub，延迟分钟级

**方案**: 部署WebSocket服务器

```python
# websocket_server.py
import asyncio
import websockets
import json

class TrainingWebSocketServer:
    """训练WebSocket服务器"""
    
    def __init__(self, port=8199):
        self.port = port
        self.clients = {}  # {student_id: websocket}
        self.training_tasks = {}  # {student_id: current_task}
    
    async def register(self, websocket, path):
        """学员注册"""
        student_id = path.strip('/')
        self.clients[student_id] = websocket
        print(f"✅ {student_id} 已连接")
        
        # 发送当前任务
        if student_id in self.training_tasks:
            await websocket.send(json.dumps({
                "type": "task",
                "data": self.training_tasks[student_id]
            }))
        
        try:
            async for message in websocket:
                await self.handle_message(student_id, message)
        except websockets.exceptions.ConnectionClosed:
            del self.clients[student_id]
            print(f"❌ {student_id} 已断开")
    
    async def handle_message(self, student_id: str, message: str):
        """处理消息"""
        data = json.loads(message)
        
        if data["type"] == "result":
            # 接收训练结果
            await self.broadcast_to_coach({
                "type": "training_result",
                "student_id": student_id,
                "data": data["data"]
            })
        
        elif data["type"] == "heartbeat":
            # 心跳响应
            await self.clients[student_id].send(json.dumps({
                "type": "heartbeat_ack",
                "timestamp": datetime.now().isoformat()
            }))
    
    async def broadcast_to_coach(self, message: Dict):
        """广播给教练"""
        if "coach" in self.clients:
            await self.clients["coach"].send(json.dumps(message))
    
    async def send_task(self, student_id: str, task: Dict):
        """发送任务"""
        self.training_tasks[student_id] = task
        if student_id in self.clients:
            await self.clients[student_id].send(json.dumps({
                "type": "task",
                "data": task
            }))
```

#### 优化5: 消息队列持久化

**现状**: 文件散落在outbox/from-{name}/

**方案**: Redis消息队列

```python
import redis

class MessageQueue:
    """消息队列"""
    
    def __init__(self, host='localhost', port=6379):
        self.redis = redis.Redis(host=host, port=port, db=0)
    
    def push(self, student_id: str, message: Dict):
        """推送消息"""
        self.redis.lpush(
            f"queue:{student_id}:inbox",
            json.dumps(message)
        )
    
    def pop(self, student_id: str) -> Optional[Dict]:
        """拉取消息"""
        data = self.redis.rpop(f"queue:{student_id}:inbox")
        if data:
            return json.loads(data)
        return None
    
    def get_count(self, student_id: str) -> int:
        """获取消息数量"""
        return self.redis.llen(f"queue:{student_id}:inbox")
```

### 2.3 自动化优化

#### 优化6: 智能调度引擎

**现状**: 教练手动调度

**方案**: 基于状态的自动调度

```python
class SmartScheduler:
    """智能调度引擎"""
    
    def __init__(self):
        self.db = TrainingDatabase()
        self.difficulty = AdaptiveDifficulty()
        self.review = WrongAnswerReview()
    
    def generate_day_task(self, student_id: str, day: int) -> Dict:
        """生成每日任务"""
        # 1. 获取学员状态
        trend = self.db.get_student_trend(student_id)
        weak_cats = self.db.get_weak_categories(student_id)
        
        # 2. 获取需要复习的错题
        review_problems = self.review.get_review_problems(student_id)
        
        # 3. 生成新题目 (渐进式)
        new_problems = self.difficulty.generate_problem_set(
            student_id,
            target_count=50
        )
        
        # 4. 组合题目 (复习30% + 新题70%)
        total_problems = review_problems[:15] + new_problems[:35]
        
        # 5. 生成对局任务
        games = self._generate_games(student_id, day)
        
        task = {
            "student_id": student_id,
            "day": day,
            "problems": total_problems,
            "games": games,
            "focus": list(weak_cats.keys())[:2] if weak_cats else [],
            "review_count": len(review_problems),
            "new_count": len(new_problems)
        }
        
        return task
```

---

## 三、围棋训练计划更新 (Day4-Day7)

### 3.1 Day4: 官子专项训练

**目标**: 提升官子计算准确率 (78% → 85%)

| 学员 | 题目 | 对局 | 专项 | 配对 |
|------|------|------|------|------|
| qoder | 80 | 8 | 官子计算+先手/后手辨析 | zhuguxia |
| xiaochen | 60 | 6 | 官子顺序+目数计算 | 教练 |
| zhuguxia | 80 | 8 | 官子计算+终局判断 | qoder |
| xiaowei | 50 | 4 | 基础官子+连接 | 教练 |

**题目分布**:
- 官子: 50% (40题)
- 死活: 20% (16题)
- 手筋: 20% (16题)
- 布局: 10% (8题)

**新增**: 错题复习 (每人10题)

### 3.2 Day5: 死活强化训练

**目标**: 提升死活题准确率 (80% → 88%)

| 学员 | 题目 | 对局 | 专项 | 配对 |
|------|------|------|------|------|
| qoder | 100 | 10 | 复杂死活+劫争 | zhuguxia |
| xiaochen | 80 | 8 | 盘角曲四+劫尽棋亡 | 教练 |
| zhuguxia | 100 | 10 | 复杂死活+双活 | qoder |
| xiaowei | 60 | 6 | 基础死活+眼位 | 教练 |

**题目分布**:
- 死活: 50% (50题)
- 官子: 20% (20题)
- 手筋: 20% (20题)
- 布局: 10% (10题)

**新增**: 错题复习 (每人15题)

### 3.3 Day6: 布局与中盘训练

**目标**: 提升布局理论 (67% → 80%)

| 学员 | 题目 | 对局 | 专项 | 配对 |
|------|------|------|------|------|
| qoder | 100 | 10 | 中国流+小林流 | zhuguxia |
| xiaochen | 80 | 8 | 中国流应对+侵入 | 教练 |
| zhuguxia | 100 | 10 | 星位+小目布局 | qoder |
| xiaowei | 60 | 6 | 基础布局+定式 | 教练 |

**题目分布**:
- 布局: 40% (40题)
- 中盘: 30% (30题)
- 死活: 15% (15题)
- 官子: 15% (15题)

**新增**: 错题复习 (每人20题)

### 3.4 Day7: 综合考核与对抗赛

**目标**: 全面评估7天训练成果

| 学员 | 题目 | 对局 | 专项 | 配对 |
|------|------|------|------|------|
| qoder | 120 | 12 | 综合考核+对抗赛 | 全员 |
| xiaochen | 100 | 10 | 综合考核+对抗赛 | 全员 |
| zhuguxia | 120 | 12 | 综合考核+对抗赛 | 全员 |
| xiaowei | 80 | 8 | 基础考核+对抗赛 | 全员 |

**题目分布**:
- 综合: 100% (随机抽取)

**对抗赛**:
- 循环赛: 每人vs每人 (3局)
- 计时赛: 每题限时60秒
- 积分制: 胜+3分，平+1分，负0分

---

## 四、实施路线图

### Phase 1: 基础优化 (Day4-Day5)

| 项目 | 时间 | 负责人 | 状态 |
|------|------|--------|------|
| 训练数据库 | Day4上午 | 诸葛马 | 🔲 |
| 错题复习引擎 | Day4下午 | 诸葛马 | 🔲 |
| 渐进式难度调节 | Day5上午 | 诸葛马 | 🔲 |
| Day4官子训练 | Day4全天 | 全体学员 | 🔲 |

### Phase 2: 通信优化 (Day5-Day6)

| 项目 | 时间 | 负责人 | 状态 |
|------|------|--------|------|
| WebSocket服务器 | Day5下午 | 诸葛马 | 🔲 |
| 消息队列持久化 | Day6上午 | 诸葛马 | 🔲 |
| Day5死活训练 | Day5全天 | 全体学员 | 🔲 |
| Day6布局训练 | Day6全天 | 全体学员 | 🔲 |

### Phase 3: 自动化优化 (Day6-Day7)

| 项目 | 时间 | 负责人 | 状态 |
|------|------|--------|------|
| 智能调度引擎 | Day6下午 | 诸葛马 | 🔲 |
| 可视化监控面板 | Day7上午 | 诸葛马 | 🔲 |
| Day7综合考核 | Day7全天 | 全体学员 | 🔲 |
| 对抗赛 | Day7下午 | 全体学员 | 🔲 |

---

## 五、预期效果

### 5.1 训练效果

| 指标 | 当前值 | Day7目标 | 提升 |
|------|--------|----------|------|
| 官子准确率 | 78% | 85% | +7% |
| 死活准确率 | 80% | 88% | +8% |
| 布局准确率 | 67% | 80% | +13% |
| 中级题准确率 | 67% | 78% | +11% |
| 错题复习率 | 0% | 100% | +100% |
| 提交率 | 0% | 95% | +95% |

### 5.2 系统效果

| 指标 | 当前值 | Day7目标 | 提升 |
|------|--------|----------|------|
| 通信延迟 | 分钟级 | 秒级 | 60x |
| 自动化率 | 20% | 70% | +50% |
| 搜索准确率 | 50% | 85% | +35% |
| 监控覆盖率 | 0% | 100% | +100% |

---

## 六、风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| WebSocket连接不稳定 | 中 | 保留SSH降级通道 |
| 学员训练疲劳 | 高 | 增加游戏化元素，减少每日题量 |
| 难度调节过度 | 中 | 人工审核难度调整 |
| 错题复习负担 | 中 | 控制复习题量≤20题/天 |

---

## 七、总结

### 7.1 核心改进

1. **训练数据持久化**: SQLite数据库统一存储
2. **错题复习闭环**: Ebbinghaus遗忘曲线驱动
3. **渐进式难度**: 动态调节，避免陡降
4. **WebSocket实时通信**: 延迟从分钟级降至秒级
5. **智能调度**: 自动任务生成，减少人工干预

### 7.2 训练计划更新

- **Day4**: 官子专项 (78% → 85%)
- **Day5**: 死活强化 (80% → 88%)
- **Day6**: 布局中盘 (67% → 80%)
- **Day7**: 综合考核+对抗赛

### 7.3 预期成果

- ✅ 7天后学员等级提升5-10级
- ✅ 所有短板分类准确率提升≥7%
- ✅ 错题复习率100%
- ✅ 提交率≥95%
- ✅ 自动化率≥70%

---

**作者**: 诸葛马 (AI教练)  
**日期**: 2026年6月28日  
**版本**: V3.1  
**状态**: ✅ 已部署
