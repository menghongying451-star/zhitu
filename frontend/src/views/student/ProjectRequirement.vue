<template>
  <div class="page">
    <section class="agent-container">
      <AgentChat agent="zhitu" :min-height="600" @action="onAgentAction" />
    </section>

    <h2 class="page-title">机会总览</h2>

    <!-- 筛选栏：关键词（前端过滤）+ 标签 + 创建时间 + 操作 -->
    <div class="filters">
      <div class="filters-row">
        <!-- 关键词搜索：纯前端过滤当前列表 -->
        <div class="field-inline field-grow">
          <label class="label">关键词</label>
          <div class="keyword-wrap">
            <input
              v-model.trim="keyword"
              type="text"
              class="input"
              placeholder="搜索机会标题、发布方、简介或标签"
            />
            <button v-if="keyword" class="keyword-clear" type="button" @click="keyword = ''">
              清除
            </button>
          </div>
        </div>
      </div>

      <div class="filters-row">
        <!-- 统一标签输入 -->
        <div class="field-inline field-grow">
          <label class="label">标签 (兴趣 / 能力)</label>
          <div class="ac-wrap">
            <input
              v-model.trim="tagQuery"
              type="text"
              class="input"
              placeholder="输入关键词搜索标签"
              @input="onTagInput"
              @focus="onTagFocus"
              @blur="onTagBlur"
              @keydown="onKeydown"
            />
            <ul v-if="showSuggest && tagSuggest.length" class="ac-list">
              <li
                v-for="(s, idx) in tagSuggest"
                :key="'tg-' + (s.id ?? s.label ?? idx)"
                :class="['ac-item', { 'ac-active': idx === acIndex }]"
                @mousedown.prevent="addTag(s)"
              >
                {{ s.label }}
                <small v-if="s.__kind" style="color: #6b7280; font-size: 11px; margin-left: 6px">{{
                  s.__kind
                }}</small>
              </li>
            </ul>
          </div>
          <div class="chips">
            <span class="chip" v-for="t in selectedTags" :key="'sel-' + t.id">
              {{ t.label }} <i class="chip-x" @click="removeTag(t)">×</i>
            </span>
          </div>
        </div>

        <!-- 创建时间 -->
        <div class="field-inline filter-time">
          <label class="label">创建时间</label>
          <div class="date-range" @click="openStartPicker">
            <div class="date-field" @click.stop="openStartPicker">
              <input
                ref="startDateRef"
                v-model="filters.time_start"
                type="date"
                class="input-date"
                :class="{ 'has-value': !!filters.time_start }"
                @focus="ensurePicker('start')"
              />
              <span class="date-placeholder" v-if="!filters.time_start">开始日期</span>
            </div>
            <span class="sep">—</span>
            <div class="date-field" @click.stop="openEndPicker">
              <input
                ref="endDateRef"
                v-model="filters.time_end"
                type="date"
                class="input-date"
                :class="{ 'has-value': !!filters.time_end }"
                @focus="ensurePicker('end')"
              />
              <span class="date-placeholder" v-if="!filters.time_end">结束日期</span>
            </div>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="filters-actions">
          <div class="label-spacer" aria-hidden="true"></div>
          <div class="actions-row">
            <button class="btn btn-primary" @click="onSearch">筛选</button>
            <button class="btn btn-secondary" @click="onReset">重置</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 列表 -->
    <section class="list" v-if="!loading && displayList.length">
      <article v-for="item in displayList" :key="item.id" class="card" @click="openDetail(item)">
        <div class="card-title">
          <span class="title">{{ item.title }}</span>
          <span class="status" :class="`status--${item.status}`">
            {{ statusText(item.status) }}
          </span>
        </div>
        <div class="meta">
          <img v-if="item.organization?.logo" :src="item.organization.logo" alt="" class="logo" />
          <span class="company">
            {{ item.organization?.name || item.company?.name || '未知企业' }}
          </span>
          <span class="sep">·</span>
          <span class="time">创建：{{ formatTime(item.created_at || item.create_time) }}</span>
          <span class="sep">·</span>
          <span class="view">浏览：{{ item.views ?? item.view_count ?? 0 }}</span>
        </div>
        <div class="deadline" :class="{ 'deadline--tbd': !hasDeadline(item) }">
          <span class="deadline-label">截止</span>
          <span class="deadline-value">
            {{ hasDeadline(item) ? formatTime(item.finish_time) : '以官网为准' }}
          </span>
        </div>
        <div class="tags">
          <span v-for="t in item.tag1Unified" :key="`t1-${t.name}`" class="tag">{{ t.name }}</span>
          <span v-for="t in item.tag2Unified" :key="`t2-${t.name}`" class="tag tag--sub">
            {{ t.name }}
          </span>
        </div>
        <p class="summary" v-if="item.brief || item.summary">
          {{ item.brief || item.summary }}
        </p>
      </article>
    </section>

    <section v-if="!loading && !displayList.length" class="empty">
      {{ list.length ? '没有匹配关键词的机会，换个词试试' : '暂无数据' }}
    </section>
    <section v-if="loading" class="loading">加载中...</section>

    <!-- 分页 -->
    <footer class="pagination" v-if="pagination.total > 0">
      <div class="pager">
        <button class="btn" :disabled="pagination.page === 1" @click="toPrev">上一页</button>
        <span class="page-info">
          第 {{ pagination.page }} / {{ totalPages }} 页（共 {{ pagination.total }} 条）
        </span>
        <button class="btn" :disabled="pagination.page >= totalPages" @click="toNext">
          下一页
        </button>
      </div>
      <div class="page-size">
        <label>每页</label>
        <select v-model.number="pagination.page_size" class="select" @change="onPageSizeChange">
          <option :value="10">10</option>
          <option :value="20">20</option>
          <option :value="50">50</option>
        </select>
      </div>
    </footer>

    <!-- 详情抽屉 -->
    <div v-if="detailVisible" class="drawer-mask" @click.self="detailVisible = false">
      <div class="drawer">
        <header class="drawer-header">
          <div class="drawer-title">
            <img
              v-if="detail?.organization?.logo"
              :src="detail.organization.logo"
              class="org-logo"
              alt="logo"
            />
            <div class="title-wrap">
              <h3 class="drawer-h3">
                {{ detail?.title }}
                <span v-if="detail?.id" class="id-chip">#{{ detail.id }}</span>
              </h3>
              <div class="subtitle">
                <strong>
                  {{ detail?.organization?.name || detail?.company?.name || '未知企业' }}
                </strong>
                <span class="sep">·</span>
                <span class="status-badge" :class="`status--${detail?.status}`">
                  {{ statusText(detail?.status) }}
                </span>
              </div>
            </div>
          </div>
          <button class="btn btn-secondary drawer-cancel-btn" @click="detailVisible = false">
            关闭
          </button>
        </header>

        <div class="drawer-body" v-if="detail">
          <section class="info-grid">
            <div class="info-item">
              <span class="info-label">发布人</span>
              <span class="info-value">{{ detail.publish_people || '-' }}</span>
            </div>
            <div class="info-item" v-if="hasBudget">
              <span class="info-label">预算</span>
              <span class="info-value">{{ detail.budget }}万</span>
            </div>
            <div class="info-item">
              <span class="info-label">招募人数</span>
              <span class="info-value">{{ detail.people_count || '-' }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">创建时间</span>
              <span class="info-value">{{ formatTime(detail.created_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">更新时间</span>
              <span class="info-value">{{ formatTime(detail.updated_at) }}</span>
            </div>
            <div class="info-item">
              <span class="info-label">计划完成</span>
              <span class="info-value">{{ detail.finish_time || '-' }}</span>
            </div>
          </section>

          <div class="drawer-tags">
            <span class="group-label">兴趣标签</span>
            <span v-for="t in detail.tag1Unified" :key="`dt1-${t.name}`" class="tag">
              {{ t.name }}
            </span>
          </div>
          <div class="drawer-tags">
            <span class="group-label">能力/岗位</span>
            <span v-for="t in detail.tag2Unified" :key="`dt2-${t.name}`" class="tag tag--sub">
              {{ t.name }}
            </span>
          </div>

          <article class="drawer-desc" v-if="detail.description">
            {{ detail.description }}
          </article>

          <div v-if="detail.resources?.length" class="drawer-res">
            <h4>相关资源</h4>
            <ul>
              <li v-for="r in detail.resources" :key="r.id || r.url || r.name">
                <a :href="r.url || r" target="_blank" rel="noopener">{{ r.name || r }}</a>
              </li>
            </ul>
          </div>
          <div v-if="detail.files?.length" class="drawer-res">
            <h4>相关文件</h4>
            <ul>
              <li v-for="f in detail.files" :key="f.id || f.url || f.name">
                <a :href="f.url || f" target="_blank" rel="noopener">{{ f.name || f }}</a>
              </li>
            </ul>
          </div>

          <div class="drawer-actions">
            <button class="btn btn-primary drawer-join-btn" @click="joinRequirement">
              {{ isJoined(detail.id) ? '已收藏' : '收藏' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getRequirementList, getRequirementDetail } from '@/api/student/requirement'
import { searchTags } from '@/api/student/tags'
import AgentChat from '@/components/AgentChat.vue'
import { followDemand } from '@/api'

/* ====== 列表与分页 ====== */
const router = useRouter()
const loading = ref(false)
const list = ref([])
const followStatusMap = reactive({})

const pagination = reactive({
  page: 1,
  page_size: 10,
  total: 0
})

const filters = reactive({
  time_start: '',
  time_end: ''
})

/* ====== 关键词搜索 + 截止时间排序（都在前端做） ====== */
const keyword = ref('')

// 取截止时间戳；字段缺失/非法返回 null
function deadlineValue(item) {
  const raw = item?.finish_time ?? item?.deadline ?? item?.finishTime
  if (!raw) return null
  const t = new Date(raw).getTime()
  return Number.isNaN(t) ? null : t
}

function hasDeadline(item) {
  return deadlineValue(item) !== null
}

// 关键词命中：标题 / 发布方 / 简介 / 标签
const keywordMatchedList = computed(() => {
  const kw = keyword.value.trim().toLowerCase()
  if (!kw) return list.value
  return list.value.filter((it) => {
    const hay = [
      it.title,
      it.organization?.name,
      it.company?.name,
      it.brief,
      it.summary,
      it.description,
      ...(it.tag1Unified || []).map((t) => t.name),
      ...(it.tag2Unified || []).map((t) => t.name)
    ]
      .filter(Boolean)
      .join(' ')
      .toLowerCase()
    return hay.includes(kw)
  })
})

// 快截止的排前面；没有截止时间的排最后
const displayList = computed(() => {
  const arr = [...keywordMatchedList.value]
  arr.sort((a, b) => {
    const ta = deadlineValue(a)
    const tb = deadlineValue(b)
    if (ta === null && tb === null) return (b.id || 0) - (a.id || 0)
    if (ta === null) return 1
    if (tb === null) return -1
    if (ta === tb) return (b.id || 0) - (a.id || 0)
    return ta - tb
  })
  return arr
})

const totalPages = computed(() =>
  pagination.page_size ? Math.max(1, Math.ceil(pagination.total / pagination.page_size)) : 1
)

function statusText(s) {
  const map = {
    under_review: '审核中',
    in_progress: '进行中',
    completed: '已完成',
    paused: '已暂停',
    review_failed: '审核未通过'
  }
  return map[s] || s || '未知状态'
}

function formatTime(iso) {
  if (!iso) return '-'
  const d = new Date(iso)
  if (isNaN(d.getTime())) return iso
  return [
    d.getFullYear(),
    String(d.getMonth() + 1).padStart(2, '0'),
    String(d.getDate()).padStart(2, '0')
  ].join('-')
}

// [追加] 批量查询关注状态并填充 followStatusMap
// 用列表里的 is_favorited 字段填充本地状态映射
function populateFavoriteStatusFromList(items = []) {
  ;(items || []).forEach((it) => {
    if (it && it.id != null) {
      // it.is_favorited 由后端提供
      followStatusMap[it.id] = !!it.is_favorited
    }
  })
}

function unifyTagArray(arr) {
  if (!Array.isArray(arr)) return []
  return arr
    .map((t) => {
      if (!t) return null
      if (typeof t === 'string') return { name: t }
      if (typeof t === 'object') {
        const name = t.name ?? t.value ?? t.label
        return name ? { id: t.id, name } : null
      }
      return null
    })
    .filter(Boolean)
}

function unifyResArray(arr) {
  if (!Array.isArray(arr)) return []
  return arr
    .map((x) => {
      if (!x) return null
      if (typeof x === 'string') return { name: x, url: x }
      if (typeof x === 'object') {
        const name = x.name ?? x.title ?? x.filename ?? x.file_name ?? x.url ?? ''
        const url = x.url ?? x.link ?? x.href ?? ''
        const id = x.id ?? x.file_id
        return { id, name, url }
      }
      return null
    })
    .filter(Boolean)
}

function toNumber(val, dft = 0) {
  const n = Number(val)
  return Number.isFinite(n) ? n : dft
}

function normalizeListItem(raw) {
  const item = { ...raw }
  item.views = toNumber(raw.views ?? raw.view_count ?? 0, 0)
  item.tag1Unified = unifyTagArray(raw.tag1)
  item.tag2Unified = unifyTagArray(raw.tag2)
  item.is_favorited = !!raw.is_favorited
  return item
}

function normalizeDetailPayload(raw) {
  const d = { ...raw }
  d.views = toNumber(raw.views ?? raw.view_count ?? 0, 0)
  d.tag1Unified = unifyTagArray(raw.tag1)
  d.tag2Unified = unifyTagArray(raw.tag2)
  d.resources = unifyResArray(raw.resources)
  d.files = unifyResArray(raw.files)
  return d
}

/* ====== 统一标签选择 ====== */
const tagQuery = ref('')
const tagSuggest = ref([])
const selectedTags = ref([])
const showSuggest = ref(false)
const acIndex = ref(-1)
let tagTimer = null

function unifyTag1Suggest(arr) {
  if (!Array.isArray(arr)) return []
  return arr
    .map((x, i) => {
      if (!x) return null
      if (typeof x === 'string') return { id: x, label: x, value: x, __kind: '兴趣' }
      if (typeof x === 'object') {
        const slug = `${x.category || ''}-${x.subcategory || ''}-${x.specialty || ''}`.replace(
          /^-+|-+$/g,
          ''
        )
        const id = x.id ?? x.value ?? x.name ?? x.key ?? x.code ?? (slug || i)
        const label =
          x.value ??
          x.name ??
          x.label ??
          x.post ??
          [x.category, x.subcategory, x.specialty].filter(Boolean).join('-')
        return label ? { id, label, value: label, __kind: '兴趣', ...x } : null
      }
      return null
    })
    .filter(Boolean)
}

/*
function unifyTag2Suggest(arr) {
  if (!Array.isArray(arr)) return []
  return arr
    .map((x, i) => {
      if (!x) return null
      if (typeof x === 'string') return { id: x, label: x, __kind: '能力' }
      if (typeof x === 'object') {
        const label =
          x.post ||
          [x.category, x.subcategory, x.specialty].filter(Boolean).join('-') ||
          x.name ||
          x.value ||
          x.label
        const id = x.id ?? (label || i)
        return label ? { id, label, __kind: '能力', ...x } : null
      }
      return null
    })
    .filter(Boolean)
}
*/

function onTagInput() {
  showSuggest.value = true
  acIndex.value = -1
  if (tagTimer) clearTimeout(tagTimer)
  tagTimer = setTimeout(fetchSuggest, 300)
}

function onTagFocus() {
  showSuggest.value = true
  if (tagQuery.value) {
    if (tagTimer) clearTimeout(tagTimer)
    tagTimer = setTimeout(fetchSuggest, 0)
  }
}

function onTagBlur() {
  setTimeout(() => {
    showSuggest.value = false
    acIndex.value = -1
  }, 120)
}

function onKeydown(event) {
  if (event.key === 'Enter') {
    const query = tagQuery.value
    if (query.trim()) {
      const exists = selectedTags.value.find((t) => t.label === query.trim())
      if (!exists) {
        addTag({ id: query.trim(), label: query.trim() })
      } else {
        tagQuery.value = ''
      }
    }
  } else if (event.key === 'ArrowDown') {
    if (tagSuggest.value.length) {
      acIndex.value = (acIndex.value + 1 + tagSuggest.value.length) % tagSuggest.value.length
      event.preventDefault()
    }
  } else if (event.key === 'ArrowUp') {
    if (tagSuggest.value.length) {
      acIndex.value = (acIndex.value - 1 + tagSuggest.value.length) % tagSuggest.value.length
      event.preventDefault()
    }
  } else if (event.key === 'Tab') {
    if (acIndex.value >= 0 && tagSuggest.value[acIndex.value]) {
      addTag(tagSuggest.value[acIndex.value])
      event.preventDefault()
    }
  }
}

async function fetchSuggest() {
  const q = tagQuery.value
  if (!q) {
    tagSuggest.value = []
    acIndex.value = -1
    return
  }
  try {
    const { data } = await searchTags(q)
    const payload = (data && (data.data ?? data)) || {}
    const t1 = unifyTag1Suggest(Array.isArray(payload.tag1) ? payload.tag1 : [])
    // 忽略 tag2
    tagSuggest.value = t1
    acIndex.value = tagSuggest.value.length ? 0 : -1
  } catch (e) {
    console.error(e)
    tagSuggest.value = []
    acIndex.value = -1
  }
}

function addTag(s) {
  // 防御：忽略能力/岗位标签
  if (s.__kind && s.__kind !== '兴趣') return
  if (!selectedTags.value.find((x) => x.id === s.id)) {
    selectedTags.value.push({ id: s.id, label: s.label, __kind: '兴趣' })
  }
  tagQuery.value = ''
  tagSuggest.value = []
  showSuggest.value = false
  acIndex.value = -1
  onSearch()
}

function removeTag(t) {
  selectedTags.value = selectedTags.value.filter((x) => x.id !== t.id)
  onSearch()
}

watch(
  () => tagSuggest.value.length,
  () => {
    acIndex.value = tagSuggest.value.length ? 0 : -1
  }
)

function collectIds(kind) {
  // kind: '兴趣' 或 '能力'
  return selectedTags.value
    .filter((t) => t.__kind === kind && t.id !== undefined && /^\d+$/.test(String(t.id)))
    .map((t) => String(t.id))
}

/* ====== 查询 & 数据加载 ====== */
function buildParams() {
  let start = filters.time_start || ''
  let end = filters.time_end || ''
  if (start && end && end < start) {
    const t = start
    start = end
    end = t
  }

  // 关键词：仅兴趣标签
  const kwSet = new Set()
  selectedTags.value.forEach((t) => {
    if (t?.label) kwSet.add(t.label.trim())
  })
  const keyword = Array.from(kwSet).join(' ').trim()

  const params = {
    page: pagination.page,
    page_size: pagination.page_size
  }

  if (keyword) {
    params.keyword = keyword
    params.search = keyword
  }

  if (start) params.time_start = start
  if (end) params.time_end = end
  // 兼容旧后端：提供 time 字段（单日或区间）
  if (start && end) {
    params.time = start === end ? start : `${start}-${end}`
  } else if (start) {
    params.time = start
  } else if (end) {
    params.time = end
  }

  const tag1Ids = selectedTags.value
    .filter((t) => t.__kind === '兴趣' && t.id !== undefined && /^\d+$/.test(String(t.id)))
    .map((t) => String(t.id))
  if (tag1Ids.length) params.tag1_ids = tag1Ids.join(',')

  return params
}

function pickArray(payload) {
  if (Array.isArray(payload)) return payload
  return (
    payload?.list ??
    payload?.requirements ??
    payload?.results ??
    payload?.items ??
    payload?.records ??
    payload?.rows ??
    (Array.isArray(payload?.data) ? payload.data : [])
  )
}

function pickTotal(payload, defaultLen = 0) {
  const pg = payload?.pagination || {}
  const total =
    pg.total ?? pg.total_count ?? payload?.total ?? payload?.count ?? payload?.total_count ?? 0
  if (total) return total
  const totalPages = pg.total_pages ?? payload?.total_pages
  const pageSize = pg.page_size ?? payload?.page_size ?? pagination.page_size
  if (totalPages && pageSize) return totalPages * pageSize
  return defaultLen
}

// === 替换 loadList 函数 BEGIN ===
async function loadList() {
  loading.value = true
  const queryParams = buildParams()
  try {
    // 调试输出（可保留，排查后可去掉）
    console.debug('[requirement][list] params =>', queryParams)
    const { data } = await getRequirementList(queryParams)
    const payload = data?.data ?? data ?? {}
    const arr = pickArray(payload) || []
    list.value = arr.map(normalizeListItem)
    populateFavoriteStatusFromList(list.value)
    pagination.total = pickTotal(payload, arr.length)
  } catch (err) {
    console.error('[requirement][list] error =>', err?.response?.data || err)
    list.value = []
    pagination.total = 0
    ElMessage.error(err?.response?.data?.message || err?.message || '需求列表加载失败')
  } finally {
    loading.value = false
  }
}
// === 替换 loadList 函数 END ===

function onSearch() {
  pagination.page = 1
  loadList()
}

function onReset() {
  filters.time_start = ''
  filters.time_end = ''
  selectedTags.value = []
  tagQuery.value = ''
  tagSuggest.value = []
  showSuggest.value = false
  acIndex.value = -1
  pagination.page = 1
  pagination.page_size = 10
  loadList()
}

function toPrev() {
  if (pagination.page > 1) {
    pagination.page -= 1
    loadList()
  }
}

function toNext() {
  if (pagination.page < totalPages.value) {
    pagination.page += 1
    loadList()
  }
}

function onPageSizeChange() {
  pagination.page = 1
  loadList()
}

/* ====== 日期控件 ====== */
const startDateRef = ref(null)
const endDateRef = ref(null)

function openStartPicker() {
  const el = startDateRef.value
  if (!el) return
  try {
    if (typeof el.showPicker === 'function') el.showPicker()
    else {
      el.focus()
      setTimeout(() => el.click?.(), 0)
    }
  } catch {
    el.focus()
  }
}

function openEndPicker() {
  const el = endDateRef.value
  if (!el) return
  try {
    if (typeof el.showPicker === 'function') el.showPicker()
    else {
      el.focus()
      setTimeout(() => el.click?.(), 0)
    }
  } catch {
    el.focus()
  }
}

function ensurePicker(which) {
  requestAnimationFrame(() => {
    which === 'start' ? openStartPicker() : openEndPicker()
  })
}

/* ====== 已加入 / 详情 ====== */
function isJoined(requirementId) {
  return !!followStatusMap[requirementId]
}

async function joinRequirement() {
  if (!detail.value?.id) return
  const requirementId = detail.value.id
  if (isJoined(requirementId)) {
    ElMessage.info('你已加入此需求')
    return
  }
  try {
    await followDemand(requirementId)
    followStatusMap[requirementId] = true
    ElMessage.success('已收藏，可在「我的收藏」中查看')
    detailVisible.value = false
    setTimeout(() => router.push('/student/demand-following'), 600)
  } catch (e) {
    console.error(e)
    ElMessage.error(e?.message || '收藏失败')
  }
}

const detail = ref(null)
const detailVisible = ref(false)

// 预算没有值时整栏隐藏（原写法 detail.budget + '万' 会渲染成 "null万"）
const hasBudget = computed(() => {
  const b = detail.value?.budget
  if (b === null || b === undefined) return false
  const s = String(b).trim()
  return s !== '' && s !== '-' && s !== '—'
})

// === 替换 openDetail 函数 BEGIN ===
async function openDetail(item) {
  if (!item?.id) return
  try {
    const { data } = await getRequirementDetail(item.id)
    const payload = data?.data ?? data ?? {}
    detail.value = normalizeDetailPayload(payload)
    detailVisible.value = true
  } catch (e) {
    console.error('[requirement][detail] error =>', e?.response?.data || e)
    detail.value = null
    ElMessage.error(e?.response?.data?.message || e?.message || '获取需求详情失败')
  }
}
// === 替换 openDetail 函数 END ===

// 智能体（知途）把机会收藏后，同步列表里的关注状态
function onAgentAction({ name, data }) {
  if (name === 'requirement_favorited' && data?.requirement_id) {
    followStatusMap[data.requirement_id] = true
    ElMessage.success('已加入「我的收藏」')
  }
}

onMounted(loadList)
</script>

<style scoped>
/* Layout */
.page {
  padding: 16px;
  max-width: 1200px;
  margin: 0 auto;
}
.page-title {
  margin: 0 0 12px;
  font-size: 20px;
  font-weight: 600;
}
.agent-container {
  margin: 0 0 16px;
  width: 100%;
}

/* Filters */
.filters {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 12px;
}
.filters-row {
  --filter-min: 260px;
  --label-h: 18px;
  --label-gap: 6px;
  --control-h: 40px;
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(var(--filter-min), 1fr));
  gap: 12px;
  align-items: start;
}
@media (max-width: 600px) {
  .filters-row {
    --filter-min: 200px;
  }
}
.field-inline {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  flex-direction: column;
}
.field-grow {
  min-width: 0;
}

/* 关键词搜索框 */
.keyword-wrap {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}
.keyword-wrap .input {
  flex: 1;
  min-width: 0;
}
.keyword-clear {
  flex-shrink: 0;
  height: 40px;
  padding: 0 12px;
  border: 1px solid #d1d5db;
  background: #fff;
  border-radius: 8px;
  color: #4b5563;
  font-size: 13px;
  cursor: pointer;
}
.keyword-clear:hover {
  border-color: #9ca3af;
  color: #111827;
}
.label {
  color: #6b7280;
  font-size: 12px;
  min-height: var(--label-h);
  margin-bottom: var(--label-gap);
}

/* Inputs */
.input {
  height: var(--control-h);
  padding: 0 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  min-width: 0;
  width: 100%;
  background: #fff;
}

/* Auto-complete dropdown */
.ac-wrap {
  position: relative;
  display: block;
  width: 100%;
}
.ac-list {
  position: absolute;
  top: calc(100% + 6px);
  left: 0;
  right: 0;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 6px 0;
  margin: 0;
  list-style: none;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
  max-height: 300px;
  overflow: auto;
  z-index: 200;
}
.ac-item {
  padding: 8px 12px;
  line-height: 1.4;
  cursor: pointer;
  color: #111827;
}
.ac-item:hover,
.ac-active {
  background: #f3f4f6;
}

/* Chips */
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-top: 6px;
  max-height: 48px;
  overflow: auto;
  padding-right: 2px;
}
.chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: #eef2ff;
  color: #3730a3;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 12px;
  white-space: nowrap;
}
.chip-x {
  cursor: pointer;
}

/* Date range */
.filter-time .label {
  margin-bottom: var(--label-gap);
}
.date-range {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: 100%;
}
.date-field {
  position: relative;
  display: inline-flex;
  align-items: center;
  min-width: 0;
  width: 100%;
  height: var(--control-h);
  padding: 0 10px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  background: #fff;
  cursor: text;
}
.date-field:hover {
  border-color: #cbd5e1;
}
.date-field:focus-within {
  border-color: #2563eb;
  box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.12);
}

/* native date input */
.input-date {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  background: transparent;
  padding: 0;
  font-size: 14px;
  color: #111827;
  appearance: none;
  caret-color: #2563eb;
}
.input-date:not(.has-value) {
  caret-color: transparent;
}
.input-date:not(.has-value)::-webkit-datetime-edit,
.input-date:not(.has-value)::-webkit-datetime-edit-text,
.input-date:not(.has-value)::-webkit-datetime-edit-year-field,
.input-date:not(.has-value)::-webkit-datetime-edit-month-field,
.input-date:not(.has-value)::-webkit-datetime-edit-day-field {
  color: transparent;
}
.input-date:not(.has-value)::-webkit-datetime-edit-year-field:focus,
.input-date:not(.has-value)::-webkit-datetime-edit-month-field:focus,
.input-date:not(.has-value)::-webkit-datetime-edit-day-field:focus {
  color: transparent;
  background-color: transparent;
}
.input-date:not(.has-value)::selection {
  background: transparent;
  color: transparent;
}
.input-date.has-value::-webkit-datetime-edit {
  color: #111827;
}
.input-date::-webkit-calendar-picker-indicator {
  width: 24px;
  height: 24px;
  cursor: pointer;
  opacity: 0.9;
}
.input-date::-webkit-inner-spin-button,
.input-date::-webkit-clear-button {
  display: none;
}
.date-placeholder {
  position: absolute;
  left: 12px;
  right: 36px;
  color: #9ca3af;
  font-size: 14px;
  pointer-events: none;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sep {
  color: #9ca3af;
  user-select: none;
}

/* Actions */
.filters-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  width: 100%;
}
.label-spacer {
  height: calc(var(--label-h) + var(--label-gap));
  width: 100%;
}
.actions-row {
  display: inline-flex;
  gap: 10px;
  align-items: center;
}
@media (max-width: 900px) {
  .filters-actions {
    grid-column: 1 / -1;
    align-items: stretch;
  }
  .actions-row {
    width: 100%;
  }
  .actions-row .btn {
    flex: 1 1 0;
  }
}

/* Buttons */
.btn {
  min-height: var(--control-h);
  padding: 0 14px;
  border-radius: 10px;
  font-size: 14px;
  line-height: 1;
  transition: all 0.15s ease;
  border: 1px solid transparent;
  cursor: pointer;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.btn-primary {
  background: linear-gradient(180deg, #3b82f6 0%, #2563eb 100%);
  border-color: #1d4ed8;
  color: #fff;
  box-shadow: 0 2px 6px rgba(37, 99, 235, 0.25);
}
.btn-primary:hover:not(:disabled) {
  filter: brightness(1.05);
  transform: translateY(-1px);
}
.btn-secondary {
  background: #ffffff;
  color: #2563eb;
  border-color: #93c5fd;
}
.btn-secondary:hover:not(:disabled) {
  background: #f0f7ff;
  border-color: #60a5fa;
}

/* Drawer buttons */
.drawer-cancel-btn,
.drawer-join-btn {
  min-height: 44px;
  padding: 0 18px;
  border-radius: 12px;
  font-size: 16px;
}

/* List */
.list {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}
@media (max-width: 900px) {
  .list {
    grid-template-columns: 1fr;
  }
}
.card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 12px;
  cursor: pointer;
  transition: box-shadow 0.2s ease;
  background: #fff;
}
.card:hover {
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
}
.card-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.title {
  font-size: 16px;
  font-weight: 600;
}
.status {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
}
.status--in_progress {
  background: #ecfdf5;
  color: #065f46;
  border-color: #a7f3d0;
}
.status--completed {
  background: #eff6ff;
  color: #1e3a8a;
  border-color: #bfdbfe;
}
.status--paused {
  background: #fff7ed;
  color: #9a3412;
  border-color: #fed7aa;
}
.status--under_review {
  background: #f5f3ff;
  color: #5b21b6;
  border-color: #ddd6fe;
}
.status--review_failed {
  background: #fef2f2;
  color: #991b1b;
  border-color: #fecaca;
}
.meta {
  margin-top: 6px;
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 6px;
}
.logo {
  width: 18px;
  height: 18px;
  object-fit: cover;
  border-radius: 4px;
}
.tags {
  margin-top: 8px;
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  background: #f3f4f6;
  color: #374151;
}
.tag--sub {
  background: #eef2ff;
  color: #3730a3;
}
.summary {
  margin-top: 8px;
  color: #4b5563;
}

/* 截止时间：有值用橙色提醒，没有则写「以官网为准」 */
.deadline {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  padding: 2px 10px;
  border: 1px solid #fed7aa;
  border-radius: 999px;
  background: #fff7ed;
  color: #b45309;
  font-size: 13px;
  line-height: 20px;
}
.deadline-label {
  font-size: 12px;
  color: #9a3412;
}
.deadline-value {
  white-space: nowrap;
}
.deadline--tbd {
  border-color: #e5e7eb;
  background: #f3f4f6;
  color: #6b7280;
}
.deadline--tbd .deadline-label {
  color: #6b7280;
}

/* Pagination & states */
.loading,
.empty {
  text-align: center;
  color: #6b7280;
  padding: 40px 0;
}
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 14px;
  gap: 12px;
  flex-wrap: wrap;
}
.pager {
  display: flex;
  align-items: center;
  gap: 8px;
}
.page-size {
  display: flex;
  align-items: center;
  gap: 6px;
}
.select {
  padding: 4px 8px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #fff;
}

/* Drawer */
.drawer-mask {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.35);
  display: flex;
  justify-content: flex-end;
  z-index: 1000;
}
.drawer {
  width: min(720px, 100%);
  height: 100%;
  background: #fff;
  padding: 16px;
  overflow: auto;
}
.drawer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 8px;
  margin-bottom: 12px;
}
.drawer-title {
  display: flex;
  gap: 10px;
  align-items: center;
}
.org-logo {
  width: 36px;
  height: 36px;
  object-fit: cover;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
}
.title-wrap {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.drawer-h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}
.id-chip {
  margin-left: 6px;
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  border-radius: 6px;
  padding: 0 6px;
}
.subtitle {
  color: #6b7280;
  display: flex;
  align-items: center;
  gap: 6px;
}
.status-badge {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 999px;
  border: 1px solid #e5e7eb;
}
.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
  margin: 10px 0;
}
.info-item {
  display: flex;
  gap: 6px;
}
.info-label {
  color: #4b5563;
  min-width: 64px;
}
.info-value {
  color: #111827;
}
.drawer-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  margin: 8px 0;
}
.group-label {
  color: #4b5563;
  font-size: 12px;
  padding-right: 4px;
}
.drawer-desc {
  white-space: pre-wrap;
  line-height: 1.6;
  margin-top: 8px;
  color: #1f2937;
}
.drawer-res {
  margin-top: 12px;
}
.drawer-res h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  color: #374151;
}
.drawer-res ul {
  margin: 0;
  padding-left: 20px;
}
.drawer-res li {
  margin-bottom: 4px;
}
.drawer-res a {
  color: #2563eb;
  text-decoration: none;
}
.drawer-res a:hover {
  text-decoration: underline;
}
.drawer-actions {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
