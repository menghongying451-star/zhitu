<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getProjectList, getProjectParticipants } from '@/api/student/project'

const router = useRouter()

const DEFAULT_AVATAR =
  'data:image/svg+xml;utf8,' +
  encodeURIComponent(
    `<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40">
      <rect width="100%" height="100%" rx="20" fill="#EEF2FF"/>
      <circle cx="20" cy="16" r="8" fill="#93C5FD"/>
      <rect x="8" y="26" width="24" height="10" rx="5" fill="#BFDBFE"/>
    </svg>`
  )

// 当前用户 id / username 候选解析（包含 user.id / student.id 等）
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
    } catch (e) {
      /* intentionally ignored: fallback null */
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
// 供多字段对照使用的我的 id 候选列表
const myUserId = ref(resolveCurrentUserId())
const myUsername = ref(resolveCurrentUsername())
const myIdCandidates = ref(
  (() => {
    const ids = new Set()
    if (myUserId.value != null) ids.add(Number(myUserId.value))
    // 从 localStorage 再补充一遍可能的 studentId
    const ls = typeof localStorage !== 'undefined' ? localStorage : null
    if (ls) {
      const keys = ['studentId', 'student_id']
      keys.forEach((k) => {
        const raw = ls.getItem(k)
        const n = Number(raw)
        if (!Number.isNaN(n)) ids.add(n)
      })
      const rawUser =
        ls.getItem('currentUser') || ls.getItem('user') || ls.getItem('profile') || ls.getItem('me')
      const obj = rawUser
        ? (() => {
            try {
              return JSON.parse(rawUser)
            } catch {
              return null
            }
          })()
        : null
      const more = [obj?.student?.id, obj?.data?.student?.id, obj?.user?.id, obj?.data?.user?.id]
      more.forEach((v) => {
        const n = Number(v)
        if (!Number.isNaN(n)) ids.add(n)
      })
    }
    return Array.from(ids)
  })()
)

const loading = ref(false)
const myProjects = ref([])

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
    return isNaN(d.getTime()) ? String(s) : d.toLocaleDateString()
  } catch {
    return String(s)
  }
}

const APPROVED_SET = new Set(['approved', 'accepted', 'joined', 'active'])
const normalizeRole = (r) => (r === 'leader' ? '组长' : r === 'member' ? '成员' : r || '')
const isMeByParticipant = (p) => {
  const cand = myIdCandidates.value
  const sid = p?.student?.id
  const uid1 = p?.user_id
  const uid2 = p?.student?.user_id
  const allIds = [sid, uid1, uid2]
    .map((x) => (x == null ? null : Number(x)))
    .filter((x) => !Number.isNaN(x))
  if (allIds.some((x) => cand.includes(x))) return true
  const u = (myUsername.value || '').trim().toLowerCase()
  const pn = String(p?.student?.username || p?.name || '')
    .trim()
    .toLowerCase()
  return !!u && !!pn && u === pn
}
const mapMemberFromParticipants = (m) => {
  const isMe = isMeByParticipant(m)
  return {
    id: m?.id ?? `${m?.student?.id ?? 'x'}`,
    userId: m?.student?.id ?? m?.student?.user_id ?? m?.user_id ?? null,
    name: m?.student?.real_name || m?.student?.username || m?.name || '成员',
    avatar: m?.student?.avatar || DEFAULT_AVATAR,
    role: normalizeRole(m?.role),
    isMe
  }
}

// 统一 leader 候选收集
const getLeaderIds = (proj) => {
  const ld = proj?.leader || {}
  const ids = []
  if (ld?.id != null) ids.push(Number(ld.id))
  if (ld?.user?.id != null) ids.push(Number(ld.user.id))
  if (ld?.student?.id != null) ids.push(Number(ld.student.id))
  if (ld?.user_id != null) ids.push(Number(ld.user_id))
  if (ld?.student_id != null) ids.push(Number(ld.student_id))
  if (ld?.account_id != null) ids.push(Number(ld.account_id))
  return ids.filter((n) => !Number.isNaN(n))
}
const getLeaderUsernames = (proj) => {
  const ld = proj?.leader || {}
  const arr = []
  if (ld?.username) arr.push(String(ld.username))
  if (ld?.user?.username) arr.push(String(ld.user.username))
  return arr.map((s) => s.trim().toLowerCase()).filter(Boolean)
}

