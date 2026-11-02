<script setup>
/**
 * 智能体对话组件（替代原 Dify iframe / embed）
 *
 * 用法：
 *   <AgentChat agent="wenshi" :inputs="{ pid: demand.id }" />
 *   <AgentChat agent="zhitu" @action="onAgentAction" />
 *   <AgentChat agent="tianbao" @action="onAgentAction" />
 *
 * action 事件：智能体完成了需要页面配合的操作，例如
 *   { name: 'requirement_published', data: { requirement_id } }   填宝发布成功
 *   { name: 'requirement_favorited', data: { requirement_id } }   知途归档到「我要揭榜」
 *   { name: 'preference_saved', data: { tag1, tag2 } }            知途方向偏好录入
 */
import { ref, reactive, computed, watch, onMounted, onBeforeUnmount, nextTick } from 'vue'
import MarkdownIt from 'markdown-it'
import { getAgentMeta, streamAgentChat } from '@/api/agent'

const props = defineProps({
  agent: { type: String, required: true },
  inputs: { type: Object, default: () => ({}) },
  minHeight: { type: [Number, String], default: 600 },
  showTone: { type: Boolean, default: true },
  title: { type: String, default: '' }
})
const emit = defineEmits(['action', 'loaded'])

const md = new MarkdownIt({ html: false, linkify: true, breaks: true })
const renderMd = (text) => md.render(text || '')

const meta = reactive({
  title: '',
  opening: '',
  suggestions: [],
  allow_file: false,
  file_hint: '',
  accept: ''
})
const messages = ref([])
const draft = ref('')
const tone = ref('')
const pendingFile = ref(null)
const loading = ref(false)
const conversationId = ref('')
const listEl = ref(null)
const fileEl = ref(null)
let controller = null

const heightStyle = computed(() => {
  const h = typeof props.minHeight === 'number' ? `${props.minHeight}px` : props.minHeight
  return { minHeight: h, height: h }
})
const canSend = computed(() => !loading.value && (draft.value.trim() || pendingFile.value))
const showSuggestions = computed(
  () => meta.suggestions?.length && !messages.value.some((m) => m.role === 'user')
)

async function loadMeta() {
  try {
    const { data } = await getAgentMeta(props.agent)
    Object.assign(meta, data)
  } catch {
    meta.opening = '智能体信息加载失败，请刷新页面重试。'
  }
  resetConversation()
  emit('loaded', { agent: props.agent })
}

function resetConversation() {
  stop()
  conversationId.value = ''
  messages.value = meta.opening ? [{ role: 'assistant', content: meta.opening }] : []
  pendingFile.value = null
}

function scrollToBottom() {
  nextTick(() => {
    const el = listEl.value
    if (el) el.scrollTop = el.scrollHeight
  })
}

function pickFile() {
  fileEl.value?.click()
}
function onFileChange(e) {
  const f = e.target.files?.[0]
  e.target.value = ''
  if (!f) return
  if (f.size > 15 * 1024 * 1024) {
    messages.value.push({ role: 'assistant', content: '文件过大，请上传 15MB 以内的文件。' })
    scrollToBottom()
    return
  }
  pendingFile.value = f
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
    e.preventDefault()
    send()
  }
}

async function send(text) {
  const query = (typeof text === 'string' ? text : draft.value).trim()
  const file = pendingFile.value
  if (loading.value || (!query && !file)) return

  messages.value.push({ role: 'user', content: query, fileName: file?.name })
  const reply = reactive({ role: 'assistant', content: '', streaming: true, error: false })
  messages.value.push(reply)
  draft.value = ''
  pendingFile.value = null
  loading.value = true
  scrollToBottom()

  controller = new AbortController()
  try {
    await streamAgentChat(
      props.agent,
      {
        query,
        file,
        conversationId: conversationId.value,
        inputs: { ...props.inputs, ...(tone.value.trim() ? { tone: tone.value.trim() } : {}) }
      },
      {
        onEvent(ev) {
          if (ev.type === 'meta') conversationId.value = ev.conversation_id
          else if (ev.type === 'delta') {
            reply.content += ev.text
            scrollToBottom()
          } else if (ev.type === 'error') {
            reply.content += (reply.content ? '\n\n' : '') + ev.message
            reply.error = true
          } else if (ev.type === 'action') emit('action', { name: ev.name, data: ev.data })
        }
      },
      controller.signal
    )
  } catch (err) {
    if (err?.name !== 'AbortError') {
      reply.content += (reply.content ? '\n\n' : '') + (err?.message || '网络异常，请稍后重试')
      reply.error = true
    }
  } finally {
    reply.streaming = false
    if (!reply.content) reply.content = '（已停止）'
    loading.value = false
    controller = null
    scrollToBottom()
  }
}

