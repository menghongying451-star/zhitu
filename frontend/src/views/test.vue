<script setup>
// 智能体调试页：三个 Python 版智能体（替代原 Dify）
import { ref } from 'vue'
import AgentChat from '@/components/AgentChat.vue'

const agent = ref('zhitu')
const pid = ref('')
</script>

<template>
  <div class="agent-test">
    <div class="bar">
      <select v-model="agent">
        <option value="zhitu">知途（学生方向测定与推荐）</option>
        <option value="wenshi">文识（项目问答，需要 pid）</option>
        <option value="tianbao">填宝（企业对话式发布）</option>
      </select>
      <input v-if="agent === 'wenshi'" v-model="pid" placeholder="需求 ID (pid)" />
    </div>
    <AgentChat
      :key="agent + pid"
      :agent="agent"
      :inputs="pid ? { pid: Number(pid) } : {}"
      :min-height="700"
    />
  </div>
</template>

<style scoped>
.agent-test {
  padding: 16px;
}
.bar {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}
.bar select,
.bar input {
  height: 32px;
  padding: 0 8px;
}
</style>
