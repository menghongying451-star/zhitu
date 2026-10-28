<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { requirementService, userService, resourcesService, fileService } from '@/api'
import { useUserStore } from '@/stores'
import { debounce } from 'lodash'
import { ElMessage, ElMessageBox } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faArrowLeft,
  faSave,
  faSpinner,
  faExclamationTriangle,
  faPlus,
  faTimes,
  faCalendar,
  faDollarSign,
  faUsers,
  faFileText,
  faComments,
  faEdit,
  faSearch,
  faUpload,
  faFile,
  faCheckCircle,
  faTags,
  faFolder,
  faHandshake,
  faClipboardCheck,
  faLock
} from '@fortawesome/free-solid-svg-icons'

// 导入评分标准管理组件
import ScoreStandardManager from '@/components/ScoreStandardManager.vue'
import AgentChat from '@/components/AgentChat.vue'

// 添加图标到库
library.add(
  faArrowLeft,
  faSave,
  faSpinner,
  faExclamationTriangle,
  faPlus,
  faTimes,
  faCalendar,
  faDollarSign,
  faUsers,
  faFileText,
  faComments,
  faEdit,
  faSearch,
  faUpload,
  faFile,
  faCheckCircle,
  faTags,
  faFolder,
  faHandshake,
  faClipboardCheck,
  faLock
)

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

// 响应式数据
const loading = ref(false)
const saving = ref(false)

// 判断当前模式
const isEditMode = computed(() => route.path.includes('/edit/'))
const createMode = computed(() => route.params.mode || 'form') // chat 或 form
const requirementId = computed(() => route.params.id)
const organizationId = computed(() => userStore.user?.company_profile?.organization?.id)

// 表单数据
const formData = ref({
  title: '',
  brief: '',
  description: '',
  budget: '',
  people_count: '',
  finish_time: '',
  support_provided: '', // 新增字段：企业可提供的支持
  evaluation_criteria_id: null, // 新增字段：评分标准ID
  tag1_ids: [], // 兴趣标签
  tag2_ids: [], // 技能标签
  resources_ids: [], // 资源ID
  files: [] // 文件URL
})

// 评分标准相关
const currentStandardId = ref(null)
const evaluationCriteria = ref(null) // 当前评分标准信息
const evaluationPublished = ref(false) // 是否已完成评分公示

// 计算是否可编辑
const isEditable = computed(() => {
  if (!isEditMode.value) return true // 创建模式总是可编辑
  return !evaluationPublished.value // 编辑模式下，只有未完成评分公示的需求才能编辑
})

// 标签相关
const tag1List = ref([]) // 兴趣标签列表
const tag2List = ref([]) // 技能标签列表
const tag1Search = ref('')
const tag2Search = ref('')
const tag1Loading = ref(false)
const tag2Loading = ref(false)
const selectedTag1 = ref([]) // 已选择的兴趣标签
const selectedTag2 = ref([]) // 已选择的技能标签

// 资源相关
const resourceList = ref([])
const resourceLoading = ref(false)
const selectedResources = ref([])
const resourceSearch = ref('')
const resourcePage = ref(1)
const resourceTotal = ref(0)

// 文件上传相关
const fileInput = ref(null)
const uploadedFiles = ref([])
const uploadingFiles = ref(false)
const deletingFiles = ref(new Set()) // 正在删除的文件ID集合

// 表单验证规则
const validateForm = () => {
  const errors = []

  if (!formData.value.title.trim()) {
    errors.push('请输入需求标题')
  }

  if (!formData.value.brief.trim()) {
    errors.push('请输入需求简介')
  }

  if (!formData.value.finish_time) {
    errors.push('请选择完成时间')
  }

  return errors
}

// 处理评分标准变化
const handleStandardChange = (standardData) => {
  // standardChanged 事件传递的是完整数据对象
  formData.value.evaluation_criteria_id = standardData?.id || null
  evaluationCriteria.value = standardData || null
}

// 搜索兴趣标签
const searchTag1 = async () => {
  try {
    if (tag1Search.value.trim() === '') {
      tag1List.value = []
      return
    }
    tag1Loading.value = true
    const response = await userService.getInterestTagList(tag1Search.value)
    if (response.status === 'success') {
      tag1List.value = response.data || []
    }
  } catch (err) {
    console.error('搜索兴趣标签失败:', err)
    ElMessage.error('搜索兴趣标签失败，请重试')
  } finally {
    tag1Loading.value = false
  }
}

// 搜索技能标签
const searchTag2 = async () => {
  try {
    if (tag2Search.value.trim() === '') {
      tag2List.value = []
      return
    }
    tag2Loading.value = true
    const response = await userService.getSkillTagList(tag2Search.value)
    if (response.status === 'success') {
      tag2List.value = response.data || []
    }
  } catch (err) {
    console.error('搜索技能标签失败:', err)
    ElMessage.error('搜索技能标签失败，请重试')
  } finally {
    tag2Loading.value = false
  }
}

// 添加兴趣标签
const addTag1 = (tag) => {
  if (!selectedTag1.value.find((t) => t.id === tag.id)) {
    selectedTag1.value.push(tag)
    formData.value.tag1_ids.push(tag.id)
  }
}

