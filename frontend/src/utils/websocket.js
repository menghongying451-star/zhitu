// src/utils/websocket.js
import { useUserStore, useAuthStore } from '@/stores'

class WebSocketService {
  constructor() {
    this.ws = null
    this.reconnectAttempts = 0
    this.maxReconnectAttempts = 5
    this.reconnectInterval = 3000
    this.heartbeatInterval = 1000 * 60 * 10 // 10分钟
    this.heartbeatTimer = null
    this.isManualClose = false
    this.listeners = new Map()
  }

  // 连接WebSocket
  connect() {
    const userStore = useUserStore()
    const authStore = useAuthStore()
    const userId = userStore.user?.id
    const token = authStore.token

    if (!userId) {
      console.error('用户未登录，无法建立WebSocket连接')
      return
    }

    if (!token) {
      console.error('用户token不存在，无法建立WebSocket连接')
      return
    }

    // 在URL中携带token作为查询参数
    const wsUrl = `${import.meta.env.VITE_BASE_WS_URL}ws/notification/${userId}/?token=${encodeURIComponent(token)}`

    try {
      this.ws = new WebSocket(wsUrl)
      this.setupEventListeners()
    } catch (error) {
      console.error('WebSocket连接失败:', error)
      this.handleReconnect()
    }
  }

  // 设置事件监听器
  setupEventListeners() {
    this.ws.onopen = () => {
      console.log('WebSocket连接成功')
      this.reconnectAttempts = 0
      this.startHeartbeat()
      this.emit('connected')
    }

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        this.handleMessage(data)
      } catch (error) {
        console.error('解析WebSocket消息失败:', error)
      }
    }

    this.ws.onclose = (event) => {
      console.log('WebSocket连接关闭:', event.code, event.reason)
      this.stopHeartbeat()
      this.emit('disconnected')

      // 如果是认证失败（code 1008），不要重连
      if (event.code === 1008) {
        console.error('WebSocket认证失败，请重新登录')
        this.emit('authFailed')
        return
      }

      if (!this.isManualClose) {
        this.handleReconnect()
      }
    }

    this.ws.onerror = (error) => {
      console.error('WebSocket错误:', error)
      this.emit('error', error)
    }
  }

  // 处理接收到的消息
  handleMessage(data) {
    switch (data.type) {
      case 'unread_count':
        this.emit('unreadCount', data.count)
        break
      case 'notification':
        this.emit('notification', data.notification)
        break
      default:
        // 如果没有type字段，可能是通知消息
        if (data.id && data.notification_type) {
          this.emit('notification', data)
        }
    }
  }

  // 发送心跳
  startHeartbeat() {
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, this.heartbeatInterval)
  }

  // 停止心跳
  stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
    }
  }

  // 重连逻辑
  handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++
      console.log(`WebSocket重连尝试 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)

      setTimeout(() => {
        this.connect()
      }, this.reconnectInterval * this.reconnectAttempts)
    } else {
      console.error('WebSocket重连失败，已达到最大重连次数')
      this.emit('maxReconnectAttemptsReached')
    }
  }

  // 添加事件监听器
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event).push(callback)
  }

  // 移除事件监听器
  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event)
      const index = callbacks.indexOf(callback)
      if (index > -1) {
        callbacks.splice(index, 1)
      }
    }
  }

  // 触发事件
  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach((callback) => {
        try {
          callback(data)
        } catch (error) {
          console.error('WebSocket事件回调执行失败:', error)
        }
      })
    }
  }

  // 发送消息
  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    } else {
      console.warn('WebSocket未连接，无法发送消息')
    }
  }

  // 关闭连接
  close() {
    this.isManualClose = true
    this.stopHeartbeat()
    if (this.ws) {
      this.ws.close()
    }
    this.listeners.clear()
  }

  // 获取连接状态
  getState() {
    return this.ws ? this.ws.readyState : WebSocket.CLOSED
  }

  // 是否已连接
  isConnected() {
    return this.ws && this.ws.readyState === WebSocket.OPEN
  }
}

// 创建单例实例
export const websocketService = new WebSocketService()
export default WebSocketService
