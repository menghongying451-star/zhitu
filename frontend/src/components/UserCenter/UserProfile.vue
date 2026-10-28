<script setup>
import { ref, onMounted, computed } from 'vue'
import { useUserStore } from '@/stores'
import { userService } from '@/api'
import { Plus, Upload } from '@element-plus/icons-vue'

const userStore = useUserStore()
const userData = ref({})

// 标签相关状态
const interestTagList = ref([])
const skillTagList = ref([])
const interestLoading = ref(false)
const skillLoading = ref(false)

// 学校相关状态
const schoolList = ref([])
const schoolLoading = ref(false)

onMounted(async () => {
  let res = await userService.getCurrentUser()
  userData.value = res.data
  userStore.setUser({ ...userData.value })

  // === 新增：获取用户数据后立即标准化 school ===
  if (userData.value?.student_profile) {
    userData.value.student_profile.school = normalizeSchoolField(
      userData.value.student_profile.school
    )
  }

  // 初始化已选择的标签
  initSelectedTags()
})

// 计算属性：判断用户类型
const isStudent = computed(() => userData.value.user_type === 'student')
const isOrganization = computed(() => userData.value.user_type === 'organization')

// 初始化已选择的标签选项和回显数据
const initSelectedTags = () => {
  if (userData.value.student_profile) {
    // 处理学校信息回显
    if (userData.value.student_profile.school) {
      // 如果school是对象，设置school_id
      if (typeof userData.value.student_profile.school === 'object') {
        userData.value.student_profile.school_id = userData.value.student_profile.school.id
        // 将当前学校添加到学校列表中，用于显示
        schoolList.value = [
          {
            id: userData.value.student_profile.school.id,
            school: userData.value.student_profile.school.name
          }
        ]
      }
    }

    // 处理兴趣标签回显
    if (userData.value.student_profile.interests?.length) {
      // 将已有的兴趣标签添加到选项列表中，供显示使用
      interestTagList.value = [...userData.value.student_profile.interests]

      // 设置已选中的兴趣标签ID
      userData.value.student_profile.interest_tags = userData.value.student_profile.interests.map(
        (item) => item.id
      )
    } else {
      userData.value.student_profile.interest_tags = []
    }

    // 处理技能标签回显
    if (userData.value.student_profile.skills?.length) {
      // 将已有的技能标签添加到选项列表中，供显示使用
      skillTagList.value = [...userData.value.student_profile.skills]

      // 设置已选中的技能标签ID
      userData.value.student_profile.ability_tags = userData.value.student_profile.skills.map(
        (item) => item.id
      )
    } else {
      userData.value.student_profile.ability_tags = []
    }
  }
}

// === 新增 BEGIN：school 字段兼容处理 ===
function normalizeSchoolField(s) {
  if (!s) return { id: '', name: '' }
  if (typeof s === 'string') return { id: '', name: s }
  if (typeof s === 'object') {
    return {
      id: s.id ?? '',
      name: s.name ?? s.title ?? s.label ?? ''
    }
  }
  return { id: '', name: String(s) }
}

const studentSchoolName = computed(() => {
  const s = userData.value?.student_profile?.school
  if (!s) return ''
  if (typeof s === 'string') return s
  if (typeof s === 'object') return s.name || s.title || s.label || ''
  return ''
})
// === 新增 END：school 字段兼容处理 ===

// 基础资料编辑
const isBasicEdit = ref(false)
const toggleBasicEdit = () => {
  if (isBasicEdit.value) {
    userData.value = { ...userStore.user }
  }
  isBasicEdit.value = !isBasicEdit.value
}

const handleUpdateUserBasic = async () => {
  try {
    await userService.updateCurrentUser({
      username: userData.value.username,
      real_name: userData.value.real_name,
      age: userData.value.age,
      gender: userData.value.gender,
      bio: userData.value.bio
    })
    userStore.setUser({ ...userData.value })
    ElMessage.success('基础资料更新成功')
    isBasicEdit.value = false
  } catch (error) {
    ElMessage.error(error.detail || '更新基础资料失败')
  }
}