// 移除兴趣标签
const removeTag1 = (index) => {
  const removedTag = selectedTag1.value.splice(index, 1)[0]
  formData.value.tag1_ids = formData.value.tag1_ids.filter((id) => id !== removedTag.id)
}

// 添加技能标签
const addTag2 = (tag) => {
  if (!selectedTag2.value.find((t) => t.id === tag.id)) {
    selectedTag2.value.push(tag)
    formData.value.tag2_ids.push(tag.id)
  }
}

// 移除技能标签
const removeTag2 = (index) => {
  const removedTag = selectedTag2.value.splice(index, 1)[0]
  formData.value.tag2_ids = formData.value.tag2_ids.filter((id) => id !== removedTag.id)
}

// 获取标签显示名称
const getTag1Name = (tag) => tag.value || tag.name
const getTag2Name = (tag) => tag.post || tag.name

// 获取资源列表
const fetchResources = async () => {
  if (!organizationId.value) return
  if (resourceSearch.value.trim() === '') {
    resourceList.value = []
    return
  }

  try {
    resourceLoading.value = true
    const params = {
      page: resourcePage.value,
      page_size: 10,
      keyword: resourceSearch.value
    }

    const response = await resourcesService.getResources(organizationId.value, params)
    if (response.status === 'success') {
      resourceList.value = response.data?.resources || []
      resourceTotal.value = response.data?.pagination?.total_count || 0
    }
  } catch (err) {
    console.error('获取资源列表失败:', err)
    ElMessage.error('获取资源列表失败，请重试')
  } finally {
    resourceLoading.value = false
  }
}

// 选择资源
const toggleResource = (resource) => {
  if (!isEditable.value) return // 不可编辑时禁用操作

  const index = selectedResources.value.findIndex((r) => r.id === resource.id)
  if (index > -1) {
    selectedResources.value.splice(index, 1)
    formData.value.resources_ids = formData.value.resources_ids.filter((id) => id !== resource.id)
  } else {
    selectedResources.value.push(resource)
    formData.value.resources_ids.push(resource.id)
  }
}

// 检查资源是否已选择
const isResourceSelected = (resource) => {
  return selectedResources.value.find((r) => r.id === resource.id)
}

// 移除已选择的资源
const removeSelectedResource = (resource) => {
  if (!isEditable.value) return // 不可编辑时禁用操作

  const index = selectedResources.value.findIndex((r) => r.id === resource.id)
  if (index > -1) {
    selectedResources.value.splice(index, 1)
    formData.value.resources_ids = formData.value.resources_ids.filter((id) => id !== resource.id)
  }
}

// 文件上传
const handleFileUpload = async (event) => {
  if (!isEditable.value) return // 不可编辑时禁用操作

  const files = Array.from(event.target.files)
  if (files.length === 0) return

  try {
    uploadingFiles.value = true

    for (const file of files) {
      if (isEditMode.value && requirementId.value) {
        // 编辑模式，直接上传到服务器
        try {
          const formDataFile = new FormData()
          formDataFile.append('files', file)

          const response = await fileService.uploadFile(
            formDataFile,
            requirementId.value,
            'requirement'
          )
          if (response.status === 'success') {
            const fileObj = {
              id: response.data.id,
              name: response.data.name || file.name,
              size: response.data.size || file.size,
              url: response.data.url,
              uploaded: true // 标记为已上传
            }
            uploadedFiles.value.push(fileObj)
            formData.value.files.push(fileObj.url)
          }
        } catch (err) {
          console.error('文件上传失败:', err)
          ElMessage.error(`文件 ${file.name} 上传失败：${err.detail || '未知错误'}`)
        }
      } else {
        // 创建模式，暂存文件对象
        const fileObj = {
          file: file,
          name: file.name,
          size: file.size,
          url: `temp://${file.name}`, // 临时URL
          uploaded: false // 标记为未上传
        }
        uploadedFiles.value.push(fileObj)
        // 创建模式不需要添加到formData.files中，将在提交时统一处理
      }
    }
  } catch (err) {
    console.error('文件处理失败:', err)
    ElMessage.error('文件处理失败，请重试')
  } finally {
    uploadingFiles.value = false
    // 清空input
    if (fileInput.value) {
      fileInput.value.value = ''
    }
  }
}

// 移除文件
const removeFile = async (index) => {
  if (!isEditable.value) return // 不可编辑时禁用操作

  const file = uploadedFiles.value[index]

  try {
    // 显示确认对话框
    await ElMessageBox.confirm(
      `确定要删除文件 "${file.name}" 吗？${
        isEditMode.value && file.uploaded ? '该操作将同时删除服务器上的文件。' : ''
      }`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )

    if (isEditMode.value && file.uploaded && file.id) {
      // 编辑模式且文件已上传，需要调用删除API
      try {
        deletingFiles.value.add(file.id)
        const deleteData = new FormData()
        deleteData.append('file_ids', file.id)

        await fileService.deleteFile(deleteData, requirementId.value, 'requirement')

        // 删除成功，从列表中移除
        uploadedFiles.value.splice(index, 1)
        formData.value.files.splice(index, 1)
        ElMessage.success('文件删除成功')
      } catch (err) {
        console.error('文件删除失败:', err)
        ElMessage.error(`文件删除失败：${err.detail || '未知错误'}`)
      } finally {
        deletingFiles.value.delete(file.id)
      }
    } else {
      // 创建模式或未上传的文件，直接从列表中移除
      uploadedFiles.value.splice(index, 1)
      formData.value.files.splice(index, 1)
      ElMessage.success('文件移除成功')
    }
  } catch (err) {
    // 用户取消删除或其他错误
    if (err !== 'cancel') {
      console.error('删除文件时发生错误:', err)
    }
  }
}

