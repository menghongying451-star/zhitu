# Authentication API 文档

## 概述

Authentication 应用提供用户认证相关的 API 接口，包括用户注册、登录、登出、密码管理、邮箱验证、账户注销等功能。

## 基础信息

- **基础URL**: `/api/v1/auth/`
- **认证方式**: JWT (JSON Web Token)
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`

## 响应格式

所有API响应都遵循统一的格式：

### 成功响应
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        // 具体数据
    },
    "error": {}
}
```

### 失败响应
```json
{
    "status": "error",
    "code": 400,
    "message": "错误信息",
    "data": {},
    "error": {
        "field_name": ["具体错误信息"]
    }
}
```

## 认证接口

### 1. 发送邮箱验证码

**接口**: `POST /api/v1/auth/send-email-code/`
**描述**: 发送邮箱验证码，支持注册、登录、重置密码等场景
**权限**: 无需认证

#### 请求头
```
Content-Type: application/json
```

#### 请求参数
```json
{
    "email": "user@example.com",
    "code_type": "register"
}
```

**参数说明**:
- `email`: 邮箱地址（必填，格式验证）
- `code_type`: 验证码类型（必填）
  - `register`: 注册验证码
  - `login`: 登录验证码
  - `reset`: 重置密码验证码
  - `change_email`: 修改邮箱验证码
  - `delete_account`: 账户注销验证码

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "验证码发送成功",
    "data": {
        "email": "user@example.com",
        "code_type": "register"
    },
    "error": {}
}
```

#### 错误响应示例
```json
{
    "status": "error",
    "code": 422,
    "message": "该邮箱已注册",
    "data": {},
    "error": {
        "email": ["该邮箱已注册"]
    }
}
```

### 2. 用户注册

**接口**: `POST /api/v1/auth/register/`
**描述**: 用户注册，支持学生和企业用户注册
**权限**: 无需认证

#### 请求头
```
Content-Type: application/json
```

#### 请求参数

**学生用户注册**:
```json
{
    "username": "student123",
    "email": "student@example.com",
    "email_code": "123456",
    "password": "Password123!",
    "confirm_password": "Password123!",
    "user_type": "student",
    "student_id": "2024001",
    "school": "北京大学",
    "major": "计算机科学与技术",
    "education": "本科",
    "grade": "2024"
}
```

**组织用户注册（加入现有组织）**:
```json
{
    "username": "user123",
    "email": "user@company.com",
    "email_code": "123456",
    "password": "Password123!",
    "confirm_password": "Password123!",
    "user_type": "organization",
    "registration_choice": "existing",
    "organization_id": 1,
    "position": "软件工程师",
    "department": "技术部"
}
```

**组织用户注册（创建新组织）**:
```json
{
    "username": "admin123",
    "email": "admin@newcompany.com",
    "email_code": "123456",
    "password": "Password123!",
    "confirm_password": "Password123!",
    "user_type": "organization",
    "registration_choice": "new",
    "organization_name": "新科技公司",
    "organization_type": "enterprise",
    "industry_or_discipline": "人工智能",
    "position": "技术总监",
    "department": "技术部"
}
```

**参数说明**:
- `username`: 用户名（必填，最大30字符）
- `email`: 邮箱地址（必填，格式验证）
- `email_code`: 邮箱验证码（必填，最大10字符）
- `password`: 密码（必填，6-128位，需包含大写字母、小写字母、数字、特殊字符中的至少两种）
- `confirm_password`: 确认密码（必填，需与密码一致）
- `user_type`: 用户类型（必填）
  - `student`: 学生用户
  - `organization`: 组织用户

**学生用户专用参数**（必填）:
- `student_id`: 学号（最大20字符）
- `school`: 学校（最大100字符）
- `major`: 专业（最大100字符）
- `education`: 学历层次（最大20字符）
- `grade`: 年级（最大10字符）

**组织用户专用参数**:
- `registration_choice`: 注册选择（组织用户必填）
  - `existing`: 加入现有组织
  - `new`: 创建新组织
- `position`: 职位/职务（必填，最大100字符）
- `department`: 部门/院系（可选，最大100字符）

**加入现有组织时的参数**:
- `organization_id`: 组织ID（必填）

**创建新组织时的参数**（必填）:
- `organization_name`: 组织名称（最大200字符）
- `organization_type`: 组织类型
  - `enterprise`: 企业
  - `university`: 大学
- `industry_or_discipline`: 行业/学科领域（最大100字符）

**组织用户权限和状态说明**:
1. **加入现有组织**：
   - `permission`: `pending`（待审核）
   - `status`: `pending`（待审核）
   - 需要组织管理员审核通过后才能正常使用

2. **创建新组织**：
   - `permission`: `owner`（所有者）
   - `status`: `pending`（待审核）
   - 用户成为新组织的创建者和所有者

#### 响应示例

**学生用户注册响应**:
```json
{
    "status": "success",
    "code": 201,
    "message": "注册成功",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "student123",
            "email": "student@example.com",
            "user_type": "student",
            "user_type_display": "学生",
            "avatar": "http://localhost:8000/media/avatars/default_student.svg",
            "is_active": true,
            "date_joined": "2024-01-20T10:30:00Z"
        },
        "student_profile": {
            "student_id": "2024001",
            "school": "北京大学",
            "major": "计算机科学与技术",
            "education_level": "本科",
            "grade": "2024"
        },
        "auth": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    },
    "error": {}
}
```

**组织用户注册响应（加入现有组织）**:
```json
{
    "status": "success",
    "code": 201,
    "message": "注册成功，等待组织管理员审核",
    "data": {
        "user": {
            "id": "660e8400-e29b-41d4-a716-446655440001",
            "username": "user123",
            "email": "user@company.com",
            "user_type": "organization",
            "user_type_display": "组织用户",
            "avatar": "http://localhost:8000/media/avatars/default_organization.svg",
            "is_active": true,
            "date_joined": "2024-01-20T10:30:00Z"
        },
        "organization_user": {
            "organization_id": 1,
            "organization_name": "科技有限公司",
            "position": "软件工程师",
            "department": "技术部",
            "permission": "pending",
            "status": "pending"
        },
        "auth": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    },
    "error": {}
}
```

**组织用户注册响应（创建新组织）**:
```json
{
    "status": "success",
    "code": 201,
    "message": "注册成功，新组织创建完成",
    "data": {
        "user": {
            "id": "770e8400-e29b-41d4-a716-446655440002",
            "username": "admin123",
            "email": "admin@newcompany.com",
            "user_type": "organization",
            "user_type_display": "组织用户",
            "avatar": "http://localhost:8000/media/avatars/default_organization.svg",
            "is_active": true,
            "date_joined": "2024-01-20T10:30:00Z"
        },
        "organization": {
            "id": 2,
            "name": "新科技公司",
            "organization_type": "enterprise",
            "industry_or_discipline": "人工智能",
            "status": "pending"
        },
        "organization_user": {
            "organization_id": 2,
            "organization_name": "新科技公司",
            "position": "技术总监",
            "department": "技术部",
            "permission": "owner",
            "status": "pending"
        },
        "auth": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    },
    "error": {}
}
```

### 3. 用户登录

**接口**: `POST /api/v1/auth/login/`
**描述**: 用户登录，支持密码登录和邮箱验证码登录
**权限**: 无需认证

#### 请求头
```
Content-Type: application/json
```

#### 请求参数

**密码登录**:
```json
{
    "type": "password",
    "username_or_email_or_phone": "user@example.com",
    "password": "password123"
}
```

**邮箱验证码登录**:
```json
{
    "type": "email-verification",
    "email": "user@example.com",
    "email_code": "123456"
}
```

**参数说明**:
- `type`: 登录类型（必填）
  - `password`: 密码登录
  - `email-verification`: 邮箱验证码登录
- `username_or_email_or_phone`: 用户名/邮箱/手机号（密码登录必填）
- `password`: 密码（密码登录必填）
- `email`: 邮箱地址（验证码登录必填）
- `email_code`: 邮箱验证码（验证码登录必填）

#### 响应示例（学生用户）
```json
{
    "status": "success",
    "code": 200,
    "message": "登录成功",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "user_20240120",
            "email": "user@example.com",
            "real_name": "张三",
            "phone": "13800138000",
            "avatar": "http://localhost:8000/media/avatars/default_student.svg",
            "gender": "male",
            "age": 20,
            "bio": "计算机科学专业学生",
            "user_type": "student",
            "is_active": true,
            "is_staff": false,
            "date_joined": "2024-01-15T08:00:00Z",
            "last_login": "2024-01-20T10:30:00Z",
            "student_profile": {
                "student_id": "2021001001",
                "school": "北京大学",
                "major": "计算机科学与技术",
                "grade": "2021",
                "education_level": "undergraduate",
                "education_level_display": "本科",
                "status": "approved",
                "status_display": "已认证",
                "expected_graduation": "2025-06-30",
                "interests": [
                    {"id": 1, "value": "人工智能"},
                    {"id": 2, "value": "机器学习"}
                ],
                "skills": [
                    {"id": 1, "post": "开发", "subclasses": "前端", "subdivision": "React"},
                    {"id": 2, "post": "开发", "subclasses": "后端", "subdivision": "Python"}
                ],
                "created_at": "2024-01-15T08:00:00Z",
                "updated_at": "2024-01-20T10:30:00Z"
            },
            "company_profile": null
        },
        "auth": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    },
    "error": {}
}
```

#### 响应示例（组织用户）
```json
{
    "status": "success",
    "code": 200,
    "message": "登录成功",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "username": "org_user_001",
            "email": "manager@company.com",
            "real_name": "李经理",
            "phone": "13900139000",
            "avatar": "http://localhost:8000/media/avatars/default_organization.svg",
            "gender": "female",
            "age": 35,
            "bio": "技术部门负责人",
            "user_type": "organization",
            "is_active": true,
            "is_staff": false,
            "date_joined": "2024-01-10T09:00:00Z",
            "last_login": "2024-01-20T11:00:00Z",
            "student_profile": null,
            "company_profile": {
                "position": "技术总监",
                "department": "技术部",
                "permission": "admin",
                "permission_display": "管理员",
                "status": "approved",
                "status_display": "已认证",
                "joined_at": "2024-01-10T09:00:00Z",
                "updated_at": "2024-01-20T11:00:00Z",
                "organization": {
                    "id": "org-001",
                    "name": "科技有限公司",
                    "code": "TECH001",
                    "leader_name": "王总",
                    "leader_title": "CEO",
                    "organization_type": "enterprise",
                    "organization_type_display": "企业",
                    "enterprise_type": "private",
                    "enterprise_type_display": "民营企业",
                    "university_type": null,
                    "university_type_display": null,
                    "industry_or_discipline": "信息技术",
                    "scale": "medium",
                    "scale_display": "中型企业",
                    "contact_person": "张秘书",
                    "contact_position": "行政助理",
                    "contact_phone": "010-12345678",
                    "contact_email": "contact@company.com",
                    "address": "北京市朝阳区科技园区",
                    "postal_code": "100000",
                    "description": "专注于人工智能技术的创新公司",
                    "website": "https://www.company.com",
                    "logo": "http://localhost:8000/media/logos/company_logo.png",
                    "status": "verified",
                    "status_display": "已认证",
                    "verified_at": "2024-01-15T14:00:00Z",
                    "established_date": "2020-01-01",
                    "created_at": "2024-01-10T09:00:00Z",
                    "updated_at": "2024-01-15T14:00:00Z"
                }
            }
        },
        "auth": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    },
    "error": {}
}
```

### 4. 邮箱验证码登录

**接口**: `POST /api/v1/auth/email-login/`
**描述**: 使用邮箱验证码登录
**权限**: 无需认证

#### 请求头
```
Content-Type: application/json
```

#### 请求参数
```json
{
    "email": "user@example.com",
    "email_code": "123456"
}
```

**参数说明**:
- `email`: 邮箱地址（必填）
- `email_code`: 邮箱验证码（必填，6位数字）

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "登录成功",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "username": "user_20240120",
            "email": "user@example.com",
            "real_name": "张三",
            "user_type": "student",
            "user_type_display": "学生",
            "avatar": "http://localhost:8000/media/avatars/default_student.svg",
            "is_active": true,
            "last_login": "2024-01-20T10:30:00Z"
        },
        "auth": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        }
    },
    "error": {}
}
```

