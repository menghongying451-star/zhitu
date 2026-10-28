import request from '@/utils/request'

// 统一错误处理
function handleError(error, defaultMsg) {
  throw error.response?.data || { detail: defaultMsg }
}

export const resourcesService = {
  // 获取资源统计数据
  getResourceStatistics: async (organizationId, period) => {
    try {
      const response = await request.get(`/api/v1/project/resource/statistics/`, {
        params: {
          period
        }
      })
      return response.data
    } catch (error) {
      handleError(error, '获取资源统计数据失败')
    }
  },

  // 查询资源列表
  getResources: async (organizationId, params) => {
    try {
      const response = await request.get(`/api/v1/project/resource/list/`, {
        params: {
          ...params,
          organization_id: organizationId
        }
      })
      return response.data
    } catch (error) {
      handleError(error, '获取资源列表失败')
    }
  },

  // 查询资源详情
  getResourceDetail: async (id) => {
    try {
      const response = await request.get(`/api/v1/project/resource/${id}/`)
      return response.data
    } catch (error) {
      handleError(error, '获取资源详情失败')
    }
  },

  // 新增资源（含文件上传）
  createResource: async (formData) => {
    try {
      const response = await request.post('/api/v1/project/resource/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return response.data
    } catch (error) {
      handleError(error, '资源上传失败')
    }
  },

  // 编辑资源
  updateResource: async (id, formdata) => {
    try {
      const response = await request.put(`/api/v1/project/resource/${id}/update/`, formdata, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return response.data
    } catch (error) {
      handleError(error, '资源更新失败')
    }
  },

  // 删除资源
  deleteResource: async (id) => {
    try {
      const response = await request.delete(`/api/v1/project/resource/${id}/delete/`)
      return response.data
    } catch (error) {
      handleError(error, '资源删除失败')
    }
  },

  // 下载资源
  downloadResource: async (id) => {
    try {
      const response = await request.get(`/api/v1/project/resource/${id}/download/`)
      return response.data
    } catch (error) {
      handleError(error, '资源下载失败')
    }
  }
}
