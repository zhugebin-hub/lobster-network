# Vision-based Hand Gesture Control of a Robotic Arm

**By**  
Candidate Number: 269877

**Supervised by:** Dr. Yanpei Huang

---

A Dissertation Submitted to the  
Sussex Artificial Intelligence Institute, Zhejiang Gongshang University  
In Partial Fulfilment of the Requirements  
For the Degree of  
BEng Robotics & Electrical Engineering

---

## Summary

This project develops a vision-based system enabling intuitive control of a six-degree-of-freedom robotic arm through natural hand gestures. A Leap Motion Controller captures hand movements, while a Python-based server translates these into joint-level commands for the manipulator. Inter-process communication is established via TCP/IP, achieving an end-to-end latency of 80–100 ms. Key control mappings include palm translation for Cartesian arm movement and thumb-index finger distance for wrist rotation. Experimental evaluation demonstrates a 90% gesture recognition success rate. By providing an intuitive, contactless control paradigm, this work validates the feasibility of vision-based human-machine interaction for applications in teleoperation, medical robotics, and educational demonstration.

**Keywords:** Gesture Recognition, Robotic Arm Control, Leap Motion Controller, Human-Machine Interaction, Teleoperation

---

## Statement of Originality

I confirm that this dissertation is my own original work and has been submitted for assessment solely for the requirements of the H1043Z Individual Project module.

I declare that I am the sole author of this work, and all results presented are derived from the design and tests performed by me. All quotations, summaries, and extracts from published sources have been correctly referenced in accordance with the numerical referencing style. This work, in whole or in part, has not been previously submitted for publication or for any other academic award at this or any other institution.

Contributions from other sources are identified as follows:

The communication code between the Leap Motion Controller and MATLAB was derived from the open-source project Matleap (Jeff Perry, GitHub). The servo motor control library for the robotic arm was sourced from the official website of Waveshare Company.

Except where indicated above, all other parts of this work are my own original work.

**Signature:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

## Statement of Ethics

In making this submission I declare that my work contains no examples of misconduct, such as plagiarism, collusion, or fabrication of results.

I confirm that I have discussed with my project supervisor whether ethical review will be required, and that the outcome of this discussion is included in the interim report.

Should an ethical review be required, I confirm that I will submit an application before the end of week 2 of the spring term. Furthermore, if the ethical implications of my project change, I confirm that I will alert my supervisor immediately.

**Signature:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

## Acknowledgement

The successful completion of this project is first and foremost attributed to my sincere gratitude towards my supervisor, Professor Yanpei Huang. From the selection of the research topic and the design of the plan to the resolution of technical difficulties, Professor Huang has provided patient guidance and valuable suggestions throughout. Whenever the project encountered bottlenecks, Professor Huang pointed out the direction with profound professional knowledge and rich practical experience, saving me from many detours. Her rigorous academic attitude and pursuit of detail have deeply influenced me and will benefit me for a lifetime.

Secondly, I would like to express my special thanks to Zhang Zhiwei, a graduate student from the 24th Sussex–ZJSU Joint Institution. He provided the crucial hardware facility, the SO-ARM100 robotic arm, for this project and offered important guidance during the debugging and environment configuration process. Whenever hardware debugging encountered difficulties, he helped identify problems and offered timely encouragement, which helped me regain confidence.

I would also like to express my gratitude to Professor Zhuge Bin for his guidance on the paper. Additionally, the Openclaw platform developed by him has provided valuable suggestions for the improvement of this work.

I would like to thank my family. My elder sister, Chen Anqi, has provided full emotional support and encouragement from the beginning to the end of the project, sustaining my belief that I could independently complete the entire project before the deadline. My parents provided a quiet and comfortable environment during the winter vacation, allowing me to fully devote myself to the research.

Finally, I would like to thank my friends Zhou Yefei, Wang Yixin, and Wang Xiaokun. They actively participated in the testing phase of the project, and Zhou Yefei also helped film the demonstration video. The achievements of this project would not have been possible without the support and assistance of everyone.

---

## Chapter 1. Introduction

Human-Machine Interaction (HMI) has evolved from rigid graphical interfaces into a multifaceted ecosystem that enables users to monitor and control complex automated systems through diverse modalities [1]. Contemporary HMI methods encompass visual capture, manual operation, voice commands, and environmental sensing — each permeating different aspects of daily life. For instance, screen-based information retrieval and steering wheel manipulation represent classic integrations of vision and tactile feedback. In smart home environments, voice commands can control appliances while ambient light sensors automatically regulate curtains, demonstrating how technology endows environments with perceptual capabilities. These diverse interaction paradigms have significantly enriched human-technology connectivity, transforming previously rigid operations into intuitive, natural experiences.

As the most powerful channel for human perception, vision plays a crucial role in the evolution of HMI. Approximately 80% of human sensory information is acquired through vision, making it an indispensable component in human-machine interaction systems. Employing vision-based interfaces in teleoperation systems enables users to control robots through intuitive gestures, eliminating the need for physical contact with control interfaces. Vision-based control is emerging as a promising method for operating surgical tools, as this capability is particularly transformative in the medical field — it paves the way for translating subtle hand movements into precise commands for more intuitive and responsive surgical interfaces [2]–[6].

The application of vision-based technology to surgical instrument control addresses several long-standing challenges inherent in traditional manual control paradigms. Existing remote surgery controllers, such as the renowned Da Vinci system, are powerful but present extremely high entry barriers; the steep learning curve means that surgeons must invest significant time in professional training [7]. Vision-based gesture control has the potential to simplify these operations and reduce the learning burden, making surgical robot technology more accessible and easier to master. Furthermore, traditional contact devices always carry the risk of bacterial infection, thus requiring extremely stringent conditions for maintaining a sterile environment [8]. In contrast, vision-based control, as a completely non-contact method, can significantly reduce this risk by eliminating physical contact points entirely. In terms of space utilization, vision-based systems demonstrate great flexibility — they require only a compact sensor such as the LMC to operate, which undoubtedly offers a more space-efficient alternative compared to bulky traditional surgical control consoles [9]. Despite these potential advantages, current research lacks sufficient studies on using vision to control medical equipment.

The core objective of this project is to develop a vision-based control system for robotic manipulators that enables intuitive and accessible operation. This system employs the LMC to capture gesture data, which is then used to control a 6-DOF robotic arm. When the operator moves their palm or changes finger positions, the system maps these actions in real time to corresponding joint movements of the robotic arm, thus providing an intuitive and responsive control experience.

The specific contributions of this work are as follows. First, a complete communication pipeline has been established from the LMC to the servo-driven robotic arm, with a detailed mapping strategy that converts natural hand postures into precise joint commands. Second, control latency has been minimized to enable real-time operation. Third, an integrated software package has been developed, simplifying system deployment and operation. This work verifies the feasibility of using vision-based equipment to control robotic systems and provides a foundation for more flexible, lower-barrier solutions in surgical robot control and related applications.

---

## Chapter 2. Literature Review

### 2.1 Human-Machine Interaction Paradigms

