<script setup>
import { ref, reactive, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import * as echarts from 'echarts/core'
import { PieChart } from 'echarts/charts'
import { TooltipComponent, LegendComponent } from 'echarts/components'

// 注册必需的组件
echarts.use([PieChart, TooltipComponent, LegendComponent])

import 'echarts-wordcloud'
import { resourcesService } from '@/api'
import { useUserStore } from '@/stores'
import { useRouter } from 'vue-router'

// 导入项目中用到的图标
import {
  faFilter,
  faDownload,
  faPlus,
  faCube,
  faCheckCircle,
  faHeart,
  faHandshake,
  faArrowUp,
  faShareAlt,
  faCode,
  faUsers,
  faBook,
  faSearch,
  faClock,
  faEye,
  faEdit,
  faChartBar,
  faPowerOff,
  faChevronLeft,
  faChevronRight,
  faCalendar,
  faChartLine,
  faTags,
  faFire,
  faExclamationTriangle,
  faSyncAlt,
  faDatabase,
  faFileAlt,
  faGraduationCap,
  faVideo,
  faWrench,
  faTrash,
  faPaperPlane,
  faToggleOn,
  faToggleOff
} from '@fortawesome/free-solid-svg-icons'

// 将图标添加到库中
library.add(
  faFilter,
  faDownload,
  faPlus,
  faCube,
  faCheckCircle,
  faHeart,
  faHandshake,
  faArrowUp,
  faShareAlt,
  faCode,
  faUsers,
  faBook,
  faSearch,
  faClock,
  faEye,
  faEdit,
  faChartBar,
  faPowerOff,
  faChevronLeft,
  faChevronRight,
  faCalendar,
  faChartLine,
  faTags,
  faFire,
  faExclamationTriangle,
  faSyncAlt,
  faDatabase,
  faFileAlt,
  faGraduationCap,
  faVideo,
  faWrench,
  faTrash,
  faPaperPlane,
  faToggleOn,
  faToggleOff
)

const router = useRouter()
// 响应式数据
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)

const filters = reactive({
  status: '',
  type: '',
  usage: '',
  timeStart: '', // 开始日期
  timeEnd: '' // 结束日期
})

const sortOptions = reactive({
  type: [],
  order: 'down'
})

// 单个排序字段选择
const sortField = ref('')

// 统计时间范围
const statisticsPeriod = ref('week')

// 排行榜类型切换（下载量/浏览量）
const rankingType = ref('downloads') // 'downloads' | 'views'

// 更新排序类型
const updateSortType = () => {
  if (sortField.value) {
    sortOptions.type = [sortField.value]
  } else {
    sortOptions.type = []
  }
}

// 用户信息
const userStore = useUserStore()

// 数据加载状态
const loading = ref(true)
const error = ref(null)
const resourcesLoading = ref(false)
const resourcesError = ref(null)

// 图表引用
const statusChartRef = ref(null)
const techCloudRef = ref(null)
let statusChart = null
let techChart = null

// 接口数据
const statisticsData = ref({
  status_distribution: {},
  data_statistics: {},
  hot_tag1s: [],
  hot_downloads: [],
  hot_views: []
})

// 资源列表数据
const resourcesData = ref({
  resources: [],
  pagination: {
    current_page: 1,
    total_pages: 1,
    total_count: 0,
    page_size: 10,
    has_next: false,
    has_previous: false
  }
})

// 状态分布数据（基于接口数据计算）
const statusDistribution = computed(() => {
  const data = statisticsData.value.status_distribution
  return [
    { label: '已发布', value: data.published || 0, color: '#10b981' },
    { label: '草稿', value: data.draft || 0, color: '#6b7280' },
    { label: '已下线', value: data.unpublished || 0, color: '#ef4444' }
  ]
})

// 数据统计（基于接口数据计算）
const dataStats = computed(() => {
  const data = statisticsData.value.data_statistics
  return [
    {
      label: '总资源数',
      value: data.total || 0,
      icon: ['fas', 'cube'],
      growth: data.total_up ? `${data.total_up}` : '0%'
    },
    {
      label: '已发布',
      value: data.published_count || 0,
      icon: ['fas', 'check-circle'],
      growth: data.published_count_up ? `${data.published_count_up}` : '0%'
    },
    {
      label: '总下载量',
      value: data.downloads || 0,
      icon: ['fas', 'download'],
      growth: data.downloads_up ? `${data.downloads_up}` : '0%'
    },
    {
      label: '总浏览量',
      value: data.views || 0,
      icon: ['fas', 'eye'],
      growth: data.views_up ? `${data.views_up}` : '0%'
    }
  ]
})

// 热门技术领域（基于接口数据计算）
const hotTechFields = computed(() => {
  return statisticsData.value.hot_tag1s.map((item) => ({
    name: item.tag,
    value: parseInt(item.count) || 0
  }))
})

// 使用热度排行（基于接口数据计算） - 修改为只显示前3个
const usageRanking = computed(() => {
  const dataSource =
    rankingType.value === 'downloads'
      ? statisticsData.value.hot_downloads
      : statisticsData.value.hot_views

  return dataSource.slice(0, 3).map((item, index) => ({
    // 只取前3个
    rank: index + 1,
    id: item.id,
    title: item.title,
    downloads: parseInt(item.downloads) || 0,
    views: parseInt(item.views) || 0,
    author: item.auther // 注意：接口返回的是 auther 而不是 author
  }))
})

// 时间范围选项
const periodOptions = ref([
  { value: 'week', label: '本周' },
  { value: 'month', label: '本月' },
  { value: 'quarter', label: '本季度' }
])

// 排行榜类型选项
const rankingOptions = ref([
  { value: 'downloads', label: '下载量排行', icon: ['fas', 'download'] },
  { value: 'views', label: '浏览量排行', icon: ['fas', 'eye'] }
])

// 标签合并处理函数
const mergeTags = (tag1Array, tag2Array) => {
  const mergedTags = []

  // 添加tag1中的所有标签（提取name字段）
  if (tag1Array && Array.isArray(tag1Array)) {
    tag1Array.forEach((tagObj) => {
      if (tagObj && tagObj.name && typeof tagObj.name === 'string' && tagObj.name.trim()) {
        mergedTags.push(tagObj.name.trim())
      }
    })
  }

  // 处理tag2，提取name字段并只显示最后一个部分
  if (tag2Array && Array.isArray(tag2Array)) {
    tag2Array.forEach((tagObj) => {
      if (tagObj && tagObj.name && typeof tagObj.name === 'string') {
        const tagName = tagObj.name
        if (tagName.includes('-')) {
          // 分割字符串，取最后一个部分
          const parts = tagName.split('-')
          const lastPart = parts[parts.length - 1]
          if (lastPart && lastPart.trim()) {
            mergedTags.push(lastPart.trim())
          }
        } else if (tagName.trim()) {
          // 如果没有分隔符，直接添加
          mergedTags.push(tagName.trim())
        }
      }
    })
  }

  // 去重并返回
  return [...new Set(mergedTags)]
}

