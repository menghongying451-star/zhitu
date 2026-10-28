import request from '@/utils/request'

export const userService = {
  // 获取当前用户信息
  getCurrentUser: async () => {
    try {
      const response = await request.get('/api/v1/user/profile/')
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取用户信息失败' }
    }
  },

  // 更新当前用户信息
  updateCurrentUser: async (userData) => {
    try {
      const response = await request.patch('/api/v1/user/update-profile/', userData)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '更新用户信息失败' }
    }
  },

  // 上传用户头像
  uploadAvatar: async (formData) => {
    try {
      const response = await request.post('/api/v1/user/upload-avatar/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '头像上传失败' }
    }
  },

  // 获取tag1（兴趣）标签列表
  getInterestTagList: async (search) => {
    try {
      const response = await request.get('/api/v1/user/tags/interests/', { params: { search } })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取兴趣标签列表失败' }
    }
  },

  // 获取tag2（技能）标签列表
  getSkillTagList: async (search) => {
    try {
      const response = await request.get('/api/v1/user/tags/abilities/', { params: { search } })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取技能标签列表失败' }
    }
  }
}
