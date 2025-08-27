import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // <--- 1. 引入 path 模块

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  
  // --- 2. 新增 resolve 配置 ---
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    }
  },
  
  server: {
    // 配置代理，解决开发时的跨域问题
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:5000',
        changeOrigin: true,
      },
    },
  },
})