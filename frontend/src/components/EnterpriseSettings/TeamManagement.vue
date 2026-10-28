<!-- components/settings/TeamManagement.vue -->
<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import {
  UserFilled,
  Search,
  EditPen,
  Check,
  Close,
  RefreshRight,
  User
} from '@element-plus/icons-vue'
import { useEnterpriseStore } from '@/stores'
import { useUserStore } from '@/stores' // 添加用户store
import { enterpriseInfoService } from '@/api'

const enterpriseStore = useEnterpriseStore()
const userStore = useUserStore() // 使用用户store

// 当前用户权限（从store获取）
const currentUserRole = computed(() => enterpriseStore.teamManagement.userRole)
const isAdminOrOwner = computed(() => ['admin', 'owner'].includes(currentUserRole.value))

// 当前用户信息
const currentUser = computed(() => userStore.user)

// 当前用户在组织中的信息
const currentUserOrgInfo = computed(() => {
  if (currentUser.value.user_type === 'organization' && currentUser.value.company_profile) {
    return {
      position: currentUser.value.company_profile.position || '-',
      department: currentUser.value.company_profile.department || '-',
      status: currentUser.value.company_profile.status_display || '-',
      permission: currentUser.value.company_profile.permission_display || '-',
      joinedAt: currentUser.value.date_joined || '-',
      organization: currentUser.value.company_profile.organization?.name || '-'
    }
  }
  return {
    position: '-',
    department: '-',
    status: '-',
    permission: '-',
    joinedAt: '-',
    organization: '-'
  }
})

// 团队统计数据
const teamStats = ref({
  totalMembers: 0,
  pendingMembers: 0,
  admins: 0
})

// 成员列表数据
const memberList = ref({
  data: [],
  loading: false,
  pagination: {
    current_page: 1,
    total_pages: 1,
    total_count: 0,
    page_size: 10
  }
})

// 搜索和过滤条件
const searchFilters = ref({
  search: '',
  status: '',
  permission: '',
  page: 1,
  page_size: 10
})

// 申请审核列表
const pendingList = ref({
  data: [],
  loading: false,
  pagination: {
    current_page: 1,
    total_pages: 1,
    total_count: 0,
    page_size: 5
  }
})

// 操作日志列表
const operationLogs = ref({
  data: [],
  loading: false,
  pagination: {
    current_page: 1,
    total_pages: 1,
    total_count: 0,
    page_size: 10
  }
})

// 编辑成员对话框
const editMemberDialog = ref({
  visible: false,
  loading: false,
  form: {
    id: '',
    permission: '',
    status: '',
    position: '',
    department: ''
  }
})

// 批量操作
const batchOperation = ref({
  selectedMembers: [],
  action: '',
  loading: false
})

// 当前活跃的标签页
const activeTab = ref('members')

// 权限显示映射
const permissionDisplayMap = {
  owner: '创建者',
  admin: '管理员',
  member: '成员',
  pending: '待分配'
}

// 状态显示映射
const statusDisplayMap = {
  pending: '待审核',
  approved: '已通过',
  rejected: '已拒绝'
}

// 获取权限显示文字
const getPermissionDisplay = (permission) => {
  return permissionDisplayMap[permission] || permission
}

// 获取状态显示文字
const getStatusDisplay = (status) => {
  return statusDisplayMap[status] || status
}

// 获取团队成员列表
const fetchMembers = async (filters = {}) => {
  memberList.value.loading = true
  try {
    const response = await enterpriseInfoService.getOrganizationMembers({
      ...searchFilters.value,
      ...filters,
      // 不在此处处理permission数组，保持原有逻辑
      permission: searchFilters.value.permission
    })

    // 处理返回的数据，添加显示字段
    const processedMembers = response.data.members.map((member) => ({
      ...member,
      permission_display: getPermissionDisplay(member.permission),
      status_display: getStatusDisplay(member.status)
    }))

    memberList.value.data = processedMembers
    memberList.value.pagination = response.data.pagination

    // 更新store中的成员数据
    enterpriseStore.setTeamMembers(processedMembers)

    // 更新统计数据
    await updateTeamStats()
  } catch (error) {
    console.error('获取团队成员失败:', error)
    ElMessage.error('获取团队成员失败')
  } finally {
    memberList.value.loading = false
  }
}

