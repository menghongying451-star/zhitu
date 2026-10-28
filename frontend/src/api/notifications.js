import request from '@/utils/request'

export const notificationService = {
  // 获取通知类型列表
  getNotificationTypes: async () => {
    try {
      const response = await request.get('/api/v1/notification/types/', {
        params: { page_size: 50 }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取通知类型失败，请稍后重试' }
    }
  },

  // 获取通知列表
  getNotifications: async (params) => {
    try {
      const response = await request.get('/api/v1/notification/notifications/', {
        params
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取通知列表失败，请稍后重试' }
    }
  },

  // 获取未读通知数量
  getUnreadNotificationsCount: async () => {
    try {
      const response = await request.get('/api/v1/notification/notifications/unread_count/')
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取未读通知数量失败，请稍后重试' }
    }
  },

  // 标记通知为已读
  markNotificationAsRead: async (notificationId) => {
    try {
      await request.post(`/api/v1/notification/notifications/${notificationId}/mark_as_read/`)
    } catch (error) {
      throw error.response?.data || { detail: '标记通知为已读失败，请稍后重试' }
    }
  },

  // 标记所有通知为已读
  markAllNotificationsAsRead: async () => {
    try {
      await request.post('/api/v1/notification/notifications/mark_all_as_read/')
    } catch (error) {
      throw error.response?.data || { detail: '标记所有通知为已读失败，请稍后重试' }
    }
  },

  // 获取用户通知设置
  getUserNotificationSettings: async () => {
    try {
      const response = await request.get('/api/v1/notification/preferences/get_preferences/')
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取用户通知设置失败，请稍后重试' }
    }
  },

  // 更新用户通知设置
  updateUserNotificationSettings: async (settings) => {
    try {
      await request.patch('/api/v1/notification/preferences/update_preferences/', settings)
    } catch (error) {
      throw error.response?.data || { detail: '更新用户通知设置失败，请稍后重试' }
    }
  },

  // 重置用户通知设置
  resetUserNotificationSettings: async () => {
    try {
      await request.post('/api/v1/notification/preferences/reset_to_default/')
    } catch (error) {
      throw error.response?.data || { detail: '重置用户通知设置失败，请稍后重试' }
    }
  }
}
