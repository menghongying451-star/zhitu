import request from '@/utils/request'
import { update } from 'lodash'

export const enterpriseInfoService = {
  // 搜索企业/机构
  searchOrganizations: async (params) => {
    try {
      const response = await request.get('/api/v1/organization/search/', {
        params: {
          search: params.search,
          organization_type: params.organization_type,
          page: params.page,
          page_size: params.page_size
        }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '搜索机构失败，请稍后重试' }
    }
  },

  // 搜索大学
  searchUniversities: async (params) => {
    try {
      const response = await request.get('/api/v1/organization/universities/', {
        params: {
          search: params.search,
          page: params.page,
          page_size: params.page_size
        }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '搜索大学失败，请稍后重试' }
    }
  },

  // 获取企业信息
  getEnterpriseInfo: async (id) => {
    try {
      const response = await request.get(`/api/v1/organization/${id}/detail/`)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取企业信息失败，请稍后重试' }
    }
  },

  // 修改企业信息
  updateEnterpriseInfo: async (data) => {
    try {
      const response = await request.patch(`/api/v1/organization/update/`, data)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '修改企业信息失败，请稍后重试' }
    }
  },

  // 上传企业logo
  uploadEnterpriseLogo: async (file) => {
    try {
      const response = await request.post(`/api/v1/organization/upload-logo/`, file)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '上传企业logo失败，请稍后重试' }
    }
  },

  // 获取组织成员列表
  getOrganizationMembers: async (params) => {
    try {
      const response = await request.get('/api/v1/organization/members/', {
        params: {
          status: params.status, // pending, approved, rejected
          permission: params.permission, // member, admin, owner, pending
          search: params.search, // 搜索关键词（用户名、真实姓名、邮箱、职位、部门）
          page: params.page,
          page_size: params.page_size
        }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取组织成员列表失败，请稍后重试' }
    }
  },

  // 更新组织成员信息
  updateOrganizationMember: async (memberId, data) => {
    try {
      const response = await request.put(`/api/v1/organization/members/${memberId}/update/`, data)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '更新组织成员信息失败，请稍后重试' }
    }
  },

  // 批量更新成员状态
  batchUpdateMembers: async (data) => {
    try {
      const response = await request.post(`/api/v1/organization/members/batch-update/`, data)
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '批量更新成员状态失败，请稍后重试' }
    }
  },

  // 获取组织操作日志
  getOrganizationLogs: async (params) => {
    try {
      const response = await request.get('/api/v1/organization/operation-logs/', { params })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取组织操作日志失败，请稍后重试' }
    }
  },

  // 组织认证
  organizationVerification: async (formData) => {
    try {
      const response = await request.post('/api/v1/organization/verification/submit/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '组织认证失败，请稍后重试' }
    }
  },

  // 获取组织认证状态
  getOrganizationVerificationStatus: async () => {
    try {
      const response = await request.get('/api/v1/organization/verification/status/')
      return response.data
    } catch (error) {
      throw error.response?.data || { detail: '获取组织认证状态失败，请稍后重试' }
    }
  }
}
