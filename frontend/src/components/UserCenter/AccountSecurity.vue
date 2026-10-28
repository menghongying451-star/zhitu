<!-- AccountSecurity.vue -->
<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore, useUserStore } from '@/stores'
import { authService, userService } from '@/api'
import router from '@/router'

const authStore = useAuthStore()
const userStore = useUserStore()

// 修改密码
const form = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const isPasswordEdit = ref(false)

// 进入"修改密码"编辑状态
const editPassword = () => {
  isPasswordEdit.value = true
}

// 取消编辑，重置表单
const cancelEdit = () => {
  form.value = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  }
  isPasswordEdit.value = false
}

// 保存新密码
const savePassword = async () => {
  if (!form.value.currentPassword) {
    ElMessage.warning('请输入当前密码')
    return
  }
  if (!form.value.newPassword) {
    ElMessage.warning('请输入新密码')
    return
  }
  if (!form.value.currentPassword === form.value.newPassword) {
    ElMessage.warning('新密码不能与当前密码相同')
    return
  }
  if (form.value.newPassword !== form.value.confirmPassword) {
    ElMessage.warning('两次输入的密码不一致')
    return
  }
  try {
    await authService.changePassword({
      old_password: form.value.currentPassword,
      new_password: form.value.newPassword,
      confirm_password: form.value.confirmPassword
    })
    ElMessage.success('密码更新成功,请重新登陆')
    cancelEdit()
    setTimeout(() => {
      authStore.removeRefreshToken()
      authStore.removeToken()
      authStore.removelogindata()
      router.push('/login').then(() => {
        window.location.reload()
      })
    }, 2000)
  } catch {
    ElMessage.error('密码更新失败')
  }
}

// 绑定信息
const boundData = ref({
  email: '',
  phone: ''
})
onMounted(async () => {
  boundData.value.email = userStore.user.email
  boundData.value.phone = userStore.user.phone
})
const dialogVisible = ref(false)
const changeType = ref('') // 'email' 或 'phone'
const newValue = ref('')
const verifyCode = ref('')
const codeSent = ref(false)
const countdown = ref(0)
let timer = null
const dialogWidth = ref(
  window.innerWidth <= 768 ? '300px' : window.innerWidth <= 1024 ? '400px' : '500px'
)
onMounted(() => {
  window.addEventListener('resize', () => {
    dialogWidth.value =
      window.innerWidth <= 768 ? '300px' : window.innerWidth <= 1024 ? '400px' : '500px'
  })
})
const openChangeDialog = (type) => {
  changeType.value = type
  newValue.value = ''
  verifyCode.value = ''
  codeSent.value = false
  dialogVisible.value = true
}

// 倒计时
const startCountdown = () => {
  countdown.value = 60
  timer = setInterval(() => {
    countdown.value--
    if (countdown.value <= 0) {
      clearInterval(timer)
      timer = null
    }
  }, 1000)
}

// 获取验证码
const sendCode = async () => {
  const value = newValue.value.trim()

  if (!value) {
    ElMessage.warning(`请输入新的${changeType.value === 'email' ? '邮箱' : '手机号'}`)
    return
  }

  // 校验格式
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  const phoneRegex = /^1[3-9]\d{9}$/ // 国内手机号格式（如需国际请调整）

  if (changeType.value === 'email' && !emailRegex.test(value)) {
    ElMessage.warning('请输入正确的邮箱格式')
    return
  }

  if (changeType.value === 'phone' && !phoneRegex.test(value)) {
    ElMessage.warning('请输入正确的手机号码格式')
    return
  }

  // 与原值是否一致
  if (
    (changeType.value === 'email' && value === boundData.value.email) ||
    (changeType.value === 'phone' && value === boundData.value.phone)
  ) {
    ElMessage.warning('新输入不能与原有一致')
    return
  }

  try {
    if (changeType.value === 'email') {
      await authService.sendEmailVerification({
        email: value,
        code_type: 'change_email'
      })
    } else if (changeType.value === 'phone') {
      await authService.sendPhoneVerification(value)
    }
    ElMessage.success('验证码已发送')
    codeSent.value = true
    startCountdown()
  } catch {
    ElMessage.error('验证码发送失败')
  }
}