#### 错误响应示例
```json
{
    "status": "error",
    "code": 422,
    "message": "验证失败",
    "data": {},
    "error": {
        "email_code": ["邮箱验证码无效或已过期"]
    }
}
```

### 5. 用户登出

**接口**: `POST /api/v1/auth/logout/`
**描述**: 用户登出，同时黑名单化访问令牌和刷新令牌
**权限**: 用户

#### 请求头
```
Authorization: Bearer <access_token>
X-Refresh-Token: <refresh_token>  # 可选，refresh_token的第三种传递方式
```

#### 请求参数
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Cookie参数（可选）
```
refresh_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### 参数说明
- **refresh_token**: 可选参数，支持多种传递方式（优先级从高到低）：
  1. **请求体**: JSON格式的`refresh_token`字段
  2. **Cookie**: 名为`refresh_token`的Cookie
  3. **请求头**: `X-Refresh-Token`请求头
  4. **智能兜底**: 如果都没有提供，系统会自动黑名单化用户的所有有效token

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "登出成功",
    "data": {},
    "error": {}
}
```

#### 安全机制
1. **双重保护**: 同时黑名单化当前请求的`access_token`和`refresh_token`
2. **多种支持**: 支持从请求体、Cookie、请求头获取`refresh_token`
3. **智能兜底**: 如果未提供`refresh_token`，自动黑名单化用户的所有有效token
4. **日志记录**: 记录登出操作日志，便于安全审计
5. **容错处理**: 即使部分token处理失败，仍确保登出成功

