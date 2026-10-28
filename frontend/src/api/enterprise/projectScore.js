import request from '@/utils/request'

export const projectScoreService = {
  // 创建评分标准
  createScoreStandard: async (data) => {
    try {
      const response = await request.post(`/api/v1/projectscore/criteria/create/`, data)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '创建评分标准失败' }
    }
  },

  // 获取评分标准列表
  getScoreStandardList: async (params) => {
    try {
      const response = await request.get(`/api/v1/projectscore/criteria/list/`, {
        params: params
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取评分标准列表失败' }
    }
  },

  // 获取评分标准详情
  getScoreStandardDetail: async (id) => {
    try {
      const response = await request.get(`/api/v1/projectscore/criteria/${id}/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取评分标准详情失败' }
    }
  },

  // 更新评分标准（可创建/更新关联评分指标）
  updateScoreStandard: async (id, data) => {
    try {
      const response = await request.put(`/api/v1/projectscore/criteria/${id}/update/`, data)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '更新评分标准失败' }
    }
  },

  // 复制评分标准生成新标准
  copyScoreStandard: async (data) => {
    try {
      const response = await request.post(`/api/v1/projectscore/criteria/clone/`, data)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '复制评分标准失败' }
    }
  },

  // 删除评分标准
  deleteScoreStandard: async (id) => {
    try {
      const response = await request.delete(`/api/v1/projectscore/criteria/${id}/delete/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '删除评分标准失败' }
    }
  },

  // 批量删除评分指标
  batchDeleteScoreIndicator: async (id, data) => {
    try {
      const response = await request.delete(
        `/api/v1/projectscore/criteria/${id}/indicators/batch/delete/`,
        { data }
      )
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '批量删除评分指标失败' }
    }
  },

  // 创建项目评分
  createProjectScore: async (id, data) => {
    try {
      const response = await request.post(`/api/v1/projectscore/evaluations/${id}/create/`, data)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '创建项目评分失败' }
    }
  },

  // 获取项目评分详情
  getProjectScoreDetail: async (id) => {
    try {
      const response = await request.get(`/api/v1/projectscore/evaluations/${id}/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取项目评分详情失败' }
    }
  },

  // 更新项目评分
  updateProjectScore: async (id, data) => {
    try {
      const response = await request.put(`/api/v1/projectscore/evaluations/${id}/update/`, data)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '更新项目评分失败' }
    }
  },

  // 提交项目评分
  submitProjectScore: async (id) => {
    try {
      const response = await request.post(`/api/v1/projectscore/evaluations/${id}/submit/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '提交项目评分失败' }
    }
  },

  // 公示项目排名
  publishProjectRanking: async (id) => {
    try {
      const response = await request.post(`/api/v1/projectscore/requirements/${id}/ranking/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '公示项目排名失败' }
    }
  },

  // 项目排名展示
  getProjectRanking: async (id) => {
    try {
      const response = await request.get(`/api/v1/projectscore/requirements/${id}/ranking/view/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取项目排名失败' }
    }
  }
}
