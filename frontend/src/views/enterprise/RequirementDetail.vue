<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { requirementService, projectScoreService } from '@/api'
import { useUserStore } from '@/stores'
import {
  faArrowLeft,
  faDownload,
  faEye,
  faFile,
  faFileAlt,
  faImage,
  faFileCode,
  faFilePdf,
  faFileArchive,
  faChevronRight,
  faCalendarAlt,
  faEdit,
  faExclamationTriangle,
  faSpinner,
  faCheckCircle,
  faCubes,
  faUserPlus,
  faBuilding,
  faClock,
  faUsers,
  faHandsHelping,
  faProjectDiagram,
  faCrown,
  faUserFriends,
  faAward,
  faClipboardList,
  faPercentage,
  faTimes,
  faTrophy,
  faMedal,
  faStar
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faArrowLeft,
  faDownload,
  faEye,
  faFile,
  faFileAlt,
  faImage,
  faFileCode,
  faFilePdf,
  faFileArchive,
  faChevronRight,
  faCalendarAlt,
  faEdit,
  faExclamationTriangle,
  faSpinner,
  faCheckCircle,
  faCubes,
  faUserPlus,
  faBuilding,
  faClock,
  faUsers,
  faHandsHelping,
  faProjectDiagram,
  faCrown,
  faUserFriends,
  faAward,
  faClipboardList,
  faPercentage,
  faTimes,
  faTrophy,
  faMedal,
  faStar
)

// 路由相关
const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 需求ID
const requirementId = computed(() => route.params.id)

// Tab状态
const activeTab = ref('requirement')

// 需求数据
const requirementData = reactive({
  id: '',
  title: '',
  brief: '',
  description: '',
  tag1: [],
  tag2: [],
  status: '',
  organization: { id: '', name: '', logo: '', status: '' },
  publish_people: '',
  finish_time: '',
  budget: '',
  people_count: '',
  support_provided: '', // 新增支持提供字段
  applications: 0,
  views: 0,
  joined_count: 0,
  resources: [],
  files: [],
  related_projects: [],
  total_project_members: 0,
  evaluation_criteria: null, // 新增评分标准字段
  evaluation_published: false, // 新增评分公示状态字段
  created_at: '',
  updated_at: ''
})

// 评分标准详情数据
const evaluationCriteriaDetail = reactive({
  id: '',
  name: '',
  description: '',
  status: '',
  indicators: [],
  total_weight: 0,
  creator: null,
  organization: null,
  created_at: '',
  updated_at: ''
})

// 项目排名数据
const projectRankingData = reactive({
  requirement: {
    id: '',
    title: '',
    evaluation_published: false
  },
  projects: [],
  total_count: 0
})

// 状态管理
const loading = ref(true)
const notFound = ref(false)
const error = ref('')
const loadingEvaluationCriteria = ref(false)
const showRankingModal = ref(false)
const loadingRanking = ref(false)
const publishingRanking = ref(false)

// 更新需求状态选项以匹配后端返回的状态
const requirementStatus = {
  under_review: { label: '审核中', color: '#FAAD14' },
  review_failed: { label: '审核失败', color: '#FF4D4F' },
  in_progress: { label: '进行中', color: '#165DFF' },
  completed: { label: '已完成', color: '#86909C' },
  paused: { label: '已暂停', color: '#F53F3F' }
}

// 项目状态映射
const projectStatus = {
  recruiting: { label: '招募中', color: '#52C41A' },
  in_progress: { label: '进行中', color: '#165DFF' },
  completed: { label: '已完成', color: '#86909C' },
  suspended: { label: '已暂停', color: '#FAAD14' },
  cancelled: { label: '已取消', color: '#FF4D4F' }
}

// 获取需求状态信息
const requirementStatusInfo = computed(() => {
  return requirementStatus[requirementData.status] || { label: '未知', color: '#86909C' }
})

// 获取项目状态信息
const getProjectStatusInfo = (status) => {
  return projectStatus[status] || { label: '未知', color: '#86909C' }
}

// 检查编辑权限
const canEdit = computed(() => {
  const user = userStore.user
  if (!user || !requirementData.organization.id) return false

  // 检查是否是发布者
  if (requirementData.publish_people === user.username) return true

  // 检查组织权限
  const userOrgId = user.company_profile?.organization?.id
  const userPermission = user.company_profile?.permission

  if (userOrgId == requirementData.organization.id) {
    return userPermission === 'owner' || userPermission === 'admin'
  }

  return false
})

// 检查是否可以管理评分
const canManageEvaluation = computed(() => {
  return canEdit.value && requirementData.evaluation_criteria
})

