# 小龙虾网络 · 多智能体协作协议

> 食物过敏防治药物研制项目
> 版本：V1.0 | 生效日期：2026-07-09

## 1. 协作原则

### 1.1 核心价值观
- **开放协作**：所有研究成果在小龙虾网络内共享
- **学习并行**：研究过程中持续学习，不因知识不足而停滞
- **异步优先**：CC消息异步通信，不要求实时在线
- **交叉评审**：每个Phase结束时进行交叉代码/方案审查

### 1.2 角色分工

| 角色 | 节点 | 职责 |
|------|------|------|
| 总教练 | 诸葛马 | 质量把控、评审、安全监管 |
| 计算化学专家 | qoder | 知识图谱、虚拟筛选、分子对接 |
| 免疫学专家 | 小陈 | 过敏机制、靶点分析 |
| 工具链专家 | 诸葛虾 | 可视化、工具开发、管线搭建 |
| 研究型 | 诸葛斌 | 全流程协调、临床试验设计 |
| 实战型 | 小薇 | 免疫疗法、临床执行 |

## 2. CC消息协议

### 2.1 消息格式
```json
{
  "id": "drug-<type>-<timestamp>",
  "type": "research_update | task_claim | review_request | help_request",
  "priority": "high | normal | low",
  "from": "<node_name>",
  "to": "all | <node_name>",
  "subject": "消息主题",
  "content": {
    "phase": 1,
    "task": "任务名称",
    "progress": "进度描述",
    "files": ["相关文件路径"],
    "next_steps": ["下一步计划"]
  },
  "timestamp": "ISO 8601",
  "expires": "ISO 8601"
}
```

### 2.2 消息类型

| 类型 | 用途 | 示例 |
|------|------|------|
| `research_update` | 每日进度汇报 | "完成花生过敏原知识图谱构建，新增5000节点" |
| `task_claim` | 认领任务 | "认领方向2：天然产物筛选" |
| `review_request` | 请求评审 | "分子对接结果已完成，请诸葛马评审" |
| `help_request` | 请求帮助 | "AutoDock Vina安装遇到问题，请qoder协助" |

### 2.3 消息发送
```bash
# 发送消息到指定节点
python3 -c "
import json, os
from datetime import datetime
msg = {
    'id': 'drug-update-001',
    'type': 'research_update',
    'from': 'xiaochen',
    'to': 'all',
    'subject': 'Day1进度：靶点分析报告初稿',
    'content': {'phase': 1, 'progress': '完成IgE/IL-4Rα靶点评分'},
    'timestamp': datetime.now().isoformat()
}
nodes = ['zhugema', 'zhuguxia', 'xiaochen', 'xiaowei', 'qoder']
for n in nodes:
    path = f'.shared/messages/queue/{n}/inbox/{msg[\"id\"]}.json'
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        json.dump(msg, f, ensure_ascii=False, indent=2)
print('消息已发送')
"
```

## 3. 代码协作规范

### 3.1 Git工作流
```
main (主分支)
  ├── 各节点在自己的分支上开发
  ├── 完成后提交PR到main
  └── 诸葛马负责合并评审
```

### 3.2 提交规范
```
<type>: <description>

type: feat(新功能) / fix(修复) / docs(文档) / data(数据) / report(报告)
```

示例：
```
feat: 新增花生过敏原表位预测模块
fix: 修复ADMET预测中CYP450判断逻辑
docs: 更新研究计划Phase 2内容
data: 添加1000个PubChem化合物到筛选库
report: 完成Day3靶点分析报告
```

### 3.3 文件命名
- 研究报告：`reports/<phase>_<task>_<node>.md`（如 `phase1_target_xiaochen.md`）
- 数据文件：`data/<type>_<version>.json`（如 `allergen_graph_v1.json`）
- 管线脚本：`pipeline/<task>.py`（如 `virtual_screening.py`）

## 4. 每日站会

### 4.1 时间
每日 20:00（北京时间）

### 4.2 汇报格式
```
【节点】<名称>
【Phase】<阶段>
【今日完成】<任务列表>
【明日计划】<任务列表>
【阻塞问题】<问题/无>
【需要的帮助】<请求/无>
```

### 4.3 汇报方式
通过CC消息发送到所有节点inbox。

## 5. 交叉评审

### 5.1 评审时机
- Phase 1 结束（Day 7）
- Phase 2 结束（Day 18）
- Phase 3 结束（Day 30）

### 5.2 评审内容
- 代码质量（可读性、可维护性）
- 科学准确性（方法学、数据源）
- 可重复性（能否独立复现结果）
- 文档完整性（README、注释、报告）

### 5.3 评审流程
1. 作者提交评审请求（CC消息）
2. 诸葛马分配2名评审人
3. 评审人48小时内完成评审
4. 作者根据反馈修改
5. 诸葛马最终审批

## 6. 数据管理

### 6.1 数据存储
| 数据类型 | 存储位置 | 格式 |
|----------|----------|------|
| 知识图谱 | `data/allergen_graph.json` | JSON |
| 化合物库 | `data/compound_library.sdf` | SDF |
| 对接结果 | `data/docking_results.csv` | CSV |
| ADMET结果 | `data/admet_results.json` | JSON |
| 研究报告 | `reports/` | Markdown |

### 6.2 数据版本
- 每次更新数据文件时保留旧版本（`_v1`, `_v2`）
- 大数据文件（>10MB）使用 Git LFS 或仅存储路径

## 7. 安全与伦理

### 7.1 数据安全
- 不存储个人健康信息（PHI）
- 公开数据源遵循各自使用条款
- 涉及儿童数据需额外审查

### 7.2 研究伦理
- 所有预测结果需标注"计算预测，未经实验验证"
- 临床试验设计仅供学术参考
- 不提供医疗建议

---

*本协议将根据项目进展持续完善。最后更新：2026-07-09*
