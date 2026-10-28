<template>
  <div class="help-docs-container">
    <!-- 左侧导航 -->
    <div class="sidebar" :class="{ 'sidebar-collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <button @click="toggleSidebar" class="toggle-btn">
          <el-icon :class="{ 'is-expanded': !sidebarCollapsed }">
            <Fold v-if="sidebarCollapsed" />
            <Expand v-else />
          </el-icon>
        </button>
        <h3 v-show="!sidebarCollapsed">帮助文档</h3>
      </div>

      <nav class="navigation" v-show="!sidebarCollapsed">
        <div class="search-box">
          <input v-model="searchQuery" type="text" placeholder="搜索文档..." class="search-input" />
        </div>

        <ul class="nav-list">
          <li v-for="item in filteredDocs" :key="item.path" class="nav-item">
            <div
              @click="toggleCategory(item)"
              class="nav-title"
              :class="{ 'has-children': item.children }"
            >
              <span class="expand-icon" v-if="item.children">
                <el-icon :class="{ 'is-expanded': expandedItems.includes(item.path) }">
                  <ArrowRight />
                </el-icon>
              </span>
              <router-link
                v-if="!item.children"
                :to="item.path"
                class="nav-link"
                :class="{ active: $route.path === item.path }"
              >
                {{ item.title }}
              </router-link>
              <span v-else class="category-name">{{ item.title }}</span>
            </div>

            <!-- 子菜单 -->
            <ul v-if="item.children && expandedItems.includes(item.path)" class="sub-nav">
              <li v-for="child in item.children" :key="child.path" class="sub-nav-item">
                <router-link
                  :to="child.path"
                  class="nav-link"
                  :class="{ active: $route.path === child.path }"
                >
                  {{ child.title }}
                </router-link>
              </li>
            </ul>
          </li>
        </ul>
      </nav>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content" :class="{ 'content-expanded': sidebarCollapsed }">
      <div class="content-header">
        <div class="header-actions">
          <router-link to="/" class="home-link">
            <el-icon><House /></el-icon>
            <span>返回首页</span>
          </router-link>
        </div>
        <div class="breadcrumb">
          <span v-for="(crumb, index) in breadcrumbs" :key="index">
            <router-link v-if="crumb.path" :to="crumb.path">{{ crumb.title }}</router-link>
            <span v-else>{{ crumb.title }}</span>
            <span v-if="index < breadcrumbs.length - 1" class="separator"> / </span>
          </span>
        </div>
      </div>

      <article class="content">
        <div class="content-inner">
          <!-- 加载状态 -->
          <div v-if="isLoading" class="loading-container">
            <div class="loading-spinner"></div>
            <p>正在加载文档...</p>
          </div>

          <!-- 文档内容 -->
          <div
            v-else-if="currentDoc"
            class="markdown-content"
            :class="{ 'error-content': currentDoc.isError }"
          >
            <div v-html="currentDoc.content"></div>
          </div>

          <!-- 404页面 - 当路由不存在于配置中时显示 -->
          <div v-else class="not-found">
            <h1>页面未找到</h1>
            <p>抱歉，您访问的文档页面不存在。</p>
            <p>请检查URL是否正确，或从左侧导航菜单中选择有效的文档。</p>
            <router-link to="/help" class="back-link">返回首页</router-link>
          </div>
        </div>

        <!-- 右侧目录 -->
        <aside class="table-of-contents" v-if="tableOfContents.length > 0 && !isLoading">
          <h4>目录</h4>
          <nav class="toc-nav">
            <ul>
              <li
                v-for="heading in tableOfContents"
                :key="heading.id"
                :class="['toc-item', `toc-level-${heading.level}`]"
              >
                <a
                  :href="`#${heading.id}`"
                  class="toc-link"
                  :class="{ active: activeHeading === heading.id }"
                  @click="scrollToHeading(heading.id)"
                >
                  {{ heading.text }}
                </a>
              </li>
            </ul>
          </nav>
        </aside>
      </article>

      <!-- 上一页/下一页 -->
      <div class="pagination" v-if="(prevDoc || nextDoc) && !isLoading">
        <router-link v-if="prevDoc" :to="prevDoc.path" class="page-link prev-page">
          <span class="arrow">←</span>
          <div>
            <small>上一页</small>
            <div>{{ prevDoc.title }}</div>
          </div>
        </router-link>

        <router-link v-if="nextDoc" :to="nextDoc.path" class="page-link next-page">
          <div>
            <small>下一页</small>
            <div>{{ nextDoc.title }}</div>
          </div>
          <span class="arrow">→</span>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, nextTick, onBeforeUnmount } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowRight, Fold, Expand, House } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

// 响应式数据
const sidebarCollapsed = ref(false)
const searchQuery = ref('')
const expandedItems = ref(['getting-started'])
const tableOfContents = ref([])
const activeHeading = ref('')
const isLoading = ref(false)
const documentCache = ref(new Map()) // 文档缓存

// 懒加载的模块
let md = null
let hljs = null

// 需要的语言包列表（根据实际需要调整）
const REQUIRED_LANGUAGES = [
  'javascript',
  'typescript',
  'css',
  'html',
  'json',
  'bash',
  'python',
  'java'
]

