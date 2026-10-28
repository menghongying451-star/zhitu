<script setup>
import { ref, onMounted, computed } from 'vue'
import {
  Plus,
  Upload,
  CircleCheck,
  Clock,
  Edit,
  Check,
  Close,
  View,
  Warning,
  RefreshRight
} from '@element-plus/icons-vue'
import { useEnterpriseStore, useUserStore } from '@/stores'
import { enterpriseInfoService } from '@/api'
import { useRouter } from 'vue-router'

const userStore = useUserStore()
const enterpriseStore = useEnterpriseStore()
const router = useRouter()

const companyForm = ref({})
const originalForm = ref({}) // 保存原始数据用于取消编辑
const isEditing = ref(false) // 编辑状态
const isLoading = ref(false) // 加载状态
const logoUploading = ref(false) // Logo上传状态
const uploadRef = ref() // 上传组件引用

// 权限判断 - 只有拥有者和管理员可以编辑
const canEdit = computed(() => {
  const userRole = enterpriseStore.teamManagement?.userRole
  return userRole === 'owner' || userRole === 'admin'
})

// 是否为组织创建者
const isOwner = computed(() => {
  return enterpriseStore.teamManagement?.userRole === 'owner'
})

// 表单验证规则
const formRules = {
  name: [{ required: true, message: '请输入组织名称', trigger: 'blur' }],
  code: [{ required: true, message: '请输入组织代码', trigger: 'blur' }],
  contactEmail: [{ type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }],
  website: [{ type: 'url', message: '请输入正确的网址格式', trigger: 'blur' }]
}

onMounted(async () => {
  await loadEnterpriseInfo()
})

