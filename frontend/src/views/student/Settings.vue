<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()

// 展示账号信息（实际项目中请从登录态/用户信息接口获取）
const accountLogin = ref('wildbreath') // 示例：当前登录账号
const copyToClipboard = async (text) => {
  try {
    await navigator.clipboard.writeText(text)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.warning('复制失败，请手动复制')
  }
}

/* ========== 个人资料 ========== */
const profileFormRef = ref()
const profileForm = reactive({
  avatarUrl: 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png',
  name: '学生姓名',
  studentId: '2025XXXX',
  major: '计算机科学与技术',
  grade: '大三',
  email: 'student@example.com',
  phone: '',
  bio: ''
})
const profileRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: ['blur', 'change'] }
  ],
  phone: [
    {
      validator: (_, v, cb) => {
        if (!v) return cb()
        const ok = /^(\+?\d{1,3}[- ]?)?\d{7,15}$/.test(v)
        ok ? cb() : cb(new Error('手机号格式不正确'))
      },
      trigger: ['blur', 'change']
    }
  ]
}
const beforeAvatarUpload = (file) => {
  const isImg = ['image/jpeg', 'image/png', 'image/gif'].includes(file.type)
  const isLt2M = file.size / 1024 / 1024 < 2
  if (!isImg) ElMessage.warning('仅支持 JPG/PNG/GIF 图片')
  if (!isLt2M) ElMessage.warning('头像大小需小于 2MB')
  return isImg && isLt2M
}
const onAvatarChange = (file) => {
  if (!file?.raw) return
  const url = URL.createObjectURL(file.raw)
  profileForm.avatarUrl = url
}
const saveProfile = async () => {
  await profileFormRef.value.validate()
  // TODO: 接入后端保存个人资料
  ElMessage.success('个人资料已保存')
}

/* ========== 账户安全（仅修改密码） ========== */
const secFormRef = ref()
const secForm = reactive({
  currentPwd: '',
  newPwd: '',
  confirmPwd: ''
})
const commonWeak = new Set(['12345678', 'password', 'qwerty', 'abc123456', '11111111'])
const pwdStrength = computed(() => {
  const v = secForm.newPwd || ''
  let score = 0
  if (v.length >= 10) score += 25
  if (v.length >= 14) score += 10
  const hasLower = /[a-z]/.test(v)
  const hasUpper = /[A-Z]/.test(v)
  const hasDigit = /\d/.test(v)
  const hasSymbol = /[^A-Za-z0-9]/.test(v)
  const variety = [hasLower, hasUpper, hasDigit, hasSymbol].filter(Boolean).length
  score += variety * 15
  if (!/\s/.test(v)) score += 5
  if (commonWeak.has(v)) score = 10
  return Math.min(score, 100)
})
const pwdStrengthColor = computed(() => {
  const s = pwdStrength.value
  if (s < 35) return '#ef4444' // 弱
  if (s < 70) return '#f59e0b' // 中
  return '#10b981' // 强
})
const pwdStrengthText = computed(() => {
  const s = pwdStrength.value
  if (s < 35) return '密码强度：弱'
  if (s < 70) return '密码强度：中'
  return '密码强度：强'
})
const pwdRules = {
  currentPwd: [{ required: true, message: '请输入当前密码', trigger: 'blur' }],
  newPwd: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    {
      validator: (_, v, cb) => {
        if (!v) return cb()
        if (/\s/.test(v)) return cb(new Error('密码不能包含空白字符'))
        if (v.length < 10) return cb(new Error('至少 10 位'))
        if (!/[a-z]/.test(v) || !/[A-Z]/.test(v) || !/\d/.test(v) || !/[^A-Za-z0-9]/.test(v)) {
          return cb(new Error('需包含大小写字母、数字和符号'))
        }
        if (v === secForm.currentPwd) return cb(new Error('新密码不能与当前密码相同'))
        if (commonWeak.has(v)) return cb(new Error('密码过于常见，请更换'))
        cb()
      },
      trigger: ['blur', 'change']
    }
  ],
  confirmPwd: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (_, v, cb) =>
        v === secForm.newPwd ? cb() : cb(new Error('两次输入的密码不一致')),
      trigger: ['blur', 'change']
    }
  ]
}
const changePassword = async () => {
  await secFormRef.value.validate()
  // TODO: 调用后端修改密码接口
  ElMessage.success('密码已更新')
  secForm.currentPwd = ''
  secForm.newPwd = ''
  secForm.confirmPwd = ''
}

// 退出登录 / 删除账号（可选操作）
const logout = () => router.push('/login')
const deleteAccount = async () => {
  try {
    await ElMessageBox.confirm('此操作不可恢复，确认要删除账号吗？', '危险操作', {
      type: 'warning',
      confirmButtonText: '确认删除',
      cancelButtonText: '取消'
    })
    // TODO: 调用后端删除账号
    ElMessage.success('账号已删除')
    router.push('/login')
  } catch {
    ElMessage.error('删除失败')
  }
}
</script>

