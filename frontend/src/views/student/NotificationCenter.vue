<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { StarFilled, Star, MoreFilled, Bell, Check, Close, Setting } from '@element-plus/icons-vue'

// 路由
const router = useRouter()

// 模拟通知数据（真实环境请用接口替换）
/*
  字段说明：
  - id: 唯一标识
  - type: 'system' | 'project' | 'application' | 'mention'
  - title: 标题
  - content: 内容摘要
  - createdAt: 创建时间（字符串或时间戳）
  - read: 是否已读
  - pinned: 是否置顶
  - projectId / projectTitle: 关联项目（项目类/提及类可能存在）
*/
const notifications = ref([
  {
    id: 'n-1001',
    type: 'system',
    title: '系统维护通知',
    content: '本周六 02:00-03:00 进行例行维护，届时服务将短暂不可用。',
    createdAt: '2025-08-12 09:00',
    read: false,
    pinned: true
  },
  {
    id: 'n-1002',
    type: 'project',
    title: '项目进度更新 - 智能客服系统开发',
    content: '接口文档已更新到 v1.2，请前往项目资源查看。',
    projectId: 101,
    projectTitle: '智能客服系统开发',
    createdAt: '2025-08-13 15:20',
    read: false,
    pinned: false
  },
  {
    id: 'n-1003',
    type: 'application',
    title: '申请已通过 - 数据可视化平台',
    content: '恭喜，你申请加入《数据可视化平台》已通过，请留意后续分工。',
    projectId: 102,
    projectTitle: '数据可视化平台',
    createdAt: '2025-08-10 08:00',
    read: true,
    pinned: false
  },
  {
    id: 'n-1004',
    type: 'mention',
    title: '在讨论中提到了你',
    content: '@你 麻烦看下 API 文档第 3 节，与前端联调参数对齐。',
    projectId: 101,
    projectTitle: '智能客服系统开发',
    createdAt: '2025-08-14 19:23',
    read: false,
    pinned: false
  },
  {
    id: 'n-1005',
    type: 'project',
    title: '任务提醒 - 智能客服系统开发',
    content: '“消息气泡组件”任务将于 8 月 20 日到期，请及时处理。',
    projectId: 101,
    projectTitle: '智能客服系统开发',
    createdAt: '2025-08-15 09:40',
    read: false,
    pinned: false
  }
])

// Tabs / 过滤
const currentTab = ref('all') // all | project | system | application | mention
const keyword = ref('')
const onlyUnread = ref(false)
const dateRange = ref([]) // [start, end]
const sortOrder = ref('desc') // desc | asc

// 选择与批量操作
const selected = ref([])

// 详情抽屉
const detailVisible = ref(false)
const currentRow = ref(null)

// 设置抽屉（偏好）
const prefVisible = ref(false)
const prefs = ref({
  receive: {
    system: true,
    project: true,
    application: true,
    mention: true
  },
  push: true,
  email: false,
  quietHours: false
})

const typeMeta = {
  system: { label: '系统', tagType: 'info' },
  project: { label: '项目', tagType: 'success' },
  application: { label: '申请', tagType: 'warning' },
  mention: { label: '提及', tagType: 'primary' }
}

// 统计
const counts = computed(() => {
  const c = { all: 0, system: 0, project: 0, application: 0, mention: 0 }
  const unread = { all: 0, system: 0, project: 0, application: 0, mention: 0 }
  for (const n of notifications.value) {
    c.all++
    c[n.type]++
    if (!n.read) {
      unread.all++
      unread[n.type]++
    }
  }
  return { total: c, unread }
})
const allUnreadCount = computed(() => counts.value.unread.all)

// 过滤 + 排序 + 分页
const pageSize = ref(10)
const currentPage = ref(1)

