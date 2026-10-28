// stores/settingsStore.js (Composition API 版本)
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useEnterpriseStore = defineStore(
  'enterprise',
  () => {
    // 企业信息
    const companyInfo = ref({
      // 基本信息
      id: '',
      organizationType: '', // enterprise（企业）/university（大学）/other（其他组织）
      organizationTypeDisplay: '', // 组织类型显示名称
      typeDisplay: '', // 类型显示名称（兼容字段）
      name: '',
      code: '', // 企业：统一社会信用代码；大学：教育部代码；其他组织：组织代码

      // 企业特有字段
      enterpriseType: '', // 企业类型（仅企业）
      enterpriseTypeDisplay: '', // 企业类型显示名称

      // 大学特有字段
      universityType: '', // 大学类型（仅大学）
      universityTypeDisplay: '', // 大学类型显示名称

      // 其他组织特有字段
      otherType: '', // 其他组织类型：government（政府机构）/ngo（非营利组织）/foundation（基金会）/association（行业协会）/research_institute（科研院所）/hospital（医疗机构）/media（媒体机构）/cultural（文化机构）/sports（体育组织）/religious（宗教组织）/international（国际组织）/community（社区组织）/cooperative（合作社）/union（工会组织）/chamber（商会）/other_unspecified（其他未分类）
      otherTypeDisplay: '', // 其他组织类型显示名称
      organizationNature: '', // 组织性质：public（公立/公办）/private（私立/民办）/joint（公私合营）/international（国际性）/regional（地区性）/national（全国性）
      organizationNatureDisplay: '', // 组织性质显示名称
      businessScope: '', // 业务范围/服务领域（适用于其他组织，最大长度200字符）
      regulatoryAuthority: '', // 监管机构（适用于政府机构、非营利组织、基金会等需要特殊监管的组织，最大长度100字符）
      licenseInfo: '', // 许可证/资质信息（适用于医疗机构、科研院所等需要特殊资质的组织）
      serviceTarget: '', // 服务对象：public（面向公众）/members（面向会员）/industry（面向行业）/government（面向政府）/enterprises（面向企业）/students（面向学生）/patients（面向患者）/community（面向社区）/other（其他）
      serviceTargetDisplay: '', // 服务对象显示名称

      industryOrDiscipline: '', // 企业：所属行业；大学：主要学科门类；其他组织：行业/学科领域
      scale: '', // 规模

      // 联系信息
      contactPerson: '', // 联系人（初步定为首个建立该组织的用户）
      contactPosition: '', // 联系人职位
      contactPhone: '',
      contactEmail: '',

      // 负责人信息
      leaderName: '', // 企业：法定代表人；大学：校长；其他组织：负责人姓名
      leaderTitle: '', // 负责人职务

      // 地址和其他信息
      address: '',
      postalCode: '', // 邮政编码
      description: '',
      website: '',
      logo: '',
      status: '', // pending/under_review/verified/rejected/closed，待认证/审核中/已认证/认证被拒/已关闭
      statusDisplay: '', // 状态显示名称
      verifiedAt: '', // 认证通过时间
      establishedDate: '',
      createdAt: '',
      updatedAt: ''
    })

    const updateCompanyInfo = (data) => {
      companyInfo.value = { ...companyInfo.value, ...data }
    }

    // 团队管理
    const teamManagement = ref({
      totalMembers: 0,
      pendingMembers: 0,
      admins: 0,
      userRole: 'member', // 当前用户角色：member, admin, owner, pending
      userRoleDisplay: '成员',
      userStatus: 'approved', // 当前用户状态：pending, approved, rejected
      userStatusDisplay: '已通过',
      userPosition: '',
      userDepartment: '',
      members: [
        {
          id: 1,
          username: 'zhangsan',
          real_name: '张三',
          phone: '138****8001',
          email: 'zhan****@example.com',
          department: '研发部',
          position: '技术总监',
          permission: 'admin',
          status: 'active',
          created_at: '2024-01-01T00:00:00Z'
        },
        {
          id: 2,
          username: 'lisi',
          real_name: '李四',
          phone: '139****9002',
          email: 'li****@example.com',
          department: '产品部',
          position: '产品经理',
          permission: 'member',
          status: 'active',
          created_at: '2024-01-02T00:00:00Z'
        }
      ]
    })

    // 设置团队成员列表
    const setTeamMembers = (members) => {
      teamManagement.value.members = members
    }

    // 更新成员信息
    const updateMemberInfo = (memberId, updates) => {
      const member = teamManagement.value.members.find((m) => m.id === memberId)
      if (member) {
        Object.assign(member, updates)
      }
    }

    // 批量更新成员
    const batchUpdateMembers = (memberIds, updates) => {
      memberIds.forEach((id) => {
        const member = teamManagement.value.members.find((m) => m.id === id)
        if (member) {
          Object.assign(member, updates)
        }
      })
    }

    // 设置用户权限信息
    const setUserPermission = (role, status, position = '', department = '') => {
      teamManagement.value.userRole = role
      teamManagement.value.userStatus = status
      teamManagement.value.userPosition = position
      teamManagement.value.userDepartment = department

      // 设置显示名称
      const roleDisplayMap = {
        owner: '拥有者',
        admin: '管理员',
        member: '成员',
        pending: '待分配'
      }

      const statusDisplayMap = {
        pending: '待审核',
        approved: '已通过',
        rejected: '已拒绝'
      }

      teamManagement.value.userRoleDisplay = roleDisplayMap[role] || role
      teamManagement.value.userStatusDisplay = statusDisplayMap[status] || status
    }

    // 更新统计数据
    const updateTeamStats = (stats) => {
      Object.assign(teamManagement.value, stats)
    }

    // // 账户安全
    // const accountSecurity = ref({
    //   adminName: '张经理',
    //   email: 'admin@xxtech.com',
    //   phone: '138****8888',
    //   twoFactor: false,
    //   loginNotification: true,
    //   abnormalProtection: true,
    //   loginHistory: [
    //     {
    //       id: 1,
    //       device: 'Windows - Chrome',
    //       location: '北京市',
    //       time: '2025-08-02 09:30',
    //       status: 'current'
    //     },
    //     {
    //       id: 2,
    //       device: 'iPhone - Safari',
    //       location: '北京市',
    //       time: '2025-08-01 18:45',
    //       status: 'active'
    //     },
    //     {
    //       id: 3,
    //       device: 'MacOS - Chrome',
    //       location: '上海市',
    //       time: '2025-07-30 14:20',
    //       status: 'offline'
    //     }
    //   ]
    // })

    // // 权限设置
    // const permissions = ref({
    //   roles: [
    //     {
    //       name: '超级管理员',
    //       description: '拥有所有权限的最高管理角色',
    //       count: 1,
    //       permissions: ['*']
    //     },
    //     {
    //       name: '项目管理员',
    //       description: '负责项目管理和团队协调',
    //       count: 3,
    //       permissions: ['project_*', 'talent_*', 'requirement_*']
    //     },
    //     {
    //       name: '普通成员',
    //       description: '基础操作权限',
    //       count: 20,
    //       permissions: ['project_view']
    //     }
    //   ],
    //   accessControl: {
    //     ipWhitelist: false,
    //     forceHttps: true,
    //     sessionTimeout: '30分钟'
    //   },
    //   auditLogs: [
    //     {
    //       id: 1,
    //       user: '张经理',
    //       action: '修改了企业信息',
    //       time: '2025-08-02 10:30',
    //       type: '修改'
    //     },
    //     {
    //       id: 2,
    //       user: '李华',
    //       action: '邀请了新成员',
    //       time: '2025-08-01 16:45',
    //       type: '邀请'
    //     }
    //   ]
    // })

    // // 通知设置
    // const notifications = ref({
    //   email: {
    //     projectUpdate: true,
    //     newApplication: true,
    //     systemMaintenance: false,
    //     marketing: false
    //   },
    //   sms: {
    //     securityAlert: true,
    //     verificationCode: true
    //   },
    //   frequency: '实时通知',
    //   pushTime: {
    //     start: '09:00',
    //     end: '18:00'
    //   },
    //   recentNotifications: [
    //     {
    //       id: 1,
    //       title: '项目"智能巡检系统"进度更新',
    //       time: '2小时前',
    //       type: 'info'
    //     },
    //     {
    //       id: 2,
    //       title: '新成员李华已成功加入团队',
    //       time: '5小时前',
    //       type: 'success'
    //     },
    //     {
    //       id: 3,
    //       title: '系统将于今晚22:00进行维护',
    //       time: '1天前',
    //       type: 'warning'
    //     }
    //   ]
    // })

    // // 系统配置
    // const systemConfig = ref({
    //   language: '简体中文',
    //   timezone: '北京时间 (GMT+8)',
    //   dateFormat: 'YYYY-MM-DD',
    //   api: {
    //     key: 'sk-1234567890abcdef',
    //     rateLimit: '1000次/小时',
    //     logging: true
    //   },
    //   integrations: [
    //     {
    //       name: 'Slack',
    //       description: '团队协作通知',
    //       connected: false,
    //       icon: 'slack'
    //     },
    //     {
    //       name: '企业微信',
    //       description: '消息推送',
    //       connected: true,
    //       icon: 'wechat'
    //     },
    //     {
    //       name: '钉钉',
    //       description: '任务同步',
    //       connected: false,
    //       icon: 'dingtalk'
    //     }
    //   ],
    //   systemStatus: {
    //     version: 'v2.1.3',
    //     lastUpdate: '2025-07-15',
    //     status: 'normal',
    //     database: 'connected'
    //   }
    // })

    // const updateAccountSecurity = (data) => {
    //   accountSecurity.value = { ...accountSecurity.value, ...data }
    // }

    // const updatePassword = (oldPassword, newPassword) => {
    //   return new Promise((resolve, reject) => {
    //     setTimeout(() => {
    //       if (oldPassword === 'correct') {
    //         resolve('密码更新成功')
    //       } else {
    //         reject('当前密码错误')
    //       }
    //     }, 1000)
    //   })
    // }

    // const kickoutSession = (sessionId) => {
    //   const index = accountSecurity.value.loginHistory.findIndex((h) => h.id === sessionId)
    //   if (index > -1) {
    //     accountSecurity.value.loginHistory[index].status = 'offline'
    //   }
    // }

    // const addRole = (role) => {
    //   permissions.value.roles.push({
    //     ...role,
    //     count: 0
    //   })
    // }

    // const updateRole = (roleName, updates) => {
    //   const role = permissions.value.roles.find((r) => r.name === roleName)
    //   if (role) {
    //     Object.assign(role, updates)
    //   }
    // }

    // const updateAccessControl = (data) => {
    //   permissions.value.accessControl = { ...permissions.value.accessControl, ...data }
    // }

    // const addAuditLog = (log) => {
    //   permissions.value.auditLogs.unshift({
    //     ...log,
    //     id: Date.now(),
    //     time: new Date().toLocaleString('zh-CN')
    //   })
    // }

    // const updateNotifications = (data) => {
    //   notifications.value = { ...notifications.value, ...data }
    // }

    // const addNotification = (notification) => {
    //   notifications.value.recentNotifications.unshift({
    //     ...notification,
    //     id: Date.now(),
    //     time: '刚刚'
    //   })
    // }

    // const updateSystemConfig = (data) => {
    //   systemConfig.value = { ...systemConfig.value, ...data }
    // }

    // const toggleIntegration = (integrationName) => {
    //   const integration = systemConfig.value.integrations.find((i) => i.name === integrationName)
    //   if (integration) {
    //     integration.connected = !integration.connected
    //   }
    // }

    // const regenerateApiKey = () => {
    //   systemConfig.value.api.key =
    //     'sk-' +
    //     Math.random().toString(36).substring(2, 15) +
    //     Math.random().toString(36).substring(2, 15)
    // }

    // const saveAllSettings = () => {
    //   return new Promise((resolve) => {
    //     setTimeout(() => {
    //       addAuditLog({
    //         user: accountSecurity.value.adminName,
    //         action: '保存了系统设置',
    //         type: '修改'
    //       })
    //       resolve('设置保存成功')
    //     }, 1000)
    //   })
    // }

    // // Computed getters
    // const currentUser = computed(() => ({
    //   name: accountSecurity.value.adminName,
    //   email: accountSecurity.value.email,
    //   role: '超级管理员'
    // }))

    // const permissionStats = computed(() => ({
    //   totalRoles: permissions.value.roles.length,
    //   totalUsers: teamManagement.value.totalMembers,
    //   activeIntegrations: systemConfig.value.integrations.filter((i) => i.connected).length
    // }))

    // const unreadNotificationsCount = computed(() => {
    //   return notifications.value.recentNotifications.length
    // })

    // const systemHealth = computed(() => {
    //   const { systemStatus } = systemConfig.value
    //   return {
    //     overall:
    //       systemStatus.status === 'normal' && systemStatus.database === 'connected'
    //         ? 'healthy'
    //         : 'warning',
    //     details: systemStatus
    //   }
    // })

    // 返回所有需要暴露的状态和方法
    return {
      // 状态
      companyInfo,
      teamManagement,
      // accountSecurity,
      // permissions,
      // notifications,
      // systemConfig,

      // Actions
      updateCompanyInfo,
      setTeamMembers,
      updateMemberInfo,
      batchUpdateMembers,
      setUserPermission,
      updateTeamStats
      // updateAccountSecurity,
      // updatePassword,
      // kickoutSession,
      // addRole,
      // updateRole,
      // updateAccessControl,
      // addAuditLog,
      // updateNotifications,
      // addNotification,
      // updateSystemConfig,
      // toggleIntegration,
      // regenerateApiKey,
      // saveAllSettings,

      // // Getters
      // currentUser,
      // permissionStats,
      // unreadNotificationsCount,
      // systemHealth
    }
  },
  {
    persist: {
      enabled: true,
      storage: localStorage,
      paths: ['companyInfo', 'accountSecurity', 'systemConfig']
    }
  }
)
