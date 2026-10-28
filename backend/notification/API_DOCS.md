# 通知系统接口文档

## 概述

本文档详细描述了基于WebSocket的实时通知系统的设计架构、接口规范以及使用方法。通知系统采用Django Channels实现WebSocket连接，支持实时推送、消息持久化、多种通知类型，并集成了在线人数统计功能。

## 系统架构

### 核心组件

- **通知模型层**: 定义通知数据结构和类型
- **服务层**: 实现通知业务逻辑和策略模式
- **WebSocket层**: 处理实时连接和消息推送
- **模板系统**: 格式化通知消息内容
- **异步任务**: 处理批量通知和定时任务

### 技术栈

- Django Channels (WebSocket支持)
- Redis (消息队列和缓存)
- Celery (异步任务处理)
- MySQL (数据持久化)

## 代码文件说明

### 核心文件

#### `models.py`
定义通知系统的数据模型：
- `NotificationType`: 通知类型配置（包含代码、名称、分类、描述等）
- `Notification`: 通知实例（包含接收者、发送者、内容、状态、优先级等）
- `NotificationTemplate`: 通知模板（标题模板、内容模板、模板变量）
- `NotificationPreference`: 用户通知偏好设置（通知方式、免打扰时间等）
- `NotificationLog`: 通知操作日志（发送记录、操作结果等）

#### `services.py`
通知服务层，包含：
- `NotificationStrategy`: 通知策略抽象基类
- `WebSocketNotificationStrategy`: WebSocket实时通知策略
- `EmailNotificationStrategy`: 邮件通知策略
- `SMSNotificationStrategy`: 短信通知策略
- `NotificationService`: 核心通知服务
- `OrganizationNotificationService`: 企业端组织用户通知服务
- 各种具体通知方法实现

#### `consumers.py`
WebSocket消费者：
- `NotificationConsumer`: 处理用户通知连接，同时管理在线用户统计
- `NotificationBroadcastConsumer`: 处理广播通知

#### `routing.py`
WebSocket路由配置

#### `templates.py`
通知消息模板和格式化工具

#### `tasks.py`
Celery异步任务定义：
- `send_requirement_deadline_reminders`: 发送需求截止评分提醒
- `send_project_scoring_notifications`: 发送项目评分通知
- `cleanup_old_notifications`: 清理旧通知
- `cleanup_old_notification_logs`: 清理旧通知日志
- `send_bulk_notification`: 批量发送通知
- `send_system_maintenance_notification`: 发送系统维护通知
- `generate_notification_statistics`: 生成通知统计
- `send_daily_deadline_reminders`: 每日截止提醒
- `send_weekly_deadline_reminders`: 每周截止提醒

#### `serializers.py`
DRF序列化器，用于API数据序列化

#### `views.py`
REST API视图集

#### `urls.py`
HTTP API路由配置

#### `signals.py`
Django信号处理器

#### `admin.py`
Django管理后台配置

## WebSocket接口

### 连接地址

#### 用户通知连接
```
ws://localhost:8000/ws/notifications/
```

**认证方式：**
- JWT Token认证（通过查询参数传递）：`ws://localhost:8000/ws/notifications/?token=your_jwt_token`
- Cookie认证（sessionid）
- 连接建立后会自动加入用户专属的通知组

#### 广播通知连接
```
ws://localhost:8000/ws/notification/broadcast/
```

**用途：**
- 系统级广播通知
- 管理员消息推送

**注意：** 用户通知连接同时负责在线人数统计，连接建立时会自动将用户添加到在线用户集合，断开时自动移除。

## Django管理员系统广播功能

### 功能概述

系统提供了完整的Django管理后台系统广播功能，允许管理员通过Web界面向用户发送系统级通知。

### 访问方式

1. 登录Django管理后台：`/admin/`
2. 进入 "通知详情" 页面
3. 在页面顶部点击蓝色的 "发送系统广播通知" 按钮
4. 填写广播内容并发送

### 广播类型

| 类型代码 | 类型名称 | 描述 |
|---------|---------|------|
| `system_announcement` | 系统公告 | 一般性系统公告和重要信息 |
| `maintenance_notice` | 维护通知 | 系统维护、升级相关通知 |
| `version_update` | 版本更新 | 系统版本更新和新功能介绍 |
| `urgent_notice` | 紧急通知 | 紧急情况和重要警告 |

### 目标用户选项

- **所有用户**: 向所有活跃用户发送
- **仅活跃用户**: 向最近30天内登录的用户发送
- **仅管理员**: 向管理员用户发送

### 发送策略

- **WebSocket**: 实时推送（默认启用）
- **邮件通知**: 可选择同时发送邮件

