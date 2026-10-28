# 校企对接平台 - 需求管理API文档

## 概述

本文档描述了校企对接平台需求管理相关API接口，包括需求的发布、查看、更新、删除等功能。

## 技术特性

- **权限验证**: 所有接口都需要用户认证，部分操作需要特定组织权限
- **数据验证**: 完整的请求参数验证和错误提示
- **关联关系处理**: 支持标签、资源、文件等多对多关联关系
- **浏览统计**: 自动记录需求浏览次数
- **分页支持**: 列表接口支持分页查询
- **搜索支持**: 支持按标题、描述、领域等条件搜索
- **虚拟文件系统**: 采用独立的虚拟文件系统管理文件，支持文件夹结构和文件操作
- **文件关联管理**: 需求与文件的关联通过专用接口管理，实现职责分离

## 文件管理说明

### 文件管理架构

本系统采用**虚拟文件系统**进行文件管理，将文件操作与需求管理分离：

1. **虚拟文件系统**
   - 独立的文件管理模块，支持文件夹层级结构
   - 提供完整的文件CRUD操作（创建、读取、更新、删除）
   - 支持文件夹创建、重命名、移动等操作
   - 通过专用API接口 `/api/v1/project/virtual-files/` 进行管理

2. **需求文件关联**
   - 新建需求时只能关联已存在的文件（通过`files_ids`参数）
   - 修改需求时不支持文件操作，文件管理通过虚拟文件系统完成
   - 文件夹不能直接关联到需求，系统会自动验证并阻止此操作

3. **文件上传流程**
   - 第一步：通过虚拟文件系统API上传文件到指定路径
   - 第二步：在创建需求时引用已上传的文件ID
   - 这种设计确保了文件管理的一致性和可维护性

### 文件数据结构

系统中的文件信息包含以下字段：

```json
{
  "id": 1,
  "name": "document.pdf",
  "path": "/projects/requirement_docs/document.pdf",
  "url": "http://localhost:8000/media/files/document.pdf",
  "size": 1024000,
  "is_folder": false,
  "created_at": "2024-01-20T10:00:00Z"
}
```

### 虚拟文件系统API

虚拟文件系统为每个需求(Requirement)或资源(Resource)提供独立的文件管理空间。所有虚拟文件系统接口都需要指定 `requirement_id` 或 `resource_id` 参数来确定操作的目标对象。

#### 主要接口列表：

**需求相关的虚拟文件系统：**
- `GET /api/v1/project/virtual-files/?requirement_id={requirement_id}` - 获取指定需求的文件列表
- `GET /api/v1/project/virtual-files/{file_id}/?requirement_id={requirement_id}` - 获取指定需求中单个文件的详情
- `POST /api/v1/project/virtual-files/upload_file/?requirement_id={requirement_id}` - 向指定需求上传文件
- `POST /api/v1/project/virtual-files/create_folder/?requirement_id={requirement_id}` - 在指定需求中创建文件夹
- `PUT /api/v1/project/virtual-files/{id}/rename/?requirement_id={requirement_id}` - 重命名指定需求中的文件/文件夹
- `PUT /api/v1/project/virtual-files/{id}/move/?requirement_id={requirement_id}` - 移动指定需求中的文件/文件夹
- `DELETE /api/v1/project/virtual-files/{id}/?requirement_id={requirement_id}` - 删除指定需求中的文件/文件夹
- `GET /api/v1/project/virtual-files/tree_structure/?requirement_id={requirement_id}` - 获取指定需求的文件树结构
- `GET /api/v1/project/virtual-files/breadcrumb/?requirement_id={requirement_id}&path={path}` - 获取指定需求中路径的面包屑导航

**资源相关的虚拟文件系统：**
- `GET /api/v1/project/virtual-files/?resource_id={resource_id}` - 获取指定资源的文件列表
- `GET /api/v1/project/virtual-files/{file_id}/?resource_id={resource_id}` - 获取指定资源中单个文件的详情
- `POST /api/v1/project/virtual-files/upload_file/?resource_id={resource_id}` - 向指定资源上传文件
- `POST /api/v1/project/virtual-files/create_folder/?resource_id={resource_id}` - 在指定资源中创建文件夹
- `PUT /api/v1/project/virtual-files/{id}/rename/?resource_id={resource_id}` - 重命名指定资源中的文件/文件夹
- `PUT /api/v1/project/virtual-files/{id}/move/?resource_id={resource_id}` - 移动指定资源中的文件/文件夹
- `DELETE /api/v1/project/virtual-files/{id}/?resource_id={resource_id}` - 删除指定资源中的文件/文件夹
- `GET /api/v1/project/virtual-files/tree_structure/?resource_id={resource_id}` - 获取指定资源的文件树结构
- `GET /api/v1/project/virtual-files/breadcrumb/?resource_id={resource_id}&path={path}` - 获取指定资源中路径的面包屑导航

**注意事项：**
- 每个接口调用时必须且只能指定 `requirement_id` 或 `resource_id` 中的一个
- 不同需求/资源的虚拟文件系统是完全独立的，互不影响
- 文件的虚拟路径在同一个需求/资源内必须唯一

## 基础信息

- **基础URL**: `/api/v1/project/`
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

## 数据模型

### Requirement 模型
- `id`: 需求ID (字符串)
- `title`: 需求标题
- `brief`: 需求简介
- `description`: 详细描述
- `tags`: 标签字符串（逗号分隔）
- `status`: 需求状态 (`under_review`, `review_failed`, `in_progress`, `completed`, `paused`)
- `organization`: 组织信息对象
- `publish_people`: 发布人姓名
- `finish_time`: 完成时间
- `budget`: 预算
- `people_count`: 人数需求
- `applications`: 申请数
- `views`: 浏览数
- `resources`: 关联资源列表
- `files`: 文件信息列表
- `evaluation_criteria_id`: 评分标准ID (可选，关联到项目评分标准)

### Organization 模型
- `id`: 组织ID
- `name`: 组织名称
- `logo`: 组织logo
- `status`: 组织状态

### Resource 模型
- `id`: 资源ID
- `title`: 资源标题
- `type`: 资源类型

### File 模型
- `id`: 文件ID
- `url`: 文件下载链接
- `name`: 文件名
- `path`: 文件路径
- `size`: 文件大小（字节）
- `create_time`: 创建时间

## API接口

### 1. 需求收藏功能

#### 1.1 切换需求收藏状态

**接口**: `POST /api/v1/project/requirement/favorite/`
**描述**: 学生用户切换指定需求的收藏状态（未收藏则收藏，已收藏则取消收藏）
**权限**: 认证用户（仅限学生用户）

##### 请求头
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

##### 请求参数
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|----------|
| requirement_id | String | 是 | 需求ID |

##### 请求示例
```json
{
    "requirement_id": "req_001"
}
```

##### 响应示例

**收藏成功时**:
```json
{
    "status": "success",
    "code": 200,
    "message": "收藏成功",
    "data": {
        "is_favorited": true,
        "favorite_info": {
            "id": 1,
            "student": {
                "id": 1,
                "user": {
                    "username": "student001",
                    "email": "student@example.com"
                }
            },
            "requirement": {
                "id": "req_001",
                "title": "AI智能推荐系统开发",
                "brief": "基于机器学习的个性化推荐系统"
            },
            "created_at": "2024-01-20T10:00:00Z"
        }
    },
    "error": {}
}
```

