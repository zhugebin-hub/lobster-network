# 第 3 章 系统设计与实现 (System Design and Implementation)

## 3.1 系统架构概述

### 3.1.1 整体架构

本系统采用分层架构设计，自下而上分为四个层次：

```
┌─────────────────────────────────────────────────────────┐
│                    应用层 (Application)                   │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │  任务管理   │ │  UI 显示    │ │   数据记录与导出    │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
─────────────────────────────────────────────────────────┤
│                    逻辑层 (Logic)                        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │ 投影算法    │ │ 碰撞检测    │ │   任务状态机        │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
─────────────────────────────────────────────────────────┤
│                    接口层 (Interface)                    │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │  XR 输入    │ │  UI 系统    │ │   文件系统          │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
├─────────────────────────────────────────────────────────┤
│                    硬件层 (Hardware)                     │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────┐ │
│  │  VR HMD    │ │ 手柄控制器 │ │   Pico Tracker      │ │
│  └─────────────┘ └─────────────┘ └─────────────────────┘ │
─────────────────────────────────────────────────────────┘
```

### 3.1.2 核心模块

系统核心模块包括：

1. **ProjectionSystem**：主控制脚本，协调所有子系统
2. **InputManager**：XR 输入处理，读取手柄按键和追踪数据
3. **ProjectionCanvas**：3D-2D 坐标投影和 UI 渲染
4. **TaskManager**：任务状态机，管理任务启动、执行和结束
5. **DataLogger**：数据采集和文件导出

### 3.1.3 数据流

```
VR 设备追踪数据 → InputDevice.GetFeatureValue()
                    ↓
         世界坐标 (Vector3)
                    ↓
    planeTransform.InverseTransformPoint()
                    ↓
         局部坐标 (Vector3)
                    ↓
         线性映射到 Canvas
                    ↓
         UI 坐标 (Vector2)
                    ↓
    碰撞检测 + 任务判定
                    ↓
         结果输出 + 数据记录
```

---

## 3.2 硬件选型与配置

### 3.2.1 VR 头戴显示器

**设备型号**：Pico 4 Enterprise

| 参数 | 规格 |
|------|------|
| 分辨率 | 2160×2160 像素/眼 |
| 刷新率 | 90Hz / 120Hz |
| 视场角 | 105° |
| 追踪类型 | Inside-Out 光学追踪 |
| 自由度 | 6DOF |
| 重量 | 295g |

**选型理由**：
- 高分辨率确保 UI 元素清晰可见
- 90Hz 刷新率满足低延迟要求
- Inside-Out 追踪无需外部基站，部署简单
- 企业版支持开发者模式和数据导出

### 3.2.2 控制器

**设备型号**：Pico Motion Controller

| 参数 | 规格 |
|------|------|
| 追踪自由度 | 6DOF |
| 按键数量 | 7 个（摇杆×2, 按键×5） |
| 触觉反馈 | 线性马达 |
| 电池续航 | 约 40 小时 |
| 连接方式 | 蓝牙 5.0 |

**按键映射**：
- 右手 A 键（Primary）：启动任务 1
- 右手 B 键（Secondary）：启动任务 2
- 左手 X 键（Primary）：启动任务 3
- 左手 Y 键（Secondary）：启动任务 4
- 左手 X + 右手 A 同时：启动任务 5
- 左手 Y + 右手 B 同时：启动任务 6

### 3.2.3 第三方追踪器

**设备型号**：Pico Tracker

| 参数 | 规格 |
|------|------|
| 追踪自由度 | 6DOF |
| 刷新率 | 1000Hz |
| 延迟 | <20ms |
| 重量 | 35g |
| 尺寸 | 50×40×25mm |

**用途**：作为额外追踪目标，模拟康复训练中的肢体标记点。

### 3.2.4 开发主机

| 组件 | 配置 |
|------|------|
| CPU | Intel Core i7-12700K |
| GPU | NVIDIA RTX 3070 |
| 内存 | 32GB DDR4 |
| 存储 | 1TB NVMe SSD |
| 操作系统 | Windows 11 Pro |

---

## 3.3 Unity 场景结构设计

### 3.3.1 Hierarchy 结构

根据提供的 Unity Hierarchy 截图，场景结构如下：

