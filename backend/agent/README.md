# agent —— Python 版智能体（替代 Dify）

原来的「文识 / 知途 / 填宝」三个 Dify 工作流，现在都改成了 Django app 里的 Python 代码。不再需要部署 Dify，也不再需要 Dify 的数据库插件和 HTTP 节点。

## 目录

```
agent/
├── conf.py          配置（模型地址、Key、上传限制等）
├── llm.py           大模型调用（OpenAI 兼容协议，支持流式、JSON 输出，自动去掉 <think>）
├── memory.py        会话记忆（存 Redis，替代 Dify 的 conversation variables）
├── documents.py     文档解析 pdf/docx/txt（替代「文档提取器」节点）
├── taxonomy.py      tag_1 / tag_2 标签读取与两段式匹配、标签热度统计
├── retrieval.py     需求信息 + Milvus 向量检索、学生→候选需求初筛
├── base.py          智能体基类、回答规范、语气设定
├── agents/
│   ├── wenshi.py    文识：项目问答
│   ├── zhitu.py     知途：方向测定 + 项目推荐
│   └── tianbao.py   填宝：企业对话式发布需求
├── views.py / urls.py   HTTP 接口（SSE 流式）
└── tests.py         用假模型跑通三个智能体的完整流程
```

## 配置

在 `.env` 中加入（完整示例见 `.env.example`）：

```
AGENT_LLM_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
AGENT_LLM_API_KEY=sk-xxxx
AGENT_LLM_MODEL=qwen-plus
```

任何 OpenAI 兼容接口都能用：通义千问、DeepSeek、硅基流动、本地 Ollama / vLLM。换模型只改 `.env`，代码不用动。

`AGENT_PUBLISH_STATUS`：填宝发布后的需求状态，默认 `under_review`，和表单发布一样先进入审核。旧版 Dify 直接写 `in_progress`，想保持旧行为就改成 `in_progress`。

依赖：`openai`（已在 requirements.txt 中），PyMuPDF、python-docx 项目原本就有。

## 接口

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/agent/` | 智能体列表 |
| GET | `/api/v1/agent/<name>/` | 开场白、推荐问题、是否可上传 |
| POST | `/api/v1/agent/<name>/chat/` | 对话，默认 SSE；加 `?stream=0` 返回普通 JSON |

`name`：`wenshi` / `zhitu` / `tianbao`。需要登录（JWT），学生、企业的身份都从 token 中取。

POST 参数（JSON 或 multipart）：`query`、`conversation_id`（首轮不传）、`inputs`（如 `{"pid": 12, "tone": "严谨"}`）、`file`。

SSE 事件：`meta`（返回 conversation_id）→ 若干 `delta`（逐字文本）→ 可能有 `action` → `done`。

Postman 调试示例：

```
POST /api/v1/agent/wenshi/chat/?stream=0
Authorization: Bearer <token>
{"query": "这个项目需要什么技能？", "inputs": {"pid": 12}}
```

## 与 Dify 节点的对应关系

### 文识（原 `文识.yml`）
| Dify 节点 | Python |
|---|---|
| HTTP 请求 read-search-v2 | `retrieval.vector_search(query, [pid])`，同时从数据库读需求的完整字段 |
| 角色生成器（LLM） | `base.tone_instruction()`，直接写进 system prompt，省掉一次模型调用 |
| 回答整理数据（LLM） | `WenShiAgent.run()` 流式回答，并带上多轮历史 |

### 知途（原 `知途.yml`）
| Dify 节点 / 分支 | Python |
|---|---|
| count==0 → 包含“哪些” | `_list_categories()`，领域列表从 tag_1 表读取 |
| 包含“介绍” | `_introduce()` |
| 其他输入：LLM3(tag1) → LLM(tag2) → LLM12 解释 | `_profile()` → `taxonomy.match_tags(mode="student")` 两段式匹配 → 流式解释 |
| 包含“确认”：LLM4/11/13 提取 ID → general-match → UPDATE frequency | `_confirm()`：直接用校验过的 ID 写 tag1/tag2_stu_match、更新热度、计算候选项目 |
| count>0 → “我对XX感兴趣”：SQL 查 tag_match → LLM 提 pid → INSERT favorite | `_favorite()`：在候选项目里做标题匹配，用 ORM 写收藏 |
| count>0 → 其他：read-search → 回答 | `_recommend()` |

### 填宝（原 `填宝.yml`）
| Dify 节点 | Python |
|---|---|
| 文档提取器 | `documents.read_upload()` |
| LLM6 抽取 13 个字段（structured output） | `_build_draft()` 用 `chat_json` 抽取，代码里统一做格式化 |
| LLM2/LLM3/LLM9/LLM10 领域、岗位匹配 | `taxonomy.match_tags(mode="requirement")` |
| 用户补充修改 → 整条流程重跑 | `_revise()`：只在当前草稿上改用户要求的字段，并告诉用户改了什么 |
| “确认” → SQL INSERT → 按标题查 pid → LLM7 提数字 → process-pdf → general-match ×2 | `_publish()`：ORM 建需求（事务）→ 设置标签 → 附件入库 → 文档向量化 |

## 顺手修掉的问题

1. **SQL 注入 / 单引号报错**：旧版 SQL 是字符串拼接的，标题或描述里有 `'` 就会失败，也能被注入。现在全部改成 ORM。
2. **身份可伪造**：旧版的 sid、organized_id、publish_people_id 通过 URL 参数传（gzip+base64 只是编码，不是加密），现在改从登录 token 取。
3. **初筛表没人写**：知途依赖 `tag_match` 表做初筛，但仓库里没有任何代码写入这张表。现在按标签重合度直接计算候选项目，同时回写 `tag_match`，原来的 `/api/v1/search/read-search/` 也能继续用。
4. **按标题反查 pid**：同名需求会查错，现在直接用新建记录的 id。
5. **接口地址对不上**：旧工作流调用的是 `/api/v1/pdf/process-pdf/`，但当前后端代码里的路由是 `upload-pdf/`，按这份代码部署的话文档进不了向量库。现在发布时直接在进程内完成向量化，不再走 HTTP。
6. **Milvus 挂掉时整轮报错**：现在退回只用数据库字段回答。
7. **提示词塞了 695 行岗位表**：每次调用都要上万 token。现在改成两段式匹配（先选大类，再选细分），标签直接从数据库读，新增标签不用改 prompt。

## 测试

```bash
python manage.py test agent
```

测试用假模型跑完三条完整流程：上传→修改→确认发布；方向测定→确认→推荐→归档；项目问答；SSE；权限。不需要真实 Key，也不需要 Milvus。
