# 📝 Dissertation Polishing Report

**论文：** Vision-based Hand Gesture Control of a Robotic Arm  
**作者：** Candidate 269877 | **导师：** Dr. Yanpei Huang  
**版本：** Ver 1.2 → 润色建议版

---

## 一、总体评价

论文结构完整，技术路线清晰，实验数据充分。主要问题集中在：

1. **第5章语体严重不一致** — 从学术写作突然变为口语化叙述（最严重）
2. **长句过多** — 多处一句话包含2-3个独立意思（run-on sentences）
3. **公式(1)缺失** — PID公式位置为空
4. **内容重复** — 4.2.4节两段话描述同一件事
5. **人称/时态不一致** — 混用 I/we/this project/this study
6. **附录内容为空** — 代码、成本表、Logbook 均未填入

---

## 二、逐章润色建议

### 摘要 (Summary)

**原文：**
> This project developed a vision-based system that allows a person to control a six degree-of-freedom robotic arm using natural gestures.

**润色后：**
> This project develops a vision-based system enabling intuitive control of a six-degree-of-freedom robotic arm through natural hand gestures.

**说明：** "developed" → "develops"（摘要通常用现在时描述论文内容）；"allows a person to control" 改为 "enabling intuitive control" 更简洁学术。

---

### Chapter 1. Introduction

#### 第一段过于冗长

**原文：**
> Human-Machine Interaction (HMI) has a history of continuous pursuit of greater naturalness. It has long shed the rigid shell of the early single graphical interface and evolved into an all-encompassing ecosystem, allowing us to monitor and control complex automated systems in various ways [1]. Today human-machine interaction methods are truly diverse, we can command machines through visual capture or achieve control through traditional manual operation, voice commands, or even environmental sensing, this change permeates every aspect of life. When you look at the screen to obtain information or hold the steering wheel with both hands to control the trajectory of the vehicle, it is a classic combination of vision and touch. In smart homes you can control furniture with a single command, or have the light sensor automatically adjust the opening and closing of the curtains for you, this is the perception ability bestowed upon the environment by technology. These diverse interaction methods have greatly enriched the connection points between humans and technology, making the originally cold operations feel as natural as breathing, truly making them within reach.

**润色后：**
> Human-Machine Interaction (HMI) has evolved from rigid graphical interfaces into a multifaceted ecosystem that enables users to monitor and control complex automated systems through diverse modalities [1]. Contemporary HMI methods encompass visual capture, manual operation, voice commands, and environmental sensing — each permeating different aspects of daily life. For instance, screen-based information retrieval and steering wheel manipulation represent classic integrations of vision and tactile feedback. In smart home environments, voice commands can control appliances while ambient light sensors automatically regulate curtains, demonstrating how technology endows environments with perceptual capabilities. These diverse interaction paradigms have significantly enriched human-technology connectivity, transforming previously rigid operations into intuitive, natural experiences.

**修改要点：**
- 拆分了原第3句（包含4个独立分句的run-on sentence）
- 去掉了 "you" 等第二人称，改为客观学术表述
- "feel as natural as breathing, truly making them within reach" 过于文学化

#### 第三段开头

**原文：**
> Utilizing visual technology to control surgical instruments is actually an attempt to address several long-standing problems in traditional manual control.

**润色后：**
> The application of vision-based technology to surgical instrument control addresses several long-standing challenges inherent in traditional manual control paradigms.

---

### Chapter 2. Literature Review

#### 2.1 节

**原文：**
> A real paradigm shift occurred in the 1970s and 80s with the introduction of graphical user interfaces (GUIs). By replacing text-based command lines with visual elements like windows, icons, and menus, pioneers like the Xerox Alto and later Apple Macintosh and Microsoft Windows implemented computers accessible to everyone, this transformation allowed non-experts to use intuitive point-and-click interactions by keyboards and mice.

**润色后：**
> A paradigm shift occurred in the 1970s and 1980s with the introduction of graphical user interfaces (GUIs). Pioneering systems such as the Xerox Alto, followed by the Apple Macintosh and Microsoft Windows, replaced text-based command lines with visual elements including windows, icons, and menus. This transformation rendered computers accessible to non-expert users through intuitive point-and-click interactions via keyboards and mice.

#### 2.2.1 节

**原文：**
> The Leap Motion Controller (LMC) distinct from these camera-based solutions, integrates active illumination with stereoscopic infrared vision, relying heavily on advanced software algorithms to achieve high-fidelity depth tracking [14], it can be observed by comparing the testing characteristics of the three mainly 3D cameras that LMC strikes a balance between performance and cost-effectiveness, making it the preferred choice for implementing this project.