// 懒加载highlight.js和语言包
const loadHighlightJs = async () => {
  if (hljs) return hljs

  try {
    // 动态导入核心库
    const hljsCore = await import('highlight.js/lib/core')
    hljs = hljsCore.default

    // 按需加载语言包
    const languagePromises = REQUIRED_LANGUAGES.map(async (lang) => {
      try {
        const module = await import(`highlight.js/lib/languages/${lang}`)
        hljs.registerLanguage(lang, module.default)
        return lang
      } catch (err) {
        console.warn(`Failed to load language: ${lang}`, err)
        return null
      }
    })

    const loadedLanguages = await Promise.all(languagePromises)
    console.log('Loaded highlight.js languages:', loadedLanguages.filter(Boolean))

    return hljs
  } catch (error) {
    console.error('Failed to load highlight.js:', error)
    // 返回一个简单的mock对象，避免破坏功能
    return {
      highlight: (code) => code,
      getLanguage: () => null
    }
  }
}

// 懒加载markdown-it
const loadMarkdownIt = async () => {
  if (md) return md

  try {
    const [MarkdownItModule, highlightJs] = await Promise.all([
      import('markdown-it'),
      loadHighlightJs()
    ])

    const MarkdownIt = MarkdownItModule.default

    // 初始化markdown解析器
    md = new MarkdownIt({
      html: true,
      linkify: true,
      typographer: false,
      breaks: true,
      highlight: function (str, lang) {
        if (lang && highlightJs.getLanguage && highlightJs.getLanguage(lang)) {
          try {
            return highlightJs.highlight(str, { language: lang }).value
          } catch (err) {
            console.error('Highlight error:', err)
          }
        }
        return ''
      }
    })

    // 设置自定义渲染规则
    setupMarkdownRules(md)

    console.log('Markdown-it initialized successfully')
    return md
  } catch (error) {
    console.error('Failed to load markdown-it:', error)
    // 返回一个简单的mock对象
    return {
      render: (content) => `<div class="markdown-fallback">${content.replace(/\n/g, '<br>')}</div>`
    }
  }
}

// 设置markdown自定义渲染规则
const setupMarkdownRules = (markdownInstance) => {
  // 添加自定义渲染规则
  markdownInstance.renderer.rules.table_open = function () {
    return '<div class="table-wrapper"><table class="markdown-table">\n'
  }

  markdownInstance.renderer.rules.table_close = function () {
    return '</table></div>\n'
  }

  // 自定义强调（加粗）渲染 - 确保正确处理
  const defaultStrongOpen =
    markdownInstance.renderer.rules.strong_open ||
    function (tokens, idx, options, env, renderer) {
      return '<strong>'
    }

  const defaultStrongClose =
    markdownInstance.renderer.rules.strong_close ||
    function (tokens, idx, options, env, renderer) {
      return '</strong>'
    }

  markdownInstance.renderer.rules.strong_open = function (tokens, idx, options, env, renderer) {
    return '<strong class="markdown-strong">'
  }

  markdownInstance.renderer.rules.strong_close = defaultStrongClose

  // 添加视频链接处理
  const defaultLinkOpen =
    markdownInstance.renderer.rules.link_open ||
    function (tokens, idx, options, env, self) {
      return self.renderToken(tokens, idx, options)
    }

  markdownInstance.renderer.rules.link_open = function (tokens, idx, options, env, self) {
    const token = tokens[idx]
    const href = token.attrGet('href')

    // 检查是否是视频链接
    if (href && href.match(/\.(mp4|webm|ogg)$/i)) {
      tokens[idx].tag = 'video'
      token.attrSet('controls', '')
      token.attrSet('preload', 'metadata')
      token.attrSet('style', 'max-width: 100%; border-radius: 8px; margin: 16px 0;')
      // 移除原始的 href 属性
      token.attrs = token.attrs.filter(([name]) => name !== 'href')
      token.attrSet('src', href)

      // 跳过链接的内容和结束标签
      for (let i = idx + 1; i < tokens.length; i++) {
        if (tokens[i].type === 'link_close') {
          tokens[i].tag = 'video'
          break
        }
      }
      return self.renderToken(tokens, idx, options)
    }

    return defaultLinkOpen(tokens, idx, options, env, self)
  }

  // 自定义标题渲染，自动生成ID和锚点
  markdownInstance.renderer.rules.heading_open = function (tokens, idx, options, env, renderer) {
    const token = tokens[idx]
    const level = token.tag.substr(1)
    const nextToken = tokens[idx + 1]

    if (nextToken && nextToken.type === 'inline') {
      // 获取原始内容，不要过早地处理标记
      const content = nextToken.children
        .filter((t) => t.type === 'text' || t.type === 'code_inline')
        .map((t) => t.content)
        .join('')

      const id = generateHeadingId(content)
      token.attrSet('id', id)
      token.attrSet('class', `markdown-heading level-${level}`)

      return `<${token.tag} id="${id}" class="markdown-heading level-${level}">
        <a class="anchor-link" href="#${id}" aria-label="Permalink"></a>`
    }

    return renderer.renderToken(tokens, idx, options)
  }

  markdownInstance.renderer.rules.heading_close = function (tokens, idx, options, env, renderer) {
    return `</${tokens[idx].tag}>\n`
  }
}

