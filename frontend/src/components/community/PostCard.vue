<template>
  <div class="post-card" @click="$emit('click')">
    <div class="post-header">
      <UserAvatar :src="post.author?.avatar_url" :size="36" class="clickable-avatar" @click.stop="goToUser(post.author?.id)" />
      <div class="post-meta">
        <span class="post-author">{{ post.author?.nickname || '匿名' }}</span>
        <span class="post-time">{{ formatTime(post.created_at) }}</span>
      </div>
      <el-button
        v-if="canDelete"
        type="danger"
        size="small"
        text
        @click.stop="$emit('delete')"
      >删除</el-button>
    </div>
    <div class="post-content">{{ post.content }}</div>
    <div v-if="post.has_conversation" class="post-tag">
      <el-tag size="small" type="success">AI对话</el-tag>
    </div>
    <div class="post-actions">
      <span class="action-item" @click.stop="$emit('like')">
        {{ liked ? '❤️' : '🤍' }} {{ post.like_count || 0 }}
      </span>
      <span class="action-item">
        💬 {{ post.comment_count || 0 }}
      </span>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import UserAvatar from '@/components/UserAvatar.vue'

const router = useRouter()

defineProps({
  post: { type: Object, required: true },
  liked: { type: Boolean, default: false },
  canDelete: { type: Boolean, default: false }
})

defineEmits(['click', 'like', 'delete'])

const goToUser = (userId) => {
  if (userId) router.push(`/user/${userId}`)
}

const formatTime = (iso) => {
  if (!iso) return ''
  const d = new Date(iso)
  const now = new Date()
  const diff = (now - d) / 1000
  if (diff < 60) return '刚刚'
  if (diff < 3600) return Math.floor(diff / 60) + '分钟前'
  if (diff < 86400) return Math.floor(diff / 3600) + '小时前'
  return d.toLocaleDateString('zh-CN')
}
</script>

<style scoped>
.post-card {
  background: rgba(255,255,255,0.6);
  backdrop-filter: blur(20px);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid rgba(255,255,255,0.5);
  box-shadow: 0 4px 16px rgba(0,0,0,0.06);
  cursor: pointer;
  transition: all 0.2s;
}
.post-card:hover {
  box-shadow: 0 8px 24px rgba(0,0,0,0.1);
}
.post-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}
.post-meta {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.post-author { font-weight: 600; font-size: 14px; color: #1d1d1f; }
.post-time { font-size: 12px; color: #9ca3af; }
.post-content {
  font-size: 15px;
  line-height: 1.6;
  color: #1d1d1f;
  margin-bottom: 10px;
  white-space: pre-wrap;
  word-break: break-word;
}
.post-tag { margin-bottom: 10px; }
.post-actions {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #6e6e73;
}
.action-item {
  cursor: pointer;
  user-select: none;
  transition: color 0.2s;
}
.action-item:hover { color: #1d1d1f; }
.clickable-avatar {
  cursor: pointer;
  transition: opacity 0.2s;
}
.clickable-avatar:hover {
  opacity: 0.7;
}
</style>