// 提交修改
const submitChange = async () => {
  if (!newValue.value) {
    ElMessage.warning(`请输入新的${changeType.value === 'email' ? '邮箱' : '手机号'}`)
    return
  }
  if (!verifyCode.value) {
    ElMessage.warning('请输入验证码')
    return
  }

  try {
    if (changeType.value === 'email') {
      const res = await authService.changeEmail({
        email: newValue.value,
        email_code: verifyCode.value
      })
      ElMessage.success('邮箱修改成功')
      boundData.value.email = res.data.email
      userStore.setUser({ ...userStore.user, email: boundData.value.email })
    } else if (changeType.value === 'phone') {
      const res = await authService.changePhone({
        phone: newValue.value,
        phone_code: verifyCode.value
      })
      ElMessage.success('手机号修改成功')
      boundData.value.phone = res.data.phone
      userStore.setUser({ ...userStore.user, phone: boundData.value.phone })
    }
    dialogVisible.value = false
  } catch {
    ElMessage.error('绑定更新失败，请检查验证码')
  }
}

// 注销账户相关
const deleteDialogVisible = ref(false)
const deleteForm = ref({
  password: '',
  reason: '',
  emailCode: '',
  confirmDeletion: false
})
const deleteCodeSent = ref(false)
const deleteCountdown = ref(0)
let deleteTimer = null

// 确认注销 - 打开注销对话框
const confirmLogout = () => {
  deleteForm.value = {
    password: '',
    reason: '',
    emailCode: '',
    confirmDeletion: false
  }
  deleteCodeSent.value = false
  deleteCountdown.value = 0
  if (deleteTimer) {
    clearInterval(deleteTimer)
    deleteTimer = null
  }
  deleteDialogVisible.value = true
}

// 注销验证码倒计时
const startDeleteCountdown = () => {
  deleteCountdown.value = 60
  deleteTimer = setInterval(() => {
    deleteCountdown.value--
    if (deleteCountdown.value <= 0) {
      clearInterval(deleteTimer)
      deleteTimer = null
    }
  }, 1000)
}

// 获取注销验证码
const sendDeleteCode = async () => {
  try {
    await authService.sendEmailVerification({
      email: boundData.value.email,
      code_type: 'delete_account'
    })
    ElMessage.success('验证码已发送到您的邮箱')
    deleteCodeSent.value = true
    startDeleteCountdown()
  } catch {
    ElMessage.error('验证码发送失败')
  }
}

// 注销账户
const logout = async () => {
  // 表单验证
  if (!deleteForm.value.password) {
    ElMessage.warning('请输入账户密码')
    return
  }
  if (!deleteForm.value.reason) {
    ElMessage.warning('请输入注销原因')
    return
  }
  if (deleteForm.value.reason.length > 500) {
    ElMessage.warning('注销原因不能超过500字符')
    return
  }
  if (!deleteForm.value.emailCode) {
    ElMessage.warning('请输入邮箱验证码')
    return
  }
  if (!deleteForm.value.confirmDeletion) {
    ElMessage.warning('请确认您要注销账户')
    return
  }

  try {
    const res = await authService.deleteAccount({
      password: deleteForm.value.password,
      reason: deleteForm.value.reason,
      email_code: deleteForm.value.emailCode,
      confirm_deletion: deleteForm.value.confirmDeletion
    })

    ElMessage.success(res.data.message || '账户注销申请提交成功，将在7天后执行删除操作')
    deleteDialogVisible.value = false

    setTimeout(() => {
      authStore.removeRefreshToken()
      authStore.removeToken()
      authStore.removelogindata()
      router.push('/login').then(() => {
        window.location.reload()
      })
    }, 2000)
  } catch {
    ElMessage.error('注销申请提交失败，请检查输入信息')
  }
}
</script>

