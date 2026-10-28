# 项目评分管理 API 文档

## 概述

本文档描述了项目评分管理系统的 REST API 接口，包括评分标准的创建、查询、更新、状态管理、复制和删除等功能，以及项目评分的创建、查询、更新和排名等功能。

### 基础信息

- **基础URL**: `/api/v1/projectscore/`
- **认证方式**: Token 认证
- **内容类型**: `application/json`
- **字符编码**: `UTF-8`

### 统一响应格式

所有 API 响应都遵循统一的格式：

```json
{
  "status": "success|error",
  "code": 200,
  "message": "操作描述信息",
  "data": {},
  "error": {}
}
```

### 分页格式

分页接口的响应数据格式：

```json
{
  "status": "success",
  "code": 200,
  "message": "获取数据成功",
  "data": {
    "results": [],
    "pagination": {
      "current_page": 1,
      "total_pages": 10,
      "total_count": 200,
      "page_size": 20,
      "previous_url": null,
      "next_url": "http://example.com/api/endpoint?page=2"
    }
  },
  "error": {}
}
```

---

## 1. 创建评分标准

### 接口信息

- **URL**: `POST /api/v1/projectscore/criteria/create/`
- **权限**: 认证用户
- **功能**: 创建全新的评分标准，新标准默认状态为 `active`

### 请求参数

```json
{
  "name": "软件项目评分标准",
  "description": "用于评估软件开发项目的综合评分标准",
  "requirement": 1,
  "is_template": false,
  "indicators": [
    {
      "name": "技术创新性",
      "description": "评估项目在技术方案、架构设计等方面的创新程度",
      "weight": 30.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 1
    },
    {
      "name": "实用性",
      "description": "评估项目的实际应用价值和市场前景",
      "weight": 25.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 2
    },
    {
      "name": "技术实现质量",
      "description": "评估代码质量、系统稳定性、性能等技术实现水平",
      "weight": 25.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 3
    },
    {
      "name": "团队协作",
      "description": "评估团队成员间的协作效率和项目管理能力",
      "weight": 20.0,
      "max_score": 100.0,
      "is_required": false,
      "order": 4
    }
  ]
}
```

#### 参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 评分标准名称，最大长度200字符 |
| description | string | 否 | 评分标准描述 |
| requirement | integer | 否 | 关联需求ID |
| is_template | boolean | 否 | 是否设为模板，默认false |
| indicators | array | 是 | 评分指标列表，至少包含1个指标 |
| indicators[].name | string | 是 | 指标名称，最大长度200字符 |
| indicators[].description | string | 否 | 指标描述 |
| indicators[].weight | decimal | 是 | 指标权重，0-100之间，所有指标权重之和必须等于100 |
| indicators[].max_score | decimal | 是 | 指标满分，必须大于0 |
| indicators[].is_required | boolean | 否 | 是否必填，默认false |
| indicators[].order | integer | 否 | 排序顺序，默认0 |

### 响应示例

**成功响应 (201)**:

```json
{
  "status": "success",
  "code": 201,
  "message": "评分标准创建成功",
  "data": {
    "id": 1,
    "name": "软件项目评分标准",
    "description": "用于评估软件开发项目的综合评分标准",
    "status": "active",
    "is_template": false,
    "creator": {
      "id": 1,
      "name": "组织用户001",
      "username": "user123",
      "avatar": "http://localhost:8000/media/avatars/1/avatar.jpg"
    },
    "organization": {
      "id": 1,
      "name": "阿里巴巴测试分公司",
      "code": "ALI_TEST_001"
    },
    "requirement": {
      "id": 1,
      "title": "今日移动端APP开发项目",
      "status": "active"
    },
    "template_source_name": null,
    "indicators": [
      {
        "id": 1,
        "name": "技术创新性",
        "description": "评估项目在技术方案、架构设计等方面的创新程度",
        "weight": 30.0,
        "max_score": 100,
        "order": 1,
        "is_required": true
      },
      {
        "id": 2,
        "name": "实用性",
        "description": "评估项目的实际应用价值和市场前景",
        "weight": 25.0,
        "max_score": 100,
        "order": 2,
        "is_required": true
      },
      {
        "id": 3,
        "name": "技术实现质量",
        "description": "评估代码质量、系统稳定性、性能等技术实现水平",
        "weight": 25.0,
        "max_score": 100,
        "order": 3,
        "is_required": true
      },
      {
        "id": 4,
        "name": "团队协作",
        "description": "评估团队成员间的协作效率和项目管理能力",
        "weight": 20.0,
        "max_score": 100,
        "order": 4,
        "is_required": false
      }
    ],
    "total_weight": 100.0,
    "is_weight_complete": true,
    "clone_count": 0,
    "can_modify": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "error": {}
}
```

**验证错误响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "数据验证失败",
  "data": {},
  "error": {
    "name": ["该字段为必填项。"],
    "indicators": ["至少需要一个评分指标。"]
  }
}
```

**权重验证错误响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "数据验证失败",
  "data": {},
  "error": {
    "indicators": ["所有指标权重之和必须等于100，当前总权重：95.0"]
  }
}
```

**指标权重范围错误响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "数据验证失败",
  "data": {},
  "error": {
    "indicators": ["指标权重必须在0-100之间，当前值：150.0"]
  }
}
```

**指标满分验证错误响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "数据验证失败",
  "data": {},
  "error": {
    "indicators": ["指标满分必须大于0"]
  }
}
```

---

## 2. 获取评分标准列表

### 接口信息

- **URL**: `GET /api/v1/projectscore/criteria/list/`
- **权限**: 组织用户
- **功能**: 获取评分标准列表，支持分页、搜索、筛选和排序
- **限制**: 组织用户只能访问本组织下的所有评分标准列表
- **重要字段**: 返回数据中包含 `is_used_by_requirements` 字段，用于快速判断评分标准是否被其他需求使用

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认20，最大100 |
| search | string | 否 | 搜索关键词，匹配名称和描述 |
| status | string | 否 | 状态筛选：draft/active/archived |
| requirement_id | integer | 否 | 关联需求ID筛选 |
| creator_id | integer | 否 | 创建者ID筛选 |
| is_template | boolean | 否 | 模板筛选：true=仅显示模板，false=仅显示非模板，不传=显示全部 |
| is_used_by_requirements | boolean | 否 | 使用状态筛选：true=仅显示已被其他需求使用的，false=仅显示未被使用的，不传=显示全部 |
| ordering | string | 否 | 排序字段：created_at/-created_at/updated_at/-updated_at/name/-name/status/-status |