### 6. 验证令牌有效性

**接口**: `GET /api/v1/auth/verify/`
**描述**: 验证访问令牌是否有效
**权限**: 用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "user_20240120",
        "email": "user@example.com",
        "is_active": true
    },
    "error": {}
}
```

### 7. 刷新访问令牌

**接口**: `POST /api/v1/auth/refresh/`
**描述**: 使用刷新令牌获取新的访问令牌
**权限**: 用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 参数说明
- **refresh_token**: 必填，刷新令牌字符串
- 使用 `RefreshTokenSerializer` 进行参数验证
- 自动验证token格式和有效性

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    },
    "error": {}
}
```

#### 错误响应示例
```json
{
    "status": "error",
    "code": 422,
    "message": "验证失败",
    "data": {},
    "error": {
        "refresh_token": ["刷新令牌无效"]
    }
}
```

### 8. 修改密码

**接口**: `PUT /api/v1/auth/password/`
**描述**: 修改用户密码
**权限**: 用户

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 请求参数
```json
{
    "old_password": "OldPass123!",
    "new_password": "NewPass123!",
    "confirm_password": "NewPass123!"
}
```

**参数说明**:
- `old_password`: 当前密码（必填）
- `new_password`: 新密码（必填，8-20位，包含字母和数字）
- `confirm_password`: 确认新密码（必填，需与新密码一致）

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "密码修改成功",
    "data": {},
    "error": {}
}
```

### 9. 修改邮箱

**接口**: `PUT /api/v1/auth/change_email/`
**描述**: 修改用户邮箱地址
**权限**: 用户

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 请求参数
```json
{
    "email": "newemail@example.com",
    "email_code": "123456"
}
```

**参数说明**:
- `email`: 新邮箱地址（必填，格式验证）
- `email_code`: 邮箱验证码（必填，6位数字）

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "邮箱修改成功",
    "data": {
        "email": "newemail@example.com"
    },
    "error": {}
}
```

