# 学生项目管理 API 文档

## 概述

本文档描述了学生项目管理系统的三个核心接口：创建项目、修改项目和删除项目。

### 基础信息

- **基础URL**: `/api/v1/studentproject/`
- **认证方式**: Bearer Token (JWT)
- **内容类型**: `application/json`
- **权限要求**: 所有接口都需要学生用户身份

---

## 1. 创建项目接口

### 接口信息

- **URL**: `POST /api/v1/studentproject/projects/create/`
- **权限**: 所有认证用户
- **功能**: 创建新项目，创建者自动成为项目leader
- **业务规则**: 不允许关联已公示评分结果的需求（evaluation_published=true）

### 请求参数

#### Headers
```http
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

#### Body Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| title | string | 是 | 项目标题，最大长度200字符 |
| description | string | 否 | 项目描述，支持富文本 |
| requirement | integer | 是 | 关联的需求ID |
| status | string | 否 | 项目状态，可选值：draft(草稿)、recruiting(招募中)、in_progress(进行中)、completed(已完成)、suspended(已暂停)、cancelled(已取消)，默认为draft |

#### 请求示例

```json
{
    "title": "基于深度学习的图像识别系统",
    "description": "本项目旨在开发一个高精度的图像识别系统，采用卷积神经网络技术，能够识别多种物体类别。项目将分为数据收集、模型训练、系统集成三个阶段。",
    "requirement": 123,
    "status": "recruiting"
}
```

### 响应格式

#### 成功响应 (201 Created)

```json
{
    "success": true,
    "message": "项目创建成功",
    "data": {
        "id": 456,
        "title": "基于深度学习的图像识别系统",
        "description": "本项目旨在开发一个高精度的图像识别系统，采用卷积神经网络技术，能够识别多种物体类别。项目将分为数据收集、模型训练、系统集成三个阶段。",
        "requirement": {
            "id": 123,
            "title": "智能图像处理技术开发",
            "description": "需要开发先进的图像处理算法",
            "budget": 50000.00,
            "required_people": 3,
            "status": "recruiting",
            "organization_name": "科技创新实验室",
            "created_at": "2024-01-15T10:30:00Z"
        },
        "status": "draft",
        "participants": [
            {
                "id": 789,
                "student": {
                    "id": 101,
                    "student_number": "2021001001",
                    "school": "清华大学",
                    "major": "计算机科学与技术",
                    "grade": "2021",
                    "real_name": "张三",
                    "username": "zhangsan",
                    "avatar": "/media/avatars/101/avatar.jpg"
                },
                "role": "leader",
                "status": "approved",
                "application_message": "项目创建者自动成为leader",
                "reviewed_by": null,
                "review_message": null,
                "applied_at": "2024-01-20T14:30:00Z",
                "reviewed_at": "2024-01-20T14:30:00Z"
            }
        ],
        "deliverables": [],
        "recent_comments": [],
        "leader": {
            "id": 101,
            "student_number": "2021001001",
            "school": "清华大学",
            "major": "计算机科学与技术",
            "grade": "2021",
            "real_name": "张三",
            "username": "zhangsan",
            "avatar": "/media/avatars/101/avatar.jpg"
        },
        "created_at": "2024-01-20T14:30:00Z",
        "updated_at": "2024-01-20T14:30:00Z"
    }
}
```

#### 错误响应

**400 Bad Request - 数据验证失败**
```json
{
    "success": false,
    "message": "数据验证失败",
    "errors": {
        "title": ["此字段为必填项。"],
        "requirement": ["无效的主键"999" - 对象不存在。"]
    }
}
```

**400 Bad Request - 需求已公示评分结果**
```json
{
    "success": false,
    "message": "数据验证失败",
    "errors": {
        "requirement": ["该需求已公示评分结果，不能再创建新项目"]
    }
}
```

**401 Unauthorized - 未认证**
```json
{
    "detail": "身份认证信息未提供。"
}
```

**403 Forbidden - 权限不足**
```json
{
    "detail": "您没有执行该操作的权限。"
}
```

**500 Internal Server Error - 服务器错误**
```json
{
    "success": false,
    "message": "项目创建失败: 数据库连接错误"
}
```

---

## 2. 修改项目接口

### 接口信息

- **URL**: `PUT /api/v1/studentproject/projects/<project_id>/update/` 或 `PATCH /api/v1/studentproject/projects/<project_id>/update/`
- **权限**: 仅项目leader
- **功能**: 修改项目信息
- **说明**: PUT为完整更新，PATCH为部分更新

### 请求参数

#### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

#### Headers
```http
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

#### Body Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| title | string | PUT:是, PATCH:否 | 项目标题，最大长度200字符 |
| description | string | 否 | 项目描述，支持富文本 |
| status | string | 否 | 项目状态: draft, recruiting, in_progress, completed, suspended, cancelled |

#### 请求示例

**PUT 请求 (完整更新)**
```json
{
    "title": "基于深度学习的智能图像识别系统",
    "description": "本项目已更新为更加智能的图像识别系统，新增了实时处理功能和更高的识别精度。项目分为四个阶段：需求分析、算法设计、系统开发、测试部署。",
    "status": "in_progress"
}
```

**PATCH 请求 (部分更新)**
```json
{
    "status": "in_progress"
}
```

### 响应格式

#### 成功响应 (200 OK)

```json
{
    "success": true,
    "message": "项目更新成功",
    "data": {
        "id": 456,
        "title": "基于深度学习的智能图像识别系统",
        "description": "本项目已更新为更加智能的图像识别系统，新增了实时处理功能和更高的识别精度。项目分为四个阶段：需求分析、算法设计、系统开发、测试部署。",
        "requirement": {
            "id": 123,
            "title": "智能图像处理技术开发",
            "description": "需要开发先进的图像处理算法",
            "budget": 50000.00,
            "required_people": 3,
            "status": "recruiting",
            "organization_name": "科技创新实验室",
            "created_at": "2024-01-15T10:30:00Z"
        },
        "status": "active",
        "participants": [
            {
                "id": 789,
                "student": {
                    "id": 101,
                    "student_number": "2021001001",
                    "school": "清华大学",
                    "major": "计算机科学与技术",
                    "grade": "2021",
                    "real_name": "张三",
                    "username": "zhangsan",
                    "avatar": "/media/avatars/101/avatar.jpg"
                },
                "role": "leader",
                "status": "approved",
                "application_message": "项目创建者自动成为leader",
                "reviewed_by": null,
                "review_message": null,
                "applied_at": "2024-01-20T14:30:00Z",
                "reviewed_at": "2024-01-20T14:30:00Z"
            }
        ],
        "deliverables": [],
        "recent_comments": [],
        "leader": {
            "id": 101,
            "student_number": "2021001001",
            "school": "清华大学",
            "major": "计算机科学与技术",
            "grade": "2021",
            "real_name": "张三",
            "username": "zhangsan",
            "avatar": "/media/avatars/101/avatar.jpg"
        },
        "created_at": "2024-01-20T14:30:00Z",
        "updated_at": "2024-01-20T15:45:00Z"
    }
}
```

#### 错误响应

**400 Bad Request - 数据验证失败**
```json
{
    "success": false,
    "message": "数据验证失败",
    "errors": {
        "status": ["\"invalid_status\" 不是合法选择。"]
    }
}
```

**403 Forbidden - 权限不足**
```json
{
    "success": false,
    "message": "权限不足，只有项目leader可以修改项目"
}
```

**404 Not Found - 项目不存在**
```json
{
    "detail": "未找到。"
}
```

**500 Internal Server Error - 服务器错误**
```json
{
    "success": false,
    "message": "项目更新失败: 数据库连接错误"
}
```

---

## 3. 删除项目接口

### 接口信息

- **URL**: `DELETE /api/v1/studentproject/projects/<project_id>/delete/`
- **权限**: 仅项目leader
- **功能**: 删除项目及其所有相关数据

### 删除范围

删除项目时会自动删除以下相关数据：
1. 解除与所有参与者的关系
2. 删除所有关联的成果（包括完整的成果链）
3. 删除所有相关联的文件信息
4. 删除所有项目评论
5. 删除所有相关通知

### 请求参数

#### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

#### Headers
```http
Authorization: Bearer <your_jwt_token>
```

#### 请求示例

