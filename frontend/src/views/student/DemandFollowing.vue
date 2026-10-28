<script setup>
/**
 * 学生端 - 需求关注（精简后的版本：去掉参与者接口调用 + 静默评分获取）
 */
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Document, Collection, FolderOpened, ChatSquare } from '@element-plus/icons-vue'
import {
  getProjectList,
  applyProject,
  createProject,
  getProjectDetail
  // getProjectParticipants  // 已移除：不再请求参与者
} from '@/api/student/project'
import { getRequirementDetail } from '@/api/student/requirement'
import {
  getRequirementResult,
  publishRequirementResult,
  getProjectScoreRanking
} from '@/api/student/requirementResult'
import { getResourceList, downloadResource } from '@/api/student/resource'
import AgentChat from '@/components/AgentChat.vue'
import { useRouter } from 'vue-router'
import request from '@/utils/request'
import { fetchFollowedDemands, followDemand, unfollowDemand } from '@/api'
// === 新增 BEGIN：申请弹窗所需依赖 ===
import { useUserStore } from '@/stores'

// === 新增 END ===

const router = useRouter()

/* ========== 用户及身份辅助 ========== */
const getCurrentUsername = () => {
  const ls = typeof localStorage !== 'undefined' ? localStorage : null
  if (!ls) return ''
  try {
    const raw =
      ls.getItem('currentUser') || ls.getItem('user') || ls.getItem('profile') || ls.getItem('me')
    if (raw) {
      const u = JSON.parse(raw)
      return u?.username ?? u?.real_name ?? ''
    }
  } catch {
    /* ignore */ void 0
  }
  return ls.getItem('username') || ''
}
const currentLogin = getCurrentUsername() || 'student'

const tryParseJSON = (v) => {
  try {
    return JSON.parse(v)
  } catch {
    return null
  }
}

const collectMyIdCandidates = () => {
  const ids = new Set()
  if (typeof window !== 'undefined') {
    const g = window
    ;[g.__USER_ID__, g.__userId__, g.__uid__, g.__ACCOUNT_ID__, g.__STUDENT_ID__].forEach((x) => {
      const n = Number(x)
      if (!Number.isNaN(n)) ids.add(n)
    })
  }
  const ls = typeof localStorage !== 'undefined' ? localStorage : null
  if (ls) {
    ;[
      'userId',
      'uid',
      'id',
      'user_id',
      'account_id',
      'accountId',
      'studentId',
      'student_id'
    ].forEach((k) => {
      const raw = ls.getItem(k)
      if (raw != null && raw.trim() !== '') {
        const n = Number(raw)
        if (!Number.isNaN(n)) ids.add(n)
      }
    })
    const rawUser =
      ls.getItem('currentUser') || ls.getItem('user') || ls.getItem('profile') || ls.getItem('me')
    const obj = rawUser ? tryParseJSON(rawUser) : null
    ;[
      obj?.id,
      obj?.user?.id,
      obj?.student?.id,
      obj?.data?.id,
      obj?.data?.user?.id,
      obj?.data?.student?.id,
      obj?.user_id,
      obj?.account_id,
      obj?.student_id
    ]
      .filter((x) => x != null)
      .forEach((x) => {
        const n = Number(x)
        if (!Number.isNaN(n)) ids.add(n)
      })
  }
  return Array.from(ids)
}
const myIdCandidates = ref(collectMyIdCandidates())

/* 判断成员（已不再请求参与者，保留函数以兼容可能的调用） */
const isMeByParticipant = (p) => {
  const cand = myIdCandidates.value
  const ids = [p?.student?.id, p?.user_id, p?.student?.user_id]
    .map((x) => (x == null ? null : Number(x)))
    .filter((x) => !Number.isNaN(x))
  if (ids.some((x) => cand.includes(x))) return true
  const login = currentLogin.trim().toLowerCase()
  const uname = String(p?.student?.username || p?.name || '')
    .trim()
    .toLowerCase()
  return !!login && !!uname && login === uname
}