// 获取需求详情（编辑模式）
const fetchRequirementDetail = async () => {
  if (!requirementId.value) return

  try {
    loading.value = true

    const response = await requirementService.getRequirementDetail(requirementId.value)

    if (response.status === 'success') {
      const data = response.data
      formData.value = {
        title: data.title || '',
        brief: data.brief || '',
        description: data.description || '',
        budget: data.budget || '',
        people_count: data.people_count || '',
        finish_time: data.finish_time || '',
        support_provided: data.support_provided || '',
        evaluation_criteria_id: data.evaluation_criteria?.id || null,
        tag1_ids: data.tag1?.map((t) => t.id) || [],
        tag2_ids: data.tag2?.map((t) => t.id) || [],
        resources_ids: data.resources?.map((r) => r.id) || [],
        files: data.files?.map((f) => f.url) || []
      }

      // 设置评分标准信息
      evaluationCriteria.value = data.evaluation_criteria || null
      evaluationPublished.value = data.evaluation_published || false
      currentStandardId.value = data.evaluation_criteria?.id || null

      // 设置已选择的标签
      selectedTag1.value = data.tag1 || []
      selectedTag2.value = data.tag2 || []
      selectedResources.value = data.resources || []
      uploadedFiles.value =
        data.files?.map((f) => ({
          id: f.id,
          name: f.name,
          size: f.size,
          url: f.url,
          uploaded: true // 标记为已上传
        })) || []
    }
  } catch (err) {
    console.error('获取需求详情失败:', err)
    ElMessage.error('获取需求详情失败，请重试')
  } finally {
    loading.value = false
  }
}

// 保存需求
const saveRequirement = async () => {
  if (!isEditable.value) {
    ElMessage.warning('该需求已完成评分公示，无法修改')
    return
  }

  const validationErrors = validateForm()
  if (validationErrors.length > 0) {
    ElMessage.error(validationErrors.join('；'))
    return
  }

  try {
    saving.value = true

    let response
    if (isEditMode.value) {
      // 编辑模式，使用原有逻辑
      const submitData = {
        ...formData.value,
        tag1_ids: formData.value.tag1_ids.join(','),
        tag2_ids: formData.value.tag2_ids.join(','),
        resource_ids: formData.value.resources_ids.join(',')
      }
      response = await requirementService.updateRequirement(requirementId.value, submitData)
    } else {
      // 创建模式，使用FormData提交，包含文件
      const formDataSubmit = new FormData()

      // 添加基本字段
      formDataSubmit.append('title', formData.value.title)
      formDataSubmit.append('brief', formData.value.brief)
      formDataSubmit.append('description', formData.value.description)
      formDataSubmit.append('budget', formData.value.budget)
      formDataSubmit.append('people_count', formData.value.people_count)
      formDataSubmit.append('finish_time', formData.value.finish_time)
      formDataSubmit.append('support_provided', formData.value.support_provided || '')

      if (formData.value.evaluation_criteria_id) {
        formDataSubmit.append('evaluation_criteria_id', formData.value.evaluation_criteria_id)
      }

      // 添加标签和资源ID
      formDataSubmit.append('tag1_ids', formData.value.tag1_ids.join(','))
      formDataSubmit.append('tag2_ids', formData.value.tag2_ids.join(','))
      formDataSubmit.append('resource_ids', formData.value.resources_ids.join(','))

      // 添加文件
      for (const fileObj of uploadedFiles.value) {
        if (!fileObj.uploaded && fileObj.file) {
          formDataSubmit.append('files', fileObj.file)
        }
      }

      response = await requirementService.createRequirement(formDataSubmit)
    }

    if (response.status === 'success') {
      ElMessage.success(`需求${isEditMode.value ? '更新' : '发布'}成功！`)
      setTimeout(() => {
        router.back()
      }, 1500)
    }
  } catch (err) {
    console.error('保存需求失败:', err)
    ElMessage.error(`需求${isEditMode.value ? '更新' : '发布'}失败，请重试`)
  } finally {
    saving.value = false
  }
}

// 返回上一页
const goBack = () => {
  router.back()
}

// 监听搜索变化
watch(
  tag1Search,
  debounce(() => {
    if (tag1Search.value.length > 0) {
      searchTag1()
    }
  }, 300)
)

watch(
  tag2Search,
  debounce(() => {
    if (tag2Search.value.length > 0) {
      searchTag2()
    }
  }, 300)
)

watch(
  resourceSearch,
  debounce(() => {
    fetchResources()
  }, 300)
)

// 生命周期
onMounted(async () => {
  if (isEditMode.value) {
    await fetchRequirementDetail()
  }
  // 初始加载资源列表
  await fetchResources()
})

// 页面标题
const pageTitle = computed(() => {
  if (isEditMode.value) {
    return evaluationPublished.value ? '查看需求（已完成评分）' : '编辑需求'
  }
  return createMode.value === 'chat' ? '对话式发布需求' : '发布新需求'
})

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 对话式发布：智能体（填宝）完成发布后的回调
const onAgentAction = ({ name }) => {
  if (name === 'requirement_published') {
    ElMessage.success('需求已发布，可在「需求管理」中查看和编辑')
  }
}
</script>