// 获取文件图标
const getFileIcon = (fileName) => {
  // 检查 fileName 是否存在且是字符串
  if (!fileName || typeof fileName !== 'string') {
    return ['fas', 'file']
  }
  const ext = fileName.split('.').pop()?.toLowerCase()

  const iconMap = {
    // 代码文件
    js: ['fas', 'file-code'],
    ts: ['fas', 'file-code'],
    vue: ['fas', 'file-code'],
    jsx: ['fas', 'file-code'],
    tsx: ['fas', 'file-code'],
    py: ['fas', 'file-code'],
    java: ['fas', 'file-code'],
    cpp: ['fas', 'file-code'],
    c: ['fas', 'file-code'],
    go: ['fas', 'file-code'],
    rs: ['fas', 'file-code'],
    php: ['fas', 'file-code'],
    rb: ['fas', 'file-code'],
    swift: ['fas', 'file-code'],
    kt: ['fas', 'file-code'],
    html: ['fas', 'file-code'],
    css: ['fas', 'file-code'],
    scss: ['fas', 'file-code'],
    sass: ['fas', 'file-code'],
    json: ['fas', 'file-code'],
    xml: ['fas', 'file-code'],
    yaml: ['fas', 'file-code'],
    yml: ['fas', 'file-code'],

    // 图片文件
    jpg: ['fas', 'image'],
    jpeg: ['fas', 'image'],
    png: ['fas', 'image'],
    gif: ['fas', 'image'],
    svg: ['fas', 'image'],
    webp: ['fas', 'image'],
    bmp: ['fas', 'image'],
    ico: ['fas', 'image'],

    // 文档文件
    pdf: ['fas', 'file-pdf'],
    doc: ['fas', 'file-alt'],
    docx: ['fas', 'file-alt'],
    txt: ['fas', 'file-alt'],
    md: ['fas', 'file-alt'],
    rtf: ['fas', 'file-alt'],

    // 压缩文件
    zip: ['fas', 'file-archive'],
    rar: ['fas', 'file-archive'],
    '7z': ['fas', 'file-archive'],
    tar: ['fas', 'file-archive'],
    gz: ['fas', 'file-archive']
  }

  return iconMap[ext] || ['fas', 'file']
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化数字
const formatNumber = (num) => {
  const number = parseInt(num)
  if (number >= 1000000) {
    return (number / 1000000).toFixed(1) + 'M'
  } else if (number >= 1000) {
    return (number / 1000).toFixed(1) + 'K'
  }
  return number.toString()
}

// 格式化时间
const formatDateTime = (dateTime) => {
  if (!dateTime) return '未知'
  const date = new Date(dateTime)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 格式化日期
const formatDate = (dateStr) => {
  if (!dateStr) return '未设定'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 获取排名等级颜色
const getRankLevelColor = (level) => {
  const levelColors = {
    'A+': '#ff4d4f',
    A: '#ff7a45',
    'B+': '#faad14',
    B: '#52c41a',
    'C+': '#13c2c2',
    C: '#165dff',
    'D+': '#722ed1',
    D: '#86909c'
  }
  return levelColors[level] || '#86909c'
}

// 下载单个文件
const downloadFile = (file) => {
  window.open(file.url, '_blank')
}

// 编辑需求
const editRequirement = () => {
  router.push(`/enterprise/requirement/edit/${requirementData.id}`)
}

// 查看项目详情
const viewProjectDetail = (projectId) => {
  router.push(`/enterprise/project-details/${projectId}`)
}

// 返回需求列表
const goBack = () => {
  router.back()
}

// Tab切换
const switchTab = (tab) => {
  activeTab.value = tab
}

// 计算关联项目统计信息
const projectStats = computed(() => {
  const projects = requirementData.related_projects || []
  const stats = {
    total: projects.length,
    recruiting: projects.filter((p) => p.status === 'recruiting').length,
    in_progress: projects.filter((p) => p.status === 'in_progress').length,
    completed: projects.filter((p) => p.status === 'completed').length,
    suspended: projects.filter((p) => p.status === 'suspended').length,
    cancelled: projects.filter((p) => p.status === 'cancelled').length
  }
  return stats
})

// 加载评分标准详情
const loadEvaluationCriteriaDetail = async (criteriaId) => {
  try {
    loadingEvaluationCriteria.value = true
    const response = await projectScoreService.getScoreStandardDetail(criteriaId)

    if (response?.data) {
      Object.assign(evaluationCriteriaDetail, response.data)
    }
  } catch (err) {
    console.error('加载评分标准详情失败:', err)
  } finally {
    loadingEvaluationCriteria.value = false
  }
}

// 获取项目排名
const getProjectRanking = async () => {
  try {
    loadingRanking.value = true
    const response = await projectScoreService.getProjectRanking(requirementId.value)

    if (response?.data) {
      Object.assign(projectRankingData, response.data)
    }
  } catch (err) {
    console.error('获取项目排名失败:', err)
    // 可以在这里添加错误提示
  } finally {
    loadingRanking.value = false
  }
}

// 查看评分详情
const viewRankingDetails = async () => {
  await getProjectRanking()
  showRankingModal.value = true
}

// 公示项目评分
const publishRanking = async () => {
  try {
    publishingRanking.value = true

    const response = await projectScoreService.publishProjectRanking(requirementId.value)

    if (response) {
      // 更新评分公示状态
      requirementData.evaluation_published = true

      // 可以在这里添加成功提示
      console.log('评分公示成功')
    }
  } catch (err) {
    console.error('公示评分失败:', err)
    // 可以在这里添加错误提示
  } finally {
    publishingRanking.value = false
  }
}

// 关闭排名弹窗
const closeRankingModal = () => {
  showRankingModal.value = false
}

// 加载需求数据
const loadRequirementData = async (id) => {
  try {
    loading.value = true
    error.value = ''

    const response = await requirementService.getRequirementDetail(id)

    if (response?.data) {
      Object.assign(requirementData, response.data)

      // 如果有评分标准，则加载详情
      if (requirementData.evaluation_criteria?.id) {
        await loadEvaluationCriteriaDetail(requirementData.evaluation_criteria.id)
      }
    } else {
      notFound.value = true
    }
  } catch (err) {
    console.error('加载需求详情失败:', err)
    error.value = '加载需求详情失败'
    notFound.value = true
  } finally {
    loading.value = false
  }
}

// 增加浏览量
const incrementViews = async (id) => {
  try {
    // 这里可以调用增加浏览量的API
    // await requirementService.incrementViews(id)
  } catch (error) {
    console.error('增加浏览量失败:', error)
  }
}

const requirementDetailRef = ref(null)
// 生命周期
onMounted(async () => {
  if (!requirementId.value) {
    router.push('/enterprise/requirement-management')
    return
  }

  await loadRequirementData(requirementId.value)

  // 增加浏览量
  if (!notFound.value && !error.value) {
    incrementViews(requirementId.value)
  }

  requirementDetailRef.value.scrollIntoView()
})
</script>

<template>
  <div class="requirement-detail" ref="requirementDetailRef">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-screen">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>加载需求详情中...</p>
      </div>
    </div>

    <!-- 404状态 -->
    <div v-else-if="notFound || error" class="not-found-screen">
      <div class="not-found-content">
        <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" class="not-found-icon" />
        <h2>{{ error || '需求不存在' }}</h2>
        <p>{{ error ? '加载需求详情时出现错误' : '您要查看的需求不存在或已被删除' }}</p>
        <button @click="goBack" class="btn-primary">
          <FontAwesomeIcon :icon="['fas', 'arrow-left']" class="mr-2" />
          返回需求列表
        </button>
      </div>
    </div>

    <!-- 正常内容 -->
    <template v-else>
      <!-- 面包屑导航 -->
      <div class="breadcrumb-nav">
        <div class="breadcrumb-container">
          <div class="breadcrumb-content">
            <button @click="goBack" class="back-btn">
              <FontAwesomeIcon :icon="['fas', 'arrow-left']" class="back-icon" />
              <span>返回</span>
            </button>
            <div class="breadcrumb-items">
              <a href="/enterprise/requirement-management" class="breadcrumb-link">需求管理</a>
              <FontAwesomeIcon :icon="['fas', 'chevron-right']" class="breadcrumb-separator" />
              <span class="breadcrumb-current">{{ requirementData.title }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 主内容区 -->
      <main class="main-content">
        <div class="content-container">
          <!-- 页面标题和操作区 -->
          <div class="page-header">
            <div class="page-header-left">
              <div class="title-section">
                <div class="title-row">
                  <h1 class="page-title">{{ requirementData.title }}</h1>
                  <span
                    class="status-badge"
                    :style="{ backgroundColor: requirementStatusInfo.color }"
                  >
                    {{ requirementStatusInfo.label }}
                  </span>
                </div>
                <p class="page-subtitle">
                  {{ requirementData.brief }}
                </p>
                <div class="organization-info">
                  <FontAwesomeIcon :icon="['fas', 'building']" class="org-icon" />
                  <span>{{ requirementData.organization.name }}</span>
                  <span
                    class="org-status"
                    v-if="requirementData.organization.status === 'verified'"
                  >
                    <FontAwesomeIcon :icon="['fas', 'check-circle']" class="verified-icon" />
                    已认证
                  </span>
                </div>
                <!-- 统计信息 -->
                <div class="stats-info">
                  <span class="stat-item">
                    <FontAwesomeIcon :icon="['fas', 'eye']" class="stat-icon" />
                    {{ formatNumber(requirementData.views) }} 浏览
                  </span>
                  <span class="stat-item">
                    <FontAwesomeIcon :icon="['fas', 'users']" class="stat-icon" />
                    {{ requirementData.total_project_members }} 已参与
                  </span>
                  <span class="stat-item">
                    <FontAwesomeIcon :icon="['fas', 'clock']" class="stat-icon" />
                    截止 {{ formatDate(requirementData.finish_time) }}
                  </span>
                </div>
              </div>
            </div>

            <div class="page-header-actions">
              <button v-if="canEdit" @click="editRequirement" class="action-btn secondary">
                <FontAwesomeIcon :icon="['fas', 'edit']" class="btn-icon" />
                <span>编辑</span>
              </button>
              <!-- <button
                @click="applyRequirement"
                class="action-btn primary"
                :disabled="applying || !canApply"
              >
                <FontAwesomeIcon
                  :icon="applying ? ['fas', 'spinner'] : ['fas', 'user-plus']"
                  class="btn-icon"
                  :class="{ 'fa-spin': applying }"
                />
                <span>{{ getApplyButtonText }}</span>
              </button> -->
            </div>
          </div>

          <!-- Tab导航 -->
          <div class="tab-navigation">
            <div class="tab-nav-container">
              <button
                @click="switchTab('requirement')"
                :class="['tab-item', { active: activeTab === 'requirement' }]"
              >
                <FontAwesomeIcon :icon="['fas', 'file-alt']" class="tab-icon" />
                <span>需求信息</span>
              </button>
              <button
                @click="switchTab('projects')"
                :class="['tab-item', { active: activeTab === 'projects' }]"
              >
                <FontAwesomeIcon :icon="['fas', 'project-diagram']" class="tab-icon" />
                <span>关联项目</span>
                <span class="project-count" v-if="requirementData.related_projects.length > 0">
                  {{ requirementData.related_projects.length }}
                </span>
              </button>
            </div>
          </div>

          <!-- Tab内容区 -->
          <div class="tab-content">
            <!-- 需求信息Tab -->
            <div v-if="activeTab === 'requirement'" class="content-grid">
              <!-- 左侧主要内容 -->
              <div class="main-column">
                <!-- 需求描述 -->
                <div class="description-section">
                  <h2 class="section-title">需求描述</h2>
                  <div class="description-content">
                    {{ requirementData.description }}
                  </div>
                </div>

                <!-- 评分标准 -->
                <div class="evaluation-criteria-section" v-if="requirementData.evaluation_criteria">
                  <div class="section-header">
                    <h2 class="section-title">
                      <FontAwesomeIcon :icon="['fas', 'award']" class="section-icon" />
                      评分标准
                    </h2>
                    <div
                      class="evaluation-badge"
                      v-if="evaluationCriteriaDetail.status === 'active'"
                    >
                      <FontAwesomeIcon :icon="['fas', 'check-circle']" class="badge-icon" />
                      <span>已启用</span>
                    </div>
                  </div>

                  <div v-if="loadingEvaluationCriteria" class="loading-criteria">
                    <FontAwesomeIcon :icon="['fas', 'spinner']" class="fa-spin loading-icon" />
                    <span>加载评分标准中...</span>
                  </div>

                  <div v-else-if="evaluationCriteriaDetail.id" class="criteria-content">
                    <!-- 评分标准基本信息 -->
                    <div class="criteria-summary">
                      <div class="summary-row">
                        <h3 class="criteria-name">{{ evaluationCriteriaDetail.name }}</h3>
                        <div class="criteria-stats">
                          <span class="stat-item">
                            <FontAwesomeIcon :icon="['fas', 'clipboard-list']" class="stat-icon" />
                            {{ evaluationCriteriaDetail.indicators.length }}项指标
                          </span>
                          <span class="stat-item">
                            <FontAwesomeIcon :icon="['fas', 'percentage']" class="stat-icon" />
                            总权重{{ evaluationCriteriaDetail.total_weight }}%
                          </span>
                        </div>
                      </div>
                      <p class="criteria-description">{{ evaluationCriteriaDetail.description }}</p>
                    </div>

                    <!-- 评分指标 -->
                    <div class="indicators-list">
                      <div
                        v-for="(indicator, index) in evaluationCriteriaDetail.indicators"
                        :key="indicator.id"
                        class="indicator-item"
                      >
                        <div class="indicator-order">{{ index + 1 }}</div>
                        <div class="indicator-content">
                          <div class="indicator-header">
                            <h5 class="indicator-name">
                              {{ indicator.name }}
                              <span class="required-badge" v-if="indicator.is_required">必填</span>
                            </h5>
                            <div class="indicator-stats">
                              <span class="stat-tag weight">{{ indicator.weight }}%</span>
                              <span class="stat-tag score">满分{{ indicator.max_score }}</span>
                            </div>
                          </div>
                          <p class="indicator-description">{{ indicator.description }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 支持提供信息 -->
                <div class="support-section" v-if="requirementData.support_provided">
                  <h2 class="section-title">提供支持</h2>
                  <div class="support-content">
                    <FontAwesomeIcon :icon="['fas', 'hands-helping']" class="support-icon" />
                    <p>{{ requirementData.support_provided }}</p>
                  </div>
                </div>

                <!-- 附件文件 -->
                <div class="files-section">
                  <div class="section-header">
                    <h2 class="section-title">附件文件</h2>
                  </div>

                  <div class="file-list" v-if="requirementData.files.length > 0">
                    <div v-for="file in requirementData.files" :key="file.id" class="file-item">
                      <div class="file-info">
                        <div class="file-icon">
                          <FontAwesomeIcon :icon="getFileIcon(file.name)" class="file-icon-inner" />
                        </div>
                        <div class="file-details">
                          <div class="file-name">{{ file.name }}</div>
                          <div class="file-meta">
                            {{ formatFileSize(file.size) }}
                            <span class="file-time">
                              {{ formatDateTime(file.created_at) }}
                            </span>
                          </div>
                        </div>
                      </div>

                      <div class="file-actions">
                        <button
                          @click="downloadFile(file)"
                          class="file-action-btn download"
                          title="下载文件"
                        >
                          <FontAwesomeIcon :icon="['fas', 'download']" />
                          <span>下载</span>
                        </button>
                      </div>
                    </div>
                  </div>

                  <div v-else class="no-files">
                    <p>暂无附件文件</p>
                  </div>
                </div>

                <!-- 相关资源 -->
                <div class="resources-section">
                  <div class="section-header">
                    <h2 class="section-title">关联资源</h2>
                  </div>

                  <div class="resource-list" v-if="requirementData.resources.length > 0">
                    <div
                      v-for="resource in requirementData.resources"
                      :key="resource.id"
                      class="resource-item"
                    >
                      <div class="resource-info">
                        <div class="resource-icon">
                          <FontAwesomeIcon :icon="['fas', 'cubes']" class="resource-icon-inner" />
                        </div>
                        <div class="resource-details">
                          <div class="resource-name">{{ resource.title }}</div>
                          <div class="resource-meta">
                            {{ resource.type }}
                          </div>
                        </div>
                      </div>

                      <div class="resource-actions">
                        <button
                          @click="router.push(`/enterprise/resource/detail/${resource.id}`)"
                          class="resource-action-btn"
                          title="查看资源"
                        >
                          <FontAwesomeIcon :icon="['fas', 'eye']" />
                          <span>查看</span>
                        </button>
                      </div>
                    </div>
                  </div>

                  <div v-else class="no-resources">
                    <p>暂无关联资源</p>
                  </div>
                </div>
              </div>

              <!-- 右侧侧边栏 -->
              <div class="sidebar-column">
                <!-- 需求信息 -->
                <div class="info-card">
                  <h2 class="card-title">需求信息</h2>

                  <div class="info-list">
                    <div class="info-item">
                      <span class="info-label">项目预算</span>
                      <span class="info-value">{{
                        requirementData.budget ? requirementData.budget + '万元' : '未设置'
                      }}</span>
                    </div>

                    <div class="info-item">
                      <span class="info-label">团队规模</span>
                      <span class="info-value">{{
                        requirementData.people_count
                          ? requirementData.people_count + '人'
                          : '未设置'
                      }}</span>
                    </div>

                    <div class="info-item">
                      <span class="info-label">完成时间</span>
                      <span class="info-value">{{ formatDate(requirementData.finish_time) }}</span>
                    </div>

                    <div class="info-item">
                      <span class="info-label">发布时间</span>
                      <span class="info-value">{{
                        formatDateTime(requirementData.created_at)
                      }}</span>
                    </div>

                    <div
                      class="info-item"
                      v-if="requirementData.updated_at !== requirementData.created_at"
                    >
                      <span class="info-label">最后更新</span>
                      <span class="info-value">{{
                        formatDateTime(requirementData.updated_at)
                      }}</span>
                    </div>

                    <div class="info-item">
                      <span class="info-label">发布人</span>
                      <span class="info-value">{{ requirementData.publish_people }}</span>
                    </div>

                    <div class="info-item">
                      <span class="info-label">发布方</span>
                      <div class="org-display">
                        <img
                          v-if="requirementData.organization.logo"
                          :src="requirementData.organization.logo"
                          alt="组织logo"
                          class="org-logo-small"
                        />
                        <FontAwesomeIcon
                          v-else
                          :icon="['fas', 'building']"
                          class="org-icon-small"
                        />
                        <span>{{ requirementData.organization.name }}</span>
                      </div>
                    </div>
                  </div>
                </div>

                <!-- 技术标签 -->
                <div class="tags-card" v-if="requirementData.tag1.length > 0">
                  <div class="card-header">
                    <h2 class="card-title">技术标签</h2>
                  </div>

                  <div class="tags-display">
                    <span v-for="tag in requirementData.tag1" :key="tag.id" class="tag primary-tag">
                      {{ tag.name.trim() }}
                    </span>
                  </div>
                </div>

                <!-- 技能标签 -->
                <div class="tags-card" v-if="requirementData.tag2.length > 0">
                  <div class="card-header">
                    <h2 class="card-title">技能标签</h2>
                  </div>

                  <div class="tags-display">
                    <span
                      v-for="tag in requirementData.tag2"
                      :key="tag.id"
                      class="tag secondary-tag"
                    >
                      {{ tag.name.trim() }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- 关联项目Tab -->
            <div v-else-if="activeTab === 'projects'" class="projects-tab-content">
              <!-- 项目统计 -->
              <div class="project-stats" v-if="requirementData.related_projects.length > 0">
                <div class="stats-grid">
                  <div class="stat-card">
                    <div class="stat-number">{{ projectStats.total }}</div>
                    <div class="stat-label">总项目数</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-number">{{ requirementData.total_project_members }}</div>
                    <div class="stat-label">参与人数</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-number">{{ projectStats.in_progress }}</div>
                    <div class="stat-label">进行中</div>
                  </div>
                  <div class="stat-card">
                    <div class="stat-number">{{ projectStats.completed }}</div>
                    <div class="stat-label">已完成</div>
                  </div>
                </div>
              </div>

              <!-- 项目列表 -->
              <div class="projects-section">
                <div class="section-header">
                  <h2 class="section-title">关联项目列表</h2>
                  <!-- 评分管理按钮 -->
                  <div class="section-actions" v-if="canManageEvaluation">
                    <button
                      v-if="requirementData.evaluation_published"
                      @click="viewRankingDetails"
                      class="ranking-action-btn view"
                      :disabled="loadingRanking"
                    >
                      <FontAwesomeIcon
                        :icon="loadingRanking ? ['fas', 'spinner'] : ['fas', 'trophy']"
                        class="btn-icon"
                        :class="{ 'fa-spin': loadingRanking }"
                      />
                      <span>查看评分</span>
                    </button>
                    <button
                      v-else
                      @click="publishRanking"
                      class="ranking-action-btn publish"
                      :disabled="publishingRanking"
                      title="请确保已为所有项目评分"
                    >
                      <FontAwesomeIcon
                        :icon="publishingRanking ? ['fas', 'spinner'] : ['fas', 'medal']"
                        class="btn-icon"
                        :class="{ 'fa-spin': publishingRanking }"
                      />
                      <span>公示评分</span>
                    </button>
                  </div>
                </div>

                <div class="project-list" v-if="requirementData.related_projects.length > 0">
                  <div
                    v-for="project in requirementData.related_projects"
                    :key="project.id"
                    class="project-card"
                  >
                    <div class="project-header">
                      <div class="project-title-row">
                        <h3 class="project-title">{{ project.title }}</h3>
                        <span
                          class="project-status-badge"
                          :style="{ backgroundColor: getProjectStatusInfo(project.status).color }"
                        >
                          {{ getProjectStatusInfo(project.status).label }}
                        </span>
                      </div>
                      <div class="project-meta">
                        <span class="project-date">
                          <FontAwesomeIcon :icon="['fas', 'calendar-alt']" class="meta-icon" />
                          创建于 {{ formatDate(project.created_at) }}
                        </span>
                      </div>
                    </div>

                    <div class="project-body">
                      <!-- 项目负责人 -->
                      <div class="project-leader">
                        <div class="leader-info">
                          <FontAwesomeIcon :icon="['fas', 'crown']" class="leader-icon" />
                          <span class="leader-label">项目负责人：</span>
                          <span class="leader-name">{{ project.leader.username }}</span>
                          <span class="leader-id">({{ project.leader.school.name }})</span>
                        </div>
                      </div>

                      <!-- 团队成员 -->
                      <div class="project-members" v-if="project.participants.length > 0">
                        <div class="members-header">
                          <FontAwesomeIcon :icon="['fas', 'user-friends']" class="members-icon" />
                          <span class="members-label"
                            >团队成员 ({{ project.participants.length }}人)</span
                          >
                        </div>
                        <div class="members-list">
                          <div
                            v-for="member in project.participants"
                            :key="member.id"
                            class="member-item"
                          >
                            <div class="member-avatar">
                              <el-avatar :src="member.avatar" :size="32" alt="Member Avatar">
                                {{ member.username.charAt(0).toUpperCase() }}
                              </el-avatar>
                            </div>
                            <div class="member-info">
                              <div class="member-name">{{ member.username }}</div>
                              <div class="member-id">{{ member.school.name }}</div>
                            </div>
                            <div class="member-role">
                              <span
                                :class="[
                                  'role-badge',
                                  member.role === 'leader' ? 'leader' : 'member'
                                ]"
                              >
                                {{ member.role === 'leader' ? '负责人' : '成员' }}
                              </span>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div class="project-footer">
                      <button @click="viewProjectDetail(project.id)" class="project-action-btn">
                        <FontAwesomeIcon :icon="['fas', 'eye']" />
                        <span>查看详情</span>
                      </button>
                    </div>
                  </div>
                </div>

                <div v-else class="no-projects">
                  <div class="no-projects-content">
                    <FontAwesomeIcon :icon="['fas', 'project-diagram']" class="no-projects-icon" />
                    <h3>暂无关联项目</h3>
                    <p>该需求目前还没有关联的项目</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- 项目排名弹窗 -->
      <div v-if="showRankingModal" class="modal-overlay" @click="closeRankingModal">
        <div class="ranking-modal" @click.stop>
          <div class="modal-header">
            <h2 class="modal-title">
              <FontAwesomeIcon :icon="['fas', 'trophy']" class="modal-icon" />
              项目评分排名
            </h2>
            <button @click="closeRankingModal" class="modal-close">
              <FontAwesomeIcon :icon="['fas', 'times']" />
            </button>
          </div>

          <div class="modal-body">
            <div v-if="loadingRanking" class="loading-ranking">
              <FontAwesomeIcon :icon="['fas', 'spinner']" class="fa-spin loading-icon" />
              <span>加载排名数据中...</span>
            </div>

            <div v-else-if="projectRankingData.projects.length > 0" class="ranking-content">
              <div class="ranking-summary">
                <div class="summary-info">
                  <h3>{{ projectRankingData.requirement.title }}</h3>
                  <p>共有 {{ projectRankingData.total_count }} 个项目参与评分</p>
                </div>
                <div class="published-status">
                  <FontAwesomeIcon :icon="['fas', 'check-circle']" class="status-icon" />
                  <span>已公示</span>
                </div>
              </div>

              <div class="ranking-list">
                <div
                  v-for="project in projectRankingData.projects"
                  :key="project.id"
                  class="ranking-item"
                  :class="{ 'top-rank': project.rank <= 3 }"
                >
                  <div class="rank-badge" :class="`rank-${project.rank}`">
                    <FontAwesomeIcon
                      v-if="project.rank === 1"
                      :icon="['fas', 'crown']"
                      class="rank-icon gold"
                    />
                    <FontAwesomeIcon
                      v-else-if="project.rank === 2"
                      :icon="['fas', 'medal']"
                      class="rank-icon silver"
                    />
                    <FontAwesomeIcon
                      v-else-if="project.rank === 3"
                      :icon="['fas', 'medal']"
                      class="rank-icon bronze"
                    />
                    <span v-else class="rank-number">{{ project.rank }}</span>
                  </div>

                  <div class="project-info">
                    <div class="project-name">{{ project.project_title }}</div>
                    <div class="project-leader">
                      <FontAwesomeIcon :icon="['fas', 'user']" class="leader-icon" />
                      <span>{{ project.project_leader.name }}</span>
                      <span v-if="project.project_leader.school" class="leader-school"
                        >({{ project.project_leader.school }})</span
                      >
                    </div>
                    <div class="criteria-info">
                      <span class="criteria-name">{{ project.criteria_name }}</span>
                    </div>
                  </div>

                  <div class="score-info">
                    <div class="final-score">{{ project.final_score }}</div>
                    <div class="score-details">
                      <span
                        class="rank-level"
                        :style="{ backgroundColor: getRankLevelColor(project.rank_level) }"
                      >
                        {{ project.rank_level_display }}
                      </span>
                      <span class="rank-percentage"
                        >前{{ (100 - project.rank_percentage).toFixed(0) }}%</span
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div v-else class="no-ranking-data">
              <FontAwesomeIcon :icon="['fas', 'trophy']" class="no-data-icon" />
              <p>暂无排名数据</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 页脚 -->
      <footer class="footer">
        <div class="footer-container">
          <div class="footer-left">
            <div class="footer-text">© 2025 智汇校企合作平台 版权所有</div>
          </div>
        </div>
      </footer>
    </template>
  </div>
</template>

<style scoped lang="scss">
// 基础样式重置
* {
  box-sizing: border-box;
}

.requirement-detail {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background-color: #f5f7fa;
  font-family: 'Inter', system-ui, sans-serif;
  color: #4e5969;
}

// 加载和错误状态
.loading-screen,
.not-found-screen {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f5f7fa;
}

.loading-content,
.not-found-content {
  text-align: center;
  padding: 2rem;

  .loading-spinner {
    width: 40px;
    height: 40px;
    border: 3px solid #e5e6eb;
    border-top: 3px solid #165dff;
    border-radius: 50%;
    margin: 0 auto 1rem;
    animation: spin 1s linear infinite;
  }

  .not-found-icon {
    font-size: 4rem;
    color: #faad14;
    margin-bottom: 1rem;
  }

  h2 {
    font-size: 1.5rem;
    font-weight: 600;
    color: #272e3b;
    margin-bottom: 0.5rem;
  }

  p {
    color: #86909c;
    margin-bottom: 2rem;
  }

  .btn-primary {
    background-color: #165dff;
    color: white;
    padding: 0.75rem 1.5rem;
    border: none;
    border-radius: 6px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s;
    display: inline-flex;
    align-items: center;

    &:hover {
      background-color: #0e42d2;
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(22, 93, 255, 0.3);
    }
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

// 面包屑导航
.breadcrumb-nav {
  background: white;
  border-bottom: 1px solid #e5e6eb;

  .breadcrumb-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0.75rem 1rem;
  }

  .breadcrumb-content {
    display: flex;
    align-items: center;
  }

  .back-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    border: 1px solid #e5e6eb;
    border-radius: 6px;
    background: white;
    color: #4e5969;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.3s;
    text-decoration: none;

    &:hover {
      border-color: #165dff;
      color: #165dff;
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }

    .back-icon {
      font-size: 0.875rem;
    }
  }

  .breadcrumb-items {
    display: flex;
    align-items: center;
    font-size: 0.875rem;
    color: #86909c;
    margin-left: 1rem;

    .breadcrumb-link {
      color: #86909c;
      text-decoration: none;
      transition: color 0.3s;

      &:hover {
        color: #165dff;
      }
    }

    .breadcrumb-separator {
      margin: 0 0.5rem;
      font-size: 0.75rem;
      color: #c9cdd4;
    }

    .breadcrumb-current {
      color: #272e3b;
      font-weight: 500;
    }
  }
}

// 主内容区
.main-content {
  flex: 1;

  .content-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 1.5rem 1rem;
  }
}

// 页面标题区
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  gap: 1rem;

  .page-header-left {
    flex: 1;
    min-width: 0;

    .title-section {
      .title-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.5rem;
        flex-wrap: wrap;

        .page-title {
          font-size: 2rem;
          font-weight: 600;
          color: #272e3b;
          margin: 0;
          line-height: 1.2;
          word-break: break-word;
        }

        .status-badge {
          display: inline-flex;
          align-items: center;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 500;
          color: white;
        }
      }

      .page-subtitle {
        color: #86909c;
        margin: 0 0 0.75rem 0;
        font-size: 0.875rem;
        line-height: 1.4;
      }

      .organization-info {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 0.75rem;
        font-size: 0.875rem;
        color: #4e5969;

        .org-icon {
          color: #86909c;
        }

        .org-status {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          color: #52c41a;
          font-size: 0.75rem;

          .verified-icon {
            font-size: 0.75rem;
          }
        }
      }

      .stats-info {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
        margin-top: 0.5rem;

        .stat-item {
          display: inline-flex;
          align-items: center;
          gap: 0.375rem;
          font-size: 0.8rem;
          color: #86909c;
          padding: 0.25rem 0.5rem;
          background-color: #f5f7fa;
          border-radius: 4px;

          .stat-icon {
            font-size: 0.75rem;
            opacity: 0.8;
          }
        }
      }
    }
  }

  .page-header-actions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.75rem;

    .action-btn {
      display: inline-flex;
      align-items: center;
      padding: 0.75rem 1rem;
      border: 1px solid #e5e6eb;
      border-radius: 6px;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s;
      text-decoration: none;

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }

      .btn-icon {
        margin-right: 0.5rem;
      }

      &.primary {
        background-color: #165dff;
        color: white;
        border-color: #165dff;
        box-shadow: 0 2px 4px rgba(22, 93, 255, 0.2);

        &:hover:not(:disabled) {
          background-color: #0e42d2;
          transform: translateY(-1px);
          box-shadow: 0 4px 8px rgba(22, 93, 255, 0.3);
        }
      }

      &.secondary {
        background-color: white;
        color: #4e5969;

        &:hover {
          border-color: #165dff;
          color: #165dff;
          transform: translateY(-1px);
          box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
      }
    }
  }
}

// Tab导航
.tab-navigation {
  background: #f5f7fa;
  border-radius: 12px 12px 0 0;
  border-bottom: 1px solid #e5e6eb;
  margin-bottom: 0;

  .tab-nav-container {
    display: flex;
    gap: 0;

    .tab-item {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      padding: 1rem 1.5rem;
      border: none;
      background: transparent;
      color: #86909c;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.3s;
      border-bottom: 3px solid transparent;
      position: relative;

      .tab-icon {
        font-size: 0.875rem;
      }

      .project-count {
        background-color: #165dff;
        color: white;
        font-size: 0.75rem;
        padding: 0.125rem 0.375rem;
        border-radius: 10px;
        min-width: 18px;
        text-align: center;
        line-height: 1;
      }

      &:hover:not(.active) {
        color: #165dff;
        background-color: rgba(22, 93, 255, 0.05);
      }

      &.active {
        color: #165dff;
        border-bottom-color: #165dff;
        background-color: #f5f7fa;

        .project-count {
          background-color: #165dff;
        }
      }
    }
  }
}

// Tab内容
.tab-content {
  background: #f5f7fa;
  border-radius: 0 0 12px 12px;
  min-height: 400px;
}

// 内容网格
.content-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 1.5rem;
  padding: 1.5rem 0;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

.main-column {
  min-width: 0;
}

.sidebar-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

// 项目Tab内容
.projects-tab-content {
  padding: 1.5rem;
}

// 项目统计
.project-stats {
  margin-bottom: 2rem;

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;

    .stat-card {
      background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);
      border: 1px solid #e5e6eb;
      border-radius: 8px;
      padding: 1.5rem;
      text-align: center;
      transition: all 0.3s;

      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
      }

      .stat-number {
        font-size: 2rem;
        font-weight: 700;
        color: #165dff;
        margin-bottom: 0.5rem;
      }

      .stat-label {
        font-size: 0.875rem;
        color: #86909c;
        font-weight: 500;
      }
    }
  }
}

