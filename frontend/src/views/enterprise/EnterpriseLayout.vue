<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Monitor,
  FolderOpened,
  Document,
  User,
  Setting,
  Expand,
  Fold,
  Menu,
  Search,
  Bell,
  Close,
  ArrowDown
} from '@element-plus/icons-vue'
import { useUserStore, useAuthStore } from '@/stores'
import { useNotificationStore } from '@/stores'
import { authService } from '@/api/auth'
import { websocketService } from '@/utils/websocket'
import router from '@/router'

const userStore = useUserStore()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const isCollapsed = ref(false)
const isMobileMenuOpen = ref(false)

// 计算属性：判断是否为审核中状态
const isPending = computed(() => {
  return userStore.user?.company_profile?.status === 'pending'
})

// 获取未读消息数
const unreadCount = computed(() => notificationStore.unreadCount)

// 获取连接状态
const isWsConnected = computed(() => notificationStore.isConnected)

const toggleSidebar = () => {
  isCollapsed.value = !isCollapsed.value
}

const toggleMobileMenu = () => {
  isMobileMenuOpen.value = !isMobileMenuOpen.value
}

const menuItems = [
  { path: '/enterprise/dashboard', icon: Monitor, label: '数据概览', requiresApproval: false },
  {
    path: '/enterprise/requirement-management',
    icon: Document,
    label: '需求发布',
    requiresApproval: true
  },
  {
    path: '/enterprise/resource-management',
    icon: FolderOpened,
    label: '资源管理',
    requiresApproval: true
  },
  {
    path: '/enterprise/notification-center',
    icon: Bell,
    label: '通知中心',
    requiresApproval: false
  },
  {
    path: '/enterprise/enterprise-settings',
    icon: Setting,
    label: '企业设置',
    requiresApproval: false
  },
  { path: '/enterprise/user-center', icon: User, label: '个人中心', requiresApproval: false }
]

// 检查菜单项是否可用
const isMenuItemDisabled = (item) => {
  return isPending.value && item.requiresApproval
}

// 处理菜单点击
const handleMenuClick = (item, event) => {
  if (isMenuItemDisabled(item)) {
    event.preventDefault()
    return false
  }
  return true
}

// 初始化WebSocket连接
const initWebSocket = () => {
  // 监听未读消息数更新
  websocketService.on('unreadCount', (count) => {
    notificationStore.setUnreadCount(count)
  })

  // 监听新通知
  websocketService.on('notification', (notification) => {
    notificationStore.addNotification(notification)

    // 显示桌面通知
    showDesktopNotification(notification)
  })

  // 监听连接状态
  websocketService.on('connected', () => {
    notificationStore.setConnected(true)
    console.log('WebSocket连接成功')
  })

  websocketService.on('disconnected', () => {
    notificationStore.setConnected(false)
    console.log('WebSocket连接断开')
  })

  websocketService.on('error', (error) => {
    console.error('WebSocket连接错误:', error)
    ElMessage.error('通知服务连接异常，请检查网络连接')
  })

  websocketService.on('maxReconnectAttemptsReached', () => {
    ElMessage.error('通知服务连接失败，请刷新页面重试')
  })

  // 建立连接
  websocketService.connect()
}

// 显示桌面通知
const showDesktopNotification = (notification) => {
  // 元素UI通知
  ElNotification({
    title: notification.title,
    message: notification.content,
    type: 'info',
    duration: 5000,
    position: 'top-right',
    onClick: () => {
      // 点击通知跳转到通知中心
      router.push('/enterprise/notification-center')
    }
  })

  // 浏览器原生通知（需要用户授权）
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification(notification.title, {
      body: notification.content,
      icon: '/favicon.ico',
      tag: `notification-${notification.id}`,
      onclick: () => {
        window.focus()
        router.push('/enterprise/notification-center')
      }
    })
  }
}

// 请求通知权限
const requestNotificationPermission = () => {
  if ('Notification' in window && Notification.permission === 'default') {
    Notification.requestPermission()
  }
}

// 处理通知按钮点击
const handleNotificationClick = () => {
  if (!isPending.value) {
    router.push('/enterprise/notification-center')
  }
}

const handleLogout = async () => {
  // 关闭WebSocket连接
  websocketService.close()

  await authService.logout()
  userStore.clearUser()
  authStore.removeToken()
  authStore.removeRefreshToken()
  notificationStore.clearNotifications()

  router.push('/login').then(() => {
    window.location.reload()
  })
}

// 组件挂载时初始化
onMounted(() => {
  // 请求通知权限
  requestNotificationPermission()

  // 如果用户已登录，初始化WebSocket
  if (userStore.user?.id) {
    initWebSocket()
  }
})

// 组件卸载时清理
onUnmounted(() => {
  websocketService.close()
})
</script>

