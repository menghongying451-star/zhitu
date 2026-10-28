import request from '@/utils/request'

// 原函数保持
export function getEvaluationDetail(projectId) {
  return request({
    url: `/api/v1/projectscore/evaluations/${projectId}/`,
    method: 'get'
  })
}

// 原安全包装保持
export async function getEvaluationDetailSafe(projectId) {
  try {
    const resp = await getEvaluationDetail(projectId)
    const payload = resp?.data
    const inner = payload && payload.data ? payload.data : payload
    return { exists: true, data: inner, raw: resp }
  } catch (err) {
    const status = err?.response?.status
    if (status === 404) {
      return { exists: false, data: null, raw: err?.response }
    }
    throw err
  }
}

/**
 * 新增：允许 404 返回（不抛异常）
 * 说明：status=404 时 axios 仍 resolve；调用方用 resp.status === 404 判断“暂无评分”
 */
export function getEvaluationDetailAllow404(projectId) {
  return request({
    url: `/api/v1/projectscore/evaluations/${projectId}/`,
    method: 'get',
    validateStatus: (status) => (status >= 200 && status < 300) || status === 404
  })
}
