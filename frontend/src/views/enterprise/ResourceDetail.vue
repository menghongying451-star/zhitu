<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { resourcesService } from '@/api'
import {
  faArrowLeft,
  faDownload,
  faEye,
  faFolder,
  faFile,
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
  faChevronRight,
  faChevronDown,
  faCalendarAlt,
  faUser,
  faEdit,
  faExclamationTriangle,
  faSpinner,
  faCopy,
  faCheckCircle,
  faShare,
  faHistory,
  faCubes,
  faTimes,
  faCheck,
  faExternalLinkAlt,
  faKey
} from '@fortawesome/free-solid-svg-icons'

library.add(
  faArrowLeft,
  faDownload,
  faEye,
  faFolder,
  faFile,
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
  faChevronRight,
  faChevronDown,
  faCalendarAlt,
  faUser,
  faEdit,
  faExclamationTriangle,
  faSpinner,
  faCopy,
  faCheckCircle,
  faShare,
  faHistory,
  faCubes,
  faTimes,
  faCheck,
  faExternalLinkAlt,
  faKey
)

// 路由相关
const route = useRoute()
const router = useRouter()

// 资源ID
const resourceId = computed(() => route.params.id)

// 资源数据
const resourceData = reactive({
  id: '',
  title: '',
  description: '',
  type: '',
  tag1: [],
  tag2: [],
  files: [],
  status: '',
  created_at: '',
  create_person: null,
  create_person_name: '',
  updated_at: '',
  update_person: null,
  update_person_name: '',
  downloads: '0',
  views: '0'
})

// 状态管理
const loading = ref(true)
const notFound = ref(false)
const error = ref('')
const downloading = ref(false)

// 页面顶部引用
const pageTopRef = ref(null)

// 资源类型选项
const resourceTypes = {
  code: { label: '代码', icon: ['fas', 'code'], color: '#165DFF' },
  dataset: { label: '数据集', icon: ['fas', 'database'], color: '#36CFC9' },
  document: { label: '文档', icon: ['fas', 'file-alt'], color: '#52C41A' },
  course: { label: '课程', icon: ['fas', 'graduation-cap'], color: '#FAAD14' },
  video: { label: '视频', icon: ['fas', 'video'], color: '#FF4D4F' },
  tool: { label: '工具', icon: ['fas', 'wrench'], color: '#86909C' }
}

// 获取资源类型信息
const resourceTypeInfo = computed(() => {
  return (
    resourceTypes[resourceData.type] || { label: '未知', icon: ['fas', 'file'], color: '#86909C' }
  )
})

// 合并所有标签
const allTags = computed(() => {
  const tags = []

  // 添加 tag1 中的标签
  if (resourceData.tag1 && Array.isArray(resourceData.tag1)) {
    tags.push(...resourceData.tag1.map((tag) => tag.name))
  }

  // 添加 tag2 中的标签
  if (resourceData.tag2 && Array.isArray(resourceData.tag2)) {
    tags.push(...resourceData.tag2.map((tag) => tag.name))
  }

  return tags
})

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
    jfif: ['fas', 'image'], // 新增 JFIF 格式

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
  if (bytes === null) return '未知大小'
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

// 文件夹操作 - 已删除

// 下载单个文件
const downloadFile = async (file) => {
  // 使用文件的download_url或url字段
  const downloadUrl = file.download_url || file.url
  if (!downloadUrl) {
    ElMessage.error('文件下载链接不可用')
    return
  }

  try {
    ElMessage.info('正在准备下载...')

    // 使用fetch获取文件，然后创建blob下载，这样可以强制下载任何类型的文件
    const response = await fetch(downloadUrl)

    if (!response.ok) {
      throw new Error('下载失败')
    }

    const blob = await response.blob()

    // 创建下载链接
    const downloadLink = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = downloadLink
    link.download = file.name
    link.style.display = 'none'

    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    // 清理内存
    window.URL.revokeObjectURL(downloadLink)

    ElMessage.success('文件下载已开始')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('文件下载失败，请重试')
  }
}

