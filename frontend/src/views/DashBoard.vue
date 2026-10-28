<template>
  <div class="page-wrapper scaled" id="dashboard">
    <div class="dashboard-wrapper">
      <div class="dashboard-container">
        <!-- 错误提示 -->
        <div v-if="loadError" class="error-block">
          <p>{{ loadError }}</p>
          <button class="retry-btn" @click="loadDashboard" :disabled="loading">重试</button>
        </div>

        <template v-else>
          <!-- 左侧环形图 -->
          <div class="left-panel">
            <RingChart
              v-if="!loading || learningDirectionData.length"
              :data="learningDirectionData"
              title="学生学习方向占比"
            />
            <div v-else class="skeleton">加载中...</div>

            <RingChart
              v-if="!loading || targetPositionData.length"
              :data="targetPositionData"
              title="学生目标岗位占比"
            />
            <div v-else class="skeleton">加载中...</div>
          </div>

          <!-- 中间区域 -->
          <div class="center-panel">
            <div class="cards">
              <Card
                v-for="(ind, idx) in indicators"
                :key="idx"
                :title="ind.title"
                :value="ind.value"
              />
            </div>

            <div class="decorative-pattern" aria-hidden="true">
              <svg width="100%" height="120" viewBox="0 0 100 30" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stop-color="#60a5fa" stop-opacity="0.8" />
                    <stop offset="50%" stop-color="#bfdbfe" stop-opacity="0.4" />
                    <stop offset="100%" stop-color="#3b82f6" stop-opacity="0.8" />
                  </linearGradient>
                  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%">
                    <feDropShadow
                      dx="0"
                      dy="0"
                      stdDeviation="3"
                      flood-color="#60a5fa"
                      flood-opacity="0.6"
                    />
                    <feDropShadow
                      dx="0"
                      dy="0"
                      stdDeviation="6"
                      flood-color="#bfdbfe"
                      flood-opacity="0.4"
                    />
                  </filter>
                </defs>
                <path fill="none" stroke="url(#grad1)" stroke-width="2" filter="url(#glow)">
                  <animate
                    attributeName="d"
                    dur="10s"
                    repeatCount="indefinite"
                    values="
                      M0 15 Q20 5 40 15 T80 15 T100 15;
                      M0 15 Q20 25 40 15 T80 15 T100 15;
                      M0 15 Q20 10 40 15 T80 15 T100 15;
                      M0 15 Q20 5 40 15 T80 15 T100 15
                    "
                  />
                </path>
                <circle r="3" fill="#bfdbfe" filter="url(#glow)">
                  <animateMotion
                    dur="12s"
                    repeatCount="indefinite"
                    path="M0 15 Q25 5 50 15 T100 15"
                  />
                </circle>
                <circle r="2" fill="#60a5fa" filter="url(#glow)" opacity="0.7">
                  <animateMotion
                    dur="15s"
                    repeatCount="indefinite"
                    path="M10 15 Q30 25 60 15 T90 15"
                  />
                </circle>
                <circle r="1.5" fill="#3b82f6" filter="url(#glow)" opacity="0.5">
                  <animateMotion
                    dur="18s"
                    repeatCount="indefinite"
                    path="M5 15 Q15 10 35 15 T70 15 T100 15"
                  />
                </circle>
              </svg>
            </div>

            <BarChart
              v-if="!loading || projectDomainData.length"
              :data="projectDomainData"
              title="项目领域分布"
              class="center-bar-chart"
            />
            <div v-else class="skeleton center-bar-chart">加载中...</div>
          </div>

          <!-- 右侧区域 -->
          <div class="right-panel">
            <WordCloudChart
              v-if="!loading || hotKeywordsData.length"
              :data="hotKeywordsData"
              title="学生创新实践兴趣词云"
            />
            <div v-else class="skeleton">加载中...</div>

            <AreaChart
              v-if="!loading || userGrowthData.length"
              :data="userGrowthData"
              title="平台总使用人数趋势"
              class="right-area-chart"
            />
            <div v-else class="skeleton right-area-chart">加载中...</div>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
