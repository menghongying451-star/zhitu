# 校企对接平台 - 组织管理API文档

## 概述

本文档描述了校企对接平台的组织管理相关API接口，包括组织认证、组织详情查看、成员管理、操作日志、配置管理等功能。

## 基础信息

- **基础URL**: `/api/v1/organization/`
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

## 组织管理接口

### 1. 组织认证材料提交

#### 接口信息
- **URL**: `/api/v1/organization/verification/submit/`
- **方法**: `POST`
- **描述**: 新组织创建者提交组织认证材料
- **权限**: 需要登录，仅限组织用户

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 请求参数
```json
{
    "code": "91110000000000000X",
    "leader_name": "张三",
    "leader_title": "总经理",

    "contact_person": "李四",
    "contact_position": "人事经理",
    "contact_phone": "010-12345678",
    "contact_email": "contact@example.com",
    "address": "北京市朝阳区某某街道123号",
    "postal_code": "100000",
    "description": "公司简介",
    "website": "https://www.example.com",
    "established_date": "2020-01-01",
    "enterprise_type": "private",
    "university_type": null
}
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "认证材料提交成功，请等待审核",
    "data": {
        "message": "认证材料提交成功，请等待审核",
        "organization_status": "under_review",
        "user_status": "pending"
    },
    "error": {}
}
```

### 2. 组织认证材料和图片提交（新接口）

#### 接口信息
- **URL**: `/api/v1/organization/verification/submit-with-images/`
- **方法**: `POST`
- **描述**: 新组织创建者一次性提交组织认证材料和认证图片（合并接口）
- **权限**: 需要登录，仅限组织用户（owner权限）
- **内容类型**: `multipart/form-data`

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### 请求参数（form-data格式）

**文本字段：**
- `code`: 组织代码（必填）
- `leader_name`: 负责人姓名（必填）
- `leader_title`: 负责人职务（必填）

- `contact_person`: 联系人姓名（必填）
- `contact_position`: 联系人职务
- `contact_phone`: 联系电话（必填）
- `contact_email`: 联系邮箱（必填）
- `address`: 地址（必填）
- `postal_code`: 邮政编码
- `description`: 组织描述
- `website`: 官方网站
- `established_date`: 成立日期（YYYY-MM-DD格式）

**企业特定字段：**
- `enterprise_type`: 企业类型（当organization_type为enterprise时必填）
  - 可选值：`state_owned`（国有企业）、`private`（民营企业）、`foreign`（外资企业）、`joint_venture`（合资企业）、`other`（其他）

**学校特定字段：**
- `university_type`: 学校类型（当organization_type为university时必填）
  - 可选值：`985`、`211`、`double_first_class`（双一流）、`undergraduate`（本科院校）、`vocational`（职业院校）、`other`（其他）

**其他组织特定字段（根据组织类型动态必填）：**
- `other_type`: 其他组织类型（当organization_type为other时必填）
  - **可选值：** government(政府机构)、ngo(非营利组织)、foundation(基金会)、association(行业协会)、research_institute(科研院所)、hospital(医疗机构)、media(媒体机构)、cultural(文化机构)、sports(体育组织)、religious(宗教组织)、international(国际组织)、community(社区组织)、cooperative(合作社)、union(工会组织)、chamber(商会)、other(其他未分类)
- `organization_nature`: 组织性质
  - **可选值：** public(公立/公办)、private(私立/民办)、joint(公私合营)、international(国际性)、regional(地区性)、national(全国性)
- `business_scope`: 业务范围（文本字段，描述组织的主要业务范围或服务领域）
- `regulatory_authority`: 监管机构（条件必填，文本字段）
  - **必填条件：** 政府机构(government)、社会团体(ngo)、基金会(foundation)
  - **说明：** 如民政部、卫健委、教育部等
- `license_info`: 许可证信息（条件必填，文本字段）
  - **必填条件：** 医院(hospital)、研究机构(research_institute)
  - **说明：** 相关的许可证号、资质证书等信息
- `service_target`: 服务对象（条件必填）
  - **必填条件：** 协会(association)、商会(chamber)、工会(union)
  - **可选值：** public(面向公众)、members(面向会员)、industry(面向行业)、government(面向政府)、enterprises(面向企业)、students(面向学生)、patients(面向患者)、community(面向社区)、other(其他)