const downloadAllFiles = async () => {
  if (resourceData.files.length === 0) {
    ElMessage.warning('没有可下载的文件')
    return
  }

  try {
    downloading.value = true
    ElMessage.info('正在获取下载信息，请稍候...')

    // 调用获取下载信息的API
    const response = await resourcesService.downloadResource(resourceData.id)

    if (response?.data?.files && Array.isArray(response.data.files)) {
      const files = response.data.files

      ElMessage.success(`准备下载 ${files.length} 个文件`)

      // 使用fetch + Blob方式下载每个文件
      const downloadPromises = files.map(async (file, index) => {
        // 为每个文件添加延迟，避免同时发起太多请求
        await new Promise((resolve) => setTimeout(resolve, index * 300))

        try {
          const fileResponse = await fetch(file.download_url)

          if (!fileResponse.ok) {
            throw new Error(`下载 ${file.name} 失败`)
          }

          const blob = await fileResponse.blob()

          // 创建下载链接
          const downloadLink = window.URL.createObjectURL(blob)
          const link = document.createElement('a')
          link.href = downloadLink
          link.download = file.name
          link.style.display = 'none'

          document.body.appendChild(link)
          link.click()
          document.body.removeChild(link)

          // 清理内存
          window.URL.revokeObjectURL(downloadLink)

          console.log(`${file.name} 下载完成`)
        } catch (error) {
          console.error(`下载 ${file.name} 失败:`, error)
          ElMessage.error(`下载 ${file.name} 失败`)
        }
      })

      // 等待所有下载完成
      await Promise.all(downloadPromises)
      ElMessage.success('所有文件下载已完成')
    } else {
      throw new Error('服务器返回的下载信息格式错误')
    }
  } catch (error) {
    console.error('获取下载信息失败:', error)

    // 根据错误类型显示不同的错误信息
    if (error.response) {
      const status = error.response.status
      const message = error.response.data?.message || error.response.data?.error

      switch (status) {
        case 404:
          ElMessage.error('资源不存在或已被删除')
          break
        case 403:
          ElMessage.error('没有权限下载此资源')
          break
        case 500:
          ElMessage.error('服务器内部错误，请稍后重试')
          break
        case 503:
          ElMessage.error('服务暂时不可用，请稍后重试')
          break
        default:
          ElMessage.error(message || `获取下载信息失败 (${status})`)
      }
    } else if (error.code === 'NETWORK_ERROR' || error.message.includes('Network')) {
      ElMessage.error('网络连接失败，请检查网络后重试')
    } else {
      ElMessage.error(error.message || '获取下载信息失败，请重试')
    }
  } finally {
    downloading.value = false
  }
}

// 复制下载链接
const copyDownloadLink = async (file) => {
  try {
    const downloadUrl = file.download_url || file.url
    if (!downloadUrl) {
      ElMessage.error('文件下载链接不可用')
      return
    }

    await navigator.clipboard.writeText(downloadUrl)
    ElMessage.success('下载链接已复制到剪贴板')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败')
  }
}

// 打开网盘链接
const openCloudLink = (file) => {
  const cloudUrl = file.cloud_link_url || file.url
  if (!cloudUrl) {
    ElMessage.error('网盘链接不可用')
    return
  }
  window.open(cloudUrl, '_blank')
}

// 复制网盘提取码
const copyCloudPassword = async (file) => {
  try {
    if (!file.cloud_password) {
      ElMessage.error('提取码不可用')
      return
    }
    await navigator.clipboard.writeText(file.cloud_password)
    ElMessage.success('提取码已复制到剪贴板')
  } catch (error) {
    console.error('复制提取码失败:', error)
    ElMessage.error('复制提取码失败')
  }
}

// 编辑资源
const editResource = () => {
  router.push(`/enterprise/resource/edit/${resourceData.id}`)
}

// 返回资源列表
const goBack = () => {
  router.back()
}

// 加载资源数据
const loadResourceData = async (id) => {
  try {
    loading.value = true
    error.value = ''

    const response = await resourcesService.getResourceDetail(id)

    if (response?.data) {
      // 更新数据结构以匹配新的API响应
      Object.assign(resourceData, {
        ...response.data,
        // 确保标签数组正确初始化
        tag1: response.data.tag1 || [],
        tag2: response.data.tag2 || [],
        // 确保用户信息正确处理
        create_person_name: response.data.create_person_name || '未知用户',
        update_person_name: response.data.update_person_name || '未知用户'
      })
    } else {
      notFound.value = true
    }
  } catch (err) {
    console.error('加载资源详情失败:', err)
    error.value = '加载资源详情失败'
    notFound.value = true
  } finally {
    loading.value = false
  }
}

