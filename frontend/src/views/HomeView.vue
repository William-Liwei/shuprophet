<template>
  <div class="home-view">
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <img src="@/assets/logo.png" alt="鼠先知" class="hero-logo" />
        <h1 class="hero-title">新一代时序智能预测与决策平台</h1>
        <p class="hero-subtitle">基于6篇CCF论文的前沿算法 · 零代码门槛 · 秒级专业预测</p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/agent')" round class="btn-primary">
            免费试用 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <el-button size="large" @click="$router.push('/algorithms')" round class="btn-secondary">查看论文</el-button>
        </div>
      </div>
    </section>

    <section class="features">
      <div class="feature-grid">
        <div class="feature-item" v-for="(f, i) in features" :key="f.title" :style="{ animationDelay: `${i * 0.1}s` }">
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
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.home-view {
  min-height: 100vh;
  background: #ffffff;
}

.hero {
  position: relative;
  padding: 100px 20px 120px;
  text-align: center;
  overflow: hidden;
  background: #ffffff;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: transparent;
  opacity: 0;
}

.hero-content {
  position: relative;
  max-width: 900px;
  margin: 0 auto;
}

.hero-logo {
  max-width: 320px;
  height: auto;
  margin-bottom: 40px;
}

.hero-title {
  font-size: 52px;
  font-weight: 800;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin: 0 0 20px;
  line-height: 1.2;
  letter-spacing: -0.03em;
}

.hero-subtitle {
  font-size: 18px;
  color: #64748b;
  margin: 0 0 40px;
  line-height: 1.8;
}

.hero-actions {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  padding: 14px 40px;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 10px 30px rgba(102,126,234,0.3);
  transition: all 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 15px 40px rgba(102,126,234,0.4);
}

.btn-secondary {
  padding: 14px 40px;
  font-size: 16px;
  font-weight: 600;
  border: 2px solid #667eea;
  color: #667eea;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
  transform: translateY(-2px);
}

.features {
  padding: 80px 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 30px;
}

.feature-item {
  padding: 40px 32px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 4px 20px rgba(0,0,0,0.06);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.6s ease-out backwards;
}

.feature-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(102,126,234,0.15);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-item h3 {
  font-size: 20px;
  font-weight: 700;
  color: #0f172a;
  margin: 0 0 12px;
}

.feature-item p {
  font-size: 14px;
  color: #64748b;
  margin: 0;
  line-height: 1.7;
}

.papers {
  padding: 80px 20px 100px;
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(180deg, transparent 0%, rgba(102,126,234,0.02) 100%);
}

.section-title {
  font-size: 36px;
  font-weight: 800;
  color: #0f172a;
  text-align: center;
  margin: 0 0 50px;
}

.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.paper-card {
  padding: 28px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
  transition: all 0.3s ease;
  border: 1px solid rgba(102,126,234,0.1);
}

.paper-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(102,126,234,0.15);
  border-color: rgba(102,126,234,0.3);
}

.paper-badge {
  display: inline-block;
  padding: 6px 14px;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 14px;
}

.paper-badge.ccfb {
  background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%);
  color: white;
}

.paper-badge.ccfc {
  background: linear-gradient(135deg, #a78bfa 0%, #8b5cf6 100%);
  color: white;
}

.paper-model {
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
  margin-bottom: 6px;
}

.paper-conf {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 36px;
  }
  .hero-subtitle {
    font-size: 16px;
  }
  .hero-logo {
    max-width: 200px;
  }
  .feature-grid, .papers-grid {
    grid-template-columns: 1fr;
  }
}
</style>