**图片文件字段：**
- `verification_image_1`: 认证图片1（必填，文件格式：JPEG/PNG/GIF/WebP，大小限制：10MB）
- `verification_image_2`: 认证图片2（可选）
- `verification_image_3`: 认证图片3（可选）
- `verification_image_4`: 认证图片4（可选）
- `verification_image_5`: 认证图片5（可选）

#### 请求示例（使用curl）
```bash
curl -X POST \
  http://localhost:8000/api/v1/organization/verification/submit-with-images/ \
  -H 'Authorization: Bearer <access_token>' \
  -F 'code=91110000000000000X' \
  -F 'leader_name=张三' \
  -F 'leader_title=总经理' \

  -F 'contact_person=李四' \
  -F 'contact_position=人事经理' \
  -F 'contact_phone=010-12345678' \
  -F 'contact_email=contact@example.com' \
  -F 'address=北京市朝阳区某某街道123号' \
  -F 'postal_code=100000' \
  -F 'description=公司简介' \
  -F 'website=https://www.example.com' \
  -F 'established_date=2020-01-01' \
  -F 'enterprise_type=private' \
  -F 'verification_image_1=@/path/to/image1.jpg' \
  -F 'verification_image_2=@/path/to/image2.jpg'
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "认证材料和图片提交成功，请等待审核",
    "data": {
        "message": "认证材料和图片提交成功，请等待审核",
        "organization_status": "under_review",
        "verification_image": [
            "http://localhost:8000/media/organization/verification_images/123/verification_123_1.jpg",
            "http://localhost:8000/media/organization/verification_images/123/verification_123_2.jpg"
        ],
        "image_count": 2
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
        "verification_image_1": ["第一张认证图片文件大小不能超过10MB"],
        "missing_fields": ["code", "leader_name"],
        "message": "请填写必填字段: 组织代码, 负责人姓名"
    }
}
```

#### 不同组织类型的字段要求

**政府机构（government）、社会团体（ngo）、基金会（foundation）：**
- 额外必填字段：`regulatory_authority`（监管机构）
- 示例：民政部、卫健委、教育部等

**医院（hospital）、研究机构（research_institute）：**
- 额外必填字段：`license_info`（许可证信息）
- 示例：医疗机构执业许可证号、科研资质证书等

**协会（association）、商会（chamber）、工会（union）：**
- 额外必填字段：`service_target`（服务对象）
- 可选值：`public`（面向公众）、`members`（面向会员）、`industry`（面向行业）、`government`（面向政府）、`enterprises`（面向企业）、`students`（面向学生）、`patients`（面向患者）、`community`（面向社区）、`other`（其他）

**其他组织类型：**
- 只需要填写基础必填字段：`code`、`leader_name`、`contact_phone`、`contact_email`、`address`

#### 注意事项

1. **文件上传要求**：
   - 支持的图片格式：JPEG、PNG、GIF、WebP
   - 单个文件大小限制：10MB
   - 图片数量：1-5张（第一张必填）
   - 字段名称：`verification_image_1` 到 `verification_image_5`

2. **请求格式**：
   - 必须使用 `multipart/form-data` 格式
   - 文本字段和文件字段可以在同一个请求中提交

3. **字段验证**：
   - 系统会根据组织的 `other_type` 字段自动判断哪些字段为必填
   - 如果缺少必填字段，会返回详细的错误信息

4. **兼容性**：
   - 此接口整合了原有的 `submit-materials` 和 `upload-images` 功能
   - 原有接口仍然保持可用以确保向后兼容

5. **事务安全**：
   - 所有数据更新在同一个事务中完成
   - 如果任何步骤失败，所有更改都会回滚

6. **状态变更**：
   - 提交成功后，组织状态将变更为"under_review"（审核中）

### 3. 组织认证状态查询

