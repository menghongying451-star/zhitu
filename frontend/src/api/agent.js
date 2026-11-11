import request, { baseURL } from '@/utils/request'
import { useAuthStore } from '@/stores'

/**
 * Python 版智能体接口（替代 Dify）
 *  GET  /api/v1/agent/<name>/        智能体信息
 *  POST /api/v1/agent/<name>/chat/   对话（SSE 流式）
 *
 * name: wenshi(项目问答) | zhitu(方向测定与推荐) | tianbao(对话式发布需求)
 */

export function getAgentMeta(name) {
  return request.get(`/api/v1/agent/${name}/`)
}

/* ---------- 历史对话 ---------- */
// 当前用户的会话列表；agent 可选：zhitu / wenshi / tianbao
export function listConversations(agent) {
  return request.get('/api/v1/agent/conversations/', { params: agent ? { agent } : {} })
}
// 单个会话（含全部消息）
export function getConversation(id) {
  return request.get(`/api/v1/agent/conversations/${id}/`)
}
export function deleteConversation(id) {
  return request.delete(`/api/v1/agent/conversations/${id}/`)
}
export function clearConversations() {
  return request.delete('/api/v1/agent/conversations/')
}

function chatUrl(name) {
  const base = baseURL || `${window.location.origin}/`
  return new URL(`api/v1/agent/${name}/chat/`, base.endsWith('/') ? base : `${base}/`).toString()
}

/**
 * 流式对话
 * @param {string} name 智能体名
 * @param {object} payload { query, conversationId, inputs, file }
 * @param {object} handlers { onEvent(ev) } 每收到一个 SSE 事件回调一次
 * @param {AbortSignal} signal 用于“停止生成”
 */
export async function streamAgentChat(name, payload, handlers = {}, signal) {
  const authStore = useAuthStore()
  // token 过期时先走一次 axios（拦截器会自动刷新 token）
  if (authStore.isTokenExpired() && authStore.refreshToken) {
    try {
      await getAgentMeta(name)
    } catch {
      /* 刷新失败交给下面的请求报错 */
    }
  }

  const form = new FormData()
  form.append('query', payload.query || '')
  if (payload.conversationId) form.append('conversation_id', payload.conversationId)
  form.append('inputs', JSON.stringify(payload.inputs || {}))
  if (payload.file) form.append('file', payload.file)

  const headers = {}
  if (authStore.token) headers.Authorization = `Bearer ${authStore.token}`

  const resp = await fetch(chatUrl(name), { method: 'POST', body: form, headers, signal })
  if (!resp.ok) {
    let detail = `请求失败（${resp.status}）`
    try {
      const data = await resp.json()
      detail = data.detail || data.message || detail
    } catch {
      /* ignore */
    }
    if (resp.status === 401) detail = '登录已过期，请刷新页面后重新登录'
    throw new Error(detail)
  }

  const reader = resp.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''
  for (;;) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    let idx
    while ((idx = buffer.indexOf('\n\n')) !== -1) {
      const block = buffer.slice(0, idx)
      buffer = buffer.slice(idx + 2)
      for (const line of block.split('\n')) {
        if (!line.startsWith('data:')) continue
        try {
          handlers.onEvent?.(JSON.parse(line.slice(5).trim()))
        } catch {
          /* 忽略无法解析的行 */
        }
      }
    }
  }
}