// 资源列表（基于接口数据计算）
const resources = computed(() => {
  return resourcesData.value.resources.map((resource) => ({
    id: resource.id,
    title: resource.title,
    description: resource.description,
    status: getStatusText(resource.status),
    type: getTypeText(resource.type),
    icon: getTypeIcon(resource.type),
    iconColor: getTypeColor(resource.type),
    typeColor: getTypeColor(resource.type),
    tagColor: getTypeColor(resource.type),
    publishDate: formatDate(resource.created_at), // 使用接口返回的字段名
    views: parseInt(resource.views) || 0,
    downloads: parseInt(resource.downloads) || 0,
    tags: mergeTags(resource.tag1, resource.tag2), // 使用新的标签合并函数
    detail1: {
      label: '创建者',
      value: resource.create_person_name || '未知', // 使用接口返回的字段名
      class: 'font-medium text-gray-900'
    },
    detail2: {
      label: '更新时间',
      value: formatDate(resource.updated_at), // 使用接口返回的字段名
      class: 'font-medium text-gray-900'
    }
  }))
})

// 分页信息
const pagination = computed(() => resourcesData.value.pagination)

// 辅助函数
const getStatusText = (status) => {
  const statusMap = {
    published: '已发布',
    draft: '草稿',
    unpublished: '已下线'
  }
  return statusMap[status] || status
}

const getTypeText = (type) => {
  const typeMap = {
    code: '代码',
    dataset: '数据集',
    document: '文档',
    course: '课程',
    video: '视频',
    tool: '工具'
  }
  return typeMap[type] || type
}

const getTypeIcon = (type) => {
  const iconMap = {
    code: ['fas', 'code'],
    dataset: ['fas', 'database'],
    document: ['fas', 'file-alt'],
    course: ['fas', 'graduation-cap'],
    video: ['fas', 'video'],
    tool: ['fas', 'wrench']
  }
  return iconMap[type] || ['fas', 'cube']
}

const getTypeColor = (type) => {
  const colorMap = {
    code: 'blue',
    dataset: 'green',
    document: 'orange',
    course: 'purple',
    video: 'red',
    tool: 'gray'
  }
  return colorMap[type] || 'blue'
}

const getTimeText = (time) => {
  const timeMap = {
    week: '最近一周',
    month: '最近一月',
    quarter: '最近三月'
  }
  return timeMap[time] || time
}

const getSortText = (sort) => {
  const sortMap = {
    name: '按名称',
    time: '按时间',
    download: '按下载量',
    view: '按浏览量'
  }
  return sortMap[sort] || sort
}