#### 接口信息
- **URL**: `/api/v1/organization/verification/status/`
- **方法**: `GET`
- **描述**: 查询组织认证状态和进度
- **权限**: 需要登录

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
        "user_type": "organization",
        "needs_verification": false,
        "user_status": "active",
        "user_status_display": "正常",
        "organization_status": "verified",
        "organization_status_display": "已认证",
        "organization_name": "测试企业",
        "organization_type": "enterprise",
        "organization_id": 1,
        "is_admin": true,
        "verification_progress": {
            "basic_info_completed": true,
            "contact_info_completed": true,
            "address_completed": true,
            "leader_info_completed": true,
            "code_completed": true
        }
    },
    "error": {}
}
```

### 3. 组织用户状态查询

#### 接口信息
- **URL**: `/api/v1/organization/user/status/`
- **方法**: `GET`
- **描述**: 查询用户在组织中的详细状态信息
- **权限**: 需要登录

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
        "id": 1,
        "username": "john_doe",
        "email": "john.doe@example.com",
        "user_type": "organization",
        "status": "approved",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "last_login": "2024-01-02T10:30:00Z",
        "organization_info": {
            "organization_id": 1,
            "organization_name": "科技创新有限公司",
            "organization_type": "enterprise",
            "organization_status": "verified",
            "organization_status_display": "已认证",
            "user_permission": "admin",
            "user_permission_display": "管理员",
            "user_status": "active",
            "user_status_display": "正常",
            "department": "技术部",
            "position": "技术总监",
            "joined_at": "2024-01-01T00:00:00Z",
            "is_verified": true
        }
    },
    "error": {}
}
```

### 4. 搜索组织

**接口**: `GET /api/v1/organization/search/`
**描述**: 搜索组织列表，支持分页和多种过滤条件
**权限**: 无需认证（公开接口）

#### 查询参数
- `search` 或 `q` (可选): 搜索关键词，支持组织名称、代码、行业/学科搜索，至少2个字符
- `organization_type` 或 `type` (可选): 组织类型过滤 (`enterprise`, `university`)
- `status` (可选): 组织状态过滤 (`pending`, `verified`, `rejected`, `suspended`)
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20

#### 请求示例
```
GET /api/v1/organization/search/?search=科技&organization_type=enterprise&status=verified&page=1&page_size=10
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "results": [
            {
                "id": "1",
                "name": "北京科技有限公司",
                "organization_type": "enterprise",
                "organization_type_display": "企业",
                "type_display": "科技企业",
                "industry_or_discipline": "信息技术",
                "scale": "中型企业",
                "address": "北京市海淀区中关村大街1号",
                "status": "verified",
                "status_display": "已认证",
                "logo": "http://localhost:8000/media/organization_logos/logo.png"
            },
            {
                "id": "2",
                "name": "上海科技大学",
                "organization_type": "university",
                "organization_type_display": "大学",
                "type_display": "研究型大学",
                "industry_or_discipline": "综合",
                "scale": "大型",
                "address": "上海市浦东新区华夏中路393号",
                "status": "verified",
                "status_display": "已认证",
                "logo": "http://localhost:8000/media/organization_logos/university_logo.png"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "total_count": 48,
            "page_size": 10,
            "has_next": true,
            "has_previous": false
        },
        "query": "科技",
        "filters": {
            "organization_type": "enterprise",
            "status": "verified"
        }
    },
    "error": {}
}
```

#### 错误响应
```json
{
    "status": "error",
    "code": 400,
    "message": "搜索关键词至少需要2个字符",
    "data": {},
    "error": {}
}
```

#### 参数说明
- **search/q**: 搜索关键词，会在组织名称、代码、行业/学科字段中进行模糊匹配
- **organization_type/type**: 
  - `enterprise`: 企业组织
  - `university`: 大学组织
- **status**: 
  - `pending`: 待审核
  - `verified`: 已认证
  - `rejected`: 已拒绝
  - `suspended`: 已暂停
- **返回字段说明**:
  - `status`: 组织状态，包含所有状态的组织（不再限制只返回已认证组织）
  - `status_display`: 状态的中文显示名称
  - 其他字段与组织详情接口相同

### 2. 获取组织详细信息

**接口**: `GET /api/v1/organization/<int:organization_id>/detail/`
**描述**: 获取指定组织的详细信息
**权限**: 无需认证（公开信息），认证用户可获取更多信息

#### 路径参数
- `organization_id`: 组织ID（整数）

#### 响应示例

