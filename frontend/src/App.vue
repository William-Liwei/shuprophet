<template>
  <div class="studio-shell">
    <a href="#main-content" class="s-skip">跳到主要内容</a>
    <button v-if="menuOpen" class="s-backdrop" aria-label="关闭导航" @click="menuOpen = false"></button>
    <aside :class="['s-sidebar', { open: menuOpen }]">
      <RouterLink to="/" class="s-brand" @click="menuOpen = false"><span class="s-brand-icon"><svg viewBox="0 0 32 32" aria-hidden="true"><path d="M3 17h5l3-8 5 17 5-21 3 12h5" /></svg></span><span>ShuProphet<small>鼠先知 · DATA STUDIO</small></span></RouterLink>
      <div class="s-workspace"><span class="s-workspace-symbol">W</span><span>Research workspace<small>数据智能工作区</small></span><el-icon><Lock /></el-icon></div>
      <span class="s-nav-label">WORKSPACE</span>
      <nav aria-label="主要导航"><RouterLink v-for="item in primary" :key="item.path" :to="item.path" :class="{ active: route.path === item.path }" @click="menuOpen = false"><el-icon><component :is="item.icon" /></el-icon><span>{{ item.name }}</span><small>{{ item.en }}</small></RouterLink></nav>
      <span class="s-nav-label s-nav-label-secondary">RESEARCH & VISION</span>
      <nav aria-label="研究与产品"><RouterLink to="/research" :class="{ active: route.path === '/research' }" @click="menuOpen = false"><el-icon><Cpu /></el-icon><span>科研与产品愿景</span><span class="s-small-count">2</span></RouterLink><RouterLink to="/algorithms" :class="{ active: route.path === '/algorithms' }" @click="menuOpen = false"><el-icon><Reading /></el-icon><span>研究文库</span></RouterLink><RouterLink to="/tools" :class="{ active: route.path === '/tools' }" @click="menuOpen = false"><el-icon><TrendCharts /></el-icon><span>下游预测工具</span></RouterLink><a href="https://weili.space" target="_blank" rel="noopener noreferrer"><el-icon><Link /></el-icon><span>Wei Li · 个人主页</span><span>↗</span></a></nav>
      <div class="s-sidebar-bottom"><div class="s-local-state"><span :class="['s-dot', { offline: !studio.connected }]"></span>{{ studio.connected ? '鼠先知引擎已连接' : '等待引擎连接' }}<button aria-label="连接设置" @click="settings = true"><el-icon><Setting /></el-icon></button></div><small>可复现的实验，可追溯的数据。</small><div class="s-version">SHUPROPHET <span>DATA STUDIO / MVP</span></div></div>
    </aside>
    <div class="s-body"><header class="s-topbar"><button class="s-menu-toggle s-icon-btn" aria-label="展开导航" @click="menuOpen = !menuOpen"><el-icon><Menu /></el-icon></button><div class="s-breadcrumb">Workspace <span>/</span><strong>{{ route.meta.title || 'Data Studio' }}</strong></div><div class="s-top-actions"><span class="s-pill">RESEARCH PREVIEW</span><span v-if="studio.pending.length" class="s-pending-label">{{ studio.pending.length }} 个计算任务</span><button class="s-icon-btn" aria-label="刷新工作区" :disabled="studio.loading" @click="studio.refresh"><el-icon><Refresh /></el-icon></button><span class="s-avatar">WL</span></div></header>
      <main id="main-content" class="s-main" tabindex="-1"><div v-if="studio.error" class="s-error" role="alert"><span>{{ studio.error }}</span><button v-if="studio.authRequired" class="s-button small" @click="settings = true">连接设置</button><button v-else class="s-button small" @click="studio.refresh">重试连接</button><button class="s-icon-btn" aria-label="关闭错误提示" @click="studio.error = ''">×</button></div><RouterView /></main>
      <footer class="s-footer"><span>SHUPROPHET / TIME SERIES DATA INTELLIGENCE</span><span>Understand. Create. Validate.</span></footer>
    </div>
    <el-dialog v-model="settings" title="工作区连接" width="min(440px, 92vw)"><p class="s-muted">需要访问令牌的工作区，请在此输入。令牌仅保存在当前浏览器会话中。</p><label class="s-field">工作区访问令牌<input v-model="accessToken" type="password" autocomplete="off" placeholder="输入访问令牌" @keyup.enter="connect" /></label><template #footer><button class="s-button primary" @click="connect">保存并连接</button></template></el-dialog>
  </div>
</template>
<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { House, Coin, Aim, MagicStick, CircleCheck, ChatDotRound, Cpu, Reading, TrendCharts, Link, Lock, Setting, Menu, Refresh } from '@element-plus/icons-vue'
import { useStudioStore } from './stores/studio'
const route = useRoute(), studio = useStudioStore()
const menuOpen = ref(false), settings = ref(false), accessToken = ref(sessionStorage.getItem('studio-access-token') || '')
const primary = [{ path: '/', name: '工作台', en: 'Overview', icon: House }, { path: '/datasets', name: '数据集', en: 'Datasets', icon: Coin }, { path: '/discover', name: '结构发现', en: 'Discover', icon: Aim }, { path: '/generate', name: '数据生成', en: 'Generate', icon: MagicStick }, { path: '/evaluate', name: '质量评估', en: 'Evaluate', icon: CircleCheck }]
primary.push({ path: '/assistant', name: '交互助手', en: 'Assistant', icon: ChatDotRound })
async function connect() { sessionStorage.setItem('studio-access-token', accessToken.value.trim()); settings.value = false; await studio.refresh() }
onMounted(() => { studio.refresh(); studio.startPolling() })
onUnmounted(studio.stopPolling)
</script>
