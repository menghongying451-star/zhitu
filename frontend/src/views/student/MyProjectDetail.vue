<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { ArrowLeft, Document, User, FolderOpened, ChatSquare } from '@element-plus/icons-vue'
import {
  getProjectDetail,
  getProjectParticipants,
  updateProject,
  deleteProject,
  updateParticipantStatus, // 新增
  handleApplications, // 新增：审核处理申请
  transferLeadership
} from '@/api/student/project'
import { getResourceList, downloadResource } from '@/api/student/resource'
import AgentChat from '@/components/AgentChat.vue'
import { getEvaluationDetail } from '@/api/student/projectEvaluation'
import {
  getDeliverables,
  getDeliverableDetail,
  submitDeliverable,
  updateDeliverable
} from '@/api/student/deliverable'
import { getProjectComments, postProjectComment } from '@/api/student/projectComment'
import { getRequirementDetail } from '@/api/student/requirement'
// === 角色判断新增 BEGIN ===
import { useUserStore } from '@/stores/modules/user'
import { getParticipantDetail } from '@/api/student/project'

const userStore = useUserStore?.() || {}
const isOrgUser = computed(() => userStore.userInfo?.user_type === 'organization')
const isStudentUser = computed(() => userStore.userInfo?.user_type === 'student')
// === 角色判断新增 END ===

// 新增：上传列表事件（替换模板内联表达式更稳）
const onUploadChange = (file, files) => {
  submitFileList.value = Array.isArray(files) ? files : []
}
const onUploadRemove = (file, files) => {
  submitFileList.value = Array.isArray(files) ? files : []
}

// 新增：移除成员弹窗控制
const removeDialogVisible = ref(false)
const removeTarget = ref(null)
const removeReason = ref('')
const removing = ref(false)

// 转让组长相关
const transferDialogVisible = ref(false)
const transferForm = reactive({
  newLeaderId: null,
  transferMessage: ''
})
const transferring = ref(false)

/* ==== 需求资源过滤工具函数（新增） ==== */
function extractRequirementIdFromProject(p) {
  if (!p) return null
  return (
    p.parentDemand?.id ||
    p.requirement_id ||
    (typeof p.requirement === 'number' && p.requirement) ||
    p.requirement?.id ||
    null
  )
}

/* === 新增 BEGIN：申请信息查看弹窗与工具函数 === */
const applicationViewerVisible = ref(false)
const applicationViewer = ref(null)

// === 替换 BEGIN：openApplicationViewer ===
function openApplicationViewer(appRow) {
  applicationViewer.value = appRow
  applicationViewerVisible.value = true
  if (appRow && appRow._needDetail && !appRow._detailLoaded && project.value?.id) {
    // 单条补齐
    enrichPendingApplicants({ id: project.value.id, pendingApplicants: [appRow] })
  }
}
// === 替换 END ===

/** 学校字段归一化为名称（兼容字符串/对象） */
function schoolToName(schoolLike) {
  if (!schoolLike) return ''
  if (typeof schoolLike === 'string') return schoolLike
  return schoolLike.name || schoolLike.title || schoolLike.label || ''
}
/* === 新增 END === */

// 新增：提取后端错误信息的工具函数（放在 <script setup> 任意工具函数区）
function extractServerError(err) {
  const data = err?.response?.data
  if (!data) return ''
  if (typeof data === 'string') return data
  const direct = data.message || data.detail
  if (direct) return String(direct)
  // 递归取第一个字段错误
  const pickFirst = (obj) => {
    if (!obj || typeof obj !== 'object') return ''
    for (const k of Object.keys(obj)) {
      const v = obj[k]
      if (Array.isArray(v) && v.length) return String(v[0])
      if (typeof v === 'string' && v) return v
      if (v && typeof v === 'object') {
        const inner = pickFirst(v)
        if (inner) return inner
      }
    }
    return ''
  }
  return pickFirst(data) || ''
}

function resourceMatchesRequirement(res, reqId) {
  if (!reqId) return false
  const rid =
    res.requirement_id ||
    res.req_id ||
    (typeof res.requirement === 'number' && res.requirement) ||
    (typeof res.requirement?.id === 'number' && res.requirement.id)
  if (rid && Number(rid) === Number(reqId)) return true
  const arr =
    res.requirement_ids || res.requirements || res.requirement_list || res.req_ids || res.req_list
  if (Array.isArray(arr) && arr.map(Number).includes(Number(reqId))) return true
  return false
}

// allList：企业资源全集；knownReqResources：需求详情里直接返回的资源数组（如果有）
function filterResourcesByRequirement(allList, reqId, knownReqResources) {
  if (Array.isArray(knownReqResources) && knownReqResources.length) {
    const idSet = new Set(knownReqResources.map((r) => r.id))
    return allList.filter((r) => idSet.has(r.id))
  }
  const matched = allList.filter((r) => resourceMatchesRequirement(r, reqId))
  return matched.length ? matched : allList
}

function normalizeEnterpriseResource(r) {
  return {
    id: r.id ?? r.resource_id ?? r.uid ?? r.name,
    title: r.title || r.name || '',
    type: r.type || r.category || '',
    created_at: r.created_at || r.update_time || r.updated_at || '',
    raw: r
  }
}

// 可选：抓取企业全部资源（分页），避免只取第一页造成遗漏
async function fetchAllOrgResources(organizationId, pageSize = 50, maxPages = 10) {
  if (!organizationId) return []
  let page = 1
  const acc = []
  let totalPages = 1
  while (page <= totalPages && page <= maxPages) {
    try {
      const resp = await getResourceList({
        organization_id: organizationId,
        page,
        page_size: pageSize
      })
      if (resp?.data?.status !== 'success') break
      const data = resp.data.data || {}
      acc.push(...(data.resources || []))
      const pg = data.pagination || {}
      totalPages = pg.total_pages || 1
      page += 1
    } catch {
      break
    }
  }
  return acc
}

