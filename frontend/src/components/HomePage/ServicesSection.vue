<script setup>
import {
  faGraduationCap,
  faCheck,
  faArrowRight,
  faBuilding,
  faUsers,
  faCity
} from '@fortawesome/free-solid-svg-icons'
import { library } from '@fortawesome/fontawesome-svg-core'

// 注册图标到库中
library.add(faGraduationCap, faCheck, faArrowRight, faBuilding, faUsers, faCity)
</script>

<template>
  <section id="services" class="services-section">
    <div class="container">
      <div class="section-header">
        <span class="section-badge">服务对象</span>
        <h2 class="section-title">整合多方优势资源，构建协同育人体系</h2>
        <p class="section-description">
          智汇平台连接校区、园区、社区与城区，构建四维产教融合生态系统，实现多方共赢
        </p>
      </div>

      <div class="services-grid">
        <!-- 服务对象1：学生（校区） -->
        <div class="service-card">
          <div class="service-header gray">
            <div class="service-bg-icon">
              <font-awesome-icon :icon="['fas', 'graduation-cap']" />
            </div>
            <div class="service-title">
              <h3>学生（校区）</h3>
              <p>实践成长，提升能力，规划职业</p>
            </div>
          </div>

          <div class="service-content">
            <div class="features-list">
              <div class="feature-item">
                <div class="feature-check gray">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>参与真实项目</h4>
                  <p>获取企业真实项目实践机会，积累实战经验</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check gray">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>能力评估与提升</h4>
                  <p>通过平台评估，了解自身能力短板，获取针对性提升建议</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check gray">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>职业规划指导</h4>
                  <p>基于产业需求分析，获取个性化职业发展建议和学习路径</p>
                </div>
              </div>
            </div>

            <router-link
              :to="{ path: '/login', query: { mode: 'register', userType: 'student' } }"
              class="service-btn gray"
            >
              学生注册 <font-awesome-icon :icon="['fas', 'arrow-right']" />
            </router-link>
          </div>
        </div>

        <!-- 服务对象2：企业（园区） -->
        <div class="service-card">
          <div class="service-header primary">
            <div class="service-bg-icon">
              <font-awesome-icon :icon="['fas', 'building']" />
            </div>
            <div class="service-title">
              <h3>企业（园区）</h3>
              <p>发布需求，获取人才，推动创新</p>
            </div>
          </div>

          <div class="service-content">
            <div class="features-list">
              <div class="feature-item">
                <div class="feature-check primary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>发布真实需求</h4>
                  <p>将企业真实项目需求发布到平台，获取匹配的学生团队</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check primary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>精准人才筛选</h4>
                  <p>基于学生能力画像，快速找到符合需求的潜在人才</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check primary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>技术创新支持</h4>
                  <p>获取平台智慧问答系统支持，解决技术难题</p>
                </div>
              </div>
            </div>

            <router-link
              :to="{ path: '/login', query: { mode: 'register', userType: 'organization' } }"
              class="service-btn primary"
            >
              企业入驻 <font-awesome-icon :icon="['fas', 'arrow-right']" />
            </router-link>
          </div>
        </div>

        <!-- 服务对象3：社区 -->
        <div class="service-card">
          <div class="service-header secondary">
            <div class="service-bg-icon">
              <font-awesome-icon :icon="['fas', 'users']" />
            </div>
            <div class="service-title">
              <h3>社区</h3>
              <p>参与实践，提供场景，促进发展</p>
            </div>
          </div>

          <div class="service-content">
            <div class="features-list">
              <div class="feature-item">
                <div class="feature-check secondary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>提供实践场景</h4>
                  <p>将社区实际需求转化为实践项目，培养实用型人才</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check secondary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>促进区域发展</h4>
                  <p>通过产教融合项目，提升社区创新能力和经济发展</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check secondary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>获取技术支持</h4>
                  <p>借助平台资源和学生团队，解决社区发展中的技术问题</p>
                </div>
              </div>
            </div>

            <router-link
              :to="{ path: '/login', query: { mode: 'register', userType: 'organization' } }"
              class="service-btn secondary"
            >
              社区合作 <font-awesome-icon :icon="['fas', 'arrow-right']" />
            </router-link>
          </div>
        </div>

        <!-- 服务对象4：城区 -->
        <div class="service-card">
          <div class="service-header tertiary">
            <div class="service-bg-icon">
              <font-awesome-icon :icon="['fas', 'city']" />
            </div>
            <div class="service-title">
              <h3>城区</h3>
              <p>统筹规划，政策支持，协调发展</p>
            </div>
          </div>

          <div class="service-content">
            <div class="features-list">
              <div class="feature-item">
                <div class="feature-check tertiary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>制定发展规划</h4>
                  <p>基于平台数据分析，制定区域产教融合发展战略规划</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check tertiary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>优化资源配置</h4>
                  <p>统筹整合教育、产业、科技等各类资源，提升配置效率</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check tertiary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>推动政策创新</h4>
                  <p>获取决策支持数据，推动产教融合相关政策制度创新</p>
                </div>
              </div>
            </div>

            <router-link
              :to="{ path: '/login', query: { mode: 'register', userType: 'organization' } }"
              class="service-btn tertiary"
            >
              城区入驻 <font-awesome-icon :icon="['fas', 'arrow-right']" />
            </router-link>
          </div>
        </div>
      </div>

      <!-- 数据统计 -->
      <!-- <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-number">500+</div>
          <p>入驻企业</p>
        </div>

        <div class="stat-card">
          <div class="stat-number">12,500+</div>
          <p>活跃学生</p>
        </div>

        <div class="stat-card">
          <div class="stat-number">1,000+</div>
          <p>真实项目</p>
        </div>

        <div class="stat-card">
          <div class="stat-number">92.7%</div>
          <p>需求匹配成功率</p>
        </div>
      </div> -->
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