// 学生信息编辑
const isStudentEdit = ref(false)
const toggleStudentEdit = () => {
  if (isStudentEdit.value) {
    userData.value = { ...userStore.user }
    // 重新初始化标签数据
    initSelectedTags()
    // === 新增：重新标准化 school，确保存在 {id,name} 结构 ===
    if (userData.value.student_profile) {
      userData.value.student_profile.school = normalizeSchoolField(
        userData.value.student_profile.school
      )
    }
  }
  isStudentEdit.value = !isStudentEdit.value
}

// 搜索兴趣标签
const searchInterestTags = async (query) => {
  if (!query) {
    // 如果没有搜索词，显示已选择的标签
    if (userData.value.student_profile?.interests?.length) {
      interestTagList.value = [...userData.value.student_profile.interests]
    }
    return
  }

  interestLoading.value = true
  try {
    const res = await userService.getInterestTagList(query)
    const searchResults = res.data || []

    // 合并搜索结果和已选择的标签，避免重复
    const existingIds = userData.value.student_profile?.interests?.map((item) => item.id) || []
    const filteredResults = searchResults.filter((item) => !existingIds.includes(item.id))

    interestTagList.value = [
      ...(userData.value.student_profile?.interests || []),
      ...filteredResults
    ]
  } catch (error) {
    console.error('搜索兴趣标签失败:', error)
    // 出错时至少保持已选择的标签
    if (userData.value.student_profile?.interests?.length) {
      interestTagList.value = [...userData.value.student_profile.interests]
    }
  } finally {
    interestLoading.value = false
  }
}

// 搜索技能标签
const searchSkillTags = async (query) => {
  if (!query) {
    // 如果没有搜索词，显示已选择的标签
    if (userData.value.student_profile?.skills?.length) {
      skillTagList.value = [...userData.value.student_profile.skills]
    }
    return
  }

  skillLoading.value = true
  try {
    const res = await userService.getSkillTagList(query)
    const searchResults = res.data || []

    // 合并搜索结果和已选择的标签，避免重复
    const existingIds = userData.value.student_profile?.skills?.map((item) => item.id) || []
    const filteredResults = searchResults.filter((item) => !existingIds.includes(item.id))

    skillTagList.value = [...(userData.value.student_profile?.skills || []), ...filteredResults]
  } catch (error) {
    console.error('搜索技能标签失败:', error)
    // 出错时至少保持已选择的标签
    if (userData.value.student_profile?.skills?.length) {
      skillTagList.value = [...userData.value.student_profile.skills]
    }
  } finally {
    skillLoading.value = false
  }
}

// 搜索学校
const searchSchools = async (query) => {
  if (!query) {
    // 如果没有搜索词，显示已选择的学校
    if (
      userData.value.student_profile?.school &&
      typeof userData.value.student_profile.school === 'object'
    ) {
      schoolList.value = [
        {
          id: userData.value.student_profile.school.id,
          school: userData.value.student_profile.school.name
        }
      ]
    }
    return
  }

  schoolLoading.value = true
  try {
    // 使用enterpriseInfoService中的searchUniversities方法搜索学校
    const { enterpriseInfoService } = await import('@/api/enterprise/info')
    const res = await enterpriseInfoService.searchUniversities({
      search: query,
      page: 1,
      page_size: 20
    })
    const searchResults = res.data?.universities || []

    schoolList.value = searchResults
  } catch (error) {
    console.error('搜索学校失败:', error)
    // 出错时至少保持已选择的学校
    if (
      userData.value.student_profile?.school &&
      typeof userData.value.student_profile.school === 'object'
    ) {
      schoolList.value = [
        {
          id: userData.value.student_profile.school.id,
          school: userData.value.student_profile.school.name
        }
      ]
    }
  } finally {
    schoolLoading.value = false
  }
}

