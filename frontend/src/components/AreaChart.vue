<template>
  <div class="area-chart-wrapper">
    <div class="chart-title">{{ title }}</div>
    <div ref="chartRef" class="area-chart-container"></div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, watch, ref } from 'vue'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([
  LineChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  DatasetComponent,
  CanvasRenderer
])

const props = defineProps({
  title: { type: String, default: '' },
  // 数据格式: [{ label | date | month, value or cumulative, increment? }]
  data: { type: Array, default: () => [] }
})

const chartRef = ref(null)
let chartInstance = null
let resizeObserver = null

function getXAxisLabels() {
  return props.data.map((d) => d.label || d.date || d.month || '')
}
function getSeriesValues() {
  return props.data.map((d) => (typeof d.value === 'number' ? d.value : d.cumulative || 0))
}

function buildOption() {
  const labels = getXAxisLabels()
  const values = getSeriesValues()

  return {
    backgroundColor: 'transparent',

    tooltip: {
      trigger: 'axis',
      appendToBody: true,
      backgroundColor: '#ffffff',
      borderColor: '#93c5fd',
      borderWidth: 1,
      textStyle: { color: '#1e293b' },
      axisPointer: {
        type: 'line',
        lineStyle: { color: '#3b82f6', width: 2, opacity: 0.3 }
      },
      formatter(params) {
        const p = params[0]
        const idx = p.dataIndex
        const raw = props.data[idx] || {}
        return [
          labels[idx],
          `累计人数：${values[idx]}`,
          raw.increment != null ? `本月新增：${raw.increment}` : ''
        ]
          .filter(Boolean)
          .join('<br/>')
      }
    },
    grid: {
      top: 20,
      left: 50,
      right: 20,
      bottom: 34,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: labels,
      boundaryGap: false,
      axisLine: { lineStyle: { color: '#94a3b8' } },
      axisTick: { show: false },
      axisLabel: { color: '#475569' }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: '#475569' },
      splitLine: { lineStyle: { color: '#e2e8f0' } }
    },
    series: [
      {
        type: 'line',
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        showSymbol: true,
        lineStyle: { width: 3, color: '#2563eb' },
        itemStyle: {
          color: '#1d4ed8',
          borderColor: '#fff',
          borderWidth: 2
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(59,130,246,0.38)' },
            { offset: 1, color: 'rgba(59,130,246,0.05)' }
          ])
        },
        data: values
      }
    ]
  }
}

function render() {
  if (!chartInstance) return
  chartInstance.setOption(buildOption(), true)
  chartInstance.resize()
}

function init() {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  render()
  resizeObserver = new ResizeObserver(() => {
    chartInstance && chartInstance.resize()
  })
  resizeObserver.observe(chartRef.value)
  window.addEventListener('resize', handleWindowResize)
}

function handleWindowResize() {
  chartInstance && chartInstance.resize()
}

watch(() => props.data, render, { deep: true })

onMounted(init)

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleWindowResize)
  if (resizeObserver) {
    resizeObserver.disconnect()
    resizeObserver = null
  }
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
})
</script>

<style scoped>
.area-chart-wrapper {
  width: 100%;
  height: clamp(340px, 42vh, 440px);
  position: relative;
  overflow: visible;
  display: flex;
  flex-direction: column;
}

.chart-title {
  font-size: 16px;
  font-weight: 700;
  text-align: center;
  margin-bottom: 10px;
  font-family: 'DIN Alternate', 'Poppins', 'PingFang SC', 'Segoe UI', Arial, sans-serif;
  background: linear-gradient(90deg, #0284c7, #6366f1 55%, #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}

.area-chart-container {
  flex: 1;
  position: relative;
  overflow: visible;
}
</style>
