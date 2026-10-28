// 学生端：需求结果发布/查询
import client from '@/utils/request'

const FEATURE_RESULTS =
  String(import.meta.env.VITE_FEATURE_REQUIREMENT_RESULTS || '').toLowerCase() === 'true'

// 正常化一个“空结果”，用于后端未就绪时优雅降级
const emptyResult = {
  data: {
    status: 'success',
    code: 200,
    message: 'not published',
    data: {
      published_at: null,
      rankings: []
    }
  }
}

// 获取需求的结果（排名）
// 关闭功能时直接返回空结构，避免 404
export async function getRequirementResult(requirementId) {
  if (!FEATURE_RESULTS) return emptyResult
  // 若功能开启，但后端暂未提供，也不要二次补打，统一让调用方兜底即可
  const res = await client.get(`/api/v1/project/requirement/${requirementId}/results`)
  return res
}

// 发布或更新需求结果（排名）
// 关闭功能时直接返回空结构，避免 404
export async function publishRequirementResult(requirementId, payload) {
  if (!FEATURE_RESULTS) return emptyResult
  const res = await client.post(
    `/api/v1/project/requirement/${requirementId}/results/publish`,
    payload
  )
  return res
}

// === 修改：获取项目评分公示后的正式排名（对 422 进行静默兼容） ===
export async function getProjectScoreRanking(requirementId) {
  if (requirementId === undefined || requirementId === null) {
    return Promise.reject(new Error('缺少 requirementId'))
  }

  // 对 422 放行，不让 axios 抛错 -> validateStatus 里手动允许
  const res = await client.get(`/api/v1/projectscore/requirements/${requirementId}/ranking/view/`, {
    validateStatus: (s) => (s >= 200 && s < 300) || s === 422
  })

  // 后端尚未公示 / 条件未满足：返回统一 pending 结构
  if (res.status === 422) {
    return {
      status: 'pending', // 自定义状态：调用方可用 status !== 'success' 判断
      code: 422,
      message: res.data?.message || res.data?.detail || 'ranking not published',
      data: null
    }
  }

  // 正常成功：直接返回后端原始 payload（保持之前调用判断逻辑不变）
  return res.data
}
