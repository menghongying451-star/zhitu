import request from '@/utils/request'

// 切换收藏状态（未收藏->收藏；已收藏->取消）
export function toggleFavoriteRequirement(requirementId) {
  return request.post('/api/v1/project/requirement/favorite/', {
    requirement_id: String(requirementId)
  })
}

// 获取当前学生用户收藏的需求列表（分页/筛选）
export function getFavoriteRequirements(params = {}) {
  return request.get('/api/v1/project/favorites/requirements/', { params })
}