// 改进的标题ID生成函数
const generateHeadingId = (text) => {
  let cleanText = text
    // 先移除加粗、斜体等标记，但保留内容
    .replace(/\*\*(.*?)\*\*/g, '$1') // 移除加粗标记但保留内容
    .replace(/\*(.*?)\*/g, '$1') // 移除斜体标记但保留内容
    .replace(/_+(.*?)_+/g, '$1') // 移除下划线标记但保留内容
    .replace(/`(.*?)`/g, '$1') // 移除行内代码标记但保留内容
    .replace(/~(.*?)~/g, '$1') // 移除删除线标记但保留内容
    .replace(/<[^>]*>/g, '') // 移除HTML标签
    .trim()

  let id = cleanText
    .toLowerCase()
    .replace(/[^\u4e00-\u9fa5\w\s-]/g, '')
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')

  if (!id) {
    id = 'heading-' + Date.now()
  }

  return id
}

// 文档数据结构
const docsData = ref([
  {
    path: '/help',
    title: '开始使用',
    icon: '📚',
    children: [
      { path: '/help/introduction', title: '系统简介', file: 'introduction' },
      { path: '/help/quick-start', title: '快速开始', file: 'quick-start' }
    ]
  },
  {
    path: '/help/user-guide/student',
    title: '学生端使用指南',
    icon: '👨‍🎓',
    children: [
      {
        path: '/help/user-guide/student/profile',
        title: '个人资料管理',
        file: 'user-guide/student/profile'
      },
      {
        path: '/help/user-guide/student/project-match',
        title: '项目匹配与申请',
        file: 'user-guide/student/project-match'
      },
      {
        path: '/help/user-guide/student/team-join',
        title: '团队加入与管理',
        file: 'user-guide/student/team-join'
      },
      {
        path: '/help/user-guide/student/learning-path',
        title: '学习路径规划',
        file: 'user-guide/student/learning-path'
      }
    ]
  },
  {
    path: '/help/user-guide/enterprise',
    title: '企业端使用指南',
    icon: '🏢',
    children: [
      {
        path: '/help/user-guide/enterprise/profile',
        title: '企业信息管理',
        file: 'user-guide/enterprise/profile'
      },
      {
        path: '/help/user-guide/enterprise/resources',
        title: '资源发布与管理',
        file: 'user-guide/enterprise/resources'
      },
      {
        path: '/help/user-guide/enterprise/demands',
        title: '需求发布与管理',
        file: 'user-guide/enterprise/demands'
      },
      {
        path: '/help/user-guide/enterprise/projects',
        title: '项目管理',
        file: 'user-guide/enterprise/projects'
      },
      {
        path: '/help/user-guide/enterprise/team',
        title: '团队管理',
        file: 'user-guide/enterprise/team'
      }
    ]
  }
])

// 验证响应是否为markdown内容
const isValidMarkdownResponse = (response, content) => {
  const contentType = response.headers.get('content-type') || ''

  if (contentType.includes('text/html')) {
    return false
  }

  if (content.includes('<script') || content.includes('<meta') || content.includes('<!DOCTYPE')) {
    return false
  }

  return true
}

// 新增：预处理markdown内容，修复加粗问题
const preprocessMarkdown = (content) => {
  // 先处理所有的加粗标记，确保它们能被正确识别
  let processed = content

  // Step 1: 标记所有加粗内容，用临时标记保护起来
  const boldBlocks = []
  let tempContent = content

  // 匹配所有可能的加粗模式
  const boldPatterns = [
    /\*\*([^*]+?)\*\*/g, // 标准加粗
    /\*\*([^*]+?)：\*\*/g, // 加粗后跟中文冒号
    /\*\*([^*]+?):\*\*/g // 加粗后跟英文冒号
  ]

  // 收集所有加粗块
  boldPatterns.forEach((pattern) => {
    let match
    while ((match = pattern.exec(content)) !== null) {
      boldBlocks.push({
        full: match[0],
        content: match[1],
        index: match.index
      })
    }
  })

  // Step 2: 处理各种特殊情况
  processed = content
    // 处理 **文本**后面紧跟标点的情况（添加零宽空格）
    .replace(/\*\*([^*]+?)\*\*([，。！？；：、,.!?;:])/g, '**$1**\u200B$2')

    // 处理 标点**文本** 的情况
    .replace(/([，。！？；：、,.!?;:])\*\*([^*]+?)\*\*/g, '$1\u200B**$2**')

    // 处理 **文本**紧跟括号的情况
    .replace(/\*\*([^*]+?)\*\*([(（【[])/g, '**$1**\u200B$2')
    .replace(/([)）】])\*\*([^*]+?)\*\*/g, '$1\u200B**$2**')

    // 处理 **文本：**其他文本 的特殊情况（冒号在加粗内）
    .replace(/\*\*([^*：:]+)[：:]\*\*/g, (match, p1) => {
      const colon = match.includes('：') ? '：' : ':'
      return `**${p1}${colon}**`
    })

    // 处理 **[链接文本]()** 的情况
    .replace(/\*\*\[([^\]]+)\]\(([^)]+)\)\*\*/g, '**[$1]($2)**')

    // 处理 **文本**[链接]() 的情况
    .replace(/\*\*([^*]+?)\*\*(\[[^\]]+\]\([^)]+\))/g, '**$1** $2')

    // 处理中英文混合的加粗
    .replace(/\*\*([^*]+?)\*\*([a-zA-Z])/g, '**$1** $2')
    .replace(/([a-zA-Z])\*\*([^*]+?)\*\*/g, '$1 **$2**')

    // 修复可能被破坏的加粗标记（连续的***或更多）
    .replace(/\*{3,}/g, '**')

    // 清理多余的零宽空格（如果有多个连续的）
    .replace(/\u200B{2,}/g, '\u200B')

  return processed
}

