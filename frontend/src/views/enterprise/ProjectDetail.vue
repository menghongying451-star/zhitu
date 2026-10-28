<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faBriefcase,
  faUsers,
  faCalendarAlt,
  faFileAlt,
  faDownload,
  faExternalLinkAlt,
  faComment,
  faReply,
  faCrown,
  faUser,
  faLink,
  faChevronDown,
  faChevronRight,
  faSpinner,
  faTrash,
  faStar, // 评分相关图标
  faEdit,
  faCheck,
  faPlus
} from '@fortawesome/free-solid-svg-icons'
import { projectService, projectScoreService } from '@/api'
import { useUserStore } from '@/stores'

const userStore = useUserStore()
const route = useRoute()

// 添加图标到库
library.add(
  faBriefcase,
  faUsers,
  faCalendarAlt,
  faFileAlt,
  faDownload,
  faExternalLinkAlt,
  faComment,
  faReply,
  faCrown,
  faUser,
  faLink,
  faChevronDown,
  faChevronRight,
  faSpinner,
  faTrash,
  faStar,
  faEdit,
  faCheck,
  faPlus
)

// 响应式数据
const projectData = ref(null)
const projectComments = ref([])
const loading = ref(true)
const commentsLoading = ref(false)

// 评论相关状态
const newComment = ref('')
const deliverableCommentTexts = ref(new Map()) // deliverableId -> comment text
const replyingTo = ref(null)
const replyContent = ref('')
const replyContext = ref(null)

// 删除相关状态
const deletingComments = ref(new Set()) // 正在删除的评论ID集合

// 提交评论相关状态
const submittingProjectComment = ref(false) // 项目评论提交状态
const submittingDeliverableComments = ref(new Set()) // 正在提交的成果评论ID集合
const submittingReply = ref(false) // 回复提交状态

// 成果展开状态
const expandedDeliverables = ref(new Set())
const deliverableDetails = ref(new Map()) // deliverableId -> detail
const deliverableComments = ref(new Map()) // deliverableId -> comments[]
const deliverableLoading = ref(new Set()) // 加载中的成果ID

// 回复展开状态
const expandedReplies = ref(new Set()) // commentId -> boolean
const commentReplies = ref(new Map()) // commentId -> replies[]
const replyLoading = ref(new Set()) // 加载中的评论ID

// 分页状态
const projectCommentsPagination = ref({
  currentPage: 1,
  hasMore: true,
  loading: false
})

const deliverableCommentsPagination = ref(new Map()) // deliverableId -> pagination info
const repliesPagination = ref(new Map()) // commentId -> pagination info

// 评分相关状态
const scoreData = ref(null) // 项目评分数据
const scoreStandard = ref(null) // 评分标准
const scoreFormData = ref({
  overall_comment: '',
  indicator_scores: []
}) // 评分表单数据
const scoreLoading = ref(false)
const scoreSubmitting = ref(false)
const scoreFormVisible = ref(false) // 评分表单是否显示
const scoreMode = ref('') // 'create', 'update', 'view'

// 项目状态映射
const statusMap = {
  recruiting: { text: '招募中', type: 'warning' },
  in_progress: { text: '进行中', type: 'primary' },
  completed: { text: '已完成', type: 'success' },
  suspended: { text: '暂停', type: 'info' },
  cancelled: { text: '已取消', type: 'danger' }
}

// 成果阶段映射
const stageMap = {
  early: { text: '前期', color: '#409eff' },
  middle: { text: '中期', color: '#e6a23c' },
  final: { text: '后期', color: '#67c23a' }
}

// 计算属性
const projectStatus = computed(() => {
  if (!projectData.value) return null
  return statusMap[projectData.value.status] || { text: '未知', type: 'info' }
})

// 检查是否有评分权限
const hasScorePermission = computed(() => {
  if (!userStore.user || !projectData.value) return false

  // 检查用户是否为管理员或所有者
  const userRole = userStore.user.company_profile?.permission
  if (userRole === 'admin' || userRole === 'owner') {
    return true
  }

  // 检查用户是否为需求创建者
  if (projectData.value.requirement && projectData.value.requirement.creator_id) {
    return userStore.user.id === projectData.value.requirement.creator_id
  }

  return false
})

// 评分状态计算
const scoreStatus = computed(() => {
  if (!projectData.value) return null

  const isEvaluated = projectData.value.is_evaluated

  if (!isEvaluated) {
    return { type: 'none', text: '未评分' }
  }

  // 如果有评分但还没获取到评分详情，显示加载状态
  if (!scoreData.value) {
    return { type: 'loading', text: '加载中...', color: '#909399' }
  }

  if (scoreData.value.status === 'draft') {
    return { type: 'draft', text: '草稿', color: '#e6a23c' }
  }

  if (scoreData.value.status === 'submitted') {
    return { type: 'submitted', text: '已提交', color: '#409eff' }
  }

  if (scoreData.value.status === 'published') {
    return { type: 'published', text: '已公示', color: '#67c23a' }
  }

  return { type: 'unknown', text: '未知状态' }
})

// 检查当前用户是否可以删除评论
const canDeleteComment = (comment) => {
  return userStore.user && comment.author_info && comment.author_info.id === userStore.user.id
}

// 删除评论
const deleteComment = async (commentId, context = null) => {
  try {
    await ElMessageBox.confirm('确定要删除这条评论吗？删除后无法恢复。', '删除确认', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })

    deletingComments.value.add(commentId)
    const projectId = route.params.id

    const response = await projectService.deleteComment(projectId, commentId)

    if (response.status === 'success') {
      ElMessage.success('评论删除成功')

      // 根据上下文类型更新相应的评论列表
      if (context) {
        if (context.type === 'project') {
          // 删除项目评论
          await refreshProjectComments()
        } else if (context.type === 'deliverable') {
          // 删除成果评论
          await refreshDeliverableComments(context.deliverableId)
        } else if (context.type === 'reply') {
          // 删除回复
          if (context.isDeliverableReply) {
            await refreshDeliverableComments(context.deliverableId)
          } else {
            await refreshProjectComments()
          }
          // 同时刷新回复列表
          if (context.parentCommentId) {
            await refreshReplies(context.parentCommentId)
          }
        }
      } else {
        // 兜底：刷新所有评论
        await refreshProjectComments()
      }
    } else {
      ElMessage.error(response.message || '删除评论失败')
    }
  } catch (error) {
    if (error === 'cancel') {
      return // 用户取消删除
    }
    console.error('删除评论失败:', error)
    ElMessage.error('删除评论失败')
  } finally {
    deletingComments.value.delete(commentId)
  }
}

// 刷新项目评论
const refreshProjectComments = async () => {
  try {
    const projectId = route.params.id
    const response = await projectService.getCommentList(projectId, {
      page: 1,
      page_size: projectCommentsPagination.value.currentPage * 10
    })

    if (response.status === 'success') {
      const commentsData = response.data
      projectComments.value = commentsData.comments || []

      // 更新分页信息
      projectCommentsPagination.value = {
        ...projectCommentsPagination.value,
        hasMore:
          (commentsData.comments || []).length === projectCommentsPagination.value.currentPage * 10
      }
    }
  } catch (error) {
    console.error('刷新项目评论失败:', error)
  }
}

// 刷新成果评论
const refreshDeliverableComments = async (deliverableId) => {
  try {
    const projectId = route.params.id
    const currentPagination = deliverableCommentsPagination.value.get(deliverableId)
    const pageSize = currentPagination ? currentPagination.currentPage * 10 : 10

    const response = await projectService.getCommentList(projectId, {
      deliverable_id: deliverableId,
      page: 1,
      page_size: pageSize
    })

    if (response.status === 'success') {
      const commentsData = response.data
      deliverableComments.value.set(deliverableId, commentsData.comments || [])

      // 更新分页信息
      if (currentPagination) {
        deliverableCommentsPagination.value.set(deliverableId, {
          ...currentPagination,
          hasMore: (commentsData.comments || []).length === pageSize
        })
      }
    }
  } catch (error) {
    console.error('刷新成果评论失败:', error)
  }
}

// 刷新回复
const refreshReplies = async (commentId) => {
  try {
    const projectId = route.params.id
    const currentPagination = repliesPagination.value.get(commentId)
    const pageSize = currentPagination ? currentPagination.currentPage * 10 : 10

    const response = await projectService.getReplyList(projectId, commentId, {
      page: 1,
      page_size: pageSize
    })

    if (response.status === 'success') {
      const repliesData = response.data
      commentReplies.value.set(commentId, repliesData.replies || [])

      // 更新分页信息
      if (currentPagination) {
        repliesPagination.value.set(commentId, {
          ...currentPagination,
          hasMore: (repliesData.replies || []).length === pageSize
        })
      }
    }
  } catch (error) {
    console.error('刷新回复失败:', error)
  }
}

