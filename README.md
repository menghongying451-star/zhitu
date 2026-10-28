# 知途 · 校园实践机会导航平台

基于智汇源码改造（已获张佳鑫老师同意），后端 Django，前端 Vue 3 + Vite。智能体用 Python 实现，代码在 `backend/agent/`，说明见 `backend/agent/README.md`。

```
zhitu/
├── backend/    Django 后端
└── frontend/   Vue 前端
```

## 本地启动（Mac）

### 1. 准备环境

```bash
brew install python@3.12 mysql redis node
brew services start mysql
brew services start redis
```

### 2. 后端

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements-zhitu.txt     # 不要用 requirements.txt，那份有 Windows 专用包

# 建一个新数据库（不要连智汇线上库）
mysql -u root -e "CREATE DATABASE zhitu DEFAULT CHARSET utf8mb4;"

cp .env.example .env    # 然后编辑 .env，见下方「必填配置」
python manage.py migrate
python manage.py loaddata tags          # 导入 194 个领域标签 + 708 个岗位标签
python manage.py seed_opportunities     # 导入种子机会（agent/fixtures/ 下的 json 和 csv）
python manage.py createsuperuser        # 管理后台账号
python manage.py runserver 0.0.0.0:8000
```

`.env` 必填配置：

```
DB_NAME=zhitu
DB_USER=root
DB_PASSWORD=你的MySQL密码
DB_HOST=127.0.0.1
REDIS_URL=redis://127.0.0.1:6379/1
AGENT_LLM_API_KEY=大模型Key（私下发，不要提交）
```

Milvus 向量库 v0 不用装，智能体会自动退回只用数据库字段回答。

自检：`python manage.py test agent`，7 个测试应全部通过。

### 3. 前端

```bash
cd frontend
cp .env.example .env.development   # 后端不在本机时，改成后端地址
npm install
npm run dev                         # 打开 http://localhost:5173
```

## 协作约定

- `.env`、API Key、数据库密码**不提交**（`.gitignore` 已排除）。
- 每人一个分支，每天合并一次到 `main`。
- 改了模型（models.py）后执行 `python manage.py makemigrations`，并把生成的迁移文件一起提交。

## 常见问题

- **建账号或登录时报 `No module named 'argon2'`**：执行 `pip install argon2-cffi`（已写进 requirements-zhitu.txt，重新执行 pip install 也可以）。
- **`npm run dev` 报 `localStorage.getItem is not a function`**：Node 25 的已知问题。要么改用 Node 22 LTS，要么用这条命令启动：`NODE_OPTIONS=--no-experimental-webstorage npm run dev`。
- **`npm install` 时 husky 报 `.git can't be found`**：已修复，拉取最新的 main 就好。
- 日志里的 `Milvus ERROR` 可以忽略，v0 没装向量库，智能体会自动改用数据库字段。