function stop() {
  controller?.abort()
}

// 用字符串作为监听源：父组件重渲染时 inputs 会是新对象，但内容不变就不重置会话
watch(
  () => props.agent,
  () => loadMeta()
)
watch(
  () => JSON.stringify(props.inputs || {}),
  () => resetConversation()
)
onMounted(loadMeta)
onBeforeUnmount(stop)
</script>

<template>
  <div class="agent-chat" :style="heightStyle">
    <header class="ac-header">
      <div class="ac-title">
        <span class="ac-dot" />
        {{ title || meta.title || '智能体' }}
      </div>
      <div class="ac-tools">
        <input
          v-if="showTone"
          v-model="tone"
          class="ac-tone"
          maxlength="20"
          placeholder="回答风格（如：严谨）"
          title="设置智能体的回答风格"
        />
        <button class="ac-btn-text" :disabled="loading" @click="resetConversation">新对话</button>
      </div>
    </header>

    <div ref="listEl" class="ac-list">
      <div v-for="(m, i) in messages" :key="i" class="ac-row" :class="m.role">
        <div class="ac-bubble" :class="{ error: m.error }">
          <div v-if="m.fileName" class="ac-file-tag">📎 {{ m.fileName }}</div>
          <!-- eslint-disable-next-line vue/no-v-html -->
          <div v-if="m.role === 'assistant'" class="ac-md" v-html="renderMd(m.content)" />
          <div v-else class="ac-plain">{{ m.content }}</div>
          <span v-if="m.streaming && !m.content" class="ac-typing"><i /><i /><i /></span>
        </div>
      </div>

      <div v-if="showSuggestions" class="ac-suggest">
        <button v-for="s in meta.suggestions" :key="s" class="ac-chip" @click="send(s)">
          {{ s }}
        </button>
      </div>
    </div>

    <footer class="ac-footer">
      <div v-if="pendingFile" class="ac-pending">
        📎 {{ pendingFile.name }}
        <button class="ac-x" title="移除" @click="pendingFile = null">×</button>
      </div>
      <div class="ac-inputbar">
        <button
          v-if="meta.allow_file"
          class="ac-icon-btn"
          :title="meta.file_hint || '上传文件'"
          :disabled="loading"
          @click="pickFile"
        >
          <svg
            viewBox="0 0 24 24"
            width="18"
            height="18"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path
              d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"
            />
          </svg>
        </button>
        <input ref="fileEl" type="file" :accept="meta.accept" hidden @change="onFileChange" />
        <textarea
          v-model="draft"
          class="ac-input"
          rows="1"
          placeholder="输入消息，Enter 发送，Shift+Enter 换行"
          @keydown="onKeydown"
        />
        <button v-if="loading" class="ac-send stop" @click="stop">停止</button>
        <button v-else class="ac-send" :disabled="!canSend" @click="send()">发送</button>
      </div>
    </footer>
  </div>
</template>

