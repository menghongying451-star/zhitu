<script setup>
import { ref, onMounted, computed } from 'vue'
import { library } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faBell,
  faCheck,
  faEye,
  faCheckDouble,
  faEllipsisV,
  faUser,
  faClock,
  faTag,
  faInfoCircle
} from '@fortawesome/free-solid-svg-icons'
import { notificationService } from '@/api/'
import { useNotificationStore } from '@/stores'

const notificationStore = useNotificationStore()

library.add(
  faBell,
  faCheck,
  faEye,
  faCheckDouble,
  faEllipsisV,
  faUser,
  faClock,
  faTag,
  faInfoCircle
)

// 响应式数据
const loading = ref(false)
const selectedStatus = ref('all')
const selectedType = ref('all')
const selectedNotifications = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const showBatchActions = ref(false)

// 详情对话框相关
const showDetailDialog = ref(false)
const selectedNotification = ref(null)

// 通知数据
const notifications = ref([])
const notificationTypes = ref([])
const pagination = ref({
  current_page: 1,
  total_pages: 1,
  total_count: 0,
  page_size: 10
})
const unreadCount = ref(0)

// 通知状态选项
const statusOptions = [
  { label: '全部', value: 'all' },
  { label: '未读', value: 'unread' },
  { label: '已读', value: 'read' }
]

// 通知类型选项 - 动态从API获取
const typeOptions = computed(() => {
  const baseOptions = [{ label: '全部类型', value: 'all' }]
  const apiOptions = notificationTypes.value.map((type) => ({
    label: type.name,
    value: type.code
  }))
  return [...baseOptions, ...apiOptions]
})

// 统计数据
const stats = computed(() => {
  const total = pagination.value.total_count
  const unread = unreadCount.value
  const read = total - unread

  return { total, unread, read }
})

// 全选状态
const isAllSelected = computed(() => {
  return (
    notifications.value.length > 0 &&
    selectedNotifications.value.length === notifications.value.length
  )
})

const isIndeterminate = computed(() => {
  return (
    selectedNotifications.value.length > 0 &&
    selectedNotifications.value.length < notifications.value.length
  )
})

// 优先级标签映射
const priorityMap = computed(() => ({
  low: { label: '低', type: 'info' },
  normal: { label: '普通', type: '' },
  medium: { label: '中等', type: 'warning' },
  high: { label: '高', type: 'danger' },
  urgent: { label: '紧急', type: 'danger' }
}))

// API调用方法
const fetchNotificationTypes = async () => {
  try {
    const response = await notificationService.getNotificationTypes()
    if (response.status === 'success') {
      notificationTypes.value = response.data.results || []
    }
  } catch (error) {
    console.error('获取通知类型失败:', error)
    ElMessage.error(error.detail || '获取通知类型失败')
  }
}

const fetchNotifications = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    // 添加筛选参数
    if (selectedStatus.value === 'read') {
      params.is_read = 'true'
    } else if (selectedStatus.value === 'unread') {
      params.is_read = 'false'
    }

    if (selectedType.value !== 'all') {
      params.notification_type = selectedType.value
    }

    const response = await notificationService.getNotifications(params)

    if (response.status === 'success') {
      notifications.value = response.data.results || []
      pagination.value = response.data.pagination || {}
    }
  } catch (error) {
    console.error('获取通知列表失败:', error)
    ElMessage.error(error.detail || '获取通知列表失败')
  } finally {
    loading.value = false
  }
}

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

// 方法
const handleStatusChange = () => {
  currentPage.value = 1
  fetchNotifications()
}

const handleTypeChange = () => {
  currentPage.value = 1
  fetchNotifications()
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedNotifications.value = []
  } else {
    selectedNotifications.value = [...notifications.value.map((n) => n.id)]
  }
  showBatchActions.value = selectedNotifications.value.length > 0
}

const handleNotificationSelect = (notificationId, selected) => {
  if (selected) {
    selectedNotifications.value.push(notificationId)
  } else {
    const index = selectedNotifications.value.indexOf(notificationId)
    if (index > -1) {
      selectedNotifications.value.splice(index, 1)
    }
  }
  showBatchActions.value = selectedNotifications.value.length > 0
}