/* 文件大小格式化 */
function formatFileSize(bytes) {
  if (bytes === 0 || !bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/* ========== 主状态 ========== */
const followedDemands = ref([])
const loading = ref(false)
const myProjectIds = ref(new Set())

/* 我的项目 ID 集合 */
const loadMyProjectIds = async () => {
  try {
    const [respLeader, respJoined] = await Promise.all([
      getProjectList({ my_projects: true, page: 1, page_size: 500 }),
      getProjectList({ my_projects: false, page: 1, page_size: 500 })
    ])
    const list1 = respLeader?.data?.data?.projects || respLeader?.data?.projects || []
    const list2 = respJoined?.data?.data?.projects || respJoined?.data?.projects || []
    myProjectIds.value = new Set([...list1, ...list2].map((p) => p.id))
  } catch {
    myProjectIds.value = new Set()
  }
}

/* ========== 分页 ========== */
const currentPage = ref(1)
const pageSize = 4
const pagedDemands = computed(() => {
  const start = (currentPage.value - 1) * pageSize
  return followedDemands.value.slice(start, start + pageSize)
})
const handlePageChange = (p) => (currentPage.value = p)

// === 替换 BEGIN：资源汇总逻辑（需求详情 + 企业资源） ===

/**
 * 规范化单个资源条目
 * @param raw 原始资源（组织资源接口返回）
 */
function mapOrgResource(raw) {
  const sizeSum = Array.isArray(raw.files)
    ? raw.files.reduce((acc, f) => acc + (Number(f.size) || 0), 0)
    : 0
  return {
    id: raw.id, // 组织资源真实 id（数字）
    source: 'organization', // 来源：组织资源接口
    title: raw.title || raw.name || '',
    name: raw.title || raw.name || '',
    description: raw.description || '',
    type: raw.type || '',
    status: raw.status || '',
    tag1: raw.tag1 || [],
    tag2: raw.tag2 || [],
    downloads: raw.downloads ?? 0,
    views: raw.views ?? 0,
    created_at: raw.created_at || '',
    updated_at: raw.updated_at || '',
    files: Array.isArray(raw.files) ? raw.files : [],
    size: sizeSum,
    uploadedAt: raw.created_at || raw.updated_at || '',
    url: '', // 在点击下载时再通过 downloadResource 拿文件
    synthetic: false
  }
}

/**
 * 把需求详情里的 files 数组（可能是字符串路径）转成“伪资源”列表
 * @param demand 当前需求
 * @param files 需求详情返回的 files（数组）
 */
function buildRequirementFileResources(demand, files) {
  if (!Array.isArray(files) || !files.length) return []
  return files
    .map((f, idx) => {
      if (!f) return null
      // f 可能是对象或字符串（相对路径 / URL）
      const isFileObj = f && typeof f === 'object'
      const fileName = isFileObj
        ? f.name
        : typeof f === 'string'
          ? f.split('/').pop()
          : `file_${idx}`
      const fileSize = isFileObj ? Number(f.size) || 0 : 0
      return {
        id: `reqfile-${demand.id}-${idx}`,
        source: 'requirement-file', // 来源：需求详情里的 files 字段
        title: fileName,
        name: fileName,
        description: '需求附件文件',
        type: isFileObj ? f.type || 'file' : 'file',
        status: 'published',
        tag1: [],
        tag2: [],
        downloads: 0,
        views: 0,
        created_at: isFileObj ? f.created_at : '',
        updated_at: isFileObj ? f.updated_at : '',
        files: [
          {
            id: `${demand.id}-${idx}`,
            name: fileName,
            path: isFileObj ? f.url : f,
            url: isFileObj ? f.url : f,
            download_url: isFileObj ? f.download_url || f.url : f,
            size: fileSize,
            is_folder: false
          }
        ],
        size: fileSize,
        uploadedAt: isFileObj ? f.created_at : '',
        url: isFileObj ? f.url : f,
        synthetic: true // 标记为本地合成
      }
    })
    .filter(Boolean)
}

/**
 * 如果需求详情里有 resources 字段（数组）且为对象列表，也转为“伪资源”或合并 id
 * 注：后端文档中 resources 可能是字符串列表或对象列表，做兼容
 */
function buildRequirementInnerResources(demand, resources) {
  if (!Array.isArray(resources) || !resources.length) return []
  return resources
    .map((r, idx) => {
      if (r && typeof r === 'object' && r.id) {
        return {
          id: `reqres-${demand.id}-${r.id}`,
          source: 'requirement-resource',
          title: r.title || r.name || `需求资源#${r.id}`,
          name: r.title || r.name || `需求资源#${r.id}`,
          description: r.description || '需求附属资源',
          type: r.type || 'resource',
          status: r.status || '',
          tag1: r.tag1 || [],
          tag2: r.tag2 || [],
          downloads: r.downloads ?? 0,
          views: r.views ?? 0,
          created_at: r.created_at || '',
          updated_at: r.updated_at || '',
          files: Array.isArray(r.files) ? r.files : [],
          size: 0,
          uploadedAt: r.created_at || r.updated_at || '',
          url: '',
          synthetic: true
        }
      }
      if (typeof r === 'string') {
        const fileName = r.split('/').pop()
        return {
          id: `reqresstr-${demand.id}-${idx}`,
          source: 'requirement-resource-string',
          title: fileName || `需求资源_${idx + 1}`,
          name: fileName || `需求资源_${idx + 1}`,
          description: '需求资源（字符串）',
          type: 'resource',
          status: '',
          tag1: [],
          tag2: [],
          downloads: 0,
          views: 0,
          created_at: '',
          updated_at: '',
          files: [
            {
              id: `${demand.id}-rs-${idx}`,
              name: fileName,
              path: r,
              url: r,
              download_url: r,
              size: 0,
              is_folder: false
            }
          ],
          size: 0,
          uploadedAt: '',
          url: r,
          synthetic: true
        }
      }
      return null
    })
    .filter(Boolean)
}

/**
 * 拉取某企业(organization)所有资源（分页）
 */
async function fetchAllOrganizationResources(orgId, pSize = 50, maxPages = 10) {
  if (!orgId) return []
  let page = 1
  let totalPages = 1
  const acc = []
  while (page <= totalPages && page <= maxPages) {
    try {
      const resp = await getResourceList({
        organization_id: orgId,
        page,
        page_size: pSize,
        status: 'published,unpublished' // 可按需求只要发布态 -> 'published'
      })
      if (resp?.data?.status !== 'success') break
      const data = resp.data.data || {}
      const list = data.resources || []
      acc.push(...list)
      const pg = data.pagination || {}
      totalPages = pg.total_pages || 1
      page += 1
    } catch {
      break
    }
  }
  return acc
}

/**
 * 主方法：为需求加载全部资源（需求详情 + 企业资源）
 * 会写入 demand.resources
 */
async function loadResourcesForDemand(demand) {
  if (!demand?.id) return
  const combined = []
  // A. 需求详情
  try {
    const respDetail = await getRequirementDetail(demand.id)
    if (respDetail?.data?.status === 'success') {
      const req = respDetail.data.data || {}
      // 需求级 files
      const fileRes = buildRequirementFileResources(demand, req.files)
      combined.push(...fileRes)
      // 需求级 resources
      const inner = buildRequirementInnerResources(demand, req.resources)
      combined.push(...inner)
      // 存储需求“原始资源引用”以便后续刷新
      demand._rawReqResources = req.resources || []
      demand._rawReqFiles = req.files || []
      demand.evaluationPublished = !!req.evaluation_published // 新增：记录公示状态
    }
  } catch {
    /* ignore */
  }

  // B. 企业全部资源
  if (demand.organization_id) {
    try {
      const orgList = await fetchAllOrganizationResources(demand.organization_id, 50, 10)
      const mapped = orgList.map(mapOrgResource)
      combined.push(...mapped)
    } catch {
      /* ignore */
    }
  }

  // C. 去重（以 id + source 组合做唯一性）
  const uniqMap = new Map()
  combined.forEach((r) => {
    const key = `${r.source}::${r.id}`
    if (!uniqMap.has(key)) uniqMap.set(key, r)
  })
  demand.resources = Array.from(uniqMap.values())

  // 调试输出
  console.log('已加载资源:', {
    demandId: demand.id,
    totalResources: demand.resources.length,
    resources: demand.resources
  })
}

/**
 * 手动刷新：重新获取（覆盖）
 */
const refreshDemandResources = async (demand) => {
  if (!demand?.id) return
  await loadResourcesForDemand(demand)
  ElMessage.success('资源已刷新')
}
// === 替换 END：资源汇总逻辑 ===

function mapFollowedItem(raw) {
  const tagNames = [
    ...((raw.tag1 || []).map((t) => t?.name || t) || []),
    ...((raw.tag2 || []).map((t) => t?.name || t) || [])
  ].filter(Boolean)

  return {
    id: raw.id,
    organization_id:
      raw.organization_id ||
      raw.organizationId ||
      raw.organization?.id ||
      raw.company?.id ||
      raw.org_id ||
      raw.orgId,
    organizationName: raw.organization?.name || raw.organization_name || '',
    title: raw.title || raw.name || `需求 #${raw.id}`,
    publisher:
      raw.publish_people || raw.publisher || raw.organization?.name || raw.company?.name || '',
    publisherLogin: `company_${raw.publish_people || raw.publisher || ''}`,
    domain: raw.field || raw.domain || '未分类',
    deadline: raw.finish_time || raw.deadline || '待定',
    budget: raw.budget || '—',
    tags: tagNames,
    briefDescription:
      raw.brief || raw.summary || (raw.description ? String(raw.description).slice(0, 100) : ''),
    messageDescription: raw.description || '',
    supportProvided: raw.support_provided || '',
    resources: [],
    _rawReqResources: Array.isArray(raw.resources) ? raw.resources : [],
    teams: [],
    evaluationPublished: !!raw.evaluation_published,
    result: { status: 'pending', publishedAt: '', rankings: [] }
  }
}

function filterResourcesForRequirement(all, reqId, knownReqResources) {
  if (knownReqResources?.length) {
    const idSet = new Set(knownReqResources.map((r) => r.id))
    return all.filter((r) => idSet.has(r.id))
  }
  const candidates = all.filter((r) => {
    const rid =
      r.requirement_id ||
      r.req_id ||
      (typeof r.requirement === 'number' && r.requirement) ||
      (typeof r.requirement?.id === 'number' && r.requirement.id)
    if (rid && Number(rid) === Number(reqId)) return true
    const arr = r.requirement_ids || r.requirements || r.requirement_list || r.req_ids || r.req_list
    if (Array.isArray(arr) && arr.map(Number).includes(Number(reqId))) return true
    return false
  })
  if (candidates.length) return candidates
  return all
}

/* ========== 加载关注需求 ========== */
const loadFollowedDemands = async () => {
  loading.value = true
  try {
    // 服务端分页参数可按需调整
    const resp = await fetchFollowedDemands({ page: 1, page_size: 200 })
    const payload = resp?.data?.data ?? resp?.data ?? {}

    // 收藏列表接口返回 data.results，需求实体在每项的 requirement 字段里
    const results =
      payload.results ??
      payload.list ??
      payload.items ??
      payload.records ??
      payload.rows ??
      (Array.isArray(payload) ? payload : [])

    const requirementArray = (results || [])
      .map((row) => row?.requirement || row) // 兼容意外结构
      .filter(Boolean)

    followedDemands.value = requirementArray.map(mapFollowedItem)

    // 继续加载队伍/资源/结果（均为服务端接口）
    for (const demand of followedDemands.value) {
      await loadResourcesForDemand(demand) // 先加载资源
      await loadTeamsForDemand(demand)
      await loadResultForDemand(demand)
    }

    const total = followedDemands.value.length
    const maxPage = Math.max(1, Math.ceil(total / pageSize))
    if (currentPage.value > maxPage) currentPage.value = maxPage
  } catch (e) {
    console.error(e)
    ElMessage.error('获取需求列表失败')
  } finally {
    loading.value = false
  }
}

/* ========== 队伍（已移除参与者请求，避免 403） ========== */
const loadTeamsForDemand = async (demand) => {
  if (!demand?.id) return
  try {
    const resp = await getProjectList({
      requirement_id: demand.id,
      page: 1,
      page_size: 50
    })
    if (resp.data.status === 'success') {
      const projects = resp.data.data.projects || []
      demand.teams = projects.map((project) => {
        const ld = project.leader || {}
        const leaderIds = []
        if (typeof ld.id === 'number') leaderIds.push(ld.id)
        if (typeof ld.user?.id === 'number') leaderIds.push(ld.user.id)
        if (typeof ld.student?.id === 'number') leaderIds.push(ld.student.id)
        if (typeof project.leader_id === 'number') leaderIds.push(project.leader_id)

        const isMine =
          myProjectIds.value.has(project.id) ||
          leaderIds.some((n) => myIdCandidates.value.includes(Number(n)))

        return {
          id: project.id,
          name: project.title,
          //affiliation: project.affiliation || '学生团队',
          affiliation: getProjectAffiliation(project),
          creator: project.leader?.username || project.creator,
          //createdAt: project.created_at ? new Date(project.created_at).toLocaleString() : '',
          createdAt: formatDateTime(project.created_at),
          status: getProjectStatusText(project.status),
          //progress: getProjectProgress(project.status),
          deliverables: project.deliverables || [],
          leaderIds,
          isMine,
          members: [],
          pendingApplicants: []
        }
      })
    } else {
      demand.teams = []
    }
  } catch {
    demand.teams = []
  }
}

/* ========== 结果发布（企业已发布的排名） ========== */
const loadResultForDemand = async (demand) => {
  if (!demand?.id) return

  // 仅在已公示标记为 true 时才请求新排名接口，避免 422
  if (demand.evaluationPublished) {
    try {
      const rankingRes = await getProjectScoreRanking(demand.id)
      if (
        rankingRes?.status === 'success' &&
        rankingRes?.data?.requirement?.evaluation_published &&
        Array.isArray(rankingRes.data.projects) &&
        rankingRes.data.projects.length
      ) {
        const publishedAt =
          rankingRes.data.requirement.published_at || rankingRes.data.requirement.publishedAt || ''
        const rankings = rankingRes.data.projects.map((p) => ({
          teamId: p.project || p.project_id || p.id,
          teamName: p.title || p.project_title || p.project_name || `项目#${p.project}`,
          score: p.final_score ?? p.weighted_score ?? p.total_score ?? p.score ?? '',
          award: p.rank_level_display || p.rank_level || '',
          remark: p.remark || p.comment || '',
          rank: p.rank
        }))
        demand.result = {
          status: 'published',
          publishedAt,
          rankings
        }
        demand.evaluationPublished = true
        return
      }
      // 若返回 pending（我们在 API 层定义的 422 映射）或其他非 success，继续尝试旧接口
    } catch {
      // 静默：继续旧接口
    }
  }

  // 兼容旧结果接口（老模式）
  try {
    const res = await getRequirementResult(demand.id)
    if (res.data?.status === 'success') {
      const data = res.data.data || {}
      const publishedAt = data.published_at || data.publishedAt || ''
      const rankings = (data.rankings || []).map((r) => ({
        teamId: r.team_id ?? r.teamId,
        teamName: r.team_name ?? r.teamName,
        score: r.score ?? '',
        award: r.award ?? '',
        remark: r.remark ?? '',
        rank: r.rank ?? 0
      }))
      if (rankings.length) {
        demand.result = {
          status: 'published',
          publishedAt,
          rankings
        }
        demand.evaluationPublished = true
      }
    }
  } catch {
    // 静默
  }
}

/* 状态/进度文本 */
const getProjectStatusText = (status) => {
  const statusMap = {
    draft: '草稿',
    recruiting: '招募中',
    in_progress: '进行中',
    completed: '已完成',
    suspended: '已暂停',
    cancelled: '已取消'
  }
  return statusMap[status] || status
}

// === 新增：通用格式化与状态标签类型映射 BEGIN ===
const formatDateTime = (s) => {
  if (!s) return ''
  // 统一去掉毫秒与时区，替换 T 为空格，只保留到秒
  // 例: 2025-09-12T11:56:59.123456+08:00 => 2025-09-12 11:56:59
  const core = String(s)
    .replace('T', ' ')
    .replace(/\.\d+/, '')
    .replace(/Z|[+-]\d{2}:?\d{2}$/i, '')

  try {
    // 尝试转换为本地时间
    const date = new Date(s)
    if (!isNaN(date.getTime())) {
      return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      })
    }
  } catch {
    // 如果转换失败，返回原始格式化结果
  }

  return core.trim()
}