// 获取项目详情和评论（并行请求）
const fetchProjectData = async () => {
  try {
    loading.value = true
    const projectId = route.params.id

    // 并行请求项目详情和项目评论
    const [projectResponse, commentsResponse] = await Promise.all([
      projectService.getProjectDetail(projectId),
      projectService.getCommentList(projectId, { page: 1, page_size: 10 })
    ])

    if (projectResponse.status === 'success') {
      projectData.value = projectResponse.data
      // 如果项目有评分，获取评分详情
      if (projectData.value.is_evaluated) {
        await fetchScoreData()
      }
    } else {
      ElMessage.error(projectResponse.message || '获取项目详情失败')
    }

    if (commentsResponse.status === 'success') {
      const commentsData = commentsResponse.data
      projectComments.value = commentsData.comments || []

      // 更新项目评论分页信息
      projectCommentsPagination.value = {
        currentPage: 1,
        hasMore: (commentsData.comments || []).length === 10,
        loading: false
      }
    } else {
      ElMessage.error(commentsResponse.message || '获取项目评论失败')
    }
  } catch (error) {
    console.error('获取项目数据失败:', error)
    ElMessage.error('获取项目数据失败')
  } finally {
    loading.value = false
  }
}

// 获取评分数据
const fetchScoreData = async () => {
  if (!projectData.value?.is_evaluated) return

  try {
    const projectId = route.params.id
    const response = await projectScoreService.getProjectScoreDetail(projectId)
    if (response.status === 'success') {
      scoreData.value = response.data
    }
  } catch (error) {
    console.error('获取评分数据失败:', error)
  }
}

// 获取评分标准
const fetchScoreStandard = async () => {
  if (!projectData.value?.requirement?.evaluation_criteria_id) return

  try {
    scoreLoading.value = true
    const response = await projectScoreService.getScoreStandardDetail(
      projectData.value.requirement.evaluation_criteria_id
    )
    if (response.status === 'success') {
      scoreStandard.value = response.data
      // 初始化表单数据
      initScoreForm()
    } else {
      ElMessage.error(response.message || '获取评分标准失败')
    }
  } catch (error) {
    console.error('获取评分标准失败:', error)
    ElMessage.error('获取评分标准失败')
  } finally {
    scoreLoading.value = false
  }
}

// 初始化评分表单
const initScoreForm = () => {
  if (!scoreStandard.value) return

  // 如果是更新模式且有现有评分数据，使用现有数据
  if (scoreMode.value === 'update' && scoreData.value) {
    scoreFormData.value = {
      overall_comment: scoreData.value.overall_comment || '',
      indicator_scores:
        scoreData.value.indicator_scores?.map((item) => ({
          indicator_id: item.indicator,
          score: parseFloat(item.score),
          comment: item.comment || ''
        })) || []
    }
  } else {
    // 创建模式，初始化空表单
    scoreFormData.value = {
      overall_comment: '',
      indicator_scores:
        scoreStandard.value.indicators?.map((indicator) => ({
          indicator_id: indicator.id,
          score: 0,
          comment: ''
        })) || []
    }
  }
}

// 显示创建评分表单
const showCreateScoreForm = async () => {
  scoreMode.value = 'create'
  scoreFormVisible.value = true
  await fetchScoreStandard()
}

// 显示更新评分表单
const showUpdateScoreForm = async () => {
  scoreMode.value = 'update'
  scoreFormVisible.value = true
  await fetchScoreStandard()
}

// 关闭评分表单
const closeScoreForm = () => {
  scoreFormVisible.value = false
  scoreMode.value = ''
  scoreFormData.value = {
    overall_comment: '',
    indicator_scores: []
  }
}

// 提交评分表单
const submitScoreForm = async () => {
  try {
    // 验证必填字段
    const requiredIndicators =
      scoreStandard.value.indicators?.filter((ind) => ind.is_required) || []
    const missingRequired = requiredIndicators.filter((indicator) => {
      const score = scoreFormData.value.indicator_scores.find(
        (s) => s.indicator_id === indicator.id
      )
      return !score || score.score === 0
    })

    if (missingRequired.length > 0) {
      ElMessage.warning(
        `请完成必填指标的评分：${missingRequired.map((ind) => ind.name).join(', ')}`
      )
      return
    }

    scoreSubmitting.value = true
    const projectId = route.params.id

    let response
    if (scoreMode.value === 'create') {
      response = await projectScoreService.createProjectScore(projectId, scoreFormData.value)
    } else if (scoreMode.value === 'update') {
      response = await projectScoreService.updateProjectScore(projectId, scoreFormData.value)
    }

    if (response.status === 'success') {
      ElMessage.success(scoreMode.value === 'create' ? '评分创建成功' : '评分更新成功')
      closeScoreForm()
      // 重新获取项目数据
      await fetchProjectData()
    } else {
      ElMessage.error(response.message || '评分操作失败')
    }
  } catch (error) {
    console.error('提交评分失败:', error)
    ElMessage.error('评分操作失败')
  } finally {
    scoreSubmitting.value = false
  }
}

// 提交评分（将草稿状态改为已提交）
const submitScore = async () => {
  try {
    await ElMessageBox.confirm('确定要提交评分吗？提交后将无法再修改。', '提交确认', {
      confirmButtonText: '提交',
      cancelButtonText: '取消',
      type: 'warning'
    })
    const projectId = route.params.id
    scoreSubmitting.value = true
    const response = await projectScoreService.submitProjectScore(projectId)

    if (response.status === 'success') {
      ElMessage.success('评分提交成功')
      // 重新获取项目数据
      await fetchProjectData()
    } else {
      ElMessage.error(response.message || '提交评分失败')
    }
  } catch (error) {
    if (error === 'cancel') {
      return // 用户取消提交
    }
    console.error('提交评分失败:', error)
    ElMessage.error('提交评分失败')
  } finally {
    scoreSubmitting.value = false
  }
}

// 获取指标评分
const getIndicatorScore = (indicatorId) => {
  return scoreFormData.value.indicator_scores.find((s) => s.indicator_id === indicatorId)
}

// 更新指标评分
const updateIndicatorScore = (indicatorId, field, value) => {
  const index = scoreFormData.value.indicator_scores.findIndex(
    (s) => s.indicator_id === indicatorId
  )
  if (index !== -1) {
    scoreFormData.value.indicator_scores[index][field] = value
  }
}

// 加载更多项目评论
const loadMoreProjectComments = async () => {
  if (!projectCommentsPagination.value.hasMore || projectCommentsPagination.value.loading) {
    return
  }

  try {
    projectCommentsPagination.value.loading = true
    const projectId = route.params.id
    const nextPage = projectCommentsPagination.value.currentPage + 1

    const response = await projectService.getCommentList(projectId, {
      page: nextPage,
      page_size: 10
    })

    if (response.status === 'success') {
      const newComments = response.data.comments || []
      projectComments.value.push(...newComments)

      projectCommentsPagination.value = {
        currentPage: nextPage,
        hasMore: newComments.length === 10,
        loading: false
      }
    } else {
      ElMessage.error(response.message || '加载更多评论失败')
    }
  } catch (error) {
    console.error('加载更多项目评论失败:', error)
    ElMessage.error('加载更多评论失败')
  } finally {
    projectCommentsPagination.value.loading = false
  }
}

// 切换成果展开状态
const toggleDeliverable = async (deliverableId) => {
  const isExpanded = expandedDeliverables.value.has(deliverableId)

  if (isExpanded) {
    // 收起
    expandedDeliverables.value.delete(deliverableId)
  } else {
    // 展开 - 并行获取成果详情和评论
    expandedDeliverables.value.add(deliverableId)

    if (!deliverableDetails.value.has(deliverableId)) {
      try {
        deliverableLoading.value.add(deliverableId)
        const projectId = route.params.id

        const [detailResponse, commentsResponse] = await Promise.all([
          projectService.getDeliverableDetail(projectId, deliverableId),
          projectService.getCommentList(projectId, {
            deliverable_id: deliverableId,
            page: 1,
            page_size: 10
          })
        ])

        if (detailResponse.status === 'success') {
          deliverableDetails.value.set(deliverableId, detailResponse.data)
        }

        if (commentsResponse.status === 'success') {
          const commentsData = commentsResponse.data
          deliverableComments.value.set(deliverableId, commentsData.comments || [])

          // 初始化成果评论分页信息
          deliverableCommentsPagination.value.set(deliverableId, {
            currentPage: 1,
            hasMore: (commentsData.comments || []).length === 10,
            loading: false
          })
        }
      } catch (error) {
        console.error('获取成果数据失败:', error)
        ElMessage.error('获取成果数据失败')
      } finally {
        deliverableLoading.value.delete(deliverableId)
      }
    }
  }
}

