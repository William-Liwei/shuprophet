<template>
  <div class="about-page">
    
    <!-- 1. 顶部 Hero 区域 -->
    <div class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">鼠先知 (SHU Prophet)</h1>
        <p class="hero-subtitle">一个集前沿算法、交互验证与实时应用于一体的时序智能决策平台</p>
        <el-button type="primary" size="large" round @click="goToExplorer">
          <el-icon><DataLine /></el-icon>
          立即开始探索
        </el-button>
      </div>
    </div>

    <!-- 2. 设计理念 -->
    <h2 class="section-title"><span>我们的理念</span></h2>
    <el-row :gutter="24">
      <el-col :lg="8" :md="12" :sm="24" :xs="24" v-for="p in philosophy" :key="p.title">
        <div class="philosophy-card">
          <div class="philosophy-icon"><el-icon><component :is="p.icon" /></el-icon></div>
          <h3>{{ p.title }}</h3>
          <p>{{ p.description }}</p>
        </div>
      </el-col>
    </el-row>

    <!-- 3. 自研模型矩阵 -->
    <h2 class="section-title"><span>自研模型矩阵：驱动平台的核心引擎</span></h2>
    <div class="intro-paragraph">
      <p>平台的核心由我们独立设计和实现的四大SOTA（State-of-the-Art）模型驱动。它们并非孤立的算法，而是一个针对时间序列预测中不同挑战（如多尺度、不确定性、长程依赖）而构建的协同矩阵，共同构成了“鼠先知”强大的预测能力。</p>
    </div>
    <div class="models-grid">
      <div class="model-intro-card" v-for="model in models" :key="model.name">
        <div class="model-card-header">
          <el-image :src="model.imageUrl" fit="cover" class="model-image" />
          <div class="model-name-overlay">
            <h3>{{ model.name }}</h3>
            <span>{{ model.tagline }}</span>
          </div>
        </div>
        <div class="model-card-body">
          <p>{{ model.description }}</p>
        </div>
      </div>
    </div>
    <div class="action-center">
      <el-button plain size="large" @click="goToAlgorithms">
        深入了解所有算法细节
        <el-icon class="el-icon--right"><Right /></el-icon>
      </el-button>
    </div>

    <!-- 4. 平台功能导览 -->
    <h2 class="section-title"><span>平台功能导览</span></h2>
    <div class="getting-started-container">
      <div class="getting-started-step" v-for="(step, index) in steps" :key="step.title">
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-content">
          <h4>{{ step.title }}</h4>
          <p>{{ step.description }}</p>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { Aim, View, MagicStick, DataLine, Right, Collection, Cpu, Opportunity, Rank } from '@element-plus/icons-vue';

const router = useRouter();

const goToExplorer = () => router.push('/');
const goToAlgorithms = () => router.push('/algorithms');

// 设计理念数据
const philosophy = ref([
  { icon: Aim, title: '从理论到实践', description: '我们致力于弥合学术研究与工业应用之间的鸿沟。平台不仅是SOTA算法的试验场，更是能将前沿理论转化为可靠、可用预测服务的桥梁。' },
  { icon: View, title: '可视化驱动洞察', description: '“一图胜千言”。我们坚信，直观的数据可视化和交互式探索是理解复杂模型、发现数据规律和建立信任的最有效途径。' },
  { icon: MagicStick, title: '开放与可扩展', description: '平台采用“CSV驱动”的开放架构。研究者无需修改任何前后端代码，仅通过更新数据文件，即可集成、验证和对比新的算法成果。' },
]);

// 自研模型数据
const models = ref([
  {
    name: 'TimeFlowDiffuser',
    tagline: '层级扩散，生成未来',
    description: '通过创新的层级式扩散框架，将生成模型的强大威力引入时序领域，尤其擅长处理长周期预测和复杂条件分布，为预测提供更丰富的可能性。',
    imageUrl: 'https://www.weili.space/about/images/timeflowdiffuser.png',
  },
  {
    name: 'EnergyPatchTST',
    tagline: '多尺度分解与不确定性量化',
    description: '专为能源领域设计，它将序列分块（Patching）并结合多尺度分析，同时创新地引入概率预测，输出预测区间而非单点，为风险决策提供关键信息。',
    imageUrl: 'https://www.weili.space/about/images/energypatchtst.png',
  },
  {
    name: 'LWSpace',
    tagline: '小波变换与状态空间',
    description: '将经典的小波分析与现代的状态空间模型（SSM）有机结合，能够在不同频率上对序列进行精细建模，对多变和充满噪声的数据具有极强的鲁棒性。',
    imageUrl: 'https://www.weili.space/about/images/lwspace.png',
  },
  {
    name: 'SWIFT',
    tagline: '双路径协同，高效预测',
    description: '协同融合了选择性状态空间（Mamba）和多尺度扩张卷积，通过双路径架构并行捕捉长程依赖和多尺度模式，实现了预测精度与效率的完美平衡。',
    imageUrl: 'https://www.weili.space/about/images/swift.png',
  },
]);