<template>
  <div class="enterprise-layout">
    <!-- 侧边栏 -->
    <aside
      class="sidebar"
      :class="{
        collapsed: isCollapsed,
        'mobile-open': isMobileMenuOpen
      }"
    >
      <!-- Logo 头部 -->
      <div class="sidebar-header">
        <div class="logo-container" v-if="!isCollapsed">
          <span class="logo-text">知途</span>
          <span class="logo-subtitle">企业版</span>
        </div>

        <!-- 桌面端折叠按钮 -->
        <button class="desktop-collapse-btn" @click="toggleSidebar">
          <el-icon :size="20">
            <Expand v-if="isCollapsed" />
            <Fold v-else />
          </el-icon>
        </button>

        <!-- 移动端关闭按钮 -->
        <button class="mobile-close-btn" @click="toggleMobileMenu">
          <el-icon><Close /></el-icon>
        </button>
      </div>

      <!-- 导航菜单 -->
      <div class="sidebar-content">
        <nav class="navigation">
          <el-tooltip
            v-for="item in menuItems"
            :key="item.path"
            :content="
              isMenuItemDisabled(item) ? '您的加入申请正在审核中，审核通过后可使用此功能' : ''
            "
            :disabled="!isMenuItemDisabled(item)"
            placement="right"
          >
            <router-link
              :to="isMenuItemDisabled(item) ? '#' : item.path"
              class="nav-link"
              :class="{ disabled: isMenuItemDisabled(item) }"
              active-class="active"
              @click="handleMenuClick(item, $event)"
            >
              <el-icon class="nav-icon" :size="18">
                <component :is="item.icon" />
              </el-icon>
              <span v-if="!isCollapsed" class="nav-text">{{ item.label }}</span>
            </router-link>
          </el-tooltip>
        </nav>
      </div>

      <!-- 企业信息 -->
      <div v-if="!isCollapsed" class="sidebar-footer">
        <div class="company-info">
          <el-avatar
            :size="40"
            :src="
              userStore.user?.company_profile?.organization?.logo ||
              'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
            "
            class="company-avatar"
          />
          <div class="company-details">
            <div class="company-name">
              {{ userStore.user?.company_profile?.organization.name || 'XX科技有限公司' }}
            </div>
            <div class="company-role">
              {{ userStore.user?.company_profile?.position || '产品经理' }}
            </div>
          </div>
        </div>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div class="main-container">
      <!-- 顶部导航 -->
      <header class="main-header">
        <div class="header-left">
          <!-- 移动端菜单按钮 -->
          <button class="mobile-menu-btn" @click="toggleMobileMenu">
            <el-icon><Menu /></el-icon>
          </button>
        </div>

        <!-- 搜索框 -->
        <!-- <div class="header-center">
          <div class="search-container">
            <el-input
              placeholder="搜索项目、人才..."
              :prefix-icon="Search"
              class="search-input"
              :disabled="isPending"
            />
          </div>
        </div> -->

        <div class="header-right">
          <!-- 连接状态指示器 -->
          <div class="connection-status" v-if="!isWsConnected">
            <el-tooltip content="通知服务未连接" placement="bottom">
              <div class="status-indicator offline"></div>
            </el-tooltip>
          </div>

          <!-- 通知按钮 -->
          <el-tooltip
            :content="isPending ? '审核通过后可使用通知功能' : '通知中心'"
            placement="bottom"
          >
            <el-badge
              :value="isPending ? 0 : unreadCount"
              :max="99"
              class="notification-badge"
              @click="handleNotificationClick"
            >
              <el-button
                :icon="Bell"
                text
                class="notification-btn"
                :class="{ disabled: isPending }"
                :disabled="isPending"
              />
            </el-badge>
          </el-tooltip>

          <!-- 用户信息 -->
          <el-dropdown>
            <div class="user-info">
              <el-avatar
                :size="32"
                :src="
                  userStore.user?.avatar ||
                  'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
                "
                class="user-avatar"
              />
              <span class="username">{{ userStore.user?.username || '张经理' }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item
                  @click="
                    router.push('/enterprise/user-center').then(() => {
                      window.location.reload()
                    })
                  "
                >
                  个人设置</el-dropdown-item
                >
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区域 -->
      <main class="main-content">
        <router-view />
      </main>
    </div>

    <!-- 移动端遮罩 -->
    <div v-if="isMobileMenuOpen" class="mobile-overlay" @click="toggleMobileMenu"></div>
  </div>
</template>

<style lang="scss" scoped>
.enterprise-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f2f3f5;
  font-family: 'Inter', sans-serif;
  height: 100vh;
  overflow: hidden;
}

.sidebar {
  width: 256px;
  background: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  z-index: 20;

  &.collapsed {
    width: 80px;
  }

  @media (max-width: 768px) {
    position: fixed;
    left: -256px;
    height: 100vh;

    &.mobile-open {
      left: 0;
    }
  }
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  border-bottom: 1px solid #e5e6eb;
  min-height: 72px;

  .logo-container {
    display: flex;
    align-items: center;
    flex: 1;
  }

  .logo-text {
    color: #165dff;
    font-size: 24px;
    font-weight: 700;
  }

  .logo-subtitle {
    margin-left: 8px;
    color: #86909c;
    font-size: 12px;
  }

  .desktop-collapse-btn {
    background: none;
    border: none;
    color: #86909c;
    cursor: pointer;
    padding: 6px;
    border-radius: 4px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;

    &:hover {
      background-color: #f7f8fa;
      color: #165dff;
    }

    @media (max-width: 768px) {
      display: none;
    }
  }

  .mobile-close-btn {
    display: none;
    background: none;
    border: none;
    color: #86909c;
    font-size: 16px;
    cursor: pointer;

    @media (max-width: 768px) {
      display: block;
    }
  }
}

