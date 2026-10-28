<template>
  <div class="dashboard-container">
    <!-- 动态背景层 -->
    <canvas ref="canvas" class="dynamic-bg"></canvas>

    <!-- 顶部工具栏 -->
    <div class="top-bar">
      <button class="login-btn" @click="goLogin">进入登录页</button>
    </div>

    <!-- 左侧环形图 -->
    <div class="left-panel">
      <RingChart :data="ringData1" title="环形图1" />
      <RingChart :data="ringData2" title="环形图2" />
    </div>

    <!-- 中间区域 -->
    <div class="center-panel">
      <div class="cards">
        <Card :title="indicators[0].title" :value="indicators[0].value" />
        <Card :title="indicators[1].title" :value="indicators[1].value" />
        <Card :title="indicators[2].title" :value="indicators[2].value" />
        <Card :title="indicators[3].title" :value="indicators[3].value" />
      </div>
      <AreaChart :data="areaData" title="平台总使用人数" />
    </div>

    <!-- 右侧区域 -->
    <div class="right-panel">
      <WordCloudChart :data="wordCloudData" title="关键词词云" />
      <BarChart :data="barChartData" title="项目领域分布" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import Card from '@/components/Card.vue'
import RingChart from '@/components/RingChart.vue'
import AreaChart from '@/components/AreaChart.vue'
import WordCloudChart from '@/components/WordCloudChart.vue'
import BarChart from '@/components/BarChart.vue'

const router = useRouter()
const goLogin = () => {
  router.push('/login')
}

const ringData1 = ref([
  { name: '分类A', value: 40 },
  { name: '分类B', value: 60 }
])
const ringData2 = ref([
  { name: '分类X', value: 25 },
  { name: '分类Y', value: 50 },
  { name: '分类Z', value: 25 }
])

const indicators = ref([
  { title: '在线人数', value: 532 },
  { title: '创建的项目数量', value: 124 },
  { title: '加入的公司数量', value: 37 },
  { title: '模型问答次数', value: 9876 }
])

const areaData = ref([
  { date: '1月', value: 120 },
  { date: '2月', value: 200 },
  { date: '3月', value: 150 },
  { date: '4月', value: 80 },
  { date: '5月', value: 70 },
  { date: '6月', value: 110 },
  { date: '7月', value: 130 }
])

const wordCloudData = ref([
  { name: '人工智能', value: 120 },
  { name: '机器学习', value: 100 },
  { name: '大数据', value: 80 },
  { name: '云计算', value: 60 },
  { name: '区块链', value: 40 },
  { name: '物联网', value: 90 },
  { name: '深度学习', value: 70 },
  { name: '算法', value: 50 },
  { name: '自然语言处理', value: 65 },
  { name: '数据挖掘', value: 55 }
])

const barChartData = ref([
  { name: '人工智能', value: 320 },
  { name: '大数据', value: 240 },
  { name: '云计算', value: 180 },
  { name: '区块链', value: 150 },
  { name: '物联网', value: 210 }
])

const canvas = ref(null)
let ctx = null
let animationFrameId = null
let width = 0
let height = 0

class Particle {
  constructor(x, y, vx, vy, radius, color) {
    this.x = x
    this.y = y
    this.vx = vx
    this.vy = vy
    this.radius = radius
    this.color = color
  }

  draw(ctx) {
    ctx.beginPath()
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2)
    ctx.fillStyle = this.color
    ctx.fill()
  }

  update() {
    this.x += this.vx
    this.y += this.vy

    // Bounce on edges
    if (this.x < this.radius || this.x > width - this.radius) this.vx = -this.vx
    if (this.y < this.radius || this.y > height - this.radius) this.vy = -this.vy
  }
}

const particles = []
const PARTICLE_COUNT = 80

function initParticles() {
  particles.length = 0
  for (let i = 0; i < PARTICLE_COUNT; i++) {
    const radius = Math.random() * 2 + 1
    const x = Math.random() * (width - radius * 2) + radius
    const y = Math.random() * (height - radius * 2) + radius
    const vx = (Math.random() - 0.5) * 0.5
    const vy = (Math.random() - 0.5) * 0.5
    const color = 'rgba(96, 165, 250, 0.6)'
    particles.push(new Particle(x, y, vx, vy, radius, color))
  }
}

