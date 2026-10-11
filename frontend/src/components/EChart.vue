<template><ECharts v-bind="$attrs" /></template>
<script setup>
import ECharts from 'vue-echarts'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, ScatterChart, BarChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent, ToolboxComponent, DataZoomComponent, VisualMapComponent } from 'echarts/components'
use([CanvasRenderer, LineChart, ScatterChart, BarChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, ToolboxComponent, DataZoomComponent, VisualMapComponent])
</script>
