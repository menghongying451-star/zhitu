# StudentProject 应用 API 设计文档

## 概述

本文档设计了学生项目对接系统的完整API接口，包括项目管理、参与者管理、成果提交、评论系统和通知功能。

## API 接口设计

### 1. 项目管理接口

#### 1.1 项目列表
**接口**: `GET /api/v1/studentproject/projects/`  
**描述**: 获取项目列表，支持分页、筛选和搜索  
**权限**: 认证用户  

**查询参数**:
- `page`: 页码 (默认: 1)
- `page_size`: 每页数量 (默认: 10, 最大: 50)
- `status`: 项目状态筛选 (planning/active/completed/paused/cancelled)
- `requirement_id`: 需求ID筛选
- `creator_id`: 创建者ID筛选
- `keyword`: 搜索关键词 (项目标题、描述)
- `sort`: 排序字段 (created_at/updated_at/title)
- `order`: 排序方式 (asc/desc)

**响应示例**:
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/v1/studentproject/projects/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "AI智能客服系统开发",
            "description": "基于大语言模型的智能客服系统...",
            "status": "active",
            "requirement": {
                "id": 1,
                "title": "AI智能客服系统开发需求"
            },
            "creator": {
                "id": 1,
                "name": "张三",
                "student_id": "2021001"
            },
            "participants_count": 5,
            "deliverables_count": 3,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-20T15:45:00Z"
        }
    ]
}
```

#### 1.2 项目详情
**接口**: `GET /api/v1/studentproject/projects/{id}/`  
**描述**: 获取项目详细信息  
**权限**: 认证用户  

**响应示例**:
```json
{
    "id": 1,
    "title": "AI智能客服系统开发",
    "description": "基于大语言模型的智能客服系统...",
    "status": "active",
    "requirement": {
        "id": 1,
        "title": "AI智能客服系统开发需求",
        "organization": "科技公司A"
    },
    "creator": {
        "id": 1,
        "name": "张三",
        "student_id": "2021001",
        "school": "清华大学",
        "major": "计算机科学与技术"
    },
    "participants": [
        {
            "id": 1,
            "student": {
                "id": 2,
                "name": "李四",
                "student_id": "2021002"
            },
            "role": "前端开发",
            "status": "active",
            "applied_at": "2024-01-16T09:00:00Z"
        }
    ],
    "deliverables": [
        {
            "id": 1,
            "title": "需求分析文档",
            "stage_type": "前期",
            "stage_version": "前期v1",
            "is_milestone": true,
            "submitted_at": "2024-01-18T14:30:00Z"
        }
    ],
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-20T15:45:00Z"
}
```

#### 1.3 创建项目
**接口**: `POST /api/v1/studentproject/projects/`  
**描述**: 创建新项目  
**权限**: 学生用户  

**请求体**:
```json
{
    "title": "AI智能客服系统开发",
    "description": "基于大语言模型的智能客服系统...",
    "requirement_id": 1,
    "status": "planning"
}
```

#### 1.4 更新项目
**接口**: `PUT /api/v1/studentproject/projects/{id}/`  
**描述**: 更新项目信息  
**权限**: 项目创建者  

#### 1.5 删除项目
**接口**: `DELETE /api/v1/studentproject/projects/{id}/`  
**描述**: 删除项目  
**权限**: 项目创建者  

### 2. 参与者管理接口

#### 2.1 申请加入项目
**接口**: `POST /api/v1/studentproject/projects/{project_id}/apply/`  
**描述**: 学生申请加入项目  
**权限**: 学生用户  

**请求体**:
```json
{
    "role": "前端开发",
    "message": "我有2年前端开发经验，熟悉React和Vue..."
}
```

#### 2.2 处理申请
**接口**: `POST /api/v1/studentproject/participants/{participant_id}/review/`  
**描述**: 项目负责人处理加入申请  
**权限**: 项目创建者  

**请求体**:
```json
{
    "action": "approve",  // approve/reject
    "message": "欢迎加入项目团队！"
}
```

#### 2.3 参与者列表
**接口**: `GET /api/v1/studentproject/projects/{project_id}/participants/`  
**描述**: 获取项目参与者列表  
**权限**: 认证用户  

#### 2.4 移除参与者
**接口**: `DELETE /api/v1/studentproject/participants/{participant_id}/`  
**描述**: 移除项目参与者  
**权限**: 项目创建者或参与者本人  

### 3. 项目成果管理接口

#### 3.1 成果列表
**接口**: `GET /api/v1/studentproject/projects/{project_id}/deliverables/`  
**描述**: 获取项目成果列表  
**权限**: 项目成员  

**查询参数**:
- `stage_type`: 阶段筛选 (前期/中期/末期)
- `is_milestone`: 是否里程碑 (true/false)
- `submitter_id`: 提交者ID筛选

#### 3.2 成果详情
**接口**: `GET /api/v1/studentproject/deliverables/{id}/`  
**描述**: 获取成果详细信息  
**权限**: 项目成员  

#### 3.3 提交成果
**接口**: `POST /api/v1/studentproject/projects/{project_id}/deliverables/`  
**描述**: 提交项目成果  
**权限**: 项目成员  

**请求体方式一 - 使用已存在的文件ID**:
```json
{
    "title": "需求分析文档",
    "description": "详细的需求分析文档，包含功能需求和非功能需求",
    "stage_type": "前期",
    "is_milestone": true,
    "progress_description": "完成了需求调研和分析工作",
    "parent_deliverable_id": null,
    "files": [1, 2, 3]  // 已存在的File记录ID列表
}
```

**请求体方式二 - 一并创建新的文件记录**:
```json
{
    "title": "需求分析文档",
    "description": "详细的需求分析文档，包含功能需求和非功能需求",
    "stage_type": "前期",
    "is_milestone": true,
    "progress_description": "完成了需求调研和分析工作",
    "new_files": [
        {
            "name": "需求分析文档.pdf",
            "url": "https://pan.baidu.com/s/1234567890abcdef",
            "size": 2048576,
            "path": "/项目文档/需求分析"
        },
        {
            "name": "用户调研报告.docx",
            "url": "https://cloud.189.cn/share/xyz123",
            "size": 1024000
        }
    ]
}
```

**请求体方式三 - 使用网盘链接方式**:
```json
{
    "title": "需求分析文档",
    "description": "详细的需求分析文档，包含功能需求和非功能需求",
    "stage_type": "前期",
    "is_milestone": true,
    "progress_description": "完成了需求调研和分析工作",
    "cloud_links": [
        {
            "url": "https://pan.baidu.com/s/1234567890abcdef",
            "password": "abc123",
            "path": "/项目文档/需求分析/网盘链接"
        },
        {
            "url": "https://cloud.189.cn/share/xyz123",
            "password": "def456"
        }
    ]
}
```

**请求体方式四 - 混合使用（既有已存在文件，又创建新文件，还有网盘链接）**:
```json
{
    "title": "需求分析文档",
    "description": "详细的需求分析文档，包含功能需求和非功能需求",
    "stage_type": "前期",
    "is_milestone": true,
    "progress_description": "完成了需求调研和分析工作",
    "files": [1, 2],  // 已存在的文件ID
    "new_files": [    // 新创建的文件
        {
            "name": "补充材料.pdf",
            "url": "https://pan.baidu.com/s/newfile123",
            "size": 512000
        }
    ],
    "cloud_links": [  // 网盘链接
        {
            "url": "https://pan.baidu.com/s/cloudlink456",
            "password": "xyz789"
        }
    ]
}
```

**new_files字段说明**:
- `name`: 文件名称（必填）
- `url`: 网盘链接地址（必填，除非提供real_path）
- `size`: 文件大小，单位字节（可选，默认0）
- `path`: 虚拟路径（可选，默认为 `/项目成果/{阶段类型}`）
- `real_path`: 本地文件路径（可选，用于本地上传文件）

**cloud_links字段说明**:
- `url`: 网盘链接地址（必填）
- `password`: 网盘链接提取密码（可选）
- `path`: 虚拟路径（可选，默认为 `/项目成果/{阶段类型}/网盘链接`）

**网盘链接文件特点**:
- 文件名称自动设置为"网盘链接"
- 文件大小为0（不记录实际大小）
- 不显示real_path字段
- 支持存储网盘密码
- 通过is_cloud_link字段标识为网盘链接文件

**版本号自动生成规则**:
- 系统会自动为每个阶段（前期/中期/末期）的成果分配递增的版本号
- 版本号从1开始，同一阶段内按提交顺序递增
- 阶段版本标识格式：`{阶段类型}-v{版本号}`（如：前期-v1、中期-v2）

#### 3.4 更新成果
**接口**: `PUT /api/v1/studentproject/deliverables/{id}/`  
**描述**: 更新成果信息  
**权限**: 成果提交者  

#### 3.5 成果版本链
**接口**: `GET /api/v1/studentproject/deliverables/{id}/version-chain/`  
**描述**: 获取成果的版本链  
**权限**: 项目成员  

### 4. 评论系统接口

#### 4.1 获取评论
**接口**: `GET /api/v1/studentproject/deliverables/{deliverable_id}/comments/`  
**描述**: 获取成果的评论列表  
**权限**: 项目成员  

**查询参数**:
- `parent_id`: 父评论ID (获取回复)
- `page`: 页码
- `page_size`: 每页数量

#### 4.2 添加评论
**接口**: `POST /api/v1/studentproject/deliverables/{deliverable_id}/comments/`  
**描述**: 添加评论或回复  
**权限**: 项目成员  

**请求体**:
```json
{
    "content": "这个需求分析很详细，建议在用户体验部分再补充一些内容",
    "parent_comment_id": null  // 如果是回复则填写父评论ID
}
```

#### 4.3 更新评论
**接口**: `PUT /api/v1/studentproject/comments/{id}/`  
**描述**: 更新评论内容  
**权限**: 评论作者  

#### 4.4 删除评论
**接口**: `DELETE /api/v1/studentproject/comments/{id}/`  
**描述**: 删除评论  
**权限**: 评论作者或项目创建者  

### 5. 通知系统接口

#### 5.1 通知列表
**接口**: `GET /api/v1/studentproject/notifications/`  
**描述**: 获取用户通知列表  
**权限**: 认证用户  

**查询参数**:
- `is_read`: 是否已读 (true/false)
- `notification_type`: 通知类型
- `page`: 页码
- `page_size`: 每页数量

#### 5.2 标记已读
**接口**: `POST /api/v1/studentproject/notifications/{id}/mark-read/`  
**描述**: 标记通知为已读  
**权限**: 通知接收者  

#### 5.3 批量标记已读
**接口**: `POST /api/v1/studentproject/notifications/mark-all-read/`  
**描述**: 标记所有通知为已读  
**权限**: 认证用户  

#### 5.4 未读通知数量
**接口**: `GET /api/v1/studentproject/notifications/unread-count/`  
**描述**: 获取未读通知数量  
**权限**: 认证用户  

### 6. 统计分析接口

#### 6.1 项目统计
**接口**: `GET /api/v1/studentproject/statistics/projects/`  
**描述**: 获取项目统计信息  
**权限**: 认证用户  

**响应示例**:
```json
{
    "total_projects": 150,
    "active_projects": 45,
    "completed_projects": 80,
    "my_projects": 5,
    "my_participated_projects": 8,
    "status_distribution": {
        "planning": 15,
        "active": 45,
        "completed": 80,
        "paused": 8,
        "cancelled": 2
    }
}
```

#### 6.2 个人统计
**接口**: `GET /api/v1/studentproject/statistics/personal/`  
**描述**: 获取个人项目统计  
**权限**: 认证用户  

## 视图类设计

### 1. 项目管理视图

```python
class StudentProjectViewSet(viewsets.ModelViewSet):
    """学生项目视图集"""
    serializer_class = StudentProjectListSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['status', 'requirement', 'creator']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'updated_at', 'title']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return StudentProjectDetailSerializer
        elif self.action == 'create':
            return StudentProjectCreateSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """申请加入项目"""
        pass