// 获取待审核成员
const fetchPendingMembers = async () => {
  if (!isAdminOrOwner.value) return

  pendingList.value.loading = true
  try {
    const response = await enterpriseInfoService.getOrganizationMembers({
      status: 'pending',
      page: pendingList.value.pagination.current_page,
      page_size: pendingList.value.pagination.page_size
    })

    // 处理返回的数据，添加显示字段
    const processedMembers = response.data.members.map((member) => ({
      ...member,
      permission_display: getPermissionDisplay(member.permission),
      status_display: getStatusDisplay(member.status)
    }))

    pendingList.value.data = processedMembers
    pendingList.value.pagination = response.data.pagination
  } catch (error) {
    console.error('获取待审核成员失败:', error)
    ElMessage.error('获取待审核成员失败')
  } finally {
    pendingList.value.loading = false
  }
}

// 获取操作日志
const fetchOperationLogs = async () => {
  operationLogs.value.loading = true
  try {
    const response = await enterpriseInfoService.getOrganizationLogs({
      page: operationLogs.value.pagination.current_page,
      page_size: operationLogs.value.pagination.page_size
    })
    operationLogs.value.data = response.data.logs
    operationLogs.value.pagination = response.data.pagination
  } catch (error) {
    console.error('获取操作日志失败:', error)
    ElMessage.error('获取操作日志失败')
  } finally {
    operationLogs.value.loading = false
  }
}

// 更新统计数据
const updateTeamStats = async () => {
  try {
    // 获取总成员数
    const totalResponse = await enterpriseInfoService.getOrganizationMembers({
      page: 1,
      page_size: 1
    })

    // 获取待审核成员数
    const pendingResponse = await enterpriseInfoService.getOrganizationMembers({
      status: 'pending',
      page: 1,
      page_size: 1
    })

    // 分别获取管理员和拥有者数量
    const adminResponse = await enterpriseInfoService.getOrganizationMembers({
      permission: 'admin',
      page: 1,
      page_size: 1
    })

    const ownerResponse = await enterpriseInfoService.getOrganizationMembers({
      permission: 'owner',
      page: 1,
      page_size: 1
    })

    const stats = {
      totalMembers: totalResponse.data.pagination.total_count || 0,
      pendingMembers: pendingResponse.data.pagination.total_count || 0,
      admins:
        (adminResponse.data.pagination.total_count || 0) +
        (ownerResponse.data.pagination.total_count || 0)
    }

    teamStats.value = stats

    // 同步更新store中的统计数据
    enterpriseStore.updateTeamStats(stats)
  } catch (error) {
    console.error('获取团队统计数据失败:', error)
    ElMessage.error('获取团队统计数据失败')
  }
}

// 搜索功能
const handleSearch = () => {
  searchFilters.value.page = 1
  fetchMembers()
}

// 重置搜索
const resetSearch = () => {
  searchFilters.value = {
    search: '',
    status: '',
    permission: '',
    page: 1,
    page_size: 10
  }
  fetchMembers()
}

// 分页变化
const handlePageChange = (page) => {
  searchFilters.value.page = page
  fetchMembers()
}

const handleSizeChange = (size) => {
  searchFilters.value.page_size = size
  searchFilters.value.page = 1
  fetchMembers()
}

// 编辑成员
const openEditMember = (member) => {
  editMemberDialog.value.form = {
    id: member.id,
    permission: member.permission,
    status: member.status,
    position: member.position || '',
    department: member.department || ''
  }
  editMemberDialog.value.visible = true
}

