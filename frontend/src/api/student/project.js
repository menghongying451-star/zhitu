import request from '@/utils/request'

// 获取项目列表
export function getProjectList(params) {
  return request({
    url: '/api/v1/studentproject/projects/',
    method: 'get',
    params
  })
}

// 获取项目详情
export function getProjectDetail(projectId) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/`,
    method: 'get'
  })
}

// 申请加入项目
export function applyProject(projectId, data) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/apply/`,
    method: 'post',
    data
  })
}

// 获取项目参与者列表和待审核申请
export function getProjectParticipants(projectId, params) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/participants/`,
    method: 'get',
    params
  })
}

// 获取参与者详情
export function getParticipantDetail(projectId, participantId) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/participants/${participantId}/`,
    method: 'get'
  })
}

// 修改参与者状态
export function updateParticipantStatus(projectId, participantId, data) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/participants/${participantId}/status/`,
    method: 'put',
    data
  })
}

// 转移负责人身份
export function transferLeadership(projectId, data) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/transfer-leadership/`,
    method: 'post',
    data
  })
}

// 创建项目
export function createProject(data) {
  return request({
    url: '/api/v1/studentproject/projects/create/',
    method: 'post',
    data
  })
}

// 修改项目
export function updateProject(projectId, data) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/update/`,
    method: 'patch',
    data
  })
}

// 删除项目
export function deleteProject(projectId) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/delete/`,
    method: 'delete'
  })
}

// 审核处理申请
export function handleApplications(projectId, data) {
  return request({
    url: `/api/v1/studentproject/projects/${projectId}/applications/handle/`,
    method: 'post',
    data,
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
}
