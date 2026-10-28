import request from '@/utils/request'

export const authService = {
  // 用户注册
  register: async (userData) => {
    try {
      const response = await request.post('/api/v1/auth/register/', userData)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '注册失败，请稍后重试' }
    }
  },

  // 用户登录
  login: async (credentials) => {
    try {
      const response = await request.post('/api/v1/auth/login/', credentials)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '登录失败，请稍后重试' }
    }
  },

  // 登出
  logout: async () => {
    try {
      const response = await request.post('/api/v1/auth/logout/')
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '登出失败，请稍后重试' }
    }
  },

  // 忘记密码
  forgetPassword: async (forgetData) => {
    try {
      const response = await request.post('/api/v1/auth/forgot-password/', forgetData)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '重置密码失败，请稍后重试' }
    }
  },

  // 发送邮箱验证码
  sendEmailVerification: async (emailData) => {
    try {
      const response = await request.post('/api/v1/auth/send-email-code/', emailData)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '发送验证码失败，请检查邮箱地址或稍后重试' }
    }
  },

  // 发送短信验证码
  sendPhoneVerification: async (phone) => {
    try {
      const response = await request.post('/api/v1/auth/send-phone-code/', { phone })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '发送验证码失败，请检查手机号或稍后重试' }
    }
  },

  // 刷新token
  refresh: async (refresh) => {
    try {
      const response = await request.post('/api/v1/auth/refresh/', { refresh_token: refresh })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '用户token刷新失败，请稍后再试' }
    }
  },

  // 修改密码
  changePassword: async (passwordData) => {
    try {
      const response = await request.post('/api/v1/auth/change-password/', passwordData)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '修改密码失败，请稍后重试' }
    }
  },

  // 修改邮箱
  changeEmail: async (emailData) => {
    try {
      const response = await request.post('/api/v1/auth/change-email/', emailData)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '修改邮箱失败，请稍后重试' }
    }
  },

  // 修改手机号
  changePhone: async (phoneData) => {
    try {
      const response = await request.post('/api/v1/auth/change-phone/', phoneData)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '修改手机号失败，请稍后重试' }
    }
  },

  // 注销账户
  deleteAccount: async (data) => {
    try {
      const response = await request.post('/api/v1/auth/delete-account/request/', data)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '注销账户失败，请稍后重试' }
    }
  }

  // 恢复账户
  // restoreAccount: async (password) => {
  //   try {
  //     const response = await request.post('/api/v1/auth/delete-account/cancel', { password })
  //     return response.data
  //   } catch (error) {
  //     throw error.response?.data || { detail: '恢复账户失败，请稍后重试' }
  //   }
  // },

  // 查看注销状态
  // checkDeleteStatus: async () => {
  //   try {
  //     const response = await request.get('/api/v1/auth/delete-account/status/')
  //     return response.data
  //   } catch (error) {
  //     throw error.response?.data || { detail: '查看注销状态失败，请稍后重试' }
  //   }
  // }
}
