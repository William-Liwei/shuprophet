<template>
  <div class="home-view">
    <section class="hero">
      <div class="hero-bg"></div>
      <div class="hero-content">
        <div
          ref="logoStageRef"
          class="hero-brand"
          @pointerenter="handleLogoPointerEnter"
          @pointerleave="handleLogoPointerLeave"
          @pointermove="handleLogoPointerMove"
        >
          <canvas ref="logoCanvasRef" class="hero-brand-canvas" aria-hidden="true"></canvas>
          <div class="hero-brand-copy">
            <div class="hero-brand-heading">
              <div class="hero-brand-cn">鼠先知</div>
              <div class="hero-brand-en">
                <span>SHU</span>
                <span>Prophet</span>
              </div>
            </div>
            <p class="hero-brand-tagline">新一代时序智能预测与决策平台</p>
          </div>
        </div>

        <h1 class="hero-title">从学术前沿到行业决策的时间序列智能引擎</h1>
        <p class="hero-subtitle">
          基于 6 篇 CCF 论文成果构建的预测体系，覆盖多尺度建模、不确定性推断与智能路由，
          支持零代码实验、多模型对比和秒级专业预测。
        </p>
        <div class="hero-actions">
          <el-button type="primary" size="large" @click="$router.push('/agent')" round class="btn-primary">
            免费试用 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
          </el-button>
          <el-button size="large" @click="$router.push('/algorithms')" round class="btn-secondary">
            查看论文
          </el-button>
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
        <div
          class="feature-item"
          v-for="(feature, index) in features"
          :key="feature.title"
          :style="{ animationDelay: `${index * 0.1}s`, backgroundImage: `url(${feature.bg})` }"
        >
          <div class="feature-content">
            <div class="feature-icon">{{ feature.icon }}</div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.desc }}</p>
          </div>
        </div>
      </div>
    </section>

    <section class="papers">
      <h2 class="section-title">学术成果</h2>
      <div class="papers-grid">
        <div class="paper-card" v-for="paper in papers" :key="paper.model">
          <div class="paper-badge" :class="paper.rank.toLowerCase().replace('-', '')">{{ paper.rank }}</div>
          <div class="paper-model">{{ paper.model }}</div>
          <div class="paper-conf">{{ paper.conf }}</div>
        </div>
      </div>
    </section>

    <section class="testimonials">
      <h2 class="section-title">用户评价</h2>
      <div class="testimonials-grid">
        <div class="testimonial-card" v-for="testimonial in testimonials" :key="testimonial.name">
          <div class="testimonial-avatar">{{ testimonial.avatar }}</div>
          <p class="testimonial-text">"{{ testimonial.text }}"</p>
          <div class="testimonial-author">
            <div class="author-name">{{ testimonial.name }}</div>
            <div class="author-title">{{ testimonial.title }}</div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'
import request from '@/utils/request'

const TAU = Math.PI * 2
const strandPalette = [
  {
    stroke: 'rgba(139, 90, 43, 0.40)',
    glow: 'rgba(139, 90, 43, 0.22)'
  },
  {
    stroke: 'rgba(210, 180, 140, 0.60)',
    glow: 'rgba(210, 180, 140, 0.26)'
  },
  {
    stroke: 'rgba(205, 133, 63, 0.32)',
    glow: 'rgba(205, 133, 63, 0.18)'
  },
  {
    stroke: 'rgba(160, 112, 67, 0.28)',
    glow: 'rgba(160, 112, 67, 0.16)'
  }
]

const baseDate = new Date('2026-02-01')
const now = new Date()
const daysPassed = Math.max(0, Math.floor((now - baseDate) / (1000 * 60 * 60 * 24)))

const communityTotal = ref(0)
const logoStageRef = ref(null)
const logoCanvasRef = ref(null)

let resizeObserver = null
let animationFrameId = 0
let animationStart = 0
let canvasContext = null
let canvasWidth = 0
let canvasHeight = 0
let hoverBoost = 0
let flowBoost = 0
let flowDirection = 1
let lastPointerMoveTime = 0
let lastPointerClientX = 0
let prefersReducedMotion = false
let strands = []