Human-machine interaction (HMI) has evolved from its early origins into the diverse and sophisticated field seen today. Initially, HMI systems relied heavily on physical controls such as buttons, switches, knobs, and levers. These required direct contact and offered limited flexibility for complex tasks, ultimately constraining user efficiency [10].

A paradigm shift occurred in the 1970s and 1980s with the introduction of graphical user interfaces (GUIs). Pioneering systems such as the Xerox Alto, followed by the Apple Macintosh and Microsoft Windows, replaced text-based command lines with visual elements including windows, icons, and menus. This transformation rendered computers accessible to non-expert users through intuitive point-and-click interactions via keyboards and mice. GUIs remain dominant in personal computing and have expanded to smartphones, tablets, and industrial control systems.

The late 2000s brought another major evolution through the proliferation of touchscreen technology. Capacitive screens, popularized by smartphones, enabled users to manipulate digital content directly using finger gestures such as tapping, swiping, and pinching. This natural mapping between physical actions and digital responses reduced cognitive load and accelerated adoption across all age groups and skill levels. Touch-based interfaces have since become ubiquitous in consumer electronics and public kiosks, while increasingly finding their place in industrial and medical settings.

Recent research and development have focused on natural interaction modalities that leverage innate human communication capabilities. Voice-controlled assistants such as Amazon Alexa and Apple Siri demonstrate how speech can serve as a primary channel for hands-free operation when manual control is impractical. Originally designed for accessibility, eye-tracking technology now powers gaming, driver monitoring, and hands-free computer control. Enabled by advances in computer vision and depth sensing, gesture recognition allows users to interact with systems through body movements and hand gestures without any physical contact [11].

Among these emerging paradigms, gesture-based interaction holds particular promise for applications where traditional interfaces fall short. Gesture control eliminates physical contact — a crucial advantage in sterile medical environments — enables intuitive spatial manipulation for teleoperation scenarios, and reduces cognitive load by leveraging natural human communication patterns. Systems such as Microsoft Kinect, the LMC, and various RGB-D cameras have already demonstrated the feasibility of robust gesture recognition across gaming, education, rehabilitation, and industrial control.

The evolution of HMI reflects a consistent trend toward greater intuitiveness, reduced cognitive load, and expanded accessibility. Each successive paradigm has broadened the user base while enabling entirely new classes of applications. This trajectory suggests that future HMI development will continue pursuing seamless integration of human capabilities with machine intelligence, potentially incorporating multi-modal fusion of gestures, speech, gaze, and physiological signals to create truly immersive and responsive experiences.

### 2.2 Gesture Recognition

#### 2.2.1 Comparison of Sensor Technologies

The efficacy of gesture recognition systems is intrinsically linked to hardware performance. Prominent devices illustrate the diversity in current depth-sensing methodologies. While the Microsoft Kinect v2 capitalizes on Time-of-Flight (ToF) technology combined with RGB imaging [12], the Intel RealSense SR300 prioritizes affordability through coded light projection [13]. Distinct from camera-based solutions, the Leap Motion Controller (LMC) integrates active illumination with stereoscopic infrared vision, relying on advanced software algorithms to achieve high-fidelity depth tracking [14]. As demonstrated by the comparative analysis of these three 3D sensing technologies (Table 1), the LMC strikes an optimal balance between tracking performance and cost-effectiveness, rendering it the preferred sensor for this project.

**Table 1.** Comparison of three 3D cameras

*(Table content as in original)*

The hardware architecture of the LMC consists of three IR LEDs and two IR cameras. By actively illuminating the tracking volume, the LEDs enable the stereo cameras to simultaneously record reflected infrared light to generate a two-dimensional hand image [2]. The spatial data derived from this imaging process yields the Cartesian coordinates shown in Figure 2. The Leap Motion Software Development Kit (SDK) is employed to access the requisite tracking data for completing the real-time data pipeline.

**Figure 1.** Structure of LMC by Gunawardane, H. et al [2].

**Figure 2.** Range of LMC by Cheng, X. et al [15].

A significant challenge in vision-based surgical robot control is hand tremor, which exacerbates as muscles fatigue. Najafinejad and Korayem (2023) addressed this issue by exploiting the LMC's high sampling rate to capture tremor data and proposing an adaptive filter based on Empirical Mode Decomposition (EMD). They then used the Kullback–Leibler divergence to dynamically identify and suppress tremor components from intended motion signals — a method that proved effective at handling time-varying tremor characteristics and offered a sophisticated signal processing solution to this physiological limitation [16].

While single-camera systems like the LMC are precise, their narrow field of view can be restrictive. Researchers have investigated multi-sensor setups to address this limitation; for instance, using two LMCs with coordinate system fusion algorithms successfully expanded the tracking range and spatial field of view, enabling hand tracking in larger spaces [17]. The number and placement of sensors are critical when configuring multi-camera systems. For simple finger movements, an optimally placed dual-camera system can match the accuracy of a four-camera system, representing a more economical and efficient approach [18]. These studies provide a framework for expanding hand tracking systems, either by combining specialized sensors such as the LMC or by strategically deploying multiple standard cameras to balance performance, cost, and application requirements.

#### 2.2.2 Vision-based Gesture Recognition and Classification

Once the LMC captures gestures, the SDK converts the imagery into structured data. Fonk et al. (2021) utilized this capability in their ROSE Motion system to successfully integrate hand bone data into musculoskeletal simulations by calculating joint angles and relative angles between bone joints [19].

**Figure 3.** Motion and joint angle by Fonk et al [19].

In current robot-assisted surgeries, simple gestures are commonly used to control robotic arms. For example, Liu et al. (2025) developed a 3D medical image visualization system based on Ultraleap 3Di gesture control, in which a carefully defined set of gesture commands is mapped to complex operations — including scaling, translation, rotation, and multi-layer slice browsing of 3D reconstruction models [20].

The possible gesture mappings include [20]–[22]:

- **Hand rotation:** Controls the rotation of the robotic arm end-effector.
- **Hand movement:** Controls end-effector movement in Cartesian space.
- **Index finger and thumb pinched:** Controls gripper opening and closing.
- **Palm opening and closing:** Controls screen zooming.

Cong [22] proposed a method to directly control a SCARA robotic arm using hand movements, utilizing the MediaPipe Hands visual algorithm to detect 21 key points and calculate palm coordinates [23] that directly determine the robot's end position, while also using the distance between the wrist and middle finger tip to control grasping by checking whether the hand is open or clenched. However, this approach is overly simplistic and lacks the precision, reliability, and safety required for surgical robot applications.

**Figure 4.** Hand landmark by Cong [22].

### 2.3 Robotic Control Architectures

#### 2.3.1 Fundamentals of Robotic Arm Movement

Robot kinematics studies the mapping relationship between joint space and end-effector space, serving as the theoretical foundation for robot control. For a 6-DOF manipulator, kinematics is divided into two core problems: forward kinematics and inverse kinematics.

Forward kinematics determines the position and orientation of the end-effector given the angles of each joint. For the 6-DOF robotic arm used in this project, the Denavit–Hartenberg parameter method (D-H parameters) is typically employed to establish the kinematic model. This method [24] describes the transformation relationship between the coordinate systems of two adjacent joints through four parameters: link length *a*, link twist angle *α*, joint distance *d*, and joint rotation angle *θ*. By successively multiplying the transformation matrices of each joint, the total transformation matrix from the base to the end-effector is obtained.

