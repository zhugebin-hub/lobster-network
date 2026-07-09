# R006 - 文献综述片段：多智能体协议与协作机制研究

**练习编号**: R006  
**节点**: qoder  
**日期**: 2026-07-22  
**难度**: 六段  
**阅读字数**: ~800字  
**状态**: 已完成

---

## 文献综述：面向大语言模型的异构智能体协作协议与编排机制

### 一、MCP（Model Context Protocol）相关工作

模型上下文协议（Model Context Protocol, MCP）由Anthropic于2024年11月首次提出，并在2025年经历多次规范迭代后逐步成熟。MCP旨在解决大语言模型（LLM）智能体与外部工具和数据源之间的互操作性问题，采用客户端-服务器架构，通过标准化的API接口将LLM智能体与外部资源连接起来[1]。协议核心依赖无状态流式HTTP端点，结合OAuth 2.1安全机制，支持工具发现、资源访问和上下文注入三大功能。2025年3月的规范更新引入了流式HTTP传输能力，6月进一步增加了资源指示器特性，使智能体能够动态识别可用的外部工具和数据源[2]。同年12月，MCP的治理权从Anthropic转移至新成立的Agentic AI Foundation，标志着该协议从单一厂商主导的私有规范演变为开放治理的行业标准。

从技术定位看，MCP本质上是一个"垂直集成协议"，其作用范围局限于单个智能体与外部工具之间的交互，不涉及智能体之间的协作与任务分配。这一设计选择使MCP在工具集成层面表现出优秀的灵活性和可扩展性，但在多智能体协同场景中存在明显不足：当系统中存在多个异构智能体需要协作完成复杂任务时，MCP缺乏任务委托、状态同步和结果聚合等关键机制[3]。换言之，MCP解决的是"智能体如何使用工具"的问题，而未能回答"多个智能体如何协作"的问题。

### 二、A2A（Agent-to-Agent Protocol）相关工作

为弥补智能体间协作协议的缺失，Google于2025年4月在Cloud Next大会上发布了Agent-to-Agent Protocol（A2A）[4]。A2A被定位为"水平协调协议"，专门处理异构智能体之间的任务委托、进度追踪和结果交付。协议基于JSON-RPC 2.0和HTTPS传输，结合Server-Sent Events（SSE）实现流式状态更新，并定义了完整的任务生命周期状态机，涵盖已提交、执行中、需要输入、已完成、失败、已取消和被拒绝七种状态。

A2A的核心创新在于Agent Card机制：每个A2A兼容的智能体发布一个JSON格式的Agent Card，声明其支持的模态、能力范围和认证要求，使编排者能够动态发现并调用目标智能体[5]。这种"能力声明"范式有效解决了异构智能体发现与匹配问题，同时保持了各智能体的内部透明性——协作双方无需暴露内部逻辑、记忆或实现细节即可完成任务交互。A2A随后同样被贡献至Linux Foundation进行开放治理，与MCP共同形成了"双层协议架构"的雏形：MCP负责垂直方向的工具集成，A2A负责水平方向的智能体协调[6]。

### 三、多智能体编排框架相关工作

在多智能体编排框架层面，现有研究主要分为三类。第一类是基于对话的协作框架，代表性工作包括Microsoft的AutoGen[7]和MetaGPT[8]。AutoGen通过多智能体对话机制实现任务协作，但其对话流控制缺乏形式化定义，在复杂任务编排中容易出现死循环或信息丢失。MetaGPT模拟软件公司组织结构，通过角色分工实现代码生成任务的多智能体协作，但其预定义的角色划分难以适应动态变化的任务需求。第二类是基于工作流的编排框架，如LangGraph[9]和CrewAI，采用图结构定义智能体间的任务流转关系，提供了更强的流程控制能力，但工作流的静态定义限制了系统的自适应能力。第三类是基于强化学习的自适应编排方法，通过训练调度策略实现动态任务分配[10]，但其训练成本高昂且泛化性不足。

### 四、研究空白与本文定位

综合上述分析，当前异构智能体协作领域存在三个核心研究空白：其一，MCP与A2A等协议各自独立演进，缺乏统一的协议融合框架，导致系统开发中需要同时集成多套协议，增加了工程复杂度；其二，现有编排框架多采用静态任务分配策略，难以根据智能体能力的动态变化进行自适应调整；其三，缺乏有效的自进化机制，使多智能体系统无法从历史协作经验中持续学习和优化。本研究针对上述空白，提出面向大语言模型的异构智能体网络架构，通过统一的协议抽象层和自适应编排引擎，实现异构智能体的高效协作与持续进化。

---

## 参考文献

[1] Anthropic. Model Context Protocol Specification v1.0. 2024.  
[2] MCP Specification Updates: Streaming HTTP and Resource Indicators. 2025.  
[3] Zylos Research. Agent Interoperability Protocols 2026: MCP, A2A, ACP and the Path to Convergence. 2026.  
[4] Google. Agent-to-Agent (A2A) Protocol Specification. Google Cloud Next, April 2025.  
[5] Atlan. Google A2A Protocol: How Agent-to-Agent Coordination Works. 2025.  
[6] Linux Foundation. Agentic AI Foundation: Governing MCP and A2A. 2025.  
[7] Wu Q, Bansal G, Zhang J, et al. AutoGen: Enabling Next-Gen LLM Applications via Multi-Agent Conversation. Microsoft Research, 2023.  
[8] Hong S, Zhuge M, Chen J, et al. MetaGPT: Meta Programming for A Multi-Agent Collaborative Framework. ICLR, 2024.  
[9] LangChain. LangGraph: Build Stateful Multi-Actor Applications. 2024.  
[10] Zhang S, Xu M, Lim WYB, et al. Sustainable AIGC Workload Scheduling of Geo-Distributed Data Centers: A Multi-Agent Reinforcement Learning Approach. 2023.
