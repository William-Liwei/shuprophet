<template>
  <div class="module-card">
    <h2 class="module-title">
      <el-icon><MagicStick /></el-icon>
      <span>智能助理 SHU Prophet</span>
    </h2>

    <!-- 对话窗口 (无变化) -->
    <div class="chat-window" ref="chatWindowRef">
      <!-- 消息历史 -->
      <div v-for="(msg, index) in messages" :key="index" class="message-container" :class="msg.sender">
        <div class="message-bubble">
          <div v-if="msg.isReport" v-html="msg.text"></div>
          <p v-else v-text="msg.text"></p> <!-- 使用v-text防止渲染意外的HTML-->
          <div v-if="msg.chartData" class="chart-container">
            <v-chart class="chart" :option="getChartOption(msg.chartData)" style="height: 350px;" autoresize/>
          </div>
        </div>
      </div>
      <!-- 加载动画 (无变化) -->
      <div v-if="isAgentTyping" class="message-container agent">
         <div class="message-bubble typing-indicator"><span></span><span></span><span></span></div>
      </div>
    </div>

    <!-- 核心升级：全新的输入区域，集成了文本输入、上传和发送按钮 -->
    <div class="input-area">
      <el-input
        v-model="userInput"
        placeholder="在这里输入消息..."
        @keyup.enter="sendMessage"
        :disabled="isAgentTyping"
        clearable
      >
        <!-- 将上传按钮集成到输入框的后面 -->
        <template #append>
          <el-upload
            ref="uploadRef"
            action="/api/agent-upload-predict"
            name="file"
            :show-file-list="false"
            :on-success="handleUploadSuccess"
            :on-error="handleUploadError"
            :before-upload="beforeUpload"
          >
            <el-button :icon="UploadFilled" :disabled="isAgentTyping"></el-button>
          </el-upload>
        </template>
      </el-input>
      <el-button type="primary" @click="sendMessage" :disabled="isAgentTyping" style="margin-left: 10px;">发送</el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { marked } from 'marked';
import { UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios';

// --- 状态定义 ---
const userInput = ref('');
const isAgentTyping = ref(false);
const chatWindowRef = ref(null);
const messages = ref([]);
const sessionId = ref(`session_${Date.now()}_${Math.random()}`); // 为每个会话创建一个唯一ID

// --- 生命周期钩子 ---
onMounted(() => {
  // 组件加载后，自动发送一个 "你好" 来触发Agent的开场白
  sendMessage('你好', true); 
});

// --- 方法 ---

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    const chatWindow = chatWindowRef.value;
    if (chatWindow) chatWindow.scrollTop = chatWindow.scrollHeight;
  });
};

// 发送纯文本消息
const sendMessage = async (initialMessage = '', isGreeting = false) => {
  const textToSend = isGreeting ? initialMessage : userInput.value.trim();
  if (!textToSend) return;

  if (!isGreeting) {
    messages.value.push({ sender: 'user', text: textToSend });
  }
  
  userInput.value = ''; // 清空输入框
  isAgentTyping.value = true;
  scrollToBottom();

  try {
    const response = await axios.post('/api/agent-message', {
      message: textToSend,
      session_id: sessionId.value
    });
    messages.value.push({ sender: 'agent', text: response.data.reply });
  } catch (error) {
    messages.value.push({ sender: 'agent', text: '抱歉，我好像遇到了一点网络问题。' });
  } finally {
    isAgentTyping.value = false;
    scrollToBottom();
  }
};

// 文件上传前的钩子
const beforeUpload = (file) => {
  const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv');
  if (!isCSV) {
    ElMessage.error('只能上传 CSV 格式的文件!');
    return false;
  }
  messages.value.push({ sender: 'user', text: `(已上传文件: ${file.name})` });
  isAgentTyping.value = true;
  scrollToBottom();
  return true;
};

// 文件上传成功的回调
const handleUploadSuccess = (response) => {
  isAgentTyping.value = false;
  if (response.error) {
    messages.value.push({ sender: 'agent', text: `分析失败: ${response.error}` });
  } else {
    const reportHtml = marked(response.report);
    messages.value.push({
      sender: 'agent',
      text: reportHtml,
      isReport: true,
      chartData: response.chart_data
    });
  }
  scrollToBottom();
};

// 文件上传失败的回调
const handleUploadError = (error) => {
  isAgentTyping.value = false;
  const errorMsg = JSON.parse(error.message)?.error || '上传或分析失败，请检查文件或后端服务。';
  messages.value.push({ sender: 'agent', text: `出现错误: ${errorMsg}` });
  scrollToBottom();
};

// ECharts图表配置 (无变化)
const getChartOption = (chartData) => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['历史数据', 'ARIMA预测值'], top: 'bottom', textStyle: { color: '#e2e8f0' } },
  grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
  xAxis: { type: 'value', name: 'X', splitLine: { show: false } },
  yAxis: { type: 'value', name: 'Y', splitLine: { lineStyle: { color: '#334155' } } },
  series: [
    { name: '历史数据', type: 'line', smooth: true, showSymbol: false, data: chartData.history_data, itemStyle: { color: '#38bdf8' } },
    { name: 'ARIMA预测值', type: 'line', smooth: true, showSymbol: false, data: chartData.forecast_data, lineStyle: { type: 'dashed' }, itemStyle: { color: '#67c23a' } }
  ]
});
</script>

<style scoped>
/* 旧样式保持不变 */
.chat-window { height: 65vh; background-color: #0c1a32; border: 1px solid #1e293b; border-radius: 8px; padding: 1rem; overflow-y: auto; display: flex; flex-direction: column; }
.message-container { display: flex; margin-bottom: 1rem; flex-shrink: 0; }
.message-container.user { justify-content: flex-end; }
.message-container.agent { justify-content: flex-start; }
.message-bubble { max-width: 90%; padding: 0.75rem 1rem; border-radius: 12px; color: #e2e8f0; line-height: 1.6; word-wrap: break-word; }
.message-container.user .message-bubble { background-color: #409eff; color: #fff; }
.message-container.agent .message-bubble { background-color: #1e293b; }
.chart-container { margin-top: 1rem; background-color: rgba(0,0,0,0.2); border-radius: 8px; padding: 1rem 0.5rem 0.5rem 0.5rem; }
.message-bubble :deep(h3) { font-size: 1.1rem; color: #87cefa; margin-top: 1rem; margin-bottom: 0.5rem; border-bottom: 1px solid #334155; padding-bottom: 0.3rem; }
.message-bubble :deep(p) { margin: 0 0 0.5rem 0; }
.typing-indicator span { height: 8px; width: 8px; float: left; margin: 0 2px; background-color: #94a3b8; display: block; border-radius: 50%; opacity: 0.4; animation: 1s blink infinite; }
.typing-indicator span:nth-child(2) { animation-delay: .2s; }
.typing-indicator span:nth-child(3) { animation-delay: .4s; }
@keyframes blink { 50% { opacity: 1; } }

/* 新增样式：用于底部的输入区域 */
.input-area {
  margin-top: 1.5rem;
  display: flex;
  align-items: center;
}
/* 深度选择器，修改el-upload的内联样式 */
.input-area :deep(.el-upload) {
  --el-input-group-append-padding: 0;
  --el-input-group-append-border-color: transparent;
}
</style>