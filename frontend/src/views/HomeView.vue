<template>
  <div class="home-view">
    
    <!-- 1. 直接在这里添加图片 -->
    <img src="@/assets/logo.png" alt="Project Logo" class="home-logo">

    <h1>鼠先知 SHU Prophet 平台</h1>
    <p class="subtitle">新一代时序智能预测与决策平台</p>
    <p class="subtitle">作者：Wei Li</p>

    <!-- 论文徽章展示墙 -->
    <div class="badge-grid">
      <div class="badge-card ccf-b">
        <div class="badge-rank">CCF-B</div>
        <div class="badge-conf">ICASSP 2026</div>
        <div class="badge-model">ScatterFusion</div>
      </div>
      <div class="badge-card ccf-b">
        <div class="badge-rank">CCF-B</div>
        <div class="badge-conf">ICASSP 2026</div>
        <div class="badge-model">AWGFormer</div>
      </div>
      <div class="badge-card ccf-c">
        <div class="badge-rank">CCF-C</div>
        <div class="badge-conf">ICANN 2025</div>
        <div class="badge-model">SWIFT</div>
      </div>
      <div class="badge-card ccf-c">
        <div class="badge-rank">CCF-C</div>
        <div class="badge-conf">ICIC 2025</div>
        <div class="badge-model">LWSpace</div>
      </div>
      <div class="badge-card ccf-c">
        <div class="badge-rank">CCF-C</div>
        <div class="badge-conf">ICIC 2025</div>
        <div class="badge-model">EnergyPatchTST</div>
      </div>
      <div class="badge-card ccf-c">
        <div class="badge-rank">CCF-C</div>
        <div class="badge-conf">ICANN 2025</div>
        <div class="badge-model">TimeFlowDiffuser</div>
      </div>
    </div>

    <el-button type="primary" size="large" @click="$router.push('/app')" round>
      进入核心功能 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
    </el-button>
    
  </div>
</template>

<script setup>
// Script 区域现在是空的，因为我们直接在模板中引用图片
</script>

<style scoped>
.home-view { 
  text-align: center; 
  padding-top: 10vh; 
}

/* 2. 为图片添加一点样式 */
.home-logo {
  max-width: 480px; /* 设置最大宽度 */
  width: 80%;       /* 宽度为父容器的80% */
  height: auto;     /* 高度自适应 */
  margin-bottom: -1.5rem;
}

/* --- 下面的样式保持不变 --- */
.home-view h1 {
  font-size: 3.5rem;
  font-weight: 800;
  background: linear-gradient(45deg, #38bdf8, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 1rem;
}

.home-view .subtitle {
  font-size: 1.25rem;
  color: #94a3b8;
  margin-bottom: 2.5rem;
}

.badge-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin: 2rem auto;
  max-width: 900px;
}

.badge-card {
  padding: 1.5rem;
  border-radius: 12px;
  text-align: center;
  transition: transform 0.3s;
  cursor: pointer;
}

.badge-card:hover {
  transform: translateY(-5px);
}

.badge-card.ccf-b {
  background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%);
  animation: pulse 2s ease-in-out infinite;
}

.badge-card.ccf-c {
  background: linear-gradient(135deg, #E0BFB8 0%, #B76E79 100%);
}

@keyframes pulse {
  0%, 100% { box-shadow: 0 0 20px rgba(255, 215, 0, 0.5); }
  50% { box-shadow: 0 0 40px rgba(255, 215, 0, 0.8); }
}

.badge-rank {
  font-size: 1.5rem;
  font-weight: 800;
  color: #1a1a1a;
  margin-bottom: 0.5rem;
}

.badge-conf {
  font-size: 0.9rem;
  font-weight: 600;
  color: #2a2a2a;
  margin-bottom: 0.3rem;
}

.badge-model {
  font-size: 1rem;
  font-weight: 500;
  color: #3a3a3a;
}
</style>