const formatDate = (dateString) => {
  if (!dateString) return '未知'
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

// 获取统计数据
const fetchStatistics = async () => {
  try {
    loading.value = true
    error.value = null

    const organizationId = userStore.user?.company_profile?.organization?.id
    if (!organizationId) {
      throw new Error('获取组织ID失败')
    }

    const response = await resourcesService.getResourceStatistics(
      organizationId,
      statisticsPeriod.value
    )

    if (response.status === 'success') {
      statisticsData.value = response.data

      // 等待数据更新和DOM渲染
      await nextTick()
      await nextTick()

      // 延迟初始化图表，确保DOM完全准备好
      setTimeout(() => {
        initCharts()
      }, 100)
    } else {
      throw new Error(response.message || '获取数据失败')
    }
  } catch (err) {
    console.error('获取统计数据失败:', err)
    error.value = err.message || '获取数据失败'
  } finally {
    loading.value = false
  }
}

// 切换统计时间范围
const changePeriod = (period) => {
  statisticsPeriod.value = period
  fetchStatistics()
}

// 获取资源列表数据 - 使用真实API
const fetchResources = async (showLoading = true) => {
  try {
    if (showLoading) {
      resourcesLoading.value = true
    }
    resourcesError.value = null

    const organizationId = userStore.user?.company_profile?.organization?.id
    if (!organizationId) {
      throw new Error('获取组织ID失败')
    }

    // 构建查询参数
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    // 添加搜索关键字
    if (searchQuery.value.trim()) {
      params.keyword = searchQuery.value.trim()
    }

    // 添加筛选条件
    if (filters.status) {
      params.status = filters.status
    }
    if (filters.type) {
      params.type = filters.type
    }

    // 日期范围筛选
    if (filters.timeStart && filters.timeEnd) {
      params.time = `${filters.timeStart}-${filters.timeEnd}` // 格式：yyyy-mm-dd-yyyy-mm-dd
    } else if (filters.timeStart) {
      params.time = filters.timeStart
    } else if (filters.timeEnd) {
      params.time = filters.timeEnd
    }

    // 添加排序参数
    if (sortOptions.type.length > 0) {
      // 使用逗号分隔数组元素
      params.sort_type = sortOptions.type.join(',')
      params.sort_order = sortOptions.order
    }

    // 使用真实API接口
    const response = await resourcesService.getResources(organizationId, params)

    if (response.status === 'success') {
      resourcesData.value = response.data
      // 更新当前页码为实际返回的页码
      currentPage.value = response.data.pagination.current_page
    } else {
      throw new Error(response.message || '获取资源列表失败')
    }
  } catch (err) {
    console.error('获取资源列表失败:', err)
    resourcesError.value = err.message || '获取资源列表失败'
  } finally {
    if (showLoading) {
      resourcesLoading.value = false
    }
  }
}

// 初始化所有图表
const initCharts = () => {
  // 销毁旧图表实例
  if (statusChart) {
    statusChart.dispose()
    statusChart = null
  }
  if (techChart) {
    techChart.dispose()
    techChart = null
  }

  // 重新初始化图表
  initStatusChart()
  initTechChart()

  // 调整图表尺寸
  setTimeout(() => {
    if (statusChart) statusChart.resize()
    if (techChart) techChart.resize()
  }, 200)
}

// 初始化状态分布图表
const initStatusChart = () => {
  if (!statusChartRef.value || !statusDistribution.value || statusDistribution.value.length === 0) {
    return
  }

  // 检查是否有有效数据
  const hasValidData = statusDistribution.value.some((item) => item.value > 0)
  if (!hasValidData) return

  try {
    statusChart = echarts.init(statusChartRef.value)

    const option = {
      tooltip: {
        trigger: 'item',
        formatter: '{a} <br/>{b}: {c} ({d}%)'
      },
      legend: {
        orient: 'horizontal',
        bottom: 5,
        left: 'center',
        itemWidth: 10,
        itemHeight: 10,
        textStyle: {
          fontSize: 11,
          color: '#6b7280'
        }
      },
      series: [
        {
          name: '资源状态',
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['50%', '42%'],
          avoidLabelOverlap: false,
          itemStyle: {
            borderRadius: 3,
            borderColor: '#fff',
            borderWidth: 2
          },
          label: {
            show: false
          },
          emphasis: {
            label: {
              show: true,
              fontSize: 14,
              fontWeight: 'bold'
            },
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          labelLine: {
            show: false
          },
          data: statusDistribution.value.map((item) => ({
            value: item.value,
            name: item.label,
            itemStyle: {
              color: item.color
            }
          }))
        }
      ]
    }

    statusChart.setOption(option)
  } catch (err) {
    console.error('状态分布图表初始化失败:', err)
  }
}

// 初始化技术词云图表
const initTechChart = () => {
  if (!techCloudRef.value || !hotTechFields.value || hotTechFields.value.length === 0) {
    return
  }

  try {
    techChart = echarts.init(techCloudRef.value)

    // 预定义颜色，避免每次刷新都变化
    const predefinedColors = [
      '#2563eb',
      '#10b981',
      '#8b5cf6',
      '#f59e0b',
      '#6366f1',
      '#ec4899',
      '#06b6d4',
      '#ef4444',
      '#eab308',
      '#6b7280'
    ]

    // 为词云创建稳定的数据结构
    const stableWordData = hotTechFields.value.map((item, index) => ({
      name: item.name,
      value: Math.max(item.value, 1),
      textStyle: {
        color: predefinedColors[index % predefinedColors.length] // 固定每个词的颜色
      }
    }))

    // 尝试使用词云
    const wordCloudOption = {
      tooltip: {
        show: true,
        formatter: function (params) {
          return `${params.name}: ${params.value} 个资源`
        }
      },
      series: [
        {
          type: 'wordCloud',
          gridSize: 10, // 增加网格大小，减少重叠和重新布局
          sizeRange: [12, 32],
          rotationRange: [0, 0], // 禁用旋转，保持稳定
          rotationStep: 0,
          shape: 'circle',
          width: '100%',
          height: '100%',
          drawOutOfBound: false,
          layoutAnimation: false, // 禁用布局动画
          // 添加这些配置来稳定布局
          left: 'center',
          top: 'center',
          right: null,
          bottom: null,
          textStyle: {
            fontFamily: 'sans-serif',
            fontWeight: 'bold'
          },
          emphasis: {
            focus: 'self',
            textStyle: {
              textShadowBlur: 10,
              textShadowColor: '#333'
            }
          },
          data: stableWordData
        }
      ]
    }

    try {
      // 延迟设置选项，等待容器完全准备好
      setTimeout(() => {
        if (techChart && !techChart.isDisposed()) {
          techChart.setOption(wordCloudOption, true) // 第二个参数true表示不合并，完全重新设置
        }
      }, 50)
    } catch (wordCloudError) {
      // 词云失败，使用柱状图备用方案
      const backupOption = {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'shadow'
          },
          formatter: function (params) {
            return `${params[0].name}: ${params[0].value} 个资源`
          }
        },
        grid: {
          left: '15%',
          right: '8%',
          bottom: '8%',
          top: '5%',
          containLabel: true
        },
        xAxis: {
          type: 'value',
          axisLabel: {
            fontSize: 10
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          },
          splitLine: {
            lineStyle: {
              color: '#f0f0f0'
            }
          }
        },
        yAxis: {
          type: 'category',
          data: hotTechFields.value
            .slice(0, 6)
            .map((item) => (item.name.length > 8 ? item.name.substring(0, 8) + '...' : item.name)),
          axisLabel: {
            fontSize: 10,
            color: '#666'
          },
          axisLine: {
            show: false
          },
          axisTick: {
            show: false
          }
        },
        series: [
          {
            type: 'bar',
            data: hotTechFields.value.slice(0, 6).map((item, index) => ({
              value: item.value,
              itemStyle: {
                color: predefinedColors[index % predefinedColors.length]
              }
            })),
            barWidth: '60%',
            label: {
              show: true,
              position: 'right',
              fontSize: 10,
              color: '#666'
            }
          }
        ]
      }

      techChart.setOption(backupOption)
    }
  } catch (err) {
    console.error('技术词云图表初始化失败:', err)
  }
}

// 资源类型
const resourceTypes = ref([
  {
    name: '代码',
    icon: ['fas', 'code'],
    color: 'text-blue-500',
    description: '源代码、组件库、脚手架'
  },
  {
    name: '数据集',
    icon: ['fas', 'database'],
    color: 'text-green-500',
    description: '训练数据、测试数据、样本集'
  },
  {
    name: '文档',
    icon: ['fas', 'file-alt'],
    color: 'text-orange-500',
    description: '技术文档、设计规范、指南'
  },
  {
    name: '课程',
    icon: ['fas', 'graduation-cap'],
    color: 'text-purple-500',
    description: '在线课程、培训材料、教程'
  },
  {
    name: '视频',
    icon: ['fas', 'video'],
    color: 'text-red-500',
    description: '教学视频、演示录屏、讲座'
  },
  {
    name: '工具',
    icon: ['fas', 'wrench'],
    color: 'text-gray-500',
    description: '开发工具、测试工具、脚本'
  }
])

// 清除所有筛选条件
const clearFilters = () => {
  searchQuery.value = ''
  filters.status = ''
  filters.type = ''
  filters.time = ''
  sortField.value = ''
  sortOptions.type = []
  sortOptions.order = 'down'
  currentPage.value = 1
}

// 计算当前筛选状态
const hasActiveFilters = computed(() => {
  return searchQuery.value || filters.status || filters.type || filters.time || sortField.value
})

const publishNewResource = () => {
  console.log('发布新资源')
  router.push('/enterprise/resource/create')
}

const quickPublish = (type) => {
  console.log('快速发布:', type)
}

const performSearch = () => {
  console.log('搜索:', searchQuery.value)
  currentPage.value = 1 // 重置到第一页
  fetchResources()
}

const editResource = (id) => {
  console.log('编辑资源:', id)
  router.push(`/enterprise/resource/edit/${id}`)
}

const viewResource = (id) => {
  console.log('查看资源:', id)
  router.push(`/enterprise/resource/detail/${id}`)
}

const offlineResource = async (id) => {
  console.log('下线资源:', id)
  try {
    // 使用真实API更新资源状态
    const response = await resourcesService.updateResource(id, { status: 'unpublished' })
    if (response.status === 'success') {
      ElMessage.success('资源下线成功')
      fetchResources(false) // 刷新列表，不显示loading
    } else {
      throw new Error(response.message || '下线失败')
    }
  } catch (error) {
    console.error('下线资源失败:', error)
    ElMessage.error('下线资源失败，请稍后重试')
  }
}

