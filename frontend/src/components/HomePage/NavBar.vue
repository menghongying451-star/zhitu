<template>
  <header :class="['navbar', { scrolled: navbarScrolled }]">
    <div class="container">
      <div class="navbar-content">
        <div class="navbar-brand">
          <a href="#" class="brand-link">
            <span class="brand-title">智汇</span>
            <span class="brand-subtitle">产教融合平台</span>
          </a>
        </div>

        <!-- 桌面导航 -->
        <nav class="desktop-nav">
          <a href="#dashboard" @click.prevent="scrollToSection('#dashboard')" class="nav-link"
            >数据大屏</a
          >
          <a href="#features" @click.prevent="scrollToSection('#features')" class="nav-link"
            >核心功能</a
          >
          <a href="#modules" @click.prevent="scrollToSection('#modules')" class="nav-link"
            >核心模块</a
          >
          <a href="#services" @click.prevent="scrollToSection('#services')" class="nav-link"
            >服务对象</a
          >
          <!-- <a href="#cases" @click.prevent="scrollToSection('#cases')" class="nav-link">成功案例</a> -->
          <a href="#faq" @click.prevent="scrollToSection('#faq')" class="nav-link">常见问题</a>
          <a @click.prevent="router.push('/help')" class="nav-link">帮助文档</a>
        </nav>

        <div class="navbar-actions">
          <router-link to="/login" class="login-link">登录</router-link>
          <router-link :to="{ path: '/login', query: { mode: 'register' } }" class="register-btn"
            >注册</router-link
          >

          <!-- 移动端菜单按钮 -->
          <button @click="toggleMobileMenu" class="menu-toggle">
            <font-awesome-icon :icon="['fas', 'bars']" />
          </button>
        </div>
      </div>

      <!-- 移动端导航菜单 -->
      <div v-show="mobileMenuVisible" class="mobile-menu">
        <div class="mobile-menu-content">
          <a href="#dashboard" @click.prevent="scrollToSection('#dashboard')" class="nav-link"
            >数据大屏</a
          >
          <a href="#features" @click.prevent="scrollToSection('#features')" class="mobile-nav-link"
            >核心功能</a
          >
          <a href="#modules" @click.prevent="scrollToSection('#modules')" class="mobile-nav-link"
            >核心模块</a
          >
          <a href="#services" @click.prevent="scrollToSection('#services')" class="mobile-nav-link"
            >服务对象</a
          >
          <!-- <a href="#cases" @click.prevent="scrollToSection('#cases')" class="mobile-nav-link"
            >成功案例</a
          > -->
          <a href="#faq" @click.prevent="scrollToSection('#faq')" class="mobile-nav-link"
            >常见问题</a
          >
          <a @click.prevent="router.push('/help')" class="mobile-nav-link">帮助文档</a>
          <div class="mobile-actions">
            <router-link to="/login" class="mobile-login-btn">登录</router-link>
            <router-link
              :to="{ path: '/login', query: { mode: 'register' } }"
              class="mobile-register-btn"
            >
              注册
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { useRouter } from 'vue-router'

const router = useRouter()
const mobileMenuVisible = ref(false)
const navbarScrolled = ref(false)

const toggleMobileMenu = () => {
  mobileMenuVisible.value = !mobileMenuVisible.value
}

const scrollToSection = (sectionId) => {
  const element = document.querySelector(sectionId)
  if (element) {
    const offsetTop = element.offsetTop - 80
    window.scrollTo({
      top: offsetTop,
      behavior: 'smooth'
    })
    mobileMenuVisible.value = false
  }
}

const handleScroll = () => {
  navbarScrolled.value = window.scrollY > 50
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})
</script>

<style scoped>
/* 导航栏样式 */
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  transition: all 0.3s ease;
  background-color: transparent;
}

.navbar.scrolled {
  background-color: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

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

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 80px;
}

.brand-link {
  display: flex;
  align-items: center;
  text-decoration: none;
}

.brand-title {
  color: #165dff;
  font-size: 24px;
  font-weight: 700;
}

.brand-subtitle {
  margin-left: 8px;
  color: #86909c;
  font-size: 14px;
}

.desktop-nav {
  display: none;
  gap: 32px;
}

@media (min-width: 768px) {
  .desktop-nav {
    display: flex;
  }
}

.nav-link {
  color: #4e5969;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.nav-link:hover {
  color: #165dff;
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 16px;
}

.login-link {
  display: none;
  color: #4e5969;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s ease;
}

.login-link:hover {
  color: #165dff;
}

@media (min-width: 640px) {
  .login-link {
    display: inline-block;
  }
}

.register-btn {
  display: none;
  padding: 8px 24px;
  background-color: #165dff;
  color: white;
  text-decoration: none;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s ease;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.register-btn:hover {
  background-color: rgba(22, 93, 255, 0.9);
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

@media (min-width: 640px) {
  .register-btn {
    display: inline-block;
  }
}

.menu-toggle {
  display: block;
  background: none;
  border: none;
  color: #4e5969;
  font-size: 24px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.menu-toggle:hover {
  color: #165dff;
}

@media (min-width: 768px) {
  .menu-toggle {
    display: none;
  }
}

/* 移动端菜单 */
.mobile-menu {
  background-color: white;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
}

@media (min-width: 768px) {
  .mobile-menu {
    display: none !important;
  }
}

.mobile-menu-content {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.mobile-nav-link {
  color: #4e5969;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 0;
  transition: color 0.2s ease;
}

.mobile-nav-link:hover {
  color: #165dff;
}

.mobile-actions {
  display: flex;
  gap: 16px;
  padding-top: 8px;
}

.mobile-login-btn,
.mobile-register-btn {
  flex: 1;
  text-align: center;
  padding: 8px 16px;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

.mobile-login-btn {
  border: 1px solid #e5e6eb;
  color: #4e5969;
}

.mobile-login-btn:hover {
  background-color: #f7f8fa;
}

.mobile-register-btn {
  background-color: #165dff;
  color: white;
}

.mobile-register-btn:hover {
  background-color: rgba(22, 93, 255, 0.9);
}
</style>
