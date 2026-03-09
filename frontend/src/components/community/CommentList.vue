<template>
  <div class="comment-list">
    <h4 class="comment-title">评论 ({{ comments.length }})</h4>
    <div v-if="showInput" class="comment-input">
      <el-input
        v-model="newComment"
        placeholder="写评论..."
        maxlength="500"
        @keyup.enter="submit"
      />
      <el-button type="primary" size="small" :disabled="!newComment.trim()" @click="submit">
        发送
      </el-button>
    </div>
    <div v-for="c in comments" :key="c.id" class="comment-item">
      <UserAvatar :src="c.author?.avatar_url" :size="28" class="clickable-avatar" @click="goToUser(c.author?.id)" />
      <div class="comment-body">
        <span class="comment-author">{{ c.author?.nickname || '匿名' }}</span>
        <span class="comment-text">{{ c.content }}</span>
        <div class="comment-meta">
          <span class="comment-time">{{ formatTime(c.created_at) }}</span>
          <span
            v-if="c.author?.id === currentUserId || isAdmin"
            class="comment-delete"
            @click="$emit('delete-comment', c.id)"
          >删除</span>
        </div>
      </div>
    </div>
    <div v-if="!comments.length" class="no-comments">暂无评论</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import UserAvatar from '@/components/UserAvatar.vue'

const router = useRouter()

defineProps({
  comments: { type: Array, default: () => [] },
  showInput: { type: Boolean, default: true },
  currentUserId: { type: Number, default: null },
  isAdmin: { type: Boolean, default: false }
})

const emit = defineEmits(['add-comment', 'delete-comment'])
const newComment = ref('')

const submit = () => {
  if (!newComment.value.trim()) return
  emit('add-comment', newComment.value.trim())
  newComment.value = ''
}

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
.comment-title {
  font-size: 14px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}
.comment-input {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
}
.comment-item {
  display: flex;
  gap: 10px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
}
.comment-item:last-child { border-bottom: none; }
.comment-body { flex: 1; }
.comment-author {
  font-weight: 600;
  font-size: 13px;
  color: #1d1d1f;
  margin-right: 8px;
}
.comment-text {
  font-size: 14px;
  color: #374151;
}
.comment-meta {
  display: flex;
  gap: 12px;
  margin-top: 4px;
  font-size: 12px;
  color: #9ca3af;
}
.comment-delete {
  cursor: pointer;
  color: #ef4444;
}
.no-comments {
  text-align: center;
  color: #9ca3af;
  padding: 20px 0;
  font-size: 14px;
}
.clickable-avatar {
  cursor: pointer;
  transition: opacity 0.2s;
}
.clickable-avatar:hover {
  opacity: 0.7;
}
</style>
