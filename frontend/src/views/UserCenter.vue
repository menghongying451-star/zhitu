<script setup>
import { ref } from 'vue'
import { UserFilled, Bell, Key } from '@element-plus/icons-vue'

const activeTab = ref('profile')
</script>

<template>
  <div class="user-center">
    <el-card class="user-center-header" shadow="never">
      <div class="header-content">
        <div class="header-info">
          <h1 class="page-title">个人中心</h1>
          <p class="page-description">管理您的个人信息、账户安全和通知设置</p>
        </div>
      </div>
    </el-card>

    <el-card class="user-center-content" shadow="never">
      <el-tabs v-model="activeTab" type="border-card" class="profile-tabs">
        <el-tab-pane label="账户安全" name="profile">
          <template #label>
            <span class="tab-label">
              <el-icon><UserFilled /></el-icon>
              个人资料
            </span>
          </template>
          <UserProfile />
        </el-tab-pane>

        <el-tab-pane label="账户设置" name="settings">
          <template #label>
            <span class="tab-label">
              <el-icon><Key /></el-icon>
              账户安全
            </span>
          </template>
          <AccountSecurity />
        </el-tab-pane>

        <el-tab-pane label="通知设置" name="notifications">
          <template #label>
            <span class="tab-label">
              <el-icon><Bell /></el-icon>
              通知设置
            </span>
          </template>
          <NotificationSettings />
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<style lang="scss" scoped>
.user-center {
  padding: 20px;
  background-color: #f5f7fa;
  min-height: 100vh;

  .user-center-header {
    margin-bottom: 20px;
    border: none;

    .header-content {
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

  .user-center-content {
    border: none;

    .profile-tabs {
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
  .user-center {
    padding: 16px;
  }
}
</style>