const mapStatusType = (s) => {
  const m = {
    草稿: 'info',
    招募中: 'success',
    进行中: 'warning',
    已完成: '',
    已暂停: 'danger',
    已取消: 'danger'
  }
  return m[s] || 'info'
}
// === 新增：通用格式化与状态标签类型映射 END ===

/*
const getProjectProgress = (status) => {
  const progressMap = {
    draft: 0,
    recruiting: 20,
    in_progress: 50,
    completed: 100,
    suspended: 30,
    cancelled: 0
  }
  return progressMap[status] != null ? progressMap[status] : 0
}
*/

/* ========== 选择需求 & 取消关注 ========== */
const selectedDemandId = ref(null)
const selectedDemand = computed(
  () => followedDemands.value.find((d) => d.id === selectedDemandId.value) || null
)
const unfollowConfirmVisible = ref(false)
const unfollowTarget = ref(null)
const openUnfollowConfirm = (d) => {
  unfollowTarget.value = d
  unfollowConfirmVisible.value = true
}
const confirmUnfollow = async () => {
  const d = unfollowTarget.value
  if (!d?.id) return
  try {
    await unfollowDemand(d.id)
    // 本地移除 UI 项（来源数据由服务端驱动）
    const idx = followedDemands.value.findIndex((x) => x.id === d.id)
    if (idx >= 0) {
      followedDemands.value.splice(idx, 1)
      const total = followedDemands.value.length
      const maxPage = Math.max(1, Math.ceil(total / pageSize))
      if (currentPage.value > maxPage) currentPage.value = maxPage
      if (selectedDemandId.value === d.id) {
        const start = (currentPage.value - 1) * pageSize
        selectedDemandId.value = followedDemands.value[start]?.id || null
      }
    }
    ElMessage.success('已取消收藏')
  } catch (e) {
    console.error(e)
    ElMessage.error(e?.message || '取消收藏失败')
  } finally {
    unfollowConfirmVisible.value = false
  }
}

/* ===== 项目隶属主体本地缓存与解析 ===== */
const saveProjectAffiliation = (id, affiliation) => {
  if (!id) return
  try {
    localStorage.setItem(`project:aff:${id}`, affiliation || '')
  } catch {
    /* ignore */
  }
}
const getSavedProjectAffiliation = (id) => {
  if (!id) return ''
  try {
    return localStorage.getItem(`project:aff:${id}`) || ''
  } catch {
    return ''
  }
}
const parseAffiliationFromDescription = (desc) => {
  if (!desc) return ''
  // 例如 “计算机学院团队，成员：...” 提取 “计算机学院”
  const m = desc.match(/^(.+?)团队[，,。]/)
  return m ? m[1].trim() : ''
}
const getProjectAffiliation = (project) => {
  return (
    project.affiliation ||
    getSavedProjectAffiliation(project.id) ||
    parseAffiliationFromDescription(project.description) ||
    '学生团队'
  )
}

/* 导航 */
const activeTab = ref('overview')
// 知途 v0：只保留机会简介和智能体问答；资料、组队、结果发布 v1 再按调研决定
const navs = [
  { key: 'overview', title: '机会简介', desc: '名称 · 标签 · 简介 · 详情', icon: Document },
  { key: 'ai', title: '智能体问答', desc: '问我这个机会的细节', icon: ChatSquare }
]
const _hiddenNavs = [
  { key: 'resources', title: '了解更多', desc: '需求相关资料', icon: FolderOpened },
  { key: 'teams', title: '揭榜立项', desc: '揭榜立项 / 加入 / 查看队伍', icon: Collection },
  { key: 'results', title: '结果发布', desc: '排名 · 奖项 · 分数', icon: Document }
]
const getTagClass = (t) => {
  if (!t) return ''
  const k = t.toLowerCase()
  if (['ai', 'nlp', 'python', 'tensorflow'].some((x) => k.includes(x))) return 'tag--ai'
  if (['vue', 'echarts', 'd3'].some((x) => k.includes(x))) return 'tag--fe'
  return 'tag--default'
}

// 新增：获取资源的文件类型（扩展名），无文件时回退到资源.type
const getRowFileType = (row) => {
  const files = Array.isArray(row?.files) ? row.files : []
  const f = files.length ? files[0] : null
  const pickExt = (s) => {
    if (!s || typeof s !== 'string') return ''
    const i = s.lastIndexOf('.')
    return i >= 0 ? s.slice(i + 1).toLowerCase() : ''
  }
  const extFromName = pickExt(f?.name)
  if (extFromName) return extFromName
  const extFromPath = pickExt(f?.path || f?.url || f?.download_url)
  if (extFromPath) return extFromPath
  return row?.type || '未知'
}

