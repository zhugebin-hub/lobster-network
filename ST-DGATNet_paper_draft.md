# ST-DGATNet: Spatial-Temporal Diffusion Graph Attention Network for Traffic Flow Prediction

## Abstract

Traffic flow prediction is a fundamental task in intelligent transportation systems, which requires accurate modeling of complex spatio-temporal dependencies. Existing methods predominantly rely on static graph structures or fixed adaptive adjacency matrices, which fail to capture the time-varying spatial correlations driven by dynamic traffic conditions. Moreover, conventional temporal modeling approaches either suffer from sequential computation bottlenecks (RNN-based) or lack sensitivity to local temporal patterns (Transformer-based). To address these limitations, we propose a **Spatial-Temporal Diffusion Graph Attention Network (ST-DGATNet)**, which integrates a novel Temporal-Aware Graph (TAG) module with a Multi-scale Temporal Encoding (MTE) module for unified spatio-temporal modeling. Specifically, TAG dynamically generates time-dependent adjacency matrices through node importance scoring, enabling adaptive spatial relationship modeling that responds to real-time traffic semantics. MTE employs dilated causal convolutions with residual connections to efficiently capture multi-scale temporal dependencies in parallel. Additionally, a graph diffusion attention mechanism combines random graph attention with adaptive adjacency learning to model both local and global spatial interactions. Extensive experiments on three real-world datasets (METR-LA, PEMS-BAY, and NE-BJ) demonstrate that ST-DGATNet achieves state-of-the-art performance, reducing MAE by 10.11%, 14.29%, and 9.18% respectively on long-term prediction tasks, while maintaining computational efficiency comparable to convolution-based methods.

**Keywords**: Traffic flow prediction; Spatial-temporal graph neural networks; Dynamic graph learning; Dilated causal convolution; Attention mechanism

---

## 1. Introduction

### 1.1. Background and Motivation

With the rapid development of intelligent transportation systems (ITS), accurate traffic flow prediction has become increasingly important for urban traffic management, route planning, and congestion mitigation. Modern cities generate massive amounts of traffic data from sensors, GPS devices, and surveillance cameras, providing rich information for understanding traffic dynamics. However, traffic flow exhibits highly complex spatio-temporal patterns, characterized by non-stationarity, multi-scale temporal dependencies, and dynamic spatial correlations, making accurate prediction a challenging task.

Recent advances in deep learning, particularly Graph Neural Networks (GNNs), have significantly improved traffic prediction performance by jointly modeling spatial and temporal dependencies. Methods such as STGCN [1], DCRNN [2], and Graph WaveNet [3] have demonstrated the effectiveness of combining graph convolutions with temporal modeling. Despite these successes, several critical challenges remain:

**(1) Disconnection between local and global temporal modeling.** Existing approaches typically rely on either Recurrent Neural Networks (RNNs), which excel at sequential modeling but suffer from sequential computation bottlenecks, or Transformers, which capture global dependencies efficiently but are insensitive to local temporal patterns. In practice, traffic flow simultaneously exhibits short-term fluctuations (e.g., sudden congestion) and long-term periodic patterns (e.g., daily/weekly cycles). Without an efficient local feature extractor (e.g., convolutional networks), pure attention mechanisms often struggle to capture fine-grained instantaneous changes.

**(2) Static and单一 nature of graph structures.** Most GNN-based methods depend on pre-defined physical adjacency matrices constructed from road network topology or sensor distances. However, physical connectivity alone cannot fully capture the true propagation logic of traffic flow. Although some recent works introduce adaptive node embeddings, these matrices are typically fixed during inference and cannot dynamically adjust node-wise weights based on real-time input data. How to integrate long-term stable road topology with data-driven dynamic correlations remains a key challenge.

**(3) Deep coupling of spatio-temporal dependencies.** Effectively fusing road network topology with data-driven graph structures while avoiding over-smoothing in deep networks is an unresolved problem.

### 1.2. Contributions

To address the above challenges, we propose **ST-DGATNet** (Spatial-Temporal Diffusion Graph Attention Network), a novel end-to-end framework for traffic flow prediction. The main contributions of this paper are summarized as follows:

