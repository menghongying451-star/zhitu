<template>
  <div class="ring-chart-wrapper" ref="wrapperRef">
    <div class="rc-header">
      <span class="rc-title">{{ title }}</span>
      <span class="rc-total-inline" v-if="showInlineTotal && totalValue !== null">
        {{ totalValue }}
      </span>
    </div>

    <div class="rc-chart-box">
      <div class="rc-chart" ref="chartRef"></div>
      <div class="rc-center-text" v-if="totalValue !== null">
        <div class="rc-center-number">{{ totalValue }}</div>
        <div class="rc-center-label">总计</div>
      </div>
    </div>

    <div class="rc-legend" :class="{ compact: isVeryNarrow }">
      <div
        v-for="(item, idx) in legendItemsLimited"
        :key="item.name + idx"
        class="rc-legend-item"
        :style="{ '--legend-color': item.color }"
      >
        <span class="dot"></span>
        <span class="name" :title="item.name">{{ item.name }}</span>
        <span class="percent">{{ item.percent }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
/**
 * 仅按需求修改：
 * 1. 解决标签说明文字被遮挡（保证文字区域可见）。
 * 2. 缩短指引线（length / length2），让文字靠近环形，避免越界被省略号。
 * 其余逻辑保持不变。
 */
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

echarts.use([PieChart, TooltipComponent, CanvasRenderer])

const props = defineProps({
  title: { type: String, default: '' },
  data: { type: Array, default: () => [] },
  showInlineTotal: { type: Boolean, default: false },
  minSliceAngle: { type: Number, default: 2 }
})

const wrapperRef = ref(null)
const chartRef = ref(null)
let chartInstance = null
let resizeObserver = null

const isVeryNarrow = ref(false)

function evaluateWidth() {
  if (!wrapperRef.value) return
  const w = wrapperRef.value.clientWidth
  isVeryNarrow.value = w < 240
}

const totalValue = computed(() =>
  props.data.reduce((s, d) => s + (typeof d.value === 'number' ? d.value : 0), 0)
)

function formatPercent(v, total) {
  if (!total) return '0'
  const pct = (v / total) * 100
  if (pct >= 10) return pct.toFixed(0)
  if (pct >= 1) return pct.toFixed(1)
  return pct.toFixed(2)
}

function generatePalette(n) {
  const arr = []
  // 根据title判断使用不同的配色方案
  const isTargetPosition = props.title.includes('目标岗位')

  const baseHues = isTargetPosition
    ? [15, 45, 75, 105, 135, 165, 195, 225, 255, 285] // 暖色调配色方案
    : [200, 265, 310, 35, 140, 5, 180, 225, 50, 280] // 原配色方案

  for (let i = 0; i < n; i++) {
    const h1 = baseHues[i % baseHues.length]
    const h2 = (h1 + 25 + ((i * 7) % 40)) % 360
    const c1 = `hsl(${h1}, 78%, 58%)`
    const c2 = `hsl(${h2}, 90%, 48%)`
    arr.push(
      new echarts.graphic.LinearGradient(0, 0, 1, 1, [
        { offset: 0, color: c1 },
        { offset: 1, color: c2 }
      ])
    )
  }
  return arr
}

const legendItems = computed(() => {
  const palette = generatePalette(props.data.length || 1)
  return props.data.map((d, i) => {
    const v = typeof d.value === 'number' ? d.value : 0
    const percent = formatPercent(v, totalValue.value)
    let solidColor = '#64748b'
    if (palette[i]?.colorStops?.[0]) solidColor = palette[i].colorStops[0].color
    return { name: d.name, value: v, percent, color: solidColor }
  })
})

const legendItemsLimited = computed(() => legendItems.value.slice(0, 5))

// 新增：固定每行最多字符数（中文“每行最多五个字”）
const MAX_LABEL_LINE_CHARS = 5

/* ============= 关键修改部分 START ============= */
const EXTRA_LABEL_SPACE = 60 // 减少额外高度，因为不需要外侧标签空间
const MAX_CHART_BASE = 320 // 增大图表基础尺寸
const MIN_CHART_BASE = 200 // 增大最小尺寸
const OUTER_RADIUS = 85 // 增大外半径
const INNER_RADIUS = 55 // 增大内半径

function resizeChartBox() {
  if (!wrapperRef.value || !chartRef.value) return
  const w = wrapperRef.value.clientWidth
  const base = Math.max(MIN_CHART_BASE, Math.min(w, MAX_CHART_BASE))
  const total = base + EXTRA_LABEL_SPACE
  chartRef.value.style.height = total + 'px'
}

function buildOption() {
  const palette = generatePalette(props.data.length || 1)
  const reduced = isVeryNarrow.value
  return {
    backgroundColor: 'transparent',
    tooltip: {
      trigger: 'item',
      appendToBody: true,
      backgroundColor: 'rgba(10,23,46,0.92)',
      borderColor: '#38bdf8',
      borderWidth: 1,
      textStyle: { color: '#f1f5f9', fontSize: 12 },
      padding: [8, 10],
      extraCssText: 'backdrop-filter:blur(4px);box-shadow:0 4px 14px rgba(0,0,0,0.25);',
      formatter: (p) => `
        <div style="line-height:1.5;font-weight:600;">
          ${p.marker} ${p.name}<br/>
          <span style="font-weight:500;">数量：</span>${p.value}<br/>
          <span style="font-weight:500;">占比：</span>${p.percent}%
        </div>`
    },
    series: [
      {
        type: 'pie',
        name: props.title,
        radius: [`${INNER_RADIUS}%`, `${OUTER_RADIUS}%`],
        center: ['50%', '50%'], // 居中显示
        data: props.data,
        minAngle: props.minSliceAngle,
        padAngle: 2,
        startAngle: 90,
        avoidLabelOverlap: false,
        itemStyle: {
          color: (p) => palette[p.dataIndex],
          shadowBlur: 20,
          shadowColor: 'rgba(0,0,0,0.30)'
        },
        label: {
          show: false // 完全隐藏所有标签
        },
        labelLine: {
          show: false // 完全隐藏所有指引线
        },
        emphasis: {
          scale: true,
          scaleSize: 8,
          itemStyle: {
            shadowBlur: 32,
            shadowColor: 'rgba(0,0,0,0.45)'
          }
        }
      }
    ]
  }
}
/* ============= 关键修改部分 END ============= */

function render() {
  if (!chartInstance) return
  chartInstance.setOption(buildOption(), true)
  chartInstance.resize()
}

function init() {
  if (!chartRef.value) return
  chartInstance = echarts.init(chartRef.value)
  resizeChartBox()
  evaluateWidth()
  render()

  resizeObserver = new ResizeObserver(() => {
    resizeChartBox()
    evaluateWidth()
    chartInstance && chartInstance.resize()
  })
  resizeObserver.observe(wrapperRef.value)
  window.addEventListener('resize', handleResize)
}

function handleResize() {
  resizeChartBox()
  evaluateWidth()
  chartInstance && chartInstance.resize()
}

watch(
  () => props.data,
  () => {
    if (!chartInstance) return
    render()
  },
  { deep: true }
)

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
:host,
.ring-chart-wrapper {
  --rc-font:
    'DIN Alternate', 'Poppins', 'PingFang SC', 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
  --rc-number-font: 'DIN Alternate', 'Poppins', 'Roboto', 'Segoe UI', sans-serif;
}

.ring-chart-wrapper {
  position: relative;
  width: 100%;
  padding: 4px 2px 10px;
  display: flex;
  flex-direction: column;
  overflow: visible;
  font-family: var(--rc-font);
}

.rc-header {
  display: flex;
  align-items: baseline;
  justify-content: center;
  gap: 10px;
  padding: 0 4px 4px;
}

.rc-title {
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.5px;
  background: linear-gradient(90deg, #0284c7, #6366f1 55%, #8b5cf6);
  -webkit-background-clip: text;
  color: transparent;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
  user-select: none;
  white-space: nowrap;
}

.rc-total-inline {
  font-size: 18px;
  font-weight: 600;
  color: #0f172a;
  text-shadow:
    0 1px 2px rgba(255, 255, 255, 0.8),
    0 2px 6px rgba(0, 0, 0, 0.15);
  font-family: var(--rc-number-font);
}

.rc-chart-box {
  position: relative;
  width: 100%;
  overflow: visible;
  display: flex;
  justify-content: center;
  align-items: center;
}

.rc-chart {
  width: 100%;
  position: relative;
  overflow: visible;
}

.rc-center-text {
  pointer-events: none;
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  z-index: 5;
  font-family: var(--rc-number-font);
}

.rc-center-number {
  font-size: 34px;
  font-weight: 700;
  line-height: 1;
  background: linear-gradient(90deg, #6366f1, #0ea5e9 70%, #22d3ee);
  -webkit-background-clip: text;
  color: transparent;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.25)) drop-shadow(0 0 6px rgba(99, 102, 241, 0.35));
  letter-spacing: 1px;
}

.rc-center-label {
  font-size: 12px;
  font-weight: 600;
  margin-top: 4px;
  letter-spacing: 0.6px;
  color: #334155;
  text-shadow: 0 1px 1px rgba(255, 255, 255, 0.7);
}

.rc-legend {
  margin-top: 6px;
  display: grid;
  width: 100%;
  gap: 8px 10px;
  grid-template-columns: 1fr; /* 改为单列 */
  overflow: visible;
}

.rc-legend.compact {
  grid-template-columns: 1fr; /* 保持单列，避免横向压缩 */
}

.rc-legend-item {
  --legend-color: #3b82f6;
  display: grid;
  grid-template-columns: 14px 1fr auto; /* 修改为三列：色点、名称、百分比 */
  align-items: center;
  gap: 4px 6px;
  font-size: 12px;
  padding: 4px 8px 4px 6px;
  border-radius: 10px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.75), rgba(227, 242, 255, 0.55));
  border: 1px solid rgba(148, 163, 184, 0.35);
  box-shadow:
    0 2px 6px -1px rgba(0, 0, 0, 0.15),
    0 4px 14px -2px rgba(0, 0, 0, 0.08);
  backdrop-filter: blur(6px);
  font-family: var(--rc-font);
  position: relative;
  overflow: visible;
}

.rc-legend-item .dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--legend-color);
  box-shadow:
    0 0 6px var(--legend-color),
    0 0 10px rgba(0, 0, 0, 0.25);
  border: 1px solid rgba(255, 255, 255, 0.85);
}

.rc-legend-item .name {
  font-weight: 600;
  color: #0f172a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  letter-spacing: 0.4px;
}

.rc-legend-item .value {
  font-weight: 600;
  color: #1e293b;
  font-family: var(--rc-number-font);
  padding: 0 2px;
}

.rc-legend-item .percent {
  font-weight: 600;
  font-family: var(--rc-number-font);
  color: #6366f1;
  letter-spacing: 0.5px;
  text-shadow: 0 0 4px rgba(99, 102, 241, 0.35);
  padding-left: 2px;
}

@media (max-width: 520px) {
  .rc-center-number {
    font-size: 30px;
  }
  .rc-legend {
    gap: 6px 8px;
  }
}
</style>