### 配置参数

- **优先级**: 普通、高、紧急
- **有效期**: 1-168小时（最多7天）
- **发送统计**: 实时显示发送成功率

### 使用示例

#### 系统维护通知
```
广播类型: 维护通知
标题: 系统维护通知 - 2024年1月15日
内容: 我们将于2024年1月15日 02:00-04:00 进行系统维护...
优先级: 高
有效期: 48小时
目标用户: 所有用户
```

#### 紧急安全通知
```
广播类型: 紧急通知
标题: 安全提醒：请立即修改密码
内容: 检测到异常登录活动，为保障账户安全...
优先级: 紧急
有效期: 24小时
目标用户: 所有用户
```

### 初始化命令

首次使用前需要运行初始化命令：

```bash
python manage.py init_system_broadcast_types
```

此命令会创建必要的通知类型和模板配置。

### 技术实现

- **表单处理**: 使用Django Forms进行数据验证
- **批量发送**: 通过NotificationService批量创建和发送通知
- **模板渲染**: 支持动态模板变量替换
- **错误处理**: 完整的异常处理和用户反馈
- **权限控制**: 仅管理员可访问系统广播功能

详细使用指南请参考：`notification/SYSTEM_BROADCAST_GUIDE.md`



### WebSocket消息格式

#### 客户端发送消息

##### 标记通知已读
```json
{
    "type": "mark_as_read",
    "notification_id": 123
}
```

**响应：**
```json
{
    "type": "mark_read_response",
    "success": true,
    "notification_id": 123
}
```

##### 获取未读通知数量
```json
{
    "type": "get_unread_count"
}
```

**响应：**
```json
{
    "type": "unread_count",
    "count": 5
}
```

##### 获取最近通知列表
```json
{
    "type": "get_recent_notifications",
    "limit": 10
}
```

**响应：**
```json
{
    "type": "recent_notifications",
    "notifications": [
        {
            "id": 123,
            "title": "新项目申请",
            "content": "学生张三申请加入您的项目",
            "notification_type": {
                "code": "student_project_application_audit",
                "name": "学生项目申请审核通知"
            },
            "priority": "HIGH",
            "created_at": "2024-01-15T10:30:00Z",
            "is_read": false,
            "sender": {
                "id": 456,
                "username": "zhangsan",
                "first_name": "三",
                "last_name": "张"
            }
        }
    ]
}
```



#### 服务端推送消息

##### 新通知推送
```json
{
    "type": "notification",
    "data": {
        "id": 123,
        "title": "新项目申请",
        "content": "学生张三申请加入您的项目",
        "notification_type": {
            "code": "student_project_application_audit",
            "name": "学生项目申请审核通知",
            "category": "project"
        },
        "priority": "HIGH",
        "status": "UNREAD",
        "created_at": "2024-01-15T10:30:00Z",
        "is_read": false,
        "sender": {
            "id": 456,
            "username": "zhangsan",
            "first_name": "三",
            "last_name": "张"
        },
        "metadata": {
            "project_id": 789,
            "application_id": 101
        }
    }
}
```

##### 未读数量更新
```json
{
    "type": "unread_count",
    "count": 5
}
```

##### 错误消息
```json
{
    "type": "error",
    "message": "通知不存在或无权限访问"
}
```



## REST API接口

### 基础URL
```
/api/v1/notification/
```

### 通知列表

#### 获取通知列表
```http
GET /api/v1/notification/notifications/
```

**查询参数：**
- `is_read`: 是否已读 (true/false)
- `notification_type`: 通知类型
- `priority`: 优先级 (LOW/MEDIUM/HIGH/URGENT)
- `page`: 页码
- `page_size`: 每页数量