// 项目列表
.projects-section {
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.5rem;

    .section-title {
      font-size: 1.125rem;
      font-weight: 600;
      color: #272e3b;
    }

    .section-actions {
      display: flex;
      gap: 0.5rem;
    }
  }

  .project-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .project-card {
    background: #fafbfc;
    border: 1px solid #e5e6eb;
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.3s;

    &:hover {
      border-color: #165dff;
      box-shadow: 0 4px 12px rgba(22, 93, 255, 0.1);
    }

    .project-header {
      margin-bottom: 1rem;

      .project-title-row {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 0.5rem;
        flex-wrap: wrap;

        .project-title {
          font-size: 1.125rem;
          font-weight: 600;
          color: #272e3b;
          margin: 0;
        }

        .project-status-badge {
          display: inline-flex;
          align-items: center;
          padding: 0.25rem 0.75rem;
          border-radius: 20px;
          font-size: 0.75rem;
          font-weight: 500;
          color: white;
        }
      }

      .project-meta {
        font-size: 0.875rem;
        color: #86909c;

        .project-date {
          display: inline-flex;
          align-items: center;
          gap: 0.375rem;

          .meta-icon {
            font-size: 0.75rem;
          }
        }
      }
    }

    .project-body {
      margin-bottom: 1rem;

      .project-leader {
        margin-bottom: 1rem;

        .leader-info {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          font-size: 0.875rem;

          .leader-icon {
            color: #faad14;
            font-size: 0.875rem;
          }

          .leader-label {
            color: #86909c;
          }

          .leader-name {
            font-weight: 600;
            color: #272e3b;
          }

          .leader-id {
            color: #86909c;
            font-size: 0.8rem;
          }
        }
      }

      .project-members {
        .members-header {
          display: flex;
          align-items: center;
          gap: 0.5rem;
          margin-bottom: 0.75rem;
          font-size: 0.875rem;
          color: #86909c;

          .members-icon {
            font-size: 0.875rem;
          }

          .members-label {
            font-weight: 500;
          }
        }

        .members-list {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .member-item {
          display: flex;
          align-items: center;
          gap: 0.75rem;
          padding: 0.5rem;
          background: white;
          border-radius: 8px;
          border: 1px solid #e5e6eb;

          .member-avatar {
            width: 32px;
            height: 32px;
            border-radius: 50%;
            background: linear-gradient(135deg, #165dff, #69b1ff);
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 600;
            font-size: 0.875rem;
          }

          .member-info {
            flex: 1;

            .member-name {
              font-weight: 500;
              color: #272e3b;
              margin-bottom: 0.125rem;
              font-size: 0.875rem;
            }

            .member-id {
              font-size: 0.75rem;
              color: #86909c;
            }
          }

          .member-role {
            .role-badge {
              padding: 0.125rem 0.5rem;
              border-radius: 12px;
              font-size: 0.75rem;
              font-weight: 500;

              &.leader {
                background-color: #faad14;
                color: white;
              }

              &.member {
                background-color: #52c41a;
                color: white;
              }
            }
          }
        }
      }
    }

    .project-footer {
      display: flex;
      justify-content: flex-end;
      padding-top: 1rem;
      border-top: 1px solid #e5e6eb;

      .project-action-btn {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        border: 1px solid #165dff;
        border-radius: 6px;
        background: white;
        color: #165dff;
        font-size: 0.875rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s;

        &:hover {
          background-color: #165dff;
          color: white;
          transform: translateY(-1px);
          box-shadow: 0 2px 8px rgba(22, 93, 255, 0.3);
        }
      }
    }
  }

  .no-projects {
    text-align: center;
    padding: 3rem 1rem;

    .no-projects-content {
      .no-projects-icon {
        font-size: 3rem;
        color: #c9cdd4;
        margin-bottom: 1rem;
      }

      h3 {
        font-size: 1.125rem;
        font-weight: 600;
        color: #272e3b;
        margin-bottom: 0.5rem;
      }

      p {
        color: #86909c;
        font-size: 0.875rem;
      }
    }
  }
}

// 评分按钮样式
.ranking-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .btn-icon {
    font-size: 0.875rem;
  }

  &.view {
    background-color: #165dff;
    color: white;
    box-shadow: 0 2px 4px rgba(22, 93, 255, 0.2);

    &:hover:not(:disabled) {
      background-color: #0e42d2;
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(22, 93, 255, 0.3);
    }
  }

  &.publish {
    background-color: #52c41a;
    color: white;
    box-shadow: 0 2px 4px rgba(82, 196, 26, 0.2);

    &:hover:not(:disabled) {
      background-color: #389e0d;
      transform: translateY(-1px);
      box-shadow: 0 4px 8px rgba(82, 196, 26, 0.3);
    }
  }
}