<template>
  <div class="requirement-editor">
    <!-- Header -->
    <div class="editor-header">
      <div class="header-content">
        <button class="back-btn" @click="goBack">
          <FontAwesomeIcon :icon="['fas', 'arrow-left']" />
          返回
        </button>
        <div class="header-title">
          <h1>
            {{ pageTitle }}
            <FontAwesomeIcon
              v-if="isEditMode && evaluationPublished"
              :icon="['fas', 'lock']"
              class="lock-icon"
              title="该需求已完成评分公示，无法修改"
            />
          </h1>
          <p v-if="!isEditMode">
            {{ createMode === 'chat' ? '通过智能对话快速发布需求' : '填写详细信息发布需求' }}
          </p>
          <p v-else-if="evaluationPublished" class="published-notice">
            <FontAwesomeIcon :icon="['fas', 'check-circle']" />
            该需求已完成评分公示，所有信息均为只读状态
          </p>
        </div>
        <div class="header-actions" v-if="(createMode !== 'chat' || isEditMode) && isEditable">
          <button class="btn btn-primary" @click="saveRequirement" :disabled="saving || loading">
            <FontAwesomeIcon
              :icon="['fas', saving ? 'spinner' : 'save']"
              :class="{ 'fa-spin': saving }"
            />
            {{ saving ? '保存中...' : isEditMode ? '更新需求' : '发布需求' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 主要内容区域 -->
    <div class="editor-content">
      <!-- 对话式发布 -->
      <div v-if="createMode === 'chat' && !isEditMode" class="chat-container">
        <AgentChat agent="tianbao" :min-height="700" :show-tone="false" @action="onAgentAction" />
      </div>

      <!-- 表单发布/编辑 -->
      <div v-else class="form-container">
        <div v-if="loading" class="loading-state">
          <FontAwesomeIcon :icon="['fas', 'spinner']" class="fa-spin" />
          加载需求信息中...
        </div>

        <form v-else @submit.prevent="" class="requirement-form">
          <!-- 基本信息 -->
          <div class="form-section">
            <h3 class="section-title">
              <FontAwesomeIcon :icon="['fas', 'file-text']" />
              基本信息
            </h3>

            <div class="form-grid">
              <div class="form-group span-2">
                <label class="form-label required">需求标题</label>
                <input
                  v-model="formData.title"
                  type="text"
                  class="form-input"
                  :class="{ readonly: !isEditable }"
                  placeholder="请输入简洁明确的需求标题"
                  maxlength="100"
                  :readonly="!isEditable"
                />
              </div>

              <div class="form-group span-2">
                <label class="form-label required">需求简介</label>
                <textarea
                  v-model="formData.brief"
                  class="form-textarea"
                  :class="{ readonly: !isEditable }"
                  placeholder="简要描述您的需求，让服务商快速了解项目概况"
                  rows="3"
                  maxlength="500"
                  :readonly="!isEditable"
                ></textarea>
                <div class="char-count">{{ formData.brief.length }}/500</div>
              </div>

              <div class="form-group span-2">
                <label class="form-label">详细描述</label>
                <textarea
                  v-model="formData.description"
                  class="form-textarea"
                  :class="{ readonly: !isEditable }"
                  placeholder="详细描述项目背景、目标、功能要求等信息"
                  rows="6"
                  maxlength="2000"
                  :readonly="!isEditable"
                ></textarea>
                <div class="char-count">{{ formData.description.length }}/2000</div>
              </div>

              <!-- 兴趣标签移到基本信息区域 -->
              <div class="form-group span-2">
                <label class="form-label">兴趣标签</label>
                <div class="tags-section" :class="{ readonly: !isEditable }">
                  <div class="tag-search-group" v-if="isEditable">
                    <div class="search-input-wrapper">
                      <FontAwesomeIcon :icon="['fas', 'search']" class="search-icon" />
                      <input
                        v-model="tag1Search"
                        type="text"
                        class="form-input search-input"
                        placeholder="搜索兴趣标签..."
                      />
                      <FontAwesomeIcon
                        v-if="tag1Loading"
                        :icon="['fas', 'spinner']"
                        class="fa-spin loading-icon"
                      />
                    </div>

                    <div v-if="tag1List.length > 0" class="tag-suggestions">
                      <button
                        v-for="tag in tag1List"
                        :key="tag.id"
                        type="button"
                        class="tag-suggestion"
                        @click="addTag1(tag)"
                        :disabled="selectedTag1.find((t) => t.id === tag.id)"
                      >
                        {{ getTag1Name(tag) }}
                      </button>
                    </div>
                  </div>

                  <div v-if="selectedTag1.length > 0" class="selected-tags">
                    <span v-for="(tag, index) in selectedTag1" :key="tag.id" class="tag-item">
                      {{ getTag1Name(tag) }}
                      <button
                        v-if="isEditable"
                        type="button"
                        @click="removeTag1(index)"
                        class="tag-remove"
                      >
                        <FontAwesomeIcon :icon="['fas', 'times']" />
                      </button>
                    </span>
                  </div>
                </div>
              </div>

              <!-- 技能标签移到基本信息区域 -->
              <div class="form-group span-2">
                <label class="form-label">技能标签</label>
                <div class="tags-section" :class="{ readonly: !isEditable }">
                  <div class="tag-search-group" v-if="isEditable">
                    <div class="search-input-wrapper">
                      <FontAwesomeIcon :icon="['fas', 'search']" class="search-icon" />
                      <input
                        v-model="tag2Search"
                        type="text"
                        class="form-input search-input"
                        placeholder="搜索技能标签..."
                      />
                      <FontAwesomeIcon
                        v-if="tag2Loading"
                        :icon="['fas', 'spinner']"
                        class="fa-spin loading-icon"
                      />
                    </div>

                    <div v-if="tag2List.length > 0" class="tag-suggestions">
                      <button
                        v-for="tag in tag2List"
                        :key="tag.id"
                        type="button"
                        class="tag-suggestion"
                        @click="addTag2(tag)"
                        :disabled="selectedTag2.find((t) => t.id === tag.id)"
                      >
                        {{ getTag2Name(tag) }}
                      </button>
                    </div>
                  </div>

                  <div v-if="selectedTag2.length > 0" class="selected-tags">
                    <span v-for="(tag, index) in selectedTag2" :key="tag.id" class="tag-item">
                      {{ getTag2Name(tag) }}
                      <button
                        v-if="isEditable"
                        type="button"
                        @click="removeTag2(index)"
                        class="tag-remove"
                      >
                        <FontAwesomeIcon :icon="['fas', 'times']" />
                      </button>
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 项目要求 -->
          <div class="form-section">
            <h3 class="section-title">
              <FontAwesomeIcon :icon="['fas', 'edit']" />
              项目要求
            </h3>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">预算</label>
                <input
                  v-model="formData.budget"
                  type="text"
                  class="form-input"
                  :class="{ readonly: !isEditable }"
                  placeholder="单位：万元，如：1 或 0.5-1.5"
                  :readonly="!isEditable"
                />
              </div>

              <div class="form-group">
                <label class="form-label">团队人数</label>
                <input
                  v-model="formData.people_count"
                  type="text"
                  class="form-input"
                  :class="{ readonly: !isEditable }"
                  placeholder="推荐的团队人数，如：3-5 或 5"
                  :readonly="!isEditable"
                />
              </div>

              <div class="form-group span-2">
                <label class="form-label required">完成时间</label>
                <el-date-picker
                  v-model="formData.finish_time"
                  type="date"
                  class="form-input"
                  :class="{ readonly: !isEditable }"
                  style="width: 100%; height: 40px; border-radius: 0.5rem"
                  :disabled="!isEditable"
                  :picker-options="{
                    disabledDate(time) {
                      return time < Date.now() - 8.64e7
                    }
                  }"
                  placeholder="选择项目的预期完成时间"
                  format="YYYY-MM-DD"
                  value-format="YYYY-MM-DD"
                />
              </div>

              <!-- 新增企业支持字段 -->
              <div class="form-group span-2">
                <label class="form-label">企业可提供的支持</label>
                <textarea
                  v-model="formData.support_provided"
                  class="form-textarea"
                  :class="{ readonly: !isEditable }"
                  placeholder="描述您的企业/组织可以为项目提供的支持，如：技术指导、设备资源、办公场地、资金支持等"
                  rows="4"
                  maxlength="1000"
                  :readonly="!isEditable"
                ></textarea>
                <div class="char-count">{{ formData.support_provided.length }}/1000</div>
              </div>
            </div>
          </div>

          <!-- 评分标准 -->
          <div class="form-section">
            <h3 class="section-title">
              <FontAwesomeIcon :icon="['fas', 'clipboard-check']" />
              项目评分标准
            </h3>

            <ScoreStandardManager
              :standardId="currentStandardId"
              :editable="isEditable"
              @update:standardId="currentStandardId = $event"
              @standardChanged="handleStandardChange"
              class="score-standard-manager"
            />
          </div>

          <!-- 关联资源 -->
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">
                <FontAwesomeIcon :icon="['fas', 'folder']" />
                关联资源
              </h3>
              <el-tooltip
                content="在这里选择已上传的资源"
                placement="top"
                effect="light"
                class="info-tooltip"
              >
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div>

            <div class="resource-section" :class="{ readonly: !isEditable }">
              <div class="search-input-wrapper" v-if="isEditable">
                <FontAwesomeIcon :icon="['fas', 'search']" class="search-icon" />
                <input
                  v-model="resourceSearch"
                  type="text"
                  class="form-input search-input"
                  placeholder="搜索资源..."
                />
                <FontAwesomeIcon
                  v-if="resourceLoading"
                  :icon="['fas', 'spinner']"
                  class="fa-spin loading-icon"
                />
              </div>

              <div v-if="isEditable && resourceList.length > 0" class="resource-list">
                <div
                  v-for="resource in resourceList"
                  :key="resource.id"
                  class="resource-item"
                  :class="{ active: isResourceSelected(resource) }"
                  @click="toggleResource(resource)"
                >
                  <div class="resource-info">
                    <h4 class="resource-title">{{ resource.title }}</h4>
                    <p class="resource-description">{{ resource.description }}</p>
                    <div class="resource-tags" v-if="resource.tags && resource.tags.length > 0">
                      <span
                        v-for="tag in resource.tags.slice(0, 3)"
                        :key="tag"
                        class="resource-tag"
                      >
                        {{ tag }}
                      </span>
                      <span v-if="resource.tags.length > 3" class="more-tags">
                        +{{ resource.tags.length - 3 }}
                      </span>
                    </div>
                  </div>
                  <div class="resource-status">
                    <FontAwesomeIcon
                      :icon="['fas', isResourceSelected(resource) ? 'check-circle' : 'plus']"
                    />
                  </div>
                </div>
              </div>

              <div
                v-else-if="isEditable && !resourceLoading && resourceSearch"
                class="no-resources"
              >
                <p>没有找到相关资源</p>
              </div>

              <div v-if="selectedResources.length > 0" class="selected-resources">
                <h4>已选择的资源 ({{ selectedResources.length }})：</h4>
                <div class="selected-resource-list">
                  <div
                    v-for="resource in selectedResources"
                    :key="resource.id"
                    class="selected-resource-item"
                  >
                    <div class="selected-resource-info">
                      <span class="selected-resource-title">{{ resource.title }}</span>
                      <div
                        class="selected-resource-tags"
                        v-if="resource.tags && resource.tags.length > 0"
                      >
                        <span v-for="tag in resource.tags.slice(0, 2)" :key="tag" class="mini-tag">
                          {{ tag }}
                        </span>
                      </div>
                    </div>
                    <button
                      v-if="isEditable"
                      type="button"
                      @click="removeSelectedResource(resource)"
                      class="resource-remove"
                    >
                      <FontAwesomeIcon :icon="['fas', 'times']" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 文件上传 -->
          <div class="form-section">
            <div class="section-header">
              <h3 class="section-title">
                <FontAwesomeIcon :icon="['fas', 'upload']" />
                附件上传
              </h3>
              <el-tooltip
                content="在这里上传该需求特有的资料，如需求文档、参考图片、技术规范等，丰富的附件有助于学生更准确地理解需求内容。"
                placement="top"
                effect="light"
                class="info-tooltip"
              >
                <el-icon class="info-icon"><InfoFilled /></el-icon>
              </el-tooltip>
            </div>

            <!-- 文件处理提示 -->
            <div class="file-upload-tip">
              <p v-if="isEditMode && !isEditable" class="tip-text readonly-tip">
                <FontAwesomeIcon :icon="['fas', 'lock']" class="tip-icon" />
                该需求已完成评分公示，文件为只读状态
              </p>
              <p v-else-if="isEditMode" class="tip-text">
                <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" class="tip-icon" />
                编辑模式：文件将立即上传到服务器，删除操作会同步删除服务器文件
              </p>
              <p v-else class="tip-text">
                <FontAwesomeIcon :icon="['fas', 'upload']" class="tip-icon" />
                创建模式：文件将在需求保存成功后统一上传
              </p>
            </div>

            <div class="file-upload-section">
              <div v-if="isEditable" class="upload-area">
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  @change="handleFileUpload"
                  class="file-input"
                  accept=".pdf,.doc,.docx,.xls,.xlsx,.txt,.png,.jpg,.jpeg"
                  :disabled="uploadingFiles"
                />
                <div class="upload-prompt">
                  <FontAwesomeIcon
                    :icon="['fas', uploadingFiles ? 'spinner' : 'upload']"
                    class="upload-icon"
                    :class="{ 'fa-spin': uploadingFiles }"
                  />
                  <p>{{ uploadingFiles ? '正在上传...' : '点击上传文件或拖拽文件到此处' }}</p>
                  <p class="upload-hint">支持 PDF、Word、Excel、图片等格式</p>
                </div>
              </div>

              <div v-if="uploadedFiles.length > 0" class="uploaded-files">
                <h4>{{ isEditable ? '已上传的文件：' : '项目附件：' }}</h4>
                <div class="file-list">
                  <div v-for="(file, index) in uploadedFiles" :key="index" class="file-item">
                    <FontAwesomeIcon :icon="['fas', 'file']" class="file-icon" />
                    <div class="file-info">
                      <span class="file-name">{{ file.name }}</span>
                      <span class="file-size">{{ formatFileSize(file.size) }}</span>
                      <span v-if="!file.uploaded" class="file-status">待上传</span>
                    </div>
                    <button
                      v-if="isEditable"
                      type="button"
                      @click="removeFile(index)"
                      class="file-remove"
                      :disabled="deletingFiles.has(file.id)"
                    >
                      <FontAwesomeIcon
                        :icon="['fas', deletingFiles.has(file.id) ? 'spinner' : 'times']"
                        :class="{ 'fa-spin': deletingFiles.has(file.id) }"
                      />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.requirement-editor {
  min-height: 100vh;
  background-color: #f8fafc;
}

// Header
.editor-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 0;
  position: sticky;
  top: 0;
  z-index: 100;

  .header-content {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    align-items: center;
    gap: 1rem;

    @media (max-width: 768px) {
      flex-direction: column;
      align-items: stretch;
      gap: 0.75rem;
    }
  }

  .back-btn {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: none;
    border: none;
    color: #6b7280;
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 0.5rem;
    transition: all 0.2s;

    &:hover {
      color: #374151;
      background-color: #f3f4f6;
    }
  }

  .header-title {
    flex: 1;

    h1 {
      font-size: 1.5rem;
      font-weight: 600;
      color: #1f2937;
      margin: 0 0 0.25rem 0;
      display: flex;
      align-items: center;
      gap: 0.5rem;

      .lock-icon {
        color: #f59e0b;
        font-size: 1.125rem;
      }
    }

    p {
      color: #6b7280;
      margin: 0;
      font-size: 0.875rem;

      &.published-notice {
        color: #059669;
        display: flex;
        align-items: center;
        gap: 0.375rem;
        font-weight: 500;
      }
    }
  }

  .header-actions {
    display: flex;
    gap: 0.75rem;
  }
}