const aggressivePreprocessMarkdown = (content) => {
  // 使用更强力的替换策略
  const lines = content.split('\n')
  const processedLines = lines.map((line) => {
    // 如果这一行包含 **
    if (line.includes('**')) {
      // 找出所有的加粗对
      const parts = []
      let lastIndex = 0
      let inBold = false

      for (let i = 0; i < line.length - 1; i++) {
        if (line[i] === '*' && line[i + 1] === '*') {
          if (!inBold) {
            // 开始加粗
            if (i > lastIndex) {
              parts.push({
                type: 'text',
                content: line.substring(lastIndex, i)
              })
            }
            lastIndex = i + 2
            inBold = true
          } else {
            // 结束加粗
            parts.push({
              type: 'bold',
              content: line.substring(lastIndex, i)
            })
            lastIndex = i + 2
            inBold = false
          }
          i++ // 跳过第二个*
        }
      }

      // 添加最后的部分
      if (lastIndex < line.length) {
        parts.push({
          type: 'text',
          content: line.substring(lastIndex)
        })
      }

      // 重新组装，确保加粗标记周围有正确的分隔
      return parts
        .map((part, index) => {
          if (part.type === 'bold') {
            const nextPart = parts[index + 1]
            const prevPart = parts[index - 1]

            let prefix = ''
            let suffix = ''

            // 检查前面是否需要空格
            if (prevPart && prevPart.content && !prevPart.content.endsWith(' ')) {
              const lastChar = prevPart.content[prevPart.content.length - 1]
              if (lastChar && !/[\s([{]/.test(lastChar)) {
                prefix = ' '
              }
            }

            // 检查后面是否需要空格
            if (nextPart && nextPart.content && !nextPart.content.startsWith(' ')) {
              const firstChar = nextPart.content[0]
              // 如果后面是标点符号，添加零宽空格；否则添加普通空格
              if (/[，。！？；：、,.!?;:]/.test(firstChar)) {
                suffix = '\u200B'
              } else if (!/[\s)]}]/.test(firstChar)) {
                suffix = ' '
              }
            }

            return `${prefix}**${part.content}**${suffix}`
          }
          return part.content
        })
        .join('')
    }
    return line
  })

  return processedLines.join('\n')
}

// 后处理HTML，确保加粗正确显示
const postProcessHTML = (html) => {
  // 移除零宽空格（如果影响显示）
  let processed = html.replace(/\u200B/g, '')

  // 确保所有的strong标签都有正确的class
  processed = processed.replace(/<strong>/g, '<strong class="md-bold">')

  // 修复可能的嵌套问题
  processed = processed.replace(/<strong>([^<]*)<strong>/g, '<strong>$1')
  processed = processed.replace(/<\/strong>([^<]*)<\/strong>/g, '$1</strong>')

  return processed
}

// 修改 importMarkdownFile 函数
const importMarkdownFile = async (filePath) => {
  try {
    if (documentCache.value.has(filePath)) {
      return documentCache.value.get(filePath)
    }

    const response = await fetch(`/docs/${filePath}.md`)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    let content = await response.text()

    // 先尝试温和的预处理
    let processedContent = preprocessMarkdown(content)

    // 检查是否还有未处理的加粗标记
    if (processedContent.includes('**')) {
      // 统计未配对的**
      const matches = processedContent.match(/\*\*/g) || []
      if (matches.length % 2 !== 0) {
        console.warn('Found unpaired ** markers, using aggressive preprocessing')
        // 使用更激进的处理
        processedContent = aggressivePreprocessMarkdown(content)
      }
    }

    // 使用markdown-it渲染
    const markdownInstance = await loadMarkdownIt()
    let renderedContent = markdownInstance.render(processedContent)

    // 后处理
    renderedContent = postProcessHTML(renderedContent)

    // 最后的检查：如果还有**没被处理，直接替换
    if (renderedContent.includes('**')) {
      renderedContent = renderedContent.replace(
        /\*\*([^*]+?)\*\*/g,
        '<strong class="md-bold">$1</strong>'
      )
    }

    documentCache.value.set(filePath, renderedContent)
    return renderedContent
  } catch (error) {
    console.error(`Failed to import markdown file: ${filePath}`, error.message)
    // 错误处理...
  }
}

// 获取文档配置信息
const getDocConfig = (path) => {
  for (const category of docsData.value) {
    if (category.path === path) {
      return category
    }
    if (category.children) {
      const child = category.children.find((c) => c.path === path)
      if (child) {
        return child
      }
    }
  }
  return null
}