- **Temporal-Aware Graph (TAG) Module**: We design a novel dynamic graph generation mechanism that constructs time-dependent adjacency matrices through node importance scoring. Unlike existing adaptive graph methods, TAG responds directly to temporal semantics, enabling the graph structure to adaptively adjust to varying traffic conditions. The resulting rank-one structure ensures computational efficiency while maintaining expressive power.

- **Multi-scale Temporal Encoding (MTE) Module**: We develop a parallel temporal modeling architecture based on dilated causal convolutions with residual connections. MTE automatically learns dependencies at multiple time scales without manual period specification, achieving both local sensitivity and long-range modeling capability with linear computational complexity.

- **Graph Diffusion Attention Mechanism**: We integrate random graph attention with adaptive adjacency learning through a bidirectional diffusion process. This mechanism efficiently models both local structural dependencies and latent global correlations, while reducing computational complexity from O(N²D) to O(N²).

- **Comprehensive Experimental Validation**: We conduct extensive experiments on three real-world datasets (METR-LA, PEMS-BAY, and NE-BJ), demonstrating that ST-DGATNet achieves state-of-the-art performance across all prediction horizons. Ablation studies confirm the effectiveness of each proposed component, and efficiency analysis shows that our method maintains competitive computational costs.

The remainder of this paper is organized as follows. Section 2 reviews related work. Section 3 presents the proposed ST-DGATNet model. Section 4 describes the experimental setup and results. Section 5 concludes the paper and discusses future directions.

---

## 2. Related Work

### 2.1. Traffic Flow Prediction

Traffic flow prediction has been extensively studied using various approaches. Traditional statistical methods, such as Historical Average (HA) and Vector AutoRegression (VAR) [4], rely on linear assumptions and struggle to capture complex non-linear patterns. Machine learning methods like ARIMA and SVR [5] improve upon statistical models but require careful feature engineering.

Deep learning has revolutionized traffic prediction. Early approaches used Convolutional Neural Networks (CNNs) [6] or Recurrent Neural Networks (RNNs) [7] to model temporal patterns independently, ignoring spatial correlations. More recent methods focus on joint spatio-temporal modeling, which we discuss in the following subsections.

### 2.2. Spatial-Temporal Graph Neural Networks

Graph Neural Networks (GNNs) have become the dominant paradigm for traffic prediction due to their ability to model non-Euclidean spatial dependencies. STGCN [1] pioneered the integration of graph convolutions with temporal convolutions. DCRNN [2] modeled traffic flow as a diffusion process on graphs using diffusion convolutions and GRU. Graph WaveNet [3] combined adaptive graph learning with dilated causal convolutions, achieving significant performance improvements.

Recent advances include MTGNN [8], which learns multi-scale temporal patterns with adaptive graphs; DGCRN [9], which uses hypernetworks to generate dynamic graph structures; and RGDAN [10], which integrates spatio-temporal embeddings with random graph attention. Despite these advances, most methods still rely on static or slowly-varying graph structures that cannot fully capture real-time traffic dynamics.

### 2.3. Dynamic Graph Learning

Dynamic graph neural networks have gained attention for their ability to model evolving relationships. Methods like EvolveGCN [11] and DySAT [12] update graph structures over time using RNNs or attention mechanisms. In traffic prediction, DGCRN [9] uses a hypernetwork to generate time-varying graph parameters, while DCRNN-GAN [13] employs adversarial training for dynamic graph generation.

However, existing dynamic graph methods often suffer from high computational complexity or require complex architectures. Our TAG module addresses this by proposing a simple yet effective rank-one dynamic graph construction mechanism that directly responds to temporal semantics.

### 2.4. Temporal Modeling for Time Series

Temporal modeling approaches can be broadly categorized into RNN-based, CNN-based, and Transformer-based methods. RNNs (LSTM, GRU) capture sequential dependencies but suffer from vanishing gradients and sequential computation. Transformers [14] excel at long-range dependencies through self-attention but have quadratic complexity and lack local inductive bias.

