<template>
  <section id="modules" class="modules-section">
    <div class="container">
      <div class="section-header">
        <span class="section-badge">核心系统</span>
        <h2 class="section-title">独创两大核心模块，打造产教融合新生态</h2>
        <p class="section-description">
          智汇平台通过多模态融合供需对接和大模型智慧问答两大核心系统，解决产教融合中拔尖人才培养的核心问题
        </p>
      </div>

      <!-- 模块1：多模态融合供需对接平台 -->
      <div class="module-card">
        <div class="module-content">
          <div class="module-text">
            <div class="module-header">
              <div class="module-badge">核心模块1</div>
              <div class="module-title-row">
                <div class="module-icon primary">
                  <font-awesome-icon :icon="['fas', 'exchange-alt']" />
                </div>
                <h3>多模态融合供需对接平台</h3>
              </div>
            </div>

            <p>基于多模态画像生成技术，构建企业需求画像与学生能力画像，实现精准匹配与对接。</p>

            <div class="features-list">
              <div class="feature-item">
                <div class="feature-check">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>多模态资源处理</h4>
                  <p>支持文本、图片、视频、代码包等多种格式的资源信息处理</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>智能画像生成</h4>
                  <p>自动生成企业需求画像和学生能力画像，包含多维度特征</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>精准匹配推荐</h4>
                  <p>基于画像相似度计算，提供精准的项目与人才匹配推荐</p>
                </div>
              </div>
            </div>

            <a href="#" class="secondary-btn">
              了解更多 <font-awesome-icon :icon="['fas', 'arrow-right']" />
            </a>
          </div>

          <div class="module-demo">
            <div class="demo-cards">
              <div class="demo-card">
                <div class="demo-card-icon">
                  <font-awesome-icon :icon="['fas', 'file-alt']" />
                </div>
                <h4>资源画像生成</h4>
                <p>对企业发布的多模态资源信息进行处理，自动生成结构化的资源画像。</p>
              </div>

              <div class="demo-card">
                <div class="demo-card-icon">
                  <font-awesome-icon :icon="['fas', 'briefcase']" />
                </div>
                <h4>企业需求画像</h4>
                <p>
                  基于企业需求内容，生成包含所需人数、开发时间、能力要求等多维度信息的需求画像。
                </p>
              </div>

              <div class="demo-card">
                <div class="demo-card-icon">
                  <font-awesome-icon :icon="['fas', 'user-circle']" />
                </div>
                <h4>学生能力画像</h4>
                <p>通过启发式问答和能力测试，生成学生兴趣画像与技能画像，辅助匹配合适项目。</p>
              </div>

              <div class="demo-card">
                <div class="demo-card-icon">
                  <font-awesome-icon :icon="['fas', 'line-chart']" />
                </div>
                <h4>技术可行性评估</h4>
                <p>对企业需求进行技术分析和评估，提供可行性报告和技术路线建议。</p>
              </div>
            </div>

            <!-- 原数据可视化部分已注释
            <div class="chart-container">
              <h4>供需匹配效果</h4>
              <div class="chart-wrapper">
                <canvas id="matchChart"></canvas>
              </div>
            </div>
            -->

            <!-- 替换为平台优势展示 -->
            <div class="advantages-container">
              <h4>平台核心优势</h4>
              <div class="advantages-grid">
                <div class="advantage-item">
                  <div class="advantage-number">95%</div>
                  <p>匹配准确率目标</p>
                </div>
                <div class="advantage-item">
                  <div class="advantage-number">10+</div>
                  <p>支持文件格式</p>
                </div>
                <div class="advantage-item">
                  <div class="advantage-number">24/7</div>
                  <p>智能服务时间</p>
                </div>
                <div class="advantage-item">
                  <div class="advantage-number">100+</div>
                  <p>技能维度分析</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- 模块2：大模型提示词智慧问答系统 -->
      <div class="module-card reverse">
        <div class="module-content">
          <div class="module-demo">
            <div class="demo-cards">
              <div class="demo-card">
                <div class="demo-card-icon secondary">
                  <font-awesome-icon :icon="['fas', 'search']" />
                </div>
                <h4>产业需求分析</h4>
                <p>构建产业需求知识库，训练专属模型，为学生解析产业真实需求及解决思路。</p>
              </div>

              <div class="demo-card">
                <div class="demo-card-icon secondary">
                  <font-awesome-icon :icon="['fas', 'lightbulb']" />
                </div>
                <h4>项目推荐</h4>
                <p>结合学生兴趣、能力及历史记录，推荐合适的真实项目，提供实践机会。</p>
              </div>

              <div class="demo-card">
                <div class="demo-card-icon secondary">
                  <font-awesome-icon :icon="['fas', 'map-signs']" />
                </div>
                <h4>学习路线规划</h4>
                <p>根据学生当前水平和目标岗位，生成个性化学习方案和成长路径。</p>
              </div>

              <div class="demo-card">
                <div class="demo-card-icon secondary">
                  <font-awesome-icon :icon="['fas', 'comments']" />
                </div>
                <h4>智能问答</h4>
                <p>基于大模型的智能问答系统，实时解答学生在学习和实践中的疑问。</p>
              </div>
            </div>

            <!-- 系统演示 -->
            <div class="chat-demo">
              <h4>智慧问答系统演示</h4>
              <div class="chat-container">
                <div class="chat-message bot">
                  <div class="chat-avatar">
                    <font-awesome-icon :icon="['fas', 'robot']" />
                  </div>
                  <div class="chat-bubble">
                    <p>你好！我是智汇平台的智慧助手，有什么可以帮助你的吗？</p>
                  </div>
                </div>

                <div class="chat-message user">
                  <div class="chat-bubble">
                    <p>我是计算机专业大二学生，想提升人工智能方面的能力，应该从哪些项目开始？</p>
                  </div>
                  <div class="chat-avatar">
                    <font-awesome-icon :icon="['fas', 'user']" />
                  </div>
                </div>

                <div class="chat-message bot">
                  <div class="chat-avatar">
                    <font-awesome-icon :icon="['fas', 'robot']" />
                  </div>
                  <div class="chat-bubble">
                    <p>根据你的情况，我推荐你从以下几个项目入手：</p>
                    <ul>
                      <li>基于深度学习的图像分类项目</li>
                      <li>简单的自然语言处理任务，如情感分析</li>
                      <li>使用强化学习训练一个简单的游戏AI</li>
                    </ul>
                    <p>
                      这些项目可以帮助你建立AI基础，并且在我们平台上都有对应的实践案例和指导资源。需要我为你详细介绍其中某个项目吗？
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="module-text">
            <div class="module-header">
              <div class="module-badge">核心模块2</div>
              <div class="module-title-row">
                <div class="module-icon secondary">
                  <font-awesome-icon :icon="['fas', 'question-circle']" />
                </div>
                <h3>大模型提示词智慧问答系统</h3>
              </div>
            </div>

            <p>
              基于大模型技术，构建产业需求分析与个性化学习推荐系统，为学生提供全方位的学习支持。
            </p>

            <div class="features-list">
              <div class="feature-item">
                <div class="feature-check secondary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>产业知识图谱</h4>
                  <p>构建完整的产业知识体系，涵盖技术栈、岗位需求、行业趋势等</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check secondary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>个性化推荐</h4>
                  <p>基于学生画像，提供个性化的项目推荐和学习路径规划</p>
                </div>
              </div>

              <div class="feature-item">
                <div class="feature-check secondary">
                  <font-awesome-icon :icon="['fas', 'check']" />
                </div>
                <div class="feature-content">
                  <h4>实时答疑</h4>
                  <p>基于大模型的智能问答系统，实时解答学生在学习过程中的疑问</p>
                </div>
              </div>
            </div>

            <a href="#" class="secondary-btn orange">
              体验智慧问答 <font-awesome-icon :icon="['fas', 'arrow-right']" />
            </a>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
