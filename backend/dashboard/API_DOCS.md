# Dashboard API 文档

## 概述

Dashboard API 提供系统统计数据的查询接口，包括用户在线状态、标签统计、项目状态统计、组织状态统计等功能。所有接口均支持Redis缓存机制，优先返回缓存数据以提升性能。

## 基础信息

- **基础URL**: `/api/v1/dashboard/`
- **认证方式**: Token认证（已配置为认证用户可见）
- **响应格式**: JSON
- **缓存机制**: Redis缓存，默认1小时过期

## 通用响应格式

### 成功响应
```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        // 具体数据内容
    }
}
```

### 错误响应
```json
{
    "code": 500,
    "message": "错误描述",
    "data": null
}
```

## 接口列表

### 1. 实时在线人数统计

**接口地址**: `GET /api/v1/dashboard/online-count/`

**功能描述**: 获取当前系统实时在线用户数量

**权限要求**: 需要Token认证

**请求参数**: 无

**响应示例**:
```json
{
    "code": 200,
    "message": "操作成功",
    "data": {
        "online_count": 156,
        "message": "当前在线人数: 156",
        "timestamp": 1704067200,
        "cache_info": {
            "is_cached": false,
            "data_source": "redis",
            "query_time": 1704067200.789
        }
    }
}
```

**字段说明**:
- `online_count`: 当前在线用户数量
- `message`: 描述信息
- `timestamp`: 查询时间戳

---

### 2. Tag1学生标签统计

**接口地址**: `GET /api/v1/dashboard/tag1-student-stats/`

**功能描述**: 获取关联学生数最多的前5个Tag1标签统计，包含数量和百分比

**权限要求**: 需要Token认证

**请求参数**: 无

**响应示例**:
```json
{
    "code": 200,
    "message": "获取Tag1学生标签统计成功",
    "data": {
        "top_tags": [
            {
                "tag_id": 1,
                "tag_name": "计算机科学",
                "student_count": 245,
                "percentage": 32.15
            },
            {
                "tag_id": 3,
                "tag_name": "人工智能",
                "student_count": 189,
                "percentage": 24.80
            }
        ],
        "total_students_with_tags": 762,
        "stats_date": "2024-01-01",
        "cache_info": {
            "is_cached": true,
            "created_at": "2024-01-15T10:30:00Z",
            "expires_at": "2024-01-15T22:30:00Z",
            "expire_seconds": 43200,
            "cache_key": "dashboard_stats:tag1_students",
            "data_source": "cache"
        }
    }
}
```

**字段说明**:
- `top_tags`: 前5个标签统计数组
  - `tag_id`: 标签ID
  - `tag_name`: 标签名称（Tag1.value字段）
  - `student_count`: 关联学生数量
  - `percentage`: 占比百分比
- `total_students_with_tags`: 拥有Tag1标签的学生总数
- `stats_date`: 统计日期

**缓存策略**: 每4小时更新一次（热点数据）

---

### 3. Tag2学生标签统计

**接口地址**: `GET /api/v1/dashboard/tag2-student-stats/`

**功能描述**: 获取关联学生数最多的前5个Tag2标签统计，包含数量和百分比

**权限要求**: 需要Token认证

**请求参数**: 无

**响应示例**:
```json
{
    "code": 200,
    "message": "获取Tag2学生标签统计成功",
    "data": {
        "top_tags": [
            {
                "tag_id": 5,
                "tag_name": "软件工程师",
                "student_count": 312,
                "percentage": 28.45
            },
            {
                "tag_id": 8,
                "tag_name": "数据分析师",
                "student_count": 267,
                "percentage": 24.32
            }
        ],
        "total_students_with_tags": 1097,
        "stats_date": "2024-01-01",
        "cache_info": {
            "is_cached": true,
            "created_at": "2024-01-15T11:00:00Z",
            "expires_at": "2024-01-15T23:00:00Z",
            "expire_seconds": 43200,
            "cache_key": "dashboard_stats:tag2_students",
            "data_source": "cache"
        }
    }
}
```

**字段说明**:
- `top_tags`: 前5个标签统计数组
  - `tag_id`: 标签ID
  - `tag_name`: 标签名称（Tag2.post字段）
  - `student_count`: 关联学生数量
  - `percentage`: 占比百分比
- `total_students_with_tags`: 拥有Tag2标签的学生总数
- `stats_date`: 统计日期

**缓存策略**: 每4小时更新一次（热点数据）

---

### 4. 项目状态统计

**接口地址**: `GET /api/v1/dashboard/project-status-stats/`

**功能描述**: 获取项目状态分布统计（排除草稿状态），按状态统计项目数量和百分比

