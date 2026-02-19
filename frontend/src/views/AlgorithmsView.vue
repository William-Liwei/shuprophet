<template>
  <div>
    <h1 class="page-title">{{ $route.meta.title }}</h1>

    <div class="algorithms-view">
      <!-- 算法选择标签页 -->
      <el-tabs v-model="activeAlgorithm" type="border-card" class="algorithm-tabs">
        
        <!-- 遍历算法数据，为每个算法创建一个标签页 -->
        <el-tab-pane 
          v-for="algo in algorithms" 
          :key="algo.name" 
          :label="algo.name" 
          :name="algo.name"
        >
          <!-- 单个算法的介绍内容 -->
          <div class="algorithm-content">
            <el-row :gutter="30">
              
              <!-- 左侧：文字描述区域 -->
              <el-col :xs="24" :md="14" style="margin-bottom: 2rem;">
                <h3><el-icon><Tickets /></el-icon> 核心思想</h3>
                <p>{{ algo.coreIdea }}</p>

                <h3><el-icon><Operation /></el-icon> 关键创新</h3>
                <ul>
                  <li v-for="innovation in algo.innovations" :key="innovation">{{ innovation }}</li>
                </ul>

                <h3><el-icon><Link /></el-icon> 成果链接</h3>
                <div class="links">
                    <el-button 
                      v-if="algo.paperLink" 
                      type="primary" 
                      plain 
                      @click="openLink(algo.paperLink)"
                    >
                      <el-icon><Document /></el-icon> 查看论文
                    </el-button>
                    <el-button 
                      v-if="algo.githubLink" 
                      type="success" 
                      plain 
                      @click="openLink(algo.githubLink)"
                    >
                      <el-icon><Share /></el-icon> GitHub 仓库
                    </el-button>
                </div>

                <div class="citation-section">
                  <h3>学术引用 (BibTeX)</h3>
                  <p>如果您的研究工作使用了本模型，请考虑引用以下文献：</p>
                  <el-button @click="showBibtex(algo)">
                    <el-icon><DocumentCopy /></el-icon> 查看 BibTeX
                  </el-button>
                </div>

              </el-col>

              

              <!-- 右侧：图片/架构图区域 -->
              <el-col :xs="24" :md="10">
                 <h3><el-icon><PictureRounded /></el-icon> 模型架构</h3>
                 <el-image 
                    :src="algo.imageUrl" 
                    fit="contain" 
                    class="architecture-image"
                 >
                    <template #error>
                      <div class="image-slot">
                        <el-icon><Picture /></el-icon>
                        <p>架构图加载失败</p>
                      </div>
                    </template>
                 </el-image>
              </el-col>

            </el-row>
          </div>
        </el-tab-pane>

        <!-- BibTeX 显示弹窗 -->
        <el-dialog
          v-model="dialogVisible"
          :title="`'${currentAlgoName}' 的 BibTeX 引用`"
          width="80%"
          max-width="600px"
          append-to-body
        >
          <div class="bibtex-container">
            <pre><code>{{ currentBibtex }}</code></pre>
          </div>
          <template #footer>
            <el-button type="primary" @click="dialogVisible = false">关闭</el-button>
          </template>
        </el-dialog>

      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';

// 当前激活的标签页名称
const activeAlgorithm = ref('ScatterFusion');

// BibTeX 弹窗相关状态
const dialogVisible = ref(false);
const currentBibtex = ref('');
const currentAlgoName = ref('');

