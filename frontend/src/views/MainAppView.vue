<template>
  <div>
    <h1 class="page-title">{{ $route.meta.title }}</h1>
    <el-row :gutter="24">
      <el-col :xs="24" :lg="14" style="margin-bottom: 24px;">
        <ResearchExplorer />
      </el-col>
      <el-col :xs="24" :lg="10">
        <LivePredictor />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import ResearchExplorer from '@/components/ResearchExplorer.vue';
import LivePredictor from '@/components/LivePredictor.vue';
</script>