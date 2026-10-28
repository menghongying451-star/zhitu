# Django 智慧项目 (Project Zhihui)

一个基于Django的智慧管理平台，集成了用户管理、组织管理、项目管理、PDF处理和AI功能的综合性Web应用。

## 🚀 项目特性

- **用户认证系统**: JWT认证、邮箱验证、密码安全
- **组织管理**: 企业、大学、其他组织的注册和管理
- **项目管理**: 需求发布、资源管理、文件处理
- **PDF处理**: 文档解析、向量化存储
- **AI集成**: 基于Transformers的智能功能
- **实时通信**: WebSocket支持
- **异步任务**: Celery任务队列
- **向量数据库**: Milvus集成

## 📋 系统要求

- Python 3.8+
- MySQL 8.0+
- Redis 6.0+
- Milvus 2.4+ (可选，用于向量搜索)

## 🛠️ 快速开始

### 1. 克隆项目

```bash
git clone <repository-url>
cd Project_Zhihui
```

### 2. 创建虚拟环境

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. 安装依赖

```bash
# 安装pip-tools (推荐)
pip install pip-tools

# 编译依赖文件
pip-compile requirements.in

# 安装依赖
pip-sync requirements.txt

# 或者直接安装 (不推荐用于生产环境)
pip install -r requirements.in
或：
pip install -r requirements.txt
```

### 4. 环境配置

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，配置以下信息:
# - 数据库连接信息
# - Redis连接信息
# - 邮件服务配置
# - 密钥设置
```

### 5. 数据库设置

```bash
# 清理旧的迁移文件
python cleanup_migrations.py --cleanup

# 创建数据库迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate

# 创建超级用户
python manage.py createsuperuser
```

### 6. 启动服务

```bash
# 开发服务器
python manage.py runserver

# 或使用Gunicorn (生产环境)
gunicorn Project_Zhihui.wsgi:application --bind 0.0.0.0:8000
```

## 🔧 开发环境配置

### 启动Redis (必需)

```bash
# Windows启动（管理员权限）
redis-server.exe redis.windows.conf
redis-cli.exe ping
```

### 启动Celery (异步任务)

```bash
# 启动Celery Worker
celery -A Project_Zhihui worker --loglevel=info

# 启动Celery Beat (定时任务)
celery -A Project_Zhihui beat --loglevel=info
```


## 📁 项目结构

```
Project_Zhihui/
├── Project_Zhihui/          # Django项目配置
├── authentication/          # 用户认证模块
├── user/                   # 用户管理模块
├── organization/           # 组织管理模块
├── project/                # 项目管理模块
├── pdf_processing/         # PDF处理模块
├── read_search/            # 搜索功能模块
├── tag_db_writer/          # 标签数据库模块
├── templates/              # HTML模板
├── static/                 # 静态文件
├── media/                  # 媒体文件
├── logs/                   # 日志文件
├── requirements.in         # 依赖配置文件
├── manage.py              # Django管理脚本
└── README.md              # 项目说明
```

## 🔑 环境变量配置

在 `.env` 文件中配置以下变量：

```env
# Django设置
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# 数据库配置
DB_NAME=project_zhihui
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=3306

# Redis配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# 邮件配置
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Milvus配置 (可选)
MILVUS_HOST=localhost
MILVUS_PORT=19530
```


## 📚 API文档

启动服务后，访问以下地址查看API文档：

- Swagger UI: `http://localhost:8000/swagger/`
- ReDoc: `http://localhost:8000/redoc/`
- Django Admin: `http://localhost:8000/admin/`

## 🚀 部署指南

### 生产环境部署

1. **环境准备**
   ```bash
   # 设置生产环境变量
   export DEBUG=False
   export ALLOWED_HOSTS=your-domain.com
   ```

2. **静态文件收集**
   ```bash
   python manage.py collectstatic --noinput
   ```

3. **数据库迁移**
   ```bash
   python manage.py migrate
   ```

4. **启动服务**
   ```bash
   # 使用Gunicorn
   gunicorn Project_Zhihui.wsgi:application --bind 0.0.0.0:8000 --workers 4
   
   # 使用Daphne (支持WebSocket)
   daphne -b 0.0.0.0 -p 8000 Project_Zhihui.asgi:application
   ```


## 🔄 迁移文件管理

本项目使用特殊的迁移文件管理策略：

- 只保留 `__init__.py` 和 `0001_initial.py` 文件
- 其他迁移文件不提交到版本控制
- 每个开发者在本地生成自己的迁移文件

详细说明请参考：[Django迁移文件管理指南](DJANGO_MIGRATIONS_GUIDE.md)

## 🛠️ 开发工具

### 代码质量检查

```bash
# 安全检查
bandit -r .

# 代码格式化 (需要安装black)
black .

# 导入排序 (需要安装isort)
isort .
```