// 增加浏览量
const incrementViews = async (id) => {
  try {
    // 这里可以调用增加浏览量的API
    // await resourcesService.incrementViews(id)
  } catch (error) {
    console.error('增加浏览量失败:', error)
  }
}

// 生命周期
onMounted(async () => {
  if (!resourceId.value) {
    router.push('/enterprise/resource-management')
    return
  }

  await loadResourceData(resourceId.value)

  // 增加浏览量
  if (!notFound.value && !error.value) {
    incrementViews(resourceId.value)
  }

  // 确保DOM完全渲染后滚动到页面顶部
  await nextTick()
  if (pageTopRef.value) {
    pageTopRef.value.scrollIntoView({
      behavior: 'instant',
      block: 'start'
    })
  }
})
</script>

<template>
  <div class="resource-detail" ref="pageTopRef">
    <!-- 加载状态 -->
    <div v-if="loading" class="loading-screen">
      <div class="loading-content">
        <div class="loading-spinner"></div>
        <p>加载资源详情中...</p>
      </div>
    </div>

    <!-- 404状态 -->
    <div v-else-if="notFound || error" class="not-found-screen">
      <div class="not-found-content">
        <FontAwesomeIcon :icon="['fas', 'exclamation-triangle']" class="not-found-icon" />
        <h2>{{ error || '资源不存在' }}</h2>
        <p>{{ error ? '加载资源详情时出现错误' : '您要查看的资源不存在或已被删除' }}</p>
        <button @click="goBack" class="btn-primary">
          <FontAwesomeIcon :icon="['fas', 'arrow-left']" class="mr-2" />
          返回资源列表
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
              <a href="/enterprise/resource-management" class="breadcrumb-link">资源管理</a>
              <FontAwesomeIcon :icon="['fas', 'chevron-right']" class="breadcrumb-separator" />
              <span class="breadcrumb-current">{{ resourceData.title }}</span>
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
                  <h1 class="page-title">{{ resourceData.title }}</h1>
                  <span class="resource-badge" :style="{ backgroundColor: resourceTypeInfo.color }">
                    {{ resourceTypeInfo.label }}
                  </span>
                </div>
                <p class="page-subtitle">
                  最后更新于 {{ formatDateTime(resourceData.updated_at) }} | 由
                  {{ resourceData.create_person_name }} 上传
                </p>
                <!-- 统计信息 -->
                <div class="stats-info">
                  <span class="stat-item">
                    <FontAwesomeIcon :icon="['fas', 'download']" class="stat-icon" />
                    {{ formatNumber(resourceData.downloads) }} 下载
                  </span>
                  <span class="stat-item">
                    <FontAwesomeIcon :icon="['fas', 'eye']" class="stat-icon" />
                    {{ formatNumber(resourceData.views) }} 浏览
                  </span>
                  <span class="stat-item">
                    <FontAwesomeIcon :icon="['fas', 'file']" class="stat-icon" />
                    {{ resourceData.files.length }} 文件
                  </span>
                  <span class="stat-item">
                    <FontAwesomeIcon :icon="['fas', 'check-circle']" class="stat-icon" />
                    {{ resourceData.status === 'published' ? '已发布' : '草稿' }}
                  </span>
                </div>
              </div>
            </div>

            <div class="page-header-actions">
              <button @click="editResource" class="action-btn secondary">
                <FontAwesomeIcon :icon="['fas', 'edit']" class="btn-icon" />
                <span>编辑</span>
              </button>
              <button @click="downloadAllFiles" class="action-btn primary" :disabled="downloading">
                <FontAwesomeIcon
                  :icon="downloading ? ['fas', 'spinner'] : ['fas', 'download']"
                  class="btn-icon"
                  :class="{ 'fa-spin': downloading }"
                />
                <span>{{ downloading ? '准备中...' : '下载全部' }}</span>
              </button>
            </div>
          </div>

          <!-- 内容网格 -->
          <div class="content-grid">
            <!-- 左侧主要内容 -->
            <div class="main-column">
              <!-- 资源描述 -->
              <div class="description-section">
                <h2 class="section-title">资源描述</h2>
                <div class="description-content">
                  {{ resourceData.description }}
                </div>
              </div>

              <!-- 文件列表 -->
              <div class="files-section" v-if="resourceData.files.length > 0">
                <div class="section-header">
                  <h2 class="section-title">资源文件</h2>
                  <div class="file-stats">共 {{ resourceData.files.length }} 个文件</div>
                </div>

                <div class="file-list">
                  <div v-for="file in resourceData.files" :key="file.id" class="file-item">
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
                      <!-- 网盘链接文件显示打开按钮 -->
                      <template v-if="file.is_cloud_link">
                        <button
                          @click="openCloudLink(file)"
                          class="file-action-btn open"
                          title="打开网盘链接"
                        >
                          <FontAwesomeIcon :icon="['fas', 'external-link-alt']" />
                          <span>打开链接</span>
                        </button>
                        <button
                          v-if="file.cloud_password"
                          @click="copyCloudPassword(file)"
                          class="file-action-btn copy"
                          title="复制提取码"
                        >
                          <FontAwesomeIcon :icon="['fas', 'key']" />
                          <span>复制提取码</span>
                        </button>
                      </template>
                      <!-- 普通文件显示下载和复制链接按钮 -->
                      <template v-else>
                        <button
                          @click="downloadFile(file)"
                          class="file-action-btn download"
                          title="下载文件"
                        >
                          <FontAwesomeIcon :icon="['fas', 'download']" />
                          <span>下载</span>
                        </button>
                        <button
                          @click="copyDownloadLink(file)"
                          class="file-action-btn copy"
                          title="复制下载链接"
                        >
                          <FontAwesomeIcon :icon="['fas', 'copy']" />
                          <span>复制链接</span>
                        </button>
                      </template>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 空状态 -->
              <div v-else class="empty-files">
                <FontAwesomeIcon :icon="['fas', 'folder']" class="empty-icon" />
                <h3>暂无文件</h3>
                <p>该资源暂时没有上传任何文件</p>
              </div>
            </div>

            <!-- 右侧侧边栏 -->
            <div class="sidebar-column">
              <!-- 资源信息 -->
              <div class="info-card">
                <h2 class="card-title">资源信息</h2>

                <div class="info-list">
                  <div class="info-item">
                    <span class="info-label">资源类型</span>
                    <span class="info-value">{{ resourceTypeInfo.label }}</span>
                  </div>

                  <div class="info-item">
                    <span class="info-label">文件数量</span>
                    <span class="info-value">{{ resourceData.files.length }}个</span>
                  </div>

                  <div class="info-item">
                    <span class="info-label">上传时间</span>
                    <span class="info-value">{{ formatDateTime(resourceData.created_at) }}</span>
                  </div>

                  <div class="info-item" v-if="resourceData.updated_at">
                    <span class="info-label">最后更新</span>
                    <span class="info-value">{{ formatDateTime(resourceData.updated_at) }}</span>
                  </div>

                  <div class="info-item">
                    <span class="info-label">上传人</span>
                    <span class="info-value">{{ resourceData.create_person_name }}</span>
                  </div>

                  <div
                    class="info-item"
                    v-if="
                      resourceData.update_person_name &&
                      resourceData.update_person_name !== resourceData.create_person_name
                    "
                  >
                    <span class="info-label">更新人</span>
                    <span class="info-value">{{ resourceData.update_person_name }}</span>
                  </div>
                </div>
              </div>

              <!-- 标签 -->
              <div class="tags-card" v-if="allTags.length > 0">
                <div class="card-header">
                  <h2 class="card-title">标签</h2>
                </div>

                <div class="tags-display">
                  <span v-for="tag in allTags" :key="tag" class="tag">
                    {{ tag }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- 页脚 -->
      <footer class="footer">
        <div class="footer-container">
          <div class="footer-left">
            <div class="footer-text">© 2026 知途团队</div>
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

.resource-detail {
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

// 顶部导航栏
.header {
  background: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 30;

  .header-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
  }

  .header-left {
    display: flex;
    align-items: center;

    .brand {
      display: flex;
      align-items: center;
      gap: 0.5rem;

      .brand-icon {
        width: 40px;
        height: 40px;
        border-radius: 8px;
        background-color: #165dff;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 1.25rem;
      }

      .brand-text {
        font-size: 1.25rem;
        font-weight: 600;
        color: #272e3b;
      }
    }
  }

  .header-right {
    display: flex;
    align-items: center;
    gap: 1.5rem;

    .notification-btn {
      position: relative;
      background: none;
      border: none;
      color: #86909c;
      font-size: 1.25rem;
      cursor: pointer;
      transition: color 0.3s;

      &:hover {
        color: #165dff;
      }

      .notification-badge {
        position: absolute;
        top: -4px;
        right: -4px;
        width: 16px;
        height: 16px;
        background-color: #ff4d4f;
        border-radius: 50%;
        color: white;
        font-size: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }

    .user-info {
      display: flex;
      align-items: center;
      gap: 0.5rem;

      .user-avatar {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        object-fit: cover;
      }

      .user-name {
        font-size: 0.875rem;
        font-weight: 500;
        color: #272e3b;
      }
    }
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
    gap: 1rem;
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

        .page-title {
          font-size: 2rem;
          font-weight: 600;
          color: #272e3b;
          margin: 0;
          line-height: 1.2;
          word-break: break-word;
        }

        .resource-badge {
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
      }

      // 新增统计信息样式
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

      &.small {
        padding: 0.5rem;
        font-size: 0.75rem;

        .btn-icon {
          margin-right: 0;
        }
      }
    }
  }
}

// 内容网格
.content-grid {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: 1.5rem;

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

// 卡片样式
.description-section,
.files-section,
.info-card,
.tags-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 1.5rem;

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
  }
}