/* 打开资源 */
// === 替换 BEGIN：openResource （支持伪资源 + 组织资源 + 懒加载下载文件） ===
const openResource = async (row) => {
  if (!row) {
    ElMessage.info('无可下载资源')
    return
  }
  row.downloading = true

  try {
    // 1) 伪资源（需求文件 / 需求内资源字符串或对象） -- 直接使用已有的文件信息
    if (row.synthetic) {
      const firstFile = Array.isArray(row.files) && row.files.length ? row.files[0] : null
      const link = firstFile?.download_url || firstFile?.url || row.url
      if (!link) {
        ElMessage.info('暂无文件')
        return
      }
      const full = link.startsWith('http') ? link : buildApiUrl(link)
      // 直接打开，不做 HEAD 探测，避免服务器限制
      window.open(full, '_blank')
      return
    }

    // 2) 组织资源（需要调用下载接口拿真正的文件 URL）
    if (typeof row.id === 'number') {
      // 若还未取过下载文件列表，则调用后端
      if (!row._fetchedDownload) {
        const resp = await downloadResource(row.id)
        const payload = resp?.data ?? {}
        if (payload.status !== 'success') {
          ElMessage.error(payload.message || '获取下载信息失败')
          return
        }
        const data = payload.data || {}
        const files = Array.isArray(data.files) ? data.files : []
        if (!files.length) {
          ElMessage.info('暂无可下载文件')
          return
        }
        // 归一化：补齐绝对地址 & 统一属性
        row.files = files.map((f) => {
          const abs =
            f.download_url && f.download_url.startsWith('http')
              ? f.download_url
              : buildApiUrl(f.download_url || f.url || f.path || '')
          return {
            id: f.id,
            name: f.name,
            size: Number(f.size) || 0,
            download_url: abs,
            created_at: f.created_at || ''
          }
        })
        row.size = row.files.reduce((acc, f) => acc + (f.size || 0), 0)
        row._fetchedDownload = true
      }

      if (!Array.isArray(row.files) || !row.files.length) {
        ElMessage.info('暂无可下载文件')
        return
      }

      // 打开第一个文件
      const first = row.files[0]
      const full = first.download_url
      if (!full) {
        ElMessage.info('下载地址不可用')
        return
      }
      window.open(full, '_blank')
      return
    }

    ElMessage.info('资源数据不完整')
  } catch (e) {
    console.error('下载失败', e)
    ElMessage.error(e?.message || '下载失败')
  } finally {
    row.downloading = false
  }
}
// === 替换 END ===

/* 创建项目（揭榜） */
const createDialogVisible = ref(false)
const createForm = reactive({
  name: '',
  //affiliation: '',
  members: [{ name: currentLogin, role: '组长/前端', contact: 'me@campus.edu' }]
})

// === 替换 BEGIN：openCreate ===
const openCreate = () => {
  if (!selectedDemand.value) return ElMessage.warning('请先选择一个需求')
  createForm.name = ''
  createForm.description = ''
  createDialogVisible.value = true
}
// === 替换 END ===
const addProjectToMyProjects = (proj) => {
  try {
    const list = JSON.parse(localStorage.getItem('myProjects:list') || '[]')
    list.push(proj)
    localStorage.setItem('myProjects:list', JSON.stringify(list))
  } catch {
    /* ignore */
  }
}
// === 替换 BEGIN：doCreateProject ===
const doCreateProject = async () => {
  const d = selectedDemand.value
  if (!d) return
  if (!createForm.name.trim()) return ElMessage.warning('请填写项目名')

  // 取当前用户作为队长展示（本地缓存用；服务端还是通过后端逻辑判定 leader）
  const leaderName = (
    userStore?.userInfo?.real_name ||
    userStore?.userInfo?.username ||
    currentLogin ||
    ''
  ).trim()

  try {
    const resp = await createProject({
      title: createForm.name.trim(),
      description: createForm.description.trim(),
      requirement: d.id,
      status: 'recruiting'
    })
    if (resp.data.status === 'success') {
      ElMessage.success('项目创建成功')
      createDialogVisible.value = false
      await loadMyProjectIds()
      await loadTeamsForDemand(d)

      const newId = resp.data.data.id
      // 本地加入缓存（简化成员：仅队长一人）
      addProjectToMyProjects({
        id: newId,
        name: `${d.title} - ${createForm.name.trim()}`,
        demandId: d.id,
        demandTitle: d.title,
        shortDescription: d.briefDescription,
        status: '招募中',
        publisher: d.publisher,
        joinDate: new Date().toLocaleDateString(),
        deliverablesCount: 0,
        members: [
          {
            id: 1,
            name: leaderName || '我',
            avatar: 'https://i.pravatar.cc/40?img=5',
            role: '组长'
          }
        ],
        tags: (d.tags || []).slice(0, 3)
      })
    } else {
      ElMessage.error(resp.data.message || '创建失败')
    }
  } catch (e) {
    console.error('创建项目失败', e)
    ElMessage.error('创建项目失败')
  }
}
// === 替换 END ===

/* 申请加入队伍 */
const teamDetailVisible = ref(false)
const teamDetail = ref(null)

// === 项目详情弹窗（查看队伍）新增状态 BEGIN ===
const teamDetailLoading = ref(false)
const teamDetailLeader = ref(null) // 队长详细信息（来自项目详情 leader）
const teamDetailIntro = ref('') // 项目介绍（后端 description / brief_description）

const mapLeader = (l = {}) => ({
  id: l.id,
  username: l.username,
  realName: l.real_name || l.username || '',
  avatar: l.avatar || '',
  phone: l.phone || '',
  major: l.major || '',
  grade: l.grade || '',
  email: l.email || ''
})
// === 项目详情弹窗（查看队伍）新增状态 END ===

const openTeamDetail = async (team) => {
  if (!team?.id) return
  teamDetailVisible.value = true
  teamDetailLoading.value = true
  teamDetail.value = team // 先放入基本行数据以便占位
  teamDetailLeader.value = null
  teamDetailIntro.value = ''
  try {
    const resp = await getProjectDetail(team.id)
    const data = resp?.data?.data || resp?.data || {}
    // 基础信息（全部来自后端）
    const statusText =
      {
        draft: '草稿',
        recruiting: '招募中',
        in_progress: '进行中',
        completed: '已完成',
        suspended: '已暂停',
        cancelled: '已取消'
      }[data.status] ||
      data.status ||
      team.status

    teamDetail.value = {
      ...teamDetail.value,
      name: data.title || team.name,
      createdAt: formatDateTime(data.created_at || team.createdAt || ''),
      status: statusText
    }
    teamDetailIntro.value =
      data.description ||
      data.brief_description ||
      data.brief ||
      (typeof data.description === 'string' ? data.description : '') ||
      ''
    teamDetailLeader.value = mapLeader(data.leader || {})
  } catch (e) {
    console.error('加载项目详情失败', e)
    ElMessage.error('加载项目详情失败')
  } finally {
    teamDetailLoading.value = false
  }
}
const applyDialogVisible = ref(false)
const applyTargetTeam = ref(null)
// 申请加入表单（六个基础字段 + 申请理由；六个基础字段来自后端用户信息，不允许编辑）
const applyForm = reactive({
  real_name: '', // 姓名
  school_name: '', // 学校
  grade: '', // 年级
  major: '', // 专业
  phone: '', // 电话
  email: '', // 邮箱
  reason: '' // 申请理由（仅用户输入）
})

// === 替换 BEGIN：加载当前学生基础信息（多来源兜底） ===
async function loadApplicantBaseInfo() {
  // 1. 首选 userStore
  const base = userStore && userStore.user ? userStore.user : {}
  const sp = base.student_profile || base.profile || {}

  // 2. JWT 解析兜底（Authorization 中的 access token）
  function decodeJwt(token) {
    try {
      const parts = token.split('.')
      if (parts.length !== 3) return {}
      const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')))
      return payload || {}
    } catch {
      return {}
    }
  }
  let jwtPayload = {}
  try {
    const auth =
      request?.defaults?.headers?.common?.Authorization ??
      request?.defaults?.headers?.Authorization ??
      localStorage.getItem('Authorization') ??
      localStorage.getItem('authorization') ??
      ''
    const pure = auth.replace(/^Bearer\s+/i, '')
    if (pure) jwtPayload = decodeJwt(pure)
  } catch {
    /* ignore */
  }

  // 3. 如果关键字段缺失，尝试用“我的项目列表”接口拿一个我创建/加入的项目，取 leader 作为个人信息（服务端已有接口，非本地模拟）
  let projectDerived = {}
  const needFetchFromProject =
    !(base.real_name || base.username || sp.real_name) ||
    !(base.school || sp.school) ||
    !(base.phone || sp.phone || base.mobile || sp.mobile)

  if (needFetchFromProject) {
    try {
      const resp = await getProjectList({ my_projects: true, page: 1, page_size: 1 })
      if (resp?.data?.status === 'success') {
        const first = (resp.data.data?.projects || [])[0]
        if (first?.leader) {
          projectDerived = first.leader
        } else if (first?.participants?.length) {
          // 兜底：把参加者里与 jwt user_id 匹配的那条当作我
          const uid = Number(jwtPayload.user_id)
          if (uid) {
            const m = first.participants.find(
              (p) => Number(p.id) === uid || Number(p.user_id) === uid
            )
            if (m) projectDerived = m
          }
        }
      }
    } catch {
      /* ignore */
    }
  }

  const prefer = (...vals) => vals.find((v) => v !== undefined && v !== null && v !== '') || ''

  // 归一化学校
  function normSchool(raw) {
    if (!raw) return ''
    if (typeof raw === 'string') return raw
    if (typeof raw === 'object') return raw.name || raw.title || raw.label || raw.school_name || ''
    return ''
  }

  const schoolRaw =
    prefer(base.school, base.school_name, sp.school, sp.school_name) ||
    prefer(projectDerived.school) ||
    ''

  applyForm.real_name = prefer(
    base.real_name,
    sp.real_name,
    base.username,
    projectDerived.real_name,
    projectDerived.username,
    ''
  )
  applyForm.school_name = normSchool(schoolRaw)
  applyForm.grade = prefer(base.grade, sp.grade, projectDerived.grade, base.grade_name)
  applyForm.major = prefer(base.major, sp.major, projectDerived.major, projectDerived.profession)
  applyForm.phone = prefer(base.phone, sp.phone, base.mobile, sp.mobile, projectDerived.phone)
  applyForm.email = prefer(base.email, sp.email, base.mail, sp.mail, projectDerived.email)

  // 清空理由
  if (typeof applyForm.reason !== 'string')
    applyForm.reason = ''

    // 将空字段统一显示占位（防止前端看起来像加载失败）
  ;['real_name', 'school_name', 'grade', 'major', 'phone', 'email'].forEach((k) => {
    if (!applyForm[k]) applyForm[k] = '（未提供）'
  })
}
// === 替换 END ===