const filteredList = computed(() => {
  let list = notifications.value.slice()

  // 根据偏好过滤类型（不接收的类型不显示）
  list = list.filter((n) => prefs.value.receive[n.type] !== false)

  // 标签过滤
  if (currentTab.value !== 'all') {
    list = list.filter((n) => n.type === currentTab.value)
  }

  // 仅未读
  if (onlyUnread.value) {
    list = list.filter((n) => !n.read)
  }

  // 关键词
  const k = keyword.value.trim().toLowerCase()
  if (k) {
    list = list.filter((n) => {
      const pool = [n.title || '', n.content || '', n.projectTitle || ''].join(' ').toLowerCase()
      return pool.includes(k)
    })
  }

  // 日期范围
  if (
    Array.isArray(dateRange.value) &&
    dateRange.value.length === 2 &&
    dateRange.value[0] &&
    dateRange.value[1]
  ) {
    const start = new Date(dateRange.value[0]).getTime()
    const end = new Date(dateRange.value[1]).getTime() + 24 * 60 * 60 * 1000 - 1
    list = list.filter((n) => {
      const t = new Date(n.createdAt).getTime()
      return t >= start && t <= end
    })
  }

  // 置顶优先 + 时间排序
  list.sort((a, b) => {
    if (a.pinned !== b.pinned) return a.pinned ? -1 : 1
    const ta = new Date(a.createdAt).getTime()
    const tb = new Date(b.createdAt).getTime()
    return sortOrder.value === 'desc' ? tb - ta : ta - tb
  })

  return list
})

const total = computed(() => filteredList.value.length)

const pagedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredList.value.slice(start, start + pageSize.value)
})

// 行点击 -> 打开详情
const openDetail = (row) => {
  currentRow.value = row
  detailVisible.value = true
  if (!row.read) {
    row.read = true
  }
}

// 跳转到项目
const goProject = (row) => {
  if (!row?.projectId) return
  router.push(`/student/my-projects/${row.projectId}`)
  detailVisible.value = false
}

// 单条操作
const toggleRead = (row) => {
  row.read = !row.read
}
const togglePin = (row) => {
  row.pinned = !row.pinned
}
const removeOne = (row) => {
  const idx = notifications.value.findIndex((n) => n.id === row.id)
  if (idx >= 0) notifications.value.splice(idx, 1)
  if (detailVisible.value && currentRow.value?.id === row.id) {
    detailVisible.value = false
  }
}

// 批量操作
const onSelectionChange = (rows) => {
  selected.value = rows
}
const markSelectedAsRead = () => {
  selected.value.forEach((r) => (r.read = true))
}
const markSelectedAsUnread = () => {
  selected.value.forEach((r) => (r.read = false))
}
const deleteSelected = () => {
  const ids = new Set(selected.value.map((r) => r.id))
  notifications.value = notifications.value.filter((n) => !ids.has(n.id))
  selected.value = []
}
const markAllFilteredAsRead = () => {
  filteredList.value.forEach((r) => (r.read = true))
}

// 重置筛选
const resetFilters = () => {
  keyword.value = ''
  onlyUnread.value = false
  dateRange.value = []
  sortOrder.value = 'desc'
  currentPage.value = 1
}
</script>

