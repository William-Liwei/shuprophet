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

    <div v-if="isLoading" v-loading="true" element-loading-text="正在处理与计算..." style="height: 550px; border-radius: 8px;"></div>
    
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
  try {
    const response = await axios.post('/api/parse-csv', {
      dataset: selectedDataset.value,
    });
    
    if (response.data.error) {
      ElMessage.error(response.data.error);
    } else {
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

  // 1. 添加平滑后的真实值系列
  legendData.push(chartData.value.actual_data.model_name);
  series.push({
    name: chartData.value.actual_data.model_name,
    type: 'line',
    smooth: true,
    showSymbol: false,
    data: chartData.value.actual_data.data,
    lineStyle: { color: '#F56C6C', width: 2.5 }
  });

  // 2. 添加所有真实的、平滑后的模型预测系列
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#909399'];
  chartData.value.model_predictions.forEach((model, index) => {
    legendData.push(model.model_name);
    series.push({
      name: model.model_name,
      type: 'line',
      smooth: true,
      showSymbol: false,
      data: model.data,
      lineStyle: { 
        type: 'dashed',
        width: 2,
        color: colors[index % colors.length]
      }
    });
  });

  return {
    title: { text: '模型性能可视化对比', left: 'center', textStyle: { color: '#e2e8f0' } },
    tooltip: { trigger: 'axis', backgroundColor: 'rgba(12, 26, 50, 0.85)', borderColor: '#1e293b' },
    legend: { data: legendData, top: 'bottom', textStyle: { color: '#e2e8f0' } },
    grid: { left: '3%', right: '4%', bottom: '10%', containLabel: true },
    xAxis: { type: 'value', name: 'X', splitLine: { show: false }, axisLabel: { color: '#94a3b8' }, nameTextStyle: { color: '#94a3b8' } },
    yAxis: { type: 'value', name: 'Y', splitLine: { lineStyle: { color: '#1e293b' } }, axisLabel: { color: '#94a3b8' }, nameTextStyle: { color: '#94a3b8' } },
    series: series,
    toolbox: { feature: { saveAsImage: {}, dataZoom: { yAxisIndex: 'none' } }, iconStyle: { borderColor: '#94a3b8' } },
    dataZoom: [{ type: 'inside', filterMode: 'weak' }, { type: 'slider', backgroundColor: 'rgba(30, 41, 59, 0.4)', fillerColor: 'rgba(64, 158, 255, 0.2)' }],
  };
});
</script>