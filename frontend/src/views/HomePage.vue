<script setup>
// 知途 v0 首页：Hero + 行动召唤 + 页脚
</script>

<template>
  <div class="homepage">
    <!-- 导航栏 -->
    <NavBar />

    <main>
      <!-- 英雄区域 -->
      <HeroSection />

      <!-- v0 精简：以下智汇原有的介绍板块暂时隐藏，v1 按调研结果重新设计 -->
      <!-- <DashBoard /> <FeaturesSection /> <ModulesSection /> <ServicesSection /> <FAQSection /> -->

      <!-- 行动召唤区域 -->
      <CTASection />
    </main>

    <!-- 页脚 -->
    <AppFooter />
  </div>
</template>

<style scoped>
/* 字体 */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

/* 全局样式 */
.homepage {
  font-family: 'Inter', sans-serif;
  background-color: #f2f3f5;
  color: #1d2129;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
  overflow-x: hidden;
}

/* 滚动行为 */
html {
  scroll-behavior: smooth;
}

/* 焦点样式 */
button:focus,
a:focus {
  outline: 2px solid #165dff;
  outline-offset: 2px;
}

/* 选择文本颜色 */
::selection {
  background-color: rgba(22, 93, 255, 0.2);
  color: #165dff;
}

/* 无障碍 */
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

/* 打印样式 */
@media print {
  .navbar,
  .mobile-menu,
  .cta-section,
  .footer {
    display: none;
  }

  .hero-section,
  .features-section,
  .modules-section,
  .services-section,
  .cases-section,
  .faq-section {
    break-inside: avoid;
    page-break-inside: avoid;
  }
}

/* 高对比度模式支持 */
@media (prefers-contrast: high) {
  .pain-point-card,
  .service-card,
  .case-card,
  .demo-card {
    border: 2px solid #1d2129;
  }

  .primary-btn,
  .secondary-btn {
    border: 2px solid currentColor;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }

  .floating-card:hover,
  .pain-point-card:hover,
  .service-card:hover,
  .case-card:hover {
    transform: none;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .homepage {
    background-color: #1d2129;
    color: white;
  }

  .features-section,
  .services-section,
  .faq-section {
    background-color: #272e3b;
  }

  .modules-section,
  .cases-section {
    background-color: #1d2129;
  }

  .pain-point-card,
  .service-card,
  .case-card,
  .demo-card,
  .floating-card,
  .chart-container,
  .chat-demo,
  .faq-item {
    background-color: #272e3b;
    border-color: #4e5969;
  }

  .module-demo {
    background-color: #1d2129;
  }

  .section-description,
  .hero-description,
  .feature-content p,
  .case-content > p,
  .faq-answer p {
    color: #c9cdd4;
  }
}
</style>
