<script setup>
import { ref, onMounted, nextTick, onBeforeUnmount, computed } from 'vue'
import { useRouter } from 'vue-router'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faBriefcase,
  faSpinner,
  faUsers,
  faChartLine,
  faCode,
  faMobile,
  faDatabase,
  faCloud,
  faPlus,
  faChevronLeft,
  faChevronRight,
  faSearch,
  faBookmark,
  faArrowUp,
  faArrowDown,
  faEye,
  faEdit,
  faBell,
  faCalendarAlt,
  faExclamationCircle,
  faCheckCircle,
  faInfoCircle,
  faFile,
  faTools,
  faBook,
  faPause,
  faPlay,
  faStop,
  faTimes,
  faComments,
  faFileText,
  faClock
} from '@fortawesome/free-solid-svg-icons'
import * as echarts from 'echarts/core'
import { BarChart, PieChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必需的组件
echarts.use([
  CanvasRenderer,
  BarChart,
  PieChart,
  TitleComponent,
  TooltipComponent,
  GridComponent,
  LegendComponent
])

import { resourcesService } from '@/api'
import { requirementService } from '@/api'
import { enterpriseOverviewService } from '@/api'
import { projectService } from '@/api'
import { notificationService } from '@/api'
import { useUserStore } from '@/stores'
import { useNotificationStore } from '@/stores'

const userStore = useUserStore()
const notificationStore = useNotificationStore()
const router = useRouter()

library.add(
  faBriefcase,
  faSpinner,
  faUsers,
  faChartLine,
  faCode,
  faMobile,
  faDatabase,
  faCloud,
  faPlus,
  faChevronLeft,
  faChevronRight,
  faSearch,
  faBookmark,
  faArrowUp,
  faArrowDown,
  faEye,
  faEdit,
  faBell,
  faCalendarAlt,
  faExclamationCircle,
  faCheckCircle,
  faInfoCircle,
  faFile,
  faTools,
  faBook,
  faPause,
  faPlay,
  faStop,
  faTimes,
  faComments,
  faFileText,
  faClock
)

// 响应式数据
const currentPage = ref(1)
const pageSize = ref(4)
const total = ref(0)
const selectedDate = ref(new Date())

// 接口数据相关
const resourcesLoading = ref(false)
const demandsLoading = ref(false)
const overviewLoading = ref(false)
const projectsLoading = ref(false)
const notificationsLoading = ref(false)
const resourcesData = ref([])
const demandsData = ref([])
const projectsData = ref([])
const resourcesPagination = ref({})
const demandsPagination = ref({})
const projectsPagination = ref({})

// 通知数据
const notifications = ref([])
const unreadCount = ref(0)

// 发布需求模态框
const showPublishModal = ref(false)

// ECharts实例
let projectChart = null
let skillChart = null

// 资源类型映射
const resourceTypeMap = {
  code: '代码',
  dataset: '数据集',
  document: '文档',
  course: '课程',
  video: '视频',
  tool: '工具'
}

// 资源状态映射
const resourceStatusMap = {
  published: '已发布',
  draft: '草稿',
  unpublished: '已下线'
}

// 需求状态映射
const demandStatusMap = {
  under_review: '审核中',
  review_failed: '审核失败',
  in_progress: '进行中',
  completed: '已完成',
  paused: '已暂停'
}

// 项目状态映射
const projectStatusMap = {
  recruiting: '招募中',
  in_progress: '进行中',
  completed: '已完成',
  suspended: '已暂停',
  cancelled: '已取消'
}

// 获取项目状态类型
const getProjectStatusType = (status) => {
  const typeMap = {
    recruiting: 'primary',
    in_progress: 'warning',
    completed: 'success',
    suspended: 'info',
    cancelled: 'danger'
  }
  return typeMap[status] || 'info'
}

// 获取项目图标
const getProjectIcon = (status) => {
  const iconMap = {
    recruiting: 'users',
    in_progress: 'spinner',
    completed: 'check-circle',
    suspended: 'pause',
    cancelled: 'times'
  }
  return iconMap[status] || 'briefcase'
}

// 获取项目图标颜色
const getProjectIconColor = (status) => {
  const colorMap = {
    recruiting: 'primary',
    in_progress: 'warning',
    completed: 'success',
    suspended: 'info',
    cancelled: 'danger'
  }
  return colorMap[status] || 'info'
}

// 计算项目进度（基于状态估算）
const getProjectProgress = (status) => {
  const progressMap = {
    recruiting: 10,
    in_progress: 65,
    completed: 100,
    suspended: 45,
    cancelled: 0
  }
  return progressMap[status] || 0
}

// 获取资源图标
const getResourceIcon = (type) => {
  const iconMap = {
    code: 'code',
    dataset: 'database',
    document: 'file',
    course: 'book',
    video: 'video',
    tool: 'tools'
  }
  return iconMap[type] || 'file'
}

// 获取资源状态类型
const getResourceStatusType = (status) => {
  const typeMap = {
    published: 'success',
    draft: 'warning',
    unpublished: 'info'
  }
  return typeMap[status] || 'info'
}

// 获取需求状态类型
const getDemandStatusType = (status) => {
  const typeMap = {
    under_review: 'warning',
    review_failed: 'danger',
    in_progress: 'primary',
    completed: 'success',
    paused: 'info'
  }
  return typeMap[status] || 'info'
}

// 获取需求图标
const getDemandIcon = (status) => {
  const iconMap = {
    under_review: 'clock',
    review_failed: 'exclamation-circle',
    in_progress: 'spinner',
    completed: 'check-circle',
    paused: 'pause'
  }
  return iconMap[status] || 'exclamation-circle'
}

// 通知相关函数
const getNotificationIcon = (notification) => {
  // 根据通知类型或优先级返回图标
  if (notification.priority === 'high' || notification.priority === 'urgent') {
    return 'exclamation-circle'
  }
  return 'info-circle'
}

// 添加通知类型映射函数
const getNotificationType = (notification) => {
  const typeMap = {
    high: 'error',
    urgent: 'error',
    medium: 'warning',
    low: 'info',
    normal: 'success'
  }

  return typeMap[notification.priority] || 'info'
}

// 数据概览
const dashboardStats = ref([
  {
    title: '发布需求',
    value: 0,
    change: 0,
    icon: 'exclamation-circle',
    color: 'primary'
  },
  {
    title: '发布资源',
    value: 0,
    change: 0,
    icon: 'database',
    color: 'success'
  },
  {
    title: '进行中项目',
    value: 0,
    change: 0,
    icon: 'spinner',
    color: 'warning'
  },
  {
    title: '项目完成率',
    value: '0%',
    change: 0,
    icon: 'chart-line',
    color: 'info'
  }
])

// 处理后的项目数据
const processedProjects = computed(() => {
  return projectsData.value.map((project) => ({
    id: project.id,
    name: project.title,
    category: project.requirement?.title || '未指定需求', // 使用需求的title作为项目类别
    manager: {
      name: project.leader?.real_name || project.leader?.username || '未分配',
      position: project.leader?.major || '项目负责人',
      avatar: project.leader?.avatar || 'https://picsum.photos/id/237/100/100'
    },
    progress: getProjectProgress(project.status),
    teamSize: project.participant_count || 0,
    startDate: formatDate(project.created_at),
    status: projectStatusMap[project.status] || project.status,
    statusType: getProjectStatusType(project.status),
    icon: getProjectIcon(project.status),
    iconColor: getProjectIconColor(project.status),
    originalData: project // 保存原始数据以便其他操作使用
  }))
})

// 处理后的资源数据
const processedResources = computed(() => {
  return resourcesData.value.map((resource) => ({
    ...resource,
    typeText: resourceTypeMap[resource.type] || resource.type,
    statusText: resourceStatusMap[resource.status] || resource.status,
    icon: getResourceIcon(resource.type),
    statusType: getResourceStatusType(resource.status),
    iconColor: getResourceStatusColor(resource.type)
  }))
})

// 处理后的需求数据
const processedDemands = computed(() => {
  return demandsData.value.map((demand) => ({
    ...demand,
    statusText: demandStatusMap[demand.status] || demand.status,
    statusType: getDemandStatusType(demand.status),
    icon: getDemandIcon(demand.status),
    iconColor: getDemandStatusColor(demand.status)
  }))
})

// 获取资源类型颜色
const getResourceStatusColor = (type) => {
  const colorMap = {
    code: 'primary',
    dataset: 'success',
    document: 'info',
    course: 'warning',
    video: 'danger',
    tool: 'primary'
  }
  return colorMap[type] || 'info'
}

// 获取需求状态颜色
const getDemandStatusColor = (status) => {
  const colorMap = {
    under_review: 'warning',
    review_failed: 'danger',
    in_progress: 'primary',
    completed: 'success',
    paused: 'info'
  }
  return colorMap[status] || 'info'
}

// 项目进度图表数据
const projectChartData = ref({
  months: [],
  completed: [],
  inProgress: [],
  recruiting: []
})

// 技能分布图表数据
const skillChartData = ref([])

// 获取通知列表
const fetchNotifications = async () => {
  try {
    notificationsLoading.value = true
    const params = {
      page: 1,
      page_size: 5
    }

    const response = await notificationService.getNotifications(params)
    if (response.status === 'success') {
      notifications.value = response.data.results || []
    }
  } catch (error) {
    console.error('获取通知列表失败:', error)
  } finally {
    notificationsLoading.value = false
  }
}

// 获取未读通知数量
const fetchUnreadCount = async () => {
  try {
    const response = await notificationService.getUnreadNotificationsCount()
    if (response.status === 'success') {
      unreadCount.value = response.data.unread_count || 0
      notificationStore.setUnreadCount(unreadCount.value)
    }
  } catch (error) {
    console.error('获取未读通知数量失败:', error)
  }
}

// 获取项目列表
const fetchProjects = async (page = 1, size = 4) => {
  try {
    projectsLoading.value = true
    const organizationId = userStore.user?.company_profile?.organization?.id
    if (!organizationId) {
      console.error('未找到组织ID')
      return
    }

    const params = {
      page: page.toString(),
      page_size: size.toString(),
      organization_id: organizationId.toString()
    }

    const response = await projectService.getProjectList(params)
    if (response.status === 'success') {
      projectsData.value = response.data.projects
      projectsPagination.value = response.data.pagination
      // 更新总数
      total.value = response.data.pagination.total_count
    }
  } catch (error) {
    console.error('获取项目列表失败:', error)
  } finally {
    projectsLoading.value = false
  }
}

// 获取企业概览数据
const fetchOverview = async () => {
  try {
    overviewLoading.value = true
    const organizationId = userStore.user?.company_profile?.organization?.id
    if (!organizationId) {
      console.error('未找到组织ID')
      return
    }

    const response = await enterpriseOverviewService.getOverview(organizationId)
    if (response.status === 'success') {
      const data = response.data

      // 更新数据概览
      dashboardStats.value[0].value = data.published_requirements.count
      dashboardStats.value[0].change = parseFloat(data.published_requirements.growth_rate) || 0

      dashboardStats.value[1].value = data.published_resources.count
      dashboardStats.value[1].change = parseFloat(data.published_resources.growth_rate) || 0

      dashboardStats.value[2].value = data.in_progress_projects.count
      dashboardStats.value[2].change = parseFloat(data.in_progress_projects.growth_rate) || 0

      dashboardStats.value[3].value = data.project_completion_rate.rate
      dashboardStats.value[3].change = parseFloat(data.project_completion_rate.growth_rate) || 0

      // 更新项目进度图表数据
      projectChartData.value = {
        months: data.monthly_progress.map((item) => item.month),
        completed: data.monthly_progress.map((item) => item.completed),
        inProgress: data.monthly_progress.map((item) => item.in_progress),
        recruiting: data.monthly_progress.map((item) => item.recruiting)
      }

      // 处理技能分布数据
      skillChartData.value = data.skill_distribution.map((item, index) => ({
        value: item.count,
        name: item.skill.split('-').pop(),
        showLegend: index < 5
      }))

      // 如果图表已经初始化，更新数据
      if (projectChart) {
        updateProjectChart()
      }
      if (skillChart) {
        updateSkillChart()
      }
    }
  } catch (error) {
    console.error('获取企业概览数据失败:', error)
  } finally {
    overviewLoading.value = false
  }
}

// 获取资源列表
const fetchResources = async (page = 1, size = 3) => {
  try {
    resourcesLoading.value = true
    const organizationId = userStore.user?.company_profile?.organization?.id
    if (!organizationId) {
      console.error('未找到组织ID')
      return
    }

    const params = {
      page,
      page_size: size
    }

    const response = await resourcesService.getResources(organizationId, params)
    if (response.status === 'success') {
      resourcesData.value = response.data.resources
      resourcesPagination.value = response.data.pagination
    }
  } catch (error) {
    console.error('获取资源列表失败:', error)
  } finally {
    resourcesLoading.value = false
  }
}

// 获取需求列表
const fetchDemands = async (page = 1, size = 3) => {
  try {
    demandsLoading.value = true
    const organizationId = userStore.user?.company_profile?.organization?.id
    if (!organizationId) {
      console.error('未找到组织ID')
      return
    }

    const params = {
      page,
      page_size: size
    }

    const response = await requirementService.getRequirementList(organizationId, params)
    if (response.status === 'success') {
      demandsData.value = response.data.requirements
      demandsPagination.value = response.data.pagination
    }
  } catch (error) {
    console.error('获取需求列表失败:', error)
  } finally {
    demandsLoading.value = false
  }
}

// 获取增长状态的样式类
const getGrowthClass = (change) => {
  if (change > 0) return 'growth-positive'
  if (change < 0) return 'growth-negative'
  return 'growth-zero'
}

// 方法
const handleSizeChange = (val) => {
  pageSize.value = val
  fetchProjects(1, val)
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchProjects(val, pageSize.value)
}

const viewProject = (project) => {
  router.push(`/enterprise/project-details/${project.originalData.id}`)
}

const publishResource = () => {
  router.push('/enterprise/resource/create')
}

const publishDemand = () => {
  showPublishModal.value = true
}

const closePublishModal = () => {
  showPublishModal.value = false
}

const selectPublishType = (type) => {
  console.log('Selected publish type:', type)
  closePublishModal()
  // 这里跳转到对应的发布页面
  if (type === 'chat') {
    // 跳转到对话式发布页面
    console.log('跳转到对话式发布页面')
    router.push('/enterprise/requirement/create/chat')
  } else {
    // 跳转到表单式发布页面
    console.log('跳转到表单式发布页面')
    router.push('/enterprise/requirement/create/form')
  }
}

const viewResource = (resource) => {
  router.push(`/enterprise/resource/detail/${resource.id}`)
}

const editResource = (resource) => {
  router.push(`/enterprise/resource/edit/${resource.id}`)
}

const viewDemand = (demand) => {
  router.push(`/enterprise/requirement/detail/${demand.id}`)
}

const editDemand = (demand) => {
  router.push(`/enterprise/requirement/edit/${demand.id}`)
}

const handleDateChange = (date) => {
  selectedDate.value = date
  console.log('选择日期:', date)
}

// 标记通知为已读
const markAsRead = async (notification) => {
  if (notification.is_read) return

  try {
    await notificationService.markNotificationAsRead(notification.id)
    // 更新本地数据
    notification.is_read = true
    notification.read_at = new Date().toISOString()

    // 更新未读计数
    await fetchUnreadCount()
  } catch (error) {
    console.error('标记通知为已读失败:', error)
  }
}

// 格式化日期
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleDateString('zh-CN')
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return ''

  const now = new Date()
  const time = new Date(timeStr)
  const diff = now - time
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return timeStr.split('T')[0]
}