// 计算属性
const filteredDocs = computed(() => {
  if (!searchQuery.value) return docsData.value

  const query = searchQuery.value.toLowerCase()
  return docsData.value.filter((item) => {
    if (item.title.toLowerCase().includes(query)) return true
    if (item.children) {
      return item.children.some((child) => child.title.toLowerCase().includes(query))
    }
    return false
  })
})

const currentDoc = ref(null)

// 加载当前文档
const loadCurrentDoc = async () => {
  const path = route.path
  const docConfig = getDocConfig(path)

  if (!docConfig) {
    currentDoc.value = null
    isLoading.value = false
    return
  }

  if (!docConfig.file) {
    console.warn(`No file configured for path: ${path}`)
    currentDoc.value = null
    isLoading.value = false
    return
  }

  isLoading.value = true

  try {
    const content = await importMarkdownFile(docConfig.file)

    currentDoc.value = {
      content,
      title: docConfig.title,
      path: path,
      isError: content.includes('markdown-error') || content.includes('文档加载失败')
    }
  } catch (error) {
    console.error('Error loading document:', error)
    currentDoc.value = {
      content: `<div class="markdown-error"><h1>文档加载失败</h1><p>发生了意外错误：${error.message}</p></div>`,
      title: '错误',
      path: path,
      isError: true
    }
  } finally {
    isLoading.value = false
  }
}

const breadcrumbs = computed(() => {
  const crumbs = [{ title: '帮助文档', path: '/help' }]
  const path = route.path

  for (const category of docsData.value) {
    if (category.children) {
      const child = category.children.find((c) => c.path === path)
      if (child) {
        crumbs.push({ title: category.title })
        crumbs.push({ title: child.title })
        break
      }
    }
  }

  return crumbs
})

// 获取所有文档的扁平列表，用于上一页/下一页导航
const flatDocsList = computed(() => {
  const docs = []

  for (const category of docsData.value) {
    if (category.file) {
      docs.push(category)
    }
    if (category.children) {
      docs.push(...category.children)
    }
  }

  return docs
})

const prevDoc = computed(() => {
  const currentIndex = flatDocsList.value.findIndex((doc) => doc.path === route.path)
  return currentIndex > 0 ? flatDocsList.value[currentIndex - 1] : null
})

const nextDoc = computed(() => {
  const currentIndex = flatDocsList.value.findIndex((doc) => doc.path === route.path)
  return currentIndex >= 0 && currentIndex < flatDocsList.value.length - 1
    ? flatDocsList.value[currentIndex + 1]
    : null
})

// 方法
const toggleSidebar = () => {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

const toggleCategory = (item) => {
  if (!item.children) return

  const index = expandedItems.value.indexOf(item.path)
  if (index > -1) {
    expandedItems.value.splice(index, 1)
  } else {
    expandedItems.value.push(item.path)
  }
}

const scrollToHeading = (id) => {
  const element = document.getElementById(id)
  if (element) {
    element.scrollIntoView({ behavior: 'smooth' })
  }
}

// 改进的目录提取函数
const extractTableOfContents = () => {
  nextTick(() => {
    const headings = document.querySelectorAll('.markdown-content .markdown-heading')

    const tocItems = []
    const headingCounts = new Map()

    headings.forEach((heading) => {
      const text = heading.textContent?.replace('Permalink', '').trim() || ''
      const level = parseInt(heading.tagName.charAt(1))
      let id = heading.id

      if (!id) {
        id = generateHeadingId(text)

        if (headingCounts.has(id)) {
          const count = headingCounts.get(id) + 1
          headingCounts.set(id, count)
          id = `${id}-${count}`
        } else {
          headingCounts.set(id, 1)
        }

        heading.id = id
      }

      if (text && level >= 1 && level <= 4) {
        tocItems.push({
          id,
          text,
          level
        })
      }
    })

    tableOfContents.value = tocItems
  })
}

// 清除文档缓存的方法
const clearDocumentCache = () => {
  documentCache.value.clear()
  loadCurrentDoc()
}

// 预加载文档的方法（使用懒加载）
const preloadDocuments = async () => {
  // 确保markdown解析器已加载
  await loadMarkdownIt()

  const allDocs = flatDocsList.value
  const loadPromises = allDocs
    .filter((doc) => doc.file && !documentCache.value.has(doc.file))
    .slice(0, 3)
    .map((doc) => importMarkdownFile(doc.file))

  try {
    await Promise.all(loadPromises)
    console.log('Documents preloaded successfully')
  } catch (error) {
    console.warn('Some documents failed to preload:', error)
  }
}

// 改进的滚动监听
const handleScroll = () => {
  const headings = document.querySelectorAll('.markdown-content .markdown-heading')
  let activeId = ''

  for (const heading of headings) {
    const rect = heading.getBoundingClientRect()
    if (rect.top <= 120 && rect.bottom > 0) {
      activeId = heading.id
    }
  }

  if (activeId !== activeHeading.value) {
    activeHeading.value = activeId
  }
}

// 监听路由变化
watch(
  () => route.path,
  async () => {
    if (route.path === '/help') {
      router.push('/help/introduction')
      return
    }
    await loadCurrentDoc()
    extractTableOfContents()
  },
  { immediate: true }
)

let scrollTimeout = null

onMounted(async () => {
  const throttledScroll = () => {
    if (scrollTimeout) return
    scrollTimeout = setTimeout(() => {
      handleScroll()
      scrollTimeout = null
    }, 100)
  }

  window.addEventListener('scroll', throttledScroll)

  await loadCurrentDoc()
  extractTableOfContents()

  // 延迟预加载其他文档
  setTimeout(() => {
    preloadDocuments()
  }, 1500) // 增加延迟，优先保证首屏加载
})

onBeforeUnmount(() => {
  if (scrollTimeout) {
    clearTimeout(scrollTimeout)
  }
})

// 提供给父组件的方法
defineExpose({
  clearDocumentCache,
  preloadDocuments,
  loadCurrentDoc
})
</script>

<style scoped>
.help-docs-container {
  display: flex;
  min-height: 100vh;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid #e4e7ed;
}

.header-actions {
  display: flex;
  align-items: center;
}

.home-link {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #409eff;
  text-decoration: none;
  font-size: 14px;
  padding: 6px 12px;
  border-radius: 4px;
  transition: all 0.3s;
}

.home-link:hover {
  background-color: #ecf5ff;
}

.home-link .el-icon {
  font-size: 16px;
}

/* 主内容区域样式 */
.main-content {
  flex: 1;
  background: #fafafa;
}

/* 加载状态样式 */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 64px 32px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #0366d6;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 侧边栏样式 */
.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e1e4e8;
  transition: all 0.3s ease;
  position: fixed;
  height: 100vh;
  overflow-y: auto;
  z-index: 100;
}