// Content
.editor-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.5rem 1rem;
}

// Chat Container
.chat-container {
  background: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

// Form Container
.form-container {
  .loading-state {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 3rem;
    color: #6b7280;
  }

  .requirement-form {
    display: flex;
    flex-direction: column;
    gap: 2rem;
  }
}

// Form Sections
.form-section {
  background: white;
  border-radius: 0.75rem;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  .section-title {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-size: 1.125rem;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 1.5rem 0;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #f3f4f6;

    .required-mark {
      color: #ef4444;
      margin-left: 0.25rem;
    }
  }
}

// Form Grid
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }

  .span-2 {
    grid-column: span 2;

    @media (max-width: 768px) {
      grid-column: span 1;
    }
  }
}

// Form Elements
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-label {
  font-weight: 500;
  color: #374151;
  font-size: 0.875rem;

  &.required::after {
    content: ' *';
    color: #ef4444;
  }
}

.form-input,
.form-select,
.form-textarea {
  padding: 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  transition: border-color 0.2s;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
  }

  &::placeholder {
    color: #9ca3af;
  }

  &:disabled,
  &.readonly {
    background-color: #f9fafb;
    cursor: not-allowed;
    color: #6b7280;
  }

  &.readonly {
    border-color: #e5e7eb;
  }
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.char-count {
  font-size: 0.75rem;
  color: #6b7280;
  text-align: right;
}

