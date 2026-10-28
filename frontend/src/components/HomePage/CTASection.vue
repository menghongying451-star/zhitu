<script setup>
import { RouterLink } from 'vue-router'

import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import {
  faArrowRight,
  faUserPlus,
  faPlayCircle,
  faHandshake,
  faProjectDiagram,
  faGraduationCap
} from '@fortawesome/free-solid-svg-icons'
import { library } from '@fortawesome/fontawesome-svg-core'
library.add(faArrowRight, faUserPlus, faPlayCircle, faHandshake, faProjectDiagram, faGraduationCap)
</script>

<template>
  <section class="cta-section">
    <div class="container">
      <h2>加入知途，找到属于你的实践方向</h2>
      <p>
        实习、大创、竞赛、实验室课题，散落在各个群和网站里的机会，<br />知途帮你按兴趣和能力集中推荐。
      </p>

      <div class="cta-actions">
        <router-link :to="{ path: '/login', query: { mode: 'register' } }" class="cta-primary-btn">
          <font-awesome-icon :icon="['fas', 'user-plus']" />
          <span>立即注册</span>
        </router-link>
      </div>

      <!-- 原统计数据部分已注释
      <div class="cta-stats">
        <div class="cta-stat">
          <div class="cta-stat-number">500+</div>
          <p>企业已入驻</p>
        </div>
        <div class="cta-stat">
          <div class="cta-stat-number">1,000+</div>
          <p>真实项目</p>
        </div>
        <div class="cta-stat">
          <div class="cta-stat-number">12,500+</div>
          <p>学生在成长</p>
        </div>
      </div>
      -->

      <!-- 替换为核心价值主张 -->
      <div class="cta-features">
        <div class="cta-feature">
          <font-awesome-icon :icon="['fas', 'graduation-cap']" class="feature-icon" />
          <h3>方向测定</h3>
          <p>和智能体聊几句，理清自己的兴趣、能力<br />和适合的方向</p>
        </div>
        <div class="cta-feature">
          <font-awesome-icon :icon="['fas', 'handshake']" class="feature-icon" />
          <h3>机会推荐</h3>
          <p>从企业项目、实验室课题、大创和竞赛中<br />推荐适合你的机会</p>
        </div>
        <div class="cta-feature">
          <font-awesome-icon :icon="['fas', 'project-diagram']" class="feature-icon" />
          <h3>随问随答</h3>
          <p>对感兴趣的机会，可以直接追问要求、时间和所需能力</p>
        </div>
      </div>
    </div>
  </section>
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

/* 行动召唤 */
.cta-section {
  padding: 80px 0;
  background: linear-gradient(to right, #165dff, #ff7d00);
  color: white;
  text-align: center;
}

.cta-section h2 {
  font-size: clamp(1.75rem, 3vw, 2.5rem);
  font-weight: 700;
  margin-bottom: 24px;
}

.cta-section p {
  max-width: 512px;
  margin: 0 auto 40px;
  color: rgba(255, 255, 255, 0.8);
}

.cta-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 16px;
  margin-bottom: 64px;
}

.cta-primary-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background-color: white;
  color: #165dff;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.cta-primary-btn:hover {
  background-color: rgba(255, 255, 255, 0.9);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.cta-secondary-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 12px 32px;
  background-color: transparent;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.cta-secondary-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

/* 原统计数据样式已注释
.cta-stats {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 48px;
}

.cta-stat {
  text-align: center;
}

.cta-stat-number {
  font-size: 32px;
  font-weight: 700;
  margin-bottom: 8px;
}

.cta-stat p {
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}
*/

/* 新增核心价值主张样式 */
.cta-features {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 48px;
  max-width: 900px;
  margin: 0 auto;
}

.cta-feature {
  flex: 1;
  min-width: 250px;
  text-align: center;
}

.feature-icon {
  font-size: 2.5rem;
  margin-bottom: 16px;
  color: rgba(255, 255, 255, 0.9);
}

.cta-feature h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 12px;
  color: white;
}

.cta-feature p {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .cta-actions {
    flex-direction: column;
    align-items: center;
  }

  .cta-features {
    flex-direction: column;
    gap: 32px;
  }

  .cta-feature {
    min-width: auto;
  }
}
</style>
