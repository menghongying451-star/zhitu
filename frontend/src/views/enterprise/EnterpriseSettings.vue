<!-- views/settings/EnterpriseSettings.vue -->
<script setup>
import { ref, onMounted, computed } from 'vue'
import { OfficeBuilding, UserFilled, Lock, Bell, Setting, Clock } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores'
import { userService } from '@/api'
// import CompanyInfo from '@/components/src/components/EnterpriseSettings/CompanyInfo.vue'
// import { defineAsyncComponent } from 'vue'

// 除了默认显示的CompanyInfo，异步引入各个设置组件，优化加载速度
// const TeamManagement = defineAsyncComponent(
//   () => import('@/components/src/components/EnterpriseSettings/TeamManagement.vue')
// )
// const PermissionSettings = defineAsyncComponent(
//   () => import('@/components/src/components/EnterpriseSettings/PermissionSettings.vue')
// )
// const EnterpriseNotification = defineAsyncComponent(
//   () => import('@/components/src/components/EnterpriseSettings/EnterpriseNotification.vue')
// )
// const SystemConfig = defineAsyncComponent(() => import('@/components/src/components/EnterpriseSettings/SystemConfig.vue'))
// const AccountSecurity = defineAsyncComponent(
//   () => import('@/components/src/components/EnterpriseSettings/AccountSecurity.vue')
// )

const activeTab = ref('company')

const userStore = useUserStore()

// 计算属性：判断是否为审核中状态
const isPending = computed(() => {
  return userStore.user?.company_profile?.status === 'pending'
})

onMounted(async () => {
  let res = await userService.getCurrentUser()
  userStore.setUser({ ...res.data })
})
</script>

<template>
  <div class="enterprise-settings">
    <el-card class="settings-header" shadow="never">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">企业设置</h1>
          <p class="page-description" v-if="!isPending">管理企业信息、团队权限和系统配置</p>
          <p class="page-description" v-else>您的加入申请正在审核中</p>
        </div>
      </div>
    </el-card>

    <!-- 审核中状态显示 -->
    <el-card v-if="isPending" shadow="never" class="pending-status">
      <div class="pending-content">
        <el-icon class="pending-icon" size="64">
          <Clock />
        </el-icon>
        <h2 class="pending-title">申请审核中</h2>
        <p class="pending-description">您的加入申请正在审核中，请耐心等待</p>
        <div class="pending-tips">
          <p>• 审核通常在 1-3 个工作日内完成</p>
          <p>• 审核完成后您将收到通知</p>
          <p>• 如有疑问请联系企业管理员</p>
        </div>
      </div>
    </el-card>

    <!-- 正常企业设置内容 -->
    <el-card v-else shadow="never" class="settings-content">
      <el-tabs v-model="activeTab" type="border-card" class="settings-tabs">
        <el-tab-pane label="企业信息" name="company">
          <template #label>
            <span class="tab-label">
              <el-icon><OfficeBuilding /></el-icon>
              企业信息
            </span>
          </template>
          <CompanyInfo />
        </el-tab-pane>

        <el-tab-pane label="团队管理" name="team">
          <template #label>
            <span class="tab-label">
              <el-icon><UserFilled /></el-icon>
              团队管理
            </span>
          </template>
          <TeamManagement />
        </el-tab-pane>

        <!-- <el-tab-pane label="权限设置" name="permissions">
          <template #label>
            <span class="tab-label">
              <el-icon><Lock /></el-icon>
              权限设置
            </span>
          </template>
          <PermissionSettings />
        </el-tab-pane> -->

        <!-- <el-tab-pane label="通知设置" name="notifications">
          <template #label>
            <span class="tab-label">
              <el-icon><Bell /></el-icon>
              通知设置
            </span>
          </template>
          <EnterpriseNotification />
        </el-tab-pane> -->

        <!-- <el-tab-pane label="系统配置" name="system">
          <template #label>
            <span class="tab-label">
              <el-icon><Setting /></el-icon>
              系统配置
            </span>
          </template>
          <SystemConfig />
        </el-tab-pane> -->
      </el-tabs>
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.enterprise-settings {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;

  .settings-header {
    margin-bottom: 20px;
    border: none;

    .header-content {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      flex-wrap: wrap;
      gap: 20px;

      .header-info {
        .page-title {
          font-size: clamp(1.5rem, 3vw, 2rem);
          font-weight: bold;
          margin: 0 0 8px 0;
          color: #303133;
        }

        .page-description {
          color: #909399;
          margin: 0;
          font-size: 14px;
        }
      }
    }
  }

  .pending-status {
    border: none;

    .pending-content {
      text-align: center;
      padding: 40px 20px;

      .pending-icon {
        color: #e6a23c;
        margin-bottom: 20px;
      }

      .pending-title {
        font-size: 24px;
        font-weight: bold;
        color: #303133;
        margin: 0 0 12px 0;
      }

      .pending-description {
        font-size: 16px;
        color: #606266;
        margin: 0 0 30px 0;
      }

      .pending-tips {
        background: #fdf6ec;
        border: 1px solid #f5dab1;
        border-radius: 4px;
        padding: 20px;
        text-align: left;
        max-width: 400px;
        margin: 0 auto;

        p {
          margin: 8px 0;
          color: #e6a23c;
          font-size: 14px;
        }
      }
    }
  }

  .settings-content {
    border: none;

    .settings-tabs {
      border: none;

      :deep(.el-tabs__header) {
        margin-bottom: 20px;
      }

      :deep(.el-tabs__nav-wrap) {
        background: #fff;
      }

      .tab-label {
        display: flex;
        align-items: center;
        gap: 8px;
      }
    }
  }
}

@media (max-width: 768px) {
  .enterprise-settings {
    padding: 16px;

    .settings-header .header-content {
      flex-direction: column;
      align-items: stretch;
    }

    .pending-status .pending-content {
      padding: 30px 15px;

      .pending-tips {
        margin: 0;
      }
    }
  }

  :deep(.el-tabs__content) {
    padding: 0;
  }
}
</style>
