# 虚拟文件系统 API 接口文档

## 概述

虚拟文件系统提供了完整的文件管理功能，支持需求文件、资源文件和项目成果文件的统一管理。所有接口都支持三种资源类型的文件操作。

## 权限说明

### 需求文件 (requirement_id)
- **读权限**: 所有认证用户
- **写权限**: 需求发布者或所属组织的管理员/所有者

### 资源文件 (resource_id)
- **读权限**: 所有认证用户
- **写权限**: 资源创建者或所属组织的管理员/所有者

### 成果文件 (deliverable_id)
- **读权限**: 项目的已批准参与者（负责人或成员）
- **写权限**: 项目的已批准参与者（负责人或成员）

## 接口列表

### 1. 文件列表获取

**接口**: `GET /api/virtual-files/`

**描述**: 获取指定资源的文件列表，支持路径过滤、文件类型过滤和搜索功能。

**查询参数**:
- `requirement_id` (可选): 需求ID
- `resource_id` (可选): 资源ID  
- `deliverable_id` (可选): 成果ID
- `path` (可选): 虚拟路径过滤，默认为根目录 `/`
- `file_type` (可选): 文件类型过滤 (`file` 或 `folder`)
- `search` (可选): 文件名搜索关键词

**注意**: 必须且只能指定 `requirement_id`、`resource_id` 或 `deliverable_id` 中的一个。

**响应示例**:
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "count": 10,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 1,
        "name": "document.pdf",
        "path": "/documents/document.pdf",
        "parent_path": "/documents",
        "is_folder": false,
        "size": 1024000,
        "file_type": "pdf",
        "url": "http://example.com/media/uploads/files/deliverable/document.pdf",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
      }
    ]
  }
}
```

### 2. 文件上传

**接口**: `POST /api/virtual-files/upload_file/`

**描述**: 上传文件到指定资源的虚拟文件系统中。

**查询参数**:
- `requirement_id` (可选): 需求ID
- `resource_id` (可选): 资源ID
- `deliverable_id` (可选): 成果ID

**请求体** (multipart/form-data):
- `files`: 要上传的文件列表
- `parent_path` (可选): 上传到的虚拟路径，默认为根目录 `/`

**响应示例**:
```json
{
  "status": "success",
  "code": 201,
  "message": "文件上传成功",
  "data": {
    "uploaded_files": [
      {
        "id": 1,
        "name": "document.pdf",
        "path": "/document.pdf",
        "size": 1024000,
        "url": "http://example.com/media/uploads/files/deliverable/document.pdf"
      }
    ]
  }
}
```

### 3. 创建文件夹

**接口**: `POST /api/virtual-files/create_folder/`

**描述**: 在指定资源的虚拟文件系统中创建文件夹。

**查询参数**:
- `requirement_id` (可选): 需求ID
- `resource_id` (可选): 资源ID
- `deliverable_id` (可选): 成果ID

**请求体**:
```json
{
  "name": "新文件夹",
  "parent_path": "/documents"
}
```

**响应示例**:
```json
{
  "status": "success",
  "code": 201,
  "message": "文件夹创建成功",
  "data": {
    "id": 2,
    "name": "新文件夹",
    "path": "/documents/新文件夹",
    "is_folder": true,
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

### 4. 批量删除文件

**接口**: `DELETE /api/virtual-files/file_delete/`

**描述**: 批量删除指定资源的文件或文件夹。

**查询参数**:
- `requirement_id` (可选): 需求ID
- `resource_id` (可选): 资源ID
- `deliverable_id` (可选): 成果ID

**请求体**:
```json
{
  "file_ids": [1, 2, 3]
}
```

**响应示例**:
```json
{
  "status": "success",
  "code": 200,
  "message": "文件删除成功",
  "data": {
    "deleted_count": 3,
    "deleted_files": [
      {"id": 1, "name": "file1.txt"},
      {"id": 2, "name": "file2.pdf"},
      {"id": 3, "name": "folder1"}
    ]
  }
}
```

### 5. 重命名文件/文件夹

**接口**: `PATCH /api/virtual-files/{file_id}/rename/`

**描述**: 重命名指定的文件或文件夹。

**查询参数**:
- `requirement_id` (可选): 需求ID
- `resource_id` (可选): 资源ID
- `deliverable_id` (可选): 成果ID

**请求体**:
```json
{
  "name": "新文件名.pdf"
}
```

**响应示例**:
```json
{
  "status": "success",
  "code": 200,
  "message": "重命名成功",
  "data": {
    "id": 1,
    "name": "新文件名.pdf",
    "path": "/documents/新文件名.pdf",
    "updated_at": "2024-01-15T10:35:00Z"
  }
}
```

### 6. 移动文件/文件夹

**接口**: `POST /api/virtual-files/{file_id}/move/`

**描述**: 移动文件或文件夹到新的路径。

**查询参数**:
- `requirement_id` (可选): 需求ID
- `resource_id` (可选): 资源ID
- `deliverable_id` (可选): 成果ID

**请求体**:
```json
{
  "parent_path": "/新目录"
}
```

**响应示例**:
```json
{
  "status": "success",
  "code": 200,
  "message": "移动成功",
  "data": {
    "id": 1,
    "name": "document.pdf",
    "path": "/新目录/document.pdf",
    "parent_path": "/新目录",
    "updated_at": "2024-01-15T10:40:00Z"
  }
}
```

### 7. 获取文件树结构

**接口**: `GET /api/virtual-files/tree_structure/`

**描述**: 获取指定资源的完整文件树结构。

**查询参数**:
- `requirement_id` (可选): 需求ID
- `resource_id` (可选): 资源ID
- `deliverable_id` (可选): 成果ID

**响应示例**:
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "name": "root",
    "path": "/",
    "is_folder": true,
    "children": [
      {
        "id": 1,
        "name": "documents",
        "path": "/documents",
        "is_folder": true,
        "children": [
          {
            "id": 2,
            "name": "report.pdf",
            "path": "/documents/report.pdf",
            "is_folder": false,
            "size": 2048000,
            "url": "http://example.com/media/uploads/files/deliverable/report.pdf"
          }
        ]
      }
    ]
  }
}
```

### 8. 获取面包屑导航

**接口**: `GET /api/virtual-files/breadcrumb/`

**描述**: 获取指定路径的面包屑导航信息。

**查询参数**:
- `requirement_id` (可选): 需求ID
- `resource_id` (可选): 资源ID
- `deliverable_id` (可选): 成果ID
- `path` (可选): 当前路径，默认为 `/`

**响应示例**:
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": [
    {"name": "根目录", "path": "/"},
    {"name": "documents", "path": "/documents"},
    {"name": "reports", "path": "/documents/reports"}
  ]
}
```

