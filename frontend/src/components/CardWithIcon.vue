<template>
  <div class="card">
    <div class="icon">{{ icon }}</div>
    <div class="content">
      <div class="title">{{ title }}</div>
      <div class="value">{{ value }}</div>
      <div class="desc">{{ desc }}</div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  title: String,
  value: [String, Number],
  icon: String,
  desc: String
})
</script>

<style scoped>
.card {
  background: linear-gradient(135deg, #4f46e5, #3b82f6);
  box-shadow: 0 4px 12px rgb(59 130 246 / 0.4);
  border-radius: 12px;
  color: white;
  display: flex;
  align-items: center;
  padding: 20px;
  cursor: default;
  transition: box-shadow 0.3s ease;
}
.card:hover {
  box-shadow: 0 6px 20px rgb(59 130 246 / 0.7);
}

.icon {
  font-size: 2.8rem;
  margin-right: 16px;
  user-select: none;
}

.content {
  flex: 1;
}

.title {
  font-weight: 600;
  font-size: 1rem;
  margin-bottom: 4px;
}

.value {
  font-size: 1.8rem;
  font-weight: 700;
  line-height: 1.2;
}

.desc {
  font-size: 0.85rem;
  opacity: 0.7;
  margin-top: 6px;
}
</style>