<style scoped>
.agent-chat {
  --ac-primary: #4f6ef7;
  --ac-primary-soft: #eef1ff;
  --ac-border: #e5e8ef;
  --ac-text: #1f2329;
  --ac-sub: #8a8f99;
  display: flex;
  flex-direction: column;
  width: 100%;
  background: #fff;
  border: 1px solid var(--ac-border);
  border-radius: 12px;
  overflow: hidden;
  color: var(--ac-text);
  font-size: 14px;
}
.ac-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 16px;
  border-bottom: 1px solid var(--ac-border);
  background: #fafbfc;
  flex-wrap: wrap;
}
.ac-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
}
.ac-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #22c55e;
}
.ac-tools {
  display: flex;
  align-items: center;
  gap: 8px;
}
.ac-tone {
  width: 160px;
  height: 30px;
  padding: 0 10px;
  border: 1px solid var(--ac-border);
  border-radius: 6px;
  font-size: 13px;
  outline: none;
}
.ac-tone:focus {
  border-color: var(--ac-primary);
}
.ac-btn-text {
  height: 30px;
  padding: 0 12px;
  border: 1px solid var(--ac-border);
  border-radius: 6px;
  background: #fff;
  cursor: pointer;
  font-size: 13px;
}
.ac-btn-text:hover:not(:disabled) {
  color: var(--ac-primary);
  border-color: var(--ac-primary);
}
.ac-list {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 14px;
  min-height: 0;
}
.ac-row {
  display: flex;
}
.ac-row.user {
  justify-content: flex-end;
}
.ac-bubble {
  max-width: 82%;
  padding: 10px 14px;
  border-radius: 12px;
  line-height: 1.7;
  word-break: break-word;
  background: #f4f5f7;
}
.ac-row.user .ac-bubble {
  background: var(--ac-primary);
  color: #fff;
  border-bottom-right-radius: 4px;
}
.ac-row.assistant .ac-bubble {
  border-bottom-left-radius: 4px;
}
.ac-bubble.error {
  background: #fff1f0;
  color: #c0392b;
}
.ac-plain {
  white-space: pre-wrap;
}
.ac-file-tag {
  font-size: 12px;
  opacity: 0.9;
  margin-bottom: 4px;
}
.ac-md :deep(p) {
  margin: 0 0 6px;
}
.ac-md :deep(p:last-child) {
  margin-bottom: 0;
}
.ac-md :deep(ul),
.ac-md :deep(ol) {
  padding-left: 20px;
  margin: 4px 0;
}
.ac-md :deep(h1),
.ac-md :deep(h2),
.ac-md :deep(h3) {
  font-size: 15px;
  margin: 8px 0 6px;
}
.ac-md :deep(hr) {
  border: none;
  border-top: 1px dashed #d6d9e0;
  margin: 10px 0;
}
.ac-md :deep(blockquote) {
  margin: 6px 0;
  padding: 4px 10px;
  border-left: 3px solid #f0b429;
  background: #fffbea;
  color: #6b5a1e;
}
.ac-md :deep(code) {
  background: #e9ecf2;
  padding: 1px 4px;
  border-radius: 4px;
  font-size: 13px;
}
.ac-typing {
  display: inline-flex;
  gap: 4px;
  padding: 4px 0;
}
.ac-typing i {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #b5bac4;
  animation: ac-blink 1.2s infinite ease-in-out;
}
.ac-typing i:nth-child(2) {
  animation-delay: 0.2s;
}
.ac-typing i:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes ac-blink {
  0%,
  80%,
  100% {
    opacity: 0.3;
  }
  40% {
    opacity: 1;
  }
}
.ac-suggest {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.ac-chip {
  padding: 6px 12px;
  border: 1px solid #d5dcff;
  border-radius: 16px;
  background: var(--ac-primary-soft);
  color: var(--ac-primary);
  cursor: pointer;
  font-size: 13px;
}
.ac-chip:hover {
  background: #e1e7ff;
}
.ac-footer {
  border-top: 1px solid var(--ac-border);
  padding: 10px 12px;
  background: #fff;
}
.ac-pending {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 8px;
  padding: 4px 10px;
  border-radius: 6px;
  background: var(--ac-primary-soft);
  color: var(--ac-primary);
  font-size: 13px;
}
.ac-x {
  border: none;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 16px;
  line-height: 1;
}
.ac-inputbar {
  display: flex;
  align-items: flex-end;
  gap: 8px;
}
.ac-icon-btn {
  flex: none;
  width: 36px;
  height: 36px;
  border: 1px solid var(--ac-border);
  border-radius: 8px;
  background: #fff;
  color: #5c6370;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}
.ac-icon-btn:hover:not(:disabled) {
  color: var(--ac-primary);
  border-color: var(--ac-primary);
}
.ac-input {
  flex: 1;
  min-height: 36px;
  max-height: 140px;
  padding: 8px 10px;
  border: 1px solid var(--ac-border);
  border-radius: 8px;
  resize: vertical;
  font: inherit;
  outline: none;
}
.ac-input:focus {
  border-color: var(--ac-primary);
}
.ac-send {
  flex: none;
  height: 36px;
  padding: 0 18px;
  border: none;
  border-radius: 8px;
  background: var(--ac-primary);
  color: #fff;
  cursor: pointer;
}
.ac-send:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.ac-send.stop {
  background: #f56c6c;
}
button:disabled {
  cursor: not-allowed;
}

/* 输入框允许在窄屏被压缩，避免撑破容器 */
.ac-input {
  min-width: 0;
}

/* 手机端：收紧头部工具条、气泡与底部输入区 */
@media (max-width: 480px) {
  .ac-header {
    padding: 8px 12px;
    gap: 8px;
  }
  .ac-tone {
    width: 120px;
  }
  .ac-bubble {
    max-width: 92%;
  }
  .ac-footer {
    padding: 8px;
  }
  .ac-send {
    padding: 0 12px;
  }
}
</style>