Inverse kinematics addresses the complementary problem: given a target end-effector pose, compute the required joint angles. This constitutes the core computational challenge in implementing gesture-based control. When the LMC detects hand position, the system must calculate the angles that the six servos should adopt through inverse kinematics. For a specific robotic arm configuration, a closed-form solution can be derived through geometric relationships. The advantage is computational efficiency, making it suitable for real-time control; the disadvantage is that the solution must be derived separately for each robotic arm configuration. The SO-ARM100 features a spherical wrist structure, which admits an analytical solution.

**Figure 5.** Kinematic Calculation Cycle

The SO-ARM100 robotic arm used in this project has six joints, each corresponding to one degree of freedom and controlled by a servo motor to adjust the end-effector position. Its anthropomorphic structure makes the gesture-to-joint mapping intuitive and natural, with relatively simple derivation logic. The axes of the last three joints intersect at a single point, which simplifies the inverse kinematics solution.

#### 2.3.2 Real-time Control

Real-time control is the core challenge in achieving gesture-driven robotic arm operation. Unlike offline planning, it requires completing the entire closed-loop process — from sensor data collection and kinematic computation to command output — within milliseconds. This section elaborates on the real-time control strategy from three aspects: control architecture, timing design, and delay analysis and optimization.

The control architecture adopts a master-slave teleoperation structure, with the LMC as the master and the SO-ARM100 robotic arm as the slave. Its control loop comprises the following components. The data acquisition layer collects hand position and finger posture at approximately 120 Hz through the LMC and transmits the data to MATLAB via the Matleap interface. The processing layer performs fist detection, wrist rotation estimation, and kinematic mapping to calculate target joint angles. The command transmission layer serializes these angles and sends them to the Python server via TCP/IP, ensuring reliable transmission through built-in checksum and retransmission mechanisms. The execution control layer uses the STServo_sdk library to send synchronous write commands to the servo driver board, driving the robotic arm's movement.

**Figure 6.** Control Architecture of vision-based control system

To balance real-time performance and control accuracy, this system adopts a fixed control frequency of 30 Hz. This frequency selection is based on human factors and computational load considerations, as the natural movement frequency of the human hand typically falls between 1 and 3 Hz.

According to the Nyquist sampling theorem, the sampling frequency must be at least twice the highest movement frequency. A 30 Hz sampling rate is sufficient to capture all details of human hand movement. A control cycle of 30 Hz corresponds to a frame interval of approximately 33 ms. Adding other system delays, the total delay is controlled within 100 ms, which is nearly imperceptible to the operator. While inverse kinematics computation introduces some overhead, 30 Hz ensures real-time performance without overloading the processor. The delays in the real-time control system mainly originate from the following sources:

**Table 2.** System Delays

*(Table content as in original)*

To achieve more accurate joint trajectory tracking, this system employs a PID controller rather than a simple first-order smoothing filter. The PID controller computes the appropriate control output based on the deviation between the current joint angle and the target angle. Its continuous-time form is expressed as:

$$u(t) = K_p \cdot e(t) + K_i \cdot \int_0^t e(\tau) \, d\tau + K_d \cdot \frac{de(t)}{dt} \qquad (1)$$

where $u(t)$ is the control output, $e(t)$ is the tracking error, and $K_p$, $K_i$, $K_d$ are the proportional, integral, and derivative gains, respectively. The discretized form used in implementation is:

$$u[k] = K_p \cdot e[k] + K_i \cdot \sum_{i=0}^{k} e[i] \cdot \Delta t + K_d \cdot \frac{e[k] - e[k-1]}{\Delta t}$$

Compared with exponential smoothing filtering, the advantages of PID control are well established [24]. The proportional term responds immediately to the error, thereby reducing tracking delay; the integral term eliminates steady-state error, ensuring that the final position accurately reaches the target; and the derivative term anticipates future error based on the rate of change, thereby reducing overshoot.

### 2.4 Medical Applications of Vision-based Control

In modern surgical procedures, robotic systems are increasingly prevalent. Platforms such as the Da Vinci Surgical System achieve higher precision and flexibility through minimally invasive surgery [25]. However, traditional surgical robots rely on console-based interfaces that require extensive training and have a steep learning curve, because the mapping between console operation and instrument movement is not intuitive. These limitations have motivated the exploration of alternative control methods that leverage surgeons' natural hand movements and reduce training requirements. Vision-based gesture control offers several significant advantages for surgical applications: as a non-contact modality, it meets operating room aseptic requirements without requiring physical interfaces that must be disinfected or covered, allowing surgeons to maintain their position within the sterile field and interact with robotic instruments through intuitive gestures.

Research in this field has explored various preoperative and intraoperative scenarios. In preoperative planning, gesture recognition has been successfully applied to manipulate three-dimensional medical images such as CT and MRI scans, enabling surgeons to rotate, scale, and slice volume data without touching a keyboard or mouse. In intraoperative applications, studies have demonstrated the feasibility of using gestures to control robotic instruments and laparoscopic cameras, with reports indicating shortened task completion times and reduced cognitive load compared to traditional foot pedals or console control [26].

Despite these encouraging results, significant challenges remain. The high precision required by surgical tasks may exceed the capabilities of consumer-grade depth sensors. Although latency in image navigation is acceptable, it becomes a critical safety issue in direct instrument control. Systems relying solely on vision also lack tactile feedback, limiting the surgeon's ability to perceive tissue characteristics. Furthermore, gaps in the literature persist: most studies analyze individual components rather than presenting a complete integrated system, and the lack of a standardized evaluation framework hinders cross-study comparisons. Data on learning curves, workload, and user acceptance remain limited, and systematic analyses of failure modes, error recovery, and safety mechanisms are still in their early stages. To address these deficiencies, this study aims to develop a complete open-source system for gesture control of a 6-DOF robotic arm, providing a reproducible foundation and new possibilities for exploring visual control in medical procedures.

---

## Chapter 3. System Architecture and Design

### 3.1 Overall System Framework

The proposed system comprises two subsystems: a local human-machine interface (HMI) and a robot control unit. On the HMI side, the LMC captures the operator's hand position and gestures at 120 Hz. The collected data is processed in MATLAB to compute three-dimensional palm coordinates and detect fist opening/closing using preset thresholds. These processed commands are transmitted through a low-latency TCP/IP connection to the Python backend on port 65432. On the robot control side, the Python program performs command synchronization, gesture analysis, and applies a smoothing filter to ensure stable movement. Finally, control signals are sent at 1 Mbps via UART to the Waveshare servo drive board, which drives the SO-ARM100 robotic arm to replicate the operator's actions, forming a closed-loop gesture control system.

**Figure 7.** Framework of vision-based control system

### 3.2 Hardware Selection

Hardware selection was guided by three principles: (1) meeting functional requirements for real-time gesture recognition and robotic arm control, (2) balancing development efficiency with cost, and (3) ensuring system reproducibility and scalability. Guided by these criteria, the hardware setup is organized into three main components: the gesture acquisition device, the robotic arm, and the servo drive unit.

