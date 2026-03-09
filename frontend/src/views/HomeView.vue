<template>
  <div class="home-view">
    <section class="hero">
      <div class="hero-content">
        <h1 class="hero-title">学术驱动的智能时序预测平台</h1>
        <p class="hero-subtitle">基于6篇CCF论文的前沿算法 · 零代码门槛 · 秒级专业预测</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/agent')" round>
            免费试用 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <el-button size="large" @click="$router.push('/algorithms')" round>查看论文</el-button>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="feature-grid">
        <div class="feature-item" v-for="f in features" :key="f.title">
          <div class="feature-icon">{{ f.icon }}</div>
          <h3>{{ f.title }}</h3>
          <p>{{ f.desc }}</p>
        </div>
      </div>
    </section>

    <section class="papers">
      <h2 class="section-title">学术成果</h2>
      <div class="papers-grid">
        <div class="paper-card" v-for="p in papers" :key="p.model">
          <div class="paper-badge" :class="p.rank.toLowerCase().replace('-','')">{{ p.rank }}</div>
          <div class="paper-model">{{ p.model }}</div>
          <div class="paper-conf">{{ p.conf }}</div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ArrowRight } from '@element-plus/icons-vue'

const features = [
  { icon: '🏢', title: '新能源预测', desc: '风电/光伏功率预测，助力双碳战略' },
  { icon: '🏭', title: '工业物联网', desc: '设备预测性维护，降低故障停机损失' },
  { icon: '📦', title: '供应链管理', desc: '销量预测与动态库存优化' },
  { icon: '🔬', title: '前沿算法', desc: '智能预测引擎自动路由选择最优算法' },
]

const papers = [
  { rank: 'CCF-B', conf: 'ICASSP 2026', model: 'ScatterFusion' },
  { rank: 'CCF-B', conf: 'ICASSP 2026', model: 'AWGFormer' },
  { rank: 'CCF-C', conf: 'ICANN 2025', model: 'SWIFT' },
  { rank: 'CCF-C', conf: 'ICIC 2025', model: 'LWSpace' },
  { rank: 'CCF-C', conf: 'ICIC 2025', model: 'EnergyPatchTST' },
  { rank: 'CCF-C', conf: 'ICANN 2025', model: 'TimeFlowDiffuser' },
]
</script>

<style scoped>
.home-view {
  min-height: 100vh;
  background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
}

.hero {
  padding: 120px 20px 80px;
  text-align: center;
  background: linear-gradient(135deg, rgba(59,130,246,0.05) 0%, rgba(147,51,234,0.05) 100%);
}

.hero-content {
  max-width: 900px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 20px;
  line-height: 1.2;
  letter-spacing: -0.02em;
}

.hero-subtitle {
  font-size: 18px;
  color: #64748b;
  margin: 0 0 40px;
  line-height: 1.6;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.features {
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 24px;
}

.feature-item {
  padding: 32px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.feature-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0,0,0,0.08);
}

.feature-icon {
  font-size: 40px;
  margin-bottom: 16px;
}

.feature-item h3 {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  margin: 0 0 8px;
}

.feature-item p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.6;
}

.papers {
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 32px;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
  margin: 0 0 48px;
}

.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.paper-card {
  padding: 24px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
}

.paper-card:hover {
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.paper-badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  margin-bottom: 12px;
}

.paper-badge.ccfb {
  background: #fef3c7;
  color: #92400e;
}

.paper-badge.ccfc {
  background: #e0e7ff;
  color: #3730a3;
}

.paper-model {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 4px;
}

.paper-conf {
  font-size: 13px;
  color: #64748b;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }
  .hero-subtitle {
    font-size: 16px;
  }
  .feature-grid, .papers-grid {
    grid-template-columns: 1fr;
  }
}
</style>