// 加载更多成果评论
const loadMoreDeliverableComments = async (deliverableId) => {
  const pagination = deliverableCommentsPagination.value.get(deliverableId)
  if (!pagination || !pagination.hasMore || pagination.loading) {
    return
  }

  try {
    pagination.loading = true
    const projectId = route.params.id
    const nextPage = pagination.currentPage + 1

    const response = await projectService.getCommentList(projectId, {
      deliverable_id: deliverableId,
      page: nextPage,
      page_size: 10
    })

    if (response.status === 'success') {
      const newComments = response.data.comments || []
      const existingComments = deliverableComments.value.get(deliverableId) || []
      deliverableComments.value.set(deliverableId, [...existingComments, ...newComments])

      deliverableCommentsPagination.value.set(deliverableId, {
        currentPage: nextPage,
        hasMore: newComments.length === 10,
        loading: false
      })
    } else {
      ElMessage.error(response.message || '加载更多成果评论失败')
    }
  } catch (error) {
    console.error('加载更多成果评论失败:', error)
    ElMessage.error('加载更多成果评论失败')
  } finally {
    pagination.loading = false
  }
}

// 切换回复展开状态
const toggleReplies = async (commentId) => {
  const isExpanded = expandedReplies.value.has(commentId)

  if (isExpanded) {
    expandedReplies.value.delete(commentId)
  } else {
    expandedReplies.value.add(commentId)

    if (!commentReplies.value.has(commentId)) {
      try {
        replyLoading.value.add(commentId)
        const projectId = route.params.id

        const response = await projectService.getReplyList(projectId, commentId, {
          page: 1,
          page_size: 10
        })

        if (response.status === 'success') {
          const repliesData = response.data
          commentReplies.value.set(commentId, repliesData.replies || [])

          // 初始化回复分页信息
          repliesPagination.value.set(commentId, {
            currentPage: 1,
            hasMore: (repliesData.replies || []).length === 10,
            loading: false
          })
        }
      } catch (error) {
        console.error('获取回复失败:', error)
        ElMessage.error('获取回复失败')
      } finally {
        replyLoading.value.delete(commentId)
      }
    }
  }
}

// 加载更多回复
const loadMoreReplies = async (commentId) => {
  const pagination = repliesPagination.value.get(commentId)
  if (!pagination || !pagination.hasMore || pagination.loading) {
    return
  }

  try {
    pagination.loading = true
    const projectId = route.params.id
    const nextPage = pagination.currentPage + 1

    const response = await projectService.getReplyList(projectId, commentId, {
      page: nextPage,
      page_size: 10
    })

    if (response.status === 'success') {
      const newReplies = response.data.replies || []
      const existingReplies = commentReplies.value.get(commentId) || []
      commentReplies.value.set(commentId, [...existingReplies, ...newReplies])

      repliesPagination.value.set(commentId, {
        currentPage: nextPage,
        hasMore: newReplies.length === 10,
        loading: false
      })
    } else {
      ElMessage.error(response.message || '加载更多回复失败')
    }
  } catch (error) {
    console.error('加载更多回复失败:', error)
    ElMessage.error('加载更多回复失败')
  } finally {
    pagination.loading = false
  }
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  const sizes = ['B', 'KB', 'MB', 'GB']
  if (bytes === 0) return '0 B'
  const i = parseInt(Math.floor(Math.log(bytes) / Math.log(1024)))
  return Math.round((bytes / Math.pow(1024, i)) * 100) / 100 + ' ' + sizes[i]
}

// 格式化时间
const formatDate = (dateString) => {
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 下载文件
const downloadFile = (file) => {
  if (file.is_cloud_link) {
    window.open(file.cloud_link_url || file.file_url, '_blank')
  } else {
    const link = document.createElement('a')
    link.href = file.file_url
    link.download = file.name
    link.click()
  }
}

// 提交项目评论
const submitProjectComment = async () => {
  if (!newComment.value.trim() || submittingProjectComment.value) return

  try {
    submittingProjectComment.value = true
    const projectId = route.params.id
    const response = await projectService.publishComment(
      projectId,
      {},
      { content: newComment.value.trim() }
    )

    if (response.status === 'success') {
      ElMessage.success('项目评论发表成功')
      newComment.value = ''
      // 重新获取项目评论
      await fetchProjectComments()
    } else {
      ElMessage.error(response.message || '评论发表失败')
    }
  } catch (error) {
    console.error('提交评论失败:', error)
    ElMessage.error('评论发表失败')
  } finally {
    submittingProjectComment.value = false
  }
}

// 提交成果评论
const submitDeliverableComment = async (deliverableId) => {
  const commentText = deliverableCommentTexts.value.get(deliverableId)
  if (!commentText?.trim() || submittingDeliverableComments.value.has(deliverableId)) return

  try {
    submittingDeliverableComments.value.add(deliverableId)
    const projectId = route.params.id
    const response = await projectService.publishComment(
      projectId,
      { deliverable_id: deliverableId },
      { content: commentText.trim() }
    )

    if (response.status === 'success') {
      ElMessage.success('成果评论发表成功')
      deliverableCommentTexts.value.set(deliverableId, '')
      // 重新获取该成果的评论
      await fetchDeliverableComments(deliverableId)
    } else {
      ElMessage.error(response.message || '评论发表失败')
    }
  } catch (error) {
    console.error('提交成果评论失败:', error)
    ElMessage.error('评论发表失败')
  } finally {
    submittingDeliverableComments.value.delete(deliverableId)
  }
}

// 提交回复
const submitReply = async () => {
  if (!replyContent.value.trim() || !replyingTo.value || submittingReply.value) return

  try {
    submittingReply.value = true
    const projectId = route.params.id
    const params = { parent_comment_id: replyingTo.value }

    // 保存当前的回复上下文，因为后面要清空
    const currentReplyContext = replyContext.value

    // 如果是回复成果评论，需要传递 deliverable_id
    if (currentReplyContext && currentReplyContext.type === 'deliverable') {
      params.deliverable_id = currentReplyContext.deliverableId
    }

    const response = await projectService.publishComment(projectId, params, {
      content: replyContent.value.trim()
    })

    if (response.status === 'success') {
      ElMessage.success('回复发表成功')
      replyContent.value = ''
      const commentId = replyingTo.value
      replyingTo.value = null
      replyContext.value = null

      // 重新获取该评论的回复
      commentReplies.value.delete(commentId)
      repliesPagination.value.delete(commentId)
      if (expandedReplies.value.has(commentId)) {
        await toggleReplies(commentId)
        await toggleReplies(commentId)
      }

      // 根据保存的上下文决定刷新哪个评论列表
      if (currentReplyContext && currentReplyContext.type === 'deliverable') {
        // 如果是成果评论的回复，重新获取成果评论
        await fetchDeliverableComments(currentReplyContext.deliverableId)
      } else {
        // 如果是项目评论的回复，重新获取项目评论
        await fetchProjectComments()
      }
    } else {
      ElMessage.error(response.message || '回复发表失败')
    }
  } catch (error) {
    console.error('提交回复失败:', error)
    ElMessage.error('回复发表失败')
  } finally {
    submittingReply.value = false
  }
}

// 取消回复
const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
  replyContext.value = null
}

// 设置项目评论回复
const setProjectCommentReply = (commentId) => {
  replyingTo.value = commentId
  replyContext.value = { type: 'project' }
}

// 设置成果评论回复
const setDeliverableCommentReply = (commentId, deliverableId) => {
  replyingTo.value = commentId
  replyContext.value = { type: 'deliverable', deliverableId }
}

// 重新获取项目评论
const fetchProjectComments = async () => {
  try {
    commentsLoading.value = true
    const projectId = route.params.id
    const response = await projectService.getCommentList(projectId, { page: 1, page_size: 10 })

    if (response.status === 'success') {
      const commentsData = response.data
      projectComments.value = commentsData.comments || []

      // 重置分页信息
      projectCommentsPagination.value = {
        currentPage: 1,
        hasMore: (commentsData.comments || []).length === 10,
        loading: false
      }
    }
  } catch (error) {
    console.error('获取项目评论失败:', error)
  } finally {
    commentsLoading.value = false
  }
}

// 重新获取成果评论
const fetchDeliverableComments = async (deliverableId) => {
  try {
    const projectId = route.params.id
    const response = await projectService.getCommentList(projectId, {
      deliverable_id: deliverableId,
      page: 1,
      page_size: 10
    })

    if (response.status === 'success') {
      const commentsData = response.data
      deliverableComments.value.set(deliverableId, commentsData.comments || [])

      // 重置分页信息
      deliverableCommentsPagination.value.set(deliverableId, {
        currentPage: 1,
        hasMore: (commentsData.comments || []).length === 10,
        loading: false
      })
    }
  } catch (error) {
    console.error('获取成果评论失败:', error)
  }
}

onMounted(() => {
  fetchProjectData()
})
</script>