**响应示例：**
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/v1/notification/notifications/?page=2",
    "previous": null,
    "results": [
        {
            "id": 123,
            "title": "项目申请通知",
            "content": "用户张三申请加入您的项目",
            "notification_type": "PROJECT_APPLICATION",
            "priority": "HIGH",
            "created_at": "2024-01-20T10:30:00Z",
            "is_read": false,
            "metadata": {
                "project_id": 456,
                "applicant_id": 789
            }
        }
    ]
}
```

#### 标记通知已读
```http
POST /api/v1/notification/notifications/{id}/mark_read/
```

**响应：**
```json
{
    "success": true,
    "message": "通知已标记为已读"
}
```

#### 批量标记已读
```http
POST /api/v1/notification/notifications/mark_all_read/
```

**请求体：**
```json
{
    "notification_ids": [123, 124, 125]
}
```

#### 获取未读数量
```http
GET /api/v1/notification/notifications/unread_count/
```

**响应：**
```json
{
    "count": 5
}
```



### 通知类型管理

#### 获取通知类型列表
```http
GET /api/v1/notification/types/
```

**响应示例：**
```json
[
    {
        "code": "PROJECT_APPLICATION",
        "name": "项目申请",
        "category": "PROJECT",
        "description": "用户申请加入项目时发送的通知",
        "default_template": "用户{applicant_name}申请加入项目{project_name}",
        "is_active": true
    }
]
```

## 通知类型和触发情形

### 已实现的企业端组织用户通知类型

#### 1. 新用户注册审核通知 (org_user_registration_audit)
- **触发时机**: 新用户申请加入组织且状态为待审核时
- **接收者**: 组织管理员（admin、super_admin权限用户）
- **优先级**: HIGH
- **模板变量**: applicant_name, organization_name, applicant_email
- **示例**: "用户张三申请加入您的组织，请及时审核"
- **实现位置**: `notification/signals.py` - `handle_organization_member_change`
- **服务方法**: `send_user_registration_audit_notification`

#### 2. 组织用户权限变更通知 (org_user_permission_change)
- **触发时机**: 组织成员权限发生变更时（适用于所有权限变更，不仅限于管理员）
- **接收者**: 被变更权限的用户
- **优先级**: HIGH
- **模板变量**: user_name, operator_name, organization_name, old_permission, new_permission, old_permission_display, new_permission_display, change_time
- **示例**: "您在组织中的权限已被更新，新权限为：管理员"
- **通知内容**: 详细说明权限变更的具体内容，包括操作者信息、原权限和新权限，并明确告知被通知者最新的权限状态
- **实现位置**: `notification/signals.py` - `handle_organization_member_change`
- **服务方法**: `send_organization_permission_change_notification`
- **向后兼容**: 保留 `send_admin_permission_change_notification` 别名方法
- **额外说明**: 包含权限的中文显示名称，便于用户理解权限变更内容

#### 2.1. 用户状态变更通知 (org_user_status_change)
- **触发时机**: 组织成员状态发生变更时（如审核通过、拒绝等）
- **接收者**: 被变更状态的用户
- **优先级**: HIGH
- **模板变量**: user_name, operator_name, organization_name, old_status, new_status, old_status_display, new_status_display, change_time
- **示例**: "您在组织中的状态已被更新为：已通过"
- **实现位置**: `notification/signals.py` - `handle_organization_member_change`
- **服务方法**: `send_organization_status_change_notification`
- **状态映射**: pending(待审核), approved(已通过), rejected(已拒绝), active(活跃), inactive(非活跃)

#### 2.2. 用户权限和状态同时变更通知 (org_user_permission_and_status_change)
- **触发时机**: 组织成员权限和状态同时发生变更时
- **接收者**: 被变更的用户
- **优先级**: HIGH
- **模板变量**: user_name, operator_name, organization_name, old_permission, new_permission, old_status, new_status, old_permission_display, new_permission_display, old_status_display, new_status_display, change_time
- **示例**: "您在组织中的权限和状态已被更新"
- **实现位置**: `notification/signals.py` - `handle_organization_member_change`
- **服务方法**: `send_organization_permission_and_status_change_notification`

#### 3. 项目创建对接需求通知 (org_project_requirement_created)
- **触发时机**: 
  1. 学生创建项目并对接需求且项目状态为招募中（recruiting）或进行中（in_progress）时
  2. 项目状态从草稿（draft）变更为招募中（recruiting）或进行中（in_progress）且项目关联需求时
- **接收者**: 需求创建者本人
- **优先级**: MEDIUM
- **模板变量**: student_name, project_title, requirement_title
- **示例**: "学生张三创建了项目'智慧校园系统'对接您发布的需求"
- **实现位置**: `notification/signals.py` - `handle_project_change`
- **服务方法**: `send_project_requirement_notification`
- **状态限制**: 仅在项目状态为 'recruiting' 或 'in_progress' 时发送

#### 4. 项目成果提交通知 (org_deliverable_submitted)
- **触发时机**: 学生提交项目成果时
- **接收者**: 需求创建者
- **优先级**: MEDIUM
- **模板变量**: student_name, project_title, deliverable_title
- **示例**: "学生张三提交了项目成果，请查看并评价"
- **实现位置**: `notification/signals.py` - `handle_deliverable_submission`
- **服务方法**: `send_deliverable_submission_notification`

#### 5. 项目完成通知 (org_project_completed)
- **触发时机**: 项目状态变更为"已完成"、"已暂停"或"已取消"时（completed, paused, cancelled, 已完成, 已暂停, 已取消）
- **接收者**: 需求创建者
- **优先级**: MEDIUM
- **模板变量**: project_title, old_status, new_status
- **示例**: "项目状态已更新为：已完成"
- **实现位置**: `notification/signals.py` - `handle_project_change`
- **服务方法**: `send_project_status_change_notification`
- **状态限制**: 仅在特定状态变更时发送通知

#### 6. 需求截止评分提醒通知 (org_requirement_deadline_reminder)
- **触发时机**: 需求截止后，且存在已完成项目时
- **接收者**: 需求创建者
- **优先级**: URGENT
- **模板变量**: requirement_title, deadline, requirement_status, completed_project_count, pending_score_count
- **示例**: "您的需求已截止，可以为已完成项目评分"
- **通知目的**: 提醒需求创建者：需求已截止，可以为已完成项目评分
- **实现位置**: `notification/tasks.py` - `send_requirement_deadline_reminders` 定时任务
- **服务方法**: `send_requirement_deadline_reminder`
- **防重复**: 24小时内不重复发送
- **触发条件**: 仅在需求下存在已完成项目时发送

#### 7. 项目评分通知 (org_project_scored)
- **触发时机**: 项目完成后需要评分时（通过定时任务检测已完成但未评分的项目）
- **接收者**: 需求创建者
- **优先级**: MEDIUM
- **模板变量**: project_title, score
- **示例**: "项目已完成，请及时进行评分"
- **通知目的**: 提醒需求创建者：需求截止后即可对已完成的项目评分
- **实现位置**: `notification/tasks.py` - `send_project_scoring_notifications` 定时任务
- **服务方法**: `send_project_scoring_notification`
- **防重复**: 7天内不重复发送

#### 8. 项目评论通知 (org_project_commented)
- **触发时机**: 项目被评论时
- **接收者**: 项目成员
- **优先级**: MEDIUM
- **模板变量**: commenter_name, project_title, comment_content
- **示例**: "您的项目收到了新的评论"
- **实现位置**: `notification/signals.py` - `handle_project_comment`
- **服务方法**: `send_project_comment_notification`
- **内容限制**: 评论内容超过100字符时截断

#### 9. 成果评论通知 (org_deliverable_commented)
- **触发时机**: 项目成果被评论时
- **接收者**: 项目成员
- **优先级**: MEDIUM
- **模板变量**: commenter_name, project_title, deliverable_title, comment_content
- **示例**: "您的项目成果收到了新的评论"
- **实现位置**: `notification/signals.py` - `handle_deliverable_comment`
- **服务方法**: `send_deliverable_comment_notification`
- **内容限制**: 评论内容超过100字符时截断

#### 10. 评论回复通知 (org_comment_reply)
- **触发时机**: 评论被回复时
- **接收者**: 原评论创建者
- **优先级**: LOW
- **模板变量**: replier_name, project_title, comment_content
- **示例**: "您的评论收到了新的回复"
- **实现位置**: `notification/signals.py` - `handle_comment_reply`
- **服务方法**: `send_project_comment_reply_notification` 或 `send_deliverable_comment_reply_notification`
- **内容限制**: 评论内容超过100字符时截断

### 已实现的学生端通知类型

#### 1. 学生项目申请审核通知 (student_project_application)
- **触发时机**: 学生申请加入某学生项目时
- **接收者**: 项目负责人（leader）
- **优先级**: HIGH
- **模板变量**: applicant_name, leader_name, project_title, application_time, application_message, project_url
- **示例**: "学生张三申请加入您的项目'智慧校园系统'，请及时审核"
- **服务方法**: `send_project_application_notification`

#### 2. 申请审核结果通知 (student_application_result)
- **触发时机**: 项目负责人审核申请后
- **接收者**: 申请人
- **优先级**: HIGH
- **模板变量**: applicant_name, project_title, result, result_display, review_time, review_message, project_url
- **示例**: "您申请加入项目'智慧校园系统'的审核结果：已通过"
- **服务方法**: `send_application_result_notification`
- **状态映射**: approved(已通过), rejected(已拒绝), pending(待审核)

#### 3. 项目成员状态变更通知 (student_member_status_change)
- **触发时机**: 项目成员状态发生变更时（包括踢出成员等）
- **接收者**: 被变更状态的成员
- **优先级**: HIGH
- **模板变量**: member_name, project_title, old_status, new_status, old_status_display, new_status_display, change_time, operator_name, project_url
- **示例**: "您在项目'智慧校园系统'中的状态已变更为：已退出"
- **服务方法**: `send_member_status_change_notification`
- **状态映射**: pending(待审核), approved(已通过), rejected(已拒绝), left(已退出)

#### 4. 项目邀请通知 (student_project_invitation)
- **触发时机**: 项目负责人给其他同学发送邀请时
- **接收者**: 被邀请人
- **优先级**: MEDIUM
- **模板变量**: inviter_name, invitee_name, project_title, invitation_time, invitation_message, expires_at, invitation_url
- **示例**: "张三邀请您加入项目'智慧校园系统'，邀请将在7天后过期"
- **服务方法**: `send_project_invitation_notification`
- **有效期**: 邀请有效期为7天

#### 5. 邀请过期提醒通知 (student_invitation_expiry_reminder)
- **触发时机**: 邀请到期前一天（通过定时任务触发）
- **接收者**: 被邀请人
- **优先级**: MEDIUM
- **模板变量**: invitee_name, inviter_name, project_title, expires_at, invitation_url
- **示例**: "您收到的项目邀请即将过期，请及时处理"
- **服务方法**: `send_invitation_expiry_reminder`
- **实现位置**: `notification/tasks.py` - `send_invitation_expiry_reminders` 定时任务
- **防重复**: 12小时内不重复发送

#### 6. 邀请反馈通知 (student_invitation_response)
- **触发时机**: 被邀请人对邀请进行反馈时
- **接收者**: 项目负责人
- **优先级**: HIGH
- **模板变量**: inviter_name, invitee_name, project_title, response, response_display, response_time, response_message, project_url
- **示例**: "李四已接受您的项目邀请"
- **服务方法**: `send_invitation_response_notification`
- **响应类型**: accepted(已接受), rejected(已拒绝)

#### 7. 项目状态变更通知 (student_project_status_change)
- **触发时机**: 项目负责人修改项目状态为"已完成"、"已暂停"、"已取消"时
- **接收者**: 所有项目成员
- **优先级**: HIGH
- **模板变量**: project_title, old_status, new_status, old_status_display, new_status_display, change_time, operator_name, members_removed, project_url
- **示例**: "项目'智慧校园系统'状态已变更为：已完成"
- **服务方法**: `send_project_status_change_notification`
- **状态映射**: active(进行中), completed(已完成), suspended(已暂停), cancelled(已取消)
- **特殊处理**: 当项目被取消且成员被移出时，会在通知中说明成员已被移出项目

#### 8. 成员被移出项目通知 (student_member_kicked)
- **触发时机**: 项目成员被项目负责人移出项目时
- **接收者**: 被移出的成员
- **优先级**: HIGH
- **模板变量**: member_name, project_title, change_time, operator_name, reason
- **示例**: "您已被移出项目'智慧校园系统'"
- **服务方法**: `send_member_kicked_notification`

#### 9. 成员退出通知 (student_member_left)
- **触发时机**: 项目成员自愿退出时
- **接收者**: 项目负责人
- **优先级**: MEDIUM
- **模板变量**: leader_name, member_name, project_title, left_time, member_role_display, project_url
- **示例**: "成员王五已退出项目'智慧校园系统'"
- **服务方法**: `send_member_left_notification`
- **注意**: 与状态变更通知区分，避免重复通知

#### 10. 项目被评价通知 (student_project_commented)
- **触发时机**: 项目或项目成果被组织用户评价时
- **接收者**: 所有项目成员
- **优先级**: MEDIUM
- **模板变量**: project_title, commenter_name, comment_time, comment_content, comment_url
- **示例**: "您的项目'智慧校园系统'收到了新的评价"
- **服务方法**: `send_project_commented_notification`

#### 11. 项目评分公示通知 (student_project_score_published)
- **触发时机**: 项目评分结果公示发布时
- **接收者**: 所有项目成员
- **优先级**: HIGH
- **模板变量**: project_title, total_score, weighted_score, evaluator_name, publish_time, score_url
- **示例**: "您的项目'智慧校园系统'评分已公示，总分：85分"
- **服务方法**: `send_project_score_published_notification`

### 通知优先级说明

- **URGENT**: 紧急通知，需要立即处理
- **HIGH**: 高优先级，需要及时关注
- **MEDIUM**: 中等优先级，正常处理
- **LOW**: 低优先级，可延后处理

## 企业端通知服务架构

### OrganizationNotificationService 类

企业端通知服务是专门为组织用户设计的通知服务层，继承自基础的 `NotificationService`，提供了8种专门的通知类型。

#### 服务实例化
```python
from notification.services import org_notification_service