// === 替换 BEGIN：openApply ===
const openApply = async (team) => {
  if (!team?.id) return
  applyTargetTeam.value = team
  await loadApplicantBaseInfo() // 每次打开实时刷新
  applyForm.reason = ''
  applyDialogVisible.value = true
}
// === 替换 END ===
const submitApply = async () => {
  const team = applyTargetTeam.value
  if (!team) return
  const reason = (applyForm.reason || '').trim()

  if (!reason) {
    ElMessage.warning('请填写申请理由')
    return
  }

  try {
    const resp = await applyProject(team.id, {
      // 只提交用户填写的理由，不再拼接其它信息
      application_message: reason
    })
    if (resp.data?.status === 'success') {
      ElMessage.success('申请已提交')
      applyDialogVisible.value = false
    } else {
      ElMessage.error(resp.data?.message || '申请失败')
    }
  } catch (e) {
    console.error('申请失败', e)
    ElMessage.error('申请失败')
  }
}

/* 企业是否可发布结果 */
const amEnterpriseOwner = computed(
  () => !!selectedDemand.value && selectedDemand.value.publisherLogin === currentLogin
)
const isPublisher = amEnterpriseOwner
const resultDialogVisible = ref(false)
const resultFormRows = ref([])
const openResultPublish = () => {
  const d = selectedDemand.value
  if (!d) return
  if (d.result?.status === 'published') {
    resultFormRows.value = (d.result.rankings || []).map((r) => ({ ...r }))
  } else {
    resultFormRows.value = (d.teams || []).map((t, i) => ({
      teamId: t.id,
      teamName: t.name,
      score: '',
      award: '',
      remark: '',
      rank: i + 1
    }))
  }
  resultDialogVisible.value = true
}
const submitResultPublish = async () => {
  const d = selectedDemand.value
  if (!d) return
  const cleaned = (resultFormRows.value || [])
    .map((r) => ({
      ...r,
      rank: Number(r.rank) || 0,
      score: r.score === '' ? '' : Number(r.score)
    }))
    .filter((r) => r.teamId && r.teamName && r.rank > 0)
    .sort((a, b) => a.rank - b.rank)
  if (!cleaned.length) return ElMessage.warning('无有效排名记录')
  try {
    const resp = await publishRequirementResult(d.id, {
      rankings: cleaned.map((r) => ({
        team_id: r.teamId,
        team_name: r.teamName,
        score: r.score,
        award: r.award,
        remark: r.remark,
        rank: r.rank
      }))
    })
    if (resp.data?.status === 'success') {
      d.result = {
        status: 'published',
        publishedAt: new Date().toLocaleString(),
        rankings: cleaned
      }
      resultDialogVisible.value = false
      ElMessage.success('排名已发布')
    } else {
      ElMessage.error(resp.data?.message || '发布失败')
    }
  } catch {
    ElMessage.error('发布失败')
  }
}

/* ========== 评分排名（只请求有权限的队伍，静默无权限） ========== */
const rankingLoading = ref(false)
const rankingList = ref([])
const rankingMessage = ref('')

/* 构建基础 API URL */
const buildApiUrl = (path) => {
  const base = (request?.defaults?.baseURL || '').replace(/\/+$/, '')
  return base ? `${base}${path}` : path
}
const getAuthHeaders = () => {
  const h = {}
  try {
    const auth =
      request?.defaults?.headers?.common?.Authorization ?? request?.defaults?.headers?.Authorization
    if (auth && typeof auth === 'string') h.Authorization = auth.trim()
  } catch {
    /* ignore */
  }
  if (!h.Authorization) {
    try {
      const ls = typeof localStorage !== 'undefined' ? localStorage : null
      if (ls) {
        const raw =
          ls.getItem('Authorization') ??
          ls.getItem('authorization') ??
          ls.getItem('access_token') ??
          ls.getItem('accessToken') ??
          ls.getItem('token') ??
          ls.getItem('jwt')
        if (raw && raw.trim()) h.Authorization = raw.startsWith('Bearer ') ? raw : `Bearer ${raw}`
      }
    } catch {
      /* ignore */
    }
  }
  return h
}

/* 只对可访问项目发请求：isMine === true */
const fetchEvaluationSilent = async (projectId, probeOnly = false) => {
  const url = buildApiUrl(`/api/v1/projectscore/evaluations/${projectId}/`)
  try {
    const resp = await fetch(url, {
      credentials: 'include',
      headers: { 'X-Requested-With': 'XMLHttpRequest', ...getAuthHeaders() }
    })
    // 401 / 403 / 404 直接标记
    if (resp.status === 401 || resp.status === 403) {
      return { ok: false, unauthorized: true, data: null }
    }
    if (resp.status === 404) {
      return { ok: false, notFound: true, data: null }
    }
    if (!resp.ok) {
      return { ok: false, data: null }
    }
    const json = await resp.json().catch(() => null)
    const data = json?.data || json || null
    return { ok: !!data, data }
  } catch {
    return { ok: false, data: null }
  }
}

const extractNumber = (v) => {
  if (v == null) return NaN
  if (typeof v === 'number') return v
  const m = String(v).match(/-?\d+(\.\d+)?/)
  return m ? Number(m[0]) : NaN
}
const pickFirst = (...vals) => vals.find((x) => x !== undefined && x !== null)
const normalizeEvaluation = (p) => {
  if (!p || typeof p !== 'object') return { scoreNum: NaN, status: '', remark: '' }
  const scoreRaw = pickFirst(
    p.weighted_score,
    p.total_score,
    p.final_score,
    p.score,
    p.overall_score,
    p?.data?.weighted_score,
    p?.data?.total_score,
    p?.data?.final_score,
    p?.data?.score,
    p?.evaluation?.weighted_score,
    p?.evaluation?.total_score,
    p?.evaluation?.score,
    p?.result?.weighted_score,
    p?.result?.total_score,
    p?.result?.score
  )
  const statusRaw = pickFirst(p.status, p?.data?.status, p?.evaluation?.status, p?.result?.status)
  const remarkRaw = pickFirst(
    p.overall_comment,
    p.comment,
    p.remark,
    p?.data?.overall_comment,
    p?.evaluation?.overall_comment,
    p?.result?.overall_comment
  )
  return {
    scoreNum: extractNumber(scoreRaw),
    status: String(statusRaw || '').toLowerCase(),
    remark: remarkRaw || ''
  }
}

// 放在 handleGetRanking 定义前
const canTryEvaluation = computed(() => {
  const authOk = !!getAuthHeaders().Authorization
  const d = selectedDemand.value
  if (!authOk || !d) return false
  // 只有有“我相关”的队伍才有可能有权限
  return (d.teams || []).some((t) => t.isMine)
})