/* 服务对象 */
.services-section {
  padding: 80px 0;
  background-color: white;
}

.section-header {
  text-align: center;
  max-width: 768px;
  margin: 0 auto 64px;
}

.section-badge {
  display: inline-block;
  padding: 4px 16px;
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
  border-radius: 9999px;
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 16px;
}

.section-title {
  font-size: clamp(1.75rem, 3vw, 2.5rem);
  font-weight: 700;
  margin-bottom: 16px;
}

.section-description {
  color: #86909c;
}

.services-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
  margin-bottom: 80px;
}

@media (min-width: 768px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .services-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1200px) {
  .services-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.service-card {
  background-color: #f7f8fa;
  border-radius: 16px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.service-card:hover {
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}

.service-header {
  height: 192px;
  position: relative;
  display: flex;
  align-items: flex-end;
  padding: 24px;
}

.service-header.primary {
  background-color: rgba(22, 93, 255, 0.1);
}

.service-header.secondary {
  background-color: rgba(255, 125, 0, 0.1);
}

.service-header.gray {
  background-color: #e5e6eb;
}

.service-header.tertiary {
  background-color: rgba(0, 180, 42, 0.1);
}

.service-bg-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 96px;
  opacity: 0.2;
}

.service-bg-icon i {
  color: #165dff;
}

.service-header.secondary .service-bg-icon i {
  color: #ff7d00;
}

.service-header.gray .service-bg-icon i {
  color: #86909c;
}

.service-header.tertiary .service-bg-icon i {
  color: #00b42a;
}

.service-title {
  position: relative;
  z-index: 1;
}

.service-title h3 {
  font-size: 20px;
  font-weight: 700;
  color: #1d2129;
  margin-bottom: 4px;
}

.service-title p {
  color: #86909c;
  font-size: 14px;
}

.service-content {
  padding: 24px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.feature-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.feature-check {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-top: 4px;
  flex-shrink: 0;
}

.feature-check.primary {
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
}

.feature-check.secondary {
  background-color: rgba(255, 125, 0, 0.1);
  color: #ff7d00;
}

.feature-check.gray {
  background-color: #e5e6eb;
  color: #86909c;
}

.feature-check.tertiary {
  background-color: rgba(0, 180, 42, 0.1);
  color: #00b42a;
}

.feature-content h4 {
  font-weight: 600;
  margin-bottom: 4px;
}

.feature-content p {
  color: #86909c;
  font-size: 14px;
}

.service-btn {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 8px 16px;
  border: 1px solid;
  border-radius: 8px;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  margin-top: 24px;
  transition: all 0.2s ease;
}

.service-btn.primary {
  border-color: #165dff;
  color: #165dff;
}

.service-btn.primary:hover {
  background-color: #165dff;
  color: white;
}

.service-btn.secondary {
  border-color: #ff7d00;
  color: #ff7d00;
}

.service-btn.secondary:hover {
  background-color: #ff7d00;
  color: white;
}

.service-btn.gray {
  border-color: #86909c;
  color: #86909c;
}

.service-btn.gray:hover {
  background-color: #86909c;
  color: white;
}

.service-btn.tertiary {
  border-color: #00b42a;
  color: #00b42a;
}

.service-btn.tertiary:hover {
  background-color: #00b42a;
  color: white;
}

/* 统计数据 */
/* .stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
}

@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .stats-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.stat-card {
  background-color: #f7f8fa;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
}

.stat-number {
  font-size: 32px;
  font-weight: 700;
  color: #165dff;
  margin-bottom: 8px;
}

.stat-card p {
  color: #86909c;
  margin: 0;
} */

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.service-card {
  animation: fadeInUp 0.6s ease-out;
}
</style>
