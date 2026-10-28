import axios from 'axios'
import { useAuthStore } from '@/stores'
import router from '@/router'
import limitedMessage from './limitedMessage'

// 请求基础URL
const baseURL = import.meta.env.VITE_BASE_URL
// WebSocket基础URL
const baseWsURL = import.meta.env.VITE_BASE_WS_URL

const instance = axios.create({
  // 基础地址，超时时间
  baseURL,
  timeout: 16000
})

// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    // 携带token
    const authStore = useAuthStore()
    if (!authStore.isTokenExpired()) {
      config.headers.Authorization = `Bearer ${authStore.token}`
    } else {
      delete config.headers.Authorization
    }
    return config
  },
  (err) => Promise.reject(err)
)

let isRefreshing = false // 是否正在刷新 token
let requestsQueue = [] // 请求队列

/* ========= 新增：公共接口与受保护路径判定 ========= */
// 可以匿名访问（即使后端目前返回 401 也不应触发刷新）的接口前缀
const PUBLIC_ENDPOINT_PREFIXES = [
  '/api/v1/dashboard/', // 首页看板统计
  '/api/v1/public/' // 预留其它公共接口
]

// 需要用户已登录的前端路由前缀（用于未登录时 401 的跳转判定）
const PROTECTED_PATH_PREFIXES = ['/student/', '/enterprise/', '/admin/']

function isPublicEndpoint(url = '') {
  try {
    const u = new URL(url, window.location.origin)
    return PUBLIC_ENDPOINT_PREFIXES.some((prefix) => u.pathname.startsWith(prefix))
  } catch {
    return PUBLIC_ENDPOINT_PREFIXES.some((prefix) => url.startsWith(prefix))
  }
}

function isProtectedFrontendPath(pathname = window.location.pathname) {
  return PROTECTED_PATH_PREFIXES.some((p) => pathname.startsWith(p))
}
/* ================================================= */

// 响应拦截器
instance.interceptors.response.use(
  (res) => {
    // 业务成功正常返回
    if (res.status >= 200 && res.status < 300) {
      return res
    }
    // 处理业务失败, 给错误提示，抛出错误
    limitedMessage.error(res.data.message || '服务异常')
    return Promise.reject(res.data)
  },
  async (err) => {
    // 错误的特殊情况 => 401 权限不足 或 token 过期 => 拦截到登录
    if (err.response?.status === 401 && location.pathname !== '/login') {
      const originalRequest = err.config
      const authStore = useAuthStore()

      const hasAccess = !!authStore.token
      const hasRefresh = !!authStore.refreshToken
      const publicApi = isPublicEndpoint(originalRequest?.url)
      const protectedPage = isProtectedFrontendPath()

      // 未登录情况下的处理
      if (!hasAccess || !hasRefresh) {
        // 受保护页面：跳转登录
        if (protectedPage) {
          authStore.removeToken()
          authStore.removeRefreshToken()
          router.push('/login')
        }
        // 公共页面：直接拒绝，不触发刷新逻辑（避免首页 401 刷新风暴）
        return Promise.reject(err)
      }

      // 已登录才尝试刷新 token，后续保持原逻辑
      // 如果是刷新 token 的请求本身失败，直接跳转登录
      if (originalRequest.url === 'api/v1/auth/refresh/') {
        authStore.removeToken()
        authStore.removeRefreshToken()
        router.push('/login')
        return Promise.reject(err)
      }

      // 已经重试过，直接跳转登录
      if (originalRequest._retry) {
        authStore.removeToken()
        authStore.removeRefreshToken()
        router.push('/login')
        return Promise.reject(err)
      }

      originalRequest._retry = true // 标记为已重试

      // 如果未在刷新，开始刷新 token
      if (!isRefreshing) {
        isRefreshing = true

        try {
          // 使用 refreshToken 调用接口获取新 token
          // 注意：这里仍使用同一个 axios 实例。如果后端需要无 Authorization 可选加 headers 覆盖。
          const refreshRes = await instance.post('api/v1/auth/refresh/', {
            refresh_token: authStore.refreshToken
          })

          // 更新 store 和 axios 默认 headers
          const { access_token, refresh_token } = refreshRes.data.data
          authStore.setToken(access_token)
          authStore.setRefreshToken(refresh_token)
          instance.defaults.headers.Authorization = `Bearer ${access_token}`

          // 重试原始请求
          const retryRes = await instance(originalRequest)

          // 重试队列中的请求并清空队列
          requestsQueue.forEach(({ resolve, reject, config }) => {
            instance(config).then(resolve).catch(reject)
          })
          requestsQueue = []

          return retryRes
        } catch (refreshErr) {
          // 刷新失败，清理并跳转登录
          authStore.removeToken()
          authStore.removeRefreshToken()
          ElMessage.error('登录已过期，请重新登录')
          router.push('/login')

          // 拒绝所有队列中的请求
          requestsQueue.forEach(({ reject }) => {
            reject(refreshErr)
          })
          requestsQueue = []

          return Promise.reject(refreshErr)
        } finally {
          isRefreshing = false
        }
      } else {
        // 正在刷新，将请求加入队列
        return new Promise((resolve, reject) => {
          requestsQueue.push({ resolve, reject, config: originalRequest })
        })
      }
    }

    // 错误的默认情况 => 只要给提示
    const message = err.response?.data?.message ?? err.message ?? '服务错误'
    limitedMessage.error(message)
    console.error(err)
    return Promise.reject(err)
  }
)

export default instance
export { baseURL, baseWsURL }
