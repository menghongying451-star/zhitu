<template>
  <section class="hero-section">
    <div class="hero-bg"></div>
    <div class="hero-decorations">
      <div class="decoration-1"></div>
      <div class="decoration-2"></div>
    </div>

    <div class="container">
      <div class="hero-content">
        <div class="hero-text">
          <div class="hero-badge">
            <span>基于大模型的产教融合平台</span>
          </div>
          <h1 class="hero-title">
            连接产业需求<br />
            <span class="gradient-text">培育创新人才</span>
          </h1>
          <p class="hero-description">
            智汇平台依托大模型技术，构建多模态融合供需对接系统与智慧问答系统，打破产教壁垒，实现精准人才培养。
          </p>

          <div class="hero-actions">
            <a @click="handleIntroClick" class="primary-btn">
              <span>了解平台</span>
              <font-awesome-icon :icon="['fas', 'arrow-right']" />
            </a>
            <a @click="handleDemoClick" class="secondary-btn">
              <font-awesome-icon :icon="['fas', 'play-circle']" />
              <span>观看演示</span>
            </a>
          </div>

          <!-- 原始统计数据已注释，改为功能亮点展示 -->
          <!--
          <div class="hero-stats">
            <div class="user-avatars">
              <img src="https://picsum.photos/id/237/100/100" alt="用户头像" class="avatar" />
              <img src="https://picsum.photos/id/238/100/100" alt="用户头像" class="avatar" />
              <img src="https://picsum.photos/id/239/100/100" alt="用户头像" class="avatar" />
              <div class="avatar-count">500+</div>
            </div>
            <div class="stats-text">
              <span><strong>500+</strong> 企业已入驻</span><br />
              <span><strong>1000+</strong> 真实项目正在对接</span>
            </div>
          </div>
          -->
        </div>

        <div class="hero-image">
          <div class="image-decoration"></div>
          <div class="main-image">
            <img src="/picture/3-800x600.jpg" alt="智汇平台界面展示" />
            <div class="image-overlay">
              <h3>多模态供需对接系统</h3>
              <p>基于大模型的智能匹配技术，实现企业需求与学生能力的精准对接</p>
            </div>
          </div>

          <!-- 原始数据浮动卡片已注释，改为功能展示卡片 -->
          <!--
          <div class="floating-card floating-card-1">
            <div class="card-icon primary">
              <font-awesome-icon :icon="['fas', 'line-chart']" />
            </div>
            <div class="card-content">
              <p class="card-label">匹配成功率</p>
              <p class="card-value primary">92.7%</p>
            </div>
          </div>

          <div class="floating-card floating-card-2">
            <div class="card-icon secondary">
              <font-awesome-icon :icon="['fas', 'users']" />
            </div>
            <div class="card-content">
              <p class="card-label">活跃用户</p>
              <p class="card-value secondary">12,500+</p>
            </div>
          </div>
          -->

          <div class="floating-card floating-card-1">
            <div class="card-icon primary">
              <font-awesome-icon :icon="['fas', 'magic-wand-sparkles']" />
            </div>
            <div class="card-content">
              <p class="card-label">智能推荐</p>
              <p class="card-value primary">精准匹配</p>
            </div>
          </div>

          <div class="floating-card floating-card-2">
            <div class="card-icon secondary">
              <font-awesome-icon :icon="['fas', 'handshake']" />
            </div>
            <div class="card-content">
              <p class="card-label">产教合作</p>
              <p class="card-value secondary">深度融合</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 信任标志部分注释，改为平台理念展示 -->
      <!--
      <div class="trust-logos">
        <p class="trust-title">受到行业领先企业的信任</p>
        <div class="logos-grid">
          <img
            v-for="i in 6"
            :key="i"
            :src="`https://picsum.photos/id/${179 + i}/200/80`"
            alt="企业Logo"
            class="logo"
          />
        </div>
      </div>
      -->

      <!-- 替代方案：平台优势展示 -->
      <div class="platform-advantages">
        <p class="advantages-title">构建未来教育新生态</p>
        <div class="advantages-grid">
          <div class="advantage-item">
            <font-awesome-icon :icon="['fas', 'microchip']" class="advantage-icon" />
            <div class="text-content">
              <h4>大模型驱动</h4>
              <p>前沿AI技术支撑</p>
            </div>
          </div>
          <div class="advantage-item">
            <font-awesome-icon :icon="['fas', 'sitemap']" class="advantage-icon" />
            <div class="text-content">
              <h4>多模态融合</h4>
              <p>全方位信息整合</p>
            </div>
          </div>
          <div class="advantage-item">
            <font-awesome-icon :icon="['fas', 'lightbulb']" class="advantage-icon" />
            <div class="text-content">
              <h4>创新驱动</h4>
              <p>突破传统教育模式</p>
            </div>
          </div>
          <div class="advantage-item">
            <font-awesome-icon :icon="['fas', 'bullseye']" class="advantage-icon" />
            <div class="text-content">
              <h4>精准对接</h4>
              <p>供需智能匹配</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