/* 原逻辑未改动 */
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Card from '@/components/Card.vue'
import RingChart from '@/components/RingChart.vue'
import AreaChart from '@/components/AreaChart.vue'
import WordCloudChart from '@/components/WordCloudChart.vue'
import BarChart from '@/components/BarChart.vue'
import { dashboardService } from '@/api/dashboardService.js'

const DEBUG = false

const learningDirectionData = ref([])
const targetPositionData = ref([])
const projectDomainData = ref([])
const hotKeywordsData = ref([])
const userGrowthData = ref([])

const IDX_ONLINE = 0
const IDX_PROJECT_TOTAL = 1
const IDX_ORG_TOTAL = 2
const IDX_QA_COUNT = 3

const indicators = ref([
  { title: '平台在线人数', value: 0 },
  { title: '平台总创建项目数', value: 0 },
  { title: '已入驻企业数', value: 0 },
  { title: '大模型累计问答次数', value: 0 }
])

const loading = ref(false)
const loadError = ref(null)
let aborted = false

function num(v, d = 0) {
  return typeof v === 'number' && !Number.isNaN(v) ? v : d
}

function mapRing(src, countKey) {
  if (!src) return []
  const arr = (src.top_tags || []).map((it) => ({
    name: it.tag_name,
    value: num(it[countKey])
  }))
  if (src.other && num(src.other[countKey]) > 0) {
    arr.push({ name: '其他', value: num(src.other[countKey]) })
  }
  return arr
}

function mapProjectFields(src) {
  if (!src) return []
  const arr = (src.top_tags || []).map((it) => ({
    name: it.tag_name,
    value: num(it.project_count)
  }))
  if (src.other && num(src.other.project_count) > 0) {
    arr.push({ name: '其他', value: num(src.other.project_count) })
  }
  return arr
}

function mapUserRegistration(obj) {
  if (!obj || !Array.isArray(obj.monthly_stats)) return []
  return obj.monthly_stats.map((m) => ({
    label: m.month_display,
    month: m.month,
    cumulative: num(m.cumulative_count),
    increment: num(m.month_new_count),
    value: num(m.cumulative_count)
  }))
}

async function loadStudyDirection() {
  try {
    const data = await dashboardService.getStudyDirectionRatio()
    if (aborted) return
    learningDirectionData.value = mapRing(data, 'student_count')
    DEBUG && console.debug('[StudyDirection]', data)
  } catch (e) {
    console.warn('学习方向失败', e)
  }
}
async function loadTargetJob() {
  try {
    const data = await dashboardService.getTargetJobRatio()
    if (aborted) return
    targetPositionData.value = mapRing(data, 'student_count')
    DEBUG && console.debug('[TargetJob]', data)
  } catch (e) {
    console.warn('目标岗位失败', e)
  }
}
async function loadOnline() {
  try {
    const data = await dashboardService.getOnlineUsers()
    if (aborted) return
    indicators.value[IDX_ONLINE].value = num(data?.online_count)
  } catch (e) {
    console.warn('在线人数失败', e)
  }
}
async function loadProjectsTotal() {
  try {
    const data = await dashboardService.getTotalProjects()
    if (aborted) return
    indicators.value[IDX_PROJECT_TOTAL].value = num(data?.total_projects)
  } catch (e) {
    console.warn('项目总数失败', e)
  }
}
async function loadOrgTotal() {
  try {
    const data = await dashboardService.getCompanyCount()
    if (aborted) return
    indicators.value[IDX_ORG_TOTAL].value = num(data?.total_organizations)
  } catch (e) {
    console.warn('组织数量失败', e)
  }
}
async function loadModelQa() {
  try {
    const data = await dashboardService.getModelQACount()
    if (aborted) return
    indicators.value[IDX_QA_COUNT].value = num(data)
  } catch (e) {
    console.warn('模型问答次数失败', e)
  }
}
async function loadProjectFields() {
  try {
    const data = await dashboardService.getProjectFieldDistribution()
    if (aborted) return
    projectDomainData.value = mapProjectFields(data)
  } catch (e) {
    console.warn('项目领域分布失败', e)
  }
}
async function loadWordCloud() {
  try {
    const data = await dashboardService.getHighFreqTags()
    if (aborted) return
    hotKeywordsData.value = Array.isArray(data) ? data : []
  } catch (e) {
    console.warn('词云失败', e)
  }
}
async function loadUserGrowth() {
  try {
    const data = await dashboardService.getUserGrowthOverTime()
    if (aborted) return
    userGrowthData.value = mapUserRegistration(data)
  } catch (e) {
    console.warn('注册趋势失败', e)
  }
}

