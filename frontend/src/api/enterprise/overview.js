import request from '@/utils/request'

export const enterpriseOverviewService = {
  getOverview: async () => {
    try {
      const response = await request.get(`/api/v1/studentproject/organization/overview/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取企业概览失败' }
    }
  }
}
