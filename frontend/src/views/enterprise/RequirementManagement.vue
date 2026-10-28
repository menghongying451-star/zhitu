<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import * as echarts from 'echarts/core'
import { LineChart } from 'echarts/charts'
import { GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'

// 注册必需的组件
echarts.use([GridComponent, LineChart, CanvasRenderer])

import { requirementService } from '@/api'
import { useUserStore } from '@/stores'
import { useRouter } from 'vue-router'

// 导入项目中用到的图标
import {
  faBars,
  faFilter,
  faDownload,
  faPlus,
  faBullhorn,
  faArrowUp,
  faArrowDown,
  faClock,
  faMinus,
  faCheckCircle,
  faUsers,
  faRocket,
  faCode,
  faChartBar,
  faPaintBrush,
  faCogs,
  faSearch,
  faEdit,
  faEye,
  faShareAlt,
  faTrash,
  faDollarSign,
  faCalendar,
  faStar,
  faChevronLeft,
  faChevronRight,
  faUpload,
  faComments,
  faFileText,
  faTimes,
  faInbox,
  faSpinner,
  faSyncAlt,
  faSort,
  faSortAlphaDown,
  faSortAlphaUp,
  faPlay,
  faExclamationTriangle,
  faPowerOff
} from '@fortawesome/free-solid-svg-icons'

// 导入outline图标
import { faBookmark } from '@fortawesome/free-regular-svg-icons'

// 将图标添加到库中
library.add(
  faBars,
  faFilter,
  faDownload,
  faPlus,
  faBullhorn,
  faArrowUp,
  faArrowDown,
  faClock,
  faMinus,
  faCheckCircle,
  faUsers,
  faRocket,
  faCode,
  faChartBar,
  faPaintBrush,
  faCogs,
  faSearch,
  faEdit,
  faEye,
  faShareAlt,
  faTrash,
  faDollarSign,
  faCalendar,
  faStar,
  faChevronLeft,
  faChevronRight,
  faBookmark,
  faUpload,
  faComments,
  faFileText,
  faTimes,
  faInbox,
  faSpinner,
  faSyncAlt,
  faSort,
  faSortAlphaDown,
  faSortAlphaUp,
  faPlay,
  faExclamationTriangle,
  faPowerOff
)

const router = useRouter()
const userStore = useUserStore()

// Reactive data
const searchQuery = ref('')
const statusFilter = ref('')
const typeFilter = ref('')
const budgetMin = ref('')
const budgetMax = ref('')
const timeStart = ref('')
const timeEnd = ref('')
const sortType = ref('')
const sortOrder = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const totalPages = ref(0)
const totalCount = ref(0)
const showPublishModal = ref(false)

// Loading states
const loading = ref(false)
const requirementsLoading = ref(false)
const statsLoading = ref(false)

// Data
const statsData = ref({
  totalRequirements: 0,
  statusCounts: {
    under_review: 0,
    review_failed: 0,
    in_progress: 0,
    completed: 0,
    paused: 0
  },
  chartData: {
    dates: [],
    publishCount: []
  }
})

const requirements = ref([])
const error = ref(null)

// Computed properties
const inProgressCount = computed(() => statsData.value.statusCounts.in_progress || 0)
const completedCount = computed(() => statsData.value.statusCounts.completed || 0)
const underReviewCount = computed(() => statsData.value.statusCounts.under_review || 0)
const pausedCount = computed(() => statsData.value.statusCounts.paused || 0)

const organizationId = computed(() => userStore.user?.company_profile?.organization?.id)

// 工具函数：格式化日期
const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 工具函数：提取标签
const extractTags = (tag1, tag2) => {
  const tags = []
  if (tag1 && Array.isArray(tag1)) {
    tags.push(...tag1.map((tag) => tag.name))
  }
  if (tag2 && Array.isArray(tag2)) {
    tags.push(
      ...tag2.map((tag) => {
        // 对tag2只取最后一部分，例如"互联网-后端开发-c/c++"展示"c/c++"
        const parts = tag.name.split('-')
        return parts[parts.length - 1]
      })
    )
  }
  return tags
}

// 工具函数：解析预算范围
const parseBudget = (budgetString) => {
  if (!budgetString) return { min: 0, max: 0, display: '未设置' }

  const parts = budgetString.split('-')
  if (parts.length === 2) {
    const min = parseInt(parts[0])
    const max = parseInt(parts[1])
    return {
      min,
      max,
      display: `${min}-${max}万`
    }
  }
  return { min: 0, max: 0, display: budgetString }
}

const formatDateToString = (date) => {
  if (!date) return ''

  // 确保是Date对象
  const dateObj = date instanceof Date ? date : new Date(date)

  // 格式化为 YYYY-MM-DD
  const year = dateObj.getFullYear()
  const month = String(dateObj.getMonth() + 1).padStart(2, '0')
  const day = String(dateObj.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

// API Methods
const fetchStatistics = async () => {
  if (!organizationId.value) return

  try {
    statsLoading.value = true
    error.value = null
    const response = await requirementService.getRequirementStatistics(organizationId.value)

    if (response.status === 'success') {
      // 根据新的接口结构更新数据
      statsData.value = {
        totalRequirements: response.data.totalRequirements,
        statusCounts: response.data.statusCounts || {
          under_review: 0,
          review_failed: 0,
          in_progress: 0,
          completed: 0,
          paused: 0
        },
        chartData: response.data.chartData || {
          dates: [],
          publishCount: []
        }
      }
    }
  } catch (err) {
    console.error('获取统计数据失败:', err)
    error.value = '获取统计数据失败'
  } finally {
    statsLoading.value = false
  }
}

const fetchRequirements = async (page = 1) => {
  if (!organizationId.value) return

  try {
    requirementsLoading.value = true
    error.value = null

    const params = {
      page,
      page_size: pageSize.value,
      ...(searchQuery.value && { keyword: searchQuery.value }),
      ...(statusFilter.value && { status: statusFilter.value }),
      ...(sortType.value && { sort_type: sortType.value }),
      ...(sortOrder.value && { sort_order: sortOrder.value })
    }

    // 处理预算筛选
    if (budgetMin.value || budgetMax.value) {
      if (budgetMin.value && budgetMax.value) {
        // 范围筛选：min-max
        params.budget = `${budgetMin.value}-${budgetMax.value}`
      } else if (budgetMin.value) {
        // 单值筛选
        params.budget = budgetMin.value
      } else if (budgetMax.value) {
        // 单值筛选
        params.budget = budgetMax.value
      }
    }

    // 处理时间筛选
    if (timeStart.value || timeEnd.value) {
      if (timeStart.value && timeEnd.value) {
        // 范围筛选：startDate-endDate
        const startStr = formatDateToString(timeStart.value)
        const endStr = formatDateToString(timeEnd.value)
        params.time = `${startStr}-${endStr}`
      } else if (timeStart.value) {
        // 单日筛选
        params.time = formatDateToString(timeStart.value)
      } else if (timeEnd.value) {
        // 单日筛选
        params.time = formatDateToString(timeEnd.value)
      }
    }

    const response = await requirementService.getRequirementList(organizationId.value, params)

    if (response.status === 'success') {
      requirements.value = response.data.requirements.map((req) => {
        const budgetInfo = parseBudget(req.budget)
        const tags = extractTags(req.tag1, req.tag2)

        return {
          id: req.id,
          title: req.title,
          status: req.status,
          urgent: false, // 根据实际API字段调整
          publishDate: formatDate(req.created_at),
          deadline: req.finish_time,
          budget: budgetInfo,
          teamSize: req.people_count,
          description: req.brief,
          fullDescription: req.description,
          tags: tags,
          applicants: req.applications || 0,
          views: req.views || 0,
          joinedCount: req.joined_count || 0,
          publisher: req.publish_people,
          bookmarked: false, // 需要单独的接口获取收藏状态
          organization: req.organization,
          supportProvided: req.support_provided,
          resources: req.resources || [],
          files: req.files || [],
          createdAt: req.created_at,
          updatedAt: req.updated_at
        }
      })

      // 更新分页信息
      const pagination = response.data.pagination
      currentPage.value = pagination.current_page
      totalPages.value = pagination.total_pages
      totalCount.value = pagination.total_count
    }
  } catch (err) {
    console.error('获取需求列表失败:', err)
    error.value = '获取需求列表失败'
    requirements.value = []
  } finally {
    requirementsLoading.value = false
  }
}

const refreshData = async () => {
  loading.value = true
  try {
    await Promise.all([fetchStatistics(), fetchRequirements(currentPage.value)])
  } finally {
    loading.value = false
  }
}

// Search and filter methods
const handleSearch = () => {
  currentPage.value = 1
  fetchRequirements(1)
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchRequirements(1)
}

// ElementPlus 分页事件处理
const handleCurrentChange = (page) => {
  currentPage.value = page
  fetchRequirements(page)
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  fetchRequirements(1)
}

// Watch for filter changes - 添加新的排序字段
watch([statusFilter, budgetMin, budgetMax, timeStart, timeEnd, sortType, sortOrder], () => {
  handleFilterChange()
})

// Other methods
const showPublishOptions = () => {
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

const toggleRequirementStatus = (id, currentStatus) => {
  const newStatus = currentStatus === 'paused' ? 'in_progress' : 'paused'
  const actionText = newStatus === 'paused' ? '暂停' : '恢复'

  ElMessageBox.confirm(`确定要${actionText}这个需求吗？`, `确认${actionText}`, {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      requirementService.updateRequirement(id, { status: newStatus }).then(() => {
        ElMessage.success(`${actionText}成功`)
        fetchRequirements(currentPage.value)
      })
    })
    .catch(() => {
      ElMessage.info(`已取消${actionText}`)
    })
}

const deleteRequirement = (id) => {
  ElMessageBox.confirm('确定要删除这个需求吗？此操作不可恢复。', '确认删除', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    requirementService.deleteRequirement(id).then(() => {
      ElMessage.success('删除成功')
      fetchRequirements(currentPage.value)
    })
  })
}

// 修改 initChart 方法
const initChart = () => {
  // 使用 nextTick 确保DOM已经更新
  nextTick(() => {
    const chartDom = document.getElementById('requirementChart')
    if (!chartDom || !statsData.value.chartData.dates.length) {
      console.log('图表容器未找到或数据为空:')
      return
    }

    // 销毁已存在的图表实例，避免重复初始化
    echarts.dispose(chartDom)

    const myChart = echarts.init(chartDom)

    const option = {
      grid: {
        top: 20,
        left: 30,
        right: 20,
        bottom: 30
      },
      xAxis: {
        type: 'category',
        data: statsData.value.chartData.dates,
        axisLine: {
          lineStyle: {
            color: '#e5e7eb'
          }
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#6b7280',
          fontSize: 12
        }
      },
      yAxis: {
        type: 'value',
        axisLine: {
          show: false
        },
        axisTick: {
          show: false
        },
        axisLabel: {
          color: '#6b7280',
          fontSize: 12
        },
        splitLine: {
          lineStyle: {
            color: '#f3f4f6'
          }
        }
      },
      series: [
        {
          data: statsData.value.chartData.publishCount,
          type: 'line',
          smooth: true,
          lineStyle: {
            color: '#3b82f6',
            width: 3
          },
          symbol: 'circle',
          symbolSize: 6,
          itemStyle: {
            color: '#3b82f6'
          },
          areaStyle: {
            color: {
              type: 'linear',
              x: 0,
              y: 0,
              x2: 0,
              y2: 1,
              colorStops: [
                {
                  offset: 0,
                  color: 'rgba(59, 130, 246, 0.1)'
                },
                {
                  offset: 1,
                  color: 'rgba(59, 130, 246, 0.01)'
                }
              ]
            }
          }
        }
      ]
    }

    myChart.setOption(option)

    // 响应式处理
    const resizeHandler = () => {
      myChart.resize()
    }

    // 移除之前的监听器，避免重复绑定
    window.removeEventListener('resize', resizeHandler)
    window.addEventListener('resize', resizeHandler)
  })
}

// Watch for chart data changes
watch(
  () => statsData.value.chartData,
  () => {
    initChart()
  },
  { deep: true }
)

// 添加一个计算属性来检查是否有活跃的筛选条件 - 包含新的排序字段
const hasActiveFilters = computed(() => {
  return !!(
    searchQuery.value ||
    statusFilter.value ||
    budgetMin.value ||
    budgetMax.value ||
    timeStart.value ||
    timeEnd.value ||
    sortType.value ||
    sortOrder.value
  )
})

// 添加活跃筛选条件的数量 - 包含新的排序字段
const activeFiltersCount = computed(() => {
  let count = 0
  if (searchQuery.value) count++
  if (statusFilter.value) count++
  if (budgetMin.value || budgetMax.value) count++
  if (timeStart.value || timeEnd.value) count++
  if (sortType.value) count++
  if (sortOrder.value) count++
  return count
})

// 清除所有筛选条件的方法 - 包含新的排序字段
const clearAllFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  budgetMin.value = ''
  budgetMax.value = ''
  timeStart.value = ''
  timeEnd.value = ''
  sortType.value = ''
  sortOrder.value = ''

  // 重置到第一页并重新获取数据
  currentPage.value = 1
  fetchRequirements(1)
}

// 清除单个筛选条件的方法 - 添加新的排序字段
const clearSingleFilter = (filterName) => {
  switch (filterName) {
    case 'search':
      searchQuery.value = ''
      break
    case 'status':
      statusFilter.value = ''
      break
    case 'budget':
      budgetMin.value = ''
      budgetMax.value = ''
      break
    case 'time':
      timeStart.value = ''
      timeEnd.value = ''
      break
    case 'sortType':
      sortType.value = ''
      break
    case 'sortOrder':
      sortOrder.value = ''
      break
  }

  currentPage.value = 1
  fetchRequirements(1)
}

const getBudgetText = () => {
  if (budgetMin.value && budgetMax.value) {
    return `${budgetMin.value}-${budgetMax.value}万`
  } else if (budgetMin.value) {
    return `${budgetMin.value}万起`
  } else if (budgetMax.value) {
    return `${budgetMax.value}万内`
  }
  return ''
}

const getTimeText = () => {
  if (timeStart.value && timeEnd.value) {
    const startStr = formatDateToString(timeStart.value)
    const endStr = formatDateToString(timeEnd.value)
    return `${startStr} 到 ${endStr}`
  } else if (timeStart.value) {
    return `${formatDateToString(timeStart.value)}`
  } else if (timeEnd.value) {
    return `${formatDateToString(timeEnd.value)}`
  }
  return ''
}

const getStatusText = (status) => {
  const statusMap = {
    under_review: '审核中',
    review_failed: '审核失败',
    in_progress: '进行中',
    completed: '已完成',
    paused: '已暂停'
  }
  return statusMap[status] || status
}

const getSortTypeText = (sortType) => {
  const sortTypeMap = {
    name: '按名称',
    time: '按时间',
    view: '按浏览量'
  }
  return sortTypeMap[sortType] || sortType
}

const getSortOrderText = (sortOrder) => {
  const sortOrderMap = {
    up: '升序',
    down: '降序'
  }
  return sortOrderMap[sortOrder] || sortOrder
}

// 根据标签类型获取颜色类
const getTagColorClass = () => {
  // 统一使用蓝色
  return 'blue'
}

// Lifecycle
onMounted(async () => {
  // 等待用户信息加载完成
  if (organizationId.value) {
    await refreshData()
  } else {
    // 如果没有组织ID，监听用户信息变化
    const unwatch = watch(organizationId, async (newId) => {
      if (newId) {
        await refreshData()
        unwatch() // 取消监听
      }
    })
  }
})
</script>

<template>
  <div class="requirements-page">
    <div class="container">
      <!-- Header Section -->
      <div class="header-section">
        <div class="header-content">
          <div class="title-section">
            <h1 class="page-title">需求发布</h1>
            <p class="page-subtitle">发布项目需求，寻找合适的人才和资源</p>
          </div>
          <div class="action-buttons">
            <button
              class="btn btn-secondary"
              @click="refreshData()"
              :disabled="loading || requirementsLoading"
            >
              <FontAwesomeIcon
                :icon="['fas', 'sync-alt']"
                class="mr-2"
                :class="{ 'fa-spin': loading || requirementsLoading }"
              />
              {{ loading || requirementsLoading ? '刷新中...' : '刷新数据' }}
            </button>
            <button class="btn btn-primary" @click="showPublishOptions">
              <font-awesome-icon :icon="['fas', 'plus']" />
              发布新需求
            </button>
          </div>
        </div>
      </div>

      <!-- 错误提示 -->
      <div v-if="error" class="error-message">
        <div class="error-content">
          <font-awesome-icon :icon="['fas', 'exclamation-triangle']" />
          {{ error }}
          <button class="btn btn-sm btn-outline" @click="refreshData()">重试</button>
        </div>
      </div>

      <!-- 需求发布和数据统计区域 -->
      <div class="publish-stats-section">
        <!-- 需求发布卡片 -->
        <div class="publish-card">
          <div class="upload-area" @click="showPublishOptions">
            <div class="upload-icon">
              <font-awesome-icon :icon="['fas', 'upload']" />
            </div>
            <h3 class="upload-title">发布新需求</h3>
            <p class="upload-subtitle">点击选择发布方式</p>
            <div class="upload-hint">支持对话式和表单式发布</div>
          </div>
        </div>

        <!-- 数据统计卡片 -->
        <div class="stats-card">
          <div class="stats-header">
            <h3 class="stats-title">需求发布趋势</h3>
            <p class="stats-subtitle">最近7周数据</p>
          </div>
          <div class="stats-content" v-if="!statsLoading">
            <div class="chart-container">
              <div id="requirementChart" class="chart"></div>
            </div>
            <div class="stats-summary">
              <div class="stat-item">
                <div class="stat-value">{{ statsData.totalRequirements }}</div>
                <div class="stat-label">总需求数量</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ inProgressCount }}</div>
                <div class="stat-label">进行中</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ completedCount }}</div>
                <div class="stat-label">已完成</div>
              </div>
            </div>
          </div>
          <div v-else class="stats-loading">
            <font-awesome-icon :icon="['fas', 'spinner']" class="fa-spin" />
            加载统计数据中...
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

      <!-- Search and Filter Section -->
      <div class="search-filter-card">
        <div class="search-section">
          <div class="search-input-wrapper">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="搜索需求标题、描述、技能要求..."
              class="search-input"
              @keyup.enter="handleSearch"
            />
            <font-awesome-icon :icon="['fas', 'search']" class="search-icon" />
            <!-- 搜索框内的清除按钮 -->
            <button
              v-if="searchQuery"
              class="clear-search-btn"
              @click="clearSingleFilter('search')"
              title="清除搜索"
            >
              <font-awesome-icon :icon="['fas', 'times']" />
            </button>
          </div>
          <button
            class="btn btn-primary search-btn"
            @click="handleSearch"
            :disabled="requirementsLoading"
          >
            搜索
          </button>
        </div>

        <!-- 筛选条件区域 -->
        <div class="filters-container">
          <div class="filters">
            <select v-model="statusFilter" class="filter-select">
              <option value="">所有状态</option>
              <option value="under_review">审核中</option>
              <option value="review_failed">审核失败</option>
              <option value="in_progress">进行中</option>
              <option value="completed">已完成</option>
              <option value="paused">已暂停</option>
            </select>

            <div class="filter-budget">
              <input
                v-model="budgetMin"
                type="number"
                placeholder="最低预算"
                class="filter-input budget-input"
                min="0"
              />
              <span class="budget-separator">-</span>
              <input
                v-model="budgetMax"
                type="number"
                placeholder="最高预算"
                class="filter-input budget-input"
                min="0"
              />
            </div>

            <div class="filter-time">
              <el-date-picker
                v-model="timeStart"
                type="date"
                placeholder="开始日期"
                class="filter-input date-input"
              />
              <span class="time-separator">-</span>
              <el-date-picker
                v-model="timeEnd"
                type="date"
                placeholder="结束日期"
                class="filter-input date-input"
              />
            </div>

            <select v-model="sortType" class="filter-select">
              <option value="">排序类型</option>
              <option value="name">按名称</option>
              <option value="time">按时间</option>
              <option value="view">按浏览量</option>
            </select>

            <select v-model="sortOrder" class="filter-select">
              <option value="">排序顺序</option>
              <option value="up">升序</option>
              <option value="down">降序</option>
            </select>
          </div>

          <!-- 清除筛选按钮区域 -->
          <div class="filter-actions">
            <button
              v-if="hasActiveFilters"
              class="btn btn-outline clear-filters-btn"
              @click="clearAllFilters"
              title="清除所有筛选条件"
            >
              <font-awesome-icon :icon="['fas', 'times-circle']" />
              清除筛选 ({{ activeFiltersCount }})
            </button>
          </div>
        </div>

        <!-- 当前筛选条件显示 -->
        <div v-if="hasActiveFilters" class="active-filters">
          <div class="active-filters-header">
            <span class="filters-label">当前筛选条件:</span>
          </div>
          <div class="filter-tags">
            <span v-if="searchQuery" class="filter-tag">
              <span class="tag-label">搜索:</span>
              <span class="tag-value">{{ searchQuery }}</span>
              <button class="tag-close" @click="clearSingleFilter('search')">
                <font-awesome-icon :icon="['fas', 'times']" />
              </button>
            </span>

            <span v-if="statusFilter" class="filter-tag">
              <span class="tag-label">状态:</span>
              <span class="tag-value">{{ getStatusText(statusFilter) }}</span>
              <button class="tag-close" @click="clearSingleFilter('status')">
                <font-awesome-icon :icon="['fas', 'times']" />
              </button>
            </span>

            <span v-if="budgetMin || budgetMax" class="filter-tag">
              <span class="tag-label">预算:</span>
              <span class="tag-value">{{ getBudgetText() }}</span>
              <button class="tag-close" @click="clearSingleFilter('budget')">
                <font-awesome-icon :icon="['fas', 'times']" />
              </button>
            </span>

            <span v-if="timeStart || timeEnd" class="filter-tag">
              <span class="tag-label">时间:</span>
              <span class="tag-value">{{ getTimeText() }}</span>
              <button class="tag-close" @click="clearSingleFilter('time')">
                <font-awesome-icon :icon="['fas', 'times']" />
              </button>
            </span>

            <span v-if="sortType" class="filter-tag">
              <span class="tag-label">排序:</span>
              <span class="tag-value">{{ getSortTypeText(sortType) }}</span>
              <button class="tag-close" @click="clearSingleFilter('sortType')">
                <font-awesome-icon :icon="['fas', 'times']" />
              </button>
            </span>

            <span v-if="sortOrder" class="filter-tag">
              <span class="tag-label">顺序:</span>
              <span class="tag-value">{{ getSortOrderText(sortOrder) }}</span>
              <button class="tag-close" @click="clearSingleFilter('sortOrder')">
                <font-awesome-icon :icon="['fas', 'times']" />
              </button>
            </span>
          </div>
        </div>
      </div>

      <!-- Requirements List -->
      <div class="requirements-list">
        <div v-if="requirementsLoading" class="loading-state">
          <font-awesome-icon :icon="['fas', 'spinner']" class="fa-spin" />
          加载需求列表中...
        </div>

        <div v-else-if="requirements.length === 0" class="empty-state">
          <font-awesome-icon :icon="['fas', 'inbox']" />
          <h3>暂无需求</h3>
          <p>当前筛选条件下没有找到相关需求</p>
        </div>

        <div v-else>
          <div v-for="requirement in requirements" :key="requirement.id" class="requirement-card">
            <div
              class="requirement-content"
              @click="router.push(`/enterprise/requirement/detail/${requirement.id}`)"
            >
              <div class="requirement-header">
                <div class="requirement-title-section">
                  <div class="title-row">
                    <h3 class="requirement-title">{{ requirement.title }}</h3>
                    <span :class="['status-badge', requirement.status]">
                      {{ getStatusText(requirement.status) }}
                    </span>
                    <span v-if="requirement.urgent" class="urgent-badge">紧急</span>
                  </div>

                  <div class="requirement-meta">
                    <span class="meta-item">
                      <font-awesome-icon :icon="['fas', 'clock']" />
                      发布于 {{ requirement.publishDate }}
                    </span>
                    <span class="meta-item">
                      <font-awesome-icon :icon="['fas', 'calendar']" />
                      {{ requirement.status === 'completed' ? '完成于' : '截止' }}
                      {{ requirement.deadline }}
                    </span>
                    <span class="meta-item">
                      <font-awesome-icon :icon="['fas', 'dollar-sign']" />
                      预算 {{ requirement.budget.display }}
                    </span>
                    <span class="meta-item" v-if="requirement.teamSize">
                      <font-awesome-icon :icon="['fas', 'users']" />
                      {{ requirement.status === 'completed' ? '团队规模' : '需要人数' }}
                      {{ requirement.teamSize }}人
                    </span>
                  </div>
                </div>
              </div>

              <p class="requirement-description">{{ requirement.description }}</p>

              <!-- 技能标签 -->
              <div class="skill-tags" v-if="requirement.tags.length > 0">
                <span
                  v-for="tag in requirement.tags.slice(0, 6)"
                  :key="tag"
                  :class="['skill-tag', getTagColorClass()]"
                >
                  {{ tag }}
                </span>
                <span v-if="requirement.tags.length > 6" class="skill-tag more">
                  +{{ requirement.tags.length - 6 }}
                </span>
              </div>

              <div class="requirement-footer">
                <div class="footer-info">
                  <div class="info-item">
                    <span class="info-label">浏览次数:</span>
                    <span class="info-value">{{ requirement.views }}次</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">发布人:</span>
                    <span class="info-value">{{ requirement.publisher }}</span>
                  </div>
                </div>
                <div class="footer-actions">
                  <button
                    v-if="requirement.status !== 'completed'"
                    class="action-btn"
                    :class="requirement.status === 'paused' ? 'resume' : 'pause'"
                    :title="requirement.status === 'paused' ? '恢复需求' : '暂停需求'"
                    @click.stop="toggleRequirementStatus(requirement.id, requirement.status)"
                  >
                    <font-awesome-icon
                      :icon="['fas', requirement.status === 'paused' ? 'paper-plane' : 'power-off']"
                    />
                  </button>
                  <button
                    v-if="requirement.status !== 'completed'"
                    class="action-btn delete"
                    title="删除"
                    @click.stop="deleteRequirement(requirement.id)"
                  >
                    <font-awesome-icon :icon="['fas', 'trash']" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ElementPlus 分页组件 -->
      <div v-if="requirements.length > 0" class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[5, 10, 20, 50, 100]"
          :total="totalCount"
          :disabled="requirementsLoading"
          layout="total, sizes, prev, pager, next, jumper"
          background
          @current-change="handleCurrentChange"
          @size-change="handleSizeChange"
          class="custom-pagination"
        />
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.requirements-page {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 1rem;

  .container {
    max-width: 1500px;
    margin: 0 auto;
  }
}

