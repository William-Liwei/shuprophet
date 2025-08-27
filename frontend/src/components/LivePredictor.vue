<template>
  <div class="module-card">
    <h2 class="module-title">
      <el-icon><Lightning /></el-icon>
      <span>实时预测体验</span>
    </h2>

    <!-- 文件上传组件 -->
    <el-upload
      drag
      action="/api/live-predict"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      :limit="1"
      :on-exceed="() => ElMessage.warning('只能上传一个文件，请先移除当前文件')"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">
        拖拽 CSV 文件到此或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          上传仅含两列 (X, Y) 的CSV文件，后台将使用ARIMA模型进行实时预测。
        </div>
      </template>
    </el-upload>
    
    <!-- 结果展示区域 -->
    <div v-if="predictionResult" v-loading="isPredicting" style="margin-top: 2rem;">
      <v-chart class="chart" :option="predictionChartOption" style="height: 450px;" autoresize/>
    </div>

    <!-- 初始状态或无结果时显示空状态 -->
    <el-empty v-else description="上传数据以开始实时预测" style="margin-top: 2rem;"/>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { ElMessage } from 'element-plus';
// Element Plus 图标在 main.js 中已全局注册，此处无需单独引入

// --- 响应式状态定义 ---

// 控制加载动画的显示
const isPredicting = ref(false);
// 存储从后端返回的预测结果
const predictionResult = ref(null);


// --- 函数定义 ---

/**
 * 文件上传前的钩子函数，用于校验文件类型和大小。
 * @param {File} file - 用户选择的文件对象。
 * @returns {boolean} - 返回 false 则取消上传。
 */
const beforeUpload = (file) => {
  const isCSV = file.type === 'text/csv' || file.name.endsWith('.csv');
  if (!isCSV) {
    ElMessage.error('只能上传 CSV 格式的文件!');
    return false; // 阻止上传
  }
  isPredicting.value = true; // 开始显示加载动画
  predictionResult.value = null; // 清空上一次的预测结果
  return true; // 允许上传
};

/**
 * 文件上传成功后的回调函数。
 * @param {object} response - 后端 API 返回的 JSON 数据。
 * @param {object} file - 上传的文件信息。
 */
const handleSuccess = (response, file) => {
  if (response.error) {
    ElMessage.error(`预测失败: ${response.error}`);
    predictionResult.value = null;
  } else {
    ElMessage.success('实时预测成功!');
    predictionResult.value = response; // 保存预测结果
  }
  isPredicting.value = false; // 结束加载动画
};

/**
 * 文件上传失败后的回调函数。
 * @param {Error} error - 错误对象。
 * @param {object} file - 上传的文件信息。
 */
const handleError = (error, file) => {
  ElMessage.error('上传或预测失败，请检查文件格式或后端服务是否正常运行。');
  isPredicting.value = false; // 结束加载动画
};

/**
 * ECharts 图表的计算属性。
 * 当 predictionResult 变化时，它会自动重新计算图表配置。
 */
const predictionChartOption = computed(() => {
  // 如果没有结果，返回一个空对象
  if (!predictionResult.value) return {};

  // 返回 ECharts 的配置对象
  return {
    title: { 
      text: '用户数据实时预测结果', 
      left: 'center', 
      textStyle: { color: '#e2e8f0' } 
    },
    tooltip: { 
      trigger: 'axis' 
    },
    legend: { 
      data: ['历史数据', 'ARIMA预测值'], 
      top: 'bottom', 
      textStyle: { color: '#e2e8f0' } 
    },
    grid: { 
      left: '3%', 
      right: '4%', 
      bottom: '10%', 
      containLabel: true 
    },
    xAxis: { 
      type: 'value', 
      name: 'X', 
      splitLine: { show: false } 
    },
    yAxis: { 
      type: 'value', 
      name: 'Y', 
      splitLine: { lineStyle: { color: '#334155' } } 
    },
    series: [
      { 
        name: '历史数据', 
        type: 'scatter', // 历史数据用散点图表示
        symbolSize: 8, 
        data: predictionResult.value.history_data,
        itemStyle: { color: '#38bdf8' }
      },
      { 
        name: 'ARIMA预测值', 
        type: 'line', // 预测数据用虚线表示
        smooth: true, 
        showSymbol: false, 
        data: predictionResult.value.forecast_data, 
        lineStyle: { type: 'dashed' }, 
        itemStyle: { color: '#67c23a' } 
      }
    ]
  };
});
</script>

<style scoped>
/* 可以在这里添加只对本组件生效的样式 */
.el-upload__tip {
  line-height: 1.2;
}
</style>