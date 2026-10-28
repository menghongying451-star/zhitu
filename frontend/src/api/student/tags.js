// 标签相关接口封装：使用项目统一 axios 实例，避免动态导入 404
import client from '@/utils/request'

// 模糊搜索：同时返回 tag1、tag2
export async function searchTags(search = '') {
  return client.get('api/v1/user/tags/search/', { params: { search } })
}

// 如需分别拉取，也可使用下列两个（当前页面未使用，保留以备扩展）
export async function listInterests(search = '') {
  return client.get('api/v1/user/tags/interests/', { params: { search } })
}

export async function listAbilities(search = '') {
  return client.get('api/v1/user/tags/abilities/', { params: { search } })
}