# 全局单例实例，可直接使用
org_notification_service.send_user_registration_audit_notification(...)
```

#### 通知类型代码规范
所有企业端通知类型代码都以 `org_` 前缀开头，便于识别和管理：
- `org_user_registration_audit`
- `org_user_permission_change`
- `org_project_requirement_created`
- `org_deliverable_submitted`
- `org_project_completed`
- `org_requirement_deadline_reminder`
- `org_project_scored`
- `org_comment_reply`

#### 信号处理机制

通知的触发主要通过Django信号机制实现，在 `signals.py` 中定义了各种模型变更的信号处理器：

```python
# 组织成员变更信号
@receiver(post_save, sender=OrganizationMember)
def handle_organization_member_change(sender, instance, created, **kwargs):
    # 处理新成员加入和权限变更
    
# 项目变更信号
@receiver(post_save, sender=Project)
def handle_project_change(sender, instance, created, **kwargs):
    # 处理项目创建和状态变更
    
# 成果提交信号
@receiver(post_save, sender=Deliverable)
def handle_deliverable_submission(sender, instance, created, **kwargs):
    # 处理成果提交
```

#### 定时任务机制

部分通知通过Celery定时任务触发：

```python
# 需求截止评分提醒（每日执行）
@shared_task
def send_requirement_deadline_reminders():
    # 检查已截止且有已完成项目的需求，发送评分提醒
    