const publishResource = async (id) => {
  console.log('发布资源:', id)
  try {
    // 使用真实API更新资源状态
    const response = await resourcesService.updateResource(id, { status: 'published' })
    if (response.status === 'success') {
      ElMessage.success('资源发布成功')
      fetchResources(false) // 刷新列表，不显示loading
    } else {
      throw new Error(response.message || '发布失败')
    }
  } catch (error) {
    console.error('发布资源失败:', error)
    ElMessage.error('发布资源失败，请稍后重试')
  }
}

const deleteResource = async (id) => {
  try {
    // 显示确认弹窗
    await ElMessageBox.confirm('确定要删除这个资源吗？此操作不可撤销。', '删除确认', {
      confirmButtonText: '确认',
      cancelButtonText: '取消',
      type: 'warning'
    })

    // 用户确认后才会执行到这里
    console.log('删除资源:', id)
    const response = await resourcesService.deleteResource(id)
    if (response.status === 'success') {
      ElMessage.success('资源删除成功')
      fetchResources(false) // 刷新列表，不显示loading
    } else {
      throw new Error(response.message || '删除失败')
    }
  } catch (error) {
    // 使用 Element Plus 提供的方法判断是否为取消操作
    if (ElMessageBox.isCancel(error)) {
      return
    }
    // 其他错误才显示错误信息
    console.error('删除资源失败:', error)
    ElMessage.error('删除资源失败，请稍后重试')
  }
}

// 添加引用
const searchSectionRef = ref(null)

// 分页事件处理函数
const handleCurrentChange = async (page) => {
  if (page !== currentPage.value) {
    currentPage.value = page
    await fetchResources()
    // 滚动到资源列表顶部
    nextTick(() => {
      if (searchSectionRef.value) {
        searchSectionRef.value.scrollIntoView({
          // behavior: 'smooth',
          block: 'start'
        })
      }
    })
  }
}

const handleSizeChange = async (size) => {
  if (size !== pageSize.value) {
    pageSize.value = size
    currentPage.value = 1 // 改变页大小时重置到第一页
    await fetchResources()
    // 滚动到资源列表顶部
    nextTick(() => {
      if (searchSectionRef.value) {
        searchSectionRef.value.scrollIntoView({
          // behavior: 'smooth',
          block: 'start'
        })
      }
    })
  }
}

// 窗口大小改变时重新调整图表
const handleResize = () => {
  // 使用防抖避免频繁调用
  clearTimeout(window.resizeTimer)
  window.resizeTimer = setTimeout(() => {
    if (statusChart) statusChart.resize()
    if (techChart) techChart.resize()
  }, 100)
}

// 刷新数据
const refreshData = async () => {
  await Promise.all([fetchStatistics(), fetchResources()])
}

// 监听筛选条件变化
watch(
  [filters, sortOptions, sortField],
  () => {
    currentPage.value = 1 // 重置到第一页
    fetchResources()
  },
  { deep: true }
)

// 生命周期
onMounted(async () => {
  // 等待 DOM 更新
  await nextTick()

  // 同时获取统计数据和资源列表
  await Promise.all([fetchStatistics(), fetchResources()])

  // 添加窗口大小监听
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  // 清理事件监听
  window.removeEventListener('resize', handleResize)

  // 清理防抖定时器
  if (window.resizeTimer) {
    clearTimeout(window.resizeTimer)
  }

  // 销毁图表实例
  if (statusChart) {
    statusChart.dispose()
    statusChart = null
  }
  if (techChart) {
    techChart.dispose()
    techChart = null
  }
})
</script>