**公开用户响应**:
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "organization": {
            "id": "1",
            "name": "北京科技有限公司",
            "code": "BJ001",
            "organization_type": "enterprise",
            "organization_type_display": "企业",
            "type_display": "科技企业",
            "industry_or_discipline": "信息技术",
            "scale": "中型企业",
            "address": "北京市海淀区中关村大街1号",
            "postal_code": "100080",
            "description": "专注于人工智能技术研发的科技企业",
            "website": "https://www.example.com",
            "established_date": "2020-01-01",
            "logo": "http://localhost:8000/media/organization_logos/logo.png",
            "status": "verified",
            "status_display": "已认证",
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z",
            "enterprise_type": "private",
            "enterprise_type_display": "民营企业",

        },
        "contact_info": {
            "contact_person": "张经理",
            "contact_phone": "010-12345678",
            "contact_email": "contact@example.com"
        },
        "leader_info": {
            "leader_name": "李总",
            "leader_title": "总经理"
        }
    },
    "error": {}
}
```

**组织成员响应（包含额外统计信息）**:
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "organization": { /* 同上 */ },
        "contact_info": { /* 同上 */ },
        "leader_info": { /* 同上 */ },
        "member_stats": {
            "total_members": 25,
            "pending_members": 3,
            "user_role": "admin",
            "user_role_display": "管理员",
            "user_status": "active",
            "user_status_display": "活跃",
            "user_position": "技术总监",
            "user_department": "研发部"
        }
    },
    "error": {}
}
```

#### 错误响应
```json
{
    "status": "error",
    "code": 404,
    "message": "组织不存在或未认证",
    "data": {},
    "error": {}
}
```

### 2. 获取组织成员列表

**接口**: `GET /api/v1/organization/members/`
**描述**: 获取当前用户所属组织的成员列表
**权限**: 组织成员

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 查询参数
- `status` (可选): 成员状态过滤 (`pending`, `approved`, `rejected`)
- `permission` (可选): 权限过滤 (`owner`, `admin`, `member`)
- `search` (可选): 搜索关键词（用户名、真实姓名、邮箱、职位、部门）
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20

#### 请求示例
```
GET /api/v1/organization/members/?status=approved&permission=admin&search=张&page=1&page_size=10
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "members": [
            {
                "id": 1,
                "username": "zhangsan",
                "real_name": "张三",
                "phone": "138****8001",
                "email": "zhan****@example.com",
                "department": "研发部",
                "position": "技术总监",
                "permission": "admin",
                "status": "approved",
                "created_at": "2024-01-01T00:00:00Z"
            },
            {
                "id": 2,
                "username": "lisi",
                "real_name": "李四",
                "phone": "139****9002",
                "email": "li****@example.com",
                "department": "产品部",
                "position": "产品经理",
                "permission": "member",
                "status": "approved",
                "created_at": "2024-01-02T00:00:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 3,
            "total_count": 25,
            "page_size": 10,
            "has_next": true,
            "has_previous": false
        }
    },
    "error": {}
}
```

#### 字段说明
- `id`: 组织用户ID
- `username`: 用户名
- `real_name`: 真实姓名（非管理员查看时会脱敏）
- `phone`: 电话号码（非管理员查看时会脱敏）
- `email`: 邮箱地址（非管理员查看时会脱敏）
- `department`: 部门
- `position`: 职位
- `permission`: 权限（owner/admin/member）
- `status`: 状态（pending/approved/rejected）
- `created_at`: 创建时间

### 3. 更新组织成员信息

**接口**: `PUT /api/v1/organization/members/<int:member_id>/update/`
**描述**: 更新指定成员的权限、状态和认证信息
**权限**: 组织管理员或所有者

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 路径参数
- `member_id`: 成员ID（整数）

#### 请求参数
```json
{
    "permission": "member",
    "status": "approved"
}
```