<template>
  <!-- 修改密码卡片 -->
  <el-card class="setting-card margin-bottom" shadow="never">
    <template #header>
      <h3>修改密码</h3>
      <div class="security-actions">
        <el-button v-if="!isPasswordEdit" type="text" @click="editPassword">修改密码</el-button>
        <template v-else>
          <el-button size="small" type="text" @click="cancelEdit">取消</el-button>
          <el-button size="small" type="primary" @click="savePassword">保存</el-button>
        </template>
      </div>
    </template>

    <el-form :model="form" label-position="top" size="large">
      <el-form-item label="当前密码">
        <el-input
          v-model="form.currentPassword"
          type="password"
          :disabled="!isPasswordEdit"
          placeholder="请输入当前密码"
        />
      </el-form-item>
      <el-form-item label="新密码">
        <el-input
          v-model="form.newPassword"
          type="password"
          :disabled="!isPasswordEdit"
          placeholder="请输入新密码"
        />
      </el-form-item>
      <el-form-item label="确认新密码">
        <el-input
          v-model="form.confirmPassword"
          type="password"
          :disabled="!isPasswordEdit"
          placeholder="请再次输入新密码"
        />
      </el-form-item>
    </el-form>
  </el-card>

  <!-- 绑定信息卡片 -->
  <el-card class="setting-card margin-bottom" shadow="never">
    <template #header>
      <h3>绑定信息</h3>
    </template>
    <el-form-item label="登录邮箱">
      <el-input v-model="boundData.email" disabled>
        <template #append>
          <el-button @click="openChangeDialog('email')">更换</el-button>
        </template>
      </el-input>
    </el-form-item>
    <el-form-item label="手机号码">
      <el-input v-model="boundData.phone" disabled>
        <template #append>
          <el-button @click="openChangeDialog('phone')">更换</el-button>
        </template>
      </el-input>
    </el-form-item>
  </el-card>

  <!-- 注销账户卡片 -->
  <el-card class="setting-card" shadow="never">
    <template #header>
      <h3>注销账户</h3>
    </template>
    <div class="logout-section">
      <p>注销后您的账户将被永久删除，此操作不可恢复。</p>
      <!-- <p>注销申请提交后，将在7天后执行删除操作，期间您可以取消注销申请。</p> -->
      <el-button type="danger" @click="confirmLogout">申请注销</el-button>
    </div>
  </el-card>

  <!-- 更换邮箱/手机号弹窗 -->
  <el-dialog
    v-model="dialogVisible"
    :title="`更换${changeType === 'email' ? '邮箱' : '手机号'}`"
    :width="dialogWidth"
  >
    <el-form label-position="top">
      <el-form-item :label="changeType === 'email' ? '新邮箱地址' : '新手机号码'">
        <el-input
          v-model="newValue"
          :placeholder="changeType === 'email' ? '请输入新邮箱' : '请输入新手机号'"
        />
      </el-form-item>
      <el-form-item label="验证码">
        <el-input v-model="verifyCode" placeholder="请输入验证码">
          <template #append>
            <el-button @click="sendCode" :disabled="countdown > 0">
              {{ countdown > 0 ? `${countdown}s后重试` : '获取验证码' }}
            </el-button>
          </template>
        </el-input>
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="dialogVisible = false">取消</el-button>
      <el-button type="primary" @click="submitChange">提交</el-button>
    </template>
  </el-dialog>

  <!-- 注销账户确认弹窗 -->
  <el-dialog
    v-model="deleteDialogVisible"
    title="注销账户"
    :width="dialogWidth"
    :close-on-click-modal="false"
  >
    <div class="delete-warning">
      <el-alert
        title="重要提醒"
        type="warning"
        description="账户注销后将无法恢复，请谨慎操作！注销申请提交后将在7天后执行删除。"
        show-icon
        :closable="false"
      />
    </div>

    <el-form :model="deleteForm" label-position="top" style="margin-top: 20px">
      <el-form-item label="账户密码" required>
        <el-input
          v-model="deleteForm.password"
          type="password"
          placeholder="请输入您的账户密码"
          show-password
        />
      </el-form-item>

      <el-form-item label="注销原因" required>
        <el-input
          v-model="deleteForm.reason"
          type="textarea"
          placeholder="请简述注销原因（必填，最多500字符）"
          :rows="3"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <el-form-item label="邮箱验证码" required>
        <el-input v-model="deleteForm.emailCode" placeholder="请输入验证码">
          <template #append>
            <el-button @click="sendDeleteCode" :disabled="deleteCountdown > 0">
              {{ deleteCountdown > 0 ? `${deleteCountdown}s后重试` : '获取验证码' }}
            </el-button>
          </template>
        </el-input>
        <div class="code-tip">验证码将发送到：{{ boundData.email }}</div>
      </el-form-item>

      <el-form-item>
        <el-checkbox v-model="deleteForm.confirmDeletion">
          我确认要注销账户，并理解此操作不可恢复
        </el-checkbox>
      </el-form-item>
    </el-form>

    <template #footer>
      <el-button @click="deleteDialogVisible = false">取消</el-button>
      <el-button type="danger" @click="logout" :disabled="!deleteForm.confirmDeletion">
        确认注销
      </el-button>
    </template>
  </el-dialog>
</template>

<style lang="scss" scoped>
.setting-card {
  border: 1px solid #e4e7ed;

  :deep(.el-card__header) {
    background: #fafafa;
    border-bottom: 1px solid #e4e7ed;
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: #303133;
    }
  }

  .security-actions {
    display: flex;
    gap: 8px;
  }

  .el-form-item {
    margin-bottom: 20px;
    .el-form-item__label {
      color: #606266;
      font-weight: 500;
    }
  }

  /* 注销卡片内部样式 */
  .logout-section {
    padding: 20px 0;
    text-align: center;
    p {
      margin-bottom: 12px;
      color: #606266;
      font-size: 14px;
    }
  }
}

/* 为第一个卡片添加底部间距 */
.margin-bottom {
  margin-bottom: 20px;
}

/* 注销对话框样式 */
.delete-warning {
  margin-bottom: 20px;
}

.code-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}
</style>