// --- 更新后的算法数据 ---
const algorithms = ref([
  {
    name: 'ScatterFusion',
    coreIdea: '一个创新的层级散射变换框架，通过协同整合散射变换与层级注意力机制，实现鲁棒的时间序列预测。该框架能够提取多尺度不变特征，同时捕捉局部和全局模式，有效应对复杂时间依赖关系的挑战。',
    innovations: [
      '层级散射变换模块(HSTM)：提取具有数学可证明性质的多尺度不变特征。',
      '尺度自适应特征增强(SAFE)：动态调整不同尺度特征的重要性。',
      '多分辨率时序注意力(MRTA)：在不同时间跨度上建模依赖关系。',
      '趋势-季节-残差(TSR)分解引导的结构感知损失函数，增强结构化预测精度。'
    ],
    paperLink: null,
    githubLink: null,
    imageUrl: 'https://www.weili.space/about/images/scatterfusion.png',
    bibtex: `@inproceedings{li2026scatterfusion,
  title={ScatterFusion: A Hierarchical Scattering Transform Framework for Enhanced Time Series Forecasting},
  author={Li, Wei},
  booktitle={IEEE International Conference on Acoustics, Speech, and Signal Processing},
  year={2026}
}`
  },
  {
    name: 'AWGFormer',
    coreIdea: '一个新颖的架构，将自适应小波分解与跨尺度注意力机制相结合，用于增强多变量时间序列预测。该方法能够在保持计算效率的同时，捕捉多个时间尺度上的模式。',
    innovations: [
      '自适应小波分解模块(AWDM)：基于信号特征动态选择最优小波基和分解层级。',
      '跨尺度特征融合(CSFF)：通过可学习的耦合矩阵捕捉不同频带之间的交互。',
      '频率感知多头注意力(FAMA)：根据频率选择性对注意力头进行加权。',
      '层级预测网络(HPN)：在多个分辨率上生成预测后进行重构。'
    ],
    paperLink: null,
    githubLink: null,
    imageUrl: 'https://www.weili.space/about/images/awgformer.png',
    bibtex: `@inproceedings{li2026awgformer,
  title={AWGFormer: Adaptive Wavelet-Guided Transformer for Multi-resolution Time Series Forecasting},
  author={Li, Wei},
  booktitle={IEEE International Conference on Acoustics, Speech, and Signal Processing},
  year={2026}
}`
  },
  {
    name: 'TimeFlowDiffuser',
    coreIdea: '引入一种新颖的、专为时序预测设计的层级式扩散模型框架。它通过自适应上下文采样和多尺度时间分辨率处理，有效解决了传统模型在多步长预测中的局限性，尤其在长周期预测任务上表现卓越。',
    innovations: [
      '层级时间分辨率(HTR)：将时间序列在不同尺度上进行下采样，并行处理，有效捕捉短期波动和长期趋势。',
      '自适应上下文采样(ACS)：动态识别并聚焦于历史数据中最相关的部分，提升预测效率和准确性。',
      '频率感知条件(FAC)：将时序分解为趋势、季节性和残差项，对不同频率的成分进行专门处理。',
      '多步长生成(MHG)：设计了统一的模型框架，能一次性高效生成不同长度的预测，而非多次迭代。'
    ],
    paperLink: null, // 请替换成您的真实论文链接
    githubLink: null, // 请替换成您的真实仓库链接
    imageUrl: 'https://www.weili.space/about/images/timeflowdiffuser.png',
    bibtex: `@inproceedings{li2025timeflowdiffuser,
  title={TimeFlowDiffuser: A Hierarchical Diffusion Framework with Adaptive Context Sampling for Multi-Horizon Time Series Forecasting},
  author={Li, Wei},
  booktitle={International Conference on Artificial Neural Networks (ICANN 2025)},
  year={2025},
  note = {Accepted}
}`
  },
  {
    name: 'EnergyPatchTST',
    coreIdea: '作为Patch Time Series Transformer的扩展，专门为能源预测领域设计。它不仅通过多尺度特征提取来捕捉不同时间分辨率的模式，还创新性地引入了概率预测框架，以应对能源系统对可靠性和不确定性估计的严格要求。',
    innovations: [
      '多尺度特征提取：通过分层架构处理不同时间分辨率的序列，同时捕捉短期波动和长期趋势。',
      '不确定性估计：采用蒙特卡洛丢弃(Monte Carlo Dropout)机制提供概率性预测，并生成校准的预测区间。',
      '未来变量集成：设计了专门的路径来整合已知的未来信息（如天气预报），提升预测精度。',
      '预训练与微调：利用迁移学习范式，在通用数据集上预训练，然后在特定的能源数据集上微调，解决了能源数据有限的问题。'
    ],
    paperLink: 'https://link.springer.com/chapter/10.1007/978-981-96-9815-8_27',
    githubLink: 'https://github.com/William-Liwei/EnergyPatchTST',
    imageUrl: 'https://www.weili.space/about/images/energypatchtst.png',
    bibtex: `@inproceedings{li2025energypatchtst,
  title={EnergyPatchTST: Multi-scale Time Series Transformers with Uncertainty Estimation for Energy Forecasting},
  author={Li, Wei and Wang, Zixin and Sun, Qizheng and Gao, Qixiang and Yang, Fenglei},
  booktitle={International Conference on Intelligent Computing},
  pages={319--330},
  year={2025},
  organization={Springer}
}`
  },
  {
    name: 'LWSpace',
    coreIdea: '一个创新的多尺度状态空间框架，它将小波分解与选择性状态空间模型（S4）相结合。该模型旨在解决时间序列中的多尺度时间动态特性，特别是在长周期预测上，通过在不同频带上进行专门处理，实现了卓越的性能和鲁棒性。',
    innovations: [
      '小波分解模块(WDM)：利用离散小波变换将时间序列分解为多个频带，实现多尺度分析。',
      '尺度特定的选择性状态空间(S4)：为每个频带应用专门的S4模型，以不同的动态特性处理各尺度信息。',
      '跨尺度注意力集成(CSAI)：通过注意力机制实现不同尺度间的信息交换，捕捉跨频带的复杂依赖。',
      '自适应视野预测(AHP)：构建了一个能高效生成多个预测视野的框架，提升了模型的实用性。'
    ],
    paperLink: 'https://link.springer.com/chapter/10.1007/978-981-96-9815-8_25',
    githubLink: null,
    imageUrl: 'https://www.weili.space/about/images/lwspace.png',
    bibtex: `@inproceedings{li2025lwspace,
  title={LWSpace: A Multi-scale State Space Framework for Enhanced Time Series Forecasting},
  author={Li, Wei},
  booktitle={International Conference on Intelligent Computing},
  pages={295--306},
  year={2025},
  organization={Springer}
}`
  },
  {
    name: 'SWIFT',
    coreIdea: '一个协同结合了选择性状态空间模型（Mamba）和多尺度扩张卷积的神经网络架构。该模型通过双路径设计，旨在同时捕捉时间序列中的长程依赖和多尺度模式，显著增强了预测性能。',
    innovations: [
      '选择性时序状态空间(STSS)模块：通过时序特定的门控机制扩展了Mamba模型，使其更适应时序数据。',
      '多尺度扩张卷积网络(MSDCN)：利用并行的、拥有自适应感受野的扩张卷积来提取多尺度特征。',
      '特征交互桥(FIB)：设计了一个桥接模块，促进状态空间路径和卷积路径之间的双向信息交换。',
      '动态尺度选择(DSS)：基于预测视野，自适应地对不同时间尺度的特征进行加权，实现动态聚焦。'
    ],
    paperLink: null, // 请替换成您的真实论文链接
    githubLink: null,
    imageUrl: 'https://www.weili.space/about/images/swift.png', // 假设图片路径，请确认
    bibtex: `@inproceedings{li2025swift,
  title={SWIFT: State-space Wavelet Integrated Forecasting Technology for Enhanced Time Series Prediction},
  author={Li, Wei},
  booktitle={International Conference on Artificial Neural Networks (ICANN 2025)},
  year={2025},
  note = {Accepted}
}`
  }
]);