### 9. 获取文件下载链接

**接口**: `GET /api/virtual-files/{file_id}/download_url/`

**描述**: 获取文件的下载链接。

**响应示例**:
```json
{
  "status": "success",
  "code": 200,
  "message": "操作成功",
  "data": {
    "download_url": "http://example.com/media/uploads/files/deliverable/document.pdf",
    "filename": "document.pdf",
    "size": 1024000,
    "expires_at": "2024-01-15T11:30:00Z"
  }
}
```

## 错误响应格式

所有接口在出现错误时都会返回统一的错误响应格式：

```json
{
  "status": "error",
  "code": 400,
  "message": "错误描述",
  "data": {},
  "errors": {
    "field_name": ["具体错误信息"]
  }
}
```

## 常见错误码

- `400`: 请求参数错误
- `401`: 未认证
- `403`: 权限不足
- `404`: 资源不存在
- `500`: 服务器内部错误

## 使用示例

### 成果文件管理示例

```javascript
// 1. 获取项目成果的文件列表
fetch('/api/virtual-files/?deliverable_id=123')
  .then(response => response.json())
  .then(data => console.log(data));

// 2. 上传文件到成果
const formData = new FormData();
formData.append('files', fileInput.files[0]);
formData.append('parent_path', '/documents');

fetch('/api/virtual-files/upload_file/?deliverable_id=123', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(data => console.log(data));

// 3. 创建文件夹
fetch('/api/virtual-files/create_folder/?deliverable_id=123', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: '设计文档',
    parent_path: '/'
  })
})
.then(response => response.json())
.then(data => console.log(data));
```

## 注意事项

1. 所有接口都需要用户认证，请在请求头中包含有效的认证信息。
2. 文件上传支持多文件同时上传。
3. 虚拟路径以 `/` 开头，表示根目录。
4. 删除文件夹时会递归删除其中的所有文件和子文件夹。
5. 移动和重命名操作会自动更新相关子文件的路径信息。
6. 成果文件的访问权限基于项目参与者身份，确保只有项目成员能够访问。