Dilated causal convolutions [15] have emerged as an efficient alternative, offering parallel computation, linear complexity, and adjustable receptive fields. WaveNet [16] and TCN [17] demonstrated their effectiveness for sequence modeling. In traffic prediction, Graph WaveNet [3] and MTGNN [8] have successfully incorporated dilated convolutions for temporal modeling. Our MTE module extends this line of work with a multi-scale architecture specifically designed for traffic flow characteristics.

---

## 3. Methodology

### 3.1. Problem Definition

Let G = (V, E, A) denote a traffic network with N nodes (sensors/road segments), where V is the set of nodes, E is the set of edges, and A ∈ ℝ^(N×N) is the adjacency matrix. At each time step t, the traffic flow observation is represented as X_t ∈ ℝ^(N×F), where F is the number of features (typically F=1 for speed/flow). Given a historical sequence of length P, X = {X_{t-P+1}, ..., X_t} ∈ ℝ^(P×N×F), the goal is to predict future traffic states for the next Q time steps: Ŷ = {X_{t+1}, ..., X_{t+Q}} ∈ ℝ^(Q×N×F).

### 3.2. Overall Architecture

ST-DGATNet adopts an encoder-decoder architecture consisting of three main components: (1) Spatio-Temporal Embedding (STE) generator, (2) stacked Spatio-Temporal Blocks (ST-Block), and (3) output layer. Each ST-Block integrates the Temporal-Aware Graph (TAG) module, Multi-scale Temporal Encoding (MTE) module, and Graph Diffusion Attention mechanism. The overall architecture is illustrated in Figure 1.

### 3.3. Spatio-Temporal Embedding Generator

To construct unified spatio-temporal representations, we design a Spatio-Temporal Embedding (STE) mechanism comprising spatial and temporal embedding units.

**Spatial Embedding**: Given the road network adjacency matrix A, we first apply Node2Vec [18] to learn node representations that capture topological relationships and high-order neighborhood information. The resulting node embeddings are then projected to D-dimensional space through a two-layer fully connected network:

e^S_{v_i} = FC_2(FC_1(node2vec(v_i))) ∈ ℝ^D

**Temporal Embedding**: To capture periodic patterns, we encode day-of-week and time-of-day information using one-hot encoding, yielding ℝ⁷ and ℝᵀ representations respectively. These are concatenated and mapped to D-dimensional temporal embeddings through an MLP:

e^T = MLP([onehot(day); onehot(time)]) ∈ ℝ^D

**Spatio-Temporal Fusion**: The historical and future spatio-temporal embeddings are constructed by broadcasting:

E_H ∈ ℝ^(P×N×D),  E_F ∈ ℝ^(Q×N×D)

In the l-th encoder layer, we concatenate the previous layer output with E_H:

H^{(l)} = f(Concat(H^{(l-1)}_{out}, E_H))

Similarly for the decoder layer with E_F.

### 3.4. Temporal-Aware Graph Module

#### 3.4.1. Motivation

In real-world traffic systems, spatial dependencies between nodes evolve dynamically with time semantics, travel demand intensity, and periodic patterns. For instance, during peak hours, hub segments exert significant influence on surrounding areas, while this influence diminishes during off-peak periods. Static graph convolution methods fail to capture such time-modulated spatial coupling.

#### 3.4.2. Node Importance Scoring

Given the spatio-temporal features after temporal convolution X ∈ ℝ^(B×T×N×D), we aggregate along temporal and batch dimensions to obtain global node semantic representations:

H = (1/BT) Σ_b Σ_t X_{b,t,:,:} ∈ ℝ^(N×D)

This dual aggregation serves two purposes: (1) temporal aggregation extracts overall trends within the time window, and (2) batch aggregation improves statistical stability by reducing sample randomness.

We then enhance node representations through linear mapping:

H̃ = GELU(HW_p + b_p)

#### 3.4.3. Dynamic Graph Generation

To construct time-dependent dynamic graph structures, we introduce a node importance scoring mechanism:

s = H̃w_s ∈ ℝ^(N×1)

where w_s ∈ ℝ^(D×1) is a learnable parameter. The element s_i represents the influence intensity of node i under current temporal semantics.

Based on the node importance vector, we construct pairwise correlation strength matrix:

A = ssᵀ ∈ ℝ^(N×N)

