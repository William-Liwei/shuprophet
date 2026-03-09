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
        <el-menu-item index="/agent">
          <el-icon><MagicStick /></el-icon>
          <span>智能助理</span>
        </el-menu-item>
        <el-menu-item index="/app">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据探索</span>
        </el-menu-item>
        <el-menu-item index="/algorithms">
          <el-icon><Cpu /></el-icon>
          <span>算法文库</span>
        </el-menu-item>
        <el-menu-item index="/solutions">
          <el-icon><Briefcase /></el-icon>
          <span>解决方案</span>
        </el-menu-item>
        <el-menu-item index="/about">
          <el-icon><InfoFilled /></el-icon>
          <span>关于项目</span>
        </el-menu-item>
        <el-menu-item index="/community">
          <el-icon><ChatDotRound /></el-icon>
          <span>社区广场</span>
        </el-menu-item>
      </el-menu>

      <!-- 用户信息区 -->
      <div class="sidebar-user">
        <template v-if="isLoggedIn">
          <div class="user-info" @click="$router.push('/profile')">
            <img :src="user?.avatar_url || '/api/user/avatars/default.png'" class="sidebar-avatar" />
            <span class="sidebar-nickname">{{ user?.nickname || user?.username }}</span>
          </div>
          <el-button size="small" text style="color:#6e6e73" @click="handleLogout">退出</el-button>
        </template>
        <template v-else>
          <el-button size="small" type="primary" @click="$router.push('/login')">登录</el-button>
          <el-button size="small" @click="$router.push('/register')">注册</el-button>
        </template>
      </div>
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
            <keep-alive include="AgentView">
              <component :is="Component" />
            </keep-alive>
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
import { onMounted, ref, computed } from 'vue';
import { Menu, TrendCharts, House, DataAnalysis, Cpu, InfoFilled, ChatDotRound, Briefcase } from '@element-plus/icons-vue';
import { useAuthStore } from '@/stores/auth';
import logoUrl from '@/assets/logo.png';

const auth = useAuthStore();
const isLoggedIn = computed(() => auth.isLoggedIn);
const user = computed(() => auth.user);

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

const handleLogout = () => {
  auth.logout();
  window.location.reload();
};
</script>

<!-- [新增] scoped CSS, 防止污染全局 -->
<style scoped>
.app-header {
  display: none;
}
.sidebar-user {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 16px;
  border-top: 1px solid rgba(0,0,0,0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  flex: 1;
  min-width: 0;
}
.sidebar-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  object-fit: cover;
}
.sidebar-nickname {
  color: #1d1d1f;
  font-size: 13px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>