// 加载企业信息
const loadEnterpriseInfo = async () => {
  try {
    isLoading.value = true
    const res = await enterpriseInfoService.getEnterpriseInfo(
      userStore.user.company_profile.organization.id
    )

    if (res.data) {
      const { organization, contact_info, leader_info, member_stats } = res.data
      const formData = {
        // 组织基本信息
        id: organization.id,
        name: organization.name,
        code: organization.code,
        organizationType: organization.organization_type,
        organizationTypeDisplay: organization.organization_type_display,

        typeDisplay: organization.type_display,
        enterpriseType: organization.enterprise_type,
        enterpriseTypeDisplay: organization.enterprise_type_display,
        universityType: organization.university_type,
        universityTypeDisplay: organization.university_type_display,

        // 其他组织特有字段
        otherType: organization.other_type,
        otherTypeDisplay: organization.other_type_display,
        organizationNature: organization.organization_nature,
        organizationNatureDisplay: organization.organization_nature_display,
        businessScope: organization.business_scope,
        regulatoryAuthority: organization.regulatory_authority,
        licenseInfo: organization.license_info,
        serviceTarget: organization.service_target,
        serviceTargetDisplay: organization.service_target_display,

        industryOrDiscipline: organization.industry_or_discipline,
        scale: organization.scale,
        address: organization.address,
        postalCode: organization.postal_code,
        description: organization.description,
        website: organization.website,
        establishedDate: organization.established_date,
        logo: organization.logo,
        status: organization.status,
        statusDisplay: organization.status_display,
        createdAt: organization.created_at,
        updatedAt: organization.updated_at,
        verifiedAt: organization.verified_at,
        rejectedReason: organization.rejected_reason, // 拒绝原因

        // 联系信息
        contactPerson: contact_info?.contact_person || '',
        contactPosition: contact_info?.contact_position || '',
        contactPhone: contact_info?.contact_phone || '',
        contactEmail: contact_info?.contact_email || '',

        // 负责人信息
        leaderName: leader_info?.leader_name || '',
        leaderTitle: leader_info?.leader_title || ''
      }

      companyForm.value = { ...formData }
      originalForm.value = { ...formData }

      enterpriseStore.updateCompanyInfo(companyForm.value)
      enterpriseStore.updateTeamStats({
        totalMembers: member_stats?.total_members || 0,
        pendingMembers: member_stats?.pending_members || 0,
        admins: member_stats?.admins || 0,
        userRole: member_stats?.user_role || '',
        userRoleDisplay: member_stats?.user_role_display || '',
        userStatus: member_stats?.user_status || '',
        userStatusDisplay: member_stats?.user_status_display || '',
        userPosition: member_stats?.user_position || '',
        userDepartment: member_stats?.user_department || ''
      })
    } else {
      companyForm.value = enterpriseStore.companyInfo || {}
      originalForm.value = { ...companyForm.value }
    }
  } catch (error) {
    console.error('获取企业信息失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 开始编辑
const startEdit = () => {
  if (!canEdit.value) {
    ElMessage.warning('您没有编辑权限')
    return
  }
  originalForm.value = { ...companyForm.value }
  isEditing.value = true
}

// 取消编辑
const cancelEdit = () => {
  ElMessageBox.confirm('确定要取消编辑吗？未保存的更改将丢失。', '确认取消', {
    confirmButtonText: '确定',
    cancelButtonText: '继续编辑',
    type: 'warning'
  })
    .then(() => {
      companyForm.value = { ...originalForm.value }
      isEditing.value = false
    })
    .catch(() => {
      // 用户选择继续编辑，不做任何操作
    })
}

// 保存企业信息
const saveEnterpriseInfo = async () => {
  try {
    isLoading.value = true

    // 构造提交数据
    const submitData = {
      name: companyForm.value.name,
      enterprise_type: companyForm.value.enterpriseType,
      university_type: companyForm.value.universityType,
      // 其他组织字段
      other_type: companyForm.value.otherType,
      organization_nature: companyForm.value.organizationNature,
      business_scope: companyForm.value.businessScope,
      regulatory_authority: companyForm.value.regulatoryAuthority,
      license_info: companyForm.value.licenseInfo,
      service_target: companyForm.value.serviceTarget,

      industry_or_discipline: companyForm.value.industryOrDiscipline,
      scale: companyForm.value.scale,
      address: companyForm.value.address,
      postal_code: companyForm.value.postalCode,
      description: companyForm.value.description,
      website: companyForm.value.website,
      established_date:
        companyForm.value.establishedDate != originalForm.value.establishedDate
          ? companyForm.value.establishedDate.toISOString().split('T')[0]
          : originalForm.value.establishedDate, // 截取年-月-日
      contact_person: companyForm.value.contactPerson,
      contact_position: companyForm.value.contactPosition,
      contact_phone: companyForm.value.contactPhone,
      contact_email: companyForm.value.contactEmail,
      leader_name: companyForm.value.leaderName,
      leader_title: companyForm.value.leaderTitle
    }

    await enterpriseInfoService.updateEnterpriseInfo(submitData)

    // 更新本地状态
    originalForm.value = { ...companyForm.value }
    enterpriseStore.updateCompanyInfo(companyForm.value)
    userStore.setUser({
      company_profile: {
        organization: { ...companyForm.value }
      }
    })
    isEditing.value = false

    ElMessage.success('企业信息保存成功')

    // 重新加载数据以获取最新状态
    await loadEnterpriseInfo()
  } catch (error) {
    console.error('保存企业信息失败:', error)
    ElMessage.error('保存企业信息失败，请重试')
  } finally {
    isLoading.value = false
  }
}

// 触发文件上传
const triggerUpload = () => {
  if (!canEdit.value || logoUploading.value) {
    return
  }
  uploadRef.value?.$el.querySelector('input[type="file"]')?.click()
}

// Logo上传前验证
const beforeLogoUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt2M = file.size / 1024 / 1024 < 2

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt2M) {
    ElMessage.error('图片大小不能超过 2MB!')
    return false
  }
  return true
}

// Logo上传处理
const handleLogoUpload = async (options) => {
  if (!canEdit.value) {
    ElMessage.warning('您没有上传权限')
    return false
  }

  try {
    logoUploading.value = true

    // 创建FormData对象
    const formData = new FormData()
    // 使用 options.file 而不是 file.raw
    formData.append('logo', options.file)

    // 调用上传API
    const response = await enterpriseInfoService.uploadEnterpriseLogo(formData)

    if (response.data && response.data.logo) {
      // 更新logo URL
      companyForm.value.logo = response.data.logo

      // 如果不在编辑模式，立即保存
      if (!isEditing.value) {
        originalForm.value.logo = response.data.logo
        enterpriseStore.updateCompanyInfo(companyForm.value)
        userStore.setUser({
          company_profile: {
            organization: {
              ...companyForm.value,
              logo: response.data.logo
            }
          }
        })
      }

      ElMessage.success('Logo上传成功')
    } else {
      ElMessage.error('Logo上传失败，请重试')
    }
  } catch (error) {
    console.error('Logo上传失败:', error)
    ElMessage.error('Logo上传失败，请重试')
  } finally {
    logoUploading.value = false
  }

  return false // 阻止element-plus的默认上传行为
}

// 判断是否为企业
const isEnterprise = computed(() => companyForm.value.organizationType === 'enterprise')

// 判断是否为大学
const isUniversity = computed(() => companyForm.value.organizationType === 'university')

// 判断是否为其他组织
const isOtherOrganization = computed(() => companyForm.value.organizationType === 'other')

// 企业类型选项
const enterpriseTypeOptions = [
  { label: '国有企业', value: 'state_owned' },
  { label: '民营企业', value: 'private' },
  { label: '外资企业', value: 'foreign' },
  { label: '合资企业', value: 'joint_venture' },
  { label: '创业公司', value: 'startup' },
  { label: '上市公司', value: 'listed' },
  { label: '其他', value: 'other' }
]

// 大学类型选项
const universityTypeOptions = [
  { label: '985工程', value: '985' },
  { label: '211工程', value: '211' },
  { label: '双一流', value: 'double_first_class' },
  { label: '普通本科', value: 'ordinary' },
  { label: '高职专科', value: 'vocational' },
  { label: '独立学院', value: 'independent' },
  { label: '民办大学', value: 'private_university' }
]

// 其他组织类型选项
const otherTypeOptions = [
  { label: '政府机构', value: 'government' },
  { label: '非营利组织', value: 'ngo' },
  { label: '基金会', value: 'foundation' },
  { label: '行业协会', value: 'association' },
  { label: '科研院所', value: 'research_institute' },
  { label: '医疗机构', value: 'hospital' },
  { label: '媒体机构', value: 'media' },
  { label: '文化机构', value: 'cultural' },
  { label: '体育组织', value: 'sports' },
  { label: '宗教组织', value: 'religious' },
  { label: '国际组织', value: 'international' },
  { label: '社区组织', value: 'community' },
  { label: '合作社', value: 'cooperative' },
  { label: '工会组织', value: 'union' },
  { label: '商会', value: 'chamber' },
  { label: '其他未分类', value: 'other_unspecified' }
]

// 组织性质选项
const organizationNatureOptions = [
  { label: '公立/公办', value: 'public' },
  { label: '私立/民办', value: 'private' },
  { label: '公私合营', value: 'joint' },
  { label: '国际性', value: 'international' },
  { label: '地区性', value: 'regional' },
  { label: '全国性', value: 'national' }
]

// 服务对象选项
const serviceTargetOptions = [
  { label: '面向公众', value: 'public' },
  { label: '面向会员', value: 'members' },
  { label: '面向行业', value: 'industry' },
  { label: '面向政府', value: 'government' },
  { label: '面向企业', value: 'enterprises' },
  { label: '面向学生', value: 'students' },
  { label: '面向患者', value: 'patients' },
  { label: '面向社区', value: 'community' },
  { label: '其他', value: 'other' }
]

// 规模选项
const scaleOptions = [
  { label: '小型（1-500人）', value: 'small' },
  { label: '中型（501-2000人）', value: 'medium' },
  { label: '大型（2001-10000人）', value: 'large' },
  { label: '超大型（10000人以上）', value: 'giant' }
]

// 根据其他组织类型判断是否需要显示特定字段
const shouldShowRegulatoryAuthority = computed(() => {
  return ['government', 'ngo', 'foundation'].includes(companyForm.value.otherType)
})

const shouldShowLicenseInfo = computed(() => {
  return ['hospital', 'research_institute'].includes(companyForm.value.otherType)
})

const shouldShowServiceTarget = computed(() => {
  return ['association', 'chamber', 'union'].includes(companyForm.value.otherType)
})

// 格式化日期显示
const formatDate = (dateStr) => {
  if (!dateStr) return '暂无'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

// 获取认证状态显示文本
const getCertificationText = computed(() => {
  if (isEnterprise.value) return '企业认证'
  if (isUniversity.value) return '高校认证'
  return '组织认证'
})

// 获取组织类型显示文本
const getOrganizationTypeText = computed(() => {
  if (isEnterprise.value) return '企业'
  if (isUniversity.value) return '大学'
  return '组织'
})

const certificationDialogVisible = ref(false)
const certificationStatusData = ref({})
const loadingCertificationStatus = ref(false)

// 认证状态相关的计算属性
const certificationConfig = computed(() => {
  const status = companyForm.value.status

  switch (status) {
    case 'pending':
      return {
        icon: Clock,
        iconColor: '#faad14',
        tagType: 'warning',
        tagText: '待认证',
        statusText: '待认证',
        statusDesc: '请尽快提交认证材料',
        bgClass: 'pending',
        showAction: isOwner.value,
        actionText: '开始认证',
        actionType: 'primary'
      }
    case 'under_review':
      return {
        icon: Clock,
        iconColor: '#1890ff',
        tagType: 'primary',
        tagText: '审核中',
        statusText: '审核中',
        statusDesc: '认证材料审核中，请耐心等待',
        bgClass: 'under-review',
        showAction: isOwner.value,
        actionText: '查看进度',
        actionType: 'default'
      }
    case 'verified':
      return {
        icon: CircleCheck,
        iconColor: '#52c41a',
        tagType: 'success',
        tagText: '已认证',
        statusText: '已认证',
        statusDesc: `认证时间：${formatDate(companyForm.value.verifiedAt)}`,
        bgClass: 'verified',
        showAction: isOwner.value,
        actionText: '查看认证',
        actionType: 'success'
      }
    case 'rejected':
      return {
        icon: Warning,
        iconColor: '#ff4d4f',
        tagType: 'danger',
        tagText: '认证被拒',
        statusText: '认证被拒',
        statusDesc: companyForm.value.rejectedReason || '认证材料不符合要求',
        bgClass: 'rejected',
        showAction: isOwner.value,
        actionText: '重新认证',
        actionType: 'primary'
      }
    case 'closed':
      return {
        icon: Warning,
        iconColor: '#8c8c8c',
        tagType: 'info',
        tagText: '已关闭',
        statusText: '已关闭',
        statusDesc: '组织已关闭',
        bgClass: 'closed',
        showAction: false,
        actionText: '',
        actionType: 'default'
      }
    default:
      return {
        icon: Clock,
        iconColor: '#faad14',
        tagType: 'warning',
        tagText: '待认证',
        statusText: '待认证',
        statusDesc: '请尽快提交认证材料',
        bgClass: 'pending',
        showAction: isOwner.value,
        actionText: '开始认证',
        actionType: 'primary'
      }
  }
})

// 认证操作处理
const handleCertificationAction = () => {
  const status = companyForm.value.status

  switch (status) {
    case 'pending':
      // 跳转到认证页面
      startCertification()
      break
    case 'under_review':
      // 查看审核进度
      viewCertificationProgress()
      break
    case 'verified':
      // 查看认证证书
      viewCertificate()
      break
    case 'rejected':
      // 重新认证
      reApplyCertification()
      break
    default:
      break
  }
}

// 开始认证
const startCertification = () => {
  // 这里应该跳转到认证页面或打开认证对话框
  // ElMessage.info('跳转到认证页面...')
  router.push('/enterprise/certification')
}

// 获取认证状态详情
const loadCertificationStatus = async () => {
  try {
    loadingCertificationStatus.value = true
    const res = await enterpriseInfoService.getOrganizationVerificationStatus()

    if (res.data) {
      certificationStatusData.value = res.data
    }
  } catch (error) {
    console.error('获取认证状态失败:', error)
    ElMessage.error('获取认证状态失败，请重试')
  } finally {
    loadingCertificationStatus.value = false
  }
}

// 查看认证进度 - 修改这个函数
const viewCertificationProgress = async () => {
  await loadCertificationStatus()
  certificationDialogVisible.value = true
}

// 查看认证证书 - 修改这个函数，实际上和查看进度是一样的
const viewCertificate = async () => {
  await loadCertificationStatus()
  certificationDialogVisible.value = true
}

// 计算认证进度百分比
const verificationProgress = computed(() => {
  if (!certificationStatusData.value.verification_progress) return 0

  const progress = certificationStatusData.value.verification_progress
  const completedSteps = Object.values(progress).filter(Boolean).length
  const totalSteps = Object.keys(progress).length

  return Math.round((completedSteps / totalSteps) * 100)
})

// 认证步骤配置
const verificationSteps = computed(() => [
  {
    key: 'basic_info_completed',
    label: '基本信息',
    description: '组织名称、类型等基本信息',
    completed: certificationStatusData.value.verification_progress?.basic_info_completed || false
  },
  {
    key: 'contact_info_completed',
    label: '联系信息',
    description: '联系人、电话、邮箱等信息',
    completed: certificationStatusData.value.verification_progress?.contact_info_completed || false
  },
  {
    key: 'address_completed',
    label: '地址信息',
    description: '详细地址、邮政编码等',
    completed: certificationStatusData.value.verification_progress?.address_completed || false
  },
  {
    key: 'leader_info_completed',
    label: '负责人信息',
    description: '法定代表人或负责人信息',
    completed: certificationStatusData.value.verification_progress?.leader_info_completed || false
  },
  {
    key: 'code_completed',
    label: '组织代码',
    description: '统一社会信用代码等',
    completed: certificationStatusData.value.verification_progress?.code_completed || false
  }
])

// 获取状态配置（用于对话框中的状态显示）
const getDialogStatusConfig = computed(() => {
  const orgStatus = certificationStatusData.value.organization_status
  const userStatus = certificationStatusData.value.user_status

  switch (orgStatus) {
    case 'pending':
      return {
        icon: Clock,
        iconColor: '#faad14',
        statusText: '待提交认证',
        statusDesc: '请完善必要信息后提交认证申请',
        bgClass: 'warning'
      }
    case 'under_review':
      return {
        icon: Clock,
        iconColor: '#1890ff',
        statusText: '审核中',
        statusDesc: '认证材料正在审核中，请耐心等待',
        bgClass: 'primary'
      }
    case 'verified':
      return {
        icon: CircleCheck,
        iconColor: '#52c41a',
        statusText: '认证通过',
        statusDesc: '恭喜！您的组织认证已通过',
        bgClass: 'success'
      }
    case 'rejected':
      return {
        icon: Warning,
        iconColor: '#ff4d4f',
        statusText: '认证被拒',
        statusDesc: '认证材料不符合要求，请修改后重新提交',
        bgClass: 'danger'
      }
    default:
      return {
        icon: Clock,
        iconColor: '#faad14',
        statusText: '待认证',
        statusDesc: '请尽快提交认证材料',
        bgClass: 'warning'
      }
  }
})

// 重新认证
const reApplyCertification = () => {
  ElMessageBox.confirm('确定要重新申请认证吗？将重新提交认证材料。', '重新认证', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  })
    .then(() => {
      // 跳转到认证页面
      startCertification()
    })
    .catch(() => {
      // 取消操作
    })
}
</script>

<template>
  <div class="company-info" v-loading="isLoading">
    <el-row :gutter="20">
      <el-col :lg="16" :xs="24">
        <div class="info-forms">
          <!-- 基本信息 -->
          <el-card class="info-card" shadow="never">
            <template #header>
              <div class="card-header">
                <div class="header-left">
                  <h3>{{ getOrganizationTypeText }}基本信息</h3>
                  <el-tag :type="certificationConfig.tagType" size="small">
                    {{ certificationConfig.tagText }}
                  </el-tag>
                </div>
                <div class="header-actions">
                  <template v-if="canEdit">
                    <template v-if="!isEditing">
                      <el-button type="primary" size="small" @click="startEdit">
                        <el-icon><Edit /></el-icon>
                        编辑信息
                      </el-button>
                    </template>
                    <template v-else>
                      <el-button
                        type="success"
                        size="small"
                        :loading="isLoading"
                        @click="saveEnterpriseInfo"
                      >
                        <el-icon><Check /></el-icon>
                        保存
                      </el-button>
                      <el-button type="default" size="small" @click="cancelEdit">
                        <el-icon><Close /></el-icon>
                        取消
                      </el-button>
                    </template>
                  </template>
                  <el-tag v-else type="info" size="small">只读模式</el-tag>
                </div>
              </div>
            </template>

            <el-form
              :model="companyForm"
              :rules="formRules"
              label-position="top"
              size="large"
              ref="companyFormRef"
            >
              <el-row :gutter="20">
                <el-col :md="12" :xs="24">
                  <el-form-item :label="getOrganizationTypeText + '名称'" prop="name">
                    <el-input
                      v-model="companyForm.name"
                      :placeholder="`请输入${getOrganizationTypeText}名称`"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
                <el-col :md="12" :xs="24">
                  <el-form-item :label="'统一社会信用代码'" prop="code">
                    <el-input
                      v-model="companyForm.code"
                      :placeholder="`请输入统一社会信用代码`"
                      :readonly="true"
                    />
                  </el-form-item>
                </el-col>

                <!-- 企业类型 -->
                <el-col v-if="isEnterprise" :md="12" :xs="24">
                  <el-form-item label="企业类型" prop="enterpriseType">
                    <el-select
                      v-model="companyForm.enterpriseType"
                      placeholder="请选择企业类型"
                      style="width: 100%"
                      :disabled="!isEditing"
                    >
                      <el-option
                        v-for="option in enterpriseTypeOptions"
                        :key="option.value"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>

                <!-- 大学类型 -->
                <el-col v-if="isUniversity" :md="12" :xs="24">
                  <el-form-item label="大学类型" prop="universityType">
                    <el-select
                      v-model="companyForm.universityType"
                      placeholder="请选择大学类型"
                      style="width: 100%"
                      :disabled="!isEditing"
                    >
                      <el-option
                        v-for="option in universityTypeOptions"
                        :key="option.value"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>

                <!-- 其他组织类型 -->
                <el-col v-if="isOtherOrganization" :md="12" :xs="24">
                  <el-form-item label="组织类型" prop="otherType">
                    <el-select
                      v-model="companyForm.otherType"
                      placeholder="请选择组织类型"
                      style="width: 100%"
                      :disabled="!isEditing"
                    >
                      <el-option
                        v-for="option in otherTypeOptions"
                        :key="option.value"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>

                <!-- 组织性质 -->
                <el-col v-if="isOtherOrganization" :md="12" :xs="24">
                  <el-form-item label="组织性质" prop="organizationNature">
                    <el-select
                      v-model="companyForm.organizationNature"
                      placeholder="请选择组织性质"
                      style="width: 100%"
                      :disabled="!isEditing"
                    >
                      <el-option
                        v-for="option in organizationNatureOptions"
                        :key="option.value"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>

                <el-col :md="12" :xs="24">
                  <el-form-item label="规模" prop="scale">
                    <el-select
                      v-model="companyForm.scale"
                      placeholder="请选择规模"
                      style="width: 100%"
                      :disabled="!isEditing"
                    >
                      <el-option
                        v-for="option in scaleOptions"
                        :key="option.value"
                        :label="option.label"
                        :value="option.value"
                      />
                    </el-select>
                  </el-form-item>
                </el-col>
                <el-col :md="12" :xs="24">
                  <el-form-item
                    :label="
                      isEnterprise ? '所属行业' : isUniversity ? '主要学科门类' : '行业/学科领域'
                    "
                    prop="industryOrDiscipline"
                  >
                    <el-input
                      v-model="companyForm.industryOrDiscipline"
                      :placeholder="`请输入${isEnterprise ? '所属行业' : isUniversity ? '主要学科门类' : '行业/学科领域'}`"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
                <el-col :md="12" :xs="24">
                  <el-form-item label="成立时间" prop="establishedDate">
                    <el-date-picker
                      v-model="companyForm.establishedDate"
                      type="date"
                      placeholder="请选择成立时间"
                      style="width: 100%"
                      :disabled="!isEditing"
                    />
                  </el-form-item>
                </el-col>
                <el-col :md="12" :xs="24">
                  <el-form-item label="邮政编码" prop="postalCode">
                    <el-input
                      v-model="companyForm.postalCode"
                      placeholder="请输入邮政编码"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="详细地址" prop="address">
                    <el-input
                      v-model="companyForm.address"
                      placeholder="请输入详细地址"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="官方网站" prop="website">
                    <el-input
                      v-model="companyForm.website"
                      placeholder="请输入官方网站"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>

                <!-- 其他组织特有字段 -->
                <template v-if="isOtherOrganization">
                  <!-- 业务范围 -->
                  <el-col :span="24">
                    <el-form-item label="业务范围/服务领域" prop="businessScope">
                      <el-input
                        v-model="companyForm.businessScope"
                        type="textarea"
                        :rows="3"
                        placeholder="请输入业务范围或服务领域..."
                        :readonly="!isEditing"
                        maxlength="200"
                        show-word-limit
                      />
                    </el-form-item>
                  </el-col>

                  <!-- 监管机构 -->
                  <el-col v-if="shouldShowRegulatoryAuthority" :span="24">
                    <el-form-item label="监管机构" prop="regulatoryAuthority">
                      <el-input
                        v-model="companyForm.regulatoryAuthority"
                        placeholder="请输入监管机构"
                        :readonly="!isEditing"
                        maxlength="100"
                      />
                    </el-form-item>
                  </el-col>

                  <!-- 许可证/资质信息 -->
                  <el-col v-if="shouldShowLicenseInfo" :span="24">
                    <el-form-item label="许可证/资质信息" prop="licenseInfo">
                      <el-input
                        v-model="companyForm.licenseInfo"
                        type="textarea"
                        :rows="4"
                        placeholder="请输入相关的许可证号、资质证书等信息..."
                        :readonly="!isEditing"
                      />
                    </el-form-item>
                  </el-col>

                  <!-- 服务对象 -->
                  <el-col v-if="shouldShowServiceTarget" :md="12" :xs="24">
                    <el-form-item label="服务对象" prop="serviceTarget">
                      <el-select
                        v-model="companyForm.serviceTarget"
                        placeholder="请选择服务对象"
                        style="width: 100%"
                        :disabled="!isEditing"
                      >
                        <el-option
                          v-for="option in serviceTargetOptions"
                          :key="option.value"
                          :label="option.label"
                          :value="option.value"
                        />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </template>

                <el-col :span="24">
                  <el-form-item :label="`${getOrganizationTypeText}简介`" prop="description">
                    <el-input
                      v-model="companyForm.description"
                      type="textarea"
                      :rows="4"
                      :placeholder="`请输入${getOrganizationTypeText}简介...`"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <!-- 负责人信息 -->
          <el-card class="info-card" shadow="never">
            <template #header>
              <h3>负责人信息</h3>
            </template>

            <el-form :model="companyForm" label-position="top" size="large">
              <el-row :gutter="20">
                <el-col :md="12" :xs="24">
                  <el-form-item
                    :label="isEnterprise ? '法定代表人' : isUniversity ? '校长' : '负责人姓名'"
                    prop="leaderName"
                  >
                    <el-input
                      v-model="companyForm.leaderName"
                      :placeholder="`请输入${isEnterprise ? '法定代表人' : isUniversity ? '校长' : '负责人'}姓名`"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
                <el-col :md="12" :xs="24">
                  <el-form-item label="负责人职务" prop="leaderTitle">
                    <el-input
                      v-model="companyForm.leaderTitle"
                      placeholder="请输入负责人职务"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>

          <!-- 联系信息 -->
          <el-card class="info-card" shadow="never">
            <template #header>
              <h3>联系信息</h3>
            </template>

            <el-form :model="companyForm" label-position="top" size="large">
              <el-row :gutter="20">
                <el-col :md="12" :xs="24">
                  <el-form-item label="联系人" prop="contactPerson">
                    <el-input
                      v-model="companyForm.contactPerson"
                      placeholder="请输入联系人"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
                <el-col :md="12" :xs="24">
                  <el-form-item label="联系人职位" prop="contactPosition">
                    <el-input
                      v-model="companyForm.contactPosition"
                      placeholder="请输入联系人职位"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
                <el-col :md="12" :xs="24">
                  <el-form-item label="联系电话" prop="contactPhone">
                    <el-input
                      v-model="companyForm.contactPhone"
                      placeholder="请输入联系电话"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
                <el-col :md="12" :xs="24">
                  <el-form-item label="联系邮箱" prop="contactEmail">
                    <el-input
                      v-model="companyForm.contactEmail"
                      placeholder="请输入联系邮箱"
                      :readonly="!isEditing"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-form>
          </el-card>
        </div>
      </el-col>

      <el-col :lg="8" :xs="24">
        <div class="side-content">
          <!-- Logo -->
          <el-card class="info-card" shadow="never">
            <template #header>
              <h3>{{ getOrganizationTypeText }}标志</h3>
            </template>

            <div class="logo-upload">
              <!-- Logo展示区域 -->
              <div
                class="logo-display"
                v-loading="logoUploading"
                :class="{ clickable: canEdit }"
                @click="canEdit ? triggerUpload() : null"
              >
                <img v-if="companyForm.logo" :src="companyForm.logo" class="logo-image" />
                <div v-else class="logo-placeholder">
                  <el-icon class="logo-icon"><Plus /></el-icon>
                  <span class="placeholder-text">点击上传Logo</span>
                </div>
                <!-- 悬浮提示 -->
                <div v-if="canEdit && companyForm.logo" class="logo-overlay">
                  <el-icon class="overlay-icon"><Upload /></el-icon>
                  <span class="overlay-text">点击更换</span>
                </div>
              </div>

              <!-- 上传组件和按钮 -->
              <div class="upload-actions" v-if="canEdit">
                <el-upload
                  ref="uploadRef"
                  class="logo-uploader"
                  action="#"
                  :show-file-list="false"
                  :before-upload="beforeLogoUpload"
                  :http-request="handleLogoUpload"
                  :disabled="!canEdit || logoUploading"
                  style="display: none"
                >
                  <div></div>
                </el-upload>

                <el-button
                  type="default"
                  size="small"
                  :loading="logoUploading"
                  :disabled="logoUploading"
                  @click="triggerUpload"
                >
                  <el-icon><Upload /></el-icon>
                  {{ companyForm.logo ? '更换Logo' : '上传Logo' }}
                </el-button>
                <p class="upload-tip">支持JPG、PNG格式，建议尺寸200x200px，大小不超过2MB</p>
              </div>

              <div v-if="!canEdit" class="upload-tip">
                <p>您没有上传权限</p>
              </div>
            </div>
          </el-card>

          <!-- 认证状态 -->
          <el-card class="info-card" shadow="never">
            <template #header>
              <div class="card-header">
                <h3>认证状态</h3>
                <el-button
                  v-if="certificationConfig.showAction"
                  :type="certificationConfig.actionType"
                  size="small"
                  @click="handleCertificationAction"
                >
                  <el-icon>
                    <View
                      v-if="
                        companyForm.status === 'under_review' || companyForm.status === 'verified'
                      "
                    />
                    <RefreshRight v-else-if="companyForm.status === 'rejected'" />
                    <CircleCheck v-else />
                  </el-icon>
                  {{ certificationConfig.actionText }}
                </el-button>
              </div>
            </template>

            <div class="certification-status">
              <div class="cert-item" :class="certificationConfig.bgClass">
                <div class="cert-info">
                  <el-icon class="cert-icon" :style="{ color: certificationConfig.iconColor }">
                    <component :is="certificationConfig.icon" />
                  </el-icon>
                  <div class="cert-details">
                    <span class="cert-name">{{ getCertificationText }}</span>
                    <div class="cert-time">
                      <span
                        :class="{
                          'success-text': companyForm.status === 'verified',
                          'warning-text':
                            companyForm.status === 'pending' ||
                            companyForm.status === 'under_review',
                          'danger-text': companyForm.status === 'rejected',
                          'info-text': companyForm.status === 'closed'
                        }"
                      >
                        {{ certificationConfig.statusDesc }}
                      </span>
                    </div>
                    <!-- 被拒绝时显示详细原因 -->
                    <div
                      v-if="companyForm.status === 'rejected' && companyForm.rejectedReason"
                      class="rejection-reason"
                    >
                      <span class="reason-label">拒绝原因：</span>
                      <span class="reason-text">{{ companyForm.rejectedReason || '未提供' }}</span>
                    </div>
                  </div>
                </div>
                <el-tag :type="certificationConfig.tagType" size="small">
                  {{ certificationConfig.tagText }}
                </el-tag>
              </div>
            </div>
          </el-card>

          <!-- 其他组织信息概览 -->
          <!-- <el-card v-if="isOtherOrganization" class="info-card" shadow="never">
            <template #header>
              <h3>组织信息概览</h3>
            </template>

            <div class="org-overview">
              <div class="overview-item">
                <span class="label">组织类型：</span>
                <span class="value">{{ companyForm.otherTypeDisplay || '未设置' }}</span>
              </div>
              <div class="overview-item">
                <span class="label">组织性质：</span>
                <span class="value">{{ companyForm.organizationNatureDisplay || '未设置' }}</span>
              </div>
              <div v-if="shouldShowServiceTarget" class="overview-item">
                <span class="label">服务对象：</span>
                <span class="value">{{ companyForm.serviceTargetDisplay || '未设置' }}</span>
              </div>
              <div
                v-if="shouldShowRegulatoryAuthority && companyForm.regulatoryAuthority"
                class="overview-item"
              >
                <span class="label">监管机构：</span>
                <span class="value">{{ companyForm.regulatoryAuthority }}</span>
              </div>
            </div>
          </el-card> -->
        </div>
      </el-col>
    </el-row>
  </div>

  <!-- 认证状态详情对话框 -->
  <el-dialog
    v-model="certificationDialogVisible"
    :title="companyForm.status === 'verified' ? '认证证书' : '认证进度'"
    width="600px"
    top="8vh"
    :close-on-click-modal="false"
    :before-close="() => (certificationDialogVisible = false)"
    class="certification-dialog-wrapper"
  >
    <div v-loading="loadingCertificationStatus" class="certification-dialog">
      <!-- 认证状态概览 -->
      <div class="status-overview">
        <div class="status-header" :class="getDialogStatusConfig.bgClass">
          <el-icon class="status-icon" :style="{ color: getDialogStatusConfig.iconColor }">
            <component :is="getDialogStatusConfig.icon" />
          </el-icon>
          <div class="status-content">
            <h4>{{ getDialogStatusConfig.statusText }}</h4>
            <p>{{ getDialogStatusConfig.statusDesc }}</p>
          </div>
        </div>
      </div>

      <!-- 组织信息概览 -->
      <div class="org-summary">
        <h5>组织信息</h5>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="label">组织名称：</span>
            <span class="value">{{
              certificationStatusData.organization_name || companyForm.name
            }}</span>
          </div>
          <div class="summary-item">
            <span class="label">组织类型：</span>
            <span class="value">{{ companyForm.organizationTypeDisplay || '企业' }}</span>
          </div>
          <div class="summary-item">
            <span class="label">组织状态：</span>
            <span class="value">{{ certificationStatusData.organization_status_display }}</span>
          </div>
          <div class="summary-item">
            <span class="label">用户状态：</span>
            <span class="value">{{ certificationStatusData.user_status_display }}</span>
          </div>
        </div>
      </div>

      <!-- 认证进度详情 -->
      <div v-if="certificationStatusData.verification_progress" class="progress-section">
        <h5>认证进度</h5>

        <!-- 进度条 -->
        <div class="progress-bar-section">
          <el-progress
            :percentage="verificationProgress"
            :color="verificationProgress === 100 ? '#52c41a' : '#409eff'"
            :stroke-width="6"
          />
          <span class="progress-text">{{ verificationProgress }}% 完成</span>
        </div>

        <!-- 步骤详情 -->
        <div class="steps-list">
          <div
            v-for="step in verificationSteps"
            :key="step.key"
            class="step-item"
            :class="{ completed: step.completed }"
          >
            <div class="step-icon">
              <el-icon v-if="step.completed" class="check-icon">
                <CircleCheck />
              </el-icon>
              <el-icon v-else class="pending-icon">
                <Clock />
              </el-icon>
            </div>
            <div class="step-content">
              <h6>{{ step.label }}</h6>
              <p>{{ step.description }}</p>
            </div>
            <div class="step-status">
              <el-tag :type="step.completed ? 'success' : 'info'" size="small">
                {{ step.completed ? '已完成' : '待完成' }}
              </el-tag>
            </div>
          </div>
        </div>
      </div>

      <!-- 已认证状态的特殊显示 -->
      <div v-if="companyForm.status === 'verified'" class="verified-info">
        <div class="certificate-info">
          <el-icon class="cert-icon"><CircleCheck /></el-icon>
          <div class="cert-details">
            <h5>认证证书</h5>
            <p>认证时间：{{ formatDate(companyForm.verifiedAt) }}</p>
            <p>认证类型：{{ getCertificationText }}</p>
          </div>
        </div>
      </div>

      <!-- 被拒绝时显示拒绝原因 -->
      <div v-if="companyForm.status === 'rejected'" class="rejection-details">
        <h5>拒绝原因</h5>
        <div class="rejection-box">
          <el-icon class="warning-icon"><Warning /></el-icon>
          <p>{{ companyForm.rejectedReason || '认证材料不符合要求，请检查后重新提交。' }}</p>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="certificationDialogVisible = false">关闭</el-button>
        <el-button
          v-if="companyForm.status === 'pending' || companyForm.status === 'rejected'"
          type="primary"
          @click="startCertification"
        >
          {{ companyForm.status === 'rejected' ? '重新认证' : '开始认证' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<style lang="scss" scoped>
.company-info {
  .info-forms {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .side-content {
    display: flex;
    flex-direction: column;
    gap: 20px;
  }

  .info-card {
    border: 1px solid #e4e7ed;

    :deep(.el-card__header) {
      background: #fafafa;
      border-bottom: 1px solid #e4e7ed;

      .card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;

        .header-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .header-actions {
          display: flex;
          align-items: center;
          gap: 8px;
        }
      }

      h3 {
        margin: 0;
        font-size: 16px;
        font-weight: 600;
        color: #303133;
      }
    }

    // 只读状态样式
    :deep(.el-input.is-disabled .el-input__wrapper),
    :deep(.el-textarea.is-disabled .el-textarea__inner),
    :deep(.el-select.is-disabled .el-select__wrapper) {
      background-color: #f8f9fa;
      border-color: #e9ecef;
      cursor: default;
    }

    :deep(.el-input[readonly] .el-input__wrapper),
    :deep(.el-textarea[readonly] .el-textarea__inner) {
      background-color: #f8f9fa;
      border-color: #e9ecef;
      cursor: default;
    }
  }

  .logo-upload {
    text-align: center;
    position: relative;

    .logo-display {
      display: inline-block;
      position: relative;
      margin-bottom: 16px;
      width: 100px;
      height: 100px;

      &.clickable {
        cursor: pointer;
      }

      .logo-image {
        width: 100px;
        height: 100px;
        border-radius: 8px;
        object-fit: cover;
        border: 1px solid #e4e7ed;
        transition: opacity 0.3s;
        display: block;
      }

      .logo-placeholder {
        width: 100px;
        height: 100px;
        border: 2px dashed #dcdfe6;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: border-color 0.3s;
        margin: 0 auto;

        &:hover {
          border-color: #409eff;
        }

        .logo-icon {
          font-size: 24px;
          color: #8c939d;
          margin-bottom: 4px;
        }

        .placeholder-text {
          font-size: 12px;
          color: #8c939d;
        }
      }

      .logo-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100px;
        height: 100px;
        background: rgba(0, 0, 0, 0.6);
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s;
        color: white;
        box-sizing: border-box;

        .overlay-icon {
          font-size: 20px;
          margin-bottom: 4px;
        }

        .overlay-text {
          font-size: 12px;
        }
      }

      &:hover .logo-overlay {
        opacity: 1;
      }

      &:hover .logo-image {
        opacity: 0.8;
      }
    }

    .upload-actions {
      display: flex;
      flex-direction: column;
      gap: 8px;
      align-items: center;

      button {
        width: 85px;
      }

      .upload-tip {
        margin: 0;
        font-size: 12px;
        color: #909399;
        line-height: 1.4;
      }
    }

    .upload-tip {
      margin-top: 16px;

      p {
        margin: 0;
        font-size: 12px;
        color: #909399;
      }
    }
  }

  .certification-status {
    .cert-item {
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      padding: 16px;
      border-radius: 8px;
      gap: 12px;

      &.pending {
        background: #fffbf0;
        border: 1px solid #ffd54f;
      }

      &.under-review {
        background: #f0f9ff;
        border: 1px solid #91d5ff;
      }

      &.verified {
        background: #f6ffed;
        border: 1px solid #b7eb8f;
      }

      &.rejected {
        background: #fff2f0;
        border: 1px solid #ffccc7;
      }

      &.closed {
        background: #f5f5f5;
        border: 1px solid #d9d9d9;
      }

      .cert-info {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        flex: 1;
        min-width: 0;

        .cert-icon {
          font-size: 18px;
          margin-top: 2px;
          flex-shrink: 0;
        }

        .cert-details {
          display: flex;
          flex-direction: column;
          gap: 4px;
          min-width: 0;
          flex: 1;

          .cert-name {
            font-weight: 500;
            font-size: 14px;
            color: #303133;
          }

          .cert-time {
            font-size: 12px;
            line-height: 1.4;

            .success-text {
              color: #52c41a;
            }

            .warning-text {
              color: #faad14;
            }

            .danger-text {
              color: #ff4d4f;
            }

            .info-text {
              color: #8c8c8c;
            }
          }

          .rejection-reason {
            margin-top: 8px;
            padding: 8px;
            background: #fff2f0;
            border-radius: 4px;
            border-left: 3px solid #ff4d4f;

            .reason-label {
              font-size: 12px;
              color: #8c8c8c;
              font-weight: 500;
            }

            .reason-text {
              font-size: 12px;
              color: #ff4d4f;
              word-break: break-all;
              line-height: 1.4;
            }
          }
        }
      }

      .el-tag {
        flex-shrink: 0;
        margin-top: 2px;
      }
    }
  }

  .org-overview {
    .overview-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .label {
        font-size: 14px;
        color: #666;
        font-weight: 500;
      }

      .value {
        font-size: 14px;
        color: #303133;
        text-align: right;
        max-width: 120px;
        word-break: break-all;
      }
    }
  }
}

