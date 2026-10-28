import request from '@/utils/request'

/**
 * 获取“已关注=已收藏”的需求列表
 * 服务端路径：GET /api/v1/project/favorites/requirements/
 * 支持参数：page, page_size, status, organization_id, search
 */
export function fetchFollowedDemands(params) {
  return request.get('/api/v1/project/favorites/requirements/', { params })
}

/**
 * 关注=收藏 需求（切换为已收藏）
 * 服务端路径：POST /api/v1/project/requirement/favorite/
 * Body: { requirement_id }
 */
export function followDemand(demandId) {
  return request.post('/api/v1/project/requirement/favorite/', {
    requirement_id: demandId
  })
}

/**
 * 取消关注=取消收藏 需求
 * 说明：后端是“切换收藏状态”的单一接口，所以这里调用同一个接口实现取消
 * 前提：只在“已收藏”的场景调用即可达到取消收藏效果
 */
export function unfollowDemand(demandId) {
  return request.post('/api/v1/project/requirement/favorite/', {
    requirement_id: demandId
  })
}

/**
 * 提示：
 * - 批量关注状态接口在后端并不存在。请改为使用需求列表中的 is_favorited 字段来渲染状态。
 * - 若确需批量确认状态，可在拉取列表后于前端聚合，而非请求后端。
 */