**取消收藏成功时**:
```json
{
    "status": "success",
    "code": 200,
    "message": "取消收藏成功",
    "data": {
        "is_favorited": false
    },
    "error": {}
}
```

#### 1.2 获取收藏的需求列表

**接口**: `GET /api/v1/project/favorites/requirements/`
**描述**: 获取当前学生用户收藏的需求列表，支持分页和筛选
**权限**: 认证用户（仅限学生用户）

##### 请求头
```
Authorization: Bearer <access_token>
```

##### 查询参数
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10)
- `status`: 需求状态筛选
- `organization_id`: 组织ID筛选
- `search`: 关键词搜索（可从需求标题、简介、描述中搜索）
- `ordering`: 排序方式
  - `-created_at`: 按收藏时间降序（默认）
  - `created_at`: 按收藏时间升序
  - `-requirement__created_at`: 按需求创建时间降序
  - `requirement__created_at`: 按需求创建时间升序

##### 请求示例
```
# 基本查询
GET /api/v1/project/favorites/requirements/?page=1&page_size=10

# 状态筛选
GET /api/v1/project/favorites/requirements/?status=in_progress

# 关键词搜索
GET /api/v1/project/favorites/requirements/?search=AI

# 排序查询
GET /api/v1/project/favorites/requirements/?ordering=-requirement__created_at
```

##### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "results": [
            {
                "id": 1,
                "student": {
                    "id": 1,
                    "user": {
                        "username": "student001",
                        "email": "student@example.com"
                    }
                },
                "requirement": {
                    "id": "req_001",
                    "title": "AI智能推荐系统开发",
                    "brief": "基于机器学习的个性化推荐系统",
                    "description": "开发一个基于用户行为分析的智能推荐系统",
                    "status": "in_progress",
                    "organization": {
                        "id": 1,
                        "name": "科技创新公司",
                        "logo": "http://localhost:8000/media/logos/company_logo.jpg"
                    },
                    "publish_people": "张经理",
                    "budget": "50000-100000",
                    "people_count": "3-5人",
                    "views": 156,
                    "applications": 12,
                    "evaluation_criteria": {
                        "id": 1,
                        "name": "AI项目评分标准",
                        "description": "针对人工智能项目的综合评分标准",
                        "status": "active",
                        "indicator_count": 5,
                        "total_weight": 100.0,
                        "created_at": "2024-01-10T09:00:00Z"
                    }
                },
                "created_at": "2024-01-20T10:00:00Z"
            }
        ],
        "pagination": {
            "count": 5,
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
    },
    "error": {}
}
```

#### 1.3 检查需求收藏状态

**接口**: `GET /api/v1/project/requirement/{requirement_id}/favorite-status/`
**描述**: 检查当前学生用户是否已收藏指定需求
**权限**: 认证用户

##### 请求头
```
Authorization: Bearer <access_token>
```

##### 路径参数
- `requirement_id`: 需求ID

##### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "is_favorited": true
    },
    "error": {}
}
```

**注意事项**:
- 只有学生用户可以使用收藏功能
- 切换收藏状态接口会自动判断当前状态并执行相应操作
- 不能收藏状态为 `under_review`（审核中）的需求，其他状态的需求均可收藏
- 收藏列表支持多种筛选和排序方式
- 非学生用户调用收藏状态检查接口时，`is_favorited` 始终返回 `false`
- 切换收藏状态接口返回的 `is_favorited` 字段表示操作后的收藏状态

### 2. 需求列表

**接口**: `GET /api/v1/project/requirements/list/`
**描述**: 获取需求列表，支持分页和筛选
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 查询参数
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10, 最大: 100)
- `budget`: 需求预算筛选（支持范围筛选，格式：min-max 或 单个值，单位默认为元）
  - 范围筛选：`budget=500000-1000000` 筛选预算在50万-100万元范围内的需求
  - 单值筛选：`budget=1000000` 筛选预算包含1000000的需求
  - 关键词筛选：`budget=500000` 筛选预算包含"500000"的需求
  - **注意**：系统会智能处理数据库中存储的范围格式预算（如"500000-1000000"），确保范围筛选的准确性
- `time`: 需求创建时间筛选（支持单日和范围筛选）
  - 单日筛选：`time=2025-08-19` 筛选指定日期创建的需求
  - 范围筛选：`time=2025-04-01-2025-08-18` 筛选指定日期范围内创建的需求
  - **注意**：时间筛选已优化时区处理，确保筛选结果的准确性
- `status`: 需求状态筛选（支持多状态查询，用逗号分隔多个状态值）
  - 单状态筛选：`status=in_progress` 筛选进行中的需求
  - 多状态筛选：`status=pending,in_progress,completed` 筛选待审核、进行中和已完成的需求
- `organization_id`: 组织ID筛选
- `sort_type`: 排序字段（title/time/view）
- `sort_order`: 排序方式（up升序/down降序）
- `keyword`: 搜索关键词（可从需求标题、描述、tag1和tag2中模糊检索）

#### 请求示例
```
# 基本查询
GET /api/v1/project/requirements/?page=1&page_size=10&status=in_progress

# 多状态查询
GET /api/v1/project/requirements/?status=pending,in_progress,completed

# 预算范围筛选
GET /api/v1/project/requirements/?budget=500000-1000000

# 单日时间筛选
GET /api/v1/project/requirements/?time=2025-08-19

# 时间范围筛选
GET /api/v1/project/requirements/?time=2025-04-01-2025-08-18

# 排序查询
GET /api/v1/project/requirements/?sort_type=view&sort_order=down

# 关键词搜索
GET /api/v1/project/requirements/?keyword=人工智能

# 组合查询
GET /api/v1/project/requirements/?page=1&page_size=20&status=in_progress&organization_id=1&sort_type=time&sort_order=down&keyword=AI
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "count": 25,
        "next": "http://localhost:8000/api/v1/project/requirements/?page=2",
        "previous": null,
        "results": [
            {
                "id": "req_001",
                "title": "AI智能推荐系统开发",
                "brief": "基于机器学习的个性化推荐系统",
                "description": "开发一个基于用户行为分析的智能推荐系统",

                "tags": "机器学习, 推荐算法, Python",
                "status": "in_progress",
                "organization": {
                    "id": 1,
                    "name": "科技创新公司",
                    "logo": "http://localhost:8000/media/logos/company_logo.jpg",
                    "status": "verified"
                },
                "publish_people": "张经理",
                "finish_time": "2024-06-30 18:00:00",
                "budget": "50000-100000",
                "people_count": "3-5人",
                "applications": 12,
                "views": 156,
                "evaluation_criteria": {
                    "id": 1,
                    "name": "AI项目评分标准",
                    "description": "针对人工智能项目的综合评分标准",
                    "status": "active",
                    "indicator_count": 5,
                    "total_weight": 100.0,
                    "created_at": "2024-01-10T09:00:00Z"
                },
                "resources": [
                    {
                        "id": "res_001",
                        "title": "推荐算法代码库",
                        "type": "code",

                    }
                ],
                "files": [
                    {
                        "id": 1,
                        "url": "http://localhost:8000/media/files/requirement_doc.pdf",
                        "name": "需求说明书.pdf",
                        "path": "/media/files/requirement_doc.pdf",
                        "size": 2048576,
                        "created_at": "2024-01-15T10:00:00Z"
                    }
                ]
            }
        ]
    },
    "error": {}
}
```