<template>
  <div id="resources-page" class="page-content">
    <div class="mb-8 container">
      <!-- 页面标题和操作按钮 -->
      <div class="header-section">
        <div class="title-area">
          <h1 class="page-title">资源发布</h1>
          <p class="page-subtitle">分享企业技术资源，建立合作共赢生态</p>
        </div>
        <div class="action-buttons">
          <button
            class="btn-secondary"
            @click="refreshData"
            :disabled="loading || resourcesLoading"
          >
            <FontAwesomeIcon
              :icon="['fas', 'sync-alt']"
              class="mr-2"
              :class="{ 'fa-spin': loading || resourcesLoading }"
            />
            {{ loading || resourcesLoading ? '刷新中...' : '刷新数据' }}
          </button>
          <button class="btn-primary" @click="publishNewResource">
            <FontAwesomeIcon :icon="['fas', 'plus']" class="mr-2" />发布新资源
          </button>
        </div>
      </div>

      <!-- 统计时间范围选择器 -->
      <div class="period-selector">
        <div class="period-title">
          <FontAwesomeIcon :icon="['fas', 'calendar']" class="mr-2" />
          统计周期
        </div>
        <div class="period-buttons">
          <button
            v-for="option in periodOptions"
            :key="option.value"
            :class="['period-btn', { 'period-btn-active': statisticsPeriod === option.value }]"
            @click="changePeriod(option.value)"
            :disabled="loading"
          >
            {{ option.label }}
          </button>
        </div>
      </div>

      <!-- 资源统计概览 -->
      <div class="stats-overview">
        <!-- 状态分布 -->
        <div class="stat-module">
          <div class="module-header">
            <h3 class="module-title">状态分布</h3>
            <FontAwesomeIcon :icon="['fas', 'chart-bar']" class="module-icon" />
          </div>
          <div class="chart-container">
            <div v-if="loading" class="chart-loading">
              <div class="loading-spinner"></div>
              <span>加载中...</span>
            </div>
            <div v-else-if="error" class="chart-error">
              <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" class="error-icon" />
              <span>{{ error }}</span>
              <button @click="fetchStatistics" class="retry-btn">重试</button>
            </div>
            <div
              v-else-if="
                !statusDistribution ||
                statusDistribution.length === 0 ||
                statusDistribution.every((item) => item.value === 0)
              "
              class="chart-empty"
            >
              <span>暂无数据</span>
            </div>
            <div v-else ref="statusChartRef" class="echarts-container"></div>
          </div>
        </div>

        <!-- 数据统计 -->
        <div class="stat-module">
          <div class="module-header">
            <h3 class="module-title">数据统计</h3>
            <FontAwesomeIcon :icon="['fas', 'chart-line']" class="module-icon" />
          </div>
          <div v-if="loading" class="chart-loading">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
          </div>
          <div v-else-if="error" class="chart-error">
            <span>数据加载失败</span>
          </div>
          <div v-else class="data-stats-list">
            <div v-for="stat in dataStats" :key="stat.label" class="stat-row">
              <div class="stat-row-left">
                <FontAwesomeIcon :icon="stat.icon" class="stat-row-icon" />
                <span class="stat-row-label">{{ stat.label }}</span>
              </div>
              <div class="stat-row-right">
                <span class="stat-row-value">{{ stat.value.toLocaleString() }}</span>
                <span
                  class="stat-row-growth"
                  :class="{
                    'growth-positive': parseFloat(stat.growth) > 0,
                    'growth-negative': parseFloat(stat.growth) < 0,
                    'growth-zero': parseFloat(stat.growth) === 0
                  }"
                >
                  {{ parseFloat(stat.growth) >= 0 ? '+' : '' }}{{ stat.growth }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- 热门领域 -->
        <div class="stat-module">
          <div class="module-header">
            <h3 class="module-title">热门领域</h3>
            <FontAwesomeIcon :icon="['fas', 'tags']" class="module-icon" />
          </div>
          <div class="chart-container">
            <div v-if="loading" class="chart-loading">
              <div class="loading-spinner"></div>
              <span>加载中...</span>
            </div>
            <div v-else-if="error" class="chart-error">
              <span>数据加载失败</span>
            </div>
            <div v-else-if="!hotTechFields || hotTechFields.length === 0" class="chart-empty">
              <span>暂无数据</span>
            </div>
            <div v-else ref="techCloudRef" class="echarts-container"></div>
          </div>
        </div>

        <!-- 使用热度 -->
        <div class="stat-module">
          <div class="module-header">
            <h3 class="module-title">使用热度</h3>
            <div class="module-controls">
              <select v-model="rankingType" class="ranking-select" :disabled="loading">
                <option v-for="option in rankingOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </option>
              </select>
            </div>
          </div>
          <div v-if="loading" class="chart-loading">
            <div class="loading-spinner"></div>
            <span>加载中...</span>
          </div>
          <div v-else-if="error" class="chart-error">
            <span>数据加载失败</span>
          </div>
          <div v-else-if="!usageRanking || usageRanking.length === 0" class="chart-empty">
            <span>暂无数据</span>
          </div>
          <div v-else class="usage-ranking">
            <div v-for="item in usageRanking" :key="item.id" class="ranking-item">
              <div class="rank-number">{{ item.rank }}</div>
              <div class="rank-content">
                <h4 class="rank-title">{{ item.title }}</h4>
                <div class="rank-stats">
                  <span class="rank-stat">
                    <FontAwesomeIcon :icon="['fas', 'download']" class="mr-1" />
                    {{ item.downloads }}
                  </span>
                  <span class="rank-stat">
                    <FontAwesomeIcon :icon="['fas', 'eye']" class="mr-1" />
                    {{ item.views }}
                  </span>
                </div>
                <!-- <div class="rank-author">{{ item.author }}</div> -->
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 搜索和筛选 -->
      <div class="search-section" ref="searchSectionRef">
        <div class="search-bar">
          <div class="search-input-wrapper">
            <input
              type="text"
              v-model="searchQuery"
              placeholder="搜索资源名称、描述、技术标签..."
              class="search-input"
              @keyup.enter="performSearch"
            />
            <FontAwesomeIcon :icon="['fas', 'search']" class="search-icon" />
          </div>
          <button
            class="btn-primary search-btn"
            @click="performSearch"
            :disabled="resourcesLoading"
          >
            {{ resourcesLoading ? '搜索中...' : '搜索' }}
          </button>
        </div>

        <div class="filters">
          <select v-model="filters.status" class="filter-select">
            <option value="">所有状态</option>
            <option value="published">已发布</option>
            <option value="draft">草稿</option>
            <option value="unpublished">已下线</option>
          </select>
          <select v-model="filters.type" class="filter-select">
            <option value="">资源类型</option>
            <option value="code">代码</option>
            <option value="dataset">数据集</option>
            <option value="document">文档</option>
            <option value="course">课程</option>
            <option value="video">视频</option>
            <option value="tool">工具</option>
          </select>
          <div class="sort-controls">
            <select v-model="sortField" class="filter-select" @change="updateSortType">
              <option value="">默认排序</option>
              <option value="name">按名称</option>
              <option value="time">按时间</option>
              <option value="download">按下载量</option>
              <option value="view">按浏览量</option>
            </select>
            <select v-model="sortOptions.order" class="filter-select">
              <option value="down">降序</option>
              <option value="up">升序</option>
            </select>
          </div>
          <div class="filter-time">
            <label>创建时间：</label>
            <el-date-picker
              v-model="filters.timeStart"
              type="date"
              placeholder="开始日期"
              class="filter-select"
              value-format="YYYY-MM-DD"
            />
            <span>到</span>
            <el-date-picker
              v-model="filters.timeEnd"
              type="date"
              placeholder="结束日期"
              class="filter-select"
              value-format="YYYY-MM-DD"
            />
          </div>
          <button
            v-if="hasActiveFilters"
            @click="clearFilters"
            class="btn-outline clear-filters-btn"
            title="清除所有筛选条件"
          >
            <FontAwesomeIcon :icon="['fas', 'filter']" class="mr-1" />
            清除筛选
          </button>
        </div>

        <!-- 筛选状态显示 -->
        <div v-if="hasActiveFilters" class="filter-status">
          <div class="filter-status-header">
            <span class="filter-status-title">当前筛选条件：</span>
          </div>
          <div class="filter-tags">
            <span v-if="searchQuery" class="filter-tag">
              <FontAwesomeIcon :icon="['fas', 'search']" class="mr-1" />
              搜索: {{ searchQuery }}
            </span>
            <span v-if="filters.status" class="filter-tag">
              状态: {{ getStatusText(filters.status) }}
            </span>
            <span v-if="filters.type" class="filter-tag">
              类型: {{ getTypeText(filters.type) }}
            </span>
            <span v-if="filters.time" class="filter-tag">
              时间: {{ getTimeText(filters.time) }}
            </span>
            <span v-if="sortField" class="filter-tag">
              排序: {{ getSortText(sortField) }} ({{
                sortOptions.order === 'up' ? '升序' : '降序'
              }})
            </span>
          </div>
        </div>
      </div>

      <!-- 资源列表 -->
      <div class="resources-section">
        <!-- 资源列表加载状态 -->
        <div v-if="resourcesLoading" class="resources-loading">
          <div class="loading-spinner"></div>
          <span>加载资源列表中...</span>
        </div>

        <!-- 资源列表错误状态 -->
        <div v-else-if="resourcesError" class="resources-error">
          <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" class="error-icon" />
          <span>{{ resourcesError }}</span>
          <button @click="fetchResources" class="retry-btn">重试</button>
        </div>

        <!-- 空状态 -->
        <div v-else-if="resources.length === 0" class="resources-empty">
          <FontAwesomeIcon :icon="['fas', 'cube']" class="empty-icon" />
          <h3>暂无资源</h3>
          <p>暂时没有找到相关资源，您可以调整筛选条件或发布新资源</p>
          <button class="btn-primary" @click="publishNewResource">
            <FontAwesomeIcon :icon="['fas', 'plus']" class="mr-2" />发布新资源
          </button>
        </div>

        <!-- 资源列表 -->
        <div v-else class="resources-list">
          <div v-for="resource in resources" :key="resource.id" class="resource-card">
            <div class="resource-content" @click="viewResource(resource.id)">
              <div class="resource-header">
                <div class="resource-info">
                  <div class="resource-meta">
                    <div
                      class="resource-icon"
                      :class="`bg-${resource.iconColor}-100 text-${resource.iconColor}-600`"
                    >
                      <FontAwesomeIcon :icon="resource.icon" class="text-xl" />
                    </div>
                    <div>
                      <h3 class="resource-title">{{ resource.title }}</h3>
                      <div class="resource-badges">
                        <span class="status-badge status-published">{{ resource.status }}</span>
                        <span
                          class="type-badge"
                          :class="`bg-${resource.typeColor}-100 text-${resource.typeColor}-800`"
                        >
                          {{ resource.type }}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div class="resource-stats">
                    <span
                      ><FontAwesomeIcon :icon="['fas', 'clock']" class="mr-1" />发布于
                      {{ resource.publishDate }}</span
                    >
                    <span
                      ><FontAwesomeIcon :icon="['fas', 'eye']" class="mr-1" />浏览
                      {{ resource.views }} 次</span
                    >
                    <span
                      ><FontAwesomeIcon :icon="['fas', 'download']" class="mr-1" />下载
                      {{ resource.downloads }} 次</span
                    >
                  </div>
                </div>
              </div>

              <p class="resource-description">{{ resource.description }}</p>

              <div class="resource-tags" v-if="resource.tags && resource.tags.length > 0">
                <span
                  v-for="tag in resource.tags.slice(0, 4)"
                  :key="tag"
                  class="tag"
                  :class="`bg-${resource.tagColor}-100 text-${resource.tagColor}-700`"
                >
                  {{ tag }}
                </span>
                <span v-if="resource.tags.length > 4" class="tag-more">
                  +{{ resource.tags.length - 4 }}
                </span>
              </div>

              <div class="resource-footer">
                <div class="resource-details">
                  <div class="detail-item">
                    <span class="detail-label">{{ resource.detail1.label }}:</span>
                    <span class="detail-value" :class="resource.detail1.class">{{
                      resource.detail1.value
                    }}</span>
                  </div>
                  <div class="detail-item">
                    <span class="detail-label">{{ resource.detail2.label }}:</span>
                    <span class="detail-value" :class="resource.detail2.class">{{
                      resource.detail2.value
                    }}</span>
                  </div>
                </div>
                <div class="resource-toolbar">
                  <button
                    v-if="resource.status === '已发布'"
                    class="toolbar-btn text-red-500 hover:text-red-700"
                    @click.stop="offlineResource(resource.id)"
                    title="下线"
                  >
                    <FontAwesomeIcon :icon="['fas', 'power-off']" />
                  </button>
                  <button
                    v-if="resource.status === '草稿' || resource.status === '已下线'"
                    class="toolbar-btn text-green-500 hover:text-green-700"
                    @click.stop="publishResource(resource.id)"
                    title="发布"
                  >
                    <FontAwesomeIcon :icon="['fas', 'paper-plane']" />
                  </button>
                  <button
                    class="toolbar-btn text-gray-500 hover:text-gray-700"
                    @click.stop="deleteResource(resource.id)"
                    title="删除"
                  >
                    <FontAwesomeIcon :icon="['fas', 'trash']" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ElementPlus 分页组件 -->
      <div v-if="resources.length > 0" class="pagination-wrapper">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[5, 10, 20, 50, 100]"
          :total="pagination.total_count"
          :disabled="resourcesLoading"
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

<style scoped lang="scss">
.page-content {
  min-height: 100vh;
  background-color: #f8fafc;
  padding: 1rem;

  .container {
    max-width: 1500px;
    margin: 0 auto;
  }
}

.header-section {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
  margin-bottom: 1.5rem;

  @media (min-width: 640px) {
    flex-direction: row;
    align-items: center;
  }
}

.title-area {
  .page-title {
    font-size: clamp(1.5rem, 3vw, 2rem);
    font-weight: 700;
    color: #111827;
  }

  .page-subtitle {
    color: #6b7280;
    margin-top: 0.5rem;
  }
}

.action-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

// 统计时间范围选择器
.period-selector {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);

  .period-title {
    display: flex;
    align-items: center;
    font-weight: 600;
    color: #374151;
    font-size: 0.875rem;
  }

  .period-buttons {
    display: flex;
    gap: 0.5rem;
  }

  .period-btn {
    padding: 0.5rem 1rem;
    border: 1px solid #d1d5db;
    background-color: white;
    color: #6b7280;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease-in-out;

    &:hover:not(:disabled) {
      background-color: #f9fafb;
      border-color: #9ca3af;
    }

    &.period-btn-active {
      background-color: #2563eb;
      border-color: #2563eb;
      color: white;
    }

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
  }
}