.sidebar-collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e1e4e8;
  display: flex;
  align-items: center;
  gap: 12px;
}

.toggle-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.toggle-btn:hover {
  background: #f0f2f5;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.toggle-btn:active {
  transform: translateY(0);
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

.toggle-btn .el-icon {
  font-size: 18px;
  color: #4a5568;
  transition: all 0.3s ease;
}

/* .toggle-btn .el-icon.is-expanded {
  color: #3182ce;
} */

.navigation {
  padding: 16px;
}

.search-box {
  margin-bottom: 16px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5da;
  border-radius: 6px;
  font-size: 14px;
}

.search-input:focus {
  outline: none;
  border-color: #0366d6;
  box-shadow: 0 0 0 3px rgba(3, 102, 214, 0.1);
}

.nav-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-item {
  margin-bottom: 4px;
}

.nav-title {
  display: flex;
  align-items: center;
  cursor: pointer;
  padding: 8px 0;
}

.expand-icon {
  width: 16px;
  margin-right: 6px;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
}

.expand-icon .el-icon.is-expanded {
  transform: rotate(90deg);
}

.nav-link {
  color: #586069;
  text-decoration: none;
  padding: 8px 0;
  display: block;
  border-radius: 6px;
  transition: all 0.2s;
}

.nav-link:hover {
  color: #0366d6;
  background: #f6f8fa;
}

.nav-link.active {
  color: #0366d6;
  background: #e3f2fd;
  font-weight: 600;
}

.category-name {
  font-weight: 600;
  color: #24292e;
}

.sub-nav {
  list-style: none;
  padding: 0;
  margin: 0 0 0 22px;
}

.sub-nav-item {
  margin-bottom: 2px;

  a {
    padding-left: 8px;
  }
}

/* 主内容区样式 */
.main-content {
  margin-left: 280px;
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  width: calc(100% - 280px);
}

.content-expanded {
  margin-left: 60px;
  width: calc(100% - 60px);
}

.content-header {
  background: white;
  border-bottom: 1px solid #e1e4e8;
  padding: 16px 32px;
}

.breadcrumb {
  font-size: 14px;
  color: #586069;
}

.breadcrumb a {
  color: #0366d6;
  text-decoration: none;
}

.breadcrumb a:hover {
  text-decoration: underline;
}

.separator {
  margin: 0 8px;
}

.content {
  display: flex;
  margin: 0 auto;
  padding: 32px;
  gap: 32px;
  max-width: 1400px;
  width: 100%;
}

.content-inner {
  width: 900px; /* 固定文档内容宽度 */
  min-width: 600px; /* 最小宽度 */
}

/* 优化的Markdown内容样式 */
.markdown-content {
  border-radius: 6px;
  padding: 48px;
  line-height: 1.7;
  font-size: 16px;
  color: #24292e;
}

/* 错误内容样式 */
.error-content {
  border-left: 4px solid #d73a49;
  background: #ffeef0;
}

.error-content h1 {
  color: #d73a49;
}

.error-content code {
  background: #fff5f5;
  border: 1px solid #fdbdbe;
}

/* 改进的标题样式，层次分明 */
.markdown-content :deep(.markdown-heading) {
  margin-top: 48px;
  margin-bottom: 24px;
  font-weight: 700;
  line-height: 1.25;
  position: relative;
  scroll-margin-top: 80px; /* 滚动时的偏移 */
}

.markdown-content :deep(.markdown-heading.level-1) {
  font-size: 2.5em;
  border-bottom: 3px solid #e1e4e8;
  padding-bottom: 16px;
  margin-top: 0;
  margin-bottom: 32px;
  color: #1a1a1a;
}

.markdown-content :deep(.markdown-heading.level-2) {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 12px;
  margin-bottom: 24px;
  color: #24292e;
}

.markdown-content :deep(.markdown-heading.level-3) {
  font-size: 1.5em;
  margin-bottom: 20px;
  color: #2c3e50;
  font-weight: 600;
}

.markdown-content :deep(.markdown-heading.level-4) {
  font-size: 1.25em;
  margin-bottom: 16px;
  color: #34495e;
  font-weight: 600;
}

/* 锚点链接样式 */
.markdown-content :deep(.anchor-link) {
  position: absolute;
  left: -24px;
  top: 0;
  bottom: 0;
  width: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  opacity: 0;
  transition: opacity 0.2s;
}

.markdown-content :deep(.anchor-link)::before {
  content: '#';
  color: #0366d6;
  font-weight: 400;
}

.markdown-content :deep(.markdown-heading):hover .anchor-link {
  opacity: 1;
}

/* 段落和文本样式 */
.markdown-content :deep(p) {
  margin: 16px 0;
  line-height: 1.7;
}

.markdown-content :deep(strong) {
  font-weight: 600;
  color: #1a1a1a;
}

/* 代码样式 */
.markdown-content :deep(code) {
  background: #f8f8f8;
  padding: 3px 6px;
  border-radius: 4px;
  font-family:
    'SFMono-Regular', 'Monaco', 'Inconsolata', 'Liberation Mono', 'Courier New', monospace;
  font-size: 0.9em;
  border: 1px solid #e1e4e8;
  color: #d73a49;
}

.markdown-content :deep(pre) {
  background: #f8f8f8;
  padding: 20px;
  border-radius: 8px;
  overflow-x: auto;
  border: 1px solid #e1e4e8;
  margin: 24px 0;
  font-size: 14px;
}

.markdown-content :deep(pre code) {
  background: none;
  padding: 0;
  border: none;
  color: inherit;
  font-size: inherit;
}

/* 引用样式 */
.markdown-content :deep(blockquote) {
  border-left: 4px solid #0366d6;
  padding: 16px 20px;
  margin: 24px 0;
  background: #f8fafc;
  color: #57606a;
  border-radius: 0 6px 6px 0;
}

.markdown-content :deep(blockquote p:first-child) {
  margin-top: 0;
}

.markdown-content :deep(blockquote p:last-child) {
  margin-bottom: 0;
}

/* 列表样式 */
.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  padding-left: 32px;
  margin: 20px 0;
}