const handleUpdateStudentInfo = async () => {
  try {
    // === 修改 BEGIN：提交时 school 兼容对象/字符串 ===
    const updateData = {
      student_profile: {
        school_id: userData.value.student_profile.school_id,
        major: userData.value.student_profile.major,
        grade: userData.value.student_profile.grade,
        education_level: userData.value.student_profile.education_level,
        expected_graduation: userData.value.student_profile.expected_graduation,
        interest_tags: userData.value.student_profile.interest_tags || [],
        ability_tags: userData.value.student_profile.ability_tags || [],
        ...(userData.value.student_profile.student_id !==
          userStore.user.student_profile.student_id && {
          student_id: userData.value.student_profile.student_id
        })
      }
    }
    // === 修改 END：提交时 school 兼容对象/字符串 ===

    await userService.updateCurrentUser(updateData)
    userStore.setUser({ ...userData.value })
    ElMessage.success('学生信息更新成功')
    isStudentEdit.value = false
  } catch (error) {
    ElMessage.error(error.detail || '更新学生信息失败')
  }
}

// 添加 ref 引用
const interestSelectRef = ref(null)
const skillSelectRef = ref(null)
// 处理兴趣标签选择变化
const handleInterestChange = (selectedIds) => {
  // 确保选择的标签在选项列表中
  selectedIds.forEach((id) => {
    if (!interestTagList.value.find((tag) => tag.id === id)) {
      // 如果选项列表中没有这个标签，从原始数据中找到并添加
      const originalTag = userData.value.student_profile?.interests?.find((tag) => tag.id === id)
      if (originalTag) {
        interestTagList.value.push(originalTag)
      }
    }
  })
  // 清除搜索关键词
  if (interestSelectRef.value) {
    interestSelectRef.value.query = ''
    // 重置选项列表为已选择的标签
    interestTagList.value = userData.value.student_profile?.interests || []
  }
}

// 处理技能标签选择变化
const handleSkillChange = (selectedIds) => {
  // 确保选择的标签在选项列表中
  selectedIds.forEach((id) => {
    if (!skillTagList.value.find((tag) => tag.id === id)) {
      // 如果选项列表中没有这个标签，从原始数据中找到并添加
      const originalTag = userData.value.student_profile?.skills?.find((tag) => tag.id === id)
      if (originalTag) {
        skillTagList.value.push(originalTag)
      }
    }
  })

  // 清除搜索关键词
  if (skillSelectRef.value) {
    skillSelectRef.value.query = ''
    // 重置选项列表为已选择的标签
    skillTagList.value = userData.value.student_profile?.skills || []
  }
}

// 企业信息编辑（只读，显示认证状态）
const getStatusColor = (status) => {
  switch (status) {
    case 'pending':
    case 'pending_verification':
      return '#eab308'
    case 'unverified':
    case 'rejected':
      return '#ef4444'
    case 'verified':
    case 'active':
      return '#22c55e'
    default:
      return '#6b7280'
  }
}

