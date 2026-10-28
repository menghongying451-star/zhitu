# 通知功能数据同步指南

本指南将帮助您将本地开发环境中的通知类型和模板数据同步到服务器上的数据库。

## 概述

通知功能包含以下数据需要同步：
- **通知类型 (NotificationType)**: 定义了各种通知的基本信息
- **通知模板 (NotificationTemplate)**: 定义了通知的标题和内容模板

## 前置条件

1. 确保服务器上已部署最新的代码
2. 确保服务器数据库已运行迁移：`python manage.py migrate`
3. 确保本地环境有完整的通知数据

## 同步步骤

### 步骤1：在本地导出数据

在本地开发环境中运行以下命令导出通知数据：

```bash
# 导出为自定义JSON格式（推荐）
python manage.py export_notification_data --output-dir notification_sync

# 或导出为Django fixture格式
python manage.py export_notification_data --output-dir notification_sync --format fixture
```

导出完成后，会在 `notification_sync` 目录中生成以下文件：
- `notification_types_YYYYMMDD_HHMMSS.json` - 通知类型数据
- `notification_templates_YYYYMMDD_HHMMSS.json` - 通知模板数据
- `notification_data_complete_YYYYMMDD_HHMMSS.json` - 完整数据文件（推荐使用）
- `README.md` - 导入说明

### 步骤2：将数据文件传输到服务器

将导出的文件传输到服务器上，可以使用以下方法：

```bash
# 使用scp传输（示例）
scp -r notification_sync/ user@server:/path/to/project/

# 或使用rsync
rsync -av notification_sync/ user@server:/path/to/project/notification_sync/
```

### 步骤3：在服务器上导入数据

登录到服务器，进入项目目录，运行导入命令：

#### 方法1：导入完整数据文件（推荐）

```bash
# 先预览导入内容（试运行）
python manage.py import_notification_data --input-file notification_sync/notification_data_complete_YYYYMMDD_HHMMSS.json --dry-run

# 确认无误后执行实际导入
python manage.py import_notification_data --input-file notification_sync/notification_data_complete_YYYYMMDD_HHMMSS.json
```

#### 方法2：从目录自动导入最新文件

```bash
# 自动查找并导入目录中最新的数据文件
python manage.py import_notification_data --input-dir notification_sync
```

#### 方法3：分别指定文件导入

```bash
# 分别指定类型和模板文件
python manage.py import_notification_data \
  --types-file notification_sync/notification_types_YYYYMMDD_HHMMSS.json \
  --templates-file notification_sync/notification_templates_YYYYMMDD_HHMMSS.json
```

#### 方法4：使用Django fixture格式导入

```bash
# 如果导出时使用了fixture格式
python manage.py import_notification_data \
  --input-dir notification_sync \
  --format fixture

# 或直接使用Django的loaddata命令
python manage.py loaddata notification_sync/notification_types_YYYYMMDD_HHMMSS.json
python manage.py loaddata notification_sync/notification_templates_YYYYMMDD_HHMMSS.json
```

## 高级选项

### 强制更新已存在的数据

如果服务器上已有部分数据，但您想要强制更新：

```bash
python manage.py import_notification_data \
  --input-file notification_sync/notification_data_complete_YYYYMMDD_HHMMSS.json \
  --force-update
```

### 试运行模式

在实际导入前，建议先使用试运行模式预览导入内容：

```bash
python manage.py import_notification_data \
  --input-file notification_sync/notification_data_complete_YYYYMMDD_HHMMSS.json \
  --dry-run
```

## 验证同步结果

导入完成后，可以通过以下方式验证数据是否正确同步：

### 1. 检查数据库记录数量

```bash
# 进入Django shell
python manage.py shell
```

```python
from notification.models import NotificationType, NotificationTemplate

# 检查通知类型数量
print(f"通知类型数量: {NotificationType.objects.count()}")

# 检查通知模板数量
print(f"通知模板数量: {NotificationTemplate.objects.count()}")

# 列出所有通知类型
for nt in NotificationType.objects.all():
    print(f"- {nt.code}: {nt.name} ({nt.category})")
```

### 2. 检查Admin界面

访问Django Admin界面，检查以下模块：
- 通知系统 → 02-通知类型
- 通知系统 → 03-通知模板

### 3. 测试通知功能

可以通过系统广播功能测试通知是否正常工作。

## 常见问题

### Q: 导入时提示"通知类型不存在"错误

**A:** 这通常是因为通知模板引用的通知类型在数据库中不存在。解决方法：
1. 确保先导入通知类型，再导入通知模板
2. 检查导出的数据是否完整
3. 使用 `--force-update` 参数强制更新

### Q: 导入后数据没有更新

**A:** 默认情况下，导入命令会跳过已存在的数据。如果需要更新已存在的数据，请使用 `--force-update` 参数。

### Q: 如何回滚导入的数据

**A:** 建议在导入前备份数据库。如果需要回滚：
1. 恢复数据库备份
2. 或手动删除导入的数据（不推荐）

### Q: 导入时出现编码错误

**A:** 确保文件使用UTF-8编码保存，特别是包含中文内容的文件。

## 自动化脚本示例

以下是一个完整的同步脚本示例：

```bash
#!/bin/bash
# sync_notification_data.sh

set -e  # 遇到错误时退出

echo "=== 通知数据同步脚本 ==="

# 配置
LOCAL_PROJECT_DIR="/path/to/local/project"
SERVER_USER="your_user"
SERVER_HOST="your_server"
SERVER_PROJECT_DIR="/path/to/server/project"
EXPORT_DIR="notification_sync"

# 步骤1：本地导出数据
echo "1. 在本地导出通知数据..."
cd $LOCAL_PROJECT_DIR
python manage.py export_notification_data --output-dir $EXPORT_DIR

# 步骤2：传输到服务器
echo "2. 传输数据到服务器..."
rsync -av $EXPORT_DIR/ $SERVER_USER@$SERVER_HOST:$SERVER_PROJECT_DIR/$EXPORT_DIR/

# 步骤3：在服务器上导入
echo "3. 在服务器上导入数据..."
ssh $SERVER_USER@$SERVER_HOST "cd $SERVER_PROJECT_DIR && python manage.py import_notification_data --input-dir $EXPORT_DIR --dry-run"

read -p "预览结果正确吗？继续导入？(y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    ssh $SERVER_USER@$SERVER_HOST "cd $SERVER_PROJECT_DIR && python manage.py import_notification_data --input-dir $EXPORT_DIR"
    echo "✅ 同步完成！"
else
    echo "❌ 同步已取消"
fi
```

## 注意事项

1. **备份重要性**: 在生产环境导入数据前，务必备份数据库
2. **权限检查**: 确保运行命令的用户有足够的数据库权限
3. **数据一致性**: 导入前确保服务器代码版本与本地一致
4. **测试验证**: 导入后务必测试通知功能是否正常工作
5. **日志监控**: 关注导入过程中的错误和警告信息

## 相关文件

- `notification/management/commands/export_notification_data.py` - 数据导出命令
- `notification/management/commands/import_notification_data.py` - 数据导入命令
- `notification/management/commands/init_notification_templates.py` - 初始化通知模板命令
- `notification/models.py` - 通知相关模型定义
- `notification/templates.py` - 通知模板定义

---

如有问题，请查看命令的帮助信息：
```bash
python manage.py export_notification_data --help
python manage.py import_notification_data --help
```