# 项目评分通知（每日执行）
@shared_task
def send_project_scoring_notifications():
    # 检查已完成但未评分的项目
```

#### 防重复发送机制

为避免重复发送通知，系统实现了多种防重复机制：

1. **时间窗口检查**: 在指定时间内不重复发送相同类型通知
2. **关联对象检查**: 基于关联对象ID检查是否已发送
3. **状态条件检查**: 只在特定条件满足时发送通知

### 模板变量系统

每种通知类型都支持模板变量，用于动态生成通知内容：

```python
# 示例：权限变更通知
template_vars = {
    'operator_name': '管理员张三',
    'organization_name': '智慧科技有限公司',
    'old_permission': 'member',
    'new_permission': 'admin'
}
```

## 使用示例

### 前端WebSocket连接示例

```javascript
// 建立WebSocket连接
const ws = new WebSocket(
    `ws://localhost:8000/ws/notifications/?token=${jwtToken}`
);

// 连接建立
ws.onopen = function(event) {
    console.log('WebSocket连接已建立');
    // 连接成功后获取未读数量
    ws.send(JSON.stringify({
        'type': 'get_unread_count'
    }));
};

// 监听消息
ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('收到消息:', data);
    
    switch(data.type) {
        case 'notification':
            // 显示新通知
            showNotification(data.data);
            break;
        case 'unread_count':
            // 更新未读数量
            updateUnreadCount(data.count);
            break;
        case 'recent_notifications':
            // 显示最近通知
            displayRecentNotifications(data.notifications);
            break;
        case 'mark_read_response':
            // 处理已读确认
            handleReadConfirmation(data);
            break;
        case 'error':
            console.error('错误:', data.message);
            break;
    }
};