```
SampleScene
├── Directional Light              # 平行光源
├── XR Interaction Manager         # XR 交互管理器
├── XR Origin (VR)                 # XR 原点
│   └── Camera Offset
│       ├── Main Camera            # 主相机
│       ├── Left Controller        # 左手柄
│       │   └── Sphere_Left        # 左手追踪球
│       ├── Right Controller       # 右手柄
│       │   └── Sphere_Right       # 右手追踪球
│       └── Pico Tracker           # 第三方追踪器
│           └── Sphere_Tracker     # 追踪器球体
├── Input Manager                  # 输入管理
├── Global Volume                  # 全局体积光
├── EventSystem                  # UI 事件系统
└── ProjectionPlaneRoot            # 投影平面根节点
    ├── PlaneVisual                # 平面可视化
    └── ProjectionCanvas           # 投影画布
        ├── TargetsContainer       # 目标体容器
        ├── RedDot                 # 红色投影点
        ├── YellowDot              # 黄色投影点
        ├── BlueDot                # 蓝色投影点
        ├── WhiteDot               # 白色投影点（中点/重心）
        ├── TimerText              # 计时器文本
        └── ResultText             # 结果文本
```

### 3.3.2 关键组件配置

**XR Origin (VR)**：
- Tracking Origin Mode: Floor
- Requested Features: Motion Controllers, Hand Tracking

**Main Camera**：
- Clear Flags: Solid Color
- Culling Mask: Everything
- Projection: Perspective
- Field of View: 90°

**ProjectionCanvas**：
- Render Mode: Screen Space - Camera
- Canvas Scaler: Scale With Screen Size
- Reference Resolution: 1920×1080
- Match: 0.5 (宽高均衡)

**RectTransform 配置**：
- RedDot/YellowDot/BlueDot: 20×20 像素圆形 Image
- WhiteDot: 24×24 像素圆形 Image（略大以突出显示）
- TargetsContainer: 容纳动态生成的目标体

### 3.3.3 材质与着色器

**投影平面材质**：
```shader
Shader "Custom/ProjectionPlane" {
    Properties {
        _Color ("Plane Color", Color) = (0.1, 0.1, 0.15, 0.8)
        _GridSpacing ("Grid Spacing", Float) = 0.1
        _GridColor ("Grid Color", Color) = (0.3, 0.3, 0.4, 0.5)
    }
    SubShader {
        Tags { "RenderType"="Transparent" "Queue"="Transparent" }
        LOD 100
        // ... 网格绘制逻辑
    }
}
```

**目标体材质**：
- 颜色：绿色 (0, 1, 0)
- 形状：正方形边框
- 尺寸：40×40 像素
- 透明度：0.7

---

## 3.4 核心算法实现

### 3.4.1 3D-2D 坐标投影算法

**算法原理**：

将世界空间中的追踪点坐标投影到 Canvas 二维平面，采用正交投影变换：

```csharp
void ProjectToCanvas(Transform sphere, RectTransform dot)
{
    if (sphere == null || dot == null) return;

    // 步骤 1: 世界坐标 → 局部坐标
    Vector3 local = planeTransform.InverseTransformPoint(sphere.position);

    // 步骤 2: 获取 Canvas 尺寸
    float halfCW = canvasRect.rect.width * 0.5f;
    float halfCH = canvasRect.rect.height * 0.5f;

    // 步骤 3: 线性映射（考虑平面世界尺寸）
    float cx = (local.x / (planeWorldWidth * 0.5f)) * halfCW;
    float cy = (local.y / (planeWorldHeight * 0.5f)) * halfCH;

    // 步骤 4: 边界裁剪
    dot.anchoredPosition = new Vector2(
        Mathf.Clamp(cx, -halfCW, halfCW),
        Mathf.Clamp(cy, -halfCH, halfCH));
}
```

**数学推导**：

设世界空间中点 P_world = (x_w, y_w, z_w)，投影平面尺寸为 (W_plane, H_plane)，Canvas 尺寸为 (W_canvas, H_canvas)。

局部坐标计算：
```
P_local = planeTransform⁻¹ × P_world
```

Canvas 坐标计算：
```
u = (x_local / (W_plane/2)) × (W_canvas/2)
v = (y_local / (H_plane/2)) × (H_canvas/2)
```

边界处理：
```
u_clamped = clamp(u, -W_canvas/2, W_canvas/2)
v_clamped = clamp(v, -H_canvas/2, H_canvas/2)
```

**性能优化**：
- 缓存 Canvas 尺寸，避免每帧重复计算
- 使用 `RectTransform.anchoredPosition` 直接设置，避免布局重建
- 空引用检查前置，减少无效计算