#### 说明
1. 需要先调用发送验证码接口，使用 `code_type: "change_email"` 向新邮箱发送验证码
2. 新邮箱不能与当前邮箱相同
3. 新邮箱不能被其他用户使用
4. 修改成功后会向旧邮箱发送通知邮件

### 10. 申请账户注销

**接口**: `POST /api/v1/auth/account/deletion/request/`
**描述**: 申请注销用户账户
**权限**: 用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
```json
{
    "password": "current_password",
    "reason": "不再使用该平台",
    "email_code": "123456",
    "confirm_deletion": true
}
```

#### 参数说明
- `password`: 当前账户密码（必填，用于身份验证）
- `reason`: 注销原因（可选，最大500字符）
- `email_code`: 邮箱验证码（必填，用于二次验证）
- `confirm_deletion`: 确认删除（必填，必须为true）

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "账户注销申请提交成功",
    "data": {
        "deletion_id": "12345",
        "scheduled_deletion_at": "2024-01-15T10:30:00Z",
        "message": "账户注销申请已提交，将在7天后执行删除操作。在此期间您可以取消注销申请。"
    },
    "error": {}
}
```

#### 安全机制
1. **多重验证**: 需要密码验证 + 邮箱验证码双重确认
2. **冷静期**: 7天冷静期，期间可以取消注销
3. **邮件通知**: 申请后立即发送确认邮件
4. **重复检查**: 防止重复提交注销申请
5. **操作记录**: 完整记录注销申请的操作日志

#### 说明
1. 需要先调用发送验证码接口，使用 `code_type: "delete_account"` 向当前邮箱发送验证码
2. 账户将在7天后自动删除，删除后无法恢复
3. 在冷静期内可以取消注销申请
4. 如果已有待处理的注销申请，将返回错误

### 11. 取消账户注销

**接口**: `POST /api/v1/auth/account/deletion/cancel/`
**描述**: 取消账户注销申请
**权限**: 用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
```json
{
    "password": "current_password"
}
```

#### 参数说明
- `password`: 当前账户密码（必填，用于身份验证）

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "账户注销申请已取消",
    "data": {
        "deletion_id": "12345",
        "cancelled_at": "2024-01-08T15:45:00Z"
    },
    "error": {}
}
```