// Tags Section
.tags-section {
  &.readonly .selected-tags .tag-item .tag-remove {
    display: none;
  }

  .tag-search-group {
    margin-bottom: 1rem;
  }

  .search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;

    .search-icon {
      position: absolute;
      left: 0.75rem;
      color: #9ca3af;
      z-index: 10;
    }

    .search-input {
      padding-left: 2.5rem;
      padding-right: 2.5rem;
      width: 100%;
    }

    .loading-icon {
      position: absolute;
      right: 0.75rem;
      color: #9ca3af;
    }
  }

  .tag-suggestions {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 0.75rem;
    max-height: 200px;
    overflow-y: auto;

    .tag-suggestion {
      padding: 0.375rem 0.75rem;
      background: #f3f4f6;
      border: 1px solid #d1d5db;
      border-radius: 9999px;
      font-size: 0.75rem;
      cursor: pointer;
      transition: all 0.2s;

      &:hover:not(:disabled) {
        background: #e5e7eb;
      }

      &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
      }
    }
  }

  .selected-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;

    .tag-item {
      display: inline-flex;
      align-items: center;
      gap: 0.25rem;
      padding: 0.25rem 0.75rem;
      background-color: #dbeafe;
      color: #1e40af;
      border-radius: 9999px;
      font-size: 0.75rem;

      .tag-remove {
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
      }
    }
  }
}

