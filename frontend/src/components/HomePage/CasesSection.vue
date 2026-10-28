<template>
  <section id="cases" class="cases-section">
    <div class="container">
      <div class="section-header">
        <span class="section-badge">成功案例</span>
        <h2 class="section-title">产教融合项目成果展示</h2>
        <p class="section-description">
          看看通过智汇平台实现的成功合作案例，了解产教融合如何创造价值
        </p>
      </div>

      <div class="cases-grid">
        <!-- 案例1 -->
        <div class="case-card">
          <div class="case-image">
            <img src="https://picsum.photos/id/160/600/400" alt="智能巡检系统项目" />
          </div>

          <div class="case-content">
            <div class="case-header">
              <img src="https://picsum.photos/id/180/100/100" alt="企业Logo" class="company-logo" />
              <div>
                <h4>智能巡检系统开发</h4>
                <p>与XX科技有限公司合作项目</p>
              </div>
            </div>

            <p>
              学生团队开发的智能巡检系统，基于计算机视觉技术，实现了设备状态自动识别与异常预警，提高了巡检效率30%以上。
            </p>

            <div class="case-footer">
              <div class="team-info">
                <div class="team-avatars">
                  <img
                    src="https://picsum.photos/id/237/100/100"
                    alt="学生头像"
                    class="team-avatar"
                  />
                  <img
                    src="https://picsum.photos/id/238/100/100"
                    alt="学生头像"
                    class="team-avatar"
                  />
                  <img
                    src="https://picsum.photos/id/239/100/100"
                    alt="学生头像"
                    class="team-avatar"
                  />
                </div>
                <span>5人团队</span>
              </div>

              <span class="case-tag primary">计算机视觉</span>
            </div>
          </div>
        </div>

        <!-- 案例2 -->
        <div class="case-card">
          <div class="case-image">
            <img src="https://picsum.photos/id/163/600/400" alt="社区服务平台" />
          </div>

          <div class="case-content">
            <div class="case-header">
              <img src="https://picsum.photos/id/181/100/100" alt="企业Logo" class="company-logo" />
              <div>
                <h4>智慧社区服务平台</h4>
                <p>与XX社区合作项目</p>
              </div>
            </div>

            <p>
              基于居民需求分析开发的智慧社区服务平台，集成了便民服务、社区活动、物业报修等功能，提升了社区管理效率和居民满意度。
            </p>

            <div class="case-footer">
              <div class="team-info">
                <div class="team-avatars">
                  <img
                    src="https://picsum.photos/id/240/100/100"
                    alt="学生头像"
                    class="team-avatar"
                  />
                  <img
                    src="https://picsum.photos/id/241/100/100"
                    alt="学生头像"
                    class="team-avatar"
                  />
                </div>
                <span>3人团队</span>
              </div>

              <span class="case-tag secondary">Web开发</span>
            </div>
          </div>
        </div>

        <!-- 案例3 -->
        <div class="case-card">
          <div class="case-image">
            <img src="https://picsum.photos/id/167/600/400" alt="智能推荐系统" />
          </div>

          <div class="case-content">
            <div class="case-header">
              <img src="https://picsum.photos/id/182/100/100" alt="企业Logo" class="company-logo" />
              <div>
                <h4>个性化推荐系统</h4>
                <p>与XX电商平台合作项目</p>
              </div>
            </div>

            <p>
              基于用户行为分析的个性化推荐系统，采用深度学习算法，提升了商品推荐准确率，用户点击率提高了25%。
            </p>

            <div class="case-footer">
              <div class="team-info">
                <div class="team-avatars">
                  <img
                    src="https://picsum.photos/id/242/100/100"
                    alt="学生头像"
                    class="team-avatar"
                  />
                  <img
                    src="https://picsum.photos/id/243/100/100"
                    alt="学生头像"
                    class="team-avatar"
                  />
                  <img
                    src="https://picsum.photos/id/244/100/100"
                    alt="学生头像"
                    class="team-avatar"
                  />
                  <img
                    src="https://picsum.photos/id/245/100/100"
                    alt="学生头像"
                    class="team-avatar"
                  />
                </div>
                <span>6人团队</span>
              </div>

              <span class="case-tag gray">机器学习</span>
            </div>
          </div>
        </div>
      </div>

      <div class="cases-action">
        <a href="#" class="secondary-btn">
          查看更多案例 <font-awesome-icon :icon="['fas', 'arrow-right']" />
        </a>
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

/* 成功案例 */
.cases-section {
  padding: 80px 0;
  background-color: #f7f8fa;
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

.cases-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 32px;
  margin-bottom: 48px;
}

@media (min-width: 768px) {
  .cases-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 1024px) {
  .cases-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}

.case-card {
  background-color: white;
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.case-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.case-image {
  height: 192px;
  overflow: hidden;
}

.case-image img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.case-card:hover .case-image img {
  transform: scale(1.1);
}

.case-content {
  padding: 24px;
}

.case-header {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.company-logo {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  margin-right: 12px;
}

.case-header h4 {
  font-weight: 600;
  margin-bottom: 2px;
}

.case-header p {
  color: #86909c;
  font-size: 14px;
  margin: 0;
}

.case-content > p {
  color: #86909c;
  font-size: 14px;
  margin-bottom: 16px;
}

.case-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.team-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.team-avatars {
  display: flex;
  margin-right: -8px;
}

.team-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 1px solid white;
  margin-right: -8px;
}

.team-info span {
  font-size: 12px;
  color: #86909c;
}

.case-tag {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 9999px;
}

.case-tag.primary {
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
}

.case-tag.secondary {
  background-color: rgba(255, 125, 0, 0.1);
  color: #ff7d00;
}

.case-tag.gray {
  background-color: #e5e6eb;
  color: #4e5969;
}

.cases-action {
  text-align: center;
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

.case-card {
  animation: fadeInUp 0.6s ease-out;
}
</style>