// Font Awesome 图标按需导入
import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faArrowRight,
  faPlayCircle,
  faMagicWandSparkles,
  faHandshake,
  faMicrochip,
  faSitemap,
  faLightbulb,
  faBullseye
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

// 将图标添加到库中
library.add(
  faArrowRight,
  faPlayCircle,
  faMagicWandSparkles,
  faHandshake,
  faMicrochip,
  faSitemap,
  faLightbulb,
  faBullseye
)

import { useRouter } from 'vue-router'
const router = useRouter()

const handleIntroClick = (event) => {
  event.preventDefault()
  router.push('/help/introduction')
}

const handleDemoClick = (event) => {
  event.preventDefault()
  router.push('/help/quick-start')
}
</script>

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

/* 英雄区域 */
.hero-section {
  position: relative;
  min-height: 100vh;
  display: flex;
  align-items: center;
  overflow: hidden;
  padding: 32px 0;
}

@media (min-width: 768px) {
  .hero-section {
    padding: 48px 0;
  }
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(22, 93, 255, 0.05), rgba(22, 93, 255, 0.1));
  pointer-events: none; /* 添加这一行，使其不接收任何鼠标事件 */
  z-index: 0; /* 确保背景在最底层 */
}

.hero-bg::after {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100%;
  height: 100%;
  background-image: url('/picture/1-1920x1080.jpg');
  background-size: cover;
  background-position: center;
  background-repeat: no-repeat;
  opacity: 0.05;
  z-index: 2;
}

.hero-decorations {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: -1;
}

.decoration-1 {
  position: absolute;
  top: 25%;
  right: -40px;
  width: 256px;
  height: 256px;
  background-color: rgba(22, 93, 255, 0.1);
  border-radius: 50%;
  filter: blur(48px);
}

.decoration-2 {
  position: absolute;
  bottom: 33.333%;
  left: -80px;
  width: 384px;
  height: 384px;
  background-color: rgba(255, 125, 0, 0.1);
  border-radius: 50%;
  filter: blur(48px);
}

.hero-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 48px;
  align-items: center;
  position: relative;
  z-index: 2; /* 确保内容在背景之上 */
}

@media (min-width: 1024px) {
  .hero-content {
    grid-template-columns: 1fr 1fr;
  }
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding-top: 60px; /* 移动端默认上边距 */
}

@media (min-width: 768px) {
  .hero-text {
    padding-top: 40px;
  }
}

.hero-badge {
  display: inline-block;
  padding: 4px 16px;
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;
  width: fit-content;
}

