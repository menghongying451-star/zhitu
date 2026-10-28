import request from '@/utils/request'

export const testService = {
  getTest: async () => {
    try {
      const response = await request.get('api/test')
      return response.data
    } catch (error) {
      console.error('Get test error:', error)
      throw error.response?.data || { detail: '获取测试数据失败，请稍后再试' }
    }
  }
}