### 2. 发布需求

**接口**: `POST /api/v1/project/requirement/`
**描述**: 发布新需求，支持JSON格式和form-data格式（可直接上传文件）
**权限**: 认证用户（组织管理员或所有者）

**默认值设置**:
- `status`: 默认为 `under_review`（待审核），由系统管理员审核通过后开始招募
- `organization`: 默认为发布者所属的组织信息（如果用户属于多个组织，取第一个）

#### 文件处理方式

支持两种文件处理方式：
1. **关联已存在文件**: 通过 `files_ids` 参数关联已上传到虚拟文件系统的文件
2. **直接上传文件**: 通过 `files` 参数直接上传新文件（仅支持form-data格式）

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|----------|
| title | String | 是 | 需求标题 |
| brief | String | 是 | 需求简介 |
| description | String | 是 | 详细描述 |
| status | String | 否 | 需求状态（默认：under_review） |
| organization | Integer | 否 | 组织ID（默认：发布者所属组织） |
| finish_time | String | 否 | 完成时间 |
| budget | String | 否 | 预算 |
| people_count | String | 否 | 人数需求 |
| evaluation_criteria_id | Integer | 否 | 评分标准ID（关联到项目评分标准） |
| tag1_ids | String | 否 | 兴趣标签ID列表（逗号分隔，如"1,2,3"） |
| tag2_ids | String | 否 | 能力标签ID列表（逗号分隔，如"4,5,6"） |
| resource_ids | String | 否 | 关联资源ID列表（逗号分隔，如"res_001,res_002"） |
| files_ids | String | 否 | 文件ID列表（逗号分隔，如"1,2,3"） |
| files | File[] | 否 | 直接上传的文件列表（仅form-data格式） |
| virtual_folder_path | String | 否 | 虚拟文件夹路径（默认："/"） |
| maintain_structure | Boolean | 否 | 是否保持文件夹结构（自动调整：virtual_folder_path为"/"时为true，否则为false） |

**注意**: 
- 不能关联文件夹，只能关联具体的文件
- 如果传入文件夹ID，系统会返回验证错误
- `files_ids` 和 `files` 可以同时使用，系统会合并处理

#### 请求头

**方式一：JSON格式**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**方式二：form-data格式（推荐，支持文件上传）**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### 请求示例

**方式一：JSON格式（关联已存在文件）**

```json
{
    "title": "移动应用UI设计需求",
    "brief": "为移动应用设计现代化用户界面",
    "description": "需要为我们的移动应用设计一套完整的用户界面，包括主页、用户中心、商品展示等页面",

    "status": "under_review",
    "organization": 1,
    "finish_time": "2024-03-20 18:00:00",
    "budget": "20000-30000",
    "people_count": "2-3人",
    "evaluation_criteria_id": 1,
    "tag1_ids": "1,2,3",
    "tag2_ids": "4,5",
    "resource_ids": "res_002",
    "files_ids": "2,3"
}
```

**方式二：form-data格式（直接上传文件）**

```python
import requests

# 准备文件和数据
files = [
    ('files', ('design_spec.pdf', open('design_spec.pdf', 'rb'), 'application/pdf')),
    ('files', ('wireframe.png', open('wireframe.png', 'rb'), 'image/png'))
]

data = {
    'title': '移动应用UI设计需求',
    'brief': '为移动应用设计现代化用户界面',
    'description': '需要为我们的移动应用设计一套完整的用户界面，包括主页、用户中心、商品展示等页面',
    'virtual_folder_path': '/projects/mobile_ui/',
    'maintain_structure': 'true'
}

headers = {
    'Authorization': 'Bearer your_access_token'
}

response = requests.post(
    'http://localhost:8000/api/v1/project/requirement/',
    files=files,
    data=data,
    headers=headers
)
```

**方式三：混合模式（同时关联已存在文件和上传新文件）**

```python
import requests

files = [
    ('files', ('new_design.pdf', open('new_design.pdf', 'rb'), 'application/pdf'))
]

data = {
    'title': '移动应用UI设计需求',
    'brief': '为移动应用设计现代化用户界面',
    'description': '详细描述...',
    'files_ids': '2,3',  # 关联已存在的文件
    'virtual_folder_path': '/projects/mobile_ui/'
}

headers = {
    'Authorization': 'Bearer your_access_token'
}

response = requests.post(
    'http://localhost:8000/api/v1/project/requirement/',
    files=files,
    data=data,
    headers=headers
)
```

#### 响应示例
```json
{
    "status": "success",
    "code": 201,
    "message": "需求发布成功",
    "data": {
        "id": "req_002",
        "title": "移动应用UI设计需求",
        "brief": "为移动应用设计现代化用户界面",
        "description": "需要为我们的移动应用设计一套完整的用户界面，包括主页、用户中心、商品展示等页面",

        "tags": "UI设计, 移动端, 用户体验",
        "status": "under_review",
        "organization": {
            "id": 1,
            "name": "科技创新公司",
            "logo": "http://localhost:8000/media/logos/company_logo.jpg",
            "status": "verified"
        },
        
        "publish_people": "李经理",
        "finish_time": "2024-03-20 18:00:00",
        "budget": "20000-30000",
        "people_count": "2-3人",
        "applications": 0,
        "views": 0,
        "evaluation_criteria": {
            "id": 2,
            "name": "UI设计评分标准",
            "description": "针对用户界面设计项目的评分标准",
            "status": "active",
            "indicator_count": 4,
            "total_weight": 100.0,
            "created_at": "2024-01-15T10:00:00Z"
        },
        "resources": [
            {
                "id": "res_002",
                "title": "设计规范文档",
                "type": "document",

            }
        ],
        "files": [
            {
                "id": 2,
                "url": "http://localhost:8000/media/files/design_brief.pdf",
                "name": "设计简介.pdf",
                "path": "/media/files/design_brief.pdf",
                "size": 1024000,
                "created_at": "2024-01-20T14:00:00Z"
            }
        ]
    },
    "error": {}
}
```

### 3. 需求详情