// 导览步骤数据
const steps = ref([
    { title: '探索科研成果', description: '在「科研成果探索」模块，选择我们预置的数据集，直观地对比多个SOTA模型在真实数据上的预测表现、MAE和MSE等关键指标。' },
    { title: '深入算法原理', description: '在「算法介绍」页面，我们为您详细解读了每个自研模型的核心思想、关键创新和架构图，并提供了论文和代码链接以供深入研究。' },
    { title: '体验实时预测', description: '在「实时预测体验」模块，您可以上传自己的CSV格式时间序列数据，平台将立即使用内置模型进行预测，让您亲身体验算法的实际效果。' }
])
</script>

<style scoped>
.about-page {
  padding: 0;
  max-width: 1200px;
  margin: 0 auto;
}

/* --- Hero Section --- */
.hero-section {
  text-align: center;
  padding: 5rem 2rem;
  margin-bottom: 4rem;
  border-radius: 18px;
  background: radial-gradient(circle, rgba(29,47,80,1) 0%, rgba(12,26,50,1) 100%);
  border: 1px solid #1e293b;
  overflow: hidden;
  position: relative;
}
.hero-content {
  position: relative;
  z-index: 2;
}
.hero-title {
  font-size: 3.2rem;
  font-weight: 800;
  background: -webkit-linear-gradient(45deg, #a78bfa, #38bdf8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 1rem 0;
}
.hero-subtitle {
  font-size: 1.2rem;
  color: #94a3b8;
  margin-bottom: 2.5rem;
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
}
.hero-section .el-button {
  font-weight: bold;
}

/* --- Section Title --- */
.section-title {
  text-align: center;
  font-size: 2.2rem;
  font-weight: 700;
  color: #e2e8f0;
  margin: 4rem 0 2.5rem 0;
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
}
.section-title span {
  position: relative;
  padding: 0 20px;
  background-color: #082a42; /* 与主背景色相同，制造断线效果 */
}
.section-title::before {
  content: '';
  position: absolute;
  width: 30%;
  height: 1px;
  background: linear-gradient(90deg, transparent, #1e293b, transparent);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: -1;
}

/* --- Philosophy Section --- */
.philosophy-card {
  background-color: #0c1a32;
  border: 1px solid #1e293b;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  height: 100%;
}
.philosophy-icon {
  font-size: 2.5rem;
  color: #87cefa;
  margin-bottom: 1rem;
}
.philosophy-card h3 {
  color: #e2e8f0;
  font-size: 1.3rem;
  margin: 0 0 1rem 0;
}
.philosophy-card p {
  color: #94a3b8;
  line-height: 1.7;
}

/* --- Models Section --- */
.intro-paragraph {
  text-align: center;
  max-width: 800px;
  margin: 0 auto 2.5rem auto;
  color: #b0c4de;
  font-size: 1.1rem;
  line-height: 1.8;
}

.models-grid {
  display: grid;
  /* 默认是单列 */
  grid-template-columns: repeat(1, 1fr); 
  gap: 1.5rem;
}

/* 在中等屏幕及以上 (>=768px)，变为两列 */
@media (min-width: 768px) {
  .models-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.model-intro-card {
  background-color: #0c1a32;
  border: 1px solid #1e293b;
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}
.model-intro-card:hover {
  transform: scale(1.03);
  box-shadow: 0 10px 30px -10px rgba(0,0,0,0.5);
  border-color: #409eff;
}

.model-card-header {
  position: relative;
  height: 200px;
}
.model-image {
  width: 100%;
  height: 100%;
  filter: brightness(0.7);
}
.model-name-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 1rem;
  background: linear-gradient(to top, rgba(12, 26, 50, 0.9) 0%, transparent 100%);
}
.model-name-overlay h3 {
  margin: 0;
  color: #fff;
  font-size: 1.5rem;
}
.model-name-overlay span {
  color: #87cefa;
  font-size: 0.9rem;
  font-weight: bold;
}

.model-card-body {
  padding: 1.5rem;
}
.model-card-body p {
  color: #b0c4de;
  line-height: 1.7;
  margin: 0;
}

.action-center {
  text-align: center;
  margin-top: 2.5rem;
}

/* --- Getting Started Section --- */
.getting-started-container {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.getting-started-step {
  display: flex;
  align-items: flex-start;
  background-color: #0c1a32;
  border: 1px solid #1e293b;
  border-radius: 10px;
  padding: 1.5rem;
  gap: 1.5rem;
}
.step-number {
  flex-shrink: 0;
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background-color: #1e293b;
  color: #87cefa;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  font-weight: bold;
}
.step-content h4 {
  margin: 0 0 0.5rem 0;
  color: #e2e8f0;
  font-size: 1.2rem;
}
.step-content p {
  margin: 0;
  color: #94a3b8;
  line-height: 1.7;
}
</style>