@media (max-width: 992px) {
  .company-info {
    .side-content {
      margin-top: 20px;
    }

    .info-card :deep(.el-card__header) {
      .card-header {
        gap: 12px;

        .header-left {
          width: 180%;
        }

        .header-actions {
          width: 100%;
          justify-content: flex-end;
        }
      }
    }

    .certification-status {
      .cert-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 12px;

        .cert-info {
          width: 100%;
        }
      }
    }
  }
}

// 对话框包装器样式
:deep(.certification-dialog-wrapper) {
  .el-dialog {
    margin: 0 auto;

    // 大屏适配 - 减少顶部距离
    @media (min-width: 1200px) {
      margin-top: 8vh;
    }

    // 中等屏幕
    @media (min-width: 768px) and (max-width: 1199px) {
      margin-top: 5vh;
      width: 90% !important;
      max-width: 600px;
    }

    // 移动端适配
    @media (max-width: 767px) {
      width: 95% !important;
      max-width: none;
      margin: 20px auto;
      max-height: calc(100vh - 40px);

      .el-dialog__header {
        padding: 16px 20px 12px;

        .el-dialog__title {
          font-size: 16px;
        }

        .el-dialog__headerbtn {
          top: 16px;
          right: 16px;
        }
      }

      .el-dialog__body {
        padding: 16px 20px;
        max-height: calc(100vh - 160px);
        overflow-y: auto;
      }

      .el-dialog__footer {
        padding: 12px 20px 16px;
      }
    }
  }
}