```http
DELETE /api/v1/studentproject/projects/456/delete/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 响应格式

#### 成功响应 (200 OK)

```json
{
    "success": true,
    "message": "项目 \"基于深度学习的智能图像识别系统\" 及其所有相关数据已成功删除"
}
```

#### 错误响应

**403 Forbidden - 权限不足**
```json
{
    "success": false,
    "message": "权限不足，只有项目leader可以删除项目"
}
```

**404 Not Found - 项目不存在**
```json
{
    "detail": "未找到。"
}
```

**500 Internal Server Error - 服务器错误**
```json
{
    "success": false,
    "message": "项目删除失败: 数据库连接错误"
}
```

---

## 项目状态说明

### 状态类型

| 状态值 | 中文名称 | 描述 | 可见性 |
|--------|----------|------|--------|
| draft | 草稿 | 项目处于草稿状态，仍在完善中 | 仅创建者可见 |
| recruiting | 招募中 | 项目正在招募成员 | 所有人可见 |
| in_progress | 进行中 | 项目正在进行中 | 所有人可见 |
| completed | 已完成 | 项目已完成 | 所有人可见 |
| suspended | 已暂停 | 项目暂时暂停 | 所有人可见 |
| cancelled | 已取消 | 项目已取消 | 所有人可见 |

### 可见性规则

1. **draft状态项目**：
   - 仅项目创建者和参与者可见
   - 组织用户访问关联需求详情时不会显示该项目
   - 其他学生无法发现该项目

2. **非draft状态项目**：
   - 所有用户都可见
   - 学生可以发现并申请加入
   - 组织用户访问关联需求详情时会显示项目信息和参与者信息

---

## 权限系统

### 用户类型权限

| 操作 | 学生用户 | 组织用户 | 管理员 |
|------|----------|----------|--------|
| 创建项目 | ✅ | ❌ | ✅ |
| 修改项目 | ✅ (仅leader) | ❌ | ✅ |
| 删除项目 | ✅ (仅leader) | ❌ | ✅ |
| 查看项目 | ✅ | ✅ (根据状态) | ✅ |

### Leader权限验证

系统通过以下条件验证用户是否为项目leader：
1. 用户已认证且为学生类型
2. 用户在项目参与者表中存在记录
3. 用户角色为'leader'
4. 参与状态为'approved'

---

## 7. 评论系统接口

### 7.1 获取评语列表接口

#### 接口信息

- **URL**: `GET /api/v1/studentproject/projects/<project_id>/comments/`
- **权限**: 项目参与者、项目负责人和项目所属组织的组织用户
- **功能**: 获取项目级或成果级评语列表

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

##### Query Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| deliverable_id | integer | 否 | 成果ID，不传则获取项目级评语，传入则获取指定成果的评语 |
| page | integer | 否 | 页码，默认为1 |
| page_size | integer | 否 | 每页数量，默认为10 |

##### Headers
```http
Authorization: Bearer <your_jwt_token>
```

##### 请求示例

**获取项目级评语：**
```http
GET /api/v1/studentproject/projects/123/comments/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**获取成果级评语：**
```http
GET /api/v1/studentproject/projects/123/comments/?deliverable_id=456
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "success": true,
    "data": {
        "comments": [
            {
                "id": 789,
                "content": "项目整体进展良好，建议在下一阶段加强技术文档的完善。",
                "author": {
                    "id": 201,
                    "real_name": "李老师",
                    "username": "teacher_li",
                    "avatar": "http://localhost:8000/media/avatars/201/avatar.jpg"
                },
                "parent_comment": null,
                "reply_count": 2,
                "is_reply": false,
                "created_at": "2024-01-20T14:30:00Z",
                "updated_at": "2024-01-20T14:30:00Z"
            },
            {
                "id": 790,
                "content": "需要补充更多的测试用例和性能分析报告。",
                "author": {
                    "id": 202,
                    "real_name": "王主管",
                    "username": "manager_wang",
                    "avatar": "http://localhost:8000/media/avatars/202/avatar.jpg"
                },
                "parent_comment": null,
                "reply_count": 0,
                "is_reply": false,
                "created_at": "2024-01-20T15:00:00Z",
                "updated_at": "2024-01-20T15:00:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 1,
            "total_count": 2,
            "page_size": 10,
            "has_next": false,
            "has_previous": false
        }
    }
}
```

### 7.2 发布评语接口

#### 接口信息

- **URL**: `POST /api/v1/studentproject/projects/<project_id>/comments/create/`
- **权限**: 只有项目关联需求所属的组织用户可以发布
- **功能**: 发布项目级或成果级评语，支持回复功能

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

##### Headers
```http
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

##### Query Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| deliverable_id | integer | 否 | 成果ID，不传则为项目级评语，传入则为指定成果的评语 |
| parent_comment_id | integer | 否 | 父评语ID，用于回复功能 |

##### Body Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| content | string | 是 | 评语内容 |

##### 请求示例

**发布项目级评语：**
```http
POST /api/v1/studentproject/projects/123/comments/create/
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

{
    "content": "项目整体进展良好，建议在下一阶段加强技术文档的完善。"
}
```

**发布成果级评语：**
```http
POST /api/v1/studentproject/projects/123/comments/create/?deliverable_id=456
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

{
    "content": "需求分析报告内容详实，但建议补充更多的用户场景分析。"
}
```

**回复评语：**
```http
POST /api/v1/studentproject/projects/123/comments/create/?parent_comment_id=789
Content-Type: application/json
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...

{
    "content": "感谢建议，我们会在下个版本中补充相关内容。"
}
```

#### 响应格式

##### 成功响应 (201 Created)

```json
{
    "success": true,
    "message": "评语发布成功",
    "data": {
        "id": 791,
        "content": "项目整体进展良好，建议在下一阶段加强技术文档的完善。",
        "author": {
            "id": 201,
            "real_name": "李老师",
            "username": "teacher_li",
            "avatar": "http://localhost:8000/media/avatars/201/avatar.jpg"
        },
        "parent_comment": null,
        "reply_count": 0,
        "is_reply": false,
        "created_at": "2024-01-20T16:30:00Z",
        "updated_at": "2024-01-20T16:30:00Z"
    }
}
```

### 7.3 更新评语接口

#### 接口信息

- **URL**: `PUT /api/v1/studentproject/projects/<project_id>/comments/<comment_id>/update/`
- **权限**: 只有评语发布者可以更新
- **功能**: 更新评语内容并记录更新时间

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |
| comment_id | integer | 是 | 评语ID |

##### Headers
```http
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

##### Body Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| content | string | 是 | 更新后的评语内容 |

##### 请求示例

```json
{
    "content": "项目整体进展良好，建议在下一阶段加强技术文档的完善，同时注意代码质量的提升。"
}
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "success": true,
    "message": "评语更新成功",
    "data": {
        "id": 791,
        "content": "项目整体进展良好，建议在下一阶段加强技术文档的完善，同时注意代码质量的提升。",
        "author": {
            "id": 201,
            "real_name": "李老师",
            "username": "teacher_li",
            "avatar": "http://localhost:8000/media/avatars/201/avatar.jpg"
        },
        "parent_comment": null,
        "reply_count": 0,
        "is_reply": false,
        "created_at": "2024-01-20T16:30:00Z",
        "updated_at": "2024-01-20T16:45:00Z"
    }
}
```

### 7.4 删除评语接口

#### 接口信息

- **URL**: `DELETE /api/v1/studentproject/projects/<project_id>/comments/<comment_id>/delete/`
- **权限**: 只有评语发布者可以删除
- **功能**: 删除评语（级联删除所有回复）

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |
| comment_id | integer | 是 | 评语ID |

##### Headers
```http
Authorization: Bearer <your_jwt_token>
```

##### 请求示例

```http
DELETE /api/v1/studentproject/projects/123/comments/791/delete/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "success": true,
    "message": "评语删除成功"
}
```

### 7.5 获取评语回复列表接口

#### 接口信息

- **URL**: `GET /api/v1/studentproject/projects/<project_id>/comments/<comment_id>/replies/`
- **权限**: 项目参与者、项目负责人和项目所属组织的组织用户
- **功能**: 获取指定评语的所有回复

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |
| comment_id | integer | 是 | 评语ID |

##### Query Parameters

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 10 | 每页显示数量 |

##### Headers
```http
Authorization: Bearer <your_jwt_token>
```

##### 请求示例

