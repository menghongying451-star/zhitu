<script setup>
import { ref, computed, reactive, onMounted, watch, nextTick } from 'vue'
import { authService, enterpriseInfoService } from '@/api'
import { useUserStore } from '@/stores'
import { useAuthStore } from '@/stores'
import { useRouter, useRoute } from 'vue-router'
import { debounce } from 'lodash-es'
import ParticleBackground from '@/components/ParticleBackground.vue'

// 导入 Element Plus 图标
import {
  User,
  Lock,
  Message,
  View,
  Hide,
  Key,
  School,
  OfficeBuilding,
  Reading,
  Promotion,
  Calendar,
  Suitcase,
  Check,
  ArrowRight,
  CircleCheck,
  CircleClose,
  Search,
  Loading,
  ArrowLeft
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const authStore = useAuthStore()

// 表单状态切换
const isLoginForm = ref(true)

// 用户类型切换
const userType = ref('student') // 'student' 或 'organization'

// 忘记密码状态
const isForgotPasswordForm = ref(false)

// 监听路由参数变化，自动切换到注册表单和用户类型
watch(
  () => route.query,
  (newQuery) => {
    // 处理 mode 参数（登录/注册）
    if (newQuery.mode === 'register') {
      isLoginForm.value = false
    }

    // 处理 userType 参数（用户类型）
    if (newQuery.userType === 'student' || newQuery.userType === 'organization') {
      userType.value = newQuery.userType
      if (newQuery.mode !== 'register') {
        showRegisterForm()
      }
    }
  },
  { immediate: true, deep: true }
)

const showLoginForm = () => {
  isLoginForm.value = true
  isForgotPasswordForm.value = false
  errorMessage.value = ''
  successMessage.value = ''
  clearFormErrors()
  passwordStrength.showIndicator = false
  passwordStrength.score = 0
  passwordStrength.level = ''
  passwordStrength.color = ''
}
const showRegisterForm = () => {
  isLoginForm.value = false
  isForgotPasswordForm.value = false
  errorMessage.value = ''
  successMessage.value = ''
  clearFormErrors()

  // 切换到注册表单时，重新计算密码强度
  const currentPassword =
    userType.value === 'student' ? studentForm.value.password : organizationForm.value.password
  if (currentPassword) {
    calculatePasswordStrength(currentPassword)
  } else {
    passwordStrength.showIndicator = false
    passwordStrength.score = 0
    passwordStrength.level = ''
    passwordStrength.color = ''
  }
}
const showForgotPasswordForm = () => {
  isLoginForm.value = false
  isForgotPasswordForm.value = true
  errorMessage.value = ''
  successMessage.value = ''
  clearFormErrors()
  // 重置忘记密码表单
  forgotPasswordForm.value = {
    email: '',
    email_code: '',
    new_password: '',
    confirm_password: ''
  }
}

// 登录方式
const loginMethod = ref('password') // 'password' 或 'email-verification'

// 登录表单数据
const loginForm = ref({
  username_or_email_or_phone: '',
  password: '',
  email: '',
  verification_code: ''
})

// 忘记密码表单数据
const forgotPasswordForm = ref({
  email: '',
  email_code: '',
  new_password: '',
  confirm_password: ''
})

// 记住我
const rememberMe = ref(false)
onMounted(() => {
  // 页面加载时自动滚动到顶部
  window.scrollTo({
    top: 0
  })

  if (authStore.rememberme && authStore.logindata) {
    loginForm.value.username_or_email_or_phone =
      authStore.logindata.username_or_email_or_phone || ''
    loginForm.value.password = authStore.logindata.password || ''
    loginForm.value.email = authStore.logindata.email || ''
    loginMethod.value = authStore.logindata.type || 'password'
  }
  rememberMe.value = authStore.rememberme
})

// 学生注册表单数据
const studentForm = ref({
  user_type: 'student',
  username: '',
  password: '',
  confirm_password: '',
  email: '',
  email_code: '',
  student_id: '',
  school: '',
  school_id: null, // 添加学校ID字段
  major: '',
  education: '',
  grade: ''
})

// 企业/机构注册表单数据
const organizationForm = ref({
  user_type: 'organization',
  username: '',
  password: '',
  confirm_password: '',
  email: '',
  email_code: '',
  registration_choice: 'existing', // 'existing' 或 'new'
  // 加入现有机构
  organization_id: null,
  position: '',
  department: '', // 新增：部门字段
  // 创建新机构
  organization_name: '',
  organization_type: 'enterprise', // 'enterprise' 或 "university" 或 'other'
  industry_or_discipline: ''
})

// 密码强度评估
const passwordStrength = reactive({
  score: 0,
  level: '',
  color: '',
  showIndicator: false
})

// 表单验证错误信息
const formErrors = reactive({
  // 通用字段
  username: '',
  email: '',
  password: '',
  confirm_password: '',
  email_code: '',

  // 登录字段
  username_or_email_or_phone: '',
  verification_code: '',

  // 忘记密码字段
  forgot_password_email: '',
  forgot_password_code: '',
  forgot_password_new: '',
  forgot_password_confirm: '',

  // 学生字段
  student_id: '',
  school: '',
  major: '',
  education: '',
  grade: '',

  // 企业字段
  position: '',
  department: '',
  organization_search: '',
  organization_name: '',
  organization_type: '',
  industry_or_discipline: ''
})

// 密码强度计算函数
const calculatePasswordStrength = (password) => {
  if (!password) {
    passwordStrength.score = 0
    passwordStrength.level = ''
    passwordStrength.showIndicator = false
    return
  }

  passwordStrength.showIndicator = true
  let score = 0

  // 长度评分
  if (password.length >= 8) score += 1
  if (password.length >= 10) score += 1
  if (password.length >= 12) score += 1

  // 字符类型评分
  if (/[a-z]/.test(password)) score += 1 // 小写字母
  if (/[A-Z]/.test(password)) score += 1 // 大写字母
  if (/\d/.test(password)) score += 1 // 数字
  if (/[^a-zA-Z0-9]/.test(password)) score += 1 // 特殊字符

  passwordStrength.score = score

  // 强度等级划分
  if (score <= 2) {
    passwordStrength.level = '很弱'
    passwordStrength.color = '#ef4444'
  } else if (score <= 3) {
    passwordStrength.level = '弱'
    passwordStrength.color = '#f59e0b'
  } else if (score <= 4) {
    passwordStrength.level = '中等'
    passwordStrength.color = '#3b82f6'
  } else if (score <= 5) {
    passwordStrength.level = '强'
    passwordStrength.color = '#10b981'
  } else {
    passwordStrength.level = '很强'
    passwordStrength.color = '#059669'
  }
}

// 表单验证函数
const validateField = (field, value, rules) => {
  for (const rule of rules) {
    if (!rule.validator(value)) {
      formErrors[field] = rule.message
      return false
    }
  }
  formErrors[field] = ''
  return true
}

// 清除表单错误
const clearFormErrors = () => {
  Object.keys(formErrors).forEach((key) => {
    formErrors[key] = ''
  })
}

// 验证规则定义
const validationRules = {
  username: [
    { validator: (v) => v && v.length >= 3, message: '用户名至少3个字符' },
    {
      validator: (v) => /^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(v),
      message: '用户名只能包含字母、数字、下划线和中文'
    }
  ],
  email: [
    { validator: (v) => v && v.length > 0, message: '请输入邮箱地址' },
    { validator: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v), message: '请输入有效的邮箱地址' }
  ],
  password: [
    { validator: (v) => v && v.length >= 8, message: '密码至少8个字符' },
    { validator: (v) => /[a-zA-Z]/.test(v), message: '密码必须包含字母' },
    { validator: (v) => /\d/.test(v), message: '密码必须包含数字' }
  ],
  confirm_password: [{ validator: (v) => v && v.length > 0, message: '请确认密码' }],
  email_code: [
    { validator: (v) => v && v.length > 0, message: '请输入验证码' },
    { validator: (v) => /^\d{6}$/.test(v), message: '验证码格式不正确' }
  ],
  username_or_email_or_phone: [
    { validator: (v) => v && v.length > 0, message: '请输入用户名、邮箱或手机号' }
  ],
  verification_code: [
    { validator: (v) => v && v.length > 0, message: '请输入验证码' },
    { validator: (v) => /^\d{6}$/.test(v), message: '验证码格式不正确' }
  ],
  // 忘记密码表单验证规则
  forgot_password_email: [
    { validator: (v) => v && v.length > 0, message: '请输入邮箱地址' },
    { validator: (v) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v), message: '请输入有效的邮箱地址' }
  ],
  forgot_password_code: [
    { validator: (v) => v && v.length > 0, message: '请输入验证码' },
    { validator: (v) => /^\d{6}$/.test(v), message: '验证码格式不正确' }
  ],
  forgot_password_new: [
    { validator: (v) => v && v.length >= 8, message: '密码至少8个字符' },
    { validator: (v) => /[a-zA-Z]/.test(v), message: '密码必须包含字母' },
    { validator: (v) => /\d/.test(v), message: '密码必须包含数字' }
  ],
  forgot_password_confirm: [{ validator: (v) => v && v.length > 0, message: '请确认密码' }],
  student_id: [
    { validator: (v) => v && v.length > 0, message: '请输入学号' },
    { validator: (v) => /^[a-zA-Z0-9]+$/.test(v), message: '学号格式不正确' }
  ],
  school: [
    {
      validator: (v) => studentForm.value.school_id && studentForm.value.school_id > 0,
      message: '请选择学校'
    }
  ],
  major: [{ validator: (v) => v && v.length > 0, message: '请输入专业' }],
  education: [{ validator: (v) => v && v.length > 0, message: '请选择学历' }],
  grade: [
    { validator: (v) => v && v > 0, message: '请输入入学年份' },
    { validator: (v) => v >= 2000 && v <= new Date().getFullYear(), message: '入学年份不正确' }
  ],
  position: [{ validator: (v) => v && v.length > 0, message: '请输入职位' }],
  department: [{ validator: (v) => v && v.length > 0, message: '请输入部门' }],
  organization_search: [
    {
      validator: (v) =>
        organizationForm.value.registration_choice !== 'existing' ||
        (v && organizationForm.value.organization_id),
      message: '请选择企业/机构'
    }
  ],
  organization_name: [
    {
      validator: (v) => organizationForm.value.registration_choice !== 'new' || (v && v.length > 0),
      message: '请输入企业/机构名称'
    }
  ],
  organization_type: [
    {
      validator: (v) => organizationForm.value.registration_choice !== 'new' || (v && v.length > 0),
      message: '请选择组织类型'
    }
  ],
  industry_or_discipline: [
    {
      validator: (v) => organizationForm.value.registration_choice !== 'new' || (v && v.length > 0),
      message: '请输入所属行业/领域'
    }
  ]
}