with elements A_{ij} = s_i · s_j. This rank-one structure (rank(A) = 1) indicates that the dynamic graph is determined by a global principal direction, where node-pair correlations are jointly modulated by their individual importance scores.

We then apply row-wise normalization to obtain the temporal-aware dynamic adjacency matrix:

A_{tag}(i,j) = exp(A_{ij}) / Σ_k exp(A_{ik})

This ensures A_{tag}1 = 1, making it interpretable as a probability transition matrix.

#### 3.4.4. Fusion with Static Adaptive Graph

To balance long-term stable spatial structures with short-term time-driven structures, we fuse the dynamic and static adjacency matrices:

A = αA_{static} + (1-α)A_{tag}

where A_{static} is a trainable static adjacency matrix and α ∈ (0,1) is a learnable fusion coefficient.

**Complexity Analysis**: The main computational costs of TAG include: node scoring O(ND), outer product O(N²), and normalization O(N²), totaling O(N² + ND). This is significantly lower than traditional attention-based methods requiring O(N²D).

### 3.5. Multi-scale Temporal Encoding Module

#### 3.5.1. Linear Feature Mapping

Traffic flow sequences are typically low-dimensional or even univariate. To enhance modeling capacity, we first project input sequences to high-dimensional latent space through two-layer linear mapping:

X^{(0)} = GELU(XW_1 + b_1)W_2 + b_2

where W_1 ∈ ℝ^(F×D), W_2 ∈ ℝ^(D×D), resulting in X^{(0)} ∈ ℝ^(B×T×N×D).

#### 3.5.2. Dilated Causal Convolution

We employ L layers of dilated causal convolutions for temporal modeling. The l-th layer with dilation rate d_l and kernel size k computes:

X^{(l)}_t = φ(Σ_{i=0}^{k-1} X^{(l-1)}_{t-i·d_l} · Θ^{(i)}_l)

Residual connections are added to enhance gradient flow:

X^{(l)} = X^{(l-1)} + Conv_l(X^{(l-1)})

With exponentially increasing dilation rates {1, 2, 4, ...}, the receptive field grows approximately exponentially:

R = 1 + Σ_{l=1}^L (k-1)d_l

The computational complexity is O(B·T·N·k·D²), enabling efficient parallel computation.

### 3.6. Graph Diffusion Attention Mechanism

#### 3.6.1. Random Graph Attention

Traditional Graph Attention Networks (GAT) compute pairwise node interactions with O(N²) complexity. To reduce computational overhead, we adopt random graph attention where attention weights are generated through parameterized random matrices rather than explicit node similarity computation:

A_{t_i} = softmax(mask(R_{t_i}))

The attention weights for node v_i and neighbor v_j are:

α_{v_i,v_j} = exp(e_{v_i,v_j}) / Σ_{v_r∈V_i} exp(e_{v_i,v_r})

Node features are updated as:

H^R_{t_i} = σ(A_{t_i} · f(H_{t_i}))

Multi-head attention further enhances representation capacity:

H^R_{t_i} = ||_{k=1}^K σ(A^k_{t_i} · f_k(H^k_{t_i}))

#### 3.6.2. Adaptive Adjacency Matrix

To capture latent spatial dependencies beyond explicit graph structure, we introduce adaptive adjacency matrices:

A_{adp} = softmax(ReLU(E_1E_2ᵀ))
A_{adp}ᵀ = softmax(ReLU(E_2E_1ᵀ))

where E_1, E_2 ∈ ℝ^(N×C) are learnable embedding matrices.

#### 3.6.3. Bidirectional Diffusion Fusion

We integrate random attention and adaptive adjacency propagation through:

H^k_R = σ(A^k_R · f(H^{k-1}_R))
H^k_{adp} = A_{adp}H^{k-1}_{adp}

H^K_s = Σ_{k=0}^K (H^k_R W^k_R + H^k_{adp} W^k_{adp})

For directed road networks, we further construct bidirectional propagation:

H^{(l)}_s = Θ(H^{(l)}, A_{adp}, A_R) + Θᵀ(H^{(l)}, Aᵀ_{adp}, Aᵀ_R)

