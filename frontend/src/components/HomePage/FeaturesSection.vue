<template>
  <section id="features" class="features-section">
    <div class="container">
      <div class="section-header">
        <span class="section-badge">平台特色</span>
        <h2 class="section-title">破解产教融合痛点，打造创新实践环境</h2>
        <p class="section-description">
          智汇平台通过技术创新，解决传统产教融合中的核心问题，为企业和学生创造价值
        </p>
      </div>

      <div class="pain-points-grid">
        <div class="pain-point-card">
          <div class="card-icon">
            <font-awesome-icon :icon="['fas', 'puzzle-piece']" />
          </div>
          <h3>需求与能力不匹配</h3>
          <p>传统产教融合中，企业需求与学生能力之间存在明显鸿沟，导致合作效率低下。</p>
          <div class="card-action">
            <span>我们的解决方案</span>
            <font-awesome-icon :icon="['fas', 'arrow-right']" />
          </div>
        </div>

        <div class="pain-point-card">
          <div class="card-icon">
            <font-awesome-icon :icon="['fas', 'book']" />
          </div>
          <h3>理论与实践脱节</h3>
          <p>学生在学校所学知识与企业实际需求存在差距，缺乏真实项目实践经验。</p>
          <div class="card-action">
            <span>我们的解决方案</span>
            <font-awesome-icon :icon="['fas', 'arrow-right']" />
          </div>
        </div>

        <div class="pain-point-card">
          <div class="card-icon">
            <font-awesome-icon :icon="['fas', 'lightbulb']" />
          </div>
          <h3>创新能力不足</h3>
          <p>传统教育模式下，学生创新思维和解决复杂问题的能力培养不足。</p>
          <div class="card-action">
            <span>我们的解决方案</span>
            <font-awesome-icon :icon="['fas', 'arrow-right']" />
          </div>
        </div>
      </div>

      <!-- 解决方案 -->
      <div class="solution-section">
        <div class="solution-content">
          <div class="solution-text">
            <span class="section-badge">核心价值</span>
            <h2>打造"创中学"实践环境，培养创新型工程人才</h2>
            <p>
              智汇平台通过多模态融合供需对接和大模型智慧问答两大核心系统，构建真实产业场景，让学生在实践中学习，在创新中成长。
            </p>

            <div class="features-list">
              <div class="feature-item">
                <div class="feature-check">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>精准供需对接</h4>
                  <p>基于多模态画像技术，实现企业需求与学生能力的精准匹配</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>真实产业场景</h4>
                  <p>引入企业真实项目，让学生在实践中提升解决实际问题的能力</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>个性化成长路径</h4>
                  <p>基于大模型的智慧问答系统，为学生提供个性化学习建议和职业规划</p>
                </div>
              </div>
            </div>

            <a href="#modules" @click.prevent="scrollToSection('#modules')" class="primary-btn">
              了解核心模块
            </a>
          </div>

          <div class="solution-image">
            <div class="image-decoration"></div>
            <div class="solution-main-image">
              <img src="/picture/48-800x600.jpg" alt="学生在平台上实践项目" />
              <div class="image-overlay">
                <h3>真实项目实践</h3>
                <p>学生在智汇平台上参与企业真实项目，积累实践经验</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const scrollToSection = (sectionId) => {
  const element = document.querySelector(sectionId)
  if (element) {
    const offsetTop = element.offsetTop - 80
    window.scrollTo({
      top: offsetTop,
      behavior: 'smooth'
    })
  }
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

/* 功能特色区域 */
.features-section {
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

.pain-points-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
  margin-bottom: 64px;
}

@media (min-width: 768px) {
  .pain-points-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .pain-points-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.pain-point-card {
  background-color: #f7f8fa;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.3s ease;
}

.pain-point-card:hover {
  background-color: white;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.pain-point-card .card-icon {
  width: 56px;
  height: 56px;
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-bottom: 20px;
}

.pain-point-card h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
}

.pain-point-card p {
  color: #86909c;
  margin-bottom: 16px;
}

.card-action {
  color: #165dff;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
}

/* 解决方案 */
.solution-section {
  background: linear-gradient(to right, rgba(22, 93, 255, 0.05), rgba(255, 125, 0, 0.05));
  border-radius: 16px;
  padding: 32px;
}

@media (min-width: 768px) {
  .solution-section {
    padding: 48px;
  }
}

.solution-content {
  display: grid;
  grid-template-columns: 1fr;
  gap: 48px;
  align-items: center;
}

@media (min-width: 1024px) {
  .solution-content {
    grid-template-columns: 1fr 1fr;
  }
}

.solution-text h2 {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 700;
  margin-bottom: 16px;
}

.solution-text p {
  color: #86909c;
  margin-bottom: 24px;
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
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  margin-top: 4px;
  flex-shrink: 0;
}

.feature-content h4 {
  font-weight: 600;
  margin-bottom: 4px;
}

.feature-content p {
  color: #86909c;
  font-size: 14px;
}

.solution-image {
  position: relative;
}

.solution-image .image-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(45deg, rgba(22, 93, 255, 0.1), rgba(255, 125, 0, 0.1));
  border-radius: 16px;
  transform: rotate(2deg);
}

.solution-main-image {
  position: relative;
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  overflow: hidden;
}

.solution-main-image img {
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

/* 响应式设计 */
@media (max-width: 768px) {
  .solution-content {
    text-align: center;
  }
}

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

.section-header,
.pain-point-card {
  animation: fadeInUp 0.6s ease-out;
}
</style>