// Score Standard Manager
.score-standard-manager {
  // 组件样式由组件本身控制
}

// Resource Section
.resource-section {
  &.readonly {
    .search-input-wrapper,
    .resource-list {
      display: none;
    }

    .selected-resources .resource-remove {
      display: none;
    }
  }

  .search-input-wrapper {
    position: relative;
    display: flex;
    align-items: center;

    .search-icon {
      position: absolute;
      left: 0.75rem;
      color: #9ca3af;
      z-index: 10;
    }

    .search-input {
      padding-left: 2.5rem;
      padding-right: 2.5rem;
      width: 100%;
    }

    .loading-icon {
      position: absolute;
      right: 0.75rem;
      color: #9ca3af;
    }
  }

  .resource-list {
    margin-top: 1rem;
    max-height: 400px;
    overflow-y: auto;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;

    .resource-item {
      display: flex;
      align-items: flex-start;
      padding: 1rem;
      border-bottom: 1px solid #f3f4f6;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        background: #f9fafb;
      }

      &.active {
        background: #dbeafe;
        border-color: #3b82f6;
      }

      &:last-child {
        border-bottom: none;
      }

      .resource-info {
        flex: 1;
        min-width: 0;

        .resource-title {
          margin: 0 0 0.5rem 0;
          font-size: 0.875rem;
          font-weight: 600;
          color: #1f2937;
          line-height: 1.25;
        }

        .resource-description {
          margin: 0 0 0.75rem 0;
          font-size: 0.75rem;
          color: #6b7280;
          line-height: 1.4;

          display: -webkit-box;
          -webkit-line-clamp: 1;
          -webkit-box-orient: vertical;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .resource-tags {
          display: flex;
          flex-wrap: wrap;
          gap: 0.375rem;
          align-items: center;

          .resource-tag {
            padding: 0.125rem 0.5rem;
            background: #f3f4f6;
            color: #4b5563;
            border-radius: 0.25rem;
            font-size: 0.625rem;
            font-weight: 500;
          }

          .more-tags {
            font-size: 0.625rem;
            color: #9ca3af;
            font-weight: 500;
          }
        }
      }

      .resource-status {
        color: #3b82f6;
        margin-left: 0.75rem;
        margin-top: 0.125rem;

        svg {
          width: 1.25rem;
          height: 1.25rem;
        }
      }
    }
  }

  .no-resources {
    text-align: center;
    padding: 2rem;
    color: #6b7280;
    font-size: 0.875rem;
    border: 1px solid #e5e7eb;
    border-radius: 0.5rem;
    margin-top: 1rem;
  }

  .selected-resources {
    margin-top: 1.5rem;
    padding-top: 1.5rem;
    border-top: 1px solid #e5e7eb;

    h4 {
      margin: 0 0 1rem 0;
      font-size: 0.875rem;
      font-weight: 600;
      color: #1f2937;
    }

    .selected-resource-list {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;

      .selected-resource-item {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0.75rem;
        background: #f0fdf4;
        border: 1px solid #d4e6da;
        border-radius: 0.5rem;

        .selected-resource-info {
          flex: 1;
          min-width: 0;

          .selected-resource-title {
            display: block;
            font-size: 0.875rem;
            font-weight: 500;
            color: #1f2937;
            margin-bottom: 0.375rem;
          }

          .selected-resource-tags {
            display: flex;
            gap: 0.25rem;
            flex-wrap: wrap;

            .mini-tag {
              padding: 0.125rem 0.375rem;
              background: #dcfce7;
              color: #166534;
              border-radius: 0.25rem;
              font-size: 0.625rem;
              font-weight: 500;
            }
          }
        }

        .resource-remove {
          background: none;
          border: none;
          color: #6b7280;
          cursor: pointer;
          padding: 0.375rem;
          border-radius: 0.25rem;
          transition: color 0.2s;
          margin-left: 0.75rem;

          &:hover {
            color: #ef4444;
          }

          svg {
            width: 1rem;
            height: 1rem;
          }
        }
      }
    }
  }
}