.markdown-content :deep(li) {
  margin: 8px 0;
  line-height: 1.7;
}

.markdown-content :deep(ul ul),
.markdown-content :deep(ol ol),
.markdown-content :deep(ul ol),
.markdown-content :deep(ol ul) {
  margin: 8px 0;
}

/* 改进的表格样式 */
.markdown-content :deep(.table-wrapper) {
  overflow-x: auto;
  margin: 24px 0;
  border-radius: 8px;
  border: 1px solid #e1e4e8;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.markdown-content :deep(.markdown-table) {
  width: 100%;
  border-collapse: collapse;
  margin: 0;
  font-size: 14px;
  background: white;
}

.markdown-content :deep(.markdown-table th),
.markdown-content :deep(.markdown-table td) {
  border: 1px solid #e1e4e8;
  padding: 12px 16px;
  text-align: left;
  vertical-align: top;
}

.markdown-content :deep(.markdown-table th) {
  background: #f8f9fa;
  font-weight: 600;
  color: #24292e;
  position: sticky;
  top: 0;
  z-index: 1;
}

.markdown-content :deep(.markdown-table tr:nth-child(even)) {
  background: #fafbfc;
}

.markdown-content :deep(.markdown-table tr:hover) {
  background: #f1f8ff;
}

/* 图片样式 */
.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 水平分隔线 */
.markdown-content :deep(hr) {
  height: 1px;
  background: #e1e4e8;
  border: none;
  margin: 32px 0;
}

/* Markdown链接样式 */
.markdown-content :deep(a) {
  color: #0366d6;
  text-decoration: none;
  transition: color 0.2s ease-in-out;
}

.markdown-content :deep(a:hover) {
  color: #0969da;
  text-decoration: underline;
}

/* 暗色主题下的链接样式 */
@media (prefers-color-scheme: dark) {
  .markdown-content :deep(a) {
    color: #58a6ff;
  }
  .markdown-content :deep(a:hover) {
    color: #79b8ff;
  }
}

/* 目录样式 */
.table-of-contents {
  width: 220px;
  position: sticky;
  top: 32px;
  height: fit-content;
  flex-shrink: 0;
}

.table-of-contents h4 {
  margin: 0 0 16px 0;
  font-size: 16px;
  font-weight: 600;
  color: #24292e;
}

.toc-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.toc-item {
  margin-bottom: 6px;
}

.toc-link {
  display: block;
  color: #57606a;
  text-decoration: none;
  font-size: 14px;
  padding: 6px 0 6px 12px;
  border-left: 2px solid transparent;
  transition: all 0.2s;
  border-radius: 0 4px 4px 0;
  line-height: 1.4;
}

