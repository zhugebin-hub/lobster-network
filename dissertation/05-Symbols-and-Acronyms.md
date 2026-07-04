# 符号与缩略语表 (List of Symbols and Acronyms)

## 缩略语

| 缩略语 | 英文全称 | 中文含义 |
|--------|----------|----------|
| VR | Virtual Reality | 虚拟现实 |
| XR | Extended Reality | 扩展现实 |
| HMD | Head-Mounted Display | 头戴式显示器 |
| ROM | Range of Motion | 关节活动度 |
| ADL | Activities of Daily Living | 日常生活活动 |
| UI | User Interface | 用户界面 |
| Canvas | Unity Canvas Component | Unity 画布组件 |
| SDK | Software Development Kit | 软件开发工具包 |
| API | Application Programming Interface | 应用程序接口 |
| FPS | Frames Per Second | 帧率 |
| FOV | Field of View | 视场角 |
| DOF | Degrees of Freedom | 自由度 |
| IMU | Inertial Measurement Unit | 惯性测量单元 |
| TCP | Transmission Control Protocol | 传输控制协议 |
| GPU | Graphics Processing Unit | 图形处理器 |

## 符号说明

| 符号 | 含义 | 单位 |
|------|------|------|
| *P*~world~ | 世界空间中的三维点坐标 | (x, y, z) |
| *P*~local~ | 局部空间中的三维点坐标 | (x, y, z) |
| *P*~canvas~ | Canvas 二维平面坐标 | (u, v) |
| *W*~plane~ | 投影平面世界宽度 | 米 (m) |
| *H*~plane~ | 投影平面世界高度 | 米 (m) |
| *W*~canvas~ | Canvas 像素宽度 | 像素 (px) |
| *H*~canvas~ | Canvas 像素高度 | 像素 (px) |
| *d*~threshold~ | 碰撞判定阈值 | 像素 (px) |
| *L*~init~ | 连线初始长度 | 像素 (px) |
| *L*~curr~ | 连线当前长度 | 像素 (px) |
| Δ*L* | 连线长度变化率 | 百分比 (%) |
| *t*~elapsed~ | 任务经过时间 | 秒 (s) |
| *t*~limit~ | 任务时间上限 | 秒 (s) |

## 坐标系定义

- **世界坐标系**：Unity 场景全局坐标系，右手系，Y 轴向上
- **局部坐标系**：以 ProjectionPlaneRoot 为原点的相对坐标系
- **Canvas 坐标系**：UI 画布二维坐标系，原点位于中心，X 轴向右，Y 轴向上
