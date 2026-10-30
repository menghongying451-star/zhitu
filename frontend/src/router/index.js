import { ref } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/home'
    },
    {
      path: '/home',
      component: () => import('@/views/HomePage.vue')
    },
    {
      path: '/login',
      component: () => import('@/views/LoginPage.vue')
    },
    {
      path: '/help/:pathMatch(.*)*',
      component: () => import('@/views/HelpDocs.vue')
    },
    {
      path: '/test',
      component: () => import('@/views/test.vue')
    },
    // 新增大屏路由，登录前可访问
    {
      path: '/dashboard',
      component: () => import('@/views/DashBoard.vue')
    },
    // 学生相关路由（只添加必要子路由）
    {
      path: '/student',
      component: () => import('@/views/student/StudentLayout.vue'),
      children: [
        {
          path: '',
          redirect: '/student/project-requirement'
        },
        {
          path: 'project-requirement',
          component: () => import('@/views/student/ProjectRequirement.vue')
        },
        {
          path: 'demand-following',
          component: () => import('@/views/student/DemandFollowing.vue')
        },
        // 历史对话（当前为纯前端 localStorage 版本）
        {
          path: 'chat-history',
          component: () => import('@/views/student/ChatHistory.vue')
        },
        {
          path: 'my-projects',
          component: () => import('@/views/student/MyProjects.vue')
        },
        {
          path: 'my-projects/:id',
          component: () => import('@/views/student/MyProjectDetail.vue')
        },
        // 新增：通知中心
        {
          path: 'notification-center',
          component: () => import('@/views/NotificationCenter.vue')
        },
        {
          path: 'settings',
          component: () => import('@/views/UserCenter.vue')
        }
      ]
    },
    // 企业相关路由（原样保留）
    {
      path: '/enterprise',
      redirect: '/enterprise/dashboard',
      component: () => import('@/views/enterprise/EnterpriseLayout.vue'),
      children: [
        {
          path: '/enterprise/dashboard',
          component: () => import('@/views/enterprise/EnterpriseDashboard.vue')
        },
        {
          path: '/enterprise/resource-management',
          component: () => import('@/views/enterprise/ResourceManagement.vue')
        },
        {
          path: '/enterprise/resource/create',
          component: () => import('@/views/enterprise/ResourceEditor.vue')
        },
        {
          path: '/enterprise/resource/edit/:id',
          component: () => import('@/views/enterprise/ResourceEditor.vue')
        },
        {
          path: '/enterprise/resource/detail/:id',
          component: () => import('@/views/enterprise/ResourceDetail.vue')
        },
        {
          path: '/enterprise/requirement-management',
          component: () => import('@/views/enterprise/RequirementManagement.vue')
        },
        {
          path: '/enterprise/requirement/create/:mode',
          component: () => import('@/views/enterprise/RequirementEditor.vue')
        },
        {
          path: '/enterprise/requirement/edit/:id',
          component: () => import('@/views/enterprise/RequirementEditor.vue')
        },
        {
          path: '/enterprise/requirement/detail/:id',
          component: () => import('@/views/enterprise/RequirementDetail.vue')
        },
        {
          path: '/enterprise/notification-center',
          component: () => import('@/views/NotificationCenter.vue')
        },
        {
          path: '/enterprise/enterprise-settings',
          component: () => import('@/views/enterprise/EnterpriseSettings.vue')
        },
        {
          path: '/enterprise/user-center',
          component: () => import('@/views/UserCenter.vue')
        },
        {
          path: '/enterprise/certification',
          component: () => import('@/views/enterprise/CertificationPage.vue')
        },
        {
          path: '/enterprise/project-details/:id',
          component: () => import('@/views/enterprise/ProjectDetail.vue')
        }
      ]
    },
    // 管理员相关路由（原样保留）
    {
      path: '/admin',
      children: [
        // 管理员子路由将在这里定义
      ]
    }
  ]
})

// 认证守卫 - 检查用户是否已登录
// const AuthGuard = async (to) => {
//   const { useAuthStore } = await import('@/stores')
//   const authStore = useAuthStore()

//   // 需要认证的路由模式
//   const authRoutes = ['/student/', '/enterprise/', '/admin/']

//   // 检查当前路由是否需要认证
//   const requiresAuth = authRoutes.some((route) => to.path.startsWith(route))

//   if (requiresAuth && !authStore.token) {
//     return '/login'
//   }

//   return true
// }

// 角色守卫 - 检查用户是否有权限访问特定角色路由
// const RoleGuard = async (to) => {
//   const { useUserStore } = await import('@/stores')
//   const userStore = useUserStore()

//   // 检查用户角色与路由的匹配
//   if (to.path.startsWith('/student/') && userStore.user.user_type !== 'student') {
//     return '/home'
//   }

//   if (to.path.startsWith('/enterprise/') && userStore.user.user_type !== 'enterprise') {
//     return '/home'
//   }

//   if (to.path.startsWith('/admin/') && userStore.user.user_type !== 'admin') {
//     return '/home'
//   }

//   return true
// }

// 路由前置守卫
// router.beforeEach(async (to) => {
//   // 白名单路由
//   const whiteList = ['/login', '/test', '/home']
//   if (whiteList.includes(to.path)) {
//     return true
//   }

//   // 先检查认证状态
//   const authCheck = await AuthGuard(to)
//   if (authCheck !== true) {
//     return authCheck
//   }

//   // 再检查角色权限
//   const roleCheck = await RoleGuard(to)
//   if (roleCheck !== true) {
//     return roleCheck
//   }

//   // 已登录时禁止访问登录页
//   if (to.path === '/login') {
//     return '/home'
//   }

//   return true
// })

// 定时刷新 token
const refreshInterval = ref(null)
router.afterEach(async (to) => {
  // 清除之前可能存在的定时器
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }

  // 导入 refresh 函数
  const { refresh } = await import('@/utils/auth')

  // 只在需要刷新的页面设置定时器
  const refreshPages = []
  // 为受保护的路由也添加 token 刷新
  const protectedPaths = ['/student/', '/enterprise/', '/admin/']
  const needsRefresh =
    refreshPages.some((page) => to.path === page) ||
    protectedPaths.some((path) => to.path.startsWith(path))

  if (needsRefresh) {
    refreshInterval.value = setInterval(
      () => {
        refresh()
      },
      1000 * 60 * 30
    )
  }
})

export default router
