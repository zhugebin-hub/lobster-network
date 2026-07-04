# 电磁场与电磁波

## 第一章 矢量分析

### 1.1 矢量代数

**矢量运算**：
- **加法**：$\mathbf{A} + \mathbf{B}$
- **点积**：$\mathbf{A} \cdot \mathbf{B} = AB\cos\theta$
- **叉积**：$\mathbf{A} \times \mathbf{B} = AB\sin\theta\mathbf{a}_n$

**三重积**：
- 标量三重积：$\mathbf{A} \cdot (\mathbf{B} \times \mathbf{C}) = \mathbf{B} \cdot (\mathbf{C} \times \mathbf{A}) = \mathbf{C} \cdot (\mathbf{A} \times \mathbf{B})$
- 矢量三重积：$\mathbf{A} \times (\mathbf{B} \times \mathbf{C}) = \mathbf{B}(\mathbf{A} \cdot \mathbf{C}) - \mathbf{C}(\mathbf{A} \cdot \mathbf{B})$

### 1.2 正交坐标系

**直角坐标系**：$(x, y, z)$
**柱坐标系**：$(\rho, \varphi, z)$
**球坐标系**：$(r, \theta, \varphi)$

### 1.3 矢量微分算子

**梯度**：
$$\nabla f = \frac{\partial f}{\partial x}\mathbf{a}_x + \frac{\partial f}{\partial y}\mathbf{a}_y + \frac{\partial f}{\partial z}\mathbf{a}_z$$

**散度**：
$$\nabla \cdot \mathbf{A} = \frac{\partial A_x}{\partial x} + \frac{\partial A_y}{\partial y} + \frac{\partial A_z}{\partial z}$$

**旋度**：
$$\nabla \times \mathbf{A} = \begin{vmatrix} \mathbf{a}_x & \mathbf{a}_y & \mathbf{a}_z \\ \frac{\partial}{\partial x} & \frac{\partial}{\partial y} & \frac{\partial}{\partial z} \\ A_x & A_y & A_z \end{vmatrix}$$

**拉普拉斯算子**：
$$\nabla^2 f = \nabla \cdot \nabla f = \frac{\partial^2 f}{\partial x^2} + \frac{\partial^2 f}{\partial y^2} + \frac{\partial^2 f}{\partial z^2}$$

### 1.4 矢量积分定理

**高斯散度定理**：
$$\int_V (\nabla \cdot \mathbf{A}) dV = \oint_S \mathbf{A} \cdot d\mathbf{S}$$

**斯托克斯定理**：
$$\int_S (\nabla \times \mathbf{A}) \cdot d\mathbf{S} = \oint_C \mathbf{A} \cdot d\mathbf{l}$$

## 第二章 静电场

### 2.1 库仑定律

真空中两个点电荷之间的作用力：
$$\mathbf{F} = \frac{q_1 q_2}{4\pi\epsilon_0 R^2}\mathbf{a}_R$$

### 2.2 电场强度

点电荷的电场强度：
$$\mathbf{E} = \frac{q}{4\pi\epsilon_0 R^2}\mathbf{a}_R$$

连续分布电荷的电场强度：
$$\mathbf{E} = \int \frac{\rho dV}{4\pi\epsilon_0 R^2}\mathbf{a}_R$$

### 2.3 高斯定律

**积分形式**：
$$\oint_S \mathbf{D} \cdot d\mathbf{S} = Q$$

**微分形式**：
$$\nabla \cdot \mathbf{D} = \rho$$

### 2.4 电位

$$V = \int \frac{\rho dV}{4\pi\epsilon_0 R}$$

$$\mathbf{E} = -\nabla V$$

### 2.5 电介质中的静电场

**本构关系**：
$$\mathbf{D} = \epsilon\mathbf{E} = \epsilon_0\epsilon_r\mathbf{E}$$

**极化强度**：
$$\mathbf{P} = \chi_e\epsilon_0\mathbf{E}$$

