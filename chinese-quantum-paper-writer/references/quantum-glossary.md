# 量子计算术语及符号

下表为建议用法，目标期刊或权威标准另有规定时以其为准。首次出现给出中文、英文和缩写，后续统一；不同概念不强行合并。引用中的原始题名保留原貌。

| 中文 | 英文/缩写 | 注意 |
|---|---|---|
| 量子比特 | qubit | 区别经典比特 |
| 量子态 | quantum state | 纯态、混合态分开 |
| 量子叠加 | superposition | 不等同于纠缠 |
| 量子纠缠 | entanglement | 非经典关联，不能据此宣称超光速通信 |
| 量子门 | quantum gate | 幺正门与测量区别 |
| 量子线路（量子电路） | quantum circuit | 正文择一统一；引文题名不改 |
| 量子线路深度 | circuit depth | 区别门数和执行时长 |
| 含噪中等规模量子计算 | noisy intermediate-scale quantum, NISQ | 中文译法有差异，明确使用口径 |
| 量子计算优势 | quantum advantage | 明确任务、基线及资源；不泛化 |
| 量子纠错 | quantum error correction, QEC | 区别错误缓解 |
| 量子错误缓解 | quantum error mitigation, QEM | 不等同于容错计算 |
| 容错量子计算 | fault-tolerant quantum computing | 需说明编码与阈值条件 |
| 物理/逻辑量子比特 | physical/logical qubit | 资源统计不可混用 |
| 保真度 | fidelity | 指定定义、对象、估计方法 |
| 量子测量 | quantum measurement | shots 译为采样次数/测量次数并说明 |
| 量子线路映射 | quantum circuit mapping | 区别布局、路由、调度 |
| 交换门 | SWAP gate | 区别逻辑置换与实际门分解 |
| 受控非门 | controlled-NOT, CNOT | 与 CZ 等原生门区别 |
| 量子傅里叶变换 | quantum Fourier transform, QFT | 不等同经典 FFT |
| 量子相位估计 | quantum phase estimation, QPE | 明确精度及假设 |
| 变分量子算法 | variational quantum algorithm, VQA | 说明经典优化器和参数化线路 |
| 变分量子本征求解器 | variational quantum eigensolver, VQE | 指定哈密顿量 |
| 量子近似优化算法 | quantum approximate optimization algorithm, QAOA | 指定层数、目标和基线 |
| 二次无约束二元优化 | quadratic unconstrained binary optimization, QUBO | 不是量子算法本身 |
| 量子退火 | quantum annealing | 区别门模型与经典模拟退火 |
| 量子机器学习 | quantum machine learning, QML | 区分量子数据与经典数据编码 |
| 参数化量子线路 | parameterized quantum circuit, PQC | 说明参数和线路结构 |
| 量子密钥分发 | quantum key distribution, QKD | 区别后量子密码 |
| 后量子密码 | post-quantum cryptography, PQC | 与参数化线路缩写冲突，按上下文避免歧义 |
| 量子启发式算法 | quantum-inspired algorithm | 可能完全在经典设备上运行，不能宣称量子硬件优势 |
| 量子游走 | quantum walk | 明确离散/连续时间模型 |
| 量子模拟 | quantum simulation | 区分量子系统模拟与经典量子线路模拟 |

## 建议符号

- `|ψ⟩`、`⟨ψ|`、`ρ` 表示纯态、对偶态、密度算符；`U` 表示幺正算符；`H` 表示哈密顿量或 Hadamard 门时必须消歧。
- `n` 量子比特数，`d` 线路深度，`G` 门数，`θ` 可训练参数，`ε` 误差参数；使用前定义，全文一致，勿与图的顶点数混用。
- 明确张量积 `⊗`、共轭转置 `†`、迹 `Tr` 的含义。单位、概率范围、对数底、渐近复杂度的自变量均要说明。
- 性能比较标注设备、噪声、线路规模、测量次数和资源计算口径。经典仿真加速不自动等于量子优势；理想态结果不等于真实硬件结果。
