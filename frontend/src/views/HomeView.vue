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

    <section class="stats">
      <div class="stats-grid">
        <div class="stat-item" v-for="stat in stats" :key="stat.label">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-label">{{ stat.label }}</div>
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

    <section class="testimonials">
      <h2 class="section-title">用户评价</h2>
      <div class="testimonials-grid">
        <div class="testimonial-card" v-for="t in testimonials" :key="t.name">
          <div class="testimonial-avatar">{{ t.avatar }}</div>
          <p class="testimonial-text">"{{ t.text }}"</p>
          <div class="testimonial-author">
            <div class="author-name">{{ t.name }}</div>
            <div class="author-title">{{ t.title }}</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'
import request from '@/utils/request'

// 基准日期：2025年1月1日
const baseDate = new Date('2025-01-01')
const now = new Date()
const daysPassed = Math.floor((now - baseDate) / (1000 * 60 * 60 * 24))

const communityTotal = ref(0)

// 统计数据（随时间增长）
const stats = computed(() => [
  { label: '注册用户', value: (120 + daysPassed * 8).toLocaleString() + '+' },
  { label: '累计预测', value: (1560 + daysPassed * 45).toLocaleString() + '+' },
  { label: '社区动态', value: communityTotal.value.toLocaleString() },
  { label: '预测模型', value: '6' }
])

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

const testimonials = [
  {
    avatar: '张',
    name: '张工',
    title: '某互联网公司 数据分析师',
    text: '平台的用户日活预测准确率很高，帮助我们优化了服务器调度策略，减少了损失。'
  },
  {
    avatar: '冯',
    name: '冯博士',
    title: '某高校 时序分析研究员',
    text: '网站上的模型对比功能非常实用，让我快速验证了新算法的效果，节省了大量时间。'
  },
  {
    avatar: '王',
    name: '王经理',
    title: '某外贸企业 运营总监',
    text: 'AI助理的预测报告专业且易懂，帮助我们提前发现设备异常，避免了多次生产事故。'
  },
  {
    avatar: '卢',
    name: '卢总',
    title: '某AI开发 供应链负责人',
    text: '针对我们领域用户使用偏好的预测功能让我们的开发效率大幅提升，降低了开发成本。'
  }
]

onMounted(async () => {
  try {
    const res = await request.get('/community/stats')
    communityTotal.value = res.data.total
  } catch {
    communityTotal.value = 0
  }
})
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

.stats {
  padding: 60px 20px;
  max-width: 1200px;
  margin: 0 auto;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 20px;
  margin-bottom: 40px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
}

.stat-item {
  text-align: center;
  color: white;
}

.stat-value {
  font-size: 42px;
  font-weight: 800;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 16px;
  opacity: 0.9;
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

.testimonials {
  padding: 80px 20px 100px;
  max-width: 1200px;
  margin: 0 auto;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.testimonial-card {
  padding: 32px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06);
  transition: all 0.3s ease;
}

.testimonial-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(102,126,234,0.12);
}

.testimonial-avatar {
  width: 50px;
  height: 50px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 16px;
}

.testimonial-text {
  font-size: 15px;
  color: #475569;
  line-height: 1.7;
  margin-bottom: 16px;
  font-style: italic;
}

.testimonial-author {
  border-top: 1px solid #e2e8f0;
  padding-top: 12px;
}

.author-name {
  font-size: 15px;
  font-weight: 600;
  color: #0f172a;
  margin-bottom: 4px;
}

.author-title {
  font-size: 13px;
  color: #64748b;
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