// 替换原 handleGetRanking
const handleGetRanking = async () => {
  const d = selectedDemand.value

  // 如果已公示并且已有正式排名，直接不再进行本地评测拼接
  if (d?.result?.status === 'published' && (d.result.rankings || []).length) {
    rankingMessage.value = '已公示'
    return
  }

  rankingList.value = []
  rankingMessage.value = ''

  if (!d || !(d.teams || []).length) {
    rankingMessage.value = '暂无评分'
    return
  }

  // 没有 token 或没有可尝试的“我的”队伍 => 直接显示暂无
  if (!canTryEvaluation.value) {
    rankingMessage.value = '暂无评分'
    return
  }

  // 只挑“我的”队伍
  const mineTeams = d.teams.filter((t) => t.isMine)
  if (!mineTeams.length) {
    rankingMessage.value = '暂无评分'
    return
  }

  rankingLoading.value = true
  try {
    // 先用第一支队伍做一次“探测”，如果 401/403/404 或无数据，直接结束
    const first = mineTeams[0]
    const probe = await fetchEvaluationSilent(first.id, true)
    if (!probe.ok) {
      rankingMessage.value = '暂无评分'
      return
    }

    // 继续并发其它（包含第一支，避免重复处理可再利用 probe）
    const restTeams = mineTeams.slice(1)
    const restResults = await Promise.all(
      restTeams.map(async (t) => {
        const r = await fetchEvaluationSilent(t.id)
        return { team: t, eval: r }
      })
    )

    // 组装全部结果（加上探测的第一支）
    const allResults = [{ team: first, eval: probe }, ...restResults].filter(
      (x) => x.eval.ok && x.eval.data
    )

    if (!allResults.length) {
      rankingMessage.value = '暂无评分'
      return
    }

    // 归一化 + 排序
    const statusOrder = { published: 3, submitted: 2, draft: 1 }
    const normalized = allResults
      .map(({ team, eval: e }) => {
        const { scoreNum, status, remark } = normalizeEvaluation(e.data)
        const valid = isFinite(scoreNum)
        return valid
          ? {
              teamId: team.id,
              projectName: team.name,
              _score: scoreNum,
              _statusWeight: statusOrder[status] || 0,
              totalScore: scoreNum.toFixed(2),
              remark: remark || ''
            }
          : null
      })
      .filter(Boolean)

    if (!normalized.length) {
      rankingMessage.value = '暂无评分'
      return
    }

    normalized.sort((a, b) => {
      if (b._statusWeight !== a._statusWeight) return b._statusWeight - a._statusWeight
      return b._score - a._score
    })

    rankingList.value = normalized.map((r, i) => ({
      rank: i + 1,
      projectId: r.teamId,
      projectName: r.projectName,
      totalScore: r.totalScore,
      remark: r.remark
    }))
  } finally {
    rankingLoading.value = false
  }
}

// === 新增：切换需求时重置本地排名状态，避免沿用上一需求的“已公示”显示 ===
watch(
  () => selectedDemandId.value,
  () => {
    const d = selectedDemand.value
    // 清理上一需求遗留的本地排名数据
    rankingLoading.value = false
    rankingList.value = []
    // 根据当前需求是否已公示设置文案；未公示时保持空字符串（等待用户点击按钮后再判定）
    rankingMessage.value = d?.result?.status === 'published' ? '已公示' : ''
  }
)

/* 队伍身份操作 */
const isMineTeam = (team) => !!team?.isMine || myProjectIds.value.has(team?.id)
const getTeamActionText = (team) => (isMineTeam(team) ? '进入项目' : '申请加入')
const handleTeamAction = (team) => {
  if (isMineTeam(team)) router.push(`/student/my-projects/${team.id}`)
  else openApply(team)
}

/* 对外接口 & 初始化 */
const handleJoinRequirement = async (requirementId) => {
  if (!requirementId) return
  try {
    await followDemand(requirementId)
    await loadFollowedDemands()
  } catch (e) {
    console.error(e)
    ElMessage.error(e?.message || '加入需求失败')
  }
}
defineExpose({ handleJoinRequirement, refreshDemandResources })

// === 新增 BEGIN：申请加入弹窗状态 ===
const userStore = useUserStore()

// 当前要申请加入的项目（队伍）信息
const applyingTeam = ref(null)

// 提交 loading
const applySubmitting = ref(false)

/**
 * 归一化学校：兼容字符串与对象
 */
function extractSchool(user) {
  const sp = user?.student_profile
  const s = sp?.school
  if (!s) return { id: '', name: '' }
  if (typeof s === 'string') return { id: '', name: s }
  return { id: s.id ?? '', name: s.name ?? s.title ?? s.label ?? '' }
}

// === 新增 END：申请加入弹窗状态 ===

onMounted(async () => {
  await loadMyProjectIds()
  await loadFollowedDemands()
  if (followedDemands.value.length) {
    const start = (currentPage.value - 1) * pageSize
    selectedDemandId.value = followedDemands.value[start]?.id
  }
})
</script>