// Header Section
.header-section {
  margin-bottom: 2rem;

  .header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
    flex-wrap: wrap;

    @media (max-width: 768px) {
      flex-direction: column;
      align-items: stretch;
    }
  }

  .title-section {
    flex: 1;

    .page-title {
      font-size: clamp(1.5rem, 3vw, 2rem);
      font-weight: 700;
      color: #1f2937;
      margin: 0 0 0.5rem 0;
    }

    .page-subtitle {
      color: #6b7280;
      margin: 0;
    }
  }

  .action-buttons {
    display: flex;
    gap: 0.75rem;
    flex-wrap: wrap;
  }
}

// 需求发布和数据统计区域
.publish-stats-section {
  display: grid;
  grid-template-columns: 1fr 2fr;
  gap: 1.5rem;
  margin-bottom: 2rem;

  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
}

// 需求发布卡片
.publish-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  align-content: center;

  .upload-area {
    border: 2px dashed #d1d5db;
    border-radius: 0.5rem;
    padding: 2rem;
    text-align: center;
    cursor: pointer;
    transition: all 0.3s ease;
    background: #fafbfc;

    &:hover {
      border-color: #3b82f6;
      background: #f0f7ff;

      .upload-icon {
        color: #3b82f6;
        transform: translateY(-2px);
      }
    }

    .upload-icon {
      font-size: 2.5rem;
      color: #9ca3af;
      margin-bottom: 1rem;
      transition: all 0.3s ease;
    }

    .upload-title {
      font-size: 1.25rem;
      font-weight: 600;
      color: #1f2937;
      margin: 0 0 0.5rem 0;
    }

    .upload-subtitle {
      color: #6b7280;
      margin: 0 0 0.75rem 0;
    }

    .upload-hint {
      font-size: 0.875rem;
      color: #9ca3af;
      margin: 0;
    }
  }
}

