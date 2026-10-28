<template>
  <div class="bar-chart-wrapper">
    <div class="chart-title">{{ title }}</div>
    <div ref="chartRef" class="bar-chart-container"></div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts/core'
import { BarChart } from 'echarts/charts'
import { TooltipComponent, GridComponent, GraphicComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([BarChart, TooltipComponent, GridComponent, CanvasRenderer, GraphicComponent])

const props = defineProps({
  data: { type: Array, default: () => [] },
  title: { type: String, default: '' }
})

const chartRef = ref(null)
let chartInstance = null
let resizeObserver = null

function genPalette(n) {
  const arr = []
  const baseHues = [205, 335, 45, 265, 120, 15, 185, 300, 60, 240]
  for (let i = 0; i < n; i++) {
    const h1 = baseHues[i % baseHues.length]
    const h2 = (h1 + 30 + i * 5) % 360
    const c1 = `hsl(${h1},80%,60%)`
    const c2 = `hsl(${h2},82%,50%)`
    arr.push([c1, c2])
  }
  return arr
}

// 文字换行处理函数
function wrapText(text, maxLength = 4) {
  if (!text) return ''
  const chars = Array.from(String(text))
  const lines = []
  for (let i = 0; i < chars.length; i += maxLength) {
    lines.push(chars.slice(i, i + maxLength).join(''))
  }
  return lines.join('\n')
}

function buildOption() {
  const names = props.data.map((d) => d.name)
  const values = props.data.map((d) => (typeof d.value === 'number' ? d.value : 0))
  const palette = genPalette(values.length || 1)
  const count = values.length
  const barWidth = count <= 4 ? 60 : count <= 6 ? 50 : count <= 8 ? 42 : count <= 10 ? 34 : 28

  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      appendToBody: true,
      backgroundColor: 'rgba(15,23,42,0.92)',
      borderColor: '#38bdf8',
      borderWidth: 1,
      textStyle: {
        color: '#f1f5f9',
        fontSize: 13,
        fontFamily: 'DIN Alternate, Poppins, "PingFang SC", "Segoe UI", Arial, sans-serif'
      },
      padding: [8, 10],
      extraCssText: 'backdrop-filter:blur(4px);box-shadow:0 4px 14px rgba(0,0,0,0.25);',
      formatter(params) {
        const p = params[0]
        return `
          <div style="line-height:1.5;font-weight:600;">
            ${p.axisValue}<br/>
            <span style="font-weight:500;">数量：</span>${p.value}
          </div>
        `
      }
    },
    grid: { top: 20, left: 60, right: 34, bottom: 80, containLabel: true },
    xAxis: {
      type: 'category',
      data: names,
      axisLine: { lineStyle: { color: '#94a3b8' } },
      axisTick: { show: false },
      axisLabel: {
        color: '#0f172a',
        fontWeight: 700,
        fontSize: 14,
        fontFamily: 'DIN Alternate, Poppins, "PingFang SC", "Segoe UI", Arial, sans-serif',
        lineHeight: 16,
        margin: 14,
        shadowColor: 'rgba(255,255,255,0.85)',
        shadowBlur: 2,
        formatter: function (value) {
          return wrapText(value, 4) // 每4个字符换行
        },
        interval: 0, // 强制显示所有标签
        rotate: 0, // 不旋转
        overflow: 'break' // 允许换行
      }
    },
    yAxis: {
      type: 'value',
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: {
        color: '#0f172a',
        fontWeight: 700,
        fontSize: 14,
        fontFamily: 'DIN Alternate, Poppins, "PingFang SC", "Segoe UI", Arial, sans-serif',
        shadowColor: 'rgba(255,255,255,0.85)',
        shadowBlur: 2
      },
      splitLine: { lineStyle: { color: 'rgba(148,163,184,0.28)' } }
    },
    series: [
      {
        type: 'bar',
        data: values,
        barWidth,
        barCategoryGap: '18%',
        label: {
          show: true,
          position: 'top',
          fontSize: 16,
          fontWeight: 700,
          color: '#0f172a',
          fontFamily: 'DIN Alternate, Poppins, "PingFang SC", "Segoe UI", Arial, sans-serif',
          textBorderColor: 'rgba(255,255,255,0.7)',
          textBorderWidth: 2,
          shadowColor: 'rgba(0,0,0,0.15)',
          shadowBlur: 2
        },
        itemStyle: {
          borderRadius: [10, 10, 6, 6],
          color: (params) => {
            const [c1, c2] = palette[params.dataIndex % palette.length]
            return new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: c1 },
              { offset: 1, color: c2 }
            ])
          },
          shadowBlur: 14,
          shadowColor: 'rgba(0,0,0,0.22)',
          shadowOffsetY: 4
        },
        emphasis: {
          itemStyle: {
            shadowBlur: 32,
            shadowColor: 'rgba(0,0,0,0.45)',
            borderColor: 'rgba(255,255,255,0.9)',
            borderWidth: 1
          },
          label: {
            color: '#1e293b',
            textBorderColor: 'rgba(255,255,255,0.95)',
            textBorderWidth: 2
          }
        },
        animationEasing: 'cubicOut',
        animationDuration: 700,
        animationDelay: (idx) => idx * 50
      }
    ]
  }
}

function render() {
  if (!chartInstance) return
  chartInstance.setOption(buildOption(), true)
}

function init() {
  if (!chartRef.value) return
  // 新增：确保容器宽高不为0再初始化
  const el = chartRef.value
  const width = el.clientWidth
  const height = el.clientHeight
  if (width === 0 || height === 0) {
    // 如果宽高为0，延迟100ms重试初始化
    setTimeout(init, 100)
    return
  }
  chartInstance = echarts.init(el)
  render()
  resizeObserver = new ResizeObserver(() => chartInstance && chartInstance.resize())
  resizeObserver.observe(el)
  window.addEventListener('resize', handleResize)
}

function handleResize() {
  chartInstance && chartInstance.resize()
}

watch(() => props.data, render, { deep: true })

onMounted(init)

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
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
.bar-chart-wrapper {
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

.bar-chart-container {
  flex: 1;
  position: relative;
  overflow: visible;
}
</style>
