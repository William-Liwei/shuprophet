<template>
  <div class="home-view">
    
    <!-- 1. 直接在这里添加图片 -->
    <img src="@/assets/logo.png" alt="Project Logo" class="home-logo">

    <h1>鼠先知 SHU Prophet 平台</h1>
    <p class="subtitle">新一代时序智能预测与决策平台</p>
    <p class="subtitle">作者：Wei Li</p>
    <el-button type="primary" size="large" @click="$router.push('/app')" round>
      进入核心功能 <el-icon class="el-icon--right"><ArrowRight /></el-icon>
    </el-button>
    
  </div>
</template>

<script setup>
// Script 区域现在是空的，因为我们直接在模板中引用图片
</script>

<style scoped>
.home-view { 
  text-align: center; 
  padding-top: 10vh; 
}

/* 2. 为图片添加一点样式 */
.home-logo {
  width: 480px;       /* 固定图片宽度 */
  margin-bottom: -1.5rem; /* 图片和标题之间的距离 */
}

/* --- 下面的样式保持不变 --- */
.home-view h1 {
  font-size: 3.5rem;
  font-weight: 800;
  background: linear-gradient(45deg, #38bdf8, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 1rem;
}

.home-view .subtitle {
  font-size: 1.25rem;
  color: #94a3b8;
  margin-bottom: 2.5rem;
}
</style>