<!-- components/settings/SystemConfig.vue -->
<template>
  <div class="system-config">
    <el-row :gutter="20">
      <el-col :lg="12" :xs="24">
        <div class="main-content">
          <!-- 系统偏好 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>系统偏好</h3>
            </template>

            <el-form :model="systemData" label-position="top" size="large">
              <el-form-item label="界面语言">
                <el-select v-model="systemData.language" style="width: 100%">
                  <el-option label="简体中文" value="简体中文" />
                  <el-option label="繁体中文" value="繁体中文" />
                  <el-option label="English" value="English" />
                </el-select>
              </el-form-item>

              <el-form-item label="时区设置">
                <el-select v-model="systemData.timezone" style="width: 100%">
                  <el-option label="北京时间 (GMT+8)" value="北京时间 (GMT+8)" />
                  <el-option label="香港时间 (GMT+8)" value="香港时间 (GMT+8)" />
                  <el-option label="新加坡时间 (GMT+8)" value="新加坡时间 (GMT+8)" />
                  <el-option label="日本时间 (GMT+9)" value="日本时间 (GMT+9)" />
                </el-select>
              </el-form-item>

              <el-form-item label="日期格式">
                <el-select v-model="systemData.dateFormat" style="width: 100%">
                  <el-option label="YYYY-MM-DD" value="YYYY-MM-DD" />
                  <el-option label="MM/DD/YYYY" value="MM/DD/YYYY" />
                  <el-option label="DD/MM/YYYY" value="DD/MM/YYYY" />
                </el-select>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- API设置 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>API设置</h3>
            </template>

            <el-form :model="systemData.api" label-position="top" size="large">
              <el-form-item>
                <template #label>
                  <div class="label-with-action">
                    <span>API密钥</span>
                    <el-button type="primary" link size="small" @click="regenerateApiKey">
                      重新生成
                    </el-button>
                  </div>
                </template>
                <el-input v-model="systemData.api.key" type="password" readonly show-password>
                  <template #append>
                    <el-button @click="copyApiKey">
                      <el-icon><CopyDocument /></el-icon>
                    </el-button>
                  </template>
                </el-input>
              </el-form-item>

              <el-form-item label="调用频率限制">
                <el-select v-model="systemData.api.rateLimit" style="width: 100%">
                  <el-option label="1000次/小时" value="1000次/小时" />
                  <el-option label="5000次/小时" value="5000次/小时" />
                  <el-option label="10000次/小时" value="10000次/小时" />
                  <el-option label="无限制" value="无限制" />
                </el-select>
              </el-form-item>

              <el-form-item>
                <div class="api-option">
                  <div class="option-info">
                    <h4>API访问日志</h4>
                    <p>记录所有API调用</p>
                  </div>
                  <el-switch v-model="systemData.api.logging" />
                </div>
              </el-form-item>
            </el-form>
          </el-card>
        </div>
      </el-col>

      <el-col :lg="12" :xs="24">
        <div class="side-content">
          <!-- 数据管理 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>数据管理</h3>
            </template>

            <div class="data-management">
              <div class="data-item">
                <div class="data-header">
                  <h4>数据备份</h4>
                  <el-tag type="success" size="small">已启用</el-tag>
                </div>
                <p>自动备份企业数据</p>
                <div class="data-actions">
                  <el-button type="default" size="small">立即备份</el-button>
                  <el-button type="primary" size="small">下载备份</el-button>
                </div>
              </div>

              <div class="data-item">
                <div class="data-header">
                  <h4>数据导出</h4>
                </div>
                <p>导出企业所有数据</p>
                <div class="data-actions">
                  <el-button type="default" size="small" @click="exportData">
                    <el-icon><Download /></el-icon>
                    导出全部数据
                  </el-button>
                </div>
              </div>

              <div class="data-item danger">
                <div class="data-header">
                  <h4>危险操作</h4>
                </div>
                <p>删除企业账户将无法恢复</p>
                <div class="data-actions">
                  <el-button type="danger" size="small" plain @click="confirmDeleteAccount">
                    <el-icon><Delete /></el-icon>
                    删除企业账户
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 第三方集成 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>第三方集成</h3>
            </template>

            <div class="integration-list">
              <div
                v-for="integration in systemData.integrations"
                :key="integration.name"
                class="integration-item"
              >
                <div class="integration-info">
                  <div class="integration-icon">
                    <el-icon>
                      <component :is="getIntegrationIcon(integration.icon)" />
                    </el-icon>
                  </div>
                  <div class="integration-details">
                    <h4>{{ integration.name }}</h4>
                    <p>{{ integration.description }}</p>
                  </div>
                </div>

                <div class="integration-action">
                  <el-tag v-if="integration.connected" type="success" size="small"> 已连接 </el-tag>
                  <el-button
                    v-else
                    type="default"
                    size="small"
                    @click="connectIntegration(integration.name)"
                  >
                    连接
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 系统状态 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>系统状态</h3>
            </template>

            <div class="system-status">
              <div class="status-item">
                <div class="status-label">系统版本</div>
                <div class="status-value">v2.1.3</div>
              </div>

              <div class="status-item">
                <div class="status-label">最后更新</div>
                <div class="status-value">2025-07-15</div>
              </div>

              <div class="status-item">
                <div class="status-label">系统状态</div>
                <div class="status-value">
                  <el-tag type="success" size="small">正常运行</el-tag>
                </div>
              </div>

              <div class="status-item">
                <div class="status-label">数据库</div>
                <div class="status-value">
                  <el-tag type="success" size="small">连接正常</el-tag>
                </div>
              </div>
            </div>

            <el-button type="primary" class="check-updates-btn">
              <el-icon><Refresh /></el-icon>
              检查更新
            </el-button>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- API密钥重新生成确认对话框 -->
    <el-dialog v-model="showRegenerateDialog" title="重新生成API密钥" width="400px">
      <div class="regenerate-warning">
        <el-icon class="warning-icon"><WarningFilled /></el-icon>
        <p>重新生成API密钥后，所有使用旧密钥的应用将无法正常工作。确定要继续吗？</p>
      </div>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showRegenerateDialog = false">取消</el-button>
          <el-button type="danger" @click="confirmRegenerateApiKey"> 确定重新生成 </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  CopyDocument,
  Download,
  Delete,
  Refresh,
  WarningFilled,
  ChatDotRound,
  Message,
  Setting
} from '@element-plus/icons-vue'
import { useEnterpriseStore } from '@/stores'