const markAsRead = async (notificationId) => {
  try {
    await notificationService.markNotificationAsRead(notificationId)
    // 更新本地数据
    const notification = notifications.value.find((n) => n.id === notificationId)
    if (notification) {
      notification.is_read = true
      notification.read_at = new Date().toISOString()
    }

    // 如果当前正在查看该通知的详情，也要更新详情中的数据
    if (selectedNotification.value && selectedNotification.value.id === notificationId) {
      selectedNotification.value.is_read = true
      selectedNotification.value.read_at = new Date().toISOString()
    }

    // 更新未读计数
    await fetchUnreadCount()
    ElMessage.success('通知已标记为已读')
  } catch (error) {
    console.error('标记通知为已读失败:', error)
    ElMessage.error(error.detail || '标记通知为已读失败')
  }
}

const viewNotificationDetail = async (notification) => {
  selectedNotification.value = { ...notification }
  showDetailDialog.value = true

  // 自动标记为已读
  if (!notification.is_read) {
    await markAsRead(notification.id)
  }
}

const closeDetailDialog = () => {
  showDetailDialog.value = false
  selectedNotification.value = null
}

// 批量操作
const batchMarkAsRead = async () => {
  try {
    const promises = selectedNotifications.value.map((id) =>
      notificationService.markNotificationAsRead(id)
    )
    await Promise.all(promises)

    // 更新本地数据
    selectedNotifications.value.forEach((id) => {
      const notification = notifications.value.find((n) => n.id === id)
      if (notification) {
        notification.is_read = true
        notification.read_at = new Date().toISOString()
      }
    })

    selectedNotifications.value = []
    showBatchActions.value = false
    await fetchUnreadCount()
    ElMessage.success('批量标记已读成功')
  } catch (error) {
    console.error('批量标记已读失败:', error)
    ElMessage.error('批量标记已读失败')
  }
}

const markAllAsRead = async () => {
  try {
    await notificationService.markAllNotificationsAsRead()
    // 重新获取数据
    await fetchNotifications()
    await fetchUnreadCount()
    ElMessage.success('所有通知已标记为已读')
  } catch (error) {
    console.error('标记所有通知为已读失败:', error)
    ElMessage.error(error.detail || '标记所有通知为已读失败')
  }
}