// 初始化项目进度图表
const initProjectChart = () => {
  const chartDom = document.getElementById('projectChart')
  if (!chartDom) return

  projectChart = echarts.init(chartDom)
  updateProjectChart()
}

// 更新项目进度图表
const updateProjectChart = () => {
  if (!projectChart) return

  // 检查数据是否为空
  const hasData =
    (projectChartData.value.months.length > 0 &&
      projectChartData.value.completed.some((val) => val > 0)) ||
    projectChartData.value.inProgress.some((val) => val > 0) ||
    projectChartData.value.recruiting.some((val) => val > 0)

  if (!hasData) {
    // 显示空状态
    const option = {
      title: {
        text: '暂无项目数据',
        textStyle: {
          color: '#909399',
          fontSize: 14,
          fontWeight: 'normal'
        },
        left: 'center',
        top: 'center'
      }
    }
    projectChart.setOption(option)
    return
  }

  // 有数据时的正常显示
  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross',
        crossStyle: {
          color: '#999'
        }
      }
    },
    legend: {
      data: ['已完成', '进行中', '招募中']
    },
    xAxis: [
      {
        type: 'category',
        data: projectChartData.value.months,
        axisPointer: {
          type: 'shadow'
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '项目数量',
        min: 0,
        axisLabel: {
          formatter: '{value}'
        }
      }
    ],
    series: [
      {
        name: '已完成',
        type: 'bar',
        data: projectChartData.value.completed,
        itemStyle: {
          color: '#67c23a'
        }
      },
      {
        name: '进行中',
        type: 'bar',
        data: projectChartData.value.inProgress,
        itemStyle: {
          color: '#e6a23c'
        }
      },
      {
        name: '招募中',
        type: 'bar',
        data: projectChartData.value.recruiting,
        itemStyle: {
          color: '#409eff'
        }
      }
    ]
  }
  projectChart.setOption(option, true)
}

