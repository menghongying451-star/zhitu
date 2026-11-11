<script setup>
/**
 * 历史对话：读取后端保存的智能体对话记录
 *   GET    /api/v1/agent/conversations/          会话列表
 *   GET    /api/v1/agent/conversations/<id>/     单个会话的全部消息
 *   DELETE /api/v1/agent/conversations/<id>/     删除一个会话
 *   DELETE /api/v1/agent/conversations/          清空全部
 */
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Timer } from '@element-plus/icons-vue'
import {
  listConversations,
  getConversation,
  deleteConversation,
  clearConversations
} from '@/api/agent'

const router = useRouter()
const conversations = ref([]) // [{ id, agent, agent_title, title, createdAt, count }]
const activeId = ref('')
const detail = ref(null) // { ...会话, messages: [{ role, content }] }
const loading = ref(false)
const detailLoading = ref(false)

const activeConversation = computed(() =>
  detail.value && detail.value.id === activeId.value ? detail.value : null
)

// 按最后对话时间倒序（后端已排好，这里再保险一次）
const sortedConversations = computed(() =>
  [...conversations.value].sort((a, b) => b.updatedAt - a.updatedAt)
)

async function load() {
  loading.value = true
  try {
    const { data } = await listConversations()
    conversations.value = (Array.isArray(data) ? data : []).map((c) => ({
      id: c.id,
      agent: c.agent,
      agentTitle: c.agent_title,
      title: c.title,
      createdAt: new Date(c.created_at).getTime(),
      updatedAt: new Date(c.updated_at).getTime(),
      count: c.message_count || 0
    }))
    if (sortedConversations.value.length) await selectConversation(sortedConversations.value[0].id)
  } catch (err) {
    ElMessage.error(err?.response?.data?.detail || '历史对话加载失败')
  } finally {
    loading.value = false
  }
}

async function selectConversation(id) {
  activeId.value = id
  detailLoading.value = true
  try {
    const { data } = await getConversation(id)
    if (activeId.value !== id) return // 用户已经点了别的
    detail.value = { ...data, createdAt: new Date(data.created_at).getTime() }
  } catch {
    ElMessage.error('这条对话加载失败')
  } finally {
    detailLoading.value = false
  }
}

function continueChat(item) {
  // 目前只有知途支持从历史接着聊（文识需要先选中具体机会）
  router.push({ path: '/student/project-requirement', query: { conv: item.id } })
}

