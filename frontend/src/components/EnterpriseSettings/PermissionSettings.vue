<!-- components/settings/PermissionSettings.vue -->
<template>
  <div class="permission-settings">
    <el-row :gutter="20">
      <el-col :lg="12" :xs="24">
        <div class="main-content">
          <!-- 角色管理 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <div class="card-header">
                <h3>角色管理</h3>
                <el-button type="primary" @click="showRoleDialog = true">
                  <el-icon><Plus /></el-icon>
                  新建角色
                </el-button>
              </div>
            </template>

            <div class="role-list">
              <div v-for="role in permissionData.roles" :key="role.name" class="role-item">
                <div class="role-info">
                  <h4>{{ role.name }}</h4>
                  <p>{{ role.description }}</p>
                </div>
                <div class="role-actions">
                  <span class="role-count">{{ role.count }}人</span>
                  <el-button
                    v-if="role.name !== '超级管理员'"
                    type="primary"
                    link
                    @click="editRole(role)"
                  >
                    <el-icon><Edit /></el-icon>
                  </el-button>
                  <el-button v-else disabled link>
                    <el-icon><Edit /></el-icon>
                  </el-button>
                </div>
              </div>
            </div>
          </el-card>

          <!-- 访问控制 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>访问控制</h3>
            </template>

            <div class="access-control-list">
              <div class="control-item">
                <div class="control-info">
                  <h4>IP白名单</h4>
                  <p>限制特定IP地址访问</p>
                </div>
                <el-switch
                  v-model="permissionData.accessControl.ipWhitelist"
                  @change="handleAccessControlChange"
                />
              </div>

              <div class="control-item">
                <div class="control-info">
                  <h4>强制HTTPS</h4>
                  <p>仅允许安全连接</p>
                </div>
                <el-switch
                  v-model="permissionData.accessControl.forceHttps"
                  @change="handleAccessControlChange"
                />
              </div>

              <div class="control-item">
                <div class="control-info">
                  <h4>会话超时</h4>
                  <p>自动登出闲置用户</p>
                </div>
                <el-select
                  v-model="permissionData.accessControl.sessionTimeout"
                  style="width: 120px"
                  @change="handleAccessControlChange"
                >
                  <el-option label="30分钟" value="30分钟" />
                  <el-option label="1小时" value="1小时" />
                  <el-option label="2小时" value="2小时" />
                  <el-option label="8小时" value="8小时" />
                </el-select>
              </div>
            </div>
          </el-card>
        </div>
      </el-col>

      <el-col :lg="12" :xs="24">
        <div class="side-content">
          <!-- 权限矩阵 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>权限矩阵</h3>
            </template>

            <div class="permission-matrix">
              <el-table :data="permissionMatrix" size="small" border>
                <el-table-column prop="module" label="功能模块" width="100" />
                <el-table-column label="普通" width="60" align="center">
                  <template #default="{ row }">
                    <el-icon :class="row.normal ? 'permission-granted' : 'permission-denied'">
                      <component :is="row.normal ? CircleCheck : CircleClose" />
                    </el-icon>
                  </template>
                </el-table-column>
                <el-table-column label="管理" width="60" align="center">
                  <template #default="{ row }">
                    <el-icon :class="row.admin ? 'permission-granted' : 'permission-denied'">
                      <component :is="row.admin ? CircleCheck : CircleClose" />
                    </el-icon>
                  </template>
                </el-table-column>
                <el-table-column label="超管" width="60" align="center">
                  <template #default="{ row }">
                    <el-icon :class="row.superAdmin ? 'permission-granted' : 'permission-denied'">
                      <component :is="row.superAdmin ? CircleCheck : CircleClose" />
                    </el-icon>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-card>

          <!-- 审计日志 -->
          <el-card class="setting-card" shadow="never">
            <template #header>
              <h3>审计日志</h3>
            </template>

            <div class="audit-logs">
              <div v-for="log in auditLogs" :key="log.id" class="log-item">
                <div class="log-content">
                  <div class="log-title">{{ log.title }}</div>
                  <div class="log-time">{{ log.time }}</div>
                </div>
                <el-tag :type="getLogTagType(log.type)" size="small">
                  {{ log.type }}
                </el-tag>
              </div>
            </div>

            <el-button type="default" class="view-all-btn"> 查看完整日志 </el-button>
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 新建/编辑角色对话框 -->
    <el-dialog v-model="showRoleDialog" :title="isEditMode ? '编辑角色' : '新建角色'" width="600px">
      <el-form
        ref="roleFormRef"
        :model="roleForm"
        :rules="roleRules"
        label-width="100px"
        size="large"
      >
        <el-form-item label="角色名称" prop="name">
          <el-input v-model="roleForm.name" placeholder="请输入角色名称" :disabled="isEditMode" />
        </el-form-item>

        <el-form-item label="角色描述" prop="description">
          <el-input
            v-model="roleForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入角色描述"
          />
        </el-form-item>

        <el-form-item label="权限设置">
          <div class="permission-checkboxes">
            <el-checkbox-group v-model="roleForm.permissions">
              <div class="permission-group">
                <h4>项目管理</h4>
                <el-checkbox label="project_view">项目查看</el-checkbox>
                <el-checkbox label="project_create">项目创建</el-checkbox>
                <el-checkbox label="project_edit">项目编辑</el-checkbox>
                <el-checkbox label="project_delete">项目删除</el-checkbox>
              </div>

              <div class="permission-group">
                <h4>人才管理</h4>
                <el-checkbox label="talent_view">人才查看</el-checkbox>
                <el-checkbox label="talent_manage">人才管理</el-checkbox>
                <el-checkbox label="talent_invite">人才邀请</el-checkbox>
              </div>

              <div class="permission-group">
                <h4>需求管理</h4>
                <el-checkbox label="requirement_view">需求查看</el-checkbox>
                <el-checkbox label="requirement_publish">需求发布</el-checkbox>
                <el-checkbox label="requirement_manage">需求管理</el-checkbox>
              </div>

              <div class="permission-group">
                <h4>系统设置</h4>
                <el-checkbox label="system_config">系统配置</el-checkbox>
                <el-checkbox label="user_manage">用户管理</el-checkbox>
                <el-checkbox label="role_manage">角色管理</el-checkbox>
              </div>
            </el-checkbox-group>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleRoleDialogClose">取消</el-button>
          <el-button type="primary" @click="handleRoleSubmit">
            {{ isEditMode ? '保存' : '创建' }}
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, CircleCheck, CircleClose } from '@element-plus/icons-vue'
import { useEnterpriseStore } from '@/stores'

