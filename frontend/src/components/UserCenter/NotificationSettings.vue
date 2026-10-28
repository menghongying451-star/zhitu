<template>
  <div class="notification-settings">
    <el-row :gutter="20">
      <el-col :lg="12" :xs="24">
        <div class="main-settings">
          <!-- 通知方式 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>通知方式</h3>
            </template>

            <div class="setting-list">
              <div class="setting-item">
                <div class="setting-info">
                  <h4>实时通知</h4>
                  <p>浏览器内实时推送通知</p>
                </div>
                <el-switch v-model="preferences.enable_websocket" @change="updateSettings" />
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <h4>邮件通知</h4>
                  <p>重要通知发送到邮箱</p>
                </div>
                <el-switch v-model="preferences.enable_email" @change="updateSettings" />
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <h4>短信通知</h4>
                  <p>紧急通知发送短信</p>
                </div>
                <el-switch v-model="preferences.enable_sms" @change="updateSettings" disabled />
              </div>
            </div>
          </el-card>

          <!-- 通知类型设置 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <div class="card-header">
                <h3>通知类型</h3>
                <span class="auto-save-tip" v-if="saving">
                  <el-icon class="saving-icon"><Loading /></el-icon>
                  保存中...
                </span>
              </div>
            </template>

            <div class="setting-list scrollable">
              <div
                v-for="(typeInfo, typeCode) in notificationTypeMap"
                :key="typeCode"
                class="setting-item"
              >
                <div class="setting-info">
                  <h4>{{ typeInfo.name }}</h4>
                  <p>{{ typeInfo.description }}</p>
                </div>
                <el-switch
                  v-model="preferences.type_preferences[typeCode]"
                  @change="updateSettings"
                />
              </div>
            </div>
          </el-card>
        </div>
      </el-col>

      <el-col :lg="12" :xs="24">
        <div class="side-settings">
          <!-- 免打扰设置 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>免打扰设置</h3>
            </template>

            <el-form label-position="top" size="large">
              <el-form-item>
                <div class="setting-item">
                  <div class="setting-info">
                    <h4>一键免打扰</h4>
                    <p>暂停所有非紧急通知</p>
                  </div>
                  <el-switch v-model="preferences.do_not_disturb" @change="updateSettings" />
                </div>
              </el-form-item>

              <el-form-item label="免打扰时间段" v-if="!preferences.do_not_disturb">
                <div class="time-range">
                  <el-time-picker
                    v-model="quietStartTime"
                    placeholder="开始时间"
                    format="HH:mm"
                    value-format="HH:mm:ss"
                    @change="updateQuietTime"
                  />
                  <span class="time-separator">至</span>
                  <el-time-picker
                    v-model="quietEndTime"
                    placeholder="结束时间"
                    format="HH:mm"
                    value-format="HH:mm:ss"
                    @change="updateQuietTime"
                  />
                </div>
                <p class="time-tip">
                  需同时设置开始时间与结束时间，在此时间段内将暂停非紧急通知推送
                </p>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 其他操作 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>其他操作</h3>
            </template>

            <div class="action-buttons">
              <el-button
                type="default"
                :loading="resetting"
                @click="resetToDefault"
                style="width: 100%"
              >
                恢复默认设置
              </el-button>
            </div>

            <p class="auto-save-note">
              <el-icon><InfoFilled /></el-icon>
              所有设置将自动保存
            </p>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { Loading, InfoFilled } from '@element-plus/icons-vue'
import { notificationService } from '@/api/'

// 状态管理
const loading = ref(false)
const saving = ref(false)
const resetting = ref(false)

// 通知偏好设置
const preferences = reactive({
  enable_websocket: true,
  enable_email: false,
  enable_sms: false,
  type_preferences: {},
  quiet_start_time: null,
  quiet_end_time: null,
  do_not_disturb: false
})

// 通知类型映射
const notificationTypeMap = ref({})

// 时间处理
const quietStartTime = computed({
  get: () => preferences.quiet_start_time,
  set: (value) => {
    preferences.quiet_start_time = value
  }
})

const quietEndTime = computed({
  get: () => preferences.quiet_end_time,
  set: (value) => {
    preferences.quiet_end_time = value
  }
})

// 获取通知类型列表
const fetchNotificationTypes = async () => {
  try {
    const response = await notificationService.getNotificationTypes()
    const typeMap = {}

    response.data.results.forEach((type) => {
      if (type.is_active) {
        typeMap[type.code] = {
          name: type.name,
          description: type.description,
          category: type.category
        }
      }
    })

    notificationTypeMap.value = typeMap
  } catch (error) {
    ElMessage.error('获取通知类型失败：' + (error.message || '请稍后重试'))
  }
}