#### 参数说明
- `permission`: 权限级别 (`owner`, `admin`, `member`, `pending`)
- `status`: 成员状态 (`pending`, `approved`, `rejected`)

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "成员信息更新成功",
    "data": {
        "id": "uuid-1",
        "username": "zhangsan",
        "real_name": "张三",
        "phone": "138****8002",
        "email": "zhang***@example.com",
        "department": "技术部",
        "position": "高级工程师",
        "permission": "member",
        "status": "approved",
        "created_at": "2024-01-01T00:00:00Z"
    },
    "error": {}
}
```

### 4. 批量更新成员状态

**接口**: `POST /api/v1/organization/members/batch-update/`
**描述**: 批量更新多个成员的状态
**权限**: 组织管理员或所有者

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
```json
{
    "member_ids": [1, 2, 3, 4],
    "action": "approve"
}
```

#### 参数说明
- `member_ids`: 成员ID数组
- `action`: 操作类型
  - `approve`: 批准（状态改为approved）
  - `reject`: 拒绝（状态改为rejected）
  - `suspend`: 暂停（状态改为rejected）
  - `activate`: 激活（状态改为approved）

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "批量approve操作完成，共更新3个成员",
    "data": {
        "updated_count": 3,
        "total_count": 4
    },
    "error": {}
}
```

### 5. 获取组织操作日志

**接口**: `GET /api/v1/organization/operation-logs/`
**描述**: 获取组织的操作日志记录
**权限**: 组织管理员或所有者

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 查询参数
- `operation` (可选): 操作类型过滤
- `operator` (可选): 操作者用户名过滤
- `page` (可选): 页码，默认1
- `page_size` (可选): 每页数量，默认20

#### 请求示例
```
GET /api/v1/organization/operation-logs/?operation=member_approve&page=1&page_size=10
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "logs": [
            {
                "id": 10,
                "operation": "member_approve",
                "operation_display": "审核通过成员",
                "operator": {
                    "id": "1",
                    "username": "admin_user",
                    "real_name": "管理员"
                },
                "target_user": {
                    "id": "2",
                    "username": "new_member",
                    "real_name": "新成员"
                },
                "ip_address": null,
                "details": {
                    "old_status": "pending",
                    "new_status": "approved",
                    "batch_operation": true
                },
                "created_at": "2025-08-08T21:21:53.160879+08:00"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 1,
            "total_count": 4,
            "page_size": 20,
            "has_next": false,
            "has_previous": false
        }
    },
    "error": {}
}
```

#### 操作类型说明

**成员审核类操作**：
- `member_approve`: 审核通过成员
- `member_reject`: 拒绝成员申请

**成员状态管理**：
- `member_suspend`: 暂停成员
- `member_activate`: 激活成员
- `member_remove`: 移除成员

**权限管理**：
- `permission_grant_admin`: 授予管理员权限
- `permission_revoke_admin`: 撤销管理员权限
- `permission_grant_member`: 授予成员权限
- `permission_revoke_member`: 撤销成员权限

**组织管理**：
- `organization_update`: 更新组织信息
- `organization_config_update`: 更新组织配置

### 6. 获取组织配置

