<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ArrowDown } from '@element-plus/icons-vue'
import { projectScoreService } from '@/api/'
import { useUserStore } from '@/stores' // 导入用户store

// 定义 props 和 emits
const props = defineProps({
  standardId: {
    type: [Number, String],
    default: null
  },
  editable: {
    type: Boolean,
    default: true,
    description: '是否允许修改评分标准'
  }
})

const emit = defineEmits(['update:standardId', 'standardChanged'])

// 获取用户store
const userStore = useUserStore()

// 基础状态
const loading = ref(false)
const currentView = ref('empty') // empty, detail, create, list, edit
const currentStandardId = ref(props.standardId)

// 评分标准详情
const standardDetail = ref({})

// 标准列表相关
const standardList = ref([])
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_count: 0,
  page_size: 10
})
const searchKeyword = ref('')
const listFilter = reactive({
  is_template: null,
  status: 'active',
  is_used_by_requirements: null // 新增：使用状态筛选
})

// 创建表单
// === 替换 BEGIN：createForm 仅保留项目名与项目描述 ===
const createForm = reactive({
  name: '',
  description: '' // 新增：项目描述（项目介绍）
})
// === 替换 END ===

// 编辑表单
const editForm = reactive({
  name: '',
  description: '',
  indicators: [],
  new_indicators: []
})
const indicatorsToDelete = ref([])

// 新增：折叠展开控制
const expandedIndicatorIndex = ref(0) // 默认展开第一个

// 新增：弹窗控制
const showAddIndicatorDialog = ref(false)
const indicatorDialogForm = reactive({
  name: '',
  description: '',
  weight: 0,
  max_score: 100,
  isEditing: false,
  editIndex: -1
})

// 新增：复制标准弹窗控制
const showCopyDialog = ref(false)
const copyDialogForm = reactive({
  name: '',
  description: '',
  sourceStandard: null
})

// 新增：删除确认弹窗控制
const showDeleteDialog = ref(false)
const deleteTarget = ref(null)

// 计算属性：检查用户是否有删除权限
const canDeleteStandard = (standard) => {
  const user = userStore.user
  if (!user) return false

  // 检查是否是创建者
  const isCreator = user.id === standard.creator_id

  // 检查是否是管理员或所有者
  const hasAdminPermission =
    user.company_profile?.permission === 'admin' || user.company_profile?.permission === 'owner'

  return isCreator || hasAdminPermission
}

// 方法定义

// 加载评分标准详情
const loadStandardDetail = async (id) => {
  loading.value = true
  try {
    // 调用真实接口
    const result = await projectScoreService.getScoreStandardDetail(id)
    standardDetail.value = result.data
  } catch (error) {
    console.error('加载评分标准详情失败:', error)
  } finally {
    loading.value = false
  }
}