// 获取用户通知偏好
const fetchUserPreferences = async () => {
  try {
    loading.value = true
    const response = await notificationService.getUserNotificationSettings()
    Object.assign(preferences, response.data)
  } catch (error) {
    ElMessage.error('获取通知设置失败：' + (error.message || '请稍后重试'))
  } finally {
    loading.value = false
  }
}

// 更新设置（防抖处理）
let updateTimer = null
const updateSettings = () => {
  if (updateTimer) {
    clearTimeout(updateTimer)
  }

  updateTimer = setTimeout(async () => {
    try {
      saving.value = true

      const settingsToUpdate = {
        enable_websocket: preferences.enable_websocket,
        enable_email: preferences.enable_email,
        enable_sms: preferences.enable_sms,
        type_preferences: preferences.type_preferences,
        quiet_start_time: preferences.quiet_start_time,
        quiet_end_time: preferences.quiet_end_time,
        do_not_disturb: preferences.do_not_disturb
      }

      await notificationService.updateUserNotificationSettings(settingsToUpdate)

      ElMessage.success('设置保存成功')
    } catch (error) {
      ElMessage.error('保存设置失败：' + (error.message || '请稍后重试'))
    } finally {
      saving.value = false
    }
  }, 800) // 800ms防抖
}

// 更新免打扰时间
const updateQuietTime = () => {
  updateSettings()
}

// 重置为默认设置
const resetToDefault = async () => {
  try {
    await ElMessageBox.confirm('确定要恢复默认通知设置吗？此操作不可撤销。', '确认重置', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    resetting.value = true
    await notificationService.resetUserNotificationSettings()

    // 重新获取设置
    await fetchUserPreferences()
    ElMessage.success('已恢复默认通知设置')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('重置设置失败：' + (error.message || '请稍后重试'))
    }
  } finally {
    resetting.value = false
  }
}

// 初始化
onMounted(async () => {
  await Promise.all([fetchNotificationTypes(), fetchUserPreferences()])
})
</script>

<style lang="scss" scoped>
.notification-settings {
  .main-settings,
  .side-settings {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .setting-card {
    border: 1px solid #e4e7ed;

    :deep(.el-card__header) {
      background: #fafafa;
      border-bottom: 1px solid #e4e7ed;

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
  }

  .auto-save-tip {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: #409eff;

    .saving-icon {
      animation: rotate 1s linear infinite;
    }
  }

  .setting-list {
    &.scrollable {
      max-height: 400px;
      overflow-y: auto;

      // 自定义滚动条样式
      &::-webkit-scrollbar {
        width: 6px;
      }

      &::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 3px;
      }

      &::-webkit-scrollbar-thumb {
        background: #c1c1c1;
        border-radius: 3px;

        &:hover {
          background: #a8a8a8;
        }
      }
    }

    .setting-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 16px;
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      margin-bottom: 12px;

      &:last-child {
        margin-bottom: 0;
      }

      .setting-info {
        flex: 1;
        margin-right: 16px;

        h4 {
          margin: 0 0 4px 0;
          font-size: 14px;
          font-weight: 500;
          color: #303133;
        }

        p {
          margin: 0;
          font-size: 12px;
          color: #909399;
          line-height: 1.4;
        }
      }
    }
  }

  .time-range {
    display: flex;
    align-items: center;
    gap: 12px;

    .time-separator {
      color: #909399;
      font-size: 14px;
    }
  }

  .time-tip {
    margin: 8px 0 0 0;
    font-size: 12px;
    color: #909399;
  }

  .action-buttons {
    margin-bottom: 16px;
  }

  .auto-save-note {
    display: flex;
    align-items: center;
    gap: 6px;
    margin: 0;
    padding: 12px;
    background: #f0f9ff;
    border: 1px solid #e1f5fe;
    border-radius: 6px;
    font-size: 12px;
    color: #666;
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 992px) {
  .notification-settings {
    .side-settings {
      margin-top: 20px;
    }

    .setting-list.scrollable {
      max-height: 300px;
    }
  }
}

@media (max-width: 768px) {
  .notification-settings {
    .time-range {
      flex-direction: column;
      align-items: stretch;
      gap: 8px;

      .time-separator {
        text-align: center;
      }
    }

    .setting-list.scrollable {
      max-height: 250px;
    }
  }
}
</style>