// 弹窗样式
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.ranking-modal {
  background: white;
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 800px;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;

  .modal-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.5rem;
    border-bottom: 1px solid #e5e6eb;
    background: linear-gradient(135deg, #f5f7fa 0%, #ffffff 100%);

    .modal-title {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      font-size: 1.25rem;
      font-weight: 600;
      color: #272e3b;
      margin: 0;

      .modal-icon {
        color: #faad14;
        font-size: 1.125rem;
      }
    }

    .modal-close {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 32px;
      height: 32px;
      border: none;
      background: none;
      color: #86909c;
      cursor: pointer;
      border-radius: 6px;
      transition: all 0.3s;

      &:hover {
        background-color: #f5f7fa;
        color: #272e3b;
      }
    }
  }

  .modal-body {
    flex: 1;
    overflow-y: auto;
    padding: 1.5rem;
  }
}

.loading-ranking {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #86909c;

  .loading-icon {
    color: #165dff;
    font-size: 1.125rem;
  }
}

.ranking-content {
  .ranking-summary {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    padding: 1rem;
    background: linear-gradient(135deg, #f6f8ff 0%, #ffffff 100%);
    border: 1px solid #e5e6eb;
    border-radius: 8px;
    margin-bottom: 1.5rem;

    .summary-info {
      flex: 1;

      h3 {
        font-size: 1.125rem;
        font-weight: 600;
        color: #272e3b;
        margin: 0 0 0.5rem 0;
      }

      p {
        color: #86909c;
        margin: 0;
        font-size: 0.875rem;
      }
    }

    .published-status {
      display: flex;
      align-items: center;
      gap: 0.375rem;
      color: #52c41a;
      font-size: 0.875rem;
      font-weight: 500;

      .status-icon {
        font-size: 0.875rem;
      }
    }
  }

  .ranking-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .ranking-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 1rem;
    background: white;
    border: 1px solid #e5e6eb;
    border-radius: 8px;
    transition: all 0.3s;

    &:hover {
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    &.top-rank {
      background: linear-gradient(135deg, #fff8e1 0%, #ffffff 100%);
      border-color: #faad14;
    }

    .rank-badge {
      display: flex;
      align-items: center;
      justify-content: center;
      width: 48px;
      height: 48px;
      border-radius: 50%;
      font-weight: 700;
      font-size: 1.125rem;
      flex-shrink: 0;

      &.rank-1 {
        background: linear-gradient(135deg, #ffec3d, #ff9800);
        color: white;
        box-shadow: 0 2px 8px rgba(255, 152, 0, 0.3);
      }

      &.rank-2 {
        background: linear-gradient(135deg, #e0e0e0, #757575);
        color: white;
        box-shadow: 0 2px 8px rgba(117, 117, 117, 0.3);
      }

      &.rank-3 {
        background: linear-gradient(135deg, #ffab40, #ff6f00);
        color: white;
        box-shadow: 0 2px 8px rgba(255, 111, 0, 0.3);
      }

      .rank-icon {
        font-size: 1.25rem;

        &.gold {
          color: #ffec3d;
        }

        &.silver {
          color: #e0e0e0;
        }

        &.bronze {
          color: #ffab40;
        }
      }

      .rank-number {
        background: #f5f7fa;
        color: #272e3b;
        border: 2px solid #e5e6eb;
      }
    }

    .project-info {
      flex: 1;
      min-width: 0;

      .project-name {
        font-size: 1rem;
        font-weight: 600;
        color: #272e3b;
        margin-bottom: 0.375rem;
        word-break: break-word;
      }

      .project-leader {
        display: flex;
        align-items: center;
        gap: 0.375rem;
        font-size: 0.875rem;
        color: #4e5969;
        margin-bottom: 0.25rem;

        .leader-icon {
          color: #86909c;
          font-size: 0.75rem;
        }

        .leader-school {
          color: #86909c;
          font-size: 0.8rem;
        }
      }

      .criteria-info {
        font-size: 0.75rem;
        color: #86909c;

        .criteria-name {
          padding: 0.125rem 0.5rem;
          background-color: #f5f7fa;
          border-radius: 12px;
        }
      }
    }

    .score-info {
      text-align: right;
      flex-shrink: 0;

      .final-score {
        font-size: 1.5rem;
        font-weight: 700;
        color: #165dff;
        margin-bottom: 0.375rem;
      }

      .score-details {
        display: flex;
        flex-direction: column;
        gap: 0.25rem;
        align-items: flex-end;

        .rank-level {
          padding: 0.125rem 0.5rem;
          border-radius: 12px;
          font-size: 0.75rem;
          font-weight: 600;
          color: white;
        }

        .rank-percentage {
          font-size: 0.75rem;
          color: #86909c;
        }
      }
    }
  }
}

.no-ranking-data {
  text-align: center;
  padding: 3rem 1rem;

  .no-data-icon {
    font-size: 3rem;
    color: #c9cdd4;
    margin-bottom: 1rem;
  }

  p {
    color: #86909c;
    font-size: 0.875rem;
  }
}

// 卡片样式
.description-section,
.evaluation-criteria-section,
.support-section,
.files-section,
.resources-section,
.info-card,
.tags-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  .section-title,
  .card-title {
    font-size: 1.125rem;
    font-weight: 600;
    color: #272e3b;
    margin-bottom: 1rem;
  }

  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;

    .section-title {
      display: flex;
      align-items: center;
      gap: 0.5rem;
      margin-bottom: 0;

      .section-icon {
        color: #52c41a;
        font-size: 1rem;
      }
    }
  }
}

.description-section,
.evaluation-criteria-section,
.support-section,
.files-section,
.resources-section {
  margin-bottom: 1.5rem;
}

// 需求描述
.description-section {
  .description-content {
    line-height: 1.6;
    color: #4e5969;
    white-space: pre-wrap;
    word-break: break-word;
  }
}

// 评分标准样式
.evaluation-criteria-section {
  .evaluation-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.75rem;
    background-color: #52c41a;
    color: white;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;

    .badge-icon {
      font-size: 0.75rem;
    }
  }

  .loading-criteria {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #86909c;
    font-size: 0.875rem;

    .loading-icon {
      color: #165dff;
    }
  }

  .criteria-content {
    .criteria-summary {
      margin-bottom: 1rem;
      padding: 0.75rem 1rem;
      background-color: #fafbfc;
      border-radius: 8px;
      border: 1px solid #e5e6eb;

      .summary-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
        flex-wrap: wrap;
        gap: 0.5rem;

        .criteria-name {
          font-size: 1rem;
          font-weight: 600;
          color: #272e3b;
          margin: 0;
        }

        .criteria-stats {
          display: flex;
          gap: 1rem;
          font-size: 0.75rem;

          .stat-item {
            display: inline-flex;
            align-items: center;
            gap: 0.25rem;
            color: #86909c;

            .stat-icon {
              font-size: 0.75rem;
            }
          }
        }
      }

      .criteria-description {
        margin: 0;
        color: #4e5969;
        line-height: 1.4;
        font-size: 0.875rem;
      }
    }

    .indicators-list {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;

      .indicator-item {
        display: flex;
        gap: 0.75rem;
        padding: 0.75rem;
        background-color: #fafbfc;
        border-radius: 6px;
        border: 1px solid #e5e6eb;
        transition: all 0.3s;

        &:hover {
          border-color: #165dff;
          background-color: #f6f8ff;
        }

        .indicator-order {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 24px;
          height: 24px;
          background-color: #165dff;
          color: white;
          border-radius: 50%;
          font-weight: 600;
          font-size: 0.75rem;
          flex-shrink: 0;
        }

        .indicator-content {
          flex: 1;
          min-width: 0;

          .indicator-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 0.5rem;
            gap: 0.75rem;

            .indicator-name {
              display: flex;
              align-items: center;
              gap: 0.5rem;
              font-size: 0.875rem;
              font-weight: 600;
              color: #272e3b;
              margin: 0;
              flex: 1;

              .required-badge {
                padding: 0.125rem 0.375rem;
                background-color: #ff4d4f;
                color: white;
                border-radius: 10px;
                font-size: 0.65rem;
                font-weight: 500;
              }
            }

            .indicator-stats {
              display: flex;
              gap: 0.5rem;
              flex-shrink: 0;

              .stat-tag {
                padding: 0.125rem 0.5rem;
                border-radius: 12px;
                font-size: 0.7rem;
                font-weight: 500;

                &.weight {
                  background-color: #52c41a;
                  color: white;
                }

                &.score {
                  background-color: #faad14;
                  color: white;
                }
              }
            }
          }

          .indicator-description {
            margin: 0;
            color: #4e5969;
            line-height: 1.4;
            font-size: 0.8rem;
          }
        }
      }
    }
  }
}