### 2.6 边界条件

- 电场强度切向分量连续：$E_{1t} = E_{2t}$
- 电通密度法向分量连续（无自由电荷）：$D_{1n} = D_{2n}$

### 2.7 电容与部分电容

**平行板电容器**：
$$C = \frac{\epsilon S}{d}$$

**同轴电容器**：
$$C = \frac{2\pi\epsilon l}{\ln(b/a)}$$

### 2.8 静电场边值问题

**泊松方程**：
$$\nabla^2 V = -\frac{\rho}{\epsilon}$$

**拉普拉斯方程**：
$$\nabla^2 V = 0$$

**唯一性定理**：给定边界条件，泊松方程/拉普拉斯方程的解是唯一的。

**镜像法**：用镜像电荷代替边界上的感应电荷。

## 第三章 恒定磁场

### 3.1 安培力定律

$$d\mathbf{F} = I d\mathbf{l} \times \mathbf{B}$$

### 3.2 毕奥-萨伐尔定律

$$\mathbf{B} = \int \frac{\mu_0 I d\mathbf{l} \times \mathbf{a}_R}{4\pi R^2}$$

### 3.3 安培环路定律

**积分形式**：
$$\oint_C \mathbf{H} \cdot d\mathbf{l} = I$$

**微分形式**：
$$\nabla \times \mathbf{H} = \mathbf{J}$$

### 3.4 磁通密度与磁矢位

$$\nabla \cdot \mathbf{B} = 0$$

引入磁矢位：
$$\mathbf{B} = \nabla \times \mathbf{A}$$

### 3.5 介质中的磁场

**本构关系**：
$$\mathbf{B} = \mu\mathbf{H} = \mu_0\mu_r\mathbf{H}$$

**磁化强度**：
$$\mathbf{M} = \chi_m\mathbf{H}$$

### 3.6 边界条件

- 磁感应强度法向分量连续：$B_{1n} = B_{2n}$
- 磁场强度切向分量连续（无面电流）：$H_{1t} = H_{2t}$

### 3.7 电感

**自感**：
$$L = \frac{N\Phi}{I}$$

**互感**：
$$M_{12} = \frac{N_2\Phi_{21}}{I_1}$$

### 3.8 磁场能量

$$W_m = \frac{1}{2}\int_V \mathbf{B} \cdot \mathbf{H} dV$$

## 第四章 时变电磁场

### 4.1 法拉第电磁感应定律

$$\oint_C \mathbf{E} \cdot d\mathbf{l} = -\frac{d}{dt}\int_S \mathbf{B} \cdot d\mathbf{S}$$

### 4.2 位移电流

$$\mathbf{J}_d = \frac{\partial \mathbf{D}}{\partial t}$$

### 4.3 麦克斯韦方程组

**积分形式**：
$$\oint_S \mathbf{D} \cdot d\mathbf{S} = \int_V \rho dV$$
$$\oint_S \mathbf{B} \cdot d\mathbf{S} = 0$$
$$\oint_C \mathbf{E} \cdot d\mathbf{l} = -\int_S \frac{\partial \mathbf{B}}{\partial t} \cdot d\mathbf{S}$$
$$\oint_C \mathbf{H} \cdot d\mathbf{l} = \int_S (\mathbf{J} + \frac{\partial \mathbf{D}}{\partial t}) \cdot d\mathbf{S}$$

**微分形式**：
$$\nabla \cdot \mathbf{D} = \rho$$
$$\nabla \cdot \mathbf{B} = 0$$
$$\nabla \times \mathbf{E} = -\frac{\partial \mathbf{B}}{\partial t}$$
$$\nabla \times \mathbf{H} = \mathbf{J} + \frac{\partial \mathbf{D}}{\partial t}$$

### 4.4 边界条件