#### 说明
1. 只能取消状态为"待处理"或"已批准"的注销申请
2. 取消后账户恢复正常使用状态
3. 会发送取消确认邮件

### 12. 查询账户注销状态

**接口**: `GET /api/v1/auth/account/deletion/status/`
**描述**: 查询当前用户的账户注销状态
**权限**: 用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应示例（有注销申请）
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "has_deletion_request": true,
        "deletion_request": {
            "id": "12345",
            "user_id": "user-uuid",
            "username": "testuser",
            "email": "user@example.com",
            "user_type": "student",
            "deletion_type": "user_request",
            "deletion_type_display": "用户主动注销",
            "reason": "不再使用该平台",
            "status": "pending",
            "status_display": "待处理",
            "requested_by": "user-uuid",
            "processed_by": null,
            "ip_address": "192.168.1.100",
            "is_data_anonymized": false,
            "requested_at": "2024-01-08T10:30:00Z",
            "processed_at": null,
            "scheduled_deletion_at": "2024-01-15T10:30:00Z",
            "actual_deletion_at": null
        }
    },
    "error": {}
}
```

#### 响应示例（无注销申请）
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "has_deletion_request": false,
        "message": "没有账户注销申请记录"
    },
    "error": {}
}
```

#### 状态说明
- `pending`: 待处理
- `approved`: 已批准
- `rejected`: 已拒绝
- `completed`: 已完成
- `cancelled`: 已取消

### 13. 请求密码重置

**接口**: `POST /api/v1/auth/reset/`
**描述**: 请求密码重置（发送重置验证码）
**权限**: 无需认证

#### 请求头
```
Content-Type: application/json
```

#### 请求参数
```json
{
    "email": "user@example.com"
}
```

**参数说明**:
- `email`: 邮箱地址（必填，格式验证）

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "重置验证码发送成功",
    "data": {
        "email": "user@example.com"
    },
    "error": {}
}
```

### 14. 重置密码

**接口**: `PUT /api/v1/auth/reset/confirm/`
**描述**: 使用验证码重置密码
**权限**: 无需认证

#### 请求头
```
Content-Type: application/json
```

#### 请求参数
```json
{
    "email": "user@example.com",
    "email_code": "123456",
    "new_password": "NewPass123!",
    "confirm_password": "NewPass123!"
}
```

**参数说明**:
- `email`: 邮箱地址（必填）
- `email_code`: 邮箱验证码（必填，6位数字）
- `new_password`: 新密码（必填，8-20位，包含字母和数字）
- `confirm_password`: 确认新密码（必填，需与新密码一致）

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "密码重置成功",
    "data": {},
    "error": {}
}
```



## 辅助接口

### 17. 验证邮箱验证码

**接口**: `POST /api/v1/auth/verify-email-code/`
**描述**: 验证邮箱验证码（不消费验证码）
**权限**: 无需认证

#### 请求头
```
Content-Type: application/json
```

#### 请求参数
```json
{
    "email": "user@example.com",
    "code": "123456",
    "code_type": "register"
}
```