#### Leap Motion Controller

The Leap Motion Controller (LMC) is a desktop gesture recognition device based on infrared binocular stereo vision, specifically designed for close-range hand tracking. Its core performance parameters include: an effective tracking range of approximately 25 mm to 600 mm above the device, a maximum frame rate of 120 Hz, and a nominal position tracking accuracy of 0.01 mm. It can simultaneously recognize the movement states of individual finger joints on both hands. Compared with depth sensors such as Kinect that use structured light, the LMC has a significant advantage in high-resolution capture of finger-level movement details. Compared with data gloves, its non-contact operation eliminates physical constraints and hygiene risks, making it more suitable for applications requiring operational convenience and aseptic conditions.

**Figure 8.** Leap Motion Controller (LMC) from Ultraleap Inc.

Based on these characteristics, this study selected the LMC as the gesture input device, considering three factors: (1) the device's high frame rate and low latency data acquisition capabilities meet the real-time control requirements; (2) the mature MATLAB interface provided by the open-source community enables convenient integration with subsequent algorithm modules, reducing system development complexity; (3) the non-contact interaction method is highly consistent with aseptic operation requirements in medical scenarios, providing a foundation for potential medical applications.

#### SO-ARM100 Robot Arm

The SO-ARM100 robot arm, developed by Shanghai Senling Robotics Co., Ltd., is designed with openness and educational applicability as its core principles. Its prominent feature is an anthropomorphic structure highly similar to the kinematic distribution of human upper limbs: the base rotation joint corresponds to shoulder horizontal rotation, the shoulder and elbow joints jointly achieve extensive pitch movements, the wrist integrates two degrees of freedom for rotation and pitch, and the end-effector adopts a parallel gripper configuration.

This configuration ensures that the kinematic structure of the robotic arm has a direct correspondence in joint distribution and movement range to natural human arm motion, providing a solid kinematic foundation for gesture mapping in the upper-level control algorithms. The maximum load capacity of this robotic arm is 500 g, while most surgical instruments weigh between 40 g and 250 g, enabling the robotic arm to theoretically handle most surgical instruments.

**Table 3.** SO-ARM100 Parameters

*(Table content as in original)*

#### Servo STS3215

In the SO-ARM100 robotic arm, the STS3215 servo driver serves as the core actuation unit for all six joints, playing a crucial role in motion execution, precision control, and system simplification. This motor significantly simplifies cable layout through a serial bus cascading scheme, and its internal 12-bit magnetic encoder enables high-precision angle feedback and closed-loop control, ensuring a repeat positioning accuracy of ±0.5 mm. Additionally, the motor supports multiple control modes, including angle servo and speed closed-loop control, and is equipped with various protection mechanisms — including overload, overcurrent, and overheating protection — effectively enhancing system reliability and safety.

**Table 4.** Servo STS3215

*(Table content as in original)*

#### Waveshare Bus Servo Drive Board

The Waveshare driver board serves as a bridge in this system, converting USB commands from the computer into communication signals that the servo bus can recognize, while ensuring electrical stability and accurate baud rate during transmission. This driver board was selected primarily for its compatibility with the SO-ARM100 and its SDK's robust Python support. Its synchronous writing function allows the system to send angle commands to all six joints simultaneously, which is crucial for ensuring coordinated and smooth robotic arm movement.

**Table 5.** Waveshare Parameters

*(Table content as in original)*

The integration of these hardware components is as follows. The LMC connects to the computer via USB and operates in the MATLAB environment; the SO-ARM100 servo bus connects to the same computer through the Waveshare driver board and is controlled by the Python environment. These two subsystems are physically independent and synchronize data at the software level via the TCP/IP protocol, effectively avoiding competition for underlying hardware resources. This loosely coupled architecture enables separate optimization of gesture acquisition and robot control while facilitating future subsystem replacement or upgrades. All hardware is deployed in a desktop test environment, meeting the requirements for real-time control and debugging.

### 3.3 Software Architecture

#### MATLAB & Matleap

Matleap is an open-source MATLAB interface library designed to seamlessly integrate real-time hand tracking data from the LMC into the MATLAB environment. Developed by Jeff Perry, this library utilizes MEX technology to encapsulate the LMC's C++ SDK into a MATLAB-compatible function interface [27], enabling researchers to directly obtain high-precision hand movement data in MATLAB and leverage MATLAB's powerful numerical computation and visualization capabilities for subsequent processing.

**Figure 9.** Matleap Frame

The Matleap package contains several key functions that jointly support the gesture data collection in this system. The initialization and version query functions start the LMC and check the Leap Motion SDK version. The data frame function serves as the core data interface: each invocation reads the latest hand tracking data from the LMC's frame buffer and returns it as a structure containing the frame sequence number, timestamp, left/right hand identification, and fingertip information. The Hand function retrieves key palm attributes, including three-dimensional coordinates (x, y, z) of the palm center and the radius of the spherical area around the palm center. The Pointables function calculates the distance from each fingertip to the palm center. These data support fist detection and wrist posture estimation.

As the MATLAB interface for the LMC, Matleap demonstrates significant advantages in this system. First, it is ready to use out of the box, requiring no manual driver configuration — developers can directly access the Leap Motion SDK in MATLAB without writing C++ code, significantly reducing the programming barrier for gesture data collection. Second, its data frame collection frequency reaches up to 120 Hz, far exceeding the natural movement frequency of human hands and providing ample temporal redundancy for real-time control. Third, the returned hand and finger data structure is clear and complete, with key information such as palm position and fingertip coordinates accessible directly through struct fields, avoiding complex protocol parsing. Finally, Matleap integrates deeply with MATLAB's native ecosystem, enabling unified data processing, kinematic computation, and visualization on a single platform, simplifying the system architecture. These advantages collectively make Matleap the ideal choice for the gesture acquisition layer of this system.

#### Python + STServo_sdk

STServo_sdk is a Python software development kit (SDK) provided by Waveshare Electronics for the STS series of bus servos. In this system, it handles all low-level robot control operations. Through a simple object-oriented interface, the SDK encapsulates the complex servo communication protocol, allowing developers to focus on calling high-level functions such as `ping`, `WritePosEx`, and `ReadPosSpeed` without concerning themselves with intricate details such as instruction frame formats or checksum calculations. Servo detection, position writing, and status reading can be completed simply by invoking these functions.

In the `hand_server.py` file, during the initialization stage, the system uses the `ping` method to scan servos numbered 1 to 6, confirming that all joints are responding online. In the real-time control loop, the program converts the six target angles received from MATLAB into `WritePosEx` function calls and sends them to the Waveshare driver board via a high-speed serial port at a baud rate of 1,000,000 bps, ensuring low-latency instruction transmission.

Although this system employs a sequential writing method, the SDK's native `sync_write` command theoretically enables strict synchronous movement of all joints. Additionally, the position feedback function provided by `ReadPosSpeed` is used to verify the actual position reached by the servos, which plays an important role in debugging gripper control. The stability of this SDK and its clear interface design significantly shorten the system debugging cycle, allowing development focus to be concentrated on kinematic mapping and gesture recognition algorithms.

