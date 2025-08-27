<template>
  <el-container class="app-layout">
    <!-- 侧边栏: 添加了 :class 绑定，用于移动端显示/隐藏 -->
    <el-aside 
      width="220px" 
      class="app-aside" 
      :class="{ 'is-mobile-open': isMobileMenuOpen }"
    >
      <div class="logo">
        <el-icon><TrendCharts /></el-icon>
        <span>鼠先知 SHU Prophet</span>
      </div>
      <!-- 菜单: 添加了 @select 事件，用于在移动端点击后收起菜单 -->
      <el-menu
        :default-active="$route.path"
        class="el-menu-vertical-demo"
        background-color="#0c1a32"
        text-color="rgba(255, 255, 255, 0.7)"
        active-text-color="#409eff"
        :router="true"
        @select="handleMenuSelect" 
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

    <!-- [修改] 将 el-main 包裹在一个新的 el-container 中，以便添加 el-header -->
    <el-container>
      <!-- [新增] 移动端专用的顶部栏 -->
      <el-header class="app-header">
        <div class="mobile-menu-toggle" @click="isMobileMenuOpen = !isMobileMenuOpen">
          <el-icon><Menu /></el-icon>
        </div>
        <div class="header-title">鼠先知 SHU Prophet</div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="app-main">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
    </el-container>

    <!-- [新增] 移动端菜单打开时的遮罩层 -->
    <div 
      v-if="isMobileMenuOpen" 
      class="menu-overlay" 
      @click="isMobileMenuOpen = false"
    ></div>

  </el-container>
</template>

<script setup>
// [修改] 导入 onMounted 和 ref
import { onMounted, ref } from 'vue';
// [新增] 导入移动端菜单需要的新图标
import { Menu, TrendCharts, House, DataAnalysis, Cpu, InfoFilled } from '@element-plus/icons-vue';
import logoUrl from '@/assets/logo.png';

// --- 您原有的 Favicon 代码 (保持不变) ---
onMounted(() => {
  let link = document.querySelector("link[rel~='icon']");
  if (!link) {
    link = document.createElement('link');
    link.rel = 'icon';
    document.getElementsByTagName('head')[0].appendChild(link);
  }
  link.href = logoUrl;
});
// --- Favicon 代码结束 ---


// --- [新增] 汉堡菜单逻辑 ---
// 控制移动端菜单是否打开
const isMobileMenuOpen = ref(false);

// 在移动端点击菜单项后，自动关闭菜单
const handleMenuSelect = () => {
  // 通过检查窗口宽度，确保此逻辑只在移动端生效
  if (window.innerWidth <= 768) {
    isMobileMenuOpen.value = false;
  }
};
// --- 汉堡菜单逻辑结束 ---
</script>

<!-- [新增] scoped CSS, 防止污染全局 -->
<style scoped>
.app-header {
  display: none; /* 默认不显示，只在移动端通过全局 CSS 显示 */
}
</style>