// --- 方法 ---
const openLink = (url) => {
  window.open(url, '_blank');
};

const showBibtex = (algo) => {
  currentAlgoName.value = algo.name;
  currentBibtex.value = algo.bibtex;
  dialogVisible.value = true;
};
</script>

<style scoped>
.algorithm-tabs {
  border: none;
  background-color: transparent;
}

/* 深度选择器，修改Element Plus组件的内部样式 */
:deep(.el-tabs__header) {
  background-color: #1a1410;
  border-bottom: 1px solid #3d2817;
}
:deep(.el-tabs__nav-wrap) {
  border-radius: 8px 8px 0 0;
}
:deep(.el-tabs__item) {
  color: #c9a87c;
}
:deep(.el-tabs__item.is-active) {
  background-color: #3d2817 !important;
  color: #FFD700 !important;
}
:deep(.el-tabs__content) {
  padding: 24px;
  background-color: #1a1410;
}

.algorithm-content h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #FFD700;
  font-size: 1.2rem;
  margin-top: 0;
  margin-bottom: 1rem;
}

.algorithm-content p, .algorithm-content li {
  line-height: 1.8;
  color: #c9a87c;
  font-size: 1rem;
}

.algorithm-content ul {
  padding-left: 20px;
}

.links {
  margin-top: 0.5rem;
  display: flex;
  gap: 12px;
}

.architecture-image {
  width: 100%;
  height: 300px;
  background-color: #1e293b;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.image-slot {
  text-align: center;
  color: #94a3b8;
}
.image-slot .el-icon {
  font-size: 40px;
}

.bibtex-container {
  background-color: #1e293b; /* 深色背景 */
  border-radius: 6px;
  padding: 1rem;
  overflow-x: auto; /* 内容过长时允许横向滚动 */
}

pre {
  margin: 0;
  white-space: pre-wrap;   /* 自动换行 */
  word-wrap: break-word; /* 单词过长时打断 */
}

code {
  color: #c7d2fe; /* 亮色文字 */
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.9rem;
}

.citation-section {
  margin-top: 2rem; /* 增加上外边距，2rem 大约等于 32px，可以根据喜好调整 */
  padding-top: 1.5rem; /* 增加上内边距，让内容区更舒适 */
  border-top: 1px solid #1e293b; /* 在上方添加一条细微的分割线，增强区隔感 */
}
</style>