// 数据统计卡片
.stats-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  .stats-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;

    .stats-title {
      font-size: 1.125rem;
      font-weight: 600;
      color: #1f2937;
      margin: 0 0 0.25rem 0;
    }

    .stats-subtitle {
      color: #6b7280;
      font-size: 0.875rem;
      margin: 0;
    }
  }

  .stats-content {
    display: flex;
    align-items: center;
    gap: 1.5rem;

    @media (max-width: 768px) {
      flex-direction: column;
    }

    .chart-container {
      flex: 1;
      width: 100%;

      .chart {
        width: 100%;
        height: 200px;
      }
    }

    .stats-summary {
      width: 120px;
      display: flex;
      flex-direction: column;
      gap: 1rem;

      @media (max-width: 768px) {
        width: 100%;
        flex-direction: row;
        justify-content: space-around;
      }

      .stat-item {
        text-align: center;

        .stat-value {
          font-size: 1.5rem;
          font-weight: 700;
          color: #1f2937;
          margin-bottom: 0.25rem;
        }

        .stat-label {
          font-size: 0.75rem;
          color: #6b7280;
        }
      }
    }
  }
}

// 模态框样式
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;

  .modal-content {
    background: white;
    border-radius: 0.75rem;
    width: 100%;
    max-width: 600px;
    max-height: 90vh;
    overflow-y: auto;

    .modal-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 1.5rem 1.5rem 0 1.5rem;

      .modal-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1f2937;
        margin: 0;
      }

      .close-btn {
        background: none;
        border: none;
        color: #6b7280;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 0.25rem;
        transition: color 0.2s;

        &:hover {
          color: #374151;
        }
      }
    }

    .modal-body {
      padding: 1.5rem;

      .publish-options {
        display: flex;
        flex-direction: column;
        gap: 1rem;

        .publish-option {
          display: flex;
          align-items: flex-start;
          gap: 1rem;
          padding: 1.5rem;
          border: 2px solid #e5e7eb;
          border-radius: 0.5rem;
          background: white;
          cursor: pointer;
          transition: all 0.2s;
          text-align: left;

          &:hover {
            border-color: #3b82f6;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
          }

          .option-icon {
            width: 3rem;
            height: 3rem;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.25rem;
            flex-shrink: 0;

            &.chat {
              background: #dbeafe;
              color: #3b82f6;
            }

            &.form {
              background: #d1fae5;
              color: #10b981;
            }
          }

          .option-content {
            flex: 1;

            .option-title {
              font-size: 1.125rem;
              font-weight: 600;
              color: #1f2937;
              margin: 0 0 0.5rem 0;
            }

            .option-description {
              color: #6b7280;
              margin: 0 0 0.75rem 0;
              line-height: 1.5;
            }

            .option-features {
              display: flex;
              flex-wrap: wrap;
              gap: 0.5rem;

              .feature {
                font-size: 0.75rem;
                color: #059669;
                background: #ecfdf5;
                padding: 0.25rem 0.5rem;
                border-radius: 0.25rem;
              }
            }
          }
        }
      }
    }
  }
}