- $\mathbf{D}$ 法向分量跃变等于面电荷密度
- $\mathbf{B}$ 法向分量连续
- $\mathbf{E}$ 切向分量连续
- $\mathbf{H}$ 切向分量跃变等于面电流密度

### 4.5 坡印廷定理

**坡印廷矢量**：
$$\mathbf{S} = \mathbf{E} \times \mathbf{H}$$

**坡印廷定理**：
$$-\oint_S \mathbf{S} \cdot d\mathbf{S} = \int_V \mathbf{J} \cdot \mathbf{E} dV + \frac{\partial}{\partial t}\int_V (\frac{1}{2}\mathbf{E} \cdot \mathbf{D} + \frac{1}{2}\mathbf{H} \cdot \mathbf{B}) dV$$

### 4.6 电磁波方程

**无源区域**（$\rho=0, \mathbf{J}=0$）：
$$\nabla^2 \mathbf{E} - \mu\epsilon\frac{\partial^2 \mathbf{E}}{\partial t^2} = 0$$
$$\nabla^2 \mathbf{H} - \mu\epsilon\frac{\partial^2 \mathbf{H}}{\partial t^2} = 0$$

## 第五章 均匀平面波

### 5.1 无损耗介质中的均匀平面波

**波动方程的解**：
$$\mathbf{E}(z,t) = \mathbf{E}_0 \cos(\omega t - kz)$$

**波数**：
$$k = \omega\sqrt{\mu\epsilon}$$

**波速**：
$$v = \frac{\omega}{k} = \frac{1}{\sqrt{\mu\epsilon}}$$

**本征阻抗**：
$$\eta = \sqrt{\frac{\mu}{\epsilon}}$$

### 5.2 导电介质中的均匀平面波

**复波数**：
$$\gamma = \alpha + j\beta = j\omega\sqrt{\mu\epsilon(1-j\frac{\sigma}{\omega\epsilon})}$$

**良导体**（$\sigma \gg \omega\epsilon$）：
$$\alpha = \beta = \sqrt{\pi f\mu\sigma}$$

**趋肤深度**：
$$\delta = \frac{1}{\alpha} = \sqrt{\frac{2}{\omega\mu\sigma}}$$

### 5.3 极化

**线极化**：电场矢量端点轨迹为直线
**圆极化**：电场矢量端点轨迹为圆
**椭圆极化**：电场矢量端点轨迹为椭圆

### 5.4 平面波的反射与透射

**反射系数**：
$$\Gamma = \frac{\eta_2 - \eta_1}{\eta_2 + \eta_1}$$

**透射系数**：
$$\tau = \frac{2\eta_2}{\eta_2 + \eta_1}$$

**驻波比**：
$$S = \frac{1+|\Gamma|}{1-|\Gamma|}$$

### 5.5 全反射与全透射

**全反射条件**：
- 波从光密介质射向光疏介质
- 入射角大于临界角：$\theta_c = \arcsin\sqrt{\frac{\epsilon_2}{\epsilon_1}}$

**布儒斯特角**：
$$\theta_B = \arctan\sqrt{\frac{\epsilon_2}{\epsilon_1}}$$

## 第六章 导行电磁波

### 6.1 传输线方程

**电报方程**：
$$-\frac{\partial V}{\partial z} = L\frac{\partial I}{\partial t} + RI$$
$$-\frac{\partial I}{\partial z} = C\frac{\partial V}{\partial t} + GV$$

**正弦稳态**：
$$-\frac{dV}{dz} = (R+j\omega L)I = ZI$$
$$-\frac{dI}{dz} = (G+j\omega C)V = YV$$

### 6.2 传输线的解

**特性阻抗**：
$$Z_0 = \sqrt{\frac{R+j\omega L}{G+j\omega C}}$$

**传播常数**：
$$\gamma = \sqrt{(R+j\omega L)(G+j\omega C)} = \alpha + j\beta$$