**注意**：当 `is_template=true` 时，此接口等同于获取可用模板列表功能，会自动使用模板专用的查询逻辑。

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取评分标准列表成功",
  "data": {
    "results": [
      {
        "id": 1,
        "name": "评分标准名称",
        "description": "评分标准描述",
        "status": "draft",
        "status_display": "草稿",
        "requirement": {
          "id": 1,
          "title": "需求标题"
        },
        "creator": {
          "id": 1,
          "username": "user123",
          "organization_name": "组织名称"
        },
        "is_template": false,
        "clone_count": 0,
        "indicators_count": 5,
        "total_weight": 100.0,
        "is_used_by_requirements": false,
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_count": 100,
      "page_size": 20,
      "previous_url": null,
      "next_url": "http://example.com/api/v1/projectscore/criteria/?page=2"
    }
  },
  "error": {}
}
```

**获取模板列表示例** (`GET /api/v1/projectscore/criteria/?is_template=true`):

```json
{
  "status": "success",
  "code": 200,
  "message": "获取评分标准列表成功",
  "data": {
    "results": [
      {
        "id": 5,
        "name": "通用项目评分模板",
        "description": "适用于大多数项目的通用评分标准模板",
        "status": "active",
        "status_display": "启用",
        "requirement": null,
        "creator": {
          "id": 1,
          "username": "admin",
          "organization_name": "技术创新组织"
        },
        "is_template": true,
        "clone_count": 15,
        "indicators_count": 4,
        "total_weight": 100.0,
        "is_used_by_requirements": true,
        "created_at": "2024-01-10T09:00:00Z",
        "updated_at": "2024-01-12T14:30:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 2,
      "total_count": 25,
      "page_size": 20,
      "previous_url": null,
      "next_url": "http://example.com/api/v1/projectscore/criteria/?is_template=true&page=2"
    }
  },
  "error": {}
}
```

**获取未被使用的评分标准示例** (`GET /api/v1/projectscore/criteria/?is_used_by_requirements=false`):

```json
{
  "status": "success",
  "code": 200,
  "message": "获取评分标准列表成功",
  "data": {
    "results": [
      {
        "id": 3,
        "name": "未使用的评分标准",
        "description": "尚未被任何需求使用的评分标准",
        "status": "active",
        "status_display": "启用",
        "requirement": {
          "id": 3,
          "title": "测试需求"
        },
        "creator": {
          "id": 2,
          "username": "user456",
          "organization_name": "技术创新组织"
        },
        "is_template": false,
        "clone_count": 0,
        "indicators_count": 3,
        "total_weight": 100.0,
        "is_used_by_requirements": false,
        "created_at": "2024-01-16T08:00:00Z",
        "updated_at": "2024-01-16T08:00:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 1,
      "total_count": 8,
      "page_size": 20,
      "previous_url": null,
      "next_url": null
    }
  },
  "error": {}
}
```

---

## 3. 获取评分标准详情

### 接口信息

- **URL**: `GET /api/v1/projectscore/criteria/{criteria_id}/detail/`
- **权限**: 认证用户
- **功能**: 获取单个评分标准的完整信息，包含所有关联指标

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取评分标准详情成功",
  "data": {
    "id": 1,
    "name": "评分标准名称",
    "description": "评分标准描述",
    "status": "active",
    "status_display": "启用",
    "requirement": {
      "id": 1,
      "title": "需求标题",
      "description": "需求描述"
    },
    "creator": {
      "id": 1,
      "username": "user123",
      "organization_name": "组织名称"
    },
    "organization": {
      "id": 1,
      "name": "组织名称"
    },
    "is_template": false,
    "template_source": null,
    "clone_count": 3,
    "indicators": [
      {
        "id": 1,
        "name": "技术创新性",
        "description": "评估项目的技术创新程度",
        "weight": 30.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 1
      },
      {
        "id": 2,
        "name": "实用性",
        "description": "评估项目的实际应用价值",
        "weight": 25.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 2
      }
    ],
    "total_weight": 100.0,
    "indicators_count": 5,
    "is_used_by_requirements": false,
    "can_edit": true,
    "can_delete": true,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "error": {}
}
```

**权限不足响应 (403)**:

```json
{
  "status": "error",
  "code": 403,
  "message": "您只能访问本组织的评分标准",
  "data": {},
  "error": {}
}
```

**资源不存在响应 (404)**:

```json
{
  "status": "error",
  "code": 404,
  "message": "资源不存在",
  "data": {},
  "error": {}
}
```

---

## 4. 更新评分标准基础信息

### 接口信息

- **URL**: `PUT /api/v1/projectscore/criteria/{criteria_id}/update/` 或 `PATCH /api/v1/projectscore/criteria/{criteria_id}/update/`
- **权限**: 组织创建者、组织管理员、该评分标准创建者
- **功能**: 更新评分标准的基础信息（名称、描述、关联需求）、批量更新评分指标信息和批量创建新的评分指标
- **限制**: 
  - 仅"启用"状态的可更新
  - 若标准已关联"已提交/已公示"的项目评分，不可更新
- **新增功能**: 
  - 支持通过 `indicators` 参数批量更新多个评分指标的信息（可用于单个或多个指标更新）
  - 支持通过 `new_indicators` 参数批量创建新的评分指标

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |

### 请求参数

#### 更新评分标准基础信息

```json
{
  "name": "更新后的评分标准名称",
  "description": "更新后的描述",
  "requirement": 2
}
```

#### 更新单个评分指标信息

```json
{
  "indicators": [
    {
      "id": 1,
      "name": "更新后的指标名称",
      "description": "更新后的指标描述",
      "weight": 35.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 1
    }
  ]
}
```

#### 批量更新多个评分指标信息

```json
{
  "indicators": [
    {
      "id": 1,
      "name": "技术创新性（批量更新）",
      "description": "评估项目在技术方案、架构设计等方面的创新程度",
      "weight": 35.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 1
    },
    {
      "id": 2,
      "name": "实用性（批量更新）",
      "description": "评估项目的实际应用价值和市场前景",
      "weight": 30.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 2
    }
  ]
}
```

#### 批量创建新的评分指标

```json
{
  "new_indicators": [
    {
      "name": "用户体验",
      "description": "评估项目的用户界面设计和交互体验",
      "weight": 15.0,
      "max_score": 100.0,
      "is_required": false,
      "order": 5
    },
    {
      "name": "可扩展性",
      "description": "评估项目架构的可扩展性和维护性",
      "weight": 20.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 6
    }
  ]
}
```

#### 同时更新现有指标和创建新指标

```json
{
  "name": "更新后的评分标准名称",
  "description": "更新后的描述",
  "indicators": [
    {
      "id": 1,
      "name": "技术创新性（更新）",
      "weight": 25.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 1
    }
  ],
  "new_indicators": [
    {
      "name": "商业价值",
      "description": "评估项目的商业化潜力和市场价值",
      "weight": 30.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 7
    }
  ]
}
```

#### 参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | PUT必填/PATCH可选 | 评分标准名称 |
| description | string | 否 | 评分标准描述 |
| requirement | integer | 否 | 关联需求ID，可为null |
| indicators | array | 否 | 要批量更新的指标列表（支持单个或多个指标更新） |
| indicators[].id | integer | 是 | 指标ID |
| indicators[].name | string | 否 | 指标名称，最大长度200字符 |
| indicators[].description | string | 否 | 指标描述 |
| indicators[].weight | decimal | 否 | 指标权重，0-100之间 |
| indicators[].max_score | decimal | 否 | 指标满分，必须大于0 |
| indicators[].is_required | boolean | 否 | 是否必填 |
| indicators[].order | integer | 否 | 排序顺序 |
| new_indicators | array | 否 | 要批量创建的新指标列表 |
| new_indicators[].name | string | 是 | 新指标名称，最大长度200字符 |
| new_indicators[].description | string | 否 | 新指标描述 |
| new_indicators[].weight | decimal | 是 | 新指标权重，0-100之间 |
| new_indicators[].max_score | decimal | 是 | 新指标满分，必须大于0 |
| new_indicators[].is_required | boolean | 否 | 是否必填，默认false |
| new_indicators[].order | integer | 否 | 排序顺序，默认0 |

**注意**: 
- `indicators` 参数支持单个或多个指标的更新，传入单个指标时数组只包含一个元素即可
- `new_indicators` 参数支持批量创建新的评分指标，创建的指标会自动关联到当前评分标准
- 可以同时使用 `indicators` 和 `new_indicators` 参数，实现更新现有指标和创建新指标的组合操作
- 所有指标（包括现有的、更新的和新创建的）的权重总和必须等于100

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "评分标准更新成功",
  "data": {
    "id": 1,
    "name": "更新后的评分标准名称",
    "description": "更新后的描述",
    "status": "active",
    "status_display": "启用",
    "requirement": {
      "id": 2,
      "title": "新需求标题"
    },
    "creator": {
      "id": 1,
      "username": "user123",
      "organization_name": "组织名称"
    },
    "organization": {
      "id": 1,
      "name": "组织名称"
    },
    "is_template": false,
    "template_source": null,
    "clone_count": 0,
    "indicators": [],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:45:00Z"
  },
  "error": {}
}
```

**更新指标成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "评分标准及指标更新成功",
  "data": {
    "id": 1,
    "name": "评分标准名称",
    "description": "评分标准描述",
    "status": "active",
    "status_display": "启用",
    "requirement": {
      "id": 1,
      "title": "需求标题"
    },
    "creator": {
      "id": 1,
      "username": "user123",
      "organization_name": "组织名称"
    },
    "organization": {
      "id": 1,
      "name": "组织名称"
    },
    "is_template": false,
    "template_source": null,
    "clone_count": 0,
    "indicators": [
      {
        "id": 1,
        "name": "技术创新性（批量更新）",
        "description": "评估项目在技术方案、架构设计等方面的创新程度",
        "weight": 35.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 1
      },
      {
        "id": 2,
        "name": "实用性（批量更新）",
        "description": "评估项目的实际应用价值和市场前景",
        "weight": 30.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 2
      }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:45:00Z"
  },
  "error": {}
}
```

**批量创建新指标成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "评分标准更新成功，新增2个评分指标",
  "data": {
    "id": 1,
    "name": "评分标准名称",
    "description": "评分标准描述",
    "status": "active",
    "status_display": "启用",
    "requirement": {
      "id": 1,
      "title": "需求标题"
    },
    "creator": {
      "id": 1,
      "username": "user123",
      "organization_name": "组织名称"
    },
    "organization": {
      "id": 1,
      "name": "组织名称"
    },
    "is_template": false,
    "template_source": null,
    "clone_count": 0,
    "indicators": [
      {
        "id": 1,
        "name": "技术创新性",
        "description": "评估项目的技术创新程度",
        "weight": 30.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 1
      },
      {
        "id": 2,
        "name": "实用性",
        "description": "评估项目的实际应用价值",
        "weight": 35.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 2
      },
      {
        "id": 5,
        "name": "用户体验",
        "description": "评估项目的用户界面设计和交互体验",
        "weight": 15.0,
        "max_score": 100.0,
        "is_required": false,
        "order": 5
      },
      {
        "id": 6,
        "name": "可扩展性",
        "description": "评估项目架构的可扩展性和维护性",
        "weight": 20.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 6
      }
    ],
    "total_weight": 100.0,
    "indicators_count": 4,
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:45:00Z"
  },
  "error": {}
}
```

**权限不足响应 (403)**:

```json
{
  "status": "error",
  "code": 403,
  "message": "权限不足，只有组织管理员或评分标准创建者可以修改",
  "data": {},
  "error": {}
}
```

**业务规则验证失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "业务规则验证失败",
  "data": {},
  "error": {
    "non_field_errors": ["已归档的评分标准不可修改"]
  }
}
```

