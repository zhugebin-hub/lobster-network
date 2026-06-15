# 附录 C Unity 场景配置详情 (Appendix C: Unity Scene Configuration Details)

## C.1 场景文件结构

### C.1.1 项目设置

| 设置项 | 值 |
|--------|------|
| Unity 版本 | 2022.3.15f1 |
| 渲染管线 | Built-in Render Pipeline |
| 目标平台 | Android (Pico) |
| 脚本后端 | IL2CPP |
| API 兼容性级别 | .NET Standard 2.1 |

### C.1.2 XR 插件配置

**XR Plugin Management**：
- Pico XR Plugin: ✅ 启用
- Meta XR Plugin: ❌ 禁用
- OpenXR: ❌ 禁用

**Pico XR Plugin 设置**：
- SDK Version: 2.1.0
- Eye Tracking: 禁用
- Hand Tracking: 禁用（本项目使用控制器）
- Spatial Audio: 启用

---

## C.2 Hierarchy 详细配置

### C.2.1 根对象

| GameObject | 组件 | 关键配置 |
|------------|------|----------|
| SampleScene | Scene | 主场景 |
| Directional Light | Light, Transform | 强度 1.0, 白色 |
| XR Interaction Manager | XRInteractionManager | 自动更新 = 0.1s |
| XR Origin (VR) | XROrigin | Tracking Origin = Floor |
| Input Manager | MonoBehaviour | 自定义输入管理 |
| Global Volume | Volume | 后处理体积 |
| EventSystem | EventSystem, StandaloneInputModule | UI 事件系统 |
| ProjectionPlaneRoot | Transform | 投影平面根节点 |

### C.2.2 XR Origin 子对象

**XR Origin (VR)**：
- 位置：(0, 0, 0)
- 旋转：(0, 0, 0)
- 缩放：(1, 1, 1)

**Camera Offset**：
- 位置：(0, 1.6, 0)  // 模拟站立高度
- 组件：CameraOffset

**Main Camera**：
- 位置：(0, 0, 0)（相对 Camera Offset）
- 投影：Perspective
- FOV: 90°
- 近裁剪：0.01
- 远裁剪：1000
- 清除标志：Solid Color
- 背景色：(0.1, 0.1, 0.15, 1.0)

**Left Controller**：
- 组件：XR Controller, XRBaseController
- 追踪：6DOF
- 可视化：Sphere_Left (红色球体)

**Right Controller**：
- 组件：XR Controller, XRBaseController
- 追踪：6DOF
- 可视化：Sphere_Right (黄色球体)

**Pico Tracker**：
- 组件：XR Controller, XRBaseController
- 追踪：6DOF
- 可视化：Sphere_Tracker (蓝色球体)

### C.2.3 ProjectionPlaneRoot 子对象

**ProjectionPlaneRoot**：
- 位置：(0, 0, -1)
- 旋转：(0, 0, 0)
- 缩放：(1, 1, 1)

**PlaneVisual**：
- 组件：MeshFilter, MeshRenderer
- 材质：ProjectionPlaneMaterial
- 尺寸：2m × 1.5m
- 颜色：半透明灰色

**ProjectionCanvas**：
- 组件：Canvas, CanvasScaler, GraphicRaycaster
- Render Mode: Screen Space - Camera
- 主相机：Main Camera
- UI Scale Mode: Scale With Screen Size
- Reference Resolution: 1920 × 1080
- Match: 0.5

**TargetsContainer**：
- 组件：RectTransform
- 锚点：Center
- 尺寸：1920 × 1080
- 用途：容纳动态生成的目标体

**RedDot**：
- 组件：RectTransform, Image
- 尺寸：20 × 20 像素
- 颜色：红色 (1, 0, 0)
- 形状：圆形

**YellowDot**：
- 组件：RectTransform, Image
- 尺寸：20 × 20 像素
- 颜色：黄色 (1, 1, 0)
- 形状：圆形

**BlueDot**：
- 组件：RectTransform, Image
- 尺寸：20 × 20 像素
- 颜色：蓝色 (0, 0, 1)
- 形状：圆形

**WhiteDot**：
- 组件：RectTransform, Image
- 尺寸：24 × 24 像素
- 颜色：白色 (1, 1, 1)
- 形状：圆形
- 初始状态：隐藏

**TimerText**：
- 组件：RectTransform, TextMeshProUGUI
- 字体：TMP Default Font
- 字号：48
- 颜色：白色
- 对齐：居中
- 初始文本："00:10"

**ResultText**：
- 组件：RectTransform, TextMeshProUGUI
- 字体：TMP Default Font
- 字号：64
- 颜色：绿色/红色（动态）
- 对齐：居中
- 初始状态：隐藏

---

## C.3 预制体配置

### C.3.1 TargetPrefab（目标体）

| 属性 | 值 |
|------|------|
| 类型 | GameObject |
| 组件 | RectTransform, Image |
| 尺寸 | 40 × 40 像素 |
| 颜色 | 绿色 (0, 1, 0) |
| 透明度 | 0.7 |
| 形状 | 正方形边框 |
| 初始状态 | 激活 |

### C.3.2 LinePrefab（连线）

| 属性 | 值 |
|------|------|
| 类型 | GameObject |
| 组件 | RectTransform, Image |
| 尺寸 | 动态（宽度=距离，高度=粗细） |
| 颜色 | 白色 (1, 1, 1) |
| 透明度 | 0.5 |
| 材质 | UI Default Material |
| 初始状态 | 激活 |

---

## C.4 脚本配置

### C.4.1 ProjectionSystem 组件

挂载于：ProjectionPlaneRoot

**Inspector 字段赋值**：

| 字段 | 赋值对象 |
|------|----------|
| redSphere | Sphere_Left |
| yellowSphere | Sphere_Right |
| blueSphere | Sphere_Tracker |
| planeTransform | ProjectionPlaneRoot |
| planeWorldWidth | 2.0 |
| planeWorldHeight | 1.5 |
| canvasRect | ProjectionCanvas |
| redDot | RedDot |
| yellowDot | YellowDot |
| blueDot | BlueDot |
| whiteDot | WhiteDot |
| timerText | TimerText |
| resultText | ResultText |
| targetsContainer | TargetsContainer |
| targetPrefab | TargetPrefab (Resources) |
| linePrefab | LinePrefab (Resources) |
| taskDuration | 10.0 |
| hitThreshold | 30.0 |

---

## C.5 资源文件

### C.5.1 材质

| 文件名 | 路径 | 用途 |
|--------|------|------|
| ProjectionPlaneMaterial | Assets/Materials/ | 投影平面可视化 |
| TargetMaterial | Assets/Materials/ | 目标体材质 |
| LineMaterial | Assets/Materials/ | 连线材质 |
| DotMaterial | Assets/Materials/ | 投影点材质 |

### C.5.2 预制体

| 文件名 | 路径 | 用途 |
|--------|------|------|
| TargetPrefab.prefab | Assets/Prefabs/ | 目标体预制体 |
| LinePrefab.prefab | Assets/Prefabs/ | 连线预制体 |

### C.5.3 脚本

| 文件名 | 路径 | 用途 |
|--------|------|------|
| ProjectionSystem.cs | Assets/Scripts/ | 主控制脚本 |

### C.5.4 场景

| 文件名 | 路径 | 用途 |
|--------|------|------|
| SampleScene.unity | Assets/Scenes/ | 主场景 |

---

**附录 C 结束**