const pointerState = {
  active: false,
  x: 0.5,
  y: 0.5
}

const stats = computed(() => [
  { label: '注册用户', value: `${(120 + daysPassed * 3).toLocaleString()}+` },
  { label: '累计预测', value: `${(1560 + daysPassed * 17).toLocaleString()}+` },
  { label: '社区动态', value: communityTotal.value.toLocaleString() },
  { label: '预测模型', value: '6' }
])

const features = [
  {
    icon: '风',
    title: '新能源预测',
    desc: '风电与光伏功率预测，支撑发电调度、消纳分析与双碳场景决策。',
    bg: '/features/energy-bg.png'
  },
  {
    icon: '工',
    title: '工业物联网',
    desc: '面向设备运行信号的异常预警与预测性维护，减少非计划停机损失。',
    bg: '/features/iot-bg.png'
  },
  {
    icon: '链',
    title: '供应链管理',
    desc: '从销量到库存的联动预测，帮助企业优化补货节奏与资源配置。',
    bg: '/features/supply-bg.png'
  },
  {
    icon: '算',
    title: '前沿算法引擎',
    desc: '自动路由最优模型组合，将复杂时序研究能力封装成稳定可用的产品体验。',
    bg: '/features/algorithm-bg.png'
  }
]

const papers = [
  { rank: 'CCF-B', conf: 'ICASSP 2026', model: 'ScatterFusion' },
  { rank: 'CCF-B', conf: 'ICASSP 2026', model: 'AWGFormer' },
  { rank: 'CCF-C', conf: 'ICANN 2025', model: 'SWIFT' },
  { rank: 'CCF-C', conf: 'ICIC 2025', model: 'LWSpace' },
  { rank: 'CCF-C', conf: 'ICIC 2025', model: 'EnergyPatchTST' },
  { rank: 'CCF-C', conf: 'ICANN 2025', model: 'TimeFlowDiffuser' }
]

const testimonials = [
  {
    avatar: '张',
    name: '张工',
    title: '某互联网公司 数据分析师',
    text: '平台对用户活跃度的预测相当稳定，帮助我们把资源调度和活动排期做得更准。'
  },
  {
    avatar: '李',
    name: '李博士',
    title: '某高校 时序分析研究员',
    text: '模型对比和可视化很实用，验证新方法时可以快速看出不同架构的优劣。'
  },
  {
    avatar: '王',
    name: '王经理',
    title: '某制造企业 运营负责人',
    text: 'AI 助理生成的报告专业但不晦涩，业务团队也能直接理解和落地执行。'
  },
  {
    avatar: '周',
    name: '周分析师',
    title: '某咨询公司 项目经理',
    text: '页面体验和结果解释都很完整，给客户做汇报时能够直接复用平台内容。'
  }
]

const fetchCommunityStats = async () => {
  try {
    const response = await request.get('/community/stats')
    communityTotal.value = response.data.total
  } catch {
    communityTotal.value = 0
  }
}

const buildStrands = (width, height) => {
  const count = Math.max(28, Math.min(54, Math.round(width / 18)))

  strands = Array.from({ length: count }, (_, index) => {
    const palette = strandPalette[index % strandPalette.length]
    const ratio = count === 1 ? 0.5 : index / (count - 1)

    return {
      baseY: height * (0.16 + ratio * 0.68),
      amplitude: 7 + Math.random() * 16,
      secondaryAmplitude: 3 + Math.random() * 8,
      frequency: 0.65 + Math.random() * 0.8,
      secondaryFrequency: 1.1 + Math.random() * 1.4,
      speed: 0.24 + Math.random() * 0.3,
      phase: Math.random() * TAU,
      thickness: 0.75 + Math.random() * 1.7,
      slant: (Math.random() - 0.5) * height * 0.2,
      stroke: palette.stroke,
      glow: palette.glow,
      blur: 8 + Math.random() * 12
    }
  })
}