.stats-overview {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  margin-bottom: 2rem;

  @media (min-width: 640px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (min-width: 1300px) {
    grid-template-columns: repeat(4, 1fr);
  }
}

.stat-module {
  background-color: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;
  border: 1px solid #f3f4f6;

  &:hover {
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }
}

.module-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #f3f4f6;

  .module-title {
    font-size: 1rem;
    font-weight: 600;
    color: #111827;
  }

  .module-icon {
    color: #6b7280;
    font-size: 1.125rem;
  }

  .module-controls {
    .ranking-select {
      padding: 0.25rem 0.5rem;
      border: 1px solid #d1d5db;
      border-radius: 0.375rem;
      background-color: white;
      color: #6b7280;
      font-size: 0.875rem;
      cursor: pointer;
      transition: all 0.15s ease-in-out;

      &:hover {
        border-color: #9ca3af;
      }
    }
  }
}

// ECharts 容器样式
.chart-container {
  .echarts-container {
    width: 100%;
    height: 240px; // 增加高度，更好利用卡片空间
  }
}

// 加载状态样式
.chart-loading,
.resources-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 240px; // 与图表容器高度保持一致
  color: #6b7280;
  font-size: 0.875rem;

  .loading-spinner {
    width: 24px;
    height: 24px;
    border: 2px solid #e5e7eb;
    border-top: 2px solid #6366f1;
    border-radius: 50%;
    margin-bottom: 0.5rem;
    animation: spin 1s linear infinite;
  }
}

