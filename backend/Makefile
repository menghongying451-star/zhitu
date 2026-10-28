# Django 智慧项目 Makefile
# 简化常用开发命令

.PHONY: help install dev test clean migrate runserver celery redis docker

# 默认目标
help:
	@echo "Django 智慧项目 - 可用命令:"
	@echo ""
	@echo "  install     - 安装项目依赖"
	@echo "  dev         - 设置开发环境"
	@echo "  test        - 运行测试"
	@echo "  migrate     - 运行数据库迁移"
	@echo "  runserver   - 启动开发服务器"
	@echo "  celery      - 启动Celery worker"
	@echo "  redis       - 启动Redis (Docker)"
	@echo "  clean       - 清理临时文件"
	@echo "  format      - 格式化代码"
	@echo "  lint        - 代码质量检查"
	@echo "  docker      - 构建Docker镜像"
	@echo ""

# 安装依赖
install:
	@echo "安装项目依赖..."
	pip install pip-tools
	pip-compile requirements.in
	pip-sync requirements.txt

# 设置开发环境
dev: install
	@echo "设置开发环境..."
	@if not exist .env (copy .env.example .env)
	python manage.py makemigrations
	python manage.py migrate
	@echo "开发环境设置完成！"
	@echo "请编辑 .env 文件配置数据库和其他设置"

# 运行测试
test:
	@echo "运行测试..."
	pytest --cov=. --cov-report=html --cov-report=term

# 数据库迁移
migrate:
	@echo "运行数据库迁移..."
	python manage.py makemigrations
	python manage.py migrate

# 启动开发服务器
runserver:
	@echo "启动开发服务器..."
	python manage.py runserver

# 启动Celery worker
celery:
	@echo "启动Celery worker..."
	celery -A Project_Zhihui worker --loglevel=info

# 启动Redis (Docker)
redis:
	@echo "启动Redis容器..."
	docker run -d -p 6379:6379 --name redis-zhihui redis:latest

# 清理临时文件
clean:
	@echo "清理临时文件..."
	@if exist __pycache__ rmdir /s /q __pycache__
	@for /d /r . %%d in (__pycache__) do @if exist "%%d" rmdir /s /q "%%d"
	@if exist .pytest_cache rmdir /s /q .pytest_cache
	@if exist htmlcov rmdir /s /q htmlcov
	@if exist .coverage del .coverage
	@del /s *.pyc 2>nul || echo "没有找到.pyc文件"

# 代码格式化
format:
	@echo "格式化代码..."
	black .
	isort .

# 代码质量检查
lint:
	@echo "代码质量检查..."
	bandit -r . -f json -o bandit-report.json || echo "安全检查完成"
	flake8 . || echo "代码风格检查完成"

# 构建Docker镜像
docker:
	@echo "构建Docker镜像..."
	docker build -t project-zhihui:latest .

# 生成requirements.txt
compile:
	@echo "编译依赖文件..."
	pip-compile requirements.in

# 更新依赖
upgrade:
	@echo "更新依赖..."
	pip-compile --upgrade requirements.in
	pip-sync requirements.txt

# 创建超级用户
superuser:
	@echo "创建超级用户..."
	python manage.py createsuperuser

# 收集静态文件
collectstatic:
	@echo "收集静态文件..."
	python manage.py collectstatic --noinput

# 生成测试数据
testdata:
	@echo "生成测试数据..."
	python generate_requirement_data.py
	python generate_tag_data.py

# 检查项目状态
check:
	@echo "检查项目状态..."
	python manage.py check
	python manage.py check --deploy

# 显示迁移状态
showmigrations:
	@echo "显示迁移状态..."
	python manage.py showmigrations

# 启动所有服务 (需要多个终端)
services:
	@echo "请在不同终端中运行以下命令:"
	@echo "1. make redis"
	@echo "2. make celery"
	@echo "3. make runserver"

# 完整设置 (新项目)
setup: dev superuser testdata
	@echo "项目设置完成！"
	@echo "运行 'make runserver' 启动开发服务器"

# 生产环境部署准备
deploy-prep:
	@echo "准备生产环境部署..."
	python manage.py check --deploy
	python manage.py collectstatic --noinput
	python manage.py migrate

# 备份数据库 (需要配置)
backup:
	@echo "备份数据库..."
	python manage.py dumpdata --natural-foreign --natural-primary > backup.json

# 恢复数据库 (需要配置)
restore:
	@echo "恢复数据库..."
	python manage.py loaddata backup.json