const computeWaveY = (strand, progress, time) => {
  const flowPhaseOffset = flowDirection * flowBoost * 0.38
  const primaryPhase =
    (progress + flowPhaseOffset * 0.06) * strand.frequency * TAU +
    time * (strand.speed + flowBoost * 0.34) +
    strand.phase
  const secondaryPhase =
    (progress + flowPhaseOffset * 0.04) * strand.secondaryFrequency * TAU * 0.75 -
    time * (strand.speed + flowBoost * 0.2) * 0.55 +
    strand.phase * 0.5

  let y = strand.baseY
  y += Math.sin(primaryPhase) * strand.amplitude
  y += Math.cos(secondaryPhase) * strand.secondaryAmplitude
  y += progress * strand.slant

  if (pointerState.active && flowBoost > 0.01) {
    const pointerX = pointerState.x * canvasWidth
    const x = progress * canvasWidth
    const distance = x - pointerX
    const spread = canvasWidth * 0.22
    const influence = Math.exp(-(distance * distance) / (2 * spread * spread)) * flowBoost
    const glideWave = Math.sin(progress * TAU * 1.2 + time * 4.2 * flowDirection + strand.phase)

    y += glideWave * influence * 4.5
  }

  return y
}

const drawStrands = (time) => {
  if (!canvasContext || !canvasWidth || !canvasHeight) {
    return
  }

  canvasContext.clearRect(0, 0, canvasWidth, canvasHeight)
  canvasContext.globalCompositeOperation = 'source-over'
  canvasContext.lineCap = 'round'
  canvasContext.lineJoin = 'round'

  const timeFactor = prefersReducedMotion ? 0.24 : 1.04 + hoverBoost * 0.18 + flowBoost * 1.8
  const segments = 18

  strands.forEach((strand, index) => {
    const points = []

    for (let step = 0; step <= segments; step += 1) {
      const progress = step / segments
      points.push({
        x: progress * canvasWidth,
        y: computeWaveY(strand, progress, time * timeFactor)
      })
    }

    canvasContext.beginPath()
    canvasContext.moveTo(points[0].x, points[0].y)

    for (let pointIndex = 1; pointIndex < points.length - 1; pointIndex += 1) {
      const current = points[pointIndex]
      const next = points[pointIndex + 1]
      const controlX = (current.x + next.x) / 2
      const controlY = (current.y + next.y) / 2
      canvasContext.quadraticCurveTo(current.x, current.y, controlX, controlY)
    }

    const penultimate = points[points.length - 2]
    const last = points[points.length - 1]
    canvasContext.quadraticCurveTo(penultimate.x, penultimate.y, last.x, last.y)

    canvasContext.lineWidth = strand.thickness + hoverBoost * 0.12 + flowBoost * 0.16
    canvasContext.strokeStyle = strand.stroke
    canvasContext.shadowBlur = strand.blur + hoverBoost * 2 + flowBoost * 3
    canvasContext.shadowColor = strand.glow
    canvasContext.globalAlpha = 0.8
    canvasContext.stroke()

    if (index % 5 === 0) {
      canvasContext.lineWidth = strand.thickness * 0.5
      canvasContext.strokeStyle = 'rgba(255, 244, 224, 0.28)'
      canvasContext.shadowBlur = strand.blur * (0.9 + flowBoost * 0.16)
      canvasContext.shadowColor = 'rgba(255, 235, 208, 0.24)'
      canvasContext.globalAlpha = 0.42
      canvasContext.stroke()
    }
  })
}

const resizeLogoCanvas = () => {
  const stage = logoStageRef.value
  const canvas = logoCanvasRef.value

  if (!stage || !canvas) {
    return
  }

  const rect = stage.getBoundingClientRect()
  const nextWidth = Math.max(1, Math.round(rect.width))
  const nextHeight = Math.max(1, Math.round(rect.height))
  const devicePixelRatio = Math.min(window.devicePixelRatio || 1, 2)

  canvas.width = Math.round(nextWidth * devicePixelRatio)
  canvas.height = Math.round(nextHeight * devicePixelRatio)
  canvas.style.width = `${nextWidth}px`
  canvas.style.height = `${nextHeight}px`

  canvasContext = canvas.getContext('2d')
  canvasWidth = nextWidth
  canvasHeight = nextHeight

  if (!canvasContext) {
    return
  }

  canvasContext.setTransform(devicePixelRatio, 0, 0, devicePixelRatio, 0, 0)
  buildStrands(nextWidth, nextHeight)
  drawStrands((performance.now() - animationStart) / 1000)
}