```

### 2. 参与者管理视图

```python
class ProjectParticipantViewSet(viewsets.ModelViewSet):
    """项目参与者视图集"""
    serializer_class = ProjectParticipantSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def review(self, request, pk=None):
        """审核参与申请"""
        pass
```

### 3. 成果管理视图

```python
class ProjectDeliverableViewSet(viewsets.ModelViewSet):
    """项目成果视图集"""
    serializer_class = ProjectDeliverableListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProjectDeliverableDetailSerializer
        return self.serializer_class
    
    @action(detail=True, methods=['get'])
    def version_chain(self, request, pk=None):
        """获取版本链"""
        pass
```

### 4. 评论系统视图

```python
class ProjectCommentViewSet(viewsets.ModelViewSet):
    """项目评论视图集"""
    serializer_class = ProjectCommentSerializer
    permission_classes = [IsAuthenticated]
```

### 5. 通知系统视图

```python
class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
    """通知视图集"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记已读"""
        pass
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """批量标记已读"""
        pass
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """未读数量"""
        pass
```

### 6. 统计分析视图

```python
class StatisticsAPIView(APIView):
    """统计分析视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取统计信息"""
        pass
```

## URL 路由设计

```python
# studentproject/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'projects', views.StudentProjectViewSet, basename='studentproject')
router.register(r'participants', views.ProjectParticipantViewSet, basename='participant')
router.register(r'deliverables', views.ProjectDeliverableViewSet, basename='deliverable')
router.register(r'comments', views.ProjectCommentViewSet, basename='comment')
router.register(r'notifications', views.NotificationViewSet, basename='notification')