.hero-title {
  font-size: clamp(2.5rem, 5vw, 4rem);
  font-weight: 700;
  line-height: 1.1;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.gradient-text {
  background: linear-gradient(to right, #165dff, #ff7d00);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-description {
  font-size: clamp(1rem, 2vw, 1.25rem);
  color: #86909c;
  max-width: 600px;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background-color: #165dff;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.primary-btn:hover {
  background-color: rgba(22, 93, 255, 0.9);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.secondary-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background-color: white;
  color: #165dff;
  border: 1px solid rgba(22, 93, 255, 0.3);
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.secondary-btn:hover {
  background-color: rgba(22, 93, 255, 0.05);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 原始统计数据样式已注释 - 替换为特色标签 */
/*
.hero-stats {
  display: flex;
  align-items: center;
  gap: 24px;
}

.user-avatars {
  display: flex;
  align-items: center;
  gap: -8px;
}

.avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid white;
  margin-right: -8px;
}

.avatar-count {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: 2px solid white;
  background-color: rgba(22, 93, 255, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #165dff;
  font-size: 12px;
  font-weight: 500;
}

.stats-text {
  font-size: 14px;
  color: #86909c;
}

.stats-text strong {
  color: #1d2129;
}
*/

/* 英雄图片 */
.hero-image {
  position: relative;
  display: none;
}

@media (min-width: 1024px) {
  .hero-image {
    display: block;
    margin-top: 80px;
  }
}

.image-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(22, 93, 255, 0.2), rgba(255, 125, 0, 0.2));
  border-radius: 16px;
  transform: rotate(3deg);
}

.main-image {
  position: relative;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.main-image img {
  width: 100%;
  height: auto;
  display: block;
}

.image-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 24px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.7), transparent);
  color: white;
}

.image-overlay h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 4px;
}

.image-overlay p {
  font-size: 14px;
  opacity: 0.8;
}

.floating-card {
  position: absolute;
  background-color: white;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  gap: 12px;
  transition: all 0.3s ease;
}

.floating-card:hover {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.floating-card-1 {
  bottom: -24px;
  left: -40px;
}

.floating-card-2 {
  top: -24px;
  right: -40px;
}

.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
}

.card-icon.primary {
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
}

.card-icon.secondary {
  background-color: rgba(255, 125, 0, 0.1);
  color: #ff7d00;
}

.card-label {
  font-size: 14px;
  font-weight: 500;
  margin: 0;
}

.card-value {
  font-size: 18px;
  font-weight: 700;
  margin: 0;
}

.card-value.primary {
  color: #165dff;
}

.card-value.secondary {
  color: #ff7d00;
}

/* 原始信任标志样式已注释 - 替换为平台优势展示 */
/*
.trust-logos {
  margin-top: 96px;
}

.trust-title {
  text-align: center;
  color: #c9cdd4;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 24px;
}

.logos-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
  align-items: center;
  opacity: 0.6;
}

@media (min-width: 768px) {
  .logos-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

@media (min-width: 1024px) {
  .logos-grid {
    grid-template-columns: repeat(6, 1fr);
  }
}

.logo {
  height: 32px;
  width: auto;
  filter: grayscale(100%);
  transition: filter 0.3s ease;
}

.logo:hover {
  filter: grayscale(0%);
}
*/

/* 新增：平台优势展示样式 */
.platform-advantages {
  margin-top: 48px;
}

@media (min-width: 768px) {
  .platform-advantages {
    margin-top: 96px;
  }
}

.advantages-title {
  text-align: center;
  color: #4e5969c7;
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 28px;
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 32px;
}

@media (min-width: 768px) {
  .advantages-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.advantage-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 24px 16px;
  border-radius: 12px;
  background-color: rgba(255, 255, 255, 0.5);
  border: 1px solid rgba(22, 93, 255, 0.1);
  transition: all 0.3s ease;
}

.advantage-item:hover {
  background-color: rgba(22, 93, 255, 0.05);
  border-color: rgba(22, 93, 255, 0.2);
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(22, 93, 255, 0.1);
}

.advantage-icon {
  font-size: 32px;
  color: #165dff;
  flex-shrink: 0;
}

.advantage-item .text-content {
  text-align: left;
}

.advantage-item h4 {
  font-size: 16px;
  font-weight: 600;
  color: #1d2129;
  margin: 0 0 4px;
}

.advantage-item p {
  font-size: 14px;
  color: #86909c;
  margin: 0;
}
</style>
