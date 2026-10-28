<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { debounce } from 'lodash-es'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { resourcesService, userService, fileService } from '@/api'
import {
  faUpload,
  faFile,
  faPlus,
  faTimes,
  faEdit,
  faTrash,
  faSave,
  faArrowLeft,
  faDownload,
  faEye,
  faCode,
  faDatabase,
  faFileAlt,
  faGraduationCap,
  faVideo,
  faWrench,
  faImage,
  faFileCode,
  faFilePdf,
  faFileArchive,
  faEllipsisV,
  faChevronRight,
  faChevronDown,
  faCopy,
  faExclamationTriangle,
  faFileEdit,
  faSpinner,
  faTags,
  faBriefcase,
  faSync,
  faInfoCircle
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faUpload,
  faFile,
  faPlus,
  faTimes,
  faEdit,
  faTrash,
  faSave,
  faArrowLeft,
  faDownload,
  faEye,
  faCode,
  faDatabase,
  faFileAlt,
  faGraduationCap,
  faVideo,
  faWrench,
  faImage,
  faFileCode,
  faFilePdf,
  faFileArchive,
  faEllipsisV,
  faChevronRight,
  faChevronDown,
  faCopy,
  faExclamationTriangle,
  faFileEdit,
  faSpinner,
  faTags,
  faBriefcase,
  faSync,
  faInfoCircle
)

// 路由相关
const route = useRoute()
const router = useRouter()

// 编辑模式检测
const isEditMode = computed(() => {
  return route.name === 'ResourceEdit' || route.params.id
})

const resourceId = computed(() => {
  return route.params.id
})

// 表单数据
const formData = reactive({
  title: '',
  description: '',
  type: '',
  status: 'draft',
  tag1_ids: [],
  tag2_ids: [],
  files: []
})

// 表单验证
const formErrors = reactive({
  title: '',
  description: '',
  type: '',
  status: '',
  files: ''
})

// 资源标签相关
const tag1Input = ref('')
const showTag1Suggestions = ref(false)
const tag1Suggestions = ref([])
const tag1SuggestionsLoading = ref(false)
const selectedTag1s = ref([])

// 技能标签相关
const tag2Input = ref('')
const showTag2Suggestions = ref(false)
const tag2Suggestions = ref([])
const tag2SuggestionsLoading = ref(false)
const selectedTag2s = ref([])

// 文件管理
const fileList = ref([]) // 新上传的文件
const existingFiles = ref([]) // 已存在的文件
const dragOver = ref(false)
const deletingFileIds = ref(new Set()) // 正在删除的文件ID集合

// 状态管理
const loading = ref(false)
const saving = ref(false)
const savingDraft = ref(false)
const updating = ref(false)

// 资源类型选项
const resourceTypes = [
  { value: 'code', label: '代码', icon: ['fas', 'code'] },
  { value: 'dataset', label: '数据集', icon: ['fas', 'database'] },
  { value: 'document', label: '文档', icon: ['fas', 'file-alt'] },
  { value: 'course', label: '课程', icon: ['fas', 'graduation-cap'] },
  { value: 'video', label: '视频', icon: ['fas', 'video'] },
  { value: 'tool', label: '工具', icon: ['fas', 'wrench'] }
]

// 资源状态选项
const statusOptions = [
  { value: 'published', label: '已发布' },
  { value: 'draft', label: '草稿' },
  { value: 'unpublished', label: '已下线' }
]

// 获取资源详情
const loadResourceDetail = async () => {
  if (!resourceId.value) return

  loading.value = true
  try {
    const response = await resourcesService.getResourceDetail(resourceId.value)
    if (response?.status === 'success' && response.data) {
      const resource = response.data

      // 填充基本信息
      formData.title = resource.title || ''
      formData.description = resource.description || ''
      formData.type = resource.type || ''
      formData.status = resource.status || 'draft'

      // 填充资源标签
      if (resource.tag1 && Array.isArray(resource.tag1)) {
        selectedTag1s.value = resource.tag1.map((tag) => ({
          id: tag.id,
          value: tag.name
        }))
        formData.tag1_ids = resource.tag1.map((tag) => tag.id)
      }

      // 填充技能标签
      if (resource.tag2 && Array.isArray(resource.tag2)) {
        selectedTag2s.value = resource.tag2.map((tag) => ({
          id: tag.id,
          post: tag.name
        }))
        formData.tag2_ids = resource.tag2.map((tag) => tag.id)
      }

      // 处理已存在的文件
      if (resource.files && Array.isArray(resource.files)) {
        existingFiles.value = resource.files.map((file) => ({
          id: file.id,
          name: file.name,
          size: file.size,
          url: file.url,
          path: file.path,
          created_at: file.created_at,
          isExisting: true
        }))
      }
    } else {
      throw new Error(response?.message || '获取资源详情失败')
    }
  } catch (error) {
    console.error('获取资源详情失败:', error)
    ElMessage.error(error.message || '获取资源详情失败')
    router.push('/enterprise/resource-management')
  } finally {
    loading.value = false
  }
}