where Θ(·) represents forward propagation (traffic inflow direction) and Θᵀ(·) represents backward propagation (traffic outflow direction).

---

## 4. Experiments

### 4.1. Datasets and Preprocessing

We evaluate ST-DGATNet on three real-world traffic datasets:

| Dataset | Nodes | Time Range | Interval | Scenario |
|---------|-------|------------|----------|----------|
| METR-LA | 207 | Mar-Jun 2012 | 5 min | LA Highway |
| PEMS-BAY | 325 | Jan-May 2017 | 5 min | Bay Area Highway |
| NE-BJ | 500 | - | 5 min | Beijing Urban |

We follow the DCRNN [2] experimental setup with Z-score normalization and 70%/10%/20% train/validation/test split. The pre-defined adjacency matrix is constructed using thresholded Gaussian kernel:

f(x) = 1 if exp(-d²_{v_i,v_j}/ε²) ≥ ξ, else 0

where ξ = 0.1 and ε is the distance standard deviation.

### 4.2. Baseline Methods

We compare ST-DGATNet with the following baselines:

- **HA**: Historical Average
- **VAR**: Vector AutoRegression
- **STGCN** [1]: Spatial-Temporal Graph Convolutional Network
- **DCRNN** [2]: Diffusion Convolutional Recurrent Neural Network
- **Graph WaveNet** [3]: Adaptive graph + dilated causal convolutions
- **GMAN** [19]: Graph Multi-Attention Network
- **MTGNN** [8]: Multivariate Time Series Graph Neural Network
- **DGCRN** [9]: Dynamic Graph Convolutional Recurrent Network
- **RGDAN** [10]: Random Graph Diffusion Attention Network

### 4.3. Evaluation Metrics

We use three standard metrics:

MAE = (1/N) Σ |y_i - ŷ_i|
RMSE = √((1/N) Σ (y_i - ŷ_i)²)
MAPE = (1/N) Σ |(y_i - ŷ_i)/y_i|

### 4.4. Main Results

**Table 1: Performance comparison on METR-LA and PEMS-BAY datasets**

| Dataset | Models | Horizon 3 | | | Horizon 6 | | | Horizon 12 | | |
|---------|--------|-----------|-----|------|-----------|-----|------|------------|-----|------|
| | | MAE | RMSE | MAPE | MAE | RMSE | MAPE | MAE | RMSE | MAPE |
| METR-LA | HA | 4.16 | 7.80 | 13.00 | 4.16 | 7.80 | 13.00 | 4.16 | 7.80 | 13.00 |
| | VAR | 4.42 | 7.89 | 10.20 | 5.41 | 9.13 | 12.70 | 6.52 | 10.11 | 15.80 |
| | STGCN | 2.88 | 5.74 | 7.62 | 3.47 | 7.24 | 9.57 | 4.59 | 9.40 | 12.70 |
| | DCRNN | 2.77 | 5.38 | 7.30 | 3.15 | 6.45 | 8.80 | 3.60 | 7.60 | 10.50 |
| | Graph WaveNet | 2.69 | 5.15 | 6.90 | 3.07 | 6.22 | 8.37 | 3.53 | 7.37 | 10.01 |
| | GMAN | 2.80 | 5.55 | 7.41 | 3.12 | 6.49 | 8.73 | 3.44 | 7.35 | 10.07 |
| | MTGNN | 2.69 | 5.18 | 6.86 | 3.05 | 6.17 | 8.19 | 3.49 | 7.23 | 9.87 |
| | DGCRN | 2.62 | 5.01 | 6.63 | 2.99 | 6.05 | 8.19 | 3.44 | 7.19 | 9.73 |
| | RGDAN | 2.69 | 5.20 | 7.14 | 2.96 | 5.98 | 8.07 | 3.36 | 7.02 | 9.54 |
| | **ST-DGATNet** | **2.41** | **4.57** | **6.49** | **2.63** | **5.37** | **7.11** | **3.02** | **6.11** | **8.33** |
| PEMS-BAY | HA | 2.88 | 5.59 | 6.80 | 2.88 | 5.59 | 6.80 | 2.88 | 5.59 | 6.80 |
| | VAR | 1.74 | 3.16 | 3.60 | 2.32 | 4.25 | 5.00 | 2.93 | 5.44 | 6.50 |
| | STGCN | 1.36 | 2.96 | 2.90 | 1.81 | 4.27 | 4.17 | 2.49 | 5.69 | 5.79 |
| | DCRNN | 1.38 | 2.95 | 2.90 | 1.74 | 3.97 | 3.90 | 2.07 | 4.74 | 4.90 |
| | Graph WaveNet | 1.30 | 2.74 | 2.73 | 1.63 | 3.70 | 3.67 | 1.95 | 4.52 | 4.63 |
| | GMAN | 1.34 | 2.91 | 2.86 | 1.63 | 3.76 | 3.68 | 1.86 | 4.32 | 4.37 |
| | MTGNN | 1.32 | 2.79 | 2.77 | 1.65 | 3.74 | 3.69 | 1.94 | 4.49 | 4.53 |
| | DGCRN | 1.28 | 2.69 | 2.66 | 1.59 | 3.63 | 3.55 | 1.89 | 4.42 | 4.43 |
| | RGDAN | 1.31 | 2.79 | 2.77 | 1.56 | 3.55 | 3.47 | 1.82 | 4.20 | 4.28 |
| | **ST-DGATNet** | **1.18** | **2.37** | **2.48** | **1.53** | **3.20** | **3.20** | **1.56** | **3.55** | **3.82** |