**批量更新指标权重验证失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "指标权重验证失败",
  "data": {},
  "error": {
    "indicators": ["所有指标权重总和必须等于100，当前总和为105.0"]
  }
}
```

**批量更新指标不存在响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "指标验证失败",
  "data": {},
  "error": {
    "indicators": ["指标ID 999 不存在或不属于当前评分标准"]
  }
}
```

**批量创建新指标验证失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "新指标验证失败",
  "data": {},
  "error": {
    "new_indicators": ["新指标名称不能为空"]
  }
}
```

**新指标权重验证失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "权重验证失败",
  "data": {},
  "error": {
    "new_indicators": ["新指标权重必须在0-100之间，当前值：150.0"]
  }
}
```

**总权重验证失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "权重验证失败",
  "data": {},
  "error": {
    "non_field_errors": ["所有指标（包括现有的、更新的和新创建的）权重总和必须等于100，当前总和为120.0"]
  }
}
```

**新指标名称重复验证失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "指标名称验证失败",
  "data": {},
  "error": {
    "new_indicators": ["指标名称'技术创新性'已存在，请使用不同的名称"]
  }
}
```

---

## 5. 切换评分标准状态

### 接口信息

- **URL**: `PATCH /api/v1/projectscore/criteria/{criteria_id}/status/`
- **权限**: 组织创建者、组织管理员
- **功能**: 单独切换评分标准的状态
- **支持的状态流转**: 
  - `draft` → `active`
  - `active` → `archived`
- **不支持反向流转**: 如 `archived` → `active`

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |

### 请求参数

```json
{
  "status": "active"
}
```

#### 参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| status | string | 是 | 目标状态：draft/active/archived |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "评分标准状态已更新为启用",
  "data": {
    "id": 1,
    "name": "评分标准名称",
    "description": "评分标准描述",
    "status": "active",
    "status_display": "启用",
    "requirement": {
      "id": 1,
      "title": "需求标题"
    },
    "creator": {
      "id": 1,
      "username": "user123",
      "organization_name": "组织名称"
    },
    "organization": {
      "id": 1,
      "name": "组织名称"
    },
    "is_template": false,
    "template_source": null,
    "clone_count": 0,
    "indicators": [],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  },
  "error": {}
}
```

**状态流转错误响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "数据验证失败",
  "data": {},
  "error": {
    "status": ["不支持从已归档状态切换到启用状态"]
  }
}
```

---

## 6. 复制评分标准生成新标准

### 接口信息

- **URL**: `POST /api/v1/projectscore/criteria/clone/`
- **权限**: 组织用户
- **功能**: 基于已有评分标准（源标准）复制生成新标准，复制内容包括所有关联指标