.sidebar.collapsed .sidebar-header {
  justify-content: center;

  .desktop-collapse-btn {
    margin: 0;
  }
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.navigation {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-link {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  color: #4e5969;
  text-decoration: none;
  border-radius: 8px;
  transition: all 0.2s ease;
  font-weight: 400;

  &:hover:not(.disabled) {
    background-color: rgba(22, 93, 255, 0.05);
    color: #165dff;
  }

  &.active:not(.disabled) {
    background-color: rgba(22, 93, 255, 0.1);
    color: #165dff;
    font-weight: 500;
  }

  // 禁用状态样式
  &.disabled {
    color: #c9cdd4;
    cursor: not-allowed;
    pointer-events: auto; // 保持指针事件以便显示tooltip

    &:hover {
      background-color: transparent;
      color: #c9cdd4;
    }

    .nav-icon {
      color: #c9cdd4;
    }

    .nav-text {
      color: #c9cdd4;
    }
  }

  .nav-text {
    white-space: nowrap;
  }
}

.sidebar.collapsed .nav-link {
  justify-content: center;
  padding: 12px;
}

.nav-icon {
  width: 20px;
  height: 20px;
  margin-right: 12px;
}

.sidebar.collapsed .nav-icon {
  margin-right: 0;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #e5e6eb;

  .company-info {
    display: flex;
    align-items: center;
  }

  .company-avatar {
    margin-right: 12px;
  }

  .company-details {
    .company-name {
      font-weight: 500;
      font-size: 14px;
      color: #1d2129;
    }

    .company-role {
      font-size: 12px;
      color: #86909c;
    }
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-header {
  background: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
  padding: 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 10;
}

.header-left {
  display: flex;
  align-items: center;
  min-width: 0;

  .mobile-menu-btn {
    display: none;
    background: none;
    border: none;
    color: #86909c;
    font-size: 20px;
    cursor: pointer;

    @media (max-width: 768px) {
      display: block;
    }
  }
}

.header-center {
  flex: 1;
  display: flex;
  justify-content: center;
  margin: 0 20px;

  @media (max-width: 640px) {
    margin: 0 12px;
  }

  .search-container {
    .search-input {
      width: 320px;
      max-width: 100%;

      @media (max-width: 640px) {
        width: 100%;
        max-width: 240px;
      }

      :deep(.el-input__wrapper) {
        background-color: #f7f8fa;
        border: none;
        border-radius: 8px;
      }

      // 禁用状态样式
      &.is-disabled :deep(.el-input__wrapper) {
        background-color: #f5f5f5;
        color: #c0c4cc;
      }
    }
  }
}

.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
  min-width: 0;

  @media (max-width: 480px) {
    gap: 8px;
  }

  .connection-status {
    .status-indicator {
      width: 8px;
      height: 8px;
      border-radius: 50%;

      &.offline {
        background-color: #f53f3f;
        animation: pulse 2s infinite;
      }
    }
  }

  .notification-badge {
    cursor: pointer;

    .notification-btn {
      background: none;
      border: none;
      color: #86909c;
      font-size: 20px;
      cursor: pointer;
      padding: 8px;
      border-radius: 6px;
      transition: all 0.2s ease;

      &:hover:not(.disabled) {
        color: #165dff;
        background-color: #f7f8fa;
      }

      // 禁用状态样式
      &.disabled {
        color: #c9cdd4;
        cursor: not-allowed;

        &:hover {
          color: #c9cdd4;
          background-color: transparent;
        }
      }
    }
  }

  .user-info {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 4px;
    border-radius: 8px;
    transition: background-color 0.2s ease;
    min-width: 0;

    &:hover {
      background-color: #f7f8fa;
    }

    .user-avatar {
      flex-shrink: 0;
    }

    .username {
      margin: 0 8px;
      font-weight: 500;
      font-size: 14px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;

      @media (max-width: 480px) {
        display: none;
      }
    }

    .dropdown-icon {
      color: #86909c;
      font-size: 12px;
      flex-shrink: 0;

      @media (max-width: 480px) {
        display: none;
      }
    }
  }
}

.main-content {
  flex: 1;
  overflow-y: auto;
}

.mobile-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 15;

  @media (min-width: 769px) {
    display: none;
  }
}

@keyframes pulse {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
  100% {
    opacity: 1;
  }
}

@media (max-width: 768px) {
  .enterprise-layout {
    .sidebar.collapsed {
      left: -80px;
    }
  }
}
</style>