.toc-link:hover {
  color: #0366d6;
  background: #f8fafc;
}

.toc-link.active {
  color: #0366d6;
  border-left-color: #0366d6;
  font-weight: 500;
  background: #f1f8ff;
}

.toc-level-1 .toc-link {
  font-weight: 600;
  font-size: 15px;
}

.toc-level-2 .toc-link {
  padding-left: 20px;
}

.toc-level-3 .toc-link {
  padding-left: 28px;
  font-size: 13px;
}

.toc-level-4 .toc-link {
  padding-left: 36px;
  font-size: 13px;
  color: #8b949e;
}

/* 分页样式 */
.pagination {
  display: flex;
  justify-content: space-between;
  margin: 32px;
  gap: 16px;
  max-width: 1400px;
  width: 100%;
  margin-left: auto;
  margin-right: auto;
}

.page-link {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: white;
  border: 1px solid #e1e4e8;
  border-radius: 6px;
  text-decoration: none;
  color: #24292e;
  transition: all 0.2s;
}

.page-link:hover {
  border-color: #0366d6;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.prev-page {
  margin-right: auto;
}

.next-page {
  margin-left: auto;
}

.arrow {
  font-size: 18px;
  font-weight: bold;
}

/* 404页面 */
.not-found {
  text-align: center;
  padding: 64px 32px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.back-link {
  color: #0366d6;
  text-decoration: none;
  font-weight: 500;
}

.back-link:hover {
  text-decoration: underline;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .content-inner {
    width: 700px;
  }
}

@media (max-width: 768px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar-collapsed {
    transform: translateX(0);
    width: 100vw;
  }

  .main-content {
    margin-left: 0;
    width: 100%;
  }

  .content {
    padding: 16px;
    flex-direction: column;
  }

  .content-inner {
    width: 100%;
    min-width: auto;
  }

  .markdown-content {
    padding: 24px 20px;
  }

  .table-of-contents {
    width: 100%;
    position: static;
  }

  .pagination {
    flex-direction: column;
    margin: 16px;
  }

  .page-link {
    width: 100%;
  }
}

/* 暗色主题支持 */
@media (prefers-color-scheme: dark) {
  .help-docs-container {
    background: #0d1117;
  }

  .sidebar {
    background: #161b22;
    border-right-color: #21262d;
  }

  .sidebar-header {
    border-bottom-color: #21262d;
  }

  .search-input {
    background: #0d1117;
    border-color: #21262d;
    color: #c9d1d9;
  }

  .nav-link {
    color: #8b949e;
  }

  .nav-link:hover {
    color: #58a6ff;
    background: #21262d;
  }

  .nav-link.active {
    color: #58a6ff;
    background: #1f6feb26;
  }

  .content-header {
    background: #161b22;
    border-bottom-color: #21262d;
  }

  .markdown-content,
  .loading-container,
  .not-found,
  .page-link {
    background: #161b22;
    color: #c9d1d9;
  }

  .markdown-content :deep(.markdown-heading) {
    color: #f0f6fc;
  }

  .markdown-content :deep(.markdown-heading.level-1) {
    border-bottom-color: #21262d;
    color: #f0f6fc;
  }

  .markdown-content :deep(.markdown-heading.level-2) {
    border-bottom-color: #21262d;
    color: #f0f6fc;
  }

  .markdown-content :deep(code) {
    background: #21262d;
    border-color: #30363d;
    color: #f85149;
  }

  .markdown-content :deep(pre) {
    background: #0d1117;
    border-color: #21262d;
  }

  .markdown-content :deep(blockquote) {
    background: #0d1117;
    border-left-color: #58a6ff;
    color: #8b949e;
  }

  .markdown-content :deep(.table-wrapper) {
    border-color: #21262d;
  }

  .markdown-content :deep(.markdown-table th),
  .markdown-content :deep(.markdown-table td) {
    border-color: #21262d;
  }

  .markdown-content :deep(.markdown-table th) {
    background: #0d1117;
    color: #c9d1d9;
  }

  .markdown-content :deep(.markdown-table tr:nth-child(even)) {
    background: #0d1117;
  }

  .markdown-content :deep(.markdown-table tr:hover) {
    background: #161b22;
  }
}

/* 添加明确的加粗样式 */
.markdown-content :deep(strong),
.markdown-content :deep(.markdown-strong) {
  font-weight: 700 !important; /* 使用 !important 确保样式生效 */
  color: #1a1a1a;
}

/* 确保加粗在各种上下文中都能正常工作 */
.markdown-content :deep(p strong),
.markdown-content :deep(li strong),
.markdown-content :deep(td strong),
.markdown-content :deep(blockquote strong) {
  font-weight: 700 !important;
}

/* 加粗链接的特殊处理 */
.markdown-content :deep(strong a),
.markdown-content :deep(a strong) {
  font-weight: 700 !important;
}

/* 暗色主题下的加粗 */
@media (prefers-color-scheme: dark) {
  .markdown-content :deep(strong),
  .markdown-content :deep(.markdown-strong) {
    color: #f0f6fc;
    font-weight: 700 !important;
  }
}
</style>