<template>
  <div class="demand-following">
    <header class="page-header">
      <div class="title">我的收藏</div>
      <div class="sub">从下方卡片中选择一个你收藏的机会，查看介绍，或向智能体追问细节。</div>
    </header>

    <section class="follow-cards" v-if="followedDemands.length">
      <div class="cards">
        <article
          v-for="d in pagedDemands"
          :key="d.id"
          class="demand-card"
          :class="{ active: d.id === selectedDemandId }"
          role="button"
          tabindex="0"
          @click="selectedDemandId = d.id"
          @keydown.enter="selectedDemandId = d.id"
        >
          <div class="card-head">
            <h3 class="name">{{ d.title }}</h3>
            <div class="head-right">
              <span v-if="d.domain && d.domain !== '未分类'" class="badge">{{ d.domain }}</span>
              <el-button
                type="danger"
                size="small"
                class="unfollow-btn"
                @click.stop="openUnfollowConfirm(d)"
              >
                取消收藏
              </el-button>
            </div>
          </div>
          <p class="desc">{{ d.briefDescription }}</p>
          <div class="tags">
            <span v-for="t in d.tags.slice(0, 4)" :key="t" class="tag" :class="getTagClass(t)">
              {{ t }}
            </span>
          </div>
          <div class="meta">
            <span>截止 {{ d.deadline }}</span>
            <span>预算 {{ d.budget }}</span>
          </div>
        </article>
      </div>

      <div class="cards-pagination" v-if="followedDemands.length > pageSize">
        <el-pagination
          background
          size="small"
          layout="prev, pager, next"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="followedDemands.length"
          @current-change="handlePageChange"
        />
      </div>
    </section>

    <el-empty
      v-if="!selectedDemand && !loading && !followedDemands.length"
      description="还没有收藏的机会，去「找机会」页面和知途聊聊吧"
    />
    <div v-if="loading" class="loading">加载中...</div>

    <div v-else-if="selectedDemand" class="content">
      <div class="tabs-nav">
        <div
          v-for="n in navs"
          :key="n.key"
          class="nav-item"
          :class="{ active: activeTab === n.key }"
          @click="activeTab = n.key"
        >
          <div class="title2">{{ n.title }}</div>
          <div class="desc">{{ n.desc }}</div>
        </div>
      </div>

      <el-tabs v-model="activeTab" type="card" class="hidden-tabs-header">
        <!-- 需求介绍 -->
        <el-tab-pane label="机会简介" name="overview">
          <section class="card">
            <div class="card-hd">
              <div class="title2">机会简介</div>
            </div>
            <div class="grid">
              <div class="field">
                <div class="label">名称</div>
                <div class="value">{{ selectedDemand.title }}</div>
              </div>
              <div class="field">
                <div class="label">发布人</div>
                <div class="value">{{ selectedDemand.publisher }}</div>
              </div>
              <div class="field">
                <div class="label">发布企业</div>
                <div class="value">{{ selectedDemand.organizationName || '—' }}</div>
              </div>

              <div class="field">
                <div class="label">截止</div>
                <div class="value">{{ selectedDemand.deadline }}</div>
              </div>
              <div class="field">
                <div class="label">预算</div>
                <div class="value">{{ selectedDemand.budget }}</div>
              </div>
              <div class="field">
                <div class="label">标签</div>
                <div class="value">
                  <el-tag v-for="t in selectedDemand.tags" :key="t" size="small" effect="plain">
                    {{ t }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div class="desc-box">
              <div class="label">简介</div>
              <p class="desc">{{ selectedDemand.briefDescription }}</p>
            </div>
            <div class="desc-box">
              <div class="label">补充</div>
              <p class="desc">{{ selectedDemand.messageDescription }}</p>
            </div>
            <!-- 新增：企业提供的支持 -->
            <div class="desc-box" v-if="selectedDemand.supportProvided">
              <div class="label">企业提供的支持</div>
              <p class="desc">{{ selectedDemand.supportProvided }}</p>
            </div>
          </section>
        </el-tab-pane>

        <!-- 企业资源 -->
        <el-tab-pane label="了解更多" name="resources">
          <section class="card">
            <div class="card-hd">
              <div class="title2">了解更多</div>
              <div class="right">
                <el-button
                  type="primary"
                  plain
                  size="small"
                  @click="refreshDemandResources(selectedDemand)"
                >
                  刷新资源列表
                </el-button>
              </div>
            </div>
            <el-empty v-if="!(selectedDemand.resources || []).length" description="暂无资源" />
            <el-table v-else :data="selectedDemand.resources" border size="small">
              <el-table-column prop="name" label="名称" min-width="220">
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
              <el-table-column label="大小" width="100">
                <template #default="{ row }">
                  {{ formatFileSize(row.size) }}
                </template>
              </el-table-column>
              <el-table-column label="上传时间" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.created_at || row.uploadedAt) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button
                    size="small"
                    type="primary"
                    link
                    @click="openResource(row)"
                    :loading="row.downloading"
                  >
                    下载
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </section>
        </el-tab-pane>

        <!-- 项目组队 -->
        <el-tab-pane label="揭榜立项" name="teams">
          <section class="card">
            <div class="card-hd">
              <div class="title2">揭榜立项</div>
              <div class="right">
                <el-button type="primary" @click="openCreate">揭榜立项</el-button>
              </div>
            </div>

            <el-empty
              v-if="!(selectedDemand.teams || []).length"
              description="暂无队伍，来第一个揭榜立项吧！"
            />

            <!-- 替换项目组队表格列定义（只改这一段） -->
            <el-table
              v-else
              :data="selectedDemand.teams"
              border
              size="small"
              class="team-list-table"
            >
              <el-table-column prop="name" label="队伍" min-width="220">
                <template #default="{ row }">
                  <span>{{ row.name }}</span>
                  <el-tag
                    v-if="row.status"
                    size="small"
                    :type="mapStatusType(row.status)"
                    class="ml8"
                    effect="plain"
                  >
                    {{ row.status }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="createdAt" label="创建时间" width="180" />
              <el-table-column label="操作" width="200" fixed="right">
                <template #default="{ row }">
                  <el-button size="small" @click="openTeamDetail(row)">查看</el-button>
                  <el-button size="small" type="success" @click="handleTeamAction(row)">
                    {{ getTeamActionText(row) }}
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </section>
        </el-tab-pane>

        <!-- 结果发布 -->
        <el-tab-pane label="结果发布" name="results">
          <section class="card">
            <div class="card-hd">
              <div class="title2">结果发布</div>
              <div class="ops">
                <!-- 修改后的按钮：不再引用 evalLoading / computeRankingFromEvaluations -->
                <el-button :loading="rankingLoading" plain @click="handleGetRanking">
                  获取评分排名
                </el-button>
                <el-button v-if="isPublisher" type="primary" @click="openResultPublish">
                  {{ selectedDemand.result?.status === 'published' ? '更新排名' : '发布排名' }}
                </el-button>
              </div>
            </div>

            <!-- 如果企业已发布正式排名，优先显示 -->
            <template v-if="selectedDemand.result?.status === 'published'">
              <div class="result-meta">已发布结果：{{ selectedDemand.result.publishedAt }}</div>
              <el-table :data="selectedDemand.result.rankings || []" border size="small">
                <el-table-column prop="rank" label="名次" width="90" />
                <el-table-column prop="teamName" label="队伍" min-width="220" />
                <el-table-column prop="score" label="分数" width="120" />
                <el-table-column prop="award" label="奖项" width="140" />
                <el-table-column prop="remark" label="备注" min-width="220" />
              </el-table>
            </template>
            <!-- 否则显示本地获取的评分排名（若有） -->
            <template v-else>
              <el-table v-if="rankingList.length" :data="rankingList" border size="small">
                <el-table-column prop="rank" label="名次" width="90" />
                <el-table-column prop="projectName" label="队伍" min-width="220" />
                <el-table-column prop="totalScore" label="分数" width="120" />
                <el-table-column prop="remark" label="备注" min-width="220" />
              </el-table>
              <div
                v-else-if="rankingMessage && !rankingLoading"
                style="color: #909399; padding: 4px 0"
              >
                {{ rankingMessage }}
              </div>
              <div v-else-if="rankingLoading" style="color: #909399">加载中...</div>
            </template>
          </section>
        </el-tab-pane>

        <!-- 智能体问答 -->
        <el-tab-pane label="智能体问答" name="ai">
          <section class="card ai-wrap">
            <div class="card-hd">
              <div class="title2">智能体问答</div>
            </div>
            <div class="ai-iframe-container">
              <AgentChat agent="wenshi" :inputs="{ pid: selectedDemand.id }" :min-height="560" />
            </div>
          </section>
        </el-tab-pane>
      </el-tabs>
    </div>

    <!-- 立项对话框 -->
    <el-dialog
      v-model="createDialogVisible"
      title="揭榜立项（隶属于所选需求）"
      width="760px"
      :close-on-click-modal="false"
    >
      <!-- === 替换 BEGIN：立项对话框表单（仅项目名+项目描述） === -->
      <div class="create-form">
        <div class="row">
          <label class="label">项目名称</label>
          <el-input
            v-model="createForm.name"
            maxlength="80"
            show-word-limit
            placeholder="填写项目名称"
          />
        </div>
        <div class="row">
          <label class="label">项目描述</label>
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="6"
            maxlength="2000"
            show-word-limit
            placeholder="填写项目简介、目标或背景（可选）"
          />
        </div>
      </div>
      <!-- === 替换 END：立项对话框表单 === -->
      <template #footer>
        <el-button @click="createDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="doCreateProject">确 定</el-button>
      </template>
    </el-dialog>

    <!-- 队伍详情对话框 -->
    <el-dialog
      v-model="teamDetailVisible"
      :title="teamDetail ? '队伍详情 - ' + teamDetail.name : '队伍详情'"
      width="720px"
      :close-on-click-modal="false"
    >
      <div v-if="teamDetail" class="team-detail">
        <!-- 基础信息 -->
        <div class="block">
          <div class="label">基础信息</div>
          <div v-if="teamDetailLoading" style="color: #909399">加载中...</div>
          <div class="base-line" v-else>
            <span class="item"><b>项目名称：</b>{{ teamDetail.name || '—' }}</span>
            <span class="item"><b>创建人：</b>{{ teamDetailLeader?.realName || '—' }}</span>
            <span class="item"><b>创建时间：</b>{{ teamDetail.createdAt || '—' }}</span>
            <span class="item status">
              <b>状态：</b>
              <el-tag size="small" :type="mapStatusType(teamDetail.status)" effect="plain">
                {{ teamDetail.status || '—' }}
              </el-tag>
            </span>
          </div>
        </div>

        <!-- 项目介绍 -->
        <div class="block">
          <div class="label">项目介绍</div>
          <div v-if="teamDetailLoading" style="color: #909399">加载中...</div>
          <div v-else class="intro-text">
            <span v-if="teamDetailIntro">{{ teamDetailIntro }}</span>
            <span v-else style="color: #909399">暂无介绍</span>
          </div>
        </div>

        <!-- 队长信息（来自接口 leader 字段） -->
        <div class="block">
          <div class="label">队长信息</div>
          <div v-if="teamDetailLoading" style="color: #909399">加载中...</div>
          <template v-else>
            <div v-if="teamDetailLeader" class="leader-card">
              <el-avatar :src="teamDetailLeader.avatar" :size="48" />
              <div class="info">
                <div class="name-row">
                  <span class="name">{{ teamDetailLeader.realName || '—' }}</span>
                  <el-tag size="small" type="success" effect="plain">队长</el-tag>
                </div>
                <div class="contact-row">
                  <span class="label">专业：</span><span>{{ teamDetailLeader.major || '—' }}</span>
                </div>
                <div class="contact-row">
                  <span class="label">年级：</span><span>{{ teamDetailLeader.grade || '—' }}</span>
                </div>
                <div class="contact-row">
                  <span class="label">手机：</span><span>{{ teamDetailLeader.phone || '—' }}</span>
                </div>
                <div class="contact-row">
                  <span class="label">邮箱：</span><span>{{ teamDetailLeader.email || '—' }}</span>
                </div>
              </div>
            </div>
            <div v-else style="color: #909399">未获取到队长信息</div>
          </template>
        </div>
      </div>
      <template #footer>
        <el-button @click="teamDetailVisible = false">关 闭</el-button>
      </template>
    </el-dialog>

    <!-- 申请加入对话框（已改为自动预填：姓名/学校/年级/专业/电话/邮箱 + 申请理由） -->
    <el-dialog
      v-model="applyDialogVisible"
      title="申请加入"
      width="520px"
      :close-on-click-modal="false"
    >
      <div class="apply-form">
        <div class="row">
          <label class="label">姓名</label>
          <el-input v-model="applyForm.real_name" disabled />
        </div>
        <div class="row">
          <label class="label">学校</label>
          <el-input v-model="applyForm.school_name" disabled />
        </div>
        <div class="row">
          <label class="label">年级</label>
          <el-input v-model="applyForm.grade" disabled />
        </div>
        <div class="row">
          <label class="label">专业</label>
          <el-input v-model="applyForm.major" disabled />
        </div>
        <div class="row">
          <label class="label">电话</label>
          <el-input v-model="applyForm.phone" disabled />
        </div>
        <div class="row">
          <label class="label">邮箱</label>
          <el-input v-model="applyForm.email" disabled />
        </div>
        <div class="row">
          <label class="label">申请理由</label>
          <el-input
            v-model="applyForm.reason"
            type="textarea"
            :rows="4"
            maxlength="500"
            show-word-limit
            placeholder="请填写申请理由（必填，500字内）"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="applyDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitApply">提 交</el-button>
      </template>
    </el-dialog>

    <!-- 取消关注确认 -->
    <el-dialog
      v-model="unfollowConfirmVisible"
      :title="unfollowTarget ? '取消收藏 - ' + unfollowTarget.title : '取消收藏'"
      width="640px"
      :close-on-click-modal="false"
      class="unfollow-confirm-dialog"
    >
      <div v-if="unfollowTarget" class="confirm-body">
        <div class="hint">取消后，该机会将从「我的收藏」中移除。</div>
        <div class="grid">
          <div class="field">
            <div class="label">发布人</div>
            <div class="value">{{ unfollowTarget.publisher }}</div>
          </div>

          <div class="field">
            <div class="label">截止</div>
            <div class="value">{{ unfollowTarget.deadline }}</div>
          </div>
          <div class="field">
            <div class="label">预算</div>
            <div class="value">{{ unfollowTarget.budget }}</div>
          </div>
        </div>
        <div class="desc-box">
          <div class="label">简介</div>
          <p class="desc">{{ unfollowTarget.briefDescription }}</p>
        </div>
      </div>
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="unfollowConfirmVisible = false">再想想</el-button>
          <el-button type="danger" @click="confirmUnfollow">确认取消</el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 发布/更新排名 -->
    <el-dialog
      v-model="resultDialogVisible"
      title="发布/更新项目排名"
      width="820px"
      :close-on-click-modal="false"
    >
      <el-alert
        v-if="!amEnterpriseOwner"
        type="warning"
        :closable="false"
        show-icon
        description="当前账号非该需求发布者，仅演示效果。将无法在真实后端接口中生效。"
        class="mb12"
      />
      <el-table :data="resultFormRows" border size="small">
        <el-table-column label="名次" width="110">
          <template #default="{ row }">
            <el-input v-model="row.rank" placeholder="1,2,3…" />
          </template>
        </el-table-column>
        <el-table-column prop="teamName" label="队伍" min-width="220" />
        <el-table-column label="分数" width="140">
          <template #default="{ row }">
            <el-input v-model="row.score" placeholder="0-100" />
          </template>
        </el-table-column>
        <el-table-column label="奖项" width="180">
          <template #default="{ row }">
            <el-select v-model="row.award" placeholder="选择奖项" clearable>
              <el-option label="金奖" value="金奖" />
              <el-option label="银奖" value="银奖" />
              <el-option label="铜奖" value="铜奖" />
              <el-option label="优秀奖" value="优秀奖" />
              <el-option label="提名奖" value="提名奖" />
              <el-option label="— 无 —" value="" />
            </el-select>
          </template>
        </el-table-column>
        <el-table-column label="备注" min-width="220">
          <template #default="{ row }">
            <el-input v-model="row.remark" placeholder="可选" />
          </template>
        </el-table-column>
      </el-table>
      <template #footer>
        <el-button @click="resultDialogVisible = false">取 消</el-button>
        <el-button type="primary" @click="submitResultPublish">发 布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
/* 原样式保持不变 (略，与之前一致) */
.demand-following {
  padding: 16px;
}
.page-header {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
  .title {
    font-weight: 800;
    color: #165dff;
    font-size: 18px;
  }
  .sub {
    color: #6b7280;
    margin-top: 4px;
  }
}
.loading {
  text-align: center;
  color: #6b7280;
  padding: 40px 0;
}
.follow-cards .cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 12px;
  margin-bottom: 12px;
}
.cards-pagination {
  display: flex;
  justify-content: center;
  padding: 4px 0 2px;
}
.demand-card {
  background: #fff;
  border: 2px solid #eef2ff;
  border-radius: 14px;
  padding: 14px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 4px 12px rgba(22, 93, 255, 0.05);
  position: relative;
}
.demand-card:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 28px rgba(22, 93, 255, 0.12);
  border-color: #dbe7ff;
}
.demand-card.active {
  border-color: #165dff;
  box-shadow: 0 0 0 3px rgba(22, 93, 255, 0.15);
}
.demand-card .card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.demand-card .head-right {
  padding-right: 96px;
}
.demand-card .name {
  margin: 0;
  font-size: 16px;
  font-weight: 700;
}
.demand-card .badge {
  font-size: 12px;
  color: #165dff;
  background: #eef4ff;
  padding: 2px 8px;
  border-radius: 999px;
  margin-right: 8px;
}
.unfollow-btn {
  position: absolute;
  top: 12px;
  right: 14px;
  z-index: 3;
}
.demand-card .desc {
  color: #6b7280;
  margin: 8px 0 6px;
  min-height: 38px;
}
.demand-card .tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 6px;
}
.tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #f3f4f6;
  color: #374151;
}
.tag--ai {
  background: #f0f9ff;
  color: #0369a1;
}
.tag--fe {
  background: #f5f3ff;
  color: #6d28d9;
}
.demand-card .meta {
  display: flex;
  gap: 10px;
  color: #6b7280;
  font-size: 12px;
}
.tabs-nav {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 8px;
  margin: 8px 0 12px;
}
.nav-item {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 8px 10px;
  cursor: pointer;
  transition: all 0.2s ease;
}
.nav-item.active {
  border-color: #165dff;
  box-shadow: 0 0 0 2px rgba(22, 93, 255, 0.15);
}
.nav-item .title2 {
  font-weight: 700;
  font-size: 14px;
}
.nav-item .desc {
  color: #6b7280;
  font-size: 12px;
}
.card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  margin-bottom: 12px;
}
.card-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}
.title2 {
  font-weight: 700;
  font-size: 15px;
}
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 10px;
}
.field .label {
  color: #6b7280;
  font-size: 12px;
}
.field .value {
  font-weight: 600;
}
.desc-box .label {
  color: #6b7280;
  font-size: 12px;
  margin-top: 10px;
}
.desc-box .desc {
  margin: 6px 0 0;
  color: #374151;
}
.ai-iframe-container {
  width: 100%;
}
.ai-wrap .ai-box {
  display: grid;
  gap: 10px;
}
.ai-wrap .msgs {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 10px;
  max-height: 300px;
  overflow: auto;
}
.msg {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
}
.msg .prefix {
  font-weight: 700;
}
.msg--ai .prefix {
  color: #165dff;
}
.msg--me .prefix {
  color: #059669;
}
.input-bar {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 8px;
}
.ai-hint {
  color: #6b7280;
  font-size: 12px;
}
.result-meta {
  color: #6b7280;
  font-size: 12px;
  margin-bottom: 8px;
}
.create-form .row,
.apply-form .row {
  display: grid;
  gap: 6px;
  margin-bottom: 10px;
}
.create-form .label,
.apply-form .label {
  font-size: 12px;
  color: #6b7280;
}
.members-grid .member-row {
  display: flex;
  gap: 8px;
}
.team-detail .block {
  margin-bottom: 10px;
}
.team-detail .label {
  font-weight: 700;
  margin-bottom: 6px;
}
.hidden-tabs-header :deep(.el-tabs__header) {
  display: none;
}
@media (max-width: 480px) {
  .demand-card .head-right {
    padding-right: 88px;
  }
}
.mb12 {
  margin-bottom: 12px;
}
.no-score-names {
  list-style: none;
  padding-left: 0;
  margin: 4px 0 0;
}
.no-score-names > li {
  line-height: 28px;
  color: #374151;
  border-bottom: 1px dashed #e5e7eb;
}

