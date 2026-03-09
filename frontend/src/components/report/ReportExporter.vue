<template>
  <el-button @click="exportReport" :loading="loading" type="success" size="small">
    <el-icon><Download /></el-icon> 导出报告
  </el-button>
</template>

<script setup>
import { ref } from 'vue';
import { Download } from '@element-plus/icons-vue';
import { generateReport } from '@/utils/pdfGenerator';
import { ElMessage } from 'element-plus';

const props = defineProps({
  title: String,
  predictions: Array,
  chartRef: Object
});

const loading = ref(false);

const exportReport = async () => {
  loading.value = true;
  try {
    const pdf = await generateReport({
      title: props.title || '预测分析报告',
      predictions: props.predictions,
      chartElement: props.chartRef
    });
    pdf.save(`预测报告_${Date.now()}.pdf`);
    ElMessage.success('报告导出成功');
  } catch (error) {
    ElMessage.error('报告导出失败');
  } finally {
    loading.value = false;
  }
};
</script>