#### 参数说明
- `email`: 邮箱地址（必填）
- `code`: 验证码（必填）
- `code_type`: 验证码类型（必填）
  - `register`: 注册验证码
  - `login`: 登录验证码
  - `reset_password`: 重置密码验证码
  - `change_email`: 修改邮箱验证码
  - `delete_account`: 账户注销验证码

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "验证码验证成功",
    "data": {
        "message": "验证码验证成功"
    },
    "error": {}
}
```

### 18. 检查邮箱是否存在

**接口**: `GET /api/v1/auth/check-email/`
**描述**: 检查邮箱是否已注册
**权限**: 无需认证

#### 请求参数
- `email`: 邮箱地址（URL参数）

#### 请求示例
```
GET /api/v1/auth/check-email/?email=user@example.com
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "exists": true
    },
    "error": {}
}
```

### 19. 检查用户名是否存在

**接口**: `GET /api/v1/auth/check-username/`
**描述**: 检查用户名是否已存在
**权限**: 无需认证

#### 请求参数
- `username`: 用户名（URL参数）

#### 请求示例
```
GET /api/v1/auth/check-username/?username=testuser
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "exists": false
    },
    "error": {}
}
```

### 20. 获取登录日志

**接口**: `GET /api/v1/auth/login-logs/`
**描述**: 获取当前用户的登录日志
**权限**: 用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": [
        {
            "id": 1,
            "user_info": {
                "username": "testuser",
                "real_name": "张三",
                "user_type": "学生"
            },
            "login_type": "password",
            "login_type_display": "密码登录",
            "ip_address": "192.168.1.100",
            "user_agent": "Mozilla/5.0...",
            "is_success": true,
            "failure_reason": null,
            "created_at": "2024-01-20T10:30:00Z"
        }
    ],
    "error": {}
}
```

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 422 | 验证失败 |
| 429 | 请求过于频繁 |
| 500 | 服务器内部错误 |

### 常见错误信息

#### 注册相关
- "邮箱已被注册"
- "用户名已存在"
- "验证码错误或已过期"
- "密码格式不正确"
- "组织名称已存在"
- "组织代码已存在"
- "学号已存在"

#### 登录相关
- "用户名或密码错误"
- "账户已被禁用"
- "验证码错误"
- "用户不存在"

#### 令牌相关
- "令牌无效"
- "令牌已过期"
- "刷新令牌无效"
- "认证凭据未提供"

#### 密码相关
- "原密码错误"
- "新密码不能与原密码相同"
- "密码格式不正确"
- "两次输入的密码不一致"



#### 账户注销相关
- "账户注销申请不存在"
- "账户注销申请已取消"
- "验证码类型错误"

#### 邮箱相关
- "邮箱格式不正确"
- "新邮箱不能与当前邮箱相同"
- "邮箱验证码发送失败"

## 注意事项

1. **安全性**
   - 所有密码在传输和存储时都经过加密处理
   - 验证码有效期为5分钟
   - 登录失败次数过多会触发账户锁定
   - 建议使用HTTPS协议进行API调用
   - 敏感操作需要验证码确认

2. **令牌管理**
   - 访问令牌有效期为7天
   - 刷新令牌有效期为14天
   - 令牌应安全存储，避免泄露
   - 退出登录时应调用登出接口清理令牌
   - 令牌过期后需要使用刷新令牌获取新的访问令牌

3. **验证码**
   - 每个邮箱每分钟最多发送1次验证码
   - 验证码为6位数字
   - 验证码使用后即失效
   - 同一邮箱同一类型的验证码同时只能有一个有效
   - 支持多种验证码类型：注册、登录、重置密码、修改邮箱、账户注销

4. **组织用户**
   - 组织用户注册后状态为 `pending`，需要在组织应用中完成认证
   - 支持企业和大学两种组织类型
   - 创建新组织时用户权限为 `owner`，加入现有组织时权限为 `pending`
   - 组织认证功能在组织应用中实现，详见组织应用API文档

5. **用户状态**
   - 学生用户注册后状态为 `approved`，可直接使用
   - 组织用户注册后状态为 `pending`，需要认证
   - 用户状态影响功能访问权限

6. **数据验证**
   - 邮箱格式必须正确
   - 用户名和邮箱不能重复
   - 密码必须符合安全要求（8-20位，包含字母和数字）
   - 组织代码和组织名称不能重复

7. **账户注销**
   - 账户注销需要邮箱验证码确认
   - 注销申请可以取消
   - 注销后数据不可恢复