.resources-loading {
  height: 200px;
  background-color: white;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

// 错误状态样式
.chart-error,
.resources-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 240px; // 与图表容器高度保持一致
  color: #ef4444;
  font-size: 0.875rem;
  text-align: center;

  .error-icon {
    font-size: 1.5rem;
    margin-bottom: 0.5rem;
  }

  .retry-btn {
    margin-top: 0.75rem;
    padding: 0.5rem 1rem;
    background-color: #6366f1;
    color: white;
    border: none;
    border-radius: 0.375rem;
    font-size: 0.75rem;
    cursor: pointer;
    transition: background-color 0.15s ease-in-out;

    &:hover {
      background-color: #5b5cf6;
    }
  }
}

.resources-error {
  height: 200px;
  background-color: white;
  border-radius: 0.5rem;
  margin-bottom: 1.5rem;
}

// 空数据状态样式
.chart-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 240px; // 与图表容器高度保持一致
  color: #9ca3af;
  font-size: 0.875rem;
}

.resources-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  background-color: white;
  border-radius: 0.5rem;
  text-align: center;
  margin-bottom: 1.5rem;

  .empty-icon {
    font-size: 3rem;
    color: #d1d5db;
    margin-bottom: 1rem;
  }

  h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
  }

  p {
    color: #6b7280;
    margin-bottom: 1.5rem;
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

// 数据统计样式
.data-stats-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.stat-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  transition: background-color 0.15s ease-in-out;

  &:hover {
    background-color: #f3f4f6;
  }

  .stat-row-left {
    display: flex;
    align-items: center;

    .stat-row-icon {
      color: #6366f1;
      margin-right: 0.75rem;
      font-size: 1rem;
    }

    .stat-row-label {
      font-size: 0.875rem;
      color: #4b5563;
      font-weight: 500;
    }
  }

  .stat-row-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;

    .stat-row-value {
      font-size: 1rem;
      font-weight: 700;
      color: #111827;
    }

    .stat-row-growth {
      font-size: 0.75rem;
      font-weight: 500;

      &.growth-positive {
        color: #10b981; // 增长为绿色
      }

      &.growth-negative {
        color: #ef4444; // 减少为红色
      }

      &.growth-zero {
        color: #9ca3af; // 无变化为灰色
      }
    }
  }
}

// 使用热度排行样式
.usage-ranking {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ranking-item {
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  transition: all 0.2s ease-in-out;

  &:hover {
    background-color: #f3f4f6;
    transform: translateX(4px);
  }

  .rank-number {
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 0.875rem;
    margin-right: 0.75rem;
    flex-shrink: 0;
  }

  .rank-content {
    flex: 1;
    min-width: 0;

    .rank-title {
      font-size: 0.875rem;
      font-weight: 600;
      color: #111827;
      margin-bottom: 0.25rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .rank-stats {
      display: flex;
      gap: 1rem;
      margin-bottom: 0.25rem;

      .rank-stat {
        font-size: 0.75rem;
        color: #6b7280;
        display: flex;
        align-items: center;
      }
    }

    .rank-author {
      font-size: 0.7rem;
      color: #9ca3af;
      font-style: italic;
    }
  }
}

.search-section {
  background-color: white;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.search-bar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;

  @media (min-width: 1024px) {
    flex-direction: row;
  }
}

.search-input-wrapper {
  flex: 1;
  position: relative;

  .search-input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    background-color: #f9fafb;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    border: none;
    outline: none;
    transition: all 0.15s ease-in-out;

    &:focus {
      ring: 2px solid #60a5fa;
      background-color: white;
    }
  }

  .search-icon {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    color: #9ca3af;
  }
}

.search-btn {
  padding: 0.75rem 1.5rem;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;

  .filter-time {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 1rem;
    flex-wrap: wrap;
    label {
      font-weight: 500;
      color: #4b5563;
    }

    :deep(.el-input) {
      width: 140px;
    }
  }

  span {
    font-weight: 500;
    color: #4b5563;
  }
}

.sort-controls {
  display: flex;
  gap: 0.5rem;
}

.clear-filters-btn {
  background-color: #fef2f2;
  color: #dc2626;
  border-color: #fecaca;

  &:hover {
    background-color: #fee2e2;
    border-color: #fca5a5;
  }
}

.filter-status {
  margin-top: 1rem;
  padding: 1rem;
  background-color: #f0f9ff;
  border-radius: 0.5rem;
  border: 1px solid #e0f2fe;

  .filter-status-header {
    margin-bottom: 0.5rem;

    .filter-status-title {
      font-size: 0.875rem;
      font-weight: 500;
      color: #0369a1;
    }
  }

  .filter-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;

    .filter-tag {
      padding: 0.25rem 0.75rem;
      background-color: #0284c7;
      color: white;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 500;
      display: flex;
      align-items: center;
    }
  }
}

.filter-select {
  padding: 0.5rem 1rem;
  background-color: #f9fafb;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  border: none;
  outline: none;
  transition: all 0.15s ease-in-out;

  &:focus {
    ring: 2px solid #60a5fa;
    background-color: white;
  }
}

.resources-section {
  margin-bottom: 2rem;
}

.resources-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.resource-card {
  background-color: white;
  border-radius: 0.5rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease-in-out;

  &:hover {
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  }

  .resource-content {
    padding: 1.5rem;
  }
}

.resource-header {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  margin-bottom: 1rem;

  @media (min-width: 1024px) {
    flex-direction: row;
    align-items: center;
  }
}

.resource-info {
  flex: 1;
}

.resource-meta {
  display: flex;
  align-items: center;
  margin-bottom: 0.5rem;

  .resource-icon {
    width: 3rem;
    height: 3rem;
    margin-right: 1rem;
    border-radius: 0.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .resource-title {
    font-weight: 600;
    font-size: 1.125rem;
    color: #111827;
  }
}

.resource-badges {
  display: flex;
  align-items: center;
  margin-top: 0.25rem;

  .status-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-right: 0.5rem;

    &.status-published {
      background-color: #dcfce7;
      color: #166534;
    }
  }

  .type-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
  }
}

.resource-stats {
  display: flex;
  align-items: center;
  font-size: 0.875rem;
  color: #6b7280;
  gap: 1rem;
  margin-left: 4rem;
  margin-top: 0.25rem;
}

.resource-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1rem;

  @media (min-width: 1024px) {
    margin-top: 0;
  }
}