**润色后：**
> Distinct from camera-based solutions, the Leap Motion Controller (LMC) integrates active illumination with stereoscopic infrared vision, relying on advanced software algorithms to achieve high-fidelity depth tracking [14]. As demonstrated by the comparative analysis of these three 3D sensing technologies (Table 1), the LMC strikes an optimal balance between tracking performance and cost-effectiveness, rendering it the preferred sensor for this project.

#### 2.3.1 节

**原文：**
> Forward kinematics is solved through a process in a given of the angles of each joint, the position and orientation of the end effector are sought.

**润色后：**
> Forward kinematics determines the position and orientation of the end-effector given the angles of each joint.

**原文：**
> The inverse kinematics addresses a more critical issue, given the target pose of the end effector, calculate the required joint angles to achieve that pose, this is the core for implementing gesture control.

**润色后：**
> Inverse kinematics addresses the complementary problem: given a target end-effector pose, compute the required joint angles. This constitutes the core computational challenge in implementing gesture-based control.

#### ⚠️ 公式(1)缺失

**原文位置（2.3.2节）：**
> Its discretized form can be expressed as:  
>                          (1)

**建议补充：**
> Its discretized form can be expressed as:
> 
> u[k] = Kp · e[k] + Ki · Σ(i=0 to k) e[i] + Kd · (e[k] - e[k-1])    (1)
> 
> where u[k] is the control output at step k, e[k] is the tracking error, and Kp, Ki, Kd are the proportional, integral, and derivative gains, respectively.

---

### Chapter 3. System Architecture and Design

#### 3.1 节

**原文：**
> This remote operating system is divided into a local human-machine interface (HMI) and a remote robot system.

**润色后：**
> The proposed system comprises two subsystems: a local human-machine interface (HMI) and a robot control unit.

**说明：** "remote" 在此处容易引起歧义（实际是本地loopback），改为 "robot control unit" 更准确。

#### 3.2 节

**原文：**
> The hardware for this system was selected based on three core principles: meeting the functional requirements for real-time gesture recognition and robotic arm control, balancing development efficiency with cost, and ensuring the system is both repeatable and scalable.

**润色后：**
> Hardware selection was guided by three principles: (1) meeting functional requirements for real-time gesture recognition and robotic arm control, (2) balancing development efficiency with cost, and (3) ensuring system reproducibility and scalability.

---

### Chapter 4. Implementation Results

#### ⚠️ 4.2.4 节 — 严重重复

**问题：** 以下两段话描述完全相同的内容，应合并。

**建议合并为一段（学术版本）：**
> To mitigate high-frequency noise in the LMC data, an exponential smoothing filter with a coefficient of α = 0.3 was applied to the target angles of the first four joints. As illustrated in Figure 17, the raw data exhibits noise amplitudes of ±40–50 mm, which would cause severe mechanical vibration if applied directly. The filtered signal significantly suppresses high-frequency jitter while maintaining tracking responsiveness. Experimental results confirm that the robotic arm exhibits markedly improved stability during stationary positioning and smoother trajectory tracking during motion, with no perceptible phase lag attributable to the 0.3 weight assigned to new data. This configuration achieves an effective trade-off between noise suppression and tracking fidelity.

---

### Chapter 5. Conclusion and Discussion ⚠️ 重点修改

**本章问题最严重：语体从学术写作突然变为口语化叙述。以下是逐段改写：**

#### 5.1 Program Summary

**原文：**
> With the growing need for easier and more natural ways to control robots, teleoperation has become an important topic in robotics, this thesis talks about how to built a teleoperation system for the SO-ARM100 robotic arm, and to make robot control feel more like natural human movement.

**润色后：**
> Driven by the growing demand for intuitive robot control interfaces, teleoperation has emerged as a significant research area in robotics. This dissertation presents the design and implementation of a gesture-based teleoperation system for the SO-ARM100 robotic arm, aiming to bridge the gap between natural human movement and robotic manipulation.

**原文：**
> This project implemented a teleoperation system that uses hand gestures to control the robotic arm, and the gestures are captured by a LMC, it picked hand gestures because they feel natural to people, the LMC captures the hand movements, then the signals go through exponential smoothing and hysteresis logic to make the tracking stable and not too shaky.

**润色后：**
> The implemented system captures operator hand gestures via the LMC and maps them to robotic arm movements. Exponential smoothing and hysteresis-based logic are applied to the gesture signals to suppress noise and ensure stable tracking.

