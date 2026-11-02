<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import {
  Document,
  Expand,
  Fold,
  Menu,
  Bell,
  Close,
  ArrowDown,
  StarFilled,
  ChatLineSquare
} from '@element-plus/icons-vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore, useAuthStore } from '@/stores'
import { useNotificationStore } from '@/stores'
import { authService } from '@/api/auth'
import { websocketService } from '@/utils/websocket'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const isCollapsed = ref(false)
const isMobileMenuOpen = ref(false)

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

// 菜单顺序（自上而下）：找机会 → 我的收藏 → 历史对话
// 知途 v0：个人设置入口已从侧边栏移除，改为点击左下角学生头像进入个人中心
const menuItems = [
  { path: '/student/project-requirement', icon: Document, label: '找机会' },
  { path: '/student/demand-following', icon: StarFilled, label: '我的收藏' },
  { path: '/student/chat-history', icon: ChatLineSquare, label: '历史对话' }
]

// 点击左下角学生信息区 → 个人中心
const goProfileCenter = () => {
  isMobileMenuOpen.value = false
  router.push('/student/settings')
}

const activeMenu = ref(
  route.path.startsWith('/student/') ? route.path : '/student/project-requirement'
)

function handleMenuSelect(index) {
  activeMenu.value = index
  router.push(index)
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
      router.push('/student/notification-center')
    }
  })

  // 浏览器原生通知（需要用户授权）
  if ('Notification' in window && Notification.permission === 'granted') {
    const notif = new Notification(notification.title, {
      body: notification.content,
      icon: '/favicon.ico',
      tag: `notification-${notification.id}`
    })

    // 设置点击事件处理器
    notif.onclick = () => {
      window.focus()
      router.push('/student/notification-center')
    }
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
  router.push('/student/notification-center')
}

// 处理退出登录
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
  <div class="student-layout">
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
          <span class="logo-subtitle">学生端</span>
        </div>
        <button class="desktop-collapse-btn" @click="toggleSidebar">
          <el-icon :size="20">
            <Expand v-if="isCollapsed" />
            <Fold v-else />
          </el-icon>
        </button>
        <button class="mobile-close-btn" @click="toggleMobileMenu">
          <el-icon><Close /></el-icon>
        </button>
      </div>
      <div class="sidebar-content">
        <nav class="navigation">
          <router-link
            v-for="item in menuItems"
            :key="item.path"
            :to="item.path"
            class="nav-link"
            active-class="active"
            @click="() => handleMenuSelect(item.path)"
          >
            <el-icon class="nav-icon" :size="18">
              <component :is="item.icon" />
            </el-icon>
            <span v-if="!isCollapsed" class="nav-text">{{ item.label }}</span>
          </router-link>
        </nav>
      </div>
      <!-- 学生信息区：点击进入个人中心 -->
      <div v-if="!isCollapsed" class="sidebar-footer">
        <div
          class="student-info"
          role="button"
          tabindex="0"
          title="个人中心"
          @click="goProfileCenter"
          @keydown.enter="goProfileCenter"
          @keydown.space.prevent="goProfileCenter"
        >
          <el-avatar
            :size="40"
            :src="
              userStore.user?.avatar ||
              'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png'
            "
            class="student-avatar"
          />
          <div class="student-details">
            <div class="student-name">{{ userStore.user?.username || '学生' }}</div>
            <div class="student-role">
              {{ userStore.user?.student_profile?.major || '专业未知' }}
            </div>
          </div>
        </div>
      </div>
    </aside>
    <div class="main-container">
      <header class="main-header">
        <div class="header-left">
          <button class="mobile-menu-btn" @click="toggleMobileMenu">
            <el-icon><Menu /></el-icon>
          </button>
        </div>
        <div class="header-right">
          <!-- 连接状态指示器 -->
          <div class="connection-status" v-if="!isWsConnected">
            <el-tooltip content="通知服务未连接" placement="bottom">
              <div class="status-indicator offline"></div>
            </el-tooltip>
          </div>

          <!-- 通知按钮 -->
          <el-tooltip content="通知中心" placement="bottom">
            <el-badge
              :value="unreadCount"
              :max="99"
              class="notification-badge"
              @click="handleNotificationClick"
            >
              <el-button :icon="Bell" text class="notification-btn" />
            </el-badge>
          </el-tooltip>

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
              <span class="username">{{ userStore.user?.username || '学生' }}</span>
              <el-icon class="dropdown-icon"><ArrowDown /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/student/settings')"
                  >个人设置</el-dropdown-item
                >
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>
      <main class="main-content">
        <router-view />
      </main>
    </div>
    <div v-if="isMobileMenuOpen" class="mobile-overlay" @click="toggleMobileMenu"></div>
  </div>
</template>

<style lang="scss" scoped>
.student-layout {
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

  &:hover {
    background-color: rgba(22, 93, 255, 0.05);
    color: #165dff;
  }

  &.active {
    background-color: rgba(22, 93, 255, 0.1);
    color: #165dff;
    font-weight: 500;
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

  .student-info {
    display: flex;
    align-items: center;
    cursor: pointer;
    padding: 6px;
    margin: -6px;
    border-radius: 8px;
    transition: background-color 0.2s ease;

    &:hover {
      background-color: #f7f8fa;
    }

    &:focus-visible {
      outline: 2px solid #165dff;
      outline-offset: 2px;
    }

    .student-avatar {
      margin-right: 12px;
    }

    .student-details {
      .student-name {
        font-weight: 500;
        font-size: 14px;
        color: #1d2129;
      }

      .student-role {
        font-size: 12px;
        color: #86909c;
      }
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

      &:hover {
        color: #165dff;
        background-color: #f7f8fa;
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
  overflow-x: hidden;
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
  .student-layout {
    .sidebar.collapsed {
      left: -80px;
    }
  }
}
</style>