### 3.4.2 碰撞检测与匹配算法

**问题定义**：

给定 N 个执行点（Dots）和 M 个目标体（Targets），判断是否存在一种匹配方案，使得每个执行点都能与一个不同的目标体在阈值距离内匹配。

**算法实现**：

采用贪心匹配策略（简化版匈牙利算法）：

```csharp
bool CheckDotsOnTargets(RectTransform[] dots, int required)
{
    if (spawnedTargets.Count < required) return false;

    bool[] used = new bool[spawnedTargets.Count];
    int matched = 0;

    foreach (var dot in dots)
    {
        if (dot == null || !dot.gameObject.activeInHierarchy) continue;

        for (int t = 0; t < spawnedTargets.Count; t++)
        {
            if (used[t]) continue;
            if (spawnedTargets[t] == null) continue;

            float dist = Vector2.Distance(
                dot.anchoredPosition,
                spawnedTargets[t].anchoredPosition);

            if (dist <= hitThreshold)  // hitThreshold = 30px
            {
                used[t] = true;
                matched++;
                break;  // 贪心：找到第一个匹配即停止
            }
        }
    }

    return matched >= required;
}
```

**算法复杂度**：
- 时间复杂度：O(N × M)，其中 N 为执行点数，M 为目标体数
- 空间复杂度：O(M)，用于标记已使用目标体

**优化空间**：
- 当前实现为贪心算法，可能不是最优匹配
- 如需最优解，可采用完整匈牙利算法（Kuhn-Munkres），复杂度 O(N³)
- 对于本应用（N≤3），贪心算法已足够

### 3.4.3 动态连线绘制算法

**功能需求**：

在任务 3、5、6 中，需要在两个投影点之间绘制动态连线，并满足以下要求：
- 连线始终连接两点中点
- 连线方向随两点位置变化而旋转
- 连线粗细随距离变化（距离越近越粗）
- 长度变化超过 15% 时判定失败

**实现代码**：

```csharp
void UpdateLine(ref GameObject lineObj, RectTransform from, RectTransform to)
{
    if (linePrefab == null || targetsContainer == null) return;

    // 延迟初始化
    if (lineObj == null)
        lineObj = Instantiate(linePrefab, targetsContainer);

    lineObj.transform.SetAsFirstSibling();  // 渲染在目标体下方

    RectTransform rt = lineObj.GetComponent<RectTransform>();
    Image img = lineObj.GetComponent<Image>();

    Vector2 fromPos = from.anchoredPosition;
    Vector2 toPos = to.anchoredPosition;
    Vector2 dir = toPos - fromPos;
    float dist = dir.magnitude;

    // 位置：两点中点
    rt.anchoredPosition = (fromPos + toPos) * 0.5f;

    // 旋转：朝向 toPos 方向
    rt.localRotation = Quaternion.Euler(
        0f, 0f, Mathf.Atan2(dir.y, dir.x) * Mathf.Rad2Deg);

    // 尺寸：宽度=距离，高度=粗细（距离越近越粗）
    float thickness = Mathf.Lerp(30f, 4f, Mathf.Clamp01(dist / 500f));
    rt.sizeDelta = new Vector2(dist, thickness);

    // 颜色：半透明白色
    if (img != null)
        img.color = new Color(1f, 1f, 1f, 0.5f);
}
```

**长度约束判定**：

```csharp
bool CheckLineLengthFailure()
{
    switch (currentTask)
    {
        case 3:
        case 5:
            {
                float cur = Vector2.Distance(
                    redDot.anchoredPosition, yellowDot.anchoredPosition);
                return initLenRY > 0f
                    && Mathf.Abs(cur - initLenRY) / initLenRY > 0.15f;
            }

        case 6:
            {
                float curRY = Vector2.Distance(redDot, yellowDot);
                float curRB = Vector2.Distance(redDot, blueDot);
                float curYB = Vector2.Distance(yellowDot, blueDot);

                if (initLenRY > 0f && Mathf.Abs(curRY - initLenRY) / initLenRY > 0.15f) return true;
                if (initLenRB > 0f && Mathf.Abs(curRB - initLenRB) / initLenRB > 0.15f) return true;
                if (initLenYB > 0f && Mathf.Abs(curYB - initLenYB) / initLenYB > 0.15f) return true;
                return false;
            }

        default:
            return false;
    }
}
```

---

## 3.5 任务系统设计

### 3.5.1 任务状态机