// 支持提供信息
.support-section {
  .support-content {
    display: flex;
    align-items: flex-start;
    gap: 0.75rem;

    .support-icon {
      color: #52c41a;
      font-size: 1.25rem;
      margin-top: 0.125rem;
    }

    p {
      flex: 1;
      margin: 0;
      line-height: 1.6;
      color: #4e5969;
    }
  }
}

// 文件列表
.file-list,
.resource-list {
  .file-item,
  .resource-item {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 0;
    border-bottom: 1px solid #f5f7fa;
    transition: background-color 0.3s;

    &:hover {
      background-color: #f5f7fa;
      border-radius: 6px;
      padding: 0.75rem;
      margin: 0 -0.75rem;
    }

    &:last-child {
      border-bottom: none;
    }

    .file-info,
    .resource-info {
      display: flex;
      align-items: center;
      gap: 0.75rem;
      flex: 1;

      .file-icon,
      .resource-icon {
        width: 32px;
        height: 32px;
        display: flex;
        align-items: center;
        justify-content: center;

        .file-icon-inner,
        .resource-icon-inner {
          color: #86909c;
          font-size: 1.125rem;
        }
      }

      .file-details,
      .resource-details {
        flex: 1;

        .file-name,
        .resource-name {
          font-weight: 500;
          color: #272e3b;
          margin-bottom: 0.125rem;
        }

        .file-meta,
        .resource-meta {
          font-size: 0.75rem;
          color: #86909c;
          display: flex;
          gap: 1rem;

          .file-time {
            opacity: 0.8;
          }
        }
      }
    }

    .file-actions,
    .resource-actions {
      display: flex;
      gap: 0.5rem;
    }
  }
}

