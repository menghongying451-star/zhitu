import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import vueJsx from '@vitejs/plugin-vue-jsx'
import vueDevTools from 'vite-plugin-vue-devtools'

import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'
import Icons from 'unplugin-icons/vite'
import IconsResolver from 'unplugin-icons/resolver'
import { visualizer } from 'rollup-plugin-visualizer'
import viteCompression from 'vite-plugin-compression'
import ImageminPlugin from 'unplugin-imagemin/vite'

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  plugins: [
    vue(),
    // vueJsx(),
    vueDevTools(),
    AutoImport({
      resolvers: [
        ElementPlusResolver(),
        IconsResolver({
          prefix: 'Icon',
          enabledCollections: ['mdi', 'ep', 'ion', 'fa']
        })
      ]
    }),
    Components({
      resolvers: [
        IconsResolver({
          enabledCollections: ['ep']
        }),
        ElementPlusResolver()
      ]
    }),
    Icons({
      autoInstall: true,
      compiler: 'vue3'
    }),
    visualizer({
      filename: 'dist/stats.html', // 分析结果文件
      // open: true, // 打包完成后自动打开
      gzipSize: true, // 显示 gzip 大小
      brotliSize: true, // 显示 brotli 大小
      template: 'treemap' // 可选: treemap, sunburst, network
    }),
    // 生成gzip压缩文件
    viteCompression({
      algorithm: 'gzip', // 压缩算法
      ext: '.gz', // 压缩后的文件扩展名
      threshold: 1024, // 只压缩大于1KB的文件
      deleteOriginFile: false, // 是否删除原文件
      filter: /\.(js|css|html|svg)$/i, // 压缩文件类型
      verbose: true // 显示压缩信息
    }),
    // 同时生成Brotli压缩（更高压缩比）
    viteCompression({
      algorithm: 'brotliCompress',
      ext: '.br',
      threshold: 1024,
      deleteOriginFile: false
    }),
    ImageminPlugin({
      // 压缩模式，可选 'squoosh' | 'sharp'
      mode: 'squoosh',
      // 压缩前图片，支持png,jpeg,webp,avif,gif格式
      beforeBundle: true,
      // 压缩后图片，只支持png,jpeg,webp,avif,gif格式
      afterBundle: true,
      // 压缩配置
      squooshOptions: {
        encodeOptions: {
          mozjpeg: {
            quality: 80
          },
          webp: {
            quality: 80
          }
        }
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  // optimizeDeps: {
  //   include: ['leaflet', 'echarts']
  // },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `
        @use "@/assets/styles/variables.scss" as *;
        @use "@/assets/styles/mixins.scss" as *;
        `
      }
    }
  },
  build: {
    assetsDir: 'assets',
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name].[hash:8].[ext]' // 带哈希便于缓存
      }
    },
    // 指定压缩器
    minify: 'terser', // 默认是 'esbuild'，terser压缩效果更好但速度较慢
    terserOptions: {
      compress: {
        // 移除console
        drop_console: true,
        // 移除debugger
        drop_debugger: true,
        // 移除未使用的代码
        dead_code: true,
        // 移除未使用的变量
        unused: true,
        // 简化if语句
        conditionals: true,
        // 合并变量声明
        join_vars: true
      },
      mangle: {
        // 混淆变量名
        toplevel: true,
        // 保留类名
        keep_classnames: false,
        // 保留函数名
        keep_fnames: false
      },
      format: {
        // 移除注释
        comments: false
      }
    }
  }
})
