<script setup>
import { ref, reactive, computed, watch } from 'vue'
import { enterpriseInfoService } from '@/api'
import { Upload, Plus } from '@element-plus/icons-vue'
import { useEnterpriseStore } from '@/stores'
import { useRouter } from 'vue-router'

const router = useRouter()

// 获取企业store
const enterpriseStore = useEnterpriseStore()

// 表单数据
const formData = reactive({
  code: '',
  leader_name: '',
  leader_title: '',
  contact_person: '',
  contact_position: '',
  contact_phone: '',
  contact_email: '',
  address: '',
  postal_code: '',
  description: '',
  website: '',
  established_date: '',
  enterprise_type: '',
  university_type: '',
  other_type: '',
  organization_nature: '',
  business_scope: '',
  regulatory_authority: '',
  license_info: '',
  service_target: '',
  verification_images: []
})

// 从store获取组织类型（只读）
const organizationType = computed(
  () => enterpriseStore.companyInfo?.organizationType || 'enterprise'
)

// 表单引用
const formRef = ref()

// 加载状态
const loading = ref(false)

// 动态构建验证规则
const rules = computed(() => {
  const baseRules = {
    code: [{ required: true, message: '请输入组织代码', trigger: 'blur' }],
    leader_name: [{ required: true, message: '请输入负责人姓名', trigger: 'blur' }],
    leader_title: [{ required: true, message: '请输入负责人职务', trigger: 'blur' }],
    contact_person: [{ required: true, message: '请输入联系人姓名', trigger: 'blur' }],
    contact_position: [{ required: true, message: '请输入联系人职务', trigger: 'blur' }],
    contact_phone: [
      { required: true, message: '请输入联系人电话', trigger: 'blur' },
      { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号码', trigger: 'blur' }
    ],
    contact_email: [
      { required: true, message: '请输入联系人邮箱', trigger: 'blur' },
      { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
    ],
    address: [{ required: true, message: '请输入地址', trigger: 'blur' }]
  }

  // 根据组织类型添加特定字段验证
  if (organizationType.value === 'enterprise') {
    baseRules.enterprise_type = [{ required: true, message: '请选择企业类型', trigger: 'change' }]
  } else if (organizationType.value === 'university') {
    baseRules.university_type = [{ required: true, message: '请选择学校类型', trigger: 'change' }]
  } else if (organizationType.value === 'other') {
    baseRules.other_type = [{ required: true, message: '请选择其他组织类型', trigger: 'change' }]

    // 根据other_type添加条件验证
    if (needsRegulatoryAuthority.value) {
      baseRules.regulatory_authority = [
        { required: true, message: '请输入监管机构', trigger: 'blur' }
      ]
    }
    if (needsLicenseInfo.value) {
      baseRules.license_info = [{ required: true, message: '请输入许可证信息', trigger: 'blur' }]
    }
    if (needsServiceTarget.value) {
      baseRules.service_target = [{ required: true, message: '请选择服务对象', trigger: 'change' }]
    }
  }

  return baseRules
})

// 企业类型选项
const enterpriseTypeOptions = [
  { label: '国有企业', value: 'state_owned' },
  { label: '民营企业', value: 'private' },
  { label: '外资企业', value: 'foreign' },
  { label: '合资企业', value: 'joint_venture' },
  { label: '其他', value: 'other' }
]

// 学校类型选项
const universityTypeOptions = [
  { label: '985院校', value: '985' },
  { label: '211院校', value: '211' },
  { label: '双一流院校', value: 'double_first_class' },
  { label: '本科院校', value: 'undergraduate' },
  { label: '职业院校', value: 'vocational' },
  { label: '其他', value: 'other' }
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
  { label: '其他未分类', value: 'other' }
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

// 获取组织类型的显示名称
const organizationTypeLabel = computed(() => {
  const typeMap = {
    enterprise: '企业',
    university: '学校',
    other: '其他组织'
  }
  return typeMap[organizationType.value] || '未知类型'
})

// 计算是否需要显示特定字段
const needsRegulatoryAuthority = computed(() => {
  return ['government', 'ngo', 'foundation'].includes(formData.other_type)
})

const needsLicenseInfo = computed(() => {
  return ['hospital', 'research_institute'].includes(formData.other_type)
})

const needsServiceTarget = computed(() => {
  return ['association', 'chamber', 'union'].includes(formData.other_type)
})

// 监听other_type变化，清空条件字段
watch(
  () => formData.other_type,
  (newValue) => {
    if (!needsRegulatoryAuthority.value) {
      formData.regulatory_authority = ''
    }
    if (!needsLicenseInfo.value) {
      formData.license_info = ''
    }
    if (!needsServiceTarget.value) {
      formData.service_target = ''
    }
  }
)

// 文件上传处理
const handleFileChange = (file, fileList) => {
  console.log('文件变化:', fileList)
  formData.verification_images = fileList
}

const handleFileRemove = (file, fileList) => {
  console.log('文件移除:', fileList)
  formData.verification_images = fileList
}

const beforeUpload = (file) => {
  const isValidType = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'].includes(file.type)
  const isValidSize = file.size / 1024 / 1024 < 10

  if (!isValidType) {
    ElMessage.error('只能上传 JPEG/PNG/GIF/WebP 格式的图片!')
    return false
  }
  if (!isValidSize) {
    ElMessage.error('图片大小不能超过 10MB!')
    return false
  }
  return true
}

// 提交表单
const submitForm = async () => {
  try {
    await formRef.value.validate()

    console.log('当前图片列表:', formData.verification_images)

    if (!formData.verification_images || formData.verification_images.length === 0) {
      ElMessage.error('请至少上传一张认证图片')
      return
    }

    loading.value = true

    // 构建FormData
    const submitData = new FormData()

    // 添加基本字段
    Object.keys(formData).forEach((key) => {
      if (key !== 'verification_images' && formData[key]) {
        submitData.append(key, formData[key])
      }
    })

    // 添加组织类型（从store获取）
    submitData.append('organization_type', organizationType.value)

    // 添加图片文件
    formData.verification_images.forEach((fileItem, index) => {
      const file = fileItem.raw || fileItem
      if (file) {
        if (index === 0) {
          submitData.append('verification_image_1', file)
        } else {
          submitData.append(`verification_image_${index + 1}`, file)
        }
      }
    })

    // 调用API
    const response = await enterpriseInfoService.organizationVerification(submitData)

    if (response.status === 'success') {
      ElMessage.success(response.message)
      // 可以在这里添加跳转逻辑
      router.push('/enterprise/enterprise-settings')
    } else {
      ElMessage.error(response.message || '提交失败')
    }
  } catch (error) {
    console.error('提交认证信息失败:', error)
    ElMessage.error('提交失败, 请检查表单输入或联系管理员')
  } finally {
    loading.value = false
  }
}

// 重置表单
const resetForm = () => {
  formRef.value.resetFields()
  formData.verification_images = []
}
</script>

<template>
  <div class="certification-page">
    <div class="certification-container">
      <h1 class="page-title">企业认证</h1>

      <el-form
        ref="formRef"
        :model="formData"
        :rules="rules"
        label-width="120px"
        class="certification-form"
      >
        <!-- 显示组织类型（只读） -->
        <el-form-item label="组织类型">
          <el-input :value="organizationTypeLabel" readonly class="readonly-input" />
        </el-form-item>

        <!-- 基本信息 -->
        <div class="form-section">
          <h3 class="section-title">基本信息</h3>

          <el-form-item label="组织代码" prop="code">
            <el-input
              v-model="formData.code"
              placeholder="请输入统一社会信用代码/教育部代码/其他相关证照编号"
            />
          </el-form-item>

          <el-form-item label="地址" prop="address">
            <el-input v-model="formData.address" placeholder="请输入详细地址" />
          </el-form-item>

          <el-form-item label="邮政编码">
            <el-input v-model="formData.postal_code" placeholder="请输入邮政编码" />
          </el-form-item>

          <el-form-item label="官方网站">
            <el-input v-model="formData.website" placeholder="请输入官方网站地址" />
          </el-form-item>

          <el-form-item label="创立时间">
            <el-date-picker
              v-model="formData.established_date"
              type="date"
              placeholder="请选择创立时间"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>

          <el-form-item label="组织描述">
            <el-input
              v-model="formData.description"
              type="textarea"
              :rows="3"
              placeholder="请输入组织简介"
            />
          </el-form-item>
        </div>

        <!-- 负责人信息 -->
        <div class="form-section">
          <h3 class="section-title">负责人信息</h3>

          <el-form-item label="负责人姓名" prop="leader_name">
            <el-input v-model="formData.leader_name" placeholder="请输入负责人姓名" />
          </el-form-item>

          <el-form-item label="负责人职务" prop="leader_title">
            <el-input v-model="formData.leader_title" placeholder="请输入负责人职务" />
          </el-form-item>
        </div>

        <!-- 联系人信息 -->
        <div class="form-section">
          <h3 class="section-title">联系人信息</h3>

          <el-form-item label="联系人姓名" prop="contact_person">
            <el-input v-model="formData.contact_person" placeholder="请输入联系人姓名" />
          </el-form-item>

          <el-form-item label="联系人职务" prop="contact_position">
            <el-input v-model="formData.contact_position" placeholder="请输入联系人职务" />
          </el-form-item>

          <el-form-item label="联系人电话" prop="contact_phone">
            <el-input v-model="formData.contact_phone" placeholder="请输入联系人电话" />
          </el-form-item>

          <el-form-item label="联系人邮箱" prop="contact_email">
            <el-input v-model="formData.contact_email" placeholder="请输入联系人邮箱" />
          </el-form-item>
        </div>

        <!-- 企业特定字段 -->
        <div v-if="organizationType === 'enterprise'" class="form-section">
          <h3 class="section-title">企业信息</h3>

          <el-form-item label="企业类型" prop="enterprise_type">
            <el-select v-model="formData.enterprise_type" placeholder="请选择企业类型">
              <el-option
                v-for="option in enterpriseTypeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
        </div>

        <!-- 学校特定字段 -->
        <div v-if="organizationType === 'university'" class="form-section">
          <h3 class="section-title">学校信息</h3>

          <el-form-item label="学校类型" prop="university_type">
            <el-select v-model="formData.university_type" placeholder="请选择学校类型">
              <el-option
                v-for="option in universityTypeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
        </div>

        <!-- 其他组织特定字段 -->
        <div v-if="organizationType === 'other'" class="form-section">
          <h3 class="section-title">组织信息</h3>

          <el-form-item label="组织类型" prop="other_type">
            <el-select v-model="formData.other_type" placeholder="请选择组织类型">
              <el-option
                v-for="option in otherTypeOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="组织性质">
            <el-select v-model="formData.organization_nature" placeholder="请选择组织性质">
              <el-option
                v-for="option in organizationNatureOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>

          <el-form-item label="业务范围">
            <el-input
              v-model="formData.business_scope"
              type="textarea"
              :rows="3"
              placeholder="请描述组织的主要业务范围或服务领域"
            />
          </el-form-item>

          <!-- 条件显示的字段 -->
          <el-form-item
            v-if="needsRegulatoryAuthority"
            label="监管机构"
            prop="regulatory_authority"
          >
            <el-input v-model="formData.regulatory_authority" placeholder="请输入监管机构" />
          </el-form-item>

          <el-form-item v-if="needsLicenseInfo" label="许可证信息" prop="license_info">
            <el-input
              v-model="formData.license_info"
              type="textarea"
              :rows="3"
              placeholder="请输入许可证相关信息"
            />
          </el-form-item>

          <el-form-item v-if="needsServiceTarget" label="服务对象" prop="service_target">
            <el-select v-model="formData.service_target" placeholder="请选择服务对象">
              <el-option
                v-for="option in serviceTargetOptions"
                :key="option.value"
                :label="option.label"
                :value="option.value"
              />
            </el-select>
          </el-form-item>
        </div>

        <!-- 认证图片上传 -->
        <div class="form-section">
          <h3 class="section-title">认证材料</h3>

          <el-form-item label="认证图片" required>
            <el-upload
              class="upload-demo"
              action="#"
              :on-change="handleFileChange"
              :on-remove="handleFileRemove"
              :before-upload="beforeUpload"
              :file-list="formData.verification_images"
              :auto-upload="false"
              multiple
              :limit="5"
              list-type="picture-card"
            >
              <el-icon class="avatar-uploader-icon"><Plus /></el-icon>
              <template #tip>
                <div class="el-upload__tip">
                  支持JPEG/PNG/GIF/WebP格式，单个文件不超过10MB，最多上传5张
                </div>
              </template>
            </el-upload>

            <!-- 显示当前已上传的文件数量 -->
            <div v-if="formData.verification_images.length > 0" class="upload-info">
              已上传 {{ formData.verification_images.length }} 张图片
            </div>
          </el-form-item>
        </div>

        <!-- 提交按钮 -->
        <el-form-item class="submit-buttons">
          <el-button type="primary" :loading="loading" @click="submitForm">
            提交认证申请
          </el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<style scoped lang="scss">
.certification-page {
  width: 100%;
  min-height: 100vh;
  background-color: #f0f0f0;
  padding: 20px;
}

.certification-container {
  max-width: 800px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  padding: 30px;
}

.page-title {
  text-align: center;
  margin-bottom: 30px;
  color: #303133;
  font-size: 24px;
  font-weight: 500;
}

.readonly-input {
  :deep(.el-input__inner) {
    background-color: #f5f7fa;
    cursor: not-allowed;
  }
}

.certification-form {
  .form-section {
    margin-bottom: 30px;

    .section-title {
      color: #409eff;
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 20px;
      padding-bottom: 8px;
      border-bottom: 2px solid #409eff;
    }
  }

  .submit-buttons {
    text-align: center;
    margin-top: 40px;

    .el-button {
      padding: 12px 30px;
      font-size: 16px;
    }
  }
}

.upload-demo {
  :deep(.el-upload-list--picture-card) {
    .el-upload-list__item {
      width: 120px;
      height: 120px;
    }
  }

  :deep(.el-upload--picture-card) {
    width: 120px;
    height: 120px;
    line-height: 120px;
  }

  .avatar-uploader-icon {
    font-size: 28px;
    color: #8c939d;
    width: 120px;
    height: 120px;
    text-align: center;
  }
}

.upload-info {
  margin-top: 8px;
  color: #67c23a;
  font-size: 14px;
}

// 响应式设计
@media (max-width: 768px) {
  .certification-page {
    padding: 10px;
  }

  .certification-container {
    padding: 20px;
  }

  .certification-form {
    :deep(.el-form-item__label) {
      width: 100px !important;
    }
  }
}
</style>