// 机构列表相关
const organizationList = ref([])
const organizationSearch = ref('')
const organizationLoading = ref(false)
const showOrganizationDropdown = ref(false)
const organizationTypeFilter = ref('')

// 学校列表相关
const schoolList = ref([])
const schoolSearch = ref('')
const schoolLoading = ref(false)
const showSchoolDropdown = ref(false)

// 获取机构列表
const searchOrganizations = debounce(async (search = '') => {
  // 只有搜索内容非空时才执行搜索
  if (!search || !search.trim()) {
    organizationList.value = []
    showOrganizationDropdown.value = false
    return
  }

  try {
    organizationLoading.value = true
    const response = await enterpriseInfoService.searchOrganizations({
      search: search.trim(),
      organization_type: organizationTypeFilter.value,
      page: '1',
      page_size: '10'
    })
    organizationList.value = response.data.results || []
    showOrganizationDropdown.value = (response.data.results || []).length > 0
  } catch (error) {
    console.error('获取机构列表失败:', error)
    organizationList.value = []
    showOrganizationDropdown.value = false
  } finally {
    organizationLoading.value = false
  }
}, 300)

// 获取学校列表
const searchSchools = debounce(async (search = '') => {
  // 只有搜索内容非空时才执行搜索
  if (!search || !search.trim()) {
    schoolList.value = []
    showSchoolDropdown.value = false
    return
  }

  try {
    schoolLoading.value = true
    const response = await enterpriseInfoService.searchUniversities({
      search: search.trim(),
      page: '1',
      page_size: '10'
    })
    schoolList.value = response.data.universities || []
    showSchoolDropdown.value = (response.data.universities || []).length > 0
  } catch (error) {
    console.error('获取学校列表失败:', error)
    schoolList.value = []
    showSchoolDropdown.value = false
  } finally {
    schoolLoading.value = false
  }
}, 300)

// 选择机构
const selectOrganization = (org) => {
  organizationForm.value.organization_id = org.id
  organizationSearch.value = org.name
  showOrganizationDropdown.value = false
  formErrors.organization_search = ''
}

// 选择学校
const selectSchool = (school) => {
  studentForm.value.school_id = school.id
  studentForm.value.school = school.school
  schoolSearch.value = school.school
  showSchoolDropdown.value = false
  formErrors.school = ''
}

// 搜索机构
const handleOrganizationSearch = (value) => {
  organizationSearch.value = value
  if (value && value.trim()) {
    searchOrganizations(value)
  } else {
    showOrganizationDropdown.value = false
    organizationList.value = []
    organizationForm.value.organization_id = null
  }
}

// 搜索学校
const handleSchoolSearch = (value) => {
  schoolSearch.value = value
  if (value && value.trim()) {
    searchSchools(value)
  } else {
    showSchoolDropdown.value = false
    schoolList.value = []
    studentForm.value.school_id = null
    studentForm.value.school = ''
  }
}

// 处理组织类型筛选变化
const handleOrganizationTypeChange = () => {
  // 如果当前有搜索内容，重新搜索
  if (organizationSearch.value && organizationSearch.value.trim()) {
    searchOrganizations(organizationSearch.value)
  }
}

// 密码可见性切换
const showLoginPassword = ref(false)
const showRegisterPassword = ref(false)

// 表单验证
const isStudentFormValid = computed(() => {
  const passwordsMatch = studentForm.value.password === studentForm.value.confirm_password

  return (
    studentForm.value.username &&
    studentForm.value.password &&
    passwordStrength.score >= 3 && // 密码强度至少为"弱"
    studentForm.value.confirm_password &&
    passwordsMatch &&
    studentForm.value.email &&
    studentForm.value.email_code &&
    studentForm.value.student_id &&
    studentForm.value.school &&
    studentForm.value.major
  )
})

const isOrganizationFormValid = computed(() => {
  const passwordsMatch = organizationForm.value.password === organizationForm.value.confirm_password

  const baseValid =
    organizationForm.value.username &&
    organizationForm.value.password &&
    passwordStrength.score >= 3 && // 密码强度至少为"弱"
    organizationForm.value.confirm_password &&
    passwordsMatch &&
    organizationForm.value.email &&
    organizationForm.value.email_code &&
    organizationForm.value.position &&
    organizationForm.value.department

  if (organizationForm.value.registration_choice === 'existing') {
    return baseValid && organizationForm.value.organization_id
  } else {
    return (
      baseValid &&
      organizationForm.value.organization_name &&
      organizationForm.value.industry_or_discipline
    )
  }
})

// 错误和成功信息
const errorMessage = ref('')
const successMessage = ref('')

// 验证码状态
const verificationStatus = reactive({
  sending: false,
  sent: false,
  countdown: 60
})

// 发送验证码
const sendVerificationCode = async (type = 'register') => {
  if (verificationStatus.sending || verificationStatus.sent) return

  let email = ''
  switch (type) {
    case 'register':
      email = userType.value === 'student' ? studentForm.value.email : organizationForm.value.email
      break
    case 'login':
      email = loginForm.value.email
      break
    default:
      break
  }

  if (!email) {
    showErrorToast('请先输入邮箱地址')
    return
  }

  try {
    verificationStatus.sending = true
    await authService.sendEmailVerification({
      email,
      code_type: type
    })

    verificationStatus.sent = true
    showSuccessToast('验证码已发送到您的邮箱')

    verificationStatus.countdown = 60
    const timer = setInterval(() => {
      verificationStatus.countdown--
      if (verificationStatus.countdown <= 0) {
        clearInterval(timer)
        verificationStatus.sent = false
      }
    }, 1000)
  } catch (error) {
    showErrorToast(error.detail || '发送验证码失败，请稍后重试')
    console.error(error)
  } finally {
    verificationStatus.sending = false
  }
}

// 提示弹窗显示
const successToast = ref(false)
const errorToast = ref(false)

const showSuccessToast = (message) => {
  successMessage.value = message
  successToast.value = true
  setTimeout(() => {
    successToast.value = false
  }, 3000)
}

const showErrorToast = (message) => {
  errorMessage.value = message
  errorToast.value = true
  setTimeout(() => {
    errorToast.value = false
  }, 3000)
}

// 处理登录
// 登录和注册的加载状态
const isLoggingIn = ref(false)
const isRegistering = ref(false)

const handleLogin = async () => {
  try {
    errorMessage.value = ''
    isLoggingIn.value = true
    const credentials = ref({})
    let response = {}

    if (loginMethod.value === 'email-verification') {
      if (!loginForm.value.verification_code) {
        showErrorToast('请输入验证码')
        return
      }
      credentials.value = {
        type: 'email-verification',
        email: loginForm.value.email,
        email_code: loginForm.value.verification_code
      }
      response = await authService.login(credentials.value)
    } else {
      if (!loginForm.value.password) {
        showErrorToast('请输入密码')
        return
      }
      credentials.value = {
        type: 'password',
        username_or_email_or_phone: loginForm.value.username_or_email_or_phone,
        password: loginForm.value.password
      }
      response = await authService.login(credentials.value)
    }

    authStore.setToken(response.data.auth.access)
    authStore.setRefreshToken(response.data.auth.refresh)
    userStore.setUser({ ...response.data.user })

    if (rememberMe.value) {
      authStore.setlogindata(credentials.value)
    } else {
      authStore.removelogindata()
    }
    authStore.setRememberme(rememberMe.value)

    if (response.data.user.user_type === 'student') {
      router.push('/student')
    } else if (response.data.user.user_type === 'organization') {
      router.push('/enterprise')
    } else {
      router.push('/home')
    }
  } catch (error) {
    showErrorToast(error.detail || '登录失败，请检查用户名和密码。')
    console.error(error)
  } finally {
    isLoggingIn.value = false
  }
}