## 示例代码

### JavaScript (Fetch API)

```javascript
// 发送邮箱验证码
const sendEmailCode = async (email, codeType) => {
    const response = await fetch('/api/v1/auth/send-email-code/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            code_type: codeType
        })
    });
    return await response.json();
};

// 学生用户注册
const registerStudent = async (userData) => {
    const response = await fetch('/api/v1/auth/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: userData.username,
            email: userData.email,
            email_code: userData.email_code,
            password: userData.password,
            user_type: 'student',
            real_name: userData.real_name,
            student_id: userData.student_id,
            university: userData.university,
            major: userData.major,
            grade: userData.grade
        })
    });
    return await response.json();
};

// 组织用户注册（创建新组织）
const registerOrganizationNew = async (userData) => {
    const response = await fetch('/api/v1/auth/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: userData.username,
            email: userData.email,
            email_code: userData.email_code,
            password: userData.password,
            user_type: 'organization',
            real_name: userData.real_name,
            organization_name: userData.organization_name,
            organization_type: userData.organization_type,
            industry_or_discipline: userData.industry_or_discipline,
            position: userData.position,
            department: userData.department
        })
    });
    return await response.json();
};

// 密码登录
const loginWithPassword = async (identifier, password) => {
    const response = await fetch('/api/v1/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            identifier: identifier,
            password: password,
            login_type: 'password'
        })
    });
    return await response.json();
};

// 邮箱验证码登录
const loginWithEmailCode = async (email, emailCode) => {
    const response = await fetch('/api/v1/auth/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            identifier: email,
            email_code: emailCode,
            login_type: 'email_code'
        })
    });
    return await response.json();
};

// 刷新令牌
const refreshToken = async (refreshToken) => {
    const response = await fetch('/api/v1/auth/refresh/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            refresh: refreshToken
        })
    });
    return await response.json();
};



// 验证令牌
const verifyToken = async (token) => {
    const response = await fetch('/api/v1/auth/verify/', {
        method: 'GET',
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
    return await response.json();
};
```

### Python (requests)

```python
import requests

# 发送邮箱验证码
def send_email_code(email, code_type):
    response = requests.post(
        'http://localhost:8000/api/v1/auth/send-email-code/',
        json={
            'email': email,
            'code_type': code_type
        }
    )
    return response.json()

# 学生用户注册
def register_student(user_data):
    response = requests.post(
        'http://localhost:8000/api/v1/auth/register/',
        json={
            'username': user_data['username'],
            'email': user_data['email'],
            'email_code': user_data['email_code'],
            'password': user_data['password'],
            'user_type': 'student',
            'real_name': user_data['real_name'],
            'student_id': user_data['student_id'],
            'university': user_data['university'],
            'major': user_data['major'],
            'grade': user_data['grade']
        }
    )
    return response.json()

# 组织用户注册（创建新组织）
def register_organization_new(user_data):
    response = requests.post(
        'http://localhost:8000/api/v1/auth/register/',
        json={
            'username': user_data['username'],
            'email': user_data['email'],
            'email_code': user_data['email_code'],
            'password': user_data['password'],
            'user_type': 'organization',
            'real_name': user_data['real_name'],
            'organization_name': user_data['organization_name'],
            'organization_type': user_data['organization_type'],
            'industry_or_discipline': user_data['industry_or_discipline'],
            'position': user_data['position'],
            'department': user_data['department']
        }
    )
    return response.json()

# 密码登录
def login_with_password(identifier, password):
    response = requests.post(
        'http://localhost:8000/api/v1/auth/login/',
        json={
            'identifier': identifier,
            'password': password,
            'login_type': 'password'
        }
    )
    return response.json()

# 邮箱验证码登录
def login_with_email_code(email, email_code):
    response = requests.post(
        'http://localhost:8000/api/v1/auth/login/',
        json={
            'identifier': email,
            'email_code': email_code,
            'login_type': 'email_code'
        }
    )
    return response.json()

# 刷新令牌
def refresh_token(refresh_token):
    response = requests.post(
        'http://localhost:8000/api/v1/auth/refresh/',
        json={
            'refresh': refresh_token
        }
    )
    return response.json()

# 验证令牌
def verify_token(token):
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.get(
        'http://localhost:8000/api/v1/auth/verify/',
        headers=headers
    )
    return response.json()
```