<template>
  <div class="s-page s-assistant-page"><div class="s-page-heading"><div><p class="s-eyebrow">YOUR DATA, IN CONVERSATION</p><h1>关于数据，我们接着聊。</h1><p>结合工作区中的数据与实验，理解结果，找到下一步。</p></div><span class="s-engine-label"><span class="s-dot"></span>{{ studio.capabilities?.assistant?.configured ? 'LLM 对话已配置' : 'LLM 等待连接' }}</span></div><section class="s-chat-panel"><div class="s-chat-context"><el-icon><Coin /></el-icon><label>当前数据<select :value="studio.selectedId" @change="studio.select($event.target.value)"><option v-if="!studio.datasets.length" value="">尚未选择数据</option><option v-for="d in studio.datasets" :key="d.id" :value="d.id">{{ d.name }}</option></select></label><button class="s-icon-btn" aria-label="开始新对话" title="开始新对话" @click="clear"><el-icon><RefreshRight /></el-icon></button></div>
    <div ref="conversation" class="s-chat-messages" aria-live="polite" aria-relevant="additions"><div v-if="!messages.length" class="s-chat-welcome"><span class="s-chat-symbol"><el-icon><ChatDotRound /></el-icon></span><p class="s-eyebrow">SHUPROPHET ASSISTANT</p><h2>从一个问题，走向下一次发现。</h2><p>我可以帮助你理解数据画像、模式分布和质量报告，<br />也可以带你完成一次数据生成实验。</p><div class="s-chat-prompts"><button v-for="prompt in prompts" :key="prompt" :disabled="busy || !studio.connected" @click="send(prompt)">{{ prompt }} <span>↗</span></button></div></div><article v-for="(message, i) in messages" :key="i" :class="['s-chat-message', message.role]"><span class="s-message-avatar">{{ message.role === 'user' ? '你' : 'SHU' }}</span><div class="s-message-content"><div class="s-message-meta"><strong>{{ message.role === 'user' ? '你' : '鼠先知助手' }}</strong><small v-if="message.dataset">{{ message.dataset }}</small></div><p>{{ message.text }}</p><div v-if="message.evidence?.length" class="s-chat-evidence"><span v-for="item in message.evidence" :key="item.id">{{ item.label }} · {{ item.id.slice(0, 8) }}</span></div><div v-if="message.actions?.length" class="s-actions"><RouterLink v-for="action in message.actions" :key="action.to" :to="action.to" class="s-button small">{{ action.label }} →</RouterLink></div></div></article><div v-if="busy" class="s-chat-thinking" role="status"><span class="s-spinner"></span>模型正在结合工作区证据回答…</div></div>
    <form class="s-chat-composer" @submit.prevent="send()"><textarea v-model="input" aria-label="向鼠先知助手提问" placeholder="例如：这些数据有哪些模式？合成数据是否改善了下游表现？" maxlength="2000" rows="2" @keydown.enter.exact.prevent="send()"></textarea><div><span>LLM 对话 · 基于工作区证据</span><button class="s-button primary" type="submit" :disabled="busy || !input.trim() || !studio.connected"><el-icon><Promotion /></el-icon>发送</button></div></form></section><p class="s-chat-footnote">浏览器保留本次会话。问题、近期对话和实验摘要会发送至配置的模型服务；不发送原始数据窗口。切换数据后使用对应上下文，回答请结合实验来源核对。</p></div>
</template>
<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { ChatDotRound, Coin, Promotion, RefreshRight } from '@element-plus/icons-vue'
import { useStudioStore } from '../../stores/studio'
const studio = useStudioStore(), input = ref(''), busy = ref(false), conversation = ref(null)
const prompts = ['概览一下当前数据', '发现了哪些模式，下一步怎么做？', '质量报告说明了什么？', 'APCL 和 SDFlow 的研究价值是什么？']
let saved = []
try { const value = JSON.parse(sessionStorage.getItem('studio-llm-conversation-v1') || '[]'); saved = Array.isArray(value) ? value.slice(-40) : [] } catch { /* empty session */ }
const messages = ref(saved)
watch(messages, () => { try { sessionStorage.setItem('studio-llm-conversation-v1', JSON.stringify(messages.value.slice(-40))) } catch { /* browser storage unavailable */ } }, { deep: true })
async function scroll() { await nextTick(); if (conversation.value) conversation.value.scrollTop = messages.value.length || busy.value ? conversation.value.scrollHeight : 0 }
async function send(prompt) {
  const text = (typeof prompt === 'string' ? prompt : input.value).trim()
  if (!text || busy.value || !studio.connected) return
  const dataset = studio.selected?.name, datasetId = studio.selectedId || ''
  const history = messages.value.filter(m => m.datasetId === datasetId && !m.error).slice(-8).map(m => ({ role: m.role, content: m.text.slice(-4000) }))
  messages.value.push({ role: 'user', text, dataset, datasetId }); input.value = ''; busy.value = true
  await scroll()
  try { const response = await studio.ask(text, history); messages.value.push({ role: 'assistant', text: response.message, actions: response.actions, evidence: response.evidence, source: response.answer_source, dataset, datasetId }) }
  catch (err) { messages.value.push({ role: 'assistant', text: err.response?.data?.error || '暂时无法连接助手，请稍后重试。', error: true, dataset, datasetId }) }
  finally { busy.value = false; await scroll() }
}
function clear() { if (!busy.value) { messages.value = []; scroll() } }
onMounted(scroll)
</script>