// 保存成员信息
const saveMemberInfo = async () => {
  editMemberDialog.value.loading = true
  try {
    await enterpriseInfoService.updateOrganizationMember(
      editMemberDialog.value.form.id,
      editMemberDialog.value.form
    )
    ElMessage.success('成员信息更新成功')
    editMemberDialog.value.visible = false

    // 更新本地数据
    const updatedData = {
      ...editMemberDialog.value.form,
      permission_display: getPermissionDisplay(editMemberDialog.value.form.permission),
      status_display: getStatusDisplay(editMemberDialog.value.form.status)
    }

    // 更新store中的成员信息
    enterpriseStore.updateMemberInfo(editMemberDialog.value.form.id, updatedData)

    // 重新获取数据确保同步
    fetchMembers()
    if (isAdminOrOwner.value) {
      fetchPendingMembers()
    }
  } catch (error) {
    console.error('更新成员信息失败:', error)
    ElMessage.error('更新成员信息失败')
  } finally {
    editMemberDialog.value.loading = false
  }
}

// 审核成员
const approveMember = async (memberId, approve = true) => {
  try {
    const updateData = {
      status: approve ? 'approved' : 'rejected',
      permission: approve ? 'member' : 'pending'
    }

    await enterpriseInfoService.updateOrganizationMember(memberId, updateData)
    ElMessage.success(approve ? '审核通过' : '审核拒绝')

    // 更新store中的成员信息
    const fullUpdateData = {
      ...updateData,
      permission_display: getPermissionDisplay(updateData.permission),
      status_display: getStatusDisplay(updateData.status)
    }
    enterpriseStore.updateMemberInfo(memberId, fullUpdateData)

    // 重新获取数据
    fetchPendingMembers()
    fetchMembers()
  } catch (error) {
    console.error('审核操作失败:', error)
    ElMessage.error('审核操作失败')
  }
}

// 批量操作
const handleBatchOperation = async () => {
  if (batchOperation.value.selectedMembers.length === 0) {
    ElMessage.warning('请选择要操作的成员')
    return
  }

  if (!batchOperation.value.action) {
    ElMessage.warning('请选择操作类型')
    return
  }

  batchOperation.value.loading = true
  try {
    const [status, permission] = batchOperation.value.action.split('-')
    const updateData = { status, permission }

    await enterpriseInfoService.batchUpdateMembers({
      member_ids: batchOperation.value.selectedMembers,
      ...updateData
    })

    ElMessage.success('批量操作成功')

    // 更新store中的批量成员信息
    const fullUpdateData = {
      ...updateData,
      permission_display: getPermissionDisplay(permission),
      status_display: getStatusDisplay(status)
    }
    enterpriseStore.batchUpdateMembers(batchOperation.value.selectedMembers, fullUpdateData)

    // 清空选择
    batchOperation.value.selectedMembers = []
    batchOperation.value.action = ''

    // 重新获取数据
    fetchMembers()
    if (isAdminOrOwner.value) {
      fetchPendingMembers()
    }
  } catch (error) {
    console.error('批量操作失败:', error)
    ElMessage.error('批量操作失败')
  } finally {
    batchOperation.value.loading = false
  }
}

// 获取权限标签类型
const getPermissionTagType = (permission) => {
  const typeMap = {
    owner: 'danger',
    admin: 'primary',
    member: 'success',
    pending: 'info'
  }
  return typeMap[permission] || ''
}

// 获取状态标签类型
const getStatusTagType = (status) => {
  const typeMap = {
    approved: 'success',
    pending: 'warning',
    rejected: 'danger'
  }
  return typeMap[status] || ''
}

// 格式化日期
const formatDate = (dateString) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 监听标签页变化
watch(activeTab, (newTab) => {
  if (newTab === 'pending' && isAdminOrOwner.value) {
    fetchPendingMembers()
  } else if (newTab === 'logs') {
    fetchOperationLogs()
  }
})

const isMobile = ref(false)
const handleResize = () => {
  isMobile.value = window.innerWidth <= 768 ? true : false
}

// 组件挂载时获取数据
onMounted(() => {
  window.addEventListener('resize', handleResize)
  fetchMembers()
  if (isAdminOrOwner.value) {
    fetchPendingMembers()
  }
})
</script>