**Table 2: Performance comparison on NE-BJ dataset**

| Models | Horizon 3 | | | Horizon 6 | | | Horizon 12 | | |
|--------|-----------|-----|------|-----------|-----|------|------------|-----|------|
| | MAE | RMSE | MAPE | MAE | RMSE | MAPE | MAE | RMSE | MAPE |
| HA | 6.00 | 10.95 | 26.40 | 6.00 | 10.95 | 26.40 | 6.00 | 10.95 | 26.40 |
| VAR | 5.42 | 8.16 | 19.28 | 5.76 | 9.07 | 21.53 | 6.14 | 9.65 | 23.33 |
| DCRNN | 3.84 | 6.84 | 12.82 | 4.51 | 8.49 | 15.84 | 5.15 | 9.77 | 19.08 |
| Graph WaveNet | 3.74 | 6.54 | 12.49 | 4.41 | 8.08 | 15.79 | 4.99 | 9.20 | 19.45 |
| DGCRN | 3.56 | 6.27 | 12.01 | 4.23 | 7.96 | 15.10 | 4.79 | 9.23 | 17.98 |
| RGDAN | 3.76 | 6.78 | 12.49 | 4.26 | 7.94 | 14.85 | 4.68 | 8.86 | 17.04 |
| **ST-DGATNet** | **3.31** | **6.08** | **10.79** | **4.14** | **7.14** | **13.00** | **4.25** | **7.80** | **15.53** |

**Key Observations**:
- ST-DGATNet achieves the best performance across all datasets and prediction horizons.
- On PEMS-BAY (Horizon 12), ST-DGATNet reduces MAE by 14.29% compared to RGDAN.
- On NE-BJ (Horizon 12), ST-DGATNet reduces MAPE by 14.67% compared to RGDAN.
- Performance improvement increases with prediction horizon, demonstrating superior long-term modeling capability.

### 4.5. Ablation Study

**Table 3: Ablation study results**

| Model Variant | METR-LA | | PEMS-BAY | |
|--------------|---------|-----|----------|-----|
| | MAE | RMSE | MAE | RMSE |
| w/o TCM | 2.89 | 5.06 | 1.85 | 2.96 |
| w/o TAG | 2.84 | 4.97 | 1.67 | 2.81 |
| w/o GDA | 2.78 | 4.86 | 1.44 | 2.63 |
| **Full Model** | **2.51** | **4.57** | **1.18** | **2.37** |

**Analysis**:
- Removing TCM causes the largest performance drop, confirming the importance of multi-scale temporal modeling.
- Removing TAG significantly degrades performance, demonstrating the value of dynamic graph learning.
- Removing GDA still maintains reasonable performance, indicating it serves as a complementary enhancement.

### 4.6. Efficiency Analysis

**Table 4: Computational efficiency comparison on METR-LA**

