# WisdomLink - 智汇

[![Vue](https://img.shields.io/badge/Vue-3.5.17-4fc08d.svg)](https://vuejs.org/) [![Pinia](https://img.shields.io/badge/Pinia-3.0.3-ffd700.svg)](https://pinia.vuejs.org/) [![Element Plus](https://img.shields.io/badge/Element%20Plus-2.10.4-409eff.svg)](https://element-plus.org/)

> 基于大模型的产教融合平台
> 通过大模型与知识库驱动的智能问答系统实现项目与学生的精准匹配和个性化学习路径引导

## 项目概述

本系统是一个面向企业、社区和学生的产教融合平台，旨在通过大模型技术打破产教融合中的信息壁垒，构建 "创中学"" 干中学 ""感中学" 的实践教育生态。核心功能包括：

- 多模态融合供需对接：支持企业发布资源与需求信息，自动生成资源画像和需求画像，同时为学生生成兴趣与能力画像
- 智能匹配机制：通过多维度算法实现企业需求与学生能力的精准匹配，辅助组建跨学科团队
- 大模型智慧问答：基于产业知识库提供产业需求分析、技术可行性评估和问题解决方案
- 个性化学习引导：根据学生能力短板和项目需求，生成定制化学习路径和资源推荐
- 全流程项目支撑：覆盖从需求理解、团队组建、技术研发到成果交付的完整实践周期

技术栈组成：

- 前端框架：Vue 3.5.13
- 状态管理：Pinia + 持久化插件
- 路由系统：Vue Router
- UI 组件库：Element Plus + 自动引入
- 构建工具：Vite 7.0.0
- 代码规范：ESLint + Prettier + husky
- 测试框架：Vitest + Playwright

## 开发指南

### 环境准备

确保已安装：

- Node.js 18+
- npm 9+
- 推荐使用 VS Code 编辑器

### 下载项目
https：
```sh
git clone https://github.com/wjt123454321/TravelDiary.git
```
ssh：
```sh
git clone git@github.com:wjt123454321/TravelDiary.git
```

### 项目初始化
进入项目目录并安装依赖包
```sh
npm install
```

### 开发模式
启动本地开发服务器
```sh
npm run dev
```

### 拉取更新
```sh
git pull
```

### 提交代码
```sh
git add .
git commit -m "commit message"
git push
```

### 生产构建
生成生产构建文件
```sh
npm run build
```

## 测试套件（未验证）

### 单元测试

```sh
npm run test:unit
```

### 端到端测试

```sh
# 首次运行需安装浏览器
npx playwright install

# 完整测试流程
npm run build && npm run test:e2e

# 指定浏览器测试（示例：Chromium）
npm run test:e2e -- --project=chromium

# 调试模式
npm run test:e2e -- --debug
```

## 代码规范

### ESLint 检查

```sh
npm run lint
```

### VS Code 配置建议

```json
{
  "editor.formatOnSave": false,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit"
  },
  "eslint.validate": ["javascript", "javascriptreact", "vue"]
}
```

## 版本历史

### 2025-07-22 wjt 创建项目

1. 核心框架搭建
    - 状态管理：集成 Pinia 及持久化插件pinia-plugin-persistedstate
    - 网络层：配置 Axios 请求拦截器
    - 路由系统：添加vue-router,实现动态路由加载
    - UI 组件库：Element Plus 按需引入
    - 开发工具链：配置 unplugin 自动导入
    - 测试工具链：集成 Vitest 和 Playwright
    - 构建工具：配置 Vite
    - 初始化 ESLint 和 prettier 规范配置
    - 提交检查：添加 git hooks，使用husky确保提交规范
    - 添加scss支持
        - 添加scss支持：安装sass-embedded
        - 添加scss变量：在src/styles/variables.scss中定义变量
        - 添加scss mixin：在src/styles/mixins.scss中定义mixin

2. 项目结构：
    ```
    ├── .husky/             # Git钩子配置
    │   └── pre-commit      # 提交前自动lint
    ├── e2e/                # 端到端测试
    ├── public/             # 静态资源
    │   └── favicon.ico
    ├── src/
    │   ├── api/            # 接口层
    │   ├── assets/         # 资源文件
    │   ├── components/     # 公共组件
    │   ├── router/         # 路由配置
    │   │   └── index.js    # 路由守卫逻辑
    │   ├── store/          # 状态管理
    │   │   ├── index.js    # Pinia配置
    │   │   └── modules/    # Pinia模块
    │   ├── utils/          # 工具库
    │   ├── views/          # 页面组件
    │   ├── App.vue         # 根组件
    │   └── main.js         # 应用入口
    ├── .eslintrc.config.js # ESLint配置
    ├── .prettierrc.js      # 代码格式化配置
    ├── .gitignore          # Git忽略规则
    ├── vite.config.ts      # Vite构建配置
    ├── package.json        # 依赖管理
    └── README.md           # 项目文档
    ```

### 2025-07-30 wjt 修改框架
1. 拆分用户模块与认证模块
2. 添加路由守卫，实现用户认证与权限控制
3. 添加企业页面框架示例，使用layout+router-view实现页面切换

### 2025-08-04 wjt 添加用户模块
1. 添加Element-icon的自动导入
    - 安装unplugin-icons，结合unplugin-auto-import实现自动导入
    - 使用时`<i-ep-plus/>`就可以自动导入Plus图标

2. 更新api模块的封装
    - 把封装axios请求放到utils/request.js中
    - api/index.js统一导出

3. 添加登录注册功能
    - 添加登录注册页面
    - 添加登录注册接口

4. 添加企业端个人中心功能
    - 添加个人中心页面
    - 实现个人资料和账户安全的接口与功能

5. 添加企业端企业信息管理功能
    - 添加企业信息管理页面
    - 未完成页面具体修改与功能
### 2025-8-10 wxc 添加资源管理模块
1.资源列表展示与搜索
  提供资源名称和类型的搜索筛选功能，方便快速定位目标资源。资源列表展示包括资源名称、类型/格式、上传人、上传日期和文件大小。

2.资源上传与格式校验  
  支持拖拽或选择文件上传，用户需填写资源名称并选择资源类型。系统根据预设的类型与文件扩展名映射规则，校验上传文件格式的合法性，确保资源类型与文件格式匹配。

3.资源下载  
  用户可一键下载所需资源，系统自动处理文件名安全性及下载链接释放，保证文件顺利下载。

4.资源编辑  
  支持资源名称和类型的修改，并可以替换上传文件，方便资源内容的维护和更新。

5.资源删除
  提供删除确认弹窗，防止误操作，支持资源的安全删除。

### 2025-8-10 wjt 重写注册登录页，更新个人中心、企业设置，设计需求管理页面、首页
1. 重写注册登录页
    - 添加lodash，用于按钮防抖
2. 更新个人中心
    - 目前实现两个部分：个人资料和账户安全
3. 更新企业设置
    - 目前实现一个部分：企业信息
    - 团队管理正在实现
    - 其他部分后续开发
4. 设计需求管理页面
    - 仅有静态页面
    - 添加echarts，用于图表展示
    - 添加echarts-wordcloud，用于词云展示
5. 设计首页
    - 仅有静态页面
    - 添加chart.js，用于图表展示
    - 添加fortawesome图标，有全局包，没有全局导入
    - 在src/plugins/fortawesome.js中添加按需导入

### 2025-8-13 wjt 完成认证模块
1. 完成企业/组织认证功能
2. 更新设计需求管理页面与资源管理页面

### 2025-8-15 wjt 完成资源管理页面
1. 完成资源管理页面
    - 顶部是资源画像图表和数据
    - 下方是是资源列表
2. 完成资源上传页面
3. 完成资源查看页面 

### 2025-8-22 wjt 完企业资源和需求功能
1. 完成企业资源和需求功能
    - 完成目前页面的全部接口接入
    - 完成目前页面的全部功能实现
    - 完成页面跳转

### 2025-8-23 wjt 完成企业首页和通知中心页面设计
1. 完成企业首页和通知中心页面设计

### 2025-8-24 wjt 优化echarts导入、拆分首页
1. 按需导入echarts
2. 拆分首页为组件，以便后续修改

### 2025-8-25 wjt 首页接口接入，设计项目页
1. 完善首页接口，并完成项目页设计
2. 修复刷新token的接口调用bug

### 2025-8-26 wjt 完善项目页接口，完成项目详情页
1. 完成企业端项目接口调用
2. 完成项目详情页

### 2025-8-27 wjt 企业端移动端适配+vite打包优化
1. 企业端移动端适配
2. vite打包优化
    - 安装rollup-plugin-visualizer分析依赖体积
    - echarts全部按需导入，把最大体积1000kb的chunk优化到400kb
    - 安装vite-plugin-compression，使用gzip和brotli压缩，把最大体积400kb的chunk优化到130kb和100kb
    - 安装terser，使用terser压缩代码
    - 安装unplugin-imagemin，使用imagemin压缩图片
3. 更改vite配置base: '/',确保路由获取资源正确

### 2025-8-31 wjt 项目评分、首页、帮助文档
1. 企业端评分标准管理功能
2. 更新首页
3. 使用指南（Markdown）

### 2025-9-7 wjt 完成通知功能
1. layout连接websocket，实现未读通知数和消息通知功能
2. 完成通知中心页面
3. 完成企业端数据概览页的通知显示
4. 完成个人中心的通知设置