// Buttons
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
  border: 1px solid transparent;
  cursor: pointer;

  &.btn-primary {
    background-color: #2563eb;
    color: white;
    border: none;

    &:hover {
      background-color: #1d4ed8;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  &.btn-secondary {
    background-color: #f3f4f6;
    color: #374151;
    border: none;

    &:hover {
      background-color: #e5e7eb;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }

  &.btn-outline {
    border-color: #d1d5db;
    background-color: white;
    color: #374151;

    &:hover {
      background-color: #f9fafb;
    }
  }
}

// 按钮样式调整
.btn {
  &.btn-outline {
    &.clear-filters-btn {
      font-size: 0.875rem;
      padding: 0.5rem 0.75rem;
    }
  }
}

// 筛选相关样式
.search-filter-card {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;

  .search-section {
    display: flex;
    gap: 1rem;
    margin-bottom: 1rem;

    @media (max-width: 768px) {
      flex-direction: column;
    }

    .search-input-wrapper {
      flex: 1;
      position: relative;

      .search-input {
        width: 100%;
        padding: 0.75rem 1rem 0.75rem 2.5rem;
        padding-right: 2.5rem; // 为清除按钮留空间
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        font-size: 0.875rem;

        &:focus {
          outline: none;
          border-color: #3b82f6;
          box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
      }

      .search-icon {
        position: absolute;
        left: 0.75rem;
        top: 50%;
        transform: translateY(-50%);
        color: #9ca3af;
      }

      .clear-search-btn {
        position: absolute;
        right: 0.75rem;
        top: 50%;
        transform: translateY(-50%);
        background: none;
        border: none;
        color: #6b7280;
        cursor: pointer;
        padding: 0.25rem;
        border-radius: 0.25rem;
        transition: color 0.2s;

        &:hover {
          color: #374151;
        }
      }
    }
  }

  .filters-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;

    @media (max-width: 768px) {
      flex-direction: column;
      align-items: stretch;
    }

    .filters {
      display: flex;
      gap: 0.75rem;
      flex-wrap: wrap;
      flex: 1;

      .filter-select {
        padding: 0.5rem 1rem;
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        color: #374151;
        min-width: 120px;

        &:focus {
          outline: none;
          border-color: #3b82f6;
        }
      }

      .filter-input {
        padding: 0.5rem 0.75rem;
        background-color: #f9fafb;
        border: 1px solid #e5e7eb;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        color: #374151;

        &:focus {
          outline: none;
          border-color: #3b82f6;
        }

        &.budget-input {
          width: 120px;
        }

        &.date-input {
          width: 140px;
        }
      }

      .filter-budget {
        display: flex;
        align-items: center;
        gap: 0.5rem;

        .budget-separator {
          color: #6b7280;
          font-weight: 500;
        }
      }

      .filter-time {
        display: flex;
        align-items: center;
        gap: 0.5rem;

        .time-separator {
          color: #6b7280;
          font-size: 0.875rem;
        }

        :deep(.el-input) {
          width: 120px;
        }
      }
    }

    .filter-actions {
      display: flex;
      gap: 0.5rem;

      .clear-filters-btn {
        white-space: nowrap;
        color: #ef4444;
        border-color: #ef4444;

        &:hover {
          background-color: #fef2f2;
          border-color: #dc2626;
          color: #dc2626;
        }
      }
    }
  }

  // 当前筛选条件显示
  .active-filters {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #f3f4f6;

    .active-filters-header {
      margin-bottom: 0.75rem;

      .filters-label {
        font-size: 0.875rem;
        font-weight: 500;
        color: #374151;
      }
    }

    .filter-tags {
      display: flex;
      gap: 0.5rem;
      flex-wrap: wrap;

      .filter-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.25rem;
        padding: 0.25rem 0.5rem;
        background-color: #f0f7ff;
        border: 1px solid #bfdbfe;
        border-radius: 0.375rem;
        font-size: 0.75rem;

        .tag-label {
          color: #1e40af;
          font-weight: 500;
        }

        .tag-value {
          color: #3730a3;
        }

        .tag-close {
          background: none;
          border: none;
          color: #6b7280;
          cursor: pointer;
          padding: 0.125rem;
          border-radius: 0.125rem;
          margin-left: 0.25rem;
          transition: color 0.2s;

          &:hover {
            color: #ef4444;
          }

          svg {
            font-size: 0.625rem;
          }
        }
      }
    }
  }
}

// Requirements List
.requirements-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.requirement-card {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
  }

  .requirement-content {
    padding: 1.5rem;
    margin: 1rem;
  }

  .requirement-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
    gap: 1rem;

    @media (max-width: 768px) {
      flex-direction: column;
    }

    .requirement-title-section {
      flex: 1;

      .title-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-bottom: 0.75rem;
        flex-wrap: wrap;

        .requirement-title {
          font-size: 1.125rem;
          font-weight: 600;
          color: #1f2937;
          margin: 0;
        }

        .status-badge {
          padding: 0.25rem 0.75rem;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;

          &.under_review {
            background-color: #fef3c7;
            color: #92400e;
          }

          &.review_failed {
            background-color: #fee2e2;
            color: #991b1b;
          }

          &.in_progress {
            background-color: #dbeafe;
            color: #1e40af;
          }

          &.completed {
            background-color: #f3f4f6;
            color: #374151;
          }

          &.paused {
            background-color: #fce7f3;
            color: #be185d;
          }
        }

        .urgent-badge {
          padding: 0.25rem 0.75rem;
          background-color: #dbeafe;
          color: #1e40af;
          border-radius: 9999px;
          font-size: 0.75rem;
          font-weight: 500;
        }
      }

      .requirement-meta {
        display: flex;
        gap: 1rem;
        flex-wrap: wrap;

        .meta-item {
          display: flex;
          align-items: center;
          gap: 0.25rem;
          color: #6b7280;
          font-size: 0.875rem;

          @media (max-width: 768px) {
            font-size: 0.775rem;
          }
        }
      }
    }

    .requirement-actions {
      display: flex;
      gap: 0.75rem;

      @media (max-width: 768px) {
        width: 100%;
        justify-content: flex-end;
      }
    }
  }

  .requirement-description {
    color: #4b5563;
    margin: 0 0 1rem 0;
    line-height: 1.6;
  }

  .skill-tags {
    display: flex;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-bottom: 1rem;

    .skill-tag {
      padding: 0.25rem 0.75rem;
      border-radius: 9999px;
      font-size: 0.75rem;

      &.blue {
        background-color: #dbeafe;
        color: #1e40af;
      }

      &.more {
        background-color: #f3f4f6;
        color: #6b7280;
      }
    }
  }

  .requirement-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 1rem;
    border-top: 1px solid #f3f4f6;

    @media (max-width: 768px) {
      flex-direction: column;
      gap: 1rem;
      align-items: flex-start;
    }

    .footer-info {
      display: flex;
      gap: 1.5rem;
      flex-wrap: wrap;

      .info-item {
        display: flex;
        align-items: center;
        gap: 0.25rem;
        font-size: 0.875rem;

        .info-label {
          color: #6b7280;
        }

        .info-value {
          font-weight: 500;
          color: #1f2937;
        }

        .rating {
          display: flex;
          align-items: center;
          gap: 0.25rem;

          .stars {
            display: flex;
            color: #d1d5db;
            font-size: 0.75rem;

            .active {
              color: #fbbf24;
            }
          }

          .rating-score {
            color: #6b7280;
            font-size: 0.75rem;
          }
        }
      }
    }

    .footer-actions {
      display: flex;
      gap: 0.5rem;

      .action-btn {
        background: none;
        border: none;
        color: #6b7280;
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 0.25rem;
        transition: color 0.2s;

        &:hover {
          color: #374151;
        }
        &.pause {
          color: #f5420b;

          &:hover {
            color: #bba4a4;
          }
        }
        &.resume {
          color: #10b981;

          &:hover {
            color: #047857;
          }
        }
        &.delete {
          color: #979797;

          &:hover {
            color: #dc2626;
          }
        }
      }
    }
  }
}

// ElementPlus 分页样式
.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 2rem;

  .custom-pagination {
    // 自定义分页样式可以在这里添加
    :deep(.el-pagination) {
      .el-pagination__total,
      .el-pagination__sizes,
      .el-pagination__jump {
        color: #6b7280;
      }

      .el-pager li {
        &:hover {
          color: #3b82f6;
        }

        &.is-active {
          background-color: #3b82f6;
          color: white;
        }
      }

      .btn-prev,
      .btn-next {
        &:hover {
          color: #3b82f6;
        }
      }
    }
  }
}

// 错误提示样式
.error-message {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 0.5rem;
  padding: 1rem;
  margin-bottom: 1.5rem;

  .error-content {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    color: #dc2626;

    svg {
      color: #dc2626;
    }
  }
}

// 加载状态样式
.stats-loading,
.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #6b7280;
}

// 空状态样式
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #6b7280;

  svg {
    font-size: 3rem;
    margin-bottom: 1rem;
    color: #d1d5db;
  }

  h3 {
    margin: 0 0 0.5rem 0;
    color: #374151;
  }

  p {
    margin: 0;
  }
}
</style>