// 连接关闭
ws.onclose = function(event) {
    console.log('WebSocket连接已关闭');
    // 可以实现重连逻辑
};

// 连接错误
ws.onerror = function(error) {
    console.log('WebSocket错误:', error);
};

// 标记通知已读
function markAsRead(notificationId) {
    ws.send(JSON.stringify({
        type: 'mark_as_read',
        notification_id: notificationId
    }));
}

// 获取未读数量
function getUnreadCount() {
    ws.send(JSON.stringify({
        type: 'get_unread_count'
    }));
}

// 获取最近通知
function getRecentNotifications(limit = 10) {
    ws.send(JSON.stringify({
        type: 'get_recent_notifications',
        limit: limit
    }));
}
```



### 后端发送通知示例

```python
from notification.services import notification_service

# 发送项目申请通知
notification_service.send_project_application_notification(
    project=project,
    applicant=user,
    application_data={'message': '希望能加入这个项目'}
)

# 发送系统公告
notification_service.create_and_send_notification(
    recipients=[user1, user2],
    notification_type='SYSTEM_ANNOUNCEMENT',
    title='系统维护通知',
    content='系统将于今晚进行维护',
    priority='HIGH'
)
```

## 通知模板系统

### 模板管理器

通知系统使用 `NotificationTemplateManager` 类来管理所有通知模板，提供以下功能：

- `render_template(template_type, context)`: 渲染指定类型的模板
- `get_template_variables(template_type)`: 获取模板变量说明
- `validate_template_context(template_type, context)`: 验证模板上下文
- `preview_template(template_type, context)`: 预览模板渲染结果

### 模板结构

每个通知模板包含以下字段：
- `title`: 通知标题模板
- `content`: 通知内容模板
- `email_subject`: 邮件主题模板（可选）
- `email_content`: 邮件内容模板（可选）
- `sms_content`: 短信内容模板（可选）
- `variables`: 模板变量说明

### 当前已配置的通知模板

#### 企业端通知模板

##### 1. 用户注册审核通知 (org_user_registration_audit)
```python
{
    'title': '新用户注册申请',
    'content': '用户 {{user_name}} ({{user_email}}) 申请加入 {{organization_name}}，请及时审核。',
    'email_subject': '新用户注册申请 - {{organization_name}}',
    'email_content': '您好，\n\n用户 {{user_name}} ({{user_email}}) 申请加入您的组织 {{organization_name}}。\n\n申请时间：{{application_time}}\n\n请登录系统进行审核。',
    'sms_content': '新用户{{user_name}}申请加入{{organization_name}}，请及时审核。',
    'variables': {
        'user_name': '申请用户姓名',
        'user_email': '申请用户邮箱',
        'organization_name': '组织名称',
        'application_time': '申请时间'
    }
}
```

##### 2. 项目成果提交通知 (org_deliverable_submitted)
```python
{
    'title': '项目成果提交通知',
    'content': '学生 {{student_name}} 提交了项目 "{{project_title}}" 的成果 "{{deliverable_title}}"。',
    'email_subject': '项目成果提交 - {{project_title}}',
    'email_content': '您好，\n\n学生 {{student_name}} 已提交项目成果：\n\n项目：{{project_title}}\n成果：{{deliverable_title}}\n提交时间：{{submission_time}}\n\n请及时查看和评审。',
    'sms_content': '学生{{student_name}}提交了项目成果，请及时查看。',
    'variables': {
        'student_name': '学生姓名',
        'project_title': '项目标题',
        'deliverable_title': '成果标题',
        'submission_time': '提交时间',
        'deliverable_description': '成果描述',
        'file_count': '文件数量',
        'deliverable_url': '成果链接'
    }
}
```

#### 学生端通知模板

##### 1. 项目邀请通知 (student_project_invitation)
```python
{
    'title': '项目邀请',
    'content': '{{inviter_name}} 邀请您加入项目 "{{project_title}}"。',
    'email_subject': '项目邀请 - {{project_title}}',
    'email_content': '您好 {{invitee_name}}，\n\n{{inviter_name}} 邀请您加入项目 "{{project_title}}"。\n\n邀请留言：{{invitation_message}}\n\n请在 {{expires_at}} 前回复邀请。',
    'sms_content': '{{inviter_name}}邀请您加入项目{{project_title}}，请及时回复。',
    'variables': {
        'inviter_name': '邀请人姓名',
        'invitee_name': '被邀请人姓名',
        'project_title': '项目标题',
        'invitation_time': '邀请时间',
        'invitation_message': '邀请留言',
        'expires_at': '过期时间'
    }
}
```

##### 2. 项目评分公示通知 (student_project_score_published)
```python
{
    'title': '项目评分公示',
    'content': '您的项目 "{{project_title}}" 评分结果已公示，总分：{{total_score}}分。',
    'email_subject': '项目评分公示 - {{project_title}}',
    'email_content': '您好，\n\n您的项目 "{{project_title}}" 评分结果已公示：\n\n总分：{{total_score}}分\n加权分：{{weighted_score}}分\n评分人：{{evaluator_name}}\n公示时间：{{publish_time}}\n\n详情请查看系统。',
    'sms_content': '您的项目{{project_title}}评分已公示，总分{{total_score}}分。',
    'variables': {
        'project_title': '项目标题',
        'total_score': '总分',
        'weighted_score': '加权分',
        'evaluator_name': '评分人姓名',
        'publish_time': '公示时间',
        'score_url': '评分详情链接'
    }
}
```

### 模板变量分类

#### 用户相关变量
- `user_name`: 用户姓名
- `user_email`: 用户邮箱
- `organization_name`: 组织名称
- `student_name`: 学生姓名
- `inviter_name`: 邀请人姓名
- `invitee_name`: 被邀请人姓名
- `member_name`: 成员姓名
- `leader_name`: 项目负责人姓名
- `commenter_name`: 评论者姓名
- `replier_name`: 回复人姓名
- `evaluator_name`: 评分人姓名
- `operator_name`: 操作人姓名

#### 项目相关变量
- `project_title`: 项目标题
- `project_description`: 项目描述
- `project_url`: 项目链接
- `requirement_title`: 需求标题
- `deliverable_title`: 成果标题
- `deliverable_description`: 成果描述
- `deliverable_url`: 成果链接
- `file_count`: 文件数量

#### 时间相关变量
- `application_time`: 申请时间
- `approval_time`: 审批时间
- `rejection_time`: 拒绝时间
- `creation_time`: 创建时间
- `submission_time`: 提交时间
- `update_time`: 更新时间
- `completion_time`: 完成时间
- `change_time`: 变更时间
- `invitation_time`: 邀请时间
- `response_time`: 回复时间
- `transfer_time`: 转移时间
- `publish_time`: 公示时间
- `comment_time`: 评论时间
- `reply_time`: 回复时间
- `left_time`: 退出时间
- `expires_at`: 过期时间
- `deadline`: 截止时间

#### 状态相关变量
- `old_status`: 原状态代码
- `new_status`: 新状态代码
- `old_status_display`: 原状态显示名
- `new_status_display`: 新状态显示名
- `response`: 回复结果代码
- `response_display`: 回复结果显示名
- `requirement_status`: 需求状态

#### 内容相关变量
- `invitation_message`: 邀请留言
- `response_message`: 回复留言
- `transfer_message`: 转移说明
- `comment_content`: 评论内容
- `reply_content`: 回复内容
- `original_comment_content`: 原评论内容
- `rejection_reason`: 拒绝理由
- `reason`: 操作理由

#### 评分相关变量
- `total_score`: 总分
- `weighted_score`: 加权分
- `score_url`: 评分详情链接

#### 统计相关变量
- `completed_project_count`: 已完成项目数
- `pending_score_count`: 待评分项目数

#### 联系相关变量
- `new_leader_contact`: 新负责人联系方式
- `comment_url`: 评论链接

### 模板渲染示例

```python
from notification.templates import NotificationTemplateManager