### 请求参数

```json
{
  "source_criteria_id": 1,
  "name": "新的评分标准",
  "description": "基于模板创建的新标准",
  "requirement": 2
}
```

#### 参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| source_criteria_id | integer | 是 | 源评分标准ID |
| name | string | 否 | 新标准名称，默认"新的评分标准" |
| description | string | 否 | 新标准描述，默认"基于模板创建的新标准" |
| requirement | integer | 否 | 关联需求ID |

### 响应示例

**成功响应 (201)**:

```json
{
  "status": "success",
  "code": 201,
  "message": "评分标准复制成功",
  "data": {
    "id": 5,
    "name": "新的评分标准",
    "description": "基于模板创建的新标准",
    "status": "active",
    "status_display": "启用",
    "requirement": {
      "id": 2,
      "title": "新需求标题"
    },
    "creator": {
      "id": 1,
      "username": "user123",
      "organization_name": "组织名称"
    },
    "organization": {
      "id": 1,
      "name": "组织名称"
    },
    "is_template": false,
    "template_source": {
      "id": 1,
      "name": "源评分标准名称"
    },
    "clone_count": 0,
    "indicators": [
      {
        "id": 10,
        "name": "技术创新性",
        "description": "评估项目的技术创新程度",
        "weight": 30.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 1
      }
    ],
    "created_at": "2024-01-15T14:30:00Z",
    "updated_at": "2024-01-15T14:30:00Z"
  },
  "error": {}
}
```

**源标准不存在响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "业务规则验证失败",
  "data": {},
  "error": {
    "non_field_errors": ["源评分标准不存在或无权访问"]
  }
}
```

---

## 7. 删除评分标准

### 接口信息

- **URL**: `DELETE /api/v1/projectscore/criteria/{criteria_id}/delete/`
- **权限**: 组织创建者、组织管理员、该评分标准创建者
- **功能**: 物理删除评分标准（永久删除数据）
- **限制**: 已关联"已提交/已公示"项目评分的标准不可删除

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "评分标准删除成功",
  "data": {},
  "error": {}
}
```

**权限不足响应 (403)**:

```json
{
  "status": "error",
  "code": 403,
  "message": "权限不足，只有组织管理员或评分标准创建者可以删除",
  "data": {},
  "error": {}
}
```

**删除限制响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "删除失败，评分标准已被使用",
  "data": {},
  "error": {
    "non_field_errors": ["该评分标准已用于项目评选，不可删除"]
  }
}
```

---

## 注意：获取模板列表功能整合说明

原来的"获取可用模板列表"接口已整合到"获取评分标准列表"接口中。

**使用方法**：
- 获取模板列表：`GET /api/v1/projectscore/criteria/?is_template=true`
- 获取非模板列表：`GET /api/v1/projectscore/criteria/?is_template=false`
- 获取全部列表：`GET /api/v1/projectscore/criteria/`

这种设计的优势：
- 减少API接口数量，提高一致性
- 统一的分页、搜索、排序逻辑
- 更灵活的筛选组合（可同时按模板状态和其他条件筛选）

---

## 错误码说明

| HTTP状态码 | 错误类型 | 说明 |
|------------|----------|------|
| 200 | 成功 | 请求成功 |
| 201 | 创建成功 | 资源创建成功 |
| 400 | 请求错误 | 请求参数错误 |
| 401 | 未授权 | 用户未登录或token无效 |
| 403 | 禁止访问 | 用户权限不足 |
| 404 | 资源不存在 | 请求的资源不存在 |
| 422 | 验证错误 | 数据验证失败或业务规则冲突 |
| 429 | 请求过频 | 请求频率超过限制 |
| 500 | 服务器错误 | 服务器内部错误 |

## 权限说明

### 用户类型

- **学生用户**: `user_type = 'student'` 且拥有 `student_profile`
- **组织用户**: `user_type = 'organization'` 且拥有 `organization_profile`
- **组织创建者**: 组织的创建者用户
- **组织管理员**: 组织的管理员用户
- **评分标准创建者**: 该评分标准的创建者
- **系统管理员**: 拥有系统级管理权限的用户

### 权限级别

1. **学生用户权限**: 可以查看所有评分标准和指标，不能进行修改操作
2. **组织用户权限**: 可以查看所有评分标准和指标，可以创建、修改、删除本组织的评分标准
3. **组织管理员权限**: 拥有组织用户权限 + 可以切换任意标准状态
4. **创建者权限**: 可以修改和删除自己创建的标准
5. **组织创建者权限**: 拥有组织内所有权限
6. **系统管理员权限**: 拥有所有权限，可以操作任何组织的评分标准

### 具体权限控制

- **查看权限**: 所有认证用户都可以查看评分标准列表、详情和指标列表
- **创建权限**: 组织用户、组织管理员可以创建评分标准
- **修改权限**: 评分标准创建者、组织管理员、系统管理员可以修改评分标准
- **删除权限**: 评分标准创建者、组织管理员、系统管理员可以删除评分标准
- **指标管理权限**: 评分标准创建者、组织管理员、系统管理员可以管理评分指标

## 业务规则

### 评分标准状态流转

```
active (启用) ⇄ archived (归档)
```

- 启用和归档状态可以相互切换
- 删除操作为物理删除，不可恢复
- 新创建的评分标准默认状态为启用
- 启用和归档状态的标准都可以修改基础信息

**注意**: order字段用于控制评分指标在列表中的显示顺序，数值越小排序越靠前

### 删除限制

- 已关联"已提交"或"已公示"状态项目评分的标准不可删除
- 删除操作为物理删除，会永久删除数据，请谨慎操作

### 模板机制

- 任何评分标准都可以作为模板被复制
- 复制时会创建全新的独立标准
- 复制的标准默认状态为启用
- 会记录模板来源关系
- 复制时会同时复制所有关联的评分指标

### 评分标准使用状态判断

- **is_used_by_requirements 字段**: 用于快速判断评分标准是否被其他需求使用
- **使用场景**: 在创建新需求时，可通过此字段判断评分标准是否可直接关联使用
- **业务逻辑**: 
  - `false`: 评分标准未被其他需求使用，可直接关联
  - `true`: 评分标准已被其他需求使用，如需使用相同样式，应调用复制接口创建新的评分标准
- **实现方式**: 通过检查评分标准是否关联了任何需求来判断使用状态

### 权重验证

- **总权重验证**: 所有指标权重之和必须严格等于100，不允许大于或小于100
- **单个指标权重范围**: 每个指标的权重必须在0-100之间（包含0和100）
- **指标满分验证**: 每个指标的满分（max_score）必须大于0
- **指标数量要求**: 创建评分标准时至少需要包含1个评分指标
- **权重精度**: 权重支持小数，建议保留1位小数以确保精确计算
- **批量操作权重验证**: 在更新评分标准时，如果同时进行指标更新和新指标创建，所有指标（包括现有的、更新的和新创建的）的权重总和必须等于100

#### 权重验证示例

**正确示例**:
```json
{
  "indicators": [
    {"weight": 40.0, "max_score": 100.0},
    {"weight": 35.0, "max_score": 100.0},
    {"weight": 25.0, "max_score": 100.0}
  ]
}
// 总权重: 40 + 35 + 25 = 100 ✓
```

**错误示例**:
```json
{
  "indicators": [
    {"weight": 50.0, "max_score": 100.0},
    {"weight": 30.0, "max_score": 100.0}
  ]
}
// 总权重: 50 + 30 = 80 ≠ 100 ✗
```

---

# 评分指标管理 API 文档

## 概述

评分指标是评分标准的组成部分，用于定义具体的评分维度。本节描述了评分指标的 CRUD 操作接口。

---

## 1. 创建评分指标

### 接口信息

- **URL**: `POST /api/v1/projectscore/criteria/{criteria_id}/indicators/create/`
- **权限**: 组织创建者、组织管理员、该评分标准创建者
- **功能**: 为指定评分标准添加新的评分指标，支持单个或批量创建
- **限制**: 仅状态为 `active`（启用）或 `inactive`（禁用）的评分标准可添加指标；若评分标准已被用于项目评选，不可添加指标

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |

### 请求参数

#### 单个指标创建

```json
{
  "name": "用户体验",
  "description": "评估产品的用户界面设计和交互体验",
  "weight": 15.0,
  "max_score": 100.0,
  "is_required": true,
  "order": 5
}
```

#### 批量指标创建

```json
{
  "indicators": [
    {
      "name": "用户体验",
      "description": "评估产品的用户界面设计和交互体验",
      "weight": 15.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 5
    },
    {
      "name": "安全性",
      "description": "评估系统的安全防护能力",
      "weight": 10.0,
      "max_score": 100.0,
      "is_required": false,
      "order": 6
    }
  ]
}
```

#### 参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| name | string | 是 | 指标名称，最大长度200字符，在同一评分标准内不可重复 |
| description | string | 否 | 指标描述 |
| weight | decimal | 是 | 指标权重，0-100之间，创建后所有指标权重之和必须等于100 |
| max_score | decimal | 是 | 指标满分，必须大于0 |
| is_required | boolean | 否 | 是否必填，默认false |
| order | integer | 否 | 排序顺序，用于控制指标在列表中的显示顺序，默认0 |
| indicators | array | 否 | 批量创建时的指标列表 |

### 响应示例

**单个指标创建成功响应 (201)**:

```json
{
  "status": "success",
  "code": 201,
  "message": "评分指标创建成功",
  "data": {
    "id": 5,
    "name": "用户体验",
    "description": "评估产品的用户界面设计和交互体验",
    "weight": 15.0,
    "max_score": 100.0,
    "is_required": true,
    "order": 5,
    "criteria": {
      "id": 1,
      "name": "软件项目评分标准"
    }
  },
  "error": {}
}
```

**批量指标创建成功响应 (201)**:

```json
{
  "status": "success",
  "code": 201,
  "message": "批量创建评分指标成功",
  "data": {
    "created_count": 2,
    "indicators": [
      {
        "id": 5,
        "name": "用户体验",
        "description": "评估产品的用户界面设计和交互体验",
        "weight": 15.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 5
      },
      {
        "id": 6,
        "name": "安全性",
        "description": "评估系统的安全防护能力",
        "weight": 10.0,
        "max_score": 100.0,
        "is_required": false,
        "order": 6
      }
    ]
  },
  "error": {}
}
```

**权重验证失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "数据验证失败",
  "data": {},
  "error": {
    "non_field_errors": ["添加指标后，所有指标权重总和必须等于100%，当前为115%"]
  }
}
```