**接口**: `GET /api/v1/project/requirement/{requirement_id}/`
**描述**: 获取指定需求的详细信息
**权限**: 认证用户

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
        "id": "req_001",
        "title": "AI智能推荐系统开发",
        "brief": "基于机器学习的个性化推荐系统",
        "description": "开发一个基于用户行为分析的智能推荐系统，支持多种推荐算法，包括协同过滤、内容推荐等",

        "tags": "机器学习, 推荐算法, Python, TensorFlow",
        "status": "in_progress",
        "organization": {
            "id": 1,
            "name": "科技创新公司",
            "logo": "http://localhost:8000/media/logos/company_logo.jpg",
            "status": "verified"
        },
        
        "publish_people": "张经理",
        "finish_time": "2024-06-30 18:00:00",
        "budget": "50000-100000",
        "people_count": "3-5人",
        "applications": 12,
        "views": 157,
        "evaluation_criteria": {
            "id": 1,
            "name": "AI项目评分标准",
            "description": "针对人工智能项目的综合评分标准",
            "status": "active",
            "indicator_count": 5,
            "total_weight": 100.0,
            "created_at": "2024-01-10T09:00:00Z"
        },
        "resources": [
            {
                "id": "res_001",
                "title": "推荐算法代码库",
                "type": "code",

            }
        ],
        "files": [
            {
                "id": 1,
                "url": "http://localhost:8000/media/files/requirement_doc.pdf",
                "name": "需求说明书.pdf",
                "path": "/media/files/requirement_doc.pdf",
                "size": 2048576,
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]
    },
    "error": {}
}
```

### 4. 修改需求

**接口**: `PUT /api/v1/project/requirement/{requirement_id}/update/` 或 `PATCH /api/v1/project/requirement/{requirement_id}/update/`
**描述**: 修改指定需求的基本信息，不支持文件操作。文件管理请使用虚拟文件系统API
**权限**: 需求发布者、同一组织管理员或同一组织所有者

#### 请求头

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 支持的参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| title | String | 需求标题 |
| brief | String | 需求简介 |
| description | String | 详细描述 |
| status | String | 需求状态 |
| organization | Integer | 组织ID |
| finish_time | String | 完成时间 |
| budget | String | 预算 |
| people_count | String | 人数需求 |
| evaluation_criteria_id | Integer | 评分标准ID |
| tag1_ids | String | 兴趣标签ID列表（逗号分隔） |
| tag2_ids | String | 能力标签ID列表（逗号分隔） |
| resource_ids | String | 关联资源ID列表（逗号分隔） |

**注意**: 
- 不支持文件相关操作（files_ids、files等参数已移除）
- 文件的添加、删除、修改请使用虚拟文件系统API
- 需求与文件的关联关系通过虚拟文件系统管理

#### 请求示例

```json
{
    "title": "AI智能推荐系统开发 v2.0",
    "description": "升级版智能推荐系统，新增深度学习算法支持",
    "status": "in_progress",
    "finish_time": "2024-07-31 18:00:00",
    "budget": "60000-120000",
    "people_count": "4-6人",
    "evaluation_criteria_id": 2,
    "tag1_ids": "1,2,3,6",
    "tag2_ids": "4,5,7",
    "resource_ids": "res_001,res_003"
}
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "需求修改成功",
    "data": {
        "id": "req_001",
        "title": "AI智能推荐系统开发 v2.0",
        "brief": "基于机器学习的个性化推荐系统",
        "description": "升级版智能推荐系统，新增深度学习算法支持",

        "tags": "机器学习, 推荐算法, Python, TensorFlow, 深度学习",
        "status": "in_progress",
        "organization": {
            "id": 1,
            "name": "科技创新公司",
            "logo": "http://localhost:8000/media/logos/company_logo.jpg",
            "status": "verified"
        },
        
        "publish_people": "张经理",
        "finish_time": "2024-07-31 18:00:00",
        "budget": "60000-120000",
        "people_count": "4-6人",
        "applications": 12,
        "views": 157,
        "evaluation_criteria": {
            "id": 2,
            "name": "AI项目评分标准v2",
            "description": "升级版AI项目评分标准，包含深度学习评估",
            "status": "active",
            "indicator_count": 6,
            "total_weight": 100.0,
            "created_at": "2024-01-20T10:00:00Z"
        },
        "resources": [
            {
                "id": "res_001",
                "title": "推荐算法代码库",
                "type": "code",

            },
            {
                "id": "res_003",
                "title": "深度学习模型",
                "type": "dataset",

            }
        ],
        "files": [
            {
                "id": 1,
                "url": "http://localhost:8000/media/files/requirement_doc.pdf",
                "name": "需求说明书.pdf",
                "path": "/media/files/requirement_doc.pdf",
                "size": 2048576,
                "created_at": "2024-01-15T10:00:00Z"
            },
            {
                "id": 4,
                "url": "http://localhost:8000/media/files/tech_spec.pdf",
                "name": "技术规格书.pdf",
                "path": "/media/files/tech_spec.pdf",
                "size": 1536000,
                "created_at": "2024-01-20T16:00:00Z"
            }
        ]
    },
    "error": {}
}
```

### 5. 删除需求

**接口**: `DELETE /api/v1/project/requirement/{requirement_id}/`
**描述**: 删除指定需求（保留关联资源）
**权限**: 需求发布者、同一组织管理员或同一组织所有者

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "需求删除成功",
    "data": {},
    "error": {}
}
```

### 6. 需求统计

**接口**: `GET /api/v1/project/requirement/statistics/`

**描述**: 获取当前用户所属组织的最近七周需求统计数据，包括总需求数、进行中需求数、已完成需求数以及每周发布数量图表数据
**权限**: 组织用户（系统会自动根据用户身份确定组织ID）

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 说明
- 只有组织用户才能访问此接口
- 系统会自动根据用户身份确定organization_id，无需在请求中指定
- 用户只能查看自己所属组织的统计数据

#### 响应示例
```json
{
    "status": "success",
    "code": "200",
    "message": "获取成功",
    "data": {
        "totalRequirements": 34,
        "in_progress": 12,
        "completed": 18,
        "chartData": {
            "dates": [
                "07-01",
                "07-08",
                "07-15",
                "07-22",
                "07-29",
                "08-05",
                "08-12"
            ],
            "publishCount": [
                4,
                9,
                4,
                7,
                3,
                1,
                4
            ]
        }
    },
    "error": {}
}
```

## 权限说明

### 操作权限
- **查看需求列表**: 任何认证用户
- **查看需求详情**: 任何认证用户
- **发布需求**: 只要是企业用户（组织成员）即可发布需求
- **修改需求**: 只允许需求发布者、同一组织管理员和同一组织所有者修改需求
- **删除需求**: 只允许需求发布者、同一组织管理员和同一组织所有者删除需求

### 组织角色
- **owner**: 所有者，拥有所有权限，可以修改删除任何需求
- **admin**: 管理员，拥有管理权限，可以修改删除任何需求
- **member**: 普通成员，可以发布需求，只能修改删除自己发布的需求

## 错误响应

### 常见错误码
- **400**: 请求参数错误
- **401**: 未认证
- **403**: 权限不足
- **404**: 资源不存在
- **422**: 验证失败

### 错误响应示例
```json
{
    "status": "error",
    "code": 403,
    "message": "您没有权限执行此操作",
    "data": {},
    "error": {
        "detail": "只有组织管理员或经理可以发布需求"
    }
}
```

```json
{
    "status": "error",
    "code": 422,
    "message": "验证失败",
    "data": {},
    "error": {
        "title": ["需求标题不能为空"],
        "organization": ["请选择有效的组织"]
    }
}
```

## 虚拟文件系统管理接口

### 1. 文件上传

**接口**: `POST /api/v1/project/virtual-files/upload_file/`
**描述**: 向指定需求或资源上传文件，支持单文件和多文件上传，支持保持文件结构
**权限**: 需求发布者、需求所属组织的所有者或管理员（需求文件）；资源创建者、资源所属组织的所有者或管理员（资源文件）

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### 查询参数
- `requirement_id`: 需求ID（与resource_id二选一）
- `resource_id`: 资源ID（与requirement_id二选一）
- `maintain_structure`: 是否保持文件结构（自动调整：virtual_folder_path为"/"时为true，否则为false）

#### 表单数据
- `files`: 要上传的文件列表（必需，支持多文件）
- `virtual_paths[0]`: 第一个文件的虚拟路径（可选，默认为"/"）
- `virtual_paths[1]`: 第二个文件的虚拟路径（可选）
- 以此类推...

#### Postman/Apifox 测试示例