// File Upload Section
.file-upload-section {
  .file-upload-tip {
    margin-bottom: 1rem;
    padding: 0.75rem;
    background: #f0f9ff;
    border: 1px solid #bae6fd;
    border-radius: 0.5rem;

    .tip-text {
      margin: 0;
      font-size: 0.875rem;
      color: #0c4a6e;
      display: flex;
      align-items: center;
      gap: 0.5rem;

      &.readonly-tip {
        background: #fef7ed;
        border-color: #fed7aa;
        color: #9a3412;

        .tip-icon {
          color: #f59e0b;
        }
      }

      .tip-icon {
        color: #0ea5e9;
        font-size: 0.875rem;
      }
    }
  }

  .upload-area {
    position: relative;
    border: 2px dashed #d1d5db;
    border-radius: 0.5rem;
    padding: 2rem;
    text-align: center;
    transition: all 0.2s;
    cursor: pointer;

    &:hover {
      border-color: #3b82f6;
      background: #f8fafc;
    }

    .file-input {
      position: absolute;
      inset: 0;
      opacity: 0;
      cursor: pointer;
    }

    .upload-prompt {
      .upload-icon {
        font-size: 2rem;
        color: #9ca3af;
        margin-bottom: 1rem;
      }

      p {
        margin: 0.5rem 0;
        color: #374151;

        &.upload-hint {
          font-size: 0.75rem;
          color: #6b7280;
        }
      }
    }
  }

  .uploaded-files {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid #f3f4f6;

    h4 {
      margin: 0 0 0.75rem 0;
      font-size: 0.875rem;
      font-weight: 500;
    }

    .file-list {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;

      .file-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.75rem;
        background: #f9fafb;
        border-radius: 0.5rem;

        .file-icon {
          color: #6b7280;
        }

        .file-info {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 0.125rem;

          .file-name {
            font-size: 0.875rem;
            font-weight: 500;
          }

          .file-size {
            font-size: 0.75rem;
            color: #6b7280;
          }

          .file-status {
            font-size: 0.75rem;
            color: #f59e0b;
            font-weight: 500;
          }
        }

        .file-remove {
          background: none;
          border: none;
          color: #6b7280;
          cursor: pointer;
          padding: 0.375rem;
          border-radius: 0.25rem;
          transition: color 0.2s;

          &:hover:not(:disabled) {
            color: #ef4444;
          }

          &:disabled {
            opacity: 0.5;
            cursor: not-allowed;
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
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  font-weight: 500;
  transition: all 0.2s;
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 0.875rem;

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

  &.btn-primary {
    background-color: #2563eb;
    color: white;

    &:hover:not(:disabled) {
      background-color: #1d4ed8;
    }
  }

  &.btn-outline {
    border-color: #d1d5db;
    background-color: white;
    color: #374151;

    &:hover:not(:disabled) {
      background-color: #f9fafb;
    }
  }

  &.btn-sm {
    padding: 0.5rem 0.75rem;
    font-size: 0.75rem;
  }
}
/* 区块标题和提示图标容器 */
.section-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;

  /* 信息提示图标样式 */
  .info-icon {
    color: #909399;
    cursor: pointer;
    font-size: 1rem;
    vertical-align: middle;
    margin-bottom: 2.15rem;
  }
}
</style>
