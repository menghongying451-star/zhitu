<template>
  <section id="faq" class="faq-section">
    <div class="container">
      <div class="section-header">
        <span class="section-badge">常见问题</span>
        <h2 class="section-title">您可能想了解的问题</h2>
        <p class="section-description">我们整理了最常咨询的问题，希望能帮助您更好地了解智汇平台</p>
      </div>

      <div class="faq-container">
        <div class="faq-list">
          <div v-for="item in faqItems" :key="item.id" class="faq-item">
            <button @click="toggleFAQ(item.id)" class="faq-question">
              <span>{{ item.question }}</span>
              <i :class="['fa', item.open ? 'fa-minus' : 'fa-plus']"></i>
            </button>
            <div v-show="item.open" class="faq-answer">
              <p v-html="item.answer"></p>
            </div>
          </div>
        </div>

        <div class="faq-contact">
          <p>还有其他问题？</p>
          <a @click="dialogVisible = true" class="primary-btn" href="javascript:void(0)">
            联系客服
            <font-awesome-icon :icon="['fab', 'qq']" />
          </a>
        </div>
      </div>
    </div>

    <!-- QQ群信息弹窗 -->
    <el-dialog v-model="dialogVisible" title="联系客服" width="360px" align-center>
      <div class="qq-info">
        <p class="qq-group-number">QQ群号：{{ qqGroupInfo.number }}</p>
        <img :src="qqGroupInfo.qrCodePath" alt="QQ群二维码" class="qq-qrcode" />
      </div>
    </el-dialog>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faQq } from '@fortawesome/free-brands-svg-icons'
import { library } from '@fortawesome/fontawesome-svg-core'

// 添加QQ图标到图标库
library.add(faQq)

// QQ群信息弹窗状态
const dialogVisible = ref(false)
const qqGroupInfo = {
  number: '611048201',
  qrCodePath: '/picture/QQ群.png'
}

// FAQ状态
const faqItems = ref([
  {
    id: 1,
    question: '企业如何在智汇平台发布项目需求？',
    answer:
      '企业可以通过以下步骤在智汇平台发布项目需求：1. 注册并认证企业账号；2. 完善企业信息和技术领域偏好；3. 在"发布需求"页面填写项目详细信息，包括项目背景、技术要求、时间周期等；4. 上传相关资料，如需求文档、技术规范等；5. 提交审核，平台将在24小时内完成审核并发布',
    open: false
  },
  {
    id: 2,
    question: '学生如何参与平台上的项目？',
    answer:
      '学生可以通过以下方式参与平台上的项目：1. 注册并完善个人资料，包括教育背景、技能特长等；2. 完成平台提供的能力测评，生成个人能力画像；3. 浏览平台上发布的项目需求，选择感兴趣的项目提交申请；4. 审核通过后，即可加入项目团队开始工作；5. 项目结束后，获得企业评价和项目经验认证',
    open: false
  },
  {
    id: 3,
    question: '平台如何保障项目质量和知识产权？',
    answer:
      '智汇平台通过以下措施保障项目质量和知识产权：项目全程管理、质量审核机制、知识产权协议、纠纷调解服务等。',
    open: false
  },
  {
    id: 4,
    question: '平台对学校有哪些支持？',
    answer: '智汇平台为学校提供：课程体系优化、实践教学资源、学生就业服务、产学研合作等支持。',
    open: false
  },
  {
    id: 5,
    question: '使用平台需要付费吗？',
    answer: '智汇平台对学生和学校完全免费，不收取任何费用。企业/组织用户也可免费发布项目需求。',
    open: false
  }
])

// 方法
const toggleFAQ = (id) => {
  const item = faqItems.value.find((item) => item.id === id)
  if (item) {
    item.open = !item.open
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

/* 常见问题 */
.faq-section {
  padding: 80px 0;
  /* background-color: white; */
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

.faq-container {
  max-width: 768px;
  margin: 0 auto;
}

.faq-list {
  margin-bottom: 48px;
}

.faq-item {
  border: 1px solid #e5e6eb;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 24px;
}

.faq-item:last-child {
  margin-bottom: 0;
}

.faq-question {
  width: 100%;
  padding: 24px;
  text-align: left;
  font-weight: 500;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: none;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.faq-question:hover {
  background-color: #f7f8fa;
}

.faq-question i {
  color: #165dff;
  transition: transform 0.3s ease;
}

.faq-answer {
  padding: 0 24px 24px;
}

.faq-answer p {
  color: #86909c;
  margin: 0;
}

.faq-contact {
  text-align: center;
}

.faq-contact p {
  color: #86909c;
  margin-bottom: 16px;
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

/* QQ群信息样式 */
.qq-info {
  text-align: center;
  padding: 20px;
}

.qq-group-number {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: #333;
}

.qq-qrcode {
  max-width: 200px;
  height: auto;
  margin: 0 auto;
  display: block;
}
</style>