---

## 2. 获取评分指标列表

### 接口信息

- **URL**: `GET /api/v1/projectscore/criteria/{criteria_id}/indicators/list/`
- **权限**: 认证用户
- **功能**: 获取指定评分标准下的所有评分指标，按 order 排序

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取指标列表成功",
  "data": {
    "criteria": {
      "id": 1,
      "name": "软件项目评分标准",
      "status": "active",
      "total_weight": 100.0
    },
    "indicators": [
      {
        "id": 1,
        "name": "技术创新性",
        "description": "评估项目在技术方案、架构设计等方面的创新程度",
        "weight": 30.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 1
      },
      {
        "id": 2,
        "name": "实用性",
        "description": "评估项目的实际应用价值和市场前景",
        "weight": 25.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 2
      },
      {
        "id": 3,
        "name": "技术实现质量",
        "description": "评估代码质量、系统稳定性、性能等技术实现水平",
        "weight": 25.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 3
      },
      {
        "id": 4,
        "name": "团队协作",
        "description": "评估团队成员间的协作效率和项目管理能力",
        "weight": 20.0,
        "max_score": 100.0,
        "is_required": false,
        "order": 4
      }
    ],
    "indicators_count": 4
  },
  "error": {}
}
```

**权限不足响应 (403)**:

```json
{
  "status": "error",
  "code": 403,
  "message": "您只能访问本组织的评分标准指标",
  "data": {},
  "error": {}
}
```

---

## 3. 更新评分指标

### 接口信息

- **URL**: `PUT/PATCH /api/v1/projectscore/criteria/{criteria_id}/indicators/{indicator_id}/update/`
- **权限**: 组织创建者、组织管理员、该评分标准创建者
- **功能**: 更新评分指标的信息，支持全量更新（PUT）或部分更新（PATCH）
- **限制**: 仅状态为 `draft`（草稿）或 `active`（启用）的评分标准可修改指标；若评分标准已被用于项目评选，不可修改指标

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |
| indicator_id | integer | 是 | 评分指标ID |

### 请求参数

```json
{
  "name": "技术创新性（更新）",
  "description": "评估项目在技术方案、架构设计、算法创新等方面的创新程度",
  "weight": 35.0,
  "max_score": 100.0,
  "is_required": true,
  "order": 1
}
```

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "评分指标更新成功",
  "data": {
    "id": 1,
    "name": "技术创新性（更新）",
    "description": "评估项目在技术方案、架构设计、算法创新等方面的创新程度",
    "weight": 35.0,
    "max_score": 100.0,
    "is_required": true,
    "order": 1,
    "criteria": {
      "id": 1,
      "name": "软件项目评分标准"
    }
  },
  "error": {}
}
```

---

## 4. 批量更新评分指标

> **注意：功能整合说明**  
> 批量更新评分指标的功能已整合到"更新评分标准基础信息"接口中（`PATCH /api/v1/projectscore/criteria/{criteria_id}/`）。  
> 推荐使用整合后的接口，通过 `indicators` 参数进行批量更新，可同时更新评分标准基础信息和指标信息。  
> 本接口仍然可用，但建议优先使用整合接口以获得更好的一致性体验。

### 接口信息

- **URL**: `PATCH /api/v1/projectscore/criteria/{criteria_id}/indicators/batch/update/`
- **权限**: 组织创建者、组织管理员、该评分标准创建者
- **功能**: 批量更新评分标准下的多个评分指标信息
- **限制**: 仅状态为 `active`（启用）或 `inactive`（禁用）的评分标准可批量更新指标；若评分标准已被用于项目评选，不可批量更新指标

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |

### 请求参数

```json
{
  "indicators": [
    {
      "id": 1,
      "name": "技术创新性（更新）",
      "description": "评估项目在技术方案、架构设计、算法创新等方面的创新程度",
      "weight": 35.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 1
    },
    {
      "id": 2,
      "name": "实用性（更新）",
      "description": "评估项目的实际应用价值和商业前景",
      "weight": 30.0,
      "max_score": 100.0,
      "is_required": true,
      "order": 2
    }
  ]
}
```

#### 参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| indicators | array | 是 | 要更新的指标列表 |
| indicators[].id | integer | 是 | 指标ID |
| indicators[].name | string | 否 | 指标名称，最大长度200字符 |
| indicators[].description | string | 否 | 指标描述 |
| indicators[].weight | decimal | 否 | 指标权重，0-100之间 |
| indicators[].max_score | decimal | 否 | 指标满分，必须大于0 |
| indicators[].is_required | boolean | 否 | 是否必填 |
| indicators[].order | integer | 否 | 排序顺序 |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "批量更新评分指标成功",
  "data": {
    "updated_count": 2,
    "indicators": [
      {
        "id": 1,
        "name": "技术创新性（更新）",
        "description": "评估项目在技术方案、架构设计、算法创新等方面的创新程度",
        "weight": 35.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 1
      },
      {
        "id": 2,
        "name": "实用性（更新）",
        "description": "评估项目的实际应用价值和商业前景",
        "weight": 30.0,
        "max_score": 100.0,
        "is_required": true,
        "order": 2
      }
    ]
  },
  "error": {}
}
```

**权重验证失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "数据验证失败",
  "data": {},
  "error": {
    "non_field_errors": ["更新后所有指标权重总和必须等于100%，当前为105%"]
  }
}
```

**指标不存在响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "数据验证失败",
  "data": {},
  "error": {
    "indicators": ["指标ID 999 不存在"]
  }
}
```

---

## 5. 删除评分指标

### 接口信息

- **URL**: `DELETE /api/v1/projectscore/criteria/{criteria_id}/indicators/{indicator_id}/delete/`
- **权限**: 组织创建者、组织管理员、该评分标准创建者
- **功能**: 删除指定评分指标（物理删除）
- **限制**: 仅状态为 `draft`（草稿）或 `active`（启用）的评分标准可删除指标；若评分标准已被用于项目评选，不可删除指标；已被 IndicatorScore 引用的指标不可删除

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |
| indicator_id | integer | 是 | 评分指标ID |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "评分指标删除成功",
  "data": {},
  "error": {}
}
```

**指标被引用响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "删除失败，指标已被使用",
  "data": {},
  "error": {
    "non_field_errors": ["该指标已被用于项目评分，不可删除"]
  }
}
```

---

## 6. 批量删除评分指标

### 接口信息

- **URL**: `DELETE /api/v1/projectscore/criteria/{criteria_id}/indicators/batch/delete/`
- **权限**: 组织创建者、组织管理员、该评分标准创建者
- **功能**: 批量删除指定的评分指标（物理删除）
- **限制**: 仅状态为 `active`（启用）的评分标准可删除指标；若评分标准已被用于项目评选，不可删除指标；已被 IndicatorScore 引用的指标不可删除
- **错误处理策略**: 策略B - 部分成功处理，返回成功和失败的详细信息

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| criteria_id | integer | 是 | 评分标准ID |

### 请求参数

**Content-Type**: `application/x-www-form-urlencoded` 或 `multipart/form-data`

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| indicator_ids | string | 是 | 要删除的指标ID列表，逗号分隔，如："1,2,3" |

### 请求示例

**Form-data 格式**:
```
indicator_ids: "1,2,3"
```

**URL-encoded 格式**:
```
indicator_ids=1%2C2%2C3
```

### 响应示例

**全部成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "批量删除成功，共删除 3 个评分指标",
  "data": {
    "total_count": 3,
    "success_count": 3,
    "error_count": 0,
    "success_results": [
      {
        "id": 1,
        "name": "技术创新性",
        "message": "删除成功"
      },
      {
        "id": 2,
        "name": "实用性",
        "message": "删除成功"
      },
      {
        "id": 3,
        "name": "技术实现质量",
        "message": "删除成功"
      }
    ],
    "error_results": []
  },
  "error": {}
}
```

**部分成功响应 (207)**:

```json
{
  "status": "success",
  "code": 207,
  "message": "批量删除部分成功，成功删除 2 个，失败 1 个",
  "data": {
    "total_count": 3,
    "success_count": 2,
    "error_count": 1,
    "success_results": [
      {
        "id": 1,
        "name": "技术创新性",
        "message": "删除成功"
      },
      {
        "id": 2,
        "name": "实用性",
        "message": "删除成功"
      }
    ],
    "error_results": [
      {
        "id": 3,
        "name": "技术实现质量",
        "error": "该指标已被评分记录引用，不可删除"
      }
    ]
  },
  "error": {}
}
```

**全部失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "批量删除失败，共 3 个指标删除失败",
  "data": {},
  "error": {
    "total_count": 3,
    "success_count": 0,
    "error_count": 3,
    "success_results": [],
    "error_results": [
      {
        "id": 1,
        "name": "技术创新性",
        "error": "该指标已被评分记录引用，不可删除"
      },
      {
        "id": 2,
        "name": "实用性",
        "error": "该指标已被评分记录引用，不可删除"
      },
      {
        "id": 999,
        "name": null,
        "error": "指标不存在或不属于该评分标准"
      }
    ]
  }
}
```

**参数验证失败响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "参数验证失败",
  "data": {},
  "error": {
    "indicator_ids": ["indicator_ids字段为必填项"]
  }
}
```

**格式错误响应 (422)**:

```json
{
  "status": "error",
  "code": 422,
  "message": "参数验证失败",
  "data": {},
  "error": {
    "indicator_ids": ["indicator_ids格式错误，应为逗号分隔的数字"]
  }
}
```

### 错误处理策略说明

本接口采用**策略B（部分成功处理）**：

1. **逐个处理**: 对每个指标ID进行独立的删除操作
2. **详细反馈**: 返回每个指标的处理结果（成功或失败及原因）
3. **状态码规则**:
   - 200: 全部成功
   - 207: 部分成功（Multi-Status）
   - 422: 全部失败或参数错误
4. **事务处理**: 每个指标的删除操作独立进行，成功的删除不会因其他指标失败而回滚

### 常见错误原因

1. **指标不存在**: 指定的指标ID不存在或不属于该评分标准
2. **指标被引用**: 指标已被评分记录（IndicatorScore）引用，不可删除
3. **评分标准状态**: 评分标准状态不为 `active`
4. **评分标准被使用**: 评分标准已被用于项目评选
5. **权限不足**: 用户没有删除权限
6. **参数格式错误**: indicator_ids 格式不正确

---

## 评分指标业务规则

### 权重管理规则