**单文件上传到需求：**
- Method: POST
- URL: `http://localhost:8000/api/v1/project/virtual-files/upload_file/?requirement_id=req_001`
- Headers: `Authorization: Bearer your_access_token`
- Body (form-data):
  - files: [选择文件] document.pdf
  - virtual_paths[0]: /documents/需求文档.pdf

**多文件上传到资源：**
- Method: POST
- URL: `http://localhost:8000/api/v1/project/virtual-files/upload_file/?resource_id=res_001`
- Headers: `Authorization: Bearer your_access_token`
- Body (form-data):
  - files: [选择文件] image1.png
  - files: [选择文件] image2.jpg
  - virtual_paths[0]: /images/logo.png
  - virtual_paths[1]: /images/banner.jpg

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "文件上传成功",
    "data": [
        {
            "id": "file_123",
            "name": "需求文档.pdf",
            "virtual_path": "/documents/需求文档.pdf",
            "file_url": "http://localhost:8000/media/uploads/files/requirement/需求文档_unique.pdf",
            "file_size": 1024000,
            "file_type": "application/pdf",
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "error": {}
}
```

### 2. 获取文件列表

**接口**: `GET /api/v1/project/virtual-files/`
**描述**: 获取指定需求或资源的文件列表
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 查询参数
- `requirement_id`: 需求ID（与resource_id二选一）
- `resource_id`: 资源ID（与requirement_id二选一）
- `path`: 文件夹路径（可选，默认为"/"）
- `file_type`: 文件类型筛选（可选）
- `search`: 搜索关键词（可选）

#### Postman/Apifox 测试示例

**获取需求文件列表：**
- Method: GET
- URL: `http://localhost:8000/api/v1/project/virtual-files/?requirement_id=req_001&path=/documents`
- Headers: `Authorization: Bearer your_access_token`

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": [
        {
            "id": "file_123",
            "name": "需求文档.pdf",
            "virtual_path": "/documents/需求文档.pdf",
            "file_url": "http://localhost:8000/media/uploads/files/requirement/需求文档_unique.pdf",
            "file_size": 1024000,
            "file_type": "application/pdf",
            "is_folder": false,
            "created_at": "2024-01-15T10:30:00Z"
        }
    ],
    "error": {}
}
```

### 3. 获取单个文件详情

**接口**: `GET /api/v1/project/virtual-files/{file_id}/`
**描述**: 获取指定文件的详细信息，系统会自动验证用户对该文件的访问权限
**权限**: 认证用户（需要对文件所属的需求或资源有访问权限）

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 路径参数
- `file_id`: 文件ID（必需）

#### 权限说明
系统会自动检查用户是否有权限访问该文件：
- 认证用户即可访问文件详情

#### Postman/Apifox 测试示例

**获取文件详情：**
- Method: GET
- URL: `http://localhost:8000/api/v1/project/virtual-files/file_123/`
- Headers: `Authorization: Bearer your_access_token`

#### 响应示例
```json
{
    "id": "file_123",
    "name": "需求文档.pdf",
    "virtual_path": "/documents/需求文档.pdf",
    "file_url": "http://localhost:8000/media/requirements/req_001/documents/需求文档_unique.pdf",
    "file_size": 1024000,
    "file_type": "application/pdf",
    "is_folder": false,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
}
```

#### 错误响应示例
```json
{
    "error": "您没有权限访问此文件"
}
```

```json
{
    "error": "文件不属于任何需求或资源"
}
```

### 4. 创建文件夹

**接口**: `POST /api/v1/project/virtual-files/create_folder/`
**描述**: 在指定需求或资源中创建文件夹
**权限**: 需求发布者、需求所属组织的所有者或管理员（需求文件夹）；资源创建者、资源所属组织的所有者或管理员（资源文件夹）

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 查询参数
- `requirement_id`: 需求ID（与resource_id二选一）
- `resource_id`: 资源ID（与requirement_id二选一）

#### 请求体
```json
{
    "folder_name": "新文件夹",
    "parent_path": "/documents"
}
```

#### Postman/Apifox 测试示例

**在需求中创建文件夹：**
- Method: POST
- URL: `http://localhost:8000/api/v1/project/virtual-files/create_folder/?requirement_id=req_001`
- Headers: 
  - `Authorization: Bearer your_access_token`
  - `Content-Type: application/json`
- Body (raw JSON):
```json
{
    "folder_name": "设计文档",
    "parent_path": "/documents"
}
```

#### 响应示例
```json
{
    "status": "success",
    "code": 201,
    "message": "文件夹创建成功",
    "data": {
        "id": "folder_456",
        "name": "设计文档",
        "virtual_path": "/documents/设计文档",
        "is_folder": true,
        "created_at": "2024-01-15T11:00:00Z"
    },
    "error": {}
}
```

### 5. 重命名文件/文件夹

**接口**: `PUT /api/v1/project/virtual-files/{file_id}/rename/`
**描述**: 重命名指定的文件或文件夹
**权限**: 需求发布者、需求所属组织的所有者或管理员（需求文件）；资源创建者、资源所属组织的所有者或管理员（资源文件）

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 查询参数
- `requirement_id`: 需求ID（与resource_id二选一）
- `resource_id`: 资源ID（与requirement_id二选一）

#### 请求体
```json
{
    "new_name": "新文件名.pdf"
}
```

#### Postman/Apifox 测试示例

**重命名需求中的文件：**
- Method: PUT
- URL: `http://localhost:8000/api/v1/project/virtual-files/file_123/rename/?requirement_id=req_001`
- Headers:
  - `Authorization: Bearer your_access_token`
  - `Content-Type: application/json`
- Body (raw JSON):
```json
{
    "new_name": "更新后的需求文档.pdf"
}
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "重命名成功",
    "data": {
        "id": "file_123",
        "name": "更新后的需求文档.pdf",
        "virtual_path": "/documents/更新后的需求文档.pdf",
        "file_url": "http://localhost:8000/media/uploads/files/requirement/更新后的需求文档_unique.pdf",
        "file_size": 1024000,
        "file_type": "application/pdf",
        "is_folder": false,
        "created_at": "2024-01-15T10:30:00Z"
    },
    "error": {}
}
```

### 6. 移动文件/文件夹

**接口**: `PUT /api/v1/project/virtual-files/{file_id}/move/`
**描述**: 移动指定的文件或文件夹到新路径
**权限**: 需求发布者、需求所属组织的所有者或管理员（需求文件）；资源创建者、资源所属组织的所有者或管理员（资源文件）

#### 请求头
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 查询参数
- `requirement_id`: 需求ID（与resource_id二选一）
- `resource_id`: 资源ID（与requirement_id二选一）

#### 请求体
```json
{
    "new_path": "/documents/archived/"
}
```

#### Postman/Apifox 测试示例

**移动需求中的文件：**
- Method: PUT
- URL: `http://localhost:8000/api/v1/project/virtual-files/file_123/move/?requirement_id=req_001`
- Headers:
  - `Authorization: Bearer your_access_token`
  - `Content-Type: application/json`
- Body (raw JSON):
```json
{
    "new_path": "/documents/archived/"
}
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "移动成功",
    "data": {
        "id": "file_123",
        "name": "需求文档.pdf",
        "virtual_path": "/documents/archived/需求文档.pdf",
        "file_url": "http://localhost:8000/media/requirements/req_001/documents/archived/需求文档_unique.pdf",
        "file_size": 1024000,
        "file_type": "application/pdf",
        "is_folder": false,
        "created_at": "2024-01-15T10:30:00Z"
    },
    "error": {}
}
```