async function removeOne(item) {
  try {
    await ElMessageBox.confirm(`删除「${item.title}」这条对话记录？`, '删除对话', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch {
    return // 用户取消
  }
  try {
    await deleteConversation(item.id)
  } catch {
    ElMessage.error('删除失败，请稍后重试')
    return
  }
  conversations.value = conversations.value.filter((c) => c.id !== item.id)
  if (activeId.value === item.id) {
    detail.value = null
    activeId.value = ''
    if (sortedConversations.value.length) selectConversation(sortedConversations.value[0].id)
  }
  ElMessage.success('已删除')
}

async function clearAll() {
  if (!conversations.value.length) return
  try {
    await ElMessageBox.confirm('清空全部历史对话？此操作不可恢复。', '清空历史', {
      type: 'warning',
      confirmButtonText: '清空',
      cancelButtonText: '取消'
    })
  } catch {
    return
  }
  try {
    await clearConversations()
  } catch {
    ElMessage.error('清空失败，请稍后重试')
    return
  }
  conversations.value = []
  activeId.value = ''
  detail.value = null
  ElMessage.success('已清空')
}

function formatTime(ts) {
  const d = new Date(ts)
  const now = new Date()
  const pad = (n) => String(n).padStart(2, '0')
  const sameDay =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate()

  if (sameDay) return `今天 ${pad(d.getHours())}:${pad(d.getMinutes())}`

  const yesterday = new Date(now)
  yesterday.setDate(now.getDate() - 1)
  const isYesterday =
    d.getFullYear() === yesterday.getFullYear() &&
    d.getMonth() === yesterday.getMonth() &&
    d.getDate() === yesterday.getDate()
  if (isYesterday) return `昨天 ${pad(d.getHours())}:${pad(d.getMinutes())}`

  return `${d.getMonth() + 1}月${d.getDate()}日 ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

onMounted(load)
</script>

<template>
  <div class="chat-history">
    <header class="page-header">
      <div class="header-text">
        <h1 class="page-title">历史对话</h1>
        <p class="page-description">回看你与智能体聊过的内容，方便接着往下问</p>
      </div>
      <el-button v-if="conversations.length" :icon="Delete" plain @click="clearAll">
        清空全部
      </el-button>
    </header>

    <div v-if="loading" class="empty-wrap">
      <el-empty description="加载中…" />
    </div>

    <div v-else-if="!conversations.length" class="empty-wrap">
      <el-empty description="还没有对话记录，去「找机会」和智能体聊聊吧" />
    </div>

    <div v-else class="history-body">
      <!-- 左：会话列表 -->
      <aside class="conv-list">
        <div v-for="item in sortedConversations" :key="item.id" class="conv-item-wrap">
          <button
            class="conv-item"
            :class="{ active: item.id === activeId }"
            @click="selectConversation(item.id)"
          >
            <div class="conv-title">{{ item.title }}</div>
            <div class="conv-meta">
              <span class="conv-time">
                <el-icon><Timer /></el-icon>
                {{ formatTime(item.createdAt) }}
              </span>
              <span class="conv-count">{{ item.agentTitle }} · {{ item.count }} 条</span>
            </div>
          </button>
          <button class="conv-delete" title="删除这条对话" @click.stop="removeOne(item)">
            <el-icon><Delete /></el-icon>
          </button>
        </div>
      </aside>

      <!-- 右：对话内容 -->
      <section class="conv-detail" v-loading="detailLoading">
        <template v-if="activeConversation">
          <div class="detail-header">
            <h2 class="detail-title">{{ activeConversation.title }}</h2>
            <span class="detail-time">{{ formatTime(activeConversation.createdAt) }}</span>
            <el-button
              v-if="activeConversation.agent === 'zhitu'"
              size="small"
              type="primary"
              plain
              @click="continueChat(activeConversation)"
            >
              接着聊
            </el-button>
          </div>

          <div class="messages">
            <div
              v-for="(m, i) in activeConversation.messages"
              :key="i"
              class="msg-row"
              :class="m.role"
            >
              <div class="msg-bubble">{{ m.content }}</div>
            </div>
          </div>
        </template>

        <el-empty v-else description="从左侧选择一条对话" />
      </section>
    </div>
  </div>
</template>

<style scoped>
.chat-history {
  padding: 24px;
  background-color: #f2f3f5;
  min-height: 100%;
  box-sizing: border-box;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;

  .page-title {
    margin: 0;
    font-size: 22px;
    font-weight: 600;
    color: #1d2129;
  }

  .page-description {
    margin: 6px 0 0;
    font-size: 14px;
    color: #86909c;
  }
}

.local-tip {
  margin-bottom: 16px;
}

.empty-wrap {
  background: #fff;
  border-radius: 12px;
  padding: 40px 0;
}

.history-body {
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

/* 左：会话列表 */
.conv-list {
  width: 320px;
  flex-shrink: 0;
  background: #fff;
  border-radius: 12px;
  padding: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  max-height: calc(100vh - 250px);
  overflow-y: auto;
}

.conv-item-wrap {
  position: relative;

  &:hover .conv-delete {
    display: inline-flex;
  }
}

.conv-item {
  position: relative;
  display: block;
  width: 100%;
  text-align: left;
  border: none;
  background: transparent;
  padding: 12px 36px 12px 12px;
  border-radius: 8px;
  cursor: pointer;
  font: inherit;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #f7f8fa;
  }

  &.active {
    background-color: rgba(22, 93, 255, 0.08);

    .conv-title {
      color: #165dff;
    }
  }

  .conv-title {
    font-size: 14px;
    font-weight: 500;
    color: #1d2129;
    line-height: 1.4;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .conv-meta {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-top: 6px;
    font-size: 12px;
    color: #86909c;
  }

  .conv-time {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }

  .conv-count {
    color: #a9aeb8;
  }
}

.conv-delete {
  position: absolute;
  top: 10px;
  right: 10px;
  display: none;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border: none;
  background: transparent;
  border-radius: 6px;
  color: #86909c;
  cursor: pointer;
  font-size: 14px;

  &:hover {
    background-color: #ffece8;
    color: #f53f3f;
  }
}

/* 右：对话内容 */
.conv-detail {
  flex: 1;
  min-width: 0;
  background: #fff;
  border-radius: 12px;
  padding: 20px 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
  max-height: calc(100vh - 250px);
  overflow-y: auto;

  .detail-header {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid #f2f3f5;
    margin-bottom: 16px;
  }

  .detail-title {
    margin: 0;
    font-size: 16px;
    font-weight: 600;
    color: #1d2129;
  }

  .detail-time {
    font-size: 12px;
    color: #86909c;
    white-space: nowrap;
  }

  .messages {
    display: flex;
    flex-direction: column;
    gap: 12px;
  }

  .msg-row {
    display: flex;

    &.user {
      justify-content: flex-end;
    }

    &.assistant {
      justify-content: flex-start;
    }
  }

  .msg-bubble {
    max-width: 76%;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 14px;
    line-height: 1.7;
    white-space: pre-wrap;
    word-break: break-word;
  }

  .msg-row.user .msg-bubble {
    background-color: #165dff;
    color: #fff;
  }

  .msg-row.assistant .msg-bubble {
    background-color: #f7f8fa;
    color: #1d2129;
  }
}

@media (max-width: 900px) {
  .history-body {
    flex-direction: column;
  }

  .conv-list {
    width: 100%;
    max-height: 280px;
  }

  .conv-detail {
    width: 100%;
  }
}
</style>
