import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore(
  'auth',
  () => {
    const token = ref('')
    const tokenExpiry = ref(null) // 用于存储过期时间（时间戳）

    // 解码JWT获取payload
    const decodeJwt = (jwtToken) => {
      try {
        // JWT由三部分组成：header.payload.signature，我们只需要payload
        const base64Url = jwtToken.split('.')[1]
        // 处理base64url格式（替换特殊字符）
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
        // 解码并转换为JSON对象
        const jsonPayload = decodeURIComponent(
          atob(base64)
            .split('')
            .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
            .join('')
        )
        return JSON.parse(jsonPayload)
      } catch (e) {
        console.error('JWT解码失败:', e)
        return null
      }
    }

    const setToken = (newToken) => {
      if (newToken) {
        token.value = newToken
        // 解码获取过期时间
        const payload = decodeJwt(newToken)
        if (payload && payload.exp) {
          // 保存过期时间（Unix时间戳，单位：秒）
          tokenExpiry.value = payload.exp * 1000 // 转换为毫秒，方便与Date.now()比较
        }
      } else {
        // 如果newToken为空，清空存储
        token.value = ''
        tokenExpiry.value = null
      }
    }

    const removeToken = () => {
      token.value = ''
      tokenExpiry.value = null
    }

    // 新增：检查token是否已过期
    const isTokenExpired = () => {
      if (!token.value || !tokenExpiry.value) {
        return true // 没有token或过期时间，视为已过期
      }
      return Date.now() > tokenExpiry.value
    }

    const refreshToken = ref('')
    const setRefreshToken = (newToken) => {
      refreshToken.value = newToken
    }
    const removeRefreshToken = () => {
      refreshToken.value = ''
    }

    const logindata = ref({
      type: 'password',
      username_or_email_or_phone: '',
      password: '',
      email: ''
    })
    const setlogindata = (obj) => {
      logindata.value = obj
    }
    const removelogindata = () => {
      logindata.value = {
        type: 'password',
        username_or_email_or_phone: '',
        password: '',
        email: ''
      }
    }
    const rememberme = ref(false)
    const setRememberme = (newRememberme) => {
      rememberme.value = newRememberme
    }

    return {
      token,
      tokenExpiry,
      setToken,
      removeToken,
      isTokenExpired,
      refreshToken,
      setRefreshToken,
      removeRefreshToken,
      logindata,
      setlogindata,
      removelogindata,
      rememberme,
      setRememberme
    }
  },
  {
    persist: {
      enabled: true,
      storage: localStorage,
      paths: ['token', 'tokenExpiry', 'refreshToken', 'logindata', 'rememberme']
    }
  }
)