const DEFAULT_AVATAR =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40">
      <rect width="100%" height="100%" rx="20" fill="#EEF2FF"/>
      <circle cx="20" cy="16" r="8" fill="#93C5FD"/>
      <rect x="8" y="26" width="24" height="10" rx="5" fill="#BFDBFE"/>
    </svg>`
  )

const route = useRoute()
const router = useRouter()
const goBackToList = () => {
  router.push('/student/my-projects')
}

const activeTab = ref('intro')

const resolveCurrentUserId = () => {
  if (typeof window !== 'undefined') {
    const g = window
    const idFromGlobal =
      g.__USER_ID__ || g.__userId__ || g.__uid__ || g.__ACCOUNT_ID__ || g.__STUDENT_ID__
    if (
      (typeof idFromGlobal === 'number' && !Number.isNaN(idFromGlobal)) ||
      (typeof idFromGlobal === 'string' && idFromGlobal.trim())
    ) {
      const n = Number(idFromGlobal)
      if (!Number.isNaN(n)) return n
    }
  }
  const tryParse = (v) => {
    try {
      return JSON.parse(v)
    } catch {
      /* ignore */ void 0
      return null
    }
  }
  const ls = typeof localStorage !== 'undefined' ? localStorage : null
  if (ls) {
    const idKeys = [
      'userId',
      'uid',
      'id',
      'user_id',
      'account_id',
      'accountId',
      'studentId',
      'student_id'
    ]
    for (const k of idKeys) {
      const raw = ls.getItem(k)
      if (raw != null && String(raw).trim() !== '') {
        const n = Number(raw)
        if (!Number.isNaN(n)) return n
      }
    }
    const rawUser =
      ls.getItem('currentUser') || ls.getItem('user') || ls.getItem('profile') || ls.getItem('me')
    const obj = rawUser ? tryParse(rawUser) : null
    const candidates = [
      obj?.id,
      obj?.user?.id,
      obj?.student?.id,
      obj?.data?.id,
      obj?.data?.user?.id,
      obj?.data?.student?.id,
      obj?.user_id,
      obj?.account_id,
      obj?.student_id
    ].filter((x) => x !== undefined && x !== null)
    for (const c of candidates) {
      const n = Number(c)
      if (!Number.isNaN(n)) return n
    }
  }
  return null
}
const resolveCurrentUsername = () => {
  if (typeof window !== 'undefined') {
    const g = window
    const fromGlobal = g.__USERNAME__ || g.__USER_NAME__ || g.__login__ || g.__account__
    if (typeof fromGlobal === 'string' && fromGlobal.trim()) return fromGlobal.trim()
  }
  const tryParse = (v) => {
    try {
      return JSON.parse(v)
    } catch {
      /* ignore */ void 0
      return null
    }
  }
  const ls = typeof localStorage !== 'undefined' ? localStorage : null
  if (ls) {
    const strKeys = ['username', 'userName', 'login', 'account', 'user_login']
    for (const k of strKeys) {
      const v = ls.getItem(k)
      if (typeof v === 'string' && v.trim()) return v.trim()
    }
    const rawUser =
      ls.getItem('currentUser') || ls.getItem('user') || ls.getItem('profile') || ls.getItem('me')
    const obj = rawUser ? tryParse(rawUser) : null
    const candidates = [
      obj?.username,
      obj?.user?.username,
      obj?.data?.username,
      obj?.data?.user?.username,
      obj?.login,
      obj?.user_login
    ].filter((x) => typeof x === 'string' && x.trim())
    if (candidates.length) return String(candidates[0]).trim()
  }
  return ''
}
const myUserId = ref(resolveCurrentUserId())
const myUsername = ref(resolveCurrentUsername())

const projectId = Number(route.params.id)
const project = ref(null)

const hasResources = computed(() => (project.value?.resources?.length || 0) > 0)
const enterpriseResources = ref([])
const hasEnterpriseResources = computed(() => (enterpriseResources.value?.length || 0) > 0)

const navs = [
  { key: 'intro', title: '项目介绍', desc: '简介 · 详细 · 要求 · 隶属需求', icon: Document },
  { key: 'students', title: '项目成员', desc: '当前团队成员', icon: User },
  { key: 'resources', title: '项目资源', desc: '资料 · 成果', icon: FolderOpened },
  { key: 'evaluation', title: '项目评分', desc: '加权分 · 指标分 · 总评语', icon: Document },
  { key: 'discussion', title: '项目问答', desc: '智能体 · Q&A', icon: ChatSquare },
  { key: 'settings', title: '项目设置', desc: '管理项目相关设置', icon: Document }
]

const roleCategories = [
  '组长/前端',
  '前端',
  '后端',
  '算法',
  '测试',
  '产品',
  '设计',
  '可视化',
  '运维',
  '数据'
]
const normalizeRole = (r) => (r === 'leader' ? '组长' : r === 'member' ? '成员' : r || '')
const mapParticipant = (m = {}) => {
  const stu = m.student || {}
  const profile = stu.student_profile || stu.profile || {}
  const schoolRaw = stu.school || profile.school
  const school =
    typeof schoolRaw === 'string'
      ? schoolRaw
      : schoolRaw && typeof schoolRaw === 'object'
        ? schoolRaw.name || schoolRaw.title || schoolRaw.label || ''
        : ''
  return {
    id: m.id ?? `${stu.id ?? 'x'}`,
    userId: stu.id,
    userLogin: stu.username,
    name: stu.real_name || stu.username || '成员',
    avatar: stu.avatar || DEFAULT_AVATAR,
    role: normalizeRole(m.role),
    phone: stu.phone || profile.phone || '', // 电话
    school, // 学校（仅名称）
    major: stu.major || profile.major || '', // 专业
    grade: stu.grade || profile.grade || '', // 年级
    email: stu.email || profile.email || '', // 邮箱
    status: m.status_text || m.status || ''
  }
}

const allStudents = computed(() => project.value?.students || [])
const myStudentIndex = computed(() =>
  allStudents.value.findIndex(
    (s) => s.userId && myUserId.value != null && Number(s.userId) === Number(myUserId.value)
  )
)
const myStudent = computed({
  get: () => (myStudentIndex.value >= 0 ? allStudents.value[myStudentIndex.value] : null),
  set: (val) => {
    if (myStudentIndex.value >= 0) allStudents.value[myStudentIndex.value] = val
  }
})
// 参与者 userId 集合，用于推断“是否企业评论”
const participantUserIdSet = computed(() => {
  const set = new Set()
  for (const s of allStudents.value) {
    const n = Number(s.userId)
    if (!Number.isNaN(n)) set.add(n)
  }
  return set
})

const isLeader = computed(() => {
  const uid = myUserId.value
  const uname = (myUsername.value || '').trim().toLowerCase()
  if (uid == null && !uname) return false
  const ids = (project.value?.leaderIds || []).map((n) => Number(n)).filter((n) => !Number.isNaN(n))
  const names = (project.value?.leaderUsernames || [])
    .map((s) =>
      String(s || '')
        .trim()
        .toLowerCase()
    )
    .filter(Boolean)
  if (uid != null && ids.includes(Number(uid))) return true
  if (uname && names.includes(uname)) return true
  const me = myStudent.value
  return !!me && String(me.role || '').includes('组长')
})
const isParticipant = computed(() => !!myStudent.value)
const canSubmitDeliverable = computed(() => isParticipant.value || isLeader.value)

// 可转让的成员列表（排除当前组长）
const transferableMembers = computed(() => {
  return allStudents.value.filter((s) => {
    // 排除当前组长
    if (String(s.role || '').includes('组长')) return false
    // 只包含已批准的成员
    if (String(s.status || '').toLowerCase() !== 'approved') return false
    return true
  })
})

// 仅当项目状态为 recruiting 时允许外部发送加入申请（此处为标志供前端逻辑引用）
const isRecruiting = computed(() => project.value?.rawStatus === 'recruiting')
// 可申请加入标记（如果后续在其它组件里引用，可通过 props/事件传递）
const canApplyJoin = computed(() => isRecruiting.value)

const groupedStudents = computed(() => {
  const list = allStudents.value.slice()
  const groups = {}
  list.forEach((s) => {
    const k = s.role && roleCategories.includes(s.role) ? s.role : '其他'
    if (!groups[k]) groups[k] = []
    groups[k].push(s)
  })
  const ordered = {}
  roleCategories.forEach((rc) => {
    if (groups[rc]?.length) ordered[rc] = groups[rc]
  })
  if (groups['其他']?.length) ordered['其他'] = groups['其他']
  return ordered
})
const pendingApplicants = computed(() => project.value?.pendingApplicants || [])

// 新增：打开“移除成员”弹窗
function openRemoveMember(row) {
  if (!isLeader.value) {
    ElMessage.warning('仅组长可移除成员')
    return
  }
  // 负责人不可被移除；仅移除已加入成员
  if (String(row.role || '').includes('组长')) {
    ElMessage.info('负责人不能被移除')
    return
  }
  if (String(row.status || '').toLowerCase() !== 'approved') {
    ElMessage.info('仅可移除已加入的成员')
    return
  }
  removeTarget.value = row
  removeReason.value = ''
  removeDialogVisible.value = true
}

// 新增：确认移除成员（后端置为 left）
async function confirmRemoveMember() {
  const pid = projectId
  const target = removeTarget.value
  if (!pid || !target?.id) return

  removing.value = true
  try {
    await updateParticipantStatus(pid, target.id, {
      status: 'left',
      reason: removeReason.value || '由负责人移除'
    })
    ElMessage.success('已移除该成员')

    // 从本地项目成员列表移除，驱动 UI 更新
    const list = Array.isArray(project.value?.students) ? project.value.students : []
    const idx = list.findIndex((p) => String(p.id) === String(target.id))
    if (idx >= 0) list.splice(idx, 1)

    removeDialogVisible.value = false
  } catch (err) {
    console.error('移除成员失败：', err)
    ElMessage.error('移除失败，请稍后重试')
  } finally {
    removing.value = false
  }
}

// 打开转让组长对话框
function openTransferDialog() {
  if (!isLeader.value) {
    ElMessage.warning('仅组长可转让权限')
    return
  }
  transferForm.newLeaderId = null
  transferForm.transferMessage = ''
  transferDialogVisible.value = true
}

// 确认转让组长
async function confirmTransferLeadership() {
  if (!transferForm.newLeaderId) {
    ElMessage.warning('请选择新负责人')
    return
  }

  const pid = projectId
  if (!pid) return

  transferring.value = true
  try {
    const payload = {
      new_leader_id: transferForm.newLeaderId,
      transfer_message: transferForm.transferMessage || '转让负责人身份'
    }

    const resp = await transferLeadership(pid, payload)
    const ok = resp?.data?.status === 'success'
    const msg = resp?.data?.message || (ok ? '转让成功' : '转让失败')

    if (ok) {
      ElMessage.success(msg)
      transferDialogVisible.value = false
      await load() // 重新加载项目数据
    } else {
      ElMessage.error(msg)
    }
  } catch (err) {
    console.error('转让组长权限失败：', err)
    const serverMsg = extractServerError(err)
    ElMessage.error(serverMsg || '转让失败，请稍后重试')
  } finally {
    transferring.value = false
  }
}

// === 替换 BEGIN：审批申请逻辑（自定义弹窗版） ===
const activeApplication = ref(null)

// 旧变量保留以防其它地方引用（不再在按钮上展示 loading）
const processingApplication = ref(false)

// 新增：两个弹窗可见性与输入内容
const approveDialogVisible = ref(false)
const rejectDialogVisible = ref(false)
const reviewMessageApprove = ref('') // 通过留言
const reviewMessageReject = ref('') // 拒绝留言
const applicationActionLoading = ref(false)

// 打开“通过”弹窗
function openApproveDialog(row) {
  if (!isLeader.value) {
    ElMessage.warning('仅组长可进行审批')
    return
  }
  activeApplication.value = row
  // 默认留言
  reviewMessageApprove.value = '欢迎加入项目团队！'
  approveDialogVisible.value = true
}

// 打开“拒绝”弹窗
function openRejectDialog(row) {
  if (!isLeader.value) {
    ElMessage.warning('仅组长可进行审批')
    return
  }
  activeApplication.value = row
  reviewMessageReject.value = '很抱歉你的申请未能通过。'
  rejectDialogVisible.value = true
}

// 通用提交
async function submitApplicationAction(action) {
  if (!isLeader.value) {
    ElMessage.warning('仅组长可进行审批')
    return
  }
  const pid = projectId
  const participantId = activeApplication.value?.id
  if (!pid || !participantId) {
    ElMessage.error('缺少必要的申请信息')
    return
  }

  const fd = new FormData()
  fd.append('participant_ids', String(participantId))
  fd.append('action', action)

  const msg =
    action === 'approve'
      ? (reviewMessageApprove.value || '欢迎加入项目团队！').trim()
      : (reviewMessageReject.value || '很抱歉你的申请未能通过。').trim()
  if (msg) fd.append('review_message', msg)

  applicationActionLoading.value = true
  try {
    const resp = await handleApplications(pid, fd)
    const ok = resp?.data?.status === 'success'
    const rmsg = resp?.data?.message || (ok ? '操作成功' : '操作失败')
    ok ? ElMessage.success(rmsg) : ElMessage.error(rmsg)
    if (ok) {
      approveDialogVisible.value = false
      rejectDialogVisible.value = false
      activeApplication.value = null
      await load() // 刷新项目数据（含参与者 & 待审核列表）
    }
  } catch (err) {
    console.error('处理申请失败：', err?.response?.data || err)
    ElMessage.error('处理申请失败，请稍后重试')
  } finally {
    applicationActionLoading.value = false
  }
}

function confirmApproveApplication() {
  submitApplicationAction('approve')
}
function confirmRejectApplication() {
  submitApplicationAction('reject')
}
// === 替换 END：审批申请逻辑（自定义弹窗版） ===

const editDialogVisible = ref(false)
const editSaving = ref(false)
const editForm = reactive({ description: '', requirementsText: '' })
const editType = ref('description') // 新增：区分编辑类型，description 或 requirements

// === 项目状态（新增） BEGIN ===
const statusOptions = [
  { value: 'recruiting', label: '招募中' },
  { value: 'in_progress', label: '进行中' },
  { value: 'completed', label: '已完成' }
]

const statusForm = reactive({
  status: ''
})
const statusSaving = ref(false)

// 初始化（项目加载后填充状态）
watch(
  () => project.value?.rawStatus,
  (s) => {
    if (s && !statusSaving.value) {
      statusForm.status = s
    }
  },
  { immediate: true }
)

// 保存项目状态（调用后端接口 updateProject）
const saveProjectStatus = async () => {
  if (!isLeader.value) {
    ElMessage.warning('仅组长可修改项目状态')
    return
  }
  if (!project.value?.id) return
  const newStatus = statusForm.status
  if (!newStatus) {
    ElMessage.warning('请选择项目状态')
    return
  }
  if (newStatus === project.value.rawStatus) {
    ElMessage.info('状态未变化')
    return
  }
  statusSaving.value = true
  try {
    // 仅发送需要更新的字段（后端接口若要求其它必填字段，请在此一并补充）
    await updateProject(project.value.id, { status: newStatus })
    // 本地同步
    project.value.rawStatus = newStatus
    project.value.status = mapStatus(newStatus)
    project.value.joinable = newStatus === 'recruiting'
    ElMessage.success('项目状态已更新')
  } catch (err) {
    console.error('更新项目状态失败：', err?.response?.data || err)
    ElMessage.error('更新项目状态失败，请稍后重试')
    // 回滚选择到旧值
    statusForm.status = project.value.rawStatus
  } finally {
    statusSaving.value = false
  }
}
// === 项目状态（新增） END ===

const openEditDialog = (type = 'description') => {
  if (!isLeader.value) return ElMessage.warning('仅组长可编辑')
  editType.value = type
  const p = project.value || {}
  if (type === 'description') {
    editForm.description = p.detailedDescription || p.briefDescription || ''
    editForm.requirementsText = (p.requirements || []).join('\n')
  } else if (type === 'requirements') {
    editForm.requirementsText = (p.requirements || []).join('\n')
    editForm.description = p.detailedDescription || p.briefDescription || ''
  }
  editDialogVisible.value = true
}

const saveEdit = async () => {
  const p = project.value
  if (!p) return
  let desc = (editForm.description || '').trim()
  let reqs = (editForm.requirementsText || '')
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean)
  // 只更新对应部分
  if (editType.value === 'requirements') {
    desc = p.detailedDescription || p.briefDescription || ''
  }
  if (editType.value === 'description') {
    reqs = p.requirements || []
  }
  const payload = {
    title: p.rawTitle || p.title || '',
    status: p.rawStatus || 'in_progress',
    description: desc,
    brief_description: desc,
    brief: desc,
    requirements: reqs
  }
  editSaving.value = true
  try {
    await updateProject(p.id, payload)
    if (editType.value === 'description') {
      p.briefDescription = desc
      p.detailedDescription = desc
    }
    if (editType.value === 'requirements') {
      p.requirements = reqs
    }
    editDialogVisible.value = false
    ElMessage.success('项目内容已更新')
  } catch (err) {
    console.error('更新项目内容失败：', err)
    ElMessage.error('更新失败，请稍后重试')
  } finally {
    editSaving.value = false
  }
}

const deleteDialogVisible = ref(false)
const deleteLoading = ref(false)
const openDeleteDialog = () => {
  if (!isLeader.value) return ElMessage.warning('仅组长可删除项目')
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  const p = project.value
  if (!p) return
  deleteLoading.value = true
  try {
    await deleteProject(p.id)
    ElMessage.success('项目已删除，团队成员已解散')
    deleteDialogVisible.value = false
    router.replace('/student/my-projects')
  } catch (err) {
    console.error('删除项目失败（后端返回）：', err?.response?.data || err)
    const msg = extractServerError(err) || '删除失败，请稍后重试'
    ElMessage.error(`删除失败：${msg}`)
  } finally {
    deleteLoading.value = false
  }
}

/* 成果提交 */
const submitDialogVisible = ref(false)
const submitLoading = ref(false)
const submitForm = reactive({
  title: '',
  description: '',
  stage_type: '',
  is_milestone: false,
  progress_description: '',
  notes: '',
  cloud_links: '',
  cloud_password: '',
  virtual_folder_path: ''
})
const submitFileList = ref([])

// 新增：本地校验状态（高亮必填未填）
const validationErrors = reactive({
  title: false,
  stage: false,
  content: false // 文件/链接 至少一项
})

const resetSubmitForm = () => {
  submitForm.title = ''
  submitForm.description = ''
  submitForm.stage_type = ''
  submitForm.is_milestone = false
  submitForm.progress_description = ''
  submitForm.notes = ''
  submitForm.cloud_links = ''
  submitForm.cloud_password = ''
  submitForm.virtual_folder_path = ''
  submitFileList.value = []
  validationErrors.title = false
  validationErrors.stage = false
  validationErrors.content = false
}
const beforeSelectFile = () => false
const openSubmitDialog = () => {
  if (!canSubmitDeliverable.value) return ElMessage.warning('仅项目成员可提交成果')
  resetSubmitForm()
  submitDialogVisible.value = true
}

// 兼容版：严格按后端要求构造 FormData，避免 400
const doSubmitDeliverable = async () => {
  if (!projectId) return
  const title = (submitForm.title || '').trim()
  const stage = (submitForm.stage_type || '').trim().toLowerCase()
  const link = (submitForm.cloud_links || '').trim()

  const hasFiles = Array.isArray(submitFileList.value) && submitFileList.value.length > 0
  const hasLink = !!link

  // 前端必填校验：标题、阶段类型、内容（文件或链接至少一项）
  validationErrors.title = !title
  validationErrors.stage = !stage
  validationErrors.content = !hasFiles && !hasLink

  if (validationErrors.title || validationErrors.stage || validationErrors.content) {
    const missing = []
    if (validationErrors.title) missing.push('成果标题')
    if (validationErrors.stage) missing.push('阶段类型')
    if (validationErrors.content) missing.push('上传文件 或 网盘链接（二选一）')
    ElMessage.warning(`请完成必填项：${missing.join('、')}`)
    return
  }

  const fd = new FormData()
  // 必填
  fd.append('title', title)
  fd.append('stage_type', stage)

  // 仅在为 true 时附加布尔字段，false 不发送（避免部分后端误判）
  if (submitForm.is_milestone === true) {
    fd.append('is_milestone', 'true')
  }

  // 可选字段：非空才 append
  {
    const raw = submitForm.description ?? ''
    const trimmed = String(raw).trim()
    // 占位值可按需调整为 '-' 或 '(none)' —— 这里使用“无”
    fd.append('description', trimmed === '' ? '无' : trimmed)
  }

  // 其余可选字段仍按“非空才 append”
  {
    const prog = (submitForm.progress_description || '').trim()
    if (prog) fd.append('progress_description', prog)
  }
  {
    const notes = (submitForm.notes || '').trim()
    if (notes) fd.append('notes', notes)
  }

  const vpath = (submitForm.virtual_folder_path || '').trim()
  if (vpath) fd.append('virtual_folder_path', vpath)

  // 文件/链接二选一：优先使用“本地文件”
  if (hasFiles) {
    submitFileList.value.forEach((f) => {
      const raw = f?.raw
      if (raw instanceof File || raw instanceof Blob) {
        const filename = f.name || raw.name || 'file.bin'
        fd.append('uploaded_files', raw, filename)
      }
    })
  } else if (hasLink) {
    fd.append('cloud_links', link)
    const pwd = (submitForm.cloud_password || '').trim()
    if (pwd) fd.append('cloud_password', pwd)
  }

  // 调试：打印实际 FormData 键值（文件仅打印名称与大小）
  try {
    const entries = Array.from(fd.entries()).map(([k, v]) => [
      k,
      v instanceof File ? `File(${v.name}, ${v.size}B)` : v
    ])
    console.log('[deliverable-submit] FormData entries:', entries)
  } catch {
    /* ignore */
  }

  submitLoading.value = true
  try {
    const resp = await submitDeliverable(projectId, fd)
    const ok = resp?.data?.status === 'success' || resp?.status === 200 || resp?.status === 201
    if (!ok) throw new Error('提交失败')

    ElMessage.success('成果提交成功')
    submitDialogVisible.value = false
    await loadDeliverables()
  } catch (err) {
    // 控制台展示后端返回，便于排障
    console.error('提交成果失败：', err?.response?.data || err)
    const msg = extractServerError(err) || '提交失败，请检查填写内容或稍后重试'
    ElMessage.error(msg)
  } finally {
    submitLoading.value = false
  }
}

/* 成果列表 / 详情 */
const deliverables = ref([])
const deliverablesLoading = ref(false)
const deliverablesPager = reactive({ page: 1, page_size: 50, total: 0 })
const fetchDeliverablesPage = async (page, pageSize) => {
  const resp = await getDeliverables(projectId, {
    page,
    page_size: pageSize,
    include_deprecated: true,
    latest_per_stage: false
  })
  const data = resp?.data?.data || {}
  const list = data?.deliverables || []
  const mapped = list.map((d) => ({
    id: d.id,
    title: d.title,
    stage_type: d.stage_type,
    stage_version: d.stage_version,
    is_milestone: !!d.is_milestone,
    is_updated: !!d.is_updated,
    is_deprecated: !!d.is_deprecated,
    file_count: d.file_count ?? (Array.isArray(d.files) ? d.files.length : 0),
    files: d.files || [],
    submitter: d.submitter,
    last_modifier: d.last_modifier,
    created_at: d.created_at,
    updated_at: d.updated_at
  }))
  const p = data?.pagination || {}
  return {
    list: mapped,
    pagination: {
      current: p.current_page || page,
      totalPages: p.total_pages || 1,
      totalCount: p.total_count || mapped.length,
      pageSize: p.page_size || pageSize
    }
  }
}
const loadDeliverables = async () => {
  if (!projectId) return
  deliverablesLoading.value = true
  try {
    const PAGE_SIZE = 50
    let page = 1
    let all = []
    const first = await fetchDeliverablesPage(page, PAGE_SIZE)
    all = all.concat(first.list)
    const totalPages = first.pagination.totalPages
    for (page = 2; page <= totalPages; page++) {
      const res = await fetchDeliverablesPage(page, PAGE_SIZE)
      all = all.concat(res.list)
    }
    const stageOrder = { final: 3, middle: 2, early: 1 }
    all.sort((a, b) => {
      const sa = stageOrder[String(a.stage_type).toLowerCase()] || 0
      const sb = stageOrder[String(b.stage_type).toLowerCase()] || 0
      if (sa !== sb) return sb - sa
      const ta = new Date(a.updated_at || a.created_at).getTime()
      const tb = new Date(b.updated_at || b.created_at).getTime()
      return tb - ta
    })
    deliverables.value = all
    deliverablesPager.page = 1
    deliverablesPager.page_size = PAGE_SIZE
    deliverablesPager.total = all.length
  } catch (err) {
    console.error('加载成果列表失败：', err)
    deliverables.value = []
    deliverablesPager.total = 0
  } finally {
    deliverablesLoading.value = false
  }
}

const deliverableDetail = ref(null)
const detailDialogVisible = ref(false)
// eslint-disable-next-line no-unused-vars
const openDeliverableDetailDialog = async (row) => {
  if (!row?.id) return
  try {
    const resp = await getDeliverableDetail(projectId, row.id)
    deliverableDetail.value = resp?.data?.data || null
    detailDialogVisible.value = true
  } catch (err) {
    console.error('获取成果详情失败：', err)
    ElMessage.error('获取成果详情失败')
  }
}

const deprecateLoading = ref(false)
// eslint-disable-next-line no-unused-vars
const deprecateDeliverable = async (row) => {
  if (!row?.id) return
  if (!canSubmitDeliverable.value) return ElMessage.warning('无权限')
  try {
    await ElMessageBox.confirm(
      `确定将成果「${row.title}」标记为弃用吗？可在必要时恢复（is_deprecated=false）。`,
      '确认弃用',
      { type: 'warning' }
    )
  } catch {
    return
  }
  deprecateLoading.value = true
  try {
    const fd = new FormData()
    fd.append('is_deprecated', 'true')
    await updateDeliverable(projectId, row.id, fd)
    ElMessage.success('已标记为弃用')
    await loadDeliverables()
  } catch (err) {
    console.error('弃用成果失败：', err)
    ElMessage.error('操作失败，请稍后重试')
  } finally {
    deprecateLoading.value = false
  }
}

import { getEvaluationDetailAllow404 } from '@/api/student/projectEvaluation'
/* ========== 项目评分（最终精简版） ========== */
const evaluation = ref(null)
const evaluationLoading = ref(false)

const loadEvaluation = async () => {
  if (!project.value) return
  // 如果项目尚未被评价，直接显示“暂无评分”且不请求
  if (!project.value.isEvaluated) {
    evaluation.value = null
    return
  }
  evaluationLoading.value = true
  try {
    const resp = await getEvaluationDetailAllow404(project.value.id)
    if (resp.status === 404) {
      evaluation.value = null
    } else {
      evaluation.value = resp?.data?.data || null
    }
  } catch {
    evaluation.value = null
  } finally {
    evaluationLoading.value = false
  }
}

/* 只在切换到评分 tab 时触发；并且先看 isEvaluated */
watch(
  () => activeTab.value,
  (v) => {
    if (v === 'evaluation') loadEvaluation()
  }
)

const STAGES = ['early', 'middle', 'final']
const stageName = (s) =>
  ({ early: '前期', middle: '中期', final: '末期' })[String(s || '').toLowerCase()] || s || '—'

const stageStats = computed(() => {
  const groups = { early: [], middle: [], final: [] }
  ;(deliverables.value || []).forEach((d) => {
    const key = String(d.stage_type || '').toLowerCase()
    if (groups[key]) groups[key].push(d)
  })
  const pickLatest = (arr) =>
    arr
      .slice()
      .sort(
        (a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)
      )[0] || null
  return {
    early: {
      count: groups.early.length,
      milestoneCount: groups.early.filter((x) => x.is_milestone).length,
      latest: pickLatest(groups.early)
    },
    middle: {
      count: groups.middle.length,
      milestoneCount: groups.middle.filter((x) => x.is_milestone).length,
      latest: pickLatest(groups.middle)
    },
    final: {
      count: groups.final.length,
      milestoneCount: groups.final.filter((x) => x.is_milestone).length,
      latest: pickLatest(groups.final)
    }
  }
})
const finishedStagesCount = computed(
  () => STAGES.filter((k) => (stageStats.value[k]?.count || 0) > 0).length
)
const overallProgress = computed(() =>
  Math.round((finishedStagesCount.value / STAGES.length) * 100)
)
const activeStep = computed(() => {
  // 无前期提交：停在第 0 步
  if (stageStats.value.early.count === 0) return 0
  // 有前期，无中期：停在第 1 步
  if (stageStats.value.middle.count === 0) return 1
  // 末期已有提交：全部完成（设置为 steps 数量 3，使三个圆都进入 finished 状态）
  if (stageStats.value.final.count > 0) return 3
  // 仅差末期：当前活跃在第三步
  return 2
})

const stageLists = computed(() => {
  const groups = { early: [], middle: [], final: [] }
  ;(deliverables.value || []).forEach((d) => {
    const key = String(d.stage_type || '').toLowerCase()
    if (groups[key]) groups[key].push(d)
  })
  const sortDesc = (arr) =>
    arr
      .slice()
      .sort(
        (a, b) => new Date(b.updated_at || b.created_at) - new Date(a.updated_at || a.created_at)
      )
  return {
    early: sortDesc(groups.early),
    middle: sortDesc(groups.middle),
    final: sortDesc(groups.final)
  }
})

/* 阶段详情面板 */
const stagePanelVisible = ref(false)
const stagePanel = reactive({
  deliverable: null,
  loadingDetail: false,
  loadingComments: false,
  comments: [], // 顶级评语
  newCommentText: '', // 仅企业可发布
  sendingNew: false
})

const openDeliverablePanel = async (d) => {
  if (!d?.id) return
  stagePanelVisible.value = true
  stagePanel.deliverable = null
  stagePanel.comments = []
  stagePanel.newCommentText = ''
  stagePanel.loadingDetail = true
  try {
    const resp = await getDeliverableDetail(projectId, d.id)
    stagePanel.deliverable = resp?.data?.data || d
  } catch (err) {
    console.error('加载阶段提交详情失败：', err)
    stagePanel.deliverable = d
  } finally {
    stagePanel.loadingDetail = false
  }
  await loadStagePanelComments()
}

async function loadStagePanelComments() {
  const d = stagePanel.deliverable
  if (!d || !d.id) {
    console.warn('[comments] deliverable missing when loading comments', d)
    return
  }
  stagePanel.loadingComments = true
  try {
    const params = {
      page: 1,
      page_size: 100,
      deliverable_id: d.id
    }
    console.debug('[comments] fetching', params)
    const resp = await getProjectComments(projectId, params)
    const dataLayer = resp?.data || {}
    const rawContainer = dataLayer.data || dataLayer
    const rawList = rawContainer.comments || rawContainer.results || []
    console.debug('[comments] raw response container:', rawContainer)
    console.debug('[comments] raw list length:', rawList.length)

    if (!Array.isArray(rawList)) {
      console.error('[comments] rawList not array =>', rawList)
      stagePanel.comments = []
      return
    }

    stagePanel.comments = rawList.map((c) => {
      const rawAuthor = c.author_info || {}
      const userType = rawAuthor.user_type
      const authorId = rawAuthor.id
      const inParticipants =
        authorId !== undefined && participantUserIdSet.value.has(Number(authorId))
      const heuristicOrg =
        !!rawAuthor.organization_name ||
        !!rawAuthor.org_name ||
        rawAuthor.is_org === true ||
        rawAuthor.is_organization === true
      const finalAuthorIsOrg =
        userType === 'organization' ||
        heuristicOrg ||
        (!userType && !inParticipants) ||
        (userType !== 'student' && !inParticipants)

      return {
        id: c.id,
        content: c.content,
        author: rawAuthor.real_name || rawAuthor.username || '用户',
        authorUsername: rawAuthor.username || '',
        avatar: rawAuthor.avatar || '',
        created_at: c.created_at,
        authorIsOrg: finalAuthorIsOrg
      }
    })
    console.debug('[comments] mapped list length:', stagePanel.comments.length)
  } catch (err) {
    console.error('[comments] load failed:', err)
    ElMessage.error('加载评语失败')
    stagePanel.comments = []
  } finally {
    stagePanel.loadingComments = false
  }
}

const projectStatusMap = {
  recruiting: '招募中',
  in_progress: '进行中',
  ongoing: '进行中',
  suspended: '已暂停',
  paused: '已暂停',
  completed: '已完成',
  cancelled: '已取消'
}
const mapStatus = (s) => projectStatusMap[s] || s || '进行中'
const formatDate = (s) => {
  if (!s) return ''
  try {
    const d = new Date(s)
    return isNaN(d.getTime()) ? String(s) : d.toLocaleString()
  } catch {
    /* ignore */ void 0
    return String(s)
  }
}

// === 新增 BEGIN：格式化到 分 的时间（YYYY-MM-DD HH:MM） ===
function formatDateMinute(s) {
  if (!s) return ''
  try {
    const d = new Date(s)
    if (isNaN(d.getTime())) return String(s)
    const pad = (n) => String(n).padStart(2, '0')
    return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
  } catch {
    return String(s)
  }
}
// === 新增 END ===

/* === 隶属主体兜底工具（新增） === */
function getSavedAffiliationLocal(projectId) {
  try {
    return localStorage.getItem(`project:aff:${projectId}`) || ''
  } catch {
    return ''
  }
}
function parseAffiliationFromDescription(desc) {
  if (!desc) return ''
  // 支持 “团队，” “团队,” “团队：” “团队:” “团队。” “团队.” 后面跟空白
  const m = desc.match(/^(.+?)团队[，,：:。.\s]/)
  return m ? m[1].trim() : ''
}

// 替换 buildViewModel(...) 为以下实现
const buildViewModel = (detail, participantsPayload) => {
  // 统一规范化“申请中”项：只展示 application_message
  const normalizePending = (a) => {
    const stu = a?.student || {}
    return {
      // 审批接口要求 participant_ids（参与者申请记录ID）
      id: a?.id ?? a?.participant_id ?? stu?.id ?? '',
      // 只保留用户填写的信息（申请理由）
      reason: a?.application_message || '' // 仅取 application_message，不再混入其他字段
    }
  }

  // 修复：读取后端真实字段名 pending_applications（保留向后兼容）
  const pendingRaw =
    participantsPayload?.pending_applications ??
    participantsPayload?.pendingApplicants ??
    detail?.pending_applications ??
    []

  // === 替换 BEGIN：pendingApplicants 归一化（精简字段 + 只取最终理由） ===
  const pendingApplicants = Array.isArray(pendingRaw)
    ? pendingRaw
        .filter((a) => a && typeof a === 'object')
        .map((a) => {
          const stu = a.student || {}
          // 学校只展示学校名，不保留对象或其它结构
          const schoolNameRaw = stu.school
          const schoolName =
            typeof schoolNameRaw === 'string'
              ? schoolNameRaw
              : schoolNameRaw && typeof schoolNameRaw === 'object'
                ? schoolNameRaw.name || schoolNameRaw.title || ''
                : ''
          const appliedAt = a.applied_at || a.appliedAt || ''
          return {
            id: a.id,
            participantId: a.id,
            userId: stu.id,
            avatar: stu.avatar || DEFAULT_AVATAR,
            real_name: stu.real_name || stu.username || '',
            name: stu.real_name || stu.username || '',
            school_name: schoolName,
            major: stu.major || '',
            grade: stu.grade || '',
            // 电话/邮箱可能不在列表接口，后续 enrich 补齐
            phone: stu.phone || '',
            email: stu.email || '',
            // 申请理由：仅取 application_message，不拼接其它字段
            reason: a.application_message || '',
            applied_at: appliedAt,
            applied_at_fmt: formatDateMinute(appliedAt),
            status: a.status || 'pending',
            review_message: a.review_message || '',
            _needDetail: !(stu.phone && stu.email), // 仍缺联系方式则补拉
            _detailLoaded: false
          }
        })
    : []
  // === 替换 END ===

  // ===== 合并参与者：detail.participants 优先（含更完整联系方式），再用 participantsPayload 补充 =====
  const participantsDetail = Array.isArray(detail?.participants) ? detail.participants : []
  const participantsFromPayload = participantsPayload?.participants || participantsPayload || []

  const mergedMap = new Map()
  // 先放 payload（可能含状态字段等）
  for (const p of participantsFromPayload) {
    if (p && p.id != null) mergedMap.set(p.id, { ...p })
  }
  // 用 detail 覆盖（提供完整 email / phone 等）
  for (const p of participantsDetail) {
    if (!p || p.id == null) continue
    const prev = mergedMap.get(p.id)
    mergedMap.set(p.id, prev ? { ...prev, ...p } : { ...p })
  }
  const participants = Array.from(mergedMap.values())
  const students = participants.map((p) => mapParticipant(p))

  // 负责人信息（保持原逻辑）
  const leaderIds = []
  const leaderUsernames = []
  const L = detail?.leader || {}
  if (typeof L?.id === 'number') leaderIds.push(L.id)
  if (typeof L?.user?.id === 'number') leaderIds.push(L.user.id)
  if (typeof L?.student?.id === 'number') leaderIds.push(L.student.id)
  if (typeof L?.user_id === 'number') leaderIds.push(L.user_id)
  if (L?.username) leaderUsernames.push(L.username)
  if (L?.user?.username) leaderUsernames.push(L.user.username)

  const me =
    students.find((s) => myUserId.value != null && Number(s.userId) === Number(myUserId.value)) ||
    null

  return {
    isEvaluated: !!detail.is_evaluated,
    rawTitle: detail.title,
    rawStatus: detail.status,
    id: detail.id,
    leaderIds,
    leaderUsernames,
    status: mapStatus(detail.status),
    publisher: detail.leader?.real_name || detail.leader?.username || detail.publisher || '—',
    joinDate: formatDate(detail.joined_at || detail.created_at),
    role: me?.role || '成员',
    title: detail.title || detail.name || '未命名项目',
    parentDemand: detail.requirement
      ? { id: detail.requirement.id, title: detail.requirement.title }
      : { id: undefined, title: '' },
    affiliation:
      detail.affiliation ||
      detail.requirement?.organization_name ||
      detail.requirement?.title ||
      '',
    briefDescription:
      detail.brief ||
      detail.brief_description ||
      (detail.description ? String(detail.description).slice(0, 120) : ''),
    detailedDescription: detail.description || '',
    requirements: Array.isArray(detail.requirements)
      ? detail.requirements
      : (detail.requirement_items || []).map((it) => it.name || it.text).filter(Boolean),
    domain: detail.domain || detail.category || '',
    tags: detail.tags || [],
    deadline: formatDate(detail.deadline || detail.end_date),
    budget: detail.budget || '',
    teamSizeNeeded: detail.team_size_needed || detail.max_participants || 0,
    students,
    // 仅包含申请理由（用户填写的 application_message）

    resources: detail.resources || [],
    deliverables: detail.deliverables || [],
    joinable: detail.status === 'recruiting',
    requirementPublisher: {
      username:
        (detail.requirement &&
          (detail.requirement.publish_people ||
            detail.requirement.publisher ||
            detail.requirement.publisher_username)) ||
        detail.publish_people ||
        detail.publisher ||
        detail.publisher_username ||
        '',
      phone:
        (detail.requirement &&
          (detail.requirement.publisher_phone ||
            detail.requirement.publish_phone ||
            detail.requirement.publisher_mobile)) ||
        detail.publisher_phone ||
        detail.publish_phone ||
        detail.publisher_mobile ||
        '',
      email:
        (detail.requirement &&
          (detail.requirement.publisher_email ||
            detail.requirement.publish_email ||
            detail.requirement.publisher_contact_email)) ||
        detail.publisher_email ||
        detail.publish_email ||
        detail.publisher_contact_email ||
        ''
    },
    pendingApplicants
  }
}

// === 新增 BEGIN：补充 pendingApplicants 详情（电话/email 等） ===
const enrichingApplicants = ref(false)

async function enrichPendingApplicants(p) {
  if (!p || !Array.isArray(p.pendingApplicants)) return
  const list = p.pendingApplicants.filter((x) => x._needDetail && !x._detailLoaded && x.id)
  if (!list.length) return
  enrichingApplicants.value = true
  try {
    // 顺序执行避免对后端造成突发压力（可选：也可 Promise.all 并发）
    for (const item of list) {
      try {
        const resp = await getParticipantDetail(p.id, item.participantId)
        const data = resp?.data?.data || {}
        const stu = data.student || {}

        const schoolNameRaw = stu.school
        const schoolName =
          typeof schoolNameRaw === 'string'
            ? schoolNameRaw
            : schoolNameRaw && typeof schoolNameRaw === 'object'
              ? schoolNameRaw.name || schoolNameRaw.title || ''
              : ''
        // 仅对后端真正提供的字段进行覆盖
        item.phone = stu.phone || item.phone
        item.email = stu.email || item.email
        item.school_name = stu.school || item.school_name
        item.major = stu.major || item.major
        item.grade = stu.grade || item.grade
        // 有些后端 detail 里可能再次给出 application_message
        item.reason = data.application_message || item.reason
        item.review_message = data.review_message || item.review_message
        item.applied_at = data.applied_at || item.applied_at
        item._detailLoaded = true
      } catch (e) {
        console.warn('[enrichPendingApplicants] 获取详情失败 participantId=', item.participantId, e)
      }
    }
  } finally {
    enrichingApplicants.value = false
  }
}
// === 新增 END ===

// ===== 新增：强制为所有已加入成员拉取详情，确保邮箱 / 电话补齐（服务器端接口 getParticipantDetail） =====
async function enrichParticipantContacts(p) {
  if (!p || !Array.isArray(p.students) || !p.id) return
  for (const m of p.students) {
    const participantId = Number(m.id)
    if (!participantId || Number.isNaN(participantId)) continue
    try {
      const resp = await getParticipantDetail(p.id, participantId)
      const data = resp?.data?.data || {}
      const s = data.student || {}
      const pick = (...keys) =>
        keys
          .map((k) => (s && s[k] != null && s[k] !== '' ? s[k] : data[k]))
          .find((v) => v != null && v !== '')
      const email =
        pick('email', 'contact_email', 'mail') ||
        (typeof s.contact === 'object' ? s.contact.email : '')
      const phone =
        pick('phone', 'mobile', 'mobile_phone') ||
        (typeof s.contact === 'object' ? s.contact.phone : '')
      if (email) m.email = email
      if (phone) m.phone = phone
      if (s.major && !m.major) m.major = s.major
      if (s.grade && !m.grade) m.grade = s.grade
      if (s.real_name && !m.name) m.name = s.real_name
    } catch (e) {
      console.warn('[enrichParticipantContacts] 详情获取失败 participant_id=', participantId, e)
    }
  }
}

// MyProjectDetail.vue  资源区域新增开始
// ========== 企业资源规范化 & 合并 ==========

// 复用格式化大小
function formatFileSize(bytes) {
  if (!bytes || bytes <= 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 规范化组织资源（与需求关注页面一致风格）
function mapOrgResource(raw) {
  const sizeSum = Array.isArray(raw.files)
    ? raw.files.reduce((acc, f) => acc + (Number(f.size) || 0), 0)
    : 0
  return {
    id: raw.id, // 数字ID -> 真实组织资源
    source: 'organization',
    name: raw.title || raw.name || '',
    title: raw.title || raw.name || '',
    description: raw.description || '',
    type: raw.type || '',
    files: Array.isArray(raw.files) ? raw.files : [],
    size: sizeSum,
    created_at: raw.created_at || raw.updated_at || '',
    uploadedAt: raw.created_at || raw.updated_at || '',
    status: raw.status || '',
    downloads: raw.downloads ?? 0,
    views: raw.views ?? 0,
    synthetic: false, // 非本地合成
    downloading: false
  }
}

// 需求详情里的 files -> 伪资源
function buildRequirementFileResources(reqDetail) {
  const arr = reqDetail?.files
  if (!Array.isArray(arr) || !arr.length) return []
  return arr
    .map((f, idx) => {
      if (!f) return null
      const isObj = typeof f === 'object'
      const fileName = isObj ? f.name : String(f).split('/').pop()
      const url = isObj ? f.url || f.download_url : f
      return {
        id: `reqfile-${reqDetail.id}-${idx}`,
        source: 'requirement-file',
        name: fileName || `附件_${idx + 1}`,
        title: fileName || `附件_${idx + 1}`,
        description: '需求附件文件',
        type: isObj ? f.type || 'file' : 'file',
        files: [
          {
            id: `${reqDetail.id}-${idx}`,
            name: fileName,
            path: url,
            url,
            download_url: url,
            size: isObj ? Number(f.size) || 0 : 0,
            is_folder: false
          }
        ],
        size: isObj ? Number(f.size) || 0 : 0,
        created_at: isObj ? f.created_at || '' : '',
        uploadedAt: isObj ? f.created_at || '' : '',
        status: 'published',
        synthetic: true,
        downloading: false
      }
    })
    .filter(Boolean)
}

// 需求详情里的 resources -> 伪资源（对象 / 字符串 混合）
function buildRequirementInnerResources(reqDetail) {
  const arr = reqDetail?.resources
  if (!Array.isArray(arr) || !arr.length) return []
  return arr
    .map((r, idx) => {
      if (r && typeof r === 'object') {
        const fileArr = Array.isArray(r.files) ? r.files : []
        const sizeSum = fileArr.reduce((s, f) => s + (Number(f.size) || 0), 0)
        return {
          id: `reqres-${reqDetail.id}-${r.id || idx}`,
          source: 'requirement-resource',
          name: r.title || r.name || `需求资源_${idx + 1}`,
          title: r.title || r.name || `需求资源_${idx + 1}`,
          description: r.description || '需求附属资源',
          type: r.type || 'resource',
          files: fileArr,
          size: sizeSum,
          created_at: r.created_at || '',
          uploadedAt: r.created_at || r.updated_at || '',
          status: r.status || '',
          synthetic: true,
          downloading: false
        }
      }
      if (typeof r === 'string') {
        const fileName = r.split('/').pop()
        return {
          id: `reqresstr-${reqDetail.id}-${idx}`,
          source: 'requirement-resource-string',
          name: fileName || `需求资源_${idx + 1}`,
          title: fileName || `需求资源_${idx + 1}`,
          description: '需求资源（链接）',
          type: 'resource',
          files: [
            {
              id: `${reqDetail.id}-rs-${idx}`,
              name: fileName,
              path: r,
              url: r,
              download_url: r,
              size: 0,
              is_folder: false
            }
          ],
          size: 0,
          created_at: '',
          uploadedAt: '',
          status: 'published',
          synthetic: true,
          downloading: false
        }
      }
      return null
    })
    .filter(Boolean)
}

// 拉取组织全部资源（分页）
async function fetchAllOrganizationResources(orgId, pageSize = 50, maxPages = 10) {
  if (!orgId) return []
  let page = 1
  let totalPages = 1
  const acc = []
  while (page <= totalPages && page <= maxPages) {
    try {
      const resp = await getResourceList({
        organization_id: orgId,
        page,
        page_size: pageSize,
        status: 'published,unpublished'
      })
      if (resp?.data?.status !== 'success') break
      const data = resp.data.data || {}
      acc.push(...(data.resources || []))
      totalPages = data.pagination?.total_pages || 1
      page += 1
    } catch {
      break
    }
  }
  return acc
}

// 计算文件类型（扩展名）
function getRowFileType(row) {
  const files = Array.isArray(row?.files) ? row.files : []
  const f = files[0]
  const pickExt = (s) => {
    if (!s || typeof s !== 'string') return ''
    const i = s.lastIndexOf('.')
    return i >= 0 ? s.slice(i + 1).toLowerCase() : ''
  }
  const nameExt = pickExt(f?.name)
  const pathExt = pickExt(f?.path || f?.url || f?.download_url)
  return nameExt || pathExt || row?.type || '未知'
}

// 下载 / 打开资源
async function openProjectResource(row) {
  if (!row) return
  row.downloading = true
  try {
    // 伪资源：直接用第一个文件的下载/直链
    if (row.synthetic) {
      const f = Array.isArray(row.files) && row.files.length ? row.files[0] : null
      const link = f?.download_url || f?.url || f?.path
      if (!link) {
        ElMessage.info('暂无可下载文件')
        return
      }
      window.open(link, '_blank')
      return
    }
    // 真实组织资源：调用下载接口
    if (typeof row.id === 'number') {
      const resp = await downloadResource(row.id)
      const data = resp?.data?.data || {}
      const files = Array.isArray(data.files) ? data.files : []
      if (!files.length) {
        ElMessage.info('暂无文件')
        return
      }
      const first = files[0]
      const url = first.download_url || first.url || first.path
      if (!url) {
        ElMessage.info('下载地址不可用')
        return
      }
      window.open(url, '_blank')
      return
    }
    ElMessage.info('资源数据不完整')
  } catch (e) {
    console.error('下载失败', e)
    ElMessage.error('下载失败')
  } finally {
    row.downloading = false
  }
}
// ========== 企业资源规范化 & 合并 结束 ==========

const loading = ref(false)
// MyProjectDetail.vue  替换 loadEnterpriseResources 函数体
const loadEnterpriseResources = async () => {
  enterpriseResources.value = []
  const reqId = extractRequirementIdFromProject(project.value)
  if (!reqId) return

  let requirementDetail = null
  try {
    const resp = await getRequirementDetail(reqId)
    if (resp?.data?.status === 'success') {
      requirementDetail = resp.data.data || {}
    }
  } catch {
    /* ignore */
  }
  if (!requirementDetail) {
    enterpriseResources.value = []
    return
  }
  // === 新增：补充需求发布人信息到 project.requirementPublisher ===
  try {
    if (project.value) {
      const pubUser =
        requirementDetail.publish_people ||
        requirementDetail.publisher ||
        requirementDetail.publisher_username ||
        ''
      const pubPhone =
        requirementDetail.publisher_phone ||
        requirementDetail.publish_phone ||
        requirementDetail.publisher_mobile ||
        ''
      const pubEmail =
        requirementDetail.publisher_email ||
        requirementDetail.publish_email ||
        requirementDetail.publisher_contact_email ||
        ''
      project.value.requirementPublisher = {
        username: pubUser || project.value.requirementPublisher?.username || '',
        phone: pubPhone || project.value.requirementPublisher?.phone || '',
        email: pubEmail || project.value.requirementPublisher?.email || ''
      }
    }
  } catch (e) {
    console.warn('[requirementPublisher] enrich failed', e)
  }

  // 需求自身附件 & 内部资源
  const reqFileRes = buildRequirementFileResources(requirementDetail)
  const reqInnerRes = buildRequirementInnerResources(requirementDetail)

  // 组织全部资源
  const orgId =
    requirementDetail.organization_id ||
    requirementDetail.organizationId ||
    requirementDetail.organization?.id ||
    project.value?.requirement?.organization_id ||
    project.value?.requirement?.organization?.id ||
    null

  let orgResources = []
  if (orgId) {
    try {
      const orgList = await fetchAllOrganizationResources(orgId, 50, 8)
      orgResources = orgList.map(mapOrgResource)
    } catch {
      orgResources = []
    }
  }

  // 合并 & 去重
  const combined = [...reqFileRes, ...reqInnerRes, ...orgResources]
  const uniq = new Map()
  combined.forEach((r) => {
    const key = `${r.source}::${r.id}`
    if (!uniq.has(key)) uniq.set(key, r)
  })
  enterpriseResources.value = Array.from(uniq.values())
}

const load = async () => {
  if (!projectId || Number.isNaN(projectId)) {
    ElMessage.warning('缺少项目ID')
    return
  }
  loading.value = true
  try {
    const [detailRes, partRes] = await Promise.all([
      getProjectDetail(projectId),
      getProjectParticipants(projectId)
    ])
    const detail = detailRes?.data?.data || detailRes?.data || {}
    const participantsPayload = partRes?.data?.data || partRes?.data || []
    project.value = buildViewModel(detail, participantsPayload)
    await enrichPendingApplicants(project.value) // 新增：补齐申请人联系方式等
    //await enrichParticipantContacts(project.value) // 补齐已加入成员邮箱/电话
    await loadEnterpriseResources()
    await loadDeliverables()
  } catch (err) {
    console.error('加载项目详情失败:', err)
    ElMessage.error('加载项目详情失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await load()
  await loadEvaluation()
})
</script>

<template>
  <div class="my-project-detail" v-if="project">
    <div class="page-header">
      <div class="left">
        <el-button class="back-btn" :icon="ArrowLeft" plain @click="goBackToList"
          >返回我的项目</el-button
        >
        <div class="title-wrap">
          <div class="name">{{ project.title }}</div>
          <!-- 状态标签移除：按需求去掉“招募中”等状态字样 -->
          <el-tag
            v-if="project.status"
            size="small"
            :type="
              project.rawStatus === 'recruiting'
                ? 'warning'
                : project.rawStatus === 'completed'
                  ? 'success'
                  : 'info'
            "
            effect="light"
            class="project-status-tag"
          >
            {{ project.status }}
          </el-tag>
        </div>
        <div class="meta">
          <span
            >隶属需求：<b>{{ project.parentDemand?.title || '—' }}</b></span
          >
          <span class="sep"></span>
          <span
            >隶属主体：<b>{{ project.affiliation || '—' }}</b></span
          >
          <span class="sep"></span>
          <span
            >项目创建人：<b>{{ project.publisher }}</b></span
          >
          <span class="sep"></span>
          <span
            >需求发布人：<b>{{ project.requirementPublisher?.username || '—' }}</b></span
          >
          <span class="sep"></span>
          <span>
            发布人联系方式：
            <b>
              <template
                v-if="project.requirementPublisher?.phone || project.requirementPublisher?.email"
              >
                {{ project.requirementPublisher?.phone || '' }}
                <template
                  v-if="project.requirementPublisher?.phone && project.requirementPublisher?.email"
                >
                  /
                </template>
                {{ project.requirementPublisher?.email || '' }}
              </template>
              <template v-else>—</template>
            </b>
          </span>
          <span class="sep"></span>
          <span
            >我的角色：<b>{{ project.role }}</b></span
          >
          <span class="sep"></span>
          <span>加入时间：{{ project.joinDate }}</span>
          <!-- 去掉领域 / 截止时间 / 预算 / 团队需要人数显示 -->
        </div>
        <div class="tags" v-if="project.tags?.length">
          <el-tag v-for="t in project.tags" :key="t" size="small" effect="plain">{{ t }}</el-tag>
        </div>
      </div>
      <div class="right">
        <div class="right project-actions">
          <el-button
            v-if="canSubmitDeliverable"
            class="action-btn submit-btn"
            type="primary"
            size="large"
            @click="openSubmitDialog"
            >提交阶段成果</el-button
          >
        </div>
      </div>
    </div>

    <div class="subnav">
      <div class="nav-grid">
        <div
          v-for="n in navs"
          :key="n.key"
          class="nav-btn"
          :class="{ active: activeTab === n.key }"
          role="button"
          tabindex="0"
          @click="activeTab = n.key"
          @keydown.enter.prevent="activeTab = n.key"
          @keydown.space.prevent="activeTab = n.key"
        >
          <div class="icon-wrap">
            <el-icon :size="24"><component :is="n.icon" /></el-icon>
          </div>
          <div class="texts">
            <div class="t1">{{ n.title }}</div>
            <div class="t2">{{ n.desc }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="content-area">
      <!-- 项目介绍 -->
      <div v-show="activeTab === 'intro'" class="panel">
        <section class="section-card accent-blue">
          <header class="section-hd header-with-action">
            <div class="title">项目介绍（会对外展示）</div>
            <el-button
              v-if="isLeader"
              link
              type="primary"
              class="card-edit-btn"
              @click="openEditDialog('description')"
              >编辑</el-button
            >
          </header>
          <div class="section-bd">
            <p v-if="project.detailedDescription || project.briefDescription" class="desc">
              {{ project.detailedDescription || project.briefDescription }}
            </p>
            <el-empty v-else description="暂无项目介绍" :image-size="60" />
          </div>
        </section>
        <!-- 具体要求（缩小高度） -->
        <section class="section-card accent-cyan compact-req">
          <header class="section-hd header-with-action">
            <div class="title">具体要求</div>
            <el-button
              v-if="isLeader"
              link
              type="primary"
              class="card-edit-btn"
              @click="openEditDialog('requirements')"
              >编辑</el-button
            >
          </header>
          <div class="section-bd">
            <ul class="req-list" v-if="(project.requirements || []).length">
              <li v-for="(r, idx) in project.requirements" :key="idx">
                <span class="dot"></span>
                <span class="text">{{ r }}</span>
              </li>
            </ul>
            <el-empty v-else description="暂无具体要求" :image-size="50" />
          </div>
        </section>

        <!-- 阶段性成果进展 -->
        <section class="section-card accent-indigo">
          <header class="section-hd">
            <div class="title">阶段性成果进展（右上角进行提交）</div>
          </header>
          <!-- 新增：提示说明 -->
          <div class="progress-hint">
            <p class="p-title">进展说明</p>
            <p class="p-text">
              此进度基于各阶段（前期 / 中期 / 末期）已提交的成果数量（含里程碑标记）。
              里程碑仅作为标识，不单独计算百分比。请在不同阶段按实际完成情况及时提交阶段性成果。
            </p>
          </div>
          <div class="section-bd">
            <el-steps
              :active="activeStep"
              align-center
              :finish-status="stageStats.final.count > 0 ? 'success' : 'process'"
            >
              <el-step
                title="前期"
                :description="
                  stageStats.early.count > 0
                    ? '提交 ' +
                      stageStats.early.count +
                      ' 次' +
                      (stageStats.early.milestoneCount
                        ? ` · 里程碑 ${stageStats.early.milestoneCount}`
                        : '')
                    : '未提交'
                "
              />
              <el-step
                title="中期"
                :description="
                  stageStats.middle.count > 0
                    ? '提交 ' +
                      stageStats.middle.count +
                      ' 次' +
                      (stageStats.middle.milestoneCount
                        ? ` · 里程碑 ${stageStats.middle.milestoneCount}`
                        : '')
                    : '未提交'
                "
              />
              <el-step
                title="末期"
                :description="
                  stageStats.final.count > 0
                    ? '提交 ' +
                      stageStats.final.count +
                      ' 次' +
                      (stageStats.final.milestoneCount
                        ? ` · 里程碑 ${stageStats.final.milestoneCount}`
                        : '')
                    : '未提交'
                "
              />
            </el-steps>

            <div class="mt12 stage-grid">
              <!-- 前期 -->
              <el-card shadow="never">
                <template #header>
                  <div class="card-hd">
                    <span>前期提交</span>
                  </div>
                </template>

                <div v-if="stageLists.early.length" class="deliverable-list">
                  <div
                    v-for="d in stageLists.early"
                    :key="d.id"
                    class="deliverable-item"
                    @click="openDeliverablePanel(d)"
                  >
                    <div class="row1">
                      <b class="title">{{ d.title }}</b>
                    </div>
                    <div class="row2 tiny muted">
                      {{ d.stage_version || '' }} · {{ d.updated_at || d.created_at }}
                    </div>
                    <div class="row3 tags">
                      <el-tag v-if="d.is_milestone" size="small" type="warning" effect="plain"
                        >里程碑</el-tag
                      >
                      <el-tag
                        v-if="d.is_updated && !d.is_deprecated"
                        size="small"
                        type="success"
                        effect="plain"
                        >有更新</el-tag
                      >
                      <el-tag v-if="d.is_deprecated" size="small" type="info" effect="plain"
                        >已弃用</el-tag
                      >
                    </div>
                  </div>
                </div>
                <el-empty v-else description="暂无" :image-size="50" />
              </el-card>

              <!-- 中期 -->
              <el-card shadow="never">
                <template #header>
                  <div class="card-hd">
                    <span>中期提交</span>
                  </div>
                </template>

                <div v-if="stageLists.middle.length" class="deliverable-list">
                  <div
                    v-for="d in stageLists.middle"
                    :key="d.id"
                    class="deliverable-item"
                    @click="openDeliverablePanel(d)"
                  >
                    <div class="row1">
                      <b class="title">{{ d.title }}</b>
                    </div>
                    <div class="row2 tiny muted">
                      {{ d.stage_version || '' }} · {{ d.updated_at || d.created_at }}
                    </div>
                    <div class="row3 tags">
                      <el-tag v-if="d.is_milestone" size="small" type="warning" effect="plain"
                        >里程碑</el-tag
                      >
                      <el-tag
                        v-if="d.is_updated && !d.is_deprecated"
                        size="small"
                        type="success"
                        effect="plain"
                        >有更新</el-tag
                      >
                      <el-tag v-if="d.is_deprecated" size="small" type="info" effect="plain"
                        >已弃用</el-tag
                      >
                    </div>
                  </div>
                </div>
                <el-empty v-else description="暂无" :image-size="50" />
              </el-card>

              <!-- 末期 -->
              <el-card shadow="never">
                <template #header>
                  <div class="card-hd">
                    <span>末期提交</span>
                  </div>
                </template>

                <div v-if="stageLists.final.length" class="deliverable-list">
                  <div
                    v-for="d in stageLists.final"
                    :key="d.id"
                    class="deliverable-item"
                    @click="openDeliverablePanel(d)"
                  >
                    <div class="row1">
                      <b class="title">{{ d.title }}</b>
                    </div>
                    <div class="row2 tiny muted">
                      {{ d.stage_version || '' }} · {{ d.updated_at || d.created_at }}
                    </div>
                    <div class="row3 tags">
                      <el-tag v-if="d.is_milestone" size="small" type="warning" effect="plain"
                        >里程碑</el-tag
                      >
                      <el-tag
                        v-if="d.is_updated && !d.is_deprecated"
                        size="small"
                        type="success"
                        effect="plain"
                        >有更新</el-tag
                      >
                      <el-tag v-if="d.is_deprecated" size="small" type="info" effect="plain"
                        >已弃用</el-tag
                      >
                    </div>
                  </div>
                </div>
                <el-empty v-else description="暂无" :image-size="50" />
              </el-card>
            </div>
          </div>
        </section>
      </div>

      <!-- 项目成员 -->
      <div v-show="activeTab === 'students'" class="panel">
        <section class="section-card accent-orange">
          <header class="section-hd"><div class="title">项目成员</div></header>
          <div class="section-bd">
            <div class="sq-tip">本列表为当前项目团队成员。</div>
            <div class="role-groups" v-if="Object.keys(groupedStudents).length">
              <div class="role-group" v-for="(list, role) in groupedStudents" :key="role">
                <div class="role-title">{{ role }}</div>
                <div class="members-grid">
                  <div v-for="m in list" :key="m.id" class="member-card">
                    <el-avatar :src="m.avatar" :size="40" />
                    <div class="info">
                      <div class="name-row">
                        <div class="name">{{ m.name }}</div>
                        <el-tag v-if="m.role" size="small" effect="plain">{{ m.role }}</el-tag>
                        <el-tag
                          v-if="myUserId != null && Number(m.userId) === Number(myUserId)"
                          size="small"
                          type="success"
                          effect="plain"
                          >我</el-tag
                        >
                      </div>
                      <div class="contact-row">
                        <span class="label">手机：</span>
                        <span class="value">{{ m.phone || '—' }}</span>
                      </div>
                      <div class="contact-row">
                        <span class="label">学校：</span>
                        <span class="value">{{ m.school || '—' }}</span>
                      </div>
                      <div class="contact-row">
                        <span class="label">专业：</span>
                        <span clas我在教三s="value">{{ m.major || '—' }}</span>
                      </div>
                      <div class="contact-row">
                        <span class="label">年级：</span>
                        <span class="value">{{ m.grade || '—' }}</span>
                      </div>
                      <div class="contact-row">
                        <span class="label">邮箱：</span>
                        <span class="value email">{{ m.email || '—' }}</span>
                      </div>
                    </div>
                    <div v-if="isLeader && !String(m.role || '').includes('组长')" class="ops">
                      <el-button text type="danger" size="small" @click="openRemoveMember(m)"
                        >移除</el-button
                      >
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <el-empty v-else description="暂无成员" />
            <!-- 项目成员 面板内，替换原来的“申请中”区块 -->
            <!-- === 再次替换 BEGIN：申请中（精简字段 + 按钮顺序调整） === -->
            <div class="block" style="margin-top: 10px" v-if="isLeader">
              <div class="role-title">申请中</div>
              <el-tag v-if="pendingApplicants.length === 0" type="info" effect="plain">暂无</el-tag>

              <div v-else class="applicant-compact-list">
                <div
                  v-for="a in pendingApplicants"
                  :key="a.id"
                  class="applicant-row simple"
                  :class="{ loading: enrichingApplicants && a._needDetail && !a._detailLoaded }"
                >
                  <div class="col avatar">
                    <el-avatar :src="a.avatar" :size="40" />
                  </div>

                  <div class="col name-major full-info">
                    <div class="nm-name" :title="a.real_name || a.name">
                      {{ a.real_name || a.name || '—' }}
                    </div>
                    <div class="field-row">
                      <span class="label">专业：</span
                      ><span class="value" :title="a.major">{{ a.major || '—' }}</span>
                    </div>
                    <div class="field-row">
                      <span class="label">年级：</span
                      ><span class="value" :title="a.grade">{{ a.grade || '—' }}</span>
                    </div>
                    <div class="field-row">
                      <span class="label">电话：</span
                      ><span class="value" :title="a.phone">{{ a.phone || '—' }}</span>
                    </div>
                    <div class="field-row">
                      <span class="label">邮箱：</span>
                      <span class="value email" :title="a.email">{{ a.email || '—' }}</span>
                    </div>
                  </div>

                  <div class="col ops">
                    <el-button type="primary" size="small" plain @click="openApplicationViewer(a)"
                      >查看</el-button
                    >
                    <el-button type="success" size="small" plain @click="openApproveDialog(a)"
                      >通过</el-button
                    >
                    <el-button type="danger" size="small" plain @click="openRejectDialog(a)"
                      >拒绝</el-button
                    >
                  </div>
                </div>
              </div>
            </div>
            <!-- === 再次替换 END === -->
          </div>
        </section>
      </div>

      <!-- 项目评分 -->
      <div v-show="activeTab === 'evaluation'" class="panel">
        <section class="section-card accent-green">
          <header class="section-hd"><div class="title">项目评分</div></header>
          <div class="section-bd">
            <el-skeleton :loading="evaluationLoading" animated :rows="4">
              <template #default>
                <template v-if="evaluation">
                  <div class="score-summary">
                    <!-- 修改：列数 2，只保留 评分状态 + 加权总分 -->
                    <el-descriptions :column="2" size="small" border>
                      <el-descriptions-item label="评分状态">
                        <el-tag
                          :type="
                            {
                              draft: 'info',
                              submitted: 'warning',
                              published: 'success'
                            }[String(evaluation.status || '').toLowerCase()] || 'info'
                          "
                          size="small"
                        >
                          {{ evaluation.status_display || evaluation.status || '—' }}
                        </el-tag>
                      </el-descriptions-item>
                      <el-descriptions-item label="加权总分">
                        {{ evaluation.weighted_score ?? '—' }}
                      </el-descriptions-item>
                    </el-descriptions>
                  </div>

                  <!-- 仅保留总评语 -->
                  <div class="mt12">
                    <div class="sub-title">总评语</div>
                    <el-card shadow="never">
                      <div style="white-space: pre-wrap">
                        {{ evaluation.overall_comment || '暂无评语' }}
                      </div>
                    </el-card>
                  </div>
                </template>
                <el-empty v-else description="暂无评分" />
              </template>
            </el-skeleton>
          </div>
        </section>
      </div>

      <!-- 资源 -->
      <div v-show="activeTab === 'resources'" class="panel">
        <section class="section-card accent-sky">
          <header class="section-hd"><div class="title">企业资源（来自所属需求）</div></header>
          <div class="section-bd">
            <el-empty v-if="!hasEnterpriseResources" description="暂无企业资源" />
            <!-- MyProjectDetail.vue  资源表格列替换开始 -->
            <el-table v-else :data="enterpriseResources" border size="small" style="width: 100%">
              <el-table-column prop="name" label="名称" min-width="240">
                <template #default="{ row }">
                  <el-tooltip
                    :content="row.description"
                    placement="top"
                    :disabled="!row.description"
                  >
                    <span>{{ row.name }}</span>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column prop="type" label="类型" width="100" />
              <el-table-column label="文件类型" width="120">
                <template #default="{ row }">
                  {{ getRowFileType(row) }}
                </template>
              </el-table-column>
              <el-table-column label="大小" width="110">
                <template #default="{ row }">
                  {{ formatFileSize(row.size) }}
                </template>
              </el-table-column>
              <el-table-column label="上传时间" width="180">
                <template #default="{ row }">
                  {{ formatDateMinute(row.created_at || row.uploadedAt) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    type="primary"
                    link
                    :loading="row.downloading"
                    @click="openProjectResource(row)"
                  >
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
            <!-- MyProjectDetail.vue  资源表格列替换结束 -->
          </div>
        </section>
      </div>

      <!-- 项目问答 -->
      <div v-show="activeTab === 'discussion'" class="panel">
        <section class="section-card accent-indigo">
          <header class="section-hd"><div class="title">项目问答 · 智能体</div></header>
          <div class="section-bd">
            <div class="ai-iframe-container">
              <AgentChat
                agent="wenshi"
                :inputs="{ pid: project.parentDemand.id }"
                :min-height="560"
              />
            </div>
          </div>
        </section>
      </div>

      <!--项目设置-->
      <div v-show="activeTab === 'settings'" class="panel">
        <section class="section-card accent-gray">
          <header class="section-hd">
            <div class="title">项目设置</div>
            <!-- 可根据实际功能继续扩展 -->
          </header>
          <div class="section-bd">
            <!-- 新增：项目状态设置（仅组长可见） -->
            <div v-if="isLeader" class="project-status-block">
              <div class="psb-title">项目状态</div>
              <el-form :inline="false" label-width="90px" class="psb-form" size="small">
                <el-form-item label="当前状态">
                  <el-select
                    v-model="statusForm.status"
                    placeholder="选择状态"
                    style="width: 220px"
                    :disabled="statusSaving"
                  >
                    <el-option
                      v-for="opt in statusOptions"
                      :key="opt.value"
                      :label="opt.label"
                      :value="opt.value"
                    />
                  </el-select>
                  <el-button
                    type="primary"
                    style="margin-left: 12px"
                    :loading="statusSaving"
                    :disabled="!statusForm.status || statusForm.status === project.rawStatus"
                    @click="saveProjectStatus"
                  >
                    保存
                  </el-button>
                </el-form-item>
                <el-form-item>
                  <div class="tiny muted">
                    说明：仅“招募中”状态允许新的学生发起加入申请；“进行中”与“已完成”状态将禁止申请。
                  </div>
                </el-form-item>
              </el-form>
            </div>
            <!-- 新增：转让组长权限 -->
            <div v-if="isLeader" class="transfer-leader-block">
              <div class="tlb-title">转让组长权限</div>
              <div class="tlb-desc">将项目负责人身份转让给其他成员</div>
              <el-button type="warning" plain size="small" @click="openTransferDialog">
                转让组长权限
              </el-button>
            </div>
            <div v-if="isLeader" class="danger-zone">
              <div class="dz-head">
                <div class="dz-title">危险操作</div>
              </div>
              <div class="dz-body">
                <p class="dz-desc">
                  删除项目将同时删除其成果、评论及成员关联，操作不可恢复。请谨慎执行。
                </p>
                <el-button type="danger" plain class="danger-delete-btn" @click="openDeleteDialog"
                  >删除项目</el-button
                >
              </div>
            </div>
            <div v-if="!isLeader" class="settings-hint-non-leader">
              只有组长可以查看修改项目信息
            </div>
          </div>
        </section>
      </div>
    </div>

    <!-- 编辑/删除对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      :title="editType === 'description' ? '编辑项目介绍' : '编辑具体要求'"
      width="720px"
      :close-on-click-modal="false"
    >
      <div class="submit-form">
        <div v-if="editType === 'description'" class="row">
          <label class="label">项目简介</label>
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="8"
            maxlength="5000"
            show-word-limit
            placeholder="填写项目的简介、背景、目标等"
          />
        </div>
        <div v-if="editType === 'requirements'" class="row">
          <label class="label">具体要求</label>
          <el-input
            v-model="editForm.requirementsText"
            type="textarea"
            :rows="6"
            placeholder="示例：&#10;1. 完成原型设计&#10;2. 搭建后端接口&#10;3. 编写使用文档"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="editDialogVisible = false">取 消</el-button>
        <el-button type="primary" :loading="editSaving" @click="saveEdit">保 存</el-button>
      </template>
    </el-dialog>

    <!-- 提交成果对话框（增强：必填标注 + 本地校验） -->
    <el-dialog
      v-model="submitDialogVisible"
      title="提交阶段成果"
      width="720px"
      :close-on-click-modal="false"
    >
      <div class="submit-form">
        <div class="row" :class="{ invalid: validationErrors.title }">
          <label class="label required">成果标题</label>
          <el-input v-model="submitForm.title" maxlength="120" placeholder="请输入成果标题" />
        </div>

        <div class="row" :class="{ invalid: validationErrors.stage }">
          <label class="label required">阶段类型</label>
          <el-select
            v-model="submitForm.stage_type"
            placeholder="请选择阶段类型"
            style="width: 260px"
          >
            <el-option label="前期（early）" value="early" />
            <el-option label="中期（middle）" value="middle" />
            <el-option label="末期（final）" value="final" />
          </el-select>
          <el-checkbox v-model="submitForm.is_milestone" style="margin-left: 16px"
            >标记为里程碑</el-checkbox
          >
        </div>

        <div class="row">
          <label class="label">成果描述（可选）</label>
          <el-input
            v-model="submitForm.description"
            type="textarea"
            :rows="4"
            placeholder="对本次提交的成果进行简要说明"
          />
        </div>

        <div class="row">
          <label class="label">进度说明（可选）</label>
          <el-input
            v-model="submitForm.progress_description"
            type="textarea"
            :rows="3"
            placeholder="进度概述、成员分工、下一步计划等"
          />
        </div>

        <div class="row">
          <label class="label">备注（可选）</label>
          <el-input v-model="submitForm.notes" placeholder="补充信息" />
        </div>

        <div class="row" :class="{ invalid: validationErrors.content }">
          <label class="label required-group">上传文件（与网盘链接二选一）</label>
          <el-upload
            drag
            multiple
            :auto-upload="false"
            :file-list="submitFileList"
            :before-upload="beforeSelectFile"
            :on-change="onUploadChange"
            :on-remove="onUploadRemove"
            accept="*"
            action=""
            list-type="text"
          >
            <i class="el-icon--upload"></i>
            <div class="el-upload__text">将文件拖到此处，或点击选择</div>
            <template #tip>
              <div class="el-upload__tip">支持多文件上传，建议压缩为一个压缩包</div>
            </template>
          </el-upload>
        </div>

        <div class="row" :class="{ invalid: validationErrors.content }">
          <label class="label required-group">网盘链接（与上传文件二选一）</label>
          <el-input
            v-model="submitForm.cloud_links"
            placeholder="如：https://pan.baidu.com/s/xxxx"
          />
          <div class="tiny muted mt4">提示：上传文件 或 网盘链接 至少提供一个</div>
        </div>
        <div class="row">
          <label class="label">网盘密码（可选）</label>
          <el-input v-model="submitForm.cloud_password" placeholder="如有，请填写提取码/密码" />
        </div>

        <div class="row">
          <label class="label">虚拟存储路径（可选）</label>
          <el-input v-model="submitForm.virtual_folder_path" placeholder="例如：/docs/middle" />
        </div>
      </div>

      <template #footer>
        <el-button @click="submitDialogVisible = false">取 消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="doSubmitDeliverable"
          >提 交</el-button
        >
      </template>
    </el-dialog>

    <!-- 成果详情对话框（表格视图入口） -->
    <el-dialog v-model="detailDialogVisible" title="成果详情" width="720px">
      <template v-if="deliverableDetail">
        <el-descriptions :column="2" border size="small">
          <el-descriptions-item label="标题">{{ deliverableDetail.title }}</el-descriptions-item>
          <el-descriptions-item label="阶段">{{
            stageName(deliverableDetail.stage_type)
          }}</el-descriptions-item>
          <el-descriptions-item label="阶段版本">{{
            deliverableDetail.stage_version
          }}</el-descriptions-item>
          <el-descriptions-item label="里程碑">
            <el-tag
              size="small"
              effect="plain"
              :type="deliverableDetail.is_milestone ? 'warning' : ''"
            >
              {{ deliverableDetail.is_milestone ? '是' : '否' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="提交者">
            {{
              deliverableDetail.submitter?.real_name || deliverableDetail.submitter?.username || '—'
            }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">{{
            deliverableDetail.updated_at
          }}</el-descriptions-item>
        </el-descriptions>

        <div class="mt12">
          <div class="sub-title">描述</div>
          <el-card shadow="never">
            <div style="white-space: pre-wrap">
              {{ deliverableDetail.description || '—' }}
            </div>
          </el-card>
        </div>

        <div class="mt12">
          <div class="sub-title">进度说明</div>
          <el-card shadow="never">
            <div style="white-space: pre-wrap">
              {{ deliverableDetail.progress_description || '—' }}
            </div>
          </el-card>
        </div>

        <div class="mt12">
          <div class="sub-title">文件</div>
          <el-table :data="deliverableDetail.files || []" border size="small" empty-text="暂无文件">
            <el-table-column prop="id" label="ID" width="90" />
            <el-table-column prop="name" label="名称" min-width="220" />
            <el-table-column prop="file_size" label="大小" width="120" />
            <el-table-column prop="uploaded_at" label="上传时间" width="180" />
            <el-table-column label="类型" width="100">
              <template #default="{ row }">
                <el-tag size="small" effect="plain" :type="row.is_cloud_link ? 'info' : 'success'">
                  {{ row.is_cloud_link ? '网盘链接' : '文件' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="160" fixed="right">
              <template #default="{ row }">
                <el-button
                  v-if="!row.is_cloud_link && row.file_url"
                  text
                  type="primary"
                  @click="window.open(row.file_url, '_blank')"
                  >下载/查看</el-button
                >
                <el-button
                  v-else-if="row.cloud_link_url"
                  text
                  type="primary"
                  @click="window.open(row.cloud_link_url, '_blank')"
                  >打开链接</el-button
                >
              </template>
            </el-table-column>
          </el-table>
        </div>
      </template>
      <template #footer>
        <el-button @click="detailDialogVisible = false">关 闭</el-button>
      </template>
    </el-dialog>

    <!-- 阶段详情面板 -->
    <el-dialog
      v-model="stagePanelVisible"
      :title="
        stagePanel.deliverable
          ? `阶段提交 · ${stageName(stagePanel.deliverable.stage_type)} · ${stagePanel.deliverable.stage_version || ''}`
          : '阶段提交'
      "
      width="900px"
      :close-on-click-modal="true"
    >
      <template v-if="stagePanel.deliverable">
        <el-card shadow="never" class="mb8">
          <template #header>
            <div class="card-hd">
              <span>提交详情</span>
            </div>
          </template>
          <el-skeleton :loading="stagePanel.loadingDetail" animated :rows="4">
            <template #default>
              <div class="mb8">
                <b>{{ stagePanel.deliverable.title }}</b>
              </div>
              <div class="muted tiny mb8">
                {{ stagePanel.deliverable.stage_version || '' }} ·
                {{ stagePanel.deliverable.updated_at || stagePanel.deliverable.created_at }}
                <el-tag
                  v-if="stagePanel.deliverable.is_milestone"
                  size="small"
                  type="warning"
                  effect="plain"
                  class="ml8"
                  >里程碑</el-tag
                >
                <el-tag
                  v-if="stagePanel.deliverable.is_deprecated"
                  size="small"
                  type="info"
                  effect="plain"
                  class="ml8"
                  >已弃用</el-tag
                >
              </div>
              <el-descriptions :column="2" size="small" border>
                <el-descriptions-item label="阶段">{{
                  stageName(stagePanel.deliverable.stage_type)
                }}</el-descriptions-item>
                <el-descriptions-item label="提交者">
                  {{
                    stagePanel.deliverable.submitter?.real_name ||
                    stagePanel.deliverable.submitter?.username ||
                    '—'
                  }}
                </el-descriptions-item>
              </el-descriptions>

              <div class="mt12">
                <div class="sub-title">描述</div>
                <el-card shadow="never">
                  <div style="white-space: pre-wrap">
                    {{ stagePanel.deliverable.description || '—' }}
                  </div>
                </el-card>
              </div>

              <div class="mt12">
                <div class="sub-title">进度说明</div>
                <el-card shadow="never">
                  <div style="white-space: pre-wrap">
                    {{ stagePanel.deliverable.progress_description || '—' }}
                  </div>
                </el-card>
              </div>

              <div class="mt12">
                <div class="sub-title">文件</div>
                <el-table
                  :data="stagePanel.deliverable.files || []"
                  border
                  size="small"
                  empty-text="暂无文件"
                >
                  <el-table-column prop="id" label="ID" width="90" />
                  <el-table-column prop="name" label="名称" min-width="220" />
                  <el-table-column prop="file_size" label="大小" width="120" />
                  <el-table-column prop="uploaded_at" label="上传时间" width="180" />
                  <el-table-column label="类型" width="100">
                    <template #default="{ row }">
                      <el-tag
                        size="small"
                        effect="plain"
                        :type="row.is_cloud_link ? 'info' : 'success'"
                      >
                        {{ row.is_cloud_link ? '网盘链接' : '文件' }}
                      </el-tag>
                    </template>
                  </el-table-column>
                  <el-table-column label="操作" width="160" fixed="right">
                    <template #default="{ row }">
                      <el-button
                        v-if="!row.is_cloud_link && row.file_url"
                        text
                        type="primary"
                        @click="window.open(row.file_url, '_blank')"
                        >下载/查看</el-button
                      >
                      <el-button
                        v-else-if="row.cloud_link_url"
                        text
                        type="primary"
                        @click="window.open(row.cloud_link_url, '_blank')"
                        >打开链接</el-button
                      >
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </template>
          </el-skeleton>
        </el-card>

        <div class="mt12">
          <div class="sub-title">与企业的对话（仅查看企业评语）</div>
          <el-card shadow="never">
            <div v-if="isOrgUser" class="comment-new-box">
              <el-input
                v-model="stagePanel.newCommentText"
                type="textarea"
                :rows="3"
                maxlength="1000"
                show-word-limit
                placeholder="发布企业评语（仅组织用户可见此输入框）"
              />
              <div style="margin-top: 8px; text-align: right">
                <el-button
                  type="primary"
                  :disabled="!stagePanel.newCommentText.trim()"
                  :loading="stagePanel.sendingNew"
                  @click="sendNewComment"
                  >发布评语</el-button
                >
              </div>
              <el-divider />
            </div>

            <el-skeleton :loading="stagePanel.loadingComments" animated :rows="3">
              <template #default>
                <div v-if="stagePanel.comments.length" class="comment-list">
                  <div v-for="c in stagePanel.comments" :key="c.id" class="comment-item">
                    <div class="comment-header">
                      <el-avatar :src="c.avatar" :size="32" />
                      <span class="comment-author">{{ c.author }}</span>
                      <span v-if="c.authorIsOrg" class="comment-tag org">企业</span>
                      <span class="comment-time">{{ c.created_at }}</span>
                    </div>
                    <div class="comment-content">{{ c.content }}</div>
                    <el-divider />
                  </div>
                </div>
                <el-empty v-else description="暂无企业评语" :image-size="60" />
              </template>
            </el-skeleton>
          </el-card>
        </div>
      </template>
      <template #footer>
        <el-button @click="stagePanelVisible = false">关 闭</el-button>
      </template>
    </el-dialog>
  </div>

  <div v-else class="not-found">
    <el-empty :description="loading ? '正在加载…' : '未找到该项目'" />
    <div class="pad">
      <el-button :icon="ArrowLeft" @click="goBackToList">返回我的项目</el-button>
    </div>
  </div>

  <!-- 插入在“编辑项目介绍”对话框之后 -->
  <el-dialog
    v-model="deleteDialogVisible"
    title="删除项目"
    width="720px"
    :close-on-click-modal="false"
    :close-on-press-escape="!deleteLoading"
    :show-close="!deleteLoading"
  >
    <div class="submit-form">
      <div class="row">
        <div class="delete-desc">
          <p>确认要删除该项目吗？此操作不可恢复。</p>
          <p>删除后将：</p>
          <ul>
            <li>解除与所有参与者的关系</li>
            <li>删除所有关联的成果及其文件</li>
            <li>删除所有项目评论与相关通知</li>
          </ul>
        </div>
      </div>
    </div>
    <template #footer>
      <el-button :disabled="deleteLoading" @click="deleteDialogVisible = false">取 消</el-button>
      <el-button type="danger" :loading="deleteLoading" @click="confirmDelete">确认删除</el-button>
    </template>
  </el-dialog>

  <!-- 新增：移除成员对话框（放在模板末尾，和其它 el-dialog 同级） -->
  <el-dialog
    v-model="removeDialogVisible"
    title="移除成员"
    width="560px"
    :close-on-click-modal="false"
    :close-on-press-escape="!removing"
    :show-close="!removing"
  >
    <div class="submit-form">
      <div class="row">
        <div>确定要移除该成员吗？此操作将把其状态设置为“离开（left）”。</div>
        <div class="tiny muted" style="margin-top: 6px">
          成员：<b>{{ removeTarget?.name || '-' }}</b>
        </div>
      </div>
      <div class="row">
        <label class="label">移除原因（可选）</label>
        <el-input
          v-model="removeReason"
          type="textarea"
          :rows="3"
          maxlength="500"
          show-word-limit
          placeholder="填写移除原因（将记录在后端）"
        />
      </div>
    </div>
    <template #footer>
      <el-button :disabled="removing" @click="removeDialogVisible = false">取 消</el-button>
      <el-button type="danger" :loading="removing" @click="confirmRemoveMember"
        >确 认 移 除</el-button
      >
    </template>
  </el-dialog>

  <!-- 转让组长弹窗 -->
  <el-dialog
    v-model="transferDialogVisible"
    title="转让组长权限"
    width="500px"
    :close-on-click-modal="false"
  >
    <el-form label-width="100px" size="small">
      <el-form-item label="选择新负责人" required>
        <el-select
          v-model="transferForm.newLeaderId"
          placeholder="请选择新负责人"
          style="width: 100%"
          :disabled="transferring"
        >
          <el-option
            v-for="m in transferableMembers"
            :key="m.id"
            :label="`${m.name} (${m.role || '成员'})`"
            :value="m.id"
          >
            <div style="display: flex; align-items: center">
              <el-avatar :src="m.avatar" :size="24" style="margin-right: 8px" />
              <span>{{ m.name }}</span>
              <el-tag size="small" style="margin-left: 8px">{{ m.role || '成员' }}</el-tag>
            </div>
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item label="转让说明">
        <el-input
          v-model="transferForm.transferMessage"
          type="textarea"
          :rows="3"
          placeholder="可选填写转让原因或说明（最多200字）"
          maxlength="200"
          show-word-limit
          :disabled="transferring"
        />
      </el-form-item>

      <el-alert
        title="注意：转让后您将失去组长权限，无法撤销此操作"
        type="warning"
        :closable="false"
        show-icon
        style="margin-bottom: 16px"
      />
    </el-form>

    <template #footer>
      <el-button @click="transferDialogVisible = false" :disabled="transferring"> 取消 </el-button>
      <el-button type="primary" @click="confirmTransferLeadership" :loading="transferring">
        确认转让
      </el-button>
    </template>
  </el-dialog>

  <!-- === 新增 BEGIN：查看申请信息弹窗 === -->
  <el-dialog
    v-model="applicationViewerVisible"
    title="申请信息"
    width="640px"
    :close-on-click-modal="false"
  >
    <!-- === 替换 BEGIN：查看申请信息描述项 === -->
    <el-descriptions :column="2" size="small" border>
      <el-descriptions-item label="姓名">
        {{ applicationViewer?.real_name || applicationViewer?.name || '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="学校">
        {{ applicationViewer?.school_name.name || '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="专业">
        {{ applicationViewer?.major || '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="年级">
        {{ applicationViewer?.grade || '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="电话">
        {{ applicationViewer?.phone || '—' }}
      </el-descriptions-item>
      <el-descriptions-item label="邮箱">
        {{ applicationViewer?.email || '—' }}
      </el-descriptions-item>
      <el-descriptions-item :span="2" label="申请理由">
        <div style="white-space: pre-wrap">{{ applicationViewer?.reason || '—' }}</div>
      </el-descriptions-item>
      <el-descriptions-item :span="2" label="提交时间">
        {{
          applicationViewer?.applied_at_fmt ||
          formatDateMinute(applicationViewer?.applied_at) ||
          '—'
        }}
      </el-descriptions-item>
    </el-descriptions>
    <!-- === 替换 END：查看申请信息描述项 === -->
    <template #footer>
      <el-button @click="applicationViewerVisible = false">关 闭</el-button>
    </template>
  </el-dialog>
  <!-- === 新增 END === -->

  <!-- === 新增 BEGIN：通过申请弹窗 === -->
  <el-dialog
    v-model="approveDialogVisible"
    title="通过申请"
    width="560px"
    :close-on-click-modal="false"
    :close-on-press-escape="!applicationActionLoading"
    :show-close="!applicationActionLoading"
  >
    <div class="submit-form">
      <div class="row">
        <label class="label">申请人</label>
        <div>{{ activeApplication?.real_name || activeApplication?.name || '—' }}</div>
      </div>
      <div class="row">
        <label class="label">申请理由</label>
        <el-card shadow="never" style="width: 100%; max-height: 150px; overflow: auto">
          <div style="white-space: pre-wrap">{{ activeApplication?.reason || '—' }}</div>
        </el-card>
      </div>
      <div class="row">
        <label class="label">审核留言（可选）</label>
        <el-input
          v-model="reviewMessageApprove"
          type="textarea"
          :rows="4"
          maxlength="500"
          show-word-limit
          placeholder="欢迎加入项目团队！"
        />
      </div>
    </div>
    <template #footer>
      <el-button :disabled="applicationActionLoading" @click="approveDialogVisible = false"
        >取 消</el-button
      >
      <el-button
        type="primary"
        :loading="applicationActionLoading"
        @click="confirmApproveApplication"
        >确 认 通 过</el-button
      >
    </template>
  </el-dialog>
  <!-- === 新增 END：通过申请弹窗 === -->

  <!-- === 新增 BEGIN：拒绝申请弹窗 === -->
  <el-dialog
    v-model="rejectDialogVisible"
    title="拒绝申请"
    width="560px"
    :close-on-click-modal="false"
    :close-on-press-escape="!applicationActionLoading"
    :show-close="!applicationActionLoading"
  >
    <div class="submit-form">
      <div class="row">
        <label class="label">申请人</label>
        <div>{{ activeApplication?.real_name || activeApplication?.name || '—' }}</div>
      </div>
      <div class="row">
        <label class="label">申请理由</label>
        <el-card shadow="never" style="width: 100%; max-height: 150px; overflow: auto">
          <div style="white-space: pre-wrap">{{ activeApplication?.reason || '—' }}</div>
        </el-card>
      </div>
      <div class="row">
        <label class="label">审核留言（可选）</label>
        <el-input
          v-model="reviewMessageReject"
          type="textarea"
          :rows="4"
          maxlength="500"
          show-word-limit
          placeholder="很抱歉你的申请未能通过。"
        />
      </div>
    </div>
    <template #footer>
      <el-button :disabled="applicationActionLoading" @click="rejectDialogVisible = false"
        >取 消</el-button
      >
      <el-button type="danger" :loading="applicationActionLoading" @click="confirmRejectApplication"
        >确 认 拒 绝</el-button
      >
    </template>
  </el-dialog>
  <!-- === 新增 END：拒绝申请弹窗 === -->
</template>

<style scoped lang="scss">
.my-project-detail {
  padding: 12px 16px 20px;
}
/* 顶部标题与返回条 */
.page-header {
  position: sticky;
  top: 0;
  z-index: 5;
  background: linear-gradient(135deg, #f5f7ff 0%, #f7fafc 100%);
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 10px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  .left {
    display: flex;
    flex-direction: column;
    gap: 6px;
    width: 100%;
  }
  .back-btn {
    align-self: flex-start;
  }
  .title-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    .name {
      font-size: 20px;
      font-weight: 800;
      color: #1d2129;
    }
  }
  .meta {
    display: flex;
    align-items: center;
    gap: 8px;
    color: #86909c;
    flex-wrap: wrap;
    .sep {
      width: 1px;
      height: 12px;
      background: #e5e6eb;
      display: inline-block;
    }
  }
  .tags {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
  }
  .right.project-actions {
    display: flex;
    gap: 18px;
    align-items: center;
    justify-content: flex-end;
    flex-wrap: nowrap;
    margin-top: 0;
  }
}

/* 统一显眼大按钮样式 */
.action-btn {
  min-width: 140px;
  font-size: 17px;
  font-weight: 700;
  height: 46px;
  border-radius: 12px;
  box-shadow: 0 4px 18px rgba(22, 93, 255, 0.16);
  transition:
    transform 0.1s,
    box-shadow 0.2s,
    filter 0.2s;
  &:hover {
    filter: brightness(1.05) saturate(1.08);
    transform: translateY(-2px) scale(1.03);
    box-shadow: 0 8px 24px rgba(22, 93, 255, 0.23);
  }
}
/* 绿色编辑按钮 */
.edit-btn {
  background: linear-gradient(90deg, #22c55e 0%, #38bdf8 100%);
  color: #fff !important;
  border: none;
  &:hover {
    background: linear-gradient(90deg, #38bdf8 0%, #22c55e 100%);
    color: #fff !important;
  }
}
/* 红色删除按钮 */
.delete-btn {
  background: linear-gradient(90deg, #ef4444 0%, #f87171 100%);
  color: #fff !important;
  border: none;
  &:hover {
    background: linear-gradient(90deg, #f87171 0%, #ef4444 100%);
    color: #fff !important;
  }
}
/* 蓝色提交成果按钮 */
.submit-btn {
  background: linear-gradient(90deg, #2563eb 0%, #38bdf8 100%);
  color: #fff !important;
  border: none;
  &:hover {
    background: linear-gradient(90deg, #38bdf8 0%, #2563eb 100%);
    color: #fff !important;
  }
}
/* 大按钮导航 */
.subnav {
  position: sticky;
  top: 64px;
  z-index: 4;
  background: #ffffffcc;
  backdrop-filter: saturate(180%) blur(6px);
  border: 1px solid #e5e6eb;
  border-radius: 16px;
  padding: 12px;
  margin-bottom: 12px;
}
.nav-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 10px;
  @media (max-width: 960px) {
    grid-template-columns: repeat(2, 1fr);
  }
  @media (max-width: 520px) {
    grid-template-columns: 1fr;
  }
}
.nav-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  border: 1px solid #e5e6eb;
  border-radius: 14px;
  padding: 14px 16px;
  background: #fff;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 10px 24px rgba(22, 93, 255, 0.1);
    border-color: #d6e0ff;
    background: linear-gradient(180deg, #ffffff, #f9fbff);
  }
  &.active {
    border-color: #165dff;
    background: linear-gradient(180deg, #f4f7ff, #eef3ff);
    box-shadow: 0 12px 28px rgba(22, 93, 255, 0.16);
  }
  .icon-wrap {
    width: 44px;
    height: 44px;
    border-radius: 12px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: #f4f6fa;
    color: #165dff;
    box-shadow: inset 0 0 0 1px #e6ebf5;
    flex-shrink: 0;
  }
  &.active .icon-wrap {
    background: #165dff;
    color: #fff;
    box-shadow: none;
  }
  .texts {
    display: flex;
    flex-direction: column;
  }
  .t1 {
    font-weight: 800;
    color: #1d2129;
    font-size: 15px;
    line-height: 1.1;
  }
  .t2 {
    color: #86909c;
    font-size: 12px;
    margin-top: 4px;
  }
}

/* 内容卡片 */
.section-card {
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 14px;
  overflow: hidden;
  &::before {
    content: '';
    display: block;
    height: 4px;
    background: #165dff;
  }
  .section-hd {
    padding: 10px 12px;
    border-bottom: 1px dashed #e5e6eb;
    .title {
      font-weight: 800;
      color: #1d2129;
    }
  }
  .section-bd {
    padding: 12px;
  }
}
.panel {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* 具体要求：缩小高度 */
.compact-req .section-bd {
  padding: 10px 12px;
  min-height: 120px;
}
.compact-req :deep(.el-empty) {
  margin: 6px 0;
}
.compact-req :deep(.el-empty__image) {
  height: 50px !important;
}

/* intro 要求列表 */
.req-list {
  margin: 0;
  padding: 0;
  list-style: none;
  li {
    display: flex;
    gap: 8px;
    align-items: flex-start;
    + li {
      margin-top: 6px;
    }
  }
  .dot {
    width: 6px;
    height: 6px;
    margin-top: 8px;
    border-radius: 50%;
    background: #165dff;
    flex-shrink: 0;
  }
  .text {
    color: #1d2129;
  }
}

/* 阶段性进展布局与样式 */
.progress-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.stage-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
  @media (max-width: 960px) {
    grid-template-columns: 1fr;
  }
}
.card-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

/* 提交卡片列表 */
.deliverable-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}
.deliverable-item {
  border: 1px solid #e5e6eb;
  border-radius: 10px;
  padding: 10px;
  background: #fff;
  cursor: pointer;
  transition:
    transform 0.06s ease,
    box-shadow 0.15s ease,
    border-color 0.15s ease;
}
.deliverable-item:hover {
  transform: translateY(-1px);
  border-color: #cfe0ff;
  box-shadow: 0 10px 24px rgba(22, 93, 255, 0.08);
}
.deliverable-item .row1 .title {
  font-weight: 700;
  color: #1d2129;
}
.deliverable-item .row2 {
  margin-top: 2px;
}
.deliverable-item .row3.tags {
  margin-top: 6px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.muted {
  color: #86909c;
}
.tiny {
  font-size: 12px;
}

.ai-iframe-container {
  width: 100%;
  min-height: 560px;
}

/* 成员网格等（保持不变） */
.role-groups {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.role-group .role-title {
  font-weight: 700;
  margin: 6px 0 8px;
  color: #1d2129;
}
.members-grid {
  display: grid;
  /* 自动填充，最小 300px，空间够时变宽，减少邮箱被挤压换行的概率 */
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}
@media (max-width: 1400px) {
  .members-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }
}
@media (max-width: 1040px) {
  .members-grid {
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  }
}
@media (max-width: 560px) {
  .members-grid {
    grid-template-columns: 1fr;
  }
}
.member-card {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  background: #fff;
}
.member-card .info {
  flex: 1;
  min-width: 0;
}
.member-card .name-row {
  display: flex;
  align-items: center;
  gap: 6px;
  font-weight: 600;
  color: #1d2129;
}
.member-card .contact {
  color: #86909c;
  font-size: 12px;
  display: flex;
  gap: 4px;
}
.member-card .ops {
  flex-shrink: 0;
}

/* 其它 */
.mt12 {
  margin-top: 12px;
}
.mb8 {
  margin-bottom: 8px;
}
.ml8 {
  margin-left: 8px;
}
.mt4 {
  margin-top: 4px;
}
.sub-title {
  font-weight: 700;
  margin-bottom: 8px;
}

/* 对话区样式（保留原注释块） */
.thread-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.thread-item {
  border-bottom: 1px dashed #eee;
  padding-bottom: 8px;
}
.thread-hd {
  display: flex;
  align-items: center;
  gap: 8px;
}
.thread-hd .info {
  flex: 1;
  min-width: 0;
}
.thread-hd .ops {
  flex-shrink: 0;
  display: inline-flex;
  gap: 8px;
}
.thread-content {
  margin: 6px 0 6px 36px;
}
.replies {
  margin-left: 36px;
  border-left: 2px solid #f0f2f7;
  padding-left: 8px;
}
.reply-item {
  display: flex;
  gap: 8px;
  padding: 6px 0;
}
.reply-body .name {
  margin-bottom: 2px;
}
.reply-editor {
  margin-top: 12px;
}

/* === 评论与回复样式（保留注释） === */
.comment-new-box {
  margin-bottom: 16px;
}
.comment-list {
  margin-top: 8px;
}
.comment-item {
  padding: 8px 0;
}
.comment-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
}
.comment-author {
  font-weight: 600;
}
.comment-tag.org {
  background: #ffe8cc;
  color: #d46b08;
  font-size: 10px;
  padding: 2px 4px;
  border-radius: 4px;
}
.comment-time {
  margin-left: auto;
  color: #999;
  font-size: 12px;
}
.comment-content {
  margin: 4px 0 6px 32px;
  white-space: pre-wrap;
  line-height: 1.5;
}

/* ===== 提交弹窗的必填标注与错误高亮 ===== */
.label.required::after {
  content: ' *';
  color: #f56c6c;
  margin-left: 4px;
}
.label.required-group::after {
  content: '（必填：二选一）';
  color: #f56c6c;
  margin-left: 6px;
  font-weight: 500;
}
.row.invalid :deep(.el-input__wrapper),
.row.invalid :deep(.el-textarea__inner),
.row.invalid :deep(.el-select .el-input__wrapper) {
  box-shadow: 0 0 0 1px #f56c6c inset !important;
}
.row.invalid :deep(.el-upload-dragger) {
  border-color: #f56c6c !important;
}

/* 删除确认正文排版微调，保持与编辑弹窗一致的留白与字号 */
.delete-desc {
  line-height: 1.6;
  color: #1d2129;
  ul {
    margin: 6px 0 0 18px;
    padding: 0;
    list-style: disc;
    color: #4e5969;
  }
  p {
    margin: 0 0 6px;
  }
}

.card-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.card-title {
  font-weight: 800;
  color: #1d2129;
  font-size: 16px;
}
.card-edit-btn {
  font-size: 15px;
  color: #2563eb !important;
  background: none !important;
  border: none !important;
  padding: 0 6px !important;
  height: 28px !important;
  line-height: 28px;
  font-weight: 500;
  cursor: pointer;
  transition: color 0.18s;
  &:hover {
    color: #1d4ed8 !important;
    text-decoration: underline;
  }
}

/* 统一：含操作按钮的 header 行布局（让两个编辑按钮与标题与成果标题对齐） */
.section-card .section-hd.header-with-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 12px;
  .title {
    font-weight: 800;
    font-size: 16px;
    line-height: 1.1;
    color: #1d2129;
  }
}

/* 若之前 card-row/card-title 仍存在，可不再使用；无需删除 */

/* 危险操作区 */
.danger-zone {
  margin-top: 28px;
  padding: 16px 18px 20px;
  border: 1px solid #fecaca;
  background: linear-gradient(180deg, #fff5f5 0%, #ffffff 100%);
  border-radius: 12px;
  position: relative;
}
.dz-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.dz-title {
  font-size: 15px;
  font-weight: 700;
  color: #b91c1c;
  display: flex;
  align-items: center;
  gap: 6px;
}
.dz-body {
  font-size: 13px;
  line-height: 1.55;
  color: #4e5969;
}
.dz-desc {
  margin: 0 0 12px;
  white-space: normal;
}
.danger-delete-btn {
  min-width: 140px;
  font-weight: 600;
}
.member-card .contact-row {
  display: flex;
  align-items: flex-start;
  gap: 4px;
  margin: 2px 0;
  font-size: 13px;
  color: #4e5969;
  flex-wrap: wrap;
}
.member-card .contact-row .label {
  width: 54px;
  min-width: 54px;
  color: #86909c;
  font-weight: 500;
  flex-shrink: 0;
  text-align: right;
  display: inline-block;
}
.member-card .contact-row .value {
  word-break: break-all;
  white-space: pre-line;
  flex: 1;
  min-width: 0;
}

/* 单行显示邮箱，防止被强制换行；溢出省略号 */
.member-card .contact-row .value.email {
  white-space: nowrap;
  word-break: normal;
  overflow: hidden;
  text-overflow: ellipsis;
  display: inline-block;
  max-width: 100%;
}

/* === 项目状态标签与设置区块（新增） === */
.project-status-tag {
  font-weight: 600;
  margin-left: 4px;
}

.project-status-block {
  margin-top: 24px;
  padding: 16px 18px 12px;
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  background: #fff;
  .psb-title {
    font-weight: 700;
    font-size: 14px;
    margin-bottom: 12px;
    color: #1d2129;
  }
  .psb-form {
    max-width: 480px;
  }
}

/* === 新增：阶段性成果进展提示与配色区分 BEGIN === */
.section-card.accent-progress {
  /* 轻微区分：顶部条及背景淡化为渐变，与其它 accent-* 不同 */
  &::before {
    background: linear-gradient(90deg, #6366f1 0%, #3b82f6 55%, #0ea5e9 100%);
  }
  .progress-hint {
    background: linear-gradient(180deg, #f0f6ff 0%, #ffffff 100%);
    border: 1px solid #dbe7ff;
    border-radius: 10px;
    margin: 10px 12px 4px;
    padding: 10px 14px 12px;
    line-height: 1.55;
    .p-title {
      margin: 0 0 6px;
      font-weight: 600;
      font-size: 13px;
      color: #1e3a8a;
    }
    .p-text {
      margin: 0;
      font-size: 12px;
      color: #334155;
      white-space: normal;
    }
  }
}
/* 评分区块（可选微调：去掉多余空白，保持一致性） */
.score-summary {
  margin-bottom: 8px;
}
/* === 新增：阶段性成果进展提示与配色区分 END === */

/* === 新增 BEGIN：申请中紧凑行样式（约原面积 1/4） === */
.applicant-compact-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-top: 6px;
}
.applicant-row {
  display: grid;
  grid-template-columns: 52px 150px 160px 1fr 140px;
  align-items: center;
  gap: 8px;
  padding: 6px 10px;
  border: 1px solid #e5e6eb;
  border-radius: 8px;
  background: #fff;
  min-height: 56px;
  font-size: 12px;
  line-height: 1.3;
  transition: background 0.15s;
}
.applicant-row:hover {
  background: #f8fafc;
}
.applicant-row.loading {
  opacity: 0.6;
  position: relative;
}
.applicant-row.loading::after {
  content: '加载中…';
  position: absolute;
  right: 8px;
  top: 4px;
  font-size: 11px;
  color: #909399;
}

.applicant-row .col {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.applicant-row .col.basic .line.name {
  font-weight: 600;
  font-size: 13px;
  color: #1d2129;
}
.applicant-row .col.basic .line.school-major {
  color: #4e5969;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.applicant-row .label {
  color: #86909c;
  margin-right: 4px;
  white-space: nowrap;
}
.applicant-row .v {
  color: #1d2129;
  word-break: break-all;
}
.applicant-row .ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.applicant-row .col.ops {
  flex-direction: row;
  justify-content: flex-end;
  gap: 6px;
}

@media (max-width: 1200px) {
  .applicant-row {
    grid-template-columns: 52px 140px 140px 1fr 120px;
  }
}
@media (max-width: 960px) {
  .applicant-row {
    grid-template-columns: 52px 150px 1fr 120px;
  }
  .applicant-row .col.grade-contact {
    display: none;
  }
}
@media (max-width: 640px) {
  .applicant-row {
    grid-template-columns: 52px 1fr 110px;
  }
  .applicant-row .col.email-reason {
    display: none;
  }
}
/* === 新增 END === */

/* === 新增 BEGIN：申请中紧凑 simple 行样式（只显示 5 项 + 操作） === */
.applicant-row.simple {
  grid-template-columns: 52px 180px 1fr 150px;
  padding: 6px 8px;
  font-size: 12px;
}
@media (max-width: 1200px) {
  .applicant-row.simple {
    grid-template-columns: 52px 160px 1fr 140px;
  }
}
@media (max-width: 960px) {
  .applicant-row.simple {
    grid-template-columns: 52px 1fr 140px;
  }
  .applicant-row.simple .col.name-major {
    min-width: 140px;
  }
}
@media (max-width: 640px) {
  .applicant-row.simple {
    grid-template-columns: 52px 1fr 120px;
  }
  .applicant-row.simple .col.contact .email {
    display: none;
  }
}

.applicant-row.simple .col.name-major {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.applicant-row.simple .nm-name {
  font-weight: 600;
  font-size: 13px;
  color: #1d2129;
  line-height: 1.2;
}
.applicant-row.simple .nm-major-grade {
  font-size: 12px;
  color: #4e5969;
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}
.applicant-row.simple .col.contact {
  display: flex;
  flex-direction: column;
  gap: 2px;
  min-width: 0;
}
.applicant-row.simple .col.contact .c-line {
  line-height: 1.2;
  color: #1d2129;
  font-size: 12px;
}
.applicant-row.simple .col.contact .email {
  max-width: 180px;
}
.applicant-row.simple .col.ops {
  display: flex;
  flex-direction: row;
  gap: 6px;
  justify-content: flex-end;
}
.applicant-row.simple .ellipsis {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
/* === 新增 END === */

/* === 新增 BEGIN：申请中 full-info 样式 === */
.applicant-row.simple .col.full-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  .nm-name {
    font-weight: 600;
    font-size: 13px;
    margin-bottom: 2px;
  }
  .field-row {
    display: flex;
    align-items: flex-start;
    gap: 2px;
    font-size: 12px;
    line-height: 1.25;
    .label {
      color: #86909c;
      flex-shrink: 0;
    }
    .value {
      color: #1d2129;
      word-break: break-all;
      &.email {
        max-width: 260px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }
  }
}
/* 中小屏裁剪邮件宽度 */
@media (max-width: 960px) {
  .applicant-row.simple .col.full-info .field-row .value.email {
    max-width: 180px;
  }
}
@media (max-width: 640px) {
  .applicant-row.simple .col.full-info .field-row .value.email {
    max-width: 140px;
  }
}
/* === 新增 END === */

.settings-hint-non-leader {
  padding: 40px 12px 56px;
  text-align: center;
  color: #86909c;
  font-size: 14px;
  line-height: 1.6;
  border: 1px dashed #e5e6eb;
  border-radius: 12px;
  background: #fafbfc;
}

.progress-hint {
  padding-left: 20px; /* 给左边添加间距 */
  padding-right: 20px;
  margin-bottom: 16px;

  .p-title {
    font-weight: 600;
    color: #374151;
    margin-bottom: 8px;
  }

  .p-text {
    color: #6b7280;
    line-height: 1.6;
    margin: 0;
  }
}

/* 转让组长块 */
.transfer-leader-block {
  margin-bottom: 24px;
  padding: 16px;
  background: #fff9e6;
  border-radius: 8px;
  border: 1px solid #ffe58f;
}

.tlb-title {
  font-size: 14px;
  font-weight: 600;
  color: #d46b08;
  margin-bottom: 8px;
}

.tlb-desc {
  font-size: 13px;
  color: #8c8c8c;
  margin-bottom: 12px;
}
</style>
