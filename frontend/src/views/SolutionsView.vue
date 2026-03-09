<template>
  <div class="solutions-view">
    <div class="hero">
      <h1>商业解决方案</h1>
      <p>基于前沿时序预测算法的行业落地场景</p>
    </div>

    <div class="scenarios">
      <div class="scenario-card" v-for="scenario in scenarios" :key="scenario.id">
        <div class="scenario-header">
          <el-icon :size="32" :color="scenario.color"><component :is="scenario.icon" /></el-icon>
          <h2>{{ scenario.title }}</h2>
        </div>
        <p class="scenario-desc">{{ scenario.description }}</p>
        <div class="pain-points">
          <h3>业务痛点</h3>
          <ul>
            <li v-for="pain in scenario.pains" :key="pain">{{ pain }}</li>
          </ul>
        </div>
        <div class="solution">
          <h3>技术方案</h3>
          <p>{{ scenario.solution }}</p>
        </div>
        <div class="chart-container">
          <div :ref="el => chartRefs[scenario.id] = el" class="chart"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import * as echarts from 'echarts';
import { Sunny, Monitor, ShoppingCart } from '@element-plus/icons-vue';

const chartRefs = reactive({});

const scenarios = [
  {
    id: 'energy',
    title: '新能源预测',
    icon: Sunny,
    color: '#f59e0b',
    description: '风电/光伏功率预测，助力双碳战略与电网稳定',
    pains: ['新能源出力波动大，电网调度困难', '弃风弃光造成资源浪费', '缺乏精准预测导致备用容量过高'],
    solution: '智能预测引擎自动分析气象数据与历史出力，提前24小时预测功率曲线，预测误差<5%，帮助电网优化调度策略'
  },
  {
    id: 'iot',
    title: '工业物联网',
    icon: Monitor,
    color: '#3b82f6',
    description: '设备预测性维护，降低故障停机损失',
    pains: ['设备突发故障导致生产中断', '定期维护成本高且效率低', '传感器数据未充分利用'],
    solution: '实时监测设备温度、振动等指标，智能识别异常趋势，提前3-7天预警潜在故障，维护成本降低30%'
  },
  {
    id: 'retail',
    title: '供应链管理',
    icon: ShoppingCart,
    color: '#10b981',
    description: '销量预测与动态库存优化',
    pains: ['库存积压或缺货频发', '促销活动效果难以预估', '季节性需求把握不准'],
    solution: '结合历史销量、节假日、促销活动等因素，智能预测未来需求，库存周转率提升25%，缺货率下降40%'
  }
];

const generateEnergyData = () => {
  const hours = Array.from({ length: 48 }, (_, i) => i);
  const historical = hours.slice(0, 24).map(h => {
    const base = 50 + 30 * Math.sin((h - 6) * Math.PI / 12);
    return base + (Math.random() - 0.5) * 8;
  });
  const forecast = hours.slice(24).map(h => {
    const base = 50 + 30 * Math.sin((h - 6) * Math.PI / 12);
    return base + (Math.random() - 0.5) * 3;
  });
  return { hours, historical, forecast };
};

const generateIoTData = () => {
  const hours = Array.from({ length: 48 }, (_, i) => i);
  const normal = hours.slice(0, 36).map(() => 65 + (Math.random() - 0.5) * 4);
  const anomaly = hours.slice(36).map((_, i) => 65 + i * 1.5 + (Math.random() - 0.5) * 3);
  return { hours, normal, anomaly };
};

const generateRetailData = () => {
  const months = ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'];
  const historical = [820, 932, 901, 934, 1290, 1330, 1320, 1450, 1200, 1100, 1520, 2100];
  const forecast = [950, 1050, 980];
  return { months, historical, forecast };
};

onMounted(() => {
  const energyData = generateEnergyData();
  const energyChart = echarts.init(chartRefs.energy);
  energyChart.setOption({
    title: { text: '风电功率预测 (MW)', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis' },
    legend: { data: ['历史数据', '预测数据'], bottom: 0 },
    xAxis: { type: 'category', data: energyData.hours.map(h => `${h}:00`) },
    yAxis: { type: 'value', name: '功率(MW)' },
    series: [
      { name: '历史数据', type: 'line', data: [...energyData.historical, ...Array(24).fill(null)], itemStyle: { color: '#3b82f6' } },
      { name: '预测数据', type: 'line', data: [...Array(24).fill(null), ...energyData.forecast], itemStyle: { color: '#f59e0b' }, lineStyle: { type: 'dashed' } }
    ]
  });

  const iotData = generateIoTData();
  const iotChart = echarts.init(chartRefs.iot);
  iotChart.setOption({
    title: { text: '设备温度监测 (°C)', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: iotData.hours.map(h => `${h}h`) },
    yAxis: { type: 'value', name: '温度(°C)' },
    visualMap: { show: false, pieces: [{ gt: 0, lte: 36, color: '#10b981' }, { gt: 36, color: '#ef4444' }] },
    series: [{ type: 'line', data: [...iotData.normal, ...iotData.anomaly], markLine: { data: [{ yAxis: 75, label: { formatter: '异常阈值' }, lineStyle: { color: '#ef4444' } }] } }]
  });

  const retailData = generateRetailData();
  const retailChart = echarts.init(chartRefs.retail);
  retailChart.setOption({
    title: { text: '月度销量预测', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis' },
    legend: { data: ['历史销量', '预测销量'], bottom: 0 },
    xAxis: { type: 'category', data: [...retailData.months, '次年1月', '次年2月', '次年3月'] },
    yAxis: { type: 'value', name: '销量' },
    series: [
      { name: '历史销量', type: 'bar', data: [...retailData.historical, ...Array(3).fill(null)], itemStyle: { color: '#3b82f6' } },
      { name: '预测销量', type: 'bar', data: [...Array(12).fill(null), ...retailData.forecast], itemStyle: { color: '#10b981' } }
    ]
  });
});
</script>

<style scoped>
.solutions-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 40px 20px;
}
.hero {
  text-align: center;
  margin-bottom: 60px;
}
.hero h1 {
  font-size: 36px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #1d1d1f;
}
.hero p {
  font-size: 18px;
  color: #6e6e73;
}
.scenarios {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 32px;
}
.scenario-card {
  background: white;
  border-radius: 12px;
  padding: 32px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.scenario-header {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 16px;
}
.scenario-header h2 {
  font-size: 24px;
  font-weight: 600;
  color: #1d1d1f;
}
.scenario-desc {
  font-size: 16px;
  color: #6e6e73;
  margin-bottom: 24px;
}
.pain-points, .solution {
  margin-bottom: 24px;
}
.pain-points h3, .solution h3 {
  font-size: 16px;
  font-weight: 600;
  color: #1d1d1f;
  margin-bottom: 12px;
}
.pain-points ul {
  list-style: none;
  padding: 0;
}
.pain-points li {
  padding: 8px 0;
  color: #6e6e73;
  font-size: 14px;
}
.pain-points li:before {
  content: "•";
  color: #ef4444;
  font-weight: bold;
  margin-right: 8px;
}
.solution p {
  color: #6e6e73;
  font-size: 14px;
  line-height: 1.6;
}
.chart-container {
  margin-top: 24px;
}
.chart {
  width: 100%;
  height: 300px;
}
</style>
