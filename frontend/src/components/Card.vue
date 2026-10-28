<template>
  <div class="card">
    <div class="title">{{ title }}</div>
    <div class="value">{{ value }}</div>
  </div>
</template>

<script setup>
defineProps({
  title: String,
  value: [String, Number]
})
</script>

<style scoped>
.card {
  background: #f3f4f6; /* 浅灰背景 */
  border-radius: 8px;
  padding: 20px;
  flex: 1;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: box-shadow 0.3s ease;
}
.card:hover {
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.title {
  font-size: 14px;
  color: #475569; /* 深灰蓝色 */
  margin-bottom: 10px;
  font-weight: 600;
}

.value {
  font-size: 28px;
  font-weight: 700;
  color: #1e293b; /* 更深的深色文字 */
  letter-spacing: 0.5px;
}
</style>
