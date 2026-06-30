# 智能导盲犬轻量化方向文献调研报告

> 调研时间：2026-06-12
> 调研方向：智能导盲犬（Guide Dog Robot）系统中的轻量化技术

---

## 一、导盲犬机器人核心系统

### 1.1 最新代表性工作

**[1] "The Design and Implementation of an Intelligent Guide Dog Robot Based on Multimodal Perception"**
- 作者：Yanxuan Zhu
- 年份：2025
- 期刊：Journal of Electronic Research and Application
- DOI：[10.26689/jera.v9i5.12397](https://doi.org/10.26689/jera.v9i5.12397)
- **摘要**：针对传统导盲设备环境感知单一、地形适应性差的问题，提出基于四足机器人平台的智能导盲系统。通过多传感器时空配准技术实现毫米波雷达（精度±0.1°）与RGB-D相机的数据融合，构建适合导盲场景的数据集。

**[2] "System Configuration and Navigation of a Guide Dog Robot: Toward Animal Guide Dog-Level Guiding Work"**
- 作者：Hochul Hwang, Tim Xia, Ibrahima Keita
- 年份：2023
- 会议：**IEEE ICRA 2023**（机器人顶级会议）
- DOI：[10.1109/icra48891.2023.10160573](https://doi.org/10.1109/icra48891.2023.10160573)
- **亮点**：以"达到真实导盲犬水平"为目标，系统性地设计了导盲机器人的配置与导航架构。

**[3] "Towards Robotic Companions: Understanding Handler-Guide Dog Interactions for Informed Guide Dog Robot Design"**
- 作者：Hochul Hwang, Hee-Tae Jung, Nicholas A. Giudice
- 年份：2024
- 会议：**ACM CHI 2024**（人机交互顶级会议）
- DOI：[10.1145/3613904.3642181](https://doi.org/10.1145/3613904.3642181)
- **亮点**：从人与真实导盲犬的交互行为中提取设计原则，为导盲机器人的人机交互提供实证基础。

**[4] "Tethering a Human with a Quadruped Robot: A Guide Dog to Help Visually Impaired People"**
- 作者：Viviana Morlando, Vincenzo Lippiello, Fabio Ruggiero
- 年份：2023
- 会议：31st Mediterranean Conference on Control and Automation (MED)
- DOI：[10.1109/med59994.2023.10185715](https://doi.org/10.1109/med59994.2023.10185715)
- **亮点**：研究四足机器人与视障人士之间的牵引交互机制，模拟真实导盲犬的牵引引导。

### 1.2 经典基础工作

**[5] "A new vision and navigation research for a guide-dog robot system in urban system"**
- 作者：Yuanlong Wei, Xiangxin Kou, Min Cheol Lee
- 年份：2014
- 会议：IEEE/ASME AIM 2014
- DOI：[10.1109/aim.2014.6878260](https://doi.org/10.1109/aim.2014.6878260)

**[6] "Vision based guide-dog robot system for visually impaired in urban system"**
- 作者：Xiangxin Kou, Yuanlong Wei, Mincheol Lee
- 年份：2013
- 会议：ICCAS 2013
- DOI：[10.1109/iccas.2013.6703876](https://doi.org/10.1109/iccas.2013.6703876)

---

## 二、轻量化目标检测模型（YOLO 系列）

### 2.1 YOLO 最新版本对比与优化

**[7] "COMPARATIVE ANALYSIS OF YOLOV8 AND YOLOV10 FOR REAL-TIME OBJECT DETECTION"**
- 作者：S. I. Hlod, A. V. Doroshenko
- 年份：2026
- 期刊：Ukrainian Journal of Information Technology
- DOI：[10.23939/ujit2026.01.051](https://doi.org/10.23939/ujit2026.01.051)
- **亮点**：对比 YOLOv8 与 YOLOv10 在资源受限环境下的实时检测性能，对导盲犬嵌入式部署有直接参考价值。

**[8] "Comparative Analysis of YOLOv8, YOLOv9, and YOLOv10 for Object Detection"**
- 作者：Tumanan Silvanus
- 年份：2025
- 期刊：IJRASET
- DOI：[10.22214/ijraset.2025.71284](https://doi.org/10.22214/ijraset.2025.71284)
- **亮点**：在 Pascal VOC 2012 数据集上系统比较三代 YOLO 的精度-速度权衡。

### 2.2 面向边缘设备的 YOLO 优化

**[9] "Edge-Optimized Real-Time Object Detection in AIoT Systems Using Quantized YOLOv8 and Deep SORT"**
- 作者：Chaoran Li
- 年份：2026
- 期刊：Informatica
- DOI：[10.31449/inf.v50i7.10210](https://doi.org/10.31449/inf.v50i7.10210)
- **亮点**：提出 EdgeTrack-YOLOv8，结合量化（quantization）与 Deep SORT 多目标跟踪，在资源受限平台上实现低延迟多目标识别。**可直接借鉴到导盲犬的边缘部署。**

**[10] "An Optimized GhostNet-YOLOv8 Architecture for Real-Time Object Detection in Edge AIoT Surveillance Applications"**
- 作者：Monish Sai Krishna Namana, Budidi Udaya Kumar
- 年份：2026
- 会议：ICIIP 2025
- DOI：[10.1109/iciip68302.2025.11346418](https://doi.org/10.1109/iciip68302.2025.11346418)
- **亮点**：用 GhostNet 替换 YOLOv8 的骨干网络，大幅减少参数量和计算量，适合边缘部署。

**[11] "Edge Computing-based Real-Time Surveillance System with YOLOv8 Object Detection using NVIDIA Jetson Nano"**
- 作者：Vedant Ghodmare 等
- 年份：2025
- 会议：ICPCSN 2025
- DOI：[10.1109/icpcsn65854.2025.11034845](https://doi.org/10.1109/icpcsn65854.2025.11034845)
- **亮点**：在 NVIDIA Jetson Nano 上部署 YOLOv8 的实际工程经验，对导盲犬硬件选型有参考价值。

### 2.3 模型压缩与轻量化 Pipeline

**[12] "A Lightweight Neural Network Compression Pipeline for Resource-Constrained Edge AI Systems"**
- 作者：Som Subhro Nath
- 年份：2026
- DOI：[10.21203/rs.3.rs-9295528/v1](https://doi.org/10.21203/rs.3.rs-9295528/v1)
- **亮点**：提出一套完整的轻量级神经网络压缩 pipeline，专为资源受限边缘设备设计，包含剪枝、量化、知识蒸馏等技术。

---

## 三、视障辅助导航与障碍物检测系统

### 3.1 基于 YOLO 的导盲系统

**[13] "Navigation Assistive Intelligent Device with YOLOv8 Object Detection and Geometric Distance Estimation"**
- 作者：M Saranya, S Arulselvarani
- 年份：2026
- 期刊：Indian Journal of Science and Technology
- DOI：[10.17485/ijst/v19i7.1923](https://doi.org/10.17485/ijst/v19i7.1923)
- **亮点**：可穿戴导航系统，结合 YOLOv8 + Deep SORT + 几何距离-角度估计，嵌入式便携平台部署。**与导盲犬轻量化高度相关。**

**[14] "Real-Time Obstacle Detection using Yolov8 for Assistive Navigation"**
- 作者：M. Saranya, S. Arulselvarani
- 年份：2025
- 期刊：Indian Journal of Science and Technology
- DOI：[10.17485/ijst/v18i25.937](https://doi.org/10.17485/ijst/v18i25.937)
- **亮点**：用 YOLOv8 + 立体视觉实时检测障碍物并计算距离/角度。

**[15] "An Affordable Intelligent Navigation Backpack for the Visually Impaired: Deep Learning-Based Obstacle Detection and Real-Time Navigation with RGB-D Integration"**
- 作者：Cheng-Li Luo, Hai Xu, Min Liu
- 年份：2025
- 期刊：Journal of Internet Technology
- DOI：[10.70003/160792642025032602011](https://doi.org/10.70003/160792642025032602011)
- **亮点**：低成本智能导航背包，深度学习障碍物检测 + RGB-D 融合实时导航。

**[16] "Low-cost guide dog robot navigation using Dueling DQN"**
- 作者：Feiran Fang
- 年份：2024
- 期刊：Applied and Computational Engineering
- DOI：[10.54254/2755-2721/95/20241751](https://doi.org/10.54254/2755-2721/95/20241751)
- **亮点**：低成本导盲机器人导航，使用 Dueling DQN 强化学习方法，不依赖单一传感器。

### 3.2 其他辅助技术

**[17] "Deep Learning-Based Assistive System for Visually Impaired Individuals: A Comparative Study of YOLO Models"**
- 作者：Dhanya Raju, Anitha G
- 年份：2026
- 期刊：International Journal on Science and Technology
- DOI：[10.71097/ijsat.v17.i2.10978](https://doi.org/10.71097/ijsat.v17.i2.10978)
- **亮点**：系统比较多种 YOLO 模型在视障辅助场景下的表现。

**[18] "Real-time computer vision and deep learning for 3D environment modeling, camera network calibration, and human-robot interaction using a robot dog"**
- 作者：Zhigang Zhu, Jie Gong, Chong Di
- 年份：2025
- 会议：Real-Time Image Processing and Deep Learning 2025
- DOI：[10.1117/12.3052817](https://doi.org/10.1117/12.3052817)
- **亮点**：基于机器狗平台的实时 3D 环境建模、相机标定与人机交互，虽然是通用机器狗，但技术可迁移到导盲犬场景。

---

## 四、硬件平台参考

| 平台 | 适用场景 | 相关论文 |
|------|---------|---------|
| **NVIDIA Jetson Nano** | 边缘深度学习推理，GPU 加速 | [11] Ghodmare et al. (2025) |
| **Raspberry Pi** | 低成本辅助视觉/导航 | [2023] Artificial Vision-Raspberry Pi Based Reader; [2024] Google pi using raspberry pi |
| **嵌入式轻量部署** | 模型量化 + 跟踪 | [9] Li (2026) EdgeTrack-YOLOv8 |
| **GhostNet + YOLO** | 极致轻量化骨干网络 | [10] Namana & Kumar (2026) |

---

## 五、技术路线总结

基于以上文献，智能导盲犬轻量化的**关键技术方向**可归纳为：

### 5.1 感知层
- **多传感器融合**：RGB-D 相机 + 毫米波雷达（Zhu 2025）
- **立体视觉障碍物检测** + 几何距离估计（Saranya 2025/2026）
- **YOLO 系列实时目标检测**（v8/v9/v10 各有优劣）

### 5.2 轻量化层
- **模型压缩 pipeline**：剪枝 + 量化 + 知识蒸馏（Nath 2026）
- **轻量骨干网络替换**：GhostNet → YOLOv8（Namana 2026）
- **边缘量化部署**：INT8 量化 + TensorRT（Li 2026）
- **云-边协同**：重计算放云端，轻推理在边缘（Du & Wei 2026）

### 5.3 导航与交互层
- **强化学习导航**：Dueling DQN（Fang 2024）
- **人机牵引交互**：四足机器人牵引机制（Morlando 2023）
- **人-导盲犬交互实证**：从真实导盲犬提取设计原则（Hwang 2024 CHI）

### 5.4 系统层
- **顶会级完整系统**：ICRA 2023 Hwang 的导盲机器人系统
- **低成本方案**：Raspberry Pi + 超声波传感器（Deepika 2026）

---

## 六、建议重点阅读的论文

1. **Hwang et al. (2023) ICRA** — 导盲机器人系统设计的标杆工作
2. **Zhu (2025)** — 多感知融合导盲犬，最新的系统设计
3. **Li (2026) EdgeTrack-YOLOv8** — 边缘量化部署的最佳实践
4. **Nath (2026)** — 完整的神经网络压缩 pipeline
5. **Saranya (2026)** — YOLOv8 + Deep SORT + 距离估计，高度契合导盲需求
6. **Hwang (2024) CHI** — 人机交互设计原则，论文写作时可用于 introduction/motivation
