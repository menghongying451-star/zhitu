<script setup>
/**
 * 历史对话（纯前端版本）
 *
 * 数据目前只存在浏览器 localStorage 里，第一次打开会写入几条演示会话。
 * 以后接后端时，把 load() / removeOne() / clearAll() 换成接口调用即可，
 * 页面结构不用动。
 *
 * 存储结构：
 *   [{ id, agent, title, createdAt, messages: [{ role: 'user' | 'assistant', content }] }]
 */
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Delete, Timer } from '@element-plus/icons-vue'

const STORAGE_KEY = 'zhitu_chat_history_v1'

// 演示数据：等你接后端后删掉这段即可
const DEMO_CONVERSATIONS = [
  {
    id: 'demo-1',
    agent: 'zhitu',
    title: '我是计算机专业的，想找 AI 方向的实习',
    createdAt: Date.now() - 1000 * 60 * 35,
    messages: [
      { role: 'user', content: '我是计算机专业大二，想找和 AI 相关的实习，有什么推荐吗？' },
      {
        role: 'assistant',
        content:
          '从你的方向看，可以先关注两类机会：一是实验室的大模型/NLP 课题，门槛相对低、能积累科研经历；二是企业的算法实习岗，通常要求能稳定实习 3 个月以上。要不要我按「人工智能」这个领域帮你筛一下现在在招的机会？'
      },
      { role: 'user', content: '好，优先看北京市内的' },
      {
        role: 'assistant',
        content:
          '已经按「人工智能 + 北京」整理出 3 个方向：大模型算法研究助理、数据分析实习、算法工程实习生。前两个对本科在读更友好，第三个要求有 Python 工程经验。'
      }
    ]
  },
  {
    id: 'demo-2',
    agent: 'zhitu',
    title: '大二可以参加哪些竞赛',
    createdAt: Date.now() - 1000 * 60 * 60 * 26,
    messages: [
      { role: 'user', content: '大二可以参加哪些竞赛？我没什么项目经历。' },
      {
        role: 'assistant',
        content:
          '没有项目经历也不用担心，竞赛本身就是很好的起步方式。适合大二的有：数学建模（组队友好、周期短）、蓝桥杯（算法基础）、以及各类创新创业大赛（偏方案设计）。你想偏算法还是偏产品？我可以再帮你细分。'
      }
    ]
  },
  {
    id: 'demo-3',
    agent: 'zhitu',
    title: '实验室招人一般看重什么',
    createdAt: Date.now() - 1000 * 60 * 60 * 24 * 5,
    messages: [
      { role: 'user', content: '实验室招人一般看重什么？' },
      {
        role: 'assistant',
        content:
          '通常看三点：一是基础（数学、编程语言），二是能否投入稳定时间（每周到岗天数），三是有没有自学过的痕迹（课程设计、开源项目、竞赛）。招人的老师一般会优先问你「最近在学什么、做过什么」。'
      }
    ]
  }
]

const conversations = ref([])
const activeId = ref('')

const activeConversation = computed(
  () => conversations.value.find((c) => c.id === activeId.value) || null
)

// 按时间倒序展示
const sortedConversations = computed(() =>
  [...conversations.value].sort((a, b) => b.createdAt - a.createdAt)
)

function load() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) {
        conversations.value = parsed
      }
    }
  } catch {
    // 存储损坏时退回演示数据
    conversations.value = []
  }

  if (!conversations.value.length) {
    conversations.value = DEMO_CONVERSATIONS.map((c) => ({ ...c, messages: [...c.messages] }))
    persist()
  }

  activeId.value = sortedConversations.value[0]?.id || ''
}

function persist() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(conversations.value))
  } catch {
    // 隐私模式/配额满时静默失败，不影响页面浏览
  }
}

function selectConversation(id) {
  activeId.value = id
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

  conversations.value = conversations.value.filter((c) => c.id !== item.id)
  if (activeId.value === item.id) {
    activeId.value = sortedConversations.value[0]?.id || ''
  }
  persist()
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

  conversations.value = []
  activeId.value = ''
  persist()
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

    <!-- 纯前端阶段：数据只在本机浏览器里 -->
    <el-alert
      class="local-tip"
      type="info"
      :closable="false"
      show-icon
      title="当前为本地演示数据，只保存在这台电脑的浏览器里，不会同步到其他设备"
    />

    <div v-if="!conversations.length" class="empty-wrap">
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
              <span class="conv-count">{{ item.messages.length }} 条</span>
            </div>
          </button>
          <button class="conv-delete" title="删除这条对话" @click.stop="removeOne(item)">
            <el-icon><Delete /></el-icon>
          </button>
        </div>
      </aside>

      <!-- 右：对话内容 -->
      <section class="conv-detail">
        <template v-if="activeConversation">
          <div class="detail-header">
            <h2 class="detail-title">{{ activeConversation.title }}</h2>
            <span class="detail-time">{{ formatTime(activeConversation.createdAt) }}</span>
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
