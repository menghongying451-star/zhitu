/**
 * 创建带最大数量限制的消息函数
 * @param {Object} options - 配置项
 * @param {number} [options.maxCount=3] - 最大消息显示数量，默认3
 * @returns {Function} 带数量限制的消息函数（支持success/warning/info/error）
 */
const createLimitedMessage = ({ maxCount = 3 } = {}) => {
  // 存储当前显示的消息实例（每个配置对应独立的实例列表）
  let messageInstances = []

  // 基础消息函数：处理数量限制和实例管理
  const limitedMessage = (options) => {
    // 超过最大数量时，关闭最早的消息
    if (messageInstances.length >= maxCount) {
      const oldestInstance = messageInstances.shift() // 移除数组第一个元素（最早的消息）
      oldestInstance.close() // 关闭该消息
    }

    // 创建新消息实例
    const instance = ElMessage(options)

    // 将新实例存入数组
    messageInstances.push(instance)

    // 重写实例的close方法：移除数组中对应的实例
    const originalClose = instance.close
    instance.close = function () {
      const index = messageInstances.indexOf(instance)
      if (index !== -1) {
        messageInstances.splice(index, 1) // 从数组中移除当前实例
      }
      originalClose() // 执行原close方法
    }

    return instance
  }

  // 为4种消息类型（success/warning/info/error）添加快捷方法
  ;['success', 'warning', 'info', 'error'].forEach((type) => {
    limitedMessage[type] = (options) => {
      // 如果传入的是字符串，直接作为message内容
      if (typeof options === 'string') {
        return limitedMessage({
          message: options,
          type
        })
      }
      // 如果传入的是对象，指定type后调用基础函数
      return limitedMessage({
        ...options,
        type
      })
    }
  })

  return limitedMessage
}

// 默认导出：使用默认最大数量（3）的消息函数
export default createLimitedMessage()

// 同时导出创建函数，允许用户自定义配置
export { createLimitedMessage }
