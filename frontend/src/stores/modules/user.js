import { defineStore } from 'pinia'
import { ref } from 'vue'

// 用户模块（保持现有功能不变）
export const useUserStore = defineStore(
  'user',
  () => {
    const user = ref({
      id: '',
      username: '',
      email: '',
      real_name: '',
      phone: '',
      avatar: '',
      gender: '',
      age: null,
      bio: '',
      user_type: '',
      is_active: true,
      is_staff: false,
      date_joined: '',
      last_login: '',
      student_profile: {
        id: '', // 学生信息唯一标识
        student_id: '', // 学号
        school: {
          id: '',
          name: ''
        }, // 学校信息对象
        major: '', // 专业
        grade: '', // 入学年份
        education_level: '', // 学历等级（如undergraduate）
        education_level_display: '', // 学历显示名称（如本科）
        status: '', // 学籍状态（如studying）
        status_display: '', // 学籍状态显示名称（如在读）
        expected_graduation: null, // 预计毕业时间
        interests: [], // 兴趣爱好列表
        skills: [], // 技能列表
        created_at: '', // 学生信息创建时间
        updated_at: '' // 学生信息更新时间
      },
      company_profile: {
        id: '', // 组织成员唯一标识
        position: '', // 职位（如CEO）
        department: '', // 部门
        permission: '', // 权限等级（如admin）
        permission_display: '', // 权限显示名称（如管理员）
        status: '', // 加入企业状态（如pending）
        status_display: '', // 加入企业显示名称（如待审核）
        joined_at: '', // 加入组织时间
        updated_at: '', // 信息更新时间
        organization: {
          id: '',
          name: '',
          code: null,
          leader_name: '',
          leader_title: '',
          registration_number: '',
          organization_type: '',
          organization_type_display: '',
          enterprise_type: '',
          enterprise_type_display: '',
          university_type: null,
          university_type_display: null,
          industry_or_discipline: '',
          scale: '',
          scale_display: '',
          contact_person: '',
          contact_position: '',
          contact_phone: '',
          contact_email: '',
          address: '',
          postal_code: '',
          description: '',
          website: '',
          logo: null,
          status: '',
          status_display: '',
          verified_at: null,
          established_date: null,
          created_at: '',
          updated_at: ''
        }
      }
    })

    const setUser = async (userData) => {
      const next = { ...user.value, ...userData }
      if (
        userData &&
        typeof userData.student_profile === 'object' &&
        userData.student_profile !== null
      ) {
        next.student_profile = { ...user.value.student_profile, ...userData.student_profile }
      }
      if (
        userData &&
        typeof userData.company_profile === 'object' &&
        userData.company_profile !== null
      ) {
        next.company_profile = {
          ...user.value.company_profile,
          ...userData.company_profile,
          organization: {
            ...user.value.company_profile.organization,
            ...(userData.company_profile?.organization || {})
          }
        }
      }
      user.value = next
    }

    const clearUser = () => {
      user.value = {
        id: '',
        username: '',
        email: '',
        real_name: '',
        phone: '',
        avatar: '',
        gender: '',
        age: null,
        bio: '',
        user_type: '',
        is_active: true,
        is_staff: false,
        date_joined: '',
        last_login: '',
        student_profile: {
          id: '', // 学生信息唯一标识
          student_id: '', // 学号
          school: {
            id: '',
            name: ''
          }, // 学校信息对象
          major: '', // 专业
          grade: '', // 入学年份
          education_level: '', // 学历等级
          education_level_display: '', // 学历显示名称
          status: '', // 学籍状态
          status_display: '', // 学籍状态显示名称
          expected_graduation: null, // 预计毕业时间
          interests: [], // 兴趣爱好列表
          skills: [], // 技能列表
          created_at: '', // 学生信息创建时间
          updated_at: '' // 学生信息更新时间
        },
        company_profile: {
          id: '', // 组织成员唯一标识
          position: '', // 职位
          department: '', // 部门
          permission: '', // 权限等级
          permission_display: '', // 权限显示名称
          status: '', // 认证状态
          status_display: '', // 认证状态显示名称
          joined_at: '', // 加入组织时间
          updated_at: '', // 信息更新时间
          organization: {
            id: '',
            name: '',
            code: null,
            leader_name: '',
            leader_title: '',
            registration_number: '',
            organization_type: '',
            organization_type_display: '',
            enterprise_type: '',
            enterprise_type_display: '',
            university_type: null,
            university_type_display: null,
            industry_or_discipline: '',
            scale: '',
            scale_display: '',
            contact_person: '',
            contact_position: '',
            contact_phone: '',
            contact_email: '',
            address: '',
            postal_code: '',
            description: '',
            website: '',
            logo: null,
            status: '',
            status_display: '',
            verified_at: null,
            established_date: null,
            created_at: '',
            updated_at: ''
          }
        }
      }
    }

    return { user, setUser, clearUser }
  },
  { persist: { enabled: true, storage: localStorage, paths: ['user'] } }
)