function connectParticles(ctx) {
  const maxDistance = 120
  for (let a = 0; a < PARTICLE_COUNT; a++) {
    for (let b = a + 1; b < PARTICLE_COUNT; b++) {
      const dx = particles[a].x - particles[b].x
      const dy = particles[a].y - particles[b].y
      const dist = Math.sqrt(dx * dx + dy * dy)
      if (dist < maxDistance) {
        ctx.strokeStyle = `rgba(96, 165, 250, ${1 - dist / maxDistance})`
        ctx.lineWidth = 1
        ctx.beginPath()
        ctx.moveTo(particles[a].x, particles[a].y)
        ctx.lineTo(particles[b].x, particles[b].y)
        ctx.stroke()
      }
    }
  }
}

function animate() {
  ctx.clearRect(0, 0, width, height)
  particles.forEach(p => {
    p.update()
    p.draw(ctx)
  })
  connectParticles(ctx)
  animationFrameId = requestAnimationFrame(animate)
}

function resizeCanvas() {
  width = window.innerWidth
  height = window.innerHeight
  canvas.value.width = width
  canvas.value.height = height
}

onMounted(() => {
  ctx = canvas.value.getContext('2d')
  resizeCanvas()
  window.addEventListener('resize', resizeCanvas)
  initParticles()
  animate()
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeCanvas)
  cancelAnimationFrame(animationFrameId)
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  height: 100vh;
  padding: 20px;
  gap: 12px;
  background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
  position: relative;
  overflow-x: hidden;
  color: #fff;
  box-sizing: border-box;
  max-width: 100vw;
  animation: bgPulse 15s ease-in-out infinite alternate;
}

/* 画布全覆盖做动态背景 */
.dynamic-bg {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  pointer-events: none;
  z-index: 0;
}

@keyframes bgPulse {
  0% {
    background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
  }
  50% {
    background: radial-gradient(circle at bottom right, #1a2a3a, #204a5a, #306478);
  }
  100% {
    background: radial-gradient(circle at top left, #0f2027, #203a43, #2c5364);
  }
}

.top-bar {
  position: fixed;
  top: 10px;
  right: 20px;
  z-index: 10;
}

.login-btn {
  background: linear-gradient(135deg, #4f46e5, #3b82f6);
  border: none;
  color: white;
  padding: 8px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.3s ease, box-shadow 0.3s ease;
  box-shadow: 0 0 8px #3b82f6aa;
}
.login-btn:hover {
  background: linear-gradient(135deg, #3b82f6, #4f46e5);
  box-shadow: 0 0 12px #4f46e5cc;
}

.left-panel,
.center-panel,
.right-panel {
  background: rgba(39, 52, 73, 0.6);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(12px);
  border: 1px solid rgba(96, 165, 250, 0.4);
  box-shadow: 0 0 15px rgba(59, 130, 246, 0.4), inset 0 0 30px rgba(37, 99, 235, 0.25);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.left-panel:hover,
.center-panel:hover,
.right-panel:hover {
  transform: translateY(-4px);
  box-shadow: 0 0 25px rgba(59, 130, 246, 0.8), inset 0 0 40px rgba(37, 99, 235, 0.35);
}

.left-panel {
  flex: 0 1 20%;
  min-width: 220px;
}

.center-panel {
  flex: 1 1 55%;
  min-width: 400px;
}

.right-panel {
  flex: 0 1 25%;
  min-width: 250px;
}

.cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 20px;
  position: relative;
  z-index: 1;
}

.cards > * {
  min-width: 140px;
  min-height: 100px;
  box-shadow: 0 0 8px rgba(96, 165, 250, 0.6), inset 0 0 6px rgba(37, 99, 235, 0.6);
  border-radius: 12px;
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  animation: glowPulse 3s ease-in-out infinite;
}
.cards > *:hover {
  transform: scale(1.05);
  box-shadow: 0 0 14px rgba(59, 130, 246, 1), inset 0 0 10px rgba(59, 130, 246, 1);
}
@keyframes glowPulse {
  0% {
    box-shadow: 0 0 8px rgba(96, 165, 250, 0.6), inset 0 0 6px rgba(37, 99, 235, 0.6);
  }
  50% {
    box-shadow: 0 0 16px rgba(96, 165, 250, 1), inset 0 0 12px rgba(37, 99, 235, 0.8);
  }
  100% {
    box-shadow: 0 0 8px rgba(96, 165, 250, 0.6), inset 0 0 6px rgba(37, 99, 235, 0.6);
  }
}
</style>