// 文件和资源操作按钮
.file-action-btn,
.resource-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border: 1px solid #e5e6eb;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  background: white;

  &.download {
    color: #165dff;
    border-color: #165dff;

    &:hover {
      background-color: #165dff;
      color: white;
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(22, 93, 255, 0.3);
    }
  }

  .fa-icon {
    font-size: 0.875rem;
  }
}

// 信息卡片
.info-card {
  .info-list {
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 0.75rem 0;
      border-bottom: 1px solid #f5f7fa;

      &:last-child {
        border-bottom: none;
        padding-bottom: 0;
      }

      .info-label {
        font-weight: 500;
        color: #86909c;
        font-size: 0.875rem;
        min-width: 80px;
        flex-shrink: 0;
      }

      .info-value {
        font-weight: 500;
        color: #272e3b;
        text-align: right;
        flex: 1;
      }

      .org-display {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        flex: 1;
        justify-content: flex-end;

        .org-logo-small {
          width: 20px;
          height: 20px;
          border-radius: 4px;
          object-fit: cover;
        }

        .org-icon-small {
          width: 20px;
          height: 20px;
          color: #86909c;
          display: flex;
          align-items: center;
          justify-content: center;
        }
      }
    }
  }
}

// 标签卡片
.tags-card {
  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }

  .tags-display {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;

    .tag {
      display: inline-flex;
      align-items: center;
      padding: 0.25rem 0.75rem;
      border-radius: 20px;
      font-size: 0.75rem;
      font-weight: 500;
      color: white;

      &.primary-tag {
        background-color: #165dff;
      }

      &.secondary-tag {
        background-color: #52c41a;
      }
    }
  }
}