系统采用有限状态机（FSM）管理任务生命周期：

```
                    ┌──────────────┐
                    │   IDLE       │
                    │  (无任务)    │
                    └──────┬───────┘
                           │ 按键触发
                           ↓
                    ┌──────────────┐
          ┌────────│   RUNNING    │────────┐
          │        │  (任务执行)  │        │
          │        └──────┬───────┘        │
          │               │                │
    时间耗尽│         成功判定│        长度约束失败
          │               │                │
          ↓               ↓                ↓
    ┌──────────┐   ┌──────────┐    ┌──────────┐
    │  DEFEAT  │   │ SUCCESS  │    │  DEFEAT  │
    └──────────┘   └──────────┘    └──────────┘
```

### 3.5.2 六个任务模块

| 任务 | 触发按键 | 执行点 | 目标数 | 特殊约束 | 训练目标 |
|------|----------|--------|--------|----------|----------|
| 1 | 右手 A | 红、黄、蓝 | 3 | 无 | 基础手眼协调 |
| 2 | 右手 B | 白 (中点)、蓝 | 2 | 无 | 中点计算 |
| 3 | 左手 X | 白 (中点)、蓝 | 2 | 红 - 黄连线长度±15% | 中点 + 距离约束 |
| 4 | 左手 Y | 白 (重心) | 1 | 无 | 重心计算 |
| 5 | 左 X+ 右 A | 白 (重心) | 1 | 红 - 黄连线长度±15% | 重心 + 单连线约束 |
| 6 | 左 Y+ 右 B | 白 (重心) | 1 | 三条连线长度±15% | 重心 + 多连线约束 |

### 3.5.3 中点与重心计算

**中点公式**（任务 2、3）：
```csharp
void SetWhiteDotToMidpoint(RectTransform a, RectTransform b)
{
    if (whiteDot == null) return;
    whiteDot.anchoredPosition = (a.anchoredPosition + b.anchoredPosition) * 0.5f;
}
```

**重心公式**（任务 4、5、6）：
```csharp
void SetWhiteDotToCentroid(RectTransform a, RectTransform b, RectTransform c)
{
    if (whiteDot == null) return;
    whiteDot.anchoredPosition =
        (a.anchoredPosition + b.anchoredPosition + c.anchoredPosition) / 3f;
}
```

### 3.5.4 同时按键检测

任务 5 和 6 需要检测两个按键的"同时"按下：

```csharp
// 记录按键按下时间戳
if (leftXDown) timeLeftXDown = Time.time;
if (rightADown) timeRightADown = Time.time;

// 同时按下判定：两键当前均按住，且按下时间差在窗口内
bool XASimul = leftX && rightA
    && (Time.time - timeLeftXDown < kSimultWindow)
    && (Time.time - timeRightADown < kSimultWindow);
```

其中 `kSimultWindow = 0.5f` 秒，允许 500ms 的时间差。

---

## 3.6 数据记录模块

### 3.6.1 采集数据类型

系统记录以下数据：

| 数据类型 | 描述 | 采样频率 |
|----------|------|----------|
| 帧号 | Unity 帧计数器 | 每帧 |
| 执行点位置 | 各投影点的 Canvas 坐标 | 每帧 |
| 累计移动距离 | 各执行点从起点开始的总移动距离 | 每帧累加 |
| 初始直线距离 | 任务启动时执行点到目标的距离 | 任务开始时 |
| 任务结果 | 成功/失败、用时 | 任务结束时 |
| 时间戳 | 系统时间 | 任务结束时 |

### 3.6.2 数据结构

```csharp
// 数据记录字段
private RectTransform[] executionDots;       // 当前任务的执行点
private RectTransform[] matchedTargets;      // 执行点对应的目标体
private float[] traveledDistance;            // 各执行点累计移动距离
private Vector2[] lastFramePos;              // 上一帧执行点位置
private float[] initDistToTarget;            // 初始直线距离
private System.Text.StringBuilder frameLog;  // 逐帧位置日志
```

### 3.6.3 逐帧记录

```csharp
// Update 中的记录逻辑
if (executionDots != null && frameLog != null)
{
    frameLog.Append($"  Frame={Time.frameCount}");
    for (int i = 0; i < executionDots.Length; i++)
    {
        if (executionDots[i] == null) continue;
        Vector2 cur = executionDots[i].anchoredPosition;
        traveledDistance[i] += Vector2.Distance(cur, lastFramePos[i]);
        lastFramePos[i] = cur;
        frameLog.Append($"  {GetDotName(executionDots[i])}={cur}");
    }
    frameLog.AppendLine();
}
```

