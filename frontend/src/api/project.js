import request from '@/utils/request'

export const projectService = {
  // 获取项目列表
  getProjectList: async (params) => {
    try {
      const response = await request.get(`/api/v1/studentproject/projects/`, { params: params })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取项目列表失败' }
    }
  },

  // 获取项目详情
  getProjectDetail: async (id) => {
    try {
      const response = await request.get(`/api/v1/studentproject/projects/${id}/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取项目详情失败' }
    }
  },

  // 获取评语列表
  /**
   * 获取评语列表
   * @param {Object} params - 查询参数对象
   * @param {string} [params.page] - 页码，可选参数
   * @param {string} [params.page_size] - 每页条数，可选参数
   * @param {string} [params.deliverable_id] - 成果ID，可选参数。不传则获取项目级评语，传入则获取指定成果的评语
   * @returns {Promise<Object>} 包含评语列表的响应对象
   */
  getCommentList: async (id, params) => {
    try {
      const response = await request.get(`/api/v1/studentproject/projects/${id}/comments/`, {
        params: params
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取项目评语列表失败' }
    }
  },

  // 获取评语回复列表
  /**
   * @param {Object} params - 查询参数对象
   * @param {string} [params.page] - 页码，可选参数
   * @param {string} [params.page_size] - 每页条数，可选参数
   * @returns {Promise<Object>} 包含评语回复列表的响应对象
   */
  getReplyList: async (projectId, commentId, params) => {
    try {
      const response = await request.get(
        `/api/v1/studentproject/projects/${projectId}/comments/${commentId}/replies/`,
        { params: params }
      )
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取评语回复列表失败' }
    }
  },

  // 发布评语
  /**
   * @param {Object} params - 查询参数对象
   * @param {string} [params.deliverable_id] - 成果 ID，可选参数。不传则为项目级评语，传入则为指定成果的评语
   * @param {string} [params.parent_comment_id] - 父评语 ID，可选参数，用于回复功能
   * @param {Object} data - 请求体参数
   * @param {string} data.content - 评语内容
   * @returns {Promise<Object>} 发布成功后的响应数据
   */
  publishComment: async (projectId, params, data) => {
    try {
      const response = await request.post(
        `/api/v1/studentproject/projects/${projectId}/comments/create/`,
        data,
        { params: params }
      )
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '发布评语失败' }
    }
  },

  // 删除评语
  deleteComment: async (projectId, commentId) => {
    try {
      const response = await request.delete(
        `/api/v1/studentproject/projects/${projectId}/comments/${commentId}/delete/`
      )
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '删除评语失败' }
    }
  },

  // 获取成果详情
  getDeliverableDetail: async (projectId, deliverableId) => {
    try {
      const response = await request.get(
        `/api/v1/studentproject/projects/${projectId}/deliverables/${deliverableId}/`
      )
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取成果详情失败' }
    }
  }
}