// 空状态
.no-files,
.no-resources {
  text-align: center;
  padding: 2rem;
  color: #86909c;
}

// 页脚
.footer {
  position: sticky;
  background: white;
  border-top: 1px solid #e5e6eb;
  padding: 1.5rem 0;

  .footer-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    justify-content: center;
    align-items: center;

    .footer-text {
      color: #86909c;
      font-size: 0.875rem;
    }
  }
}

// 工具类
.mr-1 {
  margin-right: 0.25rem;
}
.mr-2 {
  margin-right: 0.5rem;
}

// 响应式设计
@media (max-width: 1024px) and (min-width: 769px) {
  .content-grid {
    grid-template-columns: 2fr 1fr;
    gap: 1rem;
  }

  .page-header {
    .page-header-left {
      .title-section {
        .title-row {
          .page-title {
            font-size: 1.75rem;
          }
        }
      }
    }
  }

  .sidebar-column {
    gap: 1rem;
  }

  .description-section,
  .evaluation-criteria-section,
  .support-section,
  .files-section,
  .resources-section,
  .info-card,
  .tags-card {
    padding: 1.25rem;
  }

  .projects-tab-content {
    padding: 1.25rem;
  }

  .project-stats {
    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
    }
  }
}

// 小屏幕响应式设计
@media (max-width: 768px) {
  .breadcrumb-nav {
    .breadcrumb-container {
      padding: 0.5rem;
    }

    .breadcrumb-content {
      align-items: stretch;
      gap: 0.75rem;
      flex-wrap: wrap;
    }

    .back-btn {
      align-self: flex-start;
      padding: 0.3rem 0.6rem;
    }

    .breadcrumb-items {
      font-size: 0.8rem;
      margin-left: 8px;
    }
  }

  .main-content {
    .content-container {
      padding: 1rem 0.5rem;
    }
  }

  .page-header {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;

    .page-header-left {
      .title-section {
        .title-row {
          flex-wrap: wrap;
          align-items: flex-start;
          gap: 0.5rem;

          .page-title {
            font-size: 1.5rem;
          }
        }

        .stats-info {
          gap: 0.5rem;
          margin-top: 0.75rem;

          .stat-item {
            font-size: 0.75rem;
            padding: 0.2rem 0.4rem;
          }
        }
      }
    }

    .page-header-actions {
      justify-content: stretch;

      .action-btn {
        flex: 1;
        justify-content: center;
      }
    }
  }

  // Tab导航移动端优化
  .tab-navigation {
    margin: 0 -0.5rem;
    border-radius: 0;

    .tab-nav-container {
      .tab-item {
        flex: 1;
        justify-content: center;
        padding: 0.75rem 1rem;
        font-size: 0.8rem;

        .project-count {
          font-size: 0.7rem;
          padding: 0.1rem 0.3rem;
        }
      }
    }
  }

  .tab-content {
    margin: 0 -0.5rem;
    border-radius: 0;
  }

  .content-grid {
    padding: 1rem;
  }

  .projects-tab-content {
    padding: 1rem;
  }

  .projects-section {
    .section-header {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.75rem;

      .section-actions {
        width: 100%;
        justify-content: flex-end;
      }
    }
  }

  .project-stats {
    margin-bottom: 1.5rem;

    .stats-grid {
      grid-template-columns: repeat(2, 1fr);
      gap: 0.75rem;

      .stat-card {
        padding: 1rem;

        .stat-number {
          font-size: 1.5rem;
        }

        .stat-label {
          font-size: 0.8rem;
        }
      }
    }
  }

  .project-card {
    padding: 1rem;

    .project-header {
      .project-title-row {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;

        .project-title {
          font-size: 1rem;
        }
      }
    }

    .project-body {
      .project-members {
        .member-item {
          padding: 0.375rem;
          gap: 0.5rem;

          .member-avatar {
            width: 28px;
            height: 28px;
            font-size: 0.8rem;
          }

          .member-info {
            .member-name {
              font-size: 0.8rem;
            }

            .member-id {
              font-size: 0.7rem;
            }
          }

          .member-role {
            .role-badge {
              font-size: 0.7rem;
              padding: 0.1rem 0.4rem;
            }
          }
        }
      }
    }

    .project-footer {
      padding-top: 0.75rem;

      .project-action-btn {
        padding: 0.5rem 0.75rem;
        font-size: 0.8rem;
      }
    }
  }

  .description-section,
  .evaluation-criteria-section,
  .support-section,
  .files-section,
  .resources-section,
  .info-card,
  .tags-card {
    padding: 1rem;
  }

  // 弹窗移动端优化
  .modal-overlay {
    padding: 0.5rem;
  }

  .ranking-modal {
    max-height: 90vh;

    .modal-header {
      padding: 1rem;

      .modal-title {
        font-size: 1.125rem;
      }
    }

    .modal-body {
      padding: 1rem;
    }
  }

  .ranking-content {
    .ranking-summary {
      flex-direction: column;
      gap: 0.75rem;
      padding: 0.75rem;
    }

    .ranking-item {
      padding: 0.75rem;
      gap: 0.75rem;

      .rank-badge {
        width: 40px;
        height: 40px;
        font-size: 1rem;
      }

      .project-info {
        .project-name {
          font-size: 0.9rem;
        }

        .project-leader {
          font-size: 0.8rem;

          .leader-school {
            font-size: 0.75rem;
          }
        }
      }

      .score-info {
        .final-score {
          font-size: 1.25rem;
        }
      }
    }
  }

  .file-action-btn,
  .resource-action-btn {
    padding: 0.375rem 0.5rem;
    font-size: 0.675rem;

    span {
      display: none;
    }
  }

  .footer {
    .footer-container {
      flex-direction: column;
      gap: 1rem;
      text-align: center;
      padding: 0 0.5rem;
    }
  }
}
</style>