/* === 新增：队伍详情基础信息单行 & 项目表格行距 / 状态标签样式 BEGIN === */
.base-line {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 28px;
  font-size: 13px;
  line-height: 1.4;
  padding: 4px 2px 2px;
  .item {
    white-space: nowrap;
    display: flex;
    align-items: center;
  }
  .item.status {
    display: flex;
    align-items: center;
    gap: 4px;
  }
}
.ml8 {
  margin-left: 8px;
}

.team-list-table :deep(.el-table__row) {
  height: 48px; /* 增大行高 */
}
.team-list-table :deep(.el-table__cell) {
  padding-top: 12px;
  padding-bottom: 12px;
  font-size: 13px;
}
/* 保持 leader-card 原有样式可复用，无需重写，如需更贴近设计可在此微调 */
/* === 新增：队伍详情基础信息单行 & 项目表格行距 / 状态标签样式 END === */

/* === 新增 BEGIN：申请弹窗样式（可选） === */
:deep(.el-dialog__body) .el-form-item {
  margin-bottom: 18px;
}
:deep(.el-dialog__header) {
  font-weight: 600;
}
/* === 新增 END === */

/* === 新增：申请弹窗禁用输入外观优化 BEGIN === */
.apply-form :deep(.el-input.is-disabled .el-input__wrapper),
.apply-form :deep(.el-textarea.is-disabled .el-textarea__inner) {
  background: #f5f7fa !important;
  color: #555 !important;
  -webkit-text-fill-color: #555 !important;
  cursor: not-allowed;
}
/* === 新增：申请弹窗禁用输入外观优化 END === */
</style>
