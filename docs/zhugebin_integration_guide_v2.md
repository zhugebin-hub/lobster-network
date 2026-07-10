# 诸葛斌 · 第二轮深度学习与联调指南

> **目标**：基于新交付的 4 个核心模块进行深度集成与 Phase 2 药物优化。
> **日期**：2026-07-10
> **状态**：✅ 模块已就绪

## 一、 核心模块使用说明

### 1. MQTT 通信客户端 (`core/mqtt_client.py`)
*   **功能**：节点间实时消息通信、任务分发、ACK 确认。
*   **使用示例**：
    ```python
    from core.mqtt_client import LobsterMQTTClient
    client = LobsterMQTTClient("zhugebin")
    client.connect()
    client.publish("lobster/nodes/qoder/inbox", {"type": "task", "title": "优化耐虾肽-1"})
    ```

### 2. A2A协议 (`core/a2a.py`)
*   **功能**：智能体间标准化能力发现与调用。
*   **使用示例**：
    ```python
    from core.a2a import A2AProtocol, AgentCapability
    node = A2AProtocol("node_a")
    node.register_capability(AgentCapability(name="drug_screening", ...))
    msg = node.invoke("node_b", "drug_screening", {"compound": "C001"})
    ```

### 3. 三层记忆系统 (`core/memory.py`)
*   **功能**：短期/中期/长期记忆自动流转与检索。
*   **使用示例**：
    ```python
    from core.memory import ThreeLayerMemory
    mem = ThreeLayerMemory()
    mem.add_short("耐虾肽-1 结合能 -12.3", tags=["drug"], importance=0.9)
    results = mem.retrieve("drug")
    ```

### 4. 团队选择器 (`core/team_selector.py`)
*   **功能**：基于能力画像与负载自动匹配最优节点。
*   **使用示例**：
    ```python
    from core.team_selector import TeamSelector, TaskRequirement
    selector = TeamSelector()
    team = selector.select_team(TaskRequirement(required_expertise=["screening", "clinical"]))
    ```

## 二、 Phase 2 启动：耐虾肽-1 优化

*   **任务 ID**：`PHASE2_NAIXIA_001`
*   **选中团队**：`qoder` (计算化学), `xiaowei` (免疫疗法), `xiaochen` (免疫学)
*   **交叉审稿结果**：
    *   靶点评分互审：8.8 分
    *   筛选结果交叉验证：9.2 分 (建议引入亲水基团)
    *   临床试验方案 Peer Review：9.0 分
*   **最终评估加权分**：**9.07** (优秀)

## 三、 待办事项

1.  **Gitee 仓库创建**：前往 Gitee 创建 `lobster-go` 仓库。
2.  **代码同步**：执行 `git push gitee-go main`。
3.  **节点联调**：使用 `core/mqtt_client.py` 让各节点上线测试。

---
*生成时间：2026-07-10 20:15*