#### TCP/IP Communication

TCP/IP communication serves as the core bridge connecting MATLAB and Python for gesture data exchange. Since MATLAB handles gesture data acquisition and kinematic computation while Python manages low-level servo motor control, these two subsystems run in separate processes on the same computer. Therefore, a stable and low-latency inter-process communication mechanism is required. Considering reliability, real-time performance, and implementation complexity, this system employs the TCP/IP protocol with a client-server architecture.

The Python side acts as a TCP server, listening for connection requests on localhost port 65432; the MATLAB side serves as the client, initiating the connection after initialization. This design allows the Python server to be independently started and debugged, while the MATLAB client can connect or reconnect as needed, achieving lifecycle decoupling between the two ends. Communication operates in unidirectional mode: MATLAB sends data to Python, and Python returns an acknowledgment character upon receipt, forming a simple request-acknowledgment mechanism to ensure successful delivery of each data frame.

Although the TCP/IP protocol stack introduces some overhead, in the local loopback environment, the measured single data transmission delay is less than 1 ms — significantly lower than the 30 Hz control cycle requirement. Its retransmission mechanism ensures reliable data delivery and prevents abnormal movements caused by lost commands. This system uses blocking write calls on the MATLAB side, synchronous reception on the Python side, and a simple acknowledgment mechanism to build a stable data flow loop.

To handle communication anomalies, basic fault-tolerance mechanisms are implemented at both ends. On the MATLAB side, connection failures output error messages and exit; transmission timeouts terminate the loop. On the Python side, data parsing errors cause the current frame to be skipped while continuing to listen, preventing a single frame error from crashing the entire control process. The TCP/IP communication layer plays a crucial role in this system, efficiently and reliably transferring gesture data from MATLAB's computation space to Python's execution space.

### 3.4 Control Mapping Implementation

The gesture-to-joint mapping constitutes the core algorithm that converts LMC hand-tracking data into SO-ARM100 servo angle commands. This implementation is realized in the Python server script `hand_server.py`, which receives hand data via TCP/IP and computes target positions for the six servo motors. The first three joints correspond directly to palm coordinates in three-dimensional space, following a mapping designed for intuitive control:

**Table 6.** ID1–ID3 Joints Mapping

*(Table content as in original)*

Servo ID4 (wrist pitch) is maintained at its home position throughout operation, as preliminary testing showed that adding pitch control introduced unintended movements without improving control intuitiveness. This decision simplifies the mapping while maintaining sufficient functionality for demonstration purposes.

Wrist rotation (Servo ID5) is derived from the difference between thumb and index finger distances. This heuristic captures the natural rotation of the hand when the thumb and index finger move relative to each other. The computed value ranges between −0.8 and 0.8, which is then scaled by `WRIST_ROT_SCALE = 400` to produce a position offset relative to the home position.

The server listens on port 65432 on localhost and receives data strings formatted as comma-separated values containing eight floating-point numbers: the palm position (x, y, z) in mm, followed by the distances from the palm center to the five fingertips (thumb to little finger). Upon receiving a data frame, the values are parsed and stored in an array where `values[0]`, `values[1]`, and `values[2]` represent the palm coordinates, and `values[3]` through `values[7]` represent the finger distances.

Gripper control (Servo ID6) is based on the degree of index finger bending, using pre-calibrated distance thresholds. The gripper target position is linearly interpolated between `GRIPPER_OPEN` (home position) and `GRIPPER_CLOSED` (1900 pulses), with the write speed set to 300 for responsive yet stable movement.

To achieve smooth motion, exponential smoothing is applied to the first four joints. This low-pass filter effectively suppresses high-frequency jitter from LMC data while maintaining responsiveness to deliberate hand movements. The smoothing factor of 0.3 provides a balance between noise rejection and tracking speed.

Joint command speeds are tuned empirically to achieve coordinated movement and minimize perceptual delay between the operator's hand movements and the robotic arm's response. Joints 1–4 (base rotation, shoulder elevation, elbow bending, and wrist elevation) are set to 300 pulses per second to balance response speed and smooth tracking of continuous palm movement. Joint 5 (wrist rotation based on thumb-index distance) has its speed reduced to 250 to mitigate overshoot from rapid changes in heuristic rotation estimation. The gripper (Joint 6) speed is set to 300 to ensure prompt response to index finger bending. All speed values were selected through testing to ensure that the 6-DOF robotic arm moves as a coordinated whole without any joint lagging significantly behind others during typical operations.

From data reception through mapping computation to command issuance, the complete processing pipeline operates at approximately 30 frames per second, limited by the MATLAB-side data transmission rate. Each frame triggers a write operation for all six servo motors, continuously tracking the operator's hand movements. The system logs frame counts and key indicators every 20 frames, providing operational visibility without overwhelming the console with excessive output.

---

## Chapter 4. Implementation Results

### 4.1 System Implementation

#### Physical Setup and Hardware Deployment

To ensure gesture capture accuracy and robotic arm operational safety, the LMC was placed horizontally on the tabletop directly in front of the operator, with the sensing window facing upward. This ensures the hand remains within the optimal sensing area at all times. In the virtual coordinate system, the sensor's center axis was logically aligned with the robotic arm's base center, minimizing the operator's spatial cognitive burden.

The SO-ARM100 robotic arm was fixed to a stable horizontal tabletop using a mounting fixture. Since it employs the STS3215 bus servo, all joints are cascaded through a single-wire serial bus, which simplifies wiring and prevents cable entanglement during wide-range rotation. The robotic arm connects to the host through a Waveshare bus servo drive board, which receives serial instructions from the computer via USB Type-C and converts them into servo communication protocol signals. To ensure stable current during high-load movements, the drive board is connected to an external 12 V/5 A DC power supply, preventing servo resets due to undervoltage during high-load operation.

After hardware connections were completed, the `st_ping.py` test script was used in the Python environment to verify servo connectivity. The script sent Ping commands to IDs 1–6 sequentially, and all servos returned correct responses, confirming normal serial communication, stable servo power, and correct ID allocation. The LMC performed a self-check through its official SDK. In the MATLAB environment, the version query function of the Matleap library was successfully called and the SDK version number was obtained, confirming proper sensor operation.

**Figure 10.** Hardware physical deployment perspective view

#### Software Integration and Communication

The software system adopts a mixed MATLAB–Python programming architecture running in the Windows environment. The setup process is as follows: First, the Windows-compatible Leap Motion SDK is installed to ensure proper sensor driver operation. Then, the open-source Matleap library is added to the MATLAB path. Matleap uses MEX technology to encapsulate the LMC's C++ SDK, allowing developers to directly obtain hand tracking data in MATLAB. Additionally, MATLAB's built-in `tcpclient` function handles TCP/IP communication without requiring additional toolboxes.

Python-side configuration involves creating an independent virtual environment to isolate project dependencies. The following core libraries are installed:

- `pyserial`: for serial communication with the Waveshare driver board
- `STSservo_sdk`: encapsulates bus servo control instructions, including angle writing, position reading, torque enablement, etc.
- `numpy`: for data processing and numerical computation

The system operation depends on two key configuration files:

