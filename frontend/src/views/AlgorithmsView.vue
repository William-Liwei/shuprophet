<template>
  <div class="algorithms-page">
    <h1 class="page-title">{{ $route.meta.title }}</h1>

    <div class="library-summary">
      <strong>9项时序研究成果</strong>
      <span>覆盖聚类、生成、预测与不确定性建模</span>
    </div>

    <el-tabs v-model="activePublication" type="border-card" class="algorithm-tabs">
      <el-tab-pane
        v-for="paper in publications"
        :key="paper.id"
        :label="paper.name"
        :name="paper.id"
      >
        <article class="publication-content">
          <header class="publication-header">
            <div class="publication-badges">
              <el-tag
                v-for="badge in paper.badges"
                :key="badge"
                :type="badgeType(badge)"
                effect="plain"
                size="small"
              >
                {{ badge }}
              </el-tag>
            </div>
            <h2>{{ paper.title }}</h2>
            <p class="venue">{{ paper.venue }}</p>
            <p class="authors">{{ paper.authors }}</p>
          </header>

          <el-row :gutter="30">
            <el-col :xs="24" :md="14" class="details-column">
              <h3><el-icon><Tickets /></el-icon> 核心内容</h3>
              <p>{{ paper.abstractZh }}</p>

              <h3><el-icon><Operation /></el-icon> 研究要点</h3>
              <ul>
                <li v-for="highlight in paper.highlights" :key="highlight">{{ highlight }}</li>
              </ul>

              <h3><el-icon><Link /></el-icon> 成果链接</h3>
              <div v-if="paper.links.length" class="links">
                <el-button
                  v-for="link in paper.links"
                  :key="link.url"
                  :type="link.type === 'github' ? 'success' : 'primary'"
                  plain
                  @click="openLink(link.url)"
                >
                  <el-icon>
                    <Share v-if="link.type === 'github'" />
                    <Document v-else />
                  </el-icon>
                  {{ link.label }}
                </el-button>
              </div>
              <p v-else class="link-empty">公开链接尚未收录</p>

              <div class="citation-section">
                <h3><el-icon><DocumentCopy /></el-icon> 学术引用</h3>
                <el-button @click="showBibtex(paper)">
                  <el-icon><DocumentCopy /></el-icon>
                  查看 BibTeX
                </el-button>
              </div>
            </el-col>

            <el-col :xs="24" :md="10">
              <h3><el-icon><PictureRounded /></el-icon> 论文概览图</h3>
              <el-image
                :src="paper.imageUrl"
                :alt="`${paper.name} overview`"
                fit="contain"
                class="architecture-image"
              >
                <template #error>
                  <div class="image-slot">
                    <el-icon><Picture /></el-icon>
                    <p>概览图暂不可用</p>
                  </div>
                </template>
              </el-image>
            </el-col>
          </el-row>
        </article>
      </el-tab-pane>
    </el-tabs>

    <el-dialog
      v-model="dialogVisible"
      :title="`${currentPaperName} 的 BibTeX 引用`"
      width="min(680px, 90vw)"
      append-to-body
    >
      <div class="bibtex-container">
        <pre><code>{{ currentBibtex }}</code></pre>
      </div>
      <template #footer>
        <el-button type="primary" @click="dialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { publications } from '@/data/publications'

const activePublication = ref(publications[0].id)
const dialogVisible = ref(false)
const currentBibtex = ref('')
const currentPaperName = ref('')

const badgeType = (badge) => {
  if (badge === 'CCF-A') return 'danger'
  if (badge === 'CCF-B' || badge === 'Full Paper') return 'warning'
  if (badge === 'CCF-C' || badge === 'Oral') return 'success'
  return 'info'
}

const openLink = (url) => {
  window.open(url, '_blank', 'noopener,noreferrer')
}

const showBibtex = (paper) => {
  currentPaperName.value = paper.name
  currentBibtex.value = paper.bibtex
  dialogVisible.value = true
}
</script>

<style scoped>
.algorithms-page {
  max-width: 1200px;
  margin: 0 auto;
}

.library-summary {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
  color: #6e6e73;
}

.library-summary strong {
  color: #1d1d1f;
  font-size: 1.05rem;
}

.algorithm-tabs {
  border: none;
  background-color: transparent;
}

:deep(.el-tabs__header) {
  background-color: rgba(255, 255, 255, 0.8);
  border-bottom: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 8px 8px 0 0;
}

:deep(.el-tabs__item) {
  color: #6e6e73;
  font-weight: 500;
}

:deep(.el-tabs__item:hover),
:deep(.el-tabs__item.is-active) {
  color: #0071e3 !important;
}

:deep(.el-tabs__item.is-active) {
  background-color: rgba(0, 113, 227, 0.08) !important;
}

:deep(.el-tabs__content) {
  padding: 32px;
  background: rgba(255, 255, 255, 0.82);
  border-radius: 0 0 8px 8px;
}

.publication-header {
  padding-bottom: 24px;
  margin-bottom: 28px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
}

.publication-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.publication-header h2 {
  max-width: 920px;
  margin: 0 0 12px;
  color: #1d1d1f;
  font-size: 1.55rem;
  line-height: 1.35;
  overflow-wrap: anywhere;
}

.venue,
.authors {
  margin: 5px 0;
  color: #6e6e73;
  line-height: 1.55;
}

.authors {
  font-size: 0.92rem;
}

.publication-content h3 {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1d1d1f;
  font-size: 1.05rem;
  font-weight: 600;
  margin: 0 0 12px;
}

.details-column > h3:not(:first-child) {
  margin-top: 28px;
}

.publication-content p,
.publication-content li {
  color: #3a3a3c;
  font-size: 0.98rem;
  line-height: 1.75;
}

.publication-content ul {
  padding-left: 20px;
  margin-bottom: 0;
}

.links {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.link-empty {
  color: #86868b !important;
  margin: 0;
}

.citation-section {
  margin-top: 28px;
  padding-top: 22px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
}

.architecture-image {
  width: 100%;
  height: 320px;
  background-color: #f5f5f7;
  border: 1px solid rgba(0, 0, 0, 0.06);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.image-slot {
  text-align: center;
  color: #86868b;
}

.image-slot .el-icon {
  font-size: 40px;
}

.bibtex-container {
  padding: 16px;
  overflow-x: auto;
  background-color: #f5f5f7;
  border-radius: 8px;
}

pre {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

code {
  color: #1d1d1f;
  font-family: 'Courier New', Courier, monospace;
  font-size: 0.88rem;
}

@media (max-width: 767px) {
  .library-summary {
    align-items: flex-start;
    flex-direction: column;
  }

  :deep(.el-tabs__content) {
    padding: 20px 16px;
  }

  .publication-header h2 {
    font-size: 1.25rem;
  }

  .architecture-image {
    height: 240px;
    margin-top: 4px;
  }
}
</style>
