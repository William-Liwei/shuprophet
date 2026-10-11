<template>
  <div v-if="job && job.status !== 'completed'" :class="['s-job', { 's-job-failed': job.status === 'failed' }]" role="status" aria-live="polite">
    <span :class="{ 's-spinner': job.status !== 'failed' }">{{ job.status === 'failed' ? '!' : '' }}</span>
    <div><strong>{{ labels[job.status] }}</strong><p>{{ job.error || job.progress }}</p><small v-if="job.status === 'queued'">任务已保存，离开页面后可返回查看。</small></div><code>{{ job.id.slice(0, 8) }}</code>
  </div>
</template>
<script setup>
defineProps({ job: Object })
const labels = { queued: '等待鼠先知引擎', running: '正在执行实验', failed: '实验未完成' }
</script>