# 创建模板管理器实例
template_manager = NotificationTemplateManager()

# 渲染通知模板
context = {
    'user_name': '张三',
    'organization_name': '智慧科技有限公司',
    'application_time': '2024-01-15 10:30:00'
}

rendered = template_manager.render_template(
    'org_user_registration_audit', 
    context
)

print(rendered['title'])    # 新用户注册申请
print(rendered['content'])  # 用户 张三 申请加入 智慧科技有限公司，请及时审核。
```

## 配置说明

### 环境变量

```bash
# Redis配置（用于WebSocket和Celery）
REDIS_URL=redis://localhost:6379/0

# Celery配置
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Django设置

```python
# settings.py
INSTALLED_APPS = [
    # ...
    'channels',
    'notification',
    # ...
]

# Channels配置
ASGI_APPLICATION = 'Project_Zhihui.asgi.application'
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

### 路由配置

```python
# notification/routing.py
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/notification/<int:user_id>/', consumers.NotificationConsumer.as_asgi()),
    path('ws/notification/broadcast/', consumers.NotificationBroadcastConsumer.as_asgi()),
]

# notification/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # ... 其他路由
]
```

## 性能优化

### 连接管理
- 使用Redis管理WebSocket连接状态
- 自动清理断开的连接
- 支持水平扩展


### 消息队列
- 使用Celery处理大量通知发送
- 支持延时发送和定时任务
- 失败重试机制

### 数据库优化
- 通知数据分页加载
- 索引优化查询性能
- 定期清理过期通知

## 监控和日志

### 日志记录
- WebSocket连接和断开日志
- 通知发送成功/失败日志
- 性能监控日志

### 监控指标
- 活跃WebSocket连接数
- 通知发送成功率
- 平均响应时间
- 未读通知数量统计
- 实时在线用户数量
- 在线人数统计连接数
- Redis在线用户集合大小

## 故障排除

### 常见问题

1. **WebSocket连接失败**
   - 检查JWT Token是否有效
   - 确认Redis服务是否正常
   - 检查防火墙设置

2. **通知发送失败**
   - 检查Celery服务状态
   - 确认数据库连接正常
   - 查看错误日志

3. **消息延迟**
   - 检查Redis性能
   - 监控Celery队列长度
   - 优化数据库查询

### 调试工具

```bash
# 查看Celery任务状态
celery -A Project_Zhihui inspect active

# 监控Redis连接
redis-cli monitor

# 查看WebSocket连接
python manage.py shell
>>> from channels.layers import get_channel_layer
>>> channel_layer = get_channel_layer()
```

## 版本历史

- **v1.0.0**: 基础通知功能实现
- **v1.1.0**: 添加WebSocket实时推送
- **v1.2.0**: 支持通知模板和优先级
- **v1.3.0**: 添加批量操作和异步任务

## 联系方式

如有问题或建议，请联系开发团队。