async function loadDashboard() {
  if (loading.value) return
  aborted = false
  loading.value = true
  loadError.value = null
  try {
    await Promise.all([
      loadStudyDirection(),
      loadTargetJob(),
      loadOnline(),
      loadProjectsTotal(),
      loadOrgTotal(),
      loadModelQa(),
      loadProjectFields(),
      loadWordCloud(),
      loadUserGrowth()
    ])
  } catch (err) {
    loadError.value = err?.detail || '大屏数据加载失败'
  } finally {
    if (!aborted) loading.value = false
  }
}

onMounted(loadDashboard)
onBeforeUnmount(() => {
  aborted = true
})
</script>

<style scoped>
.page-wrapper {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: radial-gradient(circle at top left, #f0f4f8, #d9e2ec, #bcccdc);
  color: #1e293b;
  overflow-y: auto;
  overflow-x: hidden;
}

.dashboard-wrapper {
  flex: 1;
  height: 100%;
  overflow: visible;
  -webkit-overflow-scrolling: touch;
}

.dashboard-container {
  display: flex;
  padding: 20px;
  gap: 12px;
  min-width: 1200px;
  min-height: 600px;
  box-sizing: border-box;
  position: relative;
  animation: bgPulse 15s ease-in-out infinite alternate;
  background: transparent;
}

.dashboard-container::before {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  z-index: 0;
  background:
    radial-gradient(circle 1.5px, rgba(30, 41, 59, 0.07) 90%, transparent 100%),
    radial-gradient(circle 2px, rgba(147, 197, 253, 0.06) 90%, transparent 100%);
  background-size:
    50px 50px,
    100px 100px;
  background-position:
    0 0,
    25px 25px;
  animation: bgGridMove 60s linear infinite;
  filter: drop-shadow(0 0 3px rgba(147, 197, 253, 0.1));
}

.left-panel,
.center-panel,
.right-panel {
  background: rgba(255, 255, 255, 0.78);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
  z-index: 1;
  backdrop-filter: blur(16px);
  border: 1px solid rgba(147, 197, 253, 0.4);
  box-shadow:
    0 0 15px rgba(96, 165, 250, 0.15),
    inset 0 0 30px rgba(203, 213, 225, 0.5);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  overflow: visible;
}

.left-panel:hover,
.center-panel:hover,
.right-panel:hover {
  transform: translateY(-4px);
  box-shadow:
    0 0 25px rgba(96, 165, 250, 0.3),
    inset 0 0 40px rgba(203, 213, 225, 0.7);
}

.left-panel {
  flex: 0 1 22%;
  min-width: 260px;
}
.center-panel {
  flex: 1 1 54%;
  min-width: 420px;
}
.right-panel {
  flex: 0 1 24%;
  min-width: 300px;
}

.cards {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  grid-template-rows: repeat(2, 1fr);
  gap: 20px;
  z-index: 1;
}

.cards > * {
  min-width: 140px;
  min-height: 100px;
  border-radius: 12px;
  box-shadow:
    0 0 8px rgba(147, 197, 253, 0.6),
    inset 0 0 6px rgba(203, 213, 225, 0.6);
  transition:
    transform 0.3s ease,
    box-shadow 0.3s ease;
  animation:
    glowPulse 3s ease-in-out infinite,
    floatSlight 5s ease-in-out infinite;
  background: #f9fafb;
}

.cards > *:hover {
  transform: scale(1.05) translateY(-6px);
  box-shadow:
    0 0 14px rgba(96, 165, 250, 0.7),
    inset 0 0 10px rgba(96, 165, 250, 0.5);
}

.decorative-pattern {
  width: 100%;
  margin: 8px 0 4px;
  pointer-events: none;
  user-select: none;
  z-index: 2;
  position: relative;
}

.center-bar-chart {
  flex: 1 1 auto;
  min-height: 320px;
  border-radius: 12px;
  box-shadow:
    0 0 16px rgba(96, 165, 250, 0.3),
    inset 0 0 12px rgba(203, 213, 225, 0.7);
  background: rgba(203, 213, 225, 0.25);
  position: relative;
  overflow: visible;
}

.right-area-chart {
  flex: 1 1 auto;
  min-height: 300px;
  border-radius: 12px;
  box-shadow:
    0 0 14px rgba(96, 165, 250, 0.25),
    inset 0 0 10px rgba(203, 213, 225, 0.6);
  background: rgba(203, 213, 225, 0.2);
  position: relative;
  overflow: visible;
}

.skeleton {
  display: flex;
  align-items: center;
  justify-content: center;
  background: repeating-linear-gradient(90deg, #e2e8f0, #e2e8f0 10px, #f1f5f9 10px, #f1f5f9 20px);
  background-size: 200% 100%;
  animation: skeletonMove 1.2s linear infinite;
  border-radius: 12px;
  font-size: 14px;
  color: #475569;
  opacity: 0.85;
}

@keyframes skeletonMove {
  from {
    background-position: 0 0;
  }
  to {
    background-position: -200% 0;
  }
}

.error-block {
  position: absolute;
  top: 40px;
  left: 50%;
  transform: translateX(-50%);
  padding: 16px 24px;
  background: #fee2e2;
  color: #b91c1c;
  border: 1px solid #fca5a5;
  border-radius: 8px;
  z-index: 10;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.retry-btn {
  margin-top: 8px;
  background: #3b82f6;
  color: #fff;
  border: 0;
  padding: 6px 14px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes glowPulse {
  0% {
    box-shadow:
      0 0 8px rgba(147, 197, 253, 0.6),
      inset 0 0 6px rgba(203, 213, 225, 0.6);
  }
  50% {
    box-shadow:
      0 0 16px rgba(147, 197, 253, 0.9),
      inset 0 0 12px rgba(203, 213, 225, 0.9);
  }
  100% {
    box-shadow:
      0 0 8px rgba(147, 197, 253, 0.6),
      inset 0 0 6px rgba(203, 213, 225, 0.6);
  }
}

@keyframes floatSlight {
  0%,
  100% {
    transform: scale(1) translateY(0);
  }
  50% {
    transform: scale(1.03) translateY(-6px);
  }
}

@keyframes bgPulse {
  0% {
    filter: brightness(1);
  }
  100% {
    filter: brightness(1.05);
  }
}
@keyframes bgGridMove {
  0% {
    background-position:
      0 0,
      25px 25px;
  }
  100% {
    background-position:
      50px 50px,
      75px 75px;
  }
}

/* 统一大屏中卡片（统计指标）标题为紫色渐变，字号16，仅对大屏作用 */
.dashboard-container :deep(.card .title) {
  font-size: 16px !important;
  font-weight: 700;
  background: linear-gradient(90deg, #0284c7, #6366f1 55%, #8b5cf6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.2));
}
</style>