urlpatterns = [
    path('api/v1/studentproject/', include(router.urls)),
    path('api/v1/studentproject/statistics/', views.StatisticsAPIView.as_view(), name='statistics'),
]
```

## 权限控制

### 自定义权限类

```python
class IsProjectMember(BasePermission):
    """项目成员权限"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj
        
        # 检查是否为项目创建者或参与者
        return (project.creator.user == request.user or 
                project.participants.filter(student__user=request.user, 
                                           status__in=['approved', 'active']).exists())

class IsProjectCreator(BasePermission):
    """项目创建者权限"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'project'):
            project = obj.project
        else:
            project = obj
        
        return project.creator.user == request.user
```

## 特殊功能说明

### 1. 版本控制系统
- 自动生成阶段版本号 (前期v1, 前期v2, 中期v1...)
- 支持版本链追溯
- 里程碑版本标记

### 2. 通知系统
- 项目申请通知
- 成果提交通知
- 评论回复通知
- 项目状态变更通知

### 3. 权限管理
- 项目创建者：完全控制权限
- 项目参与者：查看和提交成果权限
- 普通用户：查看公开项目权限

### 4. 搜索和筛选
- 支持多条件组合筛选
- 全文搜索功能
- 智能排序算法

这个API设计涵盖了学生项目对接系统的所有核心功能，请审核并提出修改建议。