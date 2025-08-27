<template>
  <el-container class="app-layout">
    <el-aside width="220px" class="app-aside">
      <div class="logo">
        <el-icon><TrendCharts /></el-icon>
        <span>鼠先知 SHU Prophet</span>
      </div>
      <el-menu
        :default-active="$route.path"
        class="el-menu-vertical-demo"
        background-color="#0c1a32"
        text-color="rgba(255, 255, 255, 0.7)"
        active-text-color="#409eff"
        :router="true"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>项目概览</span>
        </el-menu-item>
        <el-menu-item index="/app">
          <el-icon><DataAnalysis /></el-icon>
          <span>核心功能</span>
        </el-menu-item>
        <el-menu-item index="/algorithms">
          <el-icon><Cpu /></el-icon>
          <span>算法文库</span>
        </el-menu-item>
        <el-menu-item index="/about">
          <el-icon><InfoFilled /></el-icon>
          <span>关于项目</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </el-main>
  </el-container>
</template>

<script setup>
// --- 新增代码开始 ---
import { onMounted } from 'vue';
import logoUrl from '@/assets/logo.png'; // 1. 从 assets 导入图片

onMounted(() => {
  // 2. 动态创建或更新 link 标签
  let link = document.querySelector("link[rel~='icon']");
  if (!link) {
    link = document.createElement('link');
    link.rel = 'icon';
    document.getElementsByTagName('head')[0].appendChild(link);
  }
  link.href = logoUrl; // 3. 将 Vite 处理后的绝对 URL 赋给 href
});
// --- 新增代码结束 ---
</script>