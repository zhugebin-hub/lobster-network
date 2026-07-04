![A close-up of a logo Description automatically
generated](media/image1.jpeg){width="6.102083333333334in"
height="2.3493055555555555in"}

Vision-based Hand Gesture Control

of a Robotic Arm

By

Candidate Number: 269877

Supervised by: Dr. Yanpei Huang

A Dissertation Submitted to the

Sussex Artificial Intelligence Institute, Zhejiang Gongshang University

In Partial Fulfilment of the Requirements

For the Degree of

BEng Communications Engineering / BEng Robotics & Electrical Engineering

**Summary**

This project presents a real-time, vision-based control system for the
SO-ARM100 six-degree-of-freedom (6-DOF) robotic arm, enabling intuitive
teleoperation via hand gestures. The system utilizes a hybrid
Matlab-Python architecture: the Leap Motion Controller (LMC) captures 3D
hand coordinates and finger postures at 120Hz via the Matleap library,
while a Python-based server drives six STS3215 bus servos using the
STServo_sdk.

Communication is established through the TCP/IP protocol on a local
loopback network, achieving a low end-to-end latency of 80--100ms. A
comprehensive motion mapping strategy translates natural hand movements
into joint commands: palm translation controls the base and arm
elevation, while a heuristic thumb-index distance mapping governs wrist
rotation. To ensure operational stability, exponential smoothing (factor
0.3) is applied to suppress sensory jitter, and a five-frame hysteresis
logic is implemented for reliable fist-clenching detection.

The final system demonstrates responsive, natural movement tracking with
a 100% success rate in gesture execution during testing. By providing an
integrated, open-source solution, this project validates the feasibility
of non-contact human-machine interaction (HMI) for applications in
teaching demonstrations, teleoperations, and sterile medical
environments.

**Keywords:** Gesture Recognition, Robotic Arm Control, Leap Motion
Controller, Human-Machine Interaction, Teleoperation

Statement of Originality

I confirm that this dissertation is my own original work and has been
submitted for assessment solely for the requirements of the H1043Z
Individual Project module.

I declare that I am the sole author of this work, and all results
presented are derived from the design and experiments performed by me.
All quotations, summaries, and extracts from published sources have been
correctly referenced in accordance with the numerical referencing style.
This work, in whole or in part, has not been previously submitted for
publication or for any other academic award at this or any other
institution.

Contributions from other sources are identified as follows:

The communication code between the Leap Motion Controller and Matlab was
derived from the open-source project Matleap (Jeff Perry, GitHub). The
servo motor control library for the robotic arm was sourced from the
official website of Waveshare Company.

Except where indicated above, all other parts of this work are my own
original work.

Signature: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

Statement of Ethics

In making this submission I declare that my work contains no examples of
misconduct, such as plagiarism, collusion, or fabrication of results.

I confirm that I have talked with my project supervisor about whether
ethical review will be required, and that the outcome of the discussion
is included in my interim report.

Should an ethical review be required, I confirm that I will submit an
application before the end of week 2 of the spring term. Furthermore, if
the ethical implications of my project change, I confirm that I will
alert my supervisor immediately.

Signature: \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Content**