**权限要求**: 需要Token认证

**请求参数**: 无

**响应示例**:
```json
{
    "code": 200,
    "message": "获取项目状态统计成功（缓存）",
    "data": {
        "status_stats": [
            {
                "status_code": "published",
                "status_name": "已发布",
                "project_count": 245,
                "percentage": 45.8
            },
            {
                "status_code": "in_progress",
                "status_name": "进行中",
                "project_count": 189,
                "percentage": 35.3
            }
        ],
        "total_projects": 535,
        "excluded_status": "draft",
        "stats_date": "2024-01-15",
        "cache_info": {
            "is_cached": true,
            "created_at": "2024-01-15T12:00:00Z",
            "expires_at": "2024-01-16T00:00:00Z",
            "expire_seconds": 43200,
            "cache_key": "dashboard_stats:project_status",
            "data_source": "cache"
        }
    }
}
```

**字段说明**:
- `status_stats`: 状态统计数组
  - `status_code`: 状态代码
  - `status_name`: 状态显示名称
  - `project_count`: 该状态的项目数量
  - `percentage`: 占比百分比
- `total_projects`: 项目总数（排除草稿状态）
- `excluded_status`: 被排除的状态
- `stats_date`: 统计日期

**缓存策略**: 每2小时更新一次（变化较频繁）

---

### 5. 组织认证状态统计

**接口地址**: `GET /api/v1/dashboard/organization-status-stats/`

**功能描述**: 获取组织认证状态分布统计，包含已认证、审核中、待认证、已关闭等状态的组织数量

**权限要求**: 需要Token认证

**请求参数**: 无

**响应示例**:
```json
{
    "code": 200,
    "message": "获取组织状态统计成功（缓存）",
    "data": {
        "all_status_stats": [
            {
                "status_code": "certified",
                "status_name": "已认证",
                "organization_count": 156,
                "percentage": 52.35
            },
            {
                "status_code": "under_review",
                "status_name": "审核中",
                "organization_count": 89,
                "percentage": 29.87
            }
        ],
        "key_status_stats": {
            "certified": {
                "count": 156,
                "name": "已认证",
                "percentage": 52.35
            },
            "under_review": {
                "count": 89,
                "name": "审核中",
                "percentage": 29.87
            },
            "pending": {
                "count": 34,
                "name": "待认证",
                "percentage": 11.41
            },
            "closed": {
                "count": 19,
                "name": "已关闭",
                "percentage": 6.38
            }
        },
        "total_organizations": 298,
        "stats_date": "2024-01-01",
        "cache_info": {
            "is_cached": true,
            "created_at": "2024-01-15T14:00:00Z",
            "expires_at": "2024-01-16T02:00:00Z",
            "expire_seconds": 43200,
            "cache_key": "dashboard_stats:org_status",
            "data_source": "cache"
        }
    }
}
```

**字段说明**:
- `all_status_stats`: 所有状态统计数组
- `key_status_stats`: 关键状态统计对象
  - `certified`: 已认证组织统计
  - `under_review`: 审核中组织统计
  - `pending`: 待认证组织统计
  - `closed`: 已关闭组织统计
- `total_organizations`: 组织总数
- `stats_date`: 统计日期

**缓存策略**: 每日6:30更新一次

---

### 6. 项目Tag1标签统计

**接口地址**: `GET /api/v1/dashboard/project-tag1-stats/`

**功能描述**: 获取关联项目数最多的前5个Tag1标签统计，通过需求(Requirement)关联统计项目数量和百分比

**权限要求**: 需要Token认证

**请求参数**: 无

**响应示例**:
```json
{
    "code": 200,
    "message": "获取项目Tag1标签统计成功（缓存）",
    "data": {
        "top_tags": [
            {
                "tag_id": 2,
                "tag_name": "Web开发",
                "project_count": 187,
                "percentage": 31.22
            },
            {
                "tag_id": 7,
                "tag_name": "移动应用",
                "project_count": 143,
                "percentage": 23.87
            }
        ],
        "total_projects_with_tags": 599,
        "stats_date": "2024-01-01",
        "cache_info": {
            "is_cached": true,
            "created_at": "2024-01-15T16:00:00Z",
            "expires_at": "2024-01-16T04:00:00Z",
            "expire_seconds": 43200,
            "cache_key": "dashboard_stats:project_tag1",
            "data_source": "cache"
        }
    }
}
```

**字段说明**:
- `top_tags`: 前5个标签统计数组
  - `tag_id`: 标签ID
  - `tag_name`: 标签名称（Tag1.value字段）
  - `project_count`: 关联项目数量
  - `percentage`: 占比百分比