// 执行注册
const executeRegister = async () => {
  try {
    errorMessage.value = ''
    isRegistering.value = true
    let userData = {}

    if (userType.value === 'student') {
      if (studentForm.value.password !== studentForm.value.confirm_password) {
        showErrorToast('两次输入的密码不一致')
        return
      }

      userData = {
        user_type: 'student',
        username: studentForm.value.username,
        password: studentForm.value.password,
        confirm_password: studentForm.value.confirm_password,
        email: studentForm.value.email,
        email_code: studentForm.value.email_code,
        student_id: studentForm.value.student_id,
        school_id: studentForm.value.school_id, // 使用学校ID而不是学校名称
        major: studentForm.value.major,
        education: studentForm.value.education,
        grade: studentForm.value.grade
      }
    } else {
      if (organizationForm.value.password !== organizationForm.value.confirm_password) {
        showErrorToast('两次输入的密码不一致')
        return
      }

      userData = {
        user_type: 'organization',
        username: organizationForm.value.username,
        password: organizationForm.value.password,
        confirm_password: organizationForm.value.confirm_password,
        email: organizationForm.value.email,
        email_code: organizationForm.value.email_code,
        registration_choice: organizationForm.value.registration_choice,
        position: organizationForm.value.position,
        department: organizationForm.value.department // 新增：部门字段
      }

      if (organizationForm.value.registration_choice === 'existing') {
        userData.organization_id = parseInt(organizationForm.value.organization_id)
      } else {
        userData.organization_name = organizationForm.value.organization_name
        userData.organization_type = organizationForm.value.organization_type
        userData.industry_or_discipline = organizationForm.value.industry_or_discipline
      }
    }

    await authService.register(userData)
    showSuccessToast('注册成功，请登录')
    setTimeout(() => {
      showLoginForm()
    }, 2000)
  } catch (error) {
    showErrorToast(error.detail || '注册失败，请检查您的输入信息。')
    console.error(error)
  } finally {
    isRegistering.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  await executeRegister()
}

// 发送忘记密码验证码
const sendForgotPasswordCode = async () => {
  if (!forgotPasswordForm.value.email) {
    showErrorToast('请先输入邮箱地址')
    return
  }

  try {
    verificationStatus.sending = true
    await authService.sendEmailVerification({
      email: forgotPasswordForm.value.email,
      code_type: 'reset_password'
    })

    verificationStatus.sent = true
    showSuccessToast('验证码已发送到您的邮箱')

    verificationStatus.countdown = 60
    const timer = setInterval(() => {
      verificationStatus.countdown--
      if (verificationStatus.countdown <= 0) {
        clearInterval(timer)
        verificationStatus.sent = false
      }
    }, 1000)
  } catch (error) {
    showErrorToast(error.detail || '发送验证码失败，请稍后重试')
    console.error(error)
  } finally {
    verificationStatus.sending = false
  }
}

// 处理忘记密码
const handleForgotPassword = async () => {
  try {
    errorMessage.value = ''

    if (!forgotPasswordForm.value.email) {
      showErrorToast('请输入邮箱地址')
      return
    }

    if (!forgotPasswordForm.value.email_code) {
      showErrorToast('请输入验证码')
      return
    }

    if (!forgotPasswordForm.value.new_password) {
      showErrorToast('请输入新密码')
      return
    }

    if (forgotPasswordForm.value.new_password !== forgotPasswordForm.value.confirm_password) {
      showErrorToast('两次输入的密码不一致')
      return
    }

    const response = await authService.forgetPassword({
      email: forgotPasswordForm.value.email,
      email_code: forgotPasswordForm.value.email_code,
      new_password: forgotPasswordForm.value.new_password,
      confirm_password: forgotPasswordForm.value.confirm_password
    })

    showSuccessToast('密码重置成功，请使用新密码登录')
    setTimeout(() => {
      showLoginForm()
    }, 2000)
  } catch (error) {
    showErrorToast(error.detail || '重置密码失败，请检查您的输入信息。')
    console.error(error)
  }
}

// 注册通用字段计算属性
const username = computed({
  get: () =>
    userType.value === 'student' ? studentForm.value.username : organizationForm.value.username,
  set: (val) => {
    if (userType.value === 'student') {
      studentForm.value.username = val
    } else {
      organizationForm.value.username = val
    }
  }
})

const password = computed({
  get: () =>
    userType.value === 'student' ? studentForm.value.password : organizationForm.value.password,
  set: (val) => {
    if (userType.value === 'student') {
      studentForm.value.password = val
    } else {
      organizationForm.value.password = val
    }
    // 计算密码强度
    calculatePasswordStrength(val)
  }
})

const confirm_password = computed({
  get: () =>
    userType.value === 'student'
      ? studentForm.value.confirm_password
      : organizationForm.value.confirm_password,
  set: (val) => {
    if (userType.value === 'student') {
      studentForm.value.confirm_password = val
    } else {
      organizationForm.value.confirm_password = val
    }
  }
})

const email = computed({
  get: () =>
    userType.value === 'student' ? studentForm.value.email : organizationForm.value.email,
  set: (val) => {
    if (userType.value === 'student') {
      studentForm.value.email = val
    } else {
      organizationForm.value.email = val
    }
  }
})

const email_code = computed({
  get: () =>
    userType.value === 'student' ? studentForm.value.email_code : organizationForm.value.email_code,
  set: (val) => {
    if (userType.value === 'student') {
      studentForm.value.email_code = val
    } else {
      organizationForm.value.email_code = val
    }
  }
})

// 验证确认密码的规则需要动态更新
const validateConfirmPassword = () => {
  const currentPassword =
    userType.value === 'student' ? studentForm.value.password : organizationForm.value.password
  const currentConfirmPassword =
    userType.value === 'student'
      ? studentForm.value.confirm_password
      : organizationForm.value.confirm_password

  if (!currentConfirmPassword) {
    formErrors.confirm_password = '请确认密码'
    return false
  }

  if (currentConfirmPassword !== currentPassword) {
    formErrors.confirm_password = '两次输入的密码不一致'
    return false
  }

  formErrors.confirm_password = ''
  return true
}

// 监听密码变化，处理确认密码验证
watch(
  [
    () =>
      userType.value === 'student' ? studentForm.value.password : organizationForm.value.password,
    () =>
      userType.value === 'student'
        ? studentForm.value.confirm_password
        : organizationForm.value.confirm_password
  ],
  ([newPassword, newConfirmPassword]) => {
    // 只有当确认密码不为空时才进行验证
    if (newConfirmPassword) {
      if (newPassword !== newConfirmPassword) {
        formErrors.confirm_password = '两次输入的密码不一致'
      } else {
        // 清除密码不一致的错误（保留其他可能的错误）
        if (formErrors.confirm_password === '两次输入的密码不一致') {
          formErrors.confirm_password = ''
        }
      }
    }
  }
)

// 监听表单模式切换，确保密码强度正确计算
watch(isLoginForm, (newIsLogin) => {
  if (!newIsLogin) {
    // 切换到注册表单
    // 延迟执行，确保DOM更新完成
    nextTick(() => {
      const currentPassword =
        userType.value === 'student' ? studentForm.value.password : organizationForm.value.password
      if (currentPassword) {
        calculatePasswordStrength(currentPassword)
      }
    })
  }
})

// 监听用户类型变化，重置相关数据
watch(userType, (newType) => {
  clearFormErrors()

  if (newType === 'organization') {
    // 重置机构相关数据
    organizationForm.value.registration_choice = 'existing'
    organizationForm.value.organization_id = null
    organizationSearch.value = ''
    organizationList.value = []
    showOrganizationDropdown.value = false
  } else {
    // 重置学校相关数据
    studentForm.value.school_id = null
    studentForm.value.school = ''
    schoolSearch.value = ''
    schoolList.value = []
    showSchoolDropdown.value = false
  }

  // 重新计算当前密码强度
  const currentPassword =
    newType === 'student' ? studentForm.value.password : organizationForm.value.password
  if (currentPassword) {
    calculatePasswordStrength(currentPassword)
  } else {
    passwordStrength.showIndicator = false
    passwordStrength.score = 0
    passwordStrength.level = ''
    passwordStrength.color = ''
  }
})

// 监听注册选择变化
watch(
  () => organizationForm.value.registration_choice,
  (newChoice) => {
    if (newChoice === 'existing') {
      // 重置创建新机构的字段
      organizationForm.value.organization_name = ''
      organizationForm.value.industry_or_discipline = ''
      formErrors.organization_name = ''
      formErrors.industry_or_discipline = ''
    } else {
      // 重置选择现有机构的字段
      organizationForm.value.organization_id = null
      organizationSearch.value = ''
      organizationTypeFilter.value = ''
      organizationList.value = []
      showOrganizationDropdown.value = false
      formErrors.organization_search = ''
    }
  }
)
</script>

<template>
  <div class="page-container">
    <!-- 悬浮返回首页按钮（新） -->
    <div class="home-float-btn-wrap">
      <router-link to="/home" class="home-float-btn" aria-label="返回首页">
        <el-icon class="home-float-icon"><ArrowLeft /></el-icon>
        <span class="home-float-text">返回首页</span>
      </router-link>
    </div>
    <!-- 添加粒子背景 -->
    <ParticleBackground v-if="ParticleBackground" />

    <!-- 页面容器 -->
    <div class="main-content">
      <!-- 左侧品牌展示区 -->
      <div class="brand-section">
        <!-- 装饰图形 -->
        <div class="decoration-circle decoration-circle--top"></div>
        <div class="decoration-circle decoration-circle--bottom"></div>

        <!-- 品牌标志 -->
        <div class="brand-header">
          <div class="brand-logo">
            <div class="logo-icon">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <h1 class="brand-title">智汇</h1>
          </div>
          <p class="brand-subtitle">连接产业需求，培育创新人才，共创校企合作新未来</p>
        </div>

        <!-- 主要内容 -->
        <div class="brand-content">
          <h2 class="brand-headline">赋能教育<br />驱动创新</h2>
          <p class="brand-description">
            智汇平台是实践育人、培养创新人才的重要平台，构建四区融合的协同育人体系，促进人才培养与产业发展的深度融合。
          </p>

          <!-- 合作优势 -->
          <div class="features-list">
            <div class="feature-item">
              <div class="feature-icon">
                <el-icon><School /></el-icon>
              </div>
              <div class="feature-content">
                <h3 class="feature-title">实践育人平台</h3>
                <p class="feature-description">打造培养创新人才的实践平台，实现产教深度融合</p>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon">
                <el-icon><OfficeBuilding /></el-icon>
              </div>
              <div class="feature-content">
                <h3 class="feature-title">四区融合模式</h3>
                <p class="feature-description">
                  整合校区、园区、社区、城区资源，构建协同育人生态体系
                </p>
              </div>
            </div>

            <div class="feature-item">
              <div class="feature-icon">
                <el-icon><Promotion /></el-icon>
              </div>
              <div class="feature-content">
                <h3 class="feature-title">人才培养体系</h3>
                <p class="feature-description">
                  通过校企合作项目，培养符合产业需求的高素质创新型人才
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部信息 -->
        <div class="brand-footer">
          <p class="copyright">© 2025 智汇校企合作平台 版权所有</p>
        </div>
      </div>

      <!-- 右侧表单区域 -->
      <div class="form-section">
        <div class="form-container">
          <!-- 移动端品牌标志 -->
          <div class="mobile-brand">
            <div class="mobile-logo">
              <el-icon><OfficeBuilding /></el-icon>
            </div>
            <h1 class="mobile-title">智汇</h1>
          </div>

          <!-- 表单切换器 -->
          <div class="form-tabs" v-if="!isForgotPasswordForm">
            <button
              @click="showLoginForm"
              :class="{ 'form-tab--active': isLoginForm }"
              class="form-tab"
            >
              登录
            </button>
            <button
              @click="showRegisterForm"
              :class="{ 'form-tab--active': !isLoginForm }"
              class="form-tab"
            >
              注册
            </button>
          </div>

          <!-- 登录表单 -->
          <div v-if="isLoginForm && !isForgotPasswordForm" class="form-content">
            <h2 class="form-title">欢迎回来</h2>
            <p class="form-subtitle">请输入您的账号信息登录智汇平台</p>

            <form @submit.prevent="handleLogin" class="auth-form">
              <!-- 密码登录 -->
              <template v-if="loginMethod === 'password'">
                <!-- 用户名/邮箱 -->
                <div class="form-group">
                  <label for="loginUsername" class="form-label">用户名/邮箱/手机号</label>
                  <div class="input-wrapper">
                    <div class="input-icon">
                      <el-icon><User /></el-icon>
                    </div>
                    <input
                      type="text"
                      id="loginUsername"
                      v-model="loginForm.username_or_email_or_phone"
                      @blur="
                        validateField(
                          'username_or_email_or_phone',
                          loginForm.username_or_email_or_phone,
                          validationRules.username_or_email_or_phone
                        )
                      "
                      class="form-input"
                      :class="{ 'form-input--error': formErrors.username_or_email_or_phone }"
                      placeholder="请输入用户名、邮箱或手机号"
                      required
                    />
                  </div>
                  <div v-if="formErrors.username_or_email_or_phone" class="field-error">
                    {{ formErrors.username_or_email_or_phone }}
                  </div>
                </div>

                <!-- 密码 -->
                <div class="form-group">
                  <div class="form-label-row">
                    <label for="loginPassword" class="form-label">密码</label>
                  </div>
                  <div class="input-wrapper">
                    <div class="input-icon">
                      <el-icon><Lock /></el-icon>
                    </div>
                    <input
                      :type="showLoginPassword ? 'text' : 'password'"
                      id="loginPassword"
                      v-model="loginForm.password"
                      class="form-input form-input--with-action"
                      placeholder="请输入密码"
                      required
                      autocomplete="current-password"
                    />
                    <button
                      type="button"
                      @click="showLoginPassword = !showLoginPassword"
                      class="input-action"
                    >
                      <el-icon>
                        <View v-if="showLoginPassword" />
                        <Hide v-else />
                      </el-icon>
                    </button>
                  </div>
                </div>

                <div class="form-link-row">
                  <a
                    href="#"
                    @click.prevent="showForgotPasswordForm"
                    class="form-link form-link--left"
                  >
                    忘记密码？
                  </a>
                  <a
                    href="#"
                    @click.prevent="loginMethod = 'email-verification'"
                    class="form-link form-link--right"
                  >
                    验证码登录
                  </a>
                </div>
              </template>

              <!-- 验证码登录 -->
              <template v-else>
                <!-- 邮箱 -->
                <div class="form-group">
                  <label for="loginEmail" class="form-label">邮箱</label>
                  <div class="input-wrapper">
                    <div class="input-icon">
                      <el-icon><Message /></el-icon>
                    </div>
                    <input
                      type="email"
                      id="loginEmail"
                      v-model="loginForm.email"
                      @blur="validateField('email', loginForm.email, validationRules.email)"
                      class="form-input"
                      :class="{ 'form-input--error': formErrors.email }"
                      placeholder="请输入邮箱"
                      required
                    />
                  </div>
                  <div v-if="formErrors.email" class="field-error">
                    {{ formErrors.email }}
                  </div>
                </div>

                <!-- 验证码 -->
                <div class="form-group">
                  <label for="loginVerificationCode" class="form-label">验证码</label>
                  <div class="verification-wrapper">
                    <div class="input-wrapper verification-input">
                      <div class="input-icon">
                        <el-icon><Key /></el-icon>
                      </div>
                      <input
                        type="text"
                        id="loginVerificationCode"
                        v-model="loginForm.verification_code"
                        @blur="
                          validateField(
                            'verification_code',
                            loginForm.verification_code,
                            validationRules.verification_code
                          )
                        "
                        class="form-input"
                        :class="{ 'form-input--error': formErrors.verification_code }"
                        placeholder="请输入验证码"
                        required
                      />
                    </div>
                    <button
                      type="button"
                      @click="sendVerificationCode('login')"
                      :disabled="verificationStatus.sending || verificationStatus.sent"
                      class="verification-btn"
                    >
                      {{
                        verificationStatus.sent
                          ? `${verificationStatus.countdown}秒后重发`
                          : '获取验证码'
                      }}
                    </button>
                  </div>
                  <div v-if="formErrors.verification_code" class="field-error">
                    {{ formErrors.verification_code }}
                  </div>
                </div>

                <div class="form-link-row" style="justify-content: flex-end">
                  <a
                    href="#"
                    @click.prevent="loginMethod = 'password'"
                    class="form-link form-link--right"
                  >
                    密码登录
                  </a>
                </div>
              </template>

              <!-- 记住我 -->
              <div class="checkbox-wrapper">
                <input id="rememberMe" v-model="rememberMe" type="checkbox" class="form-checkbox" />
                <label for="rememberMe" class="checkbox-label">记住我 30 天</label>
              </div>

              <!-- 登录按钮 -->
              <button type="submit" class="submit-btn" :disabled="isLoggingIn">
                <span>{{ isLoggingIn ? '登录中...' : '登录' }}</span>
                <el-icon v-if="!isLoggingIn"><ArrowRight /></el-icon>
                <el-icon v-else class="is-loading"><Loading /></el-icon>
              </button>
            </form>

            <!-- 注册提示 -->
            <p class="switch-form-text">
              还没有账号?
              <button @click="showRegisterForm" class="switch-form-link">立即注册</button>
            </p>
          </div>

          <!-- 忘记密码表单 -->
          <div v-if="isForgotPasswordForm" class="form-content">
            <h2 class="form-title">重置密码</h2>
            <p class="form-subtitle">请输入您的邮箱地址和新密码来重置密码</p>

            <form @submit.prevent="handleForgotPassword" class="auth-form">
              <!-- 邮箱 -->
              <div class="form-group">
                <label for="forgotEmail" class="form-label">邮箱</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <el-icon><Message /></el-icon>
                  </div>
                  <input
                    type="email"
                    id="forgotEmail"
                    v-model="forgotPasswordForm.email"
                    @blur="
                      validateField(
                        'forgot_password_email',
                        forgotPasswordForm.email,
                        validationRules.forgot_password_email
                      )
                    "
                    class="form-input"
                    :class="{ 'form-input--error': formErrors.forgot_password_email }"
                    placeholder="请输入邮箱"
                    required
                  />
                </div>
                <div v-if="formErrors.forgot_password_email" class="field-error">
                  {{ formErrors.forgot_password_email }}
                </div>
              </div>

              <!-- 验证码 -->
              <div class="form-group">
                <label for="forgotVerificationCode" class="form-label">验证码</label>
                <div class="verification-wrapper">
                  <div class="input-wrapper verification-input">
                    <div class="input-icon">
                      <el-icon><Key /></el-icon>
                    </div>
                    <input
                      type="text"
                      id="forgotVerificationCode"
                      v-model="forgotPasswordForm.email_code"
                      @blur="
                        validateField(
                          'forgot_password_code',
                          forgotPasswordForm.email_code,
                          validationRules.forgot_password_code
                        )
                      "
                      class="form-input"
                      :class="{ 'form-input--error': formErrors.forgot_password_code }"
                      placeholder="请输入验证码"
                      required
                    />
                  </div>
                  <button
                    type="button"
                    @click="sendForgotPasswordCode"
                    :disabled="verificationStatus.sending || verificationStatus.sent"
                    class="verification-btn"
                  >
                    {{
                      verificationStatus.sent
                        ? `${verificationStatus.countdown}秒后重发`
                        : '获取验证码'
                    }}
                  </button>
                </div>
                <div v-if="formErrors.forgot_password_code" class="field-error">
                  {{ formErrors.forgot_password_code }}
                </div>
              </div>

              <!-- 新密码 -->
              <div class="form-group">
                <label for="forgotNewPassword" class="form-label">新密码</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <el-icon><Lock /></el-icon>
                  </div>
                  <input
                    :type="showRegisterPassword ? 'text' : 'password'"
                    id="forgotNewPassword"
                    v-model="forgotPasswordForm.new_password"
                    @blur="
                      validateField(
                        'forgot_password_new',
                        forgotPasswordForm.new_password,
                        validationRules.forgot_password_new
                      )
                    "
                    class="form-input form-input--with-action"
                    :class="{ 'form-input--error': formErrors.forgot_password_new }"
                    placeholder="请输入新密码"
                    required
                  />
                  <button
                    type="button"
                    @click="showRegisterPassword = !showRegisterPassword"
                    class="input-action"
                  >
                    <el-icon>
                      <View v-if="showRegisterPassword" />
                      <Hide v-else />
                    </el-icon>
                  </button>
                </div>
                <div v-if="formErrors.forgot_password_new" class="field-error">
                  {{ formErrors.forgot_password_new }}
                </div>
              </div>

              <!-- 确认新密码 -->
              <div class="form-group">
                <label for="forgotConfirmPassword" class="form-label">确认新密码</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <el-icon><Lock /></el-icon>
                  </div>
                  <input
                    :type="showRegisterPassword ? 'text' : 'password'"
                    id="forgotConfirmPassword"
                    v-model="forgotPasswordForm.confirm_password"
                    @blur="
                      validateField(
                        'forgot_password_confirm',
                        forgotPasswordForm.confirm_password,
                        validationRules.forgot_password_confirm
                      )
                    "
                    class="form-input"
                    :class="{ 'form-input--error': formErrors.forgot_password_confirm }"
                    placeholder="请再次输入新密码"
                    required
                  />
                </div>
                <div v-if="formErrors.forgot_password_confirm" class="field-error">
                  {{ formErrors.forgot_password_confirm }}
                </div>
              </div>

              <!-- 重置密码按钮 -->
              <button type="submit" class="submit-btn">
                <span>重置密码</span>
              </button>
            </form>

            <!-- 返回登录提示 -->
            <p class="switch-form-text">
              想起密码了?
              <button @click="showLoginForm" class="switch-form-link">返回登录</button>
            </p>
          </div>

          <!-- 注册表单 -->
          <div v-else-if="!isLoginForm && !isForgotPasswordForm" class="form-content">
            <h2 class="form-title">创建账号</h2>
            <p class="form-subtitle">填写以下信息注册智汇平台账号，开启校企合作之旅</p>

            <form @submit.prevent="handleRegister" class="auth-form">
              <!-- 用户类型 -->
              <div class="form-group">
                <label class="form-label">用户类型</label>
                <div class="user-type-selector">
                  <label class="user-type-option">
                    <input
                      type="radio"
                      value="student"
                      v-model="userType"
                      class="user-type-radio"
                    />
                    <div class="user-type-card">
                      <div class="user-type-icon">
                        <el-icon><School /></el-icon>
                      </div>
                      <span class="user-type-label">高校学生用户</span>
                    </div>
                  </label>

                  <label class="user-type-option">
                    <input
                      type="radio"
                      value="organization"
                      v-model="userType"
                      class="user-type-radio"
                    />
                    <div class="user-type-card">
                      <div class="user-type-icon">
                        <el-icon><OfficeBuilding /></el-icon>
                      </div>
                      <span class="user-type-label">企业/机构用户</span>
                    </div>
                  </label>
                </div>
              </div>

              <!-- 用户名 -->
              <div class="form-group">
                <label for="registerUsername" class="form-label">用户名</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <el-icon><User /></el-icon>
                  </div>
                  <input
                    type="text"
                    id="registerUsername"
                    v-model="username"
                    @blur="validateField('username', username, validationRules.username)"
                    class="form-input"
                    :class="{ 'form-input--error': formErrors.username }"
                    placeholder="请设置用户名"
                    required
                  />
                </div>
                <div v-if="formErrors.username" class="field-error">
                  {{ formErrors.username }}
                </div>
              </div>

              <!-- 邮箱 -->
              <div class="form-group">
                <label for="registerEmail" class="form-label">邮箱</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <el-icon><Message /></el-icon>
                  </div>
                  <input
                    type="email"
                    id="registerEmail"
                    v-model="email"
                    @blur="validateField('email', email, validationRules.email)"
                    class="form-input"
                    :class="{ 'form-input--error': formErrors.email }"
                    placeholder="请输入邮箱地址"
                    required
                  />
                </div>
                <div v-if="formErrors.email" class="field-error">
                  {{ formErrors.email }}
                </div>
              </div>

              <!-- 密码 -->
              <div class="form-group">
                <label for="registerPassword" class="form-label">密码</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <el-icon><Lock /></el-icon>
                  </div>
                  <input
                    :type="showRegisterPassword ? 'text' : 'password'"
                    id="registerPassword"
                    v-model="password"
                    @blur="validateField('password', password, validationRules.password)"
                    class="form-input form-input--with-action"
                    :class="{ 'form-input--error': formErrors.password }"
                    placeholder="请设置密码（至少8位）"
                    required
                    minlength="8"
                    autocomplete="new-password"
                  />
                  <button
                    type="button"
                    @click="showRegisterPassword = !showRegisterPassword"
                    class="input-action"
                  >
                    <el-icon>
                      <View v-if="showRegisterPassword" />
                      <Hide v-else />
                    </el-icon>
                  </button>
                </div>

                <!-- 密码强度指示器 -->
                <div v-if="passwordStrength.showIndicator" class="password-strength">
                  <div class="strength-bar">
                    <div
                      class="strength-fill"
                      :style="{
                        width: `${(passwordStrength.score / 7) * 100}%`,
                        backgroundColor: passwordStrength.color
                      }"
                    ></div>
                  </div>
                  <span class="strength-text" :style="{ color: passwordStrength.color }">
                    密码强度：{{ passwordStrength.level }}
                  </span>
                </div>

                <div v-if="formErrors.password" class="field-error">
                  {{ formErrors.password }}
                </div>
              </div>

              <!-- 确认密码 -->
              <div class="form-group">
                <label for="confirmPassword" class="form-label">确认密码</label>
                <div class="input-wrapper">
                  <div class="input-icon">
                    <el-icon><Lock /></el-icon>
                  </div>
                  <input
                    type="password"
                    id="confirmPassword"
                    v-model="confirm_password"
                    @blur="validateConfirmPassword"
                    class="form-input"
                    :class="{ 'form-input--error': formErrors.confirm_password }"
                    placeholder="请再次输入密码"
                    required
                    autocomplete="new-password"
                  />
                </div>
                <div v-if="formErrors.confirm_password" class="field-error">
                  {{ formErrors.confirm_password }}
                </div>
              </div>

              <!-- 验证码 -->
              <div class="form-group">
                <label for="verifyCode" class="form-label">验证码</label>
                <div class="verification-wrapper">
                  <div class="input-wrapper verification-input">
                    <div class="input-icon">
                      <el-icon><Key /></el-icon>
                    </div>
                    <input
                      type="text"
                      id="verifyCode"
                      v-model="email_code"
                      @blur="validateField('email_code', email_code, validationRules.email_code)"
                      class="form-input"
                      :class="{ 'form-input--error': formErrors.email_code }"
                      placeholder="请输入验证码"
                      required
                    />
                  </div>
                  <button
                    type="button"
                    @click="sendVerificationCode('register')"
                    :disabled="verificationStatus.sending || verificationStatus.sent"
                    class="verification-btn"
                  >
                    {{
                      verificationStatus.sent
                        ? `${verificationStatus.countdown}秒后重发`
                        : '获取验证码'
                    }}
                  </button>
                </div>
                <div v-if="formErrors.email_code" class="field-error">
                  {{ formErrors.email_code }}
                </div>
              </div>

              <!-- 学生端特有字段 -->
              <template v-if="userType === 'student'">
                <div class="form-group">
                  <label for="studentId" class="form-label">学号</label>
                  <div class="input-wrapper">
                    <div class="input-icon">
                      <el-icon><User /></el-icon>
                    </div>
                    <input
                      type="text"
                      id="studentId"
                      v-model="studentForm.student_id"
                      @blur="
                        validateField(
                          'student_id',
                          studentForm.student_id,
                          validationRules.student_id
                        )
                      "
                      class="form-input"
                      :class="{ 'form-input--error': formErrors.student_id }"
                      placeholder="请输入学号"
                      required
                    />
                  </div>
                  <div v-if="formErrors.student_id" class="field-error">
                    {{ formErrors.student_id }}
                  </div>
                </div>

                <div class="form-group">
                  <label for="school" class="form-label">学校</label>
                  <div class="school-search-wrapper">
                    <div class="input-wrapper">
                      <div class="input-icon">
                        <el-icon><School /></el-icon>
                      </div>
                      <input
                        type="text"
                        id="school"
                        v-model="schoolSearch"
                        @input="handleSchoolSearch($event.target.value)"
                        @focus="showSchoolDropdown = schoolList.length > 0"
                        @blur="
                          validateField('school', studentForm.school_id, validationRules.school)
                        "
                        class="form-input"
                        :class="{ 'form-input--error': formErrors.school }"
                        placeholder="请输入学校名称进行搜索"
                        required
                      />
                    </div>

                    <!-- 搜索结果下拉框 -->
                    <div v-if="showSchoolDropdown && schoolList.length > 0" class="school-dropdown">
                      <div class="dropdown-header">
                        <span class="dropdown-title">搜索结果</span>
                        <button
                          type="button"
                          @click="showSchoolDropdown = false"
                          class="dropdown-close"
                        >
                          ×
                        </button>
                      </div>
                      <div class="dropdown-list">
                        <div
                          v-for="school in schoolList"
                          :key="school.id"
                          @click="selectSchool(school)"
                          class="school-item"
                        >
                          <div class="school-name">{{ school.school }}</div>
                        </div>
                      </div>
                    </div>

                    <!-- 加载状态 -->
                    <div v-if="schoolLoading" class="search-loading">搜索中...</div>
                  </div>
                  <div v-if="formErrors.school" class="field-error">
                    {{ formErrors.school }}
                  </div>
                </div>

                <div class="form-group">
                  <label for="major" class="form-label">专业</label>
                  <div class="input-wrapper">
                    <div class="input-icon">
                      <el-icon><Reading /></el-icon>
                    </div>
                    <input
                      type="text"
                      id="major"
                      v-model="studentForm.major"
                      @blur="validateField('major', studentForm.major, validationRules.major)"
                      class="form-input"
                      :class="{ 'form-input--error': formErrors.major }"
                      placeholder="请输入专业"
                      required
                    />
                  </div>
                  <div v-if="formErrors.major" class="field-error">
                    {{ formErrors.major }}
                  </div>
                </div>

                <div class="form-group">
                  <label for="education" class="form-label">学历</label>
                  <div class="input-wrapper">
                    <div class="input-icon">
                      <el-icon><Promotion /></el-icon>
                    </div>
                    <select
                      id="education"
                      v-model="studentForm.education"
                      @blur="
                        validateField('education', studentForm.education, validationRules.education)
                      "
                      class="form-select"
                      :class="{ 'form-select--error': formErrors.education }"
                      required
                    >
                      <option value="">请选择学历</option>
                      <option value="college">专科</option>
                      <option value="undergraduate">本科</option>
                      <option value="master">硕士</option>
                      <option value="doctor">博士</option>
                    </select>
                  </div>
                  <div v-if="formErrors.education" class="field-error">
                    {{ formErrors.education }}
                  </div>
                </div>

                <div class="form-group">
                  <label for="grade" class="form-label">入学年份</label>
                  <div class="input-wrapper">
                    <div class="input-icon">
                      <el-icon><Calendar /></el-icon>
                    </div>
                    <input
                      type="number"
                      id="grade"
                      v-model="studentForm.grade"
                      @blur="validateField('grade', studentForm.grade, validationRules.grade)"
                      class="form-input"
                      :class="{ 'form-input--error': formErrors.grade }"
                      placeholder="请输入入学年份"
                      min="2000"
                      :max="new Date().getFullYear()"
                      required
                    />
                  </div>
                  <div v-if="formErrors.grade" class="field-error">
                    {{ formErrors.grade }}
                  </div>
                </div>
              </template>

              <!-- 企业/机构端特有字段 -->
              <template v-else>
                <!-- 注册选择 -->
                <div class="form-group">
                  <label class="form-label">注册方式</label>
                  <div class="registration-choice">
                    <label class="choice-option">
                      <input
                        type="radio"
                        value="existing"
                        v-model="organizationForm.registration_choice"
                        class="choice-radio"
                      />
                      <div class="choice-card">
                        <span class="choice-label">加入企业/机构</span>
                      </div>
                    </label>
                    <label class="choice-option">
                      <input
                        type="radio"
                        value="new"
                        v-model="organizationForm.registration_choice"
                        class="choice-radio"
                      />
                      <div class="choice-card">
                        <span class="choice-label">创建企业/机构</span>
                      </div>
                    </label>
                  </div>
                </div>

                <!-- 职位 -->
                <div class="form-group">
                  <label for="position" class="form-label">职位</label>
                  <div class="input-wrapper">
                    <div class="input-icon">
                      <el-icon><Suitcase /></el-icon>
                    </div>
                    <input
                      type="text"
                      id="position"
                      v-model="organizationForm.position"
                      @blur="
                        validateField(
                          'position',
                          organizationForm.position,
                          validationRules.position
                        )
                      "
                      class="form-input"
                      :class="{ 'form-input--error': formErrors.position }"
                      placeholder="请输入您的职位"
                      required
                    />
                  </div>
                  <div v-if="formErrors.position" class="field-error">
                    {{ formErrors.position }}
                  </div>
                </div>

                <!-- 部门 -->
                <div class="form-group">
                  <label for="department" class="form-label">部门</label>
                  <div class="input-wrapper">
                    <div class="input-icon">
                      <el-icon><OfficeBuilding /></el-icon>
                    </div>
                    <input
                      type="text"
                      id="department"
                      v-model="organizationForm.department"
                      @blur="
                        validateField(
                          'department',
                          organizationForm.department,
                          validationRules.department
                        )
                      "
                      class="form-input"
                      :class="{ 'form-input--error': formErrors.department }"
                      placeholder="请输入您所在的部门"
                      required
                    />
                  </div>
                  <div v-if="formErrors.department" class="field-error">
                    {{ formErrors.department }}
                  </div>
                </div>

                <!-- 加入现有机构 -->
                <template v-if="organizationForm.registration_choice === 'existing'">
                  <!-- 搜索机构 -->
                  <div class="form-group">
                    <label for="organizationSearch" class="form-label">搜索企业/机构</label>
                    <div class="organization-search-wrapper">
                      <div class="search-input-wrapper">
                        <!-- 组织类型筛选 -->
                        <div class="org-type-filter">
                          <select
                            v-model="organizationTypeFilter"
                            @change="handleOrganizationTypeChange"
                            class="org-type-select"
                          >
                            <option value="">全部</option>
                            <option value="enterprise">企业</option>
                            <option value="university">大学</option>
                            <option value="other">其他</option>
                          </select>
                        </div>

                        <!-- 搜索输入框 -->
                        <div class="input-wrapper search-input">
                          <div class="input-icon">
                            <el-icon><Search /></el-icon>
                          </div>
                          <input
                            type="text"
                            id="organizationSearch"
                            v-model="organizationSearch"
                            @input="handleOrganizationSearch($event.target.value)"
                            @focus="showOrganizationDropdown = organizationList.length > 0"
                            @blur="
                              validateField(
                                'organization_search',
                                organizationSearch,
                                validationRules.organization_search
                              )
                            "
                            class="form-input"
                            :class="{ 'form-input--error': formErrors.organization_search }"
                            placeholder="请输入企业/机构名称进行搜索"
                            required
                          />
                        </div>
                      </div>

                      <!-- 搜索结果下拉框 -->
                      <div
                        v-if="showOrganizationDropdown && organizationList.length > 0"
                        class="organization-dropdown"
                      >
                        <div class="dropdown-header">
                          <span class="dropdown-title">搜索结果</span>
                          <button
                            type="button"
                            @click="showOrganizationDropdown = false"
                            class="dropdown-close"
                          >
                            ×
                          </button>
                        </div>
                        <div class="dropdown-list">
                          <div
                            v-for="org in organizationList"
                            :key="org.id"
                            @click="selectOrganization(org)"
                            class="organization-item"
                          >
                            <div class="org-main">
                              <h4 class="org-name">{{ org.name }}</h4>
                              <span class="org-type">{{ org.organization_type_display }}</span>
                            </div>
                            <div class="org-details">
                              <span class="org-industry">{{ org.industry_or_discipline }}</span>
                              <span class="org-address" v-if="org.address">{{ org.address }}</span>
                            </div>
                          </div>
                        </div>
                      </div>

                      <!-- 加载状态 -->
                      <div v-if="organizationLoading" class="search-loading">搜索中...</div>
                    </div>
                    <div v-if="formErrors.organization_search" class="field-error">
                      {{ formErrors.organization_search }}
                    </div>
                  </div>
                </template>

                <!-- 创建新机构 -->
                <template v-else>
                  <!-- 企业/机构名称 -->
                  <div class="form-group">
                    <label for="organizationName" class="form-label">企业/机构名称</label>
                    <div class="input-wrapper">
                      <div class="input-icon">
                        <el-icon><OfficeBuilding /></el-icon>
                      </div>
                      <input
                        type="text"
                        id="organizationName"
                        v-model="organizationForm.organization_name"
                        @blur="
                          validateField(
                            'organization_name',
                            organizationForm.organization_name,
                            validationRules.organization_name
                          )
                        "
                        class="form-input"
                        :class="{ 'form-input--error': formErrors.organization_name }"
                        placeholder="请输入企业/机构名称"
                        required
                      />
                    </div>
                    <div v-if="formErrors.organization_name" class="field-error">
                      {{ formErrors.organization_name }}
                    </div>
                  </div>

                  <!-- 组织类型 -->
                  <div class="form-group">
                    <label for="organizationType" class="form-label">组织类型</label>
                    <div class="input-wrapper">
                      <div class="input-icon">
                        <el-icon><OfficeBuilding /></el-icon>
                      </div>
                      <select
                        id="organizationType"
                        v-model="organizationForm.organization_type"
                        @blur="
                          validateField(
                            'organization_type',
                            organizationForm.organization_type,
                            validationRules.organization_type
                          )
                        "
                        class="form-select"
                        :class="{ 'form-select--error': formErrors.organization_type }"
                        required
                      >
                        <option value="">请选择组织类型</option>
                        <option value="enterprise">企业</option>
                        <option value="university">高等院校</option>
                        <option value="other">其他机构</option>
                      </select>
                    </div>
                    <div v-if="formErrors.organization_type" class="field-error">
                      {{ formErrors.organization_type }}
                    </div>
                  </div>

                  <!-- 所属行业 -->
                  <div class="form-group">
                    <label for="industryOrDiscipline" class="form-label">所属行业/领域</label>
                    <div class="input-wrapper">
                      <div class="input-icon">
                        <el-icon><Reading /></el-icon>
                      </div>
                      <input
                        type="text"
                        id="industryOrDiscipline"
                        v-model="organizationForm.industry_or_discipline"
                        @blur="
                          validateField(
                            'industry_or_discipline',
                            organizationForm.industry_or_discipline,
                            validationRules.industry_or_discipline
                          )
                        "
                        class="form-input"
                        :class="{ 'form-input--error': formErrors.industry_or_discipline }"
                        placeholder="请输入所属行业/领域"
                        required
                      />
                    </div>
                    <div v-if="formErrors.industry_or_discipline" class="field-error">
                      {{ formErrors.industry_or_discipline }}
                    </div>
                  </div>
                </template>
              </template>

              <!-- 同意条款 -->
              <div class="terms-wrapper">
                <div class="checkbox-wrapper">
                  <input id="agreeTerms" type="checkbox" class="form-checkbox" required />
                  <label for="agreeTerms" class="terms-label">
                    我已阅读并同意
                    <a href="#" class="terms-link">《用户服务协议》</a>
                    和
                    <a href="#" class="terms-link">《隐私政策》</a>
                  </label>
                </div>
              </div>

              <!-- 注册按钮 -->
              <button
                type="submit"
                :disabled="
                  isRegistering ||
                  (userType === 'student' ? !isStudentFormValid : !isOrganizationFormValid)
                "
                class="submit-btn submit-btn--register"
              >
                <span>{{ isRegistering ? '注册中...' : '注册账号' }}</span>
                <el-icon v-if="!isRegistering"><Check /></el-icon>
                <el-icon v-else class="is-loading"><Loading /></el-icon>
              </button>
            </form>

            <!-- 登录提示 -->
            <p class="switch-form-text">
              已有账号?
              <button @click="showLoginForm" class="switch-form-link">立即登录</button>
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- 页脚 -->
    <footer class="page-footer">
      <div class="footer-content">
        <!-- <div class="footer-links">
          <a href="#" class="footer-link">关于我们</a>
          <a href="#" class="footer-link">帮助中心</a>
          <a href="#" class="footer-link">联系客服</a>
          <a href="#" class="footer-link">隐私政策</a>
          <a href="#" class="footer-link">用户协议</a>
        </div> -->
        <p class="footer-copyright">© 2025 智汇校企合作平台 版权所有</p>
      </div>
    </footer>

    <!-- 成功提示弹窗 -->
    <Transition
      enter-active-class="toast-enter-active"
      enter-from-class="toast-enter-from"
      enter-to-class="toast-enter-to"
      leave-active-class="toast-leave-active"
      leave-from-class="toast-leave-from"
      leave-to-class="toast-leave-to"
    >
      <div v-if="successToast" class="toast toast--success">
        <el-icon><CircleCheck /></el-icon>
        <span>{{ successMessage }}</span>
      </div>
    </Transition>

    <!-- 错误提示弹窗 -->
    <Transition
      enter-active-class="toast-enter-active"
      enter-from-class="toast-enter-from"
      enter-to-class="toast-enter-to"
      leave-active-class="toast-leave-active"
      leave-from-class="toast-leave-from"
      leave-to-class="toast-leave-to"
    >
      <div v-if="errorToast" class="toast toast--error">
        <el-icon><CircleClose /></el-icon>
        <span>{{ errorMessage }}</span>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* 全局动画 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 加载动画 */
