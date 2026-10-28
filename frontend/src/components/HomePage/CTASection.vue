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
      <h2>加入智汇平台，开启产教融合新篇章</h2>
      <p>
        无论您是学生、企业还是社区，智汇平台都能为您提供量身定制的<br />产教融合解决方案，共同培养创新型工程人才。
      </p>

      <div class="cta-actions">
        <router-link :to="{ path: '/login', query: { mode: 'register' } }" class="cta-primary-btn">
          <font-awesome-icon :icon="['fas', 'user-plus']" />
          <span>立即注册</span>
        </router-link>
        <a href="/help/quick-start" class="cta-secondary-btn">
          <font-awesome-icon :icon="['fas', 'play-circle']" />
          <span>观看演示</span>
        </a>
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
          <h3>人才培养</h3>
          <p>培养符合企业需求的创新型工程技术与<br />管理人才</p>
        </div>
        <div class="cta-feature">
          <font-awesome-icon :icon="['fas', 'handshake']" class="feature-icon" />
          <h3>校企合作</h3>
          <p>搭建企业与院校之间的桥梁，实现深度<br />产教融合</p>
        </div>
        <div class="cta-feature">
          <font-awesome-icon :icon="['fas', 'project-diagram']" class="feature-icon" />
          <h3>实战项目</h3>
          <p>提供真实企业项目，让学生在实践中提升专业技能</p>
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
