<template>
  <div class="s-page"><div class="s-page-heading"><div><p class="s-eyebrow">DATASETS / YOUR DATA FOUNDATION</p><h1>每一份数据，都有来处。</h1><p>管理源数据、生成资产与实验记录，从这里开始下一次探索。</p></div><button class="s-button primary" :disabled="busy || !studio.connected" @click="fileInput.click()"><el-icon><Upload /></el-icon>{{ busy ? '正在导入…' : '导入 CSV' }}</button><input ref="fileInput" type="file" accept=".csv,text/csv" hidden @change="upload" /></div>
    <div class="s-import-grid"><button class="s-upload-zone" :disabled="busy || !studio.connected" @click="fileInput.click()" @dragover.prevent @drop.prevent="drop"><el-icon><UploadFilled /></el-icon><strong>拖入 CSV，开始理解数据</strong><span>UTF-8 · 最多 10 MB · 1–16 个数值变量</span><small>支持时间列自动识别；单一实体的连续序列</small></button><div class="s-demo-options"><span class="s-eyebrow">START WITH A DATASET</span><button v-for="demo in studio.demos" :key="demo.id" :disabled="busy" @click="addDemo(demo.id)"><span class="s-demo-icon"><el-icon><component :is="demo.id === 'energy' ? Lightning : Cpu" /></el-icon></span><span><strong>{{ demo.name }}</strong><small>{{ number(demo.rows) }} 行 · {{ demo.channels }} 变量 · 模拟示例</small></span><span>＋</span></button><p v-if="!studio.connected" class="s-muted">连接鼠先知引擎后，可载入示例。</p></div></div>
    <div class="s-section-heading"><h2>数据资产 <span class="s-count">{{ studio.datasets.length }}</span></h2><input v-model="search" class="s-search" aria-label="搜索数据集" placeholder="搜索数据集…" /></div>
    <div v-if="!filtered.length" class="s-panel s-empty"><el-icon><Coin /></el-icon><h3>{{ search ? '没有匹配的数据集' : '数据工作区已就绪' }}</h3><p>{{ search ? '尝试其他关键词。' : '上传自己的数据，或选择一个内置示例。' }}</p></div>
    <div v-else class="s-table-wrap"><table class="s-table"><thead><tr><th>数据集</th><th>来源</th><th>规模</th><th>采样间隔</th><th>创建时间</th><th></th></tr></thead><tbody><tr v-for="dataset in filtered" :key="dataset.id" :class="{ selected: dataset.id === studio.selectedId }"><td><button class="s-table-name" @click="studio.select(dataset.id)"><el-icon><Coin /></el-icon><span>{{ dataset.name }}<small>{{ dataset.source_sha256.slice(0, 12) }} · v1</small></span></button></td><td><span class="s-status" :class="dataset.source === 'user_upload' ? 'completed' : 'planned'">{{ dataset.source === 'user_upload' ? '用户上传' : '模拟示例' }}</span></td><td>{{ number(dataset.rows) }} 行<small>{{ dataset.columns.length }} 变量</small></td><td>{{ dataset.sampling }}</td><td>{{ date(dataset.created) }}</td><td><button class="s-button small" @click="explore(dataset.id)">探索 →</button></td></tr></tbody></table></div>
    <section v-if="studio.selected" class="s-panel"><div class="s-section-heading"><div><span class="s-eyebrow">DATA PROFILE</span><h2>{{ studio.selected.name }}</h2></div><span class="s-pill">缺失率 {{ percent(studio.selected.missing_ratio) }}</span></div><StudioChart :option="preview" :height="260" /><div class="s-info-note"><el-icon><InfoFilled /></el-icon><div><p v-for="note in studio.selected.warnings" :key="note">{{ note }}</p></div></div><div class="s-table-wrap"><table class="s-table"><thead><tr><th>变量</th><th>均值</th><th>标准差</th><th>最小值</th><th>最大值</th><th>缺失</th></tr></thead><tbody><tr v-for="column in studio.selected.statistics" :key="column.name"><td>{{ column.name }}</td><td>{{ number(column.mean) }}</td><td>{{ number(column.std) }}</td><td>{{ number(column.min) }}</td><td>{{ number(column.max) }}</td><td>{{ column.missing }}</td></tr></tbody></table></div></section>
    <section class="s-panel"><div class="s-section-heading"><h2>实验与生成资产</h2><span>配置、来源和结果一起保存</span></div><div v-if="!studio.jobs.length" class="s-empty compact"><p>结构发现与生成任务完成后，会显示在这里。</p></div><div v-else class="s-table-wrap"><table class="s-table"><thead><tr><th>实验</th><th>源数据</th><th>状态</th><th>时间</th><th></th></tr></thead><tbody><tr v-for="job in studio.jobs" :key="job.id"><td>{{ job.kind === 'discover' ? '结构发现' : '合成数据集' }}<small>{{ job.id.slice(0, 8) }} · seed {{ job.config.seed }}</small></td><td>{{ studio.datasets.find(d => d.id === job.config.dataset_id)?.name || '—' }}</td><td><span :class="['s-status', job.status]">{{ status[job.status] }}</span></td><td>{{ date(job.created) }}</td><td><div class="s-actions"><button class="s-button small" @click="openJob(job)">查看</button><button v-if="job.kind === 'generate' && job.status === 'completed'" class="s-button small" @click="studio.download(job.id)">导出</button></div></td></tr></tbody></table></div></section>
  </div>
</template>
<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { Upload, UploadFilled, Lightning, Cpu, Coin, InfoFilled } from '@element-plus/icons-vue'
import { useStudioStore } from '../../stores/studio'
import StudioChart from '../../components/studio/StudioChart.vue'
import { lines, number, percent, date } from '../../components/studio/chartOptions'
const studio = useStudioStore(), router = useRouter(), fileInput = ref(null), busy = ref(false), search = ref('')
const status = { completed: '已完成', failed: '失败', queued: '等待中', running: '运行中' }
const filtered = computed(() => studio.datasets.filter(d => d.name.toLowerCase().includes(search.value.toLowerCase())))
const preview = computed(() => lines((studio.selected?.columns || []).map((name, i) => ({ name, data: studio.selected.preview.map(row => row.values[i]) })), studio.selected?.preview.map(row => row.index)))
async function addDemo(id) { busy.value = true; try { await studio.addDemo(id) } catch { /* banner */ } finally { busy.value = false } }
async function accept(file) {
  if (!file || busy.value) return
  if (!file.name.toLowerCase().endsWith('.csv') || file.size > 10 * 1024 * 1024) { studio.error = '请选择不超过 10 MB 的 CSV 文件'; return }
  busy.value = true
  try { await studio.upload(file) } catch { /* banner */ } finally { busy.value = false; if (fileInput.value) fileInput.value.value = '' }
}
const upload = event => accept(event.target.files[0])
const drop = event => accept(event.dataTransfer.files[0])
function explore(id) { studio.select(id); router.push('/discover') }
function openJob(job) { studio.openJob(job); router.push(job.kind === 'discover' ? '/discover' : '/evaluate') }
</script>
