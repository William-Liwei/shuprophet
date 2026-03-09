<template>
  <div class="community-page">
    <div class="page-header">
      <h1 class="page-title">社区广场</h1>
      <el-radio-group v-model="sortType" @change="fetchPosts">
        <el-radio-button value="latest">最新</el-radio-button>
        <el-radio-button value="hot">热门</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 帖子详情弹窗 -->
    <el-dialog v-model="showDetail" title="帖子详情" width="600px" destroy-on-close>
      <div v-if="detailPost">
        <div class="detail-header">
          <UserAvatar :src="detailPost.author?.avatar_url" :size="40" />
          <div class="detail-meta">
            <span class="detail-author">{{ detailPost.author?.nickname }}</span>
            <span class="detail-time">{{ detailPost.created_at }}</span>
          </div>
        </div>
        <div class="detail-content">{{ detailPost.content }}</div>
        <SharedConversation v-if="detailPost.conversation" :conversation="detailPost.conversation" />
        <CommentList
          :comments="detailPost.comments || []"
          :show-input="isLoggedIn"
          :current-user-id="currentUserId"
          :is-admin="isAdmin"
          @add-comment="addComment"
          @delete-comment="deleteComment"
        />
      </div>
    </el-dialog>

    <!-- 发帖区 -->
    <PostComposer v-if="isLoggedIn" ref="composerRef" @posted="createPost" />
    <div v-else class="login-hint">
      <router-link to="/login">登录</router-link> 后参与社区讨论
    </div>

    <!-- 帖子列表 -->
    <div v-loading="loading">
      <PostCard
        v-for="p in posts"
        :key="p.id"
        :post="p"
        :liked="likedSet.has(p.id)"
        :can-delete="p.author?.id === currentUserId || isAdmin"
        @click="openDetail(p.id)"
        @like="toggleLike(p)"
        @delete="deletePost(p.id)"
      />
      <div v-if="!posts.length && !loading" class="empty-hint">还没有帖子，来发第一条吧</div>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="pagination-wrap">
      <el-pagination
        layout="prev, pager, next"
        :total="total"
        :page-size="20"
        :current-page="page"
        @current-change="changePage"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'
import UserAvatar from '@/components/UserAvatar.vue'
import PostCard from '@/components/community/PostCard.vue'
import PostComposer from '@/components/community/PostComposer.vue'
import CommentList from '@/components/community/CommentList.vue'
import SharedConversation from '@/components/community/SharedConversation.vue'

const auth = useAuthStore()
const isLoggedIn = computed(() => auth.isLoggedIn)
const currentUserId = computed(() => auth.user?.id)
const isAdmin = computed(() => auth.user?.is_admin)

const posts = ref([])
const loading = ref(false)
const page = ref(1)
const total = ref(0)
const totalPages = ref(0)
const likedSet = reactive(new Set())
const composerRef = ref(null)
const sortType = ref('latest')

const showDetail = ref(false)
const detailPost = ref(null)

onMounted(() => fetchPosts())

const fetchPosts = async () => {
  loading.value = true
  try {
    const res = await request.get('/community/posts', {
      params: { page: page.value, sort: sortType.value }
    })
    posts.value = res.data.posts
    total.value = res.data.total
    totalPages.value = res.data.pages
  } catch {
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

const changePage = (p) => {
  page.value = p
  fetchPosts()
}

const createPost = async (content) => {
  try {
    await request.post('/community/posts', { content })
    composerRef.value?.reset()
    ElMessage.success('发布成功')
    fetchPosts()
  } catch {
    ElMessage.error('发布失败')
    composerRef.value?.reset()
  }
}

const toggleLike = async (post) => {
  if (!isLoggedIn.value) {
    ElMessage.warning('请先登录')
    return
  }
  try {
    const res = await request.post(`/community/posts/${post.id}/like`)
    post.like_count = res.data.like_count
    if (res.data.liked) {
      likedSet.add(post.id)
    } else {
      likedSet.delete(post.id)
    }
  } catch {
    ElMessage.error('操作失败')
  }
}

const deletePost = async (id) => {
  try {
    await ElMessageBox.confirm('确定删除这条帖子？', '提示')
    await request.delete(`/community/posts/${id}`)
    ElMessage.success('已删除')
    fetchPosts()
  } catch { /* cancelled or error */ }
}

const openDetail = async (id) => {
  try {
    const res = await request.get(`/community/posts/${id}`)
    detailPost.value = res.data.post
    showDetail.value = true
  } catch {
    ElMessage.error('加载失败')
  }
}

const addComment = async (content) => {
  if (!detailPost.value) return
  try {
    const res = await request.post(
      `/community/posts/${detailPost.value.id}/comments`,
      { content }
    )
    detailPost.value.comments.push(res.data.comment)
    // 更新列表中的评论数
    const p = posts.value.find(x => x.id === detailPost.value.id)
    if (p) p.comment_count = (p.comment_count || 0) + 1
  } catch {
    ElMessage.error('评论失败')
  }
}

const deleteComment = async (commentId) => {
  try {
    await request.delete(`/community/comments/${commentId}`)
    detailPost.value.comments = detailPost.value.comments.filter(c => c.id !== commentId)
    const p = posts.value.find(x => x.id === detailPost.value.id)
    if (p) p.comment_count = Math.max(0, (p.comment_count || 1) - 1)
  } catch {
    ElMessage.error('删除失败')
  }
}
</script>

<style scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.login-hint {
  text-align: center;
  padding: 20px;
  color: #6e6e73;
  font-size: 15px;
  background: rgba(255,255,255,0.6);
  border-radius: 16px;
  margin-bottom: 20px;
}
.login-hint a { color: #0071e3; }
.empty-hint {
  text-align: center;
  color: #9ca3af;
  padding: 40px 0;
}
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}
.detail-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}
.detail-meta {
  display: flex;
  flex-direction: column;
}
.detail-author {
  font-weight: 600;
  font-size: 15px;
  color: #1d1d1f;
}
.detail-time {
  font-size: 12px;
  color: #9ca3af;
}
.detail-content {
  font-size: 15px;
  line-height: 1.7;
  color: #1d1d1f;
  margin-bottom: 16px;
  white-space: pre-wrap;
  word-break: break-word;
}
</style>
