import request from '@/utils/request'

export const requirementService = {
  //获取需求统计数据
  getRequirementStatistics: async () => {
    try {
      const response = await request.get(`/api/v1/project/requirement/statistics/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取需求统计数据失败' }
    }
  },

  //获取需求列表
  getRequirementList: async (organization_id, params) => {
    try {
      const response = await request.get(`/api/v1/project/requirement/list/`, {
        params: {
          ...params,
          organization_id
        }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取需求列表失败' }
    }
  },

  //获取需求详情
  getRequirementDetail: async (id) => {
    try {
      const response = await request.get(`/api/v1/project/requirement/${id}/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取需求详情失败' }
    }
  },

  //创建需求
  createRequirement: async (formdata) => {
    try {
      const response = await request.post(`/api/v1/project/requirement/`, formdata, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '创建需求失败' }
    }
  },

  //更新需求
  updateRequirement: async (id, formdata) => {
    try {
      const response = await request.put(`/api/v1/project/requirement/${id}/update/`, formdata, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '更新需求失败' }
    }
  },

  //删除需求
  deleteRequirement: async (id) => {
    try {
      const response = await request.delete(`/api/v1/project/requirement/${id}/delete/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '删除需求失败' }
    }
  }
}