```http
GET /api/v1/studentproject/projects/123/comments/789/replies/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

```http
GET /api/v1/studentproject/projects/123/comments/789/replies/?page=2&page_size=5
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "success": true,
    "data": {
        "replies": [
            {
                "id": 792,
                "content": "感谢建议，我们会在下个版本中补充技术文档。",
                "author": {
                    "id": 101,
                    "real_name": "张三",
                    "username": "zhangsan",
                    "avatar": "http://localhost:8000/media/avatars/101/avatar.jpg"
                },
                "parent_comment": {
                    "id": 789,
                    "content": "项目整体进展良好，建议在下一阶段加强技术文档的完善。"
                },
                "reply_count": 0,
                "is_reply": true,
                "created_at": "2024-01-20T17:00:00Z",
                "updated_at": "2024-01-20T17:00:00Z"
            },
            {
                "id": 793,
                "content": "我们已经开始着手准备相关文档，预计下周完成。",
                "author": {
                    "id": 102,
                    "real_name": "李四",
                    "username": "lisi",
                    "avatar": "http://localhost:8000/media/avatars/102/avatar.jpg"
                },
                "parent_comment": {
                    "id": 789,
                    "content": "项目整体进展良好，建议在下一阶段加强技术文档的完善。"
                },
                "reply_count": 0,
                "is_reply": true,
                "created_at": "2024-01-20T17:15:00Z",
                "updated_at": "2024-01-20T17:15:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "page_size": 10,
            "total_count": 2,
            "total_pages": 1,
            "has_next": false,
            "has_previous": false
        }
    }
}
```

### 7.6 评论系统权限说明

#### 权限类型

| 操作 | 学生用户 | 组织用户 | 权限说明 |
|------|----------|----------|----------|
| 查看评语列表 | ✅ (参与者/负责人) | ✅ (所属组织) | 项目参与者、负责人和所属组织用户可查看 |
| 发布评语 | ❌ | ✅ (所属组织) | 只有项目关联需求所属的组织用户可发布 |
| 回复评语 | ❌ | ✅ (所属组织) | 只有项目关联需求所属的组织用户可回复 |
| 更新评语 | ❌ | ✅ (发布者) | 只有评语发布者可以更新 |
| 删除评语 | ❌ | ✅ (发布者) | 只有评语发布者可以删除 |

#### 评语类型说明

1. **项目级评语**：针对整个项目的评价和建议
   - 不指定 `deliverable_id` 参数
   - 适用于项目整体进展、团队协作等方面的评价

2. **成果级评语**：针对特定项目成果的评价和建议
   - 指定 `deliverable_id` 参数
   - 适用于具体成果文件、阶段性成果的评价

#### 错误响应说明

**403 Forbidden - 权限不足**
```json
{
    "success": false,
    "message": "您没有权限查看评语" // 或其他权限相关错误信息
}
```

**404 Not Found - 资源不存在**
```json
{
    "detail": "未找到。"
}
```

**400 Bad Request - 数据验证失败**
```json
{
    "success": false,
    "message": "数据验证失败",
    "errors": {
        "content": ["此字段为必填项。"]
    }
}
```

---

## 错误码说明

| HTTP状态码 | 错误类型 | 描述 |
|------------|----------|------|
| 200 | 成功 | 请求成功处理 |
| 201 | 创建成功 | 资源创建成功 |
| 400 | 请求错误 | 请求参数错误或验证失败 |
| 401 | 未认证 | 缺少认证信息或认证失败 |
| 403 | 权限不足 | 用户权限不足 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 500 | 服务器错误 | 服务器内部错误 |



## 6. 项目成果管理接口

### 6.1 提交成果接口

#### 接口信息

- **URL**: `POST /api/v1/studentproject/projects/<project_id>/deliverables/submit/`
- **权限**: 项目参与者或项目负责人
- **功能**: 提交项目成果，支持文件上传和网盘链接

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

##### Headers
```http
Content-Type: multipart/form-data
Authorization: Bearer <your_jwt_token>
```

##### Body Parameters (Form-Data)

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| title | string | 是 | 成果标题，最大长度200字符 |
| description | string | 否 | 成果描述 |
| stage_type | string | 是 | 阶段类型：initial(初始版本)、revision(修订版本)、final(最终版本) |
| is_milestone | boolean | 否 | 是否为里程碑，默认false |
| progress_description | string | 否 | 进度描述 |
| notes | string | 否 | 备注信息 |
| files_ids | string | 否 | 关联的现有文件ID列表，逗号分隔（如：1,2,3） |
| uploaded_files | file[] | 否 | 上传的文件列表（支持多文件上传） |
| cloud_links | string | 否 | 网盘链接地址，直接提供链接URL |
| cloud_password | string | 否 | 网盘链接提取密码（可选） |
| virtual_folder_path | string | 否 | 虚拟文件夹路径，默认为"/"（如：/deliverables/stage1） |

##### 请求示例

**使用curl命令：**
```bash
curl -X POST \
  http://localhost:8000/api/v1/studentproject/projects/123/deliverables/submit/ \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...' \
  -F 'title=项目需求分析报告' \
  -F 'description=详细的项目需求分析文档' \
  -F 'stage_type=initial' \
  -F 'is_milestone=true' \
  -F 'files_ids=1,2,3' \
  -F 'cloud_links=https://pan.baidu.com/s/xxx' \
  -F 'cloud_password=abc123' \
  -F 'virtual_folder_path=/deliverables/stage1' \
  -F 'uploaded_files=@/path/to/file1.pdf' \
  -F 'uploaded_files=@/path/to/file2.docx'
```

**使用JavaScript (FormData)：**
```javascript
const formData = new FormData();
formData.append('title', '项目需求分析报告');
formData.append('description', '详细的项目需求分析文档');
formData.append('stage_type', 'initial');
formData.append('is_milestone', 'true');
formData.append('files_ids', '1,2,3');
formData.append('cloud_links', 'https://pan.baidu.com/s/xxx');
formData.append('cloud_password', 'abc123');
formData.append('virtual_folder_path', '/deliverables/stage1');
formData.append('uploaded_files', file1); // File object
formData.append('uploaded_files', file2); // File object

fetch('/api/v1/studentproject/projects/123/deliverables/submit/', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
});
```

#### 响应格式

##### 成功响应 (201 Created)

```json
{
    "success": true,
    "message": "成果提交成功",
    "data": {
        "id": 456,
        "title": "项目需求分析报告",
        "description": "详细的项目需求分析文档",
        "stage_type": "initial",
        "version_number": 1,
        "stage_version": 1,
        "is_milestone": true,
        "is_deprecated": false,
        "progress_description": null,
        "notes": null,
        "files": [
            {
                "id": 789,
                "name": "需求分析报告.pdf",
                "file_url": "http://localhost:8000/media/projects/123/deliverables/需求分析报告.pdf",
                "file_size": 2048576,
                "is_cloud_link": false,
                "cloud_link_url": null,
                "cloud_password": null,
                "uploaded_at": "2024-01-20T14:30:00Z"
            },
            {
                "id": 790,
                "name": "需求分析.docx",
                "file_url": null,
                "file_size": null,
                "is_cloud_link": true,
                "cloud_link_url": "https://pan.baidu.com/s/xxx",
                "uploaded_at": "2024-01-20T14:30:00Z"
            }
        ],
        "submitter": {
            "id": 101,
            "real_name": "张三",
            "student_number": "2021001001"
        },
        "created_at": "2024-01-20T14:30:00Z",
        "updated_at": "2024-01-20T14:30:00Z"
    }
}
```

##### 错误响应

**400 Bad Request - 数据验证失败**
```json
{
    "success": false,
    "message": "数据验证失败",
    "errors": {
        "title": ["此字段为必填项。"],
        "stage_type": ["\"invalid\" 不是合法选择。"]
    }
}
```

**403 Forbidden - 权限不足**
```json
{
    "success": false,
    "message": "权限不足，只有项目参与者可以提交成果"
}
```

### 6.2 更新成果接口

#### 接口信息

- **URL**: `PUT /api/v1/studentproject/projects/<project_id>/deliverables/<deliverable_id>/update/`
- **权限**: 项目参与者或项目负责人
- **功能**: 更新成果信息，仅支持修改网盘链接，不支持修改实体文件。同时支持弃用成果功能

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |
| deliverable_id | integer | 是 | 成果ID |

##### Headers
```http
Content-Type: multipart/form-data
Authorization: Bearer <your_jwt_token>
```

##### Body Parameters (Form-Data)

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| title | string | 否 | 成果标题，最大长度200字符 |
| description | string | 否 | 成果描述 |
| progress_description | string | 否 | 进度描述 |
| notes | string | 否 | 备注信息 |
| cloud_links | string | 否 | 网盘链接地址，直接提供链接URL |
| cloud_password | string | 否 | 网盘链接提取密码（可选） |
| virtual_folder_path | string | 否 | 虚拟文件夹路径，默认为"/"（如：/deliverables/stage1） |
| is_deprecated | boolean | 否 | 是否弃用成果，设置为true时将成果标记为弃用状态 |

##### 请求示例

**使用curl命令：**
```bash
curl -X PUT \
  http://localhost:8000/api/v1/studentproject/projects/123/deliverables/456/update/ \
  -H 'Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...' \
  -F 'title=更新的项目需求分析报告' \
  -F 'description=更新后的详细需求分析文档' \
  -F 'cloud_links=https://pan.baidu.com/s/updated_xxx' \
  -F 'cloud_password=new123' \
  -F 'virtual_folder_path=/deliverables/updated'
```

**使用JavaScript (FormData)：**
```javascript
const formData = new FormData();
formData.append('title', '更新的项目需求分析报告');
formData.append('description', '更新后的详细需求分析文档');
formData.append('cloud_links', 'https://pan.baidu.com/s/updated_xxx');
formData.append('cloud_password', 'new123');
formData.append('virtual_folder_path', '/deliverables/updated');