1. **权重范围**: 单个指标权重必须在0-100之间
2. **权重精度**: 支持小数，建议保留1位小数
3. **权重建议**: 建议在完成所有指标配置后，手动调整权重总和为100%

### 指标约束规则

1. **名称唯一性**: 在同一评分标准内，指标名称不可重复
2. **满分限制**: 指标满分（max_score）必须大于0
3. **状态限制**: 只有草稿和启用状态的评分标准可以修改指标
4. **使用限制**: 已被用于项目评选的评分标准不可修改指标
5. **引用限制**: 已被 IndicatorScore 引用的指标不可删除

### 排序规则

1. **默认排序**: 按 order 字段升序排列
2. **相同排序**: order 相同时按创建时间排序
3. **排序更新**: 支持通过更新 order 字段调整指标显示顺序

### 批量操作规则

1. **原子性**: 批量操作要么全部成功，要么全部失败
2. **名称验证**: 批量操作中的指标名称不可重复
3. **批量创建限制**: 通过更新评分标准接口批量创建新指标时，需要确保权重总和为100
4. **混合操作**: 支持在同一请求中同时更新现有指标和创建新指标
5. **事务安全**: 批量创建新指标与更新现有指标在同一事务中执行，确保数据一致性

---

# 项目评分管理接口

## 1. 创建项目评分

### 接口信息

- **URL**: `POST /api/v1/projectscore/evaluations/{project_id}/create/`
- **权限**: 组织创建者、组织管理员、该需求创建者
- **功能**: 为指定项目创建评分记录，支持在创建时完成所有指标的评分
- **限制**: 只能为已完成的项目创建评分，每个项目只能有一个评分记录
- **说明**: 系统会自动通过项目ID查找关联的需求，并获取对应的评分标准

### 请求参数

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | integer | 是 | 项目ID |

#### 请求体参数

```json
{
  "overall_comment": "项目整体表现优秀，技术实现水平较高",
  "indicator_scores": [
    {
      "indicator_id": 1,
      "score": 85.0,
      "comment": "技术创新性较好，有一定的创新点"
    },
    {
      "indicator_id": 2,
      "score": 90.0,
      "comment": "实用性很强，市场前景良好"
    },
    {
      "indicator_id": 3,
      "score": 88.0,
      "comment": "代码质量较高，系统稳定性好"
    },
    {
      "indicator_id": 4,
      "score": 82.0,
      "comment": "团队协作良好，项目管理规范"
    }
  ]
}
```

#### 参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| overall_comment | string | 否 | 总体评语 |
| indicator_scores | array | 否 | 指标评分列表 |
| indicator_scores[].indicator_id | integer | 是 | 指标ID |
| indicator_scores[].score | decimal | 是 | 评分，0-指标满分之间 |
| indicator_scores[].comment | string | 否 | 评分评语 |

### 响应示例

**成功响应 (201)**:

```json
{
  "status": "success",
  "code": 201,
  "message": "项目评分创建成功",
  "data": {
    "id": 1,
    "project": {
      "id": 1,
      "title": "智能学习系统",
      "description": "基于AI技术的个性化学习平台",
      "status": "completed",
      "status_display": "已完成",
      "requirement": {
        "id": 1,
        "title": "智能学习系统开发需求",
        "organization": {
          "id": 1,
          "name": "计算机学院"
        }
      }
    },
    "criteria": {
      "id": 1,
      "name": "软件项目评分标准",
      "description": "用于评估软件开发项目的综合标准",
      "status": "active",
      "status_display": "启用"
    },
    "evaluator": {
      "id": 1,
      "username": "teacher001",
      "real_name": "张老师",
      "avatar_url": "http://localhost:8000/media/avatars/1/avatar.jpg"
    },
    "status": "draft",
    "status_display": "草稿",
    "total_score": "345.00",
    "weighted_score": "86.25",
    "overall_comment": "项目整体表现优秀，技术实现水平较高",
    "indicator_scores": [
      {
        "id": 1,
        "indicator": 1,
        "indicator_name": "技术创新性",
        "indicator_weight": "30.00",
        "indicator_max_score": 100,
        "score": "85.00",
        "comment": "技术创新性较好，有一定的创新点",
        "weighted_score": "25.50"
      },
      {
        "id": 2,
        "indicator": 2,
        "indicator_name": "实用性",
        "indicator_weight": "25.00",
        "indicator_max_score": 100,
        "score": "90.00",
        "comment": "实用性很强，市场前景良好",
        "weighted_score": "22.50"
      },
      {
        "id": 3,
        "indicator": 3,
        "indicator_name": "技术实现质量",
        "indicator_weight": "25.00",
        "indicator_max_score": 100,
        "score": "88.00",
        "comment": "代码质量较高，系统稳定性好",
        "weighted_score": "22.00"
      },
      {
        "id": 4,
        "indicator": 4,
        "indicator_name": "团队协作",
        "indicator_weight": "20.00",
        "indicator_max_score": 100,
        "score": "82.00",
        "comment": "团队协作良好，项目管理规范",
        "weighted_score": "16.40"
      }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z"
  },
  "error": {}
}
```

---

## 2. 获取项目评分详情

### 接口信息