// 资源描述
.description-section {
  .description-content {
    line-height: 1.6;
    color: #4e5969;
    white-space: pre-wrap;
    word-break: break-word;
  }
}

// 文件列表
.files-section {
  .section-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1rem;

    .file-stats {
      font-size: 0.875rem;
      color: #86909c;
    }
  }

  .file-list {
    border: 1px solid #e5e6eb;
    border-radius: 8px;
    overflow: hidden;
    max-height: 500px;
    overflow-y: auto;

    .file-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0.75rem 1rem;
      border-bottom: 1px solid #f5f7fa;
      transition: background-color 0.3s;

      &:last-child {
        border-bottom: none;
      }

      &:hover {
        background-color: #f5f7fa;
      }

      .file-info {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        flex: 1;

        .file-icon {
          width: 32px;
          height: 32px;
          display: flex;
          align-items: center;
          justify-content: center;

          .file-icon-inner {
            color: #86909c;
            font-size: 1.125rem;
          }
        }

        .file-details {
          flex: 1;

          .file-name {
            font-weight: 500;
            color: #272e3b;
            margin-bottom: 0.125rem;
          }

          .file-meta {
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

      .file-actions {
        display: flex;
        gap: 0.5rem;
      }
    }
  }
}

// 改进的文件操作按钮
.file-action-btn {
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

  &.copy {
    color: #52c41a;
    border-color: #52c41a;

    &:hover {
      background-color: #52c41a;
      color: white;
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(82, 196, 26, 0.3);
    }
  }

  &.open {
    color: #7546c9;
    border-color: #7546c9;

    &:hover {
      background-color: #7546c9;
      color: white;
      transform: translateY(-1px);
      box-shadow: 0 2px 4px rgba(117, 70, 201, 0.3);
    }
  }

  .fa-icon {
    font-size: 0.875rem;
  }
}

// 空状态
.empty-files {
  text-align: center;
  padding: 3rem;
  color: #86909c;

  .empty-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    opacity: 0.5;
  }

  h3 {
    font-size: 1.125rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
    color: #4e5969;
  }

  p {
    margin: 0;
  }
}