const mapProjectForView = (p, members = [], extra = {}) => ({
  id: p.id,
  name: p.title || p.name || '未命名项目',
  demandId: p.requirement?.id,
  demandTitle: p.requirement?.title || '未指定需求',
  affiliation: p.affiliation || p.requirement?.organization_name || p.requirement?.title || '',
  shortDescription:
    p.brief || p.brief_description || (p.description ? String(p.description).slice(0, 120) : ''),
  status: mapStatus(p.status),
  publisher: p.leader?.real_name || p.leader?.username || p.publisher || '—',
  joinDate: formatDate(p.joined_at || p.created_at),
  deliverablesCount:
    typeof p.deliverable_count === 'number'
      ? p.deliverable_count
      : Array.isArray(p.deliverables)
        ? p.deliverables.length
        : 0,
  members,
  tags: p.tags || [],
  myRole: extra.myRole || '',
  meIndex: typeof extra.meIndex === 'number' ? extra.meIndex : -1
})

// “我的项目” = 我负责 + 我加入 的并集
const loadMyProjects = async () => {
  loading.value = true
  try {
    const [respLeader, respJoined] = await Promise.all([
      getProjectList({ my_projects: true, page: 1, page_size: 200 }),
      getProjectList({ my_projects: false, page: 1, page_size: 200 })
    ])
    const list1 = respLeader?.data?.data?.projects || respLeader?.data?.projects || []
    const list2 = respJoined?.data?.data?.projects || respJoined?.data?.projects || []
    const byId = new Map()
    ;[...list1, ...list2].forEach((p) => byId.set(p.id, p))
    const baseList = Array.from(byId.values())
    if (!baseList.length) {
      myProjects.value = []
      return
    }

    const limit = 4
    const results = new Array(baseList.length)
    let cursor = 0
    await Promise.all(
      Array.from({ length: Math.min(limit, baseList.length) }).map(async () => {
        while (true) {
          const idx = cursor++
          if (idx >= baseList.length) break
          const proj = baseList[idx]
          try {
            const r = await getProjectParticipants(proj.id)
            const participants = r?.data?.data?.participants || []
            const members = participants.map(mapMemberFromParticipants)

            const leaderIds = getLeaderIds(proj)
            const leaderNames = getLeaderUsernames(proj)
            const meIdx = members.findIndex((m) => m.isMe)

            const iAmLeader =
              leaderIds.some((n) => myIdCandidates.value.includes(Number(n))) ||
              (leaderNames.length > 0 &&
                leaderNames.includes((myUsername.value || '').trim().toLowerCase()))

            const iAmMember =
              meIdx >= 0
                ? true
                : participants.some((m) => {
                    const st = String(m?.status || m?.status_text || '').toLowerCase()
                    return isMeByParticipant(m) && (APPROVED_SET.has(st) || !st)
                  })

            const myRole = iAmLeader
              ? '组长'
              : meIdx >= 0
                ? members[meIdx].role || '成员'
                : iAmMember
                  ? '成员'
                  : ''

            results[idx] = mapProjectForView(proj, members, { myRole, meIndex: meIdx })
          } catch (e) {
            const iAmLeader =
              getLeaderIds(proj).some((n) => myIdCandidates.value.includes(Number(n))) ||
              getLeaderUsernames(proj).includes((myUsername.value || '').trim().toLowerCase())
            results[idx] = mapProjectForView(proj, [], { myRole: iAmLeader ? '组长' : '' })
          }
        }
      })
    )

    myProjects.value = results.filter(Boolean).sort((a, b) => {
      const at = a.joinDate ? new Date(a.joinDate).getTime() : 0
      const bt = b.joinDate ? new Date(b.joinDate).getTime() : 0
      return bt - at
    })

    console.debug('[MyProjects] uid, uname loaded. Count:', {
      uid: myUserId.value,
      uname: myUsername.value,
      count: myProjects.value.length
    })
  } catch (e) {
    console.error('加载“我的项目”失败:', e)
    ElMessage.error('加载“我的项目”失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

onMounted(loadMyProjects)

const goDetail = (p) => {
  router.push(`/student/my-projects/${p.id}`)
}
</script>

<template>
  <!-- 模板保持你当前的结构与样式 -->
  <div class="my-projects-list">
    <div class="head">
      <div class="title">我的项目</div>
      <div class="sub">仅展示与你有关的项目（创建/负责/加入）。</div>
    </div>

    <div v-if="!loading && myProjects.length === 0" class="empty">
      <el-empty description="暂无项目" />
    </div>
    <div v-else-if="loading" class="empty">
      <el-empty description="正在加载…" />
    </div>

    <div class="list" v-else>
      <el-card
        v-for="p in myProjects"
        :key="p.id"
        class="proj-item"
        shadow="hover"
        @click="goDetail(p)"
      >
        <div class="row1">
          <div class="name">{{ p.name }}</div>
          <div class="right">
            <el-tag
              :type="p.status === '进行中' ? 'success' : p.status === '招募中' ? 'warning' : 'info'"
              size="small"
            >
              {{ p.status }}
            </el-tag>
            <el-button class="submit-btn" size="default" @click.stop="goDetail(p)"
              >进入项目</el-button
            >
          </div>
        </div>
        <div class="row2">
          <div class="desc">{{ p.shortDescription }}</div>
        </div>
        <div class="row3">
          <div class="meta-left">
            <span class="aff"
              >隶属需求：<b>{{ p.demandTitle }}</b></span
            >
            <span class="sep"></span>
            <span>隶属主体：{{ p.affiliation || '—' }}</span>
            <span class="sep"></span>
            <span
              >阶段成果：<b>{{ p.deliverablesCount }}</b></span
            >
            <span class="sep"></span>
            <span v-if="p.myRole"
              >我的角色：<b>{{ p.myRole }}</b></span
            >
            <!-- <span v-if="p.meIndex >= 0" class="me-pos">我的位置：#{{ p.meIndex + 1 }}</span> -->
          </div>
          <div class="members">
            <div class="avatars">
              <el-avatar
                v-for="(m, idx) in p.members.slice(0, 6)"
                :key="m.id"
                :src="m.avatar"
                :size="26"
                class="avatar"
                :class="{ me: m.isMe }"
                :style="{ zIndex: p.members.length - idx }"
              />
              <div v-if="p.members.length > 6" class="more">+{{ p.members.length - 6 }}</div>
            </div>
            <span class="hint">成员仅对成员可见</span>
          </div>
        </div>
        <div class="row4">
          <div class="tags">
            <el-tag v-for="t in (p.tags || []).slice(0, 3)" :key="t" size="small" effect="plain">{{
              t
            }}</el-tag>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped lang="scss">
.my-projects-list {
  padding: 16px;
  .head {
    .title {
      font-size: 20px;
      font-weight: 800;
      color: #165dff;
    }
    .sub {
      color: #86909c;
      margin-top: 4px;
    }
  }
  .list {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
    margin-top: 12px;
    .proj-item {
      cursor: pointer;
      .row1 {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 6px;
        gap: 10px;
        .name {
          font-weight: 700;
          color: #1d2129;
          font-size: 16px;
        }
        .right {
          display: inline-flex;
          align-items: center;
          gap: 8px;
        }
      }
      .row2 {
        color: #4e5969;
        margin-bottom: 8px;
      }
      .row3 {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        .meta-left {
          display: flex;
          gap: 8px;
          flex-wrap: wrap;
          color: #86909c;
          .aff b {
            color: #1f2937;
          }
          .sep {
            width: 1px;
            height: 12px;
            background: #e5e6eb;
            display: inline-block;
          }
          .me-pos {
            color: #4e5969;
          }
        }
        .members {
          display: flex;
          align-items: center;
          gap: 10px;
          .avatars {
            display: inline-flex;
            align-items: center;
            .avatar {
              border: 2px solid #fff;
              box-shadow: 0 0 0 1px #e5e6eb;
              position: relative;
            }
            .avatar + .avatar {
              margin-left: -8px;
            }
            .avatar.me {
              box-shadow: 0 0 0 2px #165dff;
            }
            .avatar.me::after {
              content: '我';
              position: absolute;
              right: -4px;
              bottom: -4px;
              background: #165dff;
              color: #fff;
              font-size: 10px;
              line-height: 1;
              padding: 2px 4px;
              border-radius: 6px;
              box-shadow: 0 2px 6px rgba(22, 93, 255, 0.3);
            }
            .more {
              width: 26px;
              height: 26px;
              margin-left: -8px;
              border-radius: 50%;
              background: #f2f3f5;
              color: #4e5969;
              display: inline-flex;
              align-items: center;
              justify-content: center;
              font-size: 12px;
              box-shadow: 0 0 0 1px #e5e6eb;
            }
          }
          .hint {
            color: #86909c;
            font-size: 12px;
          }
        }
      }
      .row4 {
        margin-top: 6px;
        .tags {
          display: flex;
          gap: 6px;
          flex-wrap: wrap;
        }
      }
    }
  }
}

/* 进入项目按钮（醒目） */
.submit-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  border: none;
  color: #fff;
  border-radius: 10px;
  background: linear-gradient(135deg, #165dff, #6366f1);
  box-shadow: 0 6px 18px rgba(22, 93, 255, 0.25);
  padding: 8px 12px;
  transition:
    transform 0.12s ease,
    box-shadow 0.2s ease,
    filter 0.2s ease;
  &:hover {
    transform: translateY(-1px);
    box-shadow: 0 12px 26px rgba(22, 93, 255, 0.32);
    filter: saturate(1.05);
  }
  &:focus-visible {
    outline: 2px solid #93c5fd;
    outline-offset: 2px;
  }
}
</style>