// 加载评分标准列表
const loadStandardList = async (page = 1) => {
  loading.value = true
  try {
    const params = {
      page: page,
      page_size: pagination.value.page_size,
      search: searchKeyword.value,
      ...listFilter
    }

    // 调用真实接口
    const result = await projectScoreService.getScoreStandardList(params)
    standardList.value = result.data.results
    pagination.value = result.data.pagination
  } catch (error) {
    console.error('加载评分标准列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 显示删除确认弹窗
const showDeleteConfirmDialog = (standard) => {
  deleteTarget.value = standard
  showDeleteDialog.value = true
}

// 确认删除标准
const confirmDeleteStandard = async () => {
  if (!deleteTarget.value) return

  loading.value = true
  try {
    await projectScoreService.deleteScoreStandard(deleteTarget.value.id)

    // 删除成功后重新加载列表
    await loadStandardList(pagination.value.current_page)

    showDeleteDialog.value = false
    deleteTarget.value = null

    console.log('评分标准删除成功')

    // 如果删除的是当前选中的标准，清空选择
    if (currentStandardId.value === deleteTarget.value.id) {
      currentStandardId.value = null
      emit('update:standardId', null)
      emit('standardChanged', null)
      currentView.value = 'empty'
    }
  } catch (error) {
    console.error('删除评分标准失败:', error)
  } finally {
    loading.value = false
  }
}

// 取消删除
const cancelDeleteStandard = () => {
  showDeleteDialog.value = false
  deleteTarget.value = null
}

// 检查权重总和是否为100
const checkWeightSum = (indicators) => {
  const totalWeight = indicators.reduce((sum, indicator) => {
    return sum + (Number(indicator.weight) || 0)
  }, 0)
  return totalWeight
}

// 计算属性
const isCreateFormValid = computed(() => {
  return (
    createForm.name &&
    createForm.indicators.length > 0 &&
    createForm.indicators.every((ind) => ind.name && ind.weight >= 0 && ind.max_score > 0)
  )
})

const createFormWeightSum = computed(() => {
  return checkWeightSum(createForm.indicators)
})

const editFormWeightSum = computed(() => {
  const allIndicators = [...editForm.indicators, ...editForm.new_indicators]
  return checkWeightSum(allIndicators)
})

// 监听standardId变化
watch(
  () => props.standardId,
  (newId) => {
    currentStandardId.value = newId
    if (newId) {
      currentView.value = 'detail'
      loadStandardDetail(newId)
    } else {
      currentView.value = 'empty'
    }
  },
  { immediate: true }
)

// 监听搜索关键词变化
watch(
  searchKeyword,
  (newKeyword) => {
    if (currentView.value === 'list') {
      loadStandardList()
    }
  },
  { debounce: 500 }
)

// 监听筛选条件变化
watch(listFilter, () => {
  if (currentView.value === 'list') {
    loadStandardList()
  }
})

// 其他方法定义

// 显示创建表单
const showCreateForm = () => {
  currentView.value = 'create'
  resetCreateForm()
}

// 显示标准列表
const showStandardList = () => {
  currentView.value = 'list'
  loadStandardList()
}

// 重置创建表单
const resetCreateForm = () => {
  createForm.name = ''
  createForm.description = ''
  createForm.is_template = false
  createForm.indicators = []
  addIndicator() // 默认添加一个指标
}

// 添加指标 - 创建模式
const addIndicator = () => {
  createForm.indicators.push({
    name: '',
    description: '',
    weight: 0,
    max_score: 100,
    order: createForm.indicators.length + 1,
    is_required: true
  })
}

// 新增：显示添加指标弹窗
const showAddIndicatorModal = () => {
  resetIndicatorDialog()
  indicatorDialogForm.isEditing = false
  showAddIndicatorDialog.value = true
}

// 新增：重置弹窗表单
const resetIndicatorDialog = () => {
  indicatorDialogForm.name = ''
  indicatorDialogForm.description = ''
  indicatorDialogForm.weight = 0
  indicatorDialogForm.max_score = 100
  indicatorDialogForm.isEditing = false
  indicatorDialogForm.editIndex = -1
}

// 新增：确认添加指标
const confirmAddIndicator = () => {
  if (!indicatorDialogForm.name) {
    alert('请输入指标名称')
    return
  }

  const newIndicator = {
    name: indicatorDialogForm.name,
    description: indicatorDialogForm.description,
    weight: indicatorDialogForm.weight,
    max_score: indicatorDialogForm.max_score,
    order: editForm.indicators.length + editForm.new_indicators.length + 1,
    is_required: true
  }

  if (indicatorDialogForm.isEditing) {
    // 编辑模式
    if (indicatorDialogForm.editIndex >= 0) {
      editForm.new_indicators[indicatorDialogForm.editIndex] = newIndicator
    }
  } else {
    // 新增模式
    editForm.new_indicators.push(newIndicator)
  }

  showAddIndicatorDialog.value = false
  resetIndicatorDialog()
}

// 新增：取消添加指标
const cancelAddIndicator = () => {
  showAddIndicatorDialog.value = false
  resetIndicatorDialog()
}

// 新增：展开/折叠指标编辑
const toggleIndicatorExpand = (index) => {
  expandedIndicatorIndex.value = expandedIndicatorIndex.value === index ? -1 : index
}

// 拖拽相关变量
const draggedIndex = ref(null)
const dragOverIndex = ref(null)

// 拖拽开始
const handleDragStart = (event, index) => {
  draggedIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
  event.target.classList.add('dragging')
}

// 拖拽结束
const handleDragEnd = (event) => {
  event.target.classList.remove('dragging')
  draggedIndex.value = null
  dragOverIndex.value = null
}

// 拖拽进入
const handleDragEnter = (event, index) => {
  event.preventDefault()
  if (draggedIndex.value !== null && draggedIndex.value !== index) {
    dragOverIndex.value = index
  }
}

// 拖拽经过
const handleDragOver = (event) => {
  event.preventDefault()
  event.dataTransfer.dropEffect = 'move'
}

// 拖拽离开
const handleDragLeave = (event) => {
  // 只有当真正离开元素时才清除 dragOverIndex
  if (!event.currentTarget.contains(event.relatedTarget)) {
    dragOverIndex.value = null
  }
}

// 拖拽放置 - 创建表单
const handleDropCreate = (event, dropIndex) => {
  event.preventDefault()
  const dragIndex = draggedIndex.value

  if (dragIndex !== null && dragIndex !== dropIndex) {
    const draggedItem = createForm.indicators[dragIndex]
    createForm.indicators.splice(dragIndex, 1)
    createForm.indicators.splice(dropIndex, 0, draggedItem)

    // 重新计算order
    createForm.indicators.forEach((indicator, index) => {
      indicator.order = index + 1
    })
  }

  draggedIndex.value = null
  dragOverIndex.value = null
}

// 拖拽放置 - 编辑表单（现有指标）
const handleDropEdit = (event, dropIndex) => {
  event.preventDefault()
  const dragIndex = draggedIndex.value

  if (dragIndex !== null && dragIndex !== dropIndex) {
    const draggedItem = editForm.indicators[dragIndex]
    editForm.indicators.splice(dragIndex, 1)
    editForm.indicators.splice(dropIndex, 0, draggedItem)

    // 重新计算order
    editForm.indicators.forEach((indicator, index) => {
      indicator.order = index + 1
    })
  }

  draggedIndex.value = null
  dragOverIndex.value = null
}

// 拖拽放置 - 编辑表单（新增指标）
const handleDropEditNew = (event, dropIndex) => {
  event.preventDefault()
  const dragIndex = draggedIndex.value

  if (dragIndex !== null && dragIndex !== dropIndex) {
    const draggedItem = editForm.new_indicators[dragIndex]
    editForm.new_indicators.splice(dragIndex, 1)
    editForm.new_indicators.splice(dropIndex, 0, draggedItem)

    // 重新计算order
    editForm.new_indicators.forEach((indicator, index) => {
      indicator.order = editForm.indicators.length + index + 1
    })
  }

  draggedIndex.value = null
  dragOverIndex.value = null
}

// 移除指标
const removeIndicator = (index) => {
  createForm.indicators.splice(index, 1)
  // 重新设置order
  createForm.indicators.forEach((indicator, idx) => {
    indicator.order = idx + 1
  })
}

// 创建标准
const createStandard = async () => {
  // 检查权重总和
  const weightSum = createFormWeightSum.value
  if (weightSum !== 100) {
    alert(`权重总和必须等于100%，当前总和为${weightSum}%，请调整各指标权重。`)
    return
  }

  loading.value = true
  try {
    // 确保指标的数值字段为数字类型
    const processedIndicators = createForm.indicators.map((indicator) => ({
      ...indicator,
      weight: Number(indicator.weight) || 0,
      max_score: Number(indicator.max_score) || 100,
      order: Number(indicator.order) || 1
    }))

    const formData = {
      ...createForm,
      indicators: processedIndicators
    }

    // 调用真实接口
    const result = await projectScoreService.createScoreStandard(formData)

    const newId = result.data.id
    currentStandardId.value = newId
    emit('update:standardId', newId)
    emit('standardChanged', result.data)

    currentView.value = 'detail'
    await loadStandardDetail(newId)

    console.log('评分标准创建成功')
  } catch (error) {
    console.error('创建评分标准失败:', error)
  } finally {
    loading.value = false
  }
}

// 取消创建
const cancelCreate = () => {
  if (currentStandardId.value) {
    currentView.value = 'detail'
  } else {
    currentView.value = 'empty'
  }
}

// 新增：显示复制标准弹窗
const showCopyStandardDialog = (standard) => {
  copyDialogForm.sourceStandard = standard
  copyDialogForm.name = `基于 ${standard.name} 的副本`
  copyDialogForm.description = standard.description || `基于模板创建的新标准`
  showCopyDialog.value = true
}

// 新增：确认复制标准
const confirmCopyStandard = async () => {
  if (!copyDialogForm.name) {
    alert('请输入标准名称')
    return
  }

  loading.value = true
  try {
    const copyData = {
      source_criteria_id: copyDialogForm.sourceStandard.id,
      name: copyDialogForm.name,
      description: copyDialogForm.description
    }

    // 调用真实接口
    const result = await projectScoreService.copyScoreStandard(copyData)

    const newId = result.data.id
    currentStandardId.value = newId
    emit('update:standardId', newId)
    emit('standardChanged', result.data)

    currentView.value = 'detail'
    await loadStandardDetail(newId)

    showCopyDialog.value = false
    console.log('评分标准复制成功')
  } catch (error) {
    console.error('复制评分标准失败:', error)
  } finally {
    loading.value = false
  }
}

// 新增：取消复制标准
const cancelCopyStandard = () => {
  showCopyDialog.value = false
  copyDialogForm.sourceStandard = null
  copyDialogForm.name = ''
  copyDialogForm.description = ''
}

// 修改：选择标准 - 根据使用状态决定直接选择还是复制
const selectStandard = async (standard) => {
  // 如果标准已被使用，显示复制弹窗
  if (standard.is_used_by_requirements) {
    showCopyStandardDialog(standard)
    return
  }

  // 如果标准未被使用，直接选择
  loading.value = true
  try {
    currentStandardId.value = standard.id
    emit('update:standardId', standard.id)
    emit('standardChanged', standard)

    currentView.value = 'detail'
    await loadStandardDetail(standard.id)

    console.log('评分标准选择成功')
  } catch (error) {
    console.error('选择评分标准失败:', error)
  } finally {
    loading.value = false
  }
}

// 取消选择
const cancelSelect = () => {
  if (currentStandardId.value) {
    currentView.value = 'detail'
  } else {
    currentView.value = 'empty'
  }
}

// 分页
const changePage = (page) => {
  if (page >= 1 && page <= pagination.value.total_pages) {
    pagination.value.current_page = page
    loadStandardList(page)
  }
}

// 编辑标准
const editStandard = () => {
  currentView.value = 'edit'
  // 初始化编辑表单
  editForm.name = standardDetail.value.name
  editForm.description = standardDetail.value.description
  editForm.indicators = JSON.parse(JSON.stringify(standardDetail.value.indicators || []))
  editForm.new_indicators = []
  indicatorsToDelete.value = []
  // 重置展开状态，默认展开第一个
  expandedIndicatorIndex.value = 0
}

// 添加新指标（编辑模式） - 改为使用弹窗
const addEditIndicator = () => {
  showAddIndicatorModal()
}

// 编辑新指标
const editNewIndicator = (index) => {
  const indicator = editForm.new_indicators[index]
  indicatorDialogForm.name = indicator.name
  indicatorDialogForm.description = indicator.description
  indicatorDialogForm.weight = indicator.weight
  indicatorDialogForm.max_score = indicator.max_score
  indicatorDialogForm.isEditing = true
  indicatorDialogForm.editIndex = index
  showAddIndicatorDialog.value = true
}

// 移除新指标
const removeNewIndicator = (index) => {
  editForm.new_indicators.splice(index, 1)
}

// 标记指标为删除
const markIndicatorForDeletion = (indicatorId, index) => {
  indicatorsToDelete.value.push(indicatorId)
  editForm.indicators.splice(index, 1)
  // 如果删除的是当前展开的指标，重置展开状态
  if (expandedIndicatorIndex.value === index) {
    expandedIndicatorIndex.value = 0
  } else if (expandedIndicatorIndex.value > index) {
    expandedIndicatorIndex.value--
  }
}

// 修改：更新标准 - 调用真实接口
const updateStandard = async () => {
  // 检查权重总和
  const weightSum = editFormWeightSum.value
  if (weightSum !== 100) {
    alert(`权重总和必须等于100%，当前总和为${weightSum}%，请调整各指标权重。`)
    return
  }

  loading.value = true
  try {
    // 如果有要删除的指标，先删除
    if (indicatorsToDelete.value.length > 0) {
      const deleteData = {
        indicator_ids: indicatorsToDelete.value.join(',')
      }
      await projectScoreService.batchDeleteScoreIndicator(currentStandardId.value, deleteData)
      console.log('批量删除指标成功')
    }

    // 确保现有指标的数值字段为数字类型
    const processedIndicators = editForm.indicators.map((indicator) => ({
      ...indicator,
      weight: Number(indicator.weight) || 0,
      max_score: Number(indicator.max_score) || 100,
      order: Number(indicator.order) || 1
    }))

    // 确保新增指标的数值字段为数字类型
    const processedNewIndicators = editForm.new_indicators.map((indicator) => ({
      ...indicator,
      weight: Number(indicator.weight) || 0,
      max_score: Number(indicator.max_score) || 100,
      order: Number(indicator.order) || 1
    }))

    // 更新标准
    const updateData = {
      name: editForm.name,
      description: editForm.description,
      indicators: processedIndicators,
      new_indicators: processedNewIndicators
    }

    const result = await projectScoreService.updateScoreStandard(
      currentStandardId.value,
      updateData
    )

    // 重新加载详情
    await loadStandardDetail(currentStandardId.value)
    currentView.value = 'detail'

    emit('standardChanged', standardDetail.value)

    console.log('评分标准更新成功')
  } catch (error) {
    console.error('更新评分标准失败:', error)
  } finally {
    loading.value = false
  }
}

// 取消编辑
const cancelEdit = () => {
  currentView.value = 'detail'
}

// 组件挂载时的初始化
onMounted(() => {
  if (currentStandardId.value) {
    currentView.value = 'detail'
    loadStandardDetail(currentStandardId.value)
  }
})
</script>

<template>
  <div class="score-standard-manager">
    <!-- 无评分标准状态 -->
    <div v-if="!currentStandardId && currentView === 'empty'" class="empty-state">
      <div class="empty-content">
        <h3>暂无评分标准</h3>
        <p>
          {{ props.editable ? '请选择创建新的评分标准或从已有标准中选择' : '暂未设置评分标准' }}
        </p>
        <div class="action-buttons" v-if="props.editable">
          <button @click="showCreateForm" class="btn btn-primary">
            <i class="icon-plus"></i> 创建新标准
          </button>
          <button @click="showStandardList" class="btn btn-secondary">
            <i class="icon-list"></i> 选择已有标准
          </button>
        </div>
      </div>
    </div>

    <!-- 评分标准详情显示 -->
    <div v-if="currentStandardId && currentView === 'detail'" class="standard-detail">
      <div class="standard-header">
        <div class="standard-info">
          <h3>{{ standardDetail.name }}</h3>
          <p class="description">{{ standardDetail.description }}</p>
          <div class="meta-info">
            <span class="tag" :class="{ 'tag-template': standardDetail.is_template }">
              {{ standardDetail.is_template ? '模板' : '自定义' }}
            </span>
            <span class="total-weight">总权重: {{ standardDetail.total_weight }}%</span>
            <span v-if="standardDetail.is_used_by_requirements" class="tag tag-used">
              已被使用
            </span>
          </div>
        </div>
        <div class="action-buttons" v-if="props.editable">
          <button @click="editStandard" class="btn btn-primary">
            <i class="icon-edit"></i> 修改
          </button>
          <button @click="showStandardList" class="btn btn-secondary">
            <i class="icon-change"></i> 更换
          </button>
        </div>
      </div>

      <div class="indicators-list">
        <h4>评分指标</h4>
        <div
          class="indicator-item"
          v-for="indicator in standardDetail.indicators"
          :key="indicator.id"
        >
          <div class="indicator-header">
            <span class="indicator-name">{{ indicator.name }}</span>
            <div class="indicator-meta">
              <span class="weight">权重: {{ indicator.weight }}%</span>
              <span class="max-score">满分: {{ indicator.max_score }}</span>
              <span v-if="indicator.is_required" class="required">必填</span>
            </div>
          </div>
          <p class="indicator-description">{{ indicator.description }}</p>
        </div>
      </div>
    </div>

    <!-- 创建新标准表单 -->
    <div v-if="currentView === 'create'" class="create-form">
      <div class="form-header">
        <h3>创建评分标准</h3>
        <button @click="cancelCreate" class="btn btn-text"><i class="icon-close"></i> 取消</button>
      </div>

      <form @submit.prevent="createStandard">
        <div class="form-group">
          <label>标准名称 <span class="required">*</span></label>
          <input v-model="createForm.name" type="text" placeholder="请输入标准名称" required />
        </div>

        <div class="form-group">
          <label>标准描述</label>
          <textarea
            v-model="createForm.description"
            placeholder="请输入标准描述"
            rows="3"
          ></textarea>
        </div>

        <div class="form-group">
          <label>
            <input type="checkbox" v-model="createForm.is_template" />
            作为模板标准
          </label>
        </div>

        <div class="indicators-section">
          <div class="section-header">
            <h4>评分指标</h4>
            <button type="button" @click="addIndicator" class="btn btn-secondary btn-small">
              <i class="icon-plus"></i> 添加指标
            </button>
          </div>

          <div class="weight-summary">
            <span
              class="weight-info"
              :class="{
                'weight-valid': createFormWeightSum === 100,
                'weight-invalid': createFormWeightSum !== 100
              }"
            >
              权重总和: {{ createFormWeightSum }}%
              <span v-if="createFormWeightSum === 100" class="weight-status valid">✓</span>
              <span v-else class="weight-status invalid">{{
                createFormWeightSum < 100 ? '不足' : '超出'
              }}</span>
            </span>
          </div>

          <div class="drag-tip"><i class="icon-info"></i> 提示：可以通过拖拽来调整指标的排序</div>

          <div
            class="indicator-form"
            v-for="(indicator, index) in createForm.indicators"
            :key="index"
            :class="{
              dragging: draggedIndex === index,
              'drag-over': dragOverIndex === index,
              'drag-active': draggedIndex !== null
            }"
            draggable="true"
            @dragstart="handleDragStart($event, index)"
            @dragend="handleDragEnd"
            @dragenter="handleDragEnter($event, index)"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
            @drop="handleDropCreate($event, index)"
          >
            <div class="indicator-form-header">
              <div class="drag-handle">
                <i class="icon-drag"></i>
                <span>指标 {{ index + 1 }}</span>
                <span v-if="draggedIndex !== null && dragOverIndex !== null" class="preview-order">
                  {{
                    draggedIndex === index
                      ? '移动中'
                      : dragOverIndex === index
                        ? `→ 第${draggedIndex < index ? index : index + 1}位`
                        : ''
                  }}
                </span>
              </div>
              <button type="button" @click="removeIndicator(index)" class="btn btn-text btn-small">
                <i class="icon-delete"></i>
              </button>
            </div>

            <div class="form-row">
              <div class="form-group">
                <label>指标名称 <span class="required">*</span></label>
                <input v-model="indicator.name" type="text" required />
              </div>
              <div class="form-group">
                <label>权重 <span class="required">*</span></label>
                <input v-model.number="indicator.weight" type="number" min="0" max="100" required />
              </div>
              <div class="form-group">
                <label>满分 <span class="required">*</span></label>
                <input v-model.number="indicator.max_score" type="number" min="1" required />
              </div>
            </div>

            <div class="form-group">
              <label>指标描述</label>
              <textarea v-model="indicator.description" rows="2"></textarea>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" @click="cancelCreate" class="btn btn-secondary">取消</button>
          <button type="submit" class="btn btn-primary" :disabled="!isCreateFormValid">
            创建标准
          </button>
        </div>
      </form>
    </div>

    <!-- 标准列表选择 -->
    <div v-if="currentView === 'list'" class="standard-list">
      <div class="list-header">
        <h3>选择评分标准</h3>
        <div class="list-actions">
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索标准..."
            class="search-input"
          />
          <button @click="cancelSelect" class="btn btn-text">
            <i class="icon-close"></i> 取消
          </button>
        </div>
      </div>

      <div class="list-filters">
        <div class="filter-group">
          <label class="filter-title">标准类型：</label>
          <label>
            <input type="radio" v-model="listFilter.is_template" :value="null" />
            全部
          </label>
          <label>
            <input type="radio" v-model="listFilter.is_template" :value="true" />
            仅模板
          </label>
          <label>
            <input type="radio" v-model="listFilter.is_template" :value="false" />
            非模板
          </label>
        </div>

        <div class="filter-group">
          <label class="filter-title">使用状态：</label>
          <label>
            <input type="radio" v-model="listFilter.is_used_by_requirements" :value="null" />
            全部
          </label>
          <label>
            <input type="radio" v-model="listFilter.is_used_by_requirements" :value="false" />
            未使用
          </label>
          <label>
            <input type="radio" v-model="listFilter.is_used_by_requirements" :value="true" />
            已使用
          </label>
        </div>
      </div>

      <div class="standard-items" v-if="standardList.length > 0">
        <div
          class="standard-item"
          v-for="standard in standardList"
          :key="standard.id"
          :class="{ disabled: !props.editable }"
        >
          <div
            class="standard-item-content"
            @click="props.editable ? selectStandard(standard) : null"
          >
            <div class="item-header">
              <h5>{{ standard.name }}</h5>
              <div class="item-meta">
                <span class="tag" :class="{ 'tag-template': standard.is_template }">
                  {{ standard.is_template ? '模板' : '自定义' }}
                </span>
                <span v-if="standard.is_used_by_requirements" class="tag tag-used"> 已被使用 </span>
                <span class="indicator-count">{{ standard.indicator_count }} 项指标</span>
              </div>
            </div>
            <p class="item-description">{{ standard.description }}</p>
            <div class="item-info">
              <span>权重总计: {{ standard.total_weight }}%</span>
              <span>克隆次数: {{ standard.clone_count }}</span>
            </div>
            <div v-if="standard.is_used_by_requirements" class="usage-tip">
              <i class="icon-info"></i> 此标准已被其他需求使用，选择后将创建副本
            </div>
          </div>

          <!-- 删除按钮 -->
          <div
            v-if="props.editable && canDeleteStandard(standard)"
            class="item-actions"
            @click.stop
          >
            <button
              @click="showDeleteConfirmDialog(standard)"
              class="btn btn-danger btn-small"
              title="删除标准"
            >
              <i class="icon-delete"></i> 删除
            </button>
          </div>
        </div>
      </div>

      <div v-else class="no-data">
        <p>暂无匹配的评分标准</p>
      </div>

      <div class="pagination" v-if="pagination.total_pages > 1">
        <button
          @click="changePage(pagination.current_page - 1)"
          :disabled="pagination.current_page <= 1"
          class="btn btn-secondary btn-small"
        >
          上一页
        </button>
        <span>第 {{ pagination.current_page }} / {{ pagination.total_pages }} 页</span>
        <button
          @click="changePage(pagination.current_page + 1)"
          :disabled="pagination.current_page >= pagination.total_pages"
          class="btn btn-secondary btn-small"
        >
          下一页
        </button>
      </div>
    </div>

    <!-- 修改标准表单 -->
    <div v-if="currentView === 'edit'" class="edit-form">
      <div class="form-header">
        <h3>修改评分标准</h3>
        <button @click="cancelEdit" class="btn btn-text"><i class="icon-close"></i> 取消</button>
      </div>

      <form @submit.prevent="updateStandard">
        <div class="form-group">
          <label>标准名称 <span class="required">*</span></label>
          <input v-model="editForm.name" type="text" required />
        </div>

        <div class="form-group">
          <label>标准描述</label>
          <textarea v-model="editForm.description" rows="3"></textarea>
        </div>

        <div class="indicators-section">
          <div class="section-header">
            <h4>评分指标</h4>
            <button type="button" @click="addEditIndicator" class="btn btn-secondary btn-small">
              <i class="icon-plus"></i> 添加指标
            </button>
          </div>

          <div class="weight-summary">
            <span
              class="weight-info"
              :class="{
                'weight-valid': editFormWeightSum === 100,
                'weight-invalid': editFormWeightSum !== 100
              }"
            >
              权重总和: {{ editFormWeightSum }}%
              <span v-if="editFormWeightSum === 100" class="weight-status valid">✓</span>
              <span v-else class="weight-status invalid">{{
                editFormWeightSum < 100 ? '不足' : '超出'
              }}</span>
            </span>
          </div>

          <div class="drag-tip">
            <i class="icon-info"></i> 提示：可以通过拖拽来调整指标的排序，点击指标可展开编辑
          </div>

          <!-- 现有指标 - 折叠/展开模式 -->
          <div
            class="indicator-form compact"
            v-for="(indicator, index) in editForm.indicators"
            :key="'existing-' + indicator.id"
            :class="{
              expanded: expandedIndicatorIndex === index,
              dragging: draggedIndex === index,
              'drag-over': dragOverIndex === index,
              'drag-active': draggedIndex !== null
            }"
            draggable="true"
            @dragstart="handleDragStart($event, index)"
            @dragend="handleDragEnd"
            @dragenter="handleDragEnter($event, index)"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
            @drop="handleDropEdit($event, index)"
          >
            <div class="indicator-form-header" @click="toggleIndicatorExpand(index)">
              <div class="drag-handle">
                <i class="icon-drag"></i>
                <span>{{ indicator.name || `指标 ${index + 1}` }}</span>
                <span class="indicator-summary"
                  >权重: {{ indicator.weight }}% | 满分: {{ indicator.max_score }}</span
                >
                <el-icon
                  class="expand-icon"
                  :class="{ expanded: expandedIndicatorIndex === index }"
                >
                  <ArrowDown />
                </el-icon>
              </div>
              <button
                type="button"
                @click.stop="markIndicatorForDeletion(indicator.id, index)"
                class="btn btn-danger btn-small"
              >
                <i class="icon-delete"></i> 删除
              </button>
            </div>

            <!-- 展开的编辑内容 -->
            <div v-show="expandedIndicatorIndex === index" class="indicator-edit-content">
              <div class="form-row">
                <div class="form-group">
                  <label>指标名称 <span class="required">*</span></label>
                  <input v-model="indicator.name" type="text" required />
                </div>
                <div class="form-group">
                  <label>权重 <span class="required">*</span></label>
                  <input
                    v-model.number="indicator.weight"
                    type="number"
                    min="0"
                    max="100"
                    required
                  />
                </div>
                <div class="form-group">
                  <label>满分 <span class="required">*</span></label>
                  <input v-model.number="indicator.max_score" type="number" min="1" required />
                </div>
              </div>

              <div class="form-group">
                <label>指标描述</label>
                <textarea v-model="indicator.description" rows="2"></textarea>
              </div>
            </div>
          </div>

          <!-- 新增指标 - 卡片显示 -->
          <div class="new-indicators-section" v-if="editForm.new_indicators.length > 0">
            <h5>新增指标</h5>
            <div
              class="indicator-card"
              v-for="(indicator, index) in editForm.new_indicators"
              :key="'new-' + index"
            >
              <div class="indicator-card-header">
                <span class="indicator-name">{{ indicator.name || '未命名指标' }}</span>
                <div class="indicator-actions">
                  <button
                    type="button"
                    @click="editNewIndicator(index)"
                    class="btn btn-text btn-small"
                  >
                    <i class="icon-edit"></i> 编辑
                  </button>
                  <button
                    type="button"
                    @click="removeNewIndicator(index)"
                    class="btn btn-text btn-small"
                  >
                    <i class="icon-delete"></i> 删除
                  </button>
                </div>
              </div>
              <div class="indicator-card-content">
                <p class="indicator-description">{{ indicator.description || '暂无描述' }}</p>
                <div class="indicator-meta">
                  <span>权重: {{ indicator.weight }}%</span>
                  <span>满分: {{ indicator.max_score }}</span>
                  <span v-if="indicator.is_required" class="required">必填</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="form-actions">
          <button type="button" @click="cancelEdit" class="btn btn-secondary">取消</button>
          <button type="submit" class="btn btn-primary">保存修改</button>
        </div>
      </form>
    </div>

    <!-- 添加指标弹窗 -->
    <div v-if="showAddIndicatorDialog" class="dialog-overlay" @click="cancelAddIndicator">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h4>{{ indicatorDialogForm.isEditing ? '编辑指标' : '添加指标' }}</h4>
          <button @click="cancelAddIndicator" class="btn btn-text btn-small">
            <i class="icon-close"></i>
          </button>
        </div>

        <div class="dialog-body">
          <div class="form-group">
            <label>指标名称 <span class="required">*</span></label>
            <input
              v-model="indicatorDialogForm.name"
              type="text"
              placeholder="请输入指标名称"
              required
            />
          </div>

          <div class="form-row">
            <div class="form-group">
              <label>权重 <span class="required">*</span></label>
              <input
                v-model.number="indicatorDialogForm.weight"
                type="number"
                min="0"
                max="100"
                required
              />
            </div>
            <div class="form-group">
              <label>满分 <span class="required">*</span></label>
              <input
                v-model.number="indicatorDialogForm.max_score"
                type="number"
                min="1"
                required
              />
            </div>
          </div>

          <div class="form-group">
            <label>指标描述</label>
            <textarea
              v-model="indicatorDialogForm.description"
              placeholder="请输入指标描述"
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="cancelAddIndicator" class="btn btn-secondary">取消</button>
          <button @click="confirmAddIndicator" class="btn btn-primary">确定</button>
        </div>
      </div>
    </div>

    <!-- 复制标准弹窗 -->
    <div v-if="showCopyDialog" class="dialog-overlay" @click="cancelCopyStandard">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h4>复制评分标准</h4>
          <button @click="cancelCopyStandard" class="btn btn-text btn-small">
            <i class="icon-close"></i>
          </button>
        </div>

        <div class="dialog-body">
          <div class="source-info">
            <p><strong>源标准：</strong>{{ copyDialogForm.sourceStandard?.name }}</p>
            <p class="tips"><i class="icon-info"></i> 该标准已被其他需求使用，将为您创建一个副本</p>
          </div>

          <div class="form-group">
            <label>副本名称 <span class="required">*</span></label>
            <input
              v-model="copyDialogForm.name"
              type="text"
              placeholder="请输入新标准名称"
              required
            />
          </div>

          <div class="form-group">
            <label>副本描述</label>
            <textarea
              v-model="copyDialogForm.description"
              placeholder="请输入新标准描述"
              rows="3"
            ></textarea>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="cancelCopyStandard" class="btn btn-secondary">取消</button>
          <button @click="confirmCopyStandard" class="btn btn-primary">确认复制</button>
        </div>
      </div>
    </div>

    <!-- 删除确认弹窗 -->
    <div v-if="showDeleteDialog" class="dialog-overlay" @click="cancelDeleteStandard">
      <div class="dialog-content danger" @click.stop>
        <div class="dialog-header">
          <h4>删除评分标准</h4>
          <button @click="cancelDeleteStandard" class="btn btn-text btn-small">
            <i class="icon-close"></i>
          </button>
        </div>

        <div class="dialog-body">
          <div class="warning-info">
            <i class="icon-warning"></i>
            <div>
              <p><strong>确认要删除以下评分标准吗？</strong></p>
              <p class="delete-target">{{ deleteTarget?.name }}</p>
              <p class="warning-text">此操作不可恢复，请谨慎操作。</p>
            </div>
          </div>
        </div>

        <div class="dialog-footer">
          <button @click="cancelDeleteStandard" class="btn btn-secondary">取消</button>
          <button @click="confirmDeleteStandard" class="btn btn-danger">确认删除</button>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <p>加载中...</p>
    </div>
  </div>