const settingsStore = useEnterpriseStore()

const permissionData = computed(() => settingsStore.permissions)

const showRoleDialog = ref(false)
const isEditMode = ref(false)
const roleFormRef = ref()

const roleForm = ref({
  name: '',
  description: '',
  permissions: []
})

const roleRules = {
  name: [
    { required: true, message: '请输入角色名称', trigger: 'blur' },
    { min: 2, max: 20, message: '角色名称长度应在 2 到 20 个字符', trigger: 'blur' }
  ],
  description: [{ required: true, message: '请输入角色描述', trigger: 'blur' }]
}

// 权限矩阵数据
const permissionMatrix = ref([
  { module: '项目查看', normal: true, admin: true, superAdmin: true },
  { module: '项目创建', normal: false, admin: true, superAdmin: true },
  { module: '人才管理', normal: false, admin: true, superAdmin: true },
  { module: '需求发布', normal: false, admin: true, superAdmin: true },
  { module: '系统设置', normal: false, admin: false, superAdmin: true }
])

// 审计日志数据
const auditLogs = ref([
  {
    id: 1,
    title: '张经理 修改了企业信息',
    time: '2025-08-02 10:30',
    type: '修改'
  },
  {
    id: 2,
    title: '李华 邀请了新成员',
    time: '2025-08-01 16:45',
    type: '邀请'
  },
  {
    id: 3,
    title: '王强 创建了新项目',
    time: '2025-07-30 14:20',
    type: '创建'
  }
])

const getLogTagType = (type) => {
  const typeMap = {
    修改: 'primary',
    邀请: 'success',
    创建: 'warning',
    删除: 'danger'
  }
  return typeMap[type] || 'info'
}

const editRole = (role) => {
  isEditMode.value = true
  roleForm.value = {
    name: role.name,
    description: role.description,
    permissions: ['project_view', 'project_create'] // 示例权限
  }
  showRoleDialog.value = true
}

const handleRoleDialogClose = () => {
  showRoleDialog.value = false
  isEditMode.value = false
  roleForm.value = {
    name: '',
    description: '',
    permissions: []
  }
  roleFormRef.value?.clearValidate()
}

const handleRoleSubmit = async () => {
  try {
    await roleFormRef.value.validate()

    if (isEditMode.value) {
      ElMessage.success('角色更新成功')
    } else {
      // 添加新角色到store
      settingsStore.permissions.roles.push({
        name: roleForm.value.name,
        description: roleForm.value.description,
        count: 0
      })
      ElMessage.success('角色创建成功')
    }

    handleRoleDialogClose()
  } catch (error) {
    console.log('表单验证失败:', error)
  }
}

const handleAccessControlChange = () => {
  ElMessage.success('访问控制设置已更新')
}
</script>

<style lang="scss" scoped>
.permission-settings {
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

      .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
    }
  }

  .role-list {
    .role-item {
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

      .role-info {
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

      .role-actions {
        display: flex;
        align-items: center;
        gap: 12px;

        .role-count {
          font-size: 12px;
          color: #909399;
        }
      }
    }
  }

  .access-control-list {
    .control-item {
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

      .control-info {
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

  .permission-matrix {
    :deep(.el-table) {
      font-size: 12px;

      .permission-granted {
        color: #67c23a;
      }

      .permission-denied {
        color: #f56c6c;
      }
    }
  }

  .audit-logs {
    .log-item {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 12px;
      background: #fafafa;
      border-radius: 8px;
      margin-bottom: 8px;

      &:last-child {
        margin-bottom: 0;
      }

      .log-content {
        .log-title {
          font-size: 14px;
          font-weight: 500;
          color: #303133;
          margin-bottom: 4px;
        }

        .log-time {
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

  .permission-checkboxes {
    .permission-group {
      margin-bottom: 20px;

      h4 {
        margin: 0 0 12px 0;
        font-size: 14px;
        font-weight: 600;
        color: #303133;
        border-bottom: 1px solid #e4e7ed;
        padding-bottom: 8px;
      }

      .el-checkbox {
        display: block;
        margin: 8px 0;
      }
    }
  }
}

@media (max-width: 992px) {
  .permission-settings {
    .side-content {
      margin-top: 20px;
    }
  }
}

@media (max-width: 768px) {
  .permission-settings {
    .setting-card {
      .card-header {
        flex-direction: column;
        gap: 12px;
        align-items: stretch;
      }
    }

    .role-item,
    .control-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 12px;
    }

    .permission-matrix {
      overflow-x: auto;
    }
  }
}
</style>