.resource-description {
  color: #4b5563;
  margin-bottom: 1rem;
  margin-left: 4rem;
  line-height: 1.6;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.resource-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
  margin-left: 4rem;

  .tag {
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .tag-more {
    padding: 0.25rem 0.75rem;
    background-color: #f3f4f6;
    color: #4b5563;
    border-radius: 9999px;
    font-size: 0.75rem;
    font-weight: 500;
  }
}

.resource-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-top: 1rem;
  border-top: 1px solid #f3f4f6;
}

.resource-details {
  display: flex;
  align-items: center;
  gap: 1.5rem;

  .detail-item {
    font-size: 0.875rem;

    .detail-label {
      color: #6b7280;
    }

    .detail-value {
      margin-left: 0.25rem;
    }
  }
}

.resource-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-btn {
  color: #6b7280;
  padding: 0.5rem;
  transition: color 0.15s ease-in-out;
  cursor: pointer;
  border: none;
  background: none;

  &:hover {
    color: #374151;
  }
}

// ElementPlus 分页样式
.pagination-wrapper {
  display: flex;
  justify-content: center;
  padding: 1rem;

  .custom-pagination {
    // 自定义分页组件样式
    --el-pagination-font-size: 14px;
    --el-pagination-bg-color: #ffffff;
    --el-pagination-text-color: #606266;
    --el-pagination-border-radius: 4px;
    --el-pagination-button-color: #606266;
    --el-pagination-button-bg-color: #ffffff;
    --el-pagination-button-disabled-color: #c0c4cc;
    --el-pagination-button-disabled-bg-color: #ffffff;
    --el-pagination-hover-color: #2563eb;

    :deep(.el-pagination__total) {
      color: #6b7280;
      font-weight: 500;
    }

    :deep(.el-pagination__sizes) {
      .el-select {
        .el-input__wrapper {
          border-radius: 0.375rem;
          box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        }
      }
    }

    :deep(.el-pager) {
      li {
        border-radius: 0.375rem;
        margin: 0 2px;
        min-width: 32px;
        height: 32px;
        line-height: 30px;

        &.is-active {
          background-color: #2563eb;
          color: white;
        }

        &:hover:not(.is-active):not(.is-disabled) {
          background-color: #f3f4f6;
        }
      }
    }

    :deep(.btn-prev),
    :deep(.btn-next) {
      border-radius: 0.375rem;
      width: 32px;
      height: 32px;

      &:hover:not(.is-disabled) {
        background-color: #f3f4f6;
      }
    }

    :deep(.el-pagination__jump) {
      .el-input__wrapper {
        border-radius: 0.375rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);

        &.is-focus {
          box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
        }
      }
    }
  }

  @media (max-width: 768px) {
    .custom-pagination {
      :deep(.el-pagination__total),
      :deep(.el-pagination__sizes) {
        display: none;
      }

      :deep(.el-pagination__jump) {
        margin-left: 8px;

        .el-pagination__jump-text {
          display: none;
        }

        .el-input {
          width: 60px;
          margin-left: 0;
        }
      }
    }
  }

  @media (max-width: 480px) {
    .custom-pagination {
      :deep(.el-pagination__jump) {
        display: none;
      }
    }
  }
}

// 按钮样式
.btn-primary {
  background-color: #2563eb;
  color: white;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;

  &:hover {
    background-color: #1d4ed8;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-secondary {
  background-color: #f3f4f6;
  color: #374151;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;

  &:hover {
    background-color: #e5e7eb;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
}

.btn-outline {
  border: 1px solid #d1d5db;
  color: #374151;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  background-color: white;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;

  &:hover {
    background-color: #f9fafb;
  }
}

// 颜色工具类
.text-primary {
  color: #2563eb;
}
.text-blue-500 {
  color: #3b82f6;
}
.text-green-500 {
  color: #10b981;
}
.text-orange-500 {
  color: #f59e0b;
}
.text-purple-500 {
  color: #8b5cf6;
}
.text-red-500 {
  color: #ef4444;
}
.text-gray-500 {
  color: #6b7280;
}
.text-secondary {
  color: #6366f1;
}

.bg-primary-100 {
  background-color: #dbeafe;
}
.bg-blue-100 {
  background-color: #dbeafe;
}
.bg-green-100 {
  background-color: #dcfce7;
}
.bg-orange-100 {
  background-color: #fef3c7;
}
.bg-purple-100 {
  background-color: #f3e8ff;
}
.bg-red-100 {
  background-color: #fee2e2;
}
.bg-gray-100 {
  background-color: #f3f4f6;
}

.text-primary-600 {
  color: #2563eb;
}
.text-blue-600 {
  color: #2563eb;
}
.text-green-600 {
  color: #059669;
}
.text-orange-600 {
  color: #d97706;
}
.text-purple-600 {
  color: #7c3aed;
}
.text-red-600 {
  color: #dc2626;
}
.text-gray-600 {
  color: #4b5563;
}

.text-blue-700 {
  color: #1d4ed8;
}
.text-green-700 {
  color: #047857;
}
.text-orange-700 {
  color: #b45309;
}
.text-purple-700 {
  color: #6d28d9;
}
.text-red-700 {
  color: #b91c1c;
}
.text-gray-700 {
  color: #374151;
}

.text-blue-800 {
  color: #1e40af;
}
.text-green-800 {
  color: #065f46;
}
.text-orange-800 {
  color: #92400e;
}
.text-purple-800 {
  color: #5b21b6;
}
.text-red-800 {
  color: #991b1b;
}
.text-gray-800 {
  color: #1f2937;
}

.border-blue-500 {
  border-color: #3b82f6;
}
.border-green-500 {
  border-color: #10b981;
}
.border-orange-500 {
  border-color: #f59e0b;
}
.border-purple-500 {
  border-color: #8b5cf6;
}
.border-red-500 {
  border-color: #ef4444;
}
.border-gray-500 {
  border-color: #6b7280;
}

// 响应式设计
@media (max-width: 640px) {
  .stat-module {
    padding: 1rem;
  }

  .chart-container {
    .echarts-container {
      height: 200px; // 小屏幕上适当减少高度
    }
  }

  // 同步更新其他状态容器高度
  .chart-loading,
  .chart-error,
  .chart-empty {
    height: 200px;
  }

  .resources-loading,
  .resources-error {
    height: 150px;
  }

  .ranking-item {
    .rank-title {
      font-size: 0.8rem;
    }
  }

  .resource-stats {
    margin-left: 0;
    flex-wrap: wrap;
  }

  .resource-description {
    margin-left: 0;
  }

  .resource-tags {
    margin-left: 0;
  }

  .resource-details {
    flex-wrap: wrap;
    gap: 0.5rem;

    .detail-item {
      margin-bottom: 0.5rem;
    }
  }

  .filter-status {
    .filter-tags {
      .filter-tag {
        font-size: 0.7rem;
        padding: 0.2rem 0.6rem;
      }
    }
  }
}
</style>