// 头像上传
const uploadRef = ref(null)
const beforeAvatarUpload = (file) => {
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

const uploadAvatarRequest = async ({ file }) => {
  const formData = new FormData()
  formData.append('avatar', file)
  try {
    const res = await userService.uploadAvatar(formData)
    userData.value.avatar = res.data.avatar
    userStore.setUser({ ...userStore.user, avatar: userData.value.avatar })
    ElMessage.success('头像上传成功')
  } catch (error) {
    ElMessage.error(error.detail || '头像上传失败')
  }
}

const triggerUpload = () => {
  const inputEl = uploadRef.value.$el.querySelector('input[type=file]')
  if (inputEl) inputEl.click()
}
</script>

<template>
  <div class="user-profile">
    <el-row :gutter="20">
      <!-- 左侧：基础资料 + 详细信息 -->
      <el-col :lg="16" :xs="24">
        <!-- 基础信息卡片 -->
        <el-card class="setting-card" shadow="never">
          <template #header>
            <div class="header-content">
              <h3>基础资料</h3>
              <div class="header-actions">
                <el-button type="text" @click="toggleBasicEdit">
                  {{ isBasicEdit ? '取消' : '编辑' }}
                </el-button>
                <el-button v-if="isBasicEdit" type="primary" @click="handleUpdateUserBasic">
                  保存
                </el-button>
              </div>
            </div>
          </template>
          <el-form :model="userData" label-position="top" size="large">
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="用户名">
                  <el-input
                    v-model="userData.username"
                    :disabled="!isBasicEdit"
                    placeholder="请输入用户名"
                  />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="真实姓名">
                  <el-input
                    v-model="userData.real_name"
                    :disabled="!isBasicEdit"
                    placeholder="请输入真实姓名"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="年龄">
                  <el-input-number
                    v-model="userData.age"
                    :disabled="!isBasicEdit"
                    :min="0"
                    :max="100"
                    placeholder="请输入年龄"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="性别">
                  <el-select
                    v-model="userData.gender"
                    :disabled="!isBasicEdit"
                    placeholder="请选择性别"
                    style="width: 100%"
                  >
                    <el-option label="男" value="male" />
                    <el-option label="女" value="female" />
                    <el-option label="未知" value="unknown" />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="个人简介">
              <el-input
                v-model="userData.bio"
                :disabled="!isBasicEdit"
                type="textarea"
                :rows="3"
                placeholder="请输入个人简介"
              />
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 学生信息卡片 -->
        <el-card
          v-if="isStudent && userData.student_profile"
          class="setting-card margin-top"
          shadow="never"
        >
          <template #header>
            <div class="header-content">
              <h3>学生信息</h3>
              <div class="header-actions">
                <span
                  class="status-badge"
                  :style="{ color: getStatusColor(userData.student_profile.status) }"
                >
                  {{ userData.student_profile.status_display || '未设置' }}
                </span>
                <el-button type="text" @click="toggleStudentEdit">
                  {{ isStudentEdit ? '取消' : '编辑' }}
                </el-button>
                <el-button v-if="isStudentEdit" type="primary" @click="handleUpdateStudentInfo">
                  保存
                </el-button>
              </div>
            </div>
          </template>
          <el-form :model="userData.student_profile" label-position="top" size="large">
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="学号">
                  <el-input
                    v-model="userData.student_profile.student_id"
                    :disabled="!isStudentEdit"
                    placeholder="请输入学号"
                  />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="学校">
                  <el-select
                    v-model="userData.student_profile.school_id"
                    :disabled="!isStudentEdit"
                    filterable
                    remote
                    reserve-keyword
                    placeholder="请搜索并选择学校"
                    :remote-method="searchSchools"
                    :loading="schoolLoading"
                    style="width: 100%"
                    value-key="id"
                  >
                    <el-option
                      v-for="school in schoolList"
                      :key="school.id"
                      :label="school.school"
                      :value="school.id"
                    />
                  </el-select>
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="专业">
                  <el-input
                    v-model="userData.student_profile.major"
                    :disabled="!isStudentEdit"
                    placeholder="请输入专业"
                  />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="入学年份">
                  <el-input
                    v-model="userData.student_profile.grade"
                    :disabled="!isStudentEdit"
                    placeholder="请输入入学年份"
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="学历">
                  <el-select
                    v-model="userData.student_profile.education_level"
                    :disabled="!isStudentEdit"
                    placeholder="请选择学历"
                    style="width: 100%"
                  >
                    <el-option label="本科生" value="undergraduate" />
                    <el-option label="硕士生" value="master" />
                    <el-option label="博士生" value="doctor" />
                    <el-option label="专科生" value="college" />
                  </el-select>
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="预计毕业时间">
                  <el-date-picker
                    v-model="userData.student_profile.expected_graduation"
                    :disabled="!isStudentEdit"
                    type="date"
                    placeholder="请选择预计毕业时间"
                    format="YYYY-MM-DD"
                    value-format="YYYY-MM-DD"
                    style="width: 100%"
                  />
                </el-form-item>
              </el-col>
            </el-row>

            <!-- 兴趣爱好 - 改为可搜索的多选标签 -->
            <el-form-item label="兴趣爱好">
              <el-select
                ref="interestSelectRef"
                v-model="userData.student_profile.interest_tags"
                :disabled="!isStudentEdit"
                multiple
                filterable
                remote
                reserve-keyword
                placeholder="请搜索并选择兴趣爱好"
                :remote-method="searchInterestTags"
                :loading="interestLoading"
                style="width: 100%"
                value-key="id"
                @change="handleInterestChange"
              >
                <el-option
                  v-for="tag in interestTagList"
                  :key="tag.id"
                  :label="tag.value"
                  :value="tag.id"
                />
              </el-select>
            </el-form-item>

            <!-- 技能 - 改为可搜索的多选标签 -->
            <el-form-item label="技能">
              <el-select
                ref="skillSelectRef"
                v-model="userData.student_profile.ability_tags"
                :disabled="!isStudentEdit"
                multiple
                filterable
                remote
                reserve-keyword
                placeholder="请搜索并选择技能"
                :remote-method="searchSkillTags"
                :loading="skillLoading"
                style="width: 100%"
                value-key="id"
                @change="handleSkillChange"
              >
                <el-option
                  v-for="tag in skillTagList"
                  :key="tag.id"
                  :label="tag.post"
                  :value="tag.id"
                >
                  <div style="display: flex; justify-content: space-between">
                    <span>{{ tag.post }}</span>
                    <span style="color: #8492a6; font-size: 13px">{{ tag.category }}</span>
                  </div>
                </el-option>
              </el-select>
            </el-form-item>
          </el-form>
        </el-card>

        <!-- 企业信息卡片 -->
        <el-card
          v-if="isOrganization && userData.company_profile"
          class="setting-card margin-top"
          shadow="never"
        >
          <template #header>
            <div class="header-content">
              <h3>企业信息</h3>
              <div class="header-actions">
                <span
                  class="status-badge"
                  :style="{ color: getStatusColor(userData.company_profile.status) }"
                >
                  {{ userData.company_profile.status_display || '未认证' }}
                </span>
              </div>
            </div>
          </template>
          <el-form :model="userData.company_profile" label-position="top" size="large">
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="职位">
                  <el-input v-model="userData.company_profile.position" disabled />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="部门">
                  <el-input v-model="userData.company_profile.department" disabled />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="权限等级">
                  <el-input v-model="userData.company_profile.permission_display" disabled />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="加入时间">
                  <el-input v-model="userData.company_profile.joined_at" disabled />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>

          <!-- 组织详细信息 -->
          <el-divider>组织详情</el-divider>
          <el-form
            v-if="userData.company_profile.organization"
            :model="userData.company_profile.organization"
            label-position="top"
            size="large"
          >
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="组织名称">
                  <el-input v-model="userData.company_profile.organization.name" disabled />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="组织类型">
                  <el-input
                    v-model="userData.company_profile.organization.organization_type_display"
                    disabled
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="企业类型">
                  <el-input
                    v-model="userData.company_profile.organization.enterprise_type_display"
                    disabled
                  />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="规模">
                  <el-input
                    v-model="userData.company_profile.organization.scale_display"
                    disabled
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="行业/学科">
                  <el-input
                    v-model="userData.company_profile.organization.industry_or_discipline"
                    disabled
                  />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="注册号">
                  <el-input
                    v-model="userData.company_profile.organization.registration_number"
                    disabled
                  />
                </el-form-item>
              </el-col>
            </el-row>
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="负责人">
                  <el-input v-model="userData.company_profile.organization.leader_name" disabled />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="负责人头衔">
                  <el-input v-model="userData.company_profile.organization.leader_title" disabled />
                </el-form-item>
              </el-col>
            </el-row>
            <el-form-item label="组织描述">
              <el-input
                v-model="userData.company_profile.organization.description"
                type="textarea"
                :rows="3"
                disabled
              />
            </el-form-item>
            <el-row :gutter="20">
              <el-col :lg="12" :xs="24">
                <el-form-item label="官网地址">
                  <el-input v-model="userData.company_profile.organization.website" disabled />
                </el-form-item>
              </el-col>
              <el-col :lg="12" :xs="24">
                <el-form-item label="认证时间">
                  <el-input v-model="userData.company_profile.organization.verified_at" disabled />
                </el-form-item>
              </el-col>
            </el-row>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧：头像上传 -->
      <el-col class="avatar-col" :lg="8" :xs="24">
        <el-card class="setting-card avatar-card" shadow="never">
          <template #header>
            <h3>头像</h3>
          </template>
          <div class="avatar-upload">
            <el-upload
              ref="uploadRef"
              class="avatar-uploader"
              :show-file-list="false"
              :before-upload="beforeAvatarUpload"
              :http-request="uploadAvatarRequest"
            >
              <img v-if="userData.avatar" :src="userData.avatar" class="avatar-image" />
              <div v-else class="avatar-placeholder">
                <el-icon class="avatar-icon"><Plus /></el-icon>
              </div>
            </el-upload>
            <el-button type="default" size="small" class="avatar-button" @click="triggerUpload">
              <el-icon><Upload /></el-icon>
              上传头像
            </el-button>
            <p class="upload-tip">支持 JPG、PNG，建议尺寸 100×100px，大小不超过 2MB</p>
          </div>
        </el-card>

        <!-- 账户信息 -->
        <el-card class="setting-card margin-top" shadow="never">
          <template #header>
            <h3>账户信息</h3>
          </template>
          <div class="account-info">
            <div class="info-item">
              <span class="label">用户类型:</span>
              <span class="value">{{
                userData.user_type === 'student' ? '学生' : '企业用户'
              }}</span>
            </div>
            <div class="info-item">
              <span class="label">账户状态:</span>
              <span class="value" :style="{ color: userData.is_active ? '#22c55e' : '#ef4444' }">
                {{ userData.is_active ? '已激活' : '未激活' }}
              </span>
            </div>
            <div class="info-item">
              <span class="label">注册时间:</span>
              <span class="value">{{
                userData.date_joined ? new Date(userData.date_joined).toLocaleString() : '未知'
              }}</span>
            </div>
            <div class="info-item">
              <span class="label">最后登录:</span>
              <span class="value">{{
                userData.last_login ? new Date(userData.last_login).toLocaleString() : '从未登录'
              }}</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style lang="scss" scoped>
.user-profile {
  .setting-card {
    border: 1px solid #e4e7ed;

    :deep(.el-card__header) {
      background: #fafafa;
      border-bottom: 1px solid #e4e7ed;
      display: flex;
      align-items: center;
      justify-content: flex-start;

      .header-content {
        display: flex;
        width: 100%;
        align-items: center;

        h3 {
          margin: 0;
          font-size: 16px;
          font-weight: 600;
          color: #303133;
        }

        .header-actions {
          margin-left: auto;
          display: flex;
          align-items: center;
          gap: 8px;

          .status-badge {
            font-weight: 500;
            font-size: 14px;
            padding: 2px 8px;
            border-radius: 4px;
            background: #f3f4f6;
          }
        }
      }
    }

    &.avatar-card {
      text-align: center;

      .avatar-upload {
        padding: 20px 0;

        .avatar-uploader {
          :deep(.el-upload) {
            border-radius: 8px;
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transition: border-color 0.3s;
          }
        }

        .avatar-image {
          width: 100px;
          height: 100px;
          border-radius: 8px;
          object-fit: cover;
          display: block;
          margin: 0 auto;
        }

        .avatar-placeholder {
          width: 100px;
          height: 100px;
          border: 2px dashed #dcdfe6;
          border-radius: 8px;
          display: flex;
          align-items: center;
          justify-content: center;
          cursor: pointer;
          transition: border-color 0.3s;
          margin: 0 auto;

          &:hover {
            border-color: #409eff;
          }

          .avatar-icon {
            font-size: 24px;
            color: #8c939d;
          }
        }

        .avatar-button {
          margin-top: 15px;
        }
      }

      .upload-tip {
        font-size: 12px;
        color: #909399;
        margin-top: 8px;
        line-height: 1.4;
      }
    }

    &.margin-top {
      margin-top: 20px;
    }
  }

  .account-info {
    .info-item {
      display: flex;
      justify-content: space-between;
      padding: 8px 0;
      border-bottom: 1px solid #f0f0f0;

      &:last-child {
        border-bottom: none;
      }

      .label {
        color: #666;
        font-size: 14px;
      }

      .value {
        color: #333;
        font-size: 14px;
        font-weight: 500;
      }
    }
  }
}

@media (max-width: 1200px) {
  .user-profile .avatar-col {
    order: -1;
    margin-bottom: 20px;
  }
}
</style>