// 原Chart.js相关导入已注释
/*
import { onMounted, onUnmounted, nextTick } from 'vue'
import {
  Chart,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'

// 注册Chart.js组件
Chart.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  LineController,
  Title,
  Tooltip,
  Legend,
  Filler
)

let matchChart = null

const initChart = () => {
  const ctx = document.getElementById('matchChart')
  if (ctx) {
    matchChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: ['1月', '2月', '3月', '4月', '5月', '6月'],
        datasets: [
          {
            label: '项目匹配数量',
            data: [65, 78, 90, 105, 125, 140],
            borderColor: '#165DFF',
            backgroundColor: 'rgba(22, 93, 255, 0.1)',
            tension: 0.4,
            fill: true
          },
          {
            label: '人才匹配数量',
            data: [85, 95, 110, 130, 150, 170],
            borderColor: '#FF7D00',
            backgroundColor: 'rgba(255, 125, 0, 0.1)',
            tension: 0.4,
            fill: true
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top'
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      }
    })
  }
}

onMounted(async () => {
  // 等待DOM更新后初始化图表
  await nextTick()
  initChart()
})

onUnmounted(() => {
  // 销毁图表实例
  if (matchChart) {
    matchChart.destroy()
  }
})
*/
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

/* 核心模块 */
.modules-section {
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

.module-card {
  background-color: white;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 64px;
}

.module-card:last-child {
  margin-bottom: 0;
}

.module-content {
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 1024px) {
  .module-content {
    grid-template-columns: 1fr 1fr;
  }

  /* 模块1：左边文本，右边演示 */
  .module-text {
    order: 1;
  }

  .module-demo {
    order: 2;
  }

  /* 模块2：左边演示，右边文本 */
  .module-card.reverse .module-text {
    order: 2;
  }

  .module-card.reverse .module-demo {
    order: 1;
  }
}

.module-text {
  padding: 32px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

@media (min-width: 768px) {
  .module-text {
    padding: 48px;
  }
}

.module-header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  margin-bottom: 24px;
}

.module-title-row {
  display: flex;
  align-items: center;
}

.module-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  margin-right: 16px;
}

