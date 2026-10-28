import { authService } from '@/api'
import { useAuthStore } from '@/stores'
const authStore = useAuthStore()
export const refresh = async () => {
  const res = await authService.refresh(authStore.refreshToken)
  authStore.setToken(res.data.access_token)
  authStore.setRefreshToken(res.data.refresh_token)
}

// 简化版：根据你们实际登录存储调整字段名
export function getCurrentUser() {
  try {
    const json = localStorage.getItem('currentUser')
    if (json) return JSON.parse(json)
  } catch {
    return null
  }
  return null
}

export function getCurrentUserId() {
  const user = getCurrentUser()
  // 按照可能的后端字段做多重兜底，按需微调
  return user?.id ?? user?.user_id ?? user?.userid ?? null
}

export function getCurrentUsername() {
  const user = getCurrentUser()
  return user?.username ?? user?.real_name ?? ''
}

// 如果只保存了 token，可解析 JWT 获取 sub/user_id
export function getUserIdFromToken() {
  try {
    const token = localStorage.getItem('token')
    if (!token) return null
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload?.sub ?? payload?.user_id ?? null
  } catch {
    return null
  }
}