### 3.6.4 结果输出

任务结束时生成日志文件：

```csharp
void LogTaskResult(bool success)
{
    float elapsed = timer;
    System.Text.StringBuilder sb = new System.Text.StringBuilder();

    sb.AppendLine($"══ Task {currentTask} Result ══");
    
    if (success)
        sb.AppendLine($"[结果] SUCCESS  用时：{elapsed:F2}s");
    else
        sb.AppendLine("[结果] DEFEAT");

    sb.AppendLine("[逐帧位置]");
    sb.Append(frameLog);

    if (success && executionDots != null)
    {
        sb.AppendLine("[距离统计]");
        for (int i = 0; i < executionDots.Length; i++)
        {
            string dotName = GetDotName(executionDots[i]);
            sb.AppendLine($"  {dotName} → 累计移动距离：{traveledDistance[i]:F2}px  " +
                          $"初始直线距离：{initDistToTarget[i]:F2}px");
        }
    }

    string filename = $"Task{currentTask}_{DateTime.Now:yyyyMMdd_HHmmss}.txt";
    string path = Path.Combine(Application.persistentDataPath, filename);
    File.AppendAllText(path, sb.ToString());
}
```

**输出示例**：
```
══ Task 1 Result ══
[结果] SUCCESS  用时：3.45s
[逐帧位置]
  Frame=1234  Red=(120.5, 80.3)  Yellow=(-50.2, 100.1)  Blue=(30.0, -60.5)
  Frame=1235  Red=(121.0, 80.5)  Yellow=(-50.0, 100.3)  Blue=(30.2, -60.3)
  ...
[距离统计]
  Red → 累计移动距离：245.67px  初始直线距离：180.50px
  Yellow → 累计移动距离：312.45px  初始直线距离：220.30px
  Blue → 累计移动距离：198.23px  初始直线距离：150.75px
```

---

## 3.7 项目管理与时间规划

### 3.7.1 开发周期

本项目总开发周期为 16 周，分为以下阶段：

| 阶段 | 周次 | 主要任务 | 交付物 |
|------|------|----------|--------|
| 需求分析 | 1-2 | 文献调研、需求定义 | 需求规格说明书 |
| 系统设计 | 3-4 | 架构设计、技术选型 | 设计文档 |
| 核心开发 | 5-8 | 投影算法、碰撞检测、任务系统 | 可运行原型 |
| 功能完善 | 9-11 | 数据记录、UI 优化、调试 | 完整系统 |
| 测试验证 | 12-13 | 功能测试、性能测试 | 测试报告 |
| 文档撰写 | 14-16 | 论文写作、代码整理 | 毕业论文 |

### 3.7.2 风险管理

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|----------|
| VR 设备延迟高 | 中 | 高 | 优化渲染管线，降低画质 |
| 追踪精度不足 | 低 | 中 | 增加滤波算法，校准平面 |
| 任务难度不合理 | 中 | 中 | 预测试调整参数 |
| 开发进度延误 | 中 | 高 | 预留缓冲时间，优先核心功能 |

### 3.7.3 资源使用

| 资源类型 | 数量 | 用途 |
|----------|------|------|
| 开发主机 | 1 台 | 代码开发、场景编辑 |
| VR HMD | 1 套 | 测试、演示 |
| Pico Tracker | 1 个 | 第三方追踪 |
| Unity Pro | 1 许可 | 开发引擎（教育版免费） |
| 开发时间 | 16 周 | 全职开发 |

### 3.7.4 成本估算

| 项目 | 费用（人民币） |
|------|----------------|
| Pico 4 Enterprise | ¥3,999 |
| Pico Tracker | ¥999 |
| 开发主机（已有） | ¥0 |
| Unity 许可（教育版） | ¥0 |
| 其他软件工具 | ¥0 |
| **总计** | **¥4,998** |

---

**本章小结**

本章详细介绍了系统的设计与实现，包括：
- 分层架构设计和核心模块划分
- 硬件选型依据和配置参数
- Unity 场景结构和组件配置
- 3D-2D 投影、碰撞检测、连线绘制等核心算法
- 六个渐进式任务的设计逻辑
- 数据采集和导出机制
- 项目管理计划和成本估算

系统采用模块化设计，代码结构清晰，便于后续维护和功能扩展。
