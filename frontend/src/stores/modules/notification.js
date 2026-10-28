// src/stores/notification.js
import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useNotificationStore = defineStore('notification', () => {
  const unreadCount = ref(0)
  const notifications = ref([])
  const isConnected = ref(false)

  // 设置未读消息数
  const setUnreadCount = (count) => {
    unreadCount.value = count
  }

  // 添加新通知
  const addNotification = (notification) => {
    notifications.value.unshift(notification)
    if (!notification.is_read) {
      unreadCount.value++
    }
  }

  // 标记通知为已读
  const markAsRead = (notificationId) => {
    const notification = notifications.value.find((n) => n.id === notificationId)
    if (notification && !notification.is_read) {
      notification.is_read = true
      unreadCount.value = Math.max(0, unreadCount.value - 1)
    }
  }

  // 清空所有通知
  const clearNotifications = () => {
    notifications.value = []
    unreadCount.value = 0
  }

  // 设置连接状态
  const setConnected = (connected) => {
    isConnected.value = connected
  }

  return {
    unreadCount,
    notifications,
    isConnected,
    setUnreadCount,
    addNotification,
    markAsRead,
    clearNotifications,
    setConnected
  }
})