const renderLogoFrame = (timestamp) => {
  if (!animationStart) {
    animationStart = timestamp
  }

  hoverBoost += ((pointerState.active ? 1 : 0) - hoverBoost) * 0.08
  flowBoost += (0 - flowBoost) * 0.08
  drawStrands((timestamp - animationStart) / 1000)
  animationFrameId = window.requestAnimationFrame(renderLogoFrame)
}

const setupLogoAnimation = async () => {
  await nextTick()

  if (!logoStageRef.value || !logoCanvasRef.value) {
    return
  }

  prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  animationStart = performance.now()
  resizeLogoCanvas()

  if ('ResizeObserver' in window) {
    resizeObserver = new ResizeObserver(() => {
      resizeLogoCanvas()
    })
    resizeObserver.observe(logoStageRef.value)
  }

  animationFrameId = window.requestAnimationFrame(renderLogoFrame)
}

const handleLogoPointerEnter = () => {
  pointerState.active = true
}

const handleLogoPointerLeave = () => {
  pointerState.active = false
  pointerState.x = 0.5
  pointerState.y = 0.5
  lastPointerMoveTime = 0
}

const handleLogoPointerMove = (event) => {
  const stage = logoStageRef.value

  if (!stage) {
    return
  }

  const rect = stage.getBoundingClientRect()
  const relativeX = (event.clientX - rect.left) / rect.width
  const relativeY = (event.clientY - rect.top) / rect.height

  pointerState.x = Math.min(1, Math.max(0, relativeX))
  pointerState.y = Math.min(1, Math.max(0, relativeY))

  const nowTime = performance.now()

  if (lastPointerMoveTime) {
    const deltaX = event.clientX - lastPointerClientX
    const deltaTime = Math.max(12, nowTime - lastPointerMoveTime)
    const velocity = Math.abs(deltaX) / deltaTime

    if (Math.abs(deltaX) > 0.5) {
      flowDirection = deltaX >= 0 ? 1 : -1
      flowBoost = Math.max(flowBoost, Math.min(1.4, velocity * 1.4))
    }
  }

  lastPointerClientX = event.clientX
  lastPointerMoveTime = nowTime
}

onMounted(() => {
  setupLogoAnimation()
  fetchCommunityStats()
})