### 7. 删除文件/文件夹

**接口**: `DELETE /api/v1/project/virtual-files/{file_id}/`
**描述**: 删除指定的文件或文件夹（文件夹删除会递归删除所有子文件）
**权限**: 需求发布者、需求所属组织的所有者或管理员（需求文件）；资源创建者、资源所属组织的所有者或管理员（资源文件）

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 查询参数
- `requirement_id`: 需求ID（与resource_id二选一）
- `resource_id`: 资源ID（与requirement_id二选一）

#### Postman/Apifox 测试示例

**删除需求中的文件：**
- Method: DELETE
- URL: `http://localhost:8000/api/v1/project/virtual-files/file_123/?requirement_id=req_001`
- Headers: `Authorization: Bearer your_access_token`

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "删除成功",
    "data": {
        "id": "file_123",
        "name": "需求文档.pdf",
        "path": "/documents/需求文档.pdf",
        "size": 1024000,
        "is_folder": false,
        "created_at": "2024-01-15T10:30:00Z"
    },
    "error": {}
}
```

### 8. 获取文件树结构

**接口**: `GET /api/v1/project/virtual-files/tree_structure/`
**描述**: 获取指定需求或资源的完整文件树结构
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 查询参数
- `requirement_id`: 需求ID（与resource_id二选一）
- `resource_id`: 资源ID（与requirement_id二选一）

#### Postman/Apifox 测试示例

**获取需求文件树：**
- Method: GET
- URL: `http://localhost:8000/api/v1/project/virtual-files/tree_structure/?requirement_id=req_001`
- Headers: `Authorization: Bearer your_access_token`

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": {
        "name": "根目录",
        "path": "/",
        "is_folder": true,
        "children": [
            {
                "id": "folder_456",
                "name": "documents",
                "path": "/documents",
                "is_folder": true,
                "children": [
                    {
                        "id": "file_123",
                        "name": "需求文档.pdf",
                        "path": "/documents/需求文档.pdf",
                        "is_folder": false,
                        "file_size": 1024000,
                        "file_type": "application/pdf",
                        "created_at": "2024-01-15T10:30:00Z"
                    }
                ]
            }
        ]
    },
    "error": {}
}
```

### 9. 获取面包屑导航

**接口**: `GET /api/v1/project/virtual-files/breadcrumb/`
**描述**: 获取指定路径的面包屑导航信息
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 查询参数
- `requirement_id`: 需求ID（与resource_id二选一）
- `resource_id`: 资源ID（与requirement_id二选一）
- `path`: 文件路径（必需）

#### Postman/Apifox 测试示例

**获取面包屑导航：**
- Method: GET
- URL: `http://localhost:8000/api/v1/project/virtual-files/breadcrumb/?requirement_id=req_001&path=/documents/design/ui`
- Headers: `Authorization: Bearer your_access_token`

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "操作成功",
    "data": [
        {
            "name": "根目录",
            "path": "/"
        },
        {
            "name": "documents",
            "path": "/documents"
        },
        {
            "name": "design",
            "path": "/documents/design"
        },
        {
            "name": "ui",
            "path": "/documents/design/ui"
        }
    ],
    "error": {}
}
```

**注意**: 需求修改接口已不再支持文件操作，如需管理文件请使用虚拟文件系统API

## 资源管理接口

### 1. 发布资源

**接口**: `POST /api/v1/project/resource/`
**描述**: 发布新资源，支持JSON格式和form-data格式（可直接上传文件）
**权限**: 认证用户（组织管理员或所有者）

**默认值设置**:
- `status`: 默认为 `draft`（草稿），可设置为 `published`（已发布）
- `create_person`: 自动设置为当前用户
- `update_person`: 自动设置为当前用户

#### 文件处理方式

支持两种文件处理方式：
1. **关联已存在文件**: 通过 `files_ids` 参数关联已上传到虚拟文件系统的文件
2. **直接上传文件**: 通过 `files` 参数直接上传新文件（仅支持form-data格式）

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|----------|
| title | String | 是 | 资源标题 |
| description | String | 是 | 资源描述 |
| type | String | 是 | 资源类型 |
| status | String | 否 | 资源状态（draft/published，默认：draft） |
| tag1_ids | String | 否 | 兴趣标签ID列表（逗号分隔，如"1,2,3"） |
| tag2_ids | String | 否 | 能力标签ID列表（逗号分隔，如"4,5,6"） |
| files_ids | String | 否 | 文件ID列表（逗号分隔，如"1,2,3"） |
| files | File[] | 否 | 直接上传的文件列表（仅form-data格式） |
| virtual_folder_path | String | 否 | 虚拟文件夹路径（默认："/"） |
| maintain_structure | Boolean | 否 | 是否保持文件夹结构（自动调整） |

**注意**: 
- 只有组织用户可以发布资源
- 不能关联文件夹，只能关联具体的文件
- `files_ids` 和 `files` 可以同时使用，系统会合并处理

#### 请求头

**方式一：JSON格式**
```
Authorization: Bearer <access_token>
Content-Type: application/json
```

**方式二：form-data格式（推荐，支持文件上传）**
```
Authorization: Bearer <access_token>
Content-Type: multipart/form-data
```

#### 请求示例

**方式一：JSON格式（关联已存在文件）**

```json
{
    "title": "Python机器学习教程",
    "description": "完整的Python机器学习入门教程，包含理论和实践",
    "type": "tutorial",
    "status": "published",
    "tag1_ids": "1,2,3",
    "tag2_ids": "4,5",
    "files_ids": "2,3"
}
```

**方式二：form-data格式（直接上传文件）**

```python
import requests

# 准备文件和数据
files = [
    ('files', ('tutorial.pdf', open('tutorial.pdf', 'rb'), 'application/pdf')),
    ('files', ('code_examples.zip', open('code_examples.zip', 'rb'), 'application/zip'))
]

data = {
    'title': 'Python机器学习教程',
    'description': '完整的Python机器学习入门教程，包含理论和实践',
    'type': 'tutorial',
    'status': 'published',
    'virtual_folder_path': '/tutorials/ml/',
    'maintain_structure': 'true'
}

headers = {
    'Authorization': 'Bearer your_access_token'
}