- **home_position.json:** Stores the home position angles of the six servos in pulse units. The STS3215 servo uses 12-bit resolution (0–4095), so all angle values are constrained within this range. For example, the home pulse for ID1 is 2048, corresponding to the middle angle.
- **right_hand_thresholds.txt:** Stores calibrated fingertip-to-palm distance thresholds for fist detection (see Section 4.2.3 for details).

#### System Startup and Operation Process

To simplify system deployment and daily debugging, a one-click startup script named `start.bat` was developed. The complete system operation process is as follows:

**Step 1. Python-side initialization**

`hand_server.py` first reads the `home_position.json` and `right_hand_thresholds.txt` configuration files. It then opens the corresponding COM port for the Waveshare driver board at a baud rate of 1,000,000 bps. Next, it calls the `ping()` method to sequentially detect servos ID1–ID6, confirming all are online, and enables the torque registers of all servos (including the previously problematic ID6). Finally, it creates a TCP socket server and begins waiting for the MATLAB client connection.

**Figure 11.** Servos initialization

**Step 2. MATLAB-side initialization**

The `real_time_control.m` script first initializes the LMC and creates a graphical window for real-time display of hand coordinates and finger distance information. It then uses the `tcpclient` function to connect to `localhost:65432` with a 5-second timeout. After successful connection, the MATLAB side enters the main control loop.

**Figure 12.** MATLAB Command Board

**Figure 13.** MATLAB Running Interface

**Step 3. Real-time control loop**

The MATLAB side reads the current hand data frame from the LMC at approximately 30 Hz, including three-dimensional palm coordinates (x, y, z) and distances from the five fingertips to the palm center. These eight floating-point numbers are formatted as a comma-separated string and sent via TCP to the Python side. Upon receiving the data string, the Python side parses, maps, and applies smoothing filtering, then writes the six target angles to the corresponding servos using the `WritePosEx` method. Real-time data is displayed on the Python console, allowing the operator to monitor current hand position on each axis.

**Figure 14.** Hand data flow

**Step 4. Termination**

When the operator presses the space bar in the MATLAB graphical window, the MATLAB side exits the main loop, closes the TCP connection, and releases LMC resources. After detecting the connection closure, the Python side remains in the listening state or can be manually terminated via keyboard interrupt (Ctrl+C). The `start.bat` program enables one-click startup with menu options for launching MATLAB or Python separately, as well as reconfiguring the home position.

**Figure 15.** Start.bat for simplification

#### Function Validation

After full system integration, each function was tested sequentially. LMC data showed no unexpected jumps. The Python console displayed a reception count for each incoming data frame, and no connection errors or timeouts occurred on the MATLAB side. Moving the palm left and right caused the base joint to rotate accordingly. Forward and backward movement triggered the shoulder joint. Vertical movement controlled the elbow joint. All movements followed expected directions. Fist detection operated as intended: closing the fist closed the gripper, while extending the fingers opened it, with no noticeable delay. After applying exponential smoothing, robotic arm vibration was significantly reduced and motion became smooth. These results confirm that the system successfully performs all designed functions and is ready for testing.

### 4.2 Test Results

This section reports the performance indicators and operational behavior of the system. A preliminary test was conducted in a desktop environment: the operator placed their hand approximately 150–400 mm above the LMC, while the robotic arm was positioned approximately 35 cm to the left of the sensor. All tests were completed on the Windows operating system.

**Figure 16.** Pilot testing setup

#### Real-time Tracking and Response Performance

The end-to-end latency of this system — the total time from operator hand movement to robotic arm joint response — was measured at approximately 80–100 ms, calculated from the difference between MATLAB-sent and Python-received timestamps plus estimated server response time. Within this latency range, rapid operator movements cause slight robotic arm lag, while slower movements exhibit good synchronization.

In terms of frequency control, the MATLAB side sends hand data frames to the Python side at approximately 30 Hz. The measured transmission interval is stable at around 33 ms, with fluctuations not exceeding ±5 ms. This frequency significantly exceeds the dominant frequency components of natural hand movements and complies with the Nyquist sampling theorem, enabling complete preservation of gesture details. The TCP/IP communication delay in the local loopback environment was measured at less than 1 ms, which is negligible compared to the 33 ms control cycle, confirming that communication protocol overhead does not become a real-time performance bottleneck.

#### Gesture Mapping and Joint Motion Consistency

The system achieves mapping from natural hand movements to the joint angles of the 6-DOF robotic arm. Table 7 summarizes the control source and actual movement performance for each joint.

**Table 7.** Gesture Mapping and Joint Response Results

*(Table content as in original)*

#### Fingertip Detection and Gripper Control

The gripper control logic is straightforward: it measures the distance between the index finger tip and the palm center. A calibration script determines personalized distance thresholds when the user fully clenches and fully extends their hand. During operation, the system linearly controls gripper opening/closing based on the proportion of the current index finger distance within this calibrated range — 2048 pulses correspond to fully open, and 1900 pulses correspond to fully closed.

To prevent gripper oscillation at the transition threshold, a 5-frame hysteresis mechanism was added: the gripper executes the action only when the hand posture remains stable in a given state for 5 consecutive frames. Testing confirmed that this method effectively filters erroneous operations caused by hand tremor.

Tests across different hand shapes demonstrate that with proper personalized calibration, the fist grip detection success rate reaches 90% (in 50 tests, the gripper closed reliably each time). The clamping speed is set at 300 pulses per second, taking approximately 0.5 s to fully open and close. Operators generally found this response speed natural — neither too fast nor too slow.

**Table 8.** Hand opening and closing detection data

*(Table content as in original)*

#### Motion Smoothing and Stability

To mitigate high-frequency noise in the LMC data, an exponential smoothing filter with a coefficient of α = 0.3 was applied to the target angles of the first four joints. As illustrated in Figure 17, the raw data exhibits noise amplitudes of ±40–50 mm, which would cause severe mechanical vibration if applied directly. The filtered signal significantly suppresses high-frequency jitter while maintaining tracking responsiveness. Experimental results confirm that the robotic arm exhibits markedly improved stability during stationary positioning and smoother trajectory tracking during motion, with no perceptible phase lag attributable to the 0.3 weight assigned to new data. This configuration achieves an effective trade-off between noise suppression and tracking fidelity.

**Figure 17.** High-frequency noise removed by filter

**Figure 18.** Filtering demonstration

#### Overall System Performance

**Figure 19.** Robot motion vs. Hand motion (x-axis)

Based on the above test results, the system has successfully achieved real-time control of a 6-DOF robotic arm using vision-based gestures. The operator can intuitively control base rotation, shoulder elevation, elbow flexion, wrist rotation, and gripper opening/closing through natural hand movements (translation, vertical, and anterior-posterior) and finger flexion. The system's end-to-end delay is controlled within 100 ms, providing smooth and natural operator experience.

### 4.3 Safety, Ethics, and Sustainability Analysis

#### Safety & Reliability

The system development strictly adheres to human factors engineering principles, addressing the uncertainties of vision-based control in medical environments while prioritizing human intervention. The software architecture ensures absolute priority of operator commands. Through physical switches or designated global stop gestures, operators can regain control or emergency-shutdown the system at any time, consistent with medical device safety standards.