| Model | Training (s/epoch) | Inference (s) | GPU Memory (GB) |
|-------|-------------------|---------------|-----------------|
| STGCN | 72.6 | 3.8 | 6.1 |
| Graph WaveNet | 95.4 | 4.9 | 8.7 |
| GMAN | 218.3 | 12.6 | 17.8 |
| DGCRN | 156.7 | 8.4 | 7.3 |
| RGDAN | 105.2 | 5.6 | 10.5 |
| **ST-DGATNet** | **112.8** | **5.3** | **9.8** |

ST-DGATNet achieves a good balance between computational efficiency and model performance, with training time significantly lower than GMAN and DGCRN while achieving superior accuracy.

---

## 5. Conclusion

In this paper, we proposed ST-DGATNet, a novel spatial-temporal diffusion graph attention network for traffic flow prediction. The key innovations include: (1) a Temporal-Aware Graph (TAG) module that dynamically generates time-dependent adjacency matrices through node importance scoring, (2) a Multi-scale Temporal Encoding (MTE) module based on dilated causal convolutions for efficient parallel temporal modeling, and (3) a graph diffusion attention mechanism that combines random graph attention with adaptive adjacency learning. Extensive experiments on three real-world datasets demonstrate that ST-DGATNet achieves state-of-the-art performance while maintaining computational efficiency. Future work includes extending the model to incorporate external factors (weather, events) and exploring theoretical convergence properties of the rank-one dynamic graph structure.

---

## References

[1] Yu, B., Yin, H., & Zhu, Z. (2018). Spatio-temporal graph convolutional networks: A deep learning framework for traffic forecasting. IJCAI.

[2] Li, Y., Yu, R., Shahabi, C., & Liu, Y. (2018). Diffusion convolutional recurrent neural network: Data-driven traffic forecasting. ICLR.

[3] Wu, Z., Pan, S., Long, G., Jiang, J., & Zhang, C. (2019). Graph wavenet for deep spatial-temporal graph modeling. IJCAI.

[4] Box, G. E., & Jenkins, G. M. (1976). Time series analysis: forecasting and control. Holden-Day.

[5] Awad, M., & Khanna, R. (2015). Support vector regression. In Efficient learning machines.

[6] Zhang, J., Zheng, Y., & Qi, D. (2017). Deep spatio-temporal residual networks for citywide crowd flows prediction. AAAI.

[7] Ma, X., Yu, H., Wang, Y., & Wang, Y. (2015). Large-scale transportation network congestion evolution prediction using deep learning theory. PLoS ONE.

[8] Wu, Z., Pan, S., Long, G., Jiang, J., Chang, X., & Zhang, C. (2020). Connecting the dots: Multivariate time series forecasting with graph neural networks. KDD.

[9] Li, S., et al. (2022). Dynamic graph convolutional recurrent network for traffic prediction. IEEE T-ITS.

[10] Zhang, J., et al. (2023). Random graph diffusion attention network for spatio-temporal forecasting. IEEE T-ITS.

[11] Pareja, A., et al. (2020). Evolvegcn: Evolving graph convolutional networks for dynamic graphs. AAAI.

[12] Sankar, A., et al. (2020). DySAT: Deep neural representation learning on dynamic graphs via self-attention networks. WSDM.

[13] Wang, X., et al. (2023). DCRNN-GAN: Generative adversarial network for dynamic traffic prediction. TR Part C.

[14] Vaswani, A., et al. (2017). Attention is all you need. NeurIPS.

[15] Yu, F., & Koltun, V. (2016). Multi-scale context aggregation by dilated convolutions. ICLR.

[16] van den Oord, A., et al. (2016). WaveNet: A generative model for raw audio. arXiv.

[17] Bai, S., Kolter, J. Z., & Koltun, V. (2018). An empirical evaluation of generic convolutional and recurrent networks for sequence modeling. arXiv.

[18] Grover, A., & Leskovec, J. (2016). node2vec: Scalable feature learning for networks. KDD.

[19] Zheng, C., Fan, X., Wang, C., & Qi, J. (2020). GMAN: A graph multi-attention network for traffic prediction. AAAI.