onBeforeUnmount(() => {
  if (animationFrameId) {
    window.cancelAnimationFrame(animationFrameId)
  }

  if (resizeObserver) {
    resizeObserver.disconnect()
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

.home-view {
  min-height: 100vh;
  margin-top: -20px;
  background:
    radial-gradient(circle at top left, rgba(231, 217, 198, 0.28), transparent 28%),
    linear-gradient(180deg, #fcfbf8 0%, #ffffff 38%, #fcfaf6 100%);
}

.hero {
  position: relative;
  padding: 108px 20px 120px;
  overflow: hidden;
  text-align: center;
}

.hero::before {
  content: '';
  position: absolute;
  inset: 8% auto auto 8%;
  width: 320px;
  height: 320px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(210, 180, 140, 0.14) 0%, rgba(210, 180, 140, 0) 72%);
  filter: blur(10px);
}

.hero::after {
  content: '';
  position: absolute;
  inset: auto 6% 0 auto;
  width: 420px;
  height: 320px;
  background: radial-gradient(circle, rgba(139, 90, 43, 0.08) 0%, rgba(139, 90, 43, 0) 75%);
  filter: blur(24px);
}

.hero-bg {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(110deg, rgba(255, 255, 255, 0) 0%, rgba(244, 233, 220, 0.2) 48%, rgba(255, 255, 255, 0) 100%);
  opacity: 1;
}

.hero-content {
  position: relative;
  z-index: 1;
  max-width: 980px;
  margin: 0 auto;
}

.hero-brand {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 250px;
  margin: 0 auto 42px;
  padding: 22px 18px;
  overflow: hidden;
  isolation: isolate;
}

.hero-brand::after {
  content: '';
  position: absolute;
  inset: 14% 18%;
  background:
    radial-gradient(circle at center, rgba(255, 255, 255, 0.54) 0%, rgba(255, 255, 255, 0.12) 44%, rgba(255, 255, 255, 0) 74%);
  filter: blur(28px);
  z-index: 1;
  pointer-events: none;
}

.hero-brand-canvas {
  position: absolute;
  inset: 0;
  z-index: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  opacity: 0.96;
  mix-blend-mode: multiply;
}

.hero-brand-copy {
  position: relative;
  z-index: 2;
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 18px 28px 20px;
}

.hero-brand-copy::before {
  content: '';
  position: absolute;
  inset: 4% -12% 2%;
  z-index: -1;
  background:
    radial-gradient(ellipse at center, rgba(255, 255, 255, 0.44) 0%, rgba(255, 255, 255, 0.16) 42%, rgba(255, 255, 255, 0.04) 62%, rgba(255, 255, 255, 0) 82%);
  border-radius: 999px;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  mask-image: linear-gradient(90deg, transparent 0%, rgba(0, 0, 0, 0.78) 16%, #000 50%, rgba(0, 0, 0, 0.78) 84%, transparent 100%);
  -webkit-mask-image: linear-gradient(90deg, transparent 0%, rgba(0, 0, 0, 0.78) 16%, #000 50%, rgba(0, 0, 0, 0.78) 84%, transparent 100%);
}

.hero-brand-heading {
  display: flex;
  align-items: flex-end;
  gap: clamp(18px, 4vw, 54px);
}

.hero-brand-cn {
  font-family: 'Source Han Sans SC', 'Noto Sans SC', 'PingFang SC', sans-serif;
  font-size: clamp(56px, 11vw, 116px);
  line-height: 0.92;
  font-weight: 900;
  letter-spacing: 0.02em;
  color: #15284a;
  text-shadow: 0 10px 30px rgba(255, 255, 255, 0.42);
}

.hero-brand-en {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  font-family: 'Avenir Next', 'Montserrat', 'Segoe UI', sans-serif;
  font-size: clamp(30px, 5vw, 74px);
  line-height: 0.88;
  font-weight: 800;
  letter-spacing: -0.05em;
  color: #17305b;
  text-transform: uppercase;
  text-shadow: 0 10px 30px rgba(255, 255, 255, 0.42);
}

.hero-brand-tagline {
  margin: 0;
  font-size: clamp(18px, 2.4vw, 30px);
  line-height: 1.25;
  font-weight: 400;
  letter-spacing: 0.18em;
  color: #6b5236;
}

.hero-title {
  max-width: 860px;
  margin: 0 auto 18px;
  font-family: 'Source Han Serif SC', 'Songti SC', serif;
  font-size: clamp(38px, 5.2vw, 56px);
  line-height: 1.15;
  font-weight: 700;
  color: #162844;
  letter-spacing: -0.03em;
}

.hero-subtitle {
  max-width: 720px;
  margin: 0 auto 40px;
  font-size: 18px;
  line-height: 1.9;
  color: #5f6978;
}

.hero-actions {
  display: flex;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;
}

.btn-primary {
  padding: 14px 40px;
  border: none;
  background: linear-gradient(135deg, #8b5a2b 0%, #c7925b 62%, #d2b48c 100%);
  box-shadow: 0 14px 34px rgba(139, 90, 43, 0.26);
  font-size: 16px;
  font-weight: 600;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 40px rgba(139, 90, 43, 0.34);
}

.btn-secondary {
  padding: 14px 40px;
  border: 1px solid rgba(139, 90, 43, 0.28);
  background: rgba(255, 255, 255, 0.72);
  color: #7a5630;
  box-shadow: 0 10px 26px rgba(97, 74, 49, 0.08);
  font-size: 16px;
  font-weight: 600;
  transition: transform 0.3s ease, background 0.3s ease, color 0.3s ease;
}

.btn-secondary:hover {
  transform: translateY(-2px);
  background: rgba(139, 90, 43, 0.1);
  color: #5e3e20;
}

.stats {
  max-width: 1200px;
  margin: 0 auto 40px;
  padding: 60px 20px;
  border-radius: 24px;
  background: linear-gradient(135deg, #6a4527 0%, #9c6a3d 52%, #cfb190 100%);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 40px;
}

.stat-item {
  text-align: center;
  color: #fffaf2;
}

.stat-value {
  margin-bottom: 8px;
  font-size: 42px;
  font-weight: 800;
}

.stat-label {
  font-size: 16px;
  opacity: 0.92;
}

.features {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 30px;
}

.feature-item {
  position: relative;
  display: flex;
  align-items: center;
  min-height: 280px;
  padding: 40px 32px;
  overflow: hidden;
  border-radius: 22px;
  background: #ffffff;
  background-position: center;
  background-size: cover;
  box-shadow: 0 10px 30px rgba(48, 37, 24, 0.07);
  transition: transform 0.4s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  animation: fadeInUp 0.6s ease-out backwards;
}

.feature-item::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.78) 0%, rgba(255, 252, 246, 0.9) 100%);
  z-index: 1;
}

.feature-content {
  position: relative;
  z-index: 2;
  width: 100%;
  text-align: center;
}

.feature-item:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(139, 90, 43, 0.14);
}

.feature-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(139, 90, 43, 0.16), rgba(210, 180, 140, 0.32));
  color: #6a4527;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  font-weight: 700;
}

.feature-item h3 {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 700;
  color: #162844;
}

.feature-item p {
  margin: 0;
  font-size: 14px;
  line-height: 1.75;
  color: #5f6978;
}

.papers {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px 100px;
}

.section-title {
  margin: 0 0 50px;
  text-align: center;
  font-size: 36px;
  font-weight: 800;
  color: #162844;
}

.papers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.paper-card {
  padding: 28px;
  border: 1px solid rgba(139, 90, 43, 0.14);
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 10px 24px rgba(48, 37, 24, 0.05);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
}

.paper-card:hover {
  transform: translateY(-4px);
  border-color: rgba(139, 90, 43, 0.32);
  box-shadow: 0 16px 36px rgba(139, 90, 43, 0.12);
}

.paper-badge {
  display: inline-block;
  margin-bottom: 14px;
  padding: 6px 14px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.paper-badge.ccfb {
  background: linear-gradient(135deg, #c68a4d 0%, #9a5f2b 100%);
  color: #fff7ef;
}

.paper-badge.ccfc {
  background: linear-gradient(135deg, #d7bc92 0%, #ae7e4f 100%);
  color: #fffaf4;
}

.paper-model {
  margin-bottom: 6px;
  font-size: 17px;
  font-weight: 700;
  color: #162844;
}

.paper-conf {
  font-size: 13px;
  font-weight: 500;
  color: #5f6978;
}

.testimonials {
  max-width: 1200px;
  margin: 0 auto;
  padding: 80px 20px 100px;
}

.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 24px;
}

.testimonial-card {
  padding: 32px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.88);
  box-shadow: 0 10px 30px rgba(48, 37, 24, 0.06);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.testimonial-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 16px 36px rgba(139, 90, 43, 0.12);
}

.testimonial-avatar {
  width: 50px;
  height: 50px;
  margin-bottom: 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #8b5a2b 0%, #d2b48c 100%);
  color: #fff8ef;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 700;
}

.testimonial-text {
  margin-bottom: 16px;
  font-size: 15px;
  line-height: 1.75;
  color: #485567;
  font-style: italic;
}

.testimonial-author {
  padding-top: 12px;
  border-top: 1px solid rgba(95, 105, 120, 0.16);
}

.author-name {
  margin-bottom: 4px;
  font-size: 15px;
  font-weight: 600;
  color: #162844;
}

.author-title {
  font-size: 13px;
  color: #5f6978;
}

@media (max-width: 768px) {
  .hero {
    padding-top: 88px;
    padding-bottom: 96px;
  }

  .hero-brand {
    min-height: 210px;
    margin-bottom: 34px;
  }

  .hero-brand-heading {
    flex-direction: column;
    align-items: center;
    gap: 10px;
  }

  .hero-brand-en {
    align-items: center;
  }

  .hero-brand-tagline {
    letter-spacing: 0.1em;
  }

  .hero-subtitle {
    font-size: 16px;
  }

  .feature-grid,
  .papers-grid {
    grid-template-columns: 1fr;
  }
}
</style>
