import request from '@/utils/request'

// 获取资源列表
export function getResourceList(params) {
  return request({
    url: '/api/v1/project/resource/list/',
    method: 'get',
    params
  })
}

// 获取资源详情
export function getResourceDetail(resourceId) {
  return request({
    url: `/api/v1/project/resource/${resourceId}/`,
    method: 'get'
  })
}

// 下载资源
export function downloadResource(resourceId) {
  return request({
    url: `/api/v1/project/resource/${resourceId}/download/`,
    method: 'get'
  })
}