// 删除已存在的文件
const deleteExistingFile = async (file) => {
  try {
    await ElMessageBox.confirm(`确定要删除文件 "${file.name}" 吗？此操作不可撤销。`, '确认删除', {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
      confirmButtonClass: 'el-button--danger'
    })

    deletingFileIds.value.add(file.id)

    const formData = new FormData()
    console.log(file.id)
    formData.append('file_ids', file.id.toString())

    const response = await fileService.deleteFile(formData, resourceId.value, 'resource')

    if (response?.status === 'success') {
      // 从已存在文件列表中移除
      existingFiles.value = existingFiles.value.filter((f) => f.id !== file.id)
      ElMessage.success('文件删除成功')
    } else {
      throw new Error(response?.message || '删除失败')
    }
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除文件失败:', error)
      ElMessage.error(error.message || '删除文件失败')
    }
  } finally {
    deletingFileIds.value.delete(file.id)
  }
}

// 上传新文件
const uploadNewFiles = async () => {
  if (fileList.value.length === 0) return

  try {
    const formData = new FormData()
    fileList.value.forEach((fileItem) => {
      formData.append('files', fileItem.file)
    })

    const response = await fileService.uploadFile(formData, resourceId.value, 'resource')

    if (response?.status === 'success') {
      ElMessage.success('文件上传成功')
      // 清空新上传的文件列表
      fileList.value = []
      // 重新加载资源详情以获取最新的文件列表
      await loadResourceDetail()
    } else {
      throw new Error(response?.message || '上传失败')
    }
  } catch (error) {
    console.error('上传文件失败:', error)
    ElMessage.error(error.message || '上传文件失败')
    throw error
  }
}

// 获取资源标签建议的防抖函数
const getTag1Suggestions = debounce(async (search) => {
  if (!search || search.length < 2) {
    tag1Suggestions.value = []
    return
  }

  tag1SuggestionsLoading.value = true
  try {
    const response = await userService.getInterestTagList(search)
    if (response?.status === 'success' && Array.isArray(response.data)) {
      const selectedIds = selectedTag1s.value.map((tag) => tag.id)
      tag1Suggestions.value = response.data.filter((tag) => !selectedIds.includes(tag.id))
    } else {
      console.warn('获取资源标签建议返回数据格式异常:', response)
      tag1Suggestions.value = []
    }
  } catch (error) {
    console.error('获取资源标签建议失败:', error)
    tag1Suggestions.value = []
  } finally {
    tag1SuggestionsLoading.value = false
  }
}, 300)

// 获取技能标签建议的防抖函数
const getTag2Suggestions = debounce(async (search) => {
  if (!search || search.length < 2) {
    tag2Suggestions.value = []
    return
  }

  tag2SuggestionsLoading.value = true
  try {
    const response = await userService.getSkillTagList(search)
    if (response?.status === 'success' && Array.isArray(response.data)) {
      const selectedIds = selectedTag2s.value.map((tag) => tag.id)
      tag2Suggestions.value = response.data.filter((tag) => !selectedIds.includes(tag.id))
    } else {
      console.warn('获取技能标签建议返回数据格式异常:', response)
      tag2Suggestions.value = []
    }
  } catch (error) {
    console.error('获取技能标签建议失败:', error)
    tag2Suggestions.value = []
  } finally {
    tag2SuggestionsLoading.value = false
  }
}, 300)

// 处理资源标签输入
const handleTag1Input = (value) => {
  tag1Input.value = value
  if (value && value.length >= 2) {
    showTag1Suggestions.value = true
    getTag1Suggestions(value)
  } else {
    showTag1Suggestions.value = false
    tag1Suggestions.value = []
  }
}

// 处理技能标签输入
const handleTag2Input = (value) => {
  tag2Input.value = value
  if (value && value.length >= 2) {
    showTag2Suggestions.value = true
    getTag2Suggestions(value)
  } else {
    showTag2Suggestions.value = false
    tag2Suggestions.value = []
  }
}

// 获取文件图标
const getFileIcon = (fileName) => {
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
    gz: ['fas', 'file-archive'],

    // 视频文件
    mp4: ['fas', 'video'],
    avi: ['fas', 'video'],
    mov: ['fas', 'video'],
    wmv: ['fas', 'video'],
    flv: ['fas', 'video'],
    webm: ['fas', 'video']
  }

  return iconMap[ext] || ['fas', 'file']
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === null || bytes === undefined) return '未知大小'
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 格式化日期
const formatDate = (dateString) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 拖拽处理
const handleDragOver = (e) => {
  e.preventDefault()
  dragOver.value = true
}

const handleDragLeave = (e) => {
  e.preventDefault()
  if (!e.currentTarget.contains(e.relatedTarget)) {
    dragOver.value = false
  }
}

const handleDrop = (e) => {
  e.preventDefault()
  dragOver.value = false

  const files = Array.from(e.dataTransfer.files)
  addFiles(files)
}

// 文件输入处理
const handleFileInput = (e) => {
  const files = Array.from(e.target.files)
  addFiles(files)
  e.target.value = ''
}

