// 学生端“企业需求总览”接口封装（使用统一的 axios 实例）
import client from '@/utils/request'

const DEFAULTS = {
  page: 1,
  page_size: 10
}

// 统一封装：始终返回 { data: <payload> }，兼容调用方解构 const { data } = await xxx
function wrap(res) {
  // axios 响应：res.data 为后端 payload
  return { data: res?.data }
}

/**
 * 需求列表允许的查询参数白名单
 */
function sanitizeRequirementParams(raw = {}) {
  const allowed = new Set([
    'page',
    'page_size',
    'keyword',
    'search',
    'time_start',
    'time_end',
    'time', // 兼容后端旧聚合时间字段
    'tag1_ids',
    'tag2_ids',
    'q',
    'sort_type'
  ])
  const ret = {}
  Object.keys(raw).forEach((k) => {
    if (!allowed.has(k)) return
    const v = raw[k]
    if (v === '' || v === undefined || v === null) return
    ret[k] = v
  })
  return ret
}

/**
 * 获取需求列表
 * 正确后端路径（旧制式）：/api/v1/project/requirement/list/
 */
export async function getRequirementList(params = {}) {
  const merged = { ...DEFAULTS, ...params }
  const cleaned = sanitizeRequirementParams(merged)
  const res = await client.get('/api/v1/project/requirement/list/', {
    params: cleaned
  })
  return wrap(res)
}

/**
 * 获取需求详情
 * 路径：/api/v1/project/requirement/{id}/
 */
export async function getRequirementDetail(id) {
  if (id === undefined || id === null) {
    return Promise.reject(new Error('缺少需求 id'))
  }
  const res = await client.get(`/api/v1/project/requirement/${id}/`)
  return wrap(res)
}