**原文：**
> The robot this project used is the SO-ARM100, which has six degrees of freedom (6-DOF), it mapped the hand gestures to the end-effector movement in Cartesian space. For communication between the gesture part and the robot part I used TCP/IP on a local loopback network. Some simple tests used to see how fast and reliable the system is, the results showed an 85% success rate for gesture execution and the delay was around 80–100ms from end to end.

**润色后：**
> The SO-ARM100 6-DOF robotic arm serves as the manipulation platform, with hand gestures mapped to end-effector movements in Cartesian space. Inter-process communication between the gesture acquisition module and the robot control module is implemented via TCP/IP over a local loopback network. Performance evaluation demonstrates an 85% gesture recognition success rate and an end-to-end latency of 80–100 ms.

**原文（第二段）：**
> The system uses both MATLAB and Python, MATLAB takes care of the data from the LMC, and Python controls the robot using the STServo_sdk. One thing this project implemented is a mapping method that uses the distance between the thumb and index finger to control wrist rotation, this helps the 6-DOF arm do more delicate movements. To make the system safe and stable also added some algorithms to reduce shaking from the sensor and handle gesture switching with hysteresis checks.

**润色后：**
> The system software is implemented in MATLAB (for LMC data acquisition and kinematic computation) and Python (for robot control via the STServo_sdk). A novel mapping strategy utilizes the thumb-index finger distance to control wrist rotation, enabling finer manipulation capabilities for the 6-DOF arm. Safety and stability are enhanced through noise-reduction algorithms and hysteresis-based gesture state transitions.

**原文（第三段）：**
> Overall this project shows that a vision-based hand gesture control system can be fast and reliable, and it gives a good starting point for future work on intuitive teleoperation and human-robot collaboration.

**润色后：**
> In summary, this project demonstrates that vision-based hand gesture control can achieve both low latency and high reliability, providing a solid foundation for future research in intuitive teleoperation and human-robot collaboration.

#### 5.2 Problems and Solutions

**原文：**
> The official documentation of SO-ARM100 did not provide any Windows version SDK files at all. This really caused me some trouble during the initial stage of hardware debugging. At first, I focused on the virtual machine and spent a long time configuring the Ubuntu environment to connect to the robotic arm. However, due to my lack of familiarity with the Linux development process, various compatibility errors, driver conflicts, and the inability to establish communication between the host and the virtual machine all caused significant delays in the project progress, each failure required me to start over, resulting in a substantial slowdown in the project schedule.

**润色后：**
> The absence of a Windows-compatible SDK in the official SO-ARM100 documentation presented a significant challenge during initial hardware debugging. Initial efforts focused on configuring an Ubuntu virtual machine for robotic arm communication. However, Linux compatibility errors, driver conflicts, and host-VM communication failures significantly delayed the project schedule.

**原文：**
> Later, the mentor pointed out a clear path: Since there was no ready-made Windows version of the SDK, we would bypass it and directly start from the servo hardware and the Waveshare control board. Based on the Python library from Micro Snow's official site that has good support for Windows, we developed a custom library that met the requirements of this project, this bottom-up approach allowed me to understand the underlying communication protocol and systematically wrote the core functions such as servo detection, position reading, and angle writing. As a result, we no longer needed to run a virtual machine and also avoided the hassle of maintaining the Ubuntu environment.

**润色后：**
> Guided by the project supervisor, a bottom-up approach was adopted: a custom Python library was developed based on the Waveshare control board's serial communication protocol, leveraging the Micro Snow SDK's native Windows support. This approach eliminated the dependency on a virtual machine and enabled a deeper understanding of the underlying communication protocol, including servo detection, position reading, and angle writing functions.

**原文：**
> This custom-developed library is useful, not only has the program startup process become simpler, without relying on various external tools, but the portability of the entire system has also been greatly enhanced. As the library is written purely in Python and relies only on standard serial communication, it can be directly used on any Windows computer without the need to go through the hassle of environment configuration, this flexibility makes subsequent secondary development, testing, and even deployment on different hardware much more convenient, the reproducibility and scalability of the project have directly improved to a higher level.

**润色后：**
> This custom library simplifies the startup process and significantly enhances system portability. Being implemented purely in Python with standard serial communication dependencies, the library can be deployed on any Windows platform without complex environment configuration, thereby improving the project's reproducibility and scalability.

#### 5.2 小节标题建议修改