<template>
  <div class="project-detail">
    <!-- 自定义页面加载状态 -->
    <div v-if="loading" class="page-loading">
      <div class="loading-content">
        <font-awesome-icon :icon="faSpinner" class="loading-icon" />
        <p class="loading-text">正在加载项目信息...</p>
      </div>
    </div>

    <div v-else-if="projectData" class="project-content">
      <!-- 项目基本信息 -->
      <el-card class="project-info-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <font-awesome-icon :icon="faBriefcase" class="header-icon" />
            <span class="header-title">项目信息</span>
          </div>
        </template>

        <div class="project-info">
          <div class="project-title">
            <h1>{{ projectData.title }}</h1>
            <el-tag :type="projectStatus.type" size="large">
              {{ projectStatus.text }}
            </el-tag>
          </div>

          <div class="project-description">
            <p>{{ projectData.description }}</p>
          </div>

          <!-- 需求信息 -->
          <div class="requirement-info" v-if="projectData.requirement">
            <h3>关联需求</h3>
            <div class="requirement-card">
              <h4>{{ projectData.requirement.title }}</h4>
              <p>{{ projectData.requirement.description }}</p>
              <div class="requirement-meta">
                <span
                  >预算：{{
                    projectData.requirement.budget != null
                      ? `￥${projectData.requirement.budget}万`
                      : '未设置'
                  }}</span
                >
                <span
                  >人数：{{
                    projectData.requirement.people_count != null
                      ? `${projectData.requirement.people_count}人`
                      : '未设置'
                  }}</span
                >
                <span>发布机构：{{ projectData.requirement.organization_name }}</span>
              </div>
            </div>
          </div>

          <!-- 团队成员 -->
          <div class="team-section">
            <h3>
              <font-awesome-icon :icon="faUsers" class="section-icon" />
              团队成员
            </h3>
            <div class="team-members">
              <div
                v-for="participant in projectData.participants"
                :key="participant.id"
                class="member-card"
              >
                <el-avatar :src="participant.student.avatar" :size="40" class="member-avatar">
                  {{ participant.student.real_name.charAt(0) }}
                </el-avatar>
                <div class="member-info">
                  <div class="member-name">
                    {{ participant.student.real_name }}
                    <font-awesome-icon
                      v-if="participant.role === 'leader'"
                      :icon="faCrown"
                      class="leader-icon"
                    />
                  </div>
                  <div class="member-details">
                    <span>{{ participant.student.school.name }}</span>
                    <span>{{ participant.student.major }}</span>
                    <span>{{ participant.student.grade }}级</span>
                  </div>
                </div>
                <el-tag :type="participant.role === 'leader' ? 'warning' : 'primary'" size="small">
                  {{ participant.role === 'leader' ? '负责人' : '成员' }}
                </el-tag>
              </div>
            </div>
          </div>

          <div class="project-meta">
            <span>
              <font-awesome-icon :icon="faCalendarAlt" />
              创建时间：{{ formatDate(projectData.created_at) }}
            </span>
            <span>
              <font-awesome-icon :icon="faCalendarAlt" />
              更新时间：{{ formatDate(projectData.updated_at) }}
            </span>
          </div>
        </div>
      </el-card>

      <!-- 项目评分 -->
      <el-card class="score-card" shadow="hover" v-if="hasScorePermission">
        <template #header>
          <div class="card-header">
            <font-awesome-icon :icon="faStar" class="header-icon" />
            <span class="header-title">项目评分</span>
            <div class="score-status">
              <el-tag
                v-if="scoreStatus"
                :type="
                  scoreStatus.type === 'published'
                    ? 'success'
                    : scoreStatus.type === 'submitted'
                      ? 'primary'
                      : scoreStatus.type === 'draft'
                        ? 'warning'
                        : 'info'
                "
                size="large"
              >
                {{ scoreStatus.text }}
              </el-tag>
            </div>
          </div>
        </template>

        <div class="score-content">
          <!-- 无评分状态 -->
          <div v-if="scoreStatus?.type === 'none'" class="no-score">
            <div v-if="!projectData?.requirement?.evaluation_criteria_id">
              <p>暂无评分标准，请先创建评分标准</p>
            </div>
            <div v-else>
              <p>该项目尚未评分</p>
              <el-button type="primary" @click="showCreateScoreForm"> 创建项目评分 </el-button>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-else-if="scoreStatus?.type === 'loading'" class="loading-score">
            <div class="score-loading">
              <font-awesome-icon :icon="faSpinner" class="loading-icon" />
              <p>正在加载评分信息...</p>
            </div>
          </div>

          <!-- 草稿状态 -->
          <div v-else-if="scoreStatus?.type === 'draft'" class="draft-score">
            <div class="score-summary">
              <div class="score-info">
                <span class="total-score">总分：{{ scoreData?.weighted_score || 0 }}分</span>
                <span class="score-time">创建时间：{{ formatDate(scoreData?.created_at) }}</span>
              </div>
              <div class="score-actions">
                <el-button type="primary" @click="showUpdateScoreForm"> 修改评分 </el-button>
                <el-button type="success" @click="submitScore" :loading="scoreSubmitting">
                  {{ scoreSubmitting ? '提交中...' : '提交评分' }}
                </el-button>
              </div>
            </div>

            <!-- 评分预览 -->
            <div v-if="scoreData" class="score-preview">
              <h4>评分详情</h4>
              <div class="indicators-list">
                <div
                  v-for="indicator in scoreData.indicator_scores"
                  :key="indicator.id"
                  class="indicator-item"
                >
                  <div class="indicator-header">
                    <span class="indicator-name">{{ indicator.indicator_name }}</span>
                    <span class="indicator-score"
                      >{{ indicator.score }}/{{ indicator.indicator_max_score }}分</span
                    >
                    <span class="indicator-weight">权重：{{ indicator.indicator_weight }}%</span>
                  </div>
                  <div class="indicator-comment">{{ indicator.comment }}</div>
                </div>
              </div>
              <div v-if="scoreData.overall_comment" class="overall-comment">
                <h5>总体评语：</h5>
                <p>{{ scoreData.overall_comment }}</p>
              </div>
            </div>
          </div>

          <!-- 已提交状态（等待公示）-->
          <div v-else-if="scoreStatus?.type === 'submitted'" class="submitted-score">
            <div class="score-summary">
              <div class="score-info">
                <span class="total-score">总分：{{ scoreData?.weighted_score || 0 }}分</span>
                <span class="score-time">提交时间：{{ formatDate(scoreData?.updated_at) }}</span>
                <span class="evaluator">评分人：{{ scoreData?.evaluator?.real_name }}</span>
              </div>
            </div>

            <div class="status-description">
              <el-alert
                title="评分已提交"
                type="info"
                description="评分已完成提交，正在等待公示。公示后所有人都可以查看评分结果。"
                :closable="false"
                show-icon
              />
            </div>

            <!-- 提交状态的评分预览 -->
            <div v-if="scoreData" class="score-preview">
              <h4>评分详情</h4>
              <div class="indicators-list">
                <div
                  v-for="indicator in scoreData.indicator_scores"
                  :key="indicator.id"
                  class="indicator-item"
                >
                  <div class="indicator-header">
                    <span class="indicator-name">{{ indicator.indicator_name }}</span>
                    <span class="indicator-score"
                      >{{ indicator.score }}/{{ indicator.indicator_max_score }}分</span
                    >
                    <span class="indicator-weight">权重：{{ indicator.indicator_weight }}%</span>
                    <span class="weighted-score">得分：{{ indicator.weighted_score }}分</span>
                  </div>
                  <div class="indicator-comment">{{ indicator.comment }}</div>
                </div>
              </div>
              <div v-if="scoreData.overall_comment" class="overall-comment">
                <h5>总体评语：</h5>
                <p>{{ scoreData.overall_comment }}</p>
              </div>
            </div>
          </div>

          <!-- 已公示状态 -->
          <div v-else-if="scoreStatus?.type === 'published'" class="published-score">
            <div class="score-summary">
              <div class="score-info">
                <span class="total-score">总分：{{ scoreData?.weighted_score || 0 }}分</span>
                <span class="score-time">公示时间：{{ formatDate(scoreData?.updated_at) }}</span>
                <span class="evaluator">评分人：{{ scoreData?.evaluator?.real_name }}</span>
              </div>
            </div>

            <div class="status-description">
              <el-alert
                title="评分已公示"
                type="success"
                description="评分已正式公开发布，所有项目相关人员均可查看完整的评分结果。"
                :closable="false"
                show-icon
              />
            </div>

            <!-- 公示状态的最终评分结果 -->
            <div v-if="scoreData" class="final-score">
              <h4>最终评分结果</h4>
              <div class="indicators-list">
                <div
                  v-for="indicator in scoreData.indicator_scores"
                  :key="indicator.id"
                  class="indicator-item"
                >
                  <div class="indicator-header">
                    <span class="indicator-name">{{ indicator.indicator_name }}</span>
                    <span class="indicator-score"
                      >{{ indicator.score }}/{{ indicator.indicator_max_score }}分</span
                    >
                    <span class="indicator-weight">权重：{{ indicator.indicator_weight }}%</span>
                    <span class="weighted-score">得分：{{ indicator.weighted_score }}分</span>
                  </div>
                  <div class="indicator-comment">{{ indicator.comment }}</div>
                </div>
              </div>
              <div v-if="scoreData.overall_comment" class="overall-comment">
                <h5>总体评语：</h5>
                <p>{{ scoreData.overall_comment }}</p>
              </div>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 项目成果 -->
      <el-card class="deliverables-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <font-awesome-icon :icon="faFileAlt" class="header-icon" />
            <span class="header-title">项目成果</span>
          </div>
        </template>

        <el-timeline v-if="projectData.deliverables?.length">
          <el-timeline-item
            v-for="deliverable in projectData.deliverables"
            :key="deliverable.id"
            :color="stageMap[deliverable.stage_type]?.color"
            :size="deliverable.is_milestone ? 'large' : 'normal'"
            :type="deliverable.is_milestone ? 'primary' : 'success'"
          >
            <template #dot>
              <div class="timeline-dot" :class="{ milestone: deliverable.is_milestone }">
                <font-awesome-icon :icon="faFileAlt" />
              </div>
            </template>

            <div class="deliverable-item">
              <div class="deliverable-header" @click="toggleDeliverable(deliverable.id)">
                <div class="deliverable-title-section">
                  <font-awesome-icon
                    :icon="
                      expandedDeliverables.has(deliverable.id) ? faChevronDown : faChevronRight
                    "
                    class="expand-icon"
                  />
                  <h4>{{ deliverable.title }}</h4>
                </div>
                <div class="deliverable-badges">
                  <el-tag
                    :color="stageMap[deliverable.stage_type]?.color"
                    effect="light"
                    size="small"
                    class="white-text-tag"
                  >
                    {{ stageMap[deliverable.stage_type]?.text }}
                  </el-tag>
                  <span class="version-tag">{{ deliverable.stage_version.split('_')[1] }}</span>
                  <el-tag v-if="deliverable.is_milestone" type="warning" size="small">
                    里程碑
                  </el-tag>
                  <el-button type="text" size="small" class="comment-btn">
                    <font-awesome-icon :icon="faComment" />
                    评论成果
                  </el-button>
                </div>
              </div>

              <!-- 展开的成果内容 -->
              <div v-if="expandedDeliverables.has(deliverable.id)" class="deliverable-content">
                <div v-loading="deliverableLoading.has(deliverable.id)" class="deliverable-detail">
                  <!-- 成果描述 -->
                  <div
                    v-if="deliverableDetails.get(deliverable.id)?.description"
                    class="deliverable-description"
                  >
                    <h5>成果描述：</h5>
                    <p>{{ deliverableDetails.get(deliverable.id).description }}</p>
                  </div>

                  <!-- 进度描述 -->
                  <div
                    v-if="deliverableDetails.get(deliverable.id)?.progress_description"
                    class="progress-description"
                  >
                    <h5>进度说明：</h5>
                    <p>{{ deliverableDetails.get(deliverable.id).progress_description }}</p>
                  </div>

                  <!-- 备注信息 -->
                  <div
                    v-if="deliverableDetails.get(deliverable.id)?.notes"
                    class="deliverable-notes"
                  >
                    <h5>备注信息：</h5>
                    <p>{{ deliverableDetails.get(deliverable.id).notes }}</p>
                  </div>

                  <!-- 成果文件 -->
                  <div
                    v-if="deliverableDetails.get(deliverable.id)?.files?.length"
                    class="deliverable-files"
                  >
                    <h5>相关文件：</h5>
                    <div class="file-list">
                      <div
                        v-for="fileItem in deliverableDetails.get(deliverable.id).files"
                        :key="fileItem.id"
                        class="file-item"
                      >
                        <div class="file-info">
                          <font-awesome-icon
                            :icon="fileItem.is_cloud_link ? faExternalLinkAlt : faFileAlt"
                            class="file-icon"
                          />
                          <span class="file-name">{{ fileItem.name }}</span>
                          <span class="file-size">{{ formatFileSize(fileItem.file_size) }}</span>
                          <span
                            v-if="fileItem.is_cloud_link && fileItem.cloud_password"
                            class="cloud-password"
                          >
                            密码: {{ fileItem.cloud_password }}
                          </span>
                        </div>
                        <el-button type="primary" size="small" @click="downloadFile(fileItem)">
                          <font-awesome-icon :icon="faDownload" />
                          {{ fileItem.is_cloud_link ? '访问' : '下载' }}
                        </el-button>
                      </div>
                    </div>
                  </div>

                  <!-- 成果评论输入框 -->
                  <div class="deliverable-comment-input">
                    <h5>
                      <font-awesome-icon :icon="faComment" />
                      评论该成果
                    </h5>
                    <el-input
                      :model-value="deliverableCommentTexts.get(deliverable.id) || ''"
                      @update:model-value="
                        (val) => deliverableCommentTexts.set(deliverable.id, val)
                      "
                      type="textarea"
                      :rows="2"
                      placeholder="请输入成果评论内容..."
                      maxlength="500"
                      show-word-limit
                    />
                    <el-button
                      type="primary"
                      size="small"
                      @click="submitDeliverableComment(deliverable.id)"
                      :disabled="
                        !(deliverableCommentTexts.get(deliverable.id) || '').trim() ||
                        submittingDeliverableComments.has(deliverable.id)
                      "
                      :loading="submittingDeliverableComments.has(deliverable.id)"
                      style="margin-top: 8px"
                    >
                      {{
                        submittingDeliverableComments.has(deliverable.id) ? '发送中...' : '发表评论'
                      }}
                    </el-button>
                  </div>

                  <!-- 成果评论 -->
                  <div
                    v-if="deliverableComments.get(deliverable.id)?.length"
                    class="deliverable-comments"
                  >
                    <h5>
                      <font-awesome-icon :icon="faComment" />
                      成果评论 ({{ deliverableComments.get(deliverable.id).length }})
                    </h5>
                    <div class="comments-list">
                      <div
                        v-for="comment in deliverableComments.get(deliverable.id)"
                        :key="comment.id"
                        class="comment-item deliverable-comment-item"
                      >
                        <div class="comment-header">
                          <el-avatar :src="comment.author_info.avatar" :size="28">
                            {{ comment.author_info.real_name.charAt(0) }}
                          </el-avatar>
                          <div class="comment-meta">
                            <span class="author-name">{{ comment.author_info.real_name }}</span>
                            <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                          </div>
                          <!-- 删除按钮 - 成果评论 -->
                          <div class="comment-actions-header" v-if="canDeleteComment(comment)">
                            <el-button
                              type="text"
                              size="small"
                              class="delete-btn"
                              @click.stop="
                                deleteComment(comment.id, {
                                  type: 'deliverable',
                                  deliverableId: deliverable.id
                                })
                              "
                              :loading="deletingComments.has(comment.id)"
                            >
                              <font-awesome-icon :icon="faTrash" />
                            </el-button>
                          </div>
                        </div>

                        <div class="comment-content">
                          {{ comment.content }}
                        </div>

                        <div class="comment-actions">
                          <el-button
                            type="text"
                            size="small"
                            @click="setDeliverableCommentReply(comment.id, deliverable.id)"
                          >
                            <font-awesome-icon :icon="faReply" />
                            回复
                          </el-button>
                          <el-button
                            v-if="comment.reply_count > 0"
                            type="text"
                            size="small"
                            @click="toggleReplies(comment.id)"
                            :loading="replyLoading.has(comment.id)"
                          >
                            <font-awesome-icon :icon="faComment" />
                            {{ expandedReplies.has(comment.id) ? '收起' : '查看' }}回复 ({{
                              comment.reply_count
                            }})
                          </el-button>
                        </div>

                        <!-- 回复框 -->
                        <div v-if="replyingTo === comment.id" class="reply-form">
                          <el-input
                            v-model="replyContent"
                            type="textarea"
                            :rows="2"
                            placeholder="请输入回复内容..."
                            maxlength="300"
                            show-word-limit
                          />
                          <div class="reply-actions">
                            <el-button size="small" @click="cancelReply">取消</el-button>
                            <el-button
                              type="primary"
                              size="small"
                              @click="submitReply"
                              :disabled="!replyContent.trim() || submittingReply"
                              :loading="submittingReply"
                            >
                              {{ submittingReply ? '发送中...' : '回复' }}
                            </el-button>
                          </div>
                        </div>

                        <!-- 回复列表 -->
                        <div
                          v-if="
                            expandedReplies.has(comment.id) &&
                            commentReplies.get(comment.id)?.length
                          "
                          class="replies-list"
                        >
                          <div
                            v-for="reply in commentReplies.get(comment.id)"
                            :key="reply.id"
                            class="reply-item"
                          >
                            <div class="reply-header">
                              <el-avatar :src="reply.author_info.avatar" :size="20">
                                {{ reply.author_info.real_name.charAt(0) }}
                              </el-avatar>
                              <div class="reply-meta">
                                <span class="author-name">{{ reply.author_info.real_name }}</span>
                                <span class="reply-time">{{ formatDate(reply.created_at) }}</span>
                              </div>
                              <!-- 删除按钮 - 成果评论回复 -->
                              <div class="reply-actions-header" v-if="canDeleteComment(reply)">
                                <el-button
                                  type="text"
                                  size="small"
                                  class="delete-btn"
                                  @click.stop="
                                    deleteComment(reply.id, {
                                      type: 'reply',
                                      isDeliverableReply: true,
                                      deliverableId: deliverable.id,
                                      parentCommentId: comment.id
                                    })
                                  "
                                  :loading="deletingComments.has(reply.id)"
                                >
                                  <font-awesome-icon :icon="faTrash" />
                                </el-button>
                              </div>
                            </div>
                            <div class="reply-content">
                              {{ reply.content }}
                            </div>
                          </div>

                          <!-- 加载更多回复按钮 -->
                          <div
                            v-if="repliesPagination.get(comment.id)?.hasMore"
                            class="load-more-section"
                          >
                            <el-button
                              type="text"
                              size="small"
                              @click="loadMoreReplies(comment.id)"
                              :loading="repliesPagination.get(comment.id)?.loading"
                              class="load-more-btn"
                            >
                              <font-awesome-icon
                                :icon="
                                  repliesPagination.get(comment.id)?.loading
                                    ? faSpinner
                                    : faChevronDown
                                "
                              />
                              {{
                                repliesPagination.get(comment.id)?.loading
                                  ? '加载中...'
                                  : '查看更多回复'
                              }}
                            </el-button>
                          </div>
                        </div>
                      </div>
                    </div>

                    <!-- 加载更多成果评论按钮 -->
                    <div
                      v-if="deliverableCommentsPagination.get(deliverable.id)?.hasMore"
                      class="load-more-section"
                    >
                      <el-button
                        type="text"
                        @click="loadMoreDeliverableComments(deliverable.id)"
                        :loading="deliverableCommentsPagination.get(deliverable.id)?.loading"
                        class="load-more-btn"
                      >
                        <font-awesome-icon
                          :icon="
                            deliverableCommentsPagination.get(deliverable.id)?.loading
                              ? faSpinner
                              : faChevronDown
                          "
                        />
                        {{
                          deliverableCommentsPagination.get(deliverable.id)?.loading
                            ? '加载中...'
                            : '加载更多评论'
                        }}
                      </el-button>
                    </div>
                  </div>

                  <!-- 成果元数据 -->
                  <div v-if="deliverableDetails.get(deliverable.id)" class="deliverable-meta">
                    <span>提交时间：{{ formatDate(deliverable.created_at) }}</span>
                    <span v-if="deliverable.updated_at !== deliverable.created_at">
                      更新时间：{{ formatDate(deliverable.updated_at) }}
                    </span>
                    <span v-if="deliverableDetails.get(deliverable.id).submitter">
                      提交人：{{ deliverableDetails.get(deliverable.id).submitter.real_name }}
                    </span>
                    <span v-if="deliverableDetails.get(deliverable.id).last_modifier">
                      最后修改：{{ deliverableDetails.get(deliverable.id).last_modifier.real_name }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </el-timeline-item>
        </el-timeline>

        <div v-else class="no-deliverables">
          <p>暂无项目成果</p>
        </div>
      </el-card>

      <!-- 评论区 -->
      <el-card class="comments-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <font-awesome-icon :icon="faComment" class="header-icon" />
            <span class="header-title">项目讨论</span>
          </div>
        </template>

        <!-- 发表项目评论 -->
        <div class="new-comment-section">
          <h4>发表项目评论</h4>
          <el-input
            v-model="newComment"
            type="textarea"
            :rows="3"
            placeholder="请输入项目评论内容..."
            maxlength="500"
            show-word-limit
          />
          <el-button
            type="primary"
            @click="submitProjectComment"
            :disabled="!newComment.trim() || submittingProjectComment"
            :loading="submittingProjectComment"
            style="margin-top: 10px"
          >
            {{ submittingProjectComment ? '发送中...' : '发表评论' }}
          </el-button>
        </div>

        <el-divider />

        <!-- 项目评论列表 -->
        <div class="comment-section" v-loading="commentsLoading">
          <h4>项目评论</h4>
          <div v-if="projectComments.length" class="comments-list">
            <div
              v-for="comment in projectComments"
              :key="comment.id"
              class="comment-item project-comment-item"
            >
              <div class="comment-header">
                <el-avatar :src="comment.author_info.avatar" :size="32">
                  {{ comment.author_info.real_name.charAt(0) }}
                </el-avatar>
                <div class="comment-meta">
                  <span class="author-name">{{ comment.author_info.real_name }}</span>
                  <span class="comment-time">{{ formatDate(comment.created_at) }}</span>
                </div>
                <!-- 删除按钮 - 项目评论 -->
                <div class="comment-actions-header" v-if="canDeleteComment(comment)">
                  <el-button
                    type="text"
                    size="small"
                    class="delete-btn"
                    @click.stop="deleteComment(comment.id, { type: 'project' })"
                    :loading="deletingComments.has(comment.id)"
                  >
                    <font-awesome-icon :icon="faTrash" />
                  </el-button>
                </div>
              </div>

              <div class="comment-content">
                {{ comment.content }}
              </div>

              <div class="comment-actions">
                <el-button type="text" size="small" @click="setProjectCommentReply(comment.id)">
                  <font-awesome-icon :icon="faReply" />
                  回复
                </el-button>
                <el-button
                  v-if="comment.reply_count > 0"
                  type="text"
                  size="small"
                  @click="toggleReplies(comment.id)"
                  :loading="replyLoading.has(comment.id)"
                >
                  <font-awesome-icon :icon="faComment" />
                  {{ expandedReplies.has(comment.id) ? '收起' : '查看' }}回复 ({{
                    comment.reply_count
                  }})
                </el-button>
              </div>

              <!-- 回复框 -->
              <div v-if="replyingTo === comment.id" class="reply-form">
                <el-input
                  v-model="replyContent"
                  type="textarea"
                  :rows="2"
                  placeholder="请输入回复内容..."
                  maxlength="300"
                  show-word-limit
                />
                <div class="reply-actions">
                  <el-button size="small" @click="cancelReply">取消</el-button>
                  <el-button
                    type="primary"
                    size="small"
                    @click="submitReply"
                    :disabled="!replyContent.trim() || submittingReply"
                    :loading="submittingReply"
                  >
                    {{ submittingReply ? '发送中...' : '回复' }}
                  </el-button>
                </div>
              </div>

              <!-- 回复列表 -->
              <div
                v-if="expandedReplies.has(comment.id) && commentReplies.get(comment.id)?.length"
                class="replies-list"
              >
                <div
                  v-for="reply in commentReplies.get(comment.id)"
                  :key="reply.id"
                  class="reply-item"
                >
                  <div class="reply-header">
                    <el-avatar :src="reply.author_info.avatar" :size="24">
                      {{ reply.author_info.real_name.charAt(0) }}
                    </el-avatar>
                    <div class="reply-meta">
                      <span class="author-name">{{ reply.author_info.real_name }}</span>
                      <span class="reply-time">{{ formatDate(reply.created_at) }}</span>
                    </div>
                    <!-- 删除按钮 - 项目评论回复 -->
                    <div class="reply-actions-header" v-if="canDeleteComment(reply)">
                      <el-button
                        type="text"
                        size="small"
                        class="delete-btn"
                        @click.stop="
                          deleteComment(reply.id, {
                            type: 'reply',
                            isDeliverableReply: false,
                            parentCommentId: comment.id
                          })
                        "
                        :loading="deletingComments.has(reply.id)"
                      >
                        <font-awesome-icon :icon="faTrash" />
                      </el-button>
                    </div>
                  </div>
                  <div class="reply-content">
                    {{ reply.content }}
                  </div>
                </div>

                <!-- 加载更多回复按钮 -->
                <div v-if="repliesPagination.get(comment.id)?.hasMore" class="load-more-section">
                  <el-button
                    type="text"
                    size="small"
                    @click="loadMoreReplies(comment.id)"
                    :loading="repliesPagination.get(comment.id)?.loading"
                    class="load-more-btn"
                  >
                    <font-awesome-icon
                      :icon="repliesPagination.get(comment.id)?.loading ? faSpinner : faChevronDown"
                    />
                    {{ repliesPagination.get(comment.id)?.loading ? '加载中...' : '查看更多回复' }}
                  </el-button>
                </div>
              </div>
            </div>
          </div>

          <!-- 加载更多项目评论按钮 -->
          <div
            v-if="projectCommentsPagination.hasMore && projectComments.length"
            class="load-more-section"
          >
            <el-button
              type="text"
              @click="loadMoreProjectComments"
              :loading="projectCommentsPagination.loading"
              class="load-more-btn"
            >
              <font-awesome-icon
                :icon="projectCommentsPagination.loading ? faSpinner : faChevronDown"
              />
              {{ projectCommentsPagination.loading ? '加载中...' : '加载更多评论' }}
            </el-button>
          </div>

          <div v-if="!projectComments.length" class="no-comments">
            <p>暂无项目评论</p>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 评分表单弹窗 -->
    <el-dialog
      v-model="scoreFormVisible"
      :title="scoreMode === 'create' ? '创建项目评分' : '修改项目评分'"
      width="70%"
      :close-on-click-modal="false"
      :close-on-press-escape="false"
      class="score-form-dialog"
    >
      <div v-if="scoreStandard" class="score-form" v-loading="scoreLoading">
        <div class="score-standard-info">
          <h4>评分标准：{{ scoreStandard.name }}</h4>
          <p>{{ scoreStandard.description }}</p>
        </div>

        <el-form :model="scoreFormData" label-width="120px" class="score-form-content">
          <!-- 评分指标 -->
          <div class="indicators-section">
            <h4>评分指标</h4>
            <div
              v-for="indicator in scoreStandard.indicators"
              :key="indicator.id"
              class="indicator-form-item"
            >
              <div class="indicator-info">
                <div class="indicator-header">
                  <span class="indicator-name">
                    {{ indicator.name }}
                    <el-tag v-if="indicator.is_required" type="danger" size="small">必填</el-tag>
                  </span>
                  <span class="indicator-weight">权重：{{ indicator.weight }}%</span>
                  <span class="indicator-max-score">满分：{{ indicator.max_score }}分</span>
                </div>
                <div class="indicator-description">{{ indicator.description }}</div>
              </div>

              <el-form-item :label="`评分：`" :required="indicator.is_required">
                <el-input-number
                  :model-value="getIndicatorScore(indicator.id)?.score || 0"
                  @update:model-value="(val) => updateIndicatorScore(indicator.id, 'score', val)"
                  :min="0"
                  :max="indicator.max_score"
                  :precision="0"
                  :step="1"
                  size="large"
                />
                <span class="score-suffix">/ {{ indicator.max_score }}分</span>
              </el-form-item>

              <el-form-item :label="`评语：`">
                <el-input
                  :model-value="getIndicatorScore(indicator.id)?.comment || ''"
                  @update:model-value="(val) => updateIndicatorScore(indicator.id, 'comment', val)"
                  type="textarea"
                  :rows="2"
                  :placeholder="`请输入${indicator.name}的评语`"
                  maxlength="300"
                  show-word-limit
                />
              </el-form-item>
            </div>
          </div>

          <!-- 总体评语 -->
          <el-form-item label="总体评语：" class="overall-comment-item">
            <el-input
              v-model="scoreFormData.overall_comment"
              type="textarea"
              :rows="3"
              placeholder="请输入项目的总体评语..."
              maxlength="500"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="closeScoreForm" :disabled="scoreSubmitting">取消</el-button>
          <el-button
            type="primary"
            @click="submitScoreForm"
            :loading="scoreSubmitting"
            :disabled="scoreSubmitting"
          >
            {{ scoreSubmitting ? '提交中...' : scoreMode === 'create' ? '创建评分' : '保存修改' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.project-detail {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

// 自定义页面加载状态
.page-loading {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 60vh;

  .loading-content {
    text-align: center;

    .loading-icon {
      font-size: 32px;
      color: #409eff;
      animation: spin 1s linear infinite;
      margin-bottom: 16px;
    }

    .loading-text {
      font-size: 16px;
      color: #606266;
      margin: 0;
    }
  }
}

.project-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  justify-content: space-between;

  .header-icon {
    color: #409eff;
    font-size: 18px;
  }

  .header-title {
    font-size: 18px;
    font-weight: 600;
    color: #303133;
  }

  .score-status {
    margin-left: auto;
  }
}

// 项目评分卡片样式
.score-card {
  .score-content {
    .no-score {
      text-align: center;
      padding: 40px 20px;

      p {
        color: #909399;
        margin-bottom: 20px;
        font-size: 16px;
      }
    }

    .loading-score {
      .score-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        padding: 40px 20px;

        .loading-icon {
          font-size: 24px;
          color: #409eff;
          animation: spin 1s linear infinite;
          margin-bottom: 16px;
        }

        p {
          color: #909399;
          margin: 0;
          font-size: 16px;
        }
      }
    }

    .score-summary {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 20px;
      padding: 16px;
      background: #f8f9fa;
      border-radius: 8px;

      .score-info {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .total-score {
          font-size: 24px;
          font-weight: bold;
          color: #409eff;
        }

        .score-time,
        .evaluator {
          font-size: 14px;
          color: #909399;
        }
      }

      .score-actions {
        display: flex;
        gap: 12px;
      }
    }

    .status-description {
      margin-bottom: 20px;
    }

    .score-preview,
    .final-score {
      h4 {
        margin: 0 0 16px 0;
        color: #303133;
      }

      .indicators-list {
        .indicator-item {
          border: 1px solid #ebeef5;
          border-radius: 8px;
          padding: 16px;
          margin-bottom: 12px;
          background: #fff;

          .indicator-header {
            display: flex;
            align-items: center;
            gap: 16px;
            margin-bottom: 8px;
            flex-wrap: wrap;

            .indicator-name {
              font-weight: 600;
              color: #303133;
              flex: 1;
            }

            .indicator-score {
              font-size: 18px;
              font-weight: bold;
              color: #409eff;
            }

            .indicator-weight {
              font-size: 14px;
              color: #909399;
            }

            .weighted-score {
              font-size: 14px;
              color: #67c23a;
              font-weight: 600;
            }
          }

          .indicator-comment {
            color: #606266;
            line-height: 1.6;
            padding-left: 8px;
            border-left: 3px solid #f0f2f5;
          }
        }
      }

      .overall-comment {
        margin-top: 20px;
        padding: 16px;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 4px solid #409eff;

        h5 {
          margin: 0 0 8px 0;
          color: #303133;
        }

        p {
          margin: 0;
          color: #606266;
          line-height: 1.6;
        }
      }
    }
  }
}

// 评分表单弹窗样式
:deep(.score-form-dialog) {
  .el-dialog__body {
    padding: 20px 24px;
  }
}

.score-form {
  .score-standard-info {
    margin-bottom: 20px;
    padding: 16px;
    background: #ecf5ff;
    border-radius: 8px;
    border-left: 4px solid #409eff;

    h4 {
      margin: 0 0 8px 0;
      color: #303133;
    }

    p {
      margin: 0;
      color: #606266;
      line-height: 1.5;
    }
  }

  .indicators-section {
    h4 {
      margin: 0 0 16px 0;
      color: #303133;
    }

    .indicator-form-item {
      border: 1px solid #ebeef5;
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 20px;
      background: #fff;

      .indicator-info {
        margin-bottom: 16px;

        .indicator-header {
          display: flex;
          align-items: center;
          gap: 16px;
          margin-bottom: 8px;
          flex-wrap: wrap;

          .indicator-name {
            font-weight: 600;
            color: #303133;
            font-size: 16px;
            flex: 1;
          }

          .indicator-weight,
          .indicator-max-score {
            font-size: 14px;
            color: #909399;
            white-space: nowrap;
          }
        }

        .indicator-description {
          color: #606266;
          line-height: 1.6;
          padding: 8px 12px;
          background: #f8f9fa;
          border-radius: 4px;
        }
      }

      .el-form-item {
        margin-bottom: 16px;

        .score-suffix {
          margin-left: 8px;
          color: #909399;
          font-size: 14px;
        }
      }
    }
  }

  .overall-comment-item {
    margin-top: 24px;
    padding-top: 20px;
    border-top: 1px solid #ebeef5;
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// 删除按钮样式
.delete-btn {
  color: #f56c6c;
  padding: 4px 6px;
  min-width: auto;

  &:hover {
    background-color: #fef0f0;
    color: #f56c6c;
  }

  &.is-loading {
    color: #c0c4cc;
  }
}

.comment-actions-header,
.reply-actions-header {
  margin-left: auto;
  display: flex;
  align-items: center;
}

.comment-header,
.reply-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;

  .comment-meta,
  .reply-meta {
    flex: 1;

    .author-name {
      font-weight: 600;
      color: #303133;
      margin-right: 12px;
    }

    .comment-time,
    .reply-time {
      font-size: 12px;
      color: #909399;
    }
  }
}

// 加载更多按钮样式
.load-more-section {
  display: flex;
  justify-content: center;
  padding: 16px 0;
  border-top: 1px solid #f0f2f5;
  margin-top: 12px;

  .load-more-btn {
    color: #409eff;
    font-size: 14px;
    padding: 8px 16px;
    border-radius: 20px;
    transition: all 0.3s;

    &:hover {
      background-color: #ecf5ff;
      transform: translateY(-1px);
    }

    &:active {
      transform: translateY(0);
    }

    svg {
      margin-right: 6px;
    }

    &.is-loading svg {
      animation: spin 1s linear infinite;
    }
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 项目信息样式
.project-info {
  .project-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;

    h1 {
      margin: 0;
      font-size: 28px;
      color: #303133;
    }
  }

  .project-description {
    margin-bottom: 24px;

    p {
      font-size: 16px;
      line-height: 1.6;
      color: #606266;
      margin: 0;
    }
  }

  .requirement-info {
    margin-bottom: 24px;

    h3 {
      margin: 0 0 12px 0;
      color: #303133;
    }

    .requirement-card {
      background: #f8f9fa;
      padding: 16px;
      border-radius: 8px;
      border-left: 4px solid #409eff;

      h4 {
        margin: 0 0 8px 0;
        color: #303133;
      }

      p {
        margin: 0 0 12px 0;
        color: #606266;
        line-height: 1.5;
      }

      .requirement-meta {
        display: flex;
        gap: 20px;
        font-size: 14px;
        color: #909399;

        span {
          display: flex;
          align-items: center;
        }
      }
    }
  }

  .team-section {
    margin-bottom: 24px;

    h3 {
      display: flex;
      align-items: center;
      margin: 0 0 16px 0;
      color: #303133;

      .section-icon {
        margin-right: 8px;
        color: #409eff;
      }
    }

    .team-members {
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
      gap: 16px;

      .member-card {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        border: 1px solid #ebeef5;
        border-radius: 8px;
        background: #fff;
        transition: all 0.3s;

        &:hover {
          box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
        }

        .member-avatar {
          flex-shrink: 0;
        }

        .member-info {
          flex: 1;

          .member-name {
            display: flex;
            align-items: center;
            font-weight: 600;
            color: #303133;
            margin-bottom: 4px;

            .leader-icon {
              margin-left: 6px;
              color: #e6a23c;
            }
          }

          .member-details {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            font-size: 12px;
            color: #909399;

            span {
              background: #f0f2f5;
              padding: 2px 6px;
              border-radius: 4px;
            }
          }
        }
      }
    }
  }

  .project-meta {
    display: flex;
    gap: 24px;
    padding-top: 16px;
    border-top: 1px solid #ebeef5;
    font-size: 14px;
    color: #909399;

    span {
      display: flex;
      align-items: center;
      gap: 6px;
    }
  }
}

// 成果样式
.deliverables-card {
  .el-timeline {
    @media (max-width: 768px) {
      padding-left: 0px;
    }
  }

  .timeline-dot {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 16px;
    height: 16px;
    border-radius: 50%;

    &.milestone {
      width: 20px;
      height: 20px;
      font-size: 12px;
    }
  }

  .deliverable-item {
    .deliverable-header {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      margin-bottom: 12px;
      cursor: pointer;
      user-select: none;

      &:hover {
        background-color: #f5f7fa;
        border-radius: 4px;
        padding: 4px;
        margin: -4px;
      }

      .deliverable-title-section {
        display: flex;
        align-items: center;
        gap: 8px;
        flex: 1;

        .expand-icon {
          color: #909399;
          font-size: 12px;
          transition: transform 0.2s;
        }

        h4 {
          margin: 0;
          color: #303133;
          font-size: 18px;
        }
      }

      .deliverable-badges {
        display: flex;
        align-items: center;
        gap: 8px;
        flex-wrap: wrap;

        .white-text-tag {
          color: #fff;
        }

        .version-tag {
          font-size: 12px;
          color: #909399;
          background: #f0f2f5;
          padding: 2px 8px;
          border-radius: 12px;
        }

        .comment-btn {
          color: #409eff;
          padding: 4px 8px;

          &:hover {
            background-color: #ecf5ff;
          }
        }
      }
    }

    .deliverable-content {
      margin-left: 20px;
      padding-left: 16px;
      border-left: 2px solid #f0f2f5;

      @media (max-width: 768px) {
        margin-left: 0px;
        padding-left: 10px;
      }

      .deliverable-description,
      .progress-description,
      .deliverable-notes {
        margin: 12px 0;

        h5 {
          margin: 0 0 6px 0;
          color: #303133;
          font-size: 14px;
        }

        p {
          margin: 0;
          color: #606266;
          line-height: 1.5;
          font-size: 14px;
        }
      }

      .deliverable-comment-input {
        margin: 16px 0;
        padding: 12px;
        background: #f8f9fa;
        border-radius: 8px;
        border-left: 3px solid #409eff;

        h5 {
          margin: 0 0 8px 0;
          color: #303133;
          font-size: 14px;
          display: flex;
          align-items: center;
          gap: 6px;
        }
      }
    }

    .deliverable-files {
      margin: 16px 0;

      h5 {
        margin: 0 0 8px 0;
        color: #303133;
      }

      .file-list {
        display: flex;
        flex-direction: column;
        gap: 8px;

        .file-item {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 8px 12px;
          background: #f8f9fa;
          border-radius: 6px;

          .file-info {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            gap: 8px;
            flex: 1;

            .file-icon {
              color: #409eff;
            }

            .file-name {
              font-weight: 500;
              color: #303133;
            }

            .file-size {
              font-size: 12px;
              color: #909399;
            }

            .cloud-password {
              font-size: 12px;
              color: #e6a23c;
              background: #fdf6ec;
              padding: 2px 6px;
              border-radius: 4px;
            }
          }
        }
      }
    }

    .deliverable-comments {
      margin-top: 16px;
      padding-top: 12px;
      border-top: 1px solid #f0f2f5;

      h5 {
        margin: 0 0 12px 0;
        color: #303133;
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 14px;
      }

      .deliverable-comment-item {
        background: #f8f9fa;
        border-radius: 6px;
        padding: 12px;
        margin-bottom: 8px;

        .comment-header {
          display: flex;
          gap: 8px;

          .author-name {
            font-weight: 600;
            color: #303133;
            margin-right: 8px;
          }

          .comment-time {
            font-size: 12px;
            color: #909399;
          }
        }

        .comment-content {
          margin: 6px 0 8px 36px;
          font-size: 14px;
        }

        .comment-actions {
          margin-left: 36px;
        }

        .reply-form {
          margin: 8px 0 0 36px;
        }

        .replies-list {
          margin-left: 24px;
          margin-top: 16px;

          .reply-item {
            padding: 8px;
            background: #f8f9fa;
            border-radius: 8px;

            .reply-header {
              display: flex;
              align-items: center;
              gap: 8px;
              margin-bottom: 6px;

              .reply-meta {
                .author-name {
                  font-weight: 500;
                  color: #303133;
                  margin-right: 8px;
                  font-size: 14px;
                }

                .reply-time {
                  font-size: 11px;
                  color: #909399;
                }
              }
            }

            .reply-content {
              margin-left: 32px;
              font-size: 14px;
              line-height: 1.5;
              color: #606266;
            }
          }
        }
      }
    }

    .deliverable-meta {
      display: flex;
      gap: 16px;
      margin-top: 12px;
      font-size: 12px;
      color: #909399;
      padding-top: 8px;
      border-top: 1px solid #f0f2f5;
    }
  }

  .no-deliverables {
    text-align: center;
    color: #909399;
    padding: 40px 0;
  }
}

// 评论样式
.comments-card {
  .new-comment-section,
  .new-deliverable-comment-section {
    margin-bottom: 20px;

    h4 {
      margin: 0 0 12px 0;
      color: #303133;
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }

  .new-deliverable-comment-section {
    background: #ecf5ff;
    padding: 16px;
    border-radius: 8px;
    border-left: 4px solid #409eff;
  }

  .comment-section {
    h4 {
      margin: 0 0 16px 0;
      color: #303133;
    }
  }

  .comments-list {
    .comment-item {
      margin-bottom: 24px;
      padding-bottom: 16px;
      border-bottom: 1px solid #f0f2f5;

      &:last-child {
        border-bottom: none;
        margin-bottom: 0;
      }

      &.project-comment-item {
        border-left: 3px solid #409eff;
        padding-left: 16px;
      }

      .comment-header {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;

        .comment-meta {
          .author-name {
            font-weight: 600;
            color: #303133;
            margin-right: 12px;
          }

          .comment-time {
            font-size: 12px;
            color: #909399;
          }
        }
      }

      .comment-content {
        margin: 8px 0 12px 44px;
        line-height: 1.6;
        color: #606266;
      }

      .comment-actions {
        margin-left: 44px;
        display: flex;
        gap: 8px;
      }

      .reply-form {
        margin: 12px 0 16px 44px;

        .reply-actions {
          display: flex;
          justify-content: flex-end;
          gap: 8px;
          margin-top: 8px;
        }
      }

      .replies-list {
        margin-left: 44px;
        margin-top: 16px;

        .reply-item {
          margin-bottom: 16px;
          padding: 12px;
          background: #f8f9fa;
          border-radius: 8px;

          .reply-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 6px;

            .reply-meta {
              .author-name {
                font-weight: 500;
                color: #303133;
                margin-right: 8px;
                font-size: 14px;
              }

              .reply-time {
                font-size: 11px;
                color: #909399;
              }
            }
          }

          .reply-content {
            margin-left: 32px;
            font-size: 14px;
            line-height: 1.5;
            color: #606266;
          }
        }
      }
    }
  }

  .no-comments {
    text-align: center;
    color: #909399;
    padding: 20px 0;
  }
}

@media (max-width: 768px) {
  .project-detail {
    padding: 12px;
  }

  .project-info .team-members {
    grid-template-columns: 1fr;
  }

  .project-info .project-title {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .deliverable-item .deliverable-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .load-more-section {
    padding: 12px 0;
  }

  .score-summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
  }

  .indicator-header {
    flex-direction: column;
    align-items: flex-start !important;
    gap: 8px !important;
  }

  :deep(.score-form-dialog) {
    width: 95% !important;
  }
}
</style>