.is-loading {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 页面容器 */
.page-container {
  font-family: 'Inter', system-ui, sans-serif;
  background-color: #f5f7fa;
  color: #1d2129;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

@media (min-width: 768px) {
  .main-content {
    flex-direction: row;
  }
}

/* 品牌展示区 - 确保蓝色背景 */
.brand-section {
  display: none;
  background: linear-gradient(135deg, #1554db 0%, #0a4bdb 100%);
  padding: 4rem;
  color: #ffffff;
  position: relative;
  overflow: hidden;
  justify-content: space-between;
  flex-direction: column;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
  box-shadow: inset 0 0 100px rgba(0, 0, 0, 0.1);
}

@media (min-width: 768px) {
  .brand-section {
    display: flex;
    width: 50%;
    background: linear-gradient(135deg, #1554db 0%, #0a4bdb 100%);
  }
}

@media (min-width: 1024px) {
  .brand-section {
    padding: 8rem;
  }
}

.decoration-circle {
  position: absolute;
  background-color: rgba(255, 255, 255, 0.15);
  border-radius: 50%;
  backdrop-filter: blur(8px);
}

.decoration-circle--top {
  top: -8rem;
  right: -8rem;
  width: 16rem;
  height: 16rem;
  background: linear-gradient(45deg, rgba(255, 255, 255, 0.2), rgba(255, 255, 255, 0.1));
}

.decoration-circle--bottom {
  bottom: -12rem;
  left: -12rem;
  width: 24rem;
  height: 24rem;
  background: linear-gradient(225deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
}

.brand-header {
  position: relative;
  z-index: 10;
}

.brand-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.5rem;
}

.logo-icon {
  width: 2.5rem;
  height: 2.5rem;
  background-color: #ffffff;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1554db;
  font-size: 1.25rem;
}

.brand-title {
  font-size: clamp(1.5rem, 3vw, 2.5rem);
  font-weight: 700;
  margin: 0;
  color: #ffffff !important;
  color: #ffffff;
}

.brand-subtitle {
  color: #ffffff !important;
  color: #ffffff;
  opacity: 0.9;
  max-width: 28rem;
  margin: 0;
}

.brand-content {
  position: relative;
  z-index: 10;
  animation: fadeIn 0.5s ease-out 0.2s forwards;
  opacity: 0;
}

.brand-headline {
  font-size: clamp(1.8rem, 4vw, 3rem);
  font-weight: 700;
  margin-bottom: 1.5rem;
  margin-top: 1.5rem;
  color: #ffffff !important;
  color: #ffffff;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  line-height: 1.2;
}

.brand-description {
  color: #ffffff !important;
  color: #ffffff;
  opacity: 0.9;
  font-size: 1.125rem;
  margin-bottom: 2rem;
  max-width: 32rem;
  line-height: 1.6;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.feature-icon {
  margin-top: 0.25rem;
  background-color: rgba(255, 255, 255, 0.2);
  padding: 0.75rem;
  border-radius: 0.75rem;
  flex-shrink: 0;
}

.feature-content {
  flex: 1;
}

.feature-title {
  font-size: 1.25rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  color: #ffffff !important;
  color: #ffffff;
}

.feature-description {
  color: #ffffff !important;
  color: #ffffff;
  opacity: 0.8;
  margin: 0;
  line-height: 1.5;
}

.brand-footer {
  position: relative;
  z-index: 10;
  padding-top: 2rem;
  margin-top: 2rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  animation: fadeIn 0.5s ease-out 0.4s forwards;
  opacity: 0;
}

.copyright {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.875rem;
  margin: 0;
}

/* 表单区域 */
.form-section {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
}

@media (min-width: 768px) {
  .form-section {
    width: 50%;
    padding: 3rem;
  }
}

@media (min-width: 1024px) {
  .form-section {
    padding: 5rem;
  }
}

.form-container {
  width: 100%;
  max-width: 28rem;
  animation: fadeIn 0.5s ease-out forwards;
}

/* 移动端品牌 */
.mobile-brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

@media (min-width: 768px) {
  .mobile-brand {
    display: none;
  }
}

.mobile-logo {
  width: 2.5rem;
  height: 2.5rem;
  background-color: #1554db;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  font-size: 1.25rem;
}

.mobile-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1d2129;
  margin: 0;
}

/* 表单标签页 */
.form-tabs {
  display: flex;
  border-bottom: 1px solid #e4e6eb;
  margin-bottom: 2rem;
}

.form-tab {
  padding: 0.75rem 0.25rem;
  font-weight: 500;
  color: #86909c;
  background: none;
  border: none;
  margin-right: 1.5rem;
  transition: all 300ms ease-in-out;
  cursor: pointer;
  position: relative;
}

.form-tab:hover {
  color: #272e3b;
}

.form-tab--active {
  color: #1554db;
}

.form-tab--active::after {
  content: '';
  position: absolute;
  bottom: -1px;
  left: 0;
  right: 0;
  height: 2px;
  background-color: #1554db;
}

/* 表单内容 */
.form-content {
  animation: fadeIn 0.3s ease-out forwards;
}

.form-title {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 700;
  color: #1d2129;
  margin: 0 0 1.5rem 0;
}

.form-subtitle {
  color: #4e5969;
  margin: 0 0 2rem 0;
  line-height: 1.5;
}

/* 用户类型选择器 */
.user-type-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.user-type-option {
  position: relative;
  cursor: pointer;
}

.user-type-radio {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.user-type-card {
  border: 2px solid #c9cdd4;
  border-radius: 0.75rem;
  padding: 1rem;
  transition: all 300ms ease-in-out;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-type-radio:checked + .user-type-card {
  border-color: #1554db;
  background-color: rgba(22, 93, 255, 0.05);
}

.user-type-icon {
  width: 2rem;
  height: 2rem;
  background-color: rgba(22, 93, 255, 0.1);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #1554db;
  flex-shrink: 0;
}

@media (min-width: 768px) {
  .user-type-icon {
    width: 2.5rem;
    height: 2.5rem;
  }
}

.user-type-label {
  font-weight: 500;
  font-size: 0.875rem;
}

@media (min-width: 768px) {
  .user-type-label {
    font-size: 1rem;
  }
}

/* 注册选择样式 */
.registration-choice {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.choice-option {
  position: relative;
  cursor: pointer;
}

.choice-radio {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.choice-card {
  border: 2px solid #c9cdd4;
  border-radius: 0.75rem;
  padding: 0.75rem;
  transition: all 300ms ease-in-out;
  text-align: center;
}

.choice-radio:checked + .choice-card {
  border-color: #1554db;
  background-color: rgba(22, 93, 255, 0.05);
}

.choice-label {
  font-weight: 500;
  font-size: 0.875rem;
  color: #272e3b;
}

/* 机构类型选择 */
.organization-type-selector {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.type-option {
  position: relative;
  cursor: pointer;
}

.type-radio {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.type-card {
  border: 2px solid #c9cdd4;
  border-radius: 0.75rem;
  padding: 0.75rem;
  transition: all 300ms ease-in-out;
  text-align: center;
}

.type-radio:checked + .type-card {
  border-color: #1554db;
  background-color: rgba(22, 93, 255, 0.05);
}

.type-label {
  font-weight: 500;
  font-size: 0.875rem;
  color: #272e3b;
}

/* 机构搜索 */
.organization-search-wrapper {
  position: relative;
}

.search-input-wrapper {
  display: flex;
  gap: 1rem;
  align-items: stretch;
}

.org-type-filter {
  flex-shrink: 0;
  min-width: 5rem;
}

.org-type-select {
  width: 100%;
  height: 100%;
  padding: 0.75rem 0.5rem;
  border: 1px solid #c9cdd4;
  border-radius: 0.75rem;
  font-size: 0.875rem;
  background-color: #ffffff;
  cursor: pointer;
  transition: all 300ms ease-in-out;
}

.org-type-select:focus {
  outline: none;
  border-color: #1554db;
  box-shadow: 0 0 0 3px rgba(22, 93, 255, 0.1);
}

.search-input {
  flex: 1;
}

.organization-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid #c9cdd4;
  border-radius: 0.75rem;
  margin-top: 0.5rem;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 20rem;
  overflow: hidden;
}

.dropdown-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #e4e6eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f7fa;
}

.dropdown-title {
  font-weight: 500;
  font-size: 0.875rem;
  color: #272e3b;
}

.dropdown-close {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #86909c;
  cursor: pointer;
  padding: 0;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.dropdown-close:hover {
  color: #272e3b;
}

.dropdown-list {
  max-height: 16rem;
  overflow-y: auto;
}

.organization-item {
  padding: 1rem;
  border-bottom: 1px solid #f5f7fa;
  cursor: pointer;
  transition: all 300ms ease-in-out;
}

.organization-item:hover {
  background-color: #f5f7fa;
}

.organization-item:last-child {
  border-bottom: none;
}

.org-main {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.org-name {
  font-weight: 600;
  font-size: 1rem;
  color: #272e3b;
  margin: 0;
  flex: 1;
}

.org-type {
  background-color: rgba(22, 93, 255, 0.1);
  color: #1554db;
  font-size: 0.75rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
}

.org-details {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.org-industry {
  font-size: 0.875rem;
  color: #4e5969;
  font-weight: 500;
}

.org-address {
  font-size: 0.75rem;
  color: #86909c;
}

.search-loading {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid #c9cdd4;
  border-radius: 0.75rem;
  margin-top: 0.5rem;
  padding: 1rem;
  text-align: center;
  font-size: 0.875rem;
  color: #4e5969;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
}

/* 学校搜索 */
.school-search-wrapper {
  position: relative;
}

.school-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: #ffffff;
  border: 1px solid #c9cdd4;
  border-radius: 0.75rem;
  margin-top: 0.5rem;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  max-height: 20rem;
  overflow: hidden;
}

.school-item {
  padding: 1rem;
  border-bottom: 1px solid #f5f7fa;
  cursor: pointer;
  transition: all 300ms ease-in-out;
}

.school-item:hover {
  background-color: #f5f7fa;
}

.school-item:last-child {
  border-bottom: none;
}

.school-name {
  font-weight: 600;
  font-size: 1rem;
  color: #272e3b;
  margin: 0;
}

/* 表单样式 */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  font-weight: 500;
  color: #272e3b;
  margin-bottom: 0.25rem;
  font-size: 0.875rem;
}

.form-label-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.form-link-row {
  display: flex;
  justify-content: space-between;
}

.form-link {
  color: #1554db;
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 300ms ease-in-out;
}

.form-link:hover {
  color: rgba(22, 93, 255, 0.8);
}

.input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.input-icon {
  position: absolute;
  left: 0.75rem;
  color: #86909c;
  pointer-events: none;
  z-index: 1;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.5rem;
  border: 1px solid #c9cdd4;
  border-radius: 0.75rem;
  font-size: 1rem;
  transition: all 300ms ease-in-out;
  background-color: #ffffff;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #1554db;
  box-shadow: 0 0 0 3px rgba(22, 93, 255, 0.1);
}

.form-input--with-action {
  padding-right: 2.5rem;
}

.input-action {
  position: absolute;
  right: 0.75rem;
  background: none;
  border: none;
  color: #86909c;
  cursor: pointer;
  transition: all 300ms ease-in-out;
  padding: 0.25rem;
}

.input-action:hover {
  color: #272e3b;
}

.form-hint {
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #86909c;
}

/* 表单错误状态 */
.form-input--error,
.form-select--error {
  border-color: #ef4444;
}

.form-input--error:focus,
.form-select--error:focus {
  border-color: #ef4444;
  box-shadow: 0 0 0 3px rgba(239, 68, 68, 0.1);
}

/* 字段错误提示 */
.field-error {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #ef4444;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.field-error::before {
  content: '⚠';
  font-size: 0.75rem;
}

/* 密码强度指示器 */
.password-strength {
  margin-top: 0.75rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.strength-bar {
  flex: 1;
  height: 0.375rem;
  background-color: #e2e8f0;
  border-radius: 0.1875rem;
  overflow: hidden;
}

.strength-fill {
  height: 100%;
  transition: all 300ms ease-in-out;
  border-radius: 0.1875rem;
}

.strength-text {
  font-size: 0.875rem;
  font-weight: 500;
  transition: color 300ms ease-in-out;
  white-space: nowrap;
}

/* 验证码输入 */
.verification-wrapper {
  display: flex;
  gap: 0.75rem;
}

.verification-input {
  flex: 1;
}

.verification-btn {
  white-space: nowrap;
  padding: 0.75rem 1rem;
  border: 1px solid #c9cdd4;
  border-radius: 0.75rem;
  background-color: #ffffff;
  color: #272e3b;
  font-weight: 500;
  cursor: pointer;
  transition: all 300ms ease-in-out;
  font-size: 0.875rem;
}

.verification-btn:hover:not(:disabled) {
  background-color: #f5f7fa;
}

.verification-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* 复选框 */
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-checkbox {
  width: 1rem;
  height: 1rem;
  accent-color: #1554db;
  border-radius: 0.25rem;
}

.checkbox-label {
  font-size: 0.875rem;
  color: #272e3b;
  line-height: 1.4;
}

/* 条款 */
.terms-wrapper {
  margin-top: 0.5rem;
}

.terms-label {
  font-size: 0.875rem;
  color: #272e3b;
  line-height: 1.4;
}

.terms-link {
  color: #1554db;
  text-decoration: none;
}

.terms-link:hover {
  text-decoration: underline;
}

/* 提交按钮 */
.submit-btn {
  width: 100%;
  background-color: #1554db;
  color: #ffffff;
  font-weight: 500;
  padding: 0.75rem 1rem;
  border: none;
  border-radius: 0.75rem;
  cursor: pointer;
  transition: all 300ms ease-in-out;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-size: 1rem;
}

.submit-btn:hover:not(:disabled) {
  background-color: rgba(22, 93, 255, 0.9);
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn--register:disabled {
  background-color: #c9cdd4;
}

/* 分隔线 */
.divider {
  position: relative;
  margin: 2rem 0;
  text-align: center;
}

.divider::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 0;
  right: 0;
  height: 1px;
  background-color: #e4e6eb;
}

.divider-text {
  background-color: #f5f7fa;
  padding: 0 0.5rem;
  font-size: 0.875rem;
  color: #4e5969;
  position: relative;
}

/* 表单切换 */
.switch-form-text {
  text-align: center;
  color: #4e5969;
  margin: 2rem 0 0 0;
  font-size: 0.875rem;
}

.switch-form-link {
  color: #1554db;
  font-weight: 500;
  background: none;
  border: none;
  cursor: pointer;
  text-decoration: none;
}

.switch-form-link:hover {
  text-decoration: underline;
}

/* 页脚 */
.page-footer {
  padding: 1.5rem;
  text-align: center;
  color: #4e5969;
  font-size: 0.875rem;
  border-top: 1px solid #e4e6eb;
}

.footer-content {
  max-width: 96rem;
  margin: 0 auto;
}

.footer-links {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem 1rem;
  margin-bottom: 1rem;
}

.footer-link {
  color: #4e5969;
  text-decoration: none;
  transition: all 300ms ease-in-out;
}

.footer-link:hover {
  color: #1554db;
}

.footer-copyright {
  margin: 0;
}

/* 提示弹窗 */
.toast {
  position: fixed;
  top: 1.5rem;
  right: 1.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.75rem;
  color: #ffffff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  z-index: 1000;
  box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

.toast--success {
  background-color: #36b37e;
}

.toast--error {
  background-color: #ef4444;
}

/* 弹窗动画 */
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease-out;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-enter-to,
.toast-leave-from {
  opacity: 1;
  transform: translateX(0);
}

/* 密码输入框隐藏小眼睛 */
input[type='password']::-ms-reveal,
input[type='password']::-ms-clear {
  display: none;
}

/* 响应式设计优化 */
@media (max-width: 767px) {
  .form-section {
    padding: 1rem;
  }

  .form-container {
    max-width: none;
  }

  .user-type-selector {
    gap: 0.75rem;
  }

  .user-type-card {
    padding: 0.75rem;
    flex-direction: column;
    text-align: center;
    gap: 0.5rem;
  }

  .user-type-icon {
    width: 2rem;
    height: 2rem;
  }

  .user-type-label {
    font-size: 0.875rem;
  }

  .verification-wrapper {
    gap: 0.5rem;
  }

  .footer-links {
    gap: 1rem 0.5rem;
  }

  .registration-choice,
  .organization-type-selector {
    gap: 0.75rem;
  }

  .choice-card,
  .type-card {
    padding: 0.5rem;
  }

  .organization-dropdown {
    margin-top: 0.25rem;
  }

  .organization-item {
    padding: 0.75rem;
  }

  .org-main {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .password-strength {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .strength-text {
    text-align: center;
  }

  .search-input-wrapper {
    gap: 0.5rem;
  }

  .org-type-filter {
    min-width: 4rem;
  }
}
/* ===== 悬浮返回首页按钮（左上角） ===== */
.home-float-btn-wrap {
  position: fixed;
  top: calc(12px + env(safe-area-inset-top, 0px));
  left: calc(12px + env(safe-area-inset-left, 0px));
  z-index: 3000;
  pointer-events: none; /* 让内部按钮接管点击 */
}

.home-float-btn {
  pointer-events: auto;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: 500;
  padding: 8px 14px 8px 12px;
  border-radius: 999px;
  text-decoration: none;
  line-height: 1;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.85), rgba(255, 255, 255, 0.7));
  color: #1d2129;
  border: 1px solid rgba(255, 255, 255, 0.6);
  box-shadow:
    0 2px 4px rgba(0, 0, 0, 0.08),
    0 4px 18px -4px rgba(0, 0, 0, 0.12);
  transition:
    background 0.18s ease,
    box-shadow 0.18s ease,
    transform 0.18s ease;
}

.home-float-btn:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95), rgba(255, 255, 255, 0.8));
  box-shadow:
    0 4px 10px rgba(0, 0, 0, 0.12),
    0 6px 22px -6px rgba(0, 0, 0, 0.18);
  transform: translateY(-1px);
}

.home-float-btn:active {
  transform: translateY(0);
  box-shadow:
    0 2px 6px rgba(0, 0, 0, 0.1),
    0 3px 14px -4px rgba(0, 0, 0, 0.14);
}

.home-float-btn:focus-visible {
  outline: 2px solid #1554db;
  outline-offset: 2px;
}

.home-float-icon {
  font-size: 16px;
  line-height: 1;
  color: #1554db;
}

.home-float-text {
  /* 防止极窄屏过早换行 */
  white-space: nowrap;
}

/* 深色背景（品牌区）下的对比优化：当按钮位于蓝色区上方时保持可读性。
   简单策略：大屏时蓝色品牌区宽 50%，按钮本来就在左上角无需改变；若需要更深的对比可加一个轻微阴影外环 */
@media (min-width: 768px) {
  .home-float-btn {
    border-color: rgba(255, 255, 255, 0.55);
  }
}

/* 窄屏适配：缩小按钮内边距和字体 */
@media (max-width: 480px) {
  .home-float-btn {
    padding: 7px 12px 7px 10px;
    font-size: 13px;
  }
  .home-float-icon {
    font-size: 15px;
  }
}

/* 当用户开启“减少动态”时，关闭小的动效 */
@media (prefers-reduced-motion: reduce) {
  .home-float-btn {
    transition: none;
  }
}
</style>
