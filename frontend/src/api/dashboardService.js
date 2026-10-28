// src/api/dashboardService.js
import request from '@/utils/request'

/**
 * 统一解包：
 * 后端实际返回包装：
 * {
 *   status: "success",
 *   code: 200,
 *   message: "...",
 *   data: {...或 数字 或 数组},
 *   error: {}
 * }
 * unwrap 会在检测到这是包装结构时返回内部 data，否则原样返回。
 */
function unwrap(payload) {
  if (
    payload &&
    typeof payload === 'object' &&
    'data' in payload &&
    // 同时存在 status 或 code，大概率是包装层
    (payload.status !== undefined || payload.code !== undefined)
  ) {
    return payload.data
  }
  return payload
}

async function plainGet(url, fallbackDetail) {
  try {
    const res = await request.get(url)
    return unwrap(res.data)
  } catch (error) {
    const status = error?.response?.status
    if (status === 404) {
      // 交由调用处用 __404__ 决定默认值
      throw { __404__: true }
    }
    const data = error?.response?.data
    const detail = data?.detail || data?.message || fallbackDetail || '请求失败'
    throw { detail }
  }
}

const dashboardService = {
  // 1 学生学习方向占比
  async getStudyDirectionRatio() {
    return plainGet('/api/v1/dashboard/study-direction/', '获取学生学习方向占比失败')
  },

  // 2 学生目标岗位占比
  async getTargetJobRatio() {
    return plainGet('/api/v1/dashboard/target-job/', '获取学生目标岗位占比失败')
  },

  // 3 平台在线人数
  async getOnlineUsers() {
    return plainGet('/api/v1/dashboard/online-count/', '获取在线人数失败')
  },

  // 4 平台项目总数（返回对象，包含 total_projects / status_stats）
  async getTotalProjects() {
    return plainGet('/api/v1/dashboard/total-projects/', '获取项目总数失败')
  },

  // 5 平台组织数量（返回对象，包含 total_organizations / status_stats）
  async getCompanyCount() {
    return plainGet('/api/v1/dashboard/organization-count/', '获取组织数量失败')
  },

  // 6 模型问答次数（实现：从对象 data.answer_number 中取数，或支持直接返回 number）
  async getModelQACount() {
    try {
      const data = await plainGet('/api/v1/dashboard/model-qa-count/', '获取模型问答次数失败')
      if (typeof data === 'number') return data
      if (data && typeof data === 'object') {
        const n = Number(data.answer_number)
        return Number.isFinite(n) ? n : 0
      }
      return 0
    } catch (e) {
      if (e.__404__) return 0
      throw e
    }
  },

  // 7 项目领域分布（返回对象含 top_tags 等）
  async getProjectFieldDistribution() {
    return plainGet('/api/v1/dashboard/project-fields/', '获取项目领域分布失败')
  },

  // 8 高频问题词云（实现：把 data.top_tags 映射为 echarts-wordcloud 需要的 [{name,value}]）
  async getHighFreqTags() {
    try {
      const data = await plainGet('/api/v1/dashboard/high-freq-tags/', '获取词云失败')
      // 标准后端返回：{ top_tags:[{ tag_id, value, frequency }], total_returned, query_time }
      if (data && typeof data === 'object' && Array.isArray(data.top_tags)) {
        return data.top_tags
          .map((t) => {
            const name = (
              typeof t.value === 'string' ? t.value.trim() : String(t.value ?? '')
            ).replace(/\s+/g, ' ')
            const val = Number(t.frequency)
            return { name, value: Number.isFinite(val) ? val : 0 }
          })
          .filter((it) => it.name)
      }
      // 兼容其他可能结构
      if (Array.isArray(data)) {
        return data
          .map((it) => {
            if (typeof it === 'string') return { name: it, value: 1 }
            if (it && typeof it === 'object') {
              const nm = (it.name ?? it.value ?? '').toString().trim()
              const v = Number(it.value ?? it.frequency ?? it.count ?? 1)
              return nm ? { name: nm, value: Number.isFinite(v) ? v : 1 } : null
            }
            return null
          })
          .filter(Boolean)
      }
      if (data && typeof data === 'object') {
        if (Array.isArray(data.items)) return data.items
        if ('name' in data && 'value' in data) return [data]
      }
      return []
    } catch (e) {
      if (e.__404__) return []
      throw e
    }
  },

  // 9 用户注册趋势（返回对象含 monthly_stats / summary）
  async getUserGrowthOverTime() {
    return plainGet('/api/v1/dashboard/user-registration/', '获取用户注册趋势失败')
  }
}

export { dashboardService }
export default dashboardService
