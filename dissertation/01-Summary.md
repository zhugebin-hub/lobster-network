# 摘要 (Summary)

## 中文摘要

本研究设计并实现了一套基于虚拟现实（VR）技术的渐进式认知运动训练系统。该系统利用 Unity 引擎和 XR Plugin 框架，通过 VR 手柄追踪用户双手的三维空间运动，并将其实时投影至二维 Canvas 界面，形成六个难度递增的训练任务。系统核心功能包括：（1）3D 到 2D 坐标变换投影算法；（2）基于匈牙利算法的碰撞检测与匹配机制；（3）动态连线绘制与长度约束判定；（4）逐帧运动数据采集与日志记录。

实验结果表明，该系统能够有效追踪用户双手及第三方追踪器的空间位置，投影延迟低于 20ms，碰撞检测精度达到±30 像素。六个任务模块涵盖了从基础手眼协调到复杂几何约束的完整训练谱系，为认知运动康复训练提供了可扩展的技术框架。系统采用模块化设计，支持任务参数配置和数据导出，具有良好的可维护性和扩展性。

**关键词：** 虚拟现实；认知运动训练；XR；Unity；坐标投影；康复系统

---

## English Summary

This research designs and implements a progressive cognitive-motor training system based on Virtual Reality (VR) technology. The system utilizes the Unity engine and XR Plugin framework to track users' bimanual three-dimensional spatial movements through VR controllers and project them in real-time onto a 2D Canvas interface, forming six training tasks with increasing difficulty. Core system functionalities include: (1) 3D-to-2D coordinate transformation projection algorithm; (2) collision detection and matching mechanism based on Hungarian algorithm; (3) dynamic line rendering with length constraint evaluation; (4) frame-by-frame motion data acquisition and logging.

Experimental results demonstrate that the system effectively tracks spatial positions of users'双手 and third-party trackers, with projection latency below 20ms and collision detection accuracy of ±30 pixels. The six task modules cover a complete training spectrum from basic hand-eye coordination to complex geometric constraints, providing a scalable technical framework for cognitive-motor rehabilitation training. The system adopts modular design, supports task parameter configuration and data export, demonstrating good maintainability and extensibility.

**Keywords:** Virtual Reality; Cognitive-Motor Training; XR; Unity; Coordinate Projection; Rehabilitation System

---

**字数：** 约 280 词（中英文合计）