<template>
  <div class="team-management">
    <!-- 团队概览 -->
    <div class="team-overview-container">
      <div class="team-stats-wrapper">
        <!-- 左侧统计数据 - 始终保持三列 -->
        <div class="stats-grid">
          <el-card class="stat-card" shadow="never">
            <div class="stat-content">
              <div class="stat-icon blue">
                <el-icon><UserFilled /></el-icon>
              </div>
              <div class="stat-number">{{ teamStats.totalMembers }}</div>
              <div class="stat-label">团队成员</div>
            </div>
          </el-card>

          <el-card class="stat-card" shadow="never">
            <div class="stat-content">
              <div class="stat-icon orange">
                <el-icon><RefreshRight /></el-icon>
              </div>
              <div class="stat-number">{{ teamStats.pendingMembers }}</div>
              <div class="stat-label">待审核</div>
            </div>
          </el-card>

          <el-card class="stat-card" shadow="never">
            <div class="stat-content">
              <div class="stat-icon purple">
                <el-icon><UserFilled /></el-icon>
              </div>
              <div class="stat-number">{{ teamStats.admins }}</div>
              <div class="stat-label">创建者/管理员</div>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 右侧用户信息 -->
      <div class="user-info-wrapper">
        <el-card class="user-info-card" shadow="never">
          <div class="user-info-content">
            <div class="user-avatar-section">
              <el-avatar :src="currentUser.avatar" :size="50">
                {{ currentUser.real_name?.charAt(0) || 'U' }}
              </el-avatar>
              <div class="user-basic-info">
                <div class="user-name">{{ currentUser.real_name || '未知用户' }}</div>
                <div class="user-username">@{{ currentUser.username }}</div>
              </div>
            </div>

            <div class="user-detail-info">
              <div class="info-grid">
                <div class="info-item">
                  <span class="info-label">组织</span>
                  <span class="info-value">{{ currentUserOrgInfo.organization }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">职位</span>
                  <span class="info-value">{{ currentUserOrgInfo.position }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">部门</span>
                  <span class="info-value">{{ currentUserOrgInfo.department }}</span>
                </div>
                <div class="info-item">
                  <span class="info-label">权限</span>
                  <el-tag
                    :type="getPermissionTagType(currentUser.company_profile?.permission)"
                    size="small"
                  >
                    {{ currentUserOrgInfo.permission }}
                  </el-tag>
                </div>
                <div class="info-item">
                  <span class="info-label">状态</span>
                  <el-tag
                    :type="getStatusTagType(currentUser.company_profile?.status)"
                    size="small"
                  >
                    {{ currentUserOrgInfo.status }}
                  </el-tag>
                </div>
                <div class="info-item">
                  <span class="info-label">加入时间</span>
                  <span class="info-value">{{ formatDate(currentUserOrgInfo.joinedAt) }}</span>
                </div>
              </div>
            </div>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 主要内容 -->
    <el-card class="main-card" shadow="never">
      <el-tabs v-model="activeTab">
        <!-- 团队成员列表 -->
        <el-tab-pane label="团队成员" name="members">
          <!-- 搜索和过滤 -->
          <div class="search-filters">
            <el-row :gutter="16">
              <el-col :lg="8" :md="12" :xs="24">
                <el-input
                  v-model="searchFilters.search"
                  placeholder="搜索用户名、姓名、邮箱、职位、部门"
                  clearable
                  @keyup.enter="handleSearch"
                >
                  <template #prefix>
                    <el-icon><Search /></el-icon>
                  </template>
                </el-input>
              </el-col>
              <el-col :lg="4" :md="6" :xs="12">
                <el-select v-model="searchFilters.status" placeholder="状态" clearable>
                  <el-option label="已通过" value="approved" />
                  <el-option label="待审核" value="pending" />
                  <el-option label="已拒绝" value="rejected" />
                </el-select>
              </el-col>
              <el-col :lg="4" :md="6" :xs="12">
                <el-select v-model="searchFilters.permission" placeholder="权限" clearable>
                  <el-option label="拥有者" value="owner" />
                  <el-option label="管理员" value="admin" />
                  <el-option label="成员" value="member" />
                  <el-option label="待分配" value="pending" />
                </el-select>
              </el-col>
              <el-col :lg="8" :md="24" :xs="24">
                <el-button type="primary" @click="handleSearch">
                  <el-icon><Search /></el-icon>
                  搜索
                </el-button>
                <el-button @click="resetSearch">重置</el-button>
              </el-col>
            </el-row>
          </div>

          <!-- 批量操作 -->
          <div v-if="isAdminOrOwner" class="batch-operations">
            <el-select
              v-model="batchOperation.action"
              placeholder="批量操作"
              class="batch-operations-select"
            >
              <el-option label="批准为成员" value="approved-member" />
              <el-option label="拒绝申请" value="rejected-pending" />
              <el-option label="设为管理员" value="approved-admin" />
              <el-option label="撤销管理员" value="approved-member" />
            </el-select>
            <el-button
              type="primary"
              :loading="batchOperation.loading"
              :disabled="batchOperation.selectedMembers.length === 0"
              @click="handleBatchOperation"
            >
              执行操作 ({{ batchOperation.selectedMembers.length }})
            </el-button>
          </div>

          <!-- 成员列表 -->
          <el-table
            :data="memberList.data"
            v-loading="memberList.loading"
            @selection-change="
              (val) => (batchOperation.selectedMembers = val.map((item) => item.id))
            "
          >
            <el-table-column v-if="isAdminOrOwner" type="selection" width="55" />

            <el-table-column label="成员信息" min-width="200">
              <template #default="{ row }">
                <div class="member-info">
                  <el-avatar :src="row.user?.avatar" :size="40">
                    {{ row.real_name?.charAt(0) || row.user?.real_name?.charAt(0) || 'U' }}
                  </el-avatar>
                  <div class="member-details">
                    <div class="member-name">
                      {{ row.real_name || row.user?.real_name || '未知用户' }}
                    </div>
                    <div class="member-username">
                      @{{ row.username || row.user?.username || '' }}
                    </div>
                    <div class="member-email">{{ row.email || row.user?.email || '' }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="部门/职位" min-width="150">
              <template #default="{ row }">
                <div>{{ row.department || '-' }}</div>
                <div class="text-secondary">{{ row.position || '-' }}</div>
              </template>
            </el-table-column>

            <el-table-column label="权限" width="100">
              <template #default="{ row }">
                <el-tag :type="getPermissionTagType(row.permission)" size="small">
                  {{ getPermissionDisplay(row.permission) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusTagType(row.status)" size="small">
                  {{ getStatusDisplay(row.status) }}
                </el-tag>
              </template>
            </el-table-column>

            <el-table-column label="加入时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>

            <el-table-column
              v-if="isAdminOrOwner"
              label="操作"
              :width="isMobile ? 70 : 120"
              fixed="right"
            >
              <template #default="{ row }">
                <el-button
                  type="primary"
                  link
                  size="small"
                  @click="openEditMember(row)"
                  :disabled="row.permission === 'owner'"
                >
                  <el-icon><EditPen /></el-icon>
                  编辑
                </el-button>
              </template>
            </el-table-column>
          </el-table>

          <!-- 分页 -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="searchFilters.page"
              v-model:page-size="searchFilters.page_size"
              :total="memberList.pagination.total_count"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="handlePageChange"
              @size-change="handleSizeChange"
            />
          </div>
        </el-tab-pane>

        <!-- 申请审核（仅管理员可见） -->
        <el-tab-pane v-if="isAdminOrOwner" label="申请审核" name="pending">
          <el-table :data="pendingList.data" v-loading="pendingList.loading">
            <el-table-column label="申请人" min-width="200">
              <template #default="{ row }">
                <div class="member-info">
                  <el-avatar :src="row.user?.avatar" :size="40">
                    {{ row.real_name?.charAt(0) || row.user?.real_name?.charAt(0) || 'U' }}
                  </el-avatar>
                  <div class="member-details">
                    <div class="member-name">
                      {{ row.real_name || row.user?.real_name || '未知用户' }}
                    </div>
                    <div class="member-username">
                      @{{ row.username || row.user?.username || '' }}
                    </div>
                    <div class="member-email">{{ row.email || row.user?.email || '' }}</div>
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="部门/职位" min-width="150">
              <template #default="{ row }">
                <div>{{ row.department || '-' }}</div>
                <div class="text-secondary">{{ row.position || '-' }}</div>
              </template>
            </el-table-column>

            <el-table-column label="申请时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>

            <el-table-column label="操作" :width="isMobile ? 80 : 160" fixed="right">
              <template #default="{ row }">
                <div class="mobile-actions">
                  <el-button type="success" size="small" @click="approveMember(row.id, true)">
                    <el-icon><Check /></el-icon>
                    通过
                  </el-button>
                  <el-button type="danger" size="small" @click="approveMember(row.id, false)">
                    <el-icon><Close /></el-icon>
                    拒绝
                  </el-button>
                </div>
              </template>
            </el-table-column>
          </el-table>

          <!-- 待审核分页 -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="pendingList.pagination.current_page"
              v-model:page-size="pendingList.pagination.page_size"
              :total="pendingList.pagination.total_count"
              :page-sizes="[5, 10, 20]"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="
                (page) => {
                  pendingList.pagination.current_page = page
                  fetchPendingMembers()
                }
              "
              @size-change="
                (size) => {
                  pendingList.pagination.page_size = size
                  pendingList.pagination.current_page = 1
                  fetchPendingMembers()
                }
              "
            />
          </div>
        </el-tab-pane>

        <!-- 操作日志 -->
        <el-tab-pane label="操作日志" name="logs">
          <el-table :data="operationLogs.data" v-loading="operationLogs.loading">
            <el-table-column label="操作者" width="150">
              <template #default="{ row }">
                <div>{{ row.operator?.real_name || '系统' }}</div>
                <div class="text-secondary">@{{ row.operator?.username || '' }}</div>
              </template>
            </el-table-column>

            <el-table-column label="操作类型" width="120">
              <template #default="{ row }">
                <el-tag size="small">{{ row.operation_display || row.operation }}</el-tag>
              </template>
            </el-table-column>

            <el-table-column label="目标用户" width="150">
              <template #default="{ row }">
                <div v-if="row.target_user">{{ row.target_user.real_name }}</div>
                <div v-if="row.target_user" class="text-secondary">
                  @{{ row.target_user.username }}
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作详情" min-width="200">
              <template #default="{ row }">
                <div v-if="row.details">
                  <div v-if="row.details.changes">
                    <div
                      v-for="(change, key) in row.details.changes"
                      :key="key"
                      class="change-item"
                    >
                      <span class="change-field">{{ key }}:</span>
                      <span class="change-value"> {{ change.old }} → {{ change.new }} </span>
                    </div>
                  </div>
                  <div v-else-if="row.details.new_status">
                    状态: {{ row.details.old_status }} → {{ row.details.new_status }}
                  </div>
                </div>
              </template>
            </el-table-column>

            <el-table-column label="操作时间" width="160">
              <template #default="{ row }">
                {{ formatDate(row.created_at) }}
              </template>
            </el-table-column>
          </el-table>

          <!-- 日志分页 -->
          <div class="pagination-wrapper">
            <el-pagination
              v-model:current-page="operationLogs.pagination.current_page"
              v-model:page-size="operationLogs.pagination.page_size"
              :total="operationLogs.pagination.total_count"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next, jumper"
              @current-change="
                (page) => {
                  operationLogs.pagination.current_page = page
                  fetchOperationLogs()
                }
              "
              @size-change="
                (size) => {
                  operationLogs.pagination.page_size = size
                  operationLogs.pagination.current_page = 1
                  fetchOperationLogs()
                }
              "
            />
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 编辑成员对话框 -->
    <el-dialog v-model="editMemberDialog.visible" title="编辑成员信息" width="500px">
      <el-form :model="editMemberDialog.form" label-width="80px">
        <el-form-item label="权限">
          <el-select v-model="editMemberDialog.form.permission" style="width: 100%">
            <el-option label="成员" value="member" />
            <el-option label="管理员" value="admin" />
          </el-select>
        </el-form-item>

        <el-form-item label="状态">
          <el-select v-model="editMemberDialog.form.status" style="width: 100%">
            <el-option label="已通过" value="approved" />
            <el-option label="待审核" value="pending" />
            <el-option label="已拒绝" value="rejected" />
          </el-select>
        </el-form-item>

        <el-form-item label="职位">
          <el-input v-model="editMemberDialog.form.position" placeholder="请输入职位" />
        </el-form-item>

        <el-form-item label="部门">
          <el-input v-model="editMemberDialog.form.department" placeholder="请输入部门" />
        </el-form-item>
      </el-form>

      <template #footer>
        <div class="dialog-footer">
          <el-button @click="editMemberDialog.visible = false">取消</el-button>
          <el-button type="primary" :loading="editMemberDialog.loading" @click="saveMemberInfo">
            保存
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<style lang="scss" scoped>
.team-management {
  // 团队概览容器
  .team-overview-container {
    display: flex;
    gap: 20px;
    margin-bottom: 20px;
    align-items: stretch; // 确保等高

    // 左侧统计数据容器
    .team-stats-wrapper {
      flex: 1;
      min-width: 0; // 防止 flex 子元素撑开

      // 三列网格布局
      .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 20px;
        height: 100%; // 确保填满父容器高度
      }
    }

    // 右侧用户信息容器
    .user-info-wrapper {
      width: 400px; // 固定宽度
      flex-shrink: 0;
      transition: all 0.3s ease-in-out;
    }

    .stat-card {
      display: flex;
      align-items: center;

      :deep(.el-card__body) {
        width: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
      }
    }

    .stat-card,
    .user-info-card {
      border: 1px solid #e4e7ed;
      height: 100%; // 确保卡片填满容器高度

      .stat-content {
        text-align: center;

        .stat-icon {
          width: 48px;
          height: 48px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          margin: 0 auto 16px;

          .el-icon {
            font-size: 24px;
            color: #fff;
          }

          &.blue {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          }

          &.orange {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
          }

          &.purple {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
          }
        }

        .stat-number {
          font-size: 32px;
          font-weight: bold;
          color: #303133;
          margin-bottom: 8px;
        }

        .stat-label {
          font-size: 14px;
          color: #909399;
        }
      }

      // 用户信息卡片样式
      .user-info-content {
        .user-avatar-section {
          display: flex;
          align-items: center;
          gap: 12px;
          margin-bottom: 16px;
          padding-bottom: 12px;
          border-bottom: 1px solid #f0f0f0;

          .user-basic-info {
            flex: 1;

            .user-name {
              font-size: 15px;
              font-weight: 600;
              color: #303133;
              margin-bottom: 2px;
            }

            .user-username {
              font-size: 12px;
              color: #909399;
            }
          }
        }

        .user-detail-info {
          .info-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px 12px;

            .info-item {
              display: flex;
              flex-direction: column;
              gap: 2px;
              font-size: 12px;

              .info-label {
                color: #909399;
                font-weight: 500;
                font-size: 11px;
              }

              .info-value {
                color: #303133;
                font-size: 12px;
                word-break: break-all;
              }

              .el-tag {
                align-self: flex-start;
                font-size: 11px;
                height: 20px;
                line-height: 18px;
                padding: 0 6px;
              }
            }
          }
        }
      }
    }
  }

  .main-card {
    border: 1px solid #e4e7ed;

    .search-filters {
      margin-bottom: 20px;
      padding: 20px;
      background: #fafafa;
      border-radius: 6px;
    }

    .batch-operations {
      margin-bottom: 16px;
      padding: 16px;
      background: #f0f9ff;
      border: 1px solid #bfdbfe;
      border-radius: 6px;
      display: flex;

      .batch-operations-select {
        width: 200px;
        margin-right: 12px;
        @media (max-width: 768px) {
          width: 120px;
        }
      }
    }

    .member-info {
      display: flex;
      align-items: center;
      gap: 12px;

      .member-details {
        .member-name {
          font-weight: 500;
          color: #303133;
          margin-bottom: 4px;
        }

        .member-username {
          font-size: 12px;
          color: #909399;
          margin-bottom: 2px;
        }

        .member-email {
          font-size: 12px;
          color: #909399;
        }
      }
    }

    .text-secondary {
      color: #909399;
      font-size: 12px;
    }

    .change-item {
      margin-bottom: 4px;
      font-size: 12px;

      .change-field {
        font-weight: 500;
        margin-right: 8px;
      }

      .change-value {
        color: #409eff;
      }
    }

    @media screen and (max-width: 768px) {
      .mobile-actions {
        display: flex;
        flex-direction: column;
        width: 60px;
        gap: 8px; /* 按钮之间的间距 */

        .el-button {
          width: 100%;
          margin: 0;
        }
      }
    }

    .pagination-wrapper {
      margin-top: 20px;
      text-align: right;
    }
  }
}

// 响应式布局
@media (max-width: 1400px) {
  .team-management {
    .team-overview-container {
      .user-info-wrapper {
        width: 300px; // 中等屏幕稍微缩小宽度
        transition: all 0.3s ease-in-out;
      }
    }
  }
}
@media (max-width: 1200px) {
  .team-management {
    .team-overview-container {
      .user-info-wrapper {
        width: 280px; // 中等屏幕稍微缩小宽度
        transition: all 0.3s ease-in-out;
      }
    }
  }
}

@media (max-width: 1050px) {
  .team-management {
    .team-overview-container {
      flex-direction: column; // 小屏幕垂直排列

      .team-stats-wrapper {
        width: 100%;
      }

      .user-info-wrapper {
        width: 100%; // 小屏幕占满宽度

        .user-info-card {
          .user-info-content {
            .user-detail-info {
              .info-grid {
                grid-template-columns: repeat(3, 1fr); // 小屏幕改为3列
              }
            }
          }
        }
      }
    }
  }
}

@media (max-width: 768px) {
  .team-management {
    .team-overview-container {
      .stats-grid {
        gap: 10px; // 减小间距

        .stat-card {
          .stat-content {
            .stat-icon {
              width: 40px;
              height: 40px;
              margin-bottom: 12px;

              .el-icon {
                font-size: 20px;
              }
            }

            .stat-number {
              font-size: 24px;
              margin-bottom: 6px;
            }

            .stat-label {
              font-size: 12px;
            }
          }
        }
      }
    }

    .search-filters {
      .el-col {
        margin-bottom: 12px;

        &:last-child {
          margin-bottom: 0;
        }
      }
    }

    .main-card {
      :deep(.el-table) {
        font-size: 12px;
      }
    }
  }
}

@media (max-width: 480px) {
  .team-management {
    .team-overview-container {
      .stats-grid {
        gap: 8px; // 更小的间距

        .stat-card {
          .stat-content {
            .stat-icon {
              width: 36px;
              height: 36px;
              margin-bottom: 8px;

              .el-icon {
                font-size: 18px;
              }
            }

            .stat-number {
              font-size: 20px;
              margin-bottom: 4px;
            }

            .stat-label {
              font-size: 11px;
            }
          }
        }
      }

      .user-info-wrapper {
        .user-info-card {
          .user-info-content {
            .user-detail-info {
              .info-grid {
                grid-template-columns: 1fr 1fr; // 超小屏幕回到2列
                gap: 6px 8px;
              }
            }
          }
        }
      }
    }
  }
}
</style>
