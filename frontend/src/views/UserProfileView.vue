<template>
  <div class="user-profile-page">
    <div v-if="loading" v-loading="true" style="min-height: 300px;"></div>
    <div v-else-if="user" class="module-card">
      <div class="profile-header">
        <img :src="user.avatar_url || '/api/user/avatars/default.png'" class="user-avatar" />
        <div class="user-info">
          <h2 class="user-nickname">{{ user.nickname || user.username }}</h2>
          <div class="user-meta">
            <span class="level-badge">Lv.{{ user.level }}</span>
            <span class="post-count">{{ user.post_count }} 篇帖子</span>
          </div>
          <p v-if="user.bio" class="user-bio">{{ user.bio }}</p>
        </div>
      </div>

      <div class="posts-section">
        <h3 class="section-title">TA的帖子</h3>
        <div v-if="user.posts?.length" class="post-list">
          <div v-for="post in user.posts" :key="post.id" class="post-item" @click="goToPost(post.id)">
            <div class="post-content">{{ post.content }}</div>
            <div class="post-meta">
              <span>❤️ {{ post.like_count }}</span>
              <span>💬 {{ post.comment_count }}</span>
              <span class="post-time">{{ formatTime(post.created_at) }}</span>
            </div>
          </div>
        </div>
        <div v-else class="empty-hint">暂无帖子</div>
      </div>
    </div>
    <div v-else class="empty-hint">用户不存在</div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import request from '@/utils/request'

const route = useRoute()
const router = useRouter()
const user = ref(null)
const loading = ref(true)

onMounted(async () => {
  const userId = route.params.id
  try {
    const res = await request.get(`/user/${userId}`)
    user.value = res.data.user
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
})

const goToPost = (postId) => {
  router.push(`/community?post=${postId}`)
}

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  return `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`
}
</script>

<style scoped>
.profile-header {
  display: flex;
  gap: 24px;
  align-items: flex-start;
  margin-bottom: 32px;
}
.user-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #e5e7eb;
}
.user-info {
  flex: 1;
}
.user-nickname {
  font-size: 1.5rem;
  font-weight: 600;
  color: #1d1d1f;
  margin: 0 0 8px 0;
}
.user-meta {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 8px;
}
.level-badge {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2px 10px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
}
.post-count {
  color: #6e6e73;
  font-size: 14px;
}
.user-bio {
  color: #6e6e73;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
}
.section-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 16px;
}
.post-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.post-item {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 12px;
  cursor: pointer;
  transition: background 0.2s;
}
.post-item:hover {
  background: #e8edf3;
}
.post-content {
  font-size: 14px;
  color: #1d1d1f;
  margin-bottom: 8px;
  line-height: 1.6;
}
.post-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6e6e73;
}
.post-time {
  margin-left: auto;
}
.empty-hint {
  text-align: center;
  color: #9ca3af;
  padding: 40px 0;
}
</style>