- **URL**: `GET /api/v1/projectscore/evaluations/{project_id}/`
- **权限**: 认证用户
- **功能**: 获取指定项目的评分详细信息

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | integer | 是 | 项目ID |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取项目评分详情成功",
  "data": {
    "id": 1,
    "project": {
      "id": 1,
      "title": "智能学习系统",
      "description": "基于AI技术的个性化学习平台",
      "status": "completed",
      "status_display": "已完成",
      "requirement": {
        "id": 1,
        "title": "智能学习系统开发需求",
        "organization": {
          "id": 1,
          "name": "计算机学院"
        }
      }
    },
    "criteria": {
      "id": 1,
      "name": "软件项目评分标准",
      "description": "用于评估软件开发项目的综合标准",
      "status": "active",
      "status_display": "启用"
    },
    "evaluator": {
      "id": 1,
      "username": "teacher001",
      "real_name": "张老师",
      "avatar_url": "http://localhost:8000/media/avatars/1/avatar.jpg"
    },
    "status": "completed",
    "status_display": "已完成",
    "total_score": "345.00",
    "weighted_score": "86.25",
    "overall_comment": "项目整体表现优秀，技术实现水平较高",
    "indicator_scores": [
      {
        "id": 1,
        "indicator": 1,
        "indicator_name": "技术创新性",
        "indicator_weight": "30.00",
        "indicator_max_score": 100,
        "score": "85.00",
        "comment": "技术创新性较好，有一定的创新点",
        "weighted_score": "25.50"
      }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  },
  "error": {}
}
```

---

## 3. 更新项目评分

### 接口信息

- **URL**: `PUT /api/v1/projectscore/evaluations/{project_id}/update/`
- **权限**: 组织创建者、组织管理员、该评分创建者
- **功能**: 更新项目评分，支持批量更新多个评分指标的分数和评语
- **限制**: 已公示的评分不可修改

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | integer | 是 | 项目ID |

### 请求参数

```json
{
  "overall_comment": "项目整体表现优秀，技术实现水平很高，建议进一步优化用户体验",
  "indicator_scores": [
    {
      "indicator_id": 1,
      "score": 88.0,
      "comment": "技术创新性很好，创新点突出"
    },
    {
      "indicator_id": 2,
      "score": 92.0,
      "comment": "实用性极强，市场前景非常好"
    }
  ]
}
```

#### 参数说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| overall_comment | string | 否 | 总体评语 |
| indicator_scores | array | 否 | 要更新的指标评分列表 |
| indicator_scores[].indicator_id | integer | 是 | 指标ID |
| indicator_scores[].score | decimal | 是 | 评分，0-指标满分之间 |
| indicator_scores[].comment | string | 否 | 评分评语 |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "项目评分更新成功",
  "data": {
    "id": 1,
    "project": 1,
    "project_title": "智能学习系统",
    "criteria": 1,
    "criteria_name": "软件项目评分标准",
    "evaluator": 1,
    "evaluator_name": "张老师",
    "last_modifier": 1,
    "last_modifier_name": "张老师",
    "status": "completed",
    "status_display": "已完成",
    "total_score": 360.0,
    "weighted_total_score": 90.0,
    "overall_comment": "项目整体表现优秀，技术实现水平很高，建议进一步优化用户体验",
    "indicator_scores": [
      {
        "id": 1,
        "indicator": {
          "id": 1,
          "name": "技术创新性",
          "weight": 30.0,
          "max_score": 100.0
        },
        "score": 88.0,
        "comment": "技术创新性很好，创新点突出"
      },
      {
        "id": 2,
        "indicator": {
          "id": 2,
          "name": "实用性",
          "weight": 25.0,
          "max_score": 100.0
        },
        "score": 92.0,
        "comment": "实用性极强，市场前景非常好"
      }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T11:00:00Z"
  },
  "error": {}
}
```

---

## 4. 提交项目评分

### 接口信息

- **URL**: `POST /api/v1/projectscore/evaluations/{project_id}/submit/`
- **权限**: 组织创建者、组织管理员、该评分创建者
- **功能**: 提交项目评分，检查必填指标完整性并将状态从draft改为submitted
- **限制**: 只有草稿状态的评分可以提交，已公示的评分不可修改

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| project_id | integer | 是 | 项目ID |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "项目评分提交成功",
  "data": {
    "id": 1,
    "project": 1,
    "project_title": "智能学习系统",
    "criteria": 1,
    "criteria_name": "软件项目评分标准",
    "evaluator": 1,
    "evaluator_name": "张老师",
    "status": "submitted",
    "status_display": "已提交",
    "total_score": 345.0,
    "weighted_total_score": 86.25,
    "overall_comment": "项目整体表现优秀，技术实现水平较高",
    "submitted_at": "2024-01-15T12:00:00Z",
    "updated_at": "2024-01-15T12:00:00Z"
  },
  "error": {}
}
```

**失败响应 (400) - 必填指标未完成**:

```json
{
  "status": "error",
  "code": 400,
  "message": "评分提交失败",
  "data": {},
  "error": {
    "detail": "以下必填指标尚未评分：技术创新性、实用性",
    "missing_indicators": [
      {
        "id": 1,
        "name": "技术创新性",
        "is_required": true
      },
      {
        "id": 2,
        "name": "实用性",
        "is_required": true
      }
    ]
  }
}
```

---

## 5. 获取项目排名

### 接口信息

- **URL**: `GET /api/v1/projectscore/requirements/{requirement_id}/ranking/`
- **权限**: 认证用户
- **功能**: 获取指定需求下已完成并评分的项目排名

### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| requirement_id | integer | 是 | 需求ID |

### 查询参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认1 |
| page_size | integer | 否 | 每页数量，默认10，最大50 |

### 响应示例

**成功响应 (200)**:

```json
{
  "status": "success",
  "code": 200,
  "message": "获取项目排名成功",
  "data": {
    "results": [
      {
        "rank": 1,
        "project": {
          "id": 1,
          "title": "智能学习系统",
          "status": "completed"
        },
        "project_leader": {
          "id": 1,
          "real_name": "张三",
          "username": "zhangsan"
        },
        "criteria": {
          "id": 1,
          "name": "软件项目评分标准"
        },
        "total_score": 360.0,
        "weighted_total_score": 90.0,
        "rank_level": "excellent",
        "rank_level_display": "优秀",
        "evaluated_at": "2024-01-15T11:00:00Z"
      },
      {
        "rank": 2,
        "project": {
          "id": 2,
          "title": "在线教育平台",
          "status": "completed"
        },
        "project_leader": {
          "id": 2,
          "real_name": "李四",
          "username": "lisi"
        },
        "criteria": {
          "id": 1,
          "name": "软件项目评分标准"
        },
        "total_score": 340.0,
        "weighted_total_score": 85.0,
        "rank_level": "good",
        "rank_level_display": "良好",
        "evaluated_at": "2024-01-15T10:45:00Z"
      }
    ],
    "pagination": {
      "current_page": 1,
      "total_pages": 1,
      "total_count": 2,
      "page_size": 10,
      "previous_url": null,
      "next_url": null
    }
  },
  "error": {}
}
```

---

## 项目评分业务规则

### 评分权限规则

1. **创建权限**: 组织创建者、组织管理员、该需求创建者可以创建项目评分
2. **查看权限**: 所有认证用户可以查看项目评分详情
3. **修改权限**: 组织创建者、组织管理员、该评分创建者可以修改项目评分
4. **状态限制**: 已公示的评分不可修改

### 评分计算规则

1. **总分计算**: 所有指标评分的总和
2. **加权总分计算**: 各指标评分 × 权重的总和
3. **排名规则**: 按加权总分降序排列
4. **等级划分**: 根据加权总分自动计算等级（优秀、良好、合格、不合格）

### 项目状态更新规则

1. **评分状态同步**: 创建项目评分时，自动将项目的 `is_evaluated` 字段设为 `true`
2. **最近修改人**: 更新评分时，自动记录最近修改人信息
3. **时间戳更新**: 每次修改评分时，自动更新 `updated_at` 时间戳

### 排名展示规则

1. **排名范围**: 仅显示已完成并评分的项目
2. **排名计算**: 按加权总分降序排列，相同分数并列排名
3. **分页支持**: 支持分页查询，默认每页10条记录
4. **实时更新**: 排名数据实时计算，反映最新的评分结果
5. **公示限制**: 需求截止前禁止调用排名接口，只有公示后才能查看排名

### 公示机制规则

1. **公示条件**: 需求截止时间到达后，管理员可以手动公示评分结果
2. **公示操作**: 将需求的 `evaluation_published` 字段设为 `true`
3. **公示后限制**: 评分公示后，所有评分状态变为 `published`，不可再修改
4. **排名访问**: 只有公示后才能访问项目排名接口
5. **项目详情**: 项目详情中的评分信息只有公示后才显示总成绩和排名