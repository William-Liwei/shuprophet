<template>
  <div>
    <h1 class="page-title">{{ $route.meta.title }}</h1>
    <el-row :gutter="24">
      <el-col :xs="24" :lg="16" style="margin-bottom: 24px;">
        <ResearchExplorer />
      </el-col>
      <el-col :xs="24" :lg="8">
        <div class="guide-card">
          <div class="guide-icon">🤖</div>
          <h3>需要预测分析？</h3>
          <p>使用我们的 AI 智能助理，上传数据即可获得专业的预测报告和深度分析。</p>
          <el-button type="primary" @click="$router.push('/agent')">前往智能助理</el-button>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import ResearchExplorer from '@/components/ResearchExplorer.vue';
</script>

<style scoped>
.guide-card {
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 32px;
  text-align: center;
  border: 1px solid rgba(255,255,255,0.5);
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
}
.guide-icon {
  font-size: 48px;
  margin-bottom: 16px;
}
.guide-card h3 {
  font-size: 1.3rem;
  color: #1d1d1f;
  margin: 0 0 12px 0;
}
.guide-card p {
  color: #6e6e73;
  line-height: 1.6;
  margin-bottom: 20px;
}
</style>