</template>

<style lang="scss" scoped>
// 导入 color 模块
@use 'sass:color';

// SCSS 变量
$primary-color: #007bff;
$secondary-color: #6c757d;
$danger-color: #dc3545;
$success-color: #28a745;
$warning-color: #ffc107;
$light-bg: #f8f9fa;
$border-color: #e0e0e0;
$text-color: #333;
$text-muted: #666;
$text-light: #999;
$border-radius: 8px;
$border-radius-sm: 4px;
$spacing-xs: 5px;
$spacing-sm: 10px;
$spacing-md: 15px;
$spacing-lg: 20px;
$spacing-xl: 40px;

// 动画
@keyframes fadeInScale {
  from {
    opacity: 0;
    transform: scale(0.8);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

@keyframes slideDown {
  from {
    opacity: 0;
    max-height: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    max-height: 500px;
    transform: translateY(0);
  }
}

.score-standard-manager {
  min-height: 400px;
  // 移除外层内边距，让组件融入外层卡片
  padding: 0;

  // 空状态样式
  .empty-state {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 300px;

    .empty-content {
      text-align: center;

      h3 {
        margin-bottom: $spacing-sm;
        color: $text-muted;
      }

      p {
        margin-bottom: $spacing-lg;
        color: $text-light;
      }
    }
  }

  // 标准详情样式
  .standard-detail {
    // 移除边框，融入外层卡片
    border: none;
    border-radius: 0;
    overflow: visible;

    .standard-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: $spacing-lg;
      background-color: $light-bg;
      // 移除底部边框，用内边距分隔
      border-bottom: none;
      margin-bottom: $spacing-lg;
      border-radius: $border-radius;

      .standard-info {
        h3 {
          margin: 0 0 8px 0;
          color: $text-color;
        }

        .description {
          margin: 0 0 $spacing-sm 0;
          color: $text-muted;
          line-height: 1.5;
        }

        .meta-info {
          display: flex;
          gap: $spacing-md;
          align-items: center;

          .tag {
            padding: 4px 8px;
            border-radius: $border-radius-sm;
            font-size: 12px;
            background-color: #e9ecef;
            color: #495057;

            &.tag-template {
              background-color: #d4edda;
              color: #155724;
            }

            &.tag-used {
              background-color: #fff3cd;
              color: #856404;
            }
          }

          .total-weight {
            font-size: 14px;
            font-weight: 500;
            color: $primary-color;
          }
        }
      }
    }

    .indicators-list {
      padding: $spacing-lg;

      h4 {
        margin: 0 0 $spacing-md 0;
        color: $text-color;
      }

      .indicator-item {
        margin-bottom: $spacing-md;
        padding: $spacing-md;
        border: 1px solid $border-color;
        border-radius: 6px;
        background-color: #fff;

        .indicator-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          .indicator-name {
            font-weight: 500;
            color: $text-color;
          }

          .indicator-meta {
            display: flex;
            gap: $spacing-sm;
            font-size: 12px;
            color: $text-muted;

            .required {
              color: $danger-color;
              font-weight: 500;
            }
          }
        }

        .indicator-description {
          margin: 0;
          color: $text-muted;
          line-height: 1.4;
        }
      }
    }
  }

  // 表单样式
  .create-form,
  .edit-form {
    // 移除边框，融入外层卡片
    border: none;
    border-radius: 0;
    overflow: visible;

    .form-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-md 0 $spacing-lg 0;
      background-color: transparent;
      // 移除底部边框，用内边距分隔
      border-bottom: none;
      margin-bottom: $spacing-lg;

      h3 {
        margin: 0;
        color: $text-color;
      }
    }

    form {
      padding: 0;

      .form-group {
        margin-bottom: $spacing-md;

        label {
          display: block;
          margin-bottom: $spacing-xs;
          font-weight: 500;
          color: $text-color;
        }

        input,
        textarea {
          width: 100%;
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: $border-radius-sm;
          font-size: 14px;

          &:focus {
            outline: none;
            border-color: $primary-color;
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
          }
        }
      }

      .form-row {
        display: grid;
        grid-template-columns: 2fr 1fr 1fr;
        gap: $spacing-md;
      }

      .indicators-section {
        margin-top: $spacing-lg;
        padding-top: $spacing-lg;
        border-top: 1px solid $border-color;

        .section-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: $spacing-md;

          h4 {
            margin: 0;
            color: $text-color;
          }
        }

        .drag-tip {
          display: flex;
          align-items: center;
          gap: $spacing-xs;
          margin-bottom: $spacing-md;
          padding: 8px 12px;
          background-color: #e3f2fd;
          border: 1px solid #bbdefb;
          border-radius: $border-radius-sm;
          font-size: 12px;
          color: #1976d2;

          i {
            font-size: 14px;
          }
        }

        .weight-summary {
          margin-bottom: $spacing-md;
          padding: $spacing-sm $spacing-md;
          background-color: #f8f9fa;
          border: 1px solid $border-color;
          border-radius: $border-radius-sm;
          text-align: center;

          .weight-info {
            font-weight: 500;
            font-size: 14px;

            &.weight-valid {
              color: $success-color;
            }

            &.weight-invalid {
              color: $danger-color;
            }

            .weight-status {
              margin-left: $spacing-xs;
              font-size: 12px;
              padding: 2px 6px;
              border-radius: 3px;
              font-weight: 600;

              &.valid {
                background-color: #d4edda;
                color: #155724;
              }

              &.invalid {
                background-color: #f8d7da;
                color: #721c24;
              }
            }
          }
        }

        .indicator-form {
          margin-bottom: $spacing-lg;
          padding: $spacing-md;
          border: 1px solid $border-color;
          border-radius: 6px;
          background-color: $light-bg;
          cursor: move;
          transition: all 0.3s ease;
          position: relative;

          &.compact {
            padding: $spacing-sm $spacing-md;

            .indicator-form-header {
              cursor: pointer;
              user-select: none;

              .drag-handle {
                justify-content: space-between;
                width: 100%;

                .indicator-summary {
                  font-size: 12px;
                  color: $text-muted;
                  margin-left: auto;
                  margin-right: $spacing-sm;
                }

                .expand-icon {
                  font-size: 14px;
                  transition: transform 0.2s ease;
                  color: $text-muted;
                  margin-left: $spacing-xs;
                  cursor: pointer;

                  &.expanded {
                    transform: rotate(180deg);
                  }

                  &:hover {
                    color: $primary-color;
                  }
                }
              }
            }

            .indicator-edit-content {
              animation: slideDown 0.3s ease;
              padding-top: $spacing-md;
              border-top: 1px solid $border-color;
              margin-top: $spacing-md;
            }

            &:not(.expanded) {
              padding: $spacing-sm $spacing-md;
            }
          }

          &:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
          }

          &.dragging {
            opacity: 0.6;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
            z-index: 1000;
            transform: scale(1.02);
          }

          &.drag-over {
            border-color: $primary-color;
            background-color: rgba(0, 123, 255, 0.05);
            box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);

            &::before {
              content: '';
              position: absolute;
              top: -2px;
              left: 0;
              right: 0;
              height: 4px;
              background-color: $primary-color;
              border-radius: 2px;
            }
          }

          &.drag-active:not(.dragging):not(.drag-over) {
            opacity: 0.7;
          }

          &.new-indicator {
            background-color: #e8f5e8;
            border-color: $success-color;

            &.drag-over {
              background-color: rgba(40, 167, 69, 0.05);
              border-color: $success-color;

              &::before {
                background-color: $success-color;
              }
            }
          }

          .indicator-form-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: $spacing-md;
            font-weight: 500;
            color: $text-color;

            .drag-handle {
              display: flex;
              align-items: center;
              gap: $spacing-xs;
              cursor: move;
              flex: 1;
              min-width: 0;

              i {
                color: $text-muted;
                font-size: 14px;
                transition: color 0.2s ease;
              }

              &:hover i {
                color: $primary-color;
              }

              .preview-order {
                margin-left: $spacing-sm;
                font-size: 12px;
                color: $primary-color;
                font-weight: 600;
                background-color: rgba(0, 123, 255, 0.1);
                padding: 2px 6px;
                border-radius: 3px;
                white-space: nowrap;
                animation: fadeInScale 0.2s ease;
              }
            }
          }
        }

        // 新增指标卡片样式
        .new-indicators-section {
          margin-top: $spacing-lg;
          padding-top: $spacing-lg;
          border-top: 1px solid $border-color;

          h5 {
            margin: 0 0 $spacing-md 0;
            color: $text-color;
            font-size: 16px;
          }

          .indicator-card {
            margin-bottom: $spacing-md;
            padding: $spacing-md;
            border: 1px solid $success-color;
            border-radius: 6px;
            background-color: #f8fff8;

            .indicator-card-header {
              display: flex;
              justify-content: space-between;
              align-items: center;
              margin-bottom: 8px;

              .indicator-name {
                font-weight: 500;
                color: $text-color;
              }

              .indicator-actions {
                display: flex;
                gap: $spacing-xs;
              }
            }

            .indicator-card-content {
              .indicator-description {
                margin: 0 0 8px 0;
                color: $text-muted;
                font-size: 13px;
                line-height: 1.4;
              }

              .indicator-meta {
                display: flex;
                gap: $spacing-md;
                font-size: 12px;
                color: $text-muted;

                .required {
                  color: $danger-color;
                  font-weight: 500;
                }
              }
            }
          }
        }
      }

      .form-actions {
        display: flex;
        gap: $spacing-sm;
        justify-content: flex-end;
        margin-top: $spacing-lg;
        padding-top: $spacing-lg;
        border-top: 1px solid $border-color;
      }
    }
  }

  // 弹窗样式
  .dialog-overlay {
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
    animation: fadeInScale 0.2s ease;

    .dialog-content {
      background: white;
      border-radius: $border-radius;
      width: 90%;
      max-width: 600px;
      max-height: 80vh;
      overflow-y: auto;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);

      &.danger {
        border: 2px solid $danger-color;
      }

      .dialog-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: $spacing-lg;
        border-bottom: 1px solid $border-color;
        background-color: $light-bg;

        h4 {
          margin: 0;
          color: $text-color;
        }
      }

      .dialog-body {
        padding: $spacing-lg;

        .source-info {
          margin-bottom: $spacing-lg;
          padding: $spacing-md;
          background-color: #fff3cd;
          border: 1px solid #ffeaa7;
          border-radius: $border-radius-sm;

          p {
            margin: 0;

            &.tips {
              margin-top: $spacing-xs;
              font-size: 12px;
              color: #856404;
              display: flex;
              align-items: center;
              gap: $spacing-xs;
            }
          }
        }

        .warning-info {
          display: flex;
          gap: $spacing-md;
          padding: $spacing-md;
          background-color: #fff3cd;
          border: 1px solid #ffeaa7;
          border-radius: $border-radius-sm;

          i {
            color: $warning-color;
            font-size: 20px;
            margin-top: 2px;
          }

          p {
            margin: 0;

            &.delete-target {
              font-weight: 600;
              color: $danger-color;
              margin: $spacing-xs 0;
            }

            &.warning-text {
              font-size: 12px;
              color: #856404;
              margin-top: $spacing-xs;
            }
          }
        }

        .form-group {
          margin-bottom: $spacing-md;

          label {
            display: block;
            margin-bottom: $spacing-xs;
            font-weight: 500;
            color: $text-color;
          }

          input,
          textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid #ddd;
            border-radius: $border-radius-sm;
            font-size: 14px;

            &:focus {
              outline: none;
              border-color: $primary-color;
              box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
            }
          }
        }

        .form-row {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: $spacing-md;
        }
      }

      .dialog-footer {
        display: flex;
        justify-content: flex-end;
        gap: $spacing-sm;
        padding: $spacing-lg;
        border-top: 1px solid $border-color;
        background-color: $light-bg;
      }
    }
  }

  // 列表样式
  .standard-list {
    // 移除边框，融入外层卡片
    border: none;
    border-radius: 0;
    overflow: visible;

    .list-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: $spacing-md 0 $spacing-lg 0;
      background-color: transparent;
      // 移除底部边框，用内边距分隔
      border-bottom: none;
      margin-bottom: $spacing-lg;

      h3 {
        margin: 0;
        color: $text-color;
      }

      .list-actions {
        display: flex;
        gap: $spacing-sm;
        align-items: center;

        .search-input {
          padding: 6px 12px;
          border: 1px solid #ddd;
          border-radius: $border-radius-sm;
          font-size: 14px;
          width: 200px;
        }
      }
    }

    .list-filters {
      padding: 0 0 $spacing-lg 0;
      display: flex;
      gap: $spacing-xl;
      border-bottom: 1px solid $border-color;
      background-color: transparent;
      margin-bottom: $spacing-lg;

      .filter-group {
        display: flex;
        gap: $spacing-md;
        align-items: center;

        .filter-title {
          font-weight: 500;
          color: $text-color;
          margin-right: $spacing-xs;
        }

        label {
          display: flex;
          align-items: center;
          gap: $spacing-xs;
          cursor: pointer;
        }
      }
    }

    .standard-items {
      padding: 0;

      .standard-item {
        display: flex;
        margin-bottom: $spacing-md;
        border: 1px solid $border-color;
        border-radius: 6px;
        transition: all 0.2s;
        position: relative;

        &:hover:not(.disabled) {
          border-color: $primary-color;
          background-color: $light-bg;
        }

        &.disabled {
          opacity: 0.7;
          pointer-events: none;
        }

        &:last-child {
          margin-bottom: 0;
        }

        .standard-item-content {
          flex: 1;
          padding: $spacing-md;
          cursor: pointer;
        }

        .item-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 8px;

          h5 {
            margin: 0;
            color: $text-color;
          }

          .item-meta {
            display: flex;
            gap: $spacing-sm;
            align-items: center;
            font-size: 12px;

            .tag {
              padding: 4px 8px;
              border-radius: $border-radius-sm;
              background-color: #e9ecef;
              color: #495057;

              &.tag-template {
                background-color: #d4edda;
                color: #155724;
              }

              &.tag-used {
                background-color: #fff3cd;
                color: #856404;
              }
            }

            .indicator-count {
              color: $text-muted;
            }
          }
        }

        .item-description {
          margin: 0 0 $spacing-sm 0;
          color: $text-muted;
          line-height: 1.4;
        }

        .item-info {
          display: flex;
          gap: $spacing-md;
          font-size: 12px;
          color: $text-muted;
        }

        .usage-tip {
          margin-top: $spacing-sm;
          padding: $spacing-xs $spacing-sm;
          background-color: #e3f2fd;
          border: 1px solid #bbdefb;
          border-radius: $border-radius-sm;
          font-size: 11px;
          color: #1976d2;
          display: flex;
          align-items: center;
          gap: $spacing-xs;
        }

        .item-actions {
          display: flex;
          align-items: center;
          padding: $spacing-md;
          border-left: 1px solid $border-color;
          background-color: rgba(248, 249, 250, 0.5);
        }
      }
    }

    .no-data {
      padding: $spacing-xl 0;
      text-align: center;
      color: $text-light;
    }

    .pagination {
      display: flex;
      justify-content: center;
      align-items: center;
      gap: $spacing-sm;
      padding: $spacing-md 0 0 0;
      border-top: 1px solid $border-color;
      margin-top: $spacing-lg;
    }
  }

  // 按钮样式
  .btn {
    display: inline-flex;
    align-items: center;
    gap: $spacing-xs;
    padding: 8px 16px;
    border: 1px solid transparent;
    border-radius: $border-radius-sm;
    font-size: 14px;
    cursor: pointer;
    text-decoration: none;
    transition: all 0.2s;

    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }

    &.btn-primary {
      background-color: $primary-color;
      color: white;
      border-color: $primary-color;

      &:hover:not(:disabled) {
        background-color: color.adjust($primary-color, $lightness: -10%);
        border-color: color.adjust($primary-color, $lightness: -10%);
      }
    }

    &.btn-secondary {
      background-color: $secondary-color;
      color: white;
      border-color: $secondary-color;

      &:hover:not(:disabled) {
        background-color: color.adjust($secondary-color, $lightness: -10%);
        border-color: color.adjust($secondary-color, $lightness: -10%);
      }
    }

    &.btn-danger {
      background-color: $danger-color;
      color: white;
      border-color: $danger-color;

      &:hover:not(:disabled) {
        background-color: color.adjust($danger-color, $lightness: -10%);
        border-color: color.adjust($danger-color, $lightness: -10%);
      }
    }

    &.btn-text {
      background-color: transparent;
      color: $secondary-color;
      border: none;
      padding: 4px 8px;

      &:hover {
        color: color.adjust($secondary-color, $lightness: -15%);
        background-color: $light-bg;
      }
    }

    &.btn-small {
      padding: 4px 8px;
      font-size: 12px;
    }
  }

  .action-buttons {
    display: flex;
    gap: $spacing-sm;
  }

  // 工具样式
  .required {
    color: $danger-color;
  }

  .loading {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: $spacing-xl;
    color: $text-muted;
  }

  // 响应式
  @media (max-width: 768px) {
    padding: $spacing-md;

    .form-row {
      grid-template-columns: 1fr;
    }

    .standard-header,
    .list-header,
    .form-header {
      flex-direction: column;
      align-items: stretch;
      gap: $spacing-md;
    }

    .action-buttons {
      justify-content: center;
    }

    .list-actions {
      flex-direction: column;
      align-items: stretch;

      .search-input {
        width: 100%;
      }
    }

    .list-filters {
      flex-direction: column;
      gap: $spacing-md;

      .filter-group {
        justify-content: flex-start;
      }
    }

    .indicators-section {
      .drag-tip {
        font-size: 11px;
        padding: 6px 10px;
      }

      .indicator-form-header .drag-handle {
        font-size: 13px;

        .preview-order {
          font-size: 10px;
          padding: 1px 4px;
        }
      }
    }

    .dialog-content {
      width: 95%;
      margin: $spacing-sm;
    }

    .standard-items .standard-item {
      flex-direction: column;

      .item-actions {
        border-left: none;
        border-top: 1px solid $border-color;
        justify-content: center;
      }
    }
  }
}
</style>