response = requests.post(
    'http://localhost:8000/api/v1/project/resource/',
    files=files,
    data=data,
    headers=headers
)
```

#### 响应示例
```json
{
    "status": "success",
    "code": 201,
    "message": "资源发布成功",
    "data": {
        "id": "res_003",
        "title": "Python机器学习教程",
        "description": "完整的Python机器学习入门教程，包含理论和实践",
        "type": "tutorial",
        "status": "published",
        "create_person": "张老师",
        "update_person": "张老师",
        "created_at": "2024-01-20T15:30:00Z",
        "updated_at": "2024-01-20T15:30:00Z",
        "tag1": [
            {
                "id": 1,
                "name": "机器学习"
            }
        ],
        "tag2": [
            {
                "id": 4,
                "name": "Python"
            }
        ],
        "files": [
            {
                "id": 2,
                "url": "http://localhost:8000/media/files/tutorial.pdf",
                "name": "教程.pdf",
                "path": "/media/files/tutorial.pdf",
                "size": 2048576,
                "created_at": "2024-01-20T15:30:00Z"
            }
        ]
    },
    "error": {}
}
```

### 2. 修改资源

**接口**: `PUT /api/v1/project/resource/{resource_id}/update/` 或 `PATCH /api/v1/project/resource/{resource_id}/update/`
**描述**: 修改指定资源的基本信息，不支持文件操作。文件管理请使用虚拟文件系统API
**权限**: 资源创建者、同一组织管理员或同一组织所有者

#### 请求头

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

#### 支持的参数

| 参数名 | 类型 | 说明 |
|--------|------|------|
| title | String | 资源标题 |
| description | String | 资源描述 |
| type | String | 资源类型 |
| status | String | 资源状态 |
| tag1_ids | String | 兴趣标签ID列表（逗号分隔） |
| tag2_ids | String | 能力标签ID列表（逗号分隔） |

**注意**: 
- 不支持文件相关操作（files_ids、files等参数已移除）
- 文件的添加、删除、修改请使用虚拟文件系统API
- 资源与文件的关联关系通过虚拟文件系统管理
- `update_person` 会自动更新为当前用户

#### 请求示例

```json
{
    "title": "Python机器学习教程 v2.0",
    "description": "升级版Python机器学习教程，新增深度学习内容",
    "type": "tutorial",
    "status": "published",
    "tag1_ids": "1,2,3,6",
    "tag2_ids": "4,5,7"
}
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "资源修改成功",
    "data": {
        "id": "res_003",
        "title": "Python机器学习教程 v2.0",
        "description": "升级版Python机器学习教程，新增深度学习内容",
        "type": "tutorial",
        "status": "published",
        "create_person": "张老师",
        "update_person": "张老师",
        "created_at": "2024-01-20T15:30:00Z",
        "updated_at": "2024-01-20T16:45:00Z",
        "tag1": [
            {
                "id": 1,
                "name": "机器学习"
            },
            {
                "id": 6,
                "name": "深度学习"
            }
        ],
        "tag2": [
            {
                "id": 4,
                "name": "Python"
            },
            {
                "id": 7,
                "name": "TensorFlow"
            }
        ],
        "files": [
            {
                "id": 2,
                "url": "http://localhost:8000/media/files/tutorial.pdf",
                "name": "教程.pdf",
                "path": "/media/files/tutorial.pdf",
                "size": 2048576,
                "created_at": "2024-01-20T15:30:00Z"
            }
        ]
    },
    "error": {}
}
```

### 3. 删除资源

**接口**: `DELETE /api/v1/project/resource/{resource_id}/delete/`
**描述**: 删除指定资源及其关联的所有文件，但保留关联的需求
**权限**: 资源创建者、同一组织管理员或同一组织所有者

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求示例
```
DELETE /api/v1/project/resource/res_003/delete/
Authorization: Bearer your_access_token
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "资源删除成功",
    "data": {
        "deleted_resource_id": "res_003",
        "deleted_files_count": 3,
        "preserved_requirements_count": 2
    },
    "error": {}
}
```

#### 删除操作说明

1. **资源删除**: 完全删除资源记录
2. **文件处理**: 删除资源关联的所有文件（包括虚拟文件系统中的文件）
3. **需求关联**: 保留关联的需求，只删除关联关系
4. **并发安全**: 使用悲观锁确保删除操作的原子性
5. **权限检查**: 严格验证用户权限，确保只有授权用户可以删除

**注意**: 删除操作不可逆，请谨慎操作。建议在删除前确认资源不再需要。

### 4. 获取资源列表

**接口**: `GET /api/v1/project/resource/list/`
**描述**: 获取资源列表，支持分页、筛选、排序和搜索
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 查询参数

| 参数名 | 类型 | 必填 | 默认值 | 说明 |
|--------|------|------|--------|------|
| page | Integer | 否 | 1 | 页码 |
| page_size | Integer | 否 | 10 | 每页数量（最大100） |
| keyword | String | 否 | - | 搜索关键词（可从资源标题、标签中搜索） |
| status | String | 否 | - | 资源状态筛选（支持多状态查询，用逗号分隔多个状态值） |
| type | String | 否 | - | 资源类型筛选（支持多类型查询，用逗号分隔多个类型值，如：code,dataset,document） |
| time | String | 否 | - | 发布时间筛选（支持单日或范围筛选，格式：YYYY-MM-DD 或 YYYY-MM-DD-YYYY-MM-DD） |
| sort_type | String | 否 | time | 排序类型（name/time/download/view） |
| sort_order | String | 否 | down | 排序方式（up升序/down降序） |
| organization_id | Integer | 否 | - | 组织ID筛选 |

#### 请求示例

**单状态查询：**
```
GET /api/v1/project/resource/list/?page=1&page_size=20&keyword=机器学习&status=published&sort_type=download&sort_order=down
Authorization: Bearer your_access_token
```

**多状态查询：**
```
GET /api/v1/project/resource/list/?page=1&page_size=20&status=published,draft&sort_type=time&sort_order=down
Authorization: Bearer your_access_token
```

**类型筛选查询：**
```
GET /api/v1/project/resource/list/?page=1&page_size=20&type=code,dataset&sort_type=time&sort_order=down
Authorization: Bearer your_access_token
```

**时间范围筛选查询：**
```
GET /api/v1/project/resource/list/?page=1&page_size=20&time=2025-04-01-2025-08-18&sort_type=time&sort_order=down
Authorization: Bearer your_access_token
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "获取资源列表成功",
    "data": {
        "resources": [
            {
                "id": "res_001",
                "title": "Python机器学习教程",
                "description": "详细的Python机器学习入门教程",
                "type": "tutorial",
                "status": "published",
                "downloads": "150",
                "views": "1200",
                "create_person_name": "张老师",
                "created_at": "2024-01-20T10:00:00Z",
                "updated_at": "2024-01-20T15:30:00Z",
                "tag1": [
                    {
                        "id": 1,
                        "name": "机器学习"
                    }
                ],
                "tag2": [
                    {
                        "id": 4,
                        "name": "Python"
                    }
                ],
                "files": [
                    {
                        "id": 1,
                        "name": "tutorial.pdf",
                        "size": 1024000,
                        "url": "http://localhost:8000/media/files/tutorial.pdf"
                    }
                ]
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "page_size": 20,
            "total_count": 95,
            "has_next": true,
            "has_previous": false
        }
    },
    "error": {}
}
```

### 5. 获取资源详情

**接口**: `GET /api/v1/project/resource/{resource_id}/`
**描述**: 根据resource_id获取对应资源的详细信息
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求示例
```
GET /api/v1/project/resource/res_001/
Authorization: Bearer your_access_token
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "获取资源详情成功",
    "data": {
        "id": "res_001",
        "title": "Python机器学习教程",
        "description": "详细的Python机器学习入门教程，包含理论知识和实践案例",
        "type": "tutorial",
        "status": "published",
        "downloads": "150",
        "views": "1201",
        "create_person": "org_user_001",
        "create_person_name": "张老师",
        "update_person": "org_user_001",
        "update_person_name": "张老师",
        "created_at": "2024-01-20T10:00:00Z",
        "updated_at": "2024-01-20T15:30:00Z",
        "tag1": [
            {
                "id": 1,
                "name": "机器学习"
            },
            {
                "id": 2,
                "name": "人工智能"
            }
        ],
        "tag2": [
            {
                "id": 4,
                "name": "Python"
            },
            {
                "id": 5,
                "name": "数据分析"
            }
        ],
        "files": [
            {
                "id": 1,
                "name": "tutorial.pdf",
                "path": "/media/files/tutorial.pdf",
                "size": 1024000,
                "url": "http://localhost:8000/media/files/tutorial.pdf",
                "created_at": "2024-01-20T10:00:00Z"
            },
            {
                "id": 2,
                "name": "examples.zip",
                "path": "/media/files/examples.zip",
                "size": 2048000,
                "url": "http://localhost:8000/media/files/examples.zip",
                "created_at": "2024-01-20T10:05:00Z"
            }
        ]
    },
    "error": {}
}
```

**注意**: 访问资源详情时会自动增加浏览次数（views字段）。

### 6. 获取资源下载信息

**接口**: `GET /api/v1/project/resource/{resource_id}/download/`
**描述**: 根据resource_id获取对应资源关联的文件的完整下载URL
**权限**: 认证用户

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 请求示例
```
GET /api/v1/project/resource/res_001/download/
Authorization: Bearer your_access_token
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "获取资源下载信息成功",
    "data": {
        "resource_id": "res_001",
        "resource_title": "Python机器学习教程",
        "files": [
            {
                "id": 1,
                "name": "tutorial.pdf",
                "size": 1024000,
                "download_url": "http://localhost:8000/media/files/tutorial.pdf",
                "created_at": "2024-01-20T10:00:00Z"
            },
            {
                "id": 2,
                "name": "examples.zip",
                "size": 2048000,
                "download_url": "http://localhost:8000/media/files/examples.zip",
                "created_at": "2024-01-20T10:05:00Z"
            }
        ]
    },
    "error": {}
}
```

**注意**: 访问资源下载信息时会自动增加下载次数（downloads字段）。

### 7. 获取资源统计

**接口**: `GET /api/v1/project/resource/statistics/`
**描述**: 获取当前用户所属组织的资源统计数据，支持周度、月度、季度统计，包含状态分布、累计数据统计及增长率、热门标签和热门资源
**权限**: 组织用户（系统会自动根据用户身份确定组织ID）

#### 请求头
```
Authorization: Bearer <access_token>
```

#### 查询参数
- `period`: 统计周期 (week/month/quarter，默认: week)
- `date`: 统计截止日期 (格式: YYYY-MM-DD，默认: 当前日期)

#### 说明
- 只有组织用户才能访问此接口
- 系统会自动根据用户身份确定organization_id，无需在请求中指定
- 用户只能查看自己所属组织的资源统计数据

#### 请求示例
```
# 获取本周资源统计
GET /api/v1/project/resource/statistics/?period=week