**接口**: `GET /api/v1/organization/config/`
**描述**: 获取组织配置信息
**权限**: 组织所有者

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
        "id": "config-uuid-1",
        "organization": "org-uuid-1",
        "allow_public_registration": true,
        "require_approval_for_registration": true,
        "max_members": 100,
        "member_can_invite": false,
        "auto_approve_email_domains": ["@company.com", "@subsidiary.com"],
        "notification_settings": {
            "email_notifications": true,
            "sms_notifications": false,
            "new_member_notification": true,
            "member_status_change_notification": true
        },
        "custom_fields": {
            "employee_id": {
                "label": "员工编号",
                "required": true,
                "type": "text"
            },
            "hire_date": {
                "label": "入职日期",
                "required": false,
                "type": "date"
            }
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "error": {}
}
```

### 7. 更新组织配置

**接口**: `PUT /api/v1/organization/config/`
**描述**: 更新组织配置信息
**权限**: 组织所有者

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求参数
```json
{
    "allow_public_registration": false,
    "require_approval_for_registration": true,
    "max_members": 150,
    "member_can_invite": true,
    "auto_approve_email_domains": ["@company.com"],
    "notification_settings": {
        "email_notifications": true,
        "sms_notifications": true,
        "new_member_notification": true,
        "member_status_change_notification": false
    },
    "custom_fields": {
        "employee_id": {
            "label": "员工工号",
            "required": true,
            "type": "text"
        }
    }
}
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "组织配置更新成功",
    "data": {
        "id": "config-uuid-1",
        "organization": "org-uuid-1",
        "allow_public_registration": false,
        "require_approval_for_registration": true,
        "max_members": 150,
        "member_can_invite": true,
        "auto_approve_email_domains": ["@company.com"],
        "notification_settings": {
            "email_notifications": true,
            "sms_notifications": true,
            "new_member_notification": true,
            "member_status_change_notification": false
        },
        "custom_fields": {
            "employee_id": {
                "label": "员工工号",
                "required": true,
                "type": "text"
            }
        },
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-02T15:45:00Z"
    },
    "error": {}
}
```

### 8. 更新组织信息

**接口**: `PUT /api/v1/organization/update/`
**描述**: 更新组织基本信息
**权限**: 组织创建者和管理员

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 请求参数
```json
{
    "name": "新的组织名称",
    "leader_name": "新负责人",
    "leader_title": "新职位",
    "contact_person": "新联系人",
    "contact_position": "新联系人职位",
    "contact_phone": "010-87654321",
    "contact_email": "new_contact@example.com",
    "address": "新地址",
    "postal_code": "100001",
    "description": "更新后的组织描述",
    "website": "https://www.newwebsite.com",
    "established_date": "2021-01-01",
    "enterprise_type": "state_owned",
    "university_type": null,
    "industry_or_discipline": "新兴技术",
    "scale": "大型企业"
}
```

#### 参数说明
- 所有参数都是可选的，支持部分更新
- `enterprise_type`: 企业类型（仅企业组织）
  - `state_owned`: 国有企业
  - `private`: 民营企业
  - `foreign`: 外资企业
  - `joint_venture`: 合资企业
- `university_type`: 大学类型（仅大学组织）
  - `research`: 研究型大学
  - `comprehensive`: 综合性大学
  - `specialized`: 专业性大学
  - `vocational`: 职业技术学院

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "组织信息更新成功",
    "data": {
        "id": 1,
        "name": "新的组织名称",
        "code": "ORG001",
        "organization_type": "enterprise",
        "organization_type_display": "企业",
        "leader_name": "新负责人",
        "leader_title": "新职位",
        "contact_person": "新联系人",
        "contact_position": "新联系人职位",
        "contact_phone": "010-87654321",
        "contact_email": "new_contact@example.com",
        "address": "新地址",
        "postal_code": "100001",
        "description": "更新后的组织描述",
        "website": "https://www.newwebsite.com",
        "established_date": "2021-01-01",
        "enterprise_type": "state_owned",
        "enterprise_type_display": "国有企业",
        "industry_or_discipline": "新兴技术",
        "scale": "大型企业",
        "status": "verified",
        "status_display": "已认证",
        "updated_at": "2024-01-02T15:30:00Z"
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
        "contact_email": ["请输入有效的邮箱地址"],
        "website": ["请输入有效的网址"]
    }
}
```

### 9. 上传组织Logo

**接口**: `POST /api/v1/organization/upload-logo/`
**描述**: 上传或更新组织Logo
**权限**: 组织创建者和管理员

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### 请求参数
- `logo`: 图片文件（必需）
  - 支持格式：JPEG、PNG、GIF、WebP
  - 文件大小限制：5MB
  - 建议尺寸：正方形，至少200x200像素