| 原标题 | 建议修改 |
|--------|----------|
| Environmental compatibility issue | **A. Windows SDK Compatibility** |
| The servo angle range does not match | **B. Servo Resolution Mismatch** |
| The gripper does not respond to the fist detection | **C. Gripper Torque Enablement** |
| Unintentional wrist rotation movement | **D. Wrist Pitch Mapping Deactivation** |
| Motion Tremors & Instability | **E. High-Frequency Noise Suppression** |

#### 5.3 Limitation and Improvement

**原文：**
> Although the current SO-ARM100 mechanical arm system based on visual gesture control has been successfully tested, we have to honest and admit that the current version is still quite far from perfect, and there are several shortcomings:

**润色后：**
> Although the vision-based gesture control system for the SO-ARM100 has been successfully validated, several limitations remain:

**原文：**
> The first limitation is that the current software architecture and mapping strategies are designed for single-handed operation. Although LMC can actually track both hands simultaneously, we have not utilized this feature yet. This results in the system being unable to perform complex tasks that require left and right coordination. To achieve dual-arm collaboration, we would need to significantly modify the communication protocol and coordination algorithm to prevent the two hands from fighting with each other.

**润色后：**
> **Single-hand operation:** The current architecture supports only unilateral hand tracking. Although the LMC is capable of dual-hand tracking, this feature remains unimplemented. Extending to dual-arm coordination would require significant modifications to the communication protocol and coordination algorithms.

**原文：**
> The next issue is the complete lack of touch sensation. Currently, the system is purely positional control, and the operator has no feeling of force feedback at all. In delicate operations like medical surgeries, not having touch sensation is highly dangerous. For instance, they wouldn't even know if the operator exerts too much force and damages the tissue. Nowadays, the operators can only rely on their eyes, which not only limits the precision but also increases the risk. Although force sensors or current monitoring can solve this problem, the current hardware conditions do not support it.

**润色后：**
> **Absence of haptic feedback:** The system implements position control only, without force feedback. In precision-critical applications such as surgery, this limitation poses safety risks, as operators cannot perceive contact forces. Integration of force sensors or motor current-based force estimation is required to address this gap.

**原文：**
> Furthermore, the gesture library is too limited and the test samples are too few. The gestures currently that can be recognized are quite limited, more complex movements are completely beyond the scope of recognition. Moreover, this test involved only 3 people, and the sample size was small. In the future, more people need to be recruited, covering different hand shapes and age groups, in order to prove that this calibration method is truly effective.

**润色后：**
> **Limited gesture repertoire and sample size:** The current system recognizes only a small set of basic gestures. Furthermore, user testing involved only three participants, which is insufficient to validate the calibration method across diverse hand morphologies and age groups.

---

## 三、格式与一致性检查清单

| # | 问题 | 位置 | 修改建议 |
|---|------|------|----------|
| 1 | **公式(1)缺失** | 2.3.2节 | 补充PID离散公式 |
| 2 | **4.2.4节重复** | 第4章 | 合并或删除重复段落 |
| 3 | **人称不一致** | 全文 | 统一使用 "this study" 或被动语态 |
| 4 | **时态不一致** | 全文 | 已完成工作用过去时，系统功能用现在时 |
| 5 | **Chapter 5口语化** | 第5章 | 全面改为学术语体 |
| 6 | **"mechanical arm" vs "robotic arm"** | 全文 | 统一使用 "robotic arm" |
| 7 | **数字格式** | 全文 | 统一：80–100 ms（数字与单位间空格）|
| 8 | **参考文献格式** | References | 统一为 IEEE 格式 |
| 9 | **附录内容为空** | 附录 | 填入代码、成本表等 |

---

## 四、润色优先级

| 优先级 | 修改项 | 预计工作量 |
|--------|--------|-----------|
| 🔴 P0 | 补充公式(1) | 5分钟 |
| 🔴 P0 | 删除4.2.4重复段落 | 5分钟 |
| 🔴 P0 | 补充附录内容 | 30分钟 |
| 🟡 P1 | Chapter 5 全面改写 | 1-2小时 |
| 🟡 P1 | 全文人称/时态统一 | 30分钟 |
| 🟡 P1 | 长句拆分（第1-3章） | 1小时 |
| 🟢 P2 | 参考文献格式统一 | 30分钟 |
| 🟢 P2 | 数字/单位格式统一 | 15分钟 |

---

> 📌 **建议：** 优先完成 P0 项（公式缺失、重复内容、附录空白），这些是明显的硬伤。P1 项（Chapter 5改写）对评分影响最大。P2 项属于格式细节，可在最终排版阶段处理。