# 获取指定日期的月度统计
GET /api/v1/project/resource/statistics/?period=month&date=2024-08-19

# 获取季度统计
GET /api/v1/project/resource/statistics/?period=quarter
```

#### 响应示例
```json
{
    "status": "success",
    "code": 200,
    "message": "获取资源统计成功",
    "data": {
        "status_distribution": {
            "published": 45,
            "draft": 12,
            "unpublished": 8
        },
        "data_statistics": {
            "total": 65,
            "total_up": "15",
            "published_count": 45,
            "published_count_up": "20",
            "downloads": 1250,
            "downloads_up": "35",
            "views": 3420,
            "views_up": "28"
        },
        "hot_tag1s": [
            {
                "tag": "人工智能",
                "count": "15"
            },
            {
                "tag": "机器学习",
                "count": "12"
            },
            {
                "tag": "数据分析",
                "count": "10"
            }
        ],
        "hot_downloads": [
            {
                "id": "res_001",
                "title": "Python机器学习教程",
                "downloads": "450",
                "views": "1200",
                "auther": "张教授"
            },
            {
                "id": "res_002",
                "title": "深度学习实战指南",
                "downloads": "380",
                "views": "950",
                "auther": "李博士"
            }
        ],
        "hot_views": [
            {
                "id": "res_003",
                "title": "数据可视化案例集",
                "downloads": "200",
                "views": "1500",
                "auther": "王老师"
            },
            {
                "id": "res_001",
                "title": "Python机器学习教程",
                "downloads": "450",
                "views": "1200",
                "auther": "张教授"
            }
        ]
    },
    "error": {}
}
```

#### 响应字段说明

**status_distribution**: 状态分布统计
- `published`: 已发布资源数量
- `draft`: 草稿资源数量
- `unpublished`: 未发布资源数量

**data_statistics**: 累计数据统计及增长率
- `total`: 累计总资源数
- `total_up`: 总数增长率（百分比字符串）
- `published_count`: 累计已发布资源数
- `published_count_up`: 已发布数增长率（百分比字符串）
- `downloads`: 累计下载量
- `downloads_up`: 下载量增长率（百分比字符串）
- `views`: 累计浏览量
- `views_up`: 浏览量增长率（百分比字符串）

**hot_tag1s**: 热门标签（前10个）
- `tag`: 标签名称
- `count`: 关联资源数量

**hot_downloads**: 下载量最高的前5个资源
- `id`: 资源ID
- `title`: 资源标题
- `downloads`: 下载量
- `views`: 浏览量
- `auther`: 作者

**hot_views**: 浏览量最高的前5个资源
- 字段含义同hot_downloads

#### 增长率计算说明

增长率基于累计数据的同比计算：
- **累计数据对比**: 比较当前时间点的累计数据与上一周期同一时间点的累计数据
- **计算公式**: `增长率 = (当前累计数据 - 上期累计数据) / 上期累计数据 × 100%`
- **示例**: 8月19日的周度统计会比较8月19日累计数据与8月12日累计数据
- **特殊情况**: 当上期数据为0时，如果当前有数据则显示"100"，否则显示"0"

**注意**: 
- 所有统计数据基于累计数据计算，不受时间段限制
- 增长率以字符串形式返回，便于前端显示
- 热门资源分别按下载量和浏览量排序，可能存在重复

## 注意事项

1. **权限验证**: 所有接口都需要JWT认证，发布、修改、删除需求需要相应的组织权限
2. **数据验证**: 请求参数会进行严格验证，确保数据完整性和安全性
3. **文件管理架构变更**: 
   - 需求创建接口仅支持关联已存在的文件ID（files_ids参数）
   - 需求修改接口已完全移除文件相关操作
   - 所有文件上传、删除、管理操作请使用虚拟文件系统API (`/api/v1/project/virtual-files/`)
   - 不支持直接关联文件夹到需求，只能关联具体文件
4. **关联关系**: 删除需求时会保留关联的资源和文件，只删除关联关系
5. **浏览统计**: 查看需求详情时会自动增加浏览数；查看资源详情时会自动增加浏览数
6. **下载统计**: 获取资源下载信息时会自动增加下载次数
7. **分页查询**: 列表接口支持分页，建议合理设置页面大小以提高性能
8. **搜索功能**: 支持按标题、描述、标签进行关键词搜索
9. **状态管理**: 需求状态变更需要遵循业务流程规则
10. **文件处理流程**: 推荐的文件处理流程为：先通过虚拟文件系统上传文件 → 获取文件ID → 在需求创建时关联文件ID
11. **性能优化**: 资源列表接口针对大量数据进行了优化，支持多种排序和筛选条件