.module-badge {
  display: inline-block;
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
  padding: 6px 16px;
  border-radius: 16px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 20px;
}

.module-card.reverse .module-badge {
  background-color: rgba(255, 125, 0, 0.1);
  color: #ff7d00;
}

.module-icon.primary {
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
}

.module-icon.secondary {
  background-color: rgba(255, 125, 0, 0.1);
  color: #ff7d00;
}

.module-header h3 {
  font-size: 24px;
  font-weight: 700;
}

.module-text p {
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

.feature-check.secondary {
  background-color: rgba(255, 125, 0, 0.1);
  color: #ff7d00;
}

.feature-content h4 {
  font-weight: 600;
  margin-bottom: 4px;
}

.feature-content p {
  color: #86909c;
  font-size: 14px;
}

.module-demo {
  background-color: #f7f8fa;
  padding: 32px;
}

@media (min-width: 768px) {
  .module-demo {
    padding: 48px;
  }
}

.demo-cards {
  display: grid;
  grid-template-columns: 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

@media (min-width: 640px) {
  .demo-cards {
    grid-template-columns: repeat(2, 1fr);
  }
}

.demo-card {
  background-color: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.demo-card:hover {
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.demo-card-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  margin-bottom: 16px;
}

.demo-card-icon.secondary {
  background-color: rgba(255, 125, 0, 0.1);
  color: #ff7d00;
}

.demo-card h4 {
  font-weight: 600;
  margin-bottom: 8px;
}

.demo-card p {
  color: #86909c;
  font-size: 14px;
}

/* 原图表容器样式已注释
.chart-container {
  background-color: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chart-container h4 {
  font-weight: 600;
  margin-bottom: 16px;
}

.chart-wrapper {
  height: 256px;
}
*/

/* 新增：平台优势展示样式 */
.advantages-container {
  background-color: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.advantages-container h4 {
  font-weight: 600;
  margin-bottom: 20px;
  text-align: center;
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

@media (min-width: 640px) {
  .advantages-grid {
    grid-template-columns: repeat(4, 1fr);
  }
}

.advantage-item {
  text-align: center;
  padding: 16px;
  border-radius: 8px;
  background-color: rgba(22, 93, 255, 0.05);
  transition: all 0.3s ease;
}

.advantage-item:hover {
  background-color: rgba(22, 93, 255, 0.1);
  transform: translateY(-2px);
}

.advantage-number {
  font-size: 24px;
  font-weight: 700;
  color: #165dff;
  margin-bottom: 8px;
}

.advantage-item p {
  color: #86909c;
  font-size: 12px;
  margin: 0;
  font-weight: 500;
}

/* 聊天演示 */
.chat-demo {
  background-color: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
}

.chat-demo h4 {
  font-weight: 600;
  margin-bottom: 16px;
}

.chat-container {
  background-color: #f7f8fa;
  border-radius: 8px;
  padding: 16px;
  height: 256px;
  overflow-y: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
}

.chat-container::-webkit-scrollbar {
  display: none;
}

.chat-message {
  display: flex;
  margin-bottom: 16px;
  align-items: flex-start;
}

.chat-message:last-child {
  margin-bottom: 0;
}

.chat-message.user {
  justify-content: flex-end;
}

.chat-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  flex-shrink: 0;
}

.chat-message.bot .chat-avatar {
  background-color: rgba(22, 93, 255, 0.1);
  color: #165dff;
  margin-right: 12px;
}

.chat-message.user .chat-avatar {
  background-color: #e5e6eb;
  color: #86909c;
  margin-left: 12px;
}

.chat-bubble {
  background-color: white;
  padding: 12px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
  max-width: 80%;
}

.chat-message.bot .chat-bubble {
  border-top-left-radius: 4px;
}

.chat-message.user .chat-bubble {
  background-color: #165dff;
  color: white;
  border-top-right-radius: 4px;
}

.chat-bubble p {
  font-size: 14px;
  margin: 0;
}

.chat-bubble ul {
  font-size: 14px;
  margin: 4px 0 0 0;
  padding-left: 20px;
}

.chat-bubble li {
  margin: 4px 0;
}

/* 按钮样式 */
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

.secondary-btn.orange {
  background-color: #ff7d00;
  color: white;
  border: 1px solid #ff7d00;
}

.secondary-btn.orange:hover {
  background-color: rgba(255, 125, 0, 0.9);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .module-content {
    text-align: center;
  }
}
</style>