<template>
  <div class="notify-page">
    <div class="head">
      <div class="title">
        <el-icon :size="18" class="bell"><Bell /></el-icon>
        通知中心
        <el-tag v-if="allUnreadCount" type="danger" effect="light" size="small" class="ml8"
          >未读 {{ allUnreadCount }}</el-tag
        >
      </div>
      <div class="ops">
        <el-button size="small" @click="markAllFilteredAsRead">
          <el-icon class="mr4"><Check /></el-icon>标记当前筛选为已读
        </el-button>
        <el-button size="small" @click="resetFilters">重置</el-button>
        <el-button size="small" type="primary" plain @click="prefVisible = true">
          <el-icon class="mr4"><Setting /></el-icon>通知设置
        </el-button>
      </div>
    </div>

    <div class="toolbar">
      <el-tabs v-model="currentTab" class="tabs" @tab-change="currentPage = 1">
        <el-tab-pane :label="`全部 (${counts.total.all})`" name="all" />
        <el-tab-pane :label="`项目 (${counts.total.project})`" name="project" />
        <el-tab-pane :label="`系统 (${counts.total.system})`" name="system" />
        <el-tab-pane :label="`申请 (${counts.total.application})`" name="application" />
        <el-tab-pane :label="`提及 (${counts.total.mention})`" name="mention" />
      </el-tabs>

      <div class="filters">
        <el-input v-model="keyword" placeholder="搜索标题/内容/项目" clearable class="kw" />
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          unlink-panels
          class="dr"
        />
        <el-checkbox v-model="onlyUnread">仅未读</el-checkbox>
        <el-select v-model="sortOrder" class="so" placeholder="排序">
          <el-option label="按时间倒序" value="desc" />
          <el-option label="按时间正序" value="asc" />
        </el-select>
      </div>
    </div>

    <div class="list">
      <el-table
        :data="pagedList"
        border
        size="small"
        @selection-change="onSelectionChange"
        @row-dblclick="openDetail"
        row-class-name="notify-row"
      >
        <el-table-column type="selection" width="46" />
        <el-table-column label="类型" width="110">
          <template #default="{ row }">
            <el-tag :type="typeMeta[row.type]?.tagType" effect="light" size="small">
              {{ typeMeta[row.type]?.label || row.type }}
            </el-tag>
            <el-icon class="pin" v-if="row.pinned"><StarFilled /></el-icon>
          </template>
        </el-table-column>
        <el-table-column label="标题 / 摘要" min-width="360">
          <template #default="{ row }">
            <div class="title-line">
              <span class="title" :class="{ unread: !row.read }">{{ row.title }}</span>
              <el-tag
                v-if="row.projectTitle"
                size="small"
                type="info"
                effect="plain"
                class="proj-tag"
              >
                {{ row.projectTitle }}
              </el-tag>
            </div>
            <div class="summary">{{ row.content }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="createdAt" label="时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openDetail(row)">查看</el-button>
            <el-dropdown trigger="click">
              <el-button text
                >更多<el-icon class="ml4"><MoreFilled /></el-icon
              ></el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="toggleRead(row)">{{
                    row.read ? '标为未读' : '标为已读'
                  }}</el-dropdown-item>
                  <el-dropdown-item @click="togglePin(row)">{{
                    row.pinned ? '取消置顶' : '置顶'
                  }}</el-dropdown-item>
                  <el-dropdown-item divided @click="removeOne(row)">
                    <el-icon class="mr4"><Close /></el-icon>删除
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total === 0" class="empty">
        <el-empty description="暂无通知" />
      </div>

      <div class="table-footer" v-else>
        <div class="bulk">
          <span>已选择 {{ selected.length }} 项</span>
          <el-button size="small" @click="markSelectedAsRead">标记已读</el-button>
          <el-button size="small" @click="markSelectedAsUnread">标记未读</el-button>
          <el-button size="small" type="danger" plain @click="deleteSelected">删除</el-button>
        </div>
        <el-pagination
          layout="prev, pager, next"
          :page-size="pageSize"
          :total="total"
          v-model:current-page="currentPage"
          background
        />
      </div>
    </div>

    <!-- 详情抽屉 -->
    <el-drawer v-model="detailVisible" title="通知详情" size="40%" :close-on-click-modal="true">
      <template #header>
        <div class="drawer-hd">
          <div class="lh">
            <div class="row1">
              <el-tag
                v-if="currentRow"
                :type="typeMeta[currentRow.type]?.tagType"
                effect="light"
                size="small"
              >
                {{ currentRow ? typeMeta[currentRow.type]?.label : '' }}
              </el-tag>
              <span v-if="currentRow?.pinned" class="pin-lab"
                ><el-icon><StarFilled /></el-icon>置顶</span
              >
            </div>
            <div class="row2">
              <span class="ttl">{{ currentRow?.title }}</span>
            </div>
            <div class="row3">
              <span class="time">时间：{{ currentRow?.createdAt }}</span>
              <el-tag
                v-if="currentRow?.projectTitle"
                size="small"
                type="info"
                effect="plain"
                class="proj-tag"
              >
                {{ currentRow?.projectTitle }}
              </el-tag>
            </div>
          </div>
          <div class="rh">
            <el-button size="small" @click="currentRow && toggleRead(currentRow)">{{
              currentRow?.read ? '标为未读' : '标为已读'
            }}</el-button>
            <el-button size="small" @click="currentRow && togglePin(currentRow)">{{
              currentRow?.pinned ? '取消置顶' : '置顶'
            }}</el-button>
            <el-button size="small" type="danger" plain @click="currentRow && removeOne(currentRow)"
              >删除</el-button
            >
          </div>
        </div>
      </template>

      <div class="drawer-body">
        <div class="content">{{ currentRow?.content }}</div>
        <div class="actions">
          <el-button v-if="currentRow?.projectId" type="primary" @click="goProject(currentRow)"
            >前往项目</el-button
          >
        </div>
      </div>
    </el-drawer>

    <!-- 偏好设置 -->
    <el-drawer v-model="prefVisible" title="通知设置" size="30%">
      <div class="prefs">
        <div class="block">
          <div class="label">接收通知类型</div>
          <el-checkbox v-model="prefs.receive.system">系统</el-checkbox>
          <el-checkbox v-model="prefs.receive.project">项目</el-checkbox>
          <el-checkbox v-model="prefs.receive.application">申请</el-checkbox>
          <el-checkbox v-model="prefs.receive.mention">提及</el-checkbox>
        </div>
        <el-divider />
        <div class="block">
          <div class="label">通知方式</div>
          <el-checkbox v-model="prefs.push">站内推送</el-checkbox>
          <el-checkbox v-model="prefs.email">邮件通知</el-checkbox>
        </div>
        <el-divider />
        <div class="block">
          <div class="label">其他</div>
          <el-checkbox v-model="prefs.quietHours">夜间免打扰（23:00-8:00）</el-checkbox>
        </div>
        <div class="hint">说明：设置仅影响前端展示与订阅偏好，实际投递以后端策略为准。</div>
      </div>
    </el-drawer>
  </div>
</template>

<style scoped lang="scss">
.notify-page {
  padding: 12px 16px 20px;
}
.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
  .title {
    font-weight: 800;
    color: #1d2129;
    font-size: 18px;
    display: flex;
    align-items: center;
    .bell {
      color: #165dff;
      margin-right: 6px;
    }
    .ml8 {
      margin-left: 8px;
    }
  }
  .ops {
    display: flex;
    gap: 8px;
  }
}
.toolbar {
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  padding: 10px;
  margin-bottom: 10px;
  .tabs :deep(.el-tabs__nav) {
    margin-left: 6px;
  }
  .filters {
    margin-top: 8px;
    display: grid;
    grid-template-columns: 1fr auto auto auto;
    gap: 8px;
    align-items: center;
    .kw {
      width: 100%;
    }
    .dr {
      width: 280px;
    }
    .so {
      width: 140px;
    }
    @media (max-width: 880px) {
      grid-template-columns: 1fr 1fr;
      .dr,
      .so {
        width: 100%;
      }
    }
  }
}
.list {
  background: #fff;
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  padding: 10px;
  .notify-row td {
    vertical-align: top;
  }
  .pin {
    color: #f59e0b;
    margin-left: 6px;
  }
  .title-line {
    display: flex;
    align-items: center;
    gap: 8px;
    .title {
      font-weight: 700;
      color: #1d2129;
    }
    .title.unread {
      color: #165dff;
    }
    .proj-tag {
      margin-left: 2px;
    }
  }
  .summary {
    color: #86909c;
    margin-top: 4px;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
  }
  .empty {
    padding: 24px 0;
  }
  .table-footer {
    margin-top: 8px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    .bulk {
      display: flex;
      align-items: center;
      gap: 8px;
      color: #86909c;
    }
  }
}
.drawer-hd {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  .lh {
    .row1 {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .row2 {
      .ttl {
        font-size: 16px;
        font-weight: 800;
        color: #1d2129;
      }
    }
    .row3 {
      margin-top: 4px;
      display: flex;
      gap: 8px;
      align-items: center;
      color: #86909c;
    }
    .pin-lab {
      color: #f59e0b;
      display: inline-flex;
      align-items: center;
      gap: 4px;
      font-size: 12px;
    }
  }
  .rh {
    display: flex;
    gap: 8px;
  }
}
.drawer-body {
  .content {
    color: #4e5969;
    line-height: 1.7;
  }
  .actions {
    margin-top: 12px;
  }
}
.prefs {
  .block {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
  }
  .label {
    font-weight: 700;
    color: #1d2129;
  }
  .hint {
    color: #86909c;
    font-size: 12px;
    margin-top: 8px;
  }
}
</style>