.certification-dialog {
  // 减少各部分的间距，特别是移动端
  .status-overview {
    margin-bottom: 20px;

    .status-header {
      display: flex;
      align-items: center;
      padding: 16px;
      border-radius: 8px;
      gap: 12px;

      &.primary {
        background: #f0f9ff;
        border: 1px solid #91d5ff;
      }

      &.success {
        background: #f6ffed;
        border: 1px solid #b7eb8f;
      }

      &.warning {
        background: #fffbf0;
        border: 1px solid #ffd54f;
      }

      &.danger {
        background: #fff2f0;
        border: 1px solid #ffccc7;
      }

      .status-icon {
        font-size: 28px;
        flex-shrink: 0;
      }

      .status-content {
        flex: 1;

        h4 {
          margin: 0 0 6px 0;
          font-size: 16px;
          font-weight: 600;
          color: #303133;
        }

        p {
          margin: 0;
          font-size: 13px;
          color: #606266;
          line-height: 1.4;
        }
      }
    }
  }

  .org-summary {
    margin-bottom: 20px;

    h5 {
      margin: 0 0 12px 0;
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }

    .summary-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;

      .summary-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 10px;
        background: #f8f9fa;
        border-radius: 4px;

        .label {
          font-size: 13px;
          color: #666;
          font-weight: 500;
        }

        .value {
          font-size: 13px;
          color: #303133;
          text-align: right;
          max-width: 140px;
          word-break: break-all;
        }
      }
    }
  }

  .progress-section {
    margin-bottom: 20px;

    h5 {
      margin: 0 0 12px 0;
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }

    .progress-bar-section {
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 16px;

      :deep(.el-progress) {
        flex: 1;
      }

      .progress-text {
        font-size: 13px;
        font-weight: 600;
        color: #409eff;
        white-space: nowrap;
      }
    }

    .steps-list {
      .step-item {
        display: flex;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid #f0f0f0;
        gap: 10px;

        &:last-child {
          border-bottom: none;
        }

        &.completed {
          .step-icon .check-icon {
            color: #52c41a;
          }

          .step-content h6 {
            color: #52c41a;
          }
        }

        .step-icon {
          font-size: 16px;
          flex-shrink: 0;

          .check-icon {
            color: #52c41a;
          }

          .pending-icon {
            color: #d9d9d9;
          }
        }

        .step-content {
          flex: 1;
          min-width: 0;

          h6 {
            margin: 0 0 2px 0;
            font-size: 13px;
            font-weight: 500;
            color: #303133;
          }

          p {
            margin: 0;
            font-size: 12px;
            color: #909399;
            line-height: 1.3;
          }
        }

        .step-status {
          flex-shrink: 0;
        }
      }
    }
  }

  .verified-info {
    .certificate-info {
      display: flex;
      align-items: center;
      padding: 16px;
      background: #f6ffed;
      border: 1px solid #b7eb8f;
      border-radius: 8px;
      gap: 12px;

      .cert-icon {
        font-size: 28px;
        color: #52c41a;
        flex-shrink: 0;
      }

      .cert-details {
        flex: 1;

        h5 {
          margin: 0 0 6px 0;
          font-size: 15px;
          font-weight: 600;
          color: #52c41a;
        }

        p {
          margin: 0 0 3px 0;
          font-size: 13px;
          color: #606266;
          line-height: 1.4;

          &:last-child {
            margin-bottom: 0;
          }
        }
      }
    }
  }

  .rejection-details {
    h5 {
      margin: 0 0 12px 0;
      font-size: 15px;
      font-weight: 600;
      color: #303133;
    }

    .rejection-box {
      display: flex;
      align-items: flex-start;
      padding: 14px;
      background: #fff2f0;
      border: 1px solid #ffccc7;
      border-left: 4px solid #ff4d4f;
      border-radius: 4px;
      gap: 10px;

      .warning-icon {
        font-size: 16px;
        color: #ff4d4f;
        flex-shrink: 0;
        margin-top: 1px;
      }

      p {
        margin: 0;
        font-size: 13px;
        color: #ff4d4f;
        line-height: 1.4;
        flex: 1;
      }
    }
  }

  .dialog-footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
  }
}