// 初始化技能分布图表
const initSkillChart = () => {
  const chartDom = document.getElementById('skillChart')
  if (!chartDom) return

  skillChart = echarts.init(chartDom)
  updateSkillChart()
}

// 更新技能分布图表
const updateSkillChart = () => {
  if (!skillChart) return

  // 检查数据是否为空
  const hasData = skillChartData.value && skillChartData.value.length > 0

  if (!hasData) {
    // 显示空状态
    const option = {
      title: {
        text: '暂无技能分布数据',
        textStyle: {
          color: '#909399',
          fontSize: 14,
          fontWeight: 'normal'
        },
        left: 'center',
        top: 'center'
      }
    }
    skillChart.setOption(option)
    return
  }

  // 有数据时的正常显示
  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left',
      data: skillChartData.value.filter((item) => item.showLegend).map((item) => item.name)
    },
    series: [
      {
        name: '技能分布',
        type: 'pie',
        radius: '50%',
        center: ['50%', '60%'],
        data: skillChartData.value,
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        itemStyle: {
          color: function (params) {
            const colors = ['#409eff', '#67c23a', '#e6a23c', '#f56c6c', '#909399', '#c0c4cc']
            return colors[params.dataIndex % colors.length]
          }
        }
      }
    ]
  }
  skillChart.setOption(option, true)
}

