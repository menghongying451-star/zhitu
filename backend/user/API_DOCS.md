ming'ming'weimingmingwei# 校企对接平台 - 用户管理API文档

## 概述

本文档描述了校企对接平台用户管理相关API接口，主要包括用户资料管理和头像上传功能。

**注意**: 用户认证相关功能（注册、登录、密码管理等）已迁移至 `authentication` 应用，请参考 `authentication/API_DOCS.md`。

## 基础信息

- **基础URL**: `/api/v1/user/`
- **认证方式**: JWT Bearer Token
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
    "code": 422,
    "message": "验证失败",
    "data": {},
    "error": {
        "field_name": ["错误信息"]
    }
}
```

## 用户类型说明

系统支持两种主要用户类型：

1. **student**: 学生用户
   - 拥有独立的学生资料表（Student模型）
   - 包含学籍信息、技能、兴趣等字段

2. **company**: 企业用户
   - 拥有独立的企业资料表（Company模型）
   - 包含企业信息、联系方式、认证状态等字段

## API接口

### 1. 获取用户资料

**接口**: `GET /api/v1/user/profile/`
**描述**: 获取当前用户的详细资料信息
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应示例

**学生用户响应**:
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "student2024",
        "email": "student@example.com",
        "phone": "13800138000",
        "real_name": "张三",
        "avatar": "http://localhost:8000/media/avatars/student_avatar.jpg",
        "gender": "male",
        "birth_date": "2000-01-01",
        "bio": "计算机科学专业学生，热爱编程",
        "user_type": "student",
        "user_type_display": "学生",
        "date_joined": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-02T10:30:00Z",
        "is_active": true,
        "student_profile": {
            "student_id": "2024001001",
            "school": "清华大学",
            "major": "计算机科学与技术",
            "grade": "2024",
            "enrollment_year": 2024,
            "expected_graduation_year": 2028,
            "gpa": 3.8,
            "skills": ["Python", "Java", "JavaScript", "React"],
            "interests": ["人工智能", "Web开发", "数据科学"],
            "resume": "http://localhost:8000/media/resumes/student_resume.pdf",
            "portfolio_url": "https://github.com/student2024",
            "linkedin_url": "https://linkedin.com/in/student2024",
            "github_url": "https://github.com/student2024",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T10:30:00Z"
        }
    },
    "error": {}
}
```

**企业用户响应**:
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "username": "company2024",
        "email": "hr@company.com",
        "phone": "13900139000",
        "real_name": "李经理",
        "avatar": "http://localhost:8000/media/avatars/company_avatar.jpg",
        "gender": "female",
        "birth_date": "1985-05-15",
        "bio": "负责公司人力资源管理",
        "user_type": "company",
        "user_type_display": "企业",
        "date_joined": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-02T10:30:00Z",
        "is_active": true,
        "organization_profile": {
            "organization": {
                "id": 1,
                "name": "北京科技有限公司",
                "code": "BJ001",
                "organization_type": "enterprise",
                "organization_type_display": "企业",
                "industry_or_discipline": "信息技术",
                "status": "verified",
                "status_display": "已认证"
            },
            "permission": "admin",
            "permission_display": "管理员",
            "status": "active",
            "status_display": "活跃",
            "position": "人力资源经理",
            "department": "人事部",
            "phone": "010-12345678",
            "email": "hr@company.com",
            "notes": "负责校园招聘",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T10:30:00Z"
        }
    },
    "error": {}
}
```

### 2. 更新用户资料

**接口**: `PUT /api/v1/user/update-profile/`
**描述**: 更新用户资料信息
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数

**基础用户信息**:
```json
{
    "real_name": "张三丰",
    "phone": "13800138001",
    "gender": "male",
    "birth_date": "2000-01-01",
    "bio": "更新后的个人简介"
}
```

**学生用户额外字段**:
```json
{
    "real_name": "张三丰",
    "phone": "13800138001",
    "gender": "male",
    "birth_date": "2000-01-01",
    "bio": "计算机科学专业学生",
    "student_profile": {
        "school": "北京大学",
        "major": "软件工程",
        "grade": "2024",
        "enrollment_year": 2024,
        "expected_graduation_year": 2028,
        "gpa": 3.9,
        "skills": ["Python", "Java", "React", "Vue"],
        "interests": ["机器学习", "前端开发"],
        "portfolio_url": "https://portfolio.example.com",
        "linkedin_url": "https://linkedin.com/in/zhangsan",
        "github_url": "https://github.com/zhangsan"
    }
}
```

#### 参数说明
- `real_name`: 真实姓名
- `phone`: 手机号码
- `gender`: 性别 (`male`, `female`, `other`)
- `birth_date`: 出生日期 (YYYY-MM-DD格式)
- `bio`: 个人简介
- `student_profile`: 学生资料（仅学生用户）
  - `school`: 学校名称
  - `major`: 专业
  - `grade`: 年级
  - `enrollment_year`: 入学年份
  - `expected_graduation_year`: 预期毕业年份
  - `gpa`: 绩点
  - `skills`: 技能列表
  - `interests`: 兴趣列表
  - `portfolio_url`: 作品集链接
  - `linkedin_url`: LinkedIn链接
  - `github_url`: GitHub链接

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "资料更新成功",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "student2024",
        "email": "student@example.com",
        "phone": "13800138001",
        "real_name": "张三丰",
        "avatar": "http://localhost:8000/media/avatars/student_avatar.jpg",
        "gender": "male",
        "birth_date": "2000-01-01",
        "bio": "计算机科学专业学生",
        "user_type": "student",
        "user_type_display": "学生",
        "date_joined": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-02T10:30:00Z",
        "is_active": true,
        "student_profile": {
            "student_id": "2024001001",
            "school": "北京大学",
            "major": "软件工程",
            "grade": "2024",
            "enrollment_year": 2024,
            "expected_graduation_year": 2028,
            "gpa": 3.9,
            "skills": ["Python", "Java", "React", "Vue"],
            "interests": ["机器学习", "前端开发"],
            "resume": "http://localhost:8000/media/resumes/student_resume.pdf",
            "portfolio_url": "https://portfolio.example.com",
            "linkedin_url": "https://linkedin.com/in/zhangsan",
            "github_url": "https://github.com/zhangsan",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T15:45:00Z"
        }
    },
    "error": {}
}
```

