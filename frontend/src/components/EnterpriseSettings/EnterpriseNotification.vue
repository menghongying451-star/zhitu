<!-- components/settings/NotificationSettings.vue -->
<template>
  <div class="notification-settings">
    <el-row :gutter="20">
      <el-col :lg="12" :xs="24">
        <div class="main-settings">
          <!-- 邮件通知 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>邮件通知</h3>
            </template>

            <div class="setting-list">
              <div class="setting-item">
                <div class="setting-info">
                  <h4>项目更新</h4>
                  <p>项目状态变更时通知</p>
                </div>
                <el-switch v-model="notificationData.email.projectUpdate" />
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <h4>新申请通知</h4>
                  <p>有新的人才申请时</p>
                </div>
                <el-switch v-model="notificationData.email.newApplication" />
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <h4>系统维护</h4>
                  <p>系统升级维护通知</p>
                </div>
                <el-switch v-model="notificationData.email.systemMaintenance" />
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <h4>营销推广</h4>
                  <p>产品功能和活动推荐</p>
                </div>
                <el-switch v-model="notificationData.email.marketing" />
              </div>
            </div>
          </el-card>

          <!-- 短信通知 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>短信通知</h3>
            </template>

            <div class="setting-list">
              <div class="setting-item">
                <div class="setting-info">
                  <h4>安全警报</h4>
                  <p>异常登录和安全事件</p>
                </div>
                <el-switch v-model="notificationData.sms.securityAlert" />
              </div>

              <div class="setting-item">
                <div class="setting-info">
                  <h4>验证码</h4>
                  <p>登录和操作验证</p>
                </div>
                <el-switch v-model="notificationData.sms.verificationCode" />
              </div>
            </div>
          </el-card>
        </div>
      </el-col>

      <el-col :lg="12" :xs="24">
        <div class="side-settings">
          <!-- 通知频率 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>通知频率</h3>
            </template>

            <el-form label-position="top" size="large">
              <el-form-item label="邮件摘要频率">
                <el-select v-model="notificationData.frequency" style="width: 100%">
                  <el-option label="实时通知" value="实时通知" />
                  <el-option label="每日摘要" value="每日摘要" />
                  <el-option label="每周摘要" value="每周摘要" />
                  <el-option label="关闭" value="关闭" />
                </el-select>
              </el-form-item>

              <el-form-item label="推送时间">
                <div class="time-range">
                  <el-time-picker
                    v-model="pushTimeStart"
                    placeholder="开始时间"
                    format="HH:mm"
                    value-format="HH:mm"
                  />
                  <span class="time-separator">至</span>
                  <el-time-picker
                    v-model="pushTimeEnd"
                    placeholder="结束时间"
                    format="HH:mm"
                    value-format="HH:mm"
                  />
                </div>
                <p class="time-tip">仅在此时间段内发送非紧急通知</p>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- 通知历史 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>最近通知</h3>
            </template>

            <div class="notification-history">
              <div class="history-item info">
                <div class="history-icon">
                  <el-icon><InfoFilled /></el-icon>
                </div>
                <div class="history-content">
                  <div class="history-title">项目"智能巡检系统"进度更新</div>
                  <div class="history-time">2小时前</div>
                </div>
              </div>

              <div class="history-item success">
                <div class="history-icon">
                  <el-icon><CircleCheckFilled /></el-icon>
                </div>
                <div class="history-content">
                  <div class="history-title">新成员李华已成功加入团队</div>
                  <div class="history-time">5小时前</div>
                </div>
              </div>

              <div class="history-item warning">
                <div class="history-icon">
                  <el-icon><WarningFilled /></el-icon>
                </div>
                <div class="history-content">
                  <div class="history-title">系统将于今晚22:00进行维护</div>
                  <div class="history-time">1天前</div>
                </div>
              </div>
            </div>

            <el-button type="default" class="view-all-btn"> 查看全部通知 </el-button>
          </el-card>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { InfoFilled, CircleCheckFilled, WarningFilled } from '@element-plus/icons-vue'
import { useEnterpriseStore } from '@/stores'

const settingsStore = useEnterpriseStore()

const notificationData = computed({
  get: () => settingsStore.notifications,
  set: (value) => settingsStore.updateNotifications(value)
})

const pushTimeStart = computed({
  get: () => notificationData.value.pushTime.start,
  set: (value) => {
    notificationData.value.pushTime.start = value
  }
})

const pushTimeEnd = computed({
  get: () => notificationData.value.pushTime.end,
  set: (value) => {
    notificationData.value.pushTime.end = value
  }
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

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }
  }

  .setting-list {
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

  .notification-history {
    .history-item {
      display: flex;
      align-items: flex-start;
      padding: 12px;
      border-radius: 8px;
      border-left: 4px solid;
      margin-bottom: 12px;

      &:last-child {
        margin-bottom: 0;
      }

      &.info {
        background: #f0f9ff;
        border-left-color: #3b82f6;

        .history-icon {
          color: #3b82f6;
        }
      }

      &.success {
        background: #f0fdf4;
        border-left-color: #10b981;

        .history-icon {
          color: #10b981;
        }
      }

      &.warning {
        background: #fffbeb;
        border-left-color: #f59e0b;

        .history-icon {
          color: #f59e0b;
        }
      }

      .history-icon {
        margin: 2px 12px 0 0;
        flex-shrink: 0;
      }

      .history-content {
        .history-title {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
          margin-bottom: 4px;
        }

        .history-time {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  .view-all-btn {
    width: 100%;
    margin-top: 16px;
  }
}

@media (max-width: 992px) {
  .notification-settings {
    .side-settings {
      margin-top: 20px;
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
  }
}
</style>
