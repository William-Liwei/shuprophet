<template>
  <div class="module-card">
    <div class="agent-header">
      <h2 class="module-title">
        <el-icon><MagicStick /></el-icon>
        <span>智能助理 SHU Prophet</span>
      </h2>
      <div class="model-switcher" role="tablist" aria-label="智能助理模式切换">
        <button
          type="button"
          class="model-chip"
          :class="{ active: assistantMode === 'shu_hero' }"
          @click="switchAssistantMode('shu_hero')"
        >
          鼠先知
        </button>
        <button
          type="button"
          class="model-chip"
          :class="{ active: assistantMode === 'deepseek' }"
          @click="switchAssistantMode('deepseek')"
        >
          DeepSeek
        </button>
      </div>
    </div>

    <!-- 积分信息栏 -->
    <div class="credits-bar" v-if="creditsInfo">
      <span class="credits-item">
        今日免费: <b>{{ creditsInfo.free_remaining }}</b>/{{ creditsInfo.free_limit }}
      </span>
      <span class="credits-item">
        积分余额: <b>{{ creditsInfo.credits }}</b>
      </span>
      <el-button size="small" type="warning" plain @click="showRedeemDialog = true">兑换积分</el-button>
      <el-button size="small" plain @click="shareWebsite">分享赚积分</el-button>
    </div>

    <!-- 兑换码弹窗 -->
    <el-dialog v-model="showRedeemDialog" title="兑换积分" width="400px" destroy-on-close>
      <el-input v-model="redeemCode" placeholder="请输入兑换码" maxlength="64" clearable />
      <template #footer>
        <el-button @click="showRedeemDialog = false">取消</el-button>
        <el-button type="primary" :loading="redeeming" @click="doRedeem">兑换</el-button>
      </template>
    </el-dialog>

    <!-- 对话窗口 -->
    <div class="chat-window" ref="chatWindowRef">
      <!-- 消息历史 -->
      <div v-for="(msg, index) in messages" :key="index" class="message-container" :class="msg.sender">
        <div v-if="msg.sender === 'agent'" class="avatar-wrapper" @click="onAvatarClick(index, $event)" @mouseenter="msg.isHovering = true" @mouseleave="msg.isHovering = false">
          <div class="avatar avatar-3d" :class="{ 'is-thinking': isAgentTyping, 'is-blinking': isBlinking, 'is-combo': msg.showCombo, 'is-hovering': msg.isHovering }" :style="msg.showCombo ? {} : avatarTiltStyle">
            <svg viewBox="0 0 48 48" width="28" height="28">
              <circle cx="10" cy="16" r="8" fill="none" stroke="#1d1d1f" stroke-width="2"/>
              <circle cx="38" cy="16" r="8" fill="none" stroke="#1d1d1f" stroke-width="2"/>
              <circle cx="24" cy="26" r="11" fill="none" stroke="#1d1d1f" stroke-width="2"/>
              <circle cx="20" cy="24" :r="isBlinking ? 0.5 : 2" fill="#1d1d1f"/>
              <circle cx="28" cy="24" :r="isBlinking ? 0.5 : 2" fill="#1d1d1f"/>
              <path d="M 21 29 Q 24 31 27 29" fill="none" stroke="#1d1d1f" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M 14 28 L 9 27" stroke="#1d1d1f" stroke-width="1" stroke-linecap="round"/>
              <path d="M 14 30 L 9 31" stroke="#1d1d1f" stroke-width="1" stroke-linecap="round"/>
              <path d="M 34 28 L 39 27" stroke="#1d1d1f" stroke-width="1" stroke-linecap="round"/>
              <path d="M 34 30 L 39 31" stroke="#1d1d1f" stroke-width="1" stroke-linecap="round"/>
            </svg>
          </div>
          <div v-if="msg.showBubble" class="click-bubble">{{ msg.bubbleText }}</div>
        </div>
        <div class="message-bubble">
          <!-- 思考过程（可折叠） -->
          <div v-if="msg.thinking" class="thinking-section">
            <div class="thinking-header" @click="msg.thinkingExpanded = !msg.thinkingExpanded">
              <span class="thinking-icon">🧠</span>
              <span>思考过程（{{ msg.thinking.trajectory.length }}步）</span>
              <span class="thinking-toggle">{{ msg.thinkingExpanded ? '收起' : '展开' }}</span>
            </div>
            <div v-if="msg.thinkingExpanded" class="thinking-steps">
              <div v-for="step in msg.thinking.trajectory" :key="step.step" class="thinking-step">
                <div class="step-header">
                  <span class="step-num">{{ step.step }}</span>
                  <span class="step-tool">{{ step.tool }}</span>
                  <span class="step-time">{{ step.time }}s</span>
                </div>
                <div class="step-thought">{{ step.thought }}</div>
                <div class="step-result">{{ step.result }}</div>
              </div>
            </div>
          </div>
          <div v-html="renderMarkdown(msg.text)" class="markdown-content"></div>
          <!-- 单条消息分享按钮 -->
          <div v-if="msg.sender === 'agent' && msg.text && !isAgentTyping" class="msg-share-btn">
            <el-button size="small" text type="primary" @click.stop="shareSingleMessage(msg)">分享此回答</el-button>
          </div>
          <div v-if="msg.chartData" class="chart-container">
            <v-chart class="chart" :option="getChartOption(msg.chartData, msg.smartPrediction)" style="height: 350px;" autoresize/>
            <div v-if="msg.smartPrediction" class="smart-badge">
              <span class="badge-engine">{{ msg.smartPrediction.engine }}</span>
              <span class="badge-confidence">置信度: {{ (msg.smartPrediction.confidence * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>
        <div v-if="msg.sender === 'user'" class="avatar">
          <svg viewBox="0 0 48 48" width="28" height="28">
            <circle cx="24" cy="20" r="8" fill="none" stroke="#1d1d1f" stroke-width="2"/>
            <path d="M 12 38 Q 12 28 24 28 Q 36 28 36 38" fill="none" stroke="#1d1d1f" stroke-width="2" stroke-linecap="round"/>
          </svg>
        </div>
      </div>
      <!-- 加载动画 (无变化) -->
      <div v-if="isAgentTyping" class="message-container agent">
         <div class="message-bubble typing-indicator"><span></span><span></span><span></span></div>
      </div>
    </div>

    <!-- 输入区域：文本+文件附件+发送 -->
    <div class="input-area">
      <div v-if="pendingFile" class="file-chip">
        <span>📎 {{ pendingFile.name }}</span>
        <span class="file-chip-remove" @click="removePendingFile">✕</span>
      </div>
      <div class="input-row">
        <el-input
          v-model="userInput"
          :placeholder="inputPlaceholder"
          @keyup.enter="sendMessage"
          :disabled="isAgentTyping"
          clearable
        />
        <el-button
          :icon="UploadFilled"
          :disabled="isAgentTyping || assistantMode !== 'shu_hero'"
          @click="triggerFileSelect"
          style="margin-left: 10px;"
        >
          上传
        </el-button>
        <el-button type="primary" @click="sendMessage" :disabled="isAgentTyping" style="margin-left: 10px;">发送</el-button>
      </div>
      <input ref="fileInputRef" type="file" accept=".csv" style="display: none" @change="onFileSelected" />
    </div>

    <!-- 分享到社区按钮 -->
    <div v-if="messages.length > 1" class="share-bar">
      <el-button size="small" type="success" plain @click="shareToCommmunity">
        分享对话到社区
      </el-button>
      <el-button size="small" type="primary" plain @click="exportReport">
        <el-icon><Download /></el-icon> 导出报告
      </el-button>
    </div>

    <!-- COMBO效果 - 传送到body确保在最上层 -->
    <Teleport to="body">
      <div v-if="showGlobalCombo" class="combo-effect-big" :style="{ left: comboPos.x + 'px', top: comboPos.y + 'px' }">
        <div class="combo-mouse">🐭</div>
        <div class="combo-text-big">🎉 COMBO! 🎉</div>
        <div class="combo-fireworks">
          <span v-for="i in 12" :key="i" class="firework">✨</span>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import { marked } from 'marked';
import { UploadFilled, Download } from '@element-plus/icons-vue'
import request from '@/utils/request';
import { useAuthStore } from '@/stores/auth';

// Markdown渲染函数
marked.setOptions({ breaks: true, gfm: true });
const renderMarkdown = (text) => {
  if (!text) return '';
  try {
    // 确保 # 标题前有空行，否则 marked 不解析
    const normalized = text.replace(/([^\n])(\n#{1,3}\s)/g, '$1\n$2');
    return marked.parse(normalized);
  } catch (e) {
    return text;
  }
};

// --- 状态定义 ---
const userInput = ref('');
const isAgentTyping = ref(false);
const chatWindowRef = ref(null);
const messages = ref([]);
const sessionId = ref(`session_${Date.now()}_${Math.random()}`);
const assistantMode = ref('shu_hero');
const pendingFile = ref(null);
const fileInputRef = ref(null);
const isBlinking = ref(false);
const clickCounts = ref({});
const mousePos = ref({ x: 0, y: 0 });
const showGlobalCombo = ref(false);
const comboPos = ref({ x: 0, y: 0 });

// 积分相关状态
const creditsInfo = ref(null);
const showRedeemDialog = ref(false);
const redeemCode = ref('');
const redeeming = ref(false);

const inputPlaceholder = computed(() => {
  if (assistantMode.value === 'deepseek') {
    return '在这里输入消息，直接使用 DeepSeek-V3.2-Pro...';
  }
  return pendingFile.value ? '输入附加说明（如：帮我深度分析一下）...' : '在这里输入消息...';
});

// --- 生命周期钩子 ---
onMounted(() => {
  sendMessage('你好', true);
  startBlinking();
  fetchCredits();
  window.addEventListener('mousemove', handleMouseMove);
});

const switchAssistantMode = (mode) => {
  if (assistantMode.value === mode) return;
  assistantMode.value = mode;
  pendingFile.value = null;

  const modeWelcome =
    mode === 'deepseek'
      ? '欢迎使用 **DeepSeek-V3.2-Pro**。'
      : '已切换至 **SHU Prophet** 模式。';

  messages.value.push({ sender: 'agent', text: modeWelcome });
  scrollToBottom();
};

// 鼠标追踪
const handleMouseMove = (e) => {
  mousePos.value = { x: e.clientX, y: e.clientY };
};

// 计算头像倾斜样式
const avatarTiltStyle = computed(() => {
  const centerX = window.innerWidth / 2;
  const centerY = window.innerHeight / 2;
  const deltaX = (mousePos.value.x - centerX) / centerX;
  const deltaY = (mousePos.value.y - centerY) / centerY;
  const rotateY = deltaX * 25;
  const rotateX = -deltaY * 25;
  return {
    transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1)`
  };
});

// 眨眼效果
const startBlinking = () => {
  setInterval(() => {
    isBlinking.value = true;
    setTimeout(() => isBlinking.value = false, 150);
  }, 4000);
};

// 点击头像
const onAvatarClick = (index, event) => {
  if (!clickCounts.value[index]) clickCounts.value[index] = 0;
  clickCounts.value[index]++;

  const msg = messages.value[index];
  const phrases = ['我在，直接说。', '今天的数据怎么样？', '让我算算...', '继续发我问题。', '收到。'];

  if (clickCounts.value[index] >= 5) {
    const rect = event.currentTarget.getBoundingClientRect();
    comboPos.value = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    msg.showBubble = false;
    msg.showCombo = true;
    showGlobalCombo.value = true;
    clickCounts.value[index] = 0;
    setTimeout(() => {
      msg.showCombo = false;
      showGlobalCombo.value = false;
    }, 2000);
  } else {
    msg.showCombo = false;
    msg.bubbleText = phrases[Math.floor(Math.random() * phrases.length)];
    msg.showBubble = true;
    setTimeout(() => msg.showBubble = false, 2000);
  }
};

// --- 方法 ---

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    const chatWindow = chatWindowRef.value;
    if (chatWindow) chatWindow.scrollTop = chatWindow.scrollHeight;
  });
};

// 发送消息（支持纯文本 / 文件+文本）
const sendMessage = async (initialMessage = '', isGreeting = false) => {
  const textToSend = isGreeting ? initialMessage : userInput.value.trim();
  const file = pendingFile.value;

  // 没有文本也没有文件，不发送
  if (!textToSend && !file) return;

  // 显示用户消息
  if (!isGreeting) {
    let userText = textToSend || '';
    if (file) userText = userText ? `📎 ${file.name}\n${userText}` : `📎 ${file.name}`;
    messages.value.push({ sender: 'user', text: userText });
  }

  userInput.value = '';
  const currentFile = file;
  pendingFile.value = null;
  isAgentTyping.value = true;
  scrollToBottom();

  try {
    if (assistantMode.value === 'deepseek') {
      const response = await request.post('/deepseek-message', {
        message: textToSend,
        session_id: sessionId.value
      });
      messages.value.push({ sender: 'agent', text: response.data.reply });
    } else if (currentFile) {
      // 文件+文本模式：通过 FormData 发送
      const formData = new FormData();
      formData.append('file', currentFile);
      formData.append('message', textToSend || '');
      const response = await request.post('/agent-upload-predict', formData);
      const data = response.data;
      if (data.error) {
        messages.value.push({ sender: 'agent', text: `分析失败: ${data.error}` });
      } else {
        messages.value.push({
          sender: 'agent',
          text: data.report,
          isReport: true,
          chartData: data.chart_data,
          smartPrediction: data.smart_prediction,
          thinking: data.thinking,
          thinkingExpanded: false,
        });
      }
    } else {
      // 纯文本模式
      const response = await request.post('/agent-message', {
        message: textToSend,
        session_id: sessionId.value
      });
      messages.value.push({ sender: 'agent', text: response.data.reply });
    }
  } catch (error) {
    const status = error.response?.status;
    const errMsg = error.response?.data?.error;
    if (status === 401) {
      // 同步清除 Pinia store 状态
      const authStore = useAuthStore();
      authStore.logout();
      messages.value.push({ sender: 'agent', text: '⚠️ 登录已过期，请重新登录后使用智能助理' });
    } else if (status === 403 && errMsg) {
      messages.value.push({ sender: 'agent', text: `⚠️ ${errMsg}` });
    } else if (errMsg) {
      messages.value.push({ sender: 'agent', text: `⚠️ ${errMsg}` });
    } else {
      messages.value.push({ sender: 'agent', text: `抱歉，服务出了点问题 (${status || '网络错误'})` });
    }
  } finally {
    isAgentTyping.value = false;
    scrollToBottom();
    fetchCredits();
  }
};

// 文件选择（不自动上传）
const triggerFileSelect = () => {
  if (assistantMode.value !== 'shu_hero') {
    ElMessage.warning('DeepSeek 模式暂不支持 CSV 上传');
    return;
  }
  fileInputRef.value?.click();
};

const onFileSelected = (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv');
  if (!isCSV) {
    ElMessage.error('只能上传 CSV 格式的文件!');
    e.target.value = '';
    return;
  }
  pendingFile.value = file;
  e.target.value = '';
};

const removePendingFile = () => {
  pendingFile.value = null;
};

// 分享对话到社区
const shareToCommmunity = async () => {
  const authStore = useAuthStore();
  if (!authStore.isLoggedIn) {
    ElMessage.warning('请先登录后再分享');
    return;
  }
  const conversation = messages.value
    .filter(m => m.text)
    .map(m => ({ sender: m.sender, text: m.text }));
  try {
    await request.post('/community/share-conversation', {
      content: '分享了一段与鼠先知的AI对话',
      conversation
    });
    ElMessage.success('已分享到社区广场');
  } catch {
    ElMessage.error('分享失败');
  }
};

// 获取积分信息
const fetchCredits = async () => {
  try {
    const res = await request.get('/credits/info');
    creditsInfo.value = res.data;
  } catch {
    // 未登录或请求失败，忽略
  }
};

// 分享单条消息到社区
const shareSingleMessage = async (msg) => {
  try {
    await request.post('/community/share-conversation', {
      content: '分享了鼠先知的一条回答',
      conversation: [{ sender: msg.sender, text: msg.text }]
    });
    ElMessage.success('已分享到社区广场');
  } catch {
    ElMessage.error('分享失败');
  }
};

// 分享网站赚积分
const shareWebsite = async () => {
  try {
    await navigator.clipboard.writeText(window.location.origin);
    await request.post('/credits/task', { task_type: 'share_website' });
    ElMessage.success('链接已复制，获得 5 积分');
    fetchCredits();
  } catch {
    ElMessage.error('操作失败');
  }
};

// 导出报告
const exportReport = async () => {
  try {
    const jsPDF = (await import('jspdf')).default;
    const html2canvas = (await import('html2canvas')).default;

    const predictionMsg = messages.value.slice().reverse().find(m => m.chartData || m.isReport);
    if (!predictionMsg) {
      ElMessage.warning('暂无预测结果可导出');
      return;
    }

    const renderedMarkdown = renderMarkdown(predictionMsg.text || '预测分析完成');

    const reportHTML = `
      <div style="font-family: 'Microsoft YaHei', Arial, sans-serif; padding: 40px; width: 750px; background: white;">
        <div style="text-align: center; margin-bottom: 40px;">
          <h1 style="font-size: 28px; color: #1d1d1f; margin-bottom: 10px;">时序预测分析报告</h1>
          <p style="font-size: 14px; color: #6e6e73;">生成日期: ${new Date().toLocaleDateString('zh-CN')}</p>
          <p style="font-size: 12px; color: #86868b;">鼠先知智能预测平台</p>
        </div>
        <div style="border-top: 2px solid #f5f5f7; padding-top: 30px; margin-bottom: 30px;">
          <div style="font-size: 13px; color: #1d1d1f; line-height: 1.8;">${renderedMarkdown}</div>
        </div>
        ${predictionMsg.chartData ? '<div style="margin: 30px 0;"><h2 style="font-size: 18px; color: #1d1d1f; margin-bottom: 15px;">预测图表</h2><div id="chart-placeholder" style="width: 100%; height: 300px; background: #f5f5f7; border-radius: 8px;"></div></div>' : ''}
        <div style="margin-top: 30px; padding: 15px; background: #f5f5f7; border-radius: 8px;">
          <p style="font-size: 11px; color: #86868b; margin: 0; line-height: 1.6;">智能预测引擎基于数据特征自动路由选择最优算法，包含统计模型与深度学习模型的集成预测。</p>
        </div>
      </div>
    `;

    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = reportHTML;
    tempDiv.style.position = 'absolute';
    tempDiv.style.left = '-9999px';
    tempDiv.style.background = 'white';
    document.body.appendChild(tempDiv);

    if (predictionMsg.chartData) {
      const chartElements = document.querySelectorAll('.chart');
      if (chartElements.length > 0) {
        const chartCanvas = await html2canvas(chartElements[chartElements.length - 1], { scale: 1.2 });
        const placeholder = tempDiv.querySelector('#chart-placeholder');
        if (placeholder) {
          placeholder.style.height = 'auto';
          placeholder.innerHTML = '';
          const img = document.createElement('img');
          img.src = chartCanvas.toDataURL();
          img.style.width = '100%';
          img.style.height = 'auto';
          placeholder.appendChild(img);
        }
      }
    }

    const canvas = await html2canvas(tempDiv, { scale: 1.2, backgroundColor: '#ffffff', width: 750 });
    document.body.removeChild(tempDiv);

    const imgData = canvas.toDataURL('image/jpeg', 0.8);
    const pdf = new jsPDF('p', 'mm', [210, (canvas.height * 210) / canvas.width]);
    pdf.addImage(imgData, 'JPEG', 0, 0, 210, (canvas.height * 210) / canvas.width);
    pdf.save(`预测报告_${Date.now()}.pdf`);

    ElMessage.success('报告导出成功');
  } catch (err) {
    console.error(err);
    ElMessage.error('报告导出失败');
  }
};

// 兑换码充值
const doRedeem = async () => {
  if (!redeemCode.value.trim()) {
    ElMessage.warning('请输入兑换码');
    return;
  }
  redeeming.value = true;
  try {
    const res = await request.post('/credits/redeem', { code: redeemCode.value.trim() });
    ElMessage.success(res.data.message);
    redeemCode.value = '';
    showRedeemDialog.value = false;
    fetchCredits();
  } catch (e) {
    ElMessage.error(e.response?.data?.error || '兑换失败');
  } finally {
    redeeming.value = false;
  }
};


// ECharts图表配置 (无变化)
const getChartOption = (chartData, smartPrediction) => {
  const legends = ['历史数据', 'ARIMA预测值'];
  const series = [
    { name: '历史数据', type: 'line', smooth: true, showSymbol: false, data: chartData.history_data, itemStyle: { color: '#38bdf8' } },
    { name: 'ARIMA预测值', type: 'line', smooth: true, showSymbol: false, data: chartData.forecast_data, lineStyle: { type: 'dashed' }, itemStyle: { color: '#67c23a' } }
  ];

  if (smartPrediction && smartPrediction.predictions && chartData.forecast_data) {
    legends.push('智能预测引擎');
    const smartData = chartData.forecast_data.map((point, i) =>
      i < smartPrediction.predictions.length ? [point[0], smartPrediction.predictions[i]] : null
    ).filter(Boolean);
    series.push({
      name: '智能预测引擎', type: 'line', smooth: true, showSymbol: false,
      data: smartData, lineStyle: { type: 'dotted', width: 2 }, itemStyle: { color: '#f59e0b' }
    });
  }

  return {
    tooltip: { trigger: 'axis' },
    legend: { data: legends, top: 'bottom', textStyle: { color: '#e2e8f0' } },
    grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
    xAxis: { type: 'value', name: 'X', splitLine: { show: false } },
    yAxis: { type: 'value', name: 'Y', splitLine: { lineStyle: { color: '#334155' } } },
    series
  };
};
</script>

<style scoped>
.agent-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.agent-header .module-title {
  margin-bottom: 0;
}

.model-switcher {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 6px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(139, 90, 43, 0.12);
  box-shadow: 0 8px 20px rgba(48, 37, 24, 0.06);
}

.model-chip {
  border: none;
  background: transparent;
  color: #6e6e73;
  border-radius: 999px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.25s ease;
}

.model-chip.active {
  background: linear-gradient(135deg, #8b5a2b 0%, #b97a45 58%, #d8b28a 100%);
  color: #fff9f2;
  box-shadow: 0 8px 18px rgba(139, 90, 43, 0.2);
}

.model-chip:not(.active):hover {
  background: rgba(139, 90, 43, 0.08);
  color: #5e3e20;
}

.chat-window {
  height: 65vh;
  background-color: #F7F7F8;
  border: none;
  border-radius: 12px;
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
}
.message-container {
  display: flex;
  margin-bottom: 1rem;
  flex-shrink: 0;
  gap: 10px;
  align-items: flex-start;
}
.message-container.user {
  justify-content: flex-end;
}
.message-container.agent {
  justify-content: flex-start;
}
.avatar-wrapper {
  position: relative;
  cursor: pointer;
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
  margin-left: 20px;
  perspective: 1000px;
}
.avatar-3d {
  transform-style: preserve-3d;
  transition: transform 0.1s ease-out;
}
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  background-color: #ffffff;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  cursor: pointer;
}
.avatar-3d {
  transform-style: preserve-3d;
  transition: transform 0.05s ease-out !important;
}
.avatar:hover {
  transform: scale(1.15);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}
.avatar.is-thinking {
  animation: bounce 0.6s ease-in-out infinite;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.3);
}
.avatar.is-hovering {
  transform: scale(1.2) !important;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.25) !important;
}
.avatar.is-combo {
  animation: comboJump 0.5s ease-out, comboShrink 0.3s 1.7s ease-in !important;
  transform: none !important;
}
@keyframes comboJump {
  0% { transform: scale(1); }
  50% { transform: scale(0.3); opacity: 0.3; }
  100% { transform: scale(0); opacity: 0; }
}
@keyframes comboShrink {
  0% { transform: scale(0); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
}
.combo-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.3);
  z-index: 9999;
  pointer-events: none;
  animation: overlayFade 0.3s ease-out;
}
@keyframes overlayFade {
  0% { opacity: 0; }
  100% { opacity: 1; }
}
.combo-effect-big {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 9999;
  pointer-events: none;
}
.combo-mouse {
  position: absolute;
  font-size: 80px;
  animation: mouseRun 2s ease-in-out;
}
@keyframes mouseRun {
  0% { left: 0; top: 0; transform: rotate(0deg); }
  25% { left: 200px; top: -100px; transform: rotate(360deg); }
  50% { left: 0; top: -200px; transform: rotate(720deg); }
  75% { left: -200px; top: -100px; transform: rotate(1080deg); }
  100% { left: 0; top: 0; transform: rotate(1440deg) scale(0.2); opacity: 0; }
}
.combo-text-big {
  position: absolute;
  top: -150px;
  left: 50%;
  transform: translateX(-50%);
  font-size: 48px;
  font-weight: bold;
  color: #ff6b6b;
  text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
  animation: comboBounce 0.6s ease-out;
}
@keyframes comboBounce {
  0%, 100% { transform: translateX(-50%) scale(1); }
  50% { transform: translateX(-50%) scale(1.3); }
}
.combo-fireworks {
  position: absolute;
  top: 0;
  left: 0;
}
.firework {
  position: absolute;
  font-size: 30px;
  animation: fireworkExplode 1.5s ease-out forwards;
}
.firework:nth-child(1) { animation-delay: 0s; --fx: 150px; --fy: -150px; }
.firework:nth-child(2) { animation-delay: 0.1s; --fx: 200px; --fy: 0; }
.firework:nth-child(3) { animation-delay: 0.2s; --fx: 150px; --fy: 150px; }
.firework:nth-child(4) { animation-delay: 0.3s; --fx: 0; --fy: 200px; }
.firework:nth-child(5) { animation-delay: 0.4s; --fx: -150px; --fy: 150px; }
.firework:nth-child(6) { animation-delay: 0.5s; --fx: -200px; --fy: 0; }
.firework:nth-child(7) { animation-delay: 0.6s; --fx: -150px; --fy: -150px; }
.firework:nth-child(8) { animation-delay: 0.7s; --fx: 0; --fy: -200px; }
.firework:nth-child(9) { animation-delay: 0.8s; --fx: 100px; --fy: -100px; }
.firework:nth-child(10) { animation-delay: 0.9s; --fx: 100px; --fy: 100px; }
.firework:nth-child(11) { animation-delay: 1s; --fx: -100px; --fy: 100px; }
.firework:nth-child(12) { animation-delay: 1.1s; --fx: -100px; --fy: -100px; }
@keyframes fireworkExplode {
  0% { transform: translate(0, 0) scale(0); opacity: 1; }
  100% { transform: translate(var(--fx), var(--fy)) scale(2); opacity: 0; }
}
.click-bubble {
  position: absolute;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
  background: #ffffff;
  color: #1d1d1f;
  padding: 8px 16px;
  border-radius: 16px;
  font-size: 14px;
  white-space: nowrap;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: popIn 0.3s ease-out;
}
@keyframes popIn {
  0% { transform: translateX(-50%) scale(0); opacity: 0; }
  50% { transform: translateX(-50%) scale(1.1); }
  100% { transform: translateX(-50%) scale(1); opacity: 1; }
}
@keyframes breathe {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.03); }
}
@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-4px); }
}
.message-bubble {
  max-width: 75%;
  padding: 12px 16px;
  border-radius: 18px;
  line-height: 1.6;
  word-wrap: break-word;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
  position: relative;
}
.message-container.user .message-bubble {
  background-color: #DCF8C6;
  color: #1d1d1f;
  border-bottom-right-radius: 4px;
}
.message-container.agent .message-bubble {
  background-color: #ECECEC;
  color: #1d1d1f;
  border-bottom-left-radius: 4px;
}
.chart-container {
  margin-top: 1rem;
  background-color: #ffffff;
  border-radius: 12px;
  padding: 1rem;
  border: 1px solid #e5e5e5;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}
.smart-badge {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  font-size: 12px;
}

@media (max-width: 768px) {
  .agent-header {
    align-items: stretch;
  }

  .model-switcher {
    width: 100%;
    justify-content: space-between;
  }

  .model-chip {
    flex: 1;
    text-align: center;
  }
}
.badge-engine {
  background: linear-gradient(135deg, #f59e0b, #d97706);
  color: #fff;
  padding: 2px 10px;
  border-radius: 12px;
  font-weight: 600;
}
.badge-confidence {
  color: #6b7280;
}
.message-bubble :deep(h3) {
  font-size: 1.1rem;
  color: #1d1d1f;
  margin-top: 1rem;
  margin-bottom: 0.5rem;
  font-weight: 600;
}
.message-bubble :deep(p) {
  margin: 0 0 0.5rem 0;
}
.message-bubble :deep(strong) {
  font-weight: 600;
}
.message-bubble :deep(code) {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}
.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3) {
  font-weight: 600;
  margin-top: 1em;
  margin-bottom: 0.5em;
  color: #1d1d1f;
}
.markdown-content :deep(h1) { font-size: 1.5em; }
.markdown-content :deep(h2) { font-size: 1.3em; }
.markdown-content :deep(h3) { font-size: 1.1em; }
.markdown-content :deep(p) {
  margin: 0.5em 0;
  line-height: 1.6;
}
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin: 0.5em 0;
  padding-left: 1.5em;
}
.markdown-content :deep(li) {
  margin: 0.3em 0;
  line-height: 1.6;
}
.markdown-content :deep(pre) {
  background-color: #f6f8fa;
  border-radius: 6px;
  padding: 12px;
  overflow-x: auto;
  margin: 0.5em 0;
}
.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
}
.markdown-content :deep(strong) {
  font-weight: 600;
  color: #1d1d1f;
}
.markdown-content :deep(em) {
  font-style: italic;
}
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 8px 0;
}
.typing-indicator span {
  height: 8px;
  width: 8px;
  background-color: #999;
  border-radius: 50%;
  animation: 1s blink infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: .2s; }
.typing-indicator span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 50% { opacity: 0.3; } }

.input-area {
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.input-row {
  display: flex;
  align-items: center;
  gap: 12px;
}
.input-area :deep(.el-input__wrapper) {
  background-color: #ffffff;
  border-radius: 24px;
  padding: 12px 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}
.input-area :deep(.el-button) {
  border-radius: 20px;
  padding: 12px 24px;
  font-weight: 500;
}

/* 文件附件芯片 */
.file-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  background: #e8f4fd;
  color: #1a73e8;
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 13px;
  max-width: 300px;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
.file-chip-remove {
  cursor: pointer;
  font-size: 14px;
  color: #999;
  margin-left: 4px;
}
.file-chip-remove:hover {
  color: #e74c3c;
}

/* 思考过程样式 */
.thinking-section {
  margin-bottom: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  overflow: hidden;
  background: #fafafa;
}
.thinking-header {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  cursor: pointer;
  font-size: 13px;
  color: #6b7280;
  user-select: none;
  transition: background 0.2s;
}
.thinking-header:hover {
  background: #f0f0f0;
}
.thinking-icon {
  font-size: 16px;
}
.thinking-toggle {
  margin-left: auto;
  font-size: 12px;
  color: #9ca3af;
}
.thinking-steps {
  padding: 0 12px 10px;
  max-height: 300px;
  overflow-y: auto;
}
.thinking-step {
  padding: 6px 0;
  border-bottom: 1px dashed #e5e7eb;
  font-size: 12px;
  line-height: 1.5;
}
.thinking-step:last-child {
  border-bottom: none;
}
.step-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 2px;
}
.step-num {
  background: #e0e7ff;
  color: #4338ca;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}
.step-tool {
  font-weight: 600;
  color: #374151;
}
.step-time {
  margin-left: auto;
  color: #9ca3af;
  font-size: 11px;
}
.step-thought {
  color: #6b7280;
  padding-left: 28px;
}
.step-result {
  color: #059669;
  padding-left: 28px;
  font-family: 'Courier New', monospace;
  font-size: 11px;
  word-break: break-all;
}

/* 分享按钮栏 */
.share-bar {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
}

/* 积分信息栏 */
.credits-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 16px;
  background: #f0f7ff;
  border-radius: 10px;
  margin-bottom: 12px;
  font-size: 13px;
  color: #6e6e73;
  flex-wrap: wrap;
}
.credits-item b {
  color: #0071e3;
  font-weight: 600;
}

/* 单条消息分享按钮 */
.msg-share-btn {
  display: flex;
  justify-content: flex-end;
  margin-top: 4px;
  opacity: 0;
  transition: opacity 0.2s;
}
.message-bubble:hover .msg-share-btn {
  opacity: 1;
}
</style>