### 3. 获取兴趣标签

**接口**: `GET /api/v1/user/tags/interests/`
**描述**: 获取所有兴趣标签，支持搜索功能
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
- `search` (可选): 搜索关键词，支持模糊匹配标签内容

#### 请求示例
```
GET /api/v1/user/tags/interests/?search=机器学习
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
            "value": "机器学习"
        },
        {
            "id": 2,
            "value": "深度学习"
        }
    ],
    "error": {}
}
```

### 4. 获取能力标签

**接口**: `GET /api/v1/user/tags/abilities/`
**描述**: 获取所有level=2的能力标签，支持搜索功能
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
- `search` (可选): 搜索关键词，支持在category、subcategory、specialty字段中模糊匹配

#### 请求示例
```
GET /api/v1/user/tags/abilities/?search=java
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": [
        {
            "id": 10401,
            "post": "互联网-java",
            "category": "互联网",
            "subcategory": "java",
            "specialty": null,
            "level": 1
        },
        {
            "id": 10402,
            "post": "互联网-java-前端",
            "category": "互联网",
            "subcategory": "java",
            "specialty": "前端",
            "level": 2
        }
    ],
    "error": {}
}
```

### 5. 模糊搜索标签

**接口**: `GET /api/v1/user/tags/search/`
organization_id

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
- `query` (必需): 搜索关键词，支持模糊匹配
  - 对于兴趣标签：在value字段中搜索
  - 对于能力标签：在category、subcategory、specialty字段中搜索

#### 请求示例
```
GET /api/v1/user/tags/search/?query=学
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "tag1": [
            {
                "id": 1,
                "value": "机器学习"
            },
            {
                "id": 2,
                "value": "深度学习"
            }
        ],
        "tag2": [
            {
                "id": 10404,
                "post": "互联网-机器学习",
                "category": "互联网",
                "subcategory": "机器学习",
                "specialty": null,
                "level": 1
            }
        ],
        "total_count": {
            "tag1_count": 2,
            "tag2_count": 1,
            "total": 3
        }
    },
    "error": {}
}
```

#### 错误响应示例
```json
{
    "status": "error",
    "code": 400,
    "message": "请提供搜索关键词",
    "data": {},
    "error": {}
}
```

### 6. 上传用户头像

**接口**: `POST /api/v1/user/upload-avatar/`
**描述**: 上传用户头像图片
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### 请求参数
- `avatar`: 头像文件（图片格式：jpg, jpeg, png, gif）

#### 文件要求
- **格式**: JPG, JPEG, PNG, GIF
- **大小**: 最大5MB
- **尺寸**: 建议正方形，最小100x100像素

#### 请求示例 (multipart/form-data)
```
POST /api/v1/user/upload-avatar/
Content-Type: multipart/form-data

avatar: [binary file data]
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "头像上传成功",
    "data": {
        "avatar": "http://localhost:8000/media/avatars/user_550e8400_avatar_20240102_154530.jpg",
        "message": "头像上传成功"
    },
    "error": {}
}
```

#### 错误响应示例
```json
{
    "status": "error",
    "code": 400,
    "message": "请选择要上传的头像文件",
    "data": {},
    "error": {}
}
```

```json
{
    "status": "error",
    "code": 422,
    "message": "验证失败",
    "data": {},
    "error": {
        "avatar": ["文件大小不能超过5MB"]
    }
}
```

## 错误响应格式

所有错误响应都遵循以下格式：

```json
{
    "success": false,
    "message": "错误描述",
    "errors": {
        "field_name": ["具体错误信息"]
    }
}
```

## 状态码说明

- `200`: 请求成功
- `201`: 创建成功
- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `429`: 请求过于频繁
- `500`: 服务器内部错误

## 用户类型说明

- `student`: 学生
- `company`: 企业
- `admin`: 管理员

## 注意事项

1. 邮箱验证码有效期为5分钟
2. 同一邮箱60秒内只能发送一次验证码
3. JWT Access Token有效期为7天
4. JWT Refresh Token有效期为14天
5. 密码必须至少8位，包含大小写字母、数字、特殊字符中的至少两种
6. 用户名只能包含字母、数字、下划线，长度3-30位
7. 手机号必须是11位数字