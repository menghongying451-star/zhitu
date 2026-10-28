<template>
  <footer class="footer">
    <div class="container">
      <div class="footer-content">
        <div class="footer-brand">
          <div href="#" class="brand-link">
            <span class="brand-title">智汇</span>
            <span class="brand-subtitle">产教融合平台</span>
          </div>
          <p class="team-info">北京邮电大学智汇团队</p>
        </div>
      </div>

      <div class="footer-bottom">
        <p>© 2025 智汇产教融合平台. 保留所有权利.</p>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.container {
  max-width: 1500px;
  margin: 0 auto;
  padding: 0 16px;
}

@media (min-width: 640px) {
  .container {
    padding: 0 24px;
  }
}

@media (min-width: 1024px) {
  .container {
    padding: 0 32px;
  }
}

.footer {
  background-color: #1d2129;
  color: white;
  padding: 20px 0 20px;
}

.footer-content {
  text-align: center;
  margin-bottom: 24px;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  text-decoration: none;
  margin-bottom: 12px;
}

.footer-brand .brand-title {
  color: white;
  font-size: 24px;
  font-weight: 700;
}

.footer-brand .brand-subtitle {
  color: #c9cdd4;
  font-size: 14px;
  margin-left: 8px;
}

.team-info {
  color: #c9cdd4;
  margin: 0;
  font-size: 14px;
}

.footer-bottom {
  border-top: 1px solid #272e3b;
  padding-top: 20px;
  text-align: center;
}

.footer-bottom p {
  color: #c9cdd4;
  font-size: 14px;
  margin: 0;
}
</style>