<template>
  <div class="settings-page">
    <div class="head">
      <div class="title">个人设置</div>
      <div class="sub">管理你的个人资料与账户安全</div>
    </div>

    <!-- 账号信息展示 -->
    <el-alert type="info" :closable="false" class="acct">
      <template #title>
        当前账号：<b class="acct-val">{{ accountLogin }}</b>
        <el-button link type="primary" class="ml8" @click="copyToClipboard(accountLogin)"
          >复制</el-button
        >
      </template>
    </el-alert>

    <div class="grid">
      <!-- 左列：个人资料 -->
      <div class="col">
        <el-card class="card" shadow="never">
          <template #header>
            <div class="card-hd">个人资料</div>
          </template>
          <div class="profile">
            <div class="avatar-block">
              <el-avatar :size="72" :src="profileForm.avatarUrl" />
              <el-upload
                class="upload"
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                :before-upload="beforeAvatarUpload"
                :on-change="onAvatarChange"
              >
                <el-button size="small">更换头像</el-button>
              </el-upload>
              <div class="hint">支持 JPG/PNG/GIF，最大 2MB</div>
            </div>
            <el-form
              ref="profileFormRef"
              :model="profileForm"
              :rules="profileRules"
              label-width="96px"
              class="form"
            >
              <el-form-item label="账号">
                <el-input :model-value="accountLogin" disabled />
              </el-form-item>
              <el-form-item label="姓名" prop="name">
                <el-input v-model="profileForm.name" placeholder="请输入姓名" />
              </el-form-item>
              <el-form-item label="学号">
                <el-input v-model="profileForm.studentId" placeholder="学号" />
              </el-form-item>
              <el-form-item label="专业">
                <el-input v-model="profileForm.major" placeholder="专业" />
              </el-form-item>
              <el-form-item label="年级">
                <el-select v-model="profileForm.grade" placeholder="请选择年级">
                  <el-option label="大一" value="大一" />
                  <el-option label="大二" value="大二" />
                  <el-option label="大三" value="大三" />
                  <el-option label="大四" value="大四" />
                  <el-option label="研究生" value="研究生" />
                </el-select>
              </el-form-item>
              <el-form-item label="邮箱" prop="email">
                <el-input v-model="profileForm.email" placeholder="邮箱" />
              </el-form-item>
              <el-form-item label="手机" prop="phone">
                <el-input v-model="profileForm.phone" placeholder="可选，便于同组同学联系" />
              </el-form-item>
              <el-form-item label="个人简介">
                <el-input
                  v-model="profileForm.bio"
                  type="textarea"
                  :rows="4"
                  placeholder="简单介绍你的方向、擅长与项目经历"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="saveProfile">保存资料</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>
      </div>

      <!-- 右列：账户安全（仅修改密码） -->
      <div class="col">
        <el-card class="card" shadow="never">
          <template #header>
            <div class="card-hd">账户安全</div>
          </template>

          <div class="sec-block">
            <div class="sec-title">修改密码</div>
            <el-form
              ref="secFormRef"
              :model="secForm"
              :rules="pwdRules"
              label-width="108px"
              class="sec-form"
            >
              <el-form-item label="当前密码" prop="currentPwd">
                <el-input
                  v-model="secForm.currentPwd"
                  type="password"
                  show-password
                  autocomplete="current-password"
                />
              </el-form-item>
              <el-form-item label="新密码" prop="newPwd">
                <el-input
                  v-model="secForm.newPwd"
                  type="password"
                  show-password
                  autocomplete="new-password"
                />
                <div class="pwd-meter">
                  <el-progress
                    :percentage="pwdStrength"
                    :color="pwdStrengthColor"
                    :stroke-width="8"
                  />
                  <div class="hint">
                    {{ pwdStrengthText }}（至少10位，包含大小写字母、数字和符号）
                  </div>
                </div>
              </el-form-item>
              <el-form-item label="确认新密码" prop="confirmPwd">
                <el-input
                  v-model="secForm.confirmPwd"
                  type="password"
                  show-password
                  autocomplete="new-password"
                />
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="changePassword">更新密码</el-button>
              </el-form-item>
            </el-form>
          </div>
        </el-card>

        <el-card class="card" shadow="never">
          <template #header>
            <div class="card-hd">账户操作</div>
          </template>
          <div class="danger">
            <div class="ops">
              <el-button @click="logout">退出登录</el-button>
              <el-button type="danger" plain @click="deleteAccount">删除账号</el-button>
            </div>
            <div class="desc">删除账号为不可恢复操作，请谨慎执行。</div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<style scoped lang="scss">
.settings-page {
  padding: 12px 16px 20px;
}
.head .title {
  font-size: 20px;
  font-weight: 800;
  color: #165dff;
}
.head .sub {
  color: #86909c;
  margin-top: 4px;
}
.acct {
  margin-top: 10px;
}
.acct-val {
  color: #1d2129;
}
.ml8 {
  margin-left: 8px;
}

.grid {
  margin-top: 12px;
  display: grid;
  grid-template-columns: 1.1fr 1fr;
  gap: 12px;
}
@media (max-width: 1024px) {
  .grid {
    grid-template-columns: 1fr;
  }
}
.card {
  border-radius: 12px;
}
.card-hd {
  font-weight: 700;
}

/* 个人资料 */
.profile {
  display: grid;
  grid-template-columns: 220px 1fr;
  gap: 12px;
}
@media (max-width: 720px) {
  .profile {
    grid-template-columns: 1fr;
  }
}
.avatar-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}
.avatar-block .hint {
  color: #86909c;
  font-size: 12px;
}
.profile .form :deep(.el-input__wrapper) {
  border-radius: 8px;
}

/* 安全 */
.sec-block {
  margin-bottom: 12px;
}
.sec-title {
  font-weight: 700;
  color: #1d2129;
  margin-bottom: 8px;
}
.sec-form :deep(.el-input__wrapper) {
  border-radius: 8px;
}
.pwd-meter {
  margin-top: 6px;
  .hint {
    color: #86909c;
    font-size: 12px;
    margin-top: 4px;
  }
}

/* 危险操作 */
.danger {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.danger .ops {
  display: flex;
  gap: 8px;
}
.danger .desc {
  color: #86909c;
  font-size: 12px;
}
</style>