#### 请求示例（使用FormData）
```javascript
const formData = new FormData();
formData.append('logo', logoFile);

fetch('/api/v1/organization/upload-logo/', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${token}`
    },
    body: formData
});
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "Logo上传成功",
    "data": {
        "logo_url": "http://localhost:8000/media/organization_logos/org_1_logo_20240102153000.jpg",
        "updated_at": "2024-01-02T15:30:00Z"
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
        "logo": ["文件大小不能超过5MB", "不支持的文件格式"]
    }
}
```

#### 功能特性
- **自动文件管理**: 上传新Logo时会自动删除旧的Logo文件
- **文件重命名**: 上传的文件会自动重命名为 `org_{组织ID}_logo_{时间戳}.{扩展名}`
- **格式验证**: 严格验证文件格式和大小
- **操作日志**: 自动记录Logo更新操作日志

### 10. 组织管理页面

**接口**: `GET /api/v1/organization/management/`
**描述**: 获取组织管理页面（HTML页面）
**权限**: 组织管理员或所有者

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应
返回HTML页面，用于组织管理界面。

## 权限说明

### 组织成员权限级别
- **owner**: 组织所有者
  - 拥有所有权限
  - 可以管理组织配置
  - 可以管理所有成员
  - 可以查看所有操作日志

- **admin**: 组织管理员
  - 可以管理成员（除所有者外）
  - 可以查看操作日志
  - 可以批量操作成员

- **member**: 普通成员
  - 可以查看组织基本信息
  - 可以查看成员列表

### 成员状态说明
- **pending**: 待审核
- **approved**: 已通过
- **rejected**: 未通过

## 错误码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 422 | 验证失败 |
| 500 | 服务器内部错误 |

## 使用示例

### JavaScript (Fetch API)

```javascript
// 获取组织详情
const getOrganizationDetail = async (organizationId) => {
    const response = await fetch(`/api/v1/organization/${organizationId}/detail/`);
    return await response.json();
};

// 获取成员列表
const getMembers = async (token, filters = {}) => {
    const params = new URLSearchParams(filters);
    const response = await fetch(`/api/v1/organization/members/?${params}`, {
        headers: {
            'Authorization': `Bearer ${token}`,
        }
    });
    return await response.json();
};

// 更新组织信息
const updateOrganization = async (token, data) => {
    const response = await fetch('/api/v1/organization/update/', {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    return await response.json();
};

// 上传组织Logo
const uploadOrganizationLogo = async (token, logoFile) => {
    const formData = new FormData();
    formData.append('logo', logoFile);
    
    const response = await fetch('/api/v1/organization/upload-logo/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        body: formData
    });
    return await response.json();
};

// 更新成员信息
const updateMember = async (token, memberId, data) => {
    const response = await fetch(`/api/v1/organization/members/${memberId}/update/`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    });
    return await response.json();
};

// 批量更新成员
const batchUpdateMembers = async (token, memberIds, action) => {
    const response = await fetch('/api/v1/organization/members/batch-update/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            member_ids: memberIds,
            action: action
        })
    });
    return await response.json();
};
```

### Python (requests)

```python
import requests

# 获取组织详情
def get_organization_detail(organization_id):
    response = requests.get(
        f'http://localhost:8000/api/v1/organization/{organization_id}/detail/'
    )
    return response.json()

# 获取成员列表
def get_members(token, filters=None):
    headers = {'Authorization': f'Bearer {token}'}
    params = filters or {}
    response = requests.get(
        'http://localhost:8000/api/v1/organization/members/',
        headers=headers,
        params=params
    )
    return response.json()

# 更新组织信息
def update_organization(token, data):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.put(
        'http://localhost:8000/api/v1/organization/update/',
        headers=headers,
        json=data
    )
    return response.json()

# 上传组织Logo
def upload_organization_logo(token, logo_file_path):
    headers = {'Authorization': f'Bearer {token}'}
    with open(logo_file_path, 'rb') as f:
        files = {'logo': f}
        response = requests.post(
            'http://localhost:8000/api/v1/organization/upload-logo/',
            headers=headers,
            files=files
        )
    return response.json()

# 更新成员信息
def update_member(token, member_id, data):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.put(
        f'http://localhost:8000/api/v1/organization/members/{member_id}/update/',
        headers=headers,
        json=data
    )
    return response.json()

# 批量更新成员
def batch_update_members(token, member_ids, action):
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    data = {
        'member_ids': member_ids,
        'action': action
    }
    response = requests.post(
        'http://localhost:8000/api/v1/organization/members/batch-update/',
        headers=headers,
        json=data
    )
    return response.json()
```

## 注意事项

1. **权限验证**: 所有需要认证的接口都需要在请求头中包含有效的JWT token
2. **组织状态**: 只有状态为"verified"的组织才能被公开访问
3. **成员管理**: 管理员不能管理同级别或更高级别的成员
4. **操作日志**: 所有重要操作都会记录在操作日志中
5. **分页**: 列表接口都支持分页，建议合理设置page_size避免性能问题
6. **搜索**: 支持模糊搜索，搜索范围包括用户名、真实姓名、邮箱、职位、部门等字段