### 数据库管理

```bash
# 查看迁移状态
python manage.py showmigrations

# 重置迁移 (开发环境)
python manage.py migrate app_name zero

# 生成测试数据
python generate_requirement_data.py
python generate_tag_data.py
```

## 📖 开发指南

### 添加新功能

1. 创建新的Django应用
2. 定义模型和序列化器
3. 编写视图和URL配置
4. 添加测试用例
5. 更新API文档

### 代码规范

- 遵循PEP 8代码风格
- 使用有意义的变量和函数名
- 添加适当的注释和文档字符串
- 编写单元测试

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 故障排除

### 常见问题

1. **数据库连接错误**
   - 检查MySQL服务是否启动
   - 验证数据库配置信息
   - 确保数据库用户有足够权限

2. **Redis连接错误**
   - 检查Redis服务是否启动
   - 验证Redis配置信息

3. **迁移错误**
   - 删除迁移文件重新生成
   - 检查模型定义是否正确

4. **依赖安装错误**
   - 更新pip: `pip install --upgrade pip`
   - 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/`

### 获取帮助

- 查看项目文档
- 提交Issue
- 联系开发团队

## 📞 联系信息

- 项目维护者: [Your Name]
- 邮箱: [your-email@example.com]
- 项目地址: [repository-url]

---

**注意**: 请确保在生产环境中正确配置所有安全设置，包括SECRET_KEY、数据库密码、邮件配置等敏感信息。




          
## AllowedHostsOriginValidator 工作原理

`AllowedHostsOriginValidator` 是 Django Channels 提供的一个安全中间件，它的作用是验证 WebSocket 连接的来源（Origin）是否在允许的主机列表中。

### 为什么会导致连接被拒绝？

1. **Origin 验证机制**
   - WebSocket 连接会携带 `Origin` 头部，表明请求的来源
   - `AllowedHostsOriginValidator` 会检查这个 Origin 是否在 Django 的 `ALLOWED_HOSTS` 设置中
   - 如果 Origin 不在允许列表中，连接会被直接拒绝，不会到达后续的 JWT 中间件

2. **常见的拒绝场景**
   - 使用 Apifox 等测试工具时，Origin 可能是 `null` 或者工具的默认域名
   - 本地开发时使用 `localhost`、`127.0.0.1` 等，但 `ALLOWED_HOSTS` 配置不匹配
   - 跨域请求时，Origin 域名不在允许列表中

### 生产环境的正确配置

如果需要在生产环境中使用 `AllowedHostsOriginValidator`，应该这样配置：

#### 1. 更新 ASGI 配置

```python:d:/Project_Zhihui/Project_Zhihui/asgi.py
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from authentication.jwt_middleware import JWTAuthMiddlewareStack
import studentproject.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project_Zhihui.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(
                studentproject.routing.websocket_urlpatterns
            )
        )
    ),
})
```

#### 2. 配置 ALLOWED_HOSTS

在 `settings.py` 中正确配置允许的主机：

```python:d:/Project_Zhihui/Project_Zhihui/settings.py
# 开发环境
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    # 添加你的域名
]

# 生产环境
ALLOWED_HOSTS = [
    'yourdomain.com',
    'www.yourdomain.com',
    # 其他允许的域名
]
```

#### 3. 处理测试工具的 Origin

对于 Apifox 等测试工具，可以：

1. **在测试环境中临时禁用**（当前做法）
2. **配置测试专用的 ALLOWED_HOSTS**
3. **在 Apifox 中设置正确的 Origin 头部**

#### 4. 环境分离配置

```python:d:/Project_Zhihui/Project_Zhihui/settings.py
import os

# 根据环境变量决定是否启用 Origin 验证
ENABLE_ORIGIN_VALIDATION = os.getenv('ENABLE_ORIGIN_VALIDATION', 'True').lower() == 'true'

# 在 asgi.py 中使用
if ENABLE_ORIGIN_VALIDATION:
    websocket_app = AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(studentproject.routing.websocket_urlpatterns)
        )
    )
else:
    websocket_app = JWTAuthMiddlewareStack(
        URLRouter(studentproject.routing.websocket_urlpatterns)
    )
```

### 安全建议

1. **生产环境必须启用** - `AllowedHostsOriginValidator` 是重要的安全措施
2. **精确配置域名** - 只允许真正需要的域名
3. **避免使用通配符** - 不要使用 `*` 作为 ALLOWED_HOSTS
4. **定期审查配置** - 确保配置与实际需求匹配

现在你可以根据实际需求选择合适的配置方案。在开发阶段可以暂时禁用，但在生产环境中务必正确配置并启用这个安全中间件。

daphne -b 127.0.0.1 -p 8000 Project_Zhihui.asgi:application        