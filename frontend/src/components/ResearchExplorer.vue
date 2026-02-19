<template>
  <div class="module-card">
    <h2 class="module-title"><el-icon><Box /></el-icon><span>科研成果探索</span></h2>
    <el-form label-position="top">
      <el-form-item label="选择数据集进行预处理与分析">
        <el-select v-model="selectedDataset" placeholder="请选择数据集" style="width: 100%;" @change="runAnalysis" filterable>
          <el-option v-for="item in datasetOptions" :key="item" :label="item" :value="item"/>
        </el-select>
      </el-form-item>
    </el-form>

    <div v-if="isLoading" class="loading-container">
      <div class="progress-bar">
        <div class="progress-fill" :style="{width: loadingProgress + '%'}"></div>
      </div>
      <div class="loading-text">{{ loadingStage }}</div>
    </div>
    
    <div v-if="!isLoading && chartData">
      <el-row :gutter="12" class="metrics-cards">
        <el-col :span="12" v-for="model in chartData.model_predictions" :key="model.model_name">
          <div class="metric-card">
            <span class="model-name">{{ model.model_name }}</span>
            <div class="metrics">
              <span>MAE: <b>{{ model.metrics.mae }}</b></span>
              <span>MSE: <b>{{ model.metrics.mse }}</b></span>
            </div>
          </div>
        </el-col>
      </el-row>
      <v-chart class="chart" :option="chartOption" style="height: 450px;" autoresize/>
      <v-chart class="chart" :option="performanceOption" style="height: 300px; margin-top: 20px;" autoresize/>
    </div>

    <el-empty v-if="!isLoading && !chartData" description="请选择一个数据集开始分析" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import { ElMessage } from 'element-plus';

const selectedDataset = ref('');
const datasetOptions = ref([]);
const isLoading = ref(false);
const chartData = ref(null);
const loadingProgress = ref(0);
const loadingStage = ref('');

onMounted(async () => {
  try {
    const response = await axios.get('/api/datasets');
    datasetOptions.value = response.data;
    if (datasetOptions.value.length > 0) {
      selectedDataset.value = datasetOptions.value[0];
      runAnalysis(); // 自动加载第一个数据集
    }
  } catch (error) {
    ElMessage.error('获取数据集列表失败！');
  }
});

const runAnalysis = async () => {
  if (!selectedDataset.value) return;
  isLoading.value = true;
  chartData.value = null;
  loadingProgress.value = 0;
  loadingStage.value = '数据加载中...';

  try {
    await new Promise(r => setTimeout(r, 400));
    loadingProgress.value = 33;
    loadingStage.value = '模型推理中...';

    const response = await axios.post('/api/parse-csv', {
      dataset: selectedDataset.value,
    });

    loadingProgress.value = 66;
    loadingStage.value = '结果生成中...';
    await new Promise(r => setTimeout(r, 300));

    if (response.data.error) {
      ElMessage.error(response.data.error);
    } else {
      loadingProgress.value = 100;
      await new Promise(r => setTimeout(r, 200));
      chartData.value = response.data;
    }
  } catch (error) {
    const errorMsg = error.response?.data?.error || '分析失败，请检查后端服务。';
    ElMessage.error(errorMsg);
  } finally {
    isLoading.value = false;
  }
};

const chartOption = computed(() => {
  if (!chartData.value) return {};

  const series = [];
  const legendData = [];

  legendData.push(chartData.value.actual_data.model_name);
  series.push({
    name: chartData.value.actual_data.model_name,
    type: 'line',
    smooth: true,
    showSymbol: false,
    data: chartData.value.actual_data.data,
    lineStyle: { color: '#CD853F', width: 2.5 }
  });

  const colors = ['#FFD700', '#CD7F32', '#B87333', '#E0BFB8', '#FFBF00', '#CC5500', '#D4AF37'];
  chartData.value.model_predictions.forEach((model, index) => {
    legendData.push(model.model_name);
    series.push({
      name: model.model_name,
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: model.data,
      lineStyle: { type: 'dashed', width: 2, color: colors[index % colors.length] }
    });
  });

  return {
    title: { text: '模型性能可视化对比', left: 'center', textStyle: { color: '#FFD700' } },
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(26, 20, 16, 0.95)', borderColor: '#3d2817' },
    legend: { data: legendData, top: 'bottom', textStyle: { color: '#E0BFB8' } },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: { type: 'value', name: 'X', splitLine: { show: false }, axisLabel: { color: '#c9a87c' }, nameTextStyle: { color: '#c9a87c' } },
    yAxis: { type: 'value', name: 'Y', splitLine: { lineStyle: { color: '#3d2817' } }, axisLabel: { color: '#c9a87c' }, nameTextStyle: { color: '#c9a87c' } },
    series: series,
    toolbox: { feature: { saveAsImage: {}, dataZoom: { yAxisIndex: 'none' } }, iconStyle: { borderColor: '#94a3b8' } },
    dataZoom: [{ type: 'inside', filterMode: 'weak' }, { type: 'slider', backgroundColor: 'rgba(30, 41, 59, 0.4)', fillerColor: 'rgba(64, 158, 255, 0.2)' }],
  };
});

const performanceOption = computed(() => {
  if (!chartData.value) return {};

  // 按MAE排序（从小到大，最好的在前）
  const sorted = chartData.value.model_predictions
    .map(m => ({ name: m.model_name, mae: m.metrics.mae }))
    .sort((a, b) => a.mae - b.mae);

  const models = sorted.map(m => m.name);
  const maeValues = sorted.map(m => m.mae);
  const baseline = Math.max(...maeValues);

  return {
    title: { text: '性能对比 (MAE)', left: 'center', textStyle: { color: '#FFD700', fontSize: 16 } },
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
    xAxis: { type: 'category', data: models, axisLabel: { color: '#c9a87c', rotate: 15 } },
    yAxis: { type: 'value', name: 'MAE', axisLabel: { color: '#c9a87c' }, nameTextStyle: { color: '#c9a87c' } },
    series: [{
      type: 'bar',
      data: maeValues.map((v, i) => ({
        value: v,
        itemStyle: {
          color: i === 0 ? '#FFD700' : i === 1 ? '#E0BFB8' : i === 2 ? '#CD7F32' : '#666666'
        },
        label: {
          show: true,
          position: 'top',
          formatter: () => `↓${((baseline - v) / baseline * 100).toFixed(1)}%`,
          color: i < 3 ? '#FFD700' : '#999999'
        }
      }))
    }]
  };
});

</script>

<style scoped>
.loading-container {
  height: 400px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  gap: 1rem;
}

.progress-bar {
  width: 60%;
  height: 8px;
  background: rgba(61, 40, 23, 0.6);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #FFD700, #E0BFB8);
  transition: width 0.3s ease;
}

.loading-text {
  color: #c9a87c;
  font-size: 0.9rem;
}
</style>