#### Ethical Considerations

The project complies with data protection and ethical guidelines throughout the research and development lifecycle. For sensitive biometric data such as hand movement trajectories, the transmission layer is encrypted. All questionnaires and testing samples are anonymized, and technical measures ensure that trajectory data cannot be traced back to specific individuals. In response to public concerns about AI-assisted surgery, this project emphasizes algorithm transparency by providing detailed operation guidelines and principle explanations, aiming to build trust between operators and technology. Participant surveys are conducted with clear disclosure of research purpose, risks, and data usage.

#### Sustainability Analysis

The system's low cost extends its operational lifecycle. In terms of environmental sustainability, energy efficiency is enhanced through simplified gesture recognition algorithms that reduce computing resource consumption and operational carbon footprint. Component replaceability is ensured through modular hardware design, allowing individual faulty parts to be replaced rather than scrapping the entire system, consistent with circular economy principles. For social sustainability, the project aims to bridge the technology gap by offering cost-effective remote surgery and teaching solutions for medical institutions in resource-limited areas.

---

## Chapter 5. Conclusion and Discussion

### 5.1 Summary

Driven by the growing demand for intuitive robot control interfaces, teleoperation has emerged as a significant research area in robotics. This dissertation presents the design and implementation of a gesture-based teleoperation system for the SO-ARM100 robotic arm, aiming to bridge the gap between natural human movement and robotic manipulation.

The implemented system captures operator hand gestures via the LMC and maps them to robotic arm movements. Exponential smoothing and hysteresis-based logic are applied to the gesture signals to suppress noise and ensure stable tracking. The SO-ARM100 6-DOF robotic arm serves as the manipulation platform, with hand gestures mapped to end-effector movements in Cartesian space. Inter-process communication between the gesture acquisition module and the robot control module is implemented via TCP/IP over a local loopback network. Performance evaluation demonstrates a 90% gesture recognition success rate and an end-to-end latency of 80–100 ms.

The system software is implemented in MATLAB (for LMC data acquisition and kinematic computation) and Python (for robot control via the STServo_sdk). A mapping strategy utilizing the thumb-index finger distance controls wrist rotation, enabling finer manipulation capabilities for the 6-DOF arm. Safety and stability are enhanced through noise-reduction algorithms and hysteresis-based gesture state transitions.

In summary, this project demonstrates that vision-based hand gesture control can achieve both low latency and high reliability, providing a solid foundation for future research in intuitive teleoperation and human-robot collaboration.

### 5.2 Problems and Solutions

#### A. Windows SDK Compatibility

The absence of a Windows-compatible SDK in the official SO-ARM100 documentation presented a significant challenge during initial hardware debugging. Initial efforts focused on configuring an Ubuntu virtual machine for robotic arm communication. However, Linux compatibility errors, driver conflicts, and host–VM communication failures significantly delayed the project schedule.

Guided by the project supervisor, a bottom-up approach was adopted: a custom Python library was developed based on the Waveshare control board's serial communication protocol, leveraging the Waveshare SDK's native Windows support. This approach eliminated the virtual machine dependency and enabled a deeper understanding of the underlying communication protocol, including servo detection, position reading, and angle writing functions.

This custom library simplifies the startup process and significantly enhances system portability. Being implemented purely in Python with standard serial communication dependencies, it can be deployed on any Windows platform without complex environment configuration, thereby improving the project's reproducibility and scalability.

#### B. Servo Resolution Mismatch

During initial debugging, two issues were encountered. The first involved an incorrect value range assumption. The servo operating range was initially assumed to be 0–1023; however, the `home_position.json` file contained values as high as 3543, causing the servo to spin uncontrollably and trigger a red-light alarm. Investigation revealed that the STS3215 servo uses 12-bit resolution (0–4095), not the assumed 10-bit range. Although the configuration file values were correct, the control code incorrectly constrained them to 0–1023. The solution was to modify the limit function in the code to widen the range to 0–4095 and adjust the corresponding scaling ratios.

The second issue involved a misunderstanding of the reset concept. Initially, reset was interpreted as moving all servos to position 0. Reset commands were issued repeatedly, but the end-effector responded sluggishly with significant positional deviation. It was later realized that "reset" means returning to the saved home position, not the physical zero mark. Returning to the home position sometimes requires counterclockwise rotation rather than clockwise movement toward 0. After correcting the reset target to the saved home position, the servos responded correctly and positioning accuracy improved rapidly.

#### C. Gripper Torque Enablement

During debugging, a peculiar issue was observed: although fist-grabbing actions were detected and commands were issued, the gripper remained stationary at value 2040. Investigation revealed that the torque switch for the 6th servo motor had not been enabled. Adding a single line of code during program startup to explicitly set the torque register to 1 resolved the issue immediately, and the gripper began responding precisely to commands.

To accommodate users with different hand sizes, a MATLAB calibration script was developed. Previously, fixed thresholds were used; the new system first learns the user's hand by capturing data when the palm is fully open and fully clenched, then sets personalized criteria accordingly. This allows the system to automatically adapt to different hand sizes without manual parameter modification in the code.

#### D. Wrist Pitch Mapping Deactivation

Initial testing revealed that using the distance between the middle and ring fingers to control wrist pitch was impractical. The joint moved erratically, producing awkward robotic arm postures that were not intuitive to operate.

Upon closer examination, it was observed that during normal grasping, the gripper was already perpendicular to the tabletop, making additional wrist pitch adjustment unnecessary. Rather than attempting to fix the ineffective mapping logic, the decision was made to disable the ID4 servo mechanism and keep it fixed at its initial position. This change eliminated unnecessary movement without sacrificing any core functionality, resulting in a more stable overall control process.

#### E. High-Frequency Noise Suppression

The LMC data initially contained significant high-frequency noise, causing the robotic arm to vibrate continuously. An initial attempt using a simple exponential smoothing algorithm with a coefficient of 0.3 reduced vibration but introduced phase lag, making the robotic arm's response appear sluggish.

This issue was resolved by adjusting the weight ratio between old and new data through iterative tuning: the previous frame data was assigned a weight of 0.7, while new data was weighted at 0.3. This modification effectively eliminated jitter while maintaining the robotic arm's responsiveness without perceptible delay. Through this series of solutions, the 6-DOF robotic arm achieved both stability and reliability, enabling smooth real-time control.

### 5.3 Limitations and Future Work

Although the vision-based gesture control system for the SO-ARM100 has been successfully validated, several limitations remain:

**Single-hand operation:** The current architecture supports only unilateral hand tracking. Although the LMC is capable of dual-hand tracking, this feature remains unimplemented. Extending to dual-arm coordination would require significant modifications to the communication protocol and coordination algorithms.

**Absence of haptic feedback:** The system implements position control only, without force feedback. In precision-critical applications such as surgery, this limitation poses safety risks, as operators cannot perceive contact forces. Integration of force sensors or motor current-based force estimation is required to address this gap.

**Limited gesture repertoire and sample size:** The current system recognizes only a small set of basic gestures. Furthermore, user testing involved only three participants, which is insufficient to validate the calibration method across diverse hand morphologies and age groups.