[Acknowledgement [1](#_Toc544518795)](#_Toc544518795)

[Chapter 1. Introduction [2](#_Toc1299567698)](#_Toc1299567698)

[Chapter 2. Literature Review [3](#_Toc1925610296)](#_Toc1925610296)

[2.1 Human-Machine Interaction Paradigms
[4](#_Toc1153684582)](#_Toc1153684582)

[2.2 Gesture Gesture Recognition [5](#_Toc346920911)](#_Toc346920911)

[2.2.1 Comparison of Sensor Technologies
[5](#_Toc281649572)](#_Toc281649572)

[2.2.2 Vision-based Gesture Recognition and Classification
[7](#_Toc630398616)](#_Toc630398616)

[2.3 Robotic Control Architectures
[8](#_Toc1572708461)](#_Toc1572708461)

[2.3.1 Fundamentals of Robotic Arm Movement
[8](#_Toc1282376751)](#_Toc1282376751)

[2.3.2 Real-time Control [9](#_Toc760172765)](#_Toc760172765)

[2.4 Medical Applications of Vision-based Control
[11](#_Toc843445352)](#_Toc843445352)

[Chapter 3. Methodology [12](#_Toc246477217)](#_Toc246477217)

[3.1 Overall System Framework [12](#_Toc46631056)](#_Toc46631056)

[3.2 Hardware Selection [12](#_Toc2044110684)](#_Toc2044110684)

[3.2.1 Leap Motion Controller [12](#_Toc2072364929)](#_Toc2072364929)

[3.2.2 SO-ARM100 Robot Arm [13](#_Toc200091010)](#_Toc200091010)

[3.2.3 Servo ST3125 [14](#_Toc2117697515)](#_Toc2117697515)

[3.2.4 Waveshare Bus Servo Drive Board
[14](#_Toc1895652874)](#_Toc1895652874)

[3.3 Software Architecture [15](#_Toc170466426)](#_Toc170466426)

[3.3.1 Matlab & Matleap [15](#_Toc286036684)](#_Toc286036684)

[3.3.2 Python + STServos_sdk [16](#_Toc1350146002)](#_Toc1350146002)

[3.3.3 TCP/IP Communication [17](#_Toc1591641412)](#_Toc1591641412)

[3.4 Kinetically Modeling [18](#_Toc1660904452)](#_Toc1660904452)

[Chapter 4. Implementation & Result
[20](#_Toc1828681058)](#_Toc1828681058)

[4.1 System Implementation [20](#_Toc2004069589)](#_Toc2004069589)

[4.1.1 Physical Setup and Hardware Deployment
[20](#_Toc1264062775)](#_Toc1264062775)

[4.1.2 Software Integration and Communication
[21](#_Toc47339654)](#_Toc47339654)

[4.1.3 System startup and operation process
[22](#_Toc1068615388)](#_Toc1068615388)

[4.1.4 Function Validation [24](#_Toc813086255)](#_Toc813086255)

[4.2 Experimental Results [24](#_Toc1102241924)](#_Toc1102241924)

[4.2.1 Real-time Tracking and Response Performance
[25](#_Toc1186077646)](#_Toc1186077646)

[4.2.2 Gesture Mapping and Joint Motion Consistency
[25](#_Toc1463784868)](#_Toc1463784868)

[4.2.3 Fingertip Detection and Gripper Control Effect
[26](#_Toc259616444)](#_Toc259616444)

[4.2.4 Motion Smoothing and Stability
[27](#_Toc1834287251)](#_Toc1834287251)

[4.2.5 Overall System Performance
[27](#_Toc1738074872)](#_Toc1738074872)

[4.3 Problems and Solutions [28](#_Toc1751807210)](#_Toc1751807210)

[4.3.1 Environmental compatibility issue
[28](#_Toc622978100)](#_Toc622978100)

[4.3.2 The servo angle range does not match
[29](#_Toc1410147575)](#_Toc1410147575)

[4.3.3 The gripper does not respond to the fist detection
[29](#_Toc720764733)](#_Toc720764733)

[4.3.4 Unintentional wrist rotation movement
[30](#_Toc2085098451)](#_Toc2085098451)

[4.3.5 TCP/IP Data Parsing Error [30](#_Toc1611514211)](#_Toc1611514211)

[4.3.6 Motion Tremors & Instability
[30](#_Toc655588313)](#_Toc655588313)

[4.4 Safety, Ethics, and Sustainability Analysis
[30](#_Toc1881667481)](#_Toc1881667481)

[4.4.1 Safety & Reliability [30](#_Toc1341167445)](#_Toc1341167445)

[4.4.2 Ethical Considerations [31](#_Toc1012889203)](#_Toc1012889203)

[4.4.3 Sustainability Analysis [31](#_Toc525965052)](#_Toc525965052)

[Chapter 5. Conclusion & Recommendation
[31](#_Toc851937912)](#_Toc851937912)

[5.1 Program Summary [31](#_Toc1247012435)](#_Toc1247012435)

[5.2 Limitation [33](#_Toc1245083972)](#_Toc1245083972)

[5.3 Improvement [34](#_Toc1045661036)](#_Toc1045661036)

[References [35](#_Toc1566348651)](#_Toc1566348651)

[Appendices [1](#_Toc1767232431)](#_Toc1767232431)

[A. Overall System Framework [1](#_Toc29146160)](#_Toc29146160)

[B. Python Core Programme [2](#_Toc233239604)](#_Toc233239604)

[C. Matlab Core Programme [5](#_Toc900368653)](#_Toc900368653)

[D. Resources & Costs [8](#_Toc1326174209)](#_Toc1326174209)

[]{#_Toc544518795 .anchor}**Acknowledgement**

The successful completion of this project is first and foremost
attributed to my sincere gratitude towards my supervisor, Professor
Yanpei Huang. From the selection of the research topic, the design of
the plan to the resolution of technical difficulties, Professor Huang
has always provided me with patient guidance and valuable suggestions.
Whenever the project encountered bottlenecks, Professor Huang could
always point out the direction for me with her profound professional
knowledge and rich practical experience, saving me from many detours.
Her rigorous academic attitude and pursuit of details have also deeply
influenced me, benefiting me for a lifetime.

Secondly, I would like to express my special thanks to Zhang Zhiwei, a
graduate student from the 24th Sussex - ZJSU Joint Institution. He
provided the crucial hardware facility, the SO-ARM100 robotic arm, for
this project and offered important guidance during the debugging and
environment configuration process. Whenever the hardware debugging got
stuck, he would always help identify the problems and offer timely
encouragement, which helped me regain confidence.

I would also like to thank my family. My elder sister, Chen Anqi, has
been providing me with full spiritual support and encouragement from the
beginning to the end of the project, making me believe that I could
independently complete the entire project before the deadline. My
parents provided me with a quiet and comfortable environment during the
winter vacation, allowing me to fully devote myself to the research.

Finally, I would like to thank my friends Zhou Yefei, Wang Yixin, and
Wang Xiaokun. They actively participated in the testing phase of the
project, and Zhou Yefei also helped shoot the demonstration video. The
achievements of this project could not have been possible without the
support and assistance of everyone.

[]{#_Toc1299567698 .anchor}**Chapter 1. Introduction**

Human-machine interaction (HMI) has gradually evolved from simple
graphical interfaces into a diversified ecosystem, allowing humans to
monitor and control machines or automated systems through various
methods[\[1\]](#_Ref20752). Common HMI control methods can be classified
into visual control, manual control, audio control, environmental
interaction, and others. For example, users receive graphical
information through screens; people manually operate steering wheels to
control vehicles. In smart homes, voice recognition controls furniture,
while light sensors automatically adjust curtains. These different
interaction methods have greatly enriched how people interact with
technology, making operations more natural and accessible across various
applications.

As the most powerful channel for human perception, vision plays a
crucial role in the evolution of HMI. Approximately 80% of human sensory
information is acquired through vision, making it an indispensable
component in human-machine interaction systems. In remote operating
systems, using vision as the HMI enables users to control robots through
intuitive gestures, eliminating the need for physical contact with
control interfaces. This capability is particularly transformative in
the medical field, where vision-based control is emerging as a promising
method for operating surgical tools. By translating subtle hand
movements into precise commands, it paves the way for more intuitive and
responsive surgical interfaces[\[2\]](#_Ref20912)-[\[6\]](#_Ref20435).

Using vision to control surgical instruments can address several
limitations associated with traditional manual control methods. First,
existing remote surgical controllers such as the da Vinci Surgical
System have steep learning curves, requiring extensive training
time[\[7\]](#_Ref21441). Vision-based gesture control could potentially
simplify operation and make surgical robotics more accessible. Second,
traditional contact-based devices carry risks of bacterial infection and
require strict aseptic conditions[\[8\]](#_Ref21529)[\[9\]](#_Ref21539).
Vision control, as a non-contact method, can significantly reduce this
risk by eliminating physical touch points entirely. Third, vision-based
systems require only compact sensors like Leap Motion, offering a more
space-efficient alternative compared to traditional surgical consoles.

Despite these potential advantages, current research lacks sufficient
studies on using vision to control medical equipment. Key questions
regarding precision, latency, reliability, and clinical acceptance have
yet to be systematically addressed.

This project aims to achieve simple and feasible operations by using
vision-based devices to control robotic tools, serving as a foundational
step toward more advanced applications. The system reads gesture data
through a Leap Motion sensor and uses these data to control a 6-DOF
robotic arm (SO-ARM100). Through real-time mapping of hand positions and
finger gestures to corresponding joint movements, the system
demonstrates intuitive and responsive control. The specific
contributions of this work include: establishing a complete
communication pipeline between Leap Motion and servo-driven robotic arm;
developing a comprehensive mapping strategy that translates natural hand
gestures into precise joint commands; implementing real-time control
with minimal latency; and creating an integrated software package that
simplifies system deployment and operation.

This work helps verify the feasibility of using vision-based equipment
to control robotic systems and provides possibilities for more flexible
and lower-barrier solutions in surgical robot control and beyond.

[]{#_Toc1925610296 .anchor}**Chapter 2. Literature Review**

This chapter provides a general review of existing research and
technological developments relevant to vision-based gesture control of
robotic systems. The literature review aims to establish the theoretical
foundation for this project, identify current gaps in knowledge, and
situate the present work within the broader context of HMI, gesture
recognition technologies, and robotic control systems.

The review begins by examining the evolution of human-machine
interaction paradigms, tracing the progression from traditional physical
interfaces to contemporary vision-based approaches. Particular attention
is given to gesture recognition technologies, with a focus on optical
sensors such as the LMC, which serves as the primary input device for
this project. The capabilities, limitations, and applications of various
gesture recognition systems are critically evaluated to inform the
selection and implementation decisions made in this work.

Subsequently, the review explores robotic control architectures,
emphasizing real-time control strategies suitable for teleoperation
scenarios. The kinematics of multi-DOF manipulators, including the
SO-ARM100 platform used in this project, are discussed in relation to
gesture-based control requirements. Communication protocols and latency
considerations relevant to remote operation are also examined.

Finally, the review summarizes the findings from the existing literature
and identifies several issues that have not yet been resolved. These
issues form the basis of the work undertaken in this project. They
include the need for simpler and more accessible control interfaces for
robotic systems, the potential of non-contact gesture control in sterile
medical environments, and the lack of an integrated, open-source
platform suitable for validating vision-based robotic control concepts.
By outlining what is already known, the literature review provides the
necessary context for the research presented in the following chapters.

[]{#_Toc1153684582 .anchor}**2.1 Human-Machine Interaction Paradigms**

Human-machine interaction (HMI) has evolved significantly from its
origins to become a diverse and sophisticated field. Early HMI systems
were predominantly based on physical controls such as buttons, switches,
knobs, and levers, which required direct mechanical contact and offered
limited flexibility for complex operations. These interfaces constrained
the complexity of tasks that could be performed
efficiently[\[10\]](#_Ref21624).

The introduction of graphical user interfaces (GUIs) in the 1970s and
1980s marked a paradigm shift, replacing text-based command lines with
visual elements such as windows, icons, menus, and pointers. This
transformation, pioneered by systems like the Xerox Alto and later
popularized by Apple Macintosh and Microsoft Windows, made computers
accessible to non-expert users by enabling intuitive visual feedback and
point-and-click interactions via keyboards and mice. GUIs remain
dominant in personal computing and have expanded to diverse platforms
including smartphones, tablets, and industrial control systems.

The proliferation of touchscreen technology from the late 2000s onward
represented another major evolution. Capacitive touchscreens popularized
by smartphones and tablets, enabled direct manipulation of digital
content through finger gestures such as tapping, swiping, pinching, and
rotating. This natural mapping between physical actions and digital
responses reduced cognitive load and accelerated user adoption across
age groups and skill levels. Touch-based interfaces have since become
ubiquitous in consumer electronics, public kiosks, and increasingly in
industrial and medical settings.

More recently, research and commercial development have focused on
natural interaction modalities that leverage humans\' innate
communication capabilities. Voice-controlled assistants such as Amazon
Alexa, Google Assistant, and Apple Siri demonstrate the viability of
speech as a primary interaction channel, enabling hands-free operation
in contexts where manual control is impractical. Eye-tracking
technology, initially developed for accessibility applications, now
finds use in gaming, driver monitoring systems, and hands-free computer
control. Enabled by advances in computer vision and depth sensing,
gesture recognition allows users to interact with systems through body
movements and hand gestures without physical
contact[\[11\]](#_Ref21659).

Among these emerging paradigms, gesture-based interaction holds
particular promise for applications where traditional interfaces present
limitations. Gesture control offers several distinct advantages: it
eliminates physical contact, which is crucial in sterile medical
environments. It enables intuitive spatial manipulation, which benefits
teleoperation scenarios, and it reduces cognitive load by leveraging
natural human communication patterns. Systems such as Microsoft Kinect,
Leap Motion, and various RGB-D cameras have demonstrated the feasibility
of robust gesture recognition across diverse applications including
gaming, education, rehabilitation, and industrial control.

The evolution of HMI paradigms reflects a consistent trend toward
greater intuitiveness, reduced cognitive load, and expanded
accessibility. Each successive paradigm has broadened the population of
users who can effectively interact with technology while enabling new
classes of applications. This trajectory suggests that future HMI
development will continue pursuing even more natural, seamless
integration of human capabilities with machine intelligence, potentially
incorporating multi-modal fusion of gestures, speech, gaze, and
physiological signals to create truly immersive and responsive
interaction experiences.

[]{#_Toc346920911 .anchor}**2.2 Gesture Recognition**

[]{#_Toc281649572 .anchor}2.2.1 Comparison of Sensor Technologies

Gesture recognition tracking has corresponding requirements for various
aspects of the equipment. The existing gesture tracking devices on the
market, such as Microsoft Kinect, Intel RealSense, and LMC, are among
the leading ones. Microsoft Kinect (taking Kinect v2 as an example) is
equipped with a color camera and a depth sensor, using time-of-flight
technology (ToF) for depth perception[\[12\]](#_Ref21699); Intel
RealSense (SR300) has encoded light depth perception technology,
reducing the cost of 3D cameras[\[13\]](#_Ref21728); LMC uses
stereoscopic infrared vision, combined with active illumination and
complex software algorithms, to complete depth perception of
objects[\[2\]](#_Ref631464619)[\[14\]](#_Ref21764).

By comparing the experimental characteristics of the three mainly 3D
cameras (as shown in Table 1), it can be observed that LMC strikes a
balance between performance and cost-effectiveness, making it the
preferred choice for implementing this project.

Table 1. Comparison of three 3D cameras

![](media/image2.png){width="6.2652777777777775in"
height="0.9597222222222223in"}

The LMC is equipped with 3 IR LEDs and 2 IR cameras. The IR LEDs act as
the primary light source, used to illuminate the area being tracked. The
two side-by-side IR cameras simultaneously capture the infrared light
reflected back by the hand, generating a two-dimensional infrared image
of the hand[[\[2\]](#_Ref631464619)](#_Ref21754). As shown in the figure
2, corresponding Cartesian coordinates are generated. Apart from the
hardware facilities, real-time employment data needs to be obtained
through the Leap Motion Software Development Kit (SDK).

![](media/image3.png){width="3.1486111111111112in"
height="1.4472222222222222in"}

Figure 1. Structure of LMC by Gunawardane, H. *et al.*

![](media/image3.png){width="2.7715277777777776in"
height="1.7513888888888889in"}

Figure 2. Range of LMC by Cheng, X. *et al.*

In visual-based surgical robot control, one significant challenge is how
to mitigate hand tremors, which tend to intensify due to muscle fatigue.
To address this issue, Najafinejad and Corayem (2023) utilized the high
sampling rate of the LMC to obtain tremor data. They proposed an
adaptive filter based on Empirical Mode Decomposition (EMD) and employed
the Klumpke-Lebler divergence to dynamically identify and remove the
tremor components in the intended motion signals. This method
demonstrated effectiveness in compensating for time-varying tremor
characteristics and showcased a complex signal processing solution for
this crucial physiological limitation[\[16\]](#_Ref21849).

Although single-camera systems like the LMC offer high precision, their
limited field of view may restrict natural movements. To address this
issue, researchers explored multi-sensor configurations. For instance,
by using two LMCs and combining coordinate system fusion algorithms, the
tracking range and spatial field of view were successfully expanded,
enabling hand tracking in large spaces[\[17\]](#_Ref21878). When
considering multi-camera setups, the number and position of sensors are
crucial. For simple finger movements, a dual-camera system with the
optimal placement (for example, at the outer edge of the capture range)
can achieve the same level of accuracy as a four-camera system,
highlighting an economical and efficient configuration
approach[\[18\]](#_Ref21904). Based on these studies, a framework has
been provided for the expansion of hand tracking systems. This can be
achieved by combining specialized sensors like LMC or by strategically
deploying multiple standard cameras to balance performance, cost, and
application requirements.

[]{#_Toc630398616 .anchor}2.2.2 Vision-based Gesture Recognition and
Classification

When the gestures are captured by LMC, the gesture images can be
converted into specific gesture data through the Leap Motion SDK. Fonk
et al. (2021) developed the ROSE Motion system, successfully integrating
the hand bone data captured by the LMC into the bone simulation by
calculating joint angles, relative angles between bone joints, and other
relevant data[\[19\]](#_Ref21957).

![](media/image4.png){width="3.1284722222222223in"
height="1.6222222222222222in"}

Figure 3. Motion and joint angle by Fonl e*t al.*

In current robot-assisted surgeries, simple gestures are commonly used
to control the robot\'s arms. For instance, Liu, Z et al. (2025)
developed a 3D medical image visualization system based on Ultraleap3Di
gesture control. In this system, a carefully defined set of gesture
instructions is mapped to complex operations, such as the scaling,
translation, rotation, and multi-layer slice browsing of 3D
reconstruction models[\[20\]](#_Ref21989).

The possible gesture mappings are as
follows[\[20\]](#_Ref21989)[\[21\]](#_Ref22035)[\[22\]](#_Ref22038)

· Hand rotation -the rotation of the end of the robotic arm.

· Hand movement - End effector movement of the robotic arm.

· The index finger and the thumb are clamped together - End Effector
opens and closes.

· Palm opening and closing - Screen zooming.

Phuong and Cong (2024) proposed a method for directly controlling a
SCARA robotic arm using hand movements. They utilized the MediaPipe
Hands visual algorithm to detect 21 key points on the hand and calculate
the position coordinates of the palm[\[23\]](#_Ref22074). This
coordinate was used to directly determine where the robot\'s end should
move to. This method can determine whether the hand is open or clenched
based on the distance between the wrist and the tip of the middle
finger, which is used to control the grasping action. However, it is too
simple, rough, unsafe and inaccurate, and completely fails to meet the
high precision, high reliability, high safety and intelligent
understanding requirements that a surgical robot needs.

![](media/image5.png){width="3.3333333333333335in"
height="1.7215277777777778in"}

Figure 4. Hand landmark by Phuong and Cong

[]{#_Toc1572708461 .anchor}**2.3 Robotic Control Architectures**

[]{#_Toc1282376751 .anchor}2.3.1 Fundamentals of Robotic Arm Movement

Robot kinematics is a discipline that studies the mapping relationship
between the joint space and the end-effector space of a robot, and it
serves as the theoretical foundation for achieving robot control. For a
6-DOF manipulator, kinematics is divided into two core issues: forward
kinematics and inverse kinematics.

Forward kinematics is solved through a process. Usually, given the
angles of each joint, the position and orientation of the end effector
are sought. For the 6-DOF robotic arm used in this project, the
Denavit-Hartenberg parameter method (abbreviated as D-H parameters) is
typically employed to establish the kinematic model. The D-H parameter
method[\[24\]](#_Ref22717) describes the transformation relationship
between the coordinate systems of two adjacent joints through four
parameters (link length a, link twist angle α, joint distance d, and
joint rotation angle θ). By successively multiplying the transformation
matrices of each joint, the total transformation matrix from the base to
the end effector is obtained.

The inverse kinematics addresses a more critical issue: given the target
pose of the end effector, calculate the required joint angles to achieve
that pose. This is the core for implementing gesture control. When the
Leap Motion detects the hand position, the system needs to calculate the
angles that the six servos should rotate through inverse kinematics. For
a specific configuration of the robotic arm, a closed-form solution can
be derived through geometric relationships. The advantage is that it is
computationally fast and suitable for real-time control; the
disadvantage is that it needs to be derived separately for different
robotic arms. The SO-ARM100 has an spherical wrist structure (where the
three rotational axes can be considered to intersect at one point), and
thus has an analytical solution.

![](media/image6.png){width="3.504861111111111in"
height="1.7597222222222222in"}

Figure 5. Kinematic Calculation Cycle

The so-arm100 robotic arm used in this project has six joints. Since
each joint corresponds to one degree of freedom, each joint is
controlled by a servo motor to rotate and thereby adjust the position of
the end effector. This robotic arm mimics the structure of a human arm:
two axes at the shoulder, one axis at the elbow, two axes at the wrist,
and one axis for the gripper. This makes the mapping from gestures to
joints more intuitive and natural, and the logic is simpler and easier
to derive. The axes of the last three joints intersect at one point,
which simplifies the solution of inverse kinematics.

[]{#_Toc760172765 .anchor}2.3.2 Real-time Control

Real-time control is the core technical challenge for achieving
gesture-following of robotic arms. Unlike offline trajectory planning,
real-time control requires completing the entire closed-loop process
from sensor data acquisition, kinematic calculations to command output
within the millisecond time scale. This section elaborates on the
real-time control strategy from three aspects: control architecture,
timing design, and delay analysis and optimization.

The control architecture of this system adopts a master-slave remote
operation structure. In this system, Leap Motion acts as the master
hand, while the SO-ARM100 robotic arm serves as the slave hand. The
control loop consists of the following components.

The data acquisition layer captures hand position and finger posture via
LMC at approximately 120Hz, feeding data into Matlab through the Matleap
interface; the processing layer performs fist detection, wrist rotation
estimation, and kinematic mapping to compute target joint angles; the
instruction transmission layer serializes these angles and sends them to
the Python server via TCP/IP, ensuring reliable delivery through
built-in checksum and re-transmission; finally, the execution control
layer uses the STServo_sdk library to issue synchronous write commands
to the servo driver board, driving the robotic arm's motion.

![](media/image7.png){width="1.6423611111111112in"
height="2.3472222222222223in"}

Figure 6. Control Architecture

To balance real-time performance and control accuracy, the system adopts
a fixed control frequency of 30Hz. This frequency selection is based on
human factors and the calculation load of response delay. The natural
movement frequency of the human hand is usually within the range of
1-3Hz. According to the Nyquist sampling theorem, the sampling frequency
must be at least twice the highest movement frequency. 30Hz is
sufficient to capture all the details of human hand movement. And a
control cycle of 30Hz corresponds to a frame interval of approximately
33ms. Adding other system delays, the total delay is controlled within
100ms, which is almost imperceptible to the operator. However, the
solution of inverse kinematics has certain computational overhead. A
frequency of 30Hz can ensure real-time performance without causing the
processor to overload. The delays in the real-time control system mainly
come from the following aspects:

Table 2. System Delays

  -----------------------------------------------------------------------
             **Delay Resource**                   **Typical Value**
  ----------------------------------------- -----------------------------
             LMC Data Collection                       8-10ms

             Matlab Data Receive                       5-15ms

             Kinematic Calculate                       10-20ms

             TCP/IP Transmission                        \<1ms

               Servos Response                        100-300ms
  -----------------------------------------------------------------------

To achieve more accurate joint trajectory tracking, this system adopts a
PID controller instead of the simple first-order smoothing filter. The
PID controller calculates the appropriate control output based on the
deviation between the current joint angle and the target angle. Its
discretized form can be expressed as:

$\text{u(k)=}\text{K}_{\text{p}}\text{e(k)+}\text{K}_{\text{i}}\sum_{\text{j=0}}^{\text{k}}\text{e(j)+}\text{K}_{\text{d}}\text{[e(k)−e(k−1)]}$
(1)

Compared with exponential smoothing filtering, the advantages of PID
control lie in the following[\[24\]](#_Ref634557107): The proportional
term responds immediately to the deviation, which can shorten the
tracking delay; the integral term eliminates the static error and
ensures that the final position accurately reaches the target; the
differential term adjusts in advance according to the rate of change of
the deviation, reducing overshoot.

[]{#_Toc843445352 .anchor}**2.4 Medical Applications of Vision-based
Control**

In modern surgical procedures, the application of robotic systems is
becoming increasingly widespread, such as the Da Vinci Surgical System
and other platforms that can achieve higher precision and flexibility
through minimally invasive surgeries[\[25\]](#_Ref634321809). However,
traditional surgical robots rely on console-based interfaces, which
require extensive training and separate the surgeons from the patients.
The learning curves of these systems are still long because the mapping
between console operations and instrument movements is not intuitive.
These limitations have prompted the exploration of alternative control
methods that can utilize the natural hand movements of surgeons and
reduce the training requirements.

In this context, visual gesture control offers several significant
advantages for surgical applications. As a non-contact mode, it
perfectly aligns with the sterile requirements of the operating room,
eliminating the need for physical interfaces that must be disinfected or
covered. Surgeons can maintain their positions within the sterile area
and interact with the robotic instruments through intuitive gestures.

Research in this field has explored applications both preoperatively and
intraoperatively. In preoperative planning, gesture recognition has
successfully been applied to navigate three-dimensional medical images
such as CT and MRI scans, enabling surgeons to rotate, scale, and slice
volumetric data without touching keyboards or mice. In intraoperative
applications, studies have demonstrated that using gestures to control
robotic instruments and laparoscopic cameras is feasible, with reports
indicating that task completion times are shortened and cognitive load
is reduced compared to traditional foot pedals or console controls.

These encouraging results notwithstanding, significant challenges
remain. The high precision required for surgical tasks may exceed the
capability of consumer-level depth sensors. While latency is acceptable
in image navigation, it becomes a critical safety concern in direct
instrument control. Vision-only systems also lack tactile feedback,
limiting the surgeon\'s ability to perceive tissue characteristics.
Several gaps also exist in the literature. Most studies analyze
individual components rather than demonstrating a complete, integrated
system. The lack of standardized evaluation frameworks hinders
cross-study comparison. Data on learning curves, workload, and user
acceptance remain limited. Furthermore, systematic analysis of fault
modes, error recovery, and safety mechanisms is still at an early stage.

This research aims to address these gaps by developing a complete
open-source system for 6-DOF gesture control of a robotic arm, providing
a reproducible foundation for exploring visual control in medical
surgery.

[]{#_Toc246477217 .anchor}**Chapter 3. Methodology**

[]{#_Toc46631056 .anchor}**3.1 Overall System Framework**

See appendix A.

[]{#_Toc2044110684 .anchor}**3.2 Hardware Selection**

The hardware selection of this system follows the following principles:

A.  Meeting the functional requirements of real-time gesture recognition
    and robotic arm control;

B.  Considering both development efficiency and cost control;

C.  Ensuring the repeatability and scalability of the system.

    Based on the above principles, the system hardware mainly consists
    of three parts: gesture acquisition devices, the robotic arm body,
    and the servo drive unit.

[]{#_Toc2072364929 .anchor}3.2.1 Leap Motion Controller

The LMC is a desktop gesture recognition device based on infrared
binocular stereo vision principle, specifically designed for tracking
hand movements at close range. Its core performance parameters are as
follows: the effective tracking range is the space area approximately 25
mm to 600 mm above the device, with a maximum frame rate of 120 Hz, and
the nominal value of position tracking accuracy is 0.01 mm. It can
simultaneously recognize the movement states of each finger joint of
both hands. Compared with depth sensors like Kinect that use structured
light, the LMC has a significant advantage in high-resolution capture of
finger-level movement details. Compared with data gloves, its
non-contact operation mode eliminates the physical constraints and
hygiene risks of wearing devices, making it more suitable for
application scenarios that have high requirements for operational
convenience and aseptic conditions.

![9d8647bf-9229-452e-8aba-5b2978e7f2c4](media/image8.png){width="2.8819444444444446in"
height="1.1104166666666666in"}

Figure 7. LMC

Based on the above characteristics, this study selects the LMC as the
gesture input device, mainly considering the following three aspects:
First, the device has high frame rate and low latency data acquisition
capabilities, which can meet the requirements of real-time control tasks
for system response performance; second, relying on the mature Matlab
interface provided by the open-source community (such as the Matleap
project), it can be conveniently integrated with subsequent algorithm
modules, reducing the complexity of system development and verification;
third, the non-contact interaction method is highly consistent with the
aseptic operation requirements in medical scenarios, providing a
feasibility basis for the application of the system in related fields.

During the actual operation, the subject only needs to place their hand
at the appropriate height of the LMC, and then click the Leap Motion SDK
program, which will enable the transmission of the captured data from
the LMC to the computer, completing the first layer of data collection.

[]{#_Toc200091010 .anchor}3.2.2 SO-ARM100 Robot Arm

The SO-ARM100 robot arm developed by Shanghai Sunling Robotics Co., Ltd.
Its design is centered on openness and educational applicability. The
outstanding feature of this robot arm lies in its anthropomorphic
configuration, which closely mimics the kinematic distribution of the
human upper limb: the base rotation joint corresponds to the horizontal
rotation of the shoulder, the shoulder and elbow joints jointly achieve
a wide range of pitch movements, and the wrist integrates two degrees of
freedom for rotation and pitch. The end effector adopts a parallel
gripper form. This configuration ensures that the kinematic structure of
the robot arm has a direct correspondence with the natural movement of
the human arm in terms of joint distribution and movement range,
providing a solid kinematic foundation for the implementation of
functions such as gesture mapping in the upper-level control algorithm.

The robotic arm has a maximum load capacity of 500g, while most surgical
instruments weigh between 40g and 250g. This makes it theoretically
possible for the robotic arm to handle most surgical instruments.

Table 3. SO-ARM100 Parameters

![](media/image9.png){width="6.2625in" height="1.4951388888888888in"}

[]{#_Toc2117697515 .anchor}3.2.3 Servo ST3125

In the SO-ARM100 robotic arm, the STS3215 type serial servo motor serves
as the core driving unit for the six joints, playing a crucial role in
motion execution, precision control, and system simplification. This
motor significantly simplifies the cable layout through a serial bus
cascading scheme, and its internal 12-bit magnetic encoder enables
high-precision angle feedback and closed-loop control, ensuring that the
robotic arm achieves a repeatability positioning accuracy of ±0.5 mm.
This motor significantly simplifies the cable layout through a serial
bus cascading scheme, and its internal 12-bit magnetic encoder enables
high-precision angle feedback and closed-loop control, ensuring that the
robotic arm achieves a repeatability positioning accuracy of ±0.5 mm.
Additionally, the motor supports various control modes such as angle
servo and speed closed-loop, and is equipped with multiple protection
mechanisms including overload, overcurrent, and overheating, effectively
enhancing the reliability and safety of the system operation, and
providing a solid execution foundation for the upper-level motion
planning and remote operation algorithms.

Table 4. Servo ST3215 Parameters

  -----------------------------------------------------------------------
  **Parameters**        **Specification**
  --------------------- -------------------------------------------------
  Input Voltage         6-12.6V

  Mechanical Limited    No Limit
  Angle                 

  Rotating Angle        360° (servo mode angle control) / motor mode
                        continuous rotation

  Baudrate              1Mbps

  Gear                  high-precision metal gear

  Idling Speed          0.222sec/60°（45RPM）@12V

  Pos Sensor Resolution 360°/4096

  ID Range              0-253

  Feedback              Position, Load, Speed, Input Voltage

  Idling Current: 180   180 mA
  mA                    

  Locked-rotor Current  2.7 A

  Dimension             45.22mm x 35mm x 24.72mm
  -----------------------------------------------------------------------

[]{#_Toc1895652874 .anchor}3.2.4 Waveshare Bus Servo Drive Board

The Waveshare driver board, as a USB-UART conversion module, is
responsible for converting USB instructions from the computer into
communication signals for the servo bus. Its core function is to ensure
the electrical reliability of instruction transmission and the stability
of the baud rate. This system adopts this driver solution mainly due to
its complete compatibility with the SO-ARM100 and the SDK\'s good
support for the Python environment. Additionally, the support for
synchronous write instructions enables the simultaneous issuance of
angle instructions for the six joints, which is conducive to achieving
the coordination of the robotic arm\'s movement.

Table 5. Waveshare Parameters

  -----------------------------------------------------------------------
          **Parameters**                    **Specification**
  ------------------------------ ----------------------------------------
          Input Voltage                 9-12.6V(ST Series Servos)

     Communication interface                UART / USB Type-C

      Power supply interface          5.5×2.1mm DC or terminal block

           Product size                          42×33 mm

       Fixing hole diameter                       2.5 mm
  -----------------------------------------------------------------------

The above-mentioned hardware components are integrated in the following
way. The Leap Motion is connected to the computer via USB and runs in
the Matlab environment; the servo bus of the SO-ARM100 is connected to
the same computer through a Waveshare driver board and is controlled by
the Python environment. The two subsystems are physically independent
and achieve data synchronization through TCP/IP communication at the
software level, avoiding the contention for underlying hardware
resources. This loosely coupled architecture enables the gesture
acquisition and robot control to be optimized separately and also
facilitates the subsequent replacement or upgrade of any subsystem. All
hardware is deployed in a desktop experimental environment, meeting the
requirements for real-time control and debugging.

[]{#_Toc170466426 .anchor}**3.3 Software Architecture**

[]{#_Toc286036684 .anchor}3.3.1 Matlab & Matleap

Matleap is an open-source Matlab interface library designed to
seamlessly integrate the real-time hand tracking data from the LMC into
the Matlab environment. This library was developed by Jeff Perry and
uses MEX (MATLAB Executable) technology to encapsulate the C++ SDK of
Leap Motion into a Matlab-compatible function
interface[\[27\]](#_Ref378491536). This enables researchers to directly
obtain high-precision hand movement data in Matlab and utilize Matlab\'s
powerful numerical computation and visualization capabilities for
subsequent processing.

Matleap consists of multiple functions, and several of these functions
jointly support the gesture data collection of this system. The
initialization and version query functions enable LMC to be initialized
and to check the version sequence of the Leap Motion SDK. The data frame
function is the core data interface of this system. Each time it is
called, it will read the latest hand tracking data from the frame buffer
of Leap Motion and returns it in the form of a structure. Each return
includes the sequence of the frame, the timestamp, the determination of
the left and right hands, and the fingertip information. The Hand
function obtains the key attributes of the palm, such as the 3D
coordinates (x, y, z) of the palm center, the radius of the spherical
area around the palm center, etc. The Pointables function calculates the
distance from the fingertip to the palm center by accessing the
information of each finger\'s fingertip. These data can be used for fist
detection and wrist posture estimation.

![](media/image10.png){width="1.2465277777777777in"
height="2.4833333333333334in"}

Figure 8. Matleap Frame

As the Matlab interface of Leap Motion, Matleap demonstrates significant
advantages in this system. First, it is packaged to work right out of
the box, with no need for manual driver setup. Developers can directly
call the Leap Motion SDK in the Matlab environment without writing C++
code, significantly reducing the programming threshold for gesture data
collection. Secondly, its data frame acquisition frequency can reach up
to 120Hz, far exceeding the natural movement frequency of the human
hand, providing sufficient time redundancy for real-time control. Then,
the returned hand and finger data structures are clear and the fields
are complete. Key information such as palm position and fingertip
coordinates can be directly accessed through the structure field,
avoiding complex protocol parsing. Finally, the deep integration of
Matleap with the native ecosystem of Matlab enables unified data
processing, kinematic calculations, and visualization display on the
same platform, simplifying the system architecture. These advantages
collectively make Matleap the ideal choice for the gesture collection
layer of this system, ensuring real-time performance while also
considering development efficiency and code maintainability.

[]{#_Toc1350146002 .anchor}3.3.2 Python + STServos_sdk

STServo_sdk is a Python software development kit provided by Waveshare
Electronics for the STS series bus servo motors. In this system, it
undertakes all the underlying work of the robot control layer. This SDK
encapsulates the complex servo communication protocol through a simple
object oriented interface, allowing developers to complete operations
such as servo detection, position writing, and status reading without
needing to concern themselves with details such as instruction frame
format, checksum calculation, etc. They only need to call high-level
functions like ping, WritePosEx, and ReadPosSpeed to complete these
operations.

In hand_server.py file, during the initialization stage, the system
scans ID1 to ID6 servos using the ping method to verify that all joints
respond online. In the real-time control loop, the program converts the
six target angles sent by Matlab into calls to WritePosEx and sends them
to the Waveshare driver board through a high-speed serial port with a
baud rate of 1,000,000 bps to ensure low latency in instruction
transmission. Although this system actually uses a sequential writing
method, the native sync_write synchronous write instruction of the SDK
theoretically enables strict synchronization movement of all joints.
Additionally, the position feedback function provided by ReadPosSpeed is
used to verify the actual position reached by the servo and plays an
important role in the debugging of the clamping control. The stability
and clear interface design of the SDK significantly shorten the system
debugging cycle, allowing the development focus to be concentrated on
the kinematic mapping and gesture recognition algorithms, and becoming a
key technical support for real-time gesture control.

[]{#_Toc1591641412 .anchor}3.3.3 TCP/IP Communication

TCP/IP communication serves as the core bridge for enabling gesture data
exchange between Matlab and Python in this system. Since the Matlab side
is responsible for gesture data acquisition and kinematic calculations,
while the Python side is responsible for the underlying control of the
servo motors, the two subsystems run in different processes on the same
computer and require a stable and low latency with inter-process
communication mechanism. Considering reliability, real-time performance,
and implementation complexity, this system selects the TCP/IP protocol
as the communication solution and adopts a client-server architecture.

The Python side acts as a TCP server, listening for connection requests
on port 65432 of localhost. The Matlab side acts as the client,
initiating the connection on its own after initialization. The advantage
of this design is that the Python server can be independently started
and debugged, while the Matlab client can connect or reconnect at any
time as needed, decoupling the lifecycles of both ends. The
communication is in single-direction mode. Matlab sends data to Python,
and Python returns a confirmation character upon receiving it, forming a
simple request-confirmation mechanism to ensure that each frame of data
is successfully received.

Although the TCP/IP protocol introduces certain protocol stack overhead,
in the local loop-back network environment, the measured single data
transmission delay is less than 1ms, which is much lower than the 30Hz
control cycle requirement. The retransmission mechanism ensures the
reliable delivery of data and avoids motion abnormalities caused by lost
instructions. This system uses blocking write calls on the Matlab side
and synchronous reception on the Python side, combined with a simple
confirmation response mechanism, to form a stable data flow loop.

To handle communication anomalies, the system has implemented basic
fault tolerance mechanisms at both ends. On the Matlab side, it outputs
an error message and exits when the connection fails, and terminates the
loop when the transmission timeout occurs. On the Python side, it skips
the current frame and continues to listen when there is an error in data
parsing, avoiding the entire control process from crashing due to a
single erroneous frame. The TCP/IP communication layer plays a crucial
role in this system as it efficiently and reliably transfers gesture
data from the computing space of Matlab to the execution space of
Python, providing a stable data channel for real-time control.

[]{#_Toc1660904452 .anchor}**3.4 Kinematic Modeling**

The mapping from gestures to joints is the core algorithm for converting
Leap Motion hand tracking data into SO-ARM100 servo angle instructions.
This implementation is accomplished in the Python server script
hand_server.py, which receives hand data via TCP/IP and calculates the
target positions for the six servo motors. The first three joints
correspond directly to the palm coordinates in three-dimensional space,
following a mapping designed for intuitive control:

Table 6. ID1-ID3 Joints Mapping

  ------- ------------------ ----------------------------------------------
   Joint    Control Signal                  Mapping Formula

    ID1   Palm x-coordinate    HOME_POSITIONS\[0\] + int(x / 200 \* 500)

    ID2   Palm z-coordinate    HOME_POSITIONS\[1\] - int(z / 200 \* 500)

    ID3   Palm y-coordinate   HOME_POSITIONS\[2\] - int((y - 200) / 200 \*
                                                  500)
  ------- ------------------ ----------------------------------------------

Servo ID4 (wrist pitch) is kept at its home position throughout
operation, as preliminary testing showed that adding pitch control
introduced unintended movements without improving the intuitive nature
of the control. This decision simplifies the mapping while maintaining
sufficient functionality for demonstration purposes.

Wrist rotation (Servo ID5) is derived from the difference between thumb
and index finger distances. This heuristic captures the natural rotation
of the hand when the thumb and index finger move relative to each other.

This yields a value between -0.8 and 0.8, which is then scaled by
WRIST_ROT_SCALE = 400 to produce a position offset relative to the home
position.

The server listens on port 65432 on the localhost and receives data
strings formatted as comma-separated values. These data contain 8
floating-point numbers: the palm position (x, y, z) in mm, followed by
the distances from the palm center to the five fingertips (thumb to
little finger). After receiving a frame of data, the data is parsed and
stored in the values array, where values\[0\], values\[1\], and
values\[2\] represent the palm coordinates, and values\[3\] to
values\[7\] represent the distances of the fingers.

The control of the gripper (servo ID6) is based on the degree of index
finger bending, using pre-calibrated distance thresholds (detailed in
Section 4.2.3).

The gripper target position is then linearly interpolated between
GRIPPER_OPEN (home position) and GRIPPER_CLOSED (1900 pulses), with the
actual write speed set to 300 for responsive yet stable movement.

To achieve smooth motion, the system applies exponential smoothing to
the first four joints. This low-pass filter effectively suppresses
high-frequency jitter from Leap Motion data while maintaining
responsiveness to deliberate hand movements. The smoothing factor of 0.3
provides a balance between noise rejection and tracking speed.

The system dispatches joint commands with speed parameters empirically
tuned to achieve coordinated motion without perceptible lag between the
operator\'s hand and the robotic arm. Joints 1 through 4, which govern
the base rotation, shoulder pitch, elbow bend, and wrist pitch, are
commanded at a speed of 300 pulses per second, balancing responsiveness
with smooth tracking of the palm's continuous movement. Joint 5, which
controlling wrist rotation based on thumb-index finger difference,
operates at a slightly reduced speed of 250 to mitigate overshoot caused
by rapid changes in the heuristic rotation estimate. Joint 6, the
gripper, is also set to 300, ensuring that the opening and closing
actions follow index finger bending promptly. All speed values were
selected based on testing to ensure that the 6-DOF arm moves as a
coherent whole, with no individual joint lagging noticeably behind the
others during typical operation.

From data reception through mapping calculation to command dispatch, the
complete processing pipeline runs at approximately 30 frames per second,
constrained by the Matlab-side data transmission rate. Each frame
triggers a write to all six servos, maintaining continuous tracking of
the operator\'s hand movements. The system logs frame counts and key
metrics every 20 frames, providing visibility into operational status
without overwhelming the console.

[]{#_Toc1828681058 .anchor}**Chapter 4. Implementation & Result**

[]{#_Toc2004069589 .anchor}**4.1 System Implementation**

[]{#_Toc1264062775 .anchor}4.1.1 Physical Setup and Hardware Deployment

To ensure the accuracy of gesture capture and the safety of the robotic
arm\'s movement, the Leap Motion sensor is placed horizontally on the
tabletop directly in front of the operator, with the sensing window
vertically upward, to ensure that the hand is within its optimal sensing
area. The center axis of the sensor is logically aligned with the base
center of the robotic arm in the virtual coordinate system to minimize
the operator\'s spatial cognitive burden.

The SO-ARM100 robotic arm is fixed to a stable horizontal tabletop using
a clamp. Due to its use of the STS3215 bus servo, all joints are
cascaded through a single-wire serial bus, simplifying the wiring layout
and avoiding cable entanglement issues during large-range rotations. The
robotic arm is connected to the host through a Waveshare bus servo
driver board. The driver board receives serial commands from the
computer via the USB Type-C interface and converts the signals into the
servo communication protocol. To ensure stable current during heavy-load
movements, the driver board is connected to an external 12V/5A DC
regulated power supply to prevent the servo from resetting due to
under-voltage during high-load operation.

After the hardware connection is completed, the st_ping.py test script
in the Python environment is used to conduct online detection of all the
servos. The script sends Ping commands to IDs 1 to 6 one by one. All the
servos return correct responses, indicating that the serial
communication is normal, the servo power supply is stable, and the ID
allocation is correct. The Leap Motion Controller performs self-check
through its official SDK. In the Matlab environment, the version query
function of the Matleap library is called successfully, and the SDK
version number is returned, confirming that the sensor is working
properly.

![wps](media/image11.png){width="3.970138888888889in"
height="2.6534722222222222in"}

Figure 9. Hardware physical deployment perspective view

[]{#_Toc47339654 .anchor}4.1.2 Software Integration and Communication

The system software adopts a mixed programming architecture of Matlab
and Python, and runs under the Windows operating system environment.

First, install the official Leap Motion SDK for Windows to ensure the
normal operation of the sensor driver. Then, add the open-source Matleap
library to the Matlab path. Matleap encapsulates the Leap Motion C++ SDK
through MEX technology, allowing developers to directly access hand
tracking data in the Matlab environment. Additionally, the TCP/IP client
function of Matlab is provided by the built-in tcpclient function,
without the need for additional toolbox installation.

Python side configuration: Create an independent Python virtual
environment to isolate project dependencies. Install the following core
libraries in this environment:

pyserial: for serial communication with the Waveshare driver board;

> STSservo_sdk: encapsulates the control instructions for the bus servo,
> including angle writing, position reading, torque enablement, etc.;

numpy: for data processing and numerical calculation.

Configuration file preparation: The system operation depends on two key
configuration files.

> home_position.json: Stores the return position angles of the six
> servos, in pulse numbers. It has been confirmed that the STS3215 servo
> uses a 12-bit resolution (0--4095), so all angle values are limited
> within this range. For example, the return pulse for ID1 is 2048,
> corresponding to the middle angle.
>
> right_hand_thresholds.txt: Stores the calibrated fingertip-to-palm
> distance thresholds for fist detection (see Section 4.2.3 for
> details).

[]{#_Toc1068615388 .anchor}4.1.3 System startup and operation process

To simplify the system deployment and daily debugging, a one-click
startup script named \"start.bat\" was developed. This script can
perform the following operations (as shown in the figure). The complete
process of the system operation is as follows:

***Step 1.Python side initialization***

Hand_server.py first reads the home_position.json and
right_hand_thresholds.txt configuration files. Then, it opens the
corresponding COM port for the Waveshare driver board with a baud rate
of 1,000,000 bps. Next, it calls the ping() method to sequentially
detect the ID1 to ID6 servos, confirming that all are online, and
enables the torque registers of all servos (including the previously
problematic ID6). Finally, it creates a TCP Socket server and starts
waiting for the connection from the Matlab client.

![C:/Users/sting/Pictures/Screenshots/屏幕截图 2026-04-16
212438.png屏幕截图 2026-04-16
212438](media/image12.png){width="5.143055555555556in"
height="1.0923611111111111in"}

Figure 10. Servos initialization

***Step 2 .Matlab side initialization***

The real_time_control.m script first calls the initialization function
of Matlab to start the Leap Motion hardware and creates a graphical
window for real-time display of hand coordinates and finger distance
information. Then, it uses the tcpclient function to connect to
localhost:65432 with a timeout of 5 seconds. After the connection is
successful, the Matlab side enters the main control loop.

![屏幕截图 2026-04-16 212419](media/image13.png){width="5.875in"
height="1.3319444444444444in"}

Figure 11. Matlab Command Board

![C:/Users/sting/Pictures/Screenshots/屏幕截图 2026-04-16
212345.png屏幕截图 2026-04-16 212345](media/image14.png){width="2.8in"
height="1.351388888888889in"}

Figure 12. Matlab Running Interface

***Step 3 .Real-time control loop***

The Matlab side reads the current frame of hand data from Leap Motion at
approximately 30 Hz, including the three-dimensional coordinates of the
palm (x, y, z) and the distances from the five finger tips to the palm
center. These eight floating-point numbers are formatted as a
comma-separated string , and sent via TCP connection to the Python side.
After receiving the data string, the Python side parses, maps, and
performs smoothing filtering, and finally writes the six target angles
to the corresponding servos using the WritePosEx method. On the Python
side, the relevant data can be clearly seen, allowing the operator to
understand the current position of the hand on the coordinate axis.

![C:/Users/sting/Pictures/Screenshots/屏幕截图 2026-04-16
212525.png屏幕截图 2026-04-16
212525](media/image15.png){width="6.1090277777777775in"
height="3.845833333333333in"}

Figure 13. Hand data flow

***Step 4 .Termination method***

When the operator presses the space bar in the Matlab graphical window,
the Matlab side exits the main loop, closes the TCP connection, and
releases the Leap Motion resources. After detecting the connection
closure, the Python side remains in the listening state or is manually
terminated through keyboard interruption (Ctrl+C).

Since there is already a simplified \"start.bat\" program for this
project, the operator can simply double-click this startup program and
input the corresponding numbers through the menu options to perform the
required operations. This startup program enables one-click dual startup
(Matlab + Python), allowing for the separate launch of Matlab or Python,
as well as the reconfiguration of home position and other related
operations.

![屏幕截图 2026-04-10
122034](media/image16.png){width="6.125694444444444in"
height="1.9284722222222221in"}

Figure 14. Start.bat for simplification

[]{#_Toc813086255 .anchor}4.1.4 Function Validation

After the overall integration was completed, each functional module of
the system was verified one by one. There was no abnormal jump in Leap
Motion data. The Python console printed the receiving count every time
it received a frame of data. There were no connection timeouts or
sending failure errors on the Matlab side. When the palm was moved
manually left and right, ID1 (the base) rotated accordingly; when moved
forward and backward, ID2 (shoulder pitch) responded; when moved up and
down, ID3 (elbow bending) responded. The mapping direction was
consistent with expectations. Fist detection and gripper: When the
operator made a fist, ID6 (the gripper) reliably closed; when the
fingers were extended, the gripper opened. There was no significant
delay in the response. After enabling exponential smoothing, the tremor
of the robotic arm movement significantly decreased, and the tracking
process was smooth. The above verification results indicate that the
system has successfully achieved all the predetermined functions and is
ready for experimental testing.

[]{#_Toc1102241924 .anchor}**4.2 Experimental Results**

This section reports the performance indicators and effects achieved by
the system during actual operation. The experiments were conducted in a
desktop experimental environment. The operator placed their hand
approximately 150 mm to 400 mm above the Leap Motion Controller, and the
robotic arm was positioned about 35 cm to the left of the sensor. All
tests were completed on a Windows system.

[]{#_Toc1186077646 .anchor}4.2.1 Real-time Tracking and Response
Performance

The end-to-end latency of the system refers to the total time elapsed
from when the operator completes a hand movement to when the
corresponding joint of the robotic arm starts to move. Through an
indirect measurement method (the difference between the time stamp sent
from the Matlab end and the time stamp received at the Python end, plus
the estimated response time of the servo), the end-to-end latency of the
system was measured to be approximately 80--100 ms. Within this latency
range, if the operator\'s hand movement speed is too fast during actual
operation, the robotic arm will lag behind in following, while slow
movements will show good synchronization.

Regarding the control frequency, the Matlab end sends hand data frames
to the Python end at a rate of approximately 30 Hz. The measured sending
interval is stable at around 33 ms, with a fluctuation range not
exceeding ±5 ms. This frequency is much higher than the main frequency
components of natural hand movements, meeting the requirements of the
Nyquist sampling theorem and capable of fully preserving the details of
gesture movements.

In terms of TCP/IP communication latency, in a local loopback
environment, the time interval from when the Matlab calls the write
function to when the Python end\'s recv function returns data was
measured multiple times and was all less than 1 ms. This latency is
negligible compared to the control cycle (33 ms), indicating that the
overhead of the communication protocol stack will not become a
bottleneck for the system\'s real-time performance.

[]{#_Toc1463784868 .anchor}4.2.2 Gesture Mapping and Joint Motion
Consistency

The system has achieved the mapping from the natural hand movements to
the joint angles of the six-degree-of-freedom robotic arm. Table 7
summarizes the control sources for each joint and their actual movement
performance.

Table 7 Gesture Mapping and Joint Response Results

  ------------------------------------------------------------------------
   **Joint     **Joint    **locus of    **Results**
    ID**     Function**   control**     
  --------- ------------- ------------- ----------------------------------
    ID 1    Base rotation Hand X-axis   When the operator moves their palm
                                        to the left, the base rotates
                                        counterclockwise; when moving to
                                        the right, it rotates clockwise.
                                        The rotation angle has an
                                        approximately linear relationship
                                        with the palm offset amount, and
                                        the movement is smooth.

    ID 2      Shoulder    Hand Z-axis   When the operator moves their palm
              elevation                 forward, the shoulder joint bends
                                        forward; when moving backward, the
                                        shoulder joint bends backward. The
                                        response direction is intuitive.

    ID 3     Elbow joint  Thumb Y-axis  When the operator lifts their palm
               bending                  upwards, the angle of the elbow
                                        joint increases (bends); when
                                        lowering it, the angle of the
                                        elbow joint decreases (extends).
                                        This mapping simulates the natural
                                        movement pattern of the human arm.

    ID 4        Wrist     Fixed         After testing, enabling this
             depression                 degree of freedom would introduce
                                        unintended wrist movements,
                                        affecting the intuitiveness of
                                        operation. Therefore, in the final
                                        system, it was fixed at the
                                        resting position and remained
                                        stable during actual operation.

    ID 5     Wrist joint  Thumb-index   When the operator rotates the hand
              rotation    finger        so that the thumb and the index
                          distance      finger come closer or move apart,
                                        the wrist joint rotates
                                        accordingly. This heuristic
                                        mapping can sensitively capture
                                        the hand rotation intention, with
                                        a rotation range of approximately
                                        ±60°.

    ID 6        Claw      Distance from When the index finger is fully
                          the fingertip extended, the clamping opens to
                          to the palm   the maximum extent; when it is
                          center        fully bent (in a fist)， the
                                        clamping closes. The middle
                                        position can be adjusted
                                        continuously， and the opening and
                                        closing of the clamping is in a
                                        good linear relationship with the
                                        degree of bending of the index
                                        finger.
  ------------------------------------------------------------------------

[]{#_Toc259616444 .anchor}4.2.3 Fingertip Detection and Gripper Control
Effect

The control of the gripper is based on the distance from the fingertip
of the index finger to the center of the palm. The system acquires the
threshold values of index_min (fully bent) and index_max (fully
extended) for each operator through calibration scripts in advance.
During real-time operation, the system calculates the relative position
of the current index finger distance within the threshold range and
linearly maps it to the opening and closing degree of the gripper. The
positioning pulse 2048 corresponds to opening, and 1900 pulses
correspond to closing.

To prevent the gripper from frequently shaking near the threshold
boundary, the system incorporates a 5-frame stability hysteresis logic:
the gripper\'s target position will only be updated when the gripping
amplitude exceeds the threshold for five consecutive frames. In actual
tests, this mechanism effectively suppresses the erroneous actions of
the gripper caused by minor hand tremors.

Tests conducted on three operators with different hand sizes showed that
after personalized calibration, the success rate of the fist detection
reached 100% (a total of 50 fist movements, and the grippers closed
reliably each time). The movement speed of the grippers was set at 300
pulses per second, and the travel time from fully open to fully closed
was approximately 0.5 seconds. The operators generally considered the
response speed to be moderate and natural.

Table 8. Hand opening and closing detection data

  -----------------------------------------------------------------------------------------------
   **Tester**   **Index_min**   **Index_max**   **Palm_min**   **Palm_max**    **Punching test
                                                                                success rate**
  ------------ --------------- --------------- -------------- -------------- --------------------
       A          34.28 mm        93.66 mm        33.17 mm       87.54 mm            100%

       B          38.61 mm        99.73 mm        36.33 mm       94.78 mm            100%

       C          31.76 mm        89.47 mm        31.12 mm       82.56 mm            100%
  -----------------------------------------------------------------------------------------------

[]{#_Toc1834287251 .anchor}4.2.4 Motion Smoothing and Stability

The hand data collected by Leap Motion contains certain high-frequency
noise. If not processed, directly mapping it to the servo mechanism will
cause the robotic arm to tremble significantly. The system uses an
exponential smoothing filter to perform low-pass filtering on the target
angles of the first four joints, with a smoothing factor set to 0.3.
Comparative experiments show that in the unfiltered state, the robotic
arm still exhibits visible rapid tremors when held still, especially at
the shoulder and elbow joints, which affect the operation experience.
The high-frequency tremors of the filtered robotic arm are significantly
suppressed, remaining stable in the static state and having a smoother
trajectory during following movements. At the same time, since 30% of
the new data weight is retained, the system can still maintain a
relatively sensitive response to the operator\'s intentional movements
without showing obvious tracking lag. This smoothing strategy achieves
an engineering-acceptable balance between noise suppression and response
sensitivity.

[]{#_Toc1738074872 .anchor}4.2.5 Overall System Performance

Based on the results of the above experiments, this system has
successfully achieved real-time control of a six-degree-of-freedom
robotic arm using visual gestures. The operator can intuitively control
the base rotation, shoulder joint elevation, elbow joint bending, wrist
joint rotation, and gripper opening and closing of the robotic arm
through natural hand movements (translation, up and down, front and
back) and finger bending actions. The end-to-end delay control of the
system is within 100 ms, and the operator feels smooth and natural.

[]{#_Toc1751807210 .anchor}**4.3 Problems and Solutions**

During the development of this project, several technical challenges
were encountered and successfully resolved. This section summarizes the
main problems and their corresponding solutions.

[]{#_Toc622978100 .anchor}4.3.1 Environmental compatibility issue

In the official documentation of the SO-ARM100, no dedicated SDK file
for the Windows environment is provided. This absence posed a
significant challenge during the early stages of hardware debugging.
Initially, considerable time was spent setting up virtual machines and
configuring an Ubuntu environment to interface with the robotic arm. Due
to unfamiliarity with the Linux-based development workflow, this process
encountered repeated setbacks, including compatibility issues, driver
conflicts, and difficulties in establishing reliable communication
between the host Windows machine and the virtualized Ubuntu system. Each
failed attempt required restarting the configuration process, which
significantly delayed the overall project timeline.

However, following guidance from the project supervisor, an alternative
approach was identified. Instead of relying on a complete
SO-ARM100-specific SDK for Windows, the solution was to work directly
with the servo hardware and the Waveshare control board. By starting
from the official Waveshare Python control library, which provides
robust Windows support, a custom library tailored to the specific needs
of this project was gradually developed. This bottom-up approach
involved understanding the low-level communication protocols and
systematically building functions for servo detection, position reading,
and angle writing. The resulting library not only bypassed the need for
a virtual machine but also eliminated the complexity of maintaining a
separate Ubuntu environment.

The custom library proved to be highly advantageous. It simplified the
program startup process, reduced dependency on external tools, and
improved the portability of the entire system. Since the library is
written in pure Python and relies only on standard serial communication,
it can be easily deployed on any Windows computer without additional
environment configuration. This flexibility makes the system far more
accessible for future development, testing, and potential deployment
across different hardware setups, significantly enhancing the
reproducibility and scalability of the project.

[]{#_Toc1410147575 .anchor}4.3.2 The servo angle range does not match

During initial testing, servo positions read from the
\`home_position.json\` file were found to exceed the expected 0-1023
range, with values reaching up to 3543 pulses. This caused erratic servo
behavior and triggered red warning lights on the affected servos.
Analysis revealed that the STS3215 servos operate with 12-bit resolution
(0-4095), contrary to the initially assumed 10-bit range (0-1023).
Although the home positions were correctly saved within the 0-4095
range, the control algorithm erroneously clamped them to 0-1023. The
solution was to modify the position limiting function to accept the full
0-4095 range and update all scaling factors accordingly.

Additionally, a critical misunderstanding arose regarding the concept of
resetting the robotic arm. Initially, it was mistakenly believed that
resetting meant driving all servos to the zero position (0 pulses).
Consequently, numerous reset commands were issued, repeatedly attempting
to move the servos to zero. This led to delayed servo responses and
significant positional errors, causing substantial delays during early
debugging and consuming considerable time. The root cause was eventually
identified: a proper reset should return each servo to its neutral or
home position, as servos sometimes need to rotate counterclockwise from
their current positions rather than always clockwise toward zero. Once
this was understood and the reset logic was corrected to target the
stored home positions instead of absolute zero, the servos responded
reliably and positioning accuracy improved markedly.

[]{#_Toc720764733 .anchor}4.3.3 The gripper does not respond to the fist
detection

When a fist was detected, the gripper consistently failed to close.
Debugging revealed that the position write command was being sent
successfully, yet the actual servo position remained unchanged at 2040
pulses. Further investigation indicated that the torque enable register
for Servo ID6 had not been properly initialized. The solution involved
adding explicit torque enable commands during system initialization
using the \`write1ByteTxRx\` method to set the torque enable register
to 1. After this modification, the gripper responded reliably to fist
detection commands.

To accommodate the individual hand characteristics of different
operators, a separate Matlab script was developed. This script allows
the Leap Motion to capture the hand opening and closing range for each
person and use this personalized data for gripper recognition. By
calibrating the threshold values based on the user\'s natural hand
range, the system adapts to varying hand sizes and movement patterns.
This functionality significantly enhances the adaptability of the
robotic arm, enabling it to be controlled intuitively by a wider range
of users without requiring manual threshold adjustments.

[]{#_Toc2085098451 .anchor}4.3.4 Unintentional wrist rotation movement

Preliminary testing revealed that when the wrist pitch joint was
controlled based on the distance between the middle and ring fingers, it
moved erratically, producing unnatural arm motions. This heuristic
mapping proved unreliable and detracted from the intuitiveness of the
control interface. Since the robotic arm\'s gripper is already oriented
perpendicular to the desktop by default, an additional degree of wrist
pitch is not necessary during typical grasping operations. Rather than
investing significant time in refining this mapping, the decision was
made to completely disable ID4 and keep it fixed at its home position.
This simplification improved overall control stability without
sacrificing any essential functionality.

[]{#_Toc1611514211 .anchor}4.3.5 TCP/IP Data Parsing Error

Due to the incorrect format of the data string received from Matlab,
communication failures occur occasionally. The error message \"Unable to
convert string to floating point number 83.885.76 indicates that the
numerical value occasionally contains multiple decimal points. After
investigation, it was found that this was caused by occasional frame
loss, resulting in an incomplete string format. To address this, the
implemented solution adopted a robust parsing logic, which split the
incoming string by commas, attempted to convert each part to a floating
point number, and replaced the parts that could not be converted with
zero. Additionally, the entire parsing process was wrapped in a
try-except block to prevent the server from crashing due to a single
format error frame.

[]{#_Toc655588313 .anchor}4.3.6 Motion Tremors & Instability

Due to the presence of high-frequency noise in the Leap Motion hand
tracking data, the robotic arm exhibited significant jitter during
operation. Initially, a simple exponential smoothing method with a
smoothing factor of 0.3 was adopted. Although this reduced the jitter,
it introduced tracking lag. After debugging, the smoothing factor was
adjusted to 0.7 for the previous frame and 0.3 for the new frame,
achieving an acceptable balance between noise suppression and
responsiveness.

These solutions collectively enabled stable and reliable real-time
control of the six-degree-of-freedom robotic arm.

[]{#_Toc1881667481 .anchor}**4.4 Safety, Ethics, and Sustainability
Analysis**

[]{#_Toc1341167445 .anchor}4.4.1 Safety & Reliability

The development of this system strictly adheres to the principle of
human factors engineering, addressing the uncertainties of visual
control in the medical environment and prioritizing human intervention.
The software architecture ensures the absolute priority of operator
instructions. Through physical switches or specific \"global stop\"
gestures, operators can regain control or emergency shut down the system
at any time, in line with the safety standards of medical devices.

[]{#_Toc1012889203 .anchor}4.4.2 Ethical Considerations

The project strictly complies with data protection and ethical
guidelines throughout the entire research and development cycle.

For sensitive biometric data such as hand movement trajectories, the
system encrypts at the transmission layer. All questionnaires and
experimental samples are anonymized, and technical means are used to
ensure that the trajectory data cannot be traced back to a specific
individual. In response to public concerns about AI-assisted surgery,
this project insists on algorithm transparency and has written detailed
operation guidelines and principle explanations, aiming to build a
bridge of trust between operators and technology. All participant
surveys are conducted with clear disclosure of the research purpose,
risks, and data usage.

[]{#_Toc525965052 .anchor}4.4.3 Sustainability Analysis

The system can be maintained at low cost and thereby its lifecycle
extended. In terms of environmental sustainability, energy efficiency is
enhanced through a simplified gesture recognition algorithm that lowers
computing resource consumption and operational carbon footprint, and
component replaceability is ensured via modular hardware design,
allowing individual faulty parts to be replaced rather than scrapping
the entire machine，aligning with circular economy principles. For
social sustainability, the project aims to bridge the technology gap by
offering a cost-effective remote surgery and teaching solution for
medical institutions in resource-limited areas.

[]{#_Toc851937912 .anchor}**Chapter 5. Conclusion & Recommendation**

[]{#_Toc1247012435 .anchor}**5.1 Program Summary**

The project successfully implemented a complete vision-based gesture
control system for the SO-ARM100 robotic arm. The following sections
describe the implementation status of each component.

All hardware components were successfully integrated and tested. The LMC
was connected via USB and verified to capture hand data at approximately
120Hz through the Matleap interface. The SO-ARM100 robotic arm was
assembled and its six STS3215 servos were confirmed operational via the
st_ping.py test script, which successfully detected all servos (IDs 1
through 6) responding on the serial bus. The Waveshare driver board
provided stable communication at 1,000,000 baud rate between the
computer and the servo chain.

The software architecture was fully implemented according to the design
specifications. On the Matlab side, the real_time_control.m script
successfully initializes the Leap Motion hardware, establishes TCP/IP
connection with the Python server, and transmits hand data at a stable
30Hz rate. The graphical interface displays real-time palm position and
finger distances, with spacebar functionality for graceful termination.

On the Python side, the hand_server.py script successfully performs the
following functions:

1.  Loads home positions from home_position.json (six joint angles) and
    finger thresholds from right_hand_thresholds.txt;

2.  Initializes serial communication and verifies all six servos are
    online via the ping() method;

3.  Creates a TCP server listening on localhost:65432 and maintains
    stable connection with Matlab;

4.  Receives hand data strings (palm coordinates + 5 finger distances)
    and parses them reliably;

5.  Computes fist amount using index finger distance with hysteresis
    logic (5-frame stability check);

6.  Estimates wrist rotation using thumb-index finger difference;

7.  Maps palm coordinates to joint angles according to the defined
    mapping:

> ID1 (base rotation): palm x-coordinate
>
> ID2 (shoulder pitch): palm z-coordinate
>
> ID3 (elbow bend): palm y-coordinate
>
> ID4 (wrist pitch): maintained at home position
>
> ID5 (wrist rotation): based on thumb-index difference
>
> ID6 (gripper): based on index finger bend

8.  Applies exponential smoothing (0.3 factor) to first four joints for
    motion stability;

9.  Dispatches commands with joint-specific speeds (300 for joints 1-4
    and 6, 250 for joint 5);

10. Logs frame count and key metrics every 20 frames for debugging.

The TCP/IP communication between Matlab and Python was successfully
established and tested. Data transmission latency was measured under 1ms
in local loopback, well within the 33ms control cycle requirement. The
complete pipeline from hand movement to servo response achieves
end-to-end latency of approximately 80-100ms, which is imperceptible to
the operator.

A batch script start.bat was developed to automate environment setup and
program execution. This script activates the Python virtual environment,
sets the correct Python path, and launches either the complete system or
individual components based on user selection. This significantly
reduces the complexity of system deployment and testing.

Several features were considered but not implemented due to time
constraints or performance considerations. Wrist pitch (ID4) was
intentionally disabled after preliminary testing revealed that its
inclusion introduced unintended movements without meaningfully improving
the intuitive nature of the control interface, thus simplifying the
mapping while maintaining sufficient functionality for demonstration
purposes. Synchronous write (sync_write) was not utilized; instead, the
system employs sequential writes to each servo, which remains adequate
for the 30Hz control frequency without introducing perceptible timing
discrepancies between joints. Advanced tremor filtering, such as the
empirical mode decomposition based adaptive filter proposed in the
literature, was not implemented; the system relies on exponential
smoothing for noise reduction, which effectively suppresses
high‑frequency jitter from Leap Motion data while maintaining
responsiveness to deliberate hand movements.

Overall, the core objectives of real-time vision-based gesture control
of a 6-DOF robotic arm were successfully achieved, with all critical
components functioning as designed.

[]{#_Toc1245083972 .anchor}**5.2 Limitation**

Despite the successful implementation of real-time vision-based gesture
control for the SO-ARM100 robotic arm, several limitations remain in the
current system.

The current system is designed to control only a single robotic arm.
While the Leap Motion sensor is capable of tracking both hands
simultaneously, the software architecture and motion mapping strategy
are configured for single-handed operation. This limitation restricts
the system\'s applicability in scenarios that require bi-manual
coordination, such as complex surgical procedures or assembly tasks that
demand simultaneous manipulation of multiple objects. Extending the
system to support dual-arm control would require significant
modifications to the communication protocol, motion mapping, and
coordination algorithms to prevent interference between the two arms.

The system operates purely on position control and provides no haptic or
force feedback to the operator. In teleoperation scenarios, particularly
in surgical applications, force feedback is crucial for enabling the
operator to perceive tissue properties, applied forces, and potential
collisions. Without such feedback, the operator must rely solely on
visual cues, which limits the precision and safety of delicate
manipulations. The absence of force feedback also increases the risk of
applying excessive force that could damage the environment or the
robotic arm itself. Integrating force sensing into the end-effector or
joint-level torque sensing would be necessary to address this
limitation, but such hardware was not available in the current setup.

The system recognizes only a small set of gestures: palm position for
arm movement, index finger bending for gripper control, and thumb-index
difference for wrist rotation. More complex gestures, such as pinch
gestures with varying force levels, multi-finger combinations, or
dynamic gestures, are not implemented. This limited vocabulary
constrains the range of commands that can be conveyed to the robotic arm
and may not be sufficient for more sophisticated teleoperation tasks.

These limitations highlight the gap between the current prototype system
and the requirements for practical deployment in high-stakes
environments such as surgical robotics. Addressing these limitations
would require hardware upgrades, algorithmic improvements, and more
robust tracking solutions.

[]{#_Toc1045661036 .anchor}**5.3 Improvement**

Several directions are proposed to address the limitations of the
current system and to advance its capabilities toward practical
applications.

First, extending to dual-arm control would leverage the Leap Motion
controller\'s inherent ability to track both hands simultaneously. This
would enable the execution of bimanual tasks that are common in surgical
procedures and complex manipulations, such as tissue retraction,
suturing, or coordinated assembly. Dual-arm control would also allow for
more natural human-robot interaction, as operators could use both hands
to intuitively command two manipulators in parallel, significantly
expanding the system\'s operational dexterity and task repertoire.

Second, integrating force feedback would provide critical tactile
perception that is currently lacking. This can be realized through two
complementary approaches: (i) installing miniature force/torque sensors
at the end-effector to directly measure interaction forces with the
environment, or (ii) monitoring joint motor currents to estimate
external loads based on dynamic models. Such haptic feedback is
indispensable for delicate operations where excessive force could damage
tissue or fragile objects. Furthermore, force feedback would enable
impedance or admittance control strategies, allowing the system to adapt
its stiffness and comply with environmental constraints---a key
requirement for safe physical interaction.

Collectively, these improvements would advance the system from a
proof-of-concept demonstration prototype toward a robust and practical
tool for surgical robotics, teleoperation, and human-machine
collaboration. Each direction addresses a specific limitation while
contributing to the overarching goal of achieving higher autonomy,
reliability, and usability in real-world settings.

[]{#_Toc1566348651 .anchor}**References**

1.  Meftah, S., Sahnoun, M. H., Messaadia, M. and Benslimane, S. M.,
    \'Enhancing decision-making in Industry 5.0 through adaptive human
    machine interfaces: A systematic literature review\', Computer
    Standards & Interfaces, 2025, 104091.

2.  []{#_Ref631464619 .anchor}Gunawardane, H., Medagedara, N. and
    Madhusanka, B. G. D. A., \'Control of robot arm based on hand
    gesture using leap motion sensor technology\', International Journal
    of Robotics and Mechatronics, 2017, 10.

3.  Korayem, M. H., Madihi, M. A. and Vahidifar, V., \'Controlling
    surgical robot arm using Leap Motion Controller with Kalman
    filter\', Measurement, 2021, 178, 109372.

4.  Zhang, Q. and Deng, F., \'Dynamic gesture recognition based on Leap
    Motion and HMM-CART model\', Journal of Physics: Conference Series,
    2017, 910(1), 012037.

5.  []{#_Ref20435 .anchor}Chen, L., Li, C., Fahmy, A. and Sienz, J.,
    \'GestureMoRo: an algorithm for autonomous mobile robot
    teleoperation based on gesture recognition\', Scientific Reports,
    2024, 14(1), 6199.

6.  Mariappan, R., Gayathri, P., Pushpalatha, P., Rishik, V. S. S. and
    Satish, T., \'Real time robotic arm using Leap Motion Controller\',
    Journal of Physics: Conference Series, 2023, 2466(1), 012023.

7.  Reddington, H., Bogursky, A., Ballinger, Z., Widdowson, K., Guart,
    J., Walter, D. and Lou, F., \'Robotic Surgery Training During
    General Surgery Residency: A National Survey Study\', Journal of
    Surgical Education, 2025, 82(11), 103702.

8.  Zhang, X., Wang, J., Dai, X., Shen, S. and Chen, X., \'A non-contact
    interactive system for multi-modal surgical robots based on
    LeapMotion and visual tags\', Frontiers in Neuroscience, 2023, 17,
    1287053.

9.  Korayem, M. H. and Vahidifar, V., \'Detecting hand\'s tremor using
    Leap Motion Controller in guiding surgical robot arms and
    laparoscopic scissors\', Measurement, 2022, 204, 112133.

10. Saint-Louis, H., \'Machine-human interaction: a paradigm shift\', in
    International Conference on Human-Computer Interaction, Springer,
    2021, pp. 123-136.

11. []{#_Ref21659 .anchor}Jain, N., Gupta, V., Temperini, V. and others,
    \'Human machine interactions: from past to future - a systematic
    literature review\', Journal of Management History, 2024, 30(2) pp.
    263-302.[]{#_Ref21699 .anchor}

12. Zhao, W., \'A concise tutorial on human motion tracking and
    recognition with Microsoft Kinect\', Science China Information
    Sciences, 2016, 59(9), 93101.

13. Zabatani, A., Surazhsky, V., Sperling, E., Moshe, S. B., Menashe,
    O., Silver, D. H. and Kimmel, R., \'Intel® RealSense™ SR300 coded
    light depth camera\', IEEE Transactions on Pattern Analysis and
    Machine Intelligence, 2019, 42(10) pp. 2333-2345.

14. []{#_Ref21764 .anchor}Guzsvinecz, T., Szucs, V. and Sik-Lanyi, C.,
    \'Suitability of the Kinect Sensor and Leap Motion Controller - A
    Literature Review\', Sensors, 2019, 19(5), 1072. []{#_Ref21904
    .anchor}

15. Cheng, X., Cui, W., Liu, B. and Yang, H., \'Application of gesture
    recognition fusion algorithm based on double LeapMotion in hand
    function rehabilitation in large space\', in 2020 International
    Conference on Virtual Reality and Visualization (ICVRV), IEEE, 2020,
    pp. 249-252.[]{#_Ref21849 .anchor}

16. Najafinejad, A. and Korayem, M. H., \'Detection and minimizing the
    error caused by hand tremors using a leap motion sensor in operating
    a surgeon robot\', Measurement, 2023, 221, 113544.

17. Mulla, D. M., Majoni, N., Tilley, P. M. and Keir, P. J., \'Two
    cameras can be as good as four for marker-less hand tracking during
    simple finger movements\', Journal of Biomechanics, 2025, 181,
    112534.

18. Fonk, R., Schneeweiss, S., Simon, U. and Engelhardt, L., \'Hand
    motion capture from a 3D Leap Motion Controller for a
    musculoskeletal dynamic simulation\', Sensors, 2021, 21(4), 1199.

19. Liu, Z., Wang, B., Lin, J., Xu, H., Li, C., Chen, R. and Li, J.,
    \'Surgical applications of the Ultralearg 3Di-based
    gesture-controlled 3D imaging visualization system\', Computers in
    Biology and Medicine, 2025, 194, 110548.

20. Luongo, F., Hakim, R., Nguyen, J. H., Anandkumar, A. and Hung, A.
    J., \'Deep learning-based computer vision to recognize and classify
    suturing gestures in robot-assisted surgery\', Surgery, 2021, 169(5)
    pp. 1240-1244.

21. []{#_Ref22074 .anchor}Paulo, S. F., Relvas, F., Nicolau, H., Rekik,
    Y., Machado, V., Botelho, J. and Lopes, D. S., \'Touchless
    interaction with medical images based on 3D hand cursors supported
    by single-foot input: A case study in dentistry\', Journal of
    Biomedical Informatics, 2019, 100, 103316.

22. Cong, V. D., \'Control the Robot Arm through Vision-Based Human Hand
    Tracking\', FME Transactions, 2024, 52(1).

23. Khanesar, M. A., Yan, M., Isa, M., Piano, S. and Branson, D. T.,
    \'Precision Denavit-Hartenberg parameter calibration for industrial
    robots using a laser tracker system and intelligent optimization
    approaches\', Sensors, 2023, 23(12), 5368.

24. []{#_Ref634557107 .anchor}Adar, N. G., \'Real time control
    application of the robotic arm using neural network based inverse
    kinematics solution\', Sakarya University Journal of Science, 2021,
    25(3) pp. 849-857.

25. []{#_Ref634321809 .anchor}Vicente, E., Quijano, Y., Ferri, V. and
    Caruso, R., \'Robot-assisted cholecystectomy with the new da Vinci
    SP® surgical system: first report in Spain with video\', Updates in
    Surgery, 2025, pp. 1-4.

26. Perry, J., \'Matleap: MATLAB mex interface for the Leap Motion
    Controller\', GitHub (2020), https://github.com/jeffsp/matleap
    \[accessed 1 April 2026\].

[]{#_Toc1767232431 .anchor}**Appendices**

A.  []{#_Toc29146160 .anchor}Overall System Framework

    ![你的段落文字](media/image17.png){width="5.115277777777778in"
    height="8.70625in"}

B.  []{#_Toc233239604 .anchor}Python Core Programme (hand_server.py)

    ![](media/image18.png){width="6.048611111111111in"
    height="6.191666666666666in"}

    ![](media/image19.png){width="6.089583333333334in"
    height="2.892361111111111in"}

    ![](media/image20.png){width="6.0569444444444445in"
    height="6.0625in"}

    ![](media/image21.png){width="5.540277777777778in"
    height="3.433333333333333in"}

    ![](media/image22.png){width="6.06875in"
    height="6.082638888888889in"}

    ![](media/image23.png){width="6.079861111111111in"
    height="1.429861111111111in"}

C.  []{#_Toc900368653 .anchor}Matlab Core Programme
    (real_time_control.m)

![](media/image24.png){width="5.973611111111111in"
height="8.172222222222222in"}

![](media/image25.png){width="6.129166666666666in"
height="0.6402777777777777in"}

![](media/image25.png){width="6.097916666666666in" height="7.26875in"}

![](media/image26.png){width="6.072222222222222in"
height="2.017361111111111in"}

![](media/image26.png){width="6.063888888888889in"
height="5.631944444444445in"}

![](media/image27.png){width="6.097222222222222in"
height="1.2152777777777777in"}

D.  []{#_Toc1326174209 .anchor}Resources & Costs

+-------------------------------------+---------------+---------------+---------------+
| **Hardware Items**                  | **Cost        | **Number**    | **Resource**  |
|                                     | (CNY)**       |               |               |
+:===============:+:=================:+:=============:+:=============:+:=============:+
| SO-ARM 100      | 3D printed torso  | 158           | 1             | Seeedstudio   |
|                 +-------------------+---------------+---------------+---------------+
|                 | STS3215 servos    | 105           | 6             | Feetech       |
|                 +-------------------+---------------+---------------+---------------+
|                 | Cables            | 1.5           | 6             | Feetech       |
|                 +-------------------+---------------+---------------+---------------+
|                 | Servo Bus         | 26            | 1             | Waveshare     |
+-----------------+-------------------+---------------+---------------+---------------+
| Leap Motion Controller              | 1500          | 1             | Ultraleap     |
+-------------------------------------+---------------+---------------+---------------+
| Data cable                          | 10            | 1             | Huawei        |
+-------------------------------------+---------------+---------------+---------------+
| **Total Cost:**                     | **2333**                                      |
+-------------------------------------+-----------------------------------------------+