- `total_projects_with_tags`: 拥有Tag1标签的项目总数
- `stats_date`: 统计日期

**缓存策略**: 每日7:00更新一次

---

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 500 | 服务器内部错误 |
| 503 | Redis连接失败 |

## 缓存机制

### 缓存键格式
```
dashboard:{stats_type}:{YYYYMMDD}
```

### 缓存类型
- `tag1_students`: Tag1学生标签统计
- `tag2_students`: Tag2学生标签统计
- `project_status`: 项目状态统计
- `org_status`: 组织状态统计
- `project_tag1`: 项目Tag1标签统计

### 缓存配置
- **默认过期时间**: 12小时（43200秒）
- **Redis配置**: 使用项目默认Redis配置
- **缓存策略**: 优先返回缓存数据，缓存未命中时查询数据库并更新缓存

### 缓存信息字段

所有接口返回的数据中都包含 `cache_info` 字段，提供缓存相关信息：

```json
{
  "cache_info": {
    "is_cached": true,           // 是否来自缓存
    "created_at": "2024-01-15T10:30:00Z",  // 缓存创建时间
    "expires_at": "2024-01-15T22:30:00Z",  // 缓存过期时间
    "expire_seconds": 43200,     // 缓存有效期（秒）
    "cache_key": "dashboard_stats:tag1_students",  // 缓存键
    "data_source": "cache"       // 数据来源：cache/database/redis
  }
}
```

- `is_cached`: `true` 表示数据来自缓存，`false` 表示实时查询
- `data_source`: 
  - `cache`: 来自Redis缓存
  - `database`: 来自数据库实时查询
  - `redis`: 来自Redis直接查询（如在线人数）
- 实时查询的数据会包含 `query_time` 字段表示查询时间戳

## Celery定时任务

### 任务调度配置

所有Dashboard统计任务已配置在主 `celery.py` 文件中：

| 任务名称 | 执行时间 | 任务函数 | 功能描述 |
|----------|----------|----------|----------|
| `update-dashboard-stats-daily` | 每天6:00 | `dashboard.tasks.update_all_dashboard_stats` | 更新所有Dashboard统计数据 |
| `update-tag1-student-stats-frequent` | 每4小时 | `dashboard.tasks.update_tag1_student_stats` | 更新Tag1学生标签统计 |
| `update-tag2-student-stats-frequent` | 每4小时 | `dashboard.tasks.update_tag2_student_stats` | 更新Tag2学生标签统计 |
| `update-project-status-stats-frequent` | 每2小时 | `dashboard.tasks.update_project_status_stats` | 更新项目状态统计 |
| `update-organization-status-stats-daily` | 每天6:30 | `dashboard.tasks.update_organization_status_stats` | 更新组织状态统计 |
| `update-project-tag1-stats-daily` | 每天7:00 | `dashboard.tasks.update_project_tag1_stats` | 更新项目Tag1标签统计 |

### 启动Celery服务

```bash
# 启动Celery Worker
celery -A Project_Zhihui worker --loglevel=info

# 启动Celery Beat调度器
celery -A Project_Zhihui beat --loglevel=info

# 同时启动Worker和Beat
celery -A Project_Zhihui worker --beat --loglevel=info
```

### 监控命令

```bash
# 查看定时任务状态
celery -A Project_Zhihui inspect scheduled

# 查看活跃任务
celery -A Project_Zhihui inspect active

# 手动执行任务（测试用）
celery -A Project_Zhihui call dashboard.tasks.update_all_dashboard_stats
```

## 权限配置

所有接口已配置为认证用户可见，使用Token认证：

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def your_view_function(request):
    # 接口逻辑
```

### 获取Token

用户需要先通过认证接口获取Token，然后在请求头中携带：

```
Authorization: Token your_token_here
```

## 测试接口

项目根目录下的 `test_dashboard_apis.py` 脚本可用于测试所有接口功能：

```bash
python test_dashboard_apis.py
```

## 注意事项

1. **数据一致性**: 统计数据通过Celery定时任务更新，可能存在轻微延迟
2. **缓存失效**: Redis连接失败时会直接查询数据库
3. **性能优化**: 热点数据（Tag1/Tag2学生统计、项目状态）更新频率较高
4. **错误处理**: 所有接口都包含完善的异常处理机制
5. **扩展性**: 可根据业务需求调整缓存时间和更新频率

## 更新日志

- **v1.0.0**: 初始版本，包含6个核心统计接口
- 支持Redis缓存机制
- 集成Celery定时任务自动更新
- 完善的错误处理和日志记录