fetch('/api/v1/studentproject/projects/123/deliverables/456/update/', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer ' + token
  },
  body: formData
});
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "success": true,
    "message": "成果更新成功", // 或 "成果已标记为弃用"（当is_deprecated=true时）
    "data": {
        "id": 456,
        "title": "项目需求分析报告",
        "description": "详细的项目需求分析文档",
        "stage_type": "initial",
        "version_number": 1,
        "stage_version": 1,
        "is_milestone": true,
        "is_deprecated": false,
        "files": [
            {
                "id": 789,
                "name": "需求分析报告.pdf",
                "is_cloud_link": false,
                "cloud_link_url": null,
                "cloud_password": null
            },
            {
                "id": 791,
                "name": "更新的需求分析.docx",
                "is_cloud_link": true,
                "cloud_link_url": "https://pan.baidu.com/s/updated_xxx",
                "cloud_password": "abc123"
            },
            {
                "id": 792,
                "name": "补充材料.pdf",
                "is_cloud_link": true,
                "cloud_link_url": "https://pan.baidu.com/s/additional_xxx",
                "cloud_password": "def456"
            }
        ],
        "updated_at": "2024-01-20T15:45:00Z"
    }
}
```

### 6.3 获取成果列表接口

#### 接口信息

- **URL**: `GET /api/v1/studentproject/projects/<project_id>/deliverables/`
- **权限**: 项目参与者、项目负责人或项目所属组织的组织用户
- **功能**: 获取项目成果列表，支持多种筛选和展示模式

#### 功能特性说明

##### 默认展示
- **展示内容**: 显示项目的所有成果，包括各个阶段的所有版本
- **排序规则**: 阶段优先级（末期>中期>前期），阶段内按版本号降序排列
- **适用场景**: 查看项目的完整成果历史，了解所有提交记录

##### 里程碑成果筛选 (milestone=true)
- **展示内容**: 仅显示标记为里程碑的重要成果
- **适用场景**: 快速查看项目的关键节点成果

##### 各阶段最新成果展示 (latest_per_stage=true)
- **展示内容**: 显示每个阶段的最新版本成果（版本号最大的成果）
- **排序规则**: 按阶段优先级排序
- **适用场景**: 快速了解各阶段的最新进展

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

##### Query Parameters

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| include_deprecated | boolean | 否 | true | 是否包含已弃用的成果：true=包含，false=不包含 |
| milestone | boolean | 否 | false | 里程碑成果筛选：false=显示所有成果，true=仅显示里程碑成果 |
| latest_per_stage | boolean | 否 | false | 各阶段最新成果展示：false=显示所有成果，true=仅显示各阶段最新成果 |
| stage_type | string | 否 | - | 阶段类型筛选，可选值：early(前期)、middle(中期)、final(末期) |
| page | integer | 否 | 1 | 页码，从1开始 |
| page_size | integer | 否 | 10 | 每页数量，最大100 |

##### Headers
```http
Authorization: Bearer <your_jwt_token>
```

##### 请求示例

```http
# 默认模式：获取所有成果列表（按阶段优先级和版本号排序）
GET /api/v1/studentproject/projects/123/deliverables/

# 里程碑成果筛选：仅显示重要的里程碑成果
GET /api/v1/studentproject/projects/123/deliverables/?milestone=true

# 各阶段最新成果：显示每个阶段的最新版本
GET /api/v1/studentproject/projects/123/deliverables/?latest_per_stage=true

# 包含弃用成果的完整列表
GET /api/v1/studentproject/projects/123/deliverables/?include_deprecated=true

# 筛选特定阶段的成果
GET /api/v1/studentproject/projects/123/deliverables/?stage_type=final

# 组合查询：里程碑成果 + 包含弃用成果 + 分页
GET /api/v1/studentproject/projects/123/deliverables/?milestone=true&include_deprecated=true&page=1&page_size=20