// 格式化时间
const formatTime = (timeStr) => {
  if (!timeStr) return '-'
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

// 格式化完整时间
const formatFullTime = (timeStr) => {
  if (!timeStr) return '-'
  const date = new Date(timeStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const handlePageChange = (page) => {
  currentPage.value = page
  selectedNotifications.value = []
  showBatchActions.value = false
  fetchNotifications()
}

const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  selectedNotifications.value = []
  showBatchActions.value = false
  fetchNotifications()
}

onMounted(async () => {
  loading.value = true
  try {
    await Promise.all([fetchNotificationTypes(), fetchNotifications(), fetchUnreadCount()])
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="notification-center">
    <div class="page-container">
      <!-- 页面标题 -->
      <div class="page-header">
        <div class="header-content">
          <div class="title-section">
            <h1 class="page-title">
              <font-awesome-icon :icon="['fas', 'bell']" class="title-icon" />
              通知中心
            </h1>
            <div class="stats-badges">
              <el-badge :value="stats.unread" :hidden="stats.unread === 0">
                <span class="stat-item">共{{ stats.total }}条</span>
              </el-badge>
            </div>
          </div>
          <div class="header-actions">
            <el-button type="primary" :disabled="stats.unread === 0" @click="markAllAsRead">
              <font-awesome-icon :icon="['fas', 'check-double']" />
              全部已读
            </el-button>
          </div>
        </div>
      </div>

      <!-- 筛选区域 -->
      <div class="filter-section">
        <el-card shadow="never" class="filter-card">
          <div class="filter-content">
            <!-- 筛选选项 -->
            <div class="filter-options">
              <div class="filter-group">
                <label class="filter-label">状态:</label>
                <el-select
                  v-model="selectedStatus"
                  placeholder="选择状态"
                  @change="handleStatusChange"
                >
                  <el-option
                    v-for="option in statusOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </div>

              <div class="filter-group">
                <label class="filter-label">类型:</label>
                <el-select v-model="selectedType" placeholder="选择类型" @change="handleTypeChange">
                  <el-option
                    v-for="option in typeOptions"
                    :key="option.value"
                    :label="option.label"
                    :value="option.value"
                  />
                </el-select>
              </div>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 批量操作栏 -->
      <div v-if="showBatchActions" class="batch-actions">
        <el-card shadow="never" class="batch-card">
          <div class="batch-content">
            <span class="selected-count">已选择 {{ selectedNotifications.length }} 项</span>
            <div class="batch-buttons">
              <el-button size="small" @click="batchMarkAsRead">
                <font-awesome-icon :icon="['fas', 'check']" />
                标记已读
              </el-button>
            </div>
          </div>
        </el-card>
      </div>

      <!-- 通知列表 -->
      <div class="notifications-section">
        <el-card shadow="never" class="notifications-card">
          <!-- 列表头部 -->
          <div class="list-header">
            <el-checkbox
              v-model="isAllSelected"
              :indeterminate="isIndeterminate"
              @change="toggleSelectAll"
            />
            <span class="header-text">通知列表</span>
            <span class="result-count"> 共找到 {{ notifications.length }} 条通知 </span>
          </div>

          <!-- 通知列表 -->
          <div v-loading="loading" class="notifications-list">
            <div
              v-for="notification in notifications"
              :key="notification.id"
              class="notification-item"
              :class="{
                'notification-unread': !notification.is_read,
                'notification-selected': selectedNotifications.includes(notification.id)
              }"
            >
              <div class="notification-checkbox">
                <el-checkbox
                  :model-value="selectedNotifications.includes(notification.id)"
                  @change="(checked) => handleNotificationSelect(notification.id, checked)"
                />
              </div>

              <div class="notification-content" @click="viewNotificationDetail(notification)">
                <div class="notification-header">
                  <div class="notification-title-section">
                    <h4 class="notification-title">{{ notification.title }}</h4>
                    <div class="notification-badges">
                      <el-tag size="small" class="type-tag">
                        {{ notification.notification_type_name }}
                      </el-tag>
                      <span v-if="notification.priority === 'high'" class="priority-badge high">
                        重要
                      </span>
                    </div>
                  </div>
                  <div class="notification-meta">
                    <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
                    <span class="notification-sender">{{ notification.sender_name }}</span>
                  </div>
                </div>

                <div class="notification-body">
                  <p class="notification-text">{{ notification.content }}</p>
                </div>
              </div>

              <div class="notification-actions">
                <el-dropdown trigger="click">
                  <el-button type="text" size="small">
                    <font-awesome-icon :icon="['fas', 'ellipsis-v']" />
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="viewNotificationDetail(notification)">
                        <font-awesome-icon :icon="['fas', 'eye']" />
                        查看详情
                      </el-dropdown-item>
                      <el-dropdown-item
                        v-if="!notification.is_read"
                        @click="markAsRead(notification.id)"
                      >
                        <font-awesome-icon :icon="['fas', 'check']" />
                        标记已读
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </div>

            <!-- 空状态 -->
            <div v-if="!loading && notifications.length === 0" class="empty-state">
              <font-awesome-icon :icon="['fas', 'bell']" class="empty-icon" />
              <h3>暂无通知</h3>
              <p>
                {{
                  selectedStatus !== 'all' || selectedType !== 'all'
                    ? '没有找到符合条件的通知'
                    : '您目前没有任何通知'
                }}
              </p>
            </div>
          </div>

          <!-- 分页 -->
          <div v-if="pagination.total_count > 0" class="pagination-section">
            <el-pagination
              v-model:current-page="currentPage"
              v-model:page-size="pageSize"
              :page-sizes="[10, 20, 50, 100]"
              :total="pagination.total_count"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="handlePageChange"
              @size-change="handleSizeChange"
            />
          </div>
        </el-card>
      </div>
    </div>

    <!-- 通知详情对话框 -->
    <el-dialog
      v-model="showDetailDialog"
      title="通知详情"
      :width="800"
      :before-close="closeDetailDialog"
      class="notification-detail-dialog"
    >
      <div v-if="selectedNotification" class="notification-detail">
        <!-- 通知标题和状态 -->
        <div class="detail-section">
          <div class="detail-title-section">
            <h2 class="notification-main-title">{{ selectedNotification.title }}</h2>
            <div class="notification-status-badges">
              <el-tag :type="selectedNotification.is_read ? 'success' : 'warning'" size="small">
                {{ selectedNotification.is_read ? '已读' : '未读' }}
              </el-tag>
              <el-tag :type="priorityMap[selectedNotification.priority]?.type" size="small">
                {{
                  priorityMap[selectedNotification.priority]?.label || selectedNotification.priority
                }}
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 通知内容 -->
        <div class="detail-section">
          <h4 class="section-title">
            <font-awesome-icon :icon="['fas', 'bell']" />
            通知内容
          </h4>
          <div class="notification-content-detail">
            <p>{{ selectedNotification.content }}</p>
          </div>
        </div>

        <!-- 发送者信息 -->
        <div class="detail-section">
          <h4 class="section-title">
            <font-awesome-icon :icon="['fas', 'user']" />
            发送者信息
          </h4>
          <div class="sender-info">
            <div class="info-item">
              <span class="info-label">姓名：</span>
              <span class="info-value">{{ selectedNotification.sender_name }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">用户名：</span>
              <span class="info-value">{{ selectedNotification.sender_username }}</span>
            </div>
          </div>
        </div>

        <!-- 通知类型和相关对象 -->
        <!-- <div class="detail-section">
          <h4 class="section-title">
            <font-awesome-icon :icon="['fas', 'tag']" />
            分类信息
          </h4>
          <div class="category-info">
            <div class="info-item">
              <span class="info-label">通知类型：</span>
              <span class="info-value">
                <el-tag type="info" size="small">
                  {{ selectedNotification.notification_type_name }}
                </el-tag>
              </span>
            </div>
            <div class="info-item">
              <span class="info-label">类型代码：</span>
              <span class="info-value">{{ selectedNotification.notification_type_code }}</span>
            </div>
            <div v-if="selectedNotification.related_object_title" class="info-item">
              <span class="info-label">相关对象：</span>
              <span class="info-value">{{ selectedNotification.related_object_title }}</span>
            </div>
            <div v-if="selectedNotification.related_object_type" class="info-item">
              <span class="info-label">对象类型：</span>
              <span class="info-value">{{ selectedNotification.related_object_type }}</span>
            </div>
          </div>
        </div> -->

        <!-- 时间信息 -->
        <div class="detail-section">
          <h4 class="section-title">
            <font-awesome-icon :icon="['fas', 'clock']" />
            时间信息
          </h4>
          <div class="time-info">
            <div class="info-item">
              <span class="info-label">创建时间：</span>
              <span class="info-value">{{ formatFullTime(selectedNotification.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">发送时间：</span>
              <span class="info-value">{{ formatFullTime(selectedNotification.sent_at) }}</span>
            </div>
            <div v-if="selectedNotification.read_at" class="info-item">
              <span class="info-label">阅读时间：</span>
              <span class="info-value">{{ formatFullTime(selectedNotification.read_at) }}</span>
            </div>
            <div v-if="selectedNotification.expires_at" class="info-item">
              <span class="info-label">过期时间：</span>
              <span class="info-value">{{ formatFullTime(selectedNotification.expires_at) }}</span>
            </div>
          </div>
        </div>

        <!-- 扩展数据 -->
        <!-- <div
          v-if="
            selectedNotification.extra_data &&
            Object.keys(selectedNotification.extra_data).length > 0
          "
          class="detail-section"
        >
          <h4 class="section-title">
            <font-awesome-icon :icon="['fas', 'info-circle']" />
            扩展信息
          </h4>
          <div class="extra-data">
            <pre>{{ JSON.stringify(selectedNotification.extra_data, null, 2) }}</pre>
          </div>
        </div> -->
      </div>

      <template #footer>
        <div class="detail-footer">
          <el-button
            v-if="selectedNotification && !selectedNotification.is_read"
            type="primary"
            @click="markAsRead(selectedNotification.id)"
          >
            <font-awesome-icon :icon="['fas', 'check']" />
            标记已读
          </el-button>
          <el-button @click="closeDetailDialog">关闭</el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.notification-center {
  padding: 24px;
  background-color: #f5f7fa;
  min-height: 100vh;
}

.page-container {
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 24px;

  .header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;

    @media (max-width: 768px) {
      flex-direction: column;
      gap: 16px;
      align-items: stretch;
    }
  }

  .title-section {
    display: flex;
    align-items: center;
    gap: 16px;

    .page-title {
      font-size: 28px;
      font-weight: bold;
      color: #303133;
      margin: 0;
      display: flex;
      align-items: center;
      gap: 12px;

      .title-icon {
        color: #409eff;
      }
    }

    .stats-badges {
      .stat-item {
        font-size: 14px;
        color: #606266;
        padding: 4px 12px;
        background-color: #f5f7fa;
        border-radius: 12px;
      }
    }
  }

  .header-actions {
    display: flex;
    gap: 12px;
  }
}

.filter-section {
  margin-bottom: 16px;

  .filter-card {
    border: none;
  }

  .filter-content {
    display: flex;
    align-items: center;
    gap: 24px;

    @media (max-width: 768px) {
      flex-direction: column;
      align-items: stretch;
      gap: 16px;
    }

    .filter-options {
      display: flex;
      gap: 16px;

      @media (max-width: 768px) {
        flex-wrap: wrap;
      }

      .filter-group {
        display: flex;
        align-items: center;
        gap: 8px;
        min-width: 140px;

        .filter-label {
          font-size: 14px;
          color: #606266;
          white-space: nowrap;
        }
      }
    }
  }
}

.batch-actions {
  margin-bottom: 16px;

  .batch-card {
    border: 1px solid #409eff;
    background-color: rgba(64, 158, 255, 0.05);
  }

  .batch-content {
    display: flex;
    align-items: center;
    justify-content: space-between;

    @media (max-width: 768px) {
      flex-direction: column;
      gap: 12px;
      align-items: stretch;
    }

    .selected-count {
      color: #409eff;
      font-weight: 500;
    }

    .batch-buttons {
      display: flex;
      gap: 8px;

      @media (max-width: 768px) {
        justify-content: center;
      }
    }
  }
}

.notifications-section {
  .notifications-card {
    border: none;
  }

  .list-header {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px 0;
    border-bottom: 1px solid #ebeef5;

    .header-text {
      font-weight: 500;
      color: #303133;
    }

    .result-count {
      margin-left: auto;
      font-size: 14px;
      color: #909399;
    }
  }

  .notifications-list {
    min-height: 400px;
  }

  .notification-item {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    padding: 20px 0;
    border-bottom: 1px solid #f0f0f0;
    transition: all 0.2s ease;
    cursor: pointer;

    &:hover {
      background-color: #f9f9f9;
    }

    &.notification-unread {
      background-color: rgba(64, 158, 255, 0.02);
      border-left: 4px solid #409eff;
      padding-left: 16px;

      .notification-title {
        font-weight: 600;
        color: #303133;
      }
    }

    &.notification-selected {
      background-color: rgba(64, 158, 255, 0.08);
    }

    .notification-checkbox {
      margin-top: 2px;
    }

    .notification-content {
      flex: 1;

      .notification-header {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 8px;

        @media (max-width: 768px) {
          flex-direction: column;
          gap: 8px;
        }

        .notification-title-section {
          display: flex;
          align-items: center;
          gap: 12px;
          flex-wrap: wrap;

          .notification-title {
            font-size: 16px;
            font-weight: 500;
            color: #303133;
            margin: 0;
            line-height: 1.4;
          }

          .notification-badges {
            display: flex;
            align-items: center;
            gap: 8px;

            .type-tag {
              font-size: 12px;
            }

            .priority-badge {
              font-size: 12px;
              padding: 2px 8px;
              border-radius: 10px;
              font-weight: 500;

              &.high {
                background-color: rgba(245, 108, 108, 0.1);
                color: #f56c6c;
              }
            }
          }
        }

        .notification-meta {
          display: flex;
          flex-direction: column;
          align-items: flex-end;
          gap: 4px;
          flex-shrink: 0;

          @media (max-width: 768px) {
            align-items: flex-start;
          }

          .notification-time {
            font-size: 13px;
            color: #909399;
          }

          .notification-sender {
            font-size: 12px;
            color: #c0c4cc;
          }
        }
      }

      .notification-body {
        .notification-text {
          font-size: 14px;
          color: #606266;
          line-height: 1.6;
          margin: 0;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
        }
      }
    }

    .notification-actions {
      flex-shrink: 0;
      margin-top: 2px;
    }
  }

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 80px 20px;
    text-align: center;

    .empty-icon {
      font-size: 64px;
      color: #c0c4cc;
      margin-bottom: 16px;
    }

    h3 {
      font-size: 18px;
      color: #606266;
      margin: 0 0 8px 0;
    }

    p {
      font-size: 14px;
      color: #909399;
      margin: 0;
    }
  }

  .pagination-section {
    display: flex;
    justify-content: center;
    margin-top: 32px;
    padding-top: 24px;
    border-top: 1px solid #ebeef5;
  }
}

// 通知详情对话框样式
.notification-detail-dialog {
  :deep(.el-dialog__body) {
    padding: 0 20px 20px;
  }

  :deep(.el-dialog__footer) {
    padding: 20px;
    border-top: 1px solid #ebeef5;
  }
}

.notification-detail {
  .detail-section {
    margin-bottom: 24px;

    &:last-child {
      margin-bottom: 0;
    }

    .detail-title-section {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 16px;

      .notification-main-title {
        font-size: 20px;
        color: #303133;
        margin: 0;
        line-height: 1.4;
        flex: 1;
      }

      .notification-status-badges {
        display: flex;
        gap: 8px;
        flex-shrink: 0;
        flex-wrap: wrap;
      }
    }

    .section-title {
      font-size: 16px;
      color: #303133;
      margin: 0 0 12px 0;
      display: flex;
      align-items: center;
      gap: 8px;
      font-weight: 600;
      border-bottom: 2px solid #f0f0f0;
      padding-bottom: 8px;
    }

    .notification-content-detail {
      background-color: #f9f9f9;
      padding: 16px;
      border-radius: 8px;
      border-left: 4px solid #409eff;

      p {
        margin: 0;
        line-height: 1.6;
        color: #606266;
      }
    }

    .sender-info,
    .category-info,
    .time-info {
      .info-item {
        display: flex;
        align-items: center;
        margin-bottom: 12px;

        &:last-child {
          margin-bottom: 0;
        }

        .info-label {
          color: #909399;
          font-weight: 500;
          min-width: 80px;
          flex-shrink: 0;
        }

        .info-value {
          color: #303133;
          flex: 1;
        }
      }
    }

    .extra-data {
      background-color: #f5f7fa;
      padding: 16px;
      border-radius: 8px;
      border: 1px solid #e4e7ed;

      pre {
        margin: 0;
        font-size: 13px;
        color: #606266;
        white-space: pre-wrap;
        word-break: break-all;
      }
    }
  }
}

.detail-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

// Element Plus 组件样式覆盖
:deep(.el-dropdown-menu__item) {
  display: flex;
  align-items: center;
  gap: 8px;
}

:deep(.el-badge__content) {
  font-size: 11px;
}
</style>