const settingsStore = useEnterpriseStore()

const systemData = computed({
  get: () => settingsStore.systemConfig,
  set: (value) => settingsStore.updateSystemConfig(value)
})

const showRegenerateDialog = ref(false)

// 获取集成服务图标
const getIntegrationIcon = (iconName) => {
  const iconMap = {
    slack: ChatDotRound,
    wechat: Message,
    dingtalk: Setting
  }
  return iconMap[iconName] || Setting
}

// 复制API密钥
const copyApiKey = async () => {
  try {
    await navigator.clipboard.writeText(systemData.value.api.key)
    ElMessage.success('API密钥已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

// 重新生成API密钥
const regenerateApiKey = () => {
  showRegenerateDialog.value = true
}

const confirmRegenerateApiKey = () => {
  // 生成新的API密钥
  const newKey =
    'sk-' +
    Math.random().toString(36).substring(2, 15) +
    Math.random().toString(36).substring(2, 15)
  systemData.value.api.key = newKey

  showRegenerateDialog.value = false
  ElMessage.success('API密钥已重新生成')
}

// 数据导出
const exportData = () => {
  ElMessage.info('正在准备导出数据，请稍候...')

  // 模拟导出过程
  setTimeout(() => {
    ElMessage.success('数据导出完成')
  }, 2000)
}

// 删除企业账户确认
const confirmDeleteAccount = () => {
  ElMessageBox.prompt('请输入 "DELETE" 来确认删除企业账户', '危险操作确认', {
    confirmButtonText: '确定删除',
    cancelButtonText: '取消',
    confirmButtonClass: 'el-button--danger',
    inputPattern: /^DELETE$/,
    inputErrorMessage: '请正确输入 DELETE'
  })
    .then(() => {
      ElMessage.error('账户删除功能暂未开放')
    })
    .catch(() => {
      // 用户取消
    })
}

// 连接第三方服务
const connectIntegration = (serviceName) => {
  ElMessage.loading('正在连接...')

  // 模拟连接过程
  setTimeout(() => {
    settingsStore.toggleIntegration(serviceName)
    ElMessage.success(`${serviceName} 连接成功`)
  }, 1500)
}

// 检查系统更新
const checkUpdates = () => {
  ElMessage.loading('正在检查更新...')

  setTimeout(() => {
    ElMessage.info('当前已是最新版本')
  }, 2000)
}
</script>

<style lang="scss" scoped>
.system-config {
  .main-content,
  .side-content {
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

  .label-with-action {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
  }

  .api-option {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 16px;
    border: 1px solid #e4e7ed;
    border-radius: 8px;

    .option-info {
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

  .data-management {
    .data-item {
      padding: 16px;
      border: 1px solid #e4e7ed;
      border-radius: 8px;
      margin-bottom: 16px;

      &:last-child {
        margin-bottom: 0;
      }

      &.danger {
        border-color: #fde2e2;
        background: #fef2f2;

        h4 {
          color: #dc2626;
        }

        p {
          color: #991b1b;
        }
      }

      .data-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;

        h4 {
          margin: 0;
          font-size: 14px;
          font-weight: 500;
          color: #303133;
        }
      }

      p {
        margin: 0 0 12px 0;
        font-size: 12px;
        color: #909399;
      }

      .data-actions {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
    }
  }

  .integration-list {
    .integration-item {
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

      .integration-info {
        display: flex;
        align-items: center;
        gap: 12px;

        .integration-icon {
          width: 40px;
          height: 40px;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: #fff;

          .el-icon {
            font-size: 20px;
          }
        }

        .integration-details {
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
  }

  .system-status {
    .status-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .status-label {
        font-size: 14px;
        color: #606266;
      }

      .status-value {
        font-size: 14px;
        font-weight: 500;
        color: #303133;
      }
    }
  }

  .check-updates-btn {
    width: 100%;
    margin-top: 16px;
  }

  .regenerate-warning {
    display: flex;
    align-items: flex-start;
    gap: 12px;

    .warning-icon {
      color: #f56c6c;
      font-size: 20px;
      margin-top: 2px;
      flex-shrink: 0;
    }

    p {
      margin: 0;
      color: #606266;
      line-height: 1.5;
    }
  }
}

@media (max-width: 992px) {
  .system-config {
    .side-content {
      margin-top: 20px;
    }
  }
}

@media (max-width: 768px) {
  .system-config {
    .integration-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;

      .integration-action {
        align-self: stretch;
      }
    }

    .data-actions {
      flex-direction: column;

      .el-button {
        width: 100%;
      }
    }

    .label-with-action {
      flex-direction: column;
      align-items: flex-start;
      gap: 8px;
    }
  }
}
</style>