// 添加文件到列表
const addFiles = (files) => {
  files.forEach((file) => {
    const fileObj = {
      id: `file_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified,
      file: file
    }
    fileList.value.push(fileObj)
  })

  updateFilesData()
}

// 更新表单中的文件数据
const updateFilesData = () => {
  formData.files = fileList.value.map((file) => file.file)
}

// 删除新上传的文件
const removeFile = (fileId) => {
  fileList.value = fileList.value.filter((file) => file.id !== fileId)
  updateFilesData()
}

// 资源标签操作
const addTag1 = () => {
  tag1Input.value = ''
  showTag1Suggestions.value = false
}

const removeTag1 = (index) => {
  selectedTag1s.value.splice(index, 1)
  updateTagIds()
}

const addSuggestedTag1 = (tag) => {
  const normalizedTag = {
    id: tag.id,
    value: tag.value || tag.name
  }

  if (!selectedTag1s.value.find((t) => t.id === normalizedTag.id)) {
    selectedTag1s.value.push(normalizedTag)
    tag1Input.value = ''
    showTag1Suggestions.value = false
    tag1Suggestions.value = []
    updateTagIds()
  }
}

// 技能标签操作
const addTag2 = () => {
  tag2Input.value = ''
  showTag2Suggestions.value = false
}

const removeTag2 = (index) => {
  selectedTag2s.value.splice(index, 1)
  updateTagIds()
}

const addSuggestedTag2 = (tag) => {
  const normalizedTag = {
    id: tag.id,
    post: tag.post || tag.name,
    category: tag.category || '',
    subcategory: tag.subcategory || '',
    specialty: tag.specialty || ''
  }

  if (!selectedTag2s.value.find((t) => t.id === normalizedTag.id)) {
    selectedTag2s.value.push(normalizedTag)
    tag2Input.value = ''
    showTag2Suggestions.value = false
    tag2Suggestions.value = []
    updateTagIds()
  }
}

// 更新标签ID数组
const updateTagIds = () => {
  formData.tag1_ids = selectedTag1s.value.map((tag) => tag.id)
  formData.tag2_ids = selectedTag2s.value.map((tag) => tag.id)
}

// 延迟隐藏建议框的方法
const hideTag1SuggestionsDelayed = () => {
  setTimeout(() => {
    showTag1Suggestions.value = false
  }, 200)
}

const hideTag2SuggestionsDelayed = () => {
  setTimeout(() => {
    showTag2Suggestions.value = false
  }, 200)
}

// 表单验证
const validateForm = (isDraft = false) => {
  let isValid = true

  // 重置错误
  Object.keys(formErrors).forEach((key) => {
    formErrors[key] = ''
  })

  if (isDraft) {
    // 标题验证
    if (!formData.title.trim()) {
      formErrors.title = '请输入资源名称'
      isValid = false
    }

    // 描述验证
    if (!formData.description.trim()) {
      formErrors.description = '请输入资源描述'
      isValid = false
    }
  } else {
    // 正式发布需要所有必填字段
    if (!formData.title.trim()) {
      formErrors.title = '请输入资源名称'
      isValid = false
    }

    if (!formData.description.trim()) {
      formErrors.description = '请输入资源描述'
      isValid = false
    }

    if (!formData.type) {
      formErrors.type = '请选择资源类型'
      isValid = false
    }

    if (!formData.status) {
      formErrors.status = '请选择资源状态'
      isValid = false
    }

    // 文件验证（编辑模式下，如果没有已存在文件且没有新文件，则需要上传）
    if (!isEditMode.value && fileList.value.length === 0) {
      formErrors.files = '请至少上传一个文件'
      isValid = false
    } else if (
      isEditMode.value &&
      existingFiles.value.length === 0 &&
      fileList.value.length === 0
    ) {
      formErrors.files = '资源必须至少包含一个文件'
      isValid = false
    }
  }

  return isValid
}

// 创建FormData对象
const createFormData = (status) => {
  const formDataObj = new FormData()

  formDataObj.append('title', formData.title)
  formDataObj.append('description', formData.description)
  formDataObj.append('type', formData.type)
  formDataObj.append('status', status || formData.status)

  if (formData.tag1_ids && formData.tag1_ids.length > 0) {
    formDataObj.append('tag1_ids', formData.tag1_ids.join(','))
  } else {
    formDataObj.append('tag1_ids', '')
  }

  if (formData.tag2_ids && formData.tag2_ids.length > 0) {
    formDataObj.append('tag2_ids', formData.tag2_ids.join(','))
  } else {
    formDataObj.append('tag2_ids', '')
  }

  // 编辑模式下不包含文件，因为文件是独立管理的
  if (!isEditMode.value && formData.files.length > 0) {
    formData.files.forEach((file) => {
      formDataObj.append('files', file)
    })
  }

  return formDataObj
}

// 保存草稿
const saveDraft = async () => {
  if (!validateForm(true)) {
    return
  }

  savingDraft.value = true

  try {
    const formDataObj = createFormData('draft')
    const response = await resourcesService.createResource(formDataObj)

    if (response?.status === 'success') {
      ElMessage.success('草稿保存成功！')
      router.push('/enterprise/resource-management')
    } else {
      throw new Error(response?.message || '保存失败')
    }
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error(error.message || '保存草稿失败，请重试')
  } finally {
    savingDraft.value = false
  }
}

// 保存资源（发布）
const saveResource = async () => {
  if (!validateForm()) {
    return
  }

  saving.value = true

  try {
    const formDataObj = createFormData('published')
    const response = await resourcesService.createResource(formDataObj)

    if (response?.status === 'success') {
      ElMessage.success('资源发布成功！')
      router.push('/enterprise/resource-management')
    } else {
      throw new Error(response?.message || '发布失败')
    }
  } catch (error) {
    console.error('发布失败:', error)
    ElMessage.error(error.message || '发布失败，请重试')
  } finally {
    saving.value = false
  }
}

// 更新资源基本信息
const updateResource = async () => {
  if (!validateForm()) {
    return
  }

  updating.value = true

  try {
    const formDataObj = createFormData()

    console.log('更新资源时的标签ID:', {
      tag1_ids: formData.tag1_ids,
      tag2_ids: formData.tag2_ids
    })

    const response = await resourcesService.updateResource(resourceId.value, formDataObj)

    if (response?.status === 'success') {
      ElMessage.success('资源基本信息更新成功！')
      // 更新后重新加载数据以确保显示最新信息
      await loadResourceDetail()
    } else {
      throw new Error(response?.message || '更新失败')
    }
  } catch (error) {
    console.error('更新失败:', error)
    ElMessage.error(error.message || '更新失败，请重试')
  } finally {
    updating.value = false
  }
}

// 上传新文件并刷新
const uploadAndRefresh = async () => {
  if (fileList.value.length === 0) {
    ElMessage.warning('请先选择要上传的文件')
    return
  }

  try {
    await uploadNewFiles()
  } catch (error) {
    // 错误处理已在uploadNewFiles中处理
  }
}

// 返回资源列表
const goBack = () => {
  router.back()
}

// 组件挂载时的处理
onMounted(() => {
  if (isEditMode.value) {
    loadResourceDetail()
  }
})
</script>

<template>
  <div class="resource-editor">
    <!-- 头部 -->
    <div class="editor-header">
      <div class="header-left">
        <button class="btn-back" @click="goBack">
          <FontAwesomeIcon :icon="['fas', 'arrow-left']" class="mr-2" />
          返回
        </button>
        <h1 class="page-title">{{ isEditMode ? '编辑资源' : '发布资源' }}</h1>
      </div>
      <div class="header-actions">
        <!-- 编辑模式：只显示更新基本信息按钮 -->
        <template v-if="isEditMode">
          <button class="btn-primary" @click="updateResource" :disabled="updating || loading">
            <FontAwesomeIcon :icon="['fas', 'sync']" class="mr-2" />
            {{ updating ? '更新中...' : '更新基本信息' }}
          </button>
        </template>

        <!-- 创建模式：显示草稿和发布按钮 -->
        <template v-else>
          <button class="btn-secondary" @click="saveDraft" :disabled="savingDraft || saving">
            <FontAwesomeIcon :icon="['fas', 'file-edit']" class="mr-2" />
            {{ savingDraft ? '保存中...' : '存为草稿' }}
          </button>

          <button class="btn-primary" @click="saveResource" :disabled="saving || savingDraft">
            <FontAwesomeIcon :icon="['fas', 'save']" class="mr-2" />
            {{ saving ? '发布中...' : '发布资源' }}
          </button>
        </template>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <FontAwesomeIcon :icon="['fas', 'spinner']" spin class="loading-icon" />
      <p>加载资源详情中...</p>
    </div>

    <div v-else class="editor-content">
      <!-- 编辑模式提示信息 -->
      <div v-if="isEditMode" class="edit-info-banner">
        <FontAwesomeIcon :icon="['fas', 'info-circle']" class="info-icon" />
        <div class="info-content">
          <h4>编辑模式说明</h4>
          <p>在编辑模式下，基本信息修改和文件管理是独立的操作：</p>
          <ul>
            <li>
              <strong>基本信息修改：</strong
              >点击"更新基本信息"按钮保存标题、描述、类型、状态、标签等信息
            </li>
            <li>
              <strong>文件管理：</strong>可以独立删除现有文件或上传新文件，立即生效无需额外保存
            </li>
          </ul>
        </div>
      </div>

      <!-- 基本信息 -->
      <div class="form-section">
        <h2 class="section-title">基本信息</h2>

        <div class="form-grid">
          <!-- 资源名称 -->
          <div class="form-group">
            <label class="form-label required">资源名称</label>
            <input
              type="text"
              v-model="formData.title"
              class="form-input"
              :class="{ error: formErrors.title }"
              placeholder="请输入资源名称"
              maxlength="100"
            />
            <div v-if="formErrors.title" class="form-error">{{ formErrors.title }}</div>
          </div>

          <!-- 资源类型 -->
          <div class="form-group">
            <label class="form-label required">资源类型</label>
            <select v-model="formData.type" class="form-select" :class="{ error: formErrors.type }">
              <option value="">请选择资源类型</option>
              <option v-for="type in resourceTypes" :key="type.value" :value="type.value">
                {{ type.label }}
              </option>
            </select>
            <div v-if="formErrors.type" class="form-error">{{ formErrors.type }}</div>
          </div>
        </div>

        <!-- 资源状态（编辑模式显示） -->
        <div v-if="isEditMode" class="form-group">
          <label class="form-label required">资源状态</label>
          <select
            v-model="formData.status"
            class="form-select"
            :class="{ error: formErrors.status }"
          >
            <option value="">请选择资源状态</option>
            <option v-for="status in statusOptions" :key="status.value" :value="status.value">
              {{ status.label }}
            </option>
          </select>
          <div v-if="formErrors.status" class="form-error">{{ formErrors.status }}</div>
        </div>

        <!-- 资源描述 -->
        <div class="form-group">
          <label class="form-label required">资源描述</label>
          <textarea
            v-model="formData.description"
            class="form-textarea"
            :class="{ error: formErrors.description }"
            placeholder="请详细描述这个资源的功能、用途、特点等..."
            rows="4"
            maxlength="1000"
          ></textarea>
          <div class="char-count">{{ formData.description.length }}/1000</div>
          <div v-if="formErrors.description" class="form-error">{{ formErrors.description }}</div>
        </div>

        <!-- 资源标签 -->
        <div class="form-group">
          <label class="form-label">
            <FontAwesomeIcon :icon="['fas', 'tags']" class="mr-2" />
            资源标签
          </label>
          <div class="tags-input-container">
            <div class="tags-display">
              <span v-for="(tag, index) in selectedTag1s" :key="tag.id" class="tag tag-resource">
                {{ tag.value }}
                <button @click="removeTag1(index)" class="tag-remove">
                  <FontAwesomeIcon :icon="['fas', 'times']" />
                </button>
              </span>
              <input
                type="text"
                :value="tag1Input"
                @input="handleTag1Input($event.target.value)"
                class="tag-input"
                placeholder="搜索资源相关标签..."
                @focus="tag1Input && tag1Input.length >= 2 && (showTag1Suggestions = true)"
                @blur="hideTag1SuggestionsDelayed"
              />
            </div>

            <!-- 资源标签建议 -->
            <div
              v-if="showTag1Suggestions && (tag1Suggestions.length > 0 || tag1SuggestionsLoading)"
              class="tag-suggestions"
            >
              <div v-if="tag1SuggestionsLoading" class="suggestion-loading">
                <FontAwesomeIcon :icon="['fas', 'spinner']" spin class="mr-2" />
                搜索标签中...
              </div>

              <button
                v-for="suggestion in tag1Suggestions"
                :key="suggestion.id"
                @click="addSuggestedTag1(suggestion)"
                class="tag-suggestion"
              >
                {{ suggestion.value }}
              </button>

              <div
                v-if="!tag1SuggestionsLoading && tag1Suggestions.length === 0"
                class="no-suggestions"
              >
                暂无相关标签建议
              </div>
            </div>
          </div>
        </div>

        <!-- 技能/岗位标签 -->
        <div class="form-group">
          <label class="form-label">
            <FontAwesomeIcon :icon="['fas', 'briefcase']" class="mr-2" />
            技能/岗位标签
          </label>
          <div class="tags-input-container">
            <div class="tags-display">
              <span v-for="(tag, index) in selectedTag2s" :key="tag.id" class="tag tag-skill">
                {{ tag.post }}
                <button @click="removeTag2(index)" class="tag-remove">
                  <FontAwesomeIcon :icon="['fas', 'times']" />
                </button>
              </span>
              <input
                type="text"
                :value="tag2Input"
                @input="handleTag2Input($event.target.value)"
                class="tag-input"
                placeholder="搜索技能或岗位标签..."
                @focus="tag2Input && tag2Input.length >= 2 && (showTag2Suggestions = true)"
                @blur="hideTag2SuggestionsDelayed"
              />
            </div>

            <div
              v-if="showTag2Suggestions && (tag2Suggestions.length > 0 || tag2SuggestionsLoading)"
              class="tag-suggestions"
            >
              <div v-if="tag2SuggestionsLoading" class="suggestion-loading">
                <FontAwesomeIcon :icon="['fas', 'spinner']" spin class="mr-2" />
                搜索标签中...
              </div>

              <button
                v-for="suggestion in tag2Suggestions"
                :key="suggestion.id"
                @click="addSuggestedTag2(suggestion)"
                class="tag-suggestion"
              >
                <div class="skill-tag-content">
                  <div class="skill-post">{{ suggestion.post }}</div>
                  <div class="skill-details">
                    {{ suggestion.category }} - {{ suggestion.subcategory }} -
                    {{ suggestion.specialty }}
                  </div>
                </div>
              </button>

              <div
                v-if="!tag2SuggestionsLoading && tag2Suggestions.length === 0"
                class="no-suggestions"
              >
                暂无相关标签建议
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 文件管理 -->
      <div class="form-section">
        <h2 class="section-title">
          文件管理
          <span v-if="!isEditMode" class="required-mark">*</span>
        </h2>

        <!-- 已存在的文件（编辑模式） -->
        <div v-if="isEditMode && existingFiles.length > 0" class="existing-files-section">
          <h3 class="subsection-title">
            <FontAwesomeIcon :icon="['fas', 'file']" class="mr-2" />
            当前文件 ({{ existingFiles.length }})
          </h3>

          <div class="file-list existing-files">
            <div class="files">
              <div v-for="file in existingFiles" :key="file.id" class="file-item existing-file">
                <div class="file-info">
                  <div class="file-icon">
                    <FontAwesomeIcon :icon="getFileIcon(file.name)" class="file-icon-inner" />
                  </div>
                  <div class="file-details">
                    <div class="file-name">{{ file.name }}</div>
                    <div class="file-meta">
                      {{ formatFileSize(file.size) }} •
                      {{ formatDate(file.created_at) }}
                    </div>
                  </div>
                </div>

                <div class="file-actions">
                  <a :href="file.url" target="_blank" class="action-btn view" title="查看/下载文件">
                    <FontAwesomeIcon :icon="['fas', 'download']" />
                  </a>
                  <button
                    @click="deleteExistingFile(file)"
                    class="action-btn delete"
                    title="删除文件"
                    :disabled="deletingFileIds.has(file.id)"
                  >
                    <FontAwesomeIcon
                      :icon="deletingFileIds.has(file.id) ? ['fas', 'spinner'] : ['fas', 'trash']"
                      :spin="deletingFileIds.has(file.id)"
                    />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 新文件上传区域 -->
        <div class="upload-section">
          <h3 class="subsection-title">
            <FontAwesomeIcon :icon="['fas', 'upload']" class="mr-2" />
            {{ isEditMode ? '上传新文件' : '上传文件' }}
            <span v-if="!isEditMode" class="required-mark">*</span>
          </h3>

          <!-- 上传区域 -->
          <div
            class="upload-area"
            :class="{ 'drag-over': dragOver, error: formErrors.files }"
            @dragover="handleDragOver"
            @dragleave="handleDragLeave"
            @drop="handleDrop"
          >
            <div class="upload-content">
              <FontAwesomeIcon :icon="['fas', 'upload']" class="upload-icon" />
              <h4>拖拽文件到这里</h4>
              <p>或者点击选择文件：</p>
              <div class="upload-buttons">
                <button type="button" class="upload-btn" @click="$refs.fileInput.click()">
                  <FontAwesomeIcon :icon="['fas', 'file']" class="mr-2" />
                  选择文件
                </button>
              </div>
              <p class="upload-tip">支持多个文件同时上传</p>
            </div>

            <input
              ref="fileInput"
              type="file"
              multiple
              @change="handleFileInput"
              style="display: none"
            />
          </div>
          <div v-if="formErrors.files" class="form-error">{{ formErrors.files }}</div>

          <!-- 新选择的文件列表 -->
          <div v-if="fileList.length > 0" class="file-list new-files">
            <div class="file-list-header">
              <h4>待上传文件 ({{ fileList.length }})</h4>
              <button
                v-if="isEditMode"
                class="upload-new-files-btn"
                @click="uploadAndRefresh"
                :disabled="fileList.length === 0"
              >
                <FontAwesomeIcon :icon="['fas', 'upload']" class="mr-2" />
                上传这些文件
              </button>
            </div>
            <div class="files">
              <div v-for="file in fileList" :key="file.id" class="file-item new-file">
                <div class="file-info">
                  <div class="file-icon">
                    <FontAwesomeIcon :icon="getFileIcon(file.name)" class="file-icon-inner" />
                  </div>
                  <div class="file-details">
                    <div class="file-name">{{ file.name }}</div>
                    <div class="file-meta">
                      {{ formatFileSize(file.size) }}
                    </div>
                  </div>
                </div>

                <div class="file-actions">
                  <button @click="removeFile(file.id)" class="action-btn delete" title="移除文件">
                    <FontAwesomeIcon :icon="['fas', 'trash']" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.resource-editor {
  min-height: 100vh;
  background-color: #f9fafb;
}

.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;

  .loading-icon {
    font-size: 2rem;
    color: #3b82f6;
    margin-bottom: 1rem;
  }

  p {
    color: #6b7280;
    font-size: 1rem;
  }
}

.edit-info-banner {
  background: linear-gradient(135deg, #ebf8ff 0%, #dbeafe 100%);
  border: 1px solid #bfdbfe;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 2rem;
  display: flex;
  gap: 1rem;

  .info-icon {
    color: #3b82f6;
    font-size: 1.25rem;
    margin-top: 0.125rem;
    flex-shrink: 0;
  }

  .info-content {
    flex: 1;

    h4 {
      color: #1e40af;
      font-weight: 600;
      margin: 0 0 0.5rem 0;
      font-size: 1rem;
    }

    p {
      color: #1e40af;
      margin: 0 0 0.5rem 0;
      font-size: 0.875rem;
    }

    ul {
      margin: 0;
      padding-left: 1.25rem;
      color: #1e40af;
      font-size: 0.875rem;

      li {
        margin-bottom: 0.25rem;

        strong {
          font-weight: 600;
        }
      }
    }
  }
}

.editor-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 1rem 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  position: sticky;
  top: 0;
  z-index: 10;

  .header-left {
    display: flex;
    align-items: center;
    gap: 1rem;

    .btn-back {
      display: flex;
      align-items: center;
      padding: 0.5rem 1rem;
      background: none;
      border: 1px solid #d1d5db;
      border-radius: 0.375rem;
      color: #374151;
      cursor: pointer;
      transition: all 0.2s;

      &:hover {
        background-color: #f9fafb;
        border-color: #9ca3af;
      }
    }

    .page-title {
      font-size: 1.5rem;
      font-weight: 600;
      color: #111827;
      margin: 0;
    }
  }

  .header-actions {
    display: flex;
    gap: 1rem;

    .btn-secondary {
      background-color: #f3f4f6;
      color: #374151;
      padding: 0.75rem 1.5rem;
      border: 1px solid #d1d5db;
      border-radius: 0.375rem;
      font-weight: 500;
      cursor: pointer;
      transition: all 0.2s;

      &:hover:not(:disabled) {
        background-color: #e5e7eb;
        border-color: #9ca3af;
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }

    .btn-primary {
      background-color: #3b82f6;
      color: white;
      padding: 0.75rem 1.5rem;
      border: none;
      border-radius: 0.375rem;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover:not(:disabled) {
        background-color: #2563eb;
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }
  }
}

.editor-content {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.form-section {
  background: white;
  border-radius: 0.75rem;
  padding: 2rem;
  margin-bottom: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);

  .section-title {
    font-size: 1.25rem;
    font-weight: 600;
    color: #111827;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;

    .required-mark {
      color: #ef4444;
    }

    .optional-mark {
      color: #6b7280;
      font-size: 0.875rem;
      font-weight: 400;
    }
  }

  .subsection-title {
    font-size: 1rem;
    font-weight: 600;
    color: #374151;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;

    .required-mark {
      color: #ef4444;
    }
  }
}

.existing-files-section {
  margin-bottom: 2rem;
  padding-bottom: 2rem;
  border-bottom: 1px solid #e5e7eb;
}

.upload-section {
  h4 {
    margin-bottom: 0.5rem;
  }
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1.5rem;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.form-group {
  display: flex;
  flex-direction: column;

  .form-label {
    font-weight: 500;
    color: #374151;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.25rem;

    &.required::after {
      content: '*';
      color: #ef4444;
    }
  }

  .form-input,
  .form-select,
  .form-textarea {
    padding: 0.75rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    font-size: 0.875rem;
    transition:
      border-color 0.2s,
      box-shadow 0.2s;

    &:focus {
      outline: none;
      border-color: #3b82f6;
      box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    &.error {
      border-color: #ef4444;
      box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
    }
  }

  .form-textarea {
    resize: vertical;
    min-height: 100px;
  }

  .char-count {
    align-self: flex-end;
    font-size: 0.75rem;
    color: #6b7280;
    margin-top: 0.25rem;
  }

  .form-error {
    color: #ef4444;
    font-size: 0.75rem;
    margin-top: 0.25rem;
  }
}

.tags-input-container {
  position: relative;
  margin-bottom: 1rem;

  .tags-display {
    min-height: 2.5rem;
    padding: 0.5rem;
    border: 1px solid #d1d5db;
    border-radius: 0.375rem;
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    align-items: center;

    .tag {
      padding: 0.25rem 0.5rem;
      border-radius: 0.25rem;
      font-size: 0.75rem;
      display: flex;
      align-items: center;
      gap: 0.25rem;

      &.tag-resource {
        background-color: #3b82f6;
        color: white;
      }

      &.tag-skill {
        background-color: #10b981;
        color: white;
      }

      .tag-remove {
        background: none;
        border: none;
        color: inherit;
        cursor: pointer;
        padding: 0;
        display: flex;
        align-items: center;
        opacity: 0.8;

        &:hover {
          opacity: 1;
        }
      }
    }

    .tag-input {
      border: none;
      outline: none;
      flex: 1;
      min-width: 150px;
      padding: 0.25rem;
    }
  }

  .tag-suggestions {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #d1d5db;
    border-top: none;
    border-radius: 0 0 0.375rem 0.375rem;
    max-height: 200px;
    overflow-y: auto;
    z-index: 10;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);

    .tag-suggestion {
      display: block;
      width: 100%;
      padding: 0.5rem;
      text-align: left;
      background: none;
      border: none;
      cursor: pointer;
      font-size: 0.875rem;
      transition: background-color 0.2s;

      &:hover {
        background-color: #f3f4f6;
      }

      .skill-tag-content {
        .skill-post {
          font-weight: 500;
          color: #111827;
        }

        .skill-details {
          font-size: 0.75rem;
          color: #6b7280;
          margin-top: 0.125rem;
        }
      }
    }
  }
}

.suggestion-loading {
  padding: 0.75rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.no-suggestions {
  padding: 0.75rem;
  text-align: center;
  color: #9ca3af;
  font-size: 0.875rem;
  font-style: italic;
}

.upload-area {
  border: 2px dashed #d1d5db;
  border-radius: 0.75rem;
  padding: 2.5rem;
  text-align: center;
  transition: all 0.3s;
  cursor: pointer;
  margin-bottom: 1.5rem;

  &:hover,
  &.drag-over {
    border-color: #3b82f6;
    background-color: #f0f9ff;
  }

  &.error {
    border-color: #ef4444;
    background-color: #fef2f2;
  }

  .upload-content {
    .upload-icon {
      font-size: 2.5rem;
      color: #9ca3af;
      margin-bottom: 1rem;
    }

    h4 {
      font-size: 1rem;
      font-weight: 500;
      color: #374151;
      margin-bottom: 0.5rem;
    }

    p {
      color: #6b7280;
      margin-bottom: 0.5rem;
      font-size: 0.875rem;
    }

    .upload-buttons {
      display: flex;
      justify-content: center;
      margin: 1rem 0;

      .upload-btn {
        display: flex;
        align-items: center;
        padding: 0.75rem 1.5rem;
        background-color: #3b82f6;
        color: white;
        border: none;
        border-radius: 0.375rem;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s;
        font-size: 0.875rem;

        &:hover {
          background-color: #2563eb;
          transform: translateY(-1px);
        }

        &:active {
          transform: translateY(0);
        }
      }
    }

    .upload-tip {
      font-size: 0.75rem;
      color: #9ca3af;
    }
  }
}

.file-list {
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;

  &.existing-files {
    border-color: #d1d5db;
  }

  &.new-files {
    border-color: #3b82f6;
    border-style: dashed;
  }

  .file-list-header {
    background-color: #f9fafb;
    padding: 1rem;
    border-bottom: 1px solid #e5e7eb;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h4 {
      margin: 0;
      font-size: 1rem;
      font-weight: 500;
      color: #374151;
    }

    .upload-new-files-btn {
      background-color: #3b82f6;
      color: white;
      padding: 0.5rem 1rem;
      border: none;
      border-radius: 0.375rem;
      font-size: 0.875rem;
      font-weight: 500;
      cursor: pointer;
      transition: background-color 0.2s;

      &:hover:not(:disabled) {
        background-color: #2563eb;
      }

      &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
      }
    }
  }

  .files {
    max-height: 400px;
    overflow-y: auto;

    .file-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.75rem 1rem;
      border-bottom: 1px solid #f3f4f6;
      transition: background-color 0.2s;

      &:hover {
        background-color: #f9fafb;
      }

      &:last-child {
        border-bottom: none;
      }

      &.existing-file {
        background-color: #fefefe;
      }

      &.new-file {
        background-color: #f8fafc;
      }

      .file-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex: 1;

        .file-icon {
          width: 2rem;
          height: 2rem;
          display: flex;
          align-items: center;
          justify-content: center;

          .file-icon-inner {
            color: #6b7280;
            font-size: 1.125rem;
          }
        }

        .file-details {
          flex: 1;

          .file-name {
            font-weight: 500;
            color: #111827;
            margin-bottom: 0.125rem;
            word-break: break-all;
          }

          .file-meta {
            font-size: 0.75rem;
            color: #6b7280;
          }
        }
      }

      .file-actions {
        display: flex;
        gap: 0.5rem;

        .action-btn {
          width: 2rem;
          height: 2rem;
          border: none;
          border-radius: 0.25rem;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s;
          text-decoration: none;

          &.view {
            background-color: #eff6ff;
            color: #2563eb;

            &:hover {
              background-color: #dbeafe;
            }
          }

          &.delete {
            background-color: #fef2f2;
            color: #dc2626;

            &:hover:not(:disabled) {
              background-color: #fee2e2;
            }

            &:disabled {
              opacity: 0.6;
              cursor: not-allowed;
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .editor-header {
    padding: 1rem;
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;

    .header-left {
      justify-content: space-between;
    }

    .header-actions {
      flex-direction: column;
      gap: 0.5rem;
    }
  }

  .editor-content {
    padding: 1rem;
  }

  .form-section {
    padding: 1.5rem;
  }

  .upload-area {
    padding: 1.5rem 1rem;

    .upload-content {
      .upload-icon {
        font-size: 2rem;
      }

      h4 {
        font-size: 0.875rem;
      }
    }
  }

  .edit-info-banner {
    padding: 1rem;
    flex-direction: column;
    gap: 0.75rem;

    .info-icon {
      align-self: flex-start;
    }
  }
}
</style>