// 窗口大小改变时重新绘制图表
const handleResize = () => {
  if (projectChart) {
    projectChart.resize()
  }
  if (skillChart) {
    skillChart.resize()
  }
}

onMounted(async () => {
  await nextTick()

  // 初始化图表
  initProjectChart()
  initSkillChart()

  // 并行加载数据
  try {
    await Promise.all([
      fetchOverview(),
      fetchResources(),
      fetchDemands(),
      fetchProjects(),
      fetchNotifications(),
      fetchUnreadCount()
    ])
  } catch (error) {
    console.error('初始化数据加载失败:', error)
  }

  window.addEventListener('resize', handleResize)
})

// 清理
onBeforeUnmount(() => {
  if (projectChart) {
    projectChart.dispose()
  }
  if (skillChart) {
    skillChart.dispose()
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="enterprise-dashboard">
    <div class="dashboard-container">
      <!-- 页面标题 -->
      <div class="dashboard-header">
        <h1 class="dashboard-title">企业管理中心</h1>
        <p class="dashboard-subtitle">
          欢迎回来，{{ userStore.user.company_profile.organization.name }}
        </p>
      </div>

      <!-- 主体内容区域 -->
      <div class="dashboard-main-content">
        <!-- 左侧主要内容 -->
        <div class="left-content">
          <!-- 数据概览卡片 -->
          <div class="stats-grid">
            <el-card
              v-for="stat in dashboardStats"
              :key="stat.title"
              class="stat-card"
              shadow="hover"
            >
              <div class="stat-content">
                <div class="stat-header">
                  <h3 class="stat-title">{{ stat.title }}</h3>
                  <div class="stat-icon" :class="`stat-icon-${stat.color}`">
                    <font-awesome-icon :icon="stat.icon" />
                  </div>
                </div>
                <div class="stat-footer">
                  <div class="stat-value-section">
                    <span class="stat-value">{{ stat.value }}</span>
                    <span class="stat-change" :class="getGrowthClass(stat.change)">
                      <font-awesome-icon
                        :icon="stat.change >= 0 ? 'arrow-up' : 'arrow-down'"
                        class="arrow-icon"
                      />
                      {{ Math.abs(stat.change) }}%
                    </span>
                  </div>
                  <span class="stat-period">较上月</span>
                </div>
              </div>
            </el-card>
          </div>

          <!-- 项目进度和统计 -->
          <div class="charts-section">
            <div class="charts-grid">
              <el-card class="chart-card chart-card-large" shadow="hover">
                <template #header>
                  <div class="chart-header">
                    <h3>项目进度统计</h3>
                  </div>
                </template>
                <div v-loading="overviewLoading" class="chart-container">
                  <div id="projectChart" style="width: 100%; height: 100%"></div>
                </div>
              </el-card>

              <el-card class="chart-card" shadow="hover">
                <template #header>
                  <div class="chart-header">
                    <h3>项目技能分布</h3>
                  </div>
                </template>
                <div v-loading="overviewLoading" class="chart-container">
                  <div id="skillChart" style="width: 100%; height: 100%"></div>
                </div>
              </el-card>
            </div>
          </div>

          <!-- 项目管理 -->
          <div class="projects-section">
            <div class="section-header">
              <h3 class="section-title">项目管理</h3>
              <p class="section-subtitle">请左右滑动查看</p>
            </div>

            <el-card v-loading="projectsLoading" shadow="never" class="projects-card">
              <el-table :data="processedProjects" stripe style="width: 100%">
                <el-table-column label="项目名称" min-width="200">
                  <template #default="scope">
                    <div class="project-info">
                      <div class="project-icon" :class="`project-icon-${scope.row.iconColor}`">
                        <font-awesome-icon :icon="scope.row.icon" />
                      </div>
                      <div class="project-details">
                        <div class="project-name">{{ scope.row.name }}</div>
                        <div class="project-category">{{ scope.row.category }}</div>
                      </div>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column label="负责人" min-width="150">
                  <template #default="scope">
                    <div class="manager-info">
                      <el-avatar :size="32" :src="scope.row.manager.avatar" />
                      <div class="manager-details">
                        <div class="manager-name">{{ scope.row.manager.name }}</div>
                        <div class="manager-position">{{ scope.row.manager.position }}</div>
                      </div>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column label="进度" min-width="120">
                  <template #default="scope">
                    <div class="progress-section">
                      <el-progress :percentage="scope.row.progress" :show-text="false" />
                      <div class="progress-text">{{ scope.row.progress }}%</div>
                    </div>
                  </template>
                </el-table-column>

                <el-table-column prop="teamSize" label="团队规模" width="100">
                  <template #default="scope"> {{ scope.row.teamSize }}人 </template>
                </el-table-column>

                <el-table-column prop="startDate" label="开始日期" width="120" />

                <el-table-column label="状态" width="100">
                  <template #default="scope">
                    <el-tag :type="scope.row.statusType" size="small">
                      {{ scope.row.status }}
                    </el-tag>
                  </template>
                </el-table-column>

                <el-table-column label="操作" width="80" align="right">
                  <template #default="scope">
                    <el-button type="primary" link size="small" @click="viewProject(scope.row)">
                      查看
                    </el-button>
                  </template>
                </el-table-column>
              </el-table>

              <div class="pagination-wrapper">
                <el-pagination
                  v-model:current-page="currentPage"
                  v-model:page-size="pageSize"
                  :page-sizes="[4, 8]"
                  :total="total"
                  layout="total, sizes, prev, pager, next, jumper"
                  @size-change="handleSizeChange"
                  @current-change="handleCurrentChange"
                />
              </div>
            </el-card>
          </div>
        </div>

        <!-- 右侧边栏 -->
        <div class="right-sidebar">
          <!-- 日历 -->
          <el-card class="calendar-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <font-awesome-icon icon="calendar-alt" class="header-icon" />
                <h3>日历</h3>
              </div>
            </template>
            <el-calendar v-model="selectedDate" @input="handleDateChange">
              <template #date-cell="{ data }">
                <div class="calendar-cell">
                  {{ data.day.split('-')[2] }}
                </div>
              </template>
            </el-calendar>
          </el-card>

          <!-- 最近通知 -->
          <el-card class="notifications-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <font-awesome-icon icon="bell" class="header-icon" />
                <h3>最近通知</h3>
                <span v-if="unreadCount > 0" class="unread-count">
                  ({{ unreadCount }}条新通知)
                </span>
              </div>
            </template>

            <div v-loading="notificationsLoading" class="notifications-list">
              <div
                v-for="notification in notifications"
                :key="notification.id"
                class="notification-item"
                :class="{ 'notification-unread': !notification.is_read }"
                @click="markAsRead(notification)"
              >
                <div
                  class="notification-icon"
                  :class="`notification-${getNotificationType(notification)}`"
                >
                  <font-awesome-icon :icon="getNotificationIcon(notification)" />
                </div>
                <div class="notification-content">
                  <div class="notification-title">{{ notification.title }}</div>
                  <div class="notification-text">{{ notification.content }}</div>
                  <div class="notification-time">{{ formatTime(notification.created_at) }}</div>
                </div>
              </div>

              <!-- 空状态 -->
              <div
                v-if="!notificationsLoading && notifications.length === 0"
                class="empty-notifications"
              >
                <font-awesome-icon icon="bell" class="empty-icon" />
                <p>暂无通知</p>
              </div>
            </div>

            <!-- 查看更多链接 -->
            <div v-if="notifications.length > 0" class="notifications-footer">
              <router-link to="/enterprise/notification-center" class="view-more-link">
                查看全部通知
              </router-link>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 资源与需求卡片区域 -->
      <div class="bottom-sections">
        <!-- 需求管理卡片区域 -->
        <div class="demands-section">
          <div class="section-header">
            <h3 class="section-title">需求发布</h3>
            <router-link to="/enterprise/requirement-management" class="section-info"
              >查看更多 ></router-link
            >
          </div>

          <div v-loading="demandsLoading" class="cards-grid">
            <!-- 需求卡片 -->
            <el-card
              v-for="demand in processedDemands"
              :key="demand.id"
              class="demand-card"
              shadow="hover"
            >
              <div class="card-content">
                <div class="card-header-section">
                  <div class="card-icon" :class="`card-icon-${demand.iconColor}`">
                    <font-awesome-icon :icon="demand.icon" />
                  </div>
                  <div class="card-priority">
                    <el-tag :type="demand.statusType" size="small">
                      {{ demand.statusText }}
                    </el-tag>
                  </div>
                </div>

                <div class="card-body">
                  <h4 class="card-title">{{ demand.title }}</h4>
                  <p class="card-subtitle">{{ demand.brief }}</p>
                  <p class="card-description">{{ demand.description }}</p>

                  <div class="card-details">
                    <div class="detail-item">
                      <span class="detail-label">发布人:</span>
                      <span class="detail-value">{{ demand.publish_people }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">截止:</span>
                      <span class="detail-value">{{ formatDate(demand.finish_time) }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">浏览:</span>
                      <span class="detail-value">{{ demand.views }}次</span>
                    </div>
                  </div>
                </div>

                <div class="card-actions">
                  <el-button type="primary" size="small" @click="viewDemand(demand)">
                    <font-awesome-icon icon="eye" />
                    查看
                  </el-button>
                  <el-button type="info" size="small" plain @click="editDemand(demand)">
                    <font-awesome-icon icon="edit" />
                    编辑
                  </el-button>
                </div>
              </div>
            </el-card>

            <!-- 发布需求卡片 -->
            <el-card class="publish-card demand-publish-card" shadow="hover" @click="publishDemand">
              <div class="publish-content">
                <div class="publish-icon">
                  <font-awesome-icon icon="plus" />
                </div>
                <h4 class="publish-title">发布新需求</h4>
                <p class="publish-subtitle">点击添加新的需求</p>
              </div>
            </el-card>
          </div>
        </div>

        <!-- 资源管理卡片区域 -->
        <div class="resources-section">
          <div class="section-header">
            <h3 class="section-title">资源管理</h3>
            <router-link to="/enterprise/resource-management" class="section-info"
              >查看更多 ></router-link
            >
          </div>

          <div v-loading="resourcesLoading" class="cards-grid">
            <!-- 资源卡片 -->
            <el-card
              v-for="resource in processedResources"
              :key="resource.id"
              class="resource-card"
              shadow="hover"
            >
              <div class="card-content">
                <div class="card-header-section">
                  <div class="card-icon" :class="`card-icon-${resource.iconColor}`">
                    <font-awesome-icon :icon="resource.icon" />
                  </div>
                  <div class="card-status">
                    <el-tag :type="resource.statusType" size="small">
                      {{ resource.statusText }}
                    </el-tag>
                  </div>
                </div>

                <div class="card-body">
                  <h4 class="card-title">{{ resource.title }}</h4>
                  <p class="card-subtitle">
                    {{ resource.typeText }}
                    <span v-if="resource.tag2 && resource.tag2.length">
                      · {{ resource.tag2[0].name }}
                    </span>
                  </p>
                  <p class="card-description">{{ resource.description }}</p>

                  <div class="card-details">
                    <div class="detail-item">
                      <span class="detail-label">创建者:</span>
                      <span class="detail-value">{{ resource.create_person_name }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">下载量:</span>
                      <span class="detail-value">{{ resource.downloads }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">浏览量:</span>
                      <span class="detail-value">{{ resource.views }}</span>
                    </div>
                    <div class="detail-item">
                      <span class="detail-label">更新:</span>
                      <span class="detail-value">{{ formatDate(resource.updated_at) }}</span>
                    </div>
                  </div>
                </div>

                <div class="card-actions">
                  <el-button type="primary" size="small" @click="viewResource(resource)">
                    <font-awesome-icon icon="eye" />
                    查看
                  </el-button>
                  <el-button type="info" size="small" plain @click="editResource(resource)">
                    <font-awesome-icon icon="edit" />
                    编辑
                  </el-button>
                </div>
              </div>
            </el-card>

            <!-- 发布资源卡片 -->
            <el-card
              class="publish-card resource-publish-card"
              shadow="hover"
              @click="publishResource"
            >
              <div class="publish-content">
                <div class="publish-icon">
                  <font-awesome-icon icon="plus" />
                </div>
                <h4 class="publish-title">发布新资源</h4>
                <p class="publish-subtitle">点击添加新的资源</p>
              </div>
            </el-card>
          </div>
        </div>
      </div>
    </div>

    <!-- 发布方式选择模态框 -->
    <div v-if="showPublishModal" class="modal-overlay" @click="closePublishModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3 class="modal-title">选择发布方式</h3>
          <button class="close-btn" @click="closePublishModal">
            <font-awesome-icon :icon="['fas', 'times']" />
          </button>
        </div>
        <div class="modal-body">
          <div class="publish-options">
            <button class="publish-option" @click="selectPublishType('chat')">
              <div class="option-icon chat">
                <font-awesome-icon :icon="['fas', 'comments']" />
              </div>
              <div class="option-content">
                <h4 class="option-title">对话式发布</h4>
                <p class="option-description">通过智能对话引导，快速描述项目需求</p>
                <div class="option-features">
                  <span class="feature">• 智能推荐</span>
                  <span class="feature">• 快速便捷</span>
                  <span class="feature">• 适合新手</span>
                </div>
              </div>
            </button>
            <button class="publish-option" @click="selectPublishType('form')">
              <div class="option-icon form">
                <font-awesome-icon :icon="['fas', 'file-text']" />
              </div>
              <div class="option-content">
                <h4 class="option-title">表单式发布</h4>
                <p class="option-description">填写详细表单，精确定义项目要求</p>
                <div class="option-features">
                  <span class="feature">• 详细配置</span>
                  <span class="feature">• 精确控制</span>
                  <span class="feature">• 适合专业用户</span>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.enterprise-dashboard {
  padding: 24px;
  background-color: #f5f7fa;
}

.dashboard-container {
  max-width: 1500px;
  margin: 0 auto;
  width: 100%;
}

.dashboard-header {
  margin-bottom: 32px;

  .dashboard-title {
    font-size: clamp(1.5rem, 3vw, 2rem);
    font-weight: bold;
    color: #303133;
    margin: 0 0 8px 0;
  }

  .dashboard-subtitle {
    color: #909399;
    margin: 0;
  }
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 24px;
  margin-bottom: 8px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr 1fr;
  }
}

.stat-card {
  .stat-content {
    .stat-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 16px;

      .stat-title {
        color: #909399;
        font-weight: 500;
        font-size: 14px;
        margin: 0;
      }

      .stat-icon {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;

        &.stat-icon-primary {
          background-color: rgba(64, 158, 255, 0.1);
          color: #409eff;
        }

        &.stat-icon-warning {
          background-color: rgba(230, 162, 60, 0.1);
          color: #e6a23c;
        }

        &.stat-icon-success {
          background-color: rgba(103, 194, 58, 0.1);
          color: #67c23a;
        }

        &.stat-icon-info {
          background-color: rgba(144, 147, 153, 0.1);
          color: #909399;
        }
      }
    }

    .stat-footer {
      display: flex;
      align-items: flex-end;
      justify-content: space-between;

      @media (max-width: 768px) {
        flex-direction: column;
        align-items: flex-start;
        gap: 8px;
      }

      .stat-value-section {
        display: flex;
        align-items: center;

        .stat-value {
          font-size: 24px;
          font-weight: bold;
          color: #303133;
        }

        .stat-change {
          font-size: 12px;
          margin-left: 8px;
          display: flex;
          align-items: center;

          &.growth-positive {
            color: #10b981; // 增长为绿色
          }

          &.growth-negative {
            color: #ef4444; // 减少为红色
          }

          &.growth-zero {
            color: #9ca3af; // 无变化为灰色
          }

          .arrow-icon {
            margin-right: 4px;
          }
        }
      }
      .stat-period {
        color: #c0c4cc;
        font-size: 12px;
      }
    }
  }
}

.dashboard-main-content {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 24px;
  margin-bottom: 48px;
  overflow: hidden; /* 防止子元素溢出 */

  @media (max-width: 1200px) {
    grid-template-columns: 1fr;
  }
}

.left-content {
  display: flex;
  flex-direction: column;
  gap: 32px;
  min-width: 0; /* 允许flex项目收缩到比内容更小 */
  overflow: hidden; /* 防止子元素溢出 */
}

.charts-section {
  .charts-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 24px;

    /* 与dashboard-main-content保持一致的断点 */
    @media (max-width: 1200px) {
      grid-template-columns: 1fr;
    }
  }
}

.chart-card {
  .chart-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    h3 {
      font-weight: 600;
      color: #303133;
      margin: 0;
    }
  }

  .chart-container {
    height: 300px;
  }

  .chart-buttons {
    display: flex;
    gap: 8px;
  }
}

.right-sidebar {
  display: flex;
  flex-direction: column;
  gap: 24px;

  @media (max-width: 1200px) {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.calendar-card,
.notifications-card {
  .card-header {
    display: flex;
    align-items: center;
    gap: 8px;

    .header-icon {
      color: #409eff;
    }

    h3 {
      margin: 0;
      font-weight: 600;
      color: #303133;
      flex: 1;
    }

    .unread-count {
      color: #409eff;
      font-size: 13px;
      margin-left: auto;
    }
  }
}

.calendar-card {
  :deep(.el-calendar) {
    .el-calendar__header {
      padding: 8px 10px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-wrap: nowrap;

      .el-calendar__title {
        font-size: 16px;
        color: #303133;
        margin: 0;
        white-space: nowrap;
      }

      .el-button-group {
        display: flex;
        align-items: center;
        gap: 4px;
        flex-shrink: 0;
      }
    }
    .el-calendar__body {
      padding: 8px;
    }

    .el-calendar-table {
      .el-calendar-day {
        height: auto;
      }
      th {
        padding: 4px 0;
        font-size: 12px;
        color: #606266;
      }

      td {
        border-right: none;
        border-bottom: 1px solid #ebeef5;
        padding: 2px;

        &.is-selected {
          .calendar-cell {
            background-color: #409eff;
            color: white;
            border-radius: 4px;
          }
        }
      }
    }
  }

  .calendar-cell {
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    margin: 1px;
    transition: all 0.2s;

    &:hover {
      background-color: #f0f9ff;
      border-radius: 4px;
    }
  }
}

.notifications-card {
  .notifications-list {
    max-height: 475px;
    overflow-y: auto;

    /* 美化滚动条 */
    &::-webkit-scrollbar {
      width: 6px;
    }

    &::-webkit-scrollbar-track {
      background: #f5f7fa;
      border-radius: 3px;
    }

    &::-webkit-scrollbar-thumb {
      background: #c0c4cc;
      border-radius: 3px;

      &:hover {
        background: #909399;
      }
    }
  }

  .notification-item {
    display: flex;
    align-items: flex-start;
    padding: 12px;
    border-radius: 6px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.2s;

    &:hover {
      background-color: #f5f7fa;
    }

    &.notification-unread {
      background-color: rgba(64, 158, 255, 0.05);
      border-left: 3px solid #409eff;
    }

    .notification-icon {
      width: 32px;
      height: 32px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 12px;
      flex-shrink: 0;

      &.notification-success {
        background-color: rgba(103, 194, 58, 0.1);
        color: #67c23a;
      }

      &.notification-warning {
        background-color: rgba(230, 162, 60, 0.1);
        color: #e6a23c;
      }

      &.notification-info {
        background-color: rgba(64, 158, 255, 0.1);
        color: #409eff;
      }

      &.notification-error {
        background-color: rgba(245, 108, 108, 0.1);
        color: #f56c6c;
      }
    }

    .notification-content {
      flex: 1;

      .notification-title {
        font-weight: 500;
        color: #303133;
        margin-bottom: 4px;
        font-size: 14px;
      }

      .notification-text {
        color: #606266;
        font-size: 12px;
        line-height: 1.4;
        margin-bottom: 4px;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
      }

      .notification-time {
        color: #c0c4cc;
        font-size: 11px;
      }
    }
  }

  .empty-notifications {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    text-align: center;

    .empty-icon {
      font-size: 32px;
      color: #c0c4cc;
      margin-bottom: 12px;
    }

    p {
      color: #909399;
      margin: 0;
      font-size: 14px;
    }
  }

  .notifications-footer {
    margin-top: 16px;
    padding-top: 16px;
    border-top: 1px solid #f0f0f0;
    text-align: center;

    .view-more-link {
      color: #409eff;
      text-decoration: none;
      font-size: 14px;
      transition: color 0.2s;

      &:hover {
        color: #66b1ff;
      }
    }
  }
}

.projects-card {
  :deep(.el-card__body) {
    display: flex;
    flex-direction: column;

    @media (min-width: 1535px) {
      min-height: 425px;
    }
  }

  /* 表格容器添加水平滚动 */
  :deep(.el-table) {
    width: 100%;

    .el-table__body-wrapper {
      overflow-x: auto; /* 表格内容水平滚动 */
    }
  }

  .project-info {
    display: flex;
    align-items: center;

    .project-icon {
      width: 40px;
      height: 40px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      margin-right: 12px;
      flex-shrink: 0;

      &.project-icon-primary {
        background-color: rgba(64, 158, 255, 0.1);
        color: #409eff;
      }

      &.project-icon-warning {
        background-color: rgba(230, 162, 60, 0.1);
        color: #e6a23c;
      }

      &.project-icon-success {
        background-color: rgba(103, 194, 58, 0.1);
        color: #67c23a;
      }

      &.project-icon-info {
        background-color: rgba(144, 147, 153, 0.1);
        color: #909399;
      }

      &.project-icon-danger {
        background-color: rgba(245, 108, 108, 0.1);
        color: #f56c6c;
      }
    }

    .project-details {
      .project-name {
        font-weight: 500;
        color: #303133;
        margin-bottom: 4px;
      }

      .project-category {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .manager-info {
    display: flex;
    align-items: center;

    .manager-details {
      margin-left: 12px;

      .manager-name {
        font-weight: 500;
        color: #303133;
        margin-bottom: 4px;
      }

      .manager-position {
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .progress-section {
    margin-top: 1rem;
    .progress-text {
      font-size: 12px;
      color: #909399;
      margin-top: 4px;
      text-align: center;
    }
  }

  .pagination-wrapper {
    display: flex;
    justify-content: center;
    margin-top: auto;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;
  }
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;

  .section-title {
    font-weight: 600;
    font-size: 18px;
    color: #303133;
    margin: 0;
  }

  .section-subtitle {
    display: none;
    font-size: 14px;
    color: #909399;
    margin: 0;
  }

  @media (max-width: 1500px) {
    .section-subtitle {
      display: block;
    }
  }

  .section-info {
    color: #2b66db;
    font-size: 14px;
    text-decoration: none;
    transition: color 0.2s;

    &:hover {
      color: #1a4bc7;
    }
  }

  .section-actions {
    display: flex;
    gap: 12px;
  }

  .button-icon {
    margin-right: 8px;
  }
}

/* 底部卡片区域样式 */
.bottom-sections {
  display: flex;
  flex-direction: column;
  gap: 48px;
}

.resources-section,
.demands-section {
  width: 100%;
}

.cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr; /* 小屏幕强制单列 */
  }

  /* 中等屏幕优化 */
  @media (max-width: 1200px) and (min-width: 769px) {
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  }

  /* 超小屏幕 */
  @media (max-width: 480px) {
    grid-template-columns: 1fr;
    gap: 16px; /* 减小间距 */
  }
}

.resource-card,
.demand-card {
  height: 100%;
  transition:
    transform 0.2s,
    box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
  }

  .card-content {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .card-header-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;

    .card-icon {
      width: 48px;
      height: 48px;
      border-radius: 12px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;

      &.card-icon-primary {
        background-color: rgba(64, 158, 255, 0.1);
        color: #409eff;
      }

      &.card-icon-warning {
        background-color: rgba(230, 162, 60, 0.1);
        color: #e6a23c;
      }

      &.card-icon-success {
        background-color: rgba(103, 194, 58, 0.1);
        color: #67c23a;
      }

      &.card-icon-info {
        background-color: rgba(144, 147, 153, 0.1);
        color: #909399;
      }

      &.card-icon-danger {
        background-color: rgba(245, 108, 108, 0.1);
        color: #f56c6c;
      }
    }

    .card-status,
    .card-priority {
      flex-shrink: 0;
    }
  }

  .card-body {
    flex: 1;
    margin-bottom: 16px;

    .card-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
      line-height: 1.4;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      min-height: 44px; /* 确保标题区域高度统一 */
    }

    .card-subtitle {
      font-size: 13px;
      color: #909399;
      margin: 0 0 12px 0;
    }

    .card-description {
      font-size: 14px;
      color: #606266;
      line-height: 1.5;
      margin: 0 0 16px 0;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
      min-height: 42px; /* 2行文字的高度，确保统一 */
    }

    .card-details {
      margin-top: auto; /* 将详情部分推到底部 */

      .detail-item {
        display: flex;
        align-items: center;
        margin-bottom: 6px;
        font-size: 12px;

        .detail-label {
          color: #909399;
          margin-right: 8px;
          min-width: 50px;
        }

        .detail-value {
          color: #606266;
          flex: 1;
        }
      }
    }
  }

  .card-actions {
    display: flex;
    gap: 8px;
    margin-top: auto;

    .el-button {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 4px;
    }
  }
}

.publish-card {
  border: 2px dashed #d9d9d9;
  background-color: #fafafa;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  :deep(.el-card__body) {
    align-content: center;
  }

  &:hover {
    border-color: #409eff;
    background-color: rgba(64, 158, 255, 0.05);
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(64, 158, 255, 0.15);

    .publish-icon {
      color: #409eff;
      background-color: rgba(64, 158, 255, 0.1);
    }

    .publish-title {
      color: #409eff;
    }
  }

  .publish-content {
    text-align: center;

    .publish-icon {
      width: 64px;
      height: 64px;
      border-radius: 50%;
      background-color: rgba(144, 147, 153, 0.1);
      color: #909399;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      margin: 0 auto 16px;
      transition: all 0.3s ease;
    }

    .publish-title {
      font-size: 16px;
      font-weight: 600;
      color: #606266;
      margin: 0 0 8px 0;
      transition: color 0.3s ease;
    }

    .publish-subtitle {
      font-size: 13px;
      color: #909399;
      margin: 0;
    }
  }
}

:deep(.el-card__body) {
  height: 100%;
}

/* 模态框样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(2px);
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.8) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 24px 16px;
  border-bottom: 1px solid #ebeef5;

  .modal-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
    margin: 0;
  }

  .close-btn {
    background: none;
    border: none;
    font-size: 16px;
    color: #909399;
    cursor: pointer;
    padding: 8px;
    border-radius: 4px;
    transition: all 0.2s;

    &:hover {
      background-color: #f5f7fa;
      color: #606266;
    }
  }
}

.modal-body {
  padding: 24px;
}

.publish-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.publish-option {
  display: flex;
  align-items: flex-start;
  padding: 20px;
  border: 2px solid #ebeef5;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  width: 100%;

  &:hover {
    border-color: #409eff;
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(64, 158, 255, 0.15);

    .option-icon {
      &.chat {
        background-color: rgba(64, 158, 255, 0.15);
        color: #409eff;
      }
      &.form {
        background-color: rgba(103, 194, 58, 0.15);
        color: #67c23a;
      }
    }
  }

  .option-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    margin-right: 16px;
    flex-shrink: 0;
    transition: all 0.3s ease;

    &.chat {
      background-color: rgba(64, 158, 255, 0.1);
      color: #409eff;
    }

    &.form {
      background-color: rgba(103, 194, 58, 0.1);
      color: #67c23a;
    }
  }

  .option-content {
    flex: 1;

    .option-title {
      font-size: 16px;
      font-weight: 600;
      color: #303133;
      margin: 0 0 8px 0;
    }

    .option-description {
      font-size: 14px;
      color: #606266;
      margin: 0 0 12px 0;
      line-height: 1.5;
    }

    .option-features {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;

      .feature {
        font-size: 12px;
        color: #909399;
        background-color: #f5f7fa;
        padding: 4px 8px;
        border-radius: 4px;
      }
    }
  }
}

@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    max-height: 95vh;
  }

  .publish-option {
    flex-direction: column;
    text-align: center;

    .option-icon {
      margin: 0 auto 16px;
    }
  }
}
</style>