# 组合查询：各阶段最新成果 + 特定阶段筛选
GET /api/v1/studentproject/projects/123/deliverables/?latest_per_stage=true&stage_type=middle
```

#### 响应格式

##### 成功响应 (200 OK)

**默认展示响应示例：**
```json
{
    "success": true,
    "message": "成果列表获取成功",
    "data": {
        "results": [
            {
                "id": 458,
                "title": "项目最终报告v2",
                "description": "项目最终版本报告",
                "stage_type": "final",
                "version_number": 2,
                "stage_version": "末期v2",
                "is_milestone": true,
                "is_deprecated": false,
                "file_count": 5,
                "submitter": {
                    "id": 101,
                    "real_name": "张三",
                    "student_number": "2021001001"
                },
                "created_at": "2024-01-22T16:30:00Z",
                "updated_at": "2024-01-22T16:30:00Z"
            },
            {
                "id": 457,
                "title": "项目中期报告v3",
                "description": "项目中期第三版报告",
                "stage_type": "middle",
                "version_number": 3,
                "stage_version": "中期v3",
                "is_milestone": false,
                "is_deprecated": false,
                "file_count": 2,
                "submitter": {
                    "id": 102,
                    "real_name": "李四",
                    "student_number": "2021001002"
                },
                "created_at": "2024-01-21T14:30:00Z",
                "updated_at": "2024-01-21T14:30:00Z"
            },
            {
                "id": 456,
                "title": "项目需求分析报告",
                "description": "详细的项目需求分析文档",
                "stage_type": "early",
                "version_number": 1,
                "stage_version": "前期v1",
                "is_milestone": true,
                "is_deprecated": false,
                "file_count": 3,
                "submitter": {
                    "id": 101,
                    "real_name": "张三",
                    "student_number": "2021001001"
                },
                "created_at": "2024-01-20T14:30:00Z",
                "updated_at": "2024-01-20T15:45:00Z"
            }
        ],
        "pagination": {
            "page": 1,
            "page_size": 10,
            "total_pages": 1,
            "total_count": 3,
            "has_next": false,
            "has_previous": false
        }
    }
}
```

**里程碑成果筛选响应示例：**
```json
{
    "success": true,
    "message": "成果列表获取成功",
    "data": {
        "deliverables": [
            {
                "id": 458,
                "title": "项目最终报告v2",
                "description": "项目最终版本报告",
                "stage_type": "final",
                "version_number": 2,
                "stage_version": "末期v2",
                "is_milestone": true,
                "is_deprecated": false,
                "file_count": 5,
                "submitter": {
                    "id": 101,
                    "real_name": "张三",
                    "student_number": "2021001001"
                },
                "created_at": "2024-01-22T16:30:00Z",
                "updated_at": "2024-01-22T16:30:00Z"
            },
            {
                "id": 456,
                "title": "项目需求分析报告",
                "description": "详细的项目需求分析文档",
                "stage_type": "early",
                "version_number": 1,
                "stage_version": "前期v1",
                "is_milestone": true,
                "is_deprecated": false,
                "file_count": 3,
                "submitter": {
                    "id": 101,
                    "real_name": "张三",
                    "student_number": "2021001001"
                },
                "created_at": "2024-01-20T14:30:00Z",
                "updated_at": "2024-01-20T15:45:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 1,
            "total_count": 2,
            "has_next": false,
            "has_previous": false
        }
    }
}
```

**各阶段最新成果展示响应示例：**
```json
{
    "success": true,
    "message": "成果列表获取成功",
    "data": {
        "deliverables": [
            {
                "id": 458,
                "title": "项目最终报告v2",
                "description": "项目最终版本报告",
                "stage_type": "final",
                "version_number": 2,
                "stage_version": "末期v2",
                "is_milestone": true,
                "is_deprecated": false,
                "file_count": 5,
                "submitter": {
                    "id": 101,
                    "real_name": "张三",
                    "student_number": "2021001001"
                },
                "created_at": "2024-01-22T16:30:00Z",
                "updated_at": "2024-01-22T16:30:00Z"
            },
            {
                "id": 457,
                "title": "项目中期报告v3",
                "description": "项目中期第三版报告",
                "stage_type": "middle",
                "version_number": 3,
                "stage_version": "中期v3",
                "is_milestone": false,
                "is_deprecated": false,
                "file_count": 2,
                "submitter": {
                    "id": 102,
                    "real_name": "李四",
                    "student_number": "2021001002"
                },
                "created_at": "2024-01-21T14:30:00Z",
                "updated_at": "2024-01-21T14:30:00Z"
            },
            {
                "id": 456,
                "title": "项目需求分析报告",
                "description": "详细的项目需求分析文档",
                "stage_type": "early",
                "version_number": 2,
                "stage_version": "前期v2",
                "is_milestone": true,
                "is_deprecated": false,
                "file_count": 3,
                "submitter": {
                    "id": 101,
                    "real_name": "张三",
                    "student_number": "2021001001"
                },
                "created_at": "2024-01-20T14:30:00Z",
                "updated_at": "2024-01-20T15:45:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 1,
            "total_count": 3,
            "has_next": false,
            "has_previous": false
        }
    }
}
```

##### 字段说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| id | integer | 成果ID |
| title | string | 成果标题 |
| description | string | 成果描述 |
| stage_type | string | 阶段类型：early(前期)、middle(中期)、final(末期) |
| version_number | integer | 阶段内版本号 |
| stage_version | string | 阶段版本标识，如"前期v1"、"中期v2"、"末期v1" |
| is_milestone | boolean | 是否为里程碑版本 |
| is_deprecated | boolean | 是否已弃用 |
| file_count | integer | 关联文件数量 |
| submitter | object | 提交人信息 |
| created_at | string | 创建时间（ISO 8601格式） |
| updated_at | string | 更新时间（ISO 8601格式） |

##### 分页信息说明

| 字段名 | 类型 | 描述 |
|--------|------|------|
| page | integer | 当前页码 |
| page_size | integer | 每页数量 |
| total_pages | integer | 总页数 |
| total_count | integer | 总记录数 |
| has_next | boolean | 是否有下一页 |
| has_previous | boolean | 是否有上一页 |

##### 错误响应

**403 Forbidden - 权限不足**
```json
{
    "success": false,
    "message": "权限不足，只有项目参与者、负责人或组织用户可以查看成果列表"
}
```

**404 Not Found - 项目不存在**
```json
{
    "detail": "未找到。"
}
```


### 6.4 获取成果详情接口

#### 接口信息

- **URL**: `GET /api/v1/studentproject/projects/<project_id>/deliverables/<deliverable_id>/`
- **权限**: 项目参与者、项目负责人或项目所属组织的组织用户
- **功能**: 获取成果的详细信息，包括所有文件信息

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |
| deliverable_id | integer | 是 | 成果ID |

##### Headers
```http
Authorization: Bearer <your_jwt_token>
```

##### 请求示例

```http
GET /api/v1/studentproject/projects/123/deliverables/456/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "success": true,
    "message": "成果详情获取成功",
    "data": {
        "id": 456,
        "title": "项目需求分析报告",
        "description": "详细的项目需求分析文档",
        "stage_type": "initial",
        "version_number": 1,
        "stage_version": 1,
        "parent_deliverable": null,
        "is_milestone": true,
        "is_deprecated": false,
        "progress_description": "需求分析阶段已完成",
        "notes": "初版需求分析报告",
        "files": [
            {
                "id": 789,
                "name": "需求分析报告.pdf",
                "file_url": "http://localhost:8000/media/projects/123/deliverables/需求分析报告.pdf",
                "file_size": 2048576,
                "is_cloud_link": false,
                "cloud_link_url": null,
                "uploaded_at": "2024-01-20T14:30:00Z"
            },
            {
                "id": 791,
                "name": "更新的需求分析.docx",
                "file_url": null,
                "file_size": null,
                "is_cloud_link": true,
                "cloud_link_url": "https://pan.baidu.com/s/updated_xxx",
                "cloud_password": "abc123",
                "uploaded_at": "2024-01-20T15:45:00Z"
            }
        ],
        "submitter": {
            "id": 101,
            "real_name": "张三",
            "student_number": "2021001001",
            "school": "清华大学",
            "major": "计算机科学与技术",
            "grade": "2021"
        },
        "created_at": "2024-01-20T14:30:00Z",
        "updated_at": "2024-01-20T15:45:00Z"
    }
}
```

### 成果管理权限说明

#### 权限分级

1. **项目参与者和负责人**：
   - 可以提交成果
   - 可以更新成果（仅网盘链接）
   - 可以弃用成果
   - 可以查看成果列表和详情

2. **项目所属组织的组织用户**：
   - 可以查看成果列表和详情
   - 不能提交、更新或弃用成果

#### 成果阶段类型说明

| 阶段类型 | 中文名称 | 描述 |
|----------|----------|------|
| initial | 初始版本 | 项目成果的初始提交版本 |
| revision | 修订版本 | 对已有成果的修订和改进 |
| final | 最终版本 | 项目成果的最终确定版本 |

#### 版本管理说明

- **version_number**: 主版本号，每个独立成果的唯一标识
- **stage_version**: 阶段版本号，同一成果不同阶段的版本标识
- **parent_deliverable**: 父成果ID，用于构建版本链关系
- **is_deprecated**: 弃用标记，弃用的成果不会被删除，但会被标记

---

## 注意事项

1. **权限验证**: 所有接口都需要有效的JWT token，且用户必须为学生类型
2. **数据完整性**: 删除项目是不可逆操作，会删除所有相关数据
3. **状态管理**: 项目状态影响可见性，draft状态项目仅对参与者可见
4. **事务处理**: 所有写操作都使用数据库事务，确保数据一致性
5. **文件处理**: 删除项目时只删除文件记录，实际文件可能需要额外的清理机制
6. **并发控制**: 建议在前端实现适当的并发控制，避免重复提交
7. **成果管理**: 成果支持版本链管理，弃用成果而非删除，保持数据完整性
8. **文件支持**: 同时支持实体文件上传和网盘链接，更新时仅支持网盘链接修改

---

## 4. 获取项目列表接口

### 接口信息

- **URL**: `GET /api/v1/studentproject/projects/`
- **权限**: 所有认证用户
- **功能**: 获取项目列表，支持分页、筛选和搜索，区分多种使用场景

### 使用场景

1. **项目广场** (不传`my_projects`参数或为空): 显示所有公开的项目，类似项目广场效果
2. **我创建/负责的项目** (`my_projects=true`): 显示当前用户作为leader的项目
3. **我加入的项目** (`my_projects=false`): 显示当前用户参与的所有项目（包括负责的）

### 请求参数

#### Headers
```http
Authorization: Bearer <your_jwt_token>
```

#### Query Parameters

| 参数名 | 类型 | 必填 | 默认值 | 描述 |
|--------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 10 | 每页数量，最大50 |
| status | string | 否 | - | 项目状态筛选，支持多状态筛选，用逗号分隔 |
| requirement_id | integer | 否 | - | 需求ID筛选 |
| leader_id | integer | 否 | - | 负责人ID筛选 |
| keyword | string | 否 | - | 搜索关键词（项目标题、描述） |
| my_projects | string | 否 | - | true=我创建/负责的项目, false=我加入的项目, 不传=项目广场 |

#### 请求示例

```http
# 项目广场：获取所有公开项目，第1页，每页10条
GET /api/v1/studentproject/projects/?page=1&page_size=10

# 获取我负责的项目
GET /api/v1/studentproject/projects/?my_projects=true&page=1&page_size=10

# 获取我加入的项目
GET /api/v1/studentproject/projects/?my_projects=false&page=1&page_size=10

# 搜索包含"AI"关键词的进行中项目（项目广场）
GET /api/v1/studentproject/projects/?keyword=AI&status=in_progress

# 获取特定需求的所有项目
GET /api/v1/studentproject/projects/?requirement_id=123

# 获取特定用户负责的项目
GET /api/v1/studentproject/projects/?leader_id=456
```

### 响应格式

#### 成功响应 (200 OK)

```json
{
    "success": true,
    "message": "项目列表获取成功",
    "data": {
        "projects": [
            {
                "id": 123,
                "title": "基于深度学习的图像识别系统",
                "description": "本项目旨在开发一个高精度的图像识别系统...",
                "status": "in_progress",
                "requirement": {
                    "id": 456,
                    "title": "智能图像处理技术开发",
                    "organization_name": "科技创新实验室"
                },
                "leader": {
            "id": 789,
            "real_name": "张三",
            "school": "清华大学",
            "major": "计算机科学与技术",
            "grade": "2021",
            "email": "zhang***@example.com",
            "phone": "138****8000"
        },
                "participant_count": 3,
                "created_at": "2024-01-20T14:30:00Z",
                "updated_at": "2024-01-22T10:15:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "total_count": 48,
            "page_size": 10,
            "has_next": true,
            "has_previous": false
        }
    }
}
```

#### 错误响应

**401 Unauthorized - 未认证**
```json
{
    "detail": "身份认证信息未提供。"
}
```

**403 Forbidden - 权限不足**
```json
{
    "detail": "您没有执行该操作的权限。"
}
```

**500 Internal Server Error - 服务器错误**
```json
{
    "success": false,
    "message": "获取项目列表失败"
}
```

### 筛选和搜索说明

#### 状态筛选
- 支持单个状态：`status=in_progress`
- 支持多个状态：`status=in_progress,recruiting,completed`
- 可用状态值：`draft`, `recruiting`, `in_progress`, `completed`, `suspended`, `cancelled`

#### 关键词搜索
- 在项目标题和描述中进行模糊匹配
- 不区分大小写
- 支持中英文搜索

#### 排序规则
- 默认按创建时间倒序排列（最新创建的项目在前）
- 确保用户能够快速找到最近的项目

---

## 5. 获取项目详情接口

### 接口信息

- **URL**: `GET /api/v1/studentproject/projects/<project_id>/`
- **权限**: 认证用户（根据参与关系动态判断）
- **功能**: 获取项目的详细信息，包括参与者、成果、评论等

### 权限说明

#### 权限说明

**学生用户权限：**
- 项目广场：可以查看所有公开项目
- 个人项目：可以使用 `my_projects` 参数查看自己创建/负责或参与的项目
- 项目详情：可以查看任何项目的详情

**组织用户权限：**
- 项目广场：可以查看所有公开项目
- 个人项目：`my_projects` 参数对组织用户无效，始终显示项目广场
- 项目详情：可以查看任何项目的详情

#### 个人信息展示规则

**项目负责人（leader）信息**:
- 所有用户都可以查看完整的联系信息（包括邮箱和手机号）

**项目参与者信息**:
- **完整信息展示**（无脱敏）：
  - 项目关联需求所属的组织用户
  - 项目内的参与者（已批准状态）
- **脱敏信息展示**：
  - 其他所有用户

**脱敏规则**:
- **邮箱脱敏**: 保留前2位字符和@后的域名，中间用*替代
  - 示例: `zhangsan@example.com` → `zh*****@example.com`
- **手机号脱敏**: 保留前3位和后3位，中间用*替代
  - 示例: `13800138000` → `138****8000`

#### Leader机制说明
**每个学生项目都必须有且仅有一个leader：**
- 项目创建时，创建者自动成为leader
- Leader可以转让给其他已批准的参与者（需要额外的转让接口）
- 项目必须始终保持有一个leader，确保项目管理的连续性
- Leader拥有项目的完全管理权限（修改、删除等）

### 请求参数

#### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

#### Headers
```http
Authorization: Bearer <your_jwt_token>
```

#### 请求示例

```http
GET /api/v1/studentproject/projects/123/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 响应格式

#### 成功响应 (200 OK)

```json
{
    "success": true,
    "message": "项目详情获取成功",
    "data": {
        "id": 123,
        "title": "基于深度学习的图像识别系统",
        "description": "本项目旨在开发一个高精度的图像识别系统，采用卷积神经网络技术，能够识别多种物体类别。项目将分为数据收集、模型训练、系统集成三个阶段。",
        "requirement": {
            "id": 456,
            "title": "智能图像处理技术开发",
            "description": "需要开发先进的图像处理算法",
            "budget": 50000.00,
            "required_people": 3,
            "status": "recruiting",
            "organization_name": "科技创新实验室",
            "created_at": "2024-01-15T10:30:00Z"
        },
        "status": "in_progress",
        "participants": [
            {
                "id": 789,
                "student": {
                    "id": 101,
                    "student_number": "2021001001",
                    "school": "清华大学",
                    "major": "计算机科学与技术",
                    "grade": "2021",
                    "real_name": "张三",
                    "username": "zhangsan",
                    "avatar": "/media/avatars/101/avatar.jpg"
                },
                "role": "leader",
                "status": "approved",
                "application_message": "项目创建者自动成为leader",
                "reviewed_by": null,
                "review_message": null,
                "applied_at": "2024-01-20T14:30:00Z",
                "reviewed_at": "2024-01-20T14:30:00Z"
            },
            {
                "id": 790,
                "student": {
                    "id": 102,
                    "student_number": "2021001002",
                    "school": "清华大学",
                    "major": "人工智能",
                    "grade": "2021",
                    "real_name": "李四",
                    "username": "lisi",
                    "avatar": "/media/avatars/102/avatar.jpg"
                },
                "role": "member",
                "status": "approved",
                "application_message": "我对深度学习很感兴趣，希望能参与这个项目",
                "reviewed_by": {
                    "id": 101,
                    "real_name": "张三"
                },
                "review_message": "欢迎加入！",
                "applied_at": "2024-01-21T09:15:00Z",
                "reviewed_at": "2024-01-21T10:30:00Z"
            }
        ],
        "deliverables": [
            {
                "id": 1,
                "title": "需求分析报告",
                "description": "项目需求的详细分析文档",
                "deliverable_type": "document",
                "status": "completed",
                "files": [
                    {
                        "id": 1,
                        "filename": "需求分析报告.pdf",
                        "file_size": 2048576,
                        "file_type": "application/pdf",
                        "upload_time": "2024-01-22T14:00:00Z"
                    }
                ],
                "submitted_by": {
                    "id": 101,
                    "real_name": "张三"
                },
                "created_at": "2024-01-22T14:00:00Z",
                "updated_at": "2024-01-22T14:00:00Z"
            }
        ],
        "recent_comments": [
            {
                "id": 1,
                "content": "项目进展顺利，需求分析已完成",
                "comment_type": "progress",
                "author": {
                    "id": 101,
                    "real_name": "张三",
                    "avatar": "/media/avatars/101/avatar.jpg"
                },
                "created_at": "2024-01-22T15:30:00Z"
            }
        ],
        "leader": {
            "id": 101,
            "student_number": "2021001001",
            "school": "清华大学",
            "major": "计算机科学与技术",
            "grade": "2021",
            "real_name": "张三",
            "username": "zhangsan",
            "avatar": "/media/avatars/101/avatar.jpg"
        },
        "created_at": "2024-01-20T14:30:00Z",
        "updated_at": "2024-01-22T15:30:00Z"
    }
}
```

#### 错误响应

**403 Forbidden - 权限不足**
```json
{
    "success": false,
    "message": "权限不足，您无法查看此项目详情"
}
```

**404 Not Found - 项目不存在**
```json
{
    "detail": "未找到。"
}
```

**401 Unauthorized - 未认证**
```json
{
    "detail": "身份认证信息未提供。"
}
```

**500 Internal Server Error - 服务器错误**
```json
{
    "success": false,
    "message": "获取项目详情失败"
}
```

### 数据结构说明

#### 参与者状态
- `pending`: 申请待审核
- `approved`: 已批准
- `rejected`: 已拒绝
- `withdrawn`: 已撤回

#### 参与者角色
- `leader`: 项目负责人（每个项目有且仅有一个）
- `member`: 普通成员

#### 成果类型
- `document`: 文档类成果
- `code`: 代码类成果
- `design`: 设计类成果
- `other`: 其他类型成果

#### 成果状态
- `draft`: 草稿
- `submitted`: 已提交
- `approved`: 已批准
- `rejected`: 已拒绝
- `completed`: 已完成

---

## 6. 组织数据概览接口

### 接口信息

- **URL**: `GET /api/v1/studentproject/organization/overview/`
- **权限**: 仅组织用户
- **功能**: 获取组织的数据概览统计信息

### 请求参数

#### Headers
```http
Authorization: Bearer <your_jwt_token>
```

#### 请求示例

```http
GET /api/v1/studentproject/organization/overview/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 响应格式

#### 成功响应 (200 OK)

```json
{
    "success": true,
    "message": "组织数据概览获取成功",
    "data": {
        "published_requirements": {
            "count": 45,
            "growth_rate": "12.5%"
        },
        "published_resources": {
            "count": 128,
            "growth_rate": "8.3%"
        },
        "in_progress_projects": {
            "count": 23,
            "growth_rate": "15.0%"
        },
        "project_completion_rate": {
            "rate": "78.5%",
            "growth_rate": "5.2%"
        },
        "monthly_progress": [
            {
                "month": "1月",
                "completed": 8,
                "in_progress": 5,
                "recruiting": 3
            },
            {
                "month": "2月",
                "completed": 12,
                "in_progress": 7,
                "recruiting": 4
            },
            {
                "month": "3月",
                "completed": 15,
                "in_progress": 9,
                "recruiting": 6
            }
        ],
        "skill_distribution": [
            {
                "skill": "Python开发",
                "count": 25,
                "percentage": 18.5
            },
            {
                "skill": "前端开发",
                "count": 22,
                "percentage": 16.3
            },
            {
                "skill": "数据分析",
                "count": 18,
                "percentage": 13.3
            },
            {
                "skill": "机器学习",
                "count": 15,
                "percentage": 11.1
            },
            {
                "skill": "移动开发",
                "count": 12,
                "percentage": 8.9
            }
        ]
    }
}
```

#### 错误响应

**403 Forbidden - 权限不足**
```json
{
    "success": false,
    "message": "您不是组织用户，无权访问此数据",
    "data": {}
}
```

**401 Unauthorized - 未认证**
```json
{
    "detail": "身份认证信息未提供。"
}
```

**500 Internal Server Error - 服务器错误**
```json
{
    "success": false,
    "message": "获取组织数据概览失败",
    "data": {}
}
```

### 数据说明

#### 统计指标

| 字段 | 描述 | 计算方式 |
|------|------|----------|
| published_requirements | 发布需求统计 | 累计发布的需求数量及相比上月同期增长率 |
| published_resources | 发布资源统计 | 累计发布的资源数量及相比上月同期增长率 |
| in_progress_projects | 进行中项目统计 | 当前进行中的学生项目数量及增长率 |
| project_completion_rate | 项目完成率统计 | 项目完成率及相比上月同期的增长率 |
| monthly_progress | 项目进度统计 | 按月统计当前年份已过月份的项目状态分布 |
| skill_distribution | 技能分布统计 | 需求中最常见的前10个技能标签及其占比 |

#### 增长率计算

增长率计算公式：`((当前值 - 上月同期值) / 上月同期值) × 100%`

- 正值表示增长，负值表示下降
- 当上月同期值为0时，增长率显示为0%
- 所有增长率保留2位小数

#### 月度进度统计

- 仅统计当前年份已过的完整月份
- 包含三种项目状态：已完成(completed)、进行中(in_progress)、招募中(recruiting)
- 按项目创建时间进行月份归类

#### 技能分布统计

- 基于组织发布的所有需求关联的Tag2标签
- 返回出现频次最高的前10个技能标签
- 计算每个技能标签在所有标签中的占比
- 按出现次数降序排列



---

## 7. 项目参与者管理接口

### 7.1 申请加入项目

#### 接口信息

- **URL**: `POST /api/v1/studentproject/projects/<project_id>/apply/`
- **权限**: 学生用户
- **功能**: 学生用户申请加入项目

#### 请求参数

##### Headers
```http
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

##### Body Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| role | string | 否 | 参与角色，默认为"member" |
| application_message | string | 是 | 申请理由，最大长度500字符 |

##### 请求示例

```json
{
    "role": "member",
    "application_message": "我对这个项目很感兴趣，希望能够参与其中，我有相关的技术背景和经验..."
}
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "status": "success",
    "code": 200,
    "message": "申请提交成功，请等待项目负责人审核",
    "data": {},
    "error": {}
}
```

##### 错误响应

**400 Bad Request - 重复申请**
```json
{
    "status": "error",
    "code": 400,
    "message": "您已经申请过该项目或已是项目成员",
    "data": {},
    "error": {}
}
```

**403 Forbidden - 权限不足**
```json
{
    "status": "error",
    "code": 403,
    "message": "只有学生用户可以申请加入项目",
    "data": {},
    "error": {}
}
```

**404 Not Found - 项目不存在**
```json
{
    "detail": "未找到。"
}
```

### 7.2 处理申请（统一接口）

#### 接口信息

- **URL**: `POST /api/v1/studentproject/projects/<project_id>/applications/handle/`
- **权限**: 项目负责人
- **功能**: 项目负责人处理加入申请，支持单个和批量处理，支持form-data格式

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

##### Body Parameters（支持JSON和form-data格式）

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| participant_ids | string | 是 | 参与者申请记录ID，单个ID或多个ID用逗号分隔（如："1" 或 "1,2,3"） |
| action | string | 是 | 处理动作："approve"(同意) 或 "reject"(拒绝) |
| review_message | string | 否 | 审核留言，最大长度500字符 |

##### 请求示例

**单个申请处理（JSON格式）**
```json
{
    "participant_ids": "1",
    "action": "approve",
    "review_message": "欢迎加入项目团队！"
}
```

**批量申请处理（JSON格式）**
```json
{
    "participant_ids": "1,2,3",
    "action": "approve",
    "review_message": "欢迎加入项目团队！"
}
```

**form-data格式示例**
```
participant_ids: 1,2,3
action: approve
review_message: 欢迎加入项目团队！
```

#### 响应格式

##### 成功响应 (200 OK)

**单个申请处理**
```json
{
    "status": "success",
    "code": 200,
    "message": "申请已通过",
    "data": {},
    "error": {}
}
```

**批量申请处理**
```json
{
    "status": "success",
    "code": 200,
    "message": "成功通过了 3 个申请",
    "data": {},
    "error": {}
}
```

### 7.3 获取项目参与者列表

#### 接口信息

- **URL**: `GET /api/v1/studentproject/projects/<project_id>/participants/`
- **权限**: 项目成员或负责人
- **功能**: 获取项目参与者列表和待审核申请

#### 请求参数

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "status": "success",
    "code": 200,
    "message": "获取成功",
    "data": {
        "participants": [
            {
                "id": 1,
                "student": {
                    "id": 1,
                    "user": {
                        "id": 1,
                        "real_name": "张三",
                        "username": "zhangsan"
                    },
                    "student_id": "2021001",
                    "school": "清华大学",
                    "major": "计算机科学与技术"
                },
                "role": "leader",
                "status": "approved",
                "applied_at": "2024-01-15T10:30:00Z"
            }
        ],
        "pending_applications": [
            {
                "id": 2,
                "student": {
                    "id": 2,
                    "user": {
                        "id": 2,
                        "real_name": "李四",
                        "username": "lisi"
                    },
                    "student_id": "2021002",
                    "school": "北京大学",
                    "major": "软件工程"
                },
                "role": "member",
                "status": "pending",
                "application_message": "我对这个项目很感兴趣...",
                "applied_at": "2024-01-20T14:30:00Z"
            }
        ],
        "total_participants": 1,
        "total_pending": 1
    },
    "error": {}
}
```

### 7.4 获取参与者详情

#### 接口信息

- **URL**: `GET /api/v1/studentproject/projects/<project_id>/participants/<participant_id>/`
- **权限**: 项目成员或负责人
- **功能**: 获取特定参与者的详细信息

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "status": "success",
    "code": 200,
    "message": "获取成功",
    "data": {
        "id": 1,
        "student": {
            "id": 1,
            "user": {
                "id": 1,
                "real_name": "张三",
                "username": "zhangsan",
                "email": "zhangsan@example.com"
            },
            "student_id": "2021001",
            "school": "清华大学",
            "major": "计算机科学与技术",
            "grade": "大三",
            "phone": "13800138000"
        },
        "role": "leader",
        "status": "approved",
        "application_message": "我想创建这个项目...",
        "review_message": "项目创建者",
        "applied_at": "2024-01-15T10:30:00Z",
        "reviewed_at": "2024-01-15T10:30:00Z"
    },
    "error": {}
}
```

### 7.5 修改参与者状态

#### 接口信息

- **URL**: `PUT /api/v1/studentproject/projects/<project_id>/participants/<participant_id>/status/`
- **权限**: 项目负责人或参与者本人（限制条件见下方）
- **功能**: 统一的参与者状态修改接口，支持踢出成员、激活成员和用户自行退出项目

#### 请求参数

##### Body Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| status | string | 是 | 新状态："approved"(激活), "rejected"(停用), "left"(移除/踢出) |
| reason | string | 否 | 状态变更原因，最大长度500字符 |

##### 请求示例

**踢出成员：**
```json
{
    "status": "left",
    "reason": "违反项目规定"
}
```

**激活成员：**
```json
{
    "status": "approved",
    "reason": "重新激活参与"
}
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "status": "success",
    "code": 200,
    "message": "参与者状态已更新为移除",
    "data": {},
    "error": {}
}
```

#### 权限控制

**项目负责人权限：**
- 可以修改所有普通成员的状态
- 不能修改自己的状态（负责人不能直接退出项目，需要先转移负责人身份）
- 不能修改其他负责人的状态
- 踢出成员时，被踢出者会收到通知

**项目参与者权限：**
- 只能修改自己的状态
- 只能将自己的状态设置为"left"（退出项目）
- 退出时项目负责人会收到通知

#### 注意事项

- 状态变更会自动发送相应通知
- "left"状态表示成员已离开项目（主动退出或被踢出）
- "approved"状态表示成员正常参与项目
- "rejected"状态表示成员被暂停参与
- 返回消息中会包含被操作者的真实姓名信息

### 7.6 转移负责人身份

#### 接口信息

- **URL**: `POST /api/v1/studentproject/projects/<project_id>/transfer-leadership/`
- **权限**: 项目负责人
- **功能**: 将负责人身份转移给其他参与者

#### 请求参数

##### Body Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| new_leader_id | integer | 是 | 新负责人的参与者记录ID |
| transfer_message | string | 否 | 转移说明，最大长度200字符 |

##### 请求示例

```json
{
    "new_leader_id": 5,
    "transfer_message": "由于个人原因，将负责人身份转移给更合适的成员"
}
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "status": "success",
    "code": 200,
    "message": "负责人身份转移成功",
    "data": {},
    "error": {}
}
```

### 7.7 发送项目邀请

#### 接口信息

- **URL**: `POST /api/v1/studentproject/projects/<project_id>/send-invitation/`
- **权限**: 项目负责人
- **功能**: 项目负责人邀请学生用户加入项目

#### 请求参数

##### Headers
```http
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| project_id | integer | 是 | 项目ID |

##### Body Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| invitee_username | string | 是 | 被邀请学生的用户名，最大长度30字符 |
| invitation_message | string | 否 | 邀请留言，最大长度500字符 |

##### 请求示例

```json
{
    "invitee_username": "student_zhang",
    "invitation_message": "我们的项目需要您的专业技能，希望您能加入我们的团队..."
}
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "status": "success",
    "code": 200,
    "message": "已成功向 张三 发送邀请",
    "data": {
        "id": 1,
        "project": {
            "id": 1,
            "title": "智能学习平台开发"
        },
        "inviter": {
            "id": 1,
            "real_name": "李四",
            "student_id": "2021001"
        },
        "invitee": {
            "id": 123,
            "real_name": "张三",
            "student_id": "2021123"
        },
        "status": "pending",
        "invitation_message": "我们的项目需要您的专业技能，希望您能加入我们的团队...",
        "created_at": "2024-01-15T10:30:00Z",
        "expires_at": "2024-01-22T10:30:00Z"
    },
    "error": {}
}
```

##### 错误响应

- **400 Bad Request**: 请求参数错误
- **403 Forbidden**: 只有项目负责人可以发送邀请
- **404 Not Found**: 项目或被邀请学生不存在
- **409 Conflict**: 该学生已是项目成员或已有待处理邀请

#### 注意事项

- 只有项目负责人可以发送邀请
- 不能邀请已经是项目成员的学生
- 不能邀请已有待审核申请的学生
- 同一学生同一项目只能有一个待处理的邀请
- 邀请有效期为7天，过期后自动失效
- 发送邀请时会自动通知被邀请者

### 7.8 响应项目邀请

#### 接口信息

- **URL**: `POST /api/v1/studentproject/invitations/<invitation_id>/respond/`
- **权限**: 被邀请的学生用户
- **功能**: 被邀请学生接受或拒绝项目邀请

#### 请求参数

##### Headers
```http
Content-Type: application/json
Authorization: Bearer <your_jwt_token>
```

##### URL Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| invitation_id | integer | 是 | 邀请ID |

##### Body Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| action | string | 是 | 响应动作："accept"(接受) 或 "reject"(拒绝) |
| response_message | string | 否 | 响应留言，最大长度200字符 |

##### 请求示例

```json
{
    "action": "accept",
    "response_message": "很高兴能加入这个项目，期待与团队合作！"
}
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "status": "success",
    "code": 200,
    "message": "已成功加入项目 \"智能学习平台开发\"",
    "data": {
        "id": 1,
        "project": {
            "id": 1,
            "title": "智能学习平台开发"
        },
        "inviter": {
            "id": 1,
            "real_name": "李四",
            "student_id": "2021001"
        },
        "invitee": {
            "id": 123,
            "real_name": "张三",
            "student_id": "2021123"
        },
        "status": "accepted",
        "invitation_message": "我们的项目需要您的专业技能...",
        "response_message": "很高兴能加入这个项目，期待与团队合作！",
        "created_at": "2024-01-15T10:30:00Z",
        "responded_at": "2024-01-15T14:20:00Z"
    },
    "error": {}
}
```

##### 错误响应

- **400 Bad Request**: 请求参数错误
- **403 Forbidden**: 无权响应此邀请
- **404 Not Found**: 邀请不存在
- **409 Conflict**: 邀请已过期或已处理

#### 注意事项

- 只有被邀请者本人可以响应邀请
- 邀请过期后无法响应
- 已处理的邀请无法重复响应
- 接受邀请后会直接成为项目成员，无需审核
- 响应邀请时会自动通知邀请者

### 7.9 获取邀请列表

#### 接口信息

- **URL**: `GET /api/v1/studentproject/invitations/`
- **权限**: 学生用户
- **功能**: 获取发出的邀请和收到的邀请列表

#### 请求参数

##### Headers
```http
Authorization: Bearer <your_jwt_token>
```

##### Query Parameters

| 参数名 | 类型 | 必填 | 描述 |
|--------|------|------|------|
| type | string | 否 | 邀请类型："received"(收到的，默认) 或 "sent"(发出的) |
| status | string | 否 | 邀请状态："pending", "accepted", "rejected", "expired" |
| page | integer | 否 | 页码，默认为1 |
| page_size | integer | 否 | 每页数量，默认为10 |

##### 请求示例

```
GET /api/v1/studentproject/invitations/?type=received&status=pending&page=1&page_size=10
```

#### 响应格式

##### 成功响应 (200 OK)

```json
{
    "status": "success",
    "code": 200,
    "message": "获取成功",
    "data": {
        "invitations": [
            {
                "id": 1,
                "project": {
                    "id": 1,
                    "title": "智能学习平台开发",
                    "description": "基于AI的个性化学习平台..."
                },
                "inviter": {
                    "id": 1,
                    "real_name": "李四",
                    "student_id": "2021001"
                },
                "invitee": {
                    "id": 123,
                    "real_name": "张三",
                    "student_id": "2021123"
                },
                "status": "pending",
                "invitation_message": "我们的项目需要您的专业技能...",
                "response_message": null,
                "created_at": "2024-01-15T10:30:00Z",
                "responded_at": null,
                "expires_at": "2024-01-22T10:30:00Z",
                "is_expired": false
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 3,
            "total_count": 25,
            "has_next": true,
            "has_previous": false
        }
    },
    "error": {}
}
```

##### 错误响应

- **401 Unauthorized**: 未登录或token无效
- **403 Forbidden**: 权限不足

#### 注意事项

- 支持分页查询
- 可按邀请类型和状态筛选
- 返回数据包含邀请的完整信息
- 自动计算邀请是否过期

## 接口权限说明

### 用户类型权限

| 操作 | 学生用户 | 组织用户 | 管理员 |
|------|----------|----------|--------|
| 申请加入项目 | ✅ | ❌ | ✅ |
| 处理申请 | ✅ (仅负责人) | ❌ | ✅ |
| 查看参与者 | ✅ (项目成员) | ✅ (关联需求) | ✅ |
| 修改参与者状态 | ✅ (负责人可修改所有成员，成员只能退出) | ❌ | ✅ |
| 转移负责人 | ✅ (仅负责人) | ❌ | ✅ |
| 发送项目邀请 | ✅ (仅负责人) | ❌ | ✅ |
| 响应项目邀请 | ✅ (仅被邀请者) | ❌ | ✅ |
| 查看邀请列表 | ✅ | ❌ | ✅ |

### 参与者状态说明

| 状态值 | 中文名称 | 描述 |
|--------|----------|------|
| pending | 待审核 | 申请已提交，等待负责人审核 |
| approved | 已通过 | 申请已通过，正常参与项目 |
| rejected | 已拒绝 | 申请被拒绝 |
| suspended | 已暂停 | 参与者被暂停参与项目 |
| removed | 已移除 | 参与者被移除出项目 |

### 通知机制

系统会在以下情况自动发送通知：

1. **申请提交时**: 向项目负责人发送新申请通知
2. **申请处理时**: 向申请者发送审核结果通知
3. **参与者状态变更时**: 向被操作者发送状态变更通知
4. **负责人转移时**: 向新旧负责人发送转移通知
5. **发送邀请时**: 向被邀请者发送邀请通知
6. **响应邀请时**: 向邀请者发送响应结果通知

---

## 成果管理注意事项

### 版本管理

1. **版本号规则**：
   - 每个成果都有全局版本号（version_number）和阶段版本号（stage_version）
   - 同一阶段类型的成果会自动递增阶段版本号
   - 版本链通过parent_deliverable字段维护父子关系

2. **阶段类型**：
   - `initial`: 初始版本
   - `revision`: 修订版本
   - `final`: 最终版本

### 权限控制

| 操作 | 项目参与者 | 项目负责人 | 组织用户 |
|------|------------|------------|----------|
| 提交成果 | ✅ | ✅ | ❌ |
| 更新成果 | ✅ | ✅ | ❌ |
| 弃用成果 | ✅ | ✅ | ❌ |
| 查看成果列表 | ✅ | ✅ | ✅ (关联需求) |
| 查看成果详情 | ✅ | ✅ | ✅ (关联需求) |

### 文件支持

1. **支持的文件类型**：
   - 关联现有文件ID（通过files_ids参数）
   - 直接上传文件（通过uploaded_files参数）
   - 网盘链接（百度网盘、阿里云盘等，通过cloud_links参数）

2. **文件管理规则**：
   - 提交成果时支持所有文件类型
   - 更新成果时不支持修改实体文件，仅支持修改网盘链接
   - 弃用成果不会删除关联的文件，仅标记成果状态

### Form-Data格式说明

**提交成果和更新成果接口使用`multipart/form-data`格式**：

1. **参数格式**：
   - `files_ids`: 逗号分隔的字符串（如："1,2,3"）
   - `cloud_links`: 网盘链接地址字符串（如："https://pan.baidu.com/s/xxx"）
   - `cloud_password`: 网盘链接提取密码字符串（可选）
   - `uploaded_files`: 支持多文件上传，可重复使用该字段名
   - 其他文本参数直接作为form-data字段传递

2. **网盘链接说明**：
   - `cloud_links`: 直接提供网盘链接URL，系统会自动创建名为"网盘链接"的文件记录
   - `cloud_password`: 可选的提取密码，与cloud_links配合使用
   - 网盘链接文件统一命名为"网盘链接"，不保存实体文件相关信息（如path、size等）

3. **虚拟文件夹**：
   - 通过`virtual_folder_path`参数指定文件存储的虚拟路径
   - 默认路径为"/"，可自定义如"/deliverables/stage1"
   - 系统会自动创建不存在的虚拟文件夹

---

## 更新日志

- **v1.3.1** (2024-01-24): 优化网盘链接格式，cloud_links改为字符串格式直接存储链接地址，新增cloud_password字段存储密码，统一网盘文件名为"网盘链接"
- **v1.3.0** (2024-01-23): 新增项目成果管理接口，支持成果提交、更新、弃用、列表查看和详情查看功能，采用form-data格式支持文件上传
- **v1.2.0** (2024-01-22): 新增项目参与者管理接口，支持申请加入、审核处理、状态管理和负责人转移功能
- **v1.1.0** (2024-01-21): 新增组织数据概览接口，支持多维度数据统计和增长率分析
- **v1.0.0** (2024-01-20): 初始版本，实现基础的项目CRUD功能