**无损耗线**（R=0, G=0）：
$$Z_0 = \sqrt{\frac{L}{C}}$$
$$\gamma = j\omega\sqrt{LC}$$

### 6.3 负载与传输线的匹配

**反射系数**：
$$\Gamma(z) = \frac{Z_L - Z_0}{Z_L + Z_0}e^{-j2\beta z}$$

**输入阻抗**：
$$Z_{in}(z) = Z_0\frac{Z_L + jZ_0\tan\beta z}{Z_0 + jZ_L\tan\beta z}$$

**匹配条件**：$Z_L = Z_0$

### 6.4 阻抗圆图

**史密斯圆图**：将复反射系数平面映射到归一化阻抗平面。

**等电阻圆**：
$$(u - \frac{r}{r+1})^2 + v^2 = (\frac{1}{r+1})^2$$

**等电抗圆**：
$$(u - 1)^2 + (v - \frac{1}{x})^2 = (\frac{1}{x})^2$$

### 6.5 微波网络基础

**S参数**：
$$\begin{bmatrix} b_1 \\ b_2 \end{bmatrix} = \begin{bmatrix} S_{11} & S_{12} \\ S_{21} & S_{22} \end{bmatrix} \begin{bmatrix} a_1 \\ a_2 \end{bmatrix}$$

**互易网络**：$S_{12} = S_{21}$
**无耗网络**：$S^\dagger S = I$
**匹配网络**：$S_{11} = S_{22} = 0$

## 第七章 天线

### 7.1 天线的基本参数

**方向图**：天线辐射场的空间分布
**方向性系数**：
$$D = \frac{E_{max}^2}{E_{avg}^2} = \frac{4\pi U_{max}}{P_{rad}}$$

**增益**：
$$G = \eta D$$

**输入阻抗**：
$$Z_A = R_A + jX_A$$

**极化**：天线辐射电场的极化方式

### 7.2 基本电偶极子

**辐射场**：
$$E_\theta = j\frac{I_0 l \eta k}{4\pi r}\sin\theta e^{-jkr}$$
$$H_\varphi = \frac{E_\theta}{\eta}$$

**方向性系数**：$D = 1.5$

**辐射电阻**：
$$R_r = 80\pi^2(\frac{l}{\lambda})^2$$

### 7.3 半波偶极子

**方向图函数**：
$$F(\theta) = \frac{\cos(\frac{\pi}{2}\cos\theta)}{\sin\theta}$$

**方向性系数**：$D = 1.64$

**输入阻抗**：$Z_A = 73 + j42.5\Omega$

### 7.4 天线阵列

**阵列因子**：
$$AF = \sum_{n=1}^{N} I_n e^{j(nkd\cos\theta + \beta_n)}$$

**等间距等幅阵列**：
$$AF = \frac{\sin(N\psi/2)}{\sin(\psi/2)}, \quad \psi = kd\cos\theta + \beta$$

### 7.5 接收天线

**有效长度**：
$$l_e = \frac{V_{oc}}{E_{inc}}$$

**有效面积**：
$$A_e = \frac{\lambda^2}{4\pi}D$$

**弗里斯传输公式**：
$$\frac{P_r}{P_t} = G_t G_r (\frac{\lambda}{4\pi d})^2$$

## 第八章 电磁兼容与电磁防护

### 8.1 电磁干扰

**干扰源**：自然干扰、人为干扰
**耦合途径**：传导耦合、辐射耦合
**敏感设备**：接收机、测量仪器

### 8.2 电磁屏蔽

**屏蔽效能**：
$$SE = 20\log|\frac{E_1}{E_2}|$$

**反射损耗**：
$$R = 20\log|\frac{(Z_0+Z_s)^2}{4Z_0Z_s}|$$

**吸收损耗**：
$$A = 8.68\frac{t}{\delta}$$

### 8.3 电磁兼容设计

- 接地设计
- 滤波设计
- 屏蔽设计
- 布局布线设计