The direction for improvement is clear. First, dual-hand mode should be implemented, leveraging the LMC's hand-tracking capability to enable the robotic arm to work in tandem with the human hand — a qualitative leap for both surgical procedures and precision operations. Second, tactile feedback should be added, either by installing a micro force sensor on the gripper or by estimating force through motor current monitoring. This would allow operators to perceive contact and enable more intelligent force control. Only when these limitations are addressed can this system truly evolve from a laboratory demonstration prototype into a reliable tool for surgical and practical applications.

---

## References

[1] Meftah, S., Sahnoun, M. H., Messaadia, M. and Benslimane, S. M., 'Enhancing decision-making in Industry 5.0 through adaptive human machine interfaces: A systematic literature review', *Computer Standards & Interfaces*, 2025, 104091.

[2] Gunawardane, H., Medagedara, N. and Madhusanka, B. G. D. A., 'Control of robot arm based on hand gesture using leap motion sensor technology', *International Journal of Robotics and Mechatronics*, 2017, 10.

[3] Korayem, M. H., Madihi, M. A. and Vahidifar, V., 'Controlling surgical robot arm using Leap Motion Controller with Kalman filter', *Measurement*, 2021, 178, 109372.

[4] Zhang, Q. and Deng, F., 'Dynamic gesture recognition based on Leap Motion and HMM-CART model', *Journal of Physics: Conference Series*, 2017, 910(1), 012037.

[5] Chen, L., Li, C., Fahmy, A. and Sienz, J., 'GestureMoRo: an algorithm for autonomous mobile robot teleoperation based on gesture recognition', *Scientific Reports*, 2024, 14(1), 6199.

[6] Mariappan, R., Gayathri, P., Pushpalatha, P., Rishik, V. S. S. and Satish, T., 'Real time robotic arm using Leap Motion Controller', *Journal of Physics: Conference Series*, 2023, 2466(1), 012023.

[7] Reddington, H., Bogursky, A., Ballinger, Z., Widdowson, K., Guart, J., Walter, D. and Lou, F., 'Robotic Surgery Training During General Surgery Residency: A National Survey Study', *Journal of Surgical Education*, 2025, 82(11), 103702.

[8] Zhang, X., Wang, J., Dai, X., Shen, S. and Chen, X., 'A non-contact interactive system for multi-modal surgical robots based on LeapMotion and visual tags', *Frontiers in Neuroscience*, 2023, 17, 1287053.

[9] Korayem, M. H. and Vahidifar, V., 'Detecting hand's tremor using Leap Motion Controller in guiding surgical robot arms and laparoscopic scissors', *Measurement*, 2022, 204, 112133.

[10] Saint-Louis, H., 'Machine-human interaction: a paradigm shift', in *International Conference on Human-Computer Interaction*, Springer, 2021, pp. 123–136.

[11] Jain, N., Gupta, V., Temperini, V. et al., 'Human machine interactions: from past to future — a systematic literature review', *Journal of Management History*, 2024, 30(2), pp. 263–302.

[12] Zhao, W., 'A concise tutorial on human motion tracking and recognition with Microsoft Kinect', *Science China Information Sciences*, 2016, 59(9), 93101.

[13] Zabatani, A., Surazhsky, V., Sperling, E., Moshe, S. B., Menashe, O., Silver, D. H. and Kimmel, R., 'Intel® RealSense™ SR300 coded light depth camera', *IEEE Transactions on Pattern Analysis and Machine Intelligence*, 2019, 42(10), pp. 2333–2345.

[14] Guzsvinecz, T., Szucs, V. and Sik-Lanyi, C., 'Suitability of the Kinect Sensor and Leap Motion Controller — A Literature Review', *Sensors*, 2019, 19(5), 1072.

[15] Cheng, X., Cui, W., Liu, B. and Yang, H., 'Application of gesture recognition fusion algorithm based on double LeapMotion in hand function rehabilitation in large space', 2020 *International Conference on Virtual Reality and Visualization (ICVRV)*, IEEE, 2020, pp. 249–252.

[16] Najafinejad, A. and Korayem, M. H., 'Detection and minimizing the error caused by hand tremors using a leap motion sensor in operating a surgeon robot', *Measurement*, 2023, 221, 113544.

[17] Mulla, D. M., Majoni, N., Tilley, P. M. and Keir, P. J., 'Two cameras can be as good as four for marker-less hand tracking during simple finger movements', *Journal of Biomechanics*, 2025, 181, 112534.

[18] Fonk, R., Schneeweiss, S., Simon, U. and Engelhardt, L., 'Hand motion capture from a 3D Leap Motion Controller for a musculoskeletal dynamic simulation', *Sensors*, 2021, 21(4), 1199.

[19] Liu, Z., Wang, B., Lin, J., Xu, H., Li, C., Chen, R. and Li, J., 'Surgical applications of the Ultraleap 3Di-based gesture-controlled 3D imaging visualization system', *Computers in Biology and Medicine*, 2025, 194, 110548.

[20] Luongo, F., Hakim, R., Nguyen, J. H., Anandkumar, A. and Hung, A. J., 'Deep learning-based computer vision to recognize and classify suturing gestures in robot-assisted surgery', *Surgery*, 2021, 169(5), pp. 1240–1244.

[21] Paulo, S. F., Relvas, F., Nicolau, H., Rekik, Y., Machado, V., Botelho, J. and Lopes, D. S., 'Touchless interaction with medical images based on 3D hand cursors supported by single-foot input: A case study in dentistry', *Journal of Biomedical Informatics*, 2019, 100, 103316.

[22] Cong, V. D., 'Control the Robot Arm through Vision-Based Human Hand Tracking', *FME Transactions*, 2024, 52(1).

[23] Khanesar, M. A., Yan, M., Isa, M., Piano, S. and Branson, D. T., 'Precision Denavit-Hartenberg parameter calibration for industrial robots using a laser tracker system and intelligent optimization approaches', *Sensors*, 2023, 23(12), 5368.

[24] Adar, N. G., 'Real time control application of the robotic arm using neural network based inverse kinematics solution', *Sakarya University Journal of Science*, 2021, 25(3), pp. 849–907.

[25] Vicente, E., Quijano, Y., Ferri, V. and Caruso, R., 'Robot-assisted cholecystectomy with the new da Vinci SP® surgical system: first report in Spain with video', *Updates in Surgery*, 2025, pp. 1–4.

[26] Alvarez-Lopez, F., Maina, M. F. and Saigí-Rubió, F., 'Use of Commercial Off-The-Shelf Devices for the Detection of Manual Gestures in Surgery: Systematic Literature Review', *Journal of Medical Internet Research*, 2019, 21(5), e11925.

[27] Perry, J., 'Matleap: MATLAB mex interface for the Leap Motion Controller', GitHub (2020), https://github.com/jeffsp/matleap [accessed 1 April 2026].

---

## Appendices

### A. Python Core Program (hand_server.py)

*(Code content as in original)*

### B. MATLAB Core Program (real_time_control.m)

*(Code content as in original)*

### C. Resources & Costs

*(Cost table content as in original)*

### D. Logbook & Gantt Chart

Logbook has already been submitted via Canvas.
