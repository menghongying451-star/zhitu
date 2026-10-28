<template>
  <div class="word-cloud-wrapper">
    <div class="chart-title">{{ title }}</div>
    <div ref="chartRef" class="word-cloud-chart"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import * as echarts from 'echarts/core'
import 'echarts-wordcloud'

const props = defineProps({
  data: { type: Array, required: true },
  title: { type: String, default: '' }
})

const chartRef = ref(null)
let chartInstance = null

onMounted(() => {
  chartInstance = echarts.init(chartRef.value)
  renderChart()
})

watch(() => props.data, renderChart, { deep: true })

// 更炫酷且稳定的颜色：按词生成 HSL，高饱和度，随权重增强亮度，并加入微小的色相抖动
function hashString(str = '') {
  let h = 0
  for (let i = 0; i < str.length; i++) {
    h = (h << 5) - h + str.charCodeAt(i)
    h |= 0
  }
  return Math.abs(h)
}
function coolColor(name, value) {
  const base = hashString(name)
  // 基础色相 + 轻微抖动（更和谐）
  const hue = ((base % 360) + (base % 7) - 3) % 360
  const v = Number(value) || 0
  // 降低饱和度和亮度，使颜色更柔和
  const sat = Math.max(65, Math.min(80, 70 + Math.log10(v + 1) * 2))
  const light = Math.max(35, Math.min(55, 40 + Math.log10(v + 1) * 3))
  return `hsl(${hue}, ${sat}%, ${light}%)`
}

function renderChart() {
  if (!chartInstance) return
  const option = {
    backgroundColor: 'transparent',

    tooltip: {},
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        // 调整位置使词云完全居中
        top: 'center',
        left: 'center',
        width: '80%',
        height: '80%',
        sizeRange: [18, 70],
        rotationRange: [-90, 90],
        gridSize: 2,
        drawOutOfBound: false,
        layoutAnimation: true,
        textStyle: {
          color: (params) => coolColor(params.name, params.value)
        },
        emphasis: {
          focus: 'self',
          textStyle: {
            textShadowBlur: 10,
            textShadowColor: '#333'
          }
        },
        data: props.data
      }
    ]
  }
  chartInstance.setOption(option)
}
</script>

<style scoped>
.word-cloud-wrapper {
  width: 100%;
  height: 300px;
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

.word-cloud-chart {
  flex: 1;
}
</style>