// 移动端优化
@media (max-width: 767px) {
  .certification-dialog {
    .status-overview .status-header {
      flex-direction: column;
      text-align: center;
      gap: 10px;
      padding: 14px;

      .status-icon {
        font-size: 24px;
      }

      .status-content {
        h4 {
          font-size: 15px;
        }

        p {
          font-size: 12px;
        }
      }
    }

    .org-summary .summary-grid {
      grid-template-columns: 1fr;
      gap: 6px;

      .summary-item {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
        padding: 8px;

        .value {
          max-width: none;
          text-align: left;
        }
      }
    }

    .progress-section .progress-bar-section {
      flex-direction: column;
      align-items: stretch;
      gap: 8px;

      .progress-text {
        text-align: center;
        font-size: 12px;
      }
    }

    .verified-info .certificate-info {
      flex-direction: column;
      text-align: center;
      gap: 10px;
      padding: 14px;

      .cert-icon {
        font-size: 24px;
      }

      .cert-details {
        h5 {
          font-size: 14px;
        }

        p {
          font-size: 12px;
        }
      }
    }

    .rejection-details .rejection-box {
      flex-direction: column;
      text-align: center;
      gap: 8px;
      padding: 12px;

      .warning-icon {
        font-size: 20px;
        margin-top: 0;
      }

      p {
        font-size: 12px;
      }
    }

    .dialog-footer {
      flex-direction: column-reverse;
      gap: 8px;

      .el-button {
        width: 100%;
      }
    }
  }
}

// 超小屏幕（小于375px）
@media (max-width: 374px) {
  :deep(.certification-dialog-wrapper .el-dialog) {
    width: 98% !important;
    margin: 10px auto;
    max-height: calc(100vh - 20px);

    .el-dialog__body {
      padding: 12px 16px;
      max-height: calc(100vh - 140px);
    }

    .el-dialog__header {
      padding: 12px 16px 8px;
    }

    .el-dialog__footer {
      padding: 8px 16px 12px;
    }
  }
}
</style>