// 信息卡片
.info-card {
  .info-list {
    .info-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
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
      }

      .info-value {
        font-weight: 500;
        color: #272e3b;
        text-align: right;
      }

      .user-display {
        display: flex;
        align-items: center;
        gap: 0.5rem;

        .user-avatar-small {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          object-fit: cover;
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
    margin-bottom: 1rem;
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
      background-color: #165dff;
      color: white;
    }
  }
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

    .footer-right {
      display: flex;
      gap: 1.5rem;

      .footer-link {
        color: #86909c;
        text-decoration: none;
        font-size: 0.875rem;
        transition: color 0.3s;

        &:hover {
          color: #165dff;
        }
      }
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

// 中等屏幕适配 (平板等)
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
  .files-section,
  .info-card,
  .tags-card {
    padding: 1.25rem;
  }
}

// 小屏幕响应式设计
@media (max-width: 768px) {
  .header {
    .header-container {
      padding: 0 0.5rem;
      height: 56px;
    }

    .header-right {
      gap: 1rem;

      .user-name {
        display: none;
      }
    }
  }

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

  .description-section,
  .files-section,
  .info-card,
  .tags-card {
    padding: 1rem;
  }

  .file-action-btn {
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

    .footer-right {
      gap: 1rem;
    }
  }
}
</style>
